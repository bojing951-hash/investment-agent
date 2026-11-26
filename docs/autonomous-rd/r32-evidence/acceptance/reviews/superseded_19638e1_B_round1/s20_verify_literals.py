#!/usr/bin/python3 -I
"""只读自检: 对 PROSE/VERDICT 中未逐点入表的硬编码数字做独立复算(不计入复算点,只核本席引用数)。
用法: s20_verify_literals.py <research_snapshot.json> <metric_registry.json> <report.json> <recompute_points.json>"""
import json
import statistics
import sys

snap_p, reg_p, rep_p, pts_p = sys.argv[1:5]
S = json.load(open(snap_p, encoding='utf-8'))['series_store']
reg = json.load(open(reg_p, encoding='utf-8'))
ms = reg['metrics']
REG = ms if isinstance(ms, dict) else {m.get('metric_id') or m.get('id'): m for m in ms}
rep = json.load(open(rep_p, encoding='utf-8'))
pts = json.load(open(pts_p, encoding='utf-8'))


def at(m, d):
    i = S[m]['dates'].index(d)
    return S[m]['values'][i]


def mavg(m, ym):
    xs = [v for d, v in zip(S[m]['dates'], S[m]['values']) if d.startswith(ym) and v is not None]
    return sum(xs) / len(xs), len(xs)


def on_or_before(m, d):
    best = None
    for dd, v in zip(S[m]['dates'], S[m]['values']):
        if dd <= d and v is not None:
            best = (dd, v)
    return best


# a) USDJPY
a, b = at('USDJPY', '2026-09-18'), at('USDJPY', '2026-11-23')
print('a) USDJPY 2026-09-18=%s 2026-11-23=%s pct=%.4f' % (a, b, (b / a - 1) * 100))
# b) BEI_10Y
w = [(d, v) for d, v in zip(S['BEI_10Y']['dates'], S['BEI_10Y']['values']) if '2025-11-23' <= d <= '2026-11-23' and v is not None]
vals = [v for _, v in w]
print('b) BEI_10Y 12m window n=%d min=%.2f max=%.2f median=%.2f first=%s last=%s' % (
    len(w), min(vals), max(vals), statistics.median(vals), w[0], w[-1]))
for d in ('2026-11-19', '2026-11-20', '2026-11-23', '2026-02-27', '2026-05-04', '2026-02-02', '2026-05-29',
          '2026-01-30', '2026-04-30', '2026-05-27', '2026-08-19', '2026-10-20'):
    print('   BEI_10Y', d, on_or_before('BEI_10Y', d))
for s, e in (('2026-02-02', '2026-05-29'), ('2026-01-30', '2026-04-30'), ('2026-02-27', '2026-05-29'),
             ('2026-02-27', '2026-05-27'), ('2026-02-27', '2026-05-04'), ('2026-10-20', '2026-11-19'),
             ('2026-08-19', '2026-11-19')):
    x, y = on_or_before('BEI_10Y', s), on_or_before('BEI_10Y', e)
    print('   BEI_10Y %s(%s %.2f)→%s(%s %.2f) = %+.1fbp' % (s, x[0], x[1], e, y[0], y[1], (y[1] - x[1]) * 100))
# c) CPI 相邻基期硬算
c = at('CPI', '2026-10-01')
for base in ('2025-09-01', '2025-11-01'):
    print('c) CPI 2026-10 vs base', base, at('CPI', base), '-> %.2f%%' % ((c / at('CPI', base) - 1) * 100))
print('   CPI dates around 2025-10:', [d for d in S['CPI']['dates'] if d.startswith('2025')])
print('   CORE_CPI dates 2025:', [d for d in S['CORE_CPI']['dates'] if d.startswith('2025')])
print('   CORE_CPI YoY 2026-07=%.2f 2026-09=%.2f' % (
    (at('CORE_CPI', '2026-07-01') / at('CORE_CPI', '2025-07-01') - 1) * 100,
    (at('CORE_CPI', '2026-09-01') / at('CORE_CPI', '2025-09-01') - 1) * 100))
print('   CPI YoY 2026-07=%.2f 2026-09=%.4f' % (
    (at('CPI', '2026-07-01') / at('CPI', '2025-07-01') - 1) * 100,
    (at('CPI', '2026-09-01') / at('CPI', '2025-09-01') - 1) * 100))
for m in ('EA_HICP_YOY',):
    print('   ', m, {d: at(m, d) for d in S[m]['dates'] if d >= '2026-06-01'})
