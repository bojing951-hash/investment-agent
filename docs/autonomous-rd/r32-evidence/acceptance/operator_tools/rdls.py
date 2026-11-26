#!/usr/bin/python3 -I
"""rdls.py <tag> [<tag> ...] — read-only: basename + top-level listing of run directories named in env5.sh."""
import os
import sys

env = {}
for line in open('/tmp/r32-accept/env5.sh', encoding='utf-8'):
    line = line.strip()
    if line.startswith('export RD_'):
        k, v = line[len('export '):].split('=', 1)
        env[k] = v.strip('"')
for tag in sys.argv[1:]:
    rd = env['RD_' + tag]
    print('== %s: %s' % (tag, os.path.basename(rd)))
    for name in sorted(os.listdir(rd)):
        p = os.path.join(rd, name)
        print('   %s%s' % (name, '/' if os.path.isdir(p) else ''))
