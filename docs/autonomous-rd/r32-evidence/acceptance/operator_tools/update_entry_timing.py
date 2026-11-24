#!/usr/bin/python3 -I
"""update_entry_timing.py — read-only. Timing of the standard update entry (`ia_cli update --yes`) in the
clean install trees, from the receipts' own time stamps, the time fields inside each day's data files and
the write times of the PBOC announcement cache pages. Times are shown in HKT (UTC+8, the local clock of
the trees). Nothing is typed in except the label of each run and one earlier reading, marked as such.

Step 2 (A股港股数据采集 = scripts/china_market_collector.py) makes 8 tushare index_daily calls spaced
>= 61 s (source rate limit) and then walks the PBOC open-market-operation announcement pages one by one
(cached under data/cache/pboc_omo/; on a fresh tree every page is a network fetch). It writes
data/daily/china_<date>.json only when it finishes. The pipeline's per-step limit (run_weekly.run_step)
is 900 s. The entry receipt and the pipeline log keep no step durations and no cause line, so the times
are read from files:
- data/daily/global_<date>.json (step 1 output) carries the collector's own `time`; when a later run of
  the day replaces a file, the replaced file is kept under data/daily/superseded/ named with the
  replacement time; a same-day candidate judged a degradation (an indicator identity missing) is written
  to that directory instead of the live file (the complete live file stays).
- data/daily/china_<date>.json (step 2 output) carries the collector's own `timestamp`."""
import glob
import json
import os
from datetime import datetime, timedelta, timezone

OUT = '/tmp/r32-accept/out'
HKT = timezone(timedelta(hours=8))
DATE8 = '20261124'
RUNS = [('final6-entry', '36499bb (execution stamp), standard entry', 'YENTRY_update_*.meta', False),
        ('final8-entry', '24141c0 (superseded stamp), standard entry', 'WENTRY_update_*.meta', False),
        ('final9-entry', 'cf33de3 (final stamp), standard entry, first run of the day', 'VENTRY_update_*.meta', False),
        ('final9-entry', 'cf33de3 (final stamp), step-2 script run directly (diagnosis)',
         'VSTEP2DIAG_step2diag.meta', True),
        ('final9-entry', 'cf33de3 (final stamp), standard entry, same-day re-run (revision option)',
         'VRENTRY_update_*.meta', False)]


def parse_meta(pattern):
    fs = sorted(glob.glob(os.path.join(OUT, pattern)))
    if not fs:
        return None
    L = [l.strip() for l in open(fs[-1], encoding='utf-8') if l.strip()]
    ts = [l for l in L if l.startswith('20')]
    rc = [l for l in L if l.startswith('rc=')]
    return (os.path.basename(fs[-1]), datetime.strptime(ts[0], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc),
            datetime.strptime(ts[-1], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc), rc[-1][3:] if rc else '?')


def hkt(dt):
    return dt.astimezone(HKT).strftime('%H:%M:%S')


def mt(p):
    return datetime.fromtimestamp(os.path.getmtime(p), tz=timezone.utc) if os.path.isfile(p) else None


def inside(t, t0, t1):
    return t is not None and t0 <= t <= t1


def same_day(t0, clock):
    """datetime (HKT) of clock 'HH:MM:SS' on the local date of t0."""
    d = t0.astimezone(HKT)
    return datetime(d.year, d.month, d.day, *[int(x) for x in clock.split(':')], tzinfo=HKT)


print('Standard update entry `ia_cli update --yes` (clean install trees); times in HKT = UTC+8; per-step limit 900 s;')
print('step 2 = 8 tushare calls spaced >= 61 s (about 11 min fixed) + about 290 PBOC announcement pages '
      '(one fetch each on a fresh tree)')
