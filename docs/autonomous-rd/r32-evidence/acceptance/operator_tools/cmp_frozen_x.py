#!/usr/bin/python3 -I
"""cmp_frozen_x.py — read-only: byte identity of the frozen inputs of each X work order's run
directory against the same work order's run directory at the stamp of its last independent
review (A: 19638e1 in final3; B/T3/N30/C4: 0f3936d in final4 / final4-degraded).
Compared: root_overlay/config/release_calendar.json, root_overlay/config/metric_registry.json,
root_overlay/data/daily/research_snapshot_*.json, evidence_index.json, views_digest.json and
the run question. Writes /tmp/r32-accept/out/cmp_X_frozen.txt."""
import glob
import hashlib
import json
import os

PAIRS = [('A', '/tmp/r32-accept/final3', '20261123T145753Z', 'final5', '20261123T213303Z'),
         ('B', '/tmp/r32-accept/final4', '20261123T193157Z', 'final5', '20261123T213320Z'),
         ('T3', '/tmp/r32-accept/final4', '20261123T193215Z', 'final5', '20261123T213336Z'),
         ('N30', '/tmp/r32-accept/final4', '20261123T193232Z', 'final5', '20261123T213353Z'),
         ('C4', '/tmp/r32-accept/final4-degraded', '20261123T193254Z', 'final5-degraded', '20261123T213414Z')]


def one(root, ts):
    hits = glob.glob(os.path.join('/tmp/r32-accept', root, 'output', 'research_runs', ts + '_*'))
    assert len(hits) == 1, (root, ts, hits)
    return hits[0]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def files(rd):
    out = {}
    for p in sorted(glob.glob(os.path.join(rd, 'root_overlay', '**', '*'), recursive=True)):
        if os.path.isfile(p):
            out[os.path.relpath(p, rd)] = sha(p)
    for n in ('evidence_index.json', 'views_digest.json'):
        out[n] = sha(os.path.join(rd, n))
    return out


lines = []
for tag, oroot, ots, nroot, nts in PAIRS:
    o, n = one(oroot, ots), one(nroot, nts)
    fo, fn = files(o), files(n)
    same = [k for k in fo if k in fn and fo[k] == fn[k]]
    diff = [k for k in fo if k in fn and fo[k] != fn[k]]
    oo = [k for k in fo if k not in fn]
    nn = [k for k in fn if k not in fo]
    ro = json.load(open(os.path.join(o, 'report.json'), encoding='utf-8'))
    rn = json.load(open(os.path.join(n, 'report.json'), encoding='utf-8'))
    qo, qn = ro['run'].get('question'), rn['run'].get('question')
    so, sn = ro['research_plan'].get('cutoff'), rn['research_plan'].get('cutoff')
    lines.append('===== %s | old %s %s | new %s %s' % (tag, oroot, os.path.basename(n and o)[:20], nroot, os.path.basename(n)[:20]))
    lines.append('   git_head old %s | new %s' % (ro['run'].get('git_head'), rn['run'].get('git_head')))
    lines.append('   question identical %s | cutoff old %s new %s' % (qo == qn, so, sn))
    lines.append('   frozen files: identical %d | differing %d | only-old %d | only-new %d' % (len(same), len(diff), len(oo), len(nn)))
    for k in same:
        lines.append('      same  %s  %s' % (k, fo[k][:16]))
    for k in diff:
        lines.append('      DIFF  %s  old %s new %s' % (k, fo[k][:16], fn[k][:16]))
    for k in oo:
        lines.append('      only-old %s' % k)
    for k in nn:
        lines.append('      only-new %s' % k)
    for k in ('evidence_index.json', 'views_digest.json'):
        jo = json.load(open(os.path.join(o, k), encoding='utf-8'))
        jn = json.load(open(os.path.join(n, k), encoding='utf-8'))
        lines.append('   %s json-equal %s (old %s bytes / new %s bytes)' % (k, jo == jn, os.path.getsize(os.path.join(o, k)), os.path.getsize(os.path.join(n, k))))
text = '\n'.join(lines) + '\n'
open('/tmp/r32-accept/out/cmp_X_frozen.txt', 'w', encoding='utf-8').write(text)
print(text)
