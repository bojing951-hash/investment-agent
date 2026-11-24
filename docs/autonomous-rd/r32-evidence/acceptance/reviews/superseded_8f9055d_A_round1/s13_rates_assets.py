#!/usr/bin/python3 -I
"""⑤ three-rate decomposition, asset windows, daily co-movement.  usage: s13_rates_assets.py <snapshot>"""
import sys
import math
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import lib  # seat-owned

snap = lib.load_json(sys.argv[1])
st = lib.Store(snap)
N = [0, 0]
MIS = []


def cmp(tag, mine, claim, nd=2):
    N[0] += 1
    if isinstance(mine, (int, float)) and isinstance(claim, (int, float)):
        ok = abs(round(mine, nd) - round(claim, nd)) <= 1e-9
    else:
        ok = mine == claim
    if not ok:
        N[1] += 1
        MIS.append("%s mine=%s claim=%s" % (tag, mine, claim))
    print("   %-58s mine=%-26s claim=%-22s %s" % (tag, mine, claim, "OK" if ok else "<<< MISMATCH"))
    return ok


def lvl(mid, d):
    o = st.on_or_before(mid, d)
    return o


def chg_bp(mid, d0, d1):
    a = st.on_or_before(mid, d0)
    b = st.on_or_before(mid, d1)
    return (b[1] - a[1]) * 100.0, a, b


print("### C1 levels")
cmp("UST_10Y latest", st.on_or_before("UST_10Y", "2026-11-23"), ("2026-11-19", 5.04))
cmp("TIPS_10Y latest", st.on_or_before("TIPS_10Y", "2026-11-23"), ("2026-11-19", 2.88))
cmp("BEI_10Y latest", st.on_or_before("BEI_10Y", "2026-11-23"), ("2026-11-20", 2.15))
cmp("VIX latest", st.on_or_before("VIX", "2026-11-23"), ("2026-11-23", 27.01))
cmp("HY_OAS latest", st.on_or_before("HY_OAS", "2026-11-23"), ("2026-11-19", 3.52))
cmp("USDJPY latest (rounded 2dp)", tuple([st.on_or_before("USDJPY", "2026-11-23")[0]] + [round(st.on_or_before("USDJPY", "2026-11-23")[1], 2)]), ("2026-11-23", 159.35))
cmp("DFF latest", st.on_or_before("DFF", "2026-11-23"), ("2026-11-19", 3.88))
cmp("JP_POLICY_RATE latest", st.on_or_before("JP_POLICY_RATE", "2026-11-23"), ("2026-10-01", 1.227))
cmp("CN_PPI_YOY latest value (label in judgment = obs month-end)", st.on_or_before("CN_PPI_YOY", "2026-11-23")[1], 5.7)
cmp("CN_PPI_YOY latest series date vs judgment label", st.on_or_before("CN_PPI_YOY", "2026-11-23")[0], "2026-10-31")
cmp("CN_CPI_YOY latest value (label in judgment = obs month-end)", st.on_or_before("CN_CPI_YOY", "2026-11-23")[1], 0.7)
cmp("CN_CPI_YOY latest series date vs judgment label", st.on_or_before("CN_CPI_YOY", "2026-11-23")[0], "2026-10-31")
cmp("CN_PMI_MFG latest", st.on_or_before("CN_PMI_MFG", "2026-11-23"), ("2026-10-01", 49.3))

print("### identity nominal = real + breakeven (same day)")
for d in ["2025-11-19", "2026-08-19", "2026-10-20", "2026-10-23", "2026-11-19", "2026-11-20"]:
    u = st.at("UST_10Y", d)
    t = st.at("TIPS_10Y", d)
    b = st.at("BEI_10Y", d)
    print("   %s UST=%s TIPS=%s BEI=%s residual=%s" % (d, u, t, b, None if None in (u, t, b) else round((u - t - b) * 100, 2)))

