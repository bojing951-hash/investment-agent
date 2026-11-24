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
import datetime as dt
# ======================================================================
# part C -- supplementary facts recomputed from the read-only inputs.
# Record-only checks (SUP / NUM): reported in PROSE section 5, never counted in the 595.
# Every quoted engine / registry / calendar / snapshot sentence is located in its input, never retyped.
# ======================================================================
SUP = []


def sup(label, cond, detail=""):
    SUP.append((len(SUP) + 1, label, bool(cond), "" if cond else str(detail)[:400]))


def D(s):
    return dt.date.fromisoformat(str(s)[:10])


def days(a, b):
    return (D(b) - D(a)).days


def n(v):
    """number as the judgment writes it: at most two decimals, no trailing zeros"""
    s = "%.2f" % (v + 0.0)
    return s.rstrip("0").rstrip(".") if "." in s else s


def sg(v):
    """signed number for the narrative"""
    return ("+" if v > 0 else ("−" if v < 0 else "")) + n(abs(v))


def near(a, b, tol=0.0051):
    return abs(a - b) <= tol


def ser(mid):
    s = SS[mid]
    return {str(d)[:10]: v for d, v in zip(s["dates"], s["values"]) if v is not None}


def prevd(dct, d):
    ks = sorted(dct)
    return ks[ks.index(d) - 1]


def chg(dct, a, b):
    return round((dct[b] / dct[a] - 1.0) * 100.0, 2)


def mo(dct, y, m_):
    return round(dct["%04d-%02d-01" % (y, m_)], 6)


NUM = []


def eqn(label, got, exp):
    dec = len(str(exp).split(".")[1]) if "." in str(exp) else 0
    NUM.append((label, got, exp, round(got, dec) == exp))


EA, JPC, TK, JPR = ser("EA_HICP_YOY"), ser("JP_CPI_YOY"), ser("JP_CPI_TOKYO_YOY"), ser("JP_POLICY_RATE")
MRO, DFR, U10 = ser("ECB_MRO"), ser("ECB_DFR"), ser("UST_10Y")
EUR, JPY, DXY = ser("EURUSD"), ser("USDJPY"), ser("DXY")
SPX, NK, DAX, CAC, VIX = ser("SPX"), ser("NIKKEI225"), ser("DAX"), ser("CAC40"), ser("VIX")
GEA, GJP, FTL, FTU = ser("EA_REAL_GDP_YOY"), ser("JP_REAL_GDP_YOY"), ser("DFEDTARL"), ser("DFEDTARU")
VE = {i: mo(EA, 2026, i) for i in range(1, 11)}
VJ = {i: mo(JPC, 2026, i) for i in range(1, 11)}
CUTOFF = "2026-11-23"
W0, W1 = "2026-10-23", "2026-11-20"
FACTS = {f["fact_id"]: f for f in SNAP["facts"]}
GA = SNAP["gate_a"]
RP = R["research_plan"]
CELLS = {c["metric_id"]: c for c in RP["point_values"]["cells"]}
CON = J["l3"]["contradictions"]
LKS = J["l3"]["mechanism_chains"][0]["links"]
TRS = J["reader_map"]["transmission"][0]["links"]
TNS = J["reader_map"]["turnings"]
RGS = J["reader_map"]["regions"]
QGN = J["quality_gate_notes"]
SCE = J["l4"]["scenarios"]
HEAD = J["reader_map"]["headline_conclusion"]
REGM = {m.get("metric_id") or m.get("id"): m for m in (REG.get("metrics") if isinstance(REG, dict) else REG)}
REGTXT = json.dumps(REG, ensure_ascii=False)
RTXT = json.dumps(R, ensure_ascii=False)
SNAPTXT = json.dumps(SNAP, ensure_ascii=False)
ALLSTR = [v for _, v in LV if isinstance(v, str)]
JALL = "\n".join(ALLSTR)
CE = CALE["entries"]
JPT = [e for e in CE if e.get("entry_id") == "RC-JP-BOJ-TARGET-2026-09"][0]
JPM = [e for e in CE if e.get("entry_id") == "RC-JP-BOJ-MAINT-2026-10"][0]
TARGET = JPT["target_value"]
EJ = R["agent_judgment"]
CV = EJ["contract_verification"]
CVNV = [v for v in CV["verdicts"] if v.get("status") != "VERIFIED"]
CV_ST = Counter(v["status"] for v in CV["verdicts"] + CV["six_checks"] + CV["map_checks"])
DRI = {it.get("metric_id"): it for it in R["run"]["data_requirements"]["items"]}
STEPS = {s["step"]: s for s in R["steps"] if isinstance(s.get("envelope"), dict)}
S5 = STEPS["S5_compare"]["envelope"]["data"]
S6 = STEPS["S6_analog"]["envelope"]["data"]
EIDX_REFS = set(e["ref"] for e in EIDX)
MAPL, FULLL = MAP.split("\n"), FULL.split("\n")


def need(q, *texts):
    assert any(q in t for t in texts), ("quote not found in inputs", q[:60])
    return q


def line_of(lines, needle):
    return [i + 1 for i, l in enumerate(lines) if needle in l]


# ---- inflation readings (C1)
YEA = round(VE[10] - mo(EA, 2025, 10), 2)
YJP = round(mo(JPC, 2025, 10) - VJ[10], 2)
GAP10 = round(VE[10] - VJ[10], 2)
D04 = (round(VE[10] - VE[4], 2), round(VJ[10] - VJ[4], 2))
D06 = (round(VE[10] - VE[6], 2), round(VJ[10] - VJ[6], 2))
D05 = (round(VE[10] - VE[5], 2), round(VJ[10] - VJ[5], 2))
GAPS = [round(VE[i] - VJ[i], 2) for i in range(5, 11)]
SEPJ = round(VJ[9] - VE[9], 2)
SEPT = round(mo(TK, 2026, 9) - VE[9], 2)
JP_DIP = round(VJ[3] - VJ[4], 2)
for lab, got, exp in (("欧元区HICP 2026-10", VE[10], 4.0), ("欧元区HICP 2026-09", VE[9], 3.8), ("欧元区HICP 2026-08", VE[8], 3.2),
                      ("欧元区HICP 2026-07", VE[7], 2.9), ("欧元区HICP 2026-06", VE[6], 2.8), ("欧元区HICP 2026-05", VE[5], 3.2),
                      ("欧元区HICP 2026-04", VE[4], 3.0), ("欧元区HICP 2026-02", VE[2], 1.9), ("欧元区HICP 2026-01", VE[1], 1.7),
                      ("欧元区HICP 2025-10", mo(EA, 2025, 10), 2.1),
                      ("日本全国CPI 2026-10", VJ[10], 2.44), ("日本全国CPI 2026-09", VJ[9], 2.16), ("日本全国CPI 2026-08", VJ[8], 1.98),
                      ("日本全国CPI 2026-07", VJ[7], 1.97), ("日本全国CPI 2026-06", VJ[6], 1.67), ("日本全国CPI 2026-05", VJ[5], 1.53),
                      ("日本全国CPI 2026-04", VJ[4], 1.38), ("日本全国CPI 2026-03", VJ[3], 1.46), ("日本全国CPI 2026-02", VJ[2], 1.27),
                      ("日本全国CPI 2025-11", mo(JPC, 2025, 11), 2.9), ("日本全国CPI 2025-10", mo(JPC, 2025, 10), 2.99),
                      ("日本全国CPI 2025-09", mo(JPC, 2025, 9), 2.91), ("日本全国CPI 2025-01", mo(JPC, 2025, 1), 4.03),
                      ("东京都CPI 2026-10", mo(TK, 2026, 10), 2.73), ("东京都CPI 2026-09", mo(TK, 2026, 9), 2.69), ("东京都CPI 2026-08", mo(TK, 2026, 8), 1.9),
                      ("东京都CPI 2026-06", mo(TK, 2026, 6), 1.6), ("东京都CPI 2026-04", mo(TK, 2026, 4), 1.42),
                      ("最新水平差 欧元区−日本", GAP10, 1.56), ("同比对照 欧元区", YEA, 1.9), ("同比对照 日本(回落)", YJP, 0.55),
                      ("锚间变化 欧元区", D04[0], 1.0), ("锚间变化 日本", D04[1], 1.06), ("自2026-06 欧元区", D06[0], 1.2), ("自2026-06 日本", D06[1], 0.77),
                      ("自2026-05 欧元区", D05[0], 0.8), ("自2026-05 日本", D05[1], 0.91), ("窗内水平差最小", min(GAPS), 0.93), ("窗内水平差最大", max(GAPS), 1.67),
                      ("2026-09期 日本全国−欧元区", SEPJ, -1.64), ("2026-09期 东京−欧元区", SEPT, -1.11)):
    eqn(lab, got, exp)
def p1(v):
    s_ = n(v)
    return s_ + ".0" if "." not in s_ else s_


PATH_EA = "→".join("%s(%s)" % (p1(VE[i]), "2026-%02d" % i) for i in range(5, 11))
PATH_JP = "→".join("%s(%s)" % (p1(VJ[i]), "2026-%02d" % i) for i in range(5, 11))
sup("环1 文内两条月度路径串与序列面逐月值一致", "EA_HICP_YOY " + PATH_EA in LKS[0]["text"] and "JP_CPI_YOY " + PATH_JP in LKS[0]["text"], (PATH_EA, PATH_JP))
sup("日本 2026-05..2026-10 逐月上行;欧元区 2026-06 回落后非单调", all(VJ[i] < VJ[i + 1] for i in range(5, 10)) and VE[6] < VE[5])
sup("东京都序列自 2026-01 起、去年同月读数不在序列内", min(TK) == "2026-01-01" and "2025-10-01" not in TK and max(TK) == "2026-10-01")
sup("两条最新读数 L1 事实行 quality_status=WARN", all(FACTS[k]["quality_status"] == "WARN" for k in ("JP_CPI_YOY@2026-10-01", "EA_HICP_YOY@2026-10-01")))
sup("推定发布日: 欧元区 2026-11-16、日本 2026-11-20(相隔 4 天),规则=月末+16/月末+20",
    CELLS["EA_HICP_YOY"]["anchors"]["最新一期"]["publication_date"] == "2026-11-16" and CELLS["JP_CPI_YOY"]["anchors"]["最新一期"]["publication_date"] == "2026-11-20"
    and days("2026-11-16", "2026-11-20") == 4 and "月末+16天" in CELLS["EA_HICP_YOY"]["anchors"]["最新一期"]["publication_rule"]
    and "月末+20天" in CELLS["JP_CPI_YOY"]["anchors"]["最新一期"]["publication_rule"])

# ---- policy faces (C2 / C3)
STEPS_JP = [("2026-06", mo(JPR, 2026, 5), mo(JPR, 2026, 6)), ("2026-07", mo(JPR, 2026, 6), mo(JPR, 2026, 7)),
            ("2026-09", mo(JPR, 2026, 8), mo(JPR, 2026, 9)), ("2026-10", mo(JPR, 2026, 9), mo(JPR, 2026, 10))]
STEP_BP = [round((b - a) * 100, 1) for _, a, b in STEPS_JP]
SUM_BP = round(sum(STEP_BP), 1)
ANCH_BP = round((mo(JPR, 2026, 10) - mo(JPR, 2026, 4)) * 100, 1)
Y12_BP = round((mo(JPR, 2026, 10) - mo(JPR, 2025, 11)) * 100, 1)
LAST_MRO, LAST_DFR, LAST_JPR = max(MRO), max(DFR), max(JPR)
NONWED = sorted(set(d for d in list(MRO) + list(DFR) if D(d).weekday() != 2))
NONWED_YEARS = sorted(set(d[:4] for d in NONWED))
NONWED_2015 = [d for d in NONWED if d >= "2015-01-01"]
WIN_OBS = ["2025-06-11", "2026-06-17", "2026-09-16"]
DD = dict(d68=days("2026-09-16", CUTOFF), d371=days("2025-06-11", "2026-06-17"), d91=days("2026-06-17", "2026-09-16"),
          d8a=days("2026-09-16", JPT["effective_on"]), d8b=days("2026-09-10", JPT["decision_date"]), d24=days(JPM["decision_date"], CUTOFF),
          d14=days(JPM["decision_date"], "2026-11-13"), d58=days("2026-09-16", "2026-11-13"), d21=days(JPM["decision_date"], W1), d65=days("2026-09-16", W1),
          d6a=days("2026-06-11", "2026-06-17"), d6b=days(JPT["decision_date"], JPT["effective_on"]))
for lab, got, exp in (("MRO 2025-06-11", MRO["2025-06-11"], 2.15), ("MRO 2026-06-17", MRO["2026-06-17"], 2.4), ("MRO 2026-09-16", MRO["2026-09-16"], 2.65),
                      ("DFR 2025-06-11", DFR["2025-06-11"], 2.0), ("DFR 2026-06-17", DFR["2026-06-17"], 2.25), ("DFR 2026-09-16", DFR["2026-09-16"], 2.5),
                      ("月均 2026-04", mo(JPR, 2026, 4), 0.727), ("月均 2026-05", mo(JPR, 2026, 5), 0.727), ("月均 2026-06", mo(JPR, 2026, 6), 0.841),
                      ("月均 2026-07", mo(JPR, 2026, 7), 0.978), ("月均 2026-08", mo(JPR, 2026, 8), 0.977), ("月均 2026-09", mo(JPR, 2026, 9), 1.043),
                      ("月均 2026-10", mo(JPR, 2026, 10), 1.227), ("月均 2025-11", mo(JPR, 2025, 11), 0.478),
                      ("台阶1 bp", STEP_BP[0], 11.4), ("台阶2 bp", STEP_BP[1], 13.7), ("台阶3 bp", STEP_BP[2], 6.6), ("台阶4 bp", STEP_BP[3], 18.4),
                      ("四台阶之和 bp", SUM_BP, 50.1), ("锚间净 bp", ANCH_BP, 50.0), ("近12个月月均净 bp", Y12_BP, 74.9),
                      ("距截止天数", DD["d68"], 68), ("持平天数", DD["d371"], 371), ("两次变更间隔", DD["d91"], 91), ("生效日间隔", DD["d8a"], 8),
                      ("回推决议日间隔", DD["d8b"], 8), ("维持决议距截止", DD["d24"], 24), ("跳升起点距维持决议", DD["d14"], 14), ("跳升起点距欧央行生效", DD["d58"], 58),
                      ("跳升终点距维持决议", DD["d21"], 21), ("跳升终点距欧央行生效", DD["d65"], 65), ("决议→生效 欧央行", DD["d6a"], 6), ("决议→生效 日央行", DD["d6b"], 6),
                      ("水平差 MRO−目标", round(MRO[LAST_MRO] - TARGET, 2), 1.4), ("水平差 DFR−目标", round(DFR[LAST_DFR] - TARGET, 2), 1.25),
                      ("欧元区GDP 2026-07", mo(GEA, 2026, 7), 1.28), ("日本GDP 2026-07", mo(GJP, 2026, 7), 1.16)):
    eqn(lab, got, exp)
sup("ECB 两序列与日本月均序列末观测日", (LAST_MRO, LAST_DFR, LAST_JPR) == ("2026-09-16", "2026-09-16", "2026-10-01"), (LAST_MRO, LAST_DFR, LAST_JPR))
sup("欧央行序列非周三观测日: 全史 %d 个(年份 %s),2015 年以来 %d 个;本窗三个观测日全为周三" % (
    len(NONWED), "/".join(NONWED_YEARS), len(NONWED_2015)),
    len(NONWED_2015) == 0 and all(d in MRO and D(d).weekday() == 2 for d in WIN_OBS), NONWED)
sup("ECB 两事实行 quality_status=DEGRADED;注册表 freshness=10 天且 decision_dated=true;点值格最新一期 status=ok/policy_confirmation",
    all(FACTS[k]["quality_status"] == "DEGRADED" for k in ("ECB_MRO@2026-09-16", "ECB_DFR@2026-09-16"))
    and all(REGM[c]["freshness"]["max_calendar_lag_days"] == 10 and REGM[c]["freshness"].get("decision_dated") is True for c in ("ECB_MRO", "ECB_DFR"))
    and all(CELLS[c]["anchors"]["最新一期"]["status"] == "ok" and CELLS[c]["anchors"]["最新一期"].get("freshness_basis") == "policy_confirmation" for c in ("ECB_MRO", "ECB_DFR")))
sup("交付门: ECB_MRO/ECB_DFR 记 insufficient_coverage(日频族规格)", all(
    (DRI[c].get("outcome"), DRI[c]["spec"].get("frequency"), DRI[c]["spec"]["window"].get("n_in_window"), DRI[c]["spec"]["window"].get("expected_in_window"),
     DRI[c]["spec"]["window"].get("n_floor_in_window"), DRI[c]["spec"]["window"].get("max_adjacent_gap_days"), DRI[c]["spec"]["window"].get("max_gap_limit_days"))
    == ("insufficient_coverage", "daily", 2, 131, 66, 91, 30) for c in ("ECB_MRO", "ECB_DFR")))
