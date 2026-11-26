#!/usr/bin/python3 -I
"""Read-only: try to reproduce the engine compare face (S5) pearson of changes on a month grid.

Usage:
  python3 -I s26_compare_face.py <snapshot.json> <report.json>
"""
import json
import math
import sys


def main():
    snap = json.load(open(sys.argv[1], encoding='utf-8'))
    rep = json.load(open(sys.argv[2], encoding='utf-8'))
    store = snap['series_store']
    g = store['US_REAL_GDP']
    u = store['UNEMPLOYMENT']
    gm = {}
    for d, v in zip(g['dates'], g['values']):
        if v is not None:
            gm[d[:7]] = v
    um = {}
    for d, v in zip(u['dates'], u['values']):
        if v is not None:
            um[d[:7]] = v
    keys = sorted(k for k in gm if k in um)
    print('common month keys n=%d first=%s last=%s' % (len(keys), keys[0], keys[-1]))
    xs, ys = [], []
    for a, b in zip(keys, keys[1:]):
        xs.append((gm[b] / gm[a] - 1.0) * 100.0)
        ys.append(um[b] - um[a])
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    print('seat: n_change_pairs=%d pearson(GDP pct chg, UNEMP pp chg)=%.10f' % (n, sxy / math.sqrt(sxx * syy)))
    d = rep['steps'][60]['envelope']['data']
    print('engine: n_level=%s n_change_pairs=%s pearson_returns=%s change_basis=%s common=%s..%s a_dropped=%s b_dropped=%s' % (
        d['alignment']['n_level_observations'], d['n_change_pairs'], d['pearson_returns'], d['change_basis'],
        d['alignment']['common_first'], d['alignment']['common_last'], d['alignment']['a_dropped'], d['alignment']['b_dropped']))
    gaps = [(a, b) for a, b in zip(keys, keys[1:]) if (int(b[:4]) * 12 + int(b[5:7])) - (int(a[:4]) * 12 + int(a[5:7])) > 3]
    print('gaps > 1 quarter in common keys:', gaps)
    print('rendered in reader report? checked separately by grep')


if __name__ == '__main__':
    main()
