#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R8 第八轮审计修复回归(R8-01 无效数值 / R8-02 时间要求 / R8-03 绑定指纹)。

外审反例(基线 25f079f 复现,/tmp/r8_repro.py 六例全 BASELINE-BUG):
  R8-01-1 PMI 226 日期 values 全 "NaN" → 有效数值 0,系统记近五年有效
     观测 59,history 通过、report/archive=true;
  R8-01-2 values 全 "Infinity" → 同样错误通过;
  R8-01-3 S4 信封保留日期、values=null → 窗口函数以 1.0 占位仍判覆盖满足;
  R8-02-1 「研究 2020/01/01 至 2025/12/31 的 CN_PMI_MFG 变化」(斜杠日期
     不识别)退化为 max_available,12 个月数据交付;
  R8-02-2 「研究去年 CN_PMI_MFG 的变化」(「去年」不识别)同上误放行;
  R8-02-3 「截至2025年12月」解析层合法单侧窗,后续因 start=null 无条件
     阻断——与声明的支持能力不一致。

修复判据:
  §V(R8-01) 有效观测=合法日期+有限数值,统一采集/清洗/查询/窗口/
     未限定范围路径: NaN/±Infinity/缺 values/长度错配/全缺失/部分缺失/
     重复日期/非法日期/正常真实数据,从真实格式原始文件进入生产查询与
     交付链路;不足即阻断 report/archive;合法数值原始精度保留。
  §W(R8-02) 三态区分(未指定/已解析/无法解析): 斜杠日期+「去年」
     (自然年绑定研究时点);单侧终界窗起=实际序列首观测(不再必然拒绝);
     保留 ISO 区间/近五年/近十年/以来/单侧正例/合法回放/无限制正例。
  §G 生产入口双门: 坏值规格与斜杠窗口规格注入 run → report 拒交付+
     archive 拒归档;单侧终界满足项可交付(正例对照)。
  §B(R8-03) _git_state 未跟踪源码入指纹: 新增/改内容/转跟踪均使指纹
     变化;CODE_VERSION 印章三级链保持。

判定=逐 check 打印+exit code(0=全过)。合成裁决仅用于本门测试的身份
标记,不冒充真实独立审查。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import agent_judgment as aj          # noqa: E402
import research_orchestrator as ro   # noqa: E402
import china_market_collector as cmc  # noqa: E402
import macro_collector as mc         # noqa: E402
import research_history_query as rhq  # noqa: E402

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


# ══ 真实格式原始文件 → 生产查询链(R8-01 验收口径) ══════════════════

def _cn_item(values, y0, m0, y1, m1, dates=None,
             fetched_at='2026-11-17T02:00:00Z'):
    ds = dates if dates is not None else monthrange(y0, m0, y1, m1)
    if values is not None and not isinstance(values, list):
        values = [values] * len(ds)
    return {'date': ds[-1], 'value': 50.0, 'prev': 49.8,
            'frequency': 'monthly', 'unit': 'index_point',
            'series': {'dates': ds, 'values': values},
            'provenance': {
                'source': 'akshare_em(macro_china_pmi)',
                'fetched_at': fetched_at,
                'coverage': {'n': len(ds), 'first': ds[0], 'last': ds[-1]},
                'generated_by': 'fetch_macro_history'}}


def _new_data_root():
    d = tempfile.mkdtemp(prefix='r8g_')
    os.makedirs(os.path.join(d, 'data', 'daily'))
    os.makedirs(os.path.join(d, 'config'))
    shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
                os.path.join(d, 'config', 'metric_registry.json'))
    return d


def _run_round(droot, pmi_item, loans_item=None):
    """经生产 save_macro+merge_cn_history 写真实格式采集档(网络注入)。"""
    mc.DATA_DIR = os.path.join(droot, 'data')
    cmc.fetch_macro_history = lambda: {
        'CN_PMI_MFG': json.loads(json.dumps(pmi_item)),
        'CN_NEW_LOANS': json.loads(json.dumps(
            loans_item or _cn_item([12345.0] * 226, 2008, 1, 2026, 10)))}
    results = {'HY_OAS': {'value': 3.1, 'date': '2026-11-13',
                          'frequency': 'daily'}}
    results, _ = mc.merge_cn_history(results, data_dir=mc.DATA_DIR)
    mc.save_macro(results, [], {}, cn_history=_)


