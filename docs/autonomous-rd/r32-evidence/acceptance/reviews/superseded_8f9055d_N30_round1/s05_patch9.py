#!/usr/bin/python3 -I
# -*- coding: utf-8 -*-
"""patch9: drop the three non-data-derived points ("M1-step3 %s 变动方向符号在文", claim=True, computed=True).
They were a duplicate marker of the regex match (the sign characters are hard-coded in the regex), not an
independent recompute; the data-derived direction check is the point right below them. Counting them would
inflate the point total by 3.
usage: /usr/bin/python3 -I s05_patch9.py <s05_recompute.py>"""
import sys

p = sys.argv[1]
src = open(p, encoding="utf-8").read()

old = ('            add(s, "M1-step3 %s 变动方向符号在文(欧元− / 日元+ / 美元指数+)", True, True,'
       ' "文: " + str([("−" if mid == "EURUSD" else "+")]))\n')
new = ('            # patch9: removed the former "变动方向符号在文" point (claim True / computed True, not data-derived;\n'
       '            # it only re-marked the regex match). The data-derived direction check is the point right below.\n')
assert src.count(old) == 1, src.count(old)
src = src.replace(old, new)
open(p, "w", encoding="utf-8").write(src)
print("patch9 applied:", p)
