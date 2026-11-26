# -*- coding: utf-8 -*-
# r20_points.py — E 利率分解 / F 资产与汇率窗
# 用法: /usr/bin/python3 -I r20_points.py <RUN_DIR> <SNAPSHOT_JSON> <OUT_JSON>
import sys, os, json, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from r00_common import *

RUN, SNAP, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
sn = Snap(load(SNAP))
aj = load(os.path.join(RUN, 'agent_judgment.json'))
PTS = []
EX = {}
CAT = ['']


def cat(c):
    CAT[0] = c


def P(pid, where, key, comp, rep, note='', tol=None):
    disp = round(comp, 6) if isinstance(comp, float) else comp
    ok = same(comp, rep, tol)
    PTS.append({'id': pid, 'cat': CAT[0], 'where': where, 'key': key, 'computed': disp,
                'reported': rep, 'ok': bool(ok), 'note': note})
    print('%s|%s|%s|comp=%s|rep=%s|%s|%s' % ('OK' if ok else 'XX', pid, CAT[0], disp, rep, where, note))
    return ok


def mean(xs):
    return sum(xs) / float(len(xs)) if xs else None


def month_mean(sid, ym):
    y, m = [int(x) for x in ym.split('-')]
    return mean([b for a, b in sn.series(sid) if a.year == y and a.month == m])


d1a, d1b = D('2026-10-20'), D('2026-11-19')
d3a = D('2026-08-19')
d12a = D('2025-11-19')

# ---------------- E 利率分解 ----------------
cat('E 利率分解')
u = {d: sn.val('UST_10Y', d) for d in (d12a, d3a, d1a, d1b)}
t = {d: sn.val('TIPS_10Y', d) for d in (d12a, d3a, d1a, d1b)}
be = {d: sn.val('BEI_10Y', d) for d in (d12a, d3a, d1a, d1b)}
EX['rates_endpoints'] = {'UST_10Y': {k.isoformat(): v for k, v in u.items()}, 'TIPS_10Y': {k.isoformat(): v for k, v in t.items()},
                         'BEI_10Y': {k.isoformat(): v for k, v in be.items()}}
