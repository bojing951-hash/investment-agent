# -*- coding: utf-8 -*-
"""列出 points.jsonl 中的偏离项与分节计数。"""
import sys, os, json, collections
PTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'points.jsonl')
c = collections.Counter(); n = 0; mm = 0
for l in open(PTS, encoding='utf-8'):
    r = json.loads(l); n += 1; c[r['section']] += 1
    if r['ok'] is False:
        mm += 1
        print('MISMATCH [%s] %s\n   src=%s\n   computed=%s\n   reported=%s\n   where=%s' % (r['section'], r.get('note'), r['src'], json.dumps(r['computed'], ensure_ascii=False)[:600], json.dumps(r['reported'], ensure_ascii=False)[:600], r.get('where')))
print('tally', n, mm)
for k, v in c.items():
    print('  ', k, v)