def _latest_ymd(droot):
    files = sorted(os.listdir(os.path.join(droot, 'data', 'daily')))
    return [f for f in files if f.startswith('macro_')][-1][6:14]


def _query(droot, mid='CN_PMI_MFG'):
    return rhq.load_metric_series(mid, _latest_ymd(droot), data_dir=os.path.join(
        droot, 'data', 'daily'), trusted_root=droot)


def _eval_item(droot, question, as_of='2026-11-17', mid='CN_PMI_MFG'):
    res = _query(droot, mid)
    env_series = {'n': len(res['dates']),
                  'source': f"采集档 {res['source']['file']}",
                  'frequency': res['frequency'],
                  'first': res['dates'][0] if res['dates'] else None,
                  'last': res['dates'][-1] if res['dates'] else None,
                  'dates': res['dates'], 'values': res['values']}
    if res.get('collection_status'):
        env_series['collection_status'] = res['collection_status']
    step = {'step': f'S4_history_{mid}', 'ok': True,
            'envelope': {'data': {'series': env_series}}}
    return ro._evaluate_data_requirements(
        [mid], [step], {'target_date': as_of}, [],
        question=question,
        registry={mid: {'frequency': 'monthly'}})[0]


_FULL = [round(50.0 + (i % 7) * 0.07, 2) for i in range(226)]


def _full_root():
    d = _new_data_root()
    _run_round(d, _cn_item(_FULL, 2008, 1, 2026, 10))
    return d


print('═' * 64)
print('Audit-R8: 无效数值不计入有效覆盖 / 时间要求不静默丢失 / 绑定指纹')
print('═' * 64)

# ══ §V: R8-01 无效数值(真实格式文件→生产查询→判定→交付门) ════════
print('§V 有效观测=合法日期+有限数值(采集/清洗/查询/窗口/未限定统一)')

# V1 反例1: values 全 "NaN"(字符串词形,真实源端 NaN 序列化形态)
dV1 = _new_data_root()
_run_round(dV1, _cn_item('NaN', 2008, 1, 2026, 10))
qV1 = _query(dV1)
v1 = _eval_item(dV1, '近五年 CN_PMI_MFG 走势')
check('V1 CE1 values 全 "NaN" → 查询有效观测 0(非有限值 226 全剔'
      '+登记)+判定阻断',
      len(qV1['dates']) == 0
      and qV1['series_clean']['n_nonfinite_dropped'] == 226
      and qV1['series_clean']['n_observations'] == 0
      and v1['outcome'] == 'insufficient_coverage',
      f"n={len(qV1['dates'])} clean={qV1['series_clean']} "
      f"outcome={v1['outcome']}")

# V2 反例2: values 全 "Infinity"(与 -Infinity 同族)
dV2 = _new_data_root()
_run_round(dV2, _cn_item('Infinity', 2008, 1, 2026, 10))
v2 = _eval_item(dV2, '近五年 CN_PMI_MFG 走势')
qV2 = _query(dV2)
dV2b = _new_data_root()
_run_round(dV2b, _cn_item('-Infinity', 2008, 1, 2026, 10))
v2b = _eval_item(dV2b, '近五年 CN_PMI_MFG 走势')
check('V2 CE2 values 全 "Infinity"/-Infinity → 全剔+阻断',
      len(qV2['dates']) == 0 and v2['outcome'] == 'insufficient_coverage'
      and v2b['outcome'] == 'insufficient_coverage',
      f"+inf n={len(qV2['dates'])} outcome={v2['outcome']} "
      f"-inf outcome={v2b['outcome']}")

# V3 采集器纯函数: ±inf/nan 行不入采集史(统一采集侧规则)
import pandas as pd  # noqa: E402
_dfV3 = pd.DataFrame({
    '月份': ['2026年1月', '2026年2月', '2026年3月', '2026年4月'],
    '制造业PMI': [float('inf'), float('nan'), 50.3, float('-inf')]})
