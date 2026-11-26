#!/usr/bin/python3
"""Key-name map of agent_judgment.json and the analog step envelope (read-only, compact).
Usage: python3 -I s08_keys.py <agent_judgment.json> <report.json> <out.txt>
"""
import json
import sys


def walk(obj, prefix, depth, max_depth, out):
    if isinstance(obj, dict):
        for k in obj:
            v = obj[k]
            p = "%s.%s" % (prefix, k)
            if isinstance(v, dict):
                out.append("%s {dict %d}" % (p, len(v)))
                if depth < max_depth:
                    walk(v, p, depth + 1, max_depth, out)
            elif isinstance(v, list):
                out.append("%s [list %d] first=%s" % (p, len(v), type(v[0]).__name__ if v else "-"))
                if v and isinstance(v[0], dict) and depth < max_depth:
                    walk(v[0], p + "[0]", depth + 1, max_depth, out)
            else:
                s = json.dumps(v, ensure_ascii=False)
                out.append("%s = %s" % (p, s if len(s) <= 90 else s[:90] + ".."))


def main():
    aj_path, rep_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    out = []
    with open(aj_path, "r", encoding="utf-8") as fh:
        aj = json.load(fh)
    out.append("=== agent_judgment.json")
    walk(aj, "$", 0, 4, out)
    with open(rep_path, "r", encoding="utf-8") as fh:
        rep = json.load(fh)
    out.append("=== report.json top keys: %s" % sorted(rep.keys()))
    for k in sorted(rep.keys()):
        v = rep[k]
        if isinstance(v, dict):
            out.append("  %s {dict %d} keys=%s" % (k, len(v), sorted(v.keys())[:40]))
        elif isinstance(v, list):
            out.append("  %s [list %d]" % (k, len(v)))
        else:
            s = json.dumps(v, ensure_ascii=False)
            out.append("  %s = %s" % (k, s if len(s) <= 120 else s[:120] + ".."))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("wrote", out_path, "lines", len(out))


if __name__ == "__main__":
    main()