sup("Gate A: DEGRADED;noncore_missing 含 JP_CPI_TOKYO_YOY/BUND_10Y/BUND_2Y/EA_REAL_GDP_YOY/JP_REAL_GDP_YOY;noncore_degraded 含 ECB_MRO/ECB_DFR",
    GA["status"] == "DEGRADED" and all(k in GA["noncore_missing"] for k in ("JP_CPI_TOKYO_YOY", "BUND_10Y", "BUND_2Y", "EA_REAL_GDP_YOY", "JP_REAL_GDP_YOY"))
    and all(k in GA["noncore_degraded"] for k in ("ECB_MRO", "ECB_DFR")))
sup("注册表 JP/EA 面无 JP_POLICY_TARGET、无两地核心通胀序列;series_store 无 JGB/BUND;日债三期限事实行在场",
    "JP_POLICY_TARGET" not in REGM and not [k for k in REGM if REGM[k].get("economy") in ("JP", "EA") and re.search(r"CORE|HICX", k)]
    and not [k for k in SS if re.search(r"JGB|BUND", k)] and all(FACTS[k]["observation_date"] == "2026-11-19" for k in ("JGB2Y@2026-11-19", "JGB5Y@2026-11-19", "JGB10Y@2026-11-19")))
JGBV = [(FACTS[k]["value"], FACTS[k]["quality_status"]) for k in ("JGB2Y@2026-11-19", "JGB5Y@2026-11-19", "JGB10Y@2026-11-19")]
sup("证据索引 60 行,无 JGB/BUND 引用", len(EIDX) == 60 and not [r for r in EIDX_REFS if r.startswith(("JGB", "BUND"))])
CAL_CNT = Counter(str(e.get("metric_id")) for e in CE)
CAL_JPEA = [e for e in CE if e.get("metric_id") in ("JP_POLICY_TARGET", "EA_HICP_YOY")]
sup("冻结日历 18 条: JP_POLICY_TARGET×2、EA_HICP_YOY×3,其余 13 条非日欧面;无 ECB 条目",
    len(CE) == 18 and CAL_CNT["JP_POLICY_TARGET"] == 2 and CAL_CNT["EA_HICP_YOY"] == 3 and len(CE) - len(CAL_JPEA) == 13
    and not [e for e in CE if "ECB" in (str(e.get("metric_id")) + str(e.get("entry_id"))).upper()])
sup("日历两条日本实录字段", (JPT["decision_date"], JPT["effective_on"], JPT["target_value"], JPT["kind"], JPT["basis"]) == ("2026-09-18", "2026-09-24", 1.25, "policy_decision", "user_directive")
    and (JPM["decision_date"], JPM["kind"], JPM["target_value"], "effective_on" in JPM) == ("2026-10-30", "policy_maintenance", 1.25, False))
EA_CAL = sorted(e["obs_from"][:7] for e in CE if e.get("metric_id") == "EA_HICP_YOY")
sup("日历 EA HICP 实录观测月 2021-05/2022-06/2025-03(不覆盖本窗)", EA_CAL == ["2021-05", "2022-06", "2025-03"], EA_CAL)

# ---- FX, assets, rates (mechanism links 3-4)
EJ_ = lambda d: EUR[d] * JPY[d]
for lab, got, exp in (("EURUSD 10-23", EUR[W0], 1.1221), ("EURUSD 11-20", EUR[W1], 1.0970), ("EURUSD 11-23", EUR[CUTOFF], 1.0940),
                      ("USDJPY 10-23", JPY[W0], 156.494), ("USDJPY 11-20", JPY[W1], 159.707), ("USDJPY 11-23", JPY[CUTOFF], 159.347),
                      ("DXY 10-23", DXY[W0], 101.81), ("DXY 11-20", DXY[W1], 103.81), ("DXY 11-23", DXY[CUTOFF], 104.079),
                      ("EURUSD 至11-20 %", chg(EUR, W0, W1), -2.24), ("EURUSD 至11-23 %", chg(EUR, W0, CUTOFF), -2.51),
                      ("USDJPY 至11-20 %", chg(JPY, W0, W1), 2.05), ("USDJPY 至11-23 %", chg(JPY, W0, CUTOFF), 1.82),
                      ("DXY 至11-20 %", chg(DXY, W0, W1), 1.96), ("DXY 至11-23 %", chg(DXY, W0, CUTOFF), 2.23),
                      ("EURJPY 合成 10-23", EJ_(W0), 175.61), ("EURJPY 合成 11-20", EJ_(W1), 175.19), ("EURJPY 合成 11-23", EJ_(CUTOFF), 174.32),
                      ("EURJPY 合成 至11-20 %", chg({"a": EJ_(W0), "b": EJ_(W1)}, "a", "b"), -0.24), ("EURJPY 合成 至11-23 %", chg({"a": EJ_(W0), "b": EJ_(CUTOFF)}, "a", "b"), -0.73),
                      ("UST_10Y 末值", U10[max(U10)], 5.04), ("联邦基金目标下限", FTL[CUTOFF], 3.75), ("联邦基金目标上限", FTU[CUTOFF], 4.0),
                      ("SPX 同日收盘 %", chg(SPX, W0, W1), -9.36), ("NIKKEI225 同日收盘 %", chg(NK, W0, W1), -9.98), ("DAX 同日收盘 %", chg(DAX, W0, W1), -1.50), ("CAC40 同日收盘 %", chg(CAC, W0, W1), 1.86),
                      ("跳升窗 SPX %", chg(SPX, "2026-11-13", W1), -8.61), ("跳升窗 NIKKEI225 %", chg(NK, "2026-11-13", W1), -7.70),
                      ("跳升窗 DAX %", chg(DAX, "2026-11-13", W1), -7.28), ("跳升窗 CAC40 %", chg(CAC, "2026-11-13", W1), -5.27),
                      ("SPX 11-05 日变动 %", chg(SPX, prevd(SPX, "2026-11-05"), "2026-11-05"), -4.36), ("NIKKEI225 11-06 日变动 %", chg(NK, prevd(NK, "2026-11-06"), "2026-11-06"), -5.96),
                      ("VIX 10-23", VIX[W0], 19.45), ("VIX 11-13", VIX["2026-11-13"], 19.30), ("VIX 11-16", VIX["2026-11-16"], 22.91), ("VIX 11-17", VIX["2026-11-17"], 25.46),
                      ("VIX 11-18", VIX["2026-11-18"], 24.56), ("VIX 11-19", VIX["2026-11-19"], 28.44), ("VIX 11-20", VIX[W1], 35.89), ("VIX 11-23", VIX[CUTOFF], 27.01),
                      ("VIX 至11-20 %", chg(VIX, W0, W1), 84.5), ("VIX 11-23 较 11-20 %", chg(VIX, W1, CUTOFF), -24.7), ("VIX 至11-23 %", chg(VIX, W0, CUTOFF), 38.87),
                      ("VIX 11-04", VIX["2026-11-04"], 16.61), ("VIX 11-05", VIX["2026-11-05"], 28.18), ("VIX 11-11", VIX["2026-11-11"], 17.49),
                      ("VIX 11-05 日变动 %", chg(VIX, "2026-11-04", "2026-11-05"), 69.66), ("VIX 11-11 较 11-05 %", chg(VIX, "2026-11-05", "2026-11-11"), -37.93),
                      ("VIX 11-16 日变动 %", chg(VIX, prevd(VIX, "2026-11-16"), "2026-11-16"), 18.70), ("VIX 11-20 日变动 %", chg(VIX, prevd(VIX, "2026-11-20"), "2026-11-20"), 26.20),
                      ("引擎回贴 SPX %", chg(SPX, W0, CUTOFF), -5.51), ("引擎回贴 DAX %", chg(DAX, W0, CUTOFF), 0.11),
                      ("引擎回贴 SPX 值", SPX[CUTOFF], 7203.85), ("引擎回贴 DAX 值", DAX[CUTOFF], 25209.45), ("NIKKEI225 11-20 值", NK[W1], 56436.65),
                      ("C2 USDJPY 水平", JPY[CUTOFF], 159.35), ("C2 SPX 水平", SPX[CUTOFF], 7203.85), ("C2 VIX 水平", VIX[CUTOFF], 27.01)):
    eqn(lab, got, exp)
VDPCT = {d: chg(VIX, prevd(VIX, d), d) for d in sorted(VIX) if W0 < d <= W1 and prevd(VIX, d) >= W0}
TOP_MONTH = sorted(VDPCT, key=lambda d: -VDPCT[d])[:3]
TOP_JUMP = sorted((d for d in VDPCT if d > "2026-11-13"), key=lambda d: -VDPCT[d])[:2]
N_TD = len([d for d in sorted(VIX) if "2026-11-05" < d <= "2026-11-11"])
FXD = max(abs(chg(EUR, prevd(EUR, d), d)) for d in ("2026-11-16", "2026-11-20")) , max(abs(chg(JPY, prevd(JPY, d), d)) for d in ("2026-11-16", "2026-11-20"))
sup("VIX 月窗内最大单日跳升前三 = 11-05/11-20/11-16;跳升窗(11-13→11-20)内前二 = 11-20/11-16",
    TOP_MONTH == ["2026-11-05", "2026-11-20", "2026-11-16"] and sorted(TOP_JUMP) == ["2026-11-16", "2026-11-20"], (TOP_MONTH, TOP_JUMP))
sup("先例: 11-05→11-11 四个交易日", N_TD == 4, N_TD)
sup("两日(11-16、11-20)欧元、日元对美元单日变动幅度均不超过 0.23%", max(FXD) <= 0.23 + 1e-9, FXD)
FTL_KS = sorted(FTL)
FTL_CH = [(a, b) for a, b in zip(FTL_KS, FTL_KS[1:]) if FTL[a] != FTL[b]]
sup("美联储序列(DFEDTARL,日历日逐日)最近变动 " + FTL_CH[-1][0] + "→" + FTL_CH[-1][1] + "(" + n(FTL[FTL_CH[-1][0]]) + "→" + n(FTL[FTL_CH[-1][1]]) + ",其后至截止日无变动;此前一次变动 " + FTL_CH[-2][0] + "→" + FTL_CH[-2][1] + ")",
    FTL_CH[-1] == ("2026-09-16", "2026-09-17") and FTL_CH[-2] == ("2025-12-10", "2025-12-11") and FTL["2026-09-16"] == 3.5 and FTL["2026-09-17"] == 3.75 and max(FTL) == CUTOFF and len(FTL_CH) > 2,
    (FTL_CH[-2:], FTL["2026-09-16"], FTL["2026-09-17"]))
sup("UST_10Y 末观测日 2026-11-19;SPX/DAX/VIX 截止日值 7203.85/25209.45/27.01;FOMC 纪要 2026-11-18",
    max(U10) == "2026-11-19" and len(RP["policy_doc_facts"]) == 1 and RP["policy_doc_facts"][0]["published_on"] == "2026-11-18" and RP["policy_doc_facts"][0]["doc_id"] == "FOMC-MINUTES-2026-10")
URT = RP["us_rates_trio"]
sup("美国三利率分解: 名义 Δ-8bp = 实际 Δ+11bp + 盈亏平衡 Δ-19bp,残差 0",
    (URT["chg_bp"]["UST_10Y"], URT["chg_bp"]["TIPS_10Y"], URT["chg_bp"]["BEI_10Y"], URT["identity_residual_bp"]) == (-8.0, 11.0, -19.0, 0.0)
    and round(URT["chg_bp"]["TIPS_10Y"] + URT["chg_bp"]["BEI_10Y"], 6) == URT["chg_bp"]["UST_10Y"] and (URT["window"]["from"], URT["window"]["to"]) == ("2026-10-20", "2026-11-19"))
sup("判断档 rates_decomposition 与引擎面同值", (J["reader_map"]["rates_decomposition"]["nominal_bp"], J["reader_map"]["rates_decomposition"]["real_bp"], J["reader_map"]["rates_decomposition"]["bei_bp"]) == (-8.0, 11.0, -19.0))
sup("判断档 asset_returns_echo 与引擎 asset_moves 同值", sorted((a["metric_id"], a["chg_pct"], a["window"]["from"], a["window"]["to"]) for a in J["reader_map"]["asset_returns_echo"])
    == sorted((a["metric_id"], a["chg_pct"], a["window"]["from"], a["window"]["to"]) for a in RP["asset_moves"]["rows"] if a["metric_id"] in ("SPX", "DAX", "NIKKEI225", "VIX")))

# ---- scenarios, analog, sync face
S1R, S2R = SCE[0]["rows"], SCE[1]["rows"]
PUB_OFF = {"EA_HICP_YOY": 16, "JP_CPI_YOY": 20}
ENTRY = {m_: (dt.date(2026, 12, 31) + dt.timedelta(days=o)).isoformat() for m_, o in PUB_OFF.items()}
sup("读数入档日(引擎规则 月末+16/+20)早于情景时限 2027-02-15;两情景 deadline 同值",
    all(v < "2027-02-15" for v in ENTRY.values()) and S1R["trigger"]["deadline"] == S2R["trigger"]["deadline"] == "2027-02-15", ENTRY)
sup("证伪/触发指标与敏感变量均在册", all(m_ in SS for m_ in (S1R["falsification"]["metric_id"], S2R["falsification"]["metric_id"], "VIX") + tuple(S1R["falsification"]["secondary_metric_ids"] + S2R["falsification"]["secondary_metric_ids"] + S1R["sensitive_variables"] + S2R["sensitive_variables"])))
sup("情景阈值文字在场", "3.5%" in S1R["falsification"]["threshold"] and "2.0%" in S1R["falsification"]["threshold"] and "1.5 个百分点" in S1R["falsification"]["threshold"]
    and "≥4.0%" in S1R["trigger"]["condition"] and "高于 30" in S1R["trigger"]["condition"] and "3.0%" in S2R["falsification"]["threshold"]
    and "低于 3.0%" in S2R["trigger"]["condition"] and "低于 25" in S2R["trigger"]["condition"])
sup("证伪条件不含 VIX;VIX 25–30 区间两情景均不触发", "VIX" not in S1R["falsification"]["threshold"] and "VIX" not in S2R["falsification"]["threshold"])
sup("截止日读数与 S1 前提相容、与 S2 前提相反", VE[10] >= 3.5 and VJ[10] >= 2.0 and GAP10 >= 1.5 and not (VE[10] < 3.0 and VJ[10] < 2.0))
sup("analog 面: 扫描 1871、有效 74、TOP1 2025-03 距离 0.727212;判断档引用三数一致",
    (S6["candidates"]["scanned"], S6["candidates"]["valid"], S6["top"][0]["candidate_month"]) == (1871, 74, "2025-03") and round(S6["top"][0]["distance"], 3) == 0.727
    and all(x in J["reader_map"]["history_zero_case_note"] for x in ("1871", "74", "2025-03", "0.727")))
sup("历史类比 0 段;全文无跨地区同步/相关系数主张", J["reader_map"]["history_periods"] == [] and all(JALL.count(w) == 0 for w in ("相关系数", "同步系数", "pearson", "皮尔逊")))
sup("引擎同步面 S5_compare 两侧 = EA_HICP_YOY × ECB_MRO(月格对齐,n_change_pairs=%d,变化基=pp)" % S5["alignment"]["n_change_pairs"],
    [s["metric_id"] for s in S5["sides"]] == ["EA_HICP_YOY", "ECB_MRO"] and S5["alignment"]["mode"] == "month_grid" and S5["change_basis"] == {"a": "pp", "b": "pp"})

# ---- time point, wording, rendering fidelity
LATE = sorted(set(re.findall(r"20\d\d-\d\d-\d\d", "\n".join(v for p_, v in LV if isinstance(v, str) and p_[0] != "agent_declaration"))))
LATE = [t for t in LATE if t > CUTOFF]
sup("判断档晚于截止日的日期记号仅请求月末 2026-11-30 与情景时限 2027-02-15", LATE == ["2026-11-30", "2027-02-15"], LATE)
sup("全文「无变化」0 次;「维持不变」仅日历维持条目语境;「STALE」0 次;「全为周三」0 次",
    JALL.count("无变化") == 0 and JALL.count("维持不变") == 3 and JALL.count("STALE") == 0 and JALL.count("全为周三") == 0)
N_OCC, BAD_OCC = 0, []
for _s in ALLSTR:
    for _d in ("2026-06-11", "2026-09-10"):
        for _m in re.finditer(re.escape(_d), _s):
            N_OCC += 1
            _a = max(_s.rfind("。", 0, _m.start()), _s.rfind(";", 0, _m.start())) + 1
            _b = min([x for x in (_s.find("。", _m.end()), _s.find(";", _m.end()), len(_s)) if x >= 0])
            if not any(k in _s[_a:_b] for k in ("回推", "惯例", "推断")):
                BAD_OCC.append((_s[_a:_b][:80]))
sup("两处引擎回推决议日在全文 %d 处出现,所在句均带 回推/惯例/推断 标注" % N_OCC, N_OCC > 0 and not BAD_OCC, BAD_OCC)
norm = lambda s: "".join(s.split())
MAPN, FULLN = norm(MAP), norm(FULL)
LVS = [(p, v) for p, v in LV if isinstance(v, str) and len(v) >= 12 and not v.startswith("2026-")]
N_LV = len(LVS)
MAP_FOUND = sum(1 for _, v in LVS if norm(v) in MAPN)
FULL_FOUND = sum(1 for _, v in LVS if norm(v) in FULLN)


def unrendered(path):
    v = getp(J, path)
    return isinstance(v, str) and norm(v) not in MAPN and norm(v) not in FULLN


