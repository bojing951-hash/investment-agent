# -*- coding: utf-8 -*-
"""Build drafts PROSE.draft.md / VERDICT.draft.json from parts (seat-own files only).
usage: python3 -I s12_build.py <run_dir>"""
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def mod(n):
    s = importlib.util.spec_from_file_location(n, os.path.join(HERE, n + ".py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


run = sys.argv[1]
rd = lambda n: open(os.path.join(HERE, n), encoding="utf-8").read()
rt = json.load(open(os.path.join(HERE, "recompute_table.json"), encoding="utf-8"))
sm = rt["summary"]
assert (sm["points"], sm["ok"], sm["mismatches"], sm["not_found"], sm["errors"]) == (301, 301, 0, 0, 0), sm
assert len(rt["rows"]) == 301 and all(x["ok"] for x in rt["rows"])
p6 = json.load(open(os.path.join(HERE, "_part_p6.json"), encoding="utf-8"))
SH = dict((f, sha(os.path.join(run, f))) for f in ("agent_judgment.json", "report.json", "MAP_REPORT.md"))
assert SH == p6["F"]["info"]["sha"], "audited version changed since parts ran"
J = json.load(open(os.path.join(run, "agent_judgment.json"), encoding="utf-8"))
jdump = json.dumps(J, ensure_ascii=False)
items = mod("s12_items_a").ITEMS_A + mod("s12_items_b").ITEMS_B
attacks = mod("s12_attacks_a").ATTACKS_A + mod("s12_attacks_b").ATTACKS_B
six = mod("s12_six_a").SIX_A + mod("s12_six_b").SIX_B
D = mod("s12_desc")
for it in items:
    if it["original"]:
        assert it["original"] in jdump, "original not found: " + it["id"]
n_major = [x for x in items if x["severity"] == "MAJOR"]
n_min = [x for x in items if x["severity"] == "MINOR"]
n_nit = [x for x in items if x["severity"] == "NIT"]
verdict = "UPHELD" if not n_major else "REV"
assert verdict == "UPHELD"
bools = sum(1 for x in rt["rows"] if isinstance(x["computed"], bool) or (isinstance(x["computed"], list) and x["computed"] and all(isinstance(v, bool) for v in x["computed"])))
cats = "、".join("%s %d/%d" % (k, v[0], v[1]) for k, v in sm["by_cat"].items())
notes = ("独立零上下文席位裁决(未读研判席/操作席中间产物、安装树 audit/ 与既往审查史,未联网、未运行引擎写操作)。"
         "受审版本: agent_judgment.json sha256 前 12 位 %s、report.json %s(run 20261123T235139Z,代码印章 36499bb78a18)。"
         "抽核 %d 点、偏离 %d、未找到原文 0、脚本错误 0(分项: %s);全部由冻结快照 series_store、冻结发布日历、注册表与 report.json 引擎面独立直算后与判断档比对。"
         "逐条核验: 两地央行当前目标利率(日本央行约 1.25%%,2026-09-18 决议、2026-09-24 生效、2026-10-30 确认维持;欧央行 MRO 2.65%%/DFR 2.5%%,2026-09-16 生效,窗内两次各 +25bp)的数值、生效日与现行有效属实,"
         "待生效决定与现行目标已分记(引擎记录面无待生效项;欧央行 2026-09-16 后决议面为盲区,已单列【尚未验证】);通胀同比基期=去年同月(日本 2.99→2.44、欧元区 2.1→4.0)属实,东京 CPI 缺基期未给同比。"
         "六查+证伪共 %d 次反方攻击,无一项动摇结论。MAJOR %d;MINOR %d(传导环 1 日本腿反向时序未披露、S1 触发/证伪阈间不可判定区、S1 日本分量无数值证伪阈、「欧央行分量须待日历补录」偏强、"
         "数据需求面 6 项 insufficient_coverage 未说明、契约验证 1 项 STALE 未写明、对质注记与转折叙事未在读者文档渲染、注册表两处「决议即时生效」与引擎惯例未并列);NIT %d(S2 形态型不可判定区、汇率环 main_predicts 保留被修正的原预言、"
         "东京 CPI「中旬」标签、目标实录条目依据未写);均不改变结论。裁决 %s。"
         ) % (SH["agent_judgment.json"][:12], SH["report.json"][:12], sm["points"], sm["mismatches"], cats, len(attacks), len(n_major), len(n_min), len(n_nit), verdict)
V = {"seat": "semantic-audit-seat", "reviewer": "independent-zero-context-seat-r32-t3-round1", "verdict": verdict, "overall": verdict, "notes": notes,
     "items": [dict((k, ("%s: %s" % (it["id"], it["where"])) if k == "where" else it[k]) for k in ("severity", "where", "note", "original", "fix")) for it in items],
     "must_fix": [], "counterexamples_sought": attacks, "recompute_points": sm["points"], "recompute_mismatches": sm["mismatches"], "mismatch_details": [], "audited_at": "2026-11-24"}
L = ["# Audit-R32 T3 Round-1 独立语义审查:复算清单与裁决依据", "",
     "## 0 席位、受审版本与边界", "",
     "- 席位: independent-zero-context-seat-r32-t3-round1(semantic-audit-seat);审查日期 2026-11-24。",
     "- 受审对象: 运行目录 20261123T235139Z_2026年11月_日本和欧元区的通胀与政策环境_两地央行当前官方政策目标利率各处 下 agent_judgment.json 全文(l3/l4/reader_map/quality_gate_notes/agent_declaration)与读者报告中的判断文字(MAP_REPORT.md/FULL_REPORT.md/report.md)。",
     "- 受审版本指纹(sha256): agent_judgment.json %s;report.json %s;MAP_REPORT.md %s。" % (SH["agent_judgment.json"], SH["report.json"], SH["MAP_REPORT.md"]),
     "- 冻结输入: root_overlay 与安装树的 release_calendar.json/metric_registry.json/research_snapshot_20261123.json 逐字节相同,与 report.json run.frozen_inputs 一致;代码印章 36499bb78a18dea1ff2b027074088b0ba404c3b8 在 report.json 内。",
     "- 运行事实: run 20261123T235139Z;研究截止日 2026-11-23;判断档 written_at 2026-11-24T08:25:44+08:00;attach 20261124T002553Z;run_ok true;allow_failed_run false;validation passed true。",
     "- 边界: 只读复算;未联网;未运行 ia_cli 写操作;未读 research_archive/、树内 docs/ 与 audit/、/tmp/r32-accept 下 out/、scripts/、replay/、install*、final*(只读安装树 final6 本身)与本席目录以外的 review* 目录;未委派子代理;未读既往审查内容。",
     "- 脚本与中间表(均在本席目录): t3lib.py、s7_p1.py–s7_p6.py(六个部件)、s7_recompute.py(合并)→ recompute_table.json / recompute_table.md;本文件与裁决 JSON 由 s12_*.py 一次生成。",
     "", "## 1 裁决", "",
     "**UPHELD** —— MAJOR 0 / MINOR %d / NIT %d;recompute_points %d / recompute_mismatches %d。" % (len(n_min), len(n_nit), sm["points"], sm["mismatches"]),
     "", "## 2 复算清单", "",
     "### 2.1 计数", "",
     "- 点数 %d: 一致 %d、偏离 %d、未找到原文 %d、脚本错误 %d(规程最低 90 点)。" % (sm["points"], sm["ok"], sm["mismatches"], sm["not_found"], sm["errors"]),
     "- 点型: 直算值为数值或数值列表的点 %d 个(自快照 series_store 直算、或与 report.json 确定性面逐位对账);直算值为布尔型的点 %d 个(字段在场、标注相称、披露一致)。" % (sm["points"] - bools, bools),
     "- 每点均先直算、后比对;数值比对容差=受审值末位的半个单位。", "",
     "### 2.2 按覆盖项", "", "| 覆盖项 | 点数 | 偏离 | 核验内容 |", "|---|---|---|---|"]
for k, v in sm["by_cat"].items():
    L.append("| %s | %d | %d | %s |" % (k, v[0], v[1], D.DESC.get(k, "")))
L += ["", "### 2.3 逐点表(出处键/直算值/报告值/一致)", "", rd("recompute_table.md").rstrip(), "", "## 3 六查+证伪(逐条)", ""]
for title, lines in six:
    L.append("### " + title)
    L += ["- " + x for x in lines if x]
    L.append("")
L += ["历史同步性: " + mod("s12_six_b").HISTORY_SYNC, "", "## 4 反方攻击记录", ""]
L += ["%d. %s" % (i + 1, a) for i, a in enumerate(attacks)]
L += ["", "## 5 问题清单", ""]
for sev, name in (("MAJOR", "MAJOR(无)"), ("MINOR", "MINOR"), ("NIT", "NIT")):
    L.append("### " + name)
    for it in items:
        if it["severity"] == sev:
            L.append("- **%s** `%s`" % (it["id"], it["where"]))
            L.append("  - 问题: " + it["note"])
            if it["original"]:
                L.append("  - 原句: 「%s」" % it["original"])
            if it["fix"]:
                L.append("  - 改句: 「%s」" % it["fix"])
    L.append("")
L += ["## 6 注记(不立项)", ""] + ["- " + x for x in D.NOTES] + [""]
open(os.path.join(HERE, "PROSE.draft.md"), "w", encoding="utf-8").write("\n".join(L))
open(os.path.join(HERE, "VERDICT.draft.json"), "w", encoding="utf-8").write(json.dumps(V, ensure_ascii=False, indent=1) + "\n")
json.load(open(os.path.join(HERE, "VERDICT.draft.json"), encoding="utf-8"))
print("OK points=%d mismatches=%d major=%d minor=%d nit=%d attacks=%d bool=%d" % (sm["points"], sm["mismatches"], len(n_major), len(n_min), len(n_nit), len(attacks), bools))
print("sha", SH)
print("PROSE bytes", os.path.getsize(os.path.join(HERE, "PROSE.draft.md")), "VERDICT bytes", os.path.getsize(os.path.join(HERE, "VERDICT.draft.json")))
