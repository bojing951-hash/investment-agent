#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P2-WP-D 测试套件: 事件序列数据面(议息/发布事件结构化日历)

DESIGN §七 WP-P2-D 行(L211-L215)验收要点逐条离线覆盖:
①事件档 schema 与来源登记(免费源 URL 白名单登记制)——TestEventIdGolden/
  TestEventSchemaNegative/TestEventRegistryFace/TestEventAppendOnly/TestEventLoading;
②事件窗对齐计算单测(事件前后窗口取数经快照)——TestWindowBounds/
  TestWindowObservationsGolden/TestWindowQuality/TestSnapshotDiscipline/
  TestMountContext;
③零凭证零付费断言——TestZeroCredentialPaid(+白名单登记断言);
④CI 零回归——套件自身 exit 0(本地 CI 镜像逐套件循环)。

纪律: 零网络;全合成 fixture=唯一数据源(R014-D3/R022 常态化,测试不触
data/daily 真实档);预期值字面量硬编码(GOLDEN 表,独立预计算固化,
禁运行期从被测模块导入计算);created_at 全显式定值零墙钟。
黄金值独立复算登记: 测试内 hashlib 首原理复算(TestDeterminism),与
GOLDEN 字面量逐值相等(双源一致);fixture 定义与预计算脚本
(/tmp/p2d-golden-precompute.py,证据包 03 成员)逐字节一致。
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))

import deep_research_event_calendar as dcal
import deep_research_registrar as drr

# ══ 黄金字面量表(独立预计算固化;禁运行期重算/禁从被测模块导入计算) ══════

GOLDEN = {
    "EV_CPI": "CAL-20261101-a69dabac",        # INDICATOR_RELEASE CPI 2026-11-05
    "EV_NFP": "CAL-20261101-77e22e0f",        # INDICATOR_RELEASE NFP_MOM_K 2026-11-06
    "EV_FOMC": "CAL-20261101-b0d76694",       # FOMC_RATE_DECISION 无绑定 2026-11-19
    "EV_FOMC_DFED": "CAL-20261101-98b901c9",  # FOMC_RATE_DECISION DFEDTARL 2026-12-17
    "EV_FAR": "CAL-20261101-692eaae1",        # FOMC 远期窗外构造 2026-12-25
    "DIGEST_MAIN": "7ca5582e900ca358",        # SNAP_MAIN 内容指纹(rp 同款首16位)
    "DIGEST_DEGRADED": "293f45b126b21221",
    "DIGEST_FAIL": "c27a0288f963d1a9",
}

# ══ 合成 fixture(唯一数据源;与黄金预计算逐字节一致) ════════════════════

SNAP_MAIN = {
    "snapshot_id": "research_snapshot_20261110", "as_of": "2026-11-10",
    "gate_a": {"status": "PASS"},
    "facts": [
        {"fact_id": "CPI@2026-11-03", "metric_id": "CPI",
         "observation_date": "2026-11-03", "value": 3.2, "quality_status": "OK"},
        {"fact_id": "CPI@2026-11-04", "metric_id": "CPI",
         "observation_date": "2026-11-04", "value": 3.25, "quality_status": "OK"},
        {"fact_id": "CPI@2026-11-06", "metric_id": "CPI",
         "observation_date": "2026-11-06", "value": 3.3, "quality_status": "OK"},
        {"fact_id": "CPI@2026-11-07", "metric_id": "CPI",
         "observation_date": "2026-11-07", "value": 3.4, "quality_status": "FAIL"},
        {"fact_id": "CPI@2026-11-08", "metric_id": "CPI",
         "observation_date": "2026-11-08", "value": "N/A", "quality_status": "OK"},
        {"fact_id": "CPI@2026-10-20", "metric_id": "CPI",
         "observation_date": "2026-10-20", "value": 3.1, "quality_status": "OK"},
        {"fact_id": "NFP_MOM_K@2026-11-06", "metric_id": "NFP_MOM_K",
         "observation_date": "2026-11-06", "value": 150.0, "quality_status": "OK"},
        {"fact_id": "DFEDTARL@2026-11-19", "metric_id": "DFEDTARL",
         "observation_date": "2026-11-19", "value": 3.75, "quality_status": "OK"},
    ],
}
SNAP_DEGRADED = dict(SNAP_MAIN, snapshot_id="research_snapshot_20261111",
                     as_of="2026-11-11", gate_a={"status": "DEGRADED"})
