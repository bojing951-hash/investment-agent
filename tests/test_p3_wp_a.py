#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P3-WP-A 测试套件: 档案检索与结论版本管理

DESIGN §7 WP-P3-A 行(L170-L174)验收要点逐条离线覆盖:
①索引输入限门禁后正式产物(§3.1),索引直读原始 data/daily 负向——
  TestSnapshotIndexing(结构性不可达采集件)/TestStaticPurity(零 data/daily 字面);
②可重建性逐字节一致——TestIndexDeterminism(write→删→重建→逐字节一致+
  黄金 sha256 字面量)/TestIndexFileFace(损坏→fail-loud→重建);
③版本记录 append-only 负向+DP-1/2/3 禁回改负向——TestVersionAppendOnly/
  TestVersionValidationNegative/TestDPRegistration(回改→哨兵 AssertionError);
④修正提案走既有门禁断言(不设弱门禁旁路)——TestReviseConclusion+
  TestVersionValidationNegative(trigger 缺 id/证据<2 项一律拒);
⑤CI 零回归——套件自身 exit 0(本地 CI 镜像逐套件循环)。

纪律: 零网络;全合成 fixture=唯一数据源(测试不触 data/daily 与 config 真实档,
快照/报告/状态档全部沙箱内合成);预期值字面量硬编码(GOLDEN 表,独立预计算
固化,禁运行期从被测模块导入计算);created_at 全显式定值零墙钟。
黄金值独立复算登记: 测试内 hashlib 首原理复算(TestGoldenFirstPrinciples),
与 GOLDEN 字面量逐值相等(双源一致);fixture 定义与预计算脚本
(/tmp/p3a-golden-precompute.py,证据包 03 成员)逐字节一致。
"""
import ast
import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))

import research_index as ri                       # 被测模块
import deep_research_registrar as drr             # 上游(仅读常量/写入原语对照)

MODULE_SOURCE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  '..', 'scripts', 'research_index.py')

# ══ 黄金字面量表(独立预计算固化;禁运行期重算/禁从被测模块导入计算) ══════

GOLDEN = {
    "DIGEST_SNAP_OK": "e9175d739811d01b",          # SNAP_OK 内容指纹(sha256[:16])
    "DIGEST_SNAP_OK_V2": "738603f6b9488a44",       # 当日修订版 v2(权威选择)
    "DIGEST_SNAP_DEGRADED": "78dafefbd66f3fbc",    # DEGRADED 放行日
    "DIGEST_SNAP_FAIL": "61d1f46f212ede53",        # FAIL 日(不入索引)
    "MD_A_DIGEST": "948efa38ebd5fc67",             # 周报 A 文件字节指纹
    "MD_B_DIGEST": "156e92c5bad4a9ce",             # 周报 B(DEGRADED 放行)
    "INDEX_SMALL_SHA256": ("9c2382a1b7aa6b715183337b0fda1576"
                           "6608e215cd96e55858b674ae7d2ac14d"),
}

# ══ 合成 fixture(唯一数据源;与黄金预计算脚本逐字节一致) ═════════════════

SNAP_OK = {
    "snapshot_id": "research_snapshot_20261110", "as_of": "2026-11-10",
    "target_date": "20261110", "gate_a": {"status": "PASS"},
    "facts": [
        {"fact_id": "TEST.CPI.SYN@2026-11-03", "metric_id": "TEST.CPI.SYN",
         "observation_date": "2026-11-03", "value": 3.2, "quality_status": "OK"},
        {"fact_id": "TEST.NFP.SYN@2026-11-05", "metric_id": "TEST.NFP.SYN",
         "observation_date": "2026-11-05", "value": 150.0, "quality_status": "OK"},
    ],
}
SNAP_OK_V2 = {
    "snapshot_id": "research_snapshot_20261110_v2", "as_of": "2026-11-10",
    "target_date": "20261110", "gate_a": {"status": "PASS"},
    "facts": SNAP_OK["facts"] + [
        {"fact_id": "TEST.GOLD.SYN@2026-11-06", "metric_id": "TEST.GOLD.SYN",
         "observation_date": "2026-11-06", "value": 1.0, "quality_status": "OK"},
    ],
}
SNAP_DEGRADED = {
    "snapshot_id": "research_snapshot_20261111", "as_of": "2026-11-11",
    "target_date": "20261111", "gate_a": {"status": "DEGRADED"},
    "facts": [
        {"fact_id": "TEST.CPI.SYN@2026-11-10", "metric_id": "TEST.CPI.SYN",
         "observation_date": "2026-11-10", "value": 3.3, "quality_status": "OK"},
    ],
}
SNAP_FAIL = {
    "snapshot_id": "research_snapshot_20261112", "as_of": "2026-11-12",
    "target_date": "20261112", "gate_a": {"status": "FAIL"}, "facts": [],
}

MD_A_BYTES = ("# 合成正式周报 A(IA-P3-WP-A 测试 fixture)\n\n"
              "- 事实引用: TEST.CPI.SYN\n").encode("utf-8")
MD_B_BYTES = ("# 合成正式周报 B(降级放行 fixture)\n\n"
              "- 事实引用: TEST.GOLD.SYN\n").encode("utf-8")

THESIS_DOC = {
    "last_updated": "2026-11-05",
    "theses": [
        {"id": "T01", "name": "合成论点一(通胀粘性)", "status": "进行中",
         "confidence": 0.6,
         "quant_triggers": [{"metric": "TEST.CPI.SYN"}, {"metric": "TEST.NFP.SYN"}]},
        {"id": "T02", "name": "合成论点二(无触发器)", "status": "已验证",
         "confidence": 0.8, "quant_triggers": []},
    ],
}
VIEWS_DOC = {
    "last_updated": "2026-11-06",
    "ratings_scale": [{"rating": "超配"}, {"rating": "标配"}, {"rating": "低配"},
                      {"rating": "观望"}],
    "views": [
        {"id": "V01", "asset": "US_EQ", "rating": "超配",
         "quant_triggers": [{"metric": "TEST.CPI.SYN"}]},
    ],
    "predictions": [
        {"pred_id": "P01", "date_made": "2026-11-01", "asset": "US_EQ",
         "status": "not_yet_triggered", "metric": "TEST.CPI.SYN",
         "deadline": "2026-12-31"},
    ],
}

CHANGES_STATUS = [{"field": "status", "before": "进行中", "after": "待观察"}]
CHANGES_RATING = [{"field": "rating", "before": "超配", "after": "标配"}]
GATE_TRIG = {"kind": "trigger", "trigger_id": "TRG-SYN-1"}
GATE_EV2 = {"kind": "program_evidence", "evidence_refs": ["EV-SYN-A", "EV-SYN-B"]}

# 查询 API 专用小索引(直接构造条目,非黄金断言面)
def _qentries():
    return [
        ri._mk_entry("thesis", "THESIS-T01", date="2026-11-05", status="进行中",
                     metric_ids=["TEST.CPI.SYN", "TEST.NFP.SYN"]),
        ri._mk_entry("view", "VIEW-V01", date="2026-11-06", status="超配",
                     metric_ids=["TEST.CPI.SYN"], assets=["US_EQ"]),
        ri._mk_entry("snapshot", "research_snapshot_20261110_v2", date="2026-11-10",
                     metric_ids=["TEST.CPI.SYN"], obs_min="2026-11-03",
                     obs_max="2026-11-06", snapshot_id="research_snapshot_20261110_v2",
                     digest=GOLDEN["DIGEST_SNAP_OK_V2"]),
        ri._mk_entry("conclusion_version", "VER-20261115-001", date="2026-11-15",
                     status="status_change"),
        ri._mk_entry("formal_report", "weekly_report_20261107", date="2026-11-07"),
        ri._mk_entry("snapshot", "research_snapshot_20261111", date="2026-11-11",
                     metric_ids=["TEST.CPI.SYN"], obs_min="2026-11-10",
                     obs_max="2026-11-10", snapshot_id="research_snapshot_20261111",
                     digest=GOLDEN["DIGEST_SNAP_DEGRADED"]),
    ]


def _qindex():
    return {"schema_version": 1, "note": ri.DISCLAIMER_NOTE, "entries": _qentries()}


# ══ 沙箱基件 ═════════════════════════════════════════════════════════════

class SandboxBase(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="p3a-sandbox-")
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def _w(self, rel, data):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        return path

    def _wjson(self, rel, obj):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, sort_keys=True, indent=1)
        return path

    def write_snapshot(self, snap, subdir="snapshots"):
        return self._wjson(os.path.join(subdir, snap["snapshot_id"] + ".json"), snap)

    def write_formal_report(self, subdir, ymd, md_bytes, *, with_status=True,
                            published=True, final_quality="PASS",
                            report_digest=None):
        d = os.path.join(self.root, subdir)
        os.makedirs(d, exist_ok=True)
        fname = f"weekly_report_{ymd}.md"
        md_path = os.path.join(d, fname)
        with open(md_path, "wb") as f:
            f.write(md_bytes)
        if with_status:
            st = {"published": published, "final_quality": final_quality,
                  "report_file": fname, "target_date": ymd,
                  "report_path": md_path,
                  "report_digest": report_digest
                  if report_digest is not None
                  else hashlib.sha256(md_bytes).hexdigest()[:16]}
            with open(os.path.join(d, f"report_status_{ymd}.json"), "w",
                      encoding="utf-8") as f:
                json.dump(st, f, ensure_ascii=False, sort_keys=True, indent=1)
        return md_path

    _UNSET = object()   # 显式 None 负向入参不被默认值吞没的哨兵

    def record(self, *, archive="archive", snapshot_dir="snapshots",
               object_type="thesis", object_id="THESIS-T01",
               change_type="status_change", changes=_UNSET,
               gate_basis=_UNSET, snapshot=_UNSET,
               created_at="2026-11-15T09:00:00"):
        return ri.record_conclusion_version(
            object_type, object_id, change_type,
            changes if changes is not self._UNSET else CHANGES_STATUS,
            gate_basis if gate_basis is not self._UNSET else copy.deepcopy(GATE_TRIG),
            snapshot if snapshot is not self._UNSET
            else {"snapshot_id": SNAP_OK_V2["snapshot_id"]},
            snapshot_dir=os.path.join(self.root, snapshot_dir),
            archive_dir=os.path.join(self.root, archive),
            created_at=created_at)


# ══ 黄金字面量×首原理复算(双源一致) ═════════════════════════════════════

class TestGoldenFirstPrinciples(unittest.TestCase):
    """测试内 hashlib 首原理复算 == GOLDEN 字面量(禁调用被测模块计算)。"""

    def test_snapshot_digests_recompute(self):
        for snap, key in [(SNAP_OK, "DIGEST_SNAP_OK"),
                          (SNAP_OK_V2, "DIGEST_SNAP_OK_V2"),
                          (SNAP_DEGRADED, "DIGEST_SNAP_DEGRADED"),
                          (SNAP_FAIL, "DIGEST_SNAP_FAIL")]:
            blob = json.dumps(snap, ensure_ascii=False, sort_keys=True)
            self.assertEqual(hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16],
                             GOLDEN[key], key)

    def test_report_digest_recompute(self):
        for md, key in [(MD_A_BYTES, "MD_A_DIGEST"), (MD_B_BYTES, "MD_B_DIGEST")]:
            self.assertEqual(hashlib.sha256(md).hexdigest()[:16], GOLDEN[key], key)

    def test_index_small_sha_recompute(self):
        entry = {"kind": "thesis", "ref": "THESIS-T01", "date": "2026-11-05",
                 "status": "进行中",
                 "metric_ids": ["TEST.CPI.SYN", "TEST.NFP.SYN"],
                 "assets": None, "mechanisms": None, "obs_min": None,
                 "obs_max": None, "snapshot_id": None, "digest": None}
        doc = {"schema_version": 1, "note": ri.DISCLAIMER_NOTE,
               "entries": [entry]}   # 单条目已有序;note=被测模块登记值(输入面)
        blob = json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=1)
        self.assertEqual(hashlib.sha256(blob.encode("utf-8")).hexdigest(),
                         GOLDEN["INDEX_SMALL_SHA256"])


# ══ DP 登记定值锚定(要点③ 禁回改;REPORT §零.4) ═════════════════════════

class TestDPRegistration(unittest.TestCase):
    def test_registered_values_anchor(self):
        self.assertEqual(ri.registered_dp_values(), {
            "DP-1": "bypass_file_incremental",
            "DP-2": "O1_O2_O3_O4_full_four",
            "DP-3": "record_level",
        })

    def test_dp_selfcheck_ok(self):
        self.assertTrue(ri.dp_selfcheck())

    def test_dp_regression_detected(self):
        with patch.object(ri, "DP1_INDEX_FORM", "retrofitted_inplace"):
            with self.assertRaises(AssertionError):
                ri.dp_selfcheck()
        with patch.object(ri, "INDEXED_KINDS",
                          ("conclusion_version", "formal_report")):
            with self.assertRaises(AssertionError):
                ri.dp_selfcheck()
        self.assertTrue(ri.dp_selfcheck())   # 恢复后哨兵复绿

    def test_vocab_partition(self):
        self.assertEqual(sorted(ri.REF_KINDS),
                         sorted(ri.INDEXED_KINDS + ri.RESERVED_KINDS))
        self.assertNotIn("deep_research_task", ri.INDEXED_KINDS)
        self.assertEqual(len(ri.INDEXED_KINDS), 6)   # DP-2(a): 第一期恰 6 kind


# ══ 条目 schema(11 键;null 如实缺席) ════════════════════════════════════

class TestEntrySchema(unittest.TestCase):
    def test_eleven_keys_exact(self):
        e = ri._mk_entry("thesis", "THESIS-X", date="2026-11-01")
        self.assertEqual(set(e.keys()), {
            "kind", "ref", "date", "status", "metric_ids", "assets",
            "mechanisms", "obs_min", "obs_max", "snapshot_id", "digest"})

    def test_honest_null_absence(self):
        e = ri._mk_entry("formal_report", "weekly_report_20261107",
                         date="2026-11-07")
        for k in ("status", "metric_ids", "assets", "mechanisms",
                  "obs_min", "obs_max", "snapshot_id", "digest"):
            self.assertIsNone(e[k], k)

    def test_list_normalization(self):
        e = ri._mk_entry("thesis", "THESIS-X", date=None,
                         metric_ids=["b.m", "a.m", "b.m"], assets=["Z", "A", "Z"])
        self.assertEqual(e["metric_ids"], ["a.m", "b.m"])
        self.assertEqual(e["assets"], ["A", "Z"])

    def test_reserved_and_unknown_kind_rejected(self):
        with self.assertRaises(ValueError):
            ri._mk_entry("deep_research_task", "RD-X", date=None)
        with self.assertRaises(ValueError):
            ri._mk_entry("nonsense_kind", "X", date=None)

    def test_bad_ref_and_date_rejected(self):
        with self.assertRaises(ValueError):
            ri._mk_entry("thesis", "", date=None)
        with self.assertRaises(ValueError):
            ri._mk_entry("thesis", "THESIS-X", date="2026/11/01")
        with self.assertRaises(ValueError):
            ri._mk_entry("thesis", "THESIS-X", date="2026-13-01")

    def test_inverted_obs_range_rejected(self):
        with self.assertRaises(ValueError):
            ri._mk_entry("snapshot", "research_snapshot_20261110_v2",
                         date="2026-11-10", obs_min="2026-11-06",
                         obs_max="2026-11-03")


# ══ 索引源①: 快照(严格 glob;结构性不可达原始采集档) ═══════════════════

class TestSnapshotIndexing(SandboxBase):
    def test_golden_v2_selected_and_entry_shape(self):
        d = os.path.join(self.root, "snapshots")
        self.write_snapshot(SNAP_OK)
        self.write_snapshot(SNAP_OK_V2)
        entries, excluded = ri.index_snapshots(d)
        self.assertEqual(excluded, [])
        self.assertEqual(len(entries), 1)
        e = entries[0]
        self.assertEqual((e["kind"], e["ref"]),
                         ("snapshot", "research_snapshot_20261110_v2"))
        self.assertEqual(e["date"], "2026-11-10")
        self.assertEqual(e["metric_ids"],
                         ["TEST.CPI.SYN", "TEST.GOLD.SYN", "TEST.NFP.SYN"])
        self.assertEqual((e["obs_min"], e["obs_max"]),
                         ("2026-11-03", "2026-11-06"))
        self.assertEqual(e["digest"], GOLDEN["DIGEST_SNAP_OK_V2"])
        self.assertNotEqual(e["digest"], GOLDEN["DIGEST_SNAP_OK"])  # 选 v2 非 base

    def test_degraded_admitted(self):
        d = os.path.join(self.root, "snapshots")
        self.write_snapshot(SNAP_DEGRADED)
        entries, excluded = ri.index_snapshots(d)
        self.assertEqual(excluded, [])
        self.assertEqual(entries[0]["digest"], GOLDEN["DIGEST_SNAP_DEGRADED"])

    def test_gate_fail_excluded_honestly(self):
        d = os.path.join(self.root, "snapshots")
        self.write_snapshot(SNAP_FAIL)
        entries, excluded = ri.index_snapshots(d)
        self.assertEqual(entries, [])                       # 不填冒充值
        self.assertEqual(len(excluded), 1)
        self.assertEqual(excluded[0]["ymd"], "20261112")
        self.assertIn("Gate A", excluded[0]["reason"])

    def test_mixed_day_admission_split(self):
        d = os.path.join(self.root, "snapshots")
        for s in (SNAP_OK, SNAP_OK_V2, SNAP_DEGRADED, SNAP_FAIL):
            self.write_snapshot(s)
        entries, excluded = ri.index_snapshots(d)
        self.assertEqual(len(entries), 2)                   # 11-10(v2)+11-11
        self.assertEqual(len(excluded), 1)                  # 11-12 FAIL
        self.assertEqual({e["ref"] for e in entries},
                         {"research_snapshot_20261110_v2",
                          "research_snapshot_20261111"})

    def test_raw_collection_files_unreachable(self):
        # china_/global_/macro_/rate_economy_ 等采集件与严格 glob 零匹配零读取
        raw = {name: b'{"raw": 1}' for name in (
            "china_cpi_20261110.json", "global_macro_20261110.json",
            "macro_rates_20261110.json", "rate_economy_20261110.json",
            "japan_market_20261110.json")}
        d = os.path.join(self.root, "rawdir")
        os.makedirs(d)
        for name, blob in raw.items():
            with open(os.path.join(d, name), "wb") as f:
                f.write(blob)
        self.assertEqual(ri._snapshot_ymds(d), set())
        entries, excluded = ri.index_snapshots(d)
        self.assertEqual((entries, excluded), ([], []))
        for name, blob in raw.items():                      # 零改写
            with open(os.path.join(d, name), "rb") as f:
                self.assertEqual(f.read(), blob, name)

    def test_mixed_raw_and_snapshot_discovery(self):
        d = os.path.join(self.root, "mixed")
        os.makedirs(d)
        with open(os.path.join(d, "china_cpi_20261110.json"), "wb") as f:
            f.write(b'{"raw": 1}')
        self.write_snapshot(SNAP_DEGRADED, subdir="mixed")
        self.assertEqual(ri._snapshot_ymds(d), {"20261111"})  # 仅快照被发现

    def test_corrupted_candidate_excluded(self):
        d = os.path.join(self.root, "snapshots")
        os.makedirs(d)
        with open(os.path.join(d, "research_snapshot_20261113.json"), "w",
                  encoding="utf-8") as f:
            f.write("{NOT-JSON")
        entries, excluded = ri.index_snapshots(d)
        self.assertEqual(entries, [])
        self.assertEqual(excluded[0]["ymd"], "20261113")
        self.assertIn("select_snapshot 拒绝", excluded[0]["reason"])

    def test_assets_honest_empty_for_synthetic_metrics(self):
        # 合成指标不在注册表 → assets=[] 如实(不造值;维度面已实现)
        d = os.path.join(self.root, "snapshots")
        self.write_snapshot(SNAP_DEGRADED)
        entries, _ = ri.index_snapshots(d)
        self.assertEqual(entries[0]["assets"], [])


# ══ 索引源②: 正式报告(rp 8 条校验链在场复用) ═══════════════════════════

class TestFormalReportIndexing(SandboxBase):
    def test_published_pass_and_degraded_indexed(self):
        self.write_formal_report("reports", "20261107", MD_A_BYTES,
                                 final_quality="PASS")
        self.write_formal_report("reports", "20261114", MD_B_BYTES,
                                 final_quality="DEGRADED")
        entries = ri.index_formal_reports(os.path.join(self.root, "reports"))
        self.assertEqual([(e["kind"], e["ref"], e["date"]) for e in entries],
                         [("formal_report", "weekly_report_20261114",
                           "2026-11-14"),
                          ("formal_report", "weekly_report_20261107",
                           "2026-11-07")])   # rp 面按日期降序
        for e in entries:
            self.assertIsNone(e["digest"])   # 档键引用,不复制数值语义

    def test_unpublished_faces_excluded(self):
        # 无状态档/未发布/digest 不符/final_quality=FAIL 四负向面一律不入
        self.write_formal_report("reports", "20261121", MD_A_BYTES,
                                 with_status=False)
        self.write_formal_report("reports", "20261128", MD_A_BYTES,
                                 published=False)
        self.write_formal_report("reports", "20261205", MD_A_BYTES,
                                 report_digest="deadbeefdeadbeef")
        self.write_formal_report("reports", "20261212", MD_A_BYTES,
                                 final_quality="FAIL")
        entries = ri.index_formal_reports(os.path.join(self.root, "reports"))
        self.assertEqual(entries, [])

    def test_empty_dir(self):
        d = os.path.join(self.root, "reports")
        os.makedirs(d)
        self.assertEqual(ri.index_formal_reports(d), [])


# ══ 索引源③: 门禁后状态文件 ═════════════════════════════════════════════

class TestStateFileIndexing(SandboxBase):
    def setUp(self):
        super().setUp()
        self.tp = self._wjson("config/thesis.json", THESIS_DOC)
        self.vp = self._wjson("config/allocation_views.json", VIEWS_DOC)

    def test_thesis_entries(self):
        entries = ri.index_state_files(self.tp, self.vp)
        th = {e["ref"]: e for e in entries if e["kind"] == "thesis"}
        self.assertEqual(set(th), {"THESIS-T01", "THESIS-T02"})
        self.assertEqual((th["THESIS-T01"]["date"], th["THESIS-T01"]["status"]),
                         ("2026-11-05", "进行中"))
        self.assertEqual(th["THESIS-T01"]["metric_ids"],
                         ["TEST.CPI.SYN", "TEST.NFP.SYN"])
        self.assertEqual(th["THESIS-T02"]["metric_ids"], [])  # 零触发器如实空

    def test_view_entry_rating_status(self):
        e = {x["ref"]: x for x in
             ri.index_state_files(self.tp, self.vp)}["VIEW-V01"]
        self.assertEqual((e["status"], e["assets"], e["date"]),
                         ("超配", ["US_EQ"], "2026-11-06"))

    def test_prediction_entry(self):
        e = {x["ref"]: x for x in
             ri.index_state_files(self.tp, self.vp)}["PRED-P01"]
        self.assertEqual((e["date"], e["status"], e["metric_ids"]),
                         ("2026-11-01", "not_yet_triggered", ["TEST.CPI.SYN"]))

    def test_mechanisms_honest_absence(self):
        # DEV 状态文件无结构化机制标签(登记发现 P-A-08): 维度在,数据如实 null
        for e in ri.index_state_files(self.tp, self.vp):
            self.assertIsNone(e["mechanisms"], e["ref"])

    def test_missing_state_file_fail_loud(self):
        with self.assertRaises(FileNotFoundError):
            ri.index_state_files(os.path.join(self.root, "nope.json"), self.vp)


# ══ 版本记录: 写入路径黄金(VER- 同日单调;append-only 经 drr) ═══════════

class TestVersionRecordGolden(SandboxBase):
    def setUp(self):
        super().setUp()
        self.write_snapshot(SNAP_OK_V2)
        self.write_snapshot(SNAP_DEGRADED)
        self.write_snapshot(SNAP_FAIL)

    def test_first_record_trigger_basis(self):
        ret = self.record(created_at="2026-11-15T09:00:00")
        self.assertEqual(ret["status"], "written")
        self.assertEqual(ret["version_id"], "VER-20261115-001")
        self.assertEqual(ret["digest_snapshot"], GOLDEN["DIGEST_SNAP_OK_V2"])
        self.assertFalse(ret["applied"])                    # 旁路恒 False
        self.assertIn("不构成投资建议", ret["note"])
        self.assertTrue(os.path.exists(ret["record_path"]))
        records = ri.list_conclusion_versions(os.path.join(self.root, "archive"))
        self.assertEqual(len(records), 1)
        r = records[0]
        self.assertEqual(r["record_type"], "conclusion_version")
        self.assertEqual(r["object_id"], "THESIS-T01")
        self.assertEqual(r["gate_basis"], {"kind": "trigger",
                                           "trigger_id": "TRG-SYN-1"})  # 规范化
        self.assertEqual(r["changes"], CHANGES_STATUS)
        self.assertEqual(r["digest_snapshot"], GOLDEN["DIGEST_SNAP_OK_V2"])

    def test_same_day_monotonic_and_cross_type(self):
        self.record(created_at="2026-11-15T09:00:00")
        ret2 = self.record(object_type="view", object_id="VIEW-V01",
                           change_type="rating_change", changes=CHANGES_RATING,
                           gate_basis=copy.deepcopy(GATE_EV2),
                           created_at="2026-11-15T10:00:00")
        self.assertEqual(ret2["version_id"], "VER-20261115-002")
        ret3 = self.record(created_at="2026-11-16T09:00:00")
        self.assertEqual(ret3["version_id"], "VER-20261116-001")  # 翌日重起

    def test_degraded_snapshot_admissible_for_binding(self):
        ret = self.record(snapshot={"snapshot_id": "research_snapshot_20261111"},
                          created_at="2026-11-15T09:00:00")
        self.assertEqual(ret["digest_snapshot"], GOLDEN["DIGEST_SNAP_DEGRADED"])

    def test_deep_research_conclusion_object_type(self):
        ret = self.record(object_type="deep_research_conclusion",
                          object_id="RD-SYN-9999", created_at="2026-11-15T09:00:00")
        self.assertEqual(ret["status"], "written")

    def test_version_index_entries(self):
        self.record(created_at="2026-11-15T09:00:00")
        self.record(created_at="2026-11-15T10:00:00")
        entries = ri.index_conclusion_versions(os.path.join(self.root, "archive"))
        self.assertEqual([e["ref"] for e in entries],
                         ["VER-20261115-001", "VER-20261115-002"])
        e = entries[0]
        self.assertEqual((e["kind"], e["date"], e["status"]),
                         ("conclusion_version", "2026-11-15", "status_change"))
        self.assertEqual(e["snapshot_id"], "research_snapshot_20261110_v2")
        self.assertEqual(e["digest"], GOLDEN["DIGEST_SNAP_OK_V2"])


# ══ 版本记录: 校验负向(门禁依据强制/无弱门禁旁路;零写入) ═══════════════

class TestVersionValidationNegative(SandboxBase):
    def setUp(self):
        super().setUp()
        self.write_snapshot(SNAP_OK_V2)
        self.write_snapshot(SNAP_FAIL)
        self.archive = os.path.join(self.root, "archive")

    def _assert_zero_written(self):
        d = ri._versions_dir(self.archive)
        if os.path.isdir(d):
            self.assertEqual(os.listdir(d), [])

    def test_gate_basis_rejections(self):
        bad_bases = [
            {"kind": "oracle_gut_feel"},                       # 未知 kind
            {"kind": "trigger", "trigger_id": "  "},           # 空 trigger_id
            {"kind": "trigger"},                               # 缺 trigger_id
            {"kind": "program_evidence",
             "evidence_refs": ["EV-SYN-A"]},                   # 证据 1 项 < 2
            {"kind": "program_evidence",
             "evidence_refs": ["EV-SYN-A", ""]},               # 含空引用
            {"kind": "program_evidence"},                      # 缺 evidence_refs
            "not-a-dict",
            None,
        ]
        for bad in bad_bases:
            with self.assertRaises(ValueError, msg=repr(bad)):
                self.record(gate_basis=bad)
            self._assert_zero_written()

    def test_changes_rejections(self):
        for bad in ([], "not-list",
                    [{"field": "status", "before": "进行中", "after": "进行中"}],
                    [{"field": "status", "before": "进行中"}],
                    [{"field": "", "before": 1, "after": 2}]):
            with self.assertRaises(ValueError, msg=repr(bad)):
                self.record(changes=bad)
            self._assert_zero_written()

    def test_object_face_rejections(self):
        with self.assertRaises(ValueError):
            self.record(object_type="portfolio")               # 词表外
        with self.assertRaises(ValueError):
            self.record(object_type="view", object_id="THESIS-WRONG")  # 前缀不符
        with self.assertRaises(ValueError):
            self.record(change_type="vibe_shift")              # 词表外
        self._assert_zero_written()

    def test_snapshot_injection_face_rejections(self):
        with self.assertRaises(ValueError):
            self.record(snapshot={"snapshot_id": ""})
        with self.assertRaises(ValueError):
            self.record(snapshot={"snapshot_id": "not_a_snapshot_id"})
        with self.assertRaises(ValueError):
            self.record(snapshot=None)
        self._assert_zero_written()

    def test_snapshot_grounding_missing_file(self):
        with self.assertRaises(ValueError) as cm:
            self.record(snapshot={"snapshot_id": "research_snapshot_20269999"})
        self.assertIn("快照接地失败", str(cm.exception))
        self._assert_zero_written()

    def test_snapshot_gate_fail_fail_closed(self):
        with self.assertRaises(ValueError) as cm:
            self.record(snapshot={"snapshot_id": "research_snapshot_20261112"})
        self.assertIn("Gate A", str(cm.exception))
        self.assertIn("FAIL fail-closed", str(cm.exception))
        self._assert_zero_written()

    def test_record_validator_field_tampering(self):
        ret = self.record(created_at="2026-11-15T09:00:00")
        base = json.load(open(ret["record_path"], encoding="utf-8"))
        tampered_variants = []
        for field, bad in [
                ("record_type", "thesis"),
                ("version_id", "VER-2026-0001"),
                ("version_id", "VER-20261116-001"),           # 与 created_at 不符
                ("object_type", "portfolio"),
                ("object_id", "VIEW-OOPS"),                   # 前缀不符
                ("change_type", "vibe_shift"),
                ("changes", [{"field": "status", "before": "x", "after": "x"}]),
                ("gate_basis", {"kind": "trigger"}),
                ("snapshot_id", "junk"),
                ("digest_snapshot", "tooshort"),
                ("history", []),
                ("created_at", "2026-11-16T00:00:00")]:       # 与版本键日期不符
            t = copy.deepcopy(base)
            t[field] = bad
            tampered_variants.append(t)
        missing = copy.deepcopy(base)
        del missing["gate_basis"]
        tampered_variants.append(missing)
        for t in tampered_variants:
            with self.assertRaises(ValueError, msg=f"{t.get('version_id')}"):
                ri.validate_conclusion_version_record(t)


# ══ 版本记录: append-only(既有档零改写/重放拒/篡改 fail-loud) ════════════

class TestVersionAppendOnly(SandboxBase):
    def setUp(self):
        super().setUp()
        self.write_snapshot(SNAP_OK_V2)
        self.archive = os.path.join(self.root, "archive")

    def test_existing_records_never_modified(self):
        r1 = self.record(created_at="2026-11-15T09:00:00")
        b1 = open(r1["record_path"], "rb").read()
        self.record(object_type="view", object_id="VIEW-V01",
                    change_type="rating_change", changes=CHANGES_RATING,
                    gate_basis=copy.deepcopy(GATE_EV2),
                    created_at="2026-11-15T10:00:00")
        self.record(created_at="2026-11-16T09:00:00")
        self.assertEqual(open(r1["record_path"], "rb").read(), b1)  # 逐字节不变

    def test_tampered_archive_fail_loud(self):
        r1 = self.record(created_at="2026-11-15T09:00:00")
        rec = json.load(open(r1["record_path"], encoding="utf-8"))
        rec["object_id"] = "VIEW-HACKED"
        with open(r1["record_path"], "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, sort_keys=True, indent=1)
        with self.assertRaises(ValueError):
            ri.list_conclusion_versions(self.archive)

    def test_write_race_duplicate_rejected(self):
        r1 = self.record(created_at="2026-11-15T09:00:00")
        b1 = open(r1["record_path"], "rb").read()
        with patch.object(ri, "_same_day_max_seq",
                          lambda archive_dir, ymd8: 0):       # 并发窗口模拟
            ret = self.record(created_at="2026-11-15T11:00:00")
        self.assertEqual(ret["status"], "rejected-duplicate")  # drr 原语拒绝
        self.assertFalse(ret["applied"])
        self.assertEqual(open(r1["record_path"], "rb").read(), b1)  # 既有档不变
        self.assertEqual(len(ri.list_conclusion_versions(self.archive)), 1)


# ══ 修正提案(§3.3: 同门禁依据;提案≠回写) ═══════════════════════════════

class TestReviseConclusion(SandboxBase):
    def setUp(self):
        super().setUp()
        self.write_snapshot(SNAP_OK_V2)
        self.tp = self._wjson("config/thesis.json", THESIS_DOC)
        self.vp = self._wjson("config/allocation_views.json", VIEWS_DOC)
        self.archive = os.path.join(self.root, "archive")
        self.t0 = open(self.tp, "rb").read()
        self.v0 = open(self.vp, "rb").read()

    def test_revision_proposal_appended_not_applied(self):
        ret = ri.revise_conclusion(
            "thesis", "THESIS-T01",
            [{"field": "status", "before": "进行中", "after": "已失效"}],
            copy.deepcopy(GATE_TRIG), {"snapshot_id": "research_snapshot_20261110_v2"},
            snapshot_dir=os.path.join(self.root, "snapshots"),
            archive_dir=self.archive, created_at="2026-11-17T09:00:00")
        self.assertEqual(ret["version_id"], "VER-20261117-001")
        rec = ri.list_conclusion_versions(self.archive)[0]
        self.assertEqual(rec["change_type"], "revision_proposal")
        self.assertIn("修正提案", rec["history"][0]["note"])
        self.assertFalse(ret["applied"])

    def test_revision_gate_still_enforced_and_zero_state_write(self):
        with self.assertRaises(ValueError):                    # 弱依据仍拒
            ri.revise_conclusion(
                "thesis", "THESIS-T01", CHANGES_STATUS,
                {"kind": "program_evidence", "evidence_refs": ["ONLY-ONE"]},
                {"snapshot_id": "research_snapshot_20261110_v2"},
                snapshot_dir=os.path.join(self.root, "snapshots"),
                archive_dir=self.archive, created_at="2026-11-17T09:00:00")
        ri.revise_conclusion(
            "thesis", "THESIS-T01", CHANGES_STATUS,
            copy.deepcopy(GATE_TRIG),
            {"snapshot_id": "research_snapshot_20261110_v2"},
            snapshot_dir=os.path.join(self.root, "snapshots"),
            archive_dir=self.archive, created_at="2026-11-17T09:00:00")
        self.assertEqual(open(self.tp, "rb").read(), self.t0)  # 状态档零写入
        self.assertEqual(open(self.vp, "rb").read(), self.v0)


# ══ 索引确定性(要点②: 可重建性逐字节一致) ═══════════════════════════════

class TestIndexDeterminism(SandboxBase):
    SMALL = [ri._mk_entry("thesis", "THESIS-T01", date="2026-11-05",
                          status="进行中",
                          metric_ids=["TEST.CPI.SYN", "TEST.NFP.SYN"])]

    def test_small_index_bytes_golden(self):
        p = os.path.join(self.root, "idx", ri.RESEARCH_INDEX_FILENAME)
        ri.write_index_file(p, self.SMALL)
        self.assertEqual(
            hashlib.sha256(open(p, "rb").read()).hexdigest(),
            GOLDEN["INDEX_SMALL_SHA256"])

    def test_delete_and_rebuild_byte_identical(self):
        p = os.path.join(self.root, "idx", ri.RESEARCH_INDEX_FILENAME)
        ri.write_index_file(p, self.SMALL)
        b1 = open(p, "rb").read()
        os.remove(p)                                          # 索引灭失
        ri.rebuild_index(p, snapshot_entries=self.SMALL)
        self.assertEqual(open(p, "rb").read(), b1)            # 逐字节重建

    def test_rewrite_and_replay_idempotent(self):
        p = os.path.join(self.root, "idx", ri.RESEARCH_INDEX_FILENAME)
        ri.write_index_file(p, self.SMALL)
        b1 = open(p, "rb").read()
        ri.write_index_file(p, self.SMALL)                    # 重写幂等
        self.assertEqual(open(p, "rb").read(), b1)
        ri.update_index_entries(p, self.SMALL)                # 同键重放幂等
        self.assertEqual(open(p, "rb").read(), b1)

    def test_update_replaces_same_key_adds_new(self):
        p = os.path.join(self.root, "idx", ri.RESEARCH_INDEX_FILENAME)
        ri.write_index_file(p, self.SMALL)
        changed = ri._mk_entry("thesis", "THESIS-T01", date="2026-11-06",
                               status="待观察",
                               metric_ids=["TEST.CPI.SYN"])
        added = ri._mk_entry("view", "VIEW-V01", date="2026-11-06",
                             status="超配")
        ri.update_index_entries(p, [changed, added])
        doc = ri.load_index_file(p)
        self.assertEqual(len(doc["entries"]), 2)              # 替换非追加
        by_ref = {e["ref"]: e for e in doc["entries"]}
        self.assertEqual(by_ref["THESIS-T01"]["status"], "待观察")
        self.assertEqual(by_ref["THESIS-T01"]["date"], "2026-11-06")


# ══ 索引文件面(损坏→fail-loud;衍生物可重建) ════════════════════════════

class TestIndexFileFace(SandboxBase):
    def _write_valid(self):
        p = os.path.join(self.root, "idx", ri.RESEARCH_INDEX_FILENAME)
        ri.write_index_file(p, [
            ri._mk_entry("thesis", "THESIS-T01", date="2026-11-05"),
            ri._mk_entry("view", "VIEW-V01", date="2026-11-06")])
        return p

    def test_round_trip(self):
        p = self._write_valid()
        doc = ri.load_index_file(p)
        self.assertEqual([e["ref"] for e in doc["entries"]],
                         ["THESIS-T01", "VIEW-V01"])          # (kind,ref) 排序

    def test_corrupt_json_fail_loud(self):
        p = self._write_valid()
        with open(p, "w", encoding="utf-8") as f:
            f.write("{broken")
        with self.assertRaises(ValueError):
            ri.load_index_file(p)

    def test_wrong_schema_version(self):
        p = self._write_valid()
        doc = json.load(open(p, encoding="utf-8"))
        doc["schema_version"] = 99
        with open(p, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False)
        with self.assertRaises(ValueError):
            ri.load_index_file(p)

    def test_entry_key_set_violations(self):
        p = self._write_valid()
        doc = json.load(open(p, encoding="utf-8"))
        doc["entries"][0]["extra_key"] = 1                    # 多键
        with open(p, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False)
        with self.assertRaises(ValueError):
            ri.load_index_file(p)
        p2 = self._write_valid()
        doc = json.load(open(p2, encoding="utf-8"))
        del doc["entries"][0]["digest"]                       # 少键
        with open(p2, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False)
        with self.assertRaises(ValueError):
            ri.load_index_file(p2)

    def test_sort_drift_and_duplicate_rejected(self):
        p = self._write_valid()
        doc = json.load(open(p, encoding="utf-8"))
        doc["entries"] = list(reversed(doc["entries"]))       # 排序漂移
        with open(p, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False)
        with self.assertRaises(ValueError):
            ri.load_index_file(p)
        p2 = self._write_valid()
        doc = json.load(open(p2, encoding="utf-8"))
        doc["entries"] = [doc["entries"][0], copy.deepcopy(doc["entries"][0])]
        with open(p2, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False)
        with self.assertRaises(ValueError):
            ri.load_index_file(p2)

    def test_reserved_kind_entry_not_loadable(self):
        p = self._write_valid()
        doc = json.load(open(p, encoding="utf-8"))
        doc["entries"].append({"kind": "deep_research_task", "ref": "RD-X",
                               "date": None, "status": None, "metric_ids": None,
                               "assets": None, "mechanisms": None,
                               "obs_min": None, "obs_max": None,
                               "snapshot_id": None, "digest": None})
        with open(p, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False)
        with self.assertRaises(ValueError):
            ri.load_index_file(p)                             # O-5 禁冒充收录


# ══ 结构化查询 API(六维度;档键引用输出) ═════════════════════════════════

class TestQueryAPI(unittest.TestCase):
    def test_metric_filter(self):
        out = ri.query_index(_qindex(), metric_ids=["TEST.CPI.SYN"])
        self.assertEqual([o["ref"] for o in out],
                         ["research_snapshot_20261110_v2", "research_snapshot_20261111",
                          "THESIS-T01", "VIEW-V01"])

    def test_assets_filter(self):
        out = ri.query_index(_qindex(), assets=["US_EQ"])
        self.assertEqual([o["ref"] for o in out], ["VIEW-V01"])

    def test_status_filter_exact(self):
        self.assertEqual([o["ref"] for o in
                          ri.query_index(_qindex(), statuses=["进行中"])],
                         ["THESIS-T01"])
        self.assertEqual([o["ref"] for o in
                          ri.query_index(_qindex(), statuses=["进行中", "超配"])],
                         ["THESIS-T01", "VIEW-V01"])

    def test_key_prefix_filter(self):
        self.assertEqual([o["ref"] for o in
                          ri.query_index(_qindex(), key_prefixes=["VER-"])],
                         ["VER-20261115-001"])
        self.assertEqual([o["ref"] for o in
                          ri.query_index(_qindex(), key_prefixes=["THESIS-", "PRED-"])],
                         ["THESIS-T01"])

    def test_window_date_inclusion(self):
        # 窗 [11-01,11-06]: THESIS(11-05)/VIEW(11-06) date 落窗;
        # snap10v2 date=11-10 在窗外但 obs=[11-03,11-06] 相交→命中;
        # weekly_report(11-07)/VER(11-15)/snap11(obs 11-10) 均不命中
        out = ri.query_index(_qindex(), obs_start="2026-11-01",
                             obs_end="2026-11-06")
        self.assertEqual([o["ref"] for o in out],
                         ["research_snapshot_20261110_v2",
                          "THESIS-T01", "VIEW-V01"])

    def test_window_obs_range_overlap(self):
        # 20261111 快照 date=11-11 在窗外,obs=[11-10,11-10] 与窗相交 → 命中
        out = ri.query_index(_qindex(), obs_start="2026-11-01",
                             obs_end="2026-11-10")
        self.assertIn("research_snapshot_20261111", [o["ref"] for o in out])

    def test_filters_and_composed(self):
        out = ri.query_index(_qindex(), metric_ids=["TEST.CPI.SYN"],
                             key_prefixes=["VIEW-"])
        self.assertEqual([o["ref"] for o in out], ["VIEW-V01"])

    def test_output_shape_and_order(self):
        out = ri.query_index(_qindex())
        self.assertEqual(len(out), 6)
        for o in out:
            self.assertEqual(set(o.keys()),
                             {"kind", "ref", "snapshot_id", "digest"})
        keys = [(o["kind"], o["ref"]) for o in out]
        self.assertEqual(keys, sorted(keys))

    def test_mechanisms_dimension_honest_absence(self):
        # 条目 mechanisms 全 null(数据面缺席): 过滤器在,不造匹配
        self.assertEqual(ri.query_index(_qindex(), mechanisms=["通胀"]), [])

    def test_negative_arguments(self):
        q = _qindex()
        with self.assertRaises(ValueError):
            ri.query_index(q, obs_start="2026-11-10", obs_end="2026-11-01")
        with self.assertRaises(ValueError):
            ri.query_index(q, obs_start="2026/11/01")
        with self.assertRaises(ValueError):
            ri.query_index(q, statuses="进行中")              # 须列表
        with self.assertRaises(ValueError):
            ri.query_index(q, key_prefixes=[""])              # 空串前缀
        with self.assertRaises(ValueError):
            ri.query_index({"entries": "not-list"})
        with self.assertRaises(ValueError):
            ri.query_index(["not", "a", "dict"])


# ══ O-5 接口预留(词表在场/收录集排除/skipped_reserved) ══════════════════

class TestOSkipping(unittest.TestCase):
    def test_reserved_marker_shape(self):
        m = ri.index_reserved_kind("RD-SYN-1")
        self.assertEqual(m["kind"], "deep_research_task")
        self.assertEqual(m["ref"], "RD-SYN-1")
        self.assertIn("reserved", m["skipped"])
        self.assertIn("O-5", m["skipped"])

    def test_reserved_kind_not_constructible_as_entry(self):
        with self.assertRaises(ValueError):
            ri._mk_entry("deep_research_task", "RD-SYN-1", date=None)

    def test_indexed_set_excludes_reserved(self):
        self.assertNotIn("deep_research_task", ri.INDEXED_KINDS)
        self.assertIn("deep_research_task", ri.REF_KINDS)     # 词表在场


# ══ 静态纯度(import 白名单/零网络/零凭证/零 data/daily/墙钟受限) ════════

class TestStaticPurity(unittest.TestCase):
    def setUp(self):
        with open(MODULE_SOURCE_PATH, "r", encoding="utf-8") as f:
            self.src = f.read()
        self.tree = ast.parse(self.src)

    def test_import_whitelist(self):
        allowed_top = {"json", "os", "re", "sys",
                       "deep_research_registrar", "research_provenance",
                       "fact_engine"}
        allowed_from = {"datetime"}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    self.assertIn(a.name.split(".")[0], allowed_top,
                                  f"违规 import: {a.name}")
            elif isinstance(node, ast.ImportFrom):
                root = (node.module or "").split(".")[0]
                self.assertIn(root, allowed_from, f"违规 from-import: {node.module}")

    def test_no_network_no_credentials(self):
        low = self.src.lower()
        for token in ("socket", "urllib", "requests", "http://", "https://",
                      "api_key", "apikey", "password", "bearer", "authorization",
                      "sk-", "billing"):
            self.assertNotIn(token, low, token)

    def test_no_raw_daily_literal(self):
        self.assertNotIn("data/daily", self.src)
        # 严格快照 glob 字面锚(结构性不可达采集件的正则面)
        self.assertEqual(ri._SNAPSHOT_GLOB, "research_snapshot_*.json")
        self.assertEqual(ri._SNAPSHOT_YMD_RE.pattern,
                         r"^research_snapshot_(\d{8})(?:_v\d+)?\.json$")

    def test_wall_clock_confined_to_now_iso(self):
        clock_attrs = {"now", "utcnow", "today"}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and node.name != "_now_iso":
                for sub in ast.walk(node):
                    if (isinstance(sub, ast.Call)
                            and getattr(sub.func, "attr", None) in clock_attrs):
                        self.fail(f"墙钟调用越界: {node.name}")


# ══ 零状态文件写入(旁路不改回写签名) ═════════════════════════════════════

class TestZeroStateWrite(SandboxBase):
    def test_record_and_revise_leave_state_files_untouched(self):
        self.write_snapshot(SNAP_OK_V2)
        tp = self._wjson("config/thesis.json", THESIS_DOC)
        vp = self._wjson("config/allocation_views.json", VIEWS_DOC)
        b0 = (open(tp, "rb").read(), open(vp, "rb").read())
        self.record()
        ri.revise_conclusion(
            "view", "VIEW-V01", CHANGES_RATING, copy.deepcopy(GATE_EV2),
            {"snapshot_id": "research_snapshot_20261110_v2"},
            snapshot_dir=os.path.join(self.root, "snapshots"),
            archive_dir=os.path.join(self.root, "archive"),
            created_at="2026-11-18T09:00:00")
        self.assertEqual((open(tp, "rb").read(), open(vp, "rb").read()), b0)
        self.assertTrue(ri.DEFAULT_INDEX_DIR.endswith(
            os.path.join("data", "research")))                # 索引落 data/research


# ══ 端到端(全链沙箱内聚: 四源构建→重建→查询→O-5 预留) ═════════════════

class TestEndToEnd(SandboxBase):
    def test_full_chain(self):
        for s in (SNAP_OK, SNAP_OK_V2, SNAP_DEGRADED, SNAP_FAIL):
            self.write_snapshot(s)
        self.write_formal_report("reports", "20261107", MD_A_BYTES,
                                 final_quality="PASS")
        self.write_formal_report("reports", "20261114", MD_B_BYTES,
                                 final_quality="DEGRADED")
        self.write_formal_report("reports", "20261121", MD_A_BYTES,
                                 published=False)
        tp = self._wjson("config/thesis.json", THESIS_DOC)
        vp = self._wjson("config/allocation_views.json", VIEWS_DOC)
        archive = os.path.join(self.root, "archive")
        self.record(archive="archive")                       # VER-20261115-001
        self.record(object_type="view", object_id="VIEW-V01",
                    change_type="rating_change", changes=CHANGES_RATING,
                    gate_basis=copy.deepcopy(GATE_EV2),
                    created_at="2026-11-15T10:00:00")        # VER-20261115-002
        self.record(created_at="2026-11-16T09:00:00")        # VER-20261116-001

        snap_entries, excluded = ri.index_snapshots(
            os.path.join(self.root, "snapshots"))
        rep_entries = ri.index_formal_reports(os.path.join(self.root, "reports"))
        state_entries = ri.index_state_files(tp, vp)
        ver_entries = ri.index_conclusion_versions(archive)
        self.assertEqual((len(snap_entries), len(excluded)), (2, 1))
        self.assertEqual(len(rep_entries), 2)                # 未发布面不入
        self.assertEqual(len(state_entries), 4)
        self.assertEqual(len(ver_entries), 3)

        p = os.path.join(self.root, "idx", ri.RESEARCH_INDEX_FILENAME)
        ri.rebuild_index(p, snapshot_entries=snap_entries,
                         report_entries=rep_entries,
                         state_entries=state_entries,
                         version_entries=ver_entries)
        doc = ri.load_index_file(p)
        self.assertEqual(len(doc["entries"]), 2 + 2 + 4 + 3)  # = 11
        b1 = open(p, "rb").read()
        ri.rebuild_index(p, snapshot_entries=snap_entries,
                         report_entries=rep_entries,
                         state_entries=state_entries,
                         version_entries=ver_entries)
        self.assertEqual(open(p, "rb").read(), b1)           # 重建逐字节一致

        # O-5 预留: 登记项非索引条目
        marker = ri.index_reserved_kind("RD-SYN-1")
        self.assertNotIn(marker["kind"],
                         {e["kind"] for e in doc["entries"]})

        out_metric = ri.query_index(doc, metric_ids=["TEST.CPI.SYN"])
        self.assertEqual([o["ref"] for o in out_metric],
                         ["PRED-P01",
                          "research_snapshot_20261110_v2",
                          "research_snapshot_20261111",
                          "THESIS-T01", "VIEW-V01"])
        out_ver = ri.query_index(doc, key_prefixes=["VER-"])
        self.assertEqual(len(out_ver), 3)
        out_win = ri.query_index(doc, obs_start="2026-11-01",
                                 obs_end="2026-11-10")
        self.assertEqual(len(out_win), 7)                    # 含 obs 相交命中


if __name__ == "__main__":
    unittest.main()
