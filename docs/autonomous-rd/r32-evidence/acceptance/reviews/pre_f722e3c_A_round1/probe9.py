#!/usr/bin/env python3
"""Probe facts.derived for HY_OAS / BEI_10Y / BRENT_F / USDJPY + agent_judgment.contract_verification (read-only).

usage: python3 -I probe9.py <snapshot.json> <report.json> <out.txt>
"""
import json
import sys

snap_p, rep_p, out_p = sys.argv[1:4]
out = open(out_p, "w", encoding="utf-8")


def w(s=""):
    out.write(s + "\n")


def pj(obj, indent=1, limit=3000):
    w(json.dumps(obj, ensure_ascii=False, indent=indent)[:limit])


snap = json.load(open(snap_p, encoding="utf-8"))
for f in snap["facts"]:
    if f["metric_id"] in ("HY_OAS", "BEI_10Y", "BRENT_F", "USDJPY", "VIX", "DAX", "JP_POLICY_RATE"):
        pj({k: f.get(k) for k in ("fact_id", "value", "observation_date", "derived", "quality_status", "issues",
                                  "release_note")}, 1, 2600)

rep = json.load(open(rep_p, encoding="utf-8"))
aj = rep.get("agent_judgment") or {}
w("\n=== report.agent_judgment keys ===")
w(str(list(aj.keys())))
cv = aj.get("contract_verification")
w("=== contract_verification ===")
pj(cv, 1, 9000)
for k in aj:
    if k != "contract_verification":
        v = aj[k]
        w("%s: %s" % (k, (json.dumps(v, ensure_ascii=False)[:600] if not isinstance(v, (str, int, float, bool, type(None))) else v)))
out.close()
print("written", out_p)
