#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R5 条目5 中国任务B 独立复算脚本(操作者席,零引用研究席代码路径)。

对象: 20261117T035814Z 中国宏观信用与制造业景气(CN_NEW_LOANS×CN_PMI_MFG
对 CHINEXT/FXI)判定档 CON-1/2/3 与报告关键统计值。
输入: 本目录 seat_data/(研究席同版 ia_cli history 原始输出,sha256 见 README)。

口径(与研究席声明一致):
- 股指日频→月频: 每日历月最后一个可得收盘为月末价,月收益=环比;
  2026-11 为残月(月末观测=2026-11-11)剔除;
- 宏观月值即序列观测(月份锚=月首);
- 先行 k=1 = 宏观(M) 对 r(M+1);PMI 相位按荣枯线 50 **严格**分组
  (>50 vs <50,PMI=50.0 持平月不入任一组——修订v2统一口径,审查MF-2);
- CI(信用脉冲,M)=sum(贷款 M-11..M)−sum(贷款 M-23..M-12),单位万亿;
- 百分位=100×count(CI史≤当前)/n(含当前,与判定档『仅4.9%月份不深于此值』
  措辞一致);
- Welch t/Satterthwaite df;Mann-Whitney 正态近似双侧 p;
- PMI×CI 同月相关=Pearson(重叠窗)。

空目录重放: 克隆本仓后,仓库根执行
  python3 docs/autonomous-rd/cn-task-b-20261117T035814Z/independent_recompute.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'seat_data')

EXPECT = {  # 判定档/报告引用值 → 复算判定(阈值见 main)
    'n_returns': 119,          # 月收益 2016-12..2026-10
    'pmi_n': 226,              # PMI 全史
    'pmi_below50': 69,         # 全史 PMI<50 月数(31%)
    'loans_n': 226,
    'loans_neg': 6,            # 全史负值月
    'loans_2026_10': -5846.0,  # 亿
    'ci_2026_10': -3.58,       # 万亿
    'ci_pct': 4.9,             # 百分位
    'ci_n': 203,
    # CON-1: k=1 相位(CHINEXT,严格<50 vs >50,修订v2)
    'k1_hi_n': 67, 'k1_hi_mean': -0.74, 'k1_hi_med': -1.22,
    'k1_hi_win': 39, 'k1_hi_sd': 7.50,
    'k1_lo_n': 48, 'k1_lo_mean': 2.14, 'k1_lo_med': 0.98,
    'k1_lo_win': 58, 'k1_lo_sd': 9.81,
    'welch_t': -1.70, 'welch_p': 0.092, 'mw_p': 0.120,
    'trim_lo': 1.58, 'trim_hi': -0.57,
    'k1_fxi_n': 48, 'k1_fxi_mean': 1.45, 'k1_fxi_win': 50,
    'k1_fxi_p': 0.250, 'fxi_lo_sd': 8.07, 'fxi_hi_sd': 6.20,
    'ties': 3,
    # 极值月(CON-1/CON-2)
    'm_2024_09': 37.6, 'm_2026_07': -23.0, 'm_2026_10': -23.0,
    'm_2025_08': 24.1,
    # CON-3: PMI vs CI 同月
    'pmi_ci_r': 0.204, 'pmi_ci_p': 0.026,
    # 先行网格上限(信用族全部 |r|≤0.10;全网格最大 |r|=0.176=PMI水平k=2)
    'ci_lead_maxabs': 0.10, 'grid_maxabs': 0.176,
    # 贷款族 t 网格(审查MF-3: max|t|=1.86,无一格p<0.05)
    'loans_max_t': 1.86, 'loans_max_r': 0.171, 'loans_max_p': 0.066,
    # 两资产耦合(MF-4: 1-r²≈88%方差互不共享)
    'pair_r': 0.351, 'pair_unshared': 0.876,
    # 情景锚
    'deep_ci_n': 14, 'deep_ci_chinext': -1.51,
    'dual_n': 24, 'dual_chinext': 2.75, 'dual_fxi': 0.96,
}


