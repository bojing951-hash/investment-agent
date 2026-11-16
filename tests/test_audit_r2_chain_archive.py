#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R2 条目6 回归: 一次输入到最终归档(auto 幂等续链+归档三处核对)。

锁的面:
  R. 恢复不重 plan: --stage auto --report-dir <既有 run> → 链首
     plan(resumed=true)直续,不新建 run 目录;
  S. 已落位不重挂: L3/L4 produced+attached 在案且无新 --judgment →
     attach(skipped)——重挂会改写 attach 台账→摘要变→作废在案裁决;
  T. 归档对象=最终受审版本: 非 deliverable 一律拒归;deliverable 才
     归档,ARCHIVE_MANIFEST 内容摘要=run 目录摘要=裁决锚(三处一致),
     裁链全档随包;
  U. append-only: 归档目录已存在即拒(不覆盖历史)。
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

import agent_judgment as aj          # noqa: E402
import research_orchestrator as ro   # noqa: E402

PASS, FAIL = 0, 0
_RUN_SEQ = 100


def check(name, cond, detail=''):
    global PASS, FAIL
    print(f"  {'✅' if cond else '❌'} {name}" + (f" — {detail}" if detail and not cond else ''))
    PASS, FAIL = PASS + (1 if cond else 0), FAIL + (0 if cond else 1)


