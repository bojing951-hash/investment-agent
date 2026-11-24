#!/usr/bin/python3 -I
# Seat script 14: verify that every quoted "original" sentence in the verdict is verbatim on the read-only face.
# usage: s14_check_originals.py <VERDICT-round1.json> <agent_judgment.json> <report.json> <MAP_REPORT.md> <FULL_REPORT.md> <report.md>
import json, sys

v = json.load(open(sys.argv[1], encoding="utf-8"))
structs = [json.load(open(p, encoding="utf-8")) for p in sys.argv[2:4]]
texts = [open(p, encoding="utf-8").read() for p in sys.argv[4:7]]
names = ["agent_judgment.json", "report.json", "MAP_REPORT.md", "FULL_REPORT.md", "report.md"]

def strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for k, x in o.items():
            yield k
            yield from strings(x)
    elif isinstance(o, list):
        for x in o:
            yield from strings(x)

strs = [list(strings(s)) for s in structs]

def where(s):
    hit = []
    for nm, ss in zip(names[:2], strs):
        if any(s in x for x in ss):
            hit.append(nm)
    for nm, t in zip(names[2:], texts):
        lines = [i for i, ln in enumerate(t.split("\n"), 1) if s in ln]
        if lines:
            hit.append("%s L%s" % (nm, ",".join(map(str, lines))))
    return hit

bad = 0
for i, it in enumerate(v["items"]):
    o = it.get("original", "")
    if not o:
        print("%d %s: (no original)" % (i, it["severity"]))
        continue
    h = where(o)
    ok = bool(h)
    bad += 0 if ok else 1
    print("%d %s: %s | %s" % (i, it["severity"], "FOUND in " + "; ".join(h) if ok else "NOT FOUND", o[:110]))
print("NOT FOUND count:", bad)

# print the transmission links 2 and 3 text for items that need verbatim quotes
aj = structs[0]
print("=== transmission links (id | keys | text fields) ===")
for l in aj["reader_map"]["transmission"]:
    print("-", l.get("chain_id"), "| keys:", list(l.keys()))
    for lk in l.get("links", []):
        print("   link", lk.get("link_id") or lk.get("step"), "| keys:", list(lk.keys()))
        for k, x in lk.items():
            if isinstance(x, str) and len(x) > 30:
                print("      %s = %s" % (k, x))
