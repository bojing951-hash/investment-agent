#!/usr/bin/python3 -I
"""Dump where evidence_refs live in l4 scenarios. usage: s17_l4refs.py <agent_judgment.json>"""
import json, sys
jud = json.load(open(sys.argv[1], encoding="utf-8"))
l4 = jud.get("l4", {})
print("l4 keys:", sorted(l4.keys()))
for sc in l4.get("scenarios") or []:
    print("scenario keys:", sorted(sc.keys()))
    rows = sc.get("rows") or {}
    print("  rows keys:", sorted(rows.keys()))
    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, path + "/" + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, path + "[%d]" % i)
        elif isinstance(o, str) and ("@" in o) and len(o) < 60:
            print("    ref", path, "=", o)
    walk(sc, "")
    break
tot = 0
for sc in l4.get("scenarios") or []:
    refs = sc.get("evidence_refs") or []
    print(sc.get("id") or sc.get("scenario_id"), "n_refs=", len(refs), refs)
    tot += len(refs)
print("total scenario refs:", tot)
