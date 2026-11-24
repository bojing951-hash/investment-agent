# -*- coding: utf-8 -*-
"""rc05: 日频序列逐点直算(原始值打印,供比对)。用法: rc05_daily_dump.py <snapshot.json>"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_lib as L
snap = L.load(sys.argv[1]); F = L.Face(snap)
def show(m, dates):
    for d in dates:
        print('  %s @%s = %s' % (m, d, F.at(m, d)))
print('--- BEI/TIPS/UST at cited dates')
for m in ('UST_10Y', 'TIPS_10Y', 'BEI_10Y'):
    show(m, ['2025-11-19', '2026-02-27', '2026-05-04', '2026-06-10', '2026-06-17', '2026-08-19', '2026-10-20', '2026-10-23', '2026-11-19', '2026-11-20', '2026-11-23'])
    s = F.ss[m]; print('   last obs', s['dates'][-1], s['values'][-1], 'n', len(s['dates']))
# BEI 收紧后区间(2026-06-17 起至截止)
w = F.window('BEI_10Y', '2026-06-17', '2026-11-23')
print('BEI_10Y since 2026-06-17: min', min(w, key=lambda x: x[1]), 'max', max(w, key=lambda x: x[1]), 'n', len(w))
# 库内最近一次低于 1.8
below = [(d, v) for d, v in F.series('BEI_10Y') if v < 1.8]
print('BEI_10Y last below 1.8:', below[-1] if below else None, ' n below', len(below))
# 近月窗口: SPX/USDJPY
print('--- SPX / USDJPY / VIX / others at window ends')
for m in ('SPX', 'USDJPY', 'VIX', 'DXY', 'GOLD_F', 'SHCOMP', 'DAX', 'CAC40', 'NIKKEI225', 'BRENT_F', 'HY_OAS', 'USDCNY', 'UST_10Y', 'TIPS_10Y', 'BEI_10Y'):
    s = F.ss[m]
    print(m, 'first', s['dates'][0], 'last', s['dates'][-1], s['values'][-1], 'n', len(s['dates']))
print('--- month-end BRENT_F')
mm = {}
for d, v in F.series('BRENT_F'):
    mm[d[:7]] = (d, v)   # last obs in month
for k in sorted(mm)[-14:]:
    print('   ', k, mm[k])
b = F.at_or_before('BRENT_F', '2026-10-31'); print('BRENT last on/before 2026-10-31', b)
print('BRENT 2026-10-23', F.at('BRENT_F', '2026-10-23'), ' 2026-11-23', F.at('BRENT_F', '2026-11-23'))
print('--- HY_OAS stats')
hy = F.series('HY_OAS')
mx = max(hy, key=lambda x: x[1]); print('HY max', mx, 'first', hy[0], 'last', hy[-1], 'n', len(hy))
ge = [(d, v) for d, v in hy[:-1] if v >= hy[-1][1]]
print('HY last obs >= latest (excluding latest):', ge[-1] if ge else None, ' count', len(ge))
vals = sorted(v for d, v in hy); latest = hy[-1][1]
k = sum(1 for v in vals if v <= latest)
print('HY percentile (<=latest)/n =', k, '/', len(vals), '=', round(100.0 * k / len(vals), 2), ' (<latest):', round(100.0 * sum(1 for v in vals if v < latest) / len(vals), 2))
for d in ('2026-11-13', '2026-11-16', '2026-11-12', '2025-11-19', '2025-11-20'):
    print('   HY at', d, F.at('HY_OAS', d))
print('   HY tail', hy[-8:])
print('--- last obs of each daily series near cutoff')
for m in ('SPX', 'USDJPY', 'VIX', 'DXY', 'GOLD_F', 'SHCOMP', 'DAX', 'CAC40', 'NIKKEI225', 'BRENT_F', 'HY_OAS', 'USDCNY', 'UST_10Y', 'TIPS_10Y', 'BEI_10Y', 'HSI', 'DFEDTARU', 'DFF'):
    print('   ', m, F.series(m)[-3:])
