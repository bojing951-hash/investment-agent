# -*- coding: utf-8 -*-
"""Part 4a: section (7) mechanism chain M1 steps 1-4 (numbers routed back to the frozen snapshot).
usage: python3 -I s7_p4a.py <run_dir> <install_tree> <out_dir>"""
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
K = "⑦传导链"
cut = c.cutoff


def sec(name):
    def d(f):
        try:
            f()
        except Exception:
            c.errors.append({"section": name, "trace": traceback.format_exc()[-900:]})
    return lambda f: (d(f), f)[1]


@sec("7-step1")
def a():
    EA, JP = lib.monthly("EA_HICP_YOY"), lib.monthly("JP_CPI_YOY")
    A(K, "M1.step1", "EA_HICP_YOY 2026-02 的 1.9 升至 2026-05 的 3.2", SNAP + "EA_HICP_YOY@2026-02-01/@2026-05-01",
      [EA["2026-02"], EA["2026-05"]], [1.9, 3.2])
    A(K, "M1.step1", "(2026-06 一度回落至 2.8)", SNAP + "EA_HICP_YOY@2026-06-01", EA["2026-06"], 2.8)
    A(K, "M1.step1", "2026-10 达 4.0", SNAP + "EA_HICP_YOY@2026-10-01", EA["2026-10"], 4.0)
    A(K, "M1.step1", "JP_CPI_YOY 自 2025-01 的局部高点 4.03 回落", SNAP + "JP_CPI_YOY@2025-01-01", JP["2025-01"], 4.03)
    after = [v for k, v in sorted(JP.items()) if "2025-02" <= k <= "2026-10"]
    A(K, "M1.step1", "此后至最新观测月未再越过", SNAP + "JP_CPI_YOY 2025-02..2026-10 最大值及其是否 <4.03",
      [max(after), max(after) < 4.03], [3.66, True])
    mx = max((v, k) for k, v in JP.items())
    A(K, "M1.step1", "全序列最高为 2023-01 的 4.31", SNAP + "JP_CPI_YOY 全序列最大值(月,值)", [mx[1], mx[0]],
      ["2023-01", 4.31])
    A(K, "M1.step1", "2025-09、2025-10 两度小幅回升至 2.91、2.99", SNAP + "JP_CPI_YOY@2025-09-01/@2025-10-01",
      [JP["2025-09"], JP["2025-10"]], [2.91, 2.99])
    seg = [k for k in sorted(JP) if "2025-01" <= k <= "2026-02"]
    A(K, "M1.step1", "非逐月单调", SNAP + "JP_CPI_YOY 2025-01..2026-02 环比上升的月份",
      [b for x, b in zip(seg, seg[1:]) if JP[b] > JP[x]], ["2025-09", "2025-10"])
    A(K, "M1.step1", "经 2025-07 的 3.1 至 2026-02 的 1.27", SNAP + "JP_CPI_YOY@2025-07-01/@2026-02-01",
      [JP["2025-07"], JP["2026-02"]], [3.1, 1.27])
    A(K, "M1.step1", "此后总体回升至 2026-10 的 2.44", SNAP + "JP_CPI_YOY@2026-10-01(及是否高于 2026-02)",
      [JP["2026-10"], JP["2026-10"] > JP["2026-02"]], [2.44, True])
    calc = c.REGM["JP_CPI_YOY"]["calc"]
    A(K, "M1.step1", "JP_CPI_YOY 为注册表 2025基/2020基 拼接 同月同比(新基优先,重叠差>0.10pp 告警)",
      "metric_registry metrics[JP_CPI_YOY].calc",
      ["2025基" in calc, "2020基" in calc, "拼接(新基优先,重叠差>0.10pp 告警)" in calc], [True, True, True])


