#!/usr/bin/python3 -I
# s06b: 合并四张复算表 + 追加本阶段核验的引擎面要点(只读), 产出 pts_all.json 与 points_table.md
import sys, os, json, ast, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rc_lib import *
snap_p, rep_p, cal_p, reg_p, aj_p, outdir, mapmd_p, tc_p, rmp_p, ajm_p = sys.argv[1:11]
snap, rep, cal, reg, aj = load(snap_p, rep_p, cal_p, reg_p, aj_p)
SS = snap["series_store"]
rp = rep["research_plan"]
allpts = []
for nm in ("pts_a.json", "pts_b.json", "pts_c.json", "pts_d.json"):
    for r in json.load(open(os.path.join(outdir, nm), encoding="utf-8")):
        r["file"] = nm
        allpts.append(r)
P = Points()
F = "snapshot.series_store"
# --- X 段: 本阶段核验的引擎面要点 ---
P.add("X01", "MAP_REPORT.md(引擎渲染面)『TIPS_10Y 引擎当前面: 近30日 2.66→2.88, 上升22bp』× snapshot.series_store.TIPS_10Y", "渲染面『近30日』窗 2026-10-23→2026-11-19 实际利率变动(bp)", bp(at(SS, "TIPS_10Y", "2026-10-23"), at(SS, "TIPS_10Y", "2026-11-19")), 22.0, 1, "同窗名义 +4.0bp=实际 +22.0bp+盈亏平衡 -18.0bp; 受审稿取共同交易日窗 10-20→11-19(+11bp), 两窗并存未对账(MINOR-3)")
P.add("X02", F + ".TIPS_10Y@2026-10-23", "渲染面所引窗起值 2.66", at(SS, "TIPS_10Y", "2026-10-23"), 2.66, 2)
mapmd = open(mapmd_p, encoding="utf-8").read()
P.addb("X03", "MAP_REPORT.md", "渲染面确含『近30日2.66→2.88,上升22bp』字样", "近30日2.66→2.88,上升22bp" in mapmd)
tc_src = open(tc_p, encoding="utf-8").read()
i0 = tc_src.index("ALIASES = {"); i1 = tc_src.index("\n}\n", i0) + 2
ALIASES = ast.literal_eval(tc_src[i0:i1].split("=", 1)[1].strip())
P.addb("X04", "scripts/research_contract/text_consistency.py ALIASES", "文本一致性别名表未收录 JP_CPI_*、JP_REAL_GDP_YOY、EA_* (受审稿引擎缺口披露①)", not any(k.startswith(("JP_CPI", "JP_REAL_GDP", "EA_")) for k in ALIASES), "keys n=%d" % len(ALIASES))
P.addb("X05", "scripts/research_contract/text_consistency.py ALIASES", "别名表含美国『CPI』『GDP』别名(JP_CPI_*/JP_REAL_GDP_YOY 子串会被绑定到美国同名序列)", "CPI" in ALIASES.get("CPI", []) and "GDP" in ALIASES.get("US_REAL_GDP", []), "CPI=%s US_REAL_GDP=%s" % (ALIASES.get("CPI"), ALIASES.get("US_REAL_GDP")))
vn = []
for nm in ("MAP_REPORT.md", "FULL_REPORT.md", "report.md"):
    t = open(os.path.join(os.path.dirname(mapmd_p), nm), encoding="utf-8").read()
    vn.append(str(t.count("verdict_note")))
P.adds("X06", "MAP_REPORT.md / FULL_REPORT.md / report.md", "verdict_note 字段出现次数(受审稿引擎缺口披露⑤: 不进渲染)", ",".join(vn), "0,0,0")
P.addb("X07", "MAP_REPORT.md", "读者所见裁定为 face_off_verdict 标签(『尚不能区分』渲染 ≥3 处)", mapmd.count("尚不能区分") >= 3, "count=%d" % mapmd.count("尚不能区分"))
s7 = json.load(open(os.path.join(outdir, "env_S7_mode_gate.json"), encoding="utf-8"))["gate"]
s6env = json.load(open(os.path.join(outdir, "env_S6_analog.json"), encoding="utf-8"))["envelope"]["data"]
P.addb("X08", "report.json steps[S7_mode_gate].envelope.gate", "类比研究模式门: 描述性可用、事件研究被阻断(受审稿历史零段注记)", s7.get("descriptive") == "available" and str(s7.get("event_study", "")).startswith("blocked"), str(s7.get("event_study"))[:80])
P.addb("X09", "report.json steps[S6_analog].envelope.data.sort_basis", "类比排序依据=缺席特征数优先、其后距离, 名次非纯距离序", "(n_missing, distance, month)" in str(s6env.get("sort_basis")) and "名次非纯距离序" in str(s6env.get("sort_basis")))
P.adds("X10", "report.json research_plan.as_of_declared.bare_year_month", "问句含显式日历月(受审稿引擎缺口披露④)", rp["as_of_declared"].get("bare_year_month"), "2026年11月")
note0 = rep["notes"][0]
lst = note0.split(":", 1)[1] if ":" in note0 else note0
ms = [x.strip() for x in re.split("[、,，]", lst) if x.strip()]
P.add("X11", "report.json notes[0]", "计划注记『地图计划指标缺数』所列指标数(受审稿: 十九)", len(ms), 19, 0, "|".join(ms)[:200])
cells = rp["point_values"]["cells"]
withval = [m for m in ms if any(c["metric_id"] == m and any(a.get("status") == "ok" for a in c["anchors"].values()) for c in cells)]
P.add("X12", "report.json notes[0] × research_plan.point_values.cells", "其中在点值格有值的指标数(受审稿: 十五)", len(withval), 15, 0, "无值者=%s" % [m for m in ms if m not in withval])
P.adds("X13", "release_calendar.json version", "冻结发布日历版本(受审稿: v1.5.0)", cal.get("version"), "1.5.0")
ajm = open(ajm_p, encoding="utf-8").read()
rmp = open(rmp_p, encoding="utf-8").read()
metric2pair = {}
for eco, rf in rp["regions"].items():
    for dim, lst2 in (rf.get("dimensions") or {}).items():
        for m in lst2:
            metric2pair[m["metric_id"]] = (eco, dim)
