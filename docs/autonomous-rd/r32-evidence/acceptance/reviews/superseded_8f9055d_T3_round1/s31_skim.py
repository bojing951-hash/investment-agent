#!/usr/bin/python3 -I
"""Skim helper: print the verdict JSON's non-ledger parts and the section outline of the PROSE.
Read-only on the two deliverables. Args: <out_dir> [max_width]
"""
import json
import os
import sys

out_dir = sys.argv[1]
W = int(sys.argv[2]) if len(sys.argv) > 2 else 420
v = json.load(open(os.path.join(out_dir, "VERDICT-round1.json"), "r", encoding="utf-8"))


def cut(s, n=W):
    s = s if isinstance(s, str) else json.dumps(s, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + " …[%d chars]" % len(s)


for k in v:
    if k in ("items", "counterexamples_sought"):
        continue
    print("[%s] %s" % (k, cut(v[k], 3000)))
    print()
print("=== items (%d)" % len(v["items"]))
for it in v["items"]:
    print("-" * 8, it["severity"], "| where:", it["where"])
    print("   note:", cut(it["note"], 1400))
    print("   original:", cut(it["original"], 500))
    print("   fix:", cut(it["fix"], 700))
print("=== counterexamples_sought (%d)" % len(v["counterexamples_sought"]))
for i, a in enumerate(v["counterexamples_sought"]):
    print("%d. %s" % (i + 1, cut(a, 900)))
print("=== PROSE outline")
for i, line in enumerate(open(os.path.join(out_dir, "PROSE-round1.md"), "r", encoding="utf-8").read().split("\n")):
    if line.startswith("#") or i < 14:
        print("%4d: %s" % (i + 1, cut(line, 600)))
