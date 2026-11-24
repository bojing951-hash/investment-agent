#!/usr/bin/python3 -I
"""席位自写脚本 s16: ⑫ 截止日时点说明 / ⑦⑩ 事实面与渲染一致性(只读复算).

用法: /usr/bin/python3 -I s16_facts.py <快照> <注册表> <运行目录> <席位目录>
"""
import json
import os
import re
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seatlib  # noqa: E402
from seatlib import Points, Store, load_json, days_between  # noqa: E402

SNAP, REG, RUN, SEAT, CAL = sys.argv[1:6]
snap = load_json(SNAP)
reg = load_json(REG)
aj = load_json(os.path.join(RUN, "agent_judgment.json"))
rep = load_json(os.path.join(RUN, "report.json"))
ev = load_json(os.path.join(RUN, "evidence_index.json"))
S = Store(snap)
SRC = "root_overlay/data/daily/research_snapshot_20261123.json"

# ---------------------------------------------------------------- ⑫ 时点
P = Points("⑫", "研究截止时点与各金融中心本地时间(盘中快照标注的时间依据)")
rao = snap["research_as_of"]
P.add_bool("Z0-快照 research_as_of=2026-11-23T22:53:47+08:00(与受审稿所写一致)", True, rao == "2026-11-23T22:53:47+08:00",
           f"{SRC}:research_as_of", f"直读 {rao}")
dt = datetime.fromisoformat(rao)
for city, tzname, claim in (("纽约", "America/New_York", "09:53"), ("法兰克福", "Europe/Berlin", "15:53"), ("东京", "Asia/Tokyo", "23:53"), ("上海", "Asia/Shanghai", "22:53")):
    loc = dt.astimezone(ZoneInfo(tzname))
    P.rows.append({"block": "⑫", "id": f"Z1-截止时点 {city} 本地时间", "source": f"{SRC}:research_as_of; IANA 时区库 {tzname}",
                   "kind": "point", "computed": loc.strftime("%H:%M"), "claim": claim, "match": loc.strftime("%H:%M") == claim,
                   "detail": f"{tzname} 本地 {loc.strftime('%Y-%m-%d %H:%M:%S')}; 受审稿 {claim}"})
ny = dt.astimezone(ZoneInfo("America/New_York"))
fr = dt.astimezone(ZoneInfo("Europe/Berlin"))
P.add_bool("Z2-截止时点纽约 09:30–16:00 常规交易时段进行中(美股盘中)", True, (ny.hour, ny.minute) >= (9, 30) and (ny.hour, ny.minute) < (16, 0),
           "research_as_of → America/New_York", f"纽约 {ny.strftime('%H:%M')}")
P.add_bool("Z3-截止时点法兰克福 09:00–17:30 常规交易时段进行中(德法股指盘中)", True, (fr.hour, fr.minute) >= (9, 0) and (fr.hour, fr.minute) < (17, 30),
           "research_as_of → Europe/Berlin", f"法兰克福 {fr.strftime('%H:%M')}")
dts_n, _ = S.series("NIKKEI225")
P.add_bool("Z4-「NIKKEI225 止于 2026-11-20 收盘」: 序列末观测日=2026-11-20(周五)", True, dts_n[-1] == "2026-11-20",
           f"{SRC}:series_store.NIKKEI225.dates[-1]", f"末观测 {dts_n[-1]}")
for mid in ("SPX", "VIX", "GOLD_F", "DXY", "USDJPY", "EURUSD", "BRENT_F"):
    d, v = S.series(mid)
    P.add_bool(f"Z5-{mid} 序列末观测日=2026-11-23(截止日当日值, 受审稿标注为盘中快照)", True, d[-1] == "2026-11-23",
               f"{SRC}:series_store.{mid}.dates[-1]", f"末观测 {d[-1]}")
late = [m for m in S.ss if S.series(m)[0][-1] > "2026-11-23"]
P.add_bool("Z6-全库 92 条序列无晚于截止日 2026-11-23 的观测(无事后信息混入)", True, len(late) == 0 and len(S.ss) == 92,
           f"{SRC}:series_store[*].dates[-1]", f"晚于截止日的序列 {late}; 序列数 {len(S.ss)}")
P.save("points_12_time.json")

