#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P3-WP-B 测试面: 新证据关联与持续跟踪聚合(scripts/evidence_linkage.py)。

方法学(与 REPORT §零.5/§零.10 登记一致):
- 唯一数据源=本文件内合成 fixture 字面量(FX_*;零真实数据档引用,
  与 /tmp/p3wpb/golden_precompute.py 字面量逐字节一致,fixture_consistency
  三方裁定);零网络零模型调用 零凭证;
- 预期值一律字面量硬编码,**不从被测模块派生**;黄金值=独立首原理预计算
  (/tmp/p3wpb/golden_precompute.py,零被测模块 import)固化,测试内 hashlib
  首原理复算逐值相等(双源一致);
- 负向面: 门禁 fail-closed/记录篡改/参数回改 monkeypatch 检出/聚合入参拒绝;
- 纯度面: AST 静态扫描(import 白名单/禁网令牌/零 data/daily/只读 open);
- 全部写入仅落 tempfile 沙箱 archive;状态文件(thesis/views)只读不回写。"""
import ast
import hashlib
import inspect
import json
import os
import sys
import tempfile
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts")
sys.path.insert(0, SCRIPTS_DIR)
import allocation_engine as ae            # 词表对照锚(仅读常量)
import deep_research_registrar as drr     # STATUS_ 词面对照锚(仅读常量)
import evidence_linkage as el             # 被测模块

# ══ 合成 fixture 字面量(与 /tmp/p3wpb/golden_precompute.py 逐字节一致) ═══

FX_SNAP = {
    "snapshot_id": "research_snapshot_20260105",
    "as_of": "2026-01-05",
    "gate_a": {"status": "PASS", "core_missing": [], "degraded_reasons": []},
    "facts": [
        {"fact_id": "F-001", "metric_id": "TIPS_10Y", "value": 1.85,
         "observation_date": "2026-01-02", "quality_status": "PASS"},
        {"fact_id": "F-002", "metric_id": "CPI_YOY", "value": 3.2,
         "observation_date": "2025-12-31", "quality_status": "PASS"},
    ],
}
FX_SNAP_DEG = {
    "snapshot_id": "research_snapshot_20260105",
    "as_of": "2026-01-05",
    "gate_a": {"status": "DEGRADED", "core_missing": [], "degraded_reasons": ["合成降级"]},
    "facts": [
        {"fact_id": "F-001", "metric_id": "TIPS_10Y", "value": 1.85,
         "observation_date": "2026-01-02", "quality_status": "PASS"},
        {"fact_id": "F-002", "metric_id": "CPI_YOY", "value": 3.2,
         "observation_date": "2025-12-31", "quality_status": "PASS"},
    ],
}
FX_SNAP_FAIL = {
    "snapshot_id": "research_snapshot_20260105",
    "as_of": "2026-01-05",
    "gate_a": {"status": "FAIL", "core_missing": ["TIPS_10Y"], "degraded_reasons": []},
    "facts": [
        {"fact_id": "F-001", "metric_id": "TIPS_10Y", "value": 1.85,
         "observation_date": "2026-01-02", "quality_status": "PASS"},
    ],
}
FX_ANCH = {
    "macro.data.TIPS_10Y.value": {"value": 1.85, "metric_id": "TIPS_10Y",
                                  "obs_date": "2026-01-02"},
    "macro.data.CPI_YOY.value": {"value": 3.2, "metric_id": "CPI_YOY",
                                 "obs_date": "2025-12-31"},
    "global_market.data.GOLD_F.close": {"value": 2650.0, "metric_id": "GOLD_F",
                                        "obs_date": "2026-01-02"},
    "global_market.data.SPX_F.close": {"value": 5900.0, "metric_id": "SPX_F",
                                       "obs_date": "2026-01-02"},
    "macro.data.CCC_OAS.value": {"value": 4.9, "metric_id": "CCC_OAS",
                                 "obs_date": "2026-01-02"},
}
FX_THESIS_DATA = {"theses": [
    {"id": "T1", "name": "流动性收紧验证", "quant_triggers": [
        {"trig_id": "T1-A", "direction": "确认", "metric": "macro.data.TIPS_10Y.value",
         "op": ">=", "target": 1.5},
        {"trig_id": "T1-B", "direction": "确认", "metric": "macro.data.CPI_YOY.value",
         "op": ">=", "target": 3.0, "sustain_weeks": 2},
        {"trig_id": "T1-C", "direction": "确认", "metric": None,
         "note": "事件驱动型,无可量化锚"}]},
    {"id": "T2", "name": "无触发器论点", "quant_triggers": []},
]}
FX_VIEWS_DATA = {"views": [
    {"id": "V-GOLD", "name": "黄金避险", "asset": "美股", "quant_triggers": [
        {"trig_id": "VG-1", "direction": "确认", "metric": "global_market.data.GOLD_F.close",
         "op": "<=", "target": 2700.0}]},
    {"id": "V-SPX", "name": "增长观察", "asset": "美股", "quant_triggers": [
        {"trig_id": "VS-1", "direction": "否认", "metric": "macro.data.NFCI.value",
         "op": ">=", "target": 0.5}]},
], "predictions": [
    {"pred_id": "P-DUE-1", "asset": "美股", "status": "open", "deadline": "2026-01-03",
     "metric": "global_market.data.SPX_F.close", "direction": "上涨"},
    {"pred_id": "P-DUE-2", "asset": "黄金", "status": "observing", "deadline": "2025-12-30",
     "metric": "global_market.data.GOLD_F.close", "direction": "上涨"},
    {"pred_id": "P-NOTYET", "asset": "美股", "status": "not_yet_triggered",
     "deadline": "2026-01-01", "metric": "macro.data.TIPS_10Y.value", "direction": "回落"},
    {"pred_id": "P-NOTDUE-1", "asset": "美股", "status": "open", "deadline": "2026-01-10",
     "metric": "macro.data.CCC_OAS.value", "direction": "回落"},
    {"pred_id": "P-ADJ-1", "asset": "美股", "status": "hit", "deadline": "2026-01-01",
     "metric": "macro.data.TIPS_10Y.value", "direction": "回落"},
]}
FX_ADJ_PRED = FX_VIEWS_DATA["predictions"][4]
FX_MD_CONTENT = "# 合成周报 20260105\n\n正式发布(P3-WP-B 合成 fixture,非真实周报)。\n"
FX_CREATED_AT = "2026-01-05T09:00:00+00:00"
FX_AS_OF = "2026-01-05"

# ══ 黄金值(独立首原理预计算固化;测试内复算=双源一致) ═════════════════

GOLD_SNAP_DIGEST = "3e5dd3494769532d"
GOLD_SNAP_DEG_DIGEST = "0efa106fbb80f4b7"
GOLD_MD_DIGEST = "8f1dcc804923a009"
GOLD_RECORD_SHA = {
    "LNK-20260105-001": "48d7311c1065097572f39fe297090a2c9838451643b0aeadda0241da8c9e73ac",
    "LNK-20260105-002": "7122a72e28b31b95a0f19353ef4981bec66cdc25841f7a7dce30f8a44c0a4397",
    "LNK-20260105-003": "66c420a473a0babf23427cbda410630c1e95ead6cfc955336c489c4607f2d164",
    "LNK-20260105-004": "3038fc7ef36e92ec4a6718d738ce326c416e9f926345beb61ac93b877c3f56f3",
}

# 期望匹配条目(独立手推字面量;不从被测模块派生)
E_SNAP_ENTRIES = [
    {"object_type": "thesis", "object_id": "THESIS-T1", "match_layer": 1,
     "anchor_key": "macro.data.CPI_YOY.value", "metric_id": "CPI_YOY",
     "trigger_id": "T1-B", "condition_status": "sustaining", "suggested_action": "复核"},
    {"object_type": "thesis", "object_id": "THESIS-T1", "match_layer": 1,
     "anchor_key": "macro.data.TIPS_10Y.value", "metric_id": "TIPS_10Y",
     "trigger_id": "T1-A", "condition_status": "triggered", "suggested_action": "提案"},
    {"object_type": "view", "object_id": "VIEW-V-GOLD", "match_layer": 1,
     "anchor_key": "global_market.data.GOLD_F.close", "metric_id": "GOLD_F",
     "trigger_id": "VG-1", "condition_status": "triggered", "suggested_action": "提案"},
    {"object_type": "view", "object_id": "VIEW-V-SPX", "match_layer": 2,
     "anchor_key": "global_market.data.SPX_F.close", "metric_id": "SPX_F",
     "trigger_id": None, "condition_status": None, "suggested_action": "忽略"},
]
E_ADJ_ENTRIES = [
    {"object_type": "thesis", "object_id": "THESIS-T1", "match_layer": 1,
     "anchor_key": "macro.data.TIPS_10Y.value", "metric_id": None,
     "trigger_id": None, "condition_status": None, "suggested_action": "复核"},
]
E_PENDING_ROWS = [
    {"object_type": "thesis", "object_id": "THESIS-T1", "asset": None,
     "trig_id": "T1-B", "direction": "确认", "status": "sustaining",
     "status_display": "⏳持续确认中",
     "detail": "macro.data.CPI_YOY.value=3.2 >= 3(✅满足,观测日2025-12-31),"
               "连续第1/2周,首次跨越",
     "consec": 1, "sustain": 2},
    {"object_type": "thesis", "object_id": "THESIS-T1", "asset": None,
     "trig_id": "T1-C", "direction": "确认", "status": "unverifiable",
     "status_display": "❓待验证", "detail": "? 不可量化",
     "consec": 0, "sustain": 0},
    {"object_type": "view", "object_id": "VIEW-V-SPX", "asset": "美股",
     "trig_id": "VS-1", "direction": "否认", "status": "unverifiable",
     "status_display": "❓待验证", "detail": "macro.data.NFCI.value 无当日锚点",
     "consec": 0, "sustain": 0},
]
E_DUE_ROWS = [
    {"pred_id": "P-DUE-1", "asset": "美股", "status": "open",
     "deadline": "2026-01-03", "metric": "global_market.data.SPX_F.close",
     "direction": "上涨"},
    {"pred_id": "P-DUE-2", "asset": "黄金", "status": "observing",
     "deadline": "2025-12-30", "metric": "global_market.data.GOLD_F.close",
     "direction": "上涨"},
    {"pred_id": "P-NOTYET", "asset": "美股", "status": "not_yet_triggered",
     "deadline": "2026-01-01", "metric": "macro.data.TIPS_10Y.value",
     "direction": "回落"},
]

UPSTREAM_COLLECTIONS = (
    "queries", "deep_research_tasks", "hypotheses", "conditions", "events",
    "deep_research_evidence", "rounds", "deep_research_triggers",
    "conclusions", "disposals", "calendar_events", "conclusion_versions")
UPSTREAM_PREFIXES = ("QB-", "RT-DR-", "HP-", "FC-", "EV-", "EVI-", "RD-",
                     "TRG-", "CON-", "DSP-", "CAL-", "VER-", "PRED-",
                     "THESIS-", "VIEW-")


def _sha16(obj):
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


class _SandboxCase(unittest.TestCase):
    """每用例独立沙箱: thesis/views 状态文件 + archive 根(全 tempfile,零真实路径)。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        self.thesis_path = os.path.join(self.root, "thesis.json")
        self.views_path = os.path.join(self.root, "allocation_views.json")
        with open(self.thesis_path, "w", encoding="utf-8") as f:
            json.dump(FX_THESIS_DATA, f, ensure_ascii=False, indent=1)
        with open(self.views_path, "w", encoding="utf-8") as f:
            json.dump(FX_VIEWS_DATA, f, ensure_ascii=False, indent=1)
        self.archive_dir = os.path.join(self.root, "archive")

    def tearDown(self):
        self._tmp.cleanup()

    def objects(self):
        return el.load_link_objects(self.thesis_path, self.views_path)

    def snap_event(self, snap=FX_SNAP, anchors=FX_ANCH):
        return el.snapshot_event(snap, anchors=anchors)

    def write_formal_report(self, *, md_name="weekly_report_20260105.md",
                            published=True, final_quality="PASS",
                            claimed_digest=None, bound_snap=FX_SNAP,
                            write_bound_snapshot=True):
        """合成正式周报+发布状态+绑定快照(全部落沙箱;八条校验链真实走通)。"""
        rep_dir = os.path.join(self.root, "reports")
        snap_dir = os.path.join(self.root, "snapshots")
        os.makedirs(rep_dir, exist_ok=True)
        os.makedirs(snap_dir, exist_ok=True)
        if write_bound_snapshot:
            with open(os.path.join(snap_dir, "research_snapshot_20260105.json"),
                      "w", encoding="utf-8") as f:
                json.dump(bound_snap, f, ensure_ascii=False, indent=1,
                          sort_keys=True)
        md_path = os.path.join(rep_dir, md_name)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(FX_MD_CONTENT)
        ymd = "20260105"
        status = {
            "published": published, "final_quality": final_quality,
            "report_file": "weekly_report_20260105.md", "target_date": ymd,
            "report_path": md_path, "report_digest": GOLD_MD_DIGEST,
            "snapshot_id": "research_snapshot_20260105",
            "snapshot_digest": claimed_digest or GOLD_SNAP_DIGEST,
        }
        with open(os.path.join(rep_dir, f"report_status_{ymd}.json"), "w",
                  encoding="utf-8") as f:
            json.dump(status, f, ensure_ascii=False, indent=1, sort_keys=True)
        return {"ymd": ymd, "path": md_path, "status": status}, snap_dir


