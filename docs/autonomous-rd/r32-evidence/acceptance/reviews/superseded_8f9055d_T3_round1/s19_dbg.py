#!/usr/bin/python3 -I
import json, sys, os, re
out = sys.argv[1]
for part in "ABCD":
    rows = json.load(open(os.path.join(out, "recompute_points_%s.json" % part), "r", encoding="utf-8"))["rows"]
    for r in rows:
        s = json.dumps(r, ensure_ascii=False)
        if re.search(r"84\.5|19\.45|38\.87|24\.7|69\.66|37\.93", s):
            print(part, r["id"], r["ok"], "|", str(r.get("src"))[:80], "|", str(r.get("computed"))[:50], "|", str(r.get("reported"))[:50], "|", str(r.get("lit"))[:60])
