#!/usr/bin/env python3
"""dumpitems_all.py <VERDICT.json> [...] — print id / severity / first chars of every item (read-only)."""
import json
import sys

for p in sys.argv[1:]:
    v = json.load(open(p, encoding='utf-8'))
    print('==', p.replace('/tmp/r32-accept/', ''), '| verdict', v.get('verdict'), '| points', v.get('recompute_points'),
          '| mismatches', v.get('recompute_mismatches'), '| items', len(v.get('items') or []))
    for it in v.get('items') or []:
        t = it.get('title') or it.get('where') or it.get('item') or ''
        d = it.get('detail') or it.get('note') or it.get('finding') or ''
        fx = it.get('fix') or it.get('suggested_fix') or ''
        print('  %-4s %-6s %s | %s%s' % (it.get('id') or '-', it.get('severity'), str(t)[:70].replace('\n', ' '),
                                         str(d)[:int(sys.argv[1] and 0 or 150)].replace('\n', ' '),
                                         (' | fix: ' + str(fx)[:90].replace('\n', ' ')) if fx else ''))
