#!/usr/bin/python3 -I
"""Numeric coverage sweep: every Arabic-numeral token in the judgment's claim-bearing texts must be
either (a) a date whose YYYY-MM prefix occurs among OK recompute rows, or (b) a number whose absolute
value equals that of some reported/computed value of an OK row. Uncovered tokens are listed for manual
review (they are not automatically errors: thresholds, caliber words and counts need a human look).

Read-only. Args: <agent_judgment.json> <out_dir>
"""
import json
import os
import re
import sys

jd = json.load(open(sys.argv[1], "r", encoding="utf-8"))
out_dir = sys.argv[2]
num_set = set()
ym_set = set()
NUMRX = re.compile(r"-?\d+(?:\.\d+)?")


def flat(x, sink):
    if isinstance(x, bool):
        return
    if isinstance(x, (int, float)):
        sink.append(round(abs(float(x)), 4))
    elif isinstance(x, str):
        for m in re.findall(r"\d{4}-\d{2}(?:-\d{2})?", x):
            ym_set.add(m[:7])
        for m in NUMRX.findall(x):
            try:
                v = float(m)
            except ValueError:
                continue
            if abs(v) >= 1000 or (m.count(".") == 0 and len(m.lstrip("-")) >= 3):
                continue  # years / ids inside free text
            sink.append(round(abs(v), 4))
    elif isinstance(x, (list, tuple)):
        for y in x:
            flat(y, sink)
    elif isinstance(x, dict):
        for y in x.values():
            flat(y, sink)


n_rows = 0
for part in "ABCDE":
    p = os.path.join(out_dir, "recompute_points_%s.json" % part)
    if not os.path.exists(p):
        continue
    for r in json.load(open(p, "r", encoding="utf-8"))["rows"]:
        if not r.get("ok"):
            continue
        n_rows += 1
        sink = []
        flat(r.get("reported"), sink)
        flat(r.get("computed"), sink)
        flat(str(r.get("src")), sink)   # the seat's own computation label carries the directly computed value
        for v in sink:
            num_set.add(v)
TOK = re.compile(r"(?<![\d.])(\d{4}-\d{2}(?:-\d{2})?|\d+\.\d+|\d{1,3}(?![\d:]))")
STRIP = [
    (re.compile(r"[A-Za-z_]+[\d_][\w.]*"), " "),          # identifiers (NIKKEI225, CAC40, v1.5.0, T22:53:47 ...)
    (re.compile(r"\d{4}年\d{1,2}月"), " "),                # bare year-month words
    (re.compile(r"\b\d{2}-\d{2}\b(?!-\d{2})"), " "),      # short day-of-month paths (11-13)
    (re.compile(r"\d{2}:\d{2}:\d{2}"), " "),
    (re.compile(r"\+\d{2}:\d{2}"), " "),
    (re.compile(r"RC-[A-Z0-9-]+"), " "),
]
rm = jd["reader_map"]
TEXTS = []
for i in range(3):
    c = jd["l3"]["contradictions"][i]
    TEXTS.append(("C%d.statement" % (i + 1), c["statement"]))
    for j, x in enumerate(c.get("competing_explanations", [])):
        TEXTS.append(("C%d.cx[%d]" % (i + 1, j), x))
for i in range(4):
    TEXTS.append(("M1-%d" % (i + 1), jd["l3"]["mechanism_chains"][0]["links"][i]["text"]))
TEXTS.append(("headline", rm["headline_conclusion"]))
for r in rm["regions"]:
    TEXTS.append(("region.%s" % r["region"], r["from_to"]))
for i, l in enumerate(rm["transmission"][0]["links"]):
    for k, v in l.items():
        if k != "evidence_refs":
            TEXTS.append(("TL%d.%s" % (i + 1, k), v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)))
for i, t in enumerate(rm["turnings"]):
    for k, v in t.items():
        TEXTS.append(("T%d.%s" % (i + 1, k), v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)))
TEXTS.append(("turning_supplement", rm.get("turning_supplement") or ""))
TEXTS.append(("history_zero_case_note", rm.get("history_zero_case_note") or ""))
for s in jd["l4"]["scenarios"]:
    for k, v in s["rows"].items():
        TEXTS.append(("%s.%s" % (s["id"], k), v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)))
for i, q in enumerate(jd["quality_gate_notes"]):
    TEXTS.append(("QN[%d]" % i, q))
n_tok = n_cov = 0
unc = []
for name, s in TEXTS:
    if not isinstance(s, str):
        continue
    s2 = s
    for rx, rep in STRIP:
        s2 = rx.sub(rep, s2)
    s2 = re.sub(r'"[\w@\-]+@\d{4}-\d{2}-\d{2}"', " ", s2)   # evidence refs
    for m in TOK.finditer(s2):
        tok = m.group(1)
        n_tok += 1
        if re.match(r"\d{4}-\d{2}", tok):
            if tok[:7] in ym_set:
                n_cov += 1
                continue
        elif round(float(tok), 4) in num_set:
            n_cov += 1
            continue
        ctx = s2[max(0, m.start() - 24):m.end() + 14].replace("\n", " ")
        cand = [r["id"] for part in "ABCD" if os.path.exists(os.path.join(out_dir, "recompute_points_%s.json" % part))
                for r in json.load(open(os.path.join(out_dir, "recompute_points_%s.json" % part), "r", encoding="utf-8"))["rows"]
                if tok in json.dumps(r, ensure_ascii=False) and r.get("ok")]
        unc.append((name, tok, ctx, cand))
print("ok_rows=%d tokens=%d covered=%d uncovered=%d" % (n_rows, n_tok, n_cov, len(unc)))
for u in unc:
    print("  UNCOVERED", u[0], "|", u[1], "|", u[2], "| cand:", u[3])
