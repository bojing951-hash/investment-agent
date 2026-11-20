#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R7 第七轮审计修复回归(R7-01 任务起止日期与窗口覆盖)。

外审三项反例(基线 4e2f94c 复现):
  CE1 近五年 PMI: 168 点中窗内实际 1 点,系统记 n_in_window=168 放行;
  CE2 近十年 BEI_10Y: 2016-11-14..2026-11-12 共 2499 点,边界满足容差,
     仅因 <252×10=2520 被拒;
  CE3 明确区间 2020-01-01..2025-12-31 DXY: 输入只有 2026 年 60 点,
     被当作 max_available 通过。

修复判据(scripts/research_orchestrator.py):
  §E _question_window: 相对年限+明确日期区间统一解析(ISO/紧凑/中文年
     月日/年-月四词形;缺月日侧别补齐;以来/截至单侧界;单日期≠区间;
     词序倒置/非法日期=指定了但无法解析→阻断不回落)。
  §T 三个反例回归+正例: 从实际 dates/values 计算窗内有效去重观测;
     日历期望(工作日/ISO周/自然月/季)×半额下界替代 252×年数硬否决;
     严重断档=窗内相邻观测逐对最大间距超频率族上限阻断;错误区间/
     未知频率/信封无 dates=阻断;未限定范围 max_available 口径保留;
     S4 信封与快照序列同一覆盖判定。
  §G 生产入口双门: 反例规格注入 run → report 拒交付+archive 拒归档
     (同一判据源);满足项不触发该阻断类。
  §F(R7-02) 采集状态贯通九场景: collector→loader→工作台→判定→report→
     archive 全链——fresh 首采/连续二采/美国刷新保 CN/单项失败续用/
     两项失败续用/无历史可续/合理续用(披露放行)/严重陈旧续用
     (stale_for_task 阻断)/合法历史回放(参考端=回放时点不误判);
     断言查询输出(collection_status 三分: 文件写入/最后成功采集/数据
     统计期)、报告状态(deliverable/渲染续用披露)与归档结果,非仅原始
     JSON 字段。

判定=逐 check 打印+exit code(0=全过)。
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
import snapshot_builder as sb        # noqa: E402
import workbench_data as wd          # noqa: E402

PASS, FAIL = 0, 0


def check(name, cond, detail=''):
    global PASS, FAIL
    print(f"  {'✅' if cond else '❌'} {name}" + (f" — {detail}" if detail and not cond else ''))
    PASS = PASS + (1 if cond else 0)
    FAIL = FAIL + (0 if cond else 1)


# ── 夹具助手(与生产 ia_cli history 信封/快照 series_store 同形) ──────
def weekdayrange(d0, d1):
    out, d = [], d0
    while d <= d1:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d += timedelta(days=1)
    return out


