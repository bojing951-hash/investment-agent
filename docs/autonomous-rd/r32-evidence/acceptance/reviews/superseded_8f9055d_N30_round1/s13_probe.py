#!/usr/bin/python3 -I
# 席位自写：生成器所需的只读面结构探查(不写任何受审文件)
import json, sys, re
jp, rp, sp, cp, rgp, mp, fp, ep = sys.argv[1:9]
J = json.load(open(jp, encoding="utf-8")); R = json.load(open(rp, encoding="utf-8")); SNAP = json.load(open(sp, encoding="utf-8"))
REG = json.load(open(rgp, encoding="utf-8")); MAP = open(mp, encoding="utf-8").read(); FULL = open(fp, encoding="utf-8").read(); EIDX = json.load(open(ep, encoding="utf-8"))
def tr(v, n=260):
    s = json.dumps(v, ensure_ascii=False); return s if len(s) <= n else s[:n] + "…"
print("SNAP_TOP", [(k, type(v).__name__) for k, v in SNAP.items()][:40])
print("SNAP_META", {k: SNAP[k] for k in SNAP if not isinstance(SNAP[k], (list, dict))})
SS = SNAP["series_store"]
print("SS_KEYS_N", len(SS), sorted(k for k in SS if re.search(r"JGB|BUND|DFEDTAR|GDP|DAX|CAC|NIKKEI|DXY|EURUSD|USDJPY|VIX|SPX$|UST_10Y|ECB_|HICP|JP_CPI|JP_POLICY", k)))
k0 = "VIX"; print("SS_SAMPLE", k0, {k: (tr(v, 120) if isinstance(v, list) else v) for k, v in SS[k0].items() if k not in ("dates", "values")}, "dates0", SS[k0]["dates"][:1], SS[k0]["dates"][-1], "val_last", SS[k0]["values"][-1])
F = {f["fact_id"]: f for f in SNAP["facts"]}
print("FACTS_N", len(F), "KEYS", sorted(F[next(iter(F))].keys()))
for fid in ("JGB2Y@2026-11-19", "JGB5Y@2026-11-19", "JGB10Y@2026-11-19", "ECB_MRO@2026-09-16", "ECB_DFR@2026-09-16", "DFEDTARL@2026-11-23", "DFEDTARU@2026-11-23", "UST_10Y@2026-11-19", "JP_CPI_YOY@2026-10-01", "EA_HICP_YOY@2026-10-01", "EA_REAL_GDP_YOY@2026-07-01", "JP_REAL_GDP_YOY@2026-07-01"):
    f = F.get(fid)
    print("  FACT", fid, "MISSING" if f is None else tr({k: f[k] for k in f if k not in ("provenance",)}, 330))
print("GA_KEYS", list(SNAP["gate_a"].keys()))
print("GA_DETAIL", tr(SNAP["gate_a"].get("noncore_missing_detail"), 900))
print("REG_TOP", type(REG).__name__, (list(REG.keys())[:12] if isinstance(REG, dict) else len(REG)))
M = REG.get("metrics") if isinstance(REG, dict) else REG
print("REG_METRICS", type(M).__name__, len(M))
items = list(M.items()) if isinstance(M, dict) else [((m.get("metric_id") or m.get("id")), m) for m in M]
for mid in ("JP_CPI_TOKYO_YOY", "JP_CPI_YOY", "JP_POLICY_RATE", "ECB_MRO", "EA_HICP_YOY"):
    m = dict(items)[mid]
    print("  REG", mid, "keys", sorted(m.keys()))
    for k in ("calc", "release_semantics", "frequency", "economy"):
        print("     ", k, "=", tr(m.get(k), 330))
print("EIDX_KEYS", sorted(EIDX[0].keys()), "N", len(EIDX), "KINDS", sorted(set(e.get("kind") for e in EIDX)))
RP = R["research_plan"]
for c in RP["point_values"]["cells"]:
    print("CELL", c["metric_id"], "keys", sorted(c.keys()))
    for an, a in c["anchors"].items():
        print("    ANCHOR", an, tr(a, 520))
print("QW", tr(RP["question_window"], 400))
print("AM", tr(RP["asset_moves"], 900))
print("URT", tr(RP["us_rates_trio"], 700))
print("STEPS0_ENV", {k: tr(v, 160) for k, v in R["steps"][0]["envelope"].items() if k not in ("data", "gate_a")})
S5 = [s for s in R["steps"] if s["step"] == "S5_compare"][0]["envelope"]["data"]
print("S5", [s["metric_id"] for s in S5["sides"]], tr(S5["alignment"], 330), "pearson_returns", S5.get("pearson_returns"), "change_basis", S5.get("change_basis"))
S6 = [s for s in R["steps"] if s["step"] == "S6_analog"][0]["envelope"]["data"]
print("S6", S6["candidates"], {k: S6["top"][0][k] for k in ("rank", "candidate_month", "distance", "n_missing")})
print("RUN_KEYS", sorted(R["run"].keys()))
print("RUN_GIT", R["run"].get("git_head"), "SNAP_ID", R["steps"][0]["envelope"].get("snapshot_id"), "TARGET", R["steps"][0]["envelope"].get("target_date"))
EJ = R["agent_judgment"]
print("EJ_NULL", {k: EJ.get(k) for k in ("agent_declaration", "l3", "l4", "reader_map", "quality_gate_notes")})
CV = EJ["contract_verification"]
print("CV", CV["version"], CV["verdict"], CV["stats"], "n_verdicts", len(CV["verdicts"]), "six", len(CV["six_checks"]), "map", len(CV["map_checks"]))
print("CHAIN_ID", J["reader_map"]["transmission"][0]["chain_id"], "| TITLE", J["reader_map"]["transmission"][0]["title"])
ML = MAP.split("\n"); FL = FULL.split("\n")
print("MAP_NL", len(ML), "FULL_NL", len(FL))
for i, l in enumerate(ML):
    if any(x in l for x in ("未核验", "四地", "4/4组", "缺数格说明", "全为周三", "Δ+20bp", "主解释 vs 竞争解释", "| 区分指标 |", "2025-06-05", "JP_POLICY_TARGET", "完整运行", "git")):
        print("  MAPL", i + 1, tr(l, 420))
for i, l in enumerate(ML[58:64], 59):
    print("  MAPPOL", i, tr(l, 520))
for i, l in enumerate(ML[146:151], 147):
    print("  MAPFO", i, tr(l, 700))
for i, l in enumerate(FL):
    if "pearson" in l:
        print("  FULLL", i + 1, tr(l, 300))
print("FULL_KEYS_SAMPLE", [tr(l, 90) for l in FL if l.startswith("#")][:40])
JALL = json.dumps(J, ensure_ascii=False)
print("CNT_STALE", JALL.count("STALE"), "无变化", JALL.count("无变化"), "维持不变", JALL.count("维持不变"), "同步", JALL.count("同步"), "相关系数", JALL.count("相关系数"), "pearson", JALL.lower().count("pearson"))
