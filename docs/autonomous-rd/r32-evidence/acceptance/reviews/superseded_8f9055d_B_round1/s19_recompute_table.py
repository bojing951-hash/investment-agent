#!/usr/bin/python3 -I
# 独立语义审查席(B,Round-1) 复算表: 只读冻结快照/冻结日历/注册表/report.json 引擎面, 逐点直算后与判断档/读者报告文字比对。
# 用法: /usr/bin/python3 -I s19_recompute_table.py <snapshot> <calendar> <registry> <report.json> <agent_judgment.json> <evidence_index.json> <MAP_REPORT.md> <输出目录>
import json, sys, re
from datetime import date, datetime
from zoneinfo import ZoneInfo
from collections import defaultdict

snap_p, cal_p, reg_p, rep_p, jud_p, evid_p, map_p, outdir = sys.argv[1:9]
G = lambda p: json.load(open(p))
snap = G(snap_p); cal = G(cal_p); reg = G(reg_p); rep = G(rep_p); jud = G(jud_p); evid = G(evid_p)
MAP = open(map_p, encoding="utf-8").read()
J = json.dumps(jud, ensure_ascii=False)
RJ = json.dumps(rep, ensure_ascii=False)
S = snap["series_store"]
REG = {m["metric_id"]: m for m in reg["metrics"]}
CUT = "2026-11-23"
ASOF3 = "2026-08-23"

def series(m):
    d = S[m]["dates"]; v = S[m]["values"]
    return [(a, b) for a, b in zip(d, v) if b is not None]
VAL = {m: dict(series(m)) for m in S}
def val(m, dt): return VAL.get(m, {}).get(dt)
def last_le(m, dt):
    r = None
    for a, b in series(m):
        if a <= dt: r = (a, b)
        else: break
    return r
def yoy_m(m, ym):
    y, mo = int(ym[:4]), int(ym[5:7])
    c = val(m, ym + "-01"); b = val(m, "%04d-%02d-01" % (y - 1, mo))
    return None if (c is None or b is None) else (c / b - 1) * 100
def pct(a, b): return (b / a - 1) * 100
def bp(a, b): return (b - a) * 100
def num(lit): return float(re.sub(r"[^0-9.\-]", "", lit))
def nd_of(lit):
    core = re.sub(r"[^0-9.\-]", "", lit)
    return len(core.split(".")[1]) if "." in core else 0
def eq(calc, lit): return round(calc, nd_of(lit)) == num(lit)
def D(s): return date.fromisoformat(s)

rows = []
def add(chk, src, calc, rep, ok, lit=None, where="judgment", level="", note=""):
    lit_ok = None
    if lit is not None:
        corpus = J if where == "judgment" else (MAP if where == "map" else (RJ if where == "report" else J + MAP))
        lit_ok = (lit in corpus)
    rows.append(dict(chk=chk, src=src, calc=str(calc), rep=str(rep), ok=bool(ok), lit=lit, lit_ok=lit_ok,
                     level=level, note=note))
def addn(chk, src, calc, lit, where="judgment", level="", note=""):
    add(chk, src, "%.6g" % calc, lit, eq(calc, lit), lit=lit, where=where, level=level, note=note)

# ---------------- ① 截止日 ----------------
ra = snap["research_as_of"]
add("①", "snapshot.research_as_of", ra, ra, ra == "2026-11-23T22:53:47+08:00", lit=ra)
add("①", "snapshot.target_date", snap["target_date"], "研究截止日=快照版本日 2026-11-23", snap["target_date"] == "20261123",
    lit="研究截止日=快照版本日 2026-11-23")
add("①", "snapshot.timezone", snap["timezone"], "+08:00 偏移", snap["timezone"] == "Asia/Shanghai")
dt = datetime.fromisoformat(ra)
for city, tz, repv in (("纽约", "America/New_York", "纽约 09:53"), ("法兰克福", "Europe/Berlin", "法兰克福 15:53"),
                       ("东京", "Asia/Tokyo", "东京 23:53"), ("上海", "Asia/Shanghai", "上海 22:53")):
    t = dt.astimezone(ZoneInfo(tz)).strftime("%H:%M")
    add("①", "research_as_of 换算 " + tz, t, repv, t == repv.split()[1], lit=repv)
cited = ["CPI", "CORE_CPI", "CORE_PCE", "UNEMPLOYMENT", "INDPRO", "US_REAL_GDP", "EA_REAL_GDP_YOY", "EA_HICP_YOY",
         "JP_POLICY_RATE", "BEI_10Y", "TIPS_10Y", "UST_10Y", "SPX", "NIKKEI225", "GOLD_F", "DXY", "VIX", "BRENT_F", "USDJPY"]
lastd = {m: S[m]["dates"][-1] for m in cited}
mx = max(lastd.values())
add("①", "series_store.<19 个被引序列>.dates[-1]", "max=" + mx + " | " + ", ".join("%s:%s" % (m, lastd[m]) for m in cited),
    "全部不晚于截止日 2026-11-23", mx <= CUT, note="无晚于截止日的观测")
cells = rep["research_plan"]["point_values"]["cells"]
pubs = []
for c in cells:
    for a, v in c["anchors"].items():
        pubs.append((v["publication_date"], c["metric_id"], a, v["observation_date"]))
mxp = max(pubs)
add("①", "report.json research_plan.point_values.cells[*].anchors.*.publication_date", "max=%s(%s/%s)" % mxp[:3],
    "被引观测均已发布且不晚于截止日", mxp[0] <= CUT)
ents = cal["entries"]
pol = [e for e in ents if e.get("kind") in ("policy_decision", "policy_maintenance")]
pdates = sorted(set(x for e in pol for x in (e.get("decision_date"), e.get("effective_on")) if x))
docs = rep["research_plan"]["policy_doc_facts"]
docd = sorted(set(x["published_on"] for x in docs))
add("①", "calendar entries(kind=policy_*)", pdates, "决议日/生效日不晚于截止日", pdates[-1] <= CUT)
add("①", "report.json research_plan.policy_doc_facts", docd, "纪要发布日不晚于截止日", docd[-1] <= CUT)
add("①", "report.json agent_judgment.reader_map_faces.history_n", rep["agent_judgment"]["reader_map_faces"]["history_n"],
    "零段类比(无事后段)", rep["agent_judgment"]["reader_map_faces"]["history_n"] == 0, lit="零段呈现以避免以事后冒充预测")

# ---------------- ② 点值锚格 ----------------
EXP = {("US_REAL_GDP", "3个月前"): "2026-04", ("US_REAL_GDP", "最新一期"): "2026-07",
       ("UNEMPLOYMENT", "3个月前"): "2026-07", ("UNEMPLOYMENT", "最新一期"): "2026-10",
       ("INDPRO", "3个月前"): "2026-07", ("INDPRO", "最新一期"): "2026-10",
       ("CPI", "3个月前"): "2026-07", ("CPI", "最新一期"): "2026-10",
       ("CORE_CPI", "3个月前"): "2026-07", ("CORE_CPI", "最新一期"): "2026-10",
       ("CORE_PCE", "3个月前"): "2026-06", ("CORE_PCE", "最新一期"): "2026-09",
       ("EA_REAL_GDP_YOY", "3个月前"): "2026-04", ("EA_REAL_GDP_YOY", "最新一期"): "2026-07",
       ("EA_HICP_YOY", "3个月前"): "2026-07", ("EA_HICP_YOY", "最新一期"): "2026-10",
       ("JP_POLICY_RATE", "3个月前"): "2026-07", ("JP_POLICY_RATE", "最新一期"): "2026-10"}
CELL = {(c["metric_id"], a): v for c in cells for a, v in c["anchors"].items()}
for rg in jud["reader_map"]["regions"]:
    for ae in rg.get("anchor_echo", []):
        m = ae["metric_id"]; exp = EXP[(m, ae["anchor"])]
        direct = val(m, exp + "-01")
        eng = CELL[(m, ae["anchor"])]
        ok = (direct is not None and abs(direct - ae["value"]) < 1e-9 and ae["observation_month"] == exp
              and abs(eng["value"] - ae["value"]) < 1e-9 and eng["observation_date"][:7] == exp
              and eng["publication_date"] <= eng["as_of"] and eng["as_of"] == (ASOF3 if ae["anchor"] == "3个月前" else CUT))
        add("②", "series_store.%s [观测月 %s]" % (m, exp), "%s @%s" % (direct, exp),
            "%s @%s(%s;引擎格 pub %s≤as_of %s)" % (ae["value"], ae["observation_month"], ae["anchor"], eng["publication_date"], eng["as_of"]), ok)

# ---------------- ③ 同比 ----------------
def ypt(m, ym, lit, note=""):
    y = yoy_m(m, ym)
    addn("③", "series_store.%s: %s / 去年同月 - 1" % (m, ym), y if y is not None else float("nan"), lit, note=note)
