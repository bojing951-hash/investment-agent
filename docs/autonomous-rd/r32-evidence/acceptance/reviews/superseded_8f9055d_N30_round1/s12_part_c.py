import datetime as dt
# ======================================================================
# part C -- supplementary facts recomputed from the read-only inputs.
# Record-only checks (SUP / NUM): reported in PROSE section 5, never counted in the 595.
# Every quoted engine / registry / calendar / snapshot sentence is located in its input, never retyped.
# ======================================================================
SUP = []


def sup(label, cond, detail=""):
    SUP.append((len(SUP) + 1, label, bool(cond), "" if cond else str(detail)[:400]))


def D(s):
    return dt.date.fromisoformat(str(s)[:10])


def days(a, b):
    return (D(b) - D(a)).days


def n(v):
    """number as the judgment writes it: at most two decimals, no trailing zeros"""
    s = "%.2f" % (v + 0.0)
    return s.rstrip("0").rstrip(".") if "." in s else s


def sg(v):
    """signed number for the narrative"""
    return ("+" if v > 0 else ("−" if v < 0 else "")) + n(abs(v))


def near(a, b, tol=0.0051):
    return abs(a - b) <= tol


def ser(mid):
    s = SS[mid]
    return {str(d)[:10]: v for d, v in zip(s["dates"], s["values"]) if v is not None}


def prevd(dct, d):
    ks = sorted(dct)
    return ks[ks.index(d) - 1]


def chg(dct, a, b):
    return round((dct[b] / dct[a] - 1.0) * 100.0, 2)


def mo(dct, y, m_):
    return round(dct["%04d-%02d-01" % (y, m_)], 6)


NUM = []


def eqn(label, got, exp):
    dec = len(str(exp).split(".")[1]) if "." in str(exp) else 0
    NUM.append((label, got, exp, round(got, dec) == exp))


EA, JPC, TK, JPR = ser("EA_HICP_YOY"), ser("JP_CPI_YOY"), ser("JP_CPI_TOKYO_YOY"), ser("JP_POLICY_RATE")
MRO, DFR, U10 = ser("ECB_MRO"), ser("ECB_DFR"), ser("UST_10Y")
EUR, JPY, DXY = ser("EURUSD"), ser("USDJPY"), ser("DXY")
SPX, NK, DAX, CAC, VIX = ser("SPX"), ser("NIKKEI225"), ser("DAX"), ser("CAC40"), ser("VIX")
GEA, GJP, FTL, FTU = ser("EA_REAL_GDP_YOY"), ser("JP_REAL_GDP_YOY"), ser("DFEDTARL"), ser("DFEDTARU")
VE = {i: mo(EA, 2026, i) for i in range(1, 11)}
VJ = {i: mo(JPC, 2026, i) for i in range(1, 11)}
CUTOFF = "2026-11-23"
W0, W1 = "2026-10-23", "2026-11-20"
FACTS = {f["fact_id"]: f for f in SNAP["facts"]}
GA = SNAP["gate_a"]
RP = R["research_plan"]
CELLS = {c["metric_id"]: c for c in RP["point_values"]["cells"]}
CON = J["l3"]["contradictions"]
LKS = J["l3"]["mechanism_chains"][0]["links"]
TRS = J["reader_map"]["transmission"][0]["links"]
TNS = J["reader_map"]["turnings"]
RGS = J["reader_map"]["regions"]
QGN = J["quality_gate_notes"]
SCE = J["l4"]["scenarios"]
HEAD = J["reader_map"]["headline_conclusion"]
REGM = {m.get("metric_id") or m.get("id"): m for m in (REG.get("metrics") if isinstance(REG, dict) else REG)}
REGTXT = json.dumps(REG, ensure_ascii=False)
RTXT = json.dumps(R, ensure_ascii=False)
SNAPTXT = json.dumps(SNAP, ensure_ascii=False)
ALLSTR = [v for _, v in LV if isinstance(v, str)]
JALL = "\n".join(ALLSTR)
CE = CALE["entries"]
JPT = [e for e in CE if e.get("entry_id") == "RC-JP-BOJ-TARGET-2026-09"][0]
JPM = [e for e in CE if e.get("entry_id") == "RC-JP-BOJ-MAINT-2026-10"][0]
TARGET = JPT["target_value"]
EJ = R["agent_judgment"]
CV = EJ["contract_verification"]
CVNV = [v for v in CV["verdicts"] if v.get("status") != "VERIFIED"]
CV_ST = Counter(v["status"] for v in CV["verdicts"] + CV["six_checks"] + CV["map_checks"])
DRI = {it.get("metric_id"): it for it in R["run"]["data_requirements"]["items"]}
STEPS = {s["step"]: s for s in R["steps"] if isinstance(s.get("envelope"), dict)}
S5 = STEPS["S5_compare"]["envelope"]["data"]
S6 = STEPS["S6_analog"]["envelope"]["data"]
EIDX_REFS = set(e["ref"] for e in EIDX)
MAPL, FULLL = MAP.split("\n"), FULL.split("\n")


def need(q, *texts):
    assert any(q in t for t in texts), ("quote not found in inputs", q[:60])
    return q


def line_of(lines, needle):
    return [i + 1 for i, l in enumerate(lines) if needle in l]


# ---- inflation readings (C1)
YEA = round(VE[10] - mo(EA, 2025, 10), 2)
YJP = round(mo(JPC, 2025, 10) - VJ[10], 2)
GAP10 = round(VE[10] - VJ[10], 2)
D04 = (round(VE[10] - VE[4], 2), round(VJ[10] - VJ[4], 2))
D06 = (round(VE[10] - VE[6], 2), round(VJ[10] - VJ[6], 2))
D05 = (round(VE[10] - VE[5], 2), round(VJ[10] - VJ[5], 2))
GAPS = [round(VE[i] - VJ[i], 2) for i in range(5, 11)]
SEPJ = round(VJ[9] - VE[9], 2)
SEPT = round(mo(TK, 2026, 9) - VE[9], 2)
JP_DIP = round(VJ[3] - VJ[4], 2)
for lab, got, exp in (("欧元区HICP 2026-10", VE[10], 4.0), ("欧元区HICP 2026-09", VE[9], 3.8), ("欧元区HICP 2026-08", VE[8], 3.2),
                      ("欧元区HICP 2026-07", VE[7], 2.9), ("欧元区HICP 2026-06", VE[6], 2.8), ("欧元区HICP 2026-05", VE[5], 3.2),
                      ("欧元区HICP 2026-04", VE[4], 3.0), ("欧元区HICP 2026-02", VE[2], 1.9), ("欧元区HICP 2026-01", VE[1], 1.7),
                      ("欧元区HICP 2025-10", mo(EA, 2025, 10), 2.1),
                      ("日本全国CPI 2026-10", VJ[10], 2.44), ("日本全国CPI 2026-09", VJ[9], 2.16), ("日本全国CPI 2026-08", VJ[8], 1.98),
                      ("日本全国CPI 2026-07", VJ[7], 1.97), ("日本全国CPI 2026-06", VJ[6], 1.67), ("日本全国CPI 2026-05", VJ[5], 1.53),
                      ("日本全国CPI 2026-04", VJ[4], 1.38), ("日本全国CPI 2026-03", VJ[3], 1.46), ("日本全国CPI 2026-02", VJ[2], 1.27),
                      ("日本全国CPI 2025-11", mo(JPC, 2025, 11), 2.9), ("日本全国CPI 2025-10", mo(JPC, 2025, 10), 2.99),
                      ("日本全国CPI 2025-09", mo(JPC, 2025, 9), 2.91), ("日本全国CPI 2025-01", mo(JPC, 2025, 1), 4.03),
                      ("东京都CPI 2026-10", mo(TK, 2026, 10), 2.73), ("东京都CPI 2026-09", mo(TK, 2026, 9), 2.69), ("东京都CPI 2026-08", mo(TK, 2026, 8), 1.9),
                      ("东京都CPI 2026-06", mo(TK, 2026, 6), 1.6), ("东京都CPI 2026-04", mo(TK, 2026, 4), 1.42),
                      ("最新水平差 欧元区−日本", GAP10, 1.56), ("同比对照 欧元区", YEA, 1.9), ("同比对照 日本(回落)", YJP, 0.55),
                      ("锚间变化 欧元区", D04[0], 1.0), ("锚间变化 日本", D04[1], 1.06), ("自2026-06 欧元区", D06[0], 1.2), ("自2026-06 日本", D06[1], 0.77),
                      ("自2026-05 欧元区", D05[0], 0.8), ("自2026-05 日本", D05[1], 0.91), ("窗内水平差最小", min(GAPS), 0.93), ("窗内水平差最大", max(GAPS), 1.67),
                      ("2026-09期 日本全国−欧元区", SEPJ, -1.64), ("2026-09期 东京−欧元区", SEPT, -1.11)):
    eqn(lab, got, exp)