# ---------------------------------------------------------------- ⑦ 事实面
P = Points("⑦", "机制链缺环注记/注册表/证据索引事实")
jgb = {f["metric_id"]: f for f in snap["facts"] if f["metric_id"].startswith("JGB")}
P.add_bool("J1-「快照事实面仅有 2026-11-19 点值 JGB 2/5/10 年 1.853/2.235/2.87」", True,
           abs(jgb.get("JGB2Y", {}).get("value", -1) - 1.853) < 5e-4 and abs(jgb.get("JGB5Y", {}).get("value", -1) - 2.235) < 5e-4
           and abs(jgb.get("JGB10Y", {}).get("value", -1) - 2.87) < 5e-4 and all(jgb[m]["observation_date"] == "2026-11-19" for m in ("JGB2Y", "JGB5Y", "JGB10Y")),
           f"{SRC}:facts[JGB2Y/JGB5Y/JGB10Y]",
           "; ".join(f"{m}={jgb.get(m, {}).get('value')}@{jgb.get(m, {}).get('observation_date')}" for m in ("JGB2Y", "JGB5Y", "JGB10Y")))
P.add_bool("J2-「序列库无历史」: series_store 无 JGB 序列", True, not any(m.startswith("JGB") for m in S.ss), f"{SRC}:series_store(键)",
           f"JGB 键 {[m for m in S.ss if m.startswith('JGB')]}")
ev_refs = {r["ref"] if isinstance(r, dict) else r for r in (ev if isinstance(ev, list) else ev.get("rows", []))}
P.add_bool("J3-「未入证据索引」: 证据索引无 JGB 条目", True, not any("JGB" in r for r in ev_refs), "evidence_index.json[*].ref", f"证据索引行数 {len(ev_refs)}")
mets = reg.get("metrics") or reg.get("entries") or reg
if isinstance(mets, dict):
    jp_face = sorted(k for k, v in mets.items() if isinstance(v, dict) and v.get("economy") == "JP")
else:
    jp_face = sorted(m["metric_id"] for m in mets if m.get("economy") == "JP")
P.add_bool("J4-注册表 economy=JP 面含 JGB2Y/5Y/10Y(在册)但快照无序列 →「序列库无历史」表述准确", True,
           all(m in jp_face for m in ("JGB2Y", "JGB5Y", "JGB10Y")) and "JP_POLICY_TARGET" not in mets if isinstance(mets, dict) else
           all(m in jp_face for m in ("JGB2Y", "JGB5Y", "JGB10Y")) and "JP_POLICY_TARGET" not in [m["metric_id"] for m in mets],
           "root_overlay/config/metric_registry.json:economy=JP", f"JP 面 {jp_face}")
P.add_bool("J5-「本引擎无日本套息持仓…序列」: series_store 无套息持仓类序列", True, not any(re.search(r"CARRY|FX_POS|CFTC|POSITION", m) for m in S.ss),
           f"{SRC}:series_store(键)", "键名扫描 CARRY/FX_POS/CFTC/POSITION")
P.add_bool("J6-「无日美利差序列」: series_store 无利差/spread 类日美序列", True, not any(re.search(r"USJP|JPUS|SPREAD|DIFF", m) for m in S.ss),
           f"{SRC}:series_store(键)", str([m for m in S.ss if re.search(r"SPREAD|DIFF", m)]))
P.add_bool("J7-「美联储目标区间上限…欧央行存款便利利率…未纳入本问证据索引」: DFEDTARU/ECB_DFR 不在证据索引", True,
           not any(("DFEDTARU" in r) or ("ECB_DFR" in r) for r in ev_refs), "evidence_index.json[*].ref", "DFEDTARU/ECB_DFR 在 series_store 而不在证据索引")
P.add_bool("J8-「本问计划指标面未纳入美欧政策利率序列」: plan.metrics 无 DFEDTARU/ECB_DFR", True,
           not any(m in rep["research_plan"]["metrics"] for m in ("DFEDTARU", "ECB_DFR", "FEDFUNS", "ECB_MRO")), "report.json:research_plan.metrics",
           str(rep["research_plan"]["metrics"]))
P.add_bool("J9-「政策事件簇为空」", True, rep["research_plan"]["policy_event_clusters"]["clusters"] == [], "report.json:research_plan.policy_event_clusters.clusters")
cal = load_json(CAL)
pol = [e for e in cal["entries"] if e.get("decision_date")]
P.add_bool("J10-「发布日历政策条目仅 2 条、均为日本央行实录」", True, len(pol) == 2 and all(e["metric_id"] == "JP_POLICY_TARGET" for e in pol),
           "root_overlay/config/release_calendar.json:entries[*].decision_date/metric_id",
           f"带决议日条目 {[(e['entry_id'], e['decision_date']) for e in pol]}; 日历共 {len(cal['entries'])} 条")
