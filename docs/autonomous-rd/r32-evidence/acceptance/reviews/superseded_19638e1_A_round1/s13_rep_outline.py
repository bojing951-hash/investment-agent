#!/usr/bin/python3 -I
"""Outline of report.json (read-only): top keys, research_plan keys, step names.
Usage: python3 -I s13_rep_outline.py <report.json>
"""
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as f:
    d = json.load(f)
print("TOP:", list(d.keys()))
rp = d["research_plan"]
print("research_plan:", {k: type(v).__name__ for k, v in rp.items()})
for i, s in enumerate(d.get("steps", [])):
    keys = list(s.keys()) if isinstance(s, dict) else type(s).__name__
    print(i, s.get("step") if isinstance(s, dict) else "", s.get("name") if isinstance(s, dict) else "", keys)


def find(o, path, key, hits, depth=0):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key:
                hits.append(path + "." + k)
            find(v, path + "." + k, key, hits, depth + 1)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            find(v, path + "[%d]" % i, key, hits, depth + 1)


for key in ("aftermath_blocks", "dispersion", "turning_candidates", "asset_moves", "us_rates_trio", "policy_event_clusters",
            "gate_a", "history_sync", "sync_face", "collection_status", "contract", "semantic_review"):
    hits = []
    find(d, "", key, hits)
    print(key, "->", hits[:6])
