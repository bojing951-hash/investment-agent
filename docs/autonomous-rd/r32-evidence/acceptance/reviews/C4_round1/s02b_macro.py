#!/usr/bin/python3 -I
# s02b: 通胀面 + 增长面 + 转折面 独立复算(只读)
import sys, os, json
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

# ---------- 通胀面 ----------
P.add("I01", SNAP, "JP_CPI_YOY@2026-07", mv(SS, "JP_CPI_YOY", "2026-07"), 1.97, 2)
P.add("I02", SNAP, "JP_CPI_YOY@2026-10", mv(SS, "JP_CPI_YOY", "2026-10"), 2.44, 2)
P.adds("I03", SNAP, "JP_CPI_YOY 末观测月", last(SS, "JP_CPI_YOY")[0][:7], "2026-10")
P.add("I04", SNAP, "JP_CPI_TOKYO_YOY@2026-07", mv(SS, "JP_CPI_TOKYO_YOY", "2026-07"), 1.85, 2)
P.add("I05", SNAP, "JP_CPI_TOKYO_YOY@2026-10", mv(SS, "JP_CPI_TOKYO_YOY", "2026-10"), 2.73, 2)
P.add("I06", SNAP, "JP_CPI_TOKYO_YOY@2026-06", mv(SS, "JP_CPI_TOKYO_YOY", "2026-06"), 1.6, 1)
P.add("I07", SNAP, "JP_CPI_TOKYO_YOY@2026-09", mv(SS, "JP_CPI_TOKYO_YOY", "2026-09"), 2.69, 2)
P.add("I08", SNAP, "东京都同比 2026-09 - 2026-06 (pp)", mv(SS, "JP_CPI_TOKYO_YOY", "2026-09") - mv(SS, "JP_CPI_TOKYO_YOY", "2026-06"), 1.09, 2)
P.adds("I09", SNAP, "JP_CPI_TOKYO_YOY 序列首观测", series(SS, "JP_CPI_TOKYO_YOY")[0][0][:7], "2026-01")
P.add("I10", SNAP, "CPI@2026-10", mv(SS, "CPI", "2026-10"), 337.476, 3)
P.add("I11", SNAP, "CPI@2026-07", mv(SS, "CPI", "2026-07"), 332.813, 3)
P.addb("I12", SNAP, "CPI 无 2025-10 观测(同比基期缺)", at_month(SS, "CPI", "2025-10") is None, "有 2025-09=%s, 2025-11=%s" % (mv(SS, "CPI", "2025-09"), mv(SS, "CPI", "2025-11")))
P.add("I13", SNAP, "CPI 同比 2026-09 (基期 2025-09) %", yoy(SS, "CPI", "2026-09"), 3.72, 2)
P.add("I14", SNAP, "CPI 同比 2026-07 (基期 2025-07) %", yoy(SS, "CPI", "2026-07"), 3.30, 2)
P.addb("I15", SNAP, "CPI 2026-10 为最新月且其同比不可得、2026-09 为最近有效同比", last(SS, "CPI")[0][:7] == "2026-10" and yoy(SS, "CPI", "2026-10") is None and yoy(SS, "CPI", "2026-09") is not None)
P.add("I16", SNAP, "CORE_CPI@2026-10", mv(SS, "CORE_CPI", "2026-10"), 339.9, 1)
P.add("I17", SNAP, "CORE_CPI@2026-07", mv(SS, "CORE_CPI", "2026-07"), 336.789, 3)
P.addb("I18", SNAP, "CORE_CPI 无 2025-10 观测", at_month(SS, "CORE_CPI", "2025-10") is None)
P.add("I19", SNAP, "CORE_CPI 同比 2026-09 %", yoy(SS, "CORE_CPI", "2026-09"), 2.57, 2)
P.add("I20", SNAP, "CORE_CPI 同比 2026-07 %", yoy(SS, "CORE_CPI", "2026-07"), 2.47, 2)
P.add("I21", SNAP, "CORE_PCE@2026-09", mv(SS, "CORE_PCE", "2026-09"), 130.902, 3)
P.add("I22", SNAP, "CORE_PCE@2026-06", mv(SS, "CORE_PCE", "2026-06"), 129.969, 3)
P.add("I23", SNAP, "CORE_PCE 同比 2026-06 %", yoy(SS, "CORE_PCE", "2026-06"), 3.04, 2)
P.add("I24", SNAP, "CORE_PCE 同比 2026-09 %", yoy(SS, "CORE_PCE", "2026-09"), 3.12, 2)
P.adds("I25", SNAP, "CORE_PCE 末观测月", last(SS, "CORE_PCE")[0][:7], "2026-09")
P.add("I26", SNAP, "CN_CPI_YOY@2026-07", mv(SS, "CN_CPI_YOY", "2026-07"), 0.5, 1)
P.add("I27", SNAP, "CN_CPI_YOY@2026-10", mv(SS, "CN_CPI_YOY", "2026-10"), 0.7, 1)
P.add("I28", SNAP, "CN_PPI_YOY@2026-07", mv(SS, "CN_PPI_YOY", "2026-07"), 3.5, 1)
P.add("I29", SNAP, "CN_PPI_YOY@2026-10", mv(SS, "CN_PPI_YOY", "2026-10"), 5.7, 1)
P.adds("I30", SNAP, "CN_CPI_YOY@2026-10 序列日期(=点值格观测日 2026-10-01; 证据索引标签 2026-10-31 为期末口径, 受审稿已披露两口径不同)", at_month(SS, "CN_CPI_YOY", "2026-10")[0], "2026-10-01")
P.adds("I30b", "report.json evidence_index[*].ref", "证据索引对 CN_CPI_YOY/CN_PPI_YOY 最新一期的引用标签(期末口径)", ",".join(r["ref"] for r in rep["evidence_index"] if r["ref"].split("@")[0] in ("CN_CPI_YOY", "CN_PPI_YOY") and r["ref"].endswith("2026-10-31")), "CN_CPI_YOY@2026-10-31,CN_PPI_YOY@2026-10-31")
P.add("I31", SNAP, "剪刀差 2026-07 = PPI-CPI (pp)", mv(SS, "CN_PPI_YOY", "2026-07") - mv(SS, "CN_CPI_YOY", "2026-07"), 3.0, 1)
P.add("I32", SNAP, "剪刀差 2026-10 = PPI-CPI (pp)", mv(SS, "CN_PPI_YOY", "2026-10") - mv(SS, "CN_CPI_YOY", "2026-10"), 5.0, 1)
# 三地同向(均高于三个月前) 的四个可核配对
P.addb("I33", SNAP, "美国 CPI 同比 3.72(2026-09) > 3.30(2026-07)", yoy(SS, "CPI", "2026-09") > yoy(SS, "CPI", "2026-07"))
P.addb("I34", SNAP, "美国核心CPI同比 2.57(2026-09) > 2.47(2026-07)", yoy(SS, "CORE_CPI", "2026-09") > yoy(SS, "CORE_CPI", "2026-07"))
P.addb("I35", SNAP, "美国核心PCE同比 3.12(2026-09) > 3.04(2026-06)", yoy(SS, "CORE_PCE", "2026-09") > yoy(SS, "CORE_PCE", "2026-06"))
P.addb("I36", SNAP, "日本 2.44>1.97、东京 2.73>1.85、中国CPI 0.7>0.5、PPI 5.7>3.5", mv(SS, "JP_CPI_YOY", "2026-10") > mv(SS, "JP_CPI_YOY", "2026-07") and mv(SS, "JP_CPI_TOKYO_YOY", "2026-10") > mv(SS, "JP_CPI_TOKYO_YOY", "2026-07") and mv(SS, "CN_CPI_YOY", "2026-10") > mv(SS, "CN_CPI_YOY", "2026-07") and mv(SS, "CN_PPI_YOY", "2026-10") > mv(SS, "CN_PPI_YOY", "2026-07"))
# 转折面数值(由水平序列派生同比)
P.add("T01", SNAP, "CORE_CPI 同比 2026-05 %", yoy(SS, "CORE_CPI", "2026-05"), 2.8229, 4)
P.add("T02", SNAP, "CORE_CPI 同比 2026-08 %", yoy(SS, "CORE_CPI", "2026-08"), 2.4462, 4)
P.add("T03", SNAP, "CORE_CPI 同比 2026-09 %", yoy(SS, "CORE_CPI", "2026-09"), 2.5658, 4)
_y05, _y08 = yoy(SS, "CORE_CPI", "2026-05"), yoy(SS, "CORE_CPI", "2026-08")
P.add("T04", SNAP, "核心CPI同比 所引两位四位小数之差 2026-08 − 2026-05 (pp)(未舍入差 %.6f, 四舍五入为 -0.3768)" % (_y08 - _y05), round(_y08, 4) - round(_y05, 4), -0.3767, 4)
P.add("T04b", "report.json research_plan.turning_candidates.candidates[CORE_CPI].delta", "引擎候选面 CORE_CPI delta(受审稿『三个月回落 0.3767 个百分点』)", [c for c in rep["research_plan"]["turning_candidates"]["candidates"] if c["metric_id"] == "CORE_CPI"][0]["delta"], -0.3767, 4)
P.add("T05", SNAP, "CPI 同比 2026-02 %", yoy(SS, "CPI", "2026-02"), 2.434, 3)
P.add("T06", SNAP, "CPI 同比 2026-05 %", yoy(SS, "CPI", "2026-05"), 4.1666, 4)
P.add("T07", SNAP, "CN_CPI_YOY@2026-01", mv(SS, "CN_CPI_YOY", "2026-01"), 0.2, 1)
P.add("T08", SNAP, "CN_CPI_YOY@2026-04", mv(SS, "CN_CPI_YOY", "2026-04"), 1.2, 1)
P.add("T09", SNAP, "INDPRO 同比 2025-11 %", yoy(SS, "INDPRO", "2025-11"), 1.7543, 4)
P.add("T10", SNAP, "INDPRO 同比 2026-02 %", yoy(SS, "INDPRO", "2026-02"), 0.7972, 4)
P.add("T11", SNAP, "INDPRO 同比 2026-02 - 2025-11 (pp)", yoy(SS, "INDPRO", "2026-02") - yoy(SS, "INDPRO", "2025-11"), -0.9571, 4)
P.add("T12", SNAP, "CN_PMI_MFG@2026-02", mv(SS, "CN_PMI_MFG", "2026-02"), 49.0, 1)
P.add("T13", SNAP, "CN_PMI_MFG@2026-05", mv(SS, "CN_PMI_MFG", "2026-05"), 50.0, 1)
P.add("T14", SNAP, "CN_PMI_MFG 同比 2026-02 %", yoy(SS, "CN_PMI_MFG", "2026-02"), -2.3904, 4)
P.add("T15", SNAP, "CN_PMI_MFG 同比 2026-05 %", yoy(SS, "CN_PMI_MFG", "2026-05"), 1.0101, 4)
tc = rep["research_plan"]["turning_candidates"]["candidates"]
P.addb("T16", "report.json research_plan.turning_candidates.candidates", "候选池 9 项", len(tc) == 9, str([(c.get("metric_id"), c.get("from_ym"), c.get("to_ym")) for c in tc]))
other = {"CN_PPI_YOY": ("2026-02", "2026-05"), "CN_CPI_YOY": ("2026-01", "2026-04"), "CPI": ("2026-02", "2026-05"), "JP_CPI_YOY": ("2025-11", "2026-02"), "CN_PMI_MFG": ("2026-02", "2026-05"), "INDPRO": ("2025-11", "2026-02"), "JP_CPI_TOKYO_YOY": ("2026-06", "2026-09"), "JP_POLICY_RATE": ("2026-04", "2026-07"), "CORE_CPI": ("2026-05", "2026-08")}
eng = {c.get("metric_id"): (c.get("from_ym"), c.get("to_ym")) for c in tc}
P.addb("T17", "report.json turning_candidates", "候选池 9 项的指标与窗口与正文所述一致", all(eng.get(k) == v for k, v in other.items()) and set(eng) == set(other), str(eng))
_pp = [c for c in tc if c["metric_id"] == "CN_PPI_YOY"][0]
P.add("T18", SNAP, "CN_PPI_YOY@2026-02 / @2026-05 (与引擎候选面 value_before/value_after)", mv(SS, "CN_PPI_YOY", "2026-05") - mv(SS, "CN_PPI_YOY", "2026-02") - (_pp["value_after"] - _pp["value_before"]), 0.0, 1, "直算 %s→%s; 引擎 %s→%s" % (mv(SS, "CN_PPI_YOY", "2026-02"), mv(SS, "CN_PPI_YOY", "2026-05"), _pp["value_before"], _pp["value_after"]))
P.add("T19", SNAP, "JP_CPI_YOY@2026-02", mv(SS, "JP_CPI_YOY", "2026-02"), [c for c in tc if c["metric_id"] == "JP_CPI_YOY"][0]["value_after"], 2, "与引擎候选面 value_after 比对")
P.addb("T20", "report.json turning_candidates", "除三项所取转折外, 其余 6 项窗口终点 ≤ 2026-05", all(v[1] <= "2026-05" for k, v in eng.items() if k not in ("JP_CPI_TOKYO_YOY", "JP_POLICY_RATE", "CORE_CPI")))