def p1(v):
    s_ = n(v)
    return s_ + ".0" if "." not in s_ else s_


PATH_EA = "→".join("%s(%s)" % (p1(VE[i]), "2026-%02d" % i) for i in range(5, 11))
PATH_JP = "→".join("%s(%s)" % (p1(VJ[i]), "2026-%02d" % i) for i in range(5, 11))
sup("环1 文内两条月度路径串与序列面逐月值一致", "EA_HICP_YOY " + PATH_EA in LKS[0]["text"] and "JP_CPI_YOY " + PATH_JP in LKS[0]["text"], (PATH_EA, PATH_JP))
sup("日本 2026-05..2026-10 逐月上行;欧元区 2026-06 回落后非单调", all(VJ[i] < VJ[i + 1] for i in range(5, 10)) and VE[6] < VE[5])
sup("东京都序列自 2026-01 起、去年同月读数不在序列内", min(TK) == "2026-01-01" and "2025-10-01" not in TK and max(TK) == "2026-10-01")
sup("两条最新读数 L1 事实行 quality_status=WARN", all(FACTS[k]["quality_status"] == "WARN" for k in ("JP_CPI_YOY@2026-10-01", "EA_HICP_YOY@2026-10-01")))
sup("推定发布日: 欧元区 2026-11-16、日本 2026-11-20(相隔 4 天),规则=月末+16/月末+20",
    CELLS["EA_HICP_YOY"]["anchors"]["最新一期"]["publication_date"] == "2026-11-16" and CELLS["JP_CPI_YOY"]["anchors"]["最新一期"]["publication_date"] == "2026-11-20"
    and days("2026-11-16", "2026-11-20") == 4 and "月末+16天" in CELLS["EA_HICP_YOY"]["anchors"]["最新一期"]["publication_rule"]
    and "月末+20天" in CELLS["JP_CPI_YOY"]["anchors"]["最新一期"]["publication_rule"])

# ---- policy faces (C2 / C3)
STEPS_JP = [("2026-06", mo(JPR, 2026, 5), mo(JPR, 2026, 6)), ("2026-07", mo(JPR, 2026, 6), mo(JPR, 2026, 7)),
            ("2026-09", mo(JPR, 2026, 8), mo(JPR, 2026, 9)), ("2026-10", mo(JPR, 2026, 9), mo(JPR, 2026, 10))]
STEP_BP = [round((b - a) * 100, 1) for _, a, b in STEPS_JP]
SUM_BP = round(sum(STEP_BP), 1)
ANCH_BP = round((mo(JPR, 2026, 10) - mo(JPR, 2026, 4)) * 100, 1)
Y12_BP = round((mo(JPR, 2026, 10) - mo(JPR, 2025, 11)) * 100, 1)
LAST_MRO, LAST_DFR, LAST_JPR = max(MRO), max(DFR), max(JPR)
NONWED = sorted(set(d for d in list(MRO) + list(DFR) if D(d).weekday() != 2))
NONWED_YEARS = sorted(set(d[:4] for d in NONWED))
NONWED_2015 = [d for d in NONWED if d >= "2015-01-01"]
WIN_OBS = ["2025-06-11", "2026-06-17", "2026-09-16"]
DD = dict(d68=days("2026-09-16", CUTOFF), d371=days("2025-06-11", "2026-06-17"), d91=days("2026-06-17", "2026-09-16"),
          d8a=days("2026-09-16", JPT["effective_on"]), d8b=days("2026-09-10", JPT["decision_date"]), d24=days(JPM["decision_date"], CUTOFF),
          d14=days(JPM["decision_date"], "2026-11-13"), d58=days("2026-09-16", "2026-11-13"), d21=days(JPM["decision_date"], W1), d65=days("2026-09-16", W1),
          d6a=days("2026-06-11", "2026-06-17"), d6b=days(JPT["decision_date"], JPT["effective_on"]))
for lab, got, exp in (("MRO 2025-06-11", MRO["2025-06-11"], 2.15), ("MRO 2026-06-17", MRO["2026-06-17"], 2.4), ("MRO 2026-09-16", MRO["2026-09-16"], 2.65),
                      ("DFR 2025-06-11", DFR["2025-06-11"], 2.0), ("DFR 2026-06-17", DFR["2026-06-17"], 2.25), ("DFR 2026-09-16", DFR["2026-09-16"], 2.5),
                      ("月均 2026-04", mo(JPR, 2026, 4), 0.727), ("月均 2026-05", mo(JPR, 2026, 5), 0.727), ("月均 2026-06", mo(JPR, 2026, 6), 0.841),
                      ("月均 2026-07", mo(JPR, 2026, 7), 0.978), ("月均 2026-08", mo(JPR, 2026, 8), 0.977), ("月均 2026-09", mo(JPR, 2026, 9), 1.043),
                      ("月均 2026-10", mo(JPR, 2026, 10), 1.227), ("月均 2025-11", mo(JPR, 2025, 11), 0.478),
                      ("台阶1 bp", STEP_BP[0], 11.4), ("台阶2 bp", STEP_BP[1], 13.7), ("台阶3 bp", STEP_BP[2], 6.6), ("台阶4 bp", STEP_BP[3], 18.4),
                      ("四台阶之和 bp", SUM_BP, 50.1), ("锚间净 bp", ANCH_BP, 50.0), ("近12个月月均净 bp", Y12_BP, 74.9),
                      ("距截止天数", DD["d68"], 68), ("持平天数", DD["d371"], 371), ("两次变更间隔", DD["d91"], 91), ("生效日间隔", DD["d8a"], 8),
                      ("回推决议日间隔", DD["d8b"], 8), ("维持决议距截止", DD["d24"], 24), ("跳升起点距维持决议", DD["d14"], 14), ("跳升起点距欧央行生效", DD["d58"], 58),
                      ("跳升终点距维持决议", DD["d21"], 21), ("跳升终点距欧央行生效", DD["d65"], 65), ("决议→生效 欧央行", DD["d6a"], 6), ("决议→生效 日央行", DD["d6b"], 6),
                      ("水平差 MRO−目标", round(MRO[LAST_MRO] - TARGET, 2), 1.4), ("水平差 DFR−目标", round(DFR[LAST_DFR] - TARGET, 2), 1.25),
                      ("欧元区GDP 2026-07", mo(GEA, 2026, 7), 1.28), ("日本GDP 2026-07", mo(GJP, 2026, 7), 1.16)):
    eqn(lab, got, exp)
sup("ECB 两序列与日本月均序列末观测日", (LAST_MRO, LAST_DFR, LAST_JPR) == ("2026-09-16", "2026-09-16", "2026-10-01"), (LAST_MRO, LAST_DFR, LAST_JPR))
sup("欧央行序列非周三观测日: 全史 %d 个(年份 %s),2015 年以来 %d 个;本窗三个观测日全为周三" % (
    len(NONWED), "/".join(NONWED_YEARS), len(NONWED_2015)),
    len(NONWED_2015) == 0 and all(d in MRO and D(d).weekday() == 2 for d in WIN_OBS), NONWED)
sup("ECB 两事实行 quality_status=DEGRADED;注册表 freshness=10 天且 decision_dated=true;点值格最新一期 status=ok/policy_confirmation",
    all(FACTS[k]["quality_status"] == "DEGRADED" for k in ("ECB_MRO@2026-09-16", "ECB_DFR@2026-09-16"))
    and all(REGM[c]["freshness"]["max_calendar_lag_days"] == 10 and REGM[c]["freshness"].get("decision_dated") is True for c in ("ECB_MRO", "ECB_DFR"))
    and all(CELLS[c]["anchors"]["最新一期"]["status"] == "ok" and CELLS[c]["anchors"]["最新一期"].get("freshness_basis") == "policy_confirmation" for c in ("ECB_MRO", "ECB_DFR")))
