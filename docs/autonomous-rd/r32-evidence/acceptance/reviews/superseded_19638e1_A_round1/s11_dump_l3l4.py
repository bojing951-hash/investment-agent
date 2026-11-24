#!/usr/bin/python3 -I
"""Flatten agent_judgment.json l3 / l4 into readable lines (read-only).
Usage: python3 -I s11_dump_l3l4.py <agent_judgment.json> <out.txt>
"""
import json
import sys

out = []


def walk(o, path):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, path + "." + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + "[%d]" % i)
    else:
        out.append("%s = %s" % (path, o))


def main():
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        d = json.load(f)
    walk(d["l3"], "l3")
    walk(d["l4"], "l4")
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("lines", len(out))


if __name__ == "__main__":
    main()
