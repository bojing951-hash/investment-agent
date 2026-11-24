#!/usr/bin/python3 -I
# -*- coding: utf-8 -*-
"""s12_write_outputs.py -- render the two deliverables of the independent seat (Audit-R32 / N30 / Round-1).

usage:
  /usr/bin/python3 -I s12_write_outputs.py <recompute_table.json> <recompute_summary.json> \
     <independent_check.json> <agent_judgment.json> <report.json> <snapshot.json> \
     <release_calendar.json> <metric_registry.json> <MAP_REPORT.md> <FULL_REPORT.md> \
     <evidence_index.json> <PROSE-round1.md> <VERDICT-round1.json> \
     [judgment_contract.py] [text_consistency.py] [research_map_planner.py] [evidence_gate.py]

The first three inputs are the seat's own tables; the next nine are read-only inputs of the audited run.
The four trailing engine sources (optional) are only text-searched, never imported or executed.
The script writes exactly the two deliverables and nothing else.

Discipline built into the script:
  * every judgment sentence quoted as "original" is cut verbatim out of agent_judgment.json by start/end
    markers (never retyped) and asserted to be part of a leaf of the judgment file;
  * every engine / registry / calendar / snapshot sentence quoted in the narrative is located in the
    corresponding read-only input by a unique-substring search (never retyped);
  * every number in the narrative is either taken from the seat's recompute table / INFO rows, asserted by
    arithmetic in this script, or present in a read-only input; anything else is reported before writing.
"""
import datetime as dt
import hashlib
import json
import os
import re
import sys
from collections import Counter

ARGS = sys.argv[1:]
CHECK_ONLY = "--check-only" in ARGS
ARGS = [a for a in ARGS if a != "--check-only"]
assert len(ARGS) in (13, 17), "expected 13 or 17 path arguments, got %d" % len(ARGS)
(TABLE, SUMMARY, INDEP, JPATH, RPATH, SPATH, CPATH, REGPATH, MAPPATH, FULLPATH,
 EIDXPATH, PROSE_PATH, VERDICT_PATH) = ARGS[:13]
ENGINE_SRC = ARGS[13:17]
SEAT_DIR = os.path.dirname(os.path.abspath(PROSE_PATH))
for _p in (PROSE_PATH, VERDICT_PATH):
    assert os.path.dirname(os.path.abspath(_p)) == SEAT_DIR, "deliverables must sit in the seat directory"
AUDITED_AT = "2026-11-24"
REVIEWER = "independent-zero-context-seat-r32-n30-round1"
DECISION = "UPHELD"
GIT_HEAD = "8f9055d6e556700b08f28a3abeff284cf0c8d71f"


