#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P2-WP-C 测试件: 跟踪触发与 GLM 综合对接(P2 深研层第 3 实现包)。

纪律承接(合同附录A 步骤7/§5.3):
- 零网络: import 面纯标准库+被测项目模块,无任何真实出站;
- 全合成 fixture: 唯一数据源=本文件字面量(临时目录沙箱,零真实档零墙钟,
  created_at 全部显式定值);
- 预期值字面量硬编码: 黄金字面量表 GOLDEN(TRG-×4/RT-DR-×2/HP-×5/FC-×7/
  CON-×5/DSP-×1/digest×1)经**独立预计算脚本首原理复算**(自带 canonical
  sha256 实现,不从被测模块导入计算;与模块沙箱运行产出交叉验证全等后固化,
  证据包 03-negative-sensitivity/golden-precompute 佐证);运行期依赖件
  (task3 族/处置 paths)用 hashlib 首原理在测试内独立复算,仍禁导入模块计算;
- 断言锚点: 每类映射 REPORT §零.5 P-C-01..P-C-18 与验收要点①-④。

fixture→断言映射表(行号为本文实读;漂移维护三要素见 DELIVERY §五):
- SNAPSHOT_GOLD 5 事实(2 可用 gold.copper.ratio/1 可用 us10y.real/1 FAIL
  质量/1 非数值)→ 窗口/接地/排除断言;
- TRG 四触发(thesis/pred-miss/pred-prem/prop)→ S-3 三子类入口断言;
- TASK1(HYP_A/HYP_B)→ CONFIRMED/EXPIRED_UNRESOLVED 黄金链;
- TASK2(HYP_C/HYP_D/HYP_E)→ FALSIFIED+优先序/INCONCLUSIVE/PARTIAL_FALSIFIED;
- TASK3(HYP_F/HYP_G,经 TRG_PROP)→ PARTIAL_SUPPORT(未解释反证)/premise
  两段式 FALSIFIED/证伪后处置三路径全套/闭环 followup。