_rowsV3 = cmc._macro_month_rows(_dfV3, '月份', '制造业PMI')
check('V3 _macro_month_rows: inf/nan/-inf 行全跳,仅有限值入史',
      _rowsV3 == [('2026-03-01', 50.3)], str(_rowsV3))

# V4 反例3: S4 信封 dates 在场 values=null → 无占位,窗口成员全无效
dV4 = _full_root()
resV4 = _query(dV4)
envV4 = {'n': len(resV4['dates']), 'source': '采集档', 'frequency': 'monthly',
         'first': resV4['dates'][0], 'last': resV4['dates'][-1],
         'dates': resV4['dates'], 'values': None}
stepV4 = {'step': 'S4_history_CN_PMI_MFG', 'ok': True,
          'envelope': {'data': {'series': envV4}}}
v4 = ro._evaluate_data_requirements(
    ['CN_PMI_MFG'], [stepV4], {'target_date': '2026-11-17'}, [],
    question='近五年 CN_PMI_MFG 走势',
    registry={'CN_PMI_MFG': {'frequency': 'monthly'}})[0]
_wV4 = v4['spec'].get('window') or {}
check('V4 CE3 信封 values=null → 禁 1.0 占位,n_in_window=0 阻断',
      v4['outcome'] == 'insufficient_coverage'
      and _wV4.get('n_in_window') == 0,
      f"outcome={v4['outcome']} win={_wV4}")

# V5 长度错配: dates 226 / values 225 → 如实登记,按短侧配对不造值
dV5 = _new_data_root()
_datesV5 = monthrange(2008, 1, 2026, 10)
_run_round(dV5, _cn_item(_FULL[:225], 2008, 1, 2026, 10))
qV5 = _query(dV5)
check('V5 长度错配(226 日期/225 值) → n_length_mismatch=1+有效 225',
      qV5['series_clean']['n_length_mismatch'] == 1
      and qV5['series_clean']['n_observations'] == 225,
      str(qV5['series_clean']))

# V6 全缺失: values 全 null(JSON null)→ 无有效数值面
dV6 = _new_data_root()
_run_round(dV6, _cn_item(None, 2008, 1, 2026, 10))
qV6 = _query(dV6)
v6 = _eval_item(dV6, '近五年 CN_PMI_MFG 走势')
check('V6 values 全 null → 查询 0 观测+判定阻断',
      len(qV6['dates']) == 0
      and qV6['series_clean']['n_missing_dropped'] == 226
      and v6['outcome'] == 'insufficient_coverage',
      f"n={len(qV6['dates'])} outcome={v6['outcome']}")

# V7a 部分缺失(4 个散点单月 null,间距≤62 天不触断档上限 130)→
# 窗内有效=59-4=55,≥半额下界仍满足(数量按实际有效值)
_valsV7 = list(_FULL)
_HOLES = ('2022-03-01', '2023-07-01', '2024-08-01', '2025-02-01')
for i, ds in enumerate(monthrange(2008, 1, 2026, 10)):
    if ds in _HOLES:
        _valsV7[i] = None
dV7 = _new_data_root()
_run_round(dV7, _cn_item(_valsV7, 2008, 1, 2026, 10))
v7 = _eval_item(dV7, '近五年 CN_PMI_MFG 走势')
_wV7 = v7['spec'].get('window') or {}
check('V7a 部分缺失(4 散点月 null)→ 窗内有效 55(非 59)仍满足',
      v7['outcome'] == 'satisfied' and _wV7.get('n_in_window') == 55,
      f"outcome={v7['outcome']} n_in_window={_wV7.get('n_in_window')}")

# V7b 部分缺失(仅剩 2026-09/10)→ 窗内有效 2 < 31 阻断
_valsV7b = [None] * 226
for i, ds in enumerate(monthrange(2008, 1, 2026, 10)):
    if ds in ('2026-09-01', '2026-10-01'):
        _valsV7b[i] = 50.5