@sec("7-step2")
def b():
    def chg(m, d):
        x = [y for y in lib.changes(m, "1900-01-01", cut) if y[0] == d][0]
        return [round(x[1], 4), round(x[2], 4)]
    A(K, "M1.step2", "ECB 两次变更各 25bp: 2026-06-17 生效,MRO 2.15→2.4、DFR 2.0→2.25",
      SNAP + "ECB_MRO/ECB_DFR 2026-06-17 变更前→变更后", chg("ECB_MRO", "2026-06-17") + chg("ECB_DFR", "2026-06-17"),
      [2.15, 2.4, 2.0, 2.25])
    A(K, "M1.step2", "2026-09-16 生效,MRO 2.4→2.65、DFR 2.25→2.5",
      SNAP + "ECB_MRO/ECB_DFR 2026-09-16 变更前→变更后", chg("ECB_MRO", "2026-09-16") + chg("ECB_DFR", "2026-09-16"),
      [2.4, 2.65, 2.25, 2.5])
    A(K, "M1.step2", "冻结发布日历无 ECB 实录,发布面=序列变更日", "release_calendar 含 ECB 条目数; 两序列末观测日=末变更日",
      [len(c.ECBENT)] + [lib.at(m, cut)[0] == lib.changes(m, "1900-01-01", cut)[-1][0] for m in ("ECB_MRO", "ECB_DFR")],
      [0, True, True])
    tg = [x for x in c.cent("JP_POLICY_TARGET") if x.get("kind") == "policy_decision"][-1]
    A(K, "M1.step2", "BOJ 2026-09-18 决议(2026-09-24 生效)目标约 1.25%(发布日历实录)",
      "release_calendar entries[RC-JP-BOJ-TARGET-2026-09].decision_date/effective_on/target_value",
      [tg["decision_date"], tg["effective_on"], tg["target_value"]], ["2026-09-18", "2026-09-24", 1.25])
    A(K, "M1.step2", "2026-10-30 会议确认维持", "release_calendar entries[RC-JP-BOJ-MAINT-2026-10].decision_date",
      [x["decision_date"] for x in c.cent("JP_POLICY_TARGET") if x.get("kind") == "policy_maintenance"], ["2026-10-30"])
    JPR = lib.monthly("JP_POLICY_RATE")
    A(K, "M1.step2", "JP_POLICY_RATE 2026-09→2026-10 的台阶(1.043→1.227)", SNAP + "JP_POLICY_RATE@2026-09-01/@2026-10-01",
      [JPR["2026-09"], JPR["2026-10"]], [1.043, 1.227])
    nch = [x for x in lib.changes("JP_POLICY_RATE", "2025-11-01", cut) if round((x[2] - x[1]) * 100) != 0]
    c.F["jpr_strict_n"] = len(lib.changes("JP_POLICY_RATE", "2025-11-01", cut))
    jc = [x for x in c.cent("JP_POLICY_TARGET") if x.get("kind") != "policy_maintenance"]
    A(K, "M1.step2", "其余月均台阶在发布日历无对应实录", "近 12 个月 JP_POLICY_RATE 月均变动点数(整数 bp 非零;严格不等比较另含两次 -0.1bp 舍入伪变动) vs 日历中改变目标的 JP 条目数",
      [len(nch), len(jc)], [6, 1])


