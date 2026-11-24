#!/usr/bin/python3
"""Compact structure of report.json steps (name/status/keys), the analog step envelope, run block, embedded judgment block.
Usage: python3 -I s09_steps.py <report.json> <out.txt>
"""
import json
import sys


def short(v, n=160):
    s = json.dumps(v, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "..(%d)" % len(s)


def main():
    rep_path, out_path = sys.argv[1], sys.argv[2]
    with open(rep_path, "r", encoding="utf-8") as fh:
        rep = json.load(fh)
    out = []
    steps = rep["steps"]
    out.append("steps n=%d; step keys=%s" % (len(steps), sorted(steps[0].keys())))
    for i, st in enumerate(steps):
        env = st.get("envelope") if isinstance(st, dict) else None
        extra = ""
        if isinstance(env, dict):
            extra = " env_keys=%s" % sorted(env.keys())
        out.append("[%d] %s" % (i, short({k: v for k, v in st.items() if k not in ("envelope", "output", "stdout", "text")}, 220) + extra))
    out.append("=== run block")
    for k, v in rep["run"].items():
        out.append("run.%s = %s" % (k, short(v, 700)))
    out.append("=== embedded agent_judgment block")
    for k, v in rep["agent_judgment"].items():
        out.append("aj.%s = %s" % (k, short(v, 500)))
    out.append("=== semantic_review")
    for k, v in rep["semantic_review"].items():
        out.append("sr.%s = %s" % (k, short(v, 300)))
    out.append("=== notes")
    for n in rep["notes"]:
        out.append(short(n, 1500))
    # analog step envelope detail
    for i, st in enumerate(steps):
        env = st.get("envelope") if isinstance(st, dict) else None
        if isinstance(env, dict) and isinstance(env.get("data"), dict) and any("analog" in str(x).lower() for x in (st.get("name"), st.get("step"), env.get("name"))):
            d = env["data"]
            out.append("=== analog step [%d] data keys=%s" % (i, sorted(d.keys())))
            for k, v in d.items():
                out.append("  data.%s = %s" % (k, short(v, 900)))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("wrote", out_path, "lines", len(out))


if __name__ == "__main__":
    main()
