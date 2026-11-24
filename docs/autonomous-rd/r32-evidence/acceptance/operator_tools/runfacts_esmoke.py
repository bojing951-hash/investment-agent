#!/usr/bin/python3 -I
"""runfacts_esmoke.py <receipt prefix, e.g. ESMOKE-W>

Runs scripts/runfacts.py over the run directories named by the newest plan
receipts with the given prefix (out/<prefix><tag>_plan_*.json) and prints the
facts. Read-only (reads receipts and run directories; writes nothing)."""
import glob
import json
import os
import re
import subprocess
import sys

prefix = sys.argv[1]
files = sorted(f for f in glob.glob('/tmp/r32-accept/out/%s*_plan_*.json' % prefix)
               if re.search(r'%s[A-Z0-9]*_plan_\d{8}T\d{6}Z\.json$' % re.escape(prefix), os.path.basename(f)))
dirs = []
for f in files:
    d = json.load(open(f, encoding='utf-8'))
    rd = (d.get('data') or {}).get('report_dir')
    if rd and os.path.isfile(os.path.join(rd, 'report.json')):
        dirs.append(rd)
    else:
        print('!! no report dir for', os.path.basename(f), file=sys.stderr)
r = subprocess.run(['/usr/bin/python3', '-I', '/tmp/r32-accept/scripts/runfacts.py'] + dirs,
                   capture_output=True, text=True)
sys.stdout.write(r.stdout)
sys.stderr.write(r.stderr)
sys.exit(r.returncode)
