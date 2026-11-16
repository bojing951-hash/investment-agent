#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R1 F02 回归: 独立审查四态门(生成≠校验≠审查≠可交付)。

外审复现的缺陷: report 段 L3/L4 produced=true + semantic_review.required=true
且 verdict=REVISE 时仍返回 ok=true、warnings 空——「已生成」冒充「可交付」。

本套件锁:
  A. 四态分立: generated / machine_verified / review / deliverable;
  B. required 且审查缺席/REVISE/未绑定哈希(过期)→ ok=false + warnings
     非空 + exit 1;VERIFIED+fresh → ok=true;
  C. 修订链: 正文修订→旧裁决 fresh=False→复验新档→verdicts_n 累计,
     旧失败档不覆盖;
  D. 降级分级: critical_zero_evidence 旗标不放行;optional_data_missing
     须旗标且放行后落 validation 阶段(不再 run_ok 拦);
  E. produced=False → 不 required,但 machine_verified=False 仍不可交付。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import agent_judgment as aj  # noqa: E402

PASS, FAIL = 0, 0
_RUN_SEQ = 0


def check(name, cond, detail=''):
    global PASS, FAIL
    print(f"  {'✅' if cond else '❌'} {name}" + (f" — {detail}" if detail and not cond else ''))
    PASS, FAIL = PASS + (1 if cond else 0), FAIL + (0 if cond else 1)


def make_run(tmp, name, *, run_ok=True, l1_rows=2, produced=True,
             validation_passed=True, run_ts=None, attach_meta=True):
    global _RUN_SEQ
    if run_ts is None:
        # 裁决匹配按 run.ts_utc 键控——每个合成 run 须独立 ts 命名空间,
        # 否则他 run 的裁决档泄入本 run 的 verdicts_n/修订链
        _RUN_SEQ += 1
        run_ts = '20261116T12%04dZ' % _RUN_SEQ
    rd = os.path.join(tmp, name)
    os.makedirs(rd, exist_ok=True)
    rows = [{'metric_id': 'TEST_M%d' % i, 'value': 1.0 * i, 'unit': 'x',
             'observation_date': '2026-11-09', 'quality_status': 'OK',
             'source': {'id': 'src%d' % i, 'kind': 'synthetic'}}
            for i in range(l1_rows)]
    report = {
        'schema_version': '2.0', 'pipeline_version': 't',
        'run': {'question': '审计回归合成问题', 'ts_utc': run_ts,
                'git_head': 'synthetic',
                'degradation_policy': {
                    'critical_zero_evidence': 'L1=0 拒收,旗标不放行',
                    'optional_data_missing': 'L1 在场+诚实拒答须旗标'}},
        'steps': [], 'fanout': {},
        'layers': {
            'L1_事实层': {'rows': rows, 'available': l1_rows > 0,
                         'n': l1_rows, 'note': '合成: 无事实行'},
            'L2_机构观点层': {'views': {'available': False, 'n': 0,
                                        'note': '合成: 观点库缺席'}},
            'L3_AI推断层': {'produced': produced, 'attribution': 'ai_inferred',
                           'note': '合成: L3 注记'},
            'L4_条件情景层': {'produced': produced, 'attribution': 'ai_inferred',
                           'note': '合成: L4 注记'}},
        'evidence_index': [{'kind': 'metric', 'ref': 'TEST_M0@2026-11-09'},
                           {'kind': 'metric', 'ref': 'TEST_M1@2026-11-09'}
                           ][:max(l1_rows, 0)],
        'notes': [], 'run_ok': run_ok}
    if attach_meta:
        report['agent_judgment'] = {
            'attached': True, 'judgment_file': 'judgment.json',
            'validation': {'passed': validation_passed, 'violations': []},
            'run_ok_at_attach': True if run_ok else True}
    json.dump(report, open(os.path.join(rd, 'report.json'), 'w',
                           encoding='utf-8'), ensure_ascii=False)
    json.dump({'schema_version': aj.JUDGMENT_SCHEMA_VERSION,
               'agent_declaration': {'role': 'synthetic'},
               'l3': {'claims': []}, 'l4': {'scenarios': []}},
              open(os.path.join(rd, 'agent_judgment.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8').write(
        '# 合成报告\n\n研究正文(供内容摘要绑定)。\n')
    return rd


def write_verdict(root, rd, overall, sha=None, run_ts=None, legacy=False):
    if run_ts is None:
        # 与生产一致: 裁决档文件名内嵌该 run 的 ts_utc(匹配键)
        run_ts = json.load(open(os.path.join(rd, 'report.json'),
                                encoding='utf-8'))['run']['ts_utc']
    day = '20261116'
    d = os.path.join(root, 'audit', 'semantic_review', day)
    os.makedirs(d, exist_ok=True)
    seq = len([f for f in os.listdir(d) if run_ts in f]) + 1
    doc = {'overall': overall, 'reviewer': 'SYNTH-SEAT', 'notes': '',
           'run_ts': run_ts}
    if not legacy:
        doc['content_sha256'] = sha or aj.content_digest(rd)
    p = os.path.join(d, 'VERDICT-%s-%02d.json' % (run_ts, seq))
    json.dump(doc, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    return p


def report_stage(rd, engine_root):
    return subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'report',
         '--report-dir', rd, '--engine-root', engine_root],
        cwd=ROOT, capture_output=True, text=True, timeout=120)


def attach_stage(rd, engine_root, allow=False):
    j = os.path.join(rd, 'agent_judgment.json')
    argv = [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'attach',
            '--report-dir', rd, '--judgment', j,
            '--engine-root', engine_root]
    if allow:
        argv.append('--allow-failed-run')
    return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                          timeout=120)


