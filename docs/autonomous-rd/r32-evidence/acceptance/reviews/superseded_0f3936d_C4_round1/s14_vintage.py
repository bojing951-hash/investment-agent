#!/usr/bin/python3
"""Read-only probe: vintage / revision labels in point-value cells and their rendering.
Usage: /usr/bin/python3 -I s14_vintage.py <report.json> <MAP_REPORT.md> <agent_judgment.json> <out.txt>
"""
import json
import re
import sys


def main():
    rep_path, map_path, aj_path, out_path = sys.argv[1:5]
    out = []
    with open(rep_path, "r", encoding="utf-8") as fh:
        rep = json.load(fh)
    pv = rep.get("point_values") or {}
    out.append("point_values keys: %s" % sorted(pv.keys()))
    cells = pv.get("cells") or {}
    vint = {}
    for mid, c in cells.items():
        keys = sorted(c.keys())
        out.append("cell[%s] keys: %s" % (mid, keys))
        for k in keys:
            if any(t in k.lower() for t in ("vintage", "revision", "first", "release", "basis", "stale", "fresh", "status")):
                vint.setdefault("%s=%s" % (k, json.dumps(c.get(k), ensure_ascii=False)), []).append(mid)
    for k, mids in sorted(vint.items()):
        out.append("  %s -> %s" % (k, mids))
    for k in sorted(pv.keys()):
        if k != "cells":
            s = json.dumps(pv[k], ensure_ascii=False)
            out.append("point_values.%s = %s" % (k, s[:600]))
    with open(map_path, "r", encoding="utf-8") as fh:
        mlines = fh.read().split("\n")
    out.append("=== MAP_REPORT lines with 事后/修订/首发/vintage")
    for i, ln in enumerate(mlines, 1):
        if any(t in ln for t in ("事后", "修订值", "首发", "vintage")):
            out.append("%d: %s" % (i, ln[:700]))
    with open(aj_path, "r", encoding="utf-8") as fh:
        aj = json.load(fh)
    ajstr = json.dumps(aj, ensure_ascii=False)
    out.append("=== agent_judgment.json occurrences")
    for t in ("事后回顾", "最新修订值", "首发值", "修订口径", "vintage", "当时可知", "事后信息"):
        out.append("  %s: %d" % (t, ajstr.count(t)))
    for m in re.finditer("修订口径|当时可知", ajstr):
        out.append("   ctx: ..." + ajstr[max(0, m.start() - 80):m.end() + 80] + "...")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("wrote", out_path, "lines", len(out))


if __name__ == "__main__":
    main()