P('E01', '传导环2「美国十年期名义利率 2026-11-19 报 5.04%」', sn.key('UST_10Y', d1b), u[d1b], 5.04)
P('E02', '传导环1「BEI_10Y 水平为 2.15(观测 2026-11-20)」', sn.key('BEI_10Y', '2026-11-20'), sn.val('BEI_10Y', '2026-11-20'), 2.15)
P('E03', '传导环2「实际利率(TIPS_10Y) 2.88」(rates_decomposition 水平)', sn.key('TIPS_10Y', d1b), t[d1b], 2.88)
P('E04', '传导环2「近一月(2026-10-20→2026-11-19)名义 -8bp」', 'UST_10Y 2026-11-19 − 2026-10-20 (bp)', diff_bp(u[d1a], u[d1b]), -8)
P('E05', '「TIPS_10Y +11bp」', 'TIPS_10Y 2026-11-19 − 2026-10-20 (bp)', diff_bp(t[d1a], t[d1b]), 11)
P('E06', '「BEI_10Y -19bp」', 'BEI_10Y 2026-11-19 − 2026-10-20 (bp)', diff_bp(be[d1a], be[d1b]), -19)
P('E07', '传导环2「三个月窗(2026-08-19→2026-11-19)名义 +39bp」', 'UST_10Y 2026-11-19 − 2026-08-19 (bp)', diff_bp(u[d3a], u[d1b]), 39)
P('E08', '「实际 +53bp」', 'TIPS_10Y 2026-11-19 − 2026-08-19 (bp)', diff_bp(t[d3a], t[d1b]), 53)
P('E09', '「盈亏平衡 -14bp」', 'BEI_10Y 2026-11-19 − 2026-08-19 (bp)', diff_bp(be[d3a], be[d1b]), -14)
P('E10', '传导环2「12 个月窗(2025-11-19→2026-11-19)名义 +91bp」', 'UST_10Y 2025-11-19→2026-11-19 (bp)', diff_bp(u[d12a], u[d1b]), 91)
P('E11', '「实际 +102bp」', 'TIPS_10Y 2025-11-19→2026-11-19 (bp)', diff_bp(t[d12a], t[d1b]), 102)
P('E12', '「盈亏平衡 -11bp」', 'BEI_10Y 2025-11-19→2026-11-19 (bp)', diff_bp(be[d12a], be[d1b]), -11)
P('E13', '传导环1「三个月窗(2026-08-19→2026-11-19)自 2.30」', sn.key('BEI_10Y', d3a), be[d3a], 2.30)
P('E14', '「回落至 2.16」', sn.key('BEI_10Y', d1b), be[d1b], 2.16)
u2a, u2b = sn.val('UST_2Y', d3a), sn.val('UST_2Y', d1b)
P('E15', '传导环2「近端 UST_2Y +57bp」', 'UST_2Y 2026-11-19 − 2026-08-19 (bp)', diff_bp(u2a, u2b), 57)
c3a, c1b = sn.val('CURVE_2S10S', d3a), sn.val('CURVE_2S10S', d1b)
P('E16', '「CURVE_2S10S 同窗自 0.46」', sn.key('CURVE_2S10S', d3a), c3a, 0.46)
P('E17', '「降至 0.28」', sn.key('CURVE_2S10S', d1b), c1b, 0.28)
t1023 = sn.val('TIPS_10Y', '2026-10-23')
P('E18', '传导环3「TIPS_10Y 2.66→2.88」(2.66)', sn.key('TIPS_10Y', '2026-10-23'), t1023, 2.66)
P('E19', '「(+22bp，2026-10-23→2026-11-19)」', 'TIPS_10Y 2026-11-19 − 2026-10-23 (bp)', diff_bp(t1023, t[d1b]), 22)
P('E20', '「共同交易日窗」三利率序列在窗端点 2026-10-20/2026-08-19/2025-11-19 均有观测', 'series_store 三序列端点在场性', all(sn.val(s, d) is not None for s in ('UST_10Y', 'TIPS_10Y', 'BEI_10Y') for d in (d1a, d1b, d3a, d12a)), True)
bw = sn.win('BEI_10Y', D('2025-11-20'), D('2026-11-20'))
bmin = min(bw, key=lambda x: x[1])
EX['bei_12m_low'] = sorted([(b, a.isoformat()) for a, b in bw])[:4]
P('E21', '传导环1「最新 2.15(观测 2026-11-20，12 个月窗内最低)」', 'BEI_10Y 2025-11-20..2026-11-20 最小值@日期', '%s@%s' % (bmin[1], bmin[0].isoformat()), '2.15@2026-11-20')
P('E22', '「2026-02-27 的 2.25」', sn.key('BEI_10Y', '2026-02-27'), sn.val('BEI_10Y', '2026-02-27'), 2.25)
P('E23', '「升至 2026-05-04 的 2.50」', sn.key('BEI_10Y', '2026-05-04'), sn.val('BEI_10Y', '2026-05-04'), 2.50)
P('E24', '恒等式 近一月: 名义 −8 = 实际 11 + 盈亏平衡 −19', 'E05 + E06', diff_bp(t[d1a], t[d1b]) + diff_bp(be[d1a], be[d1b]), diff_bp(u[d1a], u[d1b]))

