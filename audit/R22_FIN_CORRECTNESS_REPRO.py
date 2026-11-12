#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R22 金融正确性复现脚本(Charter 10 §五 P0——先复现,确认后修复)。

对当前代码(修复前)跑四个问题点的最小反例,输出机器判定结果:
  5.1 汇率/收益率报价方向语义(USDJPY 日元升值案 + 国债价格 vs 收益率案)
  5.2 到期验证数据新鲜度(到期日附近无新鲜观测仍出判)
  5.3 观点标签-证据绑定(底证 NOT_YET_TESTABLE 撑 SUPPORTED 通过校验)
  5.4 mode A vintage 二次过滤缺失(vintage 快照含 obs>publish 直采信)

全合成数据(合成快照/合成views/合成VP),零真实 data/ 依赖。
用法: python3 audit/R22_FIN_CORRECTNESS_REPRO.py   (输出各案复现结果)
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
sys.path.insert(0, os.path.join(ROOT, 'tests'))

import workbench_data as wd       # noqa: E402
import view_store as vs           # noqa: E402
import view_verifier as vv        # noqa: E402
import view_plausibility as vpl   # noqa: E402

REG = wd.load_registry(ROOT)
TMAP = vv.load_forecast_target_map()
TD = tempfile.mkdtemp(prefix='r22repro_')
VIEWS_DIR = os.path.join(TD, 'views')
VP_DIR = os.path.join(TD, 'vp')
DAILY = os.path.join(TD, 'data', 'daily')
os.makedirs(VIEWS_DIR)
os.makedirs(VP_DIR)
os.makedirs(DAILY)


def iso(ymd):
    return f'{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}'


def mk_view(vid, publish, horizon, forecasts, subjects=('US_rates',)):
    doc = {
        'schema_version': '1.1', 'view_id': vid,
        'institution': {'name': 'Synthetic Bank', 'type': 'investment_bank',
                        'department': 'Research'},
        'authors': [], 'report_title': 'Syn ' + vid,
        'source_url': 'https://example.com/' + vid,
        'source_type': 'official_site', 'publish_date': publish,
        'fetch_date': '2026-11-10', 'access_level': 'public_full',
        'view_horizon': horizon, 'subjects': list(subjects),
        'core_views': [{'statement': '合成观点。', 'attribution':
                        'institution_stated', 'basis': 'verbatim_quote',
                        'quote': 'Synthetic.'}],
        'forecasts': forecasts, 'key_assumptions': [], 'evidence_cited': [],
        'mechanism_steps': [], 'risk_factors': [], 'falsification_conditions': [],
        'revisions': [], 'completeness_notes': '合成',
        'copyright_note': 'meta+link',
    }
    with open(os.path.join(VIEWS_DIR, vid + '.json'), 'w',
              encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False)
    return doc


def mk_snap(sid, ymd, series_map):
    """series_map: {mid: (dates, values)}; facts 取各序列尾值。"""
    facts = []
    for mid, (dates, values) in series_map.items():
        m = next(x for x in REG['metrics'] if x['metric_id'] == mid)
        facts.append({'metric_id': mid, 'display_name': m['display_name'],
                      'value': values[-1], 'unit': m.get('unit', ''),
                      'observation_date': dates[-1], 'quality_status': 'PASS'})
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


def daily_series(start, end, v0, v1):
    n = max((dt.date.fromisoformat(end) - dt.date.fromisoformat(start)).days, 1)
    dates, vals = [], []
    for i in range(n + 1):
        d = dt.date.fromisoformat(start) + dt.timedelta(days=i)
        if d.weekday() >= 5:            # 跳周末(交易日近似)
            continue
        dates.append(d.isoformat())
        vals.append(round(v0 + (v1 - v0) * i / n, 6))
    return dates, vals


SYN_MAP = {'schema_version': '1.0', 'subjects': {
    'US_rates': {'note': '合成', 'metrics': ['UST_10Y', 'USDJPY', 'EURUSD']}}}

print('═' * 72)
print('[5.1 复现] 汇率/收益率报价方向语义(Charter 10 §5.1 原文案)')
print('═' * 72)
# USDJPY 150→145(日元升值), 观点称"日元升值"→ Charter: 不得机械判错
# (序列自 2026-01-15 起: interval_change 基准=严格早于 publish 2026-05-01 的
#  最后观测,序列须有 publish 前历史)
dj, vj = daily_series('2026-01-15', '2026-11-10', 152.0, 145.0)
de, ve = daily_series('2026-01-15', '2026-11-10', 1.06, 1.15)
du, vu = daily_series('2026-01-15', '2026-11-10', 4.3, 3.6)   # 收益率下行
SNAP1 = mk_snap('research_snapshot_20261110', '20261110',
                {'USDJPY': (dj, vj), 'EURUSD': (de, ve), 'UST_10Y': (du, vu)})
mk_view('VIEW-20260501-101', '2026-05-01', '6m', forecasts=[
    {'target': '日元', 'value_or_direction': '日元升值',
     'horizon': '6m', 'attribution': 'institution_stated'}])
mk_view('VIEW-20260501-102', '2026-05-01', '6m', forecasts=[
    {'target': '欧元', 'value_or_direction': '欧元升值',
     'horizon': '6m', 'attribution': 'institution_stated'},
    {'target': '欧元兑美元', 'value_or_direction': '欧元升值',
     'horizon': '6m', 'attribution': 'institution_stated'}])
