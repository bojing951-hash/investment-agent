#!/usr/bin/env python3
"""Read-only: generic JSON file structure dump.
usage: s04_json_structure.py <file.json> [max_depth] [maxkeys]
"""
import json
import sys


def describe(obj, depth, max_depth, name, out, maxkeys=80):
    pad = "  " * depth
    if isinstance(obj, dict):
        keys = list(obj.keys())
        shown = keys[:maxkeys]
        out.append(f"{pad}{name}: dict({len(keys)}) keys={shown}{' …' if len(keys) > maxkeys else ''}")
        if depth < max_depth:
            for k in shown:
                describe(obj[k], depth + 1, max_depth, k, out, maxkeys)
    elif isinstance(obj, list):
        out.append(f"{pad}{name}: list({len(obj)})")
        if depth < max_depth and obj:
            describe(obj[0], depth + 1, max_depth, "[0]", out, maxkeys)
    else:
        s = repr(obj)
        if len(s) > 240:
            s = s[:240] + "..."
        out.append(f"{pad}{name}: {type(obj).__name__} = {s}")


def main():
    path = sys.argv[1]
    max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    maxkeys = int(sys.argv[3]) if len(sys.argv) > 3 else 80
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    out = []
    describe(data, 0, max_depth, "FILE", out, maxkeys)
    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
