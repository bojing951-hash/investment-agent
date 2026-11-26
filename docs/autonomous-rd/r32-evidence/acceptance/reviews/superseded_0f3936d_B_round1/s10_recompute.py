#!/usr/bin/python3 -I
# Seat script 10: independent numeric recompute for Audit-R32 B round-1.
# usage: /usr/bin/python3 -I s10_recompute.py <snapshot.json> <report.json> <agent_judgment.json> <release_calendar.json> <metric_registry.json> <out_dir>
# Read-only on all inputs; writes recompute_points.json / recompute_points.txt into <out_dir>.
import json, sys, datetime, math

SNAP, REP, AJ, CAL, REG, OUT = sys.argv[1:7]
snap = json.load(open(SNAP, encoding="utf-8"))
rep = json.load(open(REP, encoding="utf-8"))
aj = json.load(open(AJ, encoding="utf-8"))
cal = json.load(open(CAL, encoding="utf-8"))
reg = json.load(open(REG, encoding="utf-8"))
regm = {m["metric_id"]: m for m in reg["metrics"]}

POINTS = []

def add(cat, pid, source, computed, reported, ok, note=""):
    POINTS.append({"cat": cat, "id": pid, "source": source, "computed": computed,
                   "reported": reported, "match": bool(ok), "note": note})

def S(mid):
    s = snap["series_store"].get(mid)
    if s is None:
        return None
    return list(zip(s["dates"], s["values"]))

def val(mid, date):
    for d, v in S(mid):
        if d == date:
            return v
    return None

def on_or_before(mid, date):
    best = None
    for d, v in S(mid):
        if d <= date:
            best = (d, v)
    return best

def monthly(mid, ym):
    return val(mid, ym + "-01")

def yoy(mid, ym):
    y, m = [int(x) for x in ym.split("-")]
    base = "%04d-%02d" % (y - 1, m)
    cur, prev = monthly(mid, ym), monthly(mid, base)
    if cur is None or prev is None:
        return None, (cur, prev)
    return (cur / prev - 1.0) * 100.0, (cur, prev)

def r(x, nd):
    return None if x is None else round(x + 0.0, nd)

def eq_num(computed, reported, nd):
    """computed rounded to nd decimals equals reported (reported given at <= nd decimals)."""
    if computed is None:
        return False
    return abs(round(computed, nd) - reported) <= 0.5 * (10 ** (-nd)) + 1e-12

def days(a, b):
    da = datetime.date(*[int(x) for x in a.split("-")])
    db = datetime.date(*[int(x) for x in b.split("-")])
    return (db - da).days

CUT = "2026-11-23"
SRC_SNAP = "root_overlay/data/daily/research_snapshot_20261123.json"

# ---------------- (1) cutoff / dates ----------------
asof = snap["research_as_of"]
add("①", "A1-cutoff-report", "report.run.evidence_gate.as_of / MAP_REPORT header", rep["run"]["evidence_gate"]["as_of"], CUT, rep["run"]["evidence_gate"]["as_of"] == CUT)
add("①", "A2-cutoff-snapshot", SRC_SNAP + ":target_date", snap["target_date"], "20261123", snap["target_date"] == "20261123")
add("①", "A3-asof-claim", SRC_SNAP + ":research_as_of", asof, aj["quality_gate_notes"][0][aj["quality_gate_notes"][0].find("research_as_of") + len("research_as_of"): aj["quality_gate_notes"][0].find("+08:00") + 6].strip(), asof in aj["quality_gate_notes"][0])
# local clocks at cutoff
utc = datetime.datetime.strptime(asof, "%Y-%m-%dT%H:%M:%S%z").astimezone(datetime.timezone.utc)
offs = {"纽约": -5, "法兰克福": 1, "东京": 9, "上海": 8}
loc = {k: (utc + datetime.timedelta(hours=o)).strftime("%H:%M") for k, o in offs.items()}
claim = {"纽约": "09:53", "法兰克福": "15:53", "东京": "23:53", "上海": "22:53"}
add("①", "A4-local-clocks", SRC_SNAP + ":research_as_of (UTC%+.0f 固定标准时偏移换算)" % 0, loc, claim, loc == claim,
    "11 月纽约=EST(-5)/法兰克福=CET(+1),由 22:53:47+08:00=14:53:47Z 换算")

# max observation date across the whole snapshot (no post-cutoff obs available at all)
maxd = {}
for mid, s in snap["series_store"].items():
    ds = [d for d, v in zip(s["dates"], s["values"]) if v is not None]
    if ds:
        maxd[mid] = max(ds)
overall_max = max(maxd.values())
add("①", "A5-no-post-cutoff-obs", SRC_SNAP + ":series_store[*].dates max", overall_max, "<=2026-11-23", overall_max <= CUT)
late = sorted(mid for mid, d in maxd.items() if d > CUT)
add("①", "A5b-late-series-count", SRC_SNAP + ":series_store (date>2026-11-23)", len(late), 0, len(late) == 0)

last_dates = {m: maxd.get(m) for m in ["SPX", "VIX", "GOLD_F", "DXY", "USDJPY", "NIKKEI225", "BEI_10Y", "TIPS_10Y", "UST_10Y", "EA_HICP_YOY", "CPI", "CORE_CPI", "INDPRO", "UNEMPLOYMENT", "JP_POLICY_RATE", "CORE_PCE", "US_REAL_GDP", "EA_REAL_GDP_YOY"]}
add("①", "A6-cited-last-obs-dates", SRC_SNAP + ":series_store[*] last date", last_dates,
    {"SPX": "2026-11-23", "VIX": "2026-11-23", "GOLD_F": "2026-11-23", "DXY": "2026-11-23", "USDJPY": "2026-11-23", "NIKKEI225": "2026-11-20",
     "BEI_10Y": "2026-11-20", "TIPS_10Y": "2026-11-19", "UST_10Y": "2026-11-19", "EA_HICP_YOY": "2026-10-01", "CPI": "2026-10-01", "CORE_CPI": "2026-10-01",
     "INDPRO": "2026-10-01", "UNEMPLOYMENT": "2026-10-01", "JP_POLICY_RATE": "2026-10-01", "CORE_PCE": "2026-09-01", "US_REAL_GDP": "2026-07-01", "EA_REAL_GDP_YOY": "2026-07-01"},
    last_dates == {"SPX": "2026-11-23", "VIX": "2026-11-23", "GOLD_F": "2026-11-23", "DXY": "2026-11-23", "USDJPY": "2026-11-23", "NIKKEI225": "2026-11-20",
     "BEI_10Y": "2026-11-20", "TIPS_10Y": "2026-11-19", "UST_10Y": "2026-11-19", "EA_HICP_YOY": "2026-10-01", "CPI": "2026-10-01", "CORE_CPI": "2026-10-01",
     "INDPRO": "2026-10-01", "UNEMPLOYMENT": "2026-10-01", "JP_POLICY_RATE": "2026-10-01", "CORE_PCE": "2026-09-01", "US_REAL_GDP": "2026-07-01", "EA_REAL_GDP_YOY": "2026-07-01"})

# anchor publication feasibility: publication dates from engine grid, re-derived by rule arithmetic and compared to as_of
cells = rep["research_plan"]["point_values"]["cells"]
grid = {c["metric_id"]: c["anchors"] for c in cells}
rule_ok = True
pub_detail = {}
for mid, anc in grid.items():
    for lab, a in anc.items():
        pd_ = a.get("publication_date")
        asf = a.get("as_of")
        pub_detail[mid + "|" + lab] = (a["observation_date"], pd_, asf)
        if pd_ is None or pd_ > asf:
            rule_ok = False
add("①", "A7-anchor-publication<=anchor-asof", "report.research_plan.point_values.cells[*].anchors.*.publication_date vs as_of", pub_detail, "all publication_date<=as_of", rule_ok)
# rule arithmetic: month-end + lag ; quarter-end + 29
lag = {"CPI": 13, "CORE_CPI": 13, "UNEMPLOYMENT": 5, "INDPRO": 15, "JP_POLICY_RATE": 5, "EA_HICP_YOY": 16, "CORE_PCE": 30}
def month_end(ym):
    y, m = [int(x) for x in ym.split("-")]
    nm = datetime.date(y + (m == 12), (m % 12) + 1, 1)
    return (nm - datetime.timedelta(days=1)).isoformat()
arith = {}
ok_a = True
for mid, anc in grid.items():
    for lab, a in anc.items():
        od = a["observation_date"]
        if mid in lag:
            exp = (datetime.date(*[int(x) for x in month_end(od[:7]).split("-")]) + datetime.timedelta(days=lag[mid])).isoformat()
        else:
            exp = (datetime.date(*[int(x) for x in a["period_end"].split("-")]) + datetime.timedelta(days=29 if mid == "US_REAL_GDP" else 35)).isoformat()
        arith[mid + "|" + lab] = (exp, a["publication_date"])
        if exp != a["publication_date"]:
            ok_a = False
add("①", "A8-publication-rule-arithmetic", "period_end + 规则天数 vs engine publication_date", arith, "逐项相等", ok_a)

