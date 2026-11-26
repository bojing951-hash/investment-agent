#!/usr/bin/python3 -I
"""Read-only: profile the seat ledger -- value types of computed/reported among counted rows and
the ids of rows that are not plain numeric comparisons (so the prose can describe them accurately).

Usage:
  python3 -I s36_ledger_types.py <points_all.jsonl>
"""
import json
import sys
from collections import Counter


def main():
    rows = [json.loads(x) for x in open(sys.argv[1], encoding='utf-8') if x.strip()]
    counted = [r for r in rows if not (r['reported'] is None and r['computed'] is not None)]
    info = [r for r in rows if (r['reported'] is None and r['computed'] is not None)]
    print('rows=%d counted=%d info=%d mismatch=%d' % (
        len(rows), len(counted), len(info), sum(1 for r in counted if not r['ok'])))
    print('computed types (counted): %s' % dict(Counter(type(r['computed']).__name__ for r in counted)))
    print('reported types (counted): %s' % dict(Counter(type(r['reported']).__name__ for r in counted)))
    print('computed types (info): %s' % dict(Counter(type(r['computed']).__name__ for r in info)))
    print('-- rows with computed None (counted):')
    for r in counted:
        if r['computed'] is None:
            print('   ', r['section'], '|', r['id'], '| reported=%r | ok=%s' % (r['reported'], r['ok']))
    print('-- rows with bool computed:')
    for r in counted:
        if isinstance(r['computed'], bool):
            print('   ', r['section'], '|', r['id'], '| reported=%r | ok=%s' % (r['reported'], r['ok']))
    print('-- rows with str computed:')
    for r in counted:
        if isinstance(r['computed'], str):
            print('   ', r['section'], '|', r['id'], '| computed=%s | reported=%s' % (r['computed'][:60], str(r['reported'])[:60]))
    print('-- rows with non-str non-bool reported (non numeric):')
    for r in counted:
        if not isinstance(r['reported'], (str, bool, int, float)) and r['reported'] is not None:
            print('   ', r['section'], '|', r['id'], '| reported=%r' % (r['reported'],))
    print('-- info rows by id prefix:')
    pref = Counter()
    for r in info:
        pref[(r['section'], r['id'].split(' ')[0] if ' ' in r['id'] else r['id'])] += 1
    for k, v in sorted(pref.items()):
        print('   ', k, v)
    print('-- info rows (non-sync):')
    for r in info:
        if r['section'] != 'sync':
            print('   ', r['section'], '|', r['id'])
    print('-- max id length: %d; max note length: %d; max src length: %d' % (
        max(len(r['id']) for r in rows), max(len(r.get('note') or '') for r in rows),
        max(len(r.get('src') or '') for r in rows)))
    print('-- rows whose cells contain a newline or pipe:')
    n = 0
    for r in rows:
        for k in ('id', 'src', 'note'):
            s = r.get(k)
            if isinstance(s, str) and ('|' in s or '\n' in s):
                n += 1
                if n <= 5:
                    print('   ', k, '|', r['id'], '|', repr(s[:120]))
    print('   total such rows: %d' % n)


if __name__ == '__main__':
    main()
