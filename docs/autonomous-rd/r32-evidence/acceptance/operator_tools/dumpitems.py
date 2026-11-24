#!/usr/bin/python3
"""dumpitems.py <VERDICT-roundN.json> — print the findings list in full (read-only)."""
import json, sys
V = json.load(open(sys.argv[1], encoding='utf-8'))
items = V.get('items') or V.get('findings') or []
for i, it in enumerate(items):
    print('#%d [%s] %s' % (i, it.get('severity'), it.get('where')))
    for k in ('note', 'original', 'suggested', 'fix', 'evidence'):
        if it.get(k):
            print('   %s: %s' % (k, it[k]))
    print()