print("### 12m decomposition 2025-11-19 -> 2026-11-19 (common trading day)")
un, ua, ub = chg_bp("UST_10Y", "2025-11-19", "2026-11-19")
tr, ta, tb = chg_bp("TIPS_10Y", "2025-11-19", "2026-11-19")
br, ba, bb = chg_bp("BEI_10Y", "2025-11-19", "2026-11-19")
cmp("12m UST_10Y chg bp", round(un), 91, nd=0)
cmp("12m TIPS_10Y chg bp", round(tr), 102, nd=0)
cmp("12m BEI_10Y chg bp", round(br), -11, nd=0)
cmp("12m residual bp", round(un - tr - br, 2), 0.0)
cmp("12m window endpoints (UST)", (ua[0], ub[0]), ("2025-11-19", "2026-11-19"))
print("   levels: UST %s->%s TIPS %s->%s BEI %s->%s" % (ua, ub, ta, tb, ba, bb))
cmp("BEI_10Y 12m 2.27 -> 2.16", (ba[1], bb[1]), (2.27, 2.16))
print("### 1m common-day 2026-10-20 -> 2026-11-19")
un, ua, ub = chg_bp("UST_10Y", "2026-10-20", "2026-11-19")
tr, ta, tb = chg_bp("TIPS_10Y", "2026-10-20", "2026-11-19")
br, ba, bb = chg_bp("BEI_10Y", "2026-10-20", "2026-11-19")
cmp("1m UST_10Y chg bp", round(un), -8, nd=0)
cmp("1m TIPS_10Y chg bp", round(tr), 11, nd=0)
cmp("1m BEI_10Y chg bp", round(br), -19, nd=0)
cmp("1m residual bp", round(un - tr - br, 2), 0.0)
print("   levels: UST %s->%s TIPS %s->%s BEI %s->%s" % (ua, ub, ta, tb, ba, bb))
print("### 3m common-day 2026-08-19 -> 2026-11-19")
tr, ta, tb = chg_bp("TIPS_10Y", "2026-08-19", "2026-11-19")
cmp("3m TIPS_10Y chg bp", round(tr), 53, nd=0)

print("### BEI_10Y path")
cmp("BEI_10Y 2026-02-27 = 2.25", st.at("BEI_10Y", "2026-02-27"), 2.25)
cmp("BEI_10Y 2026-05-04 = 2.50", st.at("BEI_10Y", "2026-05-04"), 2.50)
cmp("BEI_10Y 2026-06-10 = 2.34", st.at("BEI_10Y", "2026-06-10"), 2.34)
cmp("BEI_10Y 2026-10-23 = 2.34", st.at("BEI_10Y", "2026-10-23"), 2.34)
post = st.in_range("BEI_10Y", "2026-06-17", "2026-11-23")
cmp("BEI_10Y range from 2026-06-17: min", min(v for d, v in post), 2.15)
cmp("BEI_10Y range from 2026-06-17: max", max(v for d, v in post), 2.40)
print("   n obs in range=%d first=%s last=%s" % (len(post), post[0], post[-1]))
cmp("calendar days 2026-10-23 -> 2026-11-20", lib.days_between("2026-10-23", "2026-11-20"), 28, nd=0)
below = [(d, v) for d, v in st.series("BEI_10Y") if v < 1.8]
cmp("last BEI_10Y obs below 1.8", below[-1], ("2020-11-30", 1.77))
cmp("BEI_10Y first obs date (informational)", st.first_date("BEI_10Y"), st.first_date("BEI_10Y"))
cmp("judgment: 1.77 is 35bp below latest 2.15 (arithmetic)", round((2.15 - 1.77) * 100), 35, nd=0)
print("   BEI_10Y 2026-11-13..2026-11-20:", st.in_range("BEI_10Y", "2026-11-13", "2026-11-23"))

print("### asset 1-month windows (base = obs nearest to 2026-10-23; end = latest <= 2026-11-23)")
A1 = {"SPX": (7623.68, 7203.85, "2026-11-23", -5.51), "SHCOMP": (3690.48, 3538.95, "2026-11-23", -4.11),
      "DAX": (25181.65, 25209.45, "2026-11-23", 0.11), "NIKKEI225": (62693.16, 56436.65, "2026-11-20", -9.98),
      "VIX": (19.45, 27.01, "2026-11-23", 38.87), "DXY": (101.81, 104.079, "2026-11-23", 2.23),
      "GOLD_F": (4007.9, 3685.2, "2026-11-23", -8.05), "UST_10Y": (5.0, 5.04, "2026-11-19", 0.8)}
