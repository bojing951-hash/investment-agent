#!/usr/bin/python3 -I
"""Compact dump of agent_judgment contract verification (read-only).
usage: s16_cv.py <report.json> <out.txt>"""
import json
import sys

rep = json.load(open(sys.argv[1], encoding="utf-8"))
aj = rep["agent_judgment"]
cv = aj["contract_verification"]
L = []
P = L.append
P("validation: " + json.dumps(aj.get("validation"), ensure_ascii=False))
for k in cv:
    if k in ("verdicts", "six_checks", "map_checks"):
        continue
    P("%s = %s" % (k, json.dumps(cv[k], ensure_ascii=False)[:1500]))
P("")
P("== verdicts (%d)" % len(cv["verdicts"]))
for v in cv["verdicts"]:
    P("%s | %s | tok=%s | %s | val=%s | exp=%s | %s | refs=%s | %s" % (
        v.get("item"), v.get("claim_type"), v.get("token"), v.get("metric"), v.get("value"), v.get("expected"),
        v.get("status"), ",".join(v.get("evidence_refs") or []), (v.get("note") or "")[:230]))
P("")
P("== six_checks")
for v in cv.get("six_checks") or []:
    P(json.dumps(v, ensure_ascii=False)[:1200])
P("")
P("== map_checks")
for v in cv.get("map_checks") or []:
    P(json.dumps(v, ensure_ascii=False)[:1500])
P("")
P("== reader_map_faces keys")
for k in aj.get("reader_map_faces") or {}:
    s = json.dumps(aj["reader_map_faces"][k], ensure_ascii=False)
    P("%s :: %s" % (k, s[:900] + ("...(%d chars)" % len(s) if len(s) > 900 else "")))
P("")
P("== semantic_review")
P(json.dumps(rep.get("semantic_review"), ensure_ascii=False)[:1500])
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(L) + "\n")
print("lines=%d" % len(L))
