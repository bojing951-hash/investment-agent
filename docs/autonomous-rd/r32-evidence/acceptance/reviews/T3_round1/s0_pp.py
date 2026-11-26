#!/usr/bin/env python3
"""Pretty-print a dotted sub-tree as JSON.  usage: python3 -I s0_pp.py <json_path> <dotted> [indent] [list_index]"""
import json
import sys


def main():
    path, dotted = sys.argv[1], sys.argv[2]
    indent = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    idx = sys.argv[4] if len(sys.argv) > 4 else None
    with open(path, "r", encoding="utf-8") as fh:
        cur = json.load(fh)
    if dotted:
        for part in dotted.split("."):
            if part == "":
                continue
            if isinstance(cur, list):
                cur = cur[int(part)]
            else:
                cur = cur[part]
    if idx is not None:
        cur = cur[int(idx)]
    print(json.dumps(cur, ensure_ascii=False, indent=indent))


if __name__ == "__main__":
    main()
