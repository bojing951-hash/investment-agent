#!/usr/bin/python3 -I
"""席位自写探针 s13c: 冻结日历中 2026-09-15..2026-11-23 的条目(只读)."""
import json
import sys

cal = json.load(open(sys.argv[1], "r", encoding="utf-8"))
print("top keys:", list(cal.keys())[:12])
ents = cal.get("entries") or cal.get("events") or cal.get("releases") or []
if isinstance(ents, dict):
    ents = list(ents.values())
print("n entries:", len(ents))
for e in ents:
    s = json.dumps(e, ensure_ascii=False)
    for k in ("release_date", "date", "scheduled_date", "published_on", "decision_date"):
        v = e.get(k) if isinstance(e, dict) else None
        if isinstance(v, str) and "2026-09-15" <= v <= "2026-11-23":
            print(s[:330])
            break
