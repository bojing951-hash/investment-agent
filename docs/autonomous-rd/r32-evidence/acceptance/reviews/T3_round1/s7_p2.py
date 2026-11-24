# -*- coding: utf-8 -*-
"""Part 2: section (4) policy face (C2/C3) + (11) honest absence + (13') central-bank target rates.
usage: python3 -I s7_p2.py <run_dir> <install_tree> <out_dir>"""
import importlib.util
import json
import os
import re
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
CAT = "④政策面"


def shift(ym, k):
    y, m = int(ym[:4]), int(ym[5:7])
    m += k
    while m < 1:
        m += 12
        y -= 1
    while m > 12:
        m -= 12
        y += 1
    return "%04d-%02d" % (y, m)


try:
    cut = c.cutoff
    mro, dfr = lib.series("ECB_MRO"), lib.series("ECB_DFR")

    def lastchg(m):
        ch = lib.changes(m, "1900-01-01", cut)
        d, v = lib.at(m, cut)
        return [d, round(v, 4), bool(ch) and ch[-1][0] == d]

    n = "欧央行主要再融资利率(ECB_MRO,政策目标口径)最新生效水平为 二点六五,观测=序列变更日=生效日 2026-09-16"
    A(CAT, "C2", n, SNAP + "ECB_MRO 截至 2026-11-23 最后观测(日,值,是否值变更日)", lastchg("ECB_MRO"),
      ["2026-09-16", 2.65, True])
    pf = json.dumps(c.plan, ensure_ascii=False)
    conv = sorted(set(re.findall(r"[^。;」』]{0,24}上一个周四[^。;」』]{0,24}", pf)))[:3]
    c.F["engine_convention_text"] = conv
    c.F["registry_ecb_release_semantics"] = c.REGM["ECB_MRO"]["release_semantics"]
    n = "决议日 2026-09-10 系引擎按『生效日前上一个周四』惯例自变更日回推"
    A(CAT, "C2", n, "独立推算: 2026-09-16 之前最近的周四; report.json research_plan 引擎惯例文本含『上一个周四』",
      [lib.thu_before("2026-09-16"), "上一个周四" in pf], ["2026-09-10", True])
    A(CAT, "C2", "冻结发布日历对欧央行无实录条目", "release_calendar.entries 中含 ECB/MRO/DFR/欧央行 的条目数",
      len(c.ECBENT), 0)
    n = "欧央行存款便利利率(ECB_DFR,操作下限口径)最新生效水平 2.5%,同一变更日(2026-09-16)"
    A(CAT, "C2", n, SNAP + "ECB_DFR 截至 2026-11-23 最后观测(日,值,是否值变更日)", lastchg("ECB_DFR"),
      ["2026-09-16", 2.5, True])
    n = "窗内两次上调(2026-06-17 与 2026-09-16 生效,各二十五个基点"
    cm, cd = lib.changes("ECB_MRO", "2026-05-23", cut), lib.changes("ECB_DFR", "2026-05-23", cut)
    A(CAT, "C2", n, SNAP + "ECB_MRO/ECB_DFR 在 (2026-05-23,2026-11-23] 的值变更点(日,变动百分点)",
      [[x[0] for x in cm], [round((x[2] - x[1]) * 100, 4) for x in cm], [x[0] for x in cd],
       [round((x[2] - x[1]) * 100, 4) for x in cd]],
      [["2026-06-17", "2026-09-16"], [25.0, 25.0], ["2026-06-17", "2026-09-16"], [25.0, 25.0]])
    n = "对应决议日 2026-06-11、2026-09-10 同为惯例回推【推断】"
    A(CAT, "C2", n, "独立推算: 各变更日之前最近的周四", [lib.thu_before("2026-06-17"), lib.thu_before("2026-09-16")],
      ["2026-06-11", "2026-09-10"])
    je = c.cent("JP_POLICY_TARGET")
    tg = [x for x in je if x.get("kind") == "policy_decision"][-1]
    mt = [x for x in je if x.get("kind") == "policy_maintenance"][-1]
    c.F["boj_entries"] = [[x["entry_id"], x.get("kind"), x.get("decision_date"), x.get("effective_on"),
                           x.get("target_value")] for x in je]
    c.F["boj_days_to_cutoff"] = [lib.days(tg["effective_on"], cut), lib.days(tg["decision_date"], cut),
                                 lib.days(mt["decision_date"], cut)]
    n = "政策目标利率(宣布值口径,发布日历最新实录·2026-11-21 更新)约一点二五,2026-09-18 决议、2026-09-24 生效"
    A(CAT, "C2", n, "release_calendar.updated; entries[RC-JP-BOJ-TARGET-2026-09].{target_value,decision_date,effective_on}",
      [c.cal["updated"], tg["target_value"], tg["decision_date"], tg["effective_on"]],
      ["2026-11-21", 1.25, "2026-09-18", "2026-09-24"], "生效日/决议日距截止(天)=%s" % c.F["boj_days_to_cutoff"])
    n = "2026-10-30 会议确认维持不变(无新调整、无生效变动)"
    A(CAT, "C2", n, "entries[RC-JP-BOJ-MAINT-2026-10].{kind,decision_date,target_value,有无 effective_on}",
      [mt.get("kind"), mt.get("decision_date"), mt.get("target_value"), "effective_on" in mt],
      ["policy_maintenance", "2026-10-30", 1.25, False])
    A(CAT, "C2", "实录无前值,属【推断】",
      "entries[RC-JP-BOJ-TARGET-2026-09] 中前值类字段名(prev/prior/old/before)",
      [k for k in tg if any(t in k.lower() for t in ("prev", "prior", "old", "before"))], [])
    JPR = lib.monthly("JP_POLICY_RATE")
    c.F["JPR"] = JPR
    n = "自 2025-11 月均零点四七八升至 2026-10 月均一点二二七"
    A(CAT, "C2", n, SNAP + "JP_POLICY_RATE@2025-11-01 与 @2026-10-01", [JPR["2025-11"], JPR["2026-10"]],
      [0.478, 1.227])
    A(CAT, "C2", "2026-10-30 至研究截止二十四天内", "独立推算: 2026-11-23 − 2026-10-30",
      lib.days("2026-10-30", cut), 24)
    n = "最新一期报 1.227%(观测月 2026-10,推定发布日 2026-11-05,L1 quality_status=WARN)"
    A(CAT, "C2", n, SNAP + "JP_POLICY_RATE 最新观测(月,值); 独立推算 2026-10-31+5天; L1 quality_status",
      [max(JPR), JPR["2026-10"], lib.rule_pub("2026-10", 5), c.l1("JP_POLICY_RATE")["quality_status"]],
      ["2026-10", 1.227, "2026-11-05", "WARN"])
    A(CAT, "C2", "六个月前锚前值为零点七二七", SNAP + "JP_POLICY_RATE@2026-04-01", JPR["2026-04"], 0.727)
    A(CAT, "C2", "月均口径非宣布值", "metric_registry metrics[JP_POLICY_RATE].release_semantics 含『月均 operative 利率而非决议值』",
      "月均 operative 利率而非决议值" in c.REGM["JP_POLICY_RATE"]["release_semantics"], True)
    n = "惟欧央行序列止于 2026-09-16(距截止六十八天)"
    A(CAT, "C2", n, SNAP + "ECB_MRO/ECB_DFR 末观测日; 独立推算距截止天数",
      [mro[-1][0], dfr[-1][0], lib.days("2026-09-16", cut)], ["2026-09-16", "2026-09-16", 68])
    pend = [x["entry_id"] for x in c.CENT
            if x.get("effective_on") and x.get("decision_date", "9999") <= cut < x["effective_on"]]
    c.F["pending_calendar"] = pend
    A(CAT, "C2", "无任何已决议而尚未生效的调整",
      "release_calendar.entries: decision_date≤2026-11-23 且 effective_on>2026-11-23 的条目; ECB 两序列窗内变更点数",
      [pend, len(cm), len(cd)], [[], 2, 2])
    A(CAT, "C2", "可核行动均已生效、无未生效决议",
      "release_calendar JP_POLICY_TARGET 条目: 2026-05-23 之后决议者的 effective_on 是否均 ≤ 截止日",
      [[x["entry_id"], x["effective_on"] <= cut] for x in je
        if x.get("effective_on") and x.get("decision_date", "") >= "2026-05-23"],
      [["RC-JP-BOJ-TARGET-2026-09", True]])
    A(CAT, "C2", "USDJPY 水平为 159.35、SPX 水平为 7203.85、VIX 水平为 27.01",
      SNAP + "USDJPY/SPX/VIX@2026-11-23",
      [lib.val("USDJPY", cut), lib.val("SPX", cut), lib.val("VIX", cut)], [159.35, 7203.85, 27.01])
    # ---- C3 visibility
    f1, f2 = c.REGM["ECB_MRO"]["freshness"], c.REGM["ECB_DFR"]["freshness"]
    A(CAT, "C3", "超过注册表新鲜度阈十天", "metric_registry metrics[ECB_MRO/ECB_DFR].freshness.max_calendar_lag_days",
      [f1["max_calendar_lag_days"], f2["max_calendar_lag_days"]], [10, 10])
    dg = json.dumps(c.ga.get("noncore_degraded"), ensure_ascii=False)
    A(CAT, "C3", "当日快照 Gate A 两序列列于 degraded 名单", "快照 gate_a.noncore_degraded",
      ["ECB_MRO" in dg, "ECB_DFR" in dg], [True, True])
    A(CAT, "C3", "L1 事实行 quality_status=DEGRADED", "report.json layers.L1_事实层.rows[ECB_MRO/ECB_DFR].quality_status",
      [c.l1("ECB_MRO")["quality_status"], c.l1("ECB_DFR")["quality_status"]], ["DEGRADED", "DEGRADED"])
    A(CAT, "C3", "注册表对两序列另注决策驱动口径(观测日=政策最后确认/变更日,无更晚已证实决议不作过期)",
      "metric_registry metrics[ECB_MRO/ECB_DFR].freshness.decision_dated 与 decision_dated_note",
      [f1["decision_dated"], f2["decision_dated"],
       all("观测日=政策最后确认/变更日" in f["decision_dated_note"] and "无更晚已证实决议不作过期" in f["decision_dated_note"]
           for f in (f1, f2))], [True, True, True])
    A(CAT, "C3", "引擎点值格据此标 ok", "report.json point_values.cells[ECB_MRO/ECB_DFR].anchors.*.status",
      sorted(set(c.cells[m]["anchors"][k]["status"] for m in ("ECB_MRO", "ECB_DFR") for k in c.cells[m]["anchors"])),
      ["ok"])
    A(CAT, "C3", "发布日历(最新版,2026-11-21 更新)对欧央行无实录条目", "release_calendar.updated; 含 ECB 的条目数",
      [c.cal["updated"], len(c.ECBENT)], ["2026-11-21", 0])
    # ---- (11) honest absence
    A("⑪诚实缺席", "JP", "注册表无 JP_POLICY_TARGET",
      "metric_registry.metrics 是否含 JP_POLICY_TARGET; 快照 series_store 是否含",
      ["JP_POLICY_TARGET" in c.REGM, "JP_POLICY_TARGET" in lib.SS], [False, False])
    # ---- (13') work-order target rates: effective now / pending separated
    n = "约一点二五,2026-09-18 决议、2026-09-24 生效"
    A("⑬'央行目标/通胀同比", "C2", n,
      "现行有效性: effective_on≤截止日; 其后仅维持条目; 日历无待生效条目(待生效决定与现行有效目标分记)",
      [tg["effective_on"] <= cut, mt["decision_date"], pend], [True, "2026-10-30", []])
    n = "欧央行主要再融资利率(ECB_MRO,政策目标口径)"
    A("⑬'央行目标/通胀同比", "C2", n, "注册表 metrics[ECB_MRO].calc 口径=主要再融资操作固定利率; 序列末值 2.65 自 2026-09-16 起至截止日无更新",
      ["主要再融资操作固定利率" in c.REGM["ECB_MRO"]["calc"], mro[-1][0]], [True, "2026-09-16"])
    n = "欧央行存款便利利率(ECB_DFR,操作下限口径)"
    A("⑬'央行目标/通胀同比", "C2", n, "注册表 metrics[ECB_DFR].calc 口径=存款便利利率 fixed rate(与 MRO 分列)",
      "存款便利利率" in c.REGM["ECB_DFR"]["calc"], True)
    # ---- finding support: BOJ monthly-average steps vs CPI direction at the time
    JPC = lib.monthly("JP_CPI_YOY")
    c.F["jpr_steps_vs_cpi"] = [
        [x[0][:7], round((x[2] - x[1]) * 100, 1), JPC[shift(x[0][:7], -1)], JPC[x[0][:7]]]
        for x in lib.changes("JP_POLICY_RATE", "2025-11-01", cut)]
    c.F["nonwed"] = {m: sum(1 for d, _ in lib.series(m) if lib.wd(d) != "Wed") for m in ("ECB_MRO", "ECB_DFR")}
    c.F["nonwed_total"] = {m: len(lib.series(m)) for m in ("ECB_MRO", "ECB_DFR")}
except Exception:
    c.errors.append({"section": "p2", "trace": traceback.format_exc()[-900:]})

lib.finish(c, "p2")
