#!/usr/bin/python3
"""Raw probe of series_store values (read-only) so the main recompute script can be written against real formats.
Usage: python3 -I s06_probe.py <snapshot.json> <out.txt>
"""
import json
import math
import sys

RANGES = {
    "DFEDTARU": ("2025-10-01", "2026-11-30"),
    "DFEDTARL": ("2025-10-01", "2026-11-30"),
    "DFF": ("2025-11-15", "2026-11-30"),
    "JP_POLICY_RATE": ("2025-09-01", "2026-12-31"),
    "CN_LPR_1Y": ("2026-06-01", "2026-12-31"),
    "CN_OMO_7D": ("2026-06-01", "2026-12-31"),
    "CN_POLICY_OVERNIGHT": ("2020-01-01", "2027-01-01"),
    "CPI": ("2025-01-01", "2026-12-31"),
    "CORE_CPI": ("2025-01-01", "2026-12-31"),
    "CORE_PCE": ("2025-01-01", "2026-12-31"),
    "UNEMPLOYMENT": ("2025-10-01", "2026-12-31"),
    "INDPRO": ("2025-01-01", "2026-12-31"),
    "US_REAL_GDP": ("2024-07-01", "2026-12-31"),
    "CN_PMI_MFG": ("2025-06-01", "2026-12-31"),
    "CN_CPI_YOY": ("2025-06-01", "2026-12-31"),
    "CN_PPI_YOY": ("2025-06-01", "2026-12-31"),
    "JP_CPI_YOY": ("2025-09-01", "2026-12-31"),
    "JP_CPI_TOKYO_YOY": ("2025-01-01", "2026-12-31"),
    "JP_REAL_GDP_YOY": ("2025-01-01", "2026-12-31"),
}


def finite(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def main():
    snap_path, out_path = sys.argv[1], sys.argv[2]
    with open(snap_path, "r", encoding="utf-8") as fh:
        snap = json.load(fh)
    store = snap["series_store"]
    out = []
    # series_store structure sample
    s = store["DFEDTARU"]
    out.append("DFEDTARU keys=%s" % sorted(s.keys()))
    out.append("DFEDTARU dates[0..2]=%s values[0..2]=%r" % (s["dates"][:3], s["values"][:3]))
    out.append("DFEDTARU dates[-3..]=%s values[-3..]=%r" % (s["dates"][-3:], s["values"][-3:]))
    out.append("types: date=%s value=%s" % (type(s["dates"][0]).__name__, type(s["values"][0]).__name__))
    for k in sorted(store.keys()):
        ser = store[k]
        if not isinstance(ser, dict) or "dates" not in ser:
            out.append("%s: not series (%s)" % (k, type(ser).__name__))
    for metric, (lo, hi) in RANGES.items():
        ser = store.get(metric)
        if ser is None:
            out.append("%s: ABSENT from series_store" % metric)
            continue
        pairs = [(d, v) for d, v in zip(ser["dates"], ser["values"]) if lo <= d <= hi]
        out.append("## %s (n_total=%d, first=%s, last=%s) range %s..%s -> %d pts"
                   % (metric, len(ser["dates"]), ser["dates"][0], ser["dates"][-1], lo, hi, len(pairs)))
        out.append("   " + "; ".join("%s=%r" % (d, v) for d, v in pairs))
    # daily asset values at specific dates (exact and nearest)
    for metric in ["SPX", "NIKKEI225", "SHCOMP", "DAX", "CAC40", "VIX", "DXY", "UST_10Y", "TIPS_10Y", "BEI_10Y"]:
        ser = store[metric]
        dd = dict(zip(ser["dates"], ser["values"]))
        out.append("## daily %s last=%s" % (metric, ser["dates"][-1]))
        for d in ["2025-11-19", "2026-10-20", "2026-10-22", "2026-10-23", "2026-11-18", "2026-11-19", "2026-11-20", "2026-11-21", "2026-11-22", "2026-11-23"]:
            out.append("   %s -> %r" % (d, dd.get(d, "<no obs>")))
        # November 2026 tail
        tail = [(d, v) for d, v in zip(ser["dates"], ser["values"]) if d >= "2026-11-01"]
        out.append("   Nov tail: " + "; ".join("%s=%.4f" % (d, v) for d, v in tail))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("wrote", out_path, "lines", len(out))


if __name__ == "__main__":
    main()
