#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter6-P4 测试 — analog 历史相似结构检索引擎 + ia_cli 接线(Afin §1)

覆盖(协调方 Round4 块4规格 + Afin §6 红线"独立重算对照引擎"):
  一、expanding z 逐值手算(1..40 序列,μ/σ/边界月手算;禁用被测函数自证);
  二、加权 z 距离手算(双特征/重归一两例);
  三、月网格聚合(last/mean4/quarter/rv21 各自独立公式复算);
  四、泄漏防护: μ/σ 只用 ≤锚点(未来观测改值→z 不变);事后窗不回吸
     锚点月;候选与锚点窗重叠排除;排序与事后严格分离。
  五、拒答路径: 短历史→insufficient_history(现状数据必然拒答=正确行为);
     候选<8→insufficient_candidates(不放宽阈值硬凑);bad_weights;
     anchor_not_complete。
  六、全管线独立重算: 60月合成序列,测试自写 expanding z+距离复算 TOP-1,
     与引擎输出逐值对照(不经被测函数)。
  七、事后演变手算(价格 pct/利率 pp/起点严格>月末/unavailable 如实);
  八、巧合判据(单维主导/事后分歧/维度缺席/TOP-1不分离)+固定披露文案
     逐字断言;估值维度缺席如实,别名序列(other族)零进入。
  九、ia_cli cmd_analog: 信封/参数校验 rc=2/拒答 rc=1/--no-aftermath。

