#!/usr/bin/env python3
"""Seat-owned read-only checks (2): evidence_refs resolution by ref string against evidence_index.json,
ECB non-Wednesday observation dates, EA_HICP calendar entries detail.
Usage: python3 -I check_refs2.py <agent_judgment.json> <evidence_index.json> <release_calendar.json> <snapshot.json>
"""
import datetime as dt
import json
import sys

aj, ev, cal, snap = [json.load(open(p, "r", encoding="utf-8")) for p in sys.argv[1:5]]
refs_set = set(r["ref"] for r in ev)
kinds = {}
for r in ev:
    kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
print("evidence_index n=%d kinds=%s" % (len(ev), kinds))
print("refs in index: %s" % sorted(refs_set))
refs = []
for c in aj["l3"]["contradictions"]:
    for ref in c.get("evidence_refs", []):
        refs.append((c["id"], ref))
for m in aj["l3"]["mechanism_chains"]:
    for l in m["links"]:
        for ref in l.get("evidence_refs", []):
            refs.append(("%s/step%d" % (m["id"], l["step"]), ref))
n_ok = 0
for owner, ref in refs:
    hit = ref in refs_set
    n_ok += hit
    if not hit:
        print("UNRESOLVED %s %s" % (owner, ref))
print("n_refs=%d resolved=%d" % (len(refs), n_ok))
# facts value for each referenced fact
facts = {f["fact_id"]: f for f in snap["facts"]}
used = sorted(set(r for _, r in refs))
for ref in used:
    f = facts.get(ref)
    print("%s -> fact value=%s quality=%s obs=%s" % (ref, f.get("value") if f else None, f.get("quality_status") if f else None, f.get("observation_date") if f else None))
store = snap["series_store"]
for sid in ("ECB_MRO", "ECB_DFR"):
    s = store[sid]
    nonwed = [(d, v) for d, v in zip(s["dates"], s["values"]) if dt.date.fromisoformat(d).strftime("%a") != "Wed"]
    print("%s n=%d non-Wed obs n=%d: %s" % (sid, len(s["dates"]), len(nonwed), nonwed))
    last10 = list(zip(s["dates"], s["values"]))[-10:]
    print("   last10: %s" % last10)
for e in cal["entries"]:
    if "HICP" in e["entry_id"] or "BOJ" in e["entry_id"]:
        print(json.dumps(e, ensure_ascii=False))
print("batches=%s" % json.dumps(cal.get("batches"), ensure_ascii=False)[:1500])
print("spec=%s" % json.dumps(cal.get("spec"), ensure_ascii=False)[:1500])