# ---------------- (2) point anchors from series_store ----------------
g = lambda mid, lab, k="value": grid[mid][lab].get(k)
# US_REAL_GDP
add("②", "B1-GDP-3m", SRC_SNAP + ":series_store.US_REAL_GDP@2026-04-01", monthly("US_REAL_GDP", "2026-04"), 24408.011, eq_num(monthly("US_REAL_GDP", "2026-04"), 24408.011, 3))
add("②", "B2-GDP-latest", SRC_SNAP + ":series_store.US_REAL_GDP@2026-07-01", monthly("US_REAL_GDP", "2026-07"), 24611.077, eq_num(monthly("US_REAL_GDP", "2026-07"), 24611.077, 3))
y, pair = yoy("US_REAL_GDP", "2026-04")
add("③", "B3-GDP-yoy-Q2", "series_store.US_REAL_GDP %s / %s" % pair, y, 2.19, eq_num(y, 2.19, 2), "基期=2025-04-01 同季")
y, pair = yoy("US_REAL_GDP", "2026-07")
add("③", "B4-GDP-yoy-Q3", "series_store.US_REAL_GDP %s / %s" % pair, y, 2.07, eq_num(y, 2.07, 2), "基期=2025-07-01 同季")
# UNEMPLOYMENT
add("②", "B5-UNEMP-3m", SRC_SNAP + ":series_store.UNEMPLOYMENT@2026-07-01", monthly("UNEMPLOYMENT", "2026-07"), 4.1, eq_num(monthly("UNEMPLOYMENT", "2026-07"), 4.1, 1))
add("②", "B6-UNEMP-latest", SRC_SNAP + ":series_store.UNEMPLOYMENT@2026-10-01", monthly("UNEMPLOYMENT", "2026-10"), 4.1, eq_num(monthly("UNEMPLOYMENT", "2026-10"), 4.1, 1))
# INDPRO
add("②", "B7-INDPRO-3m", SRC_SNAP + ":series_store.INDPRO@2026-07-01", monthly("INDPRO", "2026-07"), 103.1675, eq_num(monthly("INDPRO", "2026-07"), 103.1675, 4))
add("②", "B8-INDPRO-latest", SRC_SNAP + ":series_store.INDPRO@2026-10-01", monthly("INDPRO", "2026-10"), 103.3954, eq_num(monthly("INDPRO", "2026-10"), 103.3954, 4))
y, pair = yoy("INDPRO", "2026-07")
add("③", "B9-INDPRO-yoy-07", "series_store.INDPRO %s / %s" % pair, y, 1.25, eq_num(y, 1.25, 2), "基期=2025-07-01 同月")
y, pair = yoy("INDPRO", "2026-10")
add("③", "B10-INDPRO-yoy-10", "series_store.INDPRO %s / %s" % pair, y, 2.15, eq_num(y, 2.15, 2), "基期=2025-10-01 同月")
c = (monthly("INDPRO", "2026-10") / monthly("INDPRO", "2026-07") - 1) * 100
add("⑩", "B11-INDPRO-level-chg", "INDPRO 2026-10 / 2026-07", r(c, 4), 0.22, eq_num(c, 0.22, 2), "走位面「仅 +0.22%」")
c = (monthly("INDPRO", "2026-10") / monthly("INDPRO", "2026-09") - 1) * 100
add("⑩", "B12-INDPRO-mom-10", "INDPRO 2026-10 / 2026-09 (%s / %s)" % (monthly("INDPRO", "2026-10"), monthly("INDPRO", "2026-09")), r(c, 4), -0.43, eq_num(c, -0.43, 2), "「2026-10 环比 -0.43%」")
c = (monthly("INDPRO", "2025-10") / monthly("INDPRO", "2025-07") - 1) * 100
add("⑩", "B13-INDPRO-base-2025", "INDPRO 2025-10 / 2025-07 (%s / %s)" % (monthly("INDPRO", "2025-10"), monthly("INDPRO", "2025-07")), r(c, 4), -0.66, eq_num(c, -0.66, 2), "「上年 2025-07→2025-10 基数下行 0.66%」")
# CPI
add("②", "B14-CPI-3m", SRC_SNAP + ":series_store.CPI@2026-07-01", monthly("CPI", "2026-07"), 332.813, eq_num(monthly("CPI", "2026-07"), 332.813, 3))
add("②", "B15-CPI-latest", SRC_SNAP + ":series_store.CPI@2026-10-01", monthly("CPI", "2026-10"), 337.476, eq_num(monthly("CPI", "2026-10"), 337.476, 3))
y, pair = yoy("CPI", "2026-07")
add("③", "B16-CPI-yoy-07", "series_store.CPI %s / %s" % pair, y, 3.3, eq_num(y, 3.3, 2), "基期=2025-07-01 同月")
y, pair = yoy("CPI", "2026-10")
add("③", "B17-CPI-yoy-10-NA", "series_store.CPI 2026-10 与 2025-10", {"yoy": y, "pair": pair}, "不可得(缺2025-10基期)", y is None and pair[0] is not None and pair[1] is None)
# nearest-other-month substitution would have given:
alt = (monthly("CPI", "2026-10") / monthly("CPI", "2025-11") - 1) * 100
add("③", "B17b-CPI-yoy-10-if-substituted", "CPI 2026-10 / 2025-11 (相邻月替代口径,报告未使用)", r(alt, 2), "报告未给出该数", True, "反方核: 若以相邻月替代会得 %.2f%%, 报告如实标不可得" % alt)
y, pair = yoy("CPI", "2026-09")
add("③", "B18-CPI-latest-valid-yoy", "series_store.CPI %s / %s" % pair, {"date": "2026-09-01", "yoy": r(y, 4)}, {"date": "2026-09-01", "yoy": 3.72}, eq_num(y, 3.72, 2), "最近有效同比=2026-09")
# verify no later valid yoy exists
add("③", "B18b-CPI-latest-valid-is-09", "series_store.CPI 最后观测=2026-10(同比不可得)", maxd["CPI"], "2026-10-01", maxd["CPI"] == "2026-10-01")
# CORE_CPI
add("②", "B19-CCPI-3m", SRC_SNAP + ":series_store.CORE_CPI@2026-07-01", monthly("CORE_CPI", "2026-07"), 336.789, eq_num(monthly("CORE_CPI", "2026-07"), 336.789, 3))
add("②", "B20-CCPI-latest", SRC_SNAP + ":series_store.CORE_CPI@2026-10-01", monthly("CORE_CPI", "2026-10"), 339.9, eq_num(monthly("CORE_CPI", "2026-10"), 339.9, 3))
y, pair = yoy("CORE_CPI", "2026-07")
add("③", "B21-CCPI-yoy-07", "series_store.CORE_CPI %s / %s" % pair, y, 2.47, eq_num(y, 2.47, 2), "基期=2025-07-01 同月")
y, pair = yoy("CORE_CPI", "2026-10")
add("③", "B22-CCPI-yoy-10-NA", "series_store.CORE_CPI 2026-10 与 2025-10", {"yoy": y, "pair": pair}, "不可得(缺2025-10基期)", y is None and pair[0] is not None and pair[1] is None)
y, pair = yoy("CORE_CPI", "2026-09")
add("③", "B23-CCPI-latest-valid-yoy", "series_store.CORE_CPI %s / %s" % pair, {"date": "2026-09-01", "yoy": r(y, 4)}, {"date": "2026-09-01", "yoy": 2.57}, eq_num(y, 2.57, 2), "最近有效同比=2026-09")
# CORE_PCE
add("②", "B24-CPCE-3m", SRC_SNAP + ":series_store.CORE_PCE@2026-06-01", monthly("CORE_PCE", "2026-06"), 129.969, eq_num(monthly("CORE_PCE", "2026-06"), 129.969, 3))
add("②", "B25-CPCE-latest", SRC_SNAP + ":series_store.CORE_PCE@2026-09-01", monthly("CORE_PCE", "2026-09"), 130.902, eq_num(monthly("CORE_PCE", "2026-09"), 130.902, 3))
# 2026-07 观测在库(存量),但按规则发布日=月末+30天 > 3个月前锚的 as_of(2026-08-23)→当时不可见
_cp07_pub = (datetime.date(*[int(x) for x in month_end("2026-07").split("-")]) + datetime.timedelta(days=30)).isoformat()
_cp06_pub = (datetime.date(*[int(x) for x in month_end("2026-06").split("-")]) + datetime.timedelta(days=30)).isoformat()
_cp07_pub_eng = grid["CORE_PCE"]["3个月前"]["publication_date"] if "3个月前" in grid["CORE_PCE"] else None
add("②", "B25b-CPCE-3m-anchor-month", "CORE_PCE 2026-07 观测在库值 / 规则发布日(月末+30) vs 3个月前锚 as_of",
    {"CPCE@2026-07": monthly("CORE_PCE", "2026-07"), "pub_2026-07": _cp07_pub, "pub_2026-06": _cp06_pub, "anchor_as_of": grid["CORE_PCE"]["3个月前"].get("as_of"), "engine_anchor_obs": grid["CORE_PCE"]["3个月前"].get("observation_date")},
    {"CPCE@2026-07": 130.148, "pub_2026-07": "2026-08-30", "pub_2026-06": "2026-07-30", "anchor_as_of": "2026-08-23", "engine_anchor_obs": "2026-06-01"},
    monthly("CORE_PCE", "2026-07") == 130.148 and _cp07_pub == "2026-08-30" and _cp07_pub > grid["CORE_PCE"]["3个月前"]["as_of"] and _cp06_pub == "2026-07-30" and grid["CORE_PCE"]["3个月前"]["observation_date"] == "2026-06-01",
    "2026-07 观测在库但 2026-08-30 才发布(晚于锚 as_of 2026-08-23)→3个月前锚取 2026-06 与引擎格一致(可见性口径,非缺席口径;席位首版此检以『观测缺席』为假设有误,已更正)")
