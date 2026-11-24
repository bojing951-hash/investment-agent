#!/usr/bin/python3 -I
"""zsumm.py <tag> [prefix=Z] — key facts of the latest post-fix re-delivery receipts of one work
order (out/Z<tag>_report_*.json, out/Z<tag>_archive_*.json and the archive manifest).
Read-only."""
import glob
import json
import os
import sys

tag = sys.argv[1]
PFX = sys.argv[2] if len(sys.argv) > 2 else 'Z'
O = '/tmp/r32-accept/out'


def latest(pat):
    fs = sorted(glob.glob(os.path.join(O, pat)), key=os.path.getmtime)
    return fs[-1] if fs else None


def rc_of(receipt):
    p = receipt[:-5] + '.rc'
    return open(p, encoding='utf-8').read().strip().replace('rc=', '') if os.path.isfile(p) else None


rep = latest(PFX + '%s_report_*.json' % tag)
arc = latest(PFX + '%s_archive_*.json' % tag)
r = json.load(open(rep, encoding='utf-8'))
d = r.get('data', {})
print('== %s report %s rc=%s' % (tag, os.path.basename(rep), rc_of(rep)))
for k in ('deliverable', 'map_status_refreshed', 'map_renderer_drift', 'blocked'):
    if k in d:
        print('   report.%s = %s' % (k, d[k]))
rv = d.get('review') or {}
vd = rv.get('verdict')
print('   review.fresh = %s | review.verdict = %s' % (rv.get('fresh'), vd.get('verdict') if isinstance(vd, dict) else vd))
print('   warnings = %s' % [str(w)[:150] for w in (r.get('warnings') or d.get('warnings') or [])][:5])
print('   snapshot_id = %s | research_as_of = %s | target_date = %s' % (r.get('snapshot_id'), r.get('research_as_of'), r.get('target_date')))
print('   data keys = %s' % sorted(d.keys()))
a = json.load(open(arc, encoding='utf-8'))
ad = a.get('data', {})
print('== %s archive %s rc=%s' % (tag, os.path.basename(arc), rc_of(arc)))
for k in ('blocked', 'deliverable', 'verdict', 'verdicts_n', 'reason', 'reasons'):
    if k in ad:
        print('   archive.%s = %s' % (k, str(ad[k])[:200]))
if os.path.isdir(str(ad.get('archive_dir'))):
    print('   archive.archive_dir = ...%s' % ad['archive_dir'][-48:])
    m = json.load(open(os.path.join(ad['archive_dir'], 'ARCHIVE_MANIFEST.json'), encoding='utf-8'))
    for k in sorted(m):
        if any(t in k for t in ('code', 'head', 'sha', 'drift', 'equivalent', 'correlation', 'digest')):
            print('   manifest.%s = %s' % (k, str(m[k])[:120]))
    files = m.get('files')
    print('   manifest.files = %s' % (len(files) if hasattr(files, '__len__') else files))