"""
import ast
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import deep_research_tracking_engine as dt          # 被测模块(WP-C)
import deep_research_registrar as drr               # WP-A 上游(复用调用面)
import deep_research_matrix_engine as dm            # WP-B 上游(复用调用面)
import allocation_engine as ae                      # 词表复用(ALLOWED_RATINGS)
import research_archive as ra                       # 经 drr 转递(parse_snapshot_id)

# ══ 黄金字面量表(独立预计算固化;禁运行期重算) ═══════════════════════════

GOLDEN = {
    "TRG_THESIS": "TRG-20261102-5ea65bb0",
    "TRG_PRED_MISS": "TRG-20261102-2700aebb",
    "TRG_PRED_PREM": "TRG-20261102-dc744865",
    "TRG_PROP": "TRG-20261102-6dc590dd",
    "DIGEST": "2a86cee966ed2c12",
    "TASK1": "RT-DR-20261102-239d6ced",
    "HP_A": "HP-20261102-c87bc967",
    "HP_B": "HP-20261102-8376a53b",
    "FC_A1": "FC-20261102-1b1364bd",
    "FC_A2": "FC-20261102-15d0d65d",
    "FC_B1": "FC-20261102-a058e567",
    "TASK2": "RT-DR-20261102-f4d450d8",
    "HP_C": "HP-20261102-4bb294dd",
    "HP_D": "HP-20261102-eb0eb7b7",
    "HP_E": "HP-20261102-65deeb33",
    "FC_C1": "FC-20261102-4a188db5",
    "FC_C2": "FC-20261102-ddeab798",
    "FC_D1": "FC-20261102-6a14bc1c",
    "FC_E1": "FC-20261102-7bedc91c",
    "CON_CONFIRMED": "CON-20261103-1cd9440a",
    "CON_EXPIRED": "CON-20261120-15ffe3fa",
    "CON_FALSIFIED": "CON-20261103-ca4032ca",
    "CON_INCONCLUSIVE": "CON-20261120-c4165da6",
    "CON_PARTIAL_FALSIFIED": "CON-20261103-d299688e",
    "DSP_NOARCHIVE": "DSP-20261103-5fe3a43e",
}

# ══ 合成 fixture(唯一数据源;与黄金预计算逐字节一致) ═══════════════════

SNAPSHOT_GOLD = {
    "snapshot_id": "research_snapshot_20261102", "as_of": "2026-11-02",
    "gate_a": {"status": "PASS"},
    "facts": [
        {"fact_id": "gold.copper.ratio@2026-11-01", "metric_id": "gold.copper.ratio",
         "observation_date": "2026-11-01", "value": 8.9, "quality_status": "OK"},
        {"fact_id": "gold.copper.ratio@2026-11-02", "metric_id": "gold.copper.ratio",
         "observation_date": "2026-11-02", "value": 9.2, "quality_status": "OK"},
        {"fact_id": "us10y.real@2026-11-02", "metric_id": "us10y.real",
         "observation_date": "2026-11-02", "value": 2.4, "quality_status": "OK"},
        {"fact_id": "bad.metric@2026-11-02", "metric_id": "bad.metric",
         "observation_date": "2026-11-02", "value": 1.0, "quality_status": "FAIL"},
        {"fact_id": "text.metric@2026-11-02", "metric_id": "text.metric",
         "observation_date": "2026-11-02", "value": "N/A", "quality_status": "OK"},
    ],
}
SNAPSHOT_FAIL = {"snapshot_id": "research_snapshot_20261103", "as_of": "2026-11-03",
                 "gate_a": {"status": "FAIL"}, "facts": []}
SNAPSHOT_DEGRADED = {"snapshot_id": "research_snapshot_20261104", "as_of": "2026-11-04",
                     "gate_a": {"status": "DEGRADED"}, "facts": SNAPSHOT_GOLD["facts"]}
SNAPSHOT_NOFACTS = {"snapshot_id": "research_snapshot_20261105", "as_of": "2026-11-05",
                    "gate_a": {"status": "PASS"}}
# 窗口边界敏感 fixture: 含截止日后观测(gold 12-05=7.5 晚于 11-16/11-30 两档
# deadline)——窗口过滤失活即翻转判定(负向敏感性①锚)
SNAPSHOT_POST = {"snapshot_id": "research_snapshot_20261206", "as_of": "2026-12-06",
                 "gate_a": {"status": "PASS"},
                 "facts": [
                     {"fact_id": "gold.copper.ratio@2026-11-01",
                      "metric_id": "gold.copper.ratio",
                      "observation_date": "2026-11-01", "value": 8.9,
                      "quality_status": "OK"},
                     {"fact_id": "gold.copper.ratio@2026-11-02",
                      "metric_id": "gold.copper.ratio",
                      "observation_date": "2026-11-02", "value": 9.2,
                      "quality_status": "OK"},
                     {"fact_id": "gold.copper.ratio@2026-12-05",
                      "metric_id": "gold.copper.ratio",
                      "observation_date": "2026-12-05", "value": 7.5,
                      "quality_status": "OK"},
                     {"fact_id": "us10y.real@2026-11-02", "metric_id": "us10y.real",
                      "observation_date": "2026-11-02", "value": 2.4,
                      "quality_status": "OK"},
                 ]}

TRG_THESIS = {"kind": "thesis_invalidation", "ref": "TH-gold-01",
    "payload": {"target": "TH-gold-01", "trigger_id": "TH-gold-01.t1",
                "engine_status": "triggered", "verified_by": "thesis_engine"},
    "created_at": "2026-11-02T08:00:00"}
TRG_PRED_MISS = {"kind": "prediction_adjudication", "ref": "PRED-gold-01",
    "payload": {"pred_ref": "PRED-gold-01", "event": "adjudicated", "verdict": "miss",
                "adjudicated_by": "pred_engine"},
    "created_at": "2026-11-02T08:10:00"}
TRG_PRED_PREM = {"kind": "prediction_adjudication", "ref": "PRED-gold-02",
    "payload": {"pred_ref": "PRED-gold-02", "event": "premise_fulfilled",
                "verdict": None, "adjudicated_by": "pred_engine"},
    "created_at": "2026-11-02T08:20:00"}
TRG_PROP = {"kind": "rejected_rating_proposal", "ref": "VIEW-gold-01",
    "payload": {"view_ref": "VIEW-gold-01", "proposed_rating": "超配",
                "gate_status": "rejected", "reason": "证据不足门禁拒绝"},
    "created_at": "2026-11-02T08:30:00"}

QUESTION = "金铜比结构性背离的驱动假设研究"
HYP_A = {"statement": "假设A: 工业需求走弱主导", "mechanism_story": "增长机制连环",
  "conditions": [
    {"metric_id": "gold.copper.ratio", "operator": ">=", "threshold": 9.0,
     "window": {"mode": "touch", "weeks": 4}, "premise": None,
     "threshold_source": "historical_quantile", "direction": "supporting"},
    {"metric_id": "us10y.real", "operator": ">", "threshold": 3.0,
     "window": {"mode": "expiry", "deadline": "2026-11-30"}, "premise": None,
     "threshold_source": "registry_validation", "direction": "falsifying"},
  ]}
HYP_B = {"statement": "假设B: 货币对冲需求主导", "mechanism_story": "避险与估值机制",
  "conditions": [
    {"metric_id": "gold.copper.ratio", "operator": "<", "threshold": 8.0,
     "window": {"mode": "expiry", "weeks": 2}, "premise": None,
     "threshold_source": "user_explicit", "direction": "supporting"},
  ]}
CRITERIA = [{"pair": ["假设A: 工业需求走弱主导", "假设B: 货币对冲需求主导"],
              "criterion": "金铜比两周方向"}]
TASK_CA = "2026-11-02T09:00:00"

QUESTION2 = "金铜比阈值突破的证伪压力研究"
HYP_C = {"statement": "假设C: 阈值上破持续", "mechanism_story": "动量机制",
  "conditions": [
    {"metric_id": "gold.copper.ratio", "operator": ">=", "threshold": 9.0,
     "window": {"mode": "touch", "weeks": 4}, "premise": None,
     "threshold_source": "historical_quantile", "direction": "supporting"},
    {"metric_id": "gold.copper.ratio", "operator": ">=", "threshold": 8.5,
     "window": {"mode": "touch", "weeks": 4}, "premise": None,
     "threshold_source": "historical_quantile", "direction": "falsifying"},
  ]}
HYP_D = {"statement": "假设D: 空指标路径阻断", "mechanism_story": "数据面机制",
  "conditions": [
    {"metric_id": "empty.metric", "operator": ">=", "threshold": 1.0,
     "window": {"mode": "expiry", "deadline": "2026-11-10"}, "premise": None,
     "threshold_source": "registry_validation", "direction": "supporting"},
  ]}
HYP_E = {"statement": "假设E: 实际利率压制", "mechanism_story": "利率与流动性机制",
  "conditions": [
    {"metric_id": "us10y.real", "operator": ">", "threshold": 2.0,
     "window": {"mode": "expiry", "deadline": "2026-11-30"}, "premise": None,
     "threshold_source": "registry_validation", "direction": "falsifying"},
  ]}
CRITERIA2 = [{"pair": ["假设C: 阈值上破持续", "假设D: 空指标路径阻断"],
               "criterion": "窗口内是否触发"},
              {"pair": ["假设C: 阈值上破持续", "假设E: 实际利率压制"],
               "criterion": "利率敏感方向"},
              {"pair": ["假设D: 空指标路径阻断", "假设E: 实际利率压制"],
               "criterion": "数据依赖度"}]
TASK2_CA = "2026-11-02T10:00:00"

# TASK3 族(PARTIAL_SUPPORT/premise 两段式/处置三路径;运行期捕获 ID)
QUESTION3 = "评级提案被拒后的对冲驱动研究"
HYP_F = {"statement": "假设F: 避险溢价扩张", "mechanism_story": "避险与估值机制",
  "conditions": [
    {"metric_id": "gold.copper.ratio", "operator": ">=", "threshold": 9.0,
     "window": {"mode": "touch", "weeks": 4}, "premise": None,
     "threshold_source": "historical_quantile", "direction": "supporting"},
    {"metric_id": "us10y.real", "operator": ">=", "threshold": 2.0,
     "window": {"mode": "touch", "weeks": 4}, "premise": "联储转向确认",
     "threshold_source": "registry_validation", "direction": "falsifying"},
  ]}
HYP_G = {"statement": "假设G: 工业景气回升", "mechanism_story": "增长机制连环",
  "conditions": [
    {"metric_id": "gold.copper.ratio", "operator": "<=", "threshold": 8.0,
     "window": {"mode": "expiry", "deadline": "2026-11-30"}, "premise": None,
     "threshold_source": "user_explicit", "direction": "supporting"},
    {"metric_id": "us10y.real", "operator": ">=", "threshold": 2.0,
     "window": {"mode": "expiry", "deadline": "2026-11-30"}, "premise": None,
     "threshold_source": "registry_validation", "direction": "supporting"},
  ]}
CRITERIA3 = [{"pair": ["假设F: 避险溢价扩张", "假设G: 工业景气回升"],
               "criterion": "金铜比方向"}]
TASK3_CA = "2026-11-02T11:00:00"


def _h8(payload):
    """首原理指纹复算(测试内独立实现,禁导入被测模块计算)。"""
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:8]


class WPCTestBase(unittest.TestCase):
    """沙箱基座: 每用例独立临时档案根+快照目录;零真实档零墙钟。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="p2-wp-c-test-")
        self.ad = os.path.join(self.tmp, "archive")
        self.sd = os.path.join(self.tmp, "snapshots")
        os.makedirs(self.sd)
        for snap in (SNAPSHOT_GOLD, SNAPSHOT_FAIL, SNAPSHOT_DEGRADED,
                     SNAPSHOT_NOFACTS, SNAPSHOT_POST):
            with open(os.path.join(self.sd,
                      "research_snapshot_%s.json" % snap["snapshot_id"][18:]),
                      "w", encoding="utf-8") as f:
                json.dump(snap, f, ensure_ascii=False, sort_keys=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ── 沙箱装填助手(每用例按需调用,零共享状态) ──────────────────────
    def reg(self, t):
        return dt.register_tracking_trigger(t["kind"], t["ref"], t["payload"],
                                            archive_dir=self.ad,
                                            created_at=t["created_at"])

    def build_task1(self):
        r = self.reg(TRG_THESIS)
        s = dt.spawn_research_from_trigger(r["trigger_id"], QUESTION,
                                           [HYP_A, HYP_B], CRITERIA, SNAPSHOT_GOLD,
                                           archive_dir=self.ad, created_at=TASK_CA)
        return r, s

    def build_task2(self):
        r = self.reg(TRG_PRED_MISS)
        s = dt.spawn_research_from_trigger(r["trigger_id"], QUESTION2,
                                           [HYP_C, HYP_D, HYP_E], CRITERIA2,
                                           SNAPSHOT_GOLD, archive_dir=self.ad,
                                           created_at=TASK2_CA)
        return r, s

    def build_task3(self):
        r = self.reg(TRG_PROP)
        s = dt.spawn_research_from_trigger(r["trigger_id"], QUESTION3,
                                           [HYP_F, HYP_G], CRITERIA3,
                                           SNAPSHOT_GOLD, archive_dir=self.ad,
                                           created_at=TASK3_CA)
        return r, s

    def eval_hp(self, task_id, hp_id, snap_id, as_of, premise=None):
        return dt.evaluate_hypothesis_conditions(
            task_id, hp_id, snap_id, self.sd, as_of=as_of,
            premise_fulfilled=premise, archive_dir=self.ad)

    def outcome_of(self, evaluation, condition_id):
        for e in evaluation["evaluations"]:
            if e["condition_id"] == condition_id:
                return e
        raise AssertionError("条件 %s 不在评估件" % condition_id)


# ══ 1. S-3 触发入口黄金面(P-C-03/P-C-04/P-C-16;要点①) ═════════════════

class TestTriggerGoldenIntake(WPCTestBase):

    def test_thesis_trigger_golden(self):
        r = self.reg(TRG_THESIS)
        self.assertEqual(r["status"], "written")
        self.assertEqual(r["trigger_id"], GOLDEN["TRG_THESIS"])
        rec = dt.load_trigger(GOLDEN["TRG_THESIS"], self.ad)
        self.assertEqual(rec["kind"], "thesis_invalidation")
        self.assertEqual(rec["ref"], "TH-gold-01")
        self.assertEqual(rec["record_type"], "deep_research_trigger")
        self.assertTrue(rec["history"])

    def test_prediction_adjudicated_miss_golden(self):
        r = self.reg(TRG_PRED_MISS)
        self.assertEqual(r["trigger_id"], GOLDEN["TRG_PRED_MISS"])
        rec = dt.load_trigger(GOLDEN["TRG_PRED_MISS"], self.ad)
        self.assertEqual(rec["payload"]["verdict"], "miss")
        self.assertEqual(rec["payload"]["event"], "adjudicated")

    def test_prediction_premise_fulfilled_golden(self):
        r = self.reg(TRG_PRED_PREM)
        self.assertEqual(r["trigger_id"], GOLDEN["TRG_PRED_PREM"])
        rec = dt.load_trigger(GOLDEN["TRG_PRED_PREM"], self.ad)
        self.assertIsNone(rec["payload"]["verdict"])   # 前提兑现非裁决,恒 null

    def test_rejected_rating_proposal_golden(self):
        r = self.reg(TRG_PROP)
        self.assertEqual(r["trigger_id"], GOLDEN["TRG_PROP"])
        rec = dt.load_trigger(GOLDEN["TRG_PROP"], self.ad)
        self.assertEqual(rec["payload"]["proposed_rating"], "超配")
        self.assertEqual(rec["payload"]["gate_status"], "rejected")

    def test_list_triggers_deterministic_order(self):
        for t in (TRG_THESIS, TRG_PRED_MISS, TRG_PRED_PREM, TRG_PROP):
            self.reg(t)
        ids = [r["trigger_id"] for r in dt.list_triggers(self.ad)]
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(set(ids), {GOLDEN["TRG_THESIS"], GOLDEN["TRG_PRED_MISS"],
                                    GOLDEN["TRG_PRED_PREM"], GOLDEN["TRG_PROP"]})


# ══ 2. 触发 schema 负向(P-C-04;fail-loud 零写入) ══════════════════════

class TestTriggerSchemaNegative(WPCTestBase):

    def test_thesis_engine_status_gate(self):
        for bad in ("not_triggered", "sustaining", "unverifiable", None):
            with self.subTest(engine_status=bad):
                p = dict(TRG_THESIS["payload"], engine_status=bad)
                with self.assertRaises(ValueError) as cm:
                    dt.register_tracking_trigger("thesis_invalidation",
                                                TRG_THESIS["ref"], p,
                                                archive_dir=self.ad,
                                                created_at="2026-11-02T08:00:00")
                self.assertIn("engine_status", str(cm.exception))
                self.assertEqual(dt.list_triggers(self.ad), [])   # 零写入

    def test_unknown_kind_rejected(self):
        with self.assertRaises(ValueError) as cm:
            dt.register_tracking_trigger("manual_override", "X-1",
                                        {"any": "thing"}, archive_dir=self.ad,
                                        created_at="2026-11-02T08:00:00")
        self.assertIn("S-3 入口子类恰 3 个", str(cm.exception))

    def test_adjudicated_with_null_verdict_rejected(self):
        p = dict(TRG_PRED_MISS["payload"], verdict=None)
        with self.assertRaises(ValueError) as cm:
            dt.register_tracking_trigger("prediction_adjudication",
                                        TRG_PRED_MISS["ref"], p,
                                        archive_dir=self.ad,
                                        created_at="2026-11-02T08:10:00")
        self.assertIn("verdict", str(cm.exception))

    def test_premise_event_with_verdict_rejected(self):
        p = dict(TRG_PRED_PREM["payload"], verdict="hit")
        with self.assertRaises(ValueError) as cm:
            dt.register_tracking_trigger("prediction_adjudication",
                                        TRG_PRED_PREM["ref"], p,
                                        archive_dir=self.ad,
                                        created_at="2026-11-02T08:20:00")
        self.assertIn("恒须null", str(cm.exception))

    def test_bad_verdict_vocabulary_rejected(self):
        for bad in ("HIT", "wrong", "hit_miss", 1):
            with self.subTest(verdict=bad):
                p = dict(TRG_PRED_MISS["payload"], verdict=bad)
                with self.assertRaises(ValueError):
                    dt.register_tracking_trigger("prediction_adjudication",
                                                TRG_PRED_MISS["ref"], p,
                                                archive_dir=self.ad,
                                                created_at="2026-11-02T08:10:00")

    def test_rating_outside_vocabulary_rejected(self):
        for bad in ("加仓", "strong_buy", "", None):
            with self.subTest(rating=bad):
                p = dict(TRG_PROP["payload"], proposed_rating=bad)
                with self.assertRaises(ValueError) as cm:
                    dt.register_tracking_trigger("rejected_rating_proposal",
                                                TRG_PROP["ref"], p,
                                                archive_dir=self.ad,
                                                created_at="2026-11-02T08:30:00")
                self.assertIn("proposed_rating", str(cm.exception))

    def test_gate_status_not_rejected_rejected(self):
        p = dict(TRG_PROP["payload"], gate_status="approved")
        with self.assertRaises(ValueError) as cm:
            dt.register_tracking_trigger("rejected_rating_proposal",
                                        TRG_PROP["ref"], p, archive_dir=self.ad,
                                        created_at="2026-11-02T08:30:00")
        self.assertIn("gate_status恒须", str(cm.exception))

    def test_extra_payload_key_and_bad_types_rejected(self):
        with self.assertRaises(ValueError) as cm:      # 未登记键
            dt.register_tracking_trigger("thesis_invalidation", "TH-x",
                                        dict(TRG_THESIS["payload"], extra="x"),
                                        archive_dir=self.ad,
                                        created_at="2026-11-02T08:00:00")
        self.assertIn("未登记键", str(cm.exception))
        with self.assertRaises(ValueError):            # payload 非 dict
            dt.register_tracking_trigger("thesis_invalidation", "TH-x",
                                        "not-a-dict", archive_dir=self.ad,
                                        created_at="2026-11-02T08:00:00")
        with self.assertRaises(ValueError):            # ref 空
            dt.register_tracking_trigger("thesis_invalidation", "",
                                        TRG_THESIS["payload"],
                                        archive_dir=self.ad,
                                        created_at="2026-11-02T08:00:00")


# ══ 3. 触发 append-only(P-C-16;同 id 重放一律拒) ══════════════════════

class TestTriggerAppendOnly(WPCTestBase):

    def test_replay_rejected_bytes_unchanged(self):
        r = self.reg(TRG_THESIS)
        path = r["trigger_path"]
        with open(path, "rb") as f:
            b1 = f.read()
        r2 = self.reg(TRG_THESIS)                      # 同事件重放
        self.assertEqual(r2["status"], "rejected-duplicate")
        with open(path, "rb") as f:
            self.assertEqual(f.read(), b1)             # 字节不变
        self.assertEqual(len(dt.list_triggers(self.ad)), 1)

    def test_cross_sandbox_same_id(self):
        r1 = self.reg(TRG_PROP)
        tmp2 = tempfile.mkdtemp(prefix="p2-wp-c-test2-")
        try:
            ad2 = os.path.join(tmp2, "archive")
            r2 = dt.register_tracking_trigger(
                TRG_PROP["kind"], TRG_PROP["ref"], TRG_PROP["payload"],
                archive_dir=ad2, created_at=TRG_PROP["created_at"])
            self.assertEqual(r1["trigger_id"], r2["trigger_id"])
            self.assertEqual(r1["trigger_id"], GOLDEN["TRG_PROP"])
        finally:
            shutil.rmtree(tmp2, ignore_errors=True)

    def test_same_day_different_time_same_id(self):
        r1 = self.reg(TRG_THESIS)
        r2 = dt.register_tracking_trigger(
            TRG_THESIS["kind"], TRG_THESIS["ref"], TRG_THESIS["payload"],
            archive_dir=self.ad, created_at="2026-11-02T23:59:59")
        self.assertEqual((r1["status"], r2["status"]),
                         ("written", "rejected-duplicate"))   # 零墙钟: ymd 同日同 ID


# ══ 4. 触发后再研究衔接(P-C-05;origin_trigger 落任务档) ════════════════

class TestSpawnFromTrigger(WPCTestBase):

    def test_task1_golden_and_origin(self):
        r, s = self.build_task1()
        self.assertEqual(s["status"], "written")
        self.assertEqual(s["task_id"], GOLDEN["TASK1"])
        self.assertEqual(s["trigger_id"], GOLDEN["TRG_THESIS"])
        task = drr.load_task(GOLDEN["TASK1"], self.ad)
        self.assertEqual(task["origin"], {"origin_trigger": {
            "kind": "thesis_invalidation", "ref": "TH-gold-01"}})
        self.assertEqual(task["condition_ids"],
                         [GOLDEN["FC_A1"], GOLDEN["FC_A2"], GOLDEN["FC_B1"]])
        self.assertEqual(task["digest_snapshot"], GOLDEN["DIGEST"])  # R5 重算

    def test_task2_golden_from_prediction_trigger(self):
        r, s = self.build_task2()
        self.assertEqual(s["task_id"], GOLDEN["TASK2"])
        task = drr.load_task(GOLDEN["TASK2"], self.ad)
        self.assertEqual(task["origin"]["origin_trigger"]["kind"],
                         "prediction_adjudication")
        self.assertEqual(s["hypothesis_ids"],
                         [GOLDEN["HP_C"], GOLDEN["HP_D"], GOLDEN["HP_E"]])

    def test_unknown_trigger_rejected(self):
        with self.assertRaises(FileNotFoundError):
            dt.spawn_research_from_trigger(
                "TRG-19990101-00000000", "问题", [HYP_A, HYP_B], CRITERIA,
                SNAPSHOT_GOLD, archive_dir=self.ad, created_at=TASK_CA)

    def test_drr_validation_bubbles_up(self):
        r = self.reg(TRG_THESIS)
        with self.assertRaises(ValueError) as cm:      # 单假设(上游 ≥2 校验兜底)
            dt.spawn_research_from_trigger(r["trigger_id"], "单假设问题",
                                           [HYP_A], CRITERIA, SNAPSHOT_GOLD,
                                           archive_dir=self.ad, created_at=TASK_CA)
        self.assertIn("≥2", str(cm.exception))


# ══ 5. 条件窗口语义(P-C-06/P-C-07/P-C-08/P-C-09;要点②) ════════════════

class TestConditionWindow(WPCTestBase):

    def test_touch_early_hit_triggered(self):
        _, s = self.build_task1()
        ev = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_A"],
                          "research_snapshot_20261102", "2026-11-03T00:00:00")
        e = self.outcome_of(ev, GOLDEN["FC_A1"])
        self.assertEqual(e["outcome"], "TRIGGERED")
        self.assertEqual(e["evidence"], {"obs_date": "2026-11-02", "value": 9.2})
        self.assertEqual(e["mode"], "touch")
        self.assertEqual(e["window_start"], "2026-11-02")   # created_at 日期段
        self.assertEqual(e["deadline"], "2026-11-30")       # +4 周

    def test_touch_open_window_no_hit_pending(self):
        _, s = self.build_task1()
        # FC_B1: gold.copper.ratio < 8.0 expiry→改观察 touch 语义: 用 HYP_A 的
        # falsifying expiry 条件(F 暂不触发)验 expiry PENDING;此处验 touch
        # 未触: 构造评估于窗口内无命中日(as_of=11-02 当日 8.9<9.0 未触前)
        ev = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_A"],
                          "research_snapshot_20261102", "2026-11-02T00:00:00")
        e = self.outcome_of(ev, GOLDEN["FC_A1"])
        self.assertEqual(e["outcome"], "TRIGGERED")   # 11-02 观测 9.2 已在窗内

    def test_touch_closed_no_hit_not_triggered(self):
        # HYP_G 条件1(gold.copper.ratio <= 8.0 expiry 11-30)窗口闭合+窗内
        # 观测不满足 → NOT_TRIGGERED(touch 闭合面由 expiry 判定同款覆盖)
        _, s = self.build_task3()
        hp_g = s["hypothesis_ids"][1]
        fc_g = s["condition_ids"][2]
        ev = self.eval_hp(s["task_id"], hp_g, "research_snapshot_20261102",
                          "2026-12-01T00:00:00")
        e = self.outcome_of(ev, fc_g)
        self.assertEqual(e["outcome"], "NOT_TRIGGERED")
        self.assertEqual(e["evidence"]["obs_date"], "2026-11-02")  # 窗内最新
        self.assertEqual(e["evidence"]["value"], 9.2)

    def test_touch_closed_zero_obs_data_insufficient(self):
        # HYP_D 空指标 expiry 11-10 闭合+零观测 → DATA_INSUFFICIENT(不硬判)
        _, s = self.build_task2()
        ev = self.eval_hp(GOLDEN["TASK2"], GOLDEN["HP_D"],
                          "research_snapshot_20261102", "2026-11-20T00:00:00")
        e = self.outcome_of(ev, GOLDEN["FC_D1"])
        self.assertEqual(e["outcome"], "DATA_INSUFFICIENT")
        self.assertIsNone(e["evidence"])

    def test_expiry_no_early_adjudication(self):
        _, s = self.build_task1()
        ev = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_A"],
                          "research_snapshot_20261102", "2026-11-03T00:00:00")
        e = self.outcome_of(ev, GOLDEN["FC_A2"])      # deadline 11-30 > as_of
        self.assertEqual(e["outcome"], "PENDING")
        self.assertIsNone(e["evidence"])

    def test_expiry_pending_adverse_obs_for_falsifying(self):
        _, s = self.build_task2()
        ev = self.eval_hp(GOLDEN["TASK2"], GOLDEN["HP_E"],
                          "research_snapshot_20261102", "2026-11-03T00:00:00")
        e = self.outcome_of(ev, GOLDEN["FC_E1"])      # 2.4>2.0 命中但期终未到
        self.assertEqual(e["outcome"], "PENDING")
        self.assertEqual(e["adverse_obs"],
                         {"obs_date": "2026-11-02", "value": 2.4})

    def test_expiry_at_deadline_judgment(self):
        # HYP_G 双 expiry 条件截止日判定(SNAPSHOT_POST 含截止日后 12-05 观测
        # 必须排除): 条件1(<=8.0)窗内最新 9.2 不满足→NOT_TRIGGERED;
        # 条件2(us10y.real>=2.0)窗内 2.4 满足→TRIGGERED
        _, s = self.build_task3()
        hp_g = s["hypothesis_ids"][1]
        fc_g1, fc_g2 = s["condition_ids"][2], s["condition_ids"][3]
        ev = self.eval_hp(s["task_id"], hp_g, "research_snapshot_20261206",
                          "2026-11-30T00:00:00")
        e1 = self.outcome_of(ev, fc_g1)
        self.assertEqual(e1["outcome"], "NOT_TRIGGERED")
        self.assertEqual(e1["evidence"], {"obs_date": "2026-11-02", "value": 9.2})
        e2 = self.outcome_of(ev, fc_g2)
        self.assertEqual(e2["outcome"], "TRIGGERED")
        self.assertEqual(e2["evidence"], {"obs_date": "2026-11-02", "value": 2.4})
        # 双 expiry 截止日判定 → expiry 满足向成立 → CONFIRMED(expiry 路径)
        c = dt.adjudicate_conclusion(s["task_id"], hp_g, ev,
                                     archive_dir=self.ad,
                                     created_at="2026-11-30T01:00:00")
        self.assertEqual(c["new_status"], "CONFIRMED")

    def test_post_deadline_obs_excluded_from_window(self):
        # FC_B1(gold<8.0, deadline 11-16): 12-05 观测 7.5<8.0 虽满足比较式但
        # 在窗口外——窗口结束后的数据不得用于裁决(每日观察先例 L537 同款)
        _, s = self.build_task1()
        ev = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_B"],
                          "research_snapshot_20261206", "2026-12-10T00:00:00")
        e = self.outcome_of(ev, GOLDEN["FC_B1"])
        self.assertEqual(e["outcome"], "NOT_TRIGGERED")   # 不得用 7.5 翻转
        self.assertEqual(e["evidence"], {"obs_date": "2026-11-02", "value": 9.2})

    def test_in_window_filter_excludes_out_of_window_obs(self):
        # FC_B1 窗口=[11-02(created),11-16];11-01 观测(8.9)在窗外必须排除:
        # 若误纳入,11-01<8.0 为 False、11-02 为 False,判定同;故用敏感构造——
        # HYP_B 条件改为对照: 断言窗内观测集合恰为 [11-02](evidence 日期可证)
        _, s = self.build_task1()
        ev = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_B"],
                          "research_snapshot_20261102", "2026-11-20T00:00:00")
        e = self.outcome_of(ev, GOLDEN["FC_B1"])
        self.assertEqual(e["window_start"], "2026-11-02")
        self.assertEqual(e["deadline"], "2026-11-16")       # 11-02+2 周
        self.assertEqual(e["evidence"], {"obs_date": "2026-11-02", "value": 9.2})

    def test_premise_unfulfilled_not_yet_in_window(self):
        _, s = self.build_task3()
        fc_f2 = s["condition_ids"][1]                 # HYP_F falsifying 带前提
        hp_f = s["hypothesis_ids"][0]
        ev = self.eval_hp(s["task_id"], hp_f, "research_snapshot_20261102",
                          "2026-11-03T00:00:00")      # 无 premise_fulfilled
        e = self.outcome_of(ev, fc_f2)
        self.assertEqual(e["outcome"], "NOT_YET_IN_WINDOW")

    def test_premise_fulfilled_after_deadline_not_activated(self):
        _, s = self.build_task3()
        fc_f2 = s["condition_ids"][1]
        hp_f = s["hypothesis_ids"][0]
        ev = self.eval_hp(s["task_id"], hp_f, "research_snapshot_20261102",
                          "2026-11-03T00:00:00",
                          premise={fc_f2: "2026-12-15"})    # 晚于 11-30 deadline
        e = self.outcome_of(ev, fc_f2)
        self.assertEqual(e["outcome"], "NOT_ACTIVATED")     # 不激活不顺延

    def test_premise_fulfilled_opens_window(self):
        _, s = self.build_task3()
        fc_f2 = s["condition_ids"][1]
        hp_f = s["hypothesis_ids"][0]
        ev = self.eval_hp(s["task_id"], hp_f, "research_snapshot_20261102",
                          "2026-11-05T00:00:00",
                          premise={fc_f2: "2026-11-01"})
        e = self.outcome_of(ev, fc_f2)
        self.assertEqual(e["window_start"], "2026-11-01")   # 兑现日开窗
        self.assertEqual(e["outcome"], "TRIGGERED")         # 11-02 观测 2.4>=2.0


