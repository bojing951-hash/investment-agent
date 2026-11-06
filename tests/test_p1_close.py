#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P1-WP-CLOSE(#21 / WP-P1-CLOSE)验收件: 谱系核对脚本 tests/test_p1_close.py。

被测对象: scripts/p1_acceptance_check.py(LINEAGE-TABLE 逐行 git 列机器复演+
开工核验项+引擎列透传;纯只读)。

数据纪律(R014-D3/R022 承接): **临时目录合成 git 仓库 fixture=唯一数据源**——
git init+合成提交/分支/tag(固定身份+固定日期),零真实档依赖、零 origin 依赖、
零网络;与真实谱系核对运行步(合同 §二,脚本于真实 BASE-P1CLOSE 谱系运行)严格
分离(TestRealTableAgainstFixtureMustFail 反向证明: 真实冻结表在 fixture 上必红,
两域零互染)。预期值=字面量硬编码(不从被测模块导入计算,禁自证恒真;被测模块
仅作数据读取对象用于透传保真断言)。零新增第三方依赖(纯标准库+git CLI)。

fixture→预期值映射(逐断言组可追溯到 fixture 定义处,DELIVERY 漂移维护专节同源):
- _commit()/_merge() 固定身份+日期构造器(L78-L118) → 全部 SHA 输入面;
- _green_table()(L121-L152) → 全绿断言组(rows=3 checked=3 row_pass=3);
- _scenario() 变异表(L155-L166) → 各失败态断言组(FAIL 行文案+非零退出码);
- 硬编码伪值字面量 DRIFT_TIP/FORBIDDEN_MERGE/WRONG_BLOB(L60-L64) → 漂移/
  禁锚/blob 失配断言组。
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(REPO_ROOT, "scripts", "p1_acceptance_check.py")

# ---- 硬编码伪值字面量(预期输入,非被测模块生成) ------------------------------
DRIFT_TIP = "0000000000000000000000000000000000000000"
FORBIDDEN_MERGE = "c9626633" + "0" * 32  # 禁锚前缀开头的 40 位伪 SHA
WRONG_BLOB = "ffffffffffffffffffffffffffffffffffffffff"
MISSING_BRANCH = "dev/nonexistent-fixture-branch"
FIXTURE_CI_LITERAL = "99999999999 success 70槽=69exit0+1SKIP"
FIXTURE_AUDIT_LITERAL = "PASS"
ENGINE_NOTE_LITERAL = "来源: 冻结章登记,引擎侧登记,执行席不可达,审计复演"

# ---- 冻结章定值字面量(透传保真断言的对照源=硬编码,非从被测模块导入) -----------
FROZEN_BASE = "5e6ddcd3691a3d52a41472ef63793cb317e1d508"
FROZEN_LINEAGE = [
    ("WP-P1-A", "R044", "#14", "f6d0beb7cdba8631c9df6a20a2e9a5e6140c1c20",
     "dev/p1-impl-a", "8ec3737daedcb7f3abd77de6ee228fc4250ec6f0",
     "42063709324 success 70槽=69exit0+1SKIP", "PASS"),
    ("WP-P1-B", "R045", "#15", "fcd0537c9ac4b66dcd8a52c6186e814121feaf5f",
     "dev/p1-impl-b", "4575a768e8c942a5c8536ee7b5254bf8c88496bd",
     "42082218620 success 71槽=70exit0+1SKIP", "PASS"),
    ("WP-P1-C", "R046", "#16", "c11c998d7c6265a9dbc9ef67bcae5757ec57df9d",
     "dev/p1-impl-c", "ee053a65f3a29e2b154bf841aaf4b1f685a01bd2",
     "42094508669 success 72槽=71exit0+1SKIP", "PASS"),
    ("WP-P1-D", "R047", "#17", "82d41e214b99f09bf4521c137261f61f17a3e5ff",
     "dev/p1-impl-d", "281f9f6c7963bd4e95a63f33049f2541a337255d",
     "42101669112 success 73槽=72exit0+1SKIP", "PASS"),
    ("WP-P1-E", "R048", "#18", "64ce40c25409bdb0a3d9fecc4c5f0f5df74dd902",
     "dev/p1-impl-e", "6e2765fc0f2fe72012bb7270f094b020117396e3",
     "42211060088 success 75槽=74exit0+1SKIP", "PASS"),
    ("GAP-P1-08(参照·不计分)", "R061", "—", "ee66f3a92f7854c9db308bc604e7707ed49e3bee",
     "dev/p1-gap08", "9369a155b504657c804590be9ed53baeb9b0af6f",
     "42129438722 success 74槽=73exit0+1SKIP", "PASS"),
    ("WP-P1-F", "R062", "#19", "8b157fd3c0c0b8a42407e49c84cbcc1254aa8a75",
     "dev/p1-impl-f", "44a7a686f97ad9238b4db16c1cccfe76b09e47f9",
     "42267019257 success 76槽=75exit0+1SKIP", "PASS"),
    ("WP-P1-G", "R065", "#20", "5e6ddcd3691a3d52a41472ef63793cb317e1d508",
     "dev/p1-impl-g", "45538ab371b2d25c3fb56b9ca88a20f80aeae4b8",
     "42280763695 success 77槽=76exit0+1SKIP", "PASS"),
]

