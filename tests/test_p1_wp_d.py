# -*- coding: utf-8 -*-
"""IA-P1-WP-D(P1 查询面与共享档案衔接)专项测试。

合同 IA-P1-WP-D-AC-v1.1;DESIGN docs/P1_DESIGN.md §六 L172 验收要点:
- ① IR schema 扩展单测(economy 过滤+接地标识强制)【测试】→ T1/T1b;
- ② W-1/W-2 端到端用例: 缺席→「无数据」+差距登记断言【测试】→ T2
  (场景定义=P1_DESIGN §三(d) L88-113 实读锚定: W-1=EA 缺席主导链/
  W-2=CN 混合链;合同注记「§四 L88-115」为节号笔误,行号锚定正确,
  见 docs/P1_WP_D_REPORT.md §零.4 勘误登记);
- ③ 档案记录附 snapshot_id+digest 的校验【测试】→ T3。

数据纪律(AC-03): 合成 fixture 为唯一数据源(本文件内定义),不读
config/metric_registry.json 与 data/daily 任何真实档;预期值一律字面量
硬编码(手算/预计算,不从被测模块导入计算);零网络/零新增第三方依赖。
digest 预期值=2026-11-06 离线预计算字面量(预计算脚本
/tmp/p1-wp-d-evidence/_precompute_digest.py,fixture 定义处见下)。
"""
import copy
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import e2eb_query_ir as qir              # noqa: E402 (M-a 被测面)
import e2eb_query_mapper as eqm          # noqa: E402 (M-b 被测面)
import e2eb_query_executor as qex        # noqa: E402 (M-d 被测面)
import research_archive as ra            # noqa: E402 (M-c 被测面)

# ══ 合成 fixture(唯一数据源;AC-03.3;fixture→预期值映射见 DELIVERY 专节) ══

CREATED_AT = "2026-11-06T09:00:00+08:00"
ARCHIVED_AT = "2026-11-06T01:00:00+00:00"
W1_Q = "欧央行与美联储政策立场的分化,及其对EURUSD与欧元股的传导。"
W2_Q = "中国增长与政策组合对人民币汇率与中资股的传导。"
GOLDEN_Q = ("美日政策利率差和10年期国债收益率差最近怎么样?"
            "和美元兑日元走势合起来看是什么状态?")
AC_LITERAL = {"grounding_required": True, "no_data_policy": "report_absence"}


def _regm(mid, display, unit, source, calc=None):
    """合成 registry 条目(mapper 用 display/calc/unit;executor 用 source)。"""
    return {"metric_id": mid, "display_name": display, "calc": calc,
            "unit": unit, "source": source}


def _registry(metrics):
    return {"metrics": list(metrics),
            "by_id": {m["metric_id"]: m for m in metrics}}


# mapper 用最小合成 registry(经济体现测不依赖条目;economy=NL cue 识别)
MAPPER_REG = _registry([
    _regm("DFEDTARL", "联邦基金目标区间下限", "percent", "rate_expectations"),
    _regm("DFF", "有效联邦基金利率(日频)", "percent", "rate_expectations"),
    _regm("USDJPY", "美元兑日元", "jpy_per_usd", "global_market_collector"),
    _regm("SPX", "标普500指数", "index_point", "global_market_collector"),
])

# W-1 形态1 registry(US+global 族在场,EA 三指标零注册=设计时点复现,§三(d) L95-97)
W1_REG_FORM1 = _registry([
    _regm("DFF", "有效联邦基金利率(日频)", "percent", "rate_expectations"),
    _regm("DFEDTARL", "联邦基金目标区间下限", "percent", "rate_expectations"),
    _regm("DFEDTARU", "联邦基金目标区间上限", "percent", "rate_expectations"),
    _regm("UST_10Y", "10年期美债收益率", "percent", "macro_collector"),
    _regm("EURUSD", "欧元兑美元", "eur_per_usd", "global_market_collector"),
    _regm("EZU", "iShares MSCI欧元区ETF", "index_point", "global_market_collector"),
])