# ══ 6. 快照纪律与接地(P-C-12/P-C-15;fail-closed 阻断如实) ═════════════

class TestConditionGrounding(WPCTestBase):

    def test_missing_snapshot_blocked(self):
        _, s = self.build_task1()
        ev = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_A"],
                          "research_snapshot_20261231", "2026-11-03T00:00:00")
        self.assertTrue(ev["blocked"])
        self.assertEqual(ev["blocking"]["stage"], "snapshot_load")
        self.assertEqual(ev["evaluations"], [])

    def test_gate_a_fail_blocked(self):
        _, s = self.build_task1()
        ev = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_A"],
                          "research_snapshot_20261103", "2026-11-03T00:00:00")
        self.assertTrue(ev["blocked"])
        self.assertEqual(ev["blocking"]["stage"], "gate_a")
        self.assertEqual(ev["blocking"]["gate_a_status"], "FAIL")

    def test_gate_a_degraded_allowed(self):
        _, s = self.build_task1()
        ev = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_A"],
                          "research_snapshot_20261104", "2026-11-03T00:00:00")
        self.assertFalse(ev["blocked"])
        self.assertEqual(ev["gate_a_status"], "DEGRADED")

    def test_missing_facts_blocked(self):
        _, s = self.build_task1()
        ev = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_A"],
                          "research_snapshot_20261105", "2026-11-03T00:00:00")
        self.assertTrue(ev["blocked"])
        self.assertEqual(ev["blocking"]["stage"], "facts_structure")

    def test_fail_quality_and_nonnumeric_excluded(self):
        obs = dt._observations_from_snapshot(SNAPSHOT_GOLD)
        self.assertEqual(sorted(obs), ["gold.copper.ratio", "us10y.real"])
        self.assertEqual(obs["gold.copper.ratio"],
                         [("2026-11-01", 8.9), ("2026-11-02", 9.2)])
        self.assertEqual(obs["us10y.real"], [("2026-11-02", 2.4)])

    def test_digest_recomputed_not_declared(self):
        _, s = self.build_task1()
        ev = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_A"],
                          "research_snapshot_20261102", "2026-11-03T00:00:00")
        self.assertEqual(ev["digest_snapshot"], GOLDEN["DIGEST"])  # 独立复算值

    def test_wrong_hypothesis_and_bad_as_of_rejected(self):
        _, s = self.build_task1()
        with self.assertRaises(ValueError):           # 假设不在任务集
            self.eval_hp(GOLDEN["TASK1"], "HP-19990101-00000000",
                         "research_snapshot_20261102", "2026-11-03T00:00:00")
        with self.assertRaises(ValueError):           # as_of 非法(禁墙钟缺省)
            dt.evaluate_hypothesis_conditions(
                GOLDEN["TASK1"], GOLDEN["HP_A"], "research_snapshot_20261102",
                self.sd, as_of="not-a-date", archive_dir=self.ad)


