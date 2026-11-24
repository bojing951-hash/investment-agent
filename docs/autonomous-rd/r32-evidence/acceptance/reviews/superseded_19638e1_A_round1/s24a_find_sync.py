#!/usr/bin/python3 -I
"""Read-only: print the JSON paths of every string leaf equal to a sync label (同步/分化/缺证/基准) in report.json,
and the structure of the enclosing object.

Usage:
  python3 -I s24a_find_sync.py <report.json>
"""
import json
import sys

LABELS = set([u'同步', u'分化', u'缺证', u'基准', u'不同步'])


def walk(o, path, hits):
    if isinstance(o, str):
        if o in LABELS:
            hits.append(path)
    elif isinstance(o, dict):
        for k, v in o.items():
            walk(v, path + '.' + str(k), hits)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + '[%d]' % i, hits)


def get(rep, path):
    o = rep
    for tok in path.replace('[', '.').replace(']', '').split('.')[1:]:
        o = o[int(tok)] if isinstance(o, list) else o[tok]
    return o


def main():
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        rep = json.load(f)
    hits = []
    walk(rep, 'report', hits)
    print('label leaves: %d' % len(hits))
    # group by parent path
    parents = {}
    for h in hits:
        p = h.rsplit('.', 1)[0].rsplit('[', 1)[0] if h.endswith(']') is False and '.' in h else h
        parent = h
        for cut in ('.label', '.sync_label', '.sync', '.direction', '.relation'):
            if h.endswith(cut):
                parent = h[:-len(cut)]
                break
        parents.setdefault(parent, []).append(h)
    print('distinct parents: %d' % len(parents))
    # print the 10 longest parent paths (most specific)
    ps = sorted(parents, key=len, reverse=True)
    seen = set()
    shown = 0
    for p in ps:
        key = p.split('[')[0] if '[' in p else p
        stem = p
        # collapse list indexes to show a structural signature
        import re
        sig = re.sub(r'\[\d+\]', '[]', p)
        if sig in seen:
            continue
        seen.add(sig)
        print('PARENT', p)
        try:
            o = get(rep, p)
            print('   object:', json.dumps(o, ensure_ascii=False)[:500])
        except Exception as e:
            print('   (cannot resolve: %s)' % e)
        shown += 1
        if shown >= 14:
            break


if __name__ == '__main__':
    main()
