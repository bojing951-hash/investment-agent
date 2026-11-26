#!/usr/bin/env python3
"""Seat script: print JP_CPI_YOY and EA_HICP_YOY monthly values in a date range (read-only).
Usage: python3 -I peek_jppath.py <snapshot.json> <metric_id> <from YYYY-MM> <to YYYY-MM>
"""
import json
import sys


def main():
    snap_p, mid, y0, y1 = sys.argv[1:5]
    with open(snap_p, encoding="utf-8") as f:
        sn = json.load(f)
    store = sn["series_store"]
    s = store[mid] if isinstance(store, dict) else None
    if s is None:
        print("keys sample", list(store)[:3])
        return
    ds, vs = s["dates"], s["values"]
    prev = None
    for d, v in zip(ds, vs):
        if y0 <= d[:7] <= y1:
            tag = ""
            if prev is not None and v is not None and prev is not None:
                tag = "UP" if v > prev else ("DOWN" if v < prev else "FLAT")
            print(d, v, tag)
        if d[:7] <= y1:
            prev = v


if __name__ == "__main__":
    main()
