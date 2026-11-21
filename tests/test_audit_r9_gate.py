#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R9 第九轮审计修复回归(R9-01 有效观测规则覆盖全部数据路径 /
R9-02 时间要求无法解析时明确阻断)。

外审反例(基线 a4fb7c7 复现,/tmp/r9_repro.py 八例全 BASELINE-BUG):
  R9-01 快照直读与 max_available 绕过统一清洗——「研究 CN_PMI_MFG 的
     变化」(未限定)以下输入全被记 n=226、satisfied、报告归档通过:
     ①226 日期值全 NaN;②全 Infinity;③全 null;④225 null+仅末值
     有效;⑤226 条同一天重复观测(有效去重 1)。快照路径
     merge_macro_series/工作台 metric_series/判定器均直信原始数组。
  R9-01b S4 信封声明 n 被信任(declared n=226+全 NaN 数组 → satisfied)。
  R9-02A 「研究前年 CN_PMI_MFG 的变化」: 无匹配日期词形→返回 None→
     与「没有时间要求」混同,12 个月数据经 max_available 交付(2024 无
     数据)。
  R9-02B 「研究过去六个月 …」: 2021-11 前史+2026-10 一点共 168 点,
     最近六个月仅 1 点,仍 max_available 交付。

修复判据:
  §M(R9-01) 唯一有效观测规则覆盖全部数据路径——交叉矩阵:
     数据路径{快照(merge_macro_series→series_store→工作台/判定),
     采集档(生产采集→loader→信封)}×任务范围{明确时间窗口(近五年),
     未限定(max_available)}×数据状态{正常真实序列, 全 NaN, 全
     ±Infinity, 全空值, values 长度错配, 仅 1 个有效观测, 大量重复
     日期, 合理少量缺失};n/first/last 取自最终有效序列;不足即阻断
     report/archive;信封声明 n 不采信。
  §Y(R9-02) 三态固定: 未指定(唯一允许 max_available)/已解析(ISO·
     斜杠·近 N 年·近 N 个月·去年·前年·以来·截至)/已指定但无法
     解析(未支持时间词→明确阻断+改写提示,相对词绑定研究时点,
     资产名不误配)。
  §G 生产入口双门: 坏快照规格/前年误放行规格/近六月误放行规格 →
     report 拒交付+archive 拒归档;近六月全量正例可交付。
  §S 披露面: 快照核验披露(series_store_clean)/查询 series_clean
     (raw_n+六键)/合法数值原始精度保留。

判定=逐 check 打印+exit code(0=全过)。合成裁决仅用于本门测试的身份
标记,不冒充真实独立审查。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import agent_judgment as aj          # noqa: E402
import research_orchestrator as ro   # noqa: E402
import china_market_collector as cmc  # noqa: E402
import macro_collector as mc         # noqa: E402
import research_history_query as rhq  # noqa: E402
import snapshot_builder as sb        # noqa: E402
import workbench_data as wd          # noqa: E402

PASS, FAIL = 0, 0


def check(name, cond, detail=''):
    global PASS, FAIL
    print(f"  {'✅' if cond else '❌'} {name}" + (f" — {detail}" if detail and not cond else ''))
    PASS = PASS + (1 if cond else 0)
    FAIL = FAIL + (0 if cond else 1)