dV7b = _new_data_root()
_run_round(dV7b, _cn_item(_valsV7b, 2008, 1, 2026, 10))
v7b = _eval_item(dV7b, '近五年 CN_PMI_MFG 走势')
_wV7b = v7b['spec'].get('window') or {}
check('V7b 严重部分缺失(窗内仅 2 有效)→ 阻断',
      v7b['outcome'] == 'insufficient_coverage'
      and _wV7b.get('n_in_window') == 2,
      f"outcome={v7b['outcome']} n_in_window={_wV7b.get('n_in_window')}")

# V8 重复日期: 同日两值去重留末值+原始精度保留
_dV8 = monthrange(2008, 1, 2026, 10) + ['2026-10-01']
_vV8 = _FULL + [50.123456789123]
dV8 = _new_data_root()
_run_round(dV8, _cn_item(_vV8, 2008, 1, 2026, 10, dates=_dV8))
qV8 = _query(dV8)
check('V8 重复日期(227 行含 1 重复)→ 去重 226+留末值原始精度',
      qV8['series_clean']['n_observations'] == 226
      and qV8['dates'].count('2026-10-01') == 1
      and qV8['values'][-1] == 50.123456789123,
      f"n={qV8['series_clean']['n_observations']} "
      f"last={qV8['values'][-1]!r}")

# V9 正常真实数据: 精度逐位回读+判定满足(正例对照)
dV9 = _full_root()
qV9 = _query(dV9)
v9 = _eval_item(dV9, '近五年 CN_PMI_MFG 走势')
check('V9 正常真实数据 → 226 观测逐位回读+近五年 satisfied',
      qV9['series_clean']['n_observations'] == 226
      and qV9['values'] == [float(v) for v in _FULL]
      and v9['outcome'] == 'satisfied',
      f"n={qV9['series_clean']['n_observations']} "
      f"outcome={v9['outcome']}")

# V10 未限定范围(max_available)路径同规则: 全 NaN → 序列面在场但
# 有效观测 0 → 阻断且据实(不标「均缺席」,不因无范围放行)
v10 = _eval_item(dV1, 'CN_PMI_MFG 历史走势如何')
check('V10 max_available 路径: 全 NaN 有效 0 → 阻断+据实入据',
      v10['outcome'] == 'insufficient_coverage'
      and '有效观测 0' in v10['outcome_basis'],
      f"outcome={v10['outcome']} basis={v10['outcome_basis'][:60]}")

# V11 非法日期行: '2026-13-01' 剔除登记,其余不受影响
_dV11 = monthrange(2008, 1, 2026, 10) + ['2026-13-01']
dV11 = _new_data_root()
_run_round(dV11, _cn_item(_FULL + [51.2], 2008, 1, 2026, 10, dates=_dV11))
qV11 = _query(dV11)
check('V11 非法日期(2026-13-01)→ 剔除登记 1,有效 226',
      qV11['series_clean']['n_invalid_dates_dropped'] == 1
      and qV11['series_clean']['n_observations'] == 226,
      str(qV11['series_clean']))

# ══ §W: R8-02 时间要求(三态区分+斜杠+去年+单侧终界) ═════════════
print('§W 时间要求不静默丢失(解析/窗口/下游同源)')

qw = ro._question_window
check('W1a 斜杠全日期区间 → explicit 2020-01-01..2025-12-31',
      qw('研究 2020/01/01 至 2025/12/31 的 CN_PMI_MFG 变化') == {
          'kind': 'explicit', 'start': '2020-01-01',
          'end': '2025-12-31', 'raw': '2020/01/01..2025/12/31'})
check('W1b 斜杠年月区间(止侧月末补齐)',
      qw('2020/01 至 2025/12 走势')['start'] == '2020-01-01'
      and qw('2020/01 至 2025/12 走势')['end'] == '2025-12-31')
check('W1c 斜杠+ISO 混排区间 → explicit',
      qw('2020/01/01至2020-06-30')['start'] == '2020-01-01'
      and qw('2020/01/01至2020-06-30')['end'] == '2020-06-30')
