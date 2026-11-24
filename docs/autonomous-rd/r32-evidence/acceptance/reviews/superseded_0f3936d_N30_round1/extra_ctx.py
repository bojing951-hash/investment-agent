#!/usr/bin/env python3
"""Seat script: context numbers for counter-attacks (read-only; nothing here counts as a recompute point).
Usage: python3 -I extra_ctx.py <snapshot.json> <out.txt>
"""
import json
import sys


def main():
    snap_p, out_p = sys.argv[1:3]
    with open(snap_p, encoding="utf-8") as f:
        sn = json.load(f)
    store = sn["series_store"]
    orig = sys.stdout
    sys.stdout = open(out_p, "w", encoding="utf-8")
    try:
        def at(mid, d):
            s = store[mid]
            for x, v in zip(s["dates"], s["values"]):
                if x == d:
                    return v
            return None

        def pct(a, b):
            return (b / a - 1.0) * 100.0

        print("== cross-region index returns inside the VIX jump window (close 2026-11-13 -> close 2026-11-20) ==")
        for mid in ("SPX", "DAX", "CAC40", "NIKKEI225"):
            a, b = at(mid, "2026-11-13"), at(mid, "2026-11-20")
            print("%s: %.2f -> %.2f = %+.2f%%" % (mid, a, b, pct(a, b)))
        print("== month window (2026-10-23 -> 2026-11-20) ==")
        for mid in ("SPX", "DAX", "CAC40", "NIKKEI225"):
            a, b = at(mid, "2026-10-23"), at(mid, "2026-11-20")
            print("%s: %.2f -> %.2f = %+.2f%%" % (mid, a, b, pct(a, b)))
        print("== presumed inflation release days vs same-day closes (non-synchronous: Tokyo < Europe < New York) ==")
        mids = ("SPX", "DAX", "CAC40", "NIKKEI225", "EURUSD", "USDJPY", "VIX")
        for mid in mids:
            ds = store[mid]["dates"]
            vs = store[mid]["values"]
            row = []
            for i, d in enumerate(ds):
                if d in ("2026-11-16", "2026-11-17", "2026-11-19", "2026-11-20") and i > 0 and vs[i - 1]:
                    row.append("%s vs %s %+.2f%%" % (d[5:], ds[i - 1][5:], pct(vs[i - 1], vs[i])))
            print(mid, "|", " ; ".join(row))
        print("== earlier in-window spike episode (closes) ==")
        for mid in ("VIX", "SPX", "NIKKEI225"):
            s = store[mid]
            print(mid, " ; ".join("%s %.2f" % (d[5:], v) for d, v in zip(s["dates"], s["values"]) if "2026-11-04" <= d <= "2026-11-11"))
        print("VIX 2026-11-04 -> 11-05: %+.2f%% ; 11-05 -> 11-11: %+.2f%%" % (pct(at("VIX", "2026-11-04"), at("VIX", "2026-11-05")), pct(at("VIX", "2026-11-05"), at("VIX", "2026-11-11"))))
        print("== implied EURJPY = EURUSD x USDJPY ==")
        for d in ("2026-10-23", "2026-11-20", "2026-11-23"):
            print(d, "EURUSD %.6f x USDJPY %.3f = %.3f" % (at("EURUSD", d), at("USDJPY", d), at("EURUSD", d) * at("USDJPY", d)))
        print("10-23 -> 11-20: %+.2f%% ; 10-23 -> 11-23: %+.2f%%" % (
            pct(at("EURUSD", "2026-10-23") * at("USDJPY", "2026-10-23"), at("EURUSD", "2026-11-20") * at("USDJPY", "2026-11-20")),
            pct(at("EURUSD", "2026-10-23") * at("USDJPY", "2026-10-23"), at("EURUSD", "2026-11-23") * at("USDJPY", "2026-11-23"))))
        print("== JP_CPI_YOY path 2025-01..2026-02 (for 「持续回落」 wording) ==")
        s = store["JP_CPI_YOY"]
        print(" ; ".join("%s %.2f" % (d[:7], v) for d, v in zip(s["dates"], s["values"]) if "2025-01" <= d <= "2026-02"))
        print("== JP_POLICY_RATE 2026-04..2026-10 and steps (bp) ==")
        s = store["JP_POLICY_RATE"]
        row = [(d[:7], v) for d, v in zip(s["dates"], s["values"]) if "2026-04" <= d <= "2026-10"]
        print(" ; ".join("%s %.3f" % x for x in row))
        print("steps bp:", ["%s %+.1f" % (row[i][0], (row[i][1] - row[i - 1][1]) * 100) for i in range(1, len(row))], "sum %+.1f" % ((row[-1][1] - row[0][1]) * 100))
        print("== EA/JP momentum from alternative start months to 2026-10 (pp) ==")
        for ym in ("2026-04", "2026-05", "2026-06", "2026-07", "2026-08"):
            ea = at("EA_HICP_YOY", ym + "-01")
            jp = at("JP_CPI_YOY", ym + "-01")
            print(ym, "EA %+.2f (from %.2f) JP %+.2f (from %.2f)" % (4.0 - ea, ea, 2.44 - jp, jp))
        print("== snapshot top-level keys ==", list(sn.keys()))
        ga = sn.get("gate_a", {})
        print("gate_a keys:", list(ga.keys()))
        print("gate_a noncore_missing_detail:", json.dumps(ga.get("noncore_missing_detail"), ensure_ascii=False)[:1500])
        print("gate_a degraded/noncore lists:", json.dumps({k: ga.get(k) for k in ga if k not in ("noncore_missing_detail",)}, ensure_ascii=False)[:2500])
    finally:
        sys.stdout.close()
        sys.stdout = orig


if __name__ == "__main__":
    main()
