#!/usr/bin/python3 -I
"""List nested keys of a JSON subtree (read-only).
Usage: python3 -I s14_keys.py <report.json> <steps.61.envelope.data> [maxdepth]
"""
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as f:
    d = json.load(f)
o = d
for part in sys.argv[2].split("."):
    o = o[int(part)] if isinstance(o, list) else o[part]
maxd = int(sys.argv[3]) if len(sys.argv) > 3 else 2


def walk(x, path, depth):
    if depth > maxd:
        return
    if isinstance(x, dict):
        for k, v in x.items():
            if isinstance(v, (dict, list)):
                size = len(v)
                print("%s.%s  <%s %d>" % (path, k, type(v).__name__, size))
                if isinstance(v, dict):
                    walk(v, path + "." + k, depth + 1)
                elif v and isinstance(v[0], dict) and depth < maxd:
                    walk(v[0], path + "." + k + "[0]", depth + 1)
            else:
                print("%s.%s = %s" % (path, k, str(v)[:160]))
    elif isinstance(x, list) and x and isinstance(x[0], dict):
        walk(x[0], path + "[0]", depth + 1)


walk(o, sys.argv[2], 0)
