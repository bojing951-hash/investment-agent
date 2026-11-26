#!/usr/bin/python3 -I
"""Print context around a substring in a text file. usage: s15_ctx.py <file> <substr> [before] [after] [max_hits]"""
import sys
t = open(sys.argv[1], encoding="utf-8").read()
needle = sys.argv[2]
b = int(sys.argv[3]) if len(sys.argv) > 3 else 80
a = int(sys.argv[4]) if len(sys.argv) > 4 else 160
mx = int(sys.argv[5]) if len(sys.argv) > 5 else 20
i = 0
n = 0
while n < mx:
    i = t.find(needle, i)
    if i < 0:
        break
    line = t.count("\n", 0, i) + 1
    print("L%d: ...%s..." % (line, t[max(0, i - b): i + len(needle) + a].replace("\n", " ⏎ ")))
    i += len(needle)
    n += 1
print("hits=%d" % n)
