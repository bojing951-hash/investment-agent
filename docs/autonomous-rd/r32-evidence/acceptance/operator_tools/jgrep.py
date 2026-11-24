#!/usr/bin/python3 -I
"""jgrep.py <judgment.json> <substring> [<substring> ...] — print path + full string of every
leaf string (in dict/list order) that contains any of the substrings. Read-only."""
import json
import sys


def walk(o, path, out, subs):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, path + '.' + k if path else k, out, subs)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, '%s[%d]' % (path, i), out, subs)
    elif isinstance(o, str):
        if any(s in o for s in subs[1:]):
            out.append((path, o))


doc = json.load(open(sys.argv[1], encoding='utf-8'))
out = []
walk(doc, '', out, sys.argv)
for p, s in out:
    print('##', p)
    print(s)