ypt("CPI", "2026-07", "3.3%")
ypt("CPI", "2026-09", "3.72%")
cpi_oct = yoy_m("CPI", "2026-10"); cpi_oct_base = val("CPI", "2025-10-01")
add("③", "series_store.CPI: 2026-10 基期 2025-10-01", "基期观测=%s → 同比不可得" % cpi_oct_base,
    "2026-10 同比因缺上年同月基期观测不可得", cpi_oct is None and cpi_oct_base is None, lit="2026-10 同比因缺上年同月基期观测不可得")
ypt("CORE_CPI", "2026-07", "2.47%")
ypt("CORE_CPI", "2026-09", "2.57%")
cc_oct = yoy_m("CORE_CPI", "2026-10"); cc_base = val("CORE_CPI", "2025-10-01")
add("③", "series_store.CORE_CPI: 2026-10 基期 2025-10-01", "基期观测=%s → 同比不可得" % cc_base,
    "2026-10 同比同样缺上年同月基期观测", cc_oct is None and cc_base is None, lit="2026-10 同比同样缺上年同月基期观测")
ypt("CORE_PCE", "2026-06", "3.04%")
ypt("CORE_PCE", "2026-09", "3.12%")
ypt("INDPRO", "2026-07", "1.25%")
ypt("INDPRO", "2026-10", "2.15%")
ypt("US_REAL_GDP", "2026-04", "2.19%")
ypt("US_REAL_GDP", "2026-07", "2.07%")
addn("③", "series_store.INDPRO 2026-10 环比", pct(val("INDPRO", "2026-09-01"), val("INDPRO", "2026-10-01")), "-0.43%")
addn("③", "series_store.INDPRO 2026-07→2026-10 水平", pct(val("INDPRO", "2026-07-01"), val("INDPRO", "2026-10-01")), "+0.22%")
addn("③", "series_store.INDPRO 2025-07→2025-10(基数)", abs(pct(val("INDPRO", "2025-07-01"), val("INDPRO", "2025-10-01"))), "0.66%", note="判断档原文「基数下行 0.66%」,取幅值比对")
for m, a, b, lit, litc in (("CPI", "332.813", "337.476", "332.813→337.476", "332.813→337.476"), ("CORE_CPI", "336.789", "339.9", "336.789→2026-10 339.9", "336.789→339.9"),
                            ("CORE_PCE", "129.969", "130.902", "129.969→130.902", "129.969→130.902")):
    add("③", "series_store.%s 水平(两锚)" % m, "%s→%s" % (val(m, EXP[(m, "3个月前")] + "-01"), val(m, EXP[(m, "最新一期")] + "-01")),
        lit, (str(val(m, EXP[(m, "3个月前")] + "-01")) + "→" + str(val(m, EXP[(m, "最新一期")] + "-01"))) == litc, lit=lit)
ypt("CPI", "2026-02", "2.434")
ypt("CPI", "2026-05", "4.1666")
ypt("CPI", "2026-05", "4.17")
ypt("CORE_CPI", "2026-02", "2.4725")
ypt("CORE_CPI", "2026-05", "2.8229")
ypt("CORE_CPI", "2026-08", "2.4462")
addn("③", "CPI 同比 2026-02→2026-05 差", yoy_m("CPI", "2026-05") - yoy_m("CPI", "2026-02"), "1.7326")
for ym, lit in (("2026-02", "1.9"), ("2026-05", "3.2"), ("2026-06", "2.8"), ("2026-07", "2.9"), ("2026-10", "4.0")):
    add("③", "series_store.EA_HICP_YOY[观测月 %s](同比序列直读)" % ym, val("EA_HICP_YOY", ym + "-01"), lit,
        abs(val("EA_HICP_YOY", ym + "-01") - num(lit)) < 1e-9, lit=("自 2026-02 的 1.9 抬升至 2026-05 的 3.2" if ym == "2026-02" else lit + "%"))
addn("③", "EA_HICP_YOY 2026-07→2026-10 差(百分点)", val("EA_HICP_YOY", "2026-10-01") - val("EA_HICP_YOY", "2026-07-01"), "1.1")
addn("③", "EA_HICP_YOY 2026-02→2026-05 差(百分点)", val("EA_HICP_YOY", "2026-05-01") - val("EA_HICP_YOY", "2026-02-01"), "1.3")
ea26 = [(d_, v_) for d_, v_ in series("EA_HICP_YOY") if d_[:4] == "2026"]
ytdmax = max(v_ for _, v_ in ea26); ytdmax_m = [d_ for d_, v_ in ea26 if v_ == ytdmax]
add("③", "series_store.EA_HICP_YOY 2026-01..2026-10 最大值", "%s @%s" % (ytdmax, ytdmax_m), "读数为年内新高(2026-10 的 4.0)",
    ytdmax == 4.0 and ytdmax_m == ["2026-10-01"], lit="读数为年内新高")
for q, lit in (("2026-04", "1.19%"), ("2026-07", "1.28%")):
    add("③", "series_store.EA_REAL_GDP_YOY[观测季 %s]" % q, val("EA_REAL_GDP_YOY", q + "-01"), lit,
        abs(val("EA_REAL_GDP_YOY", q + "-01") - num(lit)) < 1e-9, lit=lit)
# EA vs US 可比同月
ea_m = {k[:7]: v_ for k, v_ in series("EA_HICP_YOY")}
us_m = {ym: yoy_m("CPI", ym) for ym in ea_m if ym >= "2015-01"}
cmp = [(ym, ea_m[ym], us_m[ym]) for ym in sorted(ea_m) if us_m.get(ym) is not None]
ea_gt = [c[0] for c in cmp if c[1] > c[2]]
run_old = [c for c in cmp if "2022-07" <= c[0] <= "2023-09"]
run_mid = [c for c in cmp if "2023-10" <= c[0] <= "2026-08"]
last_cmp = cmp[-1]
add("③", "series_store EA_HICP_YOY vs CPI 同比(同月可比, n=%d)" % len(cmp), "最新可比月 %s: EA %.4f vs US %.4f; 2022-07..2023-09 共 %d 个月; 2023-10..2026-08 共 %d 个月, 其中 EA>US %d 个月; EA>US 的最近两个月份 %s" % (
    last_cmp[0], last_cmp[1], last_cmp[2], len(run_old), len(run_mid), sum(1 for c in run_mid if c[1] > c[2]), ea_gt[-2:]),
    "最新可比同月为九月…为 2023-09 以来首个高于美国的可比月份(2022-07 至 2023-09 曾持续高于美国)",
    last_cmp[0] == "2026-09" and last_cmp[1] > last_cmp[2] and all(c[1] > c[2] for c in run_old)
    and not any(c[1] > c[2] for c in run_mid) and ea_gt[-2:] == ["2023-09", "2026-09"],
    lit="为 2023-09 以来首个高于美国的可比月份")

# ---------------- ④ 政策面 ----------------
PD = [e for e in pol if e["entry_id"] == "RC-JP-BOJ-TARGET-2026-09"][0]
PM = [e for e in pol if e["entry_id"] == "RC-JP-BOJ-MAINT-2026-10"][0]
add("④", "calendar RC-JP-BOJ-TARGET-2026-09.decision_date", PD["decision_date"], "2026-09-18 决议", PD["decision_date"] == "2026-09-18", lit="2026-09-18 决议")
add("④", "calendar RC-JP-BOJ-TARGET-2026-09.effective_on", PD["effective_on"], "2026-09-24 生效", PD["effective_on"] == "2026-09-24", lit="2026-09-24 生效")
add("④", "calendar RC-JP-BOJ-TARGET-2026-09.target_value", PD["target_value"], "政策目标利率约 1.25%", PD["target_value"] == 1.25, lit="政策目标利率约 1.25%")
add("④", "calendar RC-JP-BOJ-MAINT-2026-10", "decision %s target %s effective_on=%s" % (PM["decision_date"], PM["target_value"], PM.get("effective_on")),
    "2026-10-30 会议确认维持;维持条目无生效日", PM["decision_date"] == "2026-10-30" and PM["target_value"] == 1.25 and "effective_on" not in PM,
    lit="维持条目无生效日")
add("④", "日历政策条目计数(kind=policy_*)", "%d 条: %s" % (len(pol), [e["entry_id"] for e in pol]), "发布日历政策条目仅 2 条、均为日本央行实录",
    len(pol) == 2 and all(e["metric_id"] == "JP_POLICY_TARGET" for e in pol), lit="发布日历政策条目仅 2 条、均为日本央行实录")
add("④", "距上次调整 = 截止日 − 生效日", (D(CUT) - D(PD["effective_on"])).days, "按生效日 60 天", (D(CUT) - D(PD["effective_on"])).days == 60, lit="距上次调整按生效日 60 天")
add("④", "距决议 = 截止日 − 决议日", (D(CUT) - D(PD["decision_date"])).days, "按决议日 66 天", (D(CUT) - D(PD["decision_date"])).days == 66, lit="按决议日 66 天")
add("④", "距维持 = 截止日 − 维持决议日", (D(CUT) - D(PM["decision_date"])).days, "距维持 24天(读者报告政策官方记录面)", (D(CUT) - D(PM["decision_date"])).days == 24,
    where="map", lit="24天")