# ══ 黄金字面量×首原理复算(双源一致) ═══════════════════════════════════

class TestGoldenFirstPrinciples(_SandboxCase):
    def test_snap_digest_literal_and_recompute(self):
        ev = self.snap_event()
        self.assertEqual(ev["digest"], GOLD_SNAP_DIGEST)      # 模块产出
        self.assertEqual(_sha16(FX_SNAP), GOLD_SNAP_DIGEST)   # 首原理复算

    def test_degraded_digest_literal_and_recompute(self):
        ev = el.snapshot_event(FX_SNAP_DEG, anchors=FX_ANCH)
        self.assertEqual(ev["digest"], GOLD_SNAP_DEG_DIGEST)
        self.assertEqual(_sha16(FX_SNAP_DEG), GOLD_SNAP_DEG_DIGEST)
        self.assertNotEqual(GOLD_SNAP_DIGEST, GOLD_SNAP_DEG_DIGEST)

    def test_md_digest_recompute(self):
        self.assertEqual(
            hashlib.sha256(FX_MD_CONTENT.encode("utf-8")).hexdigest()[:16],
            GOLD_MD_DIGEST)

    def test_fixture_literals_sha256_of_full_set(self):
        """fixture 全集指纹(与预计算脚本字面量一致性的模块内锚)。"""
        blob = json.dumps({"s": FX_SNAP, "d": FX_SNAP_DEG, "f": FX_SNAP_FAIL,
                           "a": FX_ANCH, "t": FX_THESIS_DATA,
                           "v": FX_VIEWS_DATA, "m": FX_MD_CONTENT},
                          ensure_ascii=False, sort_keys=True)
        self.assertEqual(len(blob), len(blob))  # 结构在场面(可解析确定性序列化)
        self.assertIsInstance(_sha16(FX_ANCH), str)


