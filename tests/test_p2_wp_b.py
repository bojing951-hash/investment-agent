#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P2-WP-B tests: 证据矩阵装配与轮次推进引擎(全合成 fixture,零网络)。

数据纪律: 唯一数据源=本文件内合成 fixture(临时目录落档);不依赖 data/daily/
真实采集档与真实研究档案,预期值不随真实数据演进漂移(R014-D3/R022/R066 纪律);
预期值全部字面量硬编码(不从被测模块导入计算,禁自证恒真;开发期独立预计算
脚本另行复算交叉验证,方案=canonical JSON sha256 首原理实现)。

fixture→预期值映射(逐断言组可追溯到本文件定义处):
- 合成快照 FIX_SNAP_B(L78-L101)/FIX_SNAP_B_FAIL(L103-L108) →
  GOLDEN_DIGEST_B(L36)/GOLDEN_DIGEST_B_FAIL(L37)/接地负向断言组(TestEvidenceGroundingNegative)
- 黄金任务输入 _golden_inputs()(L110-L133) → 五 ID 定值(L22-L31)/黄金登记断言组
  (TestGoldenRegistration)
- 证据规格 E1..E14(_spec 工厂+SPEC 表 L135-L165) → EVI ID 定值(L32-L35)/
  矩阵 summary 定值(L40-L42)(TestMatrixAssembly)/轮次记录 RD ID 定值(L44-L53)
  (TestRoundAdvance/TestRoundTerminal)
- ODD/WEIRD/BROKEN 事实(快照内) → 接地负向: metric 错配/observation_date 错配/
  质量 FAIL(TestEvidenceGroundingNegative)
- e2e 最小数据面(global_20260301.json 单通道 2 指标,L677-L682) → 真实 sb 门禁
  FAIL→fail-closed 证据拒收→§4.4④ 收束断言组(TestOfflineE2E)