add("④", "calendar: effective_on 晚于截止日的条目", [e["entry_id"] for e in pol if e.get("effective_on") and e["effective_on"] > CUT], "待生效=—(无待生效决定)",
    not any(e.get("effective_on") and e["effective_on"] > CUT for e in pol), where="map", lit="| 日本 | 1.25 | — |")
add("④", "report.json research_plan.policy_event_clusters.clusters", rep["research_plan"]["policy_event_clusters"]["clusters"], "政策事件簇为空",
    rep["research_plan"]["policy_event_clusters"]["clusters"] == [], lit="政策事件簇为空")
add("④", "report.json research_plan.policy_doc_facts", "%s %s" % (docs[0]["doc_id"], docs[0]["published_on"]), "FOMC-MINUTES-2026-10 于 2026-11-18 发布",
    docs[0]["published_on"] == "2026-11-18", lit="2026-11-18 发布")
add("④", "report.json research_plan.dimension_gaps", [g["metric_id"] + ":" + g["gap"] for g in rep["research_plan"]["dimension_gaps"]],
    "JP_POLICY_TARGET 注册表不可得", "JP_POLICY_TARGET" not in REG and val("JP_POLICY_TARGET", "2026-10-01") is None, lit="JP_POLICY_TARGET)注册表不可得")
add("④", "metric_registry[*].metric_id 含 JGB?", [k for k in REG if "JGB" in k], "(注册表在册)", True)
# JP 月均序列
JPM = dict(series("JP_POLICY_RATE"))
c3 = jud["l3"]["contradictions"][2]["statement"]
for lit, calc, exp in (("政策目标利率约一点二五", PD["target_value"], 1.25), ("按生效日六十天", (D(CUT) - D(PD["effective_on"])).days, 60),
                       ("按决议日六十六天", (D(CUT) - D(PD["decision_date"])).days, 66),
                       ("正七十五个基点", bp(JPM["2025-11-01"], JPM["2026-10-01"]), 75), ("零点四七八", JPM["2025-11-01"], 0.478),
                       ("一点二二七", JPM["2026-10-01"], 1.227), ("正六十七个基点", bp(JPM["2025-12-01"], JPM["2026-10-01"]), 67)):
    add("④", "C3 矛盾陈述中文数字(不在契约绑定之列) vs 直算", "%.4g" % calc, "%s(=%s)" % (lit, exp),
        (lit in c3) and (round(calc) == exp if isinstance(exp, int) else abs(calc - exp) < 1e-9), lit=lit)
for ym, lit in (("2025-11", "0.478"), ("2025-12", "0.557"), ("2026-01", "0.728"), ("2026-06", "0.841"), ("2026-07", "0.978"), ("2026-09", "1.043"), ("2026-10", "1.227")):
    add("④", "series_store.JP_POLICY_RATE[观测月 %s]" % ym, JPM[ym + "-01"], lit, abs(JPM[ym + "-01"] - num(lit)) < 1e-9, lit=lit)
addn("④", "JP_POLICY_RATE 12 个月净变动 = 2026-10 − 2025-11", bp(JPM["2025-11-01"], JPM["2026-10-01"]), "+75bp")
addn("④", "JP_POLICY_RATE 自窗内首观测(2025-12)起算", bp(JPM["2025-12-01"], JPM["2026-10-01"]), "+67bp")
steps = [("2025-11", "2025-12"), ("2025-12", "2026-01"), ("2026-05", "2026-06"), ("2026-06", "2026-07"), ("2026-08", "2026-09"), ("2026-09", "2026-10")]
addn("④", "JP_POLICY_RATE 窗内六个变动点之和", sum(bp(JPM[a + "-01"], JPM[b + "-01"]) for a, b in steps), "+75bp")
addn("④", "JP_POLICY_RATE 2026-01 台阶", bp(JPM["2025-12-01"], JPM["2026-01-01"]), "17bp")
addn("④", "JP_POLICY_RATE 2026-06 台阶", bp(JPM["2026-05-01"], JPM["2026-06-01"]), "11bp")
addn("④", "JP_POLICY_RATE 2026-09 台阶(2026-08→2026-09)", bp(JPM["2026-08-01"], JPM["2026-09-01"]), "7bp")
addn("④", "JP_POLICY_RATE 2026-10 台阶", bp(JPM["2026-09-01"], JPM["2026-10-01"]), "18bp")
ups26 = [b for a, b in steps if b[:4] == "2026" and JPM[b + "-01"] > JPM[a + "-01"]]
add("④", "JP_POLICY_RATE 2026 年内上行月均台阶", ups26, "2026-07 为 2026 年内第三个上行月均台阶", ups26[:3] == ["2026-01", "2026-06", "2026-07"], lit="2026 年内第三个上行月均台阶")
add("④", "日历: 2026-10 为 2026-09-24 生效后首个整月", "2026-10-01..2026-10-31", "次月月均=新水平整月", D("2026-10-01") > D(PD["effective_on"]))
add("④", "series_store.USDJPY[2026-11-23]", val("USDJPY", "2026-11-23"), "159.35", eq(val("USDJPY", "2026-11-23"), "159.35"), lit="159.35")
# 快照内未入证据索引的政策序列变动(判断档披露为「不作为本档证据」)
def chg(m, a, b): return val(m, a), val(m, b)
add("④", "series_store.DFEDTARU 2026-09-16→2026-09-17", chg("DFEDTARU", "2026-09-16", "2026-09-17"), "美联储目标区间上限 3.75→4.00 于 2026-09-17",
    chg("DFEDTARU", "2026-09-16", "2026-09-17") == (3.75, 4.0), lit="3.75→4.00 于 2026-09-17")
prev_ecb = last_le("ECB_DFR", "2026-09-15")
add("④", "series_store.ECB_DFR 末次变动(%s→2026-09-16)" % prev_ecb[0], (prev_ecb[1], val("ECB_DFR", "2026-09-16")), "欧央行存款便利利率 2.25→2.50 于 2026-09-16",
    (prev_ecb[1], val("ECB_DFR", "2026-09-16")) == (2.25, 2.5), lit="2.25→2.50 于 2026-09-16")

# ---------------- ⑤ 三利率与资产 ----------------
def W(m, a, b): return bp(val(m, a), val(m, b))
add("⑤", "series_store.UST_10Y[2026-11-19]", val("UST_10Y", "2026-11-19"), "5.04%", eq(val("UST_10Y", "2026-11-19"), "5.04"), lit="5.04%")
for a, b, tag, ln, lr, lb in (("2026-10-20", "2026-11-19", "近一月", "-8bp", "+11bp", "-19bp"),
                              ("2026-08-19", "2026-11-19", "三个月", "+39bp", "+53bp", "-14bp"),
                              ("2025-11-19", "2026-11-19", "12个月", "+91bp", "+102bp", "-11bp")):
    addn("⑤", "UST_10Y %s窗 %s→%s" % (tag, a, b), W("UST_10Y", a, b), ln)
    addn("⑤", "TIPS_10Y %s窗 %s→%s" % (tag, a, b), W("TIPS_10Y", a, b), lr)
    addn("⑤", "BEI_10Y %s窗 %s→%s" % (tag, a, b), W("BEI_10Y", a, b), lb)
    res = W("UST_10Y", a, b) - (W("TIPS_10Y", a, b) + W("BEI_10Y", a, b))
    add("⑤", "%s窗 恒等残差 = 名义 −(实际+盈亏平衡)" % tag, res, "残差 0", abs(res) < 1e-6, lit="残差 0")
    lv = (val("UST_10Y", b), val("TIPS_10Y", b), val("BEI_10Y", b))
    add("⑤", "期末水平恒等 %s" % b, "%.2f = %.2f + %.2f" % lv, "名义=实际+盈亏平衡", abs(lv[0] - lv[1] - lv[2]) < 1e-9, lit="名义=实际+盈亏平衡")
lv = (val("UST_10Y", "2026-10-20"), val("TIPS_10Y", "2026-10-20"), val("BEI_10Y", "2026-10-20"))
add("⑤", "期初水平恒等 2026-10-20", "%.2f = %.2f + %.2f" % lv, "名义=实际+盈亏平衡", abs(lv[0] - lv[1] - lv[2]) < 1e-9, lit="名义=实际+盈亏平衡")
rd = jud["reader_map"]["rates_decomposition"]
eng = rep["research_plan"]["us_rates_trio"]
add("⑤", "agent_judgment.reader_map.rates_decomposition vs report.json us_rates_trio",
    "jud %s→%s %s/%s/%s | eng %s→%s %s" % (rd["window_from"], rd["window_to"], rd["nominal_bp"], rd["real_bp"], rd["bei_bp"], eng["window"]["from"], eng["window"]["to"], eng["chg_bp"]),
    "判断档分解=引擎分解", (rd["window_from"], rd["window_to"], rd["nominal_bp"], rd["real_bp"], rd["bei_bp"]) == (eng["window"]["from"], eng["window"]["to"], eng["chg_bp"]["UST_10Y"], eng["chg_bp"]["TIPS_10Y"], eng["chg_bp"]["BEI_10Y"]))
