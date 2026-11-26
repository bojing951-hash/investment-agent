#!/usr/bin/python3
"""Peek at structures needed by the recompute script (read-only).
Usage: python3 -I s12_peek.py <snapshot.json> <report.json> <metric_registry.json> <release_calendar.json> <out.txt>
"""
import json
import sys


def short(v, n=300):
    s = json.dumps(v, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "..(%d)" % len(s)


def main():
    snap_path, rep_path, reg_path, cal_path, out_path = sys.argv[1:6]
    out = []
    with open(snap_path, "r", encoding="utf-8") as fh:
        snap = json.load(fh)
    out.append("=== snapshot top keys")
    for k, v in snap.items():
        if k == "series_store":
            out.append("series_store: %d series" % len(v))
            continue
        if isinstance(v, dict):
            out.append("%s {dict %d} keys=%s" % (k, len(v), sorted(v.keys())[:60]))
        elif isinstance(v, list):
            out.append("%s [list %d] first=%s" % (k, len(v), short(v[0]) if v else "-"))
        else:
            out.append("%s = %s" % (k, short(v, 200)))
    ga = snap.get("gate_a")
    if isinstance(ga, dict):
        out.append("=== gate_a")
        for k, v in ga.items():
            out.append("gate_a.%s = %s" % (k, short(v, 2500)))
    for k in snap.keys():
        if k in ("series_store", "gate_a"):
            continue
        v = snap[k]
        if isinstance(v, dict) and any(x in k.lower() for x in ("quality", "status", "collection", "summary", "meta")):
            out.append("=== %s" % k)
            items = list(v.items())[:6]
            for kk, vv in items:
                out.append("%s.%s = %s" % (k, kk, short(vv, 400)))
    out.append("=== series_store metric ids")
    out.append(", ".join(sorted(snap["series_store"].keys())))
    for pfx in ("JP", "CN", "EA", "ECB", "BUND", "DE"):
        ids = [m for m in sorted(snap["series_store"]) if m.startswith(pfx)]
        out.append("%s*: %s" % (pfx, ", ".join(ids)))
    with open(rep_path, "r", encoding="utf-8") as fh:
        rep = json.load(fh)
    out.append("=== evidence_index rows 0..2")
    for r in rep["evidence_index"][:3]:
        out.append(short(r, 900))
    out.append("evidence_index row keys: %s" % sorted(rep["evidence_index"][0].keys()))
    out.append("=== research_plan.dimension_gaps")
    out.append(short(rep["research_plan"]["dimension_gaps"], 1500))
    out.append("=== research_plan.policy_doc_facts")
    out.append(short(rep["research_plan"]["policy_doc_facts"], 1500))
    out.append("=== research_plan.policy_event_clusters")
    out.append(short(rep["research_plan"]["policy_event_clusters"], 2500))
    out.append("=== research_plan.us_rates_trio")
    out.append(short(rep["research_plan"]["us_rates_trio"], 2500))
    out.append("=== research_plan.asset_moves")
    out.append(short(rep["research_plan"]["asset_moves"], 3500))
    out.append("=== research_plan.turning_candidates")
    out.append(short(rep["research_plan"]["turning_candidates"], 3500))
    out.append("=== research_plan.point_anchors / as_of_declared / cutoff / ex_post_offsets / question_window")
    for k in ("point_anchors", "as_of_declared", "cutoff", "ex_post_offsets", "question_window", "anchor_semantics_note"):
        out.append("%s = %s" % (k, short(rep["research_plan"].get(k), 700)))
    with open(reg_path, "r", encoding="utf-8") as fh:
        reg = json.load(fh)
    out.append("=== registry top keys: %s" % (sorted(reg.keys()) if isinstance(reg, dict) else type(reg).__name__))
    if isinstance(reg, dict):
        for k, v in reg.items():
            if isinstance(v, dict):
                out.append("reg.%s {dict %d} sample keys=%s" % (k, len(v), sorted(v.keys())[:12]))
                jp = [x for x in v if "JP" in x]
                out.append("   JP-like keys in %s: %s" % (k, jp[:60]))
            elif isinstance(v, list):
                out.append("reg.%s [list %d] first=%s" % (k, len(v), short(v[0], 400) if v else "-"))
            else:
                out.append("reg.%s = %s" % (k, short(v, 200)))
    with open(cal_path, "r", encoding="utf-8") as fh:
        cal = json.load(fh)
    out.append("=== calendar top keys: %s" % (sorted(cal.keys()) if isinstance(cal, dict) else type(cal).__name__))
    if isinstance(cal, dict):
        for k, v in cal.items():
            if isinstance(v, list):
                out.append("cal.%s [list %d]" % (k, len(v)))
                for e in v:
                    s = json.dumps(e, ensure_ascii=False)
                    if any(x in s for x in ("JP", "CN", "US", "FOMC", "BOJ", "LPR")):
                        out.append("   " + short(e, 500))
            else:
                out.append("cal.%s = %s" % (k, short(v, 300)))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("wrote", out_path, "lines", len(out))


if __name__ == "__main__":
    main()
