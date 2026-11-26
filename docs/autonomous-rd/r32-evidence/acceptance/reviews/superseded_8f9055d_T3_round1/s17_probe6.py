#!/usr/bin/python3 -I
"""Read-only probe #6: exact headline / turnings / scenarios / TL link texts + vintage keyword scan.
Args: <agent_judgment.json> <metric_registry.json>
"""
import json
import re
import sys

jd = json.load(open(sys.argv[1], "r", encoding="utf-8"))
reg = json.load(open(sys.argv[2], "r", encoding="utf-8"))
rm = jd["reader_map"]
print("==== headline")
print(rm["headline_conclusion"])
print("==== turnings")
for i, t in enumerate(rm["turnings"]):
    print("-- T%d" % (i + 1))
    for k, v in t.items():
        print("   %s: %s" % (k, v))
print("==== turning_supplement")
print(rm.get("turning_supplement"))
print("==== scenarios")
for s in jd["l4"]["scenarios"]:
    print("--", s.get("id"), [k for k in s.keys() if k != "rows"])
    for k, v in s["rows"].items():
        print("   %s: %s" % (k, v))
print("==== TL links")
for i, l in enumerate(rm["transmission"][0]["links"]):
    print("-- TL%d" % (i + 1))
    for k, v in l.items():
        print("   %s: %s" % (k, v))
print("==== transmission top", {k: v for k, v in rm["transmission"][0].items() if k != "links"})
print("==== vintage keyword scan")
pat = re.compile(r"事后|修订|首发|速报|终值| vintage|最新值")
def walk(o, path):
    if isinstance(o, str):
        for m in pat.finditer(o):
            s = max(0, m.start() - 30)
            print("%s | ...%s..." % (path, o[s:m.end() + 30].replace("\n", " ")))
    elif isinstance(o, dict):
        for k, v in o.items():
            walk(v, "%s.%s" % (path, k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, "%s[%d]" % (path, i))
walk({k: v for k, v in jd.items() if k != "contract_verification"}, "$")
for m in reg["metrics"]:
    if m.get("metric_id") in ("JP_CPI_YOY",):
        print("==== registry JP_CPI_YOY.calc:", m.get("calc"))
        print("==== registry JP_CPI_YOY keys:", list(m.keys()))
