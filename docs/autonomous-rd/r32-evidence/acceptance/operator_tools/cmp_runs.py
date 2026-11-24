#!/usr/bin/python3 -I
"""cmp_runs.py <old_run_dir> <new_run_dir> [<out.txt>]

Read-only, key-by-key comparison of the engine deterministic face of two run
directories of the same work order at two code stamps (the disclosure
"engine face unchanged between stamps except the fixed fields" must be a
measured statement, not an assumption).

Compared: report.json → research_plan / evidence_index / layers / run.evidence_gate /
run.frozen_inputs / run.data_requirements / steps[*].envelope, plus evidence_index.json,
AGENT_SEAT_ENVELOPE.json, views_digest.json, root_overlay/config/*.json and the frozen
snapshot bytes. Volatile keys (timestamps, code stamp, run ids) are skipped and listed.
String values are normalised for the install-tree path and the run-id prefix before
comparison; leaves that differ only by those are counted as path/run-id-only.
"""
import hashlib
import json
import os
import re
import sys

old, new = sys.argv[1:3]
out = open(sys.argv[3], 'w', encoding='utf-8') if len(sys.argv) > 3 else sys.stdout

VOLATILE = {'ts_utc', 'git_head', 'git_diff_sha256', 'stamped_at', 'written_at',
            'code_version', 'generated_at', 'timestamp', 'evaluated_at', 'now',
            'produced_by', 'report_dir', 'run_dir', 'root', 'tree', 'install_root',
            'snapshot_path', 'run_id', 'report_sha256', 'map_report_sha256',
            'content_sha256', 'digest', 'sha256'}
TREE_RE = re.compile(r'/tmp/r32-accept/[A-Za-z0-9_\-]+')
RUNID_RE = re.compile(r'\d{8}T\d{6}Z')
ISO_RE = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)')


def norm(v):
    if isinstance(v, str):
        v = TREE_RE.sub('<tree>', v)
        v = RUNID_RE.sub('<runid>', v)
        v = ISO_RE.sub('<iso>', v)
    return v


STATE_SUB = '/data/last_run'      # standard-update ledger state of the install tree


def leaves(obj, path, acc):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in VOLATILE:
                acc.setdefault('skipped', set()).add(k)
                continue
            leaves(v, path + '/' + str(k), acc)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            key = str(i)
            if isinstance(v, dict):
                for idk in ('step', 'name', 'metric_id', 'ref', 'id', 'region', 'dimension', 'anchor'):
                    if idk in v and isinstance(v[idk], str):
                        key = str(v[idk])
                        break
            leaves(v, path + '[' + key + ']', acc)
    else:
        if STATE_SUB in path:
            acc.setdefault('state', {})[path.split(STATE_SUB, 1)[0] + STATE_SUB + '/…'] = True
            return
        acc[path] = obj


def compare(label, a, b):
    la, lb = {}, {}
    leaves(a, '', la)
    leaves(b, '', lb)
    only_a = sorted(set(la) - set(lb))
    only_b = sorted(set(lb) - set(la))
    real, ponly = [], []
    for p in sorted(set(la) & set(lb)):
        if la[p] == lb[p]:
            continue
        if norm(la[p]) == norm(lb[p]):
            ponly.append(p)
        else:
            real.append(p)
    st = sorted(set(la.pop('state', {})) | set(lb.pop('state', {})))
    if st:
        print('   tree-state (install-tree standard-update ledger, not research evidence): %s' % st, file=out)
    n = len(set(la) | set(lb))
    print('## %s | leaves compared %d | identical %d | real diff %d | path/run-id only %d | only-old %d | only-new %d'
          % (label, n, n - len(real) - len(ponly) - len(only_a) - len(only_b),
             len(real), len(ponly), len(only_a), len(only_b)), file=out)
    def show(title, items, la_, lb_):
        if not items:
            return
        print('   %s (%d):' % (title, len(items)), file=out)
        for p in items[:400]:
            va, vb = la_.get(p, '<absent>'), lb_.get(p, '<absent>')
            sa, sb = json.dumps(va, ensure_ascii=False), json.dumps(vb, ensure_ascii=False)
            print('     %s\n        old: %s\n        new: %s'
                  % (p, sa[:300], sb[:300]), file=out)
        if len(items) > 400:
            print('     … %d more' % (len(items) - 400), file=out)
    show('REAL DIFF', real, la, lb)
    show('only-old', only_a, la, lb)
    show('only-new', only_b, la, lb)
    if ponly:
        print('   path/run-id-only sample: %s' % ponly[:3], file=out)
    return real, only_a, only_b


