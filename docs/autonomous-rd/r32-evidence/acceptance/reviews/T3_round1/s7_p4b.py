# -*- coding: utf-8 -*-
"""Part 4b: reader_map (headline, region from_to, three transmission links).
usage: python3 -I s7_p4b.py <run_dir> <install_tree> <out_dir>"""
import importlib.util
import json
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
K = "⑦传导链(reader_map)"
cut = c.cutoff
JP, EA, TK = lib.monthly("JP_CPI_YOY"), lib.monthly("EA_HICP_YOY"), lib.monthly("JP_CPI_TOKYO_YOY")
JPR = lib.monthly("JP_POLICY_RATE")


def sec(name):
    def d(f):
        try:
            f()
        except Exception:
            c.errors.append({"section": name, "trace": traceback.format_exc()[-900:]})
    return lambda f: (d(f), f)[1]


def vis(ym_of, date, k):
    ok = [ym for ym in EA if lib.rule_pub(ym, k) <= date]
    return max(ok)


def vis2(date):
    ok = [ym for ym in EA if lib.first_next(ym) <= date]
    return max(ok)


@sec("rm-headline")
def h():
    A(K, "HC", "日本全国 CPI 同比最新读数 2.44%(观测 2026-10,发布 2026-11-20,推定规则)", SNAP + "JP_CPI_YOY@2026-10-01", JP["2026-10"], 2.44)
    A(K, "HC", "低于去年同月(2025-10 为 2.99)", SNAP + "JP_CPI_YOY@2025-10-01", JP["2025-10"], 2.99)
    A(K, "HC", "欧元区 HICP 同比 4.0%(观测 2026-10,推定终值发布日 2026-11-16,推定规则)", SNAP + "EA_HICP_YOY@2026-10-01", EA["2026-10"], 4.0)
    A(K, "HC", "高于去年同月(2025-10 为 2.1)", SNAP + "EA_HICP_YOY@2025-10-01", EA["2025-10"], 2.1)
    A(K, "HC", "较六个月前锚两地读数均上行", SNAP + "JP_CPI_YOY/EA_HICP_YOY 2026-10 减 2026-04 是否 >0",
      [JP["2026-10"] - JP["2026-04"] > 0, EA["2026-10"] - EA["2026-04"] > 0], [True, True])
    A(K, "HC", "依据月均市场利率台阶 0.478→1.227", SNAP + "JP_POLICY_RATE@2025-11-01/@2026-10-01", [JPR["2025-11"], JPR["2026-10"]], [0.478, 1.227])
    tg = [x for x in c.cent("JP_POLICY_TARGET") if x.get("kind") == "policy_decision"][-1]
    mt = [x for x in c.cent("JP_POLICY_TARGET") if x.get("kind") == "policy_maintenance"][-1]
    A(K, "HC", "日本央行政策目标约 1.25%(2026-09-18 决议、2026-09-24 生效,2026-10-30 确认维持",
      "release_calendar: target_value/decision_date/effective_on/维持条目 decision_date",
      [tg["target_value"], tg["decision_date"], tg["effective_on"], mt["decision_date"]], [1.25, "2026-09-18", "2026-09-24", "2026-10-30"])
    A(K, "HC", "欧央行主要再融资利率 2.65%/存款便利利率 2.5%(2026-09-16 生效;决议日 2026-09-10",
      SNAP + "ECB_MRO/ECB_DFR@2026-09-16; 独立推算其前最近周四",
      [lib.val("ECB_MRO", "2026-09-16"), lib.val("ECB_DFR", "2026-09-16"), lib.thu_before("2026-09-16")], [2.65, 2.5, "2026-09-10"])
    cm = lib.changes("ECB_MRO", "2026-05-23", cut)
    A(K, "HC", "最近六个月两次同幅上调", SNAP + "ECB_MRO 窗内变更点(日,变动bp)", [[x[0] for x in cm], [round((x[2] - x[1]) * 100, 4) for x in cm]],
      [["2026-06-17", "2026-09-16"], [25.0, 25.0]])
    A(K, "HC", "惟欧央行序列止于 2026-09-16(距截止 68 天,Gate A 列 degraded)", SNAP + "ECB_MRO 末观测日; 距截止天数; gate_a.noncore_degraded",
      [lib.series("ECB_MRO")[-1][0], lib.days("2026-09-16", cut), "ECB_MRO" in json.dumps(c.ga.get("noncore_degraded"))], ["2026-09-16", 68, True])


