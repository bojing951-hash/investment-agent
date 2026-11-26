#!/usr/bin/python3 -I
"""③/⑥ monthly yoy paths + region narrative checks.
usage: s11_monthly.py <snapshot> <judgment.json>"""
import sys
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import lib  # seat-owned

snap, jud = (lib.load_json(p) for p in sys.argv[1:3])
st = lib.Store(snap)
N = [0, 0]


def cmp(tag, mine, claim, nd=4, tol=0.0):
    N[0] += 1
    if isinstance(mine, (int, float)) and isinstance(claim, (int, float)):
        ok = abs(round(mine, nd) - round(claim, nd)) <= tol
    else:
        ok = mine == claim
    if not ok:
        N[1] += 1
    print("   %-46s mine=%-26s claim=%-26s %s" % (tag, mine, claim, "OK" if ok else "<<< MISMATCH"))
    return ok


def info(tag, mine):
    print("   %-46s mine=%-26s (info only, not counted)" % (tag, mine))


def yoy(mid, ym):
    v = st.at(mid, ym + "-01")
    b = st.at(mid, lib.shift_months(ym + "-01", -12))
    if v is None or b is None:
        return None
    return (v / b - 1.0) * 100.0


def yoy_path(mid, ym0, ym1):
    out = []
    ym = ym0
    while ym <= ym1:
        out.append((ym, yoy(mid, ym)))
        ym = lib.shift_months(ym + "-01", 1)[:7]
    return out


print("### US CPI yoy (derived, same-month base)")
p = yoy_path("CPI", "2025-08", "2026-10")
for ym, v in p:
    print("   %s %s" % (ym, None if v is None else round(v, 4)))
d = dict(p)
print("-- claims --")
cmp("CPI yoy 2026-02 = 2.434", round(d["2026-02"], 3), 2.434, nd=3)
cmp("CPI yoy 2026-05 = 4.1666 (peak 4.17)", round(d["2026-05"], 4), 4.1666, nd=4)
info("CPI yoy 2026-06", round(d["2026-06"], 2))
cmp("CPI yoy 2026-07 = 3.30", round(d["2026-07"], 2), 3.30, nd=2)
cmp("CPI yoy 2026-08 = 3.35", round(d["2026-08"], 2), 3.35, nd=2)
cmp("CPI yoy 2026-09 = 3.72", round(d["2026-09"], 2), 3.72, nd=2)
cmp("CPI yoy 2026-10 missing base", d["2026-10"], None)
cmp("CPI yoy 2026-04 = 3.78", round(d["2026-04"], 2), 3.78, nd=2)
vals = [v for ym, v in p if v is not None and ym >= "2025-11"]
cmp("peak of CPI yoy in window is 2026-05", max((v, ym) for ym, v in p if v is not None and ym >= "2025-11")[1], "2026-05")
cmp("low of CPI yoy is 2026-01", min((v, ym) for ym, v in p if v is not None and "2025-11" <= ym <= "2026-10")[1], "2026-01")
info("CPI yoy 2026-01 (low)", round(d["2026-01"], 3))
# after 2026-05 never above peak
after = [v for ym, v in p if v is not None and ym > "2026-05"]
cmp("all post-2026-05 CPI yoy < 4.1666", all(v < d["2026-05"] for v in after), True)

print("### US CORE_CPI yoy")
p = yoy_path("CORE_CPI", "2025-08", "2026-10")
d = dict(p)
for ym, v in p:
    print("   %s %s" % (ym, None if v is None else round(v, 4)))
cmp("CORE_CPI yoy 2026-02 = 2.47", round(d["2026-02"], 2), 2.47, nd=2)
cmp("CORE_CPI yoy 2026-05 = 2.82", round(d["2026-05"], 2), 2.82, nd=2)
cmp("CORE_CPI yoy 2026-05 = 2.8229", round(d["2026-05"], 4), 2.8229, nd=4)
cmp("CORE_CPI yoy 2026-08 = 2.4462", round(d["2026-08"], 4), 2.4462, nd=4)
cmp("CORE_CPI delta 05->08 = -0.3767 (rounded endpoints)", round(round(d["2026-08"], 4) - round(d["2026-05"], 4), 4), -0.3767, nd=4)
cmp("CORE_CPI delta 05->08 unrounded = -0.3768", round(d["2026-08"] - d["2026-05"], 4), -0.3768, nd=4)
cmp("CORE_CPI yoy 2026-07 = 2.47 (3m anchor)", round(d["2026-07"], 2), 2.47, nd=2)
cmp("CORE_CPI latest valid yoy 2026-09 = 2.57", round(d["2026-09"], 2), 2.57, nd=2)
cmp("CORE_CPI yoy 2025-09 = 3.02", round(d["2025-09"], 2), 3.02, nd=2)

