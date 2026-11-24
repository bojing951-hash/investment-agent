#!/usr/bin/python3 -I
"""Find string values containing a substring. usage: s15_findval.py <file.json> <substr> [ctx] [max_hits]"""
import json
import sys

obj = json.load(open(sys.argv[1], encoding="utf-8"))
needle = sys.argv[2]
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 80
mx = int(sys.argv[4]) if len(sys.argv) > 4 else 40
hits = [0]


def walk(o, path):
    if hits[0] >= mx:
        return
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, path + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + "[%d]" % i)
    elif isinstance(o, str):
        i = o.find(needle)
        if i >= 0:
            print("%s :: ...%s..." % (path, o[max(0, i - ctx): i + len(needle) + ctx].replace("\n", " ")))
            hits[0] += 1


walk(obj, "")
print("hits=%d" % hits[0])
