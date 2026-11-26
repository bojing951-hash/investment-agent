#!/usr/bin/env python3
"""Read-only structure explorer.  usage: python3 -I s0_explore.py <json_path> <dotted_path> [max_depth] [max_items]"""
import json
import sys


def walk(obj, depth, max_depth, prefix, out, max_items):
    if depth > max_depth:
        return
    if isinstance(obj, dict):
        for i, (k, v) in enumerate(obj.items()):
            if i >= max_items:
                out.append(f"{prefix}{k}/ ... ({len(obj)} keys total)")
                break
            if isinstance(v, dict):
                out.append(f"{prefix}{k}/ dict({len(v)})")
                walk(v, depth + 1, max_depth, prefix + "  ", out, max_items)
            elif isinstance(v, list):
                out.append(f"{prefix}{k}/ list({len(v)})")
                if v and depth < max_depth:
                    first = v[0]
                    if isinstance(first, (dict, list)):
                        out.append(f"{prefix}  [0]:")
                        walk(first, depth + 1, max_depth, prefix + "    ", out, max_items)
                    else:
                        out.append(f"{prefix}  [0]= {repr(first)[:200]}")
            else:
                out.append(f"{prefix}{k} = {repr(v)[:300]}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:max_items]):
            if isinstance(v, (dict, list)):
                out.append(f"{prefix}[{i}]:")
                walk(v, depth + 1, max_depth, prefix + "  ", out, max_items)
            else:
                out.append(f"{prefix}[{i}] = {repr(v)[:300]}")


def main():
    path, dotted = sys.argv[1], sys.argv[2]
    max_depth = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    max_items = int(sys.argv[4]) if len(sys.argv) > 4 else 60
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    cur = data
    if dotted:
        for part in dotted.split("."):
            if part == "":
                continue
            if isinstance(cur, list):
                cur = cur[int(part)]
            else:
                cur = cur[part]
    out = []
    if isinstance(cur, (dict, list)):
        walk(cur, 0, max_depth, "", out, max_items)
        print("\n".join(out))
    else:
        print(repr(cur))


if __name__ == "__main__":
    main()
