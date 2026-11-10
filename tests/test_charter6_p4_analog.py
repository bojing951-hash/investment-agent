#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter6-P4 测试 — analog 历史相似结构检索引擎 + ia_cli 接线(Afin §1)
(Charter7 P0 修订 2026-11-10: 统一特征集/跨频率门槛/簇去重/查询时窗门)

覆盖(协调方规格 + Afin §6 红线"独立重算对照引擎"):
  一、expanding z 逐值手算(1..40 序列,μ/σ/边界月手算;禁用被测函数自证)
     + 网格步长折算观测量(Charter7-4b: 月网格36点/季网格12点边界 11/12/13);
  二、加权 z 距离手算: 旧口径(逐候选重归一,仅单元保留)与 Charter7-2 统一
     特征集固定分母 wsum_total=W_U(缺特征不再抬高剩余权重)两例对照;
  三、月网格聚合(last/mean4/quarter/rv21 各自独立公式复算);
  四、特征变换(yoy/d12m/chg_3m/diff)独立复算;
  五、泄漏防护与拒答路径: μ/σ 只用 ≤锚点;短历史→insufficient_history;
     候选<8→insufficient_candidates(不放宽);bad_weights/anchor_not_complete。
  六、全管线独立重算(60月): 测试自写统一特征集+固定分母 W_U+(缺席数,距离)
     双键排序+贪心簇去重(≥12月=异簇),与引擎输出逐值对照(零引擎内部调用);
  七、事后演变手算(价格 pct/利率 pp/起点=次月首日起/unavailable 如实;
     Charter7-3 {资产}_window 逐窗实际起止观测日);
  八、巧合判据(单维主导/独立簇事后分歧/维度缺席/TOP-1不分离——分离度按
     距离值排序)+固定披露文案逐字;估值缺席如实;别名(other族)零进入;
  九、ia_cli cmd_analog: 信封/参数校验 rc=2/拒答 rc=1/--no-aftermath/
     TOP-N 簇去重接线(独立簇<请求N→实际输出+警示)。

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


def mkey_dist(a, b):
    """两月键相差月数(独立算术)。"""
    return (int(a[:4]) * 12 + int(a[5:7])
            - int(b[:4]) * 12 - int(b[5:7]))


print("=" * 64)
print("Charter6-P4+Charter7: analog 引擎(统一特征集+簇去重+月数门槛)")
print("=" * 64)

import analog_engine as ae  # noqa: E402

# ══ [1] expanding z 手算 + 步长折算观测量(Charter7-4b) ═════════════
print("\n[1] z_at 逐值手算(1..40 序列)+月/季网格观测量门槛")
MK = months('2021-01', 40)
g = {mk: float(i + 1) for i, mk in enumerate(MK)}     # 值=1..40
# 手算(独立): idx39 → n=40, μ=20.5, Σ(i−μ)²=n(n²−1)/12=5330, σ=√133.25
mu40, sig40 = 20.5, math.sqrt(5330.0 / 40.0)
z_hand = (40.0 - mu40) / sig40
z_eng, n_eng, req_eng = ae.z_at(g, MK[39])
check("idx39: z=手算值(μ=20.5,σ=√133.25),required=36(月网格)",
      abs(z_eng - z_hand) < 1e-12 and n_eng == 40 and req_eng == 36,
      f"{z_eng} vs {z_hand} n={n_eng} req={req_eng}")
# idx34(n=34<36)→弃用;idx35(n=36)→恰好门槛(手算 μ=18.5)
z34, n34, r34 = ae.z_at(g, MK[34])
check("idx34(n=35<36)→None(不降门槛),required 随行",
      z34 is None and n34 == 35 and r34 == 36, f"{z34} {n34} {r34}")
mu36, sig36 = 18.5, math.sqrt(36.0 * (36.0 ** 2 - 1) / 12.0 / 36.0)
z36 = (36.0 - mu36) / sig36
z35_eng, n35, r35 = ae.z_at(g, MK[35])
check("idx35(n=36)→恰好门槛可算(手算μ=18.5)",
      abs(z35_eng - z36) < 1e-12 and n35 == 36 and r35 == 36,
      f"{z35_eng} vs {z36}")
check("σ=0(常数列)→None(无信息弃用)",
      ae.z_at({mk: 5.0 for mk in MK}, MK[39])[0] is None)
