# -*- coding: utf-8 -*-
"""IA-P03-E2EB-WP-B1(E2E-B 首个实现包)专项测试。

合同 IA-P03-E2EB-WP-B1-AC-v1.0(DESIGN §六 WP-B1 行 L210-214 验收要点):
- 要点① IR字段级schema校验用例(validate_ir 两阶段规则/枚举/ID格式/跨引用);
- 要点② §三(d)问题文本→IR映射黄金用例(含 MB-8/MB-9 ABSENT_REGISTRY 断言);
- 要点③ unresolved_entities负向用例(禁交易类问题→out_of_scope);
- 要点④ 模块SHA登记(落 docs/P03_E2EB_B1_REPORT.md §五,非本文件)。

数据纪律(AC-03/D-B1-11): 合成 fixture 注册表为唯一数据源(8条=7场景指标+1无关
SPX;JP在场变体+2条=10;US缺席变体-1条=7);**不读**真实 config/metric_registry.json
与 data/daily 任何档。**预期值一律字面量硬编码**(手算,不从被测模块导入计算——
自证恒真是 F 反例)。零网络/零新增第三方依赖: import 面纯标准库+项目既有模块;
两新模块源码级零网络锁+禁直读原始采集档锁(见 T5)。
"""
import os
import sys
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import e2eb_query_ir as qir                    # noqa: E402
import e2eb_query_mapper as eqm                # noqa: E402
import fact_engine as fe                       # noqa: E402 (E4/单位常量引用)

# ══ 合成 fixture 注册表(唯一数据源;D-B1-11) ═══════════════════════════
FIXTURE_METRICS = [
    {"metric_id": "DFEDTARL", "display_name": "联邦基金目标区间下限",
     "calc": "FOMC目标区间下限", "unit": "percent"},
    {"metric_id": "DFEDTARU", "display_name": "联邦基金目标区间上限",
     "calc": "FOMC目标区间上限", "unit": "percent"},
    {"metric_id": "DFF", "display_name": "有效联邦基金利率(日频)",
     "calc": "NYFed每日有效联邦基金利率", "unit": "percent"},
    {"metric_id": "UST_2Y", "display_name": "2年期美债收益率",
     "calc": "FRED系列最新观测", "unit": "percent"},
    {"metric_id": "UST_10Y", "display_name": "10年期美债收益率",
     "calc": "FRED系列最新观测", "unit": "percent"},
    {"metric_id": "CURVE_2S10S", "display_name": "2s10s期限利差",
     "calc": "FRED系列最新观测", "unit": "percentage_point"},
    {"metric_id": "USDJPY", "display_name": "美元兑日元",
     "calc": "即期汇率", "unit": "jpy_per_usd"},
    {"metric_id": "SPX", "display_name": "标普500指数",
     "calc": None, "unit": "index_point"},
]
FIXTURE_REGISTRY = {"metrics": FIXTURE_METRICS,
                    "by_id": {m["metric_id"]: m for m in FIXTURE_METRICS}}

# JP在场变体(WP-B3前瞻: 缺席=发现而非硬编码的对照面)
JP_METRICS = [
    {"metric_id": "JP_POLICY_RATE", "display_name": "日本政策利率(日银政策目标)",
     "calc": None, "unit": "percent"},
    {"metric_id": "JGB_10Y", "display_name": "日本10年期国债收益率(JGB 10Y)",
     "calc": None, "unit": "percent"},
]

# DESIGN §三(d) 第一环问题文本(L134 逐字)
GOLDEN_Q = "美日政策利率差和10年期国债收益率差最近怎么样?和美元兑日元走势合起来看是什么状态?"
CREATED_AT = "2026-11-05T12:00:00+08:00"

AC = {"grounding_required": True, "no_data_policy": "report_absence"}   # P-12字面量


def golden_ir():
    return eqm.map_question(GOLDEN_Q, created_at=CREATED_AT, registry=FIXTURE_REGISTRY)


