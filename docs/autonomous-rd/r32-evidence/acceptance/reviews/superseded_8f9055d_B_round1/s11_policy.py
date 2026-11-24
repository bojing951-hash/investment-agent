import json, sys
snap = sys.argv[1]
with open(snap) as f: s = json.load(f)
ss = s["series_store"]
def load(m):
    return dict(zip(ss[m]["dates"], ss[m]["values"]))
for m in ["DFEDTARU","DFEDTARL","ECB_DFR","ECB_MRO","DFF"]:
    se = load(m); ks = sorted(k for k in se if se[k] is not None)
    print(f"## {m}: n={len(ks)} first={ks[0]} last={ks[-1]} lastval={se[ks[-1]]}")
    prev = None
    for k in ks:
        if k < "2025-11-01": 
            prev = se[k]; continue
        if prev is not None and se[k] != prev:
            print(f"   change {k}: {prev} -> {se[k]}")
        prev = se[k]
    # show window around 2026-09
    for k in ks:
        if "2026-09-14" <= k <= "2026-09-20":
            print(f"     {k}: {se[k]}")
# days computations
import datetime as dt
def d(a,b): return (dt.date.fromisoformat(b)-dt.date.fromisoformat(a)).days
print("--- days")
print("effective 2026-09-24 -> 2026-11-23:", d("2026-09-24","2026-11-23"))
print("decision 2026-09-18 -> 2026-11-23:", d("2026-09-18","2026-11-23"))
print("maintain 2026-10-30 -> 2026-11-23:", d("2026-10-30","2026-11-23"))
print("CORE_PCE 2026-09-01 -> 2026-11-23:", d("2026-09-01","2026-11-23"), " ratio/60=", d("2026-09-01","2026-11-23")/60)
print("US_REAL_GDP 2026-07-01 -> 2026-11-23:", d("2026-07-01","2026-11-23"), " ratio/120=", d("2026-07-01","2026-11-23")/120)
print("EA_HICP 2026-10-01 -> 2026-11-23:", d("2026-10-01","2026-11-23"))
print("JP_POLICY_RATE 2026-10-01 -> 2026-11-23:", d("2026-10-01","2026-11-23"))
print("CPI 2026-10-01 -> 2026-11-23:", d("2026-10-01","2026-11-23"))
print("UNEMP 2026-10-01 -> 2026-11-23:", d("2026-10-01","2026-11-23"))
print("INDPRO 2026-10-01 -> 2026-11-23:", d("2026-10-01","2026-11-23"))
print("calendar days 2026-10-20..2026-11-19:", d("2026-10-20","2026-11-19"), " 2025-11-19..2026-11-19:", d("2025-11-19","2026-11-19"), " 2026-08-19..2026-11-19:", d("2026-08-19","2026-11-19"))
print("weekday 2026-09-18:", dt.date(2026,9,18).strftime("%A"), " 2026-09-24:", dt.date(2026,9,24).strftime("%A"), " 2026-10-30:", dt.date(2026,10,30).strftime("%A"))
# Sept 24 position: days remaining in Sept after effective
print("Sept days on/before 09-24:", 24, "after:", 30-24)