@sec("7-step3")
def d():
    eu, uj, dx = "EURUSD", "USDJPY", "DXY"
    A(K, "M1.step3", "MRO 2.65% vs BOJ 目标约 1.25%", SNAP + "ECB_MRO@2026-09-16; 日历 target_value",
      [lib.val("ECB_MRO", "2026-09-16"), 1.25], [2.65, 1.25])
    fl = [lib.at("DFEDTARL", cut), lib.at("DFEDTARU", cut)]
    c.F["fed_target"] = fl
    A(K, "M1.step3", "联邦基金目标区间 3.75%–4.00%,DFEDTARL/DFEDTARU 2026-11-23 观测", SNAP + "DFEDTARL/DFEDTARU 截至 2026-11-23 最后观测(日,值)",
      [[x[0], round(x[1], 4)] for x in fl], [["2026-11-23", 3.75], ["2026-11-23", 4.0]])
    A(K, "M1.step3", "不在本轮证据索引", "report.json evidence_index 中 DFEDTARL/DFEDTARU 行数",
      sum(1 for k in c.EVI if k.split("@")[0] in ("DFEDTARL", "DFEDTARU")), 0)
    u = lib.at("UST_10Y", cut)
    A(K, "M1.step3", "UST_10Y 最新 5.04%", SNAP + "UST_10Y 截至 2026-11-23 最后观测(值;观测日见注)", round(u[1], 2), 5.04, "观测日 " + u[0])

    def cross(mdate):
        return lib.val(eu, mdate) * lib.val(uj, mdate)
    x0, x1, x2 = cross("2026-10-23"), cross("2026-11-20"), cross(cut)
    c.F["legs"] = [[md, lib.val(eu, md), lib.val(uj, md)] for md in ("2026-05-22", "2026-10-23", "2026-11-20", cut)]
    A(K, "M1.step3", "2026-10-23 收盘 175.61→2026-11-20 收盘 175.19(-0.24%)",
      SNAP + "EURUSD×USDJPY 同日相乘 @2026-10-23/@2026-11-20 及涨跌幅%", [x0, x1, lib.pct(x0, x1)], [175.61, 175.19, -0.24])
    A(K, "M1.step3", "至 2026-11-23 盘中 174.32(较 10-23 -0.73%)", SNAP + "EURUSD×USDJPY @2026-11-23 及较 10-23 涨跌幅%",
      [x2, lib.pct(x0, x2)], [174.32, -0.73])
    A(K, "M1.step3", "合成交叉盘由 184.80 降至 175.19(-5.20%;腿: EURUSD -5.61%、USDJPY +0.43%)",
      SNAP + "EURUSD/USDJPY@2026-05-22→@2026-11-20(合成交叉盘起止与涨跌幅%,两腿涨跌幅%)",
      [cross("2026-05-22"), x1, lib.pct(cross("2026-05-22"), x1), lib.pct(lib.val(eu, "2026-05-22"), lib.val(eu, "2026-11-20")),
       lib.pct(lib.val(uj, "2026-05-22"), lib.val(uj, "2026-11-20"))], [184.80, 175.19, -5.20, -5.61, 0.43])
    JPR = lib.monthly("JP_POLICY_RATE")
    A(K, "M1.step3", "减日本政策利率 2026-05 月均 0.727% 得 1.423 个百分点", "MRO 2.15(2026-06-17 变更前) − JP_POLICY_RATE@2026-05",
      [JPR["2026-05"], round(2.15 - JPR["2026-05"], 3)], [0.727, 1.423])
    A(K, "M1.step3", "减 2026-10 月均 1.227% 得 1.423 个百分点", "MRO 2.65 − JP_POLICY_RATE@2026-10",
      round(2.65 - JPR["2026-10"], 3), 1.423)
    A(K, "M1.step3", "欧央行两度上调合计 0.5 个百分点、日本政策利率月均亦抬升 0.5 个百分点",
      "MRO 窗内变更点变动之和; JP_POLICY_RATE@2026-10 − @2026-04",
      [round(sum(z[2] - z[1] for z in lib.changes("ECB_MRO", "2026-05-23", cut)), 4), round(JPR["2026-10"] - JPR["2026-04"], 3)],
      [0.5, 0.5])

    def leg3(m, f, t):
        return [lib.val(m, f), lib.val(m, t), lib.pct(lib.val(m, f), lib.val(m, t))]
    A(K, "M1.step3", "EURUSD 由 1.1221 降至 1.0970(-2.24%)、USDJPY 由 156.494 升至 159.707(+2.05%)、DXY 由 101.81 升至 103.81(+1.96%)",
      SNAP + "EURUSD/USDJPY/DXY@2026-10-23→@2026-11-20(起,止,涨跌幅%)",
      leg3(eu, "2026-10-23", "2026-11-20") + leg3(uj, "2026-10-23", "2026-11-20") + leg3(dx, "2026-10-23", "2026-11-20"),
      [1.1221, 1.0970, -2.24, 156.494, 159.707, 2.05, 101.81, 103.81, 1.96])
    A(K, "M1.step3", "EURUSD 1.0940(-2.51%)、USDJPY 159.347(+1.82%)、DXY 104.079(+2.23%)",
      SNAP + "EURUSD/USDJPY/DXY@2026-10-23→@2026-11-23(起,止,涨跌幅%)",
      leg3(eu, "2026-10-23", cut) + leg3(uj, "2026-10-23", cut) + leg3(dx, "2026-10-23", cut),
      [1.1221, 1.0940, -2.51, 156.494, 159.347, 1.82, 101.81, 104.079, 2.23])