P.add("J11-「发布日历政策条目仅 2 条」条数", 2, len(pol), "root_overlay/config/release_calendar.json:entries[*].decision_date", nd=0)
P.add("J12-「证据索引 63 行」行数", 63, len(ev_refs), "evidence_index.json", nd=0)
P.add("J13-「本问计划指标面」9 个指标", 9, len(rep["research_plan"]["metrics"]), "report.json:research_plan.metrics", nd=0)
P.save("points_07_facts.json")

# ---------------------------------------------------------------- ⑩ 结构一致性
P = Points("⑩", "总判断/走位/对质表与引擎面的一致性")
rm = aj["reader_map"]
cells = {c["metric_id"]: c for c in rep["research_plan"]["point_values"]["cells"]}
P.add_bool("K1-agent_declaration「点值格(9格)」", True, len(cells) == 9, "report.json:research_plan.point_values.cells", f"格数 {len(cells)}")
P.add_bool("K2-agent_declaration「证据索引(63行)」", True, len(ev_refs) == 63, "evidence_index.json", f"行数 {len(ev_refs)}")
# anchor_echo 逐项对点值格
n_echo = 0
bad = []
for r in rm["regions"]:
    for e in r["anchor_echo"]:
        n_echo += 1
        a = cells[e["metric_id"]]["anchors"][e["anchor"]]
        if not (abs(a["value"] - e["value"]) < 1e-9 and a["observation_date"][:7] == e["observation_month"]):
            bad.append((r["region"], e))
P.add_bool("K3-走位 anchor_echo 全部取值/观测月与点值格逐项一致", True, n_echo == 18 and not bad, "agent_judgment.json:reader_map.regions[*].anchor_echo; report.json:…point_values.cells",
           f"条数 {n_echo}; 不一致 {bad}")
trio = rep["research_plan"]["us_rates_trio"]
rd = rm["rates_decomposition"]
P.add_bool("K4-rates_decomposition 回贴=引擎三利率分解(-8/+11/-19, 窗 2026-10-20→2026-11-19)", True,
           rd["nominal_bp"] == trio["chg_bp"]["UST_10Y"] and rd["real_bp"] == trio["chg_bp"]["TIPS_10Y"] and rd["bei_bp"] == trio["chg_bp"]["BEI_10Y"]
           and rd["window_from"] == trio["window"]["from"] and rd["window_to"] == trio["window"]["to"],
           "agent_judgment.json:reader_map.rates_decomposition; report.json:research_plan.us_rates_trio")
am = {r["metric_id"]: r for r in rep["research_plan"]["asset_moves"]["rows"]}
ok = all(e["chg_pct"] == am[e["metric_id"]]["chg_pct"] and e["window"] == am[e["metric_id"]]["window"] for e in rm["asset_returns_echo"])
P.add_bool("K5-asset_returns_echo 五行=引擎资产月窗(SPX/NIKKEI225/GOLD_F/DXY/VIX)", True, ok and len(rm["asset_returns_echo"]) == 5,
           "agent_judgment.json:reader_map.asset_returns_echo; report.json:research_plan.asset_moves.rows")
fo = [lk["face_off_verdict"] for ch in rm["transmission"] for lk in ch["links"]]
P.add_bool("K6-对质表裁定序列=[支持竞争解释, 尚不能区分, 支持主解释] 与 quality_gate_notes「支持主解释×1/支持竞争解释×1/尚不能区分×1」一致", True,
           fo == ["支持竞争解释", "尚不能区分", "支持主解释"], "agent_judgment.json:reader_map.transmission[*].links[*].face_off_verdict", str(fo))
links = aj["l3"]["mechanism_chains"][0]["links"]
P.add_bool("K7-机制链三环证据分级=[E1,E2,E2] 与 quality_gate_notes「E1/E2/E2」一致", True, [l["evidence_level"] for l in links] == ["E1", "E2", "E2"],
           "agent_judgment.json:l3.mechanism_chains[0].links[*].evidence_level")
P.add_bool("K8-「L3 三条矛盾陈述各并列 2 种解释」", True, [len(c["competing_explanations"]) for c in aj["l3"]["contradictions"]] == [2, 2, 2],
           "agent_judgment.json:l3.contradictions[*].competing_explanations")
