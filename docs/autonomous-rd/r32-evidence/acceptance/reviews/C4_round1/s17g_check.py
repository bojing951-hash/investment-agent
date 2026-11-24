# -*- coding: utf-8 -*-
#!/usr/bin/python3 -I
# s17g: 定稿前终检(只读)。用法: /usr/bin/python3 -I s17g_check.py OUTDIR DRAFT_DATA AJ
import sys, os, json
outdir, data_p, aj_p = sys.argv[1:4]
dd = json.load(open(data_p, encoding="utf-8"))
rows = dd["tbl_cmp"].split("\n")[2:] + dd["tbl_aux"].split("\n")[2:]
assert (dd["n_cmp"], dd["n_ok"], dd["n_mis"], dd["n_aux"], dd["n_all"]) == (403, 402, 1, 27, 430), dd["n_cmp"]
assert len(rows) == 430, len(rows)
bad = []
for r in rows:
    c = r.split(" | ")
    assert len(c) == 6, r[:120]
    src_, calc, rep = c[1], c[3], c[4]
    if src_ in ("datetime", "算术") or (" · " in src_ and src_.split(" · ")[0] == src_.split(" · ")[1]):
        bad.append(("src", r[:120]))
    if "pts_" in src_ or src_[:3] in ("s06", "s08", "s10", "s11"):
        bad.append(("tag", r[:120]))
    for cell in (calc, rep):
        low = cell.lower()
        if "nan" in low or "none" in low or "!!" in cell or "@@" in cell:
            bad.append(("val", r[:200]))
print("suspicious:", len(bad))
for b in bad[:40]:
    print("  ", b)
print("--- sample rows (every 18th) ---")
for i in range(0, len(rows), 18):
    print(rows[i][:260])
print("deviation rows:", [r[:70] for r in rows if r.endswith("| 偏离 |")])
import collections
print("verdict col:", collections.Counter(r.split(" | ")[5] for r in rows))
v = json.load(open(os.path.join(outdir, "_draft_VERDICT-round1.json"), encoding="utf-8"))
print("verdict", v["verdict"], v["recompute_points"], v["recompute_mismatches"], [x["severity"] for x in v["items"]])
p = open(os.path.join(outdir, "_draft_PROSE-round1.md"), encoding="utf-8").read()
print("prose bytes", len(p.encode("utf-8")), "placeholders", p.count("@@"), "sections", [l for l in p.split("\n") if l.startswith("## ")])
