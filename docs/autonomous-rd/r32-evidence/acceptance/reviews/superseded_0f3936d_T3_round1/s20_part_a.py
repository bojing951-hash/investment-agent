# -*- coding: utf-8 -*-
"""s20_part_a.py —— ①研究截止日 ②点值锚格 ③同比 ④政策面 ⑤三利率分解与资产月窗。
在 s20_recompute.py 的命名空间内 exec;只读复算,本文件不写任何文件。"""
from datetime import timezone

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None

CUTD, A6MD = D(CUT), D(A6M)
run = rep["run"]
with open(os.path.join(RUN_DIR, "MAP_REPORT.md"), encoding="utf-8") as _fh:
    MAP_TEXT = _fh.read()
with open(os.path.join(RUN_DIR, "report.md"), encoding="utf-8") as _fh:
    REPMD_TEXT = _fh.read()

# =====================================================================
# ① 研究截止日
# =====================================================================
ra = snap["research_as_of"]
add("A01", "①", "截止日=快照 research_as_of 日期", "snapshot.research_as_of", ra[:10], CUT,
    ra[:10] == CUT and "研究截止日=2026-11-23" in JT, "判断档 QGN[4]「研究截止日=2026-11-23」")
td = snap["target_date"]
add("A02", "①", "截止日=快照 target_date", "snapshot.target_date",
    "%s-%s-%s" % (td[:4], td[4:6], td[6:]), CUT, td == "20261123", "")
add("A03", "①", "研究计划 cutoff", "research_plan.cutoff", RP["cutoff"], CUT, RP["cutoff"] == CUT, "")
add("A04", "①", "证据截止", "run.evidence_asof", run["evidence_asof"], CUT, run["evidence_asof"] == CUT, "")
eg = run["evidence_gate"]
add("A05", "①", "证据门截止日与源快照", "run.evidence_gate.asof / source_snapshot_id",
    "%s / %s" % (eg["as_of"], eg["source_snapshot_id"]), "%s / %s" % (CUT, snap["snapshot_id"]),
    eg["as_of"] == CUT and eg["source_snapshot_id"] == snap["snapshot_id"], "")
ts = run["ts_utc"]
add("A06", "①", "运行时间戳(UTC)=运行目录名前缀", "run.ts_utc", ts, os.path.basename(RUN_DIR)[:16],
    ts == os.path.basename(RUN_DIR)[:16], "UTC 2026-11-23 19:21:15 = 北京 2026-11-24 03:21:15")
