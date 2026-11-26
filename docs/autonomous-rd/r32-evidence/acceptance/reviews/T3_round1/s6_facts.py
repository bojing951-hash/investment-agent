#!/usr/bin/env python3
"""Print compact snapshot facts for given metric ids.
usage: python3 -I s6_facts.py <snapshot> <metric_id> [<metric_id> ...]
"""
import json
import sys


def main():
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as fh:
        snap = json.load(fh)
    facts = snap["facts"]
    want = set(sys.argv[2:])
    print("N facts:", len(facts))
    for f in facts:
        if f.get("metric_id") in want:
            out = {
                "fact_id": f.get("fact_id"),
                "value": f.get("value"),
                "unit": f.get("unit"),
                "observation_date": f.get("observation_date"),
                "as_of": f.get("as_of"),
                "quality_status": f.get("quality_status"),
                "issues": f.get("issues"),
            }
            src = f.get("source") or {}
            out["source"] = {k: src.get(k) for k in list(src.keys())[:6]}
            der = f.get("derived") or {}
            keys = [k for k in der.keys()]
            out["derived_keys"] = keys
            for k in ("m1", "m6"):
                if isinstance(der.get(k), dict):
                    d = der[k]
                    out["derived_" + k] = {kk: d.get(kk) for kk in ("basis_date", "basis_value", "pct_change")}
            print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
