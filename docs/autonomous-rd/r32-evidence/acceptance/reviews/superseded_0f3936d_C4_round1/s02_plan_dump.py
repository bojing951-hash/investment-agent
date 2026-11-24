#!/usr/bin/python3
"""Dump research_plan.point_values / point_anchors / cutoff / as_of_declared (read-only).
Usage: python3 -I s02_plan_dump.py <report.json> <out.txt>
"""
import json
import sys


def main():
    rp_path, out_path = sys.argv[1], sys.argv[2]
    with open(rp_path, "r", encoding="utf-8") as fh:
        rep = json.load(fh)
    plan = rep["research_plan"]
    out = []
    out.append("cutoff: %s" % plan.get("cutoff"))
    out.append("point_anchors: " + json.dumps(plan.get("point_anchors"), ensure_ascii=False))
    out.append("as_of_declared: " + json.dumps(plan.get("as_of_declared"), ensure_ascii=False, indent=1))
    out.append("dimension_gaps: " + json.dumps(plan.get("dimension_gaps"), ensure_ascii=False, indent=1))
    out.append("metrics: " + json.dumps(plan.get("metrics"), ensure_ascii=False))
    out.append("context_metrics: " + json.dumps(plan.get("context_metrics"), ensure_ascii=False))
    out.append("regions: " + json.dumps(plan.get("regions"), ensure_ascii=False))
    pv = plan["point_values"]
    cells = pv["cells"]
    out.append("cells type=%s n=%s" % (type(cells).__name__, len(cells)))
    items = cells.items() if isinstance(cells, dict) else enumerate(cells)
    for k, c in items:
        out.append("---- cell %s" % k)
        out.append(json.dumps(c, ensure_ascii=False, indent=1))
    out.append("absent: " + json.dumps(pv.get("absent"), ensure_ascii=False, indent=1))
    out.append("run.evidence_gate: " + json.dumps(rep["run"].get("evidence_gate"), ensure_ascii=False, indent=1))
    out.append("run.data_requirements: " + json.dumps(rep["run"].get("data_requirements"), ensure_ascii=False, indent=1))
    out.append("notes: " + json.dumps(rep.get("notes"), ensure_ascii=False, indent=1))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("wrote", out_path, "lines", len(out))


if __name__ == "__main__":
    main()
