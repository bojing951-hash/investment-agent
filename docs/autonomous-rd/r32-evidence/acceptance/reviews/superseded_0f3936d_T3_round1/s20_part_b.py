# -*- coding: utf-8 -*-
"""s20_part_b.py —— ⑥转折 ⑦传导链 ⑧历史类比 ⑨情景 ⑩文字与数值一致性 ⑪诚实缺席/Gate A
⑫截止日当日观测时点 ⑬契约非 VERIFIED 项 ⑭交付门缺口披露 + 补充面(SUPP,不计点)。
在 s20_recompute.py 的命名空间内 exec;只读复算,本文件不写任何文件。"""

def ds(x):
    return "%.2f" % x


# =====================================================================
# ⑥ 转折判断与候选面
# =====================================================================
tc = RP["turning_candidates"]["candidates"]
t0, t1, t3 = TN[0], TN[1], TN[2]
num("F01", "⑥", "转折1 前值 JP_CPI_YOY@2025-11", "series_store.JP_CPI_YOY[2025-11-01]", jp["2025-11-01"], t0["value_before"], 1e-9)
num("F02", "⑥", "转折1 后值 JP_CPI_YOY@2026-02", "series_store.JP_CPI_YOY[2026-02-01]", jp["2026-02-01"], t0["value_after"], 1e-9)
num("F03", "⑥", "转折1 三个月变动", "F02−F01", jp["2026-02-01"] - jp["2025-11-01"], -1.63, 1e-9, tok="-1.63 个百分点")
add("F04", "⑥", "转折1 前/后月份与引擎候选面一致", "reader_map.turnings[0] / research_plan.turning_candidates[0]",
    "%s→%s" % (t0["before_date"], t0["date"]), "%s→%s" % (tc[0]["from_ym"], tc[0]["to_ym"]),
    (t0["before_date"], t0["date"], t0["metric_id"]) == (tc[0]["from_ym"], tc[0]["to_ym"], tc[0]["metric_id"]), "")


def rolling3(mp, start_ym):
    """窗口 [start_ym .. 最新] 内全部 3 个月变动 [(from_ym, to_ym, delta)]。"""
    keys = sorted(k for k in mp if k[:7] >= start_ym)
    return [(keys[i][:7], keys[i + 3][:7], mp[keys[i + 3]] - mp[keys[i]]) for i in range(len(keys) - 3)]


START = "2025-11"   # 近十二个月窗起(截止日前 12 个月观测)
r_jp = rolling3(jp, START)
mx_jp = max(r_jp, key=lambda x: abs(x[2]))
add("F05", "⑥", "JP_CPI_YOY 候选=窗内 |三个月变动| 最大者", "series_store.JP_CPI_YOY 滚动3月", "%s→%s %.2f" % mx_jp,
    "2025-11→2026-02 -1.63", mx_jp[0] == "2025-11" and mx_jp[1] == "2026-02" and abs(mx_jp[2] + 1.63) < 1e-9, "")
num("F06", "⑥", "转折2 前值 EA_HICP_YOY@2026-02", "series_store.EA_HICP_YOY[2026-02-01]", ea["2026-02-01"], t1["value_before"], 1e-9)
num("F07", "⑥", "转折2 后值 EA_HICP_YOY@2026-05", "series_store.EA_HICP_YOY[2026-05-01]", ea["2026-05-01"], t1["value_after"], 1e-9)
num("F08", "⑥", "转折2 三个月变动", "F07−F06", ea["2026-05-01"] - ea["2026-02-01"], 1.3, 1e-9, tok="+1.30 个百分点")
add("F09", "⑥", "转折2 前/后月份与引擎候选面一致", "reader_map.turnings[1] / research_plan.turning_candidates[1]",
    "%s→%s" % (t1["before_date"], t1["date"]), "%s→%s" % (tc[1]["from_ym"], tc[1]["to_ym"]),
    (t1["before_date"], t1["date"], t1["metric_id"]) == (tc[1]["from_ym"], tc[1]["to_ym"], tc[1]["metric_id"]), "")
r_ea = rolling3(ea, START)
mx_ea = max(r_ea, key=lambda x: abs(x[2]))
ties = [x for x in r_ea if abs(abs(x[2]) - abs(mx_ea[2])) < 1e-6]
add_supp("ea_rolling_tie", {"pairs_abs_delta_ge_1.2999": [(a, b, round(d, 6)) for a, b, d in ties],
                            "engine_pick": [tc[1]["from_ym"], tc[1]["to_ym"]],
                            "note": "2026-01→04 与 2026-02→05 精确同为 +1.30;浮点噪声 3.2-1.9=1.3000000000000003 > 3.0-1.7=1.2999999999999998,引擎取后者(引擎面观察)"})
add("F10", "⑥", "日本端同窗自谷底回升(2026-02 1.27→2026-05 1.53)", "series_store.JP_CPI_YOY", "%s→%s" % (jp["2026-02-01"], jp["2026-05-01"]),
    "1.27→1.53", jp["2026-05-01"] > jp["2026-02-01"] and abs(jp["2026-05-01"] - 1.53) < 1e-9, "")
num("F11", "⑥", "转折3 前值 JP_POLICY_RATE@2026-04", "series_store.JP_POLICY_RATE[2026-04-01]", pr["2026-04-01"], t3["value_before"], 1e-9)
num("F12", "⑥", "转折3 后值 JP_POLICY_RATE@2026-07", "series_store.JP_POLICY_RATE[2026-07-01]", pr["2026-07-01"], t3["value_after"], 1e-9)
num("F13", "⑥", "转折3 过渡值 2026-06", "series_store.JP_POLICY_RATE[2026-06-01]", pr["2026-06-01"], 0.841, 1e-9, tok="经 2026-06 0.841 过渡")
add("F14", "⑥", "转折3 前/后月份与引擎候选面一致", "reader_map.turnings[2] / research_plan.turning_candidates[3]",
    "%s→%s" % (t3["before_date"], t3["date"]), "%s→%s" % (tc[3]["from_ym"], tc[3]["to_ym"]),
    (t3["before_date"], t3["date"], t3["metric_id"]) == (tc[3]["from_ym"], tc[3]["to_ym"], tc[3]["metric_id"]), "")
r_pr = rolling3(pr, START)
mx_pr = max(r_pr, key=lambda x: abs(x[2]))
add("F15", "⑥", "JP_POLICY_RATE 候选=窗内 |三个月变动| 最大者", "series_store.JP_POLICY_RATE 滚动3月", "%s→%s %.3f" % mx_pr,
    "2026-04→2026-07 0.251", mx_pr[0] == "2026-04" and mx_pr[1] == "2026-07" and abs(mx_pr[2] - 0.251) < 1e-9,
    "次大 2025-11→2026-02 +0.250 / 2026-05→2026-08 +0.250")