# ---------- 增长面 ----------
P.add("G01", SNAP, "US_REAL_GDP@2026-07", mv(SS, "US_REAL_GDP", "2026-07"), 24611.077, 3)
P.add("G02", SNAP, "US_REAL_GDP@2026-04", mv(SS, "US_REAL_GDP", "2026-04"), 24408.011, 3)
P.add("G03", SNAP, "US_REAL_GDP 同比 2026-07 (基期 2025-07) %", yoy(SS, "US_REAL_GDP", "2026-07"), 2.07, 2)
P.add("G04", SNAP, "US_REAL_GDP 同比 2026-04 (基期 2025-04) %", yoy(SS, "US_REAL_GDP", "2026-04"), 2.19, 2)
P.adds("G05", SNAP, "US_REAL_GDP 末观测季", last(SS, "US_REAL_GDP")[0][:7], "2026-07")
P.add("G06", SNAP, "UNEMPLOYMENT@2026-07", mv(SS, "UNEMPLOYMENT", "2026-07"), 4.1, 1)
P.add("G07", SNAP, "UNEMPLOYMENT@2026-10", mv(SS, "UNEMPLOYMENT", "2026-10"), 4.1, 1)
P.adds("G08", SNAP, "UNEMPLOYMENT 末观测月", last(SS, "UNEMPLOYMENT")[0][:7], "2026-10")
P.add("G09", SNAP, "INDPRO@2026-10", mv(SS, "INDPRO", "2026-10"), 103.3954, 4)
P.add("G10", SNAP, "INDPRO@2026-07", mv(SS, "INDPRO", "2026-07"), 103.1675, 4)
P.add("G11", SNAP, "INDPRO 同比 2026-10 %", yoy(SS, "INDPRO", "2026-10"), 2.15, 2)
P.add("G12", SNAP, "INDPRO 同比 2026-07 %", yoy(SS, "INDPRO", "2026-07"), 1.25, 2)
P.adds("G13", SNAP, "INDPRO 末观测月", last(SS, "INDPRO")[0][:7], "2026-10")
P.add("G14", SNAP, "CN_PMI_MFG@2026-07", mv(SS, "CN_PMI_MFG", "2026-07"), 49.2, 1)
P.add("G15", SNAP, "CN_PMI_MFG@2026-10", mv(SS, "CN_PMI_MFG", "2026-10"), 49.3, 1)
P.add("G16", SNAP, "JP_REAL_GDP_YOY@2026-04", mv(SS, "JP_REAL_GDP_YOY", "2026-04"), 0.8, 2)
P.add("G17", SNAP, "JP_REAL_GDP_YOY@2026-07", mv(SS, "JP_REAL_GDP_YOY", "2026-07"), 1.16, 2)
P.adds("G18", SNAP, "JP_REAL_GDP_YOY 末观测季", last(SS, "JP_REAL_GDP_YOY")[0][:7], "2026-07")
P.addb("G19", SNAP, "两期 PMI 均在荣枯线下方(49.2、49.3 < 50)", mv(SS, "CN_PMI_MFG", "2026-07") < 50 and mv(SS, "CN_PMI_MFG", "2026-10") < 50)

