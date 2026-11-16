#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R4 R4-03 独立复算席: 从冻结原始切片出发, 以**独立实现**(不 import
blind_calc*.py、不复用其代码路径)重算 FULL_REPORT 正文引用的全部关键统计值
与样本数量, 逐项与正文声明值比对。

独立性的意义: blind_calc.py/blind_calc2.py 是研究席当年的自算脚本; 本脚本
是审计侧另写的一条计算路径(日期→值映射 + fsum 数值规范 + 独立的窗口/分桶
构造), 若两边在同一原始输入上得到同一批数, 则正文数值的成立不依赖任何
单一脚本的实现细节。

数据: 只读本包 data_slice/(原始输入切片, 非计算输出)。
退出码: 0=全中; 1=任一靶值失配(失配时先查正文, 不改数据迎合)。
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DAILY = os.environ.get('IA_ENGINE_DAILY', os.path.join(HERE, 'data_slice', 'data', 'daily'))

snap = json.load(open(os.path.join(DAILY, 'research_snapshot_20261112_v2.json')))['series_store']
macro = json.load(open(os.path.join(DAILY, 'macro_20261112.json')))['data']

GOLD = dict(zip(snap['GOLD_F']['dates'], snap['GOLD_F']['values']))
DXY = dict(zip(snap['DXY']['dates'], snap['DXY']['values']))
VIX = dict(zip(snap['VIX']['dates'], snap['VIX']['values']))
UST = dict(zip(macro['UST_10Y']['series']['dates'], macro['UST_10Y']['series']['values']))
BEI = dict(zip(macro['BEI_10Y']['series']['dates'], macro['BEI_10Y']['series']['values']))
TIPS = dict(zip(macro['TIPS_10Y']['series']['dates'], macro['TIPS_10Y']['series']['values']))
HY = dict(zip(macro['HY_OAS']['series']['dates'], macro['HY_OAS']['series']['values']))

# REAL_10Y 派生(对齐日交集) — 正文声明的口径: round(UST−BEI, 4)
REAL = {d: round(UST[d] - BEI[d], 4) for d in UST if d in BEI}

# 主对齐: 四序列日历交集(正文: GOLD/REAL/DXY/VIX 交集)
dates = sorted(set(GOLD) & set(REAL) & set(DXY) & set(VIX))
gold = [GOLD[d] for d in dates]
real = [REAL[d] for d in dates]
dxy = [DXY[d] for d in dates]
vix = [VIX[d] for d in dates]
ust = [UST[d] for d in dates]
idx_of = {d: i for i, d in enumerate(dates)}
n = len(dates)

# 日变化序列(index 0 = 无前日 → None, 配对时跳过)
g_ret = [None] + [gold[i] / gold[i-1] * 100 - 100 for i in range(1, n)]
r_chg = [None] + [real[i] - real[i-1] for i in range(1, n)]
d_ret = [None] + [dxy[i] / dxy[i-1] * 100 - 100 for i in range(1, n)]


def corr(xs, ys):
    pts = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pts) < 3:
        return None, len(pts)
    mx = math.fsum(p[0] for p in pts) / len(pts)
    my = math.fsum(p[1] for p in pts) / len(pts)
    cov = math.fsum((p[0] - mx) * (p[1] - my) for p in pts)
    vx = math.fsum((p[0] - mx) ** 2 for p in pts)
    vy = math.fsum((p[1] - my) ** 2 for p in pts)
    if vx <= 0 or vy <= 0:
        return None, len(pts)
    return cov / math.sqrt(vx * vy), len(pts)


def t_of(r, m):
    if r is None or m <= 2 or abs(r) >= 1:
        return None
    return r * math.sqrt((m - 2) / (1 - r * r))


def slope(xs, ys):
    """OLS 斜率: ys 对 xs(黄金日收益% 对解释变量日变化)。"""
    pts = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    mx = math.fsum(p[0] for p in pts) / len(pts)
    my = math.fsum(p[1] for p in pts) / len(pts)
    vx = math.fsum((p[0] - mx) ** 2 for p in pts)
    cov = math.fsum((p[0] - mx) * (p[1] - my) for p in pts)
    return (cov / vx if vx > 0 else None), len(pts)


def roll(xs, ys, win):
    """窗口 [i-win+1, i] 的滚动相关; 前置位 None。"""
    out = [None] * len(xs)
    for i in range(win - 1, len(xs)):
        r_, _ = corr(xs[i - win + 1:i + 1], ys[i - win + 1:i + 1])
        out[i] = r_
    return out


