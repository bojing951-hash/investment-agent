#!/usr/bin/env python3
"""Dump (date, value) pairs of a snapshot series_store metric.
usage: python3 -I s1_series.py <snapshot> <metric_id> [start_date] [end_date] [max_rows]
Prints keys of the entry first, then rows.
"""
import json
import sys


def main():
    snap_path, metric = sys.argv[1], sys.argv[2]
    start = sys.argv[3] if len(sys.argv) > 3 else None
    end = sys.argv[4] if len(sys.argv) > 4 else None
    max_rows = int(sys.argv[5]) if len(sys.argv) > 5 else 5000
    with open(snap_path, "r", encoding="utf-8") as fh:
        snap = json.load(fh)
    store = snap["series_store"]
    if metric not in store:
        print("NOT IN series_store:", metric)
        return
    ent = store[metric]
    meta = {k: v for k, v in ent.items() if not isinstance(v, list)}
    print("META:", json.dumps(meta, ensure_ascii=False)[:1500])
    dates = ent.get("dates") or []
    values = ent.get("values") or []
    print("N=", len(dates), "first=", dates[0] if dates else None, "last=", dates[-1] if dates else None)
    rows = 0
    for d, v in zip(dates, values):
        if start and d < start:
            continue
        if end and d > end:
            continue
        print(d, repr(v))
        rows += 1
        if rows >= max_rows:
            break


if __name__ == "__main__":
    main()
