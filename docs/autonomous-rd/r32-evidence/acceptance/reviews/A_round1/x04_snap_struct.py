import json, sys
p = sys.argv[1]
d = json.load(open(p, encoding='utf-8'))
print('TOP KEYS:', list(d.keys()))
for k in d.keys():
    v = d[k]
    if isinstance(v, (dict, list)):
        print(f'== {k}: {type(v).__name__} len={len(v)}')
    else:
        print(f'== {k}: {v!r}')
print()
print('research_as_of =', json.dumps(d.get('research_as_of'), ensure_ascii=False)[:2000])
ss = d['series_store']
print('series_store type', type(ss).__name__, len(ss))
ks = list(ss.keys())
print('series keys (first 60):', ks[:60])
print('n keys', len(ks))
# examine one series
k0 = 'CPI'
s0 = ss[k0]
print('sample series', k0, type(s0).__name__)
if isinstance(s0, dict):
    for kk, vv in s0.items():
        if isinstance(vv, (dict, list)):
            print('   ', kk, type(vv).__name__, len(vv))
        else:
            print('   ', kk, '=', repr(vv)[:300])
