#!/usr/bin/python3 -I
"""只读: report.json run 面摘要(交付门/数据需求)。用法: s16_run_keys.py <report.json>"""
import json, sys
rep = json.load(open(sys.argv[1], encoding='utf-8'))
run = rep.get('run', {})
print('run keys:', sorted(run.keys()))
for k in run:
    if k == 'data_requirements':
        continue
    v = run[k]
    s = json.dumps(v, ensure_ascii=False)
    print('==', k, '=', s[:700] + (' …[len %d]' % len(s) if len(s) > 700 else ''))
dr = run.get('data_requirements')
print('data_requirements type', type(dr).__name__, (sorted(dr.keys()) if isinstance(dr, dict) else len(dr)))
if isinstance(dr, dict):
    for k, v in dr.items():
        s = json.dumps(v, ensure_ascii=False)
        print('  --', k, '=', s[:600])