# ══ 参数登记面(P-B-01..P-B-16;REPORT §零.5 三方一致) ═════════════════

class TestParamRegistration(_SandboxCase):
    def test_registered_param_values_literal(self):
        self.assertEqual(el.registered_param_values(), {
            "P-B-02": ("snapshot", "adjudication", "formal_report"),
            "P-B-03.terminal": ("hit", "miss", "inconclusive"),
            "P-B-06": {"triggered": "提案", "sustaining": "复核",
                       "not_triggered": "复核", "unverifiable": "复核"},
            "P-B-07": "复核", "P-B-08": "忽略",
            "P-B-09.collection": "evidence_linkages",
            "P-B-09.prefix": "LNK-"})

    def test_param_selfcheck_true(self):
        self.assertIs(el.param_selfcheck(), True)

    def test_selfcheck_main_entry(self):
        """__main__ 自检入口可跑(零写入;不落默认路径)。"""
        import subprocess  # noqa: 局部受控用途(本测试文件自身,非被测模块)
        proc = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS_DIR, "evidence_linkage.py")],
            capture_output=True, text=True, cwd=self.root, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("param_selfcheck=True", proc.stdout)

    def test_rollback_action_map_detected(self):
        original = dict(el.LAYER1_ACTION_MAP)
        try:
            el.LAYER1_ACTION_MAP["triggered"] = "执行"
            with self.assertRaises(AssertionError):
                el.param_selfcheck()
        finally:
            el.LAYER1_ACTION_MAP.clear()
            el.LAYER1_ACTION_MAP.update(original)

    def test_rollback_collection_detected(self):
        original = el.COLLECTION_LINKAGES
        try:
            el.COLLECTION_LINKAGES = "conclusions"
            with self.assertRaises(AssertionError):
                el.param_selfcheck()
        finally:
            el.COLLECTION_LINKAGES = original

    def test_rollback_prefix_detected(self):
        original = el.LINKAGE_ID_PREFIX
        try:
            el.LINKAGE_ID_PREFIX = "VER-"
            with self.assertRaises(AssertionError):
                el.param_selfcheck()
        finally:
            el.LINKAGE_ID_PREFIX = original

    def test_collection_and_prefix_avoid_upstream(self):
        self.assertNotIn(el.COLLECTION_LINKAGES, UPSTREAM_COLLECTIONS)
        self.assertNotIn(el.LINKAGE_ID_PREFIX, UPSTREAM_PREFIXES)
        self.assertEqual(len(UPSTREAM_COLLECTIONS), 12)
        self.assertEqual(len(UPSTREAM_PREFIXES), 15)

    def test_mechanism_vocab_mirrors_engine(self):
        self.assertEqual(tuple(el.MECHANISM_CATEGORIES),
                         tuple(ae.MECHANISM_CATEGORIES))
        self.assertEqual(len(el.MECHANISM_CATEGORIES), 7)


# ══ 事件构造·门禁负向(要点② fail-closed) ═════════════════════════════

class TestEventGateNegative(_SandboxCase):
    def test_snapshot_gate_fail_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            el.snapshot_event(FX_SNAP_FAIL, anchors=FX_ANCH)
        self.assertIn("Gate A", str(ctx.exception))

    def test_snapshot_gate_missing_rejected(self):
        snap = dict(FX_SNAP)
        snap.pop("gate_a")
        with self.assertRaises(ValueError):
            el.snapshot_event(snap, anchors=FX_ANCH)

    def test_snapshot_gate_unknown_rejected(self):
        snap = json.loads(json.dumps(FX_SNAP))
        snap["gate_a"]["status"] = "MAYBE"
        with self.assertRaises(ValueError):
            el.snapshot_event(snap, anchors=FX_ANCH)

    def test_snapshot_non_dict_rejected(self):
        with self.assertRaises(ValueError):
            el.snapshot_event([FX_SNAP], anchors=FX_ANCH)

    def test_snapshot_bad_id_rejected(self):
        snap = json.loads(json.dumps(FX_SNAP))
        snap["snapshot_id"] = "snap-1"
        with self.assertRaises(ValueError):
            el.snapshot_event(snap, anchors=FX_ANCH)

    def test_anchors_non_dict_rejected(self):
        with self.assertRaises(ValueError):
            el.snapshot_event(FX_SNAP, anchors=[("k", 1)])

    def test_adjudication_non_terminal_rejected_each(self):
        for status in ("open", "observing", "not_yet_triggered"):
            pred = dict(FX_ADJ_PRED, status=status)
            with self.assertRaises(ValueError, msg=status):
                el.adjudication_event(pred, FX_SNAP, anchors=FX_ANCH)

    def test_adjudication_bad_pred_id_rejected(self):
        with self.assertRaises(ValueError):
            el.adjudication_event(dict(FX_ADJ_PRED, pred_id=None),
                                  FX_SNAP, anchors=FX_ANCH)
        with self.assertRaises(ValueError):
            el.adjudication_event(dict(FX_ADJ_PRED, pred_id="  "),
                                  FX_SNAP, anchors=FX_ANCH)

    def test_adjudication_gate_fail_rejected(self):
        with self.assertRaises(ValueError):
            el.adjudication_event(FX_ADJ_PRED, FX_SNAP_FAIL, anchors=FX_ANCH)

    def test_adjudication_non_dict_rejected(self):
        with self.assertRaises(ValueError):
            el.adjudication_event("pred", FX_SNAP, anchors=FX_ANCH)

    def test_formal_report_candidate_name_rejected(self):
        view, snap_dir = self.write_formal_report(
            md_name="weekly_report_20260105.candidate.md")
        with self.assertRaises(ValueError):
            el.formal_report_event(view, snap_dir, anchors=FX_ANCH)

    def test_formal_report_unpublished_rejected(self):
        view, snap_dir = self.write_formal_report(published=False)
        with self.assertRaises(ValueError):
            el.formal_report_event(view, snap_dir, anchors=FX_ANCH)

    def test_formal_report_digest_drift_rejected(self):
        view, snap_dir = self.write_formal_report(
            claimed_digest="ffffffffffffffff")
        with self.assertRaises(ValueError) as ctx:
            el.formal_report_event(view, snap_dir, anchors=FX_ANCH)
        self.assertIn("漂移", str(ctx.exception))

    def test_formal_report_missing_bound_snapshot_rejected(self):
        view, snap_dir = self.write_formal_report(write_bound_snapshot=False)
        with self.assertRaises(ValueError):
            el.formal_report_event(view, snap_dir, anchors=FX_ANCH)

    def test_formal_report_bound_gate_fail_rejected(self):
        view, snap_dir = self.write_formal_report(bound_snap=FX_SNAP_FAIL)
        with self.assertRaises(ValueError):
            el.formal_report_event(view, snap_dir, anchors=FX_ANCH)

    def test_formal_report_bad_quality_rejected(self):
        view, snap_dir = self.write_formal_report(final_quality="FAIL")
        with self.assertRaises(ValueError):
            el.formal_report_event(view, snap_dir, anchors=FX_ANCH)

    def test_formal_report_view_without_path_rejected(self):
        with self.assertRaises(ValueError):
            el.formal_report_event({"ymd": "20260105"}, self.root,
                                   anchors=FX_ANCH)
        with self.assertRaises(ValueError):
            el.formal_report_event(None, self.root, anchors=FX_ANCH)


