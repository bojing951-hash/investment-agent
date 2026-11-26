#!/usr/bin/python3 -I
"""rsum.py <replay_output.json> <stderr_file> — read-only summary of one ia_cli replay envelope."""
import json
import os
import sys

try:
    d = json.load(open(sys.argv[1], encoding='utf-8'))
except Exception as exc:  # noqa: BLE001
    print('envelope unreadable: %r' % (exc,))
    if os.path.isfile(sys.argv[2]):
        tail = open(sys.argv[2], encoding='utf-8', errors='replace').read().splitlines()[-4:]
        print('stderr tail:', ' | '.join(tail)[:600])
    sys.exit(3)
dd = d.get('data') or {}
print('ok=', d.get('ok'), '| blocked=', dd.get('blocked'), '| render_mode=', dd.get('render_mode'),
      '| failed=', dd.get('failed_checks'))
print('checks:', {c.get('check'): c.get('ok') for c in (dd.get('checks') or [])})
for c in (dd.get('checks') or []):
    if c.get('ok') is False:
        print('   FAILED', c.get('check'), '|', str(c.get('detail'))[:300])
note = dd.get('note') or d.get('error') or d.get('errors') or ''
print('note:', str(note)[:300])
