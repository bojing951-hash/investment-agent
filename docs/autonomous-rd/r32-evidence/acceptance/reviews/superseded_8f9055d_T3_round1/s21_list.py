#!/usr/bin/python3 -I
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
lo, hi = int(sys.argv[2]), int(sys.argv[3])
rows = [r for r in d["rows"] if not r["duplicate"] and not r["scope_out"]]
for i, r in enumerate(rows):
    if lo <= i < hi:
        c = json.dumps(r.get("computed"), ensure_ascii=False)
        p = json.dumps(r.get("reported"), ensure_ascii=False)
        print("%d %s|%s|%s|%s%s" % (i, r["id"], str(r.get("where"))[:34], c[:70], p[:50], "" if r["ok"] else " MISMATCH"))
