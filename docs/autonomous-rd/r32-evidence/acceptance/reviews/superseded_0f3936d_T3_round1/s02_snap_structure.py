#!/usr/bin/env python3
"""Read-only structure dump of the frozen snapshot (keys only, truncated values)."""
import json
import sys


def describe(obj, depth, max_depth, name, out, maxkeys=120):
    pad = "  " * depth
    if isinstance(obj, dict):
        keys = list(obj.keys())
        shown = keys[:maxkeys]
        out.append(f"{pad}{name}: dict({len(keys)}) keys={shown}{' …' if len(keys) > maxkeys else ''}")
        if depth < max_depth:
            for k in shown:
                if k == "series_store":
                    # only list the metric ids, not all series
                    v = obj[k]
                    if isinstance(v, dict):
                        out.append(f"{pad}  series_store metric ids ({len(v)}): {sorted(v.keys())}")
                        first = sorted(v.keys())[0]
                        describe(v[first], depth + 2, max_depth, f"series_store[{first}]", out, maxkeys)
                    continue
                describe(obj[k], depth + 1, max_depth, k, out, maxkeys)
    elif isinstance(obj, list):
        out.append(f"{pad}{name}: list({len(obj)})")
        if depth < max_depth and obj:
            describe(obj[0], depth + 1, max_depth, "[0]", out, maxkeys)
    else:
        s = repr(obj)
        if len(s) > 200:
            s = s[:200] + "..."
        out.append(f"{pad}{name}: {type(obj).__name__} = {s}")


def main():
    path = sys.argv[1]
    max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    out = []
    describe(data, 0, max_depth, "SNAP", out)
    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
