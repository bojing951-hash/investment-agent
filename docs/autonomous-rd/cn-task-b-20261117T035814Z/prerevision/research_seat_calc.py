#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 研究席自算脚本(标准库 only)— R5 audit B_run
研究问题: CN_NEW_LOANS(对实体经济人民币贷款,央行社融口径)与 CN_PMI_MFG(统计局
制造业PMI,季调,50荣枯线)对 CHINEXT(创业板指,本币,onshore)与 FXI(iShares
中国大盘ETF,美元计价复权,offshore 代理,含汇率影响)的影响。

═══════════ 口径声明(对齐方式/先行定义/防前视,全部显式) ═══════════
1. 月频对齐: 股指为日频——每月取该日历月最后一个可得收盘(月内最后观测)为月末价,
   月收益 r(M)=月末收盘(M)/月末收盘(M-1)-1。FXI=美元复权收盘;CHINEXT=指数收盘
   (无分红,指数口径)。宏观数值=该月度观测本身(序列日期即所属月)。
2. 同期(contemporaneous)相关 = 宏观(M) vs r(M): 描述性,非可操作——
   CN_NEW_LOANS(M) 由央行在 M+1 月中旬公布,r(M) 在公布前已走完,同期相关对贷款
   是纯事后;CN_PMI_MFG(M) 统计局于 M 月末(每月最后一天官方口径)公布,r(M) 大部分
   交易日发生在公布前。两者均已披露,同期数不用于任何"预测"表述。
3. 先行(lead-k) = 宏观(M) vs r(M+k),k=1,2,3: 宏观在前、股指在后。
   PMI: k=1 干净(M月末公布→M+1月初可知);贷款: k=1 部分污染(M+1月中旬才公布,
   M+1 月收益走了一半),k=2 起干净。本脚本对贷款主推 k=2,并披露 k=1 的污染。
4. 防前视: 所有宏观变换只用 ≤M 的观测——YoY差分用 M-12;12月均值比用 M-11..M;
   信用脉冲 CI(M)=sum(M-11..M)-sum(M-23..M-12)。绝无 >M 数据进入 M 期信号。
5. 相关系数=Pearson(附 t 与双侧 p,不完全 Beta 连分式精确计算)+Spearman 秩相关
   (稳健性);回归斜率=OLS+Newey-West HAC(lag=4)标准误。月收益自相关已另测。
6. 样本窗: 股指 2016-11 起才有数据 → 月收益自 2016-12 起;与宏观重叠
   2016-12..2026-10。宏观数本身 226 月全史(2008-01..2026-10),宏观单变量史实
   (分布/相位占比/负值月统计)用全史,跨资产统计只用重叠窗——两者分别标 n。
7. 无格兰杰因果检验、无协整/去趋势处理——先行相关若为弱/零,表述一律降级为
   "样本内描述性统计,不构成预测";事后相关≠预测。
8. CN_NEW_LOANS 实际口径=对实体经济发放的人民币贷款(人民银行社融口径),
   非全口径新增人民币贷款(引擎 calc 字段原话;2026-10=-5846亿 vs 央行全口径-1000亿)。
