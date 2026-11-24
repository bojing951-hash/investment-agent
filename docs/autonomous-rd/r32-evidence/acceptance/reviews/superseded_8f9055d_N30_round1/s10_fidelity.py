#!/usr/bin/python3 -I
"""Seat script: render fidelity of the judgment text in the reader reports (read-only).
usage: s10_fidelity.py <agent_judgment.json> <MAP_REPORT.md> <FULL_REPORT.md> <report.md>
Prints, per report, how many string leaves (len>=12) of the judgment are found verbatim,
and lists the leaves that are missing (truncated to 160 chars).
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
    # reports may normalise whitespace; compare with all whitespace removed
    return "".join(s.split())


def main():
    jd = json.load(open(sys.argv[1], encoding="utf-8"))
    lv = []
    leaves(jd, "", lv)
    lv = [(p, s) for p, s in lv if len(s) >= 12 and not s.startswith("2026-")]
    reports = {}
    for path in sys.argv[2:]:
        with open(path, "r", encoding="utf-8") as fh:
            reports[path] = norm(fh.read())
    print("judgment string leaves (len>=12): %d" % len(lv))
    for path, txt in reports.items():
        missing = [(p, s) for p, s in lv if norm(s) not in txt]
        print("%s: found %d / %d, missing %d" % (path.split("/")[-1], len(lv) - len(missing), len(lv), len(missing)))
        for p, s in missing[:40]:
            print("   MISSING %s : %s" % (p, s[:200]))
    # numbers in judgment text: every numeric token with metric alias-free check is done by the seat's recompute script
    return 0


if __name__ == "__main__":
    sys.exit(main())
