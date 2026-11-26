#!/usr/bin/env python3
"""Probe S6_analog top entries compactly + search for coverage / aftermath faces (read-only).

usage: python3 -I probe10.py <report.json> <out.txt>
"""
import json
import sys

rep = json.load(open(sys.argv[1], encoding="utf-8"))
out = open(sys.argv[2], "w", encoding="utf-8")


def w(s=""):
    out.write(s + "\n")


def pj(obj, indent=1, limit=3000):
    w(json.dumps(obj, ensure_ascii=False, indent=indent)[:limit])


steps = {st.get("step"): st for st in rep["steps"]}
s6 = steps["S6_analog"]
env = s6.get("envelope") or {}
w("S6 envelope keys: " + str(list(env.keys())))
data = env.get("data") or {}
top = data.get("top") or []
w("top n=%d" % len(top))
w("top[0] keys: " + str(list(top[0].keys())))
for t in top:
    w("--- rank=%s month=%s distance=%s pct=%s n_missing=%s" % (
        t.get("rank"), t.get("candidate_month"), t.get("distance"), t.get("distance_percentile"), t.get("n_missing")))
    w("  dims: " + json.dumps({k: v.get("contribution_share") for k, v in (t.get("dims") or {}).items()}))
    w("  missing: " + json.dumps(t.get("missing_features"), ensure_ascii=False))
    for fk, fv in (t.get("features_detail") or {}).items():
        w("  feat %s gap=%s" % (fk, fv.get("gap")))
    for k in t.keys():
        if k not in ("rank", "candidate_month", "distance", "distance_percentile", "n_missing", "dims",
                     "features_detail", "missing_features", "cluster_members", "norm_wsum", "accounted_wsum",
                     "missing_wsum"):
            w("  extra key %s: %s" % (k, json.dumps(t[k], ensure_ascii=False)[:1500]))
    w("  cluster_members n=%d" % len(t.get("cluster_members") or []))
c = data.get("candidates")
if isinstance(c, dict):
    w("candidates summary: " + json.dumps({k: (v if not isinstance(v, (list, dict)) else "%s len=%d" % (type(v).__name__, len(v))) for k, v in c.items()}, ensure_ascii=False)[:3000])
for k in data.keys():
    if k not in ("anchor_month", "feature_window_months", "weights", "feature_set", "normalization", "sort_basis",
                 "research_mode_gate", "disclosure", "features_dropped_at_anchor", "dispersion", "state_vector",
                 "candidates", "top"):
        w("extra data key %s: %s" % (k, json.dumps(data[k], ensure_ascii=False)[:1500]))
for k in env.keys():
    if k != "data":
        w("env.%s: %s" % (k, json.dumps(env[k], ensure_ascii=False)[:800]))
w("gate_a (S6): " + json.dumps(env.get("gate_a"), ensure_ascii=False)[:1500])
w("warnings (S6): " + json.dumps(env.get("warnings"), ensure_ascii=False)[:1500])
# search for coverage-like text anywhere in S6 envelope
s = json.dumps(env, ensure_ascii=False)
for kw in ("覆盖", "coverage", "aftermath", "ex_post", "事后"):
    i = s.find(kw)
    w("kw %s at %d: %s" % (kw, i, s[max(0, i - 200):i + 400] if i >= 0 else "-"))
out.close()
print("written", sys.argv[2])