@sec("rm-region-EA")
def e():
    A(K, "EA", "欧央行主要再融资利率(政策目标口径)由6个月前锚(观测 2025-06-11)的 2.15% 升至最新一期锚(观测 2026-09-16)的 2.65%",
      SNAP + "ECB_MRO 截至 2026-05-23 / 2026-11-23 的最后观测(日,值)",
      [lib.at("ECB_MRO", "2026-05-23"), lib.at("ECB_MRO", cut)], [["2025-06-11", 2.15], ["2026-09-16", 2.65]])
    A(K, "EA", "由 2.0% 升至 2.5%", SNAP + "ECB_DFR 截至 2026-05-23 / 2026-11-23 的最后观测值",
      [lib.at("ECB_DFR", "2026-05-23")[1], lib.at("ECB_DFR", cut)[1]], [2.0, 2.5])
    cd = lib.changes("ECB_DFR", "2026-05-23", cut)
    A(K, "EA", "两次变更(2026-06-17 生效、2026-09-16 生效,各 +25bp", SNAP + "ECB_DFR 窗内变更点(日,变动bp)",
      [[x[0] for x in cd], [round((x[2] - x[1]) * 100, 4) for x in cd]], [["2026-06-17", "2026-09-16"], [25.0, 25.0]])
    A(K, "EA", "HICP 同比由6个月前锚(观测月 2026-04)的 3.0% 至最新一期锚(观测月 2026-10)的 4.0%", SNAP + "EA_HICP_YOY@2026-04-01/@2026-10-01",
      [EA["2026-04"], EA["2026-10"]], [3.0, 4.0])
    A(K, "EA", "相比去年同月(2025-10 为 2.1)高 1.9 个百分点", "EA_HICP_YOY@2026-10 减 @2025-10", [EA["2025-10"], round(EA["2026-10"] - EA["2025-10"], 2)], [2.1, 1.9])
    A(K, "EA", "路径: 2026-01 谷底 1.7→2026-02 1.9→2026-05 3.2→2026-06 2.8→2026-10 4.0", SNAP + "EA_HICP_YOY@2026-01/02/05/06/10",
      [EA[k] for k in ("2026-01", "2026-02", "2026-05", "2026-06", "2026-10")], [1.7, 1.9, 3.2, 2.8, 4.0])
    w = [EA[k] for k in sorted(EA) if "2025-11" <= k <= "2026-10"]
    A(K, "EA", "最新读数为近十二个月最高", SNAP + "EA_HICP_YOY 2025-11..2026-10 最大值及是否等于 2026-10 值", [max(w), max(w) == EA["2026-10"]], [4.0, True])
    A(K, "EA", "发布 2026-11-16 为引擎推定规则下的终值日", "独立推算 2026-10-31+16天", lib.rule_pub("2026-10", 16), "2026-11-16")


