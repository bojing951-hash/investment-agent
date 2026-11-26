#!/usr/bin/env python3
"""Probe snapshot gate/quality faces + research_plan gaps/point_values (read-only).

usage: python3 -I probe8.py <snapshot.json> <report.json> <out.txt>
"""
import json
import sys

snap_p, rep_p, out_p = sys.argv[1:4]
out = open(out_p, "w", encoding="utf-8")


def w(s=""):
    out.write(s + "\n")


def pj(obj, indent=1, limit=3000):
    w(json.dumps(obj, ensure_ascii=False, indent=indent)[:limit])


snap = json.load(open(snap_p, encoding="utf-8"))
w("=== snapshot.gate_a ===")
pj(snap.get("gate_a"), 1, 5000)
w("=== snapshot.quality ===")
pj(snap.get("quality"), 1, 3000)
w("=== snapshot.series_store_notes ===")
pj(snap.get("series_store_notes"), 1, 5000)
w("=== snapshot.notes ===")
pj(snap.get("notes"), 1, 2000)
w("=== snapshot.sources_status ===")
pj(snap.get("sources_status"), 1, 3000)
w("=== series_provenance ===")
pj(snap.get("series_provenance"), 1, 1500)
w("=== series_store_clean ===")
w(str(snap.get("series_store_clean"))[:2000])
w("=== facts sample (CN_CPI/CN_PPI/JP_POLICY) ===")
for f in snap.get("facts", []):
    s = json.dumps(f, ensure_ascii=False)
    if any(k in s for k in ("CN_CPI_YOY", "CN_PPI_YOY", "JP_POLICY", "UNEMPLOYMENT", "CORE_PCE")):
        w(s[:600])
w("=== facts key set ===")
ks = {}
for f in snap.get("facts", []):
    for k in f:
        ks[k] = ks.get(k, 0) + 1
w(str(ks))

rep = json.load(open(rep_p, encoding="utf-8"))
rp = rep["research_plan"]
w("\n=== research_plan.dimension_gaps ===")
pj(rp.get("dimension_gaps"), 1, 5000)
w("=== research_plan.point_anchors ===")
pj(rp.get("point_anchors"), 1, 1500)
w("=== research_plan.ex_post_offsets ===")
pj(rp.get("ex_post_offsets"), 1, 800)
w("=== research_plan.us_rates_trio ===")
pj(rp.get("us_rates_trio"), 1, 3000)
w("=== research_plan.asset_moves ===")
pj(rp.get("asset_moves"), 1, 5000)
w("=== research_plan.point_values (type/len) ===")
pv = rp.get("point_values")
w(type(pv).__name__ + " " + str(len(pv) if hasattr(pv, "__len__") else ""))
if isinstance(pv, dict):
    for k in list(pv.keys())[:3]:
        w(f"[{k}]")
        pj(pv[k], 1, 2500)
elif isinstance(pv, list):
    pj(pv[:4], 1, 4000)
w("=== research_plan.policy_event_clusters ===")
pj(rp.get("policy_event_clusters"), 1, 3000)
w("=== research_plan.turning_candidates ===")
pj(rp.get("turning_candidates"), 1, 5000)
w("=== research_plan.cross_face_consistency ===")
pj(rp.get("cross_face_consistency"), 1, 3000)
w("=== research_plan.anchor_semantics_note ===")
pj(rp.get("anchor_semantics_note"), 1, 1500)
w("=== research_plan.asof_discipline ===")
pj(rp.get("asof_discipline"), 1, 2500)
out.close()
print("written", out_p)
