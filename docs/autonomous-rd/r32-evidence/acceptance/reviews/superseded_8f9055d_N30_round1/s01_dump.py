#!/usr/bin/python3 -I
"""Seat script: dump selected subtrees of report.json (read-only).
usage: s01_dump.py <report.json> <dotted path> [max list items]
"""
import json
import sys


def get(obj, dotted):
    cur = obj
    for part in dotted.split("."):
        if isinstance(cur, dict):
            if part not in cur:
                return ("__MISSING__", part)
            cur = cur[part]
        elif isinstance(cur, list):
            try:
                idx = int(part)
            except ValueError:
                return ("__NOTINDEX__", part)
            cur = cur[idx]
        else:
            return ("__NOTCONTAINER__", part)
    return cur


def trim(obj, n_items):
    if isinstance(obj, dict):
        return {k: trim(v, n_items) for k, v in obj.items()}
    if isinstance(obj, list):
        if len(obj) > n_items:
            head = [trim(v, n_items) for v in obj[:n_items]]
            return head + ["...(%d more)" % (len(obj) - n_items)]
        return [trim(v, n_items) for v in obj]
    return obj


def main():
    path = sys.argv[1]
    dotted = sys.argv[2]
    n_items = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    val = get(data, dotted)
    print(json.dumps(trim(val, n_items), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