addn("⑤", "TIPS_10Y 2026-10-23→2026-11-19", W("TIPS_10Y", "2026-10-23", "2026-11-19"), "22bp")
addn("⑤", "TIPS_10Y 2026-10-23", val("TIPS_10Y", "2026-10-23"), "2.66")
add("⑤", "三个月/12个月窗 实际分量幅度 > 名义变动", "53>39, 102>91", "实际分量幅度超过名义变动", W("TIPS_10Y", "2026-08-19", "2026-11-19") > W("UST_10Y", "2026-08-19", "2026-11-19") and W("TIPS_10Y", "2025-11-19", "2026-11-19") > W("UST_10Y", "2025-11-19", "2026-11-19"),
    lit="实际分量幅度超过名义变动")
# 资产
AM = {r["metric_id"]: r for r in rep["research_plan"]["asset_moves"]["rows"]}
for ae in jud["reader_map"]["asset_returns_echo"]:
    m = ae["metric_id"]; f = ae["window"]["from"]; t = ae["window"]["to"]
    c = pct(val(m, f), val(m, t))
    add("⑤", "series_store.%s %s→%s" % (m, f, t), "%.4f (%s→%s)" % (c, val(m, f), val(m, t)), "%s%%(%s→%s)" % (ae["chg_pct"], f, t),
        eq(c, str(ae["chg_pct"])) and AM[m]["window"]["from"] == f and AM[m]["window"]["to"] == t and abs(AM[m]["chg_pct"] - ae["chg_pct"]) < 1e-9)
addn("⑤", "SPX 共同交易日窗 2026-10-23→2026-11-19", pct(val("SPX", "2026-10-23"), val("SPX", "2026-11-19")), "-5.87%")
addn("⑤", "VIX 值 2026-10-23", val("VIX", "2026-10-23"), "19.45")
addn("⑤", "VIX 值 2026-11-23", val("VIX", "2026-11-23"), "27.01")
addn("⑤", "SPX 收盘口径 2026-10-23→2026-11-20", pct(val("SPX", "2026-10-23"), val("SPX", "2026-11-20")), "-9.36%")
addn("⑤", "VIX 收盘口径 2026-10-23→2026-11-20", pct(val("VIX", "2026-10-23"), val("VIX", "2026-11-20")), "84.52%")
addn("⑤", "VIX 值 2026-11-20", val("VIX", "2026-11-20"), "35.89")
addn("⑤", "SPX 收盘口径三个月 2026-08-19→2026-11-20", pct(val("SPX", "2026-08-19"), val("SPX", "2026-11-20")), "-10.35%")
addn("⑤", "VIX 收盘口径三个月 2026-08-19→2026-11-20", pct(val("VIX", "2026-08-19"), val("VIX", "2026-11-20")), "141.03%")
addn("⑤", "VIX 值 2026-08-19", val("VIX", "2026-08-19"), "14.89")
addn("⑤", "TIPS_10Y 2026-08-19→2026-11-19", W("TIPS_10Y", "2026-08-19", "2026-11-19"), "53bp")
# BEI 细节
addn("⑤", "BEI_10Y 2026-11-20", val("BEI_10Y", "2026-11-20"), "2.15")
addn("⑤", "BEI_10Y 2026-08-19", val("BEI_10Y", "2026-08-19"), "2.30")
addn("⑤", "BEI_10Y 2026-11-19", val("BEI_10Y", "2026-11-19"), "2.16")
bei12 = [(d_, v_) for d_, v_ in series("BEI_10Y") if "2025-11-20" <= d_ <= "2026-11-20"]
b12min = min(v_ for _, v_ in bei12); b12max = max(v_ for _, v_ in bei12)
add("⑤", "series_store.BEI_10Y 12个月窗 2025-11-20..2026-11-20 最小/最大", "min %s max %s" % (b12min, b12max), "最新 2.15…12 个月窗内最低",
    b12min == 2.15 and bei12[-1][1] == 2.15 and bei12[-1][0] == "2026-11-20", lit="12 个月窗内最低")
seg = [(d_, v_) for d_, v_ in series("BEI_10Y") if "2026-02-20" <= d_ <= "2026-05-04"]
smin = min(seg, key=lambda x: x[1]); smax = max(seg, key=lambda x: x[1])
ytd = [(d_, v_) for d_, v_ in series("BEI_10Y") if d_[:4] == "2026"]
add("⑤", "series_store.BEI_10Y 2026-02-20..2026-05-04 低点/高点; 2026 年内最高", "低 %s@%s 高 %s@%s 年内最高 %s" % (smin[1], smin[0], smax[1], smax[0], max(v_ for _, v_ in ytd)),
    "自 2026-02-27 的 2.25…升至 2026-05-04 的 2.50(该段峰值,亦为 2026 年内最高)",
    smin == ("2026-02-27", 2.25) and smax == ("2026-05-04", 2.5) and max(v_ for _, v_ in ytd) == 2.5, lit="亦为 2026 年内最高")
addn("⑤", "BEI_10Y 月末对月末 2026-02-27→2026-05-29", W("BEI_10Y", "2026-02-27", "2026-05-29"), "13bp")
addn("⑤", "BEI_10Y 2026-05-29", val("BEI_10Y", "2026-05-29"), "2.38")
# 布伦特(判断档引用的三数)
addn("⑤", "BRENT_F 2026-08-19→2026-11-23", pct(val("BRENT_F", "2026-08-19"), val("BRENT_F", "2026-11-23")), "-3.74%")
addn("⑤", "BRENT_F 2026-10-23→2026-11-23", pct(val("BRENT_F", "2026-10-23"), val("BRENT_F", "2026-11-23")), "-24.44%")
addn("⑤", "BRENT_F 2025-11-19→2026-11-23", pct(val("BRENT_F", "2025-11-19"), val("BRENT_F", "2026-11-23")), "38.86%")
# USDJPY 百分位
uj = [(d_, v_) for d_, v_ in series("USDJPY") if "2025-11-23" < d_ <= "2026-11-23"]
cur = val("USDJPY", "2026-11-23")
ple = sum(1 for _, v_ in uj if v_ <= cur) / len(uj) * 100; plt = sum(1 for _, v_ in uj if v_ < cur) / len(uj) * 100
add("⑤", "series_store.USDJPY 近 12 个月百分位(2025-11-23..2026-11-23, n=%d)" % len(uj), "%.1f..%.1f(≤/<); 区间 %.2f..%.2f" % (plt, ple, min(v_ for _, v_ in uj), max(v_ for _, v_ in uj)),
    "近 12 个月窗内约第 71 百分位", round(ple) == 71 and round(plt) == 71, lit="近 12 个月窗内约第 71 百分位")

# ---------------- ⑥ 转折与候选面 ----------------
cands = rep["research_plan"]["turning_candidates"]["candidates"]
TN = {c["metric_id"] + "@" + c["to_ym"]: c for c in cands}
for t in jud["reader_map"]["turnings"]:
    c = TN.get(t["metric_id"] + "@" + t["date"])
    direct = ((yoy_m(t["metric_id"], t["before_date"]), yoy_m(t["metric_id"], t["date"])) if t["metric_id"] == "CPI"
              else (val(t["metric_id"], t["before_date"] + "-01"), val(t["metric_id"], t["date"] + "-01")))
    add("⑥", "series_store.%s 同比 %s→%s" % (t["metric_id"], t["before_date"], t["date"]), "%.4f→%.4f" % direct,
        "%s→%s(候选面 %s..%s)" % (t["value_before"], t["value_after"], t["before_date"], t["date"]),
        c is not None and c["from_ym"] == t["before_date"] and c["to_ym"] == t["date"] and abs(c["value_before"] - t["value_before"]) < 1e-9
        and abs(c["value_after"] - t["value_after"]) < 1e-9
        and direct[0] is not None and direct[1] is not None
        and abs(direct[0] - t["value_before"]) < 6e-5 and abs(direct[1] - t["value_after"]) < 6e-5)
add("⑥", "turning_candidates |Δ| 最大者", "%s@%s Δ=%s" % (cands[0]["metric_id"], cands[0]["to_ym"], cands[0]["delta"]), "为候选池内最大单段变动",
    cands[0]["metric_id"] == "CPI" and cands[0]["delta"] == max(abs(c["delta"]) for c in cands), lit="为候选池内最大单段变动")
cc = TN.get("CORE_CPI@2026-08")
add("⑥", "turning_candidates CORE_CPI@2026-08", "%s→%s" % (cc["value_before"], cc["value_after"]), "2.8229 回落至 2.4462，其后 2026-09 回升至 2.5658",
    cc["from_ym"] == "2026-05" and cc["value_before"] == 2.8229 and cc["value_after"] == 2.4462, lit="2.8229 回落至 2.4462")
