#!/usr/bin/env python3
"""Seat-owned read-only checks: evidence_refs resolvability against evidence_index.json,
ECB observation weekdays, prev-Thursday arithmetic, calendar update date.
Usage: python3 -I check_refs.py <agent_judgment.json> <evidence_index.json> <release_calendar.json> <snapshot.json>
"""
import datetime as dt
import json
import sys

aj, ev, cal, snap = [json.load(open(p, "r", encoding="utf-8")) for p in sys.argv[1:5]]
print("evidence_index type=%s" % type(ev).__name__)
if isinstance(ev, dict):
    print("evidence_index keys=%s" % sorted(ev.keys()))
    rows = ev.get("rows") or ev.get("entries") or ev.get("items") or []
else:
    rows = ev
print("n_rows=%d; row0 keys=%s" % (len(rows), sorted(rows[0].keys()) if rows else None))
print("row0=%s" % json.dumps(rows[0], ensure_ascii=False)[:700])
idx = {}
for r in rows:
    idx[(r.get("metric_id"), r.get("observation_date"))] = r
refs = []
for c in aj["l3"]["contradictions"]:
    for ref in c.get("evidence_refs", []):
        refs.append((c["id"], ref))
for m in aj["l3"]["mechanism_chains"]:
    for l in m["links"]:
        for ref in l.get("evidence_refs", []):
            refs.append(("%s/step%d" % (m["id"], l["step"]), ref))
print("n_refs=%d" % len(refs))
n_ok = 0
for owner, ref in refs:
    parts = ref.split("@")
    key = (parts[0], parts[1]) if len(parts) == 2 else (parts[0], None)
    hit = key in idx
    n_ok += hit
    row = idx.get(key, {})
    print("%s\t%s\t%s\tvalue=%s\tquality=%s" % (owner, ref, "RESOLVED" if hit else "UNRESOLVED", row.get("value"), row.get("quality_status")))
print("resolved=%d/%d" % (n_ok, len(refs)))
store = snap["series_store"]
for sid in ("ECB_MRO", "ECB_DFR"):
    wds = sorted(set(dt.date.fromisoformat(d).strftime("%a") for d in store[sid]["dates"]))
    print("%s weekdays=%s n=%d" % (sid, wds, len(store[sid]["dates"])))
for eff in ("2025-06-11", "2026-06-17", "2026-09-16"):
    e = dt.date.fromisoformat(eff)
    print("effective %s (%s) -> prev Thursday %s ; minus 6 days=%s (%s)" % (eff, e.strftime("%a"), (e - dt.timedelta(days=(e.weekday() - 3) % 7)).isoformat(), (e - dt.timedelta(days=6)).isoformat(), (e - dt.timedelta(days=6)).strftime("%a")))
print("calendar version=%s created=%s updated=%s n_entries=%d" % (cal.get("version"), cal.get("created"), cal.get("updated"), len(cal["entries"])))
print("entry ids=%s" % [e["entry_id"] for e in cal["entries"]])
print("kinds=%s" % sorted(set(str(e.get("kind")) for e in cal["entries"])))
