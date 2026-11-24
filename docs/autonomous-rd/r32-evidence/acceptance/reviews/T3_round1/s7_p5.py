# -*- coding: utf-8 -*-
"""Part 5: section (8) history analogy note + (9) scenarios / falsification observability.
usage: python3 -I s7_p5.py <run_dir> <install_tree> <out_dir>"""
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
J = c.J
RM = J["reader_map"]
cut = c.cutoff


def sec(name):
    def d(f):
        try:
            f()
        except Exception:
            c.errors.append({"section": name, "trace": traceback.format_exc()[-900:]})
    return lambda f: (d(f), f)[1]


@sec("8-history")
def h8():
    cd = c.S6["data"]["candidates"]
    top = c.S6["data"].get("top")
    t0 = top[0] if isinstance(top, list) and top else {}
    c.F["s6_top0_keys"] = sorted(t0.keys()) if isinstance(t0, dict) else None
    c.F["s6_top0"] = t0
    A("⑧历史类比", "HIST", "S6_analog: 扫描 1871 个候选月、有效 74", "report.json steps[*].envelope(analog).data.candidates.scanned/valid",
      [cd.get("scanned"), cd.get("valid")], [1871, 74])
    A("⑧历史类比", "HIST", "TOP1 候选月 2025-03 距离 0.727", "report.json steps[*].envelope(analog).data.top[0].{candidate_month,distance}",
      [t0.get("candidate_month"), t0.get("distance")], ["2025-03", 0.727])
    A("⑧历史类比", "HIST", "历史类比 0 段", "agent_judgment.json reader_map.history_periods 长度", len(RM["history_periods"]), 0)


@sec("9-scenarios")
def s9():
    S = dict((s["id"], s["rows"]) for s in J["l4"]["scenarios"])
    s1, s2 = S["S1-STICKY-TIGHTEN"], S["S2-INFL-FADE"]
    for sid, rw in (("S1-STICKY-TIGHTEN", s1), ("S2-INFL-FADE", s2)):
        A("⑨情景", sid + ".scenario", "至 2026-12 观测月(读数按引擎发布规则于 2027-01 入档,早于时限 2027-02-15)",
          "引擎规则独立推算: 2026-12 观测月 EA_HICP_YOY 入档日(月末+16天)与 JP_CPI_YOY 入档日(月末+20天)均 < 2027-02-15",
          [lib.rule_pub("2026-12", 16), lib.rule_pub("2026-12", 20), max(lib.rule_pub("2026-12", 16), lib.rule_pub("2026-12", 20)) < rw["trigger"]["deadline"]],
          ["2027-01-16", "2027-01-20", True])
        A("⑨情景", sid + ".trigger", "以决议实录核验(冻结日历对欧央行零条实录,欧央行分量须待日历补录后方可核验;日本端两条实录可核)",
          "release_calendar: ECB 条目数; JP_POLICY_TARGET 条目数", [len(c.ECBENT), len(c.cent("JP_POLICY_TARGET"))], [0, 2])
        A("⑨情景", sid + ".trigger", "VIX", "VIX 日频序列在快照 series_store 在场(收盘口径可观测)", "VIX" in lib.SS and not lib.isMonthly("VIX"), True)
    A("⑨情景", "S1-STICKY-TIGHTEN.scenario", "欧元区 HICP 同比维持 3.5% 以上", "S1.falsification.threshold 所含证伪阈(3.5%)与前提水平一致",
      "3.5%" in s1["falsification"]["threshold"] and "低于 3.5%" in s1["falsification"]["threshold"], True)
    A("⑨情景", "S1-STICKY-TIGHTEN.scenario", "日本全国 CPI 同比维持 2.0% 以上", "S1.trigger.condition 所含日本分量触发阈(≥2.0%)与前提一致",
      "JP_CPI_YOY 同比 ≥2.0%" in s1["trigger"]["condition"], True)
    A("⑨情景", "S1-STICKY-TIGHTEN.trigger", "EA_HICP_YOY 同比 ≥4.0%", "S1 触发阈与证伪阈之差(触发 4.0 − 证伪 3.5,个百分点): 3.5–4.0 区间不触发亦不证伪且 S1 文本未披露该区间",
      round(4.0 - 3.5, 2), 0.5, "见问题清单 MINOR-2")
    A("⑨情景", "S1-STICKY-TIGHTEN.falsify", "若观测月 2026-11 与 2026-12 两月欧元区 HICP 同比均低于 3.5%(前提水平)",
      "S1.falsification.threshold 是否含日本分量(JP_CPI_YOY)的数值证伪阈", bool(re.search(r"JP_CPI_YOY|日本全国 CPI 同比.*\d", s1["falsification"]["threshold"])), False,
      "见问题清单 MINOR-3")
    A("⑨情景", "Q3", "S1 证伪阈值与前提水平对齐(3.5%)", "S2.falsification.threshold 是否披露 3.0%–3.5% 区间", "3.0%–3.5% 区间不触发亦不证伪" in s2["falsification"]["threshold"], True)
    A("⑨情景", "S2-INFL-FADE.falsify", "或 2026-12 观测月日本全国 CPI 同比不低于 2.0%", "S2.falsification.threshold 含日本分量证伪阈", "日本全国 CPI 同比不低于 2.0%" in s2["falsification"]["threshold"], True)
    A("⑨情景", "S2-INFL-FADE.asset", "相反", "两情景资产方向文字: S1 含『承压/维持高位』且 S2 含『修复/回落』(方向互补)",
      [("承压" in s1["asset_direction"]["direction"]) and ("维持高位" in s1["asset_direction"]["direction"]),
       ("修复" in s2["asset_direction"]["direction"]) and ("回落" in s2["asset_direction"]["direction"])], [True, True])
    A("⑨情景", "S2-INFL-FADE.trigger", "2027-02-15" if "2027-02-15" in s2["trigger"]["condition"] else "低于 25", "两情景 trigger.deadline 相同且证伪/触发指标均在注册表",
      [s1["trigger"]["deadline"], s2["trigger"]["deadline"],
       all(m in c.REGM for m in s1["sensitive_variables"] + s1["falsification"]["secondary_metric_ids"] + s2["sensitive_variables"] + s2["falsification"]["secondary_metric_ids"])],
      ["2027-02-15", "2027-02-15", True])
    A("⑨情景", "S2-INFL-FADE.trigger", "同时 VIX 在两读数均入档之日前最近一个交易日收盘低于 25", "截止日下未触发亦未证伪: 2026-11 观测月两地读数按引擎规则均未入档(入档日晚于截止日)",
      [lib.rule_pub("2026-11", 16) > cut, lib.rule_pub("2026-11", 20) > cut], [True, True])
    A("⑨情景", "S1-STICKY-TIGHTEN.falsify", None, "两情景 rows 五键齐备(scenario/asset_direction/sensitive_variables/falsification/trigger)",
      [sorted(s1.keys()) == sorted(["scenario", "asset_direction", "sensitive_variables", "falsification", "trigger"]),
       sorted(s2.keys()) == sorted(["scenario", "asset_direction", "sensitive_variables", "falsification", "trigger"])], [True, True])


lib.finish(c, "p5")