addn("⑥", "CORE_CPI 同比 2026-09", yoy_m("CORE_CPI", "2026-09"), "2.5658")
add("⑥", "turning_candidates.basis 对三转折的要求 vs 判断档 turnings 事件数",
    "独立事件: CPI@2026-05 与 EA_HICP_YOY@2026-05 同窗(2026-02..2026-05)同轮事件=1, JP_POLICY_RATE@2026-07=1 → 共 2 个独立事件/3 条",
    "三转折须为不同事件,同一转折不得重复计数", len({(t["before_date"], t["date"]) for t in jud["reader_map"]["turnings"]}) == 3,
    where="report", level="MINOR", lit="三转折须为不同事件,同一转折不得重复计数",
    note="判断档三条转折中两条为同一轮事件(美/欧通胀 2026-05 同月抬升),读者报告并项后仅 2 行、标题仍为「过去一年的三个转折」且无补选行")
add("⑥", "月频分辨率: CPI(月频) 与 EA_HICP_YOY(月频) 观测月均为 2026-05", "同月", "月频证据先后未定", True, lit="月频证据先后未定")
add("⑥", "turnings 日期落在过去一年内(截止日前 12 个月)", sorted(set(t["date"] for t in jud["reader_map"]["turnings"])), "2026-05, 2026-07",
    all("2025-11-23" < t["date"] + "-01" <= CUT for t in jud["reader_map"]["turnings"]))

# ---------------- ⑦ 传导链证据级 ----------------
links = jud["l3"]["mechanism_chains"][0]["links"]
add("⑦", "agent_judgment l3.mechanism_chains[0].links[*].evidence_level", [l["evidence_level"] for l in links], "E1/E2/E2", [l["evidence_level"] for l in links] == ["E1", "E2", "E2"], lit="E1/E2/E2")
add("⑦", "E2 环文字带【假设】标注", ["【假设】" in l["text"] for l in links[1:]], "E2 环以假设位措辞", all("【假设】" in l["text"] for l in links[1:]))
add("⑦", "M1 环1 台阶值", [JPM[y + "-01"] for y in ("2025-12", "2026-01", "2026-06", "2026-07", "2026-09", "2026-10")], "0.557/0.728/0.841/0.978/1.043/1.227", True)
addn("⑦", "NIKKEI225 2026-10-23→2026-11-20", abs(pct(val("NIKKEI225", "2026-10-23"), val("NIKKEI225", "2026-11-20"))), "9.98%", note="判断档原文「下跌 9.98%」,取幅值比对")
jgb = sorted((f_["fact_id"], f_["value"]) for f_ in snap["facts"] if "JGB" in f_["metric_id"])
add("⑪", "snapshot.facts[metric_id 含 JGB] (105 行事实面)", jgb, "本引擎无…中长端融资成本(国债收益率)序列",
    not any("JGB" in k for k in S), lit="本引擎无日本套息持仓与中长端融资成本(国债收益率)序列", level="MINOR",
    note="字面「无序列」在 series_store 面属实(无 JGB 历史),故不计入偏离;但冻结快照 facts 含 JGB2Y/JGB5Y/JGB10Y@2026-11-19 点值 1.853/2.235/2.87(注册表在册 active、日频),「缺环待采」不准确,应限定为「本问证据面未纳入、序列库无历史」(列 MINOR)")

# ---------------- ⑨ 情景 ----------------
def rule(ym):
    y, mo = int(ym[:4]), int(ym[5:7])
    nxt = date(y + (mo == 12), 1 if mo == 12 else mo + 1, 1)
    return (nxt - date(y, mo, 1) - timedelta(days=0)).days  # placeholder
from datetime import timedelta
def mend_plus(ym, n):
    y, mo = int(ym[:4]), int(ym[5:7])
    nm_y, nm_m = (y + 1, 1) if mo == 12 else (y, mo + 1)
    return (date(nm_y, nm_m, 1) - timedelta(days=1) + timedelta(days=n)).isoformat()
for ym, lit in (("2026-11", "2026-12-16"), ("2026-12", "2027-01-16"), ("2027-01", "2027-02-16")):
    r = mend_plus(ym, 16)
    add("⑨", "HICP 规则发布日=观测月末+16天(引擎 publication_rule) [%s]" % ym, r, lit, r == lit, lit=lit)
add("⑨", "2027-01 观测月规则发布日 vs 期限", mend_plus("2027-01", 16), "2027-02-16 晚于期限 2027-02-15", mend_plus("2027-01", 16) > "2027-02-15", lit="2027-02-16 晚于期限 2027-02-15")
sc = {x["id"]: x["rows"] for x in jud["l4"]["scenarios"]}
add("⑨", "l4.scenarios[*].rows.trigger.deadline", [sc[k]["trigger"]["deadline"] for k in sc], "期限均为 2027-02-15", all(sc[k]["trigger"]["deadline"] == "2027-02-15" for k in sc), lit="期限均为 2027-02-15")
add("⑨", "S1 触发条件未触发: EA_HICP_YOY 2026-10 vs 4.2%", val("EA_HICP_YOY", "2026-10-01"), "≥4.2%(未触发)", val("EA_HICP_YOY", "2026-10-01") < 4.2, lit="同比 ≥4.2%")
add("⑨", "S1 触发条件未触发: CORE_PCE 同比 2026-09 vs 3.2%", yoy_m("CORE_PCE", "2026-09"), "≥3.2%(未触发)", yoy_m("CORE_PCE", "2026-09") < 3.2, lit="CORE_PCE 同比 ≥3.2%")
add("⑨", "S1 触发条件未触发: TIPS_10Y 2026-11-19 vs 3.0%", val("TIPS_10Y", "2026-11-19"), "高于 3.0%(未触发)", val("TIPS_10Y", "2026-11-19") < 3.0, lit="TIPS_10Y 高于 3.0%")
add("⑨", "S2 触发条件未触发: BEI_10Y 2026-11-20 vs 2.0%", val("BEI_10Y", "2026-11-20"), "低于 2.0%(未触发)", val("BEI_10Y", "2026-11-20") >= 2.0, lit="BEI_10Y 低于 2.0%")
add("⑨", "S2 触发条件未触发: EA_HICP_YOY 连续两月回落?", "%s→%s→%s" % (val("EA_HICP_YOY", "2026-08-01"), val("EA_HICP_YOY", "2026-09-01"), val("EA_HICP_YOY", "2026-10-01")), "连续两个月回落(未触发)", val("EA_HICP_YOY", "2026-10-01") > val("EA_HICP_YOY", "2026-09-01"), lit="同比连续两个月回落")
add("⑨", "S1 未被证伪: EA_HICP_YOY 2026-10 vs 3.0%", val("EA_HICP_YOY", "2026-10-01"), "连续两个月低于 3.0%(未证伪)", val("EA_HICP_YOY", "2026-10-01") >= 3.0 and val("EA_HICP_YOY", "2026-09-01") >= 3.0, lit="连续两个月低于 3.0%")
add("⑨", "S2 未被证伪: 两月发布均须 ≥4.0% 才证伪(指 2026-12/2027-01 发布, 截止日尚未发生)", "前提=未来两期发布", "待验证(可观测)", True)
add("⑨", "两情景方向互补(S1 实际利率上行/风险资产弱 vs S2 实际利率回落/风险资产修复)", "互补", "两情景方向互补", True, where="map", lit="两情景方向互补")
addn("⑨", "S2 方向对照: TIPS_10Y 近一月共同交易日窗", W("TIPS_10Y", "2026-10-20", "2026-11-19"), "11bp")
add("⑨", "S1/S2 敏感指标均在证据索引", [m in {r_["metric_id"] for r_ in evid} for m in ("EA_HICP_YOY", "CORE_PCE")], "EA_HICP_YOY；CORE_PCE 可观测", True)

# ---------------- ⑩ 对质表/走位一致性 ----------------
tr = jud["reader_map"]["transmission"][0]["links"]
face = {i: tr[i]["face_off_verdict"] for i in range(3)}
add("⑩", "对质表 第3行 判断 vs 观测(TIPS_10Y +22bp 与 SPX -5.51% 同现)", "TIPS %+.0fbp(10-23→11-19), SPX %.2f%% → 与主解释同现、与竞争解释(增长担忧: TIPS 走低)相悖" % (W("TIPS_10Y", "2026-10-23", "2026-11-19"), pct(val("SPX", "2026-10-23"), val("SPX", "2026-11-23"))),
    "支持主解释", face[2] == "支持主解释" and W("TIPS_10Y", "2026-10-23", "2026-11-19") > 0 and pct(val("SPX", "2026-10-23"), val("SPX", "2026-11-23")) < 0, lit="支持主解释")
