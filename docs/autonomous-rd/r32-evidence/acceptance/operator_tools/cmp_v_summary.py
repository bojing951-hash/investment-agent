#!/usr/bin/python3 -I
"""cmp_v_summary.py — condense out/cmp_V_<tag>.txt (cmp_runs.py output, stamp Y -> stamp V) into
out/cmp_V_summary.txt: per work order and per report.json section, the real leaf differences
split into (a) attached-judgment content (the L3 / L4 AI layers of report.json/layers — the Y run
carries the attached, reviewed judgment; the V re-plan is plan-only and carries none) and
(b) everything else (engine deterministic faces; expected: zero — the post-Y commits only
touched the report/archive/replay delivery stages)."""
import os
import re

OUT = '/tmp/r32-accept/out'
AI = ('/L3_AI', '/L4_')
lines = ['# cmp_V_summary — stamp Y 36499bb -> stamp V cf33de3a9942578b71cecb45077b7a505d8fca01, from cmp_V_<tag>.txt (cmp_runs.py)',
         '# "engine" = every section except the L3/L4 AI layers; "judgment" = report.json/layers leaves under the AI layers',
         '# (Y runs carry the attached, reviewed judgments; the V re-plan runs are plan-only)']
tot_engine = 0
for tag in ('A', 'B', 'T3', 'N30', 'C4', 'AUG'):
    p = os.path.join(OUT, 'cmp_V_%s.txt' % tag)
    if not os.path.exists(p):
        lines.append('== %s | (no comparison file)' % tag)
        continue
    src = open(p, encoding='utf-8').read()
    head = [l for l in src.splitlines() if l.startswith('# old run')]
    lines.append('== %s | %s' % (tag, head[0][2:] if head else '?'))
    section = None
    diffs = {}
    for l in src.splitlines():
        if l.startswith('## '):
            section = l[3:].split(' | ')[0]
        elif section and re.match(r'^     /\S', l):
            diffs.setdefault(section, []).append(l[5:])
    for section, paths in diffs.items():
        judg = [q for q in paths if any(x in q for x in AI)]
        eng = [q for q in paths if not any(x in q for x in AI)]
        tot_engine += len(eng)
        lines.append('   %-26s real diff %d = judgment %d + engine %d' % (section, len(paths), len(judg), len(eng)))
        for q in eng:
            lines.append('        engine: ' + q)
    if not diffs:
        lines.append('   no real difference in any section')
lines.append('engine-face leaf differences outside the AI layers, all work orders: %d' % tot_engine)
open(os.path.join(OUT, 'cmp_V_summary.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
