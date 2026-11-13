#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R22 金融正确性(Charter 10 §五 P0: 5.1/5.2/5.3/5.4)修复回归锁。

先复现后修(audit/R22_FIN_CORRECTNESS_REPRO.py 为修复前反例档):
  §1 5.1 方向语义纯函数: 报价对(USDJPY/EURUSD/GBPUSD/USDCNY)计价货币侧
     反转/基准侧与报价对名义直接/相对措辞主体=前侧/未识别披露;
     收益率类价格侧反转/收益率侧与缺省直接;未登记指标零介入。
  §2 5.1 verify_expiry 集成: "日元升值"+USDJPY 150→145 → supports
     (修复前 against=Charter 原文案错判);"国债价格上涨"+收益率下行 →
     supports;direction_hint 语义=指标数值方向+direction_semantics 披露。
  §3 5.2 到期新鲜度: 到期日附近观测滞后>允许阈值(frequency 驱生) →
     INSUFFICIENT_DATA+freshness 五要素;新鲜案例正常判;LEVEL_TARGET 同门。
  §4 5.3 标签-证据绑定: validate_vp 纯校验(判定标签无 verdict=无据可查;
     verdict 绑定不符=拒)+binding_check 活体(BINDING_VIOLATION/LABEL_DRIFT
     /NO_MACHINE_BOUNDary 边界)+CLI --verify-binding 退出码。
  §5 5.4 mode A vintage 二次过滤: vintage 快照夹带 obs>publish 被滤+
     obs_le_publish_filter 披露;approx 分支行为与披露保持。
  §6 契约锁: legacy directions 直接比对零语义介入;verdict_to_label
     单 token 映射不变;复合 verdict 全同段取该标签。
