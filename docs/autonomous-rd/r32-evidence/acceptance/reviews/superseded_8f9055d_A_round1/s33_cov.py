#!/usr/bin/python3 -I
"""C2 explanation-B coverage figures vs engine face. usage: s33_cov.py <report.json>"""
import sys
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import json
import lib
rep = lib.load_json(sys.argv[1])
s6 = rep["steps"][61]
assert s6["step"] == "S6_analog"
sv = s6["envelope"]["data"]["state_vector"]
N = [0, 0]
def cmp(tag, mine, claim, nd=2):
    N[0] += 1
    ok = abs(round(mine, nd) - round(claim, nd)) <= 1e-9
    N[1] += 0 if ok else 1
    print("   %-60s mine=%-14s claim=%-10s %s" % (tag, mine, claim, "OK" if ok else "<<< MISMATCH"))
print("### C2 explanation B: state-vector coverage (report.json /steps[61]/envelope/data/state_vector/<dim>/coverage)")
cmp("growth coverage (judgment 0.17)", sv["growth"]["coverage"], 0.17)
cmp("inflation coverage (judgment 0.33)", sv["inflation"]["coverage"], 0.33)
cmp("credit coverage (judgment 0.5)", sv["credit"]["coverage"], 0.5)
top = s6["envelope"]["data"]["top"]
miss = [(t["candidate_month"], sorted((t.get("missing_features") or {}).keys())) for t in top]
print("   missing features per candidate (info):", miss)
n_credit_missing = sum(1 for t in top if any(k.startswith("HY_") for k in (t.get("missing_features") or {})))
cmp("credit features missing in majority of candidate months", n_credit_missing > len(top) / 2, True)
print("   analog anchor_month / feature_window_months (info):", s6["envelope"]["data"].get("anchor_month"), s6["envelope"]["data"].get("feature_window_months"))
for i, t in enumerate(top):
    print("   top[%d] (info): month=%s rank=%s distance=%s pct=%s n_missing=%s cluster_members=%s" % (i, t.get("candidate_month"), t.get("rank"), t.get("distance"), t.get("distance_percentile"), t.get("n_missing"), t.get("cluster_members")))
print("POINTS=%d MISMATCHES=%d" % (N[0], N[1]))