# W-1 形态2 registry(WP-A 落地后形态: EA 指标注册在场,source=ea_market_collector)
W1_REG_FORM2 = _registry(list(W1_REG_FORM1["metrics"]) + [
    _regm("ECB_DFR", "欧央行存款便利利率", "percent", "ea_market_collector"),
    _regm("BUND_10Y", "德国10年期国债收益率", "percent", "ea_market_collector"),
    _regm("EA_HICP_YOY", "欧元区HICP同比", "percent", "ea_market_collector"),
])

# W-2 registry(在场4+SHCOMP 注册在场;中国CPI/LPR/7天逆回购零注册,§三(d) L104/L112)
W2_REG = _registry([
    _regm("USDCNY", "美元兑人民币", "cny_per_usd", "global_market_collector"),
    _regm("FXI", "iShares中国大盘ETF", "index_point", "global_market_collector"),
    _regm("HSI", "恒生指数", "index_point", "china_market_collector"),
    _regm("HSAHP", "恒生A股溢价指数", "index_point", "china_market_collector"),
    _regm("SHCOMP", "上证综指", "index_point", "china_market_collector"),
])


def _fact(mid, value, obs_date, src_file):
    return {"fact_id": "%s@%s" % (mid, obs_date), "metric_id": mid, "value": value,
            "observation_date": obs_date, "source": {"file": src_file},
            "quality_status": "PASS",
            "calculation_ref": "合成fixture事实(P1_DESIGN §三(d) W-1/W-2 走查值)"}


# 合成快照(在场值=DESIGN §三(d) L92-99/L106-109 走查值作合成输入;ea/jp 通道 MISSING)
W1_SNAP = {
    "snapshot_id": "research_snapshot_20261102",
    "gate_a": {"status": "PASS"},
    "sources_status": {
        "rate_economy": {"status": "OK"},
        "macro": {"status": "OK"},
        "global": {"status": "OK"},
        "china": {"status": "OK"},
        "jp": {"status": "MISSING"},
        "ea": {"status": "MISSING"},
    },
    "facts": [
        _fact("DFF", 3.88, "2026-10-29", "rate_economy_20261102.json"),
        _fact("DFEDTARL", 3.75, "2026-11-01", "rate_economy_20261102.json"),
        _fact("DFEDTARU", 4.00, "2026-11-01", "rate_economy_20261102.json"),
        _fact("UST_10Y", 4.98, "2026-10-29", "macro_20261102.json"),
        _fact("EURUSD", 1.12, "2026-10-30", "global_20261102.json"),
        _fact("EZU", 65.16, "2026-10-30", "global_20261102.json"),
        _fact("USDCNY", 6.64, "2026-11-01", "global_20261102.json"),
        _fact("FXI", 33.08, "2026-10-30", "global_20261102.json"),
        _fact("HSI", 23294.42, "2026-10-30", "china_20261102.json"),
        _fact("HSAHP", 132.49, "2026-10-30", "china_20261102.json"),
    ],
}

# 变体1: ea 通道 OK 但无 EA 事实(A3 退化归因面)
W1_SNAP_EA_OK = copy.deepcopy(W1_SNAP)
W1_SNAP_EA_OK["sources_status"]["ea"] = {"status": "OK"}
# 变体2: 篡改快照(末条事实被删;digest 与 W1_SNAP 必然不同→verify 拒)
TAMPERED_SNAP = copy.deepcopy(W1_SNAP)
TAMPERED_SNAP["facts"] = TAMPERED_SNAP["facts"][:-1]

DIGEST_W1 = "758ad6f9ef881eb1"        # [预计算字面量·2026-11-06 离线 sha256 前16]
DIGEST_W1_EA_OK = "758abb9bdbeccb82"  # [预计算字面量]


# ══ IR/记录构造 helper(单缺陷注入基底) ══

def _mb(n, mid, role="level", status="PENDING_EXECUTION", reason=None):
    return {"binding_id": "MB-%d" % n, "metric_id": mid, "role": role, "window": None,
            "field": "value", "status": status, "absence_reason": reason,
            "provenance": None}


