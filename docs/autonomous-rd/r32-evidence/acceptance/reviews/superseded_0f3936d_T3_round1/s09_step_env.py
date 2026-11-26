#!/usr/bin/env python3
"""Read-only: dump one step envelope from report.json with a sub-path.
usage: s09_step_env.py <report.json> <STEP_NAME> [sub.path] [maxlen]
"""
import json
import sys


def get(node, path):
    cur = node
    for part in path.split("."):
        if isinstance(cur, dict):
            if part not in cur:
                raise KeyError(f"{part!r} not in {list(cur.keys())[:40]}")
            cur = cur[part]
        elif isinstance(cur, list):
            cur = cur[int(part)]
        else:
            raise KeyError(f"cannot descend {part!r} into {type(cur).__name__}")
    return cur


def main():
    path = sys.argv[1]
    step_name = sys.argv[2]
    sub = sys.argv[3] if len(sys.argv) > 3 else ""
    maxlen = int(sys.argv[4]) if len(sys.argv) > 4 else 20000
    with open(path, "r", encoding="utf-8") as f:
        rep = json.load(f)
    for st in rep["steps"]:
        if st.get("step") == step_name:
            env = st.get("envelope", {})
            if sub == "KEYS":
                for k, v in env.items():
                    s = json.dumps(v, ensure_ascii=False)
                    print(f"{k}: {type(v).__name__} len={len(s)} :: {s[:200]}")
                return
            node = get(env, sub) if sub else env
            s = json.dumps(node, ensure_ascii=False, indent=1)
            if len(s) > maxlen:
                s = s[:maxlen] + f"\n…(truncated, total {len(s)} chars)"
            print(s)
            return
    print("step not found:", step_name)


if __name__ == "__main__":
    main()
