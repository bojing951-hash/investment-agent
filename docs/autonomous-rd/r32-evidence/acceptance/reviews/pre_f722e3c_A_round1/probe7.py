#!/usr/bin/env python3
"""Probe registry entries by metric_id + report.json run/semantic_review/layers/evidence_index (read-only).

usage: python3 -I probe7.py <metric_registry.json> <report.json> <snapshot.json> <out.txt>
"""
import json
import sys

reg_p, rep_p, snap_p, out_p = sys.argv[1:5]
out = open(out_p, "w", encoding="utf-8")


def w(s=""):
    out.write(s + "\n")


def pj(obj, indent=1, limit=3000):
    w(json.dumps(obj, ensure_ascii=False, indent=indent)[:limit])


reg = json.load(open(reg_p, encoding="utf-8"))
mets = reg["metrics"]
ids = [m.get("metric_id") for m in mets]
w("=== registry ids (%d) ===" % len(ids))
w(" ".join(str(i) for i in ids))
w("--- registry notes ---")
pj(reg.get("notes"), 1, 4000)
for want in ("JP_POLICY_TARGET", "JP_POLICY_RATE", "CN_POLICY_OVERNIGHT", "CN_OMO_7D", "JP_CPI_TOKYO_YOY",
             "EA_HICP_YOY", "US_REAL_GDP", "EA_REAL_GDP_YOY", "JP_REAL_GDP_YOY", "HY_OAS", "BEI_10Y", "DAX"):
    hit = [m for m in mets if m.get("metric_id") == want]
    w(f"--- registry {want}: {'FOUND' if hit else 'ABSENT'}")
    if hit:
        m = hit[0]
        pj({k: m.get(k) for k in ("metric_id", "display_name", "frequency", "unit", "criticality", "status",
                                  "calc", "release_date_available", "freshness", "economy", "source")}, 1, 2500)

snap = json.load(open(snap_p, encoding="utf-8"))
w("\n=== snapshot top keys ===")
w(str(list(snap.keys())))
for k in snap:
    v = snap[k]
    if isinstance(v, (dict, list)):
        w(f"{k}: {type(v).__name__} len={len(v)}")
    else:
        w(f"{k}: {str(v)[:300]}")
ss = snap["series_store"]
w("series_store n=%d" % len(ss))
w("JP_POLICY_TARGET in series_store: %s" % ("JP_POLICY_TARGET" in ss))
w("CN_POLICY_OVERNIGHT in series_store: %s" % ("CN_POLICY_OVERNIGHT" in ss))
t = ss.get("JP_CPI_TOKYO_YOY")
if t:
    w("JP_CPI_TOKYO_YOY first=%s last=%s n=%d" % (t["dates"][0], t["dates"][-1], len(t["dates"])))
# max obs date per series
mx = {}
for sid, s in ss.items():
    ds = [d for d, v in zip(s["dates"], s["values"]) if v is not None and v == v]
    if ds:
        mx[sid] = max(ds)
over = {k: v for k, v in mx.items() if v > "2026-11-23"}
w("series with max obs date > 2026-11-23: " + json.dumps(over, ensure_ascii=False))
w("series with max obs date == 2026-11-23: " + " ".join(sorted(k for k, v in mx.items() if v == "2026-11-23")))
w("series with max obs date == 2026-11-20: " + " ".join(sorted(k for k, v in mx.items() if v == "2026-11-20")))
w("series with max obs date == 2026-11-19: " + " ".join(sorted(k for k, v in mx.items() if v == "2026-11-19")))
w("series with max obs date < 2026-11-19: " + " ".join(f"{k}@{v}" for k, v in sorted(mx.items()) if v < "2026-11-19"))

rep = json.load(open(rep_p, encoding="utf-8"))
w("\n=== report.run ===")
pj(rep.get("run"), 1, 3000)
w("=== report.semantic_review ===")
pj(rep.get("semantic_review"), 1, 3000)
w("=== report.layers keys ===")
pj({k: (list(v.keys())[:15] if isinstance(v, dict) else type(v).__name__) for k, v in rep["layers"].items()}, 1, 2000)
w("=== report.notes ===")
pj(rep.get("notes"), 1, 1500)
w("=== evidence_index sample ===")
pj(rep["evidence_index"][:3], 1, 3000)
w("=== steps (step, ok, executed) ===")
w(" ".join(f"{i}:{st.get('step')}|{st.get('ok')}|{st.get('executed')}" for i, st in enumerate(rep["steps"])))
w("=== research_plan keys ===")
pj(list(rep["research_plan"].keys()), 1, 2000)
out.close()
print("written", out_p)
