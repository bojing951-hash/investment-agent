#!/usr/bin/env python3
"""Read-only: brief view of snapshot facts rows (key fields only).
usage: s06_facts_brief.py <snapshot.json> <METRIC>[,<METRIC>...]
"""
import json
import sys


def main():
    path = sys.argv[1]
    wanted = sys.argv[2].split(",")
    with open(path, "r", encoding="utf-8") as f:
        snap = json.load(f)
    for f in snap["facts"]:
        if f.get("metric_id") in wanted:
            print(json.dumps({
                "fact_id": f.get("fact_id"),
                "display_name": f.get("display_name"),
                "value": f.get("value"),
                "unit": f.get("unit"),
                "value_type": f.get("value_type"),
                "observation_date": f.get("observation_date"),
                "as_of": f.get("as_of"),
                "source": f.get("source"),
                "quality_status": f.get("quality_status"),
                "issues": f.get("issues"),
                "high": f.get("high"),
                "low": f.get("low"),
                "calculation_ref": f.get("calculation_ref"),
            }, ensure_ascii=False))
    print("### total facts:", len(snap["facts"]))
    ids = sorted({f.get("metric_id") for f in snap["facts"]})
    print("### fact metric ids:", ids)


if __name__ == "__main__":
    main()