@sec("rm-region-JP")
def j():
    A(K, "JP", "发布日历实录(v1.5.0,2026-11-21 更新)政策目标利率约 1.25%", "release_calendar.version/updated; target_value",
      [str(c.cal.get("version")).lstrip("v"), c.cal.get("updated"), 1.25], ["1.5.0", "2026-11-21", 1.25],
      "日历 version 字段=%r(无 v 前缀),受审稿写作 v1.5.0=书写差异" % c.cal.get("version"))
    A(K, "JP", "由6个月前锚(观测月 2026-04)的 0.727% 台阶升至最新一期锚(观测月 2026-10)的 1.227%", SNAP + "JP_POLICY_RATE@2026-04-01/@2026-10-01",
      [JPR["2026-04"], JPR["2026-10"]], [0.727, 1.227])
    strict = lib.changes("JP_POLICY_RATE", "2025-11-23", cut)
    ch = [x for x in strict if round((x[2] - x[1]) * 100) != 0]
    c.F["jpr_strict_vs_step"] = [len(strict), len(ch), [[x[0], round((x[2] - x[1]) * 100, 1)] for x in strict if round((x[2] - x[1]) * 100) == 0]]
    A(K, "JP", "近 12 个月月均由 2025-11 的 0.478 升至 2026-10 的 1.227,约 +75bp", SNAP + "JP_POLICY_RATE@2025-11-01/@2026-10-01 及差×100",
      [JPR["2025-11"], JPR["2026-10"], round((JPR["2026-10"] - JPR["2025-11"]) * 100)], [0.478, 1.227, 75],
      "未取整=74.9bp,受审稿『约 +75bp』(取整 bp)")
    pw = c.cells["JP_POLICY_RATE"].get("policy_window_path") or {}
    A(K, "JP", "净 +75bp=六个变动点之和,窗口 2025-11-23..2026-11-23", SNAP + "JP_POLICY_RATE 窗 (2025-11-23,2026-11-23] 变动点数与变动和(bp); 窗启时在值/窗末值",
      [len(ch), sum(round((x[2] - x[1]) * 100) for x in ch), round(sum(x[2] - x[1] for x in ch) * 100, 1), ch[0][1], ch[-1][2]], [6, 75, 75.1, 0.478, 1.227],
      "逐台阶整数 bp 之和=75; 未取整和=75.1bp; 窗启在值→窗末=74.9bp(月均三位小数舍入所致,『约 +75bp』成立)")
    A(K, "JP", "引擎政策一年窗路径同口径", "report.json point_values.cells[JP_POLICY_RATE].policy_window_path.{window,net_bp,window_start_value,window_end_value}",
      [pw.get("window"), pw.get("net_bp"), pw.get("window_start_value"), pw.get("window_end_value")], [["2025-11-23", "2026-11-23"], 75, 0.478, 1.227])
    A(K, "JP", "2026-09→2026-10 台阶(1.043→1.227)", SNAP + "JP_POLICY_RATE@2026-09-01/@2026-10-01", [JPR["2026-09"], JPR["2026-10"]], [1.043, 1.227])
    A(K, "JP", "全国 CPI 同比由6个月前锚(观测月 2026-04)的 1.38% 升至最新一期锚(观测月 2026-10)的 2.44%", SNAP + "JP_CPI_YOY@2026-04-01/@2026-10-01",
      [JP["2026-04"], JP["2026-10"]], [1.38, 2.44])
    A(K, "JP", "最新读数相比去年同月(2025-10 为 2.99)低 0.55 个百分点", "JP_CPI_YOY@2025-10 与 2026-10 之差(绝对值)",
      [JP["2025-10"], round(abs(JP["2026-10"] - JP["2025-10"]), 2)], [2.99, 0.55])
    A(K, "JP", "由6个月前锚观测月 2026-04 的 1.42% 升至最新一期锚观测月 2026-10 的 2.73%", SNAP + "JP_CPI_TOKYO_YOY@2026-04-01/@2026-10-01",
      [TK["2026-04"], TK["2026-10"]], [1.42, 2.73])


