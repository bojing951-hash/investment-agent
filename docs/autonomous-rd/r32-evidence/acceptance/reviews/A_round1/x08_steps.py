import json, sys
p = sys.argv[1]
d = json.load(open(p, encoding='utf-8'))
print('== run')
for k, v in d['run'].items():
    if k in ('question',): continue
    s = json.dumps(v, ensure_ascii=False)
    print(f'  {k}: {s[:700]}')
print('== steps')
for i, st in enumerate(d['steps']):
    keys = list(st.keys())
    name = st.get('step') or st.get('name') or st.get('id')
    env = st.get('envelope')
    ek = list(env.keys()) if isinstance(env, dict) else type(env).__name__
    print(i, name, '| keys:', keys, '| env keys:', ek)
print('== layers')
for lk, lv in d['layers'].items():
    print(lk, list(lv.keys()) if isinstance(lv, dict) else lv)
print('== L1 rows count', len(d['layers']['L1_事实层']['rows']))
print(json.dumps(d['layers']['L1_事实层']['rows'][0], ensure_ascii=False)[:800])
print('== notes', d['notes'])
