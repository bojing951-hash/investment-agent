#!/usr/bin/env python3
"""Lookup daily values in snapshot series_store.
usage:
  python3 -I s3_daily.py <snapshot> <metric> at <date1> [<date2> ...]   # exact dates (nearest <= if missing, flagged)
  python3 -I s3_daily.py <snapshot> <metric> range <start> <end>
"""
import json
import sys


def load(snap_path):
    with open(snap_path, "r", encoding="utf-8") as fh:
        return json.load(fh)["series_store"]


def main():
    snap_path, metric, mode = sys.argv[1], sys.argv[2], sys.argv[3]
    store = load(snap_path)
    if metric not in store:
        print("NOT IN series_store:", metric)
        return
    ent = store[metric]
    dates = ent.get("dates") or []
    values = ent.get("values") or []
    pairs = list(zip(dates, values))
    if mode == "at":
        for d in sys.argv[4:]:
            hit = [(dd, vv) for dd, vv in pairs if dd == d]
            if hit:
                print(metric, d, repr(hit[0][1]))
            else:
                before = [(dd, vv) for dd, vv in pairs if dd < d]
                after = [(dd, vv) for dd, vv in pairs if dd > d]
                b = before[-1] if before else None
                a = after[0] if after else None
                print(metric, d, "NO OBS; nearest<=", b, "nearest>=", a)
    elif mode == "range":
        start, end = sys.argv[4], sys.argv[5]
        for dd, vv in pairs:
            if start <= dd <= end:
                print(metric, dd, repr(vv))
    elif mode == "last":
        n = int(sys.argv[4])
        for dd, vv in pairs[-n:]:
            print(metric, dd, repr(vv))
    elif mode == "tailinfo":
        print("N=", len(dates), "first=", dates[0], "last=", dates[-1])


if __name__ == "__main__":
    main()
