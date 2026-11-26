#!/usr/bin/python3 -I
"""Keyword-in-context fragments at the locations cited in items' `where` labels (to confirm each cited
location really carries the matter of the item). Read-only.
Args: <agent_judgment.json>
"""
import json
import re
import sys

jd = json.load(open(sys.argv[1], "r", encoding="utf-8"))
rm = jd["reader_map"]
tr = rm["transmission"][0]
C = jd["l3"]["contradictions"]
Q = jd["quality_gate_notes"]


def ctx(text, kw, w=70, maxn=6):
    out = []
    for m in list(re.finditer(kw, text))[:maxn]:
        out.append("…" + text[max(0, m.start() - w):m.end() + w].replace("\n", " ") + "…")
    return out or ["   (no hit)"]


def show(label, text, kw, w=70, maxn=6):
    print("##", label, "| keyword:", kw)
    for x in ctx(text, kw, w, maxn):
        print("   ", x)


print("=== M-1 (ECB staleness caliber) cited locations")
show("regions[0].from_to", rm["regions"][0]["from_to"], r"68|degraded|DEGRADED|新鲜度")
show("quality_gate_notes[4]", Q[4], r"68|degraded|DEGRADED|新鲜度", 50, 3)
print("=== M-3 (EA HICP publication) cited locations")
show("regions[0].from_to", rm["regions"][0]["from_to"], r"11-16|发布")
show("headline_conclusion", rm["headline_conclusion"], r"11-16|发布")
print("=== N-2 ('约' before 1.25%) cited locations")
show("regions[1].from_to", rm["regions"][1]["from_to"], r"约? ?1\.25", 30)
show("C2 statement", C[1]["statement"], r"约? ?1\.25", 30)
show("headline_conclusion", rm["headline_conclusion"], r"约? ?1\.25", 30)
print("=== N-7 (JP_POLICY_RATE WARN / publication) cited locations")
show("C2 statement", C[1]["statement"], r"1\.227|WARN|发布时间", 50)
show("quality_gate_notes[4]", Q[4], r"WARN|发布时间|11-05", 60, 4)
show("C1 statement", C[0]["statement"], r"WARN", 60, 4)
print("=== N-6 cited locations")
show("regions[1].from_to", rm["regions"][1]["from_to"], r"快照序列面|L1|东京", 50)
print("=== M-4 / M-2 cited locations")
show("regions[1].from_to", rm["regions"][1]["from_to"], r"收紧|推断|月均", 50, 5)
print("=== ring-3 verdict_note tail")
t = tr["links"][2]["verdict_note"]
print("len", len(t))
print(t[-420:])
print("=== ring-2 verdict_note tail")
t = tr["links"][1]["verdict_note"]
print("len", len(t))
print(t[-420:])
print("=== link 3 text (M1 环 3) full")
print(jd["l3"]["mechanism_chains"][0]["links"][2]["text"])
print("=== link 3 missing_link_note")
print(jd["l3"]["mechanism_chains"][0]["links"][2].get("missing_link_note"))
