#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter9 P0-1 三型验证测试(--mode A/B/C+vintage锚定+期限解析+成熟度护栏)。

锁定面(audit/C9_D_AUDIT_AND_DESIGN §P0-1 × C席复现 CONFIRMED):
① 三型区分: A=提出时证据(vintage 锚 publish)/B=当前证据更新
   (since_publish)/C=到期验证(forecast 级判定)——C席最小反例
   "三份仅 publish_date 不同的观点输出逐字节相同"不再成立
   (mode/anchor_target/maturity 随行且各型窗锚不同);
② 期限解析器: 区间取上界(6-12个月→+12m/CY2026→年末/UBS 双时点取最晚)
   +UNPARSEABLE 显式态(当前/未指明/中期/持续/下阶段/战术配置/会议间期间)
   +真实形态面(18m/2026-12/裸年/年月/ISO/两年/12月+2027年3月各+25bp);
③ 成熟度护栏: mode A/B/C 下未到期/不可解析 → relation 一律压制
   (未到期不判 supports/against);legacy 缺省行为不变(护栏对照面);
④ vintage 锚定: ≤publish 最近跨日 vintage 快照(切点披露,含当日);
   无该时点 vintage→最新快照截断(当时信息集近似,DEGRADED);
   无快照(干净clone)→ vintage_unavailable 如实;
⑤ mode C 判定序: UNPARSEABLE_HORIZON/NOT_YET_TESTABLE/NOT_MACHINE_
   VERIFIABLE/INSUFFICIENT_DATA/LEVEL_TARGET/supports/against;
⑥ revisions[]=新验证主体锚定自身date,原主张 publish 锚不变(裁定2026-11-11)。
全合成(合成快照/合成views/合成映射;真实 registry+forecast_target_map);
零真实 data/ 依赖,CI 干净 clone 可跑。
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
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


import workbench_data as wd       # noqa: E402
import view_store as vs           # noqa: E402
import view_verifier as vv        # noqa: E402

# ── 合成序列: 2024-09-01→2026-11-08 周频(覆盖 vintage 1y 窗);
#    UST_10Y 上行 4.0→4.8,SPX 下行(方向面双样本) ────────────────────────
DATES = [(dt.date(2024, 9, 1) + dt.timedelta(days=7 * i)).isoformat()
         for i in range(0, 115)]
N = len(DATES)
UST_UP = [round(4.0 + 0.8 * i / (N - 1), 6) for i in range(N)]
SPX_DOWN = [round(6000.0 - 800.0 * i / (N - 1), 6) for i in range(N)]


def _ymd_to_iso(ymd):
    return f'{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}'


def make_snap(sid, ymd, extra_stale_fact=False):
    facts = [
        {'metric_id': 'UST_10Y', 'display_name': '美债10年',
         'value': UST_UP[-1], 'unit': 'percent',
         'observation_date': _ymd_to_iso(ymd), 'quality_status': 'PASS'},
        {'metric_id': 'SPX', 'display_name': '标普500', 'value': SPX_DOWN[-1],
         'unit': 'index_point', 'observation_date': _ymd_to_iso(ymd),
         'quality_status': 'PASS'},
    ]
    if extra_stale_fact:
        facts.append({'metric_id': 'FED_FUNDS', 'display_name': '联邦基金',
                      'value': 4.25, 'unit': 'percent',
                      'observation_date': '2026-07-15',
                      'quality_status': 'PASS'})
    return {'snapshot_id': sid, 'target_date': ymd,
            'research_as_of': f'{_ymd_to_iso(ymd)}T20:00:00+08:00',
            'gate_a': {'status': 'PASS', 'core_missing': [],
                       'noncore_missing': [], 'noncore_missing_detail': {},
                       'noncore_degraded': []},
            'facts': facts,
            'series_store': {'UST_10Y': {'dates': DATES, 'values': UST_UP},
                             'SPX': {'dates': DATES, 'values': SPX_DOWN}}}


TD = tempfile.mkdtemp(prefix='c9modes_')
DAILY = os.path.join(TD, 'data', 'daily')
os.makedirs(DAILY)
# 跨日 vintage 20260901: 序列截断至 ≤2026-09-01(提出时信息集)
SEP_KEEP = [i for i, d in enumerate(DATES) if d <= '2026-09-01']
SNAP_SEP = make_snap('research_snapshot_20260901', '20260901')
SNAP_SEP['series_store'] = {
    'UST_10Y': {'dates': [DATES[i] for i in SEP_KEEP],
                'values': [UST_UP[i] for i in SEP_KEEP]},
    'SPX': {'dates': [DATES[i] for i in SEP_KEEP],
            'values': [SPX_DOWN[i] for i in SEP_KEEP]}}
