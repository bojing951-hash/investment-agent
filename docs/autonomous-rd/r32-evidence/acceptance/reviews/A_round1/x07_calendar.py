import json, sys
p = sys.argv[1]
d = json.load(open(p, encoding='utf-8'))
print('TOP:', list(d.keys()) if isinstance(d, dict) else type(d))
for k, v in d.items():
    if isinstance(v, (dict, list)):
        print(f'== {k}: {type(v).__name__} len={len(v)}')
    else:
        print(f'== {k}: {v!r}')
# find entries list
def walk(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                print('LIST at', path + '/' + k, 'len', len(v), 'item keys', list(v[0].keys()))
            elif isinstance(v, dict):
                walk(v, path + '/' + k)
walk(d)
