#!/usr/bin/env python3
"""Seat-owned read-only recompute table for T3 Round-1 independent semantic review.

Usage:
  python3 -I recompute.py <snapshot.json> <release_calendar.json> <metric_registry.json> \
            <report.json> <agent_judgment.json> <out_dir>

Every point is computed independently from the frozen snapshot series_store / frozen
calendar / registry / report.json engine faces, then compared with the value or claim as
written in the report / judgment (transcribed verbatim into REPORTED below, with location).
Outputs (in <out_dir>): recompute_table.tsv, recompute_table.md, recompute_summary.json
Status: OK = 一致; DEV = 偏离(数值/日期/方向/口径/披露); UNVER = 证据面不可核/无出处.
Kind:  numeric / date / direction / caliber / disclosure / unsourced / claim
"""
import csv
import datetime as dt
import json
import os
import sys

ARGS = sys.argv[1:]
SNAP_P, CAL_P, REG_P, REP_P, AJ_P, OUT = ARGS
with open(SNAP_P, "r", encoding="utf-8") as fh:
    SNAP = json.load(fh)
with open(CAL_P, "r", encoding="utf-8") as fh:
    CAL = json.load(fh)
with open(REG_P, "r", encoding="utf-8") as fh:
    REG = json.load(fh)
with open(REP_P, "r", encoding="utf-8") as fh:
    REP = json.load(fh)
with open(AJ_P, "r", encoding="utf-8") as fh:
    AJ = json.load(fh)

STORE = SNAP["series_store"]
CUTOFF = REP["research_plan"]["cutoff"]
POINTS = []


def ser(sid):
    s = STORE[sid]
    return list(zip(s["dates"], s["values"]))


def at(sid, date):
    """last observation with date <= date (non-null value)."""
    pts = [(d, v) for d, v in ser(sid) if d <= date and v is not None]
    return pts[-1] if pts else None


def val(sid, date):
    for d, v in ser(sid):
        if d == date:
            return v
    return None


def ym(sid, y, m):
    return val(sid, "%04d-%02d-01" % (y, m))


def month_end_plus(period_end, days):
    d = dt.date.fromisoformat(period_end) + dt.timedelta(days=days)
    return d.isoformat()


def shift_months(date_s, months):
    d = dt.date.fromisoformat(date_s)
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    return "%04d-%02d-%02d" % (y, m, d.day)


def r(x, n=2):
    return round(x + 0.0, n)


def pct(sid, d0, d1):
    a = at(sid, d0)
    b = at(sid, d1)
    return a, b, (b[1] / a[1] - 1.0) * 100.0


def add(cat, src, computed, reported, status, kind, note):
    POINTS.append({
        "id": "P%02d" % (len(POINTS) + 1),
        "cat": cat,
        "source": src,
        "computed": computed,
        "reported": reported,
        "status": status,
        "kind": kind,
        "note": note,
    })


def num_eq(a, b, tol=0.0051):
    return abs(a - b) <= tol


# ---------------------------------------------------------------- ① 截止日
asof_date = SNAP["research_as_of"][:10]
add("①", "snapshot.research_as_of / target_date; report.json research_plan.cutoff",
    "research_as_of=%s; target_date=%s" % (SNAP["research_as_of"], SNAP["target_date"]),
    "研究截止日=2026-11-23(报告 L5 / 判断档口径披露)", "OK" if (asof_date == CUTOFF == "2026-11-23") else "DEV",
    "date", "截止日与快照版本日一致" if asof_date == CUTOFF else "不一致")

cited = ["EA_HICP_YOY", "JP_CPI_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_RATE", "ECB_MRO", "ECB_DFR",
         "EURUSD", "USDJPY", "VIX", "DAX", "SPX", "NIKKEI225", "SHCOMP", "DXY", "GOLD_F", "UST_10Y",
         "TIPS_10Y", "BEI_10Y"]
last_obs = {sid: at(sid, CUTOFF) for sid in cited}
mx = max(v[0] for v in last_obs.values())
add("①", "series_store[*].dates (max date <= cutoff, 18 cited series)",
    "max last obs date=%s; 越界条数=%d" % (mx, sum(1 for d, _ in ser("EA_HICP_YOY") if d > CUTOFF)),
    "报告引用的最新观测日 2026-11-23(EURUSD/USDJPY/VIX/DAX)", "OK" if mx <= CUTOFF else "DEV",
    "date", "被引序列全部观测日 ≤ 截止日")

cells = {c["metric_id"]: c for c in REP["research_plan"]["point_values"]["cells"]}
pubs = []
for mid, c in cells.items():
    for k, a in c["anchors"].items():
        if a.get("publication_date"):
            pubs.append((a["publication_date"], mid, k))
mpub = max(pubs)
add("①", "report.json research_plan.point_values.cells[*].anchors.*.publication_date (max)",
    "max publication_date=%s (%s %s)" % mpub, "报告最晚公布日 2026-11-20(JP_CPI_YOY 最新一期)",
    "OK" if mpub[0] <= CUTOFF else "DEV", "date", "公布日均不晚于截止日")

w0 = REP["research_plan"]["question_window"]["windows"][0]
add("①", "cutoff − 6 个月(直算); report.json research_plan.question_window.windows[0]",
    "2026-11-23 − 6 月 = %s..%s" % (shift_months(CUTOFF, -6), CUTOFF),
    "最近六个月(2026-05-23..2026-11-23)(C2 陈述)", "OK" if w0["from"] == "2026-05-23" else "DEV",
    "date", "六个月窗起点=截止日−6月")

