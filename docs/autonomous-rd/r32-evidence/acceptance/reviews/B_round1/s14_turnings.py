#!/usr/bin/python3 -I
"""席位自写脚本 s14: ⑥ 转折候选面独立复算 + ⑧ 历史类比零段(只读).

用法: /usr/bin/python3 -I s14_turnings.py <快照> <report.json> <agent_judgment.json> <席位目录>
候选规则(引擎 basis 原文): 过去12个月(研究截止日)内 3 个月滚动变化绝对值最大者;每指标一候选,窗端点已按发布纪律过滤.
"""
import json
import os
import re
import sys
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seatlib  # noqa: E402
from seatlib import Points, Store, load_json, month_shift, to_date  # noqa: E402

SNAP, REP, AJ, SEAT = sys.argv[1:5]
snap = load_json(SNAP)
rep = load_json(REP)
aj = load_json(AJ)
S = Store(snap)
rp = rep["research_plan"]
SRC = "root_overlay/data/daily/research_snapshot_20261123.json:series_store"
CUT = "2026-11-23"

# 发布规则: 月末+N 天(取自 plan 点值格 publication_rule), 用于窗端点发布纪律
rule_n = {}
for cell in rp["point_values"]["cells"]:
    m = re.search(r"月末\+(\d+)天", cell["anchors"]["最新一期"]["publication_rule"])
    if m:
        rule_n[cell["metric_id"]] = int(m.group(1))


def published_by(ym, mid):
    """该观测月按推定规则是否在截止日前发布."""
    last_day = to_date(month_shift(ym + "-01", 1)) - timedelta(days=1)
    return (last_day + timedelta(days=rule_n[mid])).isoformat() <= CUT


def latest_ok(mid):
    """发布纪律下可用的最新观测月."""
    for ym in reversed([d[:7] for d in S.series(mid)[0]]):
        if ym <= "2026-11" and published_by(ym, mid):
            return ym
    return None


def yoy4(mid, ym):
    v, why = S.yoy(mid, ym)
    return v


P = Points("⑥", "转折候选面: 每指标 3 个月滚动变化最大段(独立重算)与引擎候选逐项比对")
monthly = {
    "CPI": lambda ym: yoy4("CPI", ym),
    "CORE_CPI": lambda ym: yoy4("CORE_CPI", ym),
    "CORE_PCE": lambda ym: yoy4("CORE_PCE", ym),
    "INDPRO": lambda ym: yoy4("INDPRO", ym),
    "UNEMPLOYMENT": lambda ym: S.mval("UNEMPLOYMENT", ym),
    "EA_HICP_YOY": lambda ym: S.mval("EA_HICP_YOY", ym),
    "JP_POLICY_RATE": lambda ym: S.mval("JP_POLICY_RATE", ym),
}
eng = {c["metric_id"]: c for c in rp["turning_candidates"]["candidates"]}
my_pool = {}
for mid, get in monthly.items():
    last = latest_ok(mid)
    best = None
    scan = []
    f = "2025-11"
    while True:
        t = month_shift(f + "-01", 3)[:7]
        if t > last:
            break
        a, b = get(f), get(t)
        if a is not None and b is not None:
            d = b - a
            scan.append((f, t, round(a, 4), round(b, 4), round(d, 4)))
            if best is None or abs(d) > abs(best[4]):
                best = (f, t, a, b, d)
        f = month_shift(f + "-01", 1)[:7]
    my_pool[mid] = best
    mx = max(abs(r[4]) for r in scan)
    tied = [(r[0], r[1]) for r in scan if abs(abs(r[4]) - mx) < 1e-9]
    e = eng.get(mid)
    if e is None:
        P.rows.append({"block": "⑥", "id": f"T0-{mid} 引擎候选池未列该指标", "source": "report.json:research_plan.turning_candidates.candidates", "kind": "probe",
                       "computed": None, "claim": "每指标一候选", "match": None,
                       "detail": f"独立重算最大段 {best[0]}→{best[1]} {round(best[2], 4)}→{round(best[3], 4)} Δ{round(best[4], 4)} (留档, 非受审稿数字)"})
        continue
    P.add_bool(f"T1-{mid} 候选窗 {e['from_ym']}→{e['to_ym']} 与独立重算最大段一致", True,
               (e["from_ym"], e["to_ym"]) in tied, f"{SRC}.{mid}(3 个月滚动差; 窗端点发布纪律过滤)",
               f"独立重算最大段(含并列) {tied}; 引擎 {e['from_ym']}→{e['to_ym']}" + ("" if len(tied) == 1 else f"; 并列 {len(tied)} 窗, 引擎取较近窗(并列裁决, 非错)"))
    P.add(f"T2-{mid} 候选 value_before", e["value_before"], best[2], f"{SRC}.{mid}[{e['from_ym']}]", nd=4)
    P.add(f"T3-{mid} 候选 value_after", e["value_after"], best[3], f"{SRC}.{mid}[{e['to_ym']}]", nd=4)
    P.add(f"T4-{mid} 候选 delta(=四位小数端点之差, 引擎面口径)", e["delta"], round(best[3], 4) - round(best[2], 4),
          f"{SRC}.{mid}[{e['from_ym']}..{e['to_ym']}]", f"未取端点直差 {best[4]:.6f}", nd=4)
