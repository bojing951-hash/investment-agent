#!/usr/bin/python3 -I
"""Compact table of point-value cells (read-only).
Usage: python3 -I s03_cells_table.py <report.json>
"""
import json
import sys


def main():
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        d = json.load(f)
    cells = d["research_plan"]["point_values"]["cells"]
    for c in cells:
        print("=" * 100)
        print(f"{c['region']} | {c['dimension']} | {c['metric_id']} | {c.get('display_name')} | unit={c.get('unit')} | {c.get('face_note')}")
        for k in c:
            if k in ("region", "dimension", "metric_id", "display_name", "unit", "face_note", "anchors", "policy_face"):
                continue
            print(f"   [{k}] = {json.dumps(c[k], ensure_ascii=False)}")
        for an, a in c["anchors"].items():
            extra = {k: v for k, v in a.items() if k not in ("status", "as_of", "observation_date", "publication_date", "value")}
            print(f"   -- {an}: status={a.get('status')} as_of={a.get('as_of')} obs={a.get('observation_date')} pub={a.get('publication_date')} value={a.get('value')}")
            print(f"        extra={json.dumps(extra, ensure_ascii=False)}")
        if c.get("policy_face") is not None:
            print(f"   POLICY_FACE={json.dumps(c['policy_face'], ensure_ascii=False)}")


if __name__ == "__main__":
    main()
