#!/usr/bin/python3 -I
"""xdiff_y.py <old_run_dir> <new_run_dir> — compare the engine faces of two runs of the same
work order (report.json + AGENT_SEAT_ENVELOPE.json).  Volatile fields (run id, code version,
timestamps, durations, paths) are skipped.  Prints every differing path (old -> new), capped.
Read-only."""
import hashlib
import json
import os
import re
import sys

SKIP_KEY = {'ts_utc', 'git_head', 'code_version', 'generated_at', 'created_at', 'elapsed', 'duration',
            'duration_s', 'seconds', 'timestamp', 'as_of_declared', 'run_id', 'report_dir', 'workdir',
            'started', 'finished', 'version_sha', 'question_sha256', 'engine_root', 'duration_ms',
            'elapsed_ms', 'read_first', 'wall_ms', 'n_chars', 'digest_sha256', 'envelope_sha256'}
CAP = 400


def load(rd):
    out = {}
    for name in ('report.json', 'AGENT_SEAT_ENVELOPE.json'):
        p = os.path.join(rd, name)
        with open(p, encoding='utf-8') as fh:
            out[name] = json.load(fh)
    return out


def walk(a, b, path, diffs):
    if len(diffs) >= CAP:
        return
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k in SKIP_KEY:
                continue
            if k not in a or k not in b:
                diffs.append((path + '.' + k, 'MISSING' if k not in a else 'ONLY_OLD', 'MISSING' if k not in b else 'ONLY_NEW'))
                continue
            walk(a[k], b[k], path + '.' + k, diffs)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            diffs.append((path + '.len', len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, '%s[%d]' % (path, i), diffs)
    elif a != b:
        diffs.append((path, a, b))


def canon(o):
    """replace volatile sub-objects inside step/digest structures"""
    if isinstance(o, dict):
        return {k: ('<skip>' if k in SKIP_KEY else canon(v)) for k, v in o.items()}
    if isinstance(o, list):
        return [canon(v) for v in o]
    if isinstance(o, str) and ('r32-accept/final' in o or 'research_runs/' in o or re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', o)):
        return '<volatile>'
    return o


old, new = load(sys.argv[1]), load(sys.argv[2])
for name in ('report.json', 'AGENT_SEAT_ENVELOPE.json'):
    diffs = []
    a, b = canon(old[name]), canon(new[name])
    walk(a, b, '', diffs)
    h1 = hashlib.sha256(json.dumps(a, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]
    h2 = hashlib.sha256(json.dumps(b, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]
    print('%s: canon sha old=%s new=%s | differing paths=%d' % (name, h1, h2, len(diffs)))
    for p, x, y in diffs[:CAP]:
        print('   %s\n      old: %s\n      new: %s' % (p, json.dumps(x, ensure_ascii=False)[:230], json.dumps(y, ensure_ascii=False)[:230]))
# other files byte-compare
for name in ('question_verbatim.txt', 'evidence_index.json', 'views_digest.json'):
    po, pn = os.path.join(sys.argv[1], name), os.path.join(sys.argv[2], name)
    if os.path.exists(po) and os.path.exists(pn):
        bo, bn = open(po, 'rb').read(), open(pn, 'rb').read()
        print('%s: %s' % (name, 'byte-identical' if bo == bn else 'DIFFERENT (%d vs %d bytes)' % (len(bo), len(bn))))