# ---------------------------------------------------------------- ② 点值锚格
anchors = {"6个月前": "2026-05-23", "最新一期": "2026-11-23"}
judg_txt = {
    ("EA_HICP_YOY", "6个月前"): "HICP 同比由6个月前锚(观测月 2026-04)的 3.0%",
    ("EA_HICP_YOY", "最新一期"): "升至最新一期锚(观测月 2026-10)的 4.0%",
    ("ECB_MRO", "6个月前"): "主要再融资利率…由6个月前锚(观测月 2025-06)的 2.15%",
    ("ECB_MRO", "最新一期"): "升至最新一期锚(观测月 2026-09)的 2.65%",
    ("ECB_DFR", "6个月前"): "存款便利利率(操作下限口径)由 2.0%",
    ("ECB_DFR", "最新一期"): "升至 2.5%",
    ("JP_CPI_YOY", "6个月前"): "全国 CPI 同比由6个月前锚(观测月 2026-04)的 1.38%",
    ("JP_CPI_YOY", "最新一期"): "升至最新一期锚(观测月 2026-10)的 2.44%",
    ("JP_CPI_TOKYO_YOY", "6个月前"): "东京都 CPI…由6个月前锚观测月 2026-04 的 1.42%",
    ("JP_CPI_TOKYO_YOY", "最新一期"): "升至最新一期锚观测月 2026-10 的 2.73%",
    ("JP_POLICY_RATE", "6个月前"): "月均由6个月前锚(观测月 2026-04)的 0.727%",
    ("JP_POLICY_RATE", "最新一期"): "台阶升至最新一期锚(观测月 2026-10)的 1.227%",
}
rep_vals = {
    ("EA_HICP_YOY", "6个月前"): ("2026-04-01", 3.0), ("EA_HICP_YOY", "最新一期"): ("2026-10-01", 4.0),
    ("ECB_MRO", "6个月前"): ("2025-06-11", 2.15), ("ECB_MRO", "最新一期"): ("2026-09-16", 2.65),
    ("ECB_DFR", "6个月前"): ("2025-06-11", 2.0), ("ECB_DFR", "最新一期"): ("2026-09-16", 2.5),
    ("JP_CPI_YOY", "6个月前"): ("2026-04-01", 1.38), ("JP_CPI_YOY", "最新一期"): ("2026-10-01", 2.44),
    ("JP_CPI_TOKYO_YOY", "6个月前"): ("2026-04-01", 1.42), ("JP_CPI_TOKYO_YOY", "最新一期"): ("2026-10-01", 2.73),
    ("JP_POLICY_RATE", "6个月前"): ("2026-04-01", 0.727), ("JP_POLICY_RATE", "最新一期"): ("2026-10-01", 1.227),
}
LAG = {"EA_HICP_YOY": 16, "JP_CPI_YOY": 20, "JP_CPI_TOKYO_YOY": -1, "JP_POLICY_RATE": 5}


def pub_date(sid, obs_date):
    """推定公布日 = 观测月月末 + 滞后天(规则见 report.json point_values publication_rule)。"""
    y, m = int(obs_date[:4]), int(obs_date[5:7])
    last = dt.date(y + (1 if m == 12 else 0), (m % 12) + 1, 1) - dt.timedelta(days=1)
    return (last + dt.timedelta(days=LAG[sid])).isoformat()


def anchor(sid, as_of):
    """发布纪律锚: 取『公布日 <= 锚日』的最新观测(月频按推定公布日;日频政策序列公布日=观测日)。
    返回 (pub_date, obs_date, value)。"""
    if sid in LAG:
        pts = [(pub_date(sid, d), d, v) for d, v in ser(sid) if v is not None]
        pts = [p for p in pts if p[0] <= as_of]
        return pts[-1] if pts else None
    got = at(sid, as_of)
    return (got[0], got[0], got[1]) if got else None


for mid in ["EA_HICP_YOY", "ECB_MRO", "ECB_DFR", "JP_CPI_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_RATE"]:
    for lab, as_of in anchors.items():
        got = anchor(mid, as_of)
        naive = at(mid, as_of)
        exp_d, exp_v = rep_vals[(mid, lab)]
        ok = got is not None and got[1] == exp_d and num_eq(got[2], exp_v, 0.00051)
        note = "锚格值/观测日直算一致(公布日 %s ≤ 锚日 %s)" % (got[0], as_of) if ok else "偏离"
        if lab == "6个月前" and mid in LAG and naive[0] != exp_d:
            note += ";若不按发布纪律取≤锚日最新观测得 %s=%s(公布 %s>锚日,不可见)——报告未用未发布值" % (
                naive[0][:7], naive[1], pub_date(mid, naive[0]))
        add("②", "series_store.%s 发布纪律锚(公布日<=%s)" % (mid, as_of),
            "%s = %s (公布 %s)" % (got[1], got[2], got[0]) if got else "ABSENT",
            "%s = %s (%s; 判断档走位+关键数字表)" % (exp_d, exp_v, judg_txt[(mid, lab)]),
            "OK" if ok else "DEV", "numeric", note)

# ---------------------------------------------------------------- ③ 同比基期
jp_base = ym("JP_CPI_YOY", 2025, 10)
ea_base = ym("EA_HICP_YOY", 2025, 10)
add("③", "series_store.JP_CPI_YOY @2025-10-01", str(jp_base), "去年同月(2025-10)为百分之二点九九(C1)",
    "OK" if num_eq(jp_base, 2.99) else "DEV", "numeric", "基期观测在场")
add("③", "series_store.EA_HICP_YOY @2025-10-01", str(ea_base), "去年同月(2025-10)为百分之二点一(C1)",
    "OK" if num_eq(ea_base, 2.1) else "DEV", "numeric", "基期观测在场")
add("③", "JP_CPI_YOY 2026-10 − 2025-10", "%.2f" % (ym("JP_CPI_YOY", 2026, 10) - jp_base),
    "回落约零点五五个百分点 / 低 0.55 个百分点(C1 / 日本走位)", "OK" if num_eq(ym("JP_CPI_YOY", 2026, 10) - jp_base, -0.55) else "DEV",
    "numeric", "同比之差(百分点)")
add("③", "EA_HICP_YOY 2026-10 − 2025-10", "%.2f" % (ym("EA_HICP_YOY", 2026, 10) - ea_base),
    "抬升一点九个百分点 / 高 1.9 个百分点(C1 / 欧元区走位)", "OK" if num_eq(ym("EA_HICP_YOY", 2026, 10) - ea_base, 1.9) else "DEV",
    "numeric", "同比之差(百分点)")
tk_base = at("JP_CPI_TOKYO_YOY", "2025-10-01")
add("③", "series_store.JP_CPI_TOKYO_YOY 首观测 / @<=2025-10-01", "首观测=%s; 2025-10 基期=%s" % (ser("JP_CPI_TOKYO_YOY")[0][0], tk_base),
    "序列自 2026-01 起,去年同月基期观测不可得、同比对照不可判(C1)", "OK" if tk_base is None else "DEV",
    "claim", "缺基期如实声明、未以相邻月替代")
add("③", "JP 2.44<2.99 且 EA 4.0>2.1", "JP ↓ / EA ↑", "「日本回落、欧元区抬升」(C1)",
    "OK" if (ym("JP_CPI_YOY", 2026, 10) < jp_base and ym("EA_HICP_YOY", 2026, 10) > ea_base) else "DEV", "direction", "方向词与数值一致")

# ---------------------------------------------------------------- ④ 政策面
entries = {e["entry_id"]: e for e in CAL["entries"]}
boj = entries["RC-JP-BOJ-TARGET-2026-09"]
boj_m = entries["RC-JP-BOJ-MAINT-2026-10"]
add("④", "release_calendar.entries[RC-JP-BOJ-TARGET-2026-09].decision_date", boj["decision_date"],
    "2026-09-18 决议(标题 / C2 / 日本走位)", "OK" if boj["decision_date"] == "2026-09-18" else "DEV", "date", "日历实录")
add("④", "release_calendar.entries[RC-JP-BOJ-TARGET-2026-09].effective_on", boj["effective_on"],
    "2026-09-24 生效(标题 / C2)", "OK" if boj["effective_on"] == "2026-09-24" else "DEV", "date", "日历实录")