P.add_bool("T5-引擎候选池条数=7(与受审稿「候选池7」一致)", True, len(eng) == 7, "report.json:research_plan.turning_candidates.candidates", f"条数 {len(eng)}")
order = sorted(eng.values(), key=lambda c: -abs(c["delta"]))
P.add_bool("T6-候选池按 |delta| 降序 = CPI 1.7326 > EA_HICP_YOY 1.3 > INDPRO 0.9571 > CORE_CPI 0.3767 > JP_POLICY_RATE 0.251 > CORE_PCE 0.238 > UNEMPLOYMENT 0.2", True,
           [c["metric_id"] for c in order] == ["CPI", "EA_HICP_YOY", "INDPRO", "CORE_CPI", "JP_POLICY_RATE", "CORE_PCE", "UNEMPLOYMENT"]
           and [round(c["delta"], 4) for c in order] == [1.7326, 1.3, -0.9571, -0.3767, 0.251, 0.238, -0.2],
           "report.json:research_plan.turning_candidates.candidates[*].delta")
P.add_bool("T7-受审稿 top3 所述「CPI 2.434→4.1666 为候选池内最大单段变动」", True,
           abs(eng["CPI"]["delta"]) == max(abs(c["delta"]) for c in eng.values()), "report.json:research_plan.turning_candidates.candidates")
P.add_bool("T8-受审稿「INDPRO 为增长维候选池内最大的三个月变化」", True,
           abs(eng["INDPRO"]["delta"]) == max(abs(c["delta"]) for c in eng.values() if c["dimension"] == "growth"),
           "report.json:research_plan.turning_candidates.candidates[dimension=growth]")
P.add_bool("T9-top_n_expected=3 且转折表 3 项(与受审稿「top3」/三转折一致)", True,
           rp["turning_candidates"]["top_n_expected"] == 3 and len(aj["reader_map"]["turnings"]) == 3,
           "report.json:research_plan.turning_candidates.top_n_expected; agent_judgment.json:reader_map.turnings")
turn_m = [t["metric_id"] for t in aj["reader_map"]["turnings"]]
P.add_bool("T10-转折表三项指标(CPI/INDPRO/JP_POLICY_RATE)均在候选池内且分属通胀/增长/政策三维(不同事件)", True,
           all(m in eng for m in turn_m) and len(set(eng[m]["dimension"] for m in turn_m)) == 3,
           "agent_judgment.json:reader_map.turnings[*].metric_id; report.json:…candidates[*].dimension")
P.save("points_06_turnings.json")

# ---------------------------------------------------------------- 转折叙述中的数字
P = Points("⑥", "转折表叙述数字回贴")
T = {t["metric_id"]: t for t in aj["reader_map"]["turnings"]}
P.add("N1-CPI 同比 2026-02", 2.434, yoy4("CPI", "2026-02"), f"{SRC}.CPI[2026-02-01, 2025-02-01]")
P.add("N2-CPI 同比 2026-05", 4.1666, yoy4("CPI", "2026-05"), f"{SRC}.CPI[2026-05-01, 2025-05-01]", nd=4)
P.add("N3-EA_HICP_YOY 2026-05", 3.2, S.mval("EA_HICP_YOY", "2026-05"), f"{SRC}.EA_HICP_YOY[2026-05-01]")
P.add("N4-EA_HICP_YOY 2026-06", 2.8, S.mval("EA_HICP_YOY", "2026-06"), f"{SRC}.EA_HICP_YOY[2026-06-01]")
P.add("N5-EA_HICP_YOY 2026-07", 2.9, S.mval("EA_HICP_YOY", "2026-07"), f"{SRC}.EA_HICP_YOY[2026-07-01]")
P.add("N6-EA_HICP_YOY 2026-10", 4.0, S.mval("EA_HICP_YOY", "2026-10"), f"{SRC}.EA_HICP_YOY[2026-10-01]")
P.add_bool("N7-「2026-10 的 4.0 越过 2026-05 的 3.2」", True, S.mval("EA_HICP_YOY", "2026-10") > S.mval("EA_HICP_YOY", "2026-05"),
           f"{SRC}.EA_HICP_YOY[2026-05-01, 2026-10-01]")