wa = aj["agent_declaration"]["written_at"]
wu = datetime.fromisoformat(wa).astimezone(timezone.utc)
aa = rep["agent_judgment"]["attached_at"]
au = datetime.strptime(aa, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
add("A07", "①", "判断档书写时刻≤attach 时刻(UTC)", "agent_declaration.written_at / report.agent_judgment.attached_at",
    wu.strftime("%Y-%m-%dT%H:%M:%SZ"), au.strftime("%Y-%m-%dT%H:%M:%SZ"), wu <= au, "书写在前、attach 在后")
add("A08", "①", "代码印章=规程印章", "run.git_head", run["git_head"], STAMP,
    run["git_head"] == STAMP and STAMP in MAP_TEXT, "读者报告第 4 行「代码」")
add("A09", "①", "冻结发布日历版本", "release_calendar.version", calj["version"], "1.5.0",
    calj["version"] == "1.5.0" and "v1.5.0" in JT, "判断档「发布日历实录(v1.5.0,…)」")
add("A10", "①", "冻结发布日历更新日", "release_calendar.updated", calj["updated"], "2026-11-21",
    calj["updated"] == "2026-11-21" and "2026-11-21 更新" in JT, "")
add("A11", "①", "发布日历更新日/建立日≤截止日", "release_calendar.updated / created",
    "%s / %s" % (calj["updated"], calj["created"]), "≤ %s" % CUT,
    D(calj["updated"]) <= CUTD and D(calj["created"]) <= CUTD, "")
DATE_KEYS = ("decision_date", "effective_on", "first_publish_on_or_after", "not_published_as_of", "obs_from",
             "published_on", "final_publish_on", "time")
late = 0
for e in CAL_ENT:
    for k, v in e.items():
        if isinstance(v, str) and re.match(r"^\d{4}-\d{2}-\d{2}$", v) and k != "obs_to" and D(v) > CUTD:
            late += 1
add("A12", "①", "发布日历中晚于截止日的决议/生效/发布日期个数(obs_to 远期除外)", "release_calendar.entries[*]", late, 0,
    late == 0, "晚于截止日的条目不得作可引用证据")
JTB = json.dumps({k: v for k, v in aj.items() if k != "agent_declaration"}, ensure_ascii=False)  # 不含声明块时间戳
jd = sorted(set(re.findall(r"\d{4}-\d{2}-\d{2}", JTB)))
jdl = [x for x in jd if D(x) > CUTD]
add("A13", "①", "判断档(l3/l4/reader_map/quality_gate_notes)中晚于截止日的日期字面", "agent_judgment.json 正文正则",
    ",".join(jdl), "2027-02-15", jdl == ["2027-02-15"], "仅情景期限 2027-02-15(未来时限,非证据);声明块 written_at=2026-11-24 为书写时刻")
if ZoneInfo is not None:
    t0 = datetime.fromisoformat(ra)
    for i, (tzn, label, exp) in enumerate((("America/New_York", "纽约", "09:53"), ("Europe/Berlin", "柏林", "15:53"),
                                           ("Asia/Tokyo", "东京", "23:53"), ("Asia/Shanghai", "上海", "22:53"))):
        got = t0.astimezone(ZoneInfo(tzn)).strftime("%H:%M")
        add("A%02d" % (14 + i), "①", "快照采集时刻换算(%s)" % label,
            "snapshot.research_as_of 经 IANA %s" % tzn, got, exp, got == exp and ("%s %s" % (label, exp)) in JT,
            "判断档 QGN[4] 时点说明")
CITED_DAILY = ["SPX", "VIX", "DAX", "CAC40", "NIKKEI225", "EURUSD", "USDJPY", "DXY", "UST_10Y", "TIPS_10Y", "BEI_10Y"]
after = [m for m in CITED_DAILY if series(m)[-1][0] > CUTD]
add("A18", "①", "被引日频序列的最新观测日均≤截止日", "series_store[*] last date", len(after), 0, not after,
    "越界序列: %s" % (after or "无"))

# =====================================================================
# ② 点值锚格
# =====================================================================
add("B00", "②", "六个月前锚=截止日−6月", "research_plan.point_anchors[0].as_of", RP["point_anchors"][0]["as_of"],
    A6M, RP["point_anchors"][0]["as_of"] == A6M and "2026-05-23..2026-11-23" in JT, "判断档 C2「最近六个月(2026-05-23..2026-11-23)」")
ECHO = {}
for _rg in REGI:
    for _a in REGI[_rg]["anchor_echo"]:
        ECHO[(_rg, _a["metric_id"], _a["anchor"])] = _a
PLAN = [("EA", "EA_HICP_YOY"), ("EA", "ECB_MRO"), ("EA", "ECB_DFR"),
        ("JP", "JP_CPI_YOY"), ("JP", "JP_CPI_TOKYO_YOY"), ("JP", "JP_POLICY_RATE")]
n = 0
for rg, m in PLAN:
    cell = CELLS[(rg, m)]
    for lab, asof in (("6个月前", A6MD), ("最新一期", CUTD)):
        n += 1
        pid = "B%02d" % n
        obs, v = latest_published(m, asof)
        eng = cell["anchors"][lab]
        echo = ECHO.get((rg, m, lab))
        ym = obs.isoformat()[:7]
        add(pid + "a", "②", "%s %s: 观测月" % (m, lab),
            "series_store.%s 按席位发布规则取≤%s 最新已发布观测" % (m, asof.isoformat()), ym, echo["observation_month"],
            ym == echo["observation_month"] == eng["observation_date"][:7], "engine=%s" % eng["observation_date"][:7])
        num(pid + "b", "②", "%s %s: 值" % (m, lab), "series_store.%s[%s]" % (m, obs.isoformat()), v,
            echo["value"], 1e-9, note="engine=%s" % eng["value"])
        pd_ = pub_date(m, obs).isoformat() if m in PUB_OFFSET else obs.isoformat()
        rule = ("月末%+d天" % PUB_OFFSET[m]) if m in PUB_OFFSET else "变更点序列:发布日=观测日"
        add(pid + "c", "②", "%s %s: 发布日" % (m, lab), "席位规则(%s)" % rule, pd_, eng["publication_date"],
            pd_ == eng["publication_date"] and D(pd_) <= asof, "发布日≤锚日")
RULE_TOK = {"EA_HICP_YOY": "+16天", "JP_CPI_YOY": "+20天", "JP_CPI_TOKYO_YOY": "月末−1天", "JP_POLICY_RATE": "+5天"}
k = 0
for m, tokn in RULE_TOK.items():
    k += 1
    cell = [c for (_rg, mm), c in CELLS.items() if mm == m][0]
    rule = cell["anchors"]["最新一期"]["publication_rule"]
    add("B%02d" % (36 + k), "②", "%s: 引擎推定规则文本与席位规则偏移一致" % m,
        "research_plan.point_values.cells[%s].anchors.最新一期.publication_rule" % m,
        "月末%+d天" % PUB_OFFSET[m], tokn, tokn in rule, "推定规则(非官方实录),仅核算术一致")
add("B41", "②", "EA_HICP_YOY 最新一期发布日(判断档文字)", "席位规则 2026-10 月末+16天",
    pub_date("EA_HICP_YOY", D("2026-10-01")).isoformat(), "发布 2026-11-16",
    pub_date("EA_HICP_YOY", D("2026-10-01")).isoformat() == "2026-11-16" and "发布 2026-11-16" in JT, "")
add("B42", "②", "JP_CPI_YOY 最新一期发布日(判断档文字)", "席位规则 2026-10 月末+20天",
    pub_date("JP_CPI_YOY", D("2026-10-01")).isoformat(), "发布 2026-11-20",
    pub_date("JP_CPI_YOY", D("2026-10-01")).isoformat() == "2026-11-20" and "发布 2026-11-20" in JT, "")
add("B43", "②", "JP_CPI_TOKYO_YOY 最新一期发布日(判断档文字)", "席位规则 2026-10 月末−1天",
    pub_date("JP_CPI_TOKYO_YOY", D("2026-10-01")).isoformat(), "发布 2026-10-30",
    pub_date("JP_CPI_TOKYO_YOY", D("2026-10-01")).isoformat() == "2026-10-30" and "发布 2026-10-30" in JT, "")

# =====================================================================
# ③ 同比(基期=去年同月)
# =====================================================================
jp = {d.isoformat(): v for d, v in series("JP_CPI_YOY")}
ea = {d.isoformat(): v for d, v in series("EA_HICP_YOY")}
tk = {d.isoformat(): v for d, v in series("JP_CPI_TOKYO_YOY")}
pr = {d.isoformat(): v for d, v in series("JP_POLICY_RATE")}
num("C01", "③", "JP_CPI_YOY 最新读数", "series_store.JP_CPI_YOY[2026-10-01]", jp["2026-10-01"], 2.44, 1e-9, tok="2.44%")
num("C02", "③", "JP_CPI_YOY 去年同月基期读数", "series_store.JP_CPI_YOY[2025-10-01]", jp["2025-10-01"], 2.99, 1e-9, tok="2.99")
num("C03", "③", "JP 最新读数−去年同月(百分点)", "C01−C02", jp["2026-10-01"] - jp["2025-10-01"], -0.55, 1e-9, tok="低 0.55 个百分点")
num("C04", "③", "EA_HICP_YOY 最新读数", "series_store.EA_HICP_YOY[2026-10-01]", ea["2026-10-01"], 4.0, 1e-9, tok="百分之四点零")
num("C05", "③", "EA_HICP_YOY 去年同月基期读数", "series_store.EA_HICP_YOY[2025-10-01]", ea["2025-10-01"], 2.1, 1e-9, tok="2025-10 为 2.1")
num("C06", "③", "EA 最新读数−去年同月(百分点)", "C04−C05", ea["2026-10-01"] - ea["2025-10-01"], 1.9, 1e-9, tok="高 1.9 个百分点")
add("C07", "③", "基期月份=最新观测月−12月", "series_store 两序列观测月", "2025-10", "去年同月(2025-10)",
    "去年同月(2025-10)" in JT, "")
add("C08", "③", "东京 CPI 序列首观测月", "series_store.JP_CPI_TOKYO_YOY first date", min(tk)[:7], "2026-01",
    min(tk)[:7] == "2026-01" and "序列自 2026-01 起" in JT, "")
add("C09", "③", "东京 CPI 去年同月基期观测", "series_store.JP_CPI_TOKYO_YOY[2025-10-01]", tk.get("2025-10-01"),
    "缺席", tk.get("2025-10-01") is None and "去年同月基期观测不可得" in JT, "缺基期如实标「不可得」")
add("C10", "③", "东京 CPI 序列观测数", "len(series_store.JP_CPI_TOKYO_YOY)", len(tk), 10, len(tk) == 10, "")
num("C11", "③", "东京 CPI 最新读数", "series_store.JP_CPI_TOKYO_YOY[2026-10-01]", tk["2026-10-01"], 2.73, 1e-9, tok="2.73%")
num("C12", "③", "东京 CPI 六个月前锚读数", "series_store.JP_CPI_TOKYO_YOY[2026-04-01]", tk["2026-04-01"], 1.42, 1e-9, tok="1.42%")
PATH_JP = {"2026-03": 1.46, "2026-04": 1.38, "2026-05": 1.53, "2026-06": 1.67, "2026-07": 1.97,
           "2026-08": 1.98, "2026-09": 2.16}
i = 0
for ym, rv in PATH_JP.items():
    i += 1
    num("C%02d" % (12 + i), "③", "JP_CPI_YOY 谷底后逐月路径 %s" % ym, "series_store.JP_CPI_YOY[%s-01]" % ym,
        jp["%s-01" % ym], rv, 1e-9, note="turnings[0].narrative")
PATH_EA = {"2026-01": 1.7, "2026-02": 1.9, "2026-04": 3.0, "2026-05": 3.2, "2026-06": 2.8, "2026-07": 2.9,
           "2026-08": 3.2, "2026-09": 3.8}
for ym, rv in PATH_EA.items():
    i += 1
    num("C%02d" % (12 + i), "③", "EA_HICP_YOY 逐月路径 %s" % ym, "series_store.EA_HICP_YOY[%s-01]" % ym,
        ea["%s-01" % ym], rv, 1e-9, note="turnings[1].narrative / 传导对质可见读数")
for ym, rv, src_m in (("2025-01", 4.03, "JP_CPI_YOY"), ("2025-07", 3.1, "JP_CPI_YOY"), ("2026-02", 1.27, "JP_CPI_YOY"),
                      ("2025-11", 2.9, "JP_CPI_YOY"), ("2026-05", 1.53, "JP_CPI_YOY"), ("2025-11", 2.1, "EA_HICP_YOY")):
    i += 1
    d_ = jp if src_m == "JP_CPI_YOY" else ea
    num("C%02d" % (12 + i), "③", "%s 路径点 %s" % (src_m, ym), "series_store.%s[%s-01]" % (src_m, ym), d_["%s-01" % ym], rv, 1e-9)

# =====================================================================
# ④ 政策面
# =====================================================================
mro = series("ECB_MRO")
dfr = series("ECB_DFR")
num("D01", "④", "ECB_MRO 现行有效水平", "series_store.ECB_MRO[last]", mro[-1][1], 2.65, 1e-9, tok="2.65%")
add("D02", "④", "ECB_MRO 最后观测日=生效日", "series_store.ECB_MRO last date", mro[-1][0].isoformat(), "2026-09-16",
    mro[-1][0].isoformat() == "2026-09-16", "")
num("D03", "④", "ECB_DFR 现行有效水平", "series_store.ECB_DFR[last]", dfr[-1][1], 2.5, 1e-9, tok="2.5%")
add("D04", "④", "ECB_DFR 最后观测日=生效日", "series_store.ECB_DFR last date", dfr[-1][0].isoformat(), "2026-09-16",
    dfr[-1][0].isoformat() == "2026-09-16", "")
num("D05", "④", "ECB 序列距截止天数", "截止日 − ECB_MRO 末观测日", (CUTD - mro[-1][0]).days, 68, 0, tok="距截止 68 天")


def changes(ser, tol=1e-9):
    return [(ser[i][0], ser[i - 1][1], ser[i][1]) for i in range(1, len(ser)) if abs(ser[i][1] - ser[i - 1][1]) > tol]


mc = changes(mro)
dc = changes(dfr)
(m1d, m1f, m1t), (m2d, m2f, m2t) = mc[-2], mc[-1]
(e1d, e1f, e1t), (e2d, e2f, e2t) = dc[-2], dc[-1]
add("D06", "④", "ECB_MRO 变更点1 生效日/前值→后值", "series_store.ECB_MRO 相邻变更",
    "%s %.2f→%.2f" % (m1d.isoformat(), m1f, m1t), "2026-06-17 2.15→2.4",
    m1d.isoformat() == "2026-06-17" and abs(m1f - 2.15) < 1e-9 and abs(m1t - 2.4) < 1e-9, "")
num("D07", "④", "ECB_MRO 变更点1 幅度(bp)", "(后值−前值)×100", (m1t - m1f) * 100, 25, 1e-6, tok="各 +25bp")
add("D08", "④", "ECB_MRO 变更点2 生效日/前值→后值", "series_store.ECB_MRO 相邻变更",
    "%s %.2f→%.2f" % (m2d.isoformat(), m2f, m2t), "2026-09-16 2.4→2.65",
    m2d.isoformat() == "2026-09-16" and abs(m2f - 2.4) < 1e-9 and abs(m2t - 2.65) < 1e-9, "")
num("D09", "④", "ECB_MRO 变更点2 幅度(bp)", "(后值−前值)×100", (m2t - m2f) * 100, 25, 1e-6, tok="各 25bp")
add("D10", "④", "ECB_DFR 变更点1 生效日/前值→后值", "series_store.ECB_DFR 相邻变更",
    "%s %.2f→%.2f" % (e1d.isoformat(), e1f, e1t), "2026-06-17 2.0→2.25",
    e1d.isoformat() == "2026-06-17" and abs(e1f - 2.0) < 1e-9 and abs(e1t - 2.25) < 1e-9, "")
add("D11", "④", "ECB_DFR 变更点2 生效日/前值→后值", "series_store.ECB_DFR 相邻变更",
    "%s %.2f→%.2f" % (e2d.isoformat(), e2f, e2t), "2026-09-16 2.25→2.5",
    e2d.isoformat() == "2026-09-16" and abs(e2f - 2.25) < 1e-9 and abs(e2t - 2.5) < 1e-9, "")


def prev_thursday(d):
    d = d - timedelta(days=1)
    while d.weekday() != 3:
        d -= timedelta(days=1)
    return d


add("D12", "④", "ECB 变更点1 的『生效日前上一个周四』", "日历算术", prev_thursday(m1d).isoformat(), "2026-06-11",
    prev_thursday(m1d).isoformat() == "2026-06-11" and "2026-06-11" in JT, "决议日=引擎惯例回推【推断】")
add("D13", "④", "ECB 变更点2 的『生效日前上一个周四』", "日历算术", prev_thursday(m2d).isoformat(), "2026-09-10",
    prev_thursday(m2d).isoformat() == "2026-09-10" and "2026-09-10" in JT, "")
WD = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
add("D14", "④", "两变更生效日星期", "日历算术", "%s/%s" % (WD[m1d.weekday()], WD[m2d.weekday()]), "周三/周三",
    m1d.weekday() == 2 and m2d.weekday() == 2, "引擎惯例「决议后首个周三生效」")
inwin_m = [x for x in mc if A6MD <= x[0] <= CUTD]
inwin_d = [x for x in dc if A6MD <= x[0] <= CUTD]
add("D15", "④", "六个月窗内 ECB_MRO 变更次数", "series_store.ECB_MRO 变更点∈[2026-05-23,2026-11-23]", len(inwin_m), 2,
    len(inwin_m) == 2 and "最近六个月两次同幅上调" in JT, "")
add("D16", "④", "六个月窗内 ECB_DFR 变更次数", "series_store.ECB_DFR 变更点∈[2026-05-23,2026-11-23]", len(inwin_d), 2,
    len(inwin_d) == 2, "")
num("D17", "④", "两次变更间隔天数", "2026-09-16 − 2026-06-17", (m2d - m1d).days, 91, 0, tok="相隔 91 天")
num("D18", "④", "两序列维持 2.15/2.0 的天数", "2026-06-17 − 2025-06-11", (m1d - D("2025-06-11")).days, 371, 0, tok="共 371 天")
mid_obs = [x for x in mro if D("2025-06-11") < x[0] < m1d]
add("D19", "④", "2025-06-11..2026-06-17 之间 MRO 无其他变更", "series_store.ECB_MRO 区间观测数", len(mid_obs), 0,
    not mid_obs and abs(val("ECB_MRO", "2025-06-11") - 2.15) < 1e-9, "")
BOJ_DEC = [e for e in CAL_ENT if e.get("kind") == "policy_decision" and e.get("metric_id") == "JP_POLICY_TARGET"]
BOJ_MNT = [e for e in CAL_ENT if e.get("kind") == "policy_maintenance" and e.get("metric_id") == "JP_POLICY_TARGET"]
bd = BOJ_DEC[-1] if BOJ_DEC else {}
bm = BOJ_MNT[-1] if BOJ_MNT else {}
add("D20", "④", "BOJ 目标决议日(日历实录)", "release_calendar.entries[RC-JP-BOJ-TARGET-2026-09].decision_date",
    bd.get("decision_date"), "2026-09-18", bd.get("decision_date") == "2026-09-18" and "2026-09-18 决议" in JT, "")
add("D21", "④", "BOJ 目标生效日(日历实录)", "…effective_on", bd.get("effective_on"), "2026-09-24",
    bd.get("effective_on") == "2026-09-24" and "2026-09-24 生效" in JT, "")
num("D22", "④", "BOJ 官方目标水平(日历实录)", "…target_value", bd.get("target_value"), 1.25, 1e-9, tok="政策目标 1.25%")
add("D23", "④", "BOJ 目标截至截止日已生效(现行有效)", "effective_on ≤ 2026-11-23", D(bd.get("effective_on", "2099-12-31")) <= CUTD,
    True, D(bd.get("effective_on", "2099-12-31")) <= CUTD, "待生效与现行分记:本例无待生效")
add("D24", "④", "BOJ 最近确认维持日(日历实录)", "release_calendar.entries[RC-JP-BOJ-MAINT-2026-10].decision_date",
    bm.get("decision_date"), "2026-10-30", bm.get("decision_date") == "2026-10-30" and "2026-10-30 会议确认维持" in JT, "")
num("D25", "④", "BOJ 维持后的目标水平", "…target_value", bm.get("target_value"), 1.25, 1e-9)
add("D26", "④", "距上次调整(按生效日)天数", "2026-11-23 − 2026-09-24", (CUTD - D(bd["effective_on"])).days, 60,
    (CUTD - D(bd["effective_on"])).days == 60 and "| 60天 |" in MAP_TEXT, "MAP_REPORT 官方记录表")
add("D27", "④", "距决议天数", "2026-11-23 − 2026-09-18", (CUTD - D(bd["decision_date"])).days, 66,
    (CUTD - D(bd["decision_date"])).days == 66 and "| 66天 |" in MAP_TEXT, "")
add("D28", "④", "距维持天数=核验覆盖缺口", "2026-11-23 − 2026-10-30", (CUTD - D(bm["decision_date"])).days, 24,
    (CUTD - D(bm["decision_date"])).days == 24 and "| 24天 |" in MAP_TEXT, "")
ecb_ent = [e for e in CAL_ENT if e.get("metric_id") in ("ECB_MRO", "ECB_DFR")
           or "ECB_MRO" in (e.get("metric_ids") or []) or "ECB_DFR" in (e.get("metric_ids") or [])]
add("D29", "④", "发布日历对欧央行的实录条目数", "release_calendar.entries[*].metric_id∈{ECB_MRO,ECB_DFR}", len(ecb_ent), 0,
    not ecb_ent and "冻结发布日历对欧央行无实录条目" in JT, "")
pend = [e for e in CAL_ENT if e.get("decision_date") and D(e["decision_date"]) <= CUTD and e.get("effective_on")
        and D(e["effective_on"]) > CUTD]
add("D30", "④", "已决议未生效(决议≤截止<生效)的日历条目数", "release_calendar.entries[*]", len(pend), 0,
    not pend and "无任何已决议而尚未生效的调整" in JT, "仅覆盖引擎记录面(欧央行 68 天/BOJ 24 天缺口另判)")
add("D31", "④", "注册表无 JP_POLICY_TARGET", "metric_registry.metrics[*].metric_id", "JP_POLICY_TARGET" in REG, False,
    "JP_POLICY_TARGET" not in REG and "注册表无 JP_POLICY_TARGET" in JT, "")
add("D32", "④", "ECB_MRO 注册表新鲜度阈(天)", "metric_registry.metrics[ECB_MRO].freshness.max_calendar_lag_days",
    REG["ECB_MRO"]["freshness"]["max_calendar_lag_days"], 10,
    REG["ECB_MRO"]["freshness"]["max_calendar_lag_days"] == 10 and "新鲜度阈十天" in JT, "")
add("D33", "④", "ECB_DFR L1 事实行质量", "facts[ECB_DFR@2026-09-16].quality_status", FACT["ECB_DFR@2026-09-16"]["quality_status"],
    "DEGRADED", FACT["ECB_DFR@2026-09-16"]["quality_status"] == "DEGRADED" and "quality_status=DEGRADED" in JT, "")
add("D34", "④", "ECB_MRO L1 事实行质量", "facts[ECB_MRO@2026-09-16].quality_status", FACT["ECB_MRO@2026-09-16"]["quality_status"],
    "DEGRADED", FACT["ECB_MRO@2026-09-16"]["quality_status"] == "DEGRADED", "")
_iss = json.dumps(FACT["ECB_DFR@2026-09-16"].get("issues"), ensure_ascii=False)
add("D35", "④", "ECB_DFR 过期注记文字", "facts[ECB_DFR@2026-09-16].issues", "滞后68天(>10天" if ("滞后68天" in _iss and ">10天" in _iss) else _iss,
    "滞后68天(>10天", ("滞后68天" in _iss and ">10天" in _iss), "")
num("D36", "④", "JP_POLICY_RATE 近12个月起点(2025-11 月均)", "series_store.JP_POLICY_RATE[2025-11-01]", pr["2025-11-01"], 0.478, 1e-9, tok="2025-11 的 0.478")
num("D37", "④", "JP_POLICY_RATE 最新月均(2026-10)", "series_store.JP_POLICY_RATE[2026-10-01]", pr["2026-10-01"], 1.227, 1e-9, tok="1.227%")
num("D38", "④", "近12个月月均净变动(bp)", "(1.227−0.478)×100", (pr["2026-10-01"] - pr["2025-11-01"]) * 100, 75, 0.5,
    tok="约 +75bp", note="直算 74.9bp,报告取整「约 +75bp」")
_w = [x for x in series("JP_POLICY_RATE") if D("2025-11-23") <= x[0] <= CUTD]
num("D39", "④", "引擎政策窗(2025-11-23..2026-11-23)首尾观测净变动(bp)", "窗内首观测 %.3f → 末观测 %.3f" % (_w[0][1], _w[-1][1]),
    (_w[-1][1] - _w[0][1]) * 100, 67, 0.5, tok="净 +67bp", note="判断档并列披露两种口径")
for pid, ym, rv, tokn in (("D40", "2026-09", 1.043, "1.043→1.227"), ("D41", "2026-04", 0.727, "0.727"), ("D42", "2026-06", 0.841, "0.841"),
                          ("D43", "2026-07", 0.978, "0.978"), ("D44", "2026-08", 0.977, "0.977"), ("D45", "2026-01", 0.728, "2026-01 0.728")):
    num(pid, "④", "JP_POLICY_RATE 月均台阶 %s" % ym, "series_store.JP_POLICY_RATE[%s-01]" % ym, pr["%s-01" % ym], rv, 1e-9, tok=tokn)
add("D46", "④", "口径分列: 月均≠宣布值", "research_plan…cells[JP_POLICY_RATE].face_note / 判断档",
    "月均≠政策目标宣布值" if "月均≠政策目标宣布值" in CELLS[("JP", "JP_POLICY_RATE")]["face_note"] else CELLS[("JP", "JP_POLICY_RATE")]["face_note"],
    "月均≠宣布值", "月均≠政策目标宣布值" in CELLS[("JP", "JP_POLICY_RATE")]["face_note"] and "月均≠宣布值" in JT, "")
add("D47", "④", "口径分列: ECB_MRO=政策目标(宣布值)", "…cells[ECB_MRO].policy_face.face", CELLS[("EA", "ECB_MRO")]["policy_face"]["face"],
    "政策目标口径", CELLS[("EA", "ECB_MRO")]["policy_face"]["face"] == "政策目标(宣布值)" and "政策目标口径" in JT, "")
add("D48", "④", "序列值未写成官方宣布目标(BOJ 月均 1.227 与日历目标 1.25 分列)", "判断档 C2/reader_map.regions[JP]",
    "1.227%=月均; 1.25%=日历实录目标", "同左", ("月均口径非宣布值" in JT and "月均≠宣布值" in JT), "")

# =====================================================================
# ⑤ 三利率分解与资产月窗
# =====================================================================
urt = RP["us_rates_trio"]
wf, wt = D(RM["rates_decomposition"]["window_from"]), D(RM["rates_decomposition"]["window_to"])
add("E01", "⑤", "三利率窗口端点日期", "reader_map.rates_decomposition.window_from/to", "%s..%s" % (wf.isoformat(), wt.isoformat()),
    "%s..%s" % (urt["window"]["from"], urt["window"]["to"]), (wf.isoformat(), wt.isoformat()) == (urt["window"]["from"], urt["window"]["to"]), "")
common = set(x for x, _ in series("UST_10Y")) & set(x for x, _ in series("TIPS_10Y")) & set(x for x, _ in series("BEI_10Y"))
add("E02", "⑤", "窗口两端为三序列共同观测日", "series_store 三序列 dates 交集", "%s/%s" % (wf in common, wt in common), "True/True",
    wf in common and wt in common, "")
num("E03", "⑤", "窗口日历天数", "window_to − window_from", (wt - wf).days, urt["window"]["calendar_days_between"], 0)
lv = {m: (val(m, wf), val(m, wt)) for m in ("UST_10Y", "TIPS_10Y", "BEI_10Y")}
num("E04", "⑤", "名义 UST_10Y 变动(bp)", "series_store.UST_10Y 2026-10-20→2026-11-19", (lv["UST_10Y"][1] - lv["UST_10Y"][0]) * 100,
    RM["rates_decomposition"]["nominal_bp"], 1e-6, note="端点值 %.2f→%.2f" % lv["UST_10Y"])
num("E05", "⑤", "实际 TIPS_10Y 变动(bp)", "series_store.TIPS_10Y 2026-10-20→2026-11-19", (lv["TIPS_10Y"][1] - lv["TIPS_10Y"][0]) * 100,
    RM["rates_decomposition"]["real_bp"], 1e-6, note="端点值 %.2f→%.2f" % lv["TIPS_10Y"])
num("E06", "⑤", "盈亏平衡 BEI_10Y 变动(bp)", "series_store.BEI_10Y 2026-10-20→2026-11-19", (lv["BEI_10Y"][1] - lv["BEI_10Y"][0]) * 100,
    RM["rates_decomposition"]["bei_bp"], 1e-6, note="端点值 %.2f→%.2f" % lv["BEI_10Y"])
add("E07", "⑤", "恒等式 名义Δ=实际Δ+盈亏平衡Δ (bp)", "E04/E05/E06",
    round(RM["rates_decomposition"]["real_bp"] + RM["rates_decomposition"]["bei_bp"], 6), RM["rates_decomposition"]["nominal_bp"],
    abs(RM["rates_decomposition"]["real_bp"] + RM["rates_decomposition"]["bei_bp"] - RM["rates_decomposition"]["nominal_bp"]) < 1e-6,
    "残差 0")
add("E08", "⑤", "水平恒等式 窗末 名义=实际+盈亏平衡", "series_store 2026-11-19/2026-11-20 最新同面值",
    round(lv["TIPS_10Y"][1] + lv["BEI_10Y"][1], 6), lv["UST_10Y"][1], abs(lv["TIPS_10Y"][1] + lv["BEI_10Y"][1] - lv["UST_10Y"][1]) < 0.005,
    "UST 5.04 = TIPS 2.88 + BEI 2.16")
add("E09", "⑤", "水平恒等式 窗首", "series_store 2026-10-20", round(lv["TIPS_10Y"][0] + lv["BEI_10Y"][0], 6), lv["UST_10Y"][0],
    abs(lv["TIPS_10Y"][0] + lv["BEI_10Y"][0] - lv["UST_10Y"][0]) < 0.005, "")
for pid, m, sign in (("E10", "SPX", -5.51), ("E11", "DAX", 0.11), ("E12", "NIKKEI225", -9.98), ("E13", "VIX", 38.87)):
    e_ = [x for x in RM["asset_returns_echo"] if x["metric_id"] == m][0]
    f_, t_ = D(e_["window"]["from"]), D(e_["window"]["to"])
    a, b = val(m, f_), val(m, t_)
    eng = [r for r in RP["asset_moves"]["rows"] if r["metric_id"] == m][0]
    num(pid, "⑤", "%s 资产月窗回贴(%.2f→%.2f)" % (m, a, b), "series_store.%s[%s→%s]" % (m, f_.isoformat(), t_.isoformat()),
        pct(a, b), e_["chg_pct"], 5e-3, note="引擎资产月窗 %s(至 %s)" % (eng["chg_pct"], eng["window"]["to"]))
_v = pct(val("VIX", "2026-11-20"), val("VIX", "2026-11-23"))
num("E14", "⑤", "VIX 截止日快照较 2026-11-20 收盘变动(%)", "series_store.VIX[2026-11-20→2026-11-23]", _v, -24.7, 0.05, tok="-24.7%")
add("E15", "⑤", "12 个月窗分解恒等(引擎面)", "research_plan.us_rates_trio.chg_bp_12m",
    urt["chg_bp_12m"]["TIPS_10Y"] + urt["chg_bp_12m"]["BEI_10Y"], urt["chg_bp_12m"]["UST_10Y"],
    abs(urt["chg_bp_12m"]["TIPS_10Y"] + urt["chg_bp_12m"]["BEI_10Y"] - urt["chg_bp_12m"]["UST_10Y"]) < 1e-6
    and (val("UST_10Y", "2026-11-19") - val("UST_10Y", "2025-11-19")) * 100 - urt["chg_bp_12m"]["UST_10Y"] < 0.5, "读者报告年度分解行")