print("### US CORE_PCE yoy")
p = yoy_path("CORE_PCE", "2025-07", "2026-09")
d = dict(p)
for ym, v in p:
    print("   %s %s" % (ym, None if v is None else round(v, 4)))
cmp("CORE_PCE yoy 2025-08 = 2.85", round(d["2025-08"], 2), 2.85, nd=2)
cmp("CORE_PCE yoy 2026-05 = 3.16 (peak)", round(d["2026-05"], 2), 3.16, nd=2)
cmp("CORE_PCE yoy 2026-06 = 3.04", round(d["2026-06"], 2), 3.04, nd=2)
cmp("CORE_PCE yoy 2026-07 = 3.00", round(d["2026-07"], 2), 3.00, nd=2)
info("CORE_PCE yoy 2026-08", round(d["2026-08"], 2))
cmp("CORE_PCE yoy 2026-09 = 3.12", round(d["2026-09"], 2), 3.12, nd=2)
pk = max((v, ym) for ym, v in p if v is not None and ym >= "2025-11")
cmp("CORE_PCE peak month in window", pk[1], "2026-05")
after = [v for ym, v in p if v is not None and ym > "2026-05"]
cmp("post-peak CORE_PCE never above 3.16", all(v < d["2026-05"] for v in after), True)

print("### US INDPRO yoy")
p = yoy_path("INDPRO", "2025-06", "2026-10")
d = dict(p)
for ym, v in p:
    print("   %s %s" % (ym, None if v is None else round(v, 4)))
cmp("INDPRO yoy 2025-11 = 1.7543", round(d["2025-11"], 4), 1.7543, nd=4)
cmp("INDPRO yoy 2026-02 = 0.7972", round(d["2026-02"], 4), 0.7972, nd=4)
cmp("INDPRO yoy 2026-03 = 0.69 (low)", round(d["2026-03"], 2), 0.69, nd=2)
lo = min((v, ym) for ym, v in p if v is not None and "2025-11" <= ym <= "2026-10")
cmp("INDPRO yoy low month in window", lo[1], "2026-03")
cmp("INDPRO halved: 0.7972/1.7543 < 0.5", d["2026-02"] / d["2025-11"] < 0.5, True)

print("### US GDP yoy by quarter")
for q in ["2025Q2", "2025Q3", "2025Q4", "2026Q1", "2026Q2", "2026Q3"]:
    obs = "%s-%02d-01" % (q[:4], 3 * int(q[5]) - 2)
    print("   %s level=%s yoy=%s" % (q, st.at("US_REAL_GDP", obs), round(yoy("US_REAL_GDP", obs[:7]), 3)))

print("### CN PMI (level, yoy, vs 50) 2025-11..2026-10")
above, flat, below = [], [], []
s = st.series("CN_PMI_MFG")
d = dict(s)
for (dt_, v) in s:
    if "2024-09" <= dt_[:7] <= "2026-10":
        b = st.at("CN_PMI_MFG", lib.shift_months(dt_, -12))
        print("   %s level=%s yoy=%s diff_pt=%s" % (dt_[:7], v, None if b is None else round((v / b - 1) * 100, 2), None if b is None else round(v - b, 2)))
for (dt_, v) in s:
    ym = dt_[:7]
    if "2025-11" <= ym <= "2026-10":
        (above if v > 50 else flat if v == 50 else below).append((ym, v))
