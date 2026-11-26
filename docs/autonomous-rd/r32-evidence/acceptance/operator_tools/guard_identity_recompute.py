#!/usr/bin/python3 -I
"""guard_identity_recompute.py — read-only. Evidence for the same-day re-collection guard finding at the
final stamp (clean install tree final9-entry, standard update entry re-run of 2026-11-24).

The step-2 re-collection of the same-day re-run (candidate written 17:09:06 HKT, four index valuations)
was NOT swapped in: the guard (scripts/research_provenance.py daily_face_guard_write, Audit-R25/R26)
judged it a degradation and diverted it to data/daily/superseded/. The entry receipt and the pipeline
log keep no note of it, so the guard's inputs are recomputed here with the tree's own functions
(nothing is written into the tree):
  daily_face_identity_map(_judgment_view(payload)) -> {identity: count of valid observation leaves}
  identity = first two path segments of every leaf, so source-note keys (valuation.via / valuation.note)
  of the fallback-source file count as indicator identities.
Times are HKT (UTC+8)."""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

TREE = '/tmp/r32-accept/final9-entry'
sys.dont_write_bytecode = True          # read-only: no .pyc written into the tree
sys.path.insert(0, os.path.join(TREE, 'scripts'))
import research_provenance as rp  # noqa: E402  (the acceptance tree's own code, git-archive of cf33de3)

HKT = timezone(timedelta(hours=8))
D = os.path.join(TREE, 'data', 'daily')
DATE8 = '20261124'


def hkt(t):
    return datetime.fromtimestamp(t, tz=HKT).strftime('%Y-%m-%d %H:%M:%S') if t else '(absent)'


def ids(p):
    obj = json.load(open(p, encoding='utf-8'))
    return rp.daily_face_identity_map(rp._judgment_view(obj)), obj


print('Same-day re-collection guard at the final stamp cf33de3 (clean install tree final9-entry), read-only recomputation')
print('with the tree\'s own scripts/research_provenance.py: identity = first two path segments of each leaf;')
print('valid leaf = scalar leaf with a value other than None. Times in HKT.')
print()
print('1. Files of the day per channel: live file vs files kept under data/daily/superseded/')
print('   (a superseded file whose payload time is later than the live file\'s = a candidate that was NOT swapped')
print('    in; an earlier one = the previous version kept when the live file was replaced)')
TIME_KEYS = ('timestamp', 'time', 'generated_at', 'fetched_at')   # the channels name their time field differently


def ptime(obj):
    """the collector's own time field of a daily file (first of TIME_KEYS present), else None."""
    for k in TIME_KEYS:
        if isinstance(obj.get(k), str):
            return obj[k]
    return None


live = {}
for fn in sorted(os.listdir(D)):
    if fn.endswith('_%s.json' % DATE8) and not fn.startswith('.'):
        p = os.path.join(D, fn)
        ch = fn[:-len('_%s.json' % DATE8)]
        obj = json.load(open(p, encoding='utf-8'))
        live[ch] = (os.path.getmtime(p), obj)
for fn in sorted(os.listdir(os.path.join(D, 'superseded'))):
    if '_%s_' % DATE8 not in fn:
        continue
    p = os.path.join(D, 'superseded', fn)
    ch = fn.split('_%s_' % DATE8)[0]
    m = os.path.getmtime(p)
    obj = json.load(open(p, encoding='utf-8'))
    lm, lobj = live.get(ch, (None, None))
    # decided by the collectors' own time fields (file write times of a preserved copy and of the new live
    # file fall in the same second): an OLDER payload under superseded/ = the previous version kept when the
    # live file was replaced; a NEWER payload = a candidate that was NOT swapped in
    a, b = ptime(lobj), ptime(obj)
    if a and b:
        basis = 'payload time fields'
        verdict = 'candidate NOT swapped in (diverted)' if b > a else 'previous version (live file was replaced)'
    else:
        # no time field in this channel: file write times at sub-second resolution (a preserved copy is written
        # just before the new live file; a diverted candidate is written long after the untouched live file)
        basis = 'file write times'
        verdict = ('candidate NOT swapped in (diverted)' if m > lm + 1 else
                   'previous version (live file was replaced)' if m <= lm + 1 else 'undetermined') if lm else 'undetermined'
    print('   %-13s live: written %s, time field %s | superseded %s: time field %s -> %s [%s]' % (
        ch, hkt(lm), a or '(none)', fn, b or '(none)', verdict, basis))
print()
cl = os.path.join(D, 'china_%s.json' % DATE8)
cd = os.path.join(D, 'superseded', 'china_%s_20261124_170906.json' % DATE8)
live_ids, live_obj = ids(cl)
cand_ids, cand_obj = ids(cd)
print('2. Step-2 (A股港股数据采集) china file of the day')
print('   live file     : written %s, payload timestamp %s, identities %d' % (
    hkt(os.path.getmtime(cl)), ptime(live_obj), len(live_ids)))
print('   diverted cand.: written %s, payload timestamp %s, identities %d' % (
    hkt(os.path.getmtime(cd)), ptime(cand_obj), len(cand_ids)))
miss = sorted(i for i in set(live_ids) - set(cand_ids) if live_ids[i] > 0)
new = sorted(i for i in set(cand_ids) - set(live_ids))
shrunk = sorted(i for i in set(live_ids) & set(cand_ids) if cand_ids[i] < live_ids[i])
print('3. Guard inputs: identities present in the live file and missing from the candidate (valid leaves > 0): %d' % len(miss))
for i in miss:
    print('   missing identity %s (valid leaves in live file: %d)' % ('.'.join(i), live_ids[i]))
print('   identities only in the candidate: %s' % ', '.join('.'.join(i) for i in new))
print('   identities with fewer valid leaves in the candidate: %d' % len(shrunk))
print('   -> "identity lost" branch taken: candidate diverted (status degraded_diverted)')
print()
print('4. valuation block of each file (keys only, no market values)')
for name, obj in (('live file', live_obj), ('diverted candidate', cand_obj)):
    v = obj.get('valuation')
    if isinstance(v, dict):
        print('   %-19s valuation keys: %s' % (name, ', '.join('%s%s' % (k, ' (str)' if isinstance(x, str) else '') for k, x in v.items())))
    else:
        print('   %-19s valuation: %s' % (name, type(v).__name__))
print()
print('5. Reading: the live file came from the direct run of the step-2 script, in which one valuation request')
print('   hit a read timeout through the local proxy and the fallback source supplied three indices plus the two')
print('   source-note keys via/note. The re-run collected four index valuations (000001.SH restored) but carries')
print('   no via/note keys; the guard counts those two note keys as indicator identities, so the complete')
print('   re-collection is judged to have lost 2 identities and is not swapped in.')
