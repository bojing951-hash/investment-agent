#!/usr/bin/env python3
"""Seat-owned read-only probe: prints the exact values quoted in the seat's fix sentences so that
no number in PROSE/VERDICT rests on memory.
Usage: python3 -I verify_fixnums.py <agent_judgment.json> <snapshot.json> <recompute_table.tsv> <recompute_summary.json>
"""
import csv
import json
import sys

aj, snap = [json.load(open(p, "r", encoding="utf-8")) for p in sys.argv[1:3]]
print("##### turnings")
print(json.dumps(aj["reader_map"]["turnings"], ensure_ascii=False, indent=1))
print("##### C1 statement")
print(aj["l3"]["contradictions"][0]["statement"])
store = snap["series_store"]


def ser(sid):
    s = store[sid]
    return list(zip(s["dates"], s["values"]))


print("##### JP_POLICY_RATE change points (|bp|>=0.5)")
prev = None
for d, v in ser("JP_POLICY_RATE"):
    if prev is not None and v is not None and prev is not None and abs((v - prev) * 100.0) >= 0.5:
        print("  %s %.4f->%.4f (%+.1fbp)" % (d, prev, v, (v - prev) * 100.0))
    if v is not None:
        prev = v
vals = dict(ser("JP_POLICY_RATE"))
for d in ("2025-11-01", "2025-12-01", "2026-01-01", "2026-08-01", "2026-09-01", "2026-10-01"):
    print("  JP_POLICY_RATE@%s = %s" % (d, vals.get(d)))
print("##### JP_CPI_TOKYO_YOY series")
print("  " + str(ser("JP_CPI_TOKYO_YOY")))
print("##### VIX / DAX anchors")
for sid in ("VIX", "DAX"):
    s = dict(ser(sid))
    print("  %s 2026-11-13=%s 2026-10-23=%s 2026-11-20=%s 2026-11-23=%s" % (sid, s.get("2026-11-13"), s.get("2026-10-23"), s.get("2026-11-20"), s.get("2026-11-23")))
print("##### tsv header + summary keys")
with open(sys.argv[3], "r", encoding="utf-8", newline="") as fh:
    print("  " + fh.readline().rstrip("\n"))
summ = json.load(open(sys.argv[4], "r", encoding="utf-8"))
print("  " + str(sorted(summ.keys())))
print("  " + json.dumps({k: summ[k] for k in summ if k not in ("mismatch_details",)}, ensure_ascii=False))