add("④", "release_calendar.entries[RC-JP-BOJ-TARGET-2026-09 / RC-JP-BOJ-MAINT-2026-10].target_value",
    "%s / %s(维持, decision_date=%s)" % (boj["target_value"], boj_m["target_value"], boj_m["decision_date"]),
    "政策目标约 1.25%;2026-10-30 会议确认维持约 1.25% 不变", "OK" if (boj["target_value"] == 1.25 and boj_m["target_value"] == 1.25 and boj_m["decision_date"] == "2026-10-30") else "DEV",
    "numeric", "日历实录")
d_eff = (dt.date.fromisoformat(CUTOFF) - dt.date.fromisoformat(boj["effective_on"])).days
d_dec = (dt.date.fromisoformat(CUTOFF) - dt.date.fromisoformat(boj["decision_date"])).days
d_mnt = (dt.date.fromisoformat(CUTOFF) - dt.date.fromisoformat(boj_m["decision_date"])).days
add("④", "cutoff − effective_on(BOJ)", str(d_eff), "距上次调整 60天(MAP 政策官方记录面)", "OK" if d_eff == 60 else "DEV", "numeric", "按生效日")
add("④", "cutoff − decision_date(BOJ)", str(d_dec), "距决议 66天(MAP 政策官方记录面)", "OK" if d_dec == 66 else "DEV", "numeric", "")
add("④", "cutoff − 2026-10-30(BOJ 维持)", str(d_mnt), "距维持 24天(MAP 政策官方记录面)", "OK" if d_mnt == 24 else "DEV", "numeric", "")
pending = [e for e in CAL["entries"] if e.get("kind") == "policy_decision" and e.get("effective_on") and e["effective_on"] > CUTOFF]
add("④", "release_calendar.entries[*] (kind=policy_decision 且 effective_on > cutoff)", "条数=%d" % len(pending),
    "待生效 —;引擎记录面无任何已决议而尚未生效的调整(C2)", "OK" if not pending else "DEV", "claim", "待生效与现行有效分记")


def changes(sid):
    pts = [(d, v) for d, v in ser(sid) if v is not None]
    out = []
    prev = pts[0]
    for d, v in pts[1:]:
        if v != prev[1]:
            out.append((d, prev[1], v, round((v - prev[1]) * 100, 3)))
        prev = (d, v)
    return out


for sid, rep_val in (("ECB_MRO", 2.65), ("ECB_DFR", 2.5)):
    ch = changes(sid)
    last = ch[-1]
    wd = dt.date.fromisoformat(last[0]).strftime("%a")
    add("④", "series_store.%s 末次变更点" % sid, "%s(%s) %s→%s" % (last[0], wd, last[1], last[2]),
        "最新生效水平 %s,观测=生效日 2026-09-16(C2)" % rep_val,
        "OK" if (last[0] == "2026-09-16" and num_eq(last[2], rep_val)) else "DEV", "date", "序列变更日=生效日")
    inwin = [c for c in ch if "2026-05-23" <= c[0] <= CUTOFF]
    add("④", "series_store.%s 变更点 ∈ [2026-05-23, 2026-11-23]" % sid,
        "; ".join("%s %s→%s(%+dbp)" % (c[0], c[1], c[2], round(c[3])) for c in inwin),
        "最近六个月两次同幅上调(2026-06-17、2026-09-16 生效),各 +25bp", "OK" if [c[0] for c in inwin] == ["2026-06-17", "2026-09-16"] else "DEV",
        "numeric", "窗内变更点与幅度")
d_ecb = (dt.date.fromisoformat(CUTOFF) - dt.date(2026, 9, 16)).days
add("④", "cutoff − 2026-09-16(ECB 生效)", str(d_ecb), "2026-09-16(距研究截止68天)(MAP 四分面)", "OK" if d_ecb == 68 else "DEV", "numeric", "")

ecb_cal = [e for e in CAL["entries"] if str(e.get("metric_id", "")).startswith("ECB")]
reg_mro = [m for m in REG["metrics"] if m["metric_id"] == "ECB_MRO"][0]
add("④", "release_calendar.entries[*] (metric_id 以 ECB 开头) / series_store.ECB_MRO 变更日 / metric_registry[ECB_MRO].release_semantics",
    "ECB 日历条目=%d; 序列变更日=2026-09-16; 注册表: %s" % (len(ecb_cal), reg_mro["release_semantics"][:34]),
    "决议日 2026-09-10(标题 / C2 / M1 step2 / 走位,事实位无推断标注);6个月前锚行决议 2025-06-05(MAP 四分面)", "UNVER", "date",
    "两处决议日均无日历实录可核;序列变更日 09-16≠09-10;注册表记『决议公布后生效并当日更新系列』(决议日=生效日);仅引擎 prev_thursday 惯例回推(算术自洽: 09-16−6天=09-10 周四, 06-17−6天=06-11, 2025-06-11−6天=2025-06-05)")
add("④", "release_calendar.updated", str(CAL.get("updated")), "发布日历最新实录·2026-11-21 更新(C2)", "OK" if CAL.get("updated") == "2026-11-21" else "DEV", "date", "")
for sid in ("ECB_MRO", "ECB_DFR"):
    nonwed = [(d, v) for d, v in ser(sid) if dt.date.fromisoformat(d).strftime("%a") != "Wed"]
    last_nonwed = nonwed[-1][0] if nonwed else None
    add("④", "series_store.%s 观测日星期分布" % sid, "非周三观测 %d/%d 条,最晚 %s; 其后全为周三" % (len(nonwed), len(ser(sid)), last_nonwed),
        "ECB_MRO/ECB_DFR 观测日全为周三=生效日(MAP L66 注)", "DEV", "claim", "『全为周三』对 1999–2008 年观测不成立(行文过宽,不影响近期变更点)")
add("④", "report.json point_values[ECB_MRO/ECB_DFR].anchors[最新一期].publication_date",
    "%s / %s (publication_rule=ECB 决议日当日公布(变更日观测))" % (cells["ECB_MRO"]["anchors"]["最新一期"]["publication_date"], cells["ECB_DFR"]["anchors"]["最新一期"]["publication_date"]),
    "决议日 2026-09-10,决议日当日公布(C2);走位: 2026-09-10 决议…决议日公布", "DEV", "date",
    "判断档隐含公布日 09-10,引擎发布面与关键数字表均为 2026-09-16——同一事件两个公布日")

for sid in ("ECB_MRO", "ECB_DFR"):
    st = at(sid, "2025-11-23")
    en = at(sid, CUTOFF)
    net = round((en[1] - st[1]) * 100, 1)
    add("④", "series_store.%s @<=2025-11-23 → @<=2026-11-23 (窗端点在值)" % sid, "%s→%s = %+dbp" % (st[1], en[1], net),
        "净变动 **+25bp**(MAP 政策一年窗路径, 括注 2.25→2.5 / 2.4→2.65)", "DEV", "caliber",
        "窗启在值(2025-06-11 起)→窗末在值=+50bp;同句列两步各 +25bp;引擎 net_bp=窗内首末观测差,漏计窗内首步")
