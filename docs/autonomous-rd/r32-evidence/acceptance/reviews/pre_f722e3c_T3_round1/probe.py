#!/usr/bin/env python3
"""Seat-owned read-only structure probe.
Usage: python3 -I probe.py <report.json> <agent_judgment.json> <snapshot.json> <release_calendar.json> <metric_registry.json>
Prints key names / shapes only (no interpretation), to let recompute.py address the right keys.
"""
import json
import sys


def load(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def desc(x, maxd=2, d=0):
    pad = "  " * d
    if isinstance(x, dict):
        for k, v in x.items():
            if isinstance(v, dict):
                print("%s%s: dict(%d)" % (pad, k, len(v)))
                if d < maxd:
                    desc(v, maxd, d + 1)
            elif isinstance(v, list):
                print("%s%s: list(%d) %s" % (pad, k, len(v), (type(v[0]).__name__ if v else "")))
                if v and isinstance(v[0], dict) and d < maxd:
                    desc(v[0], maxd, d + 1)
            else:
                s = repr(v)
                print("%s%s: %s" % (pad, k, s[:110]))
    else:
        print("%s<%s>" % (pad, type(x).__name__))


rep, aj, snap, cal, reg = [load(p) for p in sys.argv[1:6]]
rp = rep["research_plan"]
print("== research_plan keys"); print(sorted(rp.keys()))
for k in ("point_values", "question_window", "turning_candidates", "us_rates_trio", "asset_moves"):
    print("== research_plan.%s" % k); desc(rp.get(k), 3)
print("== steps[*] keys / step names")
print(sorted(set(k for s in rep["steps"] for k in s.keys())))
print([s.get("step") for s in rep["steps"]])
s6 = [s for s in rep["steps"] if s.get("step") == "S6_analog"][0]
print("== S6_analog envelope"); desc(s6.get("envelope"), 3)
s5 = [s for s in rep["steps"] if s.get("step") == "S5_compare"][0]
print("== S5_compare envelope"); desc(s5.get("envelope"), 2)
print("== agent_judgment top keys"); print(sorted(aj.keys()))
print("== agent_judgment.l3"); desc(aj.get("l3"), 3)
print("== snapshot top keys"); print(sorted(snap.keys()))
print("== snapshot.facts[0]"); desc(snap["facts"][0], 2)
print("== snapshot.sources_status.ea"); desc(snap["sources_status"].get("ea"), 2)
print("== snapshot.quality"); desc(snap.get("quality"), 1)
print("== calendar top keys"); print(sorted(cal.keys())); desc(cal["entries"][0], 1)
print("== registry top keys"); print(sorted(reg.keys()))
print("== series_store sample"); desc(snap["series_store"]["VIX"], 1)