def _mapped_ir(**over):
    """schema负向用例基底: 最小合法mapped IR,单缺陷注入后断言恰1条issue。"""
    ir = {
        "query_id": "QB-20261105-001", "created_at": CREATED_AT, "mode": "B",
        "question_text": "示例问题", "as_of": None, "target_snapshot_id": None,
        "metric_bindings": [{"binding_id": "MB-1", "metric_id": "DFEDTARL",
                             "role": "level", "window": None, "field": "value",
                             "status": "PENDING_EXECUTION", "absence_reason": None,
                             "provenance": None}],
        "derived_operations": [], "unresolved_entities": [],
        "answer_constraints": dict(AC),
    }
    ir.update(over)
    return ir


def _binding(**over):
    b = {"binding_id": "MB-1", "metric_id": "DFEDTARL", "role": "level",
         "window": None, "field": "value", "status": "PENDING_EXECUTION",
         "absence_reason": None, "provenance": None}
    b.update(over)
    return b


def _provenance(**over):
    p = {"metric_id": "DFEDTARL", "snapshot_id": "research_snapshot_20261102",
         "fact_id": "DFEDTARL@2026-11-01", "observation_date": "2026-11-01",
         "source_file": "rate_economy_20261102.json", "quality_status": "PASS",
         "calculation_ref": None}
    p.update(over)
    return p


def _op(**over):
    o = {"op_id": "OP-1", "op_type": "spread", "operands": ["MB-1", "MB-2"],
         "formula": "UST_10Y − UST_2Y", "unit": "percentage_point",
         "status": "NO_DATA", "result": None,
         "calculation_ref": "公式: UST_10Y − UST_2Y;operand缺席→NO_DATA"}
    o.update(over)
    return o


def _executed_ir(**over):
    """executed阶段负向用例基底: 两个RESOLVED绑定+一个COMPUTED派生,单缺陷注入。"""
    ir = {
        "query_id": "QB-20261105-001", "created_at": CREATED_AT, "mode": "B",
        "question_text": "示例问题", "as_of": None, "target_snapshot_id": None,
        "metric_bindings": [
            _binding(binding_id="MB-1", status="RESOLVED", provenance=_provenance()),
            _binding(binding_id="MB-2", metric_id="UST_2Y", status="RESOLVED",
                     provenance=_provenance(
                         metric_id="UST_2Y", fact_id="UST_2Y@2026-10-29",
                         observation_date="2026-10-29",
                         source_file="macro_20261102.json")),
        ],
        "derived_operations": [
            _op(status="COMPUTED", result=0.37,
                calculation_ref="公式: UST_10Y − UST_2Y @观测日2026-10-29")],
        "unresolved_entities": [],
        "answer_constraints": dict(AC),
    }
    ir.update(over)
    return ir


# ══ T0 fixture自检 ═════════════════════════════════════════════════════

class TestFixtureSanity(unittest.TestCase):
    def test_fixture_structure(self):
        self.assertEqual(len(FIXTURE_METRICS), 8)             # 字面量
        self.assertEqual(len(FIXTURE_REGISTRY["by_id"]), 8)
        self.assertEqual(len({m["metric_id"] for m in FIXTURE_METRICS}), 8)
        # 场景7指标单位字面量(与真实注册表实取一致,REPORT §一登记)
        units = {m["metric_id"]: m["unit"] for m in FIXTURE_METRICS}
        self.assertEqual(units["DFEDTARL"], "percent")
        self.assertEqual(units["CURVE_2S10S"], "percentage_point")
        self.assertEqual(units["USDJPY"], "jpy_per_usd")
        # fixture零日本侧身份(对照INVENTORY G-01实测语义)
        hay = "|".join((m["display_name"] or "") + "|" + (m["calc"] or "")
                       for m in FIXTURE_METRICS)
        for term in ("JGB", "日银", "BOJ", "日本政策利率", "日本国债"):
            self.assertNotIn(term, hay)


# ══ T1 IR schema校验(要点①) ═══════════════════════════════════════════