SNAP_FAIL = {"snapshot_id": "research_snapshot_20261112", "as_of": "2026-11-12",
             "gate_a": {"status": "FAIL"}, "facts": []}


def write_snapshot(root, snap):
    d = os.path.join(root, "snapshots")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, snap["snapshot_id"] + ".json")
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(snap, f, ensure_ascii=False, sort_keys=True)
    return d


def make_event(source_id, event_type, event_date, metric_id, note, created_at):
    """构造**已通过校验形态**的事件档(source_url 由白名单回填,同模块登记路径)。"""
    return {"record_type": "calendar_event",
            "event_id": dcal.make_calendar_event_id(source_id, event_type,
                                                    event_date, metric_id,
                                                    note, created_at),
            "created_at": created_at, "event_type": event_type,
            "event_date": event_date, "source_id": source_id,
            "source_url": dcal.SOURCE_WHITELIST[source_id]["url"],
            "metric_id": metric_id, "note": note,
            "history": [{"ts": created_at, "note": "测试合成档"}]}


EV_CPI = make_event("SRC_BLS_CPI", "INDICATOR_RELEASE", "2026-11-05", "CPI",
                    "美国2026年10月CPI发布(日程登记)", "2026-11-01T08:00:00")
EV_NFP = make_event("SRC_BLS_EMPSIT", "INDICATOR_RELEASE", "2026-11-06",
                    "NFP_MOM_K", "美国2026年10月非农就业报告(日程登记)",
                    "2026-11-01T08:05:00")
EV_FOMC = make_event("SRC_FED", "FOMC_RATE_DECISION", "2026-11-19", None,
                     "FOMC议息日(11月会议,日程登记)", "2026-11-01T08:10:00")
EV_FOMC_DFED = make_event("SRC_FED", "FOMC_RATE_DECISION", "2026-12-17",
                          "DFEDTARL",
                          "FOMC议息日(12月会议,目标区间下限通道绑定)",
                          "2026-11-01T08:15:00")
EV_FAR = make_event("SRC_FED", "FOMC_RATE_DECISION", "2026-12-25", None,
                    "FOMC议息日(远期窗外构造)", "2026-11-01T08:30:00")


class SandboxBase(unittest.TestCase):
    """每用例独立临时沙箱(archive+snapshots)。"""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="p2d-test-")
        self.archive = os.path.join(self.root, "archive")
        self.snapdir = write_snapshot(self.root, SNAP_MAIN)
        write_snapshot(self.root, SNAP_DEGRADED)
        write_snapshot(self.root, SNAP_FAIL)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)


# ══ 要点③+①: 白名单登记与零凭证零付费 ═════════════════════════════════

class TestSourceWhitelistRegistry(unittest.TestCase):

    def test_whitelist_three_sources_registered(self):
        self.assertEqual(sorted(dcal.SOURCE_WHITELIST),
                         ["SRC_BLS_CPI", "SRC_BLS_EMPSIT", "SRC_FED"])

    def test_every_source_free_no_credentials_no_cost(self):
        for sid, src in dcal.SOURCE_WHITELIST.items():
            self.assertEqual(src["access"], "free_public", sid)
            self.assertEqual(src["credentials"], "none", sid)
            self.assertEqual(src["cost"], "none", sid)
            self.assertTrue(src["url"].startswith("https://"), sid)

    def test_every_event_type_supported_by_some_source(self):
        for et in dcal.EVENT_TYPES:
            self.assertTrue(any(et in s["supports"]
                                for s in dcal.SOURCE_WHITELIST.values()), et)


