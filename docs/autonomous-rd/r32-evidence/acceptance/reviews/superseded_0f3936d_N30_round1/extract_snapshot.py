#!/usr/bin/env python3
"""Seat script: dump snapshot faces relevant to the N30 recompute.
Usage: python3 -I extract_snapshot.py <snapshot.json> <out.txt>
"""
import json
import sys

MONTHLY = ["JP_CPI_YOY", "EA_HICP_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_RATE", "ECB_DFR", "ECB_MRO",
           "EA_REAL_GDP_YOY", "JP_REAL_GDP_YOY"]


def main():
    snap_p, out_p = sys.argv[1], sys.argv[2]
    with open(snap_p, encoding="utf-8") as f:
        snap = json.load(f)
    orig = sys.stdout
    sys.stdout = open(out_p, "w", encoding="utf-8")
    try:
        print("snapshot_id:", snap["snapshot_id"])
        print("research_as_of:", snap["research_as_of"])
        print("target_date:", snap["target_date"])
        print("timezone:", snap["timezone"])
        print("\n=== gate_a ===")
        print(json.dumps(snap["gate_a"], ensure_ascii=False, indent=1))
        print("\n=== quality ===")
        print(json.dumps(snap["quality"], ensure_ascii=False, indent=1))
        print("\n=== notes ===")
        print(json.dumps(snap["notes"], ensure_ascii=False, indent=1))
        print("\n=== sources_status ===")
        print(json.dumps(snap["sources_status"], ensure_ascii=False, indent=1))
        ss = snap["series_store"]
        print("\n=== series_store keys sample (JP_CPI_YOY) ===")
        print(json.dumps({k: (type(v).__name__, len(v) if hasattr(v, "__len__") else v)
                          for k, v in ss["JP_CPI_YOY"].items()}, ensure_ascii=False))
        for m in MONTHLY:
            s = ss.get(m)
            print(f"\n=== series_store[{m}] FULL ===")
            if s is None:
                print("ABSENT from series_store")
            else:
                print(json.dumps(s, ensure_ascii=False))
        facts = snap["facts"]
        print("\n=== facts: keys of fact[0] ===")
        print(json.dumps(facts[0], ensure_ascii=False))
        print("\n=== facts for relevant metrics (all) ===")
        for fct in facts:
            mid = fct.get("metric_id") or fct.get("metric") or fct.get("id")
            if mid in MONTHLY:
                print(json.dumps(fct, ensure_ascii=False))
        print("\n=== reconciliation ===")
        print(json.dumps(snap["reconciliation"], ensure_ascii=False, indent=1))
    finally:
        sys.stdout.close()
        sys.stdout = orig


if __name__ == "__main__":
    main()