class TestIRSchemaValid(unittest.TestCase):
    def test_valid_mapped(self):
        self.assertEqual(qir.validate_ir(_mapped_ir(), stage="mapped"), [])

    def test_valid_executed(self):
        ir = _mapped_ir(
            metric_bindings=[
                _binding(binding_id="MB-1", status="RESOLVED",
                         provenance=_provenance()),
                _binding(binding_id="MB-2", metric_id="UST_2Y", status="RESOLVED",
                         provenance=_provenance(
                             metric_id="UST_2Y", fact_id="UST_2Y@2026-10-29",
                             observation_date="2026-10-29",
                             source_file="macro_20261102.json",
                             quality_status="DEGRADED")),
            ],
            derived_operations=[_op(op_id="OP-1", status="COMPUTED", result=0.37,
                                    operands=["MB-1", "MB-2"],
                                    calculation_ref="公式: UST_10Y − UST_2Y @观测日2026-10-29")],
        )
        self.assertEqual(qir.validate_ir(ir, stage="executed"), [])


class TestIRSchemaNegative(unittest.TestCase):
    """单缺陷注入→恰1条issue(预期issue关键词字面量)。"""

    def check(self, ir, keyword, stage="mapped"):
        issues = qir.validate_ir(ir, stage=stage)
        self.assertEqual(len(issues), 1, f"应恰1条issue,实得{issues}")
        self.assertIn(keyword, issues[0])

    def test_bad_query_id(self):
        self.check(_mapped_ir(query_id="QB-2026-11-01"), "query_id格式非法")

    def test_bad_mode(self):
        self.check(_mapped_ir(mode="A"), "mode恒须字面量")

    def test_empty_question(self):
        self.check(_mapped_ir(question_text=""), "question_text")

    def test_bad_role(self):
        self.check(_mapped_ir(metric_bindings=[_binding(role="quant")]), "role枚举外值")

    def test_derived_window_requires_window(self):
        self.check(_mapped_ir(metric_bindings=[_binding(role="derived_window",
                                                        window=None)]),
                   "window必填")

    def test_window_only_for_derived_window(self):
        self.check(_mapped_ir(metric_bindings=[_binding(window="week")]),
                   "仅derived_window可携")

    def test_bad_window_enum(self):
        self.check(_mapped_ir(metric_bindings=[_binding(role="derived_window",
                                                        window="qtd")]),
                   "window枚举外值")

    def test_bad_field(self):
        self.check(_mapped_ir(metric_bindings=[_binding(field="raw")]), "field枚举外值")

    def test_resolved_forbidden_at_mapped(self):
        self.check(_mapped_ir(metric_bindings=[_binding(status="RESOLVED",
                                                        provenance=_provenance())]),
                   "status非法于stage=mapped")

    def test_pending_with_provenance(self):
        self.check(_mapped_ir(metric_bindings=[_binding(provenance=_provenance())]),
                   "provenance须为None")

    def test_absent_without_reason(self):
        self.check(_mapped_ir(metric_bindings=[_binding(status="ABSENT_REGISTRY",
                                                        metric_id=None)]),
                   "absence_reason非空")

    def test_absent_registry_with_metric_id(self):
        self.check(_mapped_ir(metric_bindings=[_binding(
            status="ABSENT_REGISTRY", metric_id="X",
            absence_reason="x不在注册表")]), "metric_id须None")

    def test_absent_source_requires_metric_id(self):
        self.check(_mapped_ir(metric_bindings=[_binding(
            status="ABSENT_SOURCE", metric_id=None, absence_reason="通道缺失")]),
                   "metric_id须非None")

    def test_pending_forbidden_at_executed(self):
        self.check(_mapped_ir(), "status非法于stage=executed", stage="executed")

    def test_resolved_requires_provenance_executed(self):
        self.check(_mapped_ir(metric_bindings=[_binding(status="RESOLVED")]),
                   "provenance必填", stage="executed")

    def test_bad_fact_id(self):
        self.check(_mapped_ir(metric_bindings=[_binding(
            status="RESOLVED", provenance=_provenance(fact_id="DFEDTARL-2026-11-01"))]),
                   "fact_id格式非法", stage="executed")

    def test_bad_snapshot_id(self):
        self.check(_mapped_ir(metric_bindings=[_binding(
            status="RESOLVED",
            provenance=_provenance(snapshot_id="snap_20261102"))]),
                   "snapshot_id格式非法", stage="executed")

    def test_bad_quality_status(self):
        self.check(_mapped_ir(metric_bindings=[_binding(
            status="RESOLVED", provenance=_provenance(quality_status="GOOD"))]),
                   "quality_status枚举外值", stage="executed")

    def test_provenance_metric_id_mismatch(self):
        self.check(_mapped_ir(metric_bindings=[_binding(
            status="RESOLVED", provenance=_provenance(metric_id="OTHER"))]),
                   "须与binding.metric_id一致", stage="executed")

    def test_bad_op_type(self):
        self.check(_mapped_ir(metric_bindings=[_binding(), _binding(binding_id="MB-2")],
                              derived_operations=[_op(op_type="ratio")]),
                   "op_type枚举外值")

    def test_no_data_with_result(self):
        self.check(_mapped_ir(metric_bindings=[_binding(), _binding(binding_id="MB-2")],
                              derived_operations=[_op(result=0.5)]),
                   "result须None")

    def test_computed_null_result_executed(self):
        self.check(_executed_ir(derived_operations=[
            _op(status="COMPUTED", result=None,
                calculation_ref="公式: UST_10Y − UST_2Y @观测日2026-10-29")]),
            "result须为数值", stage="executed")

    def test_computed_without_calc_ref_executed(self):
        self.check(_executed_ir(derived_operations=[
            _op(status="COMPUTED", result=0.37, calculation_ref="")]),
            "calculation_ref必填", stage="executed")

    def test_computed_forbidden_at_mapped(self):
        self.check(_mapped_ir(metric_bindings=[_binding(), _binding(binding_id="MB-2")],
                              derived_operations=[_op(status="COMPUTED", result=0.37,
                                                      calculation_ref="公式: x")]),
                   "status非法于stage=mapped")

    def test_operand_unknown_binding(self):
        self.check(_mapped_ir(derived_operations=[_op(operands=["MB-99", "MB-1"])]),
                   "引用不存在的binding_id")

    def test_spread_needs_two_operands(self):
        self.check(_mapped_ir(derived_operations=[_op(operands=["MB-1"])]),
                   "spread须≥2")

    def test_bad_mapping_status(self):
        self.check(_mapped_ir(unresolved_entities=[
            {"mention": "x", "mapping_status": "unknown", "note": "n"}]),
                   "mapping_status枚举外值")

    def test_mutated_answer_constraints(self):
        self.check(_mapped_ir(answer_constraints={"grounding_required": False,
                                                  "no_data_policy": "report_absence"}),
                   "answer_constraints")

    def test_bad_binding_id_format(self):
        self.check(_mapped_ir(metric_bindings=[_binding(binding_id="MB1")]),
                   "binding_id格式非法")

    def test_duplicate_binding_ids(self):
        self.check(_mapped_ir(metric_bindings=[_binding(binding_id="MB-1"),
                                               _binding(binding_id="MB-1")]),
                   "binding_id重复")

    def test_bad_as_of(self):
        self.check(_mapped_ir(as_of="2026/10/30"), "as_of须为ISO")