w12 = sorted(k for k in ea if k[:7] >= START)
trough12 = min(w12, key=lambda k: ea[k])
add("F16", "⑥", "EA_HICP_YOY 谷底月(近十二个月 2025-11..2026-10 最小值)", "series_store.EA_HICP_YOY 近12月",
    "%s(%.1f)" % (trough12[:7], ea[trough12]), "2026-02 谷底(1.9)", False,
    "reader_map.regions[EA].from_to「路径: 2026-02 谷底 1.9」——谷底实为 2026-01 的 1.7;2026-02 的 1.9 高于前月", sev="MAJOR")
add("F17", "⑥", "同档他处自述的欧元区谷底月", "reader_map.turnings[0].follow_or_diverge / transmission[0].links[0].verdict_note",
    "%s(%.1f)" % (trough12[:7], ea[trough12]), "2026-01 的 1.7",
    trough12[:7] == "2026-01" and "欧元区 2026-01 的 1.7" in JT and "2026-01 的 1.7 升至" in JT,
    "判断档内部自相矛盾(turnings 与 from_to)", sev="MAJOR")
y26 = sorted(k for k in ea if k.startswith("2026") or k.startswith("2025"))
_t25 = min((k for k in y26 if k.startswith("2025")), key=lambda k: ea[k])
_t26 = min((k for k in y26 if k.startswith("2026")), key=lambda k: ea[k])
_tall = min(y26, key=lambda k: ea[k])
add("F18", "⑥", "EA 谷底月(三种窗口: 2025 年内 / 2026 年内 / 2025-01 以来)", "series_store.EA_HICP_YOY",
    "2025年内 %s(%.1f) / 2026年内 %s(%.1f) / 2025年以来 %s(%.1f)" % (_t25[:7], ea[_t25], _t26[:7], ea[_t26], _tall[:7], ea[_tall]),
    "均非 2026-02(2026 年内谷底=2026-01)",
    all(x[:7] != "2026-02" for x in (_t25, _t26, _tall)) and _t26[:7] == "2026-01" and _tall[:7] == "2026-01",
    "2025 年内谷底 2025-05 的 1.9;2026 年内与 2025-01 以来最小值均为 2026-01 的 1.7")
w12e = [ea[k] for k in w12]
add("F19", "⑥", "「最新读数为近十二个月最高」", "series_store.EA_HICP_YOY 近12月最大值", "%s=%.1f" % (w12[-1][:7], max(w12e)), "2026-10=4.0",
    max(w12e) == ea["2026-10-01"] and w12.count("2026-10-01") == 1, "")
decl = sorted(k for k in jp if "2025-01-01" <= k <= "2026-02-01")
ups = [(decl[i - 1][:7], decl[i][:7]) for i in range(1, len(decl)) if jp[decl[i]] > jp[decl[i - 1]]]
add("F20", "⑥", "JP_CPI_YOY 2025-01→2026-02 逐月读数回升的月数(「持续回落」)", "series_store.JP_CPI_YOY[2025-08-01..2025-10-01] 逐月差",
    len(ups), 0, not ups,
    "回升月: %s;读数 %s" % (ups, "→".join("%s %.2f" % (k[:7], jp[k]) for k in decl if "2025-08-01" <= k <= "2025-10-01")), sev="NIT")
add("F21", "⑥", "「2026-05 峰值 3.2」为局部高点", "series_store.EA_HICP_YOY 2026-04/05/06",
    "%.1f/%.1f/%.1f" % (ea["2026-04-01"], ea["2026-05-01"], ea["2026-06-01"]), "3.0/3.2/2.8",
    ea["2026-05-01"] > ea["2026-04-01"] and ea["2026-05-01"] > ea["2026-06-01"], "")
add("F22", "⑥", "「同期欧元区 HICP 亦下行(2025-11 2.1→2026-02 1.9)」方向", "series_store.EA_HICP_YOY", "%.1f→%.1f" % (ea["2025-11-01"], ea["2026-02-01"]),
    "2.1→1.9", ea["2026-02-01"] < ea["2025-11-01"], "")
jall = sorted(k for k in jp if k >= "2025-01-01")
jt_ = min(jall, key=lambda k: jp[k])
add("F23", "⑥", "日本谷底月(2025 年以来最小值)", "series_store.JP_CPI_YOY", "%s(%.2f)" % (jt_[:7], jp[jt_]), "2026-02 的 1.27",
    jt_ == "2026-02-01" and abs(jp[jt_] - 1.27) < 1e-9, "判断档 turnings[0]「日本 2026-02 的 1.27」")
add("F24", "⑥", "「候选池内最大单段变动」", "research_plan.turning_candidates[*].delta", max(tc, key=lambda c: abs(c["delta"]))["delta"], -1.63, 1e-9,
    "四个候选 Δ: %s" % [c["delta"] for c in tc])

# =====================================================================
# ⑦ 传导链各环
# =====================================================================
LEV = ["E1", "E1", "E2", "E2"]
add("G01", "⑦", "四环证据级标注", "l3.mechanism_chains[0].links[*].evidence_level", "/".join(x["evidence_level"] for x in ML),
    "/".join(LEV), [x["evidence_level"] for x in ML] == LEV, "观察环=E1;传导/归因环=E2")
add("G02", "⑦", "E2 环带缺环注记", "links[2].missing_link_note / links[3].missing_link_note",
    "%s / %s" % (bool(ML[2].get("missing_link_note")), bool(ML[3].get("missing_link_note"))), "True / True",
    bool(ML[2].get("missing_link_note")) and bool(ML[3].get("missing_link_note")), "")
add("G03", "⑦", "E2 环以【假设】/条件式措辞出现", "links[2].text / links[3].text",
    "%s / %s" % ("【假设】" in ML[2]["text"], "相容" in ML[3]["text"] and "不可证" in ML[3]["text"]), "True / True",
    "【假设】" in ML[2]["text"] and ("【假设】" in TR[2]["causal_hypothesis"]), "links[3] 观察事实+E2 归因句「均相容/不可证」")
allrefs = []
for c in C:
    allrefs += c["evidence_refs"]
for x in ML:
    allrefs += x["evidence_refs"]
add("G04", "⑦", "引用条数", "contradictions[*].evidence_refs + mechanism_chains[0].links[*].evidence_refs", len(allrefs), 20,
    len(allrefs) == 20 and "共 20 条 snapshot_fact 引用" in JT, "")
dang = [r for r in allrefs if r not in EVREFS]
add("G05", "⑦", "悬空引用数(须全部解析到 evidence_index)", "evidence_index[*].ref", len(dang), 0, not dang and "零悬空引用" in JT, "")
cnts = [len(c["evidence_refs"]) for c in C] + [len(x["evidence_refs"]) for x in ML]
add("G06", "⑦", "逐条引用数 C1/C2/C3/M1-1..4", "同上", "/".join(str(x) for x in cnts), "2/6/2/2/2/2/4", cnts == [2, 6, 2, 2, 2, 2, 4], "与契约 six_checks 披露(C1 2/C2 6/C3 2)一致")