print("   >50:", above)
print("   =50:", flat)
print("   <50:", below)
cmp("months >50 = [2025-12,2026-03,2026-04,2026-06,2026-09]", [x[0] for x in above], ["2025-12", "2026-03", "2026-04", "2026-06", "2026-09"])
cmp("values >50 = 50.1/50.4/50.3/50.3/50.1", [x[1] for x in above], [50.1, 50.4, 50.3, 50.3, 50.1])
cmp("2026-05 == 50.0", d.get("2026-05-01"), 50.0)
cmp("below-50 range = 49.0..49.8", (min(x[1] for x in below), max(x[1] for x in below)), (49.0, 49.8))
# window considered in the C1 statement: 'past 12 months (to 2026-11-23)' -- check 2025-11 too
print("   2025-11 level:", d.get("2025-11-01"))
cmp("PMI yoy 2025-10 = -2.2 (diff -1.1pt)", (round(yoy("CN_PMI_MFG", "2025-10"), 1), round(st.at("CN_PMI_MFG", "2025-10-01") - st.at("CN_PMI_MFG", "2024-10-01"), 1)), (-2.2, -1.1))
cmp("PMI yoy 2026-07 = -0.2 (diff -0.1pt)", (round(yoy("CN_PMI_MFG", "2026-07"), 1), round(st.at("CN_PMI_MFG", "2026-07-01") - st.at("CN_PMI_MFG", "2025-07-01"), 1)), (-0.2, -0.1))
cmp("PMI yoy 2026-10 = 0.6/0.61 (diff +0.3pt)", (round(yoy("CN_PMI_MFG", "2026-10"), 2), round(st.at("CN_PMI_MFG", "2026-10-01") - st.at("CN_PMI_MFG", "2025-10-01"), 1)), (0.61, 0.3))
cmp("PMI candidate 2026-02 yoy = -2.3904", round(yoy("CN_PMI_MFG", "2026-02"), 4), -2.3904, nd=4)
cmp("PMI candidate 2026-05 yoy = 1.0101", round(yoy("CN_PMI_MFG", "2026-05"), 4), 1.0101, nd=4)

for mid in ["CN_CPI_YOY", "CN_PPI_YOY", "EA_HICP_YOY", "JP_CPI_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_RATE"]:
    print("### %s (published yoy series) 2024-09..last" % mid)
    s = st.series(mid)
    print("   first=%s last=%s n=%d" % (s[0][0], s[-1][0], len(s)))
    for (dt_, v) in s:
        if dt_[:7] >= "2024-09":
            print("   %s %s" % (dt_[:7], v))

print("### claim checks CN")
info("CN_PPI monthly path 2025-11..2026-10", [pp0 for pp0 in []])
ppath = [(ym, pp0) for ym, pp0 in sorted(dict((d_[:7], v) for d_, v in st.series("CN_PPI_YOY")).items()) if "2025-11" <= ym <= "2026-10"]
info("CN_PPI path", ppath)
info("CN_PPI months with mom decline after low", [ym for i, (ym, v) in enumerate(ppath) if i > 0 and v < ppath[i - 1][1]])
pp = dict((d_[:7], v) for d_, v in st.series("CN_PPI_YOY"))
cc = dict((d_[:7], v) for d_, v in st.series("CN_CPI_YOY"))
cmp("CN_PPI 2025-11 low of window", min((v, ym) for ym, v in pp.items() if "2025-11" <= ym <= "2026-10")[1], "2025-11")
info("CN_PPI low value", min((v, ym) for ym, v in pp.items() if "2025-11" <= ym <= "2026-10")[0])
seq = [pp[ym] for ym in sorted(pp) if "2025-11" <= ym <= "2026-10"]
cmp("CN_PPI non-decreasing after low (连升)", all(seq[i] <= seq[i + 1] for i in range(len(seq) - 1)), True)
cmp("CN_PPI 2026-02 = -0.9", pp["2026-02"], -0.9)
cmp("CN_PPI 2026-05 = 3.9", pp["2026-05"], 3.9)
cmp("CN_PPI 2026-07 = 3.5", pp["2026-07"], 3.5)
cmp("CN_PPI 2026-10 = 5.7 (window max)", (pp["2026-10"], max(seq) == pp["2026-10"]), (5.7, True))
info("CN_CPI 2026-02..05 within 1.0..1.3", [cc[y] for y in ["2026-02", "2026-03", "2026-04", "2026-05"]])
cmp("CN_CPI 2026-02..05 all in [1.0,1.3]", all(1.0 <= cc[y] <= 1.3 for y in ["2026-02", "2026-03", "2026-04", "2026-05"]), True)
cmp("CN_CPI candidate 2026-01 0.2 -> 2026-04 1.2", (cc["2026-01"], cc["2026-04"]), (0.2, 1.2))
cmp("largest price swing among four (PPI -2.1 -> 5.7 = 7.8pp)", round(pp["2026-10"] - pp["2025-10"], 1), 7.8, nd=1)