class TestMakeQueryId(unittest.TestCase):
    def test_make_query_id(self):
        self.assertEqual(qir.make_query_id(CREATED_AT, 1), "QB-20261105-001")
        self.assertEqual(qir.make_query_id(CREATED_AT, 2), "QB-20261105-002")
        self.assertEqual(qir.make_query_id("2026-01-02T00:00:00+08:00", 12),
                         "QB-20260102-012")
        with self.assertRaises(ValueError):
            qir.make_query_id("bad-date", 1)
        with self.assertRaises(ValueError):
            qir.make_query_id(CREATED_AT, 0)


# ══ T2 黄金用例(要点②: §三(d)问题文本→IR) ═════════════════════════════

class TestGoldenMapping(unittest.TestCase):
    def test_golden_ir_full_literal(self):
        """§三(d)问题→IR 全量字面量对照(手算预期,DESIGN L138/L143-156对齐)。"""
        expected = {
            "query_id": "QB-20261105-001",
            "created_at": CREATED_AT,
            "mode": "B",
            "question_text": GOLDEN_Q,
            "as_of": None,
            "target_snapshot_id": None,
            "metric_bindings": [
                {"binding_id": "MB-1", "metric_id": "DFEDTARL", "role": "level",
                 "window": None, "field": "value", "status": "PENDING_EXECUTION",
                 "absence_reason": None, "provenance": None},
                {"binding_id": "MB-2", "metric_id": "DFEDTARU", "role": "level",
                 "window": None, "field": "value", "status": "PENDING_EXECUTION",
                 "absence_reason": None, "provenance": None},
                {"binding_id": "MB-3", "metric_id": "DFF", "role": "level",
                 "window": None, "field": "value", "status": "PENDING_EXECUTION",
                 "absence_reason": None, "provenance": None},
                {"binding_id": "MB-4", "metric_id": "UST_2Y", "role": "level",
                 "window": None, "field": "value", "status": "PENDING_EXECUTION",
                 "absence_reason": None, "provenance": None},
                {"binding_id": "MB-5", "metric_id": "UST_10Y", "role": "level",
                 "window": None, "field": "value", "status": "PENDING_EXECUTION",
                 "absence_reason": None, "provenance": None},
                {"binding_id": "MB-6", "metric_id": "CURVE_2S10S", "role": "level",
                 "window": None, "field": "value", "status": "PENDING_EXECUTION",
                 "absence_reason": None, "provenance": None},
                {"binding_id": "MB-7", "metric_id": "USDJPY", "role": "level",
                 "window": None, "field": "value", "status": "PENDING_EXECUTION",
                 "absence_reason": None, "provenance": None},
                {"binding_id": "MB-8", "metric_id": None, "role": "spread_component",
                 "window": None, "field": "value", "status": "ABSENT_REGISTRY",
                 "absence_reason": "日本政策利率不在注册表(8指标,INVENTORY G-01)",
                 "provenance": None},
                {"binding_id": "MB-9", "metric_id": None, "role": "spread_component",
                 "window": None, "field": "value", "status": "ABSENT_REGISTRY",
                 "absence_reason": "JGB 10Y不在注册表(8指标,INVENTORY G-01)",
                 "provenance": None},
                {"binding_id": "MB-10", "metric_id": "USDJPY", "role": "derived_window",
                 "window": "week", "field": "pct_change", "status": "PENDING_EXECUTION",
                 "absence_reason": None, "provenance": None},
                {"binding_id": "MB-11", "metric_id": "USDJPY", "role": "derived_window",
                 "window": "ytd", "field": "pct_change", "status": "PENDING_EXECUTION",
                 "absence_reason": None, "provenance": None},
            ],
            "derived_operations": [
                {"op_id": "OP-1", "op_type": "spread",
                 "operands": ["MB-8", "MB-1", "MB-2"],
                 "formula": "日本政策利率 − (DFEDTARL+DFEDTARU)/2(目标区间中值)",
                 "unit": "percentage_point", "status": "NO_DATA", "result": None,
                 "calculation_ref": ("公式: 日本政策利率 − (DFEDTARL+DFEDTARU)/2"
                                     "(目标区间中值);输入观测日与期限匹配由执行器"
                                     "(WP-B2)按E11纪律落定;operand缺席→NO_DATA"
                                     "不部分计算(DESIGN §三(c))")},
                {"op_id": "OP-2", "op_type": "spread", "operands": ["MB-9", "MB-5"],
                 "formula": "JGB 10Y − UST_10Y", "unit": "percentage_point",
                 "status": "NO_DATA", "result": None,
                 "calculation_ref": ("公式: JGB 10Y − UST_10Y;输入观测日与期限匹配"
                                     "由执行器(WP-B2)按E11纪律落定;operand缺席→"
                                     "NO_DATA不部分计算(DESIGN §三(c))")},
                {"op_id": "OP-3", "op_type": "spread", "operands": ["MB-5", "MB-4"],
                 "formula": "UST_10Y − UST_2Y(查询期计算,对照注册值CURVE_2S10S)",
                 "unit": "percentage_point", "status": "PENDING_EXECUTION",
                 "result": None,
                 "calculation_ref": ("公式: UST_10Y − UST_2Y(查询期计算,对照注册值"
                                     "CURVE_2S10S);输入观测日与期限匹配由执行器"
                                     "(WP-B2)按E11纪律落定")},
            ],
            "unresolved_entities": [],
            "answer_constraints": dict(AC),
        }
        self.assertEqual(golden_ir(), expected)

    def test_golden_mb8_mb9_absent_registry(self):
        """要点②点名断言: MB-8/MB-9 ABSENT_REGISTRY(DESIGN L152-153)。"""
        ir = golden_ir()
        mb = {b["binding_id"]: b for b in ir["metric_bindings"]}
        self.assertEqual(mb["MB-8"]["status"], "ABSENT_REGISTRY")
        self.assertEqual(mb["MB-8"]["metric_id"], None)
        self.assertEqual(mb["MB-8"]["role"], "spread_component")
        self.assertIn("不在注册表", mb["MB-8"]["absence_reason"])
        self.assertEqual(mb["MB-9"]["status"], "ABSENT_REGISTRY")
        self.assertEqual(mb["MB-9"]["metric_id"], None)
        self.assertIn("不在注册表", mb["MB-9"]["absence_reason"])
        self.assertEqual(ir["metric_bindings"][7]["binding_id"], "MB-8")
        self.assertEqual(ir["metric_bindings"][8]["binding_id"], "MB-9")

    def test_golden_passes_own_schema(self):
        self.assertEqual(qir.validate_ir(golden_ir(), stage="mapped"), [])

    def test_golden_deterministic(self):
        self.assertEqual(golden_ir(), golden_ir())

    def test_jp_present_fixture_resolves_identity(self):
        """缺席=发现而非硬编码(D-B1-04): 注册表补入日端身份后同问题自动转在场。"""
        reg = {"metrics": FIXTURE_METRICS + JP_METRICS,
               "by_id": {m["metric_id"]: m for m in FIXTURE_METRICS + JP_METRICS}}
        ir = eqm.map_question(GOLDEN_Q, created_at=CREATED_AT, registry=reg)
        mb = {b["binding_id"]: b for b in ir["metric_bindings"]}
        self.assertEqual(mb["MB-8"]["status"], "PENDING_EXECUTION")
        self.assertEqual(mb["MB-8"]["metric_id"], "JP_POLICY_RATE")
        self.assertIsNone(mb["MB-8"]["absence_reason"])
        self.assertEqual(mb["MB-9"]["status"], "PENDING_EXECUTION")
        self.assertEqual(mb["MB-9"]["metric_id"], "JGB_10Y")
        ops = {o["op_id"]: o for o in ir["derived_operations"]}
        self.assertEqual(ops["OP-1"]["status"], "PENDING_EXECUTION")
        self.assertEqual(ops["OP-2"]["status"], "PENDING_EXECUTION")
        self.assertEqual(ops["OP-3"]["status"], "PENDING_EXECUTION")
        # 全IR零缺席理由(10指标全注册)
        self.assertEqual([b for b in ir["metric_bindings"]
                          if b["absence_reason"] is not None], [])

    def test_us_metric_missing_fixture_absent(self):
        """US侧意图身份缺席变体: A1发现机制对称作用于US意图metric_id。"""
        metrics = [m for m in FIXTURE_METRICS if m["metric_id"] != "UST_2Y"]
        reg = {"metrics": metrics, "by_id": {m["metric_id"]: m for m in metrics}}
        ir = eqm.map_question(GOLDEN_Q, created_at=CREATED_AT, registry=reg)
        mb = {b["binding_id"]: b for b in ir["metric_bindings"]}
        self.assertEqual(mb["MB-4"]["metric_id"], None)
        self.assertEqual(mb["MB-4"]["status"], "ABSENT_REGISTRY")
        self.assertEqual(mb["MB-4"]["absence_reason"], "UST_2Y不在注册表(7指标)")
        ops = {o["op_id"]: o for o in ir["derived_operations"]}
        self.assertEqual(ops["OP-3"]["status"], "NO_DATA")   # operand MB-4缺席
        self.assertIsNone(ops["OP-3"]["result"])

    def test_query_seq_and_date_drive_query_id(self):
        ir = eqm.map_question(GOLDEN_Q, created_at="2026-12-31T09:30:00+08:00",
                              query_seq=2, registry=FIXTURE_REGISTRY)
        self.assertEqual(ir["query_id"], "QB-20261231-002")

    def test_no_double_trigger_dedupe(self):
        ir = eqm.map_question("美元兑日元和美元兑日元走势怎么样",
                              created_at=CREATED_AT, registry=FIXTURE_REGISTRY)
        ids = [(b["metric_id"], b["role"], b["window"]) for b in ir["metric_bindings"]]
        self.assertEqual(ids, [("USDJPY", "level", None),
                               ("USDJPY", "derived_window", "week"),
                               ("USDJPY", "derived_window", "ytd")])


