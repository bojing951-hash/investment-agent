#!/usr/bin/env python3
"""Read-only: dump a JSON sub-tree selected by dotted path with optional list index.
usage: s01_dump.py <report.json> <path.to.key[.N]> [maxlen]
"""
import json
import sys


def get(data, path):
    cur = data
    for part in path.split("."):
        if isinstance(cur, dict):
            if part not in cur:
                raise KeyError(f"key {part!r} not in dict keys {list(cur.keys())[:30]}")
            cur = cur[part]
        elif isinstance(cur, list):
            cur = cur[int(part)]
        else:
            raise KeyError(f"cannot descend into {type(cur).__name__} at {part!r}")
    return cur


def main():
    path = sys.argv[1]
    sub = sys.argv[2] if len(sys.argv) > 2 else ""
    maxlen = int(sys.argv[3]) if len(sys.argv) > 3 else 100000
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    node = get(data, sub) if sub else data
    s = json.dumps(node, ensure_ascii=False, indent=1)
    if len(s) > maxlen:
        s = s[:maxlen] + f"\n...[truncated, total {len(s)} chars]"
    sys.stdout.write(s + "\n")


if __name__ == "__main__":
    main()