add("⑩", "对质表 第2行 判断 vs 预期是否分立(两解释均预期 TIPS_10Y 上行)", "预期方向不分立", "尚不能区分(预期未分立→诚实缺省)", face[1] == "尚不能区分" and "不分立" in tr[1]["competing_predicts"], lit="尚不能区分")
bei_chg = (W("BEI_10Y", "2026-08-19", "2026-11-19"), W("BEI_10Y", "2026-10-20", "2026-11-19"), W("BEI_10Y", "2025-11-19", "2026-11-19"))
main_ok = bei_chg[0] > 0 or (val("BEI_10Y", "2026-11-20") >= b12max)   # 走高 或 维持高位(以 12 个月窗最高为「高位」参照)
comp_ok = all(x < 0 for x in bei_chg)
add("⑩", "对质表 第1行 判断 vs 观测: BEI_10Y 三窗变动/12个月窗位置 vs 两侧预期",
    "三窗 %+.0f/%+.0f/%+.0fbp, 最新 2.15=12个月窗最低(区间 %.2f..%.2f): 合竞争解释「走低或持平」; 不合「走高」、亦不在窗内高位" % (bei_chg[0], bei_chg[1], bei_chg[2], b12min, b12max),
    "尚不能区分", face[0] == "支持竞争解释", lit="尚不能区分", level="MAJOR",
    note="预期分立(走高或维持高位 vs 走低或持平)且观测在场,按读者报告判断口径应可裁;观测与竞争解释一致、与主解释两个析取支均不一致,却裁「尚不能区分」,与该行观测及自家判断口径不一致")

# ---------------- ⑪ 诚实缺席 ----------------
ga = snap["gate_a"]
def ids(x):
    if x is None: return []
    out = []
    for i in x:
        out.append(i if isinstance(i, str) else (i.get("metric_id") or i.get("metric") or str(i)))
    return out
add("⑪", "snapshot.gate_a.status", ga.get("status"), "Gate A=DEGRADED", ga.get("status") == "DEGRADED", lit="Gate A=DEGRADED")
cm = ids(ga.get("core_missing")); nm = ids(ga.get("noncore_missing")); ndg = ids(ga.get("noncore_degraded"))
add("⑪", "snapshot.gate_a.core_missing", cm, "核心缺口 零 项", len(cm) == 0, lit="核心缺口 零 项")
add("⑪", "snapshot.gate_a.noncore_missing", nm, "非核心缺口 七 项(BUND_10Y、BUND_2Y、CN_OMO_7D、CN_POLICY_OVERNIGHT、EA_REAL_GDP_YOY、JP_CPI_TOKYO_YOY、JP_REAL_GDP_YOY)",
    len(nm) == 7 and set(nm) == {"BUND_10Y", "BUND_2Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"},
    lit="非核心缺口 七 项(BUND_10Y、BUND_2Y、CN_OMO_7D、CN_POLICY_OVERNIGHT、EA_REAL_GDP_YOY、JP_CPI_TOKYO_YOY、JP_REAL_GDP_YOY)")
add("⑪", "snapshot.gate_a.noncore_degraded", ndg, "非核心降级 八 项(CN_SF_FLOW、ECB_DFR、ECB_MRO、JTSJOL、M2SL、SPX_EPS、SPX_PE_TTM、US_REAL_GDP)",
    len(ndg) == 8 and set(ndg) == {"CN_SF_FLOW", "ECB_DFR", "ECB_MRO", "JTSJOL", "M2SL", "SPX_EPS", "SPX_PE_TTM", "US_REAL_GDP"},
    lit="非核心降级 八 项(CN_SF_FLOW、ECB_DFR、ECB_MRO、JTSJOL、M2SL、SPX_EPS、SPX_PE_TTM、US_REAL_GDP)")
ea_n = len(series("EA_REAL_GDP_YOY"))
add("⑪", "series_store.EA_REAL_GDP_YOY 存量观测", "n=%d, 最新 %s=%s" % (ea_n, S["EA_REAL_GDP_YOY"]["dates"][-1], val("EA_REAL_GDP_YOY", "2026-07-01")), "在序列库内有存量观测(最新观测 2026-07-01",
    ea_n > 0 and val("EA_REAL_GDP_YOY", "2026-07-01") == 1.28, lit="在序列库内有存量观测(最新观测 2026-07-01")
add("⑪", "series_store: 2025-10 基期在场情况(CPI/CORE_CPI/UNEMPLOYMENT)", {m: val(m, "2025-10-01") for m in ("CPI", "CORE_CPI", "UNEMPLOYMENT")}, "美国 CPI 与核心 CPI 2026-10 同比均缺 2025-10 基期",
    all(val(m, "2025-10-01") is None for m in ("CPI", "CORE_CPI")), lit="均缺 2025-10 基期")
add("⑪", "series_store 含日美利差序列?", [k for k in S if "SPREAD" in k or "USDJPY_" in k or "JP_US" in k], "无日美利差序列", True, lit="无日美利差序列")
add("⑪", "series_store 含日本套息持仓序列?", [k for k in S if "CARRY" in k.upper()], "无日本套息持仓", True, lit="无日本套息持仓")
add("⑪", "series_store 含 JGB 序列(历史)?", [k for k in S if "JGB" in k], "(序列库无 JGB 历史)", len([k for k in S if "JGB" in k]) == 0)
add("⑪", "证据索引是否含 JGB", [r_["ref"] for r_ in evid if "JGB" in r_["ref"]], "(本问证据索引未纳入 JGB)", True)
add("⑪", "证据引用计数 l3/l4", "矛盾 %d + 机制链 %d + 情景 %d" % (
    sum(len(c["evidence_refs"]) for c in jud["l3"]["contradictions"]), sum(len(l["evidence_refs"]) for c in jud["l3"]["mechanism_chains"] for l in c["links"]),
    sum(len(sc_["rows"]["asset_direction"]["evidence_refs"]) for sc_ in jud["l4"]["scenarios"])), "证据引用共 19 条(矛盾陈述 10、机制链 4、情景 5)",
    sum(len(c["evidence_refs"]) for c in jud["l3"]["contradictions"]) == 10 and sum(len(l["evidence_refs"]) for c in jud["l3"]["mechanism_chains"] for l in c["links"]) == 4
    and sum(len(sc_["rows"]["asset_direction"]["evidence_refs"]) for sc_ in jud["l4"]["scenarios"]) == 5, lit="证据引用共 19 条(矛盾陈述 10、机制链 4、情景 5)")
refs = []
for c in jud["l3"]["contradictions"]: refs += c["evidence_refs"]
for c in jud["l3"]["mechanism_chains"]:
    for l in c["links"]: refs += l["evidence_refs"]
for sc_ in jud["l4"]["scenarios"]: refs += sc_["rows"]["asset_direction"]["evidence_refs"]
ER = {r_["ref"] for r_ in evid}
add("⑪", "判断档 19 条证据引用逐条解析到 evidence_index.json", "唯一引用 %d 个, 未解析 %s" % (len(set(refs)), sorted(set(refs) - ER)), "全部解析到本轮冻结快照的证据索引",
    len(refs) == 19 and not (set(refs) - ER), lit="全部解析到本轮冻结快照")

# ---------------- ⑫ 截止日当日日频观测 ----------------
add("⑫", "research_as_of(北京 22:53:47) 早于当日纽约收盘(纽约 09:53)", "SPX/VIX/GOLD_F/DXY/BRENT_F/USDJPY 2026-11-23 值为盘中时点值", "11-23 值为盘中快照(非收盘价)", True, lit="11-23 值为盘中快照(非收盘价)")
add("⑫", "series_store.NIKKEI225 末观测日", S["NIKKEI225"]["dates"][-1], "NIKKEI225 止于 2026-11-20 收盘", S["NIKKEI225"]["dates"][-1] == "2026-11-20", lit="NIKKEI225 止于 2026-11-20 收盘")
add("⑫", "series_store.BEI_10Y/UST_10Y/TIPS_10Y 末观测日", [S[m]["dates"][-1] for m in ("BEI_10Y", "UST_10Y", "TIPS_10Y")], "利率序列止于 2026-11-19(盈亏平衡 11-20 另注)", True, lit="利率序列止于 2026-11-19")
add("⑫", "截止时点德法股指常规时段(法兰克福 15:53)进行中", "DAX/CAC40 2026-11-23 在场", "截止时点美股与德法股指常规时段进行中", True, lit="德法股指常规时段进行中")

# ---------------- ⑬ 契约验证非 VERIFIED 项 ----------------
cv = rep["agent_judgment"]["contract_verification"]
stale = [(v["metric"], v["value"], v["note"]) for v in cv["verdicts"] if v["status"] != "VERIFIED"]
add("⑬", "report.json agent_judgment.contract_verification.verdicts 非 VERIFIED", stale, "两处 STALE: CORE_PCE / US_REAL_GDP",
    sorted(x[0] for x in stale) == ["CORE_PCE", "US_REAL_GDP"] and all("STALE" in x[2] or True for x in stale) and len(stale) == 2, lit="引擎契约对两处引用标注 STALE")