@sec("rm-link1")
def l1():
    A(K, "TL1.observed_fact", "EA_HICP_YOY 2026-02 1.9→2026-05 3.2→2026-10 4.0", SNAP + "EA_HICP_YOY@2026-02/05/10",
      [EA[k] for k in ("2026-02", "2026-05", "2026-10")], [1.9, 3.2, 4.0])
    A(K, "TL1.observed_fact", "JP_CPI_YOY 2026-02 1.27→2026-10 2.44", SNAP + "JP_CPI_YOY@2026-02-01/@2026-10-01", [JP["2026-02"], JP["2026-10"]], [1.27, 2.44])
    A(K, "TL1.main_predicts", "决议日(回推 2026-06-11)前可见 2026-04=3.0、生效日前可见 2026-05=3.2",
      "引擎规则(观测月末+16天)下 ≤2026-06-11 / ≤2026-06-17 已入档的最新观测月与值(读数=快照最新修订值)",
      [vis(None, "2026-06-11", 16), EA[vis(None, "2026-06-11", 16)], vis(None, "2026-06-17", 16), EA[vis(None, "2026-06-17", 16)]],
      ["2026-04", 3.0, "2026-05", 3.2])
    A(K, "TL1.main_predicts", "决议日(回推 2026-09-10)前可见 2026-07=2.9、生效日前可见 2026-08=3.2",
      "引擎规则下 ≤2026-09-10 / ≤2026-09-16 已入档的最新观测月与值",
      [vis(None, "2026-09-10", 16), EA[vis(None, "2026-09-10", 16)], vis(None, "2026-09-16", 16), EA[vis(None, "2026-09-16", 16)]],
      ["2026-07", 2.9, "2026-08", 3.2])
    A(K, "TL1.verdict_note", "发布日 2026-09-16 与生效日同日", "独立推算 2026-08 观测月的引擎发布日(月末+16天)", lib.rule_pub("2026-08", 16), "2026-09-16")
    m1 = lib.series("ECB_MRO")
    d1 = lib.series("ECB_DFR")
    A(K, "TL1.verdict_note", "两序列自 2025-06-11 至 2026-06-17 维持 2.15/2.0 共 371 天",
      SNAP + "ECB_MRO/ECB_DFR@2025-06-11(日,值); 开区间 (2025-06-11,2026-06-17) 内变更点数; 天数差",
      [lib.at("ECB_MRO", "2025-06-11"), lib.at("ECB_DFR", "2025-06-11"), len(lib.changes("ECB_MRO", "2025-06-11", "2026-06-16")),
       len(lib.changes("ECB_DFR", "2025-06-11", "2026-06-16")), lib.days("2025-06-11", "2026-06-17")],
      [["2025-06-11", 2.15], ["2025-06-11", 2.0], 0, 0, 371])
    A(K, "TL1.verdict_note", "其间读数已由 2026-01 的 1.7 升至 2026-04 的 3.0 而未触发变更", SNAP + "EA_HICP_YOY@2026-01-01/@2026-04-01",
      [EA["2026-01"], EA["2026-04"]], [1.7, 3.0])
    A(K, "TL1.verdict_note", "两次变更相隔 91 天、各 25bp", SNAP + "ECB_MRO 两变更点间隔天数与变动bp",
      [lib.days("2026-06-17", "2026-09-16"), [round((x[2] - x[1]) * 100, 4) for x in lib.changes("ECB_MRO", "2026-05-23", cut)]], [91, [25.0, 25.0]])
    A(K, "TL1.verdict_note", "第二次变更的决议日前可见读数 2.9 低于 2026-05 峰值 3.2", SNAP + "EA_HICP_YOY@2026-07-01/@2026-05-01",
      [EA["2026-07"], EA["2026-05"], EA["2026-07"] < EA["2026-05"]], [2.9, 3.2, True])
    A(K, "TL1.verdict_note", "两次变更决议日前可见读数为 2026-05 的 3.2 与 2026-08 的 3.2",
      "按日历两档形态(次月首日快报) ≤2026-06-11 / ≤2026-09-10 已发布的最新观测月与值(读数=快照最新修订值)",
      [vis2("2026-06-11"), EA[vis2("2026-06-11")], vis2("2026-09-10"), EA[vis2("2026-09-10")]], ["2026-05", 3.2, "2026-08", 3.2])


