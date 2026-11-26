#!/usr/bin/env python3
"""Probe top-level structure of the frozen snapshot / calendar / report.json (read-only).

usage: python3 -I probe_structure.py <snapshot.json> <release_calendar.json> <report.json>
"""
import json
import sys


def describe(obj, depth=0, max_depth=2, key=""):
    pad = "  " * depth
    if isinstance(obj, dict):
        keys = list(obj.keys())
        print(f"{pad}{key}: dict({len(keys)}) keys={keys[:40]}")
        if depth < max_depth:
            for k in keys[:40]:
                describe(obj[k], depth + 1, max_depth, k)
    elif isinstance(obj, list):
        print(f"{pad}{key}: list({len(obj)})"
              + (f" first_type={type(obj[0]).__name__}" if obj else ""))
        if obj and depth < max_depth and isinstance(obj[0], dict):
            describe(obj[0], depth + 1, max_depth, key + "[0]")
    else:
        s = repr(obj)
        print(f"{pad}{key}: {type(obj).__name__} = {s[:120]}")


snap_path, cal_path, rep_path = sys.argv[1:4]

print("=" * 30, "SNAPSHOT top-level", "=" * 30)
with open(snap_path, "r", encoding="utf-8") as f:
    snap = json.load(f)
for k, v in snap.items():
    if isinstance(v, dict):
        print(f"{k}: dict({len(v)}) sample_keys={list(v.keys())[:25]}")
    elif isinstance(v, list):
        print(f"{k}: list({len(v)})")
    else:
        print(f"{k}: {type(v).__name__} = {repr(v)[:200]}")

print()
print("research_as_of =", snap.get("research_as_of"))
print("target_date   =", snap.get("target_date"))
ss = snap.get("series_store")
if isinstance(ss, dict):
    ids = sorted(ss.keys())
    print(f"series_store n={len(ids)}")
    print("ids:", ids)
    first = ids[0]
    print("sample series entry keys:", list(ss[first].keys()) if isinstance(ss[first], dict) else type(ss[first]))
    print(json.dumps(ss[first], ensure_ascii=False)[:600])

print()
print("=" * 30, "CALENDAR top-level", "=" * 30)
with open(cal_path, "r", encoding="utf-8") as f:
    cal = json.load(f)
describe(cal, 0, 1)

print()
print("=" * 30, "report.json top-level", "=" * 30)
with open(rep_path, "r", encoding="utf-8") as f:
    rep = json.load(f)
for k, v in rep.items():
    if isinstance(v, dict):
        print(f"{k}: dict({len(v)}) keys={list(v.keys())[:40]}")
    elif isinstance(v, list):
        print(f"{k}: list({len(v)})")
    else:
        print(f"{k}: {type(v).__name__} = {repr(v)[:200]}")
