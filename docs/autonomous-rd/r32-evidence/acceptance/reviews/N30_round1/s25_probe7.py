# s25_probe7.py <all_json>
import sys, json, collections
a = json.load(open(sys.argv[1], encoding='utf-8'))
print('top keys', sorted(a.keys()))
pts = a['points']
print('point keys', sorted(pts[0].keys()))
c = collections.Counter(p['sec'] for p in pts)
for s, n in c.items():
    nm = sum(1 for p in pts if p['sec'] == s and not p['ok'])
    nt = sum(1 for p in pts if p['sec'] == s and p['tok'])
    print('SEC', s, 'n', n, 'mismatch', nm, 'with_tok', nt)
    ex = [p for p in pts if p['sec'] == s][:2]
    for p in ex:
        print('    src=', str(p['src'])[:150], '| comp=', str(p['comp'])[:60], '| rep=', str(p['rep'])[:50], '| note=', str(p['note'])[:70])
for k in a.keys():
    if k != 'points': print(k, '=', json.dumps(a[k], ensure_ascii=False)[:500])
