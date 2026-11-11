#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P03-FINAL-ACCEPTANCE(P0-3/Round 059)验收件: 真实链锚 + B5要点③双端闭合 + 档案round-trip。

对应合同: IA-P03-FINAL-ACCEPTANCE-SEAL-AC-v1.0 §一(E2E-B)/§三(B5要点③回补)/§六(验收件)。

结构(全部离线/零网络/零墙钟/CI可移植——仅依赖 git 内在场件: 真实注册表85+
data/daily/japan_20261105.json[B3 A2,gitignore 显式纳入];其余 data/daily 真实档
不属 CI checkout 面,其全链真实运行=scripts/p03_final_acceptance_run.py 正式驱动,
证据入 /tmp/p03-final-evidence/,不在本测试冒充):

- T1 E2E-B 真实链锚(CI可达面): 注册表基点/映射器真实注册表行为(含 B3 注册效果
  与 FD-2 现状锚)/japan 真实档锁/japan-only 沙箱→快照→R3 门禁 FAIL 拒绝(fail-closed);
- T2 B5 要点③「双端闭合版」回补(合成fixture,B5 AC-03 合成纪律;值全发明并显式
  标注,不冒充真实): 真实注册表映射+注入含日端事实的合成快照→日端绑定 RESOLVED
  +OP-1/OP-2 COMPUTED+渲染接地=双端闭合能力版(真实数据版=B3 D7 事实提取未接线
  结构性阻断,REPORT §三如实映射);
- T3 B4 档案 round-trip: executed IR append→load→digest 复算 verify 全通过。
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e2eb_query_mapper as eqm        # B1
import e2eb_query_executor as eqx      # B2
import e2eb_answer_renderer as ear     # B5
import research_archive as ra          # B4
import research_provenance as rp       # R5
import snapshot_builder as sb          # S1
import fact_engine as fe               # E1

# ══ 冻结常量(与正式驱动/REPORT 同源登记) ═════════════════════════════════
GOLDEN_QUESTION = ("美日政策利率差和10年期国债收益率差最近怎么样?"
                   "和美元兑日元走势合起来看是什么状态?")   # DESIGN §三(d) L134 逐字
CREATED_AT = "2026-11-05T20:45:00+08:00"
REAL_JAPAN_FILE = os.path.join(ROOT, "data", "daily", "japan_20261105.json")
REAL_JAPAN_SHA256 = ("6bba4718759ba12546499c1bdc510a1157b87f9462408e14071967d2"
                     "9e14e7f1")       # B3 A2 冻结全值

# B3 D12 实测锚定值(japan 真实档)
ANCHOR_JGB = {"JGB2Y": 1.891, "JGB5Y": 2.269, "JGB10Y": 2.855}
ANCHOR_POLICY = 1.043
ANCHOR_JGB_OBS = "2026-11-04"
ANCHOR_POLICY_OBS = "2026-09-01"

# T2 合成值(全发明,显式标注;B3 §零.7 fixture 值域先例 JP 0.100/0.500)
# MW-V1(2026-11-08): MB-9 计分制修复后概念"JGB 10Y"绑 JGB10Y(旧=JGB2Y 首命中
# 误映射),合成装置补 JGB10Y 事实使双端闭合按正确期限计算。
SYN = {"DFEDTARL": 3.9, "DFEDTARU": 4.1, "DFF": 4.0, "UST_2Y": 4.5,
       "UST_10Y": 4.8, "CURVE_2S10S": 0.3, "USDJPY": 150.0,
       "JP_POLICY_RATE": 0.1, "JGB2Y": 0.5, "JGB10Y": 1.2}
SYN_OBS_US = "2026-11-02"
SYN_OBS_JP = "2026-11-04"
SNAP_ID_SYN = "research_snapshot_20261102"
# OP 预期(执行器 D-B2-09: result=v[0]−mean(v[1:]),round4)
OP1_EXPECTED = round(SYN["JP_POLICY_RATE"] - (SYN["DFEDTARL"] + SYN["DFEDTARU"]) / 2, 4)
OP2_EXPECTED = round(SYN["JGB10Y"] - SYN["UST_10Y"], 4)
OP3_EXPECTED = round(SYN["UST_10Y"] - SYN["UST_2Y"], 4)


