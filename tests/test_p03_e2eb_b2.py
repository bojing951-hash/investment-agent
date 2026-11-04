# -*- coding: utf-8 -*-
"""IA-P03-E2EB-WP-B2(查询执行器)专项测试。

合同 IA-P03-E2EB-WP-B2-AC-v1.0(DESIGN §六 WP-B2 行 L216-220 验收要点):
- 要点① write=False快照绑定 + OP-3执行(R1既有优先→S1离线构建,禁墙钟);
- 要点② OP-1/OP-2 operand缺席→NO_DATA result=null(四级缺席传导);
- 要点③ as_of两时点只读锚定(不混期: 两日合成采集档同目录,值随锚点切换);
- 要点④ 执行器输出与fact_engine直算逐值相等(硬编码预期字面量);
- 要点⑤ 既有套件零回归(落CI,非本文件)。

数据纪律(AC-03/R014-D3): 全部fixture为SYNTHETIC(结构复刻真实采集JSON,
数值一律虚构发明,零真实数值转录);执行器registry参数=合成fixture注册表
(8+2变体),不读真实注册表作绑定身份;S1管线用真实注册表仅作事实身份/校验层
(tests/test_snapshot.py同构先例)。**预期值一律字面量硬编码**(手算+引擎原语
预演核验,不从被测模块导入计算——自证恒真是F反例)。零网络/零新增第三方依赖;
执行器源码级零网络/零采集档IO/禁墙钟锁(见T8)。
"""
import io
import json
import os
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import e2eb_query_ir as qir                    # noqa: E402 (executed两阶段校验)
import e2eb_query_mapper as eqm                # noqa: E402 (mapped IR生产)
import e2eb_query_executor as ex               # noqa: E402 (被测模块)
import fact_engine as fe                       # noqa: E402 (E3/E4直算对照)
import correlation_calculator as cc            # noqa: E402 (C3/C4直算对照)
import snapshot_builder as sb                  # noqa: E402 (S1 fixture构建)
import research_provenance as rp               # noqa: E402 (R1常量对照)

# ══ 合成fixture注册表(执行器绑定身份唯一数据源;B1八条+source字段) ═════════
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
# 相关性/store用扩展变体(+CCC_OAS宏观序列,+GOLD_F行情序列: 相关性两侧身份)
CCC_METRICS = FIXTURE_METRICS + [
    {"metric_id": "CCC_OAS", "display_name": "CCC投机级OAS",
     "calc": "FRED系列最新观测", "unit": "percentage_point",
     "source": "macro_collector"},
    {"metric_id": "GOLD_F", "display_name": "COMEX黄金期货",
     "calc": "主力合约收盘", "unit": "usd_per_oz",
     "source": "global_market_collector"}]
CCC_REGISTRY = {"metrics": CCC_METRICS,
                "by_id": {m["metric_id"]: m for m in CCC_METRICS}}
# JP在场变体(B1对照面: 缺席=发现而非硬编码)
JP_METRICS = [
    {"metric_id": "JP_POLICY_RATE", "display_name": "日本政策利率(日银政策目标)",
     "calc": None, "unit": "percent", "source": "boj_collector"},
    {"metric_id": "JGB_10Y", "display_name": "日本10年期国债收益率(JGB 10Y)",
     "calc": None, "unit": "percent", "source": "boj_collector"},
]
JP_REGISTRY = {"metrics": FIXTURE_METRICS + JP_METRICS,
               "by_id": {m["metric_id"]: m for m in FIXTURE_METRICS + JP_METRICS}}

# ══ DESIGN §三(d) 第一环问题文本(B1逐字复用) ═════════════════════════════
GOLDEN_Q = "美日政策利率差和10年期国债收益率差最近怎么样?和美元兑日元走势合起来看是什么状态?"
CREATED_AT = "2026-11-05T12:00:00+08:00"
AC = dict(qir.ANSWER_CONSTRAINTS)

# ══ 场景字面量(手算;SYNTHETIC虚构数值,零真实转录) ════════════════════════
# D2=20261102(研究截止2026-11-02);D1=20261101(研究截止2026-11-01)
D2_SERIES_DATES = ['2025-12-31', '2026-09-30', '2026-10-23', '2026-10-30']
D2_USDJPY_V = [150.00, 151.20, 151.50, 152.75]
D2_GOLD_V = [2400.0, 2430.0, 2440.0, 2450.0]
D1_SERIES_DATES = ['2025-12-31', '2026-09-30', '2026-10-22', '2026-10-29']
D1_USDJPY_V = [150.00, 150.80, 151.90, 152.10]
D1_GOLD_V = [2400.0, 2430.0, 2435.0, 2440.0]

DAY_D2 = {
    "ymd": "20261102",
    "obs_global": "2026-10-30", "obs_macro": "2026-10-29",
    "obs_rate": "2026-10-30", "obs_china": "2026-10-30",
    "usdjpy": {"value": 152.75, "dates": D2_SERIES_DATES, "values": D2_USDJPY_V},
    "gold": {"value": 2450.00, "dates": D2_SERIES_DATES, "values": D2_GOLD_V},
    "ust10": {"value": 5.04, "dates": ["2026-10-22", "2026-10-29"],
              "values": [5.01, 5.04]},
    "ust2": {"value": 4.58, "dates": ["2026-10-22", "2026-10-29"],
             "values": [4.66, 4.58]},
    "dfedtarl": 4.25, "dfedtaru": 4.50, "dff": 4.33,
    "bei10": 2.31, "zq_price": 95.70,
}
DAY_D1 = {
    "ymd": "20261101",
    "obs_global": "2026-10-29", "obs_macro": "2026-10-28",
    "obs_rate": "2026-10-29", "obs_china": "2026-10-29",
    "usdjpy": {"value": 152.10, "dates": D1_SERIES_DATES, "values": D1_USDJPY_V},
    "gold": {"value": 2440.00, "dates": D1_SERIES_DATES, "values": D1_GOLD_V},
    "ust10": {"value": 4.90, "dates": ["2026-10-21", "2026-10-28"],
              "values": [4.95, 4.90]},
    "ust2": {"value": 4.50, "dates": ["2026-10-21", "2026-10-28"],
             "values": [4.55, 4.50]},
    "dfedtarl": 4.25, "dfedtaru": 4.50, "dff": 4.33,
    "bei10": 2.31, "zq_price": 95.70,
}

# 预期值字面量(手算:/tmp/b2_precalc.py引擎原语预演核验后誊写)
V_D2 = {"MB-1": 4.25, "MB-2": 4.50, "MB-3": 4.33, "MB-4": 4.58, "MB-5": 5.04,
        "MB-7": 152.75, "MB-10": 0.8251, "MB-11": 1.8333}
V_D1 = {"MB-1": 4.25, "MB-2": 4.50, "MB-3": 4.33, "MB-4": 4.50, "MB-5": 4.90,
        "MB-7": 152.10, "MB-10": 0.1317, "MB-11": 1.4}
