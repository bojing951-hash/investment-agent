#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补充: 弱化起始精确定位+敏感度(beta)+2026 年内路径。数据源同 blind_calc.py"""
import json, math

import os
# Audit-R1 F05: 去绝对路径——默认引擎树本地相对解析,可用环境变量
# IA_ENGINE_DAILY 覆盖(净克隆/异机可复现,免硬编码用户目录)
DEV = os.environ.get('IA_ENGINE_DAILY',
                     os.path.expanduser('~/investment-agent-dev/data/daily'))
snap = json.load(open(f'{DEV}/research_snapshot_20261112_v2.json'))
ss = snap['series_store']
macro = json.load(open(f'{DEV}/macro_20261112.json'))['data']

GOLD = dict(zip(ss['GOLD_F']['dates'], ss['GOLD_F']['values']))
DXY = dict(zip(ss['DXY']['dates'], ss['DXY']['values']))
VIX = dict(zip(ss['VIX']['dates'], ss['VIX']['values']))
UST = dict(zip(macro['UST_10Y']['series']['dates'], macro['UST_10Y']['series']['values']))
BEI = dict(zip(macro['BEI_10Y']['series']['dates'], macro['BEI_10Y']['series']['values']))
REAL = {d: round(UST[d]-BEI[d], 4) for d in UST if d in BEI}

common = sorted(set(GOLD) & set(REAL) & set(DXY) & set(VIX))
dates = common
n = len(dates)
gold = [GOLD[d] for d in dates]; real = [REAL[d] for d in dates]
dxy = [DXY[d] for d in dates]; vix = [VIX[d] for d in dates]

def pct(v): return [None]+[(v[i]/v[i-1]-1)*100 for i in range(1,len(v))]
def diff(v): return [None]+[v[i]-v[i-1] for i in range(1,len(v))]
ust=[UST[d] for d in dates]
g_ret=pct(gold); r_chg=diff(real); d_ret=pct(dxy); u_chg=diff(ust)

def pearson(x,y):
    pts=[(a,b) for a,b in zip(x,y) if a is not None and b is not None]
    if len(pts)<3: return None,len(pts)
    mx=sum(p[0] for p in pts)/len(pts); my=sum(p[1] for p in pts)/len(pts)
    cov=sum((p[0]-mx)*(p[1]-my) for p in pts)
    vx=sum((p[0]-mx)**2 for p in pts); vy=sum((p[1]-my)**2 for p in pts)
    if vx<=0 or vy<=0: return None,len(pts)
    return cov/math.sqrt(vx*vy),len(pts)

def beta(x,y):
    """OLS slope: y on x (gold ret on rate chg)"""
    pts=[(a,b) for a,b in zip(x,y) if a is not None and b is not None]
    mx=sum(p[0] for p in pts)/len(pts); my=sum(p[1] for p in pts)/len(pts)
    vx=sum((p[0]-mx)**2 for p in pts)
    cov=sum((p[0]-mx)*(p[1]-my) for p in pts)
    return cov/vx if vx>0 else None, len(pts)

# 月度滚动252均值 2024-01..2026-11 + 滚动126
def rolling(a,b,win):
    out=[]
    for i in range(len(a)):
        if i<win: out.append(None); continue
        r_,_=pearson(a[i-win+1:i+1],b[i-win+1:i+1]); out.append(r_)
    return out

r252 = rolling(g_ret,r_chg,252)
d252 = rolling(g_ret,d_ret,252)
u252 = rolling(g_ret,u_chg,252)
r126 = rolling(g_ret,r_chg,126)
d126 = rolling(g_ret,d_ret,126)

print('=== 月末滚动252日相关(2024-01起) ===')
print('月末 | GOLD~REAL252 | GOLD~UST252 | GOLD~DXY252 | GOLD~REAL126 | GOLD~DXY126')
last_m=None
for i,d in enumerate(dates):
    if d<'2024-01-01': continue
    m=d[:7]
    if m==last_m: continue
    if i+1<len(dates) and dates[i+1][:7]==m: continue  # 月末
    last_m=m
    f=lambda v: f'{v:+.3f}' if v is not None else '  —  '
    print(f'{d} | {f(r252[i])} | {f(u252[i])} | {f(d252[i])} | {f(r126[i])} | {f(d126[i])}')