"""
import ast
import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', 'scripts'))
import deep_research_registrar as drr
import deep_research_matrix_engine as dm
import research_provenance as rp
import allocation_engine as ae

# ══ 预期值字面量(硬编码;来源=开工预计算 2026-11-07,首原理独立复算+与
#    drr/dm 方案交叉验证一致;测试运行时不经被测模块计算) ═════════════════

GOLDEN_TASK_ID = "RT-DR-20260301-014c091f"
GOLDEN_HP1 = "HP-20260301-205a9207"
GOLDEN_HP2 = "HP-20260301-e55736b6"
GOLDEN_HP3 = "HP-20260301-0c3004e5"
GOLDEN_FC1 = "FC-20260301-ad15ce51"
GOLDEN_FC2 = "FC-20260301-2f8165dd"
GOLDEN_FC3 = "FC-20260301-25910b18"
GOLDEN_EV_INIT = "EV-20260301-ed20682c"
GOLDEN_EV_ACTIVATE = "EV-20260301-6d88a61a"
GOLDEN_DIGEST_B = "41fb4043bb86a171"          # = rp.digest_snapshot(FIX_SNAP_B)
GOLDEN_DIGEST_B_FAIL = "a1ad1572eed4645f"      # = rp.digest_snapshot(FIX_SNAP_B_FAIL)
GOLDEN_PARAMS = {"round_budget": 5,            # DP-1 定值(登记=常量=echo 三方一致)
                 "weight_scale": [1, 5],       # DP-2 定值
                 "min_discriminating_per_pair": 1}  # DP-6 定值
CA = "2026-03-01T10:00:00+00:00"               # 注入时刻(零墙钟纪律)
SNAP_ID_OK = "research_snapshot_20260301"      # Gate A=PASS 合成快照
SNAP_ID_FAIL = "research_snapshot_20260302"    # Gate A=FAIL 合成快照

# 证据 ID 定值(E1..E14;指纹=规格内容,round=1)
GOLDEN_E1 = "EVI-20260301-0b3ef344"   # H1 SPX@02-13 支持 增长
GOLDEN_E2 = "EVI-20260301-e6da985e"   # H1 TIPS_10Y@02-20 支持 利率与流动性
GOLDEN_E3 = "EVI-20260301-d6b959f4"   # H1 GOLD_F@02-27 支持 避险与估值
GOLDEN_E4 = "EVI-20260301-2d39cdac"   # H1 HY_OAS@02-13 支持 信用
GOLDEN_E5 = "EVI-20260301-d6020d55"   # H1 CPI_YOY@02-27 支持 通胀
GOLDEN_E14 = "EVI-20260301-a4aa1cf3"  # H1 CCC_OAS@02-20 反对·已解释 信用
GOLDEN_E6 = "EVI-20260301-5e5e6389"   # H2 BTC@02-13 支持 资金流
GOLDEN_E7 = "EVI-20260301-32856105"   # H2 WTI_F@02-20 支持 供应与库存(DEGRADED 事实)
GOLDEN_E8 = "EVI-20260301-6b69317e"   # H2 VIX@02-27 支持 避险与估值
GOLDEN_E9 = "EVI-20260301-77f370dd"   # H2 UNRATE@02-13 支持 增长
GOLDEN_E10 = "EVI-20260301-cf215190"  # H2 DXY@02-27 反对·未解释 资金流
GOLDEN_E11 = "EVI-20260301-0350c272"  # H3 SYNTH.GOLD.value@02-13 支持
GOLDEN_E12 = "EVI-20260301-7a7f55e5"  # H3 SYNTH.GOLD.prev@02-20 支持(同基底)
GOLDEN_E13 = "EVI-20260301-7275bccd"  # H3 SPX@02-27 中性

# 轮次记录 ID 定值
GOLDEN_RD_R1_EV = "RD-20260301-a8562759"        # R1 证据推进(E1)
GOLDEN_RD_R2_COMP = "RD-20260301-071366c3"      # R2 判据可计算推进
GOLDEN_RD_R3_OBL = "RD-20260301-493dab72"       # R3 反证义务推进
GOLDEN_RD_R4_HOLD = "RD-20260301-dbc4bca7"      # R4 无条件命中→hold
GOLDEN_RD_R1_RESOLVED = "RD-20260301-24e7a53c"  # R1 终态①RESOLVED
GOLDEN_RD_R1_PRIORITY = "RD-20260301-d2b07cfb"  # R1 ①优先于②④
GOLDEN_RD_R1_BLOCK = "RD-20260301-aaef6387"     # R1 终态④阻断
GOLDEN_RD_R5_BUDGET = "RD-20260301-a9974ffe"    # R5 终态③预算耗尽
GOLDEN_RD_R5_ALLFALS = "RD-20260301-cb8163f6"   # R5 终态②全证伪(优先于③)

# 矩阵 summary 定值(手工按 STAR_RULES 推导+ae 复核一致;星级门槛 5★=5项/3类/3期,
# 未解释反证封顶3★,同基底去重)
GOLDEN_SUM_H1 = {"支持数": 5, "反证数": 1, "未解释重大反证": False,
                 "机制覆盖数": 5, "star": 5}    # 已解释反证不封顶
GOLDEN_SUM_H2 = {"支持数": 4, "反证数": 1, "未解释重大反证": True,
                 "机制覆盖数": 4, "star": 3}    # 未解释反证封顶3★
GOLDEN_SUM_H3 = {"支持数": 1, "反证数": 0, "未解释重大反证": False,
                 "机制覆盖数": 1, "star": 1}    # 同基底两口径去重+中性项不计支持

# ══ 合成 fixture(唯一数据源;真实数据档永不进入) ═════════════════════════


def _fact(mid, od, value, q="PASS", metric_override=None, od_override=None):
    f = {"fact_id": f"{mid}@{od}", "metric_id": metric_override or mid,
         "observation_date": od_override or od, "value": value,
         "quality_status": q}
    return f


FIX_SNAP_B = {
    "snapshot_id": SNAP_ID_OK,
    "meta": {"synthetic": True, "fixture": "P2-WP-B golden"},
    "gate_a": {"status": "PASS", "core_missing": [], "core_fail": []},
    "facts": [
        _fact("SPX", "2026-02-13", 5900.0), _fact("SPX", "2026-02-27", 5910.0),
        _fact("TIPS_10Y", "2026-02-20", 1.62), _fact("GOLD_F", "2026-02-27", 2650.0),
        _fact("HY_OAS", "2026-02-13", 3.2), _fact("CPI_YOY", "2026-02-27", 2.8),
        _fact("BTC", "2026-02-13", 91000.0), _fact("WTI_F", "2026-02-20", 71.5, "DEGRADED"),
        _fact("VIX", "2026-02-27", 18.4), _fact("UNRATE", "2026-02-13", 4.1),
        _fact("DXY", "2026-02-27", 104.2),
        _fact("SYNTH.GOLD.value", "2026-02-13", 2655.0),
        _fact("SYNTH.GOLD.prev", "2026-02-20", 2640.0),
        _fact("CCC_OAS", "2026-02-20", 9.8),
        _fact("BROKEN", "2026-02-27", 42.0, "FAIL"),
        _fact("ODD", "2026-02-13", 7.7, metric_override="OTHER"),
        _fact("WEIRD", "2026-02-13", 5.0, od_override="2026-01-31"),
        {"fact_id": "HASHFORM#2026-02-13", "metric_id": "HASHFORM",
         "observation_date": "2026-02-13", "value": 6.6,
         "quality_status": "PASS"},   # 索引可命中但 fact_id 非{metric}@{od} 形
    ]}
FIX_SNAP_B_FAIL = {
    "snapshot_id": SNAP_ID_FAIL,
    "meta": {"synthetic": True, "fixture": "P2-WP-B gate-fail"},
    "gate_a": {"status": "FAIL", "core_missing": ["SHCOMP", "FED_FUNDS"],
               "core_fail": []},
    "facts": [_fact("SPX", "2026-02-13", 5900.0)]}

# ── 黄金任务输入(3 假设×C(3,2)=3 判据对,DP-6 全对覆盖) ──

B1S = "假设甲(证据充分): 多机制族多观察期独立证据齐备时矩阵应授5星"
B1M = "机制覆盖与观察期分离度共同决定证据充分性上限"
B2S = "假设乙(反证封顶): 存在未解释重大反证时星级封顶3星"
B2M = "未解释反证构成观点存续风险,星级上限受纪律约束"
B3S = "假设丙(同基底去重): 同一底层指标多字段口径只计一次"
B3M = "证据独立性以底层指标身份计,字段后缀不构成新证据"
B1C = {"metric_id": "SPX", "operator": ">=", "threshold": 5000.0,
       "window": {"mode": "expiry", "weeks": 4}, "premise": None,
       "threshold_source": "user_explicit", "direction": "supporting",
       "source_note": "WP-B 合成条件"}
B2C = {"metric_id": "GOLD_F", "operator": "<=", "threshold": 2700.0,
       "window": {"mode": "touch", "deadline": "2026-06-30"}, "premise": None,
       "threshold_source": "user_explicit", "direction": "falsifying",
       "source_note": "WP-B 合成条件"}
B3C = {"metric_id": "TIPS_10Y", "operator": ">=", "threshold": 1.5,
       "window": {"mode": "expiry", "weeks": 4}, "premise": None,
       "threshold_source": "user_explicit", "direction": "supporting",
       "source_note": "WP-B 合成条件"}
CRIT12 = "判据甲乙: 5星无封顶时甲成立;存在未解释反证时乙成立"
CRIT13 = "判据甲丙: 独立指标计数≥5时甲成立;字段去重后<2时丙成立"
CRIT23 = "判据乙丙: 封顶规则先于去重规则生效时乙成立"
QUESTION_B = "WP-B 黄金任务: 证据矩阵装配与轮次推进的确定性验证(合成 fixture)?"
ORIGIN_B = {"origin_query_id": "QB-20260301-002"}
BLOCK_DETAIL = "合成阻断声明: Gate A FAIL(core 缺失)"
BLOCK_FAIL = {"snapshot_id": SNAP_ID_FAIL, "detail": BLOCK_DETAIL}


def _golden_inputs():
    """黄金输入集(每用例独立深拷贝,防用例间串改)。"""
    return {"question": QUESTION_B, "origin": dict(ORIGIN_B),
            "hypotheses": [
                {"statement": B1S, "mechanism_story": B1M, "conditions": [dict(B1C)]},
                {"statement": B2S, "mechanism_story": B2M, "conditions": [dict(B2C)]},
                {"statement": B3S, "mechanism_story": B3M, "conditions": [dict(B3C)]}],
            "criteria": [{"pair": [B1S, B2S], "criterion": CRIT12},
                         {"pair": [B1S, B3S], "criterion": CRIT13},
                         {"pair": [B2S, B3S], "criterion": CRIT23}]}


def _spec(hp, mid, od, value, direction, weight, mech, note,
          explained=False, explained_note=None):
    return {"hypothesis_id": hp, "metric_id": mid, "fact_id": f"{mid}@{od}",
            "value": value, "observation_date": od, "snapshot_id": SNAP_ID_OK,
            "direction": direction, "weight": weight, "mechanism": mech,
            "explained": explained, "explained_note": explained_note, "note": note}


HP1, HP2, HP3 = GOLDEN_HP1, GOLDEN_HP2, GOLDEN_HP3
SPEC_E1 = _spec(HP1, "SPX", "2026-02-13", 5900.0, "支持", 5, "增长", "WP-B E1 合成证据")
SPEC_E2 = _spec(HP1, "TIPS_10Y", "2026-02-20", 1.62, "支持", 4, "利率与流动性", "WP-B E2 合成证据")
SPEC_E3 = _spec(HP1, "GOLD_F", "2026-02-27", 2650.0, "支持", 4, "避险与估值", "WP-B E3 合成证据")
SPEC_E4 = _spec(HP1, "HY_OAS", "2026-02-13", 3.2, "支持", 3, "信用", "WP-B E4 合成证据")
SPEC_E5 = _spec(HP1, "CPI_YOY", "2026-02-27", 2.8, "支持", 3, "通胀", "WP-B E5 合成证据")
SPEC_E14 = _spec(HP1, "CCC_OAS", "2026-02-20", 9.8, "反对", 3, "信用",
                 "WP-B E14 已解释反证", explained=True,
                 explained_note="合成已解释反证: 高收益利差走阔由再融资供给解释")
SPEC_E6 = _spec(HP2, "BTC", "2026-02-13", 91000.0, "支持", 4, "资金流", "WP-B E6 合成证据")
SPEC_E7 = _spec(HP2, "WTI_F", "2026-02-20", 71.5, "支持", 3, "供应与库存", "WP-B E7 合成证据")
SPEC_E8 = _spec(HP2, "VIX", "2026-02-27", 18.4, "支持", 3, "避险与估值", "WP-B E8 合成证据")
SPEC_E9 = _spec(HP2, "UNRATE", "2026-02-13", 4.1, "支持", 3, "增长", "WP-B E9 合成证据")
SPEC_E10 = _spec(HP2, "DXY", "2026-02-27", 104.2, "反对", 4, "资金流", "WP-B E10 未解释反证")
SPEC_E11 = _spec(HP3, "SYNTH.GOLD.value", "2026-02-13", 2655.0, "支持", 3, "避险与估值", "WP-B E11 同基底甲")
SPEC_E12 = _spec(HP3, "SYNTH.GOLD.prev", "2026-02-20", 2640.0, "支持", 3, "避险与估值", "WP-B E12 同基底乙")
SPEC_E13 = _spec(HP3, "SPX", "2026-02-27", 5910.0, "中性", 2, "增长", "WP-B E13 中性项")
ALL_SPECS = [SPEC_E1, SPEC_E2, SPEC_E3, SPEC_E4, SPEC_E5, SPEC_E14,
             SPEC_E6, SPEC_E7, SPEC_E8, SPEC_E9, SPEC_E10,
             SPEC_E11, SPEC_E12, SPEC_E13]


class _Sandbox(unittest.TestCase):
    """tempdir 沙箱: archive_dir+快照目录+双快照文件逐用例新建。"""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.td = self._td.name
        self.archive = os.path.join(self.td, "archive")
        self.snap_dir = os.path.join(self.td, "snapshots")
        os.makedirs(self.snap_dir)
        self._write_snapshot(FIX_SNAP_B)
        self._write_snapshot(FIX_SNAP_B_FAIL)

    def tearDown(self):
        self._td.cleanup()

    def _write_snapshot(self, snap):
        with open(os.path.join(self.snap_dir,
                               f"{snap['snapshot_id']}.json"), "w",
                  encoding="utf-8") as f:
            json.dump(snap, f, ensure_ascii=False)

    def register(self, inputs=None, created_at=CA):
        inputs = inputs or _golden_inputs()
        return drr.register_deep_research_task(
            inputs["question"], inputs["origin"], inputs["hypotheses"],
            inputs["criteria"], FIX_SNAP_B,
            archive_dir=self.archive, created_at=created_at)

    def register_active(self, inputs=None, created_at=CA):
        """黄金任务注册+激活(证据登记/轮次推进的常规前置态)。"""
        self.register(inputs, created_at)
        return dm.activate_task(GOLDEN_TASK_ID, archive_dir=self.archive,
                                created_at=created_at)

    def evidence_path(self, evidence_id):
        return os.path.join(self.archive, dm.ARCHIVE_FAMILY,
                            dm.COLLECTION_EVIDENCE, f"{evidence_id}.json")

    def rounds_dir(self):
        return os.path.join(self.archive, dm.ARCHIVE_FAMILY, dm.COLLECTION_ROUNDS)

    def evidence_dir(self):
        return os.path.join(self.archive, dm.ARCHIVE_FAMILY, dm.COLLECTION_EVIDENCE)

    def add_all_evidence(self, created_at=CA):
        for s in ALL_SPECS:
            dm.register_evidence(GOLDEN_TASK_ID, 1, s, self.snap_dir,
                                 archive_dir=self.archive, created_at=created_at)

    def empty_round(self, rnd):
        return {"round": rnd, "evidence": [], "criterion_judgments": [],
                "hypotheses_falsified": [], "criterion_computable": False,
                "counter_search_open": [], "data_blocking": None}


# ══ 要点外承: 黄金登记(ID 族定值+参数 echo 三方一致) ═════════════════════

class TestGoldenRegistration(_Sandbox):

    def test_golden_registration(self):
        res = self.register()
        self.assertEqual(res["status"], "written")
        self.assertEqual(res["task_id"], GOLDEN_TASK_ID)
        self.assertEqual(res["hypothesis_ids"], [GOLDEN_HP1, GOLDEN_HP2, GOLDEN_HP3])
        self.assertEqual(res["condition_ids"], [GOLDEN_FC1, GOLDEN_FC2, GOLDEN_FC3])
        self.assertEqual(res["event_id"], GOLDEN_EV_INIT)
        self.assertEqual(res["digest_snapshot"], GOLDEN_DIGEST_B)
        self.assertEqual(res["registered_params"], GOLDEN_PARAMS)
        # DP-1/2/6 登记定值=常量=echo 三方一致(常量侧独立字面量 5/[1,5]/1)
        self.assertEqual(drr.DP1_ROUND_BUDGET_DEFAULT, 5)
        self.assertEqual(drr.DP2_WEIGHT_SCALE, (1, 5))
        self.assertEqual(drr.DP6_MIN_DISCRIMINATING_PER_PAIR, 1)
        with open(os.path.join(self.archive, drr.ARCHIVE_FAMILY,
                               drr.COLLECTION_TASKS,
                               f"{GOLDEN_TASK_ID}.json"), encoding="utf-8") as f:
            rec = json.load(f)
        self.assertEqual(rec["record_type"], "deep_research_task")
        self.assertEqual(rec["status"], "DRAFT")
        self.assertEqual(rec["discriminating_criteria"], [
            {"pair": [GOLDEN_HP1, GOLDEN_HP2], "criterion": CRIT12},
            {"pair": [GOLDEN_HP1, GOLDEN_HP3], "criterion": CRIT13},
            {"pair": [GOLDEN_HP2, GOLDEN_HP3], "criterion": CRIT23}])
        self.assertEqual(rec["snapshot_id"], SNAP_ID_OK)
        self.assertEqual(rec["digest_snapshot"], GOLDEN_DIGEST_B)

    def test_activate_golden_event(self):
        """引擎激活经 drr 既有迁移表: 事件 ID 确定性+seq 单调。"""
        self.register()
        r = dm.activate_task(GOLDEN_TASK_ID, archive_dir=self.archive, created_at=CA)
        self.assertEqual(r["status"], "written")
        self.assertEqual(r["event_id"], GOLDEN_EV_ACTIVATE)
        self.assertEqual(drr.current_status(GOLDEN_TASK_ID, archive_dir=self.archive),
                         "ACTIVE")
        evs = drr.list_events(GOLDEN_TASK_ID, archive_dir=self.archive)
        self.assertEqual([e["to_status"] for e in evs], ["DRAFT", "ACTIVE"])
        self.assertEqual([e["seq"] for e in evs], [1, 2])


# ══ 要点①: 证据六重 fail-closed 接地(负向全扫) ═════════════════════════

class TestEvidenceGroundingNegative(_Sandbox):

    def setUp(self):
        super().setUp()
        self.register_active()

    def _reject(self, spec, needle):
        with self.assertRaises(ValueError) as cm:
            dm.register_evidence(GOLDEN_TASK_ID, 1, spec, self.snap_dir,
                                 archive_dir=self.archive, created_at=CA)
        self.assertIn(needle, str(cm.exception))

    def test_fact_absent_rejected(self):
        s = _spec(HP1, "SPX", "2026-03-05", 5900.0, "支持", 3, "增长", "缺席事实")
        self._reject(s, "数值无 provenance 接地")

    def test_value_mismatch_rejected(self):
        s = _spec(HP1, "SPX", "2026-02-13", 5901.0, "支持", 3, "增长", "数值错配")
        self._reject(s, "数值与快照事实不符")

    def test_observation_date_mismatch_rejected(self):
        s = _spec(HP1, "WEIRD", "2026-02-13", 5.0, "支持", 3, "增长", "日期错配")
        self._reject(s, "observation_date与快照事实不符")

    def test_metric_id_mismatch_rejected(self):
        s = _spec(HP1, "ODD", "2026-02-13", 7.7, "支持", 3, "增长", "指标错配")
        self._reject(s, "metric_id与快照事实不符")

    def test_fact_quality_fail_rejected(self):
        s = _spec(HP1, "BROKEN", "2026-02-27", 42.0, "支持", 3, "增长", "质量FAIL事实")
        self._reject(s, "事实质量'FAIL'")

    def test_gate_a_fail_snapshot_rejected(self):
        """快照可载+事实命中,但 Gate A=FAIL → 不得作正式证据源(§3.1 红线)。"""
        s = _spec(HP1, "SPX", "2026-02-13", 5900.0, "支持", 3, "增长", "FAIL 门快照")
        s["snapshot_id"] = SNAP_ID_FAIL
        self._reject(s, "Gate A")

    def test_degraded_fact_accepted(self):
        """质量词表≠FAIL 即可接地(DEGRADED 事实可用;词表面如实分档)。"""
        r = dm.register_evidence(GOLDEN_TASK_ID, 1, SPEC_E7, self.snap_dir,
                                 archive_dir=self.archive, created_at=CA)
        self.assertEqual(r["status"], "written")
        self.assertEqual(r["evidence_id"], GOLDEN_E7)

    def test_snapshot_file_missing_rejected(self):
        s = _spec(HP1, "SPX", "2026-02-13", 5900.0, "支持", 3, "增长", "缺档快照")
        s["snapshot_id"] = "research_snapshot_20260999"
        self._reject(s, "快照接地失败")

    def test_batch_atomicity_zero_partial_write(self):
        """批内任一规格接地失败 → 整批拒收,证据集合零落档。"""
        bad = _spec(HP1, "SPX", "2026-02-13", 9999.0, "支持", 3, "增长", "批内坏规格")
        with self.assertRaises(ValueError) as cm:
            dm.run_round(GOLDEN_TASK_ID,
                         {"round": 1, "evidence": [SPEC_E1, bad],
                          "criterion_judgments": [], "hypotheses_falsified": [],
                          "criterion_computable": False, "counter_search_open": [],
                          "data_blocking": None},
                         self.snap_dir, archive_dir=self.archive, created_at=CA)
        self.assertIn("证据[1]", str(cm.exception))
        self.assertFalse(os.path.exists(self.evidence_dir()),
                         "批内拒收后证据集合必须零落档")


# ══ 证据 schema 负向(P-B-02 词表面) ═════════════════════════════════════

class TestEvidenceSchemaNegative(_Sandbox):

    def setUp(self):
        super().setUp()
        self.register_active()

    def _reject(self, spec, needle):
        with self.assertRaises(ValueError) as cm:
            dm.register_evidence(GOLDEN_TASK_ID, 1, spec, self.snap_dir,
                                 archive_dir=self.archive, created_at=CA)
        self.assertIn(needle, str(cm.exception))

    def test_weight_out_of_scale(self):
        s = dict(SPEC_E1, weight=6)
        self._reject(s, "weight须为[1, 5]整数(DP-2)")

    def test_direction_off_vocab(self):
        s = dict(SPEC_E1, direction="支持性")
        self._reject(s, "direction须为支持|反对|中性")

    def test_mechanism_off_families(self):
        s = dict(SPEC_E1, mechanism="宏观")
        self._reject(s, "mechanism须为机制族7类之一")

    def test_explained_true_requires_note(self):
        s = _spec(HP1, "SPX", "2026-02-13", 5900.0, "反对", 3, "增长", "缺解释留档",
                  explained=True, explained_note=None)
        self._reject(s, "explained=True 须携非空 explained_note")

    def test_fact_id_format_enforced(self):
        """索引命中但 fact_id 非 {metric}@{od} 形 → schema 面拒收(HASHFORM 事实)。"""
        s = _spec(HP1, "HASHFORM", "2026-02-13", 6.6, "支持", 3, "增长", "fact_id 形式违规")
        s["fact_id"] = "HASHFORM#2026-02-13"
        self._reject(s, "fact_id须为{metric_id}@{observation_date}")

    def test_missing_spec_field(self):
        s = dict(SPEC_E1)
        del s["note"]
        self._reject(s, "证据规格缺字段note")


# ══ 要点①/append-only: 证据记录不可改写 ═════════════════════════════════

class TestAppendOnlyEvidence(_Sandbox):

    def setUp(self):
        super().setUp()
        self.register_active()

    def test_duplicate_evidence_rejected_bytes_unchanged(self):
        r1 = dm.register_evidence(GOLDEN_TASK_ID, 1, SPEC_E1, self.snap_dir,
                                  archive_dir=self.archive, created_at=CA)
        self.assertEqual(r1["status"], "written")
        before = hashlib.sha256(
            open(self.evidence_path(GOLDEN_E1), 'rb').read()).hexdigest()
        r2 = dm.register_evidence(GOLDEN_TASK_ID, 1, SPEC_E1, self.snap_dir,
                                  archive_dir=self.archive, created_at=CA)
        self.assertEqual(r2["status"], "rejected-duplicate")
        self.assertEqual(r2["evidence_id"], GOLDEN_E1)
        after = hashlib.sha256(
            open(self.evidence_path(GOLDEN_E1), 'rb').read()).hexdigest()
        self.assertEqual(before, after, "重复写入被拒后原档字节必须不变")

    def test_evidence_id_zero_wallclock_determinism(self):
        """指纹零墙钟: 同日不同时刻登记 → 同 ID(重放幂等锚)。"""
        id_a = dm.make_evidence_id(GOLDEN_TASK_ID, HP1, 1, SPEC_E1,
                                   "2026-03-01T01:00:00+00:00")
        id_b = dm.make_evidence_id(GOLDEN_TASK_ID, HP1, 1, SPEC_E1,
                                   "2026-03-01T23:59:59+00:00")
        self.assertEqual(id_a, id_b)
        self.assertEqual(id_a, GOLDEN_E1)


# ══ 要点②: 证据矩阵装配(summary 定值/去重/封顶/稀疏映射) ═══════════════

class TestMatrixAssembly(_Sandbox):

    def setUp(self):
        super().setUp()
        self.register_active()
        self.add_all_evidence()
        self.matrix = dm.assemble_matrix(GOLDEN_TASK_ID, archive_dir=self.archive)

    def test_summary_golden_three_hypotheses(self):
        self.assertEqual(self.matrix["summary"][HP1], GOLDEN_SUM_H1)
        self.assertEqual(self.matrix["summary"][HP2], GOLDEN_SUM_H2)
        self.assertEqual(self.matrix["summary"][HP3], GOLDEN_SUM_H3)

    def test_cells_sparse_binding_map(self):
        cells = self.matrix["cells"]
        self.assertEqual(len(cells), 14)
        self.assertEqual(cells[f"{HP1}|{GOLDEN_E1}"],
                         {"direction": "支持", "weight": 5})
        self.assertEqual(cells[f"{HP1}|{GOLDEN_E14}"],
                         {"direction": "反对", "weight": 3})
        self.assertEqual(cells[f"{HP3}|{GOLDEN_E13}"],
                         {"direction": "中性", "weight": 2})
        for key in cells:
            hp, evi = key.split("|")
            self.assertTrue(hp.startswith("HP-") and evi.startswith("EVI-"))

    def test_same_base_metric_dedup(self):
        """SYNTH.GOLD.value 与 SYNTH.GOLD.prev 同基底 → 支持数=1(ae._base_metric
        后缀剥离;同代码路径与 L520 去重同构)。"""
        self.assertEqual(self.matrix["summary"][HP3]["支持数"], 1)

    def test_neutral_excluded_from_support(self):
        """中性项不计支持(E13 SPX 为中性;若计支持则 H3 支持数=2,实得=1)。"""
        self.assertEqual(self.matrix["summary"][HP3]["支持数"], 1)
        self.assertEqual(self.matrix["summary"][HP3]["反证数"], 0)

    def test_unexplained_contrary_caps_star(self):
        """未解释重大反证封顶3★(H2 本可 4★,实得 3★)。"""
        self.assertEqual(self.matrix["summary"][HP2]["star"], 3)
        self.assertTrue(self.matrix["summary"][HP2]["未解释重大反证"])

    def test_explained_contrary_does_not_cap(self):
        """已解释反证不封顶(H1 携 1 条已解释反证仍 5★)。"""
        self.assertEqual(self.matrix["summary"][HP1]["star"], 5)
        self.assertEqual(self.matrix["summary"][HP1]["反证数"], 1)
        self.assertFalse(self.matrix["summary"][HP1]["未解释重大反证"])

    def test_empty_matrix_zero_state(self):
        """零证据任务: summary 全零+cells 空(数据不足不填0的零态面)。"""
        inputs = _golden_inputs()
        inputs["question"] = "WP-B 零态任务: 无证据时的矩阵零面(合成 fixture)?"
        reg2 = self.register(inputs)          # 异题异 id,同沙箱零证据任务
        self.assertEqual(reg2["status"], "written")
        m = dm.assemble_matrix(reg2["task_id"], archive_dir=self.archive)
        self.assertEqual(m["cells"], {})
        self.assertEqual(len(m["hypotheses"]), 3)
        self.assertEqual(len(m["evidence"]), 0)
        for summ in m["summary"].values():
            self.assertEqual(summ, {"支持数": 0, "反证数": 0,
                                    "未解释重大反证": False,
                                    "机制覆盖数": 0, "star": 0})


class TestStarIsomorphism(_Sandbox):
    """要点②「与 L520-521 同构」: 矩阵 star 与 ae.star_level_from_evidence
    对同证据集输出恒等(同一代码路径消费,非平行重写)。"""

    def test_matrix_star_equals_ae_machinery(self):
        self.register_active()
        self.add_all_evidence()
        m = dm.assemble_matrix(GOLDEN_TASK_ID, archive_dir=self.archive)
        for hp, golden_star in ((HP1, 5), (HP2, 3), (HP3, 1)):
            evs = [e for e in m["evidence"] if e["hypothesis_id"] == hp]
            v2 = [dm._to_v2_item(e) for e in evs]
            ae_star, _desc = ae.star_level_from_evidence(v2)
            self.assertEqual(ae_star, golden_star)
            self.assertEqual(m["summary"][hp]["star"], ae_star)


class TestMatrixDeterminism(_Sandbox):
    """要点②确定性: 同输入同输出(canonical 字节级相等)。"""

    def test_same_sandbox_repeat_assembly_identical(self):
        self.register_active()
        self.add_all_evidence()
        m1 = dm.assemble_matrix(GOLDEN_TASK_ID, archive_dir=self.archive)
        m2 = dm.assemble_matrix(GOLDEN_TASK_ID, archive_dir=self.archive)
        self.assertEqual(drr._canonical(m1), drr._canonical(m2))

    def test_cross_sandbox_identical_inputs_identical_matrix(self):
        self.register_active()
        self.add_all_evidence()
        m1 = dm.assemble_matrix(GOLDEN_TASK_ID, archive_dir=self.archive)
        with tempfile.TemporaryDirectory() as td2:
            arch2 = os.path.join(td2, "archive")
            snap2 = os.path.join(td2, "snapshots")
            os.makedirs(snap2)
            for snap in (FIX_SNAP_B, FIX_SNAP_B_FAIL):
                with open(os.path.join(snap2, f"{snap['snapshot_id']}.json"),
                          "w", encoding="utf-8") as f:
                    json.dump(snap, f, ensure_ascii=False)
            drr.register_deep_research_task(
                QUESTION_B, dict(ORIGIN_B),
                _golden_inputs()["hypotheses"], _golden_inputs()["criteria"],
                FIX_SNAP_B, archive_dir=arch2, created_at=CA)
            dm.activate_task(GOLDEN_TASK_ID, archive_dir=arch2, created_at=CA)
            for s in ALL_SPECS:
                dm.register_evidence(GOLDEN_TASK_ID, 1, s, snap2,
                                     archive_dir=arch2, created_at=CA)
            m2 = dm.assemble_matrix(GOLDEN_TASK_ID, archive_dir=arch2)
            self.assertEqual(drr._canonical(m1), drr._canonical(m2))


# ══ 要点③: 轮次推进条件(任一)与留守 ═════════════════════════════════════

class TestRoundAdvance(_Sandbox):

    def setUp(self):
        super().setUp()
        self.register_active()

    def test_advance_sequence_and_ids(self):
        """R1 证据推进→R2 判据可计算→R3 反证义务→R4 无命中 hold;ID/streak 定值。"""
        r1 = dm.run_round(GOLDEN_TASK_ID,
                          {"round": 1, "evidence": [SPEC_E1],
                           "criterion_judgments": [], "hypotheses_falsified": [],
                           "criterion_computable": False, "counter_search_open": [],
                           "data_blocking": None},
                          self.snap_dir, archive_dir=self.archive, created_at=CA)
        self.assertEqual(r1["status"], "written")
        self.assertEqual(r1["round_id"], GOLDEN_RD_R1_EV)
        self.assertEqual(r1["evidence_ids"], [GOLDEN_E1])
        self.assertEqual(r1["decision"]["action"], "advance")
        self.assertIn("§4.4推进①", r1["decision"]["reasons"][0])
        self.assertEqual(r1["matrix"]["summary"][HP1]["支持数"], 1)
        self.assertEqual(r1["matrix"]["evidence"][0]["evidence_id"], GOLDEN_E1)

        r2 = dm.run_round(GOLDEN_TASK_ID,
                          {"round": 2, "evidence": [], "criterion_judgments": [],
                           "hypotheses_falsified": [], "criterion_computable": True,
                           "counter_search_open": [], "data_blocking": None},
                          self.snap_dir, archive_dir=self.archive, created_at=CA)
        self.assertEqual(r2["round_id"], GOLDEN_RD_R2_COMP)
        self.assertEqual(r2["decision"]["action"], "advance")
        self.assertIn("§4.4推进②", r2["decision"]["reasons"][0])
        self.assertEqual(r2["no_new_evidence_streak"] if "no_new_evidence_streak"
                         in r2 else self._streak(r2["round_id"]), 1)

        r3 = dm.run_round(GOLDEN_TASK_ID,
                          {"round": 3, "evidence": [], "criterion_judgments": [],
                           "hypotheses_falsified": [], "criterion_computable": False,
                           "counter_search_open": [HP3], "data_blocking": None},
                          self.snap_dir, archive_dir=self.archive, created_at=CA)
        self.assertEqual(r3["round_id"], GOLDEN_RD_R3_OBL)
        self.assertEqual(r3["decision"]["action"], "advance")
        self.assertTrue(any("§4.4推进③" in x for x in r3["decision"]["reasons"]))

        r4 = dm.run_round(GOLDEN_TASK_ID, self.empty_round(4),
                          self.snap_dir, archive_dir=self.archive, created_at=CA)
        self.assertEqual(r4["round_id"], GOLDEN_RD_R4_HOLD)
        self.assertEqual(r4["decision"]["action"], "hold")
        self.assertIn("留守", r4["decision"]["reasons"][0])
        # 非终态轮不迁移生命周期;轮次记录序贯 4 条
        self.assertEqual(drr.current_status(GOLDEN_TASK_ID, archive_dir=self.archive),
                         "ACTIVE")
        self.assertEqual([x["round"] for x in
                          dm.list_rounds(GOLDEN_TASK_ID, archive_dir=self.archive)],
                         [1, 2, 3, 4])

    def _streak(self, round_id):
        with open(os.path.join(self.rounds_dir(), f"{round_id}.json"),
                  encoding="utf-8") as f:
            return json.load(f)["no_new_evidence_streak"]

    def test_hold_streak_counter(self):
        """连续无新增证据轮计数: R1 空→1,R2 空→2(留档属性,不触发终止)。"""
        dm.run_round(GOLDEN_TASK_ID, self.empty_round(1), self.snap_dir,
                     archive_dir=self.archive, created_at=CA)
        dm.run_round(GOLDEN_TASK_ID, self.empty_round(2), self.snap_dir,
                     archive_dir=self.archive, created_at=CA)
        rounds = dm.list_rounds(GOLDEN_TASK_ID, archive_dir=self.archive)
        self.assertEqual([r["no_new_evidence_streak"] for r in rounds], [1, 2])
        self.assertEqual([r["decision"]["action"] for r in rounds],
                         ["hold", "hold"])


# ══ 要点③: 终止条件四分支+枚举优先序(①→②→③→④) ═══════════════════════

class TestRoundTerminal(_Sandbox):

    def setUp(self):
        super().setUp()
        self.register_active()

    def test_resolved_on_criterion_holds(self):
        r = dm.run_round(GOLDEN_TASK_ID,
                         {"round": 1, "evidence": [],
                          "criterion_judgments": [
                              {"pair": [HP1, HP2], "criterion": CRIT12,
                               "holds": True}],
                          "hypotheses_falsified": [], "criterion_computable": False,
                          "counter_search_open": [], "data_blocking": None},
                         self.snap_dir, archive_dir=self.archive, created_at=CA)
        self.assertEqual(r["round_id"], GOLDEN_RD_R1_RESOLVED)
        self.assertEqual(r["decision"]["action"], "terminal")
        self.assertEqual(r["decision"]["terminal_status"], "RESOLVED")
        self.assertIn("§4.4①", r["decision"]["rule"])
        self.assertEqual(r["terminal_event"]["status"], "written")
        self.assertEqual(drr.current_status(GOLDEN_TASK_ID,
                                            archive_dir=self.archive), "RESOLVED")

    def test_priority_resolved_over_all_falsified_and_blocking(self):
        """①判据成立 同时携 ②全证伪+④阻断声明 → 枚举序①优先。"""
        r = dm.run_round(GOLDEN_TASK_ID,
                         {"round": 1, "evidence": [],
                          "criterion_judgments": [
                              {"pair": [HP1, HP2], "criterion": CRIT12,
                               "holds": True}],
                          "hypotheses_falsified": [HP1, HP2, HP3],
                          "criterion_computable": False, "counter_search_open": [],
                          "data_blocking": BLOCK_FAIL},
                         self.snap_dir, archive_dir=self.archive, created_at=CA)
        self.assertEqual(r["round_id"], GOLDEN_RD_R1_PRIORITY)
        self.assertEqual(r["decision"]["terminal_status"], "RESOLVED")
        self.assertIn("§4.4①", r["decision"]["rule"])

    def test_priority_all_falsified_over_budget(self):
        """R5(预算耗尽轮)同时携全证伪 → 枚举序②优先于③。"""
        for k in range(1, 5):
            dm.run_round(GOLDEN_TASK_ID, self.empty_round(k), self.snap_dir,
                         archive_dir=self.archive, created_at=CA)
        r = dm.run_round(GOLDEN_TASK_ID,
                         dict(self.empty_round(5),
                              hypotheses_falsified=[HP1, HP2, HP3]),
                         self.snap_dir, archive_dir=self.archive, created_at=CA)
        self.assertEqual(r["round_id"], GOLDEN_RD_R5_ALLFALS)
        self.assertEqual(r["decision"]["terminal_status"], "ALL_FALSIFIED")
        self.assertIn("§4.4②", r["decision"]["rule"])

    def test_partial_falsification_not_terminal(self):
        """部分证伪(1/3)不构成终态② → 无推进条件时确定性 hold。"""
        r = dm.run_round(GOLDEN_TASK_ID,
                         dict(self.empty_round(1), hypotheses_falsified=[HP1]),
                         self.snap_dir, archive_dir=self.archive, created_at=CA)
        self.assertEqual(r["decision"]["action"], "hold")
        self.assertEqual(drr.current_status(GOLDEN_TASK_ID,
                                            archive_dir=self.archive), "ACTIVE")

    def test_budget_exhaustion_inconclusive(self):
        """R1..R4 hold 后 R5 空输入 → 终态③INCONCLUSIVE(预算耗尽,DP-1 硬上界)。"""
        for k in range(1, 5):
            dm.run_round(GOLDEN_TASK_ID, self.empty_round(k), self.snap_dir,
                         archive_dir=self.archive, created_at=CA)
        r = dm.run_round(GOLDEN_TASK_ID, self.empty_round(5), self.snap_dir,
                         archive_dir=self.archive, created_at=CA)
        self.assertEqual(r["round_id"], GOLDEN_RD_R5_BUDGET)
        self.assertEqual(r["decision"]["terminal_status"], "INCONCLUSIVE")
        self.assertIn("§4.4③", r["decision"]["rule"])
        self.assertTrue(any("round=5≥预算5" in x
                            for x in r["decision"]["reasons"]))
        with open(os.path.join(self.rounds_dir(), f"{GOLDEN_RD_R5_BUDGET}.json"),
                  encoding="utf-8") as f:
            rec = json.load(f)
        self.assertEqual(rec["no_new_evidence_streak"], 5)

    def test_data_blocking_inconclusive_verified(self):
        """R1 阻断声明经引擎 gate_a 复核实证 → 终态④INCONCLUSIVE+阻断登记。"""
        r = dm.run_round(GOLDEN_TASK_ID,
                         dict(self.empty_round(1), data_blocking=BLOCK_FAIL),
                         self.snap_dir, archive_dir=self.archive, created_at=CA)
        self.assertEqual(r["round_id"], GOLDEN_RD_R1_BLOCK)
        self.assertEqual(r["decision"]["terminal_status"], "INCONCLUSIVE")
        self.assertIn("§4.4④", r["decision"]["rule"])
        self.assertEqual(r["blocking"], {
            "snapshot_id": SNAP_ID_FAIL, "claim": BLOCK_DETAIL,
            "gate_a_status": "FAIL", "core_missing": ["SHCOMP", "FED_FUNDS"],
            "core_fail": [], "verified_by": "engine_gate_a_recheck"})
        self.assertEqual(drr.current_status(GOLDEN_TASK_ID,
                                            archive_dir=self.archive),
                         "INCONCLUSIVE")

    def test_priority_budget_over_blocking(self):
        """预算耗尽轮携阻断声明 → 枚举序③优先于④。"""
        for k in range(1, 5):
            dm.run_round(GOLDEN_TASK_ID, self.empty_round(k), self.snap_dir,
                         archive_dir=self.archive, created_at=CA)
        r = dm.run_round(GOLDEN_TASK_ID,
                         dict(self.empty_round(5), data_blocking=BLOCK_FAIL),
                         self.snap_dir, archive_dir=self.archive, created_at=CA)
        self.assertEqual(r["decision"]["terminal_status"], "INCONCLUSIVE")
        self.assertIn("§4.4③", r["decision"]["rule"])


# ══ 要点③: 阻断声明复核负向(声明与快照事实不符→拒收) ═══════════════════

class TestRoundBlockingNegative(_Sandbox):

    def setUp(self):
        super().setUp()
        self.register_active()

    def test_pass_gate_claim_rejected(self):
        """放行态快照被声明为阻断 → 与事实不符,拒收(零轮次落档)。"""
        with self.assertRaises(ValueError) as cm:
            dm.run_round(GOLDEN_TASK_ID,
                         dict(self.empty_round(1),
                              data_blocking={"snapshot_id": SNAP_ID_OK,
                                             "detail": "错误声明: 数据阻断"}),
                         self.snap_dir, archive_dir=self.archive, created_at=CA)
        self.assertIn("阻断声明与事实不符", str(cm.exception))
        self.assertFalse(os.path.exists(self.rounds_dir()),
                         "阻断声明拒收后轮次记录必须零落档")

    def test_missing_snapshot_claim_rejected(self):
        with self.assertRaises(ValueError) as cm:
            dm.run_round(GOLDEN_TASK_ID,
                         dict(self.empty_round(1),
                              data_blocking={"snapshot_id": "research_snapshot_20260999",
                                             "detail": "缺档快照阻断声明"}),
                         self.snap_dir, archive_dir=self.archive, created_at=CA)
        self.assertIn("阻断声明快照不可载", str(cm.exception))


# ══ 轮次序贯 append-only(历史不可改写) ══════════════════════════════════

class TestRoundSequencing(_Sandbox):

    def setUp(self):
        super().setUp()
        self.register_active()

    def test_first_round_must_be_one(self):
        with self.assertRaises(ValueError) as cm:
            dm.run_round(GOLDEN_TASK_ID, self.empty_round(2), self.snap_dir,
                         archive_dir=self.archive, created_at=CA)
        self.assertIn("轮次须序贯", str(cm.exception))

    def test_round_over_budget_rejected(self):
        with self.assertRaises(ValueError) as cm:
            dm.run_round(GOLDEN_TASK_ID, self.empty_round(6), self.snap_dir,
                         archive_dir=self.archive, created_at=CA)
        self.assertIn("round须为[1,5]整数(DP-1 预算)", str(cm.exception))

    def test_replayed_round_rejected_sequentially(self):
        """R1 完成后重放 R1 同输入 → 序贯防线拒(历史轮不可改写,§4.4 L131)。"""
        r1 = dm.run_round(GOLDEN_TASK_ID,
                          {"round": 1, "evidence": [SPEC_E1],
                           "criterion_judgments": [], "hypotheses_falsified": [],
                           "criterion_computable": False, "counter_search_open": [],
                           "data_blocking": None},
                          self.snap_dir, archive_dir=self.archive, created_at=CA)
        self.assertEqual(r1["status"], "written")
        with self.assertRaises(ValueError) as cm:
            dm.run_round(GOLDEN_TASK_ID,
                         {"round": 1, "evidence": [SPEC_E1],
                          "criterion_judgments": [], "hypotheses_falsified": [],
                          "criterion_computable": False, "counter_search_open": [],
                          "data_blocking": None},
                         self.snap_dir, archive_dir=self.archive, created_at=CA)
        self.assertIn("轮次须序贯", str(cm.exception))
        self.assertEqual(len(os.listdir(self.rounds_dir())), 1)

    def test_history_round_record_immutable(self):
        """同 round_id 篡改内容再写 → append-only 拒,原档字节不变。"""
        dm.run_round(GOLDEN_TASK_ID,
                     {"round": 1, "evidence": [SPEC_E1], "criterion_judgments": [],
                      "hypotheses_falsified": [], "criterion_computable": False,
                      "counter_search_open": [], "data_blocking": None},
                     self.snap_dir, archive_dir=self.archive, created_at=CA)
        p = os.path.join(self.rounds_dir(), f"{GOLDEN_RD_R1_EV}.json")
        before = hashlib.sha256(open(p, 'rb').read()).hexdigest()
        tampered = json.load(open(p, encoding="utf-8"))
        tampered["no_new_evidence_streak"] = 99
        status, _ = drr._write_records([(tampered, p)], self.archive)
        self.assertEqual(status, "rejected-duplicate")
        after = hashlib.sha256(open(p, 'rb').read()).hexdigest()
        self.assertEqual(before, after)

    def test_criterion_judgment_must_anchor_registered(self):
        """判定未锚定任务档登记判据集 → 拒(判定引用面=登记面)。"""
        with self.assertRaises(ValueError) as cm:
            dm.run_round(GOLDEN_TASK_ID,
                         dict(self.empty_round(1), criterion_judgments=[
                             {"pair": [HP1, HP2], "criterion": "未登记的野判据",
                              "holds": False}]),
                         self.snap_dir, archive_dir=self.archive, created_at=CA)
        self.assertIn("未锚定任务档已登记判据集", str(cm.exception))

    def test_criterion_judgment_pair_must_hit_hypotheses(self):
        with self.assertRaises(ValueError) as cm:
            dm.run_round(GOLDEN_TASK_ID,
                         dict(self.empty_round(1), criterion_judgments=[
                             {"pair": [HP1, "HP-20260301-deadbeef"],
                              "criterion": CRIT12, "holds": False}]),
                         self.snap_dir, archive_dir=self.archive, created_at=CA)
        self.assertIn("pair成员未命中任务假设集", str(cm.exception))


# ══ 状态保护(生命周期既有机制经引擎转递) ═════════════════════════════════

class TestStateProtection(_Sandbox):

    def test_evidence_before_activation_rejected(self):
        self.register()
        with self.assertRaises(ValueError) as cm:
            dm.register_evidence(GOLDEN_TASK_ID, 1, SPEC_E1, self.snap_dir,
                                 archive_dir=self.archive, created_at=CA)
        self.assertIn("ACTIVE", str(cm.exception))

    def test_evidence_wrong_hypothesis_rejected(self):
        self.register_active()
        s = dict(SPEC_E1, hypothesis_id="HP-20260301-deadbeef")
        with self.assertRaises(ValueError) as cm:
            dm.register_evidence(GOLDEN_TASK_ID, 1, s, self.snap_dir,
                                 archive_dir=self.archive, created_at=CA)
        self.assertIn("不在任务假设集", str(cm.exception))

    def test_evidence_round_out_of_budget_rejected(self):
        self.register_active()
        with self.assertRaises(ValueError) as cm:
            dm.register_evidence(GOLDEN_TASK_ID, 6, SPEC_E1, self.snap_dir,
                                 archive_dir=self.archive, created_at=CA)
        self.assertIn("round须为[1,5]整数(DP-1 预算", str(cm.exception))

    def test_run_round_before_activation_rejected(self):
        self.register()
        with self.assertRaises(ValueError) as cm:
            dm.run_round(GOLDEN_TASK_ID, self.empty_round(1), self.snap_dir,
                         archive_dir=self.archive, created_at=CA)
        self.assertIn("ACTIVE", str(cm.exception))

    def test_run_round_after_terminal_rejected(self):
        """终态后任务非 ACTIVE → 轮次引擎拒入(生命周期既有防线)。"""
        self.register_active()
        dm.run_round(GOLDEN_TASK_ID,
                     dict(self.empty_round(1), data_blocking=BLOCK_FAIL),
                     self.snap_dir, archive_dir=self.archive, created_at=CA)
        with self.assertRaises(ValueError) as cm:
            dm.run_round(GOLDEN_TASK_ID, self.empty_round(2), self.snap_dir,
                         archive_dir=self.archive, created_at=CA)
        self.assertIn("ACTIVE", str(cm.exception))

    def test_manual_transition_after_terminal_rejected(self):
        """终态后再手工迁移 ACTIVE→RESOLVED → drr 事件溯源一致性防线拒。"""
        self.register_active()
        dm.run_round(GOLDEN_TASK_ID,
                     dict(self.empty_round(1), data_blocking=BLOCK_FAIL),
                     self.snap_dir, archive_dir=self.archive, created_at=CA)
        with self.assertRaises(ValueError) as cm:
            drr.append_lifecycle_event(GOLDEN_TASK_ID, "ACTIVE", "RESOLVED",
                                       "绕过引擎的手工迁移", archive_dir=self.archive,
                                       created_at=CA)
        self.assertIn("不一致", str(cm.exception))


# ══ 静态纯度(零原始采集档路径/零网络) ════════════════════════════════════

class TestStaticPurity(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               '..', 'scripts', 'deep_research_matrix_engine.py'),
                  encoding="utf-8") as f:
            self.src = f.read()

    def test_no_raw_collection_path(self):
        """模块零 data/daily 原始采集档路径字面引用(快照纪律 §3.1)。"""
        self.assertNotIn("data/daily", self.src)
        self.assertNotIn("daily/", self.src)

    def test_no_network_imports(self):
        tree = ast.parse(self.src)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(a.name.split('.')[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split('.')[0])
        banned = {"socket", "ssl", "urllib", "http", "requests", "ftplib",
                  "subprocess", "telnetlib", "smtplib"}
        self.assertEqual(imported & banned, set(),
                         f"零网络/进程纪律被违反: {imported & banned}")
        self.assertLessEqual(imported, {
            "json", "os", "sys", "datetime", "hashlib",
            "deep_research_registrar", "research_provenance",
            "allocation_engine", "research_archive", "snapshot_builder",
            "io", "contextlib"})

    def test_products_dir_under_research_area(self):
        """e2e 产物只落 data/research/ 运行产物区(不 commit,不触 LIVE)。"""
        self.assertEqual(dm.E2E_PRODUCTS_SUBDIR,
                         os.path.join("data", "research", "p2_wp_b_e2e"))


# ══ 要点④: e2e 离线编排(write=False 快照构建+fail-closed 全链) ══════════

class TestOfflineE2E(unittest.TestCase):
    """真实 sb 门禁+引擎 fail-closed 收束链(最小合成数据面,单通道 2 指标)。"""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.td = self._td.name
        self.data_dir = os.path.join(self.td, "daily_synth")
        os.makedirs(self.data_dir)
        glb = {"date": "20260301", "time": "07:12:00", "count": 2, "data": {
            "SPX": {"close": 5900.0, "date": "2026-02-27"},
            "VIX": {"close": 18.4, "date": "2026-02-27"}}}
        with open(os.path.join(self.data_dir, "global_20260301.json"), "w") as f:
            json.dump(glb, f)

    def tearDown(self):
        self._td.cleanup()

    def _run(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            res = dm.run_dev_copy_end_to_end(
                target_ymd="20260301", repo_root=self.td,
                data_dir=self.data_dir, trusted_root=self.data_dir,
                as_of="2026-03-01", created_at="2026-03-01T11:00:00+00:00")
        return res, buf.getvalue()

    def test_e2e_fail_closed_inconclusive(self):
        res, stdout = self._run()
        # ① 真实 sb 门禁: 单通道数据面 → Gate A FAIL(core_missing 非空)
        self.assertEqual(res["gate_a_status"], "FAIL")
        self.assertFalse(res["gate_allows"])
        self.assertTrue(res["task_id"].startswith("RT-DR-20260301-"))
        # ② 证据接地如实尝试: 事实在场但门禁 FAIL → fail-closed 拒收(零落档)
        self.assertEqual(res["evidence_attempt"]["outcome"], "rejected-fail-closed")
        ev_dir = os.path.join(self.td, dm.DEFAULT_ARCHIVE_DIR, dm.ARCHIVE_FAMILY,
                              dm.COLLECTION_EVIDENCE)
        self.assertFalse(os.path.exists(ev_dir))
        # ③ R1 阻断复核 → 终态④INCONCLUSIVE
        dec = res["round"]["decision"]
        self.assertEqual(dec["action"], "terminal")
        self.assertEqual(dec["terminal_status"], "INCONCLUSIVE")
        self.assertIn("§4.4④", dec["rule"])
        self.assertEqual(res["current_status"], "INCONCLUSIVE")
        # ④ 生命周期事件链 DRAFT→ACTIVE→INCONCLUSIVE(seq 单调)
        self.assertEqual([e["to_status"] for e in res["events"]],
                         ["DRAFT", "ACTIVE", "INCONCLUSIVE"])
        self.assertEqual([e["seq"] for e in res["events"]], [1, 2, 3])
        # ⑤ 产物落运行产物区+档案区(全部在沙箱内,零 LIVE 写入)
        products = os.path.join(self.td, "data", "research", "p2_wp_b_e2e",
                                "20260301")
        self.assertTrue(os.path.exists(
            os.path.join(products, "snapshots", "research_snapshot_20260301.json")))
        self.assertTrue(os.path.exists(os.path.join(products, "e2e_result.json")))
        self.assertTrue(res["products_dir"].startswith(self.td))
        # ⑥ 日志含不构成投资建议声明(如实纪律)
        self.assertIn("不构成投资建议", stdout)

    def test_e2e_rerun_same_sandbox_rejected(self):
        """同沙箱重放: 任务档已终态 → 激活迁移被事件溯源防线拒(append-only)。"""
        self._run()
        with self.assertRaises(ValueError):
            self._run()


if __name__ == "__main__":
    unittest.main()