OP3_D2 = 0.46
OP3_D1 = 0.40
USDJPY_MTD_D2 = 1.0251
UST10_WEEK_PP = 0.03
UST2_WEEK_PP = -0.08
GOLD_WEEK_PCT = 0.4098          # (2450/2440−1)×100
GOLD_LEVELDIFF = 10.0           # 2450−2440(基准值路径,≠字段0.4098)
CORR_USDJPY_GOLD = 0.4675       # pearson(日收益率,共同窗3样本)
JP_OP1 = -3.625                 # 0.75−(4.25+4.50)/2
JP_OP2 = -3.34                  # 1.70−5.04


# ══ 核心覆盖fixture生成器(注册表驱动;数值=range中点或场景字面量) ══════════

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
    """写一日四通道合成采集档(SYNTHETIC;注册表枚举核心覆盖,tests/test_snapshot.py同构)。"""
    reg = fe.load_registry()                      # S1身份层(真实注册表,先例同构)
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
        elif src == "macro_collector" and "(derived)" not in src:
            if mid == "CURVE_2S10S":
                continue                           # A3场景: 本期无该指标事实
            if "(derived)" in str(m.get("source_symbol")):
                continue     # NFP_MOM_K等: compute_derived独占生产,文件层不重复立事实
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
            elif mid == "BEI_10Y":
                item = {"value": day["bei10"], "date": day["obs_macro"],
                        "frequency": "daily"}
            elif mid == "NFP":
                item = {"value": 160000, "date": "2026-10-01", "frequency": "monthly",
                        "series": {"dates": ["2026-08-01", "2026-09-01", "2026-10-01"],
                                   "values": [159800, 159900, 160000]}}
            elif mid == "CPI":
                item = {"value": 322, "date": "2026-10-01", "frequency": "monthly",
                        "series": {"dates": ["2026-08-01", "2026-09-01", "2026-10-01"],
                                   "values": [320, 321, 322]}}
            macro_data[mid] = item
    with open(os.path.join(td, f"global_{day['ymd']}.json"), "w") as f:
        json.dump({"date": day["ymd"], "time": "07:12:00",
                   "count": len(global_data), "data": global_data}, f)
    with open(os.path.join(td, f"macro_{day['ymd']}.json"), "w") as f:
        json.dump({"date": day["ymd"], "data": macro_data, "derived": {}}, f)
    # china: 五指数+AH溢价+成交额(南向/两融/估值缺席→非核心缺失→DEGRADED披露)
    cn_reg = {m["metric_id"]: m for m in metrics
              if m.get("source") == "china_market_collector"}
    indices = {}
    for mid, label in sb._CHINA_LABEL.items():
        if mid in cn_reg:
            indices[label] = {"name": label, "close": _mid(cn_reg[mid]),
                              "week_chg": 0.5, "date": day["obs_china"]}
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
             "diff_from_current": -0.10, "signal": "宽松", "date": day["obs_rate"]}],
        "real_economy": {
            "UNRATE": {"name": "失业率", "value": unrate_mid, "date": "2026-10-01", "freq": "月度"},
            "UMCSENT": {"name": "消费者信心", "value": umc_mid, "date": "2026-10-01", "freq": "月度"}}}
    with open(os.path.join(td, f"rate_economy_{day['ymd']}.json"), "w") as f:
        json.dump(rate_json, f)


# ══ 手工快照/事实/IR构造器(注入面测试) ═══════════════════════════════════

def hfact(mid, value, obs, src="macro_20261105.json", quality="PASS",
          derived=None, calc_ref=None):
    """手工事实(SYNTHETIC;仅携带执行器消费字段)。"""
    return {"metric_id": mid, "fact_id": f"{mid}@{obs}", "value": value,
            "observation_date": obs, "quality_status": quality,
            "source": {"collector": "synthetic", "file": src},
            "derived": derived, "calculation_ref": calc_ref}


def hsnap(gate="PASS", sid="research_snapshot_20261105", facts=None,
          sources=None, store=None):
    snap = {"snapshot_id": sid, "research_as_of": "2026-11-05T08:00:00+08:00",
            "target_date": sid[len("research_snapshot_"):][:8],   # 剥离_vN(R1身份核验)
            "sources_status": sources if sources is not None else {
                ch: {"status": "EXACT", "file": f"{ch}_{sid[-8:]}.json"}
                for ch in ("global", "macro", "china", "rate_economy")},
            "facts": facts or [], "gate_a": {"status": gate}}
    if store is not None:
        snap["series_store"] = store
    return snap


def _pb(bid, mid, role="level", window=None, field="value"):
    return {"binding_id": bid, "metric_id": mid, "role": role, "window": window,
            "field": field, "status": qir.PENDING_EXECUTION,
            "absence_reason": None, "provenance": None}


def _pop(oid, op_type, operands, formula, unit,
         status=qir.PENDING_EXECUTION, calc_ref="公式: 合成;执行器落定"):
    return {"op_id": oid, "op_type": op_type, "operands": operands,
            "formula": formula, "unit": unit, "status": status,
            "result": None, "calculation_ref": calc_ref}


def hand_ir(bindings, ops, question="合成问题", as_of=None):
    ir = {"query_id": "QB-20261105-001", "created_at": CREATED_AT, "mode": "B",
          "question_text": question, "as_of": as_of, "target_snapshot_id": None,
          "metric_bindings": bindings, "derived_operations": ops,
          "unresolved_entities": [], "answer_constraints": AC}
    assert qir.validate_ir(ir, stage="mapped") == [], "hand_ir基底非法"
    return ir


def golden_ir(as_of=None):
    return eqm.map_question(GOLDEN_Q, created_at=CREATED_AT, as_of=as_of,
                            registry=FIXTURE_REGISTRY)


def write_snapshot_file(td, snap):
    with open(os.path.join(td, snap["snapshot_id"] + ".json"), "w") as f:
        json.dump(snap, f)


def quiet_build(ymd, td, as_of):
    """S1 write=False构建(静默stdout;build内部warnings不入断言)。"""
    buf = io.StringIO()
    with redirect_stdout(buf):
        snap = sb.build_snapshot(target_ymd=ymd, data_dir=td, write=False,
                                 as_of=as_of, trusted_root=td)
    return snap


# ══ T0 fixture/生成器自检 ═════════════════════════════════════════════════

