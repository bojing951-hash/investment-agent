#!/usr/bin/python3 -I
"""wrun.py <tree> <y_run_dir> — print the run directory under <tree>/output/research_runs that re-plans the
same question stem as <y_run_dir> (newest by run timestamp; never the byte-identical carried copy itself).
Exit 3 with a message when there is none."""
import os
import sys

tree, y = sys.argv[1:3]
base = os.path.basename(y.rstrip('/'))
root = os.path.join(tree, 'output', 'research_runs')
c = sorted(n for n in os.listdir(root) if n[16:] == base[16:] and n[:16] != base[:16])
if not c:
    sys.exit('no re-plan run in %s for %s' % (tree, base[16:56]))
print(os.path.join(root, c[-1]))