SNAP_SEP['facts'] = [dict(f, value=UST_UP[SEP_KEEP[-1]])
                     for f in SNAP_SEP['facts']]
SNAP_LATEST = make_snap('research_snapshot_20261110', '20261110',
                        extra_stale_fact=True)
for s in (SNAP_SEP, SNAP_LATEST):
    with open(os.path.join(DAILY, s['snapshot_id'] + '.json'), 'w',
              encoding='utf-8') as f:
        json.dump(s, f, ensure_ascii=False)

SYN_MAP = {'schema_version': '1.0', 'subjects': {
    'US_rates': {'note': '合成', 'metrics': ['UST_10Y', 'SPX', 'FED_FUNDS']}}}
REG = wd.load_registry(ROOT)


def mk_view(vid, publish, horizon, forecasts=None, revisions=None):
    return {
        'schema_version': '1.1', 'view_id': vid,
        'institution': {'name': 'Synthetic Bank', 'type': 'investment_bank',
                        'department': 'Research'},
        'authors': [], 'report_title': 'Syn ' + vid,
        'source_url': 'https://example.com/' + vid,
        'source_type': 'official_site', 'publish_date': publish,
        'fetch_date': '2026-11-10', 'access_level': 'public_full',
        'view_horizon': horizon, 'subjects': ['US_rates'],
        'core_views': [{'statement': '利率上行。',
                        'attribution': 'institution_stated',
                        'basis': 'verbatim_quote', 'quote': 'Rates up.'}],
        'forecasts': forecasts or [], 'key_assumptions': [], 'evidence_cited': [],
        'mechanism_steps': [], 'risk_factors': [], 'falsification_conditions': [],
        'revisions': revisions or [], 'completeness_notes': '合成',
        'copyright_note': 'meta+link',
    }


VIEWS = {
    'VIEW-20260915-001': mk_view('VIEW-20260915-001', '2026-09-15', '12m'),
    'VIEW-20260501-002': mk_view(
        'VIEW-20260501-002', '2025-05-01', '6m',
        forecasts=[{'target': '美债10年', 'value_or_direction': '上行',
                    'horizon': '6m', 'attribution': 'institution_stated'}]),
    'VIEW-20260501-003': mk_view(
        'VIEW-20260501-003', '2025-05-01', '6m',
        forecasts=[{'target': '美债10年', 'value_or_direction': '下行',
                    'horizon': '6m', 'attribution': 'institution_stated'}]),
    'VIEW-20260501-011': mk_view(
        'VIEW-20260501-011', '2025-05-01', '6m',
        forecasts=[
            {'target': '恒生国企指数', 'value_or_direction': '上行',
             'horizon': '6m', 'attribution': 'institution_stated'},
            {'target': '美债10年', 'value_or_direction': '到 4.5% 附近',
             'horizon': '6m', 'attribution': 'institution_stated'},
            {'target': '实际利率', 'value_or_direction': '上行',
             'horizon': '6m', 'attribution': 'institution_stated'}]),
    'VIEW-20261101-004': mk_view('VIEW-20261101-004', '2026-11-01', '3m'),
    'VIEW-20261001-005': mk_view(
        'VIEW-20261001-005', '2026-10-01', 'other',
        forecasts=[{'target': '美债10年', 'value_or_direction': '上行',
                    'horizon': '中期', 'attribution': 'institution_stated'},
                   {'target': '美债10年', 'value_or_direction': '上行',
                    'horizon': '6m', 'attribution': 'institution_stated'}]),
    'VIEW-20261109-006': mk_view(
        'VIEW-20261109-006', '2026-11-09', '6m',
        forecasts=[{'target': '美债10年', 'value_or_direction': '上行',
                    'horizon': '12月+2027年3月各+25bp',
                    'attribution': 'institution_stated'}]),
    'VIEW-20261110-007': mk_view('VIEW-20261110-007', '2026-11-10', 'other'),
    'VIEW-20261110-008': mk_view(
        'VIEW-20261110-008', '2026-10-16', '3m',
        revisions=[{'date': '2026-11-10', 'change': '立场更新(合成)',
                    'source_url': 'https://example.com/rev'}]),
    'VIEW-20260801-009': mk_view('VIEW-20260801-009', '2026-08-01', '6m'),
}
VDIR = os.path.join(TD, 'views')
os.makedirs(VDIR)
for v in VIEWS.values():
    with open(os.path.join(VDIR, v['view_id'] + '.json'), 'w',
              encoding='utf-8') as f:
        json.dump(v, f, ensure_ascii=False)