class TestFixtureSanity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        write_day_files(cls.td.name, DAY_D1)
        write_day_files(cls.td.name, DAY_D2)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def test_fixture_registry_structure(self):
        self.assertEqual(len(FIXTURE_METRICS), 8)
        self.assertTrue(all(m.get("source") for m in FIXTURE_METRICS))
        self.assertEqual(FIXTURE_REGISTRY["by_id"]["USDJPY"]["unit"], "jpy_per_usd")

    def test_generator_core_covering_gate_degraded(self):
        """注册表驱动核心覆盖: core_missing空→非FAIL;非核心缺席→DEGRADED如实。"""
        snap = quiet_build("20261102", self.td.name, "2026-11-02")
        self.assertEqual(snap["gate_a"]["status"], "DEGRADED")
        self.assertEqual(snap["gate_a"]["core_missing"], [])
        self.assertEqual(snap["gate_a"]["core_fail"], [])

    def test_generator_derived_facts_present(self):
        snap = quiet_build("20261102", self.td.name, "2026-11-02")
        ids = {f["metric_id"] for f in snap["facts"]}
        for mid in ("NFP_MOM_K", "REAL_10Y", "ZQ_IMPLIED_AVG", "USDJPY", "GOLD_F"):
            self.assertIn(mid, ids, f"{mid}应经S1管线在场")
        self.assertNotIn("CURVE_2S10S", ids)       # A3场景蓄意缺席

    def test_generator_series_store(self):
        snap = quiet_build("20261102", self.td.name, "2026-11-02")
        store = snap.get("series_store") or {}
        self.assertEqual(store["USDJPY"]["values"], D2_USDJPY_V)
        self.assertEqual(store["GOLD_F"]["values"], D2_GOLD_V)
        self.assertNotIn("CCC_OAS", store)         # 宏观序列不经store(结构边界)

    def test_generator_two_days_distinct(self):
        s1 = quiet_build("20261101", self.td.name, "2026-11-01")
        f1 = {f["metric_id"]: f for f in s1["facts"]}
        self.assertEqual(f1["USDJPY"]["value"], 152.10)
        self.assertEqual(f1["USDJPY"]["observation_date"], "2026-10-29")
        self.assertEqual(f1["UST_10Y"]["observation_date"], "2026-10-28")

    def test_golden_execution_deterministic(self):
        ir = golden_ir(as_of="2026-11-02")
        r1 = ex.execute_query(ir, daily_dir=self.td.name, trusted_root=self.td.name,
                              registry=FIXTURE_REGISTRY)
        r2 = ex.execute_query(ir, daily_dir=self.td.name, trusted_root=self.td.name,
                              registry=FIXTURE_REGISTRY)
        self.assertEqual(r1["values"], r2["values"])
        self.assertEqual(r1["ir"], r2["ir"])


# ══ T1 黄金E2E(要点①: S1 write=False绑定+OP-3执行) ═══════════════════════

class TestGoldenEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        write_day_files(cls.td.name, DAY_D1)
        write_day_files(cls.td.name, DAY_D2)
        cls.result = ex.execute_query(
            golden_ir(as_of="2026-11-02"), daily_dir=cls.td.name,
            trusted_root=cls.td.name, registry=FIXTURE_REGISTRY)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def test_values_all_literals(self):
        """要点④: 全绑定值=硬编码字面量(手算,零自证)。"""
        self.assertEqual(self.result["values"], V_D2)

    def test_op3_computed_with_maturity_disclosure(self):
        op3 = {o["op_id"]: o for o in self.result["ir"]["derived_operations"]}["OP-3"]
        self.assertEqual(op3["status"], "COMPUTED")
        self.assertEqual(op3["result"], OP3_D2)
        self.assertIn("UST_10Y − UST_2Y(查询期计算", op3["calculation_ref"])
        self.assertIn("输入观测日2026-10-29,2026-10-29", op3["calculation_ref"])
        self.assertIn("期限匹配(观测日一致,E11纪律)", op3["calculation_ref"])

    def test_op1_op2_no_data_preserved(self):
        """要点②: mapper期NO_DATA终态原样保留,calc_ref零追加。"""
        ops = {o["op_id"]: o for o in self.result["ir"]["derived_operations"]}
        for oid in ("OP-1", "OP-2"):
            self.assertEqual(ops[oid]["status"], "NO_DATA")
            self.assertIsNone(ops[oid]["result"])
            self.assertTrue(ops[oid]["calculation_ref"].endswith(
                "operand缺席→NO_DATA不部分计算(DESIGN §三(c))"))
            self.assertEqual(ops[oid]["calculation_ref"].count("operand缺席"), 1)

    def test_mb6_curve_absent_data(self):
        mb = {b["binding_id"]: b for b in self.result["ir"]["metric_bindings"]}
        self.assertEqual(mb["MB-6"]["status"], "ABSENT_DATA")
        self.assertEqual(mb["MB-6"]["absence_reason"], "本期无该指标事实")

    def test_mb8_mb9_absent_registry_preserved(self):
        mb = {b["binding_id"]: b for b in self.result["ir"]["metric_bindings"]}
        self.assertEqual(mb["MB-8"]["status"], "ABSENT_REGISTRY")
        self.assertEqual(mb["MB-8"]["metric_id"], None)
        self.assertEqual(mb["MB-8"]["absence_reason"],
                         "日本政策利率不在注册表(8指标,INVENTORY G-01)")
        self.assertEqual(mb["MB-9"]["absence_reason"],
                         "JGB 10Y不在注册表(8指标,INVENTORY G-01)")

    def test_no_refusal_gate_degraded_bound(self):
        self.assertNotIn("refusal", self.result)
        self.assertEqual(self.result["gate_status"], "DEGRADED")
        self.assertEqual(self.result["snapshot_id"], "research_snapshot_20261102")
        self.assertEqual(self.result["ir"]["target_snapshot_id"],
                         "research_snapshot_20261102")

    def test_executed_ir_passes_schema_zero_pending(self):
        self.assertEqual(qir.validate_ir(self.result["ir"], stage="executed"), [])
        for b in self.result["ir"]["metric_bindings"]:
            self.assertNotEqual(b["status"], qir.PENDING_EXECUTION)
        for o in self.result["ir"]["derived_operations"]:
            self.assertNotEqual(o["status"], qir.PENDING_EXECUTION)

    def test_provenance_grounded(self):
        mb = {b["binding_id"]: b for b in self.result["ir"]["metric_bindings"]}
        p = mb["MB-5"]["provenance"]
        self.assertEqual(p["fact_id"], "UST_10Y@2026-10-29")
        self.assertEqual(p["observation_date"], "2026-10-29")
        self.assertEqual(p["source_file"], "macro_20261102.json")
        self.assertEqual(p["snapshot_id"], "research_snapshot_20261102")
        self.assertIn(p["quality_status"], qir.QUALITY_STATUS)
        wp = mb["MB-10"]["provenance"]
        self.assertIn("窗口week.pct_change", wp["calculation_ref"])
        self.assertIn("基准2026-10-23", wp["calculation_ref"])

    def test_input_ir_zero_mutation(self):
        ir = golden_ir(as_of="2026-11-02")
        before = json.dumps(ir, sort_keys=True)
        ex.execute_query(ir, daily_dir=self.td.name, trusted_root=self.td.name,
                         registry=FIXTURE_REGISTRY)
        self.assertEqual(json.dumps(ir, sort_keys=True), before)
        self.assertIsNone(ir["target_snapshot_id"])
        self.assertTrue(all(b["provenance"] is None for b in ir["metric_bindings"]))

    def test_result_is_deep_copy(self):
        ir = golden_ir(as_of="2026-11-02")
        r = ex.execute_query(ir, daily_dir=self.td.name, trusted_root=self.td.name,
                             registry=FIXTURE_REGISTRY)
        self.assertIsNot(r["ir"], ir)
        self.assertIsNot(r["ir"]["metric_bindings"][0], ir["metric_bindings"][0])

    def test_values_keys_exactly_resolved(self):
        """零填0纪律: values键集=RESOLVED绑定集(缺席绑定零占位)。"""
        resolved = {b["binding_id"] for b in self.result["ir"]["metric_bindings"]
                    if b["status"] == "RESOLVED"}
        self.assertEqual(set(self.result["values"]), resolved)
        for bid in ("MB-6", "MB-8", "MB-9"):
            self.assertNotIn(bid, self.result["values"])