print("### claim checks EA")
ea = dict((d_[:7], v) for d_, v in st.series("EA_HICP_YOY"))
cmp("EA HICP 2026-01 low = 1.7", ea["2026-01"], 1.7)
cmp("EA HICP 2026-02 = 1.9", ea["2026-02"], 1.9)
cmp("EA HICP 2026-04 = 3.0", ea["2026-04"], 3.0)
cmp("EA HICP 2026-05 = 3.2", ea["2026-05"], 3.2)
cmp("EA HICP 2026-06 = 2.8", ea["2026-06"], 2.8)
cmp("EA HICP 2026-07 = 2.9", ea["2026-07"], 2.9)
cmp("EA HICP 2026-08 = 3.2", ea["ea".replace("ea", "2026-08")] if False else ea["2026-08"], 3.2)
cmp("EA HICP 2026-10 = 4.0", ea["2026-10"], 4.0)
cmp("EA HICP increments 07,08,09,10 = +0.1,+0.3,+0.6,+0.2", tuple(round(ea[y] - ea[lib.shift_months(y + "-01", -1)[:7]], 1) for y in ["2026-07", "2026-08", "2026-09", "2026-10"]), (0.1, 0.3, 0.6, 0.2))
w = [v for ym, v in ea.items() if "2025-11" <= ym <= "2026-10"]
cmp("EA HICP 4.0 is window max (本轮最高)", max(w) == ea["2026-10"], True)
info("EA HICP all-series max (for context)", max(ea.values()))
cmp("EA HICP monotone up 2026-01..2026-05", all(ea[y] < ea[lib.shift_months(y + "-01", 1)[:7]] for y in ["2026-01", "2026-02", "2026-03", "2026-04"]), True)

print("### claim checks JP")
jp = dict((d_[:7], v) for d_, v in st.series("JP_CPI_YOY"))
cmp("JP CPI 2025-01 high = 4.03", jp["2025-01"], 4.03)
hi = max((v, ym) for ym, v in jp.items() if "2024-06" <= ym <= "2026-02")
cmp("JP CPI high month (2024-06..2026-02)", hi[1], "2025-01")
for y in ["2025-08", "2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]:
    print("   JP CPI %s %s (mom %s)" % (y, jp[y], round(jp[y] - jp[lib.shift_months(y + "-01", -1)[:7]], 2)))
cmp("JP CPI path 2025-11 2.9 / 12 2.13 / 2026-01 1.51 / 02 1.27", (jp["2025-11"], jp["2025-12"], jp["2026-01"], jp["2026-02"]), (2.9, 2.13, 1.51, 1.27))
cmp("JP CPI 2026-03 = 1.46, 2026-04 = 1.38", (jp["2026-03"], jp["2026-04"]), (1.46, 1.38))
cmp("JP CPI 2026-07 = 1.97, 2026-10 = 2.44", (jp["2026-07"], jp["2026-10"]), (1.97, 2.44))
cmp("JP CPI low month 2026-02", min((v, ym) for ym, v in jp.items() if "2025-11" <= ym <= "2026-10")[1], "2026-02")
up = all(jp[y] < jp[lib.shift_months(y + "-01", 1)[:7]] for y in ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09"])
cmp("JP CPI rising every month from 2026-05", up, True)
tk = dict((d_[:7], v) for d_, v in st.series("JP_CPI_TOKYO_YOY"))
cmp("Tokyo 2026-06 = 1.6, 2026-09 = 2.69, 2026-08 = 1.9, 2026-07 = 1.85, 2026-10 = 2.73", (tk["2026-06"], tk["2026-09"], tk["2026-08"], tk["2026-07"], tk["2026-10"]), (1.6, 2.69, 1.9, 1.85, 2.73))
info("Tokyo series first month", st.first_date("JP_CPI_TOKYO_YOY")[:7])

print("### latest consumer-price readings: EA 4.0 highest among four (latest obs month)")
print("   US CPI latest valid yoy 3.72@2026-09 (2026-10 n/a); JP 2.44; CN 0.7; EA 4.0")
cmp("EA 4.0 > US 3.72, JP 2.44, CN 0.7", ea["2026-10"] > max(3.72, jp["2026-10"], cc["2026-10"]), True)

print("=" * 100)
print("POINTS=%d MISMATCHES=%d" % (N[0], N[1]))