def monthrange(y0, m0, y1, m1):
    out, y, m = [], y0, m0
    while (y, m) <= (y1, m1):
        out.append('%04d-%02d-01' % (y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


FULL_D = monthrange(2008, 1, 2026, 10)          # 226 月
FULL_V = [round(50.0 + (i % 7) * 0.07, 2) for i in range(226)]

# 合理少量缺失: 3 个窗外月 + 3 个窗内月 null(近五年窗内 59−3=56)
_MISSING_MONTHS = ('2010-03-01', '2015-07-01', '2020-02-01',
                   '2023-04-01', '2025-06-01', '2026-08-01')
_V_FEW_MISSING = [None if d in _MISSING_MONTHS else v
                  for d, v in zip(FULL_D, FULL_V)]

# 八状态(交叉矩阵×两路径×两范围): name, values, dates, 全量有效 n
# len_mismatch=226 值/227 日期(尾部多一未配对日期→短侧配对+登记 1,
# 有效 226=完整序列,不与 staleness 混流;尾截断变体单列 M-mm2)
STATES = [
    ('normal', FULL_V, FULL_D, 226),
    ('all_nan', ['NaN'] * 226, FULL_D, 0),
    ('all_inf', ['Infinity'] * 226, FULL_D, 0),
    ('all_null', [None] * 226, FULL_D, 0),
    ('len_mismatch', FULL_V, FULL_D + ['2026-11-01'], 226),
    ('only_1_valid', [None] * 225 + [50.5], FULL_D, 1),
    ('mass_dup', [50.0 + i * 0.01 for i in range(226)],
     ['2026-10-01'] * 226, 1),
    ('few_missing', _V_FEW_MISSING, FULL_D, 220),
]
# 期望 outcome: (明确窗口 近五年, 未限定)
EXPECT = {'normal': ('satisfied', 'satisfied'),
          'all_nan': ('insufficient_coverage', 'insufficient_coverage'),
          'all_inf': ('insufficient_coverage', 'insufficient_coverage'),
          'all_null': ('insufficient_coverage', 'insufficient_coverage'),
          'len_mismatch': ('satisfied', 'satisfied'),
          'only_1_valid': ('insufficient_coverage', 'insufficient_coverage'),
          'mass_dup': ('insufficient_coverage', 'insufficient_coverage'),
          'few_missing': ('satisfied', 'satisfied')}


# ══ 路径A: 快照(生产 build 链 merge_macro_series → series_store) ══
def _snap_with(values, dates=None):
    ds = dates if dates is not None else FULL_D
    raw = {'macro': {'data': {'CN_PMI_MFG': {
        'series': {'dates': ds, 'values': values},
        'provenance': {'source': 'akshare_em(macro_china_pmi)',
                       'fetched_at': '2026-11-17T12:00:00Z',
                       'coverage': {'n': len(ds)}}}}}}
    store, prov, clean = {}, {}, {}
    sb.merge_macro_series(store, raw, prov_out=prov, clean_out=clean)
    return {'series_store': store, 'series_provenance': prov,
            **({'series_store_clean': clean} if clean else {}),
            'target_date': '2026-11-17'}


def _eval_snap(snap, question, as_of='2026-11-17'):
    return ro._evaluate_data_requirements(
        ['CN_PMI_MFG'], [], snap, [], question=question,
        registry={'CN_PMI_MFG': {'frequency': 'monthly'}})[0]


# ══ 路径B: 采集档(生产采集→loader→信封;与 R8 门同形 harness) ══
def _cn_item(values, y0, m0, y1, m1, dates=None,
             fetched_at='2026-11-17T02:00:00Z'):
    ds = dates if dates is not None else monthrange(y0, m0, y1, m1)
    return {'date': ds[-1], 'value': 50.0, 'prev': 49.8,
            'frequency': 'monthly', 'unit': 'index_point',
            'series': {'dates': ds, 'values': values},
            'provenance': {'source': 'akshare_em(macro_china_pmi)',
                           'fetched_at': fetched_at,
                           'coverage': {'n': len(ds)}}}


def _new_data_root():
    d = tempfile.mkdtemp(prefix='r9g_')
    os.makedirs(os.path.join(d, 'data', 'daily'))
    os.makedirs(os.path.join(d, 'config'))
    shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
                os.path.join(d, 'config', 'metric_registry.json'))
    return d


def _run_round(droot, pmi_item):
    mc.DATA_DIR = os.path.join(droot, 'data')
    cmc.fetch_macro_history = lambda: {
        'CN_PMI_MFG': json.loads(json.dumps(pmi_item)),
        'CN_NEW_LOANS': json.loads(json.dumps(
            _cn_item([12345.0] * 226, 2008, 1, 2026, 10)))}
    results = {'HY_OAS': {'value': 3.1, 'date': '2026-11-13',
                          'frequency': 'daily'}}
    results, _ = mc.merge_cn_history(results, data_dir=mc.DATA_DIR)
    mc.save_macro(results, [], {}, cn_history=_)


def _latest_ymd(droot):
    files = sorted(os.listdir(os.path.join(droot, 'data', 'daily')))
    return [f for f in files if f.startswith('macro_')][-1][6:14]


def _query(droot):
    return rhq.load_metric_series(
        'CN_PMI_MFG', _latest_ymd(droot),
        data_dir=os.path.join(droot, 'data', 'daily'), trusted_root=droot)


def _eval_item(droot, question, as_of='2026-11-17'):
    res = _query(droot)
    env_series = {'n': len(res['dates']),
                  'source': f"采集档 {res['source']['file']}",
                  'frequency': res['frequency'],
                  'first': res['dates'][0] if res['dates'] else None,
                  'last': res['dates'][-1] if res['dates'] else None,
                  'dates': res['dates'], 'values': res['values']}
    if res.get('series_clean'):
        env_series['series_clean'] = res['series_clean']
    if res.get('collection_status'):
        env_series['collection_status'] = res['collection_status']
    step = {'step': 'S4_history_CN_PMI_MFG', 'ok': True,
            'envelope': {'data': {'series': env_series}}}
    return ro._evaluate_data_requirements(
        ['CN_PMI_MFG'], [step], {'target_date': as_of}, [],
        question=question,
        registry={'CN_PMI_MFG': {'frequency': 'monthly'}})[0]


# ══════════════════════════════════════════════════════════════════
print('§M R9-01 交叉矩阵: 路径{快照,采集档}×范围{近五年,未限定}×八状态')

Q_EXPLICIT = '研究近五年 CN_PMI_MFG 的变化'
Q_UNSPEC = '研究 CN_PMI_MFG 的变化'

# 预计算窗内有效期望(月频,窗起≈2021-11-16,首窗内观测 2021-12-01)
_IN_WIN_N = {'normal': 59, 'len_mismatch': 59, 'few_missing': 56,
             'only_1_valid': 1, 'mass_dup': 1}

snap_items = {}      # (state, range) -> eval item(供 §G 复用)
for name, vals, dates, n_eff in STATES:
    snap = _snap_with(vals, dates)
    ms, err = wd.metric_series('CN_PMI_MFG', snap, ROOT) if \
        snap['series_store'] else (None, 'absent')
    wb_n = len(ms['dates']) if ms else 0
    r_ex = _eval_snap(snap, Q_EXPLICIT)
    r_un = _eval_snap(snap, Q_UNSPEC)
    snap_items[(name, 'ex')] = r_ex
    snap_items[(name, 'un')] = r_un
    ok_out = (r_ex['outcome'] == EXPECT[name][0]
              and r_un['outcome'] == EXPECT[name][1])
    ok_n = True
    if name in _IN_WIN_N and r_ex['outcome'] == 'satisfied':
        ok_n = ((r_ex['spec'].get('window') or {})
                .get('n_in_window') == _IN_WIN_N[name])
    if n_eff > 1:                       # 工作台面同规则(全坏值面=0)
        ok_n = ok_n and wb_n == n_eff
    else:
        ok_n = ok_n and wb_n in (n_eff, 0)
    cov_n = ((r_un['spec'].get('coverage_observed') or {}).get('n'))
    if r_un['outcome'] == 'satisfied':
        ok_n = ok_n and cov_n == n_eff
    check(f'M-snap[{name}] 快照路径 双范围判定+n={n_eff}',
          ok_out and ok_n,
          f"ex={r_ex['outcome']} un={r_un['outcome']} wb={wb_n} "
          f"cov={cov_n} n_in_win="
          f"{(r_ex['spec'].get('window') or {}).get('n_in_window')}")

# 采集档路径(每状态独立数据树)
for name, vals, dates, n_eff in STATES:
    d = _new_data_root()
    _run_round(d, _cn_item(vals, 2008, 1, 2026, 10, dates=dates))
    q = _query(d)
    r_ex = _eval_item(d, Q_EXPLICIT)
    r_un = _eval_item(d, Q_UNSPEC)
    ok_out = (r_ex['outcome'] == EXPECT[name][0]
              and r_un['outcome'] == EXPECT[name][1])
    ok_n = len(q['dates']) == n_eff
    if name in _IN_WIN_N and r_ex['outcome'] == 'satisfied':
        ok_n = ok_n and (r_ex['spec'].get('window') or {}) \
            .get('n_in_window') == _IN_WIN_N[name]
    check(f'M-coll[{name}] 采集档路径 双范围判定+n={n_eff}',
          ok_out and ok_n,
          f"ex={r_ex['outcome']} un={r_un['outcome']} "
          f"q_n={len(q['dates'])}")

# M-mm2 尾截断错配(226 日期/225 值→丢最新观测): 短侧配对后窗内末
# 观测 2026-09-01 越窗止容忍→显式窗阻断;未限定路径 freshest 缺席→
# stale_for_task(R7-02 三级阻断)——首跑曾按 satisfied 预期失败,复核
# 为生产正确判定(错配吞最新值=新鲜度与端覆盖据实失败),期望据实修正。
snap_mm2 = _snap_with(FULL_V[:-1])
r_mm2_ex = _eval_snap(snap_mm2, Q_EXPLICIT)
r_mm2_un = _eval_snap(snap_mm2, Q_UNSPEC)
dmm2 = _new_data_root()
_run_round(dmm2, _cn_item(FULL_V[:-1], 2008, 1, 2026, 10))
r_mm2c_ex = _eval_item(dmm2, Q_EXPLICIT)
r_mm2c_un = _eval_item(dmm2, Q_UNSPEC)
check('M-mm2 尾截断错配(丢最新值)→ 显式窗窗止容忍阻断+未限定 stale_for_task',
      r_mm2_ex['outcome'] == 'insufficient_coverage'
      and '早于窗止' in r_mm2_ex['outcome_basis']
      and r_mm2_un['outcome'] in ('insufficient_coverage', 'stale_for_task')
      and r_mm2c_ex['outcome'] == 'insufficient_coverage'
      and r_mm2c_un['outcome'] in ('insufficient_coverage', 'stale_for_task'),
      f"snap ex={r_mm2_ex['outcome'][:12]} un={r_mm2_un['outcome']} "
      f"coll ex={r_mm2c_ex['outcome'][:12]} un={r_mm2c_un['outcome']}")

# M-b: 信封声明 n 不采信(声明 226+全 NaN 数组 → 阻断,基线误 satisfied)
env = {'n': 226, 'source': '采集档', 'frequency': 'monthly',
       'first': FULL_D[0], 'last': FULL_D[-1],
       'dates': FULL_D, 'values': ['NaN'] * 226}
step = {'step': 'S4_history_CN_PMI_MFG', 'ok': True,
        'envelope': {'data': {'series': env}}}
r_env = ro._evaluate_data_requirements(
    ['CN_PMI_MFG'], [step], {'target_date': '2026-11-17'}, [],
    question=Q_UNSPEC,
    registry={'CN_PMI_MFG': {'frequency': 'monthly'}})[0]
check('M-b 信封声明 n=226+全 NaN 数组 → 阻断(声明 n 不采信)',
      r_env['outcome'] == 'insufficient_coverage'
      and '有效观测 0' in r_env['outcome_basis'],
      f"outcome={r_env['outcome']} basis={r_env['outcome_basis'][:60]}")

# M-c: 快照核验披露节在场(全 NaN 面=面在场有效 0,不误标均缺席)
snap_bad = _snap_with(['NaN'] * 226)
r_bad = _eval_snap(snap_bad, Q_UNSPEC)
check('M-c 快照全 NaN 未限定 → 据实「序列面在场但有效观测 0」',
      r_bad['outcome'] == 'insufficient_coverage'
      and '序列面在场但有效观测 0' in r_bad['outcome_basis']
      and snap_bad.get('series_store_clean', {}).get('CN_PMI_MFG',
                                                     {}).get('raw_n') == 226,
      f"outcome={r_bad['outcome']} basis={r_bad['outcome_basis'][:60]}")


# ══════════════════════════════════════════════════════════════════
print('§Y R9-02 时间要求三态(未指定/已解析/无法解析)')

# Y1 反例A: 「前年」+12 个月数据 → 2024 自然年窗,窗内 0 阻断
dA = _new_data_root()
_run_round(dA, _cn_item([50.0 + i * 0.1 for i in range(12)], 2025, 11, 2026, 10))
yA = _eval_item(dA, '研究前年 CN_PMI_MFG 的变化')
check('Y1 反例A「前年」+12 月数据 → 窗 2024 阻断(不落 max_available)',
      yA['outcome'] == 'insufficient_coverage'
      and (yA['spec'].get('window') or {}).get('start') == '2024-01-01'
      and (yA['spec'].get('window') or {}).get('end') == '2024-12-31'
      and yA['spec'].get('window') != 'max_available',
      f"outcome={yA['outcome']} win={yA['spec'].get('window')}")

# Y2 反例B: 「过去六个月」+168 点(前史+一点) → 相对月窗,窗内 1 阻断
dB = _new_data_root()
dB_dates = monthrange(2008, 1, 2021, 11) + ['2026-10-01']
_run_round(dB, _cn_item([50.0 + (i % 5) * 0.1 for i in range(168)],
                        2008, 1, 2021, 11, dates=dB_dates))
yB = _eval_item(dB, '研究过去六个月 CN_PMI_MFG 的变化')
check('Y2 反例B「过去六个月」+168 点 → 窗 2026-05-17..2026-11-17 窗内 1 阻断',
      yB['outcome'] == 'insufficient_coverage'
      and (yB['spec'].get('window') or {}).get('start') == '2026-05-17'
      and (yB['spec'].get('window') or {}).get('n_in_window') == 1
      and yB['spec'].get('window') != 'max_available',
      f"outcome={yB['outcome']} win={yB['spec'].get('window')}")

# Y3 前置: 全量数据树(判定层词形阻断与数据无关,正例树复用)
dF = _new_data_root()
_run_round(dF, _cn_item(FULL_V, 2008, 1, 2026, 10))

# Y3 未支持时间表达 → unparseable+提示,判定层阻断(非两特例)
_UNSUPPORTED = ['今年', '明年', '后年', '大前年', '上半年', '下半年',
                '年初', '年末', '上季度', '本季度', '上周', '本周',
                '上个月', '本月', '近三十天', '过去2周', '未来三个月',
                '六天内', '接下来两年']
y3_parse = all(
    (lambda w: w is not None and w['kind'] == 'unparseable'
     and w.get('hint'))(ro._question_window(f'研究{w_} CN_PMI_MFG 的变化'))
    for w_ in _UNSUPPORTED)
y3_eval_items = [
    _eval_item(dF, f'研究{w_} CN_PMI_MFG 的变化')
    for w_ in ('今年', '上周', '近三十天', '未来三个月')]
y3_eval = all(r['outcome'] == 'insufficient_coverage'
              and '未支持' in r['outcome_basis']
              and '改用明确日期区间' in r['outcome_basis']
              for r in y3_eval_items)
check('Y3 未支持时间表达({}个)→ 解析 unparseable+提示;判定层阻断'.format(
          len(_UNSUPPORTED)),
      y3_parse and y3_eval,
      f"parse={y3_parse} eval={y3_eval}")

# Y4 资产名护栏: 期限/周期词不误配任务时间
y4 = all(ro._question_window(q) is None for q in (
    '十年期美债收益率上行的传导', '上周期值与本周期的对比',
    '中美利差走阔的影响', '十年期与两年期国债利差'))
check('Y4 资产名护栏(十年期/上周期/中美)→ 未指定范围',
      y4 and ro._question_range_years('UST_10Y 十年期美债利率上行的传导') is None,
      f"y4={y4}")

# Y5 正例保留+新词形全量数据
y5_cases = {
    'iso': '研究 2020-01-01 至 2025-12-31 的 CN_PMI_MFG 变化',
    'slash': '研究 2020/01/01 至 2025/12/31 的 CN_PMI_MFG 变化',
    '5y': '研究近五年 CN_PMI_MFG 的变化',
    '10y': '研究近十年 CN_PMI_MFG 的变化',
    'last_year': '研究去年 CN_PMI_MFG 的变化',
    'qy': '研究前年 CN_PMI_MFG 的变化',
    '6m': '研究过去六个月 CN_PMI_MFG 的变化',
    'since': '研究 2021-01-01 以来 CN_PMI_MFG 的变化',
    'until': '研究截至2025年12月的 CN_PMI_MFG 变化',
    'unspec': '研究 CN_PMI_MFG 的变化',
}
y5 = {k: _eval_item(dF, q) for k, q in y5_cases.items()}
y5_replay = _eval_item(dF, '研究近五年 CN_PMI_MFG 的变化', as_of='2021-01-15')
check('Y5 正例保留: ISO/斜杠/近五年/近十年/去年/前年/过去六个月/'
      '以来/截至/未限定/合法回放 全 satisfied',
      all(v['outcome'] == 'satisfied' for v in y5.values())
      and y5_replay['outcome'] == 'satisfied'
      and (y5['qy']['spec'].get('window') or {}).get('start') == '2024-01-01'
      and (y5['qy']['spec'].get('window') or {}).get('n_in_window') == 12
      and (y5['6m']['spec'].get('window') or {}).get('start') == '2026-05-17'
      and (y5['6m']['spec'].get('window') or {}).get('n_in_window') == 5
      and (y5['unspec']['spec'].get('window') == 'max_available'),
      ' '.join(f"{k}={v['outcome']}" for k, v in y5.items())
      + f" replay={y5_replay['outcome']}")

# Y6 相对月窗绑定研究时点: 时点不可核验 → 窗口不可核验阻断(非系统时间)
y6 = ro._evaluate_data_requirements(
    ['CN_PMI_MFG'],
    [{'step': 'S4_history_CN_PMI_MFG', 'ok': True,
      'envelope': {'data': {'series': {
          'n': 226, 'source': '采集档', 'frequency': 'monthly',
          'dates': FULL_D, 'values': FULL_V}}}}],
    {}, [], question='研究过去六个月 CN_PMI_MFG 的变化',
    registry={'CN_PMI_MFG': {'frequency': 'monthly'}})[0]
check('Y6 研究时点不可核验+过去六个月 → 相对月窗不可核验阻断',
      y6['outcome'] == 'insufficient_coverage'
      and '相对月窗无法判定' in y6['outcome_basis'],
      f"outcome={y6['outcome']} basis={y6['outcome_basis'][:60]}")

# Y7 解析器词形: 前年→offset-2;大前年→未支持;月数词形三态
w_qy = ro._question_window('研究前年 CN_PMI_MFG 的变化')
w_dqy = ro._question_window('研究大前年 CN_PMI_MFG 的变化')
w_6m = ro._question_window('研究近六个月 CN_PMI_MFG 的变化')
w_6m_in = ro._question_window('研究六个月内 CN_PMI_MFG 的变化')
w_12m = ro._question_window('研究过去12个月 CN_PMI_MFG 的变化')
check('Y7 解析器: 前年=-2/大前年=未支持/近六个月·六个月内·过去12个月=relative_months',
      w_qy == {'kind': 'calendar_year', 'offset': -2, 'raw': '前年'}
      and w_dqy is not None and w_dqy['kind'] == 'unparseable'
      and w_6m == {'kind': 'relative_months', 'months': 6}
      and w_6m_in == {'kind': 'relative_months', 'months': 6}
      and w_12m == {'kind': 'relative_months', 'months': 12},
      f"qy={w_qy} dqy={w_dqy} 6m={w_6m} 6min={w_6m_in} 12m={w_12m}")


# ══════════════════════════════════════════════════════════════════
print('§G 生产入口双门(report/archive 同判据源)')


def make_run(tmp, name, *, req_items=None):
    global _RUN_SEQ
    _RUN_SEQ += 1
    run_ts = '20261117T21%04dZ' % _RUN_SEQ
    rd = os.path.join(tmp, name)
    os.makedirs(rd, exist_ok=True)
    rows = [{'metric_id': 'TEST_M%d' % i, 'value': 1.0 * i, 'unit': 'x',
             'observation_date': '2026-11-09', 'quality_status': 'OK',
             'source': {'id': 'src%d' % i, 'kind': 'synthetic'}}
            for i in range(2)]
    report = {
        'schema_version': '2.0', 'pipeline_version': 't',
        'run': {'question': 'Audit-R9 回归合成问题', 'ts_utc': run_ts,
                'git_head': 'synthetic', 'degradation_policy': {}},
        'steps': [], 'fanout': {},
        'layers': {
            'L1_事实层': {'rows': rows, 'available': True,
                         'n': 2, 'note': '合成: 无事实行'},
            'L2_机构观点层': {'views': {'available': False, 'n': 0,
                                        'note': '合成: 观点库缺席'}},
            'L3_AI推断层': {'produced': True, 'attribution': 'ai_inferred',
                           'note': '合成: L3 注记'},
            'L4_条件情景层': {'produced': True, 'attribution': 'ai_inferred',
                           'note': '合成: L4 注记'}},
        'evidence_index': [{'kind': 'metric', 'ref': 'TEST_M0@2026-11-09'},
                           {'kind': 'metric', 'ref': 'TEST_M1@2026-11-09'}],
        'notes': [], 'run_ok': True,
        'agent_judgment': {
            'attached': True, 'judgment_file': 'judgment.json',
            'validation': {'passed': True, 'violations': []},
            'run_ok_at_attach': True, 'allow_failed_run': False}}
    if req_items is not None:
        report['run']['data_requirements'] = {
            'frozen_at': 'plan(采集前冻结;分类与规格不随采集结果改判)',
            'items': req_items,
            'optional_face': {'tier': 'optional'}}
    json.dump(report, open(os.path.join(rd, 'report.json'), 'w',
                           encoding='utf-8'), ensure_ascii=False)
    json.dump({'schema_version': aj.JUDGMENT_SCHEMA_VERSION,
               'agent_declaration': {'role': 'synthetic'},
               'l3': {'claims': []}, 'l4': {'scenarios': []}},
              open(os.path.join(rd, 'agent_judgment.json'), 'w',
                   encoding='utf-8'), ensure_ascii=False)
    open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8').write(
        ro._render_md(report))
    json.dump({'n': 1, 'note': 'views 库在场', 'views': [
        {'view_id': 'V-2026-001', 'institution_name': '机构A',
         'publish_date': '2026-11-01', 'report_title': '标题',
         'core_views': ['主张'], 'forecasts': [], 'risk_factors': []}]},
        open(os.path.join(rd, 'views_digest.json'), 'w', encoding='utf-8'),
        ensure_ascii=False)
    return rd


