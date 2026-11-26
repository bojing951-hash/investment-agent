#!/usr/bin/python3 -I
# -*- coding: utf-8 -*-
"""patch6: convert the remaining placeholder points of s05_recompute.py into real
claim-vs-computed points (or INFO rows), and stop force-passing placeholders.
usage: /usr/bin/python3 -I s05_patch6.py <s05_recompute.py>
"""
import sys

p = sys.argv[1]
src = open(p, encoding="utf-8").read()
L = src.split("\n")


def idx(key):
    hits = [i for i, x in enumerate(L) if key in x]
    assert len(hits) == 1, (key, hits)
    return hits[0]


# 1 ---------------------------------------------------------------- secC Tokyo base
i = idx('"C1 东京都去年同月读数不在序列内"')
L[i:i + 1] = [
    '    tkb_ = V("JP_CPI_TOKYO_YOY", S(shift_months(tkN[0], -12)))',
    '    add(s, "C1 「东京都去年同月读数不在序列内」属实(去年同月 2025-10 无值;序列首观测 2026-01)", True, tkb_ is None,',
    '        "series_store.JP_CPI_TOKYO_YOY@" + S(shift_months(tkN[0], -12)) + "=缺;首观测 " + S(tkS[0][0]))',
]

# 2 ---------------------------------------------------------------- secF cluster face
i = idx('在引擎聚簇面", "see_info", "see_info"')
L[i:i + 1] = [
    '    c2_ = [c for c in cl if D(c["date_from"]) == D("2026-09-10")]',
    '    add(s, "引擎聚簇面: ECB 2026-09-10 决议簇=单地区事件(不含 8 天后的 BOJ 09-18 决议)", [False, ["EA"]],',
    '        ([c2_[0]["same_event_cross_country"], c2_[0]["regions"]] if c2_ else None), "research_plan.policy_event_clusters POLCLUSTER-02")',
    '    add(s, "判断档未把两地 2026-09 变更并称同一跨地区事件(全文「聚簇」「跨地区事件」出现次数)", 0, T.count("聚簇") + T.count("跨地区事件"), "agent_judgment 全文 vs 引擎单地区聚簇面")',
]

# 3 ---------------------------------------------------------------- secG month-window top jump
i = idx('内 VIX 最大单日跳升日", "see_info"')
L[i:i + 1] = [
    '    info("VIX_month_window_top_daily_jumps", sorted(dpm, key=lambda x: -x[1])[:3], "series_store.VIX 2026-10-23→2026-11-20 日变动%(「窗内两个最大单日跳升日」仅在跳升窗 11-13→11-20 口径成立)")',
    '    v0_, va_, vb_ = V("VIX", D0), V("VIX", "2026-11-13"), V("VIX", D1)',
    '    add(s, "「VIX 跳升集中于 2026-11-13→2026-11-20」(跳升窗净变动/月窗净变动≥0.9)", True,',
    '        ((vb_ is not None) and (va_ is not None) and (v0_ is not None) and ((vb_ - va_) >= 0.9 * (vb_ - v0_))),',
    '        "series_store.VIX %s=%r / 2026-11-13=%r / %s=%r" % (S(D0), v0_, va_, S(D1), vb_))',
]

# 4 ---------------------------------------------------------------- secK calendar counts
i = idx('"冻结日历条目总数/其中非日欧条目数"')
L[i:i + 1] = [
    '    n_jp_ = sum(1 for e in CALE if str(e.get("metric_id")) == "JP_POLICY_TARGET")',
    '    n_ea_ = sum(1 for e in CALE if str(e.get("metric_id")) == "EA_HICP_YOY")',
    '    add(s, "C3③「冻结日历实录仅覆盖日本政策目标两条与三条历史期 EA HICP」(日欧面计数)", [2, 3], [n_jp_, n_ea_], "release_calendar.entries metric_id 计数")',
    '    info("calendar_non_JP_EA_entries", [[e.get("entry_id"), e.get("metric_id"), e.get("obs_from"), e.get("basis")] for e in CALE if str(e.get("metric_id")) not in ("JP_POLICY_TARGET", "EA_HICP_YOY")], "release_calendar.entries(日欧面以外的其余条目;「仅覆盖」未限定地区时的反例)")',
]

# 5 ---------------------------------------------------------------- secK engine sync face
i = idx('"历史同步性主张: 引擎 compare 面为 EA_HICP_YOY×ECB_MRO(无 EA×JP 同步面)"')
L[i:i + 1] = [
    '    s5_ = [x.get("metric_id") for x in ((step_env("S5_compare") or {}).get("data") or {}).get("sides", [])]',
    '    add(s, "引擎地区×维度同步面(S5_compare 两侧)=EA_HICP_YOY×ECB_MRO;判断档同步性表述仅用「同月/先后未定」、未引用跨地区同步系数",',
    '        [sorted(["EA_HICP_YOY", "ECB_MRO"]), 0], [sorted(s5_), len(re.findall(r"相关系数|同步系数|pearson|皮尔逊", T))],',
    '        "steps[S5_compare].envelope.data.sides + agent_judgment 全文")',
    '    info("S5_compare_research_mode_gate", (((step_env("S5_compare") or {}).get("data") or {}).get("alignment") or {}).get("research_mode_gate"), "steps[S5_compare].envelope.data.alignment.research_mode_gate")',
]