def _mapped_ir(bindings, ops=(), unresolved=(), economy=None,
               question=W1_Q, qid="QB-20261106-001"):
    ir = {"query_id": qid, "created_at": CREATED_AT, "mode": "B",
          "question_text": question, "as_of": None, "target_snapshot_id": None,
          "metric_bindings": list(bindings), "derived_operations": list(ops),
          "unresolved_entities": list(unresolved),
          "answer_constraints": dict(AC_LITERAL)}
    if economy is not None:
        ir["economy"] = economy
    return ir


def _ea_provenance(**over):
    p = {"metric_id": "ECB_DFR", "snapshot_id": "research_snapshot_20261102",
         "fact_id": "ECB_DFR@2026-10-30", "observation_date": "2026-10-30",
         "source_file": "ea_20261102.json", "quality_status": "PASS",
         "calculation_ref": "合成fixture事实"}
    p.update(over)
    return p


def _record(**over):
    ir = over.pop("ir", None) or _mapped_ir([])
    rec = {"record_type": "query_history", "query_id": ir["query_id"],
           "created_at": CREATED_AT, "mode": "B",
           "question_text": ir["question_text"], "as_of": None,
           "snapshot_id": "research_snapshot_20261102",
           "digest_snapshot": DIGEST_W1,
           "ir": ir, "ir_stage": "mapped",
           "answer_summary": {"ir_stage": "mapped", "refusal": None,
                              "binding_status_counts": {}, "op_status_counts": {},
                              "n_unresolved": 0, "values": {}},
           "promoted_to_task_id": None,
           "archived_at": ARCHIVED_AT}
    rec.update(over)
    return rec


# W-1 形态1 mapped IR(§三(d) L90 指标清单: US 4+EA 3 缺席+EURUSD/EZU;差距登记=L95-97)
def _w1_form1_ir():
    return _mapped_ir([
        _mb(1, "DFF"), _mb(2, "DFEDTARL"), _mb(3, "DFEDTARU"), _mb(4, "UST_10Y"),
        _mb(5, None, role="spread_component", status="ABSENT_REGISTRY",
            reason="ECB_DFR不在注册表(6指标,G-P1-01→承接包WP-P1-A)"),
        _mb(6, None, role="spread_component", status="ABSENT_REGISTRY",
            reason="BUND_10Y不在注册表(6指标,G-P1-02→承接包WP-P1-A)"),
        _mb(7, None, role="spread_component", status="ABSENT_REGISTRY",
            reason="EA_HICP_YOY不在注册表(6指标,G-P1-03→承接包WP-P1-A)"),
        _mb(8, "EURUSD"), _mb(9, "EZU"),
    ], economy=None, question=W1_Q)


# W-2 mapped IR(§三(d) L104 清单: 在场4+SHCOMP 注册在场+中国宏观3 零注册;L110-112)
def _w2_ir():
    return _mapped_ir([
        _mb(1, "USDCNY"), _mb(2, "FXI"), _mb(3, "HSI"), _mb(4, "HSAHP"),
        _mb(5, "SHCOMP"),
        _mb(6, None, status="ABSENT_REGISTRY",
            reason="中国CPI不在注册表(5指标,G-P1-15→承接包WP-P1-E)"),
        _mb(7, None, status="ABSENT_REGISTRY",
            reason="LPR不在注册表(5指标,G-P1-14→承接包WP-P1-E)"),
        _mb(8, None, status="ABSENT_REGISTRY",
            reason="7天逆回购不在注册表(5指标,G-P1-18→承接包WP-P1-E)"),
    ], economy="CN", question=W2_Q)


# ══ T0 fixture 自检 ══