# ══ T2 as_of两时点只读锚定(要点③) ═══════════════════════════════════════

class TestAsOfAnchoring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        write_day_files(cls.td.name, DAY_D1)
        write_day_files(cls.td.name, DAY_D2)
        cls.r1 = ex.execute_query(golden_ir(as_of="2026-11-01"),
                                  daily_dir=cls.td.name, trusted_root=cls.td.name,
                                  registry=FIXTURE_REGISTRY)
        cls.r2 = ex.execute_query(golden_ir(as_of="2026-11-02"),
                                  daily_dir=cls.td.name, trusted_root=cls.td.name,
                                  registry=FIXTURE_REGISTRY)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def test_d1_anchored_values(self):
        self.assertEqual(self.r1["values"], V_D1)
        self.assertEqual(self.r1["snapshot_id"], "research_snapshot_20261101")
        ops = {o["op_id"]: o for o in self.r1["ir"]["derived_operations"]}
        self.assertEqual(ops["OP-3"]["result"], OP3_D1)

    def test_d1_d2_no_period_mixing(self):
        """同目录两日档并存: 值随as_of切换,晚期数据不混入早期锚点。"""
        self.assertNotEqual(self.r1["values"]["MB-7"], self.r2["values"]["MB-7"])
        self.assertNotEqual(self.r1["values"]["MB-10"], self.r2["values"]["MB-10"])
        mb1 = {b["binding_id"]: b for b in self.r1["ir"]["metric_bindings"]}
        self.assertEqual(mb1["MB-7"]["provenance"]["observation_date"], "2026-10-29")
        self.assertEqual(mb1["MB-5"]["provenance"]["observation_date"], "2026-10-28")
        self.assertEqual(mb1["MB-10"]["provenance"]["calculation_ref"],
                         "窗口week.pct_change;基准2026-10-22(E3口径)")

    def test_usdjpy_mtd_window_d2(self):
        ir = hand_ir([_pb("MB-1", "USDJPY", "derived_window", "mtd", "pct_change")],
                     [], as_of="2026-11-02")
        r = ex.execute_query(ir, daily_dir=self.td.name, trusted_root=self.td.name,
                             registry=FIXTURE_REGISTRY)
        self.assertEqual(r["values"], {"MB-1": USDJPY_MTD_D2})

    def test_as_of_before_any_files_refused(self):
        r = ex.execute_query(golden_ir(as_of="2026-10-15"),
                             daily_dir=self.td.name, trusted_root=self.td.name,
                             registry=FIXTURE_REGISTRY)
        self.assertIn("refusal", r)
        self.assertEqual(r["values"], {})
        self.assertIn("FAIL", r["refusal"])

    def test_invalid_as_of_fail_loud(self):
        ir = golden_ir()
        ir["as_of"] = "2026-13-40T00:00"          # 通过schema形状,日期非法→E4拒绝
        with self.assertRaises(ValueError) as cm:
            ex.execute_query(ir, daily_dir=self.td.name, trusted_root=self.td.name,
                             registry=FIXTURE_REGISTRY)
        self.assertIn("as_of非法", str(cm.exception))


# ══ T3 引擎口径一致性(要点④: 执行器vs引擎直算vs字面量) ═══════════════════

class TestEngineConsistency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        write_day_files(cls.td.name, DAY_D2)
        cls.snap = quiet_build("20261102", cls.td.name, "2026-11-02")

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def _exec(self, ir):
        return ex.execute_query(ir, snapshot=self.snap, registry=FIXTURE_REGISTRY)

    def test_usdjpy_windows_equal_engine_direct(self):
        r = fe.compute_period_returns(D2_SERIES_DATES, D2_USDJPY_V, "jpy_per_usd",
                                      "US", as_of="2026-11-02")
        self.assertEqual(r["week"]["pct_change"], 0.8251)
        self.assertEqual(r["mtd"]["pct_change"], 1.0251)
        self.assertEqual(r["ytd"]["pct_change"], 1.8333)
        ir = hand_ir([_pb("MB-1", "USDJPY", "derived_window", "week", "pct_change"),
                      _pb("MB-2", "USDJPY", "derived_window", "mtd", "pct_change"),
                      _pb("MB-3", "USDJPY", "derived_window", "ytd", "pct_change")],
                     [], as_of="2026-11-02")
        self.assertEqual(self._exec(ir)["values"],
                         {"MB-1": r["week"]["pct_change"],
                          "MB-2": r["mtd"]["pct_change"],
                          "MB-3": r["ytd"]["pct_change"]})

    def test_ust_week_pp_equal_engine_direct(self):
        r10 = fe.compute_period_returns(DAY_D2["ust10"]["dates"],
                                        DAY_D2["ust10"]["values"],
                                        "percent", "US", as_of="2026-11-02")
        r2 = fe.compute_period_returns(DAY_D2["ust2"]["dates"],
                                       DAY_D2["ust2"]["values"],
                                       "percent", "US", as_of="2026-11-02")
        self.assertEqual(r10["week"]["pp_change"], UST10_WEEK_PP)
        self.assertEqual(r2["week"]["pp_change"], UST2_WEEK_PP)
        ir = hand_ir([_pb("MB-1", "UST_10Y", "derived_window", "week", "pp_change"),
                      _pb("MB-2", "UST_2Y", "derived_window", "week", "pp_change")],
                     [], as_of="2026-11-02")
        self.assertEqual(self._exec(ir)["values"],
                         {"MB-1": UST10_WEEK_PP, "MB-2": UST2_WEEK_PP})

    def test_gold_week_pct_and_level_diff_basis(self):
        rg = fe.compute_period_returns(D2_SERIES_DATES, D2_GOLD_V, "usd_per_oz",
                                       "US", as_of="2026-11-02")
        self.assertEqual(rg["week"]["pct_change"], GOLD_WEEK_PCT)
        ir = hand_ir([_pb("MB-1", "GOLD_F"),
                      _pb("MB-2", "GOLD_F", "derived_window", "week", "pct_change")],
                     [_pop("OP-1", "level_diff", ["MB-1", "MB-2"],
                           "GOLD_F.level − week基准", "usd_per_oz")],
                     as_of="2026-11-02")
        r = ex.execute_query(ir, snapshot=self.snap, registry=CCC_REGISTRY)
        self.assertEqual(r["values"]["MB-2"], GOLD_WEEK_PCT)
        op = r["ir"]["derived_operations"][0]
        self.assertEqual(op["result"], GOLD_LEVELDIFF)   # 2450−2440≠字段0.4098
        self.assertIn("两时点=2026-10-30 vs 窗口基准2026-10-23", op["calculation_ref"])

    def test_spread_equal_engine_free_literal(self):
        ir = hand_ir([_pb("MB-1", "UST_10Y"), _pb("MB-2", "UST_2Y")],
                     [_pop("OP-1", "spread", ["MB-1", "MB-2"],
                           "UST_10Y − UST_2Y", "percentage_point")],
                     as_of="2026-11-02")
        r = self._exec(ir)
        self.assertEqual(r["ir"]["derived_operations"][0]["result"],
                         round(5.04 - 4.58, 4))
        self.assertEqual(r["ir"]["derived_operations"][0]["result"], OP3_D2)

    def test_correlation_equal_cc_direct(self):
        pair, common = cc.paired_returns({"dates": D2_SERIES_DATES, "values": D2_USDJPY_V},
                                         {"dates": D2_SERIES_DATES, "values": D2_GOLD_V})
        ra, rb = pair
        self.assertEqual(round(cc.pearson(ra, rb), 4), CORR_USDJPY_GOLD)
        ir = hand_ir([_pb("MB-1", "USDJPY"), _pb("MB-2", "GOLD_F")],
                     [_pop("OP-1", "correlation", ["MB-1", "MB-2"],
                           "corr(USDJPY,GOLD_F)", "dimensionless")],
                     as_of="2026-11-02")
        r = ex.execute_query(ir, snapshot=self.snap, registry=CCC_REGISTRY)
        self.assertEqual(r["ir"]["derived_operations"][0]["result"], CORR_USDJPY_GOLD)


