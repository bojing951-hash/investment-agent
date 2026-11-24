#!/usr/bin/env python3
"""Seat-owned read-only structure explorer. Usage: python3 -I explore_structure.py <file> [<file> ...]
Prints top-level keys and shallow types only (no bulk dump)."""
import json
import sys


def describe(obj, depth=0, maxdepth=2, prefix=""):
    if isinstance(obj, dict):
        keys = list(obj.keys())
        print(f"{prefix}dict[{len(keys)}]: {keys[:60]}")
        if depth < maxdepth:
            for k in keys[:40]:
                describe(obj[k], depth + 1, maxdepth, prefix + "  ." + str(k) + " -> ")
    elif isinstance(obj, list):
        print(f"{prefix}list[{len(obj)}]")
        if obj and depth < maxdepth:
            describe(obj[0], depth + 1, maxdepth, prefix + "  [0] -> ")
    else:
        s = repr(obj)
        print(f"{prefix}{type(obj).__name__}: {s[:120]}")


for path in sys.argv[1:]:
    print("=" * 100)
    print("FILE:", path)
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    describe(data, maxdepth=2)
