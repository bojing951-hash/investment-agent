#!/usr/bin/python3 -I
"""cmp_attached_v.py — read-only: the judgment attached in each final-stamp (V) tree run directory
(byte-identical carry of the execution-stamp Y run directory) must equal (1) the Y run directory's
agent_judgment.json byte for byte and (2) the folded builder judgment it was attached from at Y
(JSON-equal on the folded keys). Prints sha256 of the files and the equalities; writes
/tmp/r32-accept/out/cmp_attached_V.txt. Work orders whose tag env has no RDV_ entry are skipped."""
import hashlib
import json
import os
import sys

FOLDED = {'A': 'judgment6_A.json', 'T3': 'judgment6_T3.json', 'C4': 'judgment6_C4.json',
          'N30': 'judgment6_N30.json', 'B': 'judgment7_B.json'}
env = {}
for line in open('/tmp/r32-accept/env9.sh', encoding='utf-8'):
    line = line.strip()
    if line.startswith('export RD'):
        k, v = line[len('export '):].split('=', 1)
        env[k] = v.strip('"')
tags = sys.argv[1:] or ['A', 'T3', 'C4', 'N30', 'B']
lines = []
for tag in tags:
    w, y = env.get('RDV_' + tag), env.get('RDY_' + tag)
    pj = os.path.join(w, 'agent_judgment.json')
    if not (w and y and os.path.exists(pj) and os.path.exists(os.path.join(y, 'agent_judgment.json'))):
        lines.append('%s | skipped (no attached judgment in the V tree run directory yet)' % tag)
        continue
    bw = open(pj, 'rb').read()
    by = open(os.path.join(y, 'agent_judgment.json'), 'rb').read()
    fp = '/tmp/r32-accept/scratch_x/%s' % FOLDED[tag]
    lines.append('%s | V tree run %s' % (tag, os.path.basename(w)[:16]))
    lines.append('   V tree attached  %6d bytes sha256 %s' % (len(bw), hashlib.sha256(bw).hexdigest()))
    lines.append('   Y tree attached  %6d bytes sha256 %s | byte-equal to V tree: %s'
                 % (len(by), hashlib.sha256(by).hexdigest(), bw == by))
    if os.path.exists(fp):
        bf = open(fp, 'rb').read()
        jf, jw = json.loads(bf), json.loads(bw)
        lines.append('   folded %s %6d bytes sha256 %s' % (FOLDED[tag], len(bf), hashlib.sha256(bf).hexdigest()))
        lines.append('   folded keys all equal in attached: %s | attached-only keys %s | folded-only keys %s'
                     % (all(jf[k] == jw.get(k) for k in jf), sorted(set(jw) - set(jf)), sorted(set(jf) - set(jw))))
    else:
        lines.append('   folded file missing: %s' % fp)
text = '\n'.join(lines) + '\n'
open('/tmp/r32-accept/out/cmp_attached_V.txt', 'w', encoding='utf-8').write(text)
print(text)
