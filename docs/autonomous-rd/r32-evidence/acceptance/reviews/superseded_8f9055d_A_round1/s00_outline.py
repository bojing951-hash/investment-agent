#!/usr/bin/python3 -I
"""Read-only JSON outline tool.  usage: s00_outline.py <file.json> [max_depth] [max_list]"""
import json
import sys


def outline(obj, depth, max_depth, max_list, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = prefix + "/" + str(k)
            if isinstance(v, dict):
                print("%s  {dict %d}" % (p, len(v)))
                if depth < max_depth:
                    outline(v, depth + 1, max_depth, max_list, p)
            elif isinstance(v, list):
                print("%s  [list %d]" % (p, len(v)))
                if depth < max_depth and v:
                    first = v[0]
                    if isinstance(first, (dict, list)):
                        outline(v[:max_list], depth + 1, max_depth, max_list, p + "[0..%d]" % (min(len(v), max_list) - 1))
                    else:
                        print("%s    e.g. %r" % (p, first))
            else:
                s = repr(v)
                if len(s) > 160:
                    s = s[:160] + "...(%d chars)" % len(repr(v))
                print("%s = %s" % (p, s))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            p = prefix + "[%d]" % i
            if isinstance(v, (dict, list)):
                outline(v, depth + 1, max_depth, max_list, p)
            else:
                s = repr(v)
                if len(s) > 160:
                    s = s[:160] + "...(%d chars)" % len(repr(v))
                print("%s = %s" % (p, s))


def main():
    path = sys.argv[1]
    max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    max_list = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    outline(data, 0, max_depth, max_list)


if __name__ == "__main__":
    main()