sup("交付门: ECB_MRO/ECB_DFR 记 insufficient_coverage(日频族规格)", all(
    (DRI[c].get("outcome"), DRI[c]["spec"].get("frequency"), DRI[c]["spec"]["window"].get("n_in_window"), DRI[c]["spec"]["window"].get("expected_in_window"),
     DRI[c]["spec"]["window"].get("n_floor_in_window"), DRI[c]["spec"]["window"].get("max_adjacent_gap_days"), DRI[c]["spec"]["window"].get("max_gap_limit_days"))
    == ("insufficient_coverage", "daily", 2, 131, 66, 91, 30) for c in ("ECB_MRO", "ECB_DFR")))
sup("Gate A: DEGRADED;noncore_missing 含 JP_CPI_TOKYO_YOY/BUND_10Y/BUND_2Y/EA_REAL_GDP_YOY/JP_REAL_GDP_YOY;noncore_degraded 含 ECB_MRO/ECB_DFR",
    GA["status"] == "DEGRADED" and all(k in GA["noncore_missing"] for k in ("JP_CPI_TOKYO_YOY", "BUND_10Y", "BUND_2Y", "EA_REAL_GDP_YOY", "JP_REAL_GDP_YOY"))
    and all(k in GA["noncore_degraded"] for k in ("ECB_MRO", "ECB_DFR")))
sup("注册表 JP/EA 面无 JP_POLICY_TARGET、无两地核心通胀序列;series_store 无 JGB/BUND;日债三期限事实行在场",
    "JP_POLICY_TARGET" not in REGM and not [k for k in REGM if REGM[k].get("economy") in ("JP", "EA") and re.search(r"CORE|HICX", k)]
    and not [k for k in SS if re.search(r"JGB|BUND", k)] and all(FACTS[k]["observation_date"] == "2026-11-19" for k in ("JGB2Y@2026-11-19", "JGB5Y@2026-11-19", "JGB10Y@2026-11-19")))
JGBV = [(FACTS[k]["value"], FACTS[k]["quality_status"]) for k in ("JGB2Y@2026-11-19", "JGB5Y@2026-11-19", "JGB10Y@2026-11-19")]
sup("证据索引 60 行,无 JGB/BUND 引用", len(EIDX) == 60 and not [r for r in EIDX_REFS if r.startswith(("JGB", "BUND"))])
CAL_CNT = Counter(str(e.get("metric_id")) for e in CE)
CAL_JPEA = [e for e in CE if e.get("metric_id") in ("JP_POLICY_TARGET", "EA_HICP_YOY")]
sup("冻结日历 18 条: JP_POLICY_TARGET×2、EA_HICP_YOY×3,其余 13 条非日欧面;无 ECB 条目",
    len(CE) == 18 and CAL_CNT["JP_POLICY_TARGET"] == 2 and CAL_CNT["EA_HICP_YOY"] == 3 and len(CE) - len(CAL_JPEA) == 13
    and not [e for e in CE if "ECB" in (str(e.get("metric_id")) + str(e.get("entry_id"))).upper()])
sup("日历两条日本实录字段", (JPT["decision_date"], JPT["effective_on"], JPT["target_value"], JPT["kind"], JPT["basis"]) == ("2026-09-18", "2026-09-24", 1.25, "policy_decision", "user_directive")
    and (JPM["decision_date"], JPM["kind"], JPM["target_value"], "effective_on" in JPM) == ("2026-10-30", "policy_maintenance", 1.25, False))
EA_CAL = sorted(e["obs_from"][:7] for e in CE if e.get("metric_id") == "EA_HICP_YOY")
sup("日历 EA HICP 实录观测月 2021-05/2022-06/2025-03(不覆盖本窗)", EA_CAL == ["2021-05", "2022-06", "2025-03"], EA_CAL)

# ---- FX, assets, rates (mechanism links 3-4)
EJ_ = lambda d: EUR[d] * JPY[d]
for lab, got, exp in (("EURUSD 10-23", EUR[W0], 1.1221), ("EURUSD 11-20", EUR[W1], 1.0970), ("EURUSD 11-23", EUR[CUTOFF], 1.0940),
                      ("USDJPY 10-23", JPY[W0], 156.494), ("USDJPY 11-20", JPY[W1], 159.707), ("USDJPY 11-23", JPY[CUTOFF], 159.347),
                      ("DXY 10-23", DXY[W0], 101.81), ("DXY 11-20", DXY[W1], 103.81), ("DXY 11-23", DXY[CUTOFF], 104.079),
                      ("EURUSD 至11-20 %", chg(EUR, W0, W1), -2.24), ("EURUSD 至11-23 %", chg(EUR, W0, CUTOFF), -2.51),
                      ("USDJPY 至11-20 %", chg(JPY, W0, W1), 2.05), ("USDJPY 至11-23 %", chg(JPY, W0, CUTOFF), 1.82),
                      ("DXY 至11-20 %", chg(DXY, W0, W1), 1.96), ("DXY 至11-23 %", chg(DXY, W0, CUTOFF), 2.23),
                      ("EURJPY 合成 10-23", EJ_(W0), 175.61), ("EURJPY 合成 11-20", EJ_(W1), 175.19), ("EURJPY 合成 11-23", EJ_(CUTOFF), 174.32),
                      ("EURJPY 合成 至11-20 %", chg({"a": EJ_(W0), "b": EJ_(W1)}, "a", "b"), -0.24), ("EURJPY 合成 至11-23 %", chg({"a": EJ_(W0), "b": EJ_(CUTOFF)}, "a", "b"), -0.73),
                      ("UST_10Y 末值", U10[max(U10)], 5.04), ("联邦基金目标下限", FTL[CUTOFF], 3.75), ("联邦基金目标上限", FTU[CUTOFF], 4.0),
                      ("SPX 同日收盘 %", chg(SPX, W0, W1), -9.36), ("NIKKEI225 同日收盘 %", chg(NK, W0, W1), -9.98), ("DAX 同日收盘 %", chg(DAX, W0, W1), -1.50), ("CAC40 同日收盘 %", chg(CAC, W0, W1), 1.86),
                      ("跳升窗 SPX %", chg(SPX, "2026-11-13", W1), -8.61), ("跳升窗 NIKKEI225 %", chg(NK, "2026-11-13", W1), -7.70),
                      ("跳升窗 DAX %", chg(DAX, "2026-11-13", W1), -7.28), ("跳升窗 CAC40 %", chg(CAC, "2026-11-13", W1), -5.27),
                      ("SPX 11-05 日变动 %", chg(SPX, prevd(SPX, "2026-11-05"), "2026-11-05"), -4.36), ("NIKKEI225 11-06 日变动 %", chg(NK, prevd(NK, "2026-11-06"), "2026-11-06"), -5.96),
                      ("VIX 10-23", VIX[W0], 19.45), ("VIX 11-13", VIX["2026-11-13"], 19.30), ("VIX 11-16", VIX["2026-11-16"], 22.91), ("VIX 11-17", VIX["2026-11-17"], 25.46),
                      ("VIX 11-18", VIX["2026-11-18"], 24.56), ("VIX 11-19", VIX["2026-11-19"], 28.44), ("VIX 11-20", VIX[W1], 35.89), ("VIX 11-23", VIX[CUTOFF], 27.01),
                      ("VIX 至11-20 %", chg(VIX, W0, W1), 84.5), ("VIX 11-23 较 11-20 %", chg(VIX, W1, CUTOFF), -24.7), ("VIX 至11-23 %", chg(VIX, W0, CUTOFF), 38.87),
                      ("VIX 11-04", VIX["2026-11-04"], 16.61), ("VIX 11-05", VIX["2026-11-05"], 28.18), ("VIX 11-11", VIX["2026-11-11"], 17.49),
                      ("VIX 11-05 日变动 %", chg(VIX, "2026-11-04", "2026-11-05"), 69.66), ("VIX 11-11 较 11-05 %", chg(VIX, "2026-11-05", "2026-11-11"), -37.93),
                      ("VIX 11-16 日变动 %", chg(VIX, prevd(VIX, "2026-11-16"), "2026-11-16"), 18.70), ("VIX 11-20 日变动 %", chg(VIX, prevd(VIX, "2026-11-20"), "2026-11-20"), 26.20),
                      ("引擎回贴 SPX %", chg(SPX, W0, CUTOFF), -5.51), ("引擎回贴 DAX %", chg(DAX, W0, CUTOFF), 0.11),
                      ("引擎回贴 SPX 值", SPX[CUTOFF], 7203.85), ("引擎回贴 DAX 值", DAX[CUTOFF], 25209.45), ("NIKKEI225 11-20 值", NK[W1], 56436.65),
                      ("C2 USDJPY 水平", JPY[CUTOFF], 159.35), ("C2 SPX 水平", SPX[CUTOFF], 7203.85), ("C2 VIX 水平", VIX[CUTOFF], 27.01)):
    eqn(lab, got, exp)
