#!/usr/bin/env python3
"""Seat-owned read-only misc extractor.
Usage: python3 -I extract_misc.py sources <snap>
       python3 -I extract_misc.py registry <registry.json> <metric_id> [<metric_id>...]
       python3 -I extract_misc.py registry_economy <registry.json> <economy>
       python3 -I extract_misc.py registry_ids <registry.json>
"""
import json
import sys


def reg_items(reg):
    if isinstance(reg, dict):
        for k in ("metrics", "registry", "items"):
            if k in reg and isinstance(reg[k], (list, dict)):
                v = reg[k]
                if isinstance(v, dict):
                    return [dict(x, _key=kid) if isinstance(x, dict) else x for kid, x in v.items()]
                return v
        # maybe top-level dict of id->spec
        out = []
        for k, v in reg.items():
            if isinstance(v, dict) and ("display_name" in v or "frequency" in v or "unit" in v):
                out.append(dict(v, _key=k))
        return out
    if isinstance(reg, list):
        return reg
    return []


def main(argv):
    mode = argv[0]
    if mode == "sources":
        with open(argv[1], "r", encoding="utf-8") as fh:
            snap = json.load(fh)
        print(json.dumps(snap["sources_status"], ensure_ascii=False, indent=1))
        return
    if mode in ("registry", "registry_economy", "registry_ids"):
        with open(argv[1], "r", encoding="utf-8") as fh:
            reg = json.load(fh)
        items = reg_items(reg)
        if mode == "registry":
            want = set(argv[2:])
            for it in items:
                if it.get("_key") in want or it.get("metric_id") in want or it.get("id") in want:
                    print(json.dumps(it, ensure_ascii=False, indent=1))
                    print("-----")
        elif mode == "registry_economy":
            eco = argv[2]
            for it in items:
                if it.get("economy") == eco or eco in str(it.get("economies", "")) or eco in str(it.get("tags", "")):
                    print(json.dumps({k: it.get(k) for k in ("_key", "metric_id", "id", "display_name", "economy", "frequency", "unit", "release_rule", "criticality", "collector")}, ensure_ascii=False))
        else:
            for it in items:
                print(it.get("_key") or it.get("metric_id") or it.get("id"))
        return
    print("unknown mode")


if __name__ == "__main__":
    main(sys.argv[1:])
