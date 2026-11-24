#!/usr/bin/python3
"""dumpverdict.py <VERDICT-roundN.json> — print verdict summary + findings (read-only)."""
import json, sys
V = json.load(open(sys.argv[1], encoding='utf-8'))
skip = {'recompute_log', 'points', 'recompute_points_log', 'counterexamples'}
for k, v in V.items():
    if k in skip:
        print('%s: <%s len %s>' % (k, type(v).__name__, len(v) if hasattr(v, '__len__') else '-'))
        continue
    s = json.dumps(v, ensure_ascii=False)
    print('%s: %s' % (k, s if len(s) < 600 else s[:600] + '…'))