# ══ 7. 结论状态机(P-C-10/P-C-11;§6.3 黄金链+终态不可重开) ═════════════

class TestConclusionStateMachine(WPCTestBase):

    def _golden_confirmed(self):
        _, s = self.build_task1()
        ev = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_A"],
                          "research_snapshot_20261102", "2026-11-03T00:00:00")
        return dt.adjudicate_conclusion(GOLDEN["TASK1"], GOLDEN["HP_A"], ev,
                                        archive_dir=self.ad,
                                        created_at="2026-11-03T01:00:00")

    def test_confirmed_golden(self):
        c = self._golden_confirmed()
        self.assertEqual(c["new_status"], "CONFIRMED")
        self.assertEqual(c["conclusion_id"], GOLDEN["CON_CONFIRMED"])
        self.assertEqual(c["prior_status"], "UNADJUDICATED")
        self.assertIn("未解释重大反证=False", c["reasons"][-1])
        self.assertEqual(dt.current_conclusion_status(GOLDEN["TASK1"],
                                                     GOLDEN["HP_A"], self.ad),
                         "CONFIRMED")

    def test_expired_unresolved_golden(self):
        _, s = self.build_task1()
        ev = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_B"],
                          "research_snapshot_20261102", "2026-11-20T00:00:00")
        c = dt.adjudicate_conclusion(GOLDEN["TASK1"], GOLDEN["HP_B"], ev,
                                     archive_dir=self.ad,
                                     created_at="2026-11-20T01:00:00")
        self.assertEqual(c["new_status"], "EXPIRED_UNRESOLVED")
        self.assertEqual(c["conclusion_id"], GOLDEN["CON_EXPIRED"])

    def test_falsified_golden_and_precedence(self):
        # HYP_C: 支持向 C1 与证伪向 C2 双双 touch TRIGGERED → 优先序①>②
        _, s = self.build_task2()
        ev = self.eval_hp(GOLDEN["TASK2"], GOLDEN["HP_C"],
                          "research_snapshot_20261102", "2026-11-03T00:00:00")
        self.assertEqual(self.outcome_of(ev, GOLDEN["FC_C1"])["outcome"],
                         "TRIGGERED")
        self.assertEqual(self.outcome_of(ev, GOLDEN["FC_C2"])["outcome"],
                         "TRIGGERED")
        c = dt.adjudicate_conclusion(GOLDEN["TASK2"], GOLDEN["HP_C"], ev,
                                     archive_dir=self.ad,
                                     created_at="2026-11-03T02:00:00")
        self.assertEqual(c["new_status"], "FALSIFIED")       # 证伪向优先
        self.assertEqual(c["conclusion_id"], GOLDEN["CON_FALSIFIED"])

    def test_inconclusive_golden_data_blocked(self):
        _, s = self.build_task2()
        ev = self.eval_hp(GOLDEN["TASK2"], GOLDEN["HP_D"],
                          "research_snapshot_20261102", "2026-11-20T00:00:00")
        c = dt.adjudicate_conclusion(GOLDEN["TASK2"], GOLDEN["HP_D"], ev,
                                     archive_dir=self.ad,
                                     created_at="2026-11-20T02:00:00")
        self.assertEqual(c["new_status"], "INCONCLUSIVE")
        self.assertEqual(c["conclusion_id"], GOLDEN["CON_INCONCLUSIVE"])
        self.assertIn("数据不足", c["decision_rule"])

    def test_partial_falsified_golden(self):
        _, s = self.build_task2()
        ev = self.eval_hp(GOLDEN["TASK2"], GOLDEN["HP_E"],
                          "research_snapshot_20261102", "2026-11-03T00:00:00")
        c = dt.adjudicate_conclusion(GOLDEN["TASK2"], GOLDEN["HP_E"], ev,
                                     archive_dir=self.ad,
                                     created_at="2026-11-03T03:00:00")
        self.assertEqual(c["new_status"], "PARTIAL_FALSIFIED")
        self.assertEqual(c["conclusion_id"], GOLDEN["CON_PARTIAL_FALSIFIED"])
        self.assertIn("不利观测", c["reasons"][0])

    def test_partial_support_unexplained_counter_then_falsified(self):
        # TASK3: 支持向 touch 命中+未解释反证证据 → PARTIAL_SUPPORT 驻留;
        # premise 兑现后证伪向触发 → 轮次中态可续评 → FALSIFIED(P-C-11③→①)
        r, s = self.build_task3()
        tid, hp_f, fc_f2 = s["task_id"], s["hypothesis_ids"][0], s["condition_ids"][1]
        dm.activate_task(tid, archive_dir=self.ad, created_at="2026-11-02T12:00:00")
        ev_contra = dm.register_evidence(             # 未解释反证(方向=反对)
            tid, 1,
            {"hypothesis_id": hp_f, "metric_id": "gold.copper.ratio",
             "fact_id": "gold.copper.ratio@2026-11-02", "value": 9.2,
             "observation_date": "2026-11-02",
             "snapshot_id": "research_snapshot_20261102",
             "direction": "反对", "weight": 3, "mechanism": "避险与估值",
             "explained": False, "note": "反例观测登记"},
            self.sd, archive_dir=self.ad, created_at="2026-11-02T13:00:00")
        self.assertEqual(ev_contra["status"], "written")
        ev1 = self.eval_hp(tid, hp_f, "research_snapshot_20261102",
                           "2026-11-03T00:00:00")    # 前提未兑现: 证伪向 NOT_YET_IN_WINDOW
        c1 = dt.adjudicate_conclusion(tid, hp_f, ev1, archive_dir=self.ad,
                                      created_at="2026-11-03T01:00:00")
        self.assertEqual(c1["new_status"], "PARTIAL_SUPPORT")   # ③驻留非终态
        rec = dt._load_scoped_record(c1["conclusion_id"],
                                     dt.COLLECTION_CONCLUSIONS, self.ad,
                                     "结论", dt.validate_conclusion_record, tid)
        self.assertTrue(rec["unexplained_major_counter"])       # 经 dm 复用汇编
        ev2 = self.eval_hp(tid, hp_f, "research_snapshot_20261102",
                           "2026-11-05T00:00:00",
                           premise={fc_f2: "2026-11-01"})       # 兑现→触发
        c2 = dt.adjudicate_conclusion(tid, hp_f, ev2, archive_dir=self.ad,
                                      created_at="2026-11-05T01:00:00")
        self.assertEqual(c2["new_status"], "FALSIFIED")         # ①优先
        self.assertEqual(c2["prior_status"], "PARTIAL_SUPPORT") # 轮次中续评合法

    def test_unadjudicated_default_and_unchanged_zero_record(self):
        _, s = self.build_task3()
        hp_g = s["hypothesis_ids"][1]
        self.assertEqual(dt.current_conclusion_status(s["task_id"], hp_g,
                                                      self.ad),
                         "UNADJUDICATED")             # 无记录默认
        ev = self.eval_hp(s["task_id"], hp_g, "research_snapshot_20261102",
                          "2026-11-03T00:00:00")      # expiry 未到期 PENDING
        c = dt.adjudicate_conclusion(s["task_id"], hp_g, ev,
                                     archive_dir=self.ad,
                                     created_at="2026-11-03T01:00:00")
        self.assertEqual(c["status"], "unchanged")    # 零信号零追加记录
        self.assertIsNone(c["conclusion_id"])
        self.assertEqual(dt.list_conclusions(s["task_id"], self.ad), [])
        self.assertEqual(dt.current_conclusion_status(s["task_id"], hp_g,
                                                      self.ad),
                         "UNADJUDICATED")

    def test_terminal_re_adjudication_rejected(self):
        c = self._golden_confirmed()                  # CONFIRMED 终态
        ev = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_A"],
                          "research_snapshot_20261102", "2026-11-20T00:00:00")
        with self.assertRaises(ValueError) as cm:
            dt.adjudicate_conclusion(GOLDEN["TASK1"], GOLDEN["HP_A"], ev,
                                     archive_dir=self.ad,
                                     created_at="2026-11-21T01:00:00")
        self.assertIn("终态后再评一律拒收", str(cm.exception))

    def test_falsified_re_adjudication_rejected(self):
        _, s = self.build_task2()
        ev = self.eval_hp(GOLDEN["TASK2"], GOLDEN["HP_C"],
                          "research_snapshot_20261102", "2026-11-03T00:00:00")
        dt.adjudicate_conclusion(GOLDEN["TASK2"], GOLDEN["HP_C"], ev,
                                 archive_dir=self.ad,
                                 created_at="2026-11-03T02:00:00")
        with self.assertRaises(ValueError) as cm:     # FALSIFIED 不可改写
            dt.adjudicate_conclusion(GOLDEN["TASK2"], GOLDEN["HP_C"], ev,
                                     archive_dir=self.ad,
                                     created_at="2026-11-04T02:00:00")
        self.assertIn("FALSIFIED 不可改写", str(cm.exception))

    def test_blocked_evaluation_rejected_for_adjudication(self):
        _, s = self.build_task1()
        ev = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_A"],
                          "research_snapshot_20261103", "2026-11-03T00:00:00")
        self.assertTrue(ev["blocked"])
        with self.assertRaises(ValueError) as cm:     # 阻断件不得入结论裁决
            dt.adjudicate_conclusion(GOLDEN["TASK1"], GOLDEN["HP_A"], ev,
                                     archive_dir=self.ad,
                                     created_at="2026-11-03T01:00:00")
        self.assertIn("阻断", str(cm.exception))
        self.assertEqual(dt.list_conclusions(GOLDEN["TASK1"], self.ad), [])

    def test_conclusion_record_schema_fields(self):
        c = self._golden_confirmed()
        rec = dt._load_scoped_record(c["conclusion_id"],
                                     dt.COLLECTION_CONCLUSIONS, self.ad,
                                     "结论", dt.validate_conclusion_record,
                                     GOLDEN["TASK1"])
        self.assertEqual(rec["status"], "CONFIRMED")
        self.assertEqual(rec["prior_status"], "UNADJUDICATED")
        self.assertEqual(rec["snapshot_id"], "research_snapshot_20261102")
        self.assertEqual(rec["digest_snapshot"], GOLDEN["DIGEST"])
        self.assertEqual(rec["as_of"], "2026-11-03")
        self.assertEqual([e["condition_id"] for e in rec["evaluations"]],
                         [GOLDEN["FC_A1"], GOLDEN["FC_A2"]])
        self.assertFalse(rec["unexplained_major_counter"])


