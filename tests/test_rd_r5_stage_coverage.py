#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R5(autonomous-rd 2026-11-11): 阶段证据覆盖面验收套件。

背景(R5 盘点结论,audit/R5_STAGE_COVERAGE_INVENTORY.md):
  17 份 VP sidecar 的 stages.missing 分解为四类——①假设引用超出观点
  subjects 映射面(引擎永不出行) ②假设引用不在注册表(CPI_YOY 类语义层
  id 错配) ③mode A 事实面截断过杀(obs>publish 的事实被丢弃,尽管截断
  series_store 含 ≤publish 观测) ④真数据缺席(BUND_10Y/CN_OMO_7D 源端)。
本套件验收 R5 修复:
[1] metric_evidence_table extra_metric_ids(①: 并面/②: 如实 missing/去重/缺省契约)
[2] verify_at_publish 截断尾值恢复(③: 尾值近似+DEGRADED 披露/无尾值=真缺席/
    obs≤publish 不动/无前视窗界)
[3] build_vp 真实数据集成(真仓;CI 干净 clone 无快照按惯例 SKIP——
    真实面在本机全量套件执行)
[4] C 层契约零变动(view_label/label 不受 R5 影响;validate_vp 通过)
纪律: 预期值不经被测函数自算;不造数(合成 fixture 仅测机械规则)。
"""
import datetime as dt
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASS, FAIL, SKIP = 0, 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


def skip(name, why):
    global SKIP
    SKIP += 1
    print(f"  ⏭ {name} {why}")


import view_plausibility as vpl  # noqa: E402
import view_verifier as vv       # noqa: E402
import workbench_data as wd      # noqa: E402

# ═══════════════════════════════════════════════════════════════════
print("═" * 60)
print("[1] metric_evidence_table extra_metric_ids(假设引用并面)")
print("═" * 60)
SYN_REG = {'by_id': {
    'AAA': {'metric_id': 'AAA', 'display_name': '甲', 'unit': 'percent',
            'status': 'active'},
    'BBB': {'metric_id': 'BBB', 'display_name': '乙', 'unit': 'index_point',
            'status': 'active'},
    'INACT': {'metric_id': 'INACT', 'display_name': '丙', 'unit': 'percent',
              'status': 'retired'}}}
SYN_MAP = {'schema_version': '1.0', 'subjects': {
    's1': {'note': '合成', 'metrics': ['AAA']}}}
SYN_SNAP = {'snapshot_id': 'syn', 'target_date': '20261110',
            'facts': [
                {'metric_id': 'AAA', 'value': 1.0, 'unit': 'percent',
                 'observation_date': '2026-11-01', 'quality_status': 'PASS'},
                {'metric_id': 'BBB', 'value': 100.0, 'unit': 'index_point',
                 'observation_date': '2026-11-01', 'quality_status': 'PASS'}],
            'series_store': {}}

tab0 = vv.metric_evidence_table(['s1'], SYN_SNAP, SYN_REG, SYN_MAP)
check("缺省 None=原契约(仅 subjects 映射面,BBB 不出行)",
      [e['metric_id'] for e in tab0['evidence']] == ['AAA']
      and not tab0['missing'])

tab1 = vv.metric_evidence_table(['s1'], SYN_SNAP, SYN_REG, SYN_MAP,
                                extra_metric_ids=['BBB'])
ev1 = {e['metric_id']: e for e in tab1['evidence']}
check("①假设引用并面: BBB 出证据行",
      'BBB' in ev1)
check("①subject='hypothesis_ref'(与映射面来源区分)",
      ev1.get('BBB', {}).get('subject') == 'hypothesis_ref')
check("①映射面指标 subject 不变",
      ev1.get('AAA', {}).get('subject') == 's1')

tab2 = vv.metric_evidence_table(['s1'], SYN_SNAP, SYN_REG, SYN_MAP,
                                extra_metric_ids=['GHOST_ID'])
check("②不在注册表→missing+语义层缺口注记(禁猜)",
      any(m['metric_id'] == 'GHOST_ID' and '不在注册表' in str(m['reason'])
          and '语义层' in str(m['reason']) for m in tab2['missing'])
      and not any(e['metric_id'] == 'GHOST_ID' for e in tab2['evidence']))

tab3 = vv.metric_evidence_table(['s1'], SYN_SNAP, SYN_REG, SYN_MAP,
                                extra_metric_ids=['INACT'])
check("②非active→missing+非active 注记",
      any(m['metric_id'] == 'INACT' and '非active' in str(m['reason'])
          for m in tab3['missing']))

tab4 = vv.metric_evidence_table(['s1'], SYN_SNAP, SYN_REG, SYN_MAP,
                                extra_metric_ids=['AAA'])
check("去重: extra 与映射面重叠不重复出行",
      len(tab4['evidence']) == 1 and tab4['evidence'][0]['subject'] == 's1')

tab5a = vv.metric_evidence_table(['s1'], SYN_SNAP, SYN_REG, SYN_MAP,
                                 extra_metric_ids=['BBB', 'GHOST_ID', 'INACT'])
tab5b = vv.metric_evidence_table(['s1'], SYN_SNAP, SYN_REG, SYN_MAP,
                                 extra_metric_ids=['GHOST_ID', 'INACT', 'BBB'])
check("确定性: extra 顺序无关,输出逐字节一致",
      json.dumps(tab5a, sort_keys=True) == json.dumps(tab5b, sort_keys=True))

# ═══════════════════════════════════════════════════════════════════
print("═" * 60)
print("[2] verify_at_publish 截断尾值恢复(合成临时树)")
print("═" * 60)
# 注: interval_table→metric_series 走模块级真实注册表(ROOT),合成指标不在册
# →窗不可用;故 fixture 指标一律用真实注册表 active id,序列/事实为合成值。
DATES = [(dt.date(2026, 6, 1) + dt.timedelta(days=7 * i)).isoformat()
         for i in range(0, 24)]  # 2026-06-01 → 2026-11-10 周频
SPX_SYN = [round(4000.0 + 8.0 * i, 4) for i in range(len(DATES))]
VIX_SYN = [round(20.0 + 0.1 * i, 4) for i in range(len(DATES))]


def mk_snap_v(vid_, ymd):
    return {'snapshot_id': vid_, 'target_date': ymd,
            'research_as_of': f'{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}T20:00+08:00',
            'gate_a': {'status': 'PASS', 'core_missing': [],
                       'noncore_missing': [], 'noncore_missing_detail': {},
                       'noncore_degraded': []},
            'facts': [
                {'metric_id': 'SPX', 'display_name': '标普500(合成值)',
                 'value': SPX_SYN[-1], 'unit': 'index_point',
                 'observation_date': '2026-11-10', 'quality_status': 'PASS'},
                {'metric_id': 'VIX', 'display_name': 'VIX(合成值)',
                 'value': VIX_SYN[-1], 'unit': 'index_point',
                 'observation_date': '2026-11-10', 'quality_status': 'PASS'},
                {'metric_id': 'SOFR', 'display_name': 'SOFR(无序列)',
                 'value': 3.3, 'unit': 'percent',
                 'observation_date': '2026-11-10', 'quality_status': 'PASS'},
                {'metric_id': 'FED_FUNDS', 'display_name': '联邦基金(旧观测)',
                 'value': 4.25, 'unit': 'percent',
                 'observation_date': '2026-09-15', 'quality_status': 'PASS'}],
            'series_store': {
                'SPX': {'dates': DATES, 'values': SPX_SYN},
                'VIX': {'dates': DATES[-3:], 'values': VIX_SYN[-3:]}}}  # 全部>publish


TD = tempfile.mkdtemp(prefix='r5stage_')
DAILY = os.path.join(TD, 'data', 'daily')
os.makedirs(DAILY)
with open(os.path.join(DAILY, 'research_snapshot_20261110.json'), 'w',
          encoding='utf-8') as f:
    json.dump(mk_snap_v('research_snapshot_20261110', '20261110'), f,
              ensure_ascii=False)
VIEWS_D = os.path.join(TD, 'views')
os.makedirs(VIEWS_D)
VIEW_ID = 'VIEW-20261001-001'
with open(os.path.join(VIEWS_D, VIEW_ID + '.json'), 'w', encoding='utf-8') as f:
    json.dump({'schema_version': '1.1', 'view_id': VIEW_ID,
               'institution': {'name': 'Synthetic Bank',
                               'type': 'investment_bank',
                               'department': 'Research'},
               'authors': [], 'report_title': 'R5 fixture',
               'source_url': 'https://example.com/r5', 'source_type': 'official_site',
               'publish_date': '2026-10-01', 'fetch_date': '2026-11-10',
               'access_level': 'public_full', 'view_horizon': '6m',
               'subjects': ['equities'],
               'core_views': [{'statement': '市场上行。',
                               'attribution': 'institution_stated',
                               'basis': 'verbatim_quote', 'quote': 'Up.'}],
               'forecasts': [], 'key_assumptions': [], 'evidence_cited': [],
               'mechanism_steps': [], 'risk_factors': [],
               'falsification_conditions': [], 'revisions': [],
               'completeness_notes': '合成', 'copyright_note': 'meta+link'},
              f, ensure_ascii=False)

REG_REAL = wd.load_registry(ROOT)
REG_FIX = {'by_id': {
    mid: {'metric_id': mid, 'display_name': mid, 'unit': 'index_point',
          'status': 'active'}
    for mid in ('SPX', 'VIX', 'SOFR', 'FED_FUNDS')}}
# 主题映射面只挂 FED_FUNDS(obs≤publish): SPX/VIX/SOFR 均须经 extra 并面
MAP_FIX = {'schema_version': '1.0', 'subjects': {
    'equities': {'note': '合成', 'metrics': ['FED_FUNDS']}}}
out_a = vv.verify_at_publish(VIEW_ID, REG_FIX, MAP_FIX, views_dir=VIEWS_D,
                             root=TD, extra_metric_ids=['SPX', 'VIX', 'SOFR'])
check("mode A ok(approx_filtered 截断近似)", out_a.get('ok') is True)
ev = {e['metric_id']: e for e in out_a.get('evidence') or []}

tail_idx = max(i for i, d in enumerate(DATES) if d <= '2026-10-01')
check("③尾值恢复: SPX 出行且 level=截断尾值",
      'SPX' in ev and ev['SPX']['level'] == SPX_SYN[tail_idx])
check("③observation_date=尾值日期(≤publish)",
      ev.get('SPX', {}).get('observation_date') == DATES[tail_idx])
check("③披露: level_source=series_tail_le_publish",
      ev.get('SPX', {}).get('level_source') == 'series_tail_le_publish')
check("③披露: quality_status 压 DEGRADED",
      ev.get('SPX', {}).get('quality_status') == 'DEGRADED')
check("③无前视: SPX 1m 窗 end_date≤publish",
      ((ev.get('SPX', {}).get('changes') or {}).get('1m') or {})
      .get('end_date', '9999-99-99') <= '2026-10-01')

check("③序列全>publish→真缺席(VIX 进 missing)",
      'VIX' not in ev and any(m['metric_id'] == 'VIX'
                             for m in out_a.get('missing') or []))
check("③无序列指标 obs>publish→真缺席(SOFR 进 missing)",
      'SOFR' not in ev and any(m['metric_id'] == 'SOFR'
                               for m in out_a.get('missing') or []))
check("③obs≤publish 事实不动: FED_FUNDS 原样出行且无 level_source",
      'FED_FUNDS' in ev and ev['FED_FUNDS']['level'] == 4.25
      and 'level_source' not in ev['FED_FUNDS'])
check("③锚注记含尾值近似披露",
      'series_tail_le_publish' in str(out_a.get('mode_a_anchor', {}).get('note')))

# ①+③ 联动: 假设引用指标(面外)在 mode A 同样并面出行
out_a2 = vv.verify_at_publish(VIEW_ID, REG_FIX, MAP_FIX, views_dir=VIEWS_D,
                              root=TD, extra_metric_ids=['SPX'])
check("①×③联动: 面外假设引用指标 mode A 出行(subject=hypothesis_ref)",
      any(e['subject'] == 'hypothesis_ref' and e['metric_id'] == 'SPX'
          for e in out_a2.get('evidence') or []))
out_a3 = vv.verify_at_publish(VIEW_ID, REG_FIX, MAP_FIX, views_dir=VIEWS_D,
                              root=TD)
check("CLI 缺省契约: 不传 extra→仅 subjects 映射面(FED_FUNDS)出行",
      set(e['metric_id'] for e in out_a3.get('evidence') or []) == {'FED_FUNDS'})

# ═══════════════════════════════════════════════════════════════════
print("═" * 60)
print("[3] build_vp 真实数据集成(真仓)")
print("═" * 60)
snap_probe, _ = wd.latest_snapshot(ROOT)
if snap_probe is None:
    skip("[3] 全节", "干净 clone 无 data/daily 快照(真实面在本机全量套件执行)")
else:
    # ③截断尾值: VIEW-20261110-008(publish 2026-11-04,SPX fact obs 11-09>publish)
    r8 = vpl.build_vp('VIEW-20261110-008', dry_run=True)
    check("build_vp dry ok(VIEW-008)", r8.get('ok') is True, str(r8)[:200])
    vp8 = r8.get('doc') if isinstance(r8, dict) and 'doc' in r8 else None
    # dry_run 不落盘→直接复跑引擎面断言(build_vp 返回摘要;行面从引擎复取)
    out_a8 = vv.verify_at_publish(
        'VIEW-20261110-008', REG_REAL, vv.load_map(),
        extra_metric_ids=sorted({mr.get('metric_id')
                                 for h in (vpl.load_vp('VIEW-20261110-008')[0]
                                           .get('hypotheses') or [])
                                 for mr in h.get('metric_refs') or []
                                 if mr.get('metric_id')}))
    ev8 = {e['metric_id']: e for e in out_a8.get('evidence') or []}
    check("真仓③: SPX stage-A 行恢复(此前缺席)",
          'SPX' in ev8 and ev8['SPX'].get('level_source')
          == 'series_tail_le_publish')
    check("真仓③: SPX obs≤publish(尾值日期)",
          str(ev8.get('SPX', {}).get('observation_date', '')) <= '2026-11-04')

    # ①并面: VIEW-20261110-009(INDPRO/EEM 假设引用在 subjects 面外)
    base9, _ = vpl.load_vp('VIEW-20261110-009')
    extra9 = sorted({mr.get('metric_id') for h in base9.get('hypotheses') or []
                     for mr in h.get('metric_refs') or [] if mr.get('metric_id')})
    out_b9 = vv.verify('VIEW-20261110-009', snap_probe, REG_REAL, vv.load_map(),
                       mode='B', extra_metric_ids=extra9)
    evb9 = {e['metric_id'] for e in out_b9.get('evidence') or []}
    check("真仓①: INDPRO/EEM mode-B 并面出行(此前缺席)",
          {'INDPRO', 'EEM'} <= evb9)
    check("真仓④: BUND_10Y 仍如实缺席(源端,不造)",
          'BUND_10Y' not in evb9
          and any(m['metric_id'] == 'BUND_10Y'
                  for m in out_b9.get('missing') or []))
    # ②语义层缺口: VIEW-20261110-001 引用 CPI_YOY(注册表无)
    base1, _ = vpl.load_vp('VIEW-20261110-001')
    extra1 = sorted({mr.get('metric_id') for h in base1.get('hypotheses') or []
                     for mr in h.get('metric_refs') or [] if mr.get('metric_id')})
    out_b1 = vv.verify('VIEW-20261110-001', snap_probe, REG_REAL, vv.load_map(),
                       mode='B', extra_metric_ids=extra1)
    check("真仓②: CPI_YOY missing 注记=不在注册表(语义层缺口)",
          any(m['metric_id'] == 'CPI_YOY' and '不在注册表' in str(m['reason'])
              for m in out_b1.get('missing') or []))

    # ═════════════════════════════════════════════════════════════
    print("═" * 60)
    print("[4] C 层契约零变动 + 落库自洽")
    print("═" * 60)
    for vid in ('VIEW-20261110-008', 'VIEW-20261110-009', 'VIEW-20261110-001'):
        vp_path = f'data/institutions/verification/VP-{vid}.json'
        pre = open(vp_path, 'rb').read()
        r = vpl.build_vp(vid, dry_run=True)
        disk = vpl.load_vp(vid)[0]
        check(f"{vid}: build_vp dry ok+validate_vp 通过",
              r.get('ok') is True, str(r.get('error'))[:150])
        check(f"{vid}: view_label 与在档一致(C 层零变动)",
              r.get('view_label') == disk.get('view_label'))
        check(f"{vid}: stage_summary.C 与在档一致",
              r.get('stage_summary', {}).get('C')
              == disk.get('stage_summary', {}).get('C'))
        check(f"{vid}: dry-run 不落盘(在档文件逐字节不变)",
              open(vp_path, 'rb').read() == pre)

# ═══════════════════════════════════════════════════════════════════
print("═" * 60)
total = PASS + FAIL + SKIP
print(f"RESULT: {PASS} PASS / {FAIL} FAIL / {SKIP} SKIP (total {total})")
sys.exit(0 if FAIL == 0 else 1)
