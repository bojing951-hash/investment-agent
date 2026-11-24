#!/usr/bin/python3 -I
"""Dump ECB_DFR / ECB_MRO series around the change points and count all scenario-row refs.
usage: s18_ecbdfr.py <snapshot.json> <agent_judgment.json>"""
import sys
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import json
import lib
snap = lib.load_json(sys.argv[1])
jud = lib.load_json(sys.argv[2])
st = lib.Store(snap)
for mid in ("ECB_DFR", "ECB_MRO"):
    ser = st.series(mid)
    print(mid, "n=", len(ser), "first=", ser[0], "last=", ser[-1])
    # change points + last obs of each half-year
    prev = None
    ch = []
    for d, v in ser:
        if v != prev:
            ch.append((d, v))
            prev = v
    print("  change points (last 12):", ch[-12:])
    for probe in ("2026-06-16", "2026-06-17", "2026-09-15", "2026-09-16", "2025-11-23", "2025-11-20", "2026-08-19"):
        print("  on_or_before", probe, st.on_or_before(mid, probe))
    inwin = st.in_range(mid, "2025-11-24", "2026-11-23")
    print("  window obs:", inwin)
# scenario row refs
tot = 0
for sc in jud["l4"]["scenarios"]:
    n = 0
    for rk, rv in (sc.get("rows") or {}).items():
        refs = (rv or {}).get("evidence_refs") if isinstance(rv, dict) else None
        if refs:
            n += len(refs)
            print(sc["id"], rk, len(refs), refs)
    print(sc["id"], "total refs", n)
    tot += n
print("total scenario refs", tot)
# policy window path claims (quality note: policy-basis disclosure)
qn = jud.get("quality_gate_notes")
print("quality notes:", json.dumps(qn, ensure_ascii=False)[:3000])
