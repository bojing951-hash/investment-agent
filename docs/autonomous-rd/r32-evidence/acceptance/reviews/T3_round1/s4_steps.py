#!/usr/bin/env python3
"""List steps of report.json and print an envelope (compact).
usage:
  python3 -I s4_steps.py <report.json> list
  python3 -I s4_steps.py <report.json> env <step_name> [maxchars]
  python3 -I s4_steps.py <report.json> det <step_name> [maxchars]
"""
import json
import sys


def main():
    path, mode = sys.argv[1], sys.argv[2]
    with open(path, "r", encoding="utf-8") as fh:
        rep = json.load(fh)
    steps = rep["steps"]
    if mode == "list":
        for i, st in enumerate(steps):
            env = st.get("envelope")
            det = st.get("deterministic_face")
            print(i, st.get("step"), "executed=", st.get("executed"), "ok=", st.get("ok"),
                  "| env_keys=", (sorted(env.keys())[:12] if isinstance(env, dict) else type(env).__name__),
                  "| det_keys=", (sorted(det.keys())[:12] if isinstance(det, dict) else type(det).__name__))
        return
    name = sys.argv[3]
    maxc = int(sys.argv[4]) if len(sys.argv) > 4 else 6000
    for st in steps:
        if st.get("step") == name:
            obj = st.get("envelope") if mode == "env" else st.get("deterministic_face")
            s = json.dumps(obj, ensure_ascii=False, indent=1)
            print(s[:maxc])
            if len(s) > maxc:
                print(f"... [truncated, total {len(s)} chars]")


if __name__ == "__main__":
    main()
