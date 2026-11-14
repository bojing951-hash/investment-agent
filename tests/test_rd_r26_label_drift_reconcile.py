#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R26 VP 旧库 LABEL_DRIFT 对账(reconcile_label_drift)回归锁。

背景(RESUME R26 候选①): VP v1.0 存量 mode C verdict 含旧期词汇 no_forecast
("无机器可验预测绑定"),现行引擎已按期限可解析性分化为 UNPARSEABLE_HORIZON/
NOT_YET_TESTABLE;build_vp C 层零变动使 --build-all 不刷新存量 verdict
(R22"重建即消"预期对词汇漂移行不成立)——须经显式对账: 逐行重贴+history
留痕,可见非静默。

  §1 漂移复现: 合成 views/VP(旧词汇存量)→ binding_check 出 LABEL_DRIFT。
  §2 核心对账: 重贴 verdict(+标签随行)+verdict_history/label_history 留痕
     +reconciliations 台账+非漂移行零扰动+幂等(二跑零写)。
  §3 v1.1 面: 全 NOT_YET 档 view_label 随 rollup 变更+stage_summary.C 同步。
  §4 拒写边界: 重算=判定标签默认拒(--allow-judgment 放行);BINDING_VIOLATION
     整档拒写;CLI 退出码。
  §5 dry-run: 零写+无 .tmp 残留。
  §6 契约: no_forecast→INSUFFICIENT(存量档自洽性前提)。
