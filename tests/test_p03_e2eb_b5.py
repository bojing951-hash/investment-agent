# -*- coding: utf-8 -*-
"""IA-P03-E2EB-WP-B5(回答渲染层+端到端)专项测试。

合同 IA-P03-E2EB-WP-B5-AC-v1.0(DESIGN §六 WP-B5 行 L234-238 验收要点):
- 要点① 无provenance数值注入→渲染fail-closed负向测试;
- 要点② 端到端黄金用例: 全链路(B1映射→B2执行→B5渲染),断言美端值+日端
  「无数据」+OP-1 NO_DATA;GAP-05 write=False快照测试范式固化(L197/L236);
  B4 查询历史记录复用调用衔接(L237依赖列);
- 要点③ B3条件款: 停泊期登记不实施(REPORT §六 D-B5-16/§四),本文件无
  双端闭合版用例——非静默跳过,处置见 REPORT §七.2;
- 要点④ CI零回归(落CI,非本文件)。

数据纪律(AC-03/R014-D3): 全部fixture为SYNTHETIC(结构复刻真实采集JSON,
数值一律虚构发明,零真实数值转录;「DEV授权副本上全链路」按冻结合同AC-03
处理为fixture结构参照——B2 §七.1 审计PASS先例,测试内文档注记,差异登记
REPORT §七.1)。**预期值一律字面量硬编码**(/tmp/b5_precalc.py 真实管线预演
核验后誊写,不从被测模块导入计算——自证恒真是F反例)。零网络/零新增第三方
依赖;渲染器源码级零文件IO/零网络/禁语复用锁(见T7)。
"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import e2eb_query_ir as qir                    # noqa: E402 (B1: schema/正则复用)
import e2eb_query_mapper as eqm                # noqa: E402 (B1: 黄金问题映射+OOS词表)
import e2eb_query_executor as ex               # noqa: E402 (B2: 执行器复用调用)
import e2eb_answer_renderer as ar              # noqa: E402 (被测模块)
import snapshot_builder as sb                  # noqa: E402 (S1: write=False范式)
import research_archive as ra                  # noqa: E402 (B4: 查询历史复用调用)

# ══ 合成fixture注册表(渲染链身份唯一数据源;结构同B1/B2场景八条) ═════════
FIXTURE_METRICS = [
    {"metric_id": "DFEDTARL", "display_name": "联邦基金目标区间下限",
     "calc": "FOMC目标区间下限", "unit": "percent", "source": "rate_expectations"},
    {"metric_id": "DFEDTARU", "display_name": "联邦基金目标区间上限",
     "calc": "FOMC目标区间上限", "unit": "percent", "source": "rate_expectations"},
    {"metric_id": "DFF", "display_name": "有效联邦基金利率(日频)",
     "calc": "NYFed每日有效联邦基金利率", "unit": "percent",
     "source": "rate_expectations"},
    {"metric_id": "UST_2Y", "display_name": "2年期美债收益率",
     "calc": "FRED系列最新观测", "unit": "percent", "source": "macro_collector"},
    {"metric_id": "UST_10Y", "display_name": "10年期美债收益率",
     "calc": "FRED系列最新观测", "unit": "percent", "source": "macro_collector"},
    {"metric_id": "CURVE_2S10S", "display_name": "2s10s期限利差",
     "calc": "FRED系列最新观测", "unit": "percentage_point",
     "source": "macro_collector"},
    {"metric_id": "USDJPY", "display_name": "美元兑日元",
     "calc": "即期汇率", "unit": "jpy_per_usd", "source": "global_market_collector"},
    {"metric_id": "SPX", "display_name": "标普500指数",
     "calc": None, "unit": "index_point", "source": "global_market_collector"},
]
FIXTURE_REGISTRY = {"metrics": FIXTURE_METRICS,
                    "by_id": {m["metric_id"]: m for m in FIXTURE_METRICS}}

# ══ DESIGN §三(d) 第一环问题文本(B1逐字复用)与受理时刻 ═══════════════════
GOLDEN_Q = "美日政策利率差和10年期国债收益率差最近怎么样?和美元兑日元走势合起来看是什么状态?"
CREATED_AT = "2026-11-05T12:00:00+08:00"
AC = dict(qir.ANSWER_CONSTRAINTS)

# ══ 场景字面量(SYNTHETIC虚构数值,零真实转录;与B2 fixture相互独立) ════════
# 结构参照注记(要点②「DEV授权副本/数据档引用」的fixture承接,REPORT §七.1):
# 采集文件命名复刻 data/daily/{global,macro,china,rate_economy}_YYYYMMDD.json
# 四通道结构;数值全发明。
DAY = {
    "ymd": "20261102",
    "obs_global": "2026-10-30", "obs_macro": "2026-10-29",
    "obs_rate": "2026-10-30", "obs_china": "2026-10-30",
    "usdjpy": {"value": 149.20,
               "dates": ["2025-12-31", "2026-09-30", "2026-10-23", "2026-10-30"],
               "values": [144.00, 146.50, 148.10, 149.20]},
    "gold": {"value": 2380.00,
             "dates": ["2025-12-31", "2026-09-30", "2026-10-23", "2026-10-30"],
             "values": [2320.00, 2345.00, 2360.00, 2380.00]},
    "ust10": {"value": 4.72, "dates": ["2026-10-22", "2026-10-29"],
              "values": [4.83, 4.72]},
    "ust2": {"value": 4.31, "dates": ["2026-10-22", "2026-10-29"],
             "values": [4.44, 4.31]},
    "curve": 0.42,
    "dfedtarl": 4.00, "dfedtaru": 4.25, "dff": 4.11,
    "bei10": 2.45, "zq_price": 96.20,
}

# 预期值字面量(手算+/tmp/b5_precalc.py真实管线预演核验后誊写,零自证):
V_GOLDEN = {"MB-1": 4.0, "MB-2": 4.25, "MB-3": 4.11, "MB-4": 4.31, "MB-5": 4.72,
            "MB-6": 0.42, "MB-7": 149.2, "MB-10": 0.7427, "MB-11": 3.6111}
OP3_RESULT = 0.41                    # 4.72−4.31
SNAP_ID = "research_snapshot_20261102"
L_HEADER = ("【接地作答|模式B】query_id=QB-20261105-001;研究截止as_of=2026-11-02;"
            "快照=research_snapshot_20261102;门禁=DEGRADED")
L_MB1 = ("MB-1 DFEDTARL = 4.0 @2026-10-30(fact DFEDTARL@2026-10-30;"
         "源 rate_economy_20261102.json;快照 research_snapshot_20261102)")
L_MB7 = ("MB-7 USDJPY = 149.2 @2026-10-30(fact USDJPY@2026-10-30;"
         "源 global_20261102.json;快照 research_snapshot_20261102)")
L_MB8 = ("MB-8: 无数据——该指标不在注册表(无身份定义),无法取数"
         "(登记: 日本政策利率不在注册表(8指标,INVENTORY G-01))")
L_MB9 = ("MB-9: 无数据——该指标不在注册表(无身份定义),无法取数"
         "(登记: JGB 10Y不在注册表(8指标,INVENTORY G-01))")
L_MB10 = ("MB-10 USDJPY[week.pct_change] = 0.7427 @2026-10-30"
          "(fact USDJPY@2026-10-30;源 global_20261102.json;"
          "快照 research_snapshot_20261102)"
          " 口径: 窗口week.pct_change;基准2026-10-23(E3口径)")
L_OP1 = ("OP-1 日本政策利率 − (DFEDTARL+DFEDTARU)/2(目标区间中值): "
         "不可计算(NO_DATA,operand缺席不部分计算)")
L_OP2 = "OP-2 JGB 10Y − UST_10Y: 不可计算(NO_DATA,operand缺席不部分计算)"
L_OP3 = ("OP-3 UST_10Y − UST_2Y(查询期计算,对照注册值CURVE_2S10S) = "
         "0.41 percentage_point(公式: UST_10Y − UST_2Y(查询期计算,"
         "对照注册值CURVE_2S10S);输入观测日2026-10-29,2026-10-29;"
         "期限匹配(观测日一致,E11纪律))")
L_FOOTER = ("缺席摘要: 无数据2项/不可计算2项;缺席如实登记,不以相近指标冒充、"
            "不内插、不填0(§三(c))。本回答为接地研究信息,不构成投资建议(§七3)。")


# ══ 核心覆盖fixture生成器(注册表驱动;tests/test_snapshot.py同构范式) ══════

def _mid(metric):
    rng = (metric.get("validation") or {}).get("range")
    return round((rng[0] + rng[1]) / 2, 4) if rng else 1.0


def _freq_obs(metric, day):
    freq = metric.get("frequency")
    if freq == "monthly":
        return "2026-10-01"
    if freq == "weekly":
        return day["obs_macro"]
    return day["obs_macro"] if metric.get("source") == "macro_collector" \
        else day["obs_global"]


def write_day_files(td, day):
    """写一日四通道合成采集档(SYNTHETIC;注册表枚举核心覆盖)。"""
    reg = sb_preloaded_registry()
    metrics = reg["metrics"]
    global_data, macro_data = {}, {}
    for m in metrics:
        mid, src = m["metric_id"], m.get("source")
        if src == "global_market_collector":
            key = sb._GLOBAL_OLD_ID.get(mid, mid)
            item = {"close": _mid(m), "date": day["obs_global"]}
            if mid == "USDJPY":
                item = {"close": day["usdjpy"]["value"], "date": day["obs_global"],
                        "series": {"dates": day["usdjpy"]["dates"],
                                   "values": day["usdjpy"]["values"]}}
            elif mid == "GOLD_F":
                item = {"close": day["gold"]["value"], "date": day["obs_global"],
                        "series": {"dates": day["gold"]["dates"],
                                   "values": day["gold"]["values"]}}
            global_data[key] = item
        elif src == "macro_collector":
            if "(derived)" in str(m.get("source_symbol")):
                continue     # NFP_MOM_K等: compute_derived独占生产
            item = {"value": _mid(m), "date": _freq_obs(m, day),
                    "frequency": m.get("frequency")}
            if mid == "UST_10Y":
                item = {"value": day["ust10"]["value"], "date": day["obs_macro"],
                        "frequency": "daily",
                        "series": {"dates": day["ust10"]["dates"],
                                   "values": day["ust10"]["values"]}}
            elif mid == "UST_2Y":
                item = {"value": day["ust2"]["value"], "date": day["obs_macro"],
                        "frequency": "daily",
                        "series": {"dates": day["ust2"]["dates"],
                                   "values": day["ust2"]["values"]}}
            elif mid == "CURVE_2S10S":
                item = {"value": day["curve"], "date": day["obs_macro"],
                        "frequency": "daily"}
            elif mid == "BEI_10Y":
                item = {"value": day["bei10"], "date": day["obs_macro"],
                        "frequency": "daily"}
            elif mid == "NFP":
                item = {"value": 155000, "date": "2026-10-01", "frequency": "monthly",
                        "series": {"dates": ["2026-08-01", "2026-09-01", "2026-10-01"],
                                   "values": [154800, 154900, 155000]}}
            elif mid == "CPI":
                item = {"value": 321, "date": "2026-10-01", "frequency": "monthly",
                        "series": {"dates": ["2026-08-01", "2026-09-01", "2026-10-01"],
                                   "values": [319, 320, 321]}}
            macro_data[mid] = item
    with open(os.path.join(td, f"global_{day['ymd']}.json"), "w") as f:
        json.dump({"date": day["ymd"], "time": "07:12:00",
                   "count": len(global_data), "data": global_data}, f)
    with open(os.path.join(td, f"macro_{day['ymd']}.json"), "w") as f:
        json.dump({"date": day["ymd"], "data": macro_data, "derived": {}}, f)
    cn_reg = {m["metric_id"]: m for m in metrics
              if m.get("source") == "china_market_collector"}
    indices = {}
    for mid, label in sb._CHINA_LABEL.items():
        if mid in cn_reg:
            indices[label] = {"name": label, "close": _mid(cn_reg[mid]),
                              "week_chg": 0.4, "date": day["obs_china"]}
    china_json = {"date": day["ymd"], "data": {}, "indices": indices,
                  "ah_premium": {"close": _mid(cn_reg["HSAHP"]),
                                 "date": day["obs_china"]},
                  "turnover": {"date": day["ymd"],
                               "sh_amount_billion": _mid(cn_reg["SH_AMOUNT"]),
                               "sz_amount_billion": _mid(cn_reg["SZ_COMPONENT_AMOUNT"]),
                               "total_amount_billion": _mid(cn_reg["CN_TOTAL_TURNOVER"])}}
    with open(os.path.join(td, f"china_{day['ymd']}.json"), "w") as f:
        json.dump(china_json, f)
    unrate_mid = _mid(next(m for m in metrics if m["metric_id"] == "UNEMPLOYMENT"))
    umc_mid = _mid(next(m for m in metrics if m["metric_id"] == "UMCSENT"))
    rate_json = {"date": day["ymd"], "current_rates": {
        "DFF": {"name": "有效联邦基金利率", "value": day["dff"], "date": day["obs_rate"]},
        "DFEDTARU": {"name": "目标区间上限", "value": day["dfedtaru"], "date": day["obs_rate"]},
        "DFEDTARL": {"name": "目标区间下限", "value": day["dfedtarl"], "date": day["obs_rate"]}},
        "fed_funds_futures": [
            {"ticker": "ZQ=F", "name": "FF期货主力", "price": day["zq_price"],
             "implied_rate": round(100 - day["zq_price"], 2),
             "diff_from_current": -0.15, "signal": "宽松", "date": day["obs_rate"]}],
        "real_economy": {
            "UNRATE": {"name": "失业率", "value": unrate_mid, "date": "2026-10-01", "freq": "月度"},
            "UMCSENT": {"name": "消费者信心", "value": umc_mid, "date": "2026-10-01", "freq": "月度"}}}
    with open(os.path.join(td, f"rate_economy_{day['ymd']}.json"), "w") as f:
        json.dump(rate_json, f)


def sb_preloaded_registry():
    """S1身份层真实注册表(先例同构:B2 write_day_files 同款,只读取)。"""
    import fact_engine as fe
    return fe.load_registry()


def quiet_build(ymd, td, as_of):
    """S1 write=False构建(静默stdout;GAP-05范式,D-B5-15)。"""
    buf = io.StringIO()
    with redirect_stdout(buf):
        snap = sb.build_snapshot(target_ymd=ymd, data_dir=td, write=False,
                                 as_of=as_of, trusted_root=td)
    return snap


def golden_ir(as_of="2026-11-02"):
    return eqm.map_question(GOLDEN_Q, created_at=CREATED_AT, as_of=as_of,
                            registry=FIXTURE_REGISTRY)


# ══ 手工事实/快照/绑定构造器(注入面单测;B2同构范式) ═════════════════════

def hfact(mid, value, obs, src="global_20261102.json", quality="PASS",
          derived=None, calc_ref=None):
    """手工事实(SYNTHETIC;仅携带执行器消费字段)。"""
    return {"metric_id": mid, "fact_id": f"{mid}@{obs}", "value": value,
            "observation_date": obs, "quality_status": quality,
            "source": {"collector": "synthetic", "file": src},
            "derived": derived, "calculation_ref": calc_ref}


def hsnap(gate="PASS", sid=SNAP_ID, facts=None, sources=None):
    snap = {"snapshot_id": sid, "research_as_of": "2026-11-02T12:00:00+08:00",
            "target_date": sid[len("research_snapshot_"):][:8],
            "sources_status": sources if sources is not None else {
                ch: {"status": "EXACT", "file": f"{ch}_20261102.json"}
                for ch in ("global", "macro", "china", "rate_economy")},
            "facts": facts or [], "gate_a": {"status": gate}}
    return snap


def _pb(bid, mid, role="level", window=None, field="value"):
    return {"binding_id": bid, "metric_id": mid, "role": role, "window": window,
            "field": field, "status": qir.PENDING_EXECUTION,
            "absence_reason": None, "provenance": None}


def hand_ir(bindings, ops=None, question="合成问题", as_of=None, qid="QB-20261105-001"):
    ir = {"query_id": qid, "created_at": CREATED_AT, "mode": "B",
          "question_text": question, "as_of": as_of, "target_snapshot_id": None,
          "metric_bindings": bindings, "derived_operations": ops or [],
          "unresolved_entities": [], "answer_constraints": AC}
    assert qir.validate_ir(ir, stage="mapped") == [], "hand_ir基底非法"
    return ir


# ══ T0 fixture/生成器自检 ═════════════════════════════════════════════════

class TestFixtureSanity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        write_day_files(cls.td.name, DAY)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def test_fixture_registry_structure(self):
        self.assertEqual(len(FIXTURE_METRICS), 8)
        self.assertTrue(all(m.get("source") for m in FIXTURE_METRICS))
        self.assertEqual(FIXTURE_REGISTRY["by_id"]["USDJPY"]["unit"], "jpy_per_usd")

    def test_generator_core_covering_gate_degraded(self):
        snap = quiet_build("20261102", self.td.name, "2026-11-02")
        self.assertEqual(snap["gate_a"]["status"], "DEGRADED")
        self.assertEqual(snap["gate_a"]["core_missing"], [])
        self.assertEqual(snap["gate_a"]["core_fail"], [])

    def test_generator_curve_fact_present(self):
        """本包fixture含CURVE_2S10S(与B2蓄意A3缺席场景相互独立的设计选择)。"""
        snap = quiet_build("20261102", self.td.name, "2026-11-02")
        ids = {f["metric_id"] for f in snap["facts"]}
        self.assertIn("CURVE_2S10S", ids)

    def test_generator_series_store(self):
        snap = quiet_build("20261102", self.td.name, "2026-11-02")
        store = snap.get("series_store") or {}
        self.assertEqual(store["USDJPY"]["values"], DAY["usdjpy"]["values"])

    def test_golden_chain_deterministic(self):
        snap = quiet_build("20261102", self.td.name, "2026-11-02")
        r1 = ex.execute_query(golden_ir(), snapshot=snap, registry=FIXTURE_REGISTRY)
        a1 = ar.render_answer(r1)
        r2 = ex.execute_query(golden_ir(), snapshot=snap, registry=FIXTURE_REGISTRY)
        a2 = ar.render_answer(r2)
        self.assertEqual(a1, a2)


# ══ T1 fail-closed接地负向(要点①) ════════════════════════════════════════

class TestFailClosedGrounding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        write_day_files(cls.td.name, DAY)
        cls.snap = quiet_build("20261102", cls.td.name, "2026-11-02")
        cls.result = ex.execute_query(golden_ir(), snapshot=cls.snap,
                                      registry=FIXTURE_REGISTRY)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def _tampered(self, bid_mutator):
        import copy
        r = copy.deepcopy(self.result)
        bid_mutator({b["binding_id"]: b for b in r["ir"]["metric_bindings"]})
        return r

    def test_resolved_without_provenance_fails(self):
        """要点①核心: provenance=None的RESOLVED数值→渲染fail-closed。"""
        r = self._tampered(lambda mb: mb["MB-7"].__setitem__("provenance", None))
        with self.assertRaises(ar.GroundingError):
            ar.render_answer(r)

    def test_all_three_forms_broken_fails(self):
        """三形态全破(fact_id坏+snapshot_id坏+source_file空)→fail-closed。"""
        def break_all(mb):
            p = mb["MB-1"]["provenance"]
            p["fact_id"] = "不是fact_id格式"
            p["snapshot_id"] = "not_a_snapshot"
            p["source_file"] = ""
        r = self._tampered(break_all)
        with self.assertRaises(ar.GroundingError):
            ar.render_answer(r)

    def test_single_form_sufficient_passes(self):
        """「之一以上」(L113): 仅形态③(source_file+observation_date)完整→放行。"""
        def keep_only_form3(mb):
            p = mb["MB-1"]["provenance"]
            p["fact_id"] = "坏格式"
            p["snapshot_id"] = "坏格式"
            p["metric_id"] = None
        r = self._tampered(keep_only_form3)
        ans = ar.render_answer(r)
        self.assertEqual(ans["kind"], "grounded")

    def test_derived_without_calc_ref_fails(self):
        """派生值缺calculation_ref(L114)→fail-closed(渲染层独立复验)。"""
        import copy
        r = copy.deepcopy(self.result)
        ops = {o["op_id"]: o for o in r["ir"]["derived_operations"]}
        ops["OP-3"]["calculation_ref"] = ""
        with self.assertRaises(ar.GroundingError):
            ar.render_answer(r)

    def test_tampered_real_pipeline_fails(self):
        """真实管线产出注入缺陷(逐字节拷贝后定向篡改)→fail-closed(要点①工件)。"""
        r = self._tampered(lambda mb: mb["MB-5"].__setitem__("provenance", None))
        with self.assertRaises(ar.GroundingError):
            ar.render_answer(r)

    def test_validate_value_node_forms_unit(self):
        """单元级: 三形态逐一满足判定(D-B5-02)。"""
        ok = {"binding_id": "MB-1", "value": 1.5, "field_path": "facts[].value",
              "provenance": {"metric_id": "X", "fact_id": "X@2026-01-01",
                             "snapshot_id": "research_snapshot_20260101",
                             "source_file": "global_20260101.json",
                             "observation_date": "2026-01-01"}}
        self.assertEqual(ar.validate_value_node(ok), [])
        f2 = {**ok, "provenance": {**ok["provenance"], "fact_id": "坏",
                                   "source_file": ""}}       # 仅形态②
        self.assertEqual(ar.validate_value_node(f2), [])
        f3 = {**ok, "provenance": {**ok["provenance"], "fact_id": "坏",
                                   "snapshot_id": "坏"}}       # 仅形态③
        self.assertEqual(ar.validate_value_node(f3), [])
        none_form = {**ok, "provenance": {"metric_id": None, "fact_id": "坏",
                                          "snapshot_id": "坏", "source_file": "",
                                          "observation_date": ""}}
        self.assertTrue(ar.validate_value_node(none_form))

    def test_validate_derived_node_operand_chain_unit(self):
        """单元级: operand provenance无完整形态→issue(D-B5-03输入观测链)。"""
        node = {"op_id": "OP-1", "value": 0.5, "unit": "pp",
                "calculation_ref": "公式: 合成", "operands": ["MB-1"]}
        good_prov = {"metric_id": "X", "fact_id": "X@2026-01-01",
                     "snapshot_id": "research_snapshot_20260101",
                     "source_file": "f.json", "observation_date": "2026-01-01"}
        self.assertEqual(
            ar.validate_derived_node(node, [("MB-1", good_prov, "facts[].value")]),
            [])
        self.assertTrue(
            ar.validate_derived_node(node, [("MB-1", {}, None)]))
        self.assertTrue(
            ar.validate_derived_node(node, [("MB-1", None, None)]))

    def test_bool_and_string_value_rejected(self):
        """D-B5-11: bool/字符串数字不算数值。"""
        base = {"binding_id": "MB-1", "field_path": "facts[].value",
                "provenance": {"metric_id": "X", "fact_id": "X@2026-01-01",
                               "snapshot_id": "research_snapshot_20260101",
                               "source_file": "f.json",
                               "observation_date": "2026-01-01"}}
        self.assertTrue(ar.validate_value_node({**base, "value": True}))
        self.assertTrue(ar.validate_value_node({**base, "value": "4.25"}))

    def test_values_keys_equal_resolved_set(self):
        """结构性: values键集==RESOLVED绑定集(缺席项零数值,不部分计算)。"""
        resolved = {b["binding_id"] for b in self.result["ir"]["metric_bindings"]
                    if b["status"] == "RESOLVED"}
        self.assertEqual(set(self.result["values"].keys()), resolved)
        self.assertNotIn("MB-8", self.result["values"])
        self.assertNotIn("MB-9", self.result["values"])

    def test_grounding_error_is_valueerror(self):
        self.assertTrue(issubclass(ar.GroundingError, ValueError))

    def test_input_shape_guards(self):
        with self.assertRaises(ValueError):
            ar.render_answer({"ir": None})
        with self.assertRaises(ValueError):
            ar.render_answer("not-a-dict")

    def test_grounding_required_defense(self):
        """渲染层防御断言: grounding_required≠True→拒绝(纵深防御)。"""
        r = {**self.result,
             "ir": {**self.result["ir"],
                    "answer_constraints": {"grounding_required": False,
                                           "no_data_policy": "report_absence"}}}
        with self.assertRaises(ar.GroundingError):
            ar.render_answer(r)

    def test_refusal_renders_without_grounding_error(self):
        refusal = ex.execute_query(hand_ir([_pb("MB-1", "SPX")]), snapshot=None,
                                   daily_dir="/nonexistent-empty-dir-b5",
                                   registry=FIXTURE_REGISTRY)
        self.assertIn("refusal", refusal)
        ans = ar.render_answer(refusal)
        self.assertEqual(ans["kind"], "refusal")
        self.assertEqual(ans["n_grounded_values"], 0)


# ══ T2 缺席文本化(§三(c)四级+NO_DATA) ═════════════════════════════════════

class TestAbsenceTextualization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        write_day_files(cls.td.name, DAY)
        cls.snap = quiet_build("20261102", cls.td.name, "2026-11-02")
        cls.result = ex.execute_query(golden_ir(), snapshot=cls.snap,
                                      registry=FIXTURE_REGISTRY)
        cls.answer = ar.render_answer(cls.result)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def test_a1_phrase_mb8_mb9(self):
        """A1措辞逐字(L124): MB-8/MB-9行=「该指标不在注册表(无身份定义),无法取数」。"""
        self.assertIn(L_MB8, self.answer["lines"])
        self.assertIn(L_MB9, self.answer["lines"])

    def test_a3_phrase(self):
        """A3(L126): 已注册无事实→「本期无该指标事实」。"""
        snap = hsnap(facts=[])                       # 通道EXACT但零事实
        r = ex.execute_query(hand_ir([_pb("MB-1", "SPX")]), snapshot=snap,
                             registry=FIXTURE_REGISTRY)
        ans = ar.render_answer(r)
        self.assertIn("MB-1: 无数据——本期无该指标事实(登记: 本期无该指标事实)",
                      ans["lines"])

    def test_a2_phrase(self):
        """A2(L125): 通道MISSING→「指标已注册但当日采集缺失」。"""
        sources = {ch: {"status": "MISSING", "file": None}
                   for ch in ("global", "macro", "china", "rate_economy")}
        snap = hsnap(facts=[], sources=sources)
        r = ex.execute_query(hand_ir([_pb("MB-1", "SPX")]), snapshot=snap,
                             registry=FIXTURE_REGISTRY)
        ans = ar.render_answer(r)
        line = next(l for l in ans["lines"] if l.startswith("MB-1"))
        self.assertIn("无数据——指标已注册但当日采集缺失", line)
        self.assertIn("(登记: 指标已注册但当日采集缺失(通道global状态MISSING))", line)

    def test_a4_phrase_verbatim_reason(self):
        """A4(L127): 引擎reason原样转述,非模板词。"""
        fact = hfact("USDJPY", 149.2, "2026-10-30",
                     derived={"m1": {"available": False,
                                     "reason": "序列不足1个月(合成示意)"}})
        snap = hsnap(facts=[fact])
        r = ex.execute_query(
            hand_ir([_pb("MB-1", "USDJPY", role="derived_window",
                         window="m1", field="pct_change")]),
            snapshot=snap, registry=FIXTURE_REGISTRY)
        ans = ar.render_answer(r)
        self.assertIn("MB-1: 无数据——E3窗口不可用: 序列不足1个月(合成示意)"
                      "(引擎原因原样转述)", ans["lines"])

    def test_op1_op2_no_data_phrase(self):
        """NO_DATA措辞(L129/D-B5-07): 不部分计算。"""
        self.assertIn(L_OP1, self.answer["lines"])
        self.assertIn(L_OP2, self.answer["lines"])

    def test_absent_lines_all_carry_mark(self):
        """L129: 缺席项显式声明「无数据」。"""
        for item in self.answer["absent"]:
            line = next(l for l in self.answer["lines"]
                        if l.startswith(item["binding_id"]))
            self.assertIn("无数据", line)

    def test_footer_counts(self):
        self.assertIn(L_FOOTER, self.answer["lines"])
        self.assertEqual(len(self.answer["absent"]), 2)
        self.assertEqual(len(self.answer["no_data"]), 2)

    def test_absent_items_never_fabricated(self):
        """缺席项零编造: absent行无provenance(登记reason),不进value_nodes。"""
        absent_ids = {a["binding_id"] for a in self.answer["absent"]}
        grounded_ids = {n["binding_id"] for n in self.answer["value_nodes"]}
        self.assertEqual(absent_ids & grounded_ids, set())
        self.assertEqual(absent_ids, {"MB-8", "MB-9"})


# ══ T3 质量披露(§三(b).4/L116) ═══════════════════════════════════════════

class TestQualityDisclosure(unittest.TestCase):
    def _render_with_quality(self, quality):
        fact = hfact("SPX", 5900.0, "2026-10-30", quality=quality)
        r = ex.execute_query(hand_ir([_pb("MB-1", "SPX")]),
                             snapshot=hsnap(facts=[fact]),
                             registry=FIXTURE_REGISTRY)
        return ar.render_answer(r)

    def test_degraded_disclosure(self):
        ans = self._render_with_quality("DEGRADED")
        line = next(l for l in ans["lines"] if l.startswith("MB-1"))
        self.assertIn(" | 质量披露: DEGRADED(非PASS降级披露,A4纪律)", line)
        self.assertEqual(ans["quality_disclosures"], ["MB-1: DEGRADED"])

    def test_warn_disclosure(self):
        ans = self._render_with_quality("WARN")
        line = next(l for l in ans["lines"] if l.startswith("MB-1"))
        self.assertIn(" | 质量披露: WARN(非PASS降级披露,A4纪律)", line)

    def test_pass_no_disclosure(self):
        ans = self._render_with_quality("PASS")
        self.assertEqual(ans["quality_disclosures"], [])

    def test_header_gate_status_display(self):
        """门禁状态如实展示(黄金链=S1产出DEGRADED,快照级≠事实级质量)。"""
        td = tempfile.TemporaryDirectory()
        try:
            write_day_files(td.name, DAY)
            snap = quiet_build("20261102", td.name, "2026-11-02")
            r = ex.execute_query(golden_ir(), snapshot=snap,
                                 registry=FIXTURE_REGISTRY)
            ans = ar.render_answer(r)
            self.assertIn(L_HEADER, ans["lines"])
            self.assertEqual(ans["gate_status"], "DEGRADED")
        finally:
            td.cleanup()


# ══ T4 黄金端到端(要点②;GAP-05+B4衔接) ═══════════════════════════════════

class TestGoldenEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        write_day_files(cls.td.name, DAY)
        cls.snap = quiet_build("20261102", cls.td.name, "2026-11-02")  # GAP-05
        cls.result = ex.execute_query(golden_ir(), snapshot=cls.snap,
                                      registry=FIXTURE_REGISTRY)
        cls.answer = ar.render_answer(cls.result)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def test_us_values_all_literals(self):
        """要点②美端值: 9绑定全字面量(预演誊写,零自证)。"""
        self.assertEqual(self.result["values"], V_GOLDEN)

    def test_all_value_nodes_grounded(self):
        """9数值节点全部携完整来源标识(接地强制通过面)。"""
        self.assertEqual(self.answer["n_grounded_values"], 9)
        for node in self.answer["value_nodes"]:
            self.assertTrue(ar.validate_value_node(node) == [])
            self.assertIsNotNone(node["provenance"]["fact_id"])

    def test_jp_side_no_data(self):
        """要点②日端: MB-8/MB-9 ABSENT_REGISTRY→「无数据」如实(B3停泊=当前事实)。"""
        self.assertIn(L_MB8, self.answer["lines"])
        self.assertIn(L_MB9, self.answer["lines"])
        mb = {b["binding_id"]: b for b in self.result["ir"]["metric_bindings"]}
        self.assertEqual(mb["MB-8"]["status"], "ABSENT_REGISTRY")
        self.assertEqual(mb["MB-9"]["status"], "ABSENT_REGISTRY")

    def test_op1_no_data(self):
        """要点②点名: OP-1 NO_DATA result=None。"""
        ops = {o["op_id"]: o for o in self.result["ir"]["derived_operations"]}
        self.assertEqual(ops["OP-1"]["status"], "NO_DATA")
        self.assertIsNone(ops["OP-1"]["result"])
        self.assertIn(L_OP1, self.answer["lines"])

    def test_op2_no_data(self):
        ops = {o["op_id"]: o for o in self.result["ir"]["derived_operations"]}
        self.assertEqual(ops["OP-2"]["status"], "NO_DATA")
        self.assertIsNone(ops["OP-2"]["result"])

    def test_op3_computed_literal(self):
        """OP-3查询期计算=0.41(4.72−4.31),calculation_ref完整(E11纪律)。"""
        ops = {o["op_id"]: o for o in self.result["ir"]["derived_operations"]}
        self.assertEqual(ops["OP-3"]["status"], "COMPUTED")
        self.assertEqual(ops["OP-3"]["result"], OP3_RESULT)
        self.assertIn(L_OP3, self.answer["lines"])

    def test_key_line_literals(self):
        for line in (L_HEADER, L_MB1, L_MB7, L_MB10, L_FOOTER):
            self.assertIn(line, self.answer["lines"])

    def test_answer_text_equals_joined_lines(self):
        self.assertEqual(self.answer["answer_text"], "\n".join(self.answer["lines"]))

    def test_executed_ir_schema(self):
        self.assertEqual(qir.validate_ir(self.result["ir"], stage="executed"), [])

    def test_render_deterministic(self):
        again = ar.render_answer(
            ex.execute_query(golden_ir(), snapshot=self.snap,
                             registry=FIXTURE_REGISTRY))
        self.assertEqual(again, self.answer)

    def test_write_false_no_persistence(self):
        """GAP-05固化: 链后数据目录零research_snapshot_*.json(write=False)。"""
        persisted = [n for n in os.listdir(self.td.name)
                     if n.startswith("research_snapshot")]
        self.assertEqual(persisted, [])
        self.assertEqual(self.result["snapshot_id"], SNAP_ID)  # 内存构建

    def test_archive_append_and_verify(self):
        """B4衔接(依赖列L237): executed IR+执行结果落query_history+digest复算通过。"""
        td_a = tempfile.TemporaryDirectory()
        td_s = tempfile.TemporaryDirectory()
        try:
            with open(os.path.join(td_s.name, f"{SNAP_ID}.json"), "w") as f:
                json.dump(self.snap, f)                 # 测试侧写档(B4 verify面)
            status, path = ra.append_query_record(
                self.result["ir"], snapshot=self.snap, archive_dir=td_a.name,
                execution=self.result, archived_at="2026-11-05T04:00:00+00:00")
            self.assertEqual(status, "written")
            record = ra.load_query_record("QB-20261105-001", archive_dir=td_a.name)
            self.assertEqual(record["ir_stage"], "executed")
            ok, issues = ra.verify_query_record(record, snapshot_dir=td_s.name)
            self.assertTrue(ok, issues)
        finally:
            td_a.cleanup()
            td_s.cleanup()


# ══ T5 daily_dir自取路径+OOS边界+refusal ═════════════════════════════════

class TestDailyDirPathAndBoundaries(unittest.TestCase):
    def test_daily_dir_self_acquire_matches_injection(self):
        """执行器自取(R1无既有→S1 write=False)与注入路径产出逐值相等。"""
        td = tempfile.TemporaryDirectory()
        try:
            write_day_files(td.name, DAY)
            r = ex.execute_query(golden_ir(), daily_dir=td.name,
                                 trusted_root=td.name, registry=FIXTURE_REGISTRY)
            self.assertEqual(r["values"], V_GOLDEN)
            self.assertEqual(r["snapshot_id"], SNAP_ID)
            ans = ar.render_answer(r)
            self.assertEqual(ans["n_grounded_values"], 9)
            persisted = [n for n in os.listdir(td.name)
                         if n.startswith("research_snapshot")]
            self.assertEqual(persisted, [])           # GAP-05: 自取路径同样零持久化
        finally:
            td.cleanup()

    def test_oos_question_renders_honest_disclosure(self):
        """禁交易类问题: OOS指称如实上浮(B1)+渲染披露不构成建议(§七3)。"""
        q = "现在应该买入美元兑日元吗?能保证赚钱吗?"
        ir = eqm.map_question(q, created_at=CREATED_AT, registry=FIXTURE_REGISTRY)
        td = tempfile.TemporaryDirectory()
        try:
            write_day_files(td.name, DAY)
            snap = quiet_build("20261102", td.name, "2026-11-02")
            r = ex.execute_query(ir, snapshot=snap, registry=FIXTURE_REGISTRY)
            ans = ar.render_answer(r)                  # 守卫不误伤豁免行
            self.assertEqual(ans["kind"], "grounded")
            oos_lines = [l for l in ans["lines"] if l.startswith("未解析指称")]
            self.assertTrue(oos_lines)
            self.assertIn("out_of_scope", oos_lines[0])
            self.assertIn("不构成投资建议", oos_lines[0])
            self.assertIn("不构成投资建议", ans["lines"][-1])   # footer免责声明
        finally:
            td.cleanup()

    def test_refusal_text_and_zero_values(self):
        ir = hand_ir([_pb("MB-1", "SPX")])
        r = ex.execute_query(ir, daily_dir="/nonexistent-empty-dir-b5",
                             registry=FIXTURE_REGISTRY)
        ans = ar.render_answer(r)
        self.assertEqual(ans["kind"], "refusal")
        self.assertIn("无法作答: ", ans["answer_text"])
        refusal_line = next(l for l in ans["lines"] if l.startswith("无法作答: "))
        self.assertTrue(refusal_line)
        self.assertEqual(ans["value_nodes"], [])

    def test_empty_ir_renders_footer_only_answer(self):
        """零绑定零操作: 恒等footer+头部,无数值无缺席(合法空集)。"""
        ir = hand_ir([])
        r = ex.execute_query(ir, snapshot=hsnap(facts=[]),
                             registry=FIXTURE_REGISTRY)
        ans = ar.render_answer(r)
        self.assertEqual(ans["n_grounded_values"], 0)
        self.assertIn("缺席摘要: 无数据0项/不可计算0项", ans["lines"][-1])


# ══ T6 禁投资建议守卫(D-B5-08) ═══════════════════════════════════════════

class TestAdviceGuard(unittest.TestCase):
    def test_guard_raises_on_advice_value_line(self):
        with self.assertRaises(ar.GroundingError):
            ar.assert_no_advice([("value", "MB-1 USDJPY = 150.0 建议买入")])

    def test_guard_raises_on_derived_line(self):
        with self.assertRaises(ar.GroundingError):
            ar.assert_no_advice([("derived", "OP-1 利差 = 0.5 pp 该止损")])

    def test_guard_exempts_unresolved_and_footer(self):
        ar.assert_no_advice([
            ("unresolved", "未解析指称: 「应该买入」(out_of_scope): 禁交易类指称"),
            ("footer", "本回答为接地研究信息,不构成投资建议(§七3)。")])

    def test_guard_covers_all_wordlist_entries(self):
        """词表21词逐一命中即拒(复用eqm词表,零复制)。"""
        for pat in eqm.OUT_OF_SCOPE_PATTERNS:
            with self.assertRaises(ar.GroundingError):
                ar.assert_no_advice([("value", f"数值行含{pat}")])


# ══ T7 复用纯度锁(D-B5-12;源码级) ════════════════════════════════════════

MODULE_SOURCE = open(os.path.join(ROOT, "scripts", "e2eb_answer_renderer.py"),
                     encoding="utf-8").read()


class TestPurityAndReuse(unittest.TestCase):
    def test_zero_file_io_and_no_network(self):
        self.assertNotIn("open(", MODULE_SOURCE)
        self.assertNotIn("os.listdir", MODULE_SOURCE)
        for bad in ("import socket", "import urllib", "import requests",
                    "import subprocess", "import http"):
            self.assertNotIn(bad, MODULE_SOURCE)

    def test_no_raw_collection_paths(self):
        """AC-07.1: 渲染器源码零采集档路径引用(零文件IO的补强)。"""
        for pat in ("data/daily", "macro_2", "global_2", "china_market_",
                    "rate_economy_"):
            self.assertNotIn(pat, MODULE_SOURCE)

    def test_project_imports_exactly_qir_eqm(self):
        """D-B5-12: 依赖面恰2个项目模块(B1 qir+eqm),零其他项目依赖。"""
        import re as _re
        imports = _re.findall(r"^import (\w+)", MODULE_SOURCE, _re.M)
        self.assertEqual(sorted(imports), ["e2eb_query_ir", "e2eb_query_mapper",
                                           "os", "sys"])

    def test_reuse_no_logic_copy(self):
        """复用禁复制分叉: 无B1/B2/B4逻辑副本(执行/映射/digest函数零出现)。"""
        for forbidden in ("def execute_query", "def map_question",
                          "def digest_snapshot", "def append_query_record",
                          "def build_snapshot"):
            self.assertNotIn(forbidden, MODULE_SOURCE)

    def test_wordlist_reused_not_copied(self):
        """OOS词表复用调用: 源码引用eqm.OUT_OF_SCOPE_PATTERNS且无本地副本。"""
        self.assertIn("eqm.OUT_OF_SCOPE_PATTERNS", MODULE_SOURCE)
        self.assertNotIn('OUT_OF_SCOPE_PATTERNS = (', MODULE_SOURCE)

    def test_public_api_whitelist(self):
        """D-B5-01公共API白名单: 无白名单外公共可调用对象。"""
        allowed = {"GroundingError", "validate_value_node", "validate_derived_node",
                   "assert_no_advice", "render_answer"}
        public_callables = {n for n in dir(ar)
                            if not n.startswith("_")
                            and callable(getattr(ar, n))}
        self.assertEqual(public_callables, allowed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