class TestZeroCredentialPaid(unittest.TestCase):

    def test_module_source_no_credential_patterns(self):
        src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', 'scripts',
                                'deep_research_event_calendar.py'),
                   encoding='utf-8').read()
        for pat in ("api_key", "apikey", "token", "password", "secret",
                    "Authorization", "os.environ", "getenv"):
            self.assertNotIn(pat, src, pat)

    def test_module_no_network_imports(self):
        import ast
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            '..', 'scripts', 'deep_research_event_calendar.py')
        tree = ast.parse(open(path, encoding='utf-8').read())
        banned = ("urllib", "http", "socket", "requests", "httpx", "ssl",
                  "ftplib", "smtplib", "telnetlib", "xmlrpc")
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for n in names:
                self.assertNotIn(n.split('.')[0], banned, n)

    def test_whitelist_urls_never_fetched_anywhere(self):
        # 零访问=结构性: 模块无任何网络 API 可达面(与上一用例同源 AST 断言);
        # 本用例锚定: 源码不出现 urlopen/requests.get 等取数调用字面
        src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', 'scripts',
                                'deep_research_event_calendar.py'),
                   encoding='utf-8').read()
        for pat in ("urlopen", "requests.get", "requests.post", "http.client",
                    "socket.connect"):
            self.assertNotIn(pat, src, pat)


# ══ 要点①: 事件档 schema 与黄金 ID ═════════════════════════════════════

class TestEventIdGolden(unittest.TestCase):

    def test_ev_cpi_golden_id(self):
        self.assertEqual(EV_CPI["event_id"], GOLDEN["EV_CPI"])

    def test_ev_nfp_golden_id(self):
        self.assertEqual(EV_NFP["event_id"], GOLDEN["EV_NFP"])

    def test_ev_fomc_golden_id_none_metric(self):
        self.assertEqual(EV_FOMC["event_id"], GOLDEN["EV_FOMC"])

    def test_ev_fomc_dfed_golden_id(self):
        self.assertEqual(EV_FOMC_DFED["event_id"], GOLDEN["EV_FOMC_DFED"])


class TestEventSchemaNegative(unittest.TestCase):

    def _base(self):
        return dict(EV_CPI)

    def test_missing_field_rejected(self):
        rec = self._base()
        del rec["source_url"]
        self.assertTrue(dcal.validate_calendar_event(rec))

    def test_wrong_record_type_rejected(self):
        rec = self._base()
        rec["record_type"] = "something_else"
        self.assertTrue(dcal.validate_calendar_event(rec))

    def test_unknown_event_type_rejected(self):
        rec = self._base()
        rec["event_type"] = "ECB_RATE_DECISION"
        self.assertTrue(any("event_type非法" in i
                            for i in dcal.validate_calendar_event(rec)))

    def test_noncanonical_date_rejected(self):
        rec = self._base()
        rec["event_date"] = "2026-1-5"
        self.assertTrue(any("event_date" in i
                            for i in dcal.validate_calendar_event(rec)))

    def test_invalid_date_rejected(self):
        rec = self._base()
        rec["event_date"] = "2026-02-30"
        self.assertTrue(any("event_date" in i
                            for i in dcal.validate_calendar_event(rec)))

    def test_unregistered_source_rejected(self):
        rec = self._base()
        rec["source_id"] = "SRC_PAID_X"
        rec["event_id"] = "CAL-20261101-00000000"
        issues = dcal.validate_calendar_event(rec)
        self.assertTrue(any("source_id不在免费源白名单" in i for i in issues))

    def test_source_url_mismatch_rejected(self):
        rec = self._base()
        rec["source_url"] = "https://example.invalid/calendar"
        self.assertTrue(any("source_url与白名单登记值不符" in i
                            for i in dcal.validate_calendar_event(rec)))

    def test_source_type_not_supported_rejected(self):
        rec = self._base()   # CPI 源不支持 FOMC 类型
        rec["event_type"] = "FOMC_RATE_DECISION"
        rec["metric_id"] = None
        issues = dcal.validate_calendar_event(rec)
        self.assertTrue(any("不支持事件类型" in i for i in issues))

    def test_indicator_metric_outside_whitelist_rejected(self):
        rec = self._base()
        rec["metric_id"] = "CORE_PCE"        # 引用=1 不在最小集白名单(P-D-05)
        issues = dcal.validate_calendar_event(rec)
        self.assertTrue(any("最小集白名单" in i for i in issues))

    def test_fomc_metric_outside_channel_rejected(self):
        rec = dict(EV_FOMC)
        rec["metric_id"] = "CPI"             # FOMC 不允许 CPI 绑定
        issues = dcal.validate_calendar_event(rec)
        self.assertTrue(any("DFEDTAR" in i for i in issues))

    def test_tampered_id_rejected(self):
        rec = self._base()
        rec["event_date"] = "2026-11-06"     # 字段改动→指纹重算不符
        issues = dcal.validate_calendar_event(rec)
        self.assertTrue(any("指纹重算不符" in i for i in issues))


