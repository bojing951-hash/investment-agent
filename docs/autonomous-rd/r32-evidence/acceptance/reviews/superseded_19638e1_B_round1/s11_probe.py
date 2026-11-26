# -*- coding: utf-8 -*-
"""只读探查: 指定日期值与区间。用法: python3 -I s11_probe.py <snapshot>"""
import json, sys
snap = json.load(open(sys.argv[1], encoding='utf-8'))
ss = snap['series_store']
def S(m): return dict(zip(ss[m]['dates'], ss[m]['values']))
def near(m, d):
    s = S(m); ds = sorted(s)
    # nearest on/before and on/after
    bef = [x for x in ds if x <= d]; aft = [x for x in ds if x >= d]
    return (bef[-1], s[bef[-1]] if bef else None), (aft[0], s[aft[0]] if aft else None)
print("## exact / nearest values at key dates")
for m, d in [('UST_10Y','2026-08-19'),('TIPS_10Y','2026-08-19'),('BEI_10Y','2026-08-19'),
             ('UST_10Y','2025-11-19'),('TIPS_10Y','2025-11-19'),('BEI_10Y','2025-11-19'),
             ('SPX','2026-08-19'),('VIX','2026-08-19'),('SPX','2026-11-20'),('VIX','2026-11-20'),
             ('BEI_10Y','2026-02-27'),('BEI_10Y','2026-05-04'),('BEI_10Y','2026-02-01'),('BEI_10Y','2026-05-01'),('BEI_10Y','2026-02-28'),('BEI_10Y','2026-05-31'),
             ('TIPS_10Y','2026-08-19'),('USDJPY','2026-08-19'),('EURUSD','2026-08-19'),('EURUSD','2026-08-23'),('USDJPY','2026-08-23'),('DXY','2026-08-19'),('GOLD_F','2026-08-19')]:
    s = S(m)
    print("%-9s %s exact=%s  before=%s  after=%s" % (m, d, s.get(d), near(m, d)[0], near(m, d)[1]))
print("\n## BEI_10Y 2026-01-15..2026-06-05 (weekly-ish sample: all)")
b = S('BEI_10Y')
for d in sorted(b):
    if '2026-02-20' <= d <= '2026-03-10' or '2026-04-27' <= d <= '2026-05-12':
        print("  ", d, b[d])
import statistics
def rng(m, d0, d1):
    s = S(m); xs = [(d, v) for d, v in s.items() if d0 <= d <= d1 and v is not None]
    vals = [v for _, v in xs]
    mn = min(xs, key=lambda t: t[1]); mx = max(xs, key=lambda t: t[1])
    last = xs[-1]
    rank = sum(1 for v in vals if v <= last[1]) / len(vals)
    return dict(n=len(xs), min=mn, max=mx, last=last, pct_rank_of_last=round(rank, 3), median=statistics.median(vals))
print("\n## 12-month ranges (2025-11-23..2026-11-23)")
for m in ['USDJPY', 'EURUSD', 'BEI_10Y', 'TIPS_10Y', 'UST_10Y', 'SPX', 'GOLD_F', 'VIX', 'DXY']:
    print("%-9s" % m, rng(m, '2025-11-23', '2026-11-23'))
print("\n## 3-month changes (2026-08-19 -> latest)")
for m in ['USDJPY', 'EURUSD', 'DXY', 'GOLD_F', 'SPX', 'VIX', 'NIKKEI225', 'UST_10Y', 'TIPS_10Y', 'BEI_10Y']:
    s = S(m); a = s.get('2026-08-19'); z = s[sorted(s)[-1]]; dl = sorted(s)[-1]
    if a is None:
        bb = near(m, '2026-08-19')[0]; a = bb[1]; print("  (no 08-19 for %s; nearest before %s)" % (m, bb))
    print("  %-9s 2026-08-19=%s -> %s=%s  chg=%+.2f%%" % (m, a, dl, z, (z/a - 1) * 100))
