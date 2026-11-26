#!/usr/bin/python3 -I
# usage: s08_cells.py <report.json> [maxlen]
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
maxlen = int(sys.argv[2]) if len(sys.argv) > 2 else 260
pv = d["research_plan"]["point_values"]
print("point_values keys:", list(pv.keys()))
for k in pv:
    if k != "cells":
        print(k, "=", json.dumps(pv[k], ensure_ascii=False)[:maxlen])
cells = pv.get("cells", [])
print("n cells", len(cells))
for i, c in enumerate(cells):
    print("--- cell", i, "keys:", list(c.keys()))
    for k, v in c.items():
        print("   ", k, "=", json.dumps(v, ensure_ascii=False)[:maxlen])