# ══ T3 窗口/as_of/词表规则 ═════════════════════════════════════════════

class TestWindowsAndAsOf(unittest.TestCase):
    def test_field_for_window_unit_discipline(self):
        # 字面量: E3单位纪律(利率→pp,价格→pct,计数→abs;复用fe常量分类)
        self.assertEqual(eqm.field_for_window("percent"), "pp_change")
        self.assertEqual(eqm.field_for_window("percentage_point"), "pp_change")
        self.assertEqual(eqm.field_for_window("jpy_per_usd"), "pct_change")
        self.assertEqual(eqm.field_for_window("index_point"), "pct_change")
        self.assertEqual(eqm.field_for_window("persons"), "abs_change")
        self.assertEqual(eqm.field_for_window("persons_thousands"), "abs_change")
        with self.assertRaises(ValueError):
            eqm.field_for_window("lightyear")

    def test_usdjpy_without_trend_cue_no_windows(self):
        ir = eqm.map_question("美元兑日元现在多少",
                              created_at=CREATED_AT, registry=FIXTURE_REGISTRY)
        self.assertEqual(len(ir["metric_bindings"]), 1)
        self.assertEqual(ir["metric_bindings"][0]["window"], None)

    def test_as_of_from_question_text(self):
        ir = eqm.map_question("截至2026-10-30美日政策利率差怎么样",
                              created_at=CREATED_AT, registry=FIXTURE_REGISTRY)
        self.assertEqual(ir["as_of"], "2026-10-30")

    def test_as_of_invalid_date_ignored(self):
        # E4严格原语: 2026-13-40非真实日历日期→None,不猜映射
        ir = eqm.map_question("截至2026-13-40美日政策利率差怎么样",
                              created_at=CREATED_AT, registry=FIXTURE_REGISTRY)
        self.assertIsNone(ir["as_of"])

    def test_as_of_param_wins_over_text(self):
        ir = eqm.map_question("截至2026-10-30美日政策利率差怎么样",
                              created_at=CREATED_AT, as_of="2026-10-31",
                              registry=FIXTURE_REGISTRY)
        self.assertEqual(ir["as_of"], "2026-10-31")

    def test_us_policy_rate_level_rule(self):
        ir = eqm.map_question("美国政策利率现在什么水平",
                              created_at=CREATED_AT, registry=FIXTURE_REGISTRY)
        self.assertEqual([b["metric_id"] for b in ir["metric_bindings"]],
                         ["DFEDTARL", "DFEDTARU", "DFF"])
        self.assertEqual(ir["derived_operations"], [])
        self.assertEqual(ir["unresolved_entities"], [])

    def test_e4_reference(self):
        # E4行为锚(事实层原语,非本包实现): 合法返回date,非法None
        self.assertEqual(str(fe.parse_iso_date("2026-10-30")), "2026-10-30")
        self.assertIsNone(fe.parse_iso_date("2026-13-40"))
        self.assertIsNone(fe.parse_iso_date("2026-10-30T00:00:00"))