def vis_before(asof):
    o, v = latest_published("EA_HICP_YOY", asof)
    return "%s=%.1f" % (o.isoformat()[:7], v)


VIS = [("G07", "2026-06-17 生效前: 决议日 2026-06-11 前可见读数", "2026-06-11", "2026-04=3.0"),
       ("G08", "2026-06-17 生效前可见读数", "2026-06-17", "2026-05=3.2"),
       ("G09", "2026-09-16 生效前: 决议日 2026-09-10 前可见读数", "2026-09-10", "2026-07=2.9"),
       ("G10", "2026-09-16 生效前(含当日)可见读数", "2026-09-16", "2026-08=3.2")]
for pid, item, asof, exp in VIS:
    got = vis_before(D(asof))
    add(pid, "⑦", item, "series_store.EA_HICP_YOY 按席位规则取 <%s(含) 最新已发布" % asof, got, exp, got == exp and exp in JT, "")
add("G11", "⑦", "2026-08 读数发布日=生效日(先后时刻不可分)", "席位规则 2026-08 月末+16天", pub_date("EA_HICP_YOY", D("2026-08-01")).isoformat(),
    "2026-09-16", pub_date("EA_HICP_YOY", D("2026-08-01")).isoformat() == "2026-09-16" and "先后时刻不可分" in JT, "")
FX = [("G12", "EURUSD", "2026-10-23", 1.1221, 5e-5, "1.1221"), ("G13", "EURUSD", "2026-11-20", 1.0970, 5e-5, "1.0970"),
      ("G14", "USDJPY", "2026-10-23", 156.494, 5e-4, "156.494"), ("G15", "USDJPY", "2026-11-20", 159.707, 5e-4, "159.707"),
      ("G16", "DXY", "2026-10-23", 101.81, 5e-5, "101.81"), ("G17", "DXY", "2026-11-20", 103.81, 5e-5, "103.81"),
      ("G18", "EURUSD", "2026-11-23", 1.0940, 5e-5, "1.0940"), ("G19", "USDJPY", "2026-11-23", 159.347, 5e-4, "159.347"),
      ("G20", "DXY", "2026-11-23", 104.079, 5e-4, "104.079")]
for pid, m, d_, rv, tol, tokn in FX:
    num(pid, "⑦", "%s 水平 %s" % (m, d_), "series_store.%s[%s]" % (m, d_), val(m, d_), rv, tol, tok=tokn)
FXP = [("G21", "EURUSD", "2026-11-20", -2.24, "-2.24%"), ("G22", "USDJPY", "2026-11-20", 2.05, "+2.05%"),
       ("G23", "DXY", "2026-11-20", 1.96, "+1.96%"), ("G24", "EURUSD", "2026-11-23", -2.51, "-2.51%"),
       ("G25", "USDJPY", "2026-11-23", 1.82, "+1.82%"), ("G26", "DXY", "2026-11-23", 2.23, "+2.23%")]
for pid, m, d_, rv, tokn in FXP:
    num(pid, "⑦", "%s 月窗变动%%(2026-10-23→%s)" % (m, d_), "series_store.%s[2026-10-23→%s]" % (m, d_),
        pct(val(m, "2026-10-23"), val(m, d_)), rv, 5e-3, tok=tokn)
EQ = [("G27", "SPX", -9.36, "SPX 下跌 9.36%"), ("G28", "NIKKEI225", -9.98, "NIKKEI225 下跌 9.98%"),
      ("G29", "DAX", -1.50, "DAX 下跌 1.50%"), ("G30", "CAC40", 1.86, "CAC40 上涨 1.86%")]
for pid, m, rv, tokn in EQ:
    num(pid, "⑦", "%s 同日收盘月窗变动%%(2026-10-23→2026-11-20)" % m, "series_store.%s[2026-10-23→2026-11-20]" % m,
        pct(val(m, "2026-10-23"), val(m, "2026-11-20")), rv, 5e-3, tok=tokn)
num("G31", "⑦", "VIX 窗起收盘 2026-10-23", "series_store.VIX[2026-10-23]", val("VIX", "2026-10-23"), 19.45, 5e-5, tok="19.45")
num("G32", "⑦", "VIX 2026-11-20 收盘", "series_store.VIX[2026-11-20]", val("VIX", "2026-11-20"), 35.89, 5e-5, tok="35.89")
num("G42", "⑦", "日元对美元月窗变动%(USDJPY 倒数;2026-10-23→2026-11-20)", "series_store.USDJPY[2026-10-23→2026-11-20] 取倒数",
    pct(1.0 / val("USDJPY", "2026-10-23"), 1.0 / val("USDJPY", "2026-11-20")), -2.01, 5e-3, note="日元对美元同走弱(幅度略小于欧元),与 EURJPY 合成交叉盘 -0.24% 自洽")
num("G43", "⑦", "日元对美元月窗变动%(USDJPY 倒数;2026-10-23→2026-11-23)", "series_store.USDJPY[2026-10-23→2026-11-23] 取倒数",
    pct(1.0 / val("USDJPY", "2026-10-23"), 1.0 / val("USDJPY", "2026-11-23")), -1.79, 5e-3, note="至 2026-11-23 盘中")
num("G33", "⑦", "VIX 同日收盘月窗变动%", "series_store.VIX[2026-10-23→2026-11-20]", pct(val("VIX", "2026-10-23"), val("VIX", "2026-11-20")),
    84.5, 0.05, tok="+84.5%")
vlast6 = [x for x in series("VIX") if x[0] <= D("2026-11-20")][-6:]
vpath = "→".join("%s %.2f" % (d_.strftime("%m-%d"), v) for d_, v in vlast6)
add("G34", "⑦", "VIX 末六个交易日收盘路径", "series_store.VIX 截至 2026-11-20 末 6 观测", vpath,
    "11-13 19.30→11-16 22.91→11-17 25.46→11-18 24.56→11-19 28.44→11-20 35.89",
    vpath == "11-13 19.30→11-16 22.91→11-17 25.46→11-18 24.56→11-19 28.44→11-20 35.89", "连续 6 个交易日,中间无缺日")
n5 = len([x for x in series("VIX") if D("2026-11-13") < x[0] <= D("2026-11-20")])
add("G35", "⑦", "「跳升集中于末五个交易日」交易日数", "series_store.VIX (2026-11-13, 2026-11-20] 观测数", n5, 5, n5 == 5, "")
add("G36", "⑦", "VIX 跳升起点距最近政策日(2026-10-30)天数", "2026-11-13 − 2026-10-30", (D("2026-11-13") - D("2026-10-30")).days, 14,
    (D("2026-11-13") - D("2026-10-30")).days == 14 and "14 天" in JT, "")
