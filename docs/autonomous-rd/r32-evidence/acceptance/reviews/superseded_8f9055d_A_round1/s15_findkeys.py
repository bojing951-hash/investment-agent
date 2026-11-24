#!/usr/bin/python3 -I
"""Find key paths in a JSON (read-only). usage: s15_findkeys.py <file.json> <substr> [max_hits]"""
import json
import sys

obj = json.load(open(sys.argv[1], encoding="utf-8"))
needle = sys.argv[2].lower()
mx = int(sys.argv[3]) if len(sys.argv) > 3 else 60
hits = [0]


def walk(o, path):
    if hits[0] >= mx:
        return
    if isinstance(o, dict):
        for k, v in o.items():
            p = path + "/" + str(k)
            if needle in str(k).lower():
                s = json.dumps(v, ensure_ascii=False)
                print("%s  ::  %s" % (p, s[:260] + ("...(%d chars)" % len(s) if len(s) > 260 else "")))
                hits[0] += 1
            walk(v, p)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            if isinstance(v, (dict, list)):
                walk(v, path + "[%d]" % i)
            elif needle in str(v).lower():
                print("%s = %s" % (path + "[%d]" % i, str(v)[:260]))
                hits[0] += 1


walk(obj, "")
print("hits=%d" % hits[0])
