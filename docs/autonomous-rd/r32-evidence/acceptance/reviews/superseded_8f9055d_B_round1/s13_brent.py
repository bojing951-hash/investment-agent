import json, sys, statistics
snap = sys.argv[1]
with open(snap) as f: s = json.load(f)
ss = s["series_store"]
def load(m): return dict(zip(ss[m]["dates"], ss[m]["values"]))
for m in ["BRENT_F","WTI_F"]:
    se = {k:v for k,v in load(m).items() if v is not None}
    mon = {}
    for k, v in se.items():
        mon.setdefault(k[:7], []).append(v)
    print(f"## {m} monthly averages (partial for current month)")
    for ym in ["2025-07","2025-08","2025-09","2025-10","2025-11","2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09","2026-10","2026-11"]:
        if ym in mon:
            v = mon[ym]
            print(f"   {ym}: n={len(v)} avg={statistics.mean(v):.2f} min={min(v):.2f} max={max(v):.2f}")
    # path
    ks = sorted(se)
    pts = [k for k in ks if k >= "2026-07-01"]
    # weekly samples
    print("   path (every ~10 obs):")
    for k in pts[::10] + [pts[-1]]:
        print(f"      {k}: {se[k]}")
    print("   max in 2026-07-01..2026-11-23:", max((se[k],k) for k in pts), " min:", min((se[k],k) for k in pts))
    print("   max in Aug19..Nov23 window:", max((se[k],k) for k in pts if k>="2026-08-19"))
    # average of Oct 1..23 vs Jul avg
    o = [se[k] for k in ks if "2026-10-01"<=k<="2026-10-23"]
    print(f"   Oct 1..23 avg: {statistics.mean(o):.2f}")
