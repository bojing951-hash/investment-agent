#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P03-E2EB-WP-B4 专项测试: 共享研究档案与查询历史(append-only)。

DESIGN §六 WP-B4 验收要点(L228-232)离线可验证面全覆盖:
- 要点① append-only 不可变: T1(重复写入/改写被拒/无改写API/同日单调/跨日独立);
- 要点② ID 格式与交叉引用字段校验: T2(QB/RT 四 ID 约定+记录级落位);
- 要点③ digest 绑定: T3(R5 重算落档/篡改快照后校验拒绝/缺档/损坏/身份不符/
  错误 digest/非规范 snapshot_id/v2 文件名解析);
- 补充: T0 fixture 自检/T4 记录 schema 与确定性摘要/T5 复用与纯度锁/T6 fail-loud。

fixture→预期值映射(D-B4-12;DELIVERY 专节同款登记):
- SNAP_A/SNAP_B_V2(手造最小快照) → L_DIGEST_A='756c258d9943841d'/
  L_DIGEST_B_V2='2418e26ca8294e02'(R5 真实管线预计算誊写,/tmp/b4_precalc.py
  经 hashlib 独立旁证,零自证恒真);
- IR_M(mapped)/IR_E(executed)(手造最小 IR,过 qir.validate_ir 双阶段) →
  摘要字面量 L_SUMMARY_*/状态串字面量/157.8 数值字面量;
- 全部断言预期值字面量硬编码,不从被测模块导入计算;零真实数据档读取
  (不读 data/daily 与 data/research 任何真实档;tempdir 沙箱)。