print("═" * 60)
print("[1] 期限解析器: 真实形态普查(裁定②上界+UNPARSEABLE)")
print("═" * 60)
CASES = [
    ('CY2026', None, '2026-12-31'), ('2026年全年', None, '2026-12-31'),
    ('2026', None, '2026-12-31'), ('2027', None, '2027-12-31'),
    ('2026-2027', None, '2027-12-31'),
    ('2026-12', None, '2026-12-31'), ('2027-03', None, '2027-03-31'),
    ('2027年3月', None, '2027-03-31'), ('2026-12-15', None, '2026-12-15'),
    ('6-12个月', '2026-11-01', '2027-11-01'),
    ('12个月', '2026-11-01', '2027-11-01'),
    ('18m', '2026-10-13', '2028-04-13'),
    ('两年', '2026-01-15', '2028-01-15'),
    ('12月+2027年3月各+25bp', '2026-11-09', '2027-03-31'),
]
for text, pub, want in CASES:
    r = vv.parse_view_horizon(text, pub)
    check(f"{text!r}→{want}(上界/最晚)", r['state'] == 'parsed'
          and r['horizon_end'] == want, str(r))
for text in ('当前(会后即刻)', '未指明', '中期', '持续', '下阶段', '战术配置',
             '会议间期间', 'other', ''):
    r = vv.parse_view_horizon(text, None)
    check(f"{text!r}→UNPARSEABLE 显式态", r['state'] == 'unparseable'
          and r['horizon_end'] is None, str(r))
r = vv.parse_view_horizon('12个月', None)
check("时长型缺 publish 锚→unparseable(不猜)", r['state'] == 'unparseable')
check("_add_months 月末钳制(2026-03-31+6m→2026-09-30)",
      vv._add_months('2026-03-31', 6) == '2026-09-30')
check("_add_months 跨年(2026-11-09+18m→2028-05-09)",
      vv._add_months('2026-11-09', 18) == '2028-05-09',
      vv._add_months('2026-11-09', 18))
m = vv.maturity('6m', '2025-05-01', '20261110')
check("maturity 到期(2025-05-01+6m≤20261110)=MATURED",
      m['state'] == 'MATURED' and m['horizon_end'] == '2025-11-01')
m = vv.maturity('3m', '2026-11-01', '20261110')
check("maturity 未到期=NOT_YET_TESTABLE", m['state'] == 'NOT_YET_TESTABLE')
m = vv.maturity('未指明', '2026-10-01', '20261110')
check("maturity 不可解析=UNPARSEABLE", m['state'] == 'UNPARSEABLE')

print("═" * 60)
print("[2] mode A 提出时证据: vintage 锚定(三档 publish 输出可辨)")
print("═" * 60)
real_vdir = vs.VIEWS_DIR
vs.VIEWS_DIR = VDIR
out0915 = vv.verify_at_publish('VIEW-20260915-001', REG, SYN_MAP,
                                directions={'UST_10Y': 'up'}, root=TD)
check("publish 2026-09-15 → vintage_snapshot 锚(切点 20260901)",
      out0915['ok'] and out0915['mode_a_anchor']['anchor'] == 'vintage_snapshot'
      and out0915['mode_a_anchor']['cutoff'] == '20260901'
      and out0915['mode_a_anchor']['degraded'] is False,
      str(out0915.get('mode_a_anchor')))
check("mode A 窗末=观点时点(anchor_target=20260901,非今天)",
      out0915['anchor_target'] == '20260901' and out0915['mode'] == 'A')
ev = {e['metric_id']: e for e in out0915['evidence']}
node = ev['UST_10Y']['changes']['1y']
_exp = UST_UP[SEP_KEEP[-1]] - UST_UP[[i for i in SEP_KEEP
                                      if DATES[i] < '2025-09-01'][-1]]
check("mode A 1y 窗以 2026-09-01 为窗末(vintage 序列截断,期望pp=%.4f)" % _exp,
      node.get('available') is not False
      and abs(node.get('pp_change', 99) - _exp) < 1e-4, str(node))
