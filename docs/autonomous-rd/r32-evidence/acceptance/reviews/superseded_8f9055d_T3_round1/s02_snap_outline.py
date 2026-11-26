#!/usr/bin/python3 -I
"""Outline the research snapshot. Args: <snapshot.json>"""
import json
import sys


def main():
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    print("TOP KEYS:", list(d.keys()))
    for k, v in d.items():
        s = json.dumps(v, ensure_ascii=False)
        if len(s) > 400:
            print(f"- {k}: {type(v).__name__} len={len(v) if hasattr(v, '__len__') else ''} :: {s[:400]}...")
        else:
            print(f"- {k}: {s}")
    ss = d.get("series_store")
    print("\nseries_store type:", type(ss).__name__, "len", len(ss))
    keys = list(ss.keys())
    print("series_store keys (first 100):", keys[:100])
    k0 = keys[0]
    v0 = ss[k0]
    print("\nsample entry", k0, "type", type(v0).__name__)
    if isinstance(v0, dict):
        for kk, vv in v0.items():
            s = json.dumps(vv, ensure_ascii=False)
            print("   ", kk, ":", s[:200] + ("..." if len(s) > 200 else ""))
    elif isinstance(v0, list):
        print("   len", len(v0), "sample", json.dumps(v0[:3], ensure_ascii=False))
    facts = d.get("facts")
    print("\nfacts type:", type(facts).__name__, "len", len(facts) if facts else 0)
    if isinstance(facts, list) and facts:
        print("fact[0]:", json.dumps(facts[0], ensure_ascii=False)[:600])
        print("fact keys:", list(facts[0].keys()))
    elif isinstance(facts, dict):
        fk = list(facts.keys())
        print("facts keys sample:", fk[:10])
        print("fact sample:", json.dumps(facts[fk[0]], ensure_ascii=False)[:600])


if __name__ == "__main__":
    main()
