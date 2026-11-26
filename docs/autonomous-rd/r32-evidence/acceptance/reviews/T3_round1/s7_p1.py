# -*- coding: utf-8 -*-
"""Part 1: sections (1) research cutoff, (2) point-anchor cells, (3) yoy comparisons + honest-absence.
usage: python3 -I s7_p1.py <run_dir> <install_tree> <out_dir>"""
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


def sec(name):
    def d(f):
        try:
            f()
        except Exception as e:
            c.errors.append({"section": name, "error": repr(e), "trace": traceback.format_exc()[-700:]})
    return lambda f: (d(f), f)[1]


@sec("1-cutoff")
def s1():
    cutoff = c.cutoff
    SRC = "report.json research_plan.point_anchors[最新一期].as_of"
    A("①研究截止日", "C2", "截至研究截止 2026-11-23", SRC, cutoff, "2026-11-23")
    A("①研究截止日", "C3", "距研究截止 2026-11-23 六十八天", SRC, cutoff, "2026-11-23")
    A("①研究截止日", "Q4", "研究截止日=2026-11-23(快照版本日", SRC, cutoff, "2026-11-23")
    A("①研究截止日", "Q4", "快照采集于 2026-11-23T22:53:47+08:00", "快照 顶层键 research_as_of",
      c.snap["research_as_of"], "2026-11-23T22:53:47+08:00")
    A("①研究截止日", "Q4", "研究截止日=2026-11-23(快照版本日", "快照 顶层键 target_date(规范化 YYYYMMDD)",
      re.sub(r"\D", "", str(c.snap.get("target_date"))), "20261123")
    w = c.plan["question_window"]["windows"][0]
    A("①研究截止日", "C2", "最近六个月(2026-05-23..2026-11-23)",
      "report.json research_plan.question_window.windows[0].from/to", [w["from"], w["to"]],
      ["2026-05-23", "2026-11-23"])
    y, mo = int(cutoff[:4]), int(cutoff[5:7])
    mo -= 6
    if mo <= 0:
        mo += 12
        y -= 1
    A("①研究截止日", "C2", "最近六个月(2026-05-23..2026-11-23)", "独立推算: 截止日−6个自然月",
      "%04d-%02d-%s" % (y, mo, cutoff[8:]), "2026-05-23")
    n = "并列问句窗六个月(2026-05-22 收盘→2026-11-20 收盘)"
    A("①研究截止日", "M1.step3", n, SNAP + "EURUSD 截至 2026-05-23 的最后观测日",
      lib.at("EURUSD", "2026-05-23")[0], "2026-05-22",
      "星期核对 2026-05-23=%s 2026-05-22=%s" % (lib.wd("2026-05-23"), lib.wd("2026-05-22")))
    A("①研究截止日", "M1.step3", n, SNAP + "USDJPY 截至 2026-05-23 的最后观测日",
      lib.at("USDJPY", "2026-05-23")[0], "2026-05-22")


@sec("2-anchor-cells")
def s2():
    RM = c.J["reader_map"]
    echo = RM["regions"][0]["anchor_echo"] + RM["regions"][1]["anchor_echo"]
    c.F["n_echo"] = len(echo)
    c.F["n_cells"] = len(c.plan["point_values"]["cells"])
    for i, e in enumerate(echo):
        m, lab = e["metric_id"], e["anchor"]
        as_of = c.pa[lab]["as_of"]
        d, v = lib.asof(m, as_of)
        w = "reader_map.regions.anchor_echo[%d:%s/%s]" % (i, m, lab)
        A("②点值锚格", w, None, SNAP + "%s 截至 %s 的最新观测值" % (m, as_of), v, e["value"])
        A("②点值锚格", w, None, SNAP + "%s 截至 %s 的最新观测月" % (m, as_of), d[:7], e["observation_month"])
        an = c.cells[m]["anchors"][lab]
        A("②点值锚格", w, None,
          "report.json point_values.cells[%s].anchors[%s].value/observation_date(引擎面对账)" % (m, lab),
          [an["value"], an["observation_date"]], [e["value"], d])
        if lib.isMonthly(m):
            mm = re.search(r"月末([+−\-])\s*(\d+)天", an.get("publication_rule") or "")
            off = int(mm.group(2)) * (-1 if mm.group(1) in ("−", "-") else 1)
            A("②点值锚格", w, None, "独立推算: 观测月末 %s 加减 %s 天(规则文本=引擎 publication_rule)" % (
                lib.eom(d[:7]), mm.group(1) + mm.group(2)), lib.rule_pub(d[:7], off), an["publication_date"],
                an.get("publication_rule", ""))