class TestT0Fixture(unittest.TestCase):
    def test_t00_fixture_structure(self):
        self.assertEqual(len(W1_SNAP["facts"]), 10)                  # 字面量
        self.assertEqual(sorted(W1_SNAP["sources_status"]),
                         ["china", "ea", "global", "jp", "macro", "rate_economy"])
        self.assertEqual(len(W1_REG_FORM1["metrics"]), 6)
        self.assertEqual(len(W1_REG_FORM2["metrics"]), 9)
        self.assertEqual(len(W2_REG["metrics"]), 5)
        self.assertEqual(W1_SNAP_EA_OK["sources_status"]["ea"]["status"], "OK")
        self.assertNotEqual(DIGEST_W1, DIGEST_W1_EA_OK)              # 内容→digest 唯一


# ══ T1 要点①: IR schema 扩展(economy 过滤+接地标识强制) ══

class TestT1IRSchemaEconomy(unittest.TestCase):
    def test_t01_economies_enum_literal(self):
        self.assertEqual(qir.ECONOMIES,
                         ("US", "CN", "JP", "EA", "HK", "GLOBAL"))  # 手写字面量

    def test_t02_mapped_ir_with_economy_valid(self):
        ir = _mapped_ir([_mb(1, "ECB_DFR")], economy="EA")
        self.assertEqual(qir.validate_ir(ir, stage="mapped"), [])

    def test_t03_executed_ir_with_economy_valid(self):
        ir = _mapped_ir([_mb(1, "ECB_DFR", status="RESOLVED",
                             reason=None)], economy="EA")
        ir["metric_bindings"][0]["provenance"] = _ea_provenance()
        ir["target_snapshot_id"] = "research_snapshot_20261102"
        self.assertEqual(qir.validate_ir(ir, stage="executed"), [])

    def test_t04_ir_economy_none_valid(self):
        ir = _mapped_ir([_mb(1, "ECB_DFR")], economy=None)
        ir["economy"] = None
        self.assertEqual(qir.validate_ir(ir, stage="mapped"), [])

    def test_t05_ir_without_economy_key_valid(self):
        """旧形态兼容: 键缺席=不过滤,合法(PD-2)。"""
        ir = _mapped_ir([_mb(1, "ECB_DFR")])
        self.assertNotIn("economy", ir)
        self.assertEqual(qir.validate_ir(ir, stage="mapped"), [])

    def test_t06_ir_economy_bad_enum_rejected(self):
        ir = _mapped_ir([_mb(1, "ECB_DFR")])
        ir["economy"] = "EU"                    # 枚举外(欧元区非英文缩写EU)
        issues = qir.validate_ir(ir, stage="mapped")
        self.assertEqual(len(issues), 1)
        self.assertIn("economy须为", issues[0])

    def test_t07_grounding_forced_ea_resolved_without_provenance(self):
        """接地标识强制(DESIGN §四 L134 四经济体统一适用): RESOLVED 无 provenance→拒。"""
        ir = _mapped_ir([_mb(1, "ECB_DFR", status="RESOLVED")], economy="EA")
        ir["target_snapshot_id"] = "research_snapshot_20261102"
        issues = qir.validate_ir(ir, stage="executed")
        self.assertTrue(any("RESOLVED时provenance必填" in s for s in issues))

    def test_t08_grounding_valid_ea_resolved_with_provenance(self):
        """接地标识: EA 指标 RESOLVED 携完整 provenance(metric/snapshot/fact/观测日)→合法。"""
        ir = _mapped_ir([_mb(1, "ECB_DFR", status="RESOLVED")], economy="EA")
        ir["metric_bindings"][0]["provenance"] = _ea_provenance()
        ir["target_snapshot_id"] = "research_snapshot_20261102"
        self.assertEqual(qir.validate_ir(ir, stage="executed"), [])


# ══ T1b mapper economy 识别与传参(PD-3/PD-4) ══