for mid, (b0, b1, ed, pc) in A1.items():
    a = st.on_or_before(mid, "2026-10-23")
    b = st.on_or_before(mid, "2026-11-23")
    p = lib.pct_change(a[1], b[1])
    print("   %-10s base %s end %s" % (mid, a, b))
    cmp("%s base value" % mid, round(a[1], 2), b0, nd=2)
    cmp("%s end value" % mid, round(b[1], 2), b1, nd=2)
    cmp("%s end date" % mid, b[0], ed)
    cmp("%s chg pct" % mid, round(p, 2), pc)
cmp("CAC40 in series_store", st.has("CAC40"), True)
print("   CAC40 base/end:", st.on_or_before("CAC40", "2026-10-23"), st.on_or_before("CAC40", "2026-11-23"), st.on_or_before("CAC40", "2026-11-20"))

print("### same-day close 2026-10-23 -> 2026-11-20")
SD = {"SPX": -9.36, "DAX": -1.50, "CAC40": 1.86, "NIKKEI225": -9.98, "VIX": 84.52}
for mid, pc in SD.items():
    a = st.on_or_before(mid, "2026-10-23")
    b = st.on_or_before(mid, "2026-11-20")
    print("   %-10s %s -> %s" % (mid, a, b))
    cmp("%s base date (10-23 or prior)" % mid, a[0], "2026-10-23")
    cmp("%s 10-23 -> 11-20 pct" % mid, round(lib.pct_change(a[1], b[1]), 2), pc)

print("### common-day SPX vs TIPS")
for (d0, d1, sp, ti) in [("2025-11-19", "2026-11-19", 8.03, None), ("2025-11-19", "2026-11-19", 22.47, None), ("2025-11-19", "2026-11-19", 9.93, None),
                         ("2026-10-20", "2026-11-19", -6.96, 11), ("2026-08-19", "2026-11-19", -6.90, 53)]:
    pass


def cd(mid, d0, d1):
    a = st.on_or_before(mid, d0)
    b = st.on_or_before(mid, d1)
    return round(lib.pct_change(a[1], b[1]), 2), a[0], b[0]


for mid, exp in [("SPX", 8.03), ("NIKKEI225", 22.47), ("DAX", 9.93)]:
    p, a0, b0 = cd(mid, "2025-11-19", "2026-11-19")
    cmp("12m %s pct (2025-11-19 -> 2026-11-19)" % mid, p, exp)
    print("      obs dates %s -> %s" % (a0, b0))
p, a0, b0 = cd("SPX", "2026-10-20", "2026-11-19")
cmp("1m SPX pct (2026-10-20 -> 2026-11-19)", p, -6.96)
p, a0, b0 = cd("SPX", "2026-08-19", "2026-11-19")
cmp("3m SPX pct (2026-08-19 -> 2026-11-19)", p, -6.90)

print("### BRENT_F")
for ym, exp in [("2026-02", 72.48), ("2026-03", 118.35), ("2026-05", 92.05), ("2026-06", 72.92)]:
    m = st.month_last("BRENT_F", ym)
    cmp("BRENT_F month-end %s" % ym, (m[0], round(m[1], 2)) if m else None, (m[0], exp) if m else None)
    print("      obs %s" % (m,))
fl = st.month_last("BRENT_F", "2026-02")[1], st.month_last("BRENT_F", "2026-05")[1]
cmp("BRENT_F first-last 02->05 pct", round(lib.pct_change(fl[0], fl[1]), 2), 27.00)
cmp("BRENT_F latest", tuple([st.on_or_before("BRENT_F", "2026-11-23")[0]] + [round(st.on_or_before("BRENT_F", "2026-11-23")[1], 2)]), ("2026-11-23", 88.19))
cmp("BRENT_F 2026-10-23", st.at("BRENT_F", "2026-10-23"), 116.72)
mo = st.month_last("BRENT_F", "2026-10")
print("   BRENT_F 2026-10 month-end obs:", mo)
if mo:
    cmp("BRENT_F MTD pct (from 2026-10 month-end)", round(lib.pct_change(mo[1], 88.19), 2), -25.03)
    mtd7 = [x for x in st.series("BRENT_F") if x[0] < "2026-11-01"][-1]
    print("   last obs before November:", mtd7, " -> MTD", round(lib.pct_change(mtd7[1], 88.19), 2))

