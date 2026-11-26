#!/usr/bin/env python3
"""Seat intermediate table: monthly YoY paths + market levels at the dates the judgment text cites.

usage: python3 -I rc_paths.py <snapshot.json> <release_calendar.json> <report.json> <metric_registry.json> <MAP_REPORT.md> <out.txt>
"""
import sys

sys.path.insert(0, "/tmp/r32-accept/review/A_round1")
import rc_common as C  # noqa: E402

ctx = C.Ctx(sys.argv)
out = open(ctx.out_path, "w", encoding="utf-8")


def w(s=""):
    out.write(s + "\n")


w("=== YoY paths (same month prior year) 2025-09..2026-10 ===")
for sid in ["CPI", "CORE_CPI", "CORE_PCE", "INDPRO", "US_REAL_GDP", "CN_PMI_MFG"]:
    p = ctx.ser(sid)
    row = []
    y, m = 2025, 1
    while (y, m) <= (2026, 10):
        d = "%04d-%02d-01" % (y, m)
        yy, bd, bv = C.L.yoy(p, d)
        row.append("%s=%s" % (d[:7], "—" if yy is None else "%.4f" % yy))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    w(sid + ": " + "  ".join(row))

w("\n=== levels of monthly series 2025-09..2026-10 ===")
for sid in ["CPI", "CORE_CPI", "CORE_PCE", "INDPRO", "UNEMPLOYMENT", "CN_PMI_MFG", "CN_CPI_YOY", "CN_PPI_YOY",
            "EA_HICP_YOY", "JP_CPI_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_RATE", "BRENT_F"]:
    row = []
    y, m = 2025, 1
    while (y, m) <= (2026, 11):
        ym = "%04d-%02d" % (y, m)
        if sid == "BRENT_F":
            mv, n = ctx.mmean(sid, ym)
            t = ctx.mlast(sid, ym)
            row.append("%s=mean%s/last%s" % (ym, "—" if mv is None else "%.2f" % mv, "—" if t is None else "%.2f" % t[1]))
        else:
            v = ctx.exact(sid, ym + "-01")
            row.append("%s=%s" % (ym, "—" if v is None else "%.4g" % v))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    w(sid + ": " + "  ".join(row))

w("\n=== JP_CPI_YOY full 2024-01..2026-10 (down-turn origin check) ===")
row = []
y, m = 2024, 1
while (y, m) <= (2026, 10):
    v = ctx.exact("JP_CPI_YOY", "%04d-%02d-01" % (y, m))
    row.append("%04d-%02d=%s" % (y, m, "—" if v is None else "%.2f" % v))
    y, m = (y + 1, 1) if m == 12 else (y, m + 1)
w("  ".join(row))

w("\n=== rates: values on cited dates ===")
for sid in ["UST_10Y", "TIPS_10Y", "BEI_10Y", "UST_2Y", "CURVE_2S10S", "HY_OAS", "TIPS_5Y", "BEI_5Y"]:
    row = []
    for d in ["2025-11-19", "2025-11-20", "2026-02-17", "2026-02-20", "2026-03-31", "2026-04-30", "2026-05-19",
              "2026-05-29", "2026-06-10", "2026-06-11", "2026-06-16", "2026-06-17", "2026-07-31", "2026-08-20",
              "2026-08-21", "2026-09-09", "2026-09-10", "2026-09-15", "2026-09-16", "2026-09-17", "2026-09-30",
              "2026-10-20", "2026-10-21", "2026-10-22", "2026-10-23", "2026-11-12", "2026-11-19", "2026-11-20"]:
        t = ctx.lob(sid, d)
        row.append("%s=%s@%s" % (d[5:], "—" if t is None else "%.3f" % t[1], "" if t is None else t[0][5:]))
    w(sid + ": " + "  ".join(row))

w("\n=== BEI_10Y / TIPS_10Y / HY_OAS daily from 2026-10-13 ===")
for sid in ["BEI_10Y", "TIPS_10Y", "HY_OAS", "UST_10Y"]:
    p = [x for x in ctx.ser(sid) if x[0] >= "2026-10-13"]
    w(sid + ": " + "  ".join("%s:%.3f" % (d[5:], v) for d, v in p))

w("\n=== 30-day windows cited in text (last obs on/before start) ===")
for sid, start, end in [("BRENT_F", "2026-10-23", "2026-11-23"), ("BEI_10Y", "2026-10-20", "2026-11-20"),
                        ("USDJPY", "2026-10-23", "2026-11-23"), ("SPX", "2026-10-23", "2026-11-20"),
                        ("SPX", "2026-10-23", "2026-11-23"), ("HY_OAS", "2026-11-12", "2026-11-19"),
                        ("DXY", "2026-10-23", "2026-11-23"), ("GOLD_F", "2026-10-23", "2026-11-23"),
                        ("SHCOMP", "2026-10-23", "2026-11-23"), ("DAX", "2026-10-23", "2026-11-23"),
                        ("VIX", "2026-10-23", "2026-11-23"), ("NIKKEI225", "2026-10-23", "2026-11-20"),
                        ("UST_10Y", "2026-10-23", "2026-11-19"), ("TIPS_10Y", "2026-10-20", "2026-11-19")]:
    a = ctx.lob(sid, start)
    b = ctx.lob(sid, end)
    w("%s %s..%s : %s -> %s  chg=%.6g pct=%.4f" % (
        sid, start, end, a, b, (b[1] - a[1]) if a and b else float("nan"),
        C.L.pct(a[1], b[1]) if a and b else float("nan")))

w("\n=== BRENT_F: month-to-date 2026-11 (vs 2026-10-30 last) ===")
b_last_oct = ctx.lob("BRENT_F", "2026-10-31")
b_now = ctx.lob("BRENT_F", "2026-11-23")
w("oct_last=%s now=%s mtd=%.4f" % (b_last_oct, b_now, C.L.pct(b_last_oct[1], b_now[1])))

w("\n=== series first/last dates ===")
for sid in ["JP_POLICY_RATE", "ECB_DFR", "ECB_MRO", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "CN_LPR_1Y", "DFEDTARU", "DFF",
            "JP_CPI_TOKYO_YOY", "HY_OAS", "USDJPY", "SPX", "DAX", "SHCOMP", "NIKKEI225", "VIX", "BRENT_F"]:
    p = ctx.ser(sid)
    w("%s: n=%d first=%s last=%s" % (sid, len(p), p[0], p[-1]))

w("\n=== policy change lists (value change vs previous observation) ===")
for sid in ["ECB_DFR", "ECB_MRO", "DFEDTARU", "DFF", "CN_LPR_1Y", "CN_OMO_7D", "JP_POLICY_RATE"]:
    p = ctx.ser(sid)
    w(sid + ":")
    for c in C.L.changes_in_window(p, "2024-01-01", "2026-11-23"):
        w("   %s: %s -> %s (%+.0fbp)" % (c[0], c[1], c[2], (c[2] - c[1]) * 100))
out.close()
print("written", ctx.out_path)