class TestT1bMapperEconomy(unittest.TestCase):
    def _map(self, q):
        return eqm.map_question(q, created_at=CREATED_AT, registry=MAPPER_REG)

    def test_t09_mapper_single_family_ea(self):
        self.assertEqual(self._map("欧元区通胀最近走势怎么样?")["economy"], "EA")

    def test_t10_mapper_single_family_cn(self):
        self.assertEqual(self._map("中国A股最近表现如何?")["economy"], "CN")

    def test_t11_mapper_single_family_jp(self):
        self.assertEqual(self._map("日经指数近期走势")["economy"], "JP")

    def test_t12_mapper_single_family_us(self):
        self.assertEqual(self._map("美国最新的通胀数据如何?")["economy"], "US")

    def test_t13_mapper_concept_rule_fired_no_economy(self):
        """跨经济体比较链(概念规则触发)不设单过滤维度(PD-4;golden 整 dict 断言兼容面)。"""
        ir = self._map(GOLDEN_Q)
        self.assertNotIn("economy", ir)

    def test_t14_mapper_multi_family_no_economy(self):
        self.assertNotIn("economy", self._map("欧元区与美国的政策分化怎么看?"))

    def test_t15_mapper_zero_family_no_economy(self):
        self.assertNotIn("economy", self._map("黄金价格走势如何?"))


# ══ T2 要点②: W-1/W-2 端到端(缺席→「无数据」+差距登记) ══

class TestT2W1EAChain(unittest.TestCase):
    def test_t16_w1_form1_ea_absent_registry_chain(self):
        """W-1 形态1(设计时点复现): EA 三指标零注册→ABSENT_REGISTRY 差距登记原样保留,
        在场侧 RESOLVED,values 零编造(缺席→「无数据」)。"""
        result = qex.execute_query(_w1_form1_ir(), snapshot=W1_SNAP,
                                   registry=W1_REG_FORM1)
        ex_ir = result["ir"]
        self.assertEqual(qir.validate_ir(ex_ir, stage="executed"), [])
        by_id = {b["binding_id"]: b for b in ex_ir["metric_bindings"]}
        for n, mid_name in ((5, "ECB_DFR"), (6, "BUND_10Y"), (7, "EA_HICP_YOY")):
            b = by_id["MB-%d" % n]
            self.assertEqual(b["status"], "ABSENT_REGISTRY")
            self.assertIsNone(b["metric_id"])
            self.assertIn(mid_name + "不在注册表", b["absence_reason"])
            self.assertIn("G-P1-0", b["absence_reason"])       # 差距编号登记
            self.assertIsNone(b["provenance"])                 # 缺席零接地伪造
        self.assertEqual(by_id["MB-1"]["status"], "RESOLVED")
        self.assertEqual(by_id["MB-8"]["status"], "RESOLVED")
        self.assertEqual(result["values"],
                         {"MB-1": 3.88, "MB-2": 3.75, "MB-3": 4.00,
                          "MB-4": 4.98, "MB-8": 1.12, "MB-9": 65.16})  # 手算字面量
        for n in (1, 8):
            prov = by_id["MB-%d" % n]["provenance"]
            self.assertEqual(prov["snapshot_id"], "research_snapshot_20261102")
            self.assertTrue(prov["fact_id"])                    # 接地标识在场

    def test_t17_w1_form2_ea_channel_missing_a2(self):
        """W-1 形态2(WP-A 后): EA 注册在场+通道 MISSING→ABSENT_SOURCE 通道归因
        (PD-6 CHANNEL_OF_SOURCE 新键),values 零输出。"""
        ir = _mapped_ir([_mb(1, "ECB_DFR")], economy="EA")
        result = qex.execute_query(ir, snapshot=W1_SNAP, registry=W1_REG_FORM2)
        b = result["ir"]["metric_bindings"][0]
        self.assertEqual(b["status"], "ABSENT_SOURCE")
        self.assertIn("通道ea", b["absence_reason"])
        self.assertIn("MISSING", b["absence_reason"])
        self.assertEqual(result["values"], {})

    def test_t18_w1_form2_channel_ok_no_fact_a3(self):
        """通道 OK 但本期无 EA 事实→ABSENT_DATA 如实退化(禁填0)。"""
        ir = _mapped_ir([_mb(1, "ECB_DFR")], economy="EA")
        result = qex.execute_query(ir, snapshot=W1_SNAP_EA_OK,
                                   registry=W1_REG_FORM2)
        b = result["ir"]["metric_bindings"][0]
        self.assertEqual(b["status"], "ABSENT_DATA")
        self.assertIn("本期无该指标事实", b["absence_reason"])
        self.assertEqual(result["values"], {})


