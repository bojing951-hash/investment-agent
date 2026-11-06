#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P1-WP-CLOSE(#21 / WP-P1-CLOSE)P1 全链谱系验收核对脚本。

对冻结章 LINEAGE-TABLE(DP-C1 定值,八行=七计分行+R061 参照行)逐行做 git 列
机器复演: (a) merge SHA ∈ HEAD 祖先(merge-base --is-ancestor 复演)+(a2) 实现分
支 tip=登记值对照(ls-remote 实取[缺省] 或本地 refs 只读[fixture 模式]);
开工核验项(合同 §零②~⑦: 祖先×3+tag p03-final-20261105 可达+设计三件 blob
对照+禁锚前缀零锚定)一并输出。(b) 引擎列(主 CI run+conclusion+套件数/审计
VERDICT)执行席不可达=冻结章透传打印+来源标注,不查询不替换不伪造。

纯只读纪律: 仅调用 git 取证类子命令(rev-parse/merge-base/ls-remote),零 push
零写入零应用层网络(ls-remote=既定惯例例外);任一 git 列核验失败→输出 FAIL 行
+非零退出码(禁删 FAIL 行/放宽判据凑绿)。

用法:
  python3 scripts/p1_acceptance_check.py                 # 真实仓库+ls-remote 模式
  python3 scripts/p1_acceptance_check.py --repo R --tip-source local --table T.json
                                                         # 合成 fixture 模式(测试)
