#!/usr/bin/python3 -I
"""Dump series tail from snapshot series_store.
Args: <snapshot.json> <since_date|tailN via -n N> <metric> [<metric> ...]
Usage: s03_series.py snap.json --since 2025-01-01 JP_CPI_YOY EA_HICP_YOY
       s03_series.py snap.json --tail 25 SPX
"""
import json
import sys


def main():
    path = sys.argv[1]
    mode = sys.argv[2]
    arg = sys.argv[3]
    metrics = sys.argv[4:]
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    ss = d["series_store"]
    for m in metrics:
        if m not in ss:
            print(f"## {m}: NOT IN series_store")
            continue
        s = ss[m]
        dates = s["dates"]
        vals = s["values"]
        print(f"## {m}: n={len(dates)} first={dates[0]} last={dates[-1]} keys={list(s.keys())}")
        if mode == "--since":
            idx = [i for i, x in enumerate(dates) if x >= arg]
        else:
            idx = list(range(len(dates)))[-int(arg):]
        for i in idx:
            print(f"  {dates[i]}  {vals[i]!r}")


if __name__ == "__main__":
    main()
