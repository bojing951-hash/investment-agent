#!/usr/bin/python3 -I
"""frozen_inputs_xy.py <old_env.sh> <new_env.sh> — byte comparison of the frozen inputs of every
work order between two stamps (old and new run directories named by RD_* exports in the two env
files).  Compared per work order: root_overlay/config/release_calendar.json,
root_overlay/config/metric_registry.json, the root_overlay snapshot file(s), the verbatim work-order
question (report.json run.question; the run dir's question_verbatim.txt is a product of the engine's
report stage, listed for information only and not counted), evidence_index.json, views_digest.json;
CODE_VERSION.json of the two install trees.  Read-only."""
import glob
import hashlib
import json
import os
import re
import sys


def load_env(p):
    env = {}
    for line in open(p, encoding='utf-8'):
        line = line.strip()
        if line.startswith('export RD_'):
            k, v = line[len('export '):].split('=', 1)
            env[k] = v.strip('"')
    return env


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def tree_of(rd):
    m = re.match(r'(/tmp/r32-accept/final\d+[a-z0-9-]*)/', rd)
    return m.group(1)


old, new = load_env(sys.argv[1]), load_env(sys.argv[2])
assert set(old) == set(new), (sorted(old), sorted(new))
n_diff = 0
for k in sorted(old):
    ro, rn = old[k], new[k]
    to, tn = tree_of(ro), tree_of(rn)
    print('== %s' % k[3:])
    for rel in ('root_overlay/config/release_calendar.json', 'root_overlay/config/metric_registry.json',
                'evidence_index.json', 'views_digest.json'):
        po, pn = os.path.join(ro, rel), os.path.join(rn, rel)
        if not (os.path.exists(po) and os.path.exists(pn)):
            print('  %-44s old=%s new=%s MISSING' % (rel, os.path.exists(po), os.path.exists(pn)))
            n_diff += 1
            continue
        a, b = sha16(po), sha16(pn)
        n_diff += a != b
        print('  %-44s %s %s %s' % (rel, a, b, 'same' if a == b else 'DIFFERENT'))
    # verbatim work-order question, from the plan-stage product (report.json) on both sides
    qo = json.load(open(os.path.join(ro, 'report.json'), encoding='utf-8'))['run']['question']
    qn = json.load(open(os.path.join(rn, 'report.json'), encoding='utf-8'))['run']['question']
    a, b = hashlib.sha256(qo.encode('utf-8')).hexdigest()[:16], hashlib.sha256(qn.encode('utf-8')).hexdigest()[:16]
    n_diff += a != b
    print('  %-44s %s %s %s%s' % ('run.question (report.json)', a, b, 'same' if a == b else 'DIFFERENT',
                                 '' if qo == qn else ' | DIFFERENT TEXT'))
    for rel in ('question_verbatim.txt', 'MAP_REPORT.md', 'FULL_REPORT.md'):
        print('  [report-stage product, not counted]  %-24s old=%s new=%s' % (rel, os.path.exists(os.path.join(ro, rel)), os.path.exists(os.path.join(rn, rel))))
    so = sorted(os.path.basename(x) for x in glob.glob(os.path.join(ro, 'root_overlay/data/daily/research_snapshot_*.json')))
    sn = sorted(os.path.basename(x) for x in glob.glob(os.path.join(rn, 'root_overlay/data/daily/research_snapshot_*.json')))
    assert len(so) == 1 and len(sn) == 1, (so, sn)
    po, pn = [os.path.join(r, 'root_overlay/data/daily', s[0]) for r, s in ((ro, so), (rn, sn))]
    a, b = sha16(po), sha16(pn)
    n_diff += (a != b) or (so != sn)
    print('  %-44s %s %s %s%s' % (so[0], a, b, 'same' if a == b else 'DIFFERENT', '' if so == sn else ' | old name: %s' % so))
    co = json.load(open(os.path.join(to, 'CODE_VERSION.json'), encoding='utf-8'))['git_head']
    cn = json.load(open(os.path.join(tn, 'CODE_VERSION.json'), encoding='utf-8'))['git_head']
    print('  CODE_VERSION old: %s new: %s' % (co[:12], cn[:12]))
print('frozen-input files differing: %d' % n_diff)