_RUN_SEQ = 0


def stage_report(rd, engine_root):
    r = subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'report',
         '--report-dir', rd, '--engine-root', engine_root],
        cwd=ROOT, capture_output=True, text=True, timeout=180)
    e = json.loads(r.stdout)
    e['_warnings'] = e.get('warnings') or []
    return e['data']


def stage_archive(rd, engine_root, arc):
    return subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'archive',
         '--report-dir', rd, '--engine-root', engine_root,
         '--archive-dir', arc],
        cwd=ROOT, capture_output=True, text=True, timeout=180)


tmpG = tempfile.mkdtemp(prefix='r9gate_')
eroot = os.path.join(tmpG, 'engine')
os.makedirs(os.path.join(eroot, 'config'), exist_ok=True)
shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
            os.path.join(eroot, 'config', 'metric_registry.json'))

# G1 坏快照规格(全 NaN 未限定)→ report 拒+archive 拒
rdG1 = make_run(tmpG, 'g1', req_items=[snap_items[('all_nan', 'un')]])
eG1 = stage_report(rdG1, eroot)
aG1 = stage_archive(rdG1, eroot, os.path.join(tmpG, 'arcG1'))
check('G1 快照全 NaN 规格 → report 拒交付+archive 拒归档',
      eG1.get('deliverable') is False
      and eG1.get('blocked_class') == 'required_data_missing'
      and aG1.returncode != 0,
      f"bc={eG1.get('blocked_class')} deliv={eG1.get('deliverable')} "
      f"rc={aG1.returncode}")

