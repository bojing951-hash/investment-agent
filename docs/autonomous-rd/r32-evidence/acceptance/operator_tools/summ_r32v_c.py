#!/usr/bin/python3 -I
"""summ_r32v_c.py <console.log> [<console.log> ...] — compact factual summary of re-download replay consoles
(redl_r32v.sh / redl_r31.sh). Reads only the lines the console scripts print; computes nothing else."""
import re
import sys


def checks(line):
    # "checks: {'a': True, ...}" -> (n_true, names not True)
    body = line.split('checks: ', 1)[1]
    items = re.findall(r"'([a-z_0-9]+)': (True|False|None)", body)
    return sum(1 for _k, v in items if v == 'True'), [k for k, v in items if v != 'True']


def summarize(path):
    lines = open(path, encoding='utf-8', errors='replace').read().split('\n')
    out = ['== ' + path]
    step_rc = []
    in_steps = False
    for i, l in enumerate(lines):
        if l.startswith('--- ['):
            if 'six steps' in l:
                in_steps = True
                out.append(l[:170])
            elif in_steps and 'strict replay on the other-stamp' not in l:
                out.append('   step: ' + l[:70])
            else:
                in_steps = False
                out.append(l[:170])
            continue
        if l.startswith('rc=') and in_steps:
            step_rc.append(l[3:].split(' ')[0])
            continue
        if l.startswith('ok= ') and not in_steps:
            rc = lines[i - 1] if i and lines[i - 1].startswith('rc=') else 'rc=?'
            nt, nf = checks(lines[i + 1]) if i + 1 < len(lines) and lines[i + 1].startswith('checks: ') else (0, [])
            out.append('   %s | %s | checks_true=%d not_true=%s' % (rc, l[:110], nt, nf))
            continue
        if l.startswith('[1] downloaded HEAD='):
            head, expect = l[len('[1] downloaded HEAD='):].split(' (expect ')
            out.append('downloaded head == expected: %s' % (head == expect.rstrip(')')))
        elif l.startswith('bound files checked='):
            out.append('manifest: ' + l[:220])
        elif l.startswith(('cloned commit:', 'audit baseline:', 'RESULT', 'renamed (same blob', 'renamed,')):
            out.append('blob: ' + l[:260])
        elif l.startswith('package kind='):
            out.append(l[:200])
        elif 'files changed,' in l and 'insertions' in l:
            out.append('diffstat vs archiving stamp: ' + l.strip())
        elif l.startswith('changed paths outside docs/'):
            out.append(l)
        elif l.startswith('original package files='):
            out.append('original package comparison: ' + l)
        elif l.startswith('FAILED verdict_binding_threeway'):
            out.append('   ' + l[:200])
        elif l.startswith('package after replays:'):
            out.append('post: ' + l)
    if step_rc:
        out.append('steps rc: ' + '/'.join(step_rc) + '  (n=%d)' % len(step_rc))
    return '\n'.join(out)


for p in sys.argv[1:]:
    print(summarize(p))