add("G37", "⑦", "VIX 跳升起点距 ECB 最近生效日天数", "2026-11-13 − 2026-09-16", (D("2026-11-13") - D("2026-09-16")).days, 58,
    (D("2026-11-13") - D("2026-09-16")).days == 58 and "58 天" in JT, "")
for pid, m, d_, rv in (("G38", "SPX", "2026-11-23", 7203.85), ("G39", "DAX", "2026-11-23", 25209.45),
                       ("G40", "NIKKEI225", "2026-11-20", 56436.65), ("G41", "VIX", "2026-11-23", 27.01)):
    num(pid, "⑦", "引擎资产月窗回贴值 %s@%s" % (m, d_), "series_store.%s[%s]" % (m, d_), val(m, d_), rv, 5e-3)

# =====================================================================
# ⑧ 历史类比
# =====================================================================
add("H01", "⑧", "历史类比段数", "reader_map.history_periods", len(RM["history_periods"]), 0,
    len(RM["history_periods"]) == 0 and "历史类比 0 段" in JT, "零段如实写明")
s6 = [st for st in rep["steps"] if st.get("step") == "S6_analog"][0]["envelope"]["data"]
add("H02", "⑧", "S6 扫描候选月数", "steps[S6_analog].envelope.data.candidates.scanned", s6["candidates"]["scanned"], 1871,
    s6["candidates"]["scanned"] == 1871 and "扫描 1871 个候选月" in JT, "")
add("H03", "⑧", "S6 有效候选数", "…candidates.valid", s6["candidates"]["valid"], 74, s6["candidates"]["valid"] == 74 and "有效 74" in JT, "")
add("H04", "⑧", "S6 TOP1 候选月", "…data.top[0].candidate_month", s6["top"][0]["candidate_month"], "2025-03",
    s6["top"][0]["candidate_month"] == "2025-03" and "TOP1 候选月 2025-03" in JT, "")
num("H05", "⑧", "S6 TOP1 距离", "…data.top[0].distance", s6["top"][0]["distance"], 0.727, 5e-4, tok="距离 0.727")
add("H06", "⑧", "未以未核验的事后结果充数(零段)", "reader_map.history_zero_case_note", "不以未核验的事后结果充数", "同左",
    "不以未核验的事后结果充数" in RM["history_zero_case_note"], "")

# =====================================================================
# ⑨ 情景
# =====================================================================
s1, s2 = S["S1-STICKY-TIGHTEN"], S["S2-INFL-FADE"]
add("I01", "⑨", "两情景期限", "l4.scenarios[*].rows.trigger.deadline", "%s/%s" % (s1["trigger"]["deadline"], s2["trigger"]["deadline"]),
    "2027-02-15/2027-02-15", s1["trigger"]["deadline"] == s2["trigger"]["deadline"] == "2027-02-15", "晚于截止日(未来时限)")
pea, pjp = pub_date("EA_HICP_YOY", D("2026-12-01")), pub_date("JP_CPI_YOY", D("2026-12-01"))
add("I02", "⑨", "2026-12 观测月读数按规则入档日≤期限(EA)", "席位规则 2026-12 月末+16天", pea.isoformat(), "≤2027-02-15,且在 2027-01",
    pea <= D("2027-02-15") and pea.strftime("%Y-%m") == "2027-01" and "于 2027-01 入档" in JT, "")
add("I03", "⑨", "2026-12 观测月读数按规则入档日≤期限(JP)", "席位规则 2026-12 月末+20天", pjp.isoformat(), "≤2027-02-15",
    pjp <= D("2027-02-15"), "")
add("I04", "⑨", "S1 触发条件在截止日未可判(2026-11/12 读数未发布)", "series_store.EA_HICP_YOY 最新已发布观测", latest_published("EA_HICP_YOY", CUTD)[0].isoformat()[:7],
    "2026-10", latest_published("EA_HICP_YOY", CUTD)[0].isoformat()[:7] == "2026-10", "未触发;亦未被证伪(证伪须 2026-11 与 2026-12 两月均 <3.5)")
add("I05", "⑨", "S2 触发条件在截止日未可判", "同上", latest_published("EA_HICP_YOY", CUTD)[0].isoformat()[:7], "2026-10",
    latest_published("EA_HICP_YOY", CUTD)[0].isoformat()[:7] == "2026-10", "未触发;未被证伪(2026-10 读数 4.0≥3.5 仅为一个月)")
add("I06", "⑨", "截止日读数与情景相容: S1 前提 3.5% 以上", "series_store.EA_HICP_YOY[2026-10-01]", ea["2026-10-01"], "≥3.5", ea["2026-10-01"] >= 3.5, "")
add("I07", "⑨", "截止日读数与情景相容: S1 日本前提 2.0% 以上", "series_store.JP_CPI_YOY[2026-10-01]", jp["2026-10-01"], "≥2.0", jp["2026-10-01"] >= 2.0, "")
add("I08", "⑨", "S1 证伪阈值与前提水平对齐", "S1.falsification.threshold(3.5%) vs S1.scenario 前提(3.5% 以上)", 3.5, 3.5,
    "均低于 3.5%" in s1["falsification"]["threshold"] and "3.5% 以上" in s1["scenario"], "")
add("I09", "⑨", "S2 证伪阈值(3.5%)与前提水平(3.0% 以下)对齐?", "S2.falsification.threshold vs S2.scenario 前提", "阈值 3.5 ≠ 前提 3.0",
    "证伪阈值与前提水平对齐(3.5%)", False, "QGN[3] 的「对齐」对 S1 成立、对 S2 不成立(3.0–3.5 为两不管区)", sev="MINOR")
add("I10", "⑨", "两情景方向互补", "S1.scenario vs S2.scenario",
    "S1: HICP 维持 3.5% 以上、ECB 再上调 / S2: HICP 回落至 3.0% 以下、ECB 按兵不动", "方向相反",
    "3.5% 以上" in s1["scenario"] and "3.0% 以下" in s2["scenario"] and "至少一次 +25bp 上调" in s1["scenario"] and "按兵不动" in s2["scenario"], "")
add("I11", "⑨", "VIX 触发阈值(>30 / <25)可观测且与截止日读数相容", "series_store.VIX[2026-11-20/2026-11-23]",
    "%.2f / %.2f" % (val("VIX", "2026-11-20"), val("VIX", "2026-11-23")), "介于 25 与 30 之间(未单侧触发)",
    25 < val("VIX", "2026-11-23") < 30 and "收盘高于 30" in s1["trigger"]["condition"] and "收盘低于 25" in s2["trigger"]["condition"], "")
