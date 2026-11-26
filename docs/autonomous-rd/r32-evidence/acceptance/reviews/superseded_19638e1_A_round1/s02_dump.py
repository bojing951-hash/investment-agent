#!/usr/bin/python3 -I
"""Dump a JSON sub-tree by dotted path (read-only).
Usage: python3 -I s02_dump.py <report.json> <path.to.key> [indent]
list index via [n].  '*' prints each element's outline one level.
"""
import json
import sys


def get(obj, path):
    if path == "":
        return obj
    cur = obj
    for part in path.split("."):
        if part == "":
            continue
        while part.endswith("]") and "[" in part:
            idx = part[part.rindex("[") + 1:-1]
            cur_idx = int(idx)
            part = part[:part.rindex("[")]
            cur = cur[cur_idx]
        if isinstance(cur, dict):
            cur = cur[part]
        else:
            raise KeyError(part)
    return cur


def main():
    path = sys.argv[1]
    key = sys.argv[2]
    indent = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    sub = get(d, key)
    json.dump(sub, sys.stdout, ensure_ascii=False, indent=indent)
    print()


if __name__ == "__main__":
    main()
