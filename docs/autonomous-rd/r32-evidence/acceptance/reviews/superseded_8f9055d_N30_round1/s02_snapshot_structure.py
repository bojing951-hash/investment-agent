#!/usr/bin/python3 -I
"""Seat script: snapshot structure overview (read-only).
usage: s02_snapshot_structure.py <snapshot.json>
"""
import json
import sys


def main():
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as fh:
        snap = json.load(fh)
    print("TOP KEYS:", list(snap.keys()))
    for k in snap:
        v = snap[k]
        if isinstance(v, dict):
            print("  %s: dict(%d) keys=%s" % (k, len(v), list(v.keys())[:40]))
        elif isinstance(v, list):
            print("  %s: list(%d) first=%r" % (k, len(v), v[0] if v else None))
        else:
            s = repr(v)
            print("  %s: %s" % (k, s[:300]))
    ss = snap.get("series_store")
    if isinstance(ss, dict):
        print("\nSERIES_STORE KEYS (%d):" % len(ss))
        for k in sorted(ss.keys()):
            v = ss[k]
            if isinstance(v, dict):
                keys = list(v.keys())
                n = None
                for kk in ("dates", "values"):
                    if kk in v and isinstance(v[kk], list):
                        n = (kk, len(v[kk]))
                        break
                d = v.get("dates") if isinstance(v.get("dates"), list) else None
                print("  %-22s keys=%s n=%s first=%s last=%s" % (
                    k, keys[:12], n, (d[0] if d else None), (d[-1] if d else None)))
            else:
                print("  %s: %r" % (k, v))


if __name__ == "__main__":
    main()
