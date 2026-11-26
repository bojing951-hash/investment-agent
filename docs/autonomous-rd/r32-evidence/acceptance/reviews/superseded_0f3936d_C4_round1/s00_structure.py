#!/usr/bin/python3
"""Read-only structure explorer for report.json / snapshot / calendar / registry.
Usage: python3 -I s00_structure.py <report.json> [maxdepth]
"""
import json
import sys


def describe(obj, depth=0, maxdepth=3, key=""):
    pad = "  " * depth
    if isinstance(obj, dict):
        keys = list(obj.keys())
        print(f"{pad}{key}: dict({len(keys)}) keys={keys[:40]}{'...' if len(keys) > 40 else ''}")
        if depth < maxdepth:
            for k in keys[:40]:
                describe(obj[k], depth + 1, maxdepth, k)
    elif isinstance(obj, list):
        print(f"{pad}{key}: list({len(obj)})")
        if obj and depth < maxdepth:
            describe(obj[0], depth + 1, maxdepth, "[0]")
    else:
        s = repr(obj)
        if len(s) > 200:
            s = s[:200] + "..."
        print(f"{pad}{key}: {type(obj).__name__} = {s}")


def main():
    path = sys.argv[1]
    maxdepth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    describe(data, 0, maxdepth, "ROOT")


if __name__ == "__main__":
    main()
