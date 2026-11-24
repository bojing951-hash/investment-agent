#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Seat script: dump the audited judgment's L3 / L4 / transmission / turnings / headline text verbatim
(for the six checks and counter-attacks). Read-only.
Usage: python3 -I extract_l3_l4.py <agent_judgment.json> <out.txt>
"""
import json
import sys


def main():
    src, out = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        j = json.load(f)
    orig = sys.stdout
    sys.stdout = open(out, "w", encoding="utf-8")
    try:
        print("===== l3.contradictions =====")
        for i, c in enumerate(j["l3"]["contradictions"]):
            print("\n--- contradiction[%d] keys=%s" % (i, list(c.keys())))
            for k, v in c.items():
                if k in ("statement", "main_explanation", "conclusion", "verdict", "title", "id", "name", "dimension"):
                    print("  %s: %s" % (k, v))
                elif k == "competing_explanations":
                    for q, x in enumerate(v):
                        print("  competing[%d]: %s" % (q, x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)))
                else:
                    print("  %s: %s" % (k, json.dumps(v, ensure_ascii=False)))
        print("\n===== l3.mechanism_chains =====")
        print(json.dumps(j["l3"].get("mechanism_chains"), ensure_ascii=False, indent=1))
        print("\n===== l4 =====")
        print(json.dumps(j["l4"], ensure_ascii=False, indent=1))
        rm = j["reader_map"]
        print("\n===== reader_map.headline_conclusion =====")
        print(json.dumps(rm.get("headline_conclusion"), ensure_ascii=False, indent=1))
        print("\n===== reader_map.transmission =====")
        print(json.dumps(rm.get("transmission"), ensure_ascii=False, indent=1))
        print("\n===== reader_map.turnings =====")
        print(json.dumps(rm.get("turnings"), ensure_ascii=False, indent=1))
        for k in rm:
            if k not in ("headline_conclusion", "transmission", "turnings", "regions", "asset_returns_echo",
                         "rates_decomposition", "history_periods", "history_zero_case_note"):
                print("\n===== reader_map.%s =====" % k)
                print(json.dumps(rm[k], ensure_ascii=False, indent=1)[:6000])
        print("\n===== reader_map.rates_decomposition =====")
        print(json.dumps(rm.get("rates_decomposition"), ensure_ascii=False, indent=1))
        print("\n===== reader_map.history_zero_case_note =====")
        print(rm.get("history_zero_case_note"))
    finally:
        sys.stdout.close()
        sys.stdout = orig


if __name__ == "__main__":
    main()
