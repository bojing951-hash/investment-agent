#!/usr/bin/env python3
"""run_sec_j.py <worktree> [--tolerant]

Operator harness: run only gate section §J of tests/test_audit_r32_gate.py
from a worktree (read-only for the repo; the gate's own temp trees are used).
--tolerant: reproduction on unmodified code — drop the not-yet-existing
`carry_start` keyword before calling _policy_window_path so the checks fail
with ❌ marks instead of a TypeError."""
import importlib.util
import os
import shutil
import sys

wt = sys.argv[1]
tolerant = '--tolerant' in sys.argv[2:]
os.chdir(wt)
spec = importlib.util.spec_from_file_location(
    'g32', os.path.join(wt, 'tests', 'test_audit_r32_gate.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
if tolerant:
    _orig = m.rmp._policy_window_path

    def _patched(*a, **k):
        k.pop('carry_start', None)
        return _orig(*a, **k)
    m.rmp._policy_window_path = _patched
try:
    m.sec_j()
finally:
    print('=== §J (%s): %d/%d ===' % (
        'repro on unmodified code' if tolerant else 'HEAD ' + m.WORKTREE_HEAD[:12],
        sum(m.RESULTS), len(m.RESULTS)))
    shutil.rmtree(m.TMPG, ignore_errors=True)
