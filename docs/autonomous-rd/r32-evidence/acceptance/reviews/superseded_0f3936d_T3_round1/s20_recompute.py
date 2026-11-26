#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R32 / T3 / Round-1 独立语义审查席——只读复算脚本(主入口)。

用法:
  /usr/bin/python3 -I s20_recompute.py <snapshot.json> <release_calendar.json> \
      <metric_registry.json> <report.json> <agent_judgment.json> <evidence_index.json> \
      <OUT_DIR> [RUN_DIR]

只读: 仅打开上述只读面(及 RUN_DIR 下 MAP_REPORT.md / report.md 读者报告文本)读取;
只写 OUT_DIR 下 recompute_table.tsv / recompute_table.json / recompute_supplement.json。
分部: s20_part_a.py(①–⑤) 与 s20_part_b.py(⑥–⑭) 在本命名空间内 exec。
席位规则(与引擎推定规则相互独立复算): EA_HICP 月末+16 天; JP_CPI 月末+20 天;
东京 CPI 月末-1 天; BOJ 月均 月末+5 天; ECB 变更点序列发布日=观测日。
"""
import calendar as _cal
import json
import os
import re
import sys
from datetime import date, datetime, timedelta

SNAP_P, CAL_P, REG_P, REP_P, AJ_P, EV_P, OUT = sys.argv[1:8]
RUN_DIR = sys.argv[8] if len(sys.argv) > 8 else os.path.dirname(os.path.abspath(AJ_P))
os.makedirs(OUT, exist_ok=True)


def load(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


snap, calj, reg, rep, aj, ev = (load(p) for p in (SNAP_P, CAL_P, REG_P, REP_P, AJ_P, EV_P))
CUT = "2026-11-23"      # 判断档自称的研究截止日(待核)
A6M = "2026-05-23"      # 判断档自称的六个月前锚(待核)
STAMP = "0f3936dd7eb74c557a2350e400d58e10a09c5139"

SS = snap["series_store"]
REG = {m.get("metric_id"): m for m in reg["metrics"] if isinstance(m, dict)}
CAL_ENT = calj["entries"]
GATE = snap["gate_a"]
FACTS = snap["facts"]
FACT = {f["fact_id"]: f for f in FACTS}
C = aj["l3"]["contradictions"]
CHAIN = aj["l3"]["mechanism_chains"][0]
ML = CHAIN["links"]
S = {s["id"]: s["rows"] for s in aj["l4"]["scenarios"]}
RM = aj["reader_map"]
REGI = {r["region"]: r for r in RM["regions"]}
TR = RM["transmission"][0]["links"]
TN = RM["turnings"]
QGN = aj["quality_gate_notes"]
JT = json.dumps(aj, ensure_ascii=False)
CV = rep["agent_judgment"]["contract_verification"]
RP = rep["research_plan"]
CELLS = {(c["region"], c["metric_id"]): c for c in RP["point_values"]["cells"]}
EVREFS = {r["ref"] for r in ev}


def D(s):
    y, m, d = (int(x) for x in s[:10].split("-"))
    return date(y, m, d)


def series(m):
    e = SS[m]
    return [(D(x), v) for x, v in zip(e["dates"], e["values"])]


def val(m, d):
    """精确观测日的值;缺席返回 None。"""
    if isinstance(d, date):
        d = d.isoformat()
    e = SS.get(m)
    if e is None or d not in e["dates"]:
        return None
    return e["values"][e["dates"].index(d)]


def last_on_or_before(m, d):
    if isinstance(d, str):
        d = D(d)
    c = [x for x in series(m) if x[0] <= d]
    return c[-1] if c else None


def pct(a, b):
    return (b / a - 1.0) * 100.0


def month_end(d):
    return date(d.year, d.month, _cal.monthrange(d.year, d.month)[1])


PUB_OFFSET = {"EA_HICP_YOY": 16, "JP_CPI_YOY": 20, "JP_CPI_TOKYO_YOY": -1, "JP_POLICY_RATE": 5}


def pub_date(metric, obs):
    return month_end(obs) + timedelta(days=PUB_OFFSET[metric])


def latest_published(metric, as_of):
    """按席位规则: as_of 当日(含)已发布的最新观测。"""
    if isinstance(as_of, str):
        as_of = D(as_of)
    s = series(metric)
    if metric in PUB_OFFSET:
        c = [x for x in s if pub_date(metric, x[0]) <= as_of]
    else:
        c = [x for x in s if x[0] <= as_of]
    return c[-1] if c else None


ROWS = []
SUPP = {}
WARN = []


def _s(x):
    if isinstance(x, float):
        return round(x, 6)
    return x


def add(pid, cat, item, src, calc, rep, ok, note="", sev=""):
    """一行复算: calc=席位直算值, rep=报告/判断档值, ok=是否一致。"""
    ROWS.append({"id": pid, "cat": cat, "item": item, "src": src, "calc": _s(calc),
                 "rep": _s(rep), "ok": bool(ok), "note": note, "sev": sev})
    return bool(ok)


def num(pid, cat, item, src, calc, rep, tol=5e-3, tok=None, note="", sev=""):
    """数值点: |直算-报告|<=tol; tok=该数在判断档原文中的字面(须在场,否则记警)。"""
    if tok is not None and tok not in JT:
        WARN.append("%s: token %r not in judgment text" % (pid, tok))
    ok = calc is not None and rep is not None and abs(float(calc) - float(rep)) <= tol
    return add(pid, cat, item, src, calc, rep, ok, note, sev)


def add_supp(key, value):
    SUPP[key] = value


# ---- 分部 ----
HERE = os.path.dirname(os.path.abspath(__file__))
for _part in ("s20_part_a.py", "s20_part_b.py"):
    with open(os.path.join(HERE, _part), "r", encoding="utf-8") as _fh:
        exec(compile(_fh.read(), _part, "exec"), globals())

# ---- 汇总与落盘 ----
ids = [r["id"] for r in ROWS]
assert len(ids) == len(set(ids)), "duplicate point ids"
hits = [r for r in ROWS if r["ok"]]
miss = [r for r in ROWS if not r["ok"]]
by_sev = {}
for r in miss:
    by_sev[r["sev"] or "UNLABELED"] = by_sev.get(r["sev"] or "UNLABELED", 0) + 1

with open(os.path.join(OUT, "recompute_table.json"), "w", encoding="utf-8") as fh:
    json.dump({"points": len(ROWS), "hits": len(hits), "mismatches": len(miss),
               "rows": ROWS}, fh, ensure_ascii=False, indent=1)
cols = ("id", "cat", "item", "src", "calc", "rep", "ok", "sev", "note")
with open(os.path.join(OUT, "recompute_table.tsv"), "w", encoding="utf-8") as fh:
    fh.write("\t".join(cols) + "\n")
    for r in ROWS:
        fh.write("\t".join(str(r[c]).replace("\t", " ").replace("\n", " ") for c in cols) + "\n")
with open(os.path.join(OUT, "recompute_supplement.json"), "w", encoding="utf-8") as fh:
    json.dump(SUPP, fh, ensure_ascii=False, indent=1, default=str)

print("POINTS=%d HITS=%d MISMATCHES=%d" % (len(ROWS), len(hits), len(miss)))
print("MISMATCH_BY_SEV=%s" % json.dumps(by_sev, ensure_ascii=False))
for r in miss:
    print("  [MISS/%s] %s %s | calc=%s | rep=%s | %s" % (r["sev"] or "-", r["id"], r["cat"], r["calc"], r["rep"], r["note"]))
for w in WARN:
    print("  [WARN]", w)
print("SUPP_KEYS=%s" % sorted(SUPP.keys()))
