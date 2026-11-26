#!/usr/bin/env python3
"""Seat script: print daily closes and day-over-day % changes for the daily series in a date range (read-only).
Usage: python3 -I peek_daily_window.py <snapshot.json> <from YYYY-MM-DD> <to YYYY-MM-DD> <metric_id> [<metric_id> ...]
"""
import json
import sys


def main():
    snap_p, d0, d1 = sys.argv[1:4]
    mids = sys.argv[4:]
    with open(snap_p, encoding="utf-8") as f:
        sn = json.load(f)
    store = sn["series_store"]
    for mid in mids:
        s = store[mid]
        rows = [(d, v) for d, v in zip(s["dates"], s["values"]) if d0 <= d <= d1 and v is not None]
        out = []
        prev = None
        for d, v in rows:
            chg = "" if (prev is None or prev == 0) else ("%+.2f%%" % (((v / prev) - 1.0) * 100))
            out.append("%s %.4g %s" % (d[5:], v, chg))
            prev = v
        print(mid, "|", " ; ".join(out))


if __name__ == "__main__":
    main()
