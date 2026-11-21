#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R5 条目3 独立复算脚本(操作者席,零引用研究席/前审查席中间结果)。

对象: E2E 20261116T222254Z(BEI_10Y 上行阶段 GOLD_F×DXY)修正后三争点。
输入: 本目录 data_slice.json(=同版原始输入完整抽取,sha256 见 README)。

口径(与研究席声明一致,重放须按此):
- 水平序列按 observation_date 精确匹配取交集后,相邻对齐日求变化:
  价格类(GOLD_F/DXY/BRENT_F)= pct 收益 100*(P_t/P_{t-1}-1);
  利率类(BEI_10Y/UST_10Y/TIPS_10Y)= 日变化 pp;
- 相关=皮尔逊;t=r*sqrt((n-2)/(1-r^2));
- OLS 含截距、手写正规方程、经典标准误(自由度 n-k,k=含截距自变量数);
- 实际收益率腿 = dTIPS_10Y 直取(非 UST-BEI 差)。

验证的三个修正(Audit-R5 条目3):
  (1) corr(dBEI,dBRENT)=0.3383 → r²≈0.114(≈11.4% 方差,非"约三成";
      同期相关,非先行/因果);
  (2) 金方程 se_dBEI=0.686(正文原 0.678)、美元方程 se_dBEI=0.259(原 0.256);
  (3) 63 日滚动最长连续非负段终点=2022-05-25(原 2022-05-26;该日窗
      r=-0.0148 已转负)。

空目录重放: 克隆本仓后,仓库根执行
  python3 docs/autonomous-rd/e2e-corrected-20261116T222254Z/independent_recompute.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data_slice.json')

EXPECT = {  # 修正后应得数值(判定阈值在 main 内逐项给出)
    'r_bei_brent': 0.3383,
    'r2_bei_brent': 0.1145,
    'gold_se_bei': 0.686,
    'usd_se_bei': 0.259,
    'gold_beta_bei': -0.734,
    'usd_beta_bei': 1.152,
    'gold_beta_tips': -6.692,
    'usd_beta_tips': 2.812,
    'seg_len': 55,
    'seg_end': '2022-05-25',
    'window_0526_r': -0.0148,
    'n_windows': 2449,
}


def load(path):
    doc = json.load(open(path, encoding='utf-8'))
    return {k: dict(zip(e['dates'], e['values']))
            for k, e in doc['series'].items()}


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return sxy / math.sqrt(sum((a - mx) ** 2 for a in x)
                           * sum((b - my) ** 2 for b in y))


def ols3(y, x1, x2):
    """y ~ 1 + x1 + x2;返回 (beta, se, r2),经典标准误 df=n-3。"""
    N = len(y)
    X = [[1.0] * N, x1, x2]
    k = 3
    A = [[sum(a * b for a, b in zip(X[r], X[c])) for c in range(k)]
         for r in range(k)]
    bv = [sum(xr * yi for xr, yi in zip(X[r], y)) for r in range(k)]
    M = [A[i][:] + [bv[i]] for i in range(k)]
    for c in range(k):
        piv = next(r for r in range(c, k) if abs(M[r][c]) > 1e-12)
        M[c], M[piv] = M[piv], M[c]
        pv = M[c][c]
        M[c] = [v / pv for v in M[c]]
        for r in range(k):
            if r != c and M[r][c]:
                f = M[r][c]
                M[r] = [vr - f * vc for vr, vc in zip(M[r], M[c])]
    beta = [M[i][k] for i in range(k)]
    e = [yi - sum(bi * xi for bi, xi in zip(beta, row))
         for yi, row in zip(y, zip(*X))]
    s2 = sum(v * v for v in e) / (N - k)
    Aug = [A[i][:] + [1.0 if i == j else 0.0 for j in range(k)]
           for i in range(k)]
    for c in range(k):
        piv = next(r for r in range(c, k) if abs(Aug[r][c]) > 1e-12)
        Aug[c], Aug[piv] = Aug[piv], Aug[c]
        pv = Aug[c][c]
        Aug[c] = [v / pv for v in Aug[c]]
        for r in range(k):
            if r != c and Aug[r][c]:
                f = Aug[r][c]
                Aug[r] = [vr - f * vc for vr, vc in zip(Aug[r], Aug[c])]
    se = [math.sqrt(s2 * Aug[i][k + i]) for i in range(k)]
    tss = sum((yi - sum(y) / N) ** 2 for yi in y)
    r2 = 1 - sum(v * v for v in e) / tss
    return beta, se, r2


