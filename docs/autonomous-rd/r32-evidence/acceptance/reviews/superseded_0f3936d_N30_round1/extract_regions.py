#!/usr/bin/env python3
"""Seat script: dump reader_map.regions / asset_returns_echo / remaining reader_map keys verbatim (read-only).
Usage: python3 -I extract_regions.py <agent_judgment.json> <out.txt>
"""
import json
import sys


def main():
    src, out = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        j = json.load(f)
    rm = j["reader_map"]
    orig = sys.stdout
    sys.stdout = open(out, "w", encoding="utf-8")
    try:
        print("reader_map keys:", list(rm.keys()))
        print("===== reader_map.regions =====")
        print(json.dumps(rm.get("regions"), ensure_ascii=False, indent=1))
        print("===== reader_map.asset_returns_echo =====")
        print(json.dumps(rm.get("asset_returns_echo"), ensure_ascii=False, indent=1))
        for k in rm:
            if k not in ("headline_conclusion", "transmission", "turnings", "regions", "asset_returns_echo",
                         "rates_decomposition", "history_periods", "history_zero_case_note"):
                print("\n===== reader_map.%s =====" % k)
                print(json.dumps(rm[k], ensure_ascii=False, indent=1)[:8000])
        print("\n===== top-level keys =====", list(j.keys()))
        print("===== quality_gate_notes =====")
        print(json.dumps(j.get("quality_gate_notes"), ensure_ascii=False, indent=1))
        print("===== agent_declaration =====")
        print(json.dumps(j.get("agent_declaration"), ensure_ascii=False, indent=1))
        print("===== schema_version =====", j.get("schema_version"))
    finally:
        sys.stdout.close()
        sys.stdout = orig


if __name__ == "__main__":
    main()