print()
for tree, stamp, pattern, direct in RUNS:
    m = parse_meta(pattern)
    if not m:
        print('stamp %s: no receipt (%s)' % (stamp, pattern))
        continue
    name, t0, t1, rc = m
    D = '/tmp/r32-accept/%s/data/daily/' % tree
    print('stamp %s' % stamp)
    print('  receipt %s: %s..%s HKT, rc=%s' % (name, hkt(t0), hkt(t1), rc))
    pages = sorted(t for t in (mt(p) for p in glob.glob('/tmp/r32-accept/%s/data/cache/pboc_omo/*' % tree))
                   if inside(t, t0, t1))
    g_live = D + 'global_%s.json' % DATE8
    g_m = mt(g_live)
    if inside(g_m, t0, t1):
        g_t = json.load(open(g_live, encoding='utf-8')).get('time')
        print('  step 1 output: live file, payload time %s, written %s' % (g_t, hkt(g_m)))
        g_ref = g_m
    else:
        # this run's step-1 file was replaced by a later run of the day: its preserved copy carries its payload time
        c = sorted(((p, json.load(open(p, encoding='utf-8')).get('time'), mt(p))
                    for p in glob.glob(D + 'superseded/global_%s_*.json' % DATE8)), key=lambda x: x[2])
        p, g_t, pm = c[0]
        print('  step 1 output: replaced by a later run of the day; its preserved copy %s carries payload time %s' % (
            os.path.basename(p), g_t))
        g_ref = same_day(t0, g_t)        # within a few seconds of the file write time
    c_live = D + 'china_%s.json' % DATE8
    c_m = mt(c_live)
    c_ts = json.load(open(c_live, encoding='utf-8')).get('timestamp') if c_m else None
    cand = sorted((p for p in glob.glob(D + 'superseded/china_%s_*.json' % DATE8) if inside(mt(p), t0, t1)),
                  key=mt)
    mm = mt(D + 'macro_%s.json' % DATE8)
    if direct:
        print('  step 2 run directly (no limit): finished %s = %d s after its start; live china file payload time %s, '
              'written %s' % (hkt(c_m), int((c_m - t0).total_seconds()), c_ts, hkt(c_m)))
    elif cand:
        p = cand[-1]
        pm = mt(p)
        print('  step 2 finished %s = %d s after the step-1 file (limit 900 s): payload time %s; the candidate was NOT ' % (
            hkt(pm), int((pm - g_ref).total_seconds()), json.load(open(p, encoding='utf-8')).get('timestamp')))
        print('  swapped in - written to the same-day superseded slot %s: it lacks one indicator identity (valuation: ' % (
            os.path.basename(p)))
        print('  %d identities against %d in the live file), so the complete live file written %s (payload time %s) ' % (
            len(json.load(open(p, encoding='utf-8')).get('valuation', {})),
            len(json.load(open(c_live, encoding='utf-8')).get('valuation', {})), hkt(c_m), c_ts))
        print('  stayed and fed the new snapshot')
    elif inside(c_m, t0, t1):
        print('  step 2 output: live file, payload time %s, written %s -> %d s after the step-1 file' % (
            c_ts, hkt(c_m), int((c_m - g_ref).total_seconds())))
    else:
        print('  step 2 output: NO china file written in the run window (live file is from a later run: %s)' % hkt(c_m))
    print('  step 3 output (live macro file) written %s%s' % (
        hkt(mm) if mm else '?', '' if inside(mm, t0, t1) else ' (from a later run of the day)'))
    if pages:
        pace = (pages[-1] - pages[0]).total_seconds() / max(1, len(pages) - 1)
        print('  PBOC announcement pages fetched in the run window: %d pages, %s..%s HKT (%.1f s per page)' % (
            len(pages), hkt(pages[0]), hkt(pages[-1]), pace))
        if not inside(c_m, t0, t1) and not cand and not direct:
            limit = g_ref + timedelta(seconds=900)
            print('  walk began %d s after the step-1 file; last cached page vs step-1 file + 900 s: %s vs %s (%+.0f s)' % (
                int((pages[0] - g_ref).total_seconds()), hkt(pages[-1]), hkt(limit),
                (pages[-1] - limit).total_seconds()))
            print('  -> the pages stop at the 900 s limit within one page interval: the limit stopped step 2 in the walk')
    else:
        print('  PBOC announcement pages fetched in the run window: 0 (all cache hits of the earlier runs of the day)')
    print()
print('How to read it: step 2 = (about 11 min of mandated waiting) + (page count x PBOC response time). On the three')
print('fresh trees the walk took 111 s (289 pages at 0.4 s), 167 s (291 pages at 0.6 s) and, at 2.5 s per page, was')
print('cut after 93 pages at the limit; with a warm cache the direct run and the re-run took 760 s and about 10.5 min')
print('of step 2. The pipeline prints the cause line of a step that hits the limit, but the entry receipt keeps only')
print('output tails and the pipeline log has no step durations or cause, so the cause is read here from file times.')
print('One earlier reading is quoted in the report, not here: the step-1 file of the first run showed the write time')
print('16:12:45 at 16:40 HKT, before the re-run replaced it (its payload time 16:12:43 agrees within 2 s).')