print("### HY_OAS")
hs = st.series("HY_OAS")
cmp("HY_OAS first obs", hs[0], ("2023-11-21", hs[0][1]))
mx = max(hs, key=lambda x: x[1])
cmp("HY_OAS series max", mx, ("2025-04-07", 4.61))
vals = [v for d, v in hs if d <= "2026-11-19"]
x = 3.52
le = sum(1 for v in vals if v <= x)
lt = sum(1 for v in vals if v < x)
print("   n=%d  share<=x=%.2f  share<x=%.2f  (midrank=%.2f)  share>=x=%.2f" % (len(vals), 100.0 * le / len(vals), 100.0 * lt / len(vals), 100.0 * (le + lt) / 2 / len(vals), 100.0 * sum(1 for v in vals if v >= x) / len(vals)))
cmp("HY_OAS percentile (mid-rank, all history to date)", round(100.0 * (le + lt) / 2 / len(vals)), 92, nd=0)
cmp("HY_OAS percentile (share<=x)", round(100.0 * le / len(vals)), 92, nd=0)
last_ge = [(d, v) for d, v in hs if "2025-05-10" <= d < "2026-11-19" and v >= x]
cmp("no obs >= 3.52 between 2025-05-10 and latest", last_ge, [])
prev_ge = [(d, v) for d, v in hs if d < "2026-11-19" and v >= x]
print("   previous obs >= 3.52:", prev_ge[-1] if prev_ge else None)
cmp("last obs >= 3.52 before latest = 2025-05-09", prev_ge[-1][0] if prev_ge else None, "2025-05-09")
wk = st.on_or_before("HY_OAS", "2026-11-13")
cmp("HY_OAS ISO-week base 2026-11-13", wk, ("2026-11-13", wk[1] if wk else None))
cmp("HY_OAS 1-week chg (pp)", round(3.52 - wk[1], 2), 0.29)
d7 = lib.ymd("2026-11-19") - __import__("datetime").timedelta(days=7)
s7 = st.on_or_before("HY_OAS", d7.isoformat())
print("   strict 7d base obs:", s7)
cmp("HY_OAS strict 7-day chg (pp)", round(3.52 - s7[1], 2), 0.32)
y = st.on_or_before("HY_OAS", "2025-11-19")
cmp("HY_OAS 12m ago obs", y, ("2025-11-19", y[1] if y else None))
cmp("HY_OAS 12m chg (pp)", round(3.52 - y[1], 2), 0.35)
import datetime as _dt
print("   weekday of 2026-11-13:", _dt.date(2026, 11, 13).strftime("%a"), "; of 2026-11-19:", _dt.date(2026, 11, 19).strftime("%a"))

print("### FX")
cmp("USDCNY 2025-11-19", st.at("USDCNY", "2025-11-19"), 7.1075, nd=4)
cmp("USDCNY 2026-11-19", st.at("USDCNY", "2026-11-19"), 6.6676, nd=4)
cmp("USDCNY chg pct (full precision)", round(lib.pct_change(st.at("USDCNY", "2025-11-19"), st.at("USDCNY", "2026-11-19")), 2), -6.19)
cmp("USDJPY 2026-10-23", st.at("USDJPY", "2026-10-23"), 156.49)
cmp("USDJPY 2026-11-23", st.at("USDJPY", "2026-11-23"), 159.35)
cmp("USDJPY 1m pct (full precision)", round(lib.pct_change(st.at("USDJPY", "2026-10-23"), st.at("USDJPY", "2026-11-23")), 2), 1.82)

print("### USDJPY / SPX daily co-movement, base 2026-10-23, days 2026-10-26..2026-11-23 on common dates")
spx = dict(st.in_range("SPX", "2026-10-23", "2026-11-23"))
jpy = dict(st.in_range("USDJPY", "2026-10-23", "2026-11-23"))
base_s = st.on_or_before("SPX", "2026-10-23")
base_j = st.on_or_before("USDJPY", "2026-10-23")
print("   SPX obs in range: %d ; USDJPY obs in range: %d ; bases %s %s" % (len(spx), len(jpy), base_s, base_j))
common = sorted(set(d for d in spx if d >= "2026-10-26") & set(d for d in jpy if d >= "2026-10-26"))
print("   common dates (%d): %s" % (len(common), common))
ps, pj, prev_s, prev_j = [], [], base_s[1], base_j[1]
rows = []
for d in common:
    a = lib.pct_change(prev_s, spx[d])
    b = lib.pct_change(prev_j, jpy[d])
    rows.append((d, a, b))
    ps.append(a)
    pj.append(b)
    prev_s, prev_j = spx[d], jpy[d]


