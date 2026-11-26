"""Daily series recompute: values at dates, common trading day windows, percent changes."""
import json, sys, datetime as dt
snap = sys.argv[1]
with open(snap) as f: s = json.load(f)
ss = s["series_store"]
def load(m):
    return dict(zip(ss[m]["dates"], ss[m]["values"]))
def at(m, d):
    se = load(m); return se.get(d)
def win(m, a, b):
    se = load(m)
    if a not in se or b not in se: return None
    return (se[b], se[a], (se[b]/se[a]-1)*100.0)
def last_on_or_before(m, d):
    se = load(m)
    ks = [k for k in se if k <= d and se[k] is not None]
    return (ks[-1], se[ks[-1]]) if ks else None

for m in ["UST_10Y","TIPS_10Y","BEI_10Y"]:
    se = load(m)
    ks = sorted(se)
    print(f"## {m}: n={len(ks)} first={ks[0]} last={ks[-1]}")
    for d in ["2025-11-19","2026-02-20","2026-02-27","2026-05-04","2026-05-29","2026-08-19","2026-10-20","2026-10-23","2026-11-19","2026-11-20"]:
        print(f"   {d}: {se.get(d)}")

# Common trading days
def common_days(metrics, a, b):
    sets = [set(k for k,v in load(m).items() if v is not None and a<=k<=b) for m in metrics]
    return sorted(set.intersection(*sets))
for (a,b) in [("2026-10-20","2026-11-19"),("2025-11-19","2026-11-19"),("2026-08-19","2026-11-19"),("2026-10-23","2026-11-19")]:
    print("== window", a, "->", b, "==")
    vals = {}
    for m in ["UST_10Y","TIPS_10Y","BEI_10Y"]:
        se = load(m)
        if a in se and b in se:
            chg = (se[b]-se[a])*100
            vals[m] = (se[a], se[b], chg)
            print(f"   {m}: {se[a]} -> {se[b]}  chg={chg:+.1f}bp")
        else:
            print(f"   {m}: endpoint missing (a in={a in se}, b in={b in se})")
    if len(vals)==3:
        n = vals["UST_10Y"][2]; r = vals["TIPS_10Y"][2]; be = vals["BEI_10Y"][2]
        print(f"   nominal={n:+.1f} real+bei={r+be:+.1f} residual={n-(r+be):+.1f}")
        # identity on levels at b
        print(f"   level identity at {b}: nominal {vals['UST_10Y'][1]} vs real+bei {vals['TIPS_10Y'][1]+vals['BEI_10Y'][1]:.4f}")
    cd = common_days(["UST_10Y","TIPS_10Y","BEI_10Y"], a, b)
    print("   common days n=", len(cd), " last few:", cd[-3:] if cd else None)
