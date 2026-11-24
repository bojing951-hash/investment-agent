#!/usr/bin/python3
"""Compact per-cell table of research_plan.point_values.cells + policy paths (read-only).
Usage: python3 -I s07_cells.py <report.json> <out.txt>
"""
import json
import sys


def main():
    rp_path, out_path = sys.argv[1], sys.argv[2]
    with open(rp_path, "r", encoding="utf-8") as fh:
        rep = json.load(fh)
    plan = rep["research_plan"]
    pv = plan["point_values"]
    cells = pv["cells"]
    out = []
    items = cells.items() if isinstance(cells, dict) else enumerate(cells)
    first = True
    for k, c in items:
        if first:
            out.append("cell keys: %s" % sorted(c.keys()))
            first = False
        out.append("---- %s" % k)
        for kk in sorted(c.keys()):
            v = c[kk]
            s = json.dumps(v, ensure_ascii=False)
            if len(s) > 1800:
                s = s[:1800] + "...<truncated>"
            out.append("   %s = %s" % (kk, s))
    out.append("absent: " + json.dumps(pv.get("absent"), ensure_ascii=False, indent=1))
    out.append("=== research_plan other keys: %s" % sorted(plan.keys()))
    for k in plan.keys():
        if k in ("point_values", "point_anchors", "as_of_declared", "dimension_gaps", "metrics", "context_metrics", "regions", "cutoff"):
            continue
        s = json.dumps(plan[k], ensure_ascii=False)
        out.append("plan[%s] = %s%s" % (k, s[:2500], "..." if len(s) > 2500 else ""))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("wrote", out_path, "lines", len(out))


if __name__ == "__main__":
    main()
