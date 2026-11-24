#!/usr/bin/env python3
"""Deeper probe (read-only): snapshot gate_a/quality/notes/facts sample; calendar entries/batches.

usage: python3 -I probe2.py <snapshot.json> <release_calendar.json>
"""
import json
import sys

snap_path, cal_path = sys.argv[1:3]
snap = json.load(open(snap_path, "r", encoding="utf-8"))
cal = json.load(open(cal_path, "r", encoding="utf-8"))

print("=== gate_a ===")
print(json.dumps(snap["gate_a"], ensure_ascii=False, indent=1)[:6000])
print("\n=== quality ===")
print(json.dumps(snap["quality"], ensure_ascii=False, indent=1)[:3000])
print("\n=== notes ===")
print(json.dumps(snap["notes"], ensure_ascii=False, indent=1)[:3000])
print("\n=== sources_status ===")
print(json.dumps(snap["sources_status"], ensure_ascii=False, indent=1)[:4000])
print("\n=== series_store_notes ===")
print(json.dumps(snap["series_store_notes"], ensure_ascii=False, indent=1)[:4000])
print("\n=== series_provenance ===")
print(json.dumps(snap["series_provenance"], ensure_ascii=False, indent=1)[:2000])
print("\n=== facts sample (first 3) ===")
print(json.dumps(snap["facts"][:3], ensure_ascii=False, indent=1)[:2000])
print("\n=== facts ids ===")
print([f.get("id") or f.get("metric_id") for f in snap["facts"]])
print("\n=== reconciliation ===")
print(json.dumps(snap["reconciliation"], ensure_ascii=False)[:3000])

print("\n=== calendar spec ===")
print(cal["spec"])
print("\n=== calendar batches ===")
print(json.dumps(cal["batches"], ensure_ascii=False, indent=1)[:5000])
print("\n=== calendar entries ===")
for e in cal["entries"]:
    print(json.dumps(e, ensure_ascii=False))
