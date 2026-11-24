#!/usr/bin/python3 -I
"""Envelope outline: work-order faces and required sections vs judgment presence (read-only).
usage: s27_envelope.py <AGENT_SEAT_ENVELOPE.json> <agent_judgment.json> <question_verbatim.txt>"""
import sys
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import json
import lib
env = lib.load_json(sys.argv[1])
jud = lib.load_json(sys.argv[2])
print("question:", open(sys.argv[3], encoding="utf-8").read().strip()[:400])
def outline(o, p="", depth=0, maxd=3):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (dict, list)) and depth < maxd:
                n = len(v)
                print("%s%s (%s %d)" % ("  " * depth, k, type(v).__name__, n))
                outline(v, p + "/" + k, depth + 1, maxd)
            else:
                s = json.dumps(v, ensure_ascii=False)
                print("%s%s = %s" % ("  " * depth, k, s[:260]))
    elif isinstance(o, list) and o and depth < maxd:
        outline(o[0], p + "[0]", depth + 1, maxd)
outline(env)
print("## judgment top-level presence")
for k in ("l3", "l4", "reader_map", "quality_gate_notes", "agent_declaration", "schema_version"):
    print("  ", k, k in jud)
rm = jud["reader_map"]
print("  reader_map keys:", sorted(rm.keys()))
for k in sorted(rm.keys()):
    v = rm[k]
    print("    %s: %s len=%s" % (k, type(v).__name__, len(v) if hasattr(v, "__len__") else "-"))
print("  regions ids:", [(r.get("region") or r.get("id") or r.get("name")) for r in rm.get("regions") or []])
print("  l3 keys:", sorted(jud["l3"].keys()), "n contradictions", len(jud["l3"]["contradictions"]), "n chains", len(jud["l3"]["mechanism_chains"]))
print("  l4 scenarios:", [s.get("id") for s in jud["l4"]["scenarios"]])