# ══ T4 四级缺席(要点②/§三(c)) ═══════════════════════════════════════════

class TestAbsenceFourLevels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        write_day_files(cls.td.name, DAY_D2)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def test_a1_executor_side_registry_defense(self):
        """mapper/executor注册表漂移: 执行器侧A1防御+NO_DATA传导。"""
        ir = golden_ir(as_of="2026-11-02")
        metrics = [m for m in FIXTURE_METRICS if m["metric_id"] != "UST_2Y"]
        drifted = {"metrics": metrics, "by_id": {m["metric_id"]: m for m in metrics}}
        r = ex.execute_query(ir, daily_dir=self.td.name, trusted_root=self.td.name,
                             registry=drifted)
        mb = {b["binding_id"]: b for b in r["ir"]["metric_bindings"]}
        self.assertEqual(mb["MB-4"]["status"], "ABSENT_REGISTRY")
        self.assertIsNone(mb["MB-4"]["metric_id"])
        self.assertEqual(mb["MB-4"]["absence_reason"], "UST_2Y不在注册表(7指标)")
        op3 = {o["op_id"]: o for o in r["ir"]["derived_operations"]}["OP-3"]
        self.assertEqual(op3["status"], "NO_DATA")
        self.assertIsNone(op3["result"])
        self.assertIn("operand缺席→NO_DATA不部分计算(执行器", op3["calculation_ref"])

    def test_a2_channel_missing_via_r1_file(self):
        snap = hsnap(gate="DEGRADED", sid="research_snapshot_20261104",
                     facts=[hfact("UST_10Y", 5.04, "2026-10-30",
                                  src="macro_20261104.json")],
                     sources={"global": {"status": "EXACT"},
                              "macro": {"status": "EXACT"},
                              "china": {"status": "EXACT"},
                              "rate_economy": {"status": "MISSING"}})
        td2 = tempfile.TemporaryDirectory()
        self.addCleanup(td2.cleanup)
        write_snapshot_file(td2.name, snap)
        ir = eqm.map_question("美联储利率现在多少", created_at=CREATED_AT,
                              as_of="2026-11-04", registry=FIXTURE_REGISTRY)
        r = ex.execute_query(ir, daily_dir=td2.name, trusted_root=td2.name,
                             registry=FIXTURE_REGISTRY)
        for b in r["ir"]["metric_bindings"]:
            self.assertEqual(b["status"], "ABSENT_SOURCE", b["binding_id"])
            self.assertEqual(b["absence_reason"],
                             "指标已注册但当日采集缺失(通道rate_economy状态MISSING)")
        self.assertEqual(r["values"], {})

    def test_a2_read_fail_variant(self):
        snap = hsnap(gate="DEGRADED", sid="research_snapshot_20261103",
                     facts=[], sources={"rate_economy": {"status": "READ_FAIL"}})
        r = ex.execute_query(golden_ir(), snapshot=snap, registry=FIXTURE_REGISTRY)
        mb = {b["binding_id"]: b for b in r["ir"]["metric_bindings"]}
        self.assertEqual(mb["MB-1"]["status"], "ABSENT_SOURCE")
        self.assertIn("通道rate_economy状态READ_FAIL", mb["MB-1"]["absence_reason"])

    def test_a3_registered_channel_ok_no_fact(self):
        snap = hsnap(gate="DEGRADED", facts=[])   # 通道全EXACT而事实空
        r = ex.execute_query(golden_ir(), snapshot=snap, registry=FIXTURE_REGISTRY)
        mb = {b["binding_id"]: b for b in r["ir"]["metric_bindings"]}
        for bid in ("MB-1", "MB-4", "MB-7"):
            self.assertEqual(mb[bid]["status"], "ABSENT_DATA", bid)
        self.assertEqual(mb["MB-4"]["absence_reason"], "本期无该指标事实")

    def test_a4_fact_without_series(self):
        ir = hand_ir([_pb("MB-1", "SPX", "derived_window", "week", "pct_change")],
                     [], as_of="2026-11-02")
        r = ex.execute_query(ir, daily_dir=self.td.name, trusted_root=self.td.name,
                             registry=FIXTURE_REGISTRY)
        b = r["ir"]["metric_bindings"][0]
        self.assertEqual(b["status"], "ABSENT_WINDOW")
        self.assertEqual(b["absence_reason"],
                         "事实无窗口派生(序列缺席,窗口不可用)")

    def test_a4_window_unavailable(self):
        snap = hsnap(facts=[hfact("USDJPY", 152.75, "2026-10-30",
                                  derived={"week": {"available": False,
                                                    "reason": "序列不足3点"}})])
        ir = hand_ir([_pb("MB-1", "USDJPY", "derived_window", "week", "pct_change")], [])
        r = ex.execute_query(ir, snapshot=snap, registry=FIXTURE_REGISTRY)
        b = r["ir"]["metric_bindings"][0]
        self.assertEqual(b["status"], "ABSENT_WINDOW")
        self.assertEqual(b["absence_reason"], "E3窗口不可用: 序列不足3点")

    def test_a4_window_field_missing(self):
        snap = hsnap(facts=[hfact("USDJPY", 152.75, "2026-10-30",
                                  derived={"week": {"available": True,
                                                    "basis_date": "2026-10-23",
                                                    "pct_change": 0.8251}})])
        ir = hand_ir([_pb("MB-1", "USDJPY", "derived_window", "week", "pp_change")], [])
        r = ex.execute_query(ir, snapshot=snap, registry=FIXTURE_REGISTRY)
        b = r["ir"]["metric_bindings"][0]
        self.assertEqual(b["status"], "ABSENT_WINDOW")
        self.assertEqual(b["absence_reason"],
                         "窗口记录无字段pp_change(E3未产出该口径)")