# ══ T4 unresolved_entities负向用例(要点③) ══════════════════════════════

class TestUnresolvedEntities(unittest.TestCase):
    def test_trading_question_out_of_scope(self):
        """要点③点名: 禁交易类问题→out_of_scope(DESIGN §七3)。"""
        ir = eqm.map_question("现在应该买入美元兑日元吗?能保证赚钱吗?",
                              created_at=CREATED_AT, registry=FIXTURE_REGISTRY)
        # 手算: 「应该买」(2,5)与「买入」(4,6)重叠→合并「应该买入」;
        # 「能保证」(13,16)与「赚钱」(16,18)相接→合并「能保证赚钱」(D-B1-07)
        self.assertEqual([u["mapping_status"] for u in ir["unresolved_entities"]],
                         ["out_of_scope", "out_of_scope"])
        self.assertEqual([u["mention"] for u in ir["unresolved_entities"]],
                         ["应该买入", "能保证赚钱"])
        for u in ir["unresolved_entities"]:
            self.assertIn("不构成投资建议", u["note"])

    def test_trading_question_residual_neutral_mapping(self):
        """OOS拦截不整题拒答(渲染层拦截属WP-B5): 中性指称照常映射并双双上浮。"""
        ir = eqm.map_question("现在应该买入美元兑日元吗?能保证赚钱吗?",
                              created_at=CREATED_AT, registry=FIXTURE_REGISTRY)
        self.assertEqual(len(ir["metric_bindings"]), 1)
        self.assertEqual(ir["metric_bindings"][0]["metric_id"], "USDJPY")
        self.assertEqual(qir.validate_ir(ir, stage="mapped"), [])

    def test_no_registry_identity_floated(self):
        ir = eqm.map_question("印度政策利率现在怎么样",
                              created_at=CREATED_AT, registry=FIXTURE_REGISTRY)
        self.assertEqual(ir["metric_bindings"], [])
        self.assertEqual(ir["derived_operations"], [])
        self.assertEqual(len(ir["unresolved_entities"]), 1)
        self.assertEqual(ir["unresolved_entities"][0]["mention"], "印度政策利率")
        self.assertEqual(ir["unresolved_entities"][0]["mapping_status"],
                         "no_registry_identity")

    def test_plain_greeting_empty_ir_valid(self):
        ir = eqm.map_question("你好!", created_at=CREATED_AT,
                              registry=FIXTURE_REGISTRY)
        self.assertEqual(ir["metric_bindings"], [])
        self.assertEqual(ir["derived_operations"], [])
        self.assertEqual(ir["unresolved_entities"], [])
        self.assertEqual(qir.validate_ir(ir, stage="mapped"), [])

    def test_empty_question_rejected(self):
        with self.assertRaises(ValueError):
            eqm.map_question("   ", created_at=CREATED_AT, registry=FIXTURE_REGISTRY)