def corr(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    return cov / math.sqrt(va * vb)


cmp("number of common trading days", len(common), 21, nd=0)
cmp("corr of daily pct changes", round(corr(ps, pj), 2), 0.19)
dn = [(d, a, b) for d, a, b in rows if a < 0]
up = [(d, a, b) for d, a, b in rows if a > 0]
cmp("SPX down days", len(dn), 12, nd=0)
cmp("SPX up days", len(up), 9, nd=0)
cmp("USDJPY down on SPX-down days", sum(1 for d, a, b in dn if b < 0), 9, nd=0)
cmp("USDJPY up on SPX-down days", sum(1 for d, a, b in dn if b > 0), 3, nd=0)
cmp("USDJPY up on SPX-up days", sum(1 for d, a, b in up if b > 0), 7, nd=0)
cmp("USDJPY down on SPX-up days", sum(1 for d, a, b in up if b < 0), 2, nd=0)


def comp(items, idx):
    c = 1.0
    for it in items:
        c *= (1 + it[idx] / 100.0)
    return (c - 1.0) * 100.0


cmp("USDJPY compound on SPX-down days", round(comp(dn, 2), 2), 0.16)
cmp("USDJPY compound on SPX-up days", round(comp(up, 2), 2), 1.66)
top4 = sorted(rows, key=lambda x: x[1])[:4]
cmp("four largest SPX daily drops (dates)", [x[0] for x in top4], ["2026-11-05", "2026-11-20", "2026-11-19", "2026-11-16"])
cmp("USDJPY pct on those days", [round(x[2], 2) for x in top4], [-0.07, 0.20, -0.08, -0.06])
for d, a, b in rows:
    print("      %s SPX %+.2f%%  USDJPY %+.2f%%" % (d, a, b))

print("### JP CPI path and CN PMI window")
print("   JP_CPI_YOY 2025-01..2026-02:", st.in_range("JP_CPI_YOY", "2025-01-01", "2026-02-28"))
jp = st.in_range("JP_CPI_YOY", "2025-01-01", "2026-02-28")
cmp("JP CPI 2025-01 = 4.03", st.at("JP_CPI_YOY", "2025-01-01"), 4.03)
cmp("JP CPI max over 2025-01..2026-02 is 2025-01", max(jp, key=lambda x: x[1])[0][:7], "2025-01")
jm = [(d[:7], v) for d, v in jp]
ups = [jm[i][0] for i in range(1, len(jm)) if jm[i][1] > jm[i - 1][1]]
cmp("months of uptick between 2025-02 and 2026-02", ups, ["2025-09", "2025-10"])
print("   CN_PMI_MFG 2025-10..2026-10:", st.in_range("CN_PMI_MFG", "2025-10-01", "2026-10-31"))
pm = [(d[:7], v) for d, v in st.in_range("CN_PMI_MFG", "2025-11-01", "2026-10-31")]
cmp("CN PMI months >50 in window", [m for m, v in pm if v > 50], ["2025-12", "2026-03", "2026-04", "2026-06", "2026-09"])
cmp("CN PMI months ==50 in window", [m for m, v in pm if v == 50], ["2026-05"])
rest = [v for m, v in pm if v < 50]
cmp("CN PMI remaining months range", (min(rest), max(rest)), (49.0, 49.8))
print("   CN_PPI_YOY / CN_CPI_YOY last obs dates:", st.on_or_before("CN_PPI_YOY", "2026-11-23"), st.on_or_before("CN_CPI_YOY", "2026-11-23"), " CN_PMI:", st.on_or_before("CN_PMI_MFG", "2026-11-23"))
print("   EA_HICP window:", st.in_range("EA_HICP_YOY", "2025-10-01", "2026-10-31"))
print("=" * 100)
print("POINTS=%d MISMATCHES=%d" % (N[0], N[1]))
for m in MIS:
    print("MISMATCH:", m)
