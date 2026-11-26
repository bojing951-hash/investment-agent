#!/usr/bin/env python3
"""Read-only structure dump of report.json (keys only, truncated values)."""
import json
import sys


def describe(obj, depth, max_depth, name, out, maxkeys=60):
    pad = "  " * depth
    if isinstance(obj, dict):
        keys = list(obj.keys())
        out.append(f"{pad}{name}: dict({len(keys)}) keys={keys[:maxkeys]}")
        if depth < max_depth:
            for k in keys[:maxkeys]:
                describe(obj[k], depth + 1, max_depth, k, out, maxkeys)
    elif isinstance(obj, list):
        out.append(f"{pad}{name}: list({len(obj)})")
        if depth < max_depth and obj:
            describe(obj[0], depth + 1, max_depth, "[0]", out, maxkeys)
            if len(obj) > 1 and isinstance(obj[1], dict) and (not isinstance(obj[0], dict) or set(obj[0].keys()) != set(obj[1].keys())):
                describe(obj[1], depth + 1, max_depth, "[1]", out, maxkeys)
    else:
        s = repr(obj)
        if len(s) > 160:
            s = s[:160] + "..."
        out.append(f"{pad}{name}: {type(obj).__name__} = {s}")


def main():
    path = sys.argv[1]
    max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    out = []
    describe(data, 0, max_depth, "ROOT", out)
    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
