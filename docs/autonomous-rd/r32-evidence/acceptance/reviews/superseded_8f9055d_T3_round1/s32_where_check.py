#!/usr/bin/python3 -I
"""Where-path check: every path cited in an item's `where` must resolve in agent_judgment.json, and the
item's `original` must occur verbatim in at least one of the resolved locations. A bare field name written
after " 与 " is resolved relative to the parent of the preceding full path.
Also prints the structure fragments the where labels refer to (ring / link numbering).
Read-only. Args: <agent_judgment.json> <out_dir>
"""
import json
import os
import re
import sys

jd = json.load(open(sys.argv[1], "r", encoding="utf-8"))
out_dir = sys.argv[2]
v = json.load(open(os.path.join(out_dir, "VERDICT-round1.json"), "r", encoding="utf-8"))
PAT = re.compile(r"((?:l3|l4|reader_map|quality_gate_notes|agent_declaration)(?:\.[A-Za-z_][A-Za-z0-9_]*|\[\d+\])+)")
TOK = re.compile(r"\.([A-Za-z_][A-Za-z0-9_]*)|\[(\d+)\]")
BARE = re.compile(r"与 ([a-z_]+)")


def resolve(path):
    o = jd
    for key, idx in TOK.findall("." + path):
        if key:
            if not isinstance(o, dict) or key not in o:
                return None
            o = o[key]
        else:
            if not isinstance(o, list) or int(idx) >= len(o):
                return None
            o = o[int(idx)]
    return o


def strings(o):
    if isinstance(o, str):
        return [o]
    if isinstance(o, dict):
        return [s for x in o.values() for s in strings(x)]
    if isinstance(o, list):
        return [s for x in o for s in strings(x)]
    return []


bad = 0
for it in v["items"]:
    paths = PAT.findall(it["where"])
    bares = BARE.findall(it["where"])
    if bares and paths:
        parent = re.sub(r"\.[A-Za-z_][A-Za-z0-9_]*$", "", paths[-1])  # same object as the preceding path
        paths += [parent + "." + b for b in bares]
    orig = re.sub(r"^…", "", it["original"])
    print("==", it["severity"], it["where"][:120])
    any_hit = False
    for p in paths:
        o = resolve(p)
        if o is None:
            print("   PATH UNRESOLVED:", p)
            bad += 1
            continue
        ss = strings(o)
        hit = any(orig in s for s in ss)
        any_hit = any_hit or hit
        print("   %-58s type=%-5s strings=%-3d original_found=%s" % (p, type(o).__name__, len(ss), hit))
    if not paths or not any_hit:
        print("   !! no path / original not found in any cited location")
        bad += 1
    if not it["fix"]:
        print("   !! empty fix")
        bad += 1

print("=== structure fragments behind the where labels")
ch = jd["l3"]["mechanism_chains"][0]
print("mechanism_chains[0].links:", len(ch["links"]), "| chain id:", ch.get("chain_id") or ch.get("id"))
for i, lk in enumerate(ch["links"]):
    print("  links[%d] step=%s text: %s" % (i, lk.get("step"), (lk.get("text") or "")[:70]))
tr = jd["reader_map"]["transmission"][0]
print("transmission[0].links:", len(tr["links"]), "| title:", tr.get("title"))
for i, lk in enumerate(tr["links"]):
    print("  links[%d] face_off_verdict=%s | %s" % (i, lk.get("face_off_verdict"), str(lk.get("causal_hypothesis"))[:60]))
for i, c in enumerate(jd["l3"]["contradictions"]):
    print("  contradictions[%d] id=%s" % (i, c.get("contradiction_id") or c.get("id")))
print("  ring-3 verdict_note (full):", tr["links"][2].get("verdict_note"))
print("WHERE-CHECK", "PASS" if not bad else "FAIL(%d)" % bad)