全合成(合成快照/views/VP);真实 registry+config;CI 干净 clone 可跑。
"""
import datetime as dt
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f'  ✅ {name}')
    else:
        FAIL += 1
        print(f'  ❌ {name} {detail}')


def section(title):
    print('═' * 64)
    print(f'[{title}]')
    print('═' * 64)


import workbench_data as wd            # noqa: E402
import view_store as vs                # noqa: E402
import view_verifier as vv             # noqa: E402
import view_plausibility as vpl        # noqa: E402
import direction_semantics as dsem     # noqa: E402

REG = wd.load_registry(ROOT)
TMAP = vv.load_forecast_target_map()
SEM = dsem.load_semantics()
TD = tempfile.mkdtemp(prefix='r22t_')
VIEWS_DIR = os.path.join(TD, 'views')
VP_DIR = os.path.join(TD, 'vp')
DAILY = os.path.join(TD, 'data', 'daily')
for d in (VIEWS_DIR, VP_DIR, DAILY):
    os.makedirs(d)

SYN_MAP = {'schema_version': '1.0', 'subjects': {
    'US_rates': {'note': '合成', 'metrics': [
        'UST_10Y', 'USDJPY', 'EURUSD', 'DXY', 'FED_FUNDS', 'SPX']}}}


def iso(ymd):
    return f'{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}'


def daily_series(start, end, v0, v1):
    n = max((dt.date.fromisoformat(end) - dt.date.fromisoformat(start)).days, 1)
    dates, vals = [], []
    for i in range(n + 1):
        d = dt.date.fromisoformat(start) + dt.timedelta(days=i)
        if d.weekday() >= 5:
            continue
        dates.append(d.isoformat())
        vals.append(round(v0 + (v1 - v0) * i / n, 6))
    return dates, vals


def mk_view(vid, publish, horizon, forecasts):
    doc = {
        'schema_version': '1.1', 'view_id': vid,
        'institution': {'name': 'Synthetic Bank', 'type': 'investment_bank',
                        'department': 'Research'},
        'authors': [], 'report_title': 'Syn ' + vid,
        'source_url': 'https://example.com/' + vid,
        'source_type': 'official_site', 'publish_date': publish,
        'fetch_date': '2026-11-10', 'access_level': 'public_full',
        'view_horizon': horizon, 'subjects': ['US_rates'],
        'core_views': [{'statement': '合成观点。',
                        'attribution': 'institution_stated',
                        'basis': 'verbatim_quote', 'quote': 'Synthetic.'}],
        'forecasts': forecasts, 'key_assumptions': [], 'evidence_cited': [],
        'mechanism_steps': [], 'risk_factors': [], 'falsification_conditions': [],
        'revisions': [], 'completeness_notes': '合成',
        'copyright_note': 'meta+link',
    }
    with open(os.path.join(VIEWS_DIR, vid + '.json'), 'w',
              encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False)
    return doc


def mk_snap(sid, ymd, series_map, extra_facts=()):
    facts = []
    for mid, (dates, values) in series_map.items():
        m = next(x for x in REG['metrics'] if x['metric_id'] == mid)
        facts.append({'metric_id': mid, 'display_name': m['display_name'],
                      'value': values[-1], 'unit': m.get('unit', ''),
                      'observation_date': dates[-1], 'quality_status': 'PASS'})
    facts.extend(extra_facts)
    snap = {'snapshot_id': sid, 'target_date': ymd,
            'research_as_of': f'{iso(ymd)}T20:00:00+08:00',
            'gate_a': {'status': 'PASS', 'core_missing': [],
                       'noncore_missing': [], 'noncore_missing_detail': {},
                       'noncore_degraded': []},
            'facts': facts,
            'series_store': {mid: {'dates': d, 'values': v}
                             for mid, (d, v) in series_map.items()}}
    with open(os.path.join(DAILY, sid + '.json'), 'w', encoding='utf-8') as f:
        json.dump(snap, f, ensure_ascii=False)
    return snap


def expiry_row(vid, snap, forecasts_key=0):
    with redirect_stdout(io.StringIO()):
        out = vv.verify_expiry(vid, snap, REG, SYN_MAP, views_dir=VIEWS_DIR,
                               target_map=TMAP)
    return out, out['forecast_verdicts'][forecasts_key]


# ════════════════════════════════════════════════════════════════════
section('1 · 5.1 方向语义纯函数(direction_semantics)')
# ════════════════════════════════════════════════════════════════════
h, n = dsem.apply_metric_direction_semantics('up', 'USDJPY', ['日元', '日元升值'])
check('USDJPY 计价货币侧(日元升值)→ 反转 up→down',
      h == 'down' and n['subject_side'] == 'quote' and n['inverted'] is True)
h, n = dsem.apply_metric_direction_semantics('up', 'USDJPY',
                                             ['美元兑日元', '美元兑日元将上行'])
check('USDJPY 报价对名义(美元兑日元上行)→ 直接',
      h == 'up' and n['subject_side'] == 'pair' and n['inverted'] is False)
h, n = dsem.apply_metric_direction_semantics('up', 'USDJPY',
                                             ['日元', '日元相对美元走强'])
check('USDJPY 相对措辞主体=前侧(日元相对美元)→ 反转',
      h == 'down' and n['subject_side'] == 'quote')
h, n = dsem.apply_metric_direction_semantics('up', 'USDJPY',
                                             ['美元', '美元走强(对一篮子)'])
check('USDJPY 基准货币侧(美元走强)→ 直接',
      h == 'up' and n['subject_side'] == 'base')
h, n = dsem.apply_metric_direction_semantics('down', 'USDJPY',
                                             ['美元与日元同步波动', '下行'])
check('USDJPY 双币同现无结构 → 未识别=直接比对+披露(不猜主体)',
      h == 'down' and n['subject_side'] == 'unspecified'
      and '未识别' in n['basis'])
h, n = dsem.apply_metric_direction_semantics('up', 'EURUSD', ['欧元', '欧元升值'])
check('EURUSD 基准侧(欧元升值)→ 直接',
      h == 'up' and n['subject_side'] == 'base')
h, n = dsem.apply_metric_direction_semantics('down', 'EURUSD',
                                             ['欧元兑美元', 'EURUSD 走低'])
check('EURUSD 报价对名义(EN 词边界)→ 直接', h == 'down'
      and n['subject_side'] == 'pair')
h, n = dsem.apply_metric_direction_semantics('up', 'USDCNY', ['人民币', '人民币升值'])
check('USDCNY 计价侧(人民币升值)→ 反转', h == 'down')
h, n = dsem.apply_metric_direction_semantics('up', 'UST_10Y',
                                             ['美国10年期国债', '国债价格上涨'])
check('收益率类价格侧(国债价格上涨)→ 反转',
      h == 'down' and n['subject_side'] == 'price')
h, n = dsem.apply_metric_direction_semantics('up', 'UST_10Y',
                                             ['美国10年期国债', '收益率上行'])
check('收益率类收益率侧 → 直接', h == 'up' and n['subject_side'] == 'yield')
h, n = dsem.apply_metric_direction_semantics('up', 'UST_10Y',
                                             ['10年期国债', '10年期国债上行'])
check('收益率类缺省主体(市场惯例=N年期国债上行指收益率)→ 直接',
      h == 'up' and n['subject_side'] == 'yield')
h, n = dsem.apply_metric_direction_semantics('up', 'SPX', ['标普500', '上涨'])
check('未登记指标(SPX)→ 零介入(直接比对,无披露节点)', h == 'up' and n is None)
h, n = dsem.apply_metric_direction_semantics(None, 'USDJPY', ['日元', '目标 140'])
check('hint=None(点位型)→ 原样返回不进语义层', h is None and n is None)
h, n = dsem.apply_metric_direction_semantics('up', 'DXY', ['美元指数', '美元走强'])
check('DXY(fx_index,未登记=无反转风险)→ 直接', h == 'up' and n is None)
sem_rules = set(SEM['rules'])
reg_ids = {m['metric_id'] for m in REG['metrics']}
check('语义表条目全部在注册表(无悬空引用)', sem_rules <= reg_ids,
      str(sem_rules - reg_ids))
fx_pairs = [m['metric_id'] for m in REG['metrics']
            if m.get('asset_class') == 'fx_rate']
check('全部 fx_rate 报价对已登记语义(USDJPY/EURUSD/GBPUSD/USDCNY)',
      set(fx_pairs) <= sem_rules, str(set(fx_pairs) - sem_rules))
tsy_yields = [m['metric_id'] for m in REG['metrics']
              if m.get('asset_class') == 'rates_yield'
              and m['metric_id'].split('_')[0] in ('UST', 'JGB', 'BUND')]
check('全部国债收益率族(UST/JGB/BUND)已登记语义(价格措辞反转面;SOFR='
      '隔夜融资率无国债价格对偶,如实不登记)',
      set(tsy_yields) <= sem_rules, str(set(tsy_yields) - sem_rules))

# ════════════════════════════════════════════════════════════════════
section('2 · 5.1 verify_expiry 集成(修复前 against → supports)')
# ════════════════════════════════════════════════════════════════════
dj, vj = daily_series('2026-01-15', '2026-11-10', 152.0, 145.0)   # USDJPY ↓
de, ve = daily_series('2026-01-15', '2026-11-10', 1.06, 1.15)     # EURUSD ↑
du, vu = daily_series('2026-01-15', '2026-11-10', 4.3, 3.6)       # 收益率 ↓
dx, vx = daily_series('2026-01-15', '2026-11-10', 100.0, 106.0)   # DXY ↑
SNAP1 = mk_snap('research_snapshot_20261110', '20261110',
                {'USDJPY': (dj, vj), 'EURUSD': (de, ve),
                 'UST_10Y': (du, vu), 'DXY': (dx, vx)})
mk_view('VIEW-20260501-101', '2026-05-01', '6m', forecasts=[
    {'target': '日元', 'value_or_direction': '日元升值',
     'horizon': '6m', 'attribution': 'institution_stated'},
    {'target': '美元兑日元', 'value_or_direction': '美元兑日元上行',
     'horizon': '6m', 'attribution': 'institution_stated'},
    {'target': '欧元兑美元', 'value_or_direction': '欧元升值',
     'horizon': '6m', 'attribution': 'institution_stated'},
    {'target': '美国10年期国债', 'value_or_direction': '国债价格上涨',
     'horizon': '6m', 'attribution': 'institution_stated'},
    {'target': '美国10年期国债', 'value_or_direction': '收益率上行',
     'horizon': '6m', 'attribution': 'institution_stated'},
    {'target': '美元指数', 'value_or_direction': '美元走强',
     'horizon': '6m', 'attribution': 'institution_stated'}])
_, r = expiry_row('VIEW-20260501-101', SNAP1, 0)
check('日元升值+USDJPY 150→145 → supports(Charter 原文案,修复前 against)',
      r['verdict'] == 'supports' and r['direction_hint'] == 'down'
      and r['actual_direction'] == 'down', str(r))
check('direction_semantics 披露随行(主体=quote/反转=True/词义 vs 指标方向)',
      r.get('direction_semantics', {}).get('subject_side') == 'quote'
      and r['direction_semantics']['inverted'] is True
      and r['direction_semantics']['direction_word_meaning'] == 'up'
      and r['direction_semantics']['metric_direction'] == 'down')
_, r = expiry_row('VIEW-20260501-101', SNAP1, 1)
check('美元兑日元上行+USDJPY 实际下行 → against(报价对名义直接比对)',
      r['verdict'] == 'against' and r['direction_hint'] == 'up'
      and r['direction_semantics']['subject_side'] == 'pair')
_, r = expiry_row('VIEW-20260501-101', SNAP1, 2)
check('欧元升值+EURUSD 上行 → supports + 映射在册(R22 扩 EURUSD 报价对键;'
      ' target 含对名→pair 侧直接)',
      r['verdict'] == 'supports' and r['metric_id'] == 'EURUSD'
      and r['direction_semantics']['subject_side'] == 'pair', str(r)[:120])
_, r = expiry_row('VIEW-20260501-101', SNAP1, 3)
check('国债价格上涨+收益率 4.3→3.6 下行 → supports(修复前 against)',
      r['verdict'] == 'supports' and r['direction_hint'] == 'down'
      and r['direction_semantics']['subject_side'] == 'price')
_, r = expiry_row('VIEW-20260501-101', SNAP1, 4)
check('收益率上行+收益率实际下行 → against(收益率侧直接,语义不改判)',
      r['verdict'] == 'against' and r['direction_hint'] == 'up')
_, r = expiry_row('VIEW-20260501-101', SNAP1, 5)
check('美元走强+DXY 上行 → supports(fx_index 直接)',
      r['verdict'] == 'supports' and r['metric_id'] == 'DXY')

# ════════════════════════════════════════════════════════════════════
section('3 · 5.2 到期数据新鲜度(滞后>允许阈值=证据不足)')
# ════════════════════════════════════════════════════════════════════
# 月频: 到期 2025-11-01, 最后观测 2025-06-30(滞后 124 天 > 60)
SNAP2 = mk_snap('research_snapshot_20261110b', '20261110',
                {'FED_FUNDS': (['2025-04-30', '2025-05-31', '2025-06-30'],
                               [4.25, 4.30, 4.33])})
mk_view('VIEW-20250501-201', '2025-05-01', '6m', forecasts=[
    {'target': '联邦基金利率', 'value_or_direction': '上行',
     'horizon': '6m', 'attribution': 'institution_stated'}])
_, r = expiry_row('VIEW-20250501-201', SNAP2, 0)
check('月频滞后 124 天>60 → INSUFFICIENT_DATA 不判对错(修复前 neutral 判)',
      r['verdict'] == 'INSUFFICIENT_DATA'
      and '新鲜观测' in r['note'] and '不判' in r['note'], str(r))
fr = r.get('freshness', {})
check('freshness 五要素披露(到期日/实际观测日/允许滞后/频次/质量+发布面)',
      fr.get('prediction_due') == '2025-11-01'
      and fr.get('actual_observation_date') == '2025-06-30'
      and fr.get('gap_days') == 124 and fr.get('allowed_lag_days') == 60
      and fr.get('frequency') == 'monthly'
      and fr.get('fresh') is False
      and fr.get('release_date') is None
      and '未入库' in fr.get('release_date_basis', ''), str(fr))
# 月频新鲜案例: 到期 2025-11-30, 最后观测 2025-11-30(滞后 0)
SNAP3 = mk_snap('research_snapshot_20261110c', '20261110',
                {'FED_FUNDS': (['2025-04-30', '2025-09-30', '2025-11-30'],
                               [4.25, 4.30, 4.38])})
mk_view('VIEW-20250501-202', '2025-05-01', '6m', forecasts=[
    {'target': '联邦基金利率', 'value_or_direction': '上行',
     'horizon': '2025-11-30', 'attribution': 'institution_stated'}])
_, r = expiry_row('VIEW-20250501-202', SNAP3, 0)
check('月频新鲜(滞后 0)→ 正常判 supports(新鲜度门不误伤)',
      r['verdict'] == 'supports' and r['freshness']['gap_days'] == 0
      and r['freshness']['fresh'] is True, str(r))
# 日频界: 到期 2025-11-05, 最后观测 2025-10-24(滞后 12>10 → 不足)
# (序列自 2025-01-15 起: interval_change 基准须严格早于 publish 2025-05-01)
d5, v5 = daily_series('2025-01-15', '2025-10-24', 151.0, 148.0)
SNAP4 = mk_snap('research_snapshot_20261110d', '20261110',
                {'USDJPY': (d5, v5)})
mk_view('VIEW-20250501-203', '2025-05-01', '6m', forecasts=[
    {'target': '日元', 'value_or_direction': '日元升值',
     'horizon': '2025-11-05', 'attribution': 'institution_stated'}])
_, r = expiry_row('VIEW-20250501-203', SNAP4, 0)
check('日频滞后 12 天>10 → INSUFFICIENT_DATA(daily 允许阈值)',
      r['verdict'] == 'INSUFFICIENT_DATA'
      and r['freshness']['allowed_lag_days'] == 10
      and r['freshness']['gap_days'] == 12)
# 日频新鲜: 同上但序列补到 2025-11-04(滞后 1)
d6, v6 = daily_series('2025-01-15', '2025-11-04', 151.0, 147.0)
SNAP5 = mk_snap('research_snapshot_20261110e', '20261110',
                {'USDJPY': (d6, v6)})
_, r = expiry_row('VIEW-20250501-203', SNAP5, 0)
check('日频滞后 1 天 → 判 supports(日元升值+USDJPY 下行)',
      r['verdict'] == 'supports' and r['freshness']['gap_days'] == 1)
# LEVEL_TARGET 同门: 点位型 + 陈旧序列 → 证据不足不报"到期实际值"
mk_view('VIEW-20250501-204', '2025-05-01', '6m', forecasts=[
    {'target': '美元兑日元', 'value_or_direction': '到 140 附近',
     'horizon': '2025-11-05', 'attribution': 'institution_stated'}])
_, r = expiry_row('VIEW-20250501-204', SNAP4, 0)
check('点位型+陈旧序列 → INSUFFICIENT_DATA(不冒充到期实际值)',
      r['verdict'] == 'INSUFFICIENT_DATA' and 'actual_observation' not in r)

# ════════════════════════════════════════════════════════════════════
section('4 · 5.3 标签-证据绑定(validate_vp 纯校验 + binding_check 活体)')
# ════════════════════════════════════════════════════════════════════
vd = mk_view('VIEW-20261110-301', '2026-11-10', '12m', forecasts=[
    {'target': '联邦基金利率', 'value_or_direction': '上行',
     'horizon': '12m', 'attribution': 'institution_stated'}])


def mk_vp(hyps, view_label, vid='VIEW-20261110-301'):
    return {'schema_version': '1.0', 'view_id': vid,
            'generated_by': 'synthetic', 'hypotheses': hyps,
            'view_label': view_label}


ok, errs = vpl.validate_vp(mk_vp([{
    'label': 'SUPPORTED', 'ref': {'kind': 'core_view', 'index': 0},
    'metric_refs': [{'metric_id': 'FED_FUNDS', 'direction': 'up'}],
    'evidence': {'mode': 'C', 'forecast_index': 0}}], 'SUPPORTED'), vd)
check('判定标签+mode C 绑定无 verdict → 拒(无据可查,修复前放行)',
      not ok and any('无据可查' in e for e in errs), str(errs))
ok, errs = vpl.validate_vp(mk_vp([{
    'label': 'SUPPORTED', 'ref': {'kind': 'core_view', 'index': 0},
    'metric_refs': [{'metric_id': 'FED_FUNDS', 'direction': 'up'}],
    'evidence': {'mode': 'C', 'forecast_index': 0,
                 'verdict': 'NOT_YET_TESTABLE'}}], 'SUPPORTED'), vd)
check('底证 verdict=NOT_YET_TESTABLE 撑 SUPPORTED → 拒(Charter 原文条款)',
      not ok and any('绑定不符' in e for e in errs), str(errs))
ok, errs = vpl.validate_vp(mk_vp([{
    'label': 'NOT_YET_TESTABLE', 'ref': {'kind': 'core_view', 'index': 0},
    'metric_refs': [{'metric_id': 'FED_FUNDS', 'direction': 'up'}],
    'evidence': {'mode': 'C', 'forecast_index': 0,
                 'verdict': 'NOT_YET_TESTABLE'}}], 'NOT_YET_TESTABLE'), vd)
check('底证与标签一致(NOT_YET_TESTABLE)→ 过(合法档不受新门影响)',
      ok, str(errs))
ok, errs = vpl.validate_vp(mk_vp([{
    'label': 'NOT_YET_TESTABLE', 'ref': {'kind': 'core_view', 'index': 0},
    'metric_refs': [{'metric_id': 'FED_FUNDS', 'direction': 'up'}],
    'evidence': {'mode': 'C', 'forecast_index': 0,
                 'verdict': 'NOT_YET_TESTABLE/NOT_YET_TESTABLE'}}],
    'NOT_YET_TESTABLE'), vd)
check('复合 verdict 全同段(NOT_YET_TESTABLE/…)→ 取该标签一致通过',
      ok, str(errs))
check('verdict_to_label 单 token 映射契约不变',
      vpl.verdict_to_label('supports') == 'SUPPORTED'
      and vpl.verdict_to_label('against') == 'CONTRADICTED'
      and vpl.verdict_to_label('NOT_MACHINE_VERIFIABLE') == 'INSUFFICIENT_EVIDENCE'
      and vpl.verdict_to_label('unknown_thing') == 'INSUFFICIENT_EVIDENCE'
      and vpl.verdict_to_label('supports/against') == 'INSUFFICIENT_EVIDENCE')
# 活体: 伪造 supports verdict 的未到期预测 → BINDING_VIOLATION
vp_fab = mk_vp([{
    'label': 'SUPPORTED', 'ref': {'kind': 'core_view', 'index': 0},
    'metric_refs': [{'metric_id': 'FED_FUNDS', 'direction': 'up'}],
    'evidence': {'mode': 'C', 'forecast_index': 0, 'verdict': 'supports'}}],
    'SUPPORTED')
ok, errs = vpl.validate_vp(vp_fab, vd)
check('伪造 supports verdict 通过纯校验(结构自洽)——需活体复核兜底',
      ok, str(errs))
b = vpl.binding_check(doc=vp_fab, snapshot=SNAP1, registry=REG, vmap=SYN_MAP,
                      views_dir=VIEWS_DIR, target_map=TMAP, root=TD)
check('binding_check 活体: 当前引擎 NOT_YET_TESTABLE vs 声明 SUPPORTED → '
      'BINDING_VIOLATION + ok=False',
      b['rows'][0]['status'] == 'BINDING_VIOLATION' and b['ok'] is False
      and b['rows'][0]['recomputed_label'] == 'NOT_YET_TESTABLE',
      json.dumps(b['rows'][0], ensure_ascii=False)[:200])
# 活体: 漂移(存量 verdict 过期)披露不阻断
vp_drift = mk_vp([{
    'label': 'NOT_YET_TESTABLE', 'ref': {'kind': 'core_view', 'index': 0},
    'metric_refs': [{'metric_id': 'FED_FUNDS', 'direction': 'up'}],
    'evidence': {'mode': 'C', 'forecast_index': 0,
                 'verdict': 'NOT_MACHINE_VERIFIABLE'}}], 'NOT_YET_TESTABLE')
b = vpl.binding_check(doc=vp_drift, snapshot=SNAP1, registry=REG,
                      vmap=SYN_MAP, views_dir=VIEWS_DIR, target_map=TMAP,
                      root=TD)
check('binding_check 活体: 存量 verdict 过期(NOT_MACHINE_VERIFIABLE→'
      'NOT_YET_TESTABLE)= LABEL_DRIFT 披露不阻断',
      b['rows'][0]['status'] == 'LABEL_DRIFT' and b['ok'] is True,
      json.dumps(b['rows'][0], ensure_ascii=False)[:200])
# 活体: 一致档 → BINDING_OK; 无 mode C 绑定 → 人工审查边界
vp_ok = mk_vp([{
    'label': 'NOT_YET_TESTABLE', 'ref': {'kind': 'core_view', 'index': 0},
    'metric_refs': [{'metric_id': 'FED_FUNDS', 'direction': 'up'}],
    'evidence': {'mode': 'C', 'forecast_index': 0,
                 'verdict': 'NOT_YET_TESTABLE'}}], 'NOT_YET_TESTABLE')
b = vpl.binding_check(doc=vp_ok, snapshot=SNAP1, registry=REG, vmap=SYN_MAP,
                      views_dir=VIEWS_DIR, target_map=TMAP, root=TD)
check('binding_check 活体: 一致档 → BINDING_OK',
      b['rows'][0]['status'] == 'BINDING_OK' and b['ok'] is True)
vp_sem = mk_vp([{
    'label': 'INSUFFICIENT_EVIDENCE', 'ref': {'kind': 'core_view', 'index': 0},
    'metric_refs': [{'metric_id': 'FED_FUNDS', 'direction': 'up'}],
    'evidence': {'mode': 'A'}}], 'INSUFFICIENT_EVIDENCE')
b = vpl.binding_check(doc=vp_sem, snapshot=SNAP1, registry=REG, vmap=SYN_MAP,
                      views_dir=VIEWS_DIR, target_map=TMAP, root=TD)
check('无 mode C 绑定 → NO_MACHINE_BINDING+解释边界标注(AI/人工审查面)',
      b['rows'][0]['status'] == 'NO_MACHINE_BINDING'
      and '人工审查' in b['rows'][0].get('interpretation_boundary', ''))
# CLI 退出码: violation → 1; 一致档 → 0
with open(os.path.join(VP_DIR, 'VP-VIEW-20261110-301.json'), 'w',
          encoding='utf-8') as f:
    json.dump(vp_fab, f, ensure_ascii=False)
with redirect_stdout(io.StringIO()) as so:
    rc = vpl.main(['--verify-binding', 'VIEW-20261110-301',
                   '--vp-dir', VP_DIR, '--views-dir', VIEWS_DIR,
                   '--data-root', TD])
check('CLI --verify-binding 违规档退出码=1', rc == 1, f'rc={rc} {so.getvalue()[:120]}')
with open(os.path.join(VP_DIR, 'VP-VIEW-20261110-301.json'), 'w',
          encoding='utf-8') as f:
    json.dump(vp_ok, f, ensure_ascii=False)
with redirect_stdout(io.StringIO()) as so:
    rc = vpl.main(['--verify-binding', 'VIEW-20261110-301',
                   '--vp-dir', VP_DIR, '--views-dir', VIEWS_DIR,
                   '--data-root', TD])
check('CLI --verify-binding 一致档退出码=0(--data-root 沙箱,CI 干净面可跑)',
      rc == 0, f'rc={rc}')

# ════════════════════════════════════════════════════════════════════
section('5 · 5.4 mode A vintage 二次过滤(OPEN_ISSUES R1-MINOR-4 收口)')
# ════════════════════════════════════════════════════════════════════
dv, vv_ = daily_series('2026-05-01', '2026-09-01', 4.0, 4.2)
dv = dv + ['2026-09-20', '2026-10-05']            # 夹带未来观测
vv_ = vv_ + [4.5, 4.8]
mk_snap('research_snapshot_20260901', '20260901', {'UST_10Y': (dv, vv_)})
mk_view('VIEW-20260915-401', '2026-09-15', '12m', forecasts=[])
with redirect_stdout(io.StringIO()):
    out = vv.verify_at_publish('VIEW-20260915-401', REG, SYN_MAP,
                               views_dir=VIEWS_DIR, root=TD)
ev = [e for e in out.get('evidence', []) if e['metric_id'] == 'UST_10Y'][0]
check('vintage 快照 obs>publish 被二次过滤(修复前吃进 2026-10-05/4.8)',
      ev['observation_date'] == '2026-09-01' and ev['level'] == 4.2,
      f"obs={ev['observation_date']} level={ev['level']}")
filt = out['mode_a_anchor'].get('obs_le_publish_filter', {})
check('二次过滤执行面披露(dropped_series_obs=2)',
      filt.get('dropped_series_obs') == 2 and '二次过滤' in
      out['mode_a_anchor'].get('note', ''), str(filt))
# 无 vintage → approx 分支: 行为保持(截断近似+DEGRADED 披露)
# 专用 root: 只有 20261110 一张快照(publish 2026-09-15 之前无 vintage)
APPROX_ROOT = tempfile.mkdtemp(prefix='r22approx_')
os.makedirs(os.path.join(APPROX_ROOT, 'data', 'daily'))
with open(os.path.join(APPROX_ROOT, 'data', 'daily',
                       'research_snapshot_20261110.json'), 'w',
          encoding='utf-8') as f:
    json.dump(SNAP1, f, ensure_ascii=False)
mk_view('VIEW-20260915-402', '2026-09-15', '12m', forecasts=[])
with redirect_stdout(io.StringIO()):
    out2 = vv.verify_at_publish('VIEW-20260915-402', REG, SYN_MAP,
                                views_dir=VIEWS_DIR, root=APPROX_ROOT)
ev2 = [e for e in out2.get('evidence', []) if e['metric_id'] == 'UST_10Y'][0]
check('approx 分支(无 vintage 树)截断近似行为保持: series_tail_le_publish',
      ev2.get('level_source') == 'series_tail_le_publish'
      and ev2['observation_date'] <= '2026-09-15', str(ev2.get('level_source')))
check('approx 分支披露锚文案保持(approx_filtered/DEGRADED)',
      out2['mode_a_anchor']['anchor'] == 'approx_filtered'
      and out2['mode_a_anchor']['degraded'] is True
      and 'obs_le_publish_filter' in out2['mode_a_anchor'])

# ════════════════════════════════════════════════════════════════════
section('6 · 契约锁(legacy 面/既有行为零回归)')
# ════════════════════════════════════════════════════════════════════
with redirect_stdout(io.StringIO()):
    outL = vv.verify('VIEW-20260915-401', SNAP1, REG, SYN_MAP,
                     views_dir=VIEWS_DIR, directions={'UST_10Y': 'up'})
rel = {e['metric_id']: e['relation'] for e in outL['evidence']}
check('legacy --directions 显式指标方向=直接比对(语义层零介入: 实际下行 '
      'vs hint up → against,且证据行无 direction_semantics 节点)',
      rel.get('UST_10Y') == 'against' and outL['mode'] == 'legacy'
      and all('direction_semantics' not in e for e in outL['evidence']))
_, r = expiry_row('VIEW-20260501-101', SNAP1, 4)
check('收益率上行措辞(无价格词)判定与修复前一致(against 不被语义改判)',
      r['verdict'] == 'against')
mk_view('VIEW-20260501-501', '2026-05-01', '6m', forecasts=[
    {'target': '美债10年', 'value_or_direction': '上行',
     'horizon': '6m', 'attribution': 'institution_stated'}])
_, r = expiry_row('VIEW-20260501-501', SNAP1, 0)
check('c9 既有形态(美债10年上行+收益率实际下行)→ against(与旧套件一致)',
      r['verdict'] == 'against' and r['direction_hint'] == 'up')
map_keys = set(TMAP['targets'])
check('forecast_target_map R22 扩键在册(EURUSD/GBPUSD/USDCNY 报价对键)',
      {'欧元兑美元', '英镑兑美元', '美元兑人民币'} <= map_keys
      and '欧元' not in map_keys and '英镑' not in map_keys
      and '人民币' not in map_keys)
check('扩键全解析到注册表在册指标',
      all(v in reg_ids for v in TMAP['targets'].values()))
check('裸币短键防误配回归锁: 欧元区GDP增长 不映 EURUSD(实测拦截的碰撞)',
      vv._resolve_forecast_metric('欧元区GDP增长', TMAP) is None)
h, n = dsem.apply_metric_direction_semantics('up', 'UST_10Y',
                                             ['美国10年期国债',
                                              '国债价格上涨但收益率维持高位'])
check('收益率档价格+收益率词同现 → 未识别直接比对+披露(不猜)',
      h == 'up' and n['subject_side'] == 'unspecified')

print('═' * 64)
print(f'R22 金融正确性回归锁: PASS={PASS} FAIL={FAIL}')
sys.exit(0 if FAIL == 0 else 1)
