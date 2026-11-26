#!/usr/bin/python3 -I
"""cmp_attached.py — read-only: the judgment attached in each X run directory must be
JSON-equal to the folded builder judgment it was attached from (scratch_x/judgment5_<tag>.json).
Prints sha256 of both files and the JSON-equality; writes /tmp/r32-accept/out/cmp_attached_X.txt."""
import hashlib
import json
import os

env = {}
for line in open('/tmp/r32-accept/env5.sh', encoding='utf-8'):
    line = line.strip()
    if line.startswith('export RD_'):
        k, v = line[len('export '):].split('=', 1)
        env[k] = v.strip('"')
lines = []
for tag in ('A', 'B', 'T3', 'N30', 'C4'):
    src = '/tmp/r32-accept/scratch_x/judgment5_%s.json' % tag
    dst = os.path.join(env['RD_' + tag], 'agent_judgment.json')
    a, b = open(src, 'rb').read(), open(dst, 'rb').read()
    ja, jb = json.loads(a), json.loads(b)
    extra = sorted(set(jb) - set(ja))
    missing = sorted(set(ja) - set(jb))
    same_core = all(ja[k] == jb.get(k) for k in ja)
    lines.append('%s | run %s' % (tag, os.path.basename(env['RD_' + tag])[:16]))
    lines.append('   folded   %6d bytes sha256 %s' % (len(a), hashlib.sha256(a).hexdigest()))
    lines.append('   attached %6d bytes sha256 %s' % (len(b), hashlib.sha256(b).hexdigest()))
    lines.append('   json-equal %s | folded keys all equal in attached %s | keys only in attached %s | keys only in folded %s'
                 % (ja == jb, same_core, extra, missing))
    if extra:
        lines.append('   attached-only content: ' + json.dumps({k: jb[k] for k in extra}, ensure_ascii=False)[:700])
text = '\n'.join(lines) + '\n'
open('/tmp/r32-accept/out/cmp_attached_X.txt', 'w', encoding='utf-8').write(text)
print(text)