class TestEventRegistryFace(unittest.TestCase):

    def test_minset_metrics_all_in_registry(self):
        import fact_engine as fe
        for mid in dcal.INDICATOR_METRIC_WHITELIST:
            self.assertIsNotNone(fe.metric(mid), mid)
        for mid in dcal.FOMC_METRIC_WHITELIST:
            self.assertIsNotNone(fe.metric(mid), mid)

    def test_registry_absent_metric_rejected_via_patch(self):
        import fact_engine as fe
        orig = fe.metric
        fe.metric = lambda mid: None          # 模拟 registry 缺席(白名单成员)
        try:
            issues = dcal.validate_calendar_event(dict(EV_CPI))
            self.assertTrue(any("不在 metric_registry 在场集" in i
                                for i in issues))
        finally:
            fe.metric = orig


# ══ 要点①: append-only 与装载 ══════════════════════════════════════════

class TestEventAppendOnly(SandboxBase):

    def test_replay_same_input_rejected_duplicate(self):
        spec = {"source_id": "SRC_BLS_CPI", "event_type": "INDICATOR_RELEASE",
                "event_date": "2026-11-05", "metric_id": "CPI",
                "note": "美国2026年10月CPI发布(日程登记)"}
        r1 = dcal.register_calendar_event(spec, archive_dir=self.archive,
                                          created_at="2026-11-01T08:00:00")
        self.assertEqual(r1["status"], drr.STATUS_WRITTEN)
        r2 = dcal.register_calendar_event(spec, archive_dir=self.archive,
                                          created_at="2026-11-01T08:00:00")
        self.assertEqual(r2["status"], drr.STATUS_REJECTED_DUPLICATE)
        self.assertEqual(r1["event_id"], GOLDEN["EV_CPI"])

    def test_cross_sandbox_same_input_same_id(self):
        root2 = tempfile.mkdtemp(prefix="p2d-test2-")
        try:
            spec = {"source_id": "SRC_FED", "event_type": "FOMC_RATE_DECISION",
                    "event_date": "2026-12-17", "metric_id": "DFEDTARL",
                    "note": "FOMC议息日(12月会议,目标区间下限通道绑定)"}
            r1 = dcal.register_calendar_event(spec, archive_dir=self.archive,
                                              created_at="2026-11-01T08:15:00")
            r2 = dcal.register_calendar_event(spec, archive_dir=root2,
                                              created_at="2026-11-01T08:15:00")
            self.assertEqual(r1["event_id"], r2["event_id"])
            self.assertEqual(r1["event_id"], GOLDEN["EV_FOMC_DFED"])
        finally:
            shutil.rmtree(root2, ignore_errors=True)

    def test_tampered_archive_file_fail_loud_on_list(self):
        spec = {"source_id": "SRC_BLS_CPI", "event_type": "INDICATOR_RELEASE",
                "event_date": "2026-11-05", "metric_id": "CPI",
                "note": "美国2026年10月CPI发布(日程登记)"}
        dcal.register_calendar_event(spec, archive_dir=self.archive,
                                     created_at="2026-11-01T08:00:00")
        path = os.path.join(self.archive, dcal.ARCHIVE_FAMILY,
                            dcal.COLLECTION_CALENDAR,
                            GOLDEN["EV_CPI"] + ".json")
        rec = json.load(open(path, encoding='utf-8'))
        rec["source_url"] = "https://tampered.invalid/x"   # 篡改档
        json.dump(rec, open(path, 'w', encoding='utf-8'), ensure_ascii=False)
        with self.assertRaises(ValueError) as cm:
            dcal.list_calendar_events(archive_dir=self.archive)
        self.assertIn("档内校验失败", str(cm.exception))


