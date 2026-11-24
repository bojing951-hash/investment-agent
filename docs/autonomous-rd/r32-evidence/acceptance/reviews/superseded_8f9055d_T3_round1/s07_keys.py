#!/usr/bin/python3 -I
"""Print keys/shape of a JSON sub-tree without long arrays. Args: <json> <dotted.path> [maxdepth]
"""
import json
import re
import sys


def get(obj, path):
    cur = obj
    for name, idx in re.findall(r"([^.\[\]]+)|\[(\*|\d+)\]", path):
        if name:
            cur = cur[name]
        else:
            cur = cur[int(idx)]
    return cur


def show(o, ind, depth, maxd):
    pad = " " * ind
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (dict, list)):
                n = len(v)
                print(f"{pad}{k}: {type(v).__name__}[{n}]")
                if depth < maxd:
                    show(v, ind + 2, depth + 1, maxd)
            else:
                s = json.dumps(v, ensure_ascii=False)
                print(f"{pad}{k}: {s[:300]}")
    elif isinstance(o, list):
        if o and isinstance(o[0], (dict, list)) and depth < maxd:
            print(f"{pad}[0]:")
            show(o[0], ind + 2, depth + 1, maxd)
        elif o and not isinstance(o[0], (dict, list)):
            print(f"{pad}{json.dumps(o[:12], ensure_ascii=False)}")


d = json.load(open(sys.argv[1], "r", encoding="utf-8"))
show(get(d, sys.argv[2]), 0, 0, int(sys.argv[3]) if len(sys.argv) > 3 else 2)