UNR_VN = [i for i in range(3) if unrendered(["reader_map", "transmission", 0, "links", i, "verdict_note"])]
UNR_NAR = [i for i in range(3) if unrendered(["reader_map", "turnings", i, "narrative"])]
UNR_QGN = [i for i in range(len(QGN)) if unrendered(["quality_gate_notes", i])]
UNR_AD = [k for k in J["agent_declaration"] if len(str(J["agent_declaration"][k])) >= 12 and not str(J["agent_declaration"][k]).startswith("2026-") and unrendered(["agent_declaration", k])]
REN_M = {k: all(norm(getp(J, ["reader_map", "transmission", 0, "links", i, k])) in MAPN for i in range(3))
         for k in ("observed_fact", "causal_hypothesis", "competing_explanation", "main_predicts", "competing_predicts", "face_off_verdict", "verdict_note")}
REN_F = {k: all(norm(getp(J, ["reader_map", "transmission", 0, "links", i, k])) in FULLN for i in range(3))
         for k in ("observed_fact", "causal_hypothesis", "competing_explanation", "main_predicts", "competing_predicts", "face_off_verdict", "verdict_note")}
sup("渲染忠实度: 判断档字符串叶(len≥12)%d 个,MAP 逐字命中 %d、FULL 命中 %d;verdict_note×3/turnings narrative×3/quality_gate_notes×6/declaration×%d 两报告均未渲染" % (
    N_LV, MAP_FOUND, FULL_FOUND, len(UNR_AD)), len(UNR_VN) == 3 and len(UNR_NAR) == 3 and len(UNR_QGN) == 6 and len(UNR_AD) == 4, (UNR_VN, UNR_NAR, UNR_QGN, UNR_AD))
sup("传导三环的 causal_hypothesis / competing_explanation / main_predicts / competing_predicts / face_off_verdict 在 MAP 逐字渲染",
    all(REN_M[k] for k in REN_M if k != "verdict_note") and not REN_M["verdict_note"], REN_M)
RA = SNAP["research_as_of"]
sup("研究截止=快照 research_as_of=%s(与窗端同值);截止日值标注为盘中快照" % RA, RA == "2026-11-23T22:53:47+08:00" and RA in JALL and "盘中快照、非收盘价" in JALL)
_T0 = dt.datetime.strptime(RA, "%Y-%m-%dT%H:%M:%S%z")
TZS = {c: _T0.astimezone(dt.timezone(dt.timedelta(hours=o))).strftime("%H:%M") for c, o in (("纽约", -5), ("柏林", 1), ("东京", 9), ("上海", 8))}
sup("时区换算 纽约/柏林/东京/上海 = %s" % "/".join(TZS[c] for c in ("纽约", "柏林", "东京", "上海")),
    TZS == {"纽约": "09:53", "柏林": "15:53", "东京": "23:53", "上海": "22:53"} and all(v in QGN[4] for v in ("纽约 09:53", "柏林 15:53", "东京 23:53", "上海 22:53")), TZS)

# ---- contract verification / attach block (report.json)
WR = dt.datetime.strptime(J["agent_declaration"]["written_at"], "%Y-%m-%dT%H:%M:%S%z")
ATT = dt.datetime.strptime(EJ["attached_at"], "%Y%m%dT%H%M%SZ").replace(tzinfo=dt.timezone.utc)
EMB_NULL = [k for k in ("agent_declaration", "l3", "l4", "reader_map", "quality_gate_notes") if EJ.get(k) is None]
CV_TOK_OK = all(v["token"] in CON[1]["statement"] for v in CV["verdicts"]) and (
    round(FACTS["ECB_DFR@2026-09-16"]["value"], 2), round(JPR["2026-10-01"], 3), round(JPY[CUTOFF], 2), round(SPX[CUTOFF], 2), round(VIX[CUTOFF], 2)) == tuple(v["value"] for v in CV["verdicts"])
MC = CV["map_checks"]
sup("契约验证数值串 %d 个均在受审 C2 陈述内且值与序列/事实面一致" % len(CV["verdicts"]), CV_TOK_OK)
sup("契约 map_checks 与受审文件一致(日期次序主张、传导链 id、转折指标来源)",
    "2026-09-29 晚于 BOJ 决议日 2026-09-18" in TNS[2]["follow_or_diverge"] and J["reader_map"]["transmission"][0]["chain_id"] == "CH-INFL-POLICY-RISKOFF"
    and all(t["metric_id"] in [c["metric_id"] for c in RP["turning_candidates"]["candidates"]] for t in TNS) and all(m["status"] == "VERIFIED" for m in MC))
sup("挂接校验块计数与受审文件一致(3 条矛盾陈述/1 条机制链/2 个情景)",
    EJ["validation"]["passed"] is True and (EJ["validation"]["n_contradictions"], EJ["validation"]["n_mechanism_chains"], EJ["validation"]["n_scenarios"]) == (len(CON), len(J["l3"]["mechanism_chains"]), len(SCE)))
