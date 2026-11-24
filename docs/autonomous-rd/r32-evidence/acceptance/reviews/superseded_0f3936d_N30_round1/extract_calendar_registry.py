#!/usr/bin/env python3
"""Seat script: dump frozen release calendar (all entries + batches) and registry entries
for the metrics relevant to N30.
Usage: python3 -I extract_calendar_registry.py <calendar.json> <registry.json> <out.txt>
"""
import json
import sys

REG_WANT = ["EA_HICP_YOY", "ECB_MRO", "ECB_DFR", "JP_CPI_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_RATE",
            "EA_REAL_GDP_YOY", "JP_REAL_GDP_YOY", "JP_POLICY_TARGET", "EURUSD", "USDJPY", "DXY",
            "UST_10Y", "TIPS_10Y", "BEI_10Y"]


def main():
    cal_p, reg_p, out_p = sys.argv[1:4]
    with open(cal_p, encoding="utf-8") as f:
        cal = json.load(f)
    with open(reg_p, encoding="utf-8") as f:
        reg = json.load(f)
    orig = sys.stdout
    sys.stdout = open(out_p, "w", encoding="utf-8")
    try:
        print("=== calendar meta ===")
        for k in ("version", "created", "updated"):
            print(k, "=", cal[k])
        print("spec =", cal["spec"])
        print("\n=== calendar.batches ===")
        for b in cal["batches"]:
            print(json.dumps(b, ensure_ascii=False))
        print("\n=== calendar.entries (all) ===")
        for e in cal["entries"]:
            print(json.dumps(e, ensure_ascii=False))
        metrics = reg["metrics"]
        print("\n=== registry: count", len(metrics), "===")
        ids = [m.get("metric_id") or m.get("id") for m in metrics]
        print("has JP_POLICY_TARGET:", "JP_POLICY_TARGET" in ids)
        by_econ = {}
        for m in metrics:
            by_econ.setdefault(m.get("economy"), []).append(m.get("metric_id") or m.get("id"))
        print("economy=JP metrics:", sorted(by_econ.get("JP", [])))
        print("economy=EA metrics:", sorted(by_econ.get("EA", [])))
        print("\n=== registry entries (relevant) ===")
        for m in metrics:
            mid = m.get("metric_id") or m.get("id")
            if mid in REG_WANT:
                print(json.dumps(m, ensure_ascii=False, indent=1))
    finally:
        sys.stdout.close()
        sys.stdout = orig


if __name__ == "__main__":
    main()
