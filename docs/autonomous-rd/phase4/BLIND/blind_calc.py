#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""盲测自算: GOLD_F vs REAL_10Y/DXY 传统反向关系的滚动/分年度/分状态检验。
数据源(全部本地引擎树,只读):
  - ~/investment-agent-dev/data/daily/research_snapshot_20261112_v2.json series_store: GOLD_F/DXY/VIX
  - ~/investment-agent-dev/data/daily/macro_20261112.json data.*.series: UST_10Y/BEI_10Y/TIPS_10Y/HY_OAS
REAL_10Y = round(UST_10Y - BEI_10Y, 4) (fact_engine.py 官方派生式)
"""
import json, math

import os
# Audit-R1 F05: 去绝对路径——默认引擎树本地相对解析,可用环境变量
# IA_ENGINE_DAILY 覆盖(净克隆/异机可复现,免硬编码用户目录)
DEV = os.environ.get('IA_ENGINE_DAILY',
                     os.path.expanduser('~/investment-agent-dev/data/daily'))

snap = json.load(open(f'{DEV}/research_snapshot_20261112_v2.json'))
ss = snap['series_store']

def load_series(store, mid):
    s = store[mid]
    return list(zip(s['dates'], s['values']))

macro = json.load(open(f'{DEV}/macro_20261112.json'))['data']
m_ser = {k: list(zip(v['series']['dates'], v['series']['values']))
         for k, v in macro.items() if isinstance(v, dict) and v.get('series', {}).get('dates')}

GOLD = dict(load_series(ss, 'GOLD_F'))
DXY = dict(load_series(ss, 'DXY'))
VIX = dict(load_series(ss, 'VIX'))
UST = dict(m_ser['UST_10Y'])
BEI = dict(m_ser['BEI_10Y'])
TIPS = dict(m_ser['TIPS_10Y'])
HYOAS = dict(m_ser['HY_OAS'])

# REAL_10Y 派生(对齐日交集)
REAL = {d: round(UST[d] - BEI[d], 4) for d in UST if d in BEI}
print('REAL_10Y n=', len(REAL), 'first=', min(REAL), 'last=', max(REAL),
      'lastval=', REAL[max(REAL)])
print('check vs TIPS_10Y last:', TIPS[max(TIPS)], '(REAL 应≈TIPS,基差小)')

def aligned(*series_dicts):
    common = set(series_dicts[0])
    for s in series_dicts[1:]:
        common &= set(s)
    dates = sorted(common)
    return dates, [[s[d] for d in dates] for s in series_dicts]

# 主对齐: GOLD, REAL, DXY, VIX, UST
dates, (gold, real, dxy, vix, ust) = aligned(GOLD, REAL, DXY, VIX, UST)
n = len(dates)
print(f'\n主样本: n={n}, {dates[0]}..{dates[-1]}')

def pct(v):
    return [None] + [(v[i]/v[i-1]-1)*100 for i in range(1, len(v))]

def diff(v):
    return [None] + [v[i]-v[i-1] for i in range(1, len(v))]

g_ret = pct(gold)      # 黄金日收益率%
r_chg = diff(real)     # 实际利率日变化 pp
u_chg = diff(ust)      # 名义利率日变化 pp
d_ret = pct(dxy)       # 美元日收益率%
g_lvl, r_lvl, d_lvl = gold, real, dxy

def pearson(x, y):
    pts = [(a, b) for a, b in zip(x, y) if a is not None and b is not None
           and (a == a) and (b == b)]
    if len(pts) < 3:
        return None, len(pts)
    mx = sum(p[0] for p in pts)/len(pts); my = sum(p[1] for p in pts)/len(pts)
    cov = sum((p[0]-mx)*(p[1]-my) for p in pts)
    vx = sum((p[0]-mx)**2 for p in pts); vy = sum((p[1]-my)**2 for p in pts)
    if vx <= 0 or vy <= 0:
        return None, len(pts)
    return cov/math.sqrt(vx*vy), len(pts)

# ── 1) 全样本相关(日变化口径) ──
print('\n=== 全样本日变化相关 ===')
for name, a, b in [('GOLD_ret vs REAL10Y_chg', g_ret, r_chg),
                   ('GOLD_ret vs UST10Y_chg', g_ret, u_chg),
                   ('GOLD_ret vs DXY_ret', g_ret, d_ret),
                   ('GOLD_lvl vs REAL10Y_lvl', g_lvl, r_lvl),
                   ('GOLD_lvl vs DXY_lvl', g_lvl, d_lvl)]:
    r_, m_ = pearson(a, b)
    print(f'{name}: r={r_:+.3f} (n={m_})')

# ── 2) 分年度相关(日变化) ──
print('\n=== 分年度相关(日变化口径) ===')
print('年 | n | GOLD~REAL | GOLD~UST | GOLD~DXY')
years = sorted({d[:4] for d in dates})
for y in years:
    idx = [i for i, d in enumerate(dates) if d.startswith(y)]
    rr1 = pearson([g_ret[i] for i in idx], [r_chg[i] for i in idx])
    rr2 = pearson([g_ret[i] for i in idx], [u_chg[i] for i in idx])
    rr3 = pearson([g_ret[i] for i in idx], [d_ret[i] for i in idx])
    f = lambda t: f'{t[0]:+.3f}' if t[0] is not None else '  —  '
    print(f'{y} | {len(idx):4d} | {f(rr1)} | {f(rr2)} | {f(rr3)}')

# ── 3) 滚动 252 日相关(日变化) ──
def rolling(a, b, win):
    out = []
    for i in range(len(a)):
        if i < win:
            out.append((dates[i], None)); continue
        x = a[i-win+1:i+1]; y = b[i-win+1:i+1]
        r_, m_ = pearson(x, y)
        out.append((dates[i], r_))
    return out

roll_gr = rolling(g_ret, r_chg, 252)
roll_gd = rolling(g_ret, d_ret, 252)
roll_gu = rolling(g_ret, u_chg, 252)

def summarize(roll, name):
    pts = [(d, r) for d, r in roll if r is not None]
    print(f'\n--- {name} 滚动252日相关: {pts[0][0]}..{pts[-1][0]}, {len(pts)} 点')
    # 按年末/半年取样打印轨迹
    last_year = None
    for d, r in pts:
        y, mth = d[:4], d[5:7]
        if mth in ('06', '12') and d[:7] != last_year:
            last_year = d[:7]
            print(f'  {d}: {r:+.3f}')
    # 首次持续转正(连续>=60交易日>=0)
    run = 0; first_pos = None
    for d, r in pts:
        if r >= 0:
            run += 1
            if run >= 60 and first_pos is None:
                first_pos = d
        else:
            run = 0
    print(f'  首次连续>=60日>=0 起点: {first_pos}')
    # 各统计段均值
    for lo, hi in [('2017-01','2019-12'), ('2020-01','2021-12'), ('2022-01','2023-12'), ('2024-01','2024-12'), ('2025-01','2025-12'), ('2026-01','2026-11')]:
        seg = [r for d, r in pts if lo <= d[:7] <= hi]
        if seg:
            print(f'  均值 {lo}..{hi}: {sum(seg)/len(seg):+.3f} (min {min(seg):+.3f}, max {max(seg):+.3f}, n={len(seg)})')
    return pts

pts_gr = summarize(roll_gr, 'GOLD~REAL_10Y')
pts_gd = summarize(roll_gd, 'GOLD~DXY')
pts_gu = summarize(roll_gu, 'GOLD~UST_10Y')

# ── 4) 分状态: VIX>20 vs <=20 (日变化) ──
print('\n=== 分状态相关(阈值 VIX 收盘 20) ===')
for label, cond in [('恐慌态 VIX>20', lambda i: vix[i] > 20),
                    ('普通态 VIX<=20', lambda i: vix[i] <= 20)]:
    idx = [i for i in range(1, n) if cond(i)]
    r1 = pearson([g_ret[i] for i in idx], [r_chg[i] for i in idx])
    r2 = pearson([g_ret[i] for i in idx], [u_chg[i] for i in idx])
    r3 = pearson([g_ret[i] for i in idx], [d_ret[i] for i in idx])
    print(f'{label}: n={len(idx)} | GOLD~REAL {r1[0]:+.3f} | GOLD~UST {r2[0]:+.3f} | GOLD~DXY {r3[0]:+.3f}')

# 分状态 × 分时段(2022-2024+2025+2026 vs 2017-2021)
print('\n=== 分状态 × 分时段 ===')
for span, lo, hi in [('2017-2021', '2017', '2021'), ('2022-2026', '2022', '2026')]:
    for label, cond in [('恐慌态 VIX>20', lambda i: vix[i] > 20), ('普通态 VIX<=20', lambda i: vix[i] <= 20)]:
        idx = [i for i in range(1, n) if cond(i) and lo <= dates[i][:4] <= hi]
        if len(idx) < 30:
            continue
        r1 = pearson([g_ret[i] for i in idx], [r_chg[i] for i in idx])
        r3 = pearson([g_ret[i] for i in idx], [d_ret[i] for i in idx])
        print(f'{span} {label}: n={len(idx)} | GOLD~REAL {r1[0]:+.3f} | GOLD~DXY {r3[0]:+.3f}')

# ── 5) 事件窗: 2022-2026 内 REAL_10Y 上行日黄金表现 ──
print('\n=== 实际利率上行日 vs 下行日的黄金日均收益 ===')
for lo, hi in [('2017', '2021'), ('2022', '2026')]:
    up = [g_ret[i] for i in range(1, n) if lo <= dates[i][:4] <= hi and r_chg[i] is not None and r_chg[i] > 0]
    dn = [g_ret[i] for i in range(1, n) if lo <= dates[i][:4] <= hi and r_chg[i] is not None and r_chg[i] < 0]
    print(f'{lo}-{hi}: 实际利率上行日 n={len(up)} 黄金日均 {sum(up)/len(up):+.3f}% | 下行日 n={len(dn)} 黄金日均 {sum(dn)/len(dn):+.3f}%')
    du = [d_ret[i] for i in range(1, n) if lo <= dates[i][:4] <= hi and d_chg_pos(i)] if False else None
# 美元上行/下行日
for lo, hi in [('2017', '2021'), ('2022', '2026')]:
    up = [g_ret[i] for i in range(1, n) if lo <= dates[i][:4] <= hi and d_ret[i] is not None and d_ret[i] > 0]
    dn = [g_ret[i] for i in range(1, n) if lo <= dates[i][:4] <= hi and d_ret[i] is not None and d_ret[i] < 0]
    print(f'{lo}-{hi}: 美元上行日 n={len(up)} 黄金日均 {sum(up)/len(up):+.3f}% | 下行日 n={len(dn)} 黄金日均 {sum(dn)/len(dn):+.3f}%')

# ── 6) 水平对比: 黄金与实际利率/美元水平的同期位置(背景描述) ──
print('\n=== 关键时点水平 ===')
for d in ['2016-11-14', '2019-12-31', '2020-12-31', '2021-12-31', '2022-12-30', '2023-12-29', '2024-12-31', '2025-12-31', '2026-06-30', '2026-11-11']:
    if d in GOLD and d in REAL:
        print(f'{d}: GOLD={GOLD[d]:.1f} REAL10Y={REAL[d]:.2f} DXY={DXY.get(d)} UST10Y={UST.get(d)} VIX={VIX.get(d)}')

# 2026 年内 REAL/DXY 区间与黄金
y26 = [d for d in dates if d.startswith('2026')]
print(f'\n2026 年内: REAL10Y 区间 {min(REAL[d] for d in y26):.2f}..{max(REAL[d] for d in y26):.2f}, DXY 区间 {min(DXY[d] for d in y26):.2f}..{max(DXY[d] for d in y26):.2f}, GOLD 区间 {min(GOLD[d] for d in y26):.0f}..{max(GOLD[d] for d in y26):.0f}')
# 黄金历史新高次数(2026)
peak = 0; mx = 0
for d in dates:
    if GOLD[d] > mx:
        mx = GOLD[d]; peak += 1
print(f'全样本历史新高天数计数(逐日新高): {peak}, 全样本最高 {mx:.1f} @ {max(dates, key=lambda d: GOLD[d])}')
h26 = sum(1 for i, d in enumerate(dates) if d.startswith('2026') and gold[i] == max(gold[:i+1]))
print(f'2026 年内创新高天数: {h26}')