P.add("N8-CORE_CPI 同比 2026-02", 2.4725, yoy4("CORE_CPI", "2026-02"), f"{SRC}.CORE_CPI[2026-02-01, 2025-02-01]", nd=4)
P.add("N9-CORE_CPI 同比 2026-05", 2.8229, yoy4("CORE_CPI", "2026-05"), f"{SRC}.CORE_CPI[2026-05-01, 2025-05-01]", nd=4)
P.add_bool("N10-「同窗核心涨幅小于 headline」", True,
           (yoy4("CORE_CPI", "2026-05") - yoy4("CORE_CPI", "2026-02")) < (yoy4("CPI", "2026-05") - yoy4("CPI", "2026-02"))
           and (yoy4("CORE_CPI", "2026-05") - yoy4("CORE_CPI", "2026-02")) > 0,
           f"{SRC}.CORE_CPI/CPI[2026-02, 2026-05]", f"核心 Δ{yoy4('CORE_CPI', '2026-05') - yoy4('CORE_CPI', '2026-02'):.4f} < headline Δ{yoy4('CPI', '2026-05') - yoy4('CPI', '2026-02'):.4f}")
P.add("N11-CORE_CPI 同比 2026-08", 2.4462, yoy4("CORE_CPI", "2026-08"), f"{SRC}.CORE_CPI[2026-08-01, 2025-08-01]", nd=4)
P.add("N12-CORE_CPI 同比 2026-09(四位)", 2.5658, yoy4("CORE_CPI", "2026-09"), f"{SRC}.CORE_CPI[2026-09-01, 2025-09-01]", nd=4)
P.add("N13-EA_HICP_YOY 同窗上行(百分点)", 1.3, S.mval("EA_HICP_YOY", "2026-05") - S.mval("EA_HICP_YOY", "2026-02"), f"{SRC}.EA_HICP_YOY[2026-02-01, 2026-05-01]")
P.add("N14-INDPRO 同比 2025-11", 1.7543, yoy4("INDPRO", "2025-11"), f"{SRC}.INDPRO[2025-11-01, 2024-11-01]", nd=4)
P.add("N15-INDPRO 同比 2026-02", 0.7972, yoy4("INDPRO", "2026-02"), f"{SRC}.INDPRO[2026-02-01, 2025-02-01]", nd=4)
P.add("N16-INDPRO 三个月变化(百分点)", -0.9571, yoy4("INDPRO", "2026-02") - yoy4("INDPRO", "2025-11"), f"{SRC}.INDPRO[2025-11..2026-02]", nd=4)
P.add("N17-失业率 2025-11", 4.5, S.mval("UNEMPLOYMENT", "2025-11"), f"{SRC}.UNEMPLOYMENT[2025-11-01]")
P.add("N18-失业率 2026-02", 4.4, S.mval("UNEMPLOYMENT", "2026-02"), f"{SRC}.UNEMPLOYMENT[2026-02-01]")
P.add_bool("N19-「就业端未同向走弱」(同窗失业率下降)", True, S.mval("UNEMPLOYMENT", "2026-02") < S.mval("UNEMPLOYMENT", "2025-11"),
           f"{SRC}.UNEMPLOYMENT[2025-11-01, 2026-02-01]")
ind26 = [(ym, yoy4("INDPRO", ym)) for ym in (f"2026-{m:02d}" for m in range(1, 11))]
trough = min(ind26, key=lambda x: x[1])
P.add_bool("N20-「2026-03 见底后回升」: INDPRO 同比 2026 年内低点=2026-03, 其后各月均高于低点", True,
           trough[0] == "2026-03" and all(v > trough[1] for _, v in ind26 if _ > "2026-03") and ind26[-1][1] > trough[1],
           f"{SRC}.INDPRO[2026-01..2026-10]", "逐月同比(非单调, 06/07 回落但高于低点) " + ", ".join(f"{a}:{b:.2f}" for a, b in ind26))
