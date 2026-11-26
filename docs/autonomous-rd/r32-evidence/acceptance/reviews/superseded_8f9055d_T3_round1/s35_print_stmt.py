#!/usr/bin/python3 -I
"""Print the three L3 contradiction statements in full (wording reference for suggested fixes). Read-only.
Args: <agent_judgment.json> <release_calendar.json>
"""
import json
import sys

jd = json.load(open(sys.argv[1], "r", encoding="utf-8"))
cal = json.load(open(sys.argv[2], "r", encoding="utf-8"))
for c in jd["l3"]["contradictions"]:
    print("=== ", c.get("contradiction_id") or c.get("id"))
    for k, v in c.items():
        if k in ("statement",):
            print("[%s] %s" % (k, v))
        elif isinstance(v, str) and len(v) < 600:
            print("[%s] %s" % (k, v))
        else:
            print("[%s] <%s len %d> %s" % (k, type(v).__name__, len(json.dumps(v, ensure_ascii=False)), json.dumps(v, ensure_ascii=False)[:260]))
print("=== l4 scenario texts mentioning the BOJ target")
for sc in jd["l4"]["scenarios"]:
    t = json.dumps(sc, ensure_ascii=False)
    i = t.find("1.25")
    while i >= 0:
        print("  …%s…" % t[max(0, i - 60):i + 30])
        i = t.find("1.25", i + 1)
print("=== release calendar BOJ records")
for e in cal.get("entries", []):
    if e.get("metric_id") == "JP_POLICY_TARGET":
        print("  ", json.dumps(e, ensure_ascii=False)[:500])