数据纪律: 全部 fixture=SYNTHETIC 内存序列;零网络零真实数据目录。
运行: ~/AI内容/venv/bin/python3 tests/test_charter6_p4_analog.py
"""
import io
import json
import math
import os
import sys
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


def months(start, n):
    """['2021-01', ...] n 个月(独立于引擎的月算术)。"""
    y, m = int(start[:4]), int(start[5:7])
    out = []
    for k in range(n):
        idx = y * 12 + (m - 1) + k
        out.append('%04d-%02d' % (idx // 12, idx % 12 + 1))
    return out


def mkey_add(mk, k):
    y, m = int(mk[:4]), int(mk[5:7])
    idx = y * 12 + (m - 1) + k
    return '%04d-%02d' % (idx // 12, idx % 12 + 1)


print("=" * 64)
print("Charter6-P4: analog 引擎(六维状态向量+expanding z+加权z距离)")
print("=" * 64)

import analog_engine as ae  # noqa: E402

# ══ [1] expanding z 手算 ═══════════════════════════════════════════
print("\n[1] z_at 逐值手算(1..40 序列)")
MK = months('2021-01', 40)
g = {mk: float(i + 1) for i, mk in enumerate(MK)}     # 值=1..40
# 手算(独立): idx39 → n=40, μ=20.5, Σ(i−μ)²=n(n²−1)/12=5330, σ=√133.25
mu40, sig40 = 20.5, math.sqrt(5330.0 / 40.0)
z_hand = (40.0 - mu40) / sig40
z_eng, n_eng = ae.z_at(g, MK[39])
check("idx39: z=手算值(μ=20.5,σ=√133.25)",
      abs(z_eng - z_hand) < 1e-12 and n_eng == 40,
      f"{z_eng} vs {z_hand} n={n_eng}")
# idx34(n=34<36)→弃用;idx35(n=36)→恰好门槛(手算 μ=18.5,Σ=36·(36²−1)/12)
check("idx34(n=34<36)→None(不降门槛)", ae.z_at(g, MK[34])[0] is None)
mu36, sig36 = 18.5, math.sqrt(36.0 * (36.0 ** 2 - 1) / 12.0 / 36.0)
z36 = (36.0 - mu36) / sig36
z35_eng, n35 = ae.z_at(g, MK[35])
check("idx35(n=36)→恰好门槛可算(手算μ=18.5)",
      abs(z35_eng - z36) < 1e-12 and n35 == 36, f"{z35_eng} vs {z36}")
check("σ=0(常数列)→None(无信息弃用)",
      ae.z_at({mk: 5.0 for mk in MK}, MK[39])[0] is None)
# 泄漏规则1: 未来观测(idx36..39)改值→早期 z 不变
g2 = dict(g)
for i in (36, 37, 38, 39):
    g2[MK[i]] = 999.0
z_before, _ = ae.z_at(g, MK[35])
z_after, _ = ae.z_at(g2, MK[35])
check("泄漏规则1: 未来观测改值→当期 z 不变(expanding)",
      abs(z_before - z_after) < 1e-15)

# ══ [2] 加权 z 距离手算 ═══════════════════════════════════════════
print("\n[2] weighted_distance 手算")
D, wsum, terms = ae.weighted_distance({'f1': 1.0, 'f2': -1.0},
                                      {'f1': 0.5, 'f2': 0.0},
                                      {'f1': 0.6, 'f2': 0.4})
check("双特征: D=√(0.6·0.25+0.4·1)=√0.55(手算)",
      wsum == 1.0 and abs(D - math.sqrt(0.55)) < 1e-12, str(D))
D2, wsum2, _ = ae.weighted_distance({'f1': 1.0, 'f2': -1.0},
                                    {'f1': 0.5},          # f2 候选缺→重归一
                                    {'f1': 0.9, 'f2': 0.1})
check("重归一: 共同仅f1→w=0.9/0.9=1,D=|gap|=0.5(手算)",
      abs(wsum2 - 0.9) < 1e-15 and abs(D2 - 0.5) < 1e-12, str(D2))
D3, _, _ = ae.weighted_distance({'f1': 1.0}, {'f2': 2.0}, {'f1': 1.0})
check("无共同特征→D=None(不造距离)", D3 is None)

# ══ [3] 月网格聚合 ════════════════════════════════════════════════
print("\n[3] month_grid/_rv21_grid 聚合口径")
gl = ae.month_grid(['2024-01-05', '2024-01-20', '2024-02-03'],
                   [1.0, 2.0, 3.0], 'last')
check("last=月内末值", gl == {'2024-01': 2.0, '2024-02': 3.0}, str(gl))
gw = ae.month_grid(['2024-01-06', '2024-01-13', '2024-01-20', '2024-01-27',
                    '2024-02-03'], [1.0, 2.0, 3.0, 4.0, 5.0], 'mean4')
check("mean4=≤月末最后4个周观测均值(1月=mean(1,2,3,4)=2.5;2月=mean(2,3,4,5)=3.5)",
      gw == {'2024-01': 2.5, '2024-02': 3.5}, str(gw))
gw2 = ae.month_grid(['2024-01-06', '2024-01-13', '2024-02-03'],
                    [1.0, 2.0, 3.0], 'mean4')
check("mean4 不足4周观测→该月无值(不冒充)",
      '2024-01' not in gw2 and '2024-02' not in gw2, str(gw2))
gq = ae.month_grid(['2024-01-15', '2024-02-20', '2024-04-10'],
                   [1.0, 2.0, 3.0], 'quarter')
check("quarter=季末月对齐(季内末值)", gq == {'2024-03': 2.0, '2024-06': 3.0},
      str(gq))
# rv21: 22 个日观测(21 个对数收益),独立复算
vals = [100.0 * (1.01 ** (i if i % 2 == 0 else -i)) for i in range(22)]
dts = ['2024-03-%02d' % (i + 1) for i in range(22)]
rv = ae._rv21_grid(dts, vals)
rets = [math.log(vals[i] / vals[i - 1]) for i in range(1, 22)]
mu = sum(rets) / len(rets)
var = sum((r - mu) ** 2 for r in rets) / len(rets)
rv_hand = math.sqrt(var) * math.sqrt(252.0)
check("rv21=21个对数收益σ×√252(独立复算)",
      abs(rv['2024-03'] - rv_hand) < 1e-9, f"{rv.get('2024-03')} vs {rv_hand}")
short = ae._rv21_grid(['2024-03-%02d' % (i + 1) for i in range(10)],
                      [100.0 + i for i in range(10)])
check("rv21 不足22观测→月无值(不缩窗冒充)", short == {})

# ══ [4] 特征变换 ══════════════════════════════════════════════════
print("\n[4] feature_grids 变换(yoy/d12m/chg_3m/diff)")
MK6 = months('2023-01', 18)
cpi = {'dates': [mk + '-01' for mk in MK6],
       'values': [100.0 * (1.05 ** (i / 12.0)) for i in range(18)]}
fg = ae.feature_grids({'CPI': cpi}, {})
yoy_hand = (cpi['values'][17] / cpi['values'][5] - 1) * 100.0
check("CPI_yoy=(v_t/v_{t−12}−1)×100(手算末月)",
      abs(fg['CPI_yoy'][MK6[17]] - yoy_hand) < 1e-9,
      f"{fg['CPI_yoy'][MK6[17]]} vs {yoy_hand}")
check("CPI_yoy 前12个月无值(不足整年不缩短窗口)",
      all(mk not in fg['CPI_yoy'] for mk in MK6[:12]))
ff = {'dates': [mk + '-01' for mk in MK6[12:]],
      'values': [4.0 + 0.1 * i for i in range(6)]}
fg2 = ae.feature_grids({'FED_FUNDS': dict(dates=[mk + '-01' for mk in MK6],
                                          values=[4.0 + 0.1 * i
                                                  for i in range(18)])}, {})
d12 = (4.0 + 0.1 * 17) - (4.0 + 0.1 * 5)
check("d12m=v_t−v_{t−12}(pp,手算)",
      abs(fg2['FED_FUNDS_d12m'][MK6[17]] - d12) < 1e-12)
nfp = {'dates': [mk + '-01' for mk in MK6],
       'values': [150.0 + 10.0 * i for i in range(18)]}
fg3 = ae.feature_grids({'NFP': nfp}, {})
# 手算: 最近3个月差 = (320−310, 310−300, 300−290) 均值 = 10
check("NFP_3m_chg=最近3个月差均值(手算=10)",
      abs(fg3['NFP_3m_chg'][MK6[17]] - 10.0) < 1e-9,
      str(fg3['NFP_3m_chg'][MK6[17]]))
hy = {'dates': [mk + '-01' for mk in MK6],
      'values': [5.0 + 0.05 * i for i in range(18)]}
ig = {'dates': [mk + '-01' for mk in MK6],
      'values': [1.0 + 0.02 * i for i in range(18)]}
fg4 = ae.feature_grids({'HY_OAS': hy, 'IG_OAS': ig}, {})
gap0 = (5.0 + 0.05 * 5) - (1.0 + 0.02 * 5)
gap1 = (5.0 + 0.05 * 17) - (1.0 + 0.02 * 17)
check("HY_IG_gap=HY−IG 月末差(手算)",
      abs(fg4['HY_IG_gap_level'][MK6[17]] - gap1) < 1e-12)
check("HY_IG_gap_d12m=差值12个月变化(手算)",
      abs(fg4['HY_IG_gap_d12m'][MK6[17]] - (gap1 - gap0)) < 1e-12)

# ══ [5] 拒答路径 ══════════════════════════════════════════════════
print("\n[5] 拒答路径(阈值不放宽)")


def synth(n, mods=None):
    """n 个月合成序列族(四到五维,趋势微变;mods 可覆盖指标生成)。"""
    mk = months('2025-01', n) if n <= 22 else months('2020-01', n)
    base = {
        'UNEMPLOYMENT': [5.0 + 0.01 * i for i in range(n)],
        'CPI': [300.0 * (1.02 ** (i / 12.0)) for i in range(n)],
        'BEI_10Y': [2.0 + 0.001 * i for i in range(n)],
        'FED_FUNDS': [4.0 + 0.02 * i for i in range(n)],
        'UST_10Y': [4.2 + 0.015 * i for i in range(n)],
        'VIX': [15.0 + 0.05 * i for i in range(n)],
    }
    if mods:
        base.update(mods)
    return {k: {'dates': [m + '-01' for m in mk], 'values': v}
            for k, v in base.items()}


REG = json.load(open(os.path.join(ROOT, 'config', 'metric_registry.json'),
                     encoding='utf-8'))
import fact_engine as fe  # noqa: E402
REG_LOADED = fe.load_registry()

r22 = ae.run(synth(22), REG_LOADED)
check("短历史(22月)→拒答 insufficient_history(现状必然拒答=正确行为)",
      r22['ok'] is False and r22['error'][0] == 'insufficient_history',
      str(r22['error']))
r48 = ae.run(synth(48), REG_LOADED)
check("48月(候选仅1个<8)→拒答 insufficient_candidates",
      r48['ok'] is False and r48['error'][0] == 'insufficient_candidates',
      str(r48['error']))
rbw = ae.run(synth(60), REG_LOADED, weights={'growth': 0.5, 'inflation': 0.1,
                                             'rates': 0.1, 'credit': 0.1,
                                             'volatility': 0.1,
                                             'valuation': 0.05})
check("权重和≠1→bad_weights", rbw['error'][0] == 'bad_weights')
ranc = ae.run(synth(60), REG_LOADED, anchor='2019-12')
check("锚点月无数据→anchor_not_complete",
      ranc['ok'] is False and ranc['error'][0] == 'anchor_not_complete')
ranc2 = ae.run(synth(60), REG_LOADED, anchor='2019-13')
check("锚点格式非法→bad_anchor", ranc2['error'][0] == 'bad_anchor')

# ══ [6] 全管线独立重算(60月) ══════════════════════════════════════
print("\n[6] 全管线: 独立重算 TOP-1 对照(不经被测函数)")
N = 60
MK60 = months('2020-01', N)
sm = {
    'UNEMPLOYMENT': [5.0 + 0.01 * i for i in range(N)],
    'CPI': [300.0 * (1.02 ** (i / 12.0)) for i in range(N)],
    'BEI_10Y': [2.0 + 0.001 * i for i in range(N)],
    'FED_FUNDS': [4.0 + 0.02 * i for i in range(N)],
    'UST_10Y': [4.2 + 0.015 * i for i in range(N)],
    'HY_OAS': [5.0 + 0.01 * i for i in range(N)],
    'IG_OAS': [1.0 + 0.005 * i for i in range(N)],
    'VIX': [15.0 + 0.05 * i for i in range(N)],
}
smap = {k: {'dates': [mk + '-15' for mk in MK60], 'values': v}
        for k, v in sm.items()}
# 事后资产(稀疏日频,独立于特征面;SPX 稀疏→rv21 无值,波动维=VIX 单特征)
spx_obs = {'2022-12-15': 1000.0, '2023-01-28': 1155.0, '2023-03-31': 1210.0,
           '2023-06-30': 1331.0, '2023-12-31': 1464.1}
ust_obs = {'2023-01-05': 4.0, '2023-03-31': 4.25, '2023-06-30': 4.5,
           '2023-12-31': 4.75}
smap['SPX'] = {'dates': sorted(spx_obs), 'values': [spx_obs[d]
                                                    for d in sorted(spx_obs)]}
smap['UST_10Y'] = {
    'dates': sorted(set(ust_obs) | {mk + '-15' for mk in MK60}),
    'values': None}      # 占位,下面按日期重排
_u = {}
for mk, v in zip(MK60, sm['UST_10Y']):
    _u[mk + '-15'] = v
_u.update(ust_obs)
_uk = sorted(_u)
smap['UST_10Y'] = {'dates': _uk, 'values': [_u[d] for d in _uk]}
smap['DXY'] = {'dates': sorted(spx_obs), 'values': [100.0, 101.0, 102.0,
                                                    103.0, 104.0]}
smap['GOLD_F'] = {'dates': sorted(spx_obs), 'values': [2000.0, 2200.0,
                                                       2400.0, 2600.0, 2800.0]}

res = ae.run(smap, REG_LOADED)
check("60月→正常输出(ok=True)", res['ok'] is True, str(res.get('error')))
d = res['data']
check("锚点=最新完整月 2024-12", d['anchor_month'] == '2024-12',
      d['anchor_month'])
check("候选计数: scanned=60/valid=13/overlap=12/insufficient=35",
      d['candidates'] == {'scanned': 60, 'valid': 13, 'dropped_overlap': 12,
                          'dropped_insufficient': 35},
      str(d['candidates']))
check("13<24→样本不稳警示", any('<24' in w for w in res['warnings']),
      str(res['warnings']))

# ── 独立重算(测试自写 expanding z+等权距离;零调用引擎内部) ──
def build_feats(mp, mk_list):
    """按 Afin §1.1 变换在测试侧独立构造特征月值。"""
    def last_grid(mid):
        gmap = {}
        for dt, v in zip(mp[mid]['dates'], mp[mid]['values']):
            gmap[str(dt)[:7]] = v          # 输入已升序→月内末值
        return gmap
    u, c, b, ff, u10, hy, ig, vx = (
        last_grid('UNEMPLOYMENT'), last_grid('CPI'), last_grid('BEI_10Y'),
        last_grid('FED_FUNDS'), last_grid('UST_10Y'), last_grid('HY_OAS'),
        last_grid('IG_OAS'), last_grid('VIX'))
    feats = {}
    feats['UNEMPLOYMENT_level'] = u
    feats['BEI_10Y_level'] = b
    feats['VIX_level'] = vx
    feats['FED_FUNDS_level'] = ff
    feats['UST_10Y_level'] = u10
    for nm, gg in (('CPI_yoy', c), ('FED_FUNDS_d12m', ff),
                   ('UST_10Y_d12m', u10)):
        feats[nm] = {mk: (gg[mk] / gg[mkey_add(mk, -12)] - 1) * 100.0
                     if nm == 'CPI_yoy' and mk in gg
                     and mkey_add(mk, -12) in gg
                     and gg[mkey_add(mk, -12)] != 0
                     else (gg[mk] - gg[mkey_add(mk, -12)]
                           if mk in gg and mkey_add(mk, -12) in gg else None)
                     for mk in mk_list}
        feats[nm] = {k: v for k, v in feats[nm].items() if v is not None}
    gap = {mk: hy[mk] - ig[mk] for mk in hy if mk in ig}
    feats['HY_IG_gap_level'] = gap
    feats['HY_IG_gap_d12m'] = {mk: gap[mk] - gap[mkey_add(mk, -12)]
                               for mk in gap
                               if mkey_add(mk, -12) in gap}
    feats['HY_OAS_level'] = hy
    # D1(收尾): 独立管线补 HY_OAS_d12m——引擎 credit 第4特征;其 d12m 网格
    # 起 2021-01,z 需36月→唯一 z 可算候选=2023-12,此前测试侧缺席导致该
    # 候选的距离(引擎 0.934889)游离于交叉验证之外
    feats['HY_OAS_d12m'] = {mk: hy[mk] - hy[mkey_add(mk, -12)]
                            for mk in hy if mkey_add(mk, -12) in hy}
    return feats


FEATS = build_feats(smap, MK60)
FEAT_DIM = {k: dim for k, dim, _m, _t in ae.FEATURE_SPECS}


def ind_z(fkey, mkey):
    h = sorted(m for m in FEATS[fkey] if m <= mkey)
    if len(h) < 36:
        return None
    vs = [FEATS[fkey][m] for m in h]
    mu0 = sum(vs) / len(vs)
    var0 = sum((x - mu0) ** 2 for x in vs) / len(vs)
    if var0 <= 0:
        return None
    return (FEATS[fkey][mkey] - mu0) / math.sqrt(var0)


VALID_FEATS = [k for k in FEATS if k in
               {kk for kk, _dd, _m, _t in ae.FEATURE_SPECS}]
zs_anchor_ind = {k: ind_z(k, '2024-12') for k in VALID_FEATS}
zs_anchor_ind = {k: v for k, v in zs_anchor_ind.items() if v is not None}
cands_ind = []
cutoff = mkey_add('2024-12', -12)
for mk in MK60:
    if mk > cutoff:
        continue
    zs = {k: ind_z(k, mk) for k in VALID_FEATS}
    zs = {k: v for k, v in zs.items() if v is not None}
    if len({FEAT_DIM[k] for k in zs}) >= 4:
        cands_ind.append((mk, zs))
D_ind = []
IND_W = {}      # month → (原始权重和 ws, {特征: 归一后实际权重})——D3 独立对照
for mk, zs in cands_ind:
    common = [k for k in zs if k in zs_anchor_ind]
    wdim = {dm: 1.0 / 6.0 for dm in ('growth', 'inflation', 'rates', 'credit',
                                     'volatility', 'valuation')}   # 六维等权
    # 特征权分母=规格表该维全定义特征数(§1.1, 与数据在场无关;缺席由
    # 距离层重归一吸收)——独立复算与引擎同一登记规则
    nspec = {}
    for _k, _d, _m, _t in ae.FEATURE_SPECS:
        nspec[_d] = nspec.get(_d, 0) + 1
    fw = {k: wdim[FEAT_DIM[k]] / nspec[FEAT_DIM[k]] for k in common}
    ws = sum(fw.values())
    dd = math.sqrt(sum((fw[k] / ws) * (zs_anchor_ind[k] - zs[k]) ** 2
                       for k in common))
    D_ind.append((mk, dd))
    IND_W[mk] = (ws, {k: fw[k] / ws for k in common})
D_ind.sort(key=lambda x: (x[1], x[0]))
top1 = d['top'][0]
check("TOP-1 候选月=独立重算(手写复算管线)",
      top1['candidate_month'] == D_ind[0][0],
      f"engine={top1['candidate_month']} ind={D_ind[0][0]}")
check("TOP-1 距离=独立重算(1e-6,引擎输出6dp舍入)",
      abs(top1['distance'] - D_ind[0][1]) < 1e-6,
      f"engine={top1['distance']} ind={D_ind[0][1]}")
check("TOP-5 全序=独立重算",
      [t['candidate_month'] for t in d['top']]
      == [m for m, _ in D_ind[:5]],
      str([t['candidate_month'] for t in d['top']]))
check("重叠排除: 全部候选≤锚点−12月(2023-12)",
      all(t['candidate_month'] <= '2023-12' for t in d['top']))
check("TOP-1 距离分位=0.0(最小距离)",
      top1['distance_percentile'] == 0.0)
check("features_detail 逐特征锚点/候选 z+归一权重随行",
      all({'anchor_z', 'cand_z', 'gap', 'w_norm'} == set(v)
          for t in d['top'] for v in t['features_detail'].values()))
# D3/D4(收尾): 归一事实随行——norm_wsum(共有特征原始权重和)+逐特征
# w_norm(归一后实际权重)与测试侧独立构造的权重规则逐值对照
ws1, wn1 = IND_W[top1['candidate_month']]
check("TOP-1 norm_wsum=独立重算原始权重和(6dp)",
      top1['norm_wsum'] == round(ws1, 6),
      f"{top1['norm_wsum']} vs {round(ws1, 6)}")
check("TOP-1 逐特征 w_norm=独立重算(归一后,6dp)",
      all(v['w_norm'] == round(wn1[k], 6)
          for k, v in top1['features_detail'].items()),
      str(top1['features_detail']))
check("TOP-1 逐特征 w_norm 和=1(归一事实自洽)",
      abs(sum(v['w_norm'] for v in top1['features_detail'].values()) - 1.0)
      < 2e-5)
# dims contribution_share 和=1(数值和)
cs = sum(v['contribution_share'] for v in top1['dims'].values())
check("维度贡献份额和=1(6dp舍入容差)", abs(cs - 1.0) < 5e-6, str(cs))

# ══ [7] 事后演变(手算) ════════════════════════════════════════════
print("\n[7] aftermath 手算(候选 2022-12,起点严格>月末)")
# anchor=2023-12 回放: 候选仅 2022-12 一个(<8)→正确拒答(阈值不放宽)
res_replay = ae.run(smap, REG_LOADED, anchor='2023-12')
check("anchor=2023-12 回放: 候选仅1个<8→拒答(宁缺毋滥)",
      res_replay['ok'] is False
      and res_replay['error'][0] == 'insufficient_candidates')
# 默认锚点(2024-12)候选含 2022-12,取 top=13 拿到该块
res_a = ae.run(smap, REG_LOADED, top=13)
check("默认锚点 top=13: 候选含 2022-12(1年重叠排除窗)",
      res_a['ok'] is True
      and any(t['candidate_month'] == '2022-12' for t in res_a['data']['top']))
top_a = {t['candidate_month']: t for t in res_a['data']['top']}
# D1(收尾): 候选 2023-12 距离进入交叉验证——独立管线补 HY_OAS_d12m 后,
# 该候选(唯一 d12m z 可算者)的共同特征=12,距离与引擎逐值对照;0.934889
# 为审查 D1 记录的引擎现值(双管线一致才放行)
t2312 = top_a['2023-12']
d2312_ind = dict(D_ind)['2023-12']
check("D1: 候选2023-12 距离=独立重算(补 HY_OAS_d12m 后)",
      abs(t2312['distance'] - d2312_ind) < 1e-6
      and t2312['distance'] == 0.934889,
      f"engine={t2312['distance']} ind={d2312_ind}")
check("D1: 2023-12 共同特征恰含 HY_OAS_d12m(12特征)",
      'HY_OAS_d12m' in t2312['features_detail']
      and len(t2312['features_detail']) == 12,
      str(sorted(t2312['features_detail'])))
ws2312 = IND_W['2023-12'][0]
check("D1: 2023-12 norm_wsum=12特征原始权重和(≠TOP-1,归一差异随行)",
      t2312['norm_wsum'] == round(ws2312, 6)
      and t2312['norm_wsum'] != top1['norm_wsum'],
      f"{t2312['norm_wsum']} vs {round(ws2312, 6)}")
# HY_OAS_d12m 归一权重手算: 维权1/6 ÷ credit 规格数4 = 1/24,再除以
# 该候选12特征原始权重和
check("D1: HY_OAS_d12m w_norm=手算((1/6/4)/ws12)",
      t2312['features_detail']['HY_OAS_d12m']['w_norm']
      == round((1.0 / 24.0) / ws2312, 6),
      str(t2312['features_detail']['HY_OAS_d12m']))
t122 = top_a['2022-12']
af = t122['aftermath']
check("aftermath 标签逐字(事后非预测,不参与相似度)",
      af['label'] == '事后(候选锚点后 1/3/6/12 月, 非预测, 不参与相似度)')
# 手算: SPX 起点=2023-01-28(严格>2022-12-31 首观测)=1155;
# 1m 窗(≤2023-01-31)内无起点之后的新观测→unavailable(不以0%冒充"无变动");
# 3m=1210→+4.76%;6m=1331→+15.28%;12m=1464.1→+26.76%
sp = af['SPX']
check("SPX 1m=unavailable(窗内无起点后新观测,不以0%冒充)",
      sp['1m'] is None
      and '1m' in af['unavailable_horizons']['SPX'], str(sp))
check("SPX 3m=(1210/1155−1)×100(手算)",
      abs(sp['3m'] - (1210.0 / 1155.0 - 1) * 100) < 1e-6, str(sp['3m']))
check("SPX 6m=(1331/1155−1)×100(手算)",
      abs(sp['6m'] - (1331.0 / 1155.0 - 1) * 100) < 1e-6, str(sp['6m']))
check("SPX 12m=(1464.1/1155−1)×100(手算)",
      abs(sp['12m'] - (1464.1 / 1155.0 - 1) * 100) < 1e-6, str(sp['12m']))
# UST_10Y 起点=2023-01-05(4.0);1m 末观测=2023-01-15(4.74)→+0.74pp;
# 3m=4.25→+0.25;6m=4.5→+0.5;12m=4.75→+0.75(手算)
u10af = af['UST_10Y']
check("UST_10Y 利率类=pp(手算 1m=+0.74,3m=+0.25,12m=+0.75)",
      abs(u10af['1m'] - 0.74) < 1e-9 and abs(u10af['3m'] - 0.25) < 1e-9
      and abs(u10af['12m'] - 0.75) < 1e-9, str(u10af))
check("起点不回吸锚点月内数据(2022-12-15=1000 未入窗)",
      abs(sp['3m'] - (1210.0 / 1000.0 - 1) * 100) > 1e-6)
# 事后窗观测不足→该 horizon 如实 unavailable(禁止缩短窗/0值冒充):
# 候选 2023-02 的 SPX 3m 窗(2023-02-28,2023-05-31]内无观测(次obs=2023-06-30)
b2302 = top_a['2023-02']['aftermath']
check("候选2023-02 SPX 3m=unavailable(窗内无观测,不以缩短窗冒充)",
      b2302['SPX']['3m'] is None
      and '3m' in b2302['unavailable_horizons']['SPX'],
      str(b2302['SPX']))
check("候选2023-02 SPX 6m 窗含 2023-06-30 观测→可用",
      b2302['SPX']['6m'] is not None)
# 全 TOP 块 horizon 一致性(按资产各自): 值非None⇔该资产清单不含该horizon
# unavailable_horizons 为按资产字典(资产A缺观测不得记到资产B头上)
check("全候选 aftermath horizon 与 unavailable 清单自洽(按资产)",
      all((t['aftermath'][a][h] is None)
          == (h in t['aftermath']['unavailable_horizons'][a])
          for t in res_a['data']['top']
          for a in ae.AFTERMATH_ASSETS
          for h in ae.AFTERMATH_HORIZONS))
# 排序与事后严格分离: 关闭 aftermath 排序不变
res_no = ae.run(smap, REG_LOADED, include_aftermath=False)
check("--no-aftermath: 排序不变(泄漏规则4)",
      [t['candidate_month'] for t in res_no['data']['top']]
      == [t['candidate_month'] for t in res['data']['top']]
      and res_no['data']['top'][0]['aftermath'] is None)

# ══ [8] 泄漏/巧合判据/披露/别名隔离 ═══════════════════════════════
print("\n[8] 泄漏规则·巧合判据·固定文案·别名零进入")
# 规则2: 锚点后新增观测→锚点 z 与排序不变(固定 anchor)
smap_ext = {k: dict(v) for k, v in smap.items()}
ext_mk = months('2025-01', 3)
for k in ('UNEMPLOYMENT', 'CPI', 'BEI_10Y', 'FED_FUNDS', 'UST_10Y',
          'HY_OAS', 'IG_OAS', 'VIX'):
    smap_ext[k]['dates'] = list(smap[k]['dates']) + [m + '-15'
                                                     for m in ext_mk]
    smap_ext[k]['values'] = list(smap[k]['values']) + [9999.0] * 3
res_ext = ae.run(smap_ext, REG_LOADED, anchor='2024-12')
check("泄漏规则2: 锚点后数据突变→固定锚点下 TOP-5 排序不变",
      [t['candidate_month'] for t in res_ext['data']['top']]
      == [t['candidate_month'] for t in res['data']['top']])
check("泄漏规则2: 锚点 z 不受锚点后观测影响",
      res_ext['data']['state_vector'] == res['data']['state_vector'])
# 巧合判据: 单维主导(候选与锚点仅一维差异大)
mk60 = MK60
sm_dom = {
    'UNEMPLOYMENT': [5.0 + 0.01 * i for i in range(N)],
    'CPI': [300.0 * (1.02 ** (i / 12.0)) for i in range(N)],
    'BEI_10Y': [2.0] * N,
    'FED_FUNDS': [4.0] * N,
    'UST_10Y': [4.2] * N,
    'VIX': [15.0] * N,
}
# 常数列 σ=0→特征弃用;仅 3 特征(U/CPI_yoy... CPI_yoy 有趋势)→ 维度不足
# 改用: 除 UNEMPLOYMENT 外全部近常数微噪,锚点月 UNEMPLOYMENT 大跳
sm_dom['UNEMPLOYMENT'] = [5.0 + 0.01 * i for i in range(N - 1)] + [9.0]
sm_dom['VIX'] = [15.0 + (0.001 if i % 2 else -0.001) for i in range(N)]
sm_dom['BEI_10Y'] = [2.0 + (0.0001 if i % 2 else -0.0001) for i in range(N)]
sm_dom['FED_FUNDS'] = [4.0 + (0.0001 if i % 2 else -0.0001) for i in range(N)]
sm_dom['UST_10Y'] = [4.2 + (0.0001 if i % 2 else -0.0001) for i in range(N)]
sdmap = {k: {'dates': [m + '-15' for m in mk60], 'values': v}
         for k, v in sm_dom.items()}
res_dom = ae.run(sdmap, REG_LOADED)
check("巧合判据1: 单维主导 flag(引擎机械触发)",
      any('单一维度主导' in w for w in res_dom['warnings']),
      str(res_dom['warnings'][:4]))
check("巧合判据3: 维度缺席(估值)恒挂缺变量警示",
      any('未覆盖维度' in w for w in res['warnings']))
check("估值维度缺席如实标注(不以价格涨幅冒充)",
      res['data']['state_vector']['valuation']['coverage'] == 0.0
      and res['data']['state_vector']['valuation']['note']
      == '无估值数据, 维度缺席(如实)',
      str(res['data']['state_vector']['valuation']))

# D2(收尾)判据2: 事后方向一致率<0.6(n≥3)→分歧警示。GOLD_F 换密布月频
# 周期4模式[1,2,4,1](gold 不进特征面,只影响事后块);测试侧独立镜像
# 事后窗定义(起点=严格>候选月末首观测;3m 窗末=m+3 月末)复算 13 候选方向
smap_c2 = {k: dict(v) for k, v in smap.items()}
gk = months('2022-12', 25)                    # 2022-12..2024-12 每月15日
gvals = [[1.0, 2.0, 4.0, 1.0][i % 4] for i in range(25)]
smap_c2['GOLD_F'] = {'dates': [m + '-15' for m in gk], 'values': gvals}
res_c2 = ae.run(smap_c2, REG_LOADED, top=13)
signs = [0 if gvals[i + 3] == gvals[i + 1]
         else (1 if gvals[i + 3] > gvals[i + 1] else -1) for i in range(13)]
npos_c2 = sum(1 for s in signs if s > 0)
agree_c2 = max(npos_c2, len(signs) - npos_c2) / len(signs)
check("D2判据2: 独立复算 3m 方向 7负6正→一致率 7/13",
      signs.count(-1) == 7 and signs.count(1) == 6
      and abs(agree_c2 - 7.0 / 13.0) < 1e-12, str(signs))
check("D2判据2: GOLD_F 3m 分歧警示随行(方向一致率 0.54<0.6)",
      any(('GOLD_F 3m' in w and '分歧' in w and '0.54' in w)
          for w in res_c2['warnings']), str(res_c2['warnings'][:5]))
check("D2判据2: dispersion GOLD_F_3m 一致率=独立复算(7/13)",
      abs(res_c2['data']['dispersion']['topN_aftermath_sign_agreement']
          ['GOLD_F_3m'] - 7.0 / 13.0) < 5e-5,
      str(res_c2['data']['dispersion']['topN_aftermath_sign_agreement']))
check("D2判据2: 负对照——原稀疏序列无事后分歧警示",
      not any('分歧' in w for w in res_a['warnings']))

# D2(收尾)判据4: TOP-1 与中位不分离((med−min)/med<10%)。前向解序列:
# 逐月解 v 使自身扩展窗 z 命中目标剖面(测试侧独立数值解,镜像引擎 z
# 定义: μ/σ=含当期扩展窗,总体σ);候选窗内 z 剖面近平坦(δ·(1+0.0005k)),
# 全部特征=该解的仿射拷贝(z 仿射不变)→各候选距离挤在 <1% 带内→警示;
# 原序列(负对照)sep≈46% 不触发
def _solve_z_series(targets):
    s = [0.0, 1.0]
    for tg in targets[2:]:
        def z_of(v, s=s):
            xs = s + [v]
            n = len(xs)
            mu = sum(xs) / n
            var = sum((x - mu) ** 2 for x in xs) / n
            return float('inf') if var <= 0 else (v - mu) / var ** 0.5
        lo, hi = -1e6, 1e6
        for _ in range(200):
            mid = (lo + hi) / 2.0
            if z_of(mid) < tg:
                lo = mid
            else:
                hi = mid
        s.append((lo + hi) / 2.0)
    return s


C_T, DELTA_C4, SLOPE_C4 = 1.0, 0.5, 0.0005
tgs_c4 = [0.3 + 0.1 * math.sin(0.7 * j) for j in range(35)]
tgs_c4 += [C_T - DELTA_C4 * (1.0 + SLOPE_C4 * (47 - j))
           for j in range(35, 48)]
tgs_c4 += [C_T] * 12
s_flat = _solve_z_series(tgs_c4)


def _z_at_vals(vals, j):
    xs = vals[:j + 1]
    mu = sum(xs) / len(xs)
    var = sum((x - mu) ** 2 for x in xs) / len(xs)
    return (vals[j] - mu) / var ** 0.5


check("D2判据4自证: 解序列 z 剖面逐月命中目标(独立复算,1e-6)",
      all(abs(_z_at_vals(s_flat, j) - tgs_c4[j]) < 1e-6
          for j in range(2, 60)))
_AFF = [('UNEMPLOYMENT', 5.0, 0.3), ('CPI', 300.0, 2.0), ('BEI_10Y', 2.0, 0.05),
        ('FED_FUNDS', 4.0, 0.1), ('UST_10Y', 4.2, 0.1), ('HY_OAS', 5.0, 0.2),
        ('IG_OAS', 1.3, 0.05), ('VIX', 15.0, 0.5),
        ('SPX_CAPE', 30.0, 1.0), ('SPX_PE_TTM', 20.0, 0.7)]
smap_c4 = {mid: {'dates': [mk + '-15' for mk in MK60],
                 'values': [a + b * v for v in s_flat]}
           for mid, a, b in _AFF}
res_c4 = ae.run(smap_c4, REG_LOADED, top=13, include_aftermath=False)
check("D2判据4: 压缩距离 fixture 正常出榜(13候选全可算)",
      res_c4['ok'] is True and len(res_c4['data']['top']) >= 3,
      str(res_c4.get('error')))
check("D2判据4: TOP-1 不分离警示随行",
      any('TOP-1 未与候选分布分离' in w for w in res_c4['warnings']),
      str(res_c4['warnings'][:5]))
d_by_m = {t['candidate_month']: t['distance'] for t in res_c4['data']['top']}
d_hand_c4 = {MK60[j]: abs(C_T - tgs_c4[j]) for j in range(35, 48)}
check("D2判据4: 无扰动候选距离=手算|z_a−z_c|(1e-4;yoy/d12m 扰动仅2023-12)",
      all(abs(d_by_m[mk] - d_hand_c4[mk]) < 1e-4
          for mk in MK60[35:48] if mk != '2023-12'),
      str({mk: (d_by_m.get(mk), round(d_hand_c4[mk], 6))
           for mk in MK60[35:48]}))
_d_sorted = sorted(d_by_m.values())
_sep_c4 = ((_d_sorted[len(_d_sorted) // 2] - _d_sorted[0])
           / _d_sorted[len(_d_sorted) // 2])
check("D2判据4: 手算分离度<10%与警示自洽+负对照(原fixture分离≈46%无警示)",
      _sep_c4 < 0.10
      and not any('TOP-1 未与候选分布分离' in w for w in res['warnings']),
      f"sep={_sep_c4:.4f}")
# 固定披露文案逐字
check("固定披露三条逐字(Afin §1.5)",
      res['data']['disclosure'] == [
          '相似≠因果, 更非预测: TOP-N 是历史状态距离最近的时期, '
          '当时之后的演变只是历史记录',
          '特征为最新修订口径的描述性对齐, 不代表当时市场信息集'
          '(research_mode_gate)',
          '距离分位=该候选在全部有效候选中的相对位置, 不是概率'],
      str(res['data']['disclosure']))
rmg = res['data']['research_mode_gate']
check("research_mode_gate: descriptive=available/event_study=blocked/"
      "realtime=blocked+修订文案",
      rmg['descriptive'] == 'available' and 'blocked' in rmg['event_study']
      and 'blocked' in rmg['realtime_info_set']
      and rmg['note'] == '当时市场所见状态可能与修订后档案值不同',
      str(rmg))
# 别名序列(other族)零进入: 注入畸变别名→输出与不注入逐字节一致
ALIAS = ['BRENT', 'GOLD', 'SILVER', 'WTI', 'CNY=X', 'JPY=X', 'GBPUSD=X']
smap_alias = dict(smap)
for a in ALIAS:
    smap_alias[a] = {'dates': [m + '-15' for m in mk60],
                     'values': [10.0 ** 6 - i for i in range(N)]}
res_alias = ae.run(smap_alias, REG_LOADED)
check("other 族别名序列零进入(输出与无别名逐键一致)",
      json.dumps(res_alias['data'], sort_keys=True)
      == json.dumps(res['data'], sort_keys=True))
sv_keys = {k for dim in res['data']['state_vector'].values()
           for k in dim['features']}
check("状态向量特征面不含任何别名/价格水平类",
      not (set(ALIAS) & sv_keys) and 'SPX_level' not in sv_keys)

# ══ [9] ia_cli cmd_analog ═════════════════════════════════════════
print("\n[9] ia_cli analog 接线")
import ia_cli  # noqa: E402
import workbench_data as wd  # noqa: E402


def run_cli(argv, snap=None, series=None):
    """进程内调用 cmd_analog: monkeypatch load_context/metric_series。"""
    saved_lc, saved_ms = ia_cli.load_context, wd.metric_series
    fake_snap = snap or {
        'snapshot_id': 'research_snapshot_TEST', 'target_date': '20241231',
        'research_as_of': '2024-12-31T08:00:00+08:00',
        'gate_a': {'status': 'DEGRADED'}, 'facts': [],
        'series_store': series if series is not None
        else {k: {'dates': smap[k]['dates'], 'values': smap[k]['values']}
              for k in smap}}
    ia_cli.load_context = lambda: (fake_snap, REG_LOADED, '')
    wd.metric_series = (lambda mid, s=None, root=None, _sm=fake_snap:
                        ({'metric_id': mid, 'label': mid, 'unit': '',
                          'dates': _sm['series_store'][mid]['dates'],
                          'values': _sm['series_store'][mid]['values'],
                          'source': 'store'}, None)
                        if mid in _sm['series_store'] else (None, '无'))
    parser = ia_cli.build_parser()
    args = parser.parse_args(['analog'] + argv)
    buf = io.StringIO()
    code = 0
    try:
        with redirect_stdout(buf):
            ia_cli.cmd_analog(args)
    except SystemExit as e:
        code = e.code or 0
    finally:
        ia_cli.load_context, wd.metric_series = saved_lc, saved_ms
    try:
        return code, json.loads(buf.getvalue())
    except ValueError:
        return code, {'_raw': buf.getvalue()[:200]}


code, out = run_cli([])
check("CLI analog: ok=true+信封(analog/snapshot_id/top)",
      code == 0 and out['ok'] and out['capability'] == 'analog'
      and out['snapshot_id'] == 'research_snapshot_TEST'
      and len(out['data']['top']) == 5, str(out.get('error')))
check("CLI analog: 警示随行(13<24)", any('<24' in w for w in out['warnings']))
code, out2 = run_cli(['--weights', '0.3,0.2,0.2,0.1,0.1,0.05'])
check("CLI bad_weights(和≠1)→rc=2",
      code == 2 and out2['error']['kind'] == 'bad_weights')
code, out3 = run_cli(['--anchor', '2030-01'])
check("CLI 锚点无数据→anchor_not_complete rc=1",
      code == 1 and out3['error']['kind'] == 'anchor_not_complete')
code, out4 = run_cli(['--no-aftermath'])
check("CLI --no-aftermath→top 无事后块",
      code == 0 and all(t['aftermath'] is None
                        for t in out4['data']['top']))
code, out5 = run_cli(['--top', '2'])
check("CLI --top 2(默认锚点): 恰2条+锚点月随行",
      code == 0 and len(out5['data']['top']) == 2
      and out5['data']['anchor_month'] == '2024-12')
code, out5b = run_cli(['--top', '2', '--anchor', '2023-12'])
check("CLI --anchor 2023-12 回放: 候选仅1<8→拒答rc=1(不放宽)",
      code == 1 and out5b['error']['kind'] == 'insufficient_candidates')
code, out6 = run_cli([], snap={'snapshot_id': 'x', 'target_date': '20241231',
                               'facts': [], 'series_store': {},
                               'gate_a': {'status': 'FAIL'}})
check("CLI 序列全缺→insufficient_history rc=1(不造数)",
      code == 1 and out6['error']['kind'] == 'insufficient_history')

print("\n" + "=" * 64)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 64)
sys.exit(0 if FAIL == 0 else 1)