# G2 「前年」误放行规格 → 双拒
rdG2 = make_run(tmpG, 'g2', req_items=[yA])
eG2 = stage_report(rdG2, eroot)
aG2 = stage_archive(rdG2, eroot, os.path.join(tmpG, 'arcG2'))
check('G2 「前年」12 月数据规格 → report 拒+archive 拒',
      eG2.get('deliverable') is False
      and eG2.get('blocked_class') == 'required_data_missing'
      and aG2.returncode != 0,
      f"bc={eG2.get('blocked_class')} rc={aG2.returncode}")

# G3 「过去六个月」误放行规格 → 双拒
rdG3 = make_run(tmpG, 'g3', req_items=[yB])
eG3 = stage_report(rdG3, eroot)
aG3 = stage_archive(rdG3, eroot, os.path.join(tmpG, 'arcG3'))
check('G3 「过去六个月」168 点规格 → report 拒+archive 拒',
      eG3.get('deliverable') is False
      and eG3.get('blocked_class') == 'required_data_missing'
      and aG3.returncode != 0,
      f"bc={eG3.get('blocked_class')} rc={aG3.returncode}")

# G4 「过去六个月」全量正例 → 可交付(正例对照)
rdG4 = make_run(tmpG, 'g4', req_items=[y5['6m']])
aj.record_semantic_verdict(eroot, rdG4, 'UPHELD', 'R9-GATE')
eG4 = stage_report(rdG4, eroot)
check('G4 「过去六个月」全量 → 可交付(正例对照)',
      eG4.get('blocked_class') != 'required_data_missing'
      and eG4.get('deliverable') is True,
      f"bc={eG4.get('blocked_class')} deliv={eG4.get('deliverable')}")