out0801 = vv.verify_at_publish('VIEW-20260801-009', REG, SYN_MAP, root=TD)
check("publish 2026-08-01 无该时点 vintage → approx_filtered+DEGRADED(裁定⑦)",
      out0801['mode_a_anchor']['anchor'] == 'approx_filtered'
      and out0801['mode_a_anchor']['degraded'] is True
      and out0801['mode_a_anchor']['cutoff'] == '2026-08-01',
      str(out0801.get('mode_a_anchor')))
ev801 = out0801['evidence']
check("approx 截断: 陈旧观测(2026-07-15)在场,晚于 publish 的事实被滤",
      any(e.get('observation_date') == '2026-07-15' for e in ev801)
      and all(str(e.get('observation_date', '')) <= '2026-08-01' for e in ev801),
      str([(e['metric_id'], e.get('observation_date')) for e in ev801]))
check("mode A 未到期(12m)→护栏压制 relation(不判 supports/against)",
      out0915['maturity']['state'] == 'NOT_YET_TESTABLE'
      and all(e['relation'] is None for e in out0915['evidence'])
      and any('成熟度护栏' in (e['relation_note'] or '') for e in out0915['evidence'])
      and '提出时' in out0915['relation_semantics'])
empty_root = tempfile.mkdtemp(prefix='c9modes_empty_')
out_none = vv.verify_at_publish('VIEW-20260915-001', REG, SYN_MAP,
                                root=empty_root)
check("无快照(干净clone)→ vintage_unavailable 如实",
      out_none.get('ok') is False
      and out_none['error']['kind'] == 'vintage_unavailable',
      str(out_none.get('error')))

print("═" * 60)
print("[3] mode B 当前证据更新 + 护栏 vs legacy 对照")
print("═" * 60)
outB = vv.verify('VIEW-20261101-004', SNAP_LATEST, REG, SYN_MAP,
                 directions={'UST_10Y': 'up'}, mode='B')
check("mode B ok+since_publish 逐指标在场",
      outB['ok'] and all('since_publish' in e for e in outB['evidence']))
sp = {e['metric_id']: e for e in outB['evidence']}['UST_10Y']['since_publish']
check("since_publish=严格>publish 的区间变动(basis<publish 2026-11-01)",
      sp.get('available') is not False and sp.get('pp_change') is not None
      and sp.get('basis_date', '9999') < '2026-11-01', str(sp))
check("mode B 未到期(3m)→护栏压制 relation(legacy 可判处不判)",
      outB['n_supports'] == 0 and outB['n_against'] == 0
      and all(e['relation'] is None for e in outB['evidence'])
      and any('成熟度护栏' in (e['relation_note'] or '') for e in outB['evidence'])
      and '当前更新窗' in outB['relation_semantics'])
outL = vv.verify('VIEW-20261101-004', SNAP_LATEST, REG, SYN_MAP,
                 directions={'UST_10Y': 'up'})
check("legacy 缺省行为不变(同输入 relation=supports,已发布契约)",
      outL['mode'] == 'legacy' and outL['n_supports'] == 1
      and {e['metric_id']: e['relation'] for e in outL['evidence']}['UST_10Y']
      == 'supports')
check("legacy 输出新增披露字段(maturity/revision_anchors)且证据面不变",
      'maturity' in outL and 'revision_anchors' in outL
      and outL['n_evidence'] == 3)

print("═" * 60)
print("[4] mode C 到期验证: 判定序(显式态不猜)")
print("═" * 60)
tmap = vv.load_forecast_target_map()
c2 = vv.verify_expiry('VIEW-20260501-002', SNAP_LATEST, REG, SYN_MAP,
                      target_map=tmap)
v = c2['forecast_verdicts'][0]
check("到期+方向上行+实际上行 → supports",
      v['verdict'] == 'supports' and v['direction_hint'] == 'up'
      and v['actual_direction'] == 'up'
      and v['interval_change'].get('pp_change', 0) > 0, str(v))
check("mode C publish→horizon_end 窗(2025-05-01→2025-11-01)",
      v['horizon_end'] == '2025-11-01'
      and v['interval_change'].get('basis_date', '9999') < '2025-05-01', str(v))
c3 = vv.verify_expiry('VIEW-20260501-003', SNAP_LATEST, REG, SYN_MAP,
                      target_map=tmap)
check("到期+方向下行+实际上行 → against", c3['forecast_verdicts'][0]['verdict']
      == 'against')
c11 = vv.verify_expiry('VIEW-20260501-011', SNAP_LATEST, REG, SYN_MAP,
                       target_map={'targets': dict(tmap['targets'],
                                                   **{'实际利率': 'REAL_10Y'})})
