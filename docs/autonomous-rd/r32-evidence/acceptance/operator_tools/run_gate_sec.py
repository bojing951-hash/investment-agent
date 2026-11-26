#!/usr/bin/env python3
"""run_gate_sec.py <worktree> <module> <section>[,<section>...]

Run selected sections of one gate-test module outside the repo battery
(output stays outside the repo)."""
import os
import shutil
import sys

wt, mod, secs = sys.argv[1:4]
sys.path.insert(0, os.path.join(wt, 'tests'))
_m = __import__(mod)
for sec in secs.split(','):
    getattr(_m, sec)()
n_ok = sum(1 for x in _m.RESULTS if x)
print('=== %s %s: %d/%d ===' % (mod, secs, n_ok, len(_m.RESULTS)))
shutil.rmtree(_m.TMPG, ignore_errors=True)
sys.exit(0 if all(_m.RESULTS) else 1)