VDPCT = {d: chg(VIX, prevd(VIX, d), d) for d in sorted(VIX) if W0 < d <= W1 and prevd(VIX, d) >= W0}
TOP_MONTH = sorted(VDPCT, key=lambda d: -VDPCT[d])[:3]
TOP_JUMP = sorted((d for d in VDPCT if d > "2026-11-13"), key=lambda d: -VDPCT[d])[:2]
N_TD = len([d for d in sorted(VIX) if "2026-11-05" < d <= "2026-11-11"])
FXD = max(abs(chg(EUR, prevd(EUR, d), d)) for d in ("2026-11-16", "2026-11-20")) , max(abs(chg(JPY, prevd(JPY, d), d)) for d in ("2026-11-16", "2026-11-20"))
sup("VIX 月窗内最大单日跳升前三 = 11-05/11-20/11-16;跳升窗(11-13→11-20)内前二 = 11-20/11-16",
    TOP_MONTH == ["2026-11-05", "2026-11-20", "2026-11-16"] and sorted(TOP_JUMP) == ["2026-11-16", "2026-11-20"], (TOP_MONTH, TOP_JUMP))
sup("先例: 11-05→11-11 四个交易日", N_TD == 4, N_TD)
sup("两日(11-16、11-20)欧元、日元对美元单日变动幅度均不超过 0.23%", max(FXD) <= 0.23 + 1e-9, FXD)
FTL_KS = sorted(FTL)
FTL_CH = [(a, b) for a, b in zip(FTL_KS, FTL_KS[1:]) if FTL[a] != FTL[b]]
sup("美联储序列(DFEDTARL,日历日逐日)最近变动 " + FTL_CH[-1][0] + "→" + FTL_CH[-1][1] + "(" + n(FTL[FTL_CH[-1][0]]) + "→" + n(FTL[FTL_CH[-1][1]]) + ",其后至截止日无变动;此前一次变动 " + FTL_CH[-2][0] + "→" + FTL_CH[-2][1] + ")",
    FTL_CH[-1] == ("2026-09-16", "2026-09-17") and FTL_CH[-2] == ("2025-12-10", "2025-12-11") and FTL["2026-09-16"] == 3.5 and FTL["2026-09-17"] == 3.75 and max(FTL) == CUTOFF and len(FTL_CH) > 2,
    (FTL_CH[-2:], FTL["2026-09-16"], FTL["2026-09-17"]))
sup("UST_10Y 末观测日 2026-11-19;SPX/DAX/VIX 截止日值 7203.85/25209.45/27.01;FOMC 纪要 2026-11-18",
    max(U10) == "2026-11-19" and len(RP["policy_doc_facts"]) == 1 and RP["policy_doc_facts"][0]["published_on"] == "2026-11-18" and RP["policy_doc_facts"][0]["doc_id"] == "FOMC-MINUTES-2026-10")
URT = RP["us_rates_trio"]
sup("美国三利率分解: 名义 Δ-8bp = 实际 Δ+11bp + 盈亏平衡 Δ-19bp,残差 0",
    (URT["chg_bp"]["UST_10Y"], URT["chg_bp"]["TIPS_10Y"], URT["chg_bp"]["BEI_10Y"], URT["identity_residual_bp"]) == (-8.0, 11.0, -19.0, 0.0)
    and round(URT["chg_bp"]["TIPS_10Y"] + URT["chg_bp"]["BEI_10Y"], 6) == URT["chg_bp"]["UST_10Y"] and (URT["window"]["from"], URT["window"]["to"]) == ("2026-10-20", "2026-11-19"))
sup("判断档 rates_decomposition 与引擎面同值", (J["reader_map"]["rates_decomposition"]["nominal_bp"], J["reader_map"]["rates_decomposition"]["real_bp"], J["reader_map"]["rates_decomposition"]["bei_bp"]) == (-8.0, 11.0, -19.0))
sup("判断档 asset_returns_echo 与引擎 asset_moves 同值", sorted((a["metric_id"], a["chg_pct"], a["window"]["from"], a["window"]["to"]) for a in J["reader_map"]["asset_returns_echo"])
    == sorted((a["metric_id"], a["chg_pct"], a["window"]["from"], a["window"]["to"]) for a in RP["asset_moves"]["rows"] if a["metric_id"] in ("SPX", "DAX", "NIKKEI225", "VIX")))

# ---- scenarios, analog, sync face
S1R, S2R = SCE[0]["rows"], SCE[1]["rows"]
PUB_OFF = {"EA_HICP_YOY": 16, "JP_CPI_YOY": 20}
ENTRY = {m_: (dt.date(2026, 12, 31) + dt.timedelta(days=o)).isoformat() for m_, o in PUB_OFF.items()}
sup("读数入档日(引擎规则 月末+16/+20)早于情景时限 2027-02-15;两情景 deadline 同值",
    all(v < "2027-02-15" for v in ENTRY.values()) and S1R["trigger"]["deadline"] == S2R["trigger"]["deadline"] == "2027-02-15", ENTRY)
sup("证伪/触发指标与敏感变量均在册", all(m_ in SS for m_ in (S1R["falsification"]["metric_id"], S2R["falsification"]["metric_id"], "VIX") + tuple(S1R["falsification"]["secondary_metric_ids"] + S2R["falsification"]["secondary_metric_ids"] + S1R["sensitive_variables"] + S2R["sensitive_variables"])))
sup("情景阈值文字在场", "3.5%" in S1R["falsification"]["threshold"] and "2.0%" in S1R["falsification"]["threshold"] and "1.5 个百分点" in S1R["falsification"]["threshold"]
    and "≥4.0%" in S1R["trigger"]["condition"] and "高于 30" in S1R["trigger"]["condition"] and "3.0%" in S2R["falsification"]["threshold"]
    and "低于 3.0%" in S2R["trigger"]["condition"] and "低于 25" in S2R["trigger"]["condition"])
sup("证伪条件不含 VIX;VIX 25–30 区间两情景均不触发", "VIX" not in S1R["falsification"]["threshold"] and "VIX" not in S2R["falsification"]["threshold"])
sup("截止日读数与 S1 前提相容、与 S2 前提相反", VE[10] >= 3.5 and VJ[10] >= 2.0 and GAP10 >= 1.5 and not (VE[10] < 3.0 and VJ[10] < 2.0))
sup("analog 面: 扫描 1871、有效 74、TOP1 2025-03 距离 0.727212;判断档引用三数一致",
    (S6["candidates"]["scanned"], S6["candidates"]["valid"], S6["top"][0]["candidate_month"]) == (1871, 74, "2025-03") and round(S6["top"][0]["distance"], 3) == 0.727
    and all(x in J["reader_map"]["history_zero_case_note"] for x in ("1871", "74", "2025-03", "0.727")))
