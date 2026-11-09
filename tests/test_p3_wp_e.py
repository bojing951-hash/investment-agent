#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P3-WP-E 测试件: 个人流程整合接口(#37 挂靠;P3 收尾层第 5 实现包)。

数据面: 全合成 fixture 唯一数据源(零真实数据/零网络/零模型调用/零凭证);
预期值=黄金字面量硬编码(六面 sha256+三渲染面全文),独立首原理预计算件
/tmp/p3-wp-e/fixture_and_golden.py(零被测模块 import)与模块实跑三方
一致(交叉裁定 ALL MATCH,/tmp/p3-wp-e/cross_check.py)。

覆盖面(DESIGN §7 WP-P3-E 行 L194-198 验收要点+REPORT §零.4/§零.5
登记值逐项): DP-9 三接口/三红线(零主动采集/来源等级隔离/用户数据零落
LIVE)/append-only 档纪律/守卫四面(data+daily 快照纪律+LIVE 根四组件
序列+写入域)/AST 纯度(import 白名单+open 模式记账+禁网令牌+主流程
上游只读)/负向敏感性/零回写/确定性序列化/免责承载。
"""
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from unittest import mock

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(TESTS_DIR)
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
sys.path.insert(0, SCRIPTS_DIR)
import personal_flow_integration as pfi       # 被测模块  # noqa: E402
import report_quality_review as rqr           # 上游复用面(WP-P3-D)  # noqa: E402

MODULE_PATH = os.path.join(SCRIPTS_DIR, "personal_flow_integration.py")

# ══ 合成 fixture 字面量(唯一数据源;与首原理件同字面) ═══════════════════

FX_A1_DATE, FX_A1_ASSET, FX_A1_VIEW, FX_A1_BASIS = (
    "2026-01-05", "USDCNH", "美元/人民币短线偏强",
    "日线级别: 前高突破后回踩不破(个人技术分析)")
FX_A2_DATE, FX_A2_ASSET, FX_A2_VIEW, FX_A2_BASIS = (
    "2026-01-05", "XAUUSD", "黄金高位整理,趋势未破坏",
    "均线多头排列,回踩 20 日线(个人技术分析)")
FX_N1 = ("2026-01-05", "QB-20260105-001",
         ["USDCNH_close_日线", "XAUUSD_close_日线"])
FX_N2 = ("2026-01-12", "QB-20260112-003", ["US10Y_yield_日线"])

EXPECT_A1 = {"annotation_id": "ANN-20260105-001", "asset": "USDCNH",
             "basis": FX_A1_BASIS, "date": "2026-01-05",
             "schema_version": 1, "view": FX_A1_VIEW}
EXPECT_A2 = {"annotation_id": "ANN-20260105-002", "asset": "XAUUSD",
             "basis": FX_A2_BASIS, "date": "2026-01-05",
             "schema_version": 1, "view": FX_A2_VIEW}
EXPECT_N1 = {"archive_key": FX_N1[1], "date": FX_N1[0],
             "metric_refs": list(FX_N1[2]), "note_id": "NOTE-20260105-001",
             "schema_version": 1, "source_level": "个人观察"}
EXPECT_N2 = {"archive_key": FX_N2[1], "date": FX_N2[0],
             "metric_refs": list(FX_N2[2]), "note_id": "NOTE-20260112-002",
             "schema_version": 1, "source_level": "个人观察"}

# 接口(c) 合成 WP-D 编排面输出 fixture(结构面锚 rqr.STATS_SCHEMA_VERSION)
QUALITY_REVIEW_OUTPUT = {
    "statistics": {
        "schema_version": 1, "as_of": "2026-02-01", "window_kind": "monthly",
        "window_start": "2026-01-01", "window_end": "2026-01-31",
        "dimension_count": 5,
    },
    "briefing": ("【质量简报·合成 fixture】窗口 2026-01-01~2026-01-31(月度);"
                 "五维计量呈现;本简报为 WP-E 测试合成件,非真实产物。"),
    "suggestions": [
        {"dimension": "coverage", "summary": "覆盖度处于阈值之上(合成)",
         "requires_user_confirmation": True},
        {"dimension": "timeliness", "summary": "同日落档时效达标(合成)",
         "requires_user_confirmation": True},
    ],
    "prediction_review": {
        "statistics": {
            "counts": {"hit": 2, "hit_rate": 2 / 3, "inconclusive": 1,
                       "miss": 1, "not_yet_triggered_terminal": 1},
            "error_patterns": {
                "direction_error": ["QB-20251208-001"],
                "horizon_error": [], "magnitude_error": ["QB-20260105-001"],
                "unclassifiable": []},
        },
    },
}

# ══ 黄金字面量(六面 sha256;首原理件/测试件/模块实跑三方一致) ═══════════

GOLDEN_SHAS = {
    "G1_annotation_view_render":
        "3379001e4e4cc6d1322d8fcfd7cb1a871ca95293a364cc15cebbdd81bfe8c3c2",
    "G2_note_refs_render":
        "c350686f047ec18348416acc5d80f33cdeb7da2a794b46342d13a924719aceb0",
    "G3_annotation_archive":
        "146c74b89c33daef226f86a7520c63b83d50233b4d32031434cf1dfc2d38ff13",
    "G4_note_archive":
        "d9112cec3a7d1bdb29e54274d4882640515f16ea81ad848377476388f8d365a4",
    "G5_export_document":
        "dea070d649cb321f2a18c19684817cc60ee1abaf45c8b6383b9873d3c307288f",
    "G6_export_briefing_render":
        "20a5c876f7acac9d2ffea76f2ed3cf30e5ae29b31ebf73ff9cf40ade6774a59b",
}

GOLDEN_ANNOTATION_VIEW = "\n".join([
    "个人技术分析标注视图(接口(a);旁路标注档 append-only;"
    "零主动采集: 系统不采集用户私有流程数据,一切输入=用户主动推送/标注)",
    "标注 2 条:",
    "- [ANN-20260105-001] 2026-01-05 资产=USDCNH 观点=美元/人民币短线偏强 "
    "依据=日线级别: 前高突破后回踩不破(个人技术分析)",
    "- [ANN-20260105-002] 2026-01-05 资产=XAUUSD 观点=黄金高位整理,趋势未破坏"
    " 依据=均线多头排列,回踩 20 日线(个人技术分析)",
    "标注为用户主动填写的个人观点,系统零采集零核验零背书"
    "(零主动采集红线);不构成投资建议(禁交易/禁仓位/禁收益承诺)",
])

GOLDEN_NOTE_REFS_VIEW = "\n".join([
    "个人研究笔记引用视图(接口(b);登记格式=档键+指标引用+日期;"
    "来源等级隔离: 个人观察≠程序验证证据,证据分级外单列,不参与星级与门禁)",
    "引用 1 条:",
    "- [NOTE-20260105-001] 2026-01-05 档键=QB-20260105-001"
    " 指标引用=USDCNH_close_日线,XAUUSD_close_日线 "
    "来源等级=个人观察(证据分级外,不参与星级与门禁核验)",
    "个人观察=用户主动导入的笔记引用,来源等级与程序验证证据严格"
    "隔离(证据分级外,不参与星级与门禁核验);不构成投资建议"
    "(禁交易/禁仓位/禁收益承诺)",
])

GOLDEN_EXPORT_BRIEFING = "\n".join([
    "个人复盘结论导出(接口(c);系统→用户单向导出·零回读;"
    "用户数据零落 LIVE: 落 DEV 仓或用户指定路径)",
    "窗口: 2026-01-01 ~ 2026-01-31(monthly;as_of=2026-02-01)",
    "── 质量简报(§6.1 产物,WP-P3-D 原样承载)──",
    "【质量简报·合成 fixture】窗口 2026-01-01~2026-01-31(月度);"
    "五维计量呈现;本简报为 WP-E 测试合成件,非真实产物。",
    "── 错误模式统计(§5 产物,WP-P3-C 原样承载)──",
    "窗内终态: hit=2 miss=1 inconclusive=1(单列) not_yet_triggered终态=1"
    "(单列); 命中率=hit/(hit+miss)=0.6667(DP-6 上游登记口径)",
    "错误模式: 方向错误=QB-20251208-001 | 期限错误= "
    "| 幅度错误=QB-20260105-001 | 无法归类(单列)=",
    "校准建议清单: 2 条(注入提示词须用户确认[DP-8],"
    "requires_user_confirmation=true 标记随上游原样携带,本导出零注入)",
    "本导出为系统→用户个人复盘流程的单向材料(零回读: 用户流程"
    "数据不经本接口回流);不构成投资建议(禁交易/禁仓位/禁收益承诺)",
])


def _sha(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _tree_shas(root):
    out = {}
    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            p = os.path.join(dirpath, fn)
            with open(p, "rb") as f:
                out[p] = _sha(f.read())
    return out


def _build_golden_fixture(sb):
    """模块实跑重建黄金六面(与首原理件同字面 fixture)。"""
    ann = os.path.join(sb, "annotation_archive.jsonl")
    note = os.path.join(sb, "note_archive.jsonl")
    r1 = pfi.append_annotation(
        ann, pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET, FX_A1_VIEW,
                                  FX_A1_BASIS), user_root=sb)
    r2 = pfi.append_annotation(
        ann, pfi.build_annotation(FX_A2_DATE, FX_A2_ASSET, FX_A2_VIEW,
                                  FX_A2_BASIS), user_root=sb)
    r3 = pfi.append_note_reference(
        note, pfi.build_note_reference(*FX_N1), user_root=sb)
    pfi.append_note_reference(
        note, pfi.build_note_reference(*FX_N2, note_id="NOTE-20260112-002"),
        user_root=sb)
    doc = pfi.build_export_document(QUALITY_REVIEW_OUTPUT)
    surfaces = {
        "G1_annotation_view_render":
            pfi.render_annotation_view([r1, r2]),
        "G2_note_refs_render": pfi.render_note_references([r3]),
        "G3_annotation_archive": open(ann, "rb").read(),
        "G4_note_archive": open(note, "rb").read(),
        "G5_export_document": pfi.dump_export_document(doc),
        "G6_export_briefing_render": pfi.render_export_briefing(doc),
    }
    return surfaces


class _SandboxCase(unittest.TestCase):
    def setUp(self):
        self.sb = tempfile.mkdtemp(prefix="p3wp-e-test-")
        self.ann = os.path.join(self.sb, "annotation_archive.jsonl")
        self.note = os.path.join(self.sb, "note_archive.jsonl")

    def tearDown(self):
        for dirpath, _dirs, files in os.walk(self.sb, topdown=False):
            for fn in files:
                os.remove(os.path.join(dirpath, fn))
            os.rmdir(dirpath)


# ══ 1. 黄金双源(六面 sha+三渲染全文) ═════════════════════════════════════

class TestGoldenFirstPrinciples(_SandboxCase):
    def test_six_surface_shas_match_golden_literals(self):
        surfaces = _build_golden_fixture(self.sb)
        for name, data in surfaces.items():
            self.assertEqual(_sha(data), GOLDEN_SHAS[name], name)

    def test_annotation_view_golden_full_text(self):
        surfaces = _build_golden_fixture(self.sb)
        self.assertEqual(surfaces["G1_annotation_view_render"],
                         GOLDEN_ANNOTATION_VIEW)

    def test_note_refs_view_golden_full_text(self):
        surfaces = _build_golden_fixture(self.sb)
        self.assertEqual(surfaces["G2_note_refs_render"],
                         GOLDEN_NOTE_REFS_VIEW)

    def test_export_briefing_golden_full_text(self):
        surfaces = _build_golden_fixture(self.sb)
        self.assertEqual(surfaces["G6_export_briefing_render"],
                         GOLDEN_EXPORT_BRIEFING)

    def test_golden_fixture_records_expected_values(self):
        pfi.append_annotation(
            self.ann, pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET, FX_A1_VIEW,
                                           FX_A1_BASIS), user_root=self.sb)
        pfi.append_annotation(
            self.ann, pfi.build_annotation(FX_A2_DATE, FX_A2_ASSET, FX_A2_VIEW,
                                           FX_A2_BASIS), user_root=self.sb)
        self.assertEqual(pfi.read_annotations(self.ann),
                         [EXPECT_A1, EXPECT_A2])
        pfi.append_note_reference(
            self.note, pfi.build_note_reference(*FX_N1), user_root=self.sb)
        pfi.append_note_reference(
            self.note, pfi.build_note_reference(
                *FX_N2, note_id="NOTE-20260112-002"), user_root=self.sb)
        self.assertEqual(pfi.read_note_references(self.note),
                         [EXPECT_N1, EXPECT_N2])


# ══ 2. DP/参数登记锚定 ═══════════════════════════════════════════════════

class TestDPParamRegistration(_SandboxCase):
    def test_dp9_interface_set_and_approval_marker(self):
        self.assertEqual(pfi.DP9_INTERFACE_SET,
                         ("annotation", "note_reference", "export"))
        self.assertEqual(pfi.DP9_USER_APPROVAL,
                         "user_approved_2026-11-08_immediate")
        self.assertEqual(
            pfi.registered_dp_values()["DP-9"],
            "annotation+note_reference+export"
            "@user_approved_2026-11-08_immediate")

    def test_schema_versions_and_markers(self):
        self.assertEqual(pfi.ANNOTATION_SCHEMA_VERSION, 1)
        self.assertEqual(pfi.NOTE_SCHEMA_VERSION, 1)
        self.assertEqual(pfi.EXPORT_SCHEMA_VERSION, 1)
        self.assertEqual(pfi.ANNOTATION_MARKER, "ANN-")
        self.assertEqual(pfi.NOTE_MARKER, "NOTE-")
        self.assertEqual(pfi.ID_SEQ_MIN, 1)
        self.assertEqual(pfi.ID_SEQ_MAX, 999)

    def test_field_closed_sets(self):
        self.assertEqual(pfi.registered_param_values()["annotation_fields"],
                         ("annotation_id", "asset", "basis", "date",
                          "schema_version", "view"))
        self.assertEqual(pfi.registered_param_values()["note_fields"],
                         ("archive_key", "date", "metric_refs", "note_id",
                          "schema_version", "source_level"))
        self.assertEqual(pfi.registered_param_values()["export_fields"],
                         ("as_of", "error_pattern_statistics", "note",
                          "quality_briefing", "schema_version", "suggestions",
                          "window_end", "window_kind", "window_start"))

    def test_guard_component_registration(self):
        self.assertEqual(pfi.registered_param_values()["live_guard_seq"],
                         ("AI内容", "🤖_AI投资项目", "每周宏观追踪",
                          "investment-agent"))
        self.assertEqual(pfi.registered_param_values()["raw_dir_guard"],
                         ("data", "daily"))

    def test_registered_param_values_full_mirror(self):
        live = pfi.registered_param_values()
        for key in ("interface_set", "annotation_schema_version",
                    "note_schema_version", "export_schema_version",
                    "annotation_marker", "note_marker", "note_source_level",
                    "annotation_fields", "note_fields", "export_fields",
                    "live_guard_seq", "raw_dir_guard"):
            self.assertIn(key, live)

    def test_dp_selfcheck_passes(self):
        self.assertIs(pfi.dp_selfcheck(), True)

    def test_monkeypatch_schema_version_detected(self):
        with mock.patch.object(pfi, "ANNOTATION_SCHEMA_VERSION", 2):
            with self.assertRaises(AssertionError):
                pfi.dp_selfcheck()

    def test_monkeypatch_interface_set_detected(self):
        with mock.patch.object(pfi, "DP9_INTERFACE_SET",
                               ("annotation",)):
            with self.assertRaises(AssertionError):
                pfi.dp_selfcheck()

    def test_monkeypatch_source_level_detected(self):
        with mock.patch.object(pfi, "NOTE_SOURCE_LEVEL", "增长"):
            with self.assertRaises(AssertionError):
                pfi.dp_selfcheck()


# ══ 3. 规范形日期守卫(零 datetime 导入,纯日历判定) ══════════════════════

class TestDateGuard(_SandboxCase):
    def test_valid_forms(self):
        for s in ("2026-01-05", " 2026-01-05 ", "2024-02-29", "2000-02-29",
                  "0004-01-01", "2026-12-31"):
            self.assertEqual(pfi._parse_iso_date(s), s.strip()[:10], s)

    def test_timestamp_truncation_family_precedent(self):
        self.assertEqual(pfi._parse_iso_date("2026-01-05T12:00:00"),
                         "2026-01-05")

    def test_reject_compact_and_week_forms(self):
        for s in ("20260105", "2026-1-05", "2026-01-5", "2026/01/05",
                  "2026-W01-1", "20260105T00"):
            self.assertIsNone(pfi._parse_iso_date(s), s)

    def test_trailing_content_tolerated_by_family_precedent(self):
        # R040 续段截断语义: 首十位规范即收,尾随内容不扩大拒绝面(登记口径)
        for s in ("2026-01-05T12:00:00", "2026-01-05 xyz", "2026-01-05\tz"):
            self.assertEqual(pfi._parse_iso_date(s), "2026-01-05", s)

    def test_reject_calendar_illegal(self):
        for s in ("2026-13-01", "2026-00-10", "2026-01-00", "2026-01-32",
                  "2026-02-30", "2026-02-29", "2100-02-29", "0000-01-01"):
            self.assertIsNone(pfi._parse_iso_date(s), s)

    def test_leap_century_rule(self):
        self.assertEqual(pfi._parse_iso_date("2400-02-29"), "2400-02-29")
        self.assertIsNone(pfi._parse_iso_date("1900-02-29"))

    def test_reject_non_string(self):
        for s in (None, 123, 20260105, ["2026-01-05"], b"2026-01-05"):
            self.assertIsNone(pfi._parse_iso_date(s), repr(s))

    def test_require_iso_date_raises_with_field_name(self):
        with self.assertRaises(ValueError) as cm:
            pfi.build_annotation("2026-1-5", "USDCNH", "v", "b")
        self.assertIn("annotation#date", str(cm.exception))

    def test_ascii_digit_strictness(self):
        self.assertIsNone(pfi._parse_iso_date("２０２６-０１-０５"))
        self.assertIsNone(pfi._parse_iso_date("2026-01-0５"))


# ══ 4. 档键 ID 族(ANN-/NOTE-YYYYMMDD-NNN) ═══════════════════════════════

class TestRecordKeys(_SandboxCase):
    def test_key_format(self):
        self.assertEqual(pfi.annotation_record_key("2026-01-05", 1),
                         "ANN-20260105-001")
        self.assertEqual(pfi.annotation_record_key("2026-01-05", 999),
                         "ANN-20260105-999")
        self.assertEqual(pfi.note_record_key("2026-01-05", 42),
                         "NOTE-20260105-042")

    def test_seq_bounds(self):
        for bad in (0, -1, 1000, True, False, "1", 1.0, None):
            with self.assertRaises(ValueError, msg=repr(bad)):
                pfi.annotation_record_key("2026-01-05", bad)

    def test_key_requires_canonical_date(self):
        with self.assertRaises(ValueError):
            pfi.annotation_record_key("20260105", 1)

    def test_explicit_id_form_enforced(self):
        for bad in ("ANN-20260105-1", "ANN-20260105-0001",
                    "NOTE-20260105-001", "ann-20260105-001",
                    "ANN-20260106-001", "ANN-20260105-001x", ""):
            with self.assertRaises(ValueError, msg=repr(bad)):
                pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET, FX_A1_VIEW,
                                     FX_A1_BASIS, annotation_id=bad)

    def test_note_explicit_id_form_enforced(self):
        for bad in ("NOTE-20260112-2", "ANN-20260112-002",
                    "NOTE-20260113-002", "NOTE-20260112-0002"):
            with self.assertRaises(ValueError, msg=repr(bad)):
                pfi.build_note_reference(*FX_N2, note_id=bad)


# ══ 5. 接口(a) 标注 ══════════════════════════════════════════════════════

class TestAnnotationInterface(_SandboxCase):
    def test_build_returns_closed_field_record(self):
        rec = pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET, FX_A1_VIEW,
                                   FX_A1_BASIS)
        self.assertEqual(set(rec), set(EXPECT_A1))
        self.assertEqual(rec["annotation_id"], None)
        self.assertEqual(rec["schema_version"], 1)

    def test_build_is_pure_zero_write(self):
        before = _tree_shas(self.sb)
        pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET, FX_A1_VIEW, FX_A1_BASIS)
        self.assertEqual(_tree_shas(self.sb), before)

    def test_blank_fields_rejected(self):
        for bad_asset in ("", "   ", None, 123):
            with self.assertRaises(ValueError, msg=repr(bad_asset)):
                pfi.build_annotation(FX_A1_DATE, bad_asset, FX_A1_VIEW,
                                     FX_A1_BASIS)
        for bad_view in ("", "  "):
            with self.assertRaises(ValueError):
                pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET, bad_view,
                                     FX_A1_BASIS)
        for bad_basis in ("", "  "):
            with self.assertRaises(ValueError):
                pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET, FX_A1_VIEW,
                                     bad_basis)

    def test_extra_field_hand_dict_rejected(self):
        rec = dict(EXPECT_A1)
        rec["confidence"] = 5
        with self.assertRaises(ValueError):
            pfi.append_annotation(self.ann, rec, user_root=self.sb)

    def test_wrong_schema_version_rejected(self):
        rec = dict(EXPECT_A1)
        rec["schema_version"] = 2
        with self.assertRaises(ValueError):
            pfi.append_annotation(self.ann, rec, user_root=self.sb)

    def test_append_assigns_auto_id_and_reads_back(self):
        stored = pfi.append_annotation(
            self.ann, pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET, FX_A1_VIEW,
                                           FX_A1_BASIS), user_root=self.sb)
        self.assertEqual(stored, EXPECT_A1)
        self.assertEqual(pfi.read_annotations(self.ann), [EXPECT_A1])

    def test_append_explicit_id_passthrough(self):
        rec = pfi.build_annotation("2026-02-10", "US10Y",
                                   "收益率区间上沿,做多仓位谨慎",
                                   "区间震荡框架(个人技术分析)",
                                   annotation_id="ANN-20260210-007")
        stored = pfi.append_annotation(self.ann, rec, user_root=self.sb)
        self.assertEqual(stored["annotation_id"], "ANN-20260210-007")

    def test_read_missing_archive_returns_empty(self):
        self.assertEqual(
            pfi.read_annotations(os.path.join(self.sb, "absent.jsonl")), [])


# ══ 6. 接口(b) 笔记引用 ══════════════════════════════════════════════════

class TestNoteInterface(_SandboxCase):
    def test_build_forces_source_level(self):
        rec = pfi.build_note_reference(*FX_N1)
        self.assertEqual(rec["source_level"], "个人观察")
        self.assertEqual(set(rec), set(EXPECT_N1))

    def test_source_level_not_a_user_parameter(self):
        with self.assertRaises(TypeError):
            pfi.build_note_reference(*FX_N1, source_level="程序验证")

    def test_metric_refs_copied_not_aliased(self):
        refs = ["USDCNH_close_日线"]
        rec = pfi.build_note_reference(FX_N1[0], FX_N1[1], refs)
        refs.append("污染")
        self.assertEqual(rec["metric_refs"], ["USDCNH_close_日线"])

    def test_metric_refs_validation(self):
        for bad in ([], "USDCNH_close_日线", ["", "  "], [1, 2],
                    ["ok", None], ("a", "b")):
            with self.assertRaises(ValueError, msg=repr(bad)):
                pfi.build_note_reference(FX_N1[0], FX_N1[1], bad)

    def test_blank_archive_key_rejected(self):
        for bad in ("", "  ", None, 5):
            with self.assertRaises(ValueError, msg=repr(bad)):
                pfi.build_note_reference(FX_N1[0], bad, FX_N1[2])

    def test_hand_dict_wrong_source_level_rejected(self):
        rec = dict(EXPECT_N1)
        rec["source_level"] = "程序验证"
        with self.assertRaises(ValueError):
            pfi.append_note_reference(self.note, rec, user_root=self.sb)

    def test_append_auto_and_explicit_ids(self):
        s1 = pfi.append_note_reference(
            self.note, pfi.build_note_reference(*FX_N1), user_root=self.sb)
        self.assertEqual(s1, EXPECT_N1)
        s2 = pfi.append_note_reference(
            self.note, pfi.build_note_reference(*FX_N2,
                                                note_id="NOTE-20260112-002"),
            user_root=self.sb)
        self.assertEqual(s2, EXPECT_N2)
        self.assertEqual(pfi.read_note_references(self.note),
                         [EXPECT_N1, EXPECT_N2])

    def test_read_missing_archive_returns_empty(self):
        self.assertEqual(
            pfi.read_note_references(os.path.join(self.sb, "absent.jsonl")),
            [])


# ══ 7. append-only 档纪律 ═══════════════════════════════════════════════

class TestAppendOnly(_SandboxCase):
    def _seed(self, records, path=None):
        path = path or self.ann
        with open(path, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, sort_keys=True,
                                   ensure_ascii=False) + "\n")

    def test_same_day_monotonic_seq(self):
        pfi.append_annotation(
            self.ann, pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET, FX_A1_VIEW,
                                           FX_A1_BASIS), user_root=self.sb)
        s2 = pfi.append_annotation(
            self.ann, pfi.build_annotation(FX_A2_DATE, FX_A2_ASSET, FX_A2_VIEW,
                                           FX_A2_BASIS), user_root=self.sb)
        self.assertEqual(s2["annotation_id"], "ANN-20260105-002")

    def test_different_day_independent_seq(self):
        pfi.append_annotation(
            self.ann, pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET, FX_A1_VIEW,
                                           FX_A1_BASIS), user_root=self.sb)
        s2 = pfi.append_annotation(
            self.ann, pfi.build_annotation("2026-01-06", "US10Y", "v",
                                           "b"), user_root=self.sb)
        self.assertEqual(s2["annotation_id"], "ANN-20260106-001")

    def test_duplicate_explicit_id_rejected(self):
        pfi.append_annotation(
            self.ann, pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET, FX_A1_VIEW,
                                           FX_A1_BASIS,
                                           annotation_id="ANN-20260105-007"),
            user_root=self.sb)
        with self.assertRaises(ValueError):
            pfi.append_annotation(
                self.ann, pfi.build_annotation(FX_A1_DATE, "XAUUSD", "v2",
                                               "b2",
                                               annotation_id=
                                               "ANN-20260105-007"),
                user_root=self.sb)

    def test_append_preserves_existing_bytes_prefix(self):
        base_line = json.dumps(EXPECT_A1, sort_keys=True,
                               ensure_ascii=False) + "\n"
        self._seed([EXPECT_A1])
        before = open(self.ann, "rb").read()
        pfi.append_annotation(
            self.ann, pfi.build_annotation("2026-01-06", "US10Y", "v", "b"),
            user_root=self.sb)
        after = open(self.ann, "rb").read()
        self.assertTrue(after.startswith(before))
        self.assertEqual(after[len(before):].decode("utf-8"),
                         json.dumps({"annotation_id": "ANN-20260106-001",
                                     "asset": "US10Y", "basis": "b",
                                     "date": "2026-01-06",
                                     "schema_version": 1, "view": "v"},
                                    sort_keys=True, ensure_ascii=False)
                         + "\n")
        self.assertEqual(before.decode("utf-8"), base_line)

    def test_archive_is_jsonl_sorted_keys_lines(self):
        _build_golden_fixture(self.sb)
        for ln in open(self.ann, encoding="utf-8").read().splitlines():
            obj = json.loads(ln)
            self.assertEqual(json.dumps(obj, sort_keys=True,
                                        ensure_ascii=False), ln)

    def test_corrupt_duplicate_id_fail_loud_on_read(self):
        self._seed([EXPECT_A1, EXPECT_A1])
        with self.assertRaises(ValueError) as cm:
            pfi.read_annotations(self.ann)
        self.assertIn("重复", str(cm.exception))

    def test_corrupt_duplicate_id_fail_loud_on_append(self):
        self._seed([EXPECT_A1, EXPECT_A1])
        with self.assertRaises(ValueError):
            pfi.append_annotation(
                self.ann, pfi.build_annotation("2026-02-01", "USDCNH", "v",
                                               "b"), user_root=self.sb)

    def test_same_day_seq_overflow_fail_loud(self):
        top = dict(EXPECT_A1, annotation_id="ANN-20260105-999")
        self._seed([EXPECT_A1, top])
        with self.assertRaises(ValueError) as cm:
            pfi.append_annotation(
                self.ann, pfi.build_annotation(FX_A1_DATE, "USDCNH", "v",
                                               "b"), user_root=self.sb)
        self.assertIn("溢出", str(cm.exception))

    def test_note_archive_append_only(self):
        pfi.append_note_reference(
            self.note, pfi.build_note_reference(*FX_N1), user_root=self.sb)
        before = open(self.note, "rb").read()
        pfi.append_note_reference(
            self.note, pfi.build_note_reference(*FX_N2,
                                                note_id="NOTE-20260112-002"),
            user_root=self.sb)
        after = open(self.note, "rb").read()
        self.assertTrue(after.startswith(before))
        self.assertEqual(_sha(after), GOLDEN_SHAS["G4_note_archive"])


# ══ 8. 档读取 fail-loud ══════════════════════════════════════════════════

class TestLoadRecordsFailLoud(_SandboxCase):
    def _write(self, text):
        with open(self.ann, "w", encoding="utf-8") as f:
            f.write(text)

    def test_bad_json_line(self):
        self._write("{not json}\n")
        with self.assertRaises(ValueError) as cm:
            pfi.read_annotations(self.ann)
        self.assertIn("第 1 行", str(cm.exception))

    def test_non_dict_line(self):
        self._write("[1, 2]\n")
        with self.assertRaises(ValueError):
            pfi.read_annotations(self.ann)

    def test_missing_key_line(self):
        self._write('{"asset": "USDCNH"}\n')
        with self.assertRaises(ValueError):
            pfi.read_annotations(self.ann)

    def test_blank_lines_skipped(self):
        good = json.dumps(EXPECT_A1, sort_keys=True, ensure_ascii=False)
        self._write("\n" + good + "\n\n")
        self.assertEqual(pfi.read_annotations(self.ann), [EXPECT_A1])


# ══ 9. 来源等级隔离(三面) ════════════════════════════════════════════════

class TestSourceLevelIsolation(_SandboxCase):
    def test_isolation_check_passes(self):
        self.assertIs(pfi.source_level_isolation_check(), True)

    def test_source_level_outside_v2_vocabularies(self):
        self.assertNotIn(pfi.NOTE_SOURCE_LEVEL,
                         pfi.EVIDENCE_GRADING_V2_MECHANISMS)
        self.assertNotIn(pfi.NOTE_SOURCE_LEVEL, pfi.STAR_LEVEL_STRINGS)
        self.assertEqual(len(pfi.EVIDENCE_GRADING_V2_MECHANISMS), 7)

    def test_note_fieldset_disjoint_from_v2_evidence_fields(self):
        self.assertFalse(set(pfi._NOTE_FIELDS)
                         & set(pfi.V2_EVIDENCE_ITEM_FIELDS))

    def test_v2_field_anchor_registered(self):
        self.assertEqual(pfi.V2_EVIDENCE_ITEM_FIELDS,
                         ("contrary", "explained", "mechanism", "metric",
                          "neutral", "obs_date", "value"))

    def test_monkeypatch_vocabulary_breach_detected(self):
        with mock.patch.object(
                pfi, "EVIDENCE_GRADING_V2_MECHANISMS",
                ("信用", "避险与估值", "供应与库存", "利率与流动性", "增长",
                 "通胀", "资金流", "个人观察")):
            with self.assertRaises(AssertionError):
                pfi.source_level_isolation_check()

    def test_monkeypatch_fieldset_breach_detected(self):
        with mock.patch.object(pfi, "_NOTE_FIELDS",
                               pfi._NOTE_FIELDS + ("mechanism",)):
            with self.assertRaises(AssertionError):
                pfi.source_level_isolation_check()

    def test_render_carries_label_and_zero_star(self):
        pfi.append_note_reference(
            self.note, pfi.build_note_reference(*FX_N1), user_root=self.sb)
        out = pfi.render_note_references(pfi.read_note_references(self.note))
        self.assertIn(pfi.SOURCE_LEVEL_LABEL, out)
        self.assertNotIn("★", out)   # 渲染面零星级符号(P-E-06 隔离)
        self.assertNotIn("1-5", out)

    def test_dp_selfcheck_embeds_isolation(self):
        with mock.patch.object(pfi, "SOURCE_LEVEL_LABEL", "弱化标签"):
            with self.assertRaises(AssertionError):
                pfi.source_level_isolation_check()


# ══ 10. 零主动采集(AST 面) ═══════════════════════════════════════════════

class TestZeroActiveCollection(_SandboxCase):
    def _src_tree(self):
        with open(MODULE_PATH, encoding="utf-8") as f:
            return ast.parse(f.read())

    def test_no_directory_scan_or_process_calls(self):
        banned = {"os.listdir", "os.walk", "os.scandir", "os.system",
                  "os.popen", "glob.glob", "os.fork", "os.execv",
                  "subprocess.run", "subprocess.Popen", "subprocess.call"}
        for node in ast.walk(self._src_tree()):
            if isinstance(node, ast.Call) and isinstance(node.func,
                                                         ast.Attribute):
                self.assertNotIn(ast.unparse(node.func), banned)

    def test_import_whitelist(self):
        got = set()
        for node in ast.walk(self._src_tree()):
            if isinstance(node, ast.Import):
                got.update(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                got.add(node.module)
        self.assertEqual(got, {"json", "os", "sys", "report_quality_review"})

    def test_no_watch_or_network_tokens_outside_docstrings(self):
        tree = self._src_tree()
        docstrings = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef,
                                 ast.ClassDef, ast.AsyncFunctionDef)):
                d = ast.get_docstring(node)
                if d is not None:
                    docstrings.add(d)
        banned = ("listdir", "scandir", "watchdog", "socket", "urllib",
                  "requests", "http://", "https://", "ftp://", "subprocess")
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value in docstrings:
                    continue
                for tok in banned:
                    self.assertNotIn(tok, node.value, repr(node.value[:60]))

    def test_p3_family_modules_zero_network_imports(self):
        # P-E-09: P3 层零用户数据拉取路径断言(五模块零网络 import)
        network = {"socket", "urllib", "requests", "http", "httpx",
                   "ftplib", "smtplib", "telnetlib", "ssl", "poplib",
                   "imaplib"}
        for fn in ("research_index.py", "evidence_linkage.py",
                   "prediction_review.py", "report_quality_review.py",
                   "personal_flow_integration.py"):
            path = os.path.join(SCRIPTS_DIR, fn)
            with open(path, encoding="utf-8") as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                for n in names:
                    self.assertNotIn(n.split(".")[0], network,
                                     f"{fn}: {n}")

    def test_no_module_level_path_constants_beyond_guards_and_dev_root(self):
        # 零主动采集面: 模块级路径类常量封闭集=双守卫组件组+_DEV_ROOT
        # (守卫推导用);零数据根/零监听/零用户目录默认常量
        assign_targets = []
        for node in self._src_tree().body:
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        assign_targets.append(t.id)
        pathish = {t for t in assign_targets
                   if any(k in t for k in ("PATH", "ROOT", "DIR", "FILE"))}
        self.assertEqual(pathish,
                         {"_RAW_DIR_GUARD", "_LIVE_ROOT_GUARD", "_DEV_ROOT"})
        for banned in ("_DATA_ROOT", "_WATCH", "_USER_HOME", "_DEFAULT_PATH"):
            self.assertNotIn(banned, assign_targets)


# ══ 11. 守卫四面(快照纪律/LIVE 根/写入域) ═══════════════════════════════

class TestPathGuards(_SandboxCase):
    def _live_mock(self):
        live = os.path.join(self.sb, *pfi._LIVE_ROOT_GUARD)
        os.makedirs(live, exist_ok=True)
        return live

    def test_raw_data_daily_rejected_on_write_face(self):
        raw = os.path.join(self.sb, "data", "daily", "ann.jsonl")
        with self.assertRaises(ValueError) as cm:
            pfi.append_annotation(
                raw, pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET, FX_A1_VIEW,
                                          FX_A1_BASIS), user_root=self.sb)
        self.assertIn("快照纪律", str(cm.exception))

    def test_raw_data_daily_rejected_on_read_face(self):
        raw = os.path.join(self.sb, "data", "daily", "ann.jsonl")
        with self.assertRaises(ValueError):
            pfi.read_annotations(raw)

    def test_raw_data_daily_rejected_on_export_face(self):
        raw = os.path.join(self.sb, "data", "daily", "export.txt")
        with self.assertRaises(ValueError):
            pfi.write_export_document(raw, "x", user_root=self.sb)

    def test_raw_guard_requires_adjacency(self):
        # data 与 daily 须相邻组件: data/other/daily 不拒(结构面精确性)
        ok_dir = os.path.join(self.sb, "data", "other", "daily")
        os.makedirs(ok_dir, exist_ok=True)
        ok = os.path.join(ok_dir, "ann.jsonl")
        pfi.append_annotation(
            ok, pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET, FX_A1_VIEW,
                                     FX_A1_BASIS), user_root=self.sb)
        self.assertTrue(os.path.exists(ok))

    def test_live_root_rejected_on_write_face(self):
        live_file = os.path.join(self._live_mock(), "ann.jsonl")
        with self.assertRaises(ValueError) as cm:
            pfi.append_annotation(
                live_file, pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET,
                                                FX_A1_VIEW, FX_A1_BASIS),
                user_root=self.sb)
        self.assertIn("LIVE", str(cm.exception))

    def test_live_root_rejected_on_read_face(self):
        live_file = os.path.join(self._live_mock(), "ann.jsonl")
        with self.assertRaises(ValueError):
            pfi.read_annotations(live_file)

    def test_live_root_rejected_on_export_face(self):
        live_file = os.path.join(self._live_mock(), "export.txt")
        with self.assertRaises(ValueError):
            pfi.write_export_document(live_file, "x", user_root=self.sb)

    def test_user_root_into_live_rejected(self):
        live = self._live_mock()
        with self.assertRaises(ValueError):
            pfi.append_annotation(
                os.path.join(self.sb, "ann.jsonl"),
                pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET, FX_A1_VIEW,
                                     FX_A1_BASIS), user_root=live)

    def test_tilde_form_live_rejected_via_expanduser(self):
        live = self._live_mock()
        fake = lambda p: os.path.join(live, p[2:]) if p.startswith("~/") \
            else p                                    # noqa: E731
        with mock.patch("os.path.expanduser", side_effect=fake):
            with self.assertRaises(ValueError):
                pfi.append_annotation(
                    "~/ann.jsonl",
                    pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET, FX_A1_VIEW,
                                         FX_A1_BASIS))

    def test_write_outside_dev_root_and_user_root_rejected(self):
        other = tempfile.mkdtemp(prefix="p3wp-e-other-")
        try:
            outside = os.path.join(other, "ann.jsonl")
            with self.assertRaises(ValueError) as cm:
                pfi.append_annotation(
                    outside, pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET,
                                                  FX_A1_VIEW, FX_A1_BASIS),
                    user_root=self.sb)
            self.assertIn("DEV 仓", str(cm.exception))
        finally:
            os.rmdir(other)

    def test_dev_root_allows_without_user_root_when_patched(self):
        with mock.patch.object(pfi, "_DEV_ROOT", self.sb):
            pfi.append_annotation(
                self.ann, pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET,
                                               FX_A1_VIEW, FX_A1_BASIS))
        self.assertTrue(os.path.exists(self.ann))

    def test_live_mock_tree_itself_is_empty(self):
        self._live_mock()
        self.assertEqual(os.listdir(self._live_mock()), [])


# ══ 12. 接口(c) 导出: 校验/装配/序列化 ═══════════════════════════════════

class TestExportInterface(_SandboxCase):
    def test_validate_rejects_non_dict(self):
        with self.assertRaises(ValueError):
            pfi.validate_export_input(["not", "a", "dict"])

    def test_validate_rejects_wrong_stats_schema(self):
        bad = json.loads(json.dumps(QUALITY_REVIEW_OUTPUT))
        bad["statistics"]["schema_version"] = 2
        with self.assertRaises(ValueError) as cm:
            pfi.validate_export_input(bad)
        self.assertIn("schema_version", str(cm.exception))

    def test_validate_rejects_missing_pieces(self):
        base = json.loads(json.dumps(QUALITY_REVIEW_OUTPUT))
        for key in ("briefing", "suggestions", "prediction_review",
                    "statistics"):
            bad = json.loads(json.dumps(QUALITY_REVIEW_OUTPUT))
            del bad[key]
            with self.assertRaises(ValueError, msg=key):
                pfi.validate_export_input(bad)
        self.assertIn("statistics", base)   # base 完整性自证

    def test_validate_rejects_blank_or_non_str_briefing(self):
        for bad_value in ("", "   ", 5, None):
            bad = json.loads(json.dumps(QUALITY_REVIEW_OUTPUT))
            bad["briefing"] = bad_value
            with self.assertRaises(ValueError, msg=repr(bad_value)):
                pfi.validate_export_input(bad)

    def test_build_document_nine_keys_exact(self):
        doc = pfi.build_export_document(QUALITY_REVIEW_OUTPUT)
        self.assertEqual(set(doc), set(pfi._EXPORT_FIELDS))
        self.assertEqual(len(doc), 9)

    def test_build_document_passthrough_identity(self):
        doc = pfi.build_export_document(QUALITY_REVIEW_OUTPUT)
        q = QUALITY_REVIEW_OUTPUT
        self.assertIs(doc["quality_briefing"], q["briefing"])
        self.assertIs(doc["suggestions"], q["suggestions"])
        self.assertIs(doc["error_pattern_statistics"],
                      q["prediction_review"]["statistics"])

    def test_build_document_window_fields_carried(self):
        doc = pfi.build_export_document(QUALITY_REVIEW_OUTPUT)
        s = QUALITY_REVIEW_OUTPUT["statistics"]
        self.assertEqual(doc["as_of"], s["as_of"])
        self.assertEqual(doc["window_kind"], s["window_kind"])
        self.assertEqual(doc["window_start"], s["window_start"])
        self.assertEqual(doc["window_end"], s["window_end"])
        self.assertEqual(doc["schema_version"], 1)

    def test_build_document_note_carries_disclaimer(self):
        doc = pfi.build_export_document(QUALITY_REVIEW_OUTPUT)
        self.assertIn("单向导出", doc["note"])
        self.assertIn("不构成投资建议", doc["note"])
        self.assertIn("原样承载", doc["note"])

    def test_upstream_anchor_is_real_module_not_copy(self):
        self.assertIs(pfi.rqr, rqr)
        self.assertEqual(pfi.rqr.__name__, "report_quality_review")
        self.assertEqual(pfi.rqr.STATS_SCHEMA_VERSION,
                         rqr.STATS_SCHEMA_VERSION)
        self.assertEqual(rqr.STATS_SCHEMA_VERSION, 1)

    def test_dump_canonical_deterministic(self):
        doc = pfi.build_export_document(QUALITY_REVIEW_OUTPUT)
        d1 = pfi.dump_export_document(doc)
        d2 = pfi.dump_export_document(json.loads(json.dumps(doc)))
        self.assertEqual(d1, d2)
        self.assertEqual(json.loads(d1), doc)

    def test_dump_rejects_wrong_schema(self):
        with self.assertRaises(ValueError):
            pfi.dump_export_document({"schema_version": 2})
        with self.assertRaises(ValueError):
            pfi.dump_export_document("not-a-doc")

    def test_dump_golden_sha(self):
        doc = pfi.build_export_document(QUALITY_REVIEW_OUTPUT)
        self.assertEqual(_sha(pfi.dump_export_document(doc)),
                         GOLDEN_SHAS["G5_export_document"])


# ══ 13. 导出渲染 ═════════════════════════════════════════════════════════

class TestExportRender(_SandboxCase):
    def test_golden_briefing_full_text(self):
        doc = pfi.build_export_document(QUALITY_REVIEW_OUTPUT)
        self.assertEqual(pfi.render_export_briefing(doc),
                         GOLDEN_EXPORT_BRIEFING)
        self.assertEqual(_sha(pfi.render_export_briefing(doc)),
                         GOLDEN_SHAS["G6_export_briefing_render"])

    def test_briefing_embeds_quality_briefing_verbatim(self):
        doc = pfi.build_export_document(QUALITY_REVIEW_OUTPUT)
        self.assertIn(QUALITY_REVIEW_OUTPUT["briefing"],
                      pfi.render_export_briefing(doc))

    def test_hit_rate_na_when_absent(self):
        q = json.loads(json.dumps(QUALITY_REVIEW_OUTPUT))
        del q["prediction_review"]["statistics"]["counts"]["hit_rate"]
        out = pfi.render_export_briefing(pfi.build_export_document(q))
        self.assertIn("N/A", out)
        self.assertNotIn("0.6667", out)

    def test_hit_rate_formatted_four_decimals(self):
        doc = pfi.build_export_document(QUALITY_REVIEW_OUTPUT)
        self.assertIn("0.6667", pfi.render_export_briefing(doc))

    def test_empty_suggestions_rendered_honestly(self):
        q = json.loads(json.dumps(QUALITY_REVIEW_OUTPUT))
        q["suggestions"] = []
        out = pfi.render_export_briefing(pfi.build_export_document(q))
        self.assertIn("校准建议清单: 空(如实呈现)", out)

    def test_error_pattern_axes_present(self):
        out = pfi.render_export_briefing(
            pfi.build_export_document(QUALITY_REVIEW_OUTPUT))
        for axis in ("方向错误", "期限错误", "幅度错误", "无法归类(单列)"):
            self.assertIn(axis, out)
        self.assertIn("QB-20251208-001", out)
        self.assertIn("not_yet_triggered终态=1(单列)", out)

    def test_disclaimer_tail_present(self):
        out = pfi.render_export_briefing(
            pfi.build_export_document(QUALITY_REVIEW_OUTPUT))
        self.assertIn("不构成投资建议", out)
        self.assertIn("零回读", out)

    def test_non_doc_input_rejected(self):
        with self.assertRaises(ValueError):
            pfi.render_export_briefing({"schema_version": 2})
        with self.assertRaises(ValueError):
            pfi.render_export_briefing("x")


# ══ 14. 旁路渲染(标注/笔记视图) ══════════════════════════════════════════

class TestRenderViews(_SandboxCase):
    def test_annotation_view_golden(self):
        surfaces = _build_golden_fixture(self.sb)
        self.assertEqual(surfaces["G1_annotation_view_render"],
                         GOLDEN_ANNOTATION_VIEW)
        self.assertEqual(_sha(surfaces["G1_annotation_view_render"]),
                         GOLDEN_SHAS["G1_annotation_view_render"])

    def test_note_refs_view_golden(self):
        surfaces = _build_golden_fixture(self.sb)
        self.assertEqual(surfaces["G2_note_refs_render"],
                         GOLDEN_NOTE_REFS_VIEW)
        self.assertEqual(_sha(surfaces["G2_note_refs_render"]),
                         GOLDEN_SHAS["G2_note_refs_render"])

    def test_annotation_view_disclaimer_and_collection_note(self):
        out = pfi.render_annotation_view([EXPECT_A1])
        self.assertIn("零主动采集", out)
        self.assertIn("不构成投资建议", out)
        self.assertIn("标注 1 条:", out)

    def test_empty_records_render_zero_count(self):
        self.assertIn("标注 0 条:", pfi.render_annotation_view([]))
        self.assertIn("引用 0 条:", pfi.render_note_references([]))

    def test_non_list_input_rejected(self):
        with self.assertRaises(ValueError):
            pfi.render_annotation_view("x")
        with self.assertRaises(ValueError):
            pfi.render_note_references(None)


# ══ 15. AST 纯度(白名单/记账/行锚) ══════════════════════════════════════

class TestStaticPurity(_SandboxCase):
    def setUp(self):
        super().setUp()
        with open(MODULE_PATH, encoding="utf-8") as f:
            self.src = f.read()
        self.tree = ast.parse(self.src)

    def test_open_mode_accounting(self):
        modes = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call) \
                    and isinstance(node.func, ast.Name) \
                    and node.func.id == "open":
                self.assertGreaterEqual(len(node.args), 2, "open 须显式模式")
                modes.append(node.args[1].value)
        self.assertEqual(Counter(modes), Counter(["a", "a", "w", "r"]))

    def test_no_forbidden_write_calls(self):
        banned = {"os.remove", "os.unlink", "os.rmdir", "os.rename",
                  "os.replace", "os.mkdir", "os.makedirs", "os.chdir",
                  "os.truncate", "shutil.rmtree", "shutil.move", "shutil.copy",
                  "eval", "exec", "compile", "__import__", "os.putenv"}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                name = ast.unparse(node.func)
                if isinstance(node.func, ast.Attribute):
                    self.assertNotIn(name, banned, name)
                else:
                    self.assertNotIn(name, banned, name)

    def test_no_write_mode_variants(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call) \
                    and isinstance(node.func, ast.Name) \
                    and node.func.id == "open":
                mode = node.args[1].value
                self.assertNotIn("+", mode)
                self.assertNotIn("x", mode)

    def test_sys_path_insert_exactly_once(self):
        count = 0
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call) \
                    and ast.unparse(node.func) == "sys.path.insert":
                count += 1
        self.assertEqual(count, 1)

    def test_live_literals_line_anchored(self):
        comps = list(pfi._LIVE_ROOT_GUARD)
        for lineno, line in enumerate(self.src.splitlines(), 1):
            if any(c in line for c in comps):
                self.assertTrue("_LIVE_ROOT_GUARD" in line
                                or "live_guard_seq" in line,
                                f"LIVE 组件字面量越出守卫锚定行: L{lineno}")

    def test_no_continuous_live_path_literal(self):
        docstrings = set()
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef,
                                 ast.AsyncFunctionDef)):
                d = ast.get_docstring(node)
                if d is not None:
                    docstrings.add(d)
        joined = os.path.join(*pfi._LIVE_ROOT_GUARD)
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value in docstrings:
                    continue
                self.assertNotIn(joined, node.value)

    def test_no_continuous_raw_dir_literal(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                self.assertNotIn(
                    pfi._RAW_DIR_GUARD[0] + "/" + pfi._RAW_DIR_GUARD[1],
                    node.value)
                self.assertNotIn(
                    pfi._RAW_DIR_GUARD[0] + os.sep + pfi._RAW_DIR_GUARD[1],
                    node.value)

    def test_export_write_face_zero_read_back(self):
        # P-E-08 结构性零回读: write_export_document 函数体零读取面
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) \
                    and node.name == "write_export_document":
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Call) \
                            and isinstance(sub.func, ast.Name) \
                            and sub.func.id == "open":
                        self.assertEqual(sub.args[1].value, "w")
                    if isinstance(sub, ast.Call) \
                            and isinstance(sub.func, ast.Name):
                        self.assertNotIn(sub.func.id,
                                         ("read_annotations",
                                          "read_note_references",
                                          "_load_records"))
                return
        self.fail("write_export_document 未找到")

    def test_no_update_delete_rewrite_api_surface(self):
        # P-E-04 零改写面: 模块无 update/delete/rewrite 类公共 API(dir 扫描)
        mutators = [n for n in dir(pfi)
                    if any(k in n.lower() for k in
                           ("update", "delete", "rewrite", "remove",
                            "modify"))]
        self.assertEqual(mutators, [])

    def test_upstream_module_files_untouched_by_import(self):
        before = _sha(open(os.path.join(SCRIPTS_DIR,
                                        "report_quality_review.py"),
                           "rb").read())
        import importlib
        importlib.reload(pfi)
        after = _sha(open(os.path.join(SCRIPTS_DIR,
                                       "report_quality_review.py"),
                          "rb").read())
        self.assertEqual(before, after)

    def test_module_compiles(self):
        compile(self.src, MODULE_PATH, "exec")


# ══ 16. 负向守卫(综合) ═══════════════════════════════════════════════════

class TestNegativeInputs(_SandboxCase):
    def test_non_dict_record_rejected(self):
        with self.assertRaises(ValueError):
            pfi.append_annotation(self.ann, "not-a-dict", user_root=self.sb)
        with self.assertRaises(ValueError):
            pfi.append_note_reference(self.note, 42, user_root=self.sb)

    def test_missing_field_hand_dict_rejected(self):
        rec = {k: v for k, v in EXPECT_A1.items() if k != "basis"}
        with self.assertRaises(ValueError):
            pfi.append_annotation(self.ann, rec, user_root=self.sb)
        nrec = {k: v for k, v in EXPECT_N1.items() if k != "archive_key"}
        with self.assertRaises(ValueError):
            pfi.append_note_reference(self.note, nrec, user_root=self.sb)

    def test_export_write_non_str_content_rejected(self):
        with self.assertRaises(ValueError):
            pfi.write_export_document(
                os.path.join(self.sb, "e.txt"), 123, user_root=self.sb)

    def test_export_write_outside_roots_rejected(self):
        other = tempfile.mkdtemp(prefix="p3wp-e-neg-")
        try:
            with self.assertRaises(ValueError):
                pfi.write_export_document(os.path.join(other, "e.txt"), "x",
                                          user_root=self.sb)
        finally:
            os.rmdir(other)

    def test_export_write_live_rejected(self):
        live = os.path.join(self.sb, *pfi._LIVE_ROOT_GUARD)
        os.makedirs(live, exist_ok=True)
        with self.assertRaises(ValueError):
            pfi.write_export_document(os.path.join(live, "e.txt"), "x",
                                      user_root=self.sb)

    def test_export_write_happy_path_single_file(self):
        out_dir = os.path.join(self.sb, "exports")
        os.makedirs(out_dir, exist_ok=True)
        target = os.path.join(out_dir, "export.txt")
        content = pfi.render_export_briefing(
            pfi.build_export_document(QUALITY_REVIEW_OUTPUT))
        returned = pfi.write_export_document(target, content,
                                             user_root=self.sb)
        self.assertEqual(returned, os.path.normpath(target))
        self.assertEqual(sorted(os.listdir(out_dir)), ["export.txt"])
        with open(target, encoding="utf-8") as f:
            self.assertEqual(f.read(), content)


# ══ 17. 零回写(读写面记账) ═══════════════════════════════════════════════

class TestZeroWrite(_SandboxCase):
    def test_read_and_render_leave_tree_unchanged(self):
        pfi.append_annotation(
            self.ann, pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET, FX_A1_VIEW,
                                           FX_A1_BASIS), user_root=self.sb)
        pfi.append_note_reference(
            self.note, pfi.build_note_reference(*FX_N1), user_root=self.sb)
        with open(os.path.join(self.sb, "unrelated.txt"), "w",
                  encoding="utf-8") as f:
            f.write("旁路文件,不得被触碰")
        before = _tree_shas(self.sb)
        pfi.read_annotations(self.ann)
        pfi.read_note_references(self.note)
        pfi.render_annotation_view(pfi.read_annotations(self.ann))
        pfi.render_note_references(pfi.read_note_references(self.note))
        pfi.build_export_document(QUALITY_REVIEW_OUTPUT)
        pfi.dump_export_document(
            pfi.build_export_document(QUALITY_REVIEW_OUTPUT))
        pfi.validate_export_input(QUALITY_REVIEW_OUTPUT)
        self.assertEqual(_tree_shas(self.sb), before)

    def test_append_touches_only_target_archive(self):
        pfi.append_note_reference(
            self.note, pfi.build_note_reference(*FX_N1), user_root=self.sb)
        with open(os.path.join(self.sb, "unrelated.txt"), "w",
                  encoding="utf-8") as f:
            f.write("旁路文件,不得被触碰")
        before = _tree_shas(self.sb)
        pfi.append_annotation(
            self.ann, pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET, FX_A1_VIEW,
                                           FX_A1_BASIS), user_root=self.sb)
        after = _tree_shas(self.sb)
        self.assertEqual(set(before) | {self.ann}, set(after))
        self.assertNotEqual(before.get(self.ann), after.get(self.ann))
        for p in set(after) - {self.ann}:
            self.assertEqual(before.get(p, after[p]), after[p], p)

    def test_failed_append_leaves_no_partial_write(self):
        with open(self.ann, "w", encoding="utf-8") as f:
            f.write("")   # 空档: 重复档键场景前基础态
        rec = pfi.build_annotation(FX_A1_DATE, FX_A1_ASSET, FX_A1_VIEW,
                                   FX_A1_BASIS,
                                   annotation_id="ANN-20260105-001")
        pfi.append_annotation(self.ann, rec, user_root=self.sb)
        before = open(self.ann, "rb").read()
        with self.assertRaises(ValueError):
            pfi.append_annotation(self.ann, rec, user_root=self.sb)
        self.assertEqual(open(self.ann, "rb").read(), before)

    def test_upstream_report_quality_review_source_unchanged(self):
        before = _sha(open(os.path.join(SCRIPTS_DIR,
                                        "report_quality_review.py"),
                           "rb").read())
        _build_golden_fixture(self.sb)
        after = _sha(open(os.path.join(SCRIPTS_DIR,
                                       "report_quality_review.py"),
                          "rb").read())
        self.assertEqual(before, after)


# ══ 18. __main__ selfcheck(受控 subprocess 唯一面) ═══════════════════════

class TestSelfcheckMain(_SandboxCase):
    def test_selfcheck_main_exit_zero_with_sentinels(self):
        proc = subprocess.run(
            [sys.executable, MODULE_PATH],
            capture_output=True, text=True, cwd=self.sb, timeout=60,
            env={k: v for k, v in os.environ.items()
                 if not k.startswith("PYTHON")},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("dp_selfcheck=True", proc.stdout)
        self.assertIn("isolation_check=True", proc.stdout)
        self.assertIn("不构成投资建议", proc.stdout)
        self.assertIn("interfaces=3", proc.stdout)
        # P-E-17: __main__ 自检入口零写入零默认路径(运行后运行目录零新文件)
        self.assertEqual(os.listdir(self.sb), [])


if __name__ == "__main__":
    unittest.main()
