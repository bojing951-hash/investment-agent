# -*- coding: utf-8 -*-
"""Part 6: (10) consistency judgment-vs-rendered report, (12) intraday, (13) non-VERIFIED disclosure, (14) code gaps.
usage: python3 -I s7_p6.py <run_dir> <install_tree> <out_dir>"""
import ast
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
rep = c.rep
cut = c.cutoff
MAP, FULL, REP = c.docs["MAP_REPORT.md"], c.docs["FULL_REPORT.md"], c.docs["report.md"]
LK = RM["transmission"][0]["links"]
K10 = "⑩一致性"


def sec(name):
    def d(f):
        try:
            f()
        except Exception:
            c.errors.append({"section": name, "trace": traceback.format_exc()[-900:]})
    return lambda f: (d(f), f)[1]


@sec("10-consistency")
def k10():
    A(K10, "report.json layers.L3_AI推断层.content", None, "report.json L3 content 与 agent_judgment.json l3 逐键相等", rep["layers"]["L3_AI推断层"]["content"] == J["l3"], True)
    A(K10, "report.json layers.L4_条件情景层.content", None, "report.json L4 content 与 agent_judgment.json l4 逐键相等", rep["layers"]["L4_条件情景层"]["content"] == J["l4"], True)
    con, ml, SC = J["l3"]["contradictions"], J["l3"]["mechanism_chains"][0]["links"], J["l4"]["scenarios"]
    G = [("矛盾陈述", [x["statement"] for x in con], "FR"), ("矛盾陈述竞争解释", [s for x in con for s in x["competing_explanations"]], "FR"),
         ("机制链四环文本", [x["text"] for x in ml], "FR"), ("情景前提行", [s["rows"]["scenario"] for s in SC], "FR"),
         ("reader_map 标题与地区段", [RM["headline_conclusion"]] + [r["from_to"] for r in RM["regions"]], "M"),
         ("传导三环观察/假设/预期", [x[k] for x in LK for k in ("observed_fact", "causal_hypothesis", "competing_explanation", "main_predicts", "competing_predicts")], "M"),
         ("转折先行/同向两栏", [w[k] for w in RM["turnings"] for k in ("first_mover", "follow_or_diverge")], "M"),
         ("历史零段注记", [RM["history_zero_case_note"]], "M"),
         ("情景证伪阈/触发条件/资产方向", [s["rows"]["falsification"]["threshold"] for s in SC] + [s["rows"]["trigger"]["condition"] for s in SC] + [s["rows"]["asset_direction"]["direction"] for s in SC], "M"),
         ("传导三环对质裁定", [x["face_off_verdict"] for x in LK], "M")]
    docs = {"M": ["MAP_REPORT.md"], "FR": ["FULL_REPORT.md", "report.md"]}
    for g, ss, dk in G:
        nf = [s for s in ss if not all(s in c.docs[n] for n in docs[dk])]
        A(K10, "/".join(docs[dk]), None, "%s 逐字包含判断档字符串数(%s)" % ("/".join(docs[dk]), g), len(ss) - len(nf), len(ss),
          ("未逐字包含: %s" % [s[:40] for s in nf]) if nf else "")
    un = {"传导三环 verdict_note": [x["verdict_note"] for x in LK], "转折 narrative": [w["narrative"] for w in RM["turnings"]]}
    c.F["unrendered"] = dict((k, {"MAP": sum(s in MAP for s in v), "FULL": sum(s in FULL for s in v), "report": sum(s in REP for s in v), "n": len(v)}) for k, v in un.items())
    frag = ["371 天", "反向观察", "非当时首发值", "对质基准", "谷底月前的 BOJ", "2026-03 1.46", "尚不能区分", "已决议而尚未生效"]
    c.F["fragments"] = dict((f, [f in MAP, f in FULL, f in REP]) for f in frag)
    refs = [r for x in con for r in x["evidence_refs"]] + [r for x in ml for r in x["evidence_refs"]]
    c.F["refs"] = refs
    A(K10, "Q0", "共 20 条 snapshot_fact 引用,全部解析到本报告证据索引;零悬空引用",
      "agent_judgment.json l3 全部 evidence_refs; report.json evidence_index; 快照 series_store 是否含该指标@该日",
      [len(refs), sum(1 for r in refs if r in c.EVI and c.EVI[r]["kind"] == "snapshot_fact"),
       sum(1 for r in refs if r.split("@")[0] in lib.SS and r.split("@")[1] in dict(lib.series(r.split("@")[0])))], [20, 20, 20])
    A("⑦传导链", "M1.step1", "观察:", "agent_judgment.json l3.mechanism_chains[0].links[].evidence_level(观察环=E1,传导/归因环=E2)",
      [x["evidence_level"] for x in ml], ["E1", "E1", "E2", "E2"])
    ce = [x["competing_explanations"] for x in con]
    A(K10, "Q1", "每条矛盾陈述并列 2 条(均标【假设】或如实并列)", "agent_judgment.json l3.contradictions[].competing_explanations 条数与是否以【假设】起首",
      [[len(x) for x in ce], all(s.startswith("【假设】") for x in ce for s in x)], [[2, 2, 2], True])
    vd = [x["face_off_verdict"] for x in LK]
    A(K10, "Q1", "支持主解释 0·支持竞争解释 0·尚不能区分 3", "reader_map.transmission[0].links[].face_off_verdict 计数",
      [vd.count("支持主解释"), vd.count("支持竞争解释"), vd.count("尚不能区分")], [0, 0, 3])
    A(K10, "agent_declaration", None, "agent_judgment.json agent_declaration.basis 含『证据索引(60行)、点值格(6格)』; report.json evidence_index 行数; research_plan.point_values.cells 格数",
      ["证据索引(60行)、点值格(6格)" in J["agent_declaration"]["basis"]], [True])
    A(K10, "agent_declaration", None, "report.json evidence_index 行数; research_plan.point_values.cells 格数",
      [len(c.EVI), len(c.cells)], [60, 6])