# Charter7-4b: 36 个月史按网格步长折算——季网格 12 点(旧实现隐性 36 季
# =9 年系误设);边界 11/12/13 恰在门槛两侧
check("min_observations: 月网格=36/季网格=12(36个月史折算)",
      ae.min_observations(1) == 36 and ae.min_observations(3) == 12,
      f"{ae.min_observations(1)}/{ae.min_observations(3)}")
QK = ['%d-%02d' % (2018 + (3 + 3 * i) // 12, (3 + 3 * i) % 12 + 1)
      for i in range(13)]                        # 2018-03..2021-03 季末月
gq13 = {mk: float(i + 1) for i, mk in enumerate(QK)}
gq12 = {mk: gq13[mk] for mk in QK[:12]}
gq11 = {mk: gq13[mk] for mk in QK[:11]}
zq12, nq12, rq12 = ae.z_at(gq12, QK[11])
zq11, nq11, rq11 = ae.z_at(gq11, QK[10])
zq13, nq13, rq13 = ae.z_at(gq13, QK[12])
vals12 = [gq12[mk] for mk in QK[:12]]
mu_q = sum(vals12) / 12
sig_q = math.sqrt(sum((v - mu_q) ** 2 for v in vals12) / 12)
zq_hand = (gq12[QK[11]] - mu_q) / sig_q
check("季网格 12 点=恰好门槛(手算 z;required=12)",
      rq12 == 12 and nq12 == 12 and abs(zq12 - zq_hand) < 1e-12,
      f"{zq12} vs {zq_hand} req={rq12}")
check("季网格 11 点→None(不降门槛)/13 点→可算(required 恒12)",
      zq11 is None and nq11 == 11 and rq11 == 12
      and zq13 is not None and nq13 == 13 and rq13 == 12,
      f"11:({zq11},{nq11},{rq11}) 13:({nq13},{rq13})")
# 泄漏规则1: 未来观测(idx36..39)改值→早期 z 不变
g2 = dict(g)
for i in (36, 37, 38, 39):
    g2[MK[i]] = 999.0
z_before = ae.z_at(g, MK[35])[0]
z_after = ae.z_at(g2, MK[35])[0]
check("泄漏规则1: 未来观测改值→当期 z 不变(expanding)",
      abs(z_before - z_after) < 1e-15)

# ══ [2] 加权 z 距离手算(旧口径 vs Charter7-2 固定分母) ═════════════
print("\n[2] weighted_distance 手算(重归一旧口径 vs 固定分母 W_U)")
D, wsum, terms = ae.weighted_distance({'f1': 1.0, 'f2': -1.0},
                                      {'f1': 0.5, 'f2': 0.0},
                                      {'f1': 0.6, 'f2': 0.4})
check("双特征齐备: D=√(0.6·0.25+0.4·1)=√0.55(两口径同值)",
      wsum == 1.0 and abs(D - math.sqrt(0.55)) < 1e-12, str(D))
D2, wsum2, _ = ae.weighted_distance({'f1': 1.0, 'f2': -1.0},
                                    {'f1': 0.5},          # f2 候选缺→重归一
                                    {'f1': 0.9, 'f2': 0.1})
check("旧口径(wsum_total=None): 共同仅f1→w=0.9/0.9=1,D=0.5(仅单元保留)",
      abs(wsum2 - 0.9) < 1e-15 and abs(D2 - 0.5) < 1e-12, str(D2))
# Charter7-2: 固定分母——缺特征不再抬高剩余特征相对权重(f1 权恒 0.9)
D4, wsum4, terms4 = ae.weighted_distance({'f1': 1.0, 'f2': -1.0},
                                         {'f1': 0.5},
                                         {'f1': 0.9, 'f2': 0.1},
                                         wsum_total=1.0)
check("固定分母 W_U=1.0: wsum 恒=W_U(非共同和),f1 权恒0.9(不重归一)",
      wsum4 == 1.0 and abs(terms4['f1']['w'] - 0.9) < 1e-12
      and abs(D4 - math.sqrt(0.9 * 0.25)) < 1e-12, str(D4))
check("固定分母距离<旧口径(缺席不放大相对权重)",
      D4 < D2, f"{D4} vs {D2}")
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

# ══ [4] 特征变换 ═══════════════════════════════════════════════════
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

# ══ [5] 拒答路径 ═══════════════════════════════════════════════════
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

# ══ [6] 全管线独立重算(60月,Charter7 统一特征集口径) ══════════════
print("\n[6] 全管线: 独立重算(统一特征集+固定分母+双键排序+簇去重)")
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
_cand = d['candidates']
check("候选计数: scanned=60/valid=13/overlap=12/insufficient=35"
      "+独立簇数随行(Charter7-5)",
      _cand['scanned'] == 60 and _cand['valid'] == 13
      and _cand['dropped_overlap'] == 12
      and _cand['dropped_insufficient'] == 35
      and _cand['n_independent_clusters_topN'] == 2
      and '簇去重' in _cand['cluster_dedup'], str(_cand))
check("13<24→样本不稳警示", any('<24' in w for w in res['warnings']),
      str(res['warnings']))
check("TOP-5 请求但独立簇仅2→实际输出2+簇不足警示",
      len(d['top']) == 2
      and any('独立簇仅 2 个' in w for w in res['warnings']),
      str([t['candidate_month'] for t in d['top']]))


# ── 独立重算(测试自写统一特征集+固定分母+双键排序+贪心簇去重;零调用
#    引擎内部——特征变换/阈值/权重登记均按规格文本独立实现) ──
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
    feats['HY_OAS_d12m'] = {mk: hy[mk] - hy[mkey_add(mk, -12)]
                            for mk in hy if mkey_add(mk, -12) in hy}
    for _mid, _fk in (('SPX_CAPE', 'SPX_CAPE_level'),
                      ('SPX_PE_TTM', 'SPX_PE_TTM_level')):
        if _mid in mp:
            feats[_fk] = last_grid(_mid)
    return feats


FEATS = build_feats(smap, MK60)
FEAT_DIM = {k: dim for k, dim, _m, _t in ae.FEATURE_SPECS}
VALID_FEATS = [k for k in FEATS if k in
               {kk for kk, _dd, _m, _t in ae.FEATURE_SPECS}]


def ind_step(fkey):
    """网格自然步长=相邻键月差中位数(独立实现,Charter7-4b)。"""
    ks = sorted(FEATS[fkey])
    if len(ks) < 2:
        return 1
    gaps = sorted(abs(mkey_dist(ks[i], ks[i - 1]))
                  for i in range(1, len(ks)))
    return max(1, gaps[len(gaps) // 2])


def ind_required(fkey):
    return max(1, int(math.ceil(36 / float(ind_step(fkey)))))


def ind_z(fkey, mkey):
    """expanding z(μ/σ=含当期历史;最少观测=36/步长;独立实现)。"""
    req = ind_required(fkey)
    h = sorted(m for m in FEATS[fkey] if m <= mkey)
    if mkey not in FEATS[fkey] or len(h) < req:
        return None, len(h), req
    vs = [FEATS[fkey][m] for m in h]
    mu0 = sum(vs) / len(vs)
    var0 = sum((x - mu0) ** 2 for x in vs) / len(vs)
    if var0 <= 0:
        return None, len(h), req
    return (FEATS[fkey][mkey] - mu0) / math.sqrt(var0), len(h), req


ANCHOR = '2024-12'
U_ind = {}
for k in VALID_FEATS:
    if FEATS[k].get(ANCHOR) is None:
        continue
    z, _n, _r = ind_z(k, ANCHOR)
    if z is not None:
        U_ind[k] = z

# 特征权=维度权/该维规格表全定义特征数(§1.1,与数据在场无关)
nspec = {}
for _k, _dd, _m, _t in ae.FEATURE_SPECS:
    nspec[_dd] = nspec.get(_dd, 0) + 1
feat_w = {k: (1.0 / 6.0) / nspec[FEAT_DIM[k]] for k in U_ind}
W_U = sum(feat_w[k] for k in U_ind)

cands_ind = []
cutoff = mkey_add(ANCHOR, -12)
for mk in MK60:
    if mk > cutoff or not any(FEATS[k].get(mk) is not None
                              for k in VALID_FEATS):
        continue
    zs, miss = {}, {}
    for k in U_ind:
        if FEATS[k].get(mk) is None:
            miss[k] = 'no_value_at_candidate_month'
            continue
        z, n, req = ind_z(k, mk)
        if z is None:
            miss[k] = ('hist_%d<%d' % (n, req)) if n < req else 'sigma_0'
        else:
            zs[k] = z
    if len({FEAT_DIM[k] for k in zs}) >= 4:
        cands_ind.append((mk, zs, miss))

rows_ind = []
for mk, zs, miss in cands_ind:
    sq = sum(feat_w[k] * (U_ind[k] - zs[k]) ** 2 for k in zs)
    rows_ind.append({'m': mk, 'D': math.sqrt(sq / W_U), 'miss': miss,
                     'acct': sum(feat_w[k] for k in zs), 'zs': zs})
rows_ind.sort(key=lambda r: (len(r['miss']), r['D'], r['m']))
ds_ind = [r['D'] for r in rows_ind]
for r in rows_ind:
    r['pct'] = (sum(1 for d0 in ds_ind if d0 < r['D'])
                / (len(ds_ind) - 1) * 100.0) if len(ds_ind) > 1 else 0.0
reps_ind = []
for r in rows_ind:
    if all(abs(mkey_dist(r['m'], q['m'])) >= 12 for q in reps_ind):
        reps_ind.append(r)
    else:
        pass
cluster_ind = {r['m']: [r['m']] for r in reps_ind}
for r in rows_ind:
    owner = next((q for q in reps_ind
                  if abs(mkey_dist(r['m'], q['m'])) < 12), None)
    if owner is not None and r['m'] != owner['m']:
        cluster_ind[owner['m']].append(r['m'])

check("独立重算: 有效候选13个(镜像)", len(cands_ind) == 13,
      str(len(cands_ind)))
check("feature_set=锚点准入特征集 U(特征/wsum 独立对照)",
      d['feature_set']['features'] == sorted(U_ind)
      and d['feature_set']['n_features'] == len(U_ind)
      and d['feature_set']['wsum'] == round(W_U, 6)
      and 'anchor_admitted' in d['feature_set']['basis'],
      str(d['feature_set']))
top1 = d['top'][0]
top2 = d['top'][1]
check("TOP 全序=独立重算贪心簇代表(TOP-1=2023-12 0缺席,TOP-2=2022-12)",
      [t['candidate_month'] for t in d['top']]
      == [r['m'] for r in reps_ind[:5]]
      and [t['candidate_month'] for t in d['top']] == ['2023-12', '2022-12'],
      f"engine={[t['candidate_month'] for t in d['top']]} "
      f"ind={[r['m'] for r in reps_ind[:5]]}")
check("TOP-1 距离=独立重算(固定分母 W_U,12特征全计,1e-6)",
      abs(top1['distance'] - rows_ind[0]['D']) < 1e-6
      and len(top1['missing_features']) == 0,
      f"{top1['distance']} vs {rows_ind[0]['D']}")
_r2d = next(r['D'] for r in rows_ind if r['m'] == top2['candidate_month'])
check("TOP-2 距离=独立重算(缺席5特征不入分子、仍在分母,1e-6)",
      abs(top2['distance'] - _r2d) < 1e-6,
      f"{top2['distance']} vs {_r2d}")
check("排序双键: 0缺席候选先于5缺席(偏差更大但证据完整者不得被反超)",
      len(top1['missing_features']) == 0
      and len(top2['missing_features']) == 5
      and top2['distance'] < top1['distance'],
      f"D1={top1['distance']}(miss0) D2={top2['distance']}(miss5)")
check("norm_wsum≡W_U 全候选一致(Charter7-2 统一分母,非逐候选重归一)",
      top1['norm_wsum'] == round(W_U, 6)
      and top2['norm_wsum'] == round(W_U, 6)
      and top1['norm_wsum'] == top2['norm_wsum'],
      f"{top1['norm_wsum']} / {top2['norm_wsum']} vs {round(W_U, 6)}")
check("TOP-2 missing_features=独立重算(逐特征原因)",
      top2['missing_features']
      == {k: 'hist_24<36' for k in
          ('CPI_yoy', 'FED_FUNDS_d12m', 'HY_IG_gap_d12m', 'HY_OAS_d12m',
           'UST_10Y_d12m')},
      str(top2['missing_features']))
check("accounted/missing_wsum=独立重算(覆盖权重份额披露)",
      top2['accounted_wsum'] == round(rows_ind[1]['acct'], 6)
      and abs(top2['missing_wsum']
              - round(W_U - rows_ind[1]['acct'], 6)) < 1e-9
      and abs(top2['accounted_wsum'] + top2['missing_wsum'] - W_U) < 1e-6,
      f"{top2['accounted_wsum']}/{top2['missing_wsum']} vs "
      f"{round(rows_ind[1]['acct'], 6)}")
r2 = next(r for r in rows_ind if r['m'] == top2['candidate_month'])
check("TOP-2 逐特征 w_norm=feat_w/W_U(同一特征全候选一致,6dp)",
      all(v['w_norm'] == round(feat_w[k] / W_U, 6)
          for k, v in top2['features_detail'].items())
      and all(top1['features_detail'][k]['w_norm']
              == top2['features_detail'][k]['w_norm']
              for k in top2['features_detail']),
      str(top2['features_detail']))
check("TOP-2 features_detail gap=anchor_z−cand_z(独立 z 对照)",
      all(abs(v['gap'] - (U_ind[k] - r2['zs'][k])) < 1e-9
          for k, v in top2['features_detail'].items()))
check("cluster_members=独立贪心簇(2023-12簇含其后11个月+自身)",
      top1['cluster_members'] == sorted(cluster_ind['2023-12'])
      and top2['cluster_members'] == ['2022-12'],
      f"{top1['cluster_members']} / {top2['cluster_members']}")
check("重叠排除: 全部候选≤锚点−12月(2023-12)",
      all(t['candidate_month'] <= '2023-12' for t in d['top']))
check("TOP-1 距离分位=独立重算(0缺席但距离最大→100%)",
      abs(top1['distance_percentile'] - round(rows_ind[0]['pct'], 4)) < 1e-3
      and top1['distance_percentile'] == 100.0,
      str(top1['distance_percentile']))
check("TOP-2 距离分位=独立重算",
      abs(top2['distance_percentile'] - round(r2['pct'], 4)) < 1e-3,
      f"{top2['distance_percentile']} vs {round(r2['pct'], 4)}")
check("features_detail 逐特征锚点/候选 z+归一权重随行",
      all({'anchor_z', 'cand_z', 'gap', 'w_norm'} == set(v)
          for t in d['top'] for v in t['features_detail'].values()))
# dims contribution_share 和=1(数值和)
cs = sum(v['contribution_share'] for v in top1['dims'].values())
check("维度贡献份额和=1(6dp舍入容差)", abs(cs - 1.0) < 5e-6, str(cs))
check("normalization 注记月数折算(36个月史: 月36/季12)",
      '月网格 36 点' in d['normalization']['min_observations_note']
      and '季网格 12 点' in d['normalization']['min_observations_note'],
      d['normalization']['min_observations_note'])
check("锚点侧无弃用特征(全部12特征准入,features_dropped_at_anchor 空)",
      d['features_dropped_at_anchor'] == {},
      str(d['features_dropped_at_anchor']))

# ══ [7] 事后演变(手算+Charter7-3 窗口起止观测日) ═══════════════════
print("\n[7] aftermath 手算(候选 2022-12/2023-12,起点=次月首日起)")
# anchor=2023-12 回放: 候选仅 2022-12 一个(<8)→正确拒答(阈值不放宽)
res_replay = ae.run(smap, REG_LOADED, anchor='2023-12')
check("anchor=2023-12 回放: 候选仅1个<8→拒答(宁缺毋滥)",
      res_replay['ok'] is False
      and res_replay['error'][0] == 'insufficient_candidates')
# 默认锚点(2024-12)取 top=13: 独立簇仅2——簇成员经 cluster_members 披露
res_a = ae.run(smap, REG_LOADED, top=13)
check("默认锚点 top=13: 独立簇仅2,2023-02 以簇成员披露(非独立样本)",
      res_a['ok'] is True and len(res_a['data']['top']) == 2
      and '2023-02' in top1['cluster_members'],
      str([t['candidate_month'] for t in res_a['data']['top']]))
top_a = {t['candidate_month']: t for t in res_a['data']['top']}
# Charter7-2(D1 承接): 2023-12=12特征全计(TOP-1),与 TOP-2 同一分母 W_U
t2312 = top_a['2023-12']
check("D1: TOP-1=2023-12 全12特征(含 HY_OAS_d12m),缺席清单空",
      'HY_OAS_d12m' in t2312['features_detail']
      and len(t2312['features_detail']) == 12
      and t2312['missing_features'] == {},
      str(sorted(t2312['features_detail'])))
check("D1: norm_wsum=统一分母 W_U(TOP-1 与 TOP-2 一致,不再逐候选漂移)",
      t2312['norm_wsum'] == top_a['2022-12']['norm_wsum'] == round(W_U, 6),
      f"{t2312['norm_wsum']}")
t122 = top_a['2022-12']
af = t122['aftermath']
check("aftermath 标签逐字(事后非预测+起止口径+窗口随行,Charter7-3)",
      af['label'] == ae.AFTERMATH_LABEL
      and '起点=候选锚点月之后首个观测' in af['label']
      and '{资产}_window' in af['label'], af['label'])
# 手算: SPX 起点=2023-01-28(次月首日起首个观测)=1155;
# 1m 窗(≤2023-01-31)内无起点之后的新观测→unavailable(不以0%冒充);
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
# Charter7-3: 逐窗实际起止观测日({资产}_window)——可自行复算口径
spw = af['SPX_window']
check("SPX_window: 1m=None/3m..12m start=2023-01-28, end=各窗末观测日",
      spw == {'1m': None,
              '3m': {'start': '2023-01-28', 'end': '2023-03-31'},
              '6m': {'start': '2023-01-28', 'end': '2023-06-30'},
              '12m': {'start': '2023-01-28', 'end': '2023-12-31'}},
      str(spw))
u10af = af['UST_10Y']
check("UST_10Y 利率类=pp(手算 1m=+0.74,3m=+0.25,12m=+0.75)",
      abs(u10af['1m'] - 0.74) < 1e-9 and abs(u10af['3m'] - 0.25) < 1e-9
      and abs(u10af['12m'] - 0.75) < 1e-9, str(u10af))
check("UST_10Y_window: 起点=2023-01-05,1m 末=2023-01-15(窗内实际观测)",
      af['UST_10Y_window'] == {
          '1m': {'start': '2023-01-05', 'end': '2023-01-15'},
          '3m': {'start': '2023-01-05', 'end': '2023-03-31'},
          '6m': {'start': '2023-01-05', 'end': '2023-06-30'},
          '12m': {'start': '2023-01-05', 'end': '2023-12-31'}},
      str(af['UST_10Y_window']))
check("起点不回吸锚点月内数据(2022-12-15=1000 未入窗)",
      abs(sp['3m'] - (1210.0 / 1000.0 - 1) * 100) > 1e-6)
# 候选 2023-12(现 TOP-1): 次月起无任何 SPX 观测→全 horizon 如实
# unavailable+窗口 null(不以缩短窗/0值冒充)
af2 = t2312['aftermath']
check("候选2023-12 SPX: 次月起无观测→全horizon null+窗口null",
      all(af2['SPX'][h] is None for h in ae.AFTERMATH_HORIZONS)
      and all(af2['SPX_window'][h] is None for h in ae.AFTERMATH_HORIZONS)
      and set(af2['unavailable_horizons']['SPX'])
      == set(ae.AFTERMATH_HORIZONS),
      str(af2['SPX_window']))
# 全 TOP 块 horizon 一致性(按资产各自): 值非None⇔该资产清单不含该horizon
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
check("泄漏规则2: 锚点后数据突变→固定锚点下 TOP 排序不变",
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

# Charter7-5 判据2: 事后分歧按**独立簇代表**口径(n≥3 且一致率<0.6)。
# fixture=95月纯斜坡(步长取二进制精确值→全部 d12m 恒定 σ=0 弃用,特征面
# =7个 level 特征,全部仿射→z 剖面同一→D(j)=|z_a−z_j| 完全可手算);
# 候选 2020-01..2023-12 → 贪心簇代表恰为四个 12 月,2023-02 型相邻月不再
# 冒充独立样本。GOLD_F 月频周期7模式→四代表 3m 方向 2上2下→一致率 0.5
NR = 95
MKR = months('2017-02', NR)
_ramp = (('UNEMPLOYMENT', 5.0, 0.03125), ('BEI_10Y', 2.0, 0.015625),
         ('FED_FUNDS', 4.0, 0.0625), ('UST_10Y', 4.25, 0.03125),
         ('HY_OAS', 5.0, 0.03125), ('IG_OAS', 1.0, 0.015625),
         ('VIX', 15.0, 0.125))
smap_r = {mid: {'dates': [mk + '-15' for mk in MKR],
                'values': [a + b * i for i in range(NR)]}
          for mid, a, b in _ramp}
smap_r['DXY'] = {'dates': [mk + '-15' for mk in MKR],
                 'values': [100.0 + 0.0625 * i for i in range(NR)]}
GPATT = [0.0, 1.0, 3.0, 4.0, 8.0, 5.0, 2.0]      # 周期7(不整除12)
smap_r['GOLD_F'] = {'dates': [mk + '-15' for mk in MKR],
                    'values': [2000.0 + GPATT[i % 7] for i in range(NR)]}
res_r = ae.run(smap_r, REG_LOADED, top=8)


def ramp_z(j):
    """斜坡 0..j 的 expanding z(独立闭式复算)。"""
    xs = [float(i) for i in range(j + 1)]
    mu0 = sum(xs) / len(xs)
    var0 = sum((x - mu0) ** 2 for x in xs) / len(xs)
    return (xs[-1] - mu0) / math.sqrt(var0)


za_r = ramp_z(NR - 1)
check("ramp fixture: U=7个level特征(d12m σ=0 全弃用带原因)",
      res_r['data']['feature_set']['features']
      == ['BEI_10Y_level', 'FED_FUNDS_level', 'HY_IG_gap_level',
          'HY_OAS_level', 'UNEMPLOYMENT_level', 'UST_10Y_level', 'VIX_level']
      and sorted(res_r['data']['features_dropped_at_anchor'])
      == ['FED_FUNDS_d12m', 'HY_IG_gap_d12m', 'HY_OAS_d12m',
          'UST_10Y_d12m']
      and all(v == 'sigma_0'
              for v in res_r['data']['features_dropped_at_anchor'].values()),
      str(res_r['data']['features_dropped_at_anchor']))
check("ramp fixture: 簇代表=四个相隔12月的十二月(独立贪心)",
      [t['candidate_month'] for t in res_r['data']['top']]
      == ['2023-12', '2022-12', '2021-12', '2020-12'],
      str([t['candidate_month'] for t in res_r['data']['top']]))
check("ramp fixture: 各代表距离=手算|z_a−z_j|(仿射特征面,1e-6)",
      all(abs(t['distance'] - abs(za_r - ramp_z(MKR.index(t['candidate_month']))))
          < 1e-6 for t in res_r['data']['top']),
      str([(t['candidate_month'], t['distance']) for t in res_r['data']['top']]))
_dirs = []
for t in res_r['data']['top']:
    i0 = MKR.index(t['candidate_month'])
    v1 = 2000.0 + GPATT[(i0 + 1) % 7]
    v3 = 2000.0 + GPATT[(i0 + 3) % 7]
    _dirs.append(1 if v3 > v1 else (-1 if v3 < v1 else 0))
_agree = max(_dirs.count(1), _dirs.count(-1)) / len(_dirs)
check("D2判据2: 独立复算四代表 3m 方向 2上2下→一致率 0.5",
      _dirs.count(1) == 2 and _dirs.count(-1) == 2
      and abs(_agree - 0.5) < 1e-12, str(_dirs))
check("D2判据2: GOLD_F 3m 分歧警示随行(独立簇口径 0.50<0.6)",
      any(('GOLD_F 3m' in w and '分歧' in w and '0.50' in w)
          for w in res_r['warnings']), str(res_r['warnings'][:6]))
check("D2判据2: dispersion GOLD_F_3m=0.5+独立簇基准随行",
      res_r['data']['dispersion']['topN_aftermath_sign_agreement']
      ['GOLD_F_3m'] == 0.5
      and res_r['data']['dispersion']['n_independent_clusters'] == 4
      and '独立簇代表' in res_r['data']['dispersion']['basis'],
      str(res_r['data']['dispersion']))
check("D2判据2: UST_10Y 3m=手算 pp(斜坡 2×0.03125=0.0625)+窗口=次月起",
      all(abs(t['aftermath']['UST_10Y']['3m'] - 0.0625) < 1e-9
          and t['aftermath']['UST_10Y_window']['3m']
          == {'start': mkey_add(t['candidate_month'], 1) + '-15',
              'end': mkey_add(t['candidate_month'], 3) + '-15'}
          for t in res_r['data']['top']),
      str(res_r['data']['top'][0]['aftermath']['UST_10Y_window']))
check("D2判据2: 负对照——原稀疏序列(独立簇2<3)无事后分歧警示",
      not any('分歧' in w for w in res_a['warnings'])
      and res['data']['dispersion']['n_independent_clusters'] == 2,
      str(res['data']['dispersion']))

# D2(收尾)判据4: TOP-1 与中位不分离((med−min)/med<10%,**按距离值排序**——
# 双键排序后 rank 首位≠距离最小者,判据不得读 rank 序)。前向解序列逐月
# 命中目标 z 剖面(测试侧独立数值解,镜像 z 定义);候选窗内 z 剖面近平坦
# →各候选距离挤在 <1% 带内→警示;原序列(负对照)分离充分无警示
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
check("D2判据4: 压缩距离 fixture 正常出榜(独立簇2,13候选全可算)",
      res_c4['ok'] is True and len(res_c4['data']['top']) == 2
      and res_c4['data']['candidates']['valid'] == 13,
      str(res_c4.get('error')))
check("D2判据4: TOP-1 不分离警示随行",
      any('TOP-1 未与候选分布分离' in w for w in res_c4['warnings']),
      str(res_c4['warnings'][:5]))
# 2022-12(TOP-2,代表): 无扰动手算 D=|z_a−z_c|·√(W_acct/W_U)(yoy/d12m
# 扰动仅影响 2023-12);权重经规格表在测试侧独立登记
FEATS_C4 = build_feats(smap_c4, MK60)
FEATS = FEATS_C4                    # [6] 镜像函数复用(c4 面)
U_c4 = {}
for k in [kk for kk in FEATS_C4 if kk in
          {k2 for k2, _d2, _m2, _t2 in ae.FEATURE_SPECS}]:
    if FEATS_C4[k].get('2024-12') is None:
        continue
    z, _n, _r = ind_z(k, '2024-12')
    if z is not None:
        U_c4[k] = z
feat_w_c4 = {k: (1.0 / 6.0) / nspec[FEAT_DIM[k]] for k in U_c4}
W_U_c4 = sum(feat_w_c4[k] for k in U_c4)
_lv9 = ['UNEMPLOYMENT_level', 'BEI_10Y_level', 'FED_FUNDS_level',
        'UST_10Y_level', 'HY_OAS_level', 'HY_IG_gap_level', 'VIX_level',
        'SPX_CAPE_level', 'SPX_PE_TTM_level']
W_acct9 = sum(feat_w_c4[k] for k in _lv9)
t2_c4 = res_c4['data']['top'][1]
check("D2判据4: 2022-12 距离=手算|Δz|·√(W_acct/W_U)(固定分母,1e-4)",
      t2_c4['candidate_month'] == '2022-12'
      and abs(t2_c4['distance']
              - abs(C_T - tgs_c4[35]) * math.sqrt(W_acct9 / W_U_c4)) < 1e-4,
      f"{t2_c4['distance']} vs "
      f"{abs(C_T - tgs_c4[35]) * math.sqrt(W_acct9 / W_U_c4)}")
# 镜像全表 D(判据4 手算分离度): 沿用 ind_z 镜像,但按 c4 特征面求值
FEATS_SAVE, FEATS = FEATS, FEATS_C4
_ds_c4 = []
for mk in MK60:
    if mk > cutoff:
        continue
    zs_c, miss_c = {}, {}
    for k in U_c4:
        if FEATS_C4[k].get(mk) is None:
            miss_c[k] = 'no_value_at_candidate_month'
            continue
        z, n, req = ind_z(k, mk)
        if z is None:
            miss_c[k] = ('hist_%d<%d' % (n, req)) if n < req else 'sigma_0'
        else:
            zs_c[k] = z
    if len({FEAT_DIM[k] for k in zs_c}) >= 4:
        _ds_c4.append(math.sqrt(
            sum(feat_w_c4[k] * (U_c4[k] - zs_c[k]) ** 2 for k in zs_c)
            / W_U_c4))
FEATS = FEATS_SAVE
_ds_c4.sort()
_sep_c4 = ((_ds_c4[len(_ds_c4) // 2] - _ds_c4[0])
           / _ds_c4[len(_ds_c4) // 2])
check("D2判据4: 手算分离度<10%(13候选全表,按距离值排序)与警示自洽",
      len(_ds_c4) == 13 and _sep_c4 < 0.10,
      f"n={len(_ds_c4)} sep={_sep_c4:.4f}")
check("D2判据4: 负对照(原fixture分离充分)无该警示",
      not any('TOP-1 未与候选分布分离' in w for w in res['warnings']))
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
      "realtime=blocked(锚点月窗无跨日vintage,Charter7-1)",
      rmg['descriptive'] == 'available' and 'blocked' in rmg['event_study']
      and rmg['realtime_info_set'].startswith(
          'blocked: 查询期20241201~20241231起点月窗内无vintage快照')
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
check("CLI analog: ok=true+信封(TOP-5 请求→独立簇2 实际输出2,Charter7-5)",
      code == 0 and out['ok'] and out['capability'] == 'analog'
      and out['snapshot_id'] == 'research_snapshot_TEST'
      and len(out['data']['top']) == 2
      and out['data']['candidates']['n_independent_clusters_topN'] == 2,
      str(out.get('error')))
check("CLI analog: 警示随行(13<24+簇不足)",
      any('<24' in w for w in out['warnings'])
      and any('独立簇仅 2 个' in w for w in out['warnings']))
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
check("CLI --top 2(默认锚点): 恰2条(=独立簇数)+锚点月随行",
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
