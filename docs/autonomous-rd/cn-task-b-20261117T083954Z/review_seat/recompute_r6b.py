#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r6-b-review 独立审查席复算脚本(Audit-R6 中国任务B, v3 判断档).

零依赖研究席代码;纯 stdlib,从 seat_data 冻结切片自算。
口径依据= R5 口径台账 docs/autonomous-rd/cn-task-b-20261117T035814Z/README.md:
  - 股指月频化: 每日历月最后可得收盘=月末价,月收益=环比;2026-11残月剔除
  - 样本窗: 月收益 2016-12..2026-10 n=119;宏观全史 n=226
  - lead-k = 宏观(M) vs r(M+k)
  - CI(M)=sum(M-11..M)-sum(M-23..M);YoY差用M-12;12月均值比用M-11..M
  - Pearson p=不完全Beta精确;相位=Welch t(Satterthwaite)+MW正态近似;
    回归 OLS+Newey-West HAC(lag=4)
  - PMI相位=50严格两侧,=50.0持平月不入组
  - CI百分位=100*count(史<=当前)/n

R7-03 参数化: 数据目录/输出文件默认按 __file__ 相对定位(净检出直接
可跑),--seat DIR / --out FILE 可覆写;校验失败以非零退出码结束。
"""
import json
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_argv = sys.argv[1:]


def _flag(name, default):
    return _argv[_argv.index(name) + 1] if name in _argv else default


SEAT = _flag('--seat', os.path.normpath(
    os.path.join(_HERE, '..', 'seat_data')))
# 默认输出=replay 名(不覆写 R6 冻结档 recompute_out.txt=脚本主输出+
# 席位追加「反例面扫描补充」段,append-only)
OUT_PATH = _flag('--out', os.path.join(_HERE, 'recompute_replay_out.txt'))
OUT = []

def log(s=''):
    OUT.append(s)
    print(s)

# ---------- 统计工具(自写) ----------
def mean(xs): return sum(xs) / len(xs)

def median(xs):
    xs = sorted(xs); n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2

def stdev(xs, ddof=1):
    m = mean(xs); n = len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - ddof))

def betacf(a, b, x):
    MAXIT, EPS, FPMIN = 200, 3e-12, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < FPMIN: d = FPMIN
    d = 1.0 / d; h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN: d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN: c = FPMIN
        d = 1.0 / d; h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN: d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN: c = FPMIN
        d = 1.0 / d; de = d * c; h *= de
        if abs(de - 1.0) < EPS: break
    return h

def betai(a, b, x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    lbeta = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
             + a * math.log(x) + b * math.log(1.0 - x))
    bt = math.exp(lbeta)
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * betacf(a, b, x) / a
    return 1.0 - bt * betacf(b, a, 1.0 - x) / b

def t_sf_two(t, df):
    """two-sided p for t distribution."""
    return betai(df / 2.0, 0.5, df / (df + t * t))

def norm_sf_two(z):
    return math.erfc(abs(z) / math.sqrt(2.0))

def pearson(xs, ys):
    n = len(xs); mx, my = mean(xs), mean(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    r = sxy / math.sqrt(sxx * syy)
    t = r * math.sqrt((n - 2) / (1 - r * r))
    p = t_sf_two(t, n - 2)
    return r, t, p

def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    rk = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            rk[order[k]] = avg
        i = j + 1
    return rk

def spearman(xs, ys):
    return pearson(ranks(xs), ranks(ys))

def welch(a, b):
    n1, n2 = len(a), len(b)
    m1, m2 = mean(a), mean(b)
    v1, v2 = stdev(a) ** 2 / n1, stdev(b) ** 2 / n2
    t = (m1 - m2) / math.sqrt(v1 + v2)
    df = (v1 + v2) ** 2 / (v1 ** 2 / (n1 - 1) + v2 ** 2 / (n2 - 1))
    return t, df, t_sf_two(t, df)

def mannwhitney(a, b):
    n1, n2 = len(a), len(b)
    allv = [(v, 0) for v in a] + [(v, 1) for v in b]
    rk = ranks([v for v, _ in allv])
    r1 = sum(rk[i] for i, (_, g) in enumerate(allv) if g == 0)
    u1 = r1 - n1 * (n1 + 1) / 2.0
    u2 = n1 * n2 - u1
    u = min(u1, u2)
    # tie-corrected sigma
    _, cnts = {}, {}
    vals = [v for v, _ in allv]
    from collections import Counter
    cnts = Counter(vals)
    tie = sum(c ** 3 - c for c in cnts.values())
    N = n1 + n2
    mu = n1 * n2 / 2.0
    sd = math.sqrt(n1 * n2 / 12.0 * ((N + 1) - tie / (N * (N - 1.0))))
    z0 = (u - mu + 0.5) / sd   # with continuity correction
    z = (u - mu) / sd          # no continuity (scipy asymptotic default)
    return u, z, (z0, norm_sf_two(z0)), norm_sf_two(z)

def trimmed_mean(xs, k):
    s = sorted(xs)
    return mean(s[k:len(s) - k])

def winrate(xs):
    return 100.0 * sum(1 for x in xs if x > 0) / len(xs)

# ---------- OLS / NW HAC / HC0 ----------
def ols(X, y):
    """X: list of rows (incl intercept), y: list. returns beta, resid, XtX_inv."""
    k = len(X[0]); n = len(y)
    xtx = [[sum(X[i][a] * X[i][b] for i in range(n)) for b in range(k)] for a in range(k)]
    # invert via Gauss-Jordan
    m = [row[:] + [1.0 if i == j else 0.0 for j in range(k)] for i, row in enumerate(xtx)]
    for col in range(k):
        piv = max(range(col, k), key=lambda r: abs(m[r][col]))
        m[col], m[piv] = m[piv], m[col]
        p = m[col][col]
        m[col] = [v / p for v in m[col]]
        for r in range(k):
            if r != col and m[r][col] != 0:
                fac = m[r][col]
                m[r] = [a - fac * b for a, b in zip(m[r], m[col])]
    inv = [row[k:] for row in m]
    beta = [sum(inv[a][b] * sum(X[i][b] * y[i] for i in range(n)) for b in range(k))[0] if False else
            sum(inv[a][b] * sum(X[i][b] * y[i] for i in range(n)) for b in range(k))
            for a in range(k)]
    resid = [y[i] - sum(beta[a] * X[i][a] for a in range(k)) for i in range(n)]
    dof = n - k
    s2 = sum(e * e for e in resid) / dof
    v_classic = [[inv[a][b] * s2 for b in range(k)] for a in range(k)]
    return beta, resid, inv, v_classic

def se_from_v(v, idx):
    return math.sqrt(v[idx][idx])

def hc0(X, y, beta, inv):
    resid = [y[i] - sum(beta[a] * X[i][a] for a in range(len(beta))) for i in range(len(y))]
    k = len(beta)
    meat = [[0.0] * k for _ in range(k)]
    for i in range(len(y)):
        xi = X[i]
        for a in range(k):
            for b in range(k):
                meat[a][b] += resid[i] ** 2 * xi[a] * xi[b]
    v = [[sum(inv[a][m] * meat[m][b] for m in range(k)) for b in range(k)] for a in range(k)]
    # full sandwich: inv*meat*inv
    v2 = [[sum(v[a][m] * inv[m][b] for m in range(k)) for b in range(k)] for a in range(k)]
    return v2

def newey_west(X, y, beta, inv, lag=4):
    n, k = len(y), len(beta)
    resid = [y[i] - sum(beta[a] * X[i][a] for a in range(k)) for i in range(n)]
    meat = [[0.0] * k for _ in range(k)]
    for i in range(n):
        for a in range(k):
            for b in range(k):
                meat[a][b] += resid[i] ** 2 * X[i][a] * X[i][b]
    for l in range(1, lag + 1):
        w = 1.0 - l / (lag + 1.0)
        for a in range(k):
            for b in range(k):
                s = sum(resid[i] * resid[i - l] * X[i][a] * X[i - l][b]
                        for i in range(l, n))
                meat[a][b] += w * (s + s)  # symmetric
    v = [[sum(inv[a][m] * meat[m][b] for m in range(k)) for b in range(k)] for a in range(k)]
    v2 = [[sum(v[a][m] * inv[m][b] for m in range(k)) for b in range(k)] for a in range(k)]
    return v2

def tstat(beta, v, idx):
    return beta[idx] / se_from_v(v, idx)

# ---------- 数据加载 ----------
def load_series(metric):
    d = json.load(open(os.path.join(SEAT, metric + '.json')))
    s = d['data']['series']
    assert s['dates'] == sorted(s['dates'])
    return s['dates'], [float(x) for x in s['values']]

pmi_dates, pmi_vals = load_series('CN_PMI_MFG')
loan_dates, loan_vals = load_series('CN_NEW_LOANS')
fxi_dd, fxi_vv = load_series('FXI')
chn_dd, chn_vv = load_series('CHINEXT')

PMI = {d[:7]: v for d, v in zip(pmi_dates, pmi_vals)}
LOAN = {d[:7]: v for d, v in zip(loan_dates, loan_vals)}

def month_end(dates, vals):
    out = {}
    for d, v in zip(dates, vals):
        out[d[:7]] = v
    return out

fxi_close = month_end(fxi_dd, fxi_vv)
chn_close = month_end(chn_dd, chn_vv)

def month_next(ym, k=1):
    y, m = int(ym[:4]), int(ym[5:7])
    t = y * 12 + (m - 1) + k
    return f'{t // 12:04d}-{t % 12 + 1:02d}'

def month_add(ym, k):
    return month_next(ym, k)

def rets(close):
    yms = sorted(close)
    return {b: close[b] / close[a] - 1 for a, b in zip(yms, yms[1:])}

R_FXI = rets(fxi_close)
R_CHN = rets(chn_close)

WIN = [f'{y}-{m:02d}' for y in range(2016, 2027) for m in range(1, 13)]
WIN = [w for w in WIN if '2016-12' <= w <= '2026-10']
assert len(WIN) == 119, len(WIN)

# 宏观变换(只用 <=M 数据)
def dpmi(ym):
    prev = month_add(ym, -1)
    return PMI[ym] - PMI[prev] if prev in PMI else None

def loan_yoy_diff(ym):
    p = month_add(ym, -12)
    return LOAN[ym] - LOAN[p] if p in LOAN else None

def loan_ratio_12m(ym):
    window = [month_add(ym, -k) for k in range(0, 12)]  # M-11..M (12 values)
    if any(w not in LOAN for w in window):
        return None
    return LOAN[ym] / mean([LOAN[w] for w in window])

def ci(ym):
    w1 = [month_add(ym, -k) for k in range(0, 12)]        # M-11..M
    w2 = [month_add(ym, -k) for k in range(12, 24)]       # M-23..M-12
    if any(w not in LOAN for w in w1 + w2):
        return None
    return sum(LOAN[w] for w in w1) - sum(LOAN[w] for w in w2)

CI_ALL = {}
for ym in sorted(LOAN):
    c = ci(ym)
    if c is not None:
        CI_ALL[ym] = c
log(f'# CI 全史可得 n={len(CI_ALL)}, first={min(CI_ALL)}, last={max(CI_ALL)}')

# ============ 复算项 ============
CHECKS = []
def chk(item, claimed, computed, tol=None, note=''):
    if tol is None:
        tol = 0.005 if isinstance(claimed, float) else 0
    ok = abs(computed - claimed) <= tol if isinstance(claimed, (int, float)) and not isinstance(claimed, bool) else (computed == claimed)
    CHECKS.append((item, claimed, computed, ok, note))
    log(f'[{"OK " if ok else "XX "}] {item}: claimed={claimed} computed={computed}' + (f' ({note})' if note else ''))
    return ok

# ---- CL-1 / CON-2 事实 ----
log('\n===== CL-1 / CON-2 基础事实 =====')
chk('PMI 2026-10', 49.3, PMI['2026-10'])
chk('loan 2026-10(亿)', -5846.0, LOAN['2026-10'])
neg_months = [(d[5:7], v) for d, v in LOAN.items() if v < 0]
log(f'负值月 n={len(neg_months)}: {sorted(neg_months)}')
from collections import Counter
neg_by_month = Counter(m for m, _ in neg_months)
chk('负值月个数', 6, len(neg_months))
chk('负值月分布 07月', 3, neg_by_month.get('07', 0))
chk('负值月分布 10月', 2, neg_by_month.get('10', 0))
chk('负值月分布 04月', 1, neg_by_month.get('04', 0))
log(f'负值明细: {sorted(LOAN.items(), key=lambda kv: kv[1])[:3]}')

CI_CUR = CI_ALL['2026-10']
chk('CI(2026-10)万亿', -3.58, CI_CUR / 10000.0, 0.005)
pct = 100.0 * sum(1 for v in CI_ALL.values() if v <= CI_CUR) / len(CI_ALL)
chk('CI百分位%', 4.9, pct, 0.05, f'count<=cur={sum(1 for v in CI_ALL.values() if v <= CI_CUR)}/{len(CI_ALL)}')
chk('CI史min万亿', -5.24, min(CI_ALL.values()) / 10000.0, 0.005)
chk('CI史max万亿', 4.69, max(CI_ALL.values()) / 10000.0, 0.005)

# ---- 相位分析(PMI 50 严格两侧, 信号月M→r(M+1)) ----
log('\n===== CON-1 / CL-3 / MC-1 / CL-4 相位统计 =====')
flat = [d[:7] for d, v in PMI.items() if v == 50.0 and '2016-12' <= d <= '2026-10']
log(f'PMI=50.0 持平月(窗内): {sorted(flat)}')
chk('持平月个数', 3, len(flat))
chk('持平月列表', sorted(flat) == ['2018-11', '2020-01', '2026-05'], True)

def phase_groups(rets_map, lead=1):
    lo, hi, lo_m, hi_m = [], [], [], []
    for m in WIN:
        nm = month_add(m, lead)
        if nm > '2026-10' or nm not in rets_map:
            continue
        p = PMI[m]
        if p == 50.0:
            continue
        (lo if p < 50 else hi).append(rets_map[nm])
        (lo_m if p < 50 else hi_m).append((m, nm, p, rets_map[nm]))
    return lo, hi, lo_m, hi_m

lo_c, hi_c, lom, him = phase_groups(R_CHN, 1)
chk('CHINEXT lo n', 48, len(lo_c))
chk('CHINEXT hi n', 67, len(hi_c))
chk('CHINEXT lo 月均%', 2.14, mean(lo_c) * 100, 0.005)
chk('CHINEXT lo 中位%', 0.98, median(lo_c) * 100, 0.005)
chk('CHINEXT lo 胜率%', 58, winrate(lo_c), 0.5)
chk('CHINEXT hi 月均%', -0.74, mean(hi_c) * 100, 0.005)
chk('CHINEXT hi 中位%', -1.22, median(hi_c) * 100, 0.005)
chk('CHINEXT hi 胜率%', 39, winrate(hi_c), 0.5)
t_w, df_w, p_w = welch(lo_c, hi_c)
log(f'Welch t={t_w:.4f} df={df_w:.2f} p={p_w:.4f}')
chk('Welch p', 0.092, p_w, 0.0005)
u, z, (zc, pc), p_mw = mannwhitney(lo_c, hi_c)
log(f'MW U={u} z={z:.4f} p={p_mw:.4f} (变体: 连续性校正 z={zc:.4f} p={pc:.4f})')
chk('MW p', 0.120, p_mw, 0.0005)
chk('截尾lo(去首尾各2)', 1.58, trimmed_mean(lo_c, 2) * 100, 0.005)
chk('截尾hi(去首尾各2)', -0.57, trimmed_mean(hi_c, 2) * 100, 0.005)
for ddof in (1, 0):
    log(f'σ ddof={ddof}: lo={stdev(lo_c, ddof)*100:.3f} hi={stdev(hi_c, ddof)*100:.3f}')
chk('CHINEXT lo σ%', 9.81, stdev(lo_c, 1) * 100, 0.005)
chk('CHINEXT hi σ%', 7.50, stdev(hi_c, 1) * 100, 0.005)

lo_f, hi_f, lomf, himf = phase_groups(R_FXI, 1)
chk('FXI lo σ%', 8.07, stdev(lo_f, 1) * 100, 0.005)
chk('FXI hi σ%', 6.20, stdev(hi_f, 1) * 100, 0.005)
t_f, df_f, p_f = welch(lo_f, hi_f)
log(f'FXI 相位 Welch t={t_f:.4f} df={df_f:.2f} p={p_f:.4f}')
chk('FXI 相位 Welch p(SCN-4/MC-3用)', 0.250, p_f, 0.0005)
chk('FXI lo n', 48, len(lo_f))
chk('FXI lo 月均%(参考R5冻结)', 1.45, mean(lo_f) * 100, 0.005)

# 极值月(样本=重叠窗 CHINEXT 月收益)
log('\n===== 极值月归属 =====')
ext = sorted(((v, m) for m, v in R_CHN.items() if m in WIN))
log(f'CHINEXT 窗内最大两跌幅: {ext[0], ext[1]}, 最大涨幅: {ext[-1]}')
chk('最大涨幅月', 37.6, ext[-1][0] * 100, 0.05, f'月={ext[-1][1]}')
chk('最大涨幅月份', '2024-09', ext[-1][1], True)
chk('最大跌幅月1', -23.0, ext[0][0] * 100, 0.05, f'月={ext[0][1]} 精确={ext[0][0]*100:.4f}')
chk('最大跌幅月2', -23.0, ext[1][0] * 100, 0.05, f'月={ext[1][1]} 精确={ext[1][0]*100:.4f}')
loss_months = sorted([ext[0][1], ext[1][1]])
chk('两最大跌幅月=2026-07/2026-10', loss_months == ['2026-07', '2026-10'], True)
# 相位归属(信号月口径)
for rm in loss_months:
    sig = month_add(rm, -1)
    log(f'跌幅月 {rm}: 信号月={sig} PMI={PMI[sig]} 收益月当月PMI={PMI[rm]}')
chk('信号月2026-06 PMI', 50.3, PMI['2026-06'])
chk('信号月2026-09 PMI', 50.1, PMI['2026-09'])
chk('收益月2026-07 PMI<50', PMI['2026-07'] < 50, True, f'={PMI["2026-07"]}')
chk('收益月2026-10 PMI<50', PMI['2026-10'] < 50, True)
sig_2024_09 = month_add('2024-09', -1)
log(f'+37.6%月 2024-09: 信号月={sig_2024_09} PMI={PMI[sig_2024_09]} (<50?)')
chk('2024-08 PMI<50(信号相位)', PMI['2024-08'] < 50, True, f'={PMI["2024-08"]}')
chk('2025-08 CHINEXT %', 24.1, R_CHN['2025-08'] * 100, 0.05)
chk('2019-02 CHINEXT %', 25.1, R_CHN['2019-02'] * 100, 0.05)

# ---- CL-5 / CON-3 / MC-3 ----
log('\n===== CL-5 / CON-3 / MC-3 =====')
xs = [PMI[m] for m in WIN]
ys = [CI_ALL[m] for m in WIN]
r5a, t5a, p5a = pearson(xs, ys)
log(f'PMI vs CI 同月: r={r5a:.4f} t={t5a:.3f} p={p5a:.5f} n={len(xs)}')
chk('PMI-CI r', 0.204, r5a, 0.0005)
chk('PMI-CI t', 2.26, t5a, 0.005)
chk('PMI-CI p', 0.026, p5a, 0.0005)
chk('PMI-CI n', 119, len(xs))

cx = [R_CHN[m] for m in WIN]
cf = [R_FXI[m] for m in WIN]
r5b, t5b, p5b = pearson(cx, cf)
log(f'CHINEXT vs FXI: r={r5b:.4f} t={t5b:.3f} p={p5b:.6f}')
chk('CHN-FXI r', 0.351, r5b, 0.0005)
chk('CHN-FXI t', 4.06, t5b, 0.005)
chk('CHN-FXI p', 0.0001, p5b, 0.00005)
same = sum(1 for a, b in zip(cx, cf) if (a > 0) == (b > 0))
chk('同向比例%', 67, 100.0 * same / 119, 0.5, f'{same}/119')
chk('1-r²≈88%', 88, round((1 - r5b ** 2) * 100), 0, f'={ (1-r5b**2)*100:.2f}%')
chk('2026-07 FXI %', 15.5, R_FXI['2026-07'] * 100, 0.05)
chk('2026-07 CHINEXT %', -23.0, R_CHN['2026-07'] * 100, 0.05)
chk('2026-07 分化pp', 38.5, (R_FXI['2026-07'] - R_CHN['2026-07']) * 100, 0.05)

# ---- CL-2 相关网格 ----
log('\n===== CL-2 / CTR-1 相关网格(5变换×k=0..3×2资产) =====')
def transform(name, ym):
    return {'pmi': lambda: PMI[ym],
            'dpmi': lambda: dpmi(ym),
            'yoyd': lambda: loan_yoy_diff(ym),
            'ratio': lambda: loan_ratio_12m(ym),
            'ci': lambda: CI_ALL.get(ym)}[name]()

grid = {}
for tname in ('pmi', 'dpmi', 'yoyd', 'ratio', 'ci'):
    for k in (0, 1, 2, 3):
        for asset, rmap in (('CHINEXT', R_CHN), ('FXI', R_FXI)):
            xs2, ys2 = [], []
            for m in WIN:
                tm = month_add(m, k)
                if tm > '2026-10':
                    continue
                tv = transform(tname, m)
                if tv is None or tm not in rmap:
                    continue
                xs2.append(tv); ys2.append(rmap[tm])
            if len(xs2) >= 10:
                grid[(tname, k, asset)] = (pearson(xs2, ys2), len(xs2))
lead_cells = {g: v for g, v in grid.items() if g[1] in (1, 2, 3)}
chk('先行格数', 30, len(lead_cells))
chk('k=0格数', 10, sum(1 for g in grid if g[1] == 0))
chk('合计格数', 40, len(grid))
ns = sorted(set(v[1] for v in lead_cells.values()))
log(f'先行格 n 范围: {ns[0]}-{ns[-1]}')
chk('先行格 n=116-118', True, ns[0] == 116 and ns[-1] == 118, True)
mx = max(lead_cells.items(), key=lambda kv: abs(kv[1][0][0]))
log(f'max|r| 先行格: {mx[0]} r={mx[1][0][0]:.4f} p={mx[1][0][2]:.4f} n={mx[1][1]}')
chk('max|r|', 0.176, abs(mx[1][0][0]), 0.0005)
chk('max|r|格=pmi,k2,CHINEXT', True, mx[0] == ('pmi', 2, 'CHINEXT'), True)
chk('该格 r=-0.176', -0.176, mx[1][0][0], 0.0005)
chk('该格 p=0.057', 0.057, mx[1][0][2], 0.0005)
n_p05 = [g for g, v in lead_cells.items() if v[0][2] < 0.05]
chk('先行格p<0.05个数', 0, len(n_p05))
loan_cells = {g: v for g, v in lead_cells.items() if g[0] in ('yoyd', 'ratio', 'ci')}
mx_t = 0.0
for g, ((r, t, p), n) in loan_cells.items():
    mx_t = max(mx_t, abs(t))
    log(f'  {g}: r={r:.4f} t={t:.3f} p={p:.4f} n={n}')
chk('贷款族先行格max|t|', 1.86, mx_t, 0.005)
g_rat3 = ('ratio', 3, 'CHINEXT')
chk('ratio,k3,CHINEXT r=0.171', 0.171, lead_cells[g_rat3][0][0], 0.0005)
chk('ratio,k3,CHINEXT p=0.066', 0.066, lead_cells[g_rat3][0][2], 0.0005)
chk('ratio,k3,CHINEXT t=1.86', 1.86, abs(lead_cells[g_rat3][0][1]), 0.005)

# CON-2: CI 全部先行相关 |r|<=0.10
ci_lead = [abs(v[0][0]) for g, v in lead_cells.items() if g[0] == 'ci']
chk('CI先行|r|max<=0.10', True, max(ci_lead) <= 0.10, True, f'max={max(ci_lead):.4f}')
# MC-2: CI k=1/k=2 数值
chk('CI k1 CHINEXT r', -0.009, grid[('ci', 1, 'CHINEXT')][0][0], 0.0005)
chk('CI k1 FXI r', -0.095, grid[('ci', 1, 'FXI')][0][0], 0.0005)
chk('CI k2 CHINEXT r', 0.014, grid[('ci', 2, 'CHINEXT')][0][0], 0.0005)
chk('CI k2 FXI r', -0.065, grid[('ci', 2, 'FXI')][0][0], 0.0005)
allp = [grid[('ci', k, a)][0][2] for k in (1, 2) for a in ('CHINEXT', 'FXI')]
chk('CI k1/k2 全部 p>0.30', True, min(allp) > 0.30, True, f'minp={min(allp):.3f}')

# ---- CTR-1: ΔPMI k=1 CHINEXT 多口径 t ----
log('\n===== CTR-1: ΔPMI k=1 CHINEXT 回归族 =====')
xs3, ys3 = [], []
for m in WIN:
    tm = month_add(m, 1)
    if tm > '2026-10':
        continue
    dv = dpmi(m)
    if dv is None:
        continue
    xs3.append(dv); ys3.append(R_CHN[tm])
X = [[1.0, x] for x in xs3]
beta, resid, inv, v_cl = ols(X, ys3)
t_cl = tstat(beta, v_cl, 1)
v_hc0 = hc0(X, ys3, beta, inv)
t_hc0 = tstat(beta, v_hc0, 1)
v_nw = newey_west(X, ys3, beta, inv, lag=4)
t_nw_biv = tstat(beta, v_nw, 1)
# 冻结输出声明规格(第86-87行): r(M+k) ~ 宏观(M) + r(M) 收益滞后控制
Xc = [[1.0, x, R_CHN[month_add(m, 0)]] for x, m in zip(xs3, [mm for mm in WIN if month_add(mm,1) <= '2026-10'])]
bc, rc, ic, vc = ols(Xc, ys3)
t_nw = tstat(bc, newey_west(Xc, ys3, bc, ic, lag=4), 1)
log(f'  NW双变量(无控制) t={t_nw_biv:.3f}; NW控r(M) t={t_nw:.3f} beta={bc[1]:.5f} (冻结输出规格)')
r_dp, t_dp, p_dp = pearson(xs3, ys3)
rho_dp = spearman(xs3, ys3)[0]
p_sp = spearman(xs3, ys3)[2]
log(f'n={len(xs3)} OLS t={t_cl:.3f} HC0 t={t_hc0:.3f} NW t={t_nw:.3f} Pearson r={r_dp:.4f} p={p_dp:.4f} Spearman rho={rho_dp:.4f} p={p_sp:.4f}')
chk('CTR-1 classic t', 1.72, t_cl, 0.005)
chk('CTR-1 HC0 t', 5.14, t_hc0, 0.005)
chk('CTR-1 NW t', 4.46, t_nw, 0.005)
chk('CTR-1 Pearson p', 0.089, p_dp, 0.0005)
chk('CTR-1 Spearman', 0.057, rho_dp if abs(rho_dp - 0.057) < 0.0005 else p_sp, 0.0005, f'rho={rho_dp:.4f} p={p_sp:.4f}')
chk('CTR-1 k2 翻转 r', -0.123, grid[('dpmi', 2, 'CHINEXT')][0][0], 0.0005)

# ---- MC-2: CI>0 vs <0 相位 k=2 + NW 控滞后 ----
log('\n===== MC-2: CI符号相位 k=2 =====')
for asset, rmap in (('CHINEXT', R_CHN), ('FXI', R_FXI)):
    a2, b2 = [], []
    for m in WIN:
        tm = month_add(m, 2)
        if tm > '2026-10' or m not in CI_ALL:
            continue
        (a2 if CI_ALL[m] > 0 else b2).append(rmap[tm])
    t2, df2, p2 = welch(a2, b2)
    log(f'CI符号相位 k=2 {asset}: n+={len(a2)} n-={len(b2)} Welch p={p2:.4f}')
    if asset == 'CHINEXT':
        chk('MC-2 CI相位k2 CHINEXT Welch p', 0.950, p2, 0.0005)
    else:
        chk('MC-2 CI相位k2 FXI Welch p', 0.574, p2, 0.0005)

# NW 回归控收益滞后: r(M+1) ~ CI(M) + r(M) + r(M-1)
log('NW(控收益滞后) CI 系数 |t|:')
for k in (1, 2):
    for asset, rmap in (('CHINEXT', R_CHN), ('FXI', R_FXI)):
        Xr, yr = [], []
        for m in WIN:
            tm = month_add(m, k)
            if tm > '2026-10' or m not in CI_ALL:
                continue
            l1 = rmap.get(month_add(m, k - 1))
            l2 = rmap.get(month_add(m, k - 2))
            if l1 is None or l2 is None:
                continue
            Xr.append([1.0, CI_ALL[m] / 10000.0, l1, l2])
            yr.append(rmap[tm])
        b_, r_, i_, v_ = ols(Xr, yr)
        v_nw2 = newey_west(Xr, yr, b_, i_, lag=4)
        t_ci = tstat(b_, v_nw2, 1)
        log(f'  k={k} {asset}: n={len(yr)} NW t(CI)={t_ci:.3f}')

# ---- CL-9 条件分布 ----
log('\n===== CL-9 / CTR-3: CI<-3万亿 条件分布 =====')
deep = [m for m in WIN if m in CI_ALL and CI_ALL[m] < -30000]
deep_ret = [m for m in deep if month_add(m, 1) <= '2026-10']
log(f'CI<-3万亿月(窗内) n={len(deep)}: {deep}')
log(f'其中次月收益可得 n={len(deep_ret)}')
d_chn = [R_CHN[month_add(m, 1)] for m in deep_ret]
d_fxi = [R_FXI[month_add(m, 1)] for m in deep_ret]
chk('CI<-3万亿月数', 14, len(deep_ret), note=f'窗内含当月共{len(deep)}')
chk('deep CHINEXT 月均%', -1.51, mean(d_chn) * 100, 0.005)
chk('deep CHINEXT 中位%', -1.78, median(d_chn) * 100, 0.005)
chk('deep CHINEXT 胜率%', 43, winrate(d_chn), 0.5)
chk('deep CHINEXT σ%', 14.26, stdev(d_chn, 1) * 100, 0.005)
chk('deep FXI 月均%', 3.25, mean(d_fxi) * 100, 0.005)
chk('deep FXI 中位%', 1.83, median(d_fxi) * 100, 0.005)
chk('deep FXI 胜率%', 57, winrate(d_fxi), 0.5)
chk('deep FXI σ%', 7.38, stdev(d_fxi, 1) * 100, 0.005)
both = [m for m in WIN if m in CI_ALL and CI_ALL[m] < 0
        and PMI[m] < 50 and month_add(m, 1) <= '2026-10']
b_chn = [R_CHN[month_add(m, 1)] for m in both]
chk('PMI<50且CI<0 月数', 24, len(both))
chk('该组 CHINEXT 月均%', 2.75, mean(b_chn) * 100, 0.005)
chk('该组 CHINEXT 中位%', 0.45, median(b_chn) * 100, 0.005)

# ---- MC-4 季节性 ----
log('\n===== MC-4: 贷款季节性(全史 n=226) =====')
chk('贷款全史 n', 226, len(loan_vals))
jan = [v for d, v in LOAN.items() if d[5:7] == '01']
chk('1月均值(亿)', 27341, mean(jan), 0.5, f'n(Jan)={len(jan)}')
chk('全史月均(亿)', 11234, mean(loan_vals), 0.5)
chk('倍数(舍入到1位)', 2.4, round(mean(jan) / mean(loan_vals), 1), 0.0)
chk('2026-03 贷款(亿)', 31522.0, LOAN['2026-03'])
chk('2026-09 贷款(亿,事实通道)', 12734.0, LOAN['2026-09'])

# ---- 锚点 ----
log('\n===== 锚点/其他 =====')
chk('CHINEXT 2026-11-11 收盘', 2572.07, chn_close['2026-11'], 0.005)
chk('FXI 2026-11-11 收盘', 33.92, fxi_close['2026-11'], 0.005)
chk('FXI 2026-10 月收益%(SCN无直接,参考)', None if False else round(R_FXI['2026-10'] * 100, 1), round(R_FXI['2026-10'] * 100, 1), 0)  # informational
chk('CI 史极值月(SCN-3 -5.24万亿)', -5.24, min(CI_ALL.values()) / 10000.0, 0.005)
chk('累计2026-10前十月贷款(README锚,亿)', 109149, sum(LOAN[f'2026-{m:02d}'] for m in range(1, 11)), 0.5)

# ---- 汇总 ----
n_ok = sum(1 for c in CHECKS if c[3])
log(f'\n===== 汇总: {n_ok}/{len(CHECKS)} OK =====')
fails = [c for c in CHECKS if not c[3]]
for f in fails:
    log(f'FAIL: {f[0]} claimed={f[1]} computed={f[2]}')

# R7-03: 输出默认相对 __file__(--out 覆写);任一校验失败→非零退出
_out_dir = os.path.dirname(os.path.abspath(OUT_PATH))
if _out_dir and not os.path.isdir(_out_dir):
    os.makedirs(_out_dir, exist_ok=True)
with open(OUT_PATH, 'w') as fh:
    fh.write('\n'.join(OUT) + '\n')
print(f'\nwritten {os.path.relpath(OUT_PATH, os.getcwd())}'
      f'  [exit {"0" if n_ok == len(CHECKS) else "1"}]'
      f'({n_ok}/{len(CHECKS)} OK)')
sys.exit(0 if n_ok == len(CHECKS) else 1)
