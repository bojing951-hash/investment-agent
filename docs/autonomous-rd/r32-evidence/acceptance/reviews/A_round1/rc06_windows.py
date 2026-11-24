# -*- coding: utf-8 -*-
"""rc06: 历史段事后窗(月末口径)/12个月资产窗/近窗/USDCNY/CAC40/TR2 逐日面 直算。
用法: /usr/bin/python3 -I rc06_windows.py <snapshot.json>
"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_lib as L
import rc_points as P

snap = L.load(sys.argv[1])
F = L.Face(snap)
S8 = '⑧历史事后窗'; S5 = '⑤资产窗'; S7 = '⑦传导环数字'

# 期望值(受审稿文字: agent_judgment.history_periods[*].ex_post / 传导面 / 情景面)
EXP = {
    '2025-03': {
        'DFEDTARU': (0.00, -0.25, -0.75), 'UNEMPLOYMENT': (-0.10, 0.20, 0.10),
        'CPI': (0.52, 1.39, 3.29), 'INDPRO': (0.43, 0.62, 0.69),
        'SPX': (10.57, 19.18, 16.33), 'NIKKEI225': (13.67, 26.15, 43.37), 'DAX': (7.88, 7.75, 2.33),
        'SHCOMP': (3.26, 16.40, 16.67), 'GOLD_F': (5.92, 24.03, 48.83), 'DXY': (-7.03, -6.18, -4.08),
        'UST_10Y': (0.01, -0.07, 0.07)},
    '2022-06': {
        'DFEDTARU': (1.50, 2.75, 3.50), 'UNEMPLOYMENT': (-0.10, -0.10, 0.00),
        'CPI': (0.47, 1.31, 3.07), 'INDPRO': (0.27, -1.24, -0.89),
        'SPX': (-5.28, 1.43, 17.57), 'NIKKEI225': (-1.73, -1.13, 25.75), 'DAX': (-5.24, 8.92, 26.32),
        'SHCOMP': (-11.01, -9.10, -5.78), 'GOLD_F': (-7.49, 1.05, 6.76), 'DXY': (7.10, -1.12, -1.70),
        'UST_10Y': (0.85, 0.90, 0.83)},
    '2023-10': {
        'DFEDTARU': (0.00, 0.00, -0.50), 'UNEMPLOYMENT': (-0.20, 0.00, 0.20),
        'CPI': (0.65, 1.73, 2.58), 'INDPRO': (-1.24, -0.22, -0.99),
        'SPX': (15.54, 20.07, 36.04), 'NIKKEI225': (17.59, 24.46, 26.65), 'DAX': (14.13, 21.08, 28.81),
        'SHCOMP': (-7.63, 2.85, 8.65), 'GOLD_F': (2.71, 15.47, 37.86), 'DXY': (-3.18, -0.41, -2.51),
        'UST_10Y': (-0.89, -0.19, -0.60)},
}
DAILY = ('SPX', 'NIKKEI225', 'DAX', 'SHCOMP', 'GOLD_F', 'DXY', 'UST_10Y', 'DFEDTARU')
MONTHLY = ('UNEMPLOYMENT', 'CPI', 'INDPRO')


def me_obs(name, ym):
    return F.at_or_before(name, L.month_end(ym))


def mv(name, ym):
    return F.monthly(name).get(ym)


table = {}
for cand, exp in EXP.items():
    for m in ('3', '6', '12'):
        end_ym = L.add_months(cand, int(m))
        table.setdefault(cand, {})[m] = {}
        for s in DAILY:
            if s not in exp:
                continue
            a = me_obs(s, cand); b = me_obs(s, end_ym)
            if a is None or b is None:
                table[cand][m][s] = None
                continue
            if s in ('UST_10Y', 'DFEDTARU'):
                v = (b[1] - a[1])  # 受审稿以 pp 记(非 bp)
            else:
                v = L.pct(a[1], b[1])
            table[cand][m][s] = v
        for s in MONTHLY:
            a = mv(s, cand); b = mv(s, end_ym)
            if a is None or b is None:
                table[cand][m][s] = None
            elif s == 'UNEMPLOYMENT':
                table[cand][m][s] = b - a
            else:
                table[cand][m][s] = L.pct(a, b)

for cand in EXP:
    print('== 候选', cand)
    for s in [x for x in EXP[cand]]:
        line = '%-12s' % s
        for i, m in enumerate(('3', '6', '12')):
            v = table[cand][m][s]
            e = EXP[cand][s][i]
            ok = P.eq(v, e)
            line += ' | %s: 直算 %s 受审 %s %s' % (m, ('%.4f' % v) if v is not None else None, e, 'OK' if ok else 'MISMATCH')
            P.add(S8, 'snapshot.series_store.%s(月末口径: 候选月末最后观测→候选月+%s月末最后观测; pp)' % (s, m),
                  round(v, 4) if v is not None else None, e, ok,
                  where='agent_judgment.history_periods[%s].ex_post.%sm' % (cand, m))
        print(line)

# ---------- 起止明细(供文字核对) ----------
print('== 月末起止明细')
for cand in EXP:
    for m in ('3', '6', '12'):
        end_ym = L.add_months(cand, int(m))
        for s in DAILY:
            if s in EXP[cand]:
                a = me_obs(s, cand); b = me_obs(s, end_ym)
                print(cand, m, s, a, '->', b)
        for s in MONTHLY:
            print(cand, m, s, mv(s, cand), '@', cand, '->', mv(s, end_ym), '@', end_ym)

# ---------- 12个月资产窗 / 近窗 ----------
def w(name, d0, d1):
    a = F.at_or_before(name, d0); b = F.at_or_before(name, d1)
    return a, b


print('== 12个月资产窗 2025-11-19 -> 2026-11-19(共同交易日)')
for s, e in (('SPX', 8.03), ('NIKKEI225', 22.47), ('DAX', 9.93), ('GOLD_F', None), ('DXY', None), ('VIX', None), ('SHCOMP', None)):
    a, b = w(s, '2025-11-19', '2026-11-19')
    v = L.pct(a[1], b[1])
    print(s, a, b, '%.4f' % v)
    if e is not None:
        P.add(S7, 'snapshot.series_store.%s(2025-11-19→2026-11-19)' % s, round(v, 2), e, P.eq(v, e),
              where='TR1.step3 观察事实(12个月窗对照)')

print('== SPX 近窗')
for d0, e in (('2026-10-20', -6.96), ('2026-08-19', -6.90)):
    a, b = w('SPX', d0, '2026-11-19')
    v = L.pct(a[1], b[1])
    print('SPX', d0, a, '->', b, '%.4f' % v)
    P.add(S7, 'snapshot.series_store.SPX(%s→2026-11-19)' % d0, round(v, 2), e, P.eq(v, e),
          where='TR1.step3 观察事实(窗口对照)')

print('== USDCNY 12个月')
a, b = w('USDCNY', '2025-11-19', '2026-11-19')
v = L.pct(a[1], b[1])
print(a, b, '%.4f' % v)
P.add(S7, 'snapshot.series_store.USDCNY(2025-11-19→2026-11-19)', {'from': a, 'to': b, 'chg_pct': round(v, 2)},
      {'from': 7.1075, 'to': 6.6676, 'chg_pct': -6.19}, (P.eq(a[1], 7.1075) and P.eq(b[1], 6.6676) and P.eq(v, -6.19)),
      where='L3 C3 解释C 汇率腿')
for s, e in (('USDCNY', None),):
    pass

print('== 同日收盘口径 2026-10-23 -> 2026-11-20')
for s, e in (('SPX', -9.36), ('DAX', -1.50), ('CAC40', 1.86), ('NIKKEI225', -9.98), ('VIX', 84.52)):
    a, b = w(s, '2026-10-23', '2026-11-20')
    v = L.pct(a[1], b[1])
    print(s, a, b, '%.4f' % v, 'OK' if P.eq(v, e) else 'MISMATCH')
    P.add(S5, 'snapshot.series_store.%s(2026-10-23→2026-11-20 同日收盘口径)' % s, round(v, 2), e, P.eq(v, e),
          where='TR1.step3 观察事实 / quality_gate_notes(同日收盘口径对照)')

print('== 月窗(引擎 asset_moves 口径) 逐项')
for s, e, d1 in (('SPX', -5.51, '2026-11-23'), ('SHCOMP', -4.11, '2026-11-23'), ('DAX', 0.11, '2026-11-23'),
                 ('NIKKEI225', -9.98, '2026-11-20'), ('VIX', 38.87, '2026-11-23'), ('DXY', 2.23, '2026-11-23'),
                 ('GOLD_F', -8.05, '2026-11-23')):
    a, b = w(s, '2026-10-23', d1)
    v = L.pct(a[1], b[1])
    print(s, a, b, '%.4f' % v, 'OK' if P.eq(v, e) else 'MISMATCH')
    P.add(S5, 'snapshot.series_store.%s(2026-10-23→%s)' % (s, d1), round(v, 2), e, P.eq(v, e),
          where='agent_judgment.asset_returns_echo / TR1.step3 观察事实')

# UST_10Y 月窗
a, b = w('UST_10Y', '2026-10-23', '2026-11-19')
v = L.pct(a[1], b[1])
print('UST_10Y pct', a, b, '%.4f' % v)
P.add(S5, 'snapshot.series_store.UST_10Y(2026-10-23→2026-11-19) %', round(v, 1), 0.8, P.eq(v, 0.8),
      where='agent_judgment.asset_returns_echo[UST_10Y]')

# ---------- TR2 逐日面 ----------
print('== TR2 SPX x USDJPY 逐日面 2026-10-23 基 -> 2026-11-23')
spx = F.window('SPX', '2026-10-23', '2026-11-23')
uj = dict(F.window('USDJPY', '2026-10-23', '2026-11-23'))
pairs = []
for d, v in spx:
    if d in uj:
        pairs.append((d, v, uj[d]))
print('共同交易日数(含基日):', len(pairs))
base = pairs[0]
ds = []; du = []
for d, v, u in pairs[1:]:
    ds.append((d, L.pct(pairs[pairs.index((d, v, u)) - 1][1], v)))
    du.append((d, L.pct(pairs[pairs.index((d, v, u)) - 1][2], u)))
n = len(ds)
xs = [x[1] for x in ds]; ys = [y[1] for y in du]
mx = sum(xs) / n; my = sum(ys) / n
cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / n
corr = cov / (math.sqrt(sum((x - mx) ** 2 for x in xs) / n) * math.sqrt(sum((y - my) ** 2 for y in ys) / n))
same = sum(1 for x, y in zip(xs, ys) if (x > 0) == (y > 0))
down = [(x, y) for x, y in zip(xs, ys) if x < 0]
up = [(x, y) for x, y in zip(xs, ys) if x > 0]
comp_down = (math.prod(1 + y / 100 for x, y in down) - 1) * 100
comp_up = (math.prod(1 + y / 100 for x, y in up) - 1) * 100
print('n', n, 'corr %.4f' % corr, 'same', same, 'down', len(down), 'down&ujdown', sum(1 for x, y in down if y < 0),
      'down&ujup', sum(1 for x, y in down if y > 0), 'up', len(up), 'up&ujup', sum(1 for x, y in up if y > 0),
      'comp_down %.4f' % comp_down, 'comp_up %.4f' % comp_up)
print('逐日:', [(d, round(x, 2), round(y, 2)) for (d, x), (d2, y) in zip(ds, du)])
top4 = sorted(ds, key=lambda t: t[1])[:4]
print('四个最大单日跌幅:', [(d, round(x, 2), round(dict(du)[d], 2)) for d, x in top4])
P.add(S7, 'snapshot.series_store.SPX×USDJPY 逐日(2026-10-26..2026-11-23)',
      {'n_days': n, 'corr': round(corr, 2), 'same_dir': same, 'spx_down_days': len(down),
       'down&uj_down': sum(1 for x, y in down if y < 0), 'down&uj_up': sum(1 for x, y in down if y > 0),
       'spx_up_days': len(up), 'up&uj_up': sum(1 for x, y in up if y > 0),
       'uj_comp_on_down': round(comp_down, 2), 'uj_comp_on_up': round(comp_up, 2),
       'top4_drops': [(d, round(x, 2), round(dict(du)[d], 2)) for d, x in top4]},
      {'n_days': 21, 'corr': 0.19, 'same_dir': 16, 'spx_down_days': 12, 'down&uj_down': 9, 'down&uj_up': 3,
       'spx_up_days': 9, 'up&uj_up': 7, 'uj_comp_on_down': 0.16, 'uj_comp_on_up': 1.66,
       'top4_drops': [('2026-11-05', -0.07), ('2026-11-20', 0.20), ('2026-11-19', -0.08), ('2026-11-16', -0.06)]},
      (n == 21 and P.eq(corr, 0.19) and same == 16 and len(down) == 12 and sum(1 for x, y in down if y < 0) == 9
       and sum(1 for x, y in down if y > 0) == 3 and len(up) == 9 and sum(1 for x, y in up if y > 0) == 7
       and P.eq(comp_down, 0.16) and P.eq(comp_up, 1.66)
       and [t[0] for t in top4] == ['2026-11-05', '2026-11-20', '2026-11-19', '2026-11-16']
       and all(P.eq(dict(du)[d], e) for (d, _), e in zip(top4, [-0.07, 0.20, -0.08, -0.06]))),
      where='TR2.step1 观察事实/对质注记(逐日面)')
a, b = w('USDJPY', '2026-10-23', '2026-11-23')
v = L.pct(a[1], b[1])
print('USDJPY 窗', a, b, '%.4f' % v)
P.add(S7, 'snapshot.series_store.USDJPY(2026-10-23→2026-11-23)', {'from': a, 'to': b, 'chg': round(v, 2)},
      {'from': 156.49, 'to': 159.35, 'chg': 1.82}, (P.eq(a[1], 156.49) and P.eq(b[1], 159.35) and P.eq(v, 1.82)),
      where='TR2.step1 观察事实')
print('tally', P.tally())
