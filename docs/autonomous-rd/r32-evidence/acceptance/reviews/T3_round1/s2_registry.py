#!/usr/bin/env python3
"""Dump registry entries for given metric ids.
usage: python3 -I s2_registry.py <registry_path> <metric_id> [<metric_id> ...]
with 'ALL' prints all top-level keys and a compact metric list.
"""
import json
import sys


def as_dict(metrics):
    if isinstance(metrics, dict):
        return metrics
    out = {}
    for ent in metrics:
        mid = ent.get("metric_id") or ent.get("id")
        out[mid] = ent
    return out


def main():
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as fh:
        reg = json.load(fh)
    print("TOP KEYS:", list(reg.keys()))
    for k, v in reg.items():
        if not isinstance(v, (dict, list)):
            print(f"  {k} = {v!r}")
    metrics = as_dict(reg.get("metrics", []))
    ids = sys.argv[2:]
    if ids == ["ALL"]:
        print("N metrics:", len(metrics))
        for mid, ent in metrics.items():
            print(mid, "|", ent.get("display_name"), "|", ent.get("economy"), "|", ent.get("frequency"), "|", ent.get("criticality"), "|", ent.get("release_rule") or ent.get("publication_rule"))
        return
    for mid in ids:
        if mid in metrics:
            print("=====", mid)
            print(json.dumps(metrics[mid], ensure_ascii=False, indent=1))
        else:
            print("=====", mid, "NOT IN REGISTRY")


if __name__ == "__main__":
    main()
