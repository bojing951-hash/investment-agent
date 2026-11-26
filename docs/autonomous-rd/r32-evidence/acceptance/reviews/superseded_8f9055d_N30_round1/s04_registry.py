#!/usr/bin/python3 -I
"""Seat script: registry lookups (read-only).
usage: s04_registry.py <registry.json> economy <EA|JP|...>
       s04_registry.py <registry.json> metric <metric_id> [<metric_id> ...]
       s04_registry.py <registry.json> ids
       s04_registry.py <registry.json> notes
"""
import json
import sys


def main():
    path = sys.argv[1]
    mode = sys.argv[2]
    with open(path, "r", encoding="utf-8") as fh:
        reg = json.load(fh)
    metrics = reg["metrics"]
    if mode == "economy":
        eco = sys.argv[3]
        for m in metrics:
            if m.get("economy") == eco:
                print(json.dumps(m, ensure_ascii=False, indent=1))
    elif mode == "metric":
        ids = set(sys.argv[3:])
        for m in metrics:
            if m.get("metric_id") in ids:
                print(json.dumps(m, ensure_ascii=False, indent=1))
    elif mode == "ids":
        for m in metrics:
            print("%-20s economy=%s freq=%s unit=%s crit=%s status=%s" % (
                m.get("metric_id"), m.get("economy"), m.get("frequency"),
                m.get("unit"), m.get("criticality"), m.get("status")))
    elif mode == "notes":
        for n in reg.get("notes", []):
            print("-", n)
            print()
    elif mode == "fresh":
        for m in metrics:
            print("%-20s %s" % (m.get("metric_id"), json.dumps(m.get("freshness"), ensure_ascii=False)))


if __name__ == "__main__":
    main()