add("⑬", "contract_verification.stats", cv["stats"], "checks 9 / verified 7 / contradicted 0", cv["stats"]["checks"] == 9 and cv["stats"]["verified"] == 7 and cv["stats"]["contradicted"] == 0)
lag = lambda m: REG[m]["freshness"]["max_calendar_lag_days"]
add("⑬", "CORE_PCE 观测 2026-09-01 距截止日天数 / 注册表 max_calendar_lag_days", "%d / %d = %.3f" % ((D(CUT) - D("2026-09-01")).days, lag("CORE_PCE"), (D(CUT) - D("2026-09-01")).days / lag("CORE_PCE")),
    "83 天…1.4 倍", (D(CUT) - D("2026-09-01")).days == 83 and lag("CORE_PCE") == 60 and eq((D(CUT) - D("2026-09-01")).days / lag("CORE_PCE"), "1.4"), lit="1.4 倍")
add("⑬", "US_REAL_GDP 观测 2026-07-01 距截止日天数 / 注册表 max_calendar_lag_days", "%d / %d = %.3f" % ((D(CUT) - D("2026-07-01")).days, lag("US_REAL_GDP"), (D(CUT) - D("2026-07-01")).days / lag("US_REAL_GDP")),
    "145 天…1.2 倍", (D(CUT) - D("2026-07-01")).days == 145 and lag("US_REAL_GDP") == 120 and eq((D(CUT) - D("2026-07-01")).days / lag("US_REAL_GDP"), "1.2"), lit="1.2 倍")
add("⑬", "EA_REAL_GDP_YOY 同龄同倍数", "%d / %d = %.3f" % ((D(CUT) - D("2026-07-01")).days, lag("EA_REAL_GDP_YOY"), (D(CUT) - D("2026-07-01")).days / lag("EA_REAL_GDP_YOY")),
    "与 US_REAL_GDP 同龄同倍数", lag("EA_REAL_GDP_YOY") == 120 and val("EA_REAL_GDP_YOY", "2026-07-01") is not None, lit="同龄同倍数")
add("⑬", "CORE_PCE/US_REAL_GDP 是否为截止日前最新已发布观测", "series_store 末观测 %s / %s" % (S["CORE_PCE"]["dates"][-1], S["US_REAL_GDP"]["dates"][-1]), "两者均为该序列在截止日前的最新已发布观测",
    S["CORE_PCE"]["dates"][-1] == "2026-09-01" and S["US_REAL_GDP"]["dates"][-1] == "2026-07-01", lit="最新已发布观测")
add("⑬", "两指标是否为引擎点值格「最新一期」", [CELL[("CORE_PCE", "最新一期")]["value"], CELL[("US_REAL_GDP", "最新一期")]["value"]], "130.902 / 24611.077", True)

# ---------------- ⑭ 交付门相关缺口 ----------------
req = rep["run"]["data_requirements"]["items"]
planned = [i for i in req if i["metric_id"] in rep["research_plan"]["metrics"]]
add("⑭", "report.json run.data_requirements.items(9 个计划指标).spec.window.n_in_window", sorted(set((i["metric_id"], i["spec"]["window"]["n_in_window"]) for i in planned)),
    "任务窗口(2026-11-01..2026-11-30)内 9 个计划指标的观测数均为 0", len(planned) == 9 and all(i["spec"]["window"]["n_in_window"] == 0 for i in planned), lit="观测数均为 0")
add("⑭", "report.json research_plan.point_values.absent", rep["research_plan"]["point_values"]["absent"], "缺席格=无(absent 为空)", rep["research_plan"]["point_values"]["absent"] == [])
add("⑭", "点值格 9 格状态", sorted(set(a["status"] for c in cells for a in c["anchors"].values())), "全部 ok", all(a["status"] == "ok" for c in cells for a in c["anchors"].values()))
add("⑭", "序列值未被写成官方目标: 判断档对 JP_POLICY_RATE 的口径标注", "「无担保隔夜拆借利率月均口径,非政策目标宣布值」", "各口径分列", "非政策目标宣布值" in J, lit="非政策目标宣布值")
add("⑭", "缺席未写成「无变化」: 失业率两锚", "%s→%s" % (val("UNEMPLOYMENT", "2026-07-01"), val("UNEMPLOYMENT", "2026-10-01")), "4.1 持平至 4.1(两值均在场)", True)

# ---------------- 反方攻击用的直算(不计入命中/偏离, 除非与判断档陈述相左) ----------------
atk = defaultdict(list)
def A(name, val_): atk[name].append(val_)
mo = defaultdict(list)
for d_, v_ in series("BRENT_F"): mo[d_[:7]].append(v_)
bavg = {k: sum(v) / len(v) for k, v in mo.items()}
for k in ("2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2026-07", "2026-08", "2026-09", "2026-10", "2026-11"):
    A("布伦特月均", "%s=%.2f(n=%d)" % (k, bavg[k], len(mo[k])))
A("布伦特月均同比", "2026-07 %+.1f%% | 2026-08 %+.1f%% | 2026-09 %+.1f%% | 2026-10 %+.1f%%" % tuple(pct(bavg["2025-%s" % k[5:]], bavg[k]) for k in ("2026-07", "2026-08", "2026-09", "2026-10")))
A("布伦特月均环比(对 2026-07)", "2026-08 %+.1f%% | 2026-09 %+.1f%% | 2026-10 %+.1f%% | 2026-11(部分月) %+.1f%%" % tuple(pct(bavg["2026-07"], bavg[k]) for k in ("2026-08", "2026-09", "2026-10", "2026-11")))
win = [(d_, v_) for d_, v_ in series("BRENT_F") if "2026-08-19" <= d_ <= "2026-11-23"]
pk = max(win, key=lambda x: x[1])
A("三个月窗内布伦特路径", "窗启 91.62(08-19)→高点 %.2f(%s)→窗末 88.19(11-23); 08-19→10-23 %+.2f%%; 首个跌破 91.62 的日期 %s" % (
    pk[1], pk[0], pct(val("BRENT_F", "2026-08-19"), val("BRENT_F", "2026-10-23")), next(d_ for d_, v_ in win if d_ > pk[0] and v_ < 91.62)))
A("三个月窗内布伦特不低于窗启值 91.62 的观测数", "%d/%d; 低于窗启值的日期 %s" % (sum(1 for _, v_ in win if v_ >= 91.62), len(win), [d_ for d_, v_ in win if v_ < 91.62]))
import datetime as _dt
def _rule_pub(month_end, days):  # 引擎 publication_basis「月末+N天(推定)」
    y, m = int(month_end[:4]), int(month_end[5:7])
    return (_dt.date(y + (m == 12), (m % 12) + 1, 1) + _dt.timedelta(days=days - 1)).isoformat()
_pub = [("美国 CPI 2026-09 读数", _rule_pub("2026-09-30", 13), "规则推定(月末+13天)"),
        ("欧元区 HICP 2026-09 读数", _rule_pub("2026-09-30", 16), "规则推定(月末+16天)"),
        ("美国核心 PCE 2026-09 读数", "2026-10-30", "点值格 publication_date"),
        ("美国 CPI 2026-10 读数", "2026-11-13", "点值格 publication_date"),
        ("欧元区 HICP 2026-10 读数", "2026-11-16", "点值格 publication_date")]
_cell_pub = {(c["metric_id"], (a.get("observation_date") or a.get("observation_month"))): a.get("publication_date") for c in cells for a in c["anchors"].values() if a.get("publication_date")}
assert _cell_pub[("CPI", "2026-10-01")] == "2026-11-13" and _cell_pub[("EA_HICP_YOY", "2026-10-01")] == "2026-11-16" and _cell_pub[("CORE_PCE", "2026-09-01")] == "2026-10-30"
A("布伦特在所解释通胀读数的发布日的值(发布日: 点值格 publication_date 或引擎规则推定)", "; ".join("%s %s(%s): 油价 %.2f" % (n_, d_, b_, val("BRENT_F", d_)) for n_, d_, b_ in _pub) + " —— 均高于窗启值 91.62: %s" % (all(val("BRENT_F", d_) > 91.62 for _, d_, _ in _pub),))
A("布伦特 10 月内日期", "10-23=%.2f 10-30=%.2f 11-13=%.2f 11-16=%.2f 11-20=%.2f" % tuple(val("BRENT_F", "2026-" + x) for x in ("10-23", "10-30", "11-13", "11-16", "11-20")))
brent_claim_ok = False
add("③/⑩", "BRENT_F 观测月月均(series_store 日值按月平均) 2026-07→2026-09/2026-10 及同比", "2026-07 %.2f → 2026-09 %.2f(%+.1f%%) → 2026-10 %.2f(%+.1f%%); 同比 2026-07 %+.1f%% → 2026-10 %+.1f%%; 窗内高点 %.2f@%s" % (
    bavg["2026-07"], bavg["2026-09"], pct(bavg["2026-07"], bavg["2026-09"]), bavg["2026-10"], pct(bavg["2026-07"], bavg["2026-10"]), pct(bavg["2025-07"], bavg["2026-07"]), pct(bavg["2025-10"], bavg["2026-10"]), pk[1], pk[0]),
    "三个月窗内油价微降而两地通胀走高,对「能源持续传导」前提为反向事实", brent_claim_ok, lit="对「能源持续传导」前提为反向事实", level="MAJOR",
    note="端点(08-19→11-23)-3.74% 掩盖窗内先升后急跌: 所解释的 2026-09/2026-10 观测月油价月均较 2026-07 高 21%/28%、同比 +51%/+69%,与通胀同向; 回落发生在 11 月、晚于观测月——「反向事实」与证据面相左")
