#!/usr/bin/python3
"""Seat script: read-only structural exploration of a JSON file.
Usage: /usr/bin/python3 -I s01_explore.py <json_path> [max_depth] [max_list_items]
Prints key paths (truncated values). Never writes anything.
"""
import json
import sys


def describe(v):
    if v is None:
        return "None"
    if isinstance(v, bool):
        return "bool:%s" % v
    if isinstance(v, (int, float)):
        return "%s:%r" % (type(v).__name__, v)
    if isinstance(v, str):
        s = v.replace("\n", " ")
        return "str[%d]:%s" % (len(v), s[:160])
    if isinstance(v, list):
        return "list[%d]" % len(v)
    if isinstance(v, dict):
        return "dict[%d]" % len(v)
    return type(v).__name__


def walk(o, prefix, depth, max_depth, max_items, out):
    if isinstance(o, dict):
        for k in o:
            v = o[k]
            p = "%s.%s" % (prefix, k) if prefix else k
            out.append("%s = %s" % (p, describe(v)))
            if depth < max_depth and isinstance(v, (dict, list)):
                walk(v, p, depth + 1, max_depth, max_items, out)
    elif isinstance(o, list):
        if not o:
            return
        # show first item type only
        first = o[0]
        p = "%s[0]" % prefix
        if isinstance(first, (dict, list)):
            out.append("%s = %s" % (p, describe(first)))
            if depth < max_depth:
                walk(first, p, depth + 1, max_depth, max_items, out)
        else:
            out.append("%s = %s" % (p, describe(first)))
            if len(o) > 1:
                out.append("%s[last=%d] = %s" % (prefix, len(o) - 1, describe(o[-1])))


def main():
    path = sys.argv[1]
    max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    out = []
    walk(data, "", 0, max_depth, 3, out)
    for line in out:
        print(line)


if __name__ == "__main__":
    main()
