"""Independent YoY / MoM recompute for monthly & quarterly series directly from frozen snapshot series_store."""
import json, sys, math
snap = sys.argv[1]
with open(snap) as f: s = json.load(f)
ss = s["series_store"]
def series(m):
    d = ss[m]["dates"]; v = ss[m]["values"]
    out = {}
    for a, b in zip(d, v):
        out[a[:7]] = b
    return out
def shift(ym, k):
    y, mo = int(ym[:4]), int(ym[5:7])
    t = y*12 + (mo-1) + k
    return f"{t//12:04d}-{t%12+1:02d}"
def yoy(m, ym, k=12):
    se = series(m)
    base = shift(ym, -k)
    if ym not in se: return (None, "absent-cur")
    if base not in se: return (None, f"absent-base({base})")
    if se[ym] is None or se[base] is None or se[base] == 0: return (None, "null")
    return ((se[ym]/se[base]-1)*100.0, f"base={base}:{se[base]}")
def pct(m, a, b):
    se = series(m)
    if a not in se or b not in se: return None
    return (se[b]/se[a]-1)*100.0

print("=== CPI (level) ===")
se = series("CPI")
for ym in ["2026-02","2026-05","2026-06","2026-07","2026-08","2026-09","2026-10"]:
    print(ym, se.get(ym), "yoy=", yoy("CPI", ym))
print("2025-10 present in CPI?", "2025-10" in se)
print("CPI level chg 2026-07->2026-10 %:", pct("CPI","2026-07","2026-10"))
print("=== CORE_CPI (level) ===")
se = series("CORE_CPI")
for ym in ["2026-02","2026-05","2026-06","2026-07","2026-08","2026-09","2026-10"]:
    print(ym, se.get(ym), "yoy=", yoy("CORE_CPI", ym))
print("2025-10 present in CORE_CPI?", "2025-10" in se)
print("CORE_CPI level chg 2026-07->2026-10 %:", pct("CORE_CPI","2026-07","2026-10"))
print("=== CORE_PCE (level) ===")
se = series("CORE_PCE")
for ym in ["2025-11","2026-02","2026-05","2026-06","2026-07","2026-08","2026-09"]:
    print(ym, se.get(ym), "yoy=", yoy("CORE_PCE", ym))
print("CORE_PCE level chg 2026-06->2026-09 %:", pct("CORE_PCE","2026-06","2026-09"))
print("=== UNEMPLOYMENT ===")
se = series("UNEMPLOYMENT")
for ym in ["2025-08","2025-09","2025-10","2025-11","2026-05","2026-06","2026-07","2026-08","2026-09","2026-10"]:
    print(ym, se.get(ym))
print("=== INDPRO ===")
se = series("INDPRO")
for ym in ["2025-07","2025-08","2025-09","2025-10","2025-11","2025-12","2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09","2026-10"]:
    print(ym, se.get(ym), "yoy=", yoy("INDPRO", ym), "mom=", (None if shift(ym,-1) not in se else round((se[ym]/se[shift(ym,-1)]-1)*100,4)))
print("INDPRO 2025-07->2025-10 %:", pct("INDPRO","2025-07","2025-10"))
print("INDPRO 2026-07->2026-10 %:", pct("INDPRO","2026-07","2026-10"))
print("=== US_REAL_GDP ===")
se = series("US_REAL_GDP")
for ym in ["2025-01","2025-04","2025-07","2025-10","2026-01","2026-04","2026-07"]:
    print(ym, se.get(ym), "yoy(4q)=", yoy("US_REAL_GDP", ym, 4))
print("=== EA_REAL_GDP_YOY ===")
se = series("EA_REAL_GDP_YOY")
for ym in ["2025-01","2025-04","2025-07","2025-10","2026-01","2026-04","2026-07"]:
    print(ym, se.get(ym))
print("=== EA_HICP_YOY ===")
se = series("EA_HICP_YOY")
for ym in ["2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09","2026-10"]:
    print(ym, se.get(ym))
y2026 = {k:v for k,v in se.items() if k.startswith("2026")}
print("2026 EA_HICP_YOY:", y2026, " max=", max(y2026.values()), " argmax=", max(y2026, key=y2026.get))
print("=== JP_POLICY_RATE ===")
se = series("JP_POLICY_RATE")
for ym in ["2025-07","2025-08","2025-09","2025-10","2025-11","2025-12","2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09","2026-10"]:
    print(ym, se.get(ym))
print("JP net 2025-11->2026-10 bp:", round((se["2026-10"]-se["2025-11"])*100,1), " 2025-12->2026-10 bp:", round((se["2026-10"]-se["2025-12"])*100,1))
print("=== CPI yoy vs EA_HICP_YOY: months where EA > US ===")
c = series("CPI"); e = series("EA_HICP_YOY")
rows = []
for ym in sorted(c):
    b = shift(ym,-12)
    if b in c and ym in e and c[b]:
        cy = (c[ym]/c[b]-1)*100
        rows.append((ym, round(cy,4), e[ym], e[ym] > cy))
# print from 2022-01 onward
for r in rows:
    if r[0] >= "2022-01":
        print(r)
# runs
runs = []; cur = None
for r in rows:
    flag = r[3]
    if cur is None or cur[0] != flag:
        cur = [flag, r[0], r[0], 1]; runs.append(cur)
    else:
        cur[2] = r[0]; cur[3] += 1
print("runs (EA>US?, from, to, n):")
for r in runs[-12:]:
    print(r)
print("last comparable month:", rows[-1])
