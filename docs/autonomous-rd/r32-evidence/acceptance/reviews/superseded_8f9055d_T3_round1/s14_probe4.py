#!/usr/bin/python3 -I
"""Read-only probe #4: exact judgment texts needed as literals for part C.
Args: <agent_judgment.json>
"""
import json
import re
import sys

jd = json.load(open(sys.argv[1], "r", encoding="utf-8"))
print("==== quality_gate_notes")
for i, q in enumerate(jd["quality_gate_notes"]):
    print("[%d] %s" % (i, q))
    print()
print("==== competing explanations")
for c in jd["l3"]["contradictions"]:
    print(c["id"], json.dumps(c["competing_explanations"], ensure_ascii=False))
print("==== agent_declaration")
print(json.dumps(jd["agent_declaration"], ensure_ascii=False))
print("==== arabic numerals near non-alias metrics")
pat = re.compile(r"(ECB_MRO|ECB_DFR|JP_POLICY_RATE|EA_HICP_YOY|JP_CPI_YOY|MRO|DFR|HICP|全国 ?CPI|政策目标|月均)[^。；;]{0,40}?(\d+(?:\.\d+)?%?)")


def walk(o, path):
    if isinstance(o, str):
        for m in pat.finditer(o):
            s = max(0, m.start() - 25)
            print("%s | ...%s..." % (path, o[s:m.end() + 15].replace("\n", " ")))
    elif isinstance(o, dict):
        for k, v in o.items():
            walk(v, "%s.%s" % (path, k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, "%s[%d]" % (path, i))


walk(jd, "$")
