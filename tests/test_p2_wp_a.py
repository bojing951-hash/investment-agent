#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P2-WP-A tests: 深研任务与假设登记器(全合成 fixture,零网络)。

数据纪律: 唯一数据源=本文件内合成 fixture(临时目录落档);不依赖 data/daily/
真实采集档与真实研究档案,预期值不随真实数据演进漂移(R014-D3/R022/R066 纪律);
预期值全部字面量硬编码(不从被测模块导入计算,禁自证恒真)。

fixture→预期值映射(逐断言组可追溯到本文件定义处):
- 合成快照 FIX_SNAP(L56-L61) → GOLDEN_DIGEST(L40)/绑定校验断言组(类 TestSnapshotBinding)
- 黄金输入集 _golden_inputs()(L64-L96) → 五 ID 定值(L33-L38)/黄金登记断言组
  (TestGoldenRegistration)/重放幂等断言组(TestAppendOnly)
- 单假设/互异/origin 违规构造(各负向用例内联) → DRAFT 负向断言组(TestDraftNegative)
- 条件字段违规构造(各负向用例内联) → schema 断言组(TestConditionSchema)
- 篡改快照/篡改档(各用例内联改写 tempdir 文件) → 绑定校验断言组(TestSnapshotBinding)
"""
import hashlib
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', 'scripts'))
import deep_research_registrar as drr
import research_provenance as rp

# ══ 预期值字面量(硬编码;来源=开工预计算 2026-11-07,独立于被测模块复算) ══

GOLDEN_TASK_ID = "RT-DR-20260301-e97e9e78"        # 指纹=黄金输入集 canonical(独立预计算)
GOLDEN_HP1 = "HP-20260301-0a1ab378"
GOLDEN_HP2 = "HP-20260301-eef21af6"
GOLDEN_FC1 = "FC-20260301-a275dc62"
GOLDEN_FC2 = "FC-20260301-2cf35cc2"
GOLDEN_EVENT_INIT = "EV-20260301-b2847cc5"
GOLDEN_DIGEST = "36fdd08c3cd49f60"                 # = rp.digest_snapshot(FIX_SNAP) 独立预计算
GOLDEN_PARAMS = {"round_budget": 5,                # DP-1 定值(登记=常量=echo 三方一致)
                 "weight_scale": [1, 5],           # DP-2 定值
                 "min_discriminating_per_pair": 1}  # DP-6 定值
CA = "2026-03-01T09:00:00+00:00"                   # 注入时刻(零墙钟纪律)

# ══ 合成 fixture(唯一数据源;真实数据档永不进入) ═════════════════════════

FIX_SNAP = {"snapshot_id": "research_snapshot_20260301",
            "meta": {"synthetic": True, "fixture": "P2-WP-A golden"},
            "facts": {"TIPS_10Y": {"value": 1.62, "unit": "percent"},
                      "GOLD_F": {"value": 2650.0, "unit": "usd_per_oz"}}}

H1S = "结构性背离假设: 央行购金与地缘风险溢价主导,利率-金价负相关性已结构性减弱"
H1M = "官方部门持续购金抬高金价对实际利率上行的敏感阈值,背离在预算窗口内不消解"
H2S = "传统负相关假设: 利率-金价负相关性仍成立,当前背离为流动性驱动的暂时现象"
H2M = "滚动窗口内相关性将回升至负值区间,背离在预算窗口内消解"

C1 = {"metric_id": "TIPS_10Y", "operator": ">=", "threshold": 1.75,
      "window": {"mode": "expiry", "weeks": 12}, "premise": None,
      "threshold_source": "registry_validation", "direction": "falsifying",
      "source_note": "注册表 validation 区间上沿"}
C2 = {"metric_id": "GOLD_F", "operator": "<=", "threshold": 2600.0,
      "window": {"mode": "touch", "deadline": "2026-06-30"},
      "premise": "FOMC 6月会议前不降息",
      "threshold_source": "user_explicit", "direction": "supporting",
      "source_note": "用户显式给定"}

QUESTION = "2026年3月实际利率上行与金价坚挺的背离是否为结构性变化?"
CRITERION = "窗口末滚动60日相关系数符号: 背离假设预测>=0,传统假设预测<0"


def _golden_inputs():
    """黄金输入集(每用例独立深拷贝,防用例间串改)。"""
    return {"question": QUESTION,
            "origin": {"origin_query_id": "QB-20260301-001"},
            "hypotheses": [
                {"statement": H1S, "mechanism_story": H1M,
                 "conditions": [dict(C1)]},
                {"statement": H2S, "mechanism_story": H2M,
                 "conditions": [dict(C2)]}],
            "criteria": [{"pair": [H1S, H2S], "criterion": CRITERION}]}


class _Sandbox(unittest.TestCase):
    """tempdir 沙箱: archive_dir+快照目录+快照文件逐用例新建。"""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.archive = os.path.join(self._td.name, "archive")
        self.snap_dir = os.path.join(self._td.name, "snapshots")
        os.makedirs(self.snap_dir)
        self._write_snapshot(FIX_SNAP)

    def tearDown(self):
        self._td.cleanup()

    def _write_snapshot(self, snap):
        with open(os.path.join(self.snap_dir,
                               f"{snap['snapshot_id']}.json"), "w",
                  encoding="utf-8") as f:
            json.dump(snap, f, ensure_ascii=False)

    def register(self, inputs=None, snapshot=None, created_at=CA):
        inputs = inputs or _golden_inputs()
        return drr.register_deep_research_task(
            inputs["question"], inputs["origin"], inputs["hypotheses"],
            inputs["criteria"], snapshot or FIX_SNAP,
            archive_dir=self.archive, created_at=created_at)

    def task_path(self, task_id):
        return os.path.join(self.archive, drr.ARCHIVE_FAMILY,
                            drr.COLLECTION_TASKS, f"{task_id}.json")


class TestGoldenRegistration(_Sandbox):
    """要点②正面+DRAFT 五要件+ID 族+参数 echo 三方一致。"""

    def test_golden_registration(self):
        res = self.register()
        self.assertEqual(res["status"], "written")
        self.assertEqual(res["task_id"], GOLDEN_TASK_ID)
        self.assertEqual(res["hypothesis_ids"], [GOLDEN_HP1, GOLDEN_HP2])
        self.assertEqual(res["condition_ids"], [GOLDEN_FC1, GOLDEN_FC2])
        self.assertEqual(res["event_id"], GOLDEN_EVENT_INIT)
        self.assertEqual(res["digest_snapshot"], GOLDEN_DIGEST)
        self.assertEqual(res["registered_params"], GOLDEN_PARAMS)
        # echo=常量=登记 三方一致(R011 纪律;常量侧独立字面量 5/[1,5]/1)
        self.assertEqual(drr.DP1_ROUND_BUDGET_DEFAULT, 5)
        self.assertEqual(drr.DP2_WEIGHT_SCALE, (1, 5))
        self.assertEqual(drr.DP6_MIN_DISCRIMINATING_PER_PAIR, 1)
        # 任务档在盘内容逐字段对照(字面量预期)
        with open(self.task_path(GOLDEN_TASK_ID), encoding="utf-8") as f:
            rec = json.load(f)
        self.assertEqual(rec["record_type"], "deep_research_task")
        self.assertEqual(rec["status"], "DRAFT")
        self.assertEqual(rec["question"], QUESTION)
        self.assertEqual(rec["origin"], {"origin_query_id": "QB-20260301-001"})
        self.assertEqual(rec["hypothesis_ids"], [GOLDEN_HP1, GOLDEN_HP2])
        self.assertEqual(rec["discriminating_criteria"],
                         [{"pair": [GOLDEN_HP1, GOLDEN_HP2], "criterion": CRITERION}])
        self.assertEqual(rec["registered_params"], GOLDEN_PARAMS)
        self.assertEqual(rec["snapshot_id"], "research_snapshot_20260301")
        self.assertEqual(rec["digest_snapshot"], GOLDEN_DIGEST)
        # 条件档 registry_status(注册表实读;TIPS_10Y/GOLD_F 在注册表)
        cpath = os.path.join(self.archive, drr.ARCHIVE_FAMILY,
                             drr.COLLECTION_CONDITIONS, f"{GOLDEN_FC1}.json")
        with open(cpath, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["registry_status"], "RESOLVED")
        self.assertEqual(drr.current_status(GOLDEN_TASK_ID, archive_dir=self.archive),
                         "DRAFT")

    def test_origin_three_sources_all_register(self):
        """S-1/S-2/S-3 三入口各一正例(DESIGN §2.1 三发起来源)。"""
        for origin in (
                {"origin_anomaly": {"metric_id": "TIPS_10Y",
                                    "snapshot_id": "research_snapshot_20260301"}},
                {"origin_query_id": "QB-20260301-001"},
                {"origin_trigger": {"kind": "prediction_adjudication",
                                    "ref": "PRED-2026-001"}}):
            inputs = _golden_inputs()
            inputs["origin"] = origin
            res = self.register(inputs)
            self.assertEqual(res["status"], "written")


class TestAppendOnly(_Sandbox):
    """要点①: 重复写入/改写被拒;原档字节不动。"""

    def test_duplicate_registration_rejected_bytes_unchanged(self):
        res1 = self.register()
        self.assertEqual(res1["status"], "written")
        before = hashlib.sha256(
            open(self.task_path(GOLDEN_TASK_ID), 'rb').read()).hexdigest()
        res2 = self.register()      # 同输入重放 → 同 ID 全套
        self.assertEqual(res2["status"], "rejected-duplicate")
        after = hashlib.sha256(
            open(self.task_path(GOLDEN_TASK_ID), 'rb').read()).hexdigest()
        self.assertEqual(before, after, "重复写入被拒后原档字节必须不变")

    def test_rewrite_same_id_rejected(self):
        """改写尝试: 同 task_id 携篡改内容(轮次预算 5→9)再写入 → 拒。"""
        self.register()
        with open(self.task_path(GOLDEN_TASK_ID), encoding="utf-8") as f:
            tampered = json.load(f)
        tampered["registered_params"]["round_budget"] = 9
        status, _ = drr._write_records(
            [(tampered, self.task_path(GOLDEN_TASK_ID))], self.archive)
        self.assertEqual(status, "rejected-duplicate")
        with open(self.task_path(GOLDEN_TASK_ID), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["registered_params"]["round_budget"], 5)

    def test_duplicate_lifecycle_event_rejected(self):
        """同内容迁移事件重放被拒(公共API面): 首次写入后推导态已前移,
        重放在 from_status≠推导态 一致性防线处 fail-loud(ValueError,零写入);
        事件档文件数不增=重复未落档。"""
        self.register()
        r1 = drr.append_lifecycle_event(GOLDEN_TASK_ID, "DRAFT", "ACTIVE",
                                        "首轮证据收集开始", archive_dir=self.archive,
                                        created_at=CA)
        self.assertEqual(r1["status"], "written")
        ev_dir = os.path.join(self.archive, drr.ARCHIVE_FAMILY,
                              drr.COLLECTION_EVENTS)
        n_after_first = len(os.listdir(ev_dir))
        with self.assertRaises(ValueError) as cm:
            drr.append_lifecycle_event(GOLDEN_TASK_ID, "DRAFT", "ACTIVE",
                                       "首轮证据收集开始", archive_dir=self.archive,
                                       created_at=CA)
        self.assertIn("禁跳态", str(cm.exception))
        self.assertEqual(len(os.listdir(ev_dir)), n_after_first,
                         "重复迁移事件必须零写入")

    def test_duplicate_event_id_rejected_at_write_layer(self):
        """写入层同 event_id 预检(纵深第二层,白盒): 既有路径再写 →
        rejected-duplicate,原档字节不变。"""
        self.register()
        ev_dir = os.path.join(self.archive, drr.ARCHIVE_FAMILY,
                              drr.COLLECTION_EVENTS)
        init_id = sorted(os.listdir(ev_dir))[0][:-len(".json")]
        path = os.path.join(ev_dir, init_id + ".json")
        before = open(path, 'rb').read()
        ev = json.loads(before.decode("utf-8"))
        ev["note"] = "改写尝试(应拒)"
        status, _ = drr._write_records([(ev, path)], self.archive)
        self.assertEqual(status, "rejected-duplicate")
        self.assertEqual(open(path, 'rb').read(), before)


class TestDraftNegative(_Sandbox):
    """要点②: DRAFT 登记负向用例(假设数 <2 拒收;origin 违规拒收)。"""

    def test_single_hypothesis_rejected(self):
        inputs = _golden_inputs()
        inputs["hypotheses"] = inputs["hypotheses"][:1]
        with self.assertRaises(ValueError) as cm:
            self.register(inputs)
        self.assertIn("≥2", str(cm.exception))

    def test_zero_hypothesis_rejected(self):
        inputs = _golden_inputs()
        inputs["hypotheses"] = []
        with self.assertRaises(ValueError):
            self.register(inputs)

    def test_identical_statements_rejected(self):
        inputs = _golden_inputs()
        inputs["hypotheses"][1]["statement"] = H1S     # 互异校验
        with self.assertRaises(ValueError) as cm:
            self.register(inputs)
        self.assertIn("互异", str(cm.exception))

    def test_origin_missing_rejected(self):
        inputs = _golden_inputs()
        inputs["origin"] = {}
        with self.assertRaises(ValueError) as cm:
            self.register(inputs)
        self.assertIn("恰一", str(cm.exception))

    def test_origin_two_entries_rejected(self):
        inputs = _golden_inputs()
        inputs["origin"] = {"origin_query_id": "QB-20260301-001",
                            "origin_trigger": {"kind": "thesis_invalidation",
                                               "ref": "TH-2026-01"}}
        with self.assertRaises(ValueError):
            self.register(inputs)

    def test_origin_bad_qb_format_rejected(self):
        inputs = _golden_inputs()
        inputs["origin"] = {"origin_query_id": "QB-bad-format"}
        with self.assertRaises(ValueError) as cm:
            self.register(inputs)
        self.assertIn("QB-YYYYMMDD-NNN", str(cm.exception))

    def test_origin_bad_trigger_kind_rejected(self):
        inputs = _golden_inputs()
        inputs["origin"] = {"origin_trigger": {"kind": "unknown_kind",
                                               "ref": "X"}}
        with self.assertRaises(ValueError):
            self.register(inputs)

    def test_origin_anomaly_bad_snapshot_id_rejected(self):
        inputs = _golden_inputs()
        inputs["origin"] = {"origin_anomaly": {"metric_id": "TIPS_10Y",
                                               "snapshot_id": "snap_2026"}}
        with self.assertRaises(ValueError):
            self.register(inputs)


class TestConditionSchema(_Sandbox):
    """要点③(前半): 条件 schema 校验(§6.1 字段集)。"""

    def _bad(self, mutate):
        inputs = _golden_inputs()
        mutate(inputs["hypotheses"][0]["conditions"][0])
        with self.assertRaises(ValueError):
            self.register(inputs)

    def test_bad_operator(self):
        self._bad(lambda c: c.update(operator="="))

    def test_bad_threshold_type(self):
        self._bad(lambda c: c.update(threshold="1.75"))

    def test_bad_window_mode(self):
        self._bad(lambda c: c.update(window={"mode": "instant", "weeks": 4}))

    def test_window_neither_deadline_nor_weeks(self):
        self._bad(lambda c: c.update(window={"mode": "expiry"}))

    def test_window_both_deadline_and_weeks(self):
        self._bad(lambda c: c.update(window={"mode": "expiry", "weeks": 4,
                                             "deadline": "2026-06-30"}))

    def test_window_zero_weeks(self):
        self._bad(lambda c: c.update(window={"mode": "expiry", "weeks": 0}))

    def test_bad_deadline_format(self):
        self._bad(lambda c: c.update(window={"mode": "touch",
                                             "deadline": "2026/06/30"}))

    def test_bad_threshold_source(self):
        self._bad(lambda c: c.update(threshold_source="model_guess"))

    def test_bad_direction(self):
        self._bad(lambda c: c.update(direction="neutral"))

    def test_empty_premise(self):
        self._bad(lambda c: c.update(premise=""))

    def test_missing_per_hypothesis_condition(self):
        inputs = _golden_inputs()
        inputs["hypotheses"][1]["conditions"] = []     # 每假设 ≥1(DESIGN L152)
        with self.assertRaises(ValueError) as cm:
            self.register(inputs)
        self.assertIn("≥1", str(cm.exception))


class TestDPNoRewrite(_Sandbox):
    """要点③(后半): 登记型参数先登记后运行禁回改——回改被拒+echo 失配即校验红。"""

    def test_tampered_params_fail_record_validation(self):
        self.register()
        with open(self.task_path(GOLDEN_TASK_ID), encoding="utf-8") as f:
            rec = json.load(f)
        rec["registered_params"]["round_budget"] = 9   # 回改尝试
        issues = drr.validate_task_record(rec)
        self.assertTrue(any("round_budget" in s and "DP-1" in s
                            for s in issues), issues)
        rec2 = json.load(open(self.task_path(GOLDEN_TASK_ID), encoding="utf-8"))
        rec2["registered_params"]["weight_scale"] = [1, 3]
        issues2 = drr.validate_task_record(rec2)
        self.assertTrue(any("weight_scale" in s and "DP-2" in s
                            for s in issues2), issues2)

    def test_api_has_no_rewrite_surface(self):
        """结构性禁回改: 公开登记面无任何改写既有档的入口/参数。"""
        import inspect
        sig = inspect.signature(drr.register_deep_research_task)
        self.assertNotIn("round_budget", sig.parameters,
                         "轮次预算不得为可传参(定值即实现值,禁回改)")
        self.assertNotIn("weight_scale", sig.parameters)
        self.assertNotIn("min_discriminating_per_pair", sig.parameters)


class TestDiscriminatingCriteria(_Sandbox):
    """DP-6: 每对假设 ≥1 区分性判据。"""

    def test_no_criterion_rejected(self):
        inputs = _golden_inputs()
        inputs["criteria"] = []
        with self.assertRaises(ValueError) as cm:
            self.register(inputs)
        self.assertIn("判据不足", str(cm.exception))

    def test_partial_pair_coverage_rejected(self):
        inputs = _golden_inputs()
        h3 = {"statement": "数据质量假设: 背离源于序列对齐与数据修订伪象",
              "mechanism_story": "对齐窗口重算后背离幅度收窄至阈值内",
              "conditions": [dict(C1, metric_id="BEI_10Y", threshold=2.4)]}
        inputs["hypotheses"].append(h3)
        inputs["criteria"] = [{"pair": [H1S, H2S], "criterion": CRITERION}]  # 缺 2 对
        with self.assertRaises(ValueError) as cm:
            self.register(inputs)
        msg = str(cm.exception)
        self.assertIn("数据质量假设", msg)             # 未覆盖对被点名
        self.assertEqual(msg.count("判据不足"), 2)     # C(3,2)=3 对缺 2

    def test_full_three_pair_coverage_passes(self):
        inputs = _golden_inputs()
        h3s = "数据质量假设: 背离源于序列对齐与数据修订伪象"
        inputs["hypotheses"].append(
            {"statement": h3s,
             "mechanism_story": "对齐窗口重算后背离幅度收窄至阈值内",
             "conditions": [dict(C1, metric_id="BEI_10Y", threshold=2.4)]})
        inputs["criteria"] = [
            {"pair": [H1S, H2S], "criterion": CRITERION},
            {"pair": [H1S, h3s], "criterion": "重算后背离幅度是否收窄过半"},
            {"pair": [H2S, h3s], "criterion": "滚动相关符号是否转负"}]
        self.assertEqual(self.register(inputs)["status"], "written")

    def test_criterion_pair_member_not_in_hypotheses(self):
        inputs = _golden_inputs()
        inputs["criteria"] = [{"pair": [H1S, "不在假设集的陈述"],
                               "criterion": CRITERION}]
        with self.assertRaises(ValueError) as cm:
            self.register(inputs)
        self.assertIn("未命中假设集", str(cm.exception))


class TestSnapshotBinding(_Sandbox):
    """要点④: snapshot_id+digest 绑定校验(篡改快照→档案校验拒绝)。"""

    def test_verify_ok_golden(self):
        self.register()
        ok, issues = drr.verify_task_bindings(GOLDEN_TASK_ID, self.snap_dir,
                                              archive_dir=self.archive)
        self.assertTrue(issues == [] and ok, issues)

    def test_tampered_snapshot_rejected(self):
        self.register()
        FIX2 = dict(FIX_SNAP)
        FIX2["facts"] = {"TIPS_10Y": {"value": 9.99, "unit": "percent"},
                         "GOLD_F": {"value": 2650.0, "unit": "usd_per_oz"}}
        self._write_snapshot(FIX2)                    # 同名快照内容被篡改
        ok, issues = drr.verify_task_bindings(GOLDEN_TASK_ID, self.snap_dir,
                                              archive_dir=self.archive)
        self.assertFalse(ok)
        self.assertTrue(any("digest不匹配" in s for s in issues), issues)

    def test_tampered_record_digest_rejected(self):
        self.register()
        path = self.task_path(GOLDEN_TASK_ID)
        with open(path, encoding="utf-8") as f:
            rec = json.load(f)
        rec["digest_snapshot"] = "0123456789abcdef"   # 档案侧登记被篡改
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=1, sort_keys=True)
        ok, issues = drr.verify_task_bindings(GOLDEN_TASK_ID, self.snap_dir,
                                              archive_dir=self.archive)
        self.assertFalse(ok)
        self.assertTrue(any("digest不匹配" in s for s in issues), issues)

    def test_missing_snapshot_rejected(self):
        self.register()
        os.remove(os.path.join(self.snap_dir, "research_snapshot_20260301.json"))
        ok, issues = drr.verify_task_bindings(GOLDEN_TASK_ID, self.snap_dir,
                                              archive_dir=self.archive)
        self.assertFalse(ok)
        self.assertTrue(any("快照文件缺失" in s for s in issues), issues)

    def test_registration_recomputes_digest_not_trusting_declared(self):
        """FIX-01 双面: ①API 无 digest 入参(签名面结构性缺席);②快照 dict
        内携伪声明 digest_snapshot 键时,落档值=重算值 GOLDEN_DIGEST(禁采声明值)。"""
        import inspect
        sig = inspect.signature(drr.register_deep_research_task)
        self.assertNotIn("digest", sig.parameters)
        lying = json.loads(json.dumps(FIX_SNAP))          # 深拷贝+伪声明值
        lying["digest_snapshot"] = "0000000000000000"
        res = self.register(snapshot=lying)
        self.assertEqual(res["status"], "written")
        # 落档=对 lying 快照整体的重算值(测试侧独立重算对照),非声明值
        self.assertEqual(res["digest_snapshot"], rp.digest_snapshot(lying))
        self.assertNotEqual(res["digest_snapshot"], "0000000000000000",
                            "快照内声明 digest 必须被忽略")
        with open(self.task_path(res["task_id"]), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["digest_snapshot"],
                             rp.digest_snapshot(lying))


class TestLifecycle(_Sandbox):
    """要点①(事件面)+§2.2 状态机: 迁移表+事件溯源+当前态折叠。"""

    def test_full_chain_and_folding(self):
        self.register()
        chain = [("DRAFT", "ACTIVE", "首轮证据收集开始"),
                 ("ACTIVE", "RESOLVED", "区分性判据判定成立"),
                 ("RESOLVED", "TRACKING", "结论转持续跟踪"),
                 ("TRACKING", "ARCHIVED", "终局归档")]
        for frm, to, note in chain:
            r = drr.append_lifecycle_event(GOLDEN_TASK_ID, frm, to, note,
                                           archive_dir=self.archive, created_at=CA)
            self.assertEqual(r["status"], "written")
        self.assertEqual(drr.current_status(GOLDEN_TASK_ID,
                                            archive_dir=self.archive), "ARCHIVED")
        events = drr.list_events(GOLDEN_TASK_ID, archive_dir=self.archive)
        self.assertEqual([e["seq"] for e in events], [1, 2, 3, 4, 5])
        self.assertEqual([e["to_status"] for e in events],
                         ["DRAFT", "ACTIVE", "RESOLVED", "TRACKING", "ARCHIVED"])
        # 任务档字节未因迁移改变(事件溯源;档不可变)
        with open(self.task_path(GOLDEN_TASK_ID), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["status"], "DRAFT")

    def test_each_terminal_reachable_from_active(self):
        for term in ("RESOLVED", "ALL_FALSIFIED", "INCONCLUSIVE", "SUPERSEDED"):
            with tempfile.TemporaryDirectory() as td:   # 独立沙箱逐终态
                arch = os.path.join(td, "a")
                drr.register_deep_research_task(
                    QUESTION, {"origin_query_id": "QB-20260301-001"},
                    _golden_inputs()["hypotheses"], _golden_inputs()["criteria"],
                    FIX_SNAP, archive_dir=arch, created_at=CA)
                # 输入与黄金集相同 → id 相同(确定性指纹),直接用黄金 id
                r1 = drr.append_lifecycle_event(GOLDEN_TASK_ID, "DRAFT", "ACTIVE",
                                                "开轮", archive_dir=arch, created_at=CA)
                self.assertEqual(r1["status"], "written")
                r2 = drr.append_lifecycle_event(GOLDEN_TASK_ID, "ACTIVE", term,
                                                f"终态{term}", archive_dir=arch,
                                                created_at=CA)
                self.assertEqual(r2["status"], "written", term)

    def test_skip_state_transition_rejected(self):
        self.register()
        with self.assertRaises(ValueError) as cm:     # DRAFT→RESOLVED 跳态
            drr.append_lifecycle_event(GOLDEN_TASK_ID, "DRAFT", "RESOLVED",
                                       "跳态", archive_dir=self.archive, created_at=CA)
        self.assertIn("非法迁移", str(cm.exception))
        with self.assertRaises(ValueError) as cm2:    # from≠当前推导态
            drr.append_lifecycle_event(GOLDEN_TASK_ID, "ACTIVE", "RESOLVED",
                                       "伪起点", archive_dir=self.archive, created_at=CA)
        self.assertIn("不一致", str(cm2.exception))

    def test_archived_is_sink(self):
        self.register()
        for frm, to, note in [("DRAFT", "ACTIVE", "开轮"),
                              ("ACTIVE", "INCONCLUSIVE", "预算耗尽无新证"),
                              ("INCONCLUSIVE", "TRACKING", "转跟踪"),
                              ("TRACKING", "ARCHIVED", "归档")]:
            drr.append_lifecycle_event(GOLDEN_TASK_ID, frm, to, note,
                                       archive_dir=self.archive, created_at=CA)
        with self.assertRaises(ValueError):
            drr.append_lifecycle_event(GOLDEN_TASK_ID, "ARCHIVED", "ACTIVE",
                                       "复活", archive_dir=self.archive, created_at=CA)


class TestRevision(_Sandbox):
    """§6.3/L183: 修订=新记录+新ID(关联引用原假设);原因必填;原记录不可改写。"""

    def test_hypothesis_revision(self):
        self.register()
        before = hashlib.sha256(
            open(os.path.join(self.archive, drr.ARCHIVE_FAMILY,
                              drr.COLLECTION_HYPOTHESES,
                              f"{GOLDEN_HP1}.json"), 'rb').read()).hexdigest()
        r = drr.revise_hypothesis(GOLDEN_TASK_ID, GOLDEN_HP1,
                                  "结构性背离假设(修订): 购金流量数据加入后阈值效应增强",
                                  "新增央行购金季度数据后机制表述更新",
                                  "购金流量序列在场性复核后修订机制叙事",
                                  FIX_SNAP, archive_dir=self.archive, created_at=CA)
        self.assertEqual(r["status"], "written")
        self.assertNotEqual(r["hypothesis_id"], GOLDEN_HP1)   # 新 ID
        self.assertEqual(r["revision_of"], GOLDEN_HP1)        # 关联引用原假设
        after = hashlib.sha256(
            open(os.path.join(self.archive, drr.ARCHIVE_FAMILY,
                              drr.COLLECTION_HYPOTHESES,
                              f"{GOLDEN_HP1}.json"), 'rb').read()).hexdigest()
        self.assertEqual(before, after, "原假设记录不可改写")

    def test_revision_requires_reason(self):
        self.register()
        with self.assertRaises(ValueError):
            drr.revise_hypothesis(GOLDEN_TASK_ID, GOLDEN_HP1, "S", "M", "",
                                  FIX_SNAP, archive_dir=self.archive, created_at=CA)


class TestAbsentRegistry(_Sandbox):
    """L164①: 指标缺席注册表→ABSENT_REGISTRY 如实标,不拒收不冒充。"""

    def test_absent_metric_marked_not_rejected(self):
        inputs = _golden_inputs()
        inputs["hypotheses"][0]["conditions"][0]["metric_id"] = "XYZ_NOT_IN_REGISTRY"
        res = self.register(inputs)
        self.assertEqual(res["status"], "written")
        cpath = os.path.join(self.archive, drr.ARCHIVE_FAMILY,
                             drr.COLLECTION_CONDITIONS, f"{res['condition_ids'][0]}.json")
        with open(cpath, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["registry_status"], "ABSENT_REGISTRY")


class TestStaticPurity(unittest.TestCase):
    """AC-07.1/AC-05.4 静态面: 源码零 data/daily 直读引用+零网络 import。"""

    def setUp(self):
        self.src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     '..', 'scripts', 'deep_research_registrar.py')
        with open(self.src_path, encoding="utf-8") as f:
            self.src = f.read()

    def test_no_raw_daily_reference(self):
        self.assertNotIn("data/daily", self.src.replace(
            "data/daily 原始采集档", "").replace("结构性不可达 data/daily", ""),
            "源码不得出现 data/daily 路径直接引用(快照纪律,DESIGN §3.1)")

    def test_no_network_imports(self):
        for mod in ("requests", "urllib", "socket", "http.client", "httpx"):
            self.assertNotIn(f"import {mod}", self.src)
            self.assertNotIn(f"from {mod}", self.src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
