#!/usr/bin/env python3
"""Dump monthly paths of the key series (read-only) so the seat can eyeball turning claims.

usage: python3 -I dump_paths.py <snapshot.json> <out.txt>
"""
import sys
sys.path.insert(0, "/tmp/r32-accept/review/A_round1")
import seatlib as L

snap = L.load(sys.argv[1])
out = open(sys.argv[2], "w", encoding="utf-8")


def w(s=""):
    out.write(s + "\n")


def show(sid, start, end, kind="last"):
    pts = L.series(snap, sid)
    if pts is None:
        w(f"{sid}: NOT IN series_store")
        return
    w(f"--- {sid} n={len(pts)} first={pts[0][0]} last={pts[-1][0]} ---")
    yms = []
    y, m = int(start[:4]), int(start[5:7])
    while True:
        ym = f"{y:04d}-{m:02d}"
        if ym > end:
            break
        yms.append(ym)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    row = []
    for ym in yms:
        if kind == "last":
            t = L.month_last(pts, ym)
        elif kind == "first":
            t = L.month_first(pts, ym)
        else:
            mv, n = L.month_mean(pts, ym)
            t = (f"mean(n={n})", mv)
        if t is None:
            row.append(f"{ym}=—")
        else:
            row.append(f"{ym}={t[1]:.4g}")
    w("  ".join(row))


# monthly macro (obs dated YYYY-MM-01)
for sid in ["CPI", "CORE_CPI", "CORE_PCE", "INDPRO", "UNEMPLOYMENT", "US_REAL_GDP",
            "CN_PMI_MFG", "CN_CPI_YOY", "CN_PPI_YOY", "EA_HICP_YOY", "EA_REAL_GDP_YOY",
            "JP_CPI_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_RATE", "JP_REAL_GDP_YOY"]:
    show(sid, "2024-01", "2026-11", "first")

w("\n=== YoY derived (same month prior year) ===")
for sid in ["CPI", "CORE_CPI", "CORE_PCE", "INDPRO", "CN_PMI_MFG", "US_REAL_GDP"]:
    pts = L.series(snap, sid)
    w(f"--- YoY {sid} ---")
    row = []
    y, m = 2024, 1
    while True:
        d = f"{y:04d}-{m:02d}-01"
        if d > "2026-11-01":
            break
        yy, bd, bv = L.yoy(pts, d)
        row.append(f"{d[:7]}={'—' if yy is None else f'{yy:.4g}'}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    w("  ".join(row))

w("\n=== daily: policy series full change list 2025-01-01..2026-11-23 ===")
for sid in ["DFEDTARU", "DFEDTARL", "DFF", "ECB_DFR", "ECB_MRO", "CN_LPR_1Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT"]:
    pts = L.series(snap, sid)
    if pts is None:
        w(f"{sid}: NOT IN series_store")
        continue
    w(f"--- {sid} n={len(pts)} first={pts[0]} last={pts[-1]} ---")
    ch = L.changes_in_window(pts, "2025-01-01", "2026-11-23")
    for c in ch:
        w(f"   {c[0]}: {c[1]} -> {c[2]}")
    if sid in ("CN_OMO_7D", "CN_POLICY_OVERNIGHT", "DFF"):
        tail = [p for p in pts if p[0] >= "2026-10-20"]
        w("   tail: " + " ".join(f"{d}:{v}" for d, v in tail))

w("\n=== daily: last obs per cited market series ===")
for sid in ["SPX", "NDX", "RUT", "DXY", "EURUSD", "GOLD_F", "SILVER_F", "BRENT_F", "VIX", "DAX", "CAC40",
            "USDJPY", "USDCNY", "HY_OAS", "BB_OAS", "B_OAS", "CCC_OAS", "IG_OAS", "UST_2Y", "UST_10Y",
            "UST_30Y", "TIPS_5Y", "TIPS_10Y", "BEI_5Y", "BEI_10Y", "CURVE_2S10S", "SHCOMP", "HSI", "NIKKEI225",
            "UST_5Y"]:
    pts = L.series(snap, sid)
    w(f"{sid}: last={pts[-1]}  prev={pts[-2] if len(pts) > 1 else None}")

w("\n=== BRENT_F monthly (mean / last) 2025-10..2026-11 ===")
show("BRENT_F", "2025-10", "2026-11", "mean")
show("BRENT_F", "2025-10", "2026-11", "last")
out.close()
print("written", sys.argv[2])
