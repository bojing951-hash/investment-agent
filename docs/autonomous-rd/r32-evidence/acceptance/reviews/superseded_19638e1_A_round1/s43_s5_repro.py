#!/usr/bin/python3 -I
"""Seat-internal, read-only: try to reproduce the S5_compare figure rendered in the reader reports as
"US_REAL_GDP×UNEMPLOYMENT 日收益×日变化 pearson = -0.8936 (n=37)".  The engine face (report.json steps[60])
declares month-grid alignment, change_basis a=pct / b=pp and n_change_pairs=37, i.e. a correlation of
changes between consecutive common observations, not of daily returns.  Variants are computed from the
frozen snapshot; the only file written is the info file argv[3] (inside the seat directory).

Usage:
  python3 -I s43_s5_repro.py <research_snapshot.json> <report.json> <out.txt>
"""
import json
import math
import sys


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    syy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return sxy / (sxx * syy)


def main():
    snap = json.load(open(sys.argv[1], encoding='utf-8'))
    rep = json.load(open(sys.argv[2], encoding='utf-8'))
    store = snap['series_store']
    env = rep['steps'][60]['envelope']
    blob = json.dumps(env, ensure_ascii=False)
    assert '"pearson_returns": -0.8935653981522128' in blob and '"n_change_pairs": 37' in blob
    g, u = store['US_REAL_GDP'], store['UNEMPLOYMENT']
    gd = dict(zip(g['dates'], g['values']))
    ud = dict(zip(u['dates'], u['values']))
    common = [d for d in gd if d in ud and gd[d] is not None and ud[d] is not None]
    out = ['common observation months (GDP quarter-start months that are also unemployment observations): %d '
           '(%s..%s)' % (len(common), common[0], common[-1])]
    a_pct, b_pp, pairs = [], [], []
    for p, q in zip(common, common[1:]):
        if gd[p] in (None, 0) or ud[p] is None or gd[q] is None or ud[q] is None:
            continue
        a_pct.append((gd[q] / gd[p] - 1.0) * 100.0)   # GDP level, percent change between common observations
        b_pp.append(ud[q] - ud[p])                     # unemployment rate, percentage-point change
        pairs.append((p, q))
    r = pearson(a_pct, b_pp)
    out.append('variant A: GDP level pct change x UNEMPLOYMENT pp change between consecutive common months: '
               'pearson=%.10f n=%d' % (r, len(a_pct)))
    by, byb = [], []
    for x, (p, q) in zip(b_pp, pairs):
        base = '%04d%s' % (int(q[:4]) - 1, q[4:])
        if base in gd and gd[base]:
            by.append((gd[q] / gd[base] - 1.0) * 100.0)
            byb.append(x)
    out.append('variant B: GDP yoy (vs same quarter a year earlier) x UNEMPLOYMENT pp change: pearson=%.4f n=%d' % (
        pearson(by, byb), len(by)))
    out.append('engine face: pearson_returns=%s n_change_pairs=%s change_basis=%s' % (
        '-0.8935653981522128', 37, json.dumps(env.get('change_basis') if 'change_basis' in env else 'a=pct,b=pp')))
    # locate the declared fields wherever they sit inside the envelope
    def find(o, key):
        if isinstance(o, dict):
            if key in o:
                yield o[key]
            for vv in o.values():
                for x in find(vv, key):
                    yield x
        elif isinstance(o, list):
            for vv in o:
                for x in find(vv, key):
                    yield x
    for key in ('pearson_returns', 'n_change_pairs', 'change_basis', 'n_common_observations', 'mode'):
        out.append('face %s = %s' % (key, json.dumps(list(find(env, key)), ensure_ascii=False)[:200]))
    out.append('reproduced = %s (|diff| < 1e-9)' % (abs(r - (-0.8935653981522128)) < 1e-9))
    text = '\n'.join(out)
    open(sys.argv[3], 'w', encoding='utf-8').write(text + '\n')
    print(text)


if __name__ == '__main__':
    main()
