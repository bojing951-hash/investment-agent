import json, sys
snap = sys.argv[1]; rep = sys.argv[2]
with open(snap) as f: s = json.load(f)
facts = s["facts"]
print("n facts:", len(facts), " keys sample:", list(facts[0].keys()))
for fct in facts:
    if fct.get("metric_id") in ("SPX","VIX","GOLD_F","DXY","BRENT_F","USDJPY","NIKKEI225","DAX","EURUSD","BEI_10Y","TIPS_10Y","JP_POLICY_RATE","EA_HICP_YOY","CPI","CORE_PCE","US_REAL_GDP","EA_REAL_GDP_YOY"):
        print(json.dumps(fct, ensure_ascii=False)[:600])
ss = s["series_store"]
for m in ["EA_REAL_GDP_YOY","JP_REAL_GDP_YOY","JP_CPI_TOKYO_YOY","JP_CPI_YOY","CN_OMO_7D","CN_POLICY_OVERNIGHT","UMCSENT","US_REAL_GDP"]:
    d = ss[m]["dates"]; v = ss[m]["values"]
    nn = sum(1 for x in v if x is None)
    print(f"{m}: n={len(d)} nonnull={len(v)-nn} first={d[0]} last={d[-1]} lastval={v[-1]}")
print("reconciliation:", json.dumps(s["reconciliation"], ensure_ascii=False)[:2500])
with open(rep) as f: p = json.load(f)
# steps summary
for st in p["steps"]:
    name = st.get("step") or st.get("name")
    env = st.get("envelope") or {}
    print("STEP", name, "| keys:", list(st.keys())[:12])