def getj(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def rd(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def log(msg):
    print(msg)
    sys.stdout.flush()


def leaves(o, p, out):
    if isinstance(o, dict):
        for k, v in o.items():
            leaves(v, p + [k], out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            leaves(v, p + [i], out)
    else:
        out.append((p, o))


def leaf_strings(o, out):
    if isinstance(o, dict):
        for v in o.values():
            leaf_strings(v, out)
    elif isinstance(o, list):
        for v in o:
            leaf_strings(v, out)
    elif isinstance(o, str):
        out.append(o)


def getp(o, path):
    for k in path:
        o = o[k]
    return o


def jpath(path):
    s = ""
    for k in path:
        s += "[%r]" % k if isinstance(k, str) else "[%d]" % k
    return s


# ---------------------------------------------------------------- loading (all inputs read-only)
T = getj(TABLE)
S = getj(SUMMARY)
I = getj(INDEP)
J = getj(JPATH)
R = getj(RPATH)
SNAP = getj(SPATH)
CALE = getj(CPATH)
REG = getj(REGPATH)
MAP = rd(MAPPATH)
FULL = rd(FULLPATH)
EIDX = getj(EIDXPATH)

LV = []
leaves(J, [], LV)
CORPUS = [v for _, v in LV if isinstance(v, str)]
JALL = "\n".join(CORPUS)

PTS = T["points"]
INFO = {}
for _r in T["info"]:
    INFO.setdefault(_r["key"], []).append(_r["value"])


def info_val(key):
    vals = INFO[key]
    j0 = json.dumps(vals[0], ensure_ascii=False, sort_keys=True)
    assert all(json.dumps(v, ensure_ascii=False, sort_keys=True) == j0 for v in vals), "INFO rows differ: " + key
    return vals[0]


# ---------------------------------------------------------------- the seat's tables: shape and totals
assert len(PTS) == S["points_total"] == S["points_counted"] == 595, (len(PTS), S["points_total"], S["points_counted"])
assert S["mismatches"] == 0 and S["script_errors"] == 0, (S["mismatches"], S["script_errors"])
assert all(p["ok"] is True for p in PTS)
assert all(set(p.keys()) == {"section", "where", "claim", "computed", "source", "ok"} for p in PTS)
assert I["n"] == I["ok"] == len(I["rows"]) == 107 and I["mismatch"] == 0, (I["n"], I["ok"], len(I["rows"]), I["mismatch"])
assert all(r["ok"] is True for r in I["rows"])
N_PTS, N_MIS, N_IND = len(PTS), S["mismatches"], I["n"]
SEC = S["per_section"]
assert sum(v["points"] for v in SEC.values()) == N_PTS
assert sum(v["ok"] for v in SEC.values()) == N_PTS and sum(v["mismatch"] for v in SEC.values()) == 0
assert S["minimum_required"] == 90 and N_PTS >= S["minimum_required"]


def isnum(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def tname(v):
    if isinstance(v, bool):
        return "布尔"
    if isnum(v):
        return "数值"
    if isinstance(v, str):
        return "文本"
    if isinstance(v, list):
        return "列表"
    if isinstance(v, dict):
        return "字典"
    return "空"


TYPE_ORDER = ["数值×数值", "文本×文本", "列表×列表", "布尔×布尔", "字典×字典"]
TP = Counter("%s×%s" % (tname(p["claim"]), tname(p["computed"])) for p in PTS)
for k in TP:
    if k not in TYPE_ORDER:
        TYPE_ORDER.append(k)
assert len(TYPE_ORDER) == 9, TYPE_ORDER
N_BOOL = sum(1 for p in PTS if isinstance(p["claim"], bool) or isinstance(p["computed"], bool))

# provenance category of the "source" key (first-named side of compound sources)
SS = SNAP["series_store"]
METRIC_RE = re.compile(r"^[A-Z][A-Z0-9_]*(@|×| vs |$|[^A-Za-z])")


def cat_of(src, prev):
    s = src.strip()
    if s.startswith("同上"):
        return prev
    if s.startswith(("release_calendar", "日历", "按日历实录形态重算")):
        return "cal"
    if s.startswith("metric_registry"):
        return "reg"
    if s.startswith("evidence_index"):
        return "eidx"
    if s.startswith(("agent_judgment", "l3", "l4", "reader_map", "regions[", "全文", "M1-step")):
        return "txt"
    if re.match(r"^20\d\d-\d\d-\d\d", s) or s.startswith(("日期序", "发布 20")):
        return "date"
    if s.startswith(("引擎规则", "按引擎规则", "research_plan", "steps[", "layers", "us_rates_trio", "rates_decomposition",
                     "asset_moves", "policy_window_path", "anchors", "point_values", "contract_verification", "MAP_REPORT",
                     "report.", "judgment_contract", "text_consistency", "四候选", "窗 2026")):
        return "eng"
    if (s.startswith("snapshot") or "series_store" in s or s.startswith("规则可见性") or METRIC_RE.match(s)
            or s.startswith(("11-20/10-23", "11-23/10-23", "35.89/19.45", "EA ", "JP ", "EA−JP", "JP/Tokyo", "Tokyo ",
                             "四台阶", "锚间"))):
        return "snap"
    return "oth"


CAT_NAMES = {"snap": "快照序列面(series_store/事实行/Gate A 及其算术)", "eng": "引擎计划与步骤面(research_plan/步骤信封/读者报告/契约验证)",
             "cal": "冻结发布日历", "reg": "注册表", "txt": "判断档自身(结构/在场性/同句一致)", "eidx": "证据索引", "date": "日期算术", "oth": "其他"}
CAT = Counter()
OTH = Counter()
_prev = "oth"
for p in PTS:
    c = cat_of(p["source"], _prev)
    _prev = c
    CAT[c] += 1
    if c == "oth":
        OTH[p["source"]] += 1
assert sum(CAT.values()) == N_PTS

# run history of the main recompute script (own files)
RUNS = []
for i in range(1, 13):
    p = os.path.join(SEAT_DIR, "s05_run%d.txt" % i)
    txt = rd(p)
    cuts = [q for q in (txt.find("\nMISMATCH"), txt.find("\nERR")) if q >= 0]
    head = txt[:min(cuts)] if cuts else txt
    sj = json.loads(head)
    RUNS.append((i, sj["points_total"], sj["mismatches"], sj["script_errors"], txt.count("\nMISMATCH |"), txt.count("\nERR |")))
    assert (sj["mismatches"], sj["script_errors"]) == (RUNS[-1][4], RUNS[-1][5]), RUNS[-1]
assert RUNS[-1] == (12, N_PTS, 0, 0, 0, 0), RUNS[-1]
N_RUN = len(RUNS)
N_PATCH = len([f for f in os.listdir(SEAT_DIR) if re.match(r"^s05_patch\d+\.py$", f)])
assert N_RUN == 12 and N_PATCH == 9, (N_RUN, N_PATCH)
