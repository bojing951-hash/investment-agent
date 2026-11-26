#!/usr/bin/env python3
"""jshow.py <judgment.json> <spec> [...] — print selected parts of a judgment (read-only).
spec = dotted path with [i] indexes, e.g. l3.contradictions[0].statement ; 'keys:<path>' lists keys."""
import json
import sys

J = json.load(open(sys.argv[1], encoding='utf-8'))
for spec in sys.argv[2:]:
    keys_mode = spec.startswith('keys:')
    if keys_mode:
        spec = spec[5:]
    cur = J
    path = ''
    for tok in [t for t in spec.replace('[', '.').replace(']', '').split('.') if t]:
        path += ('.' if path else '') + tok
        if isinstance(cur, list):
            cur = cur[int(tok)]
        elif isinstance(cur, dict):
            if tok not in cur:
                print('## %s  <missing key %r; keys=%s>' % (path, tok, list(cur.keys())[:20]))
                cur = None
                break
            cur = cur[tok]
        else:
            print('## %s  <not a container>' % path)
            cur = None
            break
    print('## ' + path)
    if cur is None:
        continue
    if keys_mode:
        if isinstance(cur, dict):
            for k, v in cur.items():
                print('  %s: %s' % (k, (json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v)[:300]))
        elif isinstance(cur, list):
            for i, v in enumerate(cur):
                print('  [%d] %s' % (i, (json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v)[:300]))
        else:
            print('  ' + str(cur)[:2000])
    else:
        print(json.dumps(cur, ensure_ascii=False, indent=1) if not isinstance(cur, str) else cur)