y, pair = yoy("CORE_PCE", "2026-06")
add("③", "B26-CPCE-yoy-06", "series_store.CORE_PCE %s / %s" % pair, y, 3.04, eq_num(y, 3.04, 2), "基期=2025-06-01 同月")
y, pair = yoy("CORE_PCE", "2026-09")
add("③", "B27-CPCE-yoy-09", "series_store.CORE_PCE %s / %s" % pair, y, 3.12, eq_num(y, 3.12, 2), "基期=2025-09-01 同月")
# EA
add("②", "B28-EAGDP-3m", SRC_SNAP + ":series_store.EA_REAL_GDP_YOY@2026-04-01", monthly("EA_REAL_GDP_YOY", "2026-04"), 1.19, eq_num(monthly("EA_REAL_GDP_YOY", "2026-04"), 1.19, 2))
add("②", "B29-EAGDP-latest", SRC_SNAP + ":series_store.EA_REAL_GDP_YOY@2026-07-01", monthly("EA_REAL_GDP_YOY", "2026-07"), 1.28, eq_num(monthly("EA_REAL_GDP_YOY", "2026-07"), 1.28, 2))
add("②", "B30-EAHICP-3m", SRC_SNAP + ":series_store.EA_HICP_YOY@2026-07-01", monthly("EA_HICP_YOY", "2026-07"), 2.9, eq_num(monthly("EA_HICP_YOY", "2026-07"), 2.9, 1))
add("②", "B31-EAHICP-latest", SRC_SNAP + ":series_store.EA_HICP_YOY@2026-10-01", monthly("EA_HICP_YOY", "2026-10"), 4.0, eq_num(monthly("EA_HICP_YOY", "2026-10"), 4.0, 1))
add("⑩", "B32-EAHICP-delta", "EA_HICP_YOY 2026-10 − 2026-07", r(monthly("EA_HICP_YOY", "2026-10") - monthly("EA_HICP_YOY", "2026-07"), 2), 1.1, eq_num(monthly("EA_HICP_YOY", "2026-10") - monthly("EA_HICP_YOY", "2026-07"), 1.1, 1), "「三个月上行 1.1 个百分点」")
ea26 = [(d, v) for d, v in S("EA_HICP_YOY") if d.startswith("2026")]
add("②", "B33-EAHICP-2026-02", SRC_SNAP + ":series_store.EA_HICP_YOY@2026-02-01", monthly("EA_HICP_YOY", "2026-02"), 1.9, eq_num(monthly("EA_HICP_YOY", "2026-02"), 1.9, 1))
add("②", "B34-EAHICP-2026-05", SRC_SNAP + ":series_store.EA_HICP_YOY@2026-05-01", monthly("EA_HICP_YOY", "2026-05"), 3.2, eq_num(monthly("EA_HICP_YOY", "2026-05"), 3.2, 1))
add("②", "B35-EAHICP-2026-06", SRC_SNAP + ":series_store.EA_HICP_YOY@2026-06-01", monthly("EA_HICP_YOY", "2026-06"), 2.8, eq_num(monthly("EA_HICP_YOY", "2026-06"), 2.8, 1))
mx = max(v for d, v in ea26)
add("⑥", "B36-EAHICP-year-high", "EA_HICP_YOY 2026 年内最大值", {"max": mx, "at": [d for d, v in ea26 if v == mx]}, {"max": 4.0, "at": ["2026-10-01"]}, mx == 4.0 and [d for d, v in ea26 if v == mx] == ["2026-10-01"], "「读数为年内新高」")
add("②", "B36b-EAHICP-2026-path", SRC_SNAP + ":series_store.EA_HICP_YOY 2026 全年", [(d[:7], v) for d, v in ea26], "见 note", True, "; ".join("%s=%s" % (d[:7], v) for d, v in ea26))
# JP
add("②", "B37-JPR-3m", SRC_SNAP + ":series_store.JP_POLICY_RATE@2026-07-01", monthly("JP_POLICY_RATE", "2026-07"), 0.978, eq_num(monthly("JP_POLICY_RATE", "2026-07"), 0.978, 3))
add("②", "B38-JPR-latest", SRC_SNAP + ":series_store.JP_POLICY_RATE@2026-10-01", monthly("JP_POLICY_RATE", "2026-10"), 1.227, eq_num(monthly("JP_POLICY_RATE", "2026-10"), 1.227, 3))
steps = {"2025-11": 0.478, "2025-12": 0.557, "2026-01": 0.728, "2026-04": 0.727, "2026-05": 0.727, "2026-06": 0.841, "2026-08": 0.977, "2026-09": 1.043}
jp_path = []
for ym, exp in steps.items():
    v = monthly("JP_POLICY_RATE", ym)
    jp_path.append((ym, v))
    add("②", "B39-JPR-step-" + ym, SRC_SNAP + ":series_store.JP_POLICY_RATE@%s-01" % ym, v, exp, eq_num(v, exp, 3))
full = [(d[:7], v) for d, v in S("JP_POLICY_RATE") if "2025-10" <= d[:7] <= "2026-10"]
add("②", "B40-JPR-full-path", SRC_SNAP + ":series_store.JP_POLICY_RATE 2025-10..2026-10", full, "见 note", True, "; ".join("%s=%s" % t for t in full))
c = (monthly("JP_POLICY_RATE", "2026-10") - monthly("JP_POLICY_RATE", "2025-12")) * 100
add("⑤", "B45-JPR-net-engine", "JP_POLICY_RATE 2026-10 − 2025-12 (bp)", r(c, 2), 67, eq_num(c, 67, 0), "引擎政策窗口径(窗首观测 2025-12)")
c = (monthly("JP_POLICY_RATE", "2026-10") - monthly("JP_POLICY_RATE", "2025-11")) * 100
add("⑤", "B46-JPR-net-alt", "JP_POLICY_RATE 2026-10 − 2025-11 (bp)", r(c, 2), 75, eq_num(c, 75, 0), "窗启时在值口径")
deltas = {}
for a, b in [("2025-11", "2025-12"), ("2025-12", "2026-01"), ("2026-05", "2026-06"), ("2026-06", "2026-07"), ("2026-08", "2026-09"), ("2026-09", "2026-10")]:
    deltas[b] = round((monthly("JP_POLICY_RATE", b) - monthly("JP_POLICY_RATE", a)) * 100)
add("②", "B47-JPR-step-deltas", "JP_POLICY_RATE 相邻月均差 (bp)", deltas, {"2025-12": 8, "2026-01": 17, "2026-06": 11, "2026-07": 14, "2026-09": 7, "2026-10": 18}, deltas == {"2025-12": 8, "2026-01": 17, "2026-06": 11, "2026-07": 14, "2026-09": 7, "2026-10": 18})
ups = [(d[:7], v) for i, (d, v) in enumerate(S("JP_POLICY_RATE")) if d.startswith("2026") and i > 0 and v is not None and S("JP_POLICY_RATE")[i - 1][1] is not None and v > S("JP_POLICY_RATE")[i - 1][1]]
add("⑥", "B48-JPR-2026-upsteps", "JP_POLICY_RATE 2026 年内月均上行台阶", ups, "2026-01,06,07 (+09,10)", [u[0] for u in ups] == ["2026-01", "2026-06", "2026-07", "2026-09", "2026-10"], "「2026-07 为 2026 年内第三个上行月均台阶(此前 2026-01 +17bp、2026-06 +11bp)」")

# ---------------- (4) policy face ----------------
ents = {e["entry_id"]: e for e in cal["entries"]}
e1 = ents["RC-JP-BOJ-TARGET-2026-09"]
e2 = ents["RC-JP-BOJ-MAINT-2026-10"]
add("④", "C1-BOJ-decision", "release_calendar.entries[RC-JP-BOJ-TARGET-2026-09].decision_date", e1["decision_date"], "2026-09-18", e1["decision_date"] == "2026-09-18")
add("④", "C2-BOJ-effective", "release_calendar.entries[RC-JP-BOJ-TARGET-2026-09].effective_on", e1["effective_on"], "2026-09-24", e1["effective_on"] == "2026-09-24")
add("④", "C3-BOJ-target", "release_calendar.entries[RC-JP-BOJ-TARGET-2026-09].target_value", e1["target_value"], 1.25, e1["target_value"] == 1.25)
add("④", "C4-BOJ-maintain", "release_calendar.entries[RC-JP-BOJ-MAINT-2026-10]", {"decision_date": e2["decision_date"], "target_value": e2["target_value"], "kind": e2["kind"]}, {"decision_date": "2026-10-30", "target_value": 1.25, "kind": "policy_maintenance"}, e2["decision_date"] == "2026-10-30" and e2["target_value"] == 1.25 and e2["kind"] == "policy_maintenance")
add("④", "C5-days-effective", "2026-11-23 − 2026-09-24", days("2026-09-24", CUT), 60, days("2026-09-24", CUT) == 60)
add("④", "C6-days-decision", "2026-11-23 − 2026-09-18", days("2026-09-18", CUT), 66, days("2026-09-18", CUT) == 66)
add("④", "C7-days-maintain", "2026-11-23 − 2026-10-30 (MAP 官方记录面「距维持」)", days("2026-10-30", CUT), 24, days("2026-10-30", CUT) == 24)
pol = [e for e in cal["entries"] if e.get("kind") in ("policy_decision", "policy_maintenance")]
add("④", "C8-policy-entries", "release_calendar.entries kind=policy_*", [(e["entry_id"], e.get("decision_date")) for e in pol], "2 条,均日本央行", len(pol) == 2 and all(e["metric_id"] == "JP_POLICY_TARGET" for e in pol))
add("④", "C8b-no-later-boj", "release_calendar JP_POLICY_TARGET 条目 decision_date 最大值", max(e["decision_date"] for e in pol), "2026-10-30", max(e["decision_date"] for e in pol) == "2026-10-30", "「此后是否有新决议引擎日历无条目」")
add("⑭", "C9-target-series-absent", "metric_registry.metrics[*].metric_id + snapshot.series_store keys", {"in_registry": "JP_POLICY_TARGET" in regm, "in_store": "JP_POLICY_TARGET" in snap["series_store"]}, {"in_registry": False, "in_store": False}, ("JP_POLICY_TARGET" not in regm) and ("JP_POLICY_TARGET" not in snap["series_store"]))
add("④", "C10-calendar-version", "release_calendar.version", cal["version"], "v1.5.0", cal["version"] == "1.5.0")
add("④", "C12-JPR-registry-name", "metric_registry JP_POLICY_RATE.display_name", regm["JP_POLICY_RATE"]["display_name"], "日本无担保隔夜拆借利率(月均)", regm["JP_POLICY_RATE"]["display_name"] == "日本无担保隔夜拆借利率(月均)")
add("④", "C13-first-full-month", "生效日 2026-09-24 之后首个整月", "2026-10", "2026-10", True, "9-24 生效→10 月为首个整月;月均台阶落在 2026-09→2026-10 之交")
pdf = rep["research_plan"]["policy_doc_facts"]
add("④", "C14-FOMC-minutes", "report.research_plan.policy_doc_facts", [(d["doc_id"], d["published_on"]) for d in pdf], [("FOMC-MINUTES-2026-10", "2026-11-18")], [(d["doc_id"], d["published_on"]) for d in pdf] == [("FOMC-MINUTES-2026-10", "2026-11-18")])
add("④", "C14b-minutes<=cutoff", "FOMC 纪要发布日 ≤ 研究截止日", pdf[0]["published_on"] <= CUT, True, pdf[0]["published_on"] <= CUT)
add("④", "C15-policy-clusters-empty", "report.research_plan.policy_event_clusters.clusters", rep["research_plan"]["policy_event_clusters"]["clusters"], [], rep["research_plan"]["policy_event_clusters"]["clusters"] == [])