@sec("3-yoy")
def s3():
    JP, EA, TK = lib.monthly("JP_CPI_YOY"), lib.monthly("EA_HICP_YOY"), lib.monthly("JP_CPI_TOKYO_YOY")
    c.F["JP"] = JP
    c.F["EA"] = EA
    c.F["TK"] = TK
    n1 = "日本全国CPI同比最新读数百分之二点四四(观测 2026-10,发布 2026-11-20,引擎推定规则、非日历实录)"
    A("③同比", "C1", n1, SNAP + "JP_CPI_YOY@2026-10-01", JP["2026-10"], 2.44)
    A("③同比", "C1", n1, "独立推算 2026-10-31+20天; release_calendar.entries 中 metric_id=JP_CPI_YOY 条目数",
      [lib.rule_pub("2026-10", 20), len(c.cent("JP_CPI_YOY"))], ["2026-11-20", 0])
    A("③同比", "C1", "去年同月(2025-10)为百分之二点九九", SNAP + "JP_CPI_YOY@2025-10-01", JP["2025-10"], 2.99)
    A("③同比", "C1", "回落约零点五五个百分点", "JP_CPI_YOY@2026-10 减 @2025-10",
      round(JP["2026-10"] - JP["2025-10"], 2), -0.55)
    others = [JP[k] for k in sorted(JP) if "2025-11" <= k <= "2026-09"]
    A("③同比", "C1", "近十二个月中其余十一个月里有十个月读数低于最新值",
      "JP_CPI_YOY 2025-11..2026-09 共 %d 个月中低于 2.44 的个数" % len(others),
      sum(1 for v in others if v < JP["2026-10"]), 10, str(others))
    A("③同比", "C1", "较一、三、六个月前分别高零点二八、零点四七、一点零六",
      "JP_CPI_YOY 2026-10 减 2026-09/2026-07/2026-04",
      [round(JP["2026-10"] - JP[k], 2) for k in ("2026-09", "2026-07", "2026-04")], [0.28, 0.47, 1.06])
    n2 = "欧元区HICP同比最新读数百分之四点零(观测 2026-10,发布 2026-11-16"
    A("③同比", "C1", n2, SNAP + "EA_HICP_YOY@2026-10-01", EA["2026-10"], 4.0)
    A("③同比", "C1", n2, "独立推算 2026-10-31+16天; 日历中覆盖 2026-10 观测月的 EA_HICP_YOY 条目数",
      [lib.rule_pub("2026-10", 16),
       sum(1 for x in c.cent("EA_HICP_YOY") if x["obs_from"] <= "2026-10-01" <= x["obs_to"])],
      ["2026-11-16", 0])
    e3 = sorted(c.cent("EA_HICP_YOY"), key=lambda x: x["obs_from"])
    fl = [x["first_publish_on_or_after"] for x in e3]
    fi = [x["final_publish_on"] for x in e3]
    A("③同比", "C1", "两档形态(次月首日快报+月中终值)",
      "release_calendar.entries RC-EA-HICP-*: first_publish_on_or_after / final_publish_on",
      [all(f == lib.first_next(x["obs_from"][:7]) for f, x in zip(fl, e3)),
       all(15 <= int(f[8:10]) <= 20 for f in fi)], [True, True], "flash=%s final=%s" % (fl, fi))
    A("③同比", "C1", "该读数的首发不在该终值日",
      "按日历两档形态推及 2026-10 观测月: 快报日(次月首日)是否不等于引擎终值日",
      lib.first_next("2026-10") != lib.rule_pub("2026-10", 16), True,
      "%s vs %s" % (lib.first_next("2026-10"), lib.rule_pub("2026-10", 16)))
    A("③同比", "C1", "去年同月(2025-10)为百分之二点一", SNAP + "EA_HICP_YOY@2025-10-01", EA["2025-10"], 2.1)
    A("③同比", "C1", "抬升一点九个百分点", "EA_HICP_YOY@2026-10 减 @2025-10",
      round(EA["2026-10"] - EA["2025-10"], 2), 1.9)
    n3 = "东京都CPI同比(中旬速报先行口径)最新读数百分之二点七三(观测 2026-10,发布 2026-10-30,引擎推定规则、非日历实录)"
    A("③同比", "C1", n3, SNAP + "JP_CPI_TOKYO_YOY@2026-10-01", TK["2026-10"], 2.73)
    A("③同比", "C1", n3, "独立推算 2026-10-31−1天; 日历中 JP_CPI_TOKYO_YOY 条目数",
      [lib.rule_pub("2026-10", -1), len(c.cent("JP_CPI_TOKYO_YOY"))], ["2026-10-30", 0])
    A("③同比", "C1", "序列自 2026-01 起", SNAP + "JP_CPI_TOKYO_YOY 首/末观测月与点数",
      [min(TK), max(TK), len(TK)], ["2026-01", "2026-10", 10])
    A("③同比", "C1", "去年同月基期观测不可得、同比对照不可判", SNAP + "JP_CPI_TOKYO_YOY 是否含 2025-10",
      "2025-10" in TK, False)
    nm = json.dumps(c.ga.get("noncore_missing"), ensure_ascii=False)
    A("⑪诚实缺席", "C1", "该序列在当日快照 Gate A 列于 noncore_missing(来源文件在场而指标缺席)",
      "快照 gate_a.noncore_missing 与 noncore_missing_detail[JP_CPI_TOKYO_YOY]",
      ["JP_CPI_TOKYO_YOY" in nm,
       "来源文件在场而指标缺席" in (c.ga.get("noncore_missing_detail") or {}).get("JP_CPI_TOKYO_YOY", "")],
      [True, True])
    A("⑪诚实缺席", "C1", "L1 无对应事实行",
      "report.json layers.L1_事实层.rows 中 metric_id=JP_CPI_TOKYO_YOY 的行数",
      sum(1 for x in c.L1R if x.get("metric_id") == "JP_CPI_TOKYO_YOY"), 0)
    A("③同比", "C1", "两条全国/全区最新读数 L1 quality_status 分别为 WARN 与 WARN",
      "report.json layers.L1_事实层.rows[JP_CPI_YOY/EA_HICP_YOY].quality_status",
      [c.l1("JP_CPI_YOY")["quality_status"], c.l1("EA_HICP_YOY")["quality_status"]], ["WARN", "WARN"])


lib.finish(c, "p1")