check('W1d 斜杠非法月(2020/13/01) → unparseable 不回落',
      qw('2020/13/01 至 2025/12/31')['kind'] == 'unparseable')
check('W2a 「去年」→ calendar_year(绑定研究时点)',
      qw('研究去年 CN_PMI_MFG 的变化') == {
          'kind': 'calendar_year', 'offset': -1, 'raw': '去年'})
check('W2b 「截至2025/12」→ 单侧终界(斜杠同判)',
      qw('截至2025/12 的走势') == {
          'kind': 'explicit', 'start': None, 'end': '2025-12-31',
          'raw': '截至2025/12'})

# W3 CE(R8-02-1): 斜杠区间+仅 12 个月数据 → 阻断(基线 max_available 放行)
dW3 = _new_data_root()
_run_round(dW3, _cn_item([50.0 + i * 0.1 for i in range(12)],
                         2025, 11, 2026, 10))
w3 = _eval_item(dW3, '研究 2020/01/01 至 2025/12/31 的 CN_PMI_MFG 变化')
_wW3 = w3['spec'].get('window') or {}
check('W3 CE 斜杠区间+12 个月数据 → 窗内 2 阻断(不退化为 max_available)',
      w3['outcome'] == 'insufficient_coverage'
      and _wW3.get('start') == '2020-01-01'
      and _wW3.get('n_in_window') == 2,
      f"outcome={w3['outcome']} win={_wW3}")

# W4 CE(R8-02-2): 「去年」+仅 12 个月数据 → 窗=2025 自然年,窗内 2 阻断
w4 = _eval_item(dW3, '研究去年 CN_PMI_MFG 的变化')
_wW4 = w4['spec'].get('window') or {}
check('W4 CE 「去年」+12 个月数据 → 窗 2025-01-01..2025-12-31 窗内 2 阻断',
      w4['outcome'] == 'insufficient_coverage'
      and _wW4.get('start') == '2025-01-01'
      and _wW4.get('end') == '2025-12-31'
      and _wW4.get('n_in_window') == 2,
      f"outcome={w4['outcome']} win={_wW4}")

# W5 CE(R8-02-3): 「截至2025年12月」全量数据 → 单侧终界可满足(不再必然拒)
dW5 = _full_root()
w5 = _eval_item(dW5, '研究截至2025年12月的 CN_PMI_MFG 走势')
_wW5 = w5['spec'].get('window') or {}
check('W5 CE 「截至X」全量数据 → satisfied(窗起=序列首观测,终侧核验)',
      w5['outcome'] == 'satisfied'
      and _wW5.get('start') == '2008-01-01'
      and _wW5.get('end') == '2025-12-31'
      and _wW5.get('last_in_window') == '2025-12-01'
      and '单侧终界' in json.dumps(_wW5, ensure_ascii=False)
      + (w5['spec'].get('window', {}).get('basis') or ''),
      f"outcome={w5['outcome']} win={ {k: v for k, v in _wW5.items() if k != 'basis'} }")

# W6 「截至X」数据全在界后(仅 2026-01..10)→ 窗内 0 阻断(诚实失败)
dW6 = _new_data_root()
_run_round(dW6, _cn_item([50.0 + i * 0.1 for i in range(10)],
                         2026, 1, 2026, 10))
w6 = _eval_item(dW6, '研究截至2025年12月的 CN_PMI_MFG 走势')
_wW6 = w6['spec'].get('window') or {}
check('W6 「截至X」数据全在界后 → 窗内 0 阻断',
      w6['outcome'] == 'insufficient_coverage'
      and (_wW6.get('n_in_window') in (0, None)),
      f"outcome={w6['outcome']} win={ {k: v for k, v in _wW6.items() if k != 'basis'} }")

