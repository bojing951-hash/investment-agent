#!/usr/bin/python3 -I
"""Seat script: print a snapshot subtree / a series tail (read-only).
usage: s03_key.py <snapshot.json> key <dotted>
       s03_key.py <snapshot.json> series <metric_id> [from_date]
       s03_key.py <snapshot.json> tail <metric_id> <n>
"""
import json
import sys


def get(obj, dotted):
    cur = obj
    for part in dotted.split("."):
        cur = cur[part]
    return cur


def main():
    path = sys.argv[1]
    mode = sys.argv[2]
    with open(path, "r", encoding="utf-8") as fh:
        snap = json.load(fh)
    if mode == "key":
        print(json.dumps(get(snap, sys.argv[3]), ensure_ascii=False, indent=1))
    elif mode == "series":
        sid = sys.argv[3]
        frm = sys.argv[4] if len(sys.argv) > 4 else None
        s = snap["series_store"][sid]
        for d, v in zip(s["dates"], s["values"]):
            if frm is None or d >= frm:
                print(sid, d, repr(v))
    elif mode == "tail":
        sid = sys.argv[3]
        n = int(sys.argv[4])
        s = snap["series_store"][sid]
        for d, v in list(zip(s["dates"], s["values"]))[-n:]:
            print(sid, d, repr(v))
    elif mode == "facts":
        want = sys.argv[3:]
        for f in snap["facts"]:
            if not want or f.get("metric_id") in want:
                g = dict(f)
                g.pop("derived", None)
                print(json.dumps(g, ensure_ascii=False))
    elif mode == "clean":
        sid = sys.argv[3]
        s = snap["series_store_clean"][sid]
        print(sid, len(s.get("dates", [])), s["dates"][-1] if s.get("dates") else None)


if __name__ == "__main__":
    main()