class TestEventLoading(SandboxBase):

    def test_list_sorted_by_date_then_id(self):
        for spec, ca in (
                ({"source_id": "SRC_BLS_EMPSIT", "event_type": "INDICATOR_RELEASE",
                  "event_date": "2026-11-06", "metric_id": "NFP_MOM_K",
                  "note": "美国2026年10月非农就业报告(日程登记)"},
                 "2026-11-01T08:05:00"),
                ({"source_id": "SRC_BLS_CPI", "event_type": "INDICATOR_RELEASE",
                  "event_date": "2026-11-05", "metric_id": "CPI",
                  "note": "美国2026年10月CPI发布(日程登记)"},
                 "2026-11-01T08:00:00"),
                ({"source_id": "SRC_FED", "event_type": "FOMC_RATE_DECISION",
                  "event_date": "2026-11-19", "metric_id": None,
                  "note": "FOMC议息日(11月会议,日程登记)"},
                 "2026-11-01T08:10:00")):
            dcal.register_calendar_event(spec, archive_dir=self.archive,
                                         created_at=ca)
        evs = dcal.list_calendar_events(archive_dir=self.archive)
        self.assertEqual([e["event_id"] for e in evs],
                         [GOLDEN["EV_CPI"], GOLDEN["EV_NFP"], GOLDEN["EV_FOMC"]])

    def test_list_empty_archive(self):
        self.assertEqual(dcal.list_calendar_events(archive_dir=self.archive), [])


# ══ 要点②: 窗口边界口径(P-D-06) ═══════════════════════════════════════

class TestWindowBounds(unittest.TestCase):

    def test_default_bounds_pre_excludes_event_day(self):
        b = dcal.event_window_bounds("2026-11-05", 5, 5)
        self.assertEqual(b["pre"], ("2026-10-31", "2026-11-04"))
        self.assertEqual(b["post"], ("2026-11-05", "2026-11-10"))

    def test_pre_window_boundary_day_before_event(self):
        b = dcal.event_window_bounds("2026-11-05", 5, 5)
        self.assertEqual(dcal.classify_observation("2026-11-04", b), "pre")
        self.assertEqual(dcal.classify_observation("2026-10-31", b), "pre")
        self.assertIsNone(dcal.classify_observation("2026-10-30", b))

    def test_post_window_includes_event_day(self):
        b = dcal.event_window_bounds("2026-11-05", 5, 5)
        self.assertEqual(dcal.classify_observation("2026-11-05", b), "post")
        self.assertEqual(dcal.classify_observation("2026-11-10", b), "post")
        self.assertIsNone(dcal.classify_observation("2026-11-11", b))

    def test_post_days_zero_window_is_event_day_only(self):
        b = dcal.event_window_bounds("2026-11-05", 5, 0)
        self.assertEqual(b["post"], ("2026-11-05", "2026-11-05"))
        self.assertEqual(dcal.classify_observation("2026-11-05", b), "post")
        self.assertIsNone(dcal.classify_observation("2026-11-06", b))

    def test_pre_days_zero_window_empty_classification(self):
        b = dcal.event_window_bounds("2026-11-05", 0, 5)
        self.assertEqual(b["pre"], ("2026-11-05", "2026-11-04"))  # 空区间
        self.assertIsNone(dcal.classify_observation("2026-11-04", b))
        self.assertEqual(dcal.classify_observation("2026-11-05", b), "post")

    def test_negative_days_rejected(self):
        with self.assertRaises(ValueError):
            dcal.event_window_bounds("2026-11-05", -1, 5)

    def test_non_int_days_rejected(self):
        with self.assertRaises(ValueError):
            dcal.event_window_bounds("2026-11-05", "5", 5)
        with self.assertRaises(ValueError):
            dcal.event_window_bounds("2026-11-05", 2.5, 5)


# ══ 要点②: 事件窗观测黄金(经快照取数) ═════════════════════════════════

