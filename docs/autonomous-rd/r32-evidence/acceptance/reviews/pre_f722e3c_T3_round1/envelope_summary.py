#!/usr/bin/env python3
"""Seat-owned read-only: print envelope.data minus bulky series arrays.
Usage: python3 -I envelope_summary.py <report.json> <step_name_substr> [maxchars]"""
import json
import sys


def shrink(o, depth=0):
    if isinstance(o, dict):
        return {k: ("<list[%d] omitted>" % len(v) if isinstance(v, list) and len(v) > 12 else shrink(v, depth + 1)) for k, v in o.items()}
    if isinstance(o, list):
        return [shrink(x, depth + 1) for x in o]
    return o


def main(argv):
    path, sub = argv[0], argv[1]
    maxc = int(argv[2]) if len(argv) > 2 else 6000
    with open(path, "r", encoding="utf-8") as fh:
        rep = json.load(fh)
    for st in rep.get("steps") or []:
        name = str(st.get("step"))
        if sub in name:
            print(f"===== {name} argv={st.get('argv')} semantic_ok={st.get('semantic_ok')} note={st.get('note')}")
            env = st.get("envelope") or {}
            for k in ("ok", "capability", "snapshot_id", "research_as_of", "gate_a", "warnings"):
                if k in env:
                    print(f"{k}={json.dumps(env[k], ensure_ascii=False)[:800]}")
            print(json.dumps(shrink(env.get("data")), ensure_ascii=False, indent=1)[:maxc])


if __name__ == "__main__":
    main(sys.argv[1:])
