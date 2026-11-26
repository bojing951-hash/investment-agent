#!/usr/bin/env python3
"""Read-only: search JSON file for key names or string values containing a substring; prints paths.
usage: s10_find_keys.py <file.json> <substr> [--values] [--max N]
"""
import json
import sys


def walk(node, path, sub, want_values, hits, maxhits):
    if len(hits) >= maxhits:
        return
    if isinstance(node, dict):
        for k, v in node.items():
            p = f"{path}.{k}"
            if sub in str(k):
                s = json.dumps(v, ensure_ascii=False)
                hits.append((p, "KEY", s[:300]))
            walk(v, p, sub, want_values, hits, maxhits)
            if len(hits) >= maxhits:
                return
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f"{path}[{i}]", sub, want_values, hits, maxhits)
            if len(hits) >= maxhits:
                return
    elif want_values and isinstance(node, str):
        if sub in node:
            hits.append((path, "VAL", node[:400]))


def main():
    path = sys.argv[1]
    sub = sys.argv[2]
    want_values = "--values" in sys.argv
    maxhits = 60
    if "--max" in sys.argv:
        maxhits = int(sys.argv[sys.argv.index("--max") + 1])
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    hits = []
    walk(data, "", sub, want_values, hits, maxhits)
    for p, kind, s in hits:
        print(f"[{kind}] {p} :: {s}")
    print(f"# hits={len(hits)}")


if __name__ == "__main__":
    main()
