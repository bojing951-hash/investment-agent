#!/usr/bin/env python3
"""Seat script: print L1 rows for cited metrics + contract_verification from report.json.
Usage: python3 -I extract_l1_contract.py <report.json>
"""
import json
import sys

WANT = {"JP_CPI_YOY", "EA_HICP_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_RATE", "ECB_DFR", "ECB_MRO",
        "USDJPY", "EURUSD", "DXY", "SPX", "VIX", "DAX", "CAC40", "NIKKEI225", "UST_10Y",
        "TIPS_10Y", "BEI_10Y", "EA_REAL_GDP_YOY", "JP_REAL_GDP_YOY"}


def main():
    with open(sys.argv[1], encoding="utf-8") as f:
        rep = json.load(f)
    l1 = rep["layers"]["L1_事实层"]
    rows = l1["rows"]
    print("n L1 rows:", len(rows), "| n_facts_total:", l1.get("n_facts_total"), "| note:", l1.get("note"))
    print("row keys:", sorted(rows[0].keys()))
    print("\n--- L1 rows for cited metrics ---")
    for r in rows:
        if r.get("metric_id") in WANT:
            print(json.dumps(r, ensure_ascii=False))
    print("\n--- L1 metric ids present ---")
    print(sorted({r.get("metric_id") for r in rows}))
    cv = rep["agent_judgment"]["contract_verification"]
    print("\n--- contract_verification ---")
    print(json.dumps(cv, ensure_ascii=False, indent=1))
    print("\n--- validation ---")
    print(json.dumps(rep["agent_judgment"]["validation"], ensure_ascii=False, indent=1))
    print("\n--- reader_map_faces ---")
    print(json.dumps(rep["agent_judgment"]["reader_map_faces"], ensure_ascii=False, indent=1))
    print("\n--- notes ---")
    print(json.dumps(rep["notes"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