print('   CORE_PCE YoY 2026-06=%.2f 2026-09=%.2f' % (
    (at('CORE_PCE', '2026-06-01') / at('CORE_PCE', '2025-06-01') - 1) * 100,
    (at('CORE_PCE', '2026-09-01') / at('CORE_PCE', '2025-09-01') - 1) * 100))
# d) INDPRO
for d in ('2025-07-01', '2025-10-01', '2026-07-01', '2026-09-01', '2026-10-01'):
    print('d) INDPRO', d, at('INDPRO', d))
i7, i9, i10 = at('INDPRO', '2026-07-01'), at('INDPRO', '2026-09-01'), at('INDPRO', '2026-10-01')
print('   INDPRO level 07→10 = %+.3f%% ; m/m 09→10 = %+.3f%%' % ((i10 / i7 - 1) * 100, (i10 / i9 - 1) * 100))
b7, b10 = at('INDPRO', '2025-07-01'), at('INDPRO', '2025-10-01')
print('   INDPRO base 2025-07→2025-10 = %+.3f%%' % ((b10 / b7 - 1) * 100))
print('   INDPRO YoY 2026-07=%.3f 2026-10=%.3f' % ((i7 / b7 - 1) * 100, (i10 / b10 - 1) * 100))
# e) GDP
g2, g3 = at('US_REAL_GDP', '2026-04-01'), at('US_REAL_GDP', '2026-07-01')
print('e) US_REAL_GDP Q3/Q2 level = %+.3f%%' % ((g3 / g2 - 1) * 100))
# f) UNEMPLOYMENT
print('f) UNEMPLOYMENT', {d: at('UNEMPLOYMENT', d) for d in S['UNEMPLOYMENT']['dates'] if d >= '2026-06-01'})
# g) TIPS_10Y / UST_10Y
for d in ('2026-10-20', '2026-10-23', '2026-11-19', '2026-11-23', '2025-11-19', '2026-08-19'):
    print('g) TIPS_10Y', d, on_or_before('TIPS_10Y', d), ' UST_10Y', on_or_before('UST_10Y', d))
x, y = on_or_before('TIPS_10Y', '2026-10-23'), on_or_before('TIPS_10Y', '2026-11-19')
print('   TIPS_10Y 2026-10-23→2026-11-19 = %+.1fbp' % ((y[1] - x[1]) * 100))
# h) SPX
for d in ('2026-08-21', '2026-08-23', '2026-10-20', '2026-10-23', '2026-11-19', '2026-11-23'):
    print('h) SPX', d, on_or_before('SPX', d))
for s, e in (('2026-10-23', '2026-11-19'), ('2026-10-23', '2026-11-23'), ('2026-10-20', '2026-11-23'), ('2026-08-21', '2026-11-23'), ('2026-08-23', '2026-11-19')):
    x, y = on_or_before('SPX', s), on_or_before('SPX', e)
    if x and y:
        print('   SPX %s(%s)→%s(%s) = %+.2f%%' % (s, x[0], e, y[0], (y[1] / x[1] - 1) * 100))
# k) JP monthly averages
for ym in ('2025-11', '2025-12', '2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08', '2026-09', '2026-10'):
    print('k) JP_POLICY_RATE mavg', ym, '%.4f (n=%d)' % mavg('JP_POLICY_RATE', ym))
# l) EA GDP staleness
e = REG.get('EA_REAL_GDP_YOY') or {}
print('l) EA_REAL_GDP_YOY registry lag=', e.get('freshness'), ' status=', e.get('status'))
print('   EA_REAL_GDP_YOY last=', on_or_before('EA_REAL_GDP_YOY', '2026-11-23'))
# i) Gate A points
for p in pts:
    if p['id'] in ('P272', 'P273', 'P274', 'P275', 'P276', 'P277', 'P278', 'P279', 'P280', 'P281', 'P282', 'P283',
                   'P284', 'P285', 'P286', 'P287', 'P288', 'P289', 'P290', 'P291', 'P292', 'P293', 'P217', 'P216',
                   'P219', 'P221', 'P222', 'P223', 'P226', 'P227', 'P228', 'P232', 'P233', 'P241', 'P308', 'P309',
                   'P310', 'P311', 'P312', 'P313', 'P314', 'P315', 'P305'):
        print('i)', p['id'], '|', p['desc'][:70], '|', p['src'][:60], '|', str(p['computed'])[:80], '|', str(p['reported'])[:80], '|', p['ok'])
