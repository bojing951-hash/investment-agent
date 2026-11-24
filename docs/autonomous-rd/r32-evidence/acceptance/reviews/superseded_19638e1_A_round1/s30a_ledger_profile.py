#!/usr/bin/python3 -I
"""Seat-internal: profile the seat ledger (read-only on the ledger; prints to stdout).

Per section: counted / ok / mismatched / informational rows, and the id patterns of the informational rows.

Usage:
  python3 -I s30a_ledger_profile.py <points_all.jsonl>
"""
import json
import re
import sys
from collections import Counter, OrderedDict


def is_info(r):
    return r.get('reported') is None and r.get('computed') is not None


def main():
    rows = [json.loads(x) for x in open(sys.argv[1], encoding='utf-8') if x.strip()]
    secs = OrderedDict()
    for r in rows:
        s = secs.setdefault(r['section'], Counter())
        if is_info(r):
            s['info'] += 1
        else:
            s['counted'] += 1
            if r.get('ok'):
                s['ok'] += 1
            else:
                s['bad'] += 1
    tot = Counter()
    for k, c in secs.items():
        print('%-10s counted=%d ok=%d mismatch=%d info=%d' % (k, c['counted'], c['ok'], c['bad'], c['info']))
        tot.update(c)
    print('TOTAL      counted=%d ok=%d mismatch=%d info=%d rows=%d' % (
        tot['counted'], tot['ok'], tot['bad'], tot['info'], len(rows)))
    # informational rows by (section, id pattern)
    pats = Counter()
    for r in rows:
        if is_info(r):
            pid = r['id']
            # collapse metric ids / dates
            p = re.sub(r'[A-Z0-9_]{4,}(@[^ :]+)?', '<M>', pid)
            p = re.sub(r'\d{4}-\d{2}(-\d{2})?', '<D>', p)
            p = re.sub(r'\d+(\.\d+)?', '<n>', p)
            pats[(r['section'], p)] += 1
    print('--- informational rows by pattern')
    for (s, p), n in sorted(pats.items()):
        print('  %3d  %-8s %s' % (n, s, p))
    # distinct keys
    keys = Counter()
    for r in rows:
        keys[tuple(sorted(r.keys()))] += 1
    print('--- key sets')
    for k, n in keys.items():
        print('  %4d %s' % (n, list(k)))
    # value types
    types = Counter()
    for r in rows:
        types[(type(r.get('computed')).__name__, type(r.get('reported')).__name__)] += 1
    print('--- value type pairs (computed, reported)')
    for k, n in sorted(types.items()):
        print('  %4d %s' % (n, k))
    # any row whose ok is not a bool
    nb = sum(1 for r in rows if not isinstance(r.get('ok'), bool))
    print('rows with non-bool ok: %d' % nb)
    # informational rows with ok False?
    print('informational rows with ok False: %d' % sum(1 for r in rows if is_info(r) and not r.get('ok')))
    # counted rows with reported None?
    print('counted rows with reported None: %d' % sum(1 for r in rows if not is_info(r) and r.get('reported') is None))
    print('counted rows with computed None: %d' % sum(1 for r in rows if not is_info(r) and r.get('computed') is None))


if __name__ == '__main__':
    main()