P.add("N21-INDPRO 同比 2026-10", 2.15, yoy4("INDPRO", "2026-10"), f"{SRC}.INDPRO[2026-10-01, 2025-10-01]")
P.add("N22-JP_POLICY_RATE 2026-04", 0.727, S.mval("JP_POLICY_RATE", "2026-04"), f"{SRC}.JP_POLICY_RATE[2026-04-01]")
P.add("N23-JP_POLICY_RATE 2026-07", 0.978, S.mval("JP_POLICY_RATE", "2026-07"), f"{SRC}.JP_POLICY_RATE[2026-07-01]")
P.add("N24-JP_POLICY_RATE 2026-06(过渡)", 0.841, S.mval("JP_POLICY_RATE", "2026-06"), f"{SRC}.JP_POLICY_RATE[2026-06-01]")
jpm = {ym: S.mval("JP_POLICY_RATE", ym) for ym in [f"2025-{m:02d}" for m in range(10, 13)] + [f"2026-{m:02d}" for m in range(1, 11)]}
steps26 = [(ym, round((jpm[ym] - jpm[month_shift(ym + "-01", -1)[:7]]) * 100)) for ym in sorted(jpm) if ym >= "2026-01" and jpm[ym] - jpm[month_shift(ym + "-01", -1)[:7]] > 0.0005]
P.add_bool("N25-「2026 年内第三个上行月均台阶(此前 2026-01 +17bp、2026-06 +11bp)」", True,
           [s[0] for s in steps26] == ["2026-01", "2026-06", "2026-07", "2026-09", "2026-10"] and steps26[:3] == [("2026-01", 17), ("2026-06", 11), ("2026-07", 14)],
           f"{SRC}.JP_POLICY_RATE[2025-09..2026-10]", "2026 年上行台阶(取整 bp): " + str(steps26))
P.add("N26-JP_POLICY_RATE 2026-09", 1.043, S.mval("JP_POLICY_RATE", "2026-09"), f"{SRC}.JP_POLICY_RATE[2026-09-01]")
P.add("N27-JP_POLICY_RATE 2026-10", 1.227, S.mval("JP_POLICY_RATE", "2026-10"), f"{SRC}.JP_POLICY_RATE[2026-10-01]")
P.add("N28-台阶 2026-09 变动(bp, 整数)", 7, (S.mval("JP_POLICY_RATE", "2026-09") - S.mval("JP_POLICY_RATE", "2026-08")) * 100, f"{SRC}.JP_POLICY_RATE[2026-08-01, 2026-09-01]", nd=0)
P.add("N29-台阶 2026-10 变动(bp, 整数)", 18, (S.mval("JP_POLICY_RATE", "2026-10") - S.mval("JP_POLICY_RATE", "2026-09")) * 100, f"{SRC}.JP_POLICY_RATE[2026-09-01, 2026-10-01]", nd=0)
P.save("points_06b_turning_numbers.json")

# ---------------------------------------------------------------- ⑧ 历史类比零段
P = Points("⑧", "历史类比: 零段呈现(不以事后冒充预测)")
hm = aj["reader_map"]
P.add_bool("H1-reader_map.history_periods 为空数组", True, hm.get("history_periods") == [], "agent_judgment.json:reader_map.history_periods")
P.add_bool("H2-history_zero_case_note 非空且写明「事后结果≠当时可知」「相似≠因果≠预测」", True,
           isinstance(hm.get("history_zero_case_note"), str) and ("事后结果≠当时可知" in hm["history_zero_case_note"]) and ("相似≠因果≠预测" in hm["history_zero_case_note"]),
           "agent_judgment.json:reader_map.history_zero_case_note")
analog_months = set()
for st in rep["steps"]:
    if st.get("step") == "S6_analog":
        data = st.get("envelope", {}).get("data", {})
        for c in data.get("top", []) or []:
            if isinstance(c, dict) and isinstance(c.get("candidate_month"), str):
                analog_months.add(c["candidate_month"])
aj_txt = json.dumps(aj, ensure_ascii=False)
P.add_bool("H3-引擎 analog 候选面在场(S6_analog 执行 ok, top 候选月非空)且受审稿全文未引用任何候选月", True,
           any(st.get("step") == "S6_analog" and st.get("ok") for st in rep["steps"]) and len(analog_months) >= 3
           and not any(m in aj_txt for m in analog_months),
           "report.json:steps[S6_analog].ok/.envelope.data.top[*].candidate_month; agent_judgment.json(全文)",
           f"analog top 候选月 {sorted(analog_months)}")
P.save("points_08_history.json")