class TestWindowObservationsGolden(SandboxBase):

    def test_cpi_event_window_golden(self):
        out = dcal.event_window_observations(EV_CPI, "research_snapshot_20261110",
                                             self.snapdir)
        self.assertEqual(out["event_id"], GOLDEN["EV_CPI"])
        self.assertEqual(out["digest_snapshot"], GOLDEN["DIGEST_MAIN"])
        self.assertEqual(out["window"]["pre"],
                         {"start": "2026-10-31", "end": "2026-11-04"})
        self.assertEqual(out["window"]["post"],
                         {"start": "2026-11-05", "end": "2026-11-10"})
        self.assertEqual([(o["fact_id"], o["value"], o["window_side"])
                          for o in out["observations"]],
                         [("CPI@2026-11-03", 3.2, "pre"),
                          ("CPI@2026-11-04", 3.25, "pre"),
                          ("CPI@2026-11-06", 3.3, "post")])
        self.assertEqual(out["available"], True)
        self.assertEqual(out["status"], "OK")

    def test_nfp_event_window_golden(self):
        out = dcal.event_window_observations(EV_NFP, "research_snapshot_20261110",
                                             self.snapdir)
        self.assertEqual([(o["fact_id"], o["value"], o["window_side"])
                          for o in out["observations"]],
                         [("NFP_MOM_K@2026-11-06", 150.0, "post")])

    def test_out_of_window_observations_excluded(self):
        out = dcal.event_window_observations(EV_CPI, "research_snapshot_20261110",
                                             self.snapdir)
        # CPI@2026-10-20 在 pre 窗 [10-31,11-04] 之外 → 不得出现
        self.assertNotIn("CPI@2026-10-20",
                         [o["fact_id"] for o in out["observations"]])
        # 其他 metric 观测(NFP_MOM_K/DFEDTARL)不串窗
        self.assertEqual({o["fact_id"].split("@")[0]
                          for o in out["observations"]}, {"CPI"})

    def test_fomc_explicit_metric_window_golden(self):
        out = dcal.event_window_observations(EV_FOMC, "research_snapshot_20261110",
                                             self.snapdir, metric_id="DFEDTARL")
        self.assertEqual([(o["fact_id"], o["value"], o["window_side"])
                          for o in out["observations"]],
                         [("DFEDTARL@2026-11-19", 3.75, "post")])
        self.assertEqual(out["window"]["pre"],
                         {"start": "2026-11-14", "end": "2026-11-18"})


class TestWindowQuality(SandboxBase):

    def test_fail_quality_excluded_and_listed(self):
        out = dcal.event_window_observations(EV_CPI, "research_snapshot_20261110",
                                             self.snapdir)
        self.assertEqual([e["fact_id"] for e in out["excluded_fail"]],
                         ["CPI@2026-11-07"])
        self.assertEqual(out["excluded_fail"][0]["value"], 3.4)   # 如实保留,不填0
        self.assertNotIn("CPI@2026-11-07",
                         [o["fact_id"] for o in out["observations"]])

    def test_non_numeric_excluded_and_listed(self):
        out = dcal.event_window_observations(EV_CPI, "research_snapshot_20261110",
                                             self.snapdir)
        self.assertEqual([e["fact_id"] for e in out["excluded_non_numeric"]],
                         ["CPI@2026-11-08"])
        self.assertEqual(out["excluded_non_numeric"][0]["value"], "N/A")

    def test_zero_qualified_observations_data_insufficient(self):
        # EV_FAR(2026-12-25)窗内快照无该 metric 合格观测 → 如实 DATA_INSUFFICIENT
        out = dcal.event_window_observations(EV_FAR, "research_snapshot_20261110",
                                             self.snapdir, metric_id="CPI")
        self.assertEqual(out["available"], False)
        self.assertEqual(out["status"], "DATA_INSUFFICIENT")
        self.assertEqual(out["observations"], [])

    def test_event_without_binding_requires_metric(self):
        with self.assertRaises(ValueError) as cm:
            dcal.event_window_observations(EV_FOMC, "research_snapshot_20261110",
                                           self.snapdir)
        self.assertIn("不以相近指标冒充", str(cm.exception))


# ══ 要点②: 快照三重纪律(P-D-07) ═══════════════════════════════════════

class TestSnapshotDiscipline(SandboxBase):

    def test_missing_snapshot_rejected(self):
        with self.assertRaises(ValueError) as cm:
            dcal.event_window_observations(
                EV_CPI, "research_snapshot_20261231", self.snapdir)
        self.assertIn("快照接地失败", str(cm.exception))

    def test_gate_a_fail_snapshot_rejected(self):
        with self.assertRaises(ValueError) as cm:
            dcal.event_window_observations(
                EV_CPI, "research_snapshot_20261112", self.snapdir)
        self.assertIn("不放行正式研究", str(cm.exception))

    def test_degraded_snapshot_allowed(self):
        out = dcal.event_window_observations(
            EV_CPI, "research_snapshot_20261111", self.snapdir)
        self.assertEqual(out["gate_a_status"], "DEGRADED")
        self.assertEqual(out["digest_snapshot"], GOLDEN["DIGEST_DEGRADED"])
        self.assertEqual(out["available"], True)

    def test_digest_recomputed_matches_golden_first_principles(self):
        # digest=rp 同款首原理(canonical JSON sha256 前16位),禁采声明值
        blob = json.dumps(SNAP_MAIN, ensure_ascii=False, sort_keys=True)
        manual = hashlib.sha256(blob.encode('utf-8')).hexdigest()[:16]
        self.assertEqual(manual, GOLDEN["DIGEST_MAIN"])
        snap, dg, gs, err = dcal.load_snapshot_disciplined(
            "research_snapshot_20261110", self.snapdir)
        self.assertIsNone(err)
        self.assertEqual(dg, GOLDEN["DIGEST_MAIN"])
        self.assertEqual(gs, "PASS")

    def test_gate_status_echoed_in_window_output(self):
        out = dcal.event_window_observations(
            EV_CPI, "research_snapshot_20261110", self.snapdir)
        self.assertEqual(out["gate_a_status"], "PASS")
        self.assertEqual(out["snapshot_id"], "research_snapshot_20261110")