@sec("7-step4")
def e():
    IX = ("SPX", "NIKKEI225", "DAX", "CAC40")
    A(K, "M1.step4", "SPX 下跌 9.36%、NIKKEI225 下跌 9.98%、DAX 下跌 1.50%、CAC40 上涨 1.86%",
      SNAP + "SPX/NIKKEI225/DAX/CAC40@2026-10-23→@2026-11-20 涨跌幅%",
      [lib.pct(lib.val(m, "2026-10-23"), lib.val(m, "2026-11-20")) for m in IX], [-9.36, -9.98, -1.50, 1.86])
    A(K, "M1.step4", "VIX 由 19.45 升至 35.89(+84.5%)", SNAP + "VIX@2026-10-23/@2026-11-20",
      [lib.val("VIX", "2026-10-23"), lib.val("VIX", "2026-11-20"), lib.pct(lib.val("VIX", "2026-10-23"), lib.val("VIX", "2026-11-20"))],
      [19.45, 35.89, 84.5])
    vd = ["2026-11-13", "2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19", "2026-11-20"]
    A(K, "M1.step4", "11-13 19.30→11-16 22.91→11-17 25.46→11-18 24.56→11-19 28.44→11-20 35.89",
      SNAP + "VIX@2026-11-13..2026-11-20", [lib.val("VIX", d) for d in vd], [19.30, 22.91, 25.46, 24.56, 28.44, 35.89])
    A(K, "M1.step4", "末六个交易日收盘路径", SNAP + "VIX 截至 2026-11-20 的最后 6 个观测日",
      [d for d, _ in lib.series("VIX") if d <= "2026-11-20"][-6:], vd)
    n = "SPX -5.51%(7203.85,盘中)、DAX +0.11%(25209.45,盘中)、NIKKEI225 -9.98%(56436.65,2026-11-20 收盘)、VIX +38.87%(27.01,盘中"

    def mv(m):
        t = lib.at(m, cut)
        return [lib.pct(lib.val(m, "2026-10-23"), t[1]), round(t[1], 2), t[0]]
    A(K, "M1.step4", n, SNAP + "SPX/DAX/NIKKEI225/VIX@2026-10-23→截至截止日最后观测(涨跌幅%,末值,观测日)",
      mv("SPX") + mv("DAX") + mv("NIKKEI225") + mv("VIX"),
      [-5.51, 7203.85, cut, 0.11, 25209.45, cut, -9.98, 56436.65, "2026-11-20", 38.87, 27.01, cut])
    A(K, "M1.step4", "较 2026-11-20 收盘 -24.7%", SNAP + "VIX@2026-11-23 对 @2026-11-20 涨跌幅%",
      lib.pct(lib.val("VIX", "2026-11-20"), lib.val("VIX", cut)), -24.7)
    A(K, "M1.step4", "2026-11-04→11-05 VIX 收盘 16.61→28.18(+69.66%)", SNAP + "VIX@2026-11-04/@2026-11-05",
      [lib.val("VIX", "2026-11-04"), lib.val("VIX", "2026-11-05"), lib.pct(lib.val("VIX", "2026-11-04"), lib.val("VIX", "2026-11-05"))],
      [16.61, 28.18, 69.66])
    nobs = [d for d, _ in lib.series("VIX") if "2026-11-05" < d <= "2026-11-11"]
    A(K, "M1.step4", "至 11-11 回落至 17.49(四个交易日,较 11-05 -37.93%)",
      SNAP + "VIX@2026-11-11; 2026-11-05 之后至 11-11 观测数; 较 11-05 涨跌幅%",
      [lib.val("VIX", "2026-11-11"), len(nobs), lib.pct(lib.val("VIX", "2026-11-05"), lib.val("VIX", "2026-11-11"))],
      [17.49, 4, -37.93])
    A(K, "M1.step4", "同期 SPX 11-05 -4.36%,下一交易日 NIKKEI225 11-06 -5.96%", SNAP + "SPX@2026-11-04→11-05; NIKKEI225@2026-11-05→11-06",
      [lib.pct(lib.val("SPX", "2026-11-04"), lib.val("SPX", "2026-11-05")),
       lib.pct(lib.val("NIKKEI225", "2026-11-05"), lib.val("NIKKEI225", "2026-11-06"))], [-4.36, -5.96])

    def dchg(m, d):
        p = lib.prevobs(m, d)
        return lib.pct(p[1], lib.val(m, d))
    vdaily = dict((d, dchg("VIX", d)) for d in vd[1:])
    c.F["vix_daily"] = dict((k, round(v, 4)) for k, v in vdaily.items())
    top2 = [k for k, _ in sorted(vdaily.items(), key=lambda kv: -kv[1])[:2]]
    A(K, "M1.step4", "当日 VIX +18.70%/+26.20%,为窗内两个最大单日跳升日", SNAP + "VIX 2026-11-16/11-20 单日涨跌幅%; 窗内单日涨幅前二",
      [vdaily["2026-11-16"], vdaily["2026-11-20"], top2], [18.70, 26.20, ["2026-11-20", "2026-11-16"]])
    A(K, "M1.step4", "2026-11-13→2026-11-20: SPX -8.61%、NIKKEI225 -7.70%、DAX -7.28%、CAC40 -5.27%",
      SNAP + "四股指@2026-11-13→@2026-11-20 涨跌幅%",
      [lib.pct(lib.val(m, "2026-11-13"), lib.val(m, "2026-11-20")) for m in IX], [-8.61, -7.70, -7.28, -5.27])
    fx = [dchg("EURUSD", "2026-11-16"), dchg("EURUSD", "2026-11-20"), dchg("USDJPY", "2026-11-16"), dchg("USDJPY", "2026-11-20")]
    A(K, "M1.step4", "两日欧元、日元对美元单日变动幅度不超过 0.23%", SNAP + "EURUSD/USDJPY 2026-11-16 与 11-20 单日涨跌幅%的最大绝对值≤0.235",
      max(abs(x) for x in fx) <= 0.235, True, "四值%%=%s" % [round(x, 4) for x in fx])
    mins = dict(((m, d), dchg(m, d)) for m in IX for d in vd[1:])
    worst = min(mins.items(), key=lambda kv: kv[1])
    A(K, "M1.step4", "单日看 2026-11-20 NIKKEI225 -5.06% 深于 SPX -3.70%", SNAP + "NIKKEI225/SPX@2026-11-20 单日涨跌幅%",
      [dchg("NIKKEI225", "2026-11-20"), dchg("SPX", "2026-11-20")], [-5.06, -3.70])
    A(K, "M1.step4", "为窗内四地最大单日跌幅", SNAP + "四股指 11-13..11-20 单日涨跌幅最小值(指标,日)",
      [worst[0][0], worst[0][1]], ["NIKKEI225", "2026-11-20"])
    pdf = c.plan["policy_doc_facts"]
    A(K, "M1.step4", "FOMC 2026年10月会议纪要 2026-11-18 发布", "report.json research_plan.policy_doc_facts[0].{title,published_on}",
      [pdf[0]["title"], pdf[0]["published_on"]], ["FOMC 2026年10月会议纪要", "2026-11-18"])


lib.finish(c, "p4a")