st = at("JP_POLICY_RATE", "2025-11-23")
net_jp = round((1.227 - st[1]) * 100, 1)
add("④", "series_store.JP_POLICY_RATE @<=2025-11-23 → @<=2026-11-23", "%s(%s)→1.227 = %+.1fbp" % (st[1], st[0], net_jp),
    "净变动 **+67bp**(MAP 政策一年窗路径);近 12 个月政策窗净 +67bp(日本走位)", "DEV", "caliber",
    "同句六步之和=+75bp;窗启在值 0.478→1.227=+74.9bp;67bp 不含 2025-12 首步(+8bp)")
chj_all = [c for c in changes("JP_POLICY_RATE") if "2025-11-23" <= c[0] <= CUTOFF]
micro = [c for c in chj_all if abs(c[3]) < 0.5]
chj = [c for c in chj_all if abs(c[3]) >= 0.5]
add("④", "series_store.JP_POLICY_RATE 变更点 ∈ [2025-11-23, 2026-11-23]",
    "; ".join("%s %s→%s(%+dbp)" % (c[0], c[1], c[2], round(c[3])) for c in chj),
    "2025-12-01: 0.478→0.557(+8bp);2026-01-01: 0.557→0.728(+17bp);2026-06-01: 0.727→0.841(+11bp);2026-07-01: 0.841→0.978(+14bp);2026-09-01: 0.977→1.043(+7bp);2026-10-01: 1.043→1.227(+18bp)",
    "OK" if [c[0] for c in chj] == ["2025-12-01", "2026-01-01", "2026-06-01", "2026-07-01", "2026-09-01", "2026-10-01"] else "DEV",
    "numeric", "六个变动点日期与幅度逐项一致;引擎面与报告均省略 %s 的 %+.1fbp 微动(0.728→0.727),不影响结论" % (
        micro[0][0][:7], micro[0][3]) if micro else "六个变动点日期与幅度逐项一致")

# 公布规则算术
rules = [("EA_HICP_YOY", "2026-04-30", 16, "2026-05-16"), ("EA_HICP_YOY", "2026-10-31", 16, "2026-11-16"),
         ("JP_CPI_YOY", "2026-04-30", 20, "2026-05-20"), ("JP_CPI_YOY", "2026-10-31", 20, "2026-11-20"),
         ("JP_CPI_TOKYO_YOY", "2026-04-30", -1, "2026-04-29"), ("JP_CPI_TOKYO_YOY", "2026-10-31", -1, "2026-10-30"),
         ("JP_POLICY_RATE", "2026-04-30", 5, "2026-05-05"), ("JP_POLICY_RATE", "2026-10-31", 5, "2026-11-05")]
for mid, pe, lag, repd in rules:
    got = month_end_plus(pe, lag)
    add("④", "期末 %s %+d 天(规则: 月末%+d天,推定) [%s]" % (pe, lag, lag, mid), got, repd + "(关键数字表/覆盖表, 标注推定)",
        "OK" if got == repd else "DEV", "date", "推定规则算术一致")
add("④", "六指标 6个月前锚公布日 ≤ 2026-05-23", "最晚=%s" % max(p[0] for p in pubs if p[2] == "6个月前"),
    "6个月前锚各值按时点可见", "OK" if max(p[0] for p in pubs if p[2] == "6个月前") <= "2026-05-23" else "DEV", "date", "")
h04 = month_end_plus("2026-04-30", 16)
h05 = month_end_plus("2026-05-31", 16)
h07 = month_end_plus("2026-07-31", 16)
add("④", "HICP 终值规则 月末+16天: 2026-04→%s, 2026-05→%s, 2026-07→%s; 对质表第一行引 05-16 / 08-16" % (h04, h05, h07),
    "04 期 %s<06-11; 05 期 %s>06-11; 07 期 %s<09-10" % (h04, h05, h07),
    "2026-06-11 决议前 2026-04 读数 3.0 已发布(推定 2026-05-16);2026-09-10 决议前 2026-07 读数 2.9 已发布(推定 2026-08-16)",
    "OK", "date", "按终值规则成立;注: 冻结日历三条 EA_HICP 实录(2021M05/2022M06/2025M03)快报均在次月 1 日,若计快报则 06-11 前可见 2026-05=3.2、09-10 前可见 2026-08=3.2")

# ---------------------------------------------------------------- ⑤ 三利率与资产月窗
def trio(d0, d1, rep_trio, label):
    a = [at(s, d0) for s in ("UST_10Y", "TIPS_10Y", "BEI_10Y")]
    b = [at(s, d1) for s in ("UST_10Y", "TIPS_10Y", "BEI_10Y")]
    chg = [round((b[i][1] - a[i][1]) * 100) for i in range(3)]
    ident = chg[1] + chg[2]
    ok = chg == rep_trio and ident == chg[0]
    add("⑤", "series_store UST_10Y/TIPS_10Y/BEI_10Y %s" % label,
        "%s→%s | %s→%s | %s→%s = %+d/%+d/%+dbp; 实际+盈亏平衡=%+d" % (
            a[0][1], b[0][1], a[1][1], b[1][1], a[2][1], b[2][1], chg[0], chg[1], chg[2], ident),
        "名义 %+d = 实际 %+d + 盈亏平衡 %+dbp(MAP 三利率分解)" % tuple(rep_trio), "OK" if ok else "DEV", "numeric", "恒等式与幅度")


trio("2025-11-19", "2026-11-19", [91, 102, -11], "[2025-11-19, 2026-11-19]")
trio("2026-10-20", "2026-11-19", [-8, 11, -19], "[2026-10-20, 2026-11-19]")
lv = [at(s, "2026-11-19")[1] for s in ("UST_10Y", "TIPS_10Y", "BEI_10Y")]
add("⑤", "series_store @2026-11-19", "%s / %s / %s" % tuple(lv), "期末水平: 名义 5.04 / 实际 2.88 / 盈亏平衡 2.16", "OK" if lv == [5.04, 2.88, 2.16] else "DEV", "numeric", "")

assets = [("SPX", -9.36, "2026-11-20"), ("SHCOMP", -4.11, "2026-11-23"), ("DAX", -0.57, "2026-11-23"), ("NIKKEI225", -9.98, "2026-11-20"),
          ("VIX", 55.48, "2026-11-23"), ("DXY", 2.06, "2026-11-23"), ("GOLD_F", -9.83, "2026-11-23"), ("UST_10Y", 0.8, "2026-11-19")]
