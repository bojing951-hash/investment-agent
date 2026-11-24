#!/usr/bin/python3
"""Seat script: find every string value containing a needle inside a JSON file and print its dot path (read-only).
Usage: /usr/bin/python3 -I s07_find.py <json_path> <needle> [<needle> ...] [maxchars]
"""
import json
import sys


def walk(node, path, hits, needle):
    if isinstance(node, dict):
        for k, v in node.items():
            walk(v, path + "." + str(k) if path else str(k), hits, needle)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, "%s[%d]" % (path, i), hits, needle)
    elif isinstance(node, str):
        if needle in node:
            hits.append((path, node))


def main():
    path = sys.argv[1]
    needles = [a for a in sys.argv[2:] if not a.isdigit()]
    maxc = int(sys.argv[2 + len(needles)]) if len(sys.argv) > 2 + len(needles) else 260
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    for needle in needles:
        hits = []
        walk(data, "", hits, needle)
        print("## %r: %d hit(s)" % (needle, len(hits)))
        for p, s in hits:
            i = s.find(needle)
            lo, hi = max(0, i - 60), min(len(s), i + maxc)
            print("   %s | ...%s..." % (p, s[lo:hi]))


if __name__ == "__main__":
    main()
