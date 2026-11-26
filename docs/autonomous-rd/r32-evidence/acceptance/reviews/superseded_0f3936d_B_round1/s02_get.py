#!/usr/bin/python3 -I
# Seat script 02: dump a JSON sub-path (dotted keys, list index as number).
# usage: s02_get.py <json> <path> [maxlen]
import json, sys

path_file = sys.argv[1]
path = sys.argv[2] if len(sys.argv) > 2 else ""
maxlen = int(sys.argv[3]) if len(sys.argv) > 3 else 6000
with open(path_file, "r", encoding="utf-8") as fh:
    node = json.load(fh)
if path:
    for part in path.split("."):
        if isinstance(node, list):
            node = node[int(part)]
        else:
            if part not in node:
                print("MISSING key %r at %r" % (part, path))
                print("keys:", list(node.keys())[:80])
                sys.exit(2)
            node = node[part]
out = json.dumps(node, ensure_ascii=False, indent=1)
print(out[:maxlen])
if len(out) > maxlen:
    print("...[truncated %d of %d chars]" % (maxlen, len(out)))