add("I12", "⑨", "证伪指标在册可观测", "l4.scenarios[*].rows.falsification.metric_id", "%s/%s" % (s1["falsification"]["metric_id"], s2["falsification"]["metric_id"]),
    "EA_HICP_YOY/EA_HICP_YOY", s1["falsification"]["metric_id"] in SS and s2["falsification"]["metric_id"] in SS, "日本分量仅为 secondary,无数值证伪阈值")

# =====================================================================
# ⑩ 文字与数值一致性 / 对质表
# =====================================================================
vc = {"支持主解释": 0, "支持竞争解释": 0, "尚不能区分": 0}
for l in TR:
    vc[l["face_off_verdict"]] = vc.get(l["face_off_verdict"], 0) + 1
add("J01", "⑩", "对质裁定计数与 QGN[1] 自述一致", "reader_map.transmission[0].links[*].face_off_verdict",
    "%d/%d/%d" % (vc["支持主解释"], vc["支持竞争解释"], vc["尚不能区分"]), "0/1/2",
    (vc["支持主解释"], vc["支持竞争解释"], vc["尚不能区分"]) == (0, 1, 2) and "支持主解释 0·支持竞争解释 1·尚不能区分 2" in JT,
    "计数自洽;第 2 环裁定有效性见 J02")
tu, tl2 = val("DFEDTARU", "2026-11-23"), val("DFEDTARL", "2026-11-23")
ch_u = changes(series("DFEDTARU"))
add_supp("fed_band", {"DFEDTARU@2026-11-23": tu, "DFEDTARL@2026-11-23": tl2, "DFEDTARU_last_change": ch_u[-1][0].isoformat(),
                      "DFEDTARU_prev_value": ch_u[-1][1], "UST_10Y@2026-11-19": val("UST_10Y", "2026-11-19"),
                      "in_evidence_index": [m for m in ("DFEDTARU", "DFEDTARL", "DFF", "FED_FUNDS") if any(r.get("metric_id") == m for r in ev)]})
chg_win = {"Fed(DFEDTARU)": [x[0].isoformat() for x in ch_u if D("2026-10-23") <= x[0] <= CUTD],
           "ECB_MRO": [x[0].isoformat() for x in mc if D("2026-10-23") <= x[0] <= CUTD],
           "ECB_DFR": [x[0].isoformat() for x in dc if D("2026-10-23") <= x[0] <= CUTD],
           "BOJ_calendar": [e.get("decision_date") for e in CAL_ENT if e.get("metric_id") == "JP_POLICY_TARGET" and e.get("decision_date")
                            and D("2026-10-23") <= D(e["decision_date"]) <= CUTD]}
add_supp("policy_changes_in_fx_window_2026-10-23_2026-11-23", chg_win)
add("J02", "⑩", "对质第 2 环(EURUSD 行)裁定是否与两解释预期分立相称", "series_store.DFEDTARU/DFEDTARL@2026-11-23 + ECB_MRO 末值 + 日历 BOJ 目标",
    "美元端目标区间 %.2f–%.2f > MRO %.2f > BOJ %.2f;窗内三地无政策变动→利差主导对 EURUSD 亦预期走弱,两解释预期未分立→应为「尚不能区分」"
    % (tl2, tu, mro[-1][1], bd.get("target_value", float("nan"))), TR[1]["face_off_verdict"], False,
    "face_off_verdict=「支持竞争解释」违反读者报告自述判断口径「预期未分立=尚不能区分」;M1 step3「竞争解释在本月窗获支持」与 QGN[1] 计数随之联动", sev="MAJOR")
cr20 = pct(val("EURUSD", "2026-10-23") * val("USDJPY", "2026-10-23"), val("EURUSD", "2026-11-20") * val("USDJPY", "2026-11-20"))
cr23 = pct(val("EURUSD", "2026-10-23") * val("USDJPY", "2026-10-23"), val("EURUSD", "2026-11-23") * val("USDJPY", "2026-11-23"))
add_supp("eurjpy_synthetic_cross", {"method": "EURUSD×USDJPY 同日两腿相乘(两序列同快照同日观测)",
                                    "EURJPY@2026-10-23": val("EURUSD", "2026-10-23") * val("USDJPY", "2026-10-23"),
                                    "EURJPY@2026-11-20": val("EURUSD", "2026-11-20") * val("USDJPY", "2026-11-20"),
                                    "EURJPY@2026-11-23": val("EURUSD", "2026-11-23") * val("USDJPY", "2026-11-23"),
                                    "chg_pct_to_2026-11-20": round(cr20, 4), "chg_pct_to_2026-11-23": round(cr23, 4)})
add("J03", "⑩", "「EURJPY 交叉盘…直接检验(欧元相对日元走强)不可做」", "series_store.EURUSD×USDJPY 同日两腿合成",
    "可合成: 至 2026-11-20 %.2f%% / 至 2026-11-23 %.2f%%" % (cr20, cr23), "不可做", False,
    "合成交叉盘可算且幅度小(未支持「欧元相对日元走强」);「不可做」与证据面不符", sev="MAJOR")
mid = [(d_.isoformat(), v) for d_, v in series("VIX") if D("2026-11-04") <= d_ <= D("2026-11-12")]
add_supp("vix_midwindow_episode", {"VIX_closes_2026-11-04..2026-11-12": mid,
                                   "spike_pct_11-04_to_11-05": round(pct(val("VIX", "2026-11-04"), val("VIX", "2026-11-05")), 2),
                                   "SPX_11-04_to_11-05_pct": round(pct(val("SPX", "2026-11-04"), val("SPX", "2026-11-05")), 2),
                                   "NIKKEI225_11-04_to_11-06_pct": round(pct(val("NIKKEI225", "2026-11-04"), val("NIKKEI225", "2026-11-06")), 2)})
nmid = len([1 for d_, v in mid if d_ > "2026-11-05" and v < val("VIX", "2026-11-05")])
after20 = [(d_, v) for d_, v in series("VIX") if d_ > D("2026-11-20")]
add("J04", "⑩", "对质第 3 环「『快速回落』预期仅有一个盘中观测(2026-11-23 快照 27.01)」", "series_store.VIX 观测日 > 2026-11-20 + research_as_of(纽约 09:53=盘中)",
    "11-20 收盘后在场观测 %d 个(%s)" % (len(after20), ",".join("%s=%.2f" % (d_.isoformat(), v) for d_, v in after20)),
    "仅有一个盘中观测(2026-11-23 快照 27.01)", len(after20) == 1 and after20[0][0] == D("2026-11-23") and abs(after20[0][1] - 27.01) < 1e-9,
    "字面成立。另(不计偏离): 同窗内已有一段未援引的冲高回落收盘观测(2026-11-05 冲高 28.18 之后至 11-12 有 %d 个收盘低于冲高值),见补充面 vix_midwindow_episode" % nmid)
