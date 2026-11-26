#!/usr/bin/env python3
"""probe_opr_fix.py <engine_scripts_dir> <config_dir> <snapshot_path> <out_dir> <question_file>

Audit-R32 正式入口验收复现/修复探针(只读;输出只落 <out_dir>):
以给定引擎代码(research_map_planner / research_orchestrator)对一个迷你树
(config 副本+冻结快照副本)跑离线计划(S 步=替身信封,取数/证据口径/L1/索引
走真代码),再把**真计划点值格**喂给 official_policy_record_face——
复现「序列+惯例可推」回退在真管线是否生效。
"""
import json
import os
import shutil
import sys

scripts, config_dir, snap, out_dir, qfile = sys.argv[1:6]
sys.path.insert(0, scripts)
tree = os.path.join(out_dir, 'tree')
if os.path.isdir(tree):
    shutil.rmtree(tree)
shutil.copytree(config_dir, os.path.join(tree, 'config'))
os.makedirs(os.path.join(tree, 'data', 'daily'))
shutil.copy2(snap, os.path.join(tree, 'data', 'daily',
                                os.path.basename(snap)))
question = open(qfile, encoding='utf-8').read().rstrip('\n')

import research_map_planner as rmp      # noqa: E402
import research_orchestrator as ro      # noqa: E402


def _fake_step_ok(name, argv, timeout=180):
    return {'step': name, 'argv': list(argv), 'executed': True, 'ok': True,
            'exit_code': 0, 'semantic_ok': True, 'note': None,
            'duration_ms': 1, 'envelope': {'ok': True}}


ro.run_step = _fake_step_ok
rep = ro.run_research(question, root=tree, out_dir=os.path.join(out_dir, 'run'))
rp = rep.get('research_plan') or {}
pv = rp.get('point_values') or {}
pairs = {(eco, dim) for eco, rf in (rp.get('regions') or {}).items()
         for dim in ((rf.get('dimensions') or {}) or {})}
cal = os.path.join(tree, 'config', 'release_calendar.json')
face = rmp.official_policy_record_face(
    pv, pairs, rp.get('cutoff'), question=question, calendar_path=cal)
print('engine scripts:', scripts)
print('planner file  :', rmp.__file__)
print('question      :', question[:60])
print('cutoff        :', rp.get('cutoff'), '| planned pairs:', sorted(pairs))
for c in pv.get('cells') or []:
    if c.get('dimension') != 'policy':
        continue
    la = (c.get('anchors') or {}).get('最新一期') or {}
    pdd = la.get('policy_dates') or {}
    print('CELL %-2s %-18s latest.status=%s cell.policy_dates=%s '
          'anchor.policy_dates.decision=%s effective=%s' % (
              c.get('region'), c.get('metric_id'), la.get('status'),
              'present' if c.get('policy_dates') else 'absent',
              pdd.get('decision'), pdd.get('effective')))
print('required_regions:', face.get('required_regions'))
print('rows            :', [(r.get('region'), r.get('metric_id'),
                            r.get('official_target')) for r in face.get('rows') or []])
print('gaps            :', json.dumps(face.get('gaps'), ensure_ascii=False))
try:
    import agent_judgment as aj
    import inspect
    sig = inspect.signature(aj.blocked_class_of)
    print('blocked_class_of signature:', sig)
except Exception as e:                 # noqa: BLE001
    print('blocked_class_of import failed:', e)
