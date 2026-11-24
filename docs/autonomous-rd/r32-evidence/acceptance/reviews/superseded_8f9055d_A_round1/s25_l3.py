#!/usr/bin/python3 -I
"""Compact L3/L4/transmission structure dump (read-only). usage: s25_l3.py <agent_judgment.json>"""
import sys
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import json
import lib
jud = lib.load_json(sys.argv[1])
l3 = jud["l3"]
c0 = l3["contradictions"][0]
print("contradiction keys:", sorted(c0.keys()))
for k in sorted(c0.keys()):
    if k in ("competing_explanations", "evidence_refs"):
        continue
    print("  [%s] %s" % (k, json.dumps(c0[k], ensure_ascii=False)[:700]))
for i, e in enumerate(c0["competing_explanations"]):
    print("  C1 expl[%d]: %s" % (i, e))
for ci in (1, 2):
    c = l3["contradictions"][ci]
    print("## contradiction[%d]" % ci)
    for k in sorted(c.keys()):
        if k in ("competing_explanations", "evidence_refs", "statement"):
            continue
        print("  [%s] %s" % (k, json.dumps(c[k], ensure_ascii=False)[:600]))
    for i, e in enumerate(c["competing_explanations"]):
        print("  expl[%d]: %s" % (i, e[:520]))
ch = l3["mechanism_chains"][0]
print("## chain keys:", sorted(ch.keys()))
lk = ch["links"][0]
print("link keys:", sorted(lk.keys()))
for ci, ch in enumerate(l3["mechanism_chains"]):
    for k in sorted(ch.keys()):
        if k != "links":
            print("  chain[%d].%s = %s" % (ci, k, json.dumps(ch[k], ensure_ascii=False)[:500]))
    for li, lk in enumerate(ch["links"]):
        print("  -- chain[%d].link[%d]" % (ci, li))
        for k in sorted(lk.keys()):
            if k == "text":
                continue
            print("     [%s] %s" % (k, json.dumps(lk[k], ensure_ascii=False)[:420]))