GIT_ENV = {
    "GIT_AUTHOR_NAME": "Fixture Bot",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "Fixture Bot",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
    "GIT_AUTHOR_DATE": "2098-01-01T00:00:00+00:00",
    "GIT_COMMITTER_DATE": "2098-01-01T00:00:00+00:00",
    "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
    "HOME": os.environ.get("HOME", "/tmp"),
}


def _git(repo, *args):
    proc = subprocess.run(
        ["git", "-C", repo] + list(args),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=GIT_ENV,
    )
    if proc.returncode != 0:
        raise AssertionError("fixture git 失败: %s\n%s" % (args, proc.stderr))
    return proc.stdout.strip()


def _write(repo, rel, content):
    path = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def _commit(repo, msg):
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", msg)


def _merge(repo, branch, msg):
    _git(repo, "merge", "--no-ff", "-q", "-m", msg, branch)


def build_fixture(root):
    """合成 git 仓库谱系(零真实档/零 origin;固定身份+日期→可复现)。

    谱系形态: c0(tag p03fx+三 docs 文件)→c1→[branch dev/fx-a: a1]→m1(merge)
    →c2→[branch dev/fx-b: b1]→m2(merge)→c3=HEAD(main);
    侧支 dev/fx-side: 自 c1 分出 s1(未并入,tag side-tag 锚 s1);
    tag unreachable-tag=side-tag。
    """
    repo = os.path.join(root, "fx-repo")
    os.makedirs(repo)
    _git(repo, "init", "-q", "-b", "main")
    _write(repo, "docs/f1.md", "fixture design one\n")
    _write(repo, "docs/f2.md", "fixture design two\n")
    _write(repo, "docs/f3.md", "fixture design three\n")
    _commit(repo, "c0 base")
    c0 = _git(repo, "rev-parse", "HEAD")
    _git(repo, "tag", "p03fx")
    _write(repo, "step.txt", "c1\n")
    _commit(repo, "c1")
    c1 = _git(repo, "rev-parse", "HEAD")
    _git(repo, "branch", "dev/fx-side", c1)
    _git(repo, "checkout", "-q", "dev/fx-side")
    _write(repo, "side.txt", "side s1\n")
    _commit(repo, "s1 side")
    s1 = _git(repo, "rev-parse", "HEAD")
    _git(repo, "tag", "side-tag-20981231")
    _git(repo, "checkout", "-q", "main")
    _git(repo, "branch", "dev/fx-a", c1)
    _git(repo, "checkout", "-q", "dev/fx-a")
    _write(repo, "a.txt", "a1\n")
    _commit(repo, "a1")
    a1 = _git(repo, "rev-parse", "HEAD")
    _git(repo, "checkout", "-q", "main")
    _merge(repo, "dev/fx-a", "m1 merge fx-a")
    m1 = _git(repo, "rev-parse", "HEAD")
    _write(repo, "step.txt", "c2\n")
    _commit(repo, "c2")
    c2 = _git(repo, "rev-parse", "HEAD")
    _git(repo, "branch", "dev/fx-b", c2)
    _git(repo, "checkout", "-q", "dev/fx-b")
    _write(repo, "b.txt", "b1\n")
    _commit(repo, "b1")
    b1 = _git(repo, "rev-parse", "HEAD")
    _git(repo, "checkout", "-q", "main")
    _merge(repo, "dev/fx-b", "m2 merge fx-b")
    m2 = _git(repo, "rev-parse", "HEAD")
    _write(repo, "step.txt", "c3\n")
    _commit(repo, "c3")
    c3 = _git(repo, "rev-parse", "HEAD")
    blobs = {p: _git(repo, "rev-parse", "HEAD:" + p)
             for p in ("docs/f1.md", "docs/f2.md", "docs/f3.md")}
    return {
        "repo": repo, "c0": c0, "c1": c1, "c2": c2, "c3": c3,
        "m1": m1, "m2": m2, "a1": a1, "b1": b1, "s1": s1, "blobs": blobs,
    }


