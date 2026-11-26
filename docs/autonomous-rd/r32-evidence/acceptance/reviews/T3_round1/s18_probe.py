# -*- coding: utf-8 -*-
"""Read-only probe 4: registry wording, BOJ calendar entries, series id inventory, VIX raw values, part findings."""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
s = importlib.util.spec_from_file_location("t3lib", os.path.join(HERE, "t3lib.py"))
lib = importlib.util.module_from_spec(s)
s.loader.exec_module(lib)
c = lib.build(sys.argv[1], sys.argv[2], sys.argv[3])
J = lambda x, n=900: json.dumps(x, ensure_ascii=False)[:n]
print("series ids:", sorted(lib.SS.keys()))
for m in ("JP_CPI_YOY", "EA_HICP_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_RATE", "ECB_MRO", "ECB_DFR", "UST_10Y"):
    e = c.REGM.get(m) or {}
    print("\n[%s] keys=%s" % (m, sorted(e.keys())))
    for k in ("name", "unit", "freq", "release_semantics", "freshness", "freshness_days", "quality_rule", "tier"):
        if k in e:
            print("   %s: %s" % (k, J(e[k], 520)))
for x in c.CENT:
    if "BOJ" in x["entry_id"]:
        print("\nCAL", J(x, 1100))
dr = c.rep["run"].get("data_requirements", {})
print("\ndata_requirements:", J({k: v for k, v in dr.items() if k != "items"}, 700))
print("items:", J([[x.get("metric_id"), x.get("tier"), x.get("outcome"), (x.get("window") or {}).get("kind") if isinstance(x.get("window"), dict) else x.get("window")] for x in dr.get("items", [])], 900))
V = dict(lib.series("VIX"))
days = ["2026-10-23", "2026-11-04", "2026-11-05", "2026-11-11", "2026-11-13", "2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19", "2026-11-20", "2026-11-23"]
print("\nVIX raw:", [(d, V.get(d)) for d in days])
p = lambda a, b: round((b - a) / a * 100, 4)
print("84.5 check raw:", p(V["2026-10-23"], V["2026-11-20"]), "| from display:", p(19.45, 35.89))
print("69.66 check raw:", p(V["2026-11-04"], V["2026-11-05"]), "| display:", p(16.61, 28.18))
print("37.93 check raw:", p(V["2026-11-11"], V["2026-11-05"]), "| display:", p(17.49, 28.18))
print("24.7 check raw:", p(V["2026-11-23"], V["2026-11-20"]), "| display:", p(27.01, 35.89))
for n in ("p1", "p2", "p3", "p4a", "p4b", "p5", "p6"):
    d = json.load(open(os.path.join(HERE, "_part_%s.json" % n), encoding="utf-8"))
    print("\n== %s rows=%d" % (n, len(d["rows"])))
    for k, v in d["F"].items():
        print("  F.%s = %s" % (k, J(v, 420)))
rt = json.load(open(os.path.join(HERE, "recompute_table.json"), encoding="utf-8"))
print("\nRT summary:", J(rt["summary"], 900))
print("row keys:", list(rt["rows"][0].keys()))
print("row0:", J(rt["rows"][0], 700))
