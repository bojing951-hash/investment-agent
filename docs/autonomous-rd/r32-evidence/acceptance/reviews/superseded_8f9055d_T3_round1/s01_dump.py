#!/usr/bin/python3 -I
"""Dump a JSON sub-tree by dotted/bracket path. Args: <json> <path> [maxlist]
path forms: a.b.c  or a.b[3].c  (list index)  or a.b[*] (each element)
"""
import json
import sys
import re


def get(obj, path, maxlist=None):
    tokens = re.findall(r"([^.\[\]]+)|\[(\*|\d+)\]", path)
    cur = [obj]
    for name, idx in tokens:
        nxt = []
        for c in cur:
            if name:
                if isinstance(c, dict) and name in c:
                    nxt.append(c[name])
                else:
                    raise SystemExit(f"path miss: {name} in {path}")
            else:
                if isinstance(c, list):
                    if idx == "*":
                        nxt.extend(c)
                    else:
                        nxt.append(c[int(idx)])
                else:
                    raise SystemExit(f"path miss: index on non-list at {path}")
        cur = nxt
    return cur


def main():
    path = sys.argv[1]
    sub = sys.argv[2]
    maxlist = int(sys.argv[3]) if len(sys.argv) > 3 else None
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    res = get(d, sub)
    if len(res) == 1 and not sub.endswith("[*]"):
        out = res[0]
    else:
        out = res
    if maxlist is not None and isinstance(out, list):
        out = out[:maxlist]
    s = json.dumps(out, ensure_ascii=False, indent=1)
    lim = int(sys.argv[4]) if len(sys.argv) > 4 else 60000
    if len(s) > lim:
        print(s[:lim])
        print(f"...[TRUNCATED total {len(s)} chars]")
    else:
        print(s)


if __name__ == "__main__":
    main()