# ---------------- F 资产与汇率窗 ----------------
cat('F 资产与汇率窗')
d0 = D('2026-10-23')
d0819 = D('2026-08-19')
d20 = D('2026-11-20')
d23 = D('2026-11-23')
V = lambda sid, d: sn.val(sid, d)
spx = {d: V('SPX', d) for d in (d0819, d0, d1b, d20, d23)}
vix = {d: V('VIX', d) for d in (d0819, d0, d20, d23)}
EX['spx_vix_levels'] = {'SPX': {k.isoformat(): v for k, v in spx.items()}, 'VIX': {k.isoformat(): v for k, v in vix.items()}}
P('F01', 'asset_returns_echo「SPX 1m -5.51%(2026-10-23→2026-11-23)」', 'SPX 2026-11-23 ÷ 2026-10-23 − 1', pct(spx[d0], spx[d23]), -5.51)
P('F02', '传导环3「共同交易日窗 2026-10-23→2026-11-19 为 -5.87%」', 'SPX 2026-11-19 ÷ 2026-10-23 − 1', pct(spx[d0], spx[d1b]), -5.87)
P('F03', '「同日收盘口径(2026-10-23→2026-11-20): 标普500指数 -9.36%」', 'SPX 2026-11-20 ÷ 2026-10-23 − 1', pct(spx[d0], spx[d20]), -9.36)
P('F04', '「三个月收盘口径(2026-08-19→2026-11-20): 标普500指数 -10.35%」', 'SPX 2026-11-20 ÷ 2026-08-19 − 1', pct(spx[d0819], spx[d20]), -10.35)
P('F05', '「VIX 上涨 38.87%」', 'VIX 2026-11-23 ÷ 2026-10-23 − 1', pct(vix[d0], vix[d23]), 38.87)
P('F06', '「(19.45→」', sn.key('VIX', d0), vix[d0], 19.45)
P('F07', '「→27.01」', sn.key('VIX', d23), vix[d23], 27.01)
P('F08', '「VIX +84.52%」(2026-10-23→2026-11-20)', 'VIX 2026-11-20 ÷ 2026-10-23 − 1', pct(vix[d0], vix[d20]), 84.52)
P('F09', '「VIX +141.03%(14.89→35.89)」(2026-08-19→2026-11-20)', 'VIX 2026-11-20 ÷ 2026-08-19 − 1', pct(vix[d0819], vix[d20]), 141.03)
P('F10', '「14.89」', sn.key('VIX', d0819), vix[d0819], 14.89)
P('F11', '「→35.89」', sn.key('VIX', d20), vix[d20], 35.89)
n0 = sn.val('NIKKEI225', d0)
nl = sn.last('NIKKEI225')
P('F12', '「NIKKEI225 下跌 9.98%」(2026-10-23→2026-11-20)', 'NIKKEI225 2026-11-20 ÷ 2026-10-23 − 1', pct(n0, nl[1]), -9.98)
P('F13', '「GOLD_F 下跌 8.05%」', 'GOLD_F 2026-11-23 ÷ 2026-10-23 − 1', pct(V('GOLD_F', d0), V('GOLD_F', d23)), -8.05)
P('F14', '「DXY 上涨 2.23%」', 'DXY 2026-11-23 ÷ 2026-10-23 − 1', pct(V('DXY', d0), V('DXY', d23)), 2.23)
P('F15', '「引擎资产月窗同窗 DAX +0.11%」', 'DAX 2026-11-23 ÷ 2026-10-23 − 1', pct(V('DAX', d0), V('DAX', d23)), 0.11)
sg = [pct(spx[d0], spx[d23]), pct(n0, nl[1]), pct(vix[d0], vix[d23]), pct(V('DXY', d0), V('DXY', d23))]
P('F16', 'headline「标普500指数与日经225 走低、VIX 抬升、美元指数走强」', '四项变动符号', (sg[0] < 0 and sg[1] < 0 and sg[2] > 0 and sg[3] > 0), True)
P('F17', '传导环3「股金同跌而美元与波动率齐升」', 'SPX<0, GOLD<0, DXY>0, VIX>0', (sg[0] < 0 and pct(V('GOLD_F', d0), V('GOLD_F', d23)) < 0 and sg[2] > 0 and sg[3] > 0), True)
# USDJPY
u0, u23, u0819 = V('USDJPY', d0), V('USDJPY', d23), V('USDJPY', d0819)
le823 = sn.le('USDJPY', '2026-08-23')
P('F18', 'M1环3「近一月(2026-10-23→2026-11-23)不降反升 1.82%」', 'USDJPY 2026-11-23 ÷ 2026-10-23 − 1', pct(u0, u23), 1.82)
P('F19', '「三个月 2026-08-19→2026-11-23 为 -0.13%」', 'USDJPY 2026-11-23 ÷ 2026-08-19 − 1', pct(u0819, u23), -0.13)
P('F20', '「按 3 个月前锚 2026-08-23 的最近观测 2026-08-21」', 'USDJPY 截至 2026-08-23 最新观测日', le823[0].isoformat(), '2026-08-21')
P('F21', '「起算为 +0.29%」', 'USDJPY 2026-11-23 ÷ 2026-08-21 − 1', pct(le823[1], u23), 0.29)
w12 = sn.win('USDJPY', D('2025-11-23'), d23)
wall = sn.win('USDJPY', D('2016-11-23'), d23)