# 6 ---------------------------------------------------------------- secL last observation dates
i = idx('"截止日当日最高频观测日=截止日(存在截止日观测的序列数)"')
L[i:i + 1] = [
    '    lastd_ = {m_: S(ser(m_)[-1][0]) for m_ in ("SPX", "VIX", "DAX", "CAC40", "EURUSD", "USDJPY", "DXY", "UST_10Y", "TIPS_10Y", "NIKKEI225")}',
    '    info("last_obs_dates_cited_series", lastd_, "series_store 引用序列末观测日")',
    '    add(s, "判断档标「至 2026-11-23 盘中快照」的七序列末观测日=截止日 2026-11-23", [S(CUTOFF)] * 7,',
    '        [lastd_[m_] for m_ in ("SPX", "VIX", "DAX", "CAC40", "EURUSD", "USDJPY", "DXY")], "series_store 末观测日 vs 判断档「盘中/盘中快照」口径")',
    '    add(s, "截止日当日观测=快照时点日(research_as_of 日期)", S(CUTOFF), S(snap["research_as_of"]), "snapshot.research_as_of vs research_plan.cutoff")',
]

# 7 ---------------------------------------------------------------- secN two engine faces
i = idx('"ECB_MRO 锚格状态=ok 而 data_requirements=insufficient_coverage(引擎内部口径不一,INFO)"')
L[i:i + 1] = [
    '    for mid in ("ECB_MRO", "ECB_DFR"):',
    '        add(s, mid + " 点值格「最新一期」status=ok 而 L1 事实行 quality_status=DEGRADED(引擎 data_requirements 另判 insufficient_coverage)", ["ok", "DEGRADED"],',
    '            [cell(mid)["anchors"]["最新一期"].get("status"), l1row(mid).get("quality_status")], "research_plan.point_values vs layers.L1_事实层")',
    '    add(s, "判断档未沿用引擎「insufficient_coverage/缺数」标签(全文出现次数),改以 Gate A 降级+超阈披露", 0, T.count("insufficient_coverage") + T.count("缺数"), "agent_judgment 全文")',
]

# 8 ---------------------------------------------------------------- secN MAP engine note
i = idx('"MAP_REPORT「ECB 观测日全为周三」属引擎面陈述(实际非周三观测日数,INFO)"')
L[i:i + 1] = [
    '        info("MAP_REPORT_ECB_all_Wednesday_claim", {"map_says_all_wednesday": "ECB_MRO/ECB_DFR 观测日全为周三" in MAPTXT,',
    '             "non_wednesday_obs_dates_total": len(nonwed), "non_wednesday_since_2015": len([d_ for d_ in nonwed if D(d_) >= D("2015-01-01")]),',
    '             "non_wednesday_years": sorted(set(d_[:4] for d_ in nonwed)), "window_obs_dates": [d_ for d_ in ecbs if D(d_) >= D("2025-06-01")]},',
    '             "MAP_REPORT.md 引擎注记行 vs series_store.ECB_MRO/ECB_DFR(引擎面文字,不计入判断档偏离)")',
    '        add(s, "本窗(2025-06 起)ECB 两序列观测日均为周三;判断档未沿用「全为周三」表述", [True, 0],',
    '            [all(D(d_).weekday() == 2 for d_ in ecbs if D(d_) >= D("2025-06-01")), T.count("全为周三")], "series_store.ECB_MRO/ECB_DFR 观测日 + agent_judgment 全文")',
]

# 9 ---------------------------------------------------------------- secO Tokyo 2026-07
i = idx('未在文逐月列出(文内仅列锚格与转折端点,非必需)')
L[i:i + 1] = [
    '                    inT_ = [bool(re.search(r"(?<![\\d.])" + re.escape(("%." + str(k_) + "f") % f(ym)) + r"(?!\\d)", T)) for k_ in (1, 2, 3)]',
    '                    add(s, "窗内逐月值 %s %s 未在文出现(非锚格/转折端点,无需逐月列出;记实)" % (mid, ym), False, any(inT_),',
    '                        "series_store.%s@%s=%s;文内匹配(1/2/3 位小数)=%r" % (mid, ym, f(ym), inT_))',
]

# 10 --------------------------------------------------------------- no force-pass
i = idx('if p["claim"] == "see_info" or p["computed"] == "see_computed":')
assert 'p["ok"] = True' in L[i + 1], L[i + 1]
L[i + 1] = '            p["ok"] = False  # placeholders are never force-passed (patch6)'

out = "\n".join(L)
open(p, "w", encoding="utf-8").write(out)
print("patch6 applied; see_info/see_computed mentions left:", out.count("see_info") + out.count("see_computed"))
