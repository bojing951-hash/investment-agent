#!/usr/bin/env python3
"""Count evidence later than the research cutoff in a research-one report.

Usage: python3 -I count_late.py <report.json> [<report.json> ...]

Prints, per report: cutoff, declared as_of, L1 rows total / late, evidence
index total / late, plus per-kind late breakdown. Exit code 0 always (this is
a measuring tool; the verdict is for the caller to read).
"""
import json
import re
import sys
from collections import Counter


def ref_date(ref):
    m = re.search(r'@(\d{4}-\d{2}-\d{2})', str(ref))
    return m.group(1) if m else None


def main(paths):
    for p in paths:
        r = json.load(open(p, encoding='utf-8'))
        rp = r.get('research_plan') or {}
        cut = rp.get('cutoff')
        dec = (rp.get('as_of_declared') or {}).get('as_of')
        eff = cut
        l1 = ((r.get('layers') or {}).get('L1_事实层') or {}).get('rows') or []
        l1_late = [x for x in l1
                   if cut and str(x.get('observation_date') or '') > cut]
        ei = r.get('evidence_index') or []
        ei_late = [e for e in ei if cut and (d := ref_date(e.get('ref'))) and d > cut]
        ei_nodate = [e for e in ei if ref_date(e.get('ref')) is None]
        print('== %s' % p)
        print('   run.git_head=%s source=%s' % (
            (r.get('run') or {}).get('git_head'),
            (r.get('run') or {}).get('git_head_source')))
        print('   cutoff=%s as_of_declared=%s effective=%s' % (cut, dec, eff))
        print('   L1 rows: total=%d late(>cutoff)=%d' % (len(l1), len(l1_late)))
        print('   evidence_index: total=%d late(>cutoff)=%d nodate=%d' % (
            len(ei), len(ei_late), len(ei_nodate)))
        print('   late by kind: %s' % dict(Counter(e.get('kind') for e in ei_late)))
        if l1_late:
            print('   late L1 obs dates: %s' % dict(Counter(
                str(x.get('observation_date')) for x in l1_late)))
        print('   late evidence refs: %s' % sorted(
            {str(e.get('ref')) for e in ei_late})[:12])
        ev = r.get('evidence_view') or (r.get('run') or {}).get('evidence_view')
        if ev:
            print('   evidence_view: %s' % json.dumps(ev, ensure_ascii=False)[:900])


if __name__ == '__main__':
    main(sys.argv[1:])