def pctl(w, v):
    n = len(w)
    lt = sum(1 for a, b in w if b < v)
    le = sum(1 for a, b in w if b <= v)
    return {'le_share': le * 100.0 / n, 'lt_share': lt * 100.0 / n, 'mid': (lt + 0.5 * (le - lt)) * 100.0 / n, 'n': n}


p12, pall = pctl(w12, u23), pctl(wall, u23)
EX['usdjpy_pctl'] = {'12m': p12, 'all': pall, 'first': sn.first('USDJPY')[0].isoformat()}
P('F22', 'M1环3「近 12 个月窗内约第 71 百分位」', 'USDJPY 2025-11-23..2026-11-23 观测中 ≤ 当前值的占比', p12['le_share'], 71, tol=1.0, note='lt=%.2f mid=%.2f n=%d' % (p12['lt_share'], p12['mid'], p12['n']))
P('F23', '「序列库全史 2016-11-23 起约第 96.6 百分位」', 'USDJPY 全史 2016-11-23..2026-11-23 ≤ 当前值占比', pall['le_share'], 96.6, tol=0.5, note='lt=%.2f mid=%.2f n=%d' % (pall['lt_share'], pall['mid'], pall['n']))
P('F24', '「序列库全史 2016-11-23 起」(序列首日)', 'series_store.USDJPY.dates[0]', sn.first('USDJPY')[0].isoformat(), '2016-11-23')
# EURUSD
e23 = V('EURUSD', d23)
ew = sn.win('EURUSD', D('2025-11-23'), d23)
emin = min(ew, key=lambda x: x[1])
P('F25', 'C1「欧元兑美元 2026-11-23 为 1.093972」', sn.key('EURUSD', d23), e23, 1.093972)
P('F26', '「近 12 个月窗最低」', 'EURUSD 2025-11-23..2026-11-23 最小值@日期', '%s@%s' % (emin[1], emin[0].isoformat()), '1.093972@2026-11-23')
P('F27', '「三个月(2026-08-19→2026-11-23)-5.52%」', 'EURUSD 2026-11-23 ÷ 2026-08-19 − 1', pct(V('EURUSD', d0819), e23), -5.52)
# BRENT_F
b0819, b1023, b1123, b1119 = V('BRENT_F', d0819), V('BRENT_F', d0), V('BRENT_F', d23), V('BRENT_F', d12a)
P('F28', '传导环1「近三个月自 2026-08-19 的 91.62」', sn.key('BRENT_F', d0819), b0819, 91.62)
P('F29', '「至 2026-11-23 的 88.19」', sn.key('BRENT_F', d23), b1123, 88.19)
P('F30', '「为 -3.74%」', 'BRENT_F 2026-11-23 ÷ 2026-08-19 − 1', pct(b0819, b1123), -3.74)
P('F31', '「近一月 116.72→」', sn.key('BRENT_F', d0), b1023, 116.72)
P('F32', '「→88.19 为 -24.44%」', 'BRENT_F 2026-11-23 ÷ 2026-10-23 − 1', pct(b1023, b1123), -24.44)
P('F33', '「近 12 个月 +38.86%」', 'BRENT_F 2026-11-23 ÷ 2025-11-19 − 1', pct(b1119, b1123), 38.86, note='自 2025-11-23 起算=%s' % r(pct(V('BRENT_F', D('2025-11-23')), b1123), 4))
P('F34', '「窗内先升至 2026-10-23 的 116.72(较窗启 +27.40%)」', 'BRENT_F 2026-10-23 ÷ 2026-08-19 − 1', pct(b0819, b1023), 27.40)
bwin = sn.win('BRENT_F', d0819, d23)
bmax = max(bwin, key=lambda x: x[1])
P('F35', '「窗内高点 117.64(2026-10-30)」', 'BRENT_F 2026-08-19..2026-11-23 最大值@日期', '%s@%s' % (r(bmax[1], 2), bmax[0].isoformat()), '117.64@2026-10-30')
P('F36', '「窗内 68 个观测」', 'BRENT_F 2026-08-19..2026-11-23 观测数', len(bwin), 68)
P('F37', '「中 61 个不低于窗启值」', 'BRENT_F 窗内 ≥ 91.62 的观测数', sum(1 for a, b in bwin if b >= b0819), 61)
m07, m09, m10, m2510 = month_mean('BRENT_F', '2026-07'), month_mean('BRENT_F', '2026-09'), month_mean('BRENT_F', '2026-10'), month_mean('BRENT_F', '2025-10')
EX['brent_month_means'] = {'2025-10': m2510, '2026-07': m07, '2026-08': month_mean('BRENT_F', '2026-08'), '2026-09': m09, '2026-10': m10, '2026-11(to 11-23)': month_mean('BRENT_F', '2026-11')}
P('F38', '「月均 2026-07 84.51」', 'BRENT_F 2026-07 日值均值', m07, 84.51)
P('F39', '「→2026-09 102.26」', 'BRENT_F 2026-09 日值均值', m09, 102.26)
P('F40', '「(+21.0%)」', '月均 2026-09 ÷ 2026-07 − 1', pct(m07, m09), 21.0)
P('F41', '「→2026-10 108.34」', 'BRENT_F 2026-10 日值均值', m10, 108.34)
P('F42', '「(+28.2%)」', '月均 2026-10 ÷ 2026-07 − 1', pct(m07, m10), 28.2)
P('F43', '「2025-10 月均 63.95」', 'BRENT_F 2025-10 日值均值', m2510, 63.95)
P('F44', '「2026-10 月均较 2025-10 月均 高 69.4%」', '月均 2026-10 ÷ 2025-10 − 1', pct(m2510, m10), 69.4)
rel = ['2026-10-13', '2026-10-16', '2026-10-30', '2026-11-13', '2026-11-16']
rv = [V('BRENT_F', D(x)) for x in rel]
EX['brent_release_day'] = dict(zip(rel, rv))
P('F45', '「发布日(10-13、10-16、10-30、11-13、11-16)当日油价在 92.44 至 117.64 之间」', 'BRENT_F 各发布日值 min..max', '%s..%s' % (r(min(rv), 2), r(max(rv), 2)), '92.44..117.64')
P('F46', '「均不低于窗启值 91.62」', '五个发布日值均 ≥ 91.62', all(v >= b0819 for v in rv), True)
seg = sn.win('BRENT_F', D('2026-10-13'), D('2026-11-16'))
smin = min(seg, key=lambda x: x[1])
P('F47', '「2026-10-13 至 2026-11-16 整段区间内的最低值为 2026-11-10 的 91.49」', 'BRENT_F 2026-10-13..2026-11-16 最小值@日期', '%s@%s' % (r(smin[1], 2), smin[0].isoformat()), '91.49@2026-11-10')

json.dump({'points': PTS, 'extra': EX}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('POINTS', len(PTS), 'MISMATCH', sum(1 for p in PTS if not p['ok']))