print('═' * 64)
print('F02 独立审查四态门回归')
print('═' * 64)

tmp = tempfile.mkdtemp(prefix='f02_')
eroot = os.path.join(tmp, 'engine')
os.makedirs(eroot, exist_ok=True)
# attach 放行路径会真调 validate_judgment → 读 engine_root 指标注册表
# (合成引擎根补真注册表副本;裁决档仍只落合成根,不污染仓库)
os.makedirs(os.path.join(eroot, 'config'), exist_ok=True)
shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
            os.path.join(eroot, 'config', 'metric_registry.json'))

# ── A/B: required+缺席 → 不可交付 ──
rd1 = make_run(tmp, 'r1')
r = report_stage(rd1, eroot)
e1 = json.loads(r.stdout)
check('A1 required+审查缺席 → ok=false+exit1',
      e1['ok'] is False and r.returncode == 1)
check('A2 warnings 非空且指明审查缺席',
      e1['warnings'] and '缺席' in e1['warnings'][0])
check('A3 四态齐(generated/machine_verified/review/deliverable)',
      e1['data']['generated'] is True and e1['data']['machine_verified'] is True
      and e1['data']['review']['required'] is True
      and e1['data']['deliverable'] is False)

# ── B: REVISE → 不可交付 ──
rd2 = make_run(tmp, 'r2')
write_verdict(eroot, rd2, 'REVISE')
e2 = json.loads(report_stage(rd2, eroot).stdout)
check('B1 verdict=REVISE → ok=false+deliverable=false',
      e2['ok'] is False and e2['data']['deliverable'] is False)
check('B2 warning 点名 REVISE',
      any('REVISE' in w for w in e2['warnings']))

# ── B: VERIFIED+fresh → 可交付 ──
rd3 = make_run(tmp, 'r3')
write_verdict(eroot, rd3, 'VERIFIED')
e3 = json.loads(report_stage(rd3, eroot).stdout)
check('B3 VERIFIED+绑定哈希匹配 → ok=true+exit0',
      e3['ok'] is True and e3['data']['deliverable'] is True)
check('B4 mvp_complete 与 deliverable 同步',
      e3['data']['mvp_complete'] is True)

# ── C: 修订链(正文修订→旧裁决过期→复验新档) ──
rd4 = make_run(tmp, 'r4')
write_verdict(eroot, rd4, 'VERIFIED')
open(os.path.join(rd4, 'report.md'), 'a', encoding='utf-8').write(
    '\n修订段: 正文变更(旧裁决应失效)。\n')
e4a = json.loads(report_stage(rd4, eroot).stdout)
check('C1 正文修订后旧 VERIFIED 过期 → 不可交付',
      e4a['ok'] is False and e4a['data']['review']['fresh'] is False)
check('C2 过期 warning 在档', any('过期' in w for w in e4a['warnings']))
write_verdict(eroot, rd4, 'VERIFIED')
e4b = json.loads(report_stage(rd4, eroot).stdout)
check('C3 复验新档 → 可交付+修订链计数=2+旧档不覆盖',
      e4b['ok'] is True and e4b['data']['review']['verdicts_n'] == 2
      and len(e4b['data']['review'].get('prior_verdicts', [])) == 1)

# ── B: 旧档无绑定键(legacy) → 在场不冒充新鲜 ──
rd5 = make_run(tmp, 'r5')
write_verdict(eroot, rd5, 'VERIFIED', legacy=True)
e5 = json.loads(report_stage(rd5, eroot).stdout)
check('B5 legacy 裁决无哈希绑定 → fresh=None 不可交付',
      e5['ok'] is False and e5['data']['review']['fresh'] is None)

# ── D: 降级分级 ──
rd6 = make_run(tmp, 'r6', run_ok=False, l1_rows=0)
d6 = json.loads(attach_stage(rd6, eroot, allow=True).stdout)['data']
check('D1 critical_zero_evidence: 旗标亦不放行',
      d6.get('attached') is False
      and d6.get('blocked_class') == 'critical_zero_evidence')
rd7 = make_run(tmp, 'r7', run_ok=False, l1_rows=2)
d7a = json.loads(attach_stage(rd7, eroot, allow=False).stdout)['data']
check('D2 optional: 无旗标拦截', d7a.get('attached') is False
      and d7a.get('blocked_class') == 'optional_data_missing')
d7b = json.loads(attach_stage(rd7, eroot, allow=True).stdout)['data']
check('D3 optional: 有旗标放行至校验层(不再 run_ok 拦)',
      d7b.get('blocked') is None and d7b.get('validation_passed') is False)

# ── E: produced=False → 不 required 但仍不可交付 ──
rd8 = make_run(tmp, 'r8', produced=False)
e8 = json.loads(report_stage(rd8, eroot).stdout)
check('E1 produced=False → required=false 但 ok=false(L3/L4 未全)',
      e8['data']['review']['required'] is False and e8['ok'] is False)

print(f"\nF02 判定: {PASS} PASS / {FAIL} FAIL")
sys.exit(0 if FAIL == 0 else 1)
