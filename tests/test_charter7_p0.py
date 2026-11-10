#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter 7 P0 修复轮验收测试(2026-11-10,审计 C7_P0_seven_issues_verify)。

七项逐条(独立计算预期+边界+回归;不降门槛/不删警告/不改期望值):
  [1] realtime 门语义(5 CONFIRMED): 判据=**查询时窗起点月窗内跨日 vintage
      在场性**(research_snapshot 基础日期;同日 _vN 归并不计)——当前窗/
      历史窗在带/历史窗无带三形态+带边界(起点日=在带,次月首日=出带,
      前月末=出带)+同日修订只附披露不翻可用性;
  [2] 特征准入不对称(5 CONFIRMED): 统一特征集 U+固定分母 W_U——单元证明
      逐候选重归一会**改变排序**(0.26 vs 0.25 翻转);引擎级回归=完整证据
      候选(距离更大)必须排在小距离缺数候选之前;
  [3] aftermath 披露(3 PARTIAL): 逐窗实际起止观测日 {资产}_window 随行
      (start=次月首日起首个观测,end=+N 月末日内最后观测;窗外观测不入
      窗——2024-01-05 观测不得充当 2022-12 的 12m 末点);
  [4] 跨频率门槛(4 CONFIRMED): 季网格 36 个月史折算 12 点(11=拒/12=恰
      /13=过);锚点侧缺席带原因(release_lag 一月滞后/差2个月/季频网格
      非季末锚);不在 U 的特征对候选计算不可见(增删同构);维度缺席
      判据**双侧**(候选侧全候选缺维也警示);
  [5] 候选重叠(5 CONFIRMED): 相差<12 个月=同簇,TOP-N 只出簇代表——
      全对逐对断言 ≥12 月;相邻月(2023-01 型)只进 cluster_members;
  [6] 保留 vs 溯源(6 CONFIRMED): tempdir 全流程模拟——快照声明来源 CLEAN
      →保留策略清理(声明档 protected_archived 不删/代表档 gzip/过期未
      声明档删除)→再验仍 CLEAN(归档读回+sha256 一致+notes 披露)+
      resolve_inputs 归档回退+load_metric_series gzip 读回;
  [7] 新闻摘要模型门(7 PARTIAL): IA_NEWS_MODEL_SUMMARY 独立显式 opt-in,
      默认关闭——MODEL_* 三参齐备**不再自动调用**(零调用计数器实证);
      开启+齐备才调用;文档锁(USER_GUIDE/ia_cli)。

