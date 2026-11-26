#!/usr/bin/python3 -I
"""Print S6_analog / S8 step envelope shapes. Args: <report.json> [stepname...]"""
import json
import sys


def shape(o, depth=0, maxdepth=4, pre=""):
    pad = "  " * depth
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (dict, list)) and depth < maxdepth:
                print("%s%s: %s[%d]" % (pad, k, type(v).__name__, len(v)))
                shape(v, depth + 1, maxdepth)
            else:
                print("%s%s: %s" % (pad, k, json.dumps(v, ensure_ascii=False)[:160]))
    elif isinstance(o, list):
        for i, v in enumerate(o[:2]):
            if isinstance(v, (dict, list)) and depth < maxdepth:
                print("%s[%d]:" % (pad, i))
                shape(v, depth + 1, maxdepth)
            else:
                print("%s[%d]: %s" % (pad, i, json.dumps(v, ensure_ascii=False)[:160]))


d = json.load(open(sys.argv[1], "r", encoding="utf-8"))
names = sys.argv[2:] or ["S6_analog"]
for st in d["steps"]:
    if st.get("step") in names:
        print("== step", st.get("step"), "ok=", st.get("ok"), "keys=", list(st.keys()))
        shape(st.get("envelope"), 0, 5)
