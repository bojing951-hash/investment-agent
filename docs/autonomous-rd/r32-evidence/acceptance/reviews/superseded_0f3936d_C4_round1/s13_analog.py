#!/usr/bin/python3
"""Peek at the analog step envelope data (read-only) to fix key paths for the recompute table.
Usage: /usr/bin/python3 -I s13_analog.py <report.json> <out.txt>
"""
import json
import sys


def walk(o, pre, out, depth=0, maxdepth=4):
    if isinstance(o, dict):
        for k, v in o.items():
            p = "%s.%s" % (pre, k)
            if isinstance(v, dict) and depth < maxdepth:
                out.append("%s {dict %d}" % (p, len(v)))
                walk(v, p, out, depth + 1, maxdepth)
            elif isinstance(v, list):
                s = json.dumps(v, ensure_ascii=False)
                out.append("%s [list %d] %s" % (p, len(v), s if len(s) <= 700 else s[:700] + ".."))
            else:
                s = json.dumps(v, ensure_ascii=False)
                out.append("%s = %s" % (p, s if len(s) <= 500 else s[:500] + ".."))
    elif isinstance(o, list):
        for i, v in enumerate(o[:3]):
            walk(v, "%s[%d]" % (pre, i), out, depth + 1, maxdepth)


def main():
    rep_path, out_path = sys.argv[1], sys.argv[2]
    with open(rep_path, "r", encoding="utf-8") as fh:
        rep = json.load(fh)
    out = []
    for st in rep["steps"]:
        if st.get("step") in ("S6_analog", "S7_mode_gate", "S10_selfcheck"):
            out.append("=== %s" % st.get("step"))
            for k, v in st.items():
                if k in ("envelope",):
                    for kk, vv in v.items():
                        if kk == "data":
                            out.append("envelope.data keys: %s" % sorted(vv.keys()) if isinstance(vv, dict) else type(vv).__name__)
                            walk(vv, "data", out)
                        else:
                            s = json.dumps(vv, ensure_ascii=False)
                            out.append("envelope.%s = %s" % (kk, s[:600]))
                else:
                    s = json.dumps(v, ensure_ascii=False)
                    out.append("%s = %s" % (k, s if len(s) <= 900 else s[:900] + ".."))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("wrote", out_path, "lines", len(out))


if __name__ == "__main__":
    main()