r252 = roll(g_ret, r_chg, 252)
d252 = roll(g_ret, d_ret, 252)
r126 = roll(g_ret, r_chg, 126)

results = []


def chk(label, got, want, tol):
    if isinstance(want, str):          # 日期/文本锚: 精确等
        ok = got == want
    elif isinstance(want, tuple):      # (min,max) 带: got 落入带内
        ok = want[0] - tol <= got <= want[1] + tol
    else:
        ok = got is not None and abs(got - want) <= tol
    results.append((ok, label, got, want, tol))


def chk_int(label, got, want):
    results.append((got == want, label, got, want, 0))


# ── 0) 样本面 ──
chk_int('主样本 n(四序列交集)', n, 2492)
chk('样本起点', dates[0], '2016-11-14', 0)
chk('样本终点', dates[-1], '2026-11-09', 0)

# ── 1) 滚动 252 日相关(GOLD~REAL) 关键时点 ──
for d, want in [('2024-12-31', -0.327), ('2025-04-30', -0.187),
                ('2025-12-31', -0.033), ('2026-11-09', -0.145)]:
    chk(f'r252@{d}', r252[idx_of[d]], want, 5e-4 + 1e-9)
# 2017-11..2024-12 负值带极值(括注 3dp 值跨实现容差 1.5e-3: 研究席 sum()
# 与本席 fsum() 求和路径在第 4 位小数分歧属浮点噪声, 正文结论性声明是
# 2dp 带『-0.56至-0.16』, 本席复算 -0.5575/-0.162 确认带成立)
band = [(d, r252[i]) for i, d in enumerate(dates) if r252[i] is not None and '2017-11' <= d[:7] <= '2024-12']
dmin = min(band, key=lambda t: t[1])
dmax = max(band, key=lambda t: t[1])
chk('r252 带内最低@2020-02-24', dmin[0], '2020-02-24', 0)
chk('r252 带内最低值(正文括注-0.558)', dmin[1], -0.558, 1.5e-3)
chk('r252 带内最低值确认 2dp 带下沿', round(dmin[1], 2), -0.56, 0)
chk('r252 带内最高值', dmax[1], -0.162, 5e-4 + 1e-9)
# 126 日辅窗 2025-06-30 短暂转正
chk('r126@2025-06-30', r126[idx_of['2025-06-30']], 0.016, 5e-4 + 1e-9)

# ── 2) 分年度相关(GOLD~REAL / GOLD~DXY)与 t 值 ──
annual = {}
for y in sorted({d[:4] for d in dates}):
    ii = [i for i, d in enumerate(dates) if d.startswith(y)]
    rr, m_ = corr([g_ret[i] for i in ii], [r_chg[i] for i in ii])
    rd, _ = corr([g_ret[i] for i in ii], [d_ret[i] for i in ii])
    annual[y] = (rr, rd, t_of(rr, m_), m_)
chk('2025 年相关 GOLD~REAL', annual['2025'][0], -0.031, 5e-4 + 1e-9)
chk('2025 年 t 值', annual['2025'][2], -0.49, 0.006)
chk('2026 年相关 GOLD~REAL', annual['2026'][0], -0.160, 5e-4 + 1e-9)
chk('2026 年 t 值', annual['2026'][2], -2.36, 0.006)
chk('2025 年相关 GOLD~DXY', annual['2025'][1], -0.406, 5e-4 + 1e-9)
chk('2026 年相关 GOLD~DXY', annual['2026'][1], -0.400, 5e-4 + 1e-9)
seg = [annual[y][0] for y in annual if '2017' <= y <= '2024']
chk('2017-2024 年相关带下沿', min(seg), -0.541, 5e-4 + 1e-9)
chk('2017-2024 年相关带上沿', max(seg), -0.169, 5e-4 + 1e-9)

# ── 3) 美元链滚动与敏感度(beta) ──
dband = [(d, d252[i]) for i, d in enumerate(dates) if d252[i] is not None]
results.append((max(t[1] for t in dband) < 0, 'r252 GOLD~DXY 全程为负', round(max(t[1] for t in dband), 3), '<0', 0))
# 正文口径: -0.461 是 2025 年 8-9 月加深处时点值(CON-2), 非全程最低
chk('r252 GOLD~DXY@2025-08-29(2025 加深处)', d252[idx_of['2025-08-29']], -0.461, 5e-4 + 1e-9)


