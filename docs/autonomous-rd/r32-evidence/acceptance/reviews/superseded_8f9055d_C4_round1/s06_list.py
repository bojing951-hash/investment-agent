#!/usr/bin/python3
"""Seat script: list one field (or a short tuple of fields) of every element of a list inside a JSON file (read-only).
Usage: /usr/bin/python3 -I s06_list.py <json_path> <dotpath.to.list> <key1>[,<key2>...] [maxchars]
"""
import json
import sys


def get(o, path):
    cur = o
    for part in path.split("."):
        if isinstance(cur, dict):
            if part not in cur:
                return {"__missing_key__": part, "__keys__": sorted(cur.keys())[:80]}
            cur = cur[part]
        elif isinstance(cur, list):
            cur = cur[int(part)]
        else:
            return {"__not_container__": type(cur).__name__}
    return cur


def main():
    path, dot = sys.argv[1], sys.argv[2]
    keys = sys.argv[3].split(",")
    maxc = int(sys.argv[4]) if len(sys.argv) > 4 else 160
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    sub = data if dot == "" else get(data, dot)
    if not isinstance(sub, list):
        print(json.dumps(sub, ensure_ascii=False)[:maxc])
        return
    for i, el in enumerate(sub):
        if isinstance(el, dict):
            row = []
            for k in keys:
                v = el.get(k, "<nokey:%s>" % k)
                row.append(json.dumps(v, ensure_ascii=False, default=str))
            print("[%d] %s" % (i, " | ".join(row)[:maxc]))
        else:
            print("[%d] %s" % (i, json.dumps(el, ensure_ascii=False)[:maxc]))


if __name__ == "__main__":
    main()
