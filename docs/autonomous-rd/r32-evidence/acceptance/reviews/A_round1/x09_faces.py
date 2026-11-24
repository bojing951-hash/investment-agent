import json, sys, os
rep = sys.argv[1]; outdir = sys.argv[2]
d = json.load(open(rep, encoding='utf-8'))
def w(name, obj):
    with open(os.path.join(outdir, name), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
rp = d['research_plan']
print('research_plan keys:', list(rp.keys()))
w('mid_trio.json', rp['us_rates_trio'])
w('mid_asset_moves.json', rp['asset_moves'])
w('mid_turning.json', rp['turning_candidates'])
w('mid_clusters.json', rp['policy_event_clusters'])
w('mid_point_anchors.json', rp['point_anchors'])
w('mid_policy_doc_facts.json', rp.get('policy_doc_facts'))
w('mid_cv.json', d['agent_judgment'].get('contract_verification'))
w('mid_expost_offsets.json', rp.get('ex_post_offsets'))
aj = d['agent_judgment']
print('agent_judgment keys:', list(aj.keys()))
for k in aj:
    if k not in ('contract_verification',):
        s = json.dumps(aj[k], ensure_ascii=False)
        print(' ', k, len(s), s[:300])
for i, st in enumerate(d['steps']):
    env = st.get('envelope')
    if not isinstance(env, dict): continue
    name = st['step']
    w(f'mid_step_{i:02d}_{name}.json', env)
print('sizes:')
for fn in sorted(os.listdir(outdir)):
    if fn.startswith('mid_step_'):
        print(' ', fn, os.path.getsize(os.path.join(outdir, fn)))