"""
import argparse
import datetime
import json
import subprocess
import sys

# ---------------------------------------------------------------------------
# 冻结章定值透传(DP-C1;来源=合同 IA-P1-WP-CLOSE-AC-v1.0 冻结章,禁改写禁补值)
# ---------------------------------------------------------------------------
BASE_P1CLOSE = "5e6ddcd3691a3d52a41472ef63793cb317e1d508"
DESIGN_COMP_TIP = "7190eb7aae110dcc23cf059b4969cd9978429d4d"  # §零② 设计在场
R062_FINAL_TIP = "44a7a686f97ad9238b4db16c1cccfe76b09e47f9"   # §零③ #19 并入证明
R065_FINAL_TIP = "45538ab371b2d25c3fb56b9ca88a20f80aeae4b8"   # §零④ #20 并入证明
P03_FINAL_TAG = "p03-final-20261105"                          # §零⑥ 第一层封印在场
FORBIDDEN_ANCHOR_PREFIX = "c9626633"                          # §零⑦ 禁锚(整改前旧尖端前缀)
DESIGN_BLOBS = {                                              # §零⑤ 设计三件 blob 期望值
    "docs/P1_DATA_NEEDS_INVENTORY.md": "df79c06f66c368d93159b7a3b46852b6fcb9b196",
    "docs/P1_DELIVERY.md": "314c2644a51f2f575a90253580cb56346e2f93b6",
    "docs/P1_DESIGN.md": "10e026c08ce2828908ff7a5421aee8aba1f4e6d0",
}
ENGINE_SOURCE_NOTE = "来源: 冻结章登记,引擎侧登记,执行席不可达,审计复演"

# LINEAGE-TABLE(冻结章定值表逐字透传;字段=(包名,轮次,计分,merge_sha[git列],
# branch,branch_tip[git列],ci[引擎列],audit[引擎列]))
LINEAGE_TABLE = [
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


def default_config():
    """真实运行缺省配置=冻结章定值透传(不与任何运行态数据混合)。"""
    return {
        "base": BASE_P1CLOSE,
        "presence": {
            "design_tip": DESIGN_COMP_TIP,
            "pkg19_tip": R062_FINAL_TIP,
            "pkg20_tip": R065_FINAL_TIP,
            "tag": P03_FINAL_TAG,
            "blobs": dict(DESIGN_BLOBS),
            "forbidden_prefix": FORBIDDEN_ANCHOR_PREFIX,
        },
        "lineage": [
            {"pkg": r[0], "round": r[1], "score": r[2], "merge_sha": r[3],
             "branch": r[4], "tip_sha": r[5], "ci": r[6], "audit": r[7]}
            for r in LINEAGE_TABLE
        ],
    }


def run_git(repo, args):
    """只读执行 git 取证类子命令,返回 (rc, stdout, stderr)。"""
    proc = subprocess.run(
        ["git", "-C", repo] + list(args),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def shorten(value, limit=16):
    return value if len(value) <= limit else value[:limit] + "…"


class Reporter(object):
    """核对输出器: 即时打印(行序=核验序);FAIL 行统一前缀,便于 grep;统计 pass/fail。"""

    def __init__(self):
        self.pass_count = 0
        self.fail_count = 0

    def ok(self, text):
        self.pass_count += 1
        print(text)

    def fail(self, text):
        self.fail_count += 1
        print("FAIL: " + text)

    def skip(self, text):
        print(text)


def check_ancestor(rep, repo, sha, head="HEAD"):
    rc, out, err = run_git(repo, ["merge-base", "--is-ancestor", sha, head])
    return rc == 0, err


def resolve_tip_ls_remote(repo, branch):
    rc, out, err = run_git(repo, ["ls-remote", "origin", "refs/heads/" + branch])
    if rc != 0 or not out:
        return None, err or "ls-remote 空返回(分支缺席或远端不可达)"
    return out.split()[0], ""


def resolve_tip_local(repo, branch):
    rc, out, err = run_git(repo, ["rev-parse", "refs/heads/" + branch])
    if rc != 0 or not out:
        return None, err or "rev-parse 失败(本地分支缺席)"
    return out, ""


def anchor_sha_set(cfg):
    """本包核验面全部登记锚定值(禁锚前缀检查对象;不含来源注记/引擎列文本)。"""
    vals = [cfg.get("base") or ""]
    presence = cfg["presence"]
    vals += [presence.get("design_tip") or "", presence.get("pkg19_tip") or "",
             presence.get("pkg20_tip") or ""]
    vals += [v for v in (presence.get("blobs") or {}).values()]
    for row in cfg["lineage"]:
        vals += [row.get("merge_sha") or "", row.get("tip_sha") or ""]
    return [v for v in vals if v]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="IA-P1-WP-CLOSE P1 全链谱系验收核对(纯只读)")
    parser.add_argument("--repo", default=None,
                        help="git 仓库路径(缺省=本脚本所在仓库根)")
    parser.add_argument("--tip-source", choices=["ls-remote", "local"],
                        default="ls-remote",
                        help="分支 tip 解析源: ls-remote(真实运行)/local(合成 fixture)")
    parser.add_argument("--table", default=None,
                        help="核对表 JSON 覆盖文件(测试 fixture 用;缺省=冻结章定值)")
    args = parser.parse_args(argv)

    repo = args.repo
    if repo is None:
        import os
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if args.table:
        try:
            with open(args.table, "r", encoding="utf-8") as fh:
                cfg = json.load(fh)
        except (OSError, ValueError) as exc:
            print("FAIL: 核对表加载失败(%s): %s" % (args.table, exc))
            return 2
    else:
        cfg = default_config()

    presence = cfg.get("presence") or {}
    lineage = cfg.get("lineage") or []

    rep = Reporter()
    run_utc = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print("=== IA-P1-WP-CLOSE P1 全链谱系核对(#21 / WP-P1-CLOSE) ===")
    print("repo=%s tip-source=%s table=%s run_utc=%s" % (
        repo, args.tip_source, args.table or "<冻结章定值透传>", run_utc))
    print("--- 开工核验(合同 §零①~⑦) ---")

    # ① origin/main 尖端=BASE(仅 ls-remote 模式;fixture 无 origin,如实 SKIPPED)
    base = cfg.get("base")
    if args.tip_source == "ls-remote" and base:
        rc, out, err = run_git(repo, ["ls-remote", "origin", "refs/heads/main"])
        actual = out.split()[0] if rc == 0 and out else ""
        if actual == base:
            rep.ok("[PRESENCE] ① origin/main 尖端==BASE(%s): OK" % shorten(base))
        else:
            rep.fail("[PRESENCE] ① origin/main 尖端==BASE(%s): 实取=%s %s"
                     % (shorten(base), actual or "<空>", err))
    else:
        rep.skip("[PRESENCE] ① origin/main 尖端核对: SKIPPED(local fixture 模式无 origin)")

    # ②③④ 祖先×3(设计在场/#19 并入/#20 并入)
    for idx, key, label in (
            ("②", "design_tip", "设计在场(design-comp 尖端)"),
            ("③", "pkg19_tip", "#19 并入证明(R062 最终尖端)"),
            ("④", "pkg20_tip", "#20 并入证明(R065 最终尖端)")):
        sha = presence.get(key) or ""
        good, err = check_ancestor(rep, repo, sha)
        if good:
            rep.ok("[PRESENCE] %s 祖先 %s ∈ HEAD(%s): OK" % (idx, shorten(sha), label))
        else:
            rep.fail("[PRESENCE] %s 祖先 %s ∈ HEAD(%s) 失败: %s"
                     % (idx, sha, label, err or "非祖先"))

    # ⑤ 设计三件 blob 对照
    blobs = presence.get("blobs") or {}
    for path in sorted(blobs):
        expected = blobs[path]
        rc, out, err = run_git(repo, ["rev-parse", "HEAD:" + path])
        actual = out if rc == 0 else ""
        if actual == expected:
            rep.ok("[PRESENCE] ⑤ blob %s: OK(%s==登记值)" % (path, shorten(expected)))
        else:
            rep.fail("[PRESENCE] ⑤ blob %s: 实取=%s 登记值=%s %s"
                     % (path, actual or "<缺席>", expected, err))

    # ⑥ tag 可达(第一层终局封印在场)
    tag = presence.get("tag") or ""
    good, err = check_ancestor(rep, repo, tag)
    if good:
        rep.ok("[PRESENCE] ⑥ tag %s ∈ HEAD 谱系: OK" % tag)
    else:
        rep.fail("[PRESENCE] ⑥ tag %s ∈ HEAD 谱系失败: %s" % (tag, err or "非祖先"))

    # ⑦ 禁锚前缀于锚定值集合零出现
    prefix = presence.get("forbidden_prefix") or ""
    if prefix:
        hits = [v for v in anchor_sha_set(cfg) if v.startswith(prefix)]
        if hits:
            rep.fail("[PRESENCE] ⑦ 禁锚前缀 %s 于锚定值集合出现: %s"
                     % (prefix, ",".join(shorten(h) for h in hits)))
        else:
            rep.ok("[PRESENCE] ⑦ 禁锚前缀 %s 于锚定值集合零出现: OK" % prefix)
    else:
        rep.skip("[PRESENCE] ⑦ 禁锚前缀未登记: SKIPPED")

    print("--- LINEAGE-TABLE 逐行核对(%d 行=七计分行+R061 参照行) ---" % len(lineage))
    total = len(lineage)
    row_pass = 0
    for i, row in enumerate(lineage, 1):
        pkg = row.get("pkg", "?")
        rnd = row.get("round", "?")
        score = row.get("score", "?")
        merge_sha = row.get("merge_sha") or ""
        branch = row.get("branch") or ""
        tip_reg = row.get("tip_sha") or ""
        head = "[%%ROW %d/%d] %s %s %s" % (i, total, pkg, rnd, score)
        print(head)
        row_fail_before = rep.fail_count
        # (a) merge SHA ancestor 复演
        good, err = check_ancestor(rep, repo, merge_sha)
        if good:
            rep.ok("  (a-git) merge %s ancestor∈HEAD: OK" % shorten(merge_sha))
        else:
            rep.fail("  (a-git) %s merge %s ancestor∈HEAD 失败: %s"
                     % (head.strip(), merge_sha, err or "非祖先"))
        # (a2) 分支 tip 对照
        if args.tip_source == "ls-remote":
            actual, err = resolve_tip_ls_remote(repo, branch)
            src = "ls-remote 实取"
        else:
            actual, err = resolve_tip_local(repo, branch)
            src = "本地 refs 只读"
        if actual is not None and actual == tip_reg:
            rep.ok("  (a-git) 分支 %s tip(%s): OK(%s==登记值)"
                   % (branch, src, shorten(tip_reg)))
        else:
            rep.fail("  (a-git) %s 分支 %s tip(%s)失配: 实取=%s 登记值=%s %s"
                     % (head.strip(), branch, src, actual or "<缺席>",
                        tip_reg, err))
        # (b) 引擎列透传(不查询不替换;来源标注)
        rep.skip("  (b-engine/透传) CI=%s | audit=%s [%s]"
                 % (row.get("ci", "?"), row.get("audit", "?"), ENGINE_SOURCE_NOTE))
        # (c) 行自检结论
        if rep.fail_count == row_fail_before:
            row_pass += 1
            rep.skip("  (c) 行自检: PASS")
        else:
            rep.skip("  (c) 行自检: FAIL(git 列核验失败,见上 FAIL 行)")

    print("--- SUMMARY ---")
    print("rows=%d checked=%d row_pass=%d pass_checks=%d fail_checks=%d"
          % (total, total, row_pass, rep.pass_count, rep.fail_count))
    if rep.fail_count == 0 and row_pass == total:
        print("RESULT: ALL GREEN(rows=%d, fail=0)" % total)
        return 0
    print("RESULT: FAIL(rows=%d, row_fail=%d, fail_lines=%d)"
          % (total, total - row_pass, rep.fail_count))
    return 1


if __name__ == "__main__":
    sys.exit(main())