# ---------------- (5) rates trio ----------------
def chg_bp(mid, a, b):
    va, vb = val(mid, a), val(mid, b)
    return None if (va is None or vb is None) else (vb - va) * 100.0, va, vb
n, nu0, nu1 = chg_bp("UST_10Y", "2026-10-20", "2026-11-19")
rl, tr0, tr1 = chg_bp("TIPS_10Y", "2026-10-20", "2026-11-19")
be, be0, be1 = chg_bp("BEI_10Y", "2026-10-20", "2026-11-19")
add("⑤", "D1-UST-1m-bp", "UST_10Y 2026-11-19 − 2026-10-20 (%s→%s)" % (nu0, nu1), r(n, 1), -8, eq_num(n, -8, 0))
add("⑤", "D2-TIPS-1m-bp", "TIPS_10Y 2026-11-19 − 2026-10-20 (%s→%s)" % (tr0, tr1), r(rl, 1), 11, eq_num(rl, 11, 0))
add("⑤", "D3-BEI-1m-bp", "BEI_10Y 2026-11-19 − 2026-10-20 (%s→%s)" % (be0, be1), r(be, 1), -19, eq_num(be, -19, 0))
add("⑤", "D4-identity-1m", "名义 − (实际+盈亏平衡)", r(n - (rl + be), 2), 0, abs(n - (rl + be)) < 0.05, "残差 0")
add("⑤", "D5-levels-1119", "UST_10Y/TIPS_10Y/BEI_10Y @2026-11-19", [nu1, tr1, be1], [5.04, 2.88, 2.16], eq_num(nu1, 5.04, 2) and eq_num(tr1, 2.88, 2) and eq_num(be1, 2.16, 2))
add("⑤", "D5b-BEI-level-1120", "BEI_10Y@2026-11-20", val("BEI_10Y", "2026-11-20"), 2.15, eq_num(val("BEI_10Y", "2026-11-20"), 2.15, 2))
n3, nu0, nu1 = chg_bp("UST_10Y", "2026-08-19", "2026-11-19")
r3, tr0, tr1 = chg_bp("TIPS_10Y", "2026-08-19", "2026-11-19")
b3, be0, be1 = chg_bp("BEI_10Y", "2026-08-19", "2026-11-19")
add("⑤", "D6-UST-3m-bp", "UST_10Y 2026-11-19 − 2026-08-19 (%s→%s)" % (nu0, nu1), r(n3, 1), 39, eq_num(n3, 39, 0))
add("⑤", "D6-TIPS-3m-bp", "TIPS_10Y 2026-11-19 − 2026-08-19 (%s→%s)" % (tr0, tr1), r(r3, 1), 53, eq_num(r3, 53, 0))
add("⑤", "D6-BEI-3m-bp", "BEI_10Y 2026-11-19 − 2026-08-19 (%s→%s)" % (be0, be1), r(b3, 1), -14, eq_num(b3, -14, 0))
add("⑤", "D6-identity-3m", "名义 − (实际+盈亏平衡)", r(n3 - (r3 + b3), 2), 0, abs(n3 - (r3 + b3)) < 0.05, "残差 0")
add("⑤", "D8-BEI-3m-from", "BEI_10Y@2026-08-19", be0, 2.30, eq_num(be0, 2.30, 2), "「自 2.30 回落至 2.16」")
n12, nu0, nu1 = chg_bp("UST_10Y", "2025-11-19", "2026-11-19")
r12, tr0, tr1 = chg_bp("TIPS_10Y", "2025-11-19", "2026-11-19")
b12, be0, be1 = chg_bp("BEI_10Y", "2025-11-19", "2026-11-19")
add("⑤", "D7-UST-12m-bp", "UST_10Y 2026-11-19 − 2025-11-19 (%s→%s)" % (nu0, nu1), r(n12, 1), 91, eq_num(n12, 91, 0))
add("⑤", "D7-TIPS-12m-bp", "TIPS_10Y 2026-11-19 − 2025-11-19 (%s→%s)" % (tr0, tr1), r(r12, 1), 102, eq_num(r12, 102, 0))
add("⑤", "D7-BEI-12m-bp", "BEI_10Y 2026-11-19 − 2025-11-19 (%s→%s)" % (be0, be1), r(b12, 1), -11, eq_num(b12, -11, 0))
add("⑤", "D7-identity-12m", "名义 − (实际+盈亏平衡)", r(n12 - (r12 + b12), 2), 0, abs(n12 - (r12 + b12)) < 0.05, "残差 0")
add("⑤", "D7b-days-12m", "日历日间隔 2025-11-19→2026-11-19", days("2025-11-19", "2026-11-19"), 365, days("2025-11-19", "2026-11-19") == 365)
add("⑤", "D6b-days-1m", "日历日间隔 2026-10-20→2026-11-19", days("2026-10-20", "2026-11-19"), 30, days("2026-10-20", "2026-11-19") == 30)
win = [(d, v) for d, v in S("BEI_10Y") if "2025-11-19" <= d <= "2026-11-20"]
mn = min(v for d, v in win)
add("⑤", "D10-BEI-12m-min", "BEI_10Y [2025-11-19..2026-11-20] 最小值", {"min": mn, "at": [d for d, v in win if v == mn], "n": len(win)}, {"min": 2.15, "at": ["2026-11-20"]}, mn == 2.15 and [d for d, v in win if v == mn] == ["2026-11-20"], "「12 个月窗内最低」")
add("⑤", "D11-BEI-0227", "BEI_10Y@2026-02-27", val("BEI_10Y", "2026-02-27"), 2.25, eq_num(val("BEI_10Y", "2026-02-27"), 2.25, 2))
add("⑤", "D11-BEI-0504", "BEI_10Y@2026-05-04", val("BEI_10Y", "2026-05-04"), 2.50, eq_num(val("BEI_10Y", "2026-05-04"), 2.50, 2))
# 引擎「近30日」= facts[].derived.m1 窗(fact basis 2026-10-23 → 最新 2026-11-20),非 2026-10-21
b_1m_store, x0, x1 = chg_bp("BEI_10Y", "2026-10-23", "2026-11-20")
add("⑤", "D11b-BEI-engine-30d", "BEI_10Y 2026-11-20 − 2026-10-23 (%s→%s)" % (x0, x1), [r(b_1m_store, 1), x0, x1], [-19, 2.34, 2.15], eq_num(b_1m_store, -19, 0) and eq_num(x0, 2.34, 2) and eq_num(x1, 2.15, 2), "MAP 对质表引擎面「近30日2.34→2.15,下降19bp」= fact m1 窗(席位首版此检误用 2026-10-21 起点得 -22bp,已更正为引擎窗)")
t22, t0, t1 = chg_bp("TIPS_10Y", "2026-10-23", "2026-11-19")
add("⑤", "D12-TIPS-1023", "TIPS_10Y 2026-11-19 − 2026-10-23 (%s→%s)" % (t0, t1), r(t22, 1), 22, eq_num(t22, 22, 0), "「同窗 TIPS_10Y 2.66→2.88(+22bp)」")
add("⑤", "D12b-TIPS-levels-1023", "TIPS_10Y @2026-10-23 / @2026-11-19", [t0, t1], [2.66, 2.88], eq_num(t0, 2.66, 2) and eq_num(t1, 2.88, 2))

# ---------------- asset windows ----------------
def pct(mid, a, b):
    va, vb = val(mid, a), val(mid, b)
    return None if (va is None or vb is None) else (vb / va - 1) * 100.0, va, vb
for mid, a, b, rep_pct, rep_from, rep_to, pid in [
    ("SPX", "2026-10-23", "2026-11-23", -5.51, 7623.68, 7203.85, "E1"),
    ("NIKKEI225", "2026-10-23", "2026-11-20", -9.98, 62693.2, 56436.65, "E2"),
    ("GOLD_F", "2026-10-23", "2026-11-23", -8.05, 4007.9, 3685.2, "E3"),
    ("DXY", "2026-10-23", "2026-11-23", 2.23, 101.81, 104.079, "E4"),
    ("VIX", "2026-10-23", "2026-11-23", 38.87, 19.45, 27.01, "E5"),
]:
    c, va, vb = pct(mid, a, b)
    add("⑤", pid + "-" + mid + "-chg", "%s %s→%s (%r→%r)" % (mid, a, b, va, vb), r(c, 4), rep_pct, eq_num(c, rep_pct, 2))
    ndf, ndt = len(repr(rep_from).split(".")[1]), len(repr(rep_to).split(".")[1])   # 报告端点各自显示精度
    add("⑤", pid + "-" + mid + "-ends", "series_store.%s @%s / @%s" % (mid, a, b), [va, vb], [rep_from, rep_to], eq_num(va, rep_from, ndf) and eq_num(vb, rep_to, ndt),
        "" if ndf == 2 else "MAP 表起值显示 1 位小数(62693.2),序列值 62693.16→按显示精度比对(席位首版按 2 位比对有误,已更正)")
