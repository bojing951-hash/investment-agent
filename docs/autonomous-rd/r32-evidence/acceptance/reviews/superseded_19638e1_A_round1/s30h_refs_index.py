#!/usr/bin/python3 -I
"""Read-only: cross-check every evidence ref cited by the judgment (L3 + L4) against
evidence_index.json and series_store (observation date present, not after the cutoff).

Usage:
  python3 -I s30h_refs_index.py <agent_judgment.json> <evidence_index.json> <research_snapshot.json>
"""
import json
import sys


def walk(o, path, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == 'evidence_refs' and isinstance(v, list):
                for i, ref in enumerate(v):
                    out.append(('%s.evidence_refs[%d]' % (path, i), ref))
            else:
                walk(v, '%s.%s' % (path, k), out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, '%s[%d]' % (path, i), out)


def main():
    jud = json.load(open(sys.argv[1], encoding='utf-8'))
    idx = json.load(open(sys.argv[2], encoding='utf-8'))
    snap = json.load(open(sys.argv[3], encoding='utf-8'))
    store = snap.get('series_store', {})
    refs = []
    for top in ('l3', 'l4'):
        walk(jud.get(top, {}), top, refs)
    print('judgment refs (L3+L4): %d' % len(refs))
    uniq = {}
    for p, r in refs:
        uniq.setdefault(r, []).append(p)
    print('unique refs: %d' % len(uniq))
    rows = idx if isinstance(idx, list) else idx.get('rows', idx.get('evidence', idx))
    print('evidence_index rows: %d (type %s)' % (len(rows), type(idx).__name__))
    if rows:
        print('sample row keys: %s' % sorted(rows[0].keys()))
    index_keys = set()
    for row in rows:
        index_keys.add(json.dumps(row, ensure_ascii=False, sort_keys=True))
    bad = 0
    for ref in sorted(uniq):
        metric, _, date = ref.partition('@')
        d = store.get(metric)
        present = bool(d) and date in d.get('dates', [])
        val = None
        if present:
            val = d['values'][d['dates'].index(date)]
        in_index = any((row.get('metric_id') == metric and date in json.dumps(row, ensure_ascii=False))
                       for row in rows if isinstance(row, dict))
        flag = 'OK' if (present and in_index and date <= '2026-11-23') else 'CHECK'
        if flag != 'OK':
            bad += 1
        print('%s %-26s store=%s value=%s index=%s cited_by=%d' % (flag, ref, present, val, in_index, len(uniq[ref])))
    print('-- non-OK: %d' % bad)


if __name__ == '__main__':
    main()
