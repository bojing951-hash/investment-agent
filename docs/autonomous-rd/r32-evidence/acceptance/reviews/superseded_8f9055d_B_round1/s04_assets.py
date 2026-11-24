"""Asset windows, BEI extrema, USDJPY percentile, Brent windows — from frozen snapshot."""
import json, sys, bisect
snap = sys.argv[1]
with open(snap) as f: s = json.load(f)
ss = s["series_store"]
def load(m):
    return dict(zip(ss[m]["dates"], ss[m]["values"]))
def win(m, a, b):
    se = load(m)
    if a not in se or b not in se or se[a] is None or se[b] is None:
        return f"{m} {a}->{b}: endpoint missing (a={a in se}, b={b in se})"
    return f"{m} {a}->{b}: {se[a]} -> {se[b]}  chg={(se[b]/se[a]-1)*100:+.2f}%  abs={se[b]-se[a]:+.4f}"

print("== asset 1-month windows (engine rows) ==")
for m, a, b in [("SPX","2026-10-23","2026-11-23"),("NIKKEI225","2026-10-23","2026-11-20"),("GOLD_F","2026-10-23","2026-11-23"),("DXY","2026-10-23","2026-11-23"),("VIX","2026-10-23","2026-11-23"),("UST_10Y","2026-10-23","2026-11-19"),("SHCOMP","2026-10-23","2026-11-23"),("DAX","2026-10-23","2026-11-23")]:
    print("  ", win(m,a,b))
print("== same-day close windows ==")
for m, a, b in [("SPX","2026-10-23","2026-11-20"),("VIX","2026-10-23","2026-11-20"),("SPX","2026-08-19","2026-11-20"),("VIX","2026-08-19","2026-11-20"),("TIPS_10Y","2026-08-19","2026-11-19")]:
    print("  ", win(m,a,b))
print("== common trading day window SPX 2026-10-23 -> 2026-11-19 ==")
print("  ", win("SPX","2026-10-23","2026-11-19"))
print("== BRENT_F ==")
for m, a, b in [("BRENT_F","2026-08-19","2026-11-23"),("BRENT_F","2026-10-23","2026-11-23"),("BRENT_F","2025-11-19","2026-11-23"),("BRENT_F","2026-10-20","2026-11-19")]:
    print("  ", win(m,a,b))
se = load("BRENT_F"); ks = sorted(k for k in se if se[k] is not None)
print("   BRENT last obs:", ks[-1], se[ks[-1]], " last<=2025-11-23:", last := max(k for k in ks if k <= "2025-11-23"), se[last])
print("== USDJPY ==")
se = load("USDJPY"); ks = sorted(k for k in se if se[k] is not None)
print("   last:", ks[-1], se[ks[-1]], " n=", len(ks))
w = [se[k] for k in ks if "2025-11-23" <= k <= "2026-11-23"]
import statistics
cur = se[ks[-1]]
below = sum(1 for v in w if v < cur); eq = sum(1 for v in w if v == cur)
print(f"   12m window n={len(w)} min={min(w)} max={max(w)} cur={cur} pct(<cur)={below/len(w)*100:.1f}  pct(le)={(below+eq)/len(w)*100:.1f}")
# percentile rank definitions
def pct_rank_inc(vals, x):
    # numpy default 'linear' interpolation
    sv = sorted(vals); n = len(sv)
    import math
    rank = (n-1)*0
    # find fractional position
    j = bisect.bisect_left(sv, x)
    if j < n and sv[j] == x:
        return j/(n-1)*100
    return (j-0.5)/n*100
print(f"   pct rank (linear) = {pct_rank_inc(w, cur):.1f}")
print(f"   pct rank (count<=) = {sum(1 for v in w if v<=cur)/len(w)*100:.1f}")
# strict window exclusive of start
w2 = [se[k] for k in ks if "2025-11-24" <= k <= "2026-11-23"]
print(f"   excl-start n={len(w2)} pct(<)={sum(1 for v in w2 if v<cur)/len(w2)*100:.1f} pct_rank lin={pct_rank_inc(w2,cur):.1f}")
print("== BEI_10Y extrema ==")
se = load("BEI_10Y"); ks = sorted(k for k in se if se[k] is not None)
seg = [(k, se[k]) for k in ks if "2026-02-20" <= k <= "2026-05-04"]
mn = min(v for _, v in seg); mx = max(v for _, v in seg)
print("   seg 2026-02-20..2026-05-04: min", mn, [k for k,v in seg if v==mn], " max", mx, [k for k,v in seg if v==mx])
y26 = [(k, se[k]) for k in ks if "2026-01-01" <= k <= "2026-11-20"]
mx26 = max(v for _, v in y26)
print("   2026 max", mx26, [k for k,v in y26 if v==mx26])
w12 = [(k, se[k]) for k in ks if "2025-11-20" <= k <= "2026-11-20"]
mn12 = min(v for _, v in w12)
print("   12m(2025-11-20..2026-11-20) min", mn12, [k for k,v in w12 if v==mn12])
w12b = [(k, se[k]) for k in ks if "2025-11-23" <= k <= "2026-11-20"]
mn12b = min(v for _, v in w12b)
print("   12m(2025-11-23..2026-11-20) min", mn12b, [k for k,v in w12b if v==mn12b])
print("   all-2026 min", min(v for _,v in y26), [k for k,v in y26 if v==min(vv for _,vv in y26)])
print("== last obs of daily assets ==")
for m in ["SPX","NIKKEI225","VIX","DXY","GOLD_F","BRENT_F","USDJPY","DAX","SHCOMP","EURUSD","TIPS_10Y","UST_10Y","BEI_10Y","NDX","RUT","CAC40","HSI","SILVER_F","USDCNY"]:
    se = load(m); ks = sorted(k for k in se if se[k] is not None)
    print(f"   {m}: last={ks[-1]} val={se[ks[-1]]}  prev={ks[-2]} {se[ks[-2]]}")
