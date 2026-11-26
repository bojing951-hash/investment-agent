#!/usr/bin/python3 -I
# s02d: 公布时间 / 截止日纪律 / Gate A 与缺口披露 / 契约验证 / 时点 独立复算(只读)
import sys, os, json, re, datetime as dt
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rc_lib import *

snap_p, rep_p, cal_p, reg_p, aj_p, outdir = sys.argv[1:7]
snap, rep, cal, reg, aj = load(snap_p, rep_p, cal_p, reg_p, aj_p)
SS = snap["series_store"]
P = Points()
RP = "report.json research_plan.point_values.cells"
cells = rep["research_plan"]["point_values"]["cells"]
pv = {}
for c in cells:
    pv[(c["metric_id"], "anc")] = c["anchors"].get("3个月前", {})
    pv[(c["metric_id"], "lat")] = c["anchors"].get("最新一期", {})

# ---------- 公布时间: 受审稿日期 = 引擎点值格 publication_date, 且按引擎所载规则独立重算 ----------
def eom(ym):
    y, m = int(ym[:4]), int(ym[5:7])
    return "%04d-%02d-%02d" % (y + (m // 12), (m % 12) + 1, 1) if False else (dt.date(y + (m // 12), (m % 12) + 1, 1) - dt.timedelta(days=1)).isoformat()
rules = {  # metric -> (规则名, 函数: (period_end, observation_date) -> 发布日)
    "US_REAL_GDP": ("季末+29天", lambda pe, od: plus_days(pe, 29)),
    "UNEMPLOYMENT": ("月末+5天", lambda pe, od: plus_days(pe, 5)),
    "INDPRO": ("月末+15天", lambda pe, od: plus_days(pe, 15)),
    "CPI": ("月末+13天", lambda pe, od: plus_days(pe, 13)),
    "CORE_CPI": ("月末+13天", lambda pe, od: plus_days(pe, 13)),
    "CORE_PCE": ("月末+30天", lambda pe, od: plus_days(pe, 30)),
    "DFF": ("观测日+1天", lambda pe, od: plus_days(od, 1)),
    "CN_PMI_MFG": ("月末-1天", lambda pe, od: plus_days(pe, -1)),
    "CN_CPI_YOY": ("月末+9天", lambda pe, od: plus_days(pe, 9)),
    "CN_PPI_YOY": ("月末+9天", lambda pe, od: plus_days(pe, 9)),
    "JP_REAL_GDP_YOY": ("季末+45天", lambda pe, od: plus_days(pe, 45)),
    "JP_CPI_YOY": ("月末+20天", lambda pe, od: plus_days(pe, 20)),
    "JP_CPI_TOKYO_YOY": ("月末-1天", lambda pe, od: plus_days(pe, -1)),
    "JP_POLICY_RATE": ("月末+5天", lambda pe, od: plus_days(pe, 5)),
}
reported = {  # 受审稿所载发布日 (三个月前锚, 最新一期)
    "US_REAL_GDP": ("2026-07-29", "2026-10-29"), "UNEMPLOYMENT": ("2026-08-05", "2026-11-05"),
    "INDPRO": ("2026-08-15", "2026-11-15"), "CPI": ("2026-08-13", "2026-11-13"), "CORE_CPI": ("2026-08-13", "2026-11-13"),
    "CORE_PCE": ("2026-07-30", "2026-10-30"), "DFF": ("2026-08-23", "2026-11-20"), "CN_PMI_MFG": ("2026-07-30", "2026-10-30"),
    "CN_CPI_YOY": ("2026-08-09", "2026-11-09"), "CN_PPI_YOY": ("2026-08-09", "2026-11-09"), "JP_REAL_GDP_YOY": ("2026-08-14", "2026-11-14"),
    "JP_CPI_YOY": ("2026-08-20", "2026-11-20"), "JP_CPI_TOKYO_YOY": ("2026-07-30", "2026-10-30"), "JP_POLICY_RATE": ("2026-08-05", "2026-11-05"),
}
n = 1
for mid, (ra, rl) in reported.items():
    name, fn = rules[mid]
    for which, repd in (("anc", ra), ("lat", rl)):
        a = pv[(mid, which)]
        eng = a.get("publication_date")
        pe = a.get("period_end") or a.get("observation_date")
        calc = fn(pe, a.get("observation_date"))
        P.adds("U%02d" % n, RP, "%s[%s].publication_date(=%s; 规则%s自 period_end %s 重算=%s)" % (mid, which, eng, name, pe, calc), calc if calc == eng else "engine=%s/rule=%s" % (eng, calc), repd)
        n += 1
P.addb("U29", RP, "所引发布日(锚格)全部 ≤ 2026-08-23", all(pv[(m, "anc")].get("publication_date", "9999") <= ANC for m in reported))
P.addb("U30", RP, "所引发布日(最新一期)全部 ≤ 2026-11-23", all(pv[(m, "lat")].get("publication_date", "9999") <= CUT for m in reported))
P.addb("U31", RP, "锚格观测日全部 ≤ 2026-08-23", all(pv[(m, "anc")].get("observation_date", "9999") <= ANC for m in reported))
P.addb("U32", RP, "最新一格观测日全部 ≤ 2026-11-23", all(pv[(m, "lat")].get("observation_date", "9999") <= CUT for m in reported))
P.addb("U33", RP, "受审稿所称『引擎推定规则、非日历实录』: 除 CN_LPR_1Y 最新一期外, 所引发布日的 publication_basis 不含 calendar:", all("calendar" not in str(pv[(m, w)].get("publication_basis")) for m in reported for w in ("anc", "lat")) and str(pv[("CN_LPR_1Y", "lat")].get("publication_basis")).startswith("calendar:RC-CN-LPR-2026M11"))
P.addb("U34", RP, "东京都CPI/美国GDP 发布口径含『官方实测锚』", all(("实测锚" in str(pv[(m, w)].get("publication_basis")) or "实录锚" in str(pv[(m, w)].get("publication_basis"))) for m in ("JP_CPI_TOKYO_YOY", "US_REAL_GDP") for w in ("anc", "lat")))
P.addb("U35", RP, "DFEDTARU 发布口径=决议日当日公布、观测日=序列打印日(2026-08-23 / 2026-11-23)", pv[("DFEDTARU", "anc")]["observation_date"] == ANC and pv[("DFEDTARU", "lat")]["observation_date"] == CUT and "决议日当日公布" in str(pv[("DFEDTARU", "lat")].get("publication_basis")))
for d, wd_ in (("2026-11-14", "Saturday"), ("2026-11-15", "Sunday"), ("2026-11-05", "Thursday"), ("2026-11-13", "Friday"), ("2026-11-09", "Monday"), ("2026-11-20", "Friday")):
    P.adds("U_wd_" + d, "datetime", "推定发布日 %s 星期" % d, wd(d), wd_, "仅记录星期(引擎推定规则, 受审稿已标注非日历实录)")

# ---------- 截止日纪律: 受审稿内全部 ISO 日期 ----------
txt = json.dumps(aj, ensure_ascii=False)
dates = sorted(set(re.findall(r"20\d\d-\d\d-\d\d", txt)))
after = [d for d in dates if d > CUT]
P.adds("D01", "agent_judgment.json 全文日期扫描", "晚于研究截止日 2026-11-23 的日期(应仅为情景期限)", ",".join(after), "2027-02-23,2027-02-28")
used = ["DFEDTARU", "DFEDTARL", "DFF", "JP_POLICY_RATE", "CN_LPR_1Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "JP_CPI_YOY", "JP_CPI_TOKYO_YOY",
        "CPI", "CORE_CPI", "CORE_PCE", "CN_CPI_YOY", "CN_PPI_YOY", "US_REAL_GDP", "UNEMPLOYMENT", "INDPRO", "CN_PMI_MFG", "JP_REAL_GDP_YOY",
        "SPX", "NIKKEI225", "SHCOMP", "DAX", "CAC40", "VIX", "DXY", "USDJPY", "USDCNY", "UST_10Y", "TIPS_10Y", "BEI_10Y", "WTI_F", "BRENT_F", "WTI_SPOT_M"]
P.addb("D02", SNAP, "受审稿所用 %d 条序列的末观测日均 ≤ 2026-11-23" % len(used), all(last(SS, m)[0] <= CUT for m in used), str([(m, last(SS, m)[0]) for m in used if last(SS, m)[0] > CUT]))
P.adds("D03", "snapshot.research_as_of", "research_as_of", snap["research_as_of"], "2026-11-23T22:58:11+08:00")
P.adds("D04", "report.json research_plan.cutoff", "cutoff", rep["research_plan"]["cutoff"], "2026-11-23")
t = dt.datetime(2026, 11, 23, 22, 58, 11, tzinfo=ZoneInfo("Asia/Shanghai"))
for tz, exp, nm in (("America/New_York", "09:58:11", "纽约"), ("Europe/Berlin", "15:58:11", "法兰克福"), ("Asia/Tokyo", "23:58:11", "东京"), ("Asia/Shanghai", "22:58:11", "上海")):
    P.adds("D05_" + tz.split("/")[1], "snapshot.research_as_of + IANA 时区换算", "%s 当地时刻" % nm, t.astimezone(ZoneInfo(tz)).strftime("%H:%M:%S"), exp)
_y, _m = (2026, 11 - 3)
P.adds("D06", "datetime", "研究截止 2026-11-23 - 3 个日历月(日取 23)", "%04d-%02d-23" % (_y, _m), "2026-08-23")
P.addb("D07", RP, "三个月前锚 as_of 全部 = 2026-08-23", all(a.get("as_of") == ANC for (m, w), a in pv.items() if w == "anc"))
P.addb("D08", RP, "最新一期锚 as_of 全部 = 2026-11-23", all(a.get("as_of") == CUT for (m, w), a in pv.items() if w == "lat"))
pa = rep["research_plan"]["point_anchors"]
P.addb("D09", "report.json research_plan.point_anchors", "点锚定义: 3个月前=2026-08-23, 最新一期=2026-11-23", any(x.get("label") == "3个月前" and x.get("as_of") == ANC for x in pa) and any(x.get("label") == "最新一期" and x.get("as_of") == CUT for x in pa))

# ---------- Gate A / 缺口披露 ----------
ga = snap["gate_a"]
G = "snapshot.gate_a"
P.adds("Q01", G + ".status", "status", ga["status"], "DEGRADED")
P.add("Q02", G + ".core_missing", "core_missing 项数", len(ga["core_missing"]), 0, 0)
P.adds("Q03", G + ".noncore_missing", "非核心缺口 10 项(排序)", ",".join(sorted(ga["noncore_missing"])), "BUND_10Y,BUND_2Y,CN_OMO_7D,CN_POLICY_OVERNIGHT,EA_HICP_YOY,EA_REAL_GDP_YOY,ECB_DFR,ECB_MRO,JP_CPI_TOKYO_YOY,JP_REAL_GDP_YOY")
P.adds("Q04", G + ".noncore_degraded", "非核心降级 6 项(排序)", ",".join(sorted(ga["noncore_degraded"])), "CN_SF_FLOW,JTSJOL,M2SL,SPX_EPS,SPX_PE_TTM,US_REAL_GDP")
P.add("Q05", G + ".core_fail", "core_fail 项数", len(ga["core_fail"]), 0, 0)
P.add("Q06", G + ".noncore_fail", "noncore_fail 项数", len(ga["noncore_fail"]), 0, 0)
q = snap["quality"]
P.add("Q07", "snapshot.quality.counts", "PASS 计数", q["counts"].get("PASS"), 72, 0)
P.add("Q08", "snapshot.quality.counts", "DEGRADED 计数", q["counts"].get("DEGRADED"), 7, 0)
P.add("Q09", "snapshot.quality.counts", "FAIL 计数", q["counts"].get("FAIL"), 0, 0)
P.add("Q10", "snapshot.quality.missing_core", "missing_core 项数", len(q["missing_core"]), 0, 0)
P.add("Q11", "report.json evidence_index", "证据索引行数", len(rep["evidence_index"]), 69, 0)
P.addb("Q12", "snapshot.gate_a.noncore_missing", "被列入缺口的 CN_OMO_7D/CN_POLICY_OVERNIGHT/JP_CPI_TOKYO_YOY/JP_REAL_GDP_YOY 在 series_store 有存量观测", all(m in SS for m in ("CN_OMO_7D", "CN_POLICY_OVERNIGHT", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY")), str({m: len(SS[m]["dates"]) for m in ("CN_OMO_7D", "CN_POLICY_OVERNIGHT", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY")}))
P.addb("Q13", "snapshot.gate_a.noncore_missing", "六项欧元区序列在 series_store 缺席且 sources_status.ea 含 MISSING", all(m not in SS for m in ("BUND_10Y", "BUND_2Y", "EA_HICP_YOY", "EA_REAL_GDP_YOY", "ECB_DFR", "ECB_MRO")) and "MISSING" in json.dumps(snap["sources_status"].get("ea"), ensure_ascii=False), json.dumps(snap["sources_status"].get("ea"), ensure_ascii=False)[:300])
# 证据索引成员: 受审稿声称『不在本轮证据索引』的序列
eidx = set(r.get("metric_id") for r in rep["evidence_index"])
for k, m in enumerate(["JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "WTI_SPOT_M"]):
    P.addb("Q%02d" % (14 + k), "report.json evidence_index[*].metric_id", "受审稿称『不在本轮证据索引』: %s" % m, m not in eidx)
refs = []
for c in aj["l3"]["contradictions"]:
    refs += [r.split("@")[0] for r in c["evidence_refs"]]
for ch in aj["l3"]["mechanism_chains"]:
    for l in ch["links"]:
        refs += [r.split("@")[0] for r in l["evidence_refs"]]
for s in aj["l4"]["scenarios"]:
    refs += [r.split("@")[0] for r in s["rows"]["asset_direction"]["evidence_refs"]]
missing_refs = sorted(set(r for r in refs if r not in eidx))
P.addb("Q19", "report.json evidence_index × agent_judgment evidence_refs", "L3/L4 全部 evidence_refs 的指标均在证据索引内 (n_refs=%d)" % len(refs), len(missing_refs) == 0, str(missing_refs))

# ---------- 契约验证 ----------
cv = rep["agent_judgment"]["contract_verification"]
st = cv["stats"]
P.add("K01", "report.json agent_judgment.contract_verification.stats", "checks", st["checks"], 17, 0)
P.add("K02", "report.json agent_judgment.contract_verification.stats", "verified", st["verified"], 15, 0)
P.add("K03", "report.json agent_judgment.contract_verification.stats", "contradicted", st["contradicted"], 0, 0)
P.adds("K04", "report.json contract_verification.verdicts[*](status=STALE)", "STALE 项的指标", ",".join(sorted(v["metric"] for v in cv["verdicts"] if v["status"] == "STALE")), "CORE_PCE,US_REAL_GDP")
P.addb("K05", "report.json contract_verification.verdicts[*]", "STALE 两项数值直读一致(value==expected)", all(v["value"] == v["expected"] for v in cv["verdicts"] if v["status"] == "STALE"))
P.addb("K06", "report.json contract_verification", "n_contradictions=4", st.get("n_contradictions") == 4 and len(aj["l3"]["contradictions"]) == 4)
P.add("K07", "agent_judgment.json l3.mechanism_chains", "机制链条数", len(aj["l3"]["mechanism_chains"]), 2, 0)
P.add("K08", "agent_judgment.json l4.scenarios", "情景数", len(aj["l4"]["scenarios"]), 2, 0)
P.add("K09", "agent_judgment.json reader_map.transmission[*].links", "传导链条数/环数", len(aj["reader_map"]["transmission"]), 1, 0)
P.add("K10", "agent_judgment.json reader_map.transmission[0].links", "传导环数", len(aj["reader_map"]["transmission"][0]["links"]), 3, 0)
P.addb("K11", "agent_judgment.json reader_map.transmission[0].links[*].face_off_verdict", "三环裁定均为『尚不能区分』", all(l["face_off_verdict"] == "尚不能区分" for l in aj["reader_map"]["transmission"][0]["links"]))
P.adds("K12", "agent_judgment.json reader_map.transmission[0].links[*].distinguishing_metric", "区分指标", ",".join(l["distinguishing_metric"] for l in aj["reader_map"]["transmission"][0]["links"]), "TIPS_10Y,BEI_10Y,VIX")
P.addb("K13", "agent_judgment.json l3.contradictions[*].competing_explanations", "四条矛盾陈述各含 2 种并列解释且均带【假设】", all(len(c["competing_explanations"]) == 2 and all(x.startswith("【假设】") for x in c["competing_explanations"]) for c in aj["l3"]["contradictions"]))
P.addb("K14", "agent_judgment.json reader_map.history_periods", "历史类比取零段", len(aj["reader_map"]["history_periods"]) == 0)
P.add("K15", "agent_judgment.json reader_map.turnings", "转折数", len(aj["reader_map"]["turnings"]), 3, 0)
P.addb("K16", "agent_judgment.json reader_map.turnings[*]", "三转折为不同指标-月且跨两维度(通胀×2+政策×1)", len(set((t["metric_id"], t["date"]) for t in aj["reader_map"]["turnings"])) == 3 and set(t["metric_id"] for t in aj["reader_map"]["turnings"]) == {"JP_POLICY_RATE", "JP_CPI_TOKYO_YOY", "CORE_CPI"})
P.addb("K17", "agent_judgment.json l4.scenarios[*]", "两情景互斥(A 需 DFEDTARU≥4.25, B 需 ≤4)", "≥4.25" in aj["l4"]["scenarios"][0]["rows"]["trigger"]["condition"] and "≤4" in aj["l4"]["scenarios"][1]["rows"]["trigger"]["condition"])
P.save(outdir, "pts_d.json")
