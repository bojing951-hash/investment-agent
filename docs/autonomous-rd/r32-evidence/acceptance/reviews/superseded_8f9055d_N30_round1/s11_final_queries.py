#!/usr/bin/python3 -I
# -*- coding: utf-8 -*-
"""Final read-only queries backing the issue list (Audit-R32 / N30 / Round-1 seat).

usage: /usr/bin/python3 -I s11_final_queries.py <snapshot.json> <report.json> <release_calendar.json> <metric_registry.json> <MAP_REPORT.md> <out.txt>
"""
import datetime as dt
import json
import re
import sys
from collections import Counter

snap = json.load(open(sys.argv[1], encoding="utf-8"))
rep = json.load(open(sys.argv[2], encoding="utf-8"))
cal = json.load(open(sys.argv[3], encoding="utf-8"))
reg = json.load(open(sys.argv[4], encoding="utf-8"))
maptxt = open(sys.argv[5], encoding="utf-8").read()
out = open(sys.argv[6], "w", encoding="utf-8")


def P(*a):
    out.write(" ".join(str(x) for x in a) + "\n")


SS = snap["series_store"]
# 1 ------------------------------------------------------------------ EA/JP government yield presence
pat = re.compile(r"JGB|BUND|BKT|GILT|OAT|BTP|JPY_?10|EUR_?10|DE_?10Y|JP_?10Y", re.I)
P("[1] series_store ids matching government-yield patterns:", sorted(k for k in SS if pat.search(k)))
mets = reg.get("metrics") or reg
items = list(mets.items()) if isinstance(mets, dict) else [((m.get("metric_id") or m.get("id")), m) for m in mets]
P("[1] registry ids matching government-yield patterns:", sorted(k for k, m in items if pat.search(str(k))))
P("[1] registry ids with economy JP/EA (display_name):")
for k, m in items:
    if m.get("economy") in ("JP", "EA"):
        P("     ", k, "|", m.get("display_name"), "| economy=", m.get("economy"), "| status=", m.get("status"), "| criticality=", m.get("criticality"))
ga = snap.get("gate_a") or {}
for k in ("noncore_missing", "noncore_degraded", "status", "note"):
    P("[1] gate_a." + k, "=", json.dumps(ga.get(k), ensure_ascii=False)[:600])
det = ga.get("noncore_missing_detail") or {}
for k in ("BUND_10Y", "BUND_2Y", "JP_CPI_TOKYO_YOY", "EA_REAL_GDP_YOY", "JP_REAL_GDP_YOY"):
    P("[1] gate_a.noncore_missing_detail." + k, "=", json.dumps(det.get(k), ensure_ascii=False)[:400])
P("[1] BUND_10Y/BUND_2Y in series_store:", ("BUND_10Y" in SS), ("BUND_2Y" in SS))

# 2 ------------------------------------------------------------------ JP_CPI_YOY local high
s = SS["JP_CPI_YOY"]
jp = {str(d)[:10]: v for d, v in zip(s["dates"], s["values"]) if v is not None}
P("[2] JP_CPI_YOY 2024-10..2025-03:", [(k, jp[k]) for k in sorted(jp) if "2024-10" <= k <= "2025-03-01"])
mx = max(jp.items(), key=lambda kv: kv[1])
P("[2] JP_CPI_YOY series max:", mx, "| first/last obs:", min(jp), max(jp), "| n=", len(jp))
P("[2] JP_CPI_YOY 2025-01..2025-12:", [(k, jp[k]) for k in sorted(jp) if "2025-01" <= k <= "2025-12-01"])

# 3 ------------------------------------------------------------------ calendar composition
entries = cal.get("entries") or []
P("[3] release_calendar version/updated:", cal.get("version"), cal.get("updated"), "| n_entries=", len(entries))
P("[3] entries by metric_id:", dict(Counter(str(e.get("metric_id")) for e in entries)))
for e in entries:
    P("     ", e.get("entry_id"), "|", e.get("metric_id"), "| basis=", e.get("basis"), "| kind=", e.get("kind") or e.get("entry_type"), "| obs=", e.get("obs_from") or e.get("observation_month"), "| decision=", e.get("decision_date"), "| effective=", e.get("effective_date"), "| pub=", e.get("published_at") or e.get("release_date"))
    if str(e.get("metric_id")) in ("JP_POLICY_TARGET", "EA_HICP_YOY"):
        P("          full:", json.dumps(e, ensure_ascii=False)[:900])

# 4 ------------------------------------------------------------------ JP_POLICY_RATE change points
s = SS["JP_POLICY_RATE"]
jpr = [(str(d)[:10], v) for d, v in zip(s["dates"], s["values"]) if v is not None]
pts = []
for i in range(1, len(jpr)):
    bp = (jpr[i][1] - jpr[i - 1][1]) * 100
    if bp and jpr[i][0] > "2025-11-01":
        pts.append((jpr[i][0], jpr[i - 1][1], jpr[i][1], round(bp, 1), int(round(bp))))
P("[4] JP_POLICY_RATE month-to-month changes after 2025-11 (date, from, to, bp, bp_rounded_int):")
for x in pts:
    P("     ", x)
P("[4] sum of bp (all points):", round(sum(x[3] for x in pts), 1), "| sum of int-bp non-zero points:", sum(x[4] for x in pts), "| n non-zero at int bp:", len([x for x in pts if x[4] != 0]))

# 5 ------------------------------------------------------------------ VIX daily changes in the month window
s = SS["VIX"]
v = [(str(d)[:10], v_) for d, v_ in zip(s["dates"], s["values"]) if v_ is not None and "2026-10-23" <= str(d)[:10] <= "2026-11-23"]
dpm = [(v[i][0], round((v[i][1] / v[i - 1][1] - 1) * 100, 2)) for i in range(1, len(v))]
P("[5] VIX daily % 2026-10-23..2026-11-23:", dpm)
P("[5] top-3 by size:", sorted(dpm, key=lambda x: -x[1])[:3])
P("[5] VIX trading days 2026-11-05 -> 2026-11-11:", [x[0] for x in v if "2026-11-05" < x[0] <= "2026-11-11"])

# 6 ------------------------------------------------------------------ engine faces for ECB cells
rp_ = rep.get("research_plan") or {}
for c in (rp_.get("point_values") or {}).get("cells", []):
    if c.get("metric_id") in ("ECB_MRO", "ECB_DFR"):
        P("[6] point cell", c.get("metric_id"), json.dumps(c.get("anchors"), ensure_ascii=False)[:700])
dr = (rep.get("run") or {}).get("data_requirements") or {}
P("[6] run.data_requirements outcome:", dr.get("outcome") or dr.get("status"), "| keys:", list(dr.keys())[:12])
for it in (dr.get("items") or dr.get("series") or dr.get("metrics") or []):
    if isinstance(it, dict) and str(it.get("metric_id")) in ("ECB_MRO", "ECB_DFR"):
        P("[6] data_requirements item:", json.dumps(it, ensure_ascii=False)[:900])
P("[6] dimension_gaps:", json.dumps(rp_.get("dimension_gaps"), ensure_ascii=False)[:700])
P("[6] research_plan.point_values summary keys:", list((rp_.get("point_values") or {}).keys()))

# 7 ------------------------------------------------------------------ MAP/FULL engine text (reader-side rendering)
for i, l in enumerate(maptxt.split("\n")):
    if any(k in l for k in ("覆盖", "缺数", "全为周三", "四地", "语义审查", "待裁", "degraded", "DEGRADED", "降级")):
        P("[7] MAP line", i + 1, ":", l.strip()[:420])

out.close()
print("written", sys.argv[6])