def changes(dates, m, price):
    out = []
    for d0, d1 in zip(dates, dates[1:]):
        v0, v1 = m[d0], m[d1]
        out.append(100.0 * (v1 / v0 - 1.0) if price else v1 - v0)
    return out


def main():
    S = load(DATA)
    ok = True

    def check(name, got, exp, tol):
        nonlocal ok
        good = abs(got - exp) <= tol
        ok &= good
        print('  %s %s: got=%s expect=%s' % ('✅' if good else '❌',
                                             name, got, exp))

    # ── L5: 金/美元/油/BEI/TIPS 水平交集 → 相邻对齐日变化 ──
    dates5 = sorted(set(S['GOLD_F']) & set(S['DXY']) & set(S['BRENT_F'])
                    & set(S['BEI_10Y']) & set(S['TIPS_10Y']))
    dG = changes(dates5, S['GOLD_F'], True)
    dD = changes(dates5, S['DXY'], True)
    dBEI = changes(dates5, S['BEI_10Y'], False)
    dTIPS = changes(dates5, S['TIPS_10Y'], False)
    n = len(dG)
    print('L5 交集日=%d → 相邻变化对 n=%d' % (len(dates5), n))
    assert n == 2493, 'n 应为 2493'

    # ── 争点1 ──
    print('\n争点1: corr(dBEI,dBRENT) 解释修正')
    dB = changes(dates5, S['BRENT_F'], True)
    r = pearson(dBEI, dB)
    t = r * math.sqrt((n - 2) / (1 - r * r))
    check('r', round(r, 4), EXPECT['r_bei_brent'], 0.0005)
    check('r²(方差解释占比)', round(r * r, 4), EXPECT['r2_bei_brent'], 0.001)
    print('  t=%.1f(期望17.9)' % t)

    # ── 争点2 ──
    print('\n争点2: 金/美元方程标准误修正(dTIPS 直取腿)')
    bg, sg, r2g = ols3(dG, dBEI, dTIPS)
    bd, sd, r2d = ols3(dD, dBEI, dTIPS)
    check('金 se_dBEI', round(sg[1], 3), EXPECT['gold_se_bei'], 0.001)
    check('金 β_dBEI', round(bg[1], 3), EXPECT['gold_beta_bei'], 0.001)
    check('金 β_dTIPS', round(bg[2], 3), EXPECT['gold_beta_tips'], 0.001)
    print('  金 R²=%.3f(期望0.090) t_dBEI=%.2f(期望-1.1)'
          % (r2g, bg[1] / sg[1]))
    check('美元 se_dBEI', round(sd[1], 3), EXPECT['usd_se_bei'], 0.001)
    check('美元 β_dBEI', round(bd[1], 3), EXPECT['usd_beta_bei'], 0.001)
    check('美元 β_dTIPS', round(bd[2], 3), EXPECT['usd_beta_tips'], 0.001)
    print('  美元 R²=%.3f(期望0.110) t_dBEI=%.2f(期望+4.4)'
          % (r2d, bd[1] / sd[1]))

    # ── 争点3 ──
    print('\n争点3: 63日滚动 corr(dGOLD,dDXY) 最长非负段终点修正(金/美元对齐对)')
    gdd = sorted(set(S['GOLD_F']) & set(S['DXY']))
    chd = gdd[1:]
    dG2 = [100.0 * (S['GOLD_F'][b] / S['GOLD_F'][a] - 1.0)
           for a, b in zip(gdd, gdd[1:])]
    dD2 = [100.0 * (S['DXY'][b] / S['DXY'][a] - 1.0)
           for a, b in zip(gdd, gdd[1:])]
    W = 63
    roll = [(chd[i], pearson(dG2[i - W + 1:i + 1], dD2[i - W + 1:i + 1]))
            for i in range(W - 1, len(dG2))]
    check('窗数(金/美元对齐对2511上)', len(roll), EXPECT['n_windows'], 0)
    best, bs, be_, cur, cs = 0, None, None, 0, None
    for dt, rv in roll:
        if rv >= 0:
            if cur == 0:
                cs = dt
            cur += 1
            if cur > best:
                best, bs, be_ = cur, cs, dt
        else:
            cur = 0
    check('最长非负段窗数', best, EXPECT['seg_len'], 0)
    print('  段区间=%s..%s(期望终点%s)' % (bs, be_, EXPECT['seg_end']))
    ok &= (be_ == EXPECT['seg_end'])
    r0526 = next(rv for dt, rv in roll if dt == '2022-05-26')
    check('窗末2022-05-26的r', round(r0526, 4), EXPECT['window_0526_r'], 0.0005)

    print('\n%s: 三争点修正数值全部复算吻合' %
          ('PASS' if ok else 'FAIL'))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
