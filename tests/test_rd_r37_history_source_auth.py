#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R37: historical_coverage_audit 序列权威 history_source 优先(R25 审计 Ni-5)。

缺陷(Ni-5): 审计按注册表 source 声明通道判序列事件权威——DFF source=
rate_expectations(单点权威),而 R25 拉取的日频序列(n=3650,2016→2026)落
macro 通道(data.DFF.series)→序列事件全判非权威→auth_dates 空→覆盖面
保守低报(非假绿: 拒绝虚报方向的错误,但真实历史被降级)。

修法: 序列事件权威=history_source 优先,回落 source(与 workbench_data/
research_history_query R25 装载口径一致);点事件权威不变(声明通道=单点
采集面);build_metric_record 的 authority_channel 同口径。无 history_source
指标零漂移(auth_series_of==auth_of)。

全合成通道档+真实注册表;CI 干净 clone 可跑。
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import historical_coverage_audit as hca  # noqa: E402

REGISTRY = os.path.join(ROOT, 'config', 'metric_registry.json')

RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok)))
    print(('PASS ' if ok else 'FAIL ') + name
          + (f'  [{detail}]' if detail and not ok else ''))


def by_id(result, mid):
    return next(r for r in result['metrics'] if r['metric_id'] == mid)


# DFF 日频序列(合成 10 obs;周中连续自然日,us_rates 日历按 NYSE 近似)
DFF_DATES = ['2026-10-05', '2026-10-06', '2026-10-07', '2026-10-08',
             '2026-10-09', '2026-10-13', '2026-10-14', '2026-10-15',
             '2026-10-16', '2026-10-19']
DFF_VALUES = [4.33] * 10


def build_fx(tag):
    tmp = tempfile.mkdtemp(prefix='r37_%s_' % tag)
    daily = os.path.join(tmp, 'data', 'daily')
    os.makedirs(daily)

    def write(name, obj):
        with open(os.path.join(daily, name), 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False)

    # macro 通道: DFF 序列(历史权威=history_source) + ICSA(无 history_source
    # 回归对照,source=macro_collector) + WTI 现货别名对照
    write('macro_20261020.json', {'date': '2026-10-20', 'data': {
        'DFF': {'value': 4.33, 'date': '2026-10-19',
                'series': {'dates': DFF_DATES, 'values': DFF_VALUES}},
        'ICSA': {'value': 219000.0, 'date': '2026-10-09',
                 'series': {'dates': ['2026-09-04', '2026-09-11',
                                      '2026-10-09'],
                            'values': [219000, 218000, 217000]}},
        'WTI': {'value': 80.5, 'date': '2026-09-17',
                'series': {'dates': ['2026-08-15', '2026-09-16'],
                           'values': [80.1, 80.5]}}}})
    # rate_economy 通道: DFF 单点(点权威=声明通道 rate_expectations)
    write('rate_economy_20261020.json', {
        'date': '2026-10-20',
        'current_rates': {'DFF': {'value': 4.33, 'date': '2026-10-19'}}})
    return tmp


fx = build_fx('main')
try:
    res, _log, code = hca.run_audit(os.path.join(fx, 'data', 'daily'),
                                    os.path.join(fx, 'out'), REGISTRY)
    check('run_audit 正常退出', code == 0, f'code={code}')

    # ── §1 DFF: 序列权威升 history_source 通道 ──────────────────────
    dff = by_id(res, 'DFF')
    c = dff['counts']
    check('DFF 序列 10 obs 全入权威计数',
          c['authority_raw_records'] >= 10,
          f'authority_raw={c["authority_raw_records"]}')
    check('DFF macro 点仍非权威(点权威=rate_economy 声明通道)',
          c['non_authority_records'] >= 1,
          f'non_auth={c["non_authority_records"]}')
    check('DFF 权威观测日来自序列(span=序列首尾)',
          dff['coverage']['first_observation_date'] == DFF_DATES[0]
          and dff['coverage']['last_observation_date'] == DFF_DATES[-1],
          f'cover={dff["coverage"]["first_observation_date"]}'
          f'..{dff["coverage"]["last_observation_date"]}')
    check('DFF authority_channel=macro(history_source 通道)',
          dff['authority_channel'] == 'macro',
          f'got={dff["authority_channel"]}')
    check('DFF 序列文件入样例(series_files_sample)',
          any('macro_' in f for f in dff['discovery']['series_files_sample']),
          f'sample={dff["discovery"]["series_files_sample"]}')
    # 序列+点同日 2026-10-19: 同值不算冲突;权威唯一观测日=序列日∪点日
    check('DFF 权威唯一观测日=10(序列)+0(点同日已并在序列内)',
          c['authority_unique_observation_dates'] == 10,
          f'got={c["authority_unique_observation_dates"]}')

    # ── §2 回归: 无 history_source 指标零漂移 ──────────────────────
    icsa = by_id(res, 'ICSA')
    check('ICSA(source=macro_collector,无 history_source)序列照常权威',
          icsa['counts']['authority_raw_records'] >= 3
          and icsa['authority_channel'] == 'macro',
          f'auth={icsa["counts"]["authority_raw_records"]}'
          f' ch={icsa["authority_channel"]}')
    wti = by_id(res, 'WTI_SPOT_M')
    check('WTI 别名(source=macro_collector)序列照常权威',
          wti['counts']['authority_raw_records'] >= 2,
          f'auth={wti["counts"]["authority_raw_records"]}')

    # ── §3 判定面: DFF 状态不再因零权威而降级 ──────────────────────
    check('DFF discovery.found=True(权威序列在场)',
          dff['discovery']['found'] is True)
    st = dff.get('status')
    check('DFF status 非 MISSING/UNREADABLE 族',
          st not in ('MISSING', 'UNREADABLE', 'DERIVED_ONLY'),
          f'status={st}')
finally:
    shutil.rmtree(fx, ignore_errors=True)

# ── 汇总 ──────────────────────────────────────────────────────────
n_pass = sum(1 for _, ok in RESULTS if ok)
n_fail = len(RESULTS) - n_pass
print('═' * 64)
print(f'结果: PASS={n_pass} FAIL={n_fail}')
print('═' * 64)
sys.exit(0 if n_fail == 0 else 1)