# ---------- 点值格(引擎面)与锚格值/观测日的一致性 ----------
def pub_date(mid, od):
    y, m = int(od[:4]), int(od[5:7])
    me = dt.date(y + (m // 12), (m % 12) + 1, 1) - dt.timedelta(days=1)
    if mid in ("US_REAL_GDP", "JP_REAL_GDP_YOY"):
        return (me + dt.timedelta(days={"US_REAL_GDP": 29, "JP_REAL_GDP_YOY": 45}[mid])).isoformat()
    k = {"UNEMPLOYMENT": 5, "INDPRO": 15, "CPI": 13, "CORE_CPI": 13, "CORE_PCE": 30, "CN_PMI_MFG": -1, "CN_CPI_YOY": 9,
         "CN_PPI_YOY": 9, "JP_CPI_YOY": 20, "JP_CPI_TOKYO_YOY": -1, "JP_POLICY_RATE": 5}.get(mid)
    if k is not None:
        return (me + dt.timedelta(days=k)).isoformat()
    if mid == "DFF":
        return plus_days(od, 1)
    return od
n_ok = 0; n_all = 0; bad = []
for (mid, which), a in sorted(pv.items()):
    anc_date = ANC if which == "anc" else CUT
    cand = [(d, v) for d, v in series(SS, mid) if pub_date(mid, d) <= anc_date]
    mine = cand[-1] if cand else None
    if a.get("status") != "ok":
        bad.append((mid, which, a.get("status"), "mine=%s" % (mine,)))
        continue
    n_all += 1
    if mine and mine[0] == a["observation_date"] and abs(mine[1] - a["value"]) < 1e-6:
        n_ok += 1
    else:
        bad.append((mid, which, "engine=(%s,%s)" % (a["observation_date"], a["value"]), "mine=%s" % (mine,)))
P.addb("V01", RP, "按引擎所载发布规则独立重算: 35 个 status=ok 锚格的(观测日,值)=『发布日≤锚日的最后观测』且逐位一致 (%d/%d)" % (n_ok, n_all), n_ok == n_all and len(bad) == 1, str(bad))
bad0 = [b for b in bad if len(b) == 4 and b[2] == "no_published_observation_on_or_before_anchor"]
P.addb("V01b", RP, "CN_POLICY_OVERNIGHT 三个月前锚: 发布日≤2026-08-23 的观测不存在(独立重算)", len(bad0) == 1 and "None" in bad0[0][3], str(bad0))
echo = []
for r in aj["reader_map"]["regions"]:
    for e in r.get("anchor_echo", []):
        echo.append((r["region"], e["metric_id"], e["anchor"], e["value"], e["observation_month"]))
bad2 = []
for reg_, mid, anc, val, om in echo:
    anc_date = ANC if anc == "3个月前" else CUT
    cand = [(d, v) for d, v in series(SS, mid) if pub_date(mid, d) <= anc_date]
    mine = cand[-1] if cand else None
    if not (mine and mine[0][:7] == om and abs(mine[1] - val) < 1e-6):
        bad2.append((reg_, mid, anc, val, om, "mine=%s" % (mine,)))
P.addb("V02", "agent_judgment.json reader_map.regions[*].anchor_echo", "anchor_echo 35 项: 值与观测月=『发布日≤锚日的最后观测』(独立按发布规则重算), 逐位一致", len(bad2) == 0, str(bad2))
P.addb("V03", RP, "点值格 18 格 + 缺席 4 格", len(cells) == 18 and len(rep["research_plan"]["point_values"]["absent"]) == 4)
P.addb("V04", RP, "CORE_PCE 锚=2026-06(2026-07 发布晚于锚)", pv[("CORE_PCE", "anc")]["observation_date"][:7] == "2026-06" and plus_days("2026-07-31", 30) > ANC)
P.addb("V05", RP, "US_REAL_GDP 锚=2026-04(Q3 发布 2026-10-29 晚于锚)", pv[("US_REAL_GDP", "anc")]["observation_date"][:7] == "2026-04" and pv[("US_REAL_GDP", "lat")]["publication_date"] > ANC)
P.addb("V06", RP, "JP_REAL_GDP_YOY 锚=2026-04", pv[("JP_REAL_GDP_YOY", "anc")]["observation_date"][:7] == "2026-04")
P.save(outdir, "pts_b.json")