"""
import copy
import hashlib
import inspect
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) and
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
import research_archive as ra
import e2eb_query_ir as qir
import research_provenance as rp

MODULE_SRC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               '..', 'scripts', 'research_archive.py')
with open(MODULE_SRC_PATH, 'r', encoding='utf-8') as _f:
    MODULE_SRC = _f.read()

# ══ 合成 fixture(唯一数据源;D-B4-12) ═════════════════════════════════════

SNAP_A = {
    "snapshot_id": "research_snapshot_20261105",
    "target_date": "20261105",
    "gate_a": {"status": "PASS"},
    "facts": [{"metric_id": "USDJPY", "value": 157.8,
               "observation_date": "2026-11-04", "unit": "jpy_per_usd",
               "quality_status": "PASS"}],
}
SNAP_B_V2 = {
    "snapshot_id": "research_snapshot_20261105_v2",
    "target_date": "20261105",
    "gate_a": {"status": "DEGRADED"},
    "facts": [{"metric_id": "USDJPY", "value": 158.2,
               "observation_date": "2026-11-05", "unit": "jpy_per_usd",
               "quality_status": "PASS"}],
}

IR_M = {
    "query_id": "QB-20261105-001",
    "created_at": "2026-11-05T10:00:00+08:00",
    "mode": "B",
    "question_text": "美元兑日元最近走势如何?",
    "as_of": None,
    "target_snapshot_id": None,
    "metric_bindings": [
        {"binding_id": "MB-1", "metric_id": "USDJPY", "role": "level",
         "window": None, "field": "value", "status": "PENDING_EXECUTION",
         "absence_reason": None, "provenance": None},
        {"binding_id": "MB-2", "metric_id": None, "role": "spread_component",
         "window": None, "field": "value", "status": "ABSENT_REGISTRY",
         "absence_reason": "JGB_10Y不在注册表(81指标,INVENTORY G-01)",
         "provenance": None},
    ],
    "derived_operations": [
        {"op_id": "OP-1", "op_type": "spread", "operands": ["MB-2", "MB-1"],
         "formula": "JGB_10Y − USDJPY", "unit": "jpy_per_usd",
         "status": "NO_DATA", "result": None,
         "calculation_ref": "美日收益率差: operand MB-2 缺席→NO_DATA不部分计算"},
    ],
    "unresolved_entities": [],
    "answer_constraints": {"grounding_required": True,
                           "no_data_policy": "report_absence"},
}

IR_E = {
    "query_id": "QB-20261105-001",
    "created_at": "2026-11-05T10:00:00+08:00",
    "mode": "B",
    "question_text": "美元兑日元最近走势如何?",
    "as_of": None,
    "target_snapshot_id": "research_snapshot_20261105",
    "metric_bindings": [
        {"binding_id": "MB-1", "metric_id": "USDJPY", "role": "level",
         "window": None, "field": "value", "status": "RESOLVED",
         "absence_reason": None,
         "provenance": {"metric_id": "USDJPY",
                        "snapshot_id": "research_snapshot_20261105",
                        "fact_id": "USDJPY@2026-11-04",
                        "observation_date": "2026-11-04",
                        "source_file": "global_20261105.json",
                        "quality_status": "PASS",
                        "calculation_ref": None}},
        {"binding_id": "MB-2", "metric_id": None, "role": "spread_component",
         "window": None, "field": "value", "status": "ABSENT_REGISTRY",
         "absence_reason": "JGB_10Y不在注册表(81指标,INVENTORY G-01)",
         "provenance": None},
    ],
    "derived_operations": [
        {"op_id": "OP-1", "op_type": "spread", "operands": ["MB-2", "MB-1"],
         "formula": "JGB_10Y − USDJPY", "unit": "jpy_per_usd",
         "status": "NO_DATA", "result": None,
         "calculation_ref": "美日收益率差: operand MB-2 缺席→NO_DATA不部分计算"},
    ],
    "unresolved_entities": [],
    "answer_constraints": {"grounding_required": True,
                           "no_data_policy": "report_absence"},
}

EXEC_OK = {"ir": copy.deepcopy(IR_E), "values": {"MB-1": 157.8},
           "snapshot_id": "research_snapshot_20261105", "gate_status": "PASS"}
EXEC_REFUSAL = {"ir": copy.deepcopy(IR_M), "values": {}, "snapshot_id": None,
                "gate_status": "FAIL",
                "refusal": "Gate A状态'FAIL'不放行正式研究查询(R3)"}

# ══ 预期值字面量(硬编码;预计算=/tmp/b4_precalc.py,R5真实管线+hashlib独立旁证) ══

L_DIGEST_A = "756c258d9943841d"          # rp.digest_snapshot(SNAP_A)
L_DIGEST_B_V2 = "2418e26ca8294e02"       # rp.digest_snapshot(SNAP_B_V2)
L_REFUSAL = "Gate A状态'FAIL'不放行正式研究查询(R3)"
L_SUMMARY_MAPPED = {"ir_stage": "mapped", "refusal": None,
                    "binding_status_counts": {"ABSENT_REGISTRY": 1,
                                              "PENDING_EXECUTION": 1},
                    "op_status_counts": {"NO_DATA": 1},
                    "n_unresolved": 0, "values": {}}
L_SUMMARY_EXEC = {"ir_stage": "executed", "refusal": None,
                  "binding_status_counts": {"ABSENT_REGISTRY": 1, "RESOLVED": 1},
                  "op_status_counts": {"NO_DATA": 1},
                  "n_unresolved": 0, "values": {"MB-1": 157.8}}
L_SUMMARY_REFUSAL = {"ir_stage": "mapped", "refusal": L_REFUSAL,
                     "binding_status_counts": {"ABSENT_REGISTRY": 1,
                                               "PENDING_EXECUTION": 1},
                     "op_status_counts": {"NO_DATA": 1},
                     "n_unresolved": 0, "values": {}}
L_ARCHIVED_AT = "2026-11-05T02:00:00+00:00"

FORBIDDEN_RAW_PREFIXES = ("macro_2", "global_2", "china_market", "rate_economy")
FORBIDDEN_API_VERBS = ("update", "rewrite", "delete", "remove", "modify",
                       "erase", "drop")
ALLOWED_PUBLIC_FUNCS = {"validate_id_conventions", "parse_snapshot_id",
                        "build_answer_summary", "validate_query_record",
                        "list_query_records", "allocate_query_id",
                        "append_query_record", "load_query_record",
                        "verify_query_record", "verify_archive",
                        # 批2 WI6(2026-11-09)显式扩面: research_full sidecar
                        # (validate/write/load;旧 query_history 契约一字不动)
                        "validate_research_full", "write_research_full",
                        "load_research_full"}


def _ir_with_qid(ir, qid):
    out = copy.deepcopy(ir)
    out["query_id"] = qid
    return out


def _ir_day2(ir):
    """改日变体: created_at 2026-11-06 与 query_id QB-20261106-NNN 同步。"""
    out = copy.deepcopy(ir)
    out["created_at"] = "2026-11-06T09:30:00+08:00"
    out["query_id"] = "QB-20261106-001"
    if out.get("target_snapshot_id"):
        out["target_snapshot_id"] = "research_snapshot_20261106"
        for b in out["metric_bindings"]:
            if b.get("provenance"):
                b["provenance"]["snapshot_id"] = "research_snapshot_20261106"
    return out


class B4TestBase(unittest.TestCase):

    def fresh_archive(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return tmp.name

    def fresh_snapdir(self, *snaps):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        for s in snaps:
            self.write_snap(tmp.name, s)
        return tmp.name

    def write_snap(self, d, snap):
        path = os.path.join(d, ra._snapshot_filename(snap["snapshot_id"]))
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(snap, f, ensure_ascii=False, sort_keys=True, indent=1)
        return path

    def append_basic(self, arch, ir=None, snap=None, **kw):
        kw.setdefault("archived_at", L_ARCHIVED_AT)
        return ra.append_query_record(ir if ir is not None else copy.deepcopy(IR_M),
                                      snapshot=copy.deepcopy(
                                          snap if snap is not None else SNAP_A),
                                      archive_dir=arch, **kw)

    def file_sha(self, path):
        with open(path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()


# ══ T0 fixture 自检 ═══════════════════════════════════════════════════════

class T0FixtureSelfCheck(B4TestBase):

    def test_fixture_ir_stage_validity(self):
        self.assertEqual(qir.validate_ir(copy.deepcopy(IR_M), stage="mapped"), [])
        self.assertEqual(qir.validate_ir(copy.deepcopy(IR_E), stage="executed"), [])

    def test_fixture_digest_literals(self):
        # R5 真实管线产出==硬编码字面量(预计算誊写;hashlib 独立旁证见预演脚本)
        self.assertEqual(rp.digest_snapshot(copy.deepcopy(SNAP_A)), L_DIGEST_A)
        self.assertEqual(rp.digest_snapshot(copy.deepcopy(SNAP_B_V2)), L_DIGEST_B_V2)


# ══ T1 append-only 不可变(要点①) ═════════════════════════════════════════

class T1AppendOnly(B4TestBase):

    def test_append_mapped_written_and_readable(self):
        arch = self.fresh_archive()
        status, path = self.append_basic(arch)
        self.assertEqual(status, "written")
        self.assertTrue(os.path.exists(path))
        rec = ra.load_query_record("QB-20261105-001", archive_dir=arch)
        self.assertEqual(rec["record_type"], "query_history")
        self.assertEqual(rec["ir_stage"], "mapped")
        self.assertEqual(rec["digest_snapshot"], L_DIGEST_A)
        self.assertEqual(rec["snapshot_id"], "research_snapshot_20261105")
        self.assertEqual(rec["archived_at"], L_ARCHIVED_AT)

    def test_duplicate_append_identical_rejected_bytes_unchanged(self):
        arch = self.fresh_archive()
        _, path = self.append_basic(arch)
        sha_before = self.file_sha(path)
        status, _ = self.append_basic(arch)      # 同 query_id 同内容重复写入
        self.assertEqual(status, ra.STATUS_REJECTED_DUPLICATE)
        self.assertEqual(self.file_sha(path), sha_before)   # 既有档字节零触碰

    def test_duplicate_append_modified_content_rejected(self):
        arch = self.fresh_archive()
        _, path = self.append_basic(arch)
        sha_before = self.file_sha(path)
        other = copy.deepcopy(IR_M)
        other["question_text"] = "改写尝试: 美债10Y怎么样?"
        status, _ = self.append_basic(arch, ir=other)       # 同 id 异内容=改写
        self.assertEqual(status, ra.STATUS_REJECTED_DUPLICATE)
        self.assertEqual(self.file_sha(path), sha_before)

    def test_no_rewrite_or_delete_api(self):
        # 记录不可变不可删改(§四行6): 模块公共 API 面无任何改写/删除入口
        public = [n for n in dir(ra) if not n.startswith('_')
                  and callable(getattr(ra, n))]
        for verb in FORBIDDEN_API_VERBS:
            for name in public:
                self.assertFalse(name.lower().startswith(verb),
                                 f"公共API含改写/删除族入口: {name}")

    def test_monotonic_seq_enforced(self):
        arch = self.fresh_archive()
        self.assertEqual(self.append_basic(arch)[0], "written")            # 001
        s3, _ = self.append_basic(arch, ir=_ir_with_qid(IR_M, "QB-20261105-003"))
        self.assertEqual(s3, "written")                                    # 003 空洞合法(单调≠连续)
        s2, _ = self.append_basic(arch, ir=_ir_with_qid(IR_M, "QB-20261105-002"))
        self.assertEqual(s2, ra.STATUS_REJECTED_NON_MONOTONIC)             # 002≤max → 拒
        self.assertFalse(os.path.exists(os.path.join(
            arch, "research_archive", "query_history", "QB-20261105-002.json")))
        s4, _ = self.append_basic(arch, ir=_ir_with_qid(IR_M, "QB-20261105-004"))
        self.assertEqual(s4, "written")                                    # 004>max → 过

    def test_cross_day_independent_sequence(self):
        arch = self.fresh_archive()
        self.append_basic(arch, ir=_ir_with_qid(IR_M, "QB-20261105-005"))
        status, _ = self.append_basic(arch, ir=_ir_day2(IR_M))             # 次日 001
        self.assertEqual(status, "written")                                # 同日序列独立计数(L183)
        self.assertEqual(ra.list_query_records(archive_dir=arch, ymd="20261106"),
                         ["QB-20261106-001"])

    def test_append_never_overwrites_precreated_file(self):
        arch = self.fresh_archive()
        coll = os.path.join(arch, "research_archive", "query_history")
        os.makedirs(coll)
        garbage = os.path.join(coll, "QB-20261105-007.json")
        with open(garbage, 'w', encoding='utf-8') as f:
            f.write("PRE-EXISTING BYTES")
        status, _ = self.append_basic(arch, ir=_ir_with_qid(IR_M, "QB-20261105-007"))
        self.assertEqual(status, ra.STATUS_REJECTED_DUPLICATE)
        with open(garbage, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), "PRE-EXISTING BYTES")

    def test_allocate_query_id_scans_existing(self):
        arch = self.fresh_archive()
        self.assertEqual(ra.allocate_query_id("2026-11-05T10:00:00+08:00", arch),
                         "QB-20261105-001")                                # 空目录→001
        self.append_basic(arch)
        self.append_basic(arch, ir=_ir_with_qid(IR_M, "QB-20261105-003"))  # 空洞
        self.assertEqual(ra.allocate_query_id("2026-11-05T12:00:00+08:00", arch),
                         "QB-20261105-004")                                # max+1
        self.assertEqual(ra.allocate_query_id("2026-11-06T09:00:00+08:00", arch),
                         "QB-20261106-001")                                # 跨日新序列


# ══ T2 ID 格式与交叉引用字段校验(要点②) ═══════════════════════════════════

class T2IDConventions(B4TestBase):

    def test_conventions_valid_forms(self):
        self.assertEqual(ra.validate_id_conventions(
            query_id="QB-20261105-001",
            origin_query_id="QB-20261104-002",
            task_id="RT-20261105-001",                       # DESIGN L183 严格格式
            promoted_to_task_id="RT-2026-06-30~2026-09-30-RD-DIV-001-17788777"),
            [])                                              # E2E-A 实况形态(rtm.py:48-53)
        self.assertEqual(ra.validate_id_conventions(), [])   # 全 null 合法(字段可缺省)

    def test_conventions_invalid_forms(self):
        for kw in ({"query_id": "QB-2026115-001"},           # 日期段非8位
                   {"query_id": "QB-20261105-01"},           # 序号非3位
                   {"query_id": "QB-20261105-0001"},
                   {"query_id": "RT-20261105-001"},          # 前缀族错配
                   {"origin_query_id": "QB-20261105-1"},
                   {"task_id": "XT-20261105-001"},
                   {"task_id": "RT-"},                       # 空余部
                   {"promoted_to_task_id": ""},
                   {"promoted_to_task_id": "RT-20261105-001 "},
                   {"query_id": 123}):                       # 非字符串
            self.assertNotEqual(ra.validate_id_conventions(**kw), [],
                                f"应拒绝: {kw}")

    def test_record_query_id_date_consistency(self):
        # query_id 日期段须与 created_at 派生一致(B1 make_query_id 派生一致性)
        bad = _ir_with_qid(IR_M, "QB-20261104-001")          # created_at=2026-11-05
        with self.assertRaises(ValueError):
            self.append_basic(self.fresh_archive(), ir=bad)

    def test_promoted_to_task_id_valid_forms_accepted(self):
        arch = self.fresh_archive()
        for pt in ("RT-20261105-001",
                   "RT-2026-06-30~2026-09-30-RD-DIV-001-17788777"):
            status, _ = self.append_basic(arch, ir=_ir_with_qid(
                IR_M, "QB-20261105-00%d" % (1 if pt.endswith("001") else 2)),
                promoted_to_task_id=pt)
            self.assertEqual(status, "written")
        rec = ra.load_query_record("QB-20261105-001", archive_dir=arch)
        self.assertEqual(rec["promoted_to_task_id"], "RT-20261105-001")

    def test_promoted_to_task_id_invalid_rejected(self):
        for pt in ("XT-9", "RT-", "", 123):
            with self.assertRaises(ValueError):
                self.append_basic(self.fresh_archive(), promoted_to_task_id=pt)

    def test_record_lands_in_query_history_collection(self):
        arch = self.fresh_archive()
        _, path = self.append_basic(arch)
        self.assertEqual(path, os.path.join(
            arch, "research_archive", "query_history", "QB-20261105-001.json"))
        self.assertEqual(sorted(os.listdir(os.path.dirname(path))),
                         ["QB-20261105-001.json"])          # 零散落文件/索引文件零产生


# ══ T3 digest 绑定(要点③) ═════════════════════════════════════════════════

class T3DigestBinding(B4TestBase):

    def test_append_stores_r5_digest_literal(self):
        arch = self.fresh_archive()
        _, path = self.append_basic(arch)
        with open(path, 'r', encoding='utf-8') as f:
            rec = json.load(f)
        self.assertEqual(rec["digest_snapshot"], L_DIGEST_A)  # R5 重算值==字面量

    def test_digest_computed_not_declared(self):
        # FIX-01 纪律: API 无 digest 入参,内容绑定必模块内重算
        params = inspect.signature(ra.append_query_record).parameters
        self.assertNotIn("digest", params)
        self.assertNotIn("digest_snapshot", params)

    def test_verify_ok_untampered(self):
        arch = self.fresh_archive()
        snapdir = self.fresh_snapdir(SNAP_A)
        self.append_basic(arch)
        ok, issues = ra.verify_query_record("QB-20261105-001", snapdir,
                                            archive_dir=arch)
        self.assertTrue(ok, issues)
        self.assertEqual(issues, [])
        report = ra.verify_archive(arch, snapdir)
        self.assertEqual(report, {"n_records": 1, "n_ok": 1, "failures": []})

    def test_tampered_snapshot_rejected(self):
        arch = self.fresh_archive()
        snapdir = self.fresh_snapdir(SNAP_A)
        self.append_basic(arch)
        # 篡改快照内容(同名文件改值)→digest 复算不匹配→校验拒绝
        snap = copy.deepcopy(SNAP_A)
        snap["facts"][0]["value"] = 999.0
        self.write_snap(snapdir, snap)
        ok, issues = ra.verify_query_record("QB-20261105-001", snapdir,
                                            archive_dir=arch)
        self.assertFalse(ok)
        self.assertTrue(any("digest不匹配" in s for s in issues), issues)
        report = ra.verify_archive(arch, snapdir)
        self.assertEqual(report["n_ok"], 0)
        self.assertEqual(len(report["failures"]), 1)
        self.assertEqual(report["failures"][0]["query_id"], "QB-20261105-001")

    def test_missing_snapshot_file_rejected(self):
        arch = self.fresh_archive()
        snapdir = self.fresh_snapdir()                       # 空快照目录
        self.append_basic(arch)
        ok, issues = ra.verify_query_record("QB-20261105-001", snapdir,
                                            archive_dir=arch)
        self.assertFalse(ok)
        self.assertTrue(any("快照文件缺失" in s for s in issues), issues)

    def test_corrupt_snapshot_json_rejected(self):
        arch = self.fresh_archive()
        snapdir = self.fresh_snapdir(SNAP_A)
        self.append_basic(arch)
        with open(os.path.join(snapdir,
                               "research_snapshot_20261105.json"), 'w',
                  encoding='utf-8') as f:
            f.write("{NOT JSON")
        ok, issues = ra.verify_query_record("QB-20261105-001", snapdir,
                                            archive_dir=arch)
        self.assertFalse(ok)
        self.assertTrue(any("JSON不可解析" in s for s in issues), issues)

    def test_internal_snapshot_id_mismatch_rejected(self):
        arch = self.fresh_archive()
        snapdir = self.fresh_snapdir(SNAP_A)
        self.append_basic(arch)
        forged = copy.deepcopy(SNAP_A)
        forged["snapshot_id"] = "research_snapshot_20261104"  # 内部身份≠文件名/引用
        with open(os.path.join(snapdir, "research_snapshot_20261105.json"),
                  'w', encoding='utf-8') as f:                 # 同名文件内容被伪改
            json.dump(forged, f, ensure_ascii=False, sort_keys=True, indent=1)
        ok, issues = ra.verify_query_record("QB-20261105-001", snapdir,
                                            archive_dir=arch)
        self.assertFalse(ok)
        self.assertTrue(any("内部snapshot_id" in s for s in issues), issues)

    def test_record_with_wrong_digest_rejected(self):
        arch = self.fresh_archive()
        snapdir = self.fresh_snapdir(SNAP_A)
        _, path = self.append_basic(arch)
        with open(path, 'r', encoding='utf-8') as f:          # 档内登记值被伪改
            rec = json.load(f)
        rec["digest_snapshot"] = "aaaaaaaaaaaaaaaa"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(rec, f, ensure_ascii=False, sort_keys=True, indent=1)
        ok, issues = ra.verify_query_record(rec, snapdir)
        self.assertFalse(ok)
        self.assertTrue(any("digest不匹配" in s for s in issues), issues)

    def test_noncanonical_snapshot_id_rejected(self):
        for bad_sid in ("research_snapshot_20261105_v1",     # v1 非规范(FIX2-04)
                        "research_snapshot_20261105_v02",    # 前导零
                        "research_snapshot_20261105_v0",
                        "research_snapshot_20261105_1"):     # 非法后缀
            snap = copy.deepcopy(SNAP_A)
            snap["snapshot_id"] = bad_sid
            with self.assertRaises(ValueError):
                self.append_basic(self.fresh_archive(), snap=snap)
        self.assertIsNone(ra.parse_snapshot_id("research_snapshot_20261105_v1"))

    def test_snapshot_v2_filename_resolution(self):
        arch = self.fresh_archive()
        snapdir = self.fresh_snapdir(SNAP_B_V2)
        ir = copy.deepcopy(IR_E)
        ir["target_snapshot_id"] = "research_snapshot_20261105_v2"
        ir["metric_bindings"][0]["provenance"]["snapshot_id"] = \
            "research_snapshot_20261105_v2"
        status, path = self.append_basic(arch, ir=ir, snap=SNAP_B_V2)
        self.assertEqual(status, "written")
        with open(path, 'r', encoding='utf-8') as f:
            self.assertEqual(json.load(f)["digest_snapshot"], L_DIGEST_B_V2)
        ok, issues = ra.verify_query_record("QB-20261105-001", snapdir,
                                            archive_dir=arch)
        self.assertTrue(ok, issues)                          # vN 文件名解析正确


# ══ T4 记录 schema 与确定性摘要 ═══════════════════════════════════════════

class T4RecordSchemaAndSummary(B4TestBase):

    @staticmethod
    def _valid_record():
        return {"record_type": "query_history",
                "query_id": "QB-20261105-001",
                "created_at": "2026-11-05T10:00:00+08:00",
                "mode": "B",
                "question_text": "美元兑日元最近走势如何?",
                "as_of": None,
                "snapshot_id": "research_snapshot_20261105",
                "digest_snapshot": L_DIGEST_A,
                "ir": copy.deepcopy(IR_M),
                "ir_stage": "mapped",
                "answer_summary": copy.deepcopy(L_SUMMARY_MAPPED),
                "promoted_to_task_id": None,
                "archived_at": L_ARCHIVED_AT}

    def test_valid_record_passes(self):
        self.assertEqual(ra.validate_query_record(self._valid_record()), [])

    def test_missing_key_issues(self):
        rec = self._valid_record()
        del rec["digest_snapshot"]
        issues = ra.validate_query_record(rec)
        self.assertTrue(any("缺字段digest_snapshot" in s for s in issues), issues)

    def test_wrong_record_type_and_mode_issues(self):
        rec = self._valid_record()
        rec["record_type"] = "research_tasks"
        self.assertTrue(ra.validate_query_record(rec))
        rec = self._valid_record()
        rec["mode"] = "A"
        self.assertTrue(ra.validate_query_record(rec))

    def test_echo_divergence_issues(self):
        rec = self._valid_record()
        rec["question_text"] = "与IR不一致的问题文本"
        issues = ra.validate_query_record(rec)
        self.assertTrue(any("echo字段question_text" in s for s in issues), issues)
        rec = self._valid_record()
        rec["as_of"] = "2026-11-01"
        self.assertTrue(any("echo字段as_of" in s
                            for s in ra.validate_query_record(rec)))

    def test_ir_stage_detection_on_append(self):
        arch = self.fresh_archive()
        self.append_basic(arch, ir=copy.deepcopy(IR_M),
                          execution=None)                     # mapped
        rec = ra.load_query_record("QB-20261105-001", archive_dir=arch)
        self.assertEqual(rec["ir_stage"], "mapped")
        arch2 = self.fresh_archive()
        self.append_basic(arch2, ir=copy.deepcopy(IR_E),
                          execution=copy.deepcopy(EXEC_OK))  # executed
        rec2 = ra.load_query_record("QB-20261105-001", archive_dir=arch2)
        self.assertEqual(rec2["ir_stage"], "executed")

    def test_invalid_both_stages_fail_loud(self):
        broken = copy.deepcopy(IR_M)
        broken["mode"] = "Z"                                  # 双阶段皆非法
        with self.assertRaises(ValueError):
            self.append_basic(self.fresh_archive(), ir=broken)

    def test_answer_summary_literals_mapped(self):
        self.assertEqual(ra.build_answer_summary(copy.deepcopy(IR_M), "mapped"),
                         L_SUMMARY_MAPPED)

    def test_answer_summary_literals_executed_values(self):
        self.assertEqual(ra.build_answer_summary(copy.deepcopy(IR_E), "executed",
                                                 execution=EXEC_OK),
                         L_SUMMARY_EXEC)

    def test_answer_summary_refusal_propagated(self):
        self.assertEqual(ra.build_answer_summary(copy.deepcopy(IR_M), "mapped",
                                                 execution=EXEC_REFUSAL),
                         L_SUMMARY_REFUSAL)

    def test_target_snapshot_consistency_enforced(self):
        # executed IR 绑定 A 档而注入 B 快照 → fail-loud(绑定后不可变,L177)
        with self.assertRaises(ValueError):
            self.append_basic(self.fresh_archive(), ir=copy.deepcopy(IR_E),
                              snap=SNAP_B_V2)
        # mapped 期 target=None → 绑定注入快照合法
        status, _ = self.append_basic(self.fresh_archive(), ir=copy.deepcopy(IR_M),
                                      snap=SNAP_B_V2)
        self.assertEqual(status, "written")

    def test_execution_ir_mismatch_fail_loud(self):
        exec_bad = {"ir": copy.deepcopy(IR_E), "values": {}, "snapshot_id":
                    "research_snapshot_20261105", "gate_status": "PASS"}
        with self.assertRaises(ValueError):
            self.append_basic(self.fresh_archive(), ir=copy.deepcopy(IR_M),
                              execution=exec_bad)             # execution.ir≠ir

    def test_archived_at_injection_determinism(self):
        arch = self.fresh_archive()
        self.append_basic(arch, archived_at=L_ARCHIVED_AT)
        rec = ra.load_query_record("QB-20261105-001", archive_dir=arch)
        self.assertEqual(rec["archived_at"], L_ARCHIVED_AT)

    def test_record_ir_stage_invalid_combo_issues(self):
        rec = self._valid_record()
        rec["ir"] = copy.deepcopy(IR_E)                       # executed IR 标 mapped
        rec["ir_stage"] = "mapped"
        self.assertTrue(ra.validate_query_record(rec))        # RESOLVED/COMPUTED 禁止于 mapped(D-B1-01)

    def test_list_query_records_ymd_filter(self):
        arch = self.fresh_archive()
        self.append_basic(arch)
        self.append_basic(arch, ir=_ir_day2(IR_M))
        self.assertEqual(ra.list_query_records(archive_dir=arch),
                         ["QB-20261105-001", "QB-20261106-001"])
        self.assertEqual(ra.list_query_records(archive_dir=arch, ymd="20261105"),
                         ["QB-20261105-001"])


# ══ T5 复用与纯度锁 ═══════════════════════════════════════════════════════

class T5WiringPurity(B4TestBase):

    def test_reuse_surface_lock(self):
        # 复用面正向锁: qir(B1)+rp(R5) 真实调用(禁复制分叉)
        self.assertIn("import e2eb_query_ir", MODULE_SRC)
        self.assertIn("import research_provenance", MODULE_SRC)
        self.assertIn("rp.digest_snapshot", MODULE_SRC)
        # digest 算法零复制(自实现 sha256 截断=分叉红旗)
        self.assertNotIn("hexdigest()[:16]", MODULE_SRC)
        self.assertNotIn("hexdigest()[: 16]", MODULE_SRC)

    def test_no_raw_collection_paths(self):
        # 原始采集档文件名构造面零存在(AC-07.1;快照解析仅经 snapshot_id 规范分解)
        for pat in FORBIDDEN_RAW_PREFIXES:
            self.assertNotIn(pat, MODULE_SRC, f"源码含原始采集档文件名模式: {pat}")

    def test_open_surface_whitelisted(self):
        # 文件打开面恰3处: 记录原子写/记录读回/快照加载(D-B4-08登记面)
        # 批2 WI6(2026-11-09)显式扩面: +sidecar 原子写/sidecar 读回 = 恰5处
        self.assertEqual(MODULE_SRC.count("open("), 5)
        for func in ("append_query_record", "load_query_record",
                     "_load_snapshot_for_binding", "write_research_full",
                     "load_research_full"):
            self.assertIn("open(", inspect.getsource(getattr(ra, func)))

    def test_no_network_imports(self):
        for pat in ("import socket", "import requests", "import urllib",
                    "urlopen", "import http"):
            self.assertNotIn(pat, MODULE_SRC)

    def test_module_api_surface_whitelist(self):
        public_funcs = {n for n in dir(ra) if not n.startswith('_')
                        and callable(getattr(ra, n))
                        and getattr(getattr(ra, n), '__module__', None) == ra.__name__}
        self.assertTrue(public_funcs.issubset(ALLOWED_PUBLIC_FUNCS),
                        f"白名单外公共函数: {public_funcs - ALLOWED_PUBLIC_FUNCS}")

    def test_default_archive_dir_isolated(self):
        self.assertTrue(ra.DEFAULT_ARCHIVE_DIR.endswith(
            os.path.join("data", "research", "research_archive")))
        self.assertNotIn("AI内容", ra.DEFAULT_ARCHIVE_DIR)
        self.assertNotIn("AI内容", MODULE_SRC)


# ══ T6 fail-loud ══════════════════════════════════════════════════════════

class T6FailLoud(B4TestBase):

    def test_non_dict_snapshot_rejected(self):
        with self.assertRaises(ValueError):
            self.append_basic(self.fresh_archive(), snap={"target_date": "20261105"})

    def test_snapshot_missing_id_rejected(self):
        snap = {"target_date": "20261105", "facts": []}
        with self.assertRaises(ValueError):
            self.append_basic(self.fresh_archive(), snap=snap)

    def test_load_missing_record_raises(self):
        with self.assertRaises(FileNotFoundError):
            ra.load_query_record("QB-20261105-099", archive_dir=self.fresh_archive())

    def test_verify_nonexistent_record_raises(self):
        with self.assertRaises(FileNotFoundError):
            ra.verify_query_record("QB-20261105-099", self.fresh_snapdir(SNAP_A),
                                   archive_dir=self.fresh_archive())


if __name__ == '__main__':
    unittest.main(verbosity=2)