# ══ 要点②: 快照挂载(P-D-09) ═══════════════════════════════════════════

class TestMountContext(SandboxBase):

    def test_mount_golden_intersecting_events(self):
        ctx = dcal.mount_event_context([EV_CPI, EV_NFP, EV_FOMC],
                                       "research_snapshot_20261110",
                                       self.snapdir)
        self.assertEqual(ctx["snapshot_id"], "research_snapshot_20261110")
        self.assertEqual(ctx["digest_snapshot"], GOLDEN["DIGEST_MAIN"])
        self.assertEqual(ctx["gate_a_status"], "PASS")
        self.assertEqual(ctx["event_ids"],
                         [GOLDEN["EV_NFP"], GOLDEN["EV_CPI"], GOLDEN["EV_FOMC"]])
        self.assertEqual(ctx["future_excluded"], [])

    def test_mount_excludes_nonintersecting_event(self):
        ctx = dcal.mount_event_context([EV_CPI, EV_FAR],
                                       "research_snapshot_20261110",
                                       self.snapdir)
        self.assertEqual(ctx["event_ids"], [GOLDEN["EV_CPI"]])
        self.assertNotIn(GOLDEN["EV_FAR"], ctx["event_ids"])

    def test_mount_as_of_excludes_future_events(self):
        ctx = dcal.mount_event_context([EV_CPI, EV_FOMC],
                                       "research_snapshot_20261110",
                                       self.snapdir, as_of="2026-11-06")
        self.assertEqual(ctx["event_ids"], [GOLDEN["EV_CPI"]])
        self.assertEqual(ctx["future_excluded"],
                         [{"event_id": GOLDEN["EV_FOMC"],
                           "event_date": "2026-11-19",
                           "reason": "event_date>as_of(未来事件,如实排除)"}])

    def test_mount_gate_a_fail_rejected(self):
        with self.assertRaises(ValueError) as cm:
            dcal.mount_event_context([EV_CPI], "research_snapshot_20261112",
                                     self.snapdir)
        self.assertIn("fail-closed", str(cm.exception))

    def test_mount_zero_write_and_invalid_event_rejected(self):
        before = sorted(os.listdir(os.path.join(self.archive))) \
            if os.path.isdir(self.archive) else []
        dcal.mount_event_context([EV_CPI], "research_snapshot_20261110",
                                 self.snapdir)
        after = sorted(os.listdir(self.archive)) \
            if os.path.isdir(self.archive) else []
        self.assertEqual(before, after)          # 读侧纯计算面零写入
        bad = dict(EV_CPI)
        bad["event_type"] = "ECB_RATE_DECISION"
        with self.assertRaises(ValueError):
            dcal.mount_event_context([bad], "research_snapshot_20261110",
                                     self.snapdir)


# ══ 静态纯度与确定性 ════════════════════════════════════════════════════

