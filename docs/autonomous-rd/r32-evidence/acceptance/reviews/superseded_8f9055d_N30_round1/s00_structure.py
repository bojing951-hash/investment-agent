#!/usr/bin/python3 -I
"""Seat script: print the key structure of report.json (read-only)."""
import json
import sys


def shape(obj, depth, maxdepth, out, prefix):
    if depth > maxdepth:
        return
    if isinstance(obj, dict):
        for k in obj:
            v = obj[k]
            p = prefix + "." + str(k) if prefix else str(k)
            if isinstance(v, dict):
                out.append(p + " {dict %d}" % len(v))
                shape(v, depth + 1, maxdepth, out, p)
            elif isinstance(v, list):
                out.append(p + " [list %d]" % len(v))
                if v and depth < maxdepth:
                    first = v[0]
                    if isinstance(first, dict):
                        out.append(p + "[0] {dict keys: %s}" % list(first.keys()))
                    else:
                        out.append(p + "[0] = %r" % (first,))
            else:
                s = repr(v)
                if len(s) > 160:
                    s = s[:160] + "..."
                out.append(p + " = " + s)
    elif isinstance(obj, list):
        out.append(prefix + " [list %d]" % len(obj))


def main():
    path = sys.argv[1]
    maxdepth = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    out = []
    shape(data, 0, maxdepth, out, "")
    for line in out:
        print(line)


if __name__ == "__main__":
    main()