# ══ T5 接线/纯度/源码边界锁 ════════════════════════════════════════════

class TestWiringAndPurity(unittest.TestCase):
    def test_default_registry_wiring_via_e1(self):
        """缺省经fe.load_registry()(E1);mock注入fixture证明零真实文件读取。"""
        with mock.patch.object(fe, "load_registry", return_value=FIXTURE_REGISTRY):
            ir = eqm.map_question(GOLDEN_Q, created_at=CREATED_AT)
        self.assertEqual(ir["query_id"], "QB-20261105-001")
        mb = {b["binding_id"]: b for b in ir["metric_bindings"]}
        # fixture计数8进入缺席理由(真实注册表为81——该差值即注入生效证据)
        self.assertIn("(8指标", mb["MB-8"]["absence_reason"])

    def test_modules_pure_stdlib_no_network(self):
        for fn in (os.path.join(ROOT, "scripts", "e2eb_query_ir.py"),
                   os.path.join(ROOT, "scripts", "e2eb_query_mapper.py")):
            with open(fn, "r", encoding="utf-8") as f:
                src = f.read()
            for banned in ("import requests", "import socket", "import urllib",
                           "import http", "import openai", "import subprocess"):
                self.assertNotIn(banned, src, f"{fn}含禁用import: {banned}")

    def test_no_raw_data_daily_reference(self):
        """AC-07①: 模块源码零原始采集档路径**引用**(字符串字面量)与零文件IO。"""
        for fn in (os.path.join(ROOT, "scripts", "e2eb_query_ir.py"),
                   os.path.join(ROOT, "scripts", "e2eb_query_mapper.py")):
            with open(fn, "r", encoding="utf-8") as f:
                src = f.read()
            self.assertNotIn("'data/daily'", src, fn)     # 路径字符串字面量
            self.assertNotIn('"data/daily"', src, fn)
            self.assertNotIn("daily_", src, fn)           # 采集档文件名前缀
            self.assertNotIn("open(", src, fn)            # 零文件IO

    def test_ir_module_reuses_no_heavy_deps(self):
        """IR模块零文件IO零项目依赖(纯schema定义;mapper才接fe)。"""
        with open(os.path.join(ROOT, "scripts", "e2eb_query_ir.py"),
                  encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("open(", src)
        self.assertNotIn("import fact_engine", src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
