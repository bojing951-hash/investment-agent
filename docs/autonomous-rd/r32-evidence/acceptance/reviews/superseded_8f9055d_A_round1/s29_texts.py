#!/usr/bin/python3 -I
"""Print selected judgment texts verbatim (read-only). usage: s29_texts.py <agent_judgment.json> <needle>..."""
import sys
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import json
import lib
jud = lib.load_json(sys.argv[1])
l3 = jud["l3"]
print("### M1 link[3].text\n" + l3["mechanism_chains"][0]["links"][3]["text"])
print("\n### M1 link[3].missing_link_note\n" + l3["mechanism_chains"][0]["links"][3]["missing_link_note"])
print("\n### M1 link[2].text\n" + l3["mechanism_chains"][0]["links"][2]["text"])
print("\n### M2 link[0].text\n" + l3["mechanism_chains"][1]["links"][0]["text"])
print("\n### M2 link[1].text\n" + l3["mechanism_chains"][1]["links"][1]["text"])
tr = jud["reader_map"]["transmission"]
for ci, ch in enumerate(tr):
    print("\n### transmission[%d] keys" % ci, sorted(ch.keys()))
    for li, lk in enumerate(ch["links"]):
        for k in sorted(lk.keys()):
            if k in ("causal_hypothesis",):
                continue
            print("  [%d].link[%d].%s = %s" % (ci, li, k, json.dumps(lk[k], ensure_ascii=False)[:520]))
for sc in jud["l4"]["scenarios"]:
    print("\n### scenario", sc["id"], "keys", sorted(sc.keys()), "rows", sorted(sc["rows"].keys()))
    for rk in sorted(sc["rows"].keys()):
        print("  [%s] %s" % (rk, json.dumps(sc["rows"][rk], ensure_ascii=False)[:900]))
def find(o, path, pred, out):
    if isinstance(o, dict):
        for k, v in o.items():
            find(v, path + "/" + str(k), pred, out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            find(v, path + "[%d]" % i, pred, out)
    elif isinstance(o, str):
        for nd in sys.argv[2:]:
            i = o.find(nd)
            if i >= 0:
                out.append((nd, path, o[max(0, i - 70): i + len(nd) + 90].replace("\n", " ")))
out = []
find(jud, "", None, out)
print("\n### needle contexts")
for nd, p, s in out:
    print("  [%s] %s :: ...%s..." % (nd, p, s))
