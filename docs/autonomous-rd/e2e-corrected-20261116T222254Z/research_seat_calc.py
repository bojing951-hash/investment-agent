#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E2E 研究席自算脚本(独立 Agent Native 席;零引用系统内既有计算结果)。

研究问题: 美国盈亏平衡通胀预期(BEI_10Y)上行阶段,黄金(GOLD_F)与美元指数(DXY)
的相对表现: 通胀预期变化如何影响金价与美元的传统跷跷板关系。

数据根(只读原始序列):
- /Users/cast/investment-agent-dev/data/daily/research_snapshot_20261112_v2.json
  → series_store: GOLD_F / DXY / VIX / BRENT_F(2016-11-14..2026-11-11, n=2514)
- /Users/cast/investment-agent-dev/data/daily/macro_20261114.json
  → data.*.series: BEI_10Y / UST_10Y / TIPS_10Y(2016-11-14..2026-11-12, n≈2499)

口径声明(全部统计按此复算):
- 日频;价格类(GOLD_F/DXY/BRENT_F)取日收益率 pct=100*(P_t/P_{t-1}-1),
  相邻观测对(自然日序列内前一行,非发布日对齐——描述性口径,按统计期对齐,
  不代表当时市场信息集);
- 利率类(BEI_10Y/UST_10Y/TIPS_10Y)取日变化 pp(百分点;1pp=100bp);
- 对齐=按 observation_date 精确匹配取交集(丢弃单侧独有日期,逐处披露 n);
- 相关=皮尔逊(对原始值直算,不做异常值处理);t 统计量=r*sqrt((n-2)/(1-r^2));
- OLS=普通最小二乘,手写正规方程,标准误按经典公式,自由度 n-k-1。
"""
import json
import math

import argparse
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
# Audit-R5 条目3(5): 实际使用脚本的仓内固化版。与实际运行的唯一差异 =
# 输入路径参数化(原为上面 docstring 所记 /Users/cast/.../ 绝对路径,
# 内容同版,data_slice.json 为其完整抽取,sha256 见 README)。
DEFAULT_DATA = os.path.join(_HERE, 'data_slice.json')


def load(path=None):
    path = path or DEFAULT_DATA
    doc = json.load(open(path))
    S = {}
    for k, e in doc['series'].items():
        S[k] = dict(zip(e['dates'], e['values']))
    return S


def intersect(S, keys):
    common = set(S[keys[0]])
    for k in keys[1:]:
        common &= set(S[k])
    return sorted(d for d in common if all(S[k][d] is not None for k in keys))


def rets(S, keys, dates):
    """返回 {key: [日变化]}: 价格类=收益率%,利率类=pp 变化。"""
    out = {k: [] for k in keys}
    ds = []
    PRICE = {'GOLD_F', 'DXY', 'VIX', 'BRENT_F'}
    for prev, cur in zip(dates[:-1], dates[1:]):
        vals_ok = True
        row = {}
        for k in keys:
            a, b = S[k][prev], S[k][cur]
            if a is None or b is None:
                vals_ok = False
                break
            row[k] = 100.0 * (b / a - 1.0) if k in PRICE else (b - a)
        if vals_ok:
            ds.append(cur)
            for k in keys:
                out[k].append(row[k])
    return ds, out


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx <= 0 or syy <= 0:
        return float('nan'), n
    r = sxy / math.sqrt(sxx * syy)
    return r, n


def t_of_r(r, n):
    if n <= 3 or abs(r) >= 1:
        return float('nan')
    return r * math.sqrt((n - 2) / (1 - r * r))


def mean(xs):
    return sum(xs) / len(xs) if xs else float('nan')


def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return float('nan')
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def ols(y, X):
    """X=list of regressor lists(不含常数,内部加一列 1)。返回 (beta, se, r2, n)。"""
    n = len(y)
    k = len(X)
    cols = [[1.0] * n] + X
    p = k + 1
    # normal equations
    A = [[sum(cols[i][t] * cols[j][t] for t in range(n)) for j in range(p)]
         for i in range(p)]
    b = [sum(cols[i][t] * y[t] for t in range(n)) for i in range(p)]
    # gaussian elimination
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(p):
        piv = max(range(c, p), key=lambda r: abs(M[r][c]))
        M[c], M[piv] = M[piv], M[c]
        if abs(M[c][c]) < 1e-12:
            return None, None, None, n
        for r in range(p):
            if r != c:
                f = M[r][c] / M[c][c]
                for cc in range(c, p + 1):
                    M[r][cc] -= f * M[c][cc]
    beta = [M[i][p] / M[i][i] for i in range(p)]
    yhat = [sum(beta[i] * cols[i][t] for i in range(p)) for t in range(n)]
    my = mean(y)
    sse = sum((y[t] - yhat[t]) ** 2 for t in range(n))
    sst = sum((v - my) ** 2 for v in y)
    r2 = 1 - sse / sst if sst > 0 else float('nan')
    dof = n - p
    sigma2 = sse / dof if dof > 0 else float('nan')
    # var(beta_i)=sigma2*(X'X)^-1_ii → 逆已在对角缩放形式:M[i][i]=1/(X'X)^-1? 不,
    # 高斯消元后 M[i][i]*beta_i=M[i][p] → 需要显式逆对角。重算 (X'X)^-1 对角:
    # 用解方程组法: e_i 解 (X'X) z = e_i, z_i 即逆对角元
    invdiag = []
    for idx in range(p):
        e = [1.0 if i == idx else 0.0 for i in range(p)]
        MM = [row[:] for row in A]
        for c in range(p):
            piv = max(range(c, p), key=lambda r: abs(MM[r][c]))
            MM[c], MM[piv] = MM[piv], MM[c]
            for r in range(p):
                if r != c:
                    f = MM[r][c] / MM[c][c]
                    for cc in range(c, p):
                        MM[r][cc] -= f * MM[c][cc]
        invdiag.append(e[idx] / MM[idx][idx] if abs(MM[idx][idx]) > 1e-15 else float('nan'))
    se = [math.sqrt(sigma2 * invdiag[i]) if invdiag[i] > 0 else float('nan')
          for i in range(p)]
    return beta, se, r2, n


def pct(x):
    return '%.4f' % x if isinstance(x, float) else x


def main():
    S = load(_args.data)
    print('== 0. 序列基本面对齐 ==')
    for k in S:
        ds = sorted(S[k])
        print(f'{k}: n={len(ds)} first={ds[0]} last={ds[-1]} last_val={S[k][ds[-1]]}')

    # ---- 核心对齐集: 五序列日历交集 ----
    dates5 = intersect(S, ['GOLD_F', 'DXY', 'BEI_10Y', 'UST_10Y', 'TIPS_10Y'])
    ds, R = rets(S, ['GOLD_F', 'DXY', 'BEI_10Y', 'UST_10Y', 'TIPS_10Y'], dates5)
    n = len(ds)
    print(f'\n五序列交集观测日={len(dates5)},相邻变化对 n={n},'
          f'首变化日={ds[0]} 末变化日={ds[-1]}')
    dropped_gold_dxy = 2511 - n  # 快照侧变化对 2511(S5 对齐口径)
    print(f'(相对快照侧 DXY/GOLD_F 变化对 2511,因 BEI/TIPS 日历差掉落约 '
          f'{dropped_gold_dxy} 对)')

    # ---- 恒等式检查 UST = BEI + TIPS ----
    dev = [abs(R['UST_10Y'][i] - R['BEI_10Y'][i] - R['TIPS_10Y'][i])
           for i in range(n)]
    print(f'\n恒等式检查: |dUST-dBEI-dTIPS| 均值={mean(dev):.4f}pp '
          f'最大={max(dev):.2f}pp(2位小数舍入噪声内→TIPS 与 UST-BEI 高度同源)')

    # ---- 1. 全样本跷跷板基准 ----
    print('\n== 1. 全样本跷跷板基准(日频变化口径) ==')
    r_gd, nn = pearson(R['GOLD_F'], R['DXY'])
    print(f'corr(GOLD_F日收益, DXY日收益) 全样本 = {r_gd:.4f} (n={nn}, '
          f't={t_of_r(r_gd, nn):.1f})')
    for y in (2020, 2022, 2024, 2026):
        pass
    print('分年度 corr(GOLD,DXY):')
    for yr in range(2017, 2027):
        xs = [R['GOLD_F'][i] for i in range(n) if ds[i][:4] == str(yr)]
        ys = [R['DXY'][i] for i in range(n) if ds[i][:4] == str(yr)]
        r0, n0 = pearson(xs, ys)
        print(f'  {yr}: r={r0:+.3f} (n={n0}, t={t_of_r(r0, n0):.1f})')

    # ---- 2. BEI 日变化条件统计 ----
    print('\n== 2. BEI_10Y 日上行/下行的条件表现(日频) ==')
    dBEI = R['BEI_10Y']
    print(f'dBEI 分布: 均值={mean(dBEI):+.4f}pp 标准差≈'
          f'{math.sqrt(sum((v-mean(dBEI))**2 for v in dBEI)/(n-1)):.4f}pp '
          f'(即日均约4bp量级的噪声带)')
    for thr_bp in (1, 2, 3, 5):
        up = [i for i in range(n) if dBEI[i] > thr_bp / 100.0]
        dn = [i for i in range(n) if dBEI[i] < -thr_bp / 100.0]
        gU = [R['GOLD_F'][i] for i in up]
        dU = [R['DXY'][i] for i in up]
        gD = [R['GOLD_F'][i] for i in dn]
        dD = [R['DXY'][i] for i in dn]
        rU, nU = pearson(gU, dU)
        rD, nD = pearson(gD, dD)
        # 跷跷板同现频率: BEI 上行日中 金涨&美元跌 的比例
        bothU = sum(1 for i in up if R['GOLD_F'][i] > 0 and R['DXY'][i] < 0)
        bothD = sum(1 for i in dn if R['GOLD_F'][i] < 0 and R['DXY'][i] > 0)
        print(f'阈值±{thr_bp}bp: 上行日n={len(up)} 金均收益={mean(gU):+.3f}% '
              f'美元均={mean(dU):+.3f}% | 下行日n={len(dn)} 金均={mean(gD):+.3f}% '
              f'美元均={mean(dD):+.3f}%')
        print(f'          子样本内 corr(GOLD,DXY): 上行日={rU:+.3f}(n={nU}) '
              f'下行日={rD:+.3f}(n={nD}); '
              f'上行日中金涨&美元跌占比={bothU/len(up)*100 if up else 0:.1f}% '
              f'(上行日金涨占比={sum(1 for v in gU if v>0)/len(gU)*100 if gU else 0:.1f}%, '
              f'美元涨占比={sum(1 for v in dU if v>0)/len(dU)*100 if dU else 0:.1f}%)')

    # ---- 3. BEI 与金/美元/油的相关及 OLS 分解 ----
    print('\n== 3. 通胀预期 vs 实际利率的分解(日频) ==')
    for a, b in (('GOLD_F', 'BEI_10Y'), ('GOLD_F', 'TIPS_10Y'),
                 ('DXY', 'BEI_10Y'), ('DXY', 'TIPS_10Y'),
                 ('GOLD_F', 'UST_10Y'), ('DXY', 'UST_10Y')):
        r0, n0 = pearson(R[a], R[b])
        print(f'corr({a}, {b}) = {r0:+.4f} (n={n0}, t={t_of_r(r0, n0):.1f})')
    for y in ('GOLD_F', 'DXY'):
        beta, se, r2, n0 = ols(R[y], [R['BEI_10Y'], R['TIPS_10Y']])
        if beta:
            print(f'OLS: {y}日收益 ~ dBEI + dTIPS: 截距={beta[0]:+.4f} '
                  f'β_dBEI={beta[1]:+.3f}(se={se[1]:.3f},t={beta[1]/se[1]:.1f}) '
                  f'β_dTIPS={beta[2]:+.3f}(se={se[2]:.3f},t={beta[2]/se[2]:.1f}) '
                  f'R²={r2:.3f} n={n0}')

    # 分时段: 2017-2021 vs 2022-2026
    for lab, yrs in (('2017-2021', ('2017', '2018', '2019', '2020', '2021')),
                     ('2022-2026', ('2022', '2023', '2024', '2025', '2026'))):
        idx = [i for i in range(n) if ds[i][:4] in yrs]
        for y in ('GOLD_F', 'DXY'):
            r_b, n0 = pearson([R[y][i] for i in idx], [R['BEI_10Y'][i] for i in idx])
            r_t, _ = pearson([R[y][i] for i in idx], [R['TIPS_10Y'][i] for i in idx])
            r_gd, _ = pearson([R['GOLD_F'][i] for i in idx], [R['DXY'][i] for i in idx])
            print(f'{lab}: corr({y},dBEI)={r_b:+.3f} corr({y},dTIPS)={r_t:+.3f} '
                  f'corr(GOLD,DXY)={r_gd:+.3f} (n={n0})')

    # ---- 4. 月度窗口"上行阶段"口径 ----
    print('\n== 4. 月历窗口口径(每月=当月最后观测对上月最后观测) ==')
    months = sorted({d[:7] for d in dates5})
    mrows = []
    for mth in months:
        dm = [d for d in dates5 if d[:7] == mth]
        if len(dm) < 2:
            continue
        # 与上月衔接
        prevm = [d for d in dates5 if d < dm[0]]
        if not prevm:
            continue
        a, b = prevm[-1], dm[-1]
        g = 100 * (S['GOLD_F'][b] / S['GOLD_F'][a] - 1)
        x = 100 * (S['DXY'][b] / S['DXY'][a] - 1)
        bei = S['BEI_10Y'][b] - S['BEI_10Y'][a]
        tip = S['TIPS_10Y'][b] - S['TIPS_10Y'][a]
        mrows.append((mth, g, x, bei, tip))
    print(f'月历窗口数 n={len(mrows)} ({mrows[0][0]}..{mrows[-1][0]})')
    up = [r for r in mrows if r[3] > 0.05]
    dn = [r for r in mrows if r[3] < -0.05]
    for lab, grp in (('BEI月升>5bp', up), ('BEI月降<-5bp', dn)):
        if not grp:
            continue
        gs = [r[1] for r in grp]
        xs = [r[2] for r in grp]
        r0, n0 = pearson(gs, xs)
        print(f'{lab}: n={len(grp)} 金月均={mean(gs):+.2f}% 美元月均={mean(xs):+.2f}% '
              f'金胜率={sum(1 for v in gs if v>0)/len(gs)*100:.0f}% '
              f'美元胜率={sum(1 for v in xs if v>0)/len(xs)*100:.0f}% '
              f'月内corr(金,美元)={r0:+.3f}')
    # BEI 上行月再按实际利率方向拆
    up_tip_up = [r for r in up if r[4] > 0.05]
    up_tip_dn = [r for r in up if r[4] < -0.05]
    for lab, grp in (('BEI升且TIPS升(实际利率同升)', up_tip_up),
                     ('BEI升且TIPS降(名义由通胀预期主导)', up_tip_dn)):
        if not grp:
            continue
        gs = [r[1] for r in grp]
        xs = [r[2] for r in grp]
        print(f'  {lab}: n={len(grp)} 金月均={mean(gs):+.2f}% '
              f'美元月均={mean(xs):+.2f}% '
              f'金胜率={sum(1 for v in gs if v>0)/len(gs)*100:.0f}% '
              f'美元胜率={sum(1 for v in xs if v>0)/len(xs)*100:.0f}%')
    # 月度相关: 金月收益与美元月收益、与 dBEI
    r_gx, _ = pearson([r[1] for r in mrows], [r[2] for r in mrows])
    r_gb, _ = pearson([r[1] for r in mrows], [r[3] for r in mrows])
    r_xb, _ = pearson([r[2] for r in mrows], [r[3] for r in mrows])
    r_gt, _ = pearson([r[1] for r in mrows], [r[4] for r in mrows])
    r_xt, _ = pearson([r[2] for r in mrows], [r[4] for r in mrows])
    print(f'月度相关: corr(金,美元)={r_gx:+.3f} corr(金,dBEI)={r_gb:+.3f} '
          f'corr(美元,dBEI)={r_xb:+.3f} corr(金,dTIPS)={r_gt:+.3f} '
          f'corr(美元,dTIPS)={r_xt:+.3f} (n={len(mrows)})')

    # ---- 5. 21日滚动相位口径 ----
    print('\n== 5. 21个交易日滚动相位(上行=21日累计dBEI>+10bp) ==')
    datesX = intersect(S, ['GOLD_F', 'DXY', 'BEI_10Y'])
    dsX, RX = rets(S, ['GOLD_F', 'DXY', 'BEI_10Y'], datesX)
    nX = len(dsX)
    for H in (21, 63):
        # 相位=过去H日累计 dBEI(不含当日,防同日重叠解释)
        up_n = up_g = up_x = 0
        dn_n = dn_g = dn_x = 0
        up_pairs = []
        dn_pairs = []
        for i in range(H, nX):
            cum = sum(RX['BEI_10Y'][i - H:i])
            if cum > 0.10:
                up_n += 1
                up_g += RX['GOLD_F'][i]
                up_x += RX['DXY'][i]
                up_pairs.append((RX['GOLD_F'][i], RX['DXY'][i]))
            elif cum < -0.10:
                dn_n += 1
                dn_g += RX['GOLD_F'][i]
                dn_x += RX['DXY'][i]
                dn_pairs.append((RX['GOLD_F'][i], RX['DXY'][i]))
        rU, _ = pearson([p[0] for p in up_pairs], [p[1] for p in up_pairs])
        rD, _ = pearson([p[0] for p in dn_pairs], [p[1] for p in dn_pairs])
        print(f'{H}日相位: 上行相位日n={up_n} 金日均={up_g/up_n:+.3f}% '
              f'美元日均={up_x/up_n:+.3f}% | 下行相位日n={dn_n} '
              f'金日均={dn_g/dn_n:+.3f}% 美元日均={dn_x/dn_n:+.3f}% | '
              f'相位内corr(金,美元): 上行={rU:+.3f} 下行={rD:+.3f}')

    # ---- 6. 2026年9月机构记述复算(MSIM VP-VIEW-20261111-006) ----
    print('\n== 6. 2026年9月单月复算(检验机构记述) ==')
    def seg(k, a, b, price=True):
        va, vb = S[k].get(a), S[k].get(b)
        if va is None or vb is None:
            return None
        return 100 * (vb / va - 1) if price else (vb - va)
    a, b = '2026-08-31', '2026-09-30'
    for k, price in (('UST_10Y', False), ('TIPS_10Y', False),
                     ('BEI_10Y', False), ('GOLD_F', True), ('DXY', True),
                     ('BRENT_F', True)):
        da = [d for d in sorted(S[k]) if d <= a][-1]
        db = [d for d in sorted(S[k]) if d <= b][-1]
        v = seg(k, da, db, price)
        unit = '%' if price else 'pp'
        print(f'{k}: {da}→{db} = {v:+.2f}{unit}')

    # ---- 7. 2026 YTD 与当前位 ----
    print('\n== 7. 2026 YTD(2025-12-31→各自最后观测) ==')
    for k, price in (('GOLD_F', True), ('DXY', True), ('BRENT_F', True),
                     ('BEI_10Y', False), ('TIPS_10Y', False), ('UST_10Y', False)):
        dsK = sorted(S[k])
        a = [d for d in dsK if d <= '2025-12-31'][-1]
        b = dsK[-1]
        va, vb = S[k][a], S[k][b]
        v = 100 * (vb / va - 1) if price else (vb - va)
        print(f'{k}: {a}({va})→{b}({vb}) = {v:+.2f}{"%" if price else "pp"}')

    # ---- 8. BEI 上/下行事件日的油价共动(能源传导环) ----
    print('\n== 8. 能源传导环(BRENT_F 日收益) ==')
    dates6 = intersect(S, ['GOLD_F', 'DXY', 'BEI_10Y', 'BRENT_F'])
    ds6, R6 = rets(S, ['GOLD_F', 'DXY', 'BEI_10Y', 'BRENT_F'], dates6)
    r_bb, n6 = pearson(R6['BEI_10Y'], R6['BRENT_F'])
    print(f'corr(dBEI, dBRENT日收益) = {r_bb:+.4f} (n={n6}, '
          f't={t_of_r(r_bb, n6):.1f})')
    upb = [i for i in range(n6) if R6['BEI_10Y'][i] > 0.05]
    print(f'dBEI>+5bp 日: n={len(upb)}, '
          f'布伦特日均收益={mean([R6["BRENT_F"][i] for i in upb]):+.3f}%, '
          f'金日均={mean([R6["GOLD_F"][i] for i in upb]):+.3f}%, '
          f'美元日均={mean([R6["DXY"][i] for i in upb]):+.3f}%')
    # 控制: BEI 升且油跌 vs BEI 升且油升
    up_oilup = [i for i in upb if R6['BRENT_F'][i] > 0]
    up_oildn = [i for i in upb if R6['BRENT_F'][i] <= 0]
    print(f'  其中油同涨日 n={len(up_oilup)}: 金均={mean([R6["GOLD_F"][i] for i in up_oilup]):+.3f}% '
          f'美元均={mean([R6["DXY"][i] for i in up_oilup]):+.3f}%')
    print(f'  其中油跌日 n={len(up_oildn)}: 金均={mean([R6["GOLD_F"][i] for i in up_oildn]):+.3f}% '
          f'美元均={mean([R6["DXY"][i] for i in up_oildn]):+.3f}%')

    # ---- 9. 滚动相关稳定性 ----
    print('\n== 9. 63日滚动 corr(GOLD,DXY) 分布 ==')
    roll = []
    W = 63
    for i in range(W, n + 1):
        r0, _ = pearson(R['GOLD_F'][i - W:i], R['DXY'][i - W:i])
        roll.append((ds[i - 1], r0))
    vals = [r for _, r in roll]
    print(f'n窗={len(vals)} 均值={mean(vals):+.3f} 中位={median(vals):+.3f} '
          f'最小={min(vals):+.3f} 最大={max(vals):+.3f} '
          f'为正占比={sum(1 for v in vals if v>0)/len(vals)*100:.1f}%')
    # 末窗
    print(f'末窗(截至{roll[-1][0]}): {roll[-1][1]:+.3f}')

    print('\n== 复算完毕(全部数字可直接追溯至本脚本打印) ==')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default=DEFAULT_DATA,
                    help='data_slice.json(默认=本包切片,与原运行同版)')
    _args = ap.parse_args()
    main()