for sid, repv, repd in assets:
    a = val(sid, "2026-10-23")
    b = at(sid, CUTOFF)
    p = (b[1] / a - 1.0) * 100.0
    ok = num_eq(p, repv, 0.0051) and b[0] == repd
    add("⑤", "series_store.%s @2026-10-23 → @<=%s" % (sid, CUTOFF), "%s→%s(%s) = %+.2f%%" % (r(a, 2), r(b[1], 2), b[0], p),
        "%+.2f%%(至 %s)(MAP 资产月窗表 / M1 step4)" % (repv, repd), "OK" if ok else "DEV", "numeric", "月窗端点与幅度")

# ---------------------------------------------------------------- ⑥ 转折
def t(sid, d0, d1, rep0, rep1, where, cat="⑥"):
    a = val(sid, d0)
    b = val(sid, d1)
    ok = num_eq(a, rep0) and num_eq(b, rep1)
    add(cat, "series_store.%s @%s, @%s" % (sid, d0, d1), "%s→%s (Δ%+.2f)" % (a, b, b - a), "%s→%s (%s)" % (rep0, rep1, where),
        "OK" if ok else "DEV", "numeric", "")


t("JP_CPI_YOY", "2025-11-01", "2026-02-01", 2.9, 1.27, "转折 T1 / 候选面")
t("EA_HICP_YOY", "2026-02-01", "2026-05-01", 1.9, 3.2, "转折 T2 / 候选面")
t("JP_POLICY_RATE", "2026-04-01", "2026-07-01", 0.727, 0.978, "转折 T3 / 候选面")
t("JP_POLICY_RATE", "2026-04-01", "2026-06-01", 0.727, 0.841, "转折 T3 过渡值")
t("JP_CPI_TOKYO_YOY", "2026-06-01", "2026-09-01", 1.6, 2.69, "候选面(引擎转折候选)")
cands = REP["research_plan"]["turning_candidates"]["candidates"]
mx_delta = max(cands, key=lambda c: abs(c["delta"]))
add("⑥", "report.json turning_candidates.candidates[*].delta (|Δ| 最大)", "%s %.2f" % (mx_delta["metric_id"], mx_delta["delta"]),
    "候选池内最大单段变动(JP_CPI_YOY −1.63)", "OK" if mx_delta["metric_id"] == "JP_CPI_YOY" else "DEV", "claim", "")
jp_path = [(m, ym("JP_CPI_YOY", 2026, m)) for m in range(3, 11)]
add("⑥", "series_store.JP_CPI_YOY 2026-03..2026-10", ", ".join("%d %.2f" % (m, v) for m, v in jp_path),
    "2026-03 1.46、2026-04 1.38、2026-05 1.53、2026-06 1.67、2026-07 1.97、2026-08 1.98、2026-09 2.16、2026-10 2.44(T1 叙述)",
    "OK" if [v for _, v in jp_path] == [1.46, 1.38, 1.53, 1.67, 1.97, 1.98, 2.16, 2.44] else "DEV", "numeric", "")
ea_path = [(m, ym("EA_HICP_YOY", 2026, m)) for m in range(6, 11)]
add("⑥", "series_store.EA_HICP_YOY 2026-06..2026-10", ", ".join("%d %.1f" % (m, v) for m, v in ea_path),
    "2026-06 2.8、2026-07 2.9、2026-08 3.2、2026-09 3.8、2026-10 4.0(T2 叙述)", "OK" if [v for _, v in ea_path] == [2.8, 2.9, 3.2, 3.8, 4.0] else "DEV", "numeric", "")
jpr_path = [(m, ym("JP_POLICY_RATE", 2026, m)) for m in (1, 8, 9, 10)]
add("⑥", "series_store.JP_POLICY_RATE 2026-01, 2026-08..2026-10", ", ".join("%d %.3f" % (m, v) for m, v in jpr_path),
    "2026-01 0.728(T1 叙述);2026-08 0.977、2026-09 1.043、2026-10 1.227(T3 叙述)", "OK" if [v for _, v in jpr_path] == [0.728, 0.977, 1.043, 1.227] else "DEV", "numeric", "")
last12 = [(d, v) for d, v in ser("EA_HICP_YOY") if "2025-11-01" <= d <= "2026-10-01"]
mx12 = max(last12, key=lambda x: x[1])
ge4 = [(d, v) for d, v in ser("EA_HICP_YOY") if v is not None and v >= 4.0 and d < "2026-10-01"]
add("⑥", "series_store.EA_HICP_YOY 近12月最大值 / 2026-10 之前最近 ≥4.0", "max=%s@%s; 前次 ≥4.0=%s" % (mx12[1], mx12[0], ge4[-1][0]),
    "2026-10 达 4.0 创本轮新高 / 最新读数为近十二个月最高", "OK" if (mx12[0] == "2026-10-01" and ge4[-1][0] < "2024-01-01") else "DEV", "claim", "关系词『新高/最高』成立")

# 「2025-07 高点」
jp25 = [(d, v) for d, v in ser("JP_CPI_YOY") if d.startswith("2025-")]
jp25max = max(jp25, key=lambda x: x[1])
add("⑥", "series_store.JP_CPI_YOY 2025 各月 / 2025-06, 2025-07, 2025-08",
    "2025 最大=%s@%s; 2025-06=%.2f, 2025-07=%.2f, 2025-08=%.2f" % (jp25max[1], jp25max[0], ym("JP_CPI_YOY", 2025, 6), ym("JP_CPI_YOY", 2025, 7), ym("JP_CPI_YOY", 2025, 8)),
    "JP_CPI_YOY 自 2025-07 高点 3.1 回落至 2026-02 的 1.27(M1 step1 [E1] / 日本走位)", "DEV", "direction",
    "2025-07=3.1 非高点: 前一月 2025-06=3.27 更高;2025 年内最大为 2025-01 的 4.03;引擎 S4_history 面无『高点』标记")

# 同窗方向
ea_in_jp = (ym("EA_HICP_YOY", 2025, 11), ym("EA_HICP_YOY", 2026, 2))
add("⑥", "series_store.EA_HICP_YOY @2025-11 → @2026-02 (T1 同窗)", "%s→%s (Δ%+.1f)" % (ea_in_jp[0], ea_in_jp[1], ea_in_jp[1] - ea_in_jp[0]),
    "同期欧元区 HICP 反向上行(2026-02 1.9→2026-05 3.2),两地通胀转折方向相反(T1 跟进/背离)", "DEV", "direction",
    "T1 窗 2025-11..2026-02 内欧元区亦下行(2.1→1.9),与日本同向;所引上行属 2026-02..2026-05 另一窗")
jp_in_ea = (ym("JP_CPI_YOY", 2026, 2), ym("JP_CPI_YOY", 2026, 5))
add("⑥", "series_store.JP_CPI_YOY @2026-02 → @2026-05 (T2 同窗)", "%s→%s (Δ%+.2f)" % (jp_in_ea[0], jp_in_ea[1], jp_in_ea[1] - jp_in_ea[0]),
    "日本端同窗通胀下行(2026-05 1.53),两地背离(T2 跟进/背离)", "DEV", "direction",
    "T2 窗 2026-02..2026-05 内日本自谷底回升(1.27→1.53),与欧元区同向;与 T1 叙述『此后总体回升』自相矛盾")