# W7 既有正确行为保留(正例组)
w7a = _eval_item(dW5, '研究 2020-01-01 至 2025-12-31 的 CN_PMI_MFG 变化')
w7b = _eval_item(dW5, '近五年 CN_PMI_MFG 走势')
w7c = _eval_item(dW5, '近十年 CN_PMI_MFG 走势')
w7d = _eval_item(dW5, '2023年6月以来 CN_PMI_MFG 走势')
w7e = _eval_item(dW5, 'CN_PMI_MFG 历史走势如何')
w7f = _eval_item(dW5, '近五年 CN_PMI_MFG 走势', as_of='2021-01-15')
check('W7 既有正例保留: ISO 区间/近五年/近十年/以来/无限制/合法回放',
      w7a['outcome'] == 'satisfied'
      and w7b['outcome'] == 'satisfied'
      and w7c['outcome'] == 'satisfied'
      and w7d['outcome'] == 'satisfied'
      and w7e['outcome'] == 'satisfied'
      and w7f['outcome'] == 'satisfied',
      ' '.join(f"{k}={v['outcome']}" for k, v in [
          ('iso', w7a), ('5y', w7b), ('10y', w7c), ('since', w7d),
          ('unspec', w7e), ('replay', w7f)]))

# W8 「去年」全量数据 → 窗 2025 自然年窗内 12 满足
w8 = _eval_item(dW5, '研究去年 CN_PMI_MFG 的变化')
_wW8 = w8['spec'].get('window') or {}
check('W8 「去年」全量数据 → satisfied(2025 自然年窗内 12)',
      w8['outcome'] == 'satisfied'
      and _wW8.get('start') == '2025-01-01'
      and _wW8.get('n_in_window') == 12,
      f"outcome={w8['outcome']} n={_wW8.get('n_in_window')}")

# W9 无法解析三态: 指定了但无法解析 → 明确阻断(非 max_available)
w9 = _eval_item(dW5, '研究 2020年13月1日 至 2025年12月 的 CN_PMI_MFG 变化')
check('W9 指定但无法解析 → 阻断+「无法解析」入据(不静默丢失)',
      w9['outcome'] == 'insufficient_coverage'
      and '无法解析' in w9['outcome_basis'],
      f"outcome={w9['outcome']} basis={w9['outcome_basis'][:60]}")


