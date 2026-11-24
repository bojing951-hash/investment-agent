import json, sys
reg = sys.argv[1]
with open(reg) as f: r = json.load(f)
byid = {m.get("metric_id"): m for m in r["metrics"]}
for w in ["US_REAL_GDP","UNEMPLOYMENT","INDPRO","CPI","CORE_CPI","CORE_PCE","EA_REAL_GDP_YOY","EA_HICP_YOY","JP_POLICY_RATE","JGB10Y","DFEDTARU","ECB_DFR","BUND_10Y","JP_CPI_YOY"]:
    m = byid[w]
    print(f"## {w}")
    print("   ", json.dumps({k: m[k] for k in m if k not in ("display_name",)}, ensure_ascii=False)[:1400])
print("== notes ==")
for n in r["notes"]:
    print(" -", n[:400])
