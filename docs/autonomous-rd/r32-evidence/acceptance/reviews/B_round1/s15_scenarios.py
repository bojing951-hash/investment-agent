#!/usr/bin/python3 -I
"""席位自写脚本 s15: ⑨ 情景(触发/证伪/期限与截止日读数相容)(只读复算).

用法: /usr/bin/python3 -I s15_scenarios.py <快照> <report.json> <agent_judgment.json> <席位目录>
"""
import os
import re
import sys
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seatlib  # noqa: E402
from seatlib import Points, Store, load_json, month_shift, to_date, days_between  # noqa: E402

SNAP, REP, AJ, SEAT = sys.argv[1:5]
snap = load_json(SNAP)
rep = load_json(REP)
aj = load_json(AJ)
S = Store(snap)
rp = rep["research_plan"]
SRC = "root_overlay/data/daily/research_snapshot_20261123.json:series_store"
CUT = "2026-11-23"
sc = {s["id"]: s["rows"] for s in aj["l4"]["scenarios"]}
S1, S2 = sc["S1-INFL-STICKY"], sc["S2-INFL-FADE"]
rule_n = {}
for cell in rp["point_values"]["cells"]:
    m = re.search(r"月末\+(\d+)天", cell["anchors"]["最新一期"]["publication_rule"])
    if m:
        rule_n[cell["metric_id"]] = int(m.group(1))


def rel_date(mid, ym):
    last_day = to_date(month_shift(ym + "-01", 1)) - timedelta(days=1)
    return (last_day + timedelta(days=rule_n[mid])).isoformat()


def latest_pub_value(mid, asof):
    """截止日前已发布的最新观测月及其同比/值."""
    best = None
    for d in S.series(mid)[0]:
        ym = d[:7]
        if rel_date(mid, ym) <= asof:
            best = ym
    if mid in ("CORE_PCE",):
        v, why = S.yoy(mid, best)
        return best, v
    return best, S.mval(mid, best)


P = Points("⑨", "情景: 规则发布日/期限/触发与证伪阈值对截止日读数的相容性")
ea_ym, ea_v = latest_pub_value("EA_HICP_YOY", CUT)
pce_ym, pce_v = latest_pub_value("CORE_PCE", CUT)
tips_v = S.le("TIPS_10Y", CUT)[1]
bei_v = S.le("BEI_10Y", CUT)[1]
P.add("S0-截止日前已发布 EA_HICP_YOY 最新观测月", 202610, int(ea_ym.replace("-", "")), f"{SRC}.EA_HICP_YOY; 规则月末+{rule_n['EA_HICP_YOY']}天", nd=0)
P.add("S0b-EA_HICP_YOY 最新值", 4.0, ea_v, f"{SRC}.EA_HICP_YOY[{ea_ym}-01]")
P.add("S0c-截止日前已发布 CORE_PCE 同比最新值", 3.12, pce_v, f"{SRC}.CORE_PCE[{pce_ym}-01 同比]")
P.add("S0d-TIPS_10Y 最新值", 2.88, tips_v, f"{SRC}.TIPS_10Y[≤{CUT}]")
P.add("S0e-BEI_10Y 最新值", 2.15, bei_v, f"{SRC}.BEI_10Y[≤{CUT}]")
for obs, rel in (("2026-11", "2026-12-16"), ("2026-12", "2027-01-16"), ("2027-01", "2027-02-16")):
    got = rel_date("EA_HICP_YOY", obs)
    P.rows.append({"block": "⑨", "id": f"S1-EA_HICP_YOY 观测月 {obs} 的规则发布日", "source": f"report.json:research_plan.point_values.cells[EA_HICP_YOY].anchors.最新一期.publication_rule(月末+{rule_n['EA_HICP_YOY']}天,推定)",
                   "kind": "point", "computed": got, "claim": rel, "match": got == rel, "detail": f"{obs} 月末+{rule_n['EA_HICP_YOY']}天 = {got}; 受审稿 {rel}"})
P.add_bool("S2-「2027-01 观测月的规则发布日 2027-02-16 晚于期限 2027-02-15」", True, rel_date("EA_HICP_YOY", "2027-01") > "2027-02-15",
           "agent_judgment.json:l4.scenarios[S1].rows.scenario; 规则月末+16天", f"{rel_date('EA_HICP_YOY', '2027-01')} > 2027-02-15")
P.add_bool("S3-「规则发布日 2026-12-16、2027-01-16,均不晚于期限 2027-02-15」", True,
           rel_date("EA_HICP_YOY", "2026-11") <= "2027-02-15" and rel_date("EA_HICP_YOY", "2026-12") <= "2027-02-15",
           "agent_judgment.json:l4.scenarios[S1].rows.falsification.threshold")
P.add_bool("S4-两情景期限均为 2027-02-15", True,
           S1["trigger"]["deadline"] == "2027-02-15" and S2["trigger"]["deadline"] == "2027-02-15",
           "agent_judgment.json:l4.scenarios[*].rows.trigger.deadline")
# 截止日读数下触发/证伪状态
s1_trig = (ea_v >= 4.2) and (pce_v >= 3.2) and (tips_v > 3.0)
s2_trig = (ea_v <= 3.4) and (bei_v < 2.0)
P.add_bool("S5-S1 触发条件(EA≥4.2% 且 CORE_PCE≥3.2% 且 TIPS_10Y>3.0%)在截止日读数下未触发", True, not s1_trig,
           f"{SRC}.EA_HICP_YOY/CORE_PCE/TIPS_10Y", f"EA {ea_v} / CORE_PCE {pce_v} / TIPS {tips_v}")