# ══ §G: 生产入口双门(report/archive 同判据源) ═════════════════════
def make_run(tmp, name, *, req_items=None):
    global _RUN_SEQ
    _RUN_SEQ += 1
    run_ts = '20261117T19%04dZ' % _RUN_SEQ
    rd = os.path.join(tmp, name)
    os.makedirs(rd, exist_ok=True)
    rows = [{'metric_id': 'TEST_M%d' % i, 'value': 1.0 * i, 'unit': 'x',
             'observation_date': '2026-11-09', 'quality_status': 'OK',
             'source': {'id': 'src%d' % i, 'kind': 'synthetic'}}
            for i in range(2)]
    report = {
        'schema_version': '2.0', 'pipeline_version': 't',
        'run': {'question': 'Audit-R8 回归合成问题', 'ts_utc': run_ts,
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


print('§G 生产入口双门(坏值/斜杠窗规格 → report+archive 拒)')

tmpG = tempfile.mkdtemp(prefix='r8gate_')
eroot = os.path.join(tmpG, 'engine')
os.makedirs(os.path.join(eroot, 'config'), exist_ok=True)
shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
            os.path.join(eroot, 'config', 'metric_registry.json'))

rdG1 = make_run(tmpG, 'g1', req_items=[v1])
eG1 = stage_report(rdG1, eroot)
aG1 = stage_archive(rdG1, eroot, os.path.join(tmpG, 'arcG1'))
check('G1 全 NaN 规格(n_in_window=0)→ report 拒+archive 拒',
      eG1.get('deliverable') is False
      and eG1.get('blocked_class') == 'required_data_missing'
      and aG1.returncode != 0,
      f"bc={eG1.get('blocked_class')} deliv={eG1.get('deliverable')} "
      f"rc={aG1.returncode}")

rdG2 = make_run(tmpG, 'g2', req_items=[w3])
eG2 = stage_report(rdG2, eroot)
aG2 = stage_archive(rdG2, eroot, os.path.join(tmpG, 'arcG2'))
check('G2 斜杠窗规格(窗内 2)→ report 拒+archive 拒',
      eG2.get('deliverable') is False
      and eG2.get('blocked_class') == 'required_data_missing'
      and aG2.returncode != 0,
      f"bc={eG2.get('blocked_class')} rc={aG2.returncode}")

rdG3 = make_run(tmpG, 'g3', req_items=[w5])
aj.record_semantic_verdict(eroot, rdG3, 'UPHELD', 'R8-GATE')
eG3 = stage_report(rdG3, eroot)
check('G3 单侧终界满足项(截至X 全量)→ 可交付(正例对照)',
      eG3.get('blocked_class') != 'required_data_missing'
      and eG3.get('deliverable') is True,
      f"bc={eG3.get('blocked_class')} deliv={eG3.get('deliverable')}")

# ══ §B: R8-03 绑定指纹(未跟踪源码入指纹;印章三级链保持) ══════════
print('§B 执行源码指纹(未跟踪新增源码必须改变指纹)')

tmpB = tempfile.mkdtemp(prefix='r8bind_')
repoB = os.path.join(tmpB, 'repo')


def _git(cwd, *a):
    return subprocess.run(['git', ] + list(a), cwd=cwd,
                          capture_output=True, text=True, timeout=30)


_git(repoB if os.path.isdir(repoB) else tmpB, 'init', '-q', repoB)
open(os.path.join(repoB, 'a.py'), 'w').write('x = 1\n')
_git(repoB, 'add', 'a.py')
_git(repoB, '-c', 'user.email=t@t', '-c', 'user.name=t',
     'commit', '-qm', 'init')
_h1, _s1, _f1 = ro._git_state(repoB)
open(os.path.join(repoB, 'new_untracked.py'), 'w').write('y = 2\n')
_h2, _s2, _f2 = ro._git_state(repoB)
open(os.path.join(repoB, 'new_untracked.py'), 'w').write('y = 222\n')
_h3, _s3, _f3 = ro._git_state(repoB)
_git(repoB, 'add', 'new_untracked.py')
_git(repoB, '-c', 'user.email=t@t', '-c', 'user.name=t',
     'commit', '-qm', 'track it')
_h4, _s4, _f4 = ro._git_state(repoB)
check('B1 未跟踪源码入指纹: 同 HEAD 下新增/改内容指纹各异;'
      '转跟踪后 HEAD 变(身份移至 head,指纹归净)',
      _s1 == 'run_root' and _h1 == _h2 == _h3
      and _h4 != _h1
      and len({_f1, _f2, _f3}) == 3 and _f4 == _f1,
      f"src={_s1} heads={[_h1[:7], _h2[:7], _h3[:7], _h4[:7]]} "
      f"fps={[_f1[:8], _f2[:8], _f3[:8], _f4[:8]]}")

engB = os.path.join(tmpB, 'engine')
os.makedirs(os.path.join(engB, 'scripts'), exist_ok=True)
shutil.copy(os.path.join(ROOT, 'scripts', 'research_orchestrator.py'),
            os.path.join(engB, 'scripts', 'research_orchestrator.py'))
json.dump({'git_head': 'deadbeef' * 5,
           'git_diff_sha256': 'cafe' * 16,
           'stamped_at': '2026-11-17R8'},
          open(os.path.join(engB, 'CODE_VERSION.json'), 'w'))
rB2 = subprocess.run(
    [sys.executable, '-c',
     'import sys; sys.path.insert(0, %r); sys.path.insert(0, %r)\n'
     'import research_orchestrator as ro\n'
     'print(ro._git_state(%r))' % (engB, os.path.join(engB, 'scripts'), engB)],
    capture_output=True, text=True, timeout=60)
_stamp_out = rB2.stdout.strip()
check('B2 引擎树(无 .git)→ CODE_VERSION 印章三级命中(链保持)',
      "'deadbeef" in _stamp_out and 'code_version_stamp' in _stamp_out,
      _stamp_out[:120] or rB2.stderr[:200])

print('─' * 64)
print(f"Audit-R8 判定: {PASS} PASS / {FAIL} FAIL")
sys.exit(0 if FAIL == 0 else 1)