# ══ T5 快照获取(R1既有优先/版本/latest-ymd/注入优先/禁墙钟) ═══════════════

class TestSnapshotAcquisition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        write_day_files(cls.td.name, DAY_D2)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def _r1_snap(self, sid, dfedtarl):
        return hsnap(gate="PASS", sid=sid, facts=[
            hfact("DFEDTARL", dfedtarl, "2026-10-30", src="rate_economy_20261102.json"),
            hfact("DFEDTARU", 4.50, "2026-10-30", src="rate_economy_20261102.json"),
            hfact("DFF", 4.33, "2026-10-30", src="rate_economy_20261102.json"),
            hfact("UST_2Y", 4.58, "2026-10-29", src="macro_20261102.json"),
            hfact("UST_10Y", 5.04, "2026-10-29", src="macro_20261102.json"),
            hfact("USDJPY", 152.75, "2026-10-30", src="global_20261102.json",
                  derived={"week": {"available": True, "basis_date": "2026-10-23",
                                    "pct_change": 0.8251},
                           "ytd": {"available": True, "basis_date": "2025-12-31",
                                   "pct_change": 1.8333}})])

    def test_r1_file_wins_over_s1_build(self):
        td2 = tempfile.TemporaryDirectory()
        self.addCleanup(td2.cleanup)
        write_snapshot_file(td2.name, self._r1_snap("research_snapshot_20261102", 9.99))
        write_day_files(td2.name, DAY_D2)
        r = ex.execute_query(golden_ir(as_of="2026-11-02"), daily_dir=td2.name,
                             trusted_root=td2.name, registry=FIXTURE_REGISTRY)
        self.assertEqual(r["values"]["MB-1"], 9.99)      # R1文件值,非S1重建
        self.assertEqual(r["gate_status"], "PASS")
        self.assertEqual(r["snapshot_id"], "research_snapshot_20261102")

    def test_r1_highest_revision_selected(self):
        td2 = tempfile.TemporaryDirectory()
        self.addCleanup(td2.cleanup)
        write_snapshot_file(td2.name, self._r1_snap("research_snapshot_20261102", 9.99))
        write_snapshot_file(td2.name, self._r1_snap("research_snapshot_20261102_v2", 8.88))
        r = ex.execute_query(golden_ir(as_of="2026-11-02"), daily_dir=td2.name,
                             trusted_root=td2.name, registry=FIXTURE_REGISTRY)
        self.assertEqual(r["values"]["MB-1"], 8.88)
        self.assertEqual(r["snapshot_id"], "research_snapshot_20261102_v2")

    def test_injected_snapshot_wins_over_daily_dir(self):
        snap = self._r1_snap("research_snapshot_20261102", 7.77)
        r = ex.execute_query(golden_ir(as_of="2026-11-02"), snapshot=snap,
                             daily_dir=self.td.name, trusted_root=self.td.name,
                             registry=FIXTURE_REGISTRY)
        self.assertEqual(r["values"]["MB-1"], 7.77)

    def test_as_of_none_binds_latest_ymd_no_wallclock(self):
        td2 = tempfile.TemporaryDirectory()
        self.addCleanup(td2.cleanup)
        write_snapshot_file(td2.name, self._r1_snap("research_snapshot_20261101", 6.66))
        write_snapshot_file(td2.name, self._r1_snap("research_snapshot_20261102", 9.99))
        r = ex.execute_query(golden_ir(), daily_dir=td2.name, trusted_root=td2.name,
                             registry=FIXTURE_REGISTRY)
        self.assertEqual(r["values"]["MB-1"], 9.99)
        self.assertEqual(r["snapshot_id"], "research_snapshot_20261102")

    def test_as_of_none_empty_dir_refused_no_wallclock(self):
        td2 = tempfile.TemporaryDirectory()
        self.addCleanup(td2.cleanup)
        r = ex.execute_query(golden_ir(), daily_dir=td2.name, trusted_root=td2.name,
                             registry=FIXTURE_REGISTRY)
        self.assertIn("refusal", r)
        self.assertIn("禁墙钟", r["refusal"])
        self.assertEqual(r["values"], {})

    def test_no_snapshot_no_dir_refused(self):
        r = ex.execute_query(golden_ir(), registry=FIXTURE_REGISTRY)
        self.assertIn("refusal", r)
        self.assertIn("未注入snapshot且未提供daily_dir", r["refusal"])

    def test_r1_corrupt_falls_back_to_s1(self):
        """R1候选损坏→当日整体拒绝→S1离线构建(write=False)接管。"""
        td2 = tempfile.TemporaryDirectory()
        self.addCleanup(td2.cleanup)
        with open(os.path.join(td2.name, "research_snapshot_20261102.json"), "w") as f:
            f.write("{ not-json !!")
        write_day_files(td2.name, DAY_D2)
        r = ex.execute_query(golden_ir(as_of="2026-11-02"), daily_dir=td2.name,
                             trusted_root=td2.name, registry=FIXTURE_REGISTRY)
        self.assertNotIn("refusal", r)
        self.assertEqual(r["values"]["MB-1"], 4.25)      # S1重建值
        self.assertEqual(r["gate_status"], "DEGRADED")


# ══ T6 门禁R3(放行/拒绝/结构) ════════════════════════════════════════════

class TestGateRefusal(unittest.TestCase):
    def test_gate_fail_refused_zero_partial(self):
        snap = hsnap(gate="FAIL")
        r = ex.execute_query(golden_ir(), snapshot=snap, registry=FIXTURE_REGISTRY)
        self.assertIn("refusal", r)
        self.assertEqual(r["values"], {})
        self.assertIn("不放行正式研究查询", r["refusal"])
        self.assertIsNone(r["ir"]["target_snapshot_id"])
        statuses = [b["status"] for b in r["ir"]["metric_bindings"]]
        self.assertEqual(statuses.count(qir.PENDING_EXECUTION), 9)   # 零部分执行
        self.assertNotIn("values", r["ir"])

    def test_gate_none_refused(self):
        snap = hsnap(gate="PASS")
        snap["gate_a"] = {"status": None}
        r = ex.execute_query(golden_ir(), snapshot=snap, registry=FIXTURE_REGISTRY)
        self.assertIn("refusal", r)

    def test_gate_degraded_and_pass_allowed(self):
        for gate in ("PASS", "DEGRADED"):
            snap = hsnap(gate=gate, facts=[hfact("DFEDTARL", 4.25, "2026-10-30")])
            ir = hand_ir([_pb("MB-1", "DFEDTARL")], [])
            r = ex.execute_query(ir, snapshot=snap, registry=FIXTURE_REGISTRY)
            self.assertNotIn("refusal", r, gate)
            self.assertEqual(r["gate_status"], gate)
            self.assertEqual(r["values"], {"MB-1": 4.25})

    def test_injected_snapshot_not_mutated(self):
        snap = hsnap(facts=[hfact("DFEDTARL", 4.25, "2026-10-30")])
        before = json.dumps(snap, sort_keys=True)
        ex.execute_query(hand_ir([_pb("MB-1", "DFEDTARL")], []), snapshot=snap,
                         registry=FIXTURE_REGISTRY)
        self.assertEqual(json.dumps(snap, sort_keys=True), before)

    def test_non_dict_snapshot_refused(self):
        r = ex.execute_query(golden_ir(), snapshot=["not", "a", "dict"],
                             registry=FIXTURE_REGISTRY)
        self.assertIn("refusal", r)
        self.assertIn("快照结构非法", r["refusal"])


