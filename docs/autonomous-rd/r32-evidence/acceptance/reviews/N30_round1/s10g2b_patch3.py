import sys
p = sys.argv[1]
L = open(p, encoding='utf-8').read().split(chr(10))
i0 = [i for i, l in enumerate(L) if l.startswith('refs = set()')]
i1 = [i for i, l in enumerate(L) if l.startswith("tk('共 21 条")]
assert len(i0) == 1 and len(i1) == 1 and i1[0] > i0[0], (i0, i1)
new = [
"refs = set(); nref = 0; n4 = 0; ref4 = set()",
"for p, s in c.leaves:",
"    if 'evidence_refs' in p:",
"        for m in pat.finditer(s):",
"            if p.startswith('l3.'):",
"                nref += 1; refs.add(m.group(0))",
"            else:",
"                n4 += 1; ref4.add(m.group(0))",
"eik = {str(x['ref']): x.get('kind') for x in c.rep['evidence_index']}",
"c.diag.append('AJ l3 evidence_refs entries=' + str(nref) + ' distinct=' + str(len(refs)) + ' | other entries=' + str(n4) + ' distinct=' + str(len(ref4)))",
"c.ok('G', 'l4.scenarios asset_direction evidence_refs 亦全部解析到 evidence_index(kind=snapshot_fact)', all(eik.get(r) == 'snapshot_fact' for r in ref4), sorted(ref4))",
]
L[i1[0]:i1[0] + 1] = [
"tk('共 21 条 snapshot_fact 引用', '21', 21, nref if nref and all(eik.get(r) == 'snapshot_fact' for r in refs) else -1, 'l3(三条矛盾陈述+机制链四环) evidence_refs 条目数且全部在 evidence_index(kind=snapshot_fact)', tol=T)",
]
L[i0[0]:i0[0] + 1] = new
s = chr(10).join(L)
a = "pjc = find(sys.argv[8]); ptc = find(sys.argv[7] if False else 'text_consistency.py')"
assert s.count(a) == 1, 'paths'
s = s.replace(a, "pjc = find(sys.argv[7]); ptc = find(sys.argv[8])")
open(p, 'w', encoding='utf-8').write(s)
print('g2b patched3')
