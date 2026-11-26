#!/usr/bin/python3 -I
"""Dump snapshot facts for selected metrics + gate_a/quality blocks.
Args: <snapshot.json> [--all | metric ...]
"""
import json
import sys


def main():
    path = sys.argv[1]
    want = sys.argv[2:]
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    if "--gate" in want:
        print("=== research_as_of:", d["research_as_of"], "target_date:", d["target_date"], "tz:", d["timezone"])
        print("=== quality ===")
        print(json.dumps(d["quality"], ensure_ascii=False, indent=1))
        print("=== gate_a ===")
        print(json.dumps(d["gate_a"], ensure_ascii=False, indent=1))
        want = [w for w in want if w != "--gate"]
    if "--all" in want:
        mets = None
    else:
        mets = set(want)
    for ft in d["facts"]:
        if mets is not None and ft["metric_id"] not in mets:
            continue
        slim = {k: ft.get(k) for k in ["fact_id", "metric_id", "display_name", "value", "unit", "value_type",
                                        "observation_date", "as_of", "quality_status", "issues", "calc", "source"]}
        print(json.dumps(slim, ensure_ascii=False))


if __name__ == "__main__":
    main()