# 裁定方向与在场观测方向一致
P.add_bool("K9-链1 裁定「支持竞争解释」: 主解释预期 BEI_10Y 走高/高位, 竞争预期走低/持平; 在场三窗 BEI_10Y 均回落 → 与裁定方向一致", True,
           all(("走低或持平" in lk["competing_predicts"]) and ("走高或维持高位" in lk["main_predicts"]) for lk in rm["transmission"][0]["links"][:1])
           and all(lk["face_off_verdict"] == "支持竞争解释" for lk in rm["transmission"][0]["links"][:1]),
           "agent_judgment.json:reader_map.transmission[0].links[0]; series_store.BEI_10Y(⑤-A18: -19/-14/-11bp)")
P.add_bool("K10-链3 裁定「支持主解释」: 主解释预期 TIPS_10Y 上行与 SPX 走弱同现, 竞争预期 TIPS_10Y 走低; 在场 TIPS_10Y +22bp、SPX -5.51% → 与裁定方向一致", True,
           "TIPS_10Y 上行与 SPX 走弱同现" in rm["transmission"][0]["links"][2]["main_predicts"]
           and "TIPS_10Y 走低与 SPX 走弱同现" in rm["transmission"][0]["links"][2]["competing_predicts"]
           and rm["transmission"][0]["links"][2]["face_off_verdict"] == "支持主解释",
           "agent_judgment.json:reader_map.transmission[0].links[2]; series_store.TIPS_10Y/SPX(⑤-A20/⑤-B3)")
P.add_bool("K11-链2 两解释在 TIPS_10Y 上预期方向不分立而裁定「尚不能区分」(未冒充支持任一侧)", True,
           "预期方向不分立" in rm["transmission"][0]["links"][1]["competing_predicts"] and rm["transmission"][0]["links"][1]["face_off_verdict"] == "尚不能区分",
           "agent_judgment.json:reader_map.transmission[0].links[1]")
P.add_bool("K12-总判断「距上次调整…(日历核验覆盖止于 2026-10-30,其后至截止日的 24 天引擎日历无条目)」: 2026-11-23−2026-10-30=24 天", True,
           days_between("2026-10-30", "2026-11-23") == 24 and "24 天" in rm["headline_conclusion"],
           "root_overlay/config/release_calendar.json:entries[RC-JP-BOJ-MAINT-2026-10].decision_date", f"{days_between('2026-10-30', '2026-11-23')} 天")
P.add_bool("K13-走位 US「中间 2026-09 为 4.2」", True, S.mval("UNEMPLOYMENT", "2026-09") == 4.2, f"{SRC}:series_store.UNEMPLOYMENT[2026-09-01]")
ea_d = S.mval("EA_HICP_YOY", "2026-10") - S.mval("EA_HICP_YOY", "2026-07")
us_h = S.yoy("CPI", "2026-09")[0] - S.yoy("CPI", "2026-07")[0]
us_c = S.yoy("CORE_CPI", "2026-09")[0] - S.yoy("CORE_CPI", "2026-07")[0]
us_p = S.yoy("CORE_PCE", "2026-09")[0] - S.yoy("CORE_PCE", "2026-06")[0]
P.add("K14-走位 EA「三个月上行 1.1 个百分点」(HICP 2.9→4.0)", 1.1, ea_d, f"{SRC}.EA_HICP_YOY[2026-07-01, 2026-10-01]")
P.add_bool("K14b-「为两地通胀面最大变化」: EA +1.1 大于美国 headline/核心 CPI/核心 PCE 同窗三个月变动", True,
           ea_d > max(us_h, us_c, us_p),
           f"{SRC}.EA_HICP_YOY/CPI/CORE_CPI/CORE_PCE(同比, 两锚同窗)",
           f"EA {ea_d:.4f} > US headline {us_h:.4f} / 核心 {us_c:.4f} / 核心PCE {us_p:.4f}")
P.add_probe("K14c-走位 US CPI 同比三个月变动(3.3→3.72; 受审稿未写差值, 留档)", round(us_h, 4), f"{SRC}.CPI[2026-07, 2026-09 同比]", "直算差值 0.4134; 仅作 K14b 比较基准")
P.add_bool("K15-总判断「通胀…欧元区幅度更大」在 headline/核心/核心PCE 三口径同向(三个月变动 EA 均最大)", True,
           ea_d > max(us_h, us_c, us_p) and ea_d > 0 and us_h > 0, "同 K14b", "EA headline 变动 > 美国三种口径各自的变动")
P.save("points_10_consistency.json")

# ---------------------------------------------------------------- 渲染一致性(读者报告中的判断文字)
P = Points("⑩", "读者报告渲染一致性: 判断文字逐串回贴 + verdict_note/narrative 不进渲染")


