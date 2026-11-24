#!/usr/bin/env python3
"""Probe engine faces needed for cross-checking (read-only): S6_analog top list + dispersion,
S4_history ex-post/sync/known-then faces for the three analog months, S5_compare, S3_changes.

usage: python3 -I probe5.py <report.json> <out.txt>
"""
import json
import sys

rep_path, out_path = sys.argv[1:3]
rep = json.load(open(rep_path, "r", encoding="utf-8"))
out = open(out_path, "w", encoding="utf-8")


def w(s=""):
    out.write(s + "\n")


def pj(obj, indent=1, limit=None):
    s = json.dumps(obj, ensure_ascii=False, indent=indent)
    if limit:
        s = s[:limit]
    w(s)


steps = {}
for st in rep["steps"]:
    name = st.get("name") or st.get("step")
    steps[name] = st

w("=== step names ===")
w(" ".join(f"{i}:{(st.get('name') or st.get('step'))}" for i, st in enumerate(rep["steps"])))

s6 = steps.get("S6_analog")
env = s6.get("envelope") or {}
data = env.get("data") or {}
w("\n=== S6_analog data keys ===")
w(str(list(data.keys())))
for k in ["anchor_month", "feature_window_months", "weights", "feature_set", "normalization", "sort_basis",
          "research_mode_gate", "disclosure", "features_dropped_at_anchor", "dispersion", "state_vector"]:
    w(f"--- {k} ---")
    pj(data.get(k), 1, 6000)
w("--- candidates (count + first 3) ---")
cands = data.get("candidates")
if isinstance(cands, dict):
    w(f"candidates is dict keys={list(cands.keys())[:10]}")
    for k in list(cands.keys())[:3]:
        w(f"[{k}]")
        pj(cands[k], 1, 2500)
    vals = list(cands.values())
else:
    vals = cands or []
    w(f"n={len(vals)}")
    for c in vals[:3]:
        pj(c, 1, 2500)
w("--- top ---")
for t in data.get("top") or []:
    pj(t, 1, 9000)

for name in ["S5_compare", "S3_changes"]:
    st = steps.get(name)
    if not st:
        w(f"{name}: missing")
        continue
    env = st.get("envelope") or {}
    w(f"\n=== {name} data keys ===")
    d = env.get("data") or {}
    w(str(list(d.keys())))
    pj(d, 1, 14000)

hist = [n for n in steps if n and n.startswith("S4_history")]
w("\n=== S4_history steps ===")
w(" ".join(hist))
for name in hist:
    st = steps[name]
    env = st.get("envelope") or {}
    d = env.get("data") or {}
    w(f"--- {name} keys={list(d.keys())[:20]}")
    pj(d, 1, 3000)
out.close()
print("written", out_path)
