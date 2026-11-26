#!/usr/bin/python3
"""Seat script: print tail (and optional head) observations of series from the frozen snapshot.
Usage: /usr/bin/python3 -I s03_series_tail.py <snapshot.json> <N_tail> <metric1> [metric2 ...]
Add prefix "head:" to a metric name to also print first 3 obs.
Read-only.
"""
import json
import sys


def main():
    path = sys.argv[1]
    n_tail = int(sys.argv[2])
    metrics = sys.argv[3:]
    with open(path, "r", encoding="utf-8") as fh:
        snap = json.load(fh)
    ss = snap["series_store"]
    print("research_as_of=%s target_date=%s timezone=%s" % (
        snap.get("research_as_of"), snap.get("target_date"), snap.get("timezone")))
    for m in metrics:
        show_head = False
        name = m
        if m.startswith("head:"):
            show_head = True
            name = m[5:]
        if name not in ss:
            print("## %s : NOT IN series_store" % name)
            continue
        ser = ss[name]
        dates = ser.get("dates") or []
        vals = ser.get("values") or []
        other = {k: v for k, v in ser.items() if k not in ("dates", "values")}
        print("## %s  n=%d  first=%s last=%s  extra_keys=%s" % (
            name, len(dates), dates[0] if dates else None, dates[-1] if dates else None,
            json.dumps(other, ensure_ascii=False)[:300]))
        if show_head:
            for d, v in list(zip(dates, vals))[:3]:
                print("   HEAD %s = %r" % (d, v))
        for d, v in list(zip(dates, vals))[-n_tail:]:
            print("   %s = %r" % (d, v))


if __name__ == "__main__":
    main()