# ══ T7 派生操作(spread/level_diff/correlation) ═══════════════════════════

class TestDerivedOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        write_day_files(cls.td.name, DAY_D2)
        cls.snap = quiet_build("20261102", cls.td.name, "2026-11-02")

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def _jp_snapshot(self, jp_obs="2026-10-30", us_obs="2026-10-30"):
        return hsnap(facts=[
            hfact("JP_POLICY_RATE", 0.75, jp_obs, src="boj_20261105.json"),
            hfact("JGB_10Y", 1.70, jp_obs, src="boj_20261105.json"),
            hfact("DFEDTARL", 4.25, us_obs, src="rate_economy_20261105.json"),
            hfact("DFEDTARU", 4.50, us_obs, src="rate_economy_20261105.json"),
            hfact("DFF", 4.33, us_obs, src="rate_economy_20261105.json"),
            hfact("UST_2Y", 4.58, us_obs, src="macro_20261105.json"),
            hfact("UST_10Y", 5.04, us_obs, src="macro_20261105.json"),
            hfact("CURVE_2S10S", 0.46, us_obs, src="macro_20261105.json"),
            hfact("USDJPY", 152.75, us_obs, src="global_20261105.json",
                  derived={"week": {"available": True, "basis_date": "2026-10-23",
                                    "pct_change": 0.8251},
                           "ytd": {"available": True, "basis_date": "2025-12-31",
                                   "pct_change": 1.8333}})])

    def test_jp_present_spread_computed(self):
        """JP在场(B1对照面): OP-1/OP-2转COMPUTED,3操作数中值族。"""
        ir = eqm.map_question(GOLDEN_Q, created_at=CREATED_AT, registry=JP_REGISTRY)
        r = ex.execute_query(ir, snapshot=self._jp_snapshot(), registry=JP_REGISTRY)
        ops = {o["op_id"]: o for o in r["ir"]["derived_operations"]}
        self.assertEqual(ops["OP-1"]["status"], "COMPUTED")
        self.assertEqual(ops["OP-1"]["result"], JP_OP1)
        self.assertEqual(ops["OP-2"]["status"], "COMPUTED")
        self.assertEqual(ops["OP-2"]["result"], JP_OP2)
        self.assertIn("期限匹配(观测日一致,E11纪律)", ops["OP-1"]["calculation_ref"])

    def test_spread_maturity_mismatch_disclosed(self):
        ir = eqm.map_question(GOLDEN_Q, created_at=CREATED_AT, registry=JP_REGISTRY)
        r = ex.execute_query(ir, snapshot=self._jp_snapshot(jp_obs="2026-10-30",
                                                            us_obs="2026-10-28"),
                             registry=JP_REGISTRY)
        op1 = {o["op_id"]: o for o in r["ir"]["derived_operations"]}["OP-1"]
        self.assertEqual(op1["result"], JP_OP1)
        self.assertIn("观测日不一致(2026-10-28 vs 2026-10-30)", op1["calculation_ref"])
        self.assertIn("差异如实披露不混同", op1["calculation_ref"])

    def test_level_diff_negative_role_combo(self):
        ir = hand_ir([_pb("MB-1", "UST_10Y"), _pb("MB-2", "UST_10Y")],
                     [_pop("OP-1", "level_diff", ["MB-1", "MB-2"],
                           "两level绑定", "percentage_point")])
        with self.assertRaises(ValueError) as cm:
            ex.execute_query(ir, snapshot=self.snap, registry=FIXTURE_REGISTRY)
        self.assertIn("一level绑定+一derived_window绑定", str(cm.exception))

    def test_level_diff_negative_metric_mismatch(self):
        ir = hand_ir([_pb("MB-1", "UST_10Y"),
                      _pb("MB-2", "UST_2Y", "derived_window", "week", "pp_change")],
                     [_pop("OP-1", "level_diff", ["MB-1", "MB-2"],
                           "跨指标", "percentage_point")])
        with self.assertRaises(ValueError) as cm:
            ex.execute_query(ir, snapshot=self.snap, registry=FIXTURE_REGISTRY)
        self.assertIn("须同指标两绑定", str(cm.exception))

    def test_level_diff_basis_missing_no_data(self):
        snap = hsnap(facts=[hfact(
            "UST_10Y", 5.04, "2026-10-29",
            derived={"week": {"available": True, "basis_date": "2026-10-22",
                              "pp_change": 0.03}})])       # 无basis_value
        ir = hand_ir([_pb("MB-1", "UST_10Y"),
                      _pb("MB-2", "UST_10Y", "derived_window", "week", "pp_change")],
                     [_pop("OP-1", "level_diff", ["MB-1", "MB-2"],
                           "UST_10Y两时点", "percentage_point")])
        r = ex.execute_query(ir, snapshot=snap, registry=FIXTURE_REGISTRY)
        op = r["ir"]["derived_operations"][0]
        self.assertEqual(op["status"], "NO_DATA")
        self.assertIsNone(op["result"])
        self.assertIn("窗口基准值缺席→NO_DATA不部分计算", op["calculation_ref"])

    def test_correlation_computed_on_s1_store(self):
        ir = hand_ir([_pb("MB-1", "USDJPY"), _pb("MB-2", "GOLD_F")],
                     [_pop("OP-1", "correlation", ["MB-1", "MB-2"],
                           "corr(USDJPY,GOLD_F)", "dimensionless")])
        r = ex.execute_query(ir, snapshot=self.snap, registry=CCC_REGISTRY)
        op = r["ir"]["derived_operations"][0]
        self.assertEqual(op["status"], "COMPUTED")
        self.assertEqual(op["result"], CORR_USDJPY_GOLD)
        self.assertIn("pearson(日收益率,USDJPY,GOLD_F)", op["calculation_ref"])
        self.assertIn("共同观测窗2026-09-30~2026-10-30", op["calculation_ref"])
        self.assertIn("样本3", op["calculation_ref"])

    def test_correlation_macro_metric_not_in_store(self):
        ir = hand_ir([_pb("MB-1", "CCC_OAS"), _pb("MB-2", "USDJPY")],
                     [_pop("OP-1", "correlation", ["MB-1", "MB-2"],
                           "corr(CCC_OAS,USDJPY)", "dimensionless")])
        r = ex.execute_query(ir, snapshot=self.snap, registry=CCC_REGISTRY)
        op = r["ir"]["derived_operations"][0]
        self.assertEqual(op["status"], "NO_DATA")
        self.assertIn("序列不在快照series_store(macro通道序列不经store",
                      op["calculation_ref"])

    def test_correlation_insufficient_common_window(self):
        snap = hsnap(facts=[hfact("USDJPY", 152.10, "2026-10-29"),
                            hfact("GOLD_F", 2440.0, "2026-10-29")],
                     store={"USDJPY": {"dates": ["2026-10-28", "2026-10-29"],
                                       "values": [152.0, 152.10]},
                            "GOLD_F": {"dates": ["2026-10-28", "2026-10-29"],
                                       "values": [2438.0, 2440.0]}})
        ir = hand_ir([_pb("MB-1", "USDJPY"), _pb("MB-2", "GOLD_F")],
                     [_pop("OP-1", "correlation", ["MB-1", "MB-2"],
                           "corr", "dimensionless")])
        r = ex.execute_query(ir, snapshot=snap, registry=CCC_REGISTRY)
        op = r["ir"]["derived_operations"][0]
        self.assertEqual(op["status"], "NO_DATA")
        self.assertIn("共同观测日不足(<3,C3语义)", op["calculation_ref"])

    def test_correlation_zero_variance_no_data(self):
        snap = hsnap(facts=[hfact("USDJPY", 152.0, "2026-10-29"),
                            hfact("GOLD_F", 2440.0, "2026-10-29")],
                     store={"USDJPY": {"dates": ["2026-10-27", "2026-10-28",
                                                 "2026-10-29"],
                                       "values": [152.0, 152.0, 152.0]},
                            "GOLD_F": {"dates": ["2026-10-27", "2026-10-28",
                                                 "2026-10-29"],
                                       "values": [2430.0, 2435.0, 2440.0]}})
        ir = hand_ir([_pb("MB-1", "USDJPY"), _pb("MB-2", "GOLD_F")],
                     [_pop("OP-1", "correlation", ["MB-1", "MB-2"],
                           "corr", "dimensionless")])
        r = ex.execute_query(ir, snapshot=snap, registry=CCC_REGISTRY)
        op = r["ir"]["derived_operations"][0]
        self.assertEqual(op["status"], "NO_DATA")
        self.assertIn("零方差或样本不足(C4语义)", op["calculation_ref"])

    def test_invalid_op_type_rejected_at_schema(self):
        ir = hand_ir([_pb("MB-1", "DFEDTARL"), _pb("MB-2", "DFEDTARU")],
                     [_pop("OP-1", "spread", ["MB-1", "MB-2"], "f", "percent")])
        ir["derived_operations"][0]["op_type"] = "ratio"
        with self.assertRaises(ValueError) as cm:
            ex.execute_query(ir, snapshot=hsnap(facts=[
                hfact("DFEDTARL", 4.25, "2026-10-30"),
                hfact("DFEDTARU", 4.50, "2026-10-30")]),
                registry=FIXTURE_REGISTRY)
        self.assertIn("mapped schema", str(cm.exception))