sup("report.json 内嵌 agent_judgment 的正文五键均为 null(仅挂接元数据)", EMB_NULL == ["agent_declaration", "l3", "l4", "reader_map", "quality_gate_notes"], EMB_NULL)
sup("挂接时刻晚于判断档书写时刻(attached_at=%s,written_at=%s)" % (EJ["attached_at"], WR.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")), ATT > WR)
sup("run.git_head 与 MAP 印章同值", R["run"]["git_head"] == GIT_HEAD and GIT_HEAD in MAP)

# ---- reader-report lines quoted in the engine observations
L_HEAD, L_COV, L_WED, L_BP, L_FOH, L_KOU, L_PEAR, L_FULLHEAD = (line_of(MAPL, "## 四地三时点环境对照"), line_of(MAPL, "4/4组ok"),
    line_of(MAPL, "ECB_MRO/ECB_DFR 观测日全为周三"), line_of(MAPL, "Δ+20bp"), line_of(MAPL, "| 区分指标 | 主解释预期 | 竞争解释预期 | 已有观测 | 判断 |"),
    line_of(MAPL, "⚠未核验=无更晚已证实决议"), line_of(FULLL, "pearson = 0.264"), line_of(FULLL, "# 完整研究报告"))
L_TK = line_of(MAPL, CELLS["JP_CPI_TOKYO_YOY"]["anchors"]["最新一期"]["publication_rule"])
L_GAP = line_of(MAPL, "JP_POLICY_TARGET 不在注册表")
L_6M = [i + 1 for i, l in enumerate(MAPL) if "| 6个月前 |" in l and "——2026-09 决议 09-10、生效 09-16" in l and "2025-06-05" in l]
L_TKROW = [i + 1 for i, l in enumerate(MAPL) if "东京都" in l and l.startswith("| JP") and "| ok |" in l]

# ---- engine sources (optional; text-searched only, never imported or executed)
SRC = {os.path.basename(p): rd(p) for p in ENGINE_SRC}
ENG_ON = len(SRC) == 4
JCS, TCS, MPS, EGS = (SRC.get(k, "") for k in ("judgment_contract.py", "text_consistency.py", "research_map_planner.py", "evidence_gate.py"))
NOAL = ("JP_CPI_YOY", "EA_HICP_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_TARGET", "ECB_MRO")
_b = MPS.find("def _hist_region_reading(")
_body = MPS[_b:MPS.find("\ndef ", _b + 1)] if _b >= 0 else ""
ENG_CHK = {
    "E8 契约锚标签硬编码": "def _map_checks(" in JCS and "for _lbl in ('12个月前', '3个月前', '最新一期'):" in JCS,
    "E8 别名表未覆盖五指标": "ALIASES = {" in TCS and all(TCS.count(m_) == 0 for m_ in NOAL),
    "E11 历史截止视图两入口": all(k in MPS for k in ("def _hist_series(", "def _hist_region_reading(", "def _aof_first_pub(")) and "_aof_first_pub(" in _body,
    "E11 可见性入口": "def is_historical_view(" in EGS and "def visible_publish(" in EGS,
}

# ---- verbatim quotes used in the narrative
Q_SNAP_ISSUE = FACTS["ECB_MRO@2026-09-16"]["issues"][0]["message"]
Q_GATE_NOTE = GA["note"]
Q_DET_TOKYO, Q_DET_BUND, Q_DET_GDP = GA["noncore_missing_detail"]["JP_CPI_TOKYO_YOY"], GA["noncore_missing_detail"]["BUND_10Y"], GA["noncore_missing_detail"]["EA_REAL_GDP_YOY"]
Q_REG_JPCALC = need("各自基期内做严格同月同比后拼接", REGM["JP_CPI_YOY"]["calc"])
Q_REG_JPCALC2 = need("与官方公布值抽验一致(2026-09=2.16 vs 官方2.1)", REGM["JP_CPI_YOY"]["calc"])
Q_REG_JPCOV = need("覆盖2021-01..2026-09", REGM["JP_CPI_YOY"]["calc"])
Q_REG_TKCALC = need("基期内同月同比仅2026-01..2026-10 十个月", REGM["JP_CPI_TOKYO_YOY"]["calc"])
Q_REG_TKREL = need("每月下旬发布当月东京都区部", REGM["JP_CPI_TOKYO_YOY"]["release_semantics"])
Q_REG_ECBREL = need("决议公布后生效并当日更新系列", REGM["ECB_MRO"]["release_semantics"])
Q_REG_ECBCALC = need("管委会决议变更即时生效", REGM["ECB_MRO"]["calc"])
Q_REG_DDN = need("无更晚已证实决议不作过期", REGM["ECB_MRO"]["freshness"]["decision_dated_note"])
Q_ENG_DECNOTE = CELLS["ECB_MRO"]["anchors"]["6个月前"]["policy_dates"]["decision_note"]
Q_ENG_PUBRULE = need(CELLS["ECB_MRO"]["anchors"]["最新一期"]["publication_rule"], RTXT)
Q_MAP_TOKYO = need(CELLS["JP_CPI_TOKYO_YOY"]["anchors"]["最新一期"]["publication_rule"], MAP)
Q_ENG_STALE = CVNV[0]["note"]
Q_ENG_FACE = CELLS["ECB_MRO"]["policy_face"]["face"]
Q_VINT_RET = CELLS["EA_HICP_YOY"]["anchors"]["最新一期"]["vintage"]
Q_VINT_COL = CELLS["JP_CPI_TOKYO_YOY"]["anchors"]["最新一期"]["vintage"]
Q_MAP_WED = need("ECB_MRO/ECB_DFR 观测日全为周三", MAP)
Q_MAP_HEAD = need("## 四地三时点环境对照", MAP)
Q_MAP_COV = [l for l in MAPL if "4/4组ok" in l][0].strip()
Q_MAP_BP = [l for l in MAPL if "Δ+20bp" in l][0].strip()
Q_MAP_KOU = [l for l in MAPL if "⚠未核验" in l][0].strip()
Q_FULL_PEAR = [l for l in FULLL if "pearson = 0.264" in l][0].strip()
for _q in (Q_SNAP_ISSUE, Q_GATE_NOTE, Q_DET_TOKYO, Q_DET_BUND, Q_DET_GDP, Q_ENG_DECNOTE, Q_ENG_STALE, Q_ENG_FACE, Q_VINT_RET, Q_VINT_COL):
    need(_q, RTXT, SNAPTXT)

# ======================================================================
# issue list (original sentences are cut verbatim out of the judgment; never retyped)
# ======================================================================
ITEMS = []


def cut(path, start, end=None, keep_end=False):
    txt = getp(J, path)
    assert isinstance(txt, str), path
    assert txt.count(start) == 1, ("cut start not unique", path, start, txt.count(start))
    i = txt.index(start) + len(start)
    if end is None:
        return start
    j = txt.find(end, i)
    assert j >= 0, ("cut end not found", path, end)
    return start + txt[i:(j + len(end) if keep_end else j)]


def item(sev, where, note, path=None, start=None, end=None, keep_end=False, fix=""):
    original = cut(path, start, end, keep_end) if path is not None else ""
    assert original and any(original in c for c in CORPUS), (sev, where, original[:60])
    ITEMS.append({"severity": sev, "where": "agent_judgment.json: " + where, "note": note, "original": original, "fix": fix})


PC_, LK_P, TR_P, TN_P, RG_P = ["l3", "contradictions"], ["l3", "mechanism_chains", 0, "links"], ["reader_map", "transmission", 0, "links"], ["reader_map", "turnings"], ["reader_map", "regions"]
item("MINOR", "l3.contradictions[1].statement(C2,「升至最新水平 2.5%」处)",
     "C2 称存款便利利率升至最新水平 2.5%%,该处未附序列止于 2026-09-16、其后决议面不可见的提示;C3② 与读者地图标题、欧元区行有该提示(距截止 %d 天、Gate A 列 degraded、【尚未验证】),全文口径一致,"
     "数值无误。矛盾陈述是归档与转引的单元,宜就地带一句限定。结论不变。" % DD["d68"],
     path=PC_ + [1, "statement"], start="升至最新水平 2.5%", end=";主要再融资利率",
     fix="升至序列末观测水平 2.5%(观测=序列变更日=生效日 2026-09-16;L1 quality_status=DEGRADED——序列止于该日,其后决议面不可见【尚未验证】,详见「证据不足」第②项)")
item("MINOR", "l3.contradictions[0].statement(C1,日本全国 CPI 读数处)",
     "日本全国 CPI 同比在注册表 calc 中为引擎自算值(「" + Q_REG_JPCALC + "」," + Q_REG_JPCALC2 + ")。C1 对东京都序列点明了速报先行口径、序列自 2026-01 起、Gate A 列 noncore_missing,"
     "对全国序列的自算口径未作同样提示;点值与快照序列面逐位一致。结论不变。",
     path=PC_ + [0, "statement"], start="日本全国CPI同比百分之二点四四", end="引擎推定规则、非日历实录)", keep_end=True,
     fix="日本全国CPI同比百分之二点四四(观测 2026-10,发布 2026-11-20,引擎推定规则、非日历实录;注册表注记该序列为双基期档各自同月同比后拼接的引擎自算值,与官方公布值抽验 2026-09 为 2.16 对官方 2.1)")
item("MINOR", "l3.contradictions[2].statement(C3,「可核者五项」)",
     "五项之外另有一处两地对照不对称的缺席未列: 欧元区国债收益率 BUND_10Y/BUND_2Y 当日快照 Gate A 列于 noncore_missing(注记=「" + Q_DET_BUND + "」),而日本端 JGB2Y/JGB5Y/JGB10Y 事实行在场"
     "(2026-11-19: %s,%s)且不在 %d 行证据索引内;两地利率期限结构一维因此无法对照。属披露可改进,不改变已有结论。" % (
         "/".join(str(v) for v, _ in JGBV), "/".join(sorted(set(q for _, q in JGBV))), len(EIDX)),
     path=PC_ + [2, "statement"], start="问句所求「证据不足」面,引擎可核者五项。",
     fix="问句所求「证据不足」面,引擎可核者六项(增第⑥项: 欧元区国债收益率 BUND_10Y/BUND_2Y 当日快照 Gate A 列于缺席名单,日本端 JGB 各期限事实行在场,两地利率期限结构对照不对称)。")
item("MINOR", "reader_map.turnings[2].first_mover(东京都 CPI 转折行)",
     "该转折行以 JP_CPI_TOKYO_YOY(2026-06→2026-09,1.6→2.69)为先行指标,该序列当日快照 Gate A 列于 noncore_missing、L1 无事实行;C1 与读者地图日本行有披露,但转折行内未带标记,单看该行不知其为缺席序列上的读数。"
     "候选面命中属实(research_plan.turning_candidates 第三条同值)。结论不变。",
     path=TN_P + [2, "first_mover"], start="东京都 CPI 同比(速报先行口径)", end="(三个月 +1.09 个百分点)。", keep_end=True,
     fix="东京都 CPI 同比(速报先行口径;该序列当日快照 Gate A 列于 noncore_missing,读数取自快照序列面、L1 无对应事实行)2026-06→2026-09 由 1.6 升至 2.69(三个月 +1.09 个百分点)。")
item("MINOR", "reader_map.transmission[0].links[0..2](对质表三行)及各行的 verdict_note",
     "对质表读者可见的只有主解释预期、竞争解释预期与尚不能区分;支撑该裁定的理由均在未被渲染进读者报告的 verdict_note 里(环1: 欧央行 n=2,读数驱动与程序驱动均与观测相容;环2: 主解释预期未纳入美元端利率,两货币对美元同向,两解释在该观测上预期未分立;"
     "环3: 跳升时点不与政策日历对齐、竞争解释在时点上占优,但其快速回落预期仅有一个盘中观测)。判断档字符串叶(len≥12)在 MAP_REPORT.md 命中 %d/%d、FULL_REPORT.md 命中 %d/%d。"
     "无理由的尚不能区分易被读作两解释证据相等;裁定本身保守、不违反证据,列 MINOR。" % (MAP_FOUND, N_LV, FULL_FOUND, N_LV),
     path=TR_P + [1, "main_predicts"], start="主解释(利差主导)预期 EURUSD/USDJPY 对政策差变动敏感、方向分立",
     fix="对质表每行增列一句裁定理由(取自 verdict_note),例如环2: 该预期未纳入美元端利率(UST_10Y 最新 5.04%),两货币对美元同向,两解释在该观测上预期未分立;EURJPY 交叉盘不在证据面,以 EURUSD×USDJPY 推算幅度小(-0.24%/-0.73%)。")
item("MINOR", "l3.contradictions[1].statement(C2,欧央行决议日处)及 reader_map.transmission[0].links[0].main_predicts(环1)",
     "欧央行决议日按引擎生效日前上一个周四的惯例回推并标【推断】,处理正确;但注册表对同一序列的 release_semantics/calc 写的是「" + Q_REG_ECBREL + "」「" + Q_REG_ECBCALC + "」,与引擎惯例不一致,判断档只报引擎口径、未提示两面不一。"
     "环1 据回推决议日计算决议日前可见读数(2026-04=3.0 对 2026-05=3.2;2026-07=2.9 对 2026-08=3.2),该差别依赖未经实录证实的日期;环1 同时给出生效日前口径,结论(尚不能区分)不受影响。",
     path=PC_ + [1, "statement"], start="决议日系引擎按『生效日前上一个周四』惯例自变更日回推", end="属【推断】而非实录(冻结发布日历对欧央行无实录条目)", keep_end=True,
     fix="决议日系引擎按『生效日前上一个周四』惯例自变更日回推、属【推断】而非实录(冻结发布日历对欧央行无实录条目;注册表该序列 release_semantics 另载决议公布后生效并当日更新系列,两口径不一,以序列变更日=生效日为实证面)")
item("MINOR", "l3.contradictions[2].statement(C3②,欧央行序列降级处)",
     "C3② 把两条欧央行序列的 DEGRADED 归因于观测日距截止 %d 天、超过注册表新鲜度阈十天。引擎各面对此并不一致: 快照事实行 issues 记「%s」并列 noncore_degraded;契约验证记 STALE;"
     "而注册表 freshness 对该序列设 decision_dated=true(「%s」),研究计划点值格最新一期锚记 status=ok、freshness_basis=policy_confirmation。判断档采信了降级一面并如实写其后是否有新决议不可判【尚未验证】,未提另一面;"
     "其后决议面不可见的结论本身成立,列披露可改进。" % (DD["d68"], Q_SNAP_ISSUE, Q_REG_DDN),
     path=PC_ + [2, "statement"], start="观测日距研究截止 2026-11-23 六十八天", end="当日快照 Gate A 将该两序列列于降级名单(L1 事实行 quality_status=DEGRADED)", keep_end=True,
     fix="观测日距研究截止 2026-11-23 六十八天,超过注册表新鲜度阈十天,当日快照 Gate A 将该两序列列于降级名单(L1 事实行 quality_status=DEGRADED;注册表 freshness 另设 decision_dated 规则——无更晚已证实决议不作过期,而研究计划点值格记该锚 status=ok,引擎各面不一,故降级是否成立与其后是否有新决议在引擎面同样不可判)")
EA_AN6 = CELLS["EA_HICP_YOY"]["anchors"]["6个月前"]
EA_PUB_WK, EA_RULE = str(EA_AN6["publication_date"]), str(EA_AN6["publication_rule"])
N_EA_PUB_WK = sum(v.count("2026-05-16") for _p, v in LV if isinstance(v, str) and _p[0] != "agent_declaration")
assert EA_PUB_WK == "2026-05-16" and D(EA_PUB_WK).weekday() == 5 and "月末+16天" in EA_RULE and "该推定日落在周日" in JALL and D("2026-08-30").weekday() == 6 and N_EA_PUB_WK == 1
item("MINOR", "reader_map.regions[0].from_to(欧元区行,「发布 2026-05-16」处)",
     "欧元区 2026-04 期读数的引擎推定发布日 %s 落在周六(引擎规则「%s」推算所得,不可能是实际发布日);句中已标引擎推定规则、非日历实录,但未如东京都 2026-08 期推定日处(2026-08-30,句中已点明落在周日)那样点明落在周末。"
     "该日期在判断档正文仅此一处、只作六个月前锚的发布面标注;锚取值(观测月 2026-04 的 %s)与各处可见性结论均不依赖它。披露可改进,结论不变。" % (EA_PUB_WK, EA_RULE, p1(mo(EA, 2026, 4))),
     path=RG_P + [0, "from_to"], start="发布 2026-05-16,引擎推定规则、非日历实录",
     fix="发布 2026-05-16(周六;引擎月末+16 天推定规则、非日历实录,实际发布日以官方实录为准)")
item("NIT", "l3.mechanism_chains[0].links[3].text(环4,「为窗内两个最大单日跳升日」)",
     "该句以跳升窗(2026-11-13→2026-11-20)为窗内;同段前文的窗是月窗(2026-10-23 起),月窗内最大单日跳升是 2026-11-05(+%s%%)。句首已写跳升窗内含…,歧义有限。" % n(VDPCT["2026-11-05"]),
     path=LK_P + [3, "text"], start="为窗内两个最大单日跳升日", fix="为跳升窗内两个最大单日跳升日")
item("NIT", "l3.contradictions[2].statement(C3②)与契约验证非 VERIFIED 项的对应关系",
     "契约验证 %d 个数值串中 1 个状态为 STALE(对象 C2 的 2.5%% 数值串,值与期望值相等,状态 STALE 与该事实行的降级状态同现;引擎注记=「%s」);判断档披露了序列止于 2026-09-16 与 DEGRADED,但未点名该项 STALE,读者无法把契约面的非 VERIFIED 项与文字面对上。实质已披露。" % (len(CV["verdicts"]), Q_ENG_STALE),
     path=PC_ + [2, "statement"], start="当日快照 Gate A 将该两序列列于降级名单(L1 事实行 quality_status=DEGRADED)",
     fix="在「证据不足」第②项末补一句: 契约验证对该 2.5% 数值串记 STALE(该事实行 DEGRADED、观测滞后 68 天)。")
item("NIT", "l3.contradictions[2].statement(C3③,「冻结日历实录仅覆盖…」)",
     "冻结日历共 %d 条,除日本政策目标 %d 条与 EA HICP 历史期 %d 条外,另有非日欧面实录 %d 条;「仅覆盖」在日欧语境下成立,宜加「日欧面」限定。" % (len(CE), CAL_CNT["JP_POLICY_TARGET"], CAL_CNT["EA_HICP_YOY"], len(CE) - len(CAL_JPEA)),
     path=PC_ + [2, "statement"], start="冻结日历实录仅覆盖日本政策目标两条与三条历史期 EA HICP 快报/终值实录",
     fix="冻结日历实录于日欧面仅覆盖日本政策目标两条与三条历史期 EA HICP 快报/终值实录")
item("NIT", "l3.mechanism_chains[0].links[1].text(环2,「决议即…生效」)",
     "「2026-09-18 决议即 2026-09-24 生效」中的「即」易读作当日生效;两者相隔 %d 天(与日历条 effective_on 一致)。读者地图日本行写作决议、2026-09-24 生效,无此问题。" % DD["d6b"],
     path=LK_P + [1, "text"], start="BOJ 2026-09-18 决议即 2026-09-24 生效", fix="BOJ 2026-09-18 决议、2026-09-24 生效")
def _me(y, m_):
    return dt.date(y + (1 if m_ == 12 else 0), (m_ % 12) + 1, 1) - dt.timedelta(days=1)


EA_MAY_PUB, JP_MAY_PUB = [(_me(2026, 5) + dt.timedelta(days=k)).isoformat() for k in (16, 20)]
assert CELLS["EA_HICP_YOY"]["anchors"]["最新一期"]["publication_date"] == (_me(2026, 10) + dt.timedelta(days=16)).isoformat() == "2026-11-16"
assert CELLS["JP_CPI_YOY"]["anchors"]["最新一期"]["publication_date"] == (_me(2026, 10) + dt.timedelta(days=20)).isoformat() == "2026-11-20"
assert CELLS["EA_HICP_YOY"]["anchors"]["6个月前"]["publication_date"] == (_me(2026, 4) + dt.timedelta(days=16)).isoformat() == "2026-05-16"
assert CELLS["JP_CPI_YOY"]["anchors"]["6个月前"]["publication_date"] == (_me(2026, 4) + dt.timedelta(days=20)).isoformat() == "2026-05-20"
assert "月末+16天" in CELLS["EA_HICP_YOY"]["anchors"]["最新一期"]["publication_rule"] and "月末+20天" in CELLS["JP_CPI_YOY"]["anchors"]["最新一期"]["publication_rule"]
assert EA_MAY_PUB == "2026-06-16" and JP_MAY_PUB == "2026-06-20" and "2026-05 期观测日在窗起 2026-05-23 之前、推定发布日在窗内" in JALL
item("NIT", "reader_map.regions[0].from_to(欧元区行,「窗内月度路径 3.2(2026-05)」)",
     "2026-05 期的观测日(2026-05-01)早于窗起 2026-05-23,按引擎推定规则(月末+%d 天)其发布日为 %s,在窗内;机制链环1 对此有说明,读者地图欧元区行直接称窗内月度路径。日本行同构(2026-05 期推定发布日 %s)。" % (
         16, EA_MAY_PUB, JP_MAY_PUB),
     path=RG_P + [0, "from_to"], start="窗内月度路径 3.2(2026-05)", fix="窗内可见月度路径 3.2(2026-05)→…(2026-05 期观测日早于窗起、发布日在窗内)")
item("NIT", "l3.mechanism_chains[0].links[2].text(环3,「UST_10Y 最新 5.04%」)",
     "UST_10Y 的 5.04%% 为 %s 观测(该序列末观测日),非截止日 %s;句中未写观测日。" % (max(U10), CUTOFF),
     path=LK_P + [2, "text"], start="UST_10Y 最新 5.04%", fix="UST_10Y 最新 5.04%(观测 2026-11-19)")
item("NIT", "l4.scenarios[*].rows.trigger / falsification 与 quality_gate_notes[3]",
     "两情景的触发条件含 VIX 分量(S1 高于 30、S2 低于 25),证伪条件均不含 VIX: VIX 收盘落在 25–30 之间时两情景均不触发、亦不因此证伪;另 S1 触发阈(≥4.0%)高于其前提水平(3.5% 以上),3.5%–4.0% 区间同样是前提成立、不触发、不证伪。"
     "quality_gate_notes 只披露了 S2 的 3.0%–3.5% 放宽区间。",
     path=["quality_gate_notes", 3], start="S2 证伪阈值(3.5%)较前提水平(3.0% 以下)放宽", end="区间不触发亦不证伪", keep_end=True,
     fix="…3.0%–3.5% 区间不触发亦不证伪;S1 触发阈 4.0% 高于前提水平 3.5%,3.5%–4.0% 区间同属前提成立而不触发;VIX 收盘在 25–30 之间时两情景均不触发。")
item("NIT", "l3.mechanism_chains[0].links[1].text(环2 标题「观察: 政策面跟进」)",
     "该环证据级别为 E1(观察),正文对月均台阶只写相容、不作相容性判断;标题「跟进」带因果意味,与正文的自制口径略不称。",
     path=LK_P + [1, "text"], start="观察: 政策面跟进", fix="观察: 政策面同向变更")
item("NIT", "reader_map.regions[1].from_to(日本行,「中旬速报先行口径」)",
     "注册表对该序列的发布说明为「%s」,引擎推定规则为「%s」;「中旬」与月末−1 天的推定日不对应。" % (Q_REG_TKREL, Q_MAP_TOKYO),
     path=RG_P + [1, "from_to"], start="中旬速报先行口径", fix="速报先行口径")
item("NIT", "reader_map.regions[1].from_to(日本行,「此后总体回升」)",
     "2026-02 之后全国 CPI 同比由 %s 升至 %s 属实,但路径非逐月单调(2026-03 的 %s→2026-04 的 %s 有一次 %s 个百分点的小幅回落);同句对回落段的两次小幅回升(2025-09、2025-10)作了注明,对回升段的这次小幅回落未注明。" % (
         n(VJ[2]), n(VJ[10]), n(VJ[3]), n(VJ[4]), n(JP_DIP)),
     path=RG_P + [1, "from_to"], start="此后总体回升", fix="此后总体回升(2026-04 一次小幅回落)")
N_MIN = sum(1 for it in ITEMS if it["severity"] == "MINOR")
N_NIT = sum(1 for it in ITEMS if it["severity"] == "NIT")
N_MAJ = sum(1 for it in ITEMS if it["severity"] == "MAJOR")
assert (N_MAJ, N_MIN, N_NIT) == (0, 8, 10), (N_MAJ, N_MIN, N_NIT)
# ======================================================================
# part D -- additional derived facts, counter-attacks, engine-face observations, six checks, notes
# ======================================================================
GAPM = {"2026-%02d" % i: round(VE[i] - VJ[i], 2) for i in range(5, 11)}
GAPM_MIN, GAPM_MAX = min(GAPM, key=GAPM.get), max(GAPM, key=GAPM.get)
ALT = (round(VE[10] - mo(EA, 2025, 9), 2), round(mo(JPC, 2025, 9) - VJ[10], 2))


def fxv(dct, d, k):
    """currency level with the precision the judgment itself uses (EURUSD 4 / USDJPY 3 / DXY >=2 decimals)"""
    s_ = ("%." + str(d) + "f") % dct[k]
    if dct is DXY:
        s_ = s_.rstrip("0")
        s_ += "0" * max(0, 2 - len(s_.split(".")[1]))
    return s_


def f2(v):
    return "%.2f" % v


def f3(v):
    return "%.3f" % v


def sgn(v):
    return "+" if v > 0 else ("−" if v < 0 else "")


def sg2(v):
    return sgn(v) + f2(abs(v))


def sp1(v):
    return sgn(v) + p1(abs(v))
REG_INFL = sorted(k for k in REGM if REGM[k].get("economy") in ("JP", "EA") and re.search(r"CPI|HICP", k))
sup("注册表 JP/EA 面通胀序列 = %s" % "/".join(REG_INFL), REG_INFL == ["EA_HICP_YOY", "JP_CPI_TOKYO_YOY", "JP_CPI_YOY"], REG_INFL)
sup("C1/C2 各带两条竞争解释且有【假设】标记", all(json.dumps(CON[i], ensure_ascii=False).count("【假设】") >= 2 for i in (0, 1)),
    [json.dumps(CON[i], ensure_ascii=False).count("【假设】") for i in range(3)])
sup("机制链四环证据级别 E1,E1,E2,E2 且 E2 两环带缺环注记字段 %s" % "/".join(MLN) if (MLN := [k for k in LKS[2] if "missing" in k]) else "机制链证据级别",
    [l.get("evidence_level") for l in LKS] == ["E1", "E1", "E2", "E2"] and bool(MLN) and all(k in LKS[3] for k in MLN), (MLN, [l.get("evidence_level") for l in LKS]))
REFS_ALL = [r for c in CON for r in c.get("evidence_refs", [])] + [r for l in LKS for r in l.get("evidence_refs", [])]
N_REF = [len(c.get("evidence_refs", [])) for c in CON] + [len(l.get("evidence_refs", [])) for l in LKS]
REF_D = sorted(set(re.findall(r"@(\d{4}-\d\d-\d\d)", "\n".join(REFS_ALL))))
sup("矛盾陈述与机制链引用 %s=%d 条全部在证据索引,观测日全部不晚于截止日" % ("+".join(str(x) for x in N_REF), len(REFS_ALL)),
    all(r in EIDX_REFS for r in REFS_ALL) and len(REFS_ALL) == 21 and bool(REF_D) and max(REF_D) <= CUTOFF, (N_REF, REF_D))
WMM_LEAF = [(p, v) for p, v in LV if isinstance(v, str) and "维持不变" in v]
WMM = [(jpath(p), v[max(0, v.find("维持不变") - 24):v.find("维持不变") + 12]) for p, v in WMM_LEAF]
sup("「维持不变」%d 处均在含 2026-10-30 的叶子(日央行确认维持)或 l4 情景内" % len(WMM), all(("2026-10-30" in v or p[0] == "l4") for p, v in WMM_LEAF), WMM)
PLAN_PUB = set(str(v.get("publication_date")) for c in RP["point_values"]["cells"] for v in c["anchors"].values())
WK = []
for c in RP["point_values"]["cells"]:
    for a, v in c["anchors"].items():
        if str(v.get("publication_date") or "") >= "2025-01-01" and D(str(v.get("publication_date"))).weekday() >= 5:
            WK.append(c["metric_id"] + "/" + a + "@" + str(v.get("publication_date")))
RPTXT = json.dumps(RP, ensure_ascii=False)
RP_WK = sorted(set(d for d in re.findall(r"20\d\d-\d\d-\d\d", RPTXT) if "2025-06-01" <= d <= CUTOFF and D(d).weekday() >= 5))
CITED = sorted(set(re.findall(r"2026-\d\d-\d\d", "\n".join(v for p, v in LV if isinstance(v, str) and p[0] != "agent_declaration"))))
CITED_PUB = [d for d in CITED if d in PLAN_PUB]
CITED_WK = [d for d in CITED if D(d).weekday() >= 5 and d != CALE.get("updated")]
WKD = {d: ("周六" if D(d).weekday() == 5 else "周日") for d in CITED_WK}
sup("判断档正文落周末的日期记号 %d 个(日历版本日 %s 除外): 窗起日 2026-05-23(%s,六个月窗起点)、欧元区 2026-04 期推定发布日 2026-05-16(%s,句中未点明)、东京都 2026-08 期推定发布日 2026-08-30(%s,句中已点明);"
    "研究计划点值格推定发布日落周末者 %d 个(%s);研究计划 2025-06 以来落周末的日期记号 %d 个(%s)" % (
    len(CITED_WK), CALE.get("updated"), WKD.get("2026-05-23"), WKD.get("2026-05-16"), WKD.get("2026-08-30"), len(WK), ";".join(WK), len(RP_WK), ",".join(RP_WK)),
    CITED_WK == ["2026-05-16", "2026-05-23", "2026-08-30"] and WK == ["EA_HICP_YOY/6个月前@2026-05-16"] and "2026-05-16" in PLAN_PUB
    and all(D(d).weekday() >= 5 for d in CITED_WK + RP_WK) and "该推定日落在周日" in JALL and "2026-05-23" in RPTXT, (WK, RP_WK, CITED_WK))
sup("引擎聚簇面: POLCLUSTER-02 记为单地区事件", "POLCLUSTER-02" in RPTXT and '"same_event_cross_country": false' in RPTXT)
sup("东京都 CPI 两锚格在研究计划内 status=ok;月均锚格 vintage 与东京同为采集时点值",
    all(CELLS["JP_CPI_TOKYO_YOY"]["anchors"][a]["status"] == "ok" for a in CELLS["JP_CPI_TOKYO_YOY"]["anchors"])
    and CELLS["JP_POLICY_RATE"]["anchors"]["最新一期"]["vintage"] == Q_VINT_COL and CELLS["EA_HICP_YOY"]["anchors"]["最新一期"]["vintage"] == CELLS["JP_CPI_YOY"]["anchors"]["最新一期"]["vintage"] == Q_VINT_RET)
L_MISS = line_of(MAPL, "缺数格说明")
L_JPT = line_of(MAPL, "JP_POLICY_TARGET")
sup("MAP 覆盖句/缺数格说明/口径行/周三注记/对质表标题各在场", all(len(x) == 1 for x in (L_COV, L_WED, L_FOH, L_KOU, L_HEAD)) and len(L_MISS) >= 1 and len(L_JPT) >= 1,
    (L_COV, L_WED, L_FOH, L_KOU, L_HEAD, L_MISS, L_JPT))
REG_YIELDS = sorted(k for k in REGM if re.search(r"JGB|BUND", k))
sup("series_store 无 JGB/BUND 序列;注册表列有 %s;快照事实行有 JGB 三期限、无 BUND" % "/".join(REG_YIELDS),
    bool(REG_YIELDS) and not [k for k in SS if re.search(r"JGB|BUND", k)] and not [k for k in FACTS if "BUND" in k], (REG_YIELDS,))
NEXT_REL = {"EA_HICP_YOY": (dt.date(2026, 11, 30) + dt.timedelta(days=16)).isoformat(), "JP_CPI_YOY": (dt.date(2026, 11, 30) + dt.timedelta(days=20)).isoformat()}
sup("2026-11 期读数按引擎规则入档日 %s/%s 晚于截止日且未被判断档引用" % (NEXT_REL["EA_HICP_YOY"], NEXT_REL["JP_CPI_YOY"]),
    NEXT_REL["EA_HICP_YOY"] == "2026-12-16" and NEXT_REL["JP_CPI_YOY"] == "2026-12-20" and all(v not in JALL for v in NEXT_REL.values()), NEXT_REL)
WR_UTC = WR.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
ENG_TXT = "三项均属实(第 9 节 E8/E11)" if (ENG_ON and all(ENG_CHK.values())) else "本席未能全部核实(第 9 节 E8/E11)"

# --------------------------------------------------------------------------- counter-attacks (protocol section 4)
ATTACKS = [
    ("C1 分化", "换起点重算两地动量排序,检验「窗内动量相近」是否为挑选起点所致",
     "锚格期 2026-04→2026-10: 欧元区 " + sp1(D04[0]) + " 对日本 " + sp1(D04[1]) + " 个百分点;自 2026-05: " + sp1(D05[0]) + " 对 " + sp1(D05[1]) +
     ";自 2026-06: " + sp1(D06[0]) + " 对 " + sp1(D06[1]) + "(series_store.EA_HICP_YOY / JP_CPI_YOY 各月值)。排序随起点互换,判断档同句已列三组并自陈快慢互换。未找到反例"),
    ("C1 日本读数", "东京都读数是否被用来补全国口径之缺或与全国口径混用",
     "两口径分列: 2026-09 期对欧元区水平差 全国口径 " + sg2(SEPJ) + "(2.16−3.8)、东京口径 " + sg2(SEPT) + "(2.69−3.8)直算一致;东京序列 Gate A 列 noncore_missing、L1 无事实行已披露。未找到反例"),
    ("C1 同比基期", "同比基期是否用了相邻月,或缺基期仍给出同比",
     "欧元区基期 2025-10 期=" + n(mo(EA, 2025, 10)) + "、日本 2025-10 期=" + n(mo(JPC, 2025, 10)) + ",均为去年同月直算(同比对照 " + sp1(YEA) + "、" + sp1(-YJP) +
     " 个百分点);若以 2025-09 期为基则为 " + sg(ALT[0]) + "、" + sg(-ALT[1]) + ",与文中数字不符,可排除。东京都序列去年同月不在序列内,判断档未给东京都同比。未找到反例"),
    ("C1 竞争解释", "两条竞争解释是否同义反复或稻草人",
     "一为剪刀差收敛(高基数消退),一为持续分化(需求与政策组合驱动),对两地水平差的预言方向相反,C1 条目内「【假设】」标记出现 " + str(json.dumps(CON[0], ensure_ascii=False).count("【假设】")) +
     " 次,并写明不可在引擎面验证的依据(注册表 JP/EA 面通胀序列仅 " + "/".join(REG_INFL) + ")。真竞争"),
    ("C2 口径", "日本「收紧」是否以市场月均冒充宣布值",
     "分列月均≠宣布值并标【推断】;宣布值 1.25 单列(release_calendar RC-JP-BOJ-TARGET-2026-09: decision_date " + JPT["decision_date"] + "、effective_on " + JPT["effective_on"] +
     "、target_value " + n(JPT["target_value"]) + ")。未找到冒充"),
    ("C2 幅度", "「累计幅度相近」是否把不同口径直接相加",
     "已注口径不同仅作量级对照;欧央行 +50bp 为宣布值口径直算(MRO 2.15→2.65、DFR 2.0→2.5),日本 +50bp 为月均锚间直算(1.227−0.727=0.5 个百分点)。未找到反例"),
    ("C2 时序", "「相隔八天」是否有日级时间分辨率支撑",
     "生效日对生效日 2026-09-16→" + JPT["effective_on"] + "=" + str(DD["d8a"]) + " 天(序列变更日与日历 effective_on),回推决议日 2026-09-10→" + JPT["decision_date"] + "=" + str(DD["d8b"]) +
     " 天;判断档限同口径并声明月频分辨率下先后未定,与引擎聚簇面(POLCLUSTER-02 单地区事件,same_event_cross_country=false)一致。未找到反例"),
    ("C2 回推日", "引擎回推的欧央行决议日是否被当作事实",
     "全文两决议日共 " + str(N_OCC) + " 处出现,所在句均带 回推/惯例/推断 标注(生成器内复核),并声明不参与排序。未找到反例(注册表口径与引擎惯例不一未明示,记 MINOR-6)"),
    ("C2 事后信息", "截止日之后的信息是否被引用",
     "三条矛盾陈述与机制链四环的全部证据引用(" + "+".join(str(x) for x in N_REF) + "=" + str(len(REFS_ALL)) + " 条)观测日均不晚于 " + CUTOFF + ";正文(声明部分除外)晚于截止日的日期记号仅 " + "、".join(LATE) +
     "(问句请求的月末与情景时限);2026-11 期通胀读数按引擎规则须待 " + NEXT_REL["EA_HICP_YOY"] + "(欧元区)/" + NEXT_REL["JP_CPI_YOY"] + "(日本)入档,未被引用。未找到反例"),
    ("C3 真缺", "所列缺口是否真缺(有无序列在册而被称缺席)",
     "JP_POLICY_TARGET 不在注册表与 series_store;ECB 两序列末观测 " + LAST_MRO + ";日历无 ECB 条目;GDP 两序列在 gate_a.noncore_missing(快照事实行缺席;序列面 2026-07 期值 " + n(mo(GEA, 2026, 7)) + "/" + n(mo(GJP, 2026, 7)) +
     " 在场)。五项属实"),
    ("C3 缺席措辞", "有无把缺席写成「无变化」",
     "全文「无变化」出现 0 次;「维持不变」" + str(len(WMM)) + " 处,均在日央行 2026-10-30 确认维持(日历条目 RC-JP-BOJ-MAINT-2026-10)或 S2 情景假设的语境,不是对缺席数据的填值。未找到反例"),
    ("C3 天数", "「六十八天」「十天阈」是否算错",
     "2026-11-23−2026-09-16=" + str(DD["d68"]) + " 天;注册表 freshness.max_calendar_lag_days=10。属实"),
    ("C3 引擎缺口", "判断档是否把契约核验/别名表/历史视图三项引擎缺口写成数据缺口,或据此免于核验",
     "三项写在 quality_gate_notes 末条并标为引擎缺口披露(非本档判断问题),与 C3 五项证据缺口分列;本席只读检索引擎源码," + ENG_TXT + ";受其影响的数值本席已逐一直算(第 4 节)。未找到反例"),
    ("M1 环1", "12 个月度路径值与水平差区间是否算错",
     "12 值逐一直算一致;窗内(2026-05..2026-10)逐月水平差最小 " + n(GAPM[GAPM_MIN]) + "(" + GAPM_MIN + " 期)、最大 " + n(GAPM[GAPM_MAX]) + "(" + GAPM_MAX + " 期)。未找到反例"),
    ("M1 环2", "「合计 +50bp」是否算错",
     "四台阶 " + "+".join(n(x) for x in STEP_BP) + "=" + n(SUM_BP) + "bp,锚间净 " + n(ANCH_BP) + "bp;整数 bp 取整后均为 50。成立(取整差异不入问题清单)"),
    ("M1 环3", "主解释「方向分立」被观测否定后是否被写成支持",
     "观测为两货币同对美元走弱(EURUSD " + sg2(chg(EUR, W0, W1)) + "%、USDJPY " + sg2(chg(JPY, W0, W1)) + "%);判断档写明该预期未纳入美元端利率、两解释在该观测上预期未分立、尚不能区分。未把反证写成支持;main_predicts 措辞未加限定,记 MINOR-5"),
    ("M1 环3", "EURUSD×USDJPY 合成值是否算错",
     "1.1221×156.494、1.0970×159.707、1.0940×159.347 直算 " + n(EJ_(W0)) + "/" + n(EJ_(W1)) + "/" + n(EJ_(CUTOFF)) + ",与判断档一致(" +
     sg2(chg({"a": EJ_(W0), "b": EJ_(W1)}, "a", "b")) + "%/" + sg2(chg({"a": EJ_(W0), "b": EJ_(CUTOFF)}, "a", "b")) + "%)。未找到反例"),
    ("M1 环4", "「VIX +84.5%」「-24.7%」的舍入",
     "35.89/19.45−1=" + sg2(chg(VIX, W0, W1)) + "%;27.01/35.89−1=" + sg2(chg(VIX, W1, CUTOFF)) + "%;判断档一位小数舍入正确(二路脚本首跑的 3 点偏离即由本席比对参数误报,已核)。未找到反例"),
    ("M1 环4", "「为窗内两个最大单日跳升日」在月窗口径下是否成立",
     "月窗(2026-10-23→2026-11-20)内最大单日跳升为 " + TOP_MONTH[0] + "(+" + n(VDPCT[TOP_MONTH[0]]) + "%);该短语仅在跳升窗(2026-11-13→2026-11-20)口径成立。记 NIT-1"),
    ("M1 环4", "「快速回落」是否被当作裁定依据",
     "仅一个盘中观测(2026-11-23 盘中 27.01,较 2026-11-20 收盘 35.89 低 " + n(-chg(VIX, W1, CUTOFF)) + "%);判断档写不足以裁定。未找到反例"),
    ("l4 情景", "触发条件是否已被触发、前提是否已被证伪",
     "S1/S2 触发均需 2026-11 或 2026-12 观测月读数(尚未发布);截止日读数(欧元区 " + p1(VE[10]) + "/日本 " + p1(VJ[10]) + "/水平差 " + f2(GAP10) + ")与 S1 前提相容,与 S2 前提方向相反,S2 自标并列反例情景。未找到反例"),
    ("l4 情景", "期限 2027-02-15 是否早于读数可入档日,证伪条件是否可观测",
     "2026-12 期按引擎规则入档日: 欧元区 " + ENTRY["EA_HICP_YOY"] + "(月末+16)、日本 " + ENTRY["JP_CPI_YOY"] + "(月末+20),均早于 " + S1R["trigger"]["deadline"] +
     ";证伪指标 EA_HICP_YOY/JP_CPI_YOY 与触发分量 VIX 均在册。可观测"),
    ("l4 情景", "两情景阈值之间是否存在既不触发也不证伪的区间而未披露",
     "存在且部分未披露: VIX 收盘在 25–30 之间时两情景均不触发;S1 触发阈 4.0% 高于前提水平 3.5%,3.5%–4.0% 区间同属前提成立而不触发;判断档只披露了 S2 的 3.0%–3.5% 区间。不改变结论,记 NIT-7"),
    ("l4 历史类比", "「历史类比 0 段」是否与引擎 analog 面矛盾,有无同步性主张与引擎同步面冲突",
     "S6_analog 已执行(扫描 " + str(S6["candidates"]["scanned"]) + "、有效 " + str(S6["candidates"]["valid"]) + "、TOP1 " + S6["top"][0]["candidate_month"] + " 距离 " + str(S6["top"][0]["distance"]) + "),与判断档所引一致;"
     "判断档无跨地区同步/相关性系数主张;引擎地区×维度同步面 S5_compare 两侧=EA_HICP_YOY×ECB_MRO(月格对齐,变化对 " + str(S5["alignment"]["n_change_pairs"]) + " 对),与判断档「同月/先后未定」类表述无冲突。未找到反例"),
    ("契约", "契约验证的非 VERIFIED 项是否已实质披露",
     "契约 " + str(len(CV["verdicts"])) + " 个数值串中 " + str(len(CVNV)) + " 个 STALE(C2 的 " + CVNV[0]["token"] + ",值=期望值;引擎注记: " + Q_ENG_STALE + ");C3 第二项、headline、quality_gate_notes 披露序列止于 " + LAST_MRO +
     "、" + str(DD["d68"]) + " 天、Gate A 降级。实质披露在场(未点名状态词,记 NIT-2)"),
    ("时点", "截止日当日值是否被写成收盘",
     "明写均为 2026-11-23 盘中快照、非收盘价;快照 research_as_of=" + RA + "。相容"),
    ("版本一致", "report.json 内嵌 agent_judgment 的正文五键为 null,受审稿是否可能不是挂接时的版本",
     "运行目录内无 " + str(EJ.get("judgment_file")) + ",字节同一性在边界内不可核(列第 10 节)。间接证据一致: 挂接元数据(attached_at=" + str(EJ.get("attached_at")) + ")、validation 计数(" +
     "/".join(str(x) for x in (EJ["validation"]["n_contradictions"], EJ["validation"]["n_mechanism_chains"], EJ["validation"]["n_scenarios"])) + ")与受审稿结构一致,契约 " + str(len(CV["verdicts"])) +
     " 个数值串与 map_checks 的传导链 id、日期次序主张、转折指标来源均在受审稿内命中,书写时刻(" + WR_UTC + ")早于挂接时刻。未发现版本不一致的证据"),
    ("读者报告", "读者报告渲染是否忠实于判断档",
     "判断档字符串叶(len≥12)逐字渲染 MAP " + str(MAP_FOUND) + "/" + str(N_LV) + "、FULL " + str(FULL_FOUND) + "/" + str(N_LV) +
     ";verdict_note、turnings narrative、quality_gate_notes、agent_declaration 两报告均未渲染。不改变数值对错,裁定理由对读者不可见(记 MINOR-5 与第 9 节 E3)"),
    ("发布日", "引擎推定发布日落周末时判断档是否照引",
     "研究计划点值格的推定发布日中落周末者 " + str(len(WK)) + " 个(" + "、".join(WK) + ");判断档正文引用且见于点值格的日期为 " + "、".join(CITED_PUB) + ";正文落周末的日期记号 " + str(len(CITED_WK)) + " 个(" + "、".join(CITED_WK) + "): "
     "窗起日 2026-05-23 为六个月窗起点,东京都 2026-08 期推定日 2026-08-30 句中已点明落在周日;唯欧元区 2026-04 期推定日 2026-05-16 落在周六而句中未点明(已标引擎推定规则、非日历实录,不改变任何取值)。记 MINOR-8"),
]
N_ATT = len(ATTACKS)
assert N_ATT == 29

# --------------------------------------------------------------------------- engine-face observations (not counted)
ENG_OBS = [
    "E1 事实性文字: MAP_REPORT.md 第 %d 行引擎注记称「%s」为全称主张——序列面 %s 年共有 %d 个非周三观测日(2015 年以来 %d 个);本窗三个观测日(2025-06-11、2026-06-17、2026-09-16)均为周三。"
    "判断档未沿用该全称主张(全文「全为周三」出现 0 次)。" % (L_WED[0], Q_MAP_WED, "/".join(NONWED_YEARS), len(NONWED), len(NONWED_2015)),
    "E2 标题: MAP_REPORT.md 第 %d 行「%s」用于两地区(日本×欧元区)工单,「四地三时点」为模板残留。" % (L_HEAD[0], Q_MAP_HEAD),
    "E3 渲染: MAP_REPORT.md / FULL_REPORT.md 不渲染 verdict_note、turnings[].narrative、quality_gate_notes 与 agent_declaration(判断档字符串叶逐字渲染 %d/%d、%d/%d);对质表的裁定理由因此对读者不可见。" % (
        MAP_FOUND, N_LV, FULL_FOUND, N_LV),
    "E4 标注: FULL_REPORT.md 第 %d 行「%s」——S5_compare 信封为月格对齐(alignment.mode=%s,n_change_pairs=%d,change_basis=%s/%s),「日收益×日变化」标注与面对象不符。" % (
        L_PEAR[0], Q_FULL_PEAR, S5["alignment"]["mode"], S5["alignment"]["n_change_pairs"], S5["change_basis"]["a"], S5["change_basis"]["b"]),
    "E5 规则标签: MAP_REPORT.md 第 %s 行「%s」自身不一致(中旬 对 当月末);注册表为「%s」;%s。" % (
        "/".join(str(x) for x in L_TK), Q_MAP_TOKYO, Q_REG_TKREL,
        ("研究计划内另有落周末的日期记号 %s" % "、".join(RP_WK)) if RP_WK else "研究计划内无落周末的日期记号"),
    "E6 口径不一: ECB_MRO/ECB_DFR 在引擎各面状态不同——研究计划点值格「最新一期」status=ok(freshness_basis=policy_confirmation)/快照 Gate A 与 L1 事实行=DEGRADED(%s)/"
    "run.data_requirements=insufficient_coverage(按日频族下界: 窗内有效观测 2<66、相邻断档 91 天>30 天,套用于决策驱动型序列)/契约验证=STALE;MAP_REPORT.md 第 %d 行「%s」,第 %d 行起的缺数格说明仅列 JP_POLICY_TARGET%s。" % (
        Q_SNAP_ISSUE, L_COV[0], Q_MAP_COV, L_MISS[0],
        (";东京都 CPI 两格在表内显示 ok(第 %s 行;Gate A 列 noncore_missing)" % "/".join(str(x) for x in L_TKROW)) if len(L_TKROW) >= 2 else ""),
    "E7 口径不一: 注册表 ECB_MRO release_semantics(「%s」)与 calc(「%s」)对规划器惯例(点值格 policy_dates.decision_note=「%s」;publication_rule=「%s」)。" % (
        Q_REG_ECBREL, Q_REG_ECBCALC, Q_ENG_DECNOTE, Q_ENG_PUBRULE),
    "E8 契约覆盖(判断档 quality_gate_notes 末条①②已披露;本席只读检索引擎源码: %s): judgment_contract._map_checks 锚标签硬编码「12个月前/3个月前/最新一期」;"
    "text_consistency.ALIASES 未覆盖 JP_CPI_YOY/EA_HICP_YOY/JP_CPI_TOKYO_YOY/JP_POLICY_TARGET/ECB_MRO——这些指标的数值不在契约逐位核验内(本席已对判断档所引全部此类数值直算,见第 4 节)。" % (
        "两项属实" if (ENG_ON and ENG_CHK["E8 契约锚标签硬编码"] and ENG_CHK["E8 别名表未覆盖五指标"]) else "未能核实"),
    "E9 单位措辞: MAP_REPORT.md 第 %d 行「%s」对同比率变动使用 bp。" % (L_BP[0], Q_MAP_BP),
    "E10 文本滞后: 注册表 JP_CPI_YOY.calc 载「%s」,序列面已有 2026-10 期(series_store.JP_CPI_YOY@2026-10-01=%s)。" % (Q_REG_JPCOV, n(VJ[10])),
    "E11 视图口径(判断档 quality_gate_notes 末条③已披露;本席只读检索: %s): 历史截止视图下点值格按发布规则判可见(research_map_planner._hist_region_reading 经 _aof_first_pub)而序列路径取快照在场(_hist_series),"
    "两入口分立;本席未逐路径复算。本工单 run.evidence_gate.historical_view=%s,不属历史视图,未影响本稿。" % (
        "入口函数属实" if (ENG_ON and ENG_CHK["E11 历史截止视图两入口"]) else "未能核实", R["run"]["evidence_gate"].get("historical_view")),
    "E12 版本可追溯性: report.json 内嵌 agent_judgment 的正文五键(agent_declaration/l3/l4/reader_map/quality_gate_notes)均为 null,只存挂接元数据与契约验证;挂接元数据指向 %s,该文件不在运行目录内。"
    "只读 report.json 的读者看不到判断档正文,也无法在运行目录内核对挂接版本与受审稿的字节同一性。" % EJ.get("judgment_file"),
    "E13 表格注记: MAP_REPORT.md 第 %s 行为欧央行两序列的「6个月前」行(决议日 %s),随行印出的是「%s」——该注记是点值格 policy_dates 的静态字段,两个锚共用同一句,"
    "对 2025-06-05 的决议并不适用。" % ("/".join(str(x) for x in L_6M), CELLS["ECB_MRO"]["anchors"]["6个月前"]["policy_dates"]["decision"], Q_ENG_DECNOTE),
]
assert len(ENG_OBS) == 13

# --------------------------------------------------------------------------- six checks (protocol section 4)
SIX = [
    ("C1 分化陈述——最新读数水平分化、同比对照方向相反;窗内动量相近", [
        "- 证据相关性: 相干。evidence_refs %d 条(%s)均在证据索引。陈述内全部数值直算一致: 水平差 %s−%s=%s;同比对照欧元区 %s、日本 %s;锚间 %s 对 %s;自 2026-06 %s 对 %s;自 2026-05 %s 对 %s;"
        "两序列最新期推定发布日 %s 与 %s 相差 %d 天(引擎规则 月末+16 / 月末+20)。" % (
            N_REF[0], "、".join(CON[0]["evidence_refs"]), p1(VE[10]), p1(VJ[10]), f2(GAP10), sp1(YEA), sp1(-YJP), sp1(D04[0]), sp1(D04[1]), sp1(D06[0]), sp1(D06[1]), sp1(D05[0]), sp1(D05[1]),
            CELLS["EA_HICP_YOY"]["anchors"]["最新一期"]["publication_date"], CELLS["JP_CPI_YOY"]["anchors"]["最新一期"]["publication_date"], D4 if (D4 := days("2026-11-16", "2026-11-20")) else 0),
        "- 支持度: 水平与同比方向分化为事实位且有数;「窗内动量相近」是定性措辞、依赖起点,陈述同句列出三组起点并自陈快慢互换,措辞强度未超过证据。",
        "- 竞争解释: 两条方向真对立(高基数消退→剪刀差收敛 / 需求与政策组合驱动→持续分化),均带【假设】标记,并写明不可在引擎面验证的依据(注册表 JP/EA 面通胀序列仅 " + "/".join(REG_INFL) + ")。非稻草人。",
        "- 反对证据: 东京都序列 noncore_missing、L1 无事实行、去年同月读数不在序列内无法做同比方向对照,均已披露;两条最新读数的 L1 行 quality_status=%s/%s。未见未披露的反向事实。" % (
            FACTS["JP_CPI_YOY@2026-10-01"]["quality_status"], FACTS["EA_HICP_YOY@2026-10-01"]["quality_status"]),
        "- 结论是否超出证据: 未超出。",
        "- 证伪条件可观测性: 两解释对两地水平差的预言方向不同(收敛 / 维持或扩大),落在 EA_HICP_YOY、JP_CPI_YOY 两条在册序列上;l4 S1/S2 的证伪阈值(1.5/1.0 个百分点)与前提水平(3.5%/2.0%/3.0%)可观测。可观测。",
    ]),
    ("C2 政策面陈述——同向收紧、累计幅度相近,水平分化,口径基础不对称", [
        "- 证据相关性: evidence_refs %d 条全部解析。数值直算一致: ECB_MRO %s→%s→%s;ECB_DFR %s→%s→%s;JP_POLICY_RATE 2026-04=%s、2026-10=%s、2025-11=%s;USDJPY@2026-11-23=%s;SPX@2026-11-23=%s;VIX@2026-11-23=%s;"
        "日历 RC-JP-BOJ-TARGET-2026-09(decision_date=%s,effective_on=%s,target_value=%s,basis=%s)、RC-JP-BOJ-MAINT-2026-10(decision_date=%s,kind=%s)。" % (
            N_REF[1], f2(MRO["2025-06-11"]), f2(MRO["2026-06-17"]), f2(MRO["2026-09-16"]), f2(DFR["2025-06-11"]), f2(DFR["2026-06-17"]), f2(DFR["2026-09-16"]), f3(mo(JPR, 2026, 4)), f3(mo(JPR, 2026, 10)), f3(mo(JPR, 2025, 11)),
            "%.3f" % JPY[CUTOFF], "%.2f" % SPX[CUTOFF], "%.2f" % VIX[CUTOFF], JPT["decision_date"], JPT["effective_on"], f2(JPT["target_value"]), JPT["basis"], JPM["decision_date"], JPM["kind"]),
        "- 支持度: 欧央行端为 E1(两个 25bp 变更日直算,间隔 %d 天,此前持平 %d 天)。日本端收紧依据月均市场利率台阶与日历目标值,宣布值无前值可比——已标【推断】;累计幅度相近注明口径不同仅作量级对照。相称。" % (DD["d91"], DD["d371"]),
        "- 竞争解释: 读数驱动 vs 正常化程序/汇率与金融稳定考量,真对立,均带【假设】标记;后者的不可验证依据(政策文档事实仅 FOMC 纪要一条)与 research_plan.policy_doc_facts(%d 条: %s,published_on=%s)相符。" % (
            len(RP["policy_doc_facts"]), RP["policy_doc_facts"][0]["doc_id"], RP["policy_doc_facts"][0]["published_on"]),
        "- 反对证据: 日本宣布值前值缺席(日历仅有目标值与维持两条)、ECB 序列止于 %s、月均≠宣布值——均已写明。" % LAST_MRO,
        "- 结论是否超出证据: 水平差(MRO %s−%s=%s;DFR %s−%s=%s)有数;相隔八天限生效日对生效日(%d 天)并注回推决议日口径(%d 天);月频分辨率下先后未定,与引擎聚簇面(POLCLUSTER-02 单地区事件)不冲突。未超出。" % (
            f2(MRO[LAST_MRO]), f2(TARGET), f2(MRO[LAST_MRO] - TARGET), f2(DFR[LAST_DFR]), f2(TARGET), f2(DFR[LAST_DFR] - TARGET), DD["d8a"], DD["d8b"]),
        "- 证伪条件可观测性: 两解释的区分量是后续决议节奏与读数的联动;引擎面无 ECB 实录、日本仅两条实录——判断档未对两解释作裁决,如实并列,并注明欧央行分量须待发布日历补录后方可核验。不构成以不可观测条件支撑的结论。",
    ]),
    ("C3 证据缺口陈述——证据不足五项", [
        "- 相关性与属实: ①注册表无 JP_POLICY_TARGET(research_plan.dimension_gaps 同)属实;②ECB_MRO/ECB_DFR 末观测 %s,距 %s 为 %d 天,大于注册表 freshness.max_calendar_lag_days=10,快照 facts quality_status=DEGRADED(issues.message=「%s」),"
        "gate_a.noncore_degraded 含两序列,日历无 ECB 条目——属实;③日历日欧面仅 JP_POLICY_TARGET×2、EA_HICP_YOY×3(obs_from %s),不覆盖本窗——属实;④与锚格 vintage 相容(EA_HICP_YOY、JP_CPI_YOY=「%s」;JP_CPI_TOKYO_YOY、JP_POLICY_RATE=「%s」);"
        "⑤EA_REAL_GDP_YOY、JP_REAL_GDP_YOY 在 gate_a.noncore_missing(detail 含「%s」),序列面末观测 2026-07 期=%s/%s,注册表无两地核心通胀序列——属实。" % (
            LAST_MRO, CUTOFF, DD["d68"], Q_SNAP_ISSUE, "/".join(EA_CAL), Q_VINT_RET, Q_VINT_COL, Q_DET_GDP, f2(mo(GEA, 2026, 7)), f2(mo(GJP, 2026, 7))),
        "- 支持度与结论: 缺口没有被写成「无变化」(全文 0 次);没有把序列值写成官方宣布目标(ECB_MRO 引擎面标签=「%s」,与判断档「政策目标口径」一致)。未超出。" % Q_ENG_FACE,
        "- 竞争解释: 针对第②项的两种解释(此后无新决议 / 有新决议未反映)真对立,带【假设】标记,未裁定;区分量在引擎外(官网决议记录),判断档未把引擎外信息写入。",
        "- 反对证据与遗漏: 未列日欧主权债收益率端的不对称缺席——记 MINOR-3;第②项降级归因未提引擎另一面(decision_dated 规则、点值格 ok)——记 MINOR-7。",
        "- 证伪条件: 缺口陈述不设证伪条件;不适用。",
    ]),
    ("机制链环1(通胀路径,E1)", [
        "- 证据相关性: 12 个月度值逐一直算一致;窗内各月欧元区水平高于日本,差幅最小 %s(%s 期)、最大 %s(%s 期)。E1 与序列面直读相称。" % (f2(GAPM[GAPM_MIN]), GAPM_MIN, f2(GAPM[GAPM_MAX]), GAPM_MAX),
        "- 支持度: 两地上行(欧元区 2026-06 一度回落至 %s,非逐月单调;日本 2026-05 至 2026-10 逐月上行)逐月直算属实。" % p1(VE[6]),
        "- 反对证据: 2026-06 回落已写;2026-05 期观测日在窗前已括注。",
        "- 竞争解释与证伪条件: 观察环,无因果主张;不适用。",
    ]),
    ("机制链环2(政策面,E1)", [
        "- 证据相关性: ECB 四个端点、BOJ 日历两条、JP_POLICY_RATE 四个台阶(%s)直算一致;合计 +50bp 即四台阶之和 %sbp(整数 bp 取整后 50;锚间净 %sbp)。" % (
            "、".join("%s +%sbp" % (ym, n(bp)) for (ym, _, _), bp in zip(STEPS_JP, STEP_BP)), n(SUM_BP), n(ANCH_BP)),
        "- 支持度: 相容性措辞克制(相容、不作相容性判断);E1 相称。",
        "- 竞争解释与证伪条件: 观察环;不适用。标题「政策面跟进」略带因果色彩(记 NIT-8)。",
    ]),
    ("机制链环3(汇率,E2)", [
        "- 证据相关性: 标【假设】,缺环注记字段(%s)在场;EURUSD %s→%s(%s%%)、USDJPY %s→%s(%s%%)、DXY %s→%s(%s%%);至 %s: %s(%s%%)、%s(%s%%)、%s(%s%%);EURJPY 合成 %s/%s/%s(%s%%/%s%%)——全部直算一致(汇率各日值取自快照 series_store 的 EURUSD/USDJPY/DXY;EURJPY=同日两腿相乘)。" % (
            "/".join(MLN), fxv(EUR, 4, W0), fxv(EUR, 4, W1), sg2(chg(EUR, W0, W1)), fxv(JPY, 3, W0), fxv(JPY, 3, W1), sg2(chg(JPY, W0, W1)), fxv(DXY, 3, W0), fxv(DXY, 3, W1), sg2(chg(DXY, W0, W1)), CUTOFF,
            fxv(EUR, 4, CUTOFF), sg2(chg(EUR, W0, CUTOFF)), fxv(JPY, 3, CUTOFF), sg2(chg(JPY, W0, CUTOFF)), fxv(DXY, 3, CUTOFF), sg2(chg(DXY, W0, CUTOFF)),
            n(EJ_(W0)), n(EJ_(W1)), n(EJ_(CUTOFF)), sg2(chg({"a": EJ_(W0), "b": EJ_(W1)}, "a", "b")), sg2(chg({"a": EJ_(W0), "b": EJ_(CUTOFF)}, "a", "b"))),
        "- 支持度与结论: 主解释的原始预期「方向分立」与观测不符;判断档没有把观测写成支持主解释,而是重述为纳入美元端利率后的预期并得出尚不能区分(置信有限)。未超出证据;属保守取向。",
        "- 竞争解释: 利差主导 vs 美元全局/风险情绪主导,真对立;但经重述后两者在本月窗对 EURUSD 的预期同向,本窗不具区分力——判断档如实写明。",
        "- 反对证据: 主解释预期未获支持这一点写在正文;EURJPY 交叉盘不在证据面已写,合成值标为推算。",
        "- 证伪条件可观测性: 区分指标 EURUSD 在册且在场;两解释在其上的预言方向在本窗相同(判断档自陈),本窗不可区分;判断档未明写后续可区分的条件(如美元端利率不变而两地政策差再变动)——并入 MINOR-5。",
    ]),
    ("机制链环4(资产面,E2)", [
        "- 证据相关性: 标【假设·归因】,缺环注记字段(%s)在场;SPX %s%%、NIKKEI225 %s%%、DAX %s%%、CAC40 %s%%、VIX %s→%s(+%s%%)、末六日路径、引擎回贴面(%s/%s/%s/%s)、%s(%s%%)、"
        "先例(%s→%s,+%s%%;%s,%s%%;%d 个交易日;SPX 2026-11-05 %s%%;NIKKEI225 2026-11-06 %s%%)、跳升窗四地跌幅(%s/%s/%s/%s)、两日汇率单日变动不超过 %s%%、FOMC 纪要 %s——全部直算一致。" % (
            "/".join(MLN), sg2(chg(SPX, W0, W1)), sg2(chg(NK, W0, W1)), sg2(chg(DAX, W0, W1)), sg2(chg(CAC, W0, W1)), n(VIX[W0]), n(VIX[W1]), n(chg(VIX, W0, W1)),
            sg2(chg(SPX, W0, CUTOFF)), sg2(chg(DAX, W0, CUTOFF)), sg([a for a in J["reader_map"]["asset_returns_echo"] if a["metric_id"] == "NIKKEI225"][0]["chg_pct"]), sg2(chg(VIX, W0, CUTOFF)), n(VIX[CUTOFF]), sg2(chg(VIX, W1, CUTOFF)),
            n(VIX["2026-11-04"]), n(VIX["2026-11-05"]), n(chg(VIX, "2026-11-04", "2026-11-05")), n(VIX["2026-11-11"]), sg2(chg(VIX, "2026-11-05", "2026-11-11")), N_TD,
            sg2(chg(SPX, prevd(SPX, "2026-11-05"), "2026-11-05")), sg2(chg(NK, prevd(NK, "2026-11-06"), "2026-11-06")),
            sg2(chg(SPX, "2026-11-13", W1)), sg2(chg(NK, "2026-11-13", W1)), sg2(chg(DAX, "2026-11-13", W1)), sg2(chg(CAC, "2026-11-13", W1)), "%.2f" % max(FXD), RP["policy_doc_facts"][0]["published_on"]),
        "- 支持度与结论: 不利于主解释的两点(欧元区股指不弱于美股;VIX 跳升时点不对齐政策日历)写在正文;自陈证据倾向竞争解释但不足以裁定。未超出。",
        "- 竞争解释: 紧缩+通胀粘性 vs 全局风险/流动性冲击,真对立且同证据可容纳;第三类候选(FOMC 纪要)已列、未裁。",
        "- 证伪条件可观测性: 区分指标 VIX 在册且在场;两解释对 VIX 路径的预言不同(与政策日历联动/回落缓慢 vs 独立于日历/快速回落),待收盘数据可观测。可观测。",
        "- 行文: 「为窗内两个最大单日跳升日」仅在跳升窗口径成立(记 NIT-1)。",
    ]),
    ("对质表三行(传导链 reader_map 面)", [
        "- 环1: 持平 %d 天(2025-06-11→2026-06-17)、间隔 %d 天、各 25bp、决议日前可见读数(决议日口径 %s/%s,生效日口径 %s/%s)直算一致;「尚不能区分」与 n=2 的证据强度相称。" % (
            DD["d371"], DD["d91"], p1(VE[4]), p1(VE[7]), p1(VE[5]), p1(VE[8])),
        "- 环2: 「尚不能区分」与同页观测不矛盾(经重述后两解释预期同向);main_predicts 措辞未加限定(记 MINOR-5)。",
        "- 环3: 「尚不能区分」与正文「证据倾向竞争解释」并读时表面不一致;理由(「快速回落」仅一个盘中观测)在 verdict_note,读者面不可见(记 MINOR-5)。",
    ]),
    ("历史类比与历史段同步性", [
        "- 判断档历史类比 0 段并如实说明未逐项核验候选月的事后结果;引擎 S6_analog 已执行(steps[S6_analog].envelope.data: candidates.scanned=%d、candidates.valid=%d、top[0].candidate_month=%s、distance=%s),与判断档所引数字逐项一致(见第 4 节)。" % (
            S6["candidates"]["scanned"], S6["candidates"]["valid"], S6["top"][0]["candidate_month"], S6["top"][0]["distance"]),
        "- 全文无跨地区同步/相关性系数主张(「相关系数/同步系数/pearson/皮尔逊」出现 0 次);引擎地区×维度同步面 S5_compare 两侧=EA_HICP_YOY×ECB_MRO,与判断档「同月/先后未定」类表述无冲突。无「叙述称同步而面=缺证」或「叙述与面冲突」情形。",
    ]),
]

# --------------------------------------------------------------------------- notes (goes verbatim into the verdict record)
CAT_TXT = "、".join("%s %d 点" % (CAT_NAMES[k], CAT[k]) for k in ("snap", "eng", "cal", "reg", "eidx", "txt", "date", "oth") if CAT.get(k))
assert sum(CAT.values()) == N_PTS, (sum(CAT.values()), N_PTS)
MINOR_SUM = ["ECB 序列最新水平一句未带降级限定", "日欧 CPI 同比为引擎自算口径未注明", "日欧主权债收益率缺席未列入证据缺口", "东京都转折行未随行标注 noncore_missing",
             "对质裁定理由未渲染且主解释预期措辞未加限定", "ECB 决议日回推与注册表口径不一未明示", "ECB 降级归因未提引擎另一面", "欧元区 2026-04 期推定发布日落周六未点明"]
NIT_SUM = ["「为窗内两个最大单日跳升日」的窗口径", "契约 STALE 状态词未点名", "「冻结日历实录仅覆盖」缺日欧面限定", "「决议即…生效」", "「窗内月度路径」含观测日在窗前的一期",
           "「UST_10Y 最新 5.04%」未写观测日", "情景触发/证伪空档披露不全", "环2 标题「政策面跟进」", "「中旬速报先行口径」", "「此后总体回升」未注一次小幅回落"]
assert len(MINOR_SUM) == N_MIN and len(NIT_SUM) == N_NIT
NOTES = (
    "【N30 Round-1 零上下文独立席·裁决依据】受审稿=agent_judgment.json 全文(l3 三条矛盾陈述+机制链四环、l4 两情景、reader_map、quality_gate_notes、agent_declaration)与读者报告中的判断文字,代码印章 " + GIT_HEAD + "。"
    "主复算表 " + str(N_PTS) + " 点(规程最低 " + str(S.get("minimum_required")) + "),逐点比对报告值与直算值: 命中 " + str(N_PTS - N_MIS) + "、偏离 " + str(N_MIS) + "、脚本错误 " + str(S.get("script_errors")) +
    "(定稿前共 " + str(N_RUN) + " 次运行、" + str(N_PATCH) + " 次修补;早期偏离与报错均为本席脚本侧,逐次修至零);出处构成=" + CAT_TXT + ";"
    "其中 " + str(N_BOOL) + " 点为真/假命题(由脚本内显式谓词判定),其余为值比对;另以不共享代码的二路脚本复核 " + str(I["n"]) + " 点、偏离 " + str(I["mismatch"]) + "(不重复计入)。"
    "抽核要点: ①截止日 2026-11-23 与快照 research_as_of 一致,被引观测/发布/决议/生效日无一晚于截止日;②点值锚格 " + str(SEC["B②点值锚格"]["ok"]) + " 点全中;"
    "③同比基期均为去年同月,东京都去年同月缺值如实标无法做同比方向对照,无缺基期同比、无相邻口径顶替;④政策面宣布值/市场月均/目标值三口径分记,"
    "ECB 两次 25bp(间隔 91 天、此前持平 371 天)、BOJ 决议 2026-09-18/生效 2026-09-24/目标 1.25 与冻结日历逐项一致,8 天间隔限生效日口径;"
    "⑤美国三利率分解 −8=+11−19(bp)与资产月窗全中;⑥三转折与引擎候选面一致,先后主张限月频分辨率;⑦传导链四环数字全中(E2 两环均标【假设】并带缺环注记);"
    "⑧历史类比 0 段如实,无同步性系数主张;⑨两情景触发/证伪阈值均可观测且未被截止日读数触发或证伪,读数入档日(" + ENTRY["EA_HICP_YOY"] + "/" + ENTRY["JP_CPI_YOY"] + ")早于时限 2027-02-15;"
    "⑩headline/地区行/对质表文字与数值一致;⑪五项证据缺口逐项属实,无把缺席写成无变化;⑫截止日当日值均标盘中快照;⑬契约唯一非 VERIFIED 项(C2 的 2.5% 数值串 STALE,值=期望值)实质披露在场,未点名状态词记 NIT;"
    "⑭交付门缺口披露(ECB 两序列按日频族下界判 insufficient_coverage)与序列面一致,交付门本身不在裁决范围。"
    "六查: 三条矛盾陈述与机制链四环各做一次,竞争解释均为真对立且带【假设】标记,无未披露的反向事实,无结论超出证据;证伪条件落在在册序列(EA_HICP_YOY/JP_CPI_YOY/VIX)上可观测。"
    "反方攻击 " + str(N_ATT) + " 次,未找到可成立的反例。MAJOR " + str(N_MAJ) + " 条;MINOR " + str(N_MIN) + " 条"
    "(" + "；".join(MINOR_SUM) + "),均不改结论;"
    "NIT " + str(N_NIT) + " 条(" + "；".join(NIT_SUM) + ")。另列引擎面观察 " + str(len(ENG_OBS)) + " 条于 PROSE 第 9 节,不属判断档问题、不计入。裁决 " + DECISION + "。"
)
# ======================================================================
# part E -- render the two deliverables, provenance check, single write, post-write validation
# ======================================================================
def cell(v):
    if isinstance(v, bool):
        return "真" if v else "假"
    if v is None:
        return "null"
    s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
    s = s.replace("|", "\\|").replace("\r", " ").replace("\n", " ")
    return s if len(s) <= 320 else s[:320] + "…(截断)"


TP_TXT = "、".join("%s %d" % (k, TP[k]) for k in TYPE_ORDER if TP.get(k))
OTH_TXT = "、".join("%s×%d" % kv for kv in OTH.most_common())
SEC_SUM = (sum(v["points"] for v in SEC.values()), sum(v["ok"] for v in SEC.values()), sum(v["mismatch"] for v in SEC.values()))
assert SEC_SUM == (N_PTS, N_PTS - N_MIS, N_MIS), SEC_SUM
RUN_DIR_NAME = os.path.basename(os.path.dirname(JPATH))
P = []
P.append("# N30 Round-1 语义审查席复算清单(零上下文独立席)")
P.append("")
P.append("| 项 | 值 |")
P.append("|---|---|")
for k, v in (("席位", "semantic-audit-seat"), ("审查者", REVIEWER), ("审查日期", AUDITED_AT),
             ("受审稿", "运行目录 " + RUN_DIR_NAME + " 下 agent_judgment.json(schema " + str(J.get("schema_version")) + ")全文与两份读者报告中的判断文字"),
             ("代码印章", GIT_HEAD + "(report.json run.git_head 与 MAP_REPORT.md 印章同值)"), ("裁决", DECISION),
             ("复算点数 / 偏离 / 脚本错误", "%d / %d / %d" % (N_PTS, N_MIS, S.get("script_errors", 0))), ("二路独立复核(不重复计入)", "%d / %d" % (I["n"], I["mismatch"])),
             ("MAJOR / MINOR / NIT", "%d / %d / %d" % (N_MAJ, N_MIN, N_NIT)), ("配套文件", "VERDICT-round1.json(裁决档);本清单由席位自写脚本 s12_write_outputs.py 一次性生成")):
    P.append("| %s | %s |" % (k, cell(v)))
P.append("")
P.append("阅读提示: 本清单每个引用数字都写明出处(文件+键);「一致」指报告值与直算值在书写精度内相等(数值按报告值的小数位取 ±0.5×10 的负小数位次,文本逐字)。"
         "第 4 节为逐点复算清单,第 5 节为二路复核与不计数的补充核对,第 6 节六查,第 7 节反方攻击,第 8 节问题清单,第 9 节引擎面观察(不属判断档问题),第 10 节未核验事项,第 11 节文件清单。")
P.append("")
P.append("## 0 复算方法与定稿过程")
P.append("")
P.append("1. 只读面: 受审运行目录(agent_judgment.json、report.json、MAP_REPORT.md、FULL_REPORT.md、evidence_index.json、root_overlay/config 下的注册表与冻结发布日历)、冻结快照 research_snapshot_20261123.json、"
         "只读安装树内四个引擎源码文件(仅作文本检索,未导入、未执行)。未联网;未运行任何写操作;未读取规程第 2 节禁止的目录;席位产出只写在本目录。")
P.append("2. 主复算表(s05_recompute.py)从上述只读输入直算,逐点与报告值比对。定稿前的运行记录(点数 / 偏离 / 脚本错误):")
P.append("")
P.append("| 运行 | 点数 | 偏离 | 脚本错误 |")
P.append("|---|---|---|---|")
for i, tot, mm, se, _a, _b in RUNS:
    P.append("| %d | %d | %d | %d |" % (i, tot, mm, se))
P.append("")
P.append("3. 定稿说明: 历次偏离与报错均为本席脚本侧(比对容差参数、列表次序、期望值书写、键名),未改动任何受审数据;第 %d 次修补删去 3 个非由数据导出的恒真点,点数由 598 降为 %d。"
         "定稿为第 %d 次运行: %d 点 / 偏离 %d / 脚本错误 %d。" % (N_PATCH, N_PTS, N_RUN, N_PTS, N_MIS, S.get("script_errors", 0)))
P.append("4. 二路脚本(s06_independent_check.py,不调用主表任何函数)复核被引数值 %d 点;首跑报 3 点偏离,经查均为本席比对容差设置过紧所致(判断档按一位小数书写的百分比与序列原值直算结果之间的书写精度差),"
         "按书写精度设定容差后 %d/%d。" % (I["n"], I["ok"], I["n"]))
P.append("5. 过程中断如实披露: 本席工作曾多次因席位接口层中断(单次大文件写入失败、接口速率限制、输出长度上限、上下文压缩),均与受审内容无关;生成器因此分段写成。每次续跑都重新读取只读输入并核对代码印章(run.git_head 与 MAP 印章同值)与快照 research_as_of,受审版本未变。")
P.append("6. 裁决只依据本席亲自复算到的内容;引擎交付门(阻断类别等)不在裁决范围,本席只核判断档对缺口的披露是否与序列面一致。")
P.append("")
P.append("## 1 裁决依据摘要(逐字进入裁决档 notes)")
P.append("")
P.append(NOTES)
P.append("")
P.append("## 2 复算表总览")
P.append("")
P.append("- 规程最少点数 " + str(S.get("minimum_required")) + ";实做 " + str(N_PTS) + " 点,偏离 " + str(N_MIS) + ",脚本错误 " + str(S.get("script_errors", 0)) + "。")
P.append("- 值类型构成: " + TP_TXT + ";其中真/假命题型 " + str(N_BOOL) + " 点(脚本内显式谓词判定)。")
P.append("- 出处构成: " + CAT_TXT + "。" + (("其他类细分: " + OTH_TXT + "。") if OTH_TXT else ""))
P.append("- 二路独立复核: " + str(I["ok"]) + "/" + str(I["n"]) + " 一致,偏离 " + str(I["mismatch"]) + "。")
P.append("")
P.append("## 3 分节命中表")
P.append("")
P.append("| 节 | 点数 | 命中 | 偏离 |")
P.append("|---|---|---|---|")
for k in SEC:
    P.append("| %s | %d | %d | %d |" % (k, SEC[k]["points"], SEC[k]["ok"], SEC[k]["mismatch"]))
P.append("| 合计 | %d | %d | %d |" % SEC_SUM)
P.append("")
I4S = len(P)
P.append("## 4 逐点复算清单(%d 点)" % N_PTS)
P.append("")
P.append("| 序 | 节 | 核对项 | 报告值 | 直算值 | 出处 | 结果 |")
P.append("|---|---|---|---|---|---|---|")
MAIN_ROWS = ["| %d | %s | %s | %s | %s | %s | %s |" % (i, p["section"], cell(p["where"]), cell(p["claim"]), cell(p["computed"]), cell(p["source"]), "一致" if p["ok"] else "偏离")
             for i, p in enumerate(PTS, 1)]
P.extend(MAIN_ROWS)
P.append("")
I4E = len(P)
P.append("## 5 二路独立复核(%d 点,不重复计入)与不计数的补充核对" % I["n"])
P.append("")
P.append("| 序 | 二路核对项 | 报告值 | 独立直算值 | 一致 |")
P.append("|---|---|---|---|---|")
for i, r in enumerate(I["rows"], 1):
    P.append("| %d | %s | %s | %s | %s |" % (i, cell(r["item"]), cell(r["judgment"]), cell(r["independent"]), "一致" if r["ok"] else "偏离"))
P.append("")
P.append("生成器内补充核对(%d 项;不计数,写出前要求全部成立)" % len(SUP))
P.append("")
P.append("| 序 | 核对项 | 结果 |")
P.append("|---|---|---|")
for i, lab, ok, det in SUP:
    P.append("| %d | %s | %s |" % (i, cell(lab), "成立" if ok else "不成立 " + cell(det)))
P.append("")
P.append("生成器内第三路数值复算(%d 项;不计数,写出前要求全部成立;期望值=本席叙述所引、与判断档书写同值的数值,直算值由只读输入在本脚本内重算)" % len(NUM))
P.append("")
P.append("| 序 | 数值项 | 直算值 | 期望值 | 结果 |")
P.append("|---|---|---|---|---|")
for i, (lab, got, exp, ok) in enumerate(NUM, 1):
    P.append("| %d | %s | %s | %s | %s |" % (i, cell(lab), cell(got), cell(exp), "一致" if ok else "偏离"))
P.append("")
P.append("补充事实(逐字取自输入): 快照 gate_a.noncore_missing_detail 对 JP_CPI_TOKYO_YOY =「" + Q_DET_TOKYO + "」;gate_a.note =「" + Q_GATE_NOTE + "」;"
         "东京都读数取自快照序列面而事实行缺席,判断档已披露(记 MINOR-4)。")
P.append("")
P.append("## 6 六查逐项结论(规程第 4 节)")
P.append("")
for i, (t, bs) in enumerate(SIX, 1):
    P.append("### 6.%d %s" % (i, t))
    P.append("")
    assert all(b.startswith("- ") for b in bs)
    for b in bs:
        P.append(b)
    P.append("")
P.append("## 7 反方攻击记录(%d 次)" % N_ATT)
P.append("")
P.append("| 序 | 对象 | 攻击 | 结果 |")
P.append("|---|---|---|---|")
for i, (obj, atk, res) in enumerate(ATTACKS, 1):
    P.append("| %d | %s | %s | %s |" % (i, obj, cell(atk), cell(res)))
P.append("")
P.append("## 8 问题清单(判断档)")
P.append("")
P.append("### MAJOR(%d 条)" % N_MAJ)
P.append("")
P.append("无。" if N_MAJ == 0 else "")
P.append("")
P.append("### MINOR(%d 条;口径或披露可改进,不改结论)" % N_MIN)
P.append("")
_c = {"MINOR": 0, "NIT": 0}
for x in ITEMS:
    _c[x["severity"]] += 1
    if x["severity"] == "NIT" and _c["NIT"] == 1:
        P.append("### NIT(%d 条;行文与限定语)" % N_NIT)
        P.append("")
    P.append("- **%s-%d** 位置: `%s`" % (x["severity"], _c[x["severity"]], x["where"]))
    P.append("  - 原句(逐字截取): 「%s」" % x["original"].replace("\n", " "))
    P.append("  - 问题: %s" % x["note"])
    if x["fix"]:
        P.append("  - 建议改句: 「%s」" % x["fix"])
    P.append("")
P.append("VERDICT-round1.json 的 items 按 MINOR-1..%d、NIT-1..%d 同序排列;must_fix 为空。" % (N_MIN, N_NIT))
P.append("")
P.append("## 9 引擎面观察(%d 条;不计入判断档问题,供操作席分流)" % len(ENG_OBS))
P.append("")
P.append("说明: 以下为引擎确定性面与读者报告渲染的观察,不属于受审判断档的问题,不计入 MAJOR/MINOR/NIT;本席对受审稿的裁决不受其影响。")
P.append("")
for e in ENG_OBS:
    P.append("- " + e)
P.append("")
P.append("## 10 未核验事项与边界")
P.append("")
for t in (
    "未联网: 官方公布值、央行官网决议记录、Eurostat/总务省实际发布日未核对;注册表、冻结日历、冻结快照按冻结事实采信。判断档所称「引擎推定规则、非日历实录」的各发布日,本席只核了与引擎规则的一致性。",
    "时区换算(quality_gate_notes 第 5 条: 纽约 09:53、柏林 15:53、东京 23:53、上海 22:53)按 UTC−5/+1/+9/+8 固定偏移由脚本推算。",
    "引擎源码只读检索了 judgment_contract._map_checks 锚标签、text_consistency.ALIASES、research_map_planner 的 _hist_series/_hist_region_reading/_aof_first_pub 与 evidence_gate 的 is_historical_view/visible_publish 入口,未做全路径复算;" + (
        "本次生成时四个源码文件均在场。" if ENG_ON else "本次生成时未传入引擎源码路径,相关表述以此前检索结果为据。"),
    "东京都 CPI 逐月路径未在判断档逐月列出(文内仅锚格与转折端点);复算表对此为记实点,不要求逐月列出。",
    "「合计 +50bp」的两种算法(锚间 %sbp / 四台阶之和 %sbp)取整后一致,未列入问题清单。" % (n(ANCH_BP), n(SUM_BP)),
    "复算点数含真/假命题型点(%d 点)与记实型点;点数只表示核对密度,不表示证据强度。" % N_BOOL,
    "引擎交付门(阻断类别、是否放行)不在裁决范围;本席只核判断档对缺口的披露是否与序列面、日历一致(第 4 节 N 节)。",
    "report.json 内嵌 agent_judgment 的正文五键为 null,挂接元数据所指的 judgment5_N30.json 不在运行目录内: 挂接版本与受审稿的字节同一性在边界内不可核,只核了间接证据(第 7 节「版本一致」一行)。",
    "历史截止视图下的可见性口径未复算(本工单 run.evidence_gate.historical_view=%s)。" % R["run"]["evidence_gate"].get("historical_view"),
    "EA_REAL_GDP_YOY、JP_REAL_GDP_YOY、JP_CPI_TOKYO_YOY 当日快照事实行缺席,相关复算取快照 series_store 序列值。",
    "本席自存中间转储中有两份(dump/registry_notes.txt、dump/step_01_S2_doctor.json)因含不宜留存的名称已就地遮蔽,不参与任何复算;复算脚本(s05_recompute.py、s05_summ.py、s06_independent_check.py)文本内不引用这两个文件名。",
):
    P.append("- " + t)
P.append("")
I11S = len(P)
P.append("## 11 席位文件清单(同目录,供操作席复核)")
P.append("")
SIZES = []
for f in sorted(os.listdir(SEAT_DIR)):
    fp = os.path.join(SEAT_DIR, f)
    if f in ("PROSE-round1.md", "VERDICT-round1.json") or re.match(r"^s12_check\d+\.txt$", f):
        continue
    if os.path.isdir(fp):
        SIZES.append(len(os.listdir(fp)))
        P.append("- %s/ (%d 个文件)" % (f, len(os.listdir(fp))))
    else:
        SIZES.append(os.path.getsize(fp))
        P.append("- %s (%d 字节)" % (f, os.path.getsize(fp)))
P.append("- (生成器自身的运行日志 s12_check*.txt 正在写入,不计入;字节数为写出时刻的值。)")
P.append("")

# ---- number provenance: every numeral in the narrative must occur in an input, in the judgment, in the tables, or in the computed set
NUMTOK = re.compile(r"(?<![A-Za-z_0-9.])\d+(?:\.\d+)?")
HEADNUM = re.compile(r"^(#+ )+(\d+(?:\.\d+)*\.?) ")
DIAG = {"MAP/FULL found": (MAP_FOUND, N_LV, FULL_FOUND), "WMM": WMM, "WK": WK, "RP_WK": RP_WK, "CITED_PUB": CITED_PUB, "CITED_WK": CITED_WK,
        "LINES": (L_HEAD, L_COV, L_WED, L_BP, L_FOH, L_KOU, L_PEAR, L_MISS, L_JPT, L_TK, L_TKROW, L_6M), "REG_YIELDS": REG_YIELDS, "N_REF": N_REF, "JGBV": JGBV,
        "TYPE": dict(TP), "CAT": (dict(CAT), dict(OTH)), "FILES": sorted(os.listdir(SEAT_DIR)), "SIZES": SIZES, "FTL_CH": FTL_CH, "MAY_PUB": (EA_MAY_PUB, JP_MAY_PUB), "POLICY_CHANGE": FTL[FTL_CH[-1][0]],
        "COUNTS": (len(SUP), len(NUM), len(ATTACKS), len(ENG_OBS), N_BOOL, I["n"], I["ok"])}
assert "registry_notes" not in "".join(rd(os.path.join(SEAT_DIR, f)) for f in ("s05_recompute.py", "s05_summ.py", "s06_independent_check.py"))
assert "step_01_S2_doctor" not in "".join(rd(os.path.join(SEAT_DIR, f)) for f in ("s05_recompute.py", "s05_summ.py", "s06_independent_check.py"))
WL_TXT = "\n".join([JALL, RTXT, SNAPTXT, REGTXT, json.dumps(CALE, ensure_ascii=False), MAP, FULL, json.dumps(T, ensure_ascii=False), json.dumps(I, ensure_ascii=False),
                    json.dumps(EIDX, ensure_ascii=False), "\n".join("%r %r" % (cell(g), cell(e)) for _, g, e, _ in NUM), " ".join(list(ENTRY.values()) + list(NEXT_REL.values()) + ["%d" % x for r in RUNS for x in r[:4]]),
                    " ".join(str(i) for i in range(1, max(len(I["rows"]), len(NUM), len(SUP)) + 1)), json.dumps(DIAG, ensure_ascii=False, default=str),
                     " ".join(f2(DFR[k]) + " " + f2(MRO[k]) for k in ("2025-06-11", "2026-06-17", "2026-09-16"))])
WL = set(NUMTOK.findall(WL_TXT))
NARR = P[:I4S] + P[I4E:I11S]
MISS = sorted(set(t for t in NUMTOK.findall("\n".join(HEADNUM.sub(r"\1", ln) for ln in NARR)) if t not in WL))

V = {"seat": "semantic-audit-seat", "reviewer": REVIEWER, "verdict": DECISION, "overall": DECISION, "notes": NOTES, "items": ITEMS, "must_fix": [],
     "counterexamples_sought": ["反方攻击 %d: %s——%s → %s" % (i, o, a, r) for i, (o, a, r) in enumerate(ATTACKS, 1)],
     "recompute_points": N_PTS, "recompute_mismatches": N_MIS, "mismatch_details": [], "audited_at": AUDITED_AT}
KEYS = ["seat", "reviewer", "verdict", "overall", "notes", "items", "must_fix", "counterexamples_sought", "recompute_points", "recompute_mismatches", "mismatch_details", "audited_at"]
assert list(V.keys()) == KEYS
PROSE_TXT = "\n".join(P) + "\n"
VERDICT_TXT = json.dumps(V, ensure_ascii=False, indent=1) + "\n"

log("points=%d mismatches=%d second_path=%d/%d major=%d minor=%d nit=%d attacks=%d engine_obs=%d sup=%d(fail %d) num=%d(fail %d) prose_chars=%d verdict_chars=%d" % (
    N_PTS, N_MIS, I["ok"], I["n"], N_MAJ, N_MIN, N_NIT, N_ATT, len(ENG_OBS), len(SUP), sum(1 for s in SUP if not s[2]), len(NUM), sum(1 for x in NUM if not x[3]),
    len(PROSE_TXT), len(VERDICT_TXT)))
for s in SUP:
    if not s[2]:
        log("SUP-FAIL #%d %s :: %s" % (s[0], s[1], s[3]))
for lab, got, exp, ok in NUM:
    if not ok:
        log("NUM-FAIL %s got=%r exp=%r" % (lab, got, exp))
log("ENG_CHK " + json.dumps(ENG_CHK, ensure_ascii=False))
log("PROVENANCE-MISS " + " ".join(MISS))
for k in sorted(DIAG):
    log("%s %s" % (k, json.dumps(DIAG[k], ensure_ascii=False, default=str)[:1500]))
# ---- guards: no vendor names / no credentials in the deliverables (patterns assembled from fragments), structure checks
_W = [x + y for x, y in (("Ant", "hropic"), ("cla", "ude"), ("open", "ai"), ("chat", "gpt"), ("deep", "seek"), ("q", "wen"), ("tong", "yi"), ("gem", "ini"), ("lla", "ma"),
                          ("mis", "tral"), ("mo", "onshot"), ("ki", "mi"), ("gro", "k"), ("bai", "chuan"), ("hun", "yuan"), ("dou", "bao"), ("min", "imax"), ("step", "fun"),
                          ("ern", "ie"), ("son", "net"), ("op", "us"), ("hai", "ku"), ("fab", "le"))] + ["\u6587\u5fc3", "\u901a\u4e49", "\u667a\u8c31", "\u8c46\u5305"]
SENS_RES = [re.compile("(?<![A-Za-z0-9_])(?:" + "|".join(_W) + ")(?![A-Za-z0-9_])", re.IGNORECASE), re.compile("g" + "lm", re.IGNORECASE), re.compile("zhi" + "pu", re.IGNORECASE)]
_SECRET_SRC = ["sk-[A-Za-z0-9]{16,}", "bearer\\s+[A-Za-z0-9._\\-]{16,}", "AKIA[0-9A-Z]{16}", "gh[pousr]_[A-Za-z0-9]{20,}", "xox[baprs]-[A-Za-z0-9\\-]{10,}",
               "(api[_ \\-]?key|access[_ \\-]?token|secret[_ \\-]?key|password|passwd)\\s*[:=]\\s*[\"']?[A-Za-z0-9_.\\-]{10,}"]
for _q in _SECRET_SRC:
    SENS_RES.append(re.compile(_q, re.IGNORECASE))


def sensitive_hits(txt):
    hits = []
    for k, rx in enumerate(SENS_RES):
        for m in rx.finditer(txt):
            hits.append((k, m.start(), len(m.group(0))))
    return hits


def prewrite_asserts():
    assert not [q for q in SUP if not q[2]], "supplementary check failed"
    assert not [x for x in NUM if not x[3]], "numeric recheck failed"
    assert not MISS, ("numeral without provenance", MISS)
    assert len(MAIN_ROWS) == N_PTS and all(l.rstrip().endswith("| 一致 |") for l in MAIN_ROWS), len(MAIN_ROWS)
    assert all(l.startswith("| %d | " % i) for i, l in enumerate(MAIN_ROWS, 1)), "main row index prefix"
    assert list(V.keys()) == KEYS and V["verdict"] in ("UPHELD", "REVISE") and V["overall"] == V["verdict"] and V["must_fix"] == []
    assert V["recompute_points"] == N_PTS and V["recompute_mismatches"] == N_MIS and V["mismatch_details"] == [] and V["audited_at"] == AUDITED_AT
    assert len(ITEMS) == N_MIN + N_NIT and all(any(x["original"] in c for c in CORPUS) for x in ITEMS)
    assert all(set(x.keys()) == {"severity", "where", "note", "original", "fix"} for x in ITEMS), "item keys"
    assert all(x["where"].startswith("agent_judgment.json: ") for x in ITEMS), "item where prefix"
    assert len(V["counterexamples_sought"]) == N_ATT, "attack count"
    assert V["notes"] == NOTES, "notes identity"
    assert NOTES in PROSE_TXT, "notes not verbatim in prose"
    for _t in ("\n## 1 裁决依据摘要", "\n## 4 逐点复算清单", "\n## 5 二路独立复核", "\n## 6 六查逐项结论", "\n## 7 反方攻击记录", "\n## 8 问题清单", "\n## 9 引擎面观察", "\n## 10 未核验事项", "\n## 11 席位文件清单"):
        assert PROSE_TXT.count(_t) == 1, _t
    _bad = [l for l in PROSE_TXT.split("\n") if "| 偏离 |" in l and not l.startswith(("| 运行 | 点数 |", "| 节 | 点数 |"))]
    assert not _bad and PROSE_TXT.count("| 一致 |") >= N_PTS + I["ok"] + len(NUM), ("table cells", len(_bad), PROSE_TXT.count("| 一致 |"))
    assert "\n- - " not in PROSE_TXT
    _hits = sensitive_hits(PROSE_TXT + "\n" + VERDICT_TXT)
    assert not _hits, ("sensitive name/credential pattern hit in deliverables (pattern index, offset, length)", _hits[:8])
    assert json.loads(VERDICT_TXT) == V


if CHECK_ONLY:
    try:
        prewrite_asserts()
        log("PREWRITE-ASSERTS: all passed")
    except AssertionError as e:
        log("PREWRITE-ASSERT-FAIL %r" % (e.args,))
    open(os.path.join(SEAT_DIR, "s12_preview_prose.txt"), "w", encoding="utf-8", newline="\n").write(PROSE_TXT)
    open(os.path.join(SEAT_DIR, "s12_preview_verdict.json"), "w", encoding="utf-8", newline="\n").write(VERDICT_TXT)
    log("CHECK-ONLY: nothing written (previews in s12_preview_prose.txt / s12_preview_verdict.json)")
    sys.exit(0)
prewrite_asserts()
assert not os.path.exists(PROSE_PATH) and not os.path.exists(VERDICT_PATH), "deliverable already exists"
with open(PROSE_PATH, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(PROSE_TXT)
with open(VERDICT_PATH, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(VERDICT_TXT)
# ---- post-write validation (read back)
V2 = getj(VERDICT_PATH)
assert list(V2.keys()) == KEYS and V2["verdict"] in ("UPHELD", "REVISE") and V2["recompute_points"] == N_PTS and V2["recompute_mismatches"] == N_MIS
assert V2["notes"] == NOTES and len(V2["items"]) == N_MIN + N_NIT and V2["must_fix"] == [] and V2["counterexamples_sought"] == V["counterexamples_sought"]
PT2 = rd(PROSE_PATH)
assert all(l in PT2 for l in MAIN_ROWS) and len(MAIN_ROWS) == N_PTS
assert all(any(x["original"] in c for c in CORPUS) for x in V2["items"]) and PT2 == PROSE_TXT and rd(VERDICT_PATH) == VERDICT_TXT and V2["items"] == ITEMS
for pth in (PROSE_PATH, VERDICT_PATH):
    log("WROTE %s %d bytes sha256=%s" % (pth, os.path.getsize(pth), hashlib.sha256(open(pth, "rb").read()).hexdigest()))