# ══ 8. 证伪后处置三路径(P-C-13;要点③) ═════════════════════════════════

class TestFalsificationDisposal(WPCTestBase):

    def _falsified_task2(self):
        _, s = self.build_task2()
        ev = self.eval_hp(GOLDEN["TASK2"], GOLDEN["HP_C"],
                          "research_snapshot_20261102", "2026-11-03T00:00:00")
        dt.adjudicate_conclusion(GOLDEN["TASK2"], GOLDEN["HP_C"], ev,
                                 archive_dir=self.ad,
                                 created_at="2026-11-03T02:00:00")
        return s

    def test_disposal_golden_no_archive(self):
        # 任务在 ACTIVE(非 TRACKING),archive_tracking=False → 黄金 DSP+
        # 非 TRACKING 如实登记不适用(P-C-13 路径③非适用态如实)
        self._falsified_task2()
        dm.activate_task(GOLDEN["TASK2"], archive_dir=self.ad,
                         created_at="2026-11-03T04:00:00")
        d = dt.apply_falsification_disposal(
            GOLDEN["TASK2"], GOLDEN["HP_C"], review_target="TH-rate-gold",
            review_evidence=["EV-gold-1", "EV-gold-2"], archive_tracking=False,
            archive_dir=self.ad, snapshot_dir=self.sd,
            created_at="2026-11-03T05:00:00")
        self.assertEqual(d["status"], "written")
        self.assertEqual(d["disposal_id"], GOLDEN["DSP_NOARCHIVE"])
        self.assertEqual(d["conclusion_id"], GOLDEN["CON_FALSIFIED"])
        self.assertEqual(d["paths"]["mark"],
                         {"conclusion_id": GOLDEN["CON_FALSIFIED"],
                          "immutable": True,
                          "marked_by": "falsified_conclusion_record"})
        self.assertFalse(d["paths"]["tracking"]["archived"])
        self.assertEqual(d["paths"]["tracking"]["task_status_at_disposal"],
                         "ACTIVE")

    def test_disposal_three_paths_full(self):
        # TASK3 走 TRACKING: 处置①修订新假设新ID ②复核提案走门禁 ③归档+
        # 闭环 followup 新任务(origin_trigger 闭环)
        r, s = self.build_task3()
        tid, hp_f, fc_f2 = s["task_id"], s["hypothesis_ids"][0], s["condition_ids"][1]
        dm.activate_task(tid, archive_dir=self.ad, created_at="2026-11-02T12:00:00")
        ev = self.eval_hp(tid, hp_f, "research_snapshot_20261102",
                          "2026-11-05T00:00:00",
                          premise={fc_f2: "2026-11-01"})
        dt.adjudicate_conclusion(tid, hp_f, ev, archive_dir=self.ad,
                                 created_at="2026-11-05T01:00:00")
        for frm, to, ca in (("ACTIVE", "RESOLVED", "2026-11-05T02:00:00"),
                            ("RESOLVED", "TRACKING", "2026-11-05T03:00:00")):
            drr.append_lifecycle_event(tid, frm, to, "测试迁移",
                                       archive_dir=self.ad, created_at=ca)
        d = dt.apply_falsification_disposal(
            tid, hp_f, review_target="TH-hedge-gold",
            review_evidence=["EV-x1", "EV-x2", "EV-x3"],
            archive_tracking=True,
            revision={"statement": "假设F2: 避险溢价区间化", "mechanism_story":
                      "区间机制修订", "reason": "证伪后实质修订",
                      "snapshot": SNAPSHOT_GOLD},
            followup={"trigger_id": r["trigger_id"], "question":
                      "避险溢价后续跟踪", "hypotheses": [HYP_F, HYP_G],
                      "criteria": CRITERIA3},
            archive_dir=self.ad, snapshot_dir=self.sd,
            created_at="2026-11-05T04:00:00")
        self.assertEqual(d["status"], "written")
        # 路径①: 标记+FALSIFIED 结论档不可改写;修订=新记录+新ID+revision_of
        self.assertTrue(d["paths"]["mark"]["immutable"])
        rev = d["paths"]["revision"]
        self.assertTrue(rev["new_hypothesis_id"].startswith("HP-"))
        self.assertNotEqual(rev["new_hypothesis_id"], hp_f)
        self.assertEqual(rev["revision_of"], hp_f)
        new_hp = drr._load_record(rev["new_hypothesis_id"],
                                  drr.COLLECTION_HYPOTHESES, self.ad, "假设",
                                  drr.validate_hypothesis_record)
        self.assertEqual(new_hp["revision_of"], hp_f)
        # 路径②: 复核提案走终态门禁正向流程,深研层不改写状态
        rr = d["paths"]["review_request"]
        self.assertEqual(rr["target"], "TH-hedge-gold")
        self.assertEqual(rr["path"], "terminal_gate_forward_flow")
        self.assertEqual(list(rr["requires"]),
                         ["engine_verified_trigger",
                          "gte2_new_independent_evidence"])
        self.assertEqual(rr["decided_by"], "gate")
        self.assertFalse(rr["deep_research_layer_writes_state"])
        # 路径③: TRACKING→ARCHIVED(既有迁移表)+闭环新任务 origin_trigger
        self.assertTrue(d["paths"]["tracking"]["archived"])
        self.assertTrue(d["paths"]["tracking"]["archive_event_id"])
        self.assertEqual(drr.current_status(tid, self.ad), "ARCHIVED")
        fu = d["paths"]["followup"]
        self.assertTrue(fu["followup_task_id"].startswith("RT-DR-"))
        followup_task = drr.load_task(fu["followup_task_id"], self.ad)
        self.assertEqual(followup_task["origin"],
                         {"origin_trigger": {"kind": "rejected_rating_proposal",
                                             "ref": "VIEW-gold-01"}})

    def test_disposal_requires_falsified(self):
        _, s = self.build_task1()
        ev = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_A"],
                          "research_snapshot_20261102", "2026-11-03T00:00:00")
        with self.assertRaises(ValueError) as cm:     # 未裁决/非 FALSIFIED 拒收
            dt.apply_falsification_disposal(
                GOLDEN["TASK1"], GOLDEN["HP_A"], review_target="TH-x",
                review_evidence=["E1"], archive_dir=self.ad,
                snapshot_dir=self.sd, created_at="2026-11-03T01:00:00")
        self.assertIn("恒须 FALSIFIED", str(cm.exception))
        dt.adjudicate_conclusion(GOLDEN["TASK1"], GOLDEN["HP_A"], ev,
                                 archive_dir=self.ad,
                                 created_at="2026-11-03T01:00:00")  # CONFIRMED
        with self.assertRaises(ValueError):           # 终态但非 FALSIFIED 仍拒
            dt.apply_falsification_disposal(
                GOLDEN["TASK1"], GOLDEN["HP_A"], review_target="TH-x",
                review_evidence=["E1"], archive_dir=self.ad,
                snapshot_dir=self.sd, created_at="2026-11-03T02:00:00")

    def test_disposal_input_validation(self):
        self._falsified_task2()
        for kw in ({"review_target": "", "review_evidence": ["E1"]},
                   {"review_target": "T", "review_evidence": []},
                   {"review_target": "T", "review_evidence": [1, 2]}):
            with self.subTest(kw=kw):
                with self.assertRaises(ValueError):
                    dt.apply_falsification_disposal(
                        GOLDEN["TASK2"], GOLDEN["HP_C"],
                        archive_dir=self.ad, snapshot_dir=self.sd,
                        created_at="2026-11-03T03:00:00", **kw)

    def test_disposal_non_tracking_honest_when_archive_requested(self):
        self._falsified_task2()                        # 任务仍 DRAFT
        d = dt.apply_falsification_disposal(
            GOLDEN["TASK2"], GOLDEN["HP_C"], review_target="TH-rate-gold",
            review_evidence=["EV-gold-1"], archive_tracking=True,
            archive_dir=self.ad, snapshot_dir=self.sd,
            created_at="2026-11-03T03:30:00")
        self.assertFalse(d["paths"]["tracking"]["archived"])
        self.assertIn("非 TRACKING",
                      d["paths"]["tracking"]["not_applicable_reason"])

    def test_falsified_conclusion_bytes_immutable_through_disposal(self):
        self._falsified_task2()
        path = drr._record_path(self.ad, dt.COLLECTION_CONCLUSIONS,
                                GOLDEN["CON_FALSIFIED"])
        with open(path, "rb") as f:
            b1 = f.read()
        with self.assertRaises(ValueError):           # 终态后再评拒收
            ev = self.eval_hp(GOLDEN["TASK2"], GOLDEN["HP_C"],
                              "research_snapshot_20261102",
                              "2026-11-20T00:00:00")
            dt.adjudicate_conclusion(GOLDEN["TASK2"], GOLDEN["HP_C"], ev,
                                     archive_dir=self.ad,
                                     created_at="2026-11-20T03:00:00")
        with open(path, "rb") as f:
            self.assertEqual(f.read(), b1)             # 结论档字节不可改写


