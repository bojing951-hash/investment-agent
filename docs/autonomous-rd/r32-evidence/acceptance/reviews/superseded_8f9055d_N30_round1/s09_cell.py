#!/usr/bin/python3 -I
# usage: s09_cell.py <report.json> <metric_id> [dotted-subpath]
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
mid = sys.argv[2]
sub = sys.argv[3] if len(sys.argv) > 3 else None
pv = d["research_plan"]["point_values"]
for c in pv["cells"]:
    if c["metric_id"] == mid:
        o = c
        if sub:
            for p in sub.split("."):
                o = o[int(p)] if isinstance(o, list) else o[p]
        print(json.dumps(o, ensure_ascii=False, indent=1))
