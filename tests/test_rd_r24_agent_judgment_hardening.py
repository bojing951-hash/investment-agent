#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R24 阶段五前置: agent_judgment R23 审计余留 MINOR-1/4/5+NIT 硬化回归锁。

  §1 CON-REF(MINOR-1): 矛盾陈述零引用拒收;no_anchor_reason 明示免锚放行
  §2 SCN-TYPE(NIT): 五行类型锁——错型显式拒收且不再静默绕过下游检查
  §3 MINOR-4 门槛: run_ok=False 报告默认拒收 attach(layers 不动+attempt
     随档);allow_failed_run 显式越过+随档可审计
  §4 MINOR-5: report.md L1 行渲染 quality_status;免锚理由可见披露
  §5 ia_cli 命令面: --allow-failed-run 旗标+blocked/警告透传
全合成报告面;真实 registry;CI 干净 clone 可跑。
"""
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
import agent_judgment as aj            # noqa: E402
import research_orchestrator as ro     # noqa: E402

REG = wd.load_registry(ROOT)
MIDS = sorted({m['metric_id'] for m in (REG.get('metrics') or [])
               if m.get('metric_id')})
MID_A, MID_B = MIDS[0], MIDS[1]
EV_REFS = {'FACT_A@2026-01-10', 'FACT_B@2026-01-10', 'VP-VIEW-20260101-001'}


def base_judgment():
    """合规 judgment 母本(与 R23 套件同构;矛盾带引用)。"""
    return {
        'schema_version': '1.0',
        'agent_declaration': {'attribution': 'ai_inferred',
                              'note': '编排层 Agent 研判'},
        'l3': {
            'contradictions': [{
                'id': 'CON-1',
                'statement': '合成矛盾陈述(测试母本)',
                'basis': '基于证据索引的推断',
                'competing_explanations': ['解释一(基准)', '解释二(反例)'],
                'evidence_refs': ['FACT_A@2026-01-10',
                                  'VP-VIEW-20260101-001']}],
            'mechanism_chains': [{
                'id': 'MECH-1', 'name': '合成链',
                'links': [
                    {'step': 1, 'text': 'E1 环(引擎可验证)',
                     'evidence_level': 'E1',
                     'evidence_refs': ['FACT_A@2026-01-10']},
                    {'step': 3, 'text': 'E3 环(纯叙事)',
                     'evidence_level': 'E3',
                     'falsification_metric': MID_A}]}]},
        'l4': {
            'scenarios': [
                {'id': 'SCN-A', 'role': '基准', 'rows': {
                    'scenario': '情景A(假设非预测): 合成基准情景',
                    'asset_direction': {'direction': '上行',
                                        'confidence_tier': '有相关证据',
                                        'text': '合成方向判断',
                                        'evidence_refs': ['FACT_A@2026-01-10']},
                    'sensitive_variables': [MID_A],
                    'falsification': {'metric_id': MID_B,
                                      'threshold': '突破合成阈值 X'},
                    'trigger': {'condition': '合成可观测条件',
                                'deadline': '2027-06-30'}}},
                {'id': 'SCN-B', 'role': '反例', 'rows': {
                    'scenario': '情景B(假设非预测): 合成反例情景',
                    'asset_direction': {'direction': '区间',
                                        'confidence_tier': '纯逻辑推理',
                                        'text': '合成反例方向',
                                        'evidence_refs': []},
                    'sensitive_variables': [MID_B],
                    'falsification': {'metric_id': MID_A,
                                      'threshold': '跌破合成阈值 Y'},
                    'trigger': {'condition': '合成反例条件',
                                'deadline': '2027-06-30'}}}]},
    }


def codes(res):
    return {x['code'] for x in res['violations']}


def synth_report(run_ok=True, l1_rows=None):
    evidence = [
        {'ref': 'FACT_A@2026-01-10', 'kind': 'snapshot_fact', 'metric_id': MID_A},
        {'ref': 'FACT_B@2026-01-10', 'kind': 'snapshot_fact', 'metric_id': MID_B},
        {'ref': 'VP-VIEW-20260101-001', 'kind': 'vp_sidecar',
         'view_label': '合成观点'}]
    return {
        'schema_version': '2.0', 'pipeline_version': ro.PIPELINE_VERSION,
        'run': {'question': '合成问题', 'ts_utc': '20260101T000000Z',
                'archive_requested': False, 'git_head': None},
        'steps': [], 'fanout': {'requested': False},
        'layers': {
            'L1_事实层': {'available': True, 'snapshot_id': 'SYNTH',
                          'target_date': '2026-01-10', 'n_facts_total': 2,
                          'rows': l1_rows if l1_rows is not None else [], 'note': None},
            'L2_机构观点层': {'views': {'available': True, 'n': 1, 'rows': [],
                                        'n_bad_quarantined': 0}, 'note': '合成'},
            'L3_AI推断层': {'produced': False, 'note': '零模型管线: 不代写'},
            'L4_条件情景层': {'produced': False, 'note': '零模型管线: 不代写'}},
        'evidence_index': evidence, 'notes': [], 'run_ok': run_ok}


def setup_run(tmpdir, report):
    rd = os.path.join(tmpdir, 'run')
    os.makedirs(rd, exist_ok=True)
    with open(os.path.join(rd, 'report.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    with open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8') as f:
        f.write(ro._render_md(report))
    jp = os.path.join(tmpdir, 'judgment.json')
    with open(jp, 'w', encoding='utf-8') as f:
        json.dump(base_judgment(), f, ensure_ascii=False, indent=2)
    return rd, jp


# ══════════════════════════════════════════════════════════════════
section('1 CON-REF 矛盾零引用(MINOR-1: 零锚拒收,明示免锚放行)')
# ══════════════════════════════════════════════════════════════════
j = base_judgment()
check('母本(矛盾带引用)全绿',
      aj.validate_judgment(j, EV_REFS, set(MIDS))['passed'])

j = base_judgment()
j['l3']['contradictions'][0]['evidence_refs'] = []
r = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('矛盾零引用 → CON-REF 拒收',
      (not r['passed']) and 'CON-REF' in codes(r), f'violations={r["violations"]}')

j = base_judgment()
del j['l3']['contradictions'][0]['evidence_refs']
r = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('矛盾缺 evidence_refs 键 → CON-REF',
      (not r['passed']) and 'CON-REF' in codes(r))

j = base_judgment()
j['l3']['contradictions'][0]['evidence_refs'] = []
j['l3']['contradictions'][0]['no_anchor_reason'] = (
    '纯概念张力陈述,无对应引擎可观测锚(明示免锚)')
r = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('no_anchor_reason 非空 → 免锚放行',
      r['passed'], f'violations={r["violations"]}')

j = base_judgment()
j['l3']['contradictions'][0]['evidence_refs'] = []
j['l3']['contradictions'][0]['no_anchor_reason'] = '   '
r = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('免锚理由空白串 → 仍 CON-REF',
      (not r['passed']) and 'CON-REF' in codes(r))

j = base_judgment()
j['l3']['contradictions'][0]['evidence_refs'] = ['FAKE@2026-01-10']
r = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('悬空引用(非零) → REF 不误报 CON-REF',
      'REF' in codes(r) and 'CON-REF' not in codes(r))

# ══════════════════════════════════════════════════════════════════
section('2 SCN-TYPE 五行类型锁(NIT: 错型显式拒收)')
# ══════════════════════════════════════════════════════════════════
j = base_judgment()
j['l4']['scenarios'][0]['rows']['scenario'] = {
    'text': '错型: dict 冒充情景行'}
r = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('scenario 传 dict → SCN-TYPE(不再静默绕过 SCN-ASSUM)',
      (not r['passed']) and 'SCN-TYPE' in codes(r)
      and 'SCN-ASSUM' not in codes(r), f'codes={codes(r)}')

j = base_judgment()
j['l4']['scenarios'][0]['rows']['asset_direction'] = '上行'
r = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('asset_direction 传 str → SCN-TYPE(不再静默绕过 SCN-DIR)',
      (not r['passed']) and 'SCN-TYPE' in codes(r)
      and 'SCN-DIR' not in codes(r), f'codes={codes(r)}')

j = base_judgment()
j['l4']['scenarios'][0]['rows']['sensitive_variables'] = MID_A
r = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('sensitive_variables 传 str → SCN-TYPE(不再静默绕过 SCN-SENS)',
      (not r['passed']) and 'SCN-TYPE' in codes(r)
      and 'SCN-SENS' not in codes(r), f'codes={codes(r)}')

j = base_judgment()
j['l4']['scenarios'][0]['rows']['falsification'] = ['metric', '阈值']
r = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('falsification 传 list → SCN-TYPE(不再静默绕过 SCN-FALS)',
      (not r['passed']) and 'SCN-TYPE' in codes(r)
      and 'SCN-FALS' not in codes(r), f'codes={codes(r)}')

j = base_judgment()
j['l4']['scenarios'][0]['rows']['trigger'] = '随时触发'
r = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('trigger 传 str → SCN-TYPE(不再静默绕过 SCN-TRIG)',
      (not r['passed']) and 'SCN-TYPE' in codes(r)
      and 'SCN-TRIG' not in codes(r), f'codes={codes(r)}')

check('正确类型母本不受类型锁误伤',
      aj.validate_judgment(base_judgment(), EV_REFS, set(MIDS))['passed'])

# ══════════════════════════════════════════════════════════════════
section('3 MINOR-4 attach 门槛: run_ok=False 默认拒收')
# ══════════════════════════════════════════════════════════════════
tmp = tempfile.mkdtemp(prefix='r24_gate_')
rd, jp = setup_run(tmp, synth_report(run_ok=False))
res = aj.attach_judgment(rd, jp, root=ROOT)
check('run_ok=False → blocked=run_ok_false,attached=False',
      res['attached'] is False and res.get('blocked') == 'run_ok_false')
rj = json.load(open(os.path.join(rd, 'report.json')))
check('layers 不动(produced 仍 False)',
      rj['layers']['L3_AI推断层']['produced'] is False
      and rj['layers']['L4_条件情景层']['produced'] is False)
check('attempt 随档(agent_judgment.blocked)',
      rj['agent_judgment']['blocked'] == 'run_ok_false'
      and rj['agent_judgment']['attached'] is False)
check('judgment 副本未落(不半落位)',
      not os.path.exists(os.path.join(rd, 'agent_judgment.json')))

res = aj.attach_judgment(rd, jp, root=ROOT, allow_failed_run=True)
rj = json.load(open(os.path.join(rd, 'report.json')))
check('allow_failed_run=True → 放行落位',
      res['attached'] is True
      and rj['layers']['L3_AI推断层']['produced'] is True)
check('越过面随档可审计',
      rj['agent_judgment']['run_ok_at_attach'] is False
      and rj['agent_judgment']['allow_failed_run'] is True)

tmp = tempfile.mkdtemp(prefix='r24_ok_')
rd, jp = setup_run(tmp, synth_report(run_ok=True))
res = aj.attach_judgment(rd, jp, root=ROOT)
rj = json.load(open(os.path.join(rd, 'report.json')))
check('run_ok=True 正常路不受门槛影响',
      res['attached'] is True and 'blocked' not in res)
check('正常路 run_ok_at_attach 随档',
      rj['agent_judgment']['run_ok_at_attach'] is True
      and rj['agent_judgment']['allow_failed_run'] is False)

tmp = tempfile.mkdtemp(prefix='r24_legacy_')
rep = synth_report(run_ok=True)
del rep['run_ok']  # 旧档无 run_ok 键(=未知,非显式失败)
rd, jp = setup_run(tmp, rep)
res = aj.attach_judgment(rd, jp, root=ROOT)
check('run_ok 缺席(旧档)不误拦', res['attached'] is True)

# ══════════════════════════════════════════════════════════════════
section('4 MINOR-5 md 渲染: quality_status 随行+免锚可见')
# ══════════════════════════════════════════════════════════════════
l1_rows = [{'metric_id': MID_A, 'value': 1.23, 'unit': '%',
            'observation_date': '2026-01-10', 'quality_status': 'DEGRADED',
            'source': {'kind': 'snapshot_fact', 'id': 'FACT_A@2026-01-10'}}]
md = ro._render_md(synth_report(run_ok=True, l1_rows=l1_rows))
check('L1 行渲染 quality_status', '[质量:DEGRADED]' in md)
check('来源标注仍在', f'[来源:snapshot_fact:FACT_A@2026-01-10]' in md)

rep = synth_report(run_ok=True, l1_rows=[
    {'metric_id': MID_B, 'value': 2.0, 'unit': '%',
     'observation_date': '2026-01-10', 'quality_status': None,
     'source': {'kind': 'snapshot_fact', 'id': 'FACT_B@2026-01-10'}}])
md = ro._render_md(rep)
check('quality_status 缺席不渲空括号', '[质量:' not in md)

j = base_judgment()
j['l3']['contradictions'][0]['evidence_refs'] = []
j['l3']['contradictions'][0]['no_anchor_reason'] = '纯概念张力(明示免锚)'
rep = synth_report(run_ok=True)
rep['layers']['L3_AI推断层'] = {'produced': True,
                                 'attribution': 'ai_inferred',
                                 'content': j['l3'], 'note': '合成已落位'}
md = ro._render_md(rep)
check('免锚理由在 md 可见披露', '无锚(明示免锚: 纯概念张力(明示免锚))' in md)

# ══════════════════════════════════════════════════════════════════
section('5 ia_cli 命令面: --allow-failed-run+blocked 透传')
# ══════════════════════════════════════════════════════════════════
tmp = tempfile.mkdtemp(prefix='r24_cli_')
rd, jp = setup_run(tmp, synth_report(run_ok=False))
p = subprocess.run(
    [sys.executable, os.path.join(ROOT, 'ia_cli.py'), 'research-attach',
     '--report-dir', rd, '--judgment', jp],
    capture_output=True, text=True, timeout=120)
check('CLI rc=1(门槛拦)', p.returncode == 1, p.stdout[-400:] + p.stderr[-200:])
check('CLI warnings 含门槛提示', 'run_ok=False' in p.stdout
      and '--allow-failed-run' in p.stdout)
env = dict(os.environ, PYTHONIOENCODING='utf-8')
p2 = subprocess.run(
    [sys.executable, os.path.join(ROOT, 'ia_cli.py'), 'research-attach',
     '--report-dir', rd, '--judgment', jp, '--allow-failed-run'],
    capture_output=True, text=True, timeout=120, env=env)
check('CLI --allow-failed-run rc=0(放行)', p2.returncode == 0,
      p2.stdout[-400:] + p2.stderr[-200:])
check('CLI data 透传 run_ok_at_attach',
      '"run_ok_at_attach": false' in p2.stdout)

# ── 汇总 ──────────────────────────────────────────────────────────
print('═' * 64)
print(f'结果: PASS={PASS} FAIL={FAIL}')
print('═' * 64)
sys.exit(0 if FAIL == 0 else 1)