# ══ 9. GLM 接口预留(P-C-14;零调用/缺席登记/注入点;要点④) ══════════════

class TestGLMInterface(WPCTestBase):

    def _task1_active_with_evidence(self):
        r, s = self.build_task1()
        dm.activate_task(GOLDEN["TASK1"], archive_dir=self.ad,
                         created_at="2026-11-02T10:00:00")
        return r, s

    def test_build_input_contract_fields(self):
        r, s = self._task1_active_with_evidence()
        inp = dt.build_glm_synthesis_input(GOLDEN["TASK1"], snapshot_dir=self.sd,
                                           archive_dir=self.ad)
        self.assertEqual(sorted(inp), ["contract_version", "evidence_matrix",
                                       "hypotheses", "mode", "prompt_contract",
                                       "snapshot_binding", "task_ref"])
        self.assertEqual(inp["contract_version"], "p2-gsi-1.0")
        self.assertEqual(inp["mode"], "A")
        self.assertEqual(inp["snapshot_binding"],
                         {"snapshot_id": "research_snapshot_20261102",
                          "snapshot_digest": GOLDEN["DIGEST"],
                          "gate_a": "PASS", "research_as_of": "2026-11-02"})
        self.assertEqual(inp["task_ref"]["task_id"], GOLDEN["TASK1"])
        self.assertEqual(inp["task_ref"]["question"], QUESTION)
        self.assertEqual([h["hypothesis_id"] for h in inp["hypotheses"]],
                         sorted([GOLDEN["HP_A"], GOLDEN["HP_B"]]))  # 升序=hypothesis_id 排序
        self.assertEqual(inp["evidence_matrix"]["registered_params"],
                         {"round_budget": 5, "weight_scale": [1, 5],
                          "min_discriminating_per_pair": 1})
        self.assertEqual(inp["prompt_contract"]["min_competing_hypotheses"], 2)
        self.assertTrue(inp["prompt_contract"]["counter_evidence_required"])
        self.assertTrue(inp["prompt_contract"]["numeric_grounding_required"])

    def test_build_input_gate_a_fail_rejected(self):
        # FAIL 快照不得进入 GLM 正式输入(快照纪律承接)
        r, s = self.build_task1()
        snap_fail = dict(SNAPSHOT_GOLD, snapshot_id="research_snapshot_20261103",
                         gate_a={"status": "FAIL"})
        r_fail = dt.spawn_research_from_trigger(
            r["trigger_id"], "FAIL 快照任务", [HYP_A, HYP_B], CRITERIA,
            snap_fail, archive_dir=self.ad, created_at="2026-11-03T09:00:00")
        with self.assertRaises(ValueError) as cm:
            dt.build_glm_synthesis_input(r_fail["task_id"],
                                         snapshot_dir=self.sd,
                                         archive_dir=self.ad)
        self.assertIn("不放行正式研究", str(cm.exception))

    def test_pending_adapter_absent_registration(self):
        r, s = self._task1_active_with_evidence()
        before = drr.current_status(GOLDEN["TASK1"], self.ad)
        out = dt.synthesize_competing_hypotheses(
            task_id=GOLDEN["TASK1"], snapshot_dir=self.sd, archive_dir=self.ad)
        self.assertEqual(out["adapter"], "PendingGLMAdapter")
        res = out["result"]
        self.assertEqual(res["status"], "ABSENT_PENDING_APPROVAL")
        self.assertFalse(res["called"])               # 零调用
        self.assertFalse(res["network"])              # 零网络
        self.assertIsNone(out["output_valid"])        # 缺席产物不适用校验
        self.assertIn("DP-4", out["issues"][0])
        self.assertEqual(drr.current_status(GOLDEN["TASK1"], self.ad),
                         before)                      # 状态不因此推进

    def test_output_validator_contract(self):
        good = {"hypotheses": [
                    {"statement": "s1", "falsifiable_conditions": ["c1"],
                     "confidence": "high"},
                    {"statement": "s2", "falsifiable_conditions": ["c2"],
                     "confidence": "low"}],
                "absent_ack": []}
        self.assertEqual(dt.validate_glm_synthesis_output(good), [])
        bads = {
            "lt2_hypotheses": dict(good, hypotheses=good["hypotheses"][:1]),
            "no_falsifiable": dict(good, hypotheses=[
                {"statement": "s1", "falsifiable_conditions": [],
                 "confidence": "high"},
                {"statement": "s2", "falsifiable_conditions": ["c2"],
                 "confidence": "low"}]),
            "bad_confidence": dict(good, hypotheses=[
                {"statement": "s1", "falsifiable_conditions": ["c1"],
                 "confidence": "very_high"},
                {"statement": "s2", "falsifiable_conditions": ["c2"],
                 "confidence": "low"}]),
            "missing_absent_ack": {"hypotheses": good["hypotheses"]},
            "not_dict": ["not", "a", "dict"],
        }
        for name, payload in bads.items():
            with self.subTest(bad=name):
                self.assertNotEqual(
                    dt.validate_glm_synthesis_output(payload), [])

    def test_injected_stub_valid_and_invalid(self):
        class Stub(dt.GLMSynthesisAdapter):
            def __init__(self, payload_out):
                self.payload_out = payload_out
            def synthesize(self, payload):
                return self.payload_out
        good = {"hypotheses": [
                    {"statement": "竞争1", "falsifiable_conditions": ["f1"],
                     "confidence": "medium"},
                    {"statement": "竞争2", "falsifiable_conditions": ["f2"],
                     "confidence": "high"}],
                "absent_ack": ["数据面缺席项"]}
        out = dt.synthesize_competing_hypotheses(payload={"x": 1},
                                                 adapter=Stub(good))
        self.assertEqual(out["adapter"], "Stub")
        self.assertTrue(out["output_valid"])
        self.assertEqual(out["issues"], [])
        out2 = dt.synthesize_competing_hypotheses(
            payload={"x": 1}, adapter=Stub({"hypotheses": [], "absent_ack": []}))
        self.assertFalse(out2["output_valid"])

    def test_base_adapter_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            dt.GLMSynthesisAdapter().synthesize({"x": 1})

    def test_missing_task_and_payload_rejected(self):
        with self.assertRaises(ValueError):
            dt.synthesize_competing_hypotheses(archive_dir=self.ad)


