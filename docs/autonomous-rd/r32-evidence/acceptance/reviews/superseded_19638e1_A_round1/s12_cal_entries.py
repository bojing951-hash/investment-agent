#!/usr/bin/python3 -I
"""Print every entry of the frozen release calendar (read-only).
Usage: python3 -I s12_cal_entries.py <release_calendar.json>
"""
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as f:
    d = json.load(f)
print("TOP:", {k: (v if not isinstance(v, (list, dict)) else type(v).__name__ + "[%d]" % len(v)) for k, v in d.items()})
for k, v in d.items():
    if k not in ("entries", "batches") and isinstance(v, (list, dict)):
        print("--", k, json.dumps(v, ensure_ascii=False)[:1500])
for i, e in enumerate(d.get("entries", [])):
    print("ENTRY[%d]" % i, json.dumps(e, ensure_ascii=False))
for i, b in enumerate(d.get("batches", [])):
    print("BATCH[%d]" % i, json.dumps(b, ensure_ascii=False)[:600])
