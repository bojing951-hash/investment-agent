#!/usr/bin/python3 -I
"""Recompute part C (categories ⑪-⑮): honest absence, cutoff-day timing, contract STALE,
delivery-gate gap disclosures, target-rate calibers.

Read-only. Args:
  <snapshot.json> <report.json> <agent_judgment.json> <release_calendar.json> <metric_registry.json>
  <run_dir> <tree_dir> <out_dir>
"""
import ast
import datetime as dt
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("s10_common", os.path.join(HERE, "s10_common.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

a = sys.argv[1:]
snap, rep, jd, cal, reg = (C.load_json(p) for p in a[0:5])
run_dir, tree_dir, out_dir = a[5], a[6], a[7]
ss = snap["series_store"]
plan = rep["research_plan"]
cutoff = plan["cutoff"]
CD = C.D(cutoff)
regm = {m["metric_id"]: m for m in reg["metrics"]}
facts = {f["fact_id"]: f for f in snap["facts"]}
l1 = {r["metric_id"]: r for r in rep["layers"]["L1_事实层"]["rows"]}
ga = snap["gate_a"]
entries = cal["entries"]
cv = jd.get("contract_verification") or rep["agent_judgment"].get("contract_verification")
cells = {c["metric_id"]: c for c in plan["point_values"]["cells"]}
MAP_MD = C.read_text(os.path.join(run_dir, "MAP_REPORT.md"))


def T(p):
    return C.get(jd, p)


C1, C2, C3 = (T("l3.contradictions[%d].statement" % i) for i in range(3))
CXT = ["\n".join(T("l3.contradictions[%d].competing_explanations" % i)) for i in range(3)]
M = [T("l3.mechanism_chains[0].links[%d].text" % i) for i in range(4)]
HL = T("reader_map.headline_conclusion")
EA = T("reader_map.regions[0].from_to")
JP = T("reader_map.regions[1].from_to")
TLN = [T("reader_map.transmission[0].links[%d].verdict_note" % i) for i in range(3)]
QN = T("quality_gate_notes")
DECL = T("agent_declaration")
B = C.Book("C")
add = B.add
DAY7 = ["SPX", "VIX", "DAX", "CAC40", "EURUSD", "USDJPY", "DXY"]


def issues(mid):
    f = facts.get("%s@%s" % (mid, C.last_obs(ss, mid)[0]))
    return " ".join("%s:%s" % (i.get("category"), i.get("message")) for i in (f or {}).get("issues", []))


# ================================================================ ⑪ honest absence (series-level)
add("K001", "⑪", "C1 东京CPI Gate A 名单", "snapshot.gate_a.noncore_missing",
    "JP_CPI_TOKYO_YOY" in ga["noncore_missing"], True,
    lit="该序列在当日快照 Gate A 列于 noncore_missing(来源文件在场而指标缺席)", text=C1)
det = ga["noncore_missing_detail"]["JP_CPI_TOKYO_YOY"]
add("K002", "⑪", "C1 东京CPI 缺席注记(逐字)", "snapshot.gate_a.noncore_missing_detail.JP_CPI_TOKYO_YOY",
    det.split("(")[0], "来源文件在场而指标缺席", lit="(来源文件在场而指标缺席)", text=C1,
    note="快照全文: " + det)
add("K003", "⑪", "C1 东京CPI 无 L1 事实行", "report.layers.L1 rows metric_id",
    "JP_CPI_TOKYO_YOY" in l1, False, lit="点值取自快照序列面、L1 无对应事实行", text=C1)
lists = "非核心缺席 " + "、".join(ga["noncore_missing"]) + " | 非核心降级 " + "、".join(ga["noncore_degraded"])
add("K004", "⑪", "读者报告 Gate A 行与快照名单一致", "snapshot.gate_a.{status,noncore_missing,noncore_degraded}",
    ga["status"], "DEGRADED", ok=(ga["status"] == "DEGRADED" and lists in MAP_MD),
    lit="数据门(Gate A,源快照采集面): DEGRADED", text=MAP_MD,
    note="名单 %d 缺席/%d 降级逐字在场于 MAP_REPORT.md 第7行" % (len(ga["noncore_missing"]), len(ga["noncore_degraded"])))
add("K005", "⑪", "C1 L1 质量位 WARN/WARN", "report.layers.L1 rows quality_status",
    (l1["JP_CPI_YOY"]["quality_status"], l1["EA_HICP_YOY"]["quality_status"]), ("WARN", "WARN"),
    lit="两条全国/全区最新读数 L1 quality_status 分别为 WARN 与 WARN", text=C1)
add("K006", "⑪", "C1 WARN 原因=发布时间未验证", "snapshot.facts[*].issues",
    ("RELEASE_UNKNOWN" in issues("JP_CPI_YOY"), "RELEASE_UNKNOWN" in issues("EA_HICP_YOY")), (True, True),
    lit="引擎推定规则、非日历实录", text=C1,
    note="JP_CPI_YOY: " + issues("JP_CPI_YOY") + " | EA_HICP_YOY: " + issues("EA_HICP_YOY"))
add("K007", "⑪", "C3 L1 质量位 DEGRADED", "report.layers.L1 rows quality_status",
    (l1["ECB_MRO"]["quality_status"], l1["ECB_DFR"]["quality_status"]), ("DEGRADED", "DEGRADED"),
    lit="L1 事实行 quality_status=DEGRADED", text=C3)
add("K008", "⑪", "C3 Gate A degraded 名单", "snapshot.gate_a.noncore_degraded",
    sorted(set(["ECB_MRO", "ECB_DFR"]) & set(ga["noncore_degraded"])), ["ECB_DFR", "ECB_MRO"],
    lit="当日快照 Gate A 两序列列于 degraded 名单", text=C3)
add("K009", "⑪", "C3 滞后天数与快照 DEGRADED 原因一致", "snapshot.facts[*].issues",
    ("观测日滞后68天(>10天有效窗" in issues("ECB_MRO"), "观测日滞后68天(>10天有效窗" in issues("ECB_DFR")), (True, True),
    lit="六十八天", text=C3, note="ECB_MRO: " + issues("ECB_MRO"))
add("K010", "⑪", "对质环2 交叉盘缺席(序列面+注册表)", "snapshot.series_store keys / registry metric_id",
    ("EURJPY" in ss, "EURJPY" in regm), (False, False),
    lit="EURJPY 交叉盘序列不在证据面", text=TLN[1])
add("K011", "⑪", "C1 竞争解释『无分项构成序列』", "registry metric_id(CORE|ENERG, economy in EA/JP)",
    sorted(i for i in regm if re.search(r"CORE|ENERG", i) and regm[i].get("economy") in ("EA", "JP")), [],
    lit="引擎无分项构成与基数贡献序列", text=CXT[0])
add("K012", "⑪", "C2 竞争解释『无央行表态文本序列』", "registry metric_id(STATE|SPEECH|TEXT|MINUTE|SENTIM|SURVEY)",
    sorted(i for i in regm if re.search(r"STATE|SPEECH|TEXT|MINUTE|SENTIM|SURVEY", i)), [],
    lit="引擎无央行表态文本序列", text=CXT[1])
dg = plan.get("dimension_gaps") or []
add("K013", "⑪", "Q4 JP_POLICY_TARGET 注册表不可得", "report.research_plan.dimension_gaps / registry",
    ("JP_POLICY_TARGET" in regm, sorted(set(x.get("gap") for x in dg if x.get("metric_id") == "JP_POLICY_TARGET"))),
    (False, ["registry_absent"]), lit="JP_POLICY_TARGET 注册表不可得", text=QN[4])
add("K014", "⑪", "C1 东京序列起点(注册表注记)", "registry JP_CPI_TOKYO_YOY.calc",
    "基期内同月同比仅2026-01..2026-10 十个月" in regm["JP_CPI_TOKYO_YOY"]["calc"], True,
    lit="序列自 2026-01 起", text=C1)
tk = cells["JP_CPI_TOKYO_YOY"]["anchors"]
add("K015", "⑪", "东京CPI 点值格状态(引擎面)", "report.research_plan.point_values.cells[JP_CPI_TOKYO_YOY].anchors[*].status",
    [tk[k]["status"] for k in tk], ["degraded_or_missing", "degraded_or_missing"], ok=False, sev="SCOPE-OUT",
    note="引擎点值格对 Gate A noncore_missing 序列两锚仍标 ok,读者报告环境表该行亦标 ok(与同页第7行『缺席数据不得进入研究结论』并置);席位在 C1/QN4 按 Gate A 如实披露——引擎面口径不一,非判断偏离")

# ================================================================ ⑫ cutoff-day observation timing
last7 = [(m, C.last_obs(ss, m)[0]) for m in DAY7]
add("L001", "⑫", "C2/Q4 截止日盘中水平: 7 序列当日有观测", "snapshot.series_store.<m> 末观测日",
    last7, [(m, "2026-11-23") for m in DAY7],
    lit="SPX/VIX/DAX/CAC40 的截止日值与外汇/DXY 值均为盘中快照、非收盘价", text=QN[4])
rng = [(m, facts["%s@2026-11-23" % m]["low"] <= facts["%s@2026-11-23" % m]["value"] <= facts["%s@2026-11-23" % m]["high"],
        facts["%s@2026-11-23" % m]["low"], facts["%s@2026-11-23" % m]["high"]) for m in DAY7]
add("L002", "⑫", "盘中佐证: 当日值落在日内低/高之间", "snapshot.facts[*].{low,value,high}",
    all(x[1] for x in rng), True, lit="盘中快照", text=C2,
    note="; ".join("%s low %s/value %s/high %s" % (x[0], x[2], facts["%s@2026-11-23" % x[0]]["value"], x[3]) for x in rng))
add("L003", "⑫", "M1-4 日经末观测日=2026-11-20", "snapshot.series_store.NIKKEI225 末观测日",
    C.last_obs(ss, "NIKKEI225")[0], "2026-11-20", lit="56436.65,2026-11-20 收盘", text=M[3])
tz = C.norm_tz(snap["research_as_of"])
add("L004", "⑫", "盘中相容: 纽约开盘后/柏林收盘前/截止日为交易日", "snapshot.research_as_of 时区换算(常规交易时段 09:30-16:00 纽约、09:00-17:30 柏林)",
    (tz["NewYork"] >= "09:30", tz["Berlin"] < "17:30", tz["NewYork_weekday"] == "Mon"), (True, True, True),
    lit="纽约 09:53、柏林 15:53", text=QN[4],
    note="快照时刻 %s = 纽约 %s(%s) / 柏林 %s / 东京 %s / 上海 %s" % (
        snap["research_as_of"], tz["NewYork"], tz["NewYork_weekday"], tz["Berlin"], tz["Tokyo"], tz["Shanghai"]))
ts_run = dt.datetime.strptime(rep["run"]["ts_utc"], "%Y%m%dT%H%M%SZ").replace(tzinfo=dt.timezone.utc)
t_asof = dt.datetime.fromisoformat(snap["research_as_of"])
t_written = dt.datetime.fromisoformat(re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", DECL["written_at"]))
add("L005", "⑫", "时序: 快照时刻 < 运行起始 < 成文时刻", "snapshot.research_as_of / report.run.ts_utc / agent_declaration.written_at",
    (t_asof < ts_run, ts_run < t_written), (True, True),
    note="as_of %s | run %s | written %s (UTC)" % (t_asof.astimezone(dt.timezone.utc), ts_run, t_written.astimezone(dt.timezone.utc)))
add("L006", "⑫", "截止日当日事实 as_of 与 research_as_of 一致", "snapshot.facts[*].as_of",
    sorted(set(facts["%s@2026-11-23" % m]["as_of"] for m in DAY7)), [snap["research_as_of"]])
add("L007", "⑫", "M1-3 UST_10Y 末观测日", "snapshot.series_store.UST_10Y 末观测日",
    C.last_obs(ss, "UST_10Y")[0], "2026-11-19", lit="UST_10Y 最新 5.04%", text=M[2])
add("L008", "⑫", "同日收盘口径两端为交易日且有观测", "snapshot.series_store 8 序列在 2026-10-23/2026-11-20 的观测",
    all(C.val_at(ss, m, d) is not None for m in ["SPX", "NIKKEI225", "DAX", "CAC40", "VIX", "EURUSD", "USDJPY", "DXY"]
        for d in ("2026-10-23", "2026-11-20")), True,
    lit="同日收盘口径(窗起 2026-10-23 收盘→2026-11-20 收盘)", text=M[3])
add("L009", "⑫", "截止日与其前一交易日星期", "日历",
    (C.WD[CD.weekday()], C.WD[C.D("2026-11-20").weekday()]), ("Mon", "Fri"),
    note="11-21/11-22 为周末;快照时刻东京 23:53 已晚于当日东京场收盘,日经 11-23 观测缺席属采集滞后,席位未把 11-20 值写成截止日值")

# ================================================================ ⑬ contract verification (non-VERIFIED)
vs_ = cv["verdicts"]
stv = [x for x in vs_ if x["status"] != "VERIFIED"]
add("M001", "⑬", "契约逐位核验状态", "agent_judgment.contract_verification.verdicts[*]",
    [(x["metric"], x["status"]) for x in vs_],
    [("ECB_DFR", "STALE"), ("JP_POLICY_RATE", "VERIFIED"), ("USDJPY", "VERIFIED"), ("SPX", "VERIFIED"), ("VIX", "VERIFIED")])
add("M002", "⑬", "STALE 位数值=序列直读", "verdicts[STALE] + snapshot.series_store.ECB_DFR[2026-09-16]",
    (stv[0]["token"], stv[0]["value"], stv[0]["expected"], C.val_at(ss, "ECB_DFR", "2026-09-16")), ("2.5%", 2.5, 2.5, 2.5),
    note="STALE 为时效状态而非数值不符;contradicted=0")
deg = [x["metric"] for x in vs_ if l1.get(x["metric"], {}).get("quality_status") == "DEGRADED"]
add("M003", "⑬", "STALE 与 L1 DEGRADED 一一对应", "verdicts[*].metric × report.layers.L1 quality_status",
    (deg, [x["metric"] for x in stv]), (["ECB_DFR"], ["ECB_DFR"]),
    note="五个受核指标中仅 ECB_DFR 在 L1 为 DEGRADED;JP_POLICY_RATE 为 WARN 仍 VERIFIED——STALE 源于时效位")
add("M004", "⑬", "契约总判与统计", "agent_judgment.contract_verification.{verdict,stats}",
    (cv["verdict"], cv["stats"]["checks"], cv["stats"]["verified"], cv["stats"]["contradicted"], cv["stats"]["unbound"]),
    ("VERIFIED", 5, 4, 0, 0))
ALL = C.all_text(jd)
add("M005", "⑬", "STALE 根因(ECB_DFR DEGRADED)已在判断档披露", "agent_judgment 全文检索",
    ("STALE" in ALL, "quality_status=DEGRADED" in C3, "Gate A 列 degraded" in HL), (False, True, True),
    note="契约核验发生在成文之后,席位无从写『STALE』字样;其根因与时效风险已由 C3/QN4/总判断披露,数值经本席直读一致")

# ================================================================ ⑭ delivery-gate gap disclosures
MAINT = re.compile(r"无变化|维持不变|未调整|按兵不动|无新调整|无新决议|未再调整")
ECBP = re.compile(r"ECB|欧央行|欧元区央行")
HEDGE = re.compile(r"不可见|不可判|尚未验证|引擎记录面|仅覆盖|不设数值触发|不裁|若")
hits = []


def _walk(o, path):
    if isinstance(o, str):
        for cl in re.split(r"[。；;]", o):
            if MAINT.search(cl) and ECBP.search(cl):
                hits.append((path, cl.strip()))
    elif isinstance(o, dict):
        for k, v in o.items():
            _walk(v, "%s.%s" % (path, k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            _walk(v, "%s[%d]" % (path, i))


_walk(jd, "$")
bad_ecb = [(p, c) for p, c in hits
           if not (p.startswith("$.l4.") or "competing_explanations" in p or HEDGE.search(c)
                   or p.startswith("$.quality_gate_notes"))]
add("N001", "⑭", "欧央行 2026-09-16 后状态未被写成『无变化/维持』(事实位)", "agent_judgment 全文分句扫描(欧央行+维持类词)",
    len(bad_ecb), 0, note="命中 %d 句均为情景假设/竞争解释/带『不可见·不可判·尚未验证』限定;事实位零命中" % len(hits))
for p, c in hits:
    print("   N001 hit:", p, "|", c[:100])
for p, c in bad_ecb:
    print("   N001 BAD :", p, "|", c[:200])
add("N002", "⑭", "C2 无未生效决议限定于引擎记录面", "agent_judgment.l3.contradictions[1].statement",
    "引擎记录面(注册表序列+发布日历实录)无任何已决议而尚未生效的调整" in C2, True,
    lit="引擎记录面(注册表序列+发布日历实录)无任何已决议而尚未生效的调整", text=C2)
add("N003", "⑭", "C2 其后决议面不可见【尚未验证】", "agent_judgment.l3.contradictions[1].statement",
    "其后决议面不可见【尚未验证】" in C2, True, lit="其后决议面不可见【尚未验证】", text=C2)
add("N004", "⑭", "C3 结论覆盖面限定", "agent_judgment.l3.contradictions[2].statement",
    "仅覆盖引擎可见面" in C3, True, lit="本报告关于欧央行无未生效决议的结论仅覆盖引擎可见面", text=C3)
ecb_ent = [e["entry_id"] for e in entries if "ECB" in str(e.get("entry_id", "")) or "ECB" in str(e.get("metric_id", ""))]
pend = [e["entry_id"] for e in entries if e.get("effective_on") and e["effective_on"] > cutoff]
add("N005", "⑭", "日历零 ECB 条目 / 零待生效条目", "release_calendar.entries",
    (ecb_ent, pend), ([], []), note="日历 %s 条,version %s,updated %s" % (len(entries), cal.get("version"), cal.get("updated")))
dec = [e for e in entries if e.get("entry_id") == "RC-JP-BOJ-TARGET-2026-09"][0]
mnt = [e for e in entries if e.get("entry_id") == "RC-JP-BOJ-MAINT-2026-10"][0]
add("N006", "⑭", "C2 日央行确认维持=维持决议且目标值未变", "release_calendar RC-JP-BOJ-MAINT-2026-10 / RC-JP-BOJ-TARGET-2026-09",
    (mnt.get("kind"), mnt.get("target_value"), "effective_on" in mnt, dec["target_value"]),
    ("policy_maintenance", 1.25, False, 1.25),
    lit="2026-10-30 会议确认维持不变(无新调整、无生效变动)", text=C2)
add("N007", "⑭", "C2 日央行『收紧』方向标注【推断】", "agent_judgment.l3.contradictions[1].statement",
    ("日本端「收紧」方向依据月均市场利率台阶" in C2, "实录无前值,属【推断】" in C2), (True, True),
    lit="实录无前值,属【推断】", text=C2)
add("N008", "⑭", "总判断未把月均值写成官方目标", "agent_judgment.reader_map.headline_conclusion",
    ("1.227" in HL, "0.727" in HL, "月均" in HL), (False, False, False),
    note="总判断目标值仅 1.25(日历宣布值);月均 1.227 只出现在 C2/走位/机制链并带『月均口径』")
add("N009", "⑭", "月均≠宣布值 两处写明", "agent_judgment C2 / reader_map.regions[1].from_to",
    ("月均口径非宣布值" in C2, "月均≠宣布值" in JP), (True, True),
    lit="月均口径非宣布值", text=C2)
add("N010", "⑭", "日央行实录无前值字段", "release_calendar RC-JP-BOJ-TARGET-2026-09 字段名",
    sorted(k for k in dec.keys() if re.search(r"prev|prior|old|last|from_value|change", k, re.I)), [],
    note="实录字段: " + ", ".join(sorted(dec.keys())) + ";无前值字段,『同向收紧』的日本端方向只能来自月均台阶(席位已标【推断】)")
add("N011", "⑭", "日历『约1.25%』与总判断『1.25%』", "release_calendar RC-JP-BOJ-TARGET-2026-09.{target_value,note}",
    (dec["target_value"], "约1.25%" in dec["note"], "约1.25%" in mnt["note"]), (1.25, True, True),
    lit="日本央行政策目标 1.25%", text=HL,
    note="数值字段 1.25 精确;日历注记行文为『约1.25%』,总判断与走位未带『约』(见 PROSE NIT)")

# ================================================================ ⑮ target caliber / dates / YoY base
add("O001", "⑮", "C2 日央行三日期分记", "release_calendar RC-JP-BOJ-*",
    (dec["decision_date"], dec["effective_on"], mnt["decision_date"]), ("2026-09-18", "2026-09-24", "2026-10-30"),
    lit="2026-09-18 决议、2026-09-24 生效,2026-10-30 会议确认维持不变", text=C2)
add("O002", "⑮", "现行有效目标: 生效日≤截止日≤obs_to,且无待生效", "release_calendar RC-JP-BOJ-TARGET-2026-09",
    (dec["effective_on"] <= cutoff, dec["obs_to"] >= cutoff, len(pend)), (True, True, 0),
    lit="截至研究截止 2026-11-23", text=C2)
add("O003", "⑮", "欧央行现行生效水平=序列末观测", "snapshot.series_store.ECB_MRO/ECB_DFR 末观测",
    (C.last_obs(ss, "ECB_MRO"), C.last_obs(ss, "ECB_DFR")), (("2026-09-16", 2.65), ("2026-09-16", 2.5)),
    lit="最新生效水平", text=C2)
nonwed = {}
for mid in ("ECB_MRO", "ECB_DFR"):
    ds, _ = C.series(ss, mid)
    nonwed[mid] = (sum(1 for d in ds if C.D(d).weekday() != 2), len(ds))
add("O004", "⑮", "Q5④ 两序列含非周三观测", "snapshot.series_store.ECB_MRO/ECB_DFR 观测日星期分布",
    (nonwed["ECB_MRO"][0] > 0, nonwed["ECB_DFR"][0] > 0), (True, True),
    lit="两序列含非周三观测", text=QN[5], note="非周三观测数/总观测数: " + json.dumps(nonwed, ensure_ascii=False))
add("O005", "⑮", "Q5④ 引擎原句在场", "MAP_REPORT.md 第65行",
    "ECB_MRO/ECB_DFR 观测日全为周三=生效日" in MAP_MD, True,
    lit="引擎报告文字「观测日全为周三」", text=QN[5])
jc = C.read_text(os.path.join(tree_dir, "scripts", "research_contract", "judgment_contract.py"))
blk = jc[jc.index("# (13) Audit-R22 任务3"):jc.index("# 历史段样本前提")]
labels = list(cells["EA_HICP_YOY"]["anchors"].keys())
rx = re.compile(r"观测\s*(\d{4}-\d{2}(?:-\d{2})?(?:\s*→\s*\d{4}-\d{2}(?:-\d{2})?)+)")
nrx = sum(len(rx.findall(x)) for x in (EA, JP))
add("O006", "⑮", "Q5① 契约锚标签硬编码与本档规避", "tree judgment_contract.py (13) 块 / point_values cells anchors / 走位正文",
    ("for _lbl in ('12个月前', '3个月前', '最新一期'):" in blk, labels, nrx), (True, ["6个月前", "最新一期"], 0),
    lit="锚标签硬编码「12个月前/3个月前/最新一期」", text=QN[5],
    note="本问只有『6个月前/最新一期』两锚,(13) 的标签循环只取到『最新一期』一月,任何 ≥2 个月的『观测 X→Y』串必不成其保序子序列;席位走位正文用『观测月 X』逐锚表述,正则零命中")
tc = C.read_text(os.path.join(tree_dir, "scripts", "research_contract", "text_consistency.py"))
i0 = tc.index("ALIASES = {")
i1 = tc.index("\n}\n", i0)
aliases = ast.literal_eval(tc[i0 + len("ALIASES = "):i1 + 2])
five = ["JP_CPI_YOY", "EA_HICP_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_TARGET", "ECB_MRO"]
add("O007", "⑮", "Q5② 别名表未覆盖五指标", "tree text_consistency.ALIASES keys",
    [i for i in five if i in aliases], [],
    lit="静态别名表未覆盖 JP_CPI_YOY/EA_HICP_YOY/JP_CPI_TOKYO_YOY/JP_POLICY_TARGET/ECB_MRO", text=QN[5],
    note="ALIASES 共 %d 键;近邻键: %s" % (len(aliases), sorted(k for k in aliases if re.search(r"CPI|HICP|ECB|POLICY", k))))
NAMERX = re.compile(r"(ECB_MRO|ECB_DFR|JP_POLICY_RATE|EA_HICP_YOY|JP_CPI_YOY|JP_CPI_TOKYO_YOY|HICP 同比|全国CPI同比|东京都CPI同比"
                    r"|主要再融资利率|存款便利利率|政策目标利率|月均)[^。；;]{0,40}?(\d+\.\d+)")
ar_stmt = sorted(set(m.group(1) for s in (C1, C2, C3) for m in NAMERX.finditer(s)))
add("O008", "⑮", "陈述层『无别名指标数值用中文数字』自述", "agent_judgment l3.contradictions[*].statement 内指标名近邻的阿拉伯小数值",
    ar_stmt, ["存款便利利率", "月均"],
    lit="本档陈述层对无别名指标的数值一律用中文数字表述", text=QN[5],
    note="三条矛盾陈述正文里以阿拉伯小数出现的指标值仅『存款便利利率…2.5%』(ECB_DFR)与『月均…1.227%』(JP_POLICY_RATE),二者均有别名并经契约逐位绑定;其余无别名指标(日本全国CPI/欧元区HICP/东京CPI/BOJ目标/ECB_MRO)数值均为中文数字——自述成立。竞争解释与 reader_map/机制链层用阿拉伯数字,不在『陈述层』之内")
fr_mro = regm["ECB_MRO"]["freshness"]
fr_dfr = regm["ECB_DFR"]["freshness"]
add("O009", "⑮", "注册表决策驱动序列口径(两口径并列的依据)", "registry ECB_MRO/ECB_DFR.freshness",
    (fr_mro.get("decision_dated"), fr_dfr.get("decision_dated"),
     "无更晚已证实决议不作过期" in fr_mro.get("decision_dated_note", ""),
     fr_mro["max_calendar_lag_days"], fr_dfr["max_calendar_lag_days"]), (True, True, True, 10, 10),
    lit="超过注册表新鲜度阈十天", text=C3,
    note="席位只引滞后阈口径(Gate A=degraded);注册表同处另有 decision_dated 口径(无更晚已证实决议不作过期),引擎点值格按后者判 ok——见 PROSE MINOR")
cm = cells["ECB_MRO"]["anchors"]["最新一期"]
cd_ = cells["ECB_DFR"]["anchors"]["最新一期"]
add("O010", "⑮", "引擎点值格对欧央行现值的状态", "report.research_plan.point_values.cells[ECB_*].anchors[最新一期]",
    (cm["status"], cm.get("freshness_basis"), cm.get("policy_confirm_date"), cd_["status"]),
    ("ok", "policy_confirmation", "2026-09-16", "ok"),
    note="引擎点值格未把欧央行现值标过期/未核验(与 Gate A degraded 并存)")
add("O011", "⑮", "同比基期=去年同月(2025-10),非相邻月", "agent_judgment C1 / 总判断",
    ("去年同月(2025-10)为百分之二点九九" in C1, "去年同月(2025-10)为百分之二点一" in C1,
     "(2025-10 为 2.99)" in HL, "(2025-10 为 2.1)" in HL), (True, True, True, True))
add("O012", "⑮", "读者报告官方记录面(日本行)", "MAP_REPORT.md 第71行 + 日历复算",
    ("| 日本 | 1.25 | — | 2026-09-18 | 2026-09-24 | 2026-10-30 | 2026-10-30 | %d天 | %d天 | %d天 | RC-JP-BOJ-TARGET-2026-09(user_directive) |"
     % ((CD - C.D(dec["effective_on"])).days, (CD - C.D(dec["decision_date"])).days, (CD - C.D(mnt["decision_date"])).days)) in MAP_MD,
    True, note="距上次调整(按生效日)/距决议/距维持 = 60/66/24 天,待生效列『—』")
add("O013", "⑮", "引擎面对欧央行决议日的两种表述(范围外)",
    "registry ECB_MRO.{calc,release_semantics} vs 点值格 policy_dates / publication_rule",
    ("管委会决议变更即时生效" in regm["ECB_MRO"]["calc"], cm["policy_dates"]["decision"], cm["policy_dates"]["effective"],
     cm["publication_rule"]), (True, "2026-09-10", "2026-09-16", "ECB 决议日当日公布(变更日观测)"),
    ok=False, sev="SCOPE-OUT",
    note="注册表写『决议变更即时生效/当日更新』,读者报告覆盖表把 2026-09-16 写作『决议日当日公布』,政策表却写决议 09-10→生效 09-16——引擎内部口径不一;席位取政策表面并把决议日标【推断】,生效日 09-16 在两种读法下不变")
add("O014", "⑮", "对质环1『决议日前可见读数』的数值(修订口径注记)", "snapshot.series_store.EA_HICP_YOY",
    (C.mv(ss, "EA_HICP_YOY", "2026-05"), C.mv(ss, "EA_HICP_YOY", "2026-08")), (3.2, 3.2),
    lit="2026-05 的 3.2 与 2026-08 的 3.2", text=TLN[0],
    note="点值格 vintage_semantics=事后回顾(最新修订值,非当时首发值),注册表注明 HICP 近月含回溯修订;判断档未并列此口径(见 PROSE MINOR)")

path = B.save(out_dir)
n = len(B.rows)
nok = B.n_ok()
mis = [r for r in B.rows if not r["ok"] and r.get("sev") != "SCOPE-OUT"]
so = [r for r in B.rows if not r["ok"] and r.get("sev") == "SCOPE-OUT"]
print("PART C: points=%d ok=%d mismatch=%d (judgment mismatches=%d, scope-out observations=%d) -> %s"
      % (n, nok, n - nok, len(mis), len(so), path))
for r in mis:
    print("  MISMATCH", r["id"], r["where"], "| computed:", str(r["computed"])[:200], "| reported:", str(r["reported"])[:200])
for r in so:
    print("  SCOPE-OUT", r["id"], r["where"])
