#!/usr/bin/python3 -I
"""Read-only probe #5: region from_to texts + alias entries.
Args: <agent_judgment.json> <text_consistency.py>
"""
import ast
import json
import sys

jd = json.load(open(sys.argv[1], "r", encoding="utf-8"))
for r in jd["reader_map"]["regions"]:
    print("==", r["region"])
    print(r["from_to"])
    print("   keys:", list(r.keys()))
    for e in r.get("anchor_echo", []):
        print("   echo", e)
t = open(sys.argv[2], "r", encoding="utf-8").read()
i0 = t.index("ALIASES = {")
i1 = t.index("\n}\n", i0)
al = ast.literal_eval(t[i0 + len("ALIASES = "):i1 + 2])
for k in ("ECB_DFR", "JP_POLICY_RATE", "CPI", "CORE_CPI", "CN_CPI_YOY", "ECB_MRO", "JP_CPI_YOY", "EA_HICP_YOY"):
    print(k, al.get(k))
print("n aliases", len(al))
print("== transmission links keys", list(jd["reader_map"]["transmission"][0].keys()))
print("== reader_map keys", list(jd["reader_map"].keys()))
