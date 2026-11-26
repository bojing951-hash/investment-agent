#!/usr/bin/env python3
"""Read-only phrase locator. usage: python3 -I grep_phrases.py <file> <out.txt> <phrase> [<phrase> ...]"""
import sys

txt = open(sys.argv[1], encoding="utf-8").read()
out = open(sys.argv[2], "w", encoding="utf-8")
for ph in sys.argv[3:]:
    out.write("=== %s ===\n" % ph)
    i = 0
    k = 0
    while True:
        i = txt.find(ph, i)
        if i < 0 or k >= 6:
            break
        ln = txt.count("\n", 0, i) + 1
        out.write("L%d: …%s…\n" % (ln, txt[max(0, i - 90): i + len(ph) + 110].replace("\n", " ")))
        i += len(ph)
        k += 1
    if k == 0:
        out.write("(not found)\n")
out.close()