# 首次持续 > -0.20 (60日)
for name,roll in [('GOLD~REAL252',r252),('GOLD~UST252',u252),('GOLD~DXY252',d252)]:
    run=0; first=None
    for i,d in enumerate(dates):
        v=roll[i]
        if v is not None and v>-0.20:
            run+=1
            if run>=60 and first is None: first=(dates[i-59],d)
        else: run=0
    print(f'{name} 首次连续60日 > -0.20 区间: {first}')

# 分段 beta 与相关(敏感度)
print('\n=== 分段敏感度: gold日收益% 对 实际利率日变化pp 的回归斜率 ===')
spans=[('2017-2019','2017','2019'),('2020-2021','2020','2021'),('2022-2023','2022','2023'),('2024','2024','2024'),('2025','2025','2025'),('2026','2026','2026')]
for lab,lo,hi in spans:
    idx=[i for i in range(1,n) if lo<=dates[i][:4]<=hi]
    b_,nn=beta([r_chg[i] for i in idx],[g_ret[i] for i in idx])
    r_,_=pearson([r_chg[i] for i in idx],[g_ret[i] for i in idx])
    b2_,_=beta([d_ret[i] for i in idx],[g_ret[i] for i in idx])
    r2_,_=pearson([d_ret[i] for i in idx],[g_ret[i] for i in idx])
    print(f'{lab}: n={nn} | REAL: beta={b_:+.3f}%/pp r={r_:+.3f} | DXY: beta={b2_:+.3f}%/% r={r2_:+.3f}')

# 2026 年内路径(月度)
print('\n=== 2026 月度路径 ===')
print('月 | GOLD末 | REAL末 | DXY末 | VIX末 | 月内GOLD% | 月内REALpp | 月内DXY%')
for m in [f'2026-{i:02d}' for i in range(1,12)]:
    idx=[i for i,d in enumerate(dates) if d.startswith(m)]
    if not idx: continue
    i0,i1=idx[0],idx[-1]
    print(f'{m} | {gold[i1]:7.1f} | {real[i1]:.2f} | {dxy[i1]:6.2f} | {vix[i1]:5.2f} | {(gold[i1]/gold[i0]-1)*100:+6.2f}% | {real[i1]-real[i0]:+.2f} | {(dxy[i1]/dxy[i0]-1)*100:+5.2f}%')

# 2025 月度(弱化发生年)
print('\n=== 2025 月度路径 ===')
for m in [f'2025-{i:02d}' for i in range(1,13)]:
    idx=[i for i,d in enumerate(dates) if d.startswith(m)]
    if not idx: continue
    i0,i1=idx[0],idx[-1]
    print(f'{m} | {gold[i1]:7.1f} | {real[i1]:.2f} | {dxy[i1]:6.2f} | {(gold[i1]/gold[i0]-1)*100:+6.2f}% | {real[i1]-real[i0]:+.2f}pp | {(dxy[i1]/dxy[i0]-1)*100:+5.2f}%')

# 极端日检验: 实际利率大幅上行日(>=5bp)黄金表现
# Audit-R1 F06 修: 旧过滤 r_chg>=5 把 pp 当 bp(5pp=500bp)→n=0 恒空,
# judgment 所引 n=27/+0.07% 不可由本脚本复现。阈值改 0.05pp 并增补
# judgment 所引的 2025-2026 美元方向桶与全参考桶(口径对齐,可复算)。
for lab,lo,hi in [('2017-2024','2017','2024'),('2022-2026','2022','2026'),('2025-2026','2025','2026')]:
    big_up=[(dates[i],r_chg[i],g_ret[i]) for i in range(1,n) if lo<=dates[i][:4]<=hi and r_chg[i] is not None and r_chg[i]>=0.05]
    big_dn=[(dates[i],r_chg[i],g_ret[i]) for i in range(1,n) if lo<=dates[i][:4]<=hi and r_chg[i] is not None and r_chg[i]<=-0.05]
    au=sum(x[2] for x in big_up)/max(len(big_up),1); ad=sum(x[2] for x in big_dn)/max(len(big_dn),1)
    pu=sum(1 for x in big_up if x[2]>0)/max(len(big_up),1)*100
    print(f'{lab}: 实际利率日升>=5bp n={len(big_up)} 黄金日均{au:+.3f}% 上涨占比{pu:.0f}% | 日降>=5bp n={len(big_dn)} 黄金日均{ad:+.3f}%')
