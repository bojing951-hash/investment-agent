#!/usr/bin/python3
"""Seat script: dump selected subtrees of report.json as JSON (read-only).
Usage: /usr/bin/python3 -I s02_dump_report.py <report.json> <dotpath> [maxlist]
dotpath uses '.' separators; integer segments index lists.
"""
import json
import sys


def get(o, path):
    if not path:
        return o
    cur = o
    for part in path.split("."):
        if isinstance(cur, dict):
            if part not in cur:
                return {"__missing_key__": part, "__keys__": sorted(cur.keys())[:60]}
            cur = cur[part]
        elif isinstance(cur, list):
            try:
                cur = cur[int(part)]
            except Exception:
                return {"__bad_index__": part, "__len__": len(cur)}
        else:
            return {"__not_container__": type(cur).__name__}
    return cur


def main():
    path = sys.argv[1]
    dot = sys.argv[2] if len(sys.argv) > 2 else ""
    maxlist = int(sys.argv[3]) if len(sys.argv) > 3 else 100000
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    sub = get(data, dot)
    if isinstance(sub, list) and len(sub) > maxlist:
        sub = sub[:maxlist] + ["...truncated %d more" % (len(sub) - maxlist)]
    print(json.dumps(sub, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