sup("历史类比 0 段;全文无跨地区同步/相关系数主张", J["reader_map"]["history_periods"] == [] and all(JALL.count(w) == 0 for w in ("相关系数", "同步系数", "pearson", "皮尔逊")))
sup("引擎同步面 S5_compare 两侧 = EA_HICP_YOY × ECB_MRO(月格对齐,n_change_pairs=%d,变化基=pp)" % S5["alignment"]["n_change_pairs"],
    [s["metric_id"] for s in S5["sides"]] == ["EA_HICP_YOY", "ECB_MRO"] and S5["alignment"]["mode"] == "month_grid" and S5["change_basis"] == {"a": "pp", "b": "pp"})

# ---- time point, wording, rendering fidelity
LATE = sorted(set(re.findall(r"20\d\d-\d\d-\d\d", "\n".join(v for p_, v in LV if isinstance(v, str) and p_[0] != "agent_declaration"))))
LATE = [t for t in LATE if t > CUTOFF]
sup("判断档晚于截止日的日期记号仅请求月末 2026-11-30 与情景时限 2027-02-15", LATE == ["2026-11-30", "2027-02-15"], LATE)
sup("全文「无变化」0 次;「维持不变」仅日历维持条目语境;「STALE」0 次;「全为周三」0 次",
    JALL.count("无变化") == 0 and JALL.count("维持不变") == 3 and JALL.count("STALE") == 0 and JALL.count("全为周三") == 0)
N_OCC, BAD_OCC = 0, []
for _s in ALLSTR:
    for _d in ("2026-06-11", "2026-09-10"):
        for _m in re.finditer(re.escape(_d), _s):
            N_OCC += 1
            _a = max(_s.rfind("。", 0, _m.start()), _s.rfind(";", 0, _m.start())) + 1
            _b = min([x for x in (_s.find("。", _m.end()), _s.find(";", _m.end()), len(_s)) if x >= 0])
            if not any(k in _s[_a:_b] for k in ("回推", "惯例", "推断")):
                BAD_OCC.append((_s[_a:_b][:80]))
sup("两处引擎回推决议日在全文 %d 处出现,所在句均带 回推/惯例/推断 标注" % N_OCC, N_OCC > 0 and not BAD_OCC, BAD_OCC)
norm = lambda s: "".join(s.split())
MAPN, FULLN = norm(MAP), norm(FULL)
LVS = [(p, v) for p, v in LV if isinstance(v, str) and len(v) >= 12 and not v.startswith("2026-")]
N_LV = len(LVS)
MAP_FOUND = sum(1 for _, v in LVS if norm(v) in MAPN)
FULL_FOUND = sum(1 for _, v in LVS if norm(v) in FULLN)


def unrendered(path):
    v = getp(J, path)
    return isinstance(v, str) and norm(v) not in MAPN and norm(v) not in FULLN


UNR_VN = [i for i in range(3) if unrendered(["reader_map", "transmission", 0, "links", i, "verdict_note"])]
UNR_NAR = [i for i in range(3) if unrendered(["reader_map", "turnings", i, "narrative"])]
UNR_QGN = [i for i in range(len(QGN)) if unrendered(["quality_gate_notes", i])]
UNR_AD = [k for k in J["agent_declaration"] if len(str(J["agent_declaration"][k])) >= 12 and not str(J["agent_declaration"][k]).startswith("2026-") and unrendered(["agent_declaration", k])]
REN_M = {k: all(norm(getp(J, ["reader_map", "transmission", 0, "links", i, k])) in MAPN for i in range(3))
         for k in ("observed_fact", "causal_hypothesis", "competing_explanation", "main_predicts", "competing_predicts", "face_off_verdict", "verdict_note")}
REN_F = {k: all(norm(getp(J, ["reader_map", "transmission", 0, "links", i, k])) in FULLN for i in range(3))
         for k in ("observed_fact", "causal_hypothesis", "competing_explanation", "main_predicts", "competing_predicts", "face_off_verdict", "verdict_note")}
sup("渲染忠实度: 判断档字符串叶(len≥12)%d 个,MAP 逐字命中 %d、FULL 命中 %d;verdict_note×3/turnings narrative×3/quality_gate_notes×6/declaration×%d 两报告均未渲染" % (
    N_LV, MAP_FOUND, FULL_FOUND, len(UNR_AD)), len(UNR_VN) == 3 and len(UNR_NAR) == 3 and len(UNR_QGN) == 6 and len(UNR_AD) == 4, (UNR_VN, UNR_NAR, UNR_QGN, UNR_AD))
sup("传导三环的 causal_hypothesis / competing_explanation / main_predicts / competing_predicts / face_off_verdict 在 MAP 逐字渲染",
    all(REN_M[k] for k in REN_M if k != "verdict_note") and not REN_M["verdict_note"], REN_M)
RA = SNAP["research_as_of"]
sup("研究截止=快照 research_as_of=%s(与窗端同值);截止日值标注为盘中快照" % RA, RA == "2026-11-23T22:53:47+08:00" and RA in JALL and "盘中快照、非收盘价" in JALL)
_T0 = dt.datetime.strptime(RA, "%Y-%m-%dT%H:%M:%S%z")
TZS = {c: _T0.astimezone(dt.timezone(dt.timedelta(hours=o))).strftime("%H:%M") for c, o in (("纽约", -5), ("柏林", 1), ("东京", 9), ("上海", 8))}
sup("时区换算 纽约/柏林/东京/上海 = %s" % "/".join(TZS[c] for c in ("纽约", "柏林", "东京", "上海")),
    TZS == {"纽约": "09:53", "柏林": "15:53", "东京": "23:53", "上海": "22:53"} and all(v in QGN[4] for v in ("纽约 09:53", "柏林 15:53", "东京 23:53", "上海 22:53")), TZS)

# ---- contract verification / attach block (report.json)
WR = dt.datetime.strptime(J["agent_declaration"]["written_at"], "%Y-%m-%dT%H:%M:%S%z")
ATT = dt.datetime.strptime(EJ["attached_at"], "%Y%m%dT%H%M%SZ").replace(tzinfo=dt.timezone.utc)
EMB_NULL = [k for k in ("agent_declaration", "l3", "l4", "reader_map", "quality_gate_notes") if EJ.get(k) is None]
CV_TOK_OK = all(v["token"] in CON[1]["statement"] for v in CV["verdicts"]) and (
    round(FACTS["ECB_DFR@2026-09-16"]["value"], 2), round(JPR["2026-10-01"], 3), round(JPY[CUTOFF], 2), round(SPX[CUTOFF], 2), round(VIX[CUTOFF], 2)) == tuple(v["value"] for v in CV["verdicts"])
MC = CV["map_checks"]
sup("契约验证数值串 %d 个均在受审 C2 陈述内且值与序列/事实面一致" % len(CV["verdicts"]), CV_TOK_OK)
sup("契约 map_checks 与受审文件一致(日期次序主张、传导链 id、转折指标来源)",
    "2026-09-29 晚于 BOJ 决议日 2026-09-18" in TNS[2]["follow_or_diverge"] and J["reader_map"]["transmission"][0]["chain_id"] == "CH-INFL-POLICY-RISKOFF"
    and all(t["metric_id"] in [c["metric_id"] for c in RP["turning_candidates"]["candidates"]] for t in TNS) and all(m["status"] == "VERIFIED" for m in MC))
sup("挂接校验块计数与受审文件一致(3 条矛盾陈述/1 条机制链/2 个情景)",
    EJ["validation"]["passed"] is True and (EJ["validation"]["n_contradictions"], EJ["validation"]["n_mechanism_chains"], EJ["validation"]["n_scenarios"]) == (len(CON), len(J["l3"]["mechanism_chains"]), len(SCE)))
