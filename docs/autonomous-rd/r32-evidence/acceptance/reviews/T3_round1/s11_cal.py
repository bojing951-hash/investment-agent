#!/usr/bin/env python3
"""Read-only: dump selected release-calendar entries and registry notes needed for the recompute design.
usage: python3 -I s11_cal.py <run_dir>
"""
import json
import os
import sys


def load(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main():
    run = sys.argv[1]
    cal = load(os.path.join(run, "root_overlay", "config", "release_calendar.json"))
    reg = load(os.path.join(run, "root_overlay", "config", "metric_registry.json"))
    snap = load(os.path.join(run, "root_overlay", "data", "daily", "research_snapshot_20261123.json"))
    print("### calendar top-level (non-entries)")
    print({k: (v if k != "entries" else "<%d entries>" % len(v)) for k, v in cal.items() if k != "spec"})
    print("### spec", json.dumps(cal.get("spec"), ensure_ascii=False)[:1500])
    for x in cal["entries"]:
        eid = x["entry_id"]
        if "HICP" in eid or "BOJ" in eid:
            print("###", json.dumps(x, ensure_ascii=False))
    print("### entry keys union", sorted({k for x in cal["entries"] for k in x}))
    regm = {m["metric_id"]: m for m in reg["metrics"]}
    print("### registry top keys", sorted(k for k in reg.keys() if k != "metrics"), "n metrics", len(reg["metrics"]), "version", reg.get("version"))
    for m in ("JP_CPI_TOKYO_YOY", "JP_CPI_YOY", "EA_HICP_YOY", "JP_POLICY_RATE"):
        mm = regm[m]
        print("### registry", m)
        for k in sorted(mm.keys()):
            print("   ", k, "=", json.dumps(mm[k], ensure_ascii=False)[:700])
    print("### snapshot top keys", sorted(snap.keys()))
    for k in ("research_as_of", "as_of", "snapshot_id", "version", "generated_at", "meta"):
        if k in snap:
            print("   ", k, "=", json.dumps(snap[k], ensure_ascii=False)[:300])


if __name__ == "__main__":
    main()
