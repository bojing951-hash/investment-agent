# -*- coding: utf-8 -*-
"""rc04: 月频序列近 26 个月路径直算(同比=严格同月去年比)。
用法: rc04_paths.py <snapshot.json>"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_lib as L
snap = L.load(sys.argv[1]); F = L.Face(snap)
def path_level(m, n=27):
    mm = F.monthly(m); ks = sorted(mm)[-n:]
    out = []
    for k in ks:
        y, bs, b, v = L.yoy_level(F, m, k)
        out.append('%s:%s%s' % (k[2:], v, '' if y is None else '(y%.2f)' % y))
    print(m, 'first', F.ss[m]['dates'][0], 'last', F.ss[m]['dates'][-1], 'n', F.n(m))
    print('   ', ' '.join(out))
def path(m, n=27):
    mm = F.monthly(m); ks = sorted(mm)[-n:]
    print(m, 'first', F.ss[m]['dates'][0], 'last', F.ss[m]['dates'][-1], 'n', F.n(m))
    print('   ', ' '.join('%s:%s' % (k[2:], mm[k]) for k in ks))
for m in ('CPI', 'CORE_CPI', 'CORE_PCE', 'INDPRO'):
    path_level(m)
for m in ('UNEMPLOYMENT', 'EA_HICP_YOY', 'CN_PPI_YOY', 'CN_CPI_YOY', 'JP_CPI_YOY', 'JP_CPI_TOKYO_YOY', 'JP_POLICY_RATE', 'CN_LPR_1Y', 'CN_NEW_LOANS'):
    path(m)
mm = F.monthly('CN_PMI_MFG'); ks = sorted(mm)[-26:]
print('CN_PMI_MFG first', F.ss['CN_PMI_MFG']['dates'][0], 'last', F.ss['CN_PMI_MFG']['dates'][-1], 'n', F.n('CN_PMI_MFG'))
print('   ', ' '.join('%s:%s%s' % (k[2:], mm[k], ('(y%.2f)' % L.yoy_level(F, 'CN_PMI_MFG', k)[0]) if isinstance(L.yoy_level(F, 'CN_PMI_MFG', k)[0], float) else '') for k in ks))
above = [(k, v) for k, v in sorted(mm.items()) if k >= '2025-11' and v > 50.0]
flat = [(k, v) for k, v in sorted(mm.items()) if k >= '2025-11' and v == 50.0]
below = [(k, v) for k, v in sorted(mm.items()) if k >= '2025-11' and v < 50.0]
print('CN_PMI since 2025-11 above50:', above, ' flat:', flat, ' below min/max:', min(below, key=lambda x: x[1]), max(below, key=lambda x: x[1]))
print('below values', sorted(set(v for k, v in below)))
for m in ('CN_OMO_7D', 'CN_POLICY_OVERNIGHT', 'ECB_DFR', 'ECB_MRO', 'DFEDTARU', 'DFF'):
    s = F.ss[m]
    print(m, 'n', F.n(m), 'first', s['dates'][0], s['values'][0], 'last', s['dates'][-1], s['values'][-1])
    # change points in last 400 days
    prev = None; ch = []
    for d, v in F.series(m):
        if d < '2025-06-01': prev = (d, v); continue
        if prev is None or v != prev[1]:
            ch.append((d, None if prev is None else prev[1], v))
        prev = (d, v)
    print('    change points since 2025-06-01:', ch)
    if m in ('CN_OMO_7D', 'CN_POLICY_OVERNIGHT'):
        print('    last 6:', F.series(m)[-6:], ' distinct values:', sorted(set(s['values'])))
