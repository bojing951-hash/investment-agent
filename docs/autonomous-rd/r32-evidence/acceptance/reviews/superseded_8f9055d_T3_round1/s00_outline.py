#!/usr/bin/python3 -I
"""Read-only outline of report.json structure. Args: <report.json>"""
import json
import sys


def outline(obj, depth=0, maxdepth=3, prefix=""):
    pad = "  " * depth
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, dict):
                print(f"{pad}{k}: dict({len(v)})")
                if depth < maxdepth:
                    outline(v, depth + 1, maxdepth)
            elif isinstance(v, list):
                print(f"{pad}{k}: list({len(v)})")
                if v and depth < maxdepth and isinstance(v[0], dict):
                    print(f"{pad}  [0] keys: {list(v[0].keys())[:30]}")
            else:
                s = repr(v)
                if len(s) > 200:
                    s = s[:200] + "..."
                print(f"{pad}{k}: {s}")
    else:
        print(f"{pad}{type(obj).__name__} len={len(obj) if hasattr(obj, '__len__') else ''}")


def main():
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    print("TOP KEYS:", list(d.keys()))
    for k in d.keys():
        print("=" * 20, k, "=" * 20)
        v = d[k]
        if isinstance(v, dict):
            print(" keys:", list(v.keys())[:80])
        elif isinstance(v, list):
            print(" list len", len(v))
            if v and isinstance(v[0], dict):
                print(" [0] keys:", list(v[0].keys()))
        else:
            print(" value:", repr(v)[:300])
    maxdepth = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    for k in sys.argv[3:]:
        outline({k: d[k]}, 0, maxdepth)


if __name__ == "__main__":
    main()