for lab,lo,hi in [('2025-2026','2025','2026')]:
    d_up=[g_ret[i] for i in range(1,n) if lo<=dates[i][:4]<=hi and d_ret[i] is not None and d_ret[i]>0]
    d_dn=[g_ret[i] for i in range(1,n) if lo<=dates[i][:4]<=hi and d_ret[i] is not None and d_ret[i]<0]
    print(f'{lab} 美元方向桶: 美元上行日 n={len(d_up)} 黄金日均{sum(d_up)/max(len(d_up),1):+.3f}% | 美元下行日 n={len(d_dn)} 黄金日均{sum(d_dn)/max(len(d_dn),1):+.3f}%')

# HY_OAS 信用利差分状态(2024-2026 样本, 784 天自2023-11)
HY = dict(zip(macro['HY_OAS']['series']['dates'], macro['HY_OAS']['series']['values']))
common2 = sorted(set(GOLD)&set(REAL)&set(HY))
g2=[(GOLD[d]/GOLD[common2[i-1]]-1)*100 for i,d in enumerate(common2) if i>0]
r2=[REAL[d]-REAL[common2[i-1]] for i,d in enumerate(common2) if i>0]
h2=[HY[d]-HY[common2[i-1]] for i,d in enumerate(common2) if i>0]
# Audit-R2 条目3(NEW-2 修): DXY 日变化须与 g2/r2/h2 同一前日锚
# common2[i-1] 构造——旧实现 dts2[i-1] 在 i=0 取到末日(环绕伪值,
# 首观测的 DXY 日收益=末日→次日的错向变化,收窄桶 -0.361 实为 -0.382)
x2=[(DXY[d]/DXY[common2[i-1]]-1)*100 for i,d in enumerate(common2) if i>0]
dts2=common2[1:]
# Audit-R2 条目3(分组定义统一): 走阔(Δ>0)/收窄(Δ<0)/不变(Δ=0)三组
# 严格分立——旧实现「收窄日」用 Δ<=0 把不变日混入收窄桶,标签与样本
# 定义不符;不变日单独披露,相关统计只算严格组
stress=[i for i in range(len(dts2)) if h2[i]>0]      # 利差走阔日=信用压力
calm=[i for i in range(len(dts2)) if h2[i]<0]        # 严格收窄日
flat=[i for i in range(len(dts2)) if h2[i]==0]       # 不变日(单列,不入桶)
print(f'\n=== 信用利差分状态({dts2[0]}..{dts2[-1]}, HY_OAS 走阔/收窄/不变三组严格分立) ===')
rS,_=pearson([r2[i] for i in stress],[g2[i] for i in stress])
rC,_=pearson([r2[i] for i in calm],[g2[i] for i in calm])
rD,_=pearson([x2[i] for i in stress],[g2[i] for i in stress])
rDc,_=pearson([x2[i] for i in calm],[g2[i] for i in calm])
print(f'走阔日 n={len(stress)}: GOLD~REAL {rS:+.3f} GOLD~DXY {rD:+.3f} | 收窄日 n={len(calm)}: GOLD~REAL {rC:+.3f} GOLD~DXY {rDc:+.3f} | 不变日 n={len(flat)}(不入相关桶)')
if flat:
    rF,_=pearson([r2[i] for i in flat],[g2[i] for i in flat])
    rDf,_=pearson([x2[i] for i in flat],[g2[i] for i in flat])
    print(f'不变日参考(披露,不计入走阔/收窄对比): GOLD~REAL {rF:+.3f} GOLD~DXY {rDf:+.3f}')