@sec("12-13")
def k12():
    sa = c.snap["research_as_of"]
    A("⑫盘中口径", "Q4", "快照采集于 2026-11-23T22:53:47+08:00(纽约 09:53、柏林 15:53、东京 23:53、上海 22:53)",
      "快照 research_as_of; 独立换算四地当地时间", [sa] + [lib.tz_hm(sa, z) for z in ("America/New_York", "Europe/Berlin", "Asia/Tokyo", "Asia/Shanghai")],
      ["2026-11-23T22:53:47+08:00", "09:53", "15:53", "23:53", "22:53"])
    A("⑫盘中口径", "Q4", "SPX/VIX/DAX/CAC40 的截止日值与外汇/DXY 值均为盘中快照、非收盘价",
      "快照 series_store 中 SPX/VIX/DAX/CAC40/EURUSD/USDJPY/DXY 在 2026-11-23 是否有观测; 采集时刻(纽约/柏林)早于当地收盘",
      ["2026-11-23" in dict(lib.series(m)) for m in ("SPX", "VIX", "DAX", "CAC40", "EURUSD", "USDJPY", "DXY")]
      + [lib.tz_hm(sa, "America/New_York") < "16:00", lib.tz_hm(sa, "Europe/Berlin") < "17:30"], [True] * 9)
    A("⑫盘中口径", "Q4", "席位跨地区对照统一采用 2026-11-20 同日收盘口径", "SPX/NIKKEI225/DAX/CAC40/VIX 在 2026-11-20 是否均有观测",
      ["2026-11-20" in dict(lib.series(m)) for m in ("SPX", "NIKKEI225", "DAX", "CAC40", "VIX")], [True] * 5)
    vs = c.cv.get("verdicts") or []
    c.F["cv_stats"] = c.cv.get("stats")
    A("⑬非VERIFIED披露", "Q4", "欧央行序列止于 2026-09-16(距截止 68 天,超注册表 10 天新鲜度阈,Gate A 列 degraded",
      "report.json agent_judgment.contract_verification.verdicts[].status 计数; 判断档全文是否出现 STALE 字样",
      [sum(1 for v in vs if v["status"] == "STALE"), sum(1 for v in vs if v["status"] == "VERIFIED"), "STALE" in c.jdump], [1, 4, False],
      "ECB_DFR 2.5% 契约状态=STALE(值=期望 2.5,证据过期所致): 判断档披露成因(68 天/degraded)而未写明『契约验证非 VERIFIED』,见 MINOR-6")
    A("⑬非VERIFIED披露", "C2", "欧央行存款便利利率(ECB_DFR,操作下限口径)最新生效水平 2.5%", "report.json contract_verification.verdicts[ECB_DFR].{token,value,expected}",
      [[v["token"], v["value"], v["expected"]] for v in vs if v["metric"] == "ECB_DFR"], [["2.5%", 2.5, 2.5]])
    gap = [k for k in ("缺口 6", "任务目标", "无法解析", "多范围", "降级面") if k in c.jdump]
    dr = rep["run"].get("data_requirements", {}).get("items", [])
    c.F["data_req"] = [[x["metric_id"], x["tier"], x["outcome"], (x.get("spec") or {}).get("window", {}).get("kind")] for x in dr]
    A("⑭缺口披露", "Q4", "JP_POLICY_TARGET 注册表不可得、宣布值仅发布日历实录",
      "report.json run.data_requirements.items: 六条 planned 项 outcome=insufficient_coverage 且 window.kind=unparseable(多范围无法解析); 判断档是否出现『缺口/任务目标/无法解析/多范围/降级面』字样",
      [[len(dr), sorted(set(x["outcome"] for x in dr)), sorted(set((x.get("spec") or {}).get("window", {}).get("kind") for x in dr))], gap],
      [[6, ["insufficient_coverage"], ["unparseable"]], []], "见 MINOR-5")
    c.F["evidence_gate"] = rep["run"].get("evidence_gate")
    c.F["degradation_policy"] = rep["run"].get("degradation_policy")
    c.F["semantic_review"] = rep.get("semantic_review")
    c.F["asof_discipline"] = [c.plan.get("asof_discipline"), c.plan.get("consumed_time_spans"), c.plan.get("cutoff")]