add("②", "E6-USDJPY", "series_store.USDJPY@2026-11-23", val("USDJPY", "2026-11-23"), 159.35, eq_num(val("USDJPY", "2026-11-23"), 159.35, 2))
c, va, vb = pct("SPX", "2026-10-23", "2026-11-20")
add("⑤", "E7-SPX-close-basis", "SPX 2026-11-20 / 2026-10-23 (%r→%r)" % (va, vb), r(c, 4), -9.36, eq_num(c, -9.36, 2), "同日收盘口径")
c, va, vb = pct("VIX", "2026-10-23", "2026-11-20")
add("⑤", "E8-VIX-close-basis", "VIX 2026-11-20 / 2026-10-23 (%r→%r)" % (va, vb), r(c, 4), 84.52, eq_num(c, 84.52, 2), "同日收盘口径")
c, va, vb = pct("SPX", "2026-08-19", "2026-11-20")
add("⑤", "E9-SPX-3m-close", "SPX 2026-11-20 / 2026-08-19 (%r→%r)" % (va, vb), r(c, 4), -10.35, eq_num(c, -10.35, 2), "三个月收盘口径")
c, va, vb = pct("VIX", "2026-08-19", "2026-11-20")
add("⑤", "E10-VIX-3m-close", "VIX 2026-11-20 / 2026-08-19 (%r→%r)" % (va, vb), r(c, 4), 141.03, eq_num(c, 141.03, 2))
add("⑤", "E10b-VIX-3m-ends", "VIX @2026-08-19 / @2026-11-20", [va, vb], [14.89, 35.89], eq_num(va, 14.89, 2) and eq_num(vb, 35.89, 2))
c, va, vb = pct("UST_10Y", "2026-10-23", "2026-11-19")
add("⑤", "E11-UST-asset-row", "UST_10Y 2026-11-19 / 2026-10-23 (%r→%r)" % (va, vb), r(c, 2), 0.8, eq_num(c, 0.8, 1), "MAP 资产月窗行 +0.8%")
# SPX common window to 11-19 (used in reverse attack of link 3)
c, va, vb = pct("SPX", "2026-10-23", "2026-11-19")
add("④", "E12-SPX-common-to-1119", "SPX 2026-11-19 / 2026-10-23 (%r→%r)" % (va, vb), r(c, 4), "未载(席位补充核)", True, "反方核: 与 TIPS_10Y 同止于 11-19 的 SPX 同窗跌幅")

# ---------------- turning / yoy candidates ----------------
yy = lambda mid, ym: yoy(mid, ym)[0]
add("③", "F1-CPI-yoy-02", "CPI 2026-02 / 2025-02", r(yy("CPI", "2026-02"), 4), 2.434, eq_num(yy("CPI", "2026-02"), 2.434, 4))
add("③", "F1-CPI-yoy-05", "CPI 2026-05 / 2025-05", r(yy("CPI", "2026-05"), 4), 4.1666, eq_num(yy("CPI", "2026-05"), 4.1666, 4))
add("⑥", "F1-CPI-delta", "CPI 同比 2026-05 − 2026-02", r(yy("CPI", "2026-05") - yy("CPI", "2026-02"), 4), 1.7326, eq_num(yy("CPI", "2026-05") - yy("CPI", "2026-02"), 1.7326, 4), "「三个月上行 1.7326 个百分点」")
cpi26 = [(d[:7], yoy("CPI", d[:7])[0]) for d, v in S("CPI") if d.startswith("2026")]
mx = max(v for _, v in cpi26 if v is not None)
add("⑥", "F2-CPI-yoy-2026-max", "CPI 同比 2026 年内最大值", {"max": r(mx, 4), "at": [m for m, v in cpi26 if v == mx]}, {"max": 4.1666, "at": ["2026-05"]}, eq_num(mx, 4.17, 2) and [m for m, v in cpi26 if v == mx] == ["2026-05"], "「2026-05 高点 4.17」")
add("②", "F2b-CPI-yoy-2026-path", "CPI 同比 2026 逐月", [(m, r(v, 4) if v is not None else None) for m, v in cpi26], "见 note", True, "; ".join("%s=%s" % (m, r(v, 4) if v is not None else None) for m, v in cpi26))
for ym, exp in [("2026-02", 2.4725), ("2026-05", 2.8229), ("2026-08", 2.4462), ("2026-09", 2.5658)]:
    add("③", "F3-CCPI-yoy-" + ym, "CORE_CPI %s / 上年同月" % ym, r(yy("CORE_CPI", ym), 4), exp, eq_num(yy("CORE_CPI", ym), exp, 4))
cc26 = [(d[:7], yoy("CORE_CPI", d[:7])[0]) for d, v in S("CORE_CPI") if d.startswith("2026")]
add("②", "F3b-CCPI-yoy-2026-path", "CORE_CPI 同比 2026 逐月", [(m, r(v, 4) if v is not None else None) for m, v in cc26], "见 note", True, "; ".join("%s=%s" % (m, r(v, 4) if v is not None else None) for m, v in cc26))
add("③", "F4-INDPRO-yoy-2025-11", "INDPRO 2025-11 / 2024-11", r(yy("INDPRO", "2025-11"), 4), 1.7543, eq_num(yy("INDPRO", "2025-11"), 1.7543, 4))
add("③", "F4-INDPRO-yoy-2026-02", "INDPRO 2026-02 / 2025-02", r(yy("INDPRO", "2026-02"), 4), 0.7972, eq_num(yy("INDPRO", "2026-02"), 0.7972, 4))
add("③", "F5-CPCE-yoy-2025-11", "CORE_PCE 2025-11 / 2024-11", r(yy("CORE_PCE", "2025-11"), 4), 2.7212, eq_num(yy("CORE_PCE", "2025-11"), 2.7212, 4))
add("③", "F5-CPCE-yoy-2026-02", "CORE_PCE 2026-02 / 2025-02", r(yy("CORE_PCE", "2026-02"), 4), 2.9592, eq_num(yy("CORE_PCE", "2026-02"), 2.9592, 4))
add("②", "F6-UNEMP-05-08", "UNEMPLOYMENT @2026-05-01 / @2026-08-01", [monthly("UNEMPLOYMENT", "2026-05"), monthly("UNEMPLOYMENT", "2026-08")], [4.3, 4.1], monthly("UNEMPLOYMENT", "2026-05") == 4.3 and monthly("UNEMPLOYMENT", "2026-08") == 4.1)
cands = rep["research_plan"]["turning_candidates"]["candidates"]
top = max(cands, key=lambda c: abs(c["delta"]))
add("⑥", "F7-pool-max", "report.research_plan.turning_candidates.candidates |Δ| 最大者", {"metric": top["metric_id"], "delta": top["delta"], "n_pool": len(cands)}, {"metric": "CPI", "delta": 1.7326, "n_pool": 7}, top["metric_id"] == "CPI" and top["delta"] == 1.7326 and len(cands) == 7)
# candidate face recomputed from store
cmap = {c["metric_id"] + "|" + c["from_ym"]: c for c in cands}
recomputed = []
for mid, a, b in [("CPI", "2026-02", "2026-05"), ("CORE_CPI", "2026-05", "2026-08"), ("INDPRO", "2025-11", "2026-02"), ("CORE_PCE", "2025-11", "2026-02")]:
    c = cmap[mid + "|" + a]
    v0, v1 = yy(mid, a), yy(mid, b)
    recomputed.append(abs(round(v0, 4) - c["value_before"]) < 1e-9 and abs(round(v1, 4) - c["value_after"]) < 1e-9)
for mid, a, b in [("EA_HICP_YOY", "2026-02", "2026-05"), ("JP_POLICY_RATE", "2026-04", "2026-07"), ("UNEMPLOYMENT", "2026-05", "2026-08")]:
    c = cmap[mid + "|" + a]
    recomputed.append(monthly(mid, a) == c["value_before"] and monthly(mid, b) == c["value_after"])
add("⑥", "F7b-pool-recompute", "候选池 7 项前值→后值 series_store 复算", recomputed, "7/7 一致", all(recomputed))
# EA vs US ranking
ea_sep = monthly("EA_HICP_YOY", "2026-09")
us_sep = yy("CPI", "2026-09")
add("⑥", "F8-rank-2026-09", "EA_HICP_YOY@2026-09 vs CPI 同比 2026-09", {"EA": ea_sep, "US": r(us_sep, 4)}, "EA > US", ea_sep > us_sep)
cross = []
for m in range(1, 11):
    ym = "2026-%02d" % m
    e, u = monthly("EA_HICP_YOY", ym), yy("CPI", ym)
    cross.append((ym, e, r(u, 3) if u is not None else None, None if (e is None or u is None) else ("EA>US" if e > u else "EA<US")))
# full comparable history of the ranking (all months where both headline yoy computable)
_rank = []
for d, e in S("EA_HICP_YOY"):
    ym = d[:7]
    u = yy("CPI", ym)
    if e is not None and u is not None:
        _rank.append((ym, e, r(u, 3), "EA>US" if e > u else "EA<US"))
_gt_earlier = [x[0] for x in _rank if x[0] < "2026-09" and x[3] == "EA>US"]
_prior = [x for x in _rank if x[0] < "2026-09"]
_run = 0
for x in reversed(_prior):
    if x[3] == "EA<US":
        _run += 1
    else:
        break
add("⑥", "F8b-rank-crossings", "EA_HICP_YOY vs CPI 同比 全史可比月份位次 (series_store 直算)", {"n_comparable": len(_rank), "first": _rank[0][0], "months_EA_gt_US_earlier_than_2026-09": len(_gt_earlier), "earlier_crossing_span": [_gt_earlier[0], _gt_earlier[-1]] if _gt_earlier else [], "consecutive_EA_lt_US_right_before_2026-09": _run, "2026_rank": [x[3] for x in cross if x[3] is not None]},
    "「两地最新可比同月为九月,更早月份位次有交叉」", len(_gt_earlier) > 0,
    "字面属实: 2022-07..2023-09 共 %d 个月 EA>US;但其后 2023-10..2026-08 连续 %d 个可比月均 EA<US,2026-09 为 2023-09 以来首次反超——陈述未给时间范围(见 MINOR)" % (len(_gt_earlier), _run))
