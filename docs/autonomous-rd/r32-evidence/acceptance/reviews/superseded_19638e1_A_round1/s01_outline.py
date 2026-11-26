#!/usr/bin/python3 -I
"""Outline of report.json (read-only). Usage: python3 -I s01_outline.py <report.json> <maxdepth>"""
import json
import sys


def outline(obj, depth=0, maxdepth=3, key=""):
    pad = "  " * depth
    if isinstance(obj, dict):
        print(f"{pad}{key}: dict({len(obj)})")
        if depth < maxdepth:
            for k, v in obj.items():
                outline(v, depth + 1, maxdepth, k)
    elif isinstance(obj, list):
        print(f"{pad}{key}: list({len(obj)})")
        if depth < maxdepth and obj:
            outline(obj[0], depth + 1, maxdepth, "[0]")
    else:
        s = repr(obj)
        if len(s) > 160:
            s = s[:160] + "..."
        print(f"{pad}{key}: {type(obj).__name__} = {s}")


def main():
    path = sys.argv[1]
    maxdepth = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    outline(d, 0, maxdepth, "root")


if __name__ == "__main__":
    main()
