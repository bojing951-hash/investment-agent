#!/usr/bin/env python3
"""Seat script: explore top-level structure of report.json / snapshot / calendar / registry.
Read-only. Usage: python3 -I explore_structure.py <report.json> <snapshot.json> <calendar.json> <registry.json>
"""
import json
import sys


def shape(obj, depth=0, maxdepth=2, prefix=""):
    out = []
    if isinstance(obj, dict):
        for k in list(obj.keys())[:80]:
            v = obj[k]
            t = type(v).__name__
            if isinstance(v, (dict, list)):
                n = len(v)
                out.append(f"{prefix}{k}: {t}[{n}]")
                if depth < maxdepth:
                    out.extend(shape(v, depth + 1, maxdepth, prefix + "  "))
            else:
                s = repr(v)
                if len(s) > 120:
                    s = s[:120] + "..."
                out.append(f"{prefix}{k}: {t} = {s}")
    elif isinstance(obj, list):
        if obj:
            v = obj[0]
            out.append(f"{prefix}[0]: {type(v).__name__}")
            if isinstance(v, dict) and depth < maxdepth:
                out.extend(shape(v, depth + 1, maxdepth, prefix + "  "))
    return out


def main():
    report_p, snap_p, cal_p, reg_p = sys.argv[1:5]
    with open(report_p, encoding="utf-8") as f:
        rep = json.load(f)
    print("=== report.json top keys ===")
    for line in shape(rep, maxdepth=1):
        print(line)
    print()
    with open(snap_p, encoding="utf-8") as f:
        snap = json.load(f)
    print("=== snapshot top keys ===")
    for line in shape(snap, maxdepth=1):
        print(line)
    print()
    with open(cal_p, encoding="utf-8") as f:
        cal = json.load(f)
    print("=== calendar top keys ===")
    for line in shape(cal, maxdepth=1):
        print(line)
    print()
    with open(reg_p, encoding="utf-8") as f:
        reg = json.load(f)
    print("=== registry top keys ===")
    for line in shape(reg, maxdepth=1):
        print(line)


if __name__ == "__main__":
    main()
