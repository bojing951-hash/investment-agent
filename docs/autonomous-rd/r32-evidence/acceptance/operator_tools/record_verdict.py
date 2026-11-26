#!/usr/bin/env python3
"""record_verdict.py <install_tree> <run_dir> <VERDICT-roundN.json> [<round label>]

Audit-R32 operator step: register one independent-seat verdict through the
engine's own recorder (agent_judgment.record_semantic_verdict: append-only,
bound to the run's content digest / frozen-input digest / map report digest).
The seat's verdict word, reviewer id, notes and findings are taken verbatim
from the seat's VERDICT file; nothing is edited on the way in.
"""
import hashlib
import json
import os
import sys

tree, run_dir, vpath = sys.argv[1:4]
round_label = sys.argv[4] if len(sys.argv) > 4 else os.path.basename(vpath)
sys.path.insert(0, os.path.join(tree, 'scripts'))
sys.path.insert(0, os.path.join(tree, 'scripts', 'research_contract'))
os.chdir(tree)
import agent_judgment as aj  # noqa: E402

raw = open(vpath, 'rb').read()
v = json.loads(raw.decode('utf-8'))
if v.get('verdict') not in ('UPHELD', 'REVISE') or v.get('overall') != v.get('verdict'):
    raise SystemExit('verdict/overall must both be UPHELD or REVISE: %r / %r'
                     % (v.get('verdict'), v.get('overall')))
if not v.get('reviewer') or not v.get('notes'):
    raise SystemExit('reviewer / notes missing in the seat verdict file')
extra = {
    'round_label': round_label,
    'verdict_file': os.path.basename(vpath),
    'verdict_file_sha256': hashlib.sha256(raw).hexdigest(),
    'recompute_points': v.get('recompute_points'),
    'recompute_mismatches': v.get('recompute_mismatches'),
    'items': v.get('items') or [],
    'must_fix': v.get('must_fix') or [],
    'counterexamples_sought': v.get('counterexamples_sought') or [],
}
if v.get('audited_at'):
    extra['seat_audited_at'] = v['audited_at']
path = aj.record_semantic_verdict(tree, run_dir, v['verdict'], reviewer=v['reviewer'],
                                  notes=v['notes'], extra=extra)
doc = json.load(open(path, encoding='utf-8'))
print('recorded', path)
print('  overall=%s revision=%s predecessor=%s content_sha256=%s frozen=%s'
      % (doc.get('overall'), doc.get('revision'), doc.get('predecessor'),
         str(doc.get('content_sha256'))[:16], str(doc.get('frozen_inputs_sha256'))[:16]))
print('  notes(%d chars): %s' % (len(doc.get('notes') or ''), (doc.get('notes') or '')[:160]))
