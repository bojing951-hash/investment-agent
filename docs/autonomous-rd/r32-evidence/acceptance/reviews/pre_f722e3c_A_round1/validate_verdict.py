#!/usr/bin/env python3
"""Validate VERDICT-round1.json: valid UTF-8 JSON + all protocol-required keys + schema constraints.
usage: python3 -I validate_verdict.py <VERDICT-round1.json>
"""
import json
import sys

raw = open(sys.argv[1], "rb").read()
raw.decode("utf-8")  # raises if not valid UTF-8
v = json.loads(raw)
REQ = ["seat", "reviewer", "verdict", "overall", "notes", "items", "must_fix", "counterexamples_sought",
       "recompute_points", "recompute_mismatches", "mismatch_details", "audited_at"]
missing = [k for k in REQ if k not in v]
assert not missing, "missing keys: %s" % missing
assert v["seat"] == "semantic-audit-seat", v["seat"]
assert v["reviewer"] == "independent-zero-context-seat-r32-a-round1", v["reviewer"]
assert v["verdict"] in ("UPHELD", "REVISE") and v["overall"] in ("UPHELD", "REVISE")
assert v["verdict"] == v["overall"]
assert isinstance(v["notes"], str) and len(v["notes"]) > 20
assert isinstance(v["items"], list) and v["items"]
sev = {"MAJOR": 0, "MINOR": 0, "NIT": 0}
for it in v["items"]:
    for k in ("severity", "where", "note", "original", "fix"):
        assert k in it, "item missing %s: %s" % (k, it)
    assert it["severity"] in sev, it["severity"]
    sev[it["severity"]] += 1
    assert it["where"] and it["note"]
    if it["severity"] == "MAJOR":
        assert it["original"].strip() and it["fix"].strip(), "MAJOR without original/fix: %s" % it["where"]
assert isinstance(v["must_fix"], list)
assert len(v["must_fix"]) == sev["MAJOR"], (len(v["must_fix"]), sev)
assert all(isinstance(x, str) and x.strip() for x in v["must_fix"])
assert (sev["MAJOR"] == 0) == (v["verdict"] == "UPHELD"), "verdict/severity inconsistent"
assert isinstance(v["counterexamples_sought"], list) and len(v["counterexamples_sought"]) >= 5
assert all(isinstance(x, str) and "→" in x for x in v["counterexamples_sought"])
for tag in ("C1", "C2", "C3", "M1", "M2"):
    assert any(("反方攻击 %s" % tag) in x for x in v["counterexamples_sought"]), "no counter-attack for %s" % tag
assert isinstance(v["recompute_points"], int) and v["recompute_points"] >= 60
assert isinstance(v["recompute_mismatches"], int)
assert isinstance(v["mismatch_details"], list) and len(v["mismatch_details"]) == v["recompute_mismatches"]
assert v["audited_at"] == "2026-11-23"
print("VALID JSON (UTF-8); keys ok=%d; verdict=%s; points=%d mismatches=%d; MAJOR=%d MINOR=%d NIT=%d; must_fix=%d; counter=%d" % (
    len(REQ), v["verdict"], v["recompute_points"], v["recompute_mismatches"], sev["MAJOR"], sev["MINOR"], sev["NIT"],
    len(v["must_fix"]), len(v["counterexamples_sought"])))
