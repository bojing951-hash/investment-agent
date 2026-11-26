#!/usr/bin/python3 -I
"""只读: 紧凑抽取 report.json 引擎面(供席位复算对照)。用法: s12_faces.py <report.json> <outdir>"""
import json, sys, os

rep = json.load(open(sys.argv[1], encoding='utf-8'))
out = sys.argv[2]
os.makedirs(out, exist_ok=True)

def dump(name, obj):
    with open(os.path.join(out, 'face_%s.json' % name), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)

rp = rep.get('research_plan', {})
print('research_plan keys:', sorted(rp.keys()))
dump('point_values', rp.get('point_values'))
dump('point_anchors', rp.get('point_anchors'))
dump('turning_candidates', rp.get('turning_candidates'))
dump('us_rates_trio', rp.get('us_rates_trio'))
dump('asset_moves', rp.get('asset_moves'))
dump('policy_doc_facts', rp.get('policy_doc_facts'))
dump('dimension_gaps', rp.get('dimension_gaps'))
dump('ex_post_offsets', rp.get('ex_post_offsets'))
dump('policy_event_clusters', rp.get('policy_event_clusters'))
dump('regions', rp.get('regions'))
for k in ('cutoff', 'map_question'):
    print(k, '=', json.dumps(rp.get(k), ensure_ascii=False)[:600])

aj = rep.get('agent_judgment', {})
print('agent_judgment keys:', sorted(aj.keys()))
for k in aj:
    if k != 'contract_verification':
        v = aj[k]
        s = json.dumps(v, ensure_ascii=False)
        print('  ', k, '=', s[:300])

steps = rep.get('steps', [])
print('steps n=', len(steps))
for i, st in enumerate(steps):
    env = st.get('envelope') if isinstance(st, dict) else None
    name = st.get('name') or st.get('step') or st.get('id') if isinstance(st, dict) else None
    keys = sorted(env.keys()) if isinstance(env, dict) else type(env).__name__
    print(i, name, (st.get('status') if isinstance(st, dict) else None), keys if isinstance(keys, list) else keys)
    if isinstance(env, dict):
        dump('step%02d' % i, env)

run = rep.get('run', {})
print('run keys:', sorted(run.keys()))
