#!/usr/bin/python3 -I
"""Engine-face dumper (read-only). usage: s15_dump.py <report.json> <out.txt> <what> [args]
what = steps | step:<idx>[:depth] | cv | qa"""
import json
import sys


def outline(obj, depth, max_depth, max_list, prefix="", out=None):
    out = out or print
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = prefix + "/" + str(k)
            if isinstance(v, dict):
                out("%s  {dict %d}" % (p, len(v)))
                if depth < max_depth:
                    outline(v, depth + 1, max_depth, max_list, p, out)
            elif isinstance(v, list):
                out("%s  [list %d]" % (p, len(v)))
                if depth < max_depth and v:
                    first = v[0]
                    if isinstance(first, (dict, list)):
                        outline(v[:max_list], depth + 1, max_depth, max_list, p + "[0..%d]" % (min(len(v), max_list) - 1), out)
                    else:
                        out("%s    e.g. %s" % (p, json.dumps(first, ensure_ascii=False)[:200]))
            else:
                s = json.dumps(v, ensure_ascii=False)
                if len(s) > 600:
                    s = s[:600] + "...(%d chars)" % len(s)
                out("%s = %s" % (p, s))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            p = prefix + "[%d]" % i
            if isinstance(v, (dict, list)):
                outline(v, depth + 1, max_depth, max_list, p, out)
            else:
                s = json.dumps(v, ensure_ascii=False)
                if len(s) > 600:
                    s = s[:600] + "...(%d chars)" % len(s)
                out("%s = %s" % (p, s))


rep = json.load(open(sys.argv[1], encoding="utf-8"))
outp = sys.argv[2]
what = sys.argv[3]
lines = []
P = lines.append
if what == "steps":
    for i, s in enumerate(rep["steps"]):
        env = s.get("envelope") if isinstance(s, dict) else None
        keys = list(s.keys()) if isinstance(s, dict) else []
        P("%2d %s ok=%s exec=%s keys=%s" % (i, s.get("step"), s.get("ok"), s.get("executed"), keys))
elif what.startswith("step:"):
    _, idx, *rest = what.split(":")
    depth = int(rest[0]) if rest else 3
    ml = int(rest[1]) if len(rest) > 1 else 2
    outline(rep["steps"][int(idx)], 0, depth, ml, "", P)
elif what == "cv":
    aj = rep.get("agent_judgment", {})
    for k in aj:
        if k in ("judgment",):
            continue
        outline({k: aj[k]}, 0, 6, 40, "", P)
elif what == "ajkeys":
    outline(rep.get("agent_judgment", {}).get("judgment", {}), 0, 2, 1, "", P)
open(outp, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("lines=%d -> %s" % (len(lines), outp))
