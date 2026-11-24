#!/usr/bin/python3 -I
"""Seat script: render fidelity detail (read-only).
usage: s10b_fidelity.py <agent_judgment.json> <report.md>
For every string leaf (len>=12) of the judgment not found verbatim (whitespace-insensitive)
in the report, print the longest prefix present in the report and the divergent tail.
"""
import json
import sys


def leaves(o, p, out):
    if isinstance(o, dict):
        for k, v in o.items():
            leaves(v, p + "." + k if p else k, out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            leaves(v, "%s[%d]" % (p, i), out)
    elif isinstance(o, str):
        out.append((p, o))


def norm(s):
    return "".join(s.split())


def main():
    jd = json.load(open(sys.argv[1], encoding="utf-8"))
    lv = []
    leaves(jd, "", lv)
    lv = [(p, s) for p, s in lv if len(s) >= 12]
    txt = norm(open(sys.argv[2], encoding="utf-8").read())
    found = 0
    for p, s in lv:
        n = norm(s)
        if n in txt:
            found += 1
            continue
        # longest prefix present
        lo, hi = 0, len(n)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if n[:mid] in txt:
                lo = mid
            else:
                hi = mid - 1
        print("MISSING %s" % p)
        print("   prefix_ok(%d/%d): %s" % (lo, len(n), n[max(0, lo - 30):lo]))
        print("   divergent     : %s" % n[lo:lo + 120])
    print("found %d / %d" % (found, len(lv)))


if __name__ == "__main__":
    main()
