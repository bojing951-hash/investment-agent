#!/usr/bin/env python3
"""Seat script: peek daily series tails relevant to N30 (read-only).
Usage: python3 -I peek_daily.py <snapshot.json>
"""
import json
import sys

DAILY = ["SPX", "NIKKEI225", "DAX", "CAC40", "VIX", "EURUSD", "USDJPY", "DXY", "RUT",
         "UST_10Y", "TIPS_10Y", "BEI_10Y"]


def main():
    with open(sys.argv[1], encoding="utf-8") as f:
        snap = json.load(f)
    ss = snap["series_store"]
    for m in DAILY:
        s = ss[m]
        d, v = s["dates"], s["values"]
        n = len(d)
        print(f"\n== {m}: n={n} first={d[0]} last={d[-1]} keys={list(s.keys())}")
        # print from 2026-10-15 onward
        for i in range(n):
            if d[i] >= "2026-10-15":
                print(f"  {d[i]}  {v[i]!r}")


if __name__ == "__main__":
    main()