def make_run(tmp, name, *, run_ok=True, l1_rows=2, produced=True):
    """合成已挂判定 run(结构面与生产 attach 后同形;复用 F02 套件口径)。"""
    global _RUN_SEQ
    _RUN_SEQ += 1
    run_ts = '20261116T13%04dZ' % _RUN_SEQ
    rd = os.path.join(tmp, name)
    os.makedirs(rd, exist_ok=True)
    rows = [{'metric_id': 'TEST_M%d' % i, 'value': 1.0 * i, 'unit': 'x',
             'observation_date': '2026-11-09', 'quality_status': 'OK',
             'source': {'id': 'src%d' % i, 'kind': 'synthetic'}}
            for i in range(l1_rows)]
    report = {
        'schema_version': '2.0', 'pipeline_version': 't',
        'run': {'question': 'Audit-R2 归档回归合成问题', 'ts_utc': run_ts,
                'git_head': 'synthetic',
                'degradation_policy': {}},
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
        'notes': [], 'run_ok': run_ok,
        'agent_judgment': {
            'attached': True, 'judgment_file': 'judgment.json',
            'validation': {'passed': True, 'violations': []},
            'run_ok_at_attach': True}}
    json.dump(report, open(os.path.join(rd, 'report.json'), 'w',
                           encoding='utf-8'), ensure_ascii=False)
    json.dump({'schema_version': aj.JUDGMENT_SCHEMA_VERSION,
               'agent_declaration': {'role': 'synthetic'},
               'l3': {'claims': []}, 'l4': {'scenarios': []}},
              open(os.path.join(rd, 'agent_judgment.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8').write(
        ro._render_md(report))
    return rd


def auto_stage(rd, engine_root, archive_dir=None, judgment=None):
    argv = [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'auto',
            '--report-dir', rd, '--engine-root', engine_root]
    if archive_dir:
        argv += ['--archive-dir', archive_dir]
    if judgment:
        argv += ['--judgment', judgment]
    return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                          timeout=180)


def write_verdict(root, rd, overall):
    run_ts = json.load(open(os.path.join(rd, 'report.json'),
                            encoding='utf-8'))['run']['ts_utc']
    d = os.path.join(root, 'audit', 'semantic_review', '20261116')
    os.makedirs(d, exist_ok=True)
    seq = len([f for f in os.listdir(d) if run_ts in f]) + 1
    doc = {'overall': overall, 'reviewer': 'SYNTH-SEAT', 'notes': '',
           'run_ts': run_ts, 'recorded_at': '2026-11-16T12:00:00Z',
           'content_sha256': aj.content_digest(rd)}
    p = os.path.join(d, 'VERDICT-%s-%02d.json' % (run_ts, seq))
    json.dump(doc, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    return p


print('═' * 64)
print('Audit-R2 条目6: auto 幂等续链+最终归档回归')
print('═' * 64)

tmp = tempfile.mkdtemp(prefix='r2chain_')
eroot = os.path.join(tmp, 'engine')
os.makedirs(os.path.join(eroot, 'config'), exist_ok=True)
shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
            os.path.join(eroot, 'config', 'metric_registry.json'))

# ── R+S+T: 恢复续链→跳挂→报告→归档(三处摘要核对) ──
rd1 = make_run(tmp, 'c1')
vp1 = write_verdict(eroot, rd1, 'VERIFIED')
arc1 = os.path.join(tmp, 'arc1')
r1 = auto_stage(rd1, eroot, archive_dir=arc1)
e1 = json.loads(r1.stdout)
chain1 = {c['stage']: c for c in e1['data']['chain']}
check('R1 恢复既有 run → plan(resumed) 不重新 plan',
      chain1['plan'].get('resumed') is True and r1.returncode == 0)
check('S1 已落位无新 judgment → attach(skipped) 不重挂',
      chain1['attach'].get('skipped') is True)
check('T1 report ok+deliverable → 归档段 ok',
      chain1['report'].get('deliverable') is True
      and chain1['archive'].get('ok') is True)
man = json.load(open(os.path.join(arc1, 'ARCHIVE_MANIFEST.json'),
                     encoding='utf-8'))
check('T2 归档摘要=run 目录摘要(三处一致之 run==archive)',
      man['content_sha256'] == aj.content_digest(rd1)
      == aj.content_digest(arc1))
check('T3 归档摘要=裁决锚(bound)',
      man['content_sha256'] == json.load(
          open(vp1, encoding='utf-8'))['content_sha256'])
check('T4 裁链随包+manifest 裁决面齐',
      os.path.isfile(os.path.join(arc1, 'verdicts',
                                  os.path.basename(vp1)))
      and man['verdict'] == 'VERIFIED' and man['verdicts_n'] == 1)
check('T5 交付件副本齐(report.json/report.md/FULL_REPORT/'
      'agent_judgment.json)',
      all(os.path.isfile(os.path.join(arc1, f)) for f in
          ('report.json', 'report.md', 'FULL_REPORT.md',
           'agent_judgment.json')))

# ── U: append-only(同目录再归=拒) ──
r2 = auto_stage(rd1, eroot, archive_dir=arc1)
e2 = json.loads(r2.stdout)
check('U1 归档目录已存在 → 拒(append-only,不覆盖)',
      r2.returncode == 1 and e2['data']['chain'][-1]['ok'] is False
      and e2['data']['chain'][-1].get('blocked') == 'archive_exists')

# ── T: 非 deliverable 拒归(审查缺席=席位暂停点) ──
rd3 = make_run(tmp, 'c3')          # 无裁决档
arc3 = os.path.join(tmp, 'arc3')
r3 = auto_stage(rd3, eroot, archive_dir=arc3)
e3 = json.loads(r3.stdout)
chain3 = {c['stage']: c for c in e3['data']['chain']}
check('T6 审查缺席 → review_pause+拒归+不产归档目录',
      r3.returncode == 1 and 'review_pause' in chain3
      and not os.path.exists(arc3))

# ── T: REVISE 裁决同样拒归(席位暂停点) ──
rd4 = make_run(tmp, 'c4')
write_verdict(eroot, rd4, 'REVISE')
arc4 = os.path.join(tmp, 'arc4')
r4 = auto_stage(rd4, eroot, archive_dir=arc4)
check('T7 verdict=REVISE → 拒归(归档对象=最终受审版本)',
      r4.returncode == 1 and not os.path.exists(arc4))

# ── T: 副本不一致拒归(改渲染视图) ──
rd5 = make_run(tmp, 'c5')
write_verdict(eroot, rd5, 'VERIFIED')
open(os.path.join(rd5, 'report.md'), 'a', encoding='utf-8').write('\n篡改\n')
arc5 = os.path.join(tmp, 'arc5')
r5 = auto_stage(rd5, eroot, archive_dir=arc5)
check('T8 多副本不一致 → 拒归(报告/裁决/归档同版门)',
      r5.returncode == 1 and not os.path.exists(arc5))

# ── R: 未落位 run 恢复 → Agent Native 暂停(仍不重 plan) ──
rd6 = make_run(tmp, 'c6', produced=False)
rd6rj = os.path.join(rd6, 'report.json')
rj6 = json.load(open(rd6rj, encoding='utf-8'))
rj6['layers']['L3_AI推断层']['produced'] = False
rj6['layers']['L4_条件情景层']['produced'] = False
rj6.pop('agent_judgment', None)
json.dump(rj6, open(rd6rj, 'w', encoding='utf-8'), ensure_ascii=False)
open(os.path.join(rd6, 'report.md'), 'w', encoding='utf-8').write(
    ro._render_md(rj6))
r6 = auto_stage(rd6, eroot)
e6 = json.loads(r6.stdout)
chain6 = {c['stage']: c for c in e6['data']['chain']}
check('R2 未落位恢复 → 不重 plan+Agent Native 暂停点(judgment 缺席)',
      chain6['plan'].get('resumed') is True and 'pause' in chain6
      and r6.returncode == 1)

print(f"\n判定: {PASS} PASS / {FAIL} FAIL")
sys.exit(0 if not FAIL else 1)
