#!/usr/bin/python3 -I
"""Read-only: check that the scenario / chain falsification thresholds are observable in the frozen
series (indicator present, threshold inside the range the series has actually printed) and print the
latest reading with its observation date.  Level series are converted to year-on-year percent with
the same-month observation one year earlier as the base.

Usage:
  python3 -I s37_threshold_history.py <research_snapshot.json>
"""
import json
import sys

CUTOFF = '2026-11-23'


def monthly_yoy(store, metric):
    d = store[metric]
    dates, vals = d.get('dates') or [], d.get('values') or []
    idx = {dt: i for i, dt in enumerate(dates)}
    out = {}
    for dt, v in zip(dates, vals):
        if not dt.endswith('-01'):
            continue
        if metric.endswith('_YOY'):
            out[dt[:7]] = v
            continue
        j = idx.get('%04d-%s-01' % (int(dt[:4]) - 1, dt[5:7]))
        base = vals[j] if j is not None else None
        out[dt[:7]] = None if (v is None or base in (None, 0)) else (v / base - 1.0) * 100.0
    return out


def main():
    snap = json.load(open(sys.argv[1], encoding='utf-8'))
    store = snap['series_store']
    checks = [
        ('SCN1 falsification', 'CPI', 'yoy', 2.5, 'below'),
        ('SCN1 falsification (secondary)', 'CORE_PCE', 'yoy', 2.8, 'below'),
        ('SCN1 trigger', 'CPI', 'yoy', 3.5, 'above'),
        ('SCN2 falsification', 'BEI_10Y', 'level', 1.8, 'below'),
        ('M1 policy link falsification', 'CPI', 'yoy', 2.5, 'below'),
        ('M1 asset link falsification', 'HY_OAS', 'level', 4.61, 'above'),
    ]
    for name, metric, kind, thr, side in checks:
        d = store[metric]
        dates, vals = d['dates'], d['values']
        pts = [(dt, v) for dt, v in zip(dates, vals) if v is not None and dt <= CUTOFF]
        last = pts[-1]
        if kind == 'level':
            s = pts
        else:
            y = monthly_yoy(store, metric)
            s = [(k + '-01', v) for k, v in sorted(y.items()) if v is not None and k + '-01' <= CUTOFF]
        hits = [p for p in s if (p[1] < thr if side == 'below' else p[1] >= thr)]
        lo, hi = min(s, key=lambda p: p[1]), max(s, key=lambda p: p[1])
        print('%s | %s %s threshold %s %s | n=%d first=%s last=%s(%s) | min=%s@%s max=%s@%s | '
              'last time condition held: %s | held in last 24 obs: %d of %d' % (
                  name, metric, kind, side, thr, len(s), s[0][0], last[0], last[1],
                  round(lo[1], 4), lo[0], round(hi[1], 4), hi[0],
                  ('%s(%s)' % (hits[-1][0], round(hits[-1][1], 4))) if hits else 'never',
                  sum(1 for p in s[-24:] if (p[1] < thr if side == 'below' else p[1] >= thr)),
                  len(s[-24:])))
    # daily co-movement threshold series presence for the chain falsification indicators
    for metric in ('USDJPY', 'BRENT_F', 'TIPS_10Y'):
        d = store[metric]
        pts = [(dt, v) for dt, v in zip(d['dates'], d['values']) if v is not None]
        print('%s present: n=%d first=%s last=%s last_value=%s' % (metric, len(pts), pts[0][0], pts[-1][0], pts[-1][1]))


if __name__ == '__main__':
    main()
