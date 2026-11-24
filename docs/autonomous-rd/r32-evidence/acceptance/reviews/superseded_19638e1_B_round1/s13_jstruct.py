#!/usr/bin/python3 -I
"""只读: 打印判断档结构、agent_declaration、以及 MAP_REPORT/FULL_REPORT 中对质裁定渲染位置。用法: s13_jstruct.py <agent_judgment.json> <MAP_REPORT.md> <FULL_REPORT.md> <report.md>"""
import json, sys
aj = json.load(open(sys.argv[1], encoding='utf-8'))
print('top keys:', sorted(aj.keys()))
for k in aj:
    if k in ('l3_contradictions', 'l4_scenarios', 'reader_map', 'quality_gate_notes'):
        continue
    print('==', k, '=', json.dumps(aj[k], ensure_ascii=False)[:1500])
l3 = aj.get('l3_contradictions') or []
print('l3 n=', len(l3))
for c in l3:
    print('  ', c.get('id'), 'keys=', sorted(c.keys()))
    print('     evidence_refs=', json.dumps(c.get('evidence_refs'), ensure_ascii=False)[:400])
    print('     opposing=', json.dumps(c.get('opposing_evidence') or c.get('opposing'), ensure_ascii=False)[:400])
    for k in c:
        if k not in ('id', 'statement', 'competing_explanations', 'evidence_refs', 'keys'):
            print('     ', k, '=', json.dumps(c[k], ensure_ascii=False)[:300])
l4 = aj.get('l4_scenarios') or []
print('l4 n=', len(l4))
for s in l4:
    print('  ', json.dumps(s, ensure_ascii=False)[:1800])
rm = aj.get('reader_map') or {}
print('reader_map keys:', sorted(rm.keys()))
for k in rm:
    if k in ('transmission_links', 'headline_conclusion'):
        continue
    print('==', k, '=', json.dumps(rm[k], ensure_ascii=False)[:2600])
print('notes n=', len(aj.get('quality_gate_notes') or []))
for i, n in enumerate(aj.get('quality_gate_notes') or []):
    print('--- note', i, ':', n)
for p in sys.argv[2:]:
    txt = open(p, encoding='utf-8').read()
    lines = txt.split('\n')
    print('#####', p.split('/')[-1], 'lines=', len(lines), 'chars=', len(txt))
    for i, ln in enumerate(lines, 1):
        if any(w in ln for w in ('支持主解释', '尚不能区分', '支持竞争解释', '对质', '语义审查', '席位')):
            print('  L%d: %s' % (i, ln[:700]))
