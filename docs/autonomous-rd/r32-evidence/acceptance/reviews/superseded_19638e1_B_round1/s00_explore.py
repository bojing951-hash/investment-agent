# -*- coding: utf-8 -*-
"""只读探查: 快照顶层结构。用法: python3 -I s00_explore.py <snapshot_path>"""
import json, sys
p = sys.argv[1]
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
print("TOP KEYS:", list(d.keys()))
for k, v in d.items():
    if isinstance(v, dict):
        print(" ", k, "dict keys(%d):" % len(v), list(v.keys())[:40])
    elif isinstance(v, list):
        print(" ", k, "list len", len(v))
    else:
        s = repr(v)
        print(" ", k, "=", s[:300])
ss = d.get('series_store')
print("series_store type", type(ss).__name__, "n=", len(ss))
if isinstance(ss, dict):
    ks = sorted(ss.keys())
    print("SERIES KEYS:", ks)
    first = ss[ks[0]]
    print("first series entry type", type(first).__name__)
    if isinstance(first, dict):
        print("  entry keys", list(first.keys()))
        for kk, vv in first.items():
            if isinstance(vv, list):
                print("   ", kk, "list len", len(vv), "head", vv[:3], "tail", vv[-3:])
            else:
                print("   ", kk, "=", repr(vv)[:300])
