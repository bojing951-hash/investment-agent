#!/usr/bin/python3 -I
"""s11_policy.py — ④政策面(决议/生效/目标/距上次调整/月均口径) + ⑬契约STALE披露 + ⑭Gate A 缺口披露.
用法: /usr/bin/python3 -I s11_policy.py <冻结快照> <冻结日历> <注册表> <agent_judgment.json> <report.json> <席位目录>
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seatlib as L  # noqa: E402

snap_path, cal_path, reg_path, aj_path, rp_path, out_dir = sys.argv[1:7]
snap, cal, reg, aj, rp = (L.load_json(p) for p in (snap_path, cal_path, reg_path, aj_path, rp_path))
st = L.Store(snap)
CUT = "2026-11-23"
SRC = "root_overlay/data/daily/research_snapshot_20261123.json"
CAL = "root_overlay/config/release_calendar.json"
REG = "root_overlay/config/metric_registry.json"

# ---------------------------------------------------------------- ④ 政策面
P = L.Points("④", "政策面: 冻结日历条目/距上次调整/月均口径台阶")
ents = {e["entry_id"]: e for e in cal["entries"]}
e1 = ents.get("RC-JP-BOJ-TARGET-2026-09")
e2 = ents.get("RC-JP-BOJ-MAINT-2026-10")
P.rows.append({"block": "④", "id": "D1-RC-JP-BOJ-TARGET-2026-09 在场且 kind=policy_decision",
               "source": CAL + ":entries[entry_id=RC-JP-BOJ-TARGET-2026-09]",
               "computed": (e1["kind"] if e1 else None), "claim": "policy_decision",
               "match": bool(e1) and e1.get("kind") == "policy_decision", "detail": json.dumps(e1, ensure_ascii=False)})
P.rows.append({"block": "④", "id": "D1-决议日 decision_date", "source": CAL + ":RC-JP-BOJ-TARGET-2026-09.decision_date",
               "computed": e1["decision_date"], "claim": "2026-09-18", "match": e1["decision_date"] == "2026-09-18", "detail": "直算/直读"})
P.rows.append({"block": "④", "id": "D1-生效日 effective_on", "source": CAL + ":RC-JP-BOJ-TARGET-2026-09.effective_on",
               "computed": e1["effective_on"], "claim": "2026-09-24", "match": e1["effective_on"] == "2026-09-24", "detail": "直读"})
P.add("D1-目标水平 target_value(约一点二五)", 1.25, e1["target_value"], CAL + ":RC-JP-BOJ-TARGET-2026-09.target_value")
P.rows.append({"block": "④", "id": "D1-公告可见日 first_publish_on_or_after=决议日", "source": CAL + ":RC-JP-BOJ-TARGET-2026-09.first_publish_on_or_after",
               "computed": e1["first_publish_on_or_after"], "claim": "2026-09-18", "match": e1["first_publish_on_or_after"] == "2026-09-18", "detail": "直读"})
P.rows.append({"block": "④", "id": "D1-决议日≤截止日(可引用)", "source": CAL + ":RC-JP-BOJ-TARGET-2026-09",
               "computed": e1["decision_date"] <= CUT and e1["effective_on"] <= CUT, "claim": True, "match": e1["decision_date"] <= CUT and e1["effective_on"] <= CUT,
               "detail": f"decision {e1['decision_date']} / effective {e1['effective_on']} vs cutoff {CUT}"})
P.rows.append({"block": "④", "id": "D2-RC-JP-BOJ-MAINT-2026-10 在场且 kind=policy_maintenance", "source": CAL + ":entries[entry_id=RC-JP-BOJ-MAINT-2026-10]",
               "computed": (e2["kind"] if e2 else None), "claim": "policy_maintenance", "match": bool(e2) and e2.get("kind") == "policy_maintenance", "detail": json.dumps(e2, ensure_ascii=False)})
P.rows.append({"block": "④", "id": "D2-确认维持日 2026-10-30", "source": CAL + ":RC-JP-BOJ-MAINT-2026-10.decision_date",
               "computed": e2["decision_date"], "claim": "2026-10-30", "match": e2["decision_date"] == "2026-10-30", "detail": "直读"})
P.add("D2-维持条目目标水平", 1.25, e2["target_value"], CAL + ":RC-JP-BOJ-MAINT-2026-10.target_value")
P.rows.append({"block": "④", "id": "D2-维持条目无生效日(正文不为其挂生效日)", "source": CAL + ":RC-JP-BOJ-MAINT-2026-10",
               "computed": ("effective_on" in e2), "claim": False, "match": ("effective_on" not in e2), "detail": f"键集={list(e2.keys())}"})
# 距上次调整天数
d_eff = L.days_between(e1["effective_on"], CUT)
d_dec = L.days_between(e1["decision_date"], CUT)
d_mnt = L.days_between(e2["decision_date"], CUT)
P.rows.append({"block": "④", "id": "D3-距上次调整(按生效日 2026-09-24→截止日)天数", "source": CAL + ":RC-JP-BOJ-TARGET-2026-09.effective_on ; 快照 research_as_of",
               "computed": d_eff, "claim": 60, "match": d_eff == 60, "detail": "日历日直算"})
P.rows.append({"block": "④", "id": "D3-距上次调整(按决议日 2026-09-18→截止日)天数", "source": CAL + ":RC-JP-BOJ-TARGET-2026-09.decision_date",
               "computed": d_dec, "claim": 66, "match": d_dec == 66, "detail": "日历日直算"})
P.rows.append({"block": "④", "id": "D3-距确认维持(2026-10-30→截止日)天数=24(其后日历无条目)", "source": CAL + ":RC-JP-BOJ-MAINT-2026-10.decision_date",
               "computed": d_mnt, "claim": 24, "match": d_mnt == 24, "detail": "日历日直算"})
# 维持后至截止日日历是否有新条目
pol = [e for e in cal["entries"] if e.get("kind") in ("policy_decision", "policy_maintenance")]
later = [e["entry_id"] for e in pol if e.get("decision_date", "") > "2026-10-30"]
P.rows.append({"block": "④", "id": "D4-日历政策条目共 2 条且均为日本央行实录; 维持后无新条目", "source": CAL + ":entries(kind=policy_*)",
               "computed": [e["entry_id"] for e in pol], "claim": ["RC-JP-BOJ-TARGET-2026-09", "RC-JP-BOJ-MAINT-2026-10"],
               "match": [e["entry_id"] for e in pol] == ["RC-JP-BOJ-TARGET-2026-09", "RC-JP-BOJ-MAINT-2026-10"] and not later,
               "detail": f"政策条目={[e['entry_id'] for e in pol]}; metric_ids={sorted({e.get('metric_id') for e in pol})}; 2026-10-30 之后的新条目={later}"})
P.rows.append({"block": "④", "id": "D4-冻结日历无美欧决议/生效实录条目", "source": CAL + ":entries",
               "computed": sorted({e.get("metric_id") for e in pol}), "claim": ["JP_POLICY_TARGET"], "match": sorted({e.get("metric_id") for e in pol}) == ["JP_POLICY_TARGET"],
               "detail": "政策条目 metric_id 集合"})
P.rows.append({"block": "④", "id": "D4-冻结日历版本 v1.5.0", "source": CAL + ":version", "computed": cal["version"], "claim": "1.5.0", "match": cal["version"] == "1.5.0", "detail": "直读"})
# JP_POLICY_RATE 月均序列
rows = st.monthly("JP_POLICY_RATE", n=13)
m = dict(rows)
P.rows.append({"block": "④", "id": "D5-JP_POLICY_RATE 月均 2025-11..2026-10 逐月值", "source": SRC + ":series_store.JP_POLICY_RATE",
               "computed": rows, "claim": {"2025-11": 0.478, "2025-12": 0.557, "2026-01": 0.728, "2026-06": 0.841, "2026-07": 0.978, "2026-09": 1.043, "2026-10": 1.227, "2026-08": 0.977, "2026-04": 0.727},
               "match": all(abs(m[k] - v) < 1e-9 for k, v in {"2025-11": 0.478, "2025-12": 0.557, "2026-01": 0.728, "2026-06": 0.841, "2026-07": 0.978, "2026-09": 1.043, "2026-10": 1.227, "2026-08": 0.977, "2026-04": 0.727}.items()),
               "detail": "受审稿引用月逐月对账"})
chg = []
yms = [ym for ym, _ in rows]
for i in range(1, len(rows)):
    chg.append((yms[i], rows[i - 1][1], rows[i][1], round((rows[i][1] - rows[i - 1][1]) * 100, 2)))
P.rows.append({"block": "④", "id": "D5-月均相邻变动点(bp)", "source": SRC + ":series_store.JP_POLICY_RATE(相邻月差)",
               "computed": chg, "claim": "2025-12 +8; 2026-01 +17; 2026-06 +11; 2026-07 +14; 2026-09 +7; 2026-10 +18",
               "match": [c for c in chg if abs(c[3]) >= 0.5] and [(c[0], round(c[3])) for c in chg if abs(c[3]) >= 0.5] == [("2025-12", 8), ("2026-01", 17), ("2026-06", 11), ("2026-07", 14), ("2026-09", 7), ("2026-10", 18)],
               "detail": "变动点(≥0.5bp)逐点"})
net = (m["2026-10"] - m["2025-11"]) * 100
P.add("D5-12 个月政策窗净变动(bp): 2025-11 月均→2026-10 月均", 75, net, SRC + ":series_store.JP_POLICY_RATE[2026-10]-[2025-11]", nd=0)
P.add("D5-仅自窗内首观测 2025-12 月均起算(bp)", 67, (m["2026-10"] - m["2025-12"]) * 100, SRC + ":series_store.JP_POLICY_RATE[2026-10]-[2025-12]", nd=0)
sum_pts = sum(c[3] for c in chg if abs(c[3]) >= 0.5)
sum_int = sum(int(round(c[3])) for c in chg if abs(c[3]) >= 0.5)
npts = len([c for c in chg if abs(c[3]) >= 0.5])
P.rows.append({"block": "④", "id": "D5-净变动=窗内六个变动点之和(按所述整数 bp 精度)", "source": SRC + ":series_store.JP_POLICY_RATE(变动点求和)",
               "computed": {"六点整数bp之和": sum_int, "变动点数": npts, "端点差取整": int(round(net))},
               "claim": {"sum": 75, "n": 6},
               "match": sum_int == 75 and npts == 6 and int(round(net)) == 75,
               "detail": f"整数 bp: 8+17+11+14+7+18={sum_int}; 端点差 {net:.4f}bp→{int(round(net))}; 变动点数={npts}"})
# 精度注记(非偏离): 六点两位小数直和与端点差之差来自阈值下漂移
sub = [(yms[i], round((rows[i][1] - rows[i - 1][1]) * 100, 4)) for i in range(1, len(rows)) if 0 < abs((rows[i][1] - rows[i - 1][1]) * 100) < 0.5]
P.rows.append({"block": "④", "id": "D5-注记: 六点两位小数直和 75.1bp vs 端点差 74.9bp(阈值下漂移)", "source": SRC + ":series_store.JP_POLICY_RATE",
               "computed": {"六点两位小数直和(bp)": round(sum_pts, 2), "端点差(bp)": round(net, 2), "阈值下漂移(bp)": sub},
               "claim": "恒等仅在整数 bp 显示精度成立", "match": True,
               "detail": f"直和 {sum_pts:.2f} − 端点差 {net:.2f} = {sum_pts - net:.2f}bp; 阈值下漂移={sub}(计入 NIT, 不计偏离)"})
# 平台月份带宽
flat = [(yms[i], round((rows[i][1] - rows[i - 1][1]) * 100, 4)) for i in range(1, len(rows)) if yms[i] in ("2026-03", "2026-04", "2026-05", "2026-08")]
P.rows.append({"block": "④", "id": "D5-2026-02→05 与 2026-07→08 相邻月均差均 ≤0.001(=0.1bp)", "source": SRC + ":series_store.JP_POLICY_RATE",
               "computed": flat, "claim": True, "match": all(abs(d) <= 0.1 for _, d in flat), "detail": "相邻月均差(bp): " + str(flat)})
# 2026 年内上行台阶计数
steps26 = [c[0] for c in chg if abs(c[3]) >= 0.5 and c[0].startswith("2026")]
P.rows.append({"block": "④", "id": "D5-2026 年内上行月均台阶: 01/06/07 为头三个(2026-07 为第三个)", "source": SRC + ":series_store.JP_POLICY_RATE",
               "computed": steps26, "claim": ["2026-01", "2026-06", "2026-07", "2026-09", "2026-10"], "match": steps26[:3] == ["2026-01", "2026-06", "2026-07"],
               "detail": f"2026 年内变动点序列={steps26}"})
P.rows.append({"block": "④", "id": "D5-2026-04→2026-07 锚 0.727→0.978(经 2026-06 0.841)", "source": SRC + ":series_store.JP_POLICY_RATE[2026-04],[2026-06],[2026-07]",
               "computed": (m["2026-04"], m["2026-06"], m["2026-07"]), "claim": (0.727, 0.841, 0.978), "match": (m["2026-04"], m["2026-06"], m["2026-07"]) == (0.727, 0.841, 0.978), "detail": "直读"})
P.rows.append({"block": "④", "id": "D5-最近一级台阶=2026-09→2026-10(其后无更新观测)", "source": SRC + ":series_store.JP_POLICY_RATE.dates",
               "computed": chg[-1][0], "claim": "2026-10", "match": chg[-1][0] == "2026-10" and st.le("JP_POLICY_RATE", CUT)[0] == "2026-10-01", "detail": f"末变动点={chg[-1]}"})
# 美欧政策序列同月变动(快照序列库内)
for mid, d0, d1, v0, v1 in [("DFEDTARU", "2026-09-16", "2026-09-17", 3.75, 4.00), ("ECB_DFR", "2026-09-15", "2026-09-16", 2.25, 2.50)]:
    dates, values = st.series(mid)
    chgs = [(dates[i], values[i - 1], values[i]) for i in range(1, len(dates)) if values[i] != values[i - 1] and dates[i] >= "2026-06-01"]
    P.rows.append({"block": "④", "id": f"D6-{mid} 变动日与前后值", "source": SRC + f":series_store.{mid}",
                   "computed": chgs, "claim": (d1, v0, v1), "match": any(c[0] == d1 and abs(c[1] - v0) < 1e-9 and abs(c[2] - v1) < 1e-9 for c in chgs),
                   "detail": f"2026-06 起变动点={chgs}; 末观测={st.le(mid, CUT)}"})
P.rows.append({"block": "④", "id": "D6-DFEDTARU/ECB_DFR 不在本问证据索引(63 行)", "source": "evidence_index.json",
               "computed": sorted({r["metric_id"] for r in L.load_json(os.path.join(os.path.dirname(rp_path), "evidence_index.json"))} & {"DFEDTARU", "ECB_DFR", "ECB_MRO", "DFEDTARL"}),
               "claim": [], "match": not ({r["metric_id"] for r in L.load_json(os.path.join(os.path.dirname(rp_path), "evidence_index.json"))} & {"DFEDTARU", "ECB_DFR", "ECB_MRO", "DFEDTARL"}),
               "detail": "证据索引中命中的政策序列"})
# 注册表
items = {it["metric_id"]: it for it in reg["metrics"]}
P.rows.append({"block": "④", "id": "D7-注册表无 JP_POLICY_TARGET", "source": REG + ":metrics[metric_id=JP_POLICY_TARGET]",
               "computed": "JP_POLICY_TARGET" in items, "claim": False, "match": "JP_POLICY_TARGET" not in items, "detail": "直查"})
jp_face = sorted(mid for mid, it in items.items() if it.get("economy") == "JP")
P.rows.append({"block": "④", "id": "D7-注册表 economy=JP 面", "source": REG + ":metrics[economy=JP]", "computed": jp_face, "claim": "含 JP_POLICY_RATE, 不含政策目标序列",
               "match": "JP_POLICY_RATE" in jp_face and not any("TARGET" in x for x in jp_face), "detail": f"JP 面={jp_face}"})
P.rows.append({"block": "④", "id": "D7-快照 series_store 无 JP_POLICY_TARGET", "source": SRC + ":series_store", "computed": st.has("JP_POLICY_TARGET"), "claim": False, "match": not st.has("JP_POLICY_TARGET"), "detail": "直查"})
P.rows.append({"block": "④", "id": "D7-JP_POLICY_RATE 注册表口径=无担保隔夜拆借利率月均(非目标宣布值)", "source": REG + ":metrics[JP_POLICY_RATE].calc/value_type",
               "computed": (items["JP_POLICY_RATE"]["value_type"], items["JP_POLICY_RATE"]["calc"][:40]), "claim": "monthly_avg_rate / 日本无担保隔夜拆借利率月均",
               "match": items["JP_POLICY_RATE"]["value_type"] == "monthly_avg_rate" and "无担保隔夜拆借利率月均" in items["JP_POLICY_RATE"]["calc"], "detail": "直读"})
# 会议纪要
pdf = rp["research_plan"]["policy_doc_facts"]
P.rows.append({"block": "④", "id": "D8-FOMC-MINUTES-2026-10 发布日 2026-11-18", "source": "report.json:research_plan.policy_doc_facts[0]",
               "computed": [(p["doc_id"], p["published_on"], p["kind"]) for p in pdf], "claim": [("FOMC-MINUTES-2026-10", "2026-11-18", "minutes")],
               "match": [(p["doc_id"], p["published_on"], p["kind"]) for p in pdf] == [("FOMC-MINUTES-2026-10", "2026-11-18", "minutes")], "detail": "直读"})
P.rows.append({"block": "④", "id": "D8-政策事件簇为空", "source": "report.json:research_plan.policy_event_clusters.clusters",
               "computed": rp["research_plan"]["policy_event_clusters"]["clusters"], "claim": [], "match": rp["research_plan"]["policy_event_clusters"]["clusters"] == [], "detail": "直读"})
P.save("points_04_policy.json")

# ------------------------------------------------- ⑬ 契约 STALE / ⑭ 缺口披露
P = L.Points("⑬", "契约验证非 VERIFIED 项(STALE)的判断档披露")
cv = rp["agent_judgment"]["contract_verification"]
stale = [(v["item"], v["metric"], v["token"], v["status"], v["observation"] if "observation" in v else v.get("note")) for v in cv["verdicts"] if v["status"] != "VERIFIED"]
P.rows.append({"block": "⑬", "id": "E1-契约 verdicts 中非 VERIFIED 项恰为 CORE_PCE 与 US_REAL_GDP 两处 STALE", "source": "report.json:agent_judgment.contract_verification.verdicts",
               "computed": stale, "claim": "CORE_PCE 130.902 / US_REAL_GDP 24611.077 两处 STALE",
               "match": sorted(s[1] for s in stale) == ["CORE_PCE", "US_REAL_GDP"] and all(s[3] == "STALE" for s in stale) and len(stale) == 2,
               "detail": f"全部 verdicts={len(cv['verdicts'])}; 非 VERIFIED={stale}"})
P.rows.append({"block": "⑬", "id": "E1-契约 STALE 项数值一致(value==expected)", "source": "report.json:agent_judgment.contract_verification.verdicts",
               "computed": [(v["metric"], v["value"], v["expected"]) for v in cv["verdicts"] if v["status"] == "STALE"], "claim": True,
               "match": all(v["value"] == v["expected"] for v in cv["verdicts"] if v["status"] == "STALE"), "detail": "直读"})
d_cp = L.days_between("2026-09-01", CUT)
d_g = L.days_between("2026-07-01", CUT)
P.rows.append({"block": "⑬", "id": "E1-CORE_PCE 观测 2026-09-01 距截止日 83 天", "source": SRC + ":series_store.CORE_PCE.dates[-1] ; research_as_of",
               "computed": d_cp, "claim": 83, "match": d_cp == 83, "detail": "日历日直算"})
P.rows.append({"block": "⑬", "id": "E1-US_REAL_GDP 观测 2026-07-01 距截止日 145 天", "source": SRC + ":series_store.US_REAL_GDP.dates[-1]",
               "computed": d_g, "claim": 145, "match": d_g == 145, "detail": "日历日直算"})
P.rows.append({"block": "⑬", "id": "E1-注册表最大日历滞后: CORE_PCE=60 / US_REAL_GDP=120 / EA_REAL_GDP_YOY=120", "source": REG + ":metrics[*].freshness.max_calendar_lag_days",
               "computed": {k: items[k]["freshness"]["max_calendar_lag_days"] for k in ("CORE_PCE", "US_REAL_GDP", "EA_REAL_GDP_YOY")}, "claim": {"CORE_PCE": 60, "US_REAL_GDP": 120, "EA_REAL_GDP_YOY": 120},
               "match": {k: items[k]["freshness"]["max_calendar_lag_days"] for k in ("CORE_PCE", "US_REAL_GDP", "EA_REAL_GDP_YOY")} == {"CORE_PCE": 60, "US_REAL_GDP": 120, "EA_REAL_GDP_YOY": 120}, "detail": "直读"})
P.add("E1-CORE_PCE 倍数 83/60(报告 1.4)", 1.4, d_cp / 60.0, "83 天 / 注册表 60 天", nd=1)
P.add("E1-US_REAL_GDP 倍数 145/120(报告 1.2)", 1.2, d_g / 120.0, "145 天 / 注册表 120 天", nd=1)
P.rows.append({"block": "⑬", "id": "E1-STALE 项均为该序列截止日前最新已发布观测", "source": SRC + ":series_store.CORE_PCE/US_REAL_GDP.dates",
               "computed": (st.le("CORE_PCE", CUT)[0], st.le("US_REAL_GDP", CUT)[0]), "claim": ("2026-09-01", "2026-07-01"),
               "match": (st.le("CORE_PCE", CUT)[0], st.le("US_REAL_GDP", CUT)[0]) == ("2026-09-01", "2026-07-01"), "detail": "直读"})
P.rows.append({"block": "⑬", "id": "E1-EA_REAL_GDP_YOY 最新观测 2026-07-01 距截止日 145 天(与 US_REAL_GDP 同龄同倍数)", "source": SRC + ":series_store.EA_REAL_GDP_YOY.dates[-1]",
               "computed": (L.days_between(st.le("EA_REAL_GDP_YOY", CUT)[0], CUT), items["EA_REAL_GDP_YOY"]["freshness"]["max_calendar_lag_days"]),
               "claim": (145, 120), "match": (L.days_between(st.le("EA_REAL_GDP_YOY", CUT)[0], CUT), items["EA_REAL_GDP_YOY"]["freshness"]["max_calendar_lag_days"]) == (145, 120),
               "detail": f"直算; 序列存量观测数={len(st.series('EA_REAL_GDP_YOY')[0])}"})
P.save("points_13_stale.json")

P = L.Points("⑭", "交付门/Gate A 缺口披露与序列面一致")
ga = snap["gate_a"]
P.rows.append({"block": "⑭", "id": "F1-Gate A 状态 DEGRADED", "source": SRC + ":gate_a.status", "computed": ga["status"], "claim": "DEGRADED", "match": ga["status"] == "DEGRADED", "detail": "直读"})
P.rows.append({"block": "⑭", "id": "F1-核心缺口 0 项", "source": SRC + ":gate_a.core_missing", "computed": ga["core_missing"], "claim": [], "match": ga["core_missing"] == [], "detail": "直读"})
P.rows.append({"block": "⑭", "id": "F1-非核心缺口七项(名单一致)", "source": SRC + ":gate_a.noncore_missing", "computed": sorted(ga["noncore_missing"]),
               "claim": sorted(["BUND_10Y", "BUND_2Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"]),
               "match": sorted(ga["noncore_missing"]) == sorted(["BUND_10Y", "BUND_2Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"]), "detail": "直读"})
P.rows.append({"block": "⑭", "id": "F1-非核心降级八项(名单一致)", "source": SRC + ":gate_a.noncore_degraded", "computed": sorted(ga["noncore_degraded"]),
               "claim": sorted(["CN_SF_FLOW", "ECB_DFR", "ECB_MRO", "JTSJOL", "M2SL", "SPX_EPS", "SPX_PE_TTM", "US_REAL_GDP"]),
               "match": sorted(ga["noncore_degraded"]) == sorted(["CN_SF_FLOW", "ECB_DFR", "ECB_MRO", "JTSJOL", "M2SL", "SPX_EPS", "SPX_PE_TTM", "US_REAL_GDP"]), "detail": "直读"})
P.rows.append({"block": "⑭", "id": "F1-EA_REAL_GDP_YOY 在非核心缺口清单内但序列库有存量观测", "source": SRC + ":series_store.EA_REAL_GDP_YOY",
               "computed": ("EA_REAL_GDP_YOY" in ga["noncore_missing"], len(st.series("EA_REAL_GDP_YOY")[0]), st.le("EA_REAL_GDP_YOY", CUT)),
               "claim": (True, "有存量观测, 最新 2026-07-01"),
               "match": ("EA_REAL_GDP_YOY" in ga["noncore_missing"]) and st.le("EA_REAL_GDP_YOY", CUT)[0] == "2026-07-01", "detail": "直读"})
P.rows.append({"block": "⑭", "id": "F1-EA_REAL_GDP_YOY 在事实面缺席(facts 无该指标)", "source": SRC + ":facts[metric_id=EA_REAL_GDP_YOY]",
               "computed": [f["fact_id"] for f in snap["facts"] if f["metric_id"] == "EA_REAL_GDP_YOY"], "claim": [],
               "match": not [f for f in snap["facts"] if f["metric_id"] == "EA_REAL_GDP_YOY"], "detail": "直读"})
planned = rp["research_plan"]["metrics"]
nov = {}
for mid in planned:
    nov[mid] = len(st.between(mid, "2026-11-01", "2026-11-30"))
P.rows.append({"block": "⑭", "id": "F2-任务窗 2026-11-01..11-30 内 9 个计划指标观测数均为 0", "source": SRC + f":series_store[{','.join(planned)}].dates",
               "computed": nov, "claim": "all 0", "match": all(v == 0 for v in nov.values()) and len(nov) == 9, "detail": "直数"})
# 证据引用计数
c_refs = sum(len(c["evidence_refs"]) for c in aj["l3"]["contradictions"])
m_refs = sum(len(lk["evidence_refs"]) for ch in aj["l3"]["mechanism_chains"] for lk in ch["links"])
s_all = []
for sc in aj["l4"]["scenarios"]:
    r = sc["rows"]
    s_all += list(r["asset_direction"].get("evidence_refs", [])) + [r["falsification"]["metric_id"]] + list(r["falsification"].get("secondary_metric_ids", []))
P.rows.append({"block": "⑭", "id": "F3-证据引用计数: 矛盾陈述/机制链/情景", "source": "agent_judgment.json:l3.contradictions[*].evidence_refs; l3.mechanism_chains[*].links[*].evidence_refs; l4.scenarios[*].rows",
               "computed": {"contradictions": c_refs, "mechanism": m_refs, "scenarios_all": len(s_all), "scenarios_unique": len(set(s_all)), "total(c+m+uniq_s)": c_refs + m_refs + len(set(s_all))},
               "claim": {"contradictions": 10, "mechanism": 4, "scenarios": 5, "total": 19},
               "match": (c_refs == 10 and m_refs == 4 and len(set(s_all)) == 5 and c_refs + m_refs + len(set(s_all)) == 19),
               "detail": "逐条直数(矛盾陈述 6+3+2; 机制链 1+1+2; 情景唯一指标 TIPS_10Y/BEI_10Y/SPX/EA_HICP_YOY/CORE_PCE)"})
# 全部证据引用解析到证据索引
idx = {r["ref"] for r in L.load_json(os.path.join(os.path.dirname(rp_path), "evidence_index.json"))}
all_refs = []
for c in aj["l3"]["contradictions"]:
    all_refs += c["evidence_refs"]
for ch in aj["l3"]["mechanism_chains"]:
    for lk in ch["links"]:
        all_refs += lk["evidence_refs"]
unres = [r for r in all_refs if r not in idx]
P.rows.append({"block": "⑭", "id": "F3-矛盾陈述+机制链 evidence_refs 全部解析到证据索引", "source": "evidence_index.json[*].ref",
               "computed": unres, "claim": [], "match": not unres, "detail": f"带日期引用 {len(all_refs)} 条; 未解析={unres}"})
P.save("points_14_gate.json")