class TestT2W2CNChain(unittest.TestCase):
    def test_t19_w2_cn_mixed_chain(self):
        """W-2 CN 混合链: 在场4条 RESOLVED+SHCOMP ABSENT_DATA+中国宏观3 ABSENT_REGISTRY;
        CN 基本面结论=数据不足不可判形态(缺席指标零数值,§三(d) L113)。"""
        result = qex.execute_query(_w2_ir(), snapshot=W1_SNAP, registry=W2_REG)
        ex_ir = result["ir"]
        self.assertEqual(qir.validate_ir(ex_ir, stage="executed"), [])
        by_id = {b["binding_id"]: b for b in ex_ir["metric_bindings"]}
        self.assertEqual(by_id["MB-1"]["status"], "RESOLVED")
        self.assertEqual(by_id["MB-4"]["status"], "RESOLVED")
        self.assertEqual(by_id["MB-5"]["status"], "ABSENT_DATA")
        self.assertIn("本期无该指标事实", by_id["MB-5"]["absence_reason"])
        self.assertEqual(result["values"],
                         {"MB-1": 6.64, "MB-2": 33.08,
                          "MB-3": 23294.42, "MB-4": 132.49})    # 手算字面量

    def test_t20_w2_gap_registration_all_reasons_nonempty(self):
        """差距登记断言(两级形态): 全部缺席绑定 reason 非空;映射期 ABSENT_REGISTRY
        含 G-P1 差距编号,执行期 ABSENT_DATA 含事实归因;executed IR 自洽。"""
        result = qex.execute_query(_w2_ir(), snapshot=W1_SNAP, registry=W2_REG)
        absent = [b for b in result["ir"]["metric_bindings"]
                  if b["status"].startswith("ABSENT")]
        self.assertEqual(len(absent), 4)
        for b in absent:
            self.assertTrue(b["absence_reason"])
        registry_gaps = [b for b in absent if b["status"] == "ABSENT_REGISTRY"]
        self.assertEqual(len(registry_gaps), 3)
        for b in registry_gaps:
            self.assertIn("G-P1-1", b["absence_reason"])        # G-P1-14/15/18 族
        data_gap = [b for b in absent if b["status"] == "ABSENT_DATA"]
        self.assertEqual(len(data_gap), 1)
        self.assertIn("本期无该指标事实", data_gap[0]["absence_reason"])
        self.assertEqual(result["ir"]["economy"], "CN")


# ══ T3 要点③: 档案记录附 snapshot_id+digest 的校验 ══