class TestStaticPurity(unittest.TestCase):

    def test_import_face_whitelist(self):
        import ast
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            '..', 'scripts', 'deep_research_event_calendar.py')
        tree = ast.parse(open(path, encoding='utf-8').read())
        allowed = {"json", "os", "sys", "datetime",
                   "deep_research_registrar", "research_provenance",
                   "fact_engine"}
        seen = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                seen.update(a.name.split('.')[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                seen.add(node.module.split('.')[0])
        self.assertEqual(seen - allowed, set())

    def test_no_raw_daily_path_literal(self):
        src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', 'scripts',
                                'deep_research_event_calendar.py'),
                   encoding='utf-8').read()
        self.assertNotIn("data/daily", src)
        self.assertNotIn("data\\daily", src)

    def test_no_wallclock_calls_in_module(self):
        # 指纹零墙钟: 模块自身无 now/today 调用(_now_iso 复用上游登记件)
        src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', 'scripts',
                                'deep_research_event_calendar.py'),
                   encoding='utf-8').read()
        self.assertNotIn("datetime.now", src.replace("drr._now_iso", ""))
        self.assertNotIn("date.today", src)


class TestDeterminism(unittest.TestCase):

    def test_event_id_first_principles_recompute(self):
        # 测试内 hashlib 首原理复算(禁 import 被测模块计算),与黄金逐值相等
        fp = {"source_id": "SRC_BLS_CPI", "event_type": "INDICATOR_RELEASE",
              "event_date": "2026-11-05", "metric_id": "CPI",
              "note": "美国2026年10月CPI发布(日程登记)"}
        blob = json.dumps(fp, ensure_ascii=False, sort_keys=True)
        h = hashlib.sha256(blob.encode('utf-8')).hexdigest()[:8]
        self.assertEqual("CAL-20261101-" + h, GOLDEN["EV_CPI"])

    def test_cross_sandbox_window_output_byte_equal(self):
        outs = []
        for _ in range(2):
            root = tempfile.mkdtemp(prefix="p2d-det-")
            try:
                sd = write_snapshot(root, SNAP_MAIN)
                outs.append(json.dumps(
                    dcal.event_window_observations(
                        EV_CPI, "research_snapshot_20261110", sd),
                    ensure_ascii=False, sort_keys=True))
            finally:
                shutil.rmtree(root, ignore_errors=True)
        self.assertEqual(outs[0], outs[1])

    def test_replay_register_same_id_across_calls(self):
        root = tempfile.mkdtemp(prefix="p2d-det2-")
        try:
            spec = {"source_id": "SRC_FED", "event_type": "FOMC_RATE_DECISION",
                    "event_date": "2026-12-25", "metric_id": None,
                    "note": "FOMC议息日(远期窗外构造)"}
            r1 = dcal.register_calendar_event(spec, archive_dir=root,
                                              created_at="2026-11-01T08:30:00")
            self.assertEqual(r1["event_id"], GOLDEN["EV_FAR"])
        finally:
            shutil.rmtree(root, ignore_errors=True)


class TestEndToEnd(SandboxBase):

    def test_register_mount_window_full_chain(self):
        # 登记2事件→挂载→窗计算(OK 与 DATA_INSUFFICIENT 混合)全链沙箱内聚
        for spec, ca in (
                ({"source_id": "SRC_BLS_CPI", "event_type": "INDICATOR_RELEASE",
                  "event_date": "2026-11-05", "metric_id": "CPI",
                  "note": "美国2026年10月CPI发布(日程登记)"},
                 "2026-11-01T08:00:00"),
                ({"source_id": "SRC_FED", "event_type": "FOMC_RATE_DECISION",
                  "event_date": "2026-11-19", "metric_id": None,
                  "note": "FOMC议息日(11月会议,日程登记)"},
                 "2026-11-01T08:10:00")):
            dcal.register_calendar_event(spec, archive_dir=self.archive,
                                         created_at=ca)
        evs = dcal.list_calendar_events(archive_dir=self.archive)
        self.assertEqual(len(evs), 2)
        ctx = dcal.mount_event_context(evs, "research_snapshot_20261110",
                                       self.snapdir)
        self.assertEqual(ctx["event_ids"],
                         [GOLDEN["EV_CPI"], GOLDEN["EV_FOMC"]])
        out_ok = dcal.event_window_observations(
            evs[0], "research_snapshot_20261110", self.snapdir)
        self.assertEqual(out_ok["status"], "OK")
        out_far = dcal.event_window_observations(
            evs[1], "research_snapshot_20261110", self.snapdir,
            metric_id="DFEDTARU")
        self.assertEqual(out_far["status"], "DATA_INSUFFICIENT")  # DFEDTARU 无观测
        for out in (out_ok, out_far):
            self.assertIn("不构成投资建议", out["note"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