add("⑥", "ECB 变更日 2026-06-17 ∈ [2026-04, 2026-07]", "in-window", "ECB 端同期亦收紧(2026-06-11 决议、2026-06-17 生效),两地同向(T3)", "OK", "date", "")

# ---------------------------------------------------------------- ⑦ 传导链数字
t("EA_HICP_YOY", "2026-02-01", "2026-10-01", 1.9, 4.0, "M1 step1 / 传导链①", cat="⑦")
add("⑦", "series_store.EA_HICP_YOY @2026-05, @2026-06", "%s, %s" % (ym("EA_HICP_YOY", 2026, 5), ym("EA_HICP_YOY", 2026, 6)),
    "2026-05 的 3.2(2026-06 一度回落至 2.8)(M1 step1)", "OK" if (num_eq(ym("EA_HICP_YOY", 2026, 5), 3.2) and num_eq(ym("EA_HICP_YOY", 2026, 6), 2.8)) else "DEV", "numeric", "")
for sid, repv in (("USDJPY", 158.96), ("VIX", 30.24), ("DAX", 25039.1), ("EURUSD", 1.1)):
    v = val(sid, "2026-11-23")
    add("⑦", "series_store.%s @2026-11-23" % sid, str(v), "%s(观测 2026-11-23)(C2 / M1 step3)" % repv,
        "OK" if num_eq(v, repv, 0.0051 if sid not in ("EURUSD", "DAX") else 0.051) else "DEV", "numeric",
        "" if sid != "EURUSD" else "报告 1.1=引擎事实行值(两位有效数字),序列值 1.096491")
add("⑦", "series_store.SPX @2026-11-20", str(val("SPX", "2026-11-20")), "6910.39(观测 2026-11-20)(C2)", "OK" if num_eq(val("SPX", "2026-11-20"), 6910.39, 0.0051) else "DEV", "numeric", "")
n_evr = 0
for c in AJ["l3"]["contradictions"]:
    n_evr += len(c.get("evidence_refs", []))
for m in AJ["l3"]["mechanism_chains"]:
    for l in m["links"]:
        n_evr += len(l.get("evidence_refs", []))
add("⑦", "agent_judgment.json l3.*.evidence_refs 计数", str(n_evr), "三条矛盾陈述+机制链四环共 20 条 snapshot_fact 引用(质量门注记)", "OK" if n_evr == 20 else "DEV", "numeric", "")
ev_path = os.path.join(os.path.dirname(os.path.abspath(AJ_P)), "evidence_index.json")
if os.path.exists(ev_path):
    with open(ev_path, "r", encoding="utf-8") as fh:
        ev_refs = set(r["ref"] for r in json.load(fh))
    all_refs = []
    for c in AJ["l3"]["contradictions"]:
        all_refs += c.get("evidence_refs", [])
    for m in AJ["l3"]["mechanism_chains"]:
        for l in m["links"]:
            all_refs += l.get("evidence_refs", [])
    n_res = sum(1 for r_ in all_refs if r_ in ev_refs)
    add("⑦", "agent_judgment.json l3.*.evidence_refs ∩ evidence_index.json[*].ref", "%d/%d 可解析" % (n_res, len(all_refs)),
        "全部解析到本报告证据索引；零悬空引用(质量门注记)", "OK" if n_res == len(all_refs) else "DEV", "claim", "")

# ---------------------------------------------------------------- ⑧ 历史类比
s6 = [s for s in REP["steps"] if s["step"] == "S6_analog"][0]
env6 = s6.get("envelope", {}).get("data", {})
top = env6.get("top", []) if env6 else []
cand6 = env6.get("candidates", {}) if env6 else {}
add("⑧", "report.json steps[S6_analog].ok/executed; envelope.data.candidates.scanned/valid; envelope.data.top[*]",
    "executed=%s ok=%s; scanned=%s valid=%s; top=%s" % (s6["executed"], s6["ok"], cand6.get("scanned"), cand6.get("valid"),
                                                   ",".join("%s(%.3f)" % (c["candidate_month"], c["distance"]) for c in top)),
    "检索范围=引擎 analog 能力未启用(本问未请求历史相似对照…)(MAP L205 零段类比注 / reader_map.history_zero_case_note)", "DEV", "claim",
    "analog 已运行且给出 5 个候选;FULL_REPORT 含『历史相似结构』表;引擎内部摘要 question_summary 亦列『历史类比』(非问句原文)——缺口理由不属实")
# 反方攻击: analog 候选若被采用是否可信(本席不替研判席选段,只核其口径)
a1 = top[0]["aftermath"] if top else {}
add("⑧", "report.json steps[S6_analog].envelope.data.top[0].candidate_month/distance/aftermath.label", "%s d=%s; %s" % (
    top[0]["candidate_month"], top[0]["distance"], str(a1.get("label"))[:40]) if top else "n/a",
    "(研判席零段呈现;若采用须按事后窗口径)", "OK", "claim", "引擎候选仅 TOP5 簇代表、事后结果标『非预测』;零段呈现本身不违规,违规在理由陈述")

# ---------------------------------------------------------------- ⑨ 情景
ea_now = ym("EA_HICP_YOY", 2026, 10)
jp_now = ym("JP_CPI_YOY", 2026, 10)
vix_now = val("VIX", "2026-11-23")
add("⑨", "截止日读数 vs S1 触发阈值(EA ≥4.0, JP ≥2.0, VIX >30)", "EA=%.1f, JP=%.2f, VIX=%.2f → 4.0≥4.0 真; 2.44≥2.0 真; 30.24>30 真" % (ea_now, jp_now, vix_now),
    "2026-12 或 2027-01 发布的 EA_HICP_YOY 同比 ≥4.0% 且 JP_CPI_YOY 同比 ≥2.0%,同时 VIX 高于 30(S1 触发)", "DEV", "caliber",
    "通胀两条件绑定期为 2026-12/2027-01 发布值(尚可观测);『VIX 高于 30』未绑日期,截止日已满足,不具前瞻区分力")
add("⑨", "S1 前提『维持 3.5% 以上』 vs 证伪『两月均 <3.0%』 vs 触发 ≥4.0%", "未定带 [3.0,3.5)", "S1 前提 3.5% 以上;证伪 3.0% 以下(S1/S2 阈值)", "DEV", "caliber",
    "3.0–3.4 区间既不触发也不证伪;S2 触发 ≤3.4% 宽于其前提 <3.0%;指标在场可观测")
add("⑨", "期限 vs 截止日; 证伪指标在场", "2027-02-15 > %s; EA_HICP_YOY/JP_CPI_YOY 在 series_store" % CUTOFF, "期限 2027-02-15;证伪指标 EA_HICP_YOY(次级 JP_CPI_YOY)", "OK", "claim", "两情景方向互补(S2 自述并列反例)")

