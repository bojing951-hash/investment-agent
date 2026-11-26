import json, sys
reg = sys.argv[1]; snap = sys.argv[2]
with open(reg) as f: r = json.load(f)
with open(snap) as f: s = json.load(f)
print("registry version:", r["version"])
print("field_semantics:", json.dumps(r["field_semantics"], ensure_ascii=False)[:1500])
mets = r["metrics"]
print("n metrics:", len(mets), " sample keys:", list(mets[0].keys()))
want = ["US_REAL_GDP","UNEMPLOYMENT","INDPRO","CPI","CORE_CPI","CORE_PCE","EA_REAL_GDP_YOY","EA_HICP_YOY","JP_POLICY_RATE","JP_POLICY_TARGET","JP_CPI_TOKYO_YOY","JP_REAL_GDP_YOY","DFEDTARU","DFEDTARL","DFF","ECB_DFR","ECB_MRO","BEI_10Y","TIPS_10Y","UST_10Y","SPX","VIX","BRENT_F","USDJPY","NIKKEI225","GOLD_F","DXY","BUND_10Y","CN_OMO_7D","CN_POLICY_OVERNIGHT"]
byid = {m.get("metric_id"): m for m in mets}
for w in want:
    m = byid.get(w)
    if m is None:
        print(f"## {w}: NOT IN REGISTRY"); continue
    keep = {k: v for k, v in m.items() if k in ("metric_id","display_name","economy","dimension","frequency","criticality","max_calendar_lag_days","release_rule","release_lag_days","vintage_family","vintage_semantics","revised","collector","unit","policy_face","notes","release_rules","max_lag_days","source")}
    s_ = json.dumps(keep, ensure_ascii=False)
    print(f"## {w}: {s_[:700]}")
ids = sorted(byid)
print("JP economy metrics:", [i for i in ids if (byid[i].get("economy")=="JP")])
print("all ids:", ids)
# in snapshot but not registry; in registry but not snapshot
ss = s["series_store"]
print("registry ids not in series_store:", [i for i in ids if i not in ss])
print("series_store ids not in registry:", sorted(k for k in ss if k not in byid))