@sec("rm-link23")
def l23():
    eu, uj = "EURUSD", "USDJPY"
    x = lambda d: lib.val(eu, d) * lib.val(uj, d)
    A(K, "TL2.observed_fact", "由 2026-10-23 的约 175.61 降至 2026-11-20 的约 175.19(-0.24%)、2026-11-23 盘中约 174.32(-0.73%)",
      SNAP + "EURUSD×USDJPY@2026-10-23/@2026-11-20/@2026-11-23", [x("2026-10-23"), x("2026-11-20"), lib.pct(x("2026-10-23"), x("2026-11-20")), x(cut), lib.pct(x("2026-10-23"), x(cut))],
      [175.61, 175.19, -0.24, 174.32, -0.73])
    A(K, "TL2.verdict_note", "引擎面美元端利率高于两地", SNAP + "DFEDTARU/DFEDTARL@2026-11-23 与 MRO 2.65、BOJ 目标 1.25 的大小关系",
      [lib.at("DFEDTARL", cut)[1] > 2.65, 2.65 > 1.25], [True, True])
    c.F["fed_last_change"] = {m: lib.changes(m, "1900-01-01", cut)[-1] for m in ("DFEDTARL", "DFEDTARU")}
    A(K, "TL2.verdict_note", "美联储 2026-09-17 生效", SNAP + "DFEDTARL/DFEDTARU 最后值变更日",
      [lib.changes(m, "1900-01-01", cut)[-1][0] for m in ("DFEDTARL", "DFEDTARU")], ["2026-09-17", "2026-09-17"])
    A(K, "TL2.verdict_note", "窗内三地均无政策利率变动点", SNAP + "ECB_MRO/ECB_DFR/DFEDTARL/DFEDTARU 在 (2026-10-23,2026-11-20] 的变更点数; JP_POLICY_RATE 月值 2026-10→最新",
      [len(lib.changes(m, "2026-10-23", "2026-11-20")) for m in ("ECB_MRO", "ECB_DFR", "DFEDTARL", "DFEDTARU")] + [JPR[max(JPR)] == JPR["2026-10"] and max(JPR) <= "2026-11"],
      [0, 0, 0, 0, True])
    A(K, "TL3.competing_explanation", "VIX +84.5% 的单月幅度", SNAP + "VIX@2026-10-23→@2026-11-20 涨跌幅%", lib.pct(lib.val("VIX", "2026-10-23"), lib.val("VIX", "2026-11-20")), 84.5)
    A(K, "TL3.observed_fact", "跳升集中于末五个交易日(2026-11-13→2026-11-20,19.30→35.89)", SNAP + "VIX 2026-11-13 之后至 11-20 的观测数; 两值",
      [len([d for d, _ in lib.series("VIX") if "2026-11-13" < d <= "2026-11-20"]), lib.val("VIX", "2026-11-13"), lib.val("VIX", "2026-11-20")], [5, 19.30, 35.89])
    A(K, "TL3.verdict_note", "DAX -1.50%、CAC40 +1.86% vs SPX -9.36%", SNAP + "DAX/CAC40/SPX@2026-10-23→@2026-11-20 涨跌幅%",
      [lib.pct(lib.val(m, "2026-10-23"), lib.val(m, "2026-11-20")) for m in ("DAX", "CAC40", "SPX")], [-1.50, 1.86, -9.36])
    A(K, "TL3.verdict_note", "日本端与美股相当(-9.98%)", SNAP + "NIKKEI225@2026-10-23→@2026-11-20 涨跌幅%",
      lib.pct(lib.val("NIKKEI225", "2026-10-23"), lib.val("NIKKEI225", "2026-11-20")), -9.98)
    A(K, "TL3.verdict_note", "距最近政策日 2026-10-30(BOJ 维持决议,无变更)14 天、距 ECB 最近生效日 2026-09-16 58 天", "独立推算天数差(自 2026-11-13)",
      [lib.days("2026-10-30", "2026-11-13"), lib.days("2026-09-16", "2026-11-13")], [14, 58])
    A(K, "TL3.verdict_note", "至跳升终点 2026-11-20 为 21 天、65 天", "独立推算天数差(自 2026-11-20)",
      [lib.days("2026-10-30", "2026-11-20"), lib.days("2026-09-16", "2026-11-20")], [21, 65])
    A(K, "TL3.verdict_note", "发布当日及其后两个交易日 VIX 收盘 24.56、28.44、35.89", SNAP + "VIX@2026-11-18/19/20",
      [lib.val("VIX", d) for d in ("2026-11-18", "2026-11-19", "2026-11-20")], [24.56, 28.44, 35.89])
    A(K, "TL3.verdict_note", "2026-11-23 快照 27.01,较 2026-11-20 收盘 -24.7%", SNAP + "VIX@2026-11-23 与对 11-20 涨跌幅%",
      [lib.val("VIX", cut), lib.pct(lib.val("VIX", "2026-11-20"), lib.val("VIX", cut))], [27.01, -24.7])
    c.F["policy_event_clusters"] = c.plan.get("policy_event_clusters")


lib.finish(c, "p4b")