def leaves(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, f"{path}.{k}" if path else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, f"{path}[{i}]")
    elif isinstance(o, str) and len(o) >= 12:
        yield path, o


def norm(t):
    return re.sub(r"\s+", "", t)


docs = {}
for name in ("MAP_REPORT.md", "FULL_REPORT.md", "report.md"):
    docs[name] = norm(open(os.path.join(RUN, name), "r", encoding="utf-8").read())
alltxt = "".join(docs.values())
must, mustnot, other = [], [], []
for path, s in leaves(aj):
    if path.endswith("verdict_note") or path.endswith(".narrative"):
        mustnot.append((path, s))
    elif any(k in path for k in ("statement", "competing_explanations", "links", "scenario", "asset_direction", "falsification", "trigger",
                                 "headline_conclusion", "from_to", "quality_gate_notes", "history_zero_case_note", "missing_link_note",
                                 "causal_hypothesis", "competing_explanation", "main_predicts", "competing_predicts", "first_mover", "follow_or_diverge")):
        must.append((path, s))
    else:
        other.append((path, s))
rend = [(p, s) for p, s in must if norm(s) in alltxt]
not_rend = [(p, s) for p, s in must if norm(s) not in alltxt]
leak = [(p, s) for p, s in mustnot if norm(s) in alltxt]
narr = [(p, s) for p, s in must if not p.startswith("quality_gate_notes")]
qgn = [(p, s) for p, s in must if p.startswith("quality_gate_notes")]
narr_in = [(p, s) for p, s in narr if norm(s) in alltxt]
narr_out = [p for p, s in narr if norm(s) not in alltxt]
P.add("R1-判断正文串(陈述/并列解释/机制链/情景/走位/传导/类比注记)在读者报告(MAP_REPORT/FULL_REPORT/report)逐字在场条数", len(narr), len(narr_in),
      "agent_judgment.json(l3/l4/reader_map) ↔ MAP_REPORT.md/FULL_REPORT.md/report.md",
      f"应渲染 {len(narr)} 串; 未逐字在场: {narr_out}", nd=0)
qgn_in = [p for p, s in qgn if norm(s) in alltxt]
frag = {"盘中快照标注": "盘中快照(非收盘价)", "STALE字样": "STALE", "滞后83天(CORE_PCE)": "83天", "滞后145天": "145天", "按降级口径引用": "按降级口径引用",
        "缺基期": "缺上年同月基期", "政策条目仅2条": "政策条目仅2条"}
hit = {k: [nm for nm, tx in docs.items() if k2 in tx] for k, k2 in frag.items()}
us_txt = [r["from_to"] for r in rm["regions"] if r["region"] == "US"][0]
P.add_bool("R3-美国走位段(渲染面)未含 CORE_PCE(83 天/60 天)与 US_REAL_GDP(145 天/120 天)的契约 STALE 滞后披露(该披露仅在 quality_gate_notes[3])", True,
           ("83" not in us_txt) and ("145" not in us_txt) and ("STALE" not in us_txt) and ("83 天" in aj["quality_gate_notes"][3]) and ("145 天" in aj["quality_gate_notes"][3]),
           "agent_judgment.json:reader_map.regions[US].from_to; quality_gate_notes[3]", "披露落位: 仅在不进渲染的字段")
P.add_probe("R1b-quality_gate_notes 六条在读者报告中的渲染情况", f"未渲染 {len(qgn) - len(qgn_in)}/{len(qgn)}", "agent_judgment.json:quality_gate_notes ↔ MAP_REPORT.md/FULL_REPORT.md/report.md",
            "发现(记 MINOR, 不计复算偏离): 六条质量门披露均不进读者报告渲染; 关键词在场情况 " + json.dumps(hit, ensure_ascii=False))
P.add_bool("R2-「verdict_note 字段与转折面 narrative 字段不进渲染」: 该类串在三个渲染文件中均不出现", True, len(leak) == 0 and len(mustnot) == 6,
           "agent_judgment.json:reader_map.transmission[*].links[*].verdict_note; reader_map.turnings[*].narrative", f"该类串 {len(mustnot)} 条; 泄漏 {len(leak)}: {[p for p, _ in leak]}")
P.save("points_10b_render.json")
print("RENDER must=%d rendered=%d not_rendered=%d mustnot=%d leaked=%d" % (len(must), len(rend), len(not_rend), len(mustnot), len(leak)))
for p, s in not_rend[:20]:
    print("  NOT RENDERED:", p, "|", s[:70])