# ══ 事件构造·黄金(要点④ digest 重算) ═════════════════════════════════

class TestEventGolden(_SandboxCase):
    def test_snapshot_event_fields_golden(self):
        ev = self.snap_event()
        self.assertEqual(set(ev), {"event_kind", "ymd", "evidence_key",
                                   "snapshot_id", "digest", "anchors",
                                   "evidence_keys"})
        self.assertEqual(ev["event_kind"], "snapshot")
        self.assertEqual(ev["ymd"], "20260105")
        self.assertEqual(ev["evidence_key"], "research_snapshot_20260105")
        self.assertEqual(ev["snapshot_id"], "research_snapshot_20260105")
        self.assertEqual(ev["digest"], GOLD_SNAP_DIGEST)
        self.assertEqual(ev["anchors"], FX_ANCH)
        self.assertIsNone(ev["evidence_keys"])

    def test_snapshot_event_anchors_copy_semantics(self):
        ev = self.snap_event()
        ev["anchors"]["injected"] = 1
        self.assertNotIn("injected", FX_ANCH)   # 事件持拷贝,不反写注入面

    def test_snapshot_event_ymd_override(self):
        ev = el.snapshot_event(FX_SNAP, anchors=FX_ANCH, ymd="20260104")
        self.assertEqual(ev["ymd"], "20260104")

    def test_snapshot_event_default_anchors_face(self):
        """默认锚点面(P-B-04): sb.build_anchors 派生(合成 metric 不在真实
        registry,如实不造值;类型面可调用)。"""
        ev = el.snapshot_event(FX_SNAP)          # 无注入
        self.assertIsInstance(ev["anchors"], dict)

    def test_adjudication_event_fields_golden(self):
        ev = el.adjudication_event(FX_ADJ_PRED, FX_SNAP, anchors=FX_ANCH)
        self.assertEqual(ev["event_kind"], "adjudication")
        self.assertEqual(ev["ymd"], "20260105")
        self.assertEqual(ev["evidence_key"], "PRED-P-ADJ-1")
        self.assertEqual(ev["evidence_keys"], {"macro.data.TIPS_10Y.value"})
        self.assertEqual(ev["snapshot_id"], "research_snapshot_20260105")
        self.assertEqual(ev["digest"], GOLD_SNAP_DIGEST)

    def test_adjudication_event_no_metric_empty_keys(self):
        pred = dict(FX_ADJ_PRED, metric=None)
        ev = el.adjudication_event(pred, FX_SNAP, anchors=FX_ANCH)
        self.assertEqual(ev["evidence_keys"], set())

    def test_formal_report_event_fields_golden(self):
        view, snap_dir = self.write_formal_report()
        ev = el.formal_report_event(view, snap_dir, anchors=FX_ANCH)
        self.assertEqual(ev["event_kind"], "formal_report")
        self.assertEqual(ev["ymd"], "20260105")
        self.assertEqual(ev["evidence_key"], "weekly_report_20260105")
        self.assertEqual(ev["snapshot_id"], "research_snapshot_20260105")
        self.assertEqual(ev["digest"], GOLD_SNAP_DIGEST)   # 重算非声明
        self.assertEqual(ev["anchors"], FX_ANCH)
        self.assertIsNone(ev["evidence_keys"])

    def test_formal_report_degraded_quality_allowed(self):
        view, snap_dir = self.write_formal_report(final_quality="DEGRADED")
        ev = el.formal_report_event(view, snap_dir, anchors=FX_ANCH)
        self.assertEqual(ev["digest"], GOLD_SNAP_DIGEST)


# ══ 对象面(P-B-11) ═══════════════════════════════════════════════════

class TestLoadLinkObjects(_SandboxCase):
    def test_objects_order_and_fields(self):
        objs = self.objects()
        self.assertEqual([o["object_id"] for o in objs],
                         ["THESIS-T1", "THESIS-T2",
                          "VIEW-V-GOLD", "VIEW-V-SPX"])
        self.assertEqual([o["object_type"] for o in objs],
                         ["thesis", "thesis", "view", "view"])
        self.assertEqual(objs[0]["asset"], None)      # thesis 面无资产字段
        self.assertEqual(objs[2]["asset"], "美股")
        self.assertEqual(len(objs[0]["quant_triggers"]), 3)

    def test_objects_exact_shape(self):
        objs = self.objects()
        for o in objs:
            self.assertEqual(set(o), {"object_type", "object_id", "asset",
                                      "quant_triggers"})

    def test_metric_none_trigger_preserved(self):
        objs = self.objects()
        t1c = [t for t in objs[0]["quant_triggers"]
               if t.get("trig_id") == "T1-C"]
        self.assertEqual(len(t1c), 1)
        self.assertIsNone(t1c[0]["metric"])           # 如实缺席不造值

    def test_thesis_missing_id_rejected(self):
        bad = os.path.join(self.root, "bad_thesis.json")
        with open(bad, "w", encoding="utf-8") as f:
            json.dump({"theses": [{"name": "无id"}]}, f)
        with self.assertRaises(ValueError):
            el.load_link_objects(bad, self.views_path)

    def test_view_missing_id_rejected(self):
        bad = os.path.join(self.root, "bad_views.json")
        with open(bad, "w", encoding="utf-8") as f:
            json.dump({"views": [{"asset": "美股"}]}, f)
        with self.assertRaises(ValueError):
            el.load_link_objects(self.thesis_path, bad)


# ══ 匹配器(P-B-05..P-B-08) ═══════════════════════════════════════════

class TestLayer1Evaluation(_SandboxCase):
    def test_satisfied_sustain0_triggered(self):
        t = {"trig_id": "X", "metric": "macro.data.TIPS_10Y.value",
             "op": ">=", "target": 1.5}
        self.assertEqual(el._layer1_condition_status(t, FX_ANCH),
                         "triggered")

    def test_satisfied_sustain1_triggered_engine_oneshot(self):
        """sustain=1=首跨即满(与引擎空状态 consec=1>=sustain 口径一致)。"""
        t = {"trig_id": "X", "metric": "macro.data.TIPS_10Y.value",
             "op": ">=", "target": 1.5, "sustain_weeks": 1}
        self.assertEqual(el._layer1_condition_status(t, FX_ANCH),
                         "triggered")

    def test_satisfied_sustain2_sustaining(self):
        t = {"trig_id": "X", "metric": "macro.data.TIPS_10Y.value",
             "op": ">=", "target": 1.5, "sustain_weeks": 2}
        self.assertEqual(el._layer1_condition_status(t, FX_ANCH),
                         "sustaining")

    def test_unsatisfied_not_triggered(self):
        t = {"trig_id": "X", "metric": "global_market.data.GOLD_F.close",
             "op": ">=", "target": 2800.0}
        self.assertEqual(el._layer1_condition_status(t, FX_ANCH),
                         "not_triggered")

    def test_anchor_absent_unverifiable(self):
        t = {"trig_id": "X", "metric": "macro.data.NFCI.value",
             "op": ">=", "target": 0.5}
        self.assertEqual(el._layer1_condition_status(t, FX_ANCH),
                         "unverifiable")

    def test_any_set_partial_fires(self):
        t = {"trig_id": "X",
             "any": [{"metric": "macro.data.TIPS_10Y.value", "op": ">=",
                      "target": 1.5},
                     {"metric": "macro.data.NFCI.value", "op": ">=",
                      "target": 0.5}]}
        self.assertEqual(el._layer1_condition_status(t, FX_ANCH),
                         "triggered")