def monthrange(y0, m0, y1, m1):
    out, y, m = [], y0, m0
    while (y, m) <= (y1, m1):
        out.append('%04d-%02d-01' % (y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def spread_gap(dates, target):
    """均匀抽稀至 target 个(保端点,最大相邻间距仍≤频率族容差)——
    模拟真实十年日频因节假日/数据缺席少数十点(BEI_10Y 2499<2520)。"""
    if target >= len(dates):
        return list(dates)
    drop = len(dates) - target
    step = (len(dates) - 2) / (drop + 1)
    idx = {round(step * (i + 1)) for i in range(drop)}
    idx = {i for i in idx if 0 < i < len(dates) - 1}
    while len(idx) < drop:                      # 补齐(round 碰撞时右移)
        cand = max(idx) + 1 if idx else 1
        if cand >= len(dates) - 1:
            break
        idx.add(cand)
    return [d for i, d in enumerate(dates) if i not in idx]


def store(mid, dates):
    return {mid: {'dates': dates, 'values': [1.0] * len(dates)}}


def s4env(mid, dates, freq, source='采集档'):
    return {'step': f'S4_history_{mid}', 'ok': True,
            'envelope': {'data': {'series': {
                'n': len(dates), 'source': source, 'frequency': freq,
                'first': dates[0], 'last': dates[-1],
                'dates': list(dates), 'values': [1.0] * len(dates)}}}}


print('═' * 64)
print('Audit-R7: 任务起止日期统一解析 / 日历期望覆盖 / 严重断档')
print('═' * 64)

AS_OF = '2026-11-17'
snapW = lambda store_: {'target_date': AS_OF, 'series_store': store_}  # noqa: E731
REG = {'PMI': {'frequency': 'monthly'}, 'BEI_10Y': {'frequency': 'daily'},
       'DXY': {'frequency': 'daily'}, 'PM_M': {'frequency': 'monthly'}}

# ══ §E: 明确日期区间解析(_question_window) ═════════════════════════
print('§E 明确日期区间词面解析(统一入口)')

qw = ro._question_window
check('E1 ISO 词形区间 → explicit 2020-01-01..2025-12-31',
      qw('2020-01-01至2025-12-31 DXY 走势') == {
          'kind': 'explicit', 'start': '2020-01-01',
          'end': '2025-12-31', 'raw': '2020-01-01..2025-12-31'})
check('E2 中文词形区间(止侧月末补齐) → 2020-01-01..2025-12-31',
      qw('2020年1月到2025年12月 DXY 走势')['start'] == '2020-01-01'
      and qw('2020年1月到2025年12月 DXY 走势')['end'] == '2025-12-31')
check('E3 紧凑八位词形 → explicit 归一',
      qw('20200101到20251231')['start'] == '2020-01-01'
      and qw('20200101到20251231')['end'] == '2025-12-31')
check('E4 「X以来」→ 起界无终界(end=研究时点)',
      qw('2023年6月以来 DXY 走势') == {
          'kind': 'explicit', 'start': '2023-06-01', 'end': None,
          'raw': '2023年6月以来'})
check('E5 「截至X」→ 终界无起界',
      qw('截至2025年12月 DXY 走势') == {
          'kind': 'explicit', 'start': None, 'end': '2025-12-31',
          'raw': '截至2025年12月'})
# R12 P1①(指令⑤)契约更新: 明确研究年份/月份必须纳入要求——裸单日期
# 提及不再退化为未限定 max_available,按粒度成显式窗(年→日历年/月→自然月)。
check('E6 单日期提及 → 粒度显式窗(R12: 明确年份纳入要求)',
      qw('2026年10月的 PMI 如何') == {
          'kind': 'explicit', 'start': '2026-10-01', 'end': '2026-10-31',
          'raw': '2026年10月'})
check('E7 相对年限 → relative(端点=研究时点)',
      qw('近五年 PM_M 走势') == {'kind': 'relative', 'years': 5})
check('E8 词序倒置 → unparseable 区间倒置(不静默重排)',
      qw('2025年12月31日至2020年1月1日 DXY')['kind'] == 'unparseable'
      and '倒置' in qw('2025年12月31日至2020年1月1日 DXY')['reason'])
check('E9 非法日期词形(2020年13月) → unparseable 不回落',
      qw('2020年13月1日至2025年12月 DXY')['kind'] == 'unparseable')

# ══ §T: 三反例回归+正例(_evaluate_data_requirements) ═════════════
print('§T 任务窗口覆盖判定(实际 dates 面+日历期望)')

# T1 CE1(外审反例1): 近五年 PMI,168 点中窗内实际 1 点(基线记
#    n_in_window=168 放行)——前 167 月全在窗前,仅 2026-10 一点在窗内
_t1_dates = monthrange(2007, 12, 2021, 10) + ['2026-10-01']
t1 = ro._evaluate_data_requirements(
    ['PMI'], [], snapW(store('PMI', _t1_dates)), [],
    question='近五年制造业 PMI 走势', registry=REG)[0]
_t1w = t1['spec']['window']
check('T1 CE1 近五年/168 点仅 1 点在窗 → 阻断(n_in_window=实际去重窗内)',
      t1['outcome'] == 'insufficient_coverage'
      and _t1w.get('n_in_window') == 1
      and _t1w.get('first_in_window') == '2026-10-01',
      str(_t1w))

# T2 CE2(外审反例2): 近十年 BEI_10Y,2016-11-14..2026-11-12 真实
#    交易日 2499 点(节假日缺席),边界满足容差——基线因 2499<2520 硬拒
_t2_dates = spread_gap(
    weekdayrange(date(2016, 11, 14), date(2026, 11, 12)), 2499)
t2 = ro._evaluate_data_requirements(
    ['BEI_10Y'], [], snapW(store('BEI_10Y', _t2_dates)), [],
    question='近十年 BEI_10Y 走势', registry=REG)[0]
_t2w = t2['spec']['window']
check('T2 CE2 近十年 2499 点(边界容差内) → satisfied(日历期望×半额'
      '替代 252×年数硬否决)',
      t2['outcome'] == 'satisfied'
      # 首点 2016-11-14 在窗起容差内,窗内成员=2499−3(11-14/15/16
      # 在窗前)=2496——从实际 dates 计数,不冒充
      and _t2w.get('n_in_window') == 2496
      and _t2w.get('expected_in_window') is not None
      and _t2w.get('max_adjacent_gap_days') is not None
      and _t2w.get('max_adjacent_gap_days')
      <= _t2w.get('max_gap_limit_days'),
      str(_t2w))

# T3 CE3(外审反例3): 明确区间 2020-01-01..2025-12-31 DXY,输入只有
#    2026 年 60 个日频点——基线当 max_available 通过
_t3_dates = weekdayrange(date(2026, 8, 17), date(2026, 11, 12))
t3 = ro._evaluate_data_requirements(
    ['DXY'], [], snapW(store('DXY', _t3_dates)), [],
    question='2020年1月1日至2025年12月31日 DXY 走势', registry=REG)[0]
_t3w = t3['spec']['window']
check('T3 CE3 明确区间+输入全在 2026 → 阻断(不当 max_available)',
      t3['outcome'] == 'insufficient_coverage'
      and _t3w.get('kind') == 'explicit'
      and _t3w.get('start') == '2020-01-01'
      and _t3w.get('end') == '2025-12-31'
      and _t3w.get('n_in_window') == 0,
      str(_t3w))

# T4 正例: 正常五年月频(59/61 月=合理缺口)通过
t4 = ro._evaluate_data_requirements(
    ['PM_M'], [], snapW(store('PM_M', monthrange(2021, 12, 2026, 10))),
    [], question='近五年 PM_M 走势', registry=REG)[0]
check('T4 正常五年月频 59 月 → satisfied(合理缺口不误拒)',
      t4['outcome'] == 'satisfied', t4['outcome_basis'][:60])

# T5 正例: 正常十年交易日数据(节假日缺席~60 点)通过——**真实交易日
#    正例=工作日历扣除节假日**,非含周末人工序列
_t5_dates = spread_gap(
    weekdayrange(date(2016, 11, 20), date(2026, 11, 13)), 2549)
t5 = ro._evaluate_data_requirements(
    ['DXY'], [], snapW(store('DXY', _t5_dates)), [],
    question='近十年 DXY 走势', registry=REG)[0]
check('T5 十年交易日 2549 点(含节假日缺席) → satisfied',
      t5['outcome'] == 'satisfied'
      and t5['spec']['window'].get('n_in_window') == 2549,
      str(t5['spec']['window']))

# T6 正例: 月频合理发布滞后(末观测滞后研究时点 72 天)通过
t6 = ro._evaluate_data_requirements(
    ['PM_M'], [], {'target_date': '2026-11-12',
                   'series_store': store('PM_M',
                                         monthrange(2016, 10, 2026, 9))},
    [], question='近十年 PM_M 走势', registry=REG)[0]
check('T6 月频十年+发布滞后 72 天 → satisfied(滞后不误拒)',
      t6['outcome'] == 'satisfied', t6['outcome_basis'][:60])

# T7 反例: 两年数据冒充五年(窗起未覆盖+总量不足)阻断
t7 = ro._evaluate_data_requirements(
    ['DXY'], [], snapW(store('DXY', weekdayrange(
        date(2024, 11, 20), date(2026, 11, 13)))), [],
    question='近五年 DXY 走势', registry=REG)[0]
check('T7 两年冒充五年 → 阻断(真覆盖不足)',
      t7['outcome'] == 'insufficient_coverage', t7['outcome_basis'][:60])

# T8 反例: 双段密集中隔三年长洞(总量超半额)——严重断档阻断
_t8_dates = (weekdayrange(date(2016, 11, 20), date(2022, 6, 30))
             + weekdayrange(date(2025, 6, 2), date(2026, 11, 13)))
t8 = ro._evaluate_data_requirements(
    ['DXY'], [], snapW(store('DXY', _t8_dates)), [],
    question='近十年 DXY 走势', registry=REG)[0]
_t8w = t8['spec']['window']
check('T8 双段密集隔三年洞(总量超半额) → 严重断档阻断',
      t8['outcome'] == 'insufficient_coverage'
      and _t8w.get('max_adjacent_gap_days', 0)
      > _t8w.get('max_gap_limit_days', 0),
      str({k: _t8w.get(k) for k in (
          'n_in_window', 'expected_in_window', 'n_floor_in_window',
          'max_adjacent_gap_days', 'max_gap_limit_days')}))

# T9 反例: S4 信封无实际 dates(合成/降级形态) → 窗口成员不可核验阻断
t9 = ro._evaluate_data_requirements(
    ['DXY'], [{'step': 'S4_history_DXY', 'ok': True,
               'envelope': {'data': {'series': {
                   'n': 2500, 'source': '采集档', 'frequency': 'daily',
                   'first': '2016-11-14', 'last': '2026-11-12'}}}}],
    snapW({}), [], question='近十年 DXY 走势', registry=REG)[0]
check('T9 S4 信封无 dates → 阻断(不得凭 first/last 裁剪或总量冒充)',
      t9['outcome'] == 'insufficient_coverage'
      and '不可核验' in t9['outcome_basis'], t9['outcome_basis'][:60])

# T10 同一逻辑: 同一 dates 经快照序列面与 S4 信封面判定一致
t10_snap = ro._evaluate_data_requirements(
    ['BEI_10Y'], [], snapW(store('BEI_10Y', _t2_dates)), [],
    question='近十年 BEI_10Y 走势', registry=REG)[0]
t10_s4 = ro._evaluate_data_requirements(
    ['BEI_10Y'], [s4env('BEI_10Y', _t2_dates, 'daily')], snapW({}), [],
    question='近十年 BEI_10Y 走势', registry=REG)[0]
check('T10 快照面与 S4 信封面同一覆盖判定(n_in_window 一致)',
      t10_snap['outcome'] == t10_s4['outcome'] == 'satisfied'
      and (t10_snap['spec']['window'].get('n_in_window')
           == t10_s4['spec']['window'].get('n_in_window') == 2496),
      f"snap={t10_snap['spec']['window'].get('n_in_window')} "
      f"s4={t10_s4['spec']['window'].get('n_in_window')}")

# T11 反例: 问题带无法解析范围词形 → 阻断不回落 max_available
t11 = ro._evaluate_data_requirements(
    ['DXY'], [], snapW(store('DXY', _t5_dates)), [],
    question='2020年13月1日至2025年12月 DXY 走势', registry=REG)[0]
check('T11 指定了但无法解析(2020年13月) → 阻断不回落',
      t11['outcome'] == 'insufficient_coverage'
      and '无法解析' in t11['outcome_basis'], t11['outcome_basis'][:60])

# T12 显式区间与相对年限并存(Audit-R11 P1 语义对齐)
# R7 原口径「显式区间优先,相对年限记入 basis」=只匹配一部分约束;
# Audit-R11(2026-11-18)明确「收集全部时间约束,不允许只匹配其中一
# 部分」→多范围任务=提示拆分并阻断。判据随语义更新,阻断更严。
t12 = ro._evaluate_data_requirements(
    ['DXY'], [], snapW(store('DXY', weekdayrange(
        date(2022, 1, 3), date(2025, 6, 30)))), [],
    question='近五年 2022年1月至2025年6月 DXY 走势', registry=REG)[0]
_t12w = t12['spec']['window']
check('T12 显式区间+相对年限并存 → 多范围任务阻断(请拆分;R11 对齐)',
      _t12w.get('kind') == 'unparseable'
      and '多个时间范围约束' in str(_t12w.get('basis'))
      and '拆分' in str(_t12w.get('basis')),
      str(_t12w.get('basis')))

# T13 「X以来」→ 终界=研究时点(数据止 2026-11 与时点对齐通过)
t13 = ro._evaluate_data_requirements(
    ['DXY'], [], snapW(store('DXY', weekdayrange(
        date(2023, 6, 1), date(2026, 11, 13)))), [],
    question='2023年6月以来 DXY 走势', registry=REG)[0]
check('T13 「X以来」终界=研究时点 → satisfied(起界覆盖)',
      t13['outcome'] == 'satisfied'
      and t13['spec']['window'].get('end') == '2026-11-17',
      str(t13['spec']['window']))

# ══ §G: 生产入口双门(report/archive 同一判据源) ═════════════════
print('§G report/archive 生产入口双门')

_RUN_SEQ = 700


def make_run(tmp, name, *, req_items=None):
    global _RUN_SEQ
    _RUN_SEQ += 1
    run_ts = '20261117T17%04dZ' % _RUN_SEQ
    rd = os.path.join(tmp, name)
    os.makedirs(rd, exist_ok=True)
    rows = [{'metric_id': 'TEST_M%d' % i, 'value': 1.0 * i, 'unit': 'x',
             'observation_date': '2026-11-09', 'quality_status': 'OK',
             'source': {'id': 'src%d' % i, 'kind': 'synthetic'}}
            for i in range(2)]
    report = {
        'schema_version': '2.0', 'pipeline_version': 't',
        'run': {'question': 'Audit-R7 回归合成问题', 'ts_utc': run_ts,
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


tmp = tempfile.mkdtemp(prefix='r7gate_')
eroot = os.path.join(tmp, 'engine')
os.makedirs(os.path.join(eroot, 'config'), exist_ok=True)
shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
            os.path.join(eroot, 'config', 'metric_registry.json'))

# G1 CE1 规格(窗内 1 点)注入 run → 两门同拒
rdG1 = make_run(tmp, 'g1', req_items=[t1])
eG1 = stage_report(rdG1, eroot)
aG1 = stage_archive(rdG1, eroot, os.path.join(tmp, 'arcG1'))
check('G1 CE1 窗内 1 点 → report 拒交付+archive 拒归档',
      eG1.get('deliverable') is False
      and eG1.get('blocked_class') == 'required_data_missing'
      and aG1.returncode != 0,
      f"bc={eG1.get('blocked_class')} deliv={eG1.get('deliverable')} "
      f"rc={aG1.returncode}")

# G2 CE3 规格(明确区间 0 窗内)注入 run → 两门同拒
rdG2 = make_run(tmp, 'g2', req_items=[t3])
eG2 = stage_report(rdG2, eroot)
aG2 = stage_archive(rdG2, eroot, os.path.join(tmp, 'arcG2'))
check('G2 CE3 明确区间 0 窗内 → report 拒交付+archive 拒归档',
      eG2.get('deliverable') is False
      and eG2.get('blocked_class') == 'required_data_missing'
      and aG2.returncode != 0,
      f"bc={eG2.get('blocked_class')} rc={aG2.returncode}")

# G3 满足项(CE2 2499 点 satisfied)→ 不触发该阻断类(正例对照)
rdG3 = make_run(tmp, 'g3', req_items=[t2])
aj.record_semantic_verdict(eroot, rdG3, 'UPHELD', 'R7-GATE')
eG3 = stage_report(rdG3, eroot)
check('G3 satisfied 项 → 不因窗口判据阻断(可交付正例对照)',
      eG3.get('blocked_class') != 'required_data_missing'
      and eG3.get('deliverable') is True,
      f"bc={eG3.get('blocked_class')} deliv={eG3.get('deliverable')}")

# G4 生产接线: run_research 调用面传 _question_window 所在判据链
import inspect  # noqa: E402
check('G4 run_research 传 registry=权威注册表(判据链接线不变)',
      'registry=reg.get' in inspect.getsource(ro.run_research))

# ══ §F: R7-02 采集状态贯通九场景(collector→loader→工作台→判定→门) ══
print('§F 采集状态贯通九场景(查询/报告/归档面断言)')

_ORIG_FETCH_MH = cmc.fetch_macro_history
_MC_DATA_DIR_ORIG = mc.DATA_DIR


def _cn_item(y0, m0, y1, m1, fetched_at):
    dates = monthrange(y0, m0, y1, m1)
    return {'date': dates[-1], 'value': 50.0, 'prev': 49.8,
            'frequency': 'monthly', 'unit': 'index_point',
            'series': {'dates': dates,
                       'values': [50.0 + (i % 5) * 0.1
                                  for i in range(len(dates))]},
            'provenance': {
                'source': 'akshare_em(macro_china_pmi)',
                'fetched_at': fetched_at,
                'coverage': {'n': len(dates), 'first': dates[0],
                             'last': dates[-1]},
                'generated_by': 'fetch_macro_history'}}


def _new_data_root():
    d = tempfile.mkdtemp(prefix='r7f_')
    os.makedirs(os.path.join(d, 'data', 'daily'))
    os.makedirs(os.path.join(d, 'config'))
    shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
                os.path.join(d, 'config', 'metric_registry.json'))
    return d


class _FixedDT:
    """R26: 跨日轮模拟——save_macro 用 datetime.now() 取档日,固定到指定日。"""

    def __init__(self, y, m, d):
        import datetime as _d
        self._dt = _d.datetime(y, m, d)

    def now(self, tz=None):
        return self._dt


def _run_round(droot, fetch_result, us=None, day=None):
    """一轮正式采集(网络边界注入: fetch_result=伪造返回/异常;写档经
    生产 save_macro+merge_cn_history;day=(y,m,d)=模拟采集日,缺省=真实
    当日——Audit-R26 后同日部分面会被守卫转存,跨日续存场景须 day 推进)。
    返回 cn_status。"""
    mc.DATA_DIR = os.path.join(droot, 'data')
    if isinstance(fetch_result, BaseException):
        def _boom():
            raise fetch_result
        cmc.fetch_macro_history = _boom
    else:
        cmc.fetch_macro_history = lambda: json.loads(json.dumps(
            fetch_result))
    results = {'HY_OAS': {'value': 3.1, 'date': '2026-11-13',
                          'frequency': 'daily'}}
    if us:
        results.update(json.loads(json.dumps(us)))
    results, cn_status = mc.merge_cn_history(results, data_dir=mc.DATA_DIR)
    _orig_dt = mc.datetime
    if day:
        mc.datetime = _FixedDT(*day)
    try:
        mc.save_macro(results, [], {}, cn_history=cn_status)
    finally:
        mc.datetime = _orig_dt
    return cn_status


def _latest_ymd(droot):
    files = sorted(os.listdir(os.path.join(droot, 'data', 'daily')))
    mac = [f for f in files if f.startswith('macro_')]
    return mac[-1][6:14]


def _query(droot, mid='CN_PMI_MFG'):
    ymd = _latest_ymd(droot)
    return rhq.load_metric_series(mid, ymd, data_dir=os.path.join(
        droot, 'data', 'daily'), trusted_root=droot)


def _eval_item(droot, question, as_of, mid='CN_PMI_MFG'):
    """经真实查询面(rhq→序列+采集状态)构造 S4 信封面喂判定器——
    与生产 run_research S4 步同源(wd.metric_series 输出即信封 series)。"""
    res = _query(droot, mid)
    env_series = {'n': len(res['dates']), 'source':
                  f"采集档 {res['source']['file']}",
                  'frequency': res['frequency'],
                  'first': res['dates'][0], 'last': res['dates'][-1],
                  'dates': res['dates'], 'values': res['values']}
    if res.get('collection_status'):
        env_series['collection_status'] = res['collection_status']
    step = {'step': f'S4_history_{mid}', 'ok': True,
            'envelope': {'data': {'series': env_series}}}
    return ro._evaluate_data_requirements(
        [mid], [step], {'target_date': as_of}, [],
        question=question,
        registry={mid: {'frequency': 'monthly'}})[0]


def _eval_snap_item(droot, question, as_of, mid='CN_PMI_MFG'):
    """快照面: 序列入 series_store、provenance 入 series_provenance
    平节(与 build_snapshot merge_macro_series 同键)。"""
    res = _query(droot, mid)
    snap = {'target_date': as_of,
            'series_store': {mid: {'dates': res['dates'],
                                   'values': res['values']}}}
    if res.get('collection_status'):
        snap['series_provenance'] = {
            mid: {'fetched_at': res['collection_status']
                  .get('last_success_at'),
                  'fresh': (res['collection_status'].get('mode')
                            != 'carry_forward'),
                  'carry_forward_from': res['collection_status']
                  .get('carry_forward_from')}}
    return ro._evaluate_data_requirements(
        [mid], [], snap, [], question=question,
        registry={mid: {'frequency': 'monthly'}})[0]


# F1 首次采集 fresh: 查询面三分状态+判定 satisfied(快照面同判)
d1 = _new_data_root()
st1 = _run_round(d1, {'CN_PMI_MFG': _cn_item(2008, 1, 2026, 10,
                                             '2026-11-17T02:00:00Z'),
                      'CN_NEW_LOANS': _cn_item(2008, 1, 2026, 10,
                                               '2026-11-17T02:00:00Z')})
q1 = _query(d1)
f1 = _eval_snap_item(d1, 'CN_PMI_MFG 走势', '2026-11-17')
check('F1 首次采集 fresh → 查询 collection_status 三分'
      '(fresh/最后成功采集/统计期)+判定 satisfied',
      st1['CN_PMI_MFG']['mode'] == 'fresh'
      and q1['collection_status']['mode'] == 'fresh'
      and q1['collection_status']['last_success_at']
      == '2026-11-17T02:00:00Z'
      and q1['collection_status']['last_observation_period']
      == '2026-10-01'
      and q1['source']['file_date'] == _latest_ymd(d1)
      and f1['outcome'] == 'satisfied',
      json.dumps(q1.get('collection_status'), ensure_ascii=False))

# F1b merge_macro_series prov_out 提升(快照平节 series_provenance)
store1, prov1 = {}, {}
_item1 = json.loads(json.dumps(
    _cn_item(2021, 1, 2026, 10, '2026-11-17T02:00:00Z')))
sb.merge_macro_series(store1, {'macro': {'data': {'CN_PMI_MFG': _item1}}},
                      prov_out=prov1)
check('F1b merge_macro_series provenance → prov_out 平节(返回形状不变)',
      'CN_PMI_MFG' in store1 and prov1.get('CN_PMI_MFG', {}).get(
          'fetched_at') == '2026-11-17T02:00:00Z')

# F2 连续第二次采集 fresh: last_success_at 前移,统计期不变
st2 = _run_round(d1, {'CN_PMI_MFG': _cn_item(2008, 1, 2026, 10,
                                             '2026-11-17T04:00:00Z')})
q2 = _query(d1)
check('F2 连续第二次采集 → fresh 复跑成功(最后成功采集前移)',
      st2['CN_PMI_MFG']['mode'] == 'fresh'
      and q2['collection_status']['last_success_at']
      == '2026-11-17T04:00:00Z'
      and q2['collection_status']['last_observation_period']
      == '2026-10-01')

# F3 美国宏观刷新: CN 序列仍在档(DFF 刷新不遮蔽)+查询/判定正常
st3 = _run_round(d1, {'CN_PMI_MFG': _cn_item(2008, 1, 2026, 10,
                                             '2026-11-17T06:00:00Z')},
                 us={'DFF': {'value': 4.33, 'date': '2026-11-14',
                             'frequency': 'daily'}})
q3 = _query(d1)
check('F3 美国宏观刷新 → CN 仍在档 fresh(不遮蔽)',
      st3['CN_PMI_MFG']['mode'] == 'fresh'
      and len(q3['dates']) == 226
      and q3['collection_status']['mode'] == 'fresh')

# F4 同日单项失败(部分面): R26守卫转存——旧完整档保持规范,DFF/CN不丢
st4 = _run_round(d1, {'CN_NEW_LOANS': _cn_item(2008, 1, 2026, 10,
                                               '2026-11-17T08:00:00Z')})
q4 = _query(d1)
f4 = _eval_item(d1, '近三年 CN_PMI_MFG 走势', '2026-11-17')
_canon4 = json.load(open(os.path.join(
    d1, 'data', 'daily', 'macro_%s.json' % _latest_ymd(d1)),
    encoding='utf-8'))
_sup4 = [f for f in os.listdir(os.path.join(d1, 'data', 'daily',
                                            'superseded'))
         if f.startswith('macro_') and not f.startswith('.lock.')]
check('F4 同日部分面(丢DFF身份)→守卫转存,规范档保完整(DFF+CN在档)',
      st4['CN_NEW_LOANS']['mode'] == 'fresh'
      and 'DFF' in _canon4['data'] and 'CN_PMI_MFG' in _canon4['data']
      and q4['collection_status']['mode'] == 'fresh'
      and q4['collection_status']['last_success_at']
      == '2026-11-17T06:00:00Z'
      and _sup4
      and any(json.load(open(os.path.join(d1, 'data', 'daily',
                                          'superseded', f),
                                 encoding='utf-8'))
              ['cn_history']['CN_PMI_MFG']['mode'] == 'carry_forward'
              for f in _sup4)
      and f4['outcome'] == 'satisfied',
      f"canon指标数={len(_canon4['data'])} sup={len(_sup4)}")

# F4c 跨日单项失败: carry_forward 正道(昨日档续存,披露可见,任务窗满足)
st4c = _run_round(d1, {'CN_NEW_LOANS': _cn_item(2008, 1, 2026, 10,
                                                '2026-11-18T08:00:00Z')},
                  day=(2026, 11, 21))
q4c = _query(d1)
f4c = _eval_item(d1, '近三年 CN_PMI_MFG 走势', '2026-11-21')
check('F4c 跨日单项失败续存 → carry_forward 如实+仍满足任务窗=披露放行',
      st4c['CN_PMI_MFG']['mode'] == 'carry_forward'
      and q4c['collection_status']['mode'] == 'carry_forward'
      and q4c['collection_status']['last_success_at']
      == '2026-11-17T06:00:00Z'
      and q4c['collection_status']['last_observation_period']
      == '2026-10-01'
      and f4c['outcome'] == 'satisfied'
      and '续用披露' in f4c['outcome_basis'],
      f4c['outcome_basis'][-80:])

# F5 跨日两项失败: 双续存,查询/判定如实
st5 = _run_round(d1, RuntimeError('CN 端点不可达'), day=(2026, 11, 22))
q5 = _query(d1)
q5b = _query(d1, 'CN_NEW_LOANS')
f5 = _eval_item(d1, '近三年 CN_PMI_MFG 走势', '2026-11-22')
check('F5 跨日两项失败 → 双 carry_forward(最后成功采集不冒充本轮)',
      st5['CN_PMI_MFG']['mode'] == 'carry_forward'
      and st5['CN_NEW_LOANS']['mode'] == 'carry_forward'
      and q5['collection_status']['last_success_at']
      == '2026-11-17T06:00:00Z'
      and q5b['collection_status']['last_success_at']
      == '2026-11-18T08:00:00Z'
      and f5['outcome'] == 'satisfied'
      and f5['spec'].get('collection_status', {}).get('mode')
      == 'carry_forward')

# F6 无历史可续用: 如实缺席不造史(查询无序列→判定 missing)
d6 = _new_data_root()
st6 = _run_round(d6, RuntimeError('CN 端点不可达'))
q6s, q6e = wd.metric_series('CN_PMI_MFG', None, d6)
f6 = ro._evaluate_data_requirements(
    ['CN_PMI_MFG'], [], {'target_date': '2026-11-17'}, [],
    question='CN_PMI_MFG 走势',
    registry={'CN_PMI_MFG': {'frequency': 'monthly'}})[0]
check('F6 无历史可续用 → absent 如实缺席(查询无序列+判定 missing)',
      st6['CN_PMI_MFG']['mode'] == 'absent'
      and q6s is None
      and f6['outcome'] == 'missing',
      f"q={q6e} outcome={f6['outcome']}")

# F7 合理续用: report 渲染续用披露+可交付(正例)
rdF7 = make_run(tmp, 'f7', req_items=[f4c])
aj.record_semantic_verdict(eroot, rdF7, 'UPHELD', 'R7-F7')
eF7 = stage_report(rdF7, eroot)
mdF7 = open(os.path.join(rdF7, 'report.md'), encoding='utf-8').read()
check('F7 合理续用 → report 面续用披露可见+deliverable',
      eF7.get('deliverable') is True
      and '续用披露' in mdF7
      and 'CN_PMI_MFG' in mdF7)

# F8 严重陈旧续用(外审反例: 截至 2020-12-01 各 156 点+采集失败,
#    基线 history ok/warnings 空/report/archive 全过)
d8 = _new_data_root()
_old = {'date': '2020-12-01', 'value': 51.8, 'prev': 51.4,
        'frequency': 'monthly', 'unit': 'index_point',
        'series': {'dates': monthrange(2008, 1, 2020, 12),
                   'values': [50.0] * 156},
        'provenance': {'source': 'akshare_em(macro_china_pmi)',
                       'fetched_at': '2020-12-31T02:00:00Z'}}
_old_d = dict(_old)
_old_d['provenance'] = dict(_old['provenance'])
json.dump({'date': '20261115', 'data': {'CN_PMI_MFG': _old_d,
                                        'CN_NEW_LOANS': _old_d},
           'alerts': [], 'derived': {}},
          open(os.path.join(d8, 'data', 'daily', 'macro_20261115.json'),
               'w', encoding='utf-8'), ensure_ascii=False)
st8 = _run_round(d8, RuntimeError('CN 端点不可达'))
q8 = _query(d8)
f8 = _eval_item(d8, 'CN_PMI_MFG 走势', '2026-11-17')
rdF8 = make_run(tmp, 'f8', req_items=[f8])
eF8 = stage_report(rdF8, eroot)
aF8 = stage_archive(rdF8, eroot, os.path.join(tmp, 'arcF8'))
mdF8 = open(os.path.join(rdF8, 'report.md'), encoding='utf-8').read()
check('F8 严重陈旧续用 → stale_for_task 阻断+report 拒+archive 拒',
      st8['CN_PMI_MFG']['mode'] == 'carry_forward'
      and q8['collection_status']['mode'] == 'carry_forward'
      and q8['collection_status']['last_observation_period']
      == '2020-12-01'
      and q8['collection_status']['last_success_at']
      == '2020-12-31T02:00:00Z'
      and f8['outcome'] == 'stale_for_task'
      and '数据过期' in f8['outcome_basis']
      and eF8.get('deliverable') is False
      and eF8.get('blocked_class') == 'required_data_missing'
      and aF8.returncode != 0
      and '数据陈旧' in mdF8,
      f"outcome={f8['outcome']} bc={eF8.get('blocked_class')} "
      f"rc={aF8.returncode}")

# F9 合法历史回放: 同陈旧档,回放时点 2021-01-15(距统计期 45 天≤容忍)
#    → 参考端=回放时点不误判,satisfied+续用披露+可交付
f9 = _eval_item(d8, 'CN_PMI_MFG 走势', '2021-01-15')
rdF9 = make_run(tmp, 'f9', req_items=[f9])
aj.record_semantic_verdict(eroot, rdF9, 'UPHELD', 'R7-F9')
eF9 = stage_report(rdF9, eroot)
check('F9 合法历史回放(as_of 钉 2021-01-15) → satisfied 不误判'
      '+deliverable',
      f9['outcome'] == 'satisfied'
      and '续用披露' in f9['outcome_basis']
      and f9['spec']['collection_status']['freshness']['reference']
      == '2021-01-15'
      and eF9.get('deliverable') is True,
      f"outcome={f9['outcome']} bc={eF9.get('blocked_class')}")

# F10 ia_cli history 信封发射面(生产 cmd_history 真调): 陈旧续用档
#     → 信封带 collection_status+续用警告(查询层不再静默)
import ia_cli  # noqa: E402
import argparse as _ap  # noqa: E402
import io as _io  # noqa: E402
_args10 = _ap.Namespace(metric='CN_PMI_MFG', start=None, end=None)
_out10, _old10 = _io.StringIO(), sys.stdout
ia_cli.ROOT = d8
sys.stdout = _out10
try:
    ia_cli.cmd_history(_args10)
except SystemExit as _e10:
    if _e10.code not in (0, None):
        _r10 = None
finally:
    sys.stdout = _old10
ia_cli.ROOT = ROOT
try:
    _e10 = json.loads(_out10.getvalue())
except Exception:
    _e10 = {}
_s10 = (_e10.get('data') or {}).get('series') or {}
check('F10 ia_cli history 信封 → collection_status 随信封+续用警告',
      _e10.get('ok') is True
      and (_s10.get('collection_status') or {}).get('mode')
      == 'carry_forward'
      and (_s10.get('collection_status') or {})
      .get('last_observation_period') == '2020-12-01'
      and any('续用' in w or 'carry_forward' in w
              for w in (_e10.get('warnings') or [])),
      json.dumps(_e10.get('warnings'), ensure_ascii=False)[:120])

cmc.fetch_macro_history = _ORIG_FETCH_MH
mc.DATA_DIR = _MC_DATA_DIR_ORIG
for _d in (d1, d6, d8):
    shutil.rmtree(_d, ignore_errors=True)

shutil.rmtree(tmp, ignore_errors=True)

print('═' * 64)
print(f'Audit-R7 判定: {PASS} PASS / {FAIL} FAIL')
print('═' * 64)
sys.exit(0 if FAIL == 0 else 1)
