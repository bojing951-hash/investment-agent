#!/usr/bin/python3 -I
"""Recompute state-vector dimension coverage quoted in C2 explanation B (growth 0.17 / inflation 0.33 / credit 0.5).
usage: s32_coverage.py <report.json>"""
import sys
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import json
import lib
rep = lib.load_json(sys.argv[1])
steps = rep["steps"]
s6 = None
for i, s in enumerate(steps):
    if isinstance(s, dict) and "analog" in json.dumps(s.get("name") or s.get("id") or s.get("step") or "").lower():
        s6 = s; print("step index", i, "name", s.get("name"), "keys", sorted(s.keys())[:20])
data = s6["data"] if "data" in s6 else s6
print("data keys:", sorted(data.keys()))
sv = data.get("state_vector") or data.get("envelope", {}).get("data", {}).get("state_vector")
sv = sv or s6.get("envelope", {}).get("data", {}).get("state_vector")
print("state_vector dims:", sorted(sv.keys()))
for dim in sorted(sv.keys()):
    d = sv[dim]
    print("==", dim, "keys", sorted(d.keys()))
    feats = d.get("features") or {}
    tot_w = 0.0; has_w = 0.0; n = 0; nhas = 0
    for f, fd in feats.items():
        w = fd.get("w_norm", fd.get("weight"))
        v = fd.get("value")
        tot_w += w or 0; n += 1
        if v is not None:
            has_w += w or 0; nhas += 1
        print("   %-26s value=%-22s w_norm=%s" % (f, v, w))
    print("   -> coverage by count = %d/%d = %.2f ; by weight = %.2f" % (nhas, n, nhas / n if n else 0, has_w / tot_w if tot_w else 0))
    for k in d:
        if k != "features":
            print("   [%s] %s" % (k, json.dumps(d[k], ensure_ascii=False)[:300]))
for k in sorted(data.keys()):
    if k not in ("state_vector", "top"):
        print("[data.%s] %s" % (k, json.dumps(data[k], ensure_ascii=False)[:500]))
