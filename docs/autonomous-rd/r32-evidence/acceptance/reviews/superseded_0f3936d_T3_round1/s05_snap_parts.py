#!/usr/bin/env python3
"""Read-only: dump snapshot non-series parts (gate_a, quality, facts filtered by metric, sources_status).
usage: s05_snap_parts.py <snapshot.json> gate|quality|sources|notes|facts <METRIC>[,<METRIC>...]|recon
"""
import json
import sys


def main():
    path = sys.argv[1]
    what = sys.argv[2]
    with open(path, "r", encoding="utf-8") as f:
        snap = json.load(f)
    if what == "gate":
        node = snap["gate_a"]
    elif what == "quality":
        node = snap["quality"]
    elif what == "sources":
        node = snap["sources_status"]
    elif what == "notes":
        node = snap["notes"]
    elif what == "recon":
        node = snap["reconciliation"]
    elif what == "facts":
        wanted = sys.argv[3].split(",") if len(sys.argv) > 3 else []
        node = [f for f in snap["facts"] if (not wanted or f.get("metric_id") in wanted)]
    else:
        raise SystemExit("unknown part")
    print(json.dumps(node, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