# ---------------------------------------------------------------- ⑩ 对质表与文字
facts = {f["metric_id"]: f for f in SNAP["facts"] if f.get("observation_date") == "2026-11-23" or f.get("metric_id") in ("USDJPY", "EURUSD", "DXY", "VIX")}
m1 = {}
for f in SNAP["facts"]:
    d = (f.get("derived") or {}).get("m1") or {}
    if d.get("pct_change") is not None:
        m1[f["metric_id"]] = (d.get("basis_date"), d.get("basis_value"), d["pct_change"])
add("⑩", "snapshot.facts[EURUSD/USDJPY/DXY/VIX].derived.m1 (引擎近一月面)",
    "; ".join("%s m1 %s→%s = %+.2f%%" % (k, m1[k][1], val(k, "2026-11-23"), m1[k][2]) for k in ("EURUSD", "USDJPY", "DXY") if k in m1),
    "引擎面仅水平观测,利率→汇率为近零渠道(无本地数据支持方向依据),方向对质不可判(对质表第二行 verdict_note / M1 step3)", "DEV", "claim",
    "引擎面有近一月变化: 欧元、日元同向对美元走弱,美元指数上行——与竞争解释(同向随美元)相容,主解释『反向组合』预期与本月观测不符")
a, b, p = pct("USDJPY", "2026-10-23", CUTOFF)
add("⑩", "series_store.USDJPY @2026-10-23 → @2026-11-23", "%s→%s = %+.2f%%" % (a[1], b[1], p), "(报告未给 USDJPY 变化幅,仅称水平观测)", "DEV", "disclosure",
    "对质表第二行区分指标 EURUSD 只列 30 日变化,USDJPY 变化幅在同面可得而未用")
add("⑩", "对质表第一行裁定 vs C2 竞争解释", "同一判断档内: 行1『支持主解释』;C2『月频证据下两种驱动不可区分』", "行1: 支持主解释;C2: 月频证据下两种驱动不可区分", "DEV", "claim",
    "自相矛盾;且两解释对『决议前可见读数』预期未分立(程序驱动不禁止读数高时加息),按对质口径应=尚不能区分")
for sid in ("DAX", "CAC40", "SPX", "NIKKEI225"):
    a, b, p = pct(sid, "2026-10-23", "2026-11-20")
    add("⑩", "series_store.%s @2026-10-23 → @2026-11-20 (同日口径)" % sid, "%s→%s = %+.2f%%" % (r(a[1], 2), r(b[1], 2), p),
        ("DAX 下跌 0.57%(至 2026-11-23)、SPX 下跌 9.36%、NIKKEI225 下跌 9.98%(至 2026-11-20)(对质表第三行 / M1 step4)" if sid == "DAX" else "(同窗对照值,报告未列)"),
        "DEV" if sid == "DAX" else "OK", "disclosure",
        "同日口径(至 11-20)DAX −1.50% 远强于 SPX −9.36%,与主解释『两地股指弱于美股』在欧元区一端相反;note 仅举 NIKKEI225 跌幅大于 DAX 与 SPX,未披露此反向事实" if sid == "DAX" else "对照值")
a, b, p = pct("VIX", "2026-11-13", "2026-11-20")
add("⑩", "series_store.VIX @2026-11-13 → @2026-11-20; @2026-11-20 → @2026-11-23", "%s→%s = %+.1f%%; %s→%s = %+.1f%%" % (a[1], b[1], p, b[1], val("VIX", "2026-11-23"), (val("VIX", "2026-11-23") / b[1] - 1) * 100),
    "主解释预期 VIX 高位与政策紧缩事件日历联动、回落缓慢;竞争解释预期 VIX 冲击独立于政策日历、快速回落;裁定 尚不能区分(对质表第三行)", "DEV", "claim",
    "VIX 跳升集中于 11-13→11-20 周,距两地最近政策日(10-30)两周以上;11-23 较 11-20 回落 15.7%——两项观测均偏竞争解释,note 称『方向与紧缩叙事相容』未计入")
s5 = [s for s in REP["steps"] if s["step"] == "S5_compare"][0]["envelope"]["data"]
add("⑩", "report.json steps[S5_compare].envelope.data.pearson_returns / n_change_pairs", "%s / %s" % (round(s5["pearson_returns"], 3), s5["n_change_pairs"]), "pearson 0.264 (n=45)(MAP 日度相关)", "OK" if (round(s5["pearson_returns"], 3) == 0.264 and s5["n_change_pairs"] == 45) else "DEV", "numeric", "")

# ---------------------------------------------------------------- ⑪ 诚实缺席
reg_ids = set(m["metric_id"] for m in REG["metrics"])
add("⑪", "metric_registry.metrics[*].metric_id; series_store keys", "JP_POLICY_TARGET in registry=%s; in series_store=%s" % ("JP_POLICY_TARGET" in reg_ids, "JP_POLICY_TARGET" in STORE),
    "注册表无 JP_POLICY_TARGET…历史序列与元数据均不可得(MAP L32 / 日本走位)", "OK" if ("JP_POLICY_TARGET" not in reg_ids and "JP_POLICY_TARGET" not in STORE) else "DEV", "claim", "缺口属实")
ga = SNAP["gate_a"]
add("⑪", "snapshot.gate_a.noncore_degraded / series_store 末观测", "noncore_degraded 含 ECB_DFR/ECB_MRO=%s; 末观测=%s/%s" % (
    "ECB_DFR" in ga["noncore_degraded"] and "ECB_MRO" in ga["noncore_degraded"], at("ECB_DFR", CUTOFF)[0], at("ECB_MRO", CUTOFF)[0]),
    "欧央行序列止于 2026-09-16(DEGRADED)(标题 / C3)", "OK", "claim", "降级披露属实")
add("⑪", "snapshot.sources_status.ea; gate_a DEGRADED 成因文字", "sources_status.ea.status=%s(file=%s); ECB 事实行 issues=%s" % (
    SNAP["sources_status"]["ea"].get("status"), SNAP["sources_status"]["ea"].get("file"),
    [i for f in SNAP["facts"] if f.get("metric_id") == "ECB_DFR" for i in f.get("issues", [])][:1]),
    "ECB 数据面断档…(源端缺席)(C3 首句)", "DEV", "disclosure",
    "采集档当日 EXACT;注册表 decision_dated 注记『无更晚已证实决议不作过期』;『断档/源端缺席』系推断而非事实,后文虽标【尚未验证】并列两解释")
add("⑪", "证据面全文检索『ECB 504』(report.json 引擎面 / evidence_index / snapshot / 日历 / 注册表)", "仅出现于判断档自身文字",
    "生产观察登记 ECB 504(C3 竞争解释 1)", "UNVER", "unsourced", "证据面无此登记,数字无出处")
