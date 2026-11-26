#!/usr/bin/python3 -I
# 席位自写：生成器所需的只读面结构探查(二)(只读)
import json, sys, re
jp, rp, mp, fp = sys.argv[1:5]
J = json.load(open(jp, encoding="utf-8")); R = json.load(open(rp, encoding="utf-8"))
MAP = open(mp, encoding="utf-8").read(); FULL = open(fp, encoding="utf-8").read()
def tr(v, n=260):
    s = json.dumps(v, ensure_ascii=False); return s if len(s) <= n else s[:n] + "…"
ST = [s for s in R["steps"] if isinstance(s.get("envelope"), dict)]
print("STEPS", len(R["steps"]), "with_envelope", len(ST), "executed", sum(1 for s in R["steps"] if s.get("executed")))
s0 = ST[0]
print("STEP0", s0["step"], {k: tr(v, 200) for k, v in s0["envelope"].items() if k not in ("data", "gate_a")})
print("RA_IN_J", "2026-11-23T22:53:47+08:00" in json.dumps(J, ensure_ascii=False))
S5 = [s for s in ST if s["step"] == "S5_compare"][0]["envelope"]["data"]
print("S5", [s["metric_id"] for s in S5["sides"]], tr(S5["alignment"], 330), "pearson_returns", S5.get("pearson_returns"), "change_basis", S5.get("change_basis"))
S6 = [s for s in ST if s["step"] == "S6_analog"][0]["envelope"]["data"]
print("S6", S6["candidates"], {k: S6["top"][0][k] for k in ("rank", "candidate_month", "distance", "n_missing")})
print("RUN_KEYS", sorted(R["run"].keys()))
print("RUN_GIT", R["run"].get("git_head"), "SNAP_ID", s0["envelope"].get("snapshot_id"), "TARGET", s0["envelope"].get("target_date"), "RA", s0["envelope"].get("research_as_of"))
print("R_TOP", sorted(R.keys()))
EJ = R["agent_judgment"]
print("EJ_NULL", {k: EJ.get(k) for k in ("agent_declaration", "l3", "l4", "reader_map", "quality_gate_notes")})
CV = EJ["contract_verification"]
print("CV", CV["version"], CV["verdict"], CV["stats"], "n_verdicts", len(CV["verdicts"]), "six", len(CV["six_checks"]), "map", len(CV["map_checks"]))
print("CHAIN_ID", J["reader_map"]["transmission"][0]["chain_id"], "| TITLE", J["reader_map"]["transmission"][0]["title"])
ML = MAP.split("\n"); FL = FULL.split("\n")
print("MAP_NL", len(ML), "FULL_NL", len(FL))
for i, l in enumerate(ML):
    if any(x in l for x in ("未核验", "四地", "4/4组", "缺数格说明", "全为周三", "Δ+20bp", "主解释 vs 竞争解释", "| 区分指标 |", "2025-06-05", "JP_POLICY_TARGET", "完整运行")):
        print("  MAPL", i + 1, tr(l, 460))
for i in range(58, 66):
    print("  MAPPOL", i + 1, tr(ML[i], 330))
for i in range(146, 151):
    print("  MAPFO", i + 1, tr(ML[i], 520))
for i, l in enumerate(FL):
    if "pearson" in l:
        print("  FULLL", i + 1, tr(l, 300))
print("FULL_HEADS", [tr(l, 70) for l in FL if l.startswith("#")])
JALL = json.dumps(J, ensure_ascii=False)
print("CNT_STALE", JALL.count("STALE"), "无变化", JALL.count("无变化"), "维持不变", JALL.count("维持不变"), "同步", JALL.count("同步"), "相关系数", JALL.count("相关系数"), "pearson", JALL.lower().count("pearson"), "全为周三", JALL.count("全为周三"))
print("AD", tr(J["agent_declaration"], 200))