数据纪律: 全部 fixture=合成内存序列/临时目录;零网络零真实数据零凭证。
运行: ~/AI内容/venv/bin/python3 tests/test_charter7_p0.py
"""
import contextlib
import gzip
import hashlib
import io
import json
import math
import os
import sys
import tempfile
from datetime import datetime
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

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
    y, m = int(start[:4]), int(start[5:7])
    return ['%04d-%02d' % ((y * 12 + m - 1 + k) // 12,
                           (y * 12 + m - 1 + k) % 12 + 1) for k in range(n)]


def mkey_dist(a, b):
    return (int(a[:4]) * 12 + int(a[5:7])) - (int(b[:4]) * 12 + int(b[5:7]))


print("═" * 64)
print("Charter7 P0 七项修复验收(独立计算预期+边界+回归)")
print("═" * 64)

import analog_engine as ae          # noqa: E402
import fact_engine as fe            # noqa: E402
import research_provenance as rp    # noqa: E402
import snapshot_builder as sb       # noqa: E402
import data_retention as drt        # noqa: E402
import research_history_query as rhq  # noqa: E402
import news_collector as nc         # noqa: E402

REG = fe.load_registry()

# ══ [1] Charter7-1: realtime 门=查询时窗跨日 vintage 在场性 ═════════
print("\n[1] realtime 门语义(跨日vintage判定,同日_vN不构成vintage)")
GATE = ae.realtime_gate_text
with tempfile.TemporaryDirectory() as td:
    for name in ('research_snapshot_20260101.json',
                 'research_snapshot_20260101_v2.json',
                 'research_snapshot_20260101_v3.json',
                 'research_snapshot_20260115.json',
                 'research_snapshot_20260115_v2.json',
                 'anchors_20260120.json',
                 'research_snapshot_20260101_v2.meta.json'):
        open(os.path.join(td, name), 'w').write('{}')
    vd = rp.vintage_dates(td)
    check("vintage_dates: _vN 归并到基础日期(2个跨日vintage,研究层旁挂不计)",
          vd == ['20260101', '20260115'], str(vd))
check("vintage_dates: 目录不存在→空清单(零推断)",
      rp.vintage_dates('/nonexistent_dir_c7p0') == [])
t_cur = GATE(None, None, ['20260101', '20260115'])
check("当前窗(None)→available(现役快照即当前时点信息集)+跨日vintage计数",
      t_cur.startswith('available(现役快照即当前时点信息集;跨日vintage=2个'
                       '[20260101,20260115];')
      and '同日_vN修订不构成跨日vintage' in t_cur, t_cur)
check("当前窗无任何vintage→仍available(现役快照=当前信息集)",
      GATE(None, None, []).startswith(
          'available(现役快照即当前时点信息集;跨日vintage=0个;'))
t_band = GATE('20260101', '20260131', ['20251231', '20260115', '20260201'])
check("历史窗在带(20260115∈起点月窗)→available+select_snapshot点时取版",
      t_band.startswith('available(查询起点月窗内存在跨日vintage快照:20260115;')
      and 'select_snapshot' in t_band, t_band)
check("带边界: vintage=起点日(20260101)→在带",
      GATE('20260101', '20260131', ['20260101']).startswith(
          'available(查询起点月窗内存在跨日vintage快照:20260101;'))
t_out = GATE('20260101', '20260131', ['20251231', '20260201'])
check("带边界: 前月末(20251231)/次月首日(20260201)均出带→blocked",
      t_out.startswith('blocked: 查询期20260101~20260131起点月窗内无vintage快照'
                       '(现存跨日vintage:20251231,20260201')
      and '不得以今日修订口径冒充当时值' in t_out, t_out)
t_sd = GATE('20260101', '20260131', ['20260201'], same_day_revision=True)
check("同日 _vN 在场**不翻可用性**: 仍 blocked+尾注披露(取最高_vN)",
      t_sd.startswith('blocked:') and '当日修订版在场' in t_sd, t_sd)
t_sd2 = GATE('20260101', '20260131', ['20260105'], same_day_revision=True)
check("在带+同日修订→available 且尾注披露",
      t_sd2.startswith('available(查询起点月窗内存在跨日vintage快照:20260105')
      and '当日修订版在场' in t_sd2, t_sd2)
check("无vintage→blocked 现存清单如实'无'",
      GATE('20260101', '20260131', []).startswith(
          'blocked: 查询期20260101~20260131起点月窗内无vintage快照'
          '(现存跨日vintage:无'))

# ══ [2] Charter7-2: 统一特征集固定分母 ═════════════════════════════
print("\n[2] 特征准入不对称(固定分母 W_U,完整证据优先)")
# 单元: 同一对候选,旧口径(逐候选重归一)与固定分母**排序相反**——
# X 仅 f1(gap 0.26),Y 双特征(gap 0.25/0.25),权 f1=0.9/f2=0.1
DX_leg, wsumX_leg, _ = ae.weighted_distance(
    {'f1': 1.0, 'f2': -1.0}, {'f1': 0.74}, {'f1': 0.9, 'f2': 0.1})
DY_leg, _, _ = ae.weighted_distance(
    {'f1': 1.0, 'f2': -1.0}, {'f1': 0.75, 'f2': -0.75},
    {'f1': 0.9, 'f2': 0.1})
DX_fix, wsumX_fix, _ = ae.weighted_distance(
    {'f1': 1.0, 'f2': -1.0}, {'f1': 0.74}, {'f1': 0.9, 'f2': 0.1},
    wsum_total=1.0)
DY_fix, _, _ = ae.weighted_distance(
    {'f1': 1.0, 'f2': -1.0}, {'f1': 0.75, 'f2': -0.75},
    {'f1': 0.9, 'f2': 0.1}, wsum_total=1.0)
check("单元: 旧口径重归一把 X 剩余权放大到 1→D_X=0.26>D_Y=0.25(Y先)",
      abs(wsumX_leg - 0.9) < 1e-12 and abs(DX_leg - 0.26) < 1e-12
      and abs(DY_leg - 0.25) < 1e-12 and DX_leg > DY_leg,
      f"{DX_leg} vs {DY_leg}")
check("单元: 固定分母 W_U=1→D_X=√0.9·0.26²≈0.2469<0.25(排序翻转,X先)",
      wsumX_fix == 1.0 and abs(DX_fix - math.sqrt(0.9 * 0.26 ** 2)) < 1e-12
      and abs(DY_fix - 0.25) < 1e-12 and DX_fix < DY_fix,
      f"{DX_fix} vs {DY_fix}")

# ── 引擎级共享 fixture(60月;UST_10Y 双用=特征面+事后窗) ──
N = 60
MK60 = months('2020-01', N)
_SM = {
    'UNEMPLOYMENT': [5.0 + 0.01 * i for i in range(N)],
    'CPI': [300.0 * (1.02 ** (i / 12.0)) for i in range(N)],
    'BEI_10Y': [2.0 + 0.001 * i for i in range(N)],
    'FED_FUNDS': [4.0 + 0.02 * i for i in range(N)],
    'UST_10Y': [4.2 + 0.015 * i for i in range(N)],
    'HY_OAS': [5.0 + 0.01 * i for i in range(N)],
    'IG_OAS': [1.0 + 0.005 * i for i in range(N)],
    'VIX': [15.0 + 0.05 * i for i in range(N)],
}


def base_smap():
    return {k: {'dates': [mk + '-15' for mk in MK60], 'values': list(v)}
            for k, v in _SM.items()}


spx_obs = {'2022-12-15': 1000.0, '2023-01-28': 1155.0, '2023-03-31': 1210.0,
           '2023-06-30': 1331.0, '2023-12-31': 1464.1}
# UST 事后观测: 2024-01-05=窗外探针(2022-12 候选 12m 界=2023-12-31,
# 该观测不得充当 12m 末点/不得改变 12m 值)
ust_obs = {'2023-01-05': 4.0, '2023-03-31': 4.25, '2023-06-30': 4.5,
           '2023-12-31': 4.75, '2024-01-05': 9.99}
smap = base_smap()
smap['SPX'] = {'dates': sorted(spx_obs),
               'values': [spx_obs[d] for d in sorted(spx_obs)]}
_u = {mk + '-15': v for mk, v in zip(MK60, _SM['UST_10Y'])}
_u.update(ust_obs)
_uk = sorted(_u)
smap['UST_10Y'] = {'dates': _uk, 'values': [_u[d] for d in _uk]}
smap['DXY'] = {'dates': sorted(spx_obs),
               'values': [100.0, 101.0, 102.0, 103.0, 104.0]}
smap['GOLD_F'] = {'dates': sorted(spx_obs),
                  'values': [2000.0, 2200.0, 2400.0, 2600.0, 2800.0]}
res = ae.run(smap, REG)
check("共享fixture正常出榜(锚点2024-12)", res['ok'] is True
      and res['data']['anchor_month'] == '2024-12',
      str(res.get('error')))
topB = res['data']['top']
check("引擎级回归: TOP-1=完整证据(0缺席)且距离**更大**——缺数候选距离"
      "再小也不得反超(审计#2构造案例)",
      len(topB[0]['missing_features']) == 0
      and len(topB[1]['missing_features']) > 0
      and topB[0]['distance'] > topB[1]['distance'],
      f"D1={topB[0]['distance']}(miss{len(topB[0]['missing_features'])}) "
      f"D2={topB[1]['distance']}(miss{len(topB[1]['missing_features'])})")
check("norm_wsum 全候选一致=统一分母(非逐候选重归一)",
      len({t['norm_wsum'] for t in topB}) == 1
      and topB[0]['norm_wsum'] == res['data']['feature_set']['wsum'])
t2 = topB[1]
check("accounted_wsum+missing_wsum=W_U(缺席权重份额如实披露,6dp舍入容差)",
      abs(t2['accounted_wsum'] + t2['missing_wsum'] - t2['norm_wsum']) < 2e-6
      and t2['missing_wsum'] > 0)

# ══ [3] Charter7-3: aftermath 逐窗起止观测日披露 ═══════════════════
print("\n[3] aftermath 披露({资产}_window 逐窗实际起止观测日)")
af = {t['candidate_month']: t['aftermath'] for t in topB}['2022-12']
check("标签逐字(事后非预测+起止口径+窗口随行可复算)",
      af['label'] == ae.AFTERMATH_LABEL
      and '{资产}_window' in af['label'], af['label'])
check("GOLD_F_window: 3m={2023-01-28→2023-03-31}/12m末=2023-12-31",
      af['GOLD_F_window']['3m'] == {'start': '2023-01-28',
                                    'end': '2023-03-31'}
      and af['GOLD_F_window']['12m'] == {'start': '2023-01-28',
                                         'end': '2023-12-31'},
      str(af['GOLD_F_window']))
uw = af['UST_10Y_window']
check("UST_window: start=次月首个观测2023-01-05,1m末=2023-01-15",
      uw['1m'] == {'start': '2023-01-05', 'end': '2023-01-15'},
      str(uw))
check("窗外探针不入窗: 12m末=2023-12-31(≠2024-01-05)",
      uw['12m'] == {'start': '2023-01-05', 'end': '2023-12-31'},
      str(uw['12m']))
check("窗外探针不改变值: 12m=4.75−4.0=0.75pp(手算,非9.99−4.0)",
      abs(af['UST_10Y']['12m'] - 0.75) < 1e-9, str(af['UST_10Y']['12m']))
check("窗口内无起点后新观测→该窗None+清单如实(SPX 1m)",
      af['SPX_window']['1m'] is None
      and '1m' in af['unavailable_horizons']['SPX'])

# ══ [4] Charter7-4: 跨频率门槛 ═════════════════════════════════════
print("\n[4] 跨频率门槛(36个月史按网格步长折算+锚点缺席原因+双侧维度判据)")
def qmonths(start_q, nq):
    """自 start_q 起的 nq 个季末月(每3个月一个,独立构造)。"""
    return months(start_q, 3 * nq)[::3]


QEND = qmonths('2022-03', 12)               # 2022-03..2024-12 季末月×12
check("季末月序列自证(2022-03起12个季末,步长恒3月)",
      QEND[0] == '2022-03' and QEND[-1] == '2024-12' and len(QEND) == 12
      and all(QEND[i + 1][:7] != QEND[i][:7] for i in range(11)),
      str(QEND[:3]))


def qfeats(nq, start_q='2022-03'):
    qm = qmonths(start_q, nq)
    return {'dates': [m + '-28' for m in qm],
            'values': [30.0 + 0.1 * i for i in range(nq)]}


# 11/12/13 点均**终于锚点月2024-12**(有锚点值,纯测历史点数门槛)
res11 = ae.run({**base_smap(), 'SPX_CAPE': qfeats(11, '2022-06')}, REG)
res12 = ae.run({**base_smap(), 'SPX_CAPE': qfeats(12)}, REG)
res13 = ae.run({**base_smap(), 'SPX_CAPE': qfeats(13, '2021-12')}, REG)
d11 = res11['data']['features_dropped_at_anchor']
check("季网格 11 点(=缺1季)→锚点侧弃用 hist_11<12(36个月史=12季点)",
      'SPX_CAPE_level' not in res11['data']['feature_set']['features']
      and d11.get('SPX_CAPE_level', '').startswith('hist_11<12'),
      str(d11))
check("季网格 12 点=恰好门槛→准入(估值维入场)",
      'SPX_CAPE_level' in res12['data']['feature_set']['features'])
check("季网格 13 点→准入(过界不算过头,门槛=最少观测)",
      'SPX_CAPE_level' in res13['data']['feature_set']['features'])
# 锚点侧缺席三类原因(序列止于锚点前一月=发布滞后/差2个月/季频非季末锚)
sm_lag1 = base_smap()
sm_lag1['VIX'] = {'dates': [mk + '-15' for mk in MK60[:-1]],
                  'values': list(_SM['VIX'])[:-1]}
r_lag1 = ae.run(sm_lag1, REG)
dl = r_lag1['data']['features_dropped_at_anchor']
check("release_lag: 序列止于锚点前一月(2024-11)→发布滞后原因如实",
      r_lag1['data']['anchor_month'] == '2024-12'
      and dl.get('VIX_level', '').startswith('release_lag(序列止于2024-11'),
      str(dl))
sm_lag2 = base_smap()
sm_lag2['VIX'] = {'dates': [mk + '-15' for mk in MK60[:-2]],
                  'values': list(_SM['VIX'])[:-2]}
r_lag2 = ae.run(sm_lag2, REG)
dl2 = r_lag2['data']['features_dropped_at_anchor']
check("差2个月: 序列止于2024-10→no_value_at_anchor(距锚点差2个月)",
      r_lag2['data']['anchor_month'] == '2024-12'
      and 'no_value_at_anchor' in dl2.get('VIX_level', '')
      and '差2个月' in dl2.get('VIX_level', ''), str(dl2))
r_q = ae.run({**base_smap(), 'SPX_CAPE': qfeats(12)}, REG, anchor='2024-11')
dq = r_q['data']['features_dropped_at_anchor']
check("季频网格: 锚点2024-11非季末月→quarterly_grid 原因(最近2024-09/"
      "下一2024-12)", dq.get('SPX_CAPE_level', '').startswith(
          'quarterly_grid(季频网格仅季末月有值,最近值月2024-09/下一值月'
          '2024-12,锚点月2024-11非季末月'), str(dq))
# 不在 U 的特征对候选计算不可见: 加锚点弃用的 CAPE(11点)前后输出同构
strip = lambda r: json.dumps({'top': [(t['candidate_month'], t['distance'],
                                       t['missing_features'])
                                      for t in r['data']['top']],
                              'cands': {k: r['data']['candidates'][k]
                                        for k in ('scanned', 'valid',
                                                  'dropped_overlap',
                                                  'dropped_insufficient')},
                              'U': r['data']['feature_set']['features']},
                             sort_keys=True)
res_plain = ae.run(base_smap(), REG)
check("不在U的特征不可见: 锚点弃用的CAPE(11点)增删同构(top/候选/U全同)",
      strip(res11) == strip(res_plain))
check("锚点弃用事实仍在披露面(features_dropped_at_anchor)",
      'SPX_CAPE_level' in res11['data']['features_dropped_at_anchor']
      and 'SPX_CAPE_level' not in res_plain['data']
      ['features_dropped_at_anchor'])
# 维度缺席判据双侧: 候选侧全候选缺估值维(PE 12点准入但候选历史<12)→警示
res_pe = ae.run({**base_smap(), 'SPX_PE_TTM': qfeats(12)}, REG)
check("候选侧维度缺席也警示(估值在U但全部候选上无有效特征→双侧判据)",
      'SPX_PE_TTM_level' in res_pe['data']['feature_set']['features']
      and any('候选侧维度缺席' in w and '估值' in w
              for w in res_pe['warnings']),
      str([w for w in res_pe['warnings'] if '维度' in w]))
check("锚点侧维度缺席警示仍在(VIX止于2024-11 fixture)",
      any('未覆盖维度' in w for w in r_lag1['warnings']))

# ══ [5] Charter7-5: 簇去重 ════════════════════════════════════════
print("\n[5] 候选重叠簇去重(相差<12月=同簇,TOP-N只出代表)")
_pairs = [(a['candidate_month'], b['candidate_month'])
          for i, a in enumerate(topB) for b in topB[i + 1:]]
check("TOP-N 全对逐对断言: 任意两代表相差≥12个月",
      all(abs(mkey_dist(a, b)) >= 12 for a, b in _pairs),
      str(_pairs))
check("相邻月候选(2023-01)只进 cluster_members,不进 TOP-N",
      '2023-01' in topB[0]['cluster_members']
      and all(t['candidate_month'] != '2023-01' for t in topB),
      str(topB[0]['cluster_members']))
check("簇去重元数据随行(n_independent_clusters_topN+dedup说明)",
      res['data']['candidates']['n_independent_clusters_topN'] == len(topB)
      and '簇去重' in res['data']['candidates']['cluster_dedup'])
check("独立簇<请求N→实际输出N'=簇数+警示(TOP-5请求仅2簇)",
      len(topB) < 5 and any('独立簇仅 2 个' in w for w in res['warnings']))
# 相邻月高频相似fixture(95月斜坡): 贪心代表=四个相隔12月的十二月
NR = 95
MKR = months('2017-02', NR)
_ramp = (('UNEMPLOYMENT', 5.0, 0.03125), ('BEI_10Y', 2.0, 0.015625),
         ('FED_FUNDS', 4.0, 0.0625), ('UST_10Y', 4.25, 0.03125),
         ('HY_OAS', 5.0, 0.03125), ('IG_OAS', 1.0, 0.015625),
         ('VIX', 15.0, 0.125))
smap_r = {mid: {'dates': [mk + '-15' for mk in MKR],
                'values': [a + b * i for i in range(NR)]}
          for mid, a, b in _ramp}
res_r = ae.run(smap_r, REG, top=8)
topR = res_r['data']['top']
check("斜坡fixture: TOP-8请求→4簇代表全对≥12月(2023-12/22-12/21-12/20-12)",
      [t['candidate_month'] for t in topR]
      == ['2023-12', '2022-12', '2021-12', '2020-12']
      and all(abs(mkey_dist(a['candidate_month'], b['candidate_month'])) >= 12
              for i, a in enumerate(topR) for b in topR[i + 1:]),
      str([t['candidate_month'] for t in topR]))
check("斜坡fixture: 簇不足警示(TOP-8请求但独立簇仅4个)",
      any('独立簇仅 4 个' in w for w in res_r['warnings']))

# ══ [6] Charter7-6: 保留 vs 溯源(tempdir 全流程模拟) ══════════════
print("\n[6] 保留策略 vs 研究溯源(声明档保护归档+归档读回)")
root6 = tempfile.mkdtemp(prefix='c7p6-')
td = os.path.join(root6, 'daily')
os.makedirs(td)
MAC = {'date': '2026-01-20', 'data': {'UST_10Y': {
    'value': '4.5', 'date': '2026-01-20', 'frequency': 'daily', 'unit': '%',
    'series': {'dates': ['2026-01-10', '2026-01-15', '2026-01-20'],
               'values': ['4.3', '4.4', '4.5']}}}}
mac_bytes = json.dumps(MAC, ensure_ascii=False,
                       indent=1, sort_keys=True).encode('utf-8')
mac_digest = hashlib.sha256(mac_bytes).hexdigest()
for nm, blob in (('macro_20260105.json', b'{"old": 1}'),
                 ('macro_20260120.json', mac_bytes),
                 ('macro_20260131.json', b'{"rep": 1}'),
                 ('macro_20261108.json', b'{"recent": 1}')):
    open(os.path.join(td, nm), 'wb').write(blob)
SS = {ch: {'status': 'MISSING'} for ch in
      ('global', 'macro', 'china', 'rate_economy', 'japan', 'jp', 'ea',
       'shiller')}
SS['macro'] = {'status': 'FALLBACK', 'file': 'macro_20260120.json',
               'file_date': '20260120', 'lag_days': 5, 'sha256': mac_digest}
snap6 = {'snapshot_id': 'research_snapshot_20260125',
         'target_date': '20260125', 'sources_status': SS}
open(os.path.join(td, 'research_snapshot_20260125.json'), 'w',
     encoding='utf-8').write(json.dumps(snap6, ensure_ascii=False))
check("研究引用集=快照声明来源档(恰1个)",
      drt.research_referenced_files(td) == {'macro_20260120.json'})
notes0 = []
probs0 = rp.sources_status_problems(SS, target_ymd='20260125', data_dir=td,
                                    trusted_root=root6, notes=notes0)
check("清理前: 声明来源档在场→sources_status CLEAN", probs0 == [],
      str(probs0[:2]))
rep6 = drt.prune_daily_archives(td, keep_days=90,
                                now=datetime(2026, 11, 10, 12, 0))
check("保留策略: 过期未声明档删除(macro_20260105)",
      'macro_20260105.json' in rep6['deleted']
      and not os.path.exists(os.path.join(td, 'macro_20260105.json')),
      str(rep6['deleted']))
check("保留策略: 声明来源档 protected_archived 不删(改gzip归档)",
      'macro_20260120.json' in rep6['protected_archived']
      and not os.path.exists(os.path.join(td, 'macro_20260120.json'))
      and os.path.isfile(os.path.join(td, 'archive',
                                      'macro_20260120.json.gz')),
      str(rep6['protected_archived']))
check("保留策略: 月度代表档 gzip 归档(20260131)+新档保留(20261108)",
      'macro_20260131.json' in rep6['archived']
      and os.path.isfile(os.path.join(td, 'archive',
                                      'macro_20260131.json.gz'))
      and 'macro_20261108.json' in rep6['kept']
      and os.path.isfile(os.path.join(td, 'macro_20261108.json')))
check("研究层档不被保留策略触碰(不删/不归档,仍在采集目录)",
      not any('research_snapshot' in x for x in
              rep6['deleted'] + rep6['archived'] + rep6['protected_archived'])
      and os.path.isfile(os.path.join(td, 'research_snapshot_20260125.json')))
notes1 = []
probs1 = rp.sources_status_problems(SS, target_ymd='20260125', data_dir=td,
                                    trusted_root=root6, notes=notes1)
check("清理后: 声明档已归档→仍 CLEAN(归档读回+sha256一致)",
      probs1 == [], str(probs1[:2]))
check("清理后: 归档事实入 notes(可溯源底线=删除前必有归档可读回)",
      any('archive/macro_20260120.json.gz 在场且可读回' in n
          and 'sha256与构建时一致' in n for n in notes1), str(notes1))
raw6 = rp.read_archived_source(td, 'macro_20260120.json')
check("read_archived_source: 解压字节=原档字节(sha256口径=未压缩)",
      raw6 == mac_bytes
      and hashlib.sha256(raw6).hexdigest() == mac_digest)
check("read_archived_source: 不存在→None;路径成分经basename归一(不越界)",
      rp.read_archived_source(td, 'macro_19990101.json') is None
      and rp.read_archived_source(td, '../macro_20260120.json') == mac_bytes)
# resolve_inputs 归档回退: 采集目录无窗内档→archive/*.gz 可用(archived 标记)
root6b = tempfile.mkdtemp(prefix='c7p6b-')
td2 = os.path.join(root6b, 'daily')
os.makedirs(os.path.join(td2, 'archive'))
with gzip.open(os.path.join(td2, 'archive', 'macro_20260210.json.gz'),
               'wb') as f:
    f.write(mac_bytes)
ri = sb.resolve_inputs('20260212', data_dir=td2, trusted_root=root6b)
check("resolve_inputs 归档回退: 窗内无现行档→取归档(lag2≤7,archived=True)",
      isinstance(ri['macro'], dict) and ri['macro']['archived'] is True
      and ri['macro']['file'].endswith('macro_20260210.json.gz')
      and ri['macro']['file_date'] == '20260210'
      and ri['macro']['lag_days'] == 2 and ri['macro']['exact'] is False,
      str(ri['macro']))
ri_out = sb.resolve_inputs('20260301', data_dir=td2, trusted_root=root6b)
check("resolve_inputs 归档回退: 过窗归档不冒充(20260210→0301 lag19>7→缺)",
      ri_out['macro'] is None, str(ri_out['macro']))
# load_metric_series: 归档档 gzip 读回(老日期研究查询优雅降级)
root6c = tempfile.mkdtemp(prefix='c7p6c-')
td3 = os.path.join(root6c, 'daily')
os.makedirs(os.path.join(td3, 'archive'))
with gzip.open(os.path.join(td3, 'archive', 'macro_20260120.json.gz'),
               'wb') as f:
    f.write(mac_bytes)
ser = rhq.load_metric_series('UST_10Y', '20260121', data_dir=td3,
                             trusted_root=root6c)
check("load_metric_series: 归档读回=解压后序列(3观测+sha256=未压缩口径)",
      ser['dates'] == ['2026-01-10', '2026-01-15', '2026-01-20']
      and ser['source']['file'] == 'macro_20260120.json.gz'
      and ser['source']['sha256'] == mac_digest,
      str(ser.get('source')))

# ══ [7] Charter7-7: 新闻摘要模型门(显式 opt-in,默认关闭) ═════════
print("\n[7] 新闻摘要模型门(IA_NEWS_MODEL_SUMMARY 独立显式 opt-in)")
MODE = nc.news_model_summary_mode
_ENV_COMPLETE = {'MODEL_API_KEY': 'FAKE_KEY_C7', 'MODEL_BASE_URL':
                 'https://fake.invalid/v1', 'MODEL_NAME': 'fake-c7'}
_ENV_BLANK = {'MODEL_API_KEY': '', 'MODEL_BASE_URL': '', 'MODEL_NAME': ''}
with mock.patch.dict(os.environ, {**_ENV_COMPLETE}, clear=False):
    os.environ.pop('IA_NEWS_MODEL_SUMMARY', None)
    m_no, b_no = MODE()
    os.environ['IA_NEWS_MODEL_SUMMARY'] = '0'
    m_zero, _ = MODE()
    os.environ['IA_NEWS_MODEL_SUMMARY'] = '1'
    m_yes, b_yes = MODE()
with mock.patch.dict(os.environ, {**_ENV_BLANK,
                                  'IA_NEWS_MODEL_SUMMARY': '1'}, clear=False):
    m_inc, b_inc = MODE()
check("三参齐备+未显式开启→off_optin(**不再自动调用**,审计#7主断言)",
      m_no == 'off_optin' and '默认关闭' in b_no, f"{m_no} {b_no}")
check("开关设0≠1→仍 off_optin(显式=1唯一开启形态)", m_zero == 'off_optin')
check("显式开启+三参不齐→off_incomplete(如实说明)",
      m_inc == 'off_incomplete' and '三参不齐' in b_inc, b_inc)
check("显式开启+三参齐备→model(唯一调用形态)",
      m_yes == 'model' and '显式开启' in b_yes, b_yes)

# 零调用计数器(真实 nc.run 流程,外部源全mock)
class _FakeFH:
    def __init__(self, market):
        self._m = market

    def general_news(self, cat, min_id=0):
        return self._m

    def company_news(self, symbol, _from=None, to=None):
        return []


class _EmptyFeed:
    entries = []

    def parse(self, url):
        return self


class _FrozenDT(datetime):
    @classmethod
    def now(cls, tz=None):
        b = datetime(2026, 10, 30, 5, 30)
        return b if tz is None else b.replace(tzinfo=tz)

    @classmethod
    def utcnow(cls):
        return datetime(2026, 10, 30, 5, 30)

    @classmethod
    def today(cls):
        return datetime(2026, 10, 30, 5, 30)


import calendar                    # noqa: E402
import feedparser                  # noqa: E402
_EPOCH_OK = calendar.timegm((2026, 10, 28, 12, 0, 0, 0, 0, 0))
_MKT = [{'id': 9001, 'headline': 'Fed holds rates steady in October',
         'source': 'Reuters', 'summary': 'The Federal Reserve kept '
         'interest rates unchanged.', 'url': 'https://reuters.com/fed',
         'datetime': _EPOCH_OK}]
_saved_gen = nc.generate_news_summary


def run_news_countdown(optin):
    calls = {'n': 0}

    def fake_summary(classified):
        calls['n'] += 1
        return '## 摘要\n### 美联储/利率\n- 联储按兵不动。'

    tmp = tempfile.mkdtemp(prefix='c7p7-')
    nc.DATA_DIR = os.path.join(tmp, 'data')
    env = dict(_ENV_COMPLETE)
    if optin:
        env['IA_NEWS_MODEL_SUMMARY'] = '1'
    else:
        env['IA_NEWS_MODEL_SUMMARY'] = ''
    with mock.patch.dict(os.environ, env, clear=False), \
            mock.patch.object(nc, 'fh_client', _FakeFH(_MKT)), \
            mock.patch.object(feedparser, 'parse',
                              lambda url: _EmptyFeed()), \
            mock.patch.object(nc, 'WATCH_SYMBOLS', ['NVDA']), \
            mock.patch.object(nc, 'datetime', _FrozenDT), \
            mock.patch.object(nc, 'generate_news_summary', fake_summary), \
            contextlib.redirect_stdout(io.StringIO()):
        nc.run(now_utc='2026-10-30T05:30:00Z')
    return calls['n']


n_off = run_news_countdown(False)
n_on = run_news_countdown(True)
check("流程级零调用: 三参齐备+未opt-in→generate_news_summary 调用数=0",
      n_off == 0, f"calls={n_off}")
check("流程级开启: IA_NEWS_MODEL_SUMMARY=1→恰好调用1次",
      n_on == 1, f"calls={n_on}")
nc.generate_news_summary = _saved_gen
guide = open(os.path.join(ROOT, 'docs', 'USER_GUIDE.md'),
             encoding='utf-8').read()
cli_src = open(os.path.join(ROOT, 'ia_cli.py'), encoding='utf-8').read()
check("文档锁: USER_GUIDE 含 IA_NEWS_MODEL_SUMMARY(默认关闭说明)",
      'IA_NEWS_MODEL_SUMMARY' in guide)
check("文档锁: ia_cli 源内含该开关(--yes 提示/ENV_KEYS)",
      'IA_NEWS_MODEL_SUMMARY' in cli_src)

print()
print("═" * 64)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 64)
sys.exit(0 if FAIL == 0 else 1)