add("J05", "⑩", "总判断方向词: 日本最新读数低于去年同月", "series_store.JP_CPI_YOY 2026-10 vs 2025-10", "%.2f vs %.2f" % (jp["2026-10-01"], jp["2025-10-01"]),
    "低于", jp["2026-10-01"] < jp["2025-10-01"], "")
add("J06", "⑩", "总判断方向词: 欧元区最新读数高于去年同月", "series_store.EA_HICP_YOY 2026-10 vs 2025-10", "%.1f vs %.1f" % (ea["2026-10-01"], ea["2025-10-01"]),
    "高于", ea["2026-10-01"] > ea["2025-10-01"], "")
add_supp("six_month_anchor_direction", {"JP_CPI_YOY": [jp["2026-04-01"], jp["2026-10-01"]], "EA_HICP_YOY": [ea["2026-04-01"], ea["2026-10-01"]],
                                          "note": "较六个月前锚两地读数均上行(日本 +1.06、欧元区 +1.00 个百分点);总判断「方向相反」仅就「相比去年同月」成立"})
num("J07", "⑩", "「UST_10Y 最新 5.04%」", "series_store.UST_10Y[2026-11-19]", val("UST_10Y", "2026-11-19"), 5.04, 1e-9, tok="UST_10Y 最新 5.04%")
add("J08", "⑩", "「两地股指弱于美股」在欧元区端不成立", "series_store DAX/CAC40/SPX 2026-10-23→2026-11-20",
    "%.2f/%.2f vs %.2f" % (pct(val("DAX", "2026-10-23"), val("DAX", "2026-11-20")), pct(val("CAC40", "2026-10-23"), val("CAC40", "2026-11-20")),
                           pct(val("SPX", "2026-10-23"), val("SPX", "2026-11-20"))), "DAX -1.50、CAC40 +1.86 vs SPX -9.36",
    pct(val("DAX", "2026-10-23"), val("DAX", "2026-11-20")) > pct(val("SPX", "2026-10-23"), val("SPX", "2026-11-20"))
    and pct(val("CAC40", "2026-10-23"), val("CAC40", "2026-11-20")) > pct(val("SPX", "2026-10-23"), val("SPX", "2026-11-20")), "")
gapnik = abs(pct(val("NIKKEI225", "2026-10-23"), val("NIKKEI225", "2026-11-20")) - pct(val("SPX", "2026-10-23"), val("SPX", "2026-11-20")))
add("J09", "⑩", "「日本端与美股相当」", "series_store NIKKEI225 vs SPX 同窗变动差(百分点)", round(gapnik, 2), "≤1.0 个百分点", gapnik <= 1.0, "")
pdf = RP["policy_doc_facts"][0]
injump = D("2026-11-13") < D(pdf["published_on"]) <= D("2026-11-20")
add("J10", "⑩", "对质第 3 环时点论证(「距最近政策日 2026-10-30…14 天」)是否处理了引擎面在场的政策文献事件",
    "research_plan.policy_doc_facts[0](doc_id/published_on) / MAP_REPORT.md 政策文档事实表",
    "%s 发布日 %s,落在 VIX 跳升窗 2026-11-13→2026-11-20 内=%s" % (pdf["doc_id"], pdf["published_on"], injump),
    "判断档已处理该事件(提及 FOMC 纪要/2026-11-18)", ("FOMC" in JT or "纪要" in JT or "2026-11-18" in JT),
    "「14 天」仅就两地(日/欧)政策日成立且数值无误;同页引擎面列有 FOMC 2026年10月会议纪要 2026-11-18 发布(纪要发布≠决议日),为第三类候选驱动,判断档未援引亦未排除;裁定(尚不能区分)不变",
    sev="MINOR")


def _win4(m, a, b):
    return [(d_.isoformat(), round(v, 4)) for d_, v in series(m) if D(a) <= d_ <= D(b)]


add_supp("policy_doc_event_window", {"doc": pdf, "in_jump_window": injump,
                                     "VIX_2026-11-17..2026-11-20": _win4("VIX", "2026-11-17", "2026-11-20"),
                                     "SPX_2026-11-17..2026-11-20": _win4("SPX", "2026-11-17", "2026-11-20"),
                                     "UST_10Y_2026-11-17..2026-11-19": _win4("UST_10Y", "2026-11-17", "2026-11-19"),
                                     "EURUSD_2026-11-17..2026-11-20": _win4("EURUSD", "2026-11-17", "2026-11-20"),
                                     "USDJPY_2026-11-17..2026-11-20": _win4("USDJPY", "2026-11-17", "2026-11-20")})

# =====================================================================
# ⑪ 诚实缺席项 / Gate A
# =====================================================================
add("K01", "⑪", "东京 CPI 列于 Gate A noncore_missing", "snapshot.gate_a.noncore_missing", "JP_CPI_TOKYO_YOY" in GATE["noncore_missing"], True,
    "JP_CPI_TOKYO_YOY" in GATE["noncore_missing"] and "Gate A 列于 noncore_missing" in JT, "")
add("K02", "⑪", "缺席理由文字(来源文件在场而指标缺席)", "snapshot.gate_a.noncore_missing_detail.JP_CPI_TOKYO_YOY",
    GATE["noncore_missing_detail"].get("JP_CPI_TOKYO_YOY"), "来源文件在场而指标缺席",
    "来源文件在场而指标缺席" in GATE["noncore_missing_detail"].get("JP_CPI_TOKYO_YOY", "") and "来源文件在场而指标缺席" in JT, "")
add("K03", "⑪", "东京 CPI 无 L1 事实行", "snapshot.facts[*].metric_id", [f["fact_id"] for f in FACTS if f["metric_id"] == "JP_CPI_TOKYO_YOY"], [],
    not [f for f in FACTS if f["metric_id"] == "JP_CPI_TOKYO_YOY"] and "L1 无对应事实行" in JT, "")
add("K04", "⑪", "ECB_MRO 列于 Gate A noncore_degraded", "snapshot.gate_a.noncore_degraded", "ECB_MRO" in GATE["noncore_degraded"], True,
    "ECB_MRO" in GATE["noncore_degraded"], "")
add("K05", "⑪", "ECB_DFR 列于 Gate A noncore_degraded", "snapshot.gate_a.noncore_degraded", "ECB_DFR" in GATE["noncore_degraded"], True,
    "ECB_DFR" in GATE["noncore_degraded"] and "Gate A 列 degraded" in JT, "")
add("K06", "⑪", "JP_CPI_YOY L1 质量状态", "facts[JP_CPI_YOY@2026-10-01].quality_status", FACT["JP_CPI_YOY@2026-10-01"]["quality_status"], "WARN",
    FACT["JP_CPI_YOY@2026-10-01"]["quality_status"] == "WARN", "")
add("K07", "⑪", "EA_HICP_YOY L1 质量状态", "facts[EA_HICP_YOY@2026-10-01].quality_status", FACT["EA_HICP_YOY@2026-10-01"]["quality_status"], "WARN",
    FACT["EA_HICP_YOY@2026-10-01"]["quality_status"] == "WARN" and "WARN 与 WARN" in JT, "")
