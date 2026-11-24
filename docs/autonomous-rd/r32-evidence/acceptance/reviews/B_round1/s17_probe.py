#!/usr/bin/python3 -I
"""席位探针 s17: 受审稿结构面逐项打印(证据引用/分级/声明/契约/未渲染字段). 只读.

用法: /usr/bin/python3 -I s17_probe.py <agent_judgment.json> <report.json> <运行目录>
"""
import json
import os
import sys
from collections import Counter

aj = json.load(open(sys.argv[1], encoding="utf-8"))
rep = json.load(open(sys.argv[2], encoding="utf-8"))
RUN = sys.argv[3]
print("TOP KEYS:", list(aj.keys()))
print("\n=== agent_declaration ===")
print(json.dumps(aj.get("agent_declaration"), ensure_ascii=False, indent=1))
print("\n=== meta-ish keys ===")
for k in aj:
    if k not in ("l3", "l4", "reader_map", "quality_gate_notes", "agent_declaration"):
        print(k, "=>", json.dumps(aj[k], ensure_ascii=False)[:1500])

print("\n=== L3 contradictions ===")
raw_c = []
for c in aj["l3"]["contradictions"]:
    refs = c.get("evidence_refs", [])
    raw_c += list(refs)
    print("-", c.get("id"), "| keys:", [k for k in c.keys() if k not in ("statement", "competing_explanations", "evidence_refs")])
    print("   evidence_refs (%d): %s" % (len(refs), refs))
    for k in c:
        if k not in ("id", "statement", "competing_explanations", "evidence_refs"):
            print("   %s: %s" % (k, json.dumps(c[k], ensure_ascii=False)[:600]))
print("raw contradiction refs:", len(raw_c), "unique:", len(set(raw_c)), Counter(raw_c))
print("\n=== L3 mechanism_chains ===")
raw_m = []
for ch in aj["l3"]["mechanism_chains"]:
    print("- chain keys:", list(ch.keys()))
    for k in ch:
        if k != "links":
            print("   %s: %s" % (k, json.dumps(ch[k], ensure_ascii=False)[:400]))
    for i, lk in enumerate(ch["links"]):
        refs = lk.get("evidence_refs", [])
        raw_m += list(refs)
        print("   link", i, "keys:", list(lk.keys()))
        print("     evidence_level:", lk.get("evidence_level"), "| refs (%d): %s" % (len(refs), refs))
        for k in lk:
            if k not in ("text", "evidence_refs", "evidence_level", "causal_hypothesis", "competing_explanation", "discriminator"):
                print("     %s: %s" % (k, json.dumps(lk[k], ensure_ascii=False)[:700]))
print("raw mechanism refs:", len(raw_m), "unique:", len(set(raw_m)), Counter(raw_m))
print("\n=== L4 ===")
print("l4 keys:", list(aj["l4"].keys()))
for s in aj["l4"]["scenarios"]:
    r = s["rows"]
    refs = r.get("evidence_refs", [])
    print("-", s["id"], "keys:", list(s.keys()), "| rows keys:", list(r.keys()))
    print("   refs (%d): %s" % (len(refs), refs))
    for k in r:
        if k not in ("evidence_refs",):
            print("   %s: %s" % (k, json.dumps(r[k], ensure_ascii=False)[:500]))
for k in aj["l4"]:
    if k != "scenarios":
        print("l4.%s: %s" % (k, json.dumps(aj["l4"][k], ensure_ascii=False)[:800]))
print("\n=== reader_map keys ===", list(aj["reader_map"].keys()))
print("\n=== turnings (非渲染字段) ===")
for t in aj["reader_map"]["turnings"]:
    print("-", json.dumps({k: v for k, v in t.items() if k in ("narrative",)}, ensure_ascii=False))
print("\n=== transmission links verdict_note ===")
for ch in aj["reader_map"]["transmission"]:
    print("chain keys:", list(ch.keys()))
    for i, lk in enumerate(ch["links"]):
        print("-", i, "keys:", list(lk.keys()))
        print("   verdict_note:", lk.get("verdict_note"))
print("\n=== 渲染文件中 STALE / 契约 ===")
for name in ("MAP_REPORT.md", "FULL_REPORT.md", "report.md"):
    txt = open(os.path.join(RUN, name), encoding="utf-8").read().splitlines()
    for i, line in enumerate(txt, 1):
        if any(w in line for w in ("STALE", "VERIFIED", "契约", "83 天", "145 天", "收盘口径", "同日收盘", "盘中")):
            print("%s:%d: %s" % (name, i, line[:330]))