def _sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def hfact(mid, value, obs, src, quality="PASS", derived=None, calc_ref=None):
    """手工事实(SYNTHETIC,值全发明;仅携带执行器/渲染器消费字段)。"""
    return {"metric_id": mid, "fact_id": f"{mid}@{obs}", "value": value,
            "observation_date": obs, "quality_status": quality,
            "source": {"collector": "synthetic", "file": src},
            "derived": derived, "calculation_ref": calc_ref}


def synthetic_closed_snapshot():
    """要点③双端闭合合成快照: 美端7指标+日端2指标(注册表真实身份,值全发明)。"""
    facts = [
        hfact("DFEDTARL", SYN["DFEDTARL"], SYN_OBS_US, "rate_economy_20261102.json"),
        hfact("DFEDTARU", SYN["DFEDTARU"], SYN_OBS_US, "rate_economy_20261102.json"),
        hfact("DFF", SYN["DFF"], SYN_OBS_US, "rate_economy_20261102.json"),
        hfact("UST_2Y", SYN["UST_2Y"], SYN_OBS_US, "macro_20261102.json"),
        hfact("UST_10Y", SYN["UST_10Y"], SYN_OBS_US, "macro_20261102.json",
              calc_ref="合成fixture:MOF/BLS口径外发明值,非真实观测"),
        hfact("CURVE_2S10S", SYN["CURVE_2S10S"], SYN_OBS_US, "macro_20261102.json"),
        hfact("USDJPY", SYN["USDJPY"], SYN_OBS_US, "global_20261102.json",
              derived={"week": {"available": True, "pct_change": 0.5,
                                "basis_date": "2026-10-27"},
                       "ytd": {"available": True, "pct_change": 2.0,
                               "basis_date": "2025-12-31"}}),
        # ── 日端(B3 注册身份;合成值=要点③能力版闭合,真实数据版见 REPORT FD-1)──
        hfact("JP_POLICY_RATE", SYN["JP_POLICY_RATE"], SYN_OBS_JP,
              "japan_20261102.json", calc_ref="合成fixture:发明值,非真实观测"),
        hfact("JGB2Y", SYN["JGB2Y"], SYN_OBS_JP, "japan_20261102.json",
              calc_ref="合成fixture:发明值,非真实观测"),
        hfact("JGB10Y", SYN["JGB10Y"], SYN_OBS_JP, "japan_20261102.json",
              calc_ref="合成fixture:发明值,非真实观测"),
    ]
    return {"snapshot_id": SNAP_ID_SYN,
            "research_as_of": "2026-11-02T12:00:00+08:00", "target_date": "20261102",
            "sources_status": {ch: {"status": "EXACT", "file": f"{ch}_20261102.json"}
                               for ch in ("global", "macro", "china", "rate_economy",
                                          "japan")},
            "facts": facts, "gate_a": {"status": "PASS"}}


def run_closed_chain():
    """双端闭合全链: B1(真实注册表)→B2(注入合成快照)→B5。"""
    ir = eqm.map_question(GOLDEN_QUESTION, created_at=CREATED_AT, as_of="2026-11-02")
    execution = eqx.execute_query(ir, snapshot=synthetic_closed_snapshot())
    answer = ear.render_answer(execution)
    return ir, execution, answer


