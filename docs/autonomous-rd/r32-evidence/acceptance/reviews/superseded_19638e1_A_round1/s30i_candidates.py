#!/usr/bin/python3 -I
"""Read-only: print the engine turning-candidate face and recompute each candidate's
before/after/delta from series_store (level series -> year-on-year percent with the
12-month-earlier observation; yoy series -> the observation itself).

Usage:
  python3 -I s30i_candidates.py <report.json> <research_snapshot.json>
"""
import json
import sys


def yoy_series(store, metric):
    d = store.get(metric)
    if not d:
        return None
    dates = d.get('dates') or []
    vals = d.get('values') or []
    if metric.endswith('_YOY'):
        return dict(zip(dates, vals))
    out = {}
    idx = {dt: i for i, dt in enumerate(dates)}
    for dt, v in zip(dates, vals):
        if v is None or dt.endswith('-01') is False and len(dates) > 300:
            continue
        y, m = dt[:4], dt[5:7]
        prev = '%d-%s-01' % (int(y) - 1, m)
        j = idx.get(prev)
        if j is None:
            for cand in idx:
                if cand.startswith(prev[:7]):
                    j = idx[cand]
                    break
        if j is not None and vals[j] not in (None, 0):
            out[dt] = (v / vals[j] - 1.0) * 100.0
    return out


def main():
    rep = json.load(open(sys.argv[1], encoding='utf-8'))
    snap = json.load(open(sys.argv[2], encoding='utf-8'))
    store = snap['series_store']
    plan = rep.get('research_plan', {})
    tc = plan.get('turning_candidates', {})
    print('turning_candidates keys:', sorted(tc.keys()))
    for k in tc:
        if k != 'candidates':
            print('  %s = %s' % (k, json.dumps(tc[k], ensure_ascii=False)[:300]))
    for i, c in enumerate(tc.get('candidates', [])):
        print('--- candidate[%d]' % i)
        print(json.dumps(c, ensure_ascii=False, indent=1)[:1500])
        metric = c.get('metric_id')
        w = c.get('window') or c.get('window_months') or {}
        ys = yoy_series(store, metric)
        print('  seat yoy series n=%s' % (len(ys) if ys else None))
        if ys:
            ks = sorted(ys)
            print('  seat yoy 2025-11..2026-10:', [(k[0:7], round(ys[k], 4)) for k in ks if '2025-11' <= k[:7] <= '2026-10'])
            best = None
            for a in ks:
                for b in ks:
                    if '2025-11' <= a[:7] and b[:7] <= '2026-11' and 1 <= (int(b[:4]) * 12 + int(b[5:7])) - (int(a[:4]) * 12 + int(a[5:7])) <= 3 and ys[b] is not None and ys[a] is not None:
                        dd = ys[b] - ys[a]
                        if best is None or abs(dd) > abs(best[3]):
                            best = (a, b, (ys[a], ys[b]), dd)
            print('  seat max |delta| within <=3-month windows: %s' % (best,))
    print('-- done')


if __name__ == '__main__':
    main()
