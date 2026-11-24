#!/usr/bin/python3
"""Seat script: series lookup utilities on the frozen snapshot (read-only).
Usage:
  /usr/bin/python3 -I s04_series_tails.py <snapshot.json> at <metric>:<date>[,<date>...] ...
  /usr/bin/python3 -I s04_series_tails.py <snapshot.json> window <metric>:<from>..<to> ...
  /usr/bin/python3 -I s04_series_tails.py <snapshot.json> changes <metric>:<from>..<to> ...
`at`     -> exact-date lookup (None if absent) + nearest obs on/before the date
`window` -> every observation in [from, to]
`changes`-> observations whose value differs from the previous observation (within [from,to])
"""
import json
import sys


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)["series_store"]


def idx(dates):
    return {d: i for i, d in enumerate(dates)}


def on_or_before(dates, day):
    best = None
    for d in dates:
        if d <= day:
            best = d
        else:
            break
    return best


def main():
    ss = load(sys.argv[1])
    mode = sys.argv[2]
    for spec in sys.argv[3:]:
        metric, _, rest = spec.partition(":")
        if metric not in ss:
            print("## %s NOT IN series_store" % metric)
            continue
        dates = ss[metric]["dates"]
        vals = ss[metric]["values"]
        ix = idx(dates)
        if mode == "at":
            for day in rest.split(","):
                prev = on_or_before(dates, day)
                nxt = None
                for d in dates:
                    if d > day:
                        nxt = d
                        break
                print("%s @%s exact=%s | on_or_before=%s->%s | next=%s->%s" % (
                    metric, day,
                    vals[ix[day]] if day in ix else None,
                    prev, vals[ix[prev]] if prev else None,
                    nxt, vals[ix[nxt]] if nxt else None))
        elif mode == "window":
            a, b = rest.split("..")
            print("## %s window %s..%s" % (metric, a, b))
            for d, v in zip(dates, vals):
                if a <= d <= b:
                    print("   %s = %r" % (d, v))
        elif mode == "changes":
            a, b = rest.split("..")
            print("## %s changes %s..%s" % (metric, a, b))
            for i in range(1, len(dates)):
                if a <= dates[i] <= b and vals[i] != vals[i - 1]:
                    print("   %s: %r -> %r" % (dates[i], vals[i - 1], vals[i]))
        elif mode == "yoy":
            # yoy of level series: metric is a level; print yoy for each obs with same month previous year
            print("## %s yoy" % metric)
            for i, d in enumerate(dates):
                y, m = d[:4], d[5:7]
                base = "%d-%s-01" % (int(y) - 1, m)
                if base in ix and d >= "2025-01-01":
                    v = vals[i]
                    b = vals[ix[base]]
                    if v is None or b is None:
                        continue
                    print("   %s yoy=%.4f%% (base %s=%r, cur=%r)" % (d, (v / b - 1) * 100.0, base, b, v))


if __name__ == "__main__":
    main()
