#!/usr/bin/python3 -I
"""Recompute part A (categories ①-⑥): cutoff, point anchors, YoY, policy face, rates trio, turnings.

Read-only. Args:
  <snapshot.json> <report.json> <agent_judgment.json> <release_calendar.json> <metric_registry.json>
  <run_dir> <tree_dir> <out_dir>
Every point: value computed from the frozen snapshot series_store / frozen calendar / engine faces in
report.json, then compared with the figure in the judgment (structured field or literal in its text).
"""
import importlib.util
import os
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
cells = {c["metric_id"]: c for c in plan["point_values"]["cells"]}
regm = {m["metric_id"]: m for m in reg["metrics"]}
l1 = {r["metric_id"]: r for r in rep["layers"]["L1_事实层"]["rows"]}
SNAP = "research_snapshot_20261123.json"


def T(p):
    return C.get(jd, p)


C1, C2, C3 = (T("l3.contradictions[%d].statement" % i) for i in range(3))
M = [T("l3.mechanism_chains[0].links[%d].text" % i) for i in range(4)]
S1R = T("l4.scenarios[0].rows")
S2R = T("l4.scenarios[1].rows")
HL = T("reader_map.headline_conclusion")
EA = T("reader_map.regions[0].from_to")
JP = T("reader_map.regions[1].from_to")
ECHO = {"EA": T("reader_map.regions[0].anchor_echo"), "JP": T("reader_map.regions[1].anchor_echo")}
TL = [T("reader_map.transmission[0].links[%d]" % i) for i in range(3)]
TN = [T("reader_map.turnings[%d]" % i) for i in range(3)]
QN = T("quality_gate_notes")
ALL = C.all_text(jd)
MAP_MD = C.read_text(os.path.join(run_dir, "MAP_REPORT.md"))

B = C.Book("A")
add = B.add
# engine publication rules as printed in point_values.publication_rule (offset in days from month end)
RULE_OFF = {"JP_CPI_YOY": 20, "EA_HICP_YOY": 16, "JP_CPI_TOKYO_YOY": -1, "JP_POLICY_RATE": 5}


def pub_date(ym, mid):
    y, m = int(ym[:4]), int(ym[5:7])
    return C.add_days(C.month_end(y, m), RULE_OFF[mid])


def latest_published(mid, asof):
    """latest observation month whose rule-based publication date <= asof -> (ym, value, pubdate)."""
    mm = C.monthly(ss, mid)
    best = None
    for ym in sorted(mm):
        pd = pub_date(ym, mid)
        if pd <= asof:
            best = (ym, mm[ym], pd)
    return best


def change_points(mid, min_bp=0.5):
    ds, vs = C.series(ss, mid)
    out = []
    for i in range(1, len(ds)):
        if vs[i] is not None and vs[i - 1] is not None and abs(C.bp(vs[i], vs[i - 1])) >= min_bp:
            out.append((ds[i], vs[i - 1], vs[i]))
    return out


# ---------------------------------------------------------------- ① cutoff
add("A001", "①", "研究截止日", "snapshot.target_date / report.json:research_plan.cutoff",
    C.D(snap["target_date"]).isoformat(), cutoff, lit="2026-11-23", text=HL)
add("A002", "①", "证据截止", "report.json:run.evidence_asof vs research_plan.cutoff",
    rep["run"]["evidence_asof"], cutoff, lit="截至研究截止 2026-11-23", text=C2)
add("A003", "①", "快照时间戳", "snapshot.research_as_of", snap["research_as_of"],
    "2026-11-23T22:53:47+08:00", lit="2026-11-23T22:53:47+08:00", text=QN[4])
tz = C.norm_tz(snap["research_as_of"])
for i, (city, hhmm) in enumerate((("NewYork", "09:53"), ("Berlin", "15:53"), ("Tokyo", "23:53"), ("Shanghai", "22:53"))):
    lit = {"NewYork": "纽约 09:53", "Berlin": "柏林 15:53", "Tokyo": "东京 23:53", "Shanghai": "上海 22:53"}[city]
    add("A%03d" % (4 + i), "①", "快照时间戳时区换算", "snapshot.research_as_of -> %s 本地时间" % city,
        tz.get(city), hhmm, lit=lit, text=QN[4])
import re


