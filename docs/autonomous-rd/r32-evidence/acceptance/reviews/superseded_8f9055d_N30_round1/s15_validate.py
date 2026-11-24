#!/usr/bin/python3 -I
# -*- coding: utf-8 -*-
"""s15_validate.py -- post-write validation of the two deliverables (read-only).
usage: /usr/bin/python3 -I s15_validate.py <PROSE> <VERDICT> <agent_judgment.json>"""
import hashlib
import json
import re
import sys
from collections import Counter

PROSE, VERDICT, JPATH = sys.argv[1:4]
raw = open(VERDICT, encoding="utf-8").read()
V = json.loads(raw)
KEYS = ["seat", "reviewer", "verdict", "overall", "notes", "items", "must_fix", "counterexamples_sought",
        "recompute_points", "recompute_mismatches", "mismatch_details", "audited_at"]
assert list(V.keys()) == KEYS, list(V.keys())
assert V["seat"] == "semantic-audit-seat" and V["verdict"] in ("UPHELD", "REVISE") and V["overall"] == V["verdict"]
assert isinstance(V["recompute_points"], int) and isinstance(V["recompute_mismatches"], int) and V["mismatch_details"] == []
assert V["must_fix"] == ([] if V["verdict"] == "UPHELD" else V["must_fix"])
sev = Counter(x["severity"] for x in V["items"])
assert set(sev) <= {"MAJOR", "MINOR", "NIT"}
for x in V["items"]:
    assert list(x.keys()) == ["severity", "where", "note", "original", "fix"], list(x.keys())
    if x["severity"] == "MAJOR":
        assert x["original"] and x["fix"]
assert all(isinstance(s, str) and s.startswith("反方攻击 ") for s in V["counterexamples_sought"])
J = json.load(open(JPATH, encoding="utf-8"))
leaves = []


def walk(o):
    if isinstance(o, dict):
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)
    elif isinstance(o, str):
        leaves.append(o)


walk(J)
assert all(any(x["original"] in s for s in leaves) for x in V["items"] if x["original"])
P = open(PROSE, encoding="utf-8").read()
L = P.split("\n")
i4 = [i for i, l in enumerate(L) if l.startswith("## 4 ")][0]
i5 = [i for i, l in enumerate(L) if l.startswith("## 5 ")][0]
i6 = [i for i, l in enumerate(L) if l.startswith("## 6 ")][0]
main = [l for l in L[i4:i5] if re.match(r"^\| \d+ \| [A-O]", l)]
assert len(main) == V["recompute_points"] and all(l.rstrip().endswith("| 一致 |") for l in main), len(main)
assert [int(re.match(r"^\| (\d+) \|", l).group(1)) for l in main] == list(range(1, len(main) + 1))
assert not [l for l in L if re.match(r"^\| \d+ \|", l) and l.rstrip().endswith("| 偏离 |")], "data row marked as deviation"
sp = []
on = False
for l in L[i5:i6]:
    if l.startswith("| 序 | 二路核对项"):
        on = True
        continue
    if on:
        if l.startswith("| ") and not l.startswith("|---"):
            sp.append(l)
        elif not l.startswith("|---"):
            break
assert sp and all(l.rstrip().endswith("| 一致 |") for l in sp), len(sp)
assert V["notes"] in P and P.count(V["notes"]) == 1
assert "\n- - " not in P and "s12_preview" not in P
print("VALID verdict=%s points=%d mismatches=%d major=%d minor=%d nit=%d attacks=%d second_path_rows=%d notes_chars=%d" % (
    V["verdict"], V["recompute_points"], V["recompute_mismatches"], sev.get("MAJOR", 0), sev.get("MINOR", 0), sev.get("NIT", 0),
    len(V["counterexamples_sought"]), len(sp), len(V["notes"])))
for p in (PROSE, VERDICT):
    b = open(p, "rb").read()
    b.decode("utf-8")
    print("FILE %s bytes=%d sha256=%s" % (p, len(b), hashlib.sha256(b).hexdigest()))