def load(metric):
    doc = json.load(open(os.path.join(DATA, metric + '.json'),
                         encoding='utf-8'))
    s = doc['data']['series']
    return list(zip(s['dates'], s['values']))


def month_end(series):
    """日频→{YYYY-MM: 最后可得(日期,收盘)}。"""
    out = {}
    for d, v in series:
        out[d[:7]] = (int(d[8:10]), v)   # 日期升序→后写覆盖=月末
    return out


def monthly_returns(me):
    months = sorted(me)
    return {b: 100.0 * (me[b][1] / me[a][1] - 1.0)
            for a, b in zip(months, months[1:])}


def mean(xs):
    return sum(xs) / len(xs)


def median(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def stdev(xs, ddof=1):
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - ddof))


def pearson(xs, ys):
    n = len(xs)
    mx, my = mean(xs), mean(ys)
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    return sxy / math.sqrt(sxx * syy)


def t_sf(t, df):
    """t 分布双侧 p(独立实现: 不完全 Beta 连分式)。"""
    x = df / (df + t * t)
    a, b = df / 2.0, 0.5
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log(1.0 - x))
    tiny = 1e-300
    c, d = 1.0, 1.0 - (a + b) * x / (a + 1.0)
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d
    for j in range(1, 300):
        m = 2 * j
        num = j * (b - j) * x / ((a + m - 1.0) * (a + m))
        d = 1.0 + num * d
        d = tiny if abs(d) < tiny else d
        c = 1.0 + num / c
        c = tiny if abs(c) < tiny else c
        d = 1.0 / d
        h *= d * c
        num = -(a + j) * (a + b + j) * x / ((a + m) * (a + m + 1.0))
        d = 1.0 + num * d
        d = tiny if abs(d) < tiny else d
        c = 1.0 + num / c
        c = tiny if abs(c) < tiny else c
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 3e-12:
            break
    ib = front * h / a
    return ib                        # = P(T>|t|) 双侧


def welch(xs, ys):
    nx, ny = len(xs), len(ys)
    vx, vy = stdev(xs) ** 2, stdev(ys) ** 2
    t = (mean(xs) - mean(ys)) / math.sqrt(vx / nx + vy / ny)
    df = (vx / nx + vy / ny) ** 2 / \
        ((vx / nx) ** 2 / (nx - 1) + (vy / ny) ** 2 / (ny - 1))
    return t, df, t_sf(t, df)


def mann_whitney_p(xs, ys):
    """正态近似,秩=并列取中位(方差不作并列修正,与研究席同口径)。"""
    vals = sorted([(v, 0) for v in xs] + [(v, 1) for v in ys])
    ranks = [0.0] * len(vals)
    i = 0
    while i < len(vals):
        j = i
        while j < len(vals) and vals[j][0] == vals[i][0]:
            j += 1
        mid = (i + j - 1) / 2.0 + 1.0          # 并列组中位秩
        for k2 in range(i, j):
            ranks[k2] = mid
        i = j
    r1 = sum(r for r, (_, g) in zip(ranks, vals) if g == 0)
    n1, n2 = len(xs), len(ys)
    mu = n1 * (n1 + n2 + 1) / 2.0
    sd = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12.0)
    z = (r1 - mu) / sd
    return 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(z) / math.sqrt(2.0))))


def drop_residual(me):
    """剔除残月: 月末观测日号<20=该月未走完(研究席 2026-11 残月规则)。"""
    return {m: dv for m, dv in me.items() if dv[0] >= 20}


