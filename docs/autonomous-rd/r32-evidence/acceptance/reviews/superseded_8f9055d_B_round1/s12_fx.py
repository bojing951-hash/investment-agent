import json, sys
snap = sys.argv[1]
with open(snap) as f: s = json.load(f)
ss = s["series_store"]
def load(m): return dict(zip(ss[m]["dates"], ss[m]["values"]))
def at(m, d):
    se = load(m)
    if d in se: return se[d]
    ks = [k for k in se if k <= d and se[k] is not None]
    return (ks[-1], se[ks[-1]]) if ks else None
def chg(m, a, b):
    se = load(m)
    if a not in se or b not in se: return None
    return f"{se[a]} -> {se[b]}  {(se[b]/se[a]-1)*100:+.2f}%"
for m in ["EURUSD","USDJPY","DXY","GOLD_F","SPX","NIKKEI225","BRENT_F","VIX","NDX","DAX","CAC40","TIPS_10Y","BEI_10Y","UST_10Y","UST_2Y","CURVE_2S10S","HY_OAS","IG_OAS"]:
    print(f"## {m}")
    for a, b in [("2026-10-23","2026-11-23"),("2026-08-19","2026-11-19"),("2026-07-23","2026-11-23"),("2025-11-19","2026-11-19")]:
        r = chg(m, a, b)
        if r: print(f"    {a}->{b}: {r}")
    for d in ["2026-08-19","2026-08-23","2026-10-20","2026-11-20"]:
        print(f"      @{d}: {at(m,d)}")
# EURUSD 12m range
se = load("EURUSD"); w = [(k,v) for k,v in se.items() if "2025-11-23"<=k<="2026-11-23" and v is not None]
vals = [v for _,v in w]
print("EURUSD 12m range:", min(vals), max(vals), "last:", w[-1])
se = load("USDJPY"); w = [(k,v) for k,v in se.items() if "2025-11-23"<=k<="2026-11-23" and v is not None]
vals = [v for _,v in w]
print("USDJPY 12m range:", min(vals), max(vals), "first:", w[0], "last:", w[-1])