add("⑥", "F8c-ea-path-2026", "EA_HICP_YOY 2026 逐月", [(m, e) for m, e, u, x in cross], "见 note", True, "; ".join("%s=%s" % (m, e) for m, e, u, x in cross))
add("⑩", "F9-headline>core", "CPI 同比 2026-09 vs CORE_CPI 同比 2026-09", [r(us_sep, 4), r(yy("CORE_CPI", "2026-09"), 4)], "headline 3.72 > core 2.57", us_sep > yy("CORE_CPI", "2026-09") and eq_num(us_sep, 3.72, 2) and eq_num(yy("CORE_CPI", "2026-09"), 2.57, 2))
# magnitude comparison EA vs US
add("⑩", "F10-magnitude-EA-vs-US", "HICP 同比 Δ(07→10) vs CPI 同比 Δ(07→09 最近有效)", [r(monthly("EA_HICP_YOY", "2026-10") - monthly("EA_HICP_YOY", "2026-07"), 2), r(us_sep - yy("CPI", "2026-07"), 2)], "欧元区幅度更大", (monthly("EA_HICP_YOY", "2026-10") - monthly("EA_HICP_YOY", "2026-07")) > (us_sep - yy("CPI", "2026-07")))

# ---------------- absences / gate ----------------
ga = snap["gate_a"]
q = aj["quality_gate_notes"][3]
add("⑪", "G1-gate-a-status", "snapshot.gate_a.status", ga["status"], "DEGRADED", ga["status"] == "DEGRADED")
add("⑪", "G1b-core-missing", "snapshot.gate_a.core_missing", ga["core_missing"], [], ga["core_missing"] == [] and "核心缺口 零 项" in q)
add("⑪", "G1c-noncore-missing", "snapshot.gate_a.noncore_missing", sorted(ga["noncore_missing"]), sorted(["BUND_10Y", "BUND_2Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"]), sorted(ga["noncore_missing"]) == sorted(["BUND_10Y", "BUND_2Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"]))
add("⑪", "G1d-noncore-degraded", "snapshot.gate_a.noncore_degraded", sorted(ga["noncore_degraded"]), sorted(["CN_SF_FLOW", "ECB_DFR", "ECB_MRO", "JTSJOL", "M2SL", "SPX_EPS", "SPX_PE_TTM", "US_REAL_GDP"]), sorted(ga["noncore_degraded"]) == sorted(["CN_SF_FLOW", "ECB_DFR", "ECB_MRO", "JTSJOL", "M2SL", "SPX_EPS", "SPX_PE_TTM", "US_REAL_GDP"]))
add("⑪", "G2-EAGDP-age", "series_store.EA_REAL_GDP_YOY 末观测距截止日天数 / 注册表 max_calendar_lag_days", [days(maxd["EA_REAL_GDP_YOY"], CUT), regm["EA_REAL_GDP_YOY"]["freshness"]["max_calendar_lag_days"], r(days(maxd["EA_REAL_GDP_YOY"], CUT) / regm["EA_REAL_GDP_YOY"]["freshness"]["max_calendar_lag_days"], 3)], [145, 120, 1.208], days(maxd["EA_REAL_GDP_YOY"], CUT) == 145 and regm["EA_REAL_GDP_YOY"]["freshness"]["max_calendar_lag_days"] == 120, "「145 天,超过 120 天;与 US_REAL_GDP 同龄同倍数」")
add("⑪", "G2b-EAGDP-has-stock", "series_store.EA_REAL_GDP_YOY 观测数", len(S("EA_REAL_GDP_YOY")), ">0(存量观测在库)", len(S("EA_REAL_GDP_YOY")) > 0, "列入非核心缺口清单但库内有存量观测——判断档已披露")
add("⑪", "G3-USGDP-age", "US_REAL_GDP 末观测距截止日天数 / 注册表上限 / 倍数", [days(maxd["US_REAL_GDP"], CUT), regm["US_REAL_GDP"]["freshness"]["max_calendar_lag_days"], r(days(maxd["US_REAL_GDP"], CUT) / regm["US_REAL_GDP"]["freshness"]["max_calendar_lag_days"], 3)], [145, 120, 1.208], days(maxd["US_REAL_GDP"], CUT) == 145 and regm["US_REAL_GDP"]["freshness"]["max_calendar_lag_days"] == 120, "「1.2 倍」")
add("⑪", "G4-CPCE-age", "CORE_PCE 末观测距截止日天数 / 注册表上限 / 倍数", [days(maxd["CORE_PCE"], CUT), regm["CORE_PCE"]["freshness"]["max_calendar_lag_days"], r(days(maxd["CORE_PCE"], CUT) / regm["CORE_PCE"]["freshness"]["max_calendar_lag_days"], 3)], [83, 60, 1.383], days(maxd["CORE_PCE"], CUT) == 83 and regm["CORE_PCE"]["freshness"]["max_calendar_lag_days"] == 60, "「83 天,为 60 天的 1.4 倍」")
dr = rep["run"]["data_requirements"]["items"]
nin = {it["metric_id"]: it["spec"]["window"]["n_in_window"] for it in dr}
add("⑪", "G5-task-window-empty", "report.run.data_requirements.items[*].spec.window.n_in_window", nin, "9 项均为 0", len(nin) == 9 and all(v == 0 for v in nin.values()))
add("⑪", "G5b-outcomes", "report.run.data_requirements.items[*].outcome", sorted(set(it["outcome"] for it in dr)), ["insufficient_coverage"], sorted(set(it["outcome"] for it in dr)) == ["insufficient_coverage"])
# evidence refs
refs = []
for c in aj["l3"]["contradictions"]:
    refs.append(("C", len(c["evidence_refs"]), c["evidence_refs"]))
nC = sum(x[1] for x in refs)
nM = sum(len(l["evidence_refs"]) for ch in aj["l3"]["mechanism_chains"] for l in ch["links"])
nS = sum(len(s["rows"]["asset_direction"]["evidence_refs"]) for s in aj["l4"]["scenarios"])
idx = set(e["ref"] if isinstance(e, dict) and "ref" in e else None for e in rep["evidence_index"])
allrefs = [r for _, _, rs in refs for r in rs] + [r for ch in aj["l3"]["mechanism_chains"] for l in ch["links"] for r in l["evidence_refs"]] + [r for s in aj["l4"]["scenarios"] for r in s["rows"]["asset_direction"]["evidence_refs"]]
add("⑪", "G6-ref-count", "agent_judgment.l3/l4 evidence_refs 计数", {"C": nC, "M": nM, "S": nS, "total": nC + nM + nS}, {"C": 10, "M": 4, "S": 5, "total": 19}, (nC, nM, nS) == (10, 4, 5))
add("⑪", "G6b-refs-resolve", "evidence_refs ∩ report.evidence_index", sorted(set(allrefs) - idx), "全部解析", all(r in idx for r in allrefs), "证据索引键样例: %s" % sorted(idx)[:2])
fc = rep["run"]["evidence_gate"]["counts"]
add("⑪", "G8-facts-count", "report.run.evidence_gate.counts", {k: fc[k] for k in ("facts_kept", "facts_rebuilt", "facts_dropped", "facts_excluded_version", "series_observations_dropped")}, {"facts_kept": 105, "facts_rebuilt": 0, "facts_dropped": 0, "facts_excluded_version": 0, "series_observations_dropped": 0}, fc["facts_kept"] == 105 and fc["facts_rebuilt"] == 0 and fc["facts_dropped"] == 0 and fc["series_observations_dropped"] == 0)
add("⑪", "G8b-facts-len", "snapshot.facts 长度", len(snap["facts"]), 105, len(snap["facts"]) == 105)
# STALE
cv = rep["agent_judgment"]["contract_verification"]["verdicts"]
stale = [(v["metric"], v["token"], v["status"], v["note"]) for v in cv if v["status"] != "VERIFIED"]
add("⑬", "H1-stale-items", "report.agent_judgment.contract_verification.verdicts status!=VERIFIED", stale, "CORE_PCE 与 US_REAL_GDP 两项 STALE", sorted(x[0] for x in stale) == ["CORE_PCE", "US_REAL_GDP"] and "STALE(CORE_PCE" in q.replace(" ", "") or sorted(x[0] for x in stale) == ["CORE_PCE", "US_REAL_GDP"])
stale_vals_equal = all(v["value"] == v["expected"] for v in cv if v["status"] == "STALE")
add("⑬", "H2-stale-values-equal", "contract_verification STALE 项 value==expected", stale_vals_equal, True, stale_vals_equal, "「数值一致、观测滞后超过注册表节奏」")
disc_ok = ("CORE_PCE" in q and "观测 2026-09-01" in q and "83 天" in q and "US_REAL_GDP" in q and "观测 2026-07-01" in q and "145 天" in q)
add("⑬", "H3-stale-disclosure", "agent_judgment.quality_gate_notes[3]", disc_ok, True, disc_ok, "STALE 指标/观测期/滞后天数披露")
cvv = rep["agent_judgment"]["contract_verification"]
add("⑬", "H4-contract-stats", "contract_verification.stats", cvv["stats"], {"checks": 9, "verified": 7, "contradicted": 0}, cvv["stats"]["checks"] == 9 and cvv["stats"]["verified"] == 7 and cvv["stats"]["contradicted"] == 0)

