#!/usr/bin/env python3
"""Seat-owned read-only agent_judgment extractor.
Usage: python3 -I extract_judgment.py <agent_judgment.json> keys
       python3 -I extract_judgment.py <agent_judgment.json> get <dotted.path> [maxchars]
"""
import json, sys

def main(argv):
    path = argv[0]
    with open(path, "r", encoding="utf-8") as fh:
        aj = json.load(fh)
    mode = argv[1]
    if mode == "keys":
        for k, v in aj.items():
            if isinstance(v, dict):
                print(f"{k}: dict keys={list(v.keys())[:30]}")
                for k2, v2 in v.items():
                    if isinstance(v2, dict):
                        print(f"   .{k2}: dict keys={list(v2.keys())[:30]}")
                    elif isinstance(v2, list):
                        print(f"   .{k2}: list[{len(v2)}]")
                    else:
                        print(f"   .{k2}: {repr(v2)[:160]}")
            elif isinstance(v, list):
                print(f"{k}: list[{len(v)}]")
            else:
                print(f"{k}: {repr(v)[:200]}")
        return
    if mode == "get":
        node = aj
        for part in argv[2].split("."):
            if isinstance(node, list):
                node = node[int(part)]
            else:
                node = node[part]
        maxc = int(argv[3]) if len(argv) > 3 else 6000
        s = json.dumps(node, ensure_ascii=False, indent=1)
        print(s[:maxc])
        if len(s) > maxc:
            print(f"...[truncated, total {len(s)} chars]")
        return
    print("unknown mode")

if __name__ == "__main__":
    main(sys.argv[1:])
