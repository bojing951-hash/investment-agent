#!/usr/bin/python3 -I
"""Build the per-point recompute appendix for PROSE-round1.md from the seat's own output files.
usage: s30_appendix.py <out_appendix.md> <source-pairs-json>
source-pairs-json: [["A.1","s10_cells.py","_out_s10_cells.txt","<source keys>"], ...]"""
import sys
import json
import re
pairs = json.load(open(sys.argv[2], encoding="utf-8"))
L = []
tot = [0, 0]
for tag, script, outfile, src in pairs:
    n = m = 0
    L.append("")
    L.append("### %s %s — 出处键: %s" % (tag, script, src))
    L.append("")
    L.append("```text")
    for line in open(outfile, encoding="utf-8").read().split("\n"):
        s = line.rstrip()
        if s.startswith("###"):
            L.append(s[:200])
            continue
        if s.startswith("POINTS="):
            continue
        if "<<< MISMATCH" in s:
            m += 1
            n += 1
        elif s.endswith("OK"):
            n += 1
        elif s.lstrip().startswith("-> OK") or s.lstrip().startswith("-> consistent") or s.lstrip().startswith("-> MISMATCH") or s.lstrip().startswith("-> CHECK"):
            n += 1
            if "MISMATCH" in s or "CHECK" in s:
                m += 1
        else:
            continue
        L.append((s[:330] + (" …(截断,全行见 %s)" % outfile if len(s) > 330 else "")))
    L.append("```")
    L.append("")
    L.append("(%s 小计: %d 点, %d 不一致)" % (tag, n, m))
    tot[0] += n
    tot[1] += m
L.append("")
L.append("附录合计: %d 点, %d 不一致" % (tot[0], tot[1]))
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(L) + "\n")
print("appendix points=%d mismatches=%d lines=%d" % (tot[0], tot[1], len(L)))