# ══ T1 E2E-B 真实链锚(CI 可达面) ═══════════════════════════════════════
class TestT1RealChainAnchors(unittest.TestCase):
    """真实注册表+真实 japan 档(CI checkout 在场件)上的确定性锚。"""

    def test_t11_registry_basepoint_102_v230(self):
        """IA-P1-WP-A v1.3 域化: 85→94(85+9)/v2.1.0→v2.2.0/active 84→93;
        IA-P1-WP-E v1.3 域化(§十三.1 从属锁迁移): 94→102(94+8)/v2.2.0→v2.3.0/active 93→101。"""
        reg = fe.load_registry()
        metrics = reg["metrics"]
        self.assertEqual(len(metrics), 110)  # 数据批1: +SPX_EPS/M2SL(前 Charter7 P2-3 +SOFR/WALCL)
        self.assertEqual(reg["version"], "2.8.2")  # R6-D1(2026-11-11) CPI/PPI 换源;数据批1曾 2.7.0→2.8.0
        self.assertEqual(sum(1 for m in metrics if m.get("status") == "active"), 108)  # 数据批1 +SPX_EPS/M2SL

    def test_t12_mapper_real_registry_golden_question(self):
        """B3 注册效果锚: MB-8 由 ABSENT_REGISTRY(B5 时代 81 注册表)转为注册表命中
        JP_POLICY_RATE;MB-9=MW-V1(2026-11-08)计分制修复后绑定期限正确的
        JGB10Y(旧=JGB2Y 首命中误映射,FD-2 已闭合)。"""
        ir = eqm.map_question(GOLDEN_QUESTION, created_at=CREATED_AT,
                              as_of="2026-11-05")
        by_bid = {b["binding_id"]: b for b in ir["metric_bindings"]}
        self.assertEqual(len(ir["metric_bindings"]), 11)
        self.assertEqual(by_bid["MB-8"]["metric_id"], "JP_POLICY_RATE")
        self.assertEqual(by_bid["MB-8"]["status"], "PENDING_EXECUTION")
        self.assertIsNone(by_bid["MB-8"]["absence_reason"])   # 非ABSENT_REGISTRY
        self.assertEqual(by_bid["MB-9"]["metric_id"], "JGB10Y")  # MW-V1 期限修复锚
        self.assertEqual([op["op_id"] for op in ir["derived_operations"]],
                         ["OP-1", "OP-2", "OP-3"])
        self.assertTrue(all(op["status"] == "PENDING_EXECUTION"
                            for op in ir["derived_operations"]))
        self.assertEqual(ir["unresolved_entities"], [])

    def test_t13_real_japan_file_lock(self):
        """B3 A2 真实采集档全值锁(sha256+D12 锚定值;=E2E-B 真实任务的数据在场件)。"""
        with open(REAL_JAPAN_FILE, encoding="utf-8") as f:
            real = json.load(f)
        self.assertEqual(real["date"], "20261105")
        self.assertEqual(real["data"], dict(ANCHOR_JGB, JP_POLICY_RATE=ANCHOR_POLICY))
        self.assertEqual(real["observations"],
                         {"JGB2Y": ANCHOR_JGB_OBS, "JGB5Y": ANCHOR_JGB_OBS,
                          "JGB10Y": ANCHOR_JGB_OBS,
                          "JP_POLICY_RATE": ANCHOR_POLICY_OBS})
        self.assertEqual(_sha256_file(REAL_JAPAN_FILE), REAL_JAPAN_SHA256)

    def test_t14_japan_only_sandbox_gate_fail_refusal(self):
        """CI-checkout 形态(japan 档独在场): 生产 S1→快照(japan EXACT+sha256 全值,
        基线四通道 MISSING,gate FAIL)→R3 门禁不放行→执行器结构化拒绝零部分执行。"""
        with tempfile.TemporaryDirectory() as td:
            shutil.copy2(REAL_JAPAN_FILE, td)
            snap = sb.build_snapshot(target_ymd="20261105", data_dir=td,
                                     out_dir=td, trusted_root=td)
            st = snap["sources_status"]
            self.assertEqual(st["japan"]["status"], "EXACT")
            self.assertEqual(st["japan"]["sha256"], REAL_JAPAN_SHA256)
            for ch in rp.SOURCE_CHANNELS:
                self.assertEqual(st[ch]["status"], "MISSING", ch)
            self.assertEqual(snap["gate_a"]["status"], "FAIL")
            ir = eqm.map_question(GOLDEN_QUESTION, created_at=CREATED_AT,
                                  as_of="2026-11-05")
            execution = eqx.execute_query(ir, daily_dir=td)   # R1 自取持久快照
            self.assertIsNotNone(execution.get("refusal"))
            self.assertEqual(execution["values"], {})
            self.assertIn("不放行正式研究查询", execution["refusal"])