def load(d, *rel):
    p = os.path.join(d, *rel)
    if not os.path.exists(p):
        return None
    return open(p, encoding='utf-8').read()


def jload(d, *rel):
    p = os.path.join(d, *rel)
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding='utf-8'))


ra, rb = jload(old, 'report.json'), jload(new, 'report.json')
print('# cmp_runs\n# old: %s\n# new: %s' % (old, new), file=out)
if ra and rb:
    print('# old run %s git_head %s | new run %s git_head %s'
          % ((ra.get('run') or {}).get('run_id', (ra.get('run') or {}).get('ts_utc')),
             ((ra.get('run') or {}).get('git_head') or '')[:12],
             (rb.get('run') or {}).get('run_id', (rb.get('run') or {}).get('ts_utc')),
             ((rb.get('run') or {}).get('git_head') or '')[:12]), file=out)
    totals = [0, 0, 0]
    for key in ('research_plan', 'evidence_index', 'layers'):
        r = compare('report.json/' + key, ra.get(key), rb.get(key))
        if r:
            totals = [totals[0] + len(r[0]), totals[1] + len(r[1]), totals[2] + len(r[2])]
    for key in ('evidence_gate', 'frozen_inputs', 'data_requirements'):
        r = compare('report.json/run.' + key, (ra.get('run') or {}).get(key),
                    (rb.get('run') or {}).get(key))
        if r:
            totals = [totals[0] + len(r[0]), totals[1] + len(r[1]), totals[2] + len(r[2])]
    sa = sorted((ra.get('steps') or []), key=lambda s: str(s.get('step') or s.get('name')))
    sb = sorted((rb.get('steps') or []), key=lambda s: str(s.get('step') or s.get('name')))
    r = compare('report.json/steps[*].envelope', [s.get('envelope') for s in sa],
                [s.get('envelope') for s in sb])
    if r:
        totals = [totals[0] + len(r[0]), totals[1] + len(r[1]), totals[2] + len(r[2])]
    print('# report.json totals: real diff %d | only-old %d | only-new %d' % tuple(totals), file=out)
for rel in (('evidence_index.json',), ('AGENT_SEAT_ENVELOPE.json',), ('views_digest.json',),
            ('root_overlay', 'config', 'release_calendar.json'),
            ('root_overlay', 'config', 'metric_registry.json')):
    a, b = load(old, *rel), load(new, *rel)
    if a is None or b is None:
        print('## %s | old present %s new present %s' % ('/'.join(rel), a is not None, b is not None), file=out)
        continue
    try:
        compare('/'.join(rel), json.loads(a), json.loads(b))
    except ValueError:
        print('## %s | bytes equal: %s (%d vs %d bytes)' % ('/'.join(rel), a == b, len(a), len(b)), file=out)
snaps_a = sorted(os.listdir(os.path.join(old, 'root_overlay', 'data', 'daily')))
snaps_b = sorted(os.listdir(os.path.join(new, 'root_overlay', 'data', 'daily')))
print('## root_overlay/data/daily: old %s | new %s' % (snaps_a, snaps_b), file=out)
for s in snaps_b:
    if s in snaps_a:
        ha = hashlib.sha256(open(os.path.join(old, 'root_overlay', 'data', 'daily', s), 'rb').read()).hexdigest()
        hb = hashlib.sha256(open(os.path.join(new, 'root_overlay', 'data', 'daily', s), 'rb').read()).hexdigest()
        print('   %s sha256 old %s new %s equal %s' % (s, ha[:16], hb[:16], ha == hb), file=out)
if out is not sys.stdout:
    out.close()
    print('wrote', sys.argv[3])
