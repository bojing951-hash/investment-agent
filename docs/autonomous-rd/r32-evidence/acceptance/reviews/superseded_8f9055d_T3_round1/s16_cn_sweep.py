#!/usr/bin/python3 -I
"""Chinese-numeral coverage sweep over the three contradiction statements: every 中文数字 token that
carries a magnitude must be the `lit` of some OK recompute row (exact token) or be listed for review.
Args: <agent_judgment.json> <out_dir>
"""
import json
import os
import re
import sys

jd = json.load(open(sys.argv[1], "r", encoding="utf-8"))
out_dir = sys.argv[2]
lits = []
for part in "ABCDE":
    for r in json.load(open(os.path.join(out_dir, "recompute_points_%s.json" % part), "r", encoding="utf-8"))["rows"]:
        if r.get("ok") and r.get("lit"):
            lits.append((r["id"], r["lit"]))
NUM = "零一二三四五六七八九十百千万点两"
rx = re.compile("[零一二两三四五六七八九十百千万]+(?:点[零一二三四五六七八九]+)?(?:个)?(?:百分点|基点|天|月|次|条|点)?")
n = cov = 0
unc = []
for i in range(3):
    st = jd["l3"]["contradictions"][i]["statement"]
    for m in rx.finditer(st):
        tok = m.group(0)
        if tok in ("两", "两度", "两次", "两序列", "六个月", "两地", "两序列"):  # counted words, not magnitudes
            pass
        n += 1
        hit = [rid for rid, lit in lits if tok in lit]
        if hit:
            cov += 1
            continue
        ctx = st[max(0, m.start() - 12):m.end() + 10]
        unc.append((i + 1, tok, ctx))
print("cn tokens=%d covered=%d uncovered=%d" % (n, cov, len(unc)))
for u in unc:
    print("  UNCOVERED C%d | %s | %s" % u)
