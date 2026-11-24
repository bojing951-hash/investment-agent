#!/usr/bin/python3 -I
import json, sys, os, re
out = sys.argv[1]
for part in "ABC":
    rows = json.load(open(os.path.join(out, "recompute_points_%s.json" % part), "r", encoding="utf-8"))["rows"]
    for r in rows:
        s = json.dumps(r, ensure_ascii=False)
        if re.search(r"0\.23|0\.229|2025-10|2026-03|0\.10pp|12 ?个月|2027-01", s):
            print(part, r["id"], r["ok"], r.get("sev"), "|", str(r.get("src"))[:90], "|", str(r.get("computed"))[:60], "|", str(r.get("reported"))[:60])
