#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P3-WP-F 测试件(P3 收尾层第 6 实现包;#38 挂靠)。

全合成 fixture(唯一数据源;零真实档引用)+黄金字面量硬编码(不从被测模块
导入计算;第二源=/tmp/p3-wp-f/fixture_and_golden.py 独立首原理预计算件,
证据包 06 类三方裁定)。零网络零 GLM 零凭证零付费。subprocess 受控仅
TestCLI 一处。

fixture→断言映射表见 docs/P3_WP_F_DELIVERY.md §五。
"""
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "scripts"))
import project_final_seal as pfs  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULE_PATH = os.path.join(REPO_ROOT, "scripts", "project_final_seal.py")

AS_OF = "2026-11-08T12:00:00Z"

# ══ 合成 fixture: 迷你归档仓(10 层×1 件;与首原理件同源) ══

MINI_INDEX = {
    "L0-gov": ("docs/A_GOV.md",),
    "L1-p02": ("docs/B_P02.md",),
    "L1w3-dataw3": ("docs/C_W3.md",),
    "L2a-e2ea": ("docs/D_E2EA.md",),
    "L2fa-p03fa": ("docs/E_FA.md",),
    "L2b-e2eb": ("docs/F_E2EB.md",),
    "L3-glm": ("docs/G_GLM.md",),
    "L4-p1": ("docs/H_P1.md",),
    "L5-p2": ("docs/I_P2.md",),
    "L6-p3": ("scripts/J_P3.py",),
}


def build_mini_repo(root):
    for layer, rels in MINI_INDEX.items():
        for rel in rels:
            full = os.path.join(root, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as fh:
                fh.write("FIXTURE:" + layer + "\n")


def seven_table_all_pass():
    table = {}
    for i in range(1, 8):
        table["AC-0%d" % i] = {"evidence": "ev-0%d" % i,
                               "note": "note-0%d" % i, "verdict": "PASS"}
    return table


def seven_table_ac03_fail():
    table = seven_table_all_pass()
    row = dict(table["AC-03"])
    row["verdict"] = "FAIL"
    table["AC-03"] = row
    return table


def fresh_state(test):
    tmp = tempfile.mkdtemp(prefix="p3wpf-")
    test.addCleanup(shutil.rmtree, tmp, True)
    return os.path.join(tmp, "journal.jsonl"), tmp


def compile_on_mini(test, seven_table, remove_rel=None):
    state, tmp = fresh_state(test)
    repo = os.path.join(tmp, "mini")
    build_mini_repo(repo)
    if remove_rel:
        os.remove(os.path.join(repo, remove_rel))
    out = os.path.join(tmp, "out")
    pfs.write_baseline(state, AS_OF)
    pfs.start_final_acceptance(state, AS_OF)
    doc = pfs.compile_seal_determination(
        repo, state, seven_table, AS_OF, out_dir=out,
        archive_index={k: list(v) for k, v in MINI_INDEX.items()})
    return doc, state, out, repo


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


# ══ 黄金字面量(硬编码;来源=/tmp/p3-wp-f/fixture_and_golden.py 独立首原理
#    预计算件输出 /tmp/p3-wp-f/golden_values.json,零被测模块 import) ══

GOLDEN_FA_DIGEST = ("e13399ad60c834a4f5a1e2178a112a7ebf17f509"
                    "65e0e11fd1fbfb601987fe23")
GOLDEN_MINI_LAYER_DIGESTS = {
    "L0-gov": "4785ef3f6cc76e03e9470f553d13aab2a8a88041d49bfb0a7a6e33fe369e439e",
    "L1-p02": "320c9b718e892077c88cf37d5013a1607b355ba3d288f62efe66604b315b8134",
    "L1w3-dataw3": "2317e4a330c41572659be3155f34190389461a4b99e2832ebbf0230975755ff4",
    "L2a-e2ea": "6c9a870301549ba74bd747582fac463ceb91a6c8822fa704f70ee0b7fc948c02",
    "L2b-e2eb": "ef58f9a5a5e5d1ef357bd057e355d21c79b5fb42b0d0d088e06792342a32affb",
    "L2fa-p03fa": "3ad6b6847e8e9a0e76dcfee21e42f5f05b8f538d61a743a6a6eb990606c61b0c",
    "L3-glm": "0457eac283ccfad21e6473bfb27cd143d84ab93a9c9aabbbd27f7dc1f2adc555",
    "L4-p1": "5f386ececcfbc0ee1671e9279237e0c361c3332342eeb7b0e61670471543666d",
    "L5-p2": "5e52c2e33e39d695ddcdf99858f453bba898dfeed849f356d6c2b54c997f478e",
    "L6-p3": "19490b85ff994cf10cdcf1ebf33f2e948663bfa8799ce91764d9c0c477fb132e",
}
GOLDEN_MINI_OVERALL = ("e82fcd20458cdee817b34f77cc0165a239925789a"
                       "5370edd7b44ec6020919ec7")
GOLDEN_GREEN_JSON_SHA = ("801a592827ac85c71044e493775264676795b8b5"
                         "6c6a286861605536b6702b12")
GOLDEN_GREEN_MD_SHA = ("a05c8990128eac8e33871d25d851f54669b9b75cbda"
                       "23ed235f066583a1acd9f")
GOLDEN_FAIL_JSON_SHA = ("d7ac88068bdf86bc02da2c7b944b9a8c2fdf31af"
                        "f0794096c2956e34d05b48f9")
GOLDEN_FAIL_MD_SHA = ("30c0c9616ee902d2fbc80bc01728969b8dd66afe1f"
                      "e8fd73c139dc9fd5640c52")
GOLDEN_JOURNAL_BASELINE = (
    '{"as_of": "2026-11-08T12:00:00Z", "fa_digest": "e13399ad60c834a4f5a1e2'
    '178a112a7ebf17f50965e0e11fd1fbfb601987fe23", "journal_schema_version": '
    '1, "record_type": "baseline"}')
GOLDEN_JOURNAL_STARTED = (
    '{"as_of": "2026-11-08T12:00:00Z", "fa_digest": "e13399ad60c834a4f5a1e2'
    '178a112a7ebf17f50965e0e11fd1fbfb601987fe23", "journal_schema_version": '
    '1, "record_type": "started"}')
GOLDEN_JOURNAL_COMPILED = (
    '{"as_of": "2026-11-08T12:00:00Z", "determination": "PENDING_SUPPLEMENT'
    'ARY_EVIDENCE", "fa_digest": "e13399ad60c834a4f5a1e2178a112a7ebf17f50965'
    'e0e11fd1fbfb601987fe23", "journal_schema_version": 1, "materials_json_sh'
    'a256": "801a592827ac85c71044e493775264676795b8b56c6a286861605536b6702b1'
    '2", "materials_md_sha256": "a05c8990128eac8e33871d25d851f54669b9b75cbda'
    '23ed235f066583a1acd9f", "record_type": "compiled"}')


class TestGoldenFirstPrinciples(unittest.TestCase):
    """黄金双源: 模块输出 vs 首原理预计算字面量(逐值等值)。"""

    def test_fa_digest_golden(self):
        self.assertEqual(pfs.fa_digest(), GOLDEN_FA_DIGEST)

    def test_determine_goldens(self):
        self.assertEqual(pfs.determine(["PASS"] * 24), "SEALED")
        self.assertEqual(pfs.determine(["PASS", "NOT_VERIFIED"]),
                         "PENDING_SUPPLEMENTARY_EVIDENCE")
        self.assertEqual(pfs.determine(["PASS", "NOT_VERIFIED", "FAIL"]),
                         "NOT_SEALED")
        self.assertEqual(pfs.determine([]), "SEALED")

    def test_calendar_goldens(self):
        self.assertEqual(pfs.add_days("2026-11-05", 30), "2026-12-05")
        self.assertEqual(pfs.days_between("2026-11-05", "2026-11-08"), 3)

    def test_mini_layer_digests_golden(self):
        state, tmp = fresh_state(self)
        repo = os.path.join(tmp, "mini")
        build_mini_repo(repo)
        result = pfs.verify_archive_index(
            repo, {k: list(v) for k, v in MINI_INDEX.items()})
        self.assertEqual({row["layer_id"]: row["digest"]
                          for row in result["layers"]},
                         GOLDEN_MINI_LAYER_DIGESTS)
        self.assertEqual(result["overall_digest"], GOLDEN_MINI_OVERALL)


class TestCalendar(unittest.TestCase):
    """零 datetime 纯日历(月长表+闰年含世纪规则;3.9/3.11 一致由构造)。"""

    def test_parse_ok(self):
        self.assertEqual(pfs.parse_ymd("2026-11-08"), (2026, 11, 8))
        self.assertEqual(pfs.parse_ymd("2024-02-29"), (2024, 2, 29))
        self.assertEqual(pfs.parse_ymd("2000-02-29"), (2000, 2, 29))
        self.assertEqual(pfs.parse_ymd("0001-01-01"), (1, 1, 1))

    def test_parse_rejects_non_canonical(self):
        for bad in ("20261105", "2026-11-5", "2026-1-08", "2026-11-05x",
                    "2026/11/08", "2026-W45-4", "", "2026-11-05 ",
                    20261105, None):
            with self.assertRaises(ValueError):
                pfs.parse_ymd(bad)

    def test_parse_rejects_bounds(self):
        for bad in ("2026-13-01", "2026-00-10", "2026-11-00", "2026-11-31",
                    "2026-02-29", "2026-02-30", "1900-02-29", "0000-01-01",
                    "2026-04-31"):
            with self.assertRaises(ValueError):
                pfs.parse_ymd(bad)

    def test_ordinal_identity_and_roundtrip(self):
        self.assertEqual(pfs.ymd_to_ordinal("0001-01-01"), 1)
        self.assertEqual(pfs.ordinal_to_ymd(1), "0001-01-01")
        self.assertEqual(pfs.ordinal_to_ymd(366), "0002-01-01")
        for probe in ("2026-11-05", "2026-12-05", "2024-02-29", "2000-02-29",
                      "1900-03-01", "0001-12-31"):
            self.assertEqual(pfs.ordinal_to_ymd(pfs.ymd_to_ordinal(probe)),
                             probe)

    def test_ordinal_rejects_non_positive(self):
        for bad in (0, -1, 1.5, "1", None):
            with self.assertRaises(ValueError):
                pfs.ordinal_to_ymd(bad)

    def test_add_days_rollovers(self):
        self.assertEqual(pfs.add_days("2026-01-31", 1), "2026-02-01")
        self.assertEqual(pfs.add_days("2024-02-28", 1), "2024-02-29")
        self.assertEqual(pfs.add_days("2026-02-28", 1), "2026-03-01")
        self.assertEqual(pfs.add_days("2026-12-31", 1), "2027-01-01")
        self.assertEqual(pfs.add_days("2026-11-08", 0), "2026-11-08")

    def test_add_days_negative_before_epoch_raises(self):
        with self.assertRaises(ValueError):
            pfs.add_days("0001-01-01", -1)

    def test_days_between_signed(self):
        self.assertEqual(pfs.days_between("2026-11-08", "2026-11-05"), -3)
        self.assertEqual(pfs.days_between("2026-11-05", "2026-11-05"), 0)


class TestAsOfGuard(unittest.TestCase):
    """as_of 规范形守卫(YYYY-MM-DDTHH:MM:SSZ 二十位)。"""

    def test_accepts_canonical(self):
        self.assertEqual(pfs._validate_as_of(AS_OF), AS_OF)
        self.assertEqual(pfs._validate_as_of("2026-12-05T23:59:59Z"),
                         "2026-12-05T23:59:59Z")

    def test_rejects_shape(self):
        for bad in ("2026-11-08 12:00:00Z", "2026-11-08T12:00:00",
                    "2026-11-08T12:00:00z", "20261108T120000Z", "", None,
                    20261108, "2026-11-08T12:00:00Z ", "x" * 20):
            with self.assertRaises(ValueError):
                pfs._validate_as_of(bad)

    def test_rejects_out_of_range(self):
        for bad in ("2026-13-08T12:00:00Z", "2026-02-30T12:00:00Z",
                    "2026-11-08T24:00:00Z", "2026-11-08T12:60:00Z",
                    "2026-11-08T12:00:60Z", "2026-11-08Tab:00:00Z",
                    "2026-11-08T12:c0:00Z"):
            with self.assertRaises(ValueError):
                pfs._validate_as_of(bad)


class TestPathGuards(unittest.TestCase):
    """LIVE 根四组件序列拒+data/daily 相邻组件拒(全部读写面)。"""

    LIVE_TAIL = ("AI内容", "🤖_AI投资项目", "每周宏观追踪", "investment-agent")

    def live_path(self, tail_name):
        return "/tmp/" + "/".join(self.LIVE_TAIL) + "/" + tail_name

    def test_live_root_absolute_rejected(self):
        with self.assertRaises(ValueError):
            pfs._guarded_path(self.live_path("x.json"))

    def test_live_root_relative_rejected(self):
        with self.assertRaises(ValueError):
            pfs._guarded_path("/".join(self.LIVE_TAIL) + "/a/b.md")

    def test_live_root_tilde_rejected(self):
        with self.assertRaises(ValueError):
            pfs._guarded_path("~/" + "/".join(self.LIVE_TAIL) + "/c.jsonl")

    def test_data_daily_adjacent_rejected(self):
        with self.assertRaises(ValueError):
            pfs._guarded_path("data/daily/x.json")
        with self.assertRaises(ValueError):
            pfs._guarded_path("a/b/data/daily/c")
        with self.assertRaises(ValueError):
            pfs._guarded_path("/tmp/data/daily/notes.jsonl")

    def test_adjacent_must_be_exact_components(self):
        self.assertEqual(pfs._guarded_path("data/dailyx/a.json"),
                         os.path.normpath("data/dailyx/a.json"))
        self.assertEqual(pfs._guarded_path("datax/daily/a.json"),
                         os.path.normpath("datax/daily/a.json"))
        self.assertEqual(pfs._guarded_path("data/research/p3_final_seal/"
                                           "journal.jsonl"),
                         os.path.normpath("data/research/p3_final_seal/"
                                          "journal.jsonl"))

    def test_dot_and_plain_paths_pass(self):
        self.assertEqual(pfs._guarded_path("."), ".")
        self.assertEqual(pfs._guarded_path("docs/A_GOV.md"),
                         os.path.normpath("docs/A_GOV.md"))

    def test_io_helpers_guarded(self):
        state, tmp = fresh_state(self)
        with self.assertRaises(ValueError):
            pfs._read_bytes(self.live_path("x.json"))
        with self.assertRaises(ValueError):
            pfs._append_journal_line("data/daily/j.jsonl", "{}\n")
        with self.assertRaises(ValueError):
            pfs._write_text_once(self.live_path("y.md"), "y")
        self.assertEqual(os.listdir(tmp), [])

    def test_verify_archive_index_guards_repo_root(self):
        with self.assertRaises(ValueError):
            pfs.verify_archive_index(
                "/tmp/" + "/".join(self.LIVE_TAIL),
                {"LX": ["docs/a.md"]})

    def test_compile_guards_repo_root(self):
        state, tmp = fresh_state(self)
        pfs.write_baseline(state, AS_OF)
        pfs.start_final_acceptance(state, AS_OF)
        with self.assertRaises(ValueError):
            pfs.compile_seal_determination(
                "/tmp/" + "/".join(self.LIVE_TAIL), state,
                seven_table_all_pass(), AS_OF)


class TestJournalStateMachine(unittest.TestCase):
    """JSONL append-only 状态机(baseline→started→compiled 单发链)。"""

    def test_read_missing_returns_empty(self):
        state, _tmp = fresh_state(self)
        self.assertEqual(pfs.read_journal(state), [])

    def test_baseline_writes_one_golden_line(self):
        state, _tmp = fresh_state(self)
        record = pfs.write_baseline(state, AS_OF)
        self.assertEqual(record, {"record_type": "baseline",
                                  "journal_schema_version": 1,
                                  "as_of": AS_OF,
                                  "fa_digest": GOLDEN_FA_DIGEST})
        with open(state, "r", encoding="utf-8") as fh:
            content = fh.read()
        self.assertEqual(content, GOLDEN_JOURNAL_BASELINE + "\n")

    def test_baseline_twice_rejected(self):
        state, _tmp = fresh_state(self)
        pfs.write_baseline(state, AS_OF)
        with self.assertRaises(ValueError):
            pfs.write_baseline(state, AS_OF)

    def test_started_requires_baseline(self):
        state, _tmp = fresh_state(self)
        with self.assertRaises(ValueError):
            pfs.start_final_acceptance(state, AS_OF)

    def test_started_writes_golden_line(self):
        state, _tmp = fresh_state(self)
        pfs.write_baseline(state, AS_OF)
        pfs.start_final_acceptance(state, AS_OF)
        with open(state, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        self.assertEqual(lines, [GOLDEN_JOURNAL_BASELINE,
                                 GOLDEN_JOURNAL_STARTED])

    def test_started_twice_rejected(self):
        state, _tmp = fresh_state(self)
        pfs.write_baseline(state, AS_OF)
        pfs.start_final_acceptance(state, AS_OF)
        with self.assertRaises(ValueError):
            pfs.start_final_acceptance(state, AS_OF)

    def test_read_journal_fail_loud_malformed(self):
        state, _tmp = fresh_state(self)
        with open(state, "w", encoding="utf-8") as fh:
            fh.write("{not json}\n")
        with self.assertRaises(ValueError):
            pfs.read_journal(state)

    def test_read_journal_fail_loud_blank_line(self):
        state, _tmp = fresh_state(self)
        with open(state, "w", encoding="utf-8") as fh:
            fh.write("\n")
        with self.assertRaises(ValueError):
            pfs.read_journal(state)

    def test_read_journal_fail_loud_non_dict(self):
        state, _tmp = fresh_state(self)
        with open(state, "w", encoding="utf-8") as fh:
            fh.write("[1,2]\n")
        with self.assertRaises(ValueError):
            pfs.read_journal(state)

    def test_read_journal_fail_loud_bad_record_type(self):
        state, _tmp = fresh_state(self)
        with open(state, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"record_type": "amended",
                                 "journal_schema_version": 1,
                                 "as_of": AS_OF,
                                 "fa_digest": "x" * 64}) + "\n")
        with self.assertRaises(ValueError):
            pfs.read_journal(state)

    def test_read_journal_fail_loud_bad_schema_version(self):
        state, _tmp = fresh_state(self)
        with open(state, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"record_type": "baseline",
                                 "journal_schema_version": 2,
                                 "as_of": AS_OF,
                                 "fa_digest": "x" * 64}) + "\n")
        with self.assertRaises(ValueError):
            pfs.read_journal(state)

    def test_read_journal_fail_loud_extra_field(self):
        state, _tmp = fresh_state(self)
        with open(state, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"record_type": "baseline",
                                 "journal_schema_version": 1,
                                 "as_of": AS_OF,
                                 "fa_digest": "x" * 64,
                                 "surprise": 1}) + "\n")
        with self.assertRaises(ValueError):
            pfs.read_journal(state)

    def test_read_journal_fail_loud_compiled_missing_determination(self):
        state, _tmp = fresh_state(self)
        with open(state, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"record_type": "compiled",
                                 "journal_schema_version": 1,
                                 "as_of": AS_OF,
                                 "fa_digest": "x" * 64}) + "\n")
        with self.assertRaises(ValueError):
            pfs.read_journal(state)


class TestAmendmentRejection(unittest.TestCase):
    """L208④ 恒拒面: 终验开始后回改清单被拒;登记后亦禁回改。"""

    def test_amendment_before_registration_rejected(self):
        state, _tmp = fresh_state(self)
        with self.assertRaises(ValueError):
            pfs.propose_checklist_amendment(state, "add item")

    def test_amendment_after_baseline_rejected(self):
        state, _tmp = fresh_state(self)
        pfs.write_baseline(state, AS_OF)
        with self.assertRaises(ValueError):
            pfs.propose_checklist_amendment(state, "add item")

    def test_amendment_after_started_rejected(self):
        state, _tmp = fresh_state(self)
        pfs.write_baseline(state, AS_OF)
        pfs.start_final_acceptance(state, AS_OF)
        with self.assertRaises(ValueError):
            pfs.propose_checklist_amendment(state, "add item")


class TestDigestChainTamper(unittest.TestCase):
    """禁回改 digest 链: 登记值被回改→指纹漂移→start/compile 拒。"""

    def test_checklist_mutation_detected_at_start(self):
        state, _tmp = fresh_state(self)
        pfs.write_baseline(state, AS_OF)
        mutated = pfs.registered_checklist()
        mutated[0]["requirement"] = mutated[0]["requirement"] + " (改)"
        with mock.patch.object(pfs, "registered_checklist",
                               return_value=mutated):
            self.assertNotEqual(pfs.fa_digest(), GOLDEN_FA_DIGEST)
            with self.assertRaises(ValueError):
                pfs.start_final_acceptance(state, AS_OF)

    def test_timing_mutation_detected_at_start(self):
        state, _tmp = fresh_state(self)
        pfs.write_baseline(state, AS_OF)
        mutated = dict(pfs.registered_timing(),
                       observation_window_days=29)
        with mock.patch.object(pfs, "registered_timing",
                               return_value=mutated):
            with self.assertRaises(ValueError):
                pfs.start_final_acceptance(state, AS_OF)

    def test_checklist_mutation_detected_at_compile(self):
        state, tmp = fresh_state(self)
        repo = os.path.join(tmp, "mini")
        build_mini_repo(repo)
        pfs.write_baseline(state, AS_OF)
        pfs.start_final_acceptance(state, AS_OF)
        mutated = pfs.registered_checklist()
        mutated[3]["title"] = "篡改"
        with mock.patch.object(pfs, "registered_checklist",
                               return_value=mutated):
            with self.assertRaises(ValueError):
                pfs.compile_seal_determination(
                    repo, state, seven_table_all_pass(), AS_OF,
                    archive_index={k: list(v)
                                   for k, v in MINI_INDEX.items()})


class TestArchiveIndexVerify(unittest.TestCase):
    """归档索引在场核验(缺席如实记录不美化;索引结构校验)。"""

    def mini(self):
        state, tmp = fresh_state(self)
        repo = os.path.join(tmp, "mini")
        build_mini_repo(repo)
        return repo, tmp

    def test_all_present_counts(self):
        repo, _tmp = self.mini()
        result = pfs.verify_archive_index(
            repo, {k: list(v) for k, v in MINI_INDEX.items()})
        self.assertEqual(result["total_files"], 10)
        self.assertEqual(result["total_present"], 10)
        self.assertEqual(result["total_missing"], 0)
        self.assertEqual(result["missing_paths"], [])
        self.assertEqual([row["layer_id"] for row in result["layers"]],
                         sorted(MINI_INDEX))
        for row in result["layers"]:
            self.assertEqual(row["files_present"], row["files_total"])

    def test_missing_file_recorded_verbatim(self):
        repo, _tmp = self.mini()
        os.remove(os.path.join(repo, "docs", "B_P02.md"))
        result = pfs.verify_archive_index(
            repo, {k: list(v) for k, v in MINI_INDEX.items()})
        self.assertEqual(result["total_missing"], 1)
        self.assertEqual(result["missing_paths"], ["docs/B_P02.md"])
        l1 = result["layers_by_id"]["L1-p02"]
        self.assertEqual(l1["files_present"], 0)
        self.assertEqual(l1["files_missing"], ["docs/B_P02.md"])
        self.assertNotEqual(l1["digest"],
                            GOLDEN_MINI_LAYER_DIGESTS["L1-p02"])
        self.assertNotEqual(result["overall_digest"], GOLDEN_MINI_OVERALL)

    def test_index_rejects_non_dict(self):
        with self.assertRaises(ValueError):
            pfs.verify_archive_index("/tmp", ["L0"])

    def test_index_rejects_empty_dict(self):
        with self.assertRaises(ValueError):
            pfs.verify_archive_index("/tmp", {})

    def test_index_rejects_string_files(self):
        with self.assertRaises(ValueError):
            pfs.verify_archive_index("/tmp", {"L0": "docs/a.md"})

    def test_index_rejects_non_string_entry(self):
        with self.assertRaises(ValueError):
            pfs.verify_archive_index("/tmp", {"L0": [123]})

    def test_index_rejects_empty_layer_id(self):
        with self.assertRaises(ValueError):
            pfs.verify_archive_index("/tmp", {"": ["docs/a.md"]})


class TestSevenAcValidation(unittest.TestCase):
    """七 AC 复演输入契约(键集/字段/verdict 值域封闭)。"""

    def test_valid_table_passthrough(self):
        table = seven_table_all_pass()
        self.assertIs(pfs.validate_seven_ac_selfcheck(table), table)

    def test_rejects_non_dict(self):
        with self.assertRaises(ValueError):
            pfs.validate_seven_ac_selfcheck([seven_table_all_pass()])

    def test_rejects_missing_key(self):
        table = seven_table_all_pass()
        del table["AC-05"]
        with self.assertRaises(ValueError):
            pfs.validate_seven_ac_selfcheck(table)

    def test_rejects_extra_key(self):
        table = seven_table_all_pass()
        table["AC-08"] = {"evidence": "e", "note": "n", "verdict": "PASS"}
        with self.assertRaises(ValueError):
            pfs.validate_seven_ac_selfcheck(table)

    def test_rejects_bad_verdict(self):
        table = seven_table_all_pass()
        table["AC-02"]["verdict"] = "PASS_WITH_CAVEAT"
        with self.assertRaises(ValueError):
            pfs.validate_seven_ac_selfcheck(table)

    def test_rejects_empty_evidence(self):
        table = seven_table_all_pass()
        table["AC-01"]["evidence"] = "  "
        with self.assertRaises(ValueError):
            pfs.validate_seven_ac_selfcheck(table)

    def test_rejects_non_string_note(self):
        table = seven_table_all_pass()
        table["AC-03"]["note"] = 3
        with self.assertRaises(ValueError):
            pfs.validate_seven_ac_selfcheck(table)

    def test_rejects_non_dict_row(self):
        table = seven_table_all_pass()
        table["AC-04"] = ["bad"]
        with self.assertRaises(ValueError):
            pfs.validate_seven_ac_selfcheck(table)

    def test_rejects_extra_row_field(self):
        table = seven_table_all_pass()
        table["AC-07"]["extra"] = "x"
        with self.assertRaises(ValueError):
            pfs.validate_seven_ac_selfcheck(table)

    def test_rejects_missing_row_field(self):
        table = seven_table_all_pass()
        del table["AC-06"]["note"]
        with self.assertRaises(ValueError):
            pfs.validate_seven_ac_selfcheck(table)


class TestCompileGreenPath(unittest.TestCase):
    """绿路汇编(全 PASS+全在场→PENDING_SUPPLEMENTARY_EVIDENCE)。"""

    def compile_green(self):
        return compile_on_mini(self, seven_table_all_pass())

    def test_determination_pending(self):
        doc, _state, _out, _repo = self.compile_green()
        self.assertEqual(doc["determination"],
                         "PENDING_SUPPLEMENTARY_EVIDENCE")

    def test_verdict_counts_and_sections(self):
        doc, _state, _out, _repo = self.compile_green()
        rows = doc["checklist_verdicts"]
        self.assertEqual(len(rows), 24)
        by_id = {row["item_id"]: row for row in rows}
        for i in range(1, 8):
            self.assertEqual(by_id["FA-S1-AC-0%d" % i]["verdict"], "PASS")
        for i in range(1, 11):
            self.assertEqual(by_id["FA-S2-%02d" % i]["verdict"], "PASS")
        self.assertEqual(by_id["FA-S2-11"]["verdict"], "NOT_VERIFIED")
        self.assertEqual(by_id["FA-S3-01"]["verdict"], "PASS")
        self.assertEqual(by_id["FA-S4-01"]["verdict"], "NOT_VERIFIED")
        self.assertEqual(by_id["FA-S4-02"]["verdict"], "NOT_VERIFIED")
        self.assertEqual(by_id["FA-S4-03"]["verdict"], "PASS")
        self.assertEqual(by_id["FA-S5-01"]["verdict"], "PASS")
        self.assertEqual(by_id["FA-S6-01"]["verdict"], "PASS")
        nv = [r for r in rows if r["verdict"] == "NOT_VERIFIED"]
        self.assertEqual(len(nv), 3)
        self.assertEqual(doc["fail_items"], [])

    def test_sealed_unreachable_in_compile(self):
        """S4①② 恒 NOT_VERIFIED(零预执行)→compile 面 SEALED 结构性不可达。"""
        doc, _state, _out, _repo = self.compile_green()
        self.assertNotEqual(doc["determination"], "SEALED")

    def test_runtime_window_fields(self):
        doc, _state, _out, _repo = self.compile_green()
        rw = doc["runtime_window"]
        self.assertEqual(rw["start"], "2026-11-05")
        self.assertEqual(rw["end"], "2026-12-05")
        self.assertEqual(rw["window_days"], 30)
        self.assertEqual(rw["elapsed_days_at_as_of"], 3)
        self.assertEqual(rw["carrier"], "R018_parked_artifact")
        self.assertEqual(rw["thresholds"]["min_scheduled_execution_days"], 7)
        self.assertEqual(rw["thresholds"]["min_weekly_regressions"], 1)
        self.assertEqual(rw["thresholds"]["min_observation_days"], 30)
        self.assertEqual(rw["thresholds"]["min_task_success_rate_pct"], 95)
        self.assertEqual(rw["thresholds"]["min_formal_weekly_reports"], 4)
        self.assertEqual(rw["zero_preexecution"], True)

    def test_seven_ac_provenance_echo(self):
        doc, _state, _out, _repo = self.compile_green()
        rows = doc["seven_ac_reverification"]
        self.assertEqual([r["ac_id"] for r in rows],
                         ["AC-0%d" % i for i in range(1, 8)])
        for i, row in enumerate(rows, start=1):
            self.assertEqual(row["verdict"], "PASS")
            self.assertEqual(row["evidence"], "ev-0%d" % i)
            self.assertEqual(row["note"], "note-0%d" % i)
        self.assertIn("REPORT §四", rows[0]["provenance"])
        self.assertIn("R043", rows[0]["provenance"])

    def test_l6_p3f_presence_only_row(self):
        doc, _state, _out, _repo = self.compile_green()
        row = doc["layer_closure"][-1]
        self.assertEqual(row["layer_id"], "L6-p3f")
        self.assertEqual(row["verdict"], "NOT_VERIFIED")
        self.assertEqual(row["files_total"], 4)
        self.assertEqual(row["files_present"], 0)
        self.assertEqual(row["files_missing"], list(pfs.SELF_EXCLUDED_PATHS))

    def test_doc_keys_closed_set(self):
        doc, _state, _out, _repo = self.compile_green()
        expected = sorted(pfs.SEAL_DOC_FIELDS + ("journal_compiled_record",))
        self.assertEqual(sorted(doc.keys()), expected)

    def test_archive_block_goldens(self):
        doc, _state, _out, _repo = self.compile_green()
        index = doc["archive_index"]
        self.assertEqual(index["total_files"], 10)
        self.assertEqual(index["total_present"], 10)
        self.assertEqual(index["overall_digest"], GOLDEN_MINI_OVERALL)
        self.assertEqual({row["layer_id"]: row["digest"]
                          for row in index["layers"]},
                         GOLDEN_MINI_LAYER_DIGESTS)
        self.assertEqual(index["self_excluded"],
                         list(pfs.SELF_EXCLUDED_PATHS))

    def test_materials_golden_shas(self):
        doc, state, out, _repo = self.compile_green()
        with open(os.path.join(out, "seal_determination.json"), "rb") as fh:
            json_bytes = fh.read()
        self.assertTrue(json_bytes.endswith(b"\n"))
        self.assertEqual(sha256_bytes(json_bytes[:-1]),
                         GOLDEN_GREEN_JSON_SHA)
        with open(os.path.join(out, "seal_determination.md"), "rb") as fh:
            md_bytes = fh.read()
        self.assertEqual(sha256_bytes(md_bytes), GOLDEN_GREEN_MD_SHA)
        compiled = doc["journal_compiled_record"]
        self.assertEqual(compiled["materials_json_sha256"],
                         GOLDEN_GREEN_JSON_SHA)
        self.assertEqual(compiled["materials_md_sha256"],
                         GOLDEN_GREEN_MD_SHA)

    def test_journal_three_golden_lines(self):
        _doc, state, _out, _repo = self.compile_green()
        with open(state, "r", encoding="utf-8") as fh:
            content = fh.read()
        self.assertEqual(content, GOLDEN_JOURNAL_BASELINE + "\n"
                         + GOLDEN_JOURNAL_STARTED + "\n"
                         + GOLDEN_JOURNAL_COMPILED + "\n")

    def test_second_compile_rejected(self):
        doc, state, out, repo = self.compile_green()
        with self.assertRaises(ValueError):
            pfs.compile_seal_determination(
                repo, state, seven_table_all_pass(), AS_OF, out_dir=out,
                archive_index={k: list(v) for k, v in MINI_INDEX.items()})

    def test_out_dir_none_no_files_but_compiled_appended(self):
        state, tmp = fresh_state(self)
        repo = os.path.join(tmp, "mini")
        build_mini_repo(repo)
        pfs.write_baseline(state, AS_OF)
        pfs.start_final_acceptance(state, AS_OF)
        doc = pfs.compile_seal_determination(
            repo, state, seven_table_all_pass(), AS_OF,
            archive_index={k: list(v) for k, v in MINI_INDEX.items()})
        self.assertEqual(doc["determination"],
                         "PENDING_SUPPLEMENTARY_EVIDENCE")
        self.assertEqual(sorted(os.listdir(tmp)), ["journal.jsonl", "mini"])
        compiled = doc["journal_compiled_record"]
        self.assertIsNone(compiled["materials_json_sha256"])
        self.assertIsNone(compiled["materials_md_sha256"])


class TestCompileFailPath(unittest.TestCase):
    """败路汇编(AC-03 FAIL→NOT_SEALED;FAIL 项逐字留档)。"""

    def test_determination_not_sealed(self):
        doc, _state, _out, _repo = compile_on_mini(self,
                                                   seven_table_ac03_fail())
        self.assertEqual(doc["determination"], "NOT_SEALED")

    def test_fail_items_verbatim(self):
        doc, _state, _out, _repo = compile_on_mini(self,
                                                   seven_table_ac03_fail())
        self.assertEqual([row["item_id"] for row in doc["fail_items"]],
                         ["FA-S1-AC-03"])
        failed = doc["fail_items"][0]
        self.assertIn("evidence=ev-03", failed["detail"])
        self.assertEqual(failed["verdict"], "FAIL")

    def test_materials_golden_shas(self):
        doc, _state, out, _repo = compile_on_mini(self,
                                                  seven_table_ac03_fail())
        with open(os.path.join(out, "seal_determination.json"), "rb") as fh:
            json_bytes = fh.read()
        self.assertEqual(sha256_bytes(json_bytes[:-1]),
                         GOLDEN_FAIL_JSON_SHA)
        with open(os.path.join(out, "seal_determination.md"), "rb") as fh:
            self.assertEqual(sha256_bytes(fh.read()), GOLDEN_FAIL_MD_SHA)
        compiled = doc["journal_compiled_record"]
        self.assertEqual(compiled["determination"], "NOT_SEALED")


class TestCompileMissingArchive(unittest.TestCase):
    """缺席如实: 迷你仓缺 1 件→S2 层 FAIL+S3 FAIL→NOT_SEALED。"""

    def test_missing_layer_file_fails(self):
        doc, _state, _out, _repo = compile_on_mini(
            self, seven_table_all_pass(), remove_rel="docs/B_P02.md")
        self.assertEqual(doc["determination"], "NOT_SEALED")
        self.assertEqual([row["item_id"] for row in doc["fail_items"]],
                         ["FA-S2-02", "FA-S3-01"])
        self.assertEqual(doc["archive_index"]["missing_paths"],
                         ["docs/B_P02.md"])
        l1 = [row for row in doc["layer_closure"]
              if row["layer_id"] == "L1-p02"][0]
        self.assertEqual(l1["verdict"], "FAIL")
        self.assertEqual(l1["files_missing"], ["docs/B_P02.md"])
        self.assertIn("缺席如实登记: ['docs/B_P02.md']", l1["note"])


class TestCompileStatePreconditions(unittest.TestCase):
    """状态机前置: 未 started 拒汇编;坏七AC表拒汇编。"""

    def test_compile_before_started_rejected(self):
        state, tmp = fresh_state(self)
        repo = os.path.join(tmp, "mini")
        build_mini_repo(repo)
        pfs.write_baseline(state, AS_OF)
        with self.assertRaises(ValueError):
            pfs.compile_seal_determination(
                repo, state, seven_table_all_pass(), AS_OF,
                archive_index={k: list(v) for k, v in MINI_INDEX.items()})

    def test_compile_without_baseline_rejected(self):
        state, tmp = fresh_state(self)
        repo = os.path.join(tmp, "mini")
        build_mini_repo(repo)
        with self.assertRaises(ValueError):
            pfs.compile_seal_determination(
                repo, state, seven_table_all_pass(), AS_OF,
                archive_index={k: list(v) for k, v in MINI_INDEX.items()})

    def test_compile_rejects_bad_seven_ac_table(self):
        state, tmp = fresh_state(self)
        repo = os.path.join(tmp, "mini")
        build_mini_repo(repo)
        pfs.write_baseline(state, AS_OF)
        pfs.start_final_acceptance(state, AS_OF)
        bad = seven_table_all_pass()
        bad["AC-01"]["verdict"] = "MAYBE"
        with self.assertRaises(ValueError):
            pfs.compile_seal_determination(
                repo, state, bad, AS_OF,
                archive_index={k: list(v) for k, v in MINI_INDEX.items()})

    def test_compile_rejects_bad_as_of(self):
        state, tmp = fresh_state(self)
        repo = os.path.join(tmp, "mini")
        build_mini_repo(repo)
        with self.assertRaises(ValueError):
            pfs.compile_seal_determination(
                repo, state, seven_table_all_pass(), "2026-11-08 12:00:00Z",
                archive_index={k: list(v) for k, v in MINI_INDEX.items()})


class TestRender(unittest.TestCase):
    """人读渲染(如实不美化;免责尾行)。"""

    def test_green_render_structure(self):
        doc, _state, _out, _repo = compile_on_mini(self,
                                                   seven_table_all_pass())
        md = pfs.render_seal_determination(doc)
        self.assertTrue(md.startswith(
            "== 项目总封版判定材料(P3 终验·如实汇编) ==\n"))
        self.assertIn("观察钟 elapsed: 3/30 天(as_of 时点)", md)
        self.assertIn("PENDING_SUPPLEMENTARY_EVIDENCE", md)
        self.assertIn("overall_digest=" + GOLDEN_MINI_OVERALL, md)
        self.assertIn("无 FAIL 项", md)
        self.assertIn("-- 免责 --\n"
                      "本判定材料为项目工程收尾状态如实汇编,不构成投资建议"
                      "(禁交易/禁仓位/禁收益承诺);FAIL/NOT_VERIFIED 项如实"
                      "留档,不美化\n", md)
        self.assertTrue(md.endswith("不美化\n"))

    def test_fail_render_fail_section(self):
        doc, _state, _out, _repo = compile_on_mini(self,
                                                   seven_table_ac03_fail())
        md = pfs.render_seal_determination(doc)
        self.assertIn("[FAIL] FA-S1-AC-03", md)
        self.assertIn("NOT_SEALED", md)
        self.assertNotIn("无 FAIL 项", md)

    def test_s4_registration_lines_rendered(self):
        doc, _state, _out, _repo = compile_on_mini(self,
                                                   seven_table_all_pass())
        md = pfs.render_seal_determination(doc)
        self.assertIn("FA-S4-01 | NOT_VERIFIED | 登记面 only(零预执行)", md)
        self.assertIn("FA-S4-02 | NOT_VERIFIED | 登记面 only(零预执行); "
                      "观察窗 elapsed=3/30 天(起算 2026-11-05→终点 2026-12-05)",
                      md)
        self.assertIn("FA-S4-03 | PASS | 载体=R018_parked_artifact", md)


class TestRegisteredValues(unittest.TestCase):
    """DP/参数登记锚定(REPORT §零.4/§零.5 逐值;回改→selfcheck 红)。"""

    def test_registered_dp_values_dp10(self):
        dp = pfs.registered_dp_values()["DP-10"]
        self.assertEqual(dp["observation_start"], "2026-11-05")
        self.assertEqual(dp["observation_window_days"], 30)
        self.assertEqual(dp["observation_end"], "2026-12-05")
        self.assertEqual(dp["carrier"], "R018_parked_artifact")
        self.assertEqual(dp["zero_preexecution"], True)
        self.assertIn("user_approved_2026-11-08_now_dispatch_F",
                      dp["user_approval"])

    def test_registered_dp_values_upstream_zero_consumption(self):
        dp = pfs.registered_dp_values()
        self.assertIn("零消费零改写", dp["DP-1/DP-2/DP-3"])
        self.assertIn("零消费零改写", dp["DP-5/DP-6"])
        self.assertIn("零消费零改写", dp["DP-7"])
        self.assertIn("零触及", dp["DP-4/DP-8/DP-9"])

    def test_registered_param_values_counts(self):
        params = pfs.registered_param_values()
        self.assertEqual(params["checklist_item_count"], 24)
        self.assertEqual(params["section_counts"],
                         {"S1": 7, "S2": 11, "S3": 1, "S4": 3, "S5": 1,
                          "S6": 1})
        self.assertEqual(params["layer_registry_count"], 11)
        self.assertEqual(params["archive_layer_count"], 10)
        self.assertEqual(params["archive_total_files"], 154)
        self.assertEqual(params["self_excluded_count"], 4)
        self.assertEqual(params["journal_record_types"],
                         ["baseline", "started", "compiled"])
        self.assertEqual(params["supplementary_round_after"], "2026-12-05")

    def test_dp_selfcheck_ok(self):
        self.assertTrue(pfs.dp_selfcheck().startswith("dp_selfcheck OK"))

    def test_dp_selfcheck_detects_dp10_tamper(self):
        with mock.patch.object(pfs, "DP10_OBSERVATION_WINDOW_DAYS", 29):
            with self.assertRaises(AssertionError):
                pfs.dp_selfcheck()

    def test_dp_selfcheck_detects_threshold_tamper(self):
        with mock.patch.object(pfs, "RT_MIN_TASK_SUCCESS_RATE_PCT", 90):
            with self.assertRaises(AssertionError):
                pfs.dp_selfcheck()

    def test_self_excluded_paths(self):
        self.assertEqual(sorted(pfs.SELF_EXCLUDED_PATHS), sorted([
            "scripts/project_final_seal.py", "tests/test_p3_wp_f.py",
            "docs/P3_WP_F_REPORT.md", "docs/P3_WP_F_DELIVERY.md"]))


class TestRegisteredIndex(unittest.TestCase):
    """154 件冻结登记索引(计数/唯一性/F 自豁免/样例锚)。"""

    def test_layer_counts(self):
        counts = {layer: len(files)
                  for layer, files in pfs.ARCHIVE_INDEX.items()}
        self.assertEqual(counts, {
            "L0-gov": 21, "L1-p02": 45, "L1w3-dataw3": 2, "L2a-e2ea": 2,
            "L2fa-p03fa": 2, "L2b-e2eb": 13, "L3-glm": 12, "L4-p1": 23,
            "L5-p2": 11, "L6-p3": 23})
        self.assertEqual(sum(counts.values()), 154)

    def test_paths_unique_and_self_excluded(self):
        all_paths = [p for files in pfs.ARCHIVE_INDEX.values() for p in files]
        self.assertEqual(len(all_paths), len(set(all_paths)))
        self.assertEqual(set(all_paths) & set(pfs.SELF_EXCLUDED_PATHS),
                         set())

    def test_sample_anchors(self):
        self.assertIn("docs/P3_DESIGN.md", pfs.ARCHIVE_INDEX["L6-p3"])
        self.assertIn("scripts/report_quality_review.py",
                      pfs.ARCHIVE_INDEX["L6-p3"])
        self.assertIn("tests/test_p3_wp_e.py", pfs.ARCHIVE_INDEX["L6-p3"])
        self.assertIn("docs/P0_2_W5_SEALING.md", pfs.ARCHIVE_INDEX["L1-p02"])
        self.assertIn("docs/P03_FINAL_ACCEPTANCE_REPORT.md",
                      pfs.ARCHIVE_INDEX["L2fa-p03fa"])

    def test_layer_registry_shape(self):
        ids = [row["layer_id"] for row in pfs.LAYER_REGISTRY]
        self.assertEqual(ids[-1], "L6-p3f")
        self.assertEqual(len(ids), 11)
        mapped = {row["archive_layer"] for row in pfs.LAYER_REGISTRY
                  if row["archive_layer"] is not None}
        self.assertEqual(mapped, set(pfs.ARCHIVE_INDEX))


def _docstring_constant_nodes(tree):
    """模块/函数/类 docstring 常量节点 id 集(纪律词面豁免;剥 docstring 扫描)。"""
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)):
            body = node.body
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                found.add(id(body[0].value))
    return found


class TestAstPurity(unittest.TestCase):
    """AST 纯度: import 封闭集+open 恰 3 helper+零禁调用+零连续 LIVE 字面量。"""

    def setUp(self):
        with open(MODULE_PATH, "r", encoding="utf-8") as fh:
            self.source = fh.read()
        self.tree = ast.parse(self.source)
        self.docstrings = _docstring_constant_nodes(self.tree)

    def test_import_closed_set(self):
        imports = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                imports.add((node.module or "").split(".")[0])
        self.assertEqual(imports, {"json", "os", "sys", "hashlib"})

    def test_no_forbidden_calls(self):
        forbidden = {"popen", "system", "walk", "listdir", "scandir",
                     "remove", "unlink", "rmtree", "eval", "exec",
                     "insert", "__import__"}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = (func.id if isinstance(func, ast.Name)
                        else func.attr if isinstance(func, ast.Attribute)
                        else "")
                self.assertNotIn(name, forbidden,
                                 "禁调用面命中: %s@L%d" % (name,
                                                           node.lineno))

    def test_no_network_literals(self):
        for node in ast.walk(self.tree):
            if (isinstance(node, ast.Constant)
                    and isinstance(node.value, str)
                    and id(node) not in self.docstrings):
                for token in ("http://", "https://", "ws://", "ftp://"):
                    self.assertNotIn(token, node.value)

    def test_open_exactly_three_helpers(self):
        opens = [node for node in ast.walk(self.tree)
                 if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name)
                 and node.func.id == "open"]
        modes = []
        for node in opens:
            self.assertTrue(len(node.args) >= 2)
            mode = node.args[1]
            self.assertIsInstance(mode, ast.Constant)
            modes.append(mode.value)
        self.assertEqual(sorted(modes), ["a", "rb", "w"])

    def test_no_contiguous_live_or_daily_literal(self):
        for node in ast.walk(self.tree):
            if (isinstance(node, ast.Constant)
                    and isinstance(node.value, str)
                    and id(node) not in self.docstrings):
                s = node.value
                self.assertFalse(
                    "每周宏观追踪" in s and "investment-agent" in s,
                    "源码含连续 LIVE 路径字面量: %r" % (s,))
                self.assertFalse("data/daily" in s,
                                  "源码含连续 data/daily 字面量: %r" % (s,))

    def test_module_compiles(self):
        compile(self.source, MODULE_PATH, "exec")


class TestZeroActiveCollection(unittest.TestCase):
    """零主动采集: 零监视令牌+零扫描调用(在场性=纯 isfile 核验)。"""

    def test_no_watch_tokens(self):
        with open(MODULE_PATH, "r", encoding="utf-8") as fh:
            source = fh.read()
        for token in ("watchdog", "inotify", "fsevent", "while True"):
            self.assertNotIn(token, source)

    def test_presence_check_is_isfile_only(self):
        with open(MODULE_PATH, "r", encoding="utf-8") as fh:
            source = fh.read()
        self.assertIn("os.path.isfile", source)


class TestRealRepoSample(unittest.TestCase):
    """真实仓稳定样例在场(实跑面归 step 10;此处仅稳定锚抽检)。"""

    def test_stable_anchors_present(self):
        anchors = [
            "docs/P3_DESIGN.md", "docs/P3_INVENTORY.md",
            "docs/P3_DELIVERY.md",
            ".github/workflows/offline-tests.yml",
            "docs/P3_WP_A_REPORT.md", "docs/P3_WP_A_DELIVERY.md",
            "docs/P3_WP_B_REPORT.md", "docs/P3_WP_B_DELIVERY.md",
            "docs/P3_WP_C_REPORT.md", "docs/P3_WP_C_DELIVERY.md",
            "docs/P3_WP_D_REPORT.md", "docs/P3_WP_D_DELIVERY.md",
            "docs/P3_WP_E_REPORT.md", "docs/P3_WP_E_DELIVERY.md",
            "scripts/research_index.py", "scripts/evidence_linkage.py",
            "scripts/prediction_review.py", "scripts/report_quality_review.py",
            "scripts/personal_flow_integration.py",
            "tests/test_p3_wp_a.py", "tests/test_p3_wp_b.py",
            "tests/test_p3_wp_c.py", "tests/test_p3_wp_d.py",
            "tests/test_p3_wp_e.py",
            "scripts/project_final_seal.py",
            "tests/test_p3_wp_f.py",
            "docs/P3_WP_F_REPORT.md",
        ]
        for rel in anchors:
            self.assertTrue(os.path.isfile(os.path.join(REPO_ROOT, rel)),
                            "稳定锚缺席: %s" % (rel,))

    def test_module_matches_registered_index_semantics(self):
        """默认索引层集与迷你索引层集同名(compile 自定义索引面可用)。"""
        self.assertEqual(set(pfs.ARCHIVE_INDEX), set(MINI_INDEX))


class TestCLI(unittest.TestCase):
    """__main__ 入口(subprocess 受控;selfcheck 零写+run 面+守卫)。"""

    def run_cli(self, args, cwd):
        return subprocess.run([sys.executable, MODULE_PATH] + args,
                              cwd=cwd, capture_output=True, text=True,
                              timeout=120)

    def test_selfcheck_exit0_sentinel_zero_write(self):
        tmp = tempfile.mkdtemp(prefix="p3wpf-cli-")
        self.addCleanup(shutil.rmtree, tmp, True)
        proc = self.run_cli(["selfcheck"], tmp)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("dp_selfcheck OK", proc.stdout)
        self.assertIn("user_approved_2026-11-08_now_dispatch_F", proc.stdout)
        self.assertEqual(os.listdir(tmp), [])

    def test_bad_subcommand_exit2(self):
        proc = self.run_cli(["amend-list"], tempfile.gettempdir())
        self.assertEqual(proc.returncode, 2)
        self.assertIn("用法", proc.stderr)

    def test_run_missing_args_exit2(self):
        proc = self.run_cli(["run"], tempfile.gettempdir())
        self.assertEqual(proc.returncode, 2)

    def test_run_on_mini_default_index_honest_not_sealed(self):
        tmp = tempfile.mkdtemp(prefix="p3wpf-run-")
        self.addCleanup(shutil.rmtree, tmp, True)
        repo = os.path.join(tmp, "mini")
        build_mini_repo(repo)
        table_path = os.path.join(tmp, "seven_ac.json")
        with open(table_path, "w", encoding="utf-8") as fh:
            json.dump(seven_table_all_pass(), fh, ensure_ascii=False)
        state = os.path.join(tmp, "journal.jsonl")
        out = os.path.join(tmp, "out")
        proc = self.run_cli(["run", "--repo-root", repo, "--as-of", AS_OF,
                             "--seven-ac-file", table_path,
                             "--state-path", state, "--out-dir", out],
                            tmp)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("判定=NOT_SEALED", proc.stdout)
        self.assertIn("elapsed=3/30 天", proc.stdout)
        self.assertIn("FAIL 项=11", proc.stdout)
        self.assertIn("NOT_VERIFIED 项=3", proc.stdout)
        with open(state, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        self.assertEqual(len(lines), 3)
        records = [json.loads(line) for line in lines]
        self.assertEqual([r["record_type"] for r in records],
                         ["baseline", "started", "compiled"])
        self.assertEqual(records[0]["fa_digest"], GOLDEN_FA_DIGEST)
        self.assertEqual(records[2]["determination"], "NOT_SEALED")
        self.assertTrue(os.path.isfile(os.path.join(
            out, "seal_determination.json")))
        self.assertTrue(os.path.isfile(os.path.join(
            out, "seal_determination.md")))

    def test_run_rerun_rejected_exit1(self):
        tmp = tempfile.mkdtemp(prefix="p3wpf-rerun-")
        self.addCleanup(shutil.rmtree, tmp, True)
        repo = os.path.join(tmp, "mini")
        build_mini_repo(repo)
        table_path = os.path.join(tmp, "seven_ac.json")
        with open(table_path, "w", encoding="utf-8") as fh:
            json.dump(seven_table_all_pass(), fh, ensure_ascii=False)
        state = os.path.join(tmp, "journal.jsonl")
        out = os.path.join(tmp, "out")
        args = ["run", "--repo-root", repo, "--as-of", AS_OF,
                "--seven-ac-file", table_path, "--state-path", state,
                "--out-dir", out]
        first = self.run_cli(args, tmp)
        self.assertEqual(first.returncode, 0, first.stderr)
        second = self.run_cli(args, tmp)
        self.assertEqual(second.returncode, 1)
        self.assertIn("baseline 已登记", second.stderr)
        with open(state, "r", encoding="utf-8") as fh:
            self.assertEqual(len(fh.read().splitlines()), 3)

    def test_run_state_path_guard_exit1(self):
        tmp = tempfile.mkdtemp(prefix="p3wpf-guard-")
        self.addCleanup(shutil.rmtree, tmp, True)
        repo = os.path.join(tmp, "mini")
        build_mini_repo(repo)
        table_path = os.path.join(tmp, "seven_ac.json")
        with open(table_path, "w", encoding="utf-8") as fh:
            json.dump(seven_table_all_pass(), fh, ensure_ascii=False)
        proc = self.run_cli(["run", "--repo-root", repo, "--as-of", AS_OF,
                             "--seven-ac-file", table_path,
                             "--state-path",
                             os.path.join(tmp, "data", "daily",
                                          "journal.jsonl")], tmp)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("data/daily", proc.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
