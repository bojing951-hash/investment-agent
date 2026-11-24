#!/usr/bin/env python3
"""verify_manifest.py <package_dir>   (read-only; run with python -I)

"Unpack exactly per the manifest" check for a downloaded archive package:
every file the ARCHIVE_MANIFEST.json binds must be present with the bound
digest — copies_sha16 (ten package files), verdict_chain[*].file/sha256 and
frozen_inputs (root_overlay copies). Prints one line per group and exits 1 on
any missing file or digest mismatch. Nothing is written.
"""
import hashlib
import json
import os
import sys

pkg = sys.argv[1]
m = json.load(open(os.path.join(pkg, 'ARCHIVE_MANIFEST.json'), encoding='utf-8'))


def sha16(rel):
    p = os.path.join(pkg, rel)
    if not os.path.isfile(p):
        return None
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


bad, n = [], 0
for rel, want in sorted((m.get('copies_sha16') or {}).items()):
    n += 1
    got = sha16(rel)
    if got != want:
        bad.append('copy %s: %s != %s' % (rel, got, want))
for v in m.get('verdict_chain') or []:
    n += 1
    got = sha16(v['file'])
    if got != str(v['sha256'])[:16]:
        bad.append('verdict %s: %s != %s' % (v['file'], got, v['sha256']))
for rel, want in sorted((m.get('frozen_inputs') or {}).items()):
    n += 1
    got = sha16(os.path.join('root_overlay', rel))
    if got != want:
        bad.append('frozen %s: %s != %s' % (rel, got, want))
extra = []
bound = set((m.get('copies_sha16') or {})) | {v['file'] for v in (m.get('verdict_chain') or [])} | \
    {os.path.join('root_overlay', r) for r in (m.get('frozen_inputs') or {})}
for dp, _, fns in os.walk(pkg):
    for fn in fns:
        rel = os.path.relpath(os.path.join(dp, fn), pkg)
        if rel not in bound and rel != 'ARCHIVE_MANIFEST.json':
            extra.append(rel)
print('manifest run_ts=%s run_code_git_head=%s verdict=%s verdicts_n=%s frozen_inputs_sha256=%s'
      % (m.get('run_ts'), m.get('run_code_git_head'), m.get('verdict'), m.get('verdicts_n'),
         str(m.get('frozen_inputs_sha256'))[:16]))
print('bound files checked=%d mismatches/missing=%d | files outside the manifest: %d %s'
      % (n, len(bad), len(extra), sorted(extra)[:6]))
for b in bad:
    print('  MISMATCH', b)
sys.exit(1 if bad else 0)
