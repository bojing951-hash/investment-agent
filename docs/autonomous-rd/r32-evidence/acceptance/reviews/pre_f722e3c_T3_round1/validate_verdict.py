#!/usr/bin/env python3
"""Seat-owned validator: checks VERDICT-round1.json is legal JSON and carries every key required by the
protocol §6 schema (types, enum values, MAJOR original/fix presence, count consistency with PROSE).
Usage: python3 -I validate_verdict.py <VERDICT-round1.json> <PROSE-round1.md> <recompute_summary.json>
"""
import json
import re
import sys

VP, PP, SP = sys.argv[1:4]
with open(VP, "rb") as fh:
    raw = fh.read()
v = json.loads(raw.decode("utf-8"))  # raises on illegal JSON
s = json.load(open(SP, "r", encoding="utf-8"))
errs = []
REQ = ["seat", "reviewer", "verdict", "overall", "notes", "items", "must_fix", "counterexamples_sought",
       "recompute_points", "recompute_mismatches", "mismatch_details", "audited_at"]
for k in REQ:
    if k not in v:
        errs.append("missing key %s" % k)
extra = sorted(set(v) - set(REQ))
if extra:
    errs.append("unexpected top-level keys %s" % extra)
if v.get("seat") != "semantic-audit-seat":
    errs.append("seat")
if v.get("verdict") not in ("UPHELD", "REVISE") or v.get("overall") != v.get("verdict"):
    errs.append("verdict/overall")
if v.get("reviewer") != "independent-zero-context-seat-r32-t3-round1":
    errs.append("reviewer")
if not isinstance(v.get("notes"), str) or not v["notes"].strip():
    errs.append("notes")
if not isinstance(v.get("audited_at"), str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v["audited_at"]):
    errs.append("audited_at")
items = v.get("items")
if not isinstance(items, list) or not items:
    errs.append("items")
    items = []
cnt = {"MAJOR": 0, "MINOR": 0, "NIT": 0}
for i, it in enumerate(items):
    for k in ("severity", "where", "note", "original", "fix"):
        if k not in it:
            errs.append("items[%d] missing %s" % (i, k))
    sev = it.get("severity")
    if sev not in cnt:
        errs.append("items[%d] severity %r" % (i, sev))
        continue
    cnt[sev] += 1
    if not isinstance(it.get("where"), str) or not it["where"].strip() or not isinstance(it.get("note"), str) or not it["note"].strip():
        errs.append("items[%d] where/note empty" % i)
    if sev == "MAJOR" and not (isinstance(it.get("original"), str) and it["original"].strip() and isinstance(it.get("fix"), str) and it["fix"].strip()):
        errs.append("items[%d] MAJOR without original/fix" % i)
mf = v.get("must_fix")
if not isinstance(mf, list) or len(mf) != cnt["MAJOR"] or (v.get("verdict") == "UPHELD" and mf):
    errs.append("must_fix count %s vs MAJOR %s" % (len(mf) if isinstance(mf, list) else None, cnt["MAJOR"]))
ce = v.get("counterexamples_sought")
if not isinstance(ce, list) or not ce or not all(isinstance(x, str) and "→" in x for x in ce):
    errs.append("counterexamples_sought")
for k in ("recompute_points", "recompute_mismatches"):
    if not isinstance(v.get(k), int) or isinstance(v.get(k), bool):
        errs.append("%s not int" % k)
if v.get("recompute_points") != s["recompute_points"] or v.get("recompute_mismatches") != s["recompute_mismatches"]:
    errs.append("counts differ from recompute_summary.json")
if not isinstance(v.get("mismatch_details"), list) or len(v["mismatch_details"]) != v.get("recompute_mismatches"):
    errs.append("mismatch_details length")
if v.get("recompute_points") < 40:
    errs.append("coverage below protocol minimum 40")
if v.get("verdict") == "REVISE" and cnt["MAJOR"] == 0:
    errs.append("REVISE without MAJOR")
if v.get("verdict") == "UPHELD" and cnt["MAJOR"]:
    errs.append("UPHELD with MAJOR")
# every MAJOR original must occur verbatim in PROSE too
prose = open(PP, "r", encoding="utf-8").read()
for it in items:
    if it.get("severity") == "MAJOR" and it.get("original") and ("「%s」" % it["original"]) not in prose:
        errs.append("MAJOR original not quoted in PROSE: %s" % it["original"][:30])
print("json_ok=True bytes=%d keys=%s" % (len(raw), sorted(v.keys())))
print("verdict=%s overall=%s items MAJOR=%d MINOR=%d NIT=%d must_fix=%d counterexamples=%d points=%d mismatches=%d mismatch_details=%d audited_at=%s notes_chars=%d" % (
    v.get("verdict"), v.get("overall"), cnt["MAJOR"], cnt["MINOR"], cnt["NIT"], len(mf) if isinstance(mf, list) else -1, len(ce) if isinstance(ce, list) else -1,
    v.get("recompute_points", -1), v.get("recompute_mismatches", -1), len(v.get("mismatch_details", [])), v.get("audited_at"), len(v.get("notes", ""))))
print("prose_chars=%d prose_lines=%d" % (len(prose), prose.count("\n")))
if errs:
    print("VALIDATION FAILED:")
    for e in errs:
        print("  - %s" % e)
    sys.exit(1)
print("VALIDATION PASSED: legal JSON, all protocol keys present, counts consistent")
