#!/usr/bin/env python3
"""Read-only: list steps in report.json with envelope key summary.
usage: s08_steps.py <report.json> [STEP_NAME_PREFIX]
"""
import json
import sys


def main():
    path = sys.argv[1]
    prefix = sys.argv[2] if len(sys.argv) > 2 else None
    with open(path, "r", encoding="utf-8") as f:
        rep = json.load(f)
    for st in rep["steps"]:
        name = st.get("step")
        if prefix and not name.startswith(prefix):
            continue
        env = st.get("envelope")
        head = {k: st.get(k) for k in ("executed", "ok", "exit_code", "semantic_ok") if k in st}
        print(f"== {name}: {json.dumps(head, ensure_ascii=False)} note={str(st.get('note'))[:200]!r}")
        if isinstance(env, dict):
            for k, v in env.items():
                s = json.dumps(v, ensure_ascii=False)
                if len(s) > 300:
                    s = s[:300] + f"…(len {len(s)})"
                print(f"     env.{k} = {s}")


if __name__ == "__main__":
    main()
