#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R23 阶段四 Agent Native L3/L4 落位回归锁(Charter 10 §六)。

  §1 validate_judgment 纯函数: 合规 judgment 全绿(真实 registry 指标面)
  §2 违规变异矩阵: 13 类纪律码逐一变异触发(锁有牙,防为过校验稀释)
  §3 attach 半落位纪律: 过=produced True+原文入档+md 重渲;
     不过=produced 保持 False+violations 落档(绝不半落位)
  §4 零生成不变式: 落位内容与 judgment 文件 deep-equal(校验器零改写)
  §5 ia_cli research-attach 命令面: 实解析+真实子进程信封+退出码
全合成报告面(合成 evidence_index/layers);真实 registry;CI 干净 clone 可跑。
"""
import copy
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
    """合规 judgment 模板(所有变异的母本)。"""
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
                    {'step': 2, 'text': 'E2 环(部分支持)',
                     'evidence_level': 'E2',
                     'missing_link_note': '本引擎无该序列,此环为【假设】',
                     'evidence_refs': ['FACT_B@2026-01-10']},
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


def synth_report(tmpdir, n_ev=3):
    """最小合成 research-run 报告(attach 只依赖 layers/evidence_index 面)。"""
    evidence = [
        {'ref': 'FACT_A@2026-01-10', 'kind': 'snapshot_fact',
         'metric_id': MID_A},
        {'ref': 'FACT_B@2026-01-10', 'kind': 'snapshot_fact',
         'metric_id': MID_B},
        {'ref': 'VP-VIEW-20260101-001', 'kind': 'vp_sidecar',
         'view_label': '合成观点'}][:n_ev]
    return {
        'schema_version': '2.0', 'pipeline_version': ro.PIPELINE_VERSION,
        'run': {'question': '合成问题', 'ts_utc': '20260101T000000Z',
                'archive_requested': False, 'git_head': None},
        'steps': [], 'fanout': {'requested': False},
        'layers': {
            'L1_事实层': {'available': True, 'snapshot_id': 'SYNTH',
                          'target_date': '2026-01-10', 'n_facts_total': 2,
                          'rows': [], 'note': None},
            'L2_机构观点层': {'views': {'available': True, 'n': 1, 'rows': [],
                                        'n_bad_quarantined': 0},
                               'note': '合成'},
            'L3_AI推断层': {'produced': False, 'note': '零模型管线: 不代写'},
            'L4_条件情景层': {'produced': False, 'note': '零模型管线: 不代写'}},
        'evidence_index': evidence, 'notes': [], 'run_ok': True}


def write_report(tmpdir, report):
    rd = os.path.join(tmpdir, 'run')
    os.makedirs(rd, exist_ok=True)
    with open(os.path.join(rd, 'report.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    with open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8') as f:
        f.write(ro._render_md(report))
    return rd


def write_judgment(tmpdir, judgment, name='judgment.json'):
    p = os.path.join(tmpdir, name)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(judgment, f, ensure_ascii=False, indent=2)
    return p


# ══════════════════════════════════════════════════════════════════
section('1 validate_judgment 纯函数(合规母本+真实 registry)')
# ══════════════════════════════════════════════════════════════════
res = aj.validate_judgment(base_judgment(), EV_REFS, set(MIDS))
check('合规母本全绿', res['passed'] and not res['violations'],
      f"violations={res['violations']}")
check('计数面', res['n_contradictions'] == 1
      and res['n_mechanism_chains'] == 1 and res['n_scenarios'] == 2)
check('非 object 根=SCHEMA 拒', not aj.validate_judgment(
    [], EV_REFS, set(MIDS))['passed'])
check('schema_version 不符=SCHEMA',
      'SCHEMA' in codes(aj.validate_judgment(
          {**base_judgment(), 'schema_version': '0.9'}, EV_REFS, set(MIDS))))
check('空 contradictions=SCHEMA', 'SCHEMA' in codes(aj.validate_judgment(
    {**base_judgment(),
     'l3': {'contradictions': [], 'mechanism_chains': []}},
    EV_REFS, set(MIDS))))

# ══════════════════════════════════════════════════════════════════
section('2 违规变异矩阵(逐码触发=锁有牙)')
# ══════════════════════════════════════════════════════════════════


def mutate(fn):
    j = base_judgment()
    fn(j)
    return aj.validate_judgment(j, EV_REFS, set(MIDS))


def m_attr(j):
    j['agent_declaration']['attribution'] = 'institution_stated'


def m_con_exp(j):
    j['l3']['contradictions'][0]['competing_explanations'] = ['仅一种解释']


def m_ref(j):
    j['l3']['contradictions'][0]['evidence_refs'] = ['FAKE@2026-01-10']


def m_e1_ref(j):
    j['l3']['mechanism_chains'][0]['links'][0]['evidence_refs'] = []


def m_e2_assum(j):
    j['l3']['mechanism_chains'][0]['links'][1]['missing_link_note'] = '无缺失'


def m_e3_fals(j):
    j['l3']['mechanism_chains'][0]['links'][2]['falsification_metric'] = 'NOT_A_METRIC'


def m_scn_five(j):
    del j['l4']['scenarios'][0]['rows']['trigger']


def m_scn_assum(j):
    j['l4']['scenarios'][0]['rows']['scenario'] = '情景A: 必然发生的预测'


def m_scn_dir(j):
    j['l4']['scenarios'][0]['rows']['asset_direction']['confidence_tier'] = '高置信'


def m_scn_sens(j):
    j['l4']['scenarios'][0]['rows']['sensitive_variables'] = [
        MID_A, MID_B, MIDS[2]]


def m_scn_sens_unreg(j):
    j['l4']['scenarios'][0]['rows']['sensitive_variables'] = ['NOT_A_METRIC']


def m_scn_fals(j):
    j['l4']['scenarios'][0]['rows']['falsification']['threshold'] = ''


def m_scn_trig(j):
    j['l4']['scenarios'][0]['rows']['trigger']['deadline'] = '随时'


def m_scn_plural(j):
    j['l4']['scenarios'] = j['l4']['scenarios'][:1]


MATRIX = [('ATTR 归因冒充机构', 'ATTR', m_attr),
          ('CON-EXP 单一解释', 'CON-EXP', m_con_exp),
          ('REF 悬空证据引用', 'REF', m_ref),
          ('E1-REF E1 环零引用', 'E1-REF', m_e1_ref),
          ('E2-ASSUM 缺失环不明写假设', 'E2-ASSUM', m_e2_assum),
          ('E3-FALS 证伪指标不在册', 'E3-FALS', m_e3_fals),
          ('SCN-FIVE 五行缺一', 'SCN-FIVE', m_scn_five),
          ('SCN-ASSUM 情景冒充预测', 'SCN-ASSUM', m_scn_assum),
          ('SCN-DIR 置信层级越枚举', 'SCN-DIR', m_scn_dir),
          ('SCN-SENS 敏感变量超2', 'SCN-SENS', m_scn_sens),
          ('SCN-SENS 敏感变量不在册', 'SCN-SENS', m_scn_sens_unreg),
          ('SCN-FALS 阈值为空', 'SCN-FALS', m_scn_fals),
          ('SCN-TRIG 时限非日期', 'SCN-TRIG', m_scn_trig),
          ('SCN-PLURAL 单一情景孤证', 'SCN-PLURAL', m_scn_plural)]
for name, code, fn in MATRIX:
    r = mutate(fn)
    check(f'{name} → {code}', (not r['passed']) and code in codes(r),
          f"violations={r['violations']}")
# 变异面不误伤: 每个变异只触发其目标码族(无 SCHEMA 连坐)
r = mutate(m_scn_trig)
check('变异不连坐(单一变异只出目标码)', codes(r) == {'SCN-TRIG'},
      f"codes={codes(r)}")

# ══════════════════════════════════════════════════════════════════
section('3 attach 半落位纪律(过=落位/不过=保持 False)')
# ══════════════════════════════════════════════════════════════════
with tempfile.TemporaryDirectory() as td:
    rd = write_report(td, synth_report(td))
    jp = write_judgment(td, base_judgment())
    res = aj.attach_judgment(rd, jp, root=ROOT)
    check('合规 attach 成功', res['attached'] and res['validation']['passed'])
    check('L3/L4 produced=True',
          res['layers_summary']['L3_produced']
          and res['layers_summary']['L4_produced'])
    rep = json.load(open(os.path.join(rd, 'report.json')))
    check('attribution=ai_inferred 落层',
          rep['layers']['L3_AI推断层']['attribution'] == 'ai_inferred'
          and rep['layers']['L4_条件情景层']['attribution'] == 'ai_inferred')
    check('judgment 副本入档',
          json.load(open(os.path.join(rd, 'agent_judgment.json')))
          == base_judgment())
    md = open(os.path.join(rd, 'report.md')).read()
    check('report.md 重渲含 L3 内容',
          'CON-1' in md and '竞争性解释1' in md and 'E1 环' in md)
    check('report.md 重渲含 L4 五行',
          'SCN-A' in md and '证伪指标' in md and '触发条件' in md)

    # 不过=半落位拒绝
    jbad = base_judgment()
    jbad['l3']['contradictions'][0]['evidence_refs'] = ['FAKE@2026-01-10']
    jbad['l4']['scenarios'] = jbad['l4']['scenarios'][:1]
    jp2 = write_judgment(td, jbad, 'judgment_bad.json')
    res2 = aj.attach_judgment(rd, jp2, root=ROOT)
    check('违规 attach 拒绝', not res2['attached'])
    rep2 = json.load(open(os.path.join(rd, 'report.json')))
    check('produced 保持 False(绝不半落位)',
          not rep2['layers']['L3_AI推断层']['produced']
          and not rep2['layers']['L4_条件情景层']['produced'])
    check('violations 落档供修订重提',
          {'REF', 'SCN-PLURAL'} <= codes(rep2['agent_judgment']['validation']))
    check('attached=False 时 judgment 副本不写(旧档保持)',
          json.load(open(os.path.join(rd, 'agent_judgment.json')))
          == base_judgment())

    # 修订重提闭环: 修正后再 attach → 恢复 produced=True
    res3 = aj.attach_judgment(rd, jp, root=ROOT)
    check('修订重提恢复 produced=True', res3['attached'])
    check('无过期 content 残留(失败尝试零内容渗入)',
          json.load(open(os.path.join(rd, 'agent_judgment.json')))
          == base_judgment())

# ══════════════════════════════════════════════════════════════════
section('4 零生成不变式(校验器零改写零生成)')
# ══════════════════════════════════════════════════════════════════
with tempfile.TemporaryDirectory() as td:
    rd = write_report(td, synth_report(td))
    jp = write_judgment(td, base_judgment())
    aj.attach_judgment(rd, jp, root=ROOT)
    rep = json.load(open(os.path.join(rd, 'report.json')))
    j = base_judgment()
    check('L3 content 与 judgment 原文 deep-equal',
          rep['layers']['L3_AI推断层']['content'] == j['l3'])
    check('L4 content 与 judgment 原文 deep-equal',
          rep['layers']['L4_条件情景层']['content'] == j['l4'])
    check('确定性面零污染(steps/evidence_index/run 不动)',
          rep['steps'] == [] and rep['run_ok'] is True
          and len(rep['evidence_index']) == 3)

# ══════════════════════════════════════════════════════════════════
section('5 ia_cli research-attach 命令面(子进程信封+退出码)')
# ══════════════════════════════════════════════════════════════════
sys.path.insert(0, ROOT)
import ia_cli  # noqa: E402

parser = ia_cli.build_parser()
ns = parser.parse_args(['research-attach', '--report-dir', '/tmp/x',
                        '--judgment', '/tmp/j.json'])
check('子命令实解析', ns.capability == 'research-attach'
      and ns.report_dir == '/tmp/x' and ns.judgment == '/tmp/j.json')
check('handlers 注册 research-attach',
      hasattr(ia_cli, 'cmd_research_attach'))

with tempfile.TemporaryDirectory() as td:
    rd = write_report(td, synth_report(td))
    jp = write_judgment(td, base_judgment())
    p = subprocess.run([sys.executable, os.path.join(ROOT, 'ia_cli.py'),
                        'research-attach', '--report-dir', rd,
                        '--judgment', jp],
                       capture_output=True, text=True, timeout=120, cwd=ROOT)
    env = json.loads(p.stdout)
    check('合规子进程: 信封 ok+exit 0',
          p.returncode == 0 and env['ok'] and env['capability'] == 'research-attach'
          and env['data']['attached'] and env['data']['layers_summary']['L3_produced'])
    check('信封载 violations 计数面',
          env['data']['validation']['n_violations'] == 0
          and env['data']['validation']['n_scenarios'] == 2)

    jbad = base_judgment()
    jbad['agent_declaration']['attribution'] = 'institution_stated'
    jp2 = write_judgment(td, jbad, 'bad2.json')
    p2 = subprocess.run([sys.executable, os.path.join(ROOT, 'ia_cli.py'),
                         'research-attach', '--report-dir', rd,
                         '--judgment', jp2],
                        capture_output=True, text=True, timeout=120, cwd=ROOT)
    env2 = json.loads(p2.stdout)
    check('违规子进程: ok=False+exit 1+ATTR 明细',
          p2.returncode == 1 and not env2['ok']
          and any(w.startswith('ATTR') for w in env2['warnings']))
    check('违规后报告 produced 仍 False(子进程面复核)',
          not env2['data']['layers_summary']['L3_produced'])

# ══════════════════════════════════════════════════════════════════
print('═' * 64)
print(f'总计: PASS={PASS} FAIL={FAIL}')
print('═' * 64)
sys.exit(0 if FAIL == 0 else 1)