@sec("14-code")
def k14():
    src = open(os.path.join(c.tree, "scripts", "research_contract", "judgment_contract.py"), encoding="utf-8").read().split("\n")
    hit = [i + 1 for i, l in enumerate(src) if "for _lbl in ('12个月前', '3个月前', '最新一期'):" in l]
    near = [i for i in hit if any("(13)" in src[j] for j in range(max(0, i - 60), i))]
    A("⑭代码缺口", "Q5", "judgment_contract._map_checks (13))锚标签硬编码「12个月前/3个月前/最新一期」",
      "安装树 scripts/research_contract/judgment_contract.py: 是否存在硬编码锚标签行,及其前 60 行内是否有 (13) 注释",
      [bool(hit), bool(near)], [True, True], "硬编码行号=%s" % hit)
    A("⑭代码缺口", "Q5", "本问锚为「6个月前/最新一期」", "report.json research_plan.point_anchors[].label",
      [a["label"] for a in c.plan["point_anchors"]], ["6个月前", "最新一期"])
    al = None
    tsrc = open(os.path.join(c.tree, "scripts", "research_contract", "text_consistency.py"), encoding="utf-8").read()
    for node in ast.walk(ast.parse(tsrc)):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ALIASES" for t in node.targets):
            al = ast.literal_eval(node.value)
    five = ["JP_CPI_YOY", "EA_HICP_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_TARGET", "ECB_MRO"]
    A("⑭代码缺口", "Q5", "text_consistency.ALIASES 静态别名表未覆盖 JP_CPI_YOY/EA_HICP_YOY/JP_CPI_TOKYO_YOY/JP_POLICY_TARGET/ECB_MRO",
      "安装树 scripts/research_contract/text_consistency.py ALIASES 键是否含上述五指标", [m in al for m in five], [False] * 5)
    A("⑭代码缺口", "Q5", "带别名指标的最新值带指标 id 由契约逐位核验",
      "ALIASES 含 CPI; 契约验证 verdicts 的 metric 均为 ALIASES 键",
      ["CPI" in al, sorted(set(v["metric"] for v in c.cv.get("verdicts", []))), all(v["metric"] in al for v in c.cv.get("verdicts", []))],
      [True, ["ECB_DFR", "JP_POLICY_RATE", "SPX", "USDJPY", "VIX"], True], "『机构归因式引用跳过』的运行期行为未在代码执行面核验")
    A("⑭代码缺口", "Q5", "引擎报告文字「观测日全为周三」对变更点序列表述过宽(两序列含非周三观测)", "MAP_REPORT.md 含该文字; 两序列非周三观测数",
      ["观测日全为周三" in MAP] + [sum(1 for d, _ in lib.series(m) if lib.wd(d) != "Wed") for m in ("ECB_MRO", "ECB_DFR")], [True, 9, 21])
    info = {"sha": dict((f, lib.sha(os.path.join(c.run_dir, f))) for f in ("agent_judgment.json", "report.json", "MAP_REPORT.md"))}
    info["frozen_overlay_eq_tree"] = dict((rel, lib.sha(os.path.join(c.run_dir, "root_overlay", rel)) == lib.sha(os.path.join(c.tree, rel)))
                                          for rel in ("config/release_calendar.json", "config/metric_registry.json", "data/daily/research_snapshot_20261123.json"))
    info["frozen_inputs"] = rep["run"].get("frozen_inputs")
    info["stamp_in_report"] = "36499bb78a18dea1ff2b027074088b0ba404c3b8" in open(os.path.join(c.run_dir, "report.json"), encoding="utf-8").read()
    info["run_ts"] = rep["run"].get("ts_utc")
    info["written_at"] = J["agent_declaration"].get("written_at")
    c.F["info"] = info


k10()
k12()
k14()
lib.finish(c, "p6")
