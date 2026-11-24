#!/usr/bin/python3 -I
# usage: s06_tail.py <snapshot> <metric> <from_date> <to_date>
import json, sys
snap = json.load(open(sys.argv[1], encoding="utf-8"))
mid, a, b = sys.argv[2], sys.argv[3], sys.argv[4]
s = snap["series_store"].get(mid)
if s is None:
    print(mid, "ABSENT from series_store"); sys.exit(0)
n = 0
for d, v in zip(s["dates"], s["values"]):
    if a <= d <= b:
        print("%s %s %r" % (mid, d, v)); n += 1
print("-- %s: %d obs in [%s,%s]; total %d; first %s last %s" % (mid, n, a, b, len(s["dates"]), s["dates"][0], s["dates"][-1]))
