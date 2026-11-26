#!/usr/bin/python3 -I
"""Diff report.json embedded agent_judgment vs standalone agent_judgment.json. usage: s24_embed.py <report.json> <agent_judgment.json>"""
import sys, json
rep = json.load(open(sys.argv[1], encoding="utf-8"))
b = json.load(open(sys.argv[2], encoding="utf-8"))
a = rep["agent_judgment"]
print("type embedded:", type(a).__name__, "; standalone keys:", sorted(b.keys()))
if isinstance(a, dict):
    print("embedded keys:", sorted(a.keys()))
sa = json.dumps(a, ensure_ascii=False, indent=1, sort_keys=True).split("\n")
sb = json.dumps(b, ensure_ascii=False, indent=1, sort_keys=True).split("\n")
import difflib
n = 0
for l in difflib.unified_diff(sa, sb, "embedded", "standalone", lineterm="", n=1):
    if l.startswith(("@", "---", "+++")):
        print(l[:200]); continue
    n += 1
    if n <= 60:
        print(l[:330])
print("diff lines:", n)