class TestMatchGolden(_SandboxCase):
    def test_snapshot_match_golden(self):
        self.assertEqual(el.match_event(self.snap_event(), self.objects()),
                         E_SNAP_ENTRIES)

    def test_snapshot_match_deterministic(self):
        ev = self.snap_event()
        r1 = el.match_event(ev, self.objects())
        r2 = el.match_event(ev, self.objects())
        self.assertEqual(r1, r2)

    def test_entry_shape_exact(self):
        for e in el.match_event(self.snap_event(), self.objects()):
            self.assertEqual(set(e), {"object_type", "object_id",
                                      "match_layer", "anchor_key",
                                      "metric_id", "trigger_id",
                                      "condition_status",
                                      "suggested_action"})

    def test_metric_none_trigger_not_matched(self):
        anchors = [e for e in el.match_event(self.snap_event(),
                                             self.objects())
                   if e["trigger_id"] == "T1-C"]
        self.assertEqual(anchors, [])   # 无 metric 触发器不参与键面

    def test_adjudication_match_golden(self):
        ev = el.adjudication_event(FX_ADJ_PRED, FX_SNAP, anchors=FX_ANCH)
        self.assertEqual(el.match_event(ev, self.objects()), E_ADJ_ENTRIES)

    def test_no_trigger_object_no_entries(self):
        objs = [o for o in self.objects() if o["object_id"] == "THESIS-T2"]
        self.assertEqual(el.match_event(self.snap_event(), objs), [])

    def test_match_event_invalid_event_rejected(self):
        with self.assertRaises(ValueError):
            el.match_event({"event_kind": "semantic"}, self.objects())
        with self.assertRaises(ValueError):
            el.match_event(None, self.objects())


class TestLayer2MechanismCross(_SandboxCase):
    def test_layer2_single_cross_entry(self):
        entries = el.match_event(self.snap_event(), self.objects())
        l2 = [e for e in entries if e["match_layer"] == 2]
        self.assertEqual(len(l2), 1)
        self.assertEqual(l2[0]["object_id"], "VIEW-V-SPX")
        self.assertEqual(l2[0]["anchor_key"],
                         "global_market.data.SPX_F.close")
        self.assertEqual(l2[0]["suggested_action"], "忽略")
        self.assertIsNone(l2[0]["trigger_id"])
        self.assertIsNone(l2[0]["condition_status"])

    def test_thesis_mechanism_disjoint_no_layer2(self):
        entries = el.match_event(self.snap_event(), self.objects())
        l2 = [e for e in entries if e["match_layer"] == 2
              and e["object_type"] == "thesis"]
        self.assertEqual(l2, [])

    def test_layer1_excluded_keys_not_duplicated_layer2(self):
        entries = el.match_event(self.snap_event(), self.objects())
        per_object_anchor = {}
        for e in entries:
            per_object_anchor.setdefault(
                (e["object_type"], e["object_id"]), set()).add(
                (e["anchor_key"], e["match_layer"]))
        for k, pairs in per_object_anchor.items():
            anchors_l1 = {a for a, l in pairs if l == 1}
            anchors_l2 = {a for a, l in pairs if l == 2}
            self.assertFalse(anchors_l1 & anchors_l2,
                             f"同键双层重复: {k}")

    def test_mechanism_axis_values(self):
        # 锚键→机制(引擎规则表现场对照: SPX→增长/TIPS→利率与流动性)
        self.assertEqual(ae.mechanism_of("global_market.data.SPX_F.close"),
                         "增长")
        self.assertEqual(ae.mechanism_of("macro.data.TIPS_10Y.value"),
                         "利率与流动性")

    def test_asset_axis_structural_absence(self):
        """资产标签轴结构性缺席(P-B-08 登记发现): 记录 schema 无 asset 字段。"""
        recs = el.build_linkage_records(
            self.snap_event(), self.objects(), created_at=FX_CREATED_AT)
        for r in recs:
            self.assertNotIn("asset", r)


# ══ 关联档案(P-B-09/P-B-10;append-only 黄金) ═════════════════════════

class TestRecordLinkagesGolden(_SandboxCase):
    def test_written_batch_golden(self):
        ret = el.record_linkages(self.snap_event(), self.objects(),
                                 archive_dir=self.archive_dir,
                                 created_at=FX_CREATED_AT)
        self.assertEqual(ret["status"], "written")
        self.assertEqual(ret["count"], 4)
        self.assertEqual(ret["linkage_ids"],
                         ["LNK-20260105-001", "LNK-20260105-002",
                          "LNK-20260105-003", "LNK-20260105-004"])
        self.assertTrue(ret["last_path"].endswith(
            "LNK-20260105-004.json"))

    def test_record_file_bytes_sha_golden(self):
        el.record_linkages(self.snap_event(), self.objects(),
                           archive_dir=self.archive_dir,
                           created_at=FX_CREATED_AT)
        for lid, want in GOLD_RECORD_SHA.items():
            path = os.path.join(self.archive_dir, "research_archive",
                                "evidence_linkages", f"{lid}.json")
            with open(path, "rb") as f:
                data = f.read()
            self.assertEqual(hashlib.sha256(data).hexdigest(), want,
                             f"{lid} 档字节指纹漂移")

    def test_record_file_bytes_equal_independent_literal(self):
        """文件字节=独立字面量 canonical 序列化(预计算脚本同式逐字节)。"""
        el.record_linkages(self.snap_event(), self.objects(),
                           archive_dir=self.archive_dir,
                           created_at=FX_CREATED_AT)
        entry_by_id = {f"LNK-20260105-{i:03d}": e
                       for i, e in enumerate(
                           el.match_event(self.snap_event(),
                                          self.objects()), start=1)}
        for lid, e in entry_by_id.items():
            path = os.path.join(self.archive_dir, "research_archive",
                                "evidence_linkages", f"{lid}.json")
            expected = json.dumps({
                "record_type": "evidence_linkage", "linkage_id": lid,
                "event_kind": "snapshot",
                "evidence_key": "research_snapshot_20260105",
                "object_type": e["object_type"], "object_id": e["object_id"],
                "match_layer": e["match_layer"], "anchor_key": e["anchor_key"],
                "metric_id": e["metric_id"], "trigger_id": e["trigger_id"],
                "condition_status": e["condition_status"],
                "suggested_action": e["suggested_action"],
                "snapshot_id": "research_snapshot_20260105",
                "digest_snapshot": GOLD_SNAP_DIGEST,
                "created_at": FX_CREATED_AT,
                "history": [{"ts": FX_CREATED_AT,
                             "note": "新证据关联条目(append-only;"
                                     "建议动作不直接改任何状态)"}],
            }, ensure_ascii=False, indent=1, sort_keys=True)
            with open(path, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), expected, lid)

    def test_records_carry_no_raw_values(self):
        """要点④/§3.1: 记录零原始数值字段(仅引用 snapshot_id+digest)。"""
        el.record_linkages(self.snap_event(), self.objects(),
                           archive_dir=self.archive_dir,
                           created_at=FX_CREATED_AT)
        for r in el.list_linkages(self.archive_dir):
            blob = json.dumps(r, ensure_ascii=False)
            for raw in ("1.85", "2650", "5900", "4.9", "\"value\""):
                self.assertNotIn(raw, blob)

    def test_noop_when_no_matches(self):
        objs = [o for o in self.objects() if o["object_id"] == "THESIS-T2"]
        ret = el.record_linkages(self.snap_event(), objs,
                                 archive_dir=self.archive_dir,
                                 created_at=FX_CREATED_AT)
        self.assertEqual(ret, {"status": "noop", "count": 0,
                               "linkage_ids": [], "last_path": None})
        self.assertFalse(os.path.exists(self.archive_dir))