def _green_table(fx):
    """全绿核对表(输入=fixture 实取 SHA;预期结论=硬编码字面量)。"""
    return {
        "base": None,
        "presence": {
            "design_tip": fx["m1"],
            "pkg19_tip": fx["m2"],
            "pkg20_tip": fx["c3"],
            "tag": "p03fx",
            "blobs": dict(fx["blobs"]),
            "forbidden_prefix": "c9626633",
        },
        "lineage": [
            {"pkg": "FX-A", "round": "RX01", "score": "#x1",
             "merge_sha": fx["m1"], "branch": "dev/fx-a", "tip_sha": fx["a1"],
             "ci": FIXTURE_CI_LITERAL, "audit": FIXTURE_AUDIT_LITERAL},
            {"pkg": "FX-B", "round": "RX02", "score": "#x2",
             "merge_sha": fx["m2"], "branch": "dev/fx-b", "tip_sha": fx["b1"],
             "ci": FIXTURE_CI_LITERAL, "audit": FIXTURE_AUDIT_LITERAL},
            {"pkg": "GAP-FX(参照·不计分)", "round": "RX03", "score": "—",
             "merge_sha": fx["c3"], "branch": "main", "tip_sha": fx["c3"],
             "ci": FIXTURE_CI_LITERAL, "audit": FIXTURE_AUDIT_LITERAL},
        ],
    }


def _scenario(fx, mutate):
    """变异表工厂: 深拷贝全绿表后应用单一变异(每用例恰一缺陷面)。"""
    import copy
    table = copy.deepcopy(_green_table(fx))
    mutate(table)
    return table


def run_script(repo, table_path=None, extra=None):
    cmd = [sys.executable, SCRIPT_PATH, "--repo", repo, "--tip-source", "local"]
    if table_path:
        cmd += ["--table", table_path]
    if extra:
        cmd += extra
    proc = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc.returncode, proc.stdout, proc.stderr