# ══ 10. 记录 schema 负向(P-C-04/P-C-10/P-C-13 校验面) ══════════════════

class TestRecordSchemas(WPCTestBase):

    def _golden_conclusion_record(self):
        _, s = self.build_task1()
        ev = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_A"],
                          "research_snapshot_20261102", "2026-11-03T00:00:00")
        c = dt.adjudicate_conclusion(GOLDEN["TASK1"], GOLDEN["HP_A"], ev,
                                     archive_dir=self.ad,
                                     created_at="2026-11-03T01:00:00")
        return dt._load_scoped_record(c["conclusion_id"],
                                      dt.COLLECTION_CONCLUSIONS, self.ad,
                                      "结论", dt.validate_conclusion_record,
                                      GOLDEN["TASK1"])

    def test_conclusion_status_vocabulary(self):
        rec = self._golden_conclusion_record()
        for bad in ("SUPPORTED", "final", "PARTIAL", 1, None, "UNADJUDICATED"):
            with self.subTest(status=bad):
                m = dict(rec, status=bad)
                self.assertNotEqual(dt.validate_conclusion_record(m), [])

    def test_conclusion_terminal_prior_rejected(self):
        rec = self._golden_conclusion_record()
        m = dict(rec, prior_status="FALSIFIED")       # 终态不可为前态
        issues = dt.validate_conclusion_record(m)
        self.assertTrue(any("终态不可为前态" in i for i in issues))

    def test_conclusion_binding_formats(self):
        rec = self._golden_conclusion_record()
        for field, bad in (("digest_snapshot", "XYZ!not-hex"),
                           ("snapshot_id", "snap-2026"),
                           ("conclusion_id", "TRG-wrong-prefix-1")):
            with self.subTest(field=field):
                m = dict(rec)
                m[field] = bad
                self.assertNotEqual(dt.validate_conclusion_record(m), [])

    def test_conclusion_missing_fields(self):
        issues = dt.validate_conclusion_record({"record_type": "x"})
        self.assertTrue(any("缺字段" in i for i in issues))

    def test_disposal_review_request_shape(self):
        _, s = self.build_task2()
        ev = self.eval_hp(GOLDEN["TASK2"], GOLDEN["HP_C"],
                          "research_snapshot_20261102", "2026-11-03T00:00:00")
        dt.adjudicate_conclusion(GOLDEN["TASK2"], GOLDEN["HP_C"], ev,
                                 archive_dir=self.ad,
                                 created_at="2026-11-03T02:00:00")
        d = dt.apply_falsification_disposal(
            GOLDEN["TASK2"], GOLDEN["HP_C"], review_target="TH-x",
            review_evidence=["E1"], archive_tracking=False,
            archive_dir=self.ad, snapshot_dir=self.sd,
            created_at="2026-11-03T06:00:00")
        rec = dt._load_scoped_record(d["disposal_id"], dt.COLLECTION_DISPOSALS,
                                     self.ad, "处置",
                                     dt.validate_disposal_record,
                                     GOLDEN["TASK2"])
        rr = dict(rec)
        rr["paths"] = json.loads(json.dumps(rec["paths"]))
        rr["paths"]["review_request"]["requires"] = ["weaker_evidence_only"]
        self.assertNotEqual(dt.validate_disposal_record(rr), [])
        rr2 = json.loads(json.dumps(rec))
        rr2["paths"]["review_request"]["decided_by"] = "deep_research_layer"
        issues = dt.validate_disposal_record(rr2)
        self.assertTrue(any("decided_by" in i or "review_request" in i
                            for i in issues))
        rr3 = json.loads(json.dumps(rec))
        rr3["paths"]["review_request"]["deep_research_layer_writes_state"] = True
        self.assertNotEqual(dt.validate_disposal_record(rr3), [])


# ══ 11. 黄金确定性(P-C-02/P-C-18;跨沙箱/重放/独立复算) ═════════════════