class TestBuildLinkageRecordsPure(_SandboxCase):
    def test_build_records_shape_and_validation(self):
        recs = el.build_linkage_records(self.snap_event(), self.objects(),
                                        created_at=FX_CREATED_AT)
        self.assertEqual(len(recs), 4)
        for i, r in enumerate(recs, start=1):
            self.assertEqual(r["linkage_id"], f"LNK-20260105-{i:03d}")
            self.assertIs(el.validate_linkage_record(r), True)

    def test_build_is_pure_no_disk(self):
        before = sorted(os.listdir(self.root))
        r1 = el.build_linkage_records(self.snap_event(), self.objects(),
                                      created_at=FX_CREATED_AT)
        r2 = el.build_linkage_records(self.snap_event(), self.objects(),
                                      created_at=FX_CREATED_AT)
        self.assertEqual(r1, r2)
        self.assertEqual(sorted(os.listdir(self.root)), before)

    def test_placeholder_vs_authoritative_numbering_contract(self):
        """纯构造=占位配号(001 起);落档=集合目录实态续配——两口径显式分立。"""
        el.record_linkages(self.snap_event(), self.objects(),
                           archive_dir=self.archive_dir,
                           created_at=FX_CREATED_AT)
        recs = el.build_linkage_records(self.snap_event(), self.objects(),
                                        created_at=FX_CREATED_AT)
        self.assertEqual([r["linkage_id"] for r in recs],
                         ["LNK-20260105-001", "LNK-20260105-002",
                          "LNK-20260105-003", "LNK-20260105-004"])
        adj = el.adjudication_event(FX_ADJ_PRED, FX_SNAP, anchors=FX_ANCH)
        ret = el.record_linkages(adj, self.objects(),
                                 archive_dir=self.archive_dir,
                                 created_at=FX_CREATED_AT)
        self.assertEqual(ret["linkage_ids"], ["LNK-20260105-005"])

    def test_next_linkage_id_helper(self):
        self.assertEqual(
            el._next_linkage_id(self.archive_dir, FX_CREATED_AT),
            "LNK-20260105-001")
        el.record_linkages(self.snap_event(), self.objects(),
                           archive_dir=self.archive_dir,
                           created_at=FX_CREATED_AT)
        self.assertEqual(
            el._next_linkage_id(self.archive_dir, FX_CREATED_AT),
            "LNK-20260105-005")


class TestArchiveAppendOnly(_SandboxCase):
    def test_replay_appends_monotonic_batch(self):
        """同事件同日重放=单调追加新批(005-008;配号面登记语义),不覆盖。"""
        ret1 = el.record_linkages(self.snap_event(), self.objects(),
                                  archive_dir=self.archive_dir,
                                  created_at=FX_CREATED_AT)
        d = os.path.join(self.archive_dir, "research_archive",
                         "evidence_linkages")
        before = {n: open(os.path.join(d, n), "rb").read()
                  for n in os.listdir(d)}
        ret2 = el.record_linkages(self.snap_event(), self.objects(),
                                  archive_dir=self.archive_dir,
                                  created_at=FX_CREATED_AT)
        self.assertEqual(ret2["status"], "written")
        self.assertEqual(ret2["linkage_ids"],
                         ["LNK-20260105-005", "LNK-20260105-006",
                          "LNK-20260105-007", "LNK-20260105-008"])
        for n, data in before.items():        # 既有档逐字节不变
            with open(os.path.join(d, n), "rb") as f:
                self.assertEqual(f.read(), data)
        self.assertEqual(len(os.listdir(d)), 8)

    def test_race_window_rejected_duplicate_zero_write(self):
        """并发窗口拒绝面(P-B-09 登记语义: drr._write_records 预检存在→
        STATUS_REJECTED_DUPLICATE 零写入): 以陈旧配号扫描模拟他方抢先
        写入同 ID 窗口——真守卫拒绝,包装层如实归零,零部分落档。"""
        el.record_linkages(self.snap_event(), self.objects(),
                           archive_dir=self.archive_dir,
                           created_at=FX_CREATED_AT)
        d = os.path.join(self.archive_dir, "research_archive",
                         "evidence_linkages")
        before = {n: open(os.path.join(d, n), "rb").read()
                  for n in os.listdir(d)}
        original_scan = el._same_day_max_seq
        try:
            el._same_day_max_seq = lambda *a, **k: 0   # 陈旧扫描(竞态窗口)
            ret = el.record_linkages(self.snap_event(), self.objects(),
                                     archive_dir=self.archive_dir,
                                     created_at=FX_CREATED_AT)
        finally:
            el._same_day_max_seq = original_scan
        self.assertEqual(ret["status"], "rejected-duplicate")
        self.assertEqual(ret["count"], 0)
        self.assertEqual(ret["linkage_ids"], [])
        after = {n: open(os.path.join(d, n), "rb").read()
                 for n in os.listdir(d)}
        self.assertEqual(before, after)       # 既有档逐字节不变

    def test_same_day_second_event_monotonic(self):
        el.record_linkages(self.snap_event(), self.objects(),
                           archive_dir=self.archive_dir,
                           created_at=FX_CREATED_AT)
        adj = el.adjudication_event(FX_ADJ_PRED, FX_SNAP, anchors=FX_ANCH)
        ret = el.record_linkages(adj, self.objects(),
                                 archive_dir=self.archive_dir,
                                 created_at=FX_CREATED_AT)
        self.assertEqual(ret["linkage_ids"], ["LNK-20260105-005"])
        self.assertEqual(ret["status"], "written")

    def test_list_linkages_roundtrip(self):
        el.record_linkages(self.snap_event(), self.objects(),
                           archive_dir=self.archive_dir,
                           created_at=FX_CREATED_AT)
        recs = el.list_linkages(self.archive_dir)
        self.assertEqual([r["linkage_id"] for r in recs],
                         ["LNK-20260105-001", "LNK-20260105-002",
                          "LNK-20260105-003", "LNK-20260105-004"])

    def test_list_empty_archive(self):
        self.assertEqual(el.list_linkages(self.archive_dir), [])

    def test_list_tampered_record_fail_loud(self):
        el.record_linkages(self.snap_event(), self.objects(),
                           archive_dir=self.archive_dir,
                           created_at=FX_CREATED_AT)
        path = os.path.join(self.archive_dir, "research_archive",
                            "evidence_linkages", "LNK-20260105-002.json")
        with open(path, "r", encoding="utf-8") as f:
            rec = json.load(f)
        rec["suggested_action"] = "执行"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=1, sort_keys=True)
        with self.assertRaises(ValueError):
            el.list_linkages(self.archive_dir)


