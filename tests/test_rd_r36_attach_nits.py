#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R36 操作者紧凑波: R25 审计余留 NIT 三修回归锁。

  §1 Ni-3 原子写: _atomic_write_text 临时文件+os.replace;_write_report
     先渲 md 后落盘(渲染异常=两文件都不动,不产生 json 新/md 旧中间态);
     成功路径零 .tmp 残留
  §2 Ni-2 attach 历史: 重 attach 不抹上一轮记录——压缩进 attach_history
     追加链(含 blocked/validation.passed/契约 verdict 摘要),最近 5 轮
  §3 Ni-4 副指标重复: secondary_metric_ids 与主锚重复/内部重复 →
     SCN-FALS2 契约明示拒(不静默去重);合法副表不受影响
全合成报告面;真实 registry;CI 干净 clone 可跑。
"""
import json
import os
import sys
import tempfile
from unittest import mock

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
    """合规 judgment 母本(与 R24 套件同构)。"""
    return {
        'schema_version': '1.1',
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
                                      'threshold': '突破合成阈值 4.5'},
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
                                      'threshold': '跌破合成阈值 2.5'},
                    'trigger': {'condition': '合成反例条件',
                                'deadline': '2027-06-30'}}}]},
    }


def codes(res):
    return {x['code'] for x in res['violations']}


def synth_report(run_ok=True):
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
                          'rows': [], 'note': None},
            'L2_机构观点层': {'views': {'available': True, 'n': 1,
                                        'rows': [{'view_id': 'VIEW-20260101-001',
                                                  'view_label': 'SUPPORTING'}],
                                        'n_bad_quarantined': 0}, 'note': '合成'},
            'L3_AI推断层': {'produced': False, 'note': '零模型管线: 不代写'},
            'L4_条件情景层': {'produced': False, 'note': '零模型管线: 不代写'}},
        'evidence_index': evidence, 'notes': [], 'run_ok': run_ok}


def setup_run(tmpdir, report, judgment=None):
    rd = os.path.join(tmpdir, 'run')
    os.makedirs(rd, exist_ok=True)
    with open(os.path.join(rd, 'report.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    with open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8') as f:
        f.write(ro._render_md(report))
    jp = os.path.join(tmpdir, 'judgment.json')
    with open(jp, 'w', encoding='utf-8') as f:
        json.dump(judgment or base_judgment(), f, ensure_ascii=False,
                  indent=2)
    return rd, jp


def load_rd(rd, name='report.json'):
    with open(os.path.join(rd, name), encoding='utf-8') as f:
        return json.load(f)


# ══════════════════════════════════════════════════════════════════
section('1 Ni-3 原子写(_atomic_write_text/_write_report)')
# ══════════════════════════════════════════════════════════════════
with tempfile.TemporaryDirectory() as td:
    p = os.path.join(td, 'x.json')
    aj._atomic_write_text(p, '第一版')
    check('新文件写入+内容正确',
          os.path.exists(p) and open(p, encoding='utf-8').read() == '第一版')
    check('成功后零 .tmp 残留',
          not os.path.exists(p + '.tmp')
          and [f for f in os.listdir(td) if f.endswith('.tmp')] == [])

    aj._atomic_write_text(p, '第二版')
    check('覆盖写=新全文',
          open(p, encoding='utf-8').read() == '第二版')
    check('覆盖后仍零 .tmp',
          [f for f in os.listdir(td) if f.endswith('.tmp')] == [])

    # replace 失败注入: 目标保旧全文(要么旧要么新,无半写)
    boom = OSError('合成中断')
    with mock.patch.object(aj.os, 'replace', side_effect=boom):
        try:
            aj._atomic_write_text(p, '第三版')
            raised = False
        except OSError:
            raised = True
    check('replace 中断=异常上抛(调用方可见失败)',
          raised)
    check('中断后目标保旧全文',
          open(p, encoding='utf-8').read() == '第二版')

with tempfile.TemporaryDirectory() as td:
    report = synth_report()
    rd, jp = setup_run(td, report)
    with open(os.path.join(rd, 'report.json'), encoding='utf-8') as f:
        old_json = f.read()
    # 渲染失败注入: 先渲 md 后落盘 → json 不动
    with mock.patch.object(ro, '_render_md',
                           side_effect=RuntimeError('合成渲染崩')):
        try:
            aj._write_report(rd, report, os.path.join(rd, 'report.json'))
            raised = False
        except RuntimeError:
            raised = True
    check('渲染崩=异常上抛且 report.json 保旧全文',
          raised
          and open(os.path.join(rd, 'report.json'),
                   encoding='utf-8').read() == old_json)

    aj._write_report(rd, report, os.path.join(rd, 'report.json'))
    check('_write_report 正常路径 json/md 双落盘',
          load_rd(rd) == report
          and os.path.getsize(os.path.join(rd, 'report.md')) > 0)
    check('正常路径后零 .tmp',
          [f for f in os.listdir(rd) if f.endswith('.tmp')] == [])

# ══════════════════════════════════════════════════════════════════
section('2 Ni-2 attach 历史(重 attach 不抹上一轮记录)')
# ══════════════════════════════════════════════════════════════════
with tempfile.TemporaryDirectory() as td:
    # 第一轮: run_ok=False → blocked(run_ok_false)
    rd, jp = setup_run(td, synth_report(run_ok=False))
    r1 = aj.attach_judgment(rd, jp, root=ROOT)
    m1 = load_rd(rd)['agent_judgment']
    check('首轮 blocked=run_ok_false 且无历史链',
          (not r1['attached']) and m1['blocked'] == 'run_ok_false'
          and 'attach_history' not in m1)

    # 第二轮: 修复底座 → 成功落位;上一轮 blocked 须入历史链
    rep = load_rd(rd)
    rep['run_ok'] = True
    with open(os.path.join(rd, 'report.json'), 'w', encoding='utf-8') as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    r2 = aj.attach_judgment(rd, jp, root=ROOT)
    m2 = load_rd(rd)['agent_judgment']
    check('次轮成功落位',
          r2['attached'] and m2['attached'] is True)
    check('上一轮 blocked 记录入 attach_history',
          len(m2.get('attach_history') or []) == 1
          and m2['attach_history'][0].get('blocked') == 'run_ok_false'
          and m2['attach_history'][0].get('attached') is False)
    check('历史记录带时间戳与判定档名',
          bool(m2['attach_history'][0].get('attached_at'))
          and m2['attach_history'][0].get('judgment_file') == 'judgment.json')

    # 第三轮: 修订后再提(成功→成功);链追加且首轮仍在
    j = base_judgment()
    j['l3']['contradictions'][0]['statement'] = '修订后陈述(再提)'
    with open(jp, 'w', encoding='utf-8') as f:
        json.dump(j, f, ensure_ascii=False, indent=2)
    r3 = aj.attach_judgment(rd, jp, root=ROOT)
    m3 = load_rd(rd)['agent_judgment']
    check('三轮后历史链=2 且时序保持',
          len(m3.get('attach_history') or []) == 2
          and m3['attach_history'][0].get('blocked') == 'run_ok_false'
          and m3['attach_history'][1].get('validation_passed') is True)
    check('当前面=最新一轮(attached/无 blocked 键)',
          r3['attached'] and m3['attached'] is True
          and 'blocked' not in m3)

    # 封顶: 连续重提到第 7 轮,链长 ≤5(防无界)
    for i in range(4):
        j = base_judgment()
        j['l3']['contradictions'][0]['statement'] = f'修订第{chr(0x7532 + i)}轮再提'
        with open(jp, 'w', encoding='utf-8') as f:
            json.dump(j, f, ensure_ascii=False, indent=2)
        aj.attach_judgment(rd, jp, root=ROOT)
    m7 = load_rd(rd)['agent_judgment']
    check('7 轮后历史链封顶 5(最近优先)',
          len(m7.get('attach_history') or []) == 5
          and m7['attach_history'][-1].get('validation_passed') is True)
    check('attach 路径同样零 .tmp',
          [f for f in os.listdir(rd) if f.endswith('.tmp')] == [])

# ══════════════════════════════════════════════════════════════════
section('3 Ni-4 副指标重复契约明示拒(SCN-FALS2)')
# ══════════════════════════════════════════════════════════════════
j = base_judgment()
j['l4']['scenarios'][0]['rows']['falsification']['secondary_metric_ids'] \
    = [MID_A]
r = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('合法副表(异于主锚,无重复)全绿',
      r['passed'], f'violations={r["violations"]}')

j = base_judgment()
j['l4']['scenarios'][0]['rows']['falsification']['secondary_metric_ids'] \
    = [MID_B]
r = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('副指标=主锚 → SCN-FALS2 拒',
      (not r['passed']) and 'SCN-FALS2' in codes(r)
      and any('主锚' in x['detail'] for x in r['violations']),
      f'violations={r["violations"]}')

j = base_judgment()
j['l4']['scenarios'][0]['rows']['falsification']['secondary_metric_ids'] \
    = [MID_A, MID_B]
r = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('副表含主锚(混合) → 拒且消息点名主锚',
      (not r['passed'])
      and any('主锚' in x['detail'] for x in r['violations']),
      f'violations={r["violations"]}')

j = base_judgment()
j['l4']['scenarios'][0]['rows']['falsification']['secondary_metric_ids'] \
    = [MID_A, MID_A]
r = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('副表内部重复 → 拒(不静默去重)',
      (not r['passed'])
      and any('列表内重复' in x['detail'] for x in r['violations']),
      f'violations={r["violations"]}')

# 无副表(单指标条件)不受影响
j = base_judgment()
r = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('无副表(字段缺席)不违规',
      r['passed'], f'violations={r["violations"]}')

# 合法副表过全链 attach(validator+contract 双门)
with tempfile.TemporaryDirectory() as td:
    j = base_judgment()
    j['l4']['scenarios'][0]['rows']['falsification']['secondary_metric_ids'] \
        = [MID_A]
    rd, jp = setup_run(td, synth_report(), judgment=j)
    res = aj.attach_judgment(rd, jp, root=ROOT)
    check('合法副表过全链 attach(含契约门)',
          res['attached'] and res['contract_verification'].get('verdict') == 'VERIFIED',
          f'contract={res["contract_verification"].get("violations")}')

# ── 汇总 ──────────────────────────────────────────────────────────
print('═' * 64)
print(f'结果: PASS={PASS} FAIL={FAIL}')
print('═' * 64)
sys.exit(0 if FAIL == 0 else 1)