planm = [m for _, m in PLAN]
add("K08", "⑪", "六计划指标中除东京 CPI 外均不在任何缺席名单", "snapshot.gate_a.core_missing/noncore_missing/noncore_fail/core_fail",
    [m for m in planm if m in GATE["noncore_missing"] or m in GATE["core_missing"] or m in GATE["noncore_fail"] or m in GATE["core_fail"]],
    ["JP_CPI_TOKYO_YOY"], [m for m in planm if m in (GATE["noncore_missing"] + GATE["core_missing"] + GATE["noncore_fail"] + GATE["core_fail"])] == ["JP_CPI_TOKYO_YOY"], "")
add("K09", "⑪", "JP_POLICY_TARGET 缺口=注册表缺席(引擎面)", "research_plan.dimension_gaps[*]", [(g["metric_id"], g["gap"]) for g in RP["dimension_gaps"]],
    [("JP_POLICY_TARGET", "registry_absent")], [(g["metric_id"], g["gap"]) for g in RP["dimension_gaps"]] == [("JP_POLICY_TARGET", "registry_absent")], "")
add("K10", "⑪", "Gate A 总体状态如实披露", "snapshot.gate_a.status / report.md 第 5 行", GATE["status"], "DEGRADED(报告已披露)",
    GATE["status"] == "DEGRADED" and "gate_a" in REPMD_TEXT and "DEGRADED" in REPMD_TEXT, "MAP_REPORT.md 无总体状态行(仅经判断文字披露具体名单)=引擎渲染观察")
add("K11", "⑪", "未以相邻口径冒充(东京 CPI 与全国 CPI 分列)", "判断档 C1 / reader_map.regions[JP]", "东京都CPI同比(中旬速报先行口径) 单列", "同左",
    "中旬速报先行口径" in JT and "去年同月基期观测不可得" in JT, "")

add("K12", "⑪", "C1 竞争解释「引擎无分项构成与基数贡献序列」", "snapshot.series_store 指标名含 HICP/CPI 者",
    [m for m in SS if "HICP" in m or "CPI" in m], "无欧元区/日本核心或分项序列",
    not [m for m in SS if ("HICP" in m or "CPI" in m) and m not in ("EA_HICP_YOY", "CN_CPI_YOY", "JP_CPI_YOY", "JP_CPI_TOKYO_YOY", "CPI", "CORE_CPI")]
    and "引擎无分项构成与基数贡献序列" in JT, "在册: EA_HICP_YOY、CN_CPI_YOY、JP_CPI_YOY、JP_CPI_TOKYO_YOY、CPI、CORE_CPI(后两者为美国指标)")
add_supp("contract_face", {"version": CV.get("version"), "stats": CV.get("stats"), "unresolved_unbound": CV.get("unresolved_unbound"),
                           "map_checks": [(m.get("item"), m.get("status"), m.get("note")) for m in CV.get("map_checks", [])],
                           "fact_calc_JP_CPI_YOY": str(FACT["JP_CPI_YOY@2026-10-01"].get("calc")),
                           "fact_issues": {k: FACT[k + "@2026-10-01"].get("issues") for k in ("JP_CPI_YOY", "EA_HICP_YOY", "JP_POLICY_RATE")}})

# =====================================================================
# ⑫ 截止日当日日频观测时点
# =====================================================================
add("L01", "⑫", "快照采集时间戳字面", "snapshot.research_as_of / 判断档 QGN[4]", ra, "2026-11-23T22:53:47+08:00", ra == "2026-11-23T22:53:47+08:00" and ra in JT, "")
cutd_metrics = ["SPX", "VIX", "DAX", "CAC40", "EURUSD", "USDJPY", "DXY"]
bad = [m for m in cutd_metrics if FACT.get("%s@2026-11-23" % m) is None]
add("L02", "⑫", "截止日当日观测的日频指标(事实行在场)", "snapshot.facts[*].observation_date=2026-11-23", [m for m in cutd_metrics if ("%s@2026-11-23" % m) in FACT],
    cutd_metrics, not bad, "")
add("L03", "⑫", "截止日值标注为盘中快照、非收盘价", "判断档 QGN[4]/C2", "SPX/VIX/DAX/CAC40 截止日值与外汇/DXY 值=盘中快照、非收盘价", "同左",
    "均为盘中快照、非收盘价" in JT and "盘中快照、非收盘价" in JT, "")