jp_cpi_cal = [e for e in CAL["entries"] if e.get("metric_id") in ("JP_CPI_YOY", "JP_CPI_TOKYO_YOY")]
add("⑪", "release_calendar.entries[*] (metric_id ∈ JP_CPI_YOY/JP_CPI_TOKYO_YOY); 引擎 publication_rule", "JP CPI 日历条目=%d; 东京规则文本含『官方实录锚 2026年10月分=2026-10-30』; 全国规则无实录锚" % len(jp_cpi_cal),
    "全国: 官方实录公表日同为 2026-11-20,引擎外旁证;东京: 官方实录公表日同为 2026-10-30,引擎外旁证(C1 / 日本走位)", "UNVER", "unsourced",
    "东京 10-30 可由引擎规则文本旁证;全国 2026-11-20『官方实录』在只读面无出处(已标引擎外旁证)")
add("⑪", "snapshot.gate_a.noncore_missing; series_store.JP_CPI_TOKYO_YOY; facts[JP_CPI_TOKYO_YOY]", "noncore_missing 含 JP_CPI_TOKYO_YOY=%s; series n=%d 末=%s; 事实行数=%d" % (
    "JP_CPI_TOKYO_YOY" in ga["noncore_missing"], len(ser("JP_CPI_TOKYO_YOY")), ser("JP_CPI_TOKYO_YOY")[-1], sum(1 for f in SNAP["facts"] if f.get("metric_id") == "JP_CPI_TOKYO_YOY")),
    "JP×inflation | 东京都CPI同比 | ok | ok(MAP 覆盖表);东京 2.73 引用无质量/缺席注记", "DEV", "disclosure",
    "Gate A 将东京 CPI 列为非核心缺数(来源文件在场而指标缺席),报告未披露该项,仅披露总体 DEGRADED")

# ---------------------------------------------------------------- ⑫ 截止日当日观测
vix_fact = [f for f in SNAP["facts"] if f.get("metric_id") == "VIX"][0]
add("⑫", "snapshot.research_as_of; facts[VIX@2026-11-23].calc; series_store.VIX @2026-11-20 / @2026-11-23",
    "research_as_of=%s; calc=『%s』; 11-20=%s, 11-23=%s" % (SNAP["research_as_of"], vix_fact["calc"], val("VIX", "2026-11-20"), val("VIX", "2026-11-23")),
    "11-23 值为当日实时快照(非收盘价)(M1 step3/step4 / 对质表)", "DEV", "disclosure",
    "说明与快照事实行『VIX指数收盘』口径相反;快照时间 20:41(+08:00)=12:41Z 时美股常规时段未开,30.24≠11-20 收盘 35.89,该值时点/口径在证据面不可核;VIX 月窗 +55.5% 与 S1 触发『VIX>30』均依赖此值(同日口径至 11-20 为 +84.5%)")
add("⑫", "series_store.DAX @2026-11-23 vs @2026-11-20; research_as_of", "11-20=%s, 11-23=%s" % (val("DAX", "2026-11-20"), val("DAX", "2026-11-23")),
    "DAX 下跌 0.57%(至 2026-11-23,当日实时快照、非收盘价)", "OK", "disclosure", "带时点/口径说明;与 12:41Z 时点相容(同日口径至 11-20 为 −1.50%)")

# ---------------------------------------------------------------- ⑬ 目标利率与同比
add("⑬", "release_calendar RC-JP-BOJ-TARGET-2026-09 (effective_on 2026-09-24 ≤ cutoff); RC-JP-BOJ-MAINT-2026-10", "现行有效目标=1.25(生效 2026-09-24, 维持至 2026-10-30 核验)",
    "日本央行政策目标约 1.25%(2026-09-18 决议、2026-09-24 生效,2026-10-30 确认维持)", "OK", "numeric", "现行有效;无待生效")
add("⑬", "series_store.ECB_MRO/ECB_DFR 末值; gate_a", "MRO 2.65 / DFR 2.5 (2026-09-16 起, DEGRADED)", "欧央行主要再融资利率 2.65%/存款便利利率 2.5%(2026-09-16 生效;DEGRADED)", "OK", "numeric",
    "序列面现行值;『官方目标』定性无日历实录(MAP 标草稿 map_official_target_missing),判断档以 DEGRADED+【尚未验证】披露")
add("⑬", "JP_POLICY_RATE 2026-10 月均 vs 日历目标", "1.227 vs 1.25", "最新一期报 1.227%…月均口径非宣布值(C2)", "OK", "claim", "两口径分列未冒充")

# ---------------------------------------------------------------- 输出
os.makedirs(OUT, exist_ok=True)
cols = ["id", "cat", "source", "computed", "reported", "status", "kind", "note"]
with open(os.path.join(OUT, "recompute_table.tsv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t")
    w.writeheader()
    for p in POINTS:
        w.writerow(p)
with open(os.path.join(OUT, "recompute_table.md"), "w", encoding="utf-8") as fh:
    fh.write("# T3 Round-1 复算表(席位自算;只读面直算后与报告/判断档文字比对)\n\n")
    fh.write("| # | 类 | 出处键 | 直算值 | 报告值 | 一致与否 | 类型 | 备注 |\n|---|---|---|---|---|---|---|---|\n")
    for p in POINTS:
        cells_ = [p["id"], p["cat"], p["source"], p["computed"], p["reported"], p["status"], p["kind"], p["note"]]
        fh.write("| " + " | ".join(str(c).replace("|", "\\|").replace("\n", " ") for c in cells_) + " |\n")
n = len(POINTS)
ok_n = sum(1 for p in POINTS if p["status"] == "OK")
dev = [p for p in POINTS if p["status"] == "DEV"]
unver = [p for p in POINTS if p["status"] == "UNVER"]
kinds = {}
for p in dev + unver:
    kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
summary = {
    "recompute_points": n,
    "ok": ok_n,
    "recompute_mismatches": len(dev) + len(unver),
    "dev": len(dev),
    "unver": len(unver),
    "mismatch_kinds": kinds,
    "mismatch_details": ["%s [%s/%s] %s: 直算=%s | 报告=%s | %s" % (p["id"], p["cat"], p["kind"], p["source"], p["computed"], p["reported"], p["note"]) for p in dev + unver],
    "by_cat": {},
}
for p in POINTS:
    c = summary["by_cat"].setdefault(p["cat"], {"n": 0, "ok": 0, "mismatch": 0})
    c["n"] += 1
    if p["status"] == "OK":
        c["ok"] += 1
    else:
        c["mismatch"] += 1
with open(os.path.join(OUT, "recompute_summary.json"), "w", encoding="utf-8") as fh:
    json.dump(summary, fh, ensure_ascii=False, indent=1)
print("recompute_points=%d ok=%d dev=%d unver=%d mismatches=%d kinds=%s" % (n, ok_n, len(dev), len(unver), len(dev) + len(unver), kinds))
for p in POINTS:
    print("%s %s %-3s %-11s computed=%s | reported=%s" % (p["id"], p["cat"], p["status"], p["kind"], p["computed"][:150], p["reported"][:110]))