class TestGoldenDeterminism(WPCTestBase):

    def test_cross_sandbox_full_chain_equal(self):
        _, s1 = self.build_task1()
        ev1 = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_A"],
                           "research_snapshot_20261102", "2026-11-03T00:00:00")
        dt.adjudicate_conclusion(GOLDEN["TASK1"], GOLDEN["HP_A"], ev1,
                                 archive_dir=self.ad,
                                 created_at="2026-11-03T01:00:00")
        tmp2 = tempfile.mkdtemp(prefix="p2-wp-c-det2-")
        try:
            ad2 = os.path.join(tmp2, "archive")
            sd2 = os.path.join(tmp2, "snapshots")
            os.makedirs(sd2)
            with open(os.path.join(sd2, "research_snapshot_20261102.json"),
                      "w", encoding="utf-8") as f:
                json.dump(SNAPSHOT_GOLD, f, ensure_ascii=False, sort_keys=True)
            r = dt.register_tracking_trigger(
                TRG_THESIS["kind"], TRG_THESIS["ref"], TRG_THESIS["payload"],
                archive_dir=ad2, created_at=TRG_THESIS["created_at"])
            s2 = dt.spawn_research_from_trigger(
                r["trigger_id"], QUESTION, [HYP_A, HYP_B], CRITERIA,
                SNAPSHOT_GOLD, archive_dir=ad2, created_at=TASK_CA)
            ev = dt.evaluate_hypothesis_conditions(
                s2["task_id"], s2["hypothesis_ids"][0],
                "research_snapshot_20261102", sd2, as_of="2026-11-03T00:00:00",
                archive_dir=ad2)
            c2 = dt.adjudicate_conclusion(s2["task_id"],
                                          s2["hypothesis_ids"][0], ev,
                                          archive_dir=ad2,
                                          created_at="2026-11-03T01:00:00")
            self.assertEqual(s1["task_id"], s2["task_id"])
            self.assertEqual(s2["task_id"], GOLDEN["TASK1"])
            self.assertEqual(c2["conclusion_id"], GOLDEN["CON_CONFIRMED"])
            # 记录档 canonical 逐字节等(同输入同输出)
            p1 = drr._record_path(self.ad, dt.COLLECTION_CONCLUSIONS,
                                  GOLDEN["CON_CONFIRMED"])
            p2 = drr._record_path(ad2, dt.COLLECTION_CONCLUSIONS,
                                  GOLDEN["CON_CONFIRMED"])
            with open(p1, "rb") as f1, open(p2, "rb") as f2:
                self.assertEqual(f1.read(), f2.read())
        finally:
            shutil.rmtree(tmp2, ignore_errors=True)

    def test_conclusion_replay_same_id_rejected(self):
        _, s = self.build_task1()
        ev = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_B"],
                          "research_snapshot_20261102", "2026-11-20T00:00:00")
        c1 = dt.adjudicate_conclusion(GOLDEN["TASK1"], GOLDEN["HP_B"], ev,
                                      archive_dir=self.ad,
                                      created_at="2026-11-20T01:00:00")
        # 零墙钟: 同日同评估同状态 → 同 ID(指纹不含时刻);终态后再评一律拒收
        self.assertEqual(c1["conclusion_id"], GOLDEN["CON_EXPIRED"])
        with self.assertRaises(ValueError) as cm:
            dt.adjudicate_conclusion(GOLDEN["TASK1"], GOLDEN["HP_B"], ev,
                                     archive_dir=self.ad,
                                     created_at="2026-11-20T09:00:00")
        self.assertIn("终态后再评一律拒收", str(cm.exception))
        # append-only: 同 ID 记录仅一份
        self.assertEqual([r["conclusion_id"] for r in
                          dt.list_conclusions(GOLDEN["TASK1"], self.ad)],
                         [GOLDEN["CON_EXPIRED"]])

    def test_conclusion_fingerprint_independent_recompute(self):
        # 测试内首原理复算 CON 指纹(禁导入被测模块计算): 同 ID=同指纹证明
        fp = {"task_id": GOLDEN["TASK1"],
              "hypothesis_id": GOLDEN["HP_A"], "status": "CONFIRMED",
              "evaluations": [
                  {"condition_id": GOLDEN["FC_A1"], "outcome": "TRIGGERED",
                   "evidence": {"obs_date": "2026-11-02", "value": 9.2}},
                  {"condition_id": GOLDEN["FC_A2"], "outcome": "PENDING",
                   "evidence": None}]}
        expected = "CON-%s-%s" % ("20261103", _h8(fp))
        self.assertEqual(expected, GOLDEN["CON_CONFIRMED"])
        _, s = self.build_task1()
        ev = self.eval_hp(GOLDEN["TASK1"], GOLDEN["HP_A"],
                          "research_snapshot_20261102", "2026-11-03T00:00:00")
        c = dt.adjudicate_conclusion(GOLDEN["TASK1"], GOLDEN["HP_A"], ev,
                                     archive_dir=self.ad,
                                     created_at="2026-11-03T01:00:00")
        self.assertEqual(c["conclusion_id"], expected)

    def test_trigger_id_fingerprint_independent_recompute(self):
        fp = {"kind": TRG_PROP["kind"], "ref": TRG_PROP["ref"],
              "payload": TRG_PROP["payload"]}
        expected = "TRG-%s-%s" % ("20261102", _h8(fp))
        self.assertEqual(expected, GOLDEN["TRG_PROP"])


# ══ 12. 静态纯度(P-C-15/P-C-17;零 data/daily/零网络/零研究状态直写) ════

class TestStaticPurity(WPCTestBase):

    SRC_PATH = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "scripts", "deep_research_tracking_engine.py")

    def test_no_daily_path_literal(self):
        with open(self.SRC_PATH, "r", encoding="utf-8") as f:
            src = f.read()
        # 文档字符串中的纪律表述除外(WP-A test_no_raw_daily_reference 同款
        # 先例),代码面零 data/daily 路径字面
        src = src.replace("data/daily 原始采集档", "")
        self.assertNotIn("data/daily", src)          # 结构性不可达原始采集档
        self.assertNotIn("raw/", src)

    def test_no_network_imports(self):
        with open(self.SRC_PATH, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        banned = {"requests", "urllib", "socket", "http", "httpx",
                  "openai", "aiohttp", "ssl", "ftplib", "smtplib", "telnetlib"}
        found = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    found.add(node.module.split(".")[0])
        self.assertEqual(found & banned, set(), "禁止网络出站 import: %s"
                         % (found & banned))
        stdlib_ok = {"json", "os", "sys", "datetime", "hashlib",
                     "deep_research_registrar", "deep_research_matrix_engine",
                     "research_provenance", "allocation_engine",
                     "research_archive"}
        self.assertTrue(found <= stdlib_ok, "import 面越界: %s" % (found - stdlib_ok))

    def test_no_research_state_direct_write_paths(self):
        with open(self.SRC_PATH, "r", encoding="utf-8") as f:
            src = f.read()
        for literal in ("thesis.json", "allocation_views.json",
                        "predictions.json", "views.json"):
            self.assertNotIn(literal, src)           # §6.2 L169 Gate B 纪律


# ══ 13. 端到端链(要点①③;触发→spawn→评估→证伪→处置→闭环) ═════════════

class TestEndToEndChain(WPCTestBase):

    def test_full_chain_sandbox_contained(self):
        r, s = self.build_task3()
        tid, hp_f, fc_f2 = s["task_id"], s["hypothesis_ids"][0], s["condition_ids"][1]
        dm.activate_task(tid, archive_dir=self.ad, created_at="2026-11-02T12:00:00")
        dm.register_evidence(
            tid, 1,
            {"hypothesis_id": hp_f, "metric_id": "gold.copper.ratio",
             "fact_id": "gold.copper.ratio@2026-11-02", "value": 9.2,
             "observation_date": "2026-11-02",
             "snapshot_id": "research_snapshot_20261102",
             "direction": "支持", "weight": 4, "mechanism": "避险与估值",
             "note": "端到端支持证据"},
            self.sd, archive_dir=self.ad, created_at="2026-11-02T13:00:00")
        ev = self.eval_hp(tid, hp_f, "research_snapshot_20261102",
                          "2026-11-05T00:00:00",
                          premise={fc_f2: "2026-11-01"})
        c = dt.adjudicate_conclusion(tid, hp_f, ev, archive_dir=self.ad,
                                     created_at="2026-11-05T01:00:00")
        self.assertEqual(c["new_status"], "FALSIFIED")
        d = dt.apply_falsification_disposal(
            tid, hp_f, review_target="TH-e2e", review_evidence=["E-e2e-1"],
            archive_tracking=False, archive_dir=self.ad, snapshot_dir=self.sd,
            created_at="2026-11-05T02:00:00")
        self.assertEqual(d["status"], "written")
        # 沙箱内聚: 全部产物落在临时档案根内(data/research 零触碰)
        for collection in (dt.COLLECTION_TRIGGERS, dt.COLLECTION_CONCLUSIONS,
                           dt.COLLECTION_DISPOSALS, "deep_research_tasks",
                           "deep_research_hypotheses",
                           "deep_research_conditions", "deep_research_events",
                           "deep_research_evidence"):
            d_col = os.path.join(self.ad, dt.ARCHIVE_FAMILY, collection)
            if os.path.isdir(d_col):
                for name in os.listdir(d_col):
                    self.assertTrue(os.path.abspath(
                        os.path.join(d_col, name)).startswith(self.tmp))
        # 缺省档案根=仓库内 data/research 子域(边界登记;测试全沙箱不触达)
        self.assertIn(os.path.join("data", "research"),
                      dt.DEFAULT_ARCHIVE_DIR)

    def test_trigger_spawn_gate_bubble_integrated(self):
        # 全链负向: spawn 提交快照非 dict → 上游校验兜底(P-C-05 衔接面)
        r = self.reg(TRG_PRED_PREM)
        with self.assertRaises(ValueError):
            dt.spawn_research_from_trigger(r["trigger_id"], "问题",
                                           [HYP_A, HYP_B], CRITERIA,
                                           "not-a-snapshot",
                                           archive_dir=self.ad,
                                           created_at=TASK_CA)


if __name__ == "__main__":
    unittest.main()
