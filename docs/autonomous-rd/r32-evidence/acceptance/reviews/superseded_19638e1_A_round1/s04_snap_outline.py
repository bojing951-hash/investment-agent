#!/usr/bin/python3 -I
"""Outline of the frozen snapshot (read-only).
Usage: python3 -I s04_snap_outline.py <snapshot.json>
"""
import json
import sys


def short(o, n=300):
    s = json.dumps(o, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "..."


def main():
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        d = json.load(f)
    print("TOP KEYS:", list(d.keys()))
    for k, v in d.items():
        if k in ("series_store", "facts"):
            continue
        print(f"--- {k}: {short(v, 1500)}")
    ss = d.get("series_store")
    print("\n=== series_store type:", type(ss).__name__, "len:", len(ss))
    if isinstance(ss, dict):
        for mid in sorted(ss.keys()):
            ent = ss[mid]
            if isinstance(ent, dict):
                keys = list(ent.keys())
                print(f"{mid}: keys={keys}")
            else:
                print(f"{mid}: {type(ent).__name__} {short(ent, 200)}")
    facts = d.get("facts")
    print("\n=== facts type:", type(facts).__name__, "len:", len(facts))
    if isinstance(facts, list) and facts:
        print("fact[0] keys:", list(facts[0].keys()) if isinstance(facts[0], dict) else type(facts[0]))
        print("fact[0]:", short(facts[0], 800))
    elif isinstance(facts, dict):
        ks = list(facts.keys())
        print("fact keys:", ks[:50])
        print("fact[first]:", short(facts[ks[0]], 800))


if __name__ == "__main__":
    main()
