#!/usr/bin/python3 -I
"""Registry lookup. Args: <registry.json> [--grep substr | --metric ID ...] [--brief]
"""
import json
import sys


def main():
    path = sys.argv[1]
    args = sys.argv[2:]
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    if args and args[0] == "--fieldsem":
        print(json.dumps(d["field_semantics"], ensure_ascii=False, indent=1))
        return
    mets = d["metrics"]
    ids = [m["metric_id"] for m in mets]
    if args and args[0] == "--ids":
        print(ids)
        return
    if args and args[0] == "--grep":
        sub = args[1]
        for m in mets:
            s = json.dumps(m, ensure_ascii=False)
            if sub.lower() in s.lower():
                print(f"- {m['metric_id']} :: {m.get('display_name')} :: economy={m.get('economy')} status={m.get('status')} crit={m.get('criticality')}")
        return
    want = set(a for a in args if not a.startswith("--"))
    brief = "--brief" in args
    for m in mets:
        if m["metric_id"] in want:
            if brief:
                print(f"## {m['metric_id']}: freq={m.get('frequency')} economy={m.get('economy')} crit={m.get('criticality')} status={m.get('status')} freshness={json.dumps(m.get('freshness'), ensure_ascii=False)}")
            else:
                print(json.dumps(m, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
