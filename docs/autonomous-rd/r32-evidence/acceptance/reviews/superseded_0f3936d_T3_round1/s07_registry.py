#!/usr/bin/env python3
"""Read-only: registry inspection.
usage: s07_registry.py <metric_registry.json> top            -> top-level structure
       s07_registry.py <metric_registry.json> get <METRIC>[,<METRIC>...]
       s07_registry.py <metric_registry.json> search <substr>
"""
import json
import sys


def main():
    path = sys.argv[1]
    what = sys.argv[2]
    with open(path, "r", encoding="utf-8") as f:
        reg = json.load(f)

    def iter_metrics():
        if isinstance(reg, dict) and isinstance(reg.get("metrics"), list):
            for v in reg["metrics"]:
                if isinstance(v, dict):
                    yield v.get("metric_id") or v.get("id"), v
            return
        if isinstance(reg, dict):
            for k, v in reg.items():
                if isinstance(v, dict) and "metric_id" not in v:
                    # maybe container of metrics
                    for kk, vv in v.items():
                        if isinstance(vv, dict):
                            yield kk, vv
                elif isinstance(v, dict):
                    yield k, v
        elif isinstance(reg, list):
            for v in reg:
                if isinstance(v, dict):
                    yield v.get("metric_id") or v.get("id"), v

    if what == "top":
        if isinstance(reg, dict):
            for k, v in reg.items():
                if isinstance(v, (dict, list)):
                    n = len(v)
                    sample = (list(v.keys())[:6] if isinstance(v, dict) else [str(x)[:80] for x in v[:2]])
                    print(f"{k}: {type(v).__name__}({n}) sample={sample}")
                else:
                    s = str(v)
                    print(f"{k}: {s[:600]}")
        else:
            print(type(reg), len(reg))
    elif what == "get":
        wanted = sys.argv[3].split(",")
        found = {}
        for k, v in iter_metrics():
            if k in wanted and k not in found:
                found[k] = v
        for w in wanted:
            print(f"=== {w}: " + ("NOT FOUND" if w not in found else json.dumps(found[w], ensure_ascii=False, indent=1)))
    elif what == "search":
        sub = sys.argv[3]
        for k, v in iter_metrics():
            s = json.dumps(v, ensure_ascii=False)
            if sub in s or sub in str(k):
                print(f"--- {k}")
                print(s[:3000])
    elif what == "ids":
        ids = sorted(str(k) for k, _ in iter_metrics())
        print(len(ids))
        print(ids)


if __name__ == "__main__":
    main()
