#!/usr/bin/python3 -I
"""Has the audited judgment changed since my pretty copy was taken? usage: s23_drift.py <_judgment_pretty.json> <agent_judgment.json> <report.json> <MAP_REPORT.sha256> <MAP_REPORT.md>"""
import sys, json, hashlib
a = json.load(open(sys.argv[1], encoding="utf-8"))
b = json.load(open(sys.argv[2], encoding="utf-8"))
sa = json.dumps(a, ensure_ascii=False, indent=2, sort_keys=True)
sb = json.dumps(b, ensure_ascii=False, indent=2, sort_keys=True)
print("pretty copy == current agent_judgment.json (canonical):", sa == sb, len(sa), len(sb))
if sa != sb:
    la, lb = sa.split("\n"), sb.split("\n")
    import difflib
    n = 0
    for l in difflib.unified_diff(la, lb, lineterm="", n=0):
        if l.startswith(("+", "-")) and not l.startswith(("+++", "---")):
            n += 1
            if n <= 40:
                print("  ", l[:300])
    print("changed lines:", n)
rep = json.load(open(sys.argv[3], encoding="utf-8"))
print("report.json agent_judgment == standalone agent_judgment.json:", json.dumps(rep.get("agent_judgment"), sort_keys=True, ensure_ascii=False) == json.dumps(b, sort_keys=True, ensure_ascii=False))
print("report.json top keys:", sorted(rep.keys())[:60])
sr = rep.get("semantic_review")
print("report.json semantic_review:", json.dumps(sr, ensure_ascii=False)[:600])
print("MAP_REPORT.sha256 file:", open(sys.argv[4], encoding="utf-8").read().strip())
h = hashlib.sha256(open(sys.argv[5], "rb").read()).hexdigest()
print("MAP_REPORT.md sha256 now:", h)
print("judgment keys:", sorted(b.keys()))
print("judgment status-ish fields:", {k: b[k] for k in b if k in ("status", "verdict", "version", "judgment_id", "created_at", "round", "review_round")})
