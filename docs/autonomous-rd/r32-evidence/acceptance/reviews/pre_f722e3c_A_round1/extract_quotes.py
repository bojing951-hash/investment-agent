#!/usr/bin/env python3
"""Extract exact quote windows from MAP_REPORT.md / agent_judgment.json (read-only) for PROSE/VERDICT originals.
usage: python3 -I extract_quotes.py <MAP_REPORT.md> <agent_judgment.json> <out.txt>
"""
import json
import sys

lines = open(sys.argv[1], encoding="utf-8").read().split("\n")
aj = json.load(open(sys.argv[2], encoding="utf-8"))
out = open(sys.argv[3], "w", encoding="utf-8")


def w(s=""):
    out.write(s + "\n")


def win(n, needle, before=60, after=220):
    x = lines[n - 1]
    i = x.find(needle)
    if i < 0:
        w("L%d: needle NOT FOUND: %s" % (n, needle))
        return
    w("L%d@%d: …%s…" % (n, i, x[max(0, i - before): i + len(needle) + after]))


w("=== L11 headline ===")
w(lines[10])
w("=== L80 windows ===")
for nd in ("CORE_PCE", "按兵不动", "HY_OAS"):
    win(80, nd)
w("=== L123/L126/L129/L130/L133 ===")
for n in (123, 126, 129, 130, 133):
    w("L%d: %s" % (n, lines[n - 1]))
w("=== policy four-way DFEDTARU rows (L86-109) ===")
for n in range(86, 110):
    if "DFEDTARU" in lines[n - 1] or "DFF" in lines[n - 1] or n in (86, 87, 88):
        w("L%d: %s" % (n, lines[n - 1]))
w("=== L111 ===")
w("L111: %s" % lines[110])
w("=== L166-L172 asset table ===")
for n in range(163, 173):
    w("L%d: %s" % (n, lines[n - 1]))
w("=== L180 windows ===")
for nd in ("制造业PMI", "按兵不动", "隔夜"):
    win(180, nd, 80, 300)
w("=== L186 JP walk ===")
for nd in ("0.557", "1.25"):
    win(186, nd, 120, 260)
w("=== L191/L196/L199 ===")
for n in (191, 196, 199):
    w("L%d: %s" % (n, lines[n - 1]))
w("=== L192-L208 transmission ===")
for n in range(192, 209):
    w("L%d: %s" % (n, lines[n - 1]))
w("=== L212-L219 confrontation ===")
for n in range(212, 220):
    w("L%d: %s" % (n, lines[n - 1]))
w("=== L223-L228 scenarios ===")
for n in range(223, 229):
    w("L%d: %s" % (n, lines[n - 1]))
w("=== L232-L238 turnings ===")
for n in range(232, 239):
    w("L%d: %s" % (n, lines[n - 1]))
w("=== agent_judgment M1 link1 / link2 / C3 ===")
l3 = aj.get("l3") or {}
for ch in (l3.get("mechanism_chains") or []):
    for lk in (ch.get("links") or []):
        txt = json.dumps(lk, ensure_ascii=False)
        if "CORE_PCE" in txt or "时序为事实" in txt:
            w("M[%s] link: %s" % (ch.get("chain_id") or ch.get("id"), txt[:1500]))
for c in (l3.get("contradictions") or []):
    txt = json.dumps(c, ensure_ascii=False)
    if "按兵不动" in txt or "无中国利率预期" in txt or "荣枯线" in txt:
        i = txt.find("statement")
        w("C[%s]: %s" % (c.get("contradiction_id") or c.get("id"), txt[:1400]))
w("=== agent_judgment l4 SCN rows ===")
l4 = aj.get("l4") or {}
w(json.dumps(l4, ensure_ascii=False)[:3500])
w("=== reader_map.transmission ===")
rm = aj.get("reader_map") or {}
w(json.dumps(rm.get("transmission"), ensure_ascii=False)[:4000])
w("=== reader_map.turnings ===")
w(json.dumps(rm.get("turnings"), ensure_ascii=False)[:3000])
w("=== history sync lines ===")
for n in (335, 453, 577):
    w("L%d: %s" % (n, lines[n - 1]))
out.close()
print("written", sys.argv[3])