# ══════════════════════════════════════════════════════════════════
print('§S 披露面(核验披露/查询清洗登记/精度保留)')

# S1 双层披露: 建档面 series_store_clean 记错配(226 值/227 日期);
# 读面 metric_series series_clean 记建档后数组(n=226 全有效)
snap_mm = _snap_with(FULL_V, FULL_D + ['2026-11-01'])
ms_mm, err_mm = wd.metric_series('CN_PMI_MFG', snap_mm, ROOT)
sc_build = snap_mm.get('series_store_clean', {}).get('CN_PMI_MFG', {})
sc_mm = ms_mm['series_clean'] if ms_mm else {}
check('S1 错配双层披露: 建档面 mismatch=1(raw_n=227→226)+读面 n=226',
      ms_mm is not None and len(ms_mm['dates']) == 226
      and sc_build.get('raw_n') == 227
      and sc_build.get('n_length_mismatch') == 1
      and sc_build.get('n_observations') == 226
      and sc_mm.get('n_observations') == 226,
      f"err={err_mm} build={sc_build} read={sc_mm}")

# S2 建档核验披露节 series_store_clean(全 NaN 面在场有效 0)
sc2 = snap_bad.get('series_store_clean', {}).get('CN_PMI_MFG', {})
check('S2 快照 series_store_clean: raw_n=226/n_observations=0/n_nonfinite=226',
      sc2.get('raw_n') == 226 and sc2.get('n_observations') == 0
      and sc2.get('n_nonfinite_dropped') == 226,
      str(sc2))

# S3 重复日期去重留末值: 合法数值原始精度逐位保留(快照路径)
snap_dup = _snap_with(FULL_V + [50.123456789123],
                      dates=FULL_D + ['2026-10-01'])
ms_dup, _ = wd.metric_series('CN_PMI_MFG', snap_dup, ROOT)
check('S3 快照重复日期(227 含 1 重复)→ 去重 226+末值精度逐位保留',
      ms_dup is not None and len(ms_dup['dates']) == 226
      and ms_dup['values'][-1] == 50.123456789123,
      f"n={len(ms_dup['dates']) if ms_dup else None} "
      f"last={ms_dup['values'][-1] if ms_dup else None!r}")


print('─' * 64)
print(f'Audit-R9 判定: {PASS} PASS / {FAIL} FAIL')
sys.exit(0 if FAIL == 0 else 1)