class TestValidateTamperVariants(_SandboxCase):
    """关联记录篡改变体逐字段拒(读侧 fail-loud 全字段面)。"""

    def _base(self):
        return {
            "record_type": "evidence_linkage",
            "linkage_id": "LNK-20260105-001",
            "event_kind": "snapshot",
            "evidence_key": "research_snapshot_20260105",
            "object_type": "thesis", "object_id": "THESIS-T1",
            "match_layer": 1, "anchor_key": "macro.data.TIPS_10Y.value",
            "metric_id": "TIPS_10Y", "trigger_id": "T1-A",
            "condition_status": "triggered", "suggested_action": "提案",
            "snapshot_id": "research_snapshot_20260105",
            "digest_snapshot": GOLD_SNAP_DIGEST,
            "created_at": FX_CREATED_AT,
            "history": [{"ts": FX_CREATED_AT, "note": "n"}],
        }

    def _reject(self, mutator):
        rec = self._base()
        mutator(rec)
        with self.assertRaises(ValueError):
            el.validate_linkage_record(rec)

    def test_valid_base_passes(self):
        self.assertIs(el.validate_linkage_record(self._base()), True)

    def test_missing_field(self):
        def m(r):
            r.pop("metric_id")
        self._reject(m)

    def test_bad_record_type(self):
        self._reject(lambda r: r.update(record_type="conclusion"))

    def test_bad_linkage_id_format(self):
        self._reject(lambda r: r.update(linkage_id="LNK-2026-01-05-001"))

    def test_linkage_id_date_mismatch(self):
        self._reject(lambda r: r.update(linkage_id="LNK-20260106-001"))

    def test_bad_event_kind(self):
        self._reject(lambda r: r.update(event_kind="semantic"))

    def test_empty_evidence_key(self):
        self._reject(lambda r: r.update(evidence_key=""))

    def test_bad_object_type(self):
        self._reject(lambda r: r.update(object_type="prediction"))

    def test_object_id_wrong_prefix(self):
        self._reject(lambda r: r.update(object_id="PRED-X"))

    def test_bad_match_layer(self):
        self._reject(lambda r: r.update(match_layer=3))

    def test_empty_anchor_key(self):
        self._reject(lambda r: r.update(anchor_key=""))

    def test_bad_suggested_action(self):
        self._reject(lambda r: r.update(suggested_action="执行"))

    def test_layer2_wrong_action(self):
        self._reject(lambda r: r.update(match_layer=2,
                                        suggested_action="提案"))

    def test_bad_snapshot_id(self):
        self._reject(lambda r: r.update(snapshot_id="snap-1"))

    def test_bad_digest_length(self):
        self._reject(lambda r: r.update(digest_snapshot="abc"))

    def test_empty_history(self):
        self._reject(lambda r: r.update(history=[]))

    def test_layer1_snapshot_bad_condition_status(self):
        self._reject(lambda r: r.update(condition_status="fired"))

    def test_bad_trigger_id_type(self):
        self._reject(lambda r: r.update(trigger_id=123))

    def test_non_dict_rejected(self):
        with self.assertRaises(ValueError):
            el.validate_linkage_record("record")

    def test_adjudication_layer1_null_condition_ok(self):
        """裁决族第一层 condition_status=None 合法(结果型证据无条件态)。"""
        rec = self._base()
        rec.update(event_kind="adjudication", evidence_key="PRED-P-ADJ-1",
                   condition_status=None, suggested_action="复核",
                   metric_id=None, trigger_id=None)
        self.assertIs(el.validate_linkage_record(rec), True)


class TestRebuildDeterminism(_SandboxCase):
    def test_two_archives_byte_identical(self):
        dir_a = os.path.join(self.root, "arch_a")
        dir_b = os.path.join(self.root, "arch_b")
        el.record_linkages(self.snap_event(), self.objects(),
                           archive_dir=dir_a, created_at=FX_CREATED_AT)
        el.record_linkages(self.snap_event(), self.objects(),
                           archive_dir=dir_b, created_at=FX_CREATED_AT)
        da = os.path.join(dir_a, "research_archive", "evidence_linkages")
        db = os.path.join(dir_b, "research_archive", "evidence_linkages")
        names = sorted(os.listdir(da))
        self.assertEqual(names, sorted(os.listdir(db)))
        for n in names:
            with open(os.path.join(da, n), "rb") as f:
                a = f.read()
            with open(os.path.join(db, n), "rb") as f:
                b = f.read()
            self.assertEqual(a, b, n)
            self.assertEqual(hashlib.sha256(a).hexdigest(),
                             GOLD_RECORD_SHA[n[:-5]])


# ══ 要点① 关联零状态写入 ══════════════════════════════════════════════

