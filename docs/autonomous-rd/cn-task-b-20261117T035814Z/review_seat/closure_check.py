#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
闭环复验(修订v2): 用本席独立实现复算修订后引用的全部新数字。
只核修处 + 周边不变性;数据/对齐/变换与 recompute.py 同源(重新实现调用)。
"""
import json
import math
import os

DATA = '/tmp/audit_r5/B_run/seat_data'


def t_pdf(x, df):
    ln = (math.lgamma((df + 1) / 2.0) - math.lgamma(df / 2.0)
          - 0.5 * math.log(df * math.pi))
    return math.exp(ln - (df + 1) / 2.0 * math.log1p(x * x / df))


def t_p_two(t, df):
    a = abs(t)
    if a == 0:
        return 1.0
    n = 40000
    h = a / n
    s = t_pdf(0.0, df) + t_pdf(a, df)
    for i in range(1, n):
        s += t_pdf(i * h, df) * (4.0 if i % 2 else 2.0)
    return max(0.0, min(1.0, 2.0 * (0.5 - s * h / 3.0)))


def mean(xs):
    return sum(xs) / len(xs)


def stdev(xs):
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def median(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def welch(a, b):
    na, nb = len(a), len(b)
    va, vb = stdev(a) ** 2, stdev(b) ** 2
    se2 = va / na + vb / nb
    t = (mean(a) - mean(b)) / math.sqrt(se2)
    df = se2 ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    return t, df, t_p_two(t, df)


def load(m):
    s = json.load(open(os.path.join(DATA, m + '.json'), encoding='utf-8'))['data']['series']
    return list(zip(s['dates'], s['values']))


def month_end(series):
    out = {}
    for d, v in series:
        ym = d[:7]
        if ym not in out or d > out[ym][0]:
            out[ym] = (d, v)
    return out


pmi = {d[:7]: v for d, v in load('CN_PMI_MFG')}
me_fx, me_ch = month_end(load('FXI')), month_end(load('CHINEXT'))
ms = sorted(set(me_fx) & set(me_ch))
rets, prev = {}, None
for ym in ms:
    if prev:
        rets[ym] = (me_ch[ym][1] / me_ch[prev][1] - 1.0,
                    me_fx[ym][1] / me_fx[prev][1] - 1.0)
    prev = ym
rm = sorted(rets)
if min(int(me_fx[rm[-1]][0][8:10]), int(me_ch[rm[-1]][0][8:10])) < 25:
    del rets[rm[-1]]
    rm.remove(rm[-1])
pmi_keys = sorted(pmi)


def pmi_diff(m):
    i = pmi_keys.index(m)
    return pmi[m] - pmi[pmi_keys[i - 1]]


def pstats(v):
    return (len(v), mean(v) * 100, median(v) * 100,
            sum(1 for x in v if x > 0) / len(v) * 100, stdev(v) * 100)


R = []


def chk(cid, desc, got, exp, tol=0.005):
    ok = (got == exp) if isinstance(exp, str) else (abs(got - exp) <= tol)
    R.append((cid, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {cid} {desc}: 复算={got} 修订引用={exp}")


print('== C1 严格分组(k=1)全部引用数字 ==')
for col, an in ((0, 'CHINEXT'), (1, 'FXI')):
    hi, lo = [], []
    for i, m in enumerate(rm):
        if i + 1 >= len(rm):
            continue
        if pmi[m] > 50:
            hi.append(rets[rm[i + 1]][col])
        elif pmi[m] < 50:
            lo.append(rets[rm[i + 1]][col])
    n, mu, med, win, sd = pstats(lo)
    t, df, p = welch(hi, lo)
    if an == 'CHINEXT':
        chk('C1a', 'lo n', n, 48, 0)
        chk('C1b', 'lo 月均%', mu, 2.14)
        chk('C1c', 'lo 中位%', med, 0.98)
        chk('C1d', 'lo 胜率%', win, 58, 0.5)
        chk('C1e', 'lo σ%', sd, 9.81)
        chk('C1f', 'Welch t', t, -1.70, 0.005)
        chk('C1g', 'Welch df', df, 84, 0.5)
        chk('C1h', 'Welch p', p, 0.092, 0.0015)
        nh, muh, medh, winh, sdh = pstats(hi)
        chk('C1i', 'hi n/月均/中位/胜率/σ 不变', f'{nh}/{muh:.2f}/{medh:.2f}/{winh:.0f}/{sdh:.2f}',
            '67/-0.74/-1.22/39/7.50', None)
    else:
        chk('C1j', 'FXI lo n', n, 48, 0)
        chk('C1k', 'FXI lo 月均%', mu, 1.45)
        chk('C1l', 'FXI lo 中位%', med, 0.34)
        chk('C1m', 'FXI lo 胜率%', win, 50, 0.5)
        chk('C1n', 'FXI lo σ%(CL-4=8.07)', sd, 8.07)
        chk('C1o', 'FXI Welch t', t, -1.16, 0.005)
        chk('C1p', 'FXI Welch p(MC-3E3/SCN-4=0.250)', p, 0.250, 0.0015)

print('== C2 截尾均值(严格组, CL-3 +1.58% vs -0.57%) ==')
lo_r = sorted(rets[rm[i + 1]][0] for i, m in enumerate(rm)
              if i + 1 < len(rm) and pmi[m] < 50)
hi_r = sorted(rets[rm[i + 1]][0] for i, m in enumerate(rm)
              if i + 1 < len(rm) and pmi[m] > 50)
chk('C2a', '严格lo 截尾均值%', mean(lo_r[2:-2]) * 100, 1.58)
chk('C2b', 'hi 截尾均值%(不变)', mean(hi_r[2:-2]) * 100, -0.57)

print('== C3 k=0 描述行(严格, v2输出) ==')
for col, an, exps in ((0, 'CHINEXT', (49, 0.18, -1.04, 49, 10.48, 0.933)),
                      (1, 'FXI', (49, 0.68, -0.45, 49, 8.59, 0.734))):
    hi, lo = [], []
    for m in rm:
        if pmi[m] > 50:
            hi.append(rets[m][col])
        elif pmi[m] < 50:
            lo.append(rets[m][col])
    n, mu, med, win, sd = pstats(lo)
    _, _, p = welch(hi, lo)
    chk(f'C3-{an}', f'k=0 {an} lo n/月均/中位/胜率/σ/p',
        f'{n}/{mu:.2f}/{med:.2f}/{win:.0f}/{sd:.2f}/{p:.3f}',
        f'{exps[0]}/{exps[1]:.2f}/{exps[2]:.2f}/{exps[3]}/{exps[4]:.2f}/{exps[5]:.3f}', None)

print('== C4 ΔPMI 严格块(v2输出) ==')
for col, an, exps in ((0, 'CHINEXT', (64, 0.43, -0.93, 47, 8.24, 0.984)),
                      (1, 'FXI', (64, 0.81, 0.52, 53, 7.54, 0.624))):
    hi, lo = [], []
    for i, m in enumerate(rm):
        if i + 1 >= len(rm) or m not in pmi or pmi_keys.index(m) == 0:
            continue
        d = pmi_diff(m)
        if d > 0:
            hi.append(rets[rm[i + 1]][col])
        elif d < 0:
            lo.append(rets[rm[i + 1]][col])
    n, mu, med, win, sd = pstats(lo)
    _, _, p = welch(hi, lo)
    chk(f'C4-{an}', f'ΔPMI {an} lo n/月均/中位/胜率/σ/p',
        f'{n}/{mu:.2f}/{med:.2f}/{win:.0f}/{sd:.2f}/{p:.3f}',
        f'{exps[0]}/{exps[1]:.2f}/{exps[2]:.2f}/{exps[3]}/{exps[4]:.2f}/{exps[5]:.3f}', None)

print('== C5 持平月披露与 1-r² ==')
tie = [m for m in rm if pmi[m] == 50.0]
chk('C5a', 'PMI=50.0持平月(判定档basis披露)', ','.join(tie), '2018-11,2020-01,2026-05', None)
chk('C5b', '1-r²(MC-3 改文≈88%)', round(1 - 0.351 ** 2, 3), 0.877, 0.001)

n_ok = sum(1 for _, ok in R if ok)
print(f'\n闭环复算项: {len(R)}, PASS: {n_ok}, FAIL: {len(R) - n_ok}')
