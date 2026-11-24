#!/usr/bin/python3 -I
"""Citation check: print the ledger rows cited in the seat's findings, the per-category totals, the
transmission-ring verdict notes and the EA HICP monthly path (for the seat's own margin computations).
Read-only. Args: <out_dir> <agent_judgment.json> <snapshot.json> [row ids...]
"""
import json
import os
import sys

out_dir, jdp, snapp = sys.argv[1], sys.argv[2], sys.argv[3]
ids = set(sys.argv[4:])
d = json.load(open(os.path.join(out_dir, "recompute_points.json"), "r", encoding="utf-8"))
print("TOTALS", {k: d[k] for k in ("recompute_points", "recompute_mismatches", "duplicate_pair_rechecks", "duplicate_rechecks_ok", "scope_out_observations")})
for c, v in d["by_category"].items():
    print("CAT", c, v)
allids = [r["id"] for r in d["rows"]]
print("rows=%d unique_ids=%d" % (len(allids), len(set(allids))))
for r in d["rows"]:
    if (not ids and len(sys.argv) > 4) or r["id"] in ids:
        print("%s |%s| %s | %s | %s | ok=%s%s%s" % (
            r["id"], r.get("cat", "")[:8], str(r.get("where"))[:60], str(r.get("computed"))[:44], str(r.get("reported"))[:44],
            r.get("ok"), " DUP" if r.get("duplicate") else "", " SCOPE-OUT" if r.get("scope_out") else ""))
jd = json.load(open(jdp, "r", encoding="utf-8"))
rm = jd["reader_map"]
print("=== transmission")
print(json.dumps(rm["transmission"], ensure_ascii=False, indent=0))
print("=== turnings")
print(json.dumps(rm.get("turnings"), ensure_ascii=False, indent=0))
snap = json.load(open(snapp, "r", encoding="utf-8"))
for mid in ("EA_HICP_YOY", "JP_CPI_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_RATE"):
    s = snap["series_store"][mid]
    print("=== series", mid, "keys", sorted(s.keys())[:12])
    ds, vs = s["dates"], s["values"]
    print("   ", [(ds[i], vs[i]) for i in range(len(ds)) if ds[i][:4] in ("2025", "2026")])
