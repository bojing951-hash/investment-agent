#!/usr/bin/python3 -I
"""Read-only: list series_store metric ids matching given substrings and facts whose text
matches given substrings (for citing single-point facts and absence of a series).

Usage:
  python3 -I s30g_snap_facts.py <research_snapshot.json> <substr> [<substr> ...]
"""
import json
import sys


def main():
    snap = json.load(open(sys.argv[1], encoding='utf-8'))
    pats = sys.argv[2:]
    store = snap.get('series_store', {})
    print('series_store n=%d' % len(store))
    for k in sorted(store):
        if any(p.lower() in k.lower() for p in pats):
            d = store[k]
            print('  series %s n=%d first=%s last=%s' % (k, len(d.get('dates', [])),
                                                         (d.get('dates') or ['-'])[0], (d.get('dates') or ['-'])[-1]))
    facts = snap.get('facts')
    print('facts type=%s' % type(facts).__name__)
    items = facts.items() if isinstance(facts, dict) else enumerate(facts)
    for k, v in items:
        blob = json.dumps(v, ensure_ascii=False)
        key = str(k)
        if any(p.lower() in (key + ' ' + blob).lower() for p in pats):
            print('  fact %s = %s' % (key, blob[:300]))
    print('-- done')


if __name__ == '__main__':
    main()