全合成(合成快照/views/VP);真实 registry+config;CI 干净 clone 可跑。
"""
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile

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
import view_verifier as vv             # noqa: E402
import view_plausibility as vpl        # noqa: E402

REG = wd.load_registry(ROOT)
TD = tempfile.mkdtemp(prefix='r26t_')
VIEWS_DIR = os.path.join(TD, 'views')
VP_DIR = os.path.join(TD, 'vp')
DAILY = os.path.join(TD, 'data', 'daily')
for d in (VIEWS_DIR, VP_DIR, DAILY):
    os.makedirs(d)

SYN_MAP = {'schema_version': '1.0', 'subjects': {
    'US_rates': {'note': '合成', 'metrics': [
        'UST_10Y', 'USDJPY', 'EURUSD', 'DXY', 'FED_FUNDS', 'SPX']}}}
with open(os.path.join(TD, 'vmap.json'), 'w', encoding='utf-8') as f:
    json.dump(SYN_MAP, f, ensure_ascii=False)


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


def mk_snap(sid, ymd, series_map):
    facts = []
    for mid, (dates, values) in series_map.items():
        m = next(x for x in REG['metrics'] if x['metric_id'] == mid)
        facts.append({'metric_id': mid, 'display_name': m['display_name'],
                      'value': values[-1], 'unit': m.get('unit', ''),
                      'observation_date': dates[-1], 'quality_status': 'PASS'})
    snap = {'snapshot_id': sid, 'target_date': ymd,
            'research_as_of': f'{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}T20:00:00+08:00',
            'gate_a': {'status': 'PASS', 'core_missing': [],
                       'noncore_missing': [], 'noncore_missing_detail': {},
                       'noncore_degraded': []},
            'facts': facts,
            'series_store': {mid: {'dates': d, 'values': v}
                             for mid, (d, v) in series_map.items()}}
    with open(os.path.join(DAILY, sid + '.json'), 'w', encoding='utf-8') as f:
        json.dump(snap, f, ensure_ascii=False)
    return snap


def read_vp(vid):
    with open(os.path.join(VP_DIR, f'VP-{vid}.json'), encoding='utf-8') as f:
        return json.load(f)


def write_vp(vid, doc):
    with open(os.path.join(VP_DIR, f'VP-{vid}.json'), 'w',
              encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    return doc


def hyp(label, fi, verdict, linked=None, mode='C'):
    return {'label': label,
            'ref': {'kind': 'core_view', 'index': 0},
            'metric_refs': [{'metric_id': 'FED_FUNDS', 'direction': 'up'}],
            'evidence': {'mode': mode, 'forecast_index': fi,
                         'verdict': verdict,
                         **({'linked_forecasts': linked} if linked else {})}}


# ════════════════════════════════════════════════════════════════════
section('1 · 漂移复现(旧词汇 no_forecast 存量 vs 现行引擎分化)')
# ════════════════════════════════════════════════════════════════════
dx, vx = daily_series('2026-01-15', '2026-11-10', 100.0, 106.0)   # DXY ↑
mk_snap('research_snapshot_20261112', '20261112', {'DXY': (dx, vx)})

# 401: fc0 期限不可解析('当前'词汇)→UNPARSEABLE_HORIZON;fc1 12m 未到期→
# NOT_YET_TESTABLE(镜像生产 VIEW-20261110-002/007 两类漂移)
mk_view('VIEW-20261110-401', '2026-11-10', '12m', forecasts=[
    {'target': '联邦基金利率', 'value_or_direction': '维持3.75%-4.00%',
     'horizon': '当前(会后即刻)', 'attribution': 'institution_stated'},
    {'target': '联邦基金利率', 'value_or_direction': '回归2%目标',
     'horizon': '12m', 'attribution': 'institution_stated'}])
vp401 = write_vp('VIEW-20261110-401', {
    'schema_version': '1.0', 'view_id': 'VIEW-20261110-401',
    'generated_by': 'synthetic-v1.0-era',
    'view_label': 'INSUFFICIENT_EVIDENCE',
    'hypotheses': [
        hyp('INSUFFICIENT_EVIDENCE', 0, 'no_forecast', linked=[0]),
        hyp('INSUFFICIENT_EVIDENCE', 0, 'no_forecast', linked=[1]),
        hyp('INSUFFICIENT_EVIDENCE', None, 'NOT_MACHINE_VERIFIABLE'),
    ]})
b = vpl.binding_check(view_id='VIEW-20261110-401', vp_dir=VP_DIR,
                      views_dir=VIEWS_DIR, root=TD)
check('漂移复现: hyp0/hyp1=LABEL_DRIFT,hyp2(BINDING_OK 行)不误报',
      [r['status'] for r in b['rows']] ==
      ['LABEL_DRIFT', 'LABEL_DRIFT', 'BINDING_OK']
      and b['ok'] is True and b['summary']['LABEL_DRIFT'] == 2,
      json.dumps(b['summary'], ensure_ascii=False))
check('漂移行当前 verdict 分化如实: hyp0→UNPARSEABLE_HORIZON(词汇现代化,'
      '标签不变)/hyp1→NOT_YET_TESTABLE(未到期边界,标签须随行)',
      b['rows'][0]['current_verdict'] == 'UNPARSEABLE_HORIZON'
      and b['rows'][0]['recomputed_label'] == 'INSUFFICIENT_EVIDENCE'
      and b['rows'][1]['current_verdict'] == 'NOT_YET_TESTABLE'
      and b['rows'][1]['recomputed_label'] == 'NOT_YET_TESTABLE',
      json.dumps(b['rows'][1], ensure_ascii=False)[:160])

# ════════════════════════════════════════════════════════════════════
section('2 · 核心对账(重贴+留痕+零扰动+幂等)')
# ════════════════════════════════════════════════════════════════════
hyp2_before = json.dumps(vp401['hypotheses'][2], ensure_ascii=False,
                         sort_keys=True)
out = vpl.reconcile_label_drift('VIEW-20261110-401', vp_dir=VP_DIR,
                                views_dir=VIEWS_DIR, root=TD)
check('对账成功: 2 行重贴+写盘+写后漂移清零',
      out.get('ok') is True and out.get('n_reconciled') == 2
      and out.get('written') is True
      and out.get('binding_summary_post', {}).get('LABEL_DRIFT') == 0,
      json.dumps(out, ensure_ascii=False)[:200])
d = read_vp('VIEW-20261110-401')
h0, h1, h2 = d['hypotheses']
check('hyp0 重贴: verdict no_forecast→UNPARSEABLE_HORIZON,标签不变'
      '(INSUFFICIENT),无 label_history(未变不造史)',
      h0['evidence']['verdict'] == 'UNPARSEABLE_HORIZON'
      and h0['label'] == 'INSUFFICIENT_EVIDENCE'
      and 'label_history' not in h0)
vh = h0['evidence']['verdict_history']
check('hyp0 verdict_history 留痕: from/to/basis/snapshot_id/by 齐全'
      '(可见非静默)',
      len(vh) == 1 and vh[0]['from'] == 'no_forecast'
      and vh[0]['to'] == 'UNPARSEABLE_HORIZON'
      and 'basis' in vh[0] and 'snapshot_id' in vh[0]
      and 'reconcile_label_drift' in vh[0]['by'] and 'HKT' in vh[0]['date'],
      json.dumps(vh, ensure_ascii=False)[:200])
check('hyp1 重贴+标签随行: verdict→NOT_YET_TESTABLE 且标签 INSUFFICIENT→'
      'NOT_YET_TESTABLE+label_history 留痕',
      h1['evidence']['verdict'] == 'NOT_YET_TESTABLE'
      and h1['label'] == 'NOT_YET_TESTABLE'
      and h1['label_history'][0]['from'] == 'INSUFFICIENT_EVIDENCE'
      and h1['label_history'][0]['to'] == 'NOT_YET_TESTABLE'
      and 'verdict 重贴随行' in h1['label_history'][0]['reason'])
check('混合档 view_label 不变([INSUFF,NOT_YET,…]→INSUFFICIENT)+'
      'view_label_changed=False 如实',
      d['view_label'] == 'INSUFFICIENT_EVIDENCE'
      and out.get('view_label_changed') is False)
check('非漂移行(hyp2)零扰动(逐字节一致)',
      json.dumps(h2, ensure_ascii=False, sort_keys=True) == hyp2_before
      and 'verdict_history' not in h2['evidence'])
rec = d['reconciliations'][-1]
check('reconciliations 台账: n_rows/rows 逐行 from→to/principle 可见非静默',
      rec['n_rows'] == 2 and len(rec['rows']) == 2
      and rec['rows'][0]['verdict_from'] == 'no_forecast'
      and rec['rows'][1]['label_to'] == 'NOT_YET_TESTABLE'
      and '可见非静默' in rec['principle'] and rec['round'] == 'R26')
import view_store as vs                       # noqa: E402
vd401, _ = vs.get_view('VIEW-20261110-401', VIEWS_DIR)
okv, errsv = vpl.validate_vp(d, vd401)
check('重贴后 validate_vp 全过(标签-verdict 绑定+聚合一致)',
      okv, str(errsv))
b2 = vpl.binding_check(view_id='VIEW-20261110-401', vp_dir=VP_DIR,
                       views_dir=VIEWS_DIR, root=TD)
check('写后活体复证: 3 行全 BINDING_OK(ok=True)',
      b2['summary'] == {'BINDING_OK': 3, 'BINDING_VIOLATION': 0,
                        'LABEL_DRIFT': 0, 'NO_MACHINE_BINDING': 0,
                        'ENGINE_UNAVAILABLE': 0, 'VP_MISSING': 0}
      and b2['ok'] is True, json.dumps(b2['summary'], ensure_ascii=False))
before_bytes = open(os.path.join(VP_DIR, 'VP-VIEW-20261110-401.json'),
                    'rb').read()
out2 = vpl.reconcile_label_drift('VIEW-20261110-401', vp_dir=VP_DIR,
                                 views_dir=VIEWS_DIR, root=TD)
after_bytes = open(os.path.join(VP_DIR, 'VP-VIEW-20261110-401.json'),
                   'rb').read()
check('幂等: 二跑零漂移=零写(文件字节不变,n_reconciled=0)',
      out2.get('ok') is True and out2.get('n_reconciled') == 0
      and out2.get('written') is False and before_bytes == after_bytes)

# ════════════════════════════════════════════════════════════════════
section('3 · v1.1 面: view_label 变更随行+stage_summary.C 同步')
# ════════════════════════════════════════════════════════════════════
# 403: 双 12m 未到期假设均漂移→NOT_YET→全 NOT_YET 档 rollup=NOT_YET_TESTABLE
mk_view('VIEW-20261110-403', '2026-11-10', '12m', forecasts=[
    {'target': '联邦基金利率', 'value_or_direction': '回归2%目标',
     'horizon': '12m', 'attribution': 'institution_stated'},
    {'target': '联邦基金利率', 'value_or_direction': '降至3.0%',
     'horizon': '12m', 'attribution': 'institution_stated'}])


def v11_hyp(label, fi, verdict, linked):
    h = hyp(label, fi, verdict, linked)
    h['stages'] = {'A': {'anchor': 'syn', 'rows': [], 'n_rows': 0,
                         'n_judged': 0}, 'B': {'snapshot_id': 'syn',
                                               'rows': [], 'n_rows': 0,
                                               'n_judged': 0}}
    h['stage_labels'] = {'A': 'INSUFFICIENT_EVIDENCE',
                         'B': 'INSUFFICIENT_EVIDENCE',
                         'semantics': '假设证据评价(非预测验证)'}
    return h


write_vp('VIEW-20261110-403', {
    'schema_version': '1.1', 'view_id': 'VIEW-20261110-403',
    'generated_by': 'synthetic-v1.1-era', 'view_label': 'INSUFFICIENT_EVIDENCE',
    'hypotheses': [
        v11_hyp('INSUFFICIENT_EVIDENCE', 0, 'no_forecast', [0]),
        v11_hyp('INSUFFICIENT_EVIDENCE', 1, 'no_forecast', [1])],
    'stage_summary': {'A': 'INSUFFICIENT_EVIDENCE',
                      'B': 'INSUFFICIENT_EVIDENCE',
                      'C': 'INSUFFICIENT_EVIDENCE', 'semantics': 'syn'}})
out3 = vpl.reconcile_label_drift('VIEW-20261110-403', vp_dir=VP_DIR,
                                 views_dir=VIEWS_DIR, root=TD)
d3 = read_vp('VIEW-20261110-403')
check('全 NOT_YET 档: view_label INSUFFICIENT→NOT_YET_TESTABLE+'
      'view_label_changed=True',
      out3.get('ok') and out3.get('view_label_changed') is True
      and d3['view_label'] == 'NOT_YET_TESTABLE'
      and out3.get('view_label') == 'NOT_YET_TESTABLE')
check('stage_summary.C 与 view_label 同步(v1.1 契约 C=view_label)',
      d3['stage_summary']['C'] == 'NOT_YET_TESTABLE')
vd403, _ = vs.get_view('VIEW-20261110-403', VIEWS_DIR)
okv3, errsv3 = vpl.validate_vp(d3, vd403)
check('v1.1 重贴后 validate_vp 全过(stages/stage_summary 一致)',
      okv3, str(errsv3))

# ════════════════════════════════════════════════════════════════════
section('4 · 拒写边界(判定标签默认拒/红线整档拒/CLI 退出码)')
# ════════════════════════════════════════════════════════════════════
# 402: 已到期+数据支持 → 当前引擎 supports;存量 no_forecast+INSUFFICIENT
# → 重算标签=SUPPORTED=判定内容变更 → 默认拒写
mk_view('VIEW-20260501-402', '2026-05-01', '6m', forecasts=[
    {'target': '美元指数', 'value_or_direction': '美元走强',
     'horizon': '6m', 'attribution': 'institution_stated'}])
write_vp('VIEW-20260501-402', {
    'schema_version': '1.0', 'view_id': 'VIEW-20260501-402',
    'generated_by': 'synthetic-v1.0-era', 'view_label': 'INSUFFICIENT_EVIDENCE',
    'hypotheses': [hyp('INSUFFICIENT_EVIDENCE', 0, 'no_forecast',
                       linked=[0])]})
p402 = os.path.join(VP_DIR, 'VP-VIEW-20260501-402.json')
raw402 = open(p402, 'rb').read()
outj = vpl.reconcile_label_drift('VIEW-20260501-402', vp_dir=VP_DIR,
                                 views_dir=VIEWS_DIR, root=TD)
check('重算=supports(判定标签)→ 默认整档拒写(judgment_relabel_refused),'
      '文件字节不变',
      outj.get('ok') is False
      and outj['error']['kind'] == 'judgment_relabel_refused'
      and open(p402, 'rb').read() == raw402
      and outj['error']['rows'][0]['recomputed_label'] == 'SUPPORTED',
      json.dumps(outj.get('error'), ensure_ascii=False)[:200])
outj2 = vpl.reconcile_label_drift('VIEW-20260501-402', vp_dir=VP_DIR,
                                  views_dir=VIEWS_DIR, root=TD,
                                  allow_judgment=True)
d402 = read_vp('VIEW-20260501-402')
check('--allow-judgment 显式放行: verdict→supports+标签→SUPPORTED+双史留痕'
      '+view_label→SUPPORTED',
      outj2.get('ok') is True and outj2['n_reconciled'] == 1
      and d402['hypotheses'][0]['evidence']['verdict'] == 'supports'
      and d402['hypotheses'][0]['label'] == 'SUPPORTED'
      and d402['view_label'] == 'SUPPORTED'
      and d402['hypotheses'][0]['label_history'][0]['from'] ==
      'INSUFFICIENT_EVIDENCE')
vd402, _ = vs.get_view('VIEW-20260501-402', VIEWS_DIR)
okv2, errsv2 = vpl.validate_vp(d402, vd402)
check('判定重贴后 validate_vp 全过(判定标签由底证 verdict 产生)',
      okv2, str(errsv2))
# 405: 伪造 supports 的未到期预测(BINDING_VIOLATION 红线)→ 整档拒写
mk_view('VIEW-20261110-405', '2026-11-10', '12m', forecasts=[
    {'target': '联邦基金利率', 'value_or_direction': '回归2%目标',
     'horizon': '12m', 'attribution': 'institution_stated'}])
write_vp('VIEW-20261110-405', {
    'schema_version': '1.0', 'view_id': 'VIEW-20261110-405',
    'generated_by': 'synthetic-v1.0-era', 'view_label': 'SUPPORTED',
    'hypotheses': [hyp('SUPPORTED', 0, 'supports', linked=[0])]})
p405 = os.path.join(VP_DIR, 'VP-VIEW-20261110-405.json')
raw405 = open(p405, 'rb').read()
outv = vpl.reconcile_label_drift('VIEW-20261110-405', vp_dir=VP_DIR,
                                 views_dir=VIEWS_DIR, root=TD)
check('BINDING_VIOLATION 行在场 → 整档拒写(红线不与对账混写)+文件不变',
      outv.get('ok') is False
      and outv['error']['kind'] == 'binding_violation_present'
      and open(p405, 'rb').read() == raw405,
      json.dumps(outv.get('error'), ensure_ascii=False)[:160])


def cli(*argv):
    return subprocess.run(
        [sys.executable, os.path.join(ROOT, 'scripts', 'view_plausibility.py'),
         *argv], capture_output=True, text=True)


r_ok = cli('--reconcile-drift', 'VIEW-20261110-401', '--vp-dir', VP_DIR,
           '--views-dir', VIEWS_DIR, '--data-root', TD)
check('CLI: 已对账档 → exit 0 + n_reconciled=0(幂等面)',
      r_ok.returncode == 0 and '"n_reconciled": 0' in r_ok.stdout,
      r_ok.stdout[:160] + r_ok.stderr[:160])
r_v = cli('--reconcile-drift', 'VIEW-20261110-405', '--vp-dir', VP_DIR,
          '--views-dir', VIEWS_DIR, '--data-root', TD)
check('CLI: violation 档 → exit 1(拒写可观测)',
      r_v.returncode == 1 and 'binding_violation_present' in r_v.stdout,
      r_v.stdout[:160])
r_all = cli('--reconcile-drift-all', '--vp-dir', VP_DIR,
            '--views-dir', VIEWS_DIR, '--data-root', TD)
check('CLI --reconcile-drift-all: 档区含 violation 档 → 汇总 exit 1'
      '(拒写可观测,不静默吞)',
      r_all.returncode == 1 and '"n_ok": 3' in r_all.stdout
      and 'binding_violation_present' in r_all.stdout, r_all.stdout[:200])

# ════════════════════════════════════════════════════════════════════
section('5 · dry-run(零写+无 .tmp 残留)')
# ════════════════════════════════════════════════════════════════════
mk_view('VIEW-20261110-406', '2026-11-10', '12m', forecasts=[
    {'target': '联邦基金利率', 'value_or_direction': '维持3.75%-4.00%',
     'horizon': '当前(会后即刻)', 'attribution': 'institution_stated'}])
write_vp('VIEW-20261110-406', {
    'schema_version': '1.0', 'view_id': 'VIEW-20261110-406',
    'generated_by': 'synthetic-v1.0-era', 'view_label': 'INSUFFICIENT_EVIDENCE',
    'hypotheses': [hyp('INSUFFICIENT_EVIDENCE', 0, 'no_forecast',
                       linked=[0])]})
p406 = os.path.join(VP_DIR, 'VP-VIEW-20261110-406.json')
raw406 = open(p406, 'rb').read()
outd = vpl.reconcile_label_drift('VIEW-20261110-406', vp_dir=VP_DIR,
                                 views_dir=VIEWS_DIR, root=TD, dry_run=True)
check('dry-run: 判定面完整(n_reconciled=1)+零写(字节不变)',
      outd.get('ok') is True and outd.get('n_reconciled') == 1
      and outd.get('written') is False and open(p406, 'rb').read() == raw406)
check('无 .tmp 残留(原子写纪律: temp+os.replace)',
      not any(n.endswith('.tmp') for n in os.listdir(VP_DIR)),
      str([n for n in os.listdir(VP_DIR) if n.endswith('.tmp')]))
# 实写一轮后同样无残留
vpl.reconcile_label_drift('VIEW-20261110-406', vp_dir=VP_DIR,
                          views_dir=VIEWS_DIR, root=TD)
check('实写后亦无 .tmp 残留',
      not any(n.endswith('.tmp') for n in os.listdir(VP_DIR)))
# 全净档区聚合: 幂等汇总面 exit 0
VP_DIR_CLEAN = os.path.join(TD, 'vp_clean')
os.makedirs(VP_DIR_CLEAN)
for vid in ('VIEW-20261110-401', 'VIEW-20261110-406'):
    with open(os.path.join(VP_DIR, f'VP-{vid}.json'), 'rb') as fsrc, \
            open(os.path.join(VP_DIR_CLEAN, f'VP-{vid}.json'), 'wb') as fdst:
        fdst.write(fsrc.read())
r_all2 = cli('--reconcile-drift-all', '--vp-dir', VP_DIR_CLEAN,
             '--views-dir', VIEWS_DIR, '--data-root', TD)
check('CLI --reconcile-drift-all: 全净档区 → exit 0+n_reconciled_rows=0'
      '(幂等汇总面)',
      r_all2.returncode == 0 and '"n_reconciled_rows": 0' in r_all2.stdout
      and '"ok": true' in r_all2.stdout, r_all2.stdout[:200])

# ════════════════════════════════════════════════════════════════════
section('6 · 契约前提(no_forecast 存量档自洽性)')
# ════════════════════════════════════════════════════════════════════
check('verdict_to_label(no_forecast)=INSUFFICIENT(未知词汇不猜)——存量档'
      '标签自洽的前提,重贴由对账显式驱动',
      vpl.verdict_to_label('no_forecast') == 'INSUFFICIENT_EVIDENCE')
check('生产漂移两类映射不变: UNPARSEABLE_HORIZON→INSUFFICIENT(标签不动)/'
      'NOT_YET_TESTABLE→NOT_YET_TESTABLE(标签随行)',
      vpl.verdict_to_label('UNPARSEABLE_HORIZON') == 'INSUFFICIENT_EVIDENCE'
      and vpl.verdict_to_label('NOT_YET_TESTABLE') == 'NOT_YET_TESTABLE')

# ════════════════════════════════════════════════════════════════════
print('═' * 64)
print(f'总结: PASS={PASS} FAIL={FAIL}')
sys.exit(0 if FAIL == 0 else 1)
