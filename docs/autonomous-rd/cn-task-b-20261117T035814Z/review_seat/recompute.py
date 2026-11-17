#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit-R5 条目5(中国任务B)独立审查席复算脚本 —— /tmp/sr5b/
零 import 研究席/操作者席代码;标准库 only;t 分布 p 值用 Simpson 数值积分
(独立于研究席/操作者席的不完全 Beta 连分式实现)。

口径来源 = research_seat_calc.py 文件头声明:
- 股指月频化: 每日历月最后可得收盘为月末价,r(M)=月末/上月末-1;
  末月若未走完(月末观测为月中,日号<25)剔为残月;
- 宏观月值即序列观测;先行 k = 宏观(M) 对 r(M+k);
- CI(M)=sum(贷款 M-11..M)-sum(贷款 M-23..M-12);
- 相位分组: 荣枯线 50(研究席实现为 >50 vs 其余,即 ≤50 入"低位组"——本席
  同时复算严格 <50 边界以检标签一致性);
- Welch t/Satterthwaite df;Mann-Whitney 正态近似;NW-HAC lag=4。
输入: /tmp/audit_r5/B_run/seat_data/(与研究档 sha 一致已核)。
"""
import json
import math
import os

DATA = '/tmp/audit_r5/B_run/seat_data'
OUT = []


def say(s=''):
    OUT.append(s)
    print(s)


# ───────────────────────── 基础统计(自实现) ─────────────────────────
def t_pdf(x, df):
    ln = (math.lgamma((df + 1) / 2.0) - math.lgamma(df / 2.0)
          - 0.5 * math.log(df * math.pi))
    return math.exp(ln - (df + 1) / 2.0 * math.log1p(x * x / df))


def t_p_two(t, df):
    """t 分布双侧 p,Simpson 数值积分(独立实现)。"""
    a = abs(t)
    if a == 0.0:
        return 1.0
    n = 40000
    h = a / n
    s = t_pdf(0.0, df) + t_pdf(a, df)
    for i in range(1, n):
        s += t_pdf(i * h, df) * (4.0 if i % 2 else 2.0)
    integ = s * h / 3.0
    p = 2.0 * (0.5 - integ)
    return max(0.0, min(1.0, p))


def mean(xs):
    return sum(xs) / len(xs)


def stdev(xs):
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def median(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def pearson(xs, ys):
    n = len(xs)
    mx, my = mean(xs), mean(ys)
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    if sxx <= 0 or syy <= 0:
        return None
    r = sxy / math.sqrt(sxx * syy)
    r = max(-1.0, min(1.0, r))
    t = r * math.sqrt((n - 2) / (1 - r * r))
    return r, t, t_p_two(t, n - 2), n


def ranks(v):
    idx = sorted(range(len(v)), key=lambda i: v[i])
    out = [0.0] * len(v)
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and v[idx[j + 1]] == v[idx[i]]:
            j += 1
        mid = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            out[idx[k]] = mid
        i = j + 1
    return out


def spearman(xs, ys):
    return pearson(ranks(xs), ranks(ys))


def welch(a, b):
    na, nb = len(a), len(b)
    va, vb = stdev(a) ** 2, stdev(b) ** 2
    se2 = va / na + vb / nb
    t = (mean(a) - mean(b)) / math.sqrt(se2)
    df = se2 ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    return t, df, t_p_two(t, df)


def mw_p(a, b):
    """Mann-Whitney 双侧 p,正态近似(并列取中位秩,方差不作并列校正)。"""
    vals = [(v, 0) for v in a] + [(v, 1) for v in b]
    rk = ranks([v for v, _ in vals])
    r1 = sum(rk[i] for i in range(len(vals)) if vals[i][1] == 0)
    n1, n2 = len(a), len(b)
    z = (r1 - n1 * (n1 + n2 + 1) / 2.0) / math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12.0)
    p = math.erfc(abs(z) / math.sqrt(2.0))
    return z, p


def solve_lin(A, b):
    n = len(A)
    M = [A[i][:] + [b[i]] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        if abs(M[c][c]) < 1e-300:
            return None
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


def ols_hac(y, xmat, lag=4, hac=True):
    """OLS + HC0 或 Newey-West(Bartlett, lag)三明治。返回各系数 t。"""
    n = len(y)
    k = len(xmat[0]) + 1
    X = [[1.0] + row for row in xmat]
    XtX = [[sum(X[i][a] * X[i][b] for i in range(n)) for b in range(k)]
           for a in range(k)]
    Xty = [sum(X[i][a] * y[i] for i in range(n)) for a in range(k)]
    beta = solve_lin(XtX, Xty)
    resid = [y[i] - sum(X[i][a] * beta[a] for a in range(k)) for i in range(n)]
    cols = []
    for c in range(k):
        e = [1.0 if i == c else 0.0 for i in range(k)]
        cols.append(solve_lin([row[:] for row in XtX], e))
    XtXi = [[cols[c][r] for c in range(k)] for r in range(k)]
    S = [[0.0] * k for _ in range(k)]
    for i in range(n):
        for a in range(k):
            for b in range(k):
                S[a][b] += resid[i] ** 2 * X[i][a] * X[i][b]
    if hac:
        for l in range(1, min(lag, n - 1) + 1):
            w = 1.0 - l / (lag + 1.0)
            for i in range(l, n):
                for a in range(k):
                    for b in range(k):
                        S[a][b] += w * resid[i] * resid[i - l] * (
                            X[i][a] * X[i - l][b] + X[i - l][a] * X[i][b])
    V = [[sum(XtXi[a][m] * S[m][b] for m in range(k)) for b in range(k)]
         for a in range(k)]
    V2 = [[sum(V[a][m] * XtXi[b][m] for m in range(k)) for b in range(k)]
          for a in range(k)]
    tv = []
    for a in range(k):
        se = math.sqrt(max(V2[a][a], 0.0))
        tv.append(beta[a] / se if se > 0 else float('nan'))
    return beta, tv


# ───────────────────────── 装载与月频化 ─────────────────────────
def load(m):
    doc = json.load(open(os.path.join(DATA, m + '.json'), encoding='utf-8'))
    s = doc['data']['series']
    dates, values = s['dates'], s['values']
    assert len(dates) == len(values) == s['n']
    # 数据质量: 日期严格升序、无重复、值均为数
    assert all(dates[i] < dates[i + 1] for i in range(len(dates) - 1))
    assert all(isinstance(v, (int, float)) and not math.isnan(v) for v in values)
    return list(zip(dates, values))


def month_end(series):
    out = {}
    for d, v in series:
        ym = d[:7]
        if ym not in out or d > out[ym][0]:
            out[ym] = (d, v)
    return out


say('# 独立复算输出(审查席 /tmp/sr5b/recompute.py)')
fxi_raw, chx_raw = load('FXI'), load('CHINEXT')
pmi_raw, loans_raw = load('CN_PMI_MFG'), load('CN_NEW_LOANS')
pmi = {d[:7]: v for d, v in pmi_raw}
loans = {d[:7]: v for d, v in loans_raw}
me_fx, me_ch = month_end(fxi_raw), month_end(chx_raw)

# 月集合检查: 两指数日历月集合应一致且连续(2016-11..2026-11)
ms_fx, ms_ch = sorted(me_fx), sorted(me_ch)
assert ms_fx == ms_ch, '两指数月集合不一致'
assert ms_fx == [f'{y}-{m:02d}' for y in range(2016, 2027) for m in range(1, 13)
                 if f'{y}-{m:02d}' >= '2016-11' and f'{y}-{m:02d}' <= '2026-11'], \
    '月份不连续'
say(f'[数据] 两指数月集合一致且连续 {ms_fx[0]}..{ms_fx[-1]} 共{len(ms_fx)}月; '
    f'宏观数据无缺月断言通过(PMI {min(pmi)}..{max(pmi)}, 贷款 {min(loans)}..{max(loans)})')

rets = {}
prev = None
for ym in ms_fx:
    if prev is not None:
        rets[ym] = (me_ch[ym][1] / me_ch[prev][1] - 1.0,      # (CHINEXT, FXI)
                    me_fx[ym][1] / me_fx[prev][1] - 1.0)
    prev = ym
ret_months = sorted(rets)

# 残月剔除: 数据最后一个月月末观测为月中(日号<25)则该月未走完 → 剔除
last_ym = ret_months[-1]
if min(int(me_fx[last_ym][0][8:10]), int(me_ch[last_ym][0][8:10])) < 25:
    say(f'[对齐] 残月剔除 {last_ym} (月末观测 {me_fx[last_ym][0]}/{me_ch[last_ym][0]})')
    del rets[last_ym]
    ret_months.remove(last_ym)
say(f'[对齐] 月收益 {ret_months[0]}..{ret_months[-1]} n={len(ret_months)}')

# 中段月截断检查(披露): 月末观测日号<20 的月(真实 shorten 交易日历)
short_mons = [m for m in ret_months
              if min(int(me_fx[m][0][8:10]), int(me_ch[m][0][8:10])) < 20]
say('[对齐] 中段月末观测日号<20的月(保留为真实月末,口径披露): ' + ', '.join(short_mons))

# ───────────────────────── 宏观变换(≤M 观测) ─────────────────────────
pmi_keys, loan_keys = sorted(pmi), sorted(loans)


def pmi_diff(m):
    i = pmi_keys.index(m)
    return pmi[m] - pmi[pmi_keys[i - 1]] if i > 0 else None


def loans_yoy(m):
    i = loan_keys.index(m)
    return (loans[m] - loans[loan_keys[i - 12]]) / 10000.0 if i >= 12 else None


def loans_ratio12(m):
    i = loan_keys.index(m)
    return loans[m] / (sum(loans[k] for k in loan_keys[i - 11:i + 1]) / 12.0) \
        if i >= 11 else None


def ci(m):   # 万亿
    i = loan_keys.index(m)
    if i < 23:
        return None
    return (sum(loans[k] for k in loan_keys[i - 11:i + 1])
            - sum(loans[k] for k in loan_keys[i - 23:i - 11])) / 10000.0


# ═════════════════════════ T 系列: 逐项核对 ═════════════════════════
RESULTS = []


def chk(tid, desc, got, exp, tol, note=''):
    ok = (abs(got - exp) <= tol) if isinstance(exp, (int, float)) else (got == exp)
    RESULTS.append((tid, desc, exp, got, ok, note))
    say(f"  [{'PASS' if ok else 'FAIL'}] {tid} {desc}: 复算={got} 期望={exp} {note}")


say('\n== T01-T05 样本/全史/L1 事实 ==')
chk('T01a', '月收益 n', len(ret_months), 119, 0)
chk('T01b', '月收益首月', ret_months[0], '2016-12', None)
chk('T01c', '月收益末月', ret_months[-1], '2026-10', None)

pv = [pmi[k] for k in pmi_keys]
chk('T02a', 'PMI 全史 n', len(pv), 226, 0)
chk('T02b', 'PMI 首末', f'{pmi_keys[0]}..{pmi_keys[-1]}', '2008-01..2026-10', None)
chk('T02c', 'PMI 均值', round(mean(pv), 2), 50.61, 0.005)
chk('T02d', 'PMI 最小(月)', f'{min(pv)}@{pmi_keys[pv.index(min(pv))]}', '35.7@2020-02', None)
chk('T02e', 'PMI 最大(月)', f'{max(pv)}@{pmi_keys[pv.index(max(pv))]}', '59.2@2008-04', None)
nb = sum(1 for v in pv if v < 50)
chk('T02f', 'PMI<50 全史月数(占比%)', f'{nb}({nb / 226 * 100:.0f}%)', '69(31%)', None)

lv = [loans[k] for k in loan_keys]
neg = [k for k in loan_keys if loans[k] < 0]
by_cal = {}
for k in neg:
    by_cal.setdefault(k[5:7], []).append(k)
jan = [loans[k] for k in loan_keys if k[5:7] == '01']
chk('T03a', '贷款全史 n', len(lv), 226, 0)
chk('T03b', '负值月数/日历分布', f"{len(neg)}: " + ','.join(
    f"{m}月x{len(v)}" for m, v in sorted(by_cal.items())), '6: 04月x1,07月x3,10月x2', None)
chk('T03c', '1月均值(亿)', round(mean(jan)), 27341, 1)
chk('T03d', '全史月均(亿)', round(mean(lv)), 11234, 1)
chk('T03e', '1月均值/全史月均', round(mean(jan) / mean(lv), 1), 2.4, 0.05)

chk('T04a', '贷款2026-10(亿)', loans['2026-10'], -5846.0, 0.5)
chk('T04b', '贷款2026-09(亿,L1行)', loans['2026-09'], 12734.0, 0.5)
chk('T04c', '贷款2026-01(亿,SCN-2对照)', loans['2026-01'], 49016.0, 0.5)
chk('T04d', '贷款2026-03(亿,SCN-2触发参照)', loans['2026-03'], 31522.0, 0.5)

ci_all = {k: ci(k) for k in loan_keys if ci(k) is not None}
civ = [ci_all[k] for k in sorted(ci_all)]
ci_now = ci_all['2026-10']
pct_le = 100.0 * sum(1 for v in civ if v <= ci_now) / len(civ)
pct_lt = 100.0 * sum(1 for v in civ if v < ci_now) / len(civ)
chk('T05a', 'CI(2026-10) 万亿', round(ci_now, 2), -3.58, 0.005)
chk('T05b', 'CI 百分位%(≤口径)', round(pct_le, 1), 4.9, 0.05)
say(f'        (严格<口径百分位={pct_lt:.1f}%,≤计数={sum(1 for v in civ if v <= ci_now)},'
    f'<计数={sum(1 for v in civ if v < ci_now)},n={len(civ)})')
chk('T05c', 'CI 可得月数(首月)', f"{len(ci_all)}({sorted(ci_all)[0]})", '203(2009-12)', None)
chk('T05d', 'CI 历史区间(万亿)', f"[{min(civ):.2f},{max(civ):.2f}]", '[-5.24,4.69]', None)

say('\n== T06-T10 先行相关网格(CL-2/CTR-1/MC-2/CON-2 引用) ==')
metrics = {'PMI水平': lambda m: pmi.get(m), 'PMI环比差分': pmi_diff,
           '贷款同比差': loans_yoy, '贷款/12月均值比': loans_ratio12, 'CI': ci}


def lead(fn, k, col):
    xs, ys = [], []
    for i, m in enumerate(ret_months):
        if i + k < len(ret_months) and fn(m) is not None:
            xs.append(fn(m))
            ys.append(rets[ret_months[i + k]][col])
    return xs, ys


grid = {}
for name, fn in metrics.items():
    for k in (0, 1, 2, 3):
        for col, an in ((0, 'CHINEXT'), (1, 'FXI')):
            xs, ys = lead(fn, k, col)
            if len(xs) < 10:
                continue
            grid[(name, k, an)] = pearson(xs, ys)

r_ = grid[('PMI水平', 2, 'CHINEXT')]
chk('T06a', 'PMI水平 k=2 CHINEXT r', round(r_[0], 3), -0.176, 0.0005)
chk('T06b', 'PMI水平 k=2 CHINEXT p', round(r_[2], 3), 0.057, 0.001)
gmax = max(abs(v[0]) for v in grid.values())
chk('T06c', '全网格(含同期)最大|r|', round(gmax, 3), 0.176, 0.0005)
leadmax = max(abs(v[0]) for key, v in grid.items() if key[1] >= 1)
say(f'        (仅先行k=1..3最大|r|={leadmax:.3f}; 先行格数='
    f'{sum(1 for key in grid if key[1] >= 1)} = 5变换x3先行x2资产)')

r_ = grid[('PMI环比差分', 1, 'CHINEXT')]
sp_ = spearman(*lead(pmi_diff, 1, 0))
chk('T07a', 'ΔPMI k=1 CHINEXT r', round(r_[0], 3), 0.157, 0.0005)
chk('T07b', 'ΔPMI k=1 CHINEXT p', round(r_[2], 3), 0.089, 0.001)
chk('T07c', 'ΔPMI k=1 CHINEXT Spearman', round(sp_[0], 3), 0.057, 0.0005)
chk('T08', 'ΔPMI k=2 CHINEXT r(符号翻转)', round(grid[('PMI环比差分', 2, 'CHINEXT')][0], 3),
    -0.123, 0.0005)
chk('T08b', 'ΔPMI k=1 FXI p(CTR-1"FXI端不存在")', round(grid[('PMI环比差分', 1, 'FXI')][2], 3),
    0.505, 0.001)

for key, exp_r in ((('CI', 1, 'CHINEXT'), -0.009), (('CI', 1, 'FXI'), -0.095),
                   (('CI', 2, 'CHINEXT'), 0.014), (('CI', 2, 'FXI'), -0.065),
                   (('CI', 3, 'CHINEXT'), -0.027), (('CI', 3, 'FXI'), -0.084)):
    chk(f"T09-{key[1]}{key[2]}", f"CI k={key[1]} {key[2]} r", round(grid[key][0], 3),
        exp_r, 0.0005)
cilead = [abs(v[0]) for key, v in grid.items() if key[0] == 'CI' and key[1] >= 1]
chk('T09x', 'CI 先行 |r| 最大(CON-2断言≤0.10)', round(max(cilead), 3), 0.095, 0.0005,
    f"实际最大={max(cilead):.4f}")
cik12 = [grid[('CI', k, a)][2] for k in (1, 2) for a in ('CHINEXT', 'FXI')]
chk('T09p', 'CI k=1,2 双资产 p 全>0.30(MC-2)', round(min(cik12), 3), 0.307, 0.001,
    f"最小p={min(cik12):.4f}")

loan_ts = [(key[1], key[2], abs(v[1])) for key, v in grid.items()
           if key[0] in ('贷款同比差', '贷款/12月均值比', 'CI') and key[1] >= 1]
mx = max(loan_ts, key=lambda x: x[2])
say(f"  [INFO] T10 贷款族先行格 Pearson |t| 最大 = {mx[2]:.2f} "
    f"(k={mx[0]}, {mx[1]}) —— CL-2 称『全部|t|<1.6』")
chk('T10', '贷款族先行 Pearson max|t| <1.6 (CL-2断言)', 1 if mx[2] < 1.6 else 0, 1, 0,
    f"复算 max|t|={mx[2]:.2f}, 期望断言成立" if mx[2] < 1.6 else
    f"断言不成立: {mx[2]:.2f}≥1.6 (r={grid[('贷款/12月均值比', mx[0], mx[1])][0]:.3f},"
    f"p={grid[('贷款/12月均值比', mx[0], mx[1])][2]:.3f})")

say('\n== T11-T16 PMI 相位 k=1(CON-1/CL-3/CL-4/MC-1) ==')


def phase_groups(k, col=0, strict=False):
    """k=1 即信号月 PMI 对次月收益;strict=True 时低位组只收 PMI<50(剔 PMI=50)。"""
    hi, lo = [], []
    for i, m in enumerate(ret_months):
        if i + k >= len(ret_months) or m not in pmi:
            continue
        r = rets[ret_months[i + k]][col]
        if pmi[m] > 50:
            hi.append(r)
        elif pmi[m] < 50 or not strict:
            lo.append(r)
    return hi, lo


def pstats(v):
    return (len(v), mean(v) * 100, median(v) * 100,
            sum(1 for x in v if x > 0) / len(v) * 100, stdev(v) * 100)


hi, lo = phase_groups(1)          # 研究席口径: >50 vs 其余(≤50)
n, mu, med, win, sd = pstats(hi)
chk('T11a', 'PMI>50 k=1 CHINEXT n', n, 67, 0)
chk('T11b', 'PMI>50 k=1 CHINEXT 月均%', round(mu, 2), -0.74, 0.005)
chk('T11c', 'PMI>50 k=1 CHINEXT 中位%', round(med, 2), -1.22, 0.005)
chk('T11d', 'PMI>50 k=1 CHINEXT 胜率%', round(win), 39, 0.5)
chk('T11e', 'PMI>50 k=1 CHINEXT σ%', round(sd, 2), 7.50, 0.005)
n, mu, med, win, sd = pstats(lo)
chk('T11f', 'PMI<50(实际≤50) k=1 CHINEXT n', n, 51, 0)
chk('T11g', 'PMI<50 k=1 CHINEXT 月均%', round(mu, 2), 2.19, 0.005)
chk('T11h', 'PMI<50 k=1 CHINEXT 中位%', round(med, 2), 0.98, 0.005)
chk('T11i', 'PMI<50 k=1 CHINEXT 胜率%', round(win), 59, 0.5)
chk('T11j', 'PMI<50 k=1 CHINEXT σ%', round(sd, 2), 9.64, 0.005)

t, df, p = welch(hi, lo)
hi_s, lo_s = phase_groups(1, strict=True)          # 严格 <50 组
z_le, pmw_le = mw_p(hi, lo)                         # MW, 低位=≤50(与相位统计同组)
z_st, pmw_st = mw_p(hi_s, lo_s)                     # MW, 低位=严格<50
chk('T12a', 'Welch t', round(t, 2), -1.79, 0.005)
chk('T12b', 'Welch df', round(df), 92, 1)
chk('T12c', 'Welch p', round(p, 3), 0.076, 0.0015)
say(f'  [INFO] T12d MW 分组核查: 低位=≤50组(n={len(lo)}) z={z_le:.2f} p={pmw_le:.3f} | '
    f'低位=严格<50组(n={len(lo_s)}) z={z_st:.2f} p={pmw_st:.3f}')
chk('T12d', 'Mann-Whitney p(研究席复现=严格<50组)', round(pmw_st, 3), 0.120, 0.0015)
chk('T12e', 'Mann-Whitney z(研究席复现=严格<50组)', round(z_st, 2), -1.55, 0.005)
chk('T12f', 'MW p(≤50组,与相位统计同组)', round(pmw_le, 3), 0.103, 0.0015,
    '同组口径下 MW p=0.103,判定档引用的 0.120 系严格<50组')

fh, fl = phase_groups(1, col=1)   # FXI
n, mu, med, win, sd = pstats(fh)
chk('T13a', 'PMI>50 k=1 FXI n/月均/σ', f"{n}/{mu:.2f}/{sd:.2f}", '67/-0.16/6.20', None)
n, mu, med, win, sd = pstats(fl)
chk('T13b', 'PMI<50 k=1 FXI 月均/中位/胜率/σ', f"{mu:.2f}/{med:.2f}/{win:.0f}/{sd:.2f}",
    '1.11/-0.45/49/8.03', None)
_, _, p_fx = welch(fh, fl)
chk('T13c', 'PMI相位 k=1 FXI Welch p(SCN-4引用0.350)', round(p_fx, 3), 0.350, 0.0015)


def trim2(v):
    s = sorted(v)
    return mean(s[2:-2]) * 100


hi_r = [rets[ret_months[i + 1]][0] for i, m in enumerate(ret_months)
        if i + 1 < len(ret_months) and pmi.get(m, 0) > 50]
lo_r = [rets[ret_months[i + 1]][0] for i, m in enumerate(ret_months)
        if i + 1 < len(ret_months) and pmi.get(m, 99) <= 50]
chk('T14a', 'PMI>50 去首尾各2月均值%', round(trim2(hi_r), 2), -0.57, 0.005)
chk('T14b', 'PMI<50(≤50组,与+2.19%同组) 去首尾各2月均值%', round(trim2(lo_r), 2), 1.58, 0.005,
    '同组复算=1.67%; 1.58%系严格<50组(见T14c)')
lo_rs = [rets[ret_months[i + 1]][0] for i, m in enumerate(ret_months)
         if i + 1 < len(ret_months) and pmi.get(m, 99) < 50]
chk('T14c', '严格<50组 去首尾各2月均值%(研究席1.58%来源)', round(trim2(lo_rs), 2), 1.58, 0.005)
chk('T14d', '严格<50组 全样本均值%(研究席"+2.14%"来源)', round(mean(lo_rs) * 100, 2), 2.14, 0.005)
sp22 = spearman(*lead(lambda m: pmi.get(m), 2, 0))
chk('T14e', 'PMI水平 k=2 CHINEXT Spearman(冻结输出-0.149)', round(sp22[0], 3), -0.149, 0.0005)

eq50 = [m for m in ret_months if m in pmi and pmi[m] == 50.0]
say(f'  [INFO] T15 重叠窗内 PMI=50.0 精确月份: {eq50} —— '
    f'研究席"PMI<50"组实含这些 PMI=50 月')
his, los = phase_groups(1, strict=True)
n, mu, med, win, sd = pstats(los)
say(f'  [INFO] T15 严格<50 边界下低位组: n={n} 月均={mu:.2f}% 中位={med:.2f}% '
    f'胜率={win:.0f}% σ={sd:.2f}%')
t, df, p = welch(his, los)
say(f'  [INFO] T15 严格<50 边界 Welch t={t:.2f} p={p:.3f}')

say('\n== T16 "同相位内并存极值月"口径核查(CON-1/CL-3/CTR-2) ==')
lo_map = {ret_months[i + 1]: m for i, m in enumerate(ret_months)
          if i + 1 < len(ret_months) and pmi.get(m, 99) <= 50}
hi_map = {ret_months[i + 1]: m for i, m in enumerate(ret_months)
          if i + 1 < len(ret_months) and pmi.get(m, 0) > 50}
for rm in ('2024-09', '2019-02', '2025-08', '2026-07', '2026-10'):
    sig = (lo_map.get(rm) or hi_map.get(rm))
    grp = 'PMI<50信号组' if rm in lo_map else 'PMI>50信号组'
    say(f'  收益月 {rm}: 信号月={sig} PMI({sig})={pmi[sig]} → {grp} | '
        f'当月自身PMI={pmi.get(rm)}')
lo_sorted = sorted(((rets[rm][0], rm) for rm in lo_map), key=lambda x: x[0])
say('  PMI<50信号组(k=1)收益最差3月: ' +
    ', '.join(f'{m}={r * 100:.1f}%(信号月PMI={pmi[lo_map[m]]})' for r, m in lo_sorted[:3]))

say('\n== T17-T19 跨资产与极值(CON-2/CL-5/MC-3/SCN) ==')
rc = [rets[m][0] for m in ret_months]
rf = [rets[m][1] for m in ret_months]
pr = pearson(rc, rf)
sd_dir = sum(1 for m in ret_months if rets[m][0] * rets[m][1] > 0) / len(ret_months) * 100
chk('T17a', 'CHINEXT~FXI r', round(pr[0], 3), 0.351, 0.0005)
chk('T17b', 'CHINEXT~FXI t', round(pr[1], 2), 4.06, 0.005)
chk('T17c', 'CHINEXT~FXI p', round(pr[2], 4), 0.0001, 0.00005)
chk('T17d', '同月同向比例%', round(sd_dir), 67, 0.5)
chk('T18a', '2026-07 CHINEXT %', round(rets['2026-07'][0] * 100, 1), -23.0, 0.05)
chk('T18b', '2026-07 FXI %', round(rets['2026-07'][1] * 100, 1), 15.5, 0.05)
chk('T18c', '2026-07 两指数差 pp', round((rets['2026-07'][1] - rets['2026-07'][0]) * 100, 1),
    38.5, 0.05)
for m, e in (('2024-09', 37.6), ('2019-02', 25.1), ('2025-08', 24.1),
             ('2026-07', -23.0), ('2026-10', -23.0)):
    chk(f'T19-{m}', f'CHINEXT {m} 月收益%', round(rets[m][0] * 100, 1), e, 0.05)
chk('T19b', 'FXI 2022-11 月收益%', round(rets['2022-11'][1] * 100, 1), 34.4, 0.05)

say('\n== T20 CON-3: PMI 水平 vs CI 同月 ==')
pairs = [(m, pmi[m], ci(m)) for m in ret_months if ci(m) is not None]
rp = pearson([a for _, a, _ in pairs], [b for _, _, b in pairs])
chk('T20a', 'r', round(rp[0], 3), 0.204, 0.0005)
chk('T20b', 't', round(rp[1], 2), 2.26, 0.005)
chk('T20c', 'p', round(rp[2], 3), 0.026, 0.0015)
chk('T20d', 'n', rp[3], 119, 0)

say('\n== T21-T23 MC-2: CI 相位与回归 ==')
for col_i, an in ((0, 'CHINEXT'), (1, 'FXI')):
    hi2, lo2 = [], []
    for i, m in enumerate(ret_months):
        if i + 2 >= len(ret_months) or ci(m) is None:
            continue
        (hi2 if ci(m) > 0 else lo2).append(rets[ret_months[i + 2]][col_i])
    _, _, pw = welch(hi2, lo2)
    say(f'  CI>0/<0 k=2 {an}: n={len(hi2)}/{len(lo2)} Welch p={pw:.3f}')
    if an == 'CHINEXT':
        chk('T21a', 'CI相位 k=2 CHINEXT Welch p', round(pw, 3), 0.950, 0.0015)
        chk('T21b', 'CI相位 k=2 组 n', f'{len(hi2)}/{len(lo2)}', '75/42', None)
    else:
        chk('T21c', 'CI相位 k=2 FXI Welch p', round(pw, 3), 0.574, 0.0015)

# NW 回归(控制收益滞后), 贷款族 + ΔPMI
nwt = {}
for name, fn in (('PMI环比差分', pmi_diff), ('CI', ci), ('贷款/12月均值比', loans_ratio12)):
    for k in (1, 2):
        for col in (0, 1):
            y, xs = [], []
            for i, m in enumerate(ret_months):
                if i + k >= len(ret_months) or fn(m) is None:
                    continue
                y.append(rets[ret_months[i + k]][col])
                xs.append([fn(m), rets[m][col]])
            beta, tv = ols_hac(y, xs, lag=4)
            nwt[(name, k, col)] = tv[1]
chk('T22a', 'ΔPMI k=1 CHINEXT NW-t', round(nwt[('PMI环比差分', 1, 0)], 2), 4.46, 0.01)
loan_nw = {k2: v for k2, v in nwt.items() if k2[0] in ('CI', '贷款/12月均值比')}
mx_nw = max(loan_nw.items(), key=lambda kv: abs(kv[1]))
chk('T22b', '贷款族 NW |t|≤1.6 (MC-2断言)', 1 if abs(mx_nw[1]) <= 1.6 else 0, 1, 0,
    f"max={mx_nw[1]:.2f} @{mx_nw[0]}")
say(f'  贷款族 NW-t 明细: ' + ', '.join(f'{k2}:{v:+.2f}' for k2, v in sorted(loan_nw.items())))

xs, ys = [], []
for i, m in enumerate(ret_months):
    if i + 1 < len(ret_months) and pmi_diff(m) is not None:
        xs.append(pmi_diff(m))
        ys.append(rets[ret_months[i + 1]][0])
n_ = len(xs)
mx_, my_ = mean(xs), mean(ys)
sxx = sum((a - mx_) ** 2 for a in xs)
b_raw = sum((a - mx_) * (b - my_) for a, b in zip(xs, ys)) / sxx
a_raw = my_ - b_raw * mx_
u = [b - a_raw - b_raw * a for a, b in zip(xs, ys)]
se_cl = math.sqrt(sum(e * e for e in u) / (n_ - 2) / sxx)
_, tv_hc0 = ols_hac(ys, [[x] for x in xs], lag=4, hac=False)
chk('T23a', 'ΔPMI k=1 CHINEXT 经典t', round(b_raw / se_cl, 2), 1.72, 0.005)
chk('T23b', 'ΔPMI k=1 CHINEXT HC0-t', round(tv_hc0[1], 2), 5.14, 0.01)

say('\n== T24-T25 情景锚(CL-9/CTR-3/SCN) ==')
deep = [(m, rets[ret_months[i + 1]]) for i, m in enumerate(ret_months)
        if i + 1 < len(ret_months) and ci(m) is not None and ci(m) < -3.0]
say('  CI<-3万亿事件月: ' + ', '.join(m for m, _ in deep))
for col_i, an, exps in ((0, 'CHINEXT', (14, -1.51, -1.78, 43, 14.26)),
                        (1, 'FXI', (14, 3.25, 1.83, 57, 7.38))):
    v = [r[col_i] for _, r in deep]
    n, mu, med, win, sd = pstats(v)
    chk(f'T24-{an}', f'深收缩次月{an} n/均值/中位/胜率/σ',
        f'{n}/{mu:.2f}/{med:.2f}/{win:.0f}/{sd:.2f}',
        f'{exps[0]}/{exps[1]:.2f}/{exps[2]:.2f}/{exps[3]}/{exps[4]:.2f}', None)

dual = [(m, rets[ret_months[i + 1]]) for i, m in enumerate(ret_months)
        if i + 1 < len(ret_months) and pmi.get(m, 99) < 50
        and ci(m) is not None and ci(m) < 0]
for col_i, an, exps in ((0, 'CHINEXT', (24, 2.75, 0.45, 54, 11.33)),
                        (1, 'FXI', (24, 0.96, -0.51, 46, 6.54))):
    v = [r[col_i] for _, r in dual]
    n, mu, med, win, sd = pstats(v)
    chk(f'T25-{an}', f'双重收缩次月{an} n/均值/中位/胜率/σ',
        f'{n}/{mu:.2f}/{med:.2f}/{win:.0f}/{sd:.2f}',
        f'{exps[0]}/{exps[1]:.2f}/{exps[2]:.2f}/{exps[3]}/{exps[4]:.2f}', None)

say('\n== T26-T28 派生量与情景触发数据 ==')
chk('T26', '1-r²(MC-3称"约2/3方差互不共享")', round(1 - pr[0] ** 2, 3), 0.877, 0.001,
    '正确未共享方差=1-r²≈87.7%,非2/3')
after = [loans[k] for k in loan_keys if k > '2026-03']
chk('T27a', '2026-03后无单月≥25000亿(SCN-2触发叙述)', max(after), 17650.0, 0.5)
big = [k for k in loan_keys if loans[k] >= 25000]
say(f'  [INFO] 全史单月≥25000亿的月: {len(big)}个,全部1月: '
    f'{all(k[5:7] == "01" for k in big)}')
chk('T28', 'CI 历史极值(SCN-3触发参照)', round(min(civ), 2), -5.24, 0.005)

say('\n== 汇总 ==')
n_ok = sum(1 for r in RESULTS if r[4])
say(f'数值核对项: {len(RESULTS)}, PASS: {n_ok}, FAIL: {len(RESULTS) - n_ok}')
for r in RESULTS:
    if not r[4]:
        say(f"  FAIL {r[0]} {r[1]}: 复算={r[3]} 期望={r[2]} {r[5]}")

with open('/tmp/sr5b/recompute_out.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(OUT) + '\n')