class TestT3ArchiveBinding(unittest.TestCase):
    def test_t21_w1_full_chain_archive_economy_echo(self):
        """W-1 全链(执行→归档→验证): economy echo 落地+snapshot_id/digest 绑定复算通过。"""
        with tempfile.TemporaryDirectory() as td:
            snap_path = os.path.join(td, "research_snapshot_20261102.json")
            with open(snap_path, 'w', encoding='utf-8') as f:
                json.dump(W1_SNAP, f, ensure_ascii=False)
            result = qex.execute_query(
                _mapped_ir([_mb(1, "ECB_DFR")], economy="EA"),
                snapshot=W1_SNAP, registry=W1_REG_FORM2)
            status, path = ra.append_query_record(
                result["ir"], snapshot=W1_SNAP, archive_dir=td, execution=result,
                archived_at=ARCHIVED_AT)
            self.assertEqual(status, ra.STATUS_WRITTEN)
            rec = ra.load_query_record("QB-20261106-001", archive_dir=td)
            self.assertEqual(rec["economy"], "EA")               # echo 落地(L142)
            ok, issues = ra.verify_query_record(rec, td, archive_dir=td)
            self.assertTrue(ok, issues)                          # digest 复算通过

    def test_t22_archive_tampered_snapshot_digest_mismatch(self):
        """篡改快照→digest 不匹配→verify 拒(内容级绑定防漂移)。"""
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "research_snapshot_20261102.json"),
                      'w', encoding='utf-8') as f:
                json.dump(W1_SNAP, f, ensure_ascii=False)
            result = qex.execute_query(
                _mapped_ir([_mb(1, "DFF")], economy=None),
                snapshot=W1_SNAP, registry=W1_REG_FORM1)
            ra.append_query_record(result["ir"], snapshot=W1_SNAP,
                                    archive_dir=td, execution=result,
                                    archived_at=ARCHIVED_AT)
            # 篡改: 快照内容改动(末条事实被删)后重写同文件
            with open(os.path.join(td, "research_snapshot_20261102.json"),
                      'w', encoding='utf-8') as f:
                json.dump(TAMPERED_SNAP, f, ensure_ascii=False)
            ok, issues = ra.verify_query_record("QB-20261106-001", td,
                                                archive_dir=td)
            self.assertFalse(ok)
            self.assertTrue(any("digest不匹配" in s for s in issues))

    def test_t23_record_carries_snapshot_id_and_digest_literal(self):
        """append 产记录必携 snapshot_id+digest_snapshot(QUERY_RECORD_KEYS 必附面);
        digest=预计算字面量(R5 sha256 前16,fixture 内容绑定)。"""
        with tempfile.TemporaryDirectory() as td:
            result = qex.execute_query(
                _mapped_ir([_mb(1, "ECB_DFR")], economy="EA"),
                snapshot=W1_SNAP, registry=W1_REG_FORM2)
            status, _ = ra.append_query_record(
                result["ir"], snapshot=W1_SNAP, archive_dir=td, execution=result,
                archived_at=ARCHIVED_AT)
            self.assertEqual(status, ra.STATUS_WRITTEN)
            rec = ra.load_query_record("QB-20261106-001", archive_dir=td)
            self.assertEqual(rec["snapshot_id"], "research_snapshot_20261102")
            self.assertEqual(rec["digest_snapshot"], DIGEST_W1)  # 预计算字面量

    def test_t24_validate_economy_echo_ok(self):
        self.assertEqual(ra.validate_query_record(
            _record(economy="EA", ir=_mapped_ir([], economy="EA"))), [])

    def test_t25_validate_economy_bad_enum(self):
        issues = ra.validate_query_record(_record(economy="XX"))
        self.assertTrue(any("economy须为" in s for s in issues))

    def test_t26_validate_missing_echo_when_ir_has_economy(self):
        """衔接设计 L142: IR 携经济体维度而记录未 echo→拒。"""
        issues = ra.validate_query_record(_record(ir=_mapped_ir([], economy="EA")))
        self.assertTrue(any("未echo" in s for s in issues))

    def test_t27_validate_economy_mismatch(self):
        issues = ra.validate_query_record(
            _record(economy="US", ir=_mapped_ir([], economy="EA")))
        self.assertTrue(any("不一致" in s for s in issues))

    def test_t28_legacy_record_without_economy_valid(self):
        """旧形态兼容: 记录与 IR 均无 economy→零 issue。"""
        self.assertEqual(ra.validate_query_record(_record()), [])

    def test_t29_id_conventions_qb_rt_four_economy_context(self):
        """QB-/RT- 引用约定(§四 L140)四经济体语境证成: W-1 记录晋升 RT- 合法形态。"""
        self.assertEqual(ra.validate_id_conventions(query_id="QB-20261106-001"), [])
        self.assertEqual(ra.validate_id_conventions(
            query_id="QB-20261106-001", promoted_to_task_id="RT-20261106-001"), [])
        self.assertTrue(ra.validate_id_conventions(query_id="QB-XXXX-1"))
        self.assertTrue(ra.validate_id_conventions(task_id="RT-"))
        self.assertEqual(ra.validate_id_conventions(
            origin_query_id="QB-20261106-001", task_id="RT-20261106-002"), [])


if __name__ == "__main__":
    unittest.main()
