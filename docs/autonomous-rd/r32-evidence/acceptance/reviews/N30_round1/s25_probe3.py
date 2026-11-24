# s25_probe3.py <snap> <reg> <aj> <all_json> <report>
import sys, json, re
snap = json.load(open(sys.argv[1], encoding='utf-8')); reg = json.load(open(sys.argv[2], encoding='utf-8')); aj = json.load(open(sys.argv[3], encoding='utf-8'))
allp = json.load(open(sys.argv[4], encoding='utf-8')); rep = json.load(open(sys.argv[5], encoding='utf-8'))
S = snap['series_store']
def mm(m):
    v = S[m]['values']; i = max(range(len(v)), key=lambda k: (v[k] is not None, v[k] if v[k] is not None else -1e9))
    j = min(range(len(v)), key=lambda k: (v[k] is not None, -(v[k] if v[k] is not None else 1e9)))
    return (S[m]['dates'][i], v[i], S[m]['dates'][j], v[j])
print('JP max/min', mm('JP_CPI_YOY')); print('EA max/min', mm('EA_HICP_YOY'))
print('JP 2023:', [(d[:7], v) for d, v in zip(S['JP_CPI_YOY']['dates'], S['JP_CPI_YOY']['values']) if d[:4] == '2023'][:4])
rl = reg.get('metrics') if isinstance(reg, dict) else reg
for m in ('JP_CPI_YOY', 'JP_CPI_TOKYO_YOY', 'EA_HICP_YOY'):
    r = [x for x in rl if x.get('metric_id') == m][0]
    print(m, 'keys', sorted(r.keys()))
    for k in ('calc', 'freshness', 'release_semantics', 'basis', 'definition'):
        if k in r: print('   ', k, '=', json.dumps(r[k], ensure_ascii=False)[:520])
ga = snap.get('gate_a', {})
print('gate_a keys', sorted(ga.keys())[:20])
nm = ga.get('noncore_missing')
print('noncore_missing type', type(nm).__name__, json.dumps(nm, ensure_ascii=False)[:900])
nd = ga.get('noncore_degraded')
print('noncore_degraded', json.dumps(nd, ensure_ascii=False)[:500])
pts = allp['points']
anch = [p for p in pts if p['tok']]
print('points total', len(pts), '| text-anchored(tok)', len(anch), '| no-tok', len(pts) - len(anch), '| MAP', sum(1 for p in pts if p['sec'] == 'MAP'))
okc = [p for p in pts if p['tok'] and p['where'].startswith(('l3', 'l4', 'reader_map', 'quality_gate_notes'))]
print('text-anchored in judgment body', len(okc), 'distinct tokens(leaf,start)', len(set((p['where'], p['tok']) for p in okc)))
import collections
print('leaves with anchored points', len(set(p['where'] for p in okc)))
print('top-level keys snap', sorted(snap.keys())[:30])