add("L04", "⑫", "时点说明与 research_as_of 相容(纽约 09:53=开盘后盘中)", "snapshot.research_as_of→America/New_York",
    datetime.fromisoformat(ra).astimezone(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M") if ZoneInfo else "n/a", "2026-11-23 09:53(盘中)",
    ZoneInfo is not None and datetime.fromisoformat(ra).astimezone(ZoneInfo("America/New_York")).strftime("%H:%M") == "09:53", "")
add("L05", "⑫", "NIKKEI225 最新观测=2026-11-20(截止日无观测,未以旧值充当日值)", "series_store.NIKKEI225 last date", series("NIKKEI225")[-1][0].isoformat(),
    "2026-11-20", series("NIKKEI225")[-1][0].isoformat() == "2026-11-20" and "56436.65,2026-11-20 收盘" in JT, "")

# =====================================================================
# ⑬ 契约验证非 VERIFIED 项
# =====================================================================
vs = CV["verdicts"]
st_ = [v for v in vs if v["status"] != "VERIFIED"]
add("M01", "⑬", "契约逐项判定: 总数/VERIFIED/非 VERIFIED", "report.agent_judgment.contract_verification.verdicts[*].status",
    "%d/%d/%d" % (len(vs), len(vs) - len(st_), len(st_)), "5/4/1", (len(vs), len(vs) - len(st_), len(st_)) == (5, 4, 1), "")
add("M02", "⑬", "STALE 项=ECB_DFR@2026-09-16=2.5(与序列面一致)", "…verdicts[0] / series_store.ECB_DFR[2026-09-16]",
    "%s@%s=%s" % (st_[0]["metric"], FACT["ECB_DFR@2026-09-16"]["observation_date"], val("ECB_DFR", "2026-09-16")) if st_ else "无",
    "ECB_DFR@2026-09-16=2.5", bool(st_) and st_[0]["metric"] == "ECB_DFR" and abs(val("ECB_DFR", "2026-09-16") - st_[0]["value"]) < 1e-9, "")
add("M03", "⑬", "判断档对该 STALE 指标作了披露(指标/观测期/原因)", "判断档 C3/QGN[4] vs facts[ECB_DFR@…].issues",
    "ECB 序列止于 2026-09-16,距截止 68 天,超 10 天阈,DEGRADED", "同左",
    "欧央行序列止于 2026-09-16" in JT and "68 天" in JT and "quality_status=DEGRADED" in JT and "68" in json.dumps(FACT["ECB_DFR@2026-09-16"]["issues"], ensure_ascii=False), "")
for pid, m, d_, rv in (("M04", "JP_POLICY_RATE", "2026-10-01", 1.227), ("M05", "USDJPY", "2026-11-23", 159.35),
                       ("M06", "SPX", "2026-11-23", 7203.85), ("M07", "VIX", "2026-11-23", 27.01)):
    num(pid, "⑬", "契约 VERIFIED 项独立复算 %s@%s" % (m, d_), "series_store.%s[%s]" % (m, d_), val(m, d_), rv, 5e-3)
add("M09", "⑬", "C3「L1 事实行 quality_status=DEGRADED」对两序列均成立", "facts[ECB_MRO@2026-09-16/ECB_DFR@2026-09-16].quality_status",
    "%s/%s" % (FACT["ECB_MRO@2026-09-16"]["quality_status"], FACT["ECB_DFR@2026-09-16"]["quality_status"]), "DEGRADED/DEGRADED",
    FACT["ECB_MRO@2026-09-16"]["quality_status"] == "DEGRADED" and FACT["ECB_DFR@2026-09-16"]["quality_status"] == "DEGRADED", "")
add("M08", "⑬", "契约总体判定(引擎面)", "…contract_verification.verdict", CV["verdict"], "VERIFIED", CV["verdict"] == "VERIFIED",
    "中文数字陈述(如「百分之二点四四」)不进确定性数值绑定,须靠本席独立复算——见 C01/C04")

# =====================================================================
# ⑭ 交付门相关缺口披露 + 杂项
# =====================================================================
add("N01", "⑭", "JP_POLICY_TARGET 缺席格如实呈现为「数据不可得」", "MAP_REPORT.md 缺数格说明 / reader_map.regions[JP]", "数据不可得", "同左",
    "JP_POLICY_TARGET" in MAP_TEXT and "数据不可得" in MAP_TEXT and "注册表无 JP_POLICY_TARGET" in JT, "")
add("N02", "⑭", "缺席未写成「无变化」", "判断档 C1 / regions[JP]", "东京 CPI 去年同月对照不可得、不可判", "同左",
    "去年同月基期观测不可得" in JT and "去年同月对照不可得" in JT, "")
add("N03", "⑭", "欧央行「无未生效决议」结论限定于引擎可见面", "判断档 C2/C3", "仅覆盖引擎可见面【尚未验证】", "同左",
    "仅覆盖引擎可见面" in JT and "其后决议面不可见【尚未验证】" in JT, "BOJ 侧核验覆盖止于 2026-10-30(24 天)未对称标注=MINOR")
add("N04", "⑭", "证据索引行数", "evidence_index.json / 判断档 agent_declaration.basis", len(ev), 60, len(ev) == 60 and "证据索引(60行)" in JT, "")
nonwed = sum(1 for x in mro + dfr if x[0].weekday() != 2)
add("N05", "⑭", "QGN[5]④ 自述: 两 ECB 序列含非周三观测", "series_store.ECB_MRO/ECB_DFR 观测日星期", nonwed, ">0", nonwed > 0, "非周三观测 %d 个(最早 1999-01-01/01-04 等)" % nonwed)
add("N06", "⑭", "QGN[5]⑤ 自述: 引擎报告「截止日−12月/−3月」残留", "MAP_REPORT.md 第 7 行 / research_plan.point_anchors", "截止日−12月/−3月" in MAP_TEXT,
    True, "截止日−12月/−3月" in MAP_TEXT and "截止日−12月/−3月" in JT, "判断档已披露该残留;实际锚=6个月前/最新一期")
regtxt = json.dumps(REG["JP_CPI_YOY"], ensure_ascii=False)
add("N07", "⑭", "「注册表 2025基/2020基 … 同月同比(新基优先,重叠差>0.10pp 告警)」", "metric_registry.metrics[JP_CPI_YOY].calc",
    "新基优先,重叠差>0.10pp 告警" if "新基优先,重叠差>0.10pp 告警" in regtxt else regtxt[:60], "同左", "新基优先,重叠差>0.10pp 告警" in regtxt, "")
add("N08", "⑭", "「spliced」一词是否出自注册表", "metric_registry.json 全文", open(REG_P, encoding="utf-8").read().count("spliced"), ">0(注册表用「拼接」)",
    open(REG_P, encoding="utf-8").read().count("spliced") > 0, "注册表无「spliced」字样(有「拼接」5 处);实质内容相符,仅措辞", sev="NIT")
# ---- 补充面(不计点) ----
def _pw(c):
    x = c["policy_window_path"]
    return x[0] if isinstance(x, list) else x


pwp = {(rg, m): _pw(CELLS[(rg, m)]) for rg, m in (("EA", "ECB_MRO"), ("EA", "ECB_DFR"), ("JP", "JP_POLICY_RATE"))}
add_supp("engine_policy_window_net_bp", {
    "ECB_MRO": {"engine_net_bp": pwp[("EA", "ECB_MRO")]["net_bp"], "window_start_value": pwp[("EA", "ECB_MRO")]["window_start_value"],
                "pre_window_level(series)": m1f, "end": mro[-1][1],
                "note": "net_bp 取窗内首观测(2026-06-17 生效后的 2.4)为起点,未计窗内列出的第一个 +25bp 事件;自窗启前水平 2.15 起算净变动为 +50bp。判断档未引用该净额(只写「两次同幅上调」),不受影响"},
    "ECB_DFR": {"engine_net_bp": pwp[("EA", "ECB_DFR")]["net_bp"], "pre_window_level(series)": e1f, "end": dfr[-1][1]},
    "JP_POLICY_RATE": {"engine_net_bp": pwp[("JP", "JP_POLICY_RATE")]["net_bp"], "judgment_cited": "净 +67bp"}})
add_supp("engine_notes_plan_metrics_missing", {"report.notes": rep["notes"], "cells_status": {(rg + "/" + m): CELLS[(rg, m)]["anchors"]["最新一期"]["status"] for rg, m in PLAN},
                                            "report.md_tail": [l for l in REPMD_TEXT.split("\n") if "地图计划指标缺数" in l][:1],
                                            "note": "引擎注记把六个计划指标全列为「缺数」,而点值格 12 锚全 ok;属引擎面自述矛盾(交付门面),判断档未采信该注记"})
add_supp("facts_on_cutoff_date", {f["fact_id"]: {"value": f["value"], "calc": str(f.get("calc"))[:60]} for f in FACTS if f["observation_date"] == CUT})
add_supp("turning_candidates_engine", [(c["metric_id"], c["from_ym"], c["to_ym"], c["value_before"], c["value_after"], c["delta"]) for c in tc])