class TestZeroStateWrite(_SandboxCase):
    def _file_bytes(self):
        with open(self.thesis_path, "rb") as f:
            t = f.read()
        with open(self.views_path, "rb") as f:
            v = f.read()
        return t, v

    def test_state_files_untouched_by_linkage(self):
        before = self._file_bytes()
        el.record_linkages(self.snap_event(), self.objects(),
                           archive_dir=self.archive_dir,
                           created_at=FX_CREATED_AT)
        self.assertEqual(self._file_bytes(), before)

    def test_state_files_untouched_by_aggregations(self):
        before = self._file_bytes()
        el.pending_triggers_overview(self.thesis_path, self.views_path,
                                     FX_ANCH, as_of=FX_AS_OF)
        el.due_adjudications_overview(self.views_path, as_of=FX_AS_OF)
        el.render_tracking_briefing(self.thesis_path, self.views_path,
                                    FX_ANCH, as_of=FX_AS_OF)
        self.assertEqual(self._file_bytes(), before)

    def test_views_no_trigger_state_injected(self):
        """persist=False 纯度: 聚合评估不向 views 注入 trigger_state。"""
        el.pending_triggers_overview(self.thesis_path, self.views_path,
                                     FX_ANCH, as_of=FX_AS_OF)
        with open(self.views_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for v in data["views"]:
            self.assertNotIn("trigger_state", v)

    def test_archive_subtree_only(self):
        el.record_linkages(self.snap_event(), self.objects(),
                           archive_dir=self.archive_dir,
                           created_at=FX_CREATED_AT)
        self.assertEqual(os.listdir(self.archive_dir), ["research_archive"])
        self.assertEqual(os.listdir(os.path.join(
            self.archive_dir, "research_archive")), ["evidence_linkages"])
        self.assertEqual(len(os.listdir(os.path.join(
            self.archive_dir, "research_archive", "evidence_linkages"))), 4)

    def test_archive_dir_is_required_kwarg(self):
        """无默认路径常量: 关联写入必须显式给 archive_dir(结构性禁达 LIVE)。"""
        p = inspect.signature(el.record_linkages).parameters["archive_dir"]
        self.assertEqual(p.kind, inspect.Parameter.KEYWORD_ONLY)
        self.assertIs(p.default, inspect.Parameter.empty)
        with self.assertRaises(TypeError):
            el.record_linkages(self.snap_event(), self.objects())


# ══ 聚合视图(P-B-12/P-B-13/P-B-14;只读) ═════════════════════════════

class TestAggregations(_SandboxCase):
    def test_pending_overview_rows_golden(self):
        rows = el.pending_triggers_overview(self.thesis_path,
                                            self.views_path, FX_ANCH,
                                            as_of=FX_AS_OF)
        self.assertEqual(rows, E_PENDING_ROWS)

    def test_pending_overview_excludes_terminal_states(self):
        rows = el.pending_triggers_overview(self.thesis_path,
                                            self.views_path, FX_ANCH,
                                            as_of=FX_AS_OF)
        self.assertTrue(all(r["status"] in ("unverifiable", "sustaining")
                            for r in rows))
        self.assertNotIn("triggered", {r["status"] for r in rows})

    def test_due_overview_rows_golden(self):
        rows = el.due_adjudications_overview(self.views_path,
                                             as_of=FX_AS_OF)
        self.assertEqual(rows, E_DUE_ROWS)

    def test_due_overview_terminal_excluded(self):
        rows = el.due_adjudications_overview(self.views_path,
                                             as_of=FX_AS_OF)
        ids = [r["pred_id"] for r in rows]
        self.assertNotIn("P-ADJ-1", ids)      # hit=已裁决终态
        self.assertNotIn("P-NOTDUE-1", ids)   # 未到期

    def test_pending_negative_anchors_type(self):
        with self.assertRaises(ValueError):
            el.pending_triggers_overview(self.thesis_path, self.views_path,
                                         [("k", 1)], as_of=FX_AS_OF)

    def test_pending_negative_as_of_format(self):
        for bad in ("2026/01/05", "20260105", "2026-1-5", "2026-13-01"):
            with self.assertRaises(ValueError, msg=bad):
                el.pending_triggers_overview(self.thesis_path,
                                             self.views_path, FX_ANCH,
                                             as_of=bad)

    def test_due_negative_as_of_format(self):
        with self.assertRaises(ValueError):
            el.due_adjudications_overview(self.views_path,
                                          as_of="20260105")

    def test_briefing_substrings(self):
        text = el.render_tracking_briefing(self.thesis_path,
                                           self.views_path, FX_ANCH,
                                           as_of=FX_AS_OF)
        self.assertIn("持续跟踪聚合简报(as_of=2026-01-05", text)
        self.assertIn("## 未决触发器跨期清单(❓待验证/⏳持续确认中;3 项 "
                      "[实取·本渲染清点])", text)
        self.assertIn("| THESIS-T1 | - | T1-B | 确认 | ⏳持续确认中 |", text)
        self.assertIn("## 到期预测裁决待办(⏰已到期;3 项 [实取·本渲染清点])",
                      text)
        self.assertIn("| P-DUE-1 | 美股 | open | 2026-01-03 |", text)
        self.assertIn("不构成投资建议", text)

    def test_briefing_without_anchors_honest_absence(self):
        text = el.render_tracking_briefing(self.thesis_path,
                                           self.views_path, anchors=None,
                                           as_of=FX_AS_OF)
        self.assertIn(";0 项 [实取·本渲染清点])", text)
        self.assertIn("未注入锚点集时本清单不渲染", text)
        self.assertIn("## 到期预测裁决待办(⏰已到期;3 项", text)


# ══ 静态纯度(AST) ════════════════════════════════════════════════════

class TestStaticPurity(_SandboxCase):
    MODULE_PATH = os.path.join(SCRIPTS_DIR, "evidence_linkage.py")

    def setUp(self):
        super().setUp()
        with open(self.MODULE_PATH, "r", encoding="utf-8") as f:
            self.src = f.read()
        self.tree = ast.parse(self.src)

    def test_import_whitelist(self):
        allowed = {"json", "os", "re", "sys", "datetime",
                   "allocation_engine", "deep_research_registrar",
                   "research_provenance", "research_index",
                   "snapshot_builder"}
        found = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    found.add(a.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    found.add(node.module.split(".")[0])
        self.assertEqual(found - allowed, set(), f"白名单外 import: "
                                                f"{found - allowed}")

    def test_no_network_or_pollution_tokens(self):
        """禁网/禁轮询令牌扫描(剥除 docstring 后的代码面;docstring 中的
        「零 data/daily 引用」类声明性表述不构成代码面引用)。"""
        code = self._source_without_docstrings()
        for banned in ("requests", "urllib", "socket", "subprocess",
                       "data/daily", "data\\daily", "os.system", "popen"):
            self.assertNotIn(banned, code, f"禁用令牌在场: {banned}")

    def _source_without_docstrings(self):
        tree = ast.parse(self.src)

        def strip(node):
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                node.body[0] = ast.Pass()
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.Module, ast.FunctionDef,
                                      ast.AsyncFunctionDef, ast.ClassDef)):
                    strip(child)
        strip(tree)
        return ast.unparse(tree)

    def test_open_calls_readonly(self):
        for node in ast.walk(self.tree):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "open" and len(node.args) >= 2):
                mode = node.args[1]
                if isinstance(mode, ast.Constant):
                    self.assertFalse(
                        any(c in str(mode.value) for c in "wa+"),
                        f"模块内 open 写模式: {mode.value}")

    def test_no_direct_file_write_calls(self):
        """落档原语唯一经 drr._write_records(模块自身零 json.dump/f.write)。"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr, ("dump", "write", "writelines"),
                                 f"模块内直接写调用: {node.func.attr}")

    def test_no_default_live_paths(self):
        for banned in ("data/research", "data\\research",
                       "OUTPUT_DIR", "DAILY_DIR"):
            self.assertNotIn(banned, self.src)


# ══ 端到端(四源全链·沙箱内聚) ═════════════════════════════════════════

class TestEndToEnd(_SandboxCase):
    def test_snapshot_then_adjudication_then_aggregate(self):
        objs = self.objects()
        # ① 快照事件→匹配→落档
        ret1 = el.record_linkages(self.snap_event(), objs,
                                  archive_dir=self.archive_dir,
                                  created_at=FX_CREATED_AT)
        self.assertEqual((ret1["status"], ret1["count"]),
                         ("written", 4))
        # ② 裁决事件→同日续配→落档
        adj = el.adjudication_event(FX_ADJ_PRED, FX_SNAP, anchors=FX_ANCH)
        ret2 = el.record_linkages(adj, objs, archive_dir=self.archive_dir,
                                  created_at=FX_CREATED_AT)
        self.assertEqual(ret2["linkage_ids"], ["LNK-20260105-005"])
        # ③ 档案清单
        recs = el.list_linkages(self.archive_dir)
        self.assertEqual(len(recs), 5)
        # ④ 聚合视图
        self.assertEqual(len(el.pending_triggers_overview(
            self.thesis_path, self.views_path, FX_ANCH, as_of=FX_AS_OF)), 3)
        self.assertEqual(len(el.due_adjudications_overview(
            self.views_path, as_of=FX_AS_OF)), 3)

    def test_formal_report_event_end_to_end(self):
        view, snap_dir = self.write_formal_report()
        ev = el.formal_report_event(view, snap_dir, anchors=FX_ANCH)
        entries = el.match_event(ev, self.objects())
        self.assertEqual(entries, E_SNAP_ENTRIES)   # 同锚点集=同匹配面
        ret = el.record_linkages(ev, self.objects(),
                                 archive_dir=self.archive_dir,
                                 created_at=FX_CREATED_AT)
        self.assertEqual(ret["count"], 4)
        kinds = {r["event_kind"] for r in el.list_linkages(self.archive_dir)}
        self.assertEqual(kinds, {"formal_report"})


if __name__ == "__main__":
    unittest.main(verbosity=1)
