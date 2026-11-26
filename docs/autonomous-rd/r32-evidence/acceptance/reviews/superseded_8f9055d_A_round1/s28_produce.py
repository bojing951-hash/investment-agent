#!/usr/bin/python3 -I
"""Print the envelope's work-order text (produce / then / discipline / contract spec). usage: s28_produce.py <AGENT_SEAT_ENVELOPE.json>"""
import sys
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import json
import lib
env = lib.load_json(sys.argv[1])
for k in ("produce", "then", "discipline", "read_first"):
    v = env.get(k)
    if isinstance(v, list):
        for i, x in enumerate(v):
            print("[%s %d] %s" % (k, i, x))
            print()
    else:
        print("[%s] %s" % (k, v))
        print()
rc = env["reader_map_contract"]
for k, v in rc.items():
    if k == "engine_faces":
        continue
    print("[reader_map_contract.%s] %s" % (k, json.dumps(v, ensure_ascii=False)[:2500]))
    print()
ef = rc["engine_faces"]
for k in ("point_anchors", "ex_post_offsets", "point_values_absent", "policy_doc_facts", "dimension_gaps"):
    print("[engine_faces.%s] %s" % (k, json.dumps(ef.get(k), ensure_ascii=False)[:1200]))
    print()
