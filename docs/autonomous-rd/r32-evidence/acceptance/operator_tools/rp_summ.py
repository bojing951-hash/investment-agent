#!/usr/bin/python3 -I
"""rp_summ.py <receipt.json> — one-line summary of a replay receipt (+ failing checks
and the three key checks).  Read-only."""
import json
import sys

r = json.load(open(sys.argv[1], encoding='utf-8'))
d = r.get('data', r) if isinstance(r, dict) else {}
checks = [c for c in (d.get('checks') or []) if isinstance(c, dict)]
n_ok = sum(1 for c in checks if c.get('ok'))
print('ok=%s | rc-level blocked=%s | render_mode=%s | failed=%s | checks ok %d/%d'
      % (r.get('ok'), d.get('blocked'), d.get('render_mode'), d.get('failed'), n_ok, len(checks)))
for c in checks:
    if (not c.get('ok')) or c.get('check') in ('verdict_binding_threeway', 'code_version_match',
                                               'deterministic_rerender', 'map_fullfile_anchor'):
        print('   [%s] %s | %s' % ('ok' if c.get('ok') else 'XX', c.get('check'),
                                   str(c.get('detail', ''))[:170]))
for w in (r.get('warnings') or [])[:5]:
    print('   warning: %s' % str(w)[:200])
