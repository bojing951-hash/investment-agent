#!/usr/bin/env python3
"""Probe 11: engine faces needed by the recompute (compact) + z-definition test for CN_PMI (read-only).

usage: python3 -I probe11.py <snapshot.json> <report.json> <out.txt>
"""
import json
import sys

snap = json.load(open(sys.argv[1], encoding="utf-8"))
rep = json.load(open(sys.argv[2], encoding="utf-8"))
out = open(sys.argv[3], "w", encoding="utf-8")


def w(s=""):
    out.write(s + "\n")


def pj(obj, limit=2500, indent=None):
    w(json.dumps(obj, ensure_ascii=False, indent=indent)[:limit])


ss = snap["series_store"]
w("=== top-level snapshot keys ===")
w(str(list(snap.keys())))
w("research_as_of=%s timezone=%s target_date=%s snapshot_id=%s" % (
    snap.get("research_as_of"), snap.get("timezone"), snap.get("target_date"), snap.get("snapshot_id")))
w("=== gate_a (snapshot) ===")
pj(snap.get("gate_a"), 6000)
w("=== quality (snapshot) keys ===")
q = snap.get("quality")
w(type(q).__name__ + " " + (str(list(q.keys()))[:1500] if isinstance(q, dict) else str(q)[:500]))
if isinstance(q, dict):
    for k, v in q.items():
        s = json.dumps(v, ensure_ascii=False)
        w("  quality.%s: %s" % (k, s[:900]))

w("=== steps gate_a statuses ===")
from collections import Counter
cnt = Counter()
nonok = []
for st in rep["steps"]:
    env = st.get("envelope") or {}
    ga = env.get("gate_a")
    stat = ga.get("status") if isinstance(ga, dict) else ga
    cnt[str(stat)] += 1
    if str(stat) not in ("OK", "None"):
        nonok.append(st.get("step"))
w(str(dict(cnt)) + " n_steps=%d" % len(rep["steps"]))
w("non-OK steps: " + ",".join(nonok))
st0 = rep["steps"][0]
pj(st0.get("envelope", {}).get("gate_a"), 1500)

w("=== run block ===")
run = rep.get("run") or {}
for k, v in run.items():
    s = json.dumps(v, ensure_ascii=False)
    w("run.%s: %s" % (k, s[:700]))

rp = rep.get("research_plan") or {}
w("=== research_plan keys ===")
w(str(list(rp.keys())))
for k in ("cutoff", "point_anchors", "turning_candidates", "us_rates_trio", "asset_moves", "policy_event_clusters",
          "policy_doc_facts", "dimension_gaps", "ex_post_offsets"):
    w("--- research_plan.%s" % k)
    pj(rp.get(k), 5000)

aj = rep.get("agent_judgment") or {}
w("=== agent_judgment keys ===")
w(str(list(aj.keys())))
for k in aj:
    if k in ("contract_verification",):
        continue
    v = aj[k]
    if isinstance(v, (str, int, float, bool, type(None))):
        w("aj.%s = %s" % (k, str(v)[:600]))
    else:
        w("aj.%s: %s" % (k, json.dumps(v, ensure_ascii=False)[:400] + " …(len=%d)" % len(json.dumps(v, ensure_ascii=False))))

w("=== series presence ===")
for sid in sorted(ss.keys()):
    s = ss[sid]
    ds = [d for d, v in zip(s["dates"], s["values"]) if v is not None]
    w("%s n=%d first=%s last=%s" % (sid, len(ds), ds[0] if ds else None, ds[-1] if ds else None))

w("=== z-definition test CN_PMI_MFG ===")
import statistics
s = ss["CN_PMI_MFG"]
pts = [(d, v) for d, v in zip(s["dates"], s["values"]) if v is not None]
idx = {d[:7]: v for d, v in pts}
w("CN_PMI path 2025-01..2026-10: " + " ".join("%s=%s" % (k, idx.get(k)) for k in sorted(idx) if k >= "2025-01"))
for target in ("2026-02", "2026-05"):
    i = [j for j, (d, v) in enumerate(pts) if d[:7] == target][0]
    xs = [v for d, v in pts]
    up_to = xs[:i + 1]
    up_to_prev = xs[:i]
    res = {
        "expanding_ddof0": (xs[i] - statistics.fmean(up_to)) / statistics.pstdev(up_to),
        "expanding_ddof1": (xs[i] - statistics.fmean(up_to)) / statistics.stdev(up_to),
        "exp_prev_ddof0": (xs[i] - statistics.fmean(up_to_prev)) / statistics.pstdev(up_to_prev),
        "exp_prev_ddof1": (xs[i] - statistics.fmean(up_to_prev)) / statistics.stdev(up_to_prev),
        "full_ddof0": (xs[i] - statistics.fmean(xs)) / statistics.pstdev(xs),
        "full_ddof1": (xs[i] - statistics.fmean(xs)) / statistics.stdev(xs),
    }
    w("%s x=%s first=%s n_up=%d: %s" % (target, xs[i], pts[0], len(up_to), json.dumps({k: round(v, 4) for k, v in res.items()})))
w("=== S6 top: state_vector coverage / windows ===")
steps = {st.get("step"): st for st in rep["steps"]}
s6 = steps["S6_analog"]["envelope"]["data"]
pj(s6.get("state_vector"), 2500)
w("feature_window_months=%s anchor_month=%s sort_basis=%s" % (s6.get("feature_window_months"), s6.get("anchor_month"), s6.get("sort_basis")))
t0 = s6["top"][0]
pj(t0.get("aftermath"), 3000)
pj(t0.get("windows"), 800)
w("=== HY_OAS first obs / history months at 2025-03 and 2022-06 ===")
h = ss.get("HY_OAS")
if h:
    ds = [d for d, v in zip(h["dates"], h["values"]) if v is not None]
    w("HY_OAS n=%d first=%s last=%s; months<=2025-03: %d" % (len(ds), ds[0], ds[-1], len({d[:7] for d in ds if d <= "2025-03-31"})))
out.close()
print("written", sys.argv[3])