# ---------------- round-1 supplement (seat): faces probed after the first pass ----------------
import hashlib
add("⑪", "I1-evidence-index-rows", "report.evidence_index 长度", len(rep["evidence_index"]), 63, len(rep["evidence_index"]) == 63, "agent_declaration「证据索引(63行)」/FULL_REPORT「证据行: 63」")
add("②", "I2-point-cells", "report.research_plan.point_values.cells 长度", len(cells), 9, len(cells) == 9, "agent_declaration「点值格(9格)」")
add("④", "I3-maintain-no-effective", "release_calendar.entries[RC-JP-BOJ-MAINT-2026-10] 是否含 effective_on 键", "effective_on" in e2, False, "effective_on" not in e2, "「维持条目无生效日,正文不为其挂生效日」")
# anchor_echo (16 entries) vs engine grid
echo_ok = []
for reg_ in aj["reader_map"]["regions"]:
    for e in reg_["anchor_echo"]:
        a = grid[e["metric_id"]][e["anchor"]]
        echo_ok.append(e["value"] == a["value"] and e["observation_month"] == a["observation_date"][:7])
add("②", "I4-anchor-echo-vs-grid", "agent_judgment.reader_map.regions[*].anchor_echo vs report.research_plan.point_values.cells[*].anchors", "%d/%d" % (sum(echo_ok), len(echo_ok)), "18/18 值与观测月一致", all(echo_ok) and len(echo_ok) == 18)
# USDJPY 12-month position
_u = [(d, v) for d, v in S("USDJPY") if v is not None and "2025-11-23" <= d <= CUT]
_ul = _u[-1]
_pr = sum(1 for d, v in _u if v <= _ul[1]) / float(len(_u)) * 100.0
add("⑦", "I5-USDJPY-12m-position", "USDJPY [2025-11-23..2026-11-23] 末值/窗内最小/最大/末值分位", {"last": _ul, "min": r(min(v for d, v in _u), 3), "max": r(max(v for d, v in _u), 3), "pct_rank": r(_pr, 1), "n": len(_u), "m1_pct": r(pct("USDJPY", "2026-10-23", CUT)[0], 2), "m3_pct": r(pct("USDJPY", "2026-08-19", CUT)[0], 2)},
    {"last": "2026-11-23=159.347", "min": 152.453, "max": 163.864, "pct_rank": 71.0, "n": 259, "m1_pct": 1.82, "m3_pct": -0.13},
    _ul == ("2026-11-23", 159.347) and abs(min(v for d, v in _u) - 152.453) < 5e-4 and abs(max(v for d, v in _u) - 163.864) < 5e-4 and abs(_pr - 71.0) < 0.05 and len(_u) == 259,
    "「USDJPY 仍处高位」: 12 个月窗内约 71% 分位(窗内最大 163.864),近一月 +1.82%、三个月 -0.13%")
# BEI earlier up-leg endpoints
_b = [(d, v) for d, v in S("BEI_10Y") if "2026-02-20" <= d <= "2026-05-04" and v is not None]
_bmax = max(_b, key=lambda t: t[1]); _bmin = min(_b, key=lambda t: t[1])
add("§4", "I6-BEI-earlier-leg-endpoints", "BEI_10Y [2026-02-20..2026-05-04] 窗内最小/最大;月末对照 2026-02-27→2026-05-29", {"window_min": _bmin, "window_max": _bmax, "month_end_05-29": val("BEI_10Y", "2026-05-29"), "me_to_me_bp": r((val("BEI_10Y", "2026-05-29") - val("BEI_10Y", "2026-02-27")) * 100, 0)},
    {"window_min": "2026-02-27=2.25", "window_max": "2026-05-04=2.5", "month_end_05-29": 2.38, "me_to_me_bp": 13},
    _bmin == ("2026-02-27", 2.25) and _bmax == ("2026-05-04", 2.5) and val("BEI_10Y", "2026-05-29") == 2.38,
    "判断档两端点=该窗最小值→最大值(05-04 亦为 2026 年内最高);月末对月末仅 +13bp——端点未注明「段内峰值」(见 MINOR)")
# scenario thresholds vs cutoff readings / release schedule
def rel_date(ym, lagd):
    return (datetime.date(*[int(x) for x in month_end(ym).split("-")]) + datetime.timedelta(days=lagd)).isoformat()
_hicp_rel = {ym: rel_date(ym, 16) for ym in ("2026-09", "2026-10", "2026-11", "2026-12", "2027-01")}
_ea09, _ea10 = monthly("EA_HICP_YOY", "2026-09"), monthly("EA_HICP_YOY", "2026-10")
_cp09 = yy("CORE_PCE", "2026-09")
_tips, _bei = val("TIPS_10Y", "2026-11-19"), val("BEI_10Y", "2026-11-20")
add("⑨", "J0-hicp-release-schedule", "EA_HICP_YOY 观测月→规则发布日(月末+16,引擎同规则)", _hicp_rel, {"2026-10": "2026-11-16", "2026-11": "2026-12-16", "2026-12": "2027-01-16", "2027-01": "2027-02-16"}, _hicp_rel == {"2026-09": "2026-10-16", "2026-10": "2026-11-16", "2026-11": "2026-12-16", "2026-12": "2027-01-16", "2027-01": "2027-02-16"})
add("⑨", "J1-S1-trigger-not-met", "截止日读数: EA_HICP_YOY@2026-10 / CORE_PCE 同比@2026-09 / TIPS_10Y@2026-11-19", {"EA": _ea10, "CORE_PCE_yoy": r(_cp09, 2), "TIPS": _tips}, {"EA": "<4.2", "CORE_PCE_yoy": "<3.2", "TIPS": "<3.0"}, _ea10 < 4.2 and _cp09 < 3.2 and _tips < 3.0, "S1 触发条件在截止日尚未到达=待验证情景")
add("⑨", "J2-S1-state-holds-at-cutoff", "同上三项读数 vs S1 情景状态(维持 3.5% 以上 / 3.0% 以上)", {"EA": _ea10, "CORE_PCE_yoy": r(_cp09, 2)}, {"EA": ">=3.5", "CORE_PCE_yoy": ">=3.0"}, _ea10 >= 3.5 and _cp09 >= 3.0, "S1 前提与截止日读数相容(未被证伪)")
add("⑨", "J3-S2-trigger-not-met", "截止日读数: EA_HICP_YOY 2026-09→2026-10 / BEI_10Y@2026-11-20", {"EA_09": _ea09, "EA_10": _ea10, "BEI": _bei}, {"EA": "未连续回落", "BEI": ">2.0"}, _ea10 >= _ea09 and _bei > 2.0, "S2 触发条件尚未到达")
add("⑨", "J4-S2-falsifier-reachable", "S2 证伪: 2026-12 与 2027-01 两月发布=2026-11/2026-12 观测月(%s/%s),期限 2027-02-15" % (_hicp_rel["2026-11"], _hicp_rel["2026-12"]), {"releases": [_hicp_rel["2026-11"], _hicp_rel["2026-12"]], "<=deadline": max(_hicp_rel["2026-11"], _hicp_rel["2026-12"]) <= "2027-02-15"}, "两次发布均在期限内=可观测可触发", max(_hicp_rel["2026-11"], _hicp_rel["2026-12"]) <= "2027-02-15")
# S1 falsifier as worded: 「2027-01 前发布…连续两个月低于 3.0%」
_pre2701 = [ym for ym in sorted(_hicp_rel) if _hicp_rel[ym] < "2027-01-01"]
_pairs = [(_pre2701[i], _pre2701[i + 1]) for i in range(len(_pre2701) - 1)]
_pair_vals = [(a, monthly("EA_HICP_YOY", a), b, monthly("EA_HICP_YOY", b)) for a, b in _pairs]
_s1_reach = any(a_v is not None and b_v is not None and a_v < 3.0 and b_v < 3.0 for a, a_v, b, b_v in _pair_vals)
add("⑨", "J5-S1-falsifier-reachable", "S1 证伪字面「2027-01 前发布…连续两个月低于 3.0%」直算",
    {"obs_months_released_before_2027-01": _pre2701, "release_dates": [_hicp_rel[y] for y in _pre2701], "consecutive_pairs(obs_month,reading)": _pair_vals, "reachable": _s1_reach},
    "证伪条件可观测且与截止日读数相容(可触发)",
    _s1_reach,
    "偏离: 截止日后、2027-01 前只剩 2026-11 观测月一次发布(2026-12-16);可与它相邻的 2026-10 读数=4.0 已于 2026-11-16 发布→「连续两个月低于 3.0%」在 2027-01 前不可能成立,S1 证伪条件按字面不可触发(见 MAJOR-1)")
add("⑨", "J6-scenarios-complementary", "S1 状态(维持 3.5% 以上/3.0% 以上) vs S2 状态(回落至 3.0% 以下/2.8% 以下)", "S1=延续上行, S2=回落;资产方向 S1=利率上/风险资产弱/美元强, S2=通胀补偿与实际利率回落/风险资产与黄金修复/美元弱", "方向互补", True, "两情景方向互补非孤证;S1 证伪阈(<3.0)与 S2 证伪阈(>=4.0)互补")
add("⑨", "J7-trigger-release-window", "S1 触发「2026-12 或 2027-01 发布」对应发布日", [_hicp_rel["2026-11"], _hicp_rel["2026-12"]], "均 <= 2027-02-15", max(_hicp_rel["2026-11"], _hicp_rel["2026-12"]) <= "2027-02-15", "2027-01 观测月发布日 %s 晚于期限→「至 2027-01」只能指发布月(2026-11/2026-12 观测月)" % _hicp_rel["2027-01"])
# plan metrics vs policy-rate series in the frozen store
_POL = ("DFEDTARU", "DFEDTARL", "DFF", "FED_FUNDS", "ECB_DFR", "ECB_MRO")
add("⑭", "K1-plan-has-no-US-EA-policy-rate", "report.run.data_requirements.items[*].metric_id", sorted(nin), "不含美欧政策利率序列", not any(m in _POL for m in nin) and len(nin) == 9, "「本问计划指标面未纳入美欧政策利率序列」属实")
def _steps(mid, lo, hi):
    """变更点=窗内观测对其『全序列前一观测』的变动(前值可在窗启前一格,与引擎政策窗口径同)。"""
    _s = [(d, v) for d, v in S(mid) if v is not None]
    return [(_s[i][0], _s[i - 1][1], _s[i][1]) for i in range(1, len(_s)) if lo <= _s[i][0] <= hi and abs(_s[i][1] - _s[i - 1][1]) > 1e-9]
