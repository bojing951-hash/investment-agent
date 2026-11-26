#!/usr/bin/env python3
"""Probe 14: visibility at September policy decisions + misc NIT checks (read-only).
usage: python3 -I probe14.py <snapshot> <calendar> <report.json> <registry> <MAP_REPORT.md> <out.txt>
"""
import sys

sys.path.insert(0, "/tmp/r32-accept/review/A_round1")
import rc_common as C  # noqa: E402

ctx = C.Ctx(sys.argv)
out = open(sys.argv[6], "w", encoding="utf-8")


def w(s=""):
    out.write(s + "\n")


w("=== visibility at policy decision dates (rule/calendar based) ===")
for anc in ("2026-06-10", "2026-06-11", "2026-09-10", "2026-09-16", "2026-09-18", "2026-11-23"):
    for sid in ("CPI", "CORE_PCE", "CORE_CPI", "EA_HICP_YOY", "JP_CPI_YOY", "JP_CPI_TOKYO_YOY"):
        w("%s %s -> %s" % (anc, sid, ctx.visible(sid, anc)))
w("=== CPI yoy 2026-05..2026-10 ===")
for m in range(5, 11):
    w("2026-%02d %s" % (m, ctx.yoy("CPI", "2026-%02d-01" % m)))
w("=== CN_PMI_MFG months >50 since 2025-01 ===")
w(str([(d[:7], v) for d, v in ctx.ser("CN_PMI_MFG") if d >= "2025-01-01" and v is not None and v > 50]))
w(str([(d[:7], v) for d, v in ctx.ser("CN_PMI_MFG") if d >= "2025-01-01" and v is not None and v == 50]))
w("=== HY_OAS recent ===")
w(str([(d, v) for d, v in ctx.ser("HY_OAS") if d >= "2026-10-20"]))
h = dict((d, v) for d, v in ctx.ser("HY_OAS") if v is not None)
b = ctx.lob("HY_OAS", "2026-11-12")
w("strict 7d basis 2026-11-12=%s -> 3.52 = %+.2fpp" % (b, 3.52 - b[1]))
vals = [v for d, v in ctx.ser("HY_OAS") if v is not None and d <= "2026-11-19"]
w("HY_OAS n=%d first=%s max=%s days>3.52=%d last>3.52=%s" % (
    len(vals), ctx.ser("HY_OAS")[0][0], max(vals), sum(1 for v in vals if v > 3.52),
    max(d for d, v in ctx.ser("HY_OAS") if v is not None and v > 3.52)))
w("=== BEI_10Y pre/post tightening ===")
w(str([(d, v) for d, v in ctx.ser("BEI_10Y") if "2026-02-20" <= d <= "2026-02-28"]))
w(str([(d, v) for d, v in ctx.ser("BEI_10Y") if "2026-05-01" <= d <= "2026-05-06"]))
w(str([(d, v) for d, v in ctx.ser("BEI_10Y") if "2026-06-08" <= d <= "2026-06-12"]))
w(str([(d, v) for d, v in ctx.ser("BEI_10Y") if "2026-09-08" <= d <= "2026-09-12"]))
w("=== BEI_10Y 12m common-day ===")
a = ctx.lob("BEI_10Y", "2025-11-19")
b = ctx.lob("BEI_10Y", "2026-11-19")
w("%s -> %s = %+.0fbp; 11-20=%s" % (a, b, (b[1] - a[1]) * 100, ctx.exact("BEI_10Y", "2026-11-20")))
w("=== JP_POLICY_RATE monthly 2025-09..2026-10 ===")
w(str([(d[:7], v) for d, v in ctx.ser("JP_POLICY_RATE") if "2025-09-01" <= d <= "2026-10-31"]))
w("=== EA HICP yoy 2025-10..2026-10 ===")
w(str([(d[:7], v) for d, v in ctx.ser("EA_HICP_YOY") if "2025-10-01" <= d <= "2026-10-31"]))
w("=== CORE_CPI yoy? series CORE_CPI level 2026-01..2026-05 ===")
for m in range(1, 6):
    w("2026-%02d %s" % (m, ctx.yoy("CORE_CPI", "2026-%02d-01" % m)))
w("=== BRENT_F month-end 2026-02..05 ===")
for m in range(2, 6):
    w("2026-%02d %s" % (m, ctx.mlast("BRENT_F", "2026-%02d" % m)))
w("=== two-caliber max gaps (engine aftermath vs month-end) ===")
rep = ctx.rep
try:
    st = [s for s in rep["steps"] if s.get("step") == "S6_analog"][0]
    top = st["envelope"]["data"]["top"]
    for c in top[:3]:
        lab = c.get("anchor_month")
        for met, af in (c.get("aftermath") or {}).items():
            if not isinstance(af, dict) or "_" in met:
                continue
            for k in ("3m", "6m", "12m"):
                if k in af:
                    w("%s %s %s engine=%s" % (lab, met, k, af[k]))
except Exception as e:  # noqa: BLE001
    w("ERR %r" % (e,))
out.close()
print("written", sys.argv[6])
