#!/usr/bin/python3 -I
"""Supplementary computations behind the seat's own findings (MINOR/NIT notes and counter-attacks).

These are NOT recomputations of numbers claimed by the judgment; they are the seat's additions, so they are
kept out of the recompute-point count and recorded separately with their source keys so that every number
quoted in PROSE-round1.md / VERDICT-round1.json can be traced (file + key).

Read-only. Args: <snapshot.json> <metric_registry.json> <release_calendar.json> <run_dir> <out_dir>
"""
import datetime as dt
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("s10_common", os.path.join(HERE, "s10_common.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

snap, reg, cal = (C.load_json(p) for p in sys.argv[1:4])
run_dir, out_dir = sys.argv[4], sys.argv[5]
ss = snap["series_store"]
regm = {m["metric_id"]: m for m in reg["metrics"]}
S = []


def rec(sid, what, src, value):
    S.append({"id": sid, "what": what, "src": src, "value": value})


# S01 day-level single-day changes (close-to-close, previous available observation)
DAYS = ["2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19", "2026-11-20"]
day = {}
for mid in ("SPX", "NIKKEI225", "DAX", "CAC40", "VIX", "EURUSD", "USDJPY"):
    ds, vs = C.series(ss, mid)
    row = []
    for d in DAYS:
        k = ds.index(d)
        row.append([d, C.rnd(vs[k - 1], 4), C.rnd(vs[k], 4), C.rnd(C.pct(vs[k], vs[k - 1]), 2)])
    day[mid] = row
rec("S01", "发布日窗内逐日收盘变动%(前值→当日值→变动)", "series_store.{SPX,NIKKEI225,DAX,CAC40,VIX,EURUSD,USDJPY} 2026-11-16..2026-11-20", day)

# S02 multi-horizon differences of the latest YoY readings
mh = {}
for mid in ("JP_CPI_YOY", "EA_HICP_YOY"):
    m = C.monthly(ss, mid)
    ks = sorted(m)
    last = ks[-1]
    prior = [k for k in ks if "2025-11" <= k <= "2026-09"]
    mh[mid] = {"latest": [last, m[last]],
               "diff_vs": {k: C.rnd(m[last] - m[k], 2) for k in ("2026-09", "2026-07", "2026-04", "2025-10")},
               "prior_11_months_below_latest": ["%d/%d" % (sum(1 for k in prior if m[k] < m[last]), len(prior)),
                                               {k: m[k] for k in prior}]}
rec("S02", "最新同比读数相对 1/3/6/12 个月前与去年同月的差;近 12 个月其余各月低于最新值的个数",
    "series_store.JP_CPI_YOY / EA_HICP_YOY", mh)

# S03 JP_POLICY_RATE monthly steps in bp and change points vs BOJ decision records
ds, vs = C.series(ss, "JP_POLICY_RATE")
steps = [[ds[i], C.rnd(vs[i - 1], 3), C.rnd(vs[i], 3), C.rnd(C.bp(vs[i], vs[i - 1]), 1)] for i in range(1, len(vs)) if "2025-11" <= ds[i][:7] <= "2026-10"]
pts = [[ds[i], C.rnd(C.bp(vs[i], vs[i - 1]), 1)] for i in range(1, len(vs)) if vs[i] != vs[i - 1] and "2025-11-23" <= ds[i] <= "2026-11-23"]
dec = sorted(e["decision_date"] for e in cal.get("entries", []) if e.get("metric_id") == "JP_POLICY_TARGET" and e.get("kind") == "policy_decision")
withrec = [p[0] for p in pts if any(0 <= (C.D(p[0]) - C.D(x)).days <= 45 for x in dec)]
rec("S03", "月均逐月台阶(bp)与一年窗变动点及其前 45 天内的日央行决议实录", "series_store.JP_POLICY_RATE; release_calendar JP_POLICY_TARGET policy_decision",
    {"steps_into_month": steps, "change_points_1y": pts, "boj_decisions": dec, "points_with_record_within_45d": withrec})

# S04 synthetic EURJPY over longer windows (six-month window = question window start 2026-05-23,
# taken from the latest common observation of the two legs on or before that date)
ed, ev = C.series(ss, "EURUSD")
jd_, jv = C.series(ss, "USDJPY")
_common = sorted(set(d for d, v in zip(ed, ev) if v is not None and d <= "2026-05-23")
                 & set(d for d, v in zip(jd_, jv) if v is not None and d <= "2026-05-23"))
START6 = _common[-1]


def cross(d):
    return ev[ed.index(d)] * jv[jd_.index(d)]


cr = {d: C.rnd(cross(d), 4) for d in sorted(set((START6, "2026-08-20", "2026-09-15", "2026-09-16", "2026-10-23", "2026-11-20", "2026-11-23")))}
legs = {"EURUSD %s→2026-11-20 %%" % START6: C.rnd(C.pct(ev[ed.index("2026-11-20")], ev[ed.index(START6)]), 4),
        "USDJPY %s→2026-11-20 %%" % START6: C.rnd(C.pct(jv[jd_.index("2026-11-20")], jv[jd_.index(START6)]), 4)}
chg = {a + "→" + b: C.rnd(C.pct(cross(b), cross(a)), 2) for a, b in ((START6, "2026-11-20"), ("2026-08-20", "2026-11-20"),
                                                                     (START6, "2026-09-15"), ("2026-09-16", "2026-11-20"),
                                                                     (START6, "2026-10-23"), ("2026-10-23", "2026-11-20"))}
pol = {}
for day in (START6, "2026-11-20"):
    mro = C.last_on_or_before(ss, "ECB_MRO", day)
    jpr = C.last_on_or_before(ss, "JP_POLICY_RATE", day)
    pol[day] = {"ECB_MRO": list(mro), "JP_POLICY_RATE": list(jpr), "diff_pp": C.rnd(mro[1] - jpr[1], 3)}
rec("S04", "合成交叉盘(EURUSD×USDJPY)长窗与窗两端可见政策水平差(MRO−日本月均)",
    "series_store.EURUSD × series_store.USDJPY; series_store.ECB_MRO; series_store.JP_POLICY_RATE",
    {"start6": START6, "cross": cr, "legs": legs, "cross_change_%": chg, "visible_policy_differential": pol})

# S10 margins behind the face-off-1 'opposing observation' (latest-vintage readings)
ea_m = C.monthly(ss, "EA_HICP_YOY")
rec("S10", "对质环 1 各『变更前可见读数』相对 2026-02 的差;2026-05 峰值与第二次决议日前读数的差(修订敏感度)",
    "series_store.EA_HICP_YOY @2026-02/2026-04/2026-05/2026-07/2026-08",
    {"vs_2026-02": {k: C.rnd(ea_m[k] - ea_m["2026-02"], 2) for k in ("2026-04", "2026-05", "2026-07", "2026-08")},
     "peak_minus_2026-07": C.rnd(ea_m["2026-05"] - ea_m["2026-07"], 2)})

# S05 like-for-like US policy band and market yield
rec("S05", "美元端政策利率(同口径)与市场收益率", "series_store.DFEDTARL/DFEDTARU/UST_10Y 末观测",
    {m: list(C.last_obs(ss, m)) for m in ("DFEDTARL", "DFEDTARU", "UST_10Y")})

# S06 registry caliber texts quoted in the findings
fres = {m: regm[m].get("freshness") for m in ("ECB_MRO", "ECB_DFR")}
ea_reg = json.dumps(regm["EA_HICP_YOY"], ensure_ascii=False)
i_rev = ea_reg.find("修订")
rec("S06", "注册表口径文字", "metric_registry.ECB_MRO/ECB_DFR.freshness; EA_HICP_YOY 内『修订』上下文与 release_semantics 全文",
    {"freshness": fres, "EA_HICP_revision_ctx": ea_reg[max(0, i_rev - 160):i_rev + 200] if i_rev >= 0 else None,
     "EA_HICP_release_semantics": regm["EA_HICP_YOY"].get("release_semantics")})

# S07 VIX month-window change at displayed vs stored precision
rec("S07", "VIX 月窗幅度两种精度", "series_store.VIX @2026-10-23/@2026-11-20",
    {"stored": C.rnd(C.pct(35.889999, 19.450001), 4), "displayed": C.rnd(C.pct(35.89, 19.45), 4)})

# S08 JP CPI series maximum
m = C.monthly(ss, "JP_CPI_YOY")
mx = max(m, key=lambda k: m[k])
rec("S08", "JP_CPI_YOY 全序列最高", "series_store.JP_CPI_YOY", [mx, m[mx]])

# S09 reader-report line checks (textual)
lines = open(os.path.join(run_dir, "MAP_REPORT.md"), "r", encoding="utf-8").read().split("\n")
full = open(os.path.join(run_dir, "FULL_REPORT.md"), "r", encoding="utf-8").read().split("\n")
rep = open(os.path.join(run_dir, "report.md"), "r", encoding="utf-8").read()
txt = {"MAP": {"见裁定理由": [i + 1 for i, x in enumerate(lines) if "见裁定理由" in x],
               "2026-11-05": [i + 1 for i, x in enumerate(lines) if "2026-11-05" in x],
               "同轮事件并项": [i + 1 for i, x in enumerate(lines) if "同轮事件并项" in x],
               "STALE": [i + 1 for i, x in enumerate(lines) if "STALE" in x]},
       "FULL": {"seat_invoked=False": [i + 1 for i, x in enumerate(full) if "seat_invoked=False" in x],
                "STALE": [i + 1 for i, x in enumerate(full) if "STALE" in x]},
       "report.md STALE": rep.count("STALE")}
rec("S09", "读者报告行号核对", "MAP_REPORT.md / FULL_REPORT.md / report.md 文本", txt)

json.dump(S, open(os.path.join(out_dir, "supplement.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for s in S:
    print("==", s["id"], s["what"])
    print("   src:", s["src"])
    print("   ", json.dumps(s["value"], ensure_ascii=False))