okpairs = set()
for c in cells:
    if any(a.get("status") == "ok" for a in c["anchors"].values()) and c["metric_id"] in metric2pair:
        okpairs.add(metric2pair[c["metric_id"]])
planned = set(metric2pair.values())
zero = sorted(planned - okpairs)
P.addb("X14", "report.json research_plan.regions×point_values.cells × scripts/agent_judgment.py BLOCKING_BLOCKED_CLASSES", "交付门: 地区×维度组零 ok 格(map_core_dimension_missing 属阻断类)——受审稿『引擎交付门以核心维度缺数判为不可交付』", "map_core_dimension_missing" in ajm and len(zero) > 0 and all(z[0] == "EA" for z in zero), "零 ok 格组=%s / 计划组 %d" % (zero, len(planned)))
P.addb("X15", "scripts/research_map_planner.py 并项补选口径 × MAP_REPORT.md", "引擎并项规则=同维度且观测窗重叠的转折计同一轮; 补选行标注『引擎补选』(受审稿转折取舍注记)", "同维度且观测窗重叠的转折" in rmp and "引擎补选" in mapmd, "MAP_REPORT『引擎补选』出现 %d 次" % mapmd.count("引擎补选"))
_x16 = [s.get("step") for s in rep["steps"] if s.get("ok") is not True]
_s8 = [s for s in rep["steps"] if s.get("step") == "S8_grounded_qa"][0]
_s8e = _s8.get("envelope") or {}
_x16 = [s.get("step") for s in rep["steps"] if s.get("ok") is not True]
_s8 = [s for s in rep["steps"] if s.get("step") == "S8_grounded_qa"][0]
_s8e = _s8.get("envelope") or {}
P.addb("X16", "report.json run_ok / steps[*].ok / steps[S8_grounded_qa].envelope", "run_ok=true 且 66 步 step 级 ok 全为 true(62 已执行+4 未执行); S8_grounded_qa 信封含 unmapped(地图问句不属其支持的问题类型, 非失败步骤)", rep.get("run_ok") is True and len(_x16) == 0 and len(rep["steps"]) == 66 and "unmapped" in json.dumps(_s8e, ensure_ascii=False), "ok!=true 步骤=%s; S8 信封状态=%s" % (_x16, _s8e.get("status")))
P.addb("X17", F + ".UST_10Y/TIPS_10Y/BEI_10Y", "10-23→11-19 窗三利率恒等残差=0(+4 = +22 − 18)", abs(bp(at(SS, "UST_10Y", "2026-10-23"), at(SS, "UST_10Y", "2026-11-19")) - bp(at(SS, "TIPS_10Y", "2026-10-23"), at(SS, "TIPS_10Y", "2026-11-19")) - bp(at(SS, "BEI_10Y", "2026-10-23"), at(SS, "BEI_10Y", "2026-11-19"))) < 1e-9)
pts_x = P.pts
for r in pts_x:
    r["file"] = "s06"
allpts += pts_x
n = len(allpts); mis = [r for r in allpts if not r["ok"]]
json.dump(allpts, open(os.path.join(outdir, "pts_all.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
# markdown 表
L = ["| 编号 | 出处(文件+键) | 复算项 | 直算值 | 受审稿值 | 一致 |", "|---|---|---|---|---|---|"]
for r in allpts:
    cv = r.get("calc_str", ""); rv = json.dumps(r.get("report"), ensure_ascii=False) if not isinstance(r.get("report"), str) else r["report"]
    key = str(r.get("key", "")).replace("|", "/")
    L.append("| %s | %s | %s | %s | %s | %s |" % (r["id"], str(r.get("face", "")).replace("|", "/")[:150], key[:150], str(cv)[:80], str(rv)[:80], "是" if r["ok"] else "**否**"))
open(os.path.join(outdir, "points_table.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
from collections import Counter
print("TOTAL points =", n, "| mismatches =", len(mis))
print("by file:", dict(Counter(r["file"] for r in allpts)))
for r in mis:
    print("  MISMATCH", r["id"], "|", r["file"], "|", r.get("key"), "| calc=", r.get("calc_str"), "| report=", r.get("report"), "|", r.get("note"))
print("table lines", len(L))