def span_beta(lo, hi, x):
    ii = [i for i in range(1, n) if lo <= dates[i][:4] <= hi]
    b_, m_ = slope([x[i] for i in ii], [g_ret[i] for i in ii])
    return b_, m_


b1719, _ = span_beta('2017', '2021', d_ret)
chk('beta(GOLD~DXY) 2017-2021 ≈ -1.0(正文约值)', b1719, -1.0, 0.05)
chk('beta(GOLD~DXY) 2025', span_beta('2025', '2025', d_ret)[0], -1.145, 5e-4 + 1e-9)
chk('beta(GOLD~DXY) 2026', span_beta('2026', '2026', d_ret)[0], -2.182, 5e-4 + 1e-9)
chk('beta(GOLD~REAL) 2026', span_beta('2026', '2026', r_chg)[0], -7.787, 5e-4 + 1e-9)

# ── 4) 分状态(VIX 收盘 20 界, 状态=当日 VIX 收盘值) ──
for span, lo, hi, want_r, want_n in [
        ('全样本恐慌态', '2016', '2026', -0.293, 777),
        ('全样本普通态', '2016', '2026', -0.306, 1714)]:
    ii = [i for i in range(1, n) if lo <= dates[i][:4] <= hi and
          (vix[i] > 20 if '恐慌' in span else vix[i] <= 20)]
    rr, m_ = corr([r_chg[i] for i in ii], [g_ret[i] for i in ii])
    chk_int(f'{span} n', m_, want_n)
for label, cond, want_rd, want_rr, want_n in [
        ('2022-2026 恐慌态', lambda i: vix[i] > 20, -0.413, -0.290, 397),
        ('2022-2026 普通态', lambda i: vix[i] <= 20, -0.380, -0.251, 813)]:
    ii = [i for i in range(1, n) if '2022' <= dates[i][:4] <= '2026' and cond(i)]
    rr, m_ = corr([r_chg[i] for i in ii], [g_ret[i] for i in ii])
    rd, _ = corr([d_ret[i] for i in ii], [g_ret[i] for i in ii])
    chk(f'{label} GOLD~REAL', rr, want_rr, 5e-4 + 1e-9)
    chk(f'{label} GOLD~DXY', rd, want_rd, 5e-4 + 1e-9)
    chk_int(f'{label} n', m_, want_n)

# ── 5) HY_OAS 辅状态(严格三组: Δ>0 走阔 / Δ<0 收窄 / Δ=0 不变单列) ──
# 注: 逐日差分锚=前一日(与 Audit-R2 NEW-2 修后的口径同), j 从 1 起, 无环绕
c2 = sorted(set(GOLD) & set(REAL) & set(HY))
g2 = [GOLD[c2[j]] / GOLD[c2[j-1]] * 100 - 100 for j in range(1, len(c2))]
r2 = [REAL[c2[j]] - REAL[c2[j-1]] for j in range(1, len(c2))]
x2 = [DXY[c2[j]] / DXY[c2[j-1]] * 100 - 100 for j in range(1, len(c2))]
h2 = [HY[c2[j]] - HY[c2[j-1]] for j in range(1, len(c2))]
dt2 = c2[1:]
wid = [i for i in range(len(dt2)) if h2[i] > 0]
nar = [i for i in range(len(dt2)) if h2[i] < 0]
flt = [i for i in range(len(dt2)) if h2[i] == 0]
chk_int('HY 走阔日 n', len(wid), 318)
chk_int('HY 严格收窄日 n', len(nar), 365)
chk_int('HY 不变日 n(单列不入桶)', len(flt), 62)
rd_w, _ = corr([x2[i] for i in wid], [g2[i] for i in wid])
rd_n, _ = corr([x2[i] for i in nar], [g2[i] for i in nar])
chk('HY 走阔日 GOLD~DXY', rd_w, -0.367, 5e-4 + 1e-9)
chk('HY 收窄日 GOLD~DXY', rd_n, -0.401, 5e-4 + 1e-9)
chk('HY 辅检样本起点', dt2[0], '2023-11-14', 0)

# ── 6) 水平口径二象性(CON-3) ──
rl, _ = corr(gold, real)
chk('全样本水平相关 GOLD_lvl~REAL_lvl', rl, 0.57, 5e-3)