"""
import json, math, os

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seat_data')

# ---------- 不完全 Beta(t 分布精确 p 值,标准库实现) ----------
def betacf(a, b, x):
    MAXIT, EPS, FPMIN = 200, 3e-12, 1e-300
    qab, qap, qam = a+b, a+1.0, a-1.0
    c, d = 1.0, 1.0-qab*x/qap
    if abs(d) < FPMIN: d = FPMIN
    d = 1.0/d; h = d
    for m in range(1, MAXIT+1):
        m2 = 2*m
        aa = m*(b-m)*x/((qam+m2)*(a+m2))
        d = 1.0+aa*d;  d = FPMIN if abs(d) < FPMIN else d
        c = 1.0+aa/c;  c = FPMIN if abs(c) < FPMIN else c
        d = 1.0/d; h *= d*c
        aa = -(a+m)*(qab+m)*x/((a+m2)*(qap+m2))
        d = 1.0+aa*d;  d = FPMIN if abs(d) < FPMIN else d
        c = 1.0+aa/c;  c = FPMIN if abs(c) < FPMIN else c
        d = 1.0/d; de = d*c; h *= de
        if abs(de-1.0) < EPS: break
    return h

def betainc(a, b, x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    lbeta = math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b)
    front = math.exp(lbeta + a*math.log(x) + b*math.log(1.0-x))
    if x < (a+1.0)/(a+b+2.0):
        return front*betacf(a, b, x)/a
    return 1.0-front*betacf(b, a, 1.0-x)/b

def t_p(t, df):
    x = df/(df+t*t)
    return betainc(df/2.0, 0.5, x)

# ---------- 基础统计 ----------
def pearson(xs, ys):
    n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
    sxy = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    sxx = sum((x-mx)**2 for x in xs); syy = sum((y-my)**2 for y in ys)
    if sxx <= 0 or syy <= 0: return None
    r = sxy/math.sqrt(sxx*syy)
    r = max(-1.0, min(1.0, r))
    t = r*math.sqrt((n-2)/(1-r*r)) if n > 2 and abs(r) < 1 else float('inf')
    return r, t, t_p(t, n-2), n

def ranks(v):
    idx = sorted(range(len(v)), key=lambda i: v[i])
    out = [0.0]*len(v); i = 0
    while i < len(idx):
        j = i
        while j+1 < len(idx) and v[idx[j+1]] == v[idx[i]]: j += 1
        avg = (i+j)/2.0 + 1.0
        for k in range(i, j+1): out[idx[k]] = avg
        i = j+1
    return out

def spearman(xs, ys):
    return pearson(ranks(xs), ranks(ys))

def solve_lin(A, b):
    """高斯-约当消元解 A x = b(带部分主元)。"""
    n = len(A)
    M = [A[i][:]+[b[i]] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r2: abs(M[r2][c]))
        M[c], M[p] = M[p], M[c]
        if abs(M[c][c]) < 1e-300: return None
        for r2 in range(n):
            if r2 != c:
                f = M[r2][c]/M[c][c]
                M[r2] = [a-f*bb for a, bb in zip(M[r2], M[c])]
    return [M[i][n]/M[i][i] for i in range(n)]

def ols_nw(y, xmat, lag=4):
    """OLS + Newey-West HAC。xmat 每行=一个观测的自变量(不含常数,内部加)。"""
    n = len(y); k = len(xmat[0])+1
    X = [[1.0]+row for row in xmat]
    XtX = [[sum(X[i][a]*X[i][b] for i in range(n)) for b in range(k)] for a in range(k)]
    Xty = [sum(X[i][a]*y[i] for i in range(n)) for a in range(k)]
    beta = solve_lin(XtX, Xty)
    if beta is None: return None
    resid = [y[i]-sum(X[i][a]*beta[a] for a in range(k)) for i in range(n)]
    # (X'X)^{-1} 逐列求解
    cols = []
    for c in range(k):
        e = [1.0 if i == c else 0.0 for i in range(k)]
        col = solve_lin([row[:] for row in XtX], e)
        if col is None: return None
        cols.append(col)
    XtXinv = [[cols[c][r] for c in range(k)] for r in range(k)]  # [r][c]
    # NW meat
    S = [[0.0]*k for _ in range(k)]
    for i in range(n):
        xi, u = X[i], resid[i]
        for a in range(k):
            for b in range(k):
                S[a][b] += u*u*xi[a]*xi[b]
    for l in range(1, min(lag, n-1)+1):
        w = 1.0-l/(lag+1.0)
        for i in range(l, n):
            ui, ul = resid[i], resid[i-l]
            for a in range(k):
                for b in range(k):
                    S[a][b] += w*ui*ul*(X[i][a]*X[i-l][b]+X[i-l][a]*X[i][b])
    # V = (X'X)^-1 S (X'X)^-1
    V = [[sum(XtXinv[a][m]*S[m][b] for m in range(k)) for b in range(k)] for a in range(k)]
    V2 = [[sum(V[a][m]*XtXinv[b][m] for m in range(k)) for b in range(k)] for a in range(k)]
    se = [math.sqrt(max(V2[a][a], 0.0)) for a in range(k)]
    tv = [beta[a]/se[a] if se[a] > 0 else float('nan') for a in range(k)]
    pv = [t_p(tv[a], n-k) if se[a] > 0 else float('nan') for a in range(k)]
    r2 = 1.0-sum(e*e for e in resid)/sum((yi-sum(y)/n)**2 for yi in y)
    return beta, se, tv, pv, r2, n

def phase_stats(rets, label):
    if not rets: return f'{label}: n=0'
    n = len(rets); mu = sum(rets)/n
    sd = math.sqrt(sum((x-mu)**2 for x in rets)/(n-1)) if n > 1 else float('nan')
    win = sum(1 for x in rets if x > 0)/n
    srt = sorted(rets); med = srt[n//2] if n % 2 else (srt[n//2-1]+srt[n//2])/2
    return (f'{label}: n={n} 月均收益={mu*100:+.2f}%/月 中位={med*100:+.2f}% '
            f'胜率={win*100:.0f}% 月度标准差={sd*100:.2f}%')

def welch_t(a, b):
    na, nb = len(a), len(b)
    ma, mb = sum(a)/na, sum(b)/nb
    va = sum((x-ma)**2 for x in a)/(na-1); vb = sum((x-mb)**2 for x in b)/(nb-1)
    se2 = va/na+vb/nb
    t = (ma-mb)/math.sqrt(se2) if se2 > 0 else float('nan')
    df = se2*se2/((va/na)**2/(na-1)+(vb/nb)**2/(nb-1)) if se2 > 0 else 1
    return t, df, t_p(t, df)

# ---------- 装载 ----------
def load(m):
    s = json.load(open(os.path.join(DATA, m+'.json')))['data']['series']
    return dict(zip(s['dates'], s['values'])), s

fxi, sfxi = load('FXI'); chx, schx = load('CHINEXT')
pmi_raw, spmi = load('CN_PMI_MFG'); loans_raw, sloans = load('CN_NEW_LOANS')
# 宏观序列键为 YYYY-MM-01 → 统一为 YYYY-MM
pmi = {k[:7]: v for k, v in pmi_raw.items()}
loans = {k[:7]: v for k, v in loans_raw.items()}

# ---------- 股指月频化: 月末最后收盘 ----------
def monthly_close(d):
    """月末价=该日历月最后一个交易日收盘;返回 {YYYY-MM:(最后日期,收盘)}。"""
    out = {}
    for date, v in d.items():
        ym = date[:7]
        if ym not in out or date > out[ym][0]:
            out[ym] = (date, v)
    return dict(sorted(out.items()))

fxi_m, chx_m = monthly_close(fxi), monthly_close(chx)
yms = sorted(set(fxi_m) & set(chx_m))
def month_ret(mclose, ym):
    i = yms.index(ym)
    return mclose[ym][1]/mclose[yms[i-1]][1]-1 if i > 0 else None
rets = {}
for ym in yms:
    rf = month_ret(fxi_m, ym); rc = month_ret(chx_m, ym)
    if rf is not None and rc is not None:
        rets[ym] = (rc, rf)   # (CHINEXT, FXI)
ret_months = sorted(rets)
# 剔除不完整末月: 仅当样本最后一个月的月末观测日为月中(数据截至月中)时剔除。
# 注: 2020-01 CHINEXT 月末=01-23(春节+疫情延长休市)是真实月末,不剔;
# 两指数交易日历不同导致的月末日期错位(≤数日)作为口径披露,不做删改。
last_ym = ret_months[-1]
if min(fxi_m[last_ym][0][8:10], chx_m[last_ym][0][8:10]) < '25':
    print(f'[对齐] 剔除残月 {last_ym}(月末观测为月中 {fxi_m[last_ym][0]}/{chx_m[last_ym][0]},'
          '该月未走完,非完整月)')
    del rets[last_ym]; ret_months.remove(last_ym)
print(f'[对齐] 月收益区间 {ret_months[0]}..{ret_months[-1]} n={len(ret_months)}')

# ---------- 宏观变换(全部只用 ≤M 观测) ----------
pmi_keys = sorted(pmi)
def pmi_diff(m):
    i = pmi_keys.index(m)
    return pmi[m]-pmi[pmi_keys[i-1]] if i > 0 else None
loan_keys = sorted(loans)
def l_sum(m_from, m_to):
    return sum(loans[k] for k in loan_keys[loan_keys.index(m_from):loan_keys.index(m_to)+1])
def loans_yoy_diff(m):   # 同比差(亿),稳健于负基数
    i = loan_keys.index(m)
    return loans[m]-loans[loan_keys[i-12]] if i >= 12 else None
def loans_ratio12(m):    # 与近12月均值之比
    i = loan_keys.index(m)
    return loans[m]/(sum(loans[k] for k in loan_keys[i-11:i+1])/12.0) if i >= 11 else None
def credit_impulse(m):   # 12月滚动和的同比变化(亿)
    i = loan_keys.index(m)
    if i < 23: return None
    return (sum(loans[k] for k in loan_keys[i-11:i+1])
            - sum(loans[k] for k in loan_keys[i-23:i-11]))

# ---------- 全史宏观事实(E1 锚,2008-01..2026-10 n=226) ----------
pmi_vals = [pmi[k] for k in pmi_keys]
n_below50 = sum(1 for v in pmi_vals if v < 50)
loan_vals = [loans[k] for k in loan_keys]
n_neg = sum(1 for v in loan_vals if v < 0)
jan_vals = [loans[k] for k in loan_keys if k[5:7] == '01']
print(f'\n[全史 E1] CN_PMI_MFG n={len(pmi_vals)}({pmi_keys[0]}..{pmi_keys[-1]}) '
      f'均值={sum(pmi_vals)/len(pmi_vals):.2f} 最小={min(pmi_vals):.1f}({pmi_keys[pmi_vals.index(min(pmi_vals))][:7]}) '
      f'最大={max(pmi_vals):.1f}({pmi_keys[pmi_vals.index(max(pmi_vals))][:7]}) <50月数={n_below50}({n_below50/len(pmi_vals)*100:.0f}%)')
print(f'[全史 E1] 2016-12起重叠窗内 PMI<50 占比: '
      f'{sum(1 for k in ret_months if k in pmi and pmi[k] < 50)}/{sum(1 for k in ret_months if k in pmi)}')
print(f'[全史 E1] CN_NEW_LOANS(对实体口径) n={len(loan_vals)} 负值月={n_neg} '
      f'1月均值={sum(jan_vals)/len(jan_vals):.0f}亿 vs 全史月均={sum(loan_vals)/len(loan_vals):.0f}亿')
neg_by_cal = {}
for k in loan_keys:
    if loans[k] < 0: neg_by_cal.setdefault(k[5:7], []).append(k)
print(f'[全史 E1] 负值月按日历月分布: ' + ', '.join(f'{m}月x{len(v)}' for m, v in sorted(neg_by_cal.items())))
ci_now = credit_impulse('2026-10')
ci_hist = [(k, credit_impulse(k)) for k in loan_keys if credit_impulse(k) is not None]
ci_sorted = sorted(c for _, c in ci_hist)
pct = sum(1 for c in ci_sorted if c <= ci_now)/len(ci_sorted)*100
print(f'[全史 E1] 信用脉冲 CI(2026-10)={ci_now/10000:+.2f}万亿 历史百分位={pct:.1f}% '
      f'(CI可得月数 n={len(ci_sorted)},历史区间[{min(ci_sorted)/10000:+.2f},{max(ci_sorted)/10000:+.2f}]万亿)')

# ---------- 相关: 同期与先行 ----------
print('\n[相关] 股指月收益 vs 宏观(重叠窗;先行=宏观在前防前视,贷款k=1有月中公布污染已披露)')
def yoy_tr(m):
    v = loans_yoy_diff(m)
    return None if v is None else v/10000.0
def ci_tr(m):
    v = credit_impulse(m)
    return None if v is None else v/10000.0
metrics = {
    'PMI水平': lambda m: pmi.get(m),
    'PMI环比差分': lambda m: pmi_diff(m),
    '新增贷款同比差(万亿)': yoy_tr,
    '贷款/近12月均值比': lambda m: loans_ratio12(m),
    '信用脉冲CI(万亿)': ci_tr,
}
def lead_corr(fn, k, col):
    xs, ys = [], []
    for i, m in enumerate(ret_months):
        j = i+k
        if j < len(ret_months) and fn(m) is not None:
            xs.append(fn(m)); ys.append(rets[ret_months[j]][col])
    return xs, ys

hdr = f"{'指标':<14}{'先行k':>5} {'资产':<9}{'n':>4} {'Pearson r':>10} {'t':>7} {'p':>7} {'Spearman':>9}"
print(hdr)
for name, fn in metrics.items():
    for k in (0, 1, 2, 3):
        for ci, asset in ((0, 'CHINEXT'), (1, 'FXI')):
            xs, ys = lead_corr(fn, k, ci)
            if len(xs) < 10: continue
            pr = pearson(xs, ys); sp = spearman(xs, ys)
            print(f'{name:<14}{k:>5} {asset:<9}{pr[3]:>4} {pr[0]:>10.3f} {pr[1]:>7.2f} {pr[2]:>7.3f} {sp[0]:>9.3f}')

# 两股指月收益互相关(美元/离岸 vs 本币/在岸 混杂讨论的 E1 锚)
pair = pearson([rets[m][0] for m in ret_months], [rets[m][1] for m in ret_months])
print(f'\n[E1] CHINEXT vs FXI 月收益同步性: r={pair[0]:.3f} t={pair[1]:.2f} p={pair[2]:.4f} n={pair[3]} '
      f'(同月同向比例={sum(1 for m in ret_months if rets[m][0]*rets[m][1] > 0)/len(ret_months)*100:.0f}%)')
mu_c = sum(rets[m][0] for m in ret_months)/len(ret_months)*100
mu_f = sum(rets[m][1] for m in ret_months)/len(ret_months)*100
print(f'[E1] 重叠窗月均: CHINEXT={mu_c:+.2f}%/月 FXI={mu_f:+.2f}%/月 差={mu_c-mu_f:+.2f}pp/月')

# ---------- 相位统计 ----------
print('\n[相位] PMI>50 vs <50(同月=描述性;下月=可操作先行)')
for k, lab in ((0, '同月(描述性)'), (1, '下月(PMI月末公布→干净先行)')):
    for ci, asset in ((0, 'CHINEXT'), (1, 'FXI')):
        hi, lo = [], []
        for i, m in enumerate(ret_months):
            j = i+k
            if j >= len(ret_months) or m not in pmi: continue
            (hi if pmi[m] > 50 else lo).append(rets[ret_months[j]][ci])
        print(f'  k={k} {lab} {asset}: ' + phase_stats(hi, 'PMI>50') + ' | ' + phase_stats(lo, 'PMI<50'))
        if len(hi) > 2 and len(lo) > 2:
            t, df, p = welch_t(hi, lo)
            print(f'      Welch t={t:+.2f} df={df:.0f} p={p:.3f}')

print('\n[相位] PMI环比上行(Δ>0) vs 下行(Δ<0)对下月收益')
for ci, asset in ((0, 'CHINEXT'), (1, 'FXI')):
    hi, lo = [], []
    for i, m in enumerate(ret_months):
        if i+1 >= len(ret_months) or pmi_diff(m) is None: continue
        (hi if pmi_diff(m) > 0 else lo).append(rets[ret_months[i+1]][ci])
    print(f'  {asset}: ' + phase_stats(hi, 'ΔPMI>0') + ' | ' + phase_stats(lo, 'ΔPMI<0'))
    if len(hi) > 2 and len(lo) > 2:
        t, df, p = welch_t(hi, lo)
        print(f'      Welch t={t:+.2f} df={df:.0f} p={p:.3f}')

print('\n[相位] 信用脉冲CI>0(信用扩张) vs <0(收缩)对下月与隔月收益')
for k, lab in ((1, '下月(含公布污染,仅参考)'), (2, '隔月(干净先行)')):
    for ci, asset in ((0, 'CHINEXT'), (1, 'FXI')):
        hi, lo = [], []
        for i, m in enumerate(ret_months):
            j = i+k
            if j >= len(ret_months) or credit_impulse(m) is None: continue
            (hi if credit_impulse(m) > 0 else lo).append(rets[ret_months[j]][ci])
        print(f'  k={k} {lab} {asset}: ' + phase_stats(hi, 'CI>0') + ' | ' + phase_stats(lo, 'CI<0'))
        if len(hi) > 2 and len(lo) > 2:
            t, df, p = welch_t(hi, lo)
            print(f'      Welch t={t:+.2f} df={df:.0f} p={p:.3f}')

print('\n[相位] CI边际方向 ΔCI>0 vs <0 对下月收益(信用脉冲二阶)')
def ci_delta(m):
    i = loan_keys.index(m)
    if i < 24: return None
    return credit_impulse(m)-credit_impulse(loan_keys[i-1])
for ci, asset in ((0, 'CHINEXT'), (1, 'FXI')):
    hi, lo = [], []
    for i, m in enumerate(ret_months):
        if i+1 >= len(ret_months) or ci_delta(m) is None: continue
        (hi if ci_delta(m) > 0 else lo).append(rets[ret_months[i+1]][ci])
    print(f'  {asset}: ' + phase_stats(hi, 'ΔCI>0') + ' | ' + phase_stats(lo, 'ΔCI<0'))

# ---------- 预测回归(NW-HAC;控制收益自身滞后) ----------
print('\n[回归] r(M+k) ~ 宏观(M) + r(M) 收益自身滞后控制(Newey-West HAC lag=4,括号=t)')
def pred_reg(fn, k, col, name):
    y, xs = [], []
    for i, m in enumerate(ret_months):
        j = i+k
        if j >= len(ret_months) or fn(m) is None: continue
        y.append(rets[ret_months[j]][col]); xs.append([fn(m), rets[m][col]])
    if len(y) < 20: return
    beta, se, tv, pv, r2, n = ols_nw(y, xs)
    print(f'  {name} k={k} {"CHINEXT" if col == 0 else "FXI"}: '
          f'宏观β={beta[1]:+.5f}(t={tv[1]:+.2f},p={pv[1]:.3f}) '
          f'收益滞后β={beta[2]:+.3f}(t={tv[2]:+.2f}) R2={r2:.3f} n={n}')

for name, fn in (('PMI环比差分', lambda m: pmi_diff(m)),
                 ('信用脉冲CI(万亿)', ci_tr),
                 ('贷款/12月均值比', lambda m: loans_ratio12(m))):
    for k in (1, 2):
        for col in (0, 1):
            pred_reg(fn, k, col, name)

# ---------- 收益自相关(方法学披露) ----------
r0 = [rets[m][0] for m in ret_months]
ac1 = pearson(r0[:-1], r0[1:])
print(f'\n[方法] CHINEXT 月收益 lag-1 自相关 r={ac1[0]:+.3f}(p={ac1[2]:.3f}) → NW 修正依据')

# ---------- 当前状态锚 ----------
print('\n[当前锚] 近12月PMI: ' + ', '.join(f'{k[:7]}={pmi[k]}' for k in pmi_keys[-12:]))
print('[当前锚] 近12月新增贷款(亿): ' + ', '.join(f'{k[:7]}={loans[k]:.0f}' for k in loan_keys[-12:]))

# ---------- 补充A: NW-t 与经典/HC0-t 交叉验证(ΔPMI k=1 CHINEXT 反常强t) ----------
print('\n[稳健性] ΔPMI(M) 对 r(M+1,CHINEXT) 回归: NW-t vs 经典t vs HC0-t vs Pearson-t')
xs, ys = [], []
for i, m in enumerate(ret_months):
    if i+1 < len(ret_months) and pmi_diff(m) is not None:
        xs.append(pmi_diff(m)); ys.append(rets[ret_months[i+1]][0])
n_ = len(xs); mx_ = sum(xs)/n_; my_ = sum(ys)/n_
sxx = sum((a-mx_)**2 for a in xs)
beta_raw = sum((a-mx_)*(b-my_) for a, b in zip(xs, ys))/sxx
alpha_raw = my_-beta_raw*mx_
u_ = [b-alpha_raw-beta_raw*a for a, b in zip(xs, ys)]
se_cl = math.sqrt(sum(e*e for e in u_)/(n_-2)/(sxx))
X_ = [[1.0, a] for a in xs]
XtX = [[sum(X_[i][a]*X_[i][b] for i in range(n_)) for b in range(2)] for a in range(2)]
cols_ = [solve_lin([r[:] for r in XtX], [1.0 if i == c else 0.0 for i in range(2)]) for c in range(2)]
XtXinv_ = [[cols_[c][r] for c in range(2)] for r in range(2)]
S_ = [[0.0]*2 for _ in range(2)]
for i in range(n_):
    xi, ui = X_[i], u_[i]
    for a in range(2):
        for b in range(2): S_[a][b] += ui*ui*xi[a]*xi[b]
V_ = [[sum(XtXinv_[a][m]*S_[m][b] for m in range(2)) for b in range(2)] for a in range(2)]
V2_ = [[sum(V_[a][m]*XtXinv_[b][m] for m in range(2)) for b in range(2)] for a in range(2)]
se_hc0 = math.sqrt(V2_[1][1])
pr_ = pearson(xs, ys)
print(f'  beta={beta_raw:+.5f} 经典t={beta_raw/se_cl:+.2f} HC0-t={beta_raw/se_hc0:+.2f} '
      f'Pearson-t={pr_[1]:+.2f} (NW-t=+4.46 见上;差异=控制收益滞后+HAC,'
      f'Pearson r={pr_[0]:.3f} vs Spearman={spearman(xs, ys)[0]:.3f} → 线性相关被少数极值月驱动,秩相关近零)')

# ---------- 补充B: 情景历史锚(E1,重叠窗内) ----------
print('\n[情景锚] 历史上 CI<-3万亿(深信用收缩)后的下月股指收益(重叠窗内)')
sel = [(m, rets[ret_months[i+1]]) for i, m in enumerate(ret_months)
       if i+1 < len(ret_months) and credit_impulse(m) is not None and credit_impulse(m) < -30000]
if sel:
    print('  事件月: ' + ', '.join(m for m, _ in sel))
    print('  ' + phase_stats([r[0] for _, r in sel], 'CI<-3万亿→下月CHINEXT'))
    print('  ' + phase_stats([r[1] for _, r in sel], 'CI<-3万亿→下月FXI'))
print('\n[情景锚] PMI<50 且 CI<0(双重收缩)后的下月收益')
sel2 = [(m, rets[ret_months[i+1]]) for i, m in enumerate(ret_months)
        if i+1 < len(ret_months) and m in pmi and pmi[m] < 50
        and credit_impulse(m) is not None and credit_impulse(m) < 0]
print(f'  事件月数 n={len(sel2)}: ' + ', '.join(m for m, _ in sel2))
if sel2:
    print('  ' + phase_stats([r[0] for _, r in sel2], '双重收缩→下月CHINEXT'))
    print('  ' + phase_stats([r[1] for _, r in sel2], '双重收缩→下月FXI'))
print('\n[情景锚] ΔCI相位 Welch 检验(补上)')
for ci, asset in ((0, 'CHINEXT'), (1, 'FXI')):
    hi, lo = [], []
    for i, m in enumerate(ret_months):
        if i+1 >= len(ret_months) or ci_delta(m) is None: continue
        (hi if ci_delta(m) > 0 else lo).append(rets[ret_months[i+1]][ci])
    t, df, p = welch_t(hi, lo)
    print(f'  {asset}: ΔCI>0 vs <0 下月收益 Welch t={t:+.2f} df={df:.0f} p={p:.3f}')

# ---------- 补充C: 两宏观指标内部一致性 ----------
pairs = [(m, pmi[m], credit_impulse(m)) for m in ret_months
         if m in pmi and credit_impulse(m) is not None]
r_pci = pearson([p for _, p, _ in pairs], [c/10000.0 for _, _, c in pairs])
print(f'\n[宏观内部] PMI水平 vs 信用脉冲CI 同月相关: r={r_pci[0]:+.3f} t={r_pci[1]:+.2f} '
      f'p={r_pci[2]:.3f} n={r_pci[3]} → 两大宏观信号本身仅弱同步,'
      '"宏观信用×制造业景气"并非单一共同因子')

# ---------- 补充D: PMI相位结果的极值依赖与秩检验 ----------
def mannwhitney(a, b):
    """Mann-Whitney U 双侧 p(正态近似,无并列校正)。"""
    allv = [(v, 0) for v in a]+[(v, 1) for v in b]
    rk = ranks([v for v, _ in allv])
    r1 = sum(rk[i] for i in range(len(allv)) if allv[i][1] == 0)
    n1, n2 = len(a), len(b)
    mu = n1*(n1+n2+1)/2.0
    su = n1*n2*(n1+n2+1)/12.0
    z = (r1-mu)/math.sqrt(su)
    p = 2.0*(1.0-0.5*(1.0+math.erf(abs(z)/math.sqrt(2.0))))
    return z, p

print('\n[稳健性] PMI相位(k=1)结果的极值依赖: 各相位收益 top3 月与去尾均值')
for ci, asset in ((0, 'CHINEXT'), (1, 'FXI')):
    hi = [(rets[ret_months[i+1]][ci], ret_months[i+1], m) for i, m in enumerate(ret_months)
          if i+1 < len(ret_months) and m in pmi and pmi[m] > 50]
    lo = [(rets[ret_months[i+1]][ci], ret_months[i+1], m) for i, m in enumerate(ret_months)
          if i+1 < len(ret_months) and m in pmi and pmi[m] < 50]
    for lab, arr in (('PMI>50', hi), ('PMI<50', lo)):
        vv = sorted(x[0] for x in arr)
        trim = vv[2:-2] if len(vv) > 8 else vv
        top3 = sorted(arr, key=lambda x: -x[0])[:3]
        print(f'  {asset} {lab}: 去首尾各2月均值={sum(trim)/len(trim)*100:+.2f}%/月 '
              f'(全样本均值={sum(x[0] for x in arr)/len(arr)*100:+.2f}%) '
              f'top3: ' + ', '.join(f'{m_}→{r_*100:+.1f}%(信号月{s})' for r_, m_, s in top3))
    z, p = mannwhitney([x[0] for x in hi], [x[0] for x in lo])
    print(f'  {asset} PMI相位 Mann-Whitney z={z:+.2f} p={p:.3f}')

print('\n[稳健性] 重叠窗 CHINEXT/FXI 最大单月(相位上下文)')
for ci, asset in ((0, 'CHINEXT'), (1, 'FXI')):
    sr = sorted(((rets[m][ci], m) for m in ret_months), key=lambda x: -abs(x[0]))[:5]
    print(f'  {asset}: ' + ', '.join(f'{m}={v*100:+.1f}%(当月PMI={pmi.get(m,"NA")})' for v, m in sr))