class FixtureTestBase(unittest.TestCase):
    """每个用例独立临时目录+独立 fixture(零共享状态)。"""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="p1_close_fx_")
        self.fx = build_fixture(self.root)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def write_table(self, table):
        path = os.path.join(self.root, "table.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(table, fh, ensure_ascii=False)
        return path


class TestFrozenTableFidelity(unittest.TestCase):
    """冻结章定值透传保真(DP-C1): 脚本内嵌表==硬编码字面量(双向对照)。"""

    def test_embedded_lineage_table_equals_frozen_literals(self):
        spec = importlib.util.spec_from_file_location(
            "p1_acceptance_check", SCRIPT_PATH)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual([tuple(r) for r in mod.LINEAGE_TABLE], FROZEN_LINEAGE)
        self.assertEqual(mod.BASE_P1CLOSE, FROZEN_BASE)
        self.assertEqual(len(mod.LINEAGE_TABLE), 8)
        self.assertEqual(mod.ENGINE_SOURCE_NOTE, ENGINE_NOTE_LITERAL)


class TestFixtureAllGreen(FixtureTestBase):
    """ancestor 通过态+tip 一致态+引擎列透传+全绿退出码 0。"""

    def test_all_green_exit0_and_summary_literals(self):
        path = self.write_table(_green_table(self.fx))
        rc, out, err = run_script(self.fx["repo"], path)
        self.assertEqual(rc, 0, "全绿 fixture 退出码应为 0;stderr=%s" % err)
        self.assertIn("RESULT: ALL GREEN(rows=3, fail=0)", out)
        self.assertIn("rows=3 checked=3 row_pass=3", out)
        self.assertNotIn("FAIL:", out)
        # 在场核验七项: ①SKIPPED+②③④OK+⑤×3+⑥OK+⑦OK
        self.assertIn("[PRESENCE] ① origin/main 尖端核对: SKIPPED"
                      "(local fixture 模式无 origin)", out)
        self.assertIn("② 祖先", out)
        self.assertIn("③ 祖先", out)
        self.assertIn("④ 祖先", out)
        self.assertIn("⑥ tag p03fx ∈ HEAD 谱系: OK", out)
        self.assertIn("⑦ 禁锚前缀 c9626633 于锚定值集合零出现: OK", out)

    def test_engine_columns_transmitted_verbatim_with_note(self):
        path = self.write_table(_green_table(self.fx))
        rc, out, _ = run_script(self.fx["repo"], path)
        self.assertEqual(out.count(FIXTURE_CI_LITERAL), 3)
        self.assertEqual(out.count(ENGINE_NOTE_LITERAL), 3)
        self.assertIn("audit=PASS", out)


class TestAncestorFailState(FixtureTestBase):
    """ancestor 失败态: 未并入侧支提交作 merge SHA→FAIL 行+非零退出。"""

    def test_unmerged_side_commit_ancestor_fails(self):
        def mutate(table):
            table["lineage"][1]["merge_sha"] = self.fx["s1"]
        rc, out, _ = run_script(
            self.fx["repo"], self.write_table(_scenario(self.fx, mutate)))
        self.assertNotEqual(rc, 0)
        self.assertIn("RESULT: FAIL(rows=3, row_fail=1", out)
        self.assertIn("ancestor∈HEAD 失败", out)
        self.assertIn("(c) 行自检: FAIL", out)
        self.assertIn("rows=3 checked=3 row_pass=2", out)

    def test_nonexistent_merge_sha_fails(self):
        bogus = "1234567890123456789012345678901234567890"
        def mutate(table):
            table["lineage"][0]["merge_sha"] = bogus
        rc, out, _ = run_script(
            self.fx["repo"], self.write_table(_scenario(self.fx, mutate)))
        self.assertNotEqual(rc, 0)
        self.assertIn(bogus, out)
        self.assertIn("ancestor∈HEAD 失败", out)


class TestTipStates(FixtureTestBase):
    """tip 一致态(全绿已证)与漂移/分支缺席态。"""

    def test_tip_drift_hardcoded_zero_sha_fails(self):
        def mutate(table):
            table["lineage"][0]["tip_sha"] = DRIFT_TIP
        rc, out, _ = run_script(
            self.fx["repo"], self.write_table(_scenario(self.fx, mutate)))
        self.assertNotEqual(rc, 0)
        self.assertIn("tip(本地 refs 只读)失配", out)
        self.assertIn(DRIFT_TIP, out)
        self.assertIn("RESULT: FAIL", out)

    def test_missing_branch_tip_fails(self):
        def mutate(table):
            table["lineage"][2]["branch"] = MISSING_BRANCH
        rc, out, _ = run_script(
            self.fx["repo"], self.write_table(_scenario(self.fx, mutate)))
        self.assertNotEqual(rc, 0)
        self.assertIn("分支 %s tip" % MISSING_BRANCH, out)
        self.assertIn("<缺席>", out)


class TestPresenceFailStates(FixtureTestBase):
    """在场核验失败态: 祖先②/tag⑥/blob⑤/禁锚⑦。"""

    def test_presence_design_tip_unreachable_fails(self):
        def mutate(table):
            table["presence"]["design_tip"] = self.fx["s1"]
        rc, out, _ = run_script(
            self.fx["repo"], self.write_table(_scenario(self.fx, mutate)))
        self.assertNotEqual(rc, 0)
        self.assertIn("② 祖先", out)
        self.assertIn("失败", out)

    def test_presence_tag_on_side_commit_fails(self):
        def mutate(table):
            table["presence"]["tag"] = "side-tag-20981231"
        rc, out, _ = run_script(
            self.fx["repo"], self.write_table(_scenario(self.fx, mutate)))
        self.assertNotEqual(rc, 0)
        self.assertIn("⑥ tag side-tag-20981231 ∈ HEAD 谱系失败", out)

    def test_presence_blob_mismatch_fails(self):
        def mutate(table):
            table["presence"]["blobs"]["docs/f1.md"] = WRONG_BLOB
        rc, out, _ = run_script(
            self.fx["repo"], self.write_table(_scenario(self.fx, mutate)))
        self.assertNotEqual(rc, 0)
        self.assertIn("⑤ blob docs/f1.md: 实取=", out)
        self.assertIn(WRONG_BLOB, out)

    def test_forbidden_anchor_prefix_in_anchor_set_fails(self):
        def mutate(table):
            table["lineage"][0]["merge_sha"] = FORBIDDEN_MERGE
        rc, out, _ = run_script(
            self.fx["repo"], self.write_table(_scenario(self.fx, mutate)))
        self.assertNotEqual(rc, 0)
        self.assertIn("⑦ 禁锚前缀 c9626633 于锚定值集合出现", out)
        # 同一行 ancestor 亦必失败(伪 SHA 非对象)
        self.assertIn("ancestor∈HEAD 失败", out)


class TestRealFixtureSeparation(FixtureTestBase):
    """真实冻结表×fixture 域分离: 真实锚定值在合成仓库上必须全红(零互染)。"""

    def test_real_table_against_fixture_must_fail(self):
        rc, out, _ = run_script(self.fx["repo"])  # 无 --table=冻结章定值
        self.assertNotEqual(rc, 0)
        self.assertIn("RESULT: FAIL", out)
        self.assertIn(FROZEN_BASE[:16], out)  # ① skipped(local),但 base 不查
        self.assertIn("ancestor∈HEAD 失败", out)


class TestUsageErrors(unittest.TestCase):
    """用法错误态: 非法 tip-source=argparse exit 2;坏核对表=exit 2。"""

    def test_invalid_tip_source_exits_2(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT_PATH, "--tip-source", "bogus"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(proc.returncode, 2)

    def test_missing_table_file_exits_2(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT_PATH, "--repo", "/tmp",
             "--tip-source", "local", "--table", "/tmp/no-such-table.json"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("FAIL: 核对表加载失败", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