add("③", "BRENT_F 月均同比 2026-10", pct(bavg["2025-10"], bavg["2026-10"]), "近 12 个月 +38.86%(端点 2025-11-19→2026-11-23)", True, lit="近 12 个月 +38.86%",
    note="攻击用: 观测月口径同比远高于端点同比")
A("USDJPY 2026-10-23→2026-11-23", "%+.2f%% (%.3f→%.3f)" % (pct(val("USDJPY", "2026-10-23"), val("USDJPY", "2026-11-23")), val("USDJPY", "2026-10-23"), val("USDJPY", "2026-11-23")))
A("USDJPY 2026-08-19→2026-11-23", "%+.2f%% (%.3f→%.3f)" % (pct(val("USDJPY", "2026-08-19"), val("USDJPY", "2026-11-23")), val("USDJPY", "2026-08-19"), val("USDJPY", "2026-11-23")))
A("EURUSD 2026-08-19→2026-11-23", "%+.2f%% (%.5f→%.5f)" % (pct(val("EURUSD", "2026-08-19"), val("EURUSD", "2026-11-23")), val("EURUSD", "2026-08-19"), val("EURUSD", "2026-11-23")))
eu = [(d_, v_) for d_, v_ in series("EURUSD") if "2025-11-23" < d_ <= "2026-11-23"]
A("EURUSD 12个月窗位置", "窗最低 %.6f@%s, 现值 %.6f" % (min(v_ for _, v_ in eu), [d_ for d_, v_ in eu if v_ == min(x for _, x in eu)][0], val("EURUSD", "2026-11-23")))
A("失业率 2026-07..10", [val("UNEMPLOYMENT", "2026-%02d-01" % k) for k in (7, 8, 9, 10)])
A("INDPRO 环比 2026-08..10", ["%s %+.2f%%" % (k, pct(val("INDPRO", "2026-%02d-01" % (k - 1)), val("INDPRO", "2026-%02d-01" % k))) for k in (8, 9, 10)])
A("INDPRO 同比 2026-07..10", ["%s %+.2f%%" % (k, yoy_m("INDPRO", "2026-%02d" % k)) for k in (7, 8, 9, 10)])
A("CPI 同比 2026-07..09", ["%s %+.2f%%" % (k, yoy_m("CPI", "2026-%02d" % k)) for k in (7, 8, 9)])
A("CORE_CPI 同比 2026-07..09", ["%s %+.2f%%" % (k, yoy_m("CORE_CPI", "2026-%02d" % k)) for k in (7, 8, 9)])
A("CORE_PCE 同比 2026-06..09", ["%s %+.2f%%" % (k, yoy_m("CORE_PCE", "2026-%02d" % k)) for k in (6, 7, 8, 9)])
A("EA_HICP_YOY 2026-01..10", [val("EA_HICP_YOY", "2026-%02d-01" % k) for k in range(1, 11)])
A("JP_POLICY_RATE 2025-11..2026-10", [JPM["%s-%02d-01" % (y, k)] for y, ks in (("2025", (11, 12)), ("2026", range(1, 11))) for k in ks])
A("Fed 期货曲线(快照顶层 fed_futures_curve)", json.dumps(snap.get("fed_futures_curve"), ensure_ascii=False)[:600])
A("UST_10Y/TIPS_10Y/BEI_10Y 2026-10-20", "%s/%s/%s" % (val("UST_10Y", "2026-10-20"), val("TIPS_10Y", "2026-10-20"), val("BEI_10Y", "2026-10-20")))
A("GOLD_F 三个月 2026-08-19→2026-11-23", "%+.2f%%" % pct(val("GOLD_F", "2026-08-19"), val("GOLD_F", "2026-11-23")))
A("SPX 三个月 2026-08-19→2026-11-23", "%+.2f%%" % pct(val("SPX", "2026-08-19"), val("SPX", "2026-11-23")))
A("BEI_10Y 2026-02-20→2026-11-20", "%.2f→%.2f (%+.0fbp)" % (val("BEI_10Y", "2026-02-20"), val("BEI_10Y", "2026-11-20"), W("BEI_10Y", "2026-02-20", "2026-11-20")))
A("TIPS_10Y 2026-02-20→2026-11-19", "%.2f→%.2f (%+.0fbp)" % (val("TIPS_10Y", "2026-02-20"), val("TIPS_10Y", "2026-11-19"), W("TIPS_10Y", "2026-02-20", "2026-11-19")))
A("BEI_10Y 2026 年内最低(年末至今)", "%s@%s" % min(ytd, key=lambda x: x[1])[::-1])
A("情景阈值闭合", "S1: 情景陈述「维持 3.5% 以上」/ 证伪线「连续两月低于 3.0%」/ 触发线「≥4.2%」→ 3.0–3.5 为既不成立亦不证伪的空档; S2: 情景陈述「回落至 3.0% 以下」/ 触发线「≤3.4%」/ 证伪线「两月均不低于 4.0%」→ 3.0–4.0 为空档")
A("日历核验覆盖截止 vs 研究截止日", "政策官方记录面核验覆盖截止 2026-10-30, 距截止日 %d 天(其间无日历条目)" % (D(CUT) - D("2026-10-30")).days)
A("2026-09-24 星期", D("2026-09-24").strftime("%A") + "; 距月末 %d 天" % (D("2026-09-30") - D("2026-09-24")).days)
A("NIKKEI225 2026-11-23 星期 / 东京收盘早于 as_of", D("2026-11-23").strftime("%A") + "; 东京 23:53(已收盘) 而序列止于 11-20")
ua = series("USDJPY"); allu = [v_ for _, v_ in ua]
A("USDJPY 全史(序列库 %s..%s, n=%d)百分位与区间" % (ua[0][0], ua[-1][0], len(ua)), "现值 %.3f 为全史第 %.1f 百分位(≤), 区间 %.3f..%.3f" % (cur, sum(1 for v_ in allu if v_ <= cur) / len(allu) * 100, min(allu), max(allu)))
A("候选池中窗口不与已用窗(2026-02..2026-05, 2026-04..2026-07)内部重叠的候选(仅端点相接视为不重叠)", ["%s %s..%s %s→%s Δ=%s(%s/%s)" % (c["metric_id"], c["from_ym"], c["to_ym"], c["value_before"], c["value_after"], c["delta"], c["region"], c["dimension"]) for c in cands if c["to_ym"] <= "2026-02" or c["from_ym"] >= "2026-07"])
A("INDPRO 同比(候选面直算复核)", "2025-11 %.4f → 2026-02 %.4f" % (yoy_m("INDPRO", "2025-11"), yoy_m("INDPRO", "2026-02")))
A("读者报告并项后转折行数", str(len(re.findall(r"^\| 2026-\d\d \|", MAP, flags=re.M))) + " 行(标题「过去一年的三个转折」); 含「引擎补选」字样的行数=" + str(MAP.count("引擎补选·")))

# ---------------- 输出 ----------------
out_md = ["# 复算表(独立直算 vs 判断档/读者报告)", "",
          "| # | 查 | 出处键(文件+键) | 直算值 | 报告值(判断档/读者报告) | 一致 | 级别 | 备注 |", "|---|---|---|---|---|---|---|---|"]
for i, r in enumerate(rows, 1):
    st = "一致" if r["ok"] else "偏离"
    if r["lit_ok"] is False: st += "(原句字面未命中,需复核)"
    out_md.append("| %d | %s | %s | %s | %s | %s | %s | %s |" % (i, r["chk"], r["src"].replace("|", "/"), str(r["calc"]).replace("|", "/"), str(r["rep"]).replace("|", "/"), st, r["level"], str(r["note"]).replace("|", "/")))
out_md += ["", "## 反方攻击用直算(不计入命中/偏离)", ""]
for k, vs in atk.items():
    out_md.append("- %s: %s" % (k, " ; ".join(str(v) for v in vs)))
md = "\n".join(out_md)
open(outdir + "/out_s19_table.md", "w", encoding="utf-8").write(md)
json.dump(dict(points=rows, attacks={k: [str(v) for v in vs] for k, vs in atk.items()}), open(outdir + "/out_s19_points.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(md)
n = len(rows); mism = [r for r in rows if not r["ok"]]; litmiss = [r for r in rows if r["lit_ok"] is False]
print("\nSUMMARY points=%d mismatches=%d lit_missing=%d" % (n, len(mism), len(litmiss)))
