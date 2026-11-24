#!/usr/bin/python3 -I
"""Find dict keys matching a substring anywhere in a JSON file (read-only).
Usage: python3 -I s15_findkeys.py <report.json> <substr> [<substr> ...]
"""
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as f:
    d = json.load(f)
subs = sys.argv[2:]
seen = {}


def walk(o, path, depth=0):
    if isinstance(o, dict):
        for k, v in o.items():
            if any(s in str(k) for s in subs):
                key = str(k)
                if key not in seen:
                    seen[key] = (path + "." + key, type(v).__name__, (len(v) if hasattr(v, "__len__") else v))
            if depth < 9:
                walk(v, path + "." + str(k), depth + 1)
    elif isinstance(o, list) and o and depth < 9:
        walk(o[0], path + "[0]", depth + 1)


walk(d, "")
for k, (p, t, n) in sorted(seen.items()):
    print("%-40s %-6s %s  @ %s" % (k, t, n, p[:140]))