mk_view('VIEW-20260501-103', '2026-05-01', '6m', forecasts=[
    {'target': '美国10年期国债', 'value_or_direction': '国债价格上涨',
     'horizon': '6m', 'attribution': 'institution_stated'}])
for vid, desc in (('VIEW-20260501-101', '日元升值,USDJPY 150→145(实际日元升值)'),
                  ('VIEW-20260501-102', '欧元面: target=欧元(裸币,不映射)/'
                  '欧元兑美元(报价对,映射)+措辞"欧元升值",EURUSD 1.06→1.15'),
                  ('VIEW-20260501-103', '国债价格上涨,收益率 4.0→3.6(实际价格上升)')):
    with redirect_stdout(io.StringIO()):
        out = vv.verify_expiry(vid, SNAP1, REG, SYN_MAP, target_map=TMAP,
                               views_dir=VIEWS_DIR)
    for r in out['forecast_verdicts']:
        print(f'  {vid} #{r["index"]}: {desc}')
        print(f'    hint={r.get("direction_hint")} actual={r.get("actual_direction")}'
              f' → verdict={r["verdict"]}')

print()
print('═' * 72)
print('[5.2 复现] 到期验证数据新鲜度(Charter 10 §5.2 原文案)')
print('═' * 72)
# 到期 2025-11-01, 序列止于 2025-06-30(距到期 4 个月, 月频宏观典型陈旧)
dm = ['2025-04-30', '2025-05-31', '2025-06-30']
mk_view('VIEW-20250501-201', '2025-05-01', '6m', forecasts=[
    {'target': '联邦基金利率', 'value_or_direction': '上行',
     'horizon': '6m', 'attribution': 'institution_stated'}])
SNAP2 = mk_snap('research_snapshot_20261110b', '20261110',
                {'FED_FUNDS': (dm, [4.25, 4.25, 4.25])})
SYN_MAP2 = {'schema_version': '1.0', 'subjects': {
    'US_rates': {'note': '合成', 'metrics': ['FED_FUNDS']}}}
with redirect_stdout(io.StringIO()):
    out = vv.verify_expiry('VIEW-20250501-201', SNAP2, REG, SYN_MAP2,
                           target_map=TMAP, views_dir=VIEWS_DIR)
r = out['forecast_verdicts'][0]
print(f'  到期=2025-11-01, 序列最后观测=2025-06-30(距到期 124 天)')
print(f'    → verdict={r["verdict"]}(Charter 要求: 无足够新鲜数据须返回证据不足)')

print()
print('═' * 72)
print('[5.3 复现] 观点标签-证据绑定(Charter 10 §5.3 原文案)')
print('═' * 72)
# 底证 NOT_YET_TESTABLE 的假设标 SUPPORTED → validate_vp 应拒,实际放行
view_doc = mk_view('VIEW-20261110-301', '2026-11-10', '12m', forecasts=[
    {'target': '联邦基金利率', 'value_or_direction': '上行',
     'horizon': '12m', 'attribution': 'institution_stated'}])
vp_bad = {
    'schema_version': '1.0', 'view_id': 'VIEW-20261110-301',
    'generated_by': 'synthetic',
    'hypotheses': [{
        'label': 'SUPPORTED',          # ← 底证未到期(NOT_YET_TESTABLE)
        'ref': {'kind': 'core_view', 'index': 0},
        'metric_refs': [{'metric_id': 'FED_FUNDS', 'direction': 'up'}],
        'evidence': {'mode': 'C', 'forecast_index': 1},
    }],
    'view_label': 'SUPPORTED',
}
ok, errs = vpl.validate_vp(vp_bad, view_doc)
print(f'  底证=NOT_YET_TESTABLE(12m 未到期), 假设标 SUPPORTED')
print(f'    validate_vp → ok={ok} errors={errs}')
print(f'    (Charter: 不得允许底证 NOT_YET_TESTABLE 却标 SUPPORTED)')

print()
print('═' * 72)
print('[5.4 复现] mode A vintage 二次过滤缺失(OPEN_ISSUES R1-MINOR-4)')
print('═' * 72)
# vintage 快照 target=2026-09-01 ≤ publish 2026-09-15, 但序列夹带 obs>publish
dv, vv_ = daily_series('2026-05-01', '2026-09-01', 4.0, 4.2)
dv = dv + ['2026-09-20', '2026-10-05']        # 未来观测混入 vintage 面
vv_ = vv_ + [4.5, 4.8]
mk_snap('research_snapshot_20260901', '20260901', {'UST_10Y': (dv, vv_)})
mk_view('VIEW-20260915-401', '2026-09-15', '12m', forecasts=[])
with redirect_stdout(io.StringIO()):
    out = vv.verify_at_publish('VIEW-20260915-401', REG, SYN_MAP,
                               views_dir=VIEWS_DIR, root=TD)
ev = [e for e in out.get('evidence', []) if e['metric_id'] == 'UST_10Y'][0]
print(f'  vintage 快照序列含 obs>publish(2026-09-20/10-05), publish=2026-09-15')
print(f'    mode A 证据行 observation_date={ev["observation_date"]}'
      f' level={ev["level"]}')
print(f'    (若为 2026-10-05/4.8 → 前视泄漏: 提出时证据窗吃进未来观测)')
