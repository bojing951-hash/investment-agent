#!/usr/bin/env python3
"""Read-only: print series from frozen snapshot.
usage: s03_series.py <snapshot.json> <METRIC> [<METRIC> ...] [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--tail N]
"""
import json
import sys
import math


def main():
    args = sys.argv[1:]
    path = args[0]
    frm = None
    to = None
    tail = None
    metrics = []
    i = 1
    while i < len(args):
        a = args[i]
        if a == "--from":
            frm = args[i + 1]
            i += 2
        elif a == "--to":
            to = args[i + 1]
            i += 2
        elif a == "--tail":
            tail = int(args[i + 1])
            i += 2
        else:
            metrics.append(a)
            i += 1
    with open(path, "r", encoding="utf-8") as f:
        snap = json.load(f)
    store = snap["series_store"]
    for m in metrics:
        if m not in store:
            print(f"## {m}: NOT IN series_store")
            continue
        s = store[m]
        dates = s.get("dates", [])
        vals = s.get("values", [])
        print(f"## {m}: n={len(dates)} first={dates[0] if dates else None} last={dates[-1] if dates else None} extra_keys={[k for k in s if k not in ('dates','values')]}")
        for k in s:
            if k not in ("dates", "values"):
                print(f"   {k} = {json.dumps(s[k], ensure_ascii=False)[:400]}")
        rows = list(zip(dates, vals))
        if frm:
            rows = [r for r in rows if r[0] >= frm]
        if to:
            rows = [r for r in rows if r[0] <= to]
        if tail:
            rows = rows[-tail:]
        for d, v in rows:
            if isinstance(v, float):
                print(f"   {d}  {v!r}")
            else:
                print(f"   {d}  {v}")


if __name__ == "__main__":
    main()