P.add_bool("S6-S2 触发条件(EA≤3.4% 且 BEI_10Y<2.0%)在截止日读数下未触发", True, not s2_trig,
           f"{SRC}.EA_HICP_YOY/BEI_10Y", f"EA {ea_v} / BEI {bei_v}")
P.add_bool("S7-S1 证伪线(连续两月 <3.0%)在截止日读数下未触发(最新 4.0≥3.0)", True, ea_v >= 3.0, f"{SRC}.EA_HICP_YOY[{ea_ym}-01]")
tgt = ["2026-11", "2026-12"]  # S2 证伪所需的两次发布对应观测月
avail = [ym for ym in tgt if rel_date("EA_HICP_YOY", ym) <= CUT]
P.add("S8-S2 证伪所需的 2026-11/2026-12 观测月在截止日已发布数(前瞻条件, 截止日尚不可判=相容)", 0, len(avail),
      f"{SRC}.EA_HICP_YOY; 规则月末+{rule_n['EA_HICP_YOY']}天", f"发布日 {[rel_date('EA_HICP_YOY', y) for y in tgt]} 均晚于截止日", nd=0)
P.add_bool("S9-S1 情景陈述界(EA≥3.5%、CORE_PCE≥3.0%)与截止日读数相容", True, ea_v >= 3.5 and pce_v >= 3.0,
           f"{SRC}.EA_HICP_YOY/CORE_PCE", "S1=延续假设; 当前读数在界内")
P.add_bool("S10-两情景在区分指标 EA_HICP_YOY 上的预言方向相反(S1≥3.5% 对 S2<3.0%)", True,
           ("3.5% 以上" in S1["scenario"]) and ("3.0% 以下" in S2["scenario"]),
           "agent_judgment.json:l4.scenarios[*].rows.scenario")
# 阈值内部一致性: 情景陈述/证伪/触发三处的数字
t1 = f"{S1['scenario']}|{S1['falsification']['threshold']}|{S1['trigger']['condition']}"
t2 = f"{S2['scenario']}|{S2['falsification']['threshold']}|{S2['trigger']['condition']}"
P.add_bool("S11-S1 证伪线 3.0% 在陈述与证伪两处一致; 缓冲带 3.0–3.5%", True, t1.count("3.0%") >= 2 and "3.5%" in t1, "agent_judgment.json:l4.scenarios[S1]")
P.add_bool("S12-S2 触发线 3.4%/证伪线 4.0%/陈述界 3.0% 在三处一致", True, ("≤3.4%" in t2) and ("4.0%" in t2) and t2.count("3.0%") >= 2, "agent_judgment.json:l4.scenarios[S2]")
P.add_bool("S13-两情景缓冲带互不重叠地定义了「既未触发也未证伪」区间(S1: 3.0–3.5; S2: 3.0–4.0)", True,
           ("3.0% 至 3.5% 之间为缓冲带" in S1["falsification"]["threshold"]) and ("3.0% 至 4.0% 之间为缓冲带" in S2["falsification"]["threshold"]),
           "agent_judgment.json:l4.scenarios[*].rows.falsification.threshold")
# 可观测性: 被点名指标须在证据面在场
need = ["EA_HICP_YOY", "CORE_PCE", "TIPS_10Y", "BEI_10Y", "JP_POLICY_RATE", "SPX"]
P.add_bool("S14-情景点名的区分/敏感指标(EA_HICP_YOY/CORE_PCE/TIPS_10Y/BEI_10Y/JP_POLICY_RATE/SPX)均在冻结 series_store 在场", True,
           all(S.has(m) for m in need), f"{SRC}", str([m for m in need if not S.has(m)]))
P.add_bool("S15-S2 所述「与近一月观察(实际利率 +11bp 而风险资产回落)相反」: S2 方向为实际利率回落/风险资产修复, 与观察相反", True,
           ("通胀补偿与实际利率双双回落,风险资产修复" in S2["asset_direction"]["direction"]),
           "agent_judgment.json:l4.scenarios[S2].rows.asset_direction.direction; series_store.TIPS_10Y(+11bp)/SPX(回落)")
P.add_bool("S16-S1/S2 资产方向预言相反(利率敏感资产: 走弱 对 修复; 美元: 偏强 对 走弱)", True,
           ("美元指数相对非美货币偏强" in S1["asset_direction"]["direction"]) and ("美元走弱" in S2["asset_direction"]["direction"]),
           "agent_judgment.json:l4.scenarios[*].rows.asset_direction.direction")
six = aj.get("contract_verification", {}).get("six_checks", []) or load_json(os.path.join(SEAT, "x_agent_judgment_meta.json"))["contract_verification"]["six_checks"]
P.add_bool("S17-引擎契约 six_checks: 两情景 overreach/falsifiable 均 VERIFIED", True,
           all(c["status"] == "VERIFIED" for c in six if c["item"].startswith("S")) and len([c for c in six if c["item"].startswith("S")]) == 4,
           "x_agent_judgment_meta.json:contract_verification.six_checks[item=S1/S2]")
P.save("points_09_scenarios.json")