_pol_steps = {m: _steps(m, "2026-08-19", CUT) for m in _POL}
add("⑭", "K2-store-has-US-EA-policy-rates", "series_store DFEDTARU/DFEDTARL/ECB_DFR/ECB_MRO/FED_FUNDS [2026-08-19..2026-11-23] 变更点", _pol_steps, "判断档未引用(称「依本问证据不可判」)",
    _pol_steps["DFEDTARU"] == [("2026-09-17", 3.75, 4.0)] and _pol_steps["ECB_DFR"] == [("2026-09-16", 2.25, 2.5)],
    "快照在库但不在本问计划指标面/证据索引: 美联储目标区间上限 2026-09-17 起 3.75→4.00(+25bp),欧央行存款便利利率 2026-09-16 起 2.25→2.50(+25bp)——与日本央行 2026-09-18 决议同月收紧;计划面/证据索引确未纳入(披露口径见 MINOR)")
add("⑭", "K3-JGB-registered-not-collected", "metric_registry JGB2Y/5Y/10Y 在册; series_store 是否在库", {"registered": all(m in regm for m in ("JGB2Y", "JGB5Y", "JGB10Y")), "in_store": [m for m in ("JGB2Y", "JGB5Y", "JGB10Y") if m in snap["series_store"]]}, {"registered": True, "in_store": []}, all(m in regm for m in ("JGB2Y", "JGB5Y", "JGB10Y")) and not any(m in snap["series_store"] for m in ("JGB2Y", "JGB5Y", "JGB10Y")), "「本引擎无日本融资成本/套息持仓序列」: 套息持仓序列确无;JGB 收益率在册但本轮未采,JP_POLICY_RATE 本身即隔夜资金利率月均(措辞见 NIT)")
# in-face context not cited by the judgment
add("§4", "K4-UMCSENT-anchor-window", "UMCSENT @2026-07-01 / @2026-10-01", [monthly("UMCSENT", "2026-07"), monthly("UMCSENT", "2026-10")], [55.2, 48.0], monthly("UMCSENT", "2026-07") == 55.2 and monthly("UMCSENT", "2026-10") == 48.0, "判断档未引用的软数据(不在本问计划指标面与证据索引,仅快照在库): 锚窗内回落 7.2 点(见六查 C2)")
add("§4", "K5-EURUSD-3m", "EURUSD 2026-11-23 / 2026-08-19", r(pct("EURUSD", "2026-08-19", CUT)[0], 2), -5.52, eq_num(pct("EURUSD", "2026-08-19", CUT)[0], -5.52, 2), "「弱欧元放大输入压力」前提: 三个月 -5.52%、近一月 -2.51%,同向")
add("§4", "K6-BRENT-windows", "BRENT_F 近一月/三个月/12 个月", [r(pct("BRENT_F", "2026-10-23", CUT)[0], 2), r(pct("BRENT_F", "2026-08-19", CUT)[0], 2), r(pct("BRENT_F", "2025-11-19", CUT)[0], 2)], [-24.44, -3.74, 38.86], eq_num(pct("BRENT_F", "2026-10-23", CUT)[0], -24.44, 2) and eq_num(pct("BRENT_F", "2026-08-19", CUT)[0], -3.74, 2) and eq_num(pct("BRENT_F", "2025-11-19", CUT)[0], 38.86, 2), "能源前提的在场对照: 近一月 -24.44%,判断档未引用(见六查 C1)")
for mid, a, b, rep_pct, rep_from, rep_to in [("SHCOMP", "2026-10-23", "2026-11-23", -4.11, 3690.48, 3538.95), ("DAX", "2026-10-23", "2026-11-23", 0.11, 25181.7, 25209.4)]:
    c, va, vb = pct(mid, a, b)
    add("⑩", "K7-MAP-asset-row-" + mid, "%s %s→%s (%r→%r)" % (mid, a, b, va, vb), [r(c, 4), va, vb], [rep_pct, rep_from, rep_to], eq_num(c, rep_pct, 2) and eq_num(va, rep_from, 1) and eq_num(vb, rep_to, 1), "MAP 资产月窗表引擎行(判断档未引用)")
# analog face / zero-case
_st = [s for s in rep["steps"] if s.get("step") == "S6_analog"][0]
_top = _st["envelope"]["data"]["top"]
add("⑧", "L1-analog-top-face", "report.steps[S6_analog].envelope.data.top", [(t["rank"], t["candidate_month"], t["distance"]) for t in _top], "FULL_REPORT「历史相似结构」5 段", [(t["rank"], t["candidate_month"], t["distance"]) for t in _top] == [(1, "2025-03", 0.727212), (2, "2022-06", 0.791806), (3, "2023-10", 1.054168), (4, "2021-02", 1.284945), (5, "2020-01", 1.357685)], "引擎候选面 5 段(候选月全窗数据事后筛得)")
add("⑧", "L2-history-zero-case", "agent_judgment.reader_map.history_periods / history_zero_case_note; report.agent_judgment.reader_map_faces.history_n", {"history_periods": aj["reader_map"]["history_periods"], "history_n": rep["agent_judgment"]["reader_map_faces"]["history_n"], "note_len": len(aj["reader_map"]["history_zero_case_note"])}, {"history_periods": [], "history_n": 0, "note": "在场"}, aj["reader_map"]["history_periods"] == [] and rep["agent_judgment"]["reader_map_faces"]["history_n"] == 0 and len(aj["reader_map"]["history_zero_case_note"]) > 40, "零段类比: 引擎候选 5 段在场,判断档未采纳任何段、未引任何候选数字(无可复算数字);事后结果≠当时可知的表述与引擎注记一致")
# intraday labelling for cutoff-day observations
_ajtxt = json.dumps(aj, ensure_ascii=False)
add("⑫", "M1-intraday-label", "agent_judgment 全文「盘中快照」出现次数 / 报告内 2026-11-23 日频值(SPX/VIX/GOLD_F/DXY/USDJPY)", {"n_label": _ajtxt.count("盘中快照"), "as_of": asof}, {"n_label": ">=4", "as_of": "2026-11-23T22:53:47+08:00"}, _ajtxt.count("盘中快照") >= 4 and asof == "2026-11-23T22:53:47+08:00", "截止日当日值均带「盘中快照、非收盘价」说明;与 research_as_of(纽约 09:53)相容")
# optional: reader report rendering + sha anchor
if len(sys.argv) > 8:
    MAP, SHAF = sys.argv[7], sys.argv[8]
    _sha = hashlib.sha256(open(MAP, "rb").read()).hexdigest()
    _shaf = open(SHAF, encoding="utf-8").read().split()[0]
    add("①", "M2-map-sha-anchor", "MAP_REPORT.sha256 vs sha256(MAP_REPORT.md)", [_sha[:16], _shaf[:16]], "相等", _sha == _shaf)
    _txt = open(MAP, encoding="utf-8").read()
    _vn = [l["verdict_note"][:24] for ch in aj["reader_map"]["transmission"] for l in ch["links"]]
    _nr = [t["narrative"][:24] for t in aj["reader_map"]["turnings"]]
    add("⑩", "M3-unrendered-fields", "MAP_REPORT.md 是否含 verdict_note / narrative 专有句", {"verdict_note": [v in _txt for v in _vn], "narrative": [v in _txt for v in _nr]}, "均不进渲染(与 quality_gate_notes 一致)", not any(v in _txt for v in _vn + _nr))
    _parts = [aj["reader_map"]["headline_conclusion"]] + [rg["from_to"] for rg in aj["reader_map"]["regions"]] + [l["observed_fact"] for ch in aj["reader_map"]["transmission"] for l in ch["links"]] + [t["first_mover"] for t in aj["reader_map"]["turnings"]] + [t["follow_or_diverge"] for t in aj["reader_map"]["turnings"]] + [s["rows"]["falsification"]["threshold"] for s in aj["l4"]["scenarios"]] + [s["rows"]["trigger"]["condition"] for s in aj["l4"]["scenarios"]]
    add("⑩", "M4-reader-map-verbatim", "MAP_REPORT.md 含判断档 headline/走位/传导/转折/情景证伪与触发原文", "%d/%d" % (sum(p in _txt for p in _parts), len(_parts)), "全部逐字渲染", all(p in _txt for p in _parts), "读者报告判断文字=判断档原文(含 S1 证伪句)")
    add("⑫", "M5-map-cutoff-header", "MAP_REPORT.md 研究截止日行", "2026-11-23" in _txt.split("\n")[3], True, "2026-11-23" in _txt.split("\n")[3])

# ---------------- output ----------------
n = len(POINTS)
mis = [p for p in POINTS if not p["match"]]
for p in POINTS:
    p["computed"] = json.loads(json.dumps(p["computed"], ensure_ascii=False, default=str))
    p["reported"] = json.loads(json.dumps(p["reported"], ensure_ascii=False, default=str))
json.dump({"recompute_points": n, "recompute_mismatches": len(mis), "points": POINTS}, open(OUT + "/recompute_points.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
with open(OUT + "/recompute_points.txt", "w", encoding="utf-8") as fh:
    for p in POINTS:
        fh.write("[%s] %s | %s\n    直算=%s\n    报告=%s | %s %s\n" % (p["cat"], p["id"], p["source"], json.dumps(p["computed"], ensure_ascii=False), json.dumps(p["reported"], ensure_ascii=False), "一致" if p["match"] else "!!偏离!!", ("| " + p["note"]) if p["note"] else ""))
print("recompute_points=%d mismatches=%d" % (n, len(mis)))
for p in mis:
    print("MISMATCH", p["id"], json.dumps(p["computed"], ensure_ascii=False), "vs", json.dumps(p["reported"], ensure_ascii=False))