sup("report.json 内嵌 agent_judgment 的正文五键均为 null(仅挂接元数据)", EMB_NULL == ["agent_declaration", "l3", "l4", "reader_map", "quality_gate_notes"], EMB_NULL)
sup("挂接时刻晚于判断档书写时刻(attached_at=%s,written_at=%s)" % (EJ["attached_at"], WR.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")), ATT > WR)
sup("run.git_head 与 MAP 印章同值", R["run"]["git_head"] == GIT_HEAD and GIT_HEAD in MAP)

# ---- reader-report lines quoted in the engine observations
L_HEAD, L_COV, L_WED, L_BP, L_FOH, L_KOU, L_PEAR, L_FULLHEAD = (line_of(MAPL, "## 四地三时点环境对照"), line_of(MAPL, "4/4组ok"),
    line_of(MAPL, "ECB_MRO/ECB_DFR 观测日全为周三"), line_of(MAPL, "Δ+20bp"), line_of(MAPL, "| 区分指标 | 主解释预期 | 竞争解释预期 | 已有观测 | 判断 |"),
    line_of(MAPL, "⚠未核验=无更晚已证实决议"), line_of(FULLL, "pearson = 0.264"), line_of(FULLL, "# 完整研究报告"))
L_TK = line_of(MAPL, CELLS["JP_CPI_TOKYO_YOY"]["anchors"]["最新一期"]["publication_rule"])
L_GAP = line_of(MAPL, "JP_POLICY_TARGET 不在注册表")
L_6M = [i + 1 for i, l in enumerate(MAPL) if "| 6个月前 |" in l and "——2026-09 决议 09-10、生效 09-16" in l and "2025-06-05" in l]
L_TKROW = [i + 1 for i, l in enumerate(MAPL) if "东京都" in l and l.startswith("| JP") and "| ok |" in l]

# ---- engine sources (optional; text-searched only, never imported or executed)
SRC = {os.path.basename(p): rd(p) for p in ENGINE_SRC}
ENG_ON = len(SRC) == 4
JCS, TCS, MPS, EGS = (SRC.get(k, "") for k in ("judgment_contract.py", "text_consistency.py", "research_map_planner.py", "evidence_gate.py"))
NOAL = ("JP_CPI_YOY", "EA_HICP_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_TARGET", "ECB_MRO")
_b = MPS.find("def _hist_region_reading(")
_body = MPS[_b:MPS.find("\ndef ", _b + 1)] if _b >= 0 else ""
ENG_CHK = {
    "E8 契约锚标签硬编码": "def _map_checks(" in JCS and "for _lbl in ('12个月前', '3个月前', '最新一期'):" in JCS,
    "E8 别名表未覆盖五指标": "ALIASES = {" in TCS and all(TCS.count(m_) == 0 for m_ in NOAL),
    "E11 历史截止视图两入口": all(k in MPS for k in ("def _hist_series(", "def _hist_region_reading(", "def _aof_first_pub(")) and "_aof_first_pub(" in _body,
    "E11 可见性入口": "def is_historical_view(" in EGS and "def visible_publish(" in EGS,
}

# ---- verbatim quotes used in the narrative
Q_SNAP_ISSUE = FACTS["ECB_MRO@2026-09-16"]["issues"][0]["message"]
Q_GATE_NOTE = GA["note"]
Q_DET_TOKYO, Q_DET_BUND, Q_DET_GDP = GA["noncore_missing_detail"]["JP_CPI_TOKYO_YOY"], GA["noncore_missing_detail"]["BUND_10Y"], GA["noncore_missing_detail"]["EA_REAL_GDP_YOY"]
Q_REG_JPCALC = need("各自基期内做严格同月同比后拼接", REGM["JP_CPI_YOY"]["calc"])
Q_REG_JPCALC2 = need("与官方公布值抽验一致(2026-09=2.16 vs 官方2.1)", REGM["JP_CPI_YOY"]["calc"])
Q_REG_JPCOV = need("覆盖2021-01..2026-09", REGM["JP_CPI_YOY"]["calc"])
Q_REG_TKCALC = need("基期内同月同比仅2026-01..2026-10 十个月", REGM["JP_CPI_TOKYO_YOY"]["calc"])
Q_REG_TKREL = need("每月下旬发布当月东京都区部", REGM["JP_CPI_TOKYO_YOY"]["release_semantics"])
Q_REG_ECBREL = need("决议公布后生效并当日更新系列", REGM["ECB_MRO"]["release_semantics"])
Q_REG_ECBCALC = need("管委会决议变更即时生效", REGM["ECB_MRO"]["calc"])
Q_REG_DDN = need("无更晚已证实决议不作过期", REGM["ECB_MRO"]["freshness"]["decision_dated_note"])
Q_ENG_DECNOTE = CELLS["ECB_MRO"]["anchors"]["6个月前"]["policy_dates"]["decision_note"]
Q_ENG_PUBRULE = need(CELLS["ECB_MRO"]["anchors"]["最新一期"]["publication_rule"], RTXT)
Q_MAP_TOKYO = need(CELLS["JP_CPI_TOKYO_YOY"]["anchors"]["最新一期"]["publication_rule"], MAP)
Q_ENG_STALE = CVNV[0]["note"]
Q_ENG_FACE = CELLS["ECB_MRO"]["policy_face"]["face"]
Q_VINT_RET = CELLS["EA_HICP_YOY"]["anchors"]["最新一期"]["vintage"]
Q_VINT_COL = CELLS["JP_CPI_TOKYO_YOY"]["anchors"]["最新一期"]["vintage"]
Q_MAP_WED = need("ECB_MRO/ECB_DFR 观测日全为周三", MAP)
Q_MAP_HEAD = need("## 四地三时点环境对照", MAP)
Q_MAP_COV = [l for l in MAPL if "4/4组ok" in l][0].strip()
Q_MAP_BP = [l for l in MAPL if "Δ+20bp" in l][0].strip()
Q_MAP_KOU = [l for l in MAPL if "⚠未核验" in l][0].strip()
Q_FULL_PEAR = [l for l in FULLL if "pearson = 0.264" in l][0].strip()
for _q in (Q_SNAP_ISSUE, Q_GATE_NOTE, Q_DET_TOKYO, Q_DET_BUND, Q_DET_GDP, Q_ENG_DECNOTE, Q_ENG_STALE, Q_ENG_FACE, Q_VINT_RET, Q_VINT_COL):
    need(_q, RTXT, SNAPTXT)

# ======================================================================
# issue list (original sentences are cut verbatim out of the judgment; never retyped)
# ======================================================================
ITEMS = []


def cut(path, start, end=None, keep_end=False):
    txt = getp(J, path)
    assert isinstance(txt, str), path
    assert txt.count(start) == 1, ("cut start not unique", path, start, txt.count(start))
    i = txt.index(start) + len(start)
    if end is None:
        return start
    j = txt.find(end, i)
    assert j >= 0, ("cut end not found", path, end)
    return start + txt[i:(j + len(end) if keep_end else j)]


def item(sev, where, note, path=None, start=None, end=None, keep_end=False, fix=""):
    original = cut(path, start, end, keep_end) if path is not None else ""
    assert original and any(original in c for c in CORPUS), (sev, where, original[:60])
    ITEMS.append({"severity": sev, "where": "agent_judgment.json: " + where, "note": note, "original": original, "fix": fix})


PC_, LK_P, TR_P, TN_P, RG_P = ["l3", "contradictions"], ["l3", "mechanism_chains", 0, "links"], ["reader_map", "transmission", 0, "links"], ["reader_map", "turnings"], ["reader_map", "regions"]
item("MINOR", "l3.contradictions[1].statement(C2,「升至最新水平 2.5%」处)",
     "C2 称存款便利利率升至最新水平 2.5%%,该处未附序列止于 2026-09-16、其后决议面不可见的提示;C3② 与读者地图标题、欧元区行有该提示(距截止 %d 天、Gate A 列 degraded、【尚未验证】),全文口径一致,"
     "数值无误。矛盾陈述是归档与转引的单元,宜就地带一句限定。结论不变。" % DD["d68"],
     path=PC_ + [1, "statement"], start="升至最新水平 2.5%", end=";主要再融资利率",
     fix="升至序列末观测水平 2.5%(观测=序列变更日=生效日 2026-09-16;L1 quality_status=DEGRADED——序列止于该日,其后决议面不可见【尚未验证】,详见「证据不足」第②项)")
item("MINOR", "l3.contradictions[0].statement(C1,日本全国 CPI 读数处)",
     "日本全国 CPI 同比在注册表 calc 中为引擎自算值(「" + Q_REG_JPCALC + "」," + Q_REG_JPCALC2 + ")。C1 对东京都序列点明了速报先行口径、序列自 2026-01 起、Gate A 列 noncore_missing,"
     "对全国序列的自算口径未作同样提示;点值与快照序列面逐位一致。结论不变。",
     path=PC_ + [0, "statement"], start="日本全国CPI同比百分之二点四四", end="引擎推定规则、非日历实录)", keep_end=True,
     fix="日本全国CPI同比百分之二点四四(观测 2026-10,发布 2026-11-20,引擎推定规则、非日历实录;注册表注记该序列为双基期档各自同月同比后拼接的引擎自算值,与官方公布值抽验 2026-09 为 2.16 对官方 2.1)")
item("MINOR", "l3.contradictions[2].statement(C3,「可核者五项」)",
     "五项之外另有一处两地对照不对称的缺席未列: 欧元区国债收益率 BUND_10Y/BUND_2Y 当日快照 Gate A 列于 noncore_missing(注记=「" + Q_DET_BUND + "」),而日本端 JGB2Y/JGB5Y/JGB10Y 事实行在场"
     "(2026-11-19: %s,%s)且不在 %d 行证据索引内;两地利率期限结构一维因此无法对照。属披露可改进,不改变已有结论。" % (
         "/".join(str(v) for v, _ in JGBV), "/".join(sorted(set(q for _, q in JGBV))), len(EIDX)),
     path=PC_ + [2, "statement"], start="问句所求「证据不足」面,引擎可核者五项。",
     fix="问句所求「证据不足」面,引擎可核者六项(增第⑥项: 欧元区国债收益率 BUND_10Y/BUND_2Y 当日快照 Gate A 列于缺席名单,日本端 JGB 各期限事实行在场,两地利率期限结构对照不对称)。")
item("MINOR", "reader_map.turnings[2].first_mover(东京都 CPI 转折行)",
     "该转折行以 JP_CPI_TOKYO_YOY(2026-06→2026-09,1.6→2.69)为先行指标,该序列当日快照 Gate A 列于 noncore_missing、L1 无事实行;C1 与读者地图日本行有披露,但转折行内未带标记,单看该行不知其为缺席序列上的读数。"
     "候选面命中属实(research_plan.turning_candidates 第三条同值)。结论不变。",
     path=TN_P + [2, "first_mover"], start="东京都 CPI 同比(速报先行口径)", end="(三个月 +1.09 个百分点)。", keep_end=True,
     fix="东京都 CPI 同比(速报先行口径;该序列当日快照 Gate A 列于 noncore_missing,读数取自快照序列面、L1 无对应事实行)2026-06→2026-09 由 1.6 升至 2.69(三个月 +1.09 个百分点)。")
item("MINOR", "reader_map.transmission[0].links[0..2](对质表三行)及各行的 verdict_note",
     "对质表读者可见的只有主解释预期、竞争解释预期与尚不能区分;支撑该裁定的理由均在未被渲染进读者报告的 verdict_note 里(环1: 欧央行 n=2,读数驱动与程序驱动均与观测相容;环2: 主解释预期未纳入美元端利率,两货币对美元同向,两解释在该观测上预期未分立;"
     "环3: 跳升时点不与政策日历对齐、竞争解释在时点上占优,但其快速回落预期仅有一个盘中观测)。判断档字符串叶(len≥12)在 MAP_REPORT.md 命中 %d/%d、FULL_REPORT.md 命中 %d/%d。"
     "无理由的尚不能区分易被读作两解释证据相等;裁定本身保守、不违反证据,列 MINOR。" % (MAP_FOUND, N_LV, FULL_FOUND, N_LV),
     path=TR_P + [1, "main_predicts"], start="主解释(利差主导)预期 EURUSD/USDJPY 对政策差变动敏感、方向分立",
     fix="对质表每行增列一句裁定理由(取自 verdict_note),例如环2: 该预期未纳入美元端利率(UST_10Y 最新 5.04%),两货币对美元同向,两解释在该观测上预期未分立;EURJPY 交叉盘不在证据面,以 EURUSD×USDJPY 推算幅度小(-0.24%/-0.73%)。")
item("MINOR", "l3.contradictions[1].statement(C2,欧央行决议日处)及 reader_map.transmission[0].links[0].main_predicts(环1)",
     "欧央行决议日按引擎生效日前上一个周四的惯例回推并标【推断】,处理正确;但注册表对同一序列的 release_semantics/calc 写的是「" + Q_REG_ECBREL + "」「" + Q_REG_ECBCALC + "」,与引擎惯例不一致,判断档只报引擎口径、未提示两面不一。"
     "环1 据回推决议日计算决议日前可见读数(2026-04=3.0 对 2026-05=3.2;2026-07=2.9 对 2026-08=3.2),该差别依赖未经实录证实的日期;环1 同时给出生效日前口径,结论(尚不能区分)不受影响。",
     path=PC_ + [1, "statement"], start="决议日系引擎按『生效日前上一个周四』惯例自变更日回推", end="属【推断】而非实录(冻结发布日历对欧央行无实录条目)", keep_end=True,
     fix="决议日系引擎按『生效日前上一个周四』惯例自变更日回推、属【推断】而非实录(冻结发布日历对欧央行无实录条目;注册表该序列 release_semantics 另载决议公布后生效并当日更新系列,两口径不一,以序列变更日=生效日为实证面)")
item("MINOR", "l3.contradictions[2].statement(C3②,欧央行序列降级处)",
     "C3② 把两条欧央行序列的 DEGRADED 归因于观测日距截止 %d 天、超过注册表新鲜度阈十天。引擎各面对此并不一致: 快照事实行 issues 记「%s」并列 noncore_degraded;契约验证记 STALE;"
     "而注册表 freshness 对该序列设 decision_dated=true(「%s」),研究计划点值格最新一期锚记 status=ok、freshness_basis=policy_confirmation。判断档采信了降级一面并如实写其后是否有新决议不可判【尚未验证】,未提另一面;"
     "其后决议面不可见的结论本身成立,列披露可改进。" % (DD["d68"], Q_SNAP_ISSUE, Q_REG_DDN),
     path=PC_ + [2, "statement"], start="观测日距研究截止 2026-11-23 六十八天", end="当日快照 Gate A 将该两序列列于降级名单(L1 事实行 quality_status=DEGRADED)", keep_end=True,
     fix="观测日距研究截止 2026-11-23 六十八天,超过注册表新鲜度阈十天,当日快照 Gate A 将该两序列列于降级名单(L1 事实行 quality_status=DEGRADED;注册表 freshness 另设 decision_dated 规则——无更晚已证实决议不作过期,而研究计划点值格记该锚 status=ok,引擎各面不一,故降级是否成立与其后是否有新决议在引擎面同样不可判)")
EA_AN6 = CELLS["EA_HICP_YOY"]["anchors"]["6个月前"]
EA_PUB_WK, EA_RULE = str(EA_AN6["publication_date"]), str(EA_AN6["publication_rule"])
N_EA_PUB_WK = sum(v.count("2026-05-16") for _p, v in LV if isinstance(v, str) and _p[0] != "agent_declaration")
assert EA_PUB_WK == "2026-05-16" and D(EA_PUB_WK).weekday() == 5 and "月末+16天" in EA_RULE and "该推定日落在周日" in JALL and D("2026-08-30").weekday() == 6 and N_EA_PUB_WK == 1
item("MINOR", "reader_map.regions[0].from_to(欧元区行,「发布 2026-05-16」处)",
     "欧元区 2026-04 期读数的引擎推定发布日 %s 落在周六(引擎规则「%s」推算所得,不可能是实际发布日);句中已标引擎推定规则、非日历实录,但未如东京都 2026-08 期推定日处(2026-08-30,句中已点明落在周日)那样点明落在周末。"
     "该日期在判断档正文仅此一处、只作六个月前锚的发布面标注;锚取值(观测月 2026-04 的 %s)与各处可见性结论均不依赖它。披露可改进,结论不变。" % (EA_PUB_WK, EA_RULE, p1(mo(EA, 2026, 4))),
     path=RG_P + [0, "from_to"], start="发布 2026-05-16,引擎推定规则、非日历实录",
     fix="发布 2026-05-16(周六;引擎月末+16 天推定规则、非日历实录,实际发布日以官方实录为准)")
item("NIT", "l3.mechanism_chains[0].links[3].text(环4,「为窗内两个最大单日跳升日」)",
     "该句以跳升窗(2026-11-13→2026-11-20)为窗内;同段前文的窗是月窗(2026-10-23 起),月窗内最大单日跳升是 2026-11-05(+%s%%)。句首已写跳升窗内含…,歧义有限。" % n(VDPCT["2026-11-05"]),
     path=LK_P + [3, "text"], start="为窗内两个最大单日跳升日", fix="为跳升窗内两个最大单日跳升日")
item("NIT", "l3.contradictions[2].statement(C3②)与契约验证非 VERIFIED 项的对应关系",
     "契约验证 %d 个数值串中 1 个状态为 STALE(对象 C2 的 2.5%% 数值串,值与期望值相等,状态 STALE 与该事实行的降级状态同现;引擎注记=「%s」);判断档披露了序列止于 2026-09-16 与 DEGRADED,但未点名该项 STALE,读者无法把契约面的非 VERIFIED 项与文字面对上。实质已披露。" % (len(CV["verdicts"]), Q_ENG_STALE),
     path=PC_ + [2, "statement"], start="当日快照 Gate A 将该两序列列于降级名单(L1 事实行 quality_status=DEGRADED)",
     fix="在「证据不足」第②项末补一句: 契约验证对该 2.5% 数值串记 STALE(该事实行 DEGRADED、观测滞后 68 天)。")
item("NIT", "l3.contradictions[2].statement(C3③,「冻结日历实录仅覆盖…」)",
     "冻结日历共 %d 条,除日本政策目标 %d 条与 EA HICP 历史期 %d 条外,另有非日欧面实录 %d 条;「仅覆盖」在日欧语境下成立,宜加「日欧面」限定。" % (len(CE), CAL_CNT["JP_POLICY_TARGET"], CAL_CNT["EA_HICP_YOY"], len(CE) - len(CAL_JPEA)),
     path=PC_ + [2, "statement"], start="冻结日历实录仅覆盖日本政策目标两条与三条历史期 EA HICP 快报/终值实录",
     fix="冻结日历实录于日欧面仅覆盖日本政策目标两条与三条历史期 EA HICP 快报/终值实录")
item("NIT", "l3.mechanism_chains[0].links[1].text(环2,「决议即…生效」)",
     "「2026-09-18 决议即 2026-09-24 生效」中的「即」易读作当日生效;两者相隔 %d 天(与日历条 effective_on 一致)。读者地图日本行写作决议、2026-09-24 生效,无此问题。" % DD["d6b"],
     path=LK_P + [1, "text"], start="BOJ 2026-09-18 决议即 2026-09-24 生效", fix="BOJ 2026-09-18 决议、2026-09-24 生效")
def _me(y, m_):
    return dt.date(y + (1 if m_ == 12 else 0), (m_ % 12) + 1, 1) - dt.timedelta(days=1)


EA_MAY_PUB, JP_MAY_PUB = [(_me(2026, 5) + dt.timedelta(days=k)).isoformat() for k in (16, 20)]
assert CELLS["EA_HICP_YOY"]["anchors"]["最新一期"]["publication_date"] == (_me(2026, 10) + dt.timedelta(days=16)).isoformat() == "2026-11-16"
assert CELLS["JP_CPI_YOY"]["anchors"]["最新一期"]["publication_date"] == (_me(2026, 10) + dt.timedelta(days=20)).isoformat() == "2026-11-20"
assert CELLS["EA_HICP_YOY"]["anchors"]["6个月前"]["publication_date"] == (_me(2026, 4) + dt.timedelta(days=16)).isoformat() == "2026-05-16"
assert CELLS["JP_CPI_YOY"]["anchors"]["6个月前"]["publication_date"] == (_me(2026, 4) + dt.timedelta(days=20)).isoformat() == "2026-05-20"
assert "月末+16天" in CELLS["EA_HICP_YOY"]["anchors"]["最新一期"]["publication_rule"] and "月末+20天" in CELLS["JP_CPI_YOY"]["anchors"]["最新一期"]["publication_rule"]
assert EA_MAY_PUB == "2026-06-16" and JP_MAY_PUB == "2026-06-20" and "2026-05 期观测日在窗起 2026-05-23 之前、推定发布日在窗内" in JALL
item("NIT", "reader_map.regions[0].from_to(欧元区行,「窗内月度路径 3.2(2026-05)」)",
     "2026-05 期的观测日(2026-05-01)早于窗起 2026-05-23,按引擎推定规则(月末+%d 天)其发布日为 %s,在窗内;机制链环1 对此有说明,读者地图欧元区行直接称窗内月度路径。日本行同构(2026-05 期推定发布日 %s)。" % (
         16, EA_MAY_PUB, JP_MAY_PUB),
     path=RG_P + [0, "from_to"], start="窗内月度路径 3.2(2026-05)", fix="窗内可见月度路径 3.2(2026-05)→…(2026-05 期观测日早于窗起、发布日在窗内)")
item("NIT", "l3.mechanism_chains[0].links[2].text(环3,「UST_10Y 最新 5.04%」)",
     "UST_10Y 的 5.04%% 为 %s 观测(该序列末观测日),非截止日 %s;句中未写观测日。" % (max(U10), CUTOFF),
     path=LK_P + [2, "text"], start="UST_10Y 最新 5.04%", fix="UST_10Y 最新 5.04%(观测 2026-11-19)")
item("NIT", "l4.scenarios[*].rows.trigger / falsification 与 quality_gate_notes[3]",
     "两情景的触发条件含 VIX 分量(S1 高于 30、S2 低于 25),证伪条件均不含 VIX: VIX 收盘落在 25–30 之间时两情景均不触发、亦不因此证伪;另 S1 触发阈(≥4.0%)高于其前提水平(3.5% 以上),3.5%–4.0% 区间同样是前提成立、不触发、不证伪。"
     "quality_gate_notes 只披露了 S2 的 3.0%–3.5% 放宽区间。",
     path=["quality_gate_notes", 3], start="S2 证伪阈值(3.5%)较前提水平(3.0% 以下)放宽", end="区间不触发亦不证伪", keep_end=True,
     fix="…3.0%–3.5% 区间不触发亦不证伪;S1 触发阈 4.0% 高于前提水平 3.5%,3.5%–4.0% 区间同属前提成立而不触发;VIX 收盘在 25–30 之间时两情景均不触发。")
item("NIT", "l3.mechanism_chains[0].links[1].text(环2 标题「观察: 政策面跟进」)",
     "该环证据级别为 E1(观察),正文对月均台阶只写相容、不作相容性判断;标题「跟进」带因果意味,与正文的自制口径略不称。",
     path=LK_P + [1, "text"], start="观察: 政策面跟进", fix="观察: 政策面同向变更")
item("NIT", "reader_map.regions[1].from_to(日本行,「中旬速报先行口径」)",
     "注册表对该序列的发布说明为「%s」,引擎推定规则为「%s」;「中旬」与月末−1 天的推定日不对应。" % (Q_REG_TKREL, Q_MAP_TOKYO),
     path=RG_P + [1, "from_to"], start="中旬速报先行口径", fix="速报先行口径")
item("NIT", "reader_map.regions[1].from_to(日本行,「此后总体回升」)",
     "2026-02 之后全国 CPI 同比由 %s 升至 %s 属实,但路径非逐月单调(2026-03 的 %s→2026-04 的 %s 有一次 %s 个百分点的小幅回落);同句对回落段的两次小幅回升(2025-09、2025-10)作了注明,对回升段的这次小幅回落未注明。" % (
         n(VJ[2]), n(VJ[10]), n(VJ[3]), n(VJ[4]), n(JP_DIP)),
     path=RG_P + [1, "from_to"], start="此后总体回升", fix="此后总体回升(2026-04 一次小幅回落)")
N_MIN = sum(1 for it in ITEMS if it["severity"] == "MINOR")
N_NIT = sum(1 for it in ITEMS if it["severity"] == "NIT")
N_MAJ = sum(1 for it in ITEMS if it["severity"] == "MAJOR")
assert (N_MAJ, N_MIN, N_NIT) == (0, 8, 10), (N_MAJ, N_MIN, N_NIT)
