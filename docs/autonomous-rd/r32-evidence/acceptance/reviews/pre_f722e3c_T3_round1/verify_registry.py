#!/usr/bin/env python3
"""Seat-owned read-only probe: prints registry entries and ECB fact rows / sources_status quoted in the
seat's PROSE/VERDICT, plus ECB non-Wednesday observation counts.
Usage: python3 -I verify_registry.py <metric_registry.json> <snapshot.json>
"""
import datetime as dt
import json
import sys

reg, snap = [json.load(open(p, "r", encoding="utf-8")) for p in sys.argv[1:3]]
print("registry top keys: %s" % sorted(reg.keys()))
metrics = reg.get("metrics", reg)
if isinstance(metrics, list):
    metrics = {m.get("metric_id") or m.get("id"): m for m in metrics}
for mid in ("ECB_MRO", "ECB_DFR", "JP_CPI_YOY", "JP_POLICY_RATE", "JP_CPI_TOKYO_YOY"):
    m = metrics.get(mid)
    if m is None:
        print("## %s: NOT IN REGISTRY" % mid)
        continue
    print("## %s keys: %s" % (mid, sorted(m.keys())))
    for k, v in m.items():
        s = json.dumps(v, ensure_ascii=False)
        if any(t in s for t in ("lag", "lag_days", "决议", "拼接", "发布", "/release", "publish", "decision", "calc", "fresh", "天")):
            print("   %s = %s" % (k, s[:420]))
print("## sources_status.ea")
print(json.dumps(snap.get("sources_status", {}).get("ea"), ensure_ascii=False)[:600])
print("## facts ECB")
for f in snap["facts"]:
    if str(f.get("metric_id", "")).startswith("ECB"):
        print(json.dumps({k: f.get(k) for k in ("fact_id", "metric_id", "value", "observation_date", "quality_status", "issue", "issues", "release_date", "publication_date")}, ensure_ascii=False)[:700])
store = snap["series_store"]
for sid in ("ECB_MRO", "ECB_DFR"):
    s = store[sid]
    nw = [(d, v) for d, v in zip(s["dates"], s["values"]) if dt.date.fromisoformat(d).strftime("%a") != "Wed"]
    print("## %s n=%d non-Wed=%d first=%s last_nonwed=%s last=%s" % (sid, len(s["dates"]), len(nw), s["dates"][0], nw[-1][0] if nw else None, s["dates"][-1]))