def find_paths(o, needle, path="", out=None):
    """JSON paths of every string field containing needle."""
    if out is None:
        out = []
    if isinstance(o, str):
        if needle in o:
            out.append(path)
    elif isinstance(o, dict):
        for k, v in o.items():
            find_paths(v, needle, path + "." + k, out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            find_paths(v, needle, path + "[%d]" % i, out)
    return out


dates = sorted(set(re.findall(r"\d{4}-\d{2}-\d{2}", ALL)))
late = [x for x in dates if C.D(x) > CD]
late_paths = {x: sorted(set(find_paths(jd, x))) for x in late}
ALLOW8 = (".agent_declaration.written_at", ".l4.scenarios", ".quality_gate_notes[3]")
ok8 = bool(late) and all(p.startswith(ALLOW8) for ps in late_paths.values() for p in ps)
add("A008", "①", "晚于截止日的日期字面", "agent_judgment.json 全文正则扫描+逐处路径归类",
    late_paths, "仅成文时间戳(agent_declaration.written_at)或情景时限(l4.scenarios 与 quality_gate_notes[3] 证伪面注记)", ok=ok8,
    note="2026-11-24 仅为成文时间戳(written_at); 2027-02-15 仅为情景时限" if ok8 else "存在事实位引用截止日后日期")
months = sorted(set(re.findall(r"(?<![\d-])\d{4}-\d{2}(?![\d-])", ALL)))
late_m = [x for x in months if x > cutoff[:7]]
late_m_paths = {x: sorted(set(find_paths(jd, x))) for x in late_m}
ok9 = bool(late_m_paths) and all(p.startswith(".l4.scenarios") for ps in late_m_paths.values() for p in ps)
add("A009", "①", "晚于截止月的月份字面", "agent_judgment.json 全文正则扫描+逐处路径归类",
    late_m_paths, "仅情景观测月/入档月(l4.scenarios)", ok=ok9,
    note="截止月后月份须仅出现在情景层(前瞻标注【假设·非预测】)" if ok9 else "存在事实位引用截止月后月份")
add("A010", "①", "最近六个月窗口", "cutoff-6月 vs judgment", C.add_months(CD, -6).isoformat(), "2026-05-23",
    lit="最近六个月(2026-05-23..2026-11-23)", text=C2)
add("A011", "①", "引擎窗口端点", "report.json:research_plan.question_window", plan["question_window"]["windows"][0]["from"] + ".." + plan["question_window"]["windows"][0]["to"],
    "2026-05-23..2026-11-23")
cv = C.load_json(os.path.join(tree_dir, "CODE_VERSION.json"))
add("A012", "①", "代码印章", "report.json:run.git_head / CODE_VERSION.json:git_head",
    rep["run"]["git_head"] == cv["git_head"], True, note=cv["git_head"][:12])
fi = rep["run"]["frozen_inputs"]
for i, (key, fn, pref) in enumerate((("config/release_calendar.json", "config/release_calendar.json", "e44fd2aa5ced0310"),
                                     ("config/metric_registry.json", "config/metric_registry.json", "fa396d22175a4814"),
                                     ("data/daily/research_snapshot_20261123.json", "data/daily/research_snapshot_20261123.json", "2d650f1128cdd356"))):
    h_tree = C.sha256_file(os.path.join(tree_dir, fn))[:16]
    h_run = C.sha256_file(os.path.join(run_dir, "root_overlay", fn))[:16]
    add("A%03d" % (13 + i), "①", "冻结输入哈希", "sha256(%s) 前16位 vs report.json:run.frozen_inputs" % key,
        h_tree, fi[key], note="运行目录 overlay 副本=%s, 协议印章=%s, 三者%s" % (h_run, pref, "一致" if h_tree == h_run == pref == fi[key] else "不一致"))
add("A016", "①", "读者报告校验", "MAP_REPORT.sha256 vs sha256(MAP_REPORT.md)",
    C.sha256_file(os.path.join(run_dir, "MAP_REPORT.md")), C.read_text(os.path.join(run_dir, "MAP_REPORT.sha256")).split()[0])

# publication-rule arithmetic (rule text lives in point_values.publication_rule)
for i, (mid, lit) in enumerate((("JP_CPI_YOY", "发布 2026-11-20"), ("EA_HICP_YOY", "发布 2026-11-16"),
                                ("JP_CPI_TOKYO_YOY", "发布 2026-10-30"))):
    pd_ = pub_date("2026-10", mid).isoformat()
    add("A%03d" % (17 + i), "①", "发布日(推定规则)", "%s:series_store 月末%s天 vs point_values.publication_date" % (SNAP, "%+d" % RULE_OFF[mid]),
        pd_, cells[mid]["anchors"]["最新一期"]["publication_date"], lit=lit, text=C1)
add("A020", "①", "发布日(推定规则)", "JP_POLICY_RATE 月末+5天 vs point_values.publication_date",
    pub_date("2026-10", "JP_POLICY_RATE").isoformat(), cells["JP_POLICY_RATE"]["anchors"]["最新一期"]["publication_date"],
    note="判断档正文未给出 JP_POLICY_RATE 的发布日(仅观测月)")
A6 = C.D(plan["point_anchors"][0]["as_of"])
for i, mid in enumerate(("JP_CPI_YOY", "EA_HICP_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_RATE")):
    lp = latest_published(mid, A6)
    ok = lp is not None and lp[0] == "2026-04" and pub_date("2026-05", mid) > A6
    add("A%03d" % (21 + i), "①", "六个月前锚可见性", "%s:series_store + 推定规则: 发布日≤%s 的最新观测月; 次月发布日=%s" % (SNAP, A6, pub_date("2026-05", mid)),
        lp[0] if lp else None, "2026-04", ok=ok)
ecb_cal = [e for e in cal["entries"] if e.get("metric_id") in ("ECB_MRO", "ECB_DFR") or "ECB" in str(e.get("metric_id", ""))]
cal_hit = [e["entry_id"] for e in cal["entries"] if e.get("metric_id") in ("JP_CPI_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_RATE", "ECB_MRO", "ECB_DFR")
           or (e.get("metric_id") == "EA_HICP_YOY" and e.get("obs_from", "") >= "2026-01-01")]
add("A025", "①", "日历优先/无实录", "release_calendar.json:entries 命中检索", cal_hit, [],
    lit="引擎推定规则、非日历实录", text=C1, note="命中空集=只能用推定规则")
ea_cal = [e for e in cal["entries"] if e.get("metric_id") == "EA_HICP_YOY"]


def next_month_first(obs_from):
    y, m = int(obs_from[:4]), int(obs_from[5:7])
    return "%04d-%02d-01" % (y + m // 12, m % 12 + 1)


tier = [(e["entry_id"], next_month_first(e["obs_from"]), e["first_publish_on_or_after"], e.get("final_publish_on")) for e in ea_cal]
two_tier = [t[1] == t[2] and bool(t[3]) for t in tier]
add("A026", "①", "EA HICP 日历实录形态", "release_calendar.json:entries EA_HICP_YOY(%d 条): 快报日=次月首日 且 有终值日" % len(ea_cal),
    (len(ea_cal), all(two_tier)), (3, True), lit="次月首日快报+月中终值", text=TL[0]["verdict_note"],
    note="实录: " + "; ".join("%s 快报 %s/终值 %s" % (t[0], t[2], t[3]) for t in tier))

# ---------------------------------------------------------------- ② point anchors
ANCH = [(p["label"], C.D(p["as_of"])) for p in plan["point_anchors"]]
LITV = {"EA_HICP_YOY": ("3.0%", "4.0%"), "ECB_MRO": ("2.15%", "2.65%"), "ECB_DFR": ("2.0%", "2.5%"),
        "JP_CPI_YOY": ("1.38%", "2.44%"), "JP_CPI_TOKYO_YOY": ("1.42%", "2.73%"), "JP_POLICY_RATE": ("0.727%", "1.227%")}
n = 1
for mid in ("EA_HICP_YOY", "ECB_MRO", "ECB_DFR", "JP_CPI_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_RATE"):
    reg_ = "EA" if mid.startswith(("EA", "ECB")) else "JP"
    txt = EA if reg_ == "EA" else JP
    for k, (lab, asof) in enumerate(ANCH):
        if mid in RULE_OFF:
            lp = latest_published(mid, asof)
            obs_date, v = lp[0] + "-01", lp[1]
            src = "%s:series_store.%s[%s]+推定规则(发布日≤%s)" % (SNAP, mid, lp[0], asof)
        else:
            lo = C.last_on_or_before(ss, mid, asof)
            obs_date, v = lo
            src = "%s:series_store.%s 发布日≤%s 的最后观测" % (SNAP, mid, asof)
        anc = cells[mid]["anchors"][lab]
        add("B%03d" % n, "②", "%s 走位/点值格" % reg_, src, v, anc["value"], lit=LITV[mid][k], text=txt); n += 1
        add("B%03d" % n, "②", "%s 点值格" % reg_, src + " 观测日", obs_date, anc["observation_date"]); n += 1
        ech = [e for e in ECHO[reg_] if e["metric_id"] == mid and e["anchor"] == lab][0]
        add("B%03d" % n, "②", "%s anchor_echo" % reg_, src, (v, obs_date[:7]), (ech["value"], ech["observation_month"]),
            lit=LITV[mid][k], text=txt); n += 1

# ---------------------------------------------------------------- ③ YoY
add("C001", "③", "C1 去年同月基期", SNAP + ":series_store.JP_CPI_YOY[2025-10-01]", C.mv(ss, "JP_CPI_YOY", "2025-10"), 2.99,
    lit="去年同月(2025-10)为百分之二点九九", text=C1)
add("C002", "③", "C1 同比读数差", "JP_CPI_YOY 2026-10 − 2025-10", C.rnd(C.mv(ss, "JP_CPI_YOY", "2026-10") - C.mv(ss, "JP_CPI_YOY", "2025-10"), 2), -0.55,
    lit="回落约零点五五个百分点", text=C1)
add("C003", "③", "C1 基期=同月(非相邻月)", SNAP + ":series_store.JP_CPI_YOY dates 含 2025-10-01",
    "2025-10-01" in ss["JP_CPI_YOY"]["dates"], True)
add("C004", "③", "C1 去年同月基期", SNAP + ":series_store.EA_HICP_YOY[2025-10-01]", C.mv(ss, "EA_HICP_YOY", "2025-10"), 2.1,
    lit="去年同月(2025-10)为百分之二点一", text=C1)
add("C005", "③", "C1 同比读数差", "EA_HICP_YOY 2026-10 − 2025-10", C.rnd(C.mv(ss, "EA_HICP_YOY", "2026-10") - C.mv(ss, "EA_HICP_YOY", "2025-10"), 2), 1.9,
    lit="抬升一点九个百分点", text=C1)
add("C006", "③", "C1 基期=同月(非相邻月)", SNAP + ":series_store.EA_HICP_YOY dates 含 2025-10-01",
    "2025-10-01" in ss["EA_HICP_YOY"]["dates"], True)
add("C007", "③", "C1 东京基期缺席", SNAP + ":series_store.JP_CPI_TOKYO_YOY[2025-10-01]", C.mv(ss, "JP_CPI_TOKYO_YOY", "2025-10"), None,
    lit="序列自 2026-01 起,去年同月基期观测不可得", text=C1)
add("C008", "③", "C1 东京序列起点", SNAP + ":series_store.JP_CPI_TOKYO_YOY 首观测", C.first_obs(ss, "JP_CPI_TOKYO_YOY")[0], "2026-01-01",
    lit="序列自 2026-01 起", text=C1)
add("C009", "③", "总判断 方向词", "JP_CPI_YOY 2026-10 < 2025-10", C.mv(ss, "JP_CPI_YOY", "2026-10") < C.mv(ss, "JP_CPI_YOY", "2025-10"), True,
    lit="低于去年同月(2025-10 为 2.99)", text=HL)
add("C010", "③", "总判断 方向词", "EA_HICP_YOY 2026-10 > 2025-10", C.mv(ss, "EA_HICP_YOY", "2026-10") > C.mv(ss, "EA_HICP_YOY", "2025-10"), True,
    lit="高于去年同月(2025-10 为 2.1)", text=HL)
up = (C.mv(ss, "JP_CPI_YOY", "2026-10") > C.mv(ss, "JP_CPI_YOY", "2026-04")) and (C.mv(ss, "EA_HICP_YOY", "2026-10") > C.mv(ss, "EA_HICP_YOY", "2026-04"))
add("C011", "③", "总判断 较六个月前锚", "JP_CPI_YOY/EA_HICP_YOY 2026-10 vs 2026-04", up, True,
    lit="较六个月前锚两地读数均上行", text=HL)
add("C012", "③", "JP 走位", "JP_CPI_YOY 2025-10 − 2026-10", C.rnd(C.mv(ss, "JP_CPI_YOY", "2025-10") - C.mv(ss, "JP_CPI_YOY", "2026-10"), 2), 0.55,
    lit="低 0.55 个百分点", text=JP)
add("C013", "③", "EA 走位", "EA_HICP_YOY 2026-10 − 2025-10", C.rnd(C.mv(ss, "EA_HICP_YOY", "2026-10") - C.mv(ss, "EA_HICP_YOY", "2025-10"), 2), 1.9,
    lit="高 1.9 个百分点", text=EA)
eam = C.monthly(ss, "EA_HICP_YOY")
last12 = [(k, eam[k]) for k in sorted(eam) if k >= C.add_months(CD, -12).strftime("%Y-%m")]
mx = max(last12, key=lambda kv: kv[1])
add("C014", "③", "EA 走位 关系词", "EA_HICP_YOY 近十二个月(%s..%s)最大值" % (last12[0][0], last12[-1][0]), mx, ("2026-10", 4.0),
    lit="最新读数为近十二个月最高", text=EA)
tr = min(last12, key=lambda kv: kv[1])
add("C015", "③", "EA 走位 谷底", "EA_HICP_YOY 近十二个月最小值", tr, ("2026-01", 1.7), lit="2026-01 谷底 1.7", text=EA)
jpm = C.monthly(ss, "JP_CPI_YOY")
last12j = [(k, jpm[k]) for k in sorted(jpm) if k >= C.add_months(CD, -12).strftime("%Y-%m")]
trj = min(last12j, key=lambda kv: kv[1])
add("C016", "③", "JP 走位 谷底", "JP_CPI_YOY 近十二个月最小值", trj, ("2026-02", 1.27), lit="至 2026-02 的 1.27", text=JP)
add("C017", "③", "JP 同比口径", "metric_registry.json:JP_CPI_YOY.calc", "严格同月同比后拼接(新基优先,重叠差>0.10pp 告警)" in regm["JP_CPI_YOY"]["calc"], True,
    lit="2025基/2020基 拼接 同月同比(新基优先,重叠差>0.10pp 告警)", text=M[0])
add("C018", "③", "EA 同比口径", "metric_registry.json:EA_HICP_YOY.calc 含『年度变化率』", "年度变化率" in regm["EA_HICP_YOY"]["calc"], True,
    lit="欧元区HICP同比", text=C1)

# ---------------------------------------------------------------- ④ policy face
mro_cp = change_points("ECB_MRO")
dfr_cp = change_points("ECB_DFR")
add("D001", "④", "C2 ECB_MRO 最后观测日", SNAP + ":series_store.ECB_MRO[-1]", C.last_obs(ss, "ECB_MRO")[0], "2026-09-16",
    lit="观测=序列变更日=生效日 2026-09-16", text=C2)
add("D002", "④", "C2 ECB_MRO 现行水平", SNAP + ":series_store.ECB_MRO[2026-09-16]", C.last_obs(ss, "ECB_MRO")[1], 2.65,
    lit="最新生效水平为 二点六五", text=C2)
add("D003", "④", "C2 ECB_DFR 现行水平", SNAP + ":series_store.ECB_DFR[2026-09-16]", C.last_obs(ss, "ECB_DFR")[1], 2.5,
    lit="最新生效水平 2.5%", text=C2)
add("D004", "④", "C2 ECB_DFR 同日", SNAP + ":series_store.ECB_DFR[-1] 日期", C.last_obs(ss, "ECB_DFR")[0], "2026-09-16",
    lit="同一变更日(2026-09-16)", text=C2)
pwp = {m: cells[m]["policy_window_path"] for m in ("ECB_MRO", "ECB_DFR", "JP_POLICY_RATE")}
for i, (cp, mid) in enumerate(((mro_cp[-2], "ECB_MRO"), (mro_cp[-1], "ECB_MRO"), (dfr_cp[-2], "ECB_DFR"), (dfr_cp[-1], "ECB_DFR"))):
    ev = pwp[mid]["events"][i % 2]
    add("D%03d" % (5 + i), "④", "政策变更点", "%s:series_store.%s 变更点 %s" % (SNAP, mid, cp[0]),
        (cp[0], cp[1], cp[2], int(round(C.bp(cp[2], cp[1])))), (ev["date"], ev["from"], ev["to"], ev["delta_bp"]))
add("D009", "④", "生效日=周三", "weekday(2026-09-16)", C.WD[C.D("2026-09-16").weekday()], "Wed")
add("D010", "④", "生效日=周三", "weekday(2026-06-17)", C.WD[C.D("2026-06-17").weekday()], "Wed")
add("D011", "④", "C2 决议日(回推)", "生效日前上一个周四(2026-09-16)", C.prev_weekday(C.D("2026-09-16"), 3).isoformat(), "2026-09-10",
    lit="决议日 2026-09-10 系引擎按", text=C2)
add("D012", "④", "C2 决议日(回推)", "生效日前上一个周四(2026-06-17)", C.prev_weekday(C.D("2026-06-17"), 3).isoformat(), "2026-06-11",
    lit="对应决议日 2026-06-11", text=C2)
add("D013", "④", "传导环1 间隔", "2026-09-16 − 2026-06-17 (天)", (C.D("2026-09-16") - C.D("2026-06-17")).days, 91,
    lit="两次变更相隔 91 天", text=TL[0]["verdict_note"])
add("D014", "④", "C3 观测滞后", "cutoff − 2026-09-16 (天)", (CD - C.D("2026-09-16")).days, 68, lit="六十八天", text=C3)
add("D015", "④", "C3 滞后(总判断)", "cutoff − 2026-09-16 (天)", (CD - C.D("2026-09-16")).days, 68, lit="距截止 68 天", text=HL)
add("D016", "④", "C3 新鲜度阈", "metric_registry.json:ECB_MRO.freshness.max_calendar_lag_days", regm["ECB_MRO"]["freshness"]["max_calendar_lag_days"], 10,
    lit="超过注册表新鲜度阈十天", text=C3,
    note="注册表同处另有 decision_dated 注记(无更晚已证实决议不作过期);引擎点值格 freshness_basis=policy_confirmation/status=ok——见问题清单 MINOR")
deg = snap["gate_a"]["noncore_degraded"]
add("D017", "④", "C3 Gate A", "snapshot.gate_a.noncore_degraded 含 ECB_MRO/ECB_DFR", [m for m in ("ECB_MRO", "ECB_DFR") if m in deg], ["ECB_MRO", "ECB_DFR"],
    lit="Gate A 两序列列于 degraded 名单", text=C3)
add("D018", "④", "C3 L1 质量", "report.json:L1 rows quality_status", (l1["ECB_MRO"]["quality_status"], l1["ECB_DFR"]["quality_status"]), ("DEGRADED", "DEGRADED"),
    lit="L1 事实行 quality_status=DEGRADED", text=C3)
add("D019", "④", "C3 日历无 ECB 实录", "release_calendar.json:entries", ecb_cal, [], lit="对欧央行无实录条目", text=C3)
boj = {e["entry_id"]: e for e in cal["entries"] if e.get("metric_id") == "JP_POLICY_TARGET"}
bt = boj.get("RC-JP-BOJ-TARGET-2026-09", {})
bm = boj.get("RC-JP-BOJ-MAINT-2026-10", {})
add("D020", "④", "C2 BOJ 决议日", "release_calendar.json:RC-JP-BOJ-TARGET-2026-09.decision_date", bt.get("decision_date"), "2026-09-18",
    lit="约一点二五,2026-09-18 决议、2026-09-24 生效", text=C2)
add("D021", "④", "C2 BOJ 生效日", "release_calendar.json:RC-JP-BOJ-TARGET-2026-09.effective_on", bt.get("effective_on"), "2026-09-24", lit="2026-09-24 生效", text=C2)
add("D022", "④", "C2 BOJ 目标值", "release_calendar.json:RC-JP-BOJ-TARGET-2026-09.target_value", bt.get("target_value"), 1.25, lit="约一点二五", text=C2)
add("D023", "④", "C2 BOJ 确认维持", "release_calendar.json:RC-JP-BOJ-MAINT-2026-10", (bm.get("decision_date"), bm.get("target_value"), bm.get("kind")),
    ("2026-10-30", 1.25, "policy_maintenance"), lit="2026-10-30 会议确认维持不变(无新调整、无生效变动)", text=C2)
add("D024", "④", "C2 无待生效决定", "release_calendar.json 全部条目 effective_on > 截止日 计数",
    [e["entry_id"] for e in cal["entries"] if e.get("effective_on") and e["effective_on"] > cutoff], [],
    lit="可核行动均已生效、无未生效决议", text=C2)
add("D025", "④", "C2 维持后天数", "cutoff − 2026-10-30 (天)", (CD - C.D("2026-10-30")).days, 24, lit="二十四天内", text=C2)
add("D026", "④", "读者报告 距上次调整", "cutoff − effective_on / decision_date / 维持日 (天)",
    "%d天|%d天|%d天" % ((CD - C.D(bt["effective_on"])).days, (CD - C.D(bt["decision_date"])).days, (CD - C.D(bm["decision_date"])).days),
    "60天|66天|24天", lit="| 60天 | 66天 | 24天 | RC-JP-BOJ-TARGET-2026-09(user_directive) |", text=MAP_MD)
add("D027", "④", "BOJ 首发日", "RC-JP-BOJ-TARGET-2026-09.first_publish_on_or_after", bt.get("first_publish_on_or_after"), bt.get("decision_date"))
win_ecb = [c for c in mro_cp if C.add_months(CD, -6) <= C.D(c[0]) <= CD]
add("D028", "④", "C2 窗内上调次数", "ECB_MRO 变更点落在 [2026-05-23, 2026-11-23]", len(win_ecb), 2, lit="窗内两次上调", text=C2)
add("D029", "④", "JP 走位 目标口径缺席", "metric_registry.json:metrics 含 JP_POLICY_TARGET", "JP_POLICY_TARGET" in regm, False,
    lit="注册表无 JP_POLICY_TARGET", text=JP)
add("D030", "④", "C2 月均≠宣布值", "metric_registry.json:JP_POLICY_RATE.calc", "月均" in regm["JP_POLICY_RATE"]["calc"] and "与BOJ决议目标值口径不同" in regm["JP_POLICY_RATE"]["calc"], True,
    lit="月均口径非宣布值", text=C2)
add("D031", "④", "传导环2 联邦基金目标区间", SNAP + ":series_store.DFEDTARL/DFEDTARU[2026-11-23]",
    (C.val_at(ss, "DFEDTARL", "2026-11-23"), C.val_at(ss, "DFEDTARU", "2026-11-23")), (3.75, 4.0),
    lit="联邦基金目标区间 3.75%–4.00%", text=TL[1]["verdict_note"])
fed_cp = change_points("DFEDTARU")
add("D032", "④", "传导环2 美联储生效日", SNAP + ":series_store.DFEDTARU 最后变更点", fed_cp[-1][0], "2026-09-17",
    lit="美联储 2026-09-17 生效", text=TL[1]["verdict_note"])
eidx = {r["ref"] for r in rep["evidence_index"]}
add("D033", "④", "传导环2 索引外引用披露", "report.json:evidence_index 含 DFEDTARL/U", sorted(r for r in eidx if r.startswith("DFEDTAR")), [],
    lit="不在本轮证据索引", text=TL[1]["verdict_note"])
jpmr = C.monthly(ss, "JP_POLICY_RATE")
add("D034", "④", "JP 走位 近12月净变动", "JP_POLICY_RATE 2026-10 − 2025-11 (bp)", C.rnd(C.bp(jpmr["2026-10"], jpmr["2025-11"]), 0), 75,
    lit="约 +75bp", text=JP)
jcp = [c for c in change_points("JP_POLICY_RATE") if C.D(c[0]) > C.add_months(CD, -12)]
add("D035", "④", "JP 走位 变动点之和", "JP_POLICY_RATE 窗内(>2025-11-23)变动点 bp 之和", int(sum(round(C.bp(c[2], c[1])) for c in jcp)), 75,
    lit="净 +75bp=六个变动点之和", text=JP)
add("D036", "④", "JP 走位 变动点个数", "同上 变动点个数", len(jcp), 6)
add("D037", "④", "JP 走位 一年窗", "research_plan.point_values.JP_POLICY_RATE.policy_window_path.window",
    "%s..%s" % tuple(pwp["JP_POLICY_RATE"]["window"]), "2025-11-23..2026-11-23", lit="窗口 2025-11-23..2026-11-23", text=JP)
add("D038", "④", "M1-2 月均台阶", SNAP + ":series_store.JP_POLICY_RATE 2026-09/2026-10", (jpmr["2026-09"], jpmr["2026-10"]), (1.043, 1.227),
    lit="1.043→1.227", text=M[1])
add("D039", "④", "C2 月均锚", "JP_POLICY_RATE 2026-04 / 2026-10", (jpmr["2026-04"], jpmr["2026-10"]), (0.727, 1.227),
    lit="最新一期报 1.227%,六个月前锚前值为零点七二七", text=C2)
add("D040", "④", "C2 月均起点", "JP_POLICY_RATE 2025-11", jpmr["2025-11"], 0.478, lit="自 2025-11 月均零点四七八升至 2026-10 月均一点二二七", text=C2)
for i, mid in enumerate(("ECB_MRO", "ECB_DFR")):
    evs = pwp[mid]["events"]
    add("D%03d" % (41 + i), "④", "读者报告 一年窗净变动闭合", "%s policy_window_path 净变动 vs 变动点之和 vs 序列首尾差" % mid,
        (pwp[mid]["net_bp"], sum(e["delta_bp"] for e in evs), int(round(C.bp(C.last_obs(ss, mid)[1], evs[0]["from"])))),
        (50, 50, 50))

# ---------------------------------------------------------------- ⑤ rates trio + asset echo
trio = plan["us_rates_trio"]
u0, u1 = C.val_at(ss, "UST_10Y", "2026-10-20"), C.val_at(ss, "UST_10Y", "2026-11-19")
t0, t1 = C.val_at(ss, "TIPS_10Y", "2026-10-20"), C.val_at(ss, "TIPS_10Y", "2026-11-19")
b0, b1 = C.val_at(ss, "BEI_10Y", "2026-10-20"), C.val_at(ss, "BEI_10Y", "2026-11-19")
rd = jd["reader_map"]["rates_decomposition"]
add("E001", "⑤", "rates_decomposition 名义", SNAP + ":series_store.UST_10Y 2026-10-20→2026-11-19 (bp) (%.2f→%.2f)" % (u0, u1),
    C.rnd(C.bp(u1, u0), 1), rd["nominal_bp"])
add("E001b", "⑤", "rates_decomposition 名义(引擎面)", "research_plan.us_rates_trio.chg_bp.UST_10Y vs reader_map", trio["chg_bp"]["UST_10Y"], rd["nominal_bp"])
add("E002b", "⑤", "rates_decomposition 实际(引擎面)", "us_rates_trio.chg_bp.TIPS_10Y vs reader_map", trio["chg_bp"]["TIPS_10Y"], rd["real_bp"])
add("E003b", "⑤", "rates_decomposition 盈亏平衡(引擎面)", "us_rates_trio.chg_bp.BEI_10Y vs reader_map", trio["chg_bp"]["BEI_10Y"], rd["bei_bp"])
add("E002", "⑤", "rates_decomposition 实际", "TIPS_10Y 2026-10-20→2026-11-19 (bp) (%.2f→%.2f)" % (t0, t1), C.rnd(C.bp(t1, t0), 1), rd["real_bp"])
add("E003", "⑤", "rates_decomposition 盈亏平衡", "BEI_10Y 2026-10-20→2026-11-19 (bp) (%.2f→%.2f)" % (b0, b1), C.rnd(C.bp(b1, b0), 1), rd["bei_bp"])
add("E004", "⑤", "名义=实际+盈亏平衡", "Δ名义 − (Δ实际+ΔBEI) 残差(bp)", C.rnd(C.bp(u1, u0) - (C.bp(t1, t0) + C.bp(b1, b0)), 6), 0.0)
add("E005", "⑤", "水平恒等", "2026-11-19: UST_10Y − (TIPS_10Y+BEI_10Y)", C.rnd(u1 - (t1 + b1), 6), 0.0)
add("E006", "⑤", "rates_decomposition 窗起", "UST_10Y 2026-10-20 在场=三序列共同日", rd["window_from"], trio["window"]["from"])
_last3 = (C.last_obs(ss, "UST_10Y")[0], C.last_obs(ss, "TIPS_10Y")[0], C.last_obs(ss, "BEI_10Y")[0])
_common = [d for d in ss["UST_10Y"]["dates"] if d in ss["TIPS_10Y"]["dates"] and d in ss["BEI_10Y"]["dates"]]
add("E007", "⑤", "rates_decomposition 窗止", "三序列共同交易日最后一天 vs us_rates_trio.window.to(三序列各自最后观测 %s/%s/%s)" % _last3,
    _common[-1], rd["window_to"], note="引擎窗=共同交易日; BEI_10Y 单独另有 2026-11-20 观测(名义/实际无同日观测,不入共同窗)")
u12, t12, b12 = C.val_at(ss, "UST_10Y", "2025-11-19"), C.val_at(ss, "TIPS_10Y", "2025-11-19"), C.val_at(ss, "BEI_10Y", "2025-11-19")
add("E008", "⑤", "12个月窗 名义", "UST_10Y 2025-11-19→2026-11-19 (bp)", C.rnd(C.bp(u1, u12), 1), trio["chg_bp_12m"]["UST_10Y"])
add("E009", "⑤", "12个月窗 实际", "TIPS_10Y 2025-11-19→2026-11-19 (bp)", C.rnd(C.bp(t1, t12), 1), trio["chg_bp_12m"]["TIPS_10Y"])
add("E010", "⑤", "12个月窗 盈亏平衡", "BEI_10Y 2025-11-19→2026-11-19 (bp)", C.rnd(C.bp(b1, b12), 1), trio["chg_bp_12m"]["BEI_10Y"])
am = {r["metric_id"]: r for r in plan["asset_moves"]["rows"]}
echo = {e["metric_id"]: e for e in jd["reader_map"]["asset_returns_echo"]}
for i, mid in enumerate(("NIKKEI225", "DAX", "SPX", "VIX")):
    lo = C.last_on_or_before(ss, mid, CD)
    add("E%03d" % (11 + i), "⑤", "asset_returns_echo", "%s:series_store.%s 2026-10-23→%s" % (SNAP, mid, lo[0]),
        C.rnd(C.pct(lo[1], C.val_at(ss, mid, "2026-10-23")), 2), echo[mid]["chg_pct"],
        ok=None)
    e_ = echo[mid]
    if not (e_["window"]["from"] == "2026-10-23" and e_["window"]["to"] == lo[0] and am[mid]["window"] == e_["window"]):
        B.rows[-1]["ok"] = False
    B.rows[-1]["note"] = "窗口 %s..%s(引擎 asset_moves 同窗)" % (e_["window"]["from"], e_["window"]["to"])
v20, v23 = C.val_at(ss, "VIX", "2026-11-20"), C.val_at(ss, "VIX", "2026-11-23")
add("E015", "⑤", "M1-4 VIX 盘中较收盘", "VIX 2026-11-23 vs 2026-11-20", C.rnd(C.pct(v23, v20), 2), -24.7, lit="较 2026-11-20 收盘 -24.7%", text=M[3])
add("E016", "⑤", "M1-3 UST_10Y", "UST_10Y 最后观测", C.last_obs(ss, "UST_10Y"), ("2026-11-19", 5.04), lit="UST_10Y 最新 5.04%", text=M[2])

# ---------------------------------------------------------------- ⑥ turnings
cand = plan["turning_candidates"]["candidates"]
tn = jd["reader_map"]["turnings"]
for i in range(3):
    t = tn[i]
    c = [x for x in cand if x["metric_id"] == t["metric_id"] and x["from_ym"] == t["before_date"] and x["to_ym"] == t["date"]]
    mm = C.monthly(ss, t["metric_id"])
    add("F%03d" % (1 + 4 * i), "⑥", "转折%d 候选面同源" % (i + 1), "research_plan.turning_candidates.candidates",
        [(x["from_ym"], x["to_ym"], x["value_before"], x["value_after"]) for x in c], [(t["before_date"], t["date"], t["value_before"], t["value_after"])])
    add("F%03d" % (2 + 4 * i), "⑥", "转折%d 前值" % (i + 1), "%s:series_store.%s[%s]" % (SNAP, t["metric_id"], t["before_date"]), mm[t["before_date"]], t["value_before"])
    add("F%03d" % (3 + 4 * i), "⑥", "转折%d 后值" % (i + 1), "%s:series_store.%s[%s]" % (SNAP, t["metric_id"], t["date"]), mm[t["date"]], t["value_after"])
    add("F%03d" % (4 + 4 * i), "⑥", "转折%d 幅度" % (i + 1), "后值−前值", C.rnd(mm[t["date"]] - mm[t["before_date"]], 3 if i == 2 else 2), c[0]["delta"])
add("F013", "⑥", "转折1 关系词", "候选池 |delta| 最大者", max(cand, key=lambda x: abs(x["delta"]))["metric_id"] + "@" + max(cand, key=lambda x: abs(x["delta"]))["to_ym"], "JP_CPI_YOY@2026-02",
    lit="候选池内最大单段变动", text=TN[0]["first_mover"])
add("F014", "⑥", "转折1 首变", "JP_CPI_YOY 2025-11→2026-02", (jpm["2025-11"], jpm["2026-02"]), (2.9, 1.27),
    lit="2025-11→2026-02 由 2.9 降至 1.27(三个月 -1.63 个百分点", text=TN[0]["first_mover"])
add("F015", "⑥", "转折1 同向", "EA_HICP_YOY 2025-11→2026-02", (eam["2025-11"], eam["2026-02"]), (2.1, 1.9),
    lit="同期欧元区 HICP 亦下行(2025-11 2.1→2026-02 1.9)", text=TN[0]["follow_or_diverge"])
add("F016", "⑥", "转折1 谷底相邻", "两序列近十二个月谷底月", (tr[0], trj[0]), ("2026-01", "2026-02"),
    lit="两地谷底相邻(欧元区 2026-01 的 1.7、日本 2026-02 的 1.27)", text=TN[0]["follow_or_diverge"])
add("F017", "⑥", "转折1 谷底月相差", "谷底月差(月): 日本谷底月 − 欧元区谷底月",
    (int(trj[0][:4]) * 12 + int(trj[0][5:7])) - (int(tr[0][:4]) * 12 + int(tr[0][5:7])), 1,
    lit="按谷底月欧元区(2026-01)先于日本(2026-02)一个月转入上行", text=TN[0]["follow_or_diverge"])
add("F018", "⑥", "转折1 候选面排序", "候选面转折日(区间终点月)", [x["to_ym"] for x in cand if x["metric_id"] in ("JP_CPI_YOY", "EA_HICP_YOY")], ["2026-02", "2026-05"],
    lit="则为日本(2026-02)先于欧元区(2026-05)", text=TN[0]["follow_or_diverge"])
k = 19
for ym, v in (("2026-03", 1.46), ("2026-04", 1.38), ("2026-05", 1.53), ("2026-06", 1.67), ("2026-07", 1.97), ("2026-08", 1.98), ("2026-09", 2.16), ("2026-10", 2.44)):
    add("F%03d" % k, "⑥", "转折1 叙述路径", "%s:series_store.JP_CPI_YOY[%s]" % (SNAP, ym), jpm[ym], v,
        lit="%s %s" % (ym, ("%.2f" % v)), text=TN[0]["narrative"]); k += 1
add("F%03d" % k, "⑥", "转折1 叙述 BOJ 台阶", "JP_POLICY_RATE[2026-01]", jpmr["2026-01"], 0.728, lit="BOJ 月均台阶(2026-01 0.728)", text=TN[0]["narrative"]); k += 1
for ym, v in (("2026-06", 2.8), ("2026-07", 2.9), ("2026-08", 3.2), ("2026-09", 3.8), ("2026-10", 4.0)):
    add("F%03d" % k, "⑥", "转折2 叙述路径", "%s:series_store.EA_HICP_YOY[%s]" % (SNAP, ym), eam[ym], v,
        lit="%s %s" % (ym, ("%.1f" % v)), text=TN[1]["narrative"]); k += 1
add("F%03d" % k, "⑥", "转折2 日本同窗", "JP_CPI_YOY 2026-02→2026-05", (jpm["2026-02"], jpm["2026-05"]), (1.27, 1.53),
    lit="2026-02 1.27→2026-05 1.53", text=TN[1]["follow_or_diverge"]); k += 1
add("F%03d" % k, "⑥", "转折2 先后未定", "同月分辨率不可判→须写『先后未定』", "月频先后未定" in TN[1]["follow_or_diverge"], True,
    lit="月频先后未定", text=TN[1]["follow_or_diverge"]); k += 1
add("F%03d" % k, "⑥", "转折3 过渡月", "JP_POLICY_RATE[2026-06]", jpmr["2026-06"], 0.841, lit="经 2026-06 0.841 过渡", text=TN[2]["first_mover"]); k += 1
for ym, v in (("2026-08", 0.977), ("2026-09", 1.043), ("2026-10", 1.227)):
    add("F%03d" % k, "⑥", "转折3 叙述路径", "%s:series_store.JP_POLICY_RATE[%s]" % (SNAP, ym), jpmr[ym], v,
        lit="%s %s" % (ym, ("%.3f" % v)), text=TN[2]["narrative"]); k += 1
add("F%03d" % k, "⑥", "转折3 先后未定", "月频台阶 vs 欧央行变更日→须写『先后未定』", "先后未定" in TN[2]["follow_or_diverge"], True,
    lit="先后未定", text=TN[2]["follow_or_diverge"]); k += 1
DIM = {"JP_CPI_YOY": "inflation", "EA_HICP_YOY": "inflation", "JP_POLICY_RATE": "policy"}
add("F%03d" % k, "⑥", "三转折=不同事件", "转折 (metric_id,date) 去重数 / 指标维度数 / 地区数",
    (len({(t["metric_id"], t["date"]) for t in tn}), len({DIM[t["metric_id"]] for t in tn}), len({t["metric_id"][:2] for t in tn})), (3, 2, 2),
    note="三个不同事件(JP_CPI_YOY@2026-02 / EA_HICP_YOY@2026-05 / JP_POLICY_RATE@2026-07); 指标维度=通胀(日/欧元区两序列)+政策; 地区 JP/EA")

out = B.save(out_dir)
bad = [r for r in B.rows if not r["ok"]]
print("PART A: points=%d ok=%d mismatch=%d -> %s" % (len(B.rows), B.n_ok(), len(bad), out))
for r in bad:
    print("  MISMATCH", r["id"], r["cat"], r["where"], "| computed=", r["computed"], "| reported=", r["reported"], "| lit_found=", r["lit_found"], "|", r["note"])