def main():
    ok = True

    def chk(name, got, exp, tol):
        nonlocal ok
        good = abs(got - exp) <= tol
        ok &= good
        print('  %s %s: got=%s expect=%s' % ('✅' if good else '❌',
                                             name, got, exp))

    pmi = {d[:7]: v for d, v in load('CN_PMI_MFG')}
    loans = {d[:7]: v for d, v in load('CN_NEW_LOANS')}
    me_ch = drop_residual(month_end(load('CHINEXT')))
    me_fx = drop_residual(month_end(load('FXI')))
    r_ch = monthly_returns(me_ch)
    r_fxi = monthly_returns(me_fx)

    # ── 样本与全史 ──
    print('样本与全史')
    chk('月收益 n', len(r_ch), EXPECT['n_returns'], 0)
    chk('月收益首月', 1 if min(r_ch) == '2016-12' else 0, 1, 0)
    chk('月收益末月', 1 if max(r_ch) == '2026-10' else 0, 1, 0)
    chk('PMI n', len(pmi), EXPECT['pmi_n'], 0)
    below = sum(1 for v in pmi.values() if v < 50)
    chk('PMI<50 全史月数', below, EXPECT['pmi_below50'], 0)
    chk('PMI<50 占比%', round(100.0 * below / len(pmi)), 31, 0)
    chk('贷款 n', len(loans), EXPECT['loans_n'], 0)
    chk('贷款负值月', sum(1 for v in loans.values() if v < 0),
        EXPECT['loans_neg'], 0)
    chk('2026-10 贷款(亿)', loans['2026-10'], EXPECT['loans_2026_10'], 0.5)

    # ── CI 信用脉冲 ──
    print('信用脉冲 CI(12月滚动差,万亿)')
    months = sorted(loans)
    ci = {}
    for i, m in enumerate(months):
        if i < 23:
            continue
        cur = sum(loans[months[j]] for j in range(i - 11, i + 1))
        prev = sum(loans[months[j]] for j in range(i - 23, i - 11))
        ci[m] = (cur - prev) / 10000.0        # 月键=YYYY-MM
    chk('CI 可得月数', len(ci), EXPECT['ci_n'], 0)
    cur_ci = ci['2026-10']
    chk('CI(2026-10) 万亿', round(cur_ci, 2), EXPECT['ci_2026_10'], 0.005)
    pct = 100.0 * sum(1 for v in ci.values() if v <= cur_ci) / len(ci)
    chk('CI 历史百分位', round(pct, 1), EXPECT['ci_pct'], 0.15)

    # ── CON-1: PMI 相位 k=1(严格分组,=50.0 不入组) ──
    print('CON-1: PMI>50 vs PMI<50(严格) 对 CHINEXT/FXI 次月收益(k=1)')
    sig = [m for m in sorted(r_ch) if m in pmi]      # 信号月=有月收益当月
    hi, lo, tie = [], [], []
    for m in sig:
        nm = next_month(m)
        if nm not in r_ch:
            continue
        if pmi[m] > 50:
            hi.append(r_ch[nm])
        elif pmi[m] < 50:
            lo.append(r_ch[nm])
        else:
            tie.append(m)
    chk('持平月(PMI=50.0)数', len(tie), EXPECT['ties'], 0)
    chk('高位组 n', len(hi), EXPECT['k1_hi_n'], 0)
    chk('低位组 n', len(lo), EXPECT['k1_lo_n'], 0)
    chk('高位组月均%', round(mean(hi), 2), EXPECT['k1_hi_mean'], 0.005)
    chk('低位组月均%', round(mean(lo), 2), EXPECT['k1_lo_mean'], 0.005)
    chk('高位组中位%', round(median(hi), 2), EXPECT['k1_hi_med'], 0.005)
    chk('低位组中位%', round(median(lo), 2), EXPECT['k1_lo_med'], 0.005)
    chk('高位组上涨概率%', round(100.0 * sum(v > 0 for v in hi) / len(hi)),
        EXPECT['k1_hi_win'], 0)
    chk('低位组上涨概率%', round(100.0 * sum(v > 0 for v in lo) / len(lo)),
        EXPECT['k1_lo_win'], 0)
    chk('高位组σ%', round(stdev(hi), 2), EXPECT['k1_hi_sd'], 0.005)
    chk('低位组σ%', round(stdev(lo), 2), EXPECT['k1_lo_sd'], 0.005)
    t, df, p = welch(hi, lo)
    chk('Welch t', round(t, 2), EXPECT['welch_t'], 0.005)
    chk('Welch df', round(df), 84, 1)
    chk('Welch p', round(p, 3), EXPECT['welch_p'], 0.0015)
    chk('MW p(严格同口径)', round(mann_whitney_p(lo, hi), 3),
        EXPECT['mw_p'], 0.0015)
    trim = lambda xs: mean(sorted(xs)[2:-2])        # 去首尾各2月
    chk('低位组截尾均值%', round(trim(lo), 2), EXPECT['trim_lo'], 0.005)
    chk('高位组截尾均值%', round(trim(hi), 2), EXPECT['trim_hi'], 0.005)
    # FXI 端(MC-3/SCN-4 引用)
    hi_f, lo_f = [], []
    for m in sig:
        nm = next_month(m)
        if nm not in r_fxi or m not in pmi:
            continue
        if pmi[m] > 50:
            hi_f.append(r_fxi[nm])
        elif pmi[m] < 50:
            lo_f.append(r_fxi[nm])
    chk('FXI 低位组 n', len(lo_f), EXPECT['k1_fxi_n'], 0)
    chk('FXI 低位组月均%', round(mean(lo_f), 2), EXPECT['k1_fxi_mean'], 0.005)
    chk('FXI 低位组胜率%', round(100.0 * sum(v > 0 for v in lo_f) / len(lo_f)),
        EXPECT['k1_fxi_win'], 0)
    chk('FXI 低位组σ%', round(stdev(lo_f), 2), EXPECT['fxi_lo_sd'], 0.005)
    chk('FXI 高位组σ%', round(stdev(hi_f), 2), EXPECT['fxi_hi_sd'], 0.005)
    tf, dff, pf = welch(hi_f, lo_f)
    chk('FXI Welch p', round(pf, 3), EXPECT['k1_fxi_p'], 0.0015)

    # ── 极值月 ──
    print('极值月(报告引用)')
    for m, exp in (('2024-09', EXPECT['m_2024_09']),
                   ('2025-08', EXPECT['m_2025_08']),
                   ('2026-07', EXPECT['m_2026_07']),
                   ('2026-10', EXPECT['m_2026_10'])):
        chk('%s CHINEXT 月收益%%' % m, round(r_ch[m], 1), exp, 0.05)

    # ── CON-3: PMI vs CI 同月 ──
    print('CON-3: PMI 水平 vs CI 同月相关(重叠窗)')
    common = [m for m in sorted(r_ch) if m in pmi and m in ci]
    r = pearson([pmi[m] for m in common], [ci[m] for m in common])
    n = len(common)
    tr = r * math.sqrt((n - 2) / (1 - r * r))
    chk('n', n, 119, 0)
    chk('r', round(r, 3), EXPECT['pmi_ci_r'], 0.0005)
    chk('p', round(t_sf(tr, n - 2), 3), EXPECT['pmi_ci_p'], 0.0015)

    # ── 先行网格上限 ──
    print('先行相关网格上限(CON-2 断言)')
    leads = []
    for k in (1, 2, 3):
        pairs = [(m, mk) for m in sorted(r_ch) if m in pmi
                 for mk in [shift(m, k)] if mk in r_ch]
        leads.append(pearson([pmi[m] for m, _ in pairs],
                             [r_ch[mk] for _, mk in pairs]))
    ci_leads = []
    for rset in (r_ch, r_fxi):
        for k in (1, 2, 3):
            pairs = [(m, mk) for m in sorted(rset) if m in ci
                     for mk in [shift(m, k)] if mk in rset]
            ci_leads.append(pearson([ci[m] for m, _ in pairs],
                                    [rset[mk] for _, mk in pairs]))
    print('  PMI 水平 k=1..3 r:', [round(v, 3) for v in leads])
    print('  CI 先行 r(CHINEXT+FXI, k=1..3):', [round(v, 3) for v in ci_leads])
    ci_max = max(abs(v) for v in ci_leads)
    good = ci_max <= EXPECT['ci_lead_maxabs']
    print('  %s CI 先行 |r|≤0.10 断言: max=%.3f' %
          ('✅' if good else '❌', ci_max))
    ok &= good
    chk('全网格最大 |r|(PMI水平k=2)', round(max(abs(v) for v in leads), 3),
        EXPECT['grid_maxabs'], 0.0005)

    # ── 贷款族 t 网格(审查MF-3: max|t|=1.86 且无一格 p<0.05) ──
    print('贷款族(贷款/近12月均值比)先行格 t(审查MF-3)')
    ratio = {}
    lkeys = sorted(loans)
    for i, m in enumerate(lkeys):
        if i < 11:
            continue
        ratio[m] = loans[m] / mean([loans[j] for j in lkeys[i - 11:i + 1]])
    cells = []
    for rset, aname in ((r_ch, 'CHINEXT'), (r_fxi, 'FXI')):
        for k in (1, 2, 3):
            pairs = [(m, mk) for m in sorted(rset) if m in ratio
                     for mk in [shift(m, k)] if mk in rset]
            if len(pairs) < 10:
                continue
            rr = pearson([ratio[m] for m, _ in pairs],
                         [rset[mk] for _, mk in pairs])
            nn = len(pairs)
            tt = rr * math.sqrt((nn - 2) / (1 - rr * rr))
            cells.append((aname, k, rr, tt, t_sf(tt, nn - 2)))
    mx = max(cells, key=lambda c: abs(c[3]))
    print('  全格:', ['%s k=%d r=%+.3f t=%+.2f p=%.3f' % c for c in cells])
    chk('max|t| 格资产=CHINEXT', 1 if mx[0] == 'CHINEXT' else 0, 1, 0)
    chk('max|t| 格 k', mx[1], 3, 0)
    chk('max|t|', round(abs(mx[3]), 2), EXPECT['loans_max_t'], 0.005)
    chk('max格 r', round(mx[2], 3), EXPECT['loans_max_r'], 0.0005)
    chk('max格 p', round(mx[4], 3), EXPECT['loans_max_p'], 0.0015)
    good = all(c[4] >= 0.05 for c in cells)
    print('  %s 贷款族无一格 p<0.05: min p=%.3f' %
          ('✅' if good else '❌', min(c[4] for c in cells)))
    ok &= good

    # ── 两资产耦合(MF-4: 1-r²≈88%) ──
    print('CHINEXT~FXI 月收益耦合(MF-4)')
    common2 = [m for m in sorted(r_ch) if m in r_fxi]
    pr = pearson([r_ch[m] for m in common2], [r_fxi[m] for m in common2])
    chk('r', round(pr, 3), EXPECT['pair_r'], 0.0005)
    chk('1-r²(未共享方差)', round(1 - pr * pr, 3), EXPECT['pair_unshared'],
        0.0005)

    # ── 情景锚 ──
    print('情景锚(报告 L4)')
    deep = [r_ch[nm] for m in sorted(r_ch) if m in ci and ci[m] < -3.0
            for nm in [next_month(m)] if nm in r_ch]
    chk('CI<-3万亿 事件数', len(deep), EXPECT['deep_ci_n'], 0)
    chk('深收缩次月 CHINEXT 月均%', round(mean(deep), 2),
        EXPECT['deep_ci_chinext'], 0.005)
    dual = [m for m in sorted(r_ch) if m in pmi and m in ci
            and pmi[m] < 50 and ci[m] < 0]
    dual_ch = [r_ch[next_month(m)] for m in dual
               if next_month(m) in r_ch]
    dual_fx = [r_fxi[next_month(m)] for m in dual
               if next_month(m) in r_fxi]
    chk('双重收缩事件数', len(dual_ch), EXPECT['dual_n'], 0)
    chk('双重收缩次月 CHINEXT%', round(mean(dual_ch), 2),
        EXPECT['dual_chinext'], 0.005)
    chk('双重收缩次月 FXI%', round(mean(dual_fx), 2),
        EXPECT['dual_fxi'], 0.005)

    print('\n%s: 判定档与报告关键统计值独立复算%s' %
          ('PASS' if ok else 'FAIL',
           '全部吻合' if ok else '存在失配'))
    sys.exit(0 if ok else 1)


def next_month(m):
    y, mo = int(m[:4]), int(m[5:7])
    return '%04d-%02d' % (y + mo // 12, mo % 12 + 1)


def shift(m, k):
    out = m
    for _ in range(k):
        out = next_month(out)
    return out


if __name__ == '__main__':
    main()
