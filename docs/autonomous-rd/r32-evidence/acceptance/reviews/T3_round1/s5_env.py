#!/usr/bin/env python3
"""Print a step envelope with long lists/arrays abbreviated.
usage: python3 -I s5_env.py <report.json> <step_name> [max_list_items] [max_str]
"""
import json
import sys


def abbrev(obj, depth, max_items, max_str):
    if isinstance(obj, dict):
        return {k: abbrev(v, depth + 1, max_items, max_str) for k, v in obj.items()}
    if isinstance(obj, list):
        if len(obj) > max_items and all(not isinstance(x, (dict, list)) for x in obj):
            head = obj[:max_items // 2]
            tail = obj[-max_items // 2:]
            return [abbrev(x, depth + 1, max_items, max_str) for x in head] + [f"... ({len(obj)} items) ..."] + [abbrev(x, depth + 1, max_items, max_str) for x in tail]
        if len(obj) > max_items * 3:
            return [abbrev(x, depth + 1, max_items, max_str) for x in obj[:max_items]] + [f"... ({len(obj)} items total) ..."]
        return [abbrev(x, depth + 1, max_items, max_str) for x in obj]
    if isinstance(obj, str) and len(obj) > max_str:
        return obj[:max_str] + f"...(+{len(obj) - max_str} chars)"
    return obj


def main():
    path, name = sys.argv[1], sys.argv[2]
    max_items = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    max_str = int(sys.argv[4]) if len(sys.argv) > 4 else 600
    with open(path, "r", encoding="utf-8") as fh:
        rep = json.load(fh)
    for st in rep["steps"]:
        if st.get("step") == name:
            env = st.get("envelope")
            print(json.dumps(abbrev(env, 0, max_items, max_str), ensure_ascii=False, indent=1))
            return
    print("step not found:", name)


if __name__ == "__main__":
    main()
