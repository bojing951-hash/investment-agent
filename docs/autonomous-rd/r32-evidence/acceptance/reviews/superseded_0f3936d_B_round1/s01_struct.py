#!/usr/bin/python3 -I
# Seat script 01: structure probe of report.json / snapshot (read-only).
import json, sys

def outline(obj, depth, maxdepth, prefix=""):
    if depth > maxdepth:
        return
    if isinstance(obj, dict):
        for k in list(obj.keys())[:60]:
            v = obj[k]
            t = type(v).__name__
            extra = ""
            if isinstance(v, (dict, list)):
                extra = " len=%d" % len(v)
            elif isinstance(v, (str, int, float, bool)) or v is None:
                s = repr(v)
                extra = " = " + (s[:110] + ("…" if len(s) > 110 else ""))
            print("%s%s: %s%s" % (prefix, k, t, extra))
            outline(v, depth + 1, maxdepth, prefix + "  ")
    elif isinstance(obj, list):
        if obj:
            first = obj[0]
            print("%s[0]: %s" % (prefix, type(first).__name__))
            if isinstance(first, (dict, list)):
                outline(first, depth + 1, maxdepth, prefix + "  ")

path = sys.argv[1]
maxdepth = int(sys.argv[2]) if len(sys.argv) > 2 else 1
with open(path, "r", encoding="utf-8") as fh:
    data = json.load(fh)
outline(data, 0, maxdepth)