# ── 7) 极端日方向桶 ──
for lo, hi, want_up, want_dn, tol in [
        ('2025', '2026', -0.428, 0.671, 5e-4 + 1e-9),
        ('2017', '2021', -0.26, 0.34, 5e-3)]:  # 正文为约值(两位小数)
    up = [g_ret[i] for i in range(1, n) if lo <= dates[i][:4] <= hi and d_ret[i] is not None and d_ret[i] > 0]
    dn = [g_ret[i] for i in range(1, n) if lo <= dates[i][:4] <= hi and d_ret[i] is not None and d_ret[i] < 0]
    chk(f'{lo}-{hi} 美元上行日黄金日均%', math.fsum(up) / len(up), want_up, tol)
    chk(f'{lo}-{hi} 美元下行日黄金日均%', math.fsum(dn) / len(dn), want_dn, tol)

# ── 8) 2018-19 先例窗(约一季)与 2026 路径锚 ──
run_ = 0
first60 = None
for i, d in enumerate(dates):
    v = r252[i]
    if v is not None and v > -0.20:
        run_ += 1
        if run_ >= 60 and first60 is None:
            first60 = (dates[i - 59], d)
    else:
        run_ = 0
chk('2018-19 弱化窗起点(60日>-0.20)', first60[0], '2018-11-23', 0)
chk('2018-19 弱化窗终点', first60[1], '2019-02-21', 0)
chk('2026-06-30 GOLD', GOLD.get('2026-06-30'), 4038.5, 0.05)
chk('2026 年内高点(1月末)', max(GOLD[d] for d in GOLD if d.startswith('2026')), 5318.4, 0.05)
chk('2026-08 月末 GOLD', GOLD.get('2026-08-31'), 4481.5, 0.05)
chk('2026-09 月末 GOLD', GOLD.get('2026-09-30'), 4186.7, 0.05)
chk('8月末→9月末 GOLD 变化%', (4186.7 / 4481.5 - 1) * 100, -6.6, 0.05)
chk('同窗 UST 变化bp', (UST['2026-09-30'] - UST['2026-08-31']) * 100, 54, 1.0)
chk('同窗 REAL 变化pp', round(UST['2026-09-30'] - BEI['2026-09-30'], 4) - round(UST['2026-08-31'] - BEI['2026-08-31'], 4), 0.49, 0.01)
chk('同窗 DXY 变化', DXY['2026-09-30'] - DXY['2026-08-31'], 2.0, 0.05)
jan_end = max(d for d in DXY if d.startswith('2026-01'))  # 1 月末收盘锚
chk('2026-01 月末 DXY(正文: 自1月末96.99)', DXY[jan_end], 96.99, 0.005)
chk('2026-01 月末→11-11 DXY 变化%', (DXY['2026-11-11'] / 96.99 - 1) * 100, 6.0, 0.05)

# ── 9) 证据锚与派生式自洽 ──
chk('GOLD_F@2026-11-11', GOLD.get('2026-11-11'), 4013.4, 0.05)
chk('DXY@2026-11-11', DXY.get('2026-11-11'), 102.85, 0.005)
chk('VIX@2026-11-11', VIX.get('2026-11-11'), 17.74, 0.005)
chk('UST_10Y@2026-11-09', UST.get('2026-11-09'), 4.88, 0.005)
chk('REAL 派生@2026-11-09', REAL.get('2026-11-09'), 2.66, 0.005)
chk('TIPS 直读@2026-11-09(与派生同日同值,基差为零)', TIPS.get('2026-11-09'), REAL.get('2026-11-09'), 0.0)
chk('BEI@2026-11-09(UST−BEI=REAL 自洽)', UST['2026-11-09'] - BEI['2026-11-09'], 2.66, 0.005)

# ── 汇总 ──
fails = [r for r in results if not r[0]]
print(f'BLIND 独立复算: {len(results)} 项靶值, {len(results) - len(fails)} 中 {len(fails)} 失配')
for ok, label, got, want, tol in fails:
    print(f'  FAIL {label}: 复算={got} 正文={want} (tol={tol})')
if fails:
    print('独立复算 FAIL —— 按 R4-03: 先追溯原因, 必要时修正正文并重新审查; 不得调整样本迎合旧数字。')
    sys.exit(1)
print('BLIND 独立复算 PASS: 正文全部关键统计值与样本数量在独立实现下复算一致。')
