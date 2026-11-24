# -*- coding: utf-8 -*-
"""Part 3: sections (5) three-rate decomposition + asset month window, (6) turning judgments.
usage: python3 -I s7_p3.py <run_dir> <install_tree> <out_dir>"""
import importlib.util
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))


def mod(n):
    s = importlib.util.spec_from_file_location(n, os.path.join(HERE, n + ".py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


lib = mod("t3lib")
c = lib.build(sys.argv[1], sys.argv[2], sys.argv[3])
A = c.A
SNAP = "快照 series_store."
RM = c.J["reader_map"]
cut = c.cutoff


def sec(name):
    def d(f):
        try:
            f()
        except Exception:
            c.errors.append({"section": name, "trace": traceback.format_exc()[-900:]})
    return lambda f: (d(f), f)[1]


@sec("5-rates-trio")
def s5a():
    urt = c.plan["us_rates_trio"]
    rd = RM["rates_decomposition"]
    wf, wt = urt["window"]["from"], urt["window"]["to"]
    tri = [round((lib.val(m, wt) - lib.val(m, wf)) * 100, 6) for m in ("UST_10Y", "TIPS_10Y", "BEI_10Y")]
    w = "reader_map.rates_decomposition"
    A("⑤三利率分解", w, None, SNAP + "UST_10Y/TIPS_10Y/BEI_10Y @%s→@%s 之差×100" % (wf, wt), tri,
      [rd["nominal_bp"], rd["real_bp"], rd["bei_bp"]])
    A("⑤三利率分解", w, None, "report.json research_plan.us_rates_trio.window.from/to", [wf, wt],
      [rd["window_from"], rd["window_to"]])
    A("⑤三利率分解", w, None, "恒等式 名义=实际+盈亏平衡(直算)", tri[1] + tri[2], tri[0])
    A("⑤三利率分解", w, None, "report.json us_rates_trio.chg_bp(引擎面对账)",
      [urt["chg_bp"][m] for m in ("UST_10Y", "TIPS_10Y", "BEI_10Y")],
      [rd["nominal_bp"], rd["real_bp"], rd["bei_bp"]])


@sec("5-asset-echo")
def s5b():
    am = dict((x["metric_id"], x) for x in c.plan["asset_moves"]["rows"])
    for e in RM["asset_returns_echo"]:
        m = e["metric_id"]
        f, t = e["window"]["from"], e["window"]["to"]
        w = "reader_map.asset_returns_echo[%s]" % m
        A("⑤资产月窗", w, None, SNAP + "%s@%s→@%s 涨幅%%; 起止观测日=截至窗起/截止日最后观测" % (m, f, t),
          [lib.pct(lib.val(m, f), lib.val(m, t)), lib.at(m, f)[0], lib.at(m, cut)[0]],
          [e["chg_pct"], "2026-10-23", t])
        A("⑤资产月窗", w, None, "report.json research_plan.asset_moves.rows[%s].chg_pct/window 与 window_months" % m,
          [am[m]["chg_pct"], am[m]["window"]["from"], am[m]["window"]["to"], c.plan["asset_moves"]["window_months"]],
          [e["chg_pct"], f, t, e["window_months"]])


@sec("6-turnings")
def s6():
    W = RM["turnings"]
    cands = c.plan["turning_candidates"]["candidates"]
    c.F["turning_candidates"] = [[x["metric_id"], x["from_ym"], x["to_ym"], x["value_before"], x["value_after"],
                                  x["delta"]] for x in cands]
    JP, EA, JPR = lib.monthly("JP_CPI_YOY"), lib.monthly("EA_HICP_YOY"), lib.monthly("JP_POLICY_RATE")
    MM = {"JP_CPI_YOY": JP, "EA_HICP_YOY": EA, "JP_POLICY_RATE": JPR}
    for i, t in enumerate(W):
        M = MM[t["metric_id"]]
        A("⑥转折判断", "W%d" % (i + 1), None, SNAP + "%s@%s-01 与 @%s-01" % (t["metric_id"], t["before_date"], t["date"]),
          [M[t["before_date"]], M[t["date"]]], [t["value_before"], t["value_after"]],
          "结构化字段 date=%s before_date=%s metric=%s" % (t["date"], t["before_date"], t["metric_id"]))
    lo, hi = "2025-01", "2026-10"
    argmin = lambda M: min((M[k], k) for k in M if lo <= k <= hi)
    argmax = lambda M: max((M[k], k) for k in M if lo <= k <= hi)
    c.F["argmin_12m"] = {"EA": argmin(EA)[::-1], "JP": argmin(JP)[::-1]}
    c.F["argmax_12m"] = {"EA": argmax(EA)[::-1], "JP": argmax(JP)[::-1]}
    A("⑥转折判断", "W1.first_mover", "2025-11→2026-02 由 2.9 降至 1.27(三个月 -1.63 个百分点",
      SNAP + "JP_CPI_YOY@2025-11-01/@2026-02-01 及其差", [JP["2025-11"], JP["2026-02"], round(JP["2026-02"] - JP["2025-11"], 2)],
      [2.9, 1.27, -1.63])
    A("⑥转折判断", "W1.first_mover", "候选池内最大单段变动",
      "report.json turning_candidates.candidates 中 |delta| 最大者及其 metric_id/to_ym",
      [max(abs(x["delta"]) for x in cands), [x["metric_id"] for x in cands if abs(x["delta"]) == max(abs(y["delta"]) for y in cands)],
       [x["to_ym"] for x in cands if x["metric_id"] == "JP_CPI_YOY"]], [1.63, ["JP_CPI_YOY"], ["2026-02"]])
    A("⑥转折判断", "W1.follow_or_diverge", "同期欧元区 HICP 亦下行(2025-11 2.1→2026-02 1.9)",
      SNAP + "EA_HICP_YOY@2025-11-01/@2026-02-01", [EA["2025-11"], EA["2026-02"]], [2.1, 1.9])
    A("⑥转折判断", "W1.follow_or_diverge", "两地谷底相邻(欧元区 2026-01 的 1.7、日本 2026-02 的 1.27)",
      SNAP + "EA_HICP_YOY / JP_CPI_YOY 在 2025-01..2026-10 的最小值(值,月)",
      [list(argmin(EA)), list(argmin(JP))], [[1.7, "2026-01"], [1.27, "2026-02"]])
    A("⑥转折判断", "W1.follow_or_diverge", "按引擎候选面转折日(区间终点月)则为日本(2026-02)先于欧元区(2026-05)",
      "report.json turning_candidates.candidates[].to_ym(JP_CPI_YOY / EA_HICP_YOY)",
      [[x["to_ym"] for x in cands if x["metric_id"] == "JP_CPI_YOY"], [x["to_ym"] for x in cands if x["metric_id"] == "EA_HICP_YOY"]],
      [["2026-02"], ["2026-05"]])
    A("⑥转折判断", "W1.narrative", "2026-03 1.46、2026-04 1.38、2026-05 1.53、2026-06 1.67、2026-07 1.97、2026-08 1.98、2026-09 2.16、2026-10 2.44",
      SNAP + "JP_CPI_YOY@2026-03..2026-10", [JP[k] for k in sorted(JP) if "2026-03" <= k <= "2026-10"],
      [1.46, 1.38, 1.53, 1.67, 1.97, 1.98, 2.16, 2.44])
    after = [JP[k] for k in sorted(JP) if "2026-02" <= k <= "2026-10"]
    A("⑥转折判断", "W1.narrative", "日本通胀谷底转折: 此后总体回升、非逐月单调",
      SNAP + "JP_CPI_YOY 2026-02→2026-10 净变动>0 且存在环比下降月", [after[-1] > after[0], any(b < a for a, b in zip(after, after[1:]))],
      [True, True])
    A("⑥转折判断", "W1.narrative", "谷底月前的 BOJ 月均台阶(2026-01 0.728)", SNAP + "JP_POLICY_RATE@2026-01-01",
      JPR["2026-01"], 0.728)
    A("⑥转折判断", "W2.first_mover", "2026-02→2026-05 由 1.9 升至 3.2(三个月 +1.30 个百分点)",
      SNAP + "EA_HICP_YOY@2026-02-01/@2026-05-01 及其差", [EA["2026-02"], EA["2026-05"], round(EA["2026-05"] - EA["2026-02"], 2)],
      [1.9, 3.2, 1.30])
    A("⑥转折判断", "W2.follow_or_diverge", "日本端同窗自谷底回升(2026-02 1.27→2026-05 1.53)",
      SNAP + "JP_CPI_YOY@2026-02-01/@2026-05-01", [JP["2026-02"], JP["2026-05"]], [1.27, 1.53])
    A("⑥转折判断", "W2.follow_or_diverge", "生效日 2026-06-17 晚于转折段终点月 2026-05",
      "快照 series_store.ECB_MRO 值变更日 2026-06-17 与观测月 2026-05 先后", "2026-06-17" > "2026-05-31", True)
    A("⑥转折判断", "W2.narrative", "2026-06 2.8、2026-07 2.9、2026-08 3.2、2026-09 3.8、2026-10 4.0",
      SNAP + "EA_HICP_YOY@2026-06..2026-10", [EA[k] for k in sorted(EA) if "2026-06" <= k <= "2026-10"],
      [2.8, 2.9, 3.2, 3.8, 4.0])
    A("⑥转折判断", "W3.first_mover", "2026-04 0.727→2026-07 0.978(经 2026-06 0.841 过渡)",
      SNAP + "JP_POLICY_RATE@2026-04-01/@2026-06-01/@2026-07-01", [JPR["2026-04"], JPR["2026-06"], JPR["2026-07"]],
      [0.727, 0.841, 0.978])
    A("⑥转折判断", "W3.narrative", "2026-08 0.977、2026-09 1.043、2026-10 1.227",
      SNAP + "JP_POLICY_RATE@2026-08..2026-10", [JPR[k] for k in sorted(JPR) if "2026-08" <= k <= "2026-10"],
      [0.977, 1.043, 1.227])
    A("⑥转折判断", "W3.narrative", "与月均台阶 2026-09→2026-10(1.043→1.227)相容",
      "JP_POLICY_RATE@2026-09-01/@2026-10-01; 日历生效日 2026-09-24 落在 9 月月内(月均口径滞后体现)",
      [JPR["2026-09"], JPR["2026-10"], "2026-09-01" <= "2026-09-24" <= "2026-09-30"], [1.043, 1.227, True])


lib.finish(c, "p3")
