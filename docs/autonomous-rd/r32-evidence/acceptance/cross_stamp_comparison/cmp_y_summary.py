#!/usr/bin/python3 -I
"""cmp_y_summary.py — condense out/cmp_Y_<tag>.txt (cmp_runs.py output, stamp X -> stamp Y) into
out/cmp_Y_summary.txt: per work order and per report.json section, the real leaf differences
split into (a) attached-judgment content (the L3 / L4 AI layers of report.json/layers — these are the
builder revisions, not engine output) and (b) everything else (engine deterministic faces)."""
import re
import os

OUT = '/tmp/r32-accept/out'
AI = ('/L3_AI', '/L4_')
lines = ['# cmp_Y_summary — stamp X 8f9055d -> stamp Y 36499bb, from cmp_Y_<tag>.txt (cmp_runs.py)',
         '# "engine" = every section except the L3/L4 AI layers; "judgment" = report.json/layers leaves under the AI layers',
         '# (differences there are the attached, revised judgments; N30 at Y carries no attached judgment yet)']
tot_engine = 0
for tag in ('A', 'B', 'T3', 'N30', 'C4', 'AUG'):
    src = open(os.path.join(OUT, 'cmp_Y_%s.txt' % tag), encoding='utf-8').read()
    head = [l for l in src.splitlines() if l.startswith('# old run')][0]
    lines.append('== %s | %s' % (tag, head[2:]))
    section = None
    diffs = {}
    for l in src.splitlines():
        if l.startswith('## '):
            section = l[3:].split(' | ')[0]
        elif section and re.match(r'^     /\S', l):
            diffs.setdefault(section, []).append(l[5:])
    for section, paths in diffs.items():
        judg = [p for p in paths if any(x in p for x in AI)]
        eng = [p for p in paths if not any(x in p for x in AI)]
        tot_engine += len(eng)
        lines.append('   %-26s real diff %d = judgment %d + engine %d' % (section, len(paths), len(judg), len(eng)))
        for p in eng:
            lines.append('        engine: ' + p)
    if not diffs:
        lines.append('   no real difference in any section')
lines.append('engine-face leaf differences outside the AI layers, all work orders: %d' % tot_engine)
open(os.path.join(OUT, 'cmp_Y_summary.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
