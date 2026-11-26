#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""裁决档自检(只读): schema 键序/取值域/MAJOR original+fix 非空/original 逐字在场/计数与复算表一致。
usage: /usr/bin/python3 -I s31_validate.py <agent_judgment.json> <OUT_DIR>"""
import json
import os
import sys

AJ_P, OUT = sys.argv[1:3]
with open(AJ_P, "r", encoding="utf-8") as fh:
    aj = json.load(fh)
with open(os.path.join(OUT, "recompute_table.json"), "r", encoding="utf-8") as fh:
    TBL = json.load(fh)

raw = open(os.path.join(OUT, "VERDICT-round1.json"), "rb").read()
raw.decode("utf-8")                      # 非法 UTF-8 即抛错
V = json.loads(raw.decode("utf-8"))
probs = []
KEYS = ["seat", "reviewer", "verdict", "overall", "notes", "items", "must_fix", "counterexamples_sought",
        "recompute_points", "recompute_mismatches", "mismatch_details", "audited_at"]
if list(V.keys()) != KEYS:
    probs.append("top-level keys/order: %s" % list(V.keys()))
if V["verdict"] not in ("UPHELD", "REVISE") or V["overall"] != V["verdict"]:
    probs.append("verdict/overall")
if V["seat"] != "semantic-audit-seat":
    probs.append("seat")
IKEYS = ["severity", "where", "note", "original", "fix"]
n_major = 0
for i, it in enumerate(V["items"]):
    if list(it.keys()) != IKEYS:
        probs.append("item %d keys %s" % (i, list(it.keys())))
    if it["severity"] not in ("MAJOR", "MINOR", "NIT"):
        probs.append("item %d severity" % i)
    if it["severity"] == "MAJOR":
        n_major += 1
        if not it["original"] or not it["fix"]:
            probs.append("MAJOR item %d empty original/fix" % i)
        if it["original"] == it["fix"]:
            probs.append("MAJOR item %d fix == original" % i)


def strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            for s in strings(v):
                yield s
    elif isinstance(x, list):
        for v in x:
            for s in strings(v):
                yield s


ALL = "\n".join(strings(aj))
for i, it in enumerate(V["items"]):
    if it["original"] and it["original"] not in ALL:
        probs.append("item %d original not verbatim in agent_judgment.json" % i)
if len(V["must_fix"]) != n_major:
    probs.append("must_fix %d vs MAJOR %d" % (len(V["must_fix"]), n_major))
for m in V["must_fix"]:
    if "原句: " not in m or " | 改句: " not in m:
        probs.append("must_fix format: %s" % m[:40])
    o = m.split("原句: ", 1)[1].split(" | 改句: ", 1)[0]
    if o not in ALL:
        probs.append("must_fix original not verbatim: %s" % o[:40])
if len(V["counterexamples_sought"]) < 7:
    probs.append("counterexamples < 7 (3 条 L3 + 4 环各至少一条)")
if V["recompute_points"] != TBL["points"] or V["recompute_mismatches"] != TBL["mismatches"]:
    probs.append("counts vs table")
if len(V["mismatch_details"]) != V["recompute_mismatches"]:
    probs.append("mismatch_details length")
ids = [r["id"] for r in TBL["rows"] if not r["ok"]]
if sorted(d["id"] for d in V["mismatch_details"]) != sorted(ids):
    probs.append("mismatch_details ids")
if V["recompute_points"] < 90:
    probs.append("below protocol minimum 90")
if V["audited_at"] != "2026-11-24":
    probs.append("audited_at")
prose = open(os.path.join(OUT, "PROSE-round1.md"), "r", encoding="utf-8").read()
for i, it in enumerate(V["items"]):
    if it["severity"] == "MAJOR" and (it["original"] not in prose or it["fix"] not in prose):
        probs.append("MAJOR item %d not rendered in PROSE" % i)
print("sev counts:", {s: sum(it["severity"] == s for it in V["items"]) for s in ("MAJOR", "MINOR", "NIT")})
print("points/mismatches:", V["recompute_points"], V["recompute_mismatches"], "| counter:", len(V["counterexamples_sought"]),
      "| must_fix:", len(V["must_fix"]), "| notes chars:", len(V["notes"]), "| prose chars:", len(prose))
print("PROBLEMS:", probs if probs else "none")
sys.exit(1 if probs else 0)