# ══ T8 纯度/接线(源码级锁) ═══════════════════════════════════════════════

EXECUTOR_SOURCE = open(os.path.join(ROOT, "scripts", "e2eb_query_executor.py"),
                       encoding="utf-8").read()
# 纯度检查对象=纯代码(docstring中的纪律文字提及不作命中;T8自检用)
EXECUTOR_CODE = re.sub(r'"""[\s\S]*?"""', '""', EXECUTOR_SOURCE)


class TestPurityAndWiring(unittest.TestCase):
    def test_no_network_surface(self):
        for pat in ("requests", "urllib", "socket", "http.client", "httpx",
                    "subprocess", "websocket"):
            self.assertNotIn(pat, EXECUTOR_SOURCE, f"网络面零容忍: {pat}")

    def test_no_collector_file_io(self):
        """数据入口纪律: 零open()/零glob调用;唯一IO=os.listdir枚举快照层文件名。"""
        self.assertNotIn("open(", EXECUTOR_CODE)
        self.assertIsNone(re.search(r"\bglob\b", EXECUTOR_CODE))   # 'global'不误伤
        self.assertIn("os.listdir", EXECUTOR_CODE)

    def test_no_wall_clock(self):
        for pat in ("datetime.now", "date.today", "time.time", "utcnow"):
            self.assertNotIn(pat, EXECUTOR_CODE, f"禁墙钟: {pat}")

    def test_wiring_reuses_established_interfaces(self):
        """接线锁: R1/R3/S1/E1复用(零复制);IR经B1模块;不import映射器。"""
        self.assertIn("rp.select_snapshot", EXECUTOR_SOURCE)
        self.assertIn("rp.gate_allows_formal_research", EXECUTOR_SOURCE)
        self.assertIn("sb.build_snapshot", EXECUTOR_SOURCE)
        self.assertIn("fe.load_registry", EXECUTOR_SOURCE)
        self.assertIn("qir.validate_ir", EXECUTOR_SOURCE)
        self.assertIn("cc.paired_returns", EXECUTOR_SOURCE)
        self.assertIn("cc.pearson", EXECUTOR_SOURCE)
        self.assertIn("fe.parse_iso_date", EXECUTOR_SOURCE)
        self.assertNotIn("import e2eb_query_mapper", EXECUTOR_SOURCE)

    def test_absence_reason_no_invented_numbers(self):
        """缺席措辞纪律: 模板常量不含编造数值(缺值如实缺席零填0)。"""
        for tmpl in (ex.REASON_ABSENT_SOURCE, ex.REASON_ABSENT_DATA,
                     ex.REASON_ABSENT_DATA_DERIVED, ex.REASON_ABSENT_WINDOW_NO_SERIES,
                     ex.REASON_ABSENT_WINDOW_NO_FIELD):
            self.assertNotIn("0.0", tmpl)
            self.assertNotIn("=0", tmpl)


# ══ T9 fail-loud ══════════════════════════════════════════════════════════

class TestFailLoud(unittest.TestCase):
    def test_invalid_mapped_ir_rejected(self):
        ir = golden_ir()
        del ir["metric_bindings"][0]["metric_id"]      # 缺必填字段
        with self.assertRaises(ValueError) as cm:
            ex.execute_query(ir, snapshot=hsnap(), registry=FIXTURE_REGISTRY)
        self.assertIn("mapped schema", str(cm.exception))

    def test_executed_output_sabotage_detected(self):
        """D-B2-13: 产出必过executed schema——注入非法终态被fail-loud拦截。"""
        snap = hsnap(facts=[hfact("DFEDTARL", 4.25, "2026-10-30"),
                            hfact("DFEDTARU", 4.50, "2026-10-30")])
        ir = hand_ir([_pb("MB-1", "DFEDTARL"), _pb("MB-2", "DFEDTARU")],
                     [_pop("OP-1", "spread", ["MB-1", "MB-2"], "f", "percent")])

        def sabotage(op, bindings, values):
            op["result"] = 42.0
            op["status"] = "BANANA"                    # 枚举外终态
        with mock.patch.object(ex, "_execute_spread", side_effect=sabotage):
            with self.assertRaises(ValueError) as cm:
                ex.execute_query(ir, snapshot=snap, registry=FIXTURE_REGISTRY)
        self.assertIn("executed schema", str(cm.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