# ══ T2 B5 要点③ 双端闭合(合成能力版;真实数据版=FD-1 结构性阻断如实登记) ══
class TestT2DualEndedClosure(unittest.TestCase):
    """B5 REPORT §四③「升级版待 B3 落定,由后续轮承接」承接件。

    B3 已落定(注册表 85+真实档),日端注册表命中面=真实(真实注册表驱动);
    日端**事实**面=合成(值全发明;真实 japan 事实提取=B3 D7 未接线,白名单外,
    REPORT §四 FD-1 登记,修复属后续接线轮)。本组=要点③「测试+新数据档」工件中
    「测试」件的能力闭合证明。"""

    @classmethod
    def setUpClass(cls):
        cls.ir, cls.execution, cls.answer = run_closed_chain()

    def test_t21_jp_bindings_resolved_with_provenance(self):
        by_bid = {b["binding_id"]: b for b in self.execution["ir"]["metric_bindings"]}
        for bid, mid in (("MB-8", "JP_POLICY_RATE"), ("MB-9", "JGB10Y")):
            b = by_bid[bid]
            self.assertEqual(b["metric_id"], mid)
            self.assertEqual(b["status"], "RESOLVED", bid)
            self.assertEqual(b["provenance"]["observation_date"], SYN_OBS_JP)
            self.assertEqual(b["provenance"]["snapshot_id"], SNAP_ID_SYN)
            self.assertEqual(self.execution["values"][bid], SYN[mid])

    def test_t22_spread_ops_computed_dual_ended(self):
        by_op = {op["op_id"]: op for op in self.execution["ir"]["derived_operations"]}
        self.assertEqual(by_op["OP-1"]["status"], "COMPUTED")
        self.assertEqual(by_op["OP-1"]["result"], OP1_EXPECTED)   # 日端−美端中值
        self.assertEqual(by_op["OP-2"]["status"], "COMPUTED")
        self.assertEqual(by_op["OP-2"]["result"], OP2_EXPECTED)
        self.assertEqual(by_op["OP-3"]["result"], OP3_EXPECTED)
        self.assertIn("观测日不一致", by_op["OP-1"]["calculation_ref"])  # 期限不匹配如实披露

    def test_t23_renderer_grounds_both_ends(self):
        self.assertEqual(self.answer["kind"], "grounded")
        self.assertEqual(self.answer["absent"], [])
        self.assertEqual(self.answer["no_data"], [])
        self.assertEqual(self.answer["n_grounded_values"], 11)
        text = self.answer["answer_text"]
        self.assertIn("MB-8 JP_POLICY_RATE = 0.1", text)
        self.assertIn("MB-9 JGB10Y = 1.2", text)
        self.assertIn(f"OP-1", text)
        self.assertIn(f"= {OP1_EXPECTED}", text)
        self.assertIn("无数据0项/不可计算0项", text)

    def test_t24_determinism_double_run(self):
        _, ex2, ans2 = run_closed_chain()
        self.assertEqual(ex2["values"], self.execution["values"])
        self.assertEqual(ans2["answer_text"], self.answer["answer_text"])


# ══ T3 B4 档案 round-trip(双端闭合链产物 append→load→verify) ═══════════
class TestT3ArchiveRoundTrip(unittest.TestCase):
    def test_t31_append_load_verify(self):
        ir = eqm.map_question(GOLDEN_QUESTION, created_at=CREATED_AT,
                              as_of="2026-11-02")
        snap = synthetic_closed_snapshot()
        execution = eqx.execute_query(ir, snapshot=snap)
        with tempfile.TemporaryDirectory() as td:
            sdir = os.path.join(td, "snapdir")
            os.makedirs(sdir)
            with open(os.path.join(sdir, f"{SNAP_ID_SYN}.json"), "w",
                      encoding="utf-8") as f:
                json.dump(snap, f, ensure_ascii=False)
            st, path = ra.append_query_record(execution["ir"], snapshot=snap,
                                              archive_dir=td, execution=execution,
                                              archived_at="2026-11-05T12:46:00+00:00")
            self.assertEqual(st, ra.STATUS_WRITTEN)
            rec = ra.load_query_record(execution["ir"]["query_id"], archive_dir=td)
            self.assertEqual(rec["ir_stage"], "executed")
            self.assertEqual(rec["digest_snapshot"],
                             rp.digest_snapshot(snap))
            ok, issues = ra.verify_query_record(rec, sdir, archive_dir=td)
            self.assertTrue(ok, issues)


if __name__ == "__main__":
    unittest.main(verbosity=2)
