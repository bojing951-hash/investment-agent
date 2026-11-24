import json, sys, re
rep = sys.argv[1]
pats = sys.argv[2:]
d = json.load(open(rep, encoding='utf-8'))
def walk(o, path):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, path + [str(k)])
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, path + [str(i)])
    else:
        yield path, o
hits = {p: [] for p in pats}
for path, v in walk(d, []):
    s = repr(v) if not isinstance(v, str) else v
    for p in pats:
        if re.search(p, s):
            hits[p].append(('/'.join(path[:8]), s[:160]))
for p in pats:
    print('==', p, len(hits[p]))
    for h in hits[p][:12]:
        print('   ', h[0], '|', h[1])