v11 = {r['index']: r for r in c11['forecast_verdicts']}
check("未映射 target(恒生国企指数)→NOT_MACHINE_VERIFIABLE(禁猜)",
      v11[1]['verdict'] == 'NOT_MACHINE_VERIFIABLE')
check("点位型(到 4.5% 附近)→LEVEL_TARGET 只报告不判",
      v11[2]['verdict'] == 'LEVEL_TARGET'
      and v11[2]['actual_observation']['date'] <= '2025-11-01'
      and v11[2]['actual_observation']['date'] > '2025-05-01',
      str(v11[2].get('actual_observation')))
check("映射在册但无序列(实际利率,单点观测源)→INSUFFICIENT_DATA",
      v11[3]['verdict'] == 'INSUFFICIENT_DATA', str(v11[3]))
c5 = vv.verify_expiry('VIEW-20261001-005', SNAP_LATEST, REG, SYN_MAP,
                      target_map=tmap)
vs5 = {r['index']: r['verdict'] for r in c5['forecast_verdicts']}
check("forecast 期限'中期'→UNPARSEABLE_HORIZON", vs5[1] == 'UNPARSEABLE_HORIZON')
check("forecast 期限 6m 未到期→NOT_YET_TESTABLE(2026-10-01+6m>2026-11-10)",
      vs5[2] == 'NOT_YET_TESTABLE')
c6 = vv.verify_expiry('VIEW-20261109-006', SNAP_LATEST, REG, SYN_MAP,
                      target_map=tmap)
r6 = c6['forecast_verdicts'][0]
check("UBS 双时点期限(12月+2027年3月)→上界 2027-03-31 未到期",
      r6['horizon_end'] == '2027-03-31' and r6['verdict'] == 'NOT_YET_TESTABLE',
      str(r6))
c7 = vv.verify_expiry('VIEW-20261110-007', SNAP_LATEST, REG, SYN_MAP,
                      target_map=tmap)
check("forecasts 空(BIS 回顾型真实反例)→注记而非伪造判定",
      c7['ok'] and c7['n_forecasts'] == 0
      and '回顾性刊物' in (c7.get('no_forecasts_note') or ''),
      str(c7.get('no_forecasts_note')))

print("═" * 60)
print("[5] revisions 修订锚(裁定: 修订=新验证主体,原锚不变)")
print("═" * 60)
out8 = vv.verify('VIEW-20261110-008', SNAP_LATEST, REG, SYN_MAP, mode='B')
check("revision_anchors 登记 2026-11-10 为主体",
      out8['revision_anchors'][0]['date'] == '2026-11-10'
      and out8['revision_anchors'][0]['anchor'] == 'independent_subject')
check("原主张 publish 锚不变(2026-10-16,历史不覆盖)",
      out8['publish_date'] == '2026-10-16')

print("═" * 60)
print("[6] CLI: --mode 面")
print("═" * 60)
with redirect_stdout(io.StringIO()) as buf:
    rc = vv.main(['VIEW-20260915-001', '--mode', 'X'], data_root=TD)
check("--mode 非法 → rc=2 bad_mode", rc == 2 and 'bad_mode' in buf.getvalue())
with redirect_stdout(io.StringIO()) as buf:
    rc = vv.main(['VIEW-20261109-006', '--mode', 'C'], data_root=TD)
outc = json.loads(buf.getvalue())
check("--mode C 单 JSON 可解析+mode 字段", rc == 0 and outc['mode'] == 'C'
      and outc['ok'])
with redirect_stdout(io.StringIO()) as buf:
    rc = vv.main(['VIEW-20260915-001', '--mode', 'A'], data_root=TD)
outa = json.loads(buf.getvalue())
check("--mode A 单 JSON+mode_a_anchor 在场", rc == 0 and outa['mode'] == 'A'
      and outa['mode_a_anchor']['cutoff'] == '20260901')
with redirect_stdout(io.StringIO()) as buf:
    rc = vv.main(['VIEW-20261101-004', '--mode', 'all'], data_root=TD)
outall = json.loads(buf.getvalue())
check("--mode all → A/B/C 三块", rc == 0 and outall['mode'] == 'all'
      and all(k in outall for k in ('A', 'B', 'C'))
      and outall['A']['mode'] == 'A' and outall['B']['mode'] == 'B'
      and outall['C']['mode'] == 'C')
vs.VIEWS_DIR = real_vdir

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
