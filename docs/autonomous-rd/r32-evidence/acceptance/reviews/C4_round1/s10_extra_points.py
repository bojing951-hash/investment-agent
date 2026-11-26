#!/usr/bin/python3 -I
# s10: 数字全量扫描补点(X19 收紧 + X21..X43)并打印对应引擎面结构。只读; 产出只写本席目录; 可重复运行(按编号替换)。
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rc_lib import *
snap_p, rep_p, cal_p, reg_p, aj_p, mapmd_p, env_p, outdir = sys.argv[1:9]
snap, rep, cal, reg, aj = load(snap_p, rep_p, cal_p, reg_p, aj_p)
mapmd = open(mapmd_p, encoding="utf-8").read(); env = json.load(open(env_p, encoding="utf-8"))
SS = snap["series_store"]; rp = rep["research_plan"]; F = "snapshot.series_store"
def J(o, n=600):
    s = json.dumps(o, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "…"
def ctx(blob, kw, a=140, b=260, maxn=2):
    out = []
    for m in list(re.finditer(re.escape(kw), blob))[:maxn]:
        out.append("…" + blob[max(0, m.start() - a):m.end() + b].replace("\\n", " ").replace("\n", " ") + "…")
    return out or ["NOT FOUND"]
blob_all = json.dumps(snap, ensure_ascii=False)
blob_rp = json.dumps(rep, ensure_ascii=False)
blob_env = json.dumps(env, ensure_ascii=False)
print("=== (a) 缺口明细文字出处 ===")
for kw in ("ea:MISSING", "注册表未登记该指标子源状态键", "档内无该指标子源状态记录", "FRED_JP_GDP", "采集器已取到而事实未生成"):
    for where, blob in (("report.json", blob_rp), ("snapshot", blob_all), ("envelope", blob_env)):
        c = ctx(blob, kw, 60, 200, 1)
        if c[0] != "NOT FOUND":
            print("  [%s] in %s: %s" % (kw, where, c[0]))
print("=== (b) 日历条目键名与日本央行条目 ===")
print("  entry keys:", sorted(cal["entries"][0].keys()))
boj = [e for e in cal["entries"] if "1.25" in J(e, 4000) or "BOJ" in J(e, 4000)]
for e in boj:
    print("  ", J(e, 620))
print("=== (c) 『干净安装/历史补全』出处 ===")
for kw in ("干净", "补全", "降级安装", "降级面"):
    for where, blob in (("report.json", blob_rp), ("snapshot", blob_all), ("envelope", blob_env)):
        c = ctx(blob, kw, 80, 160, 1)
        if c[0] != "NOT FOUND":
            print("  [%s] in %s: %s" % (kw, where, c[0]))
print("=== (d) 政策一年窗路径(日本/美国) ===")
for m in re.finditer(r"政策一年窗路径\*\* [^\n]{0,420}", mapmd):
    line = m.group(0)
    if any(k in line for k in ("无担保", "联邦基金", "DFEDTARU", "上限")):
        print("  ", line[:430])
print("=== (e) 信封: 历史段数规则 ===")
for m in list(re.finditer(r"历史[^\n]{0,60}?(0\.\.|0~|0-|0–|至多|最多|≤) ?3", blob_env))[:4]:
    print("  …" + blob_env[max(0, m.start() - 60):m.end() + 60] + "…")
for kw in ("history_periods", "零段"):
    print("  [%s]" % kw, ctx(blob_env, kw, 120, 260, 2))
print("=== (f) evidence_index kind 取值 ===", sorted(set(str(r.get("kind")) for r in rep["evidence_index"])), "| rows", len(rep["evidence_index"]))
txt = json.dumps(aj, ensure_ascii=False)
txt2 = re.sub(r"20\d\d-\d\d-\d\d", " ", txt)
yms = sorted(set(re.findall(r"(?<!\d)(20\d\d)-(0[1-9]|1[0-2])(?!\d)", txt2)))
print("=== (g) 受审稿 YYYY-MM 取值:", sorted(set("%s-%s" % t for t in yms)))
# ---------------- 补点 ----------------
pts = json.load(open(os.path.join(outdir, "pts_all.json"), encoding="utf-8"))
P = Points()
cells = {c["metric_id"]: c for c in rp["point_values"]["cells"]}
lat = cells["CN_OMO_7D"]["anchors"]["最新一期"]
P.addb("X19", "report.json research_plan.point_values.cells[CN_OMO_7D].anchors[最新一期].freshness*", "七天逆回购最新一格: freshness=stale、freshness_lag_days=24、freshness_window_days=10(受审稿『引擎注记为过期: 末观测滞后二十四天、超出十天发布频率窗口』)", lat.get("freshness") == "stale" and lat.get("freshness_lag_days") == 24 and lat.get("freshness_window_days") == 10, str(lat.get("freshness_note"))[:220])
for i, mid in enumerate(("CN_CPI_YOY", "CN_PPI_YOY", "UNEMPLOYMENT", "CN_PMI_MFG")):
    P.adds("X%d" % (21 + i), F + ".%s@<=2026-08-23" % mid, "%s 三个月前锚观测日(受审稿『观测 2026-07-01』; 月频序列按月首日记)" % mid, at_or_before(SS, mid, ANC)[0], "2026-07-01")
P.adds("X25", F + ".CORE_CPI 2026-08 观测", "CORE_CPI 2026-08 观测日(受审稿『窗口终点 2026-08-01 略早于三个月前锚』)", [d for d, v in series(SS, "CORE_CPI") if d.startswith("2026-08")][0], "2026-08-01")
P.adds("X26", F + ".CORE_PCE 末观测", "CORE_PCE 最新水平观测日(受审稿『观测 2026-09-01』/证据索引引用 CORE_PCE@2026-09-01)", last(SS, "CORE_PCE")[0], "2026-09-01")
urt = rp["us_rates_trio"]
P.adds("X27", "report.json research_plan.us_rates_trio.window.from", "共同交易日三利率窗起(受审稿『近一月共同交易日窗(2026-10-20→2026-11-19)』)", urt["window"]["from"], "2026-10-20")
P.adds("X28", "report.json research_plan.us_rates_trio.window_12m.from", "12 个月窗起(受审稿『12 个月窗(2025-11-19→2026-11-19)』)", urt["window_12m"]["from"], "2025-11-19")
P.addb("X29", "report.json research_plan.asset_moves.window_rule", "资产月窗规则含 2026-10-23 与 2026-11-23(受审稿『引擎近一月窗(2026-10-23→2026-11-23)』)", "2026-10-23" in rp["asset_moves"]["window_rule"] and "2026-11-23" in rp["asset_moves"]["window_rule"], rp["asset_moves"]["window_rule"])
P.adds("X30", "report.json research_plan.policy_doc_facts[0].published_on", "FOMC 2026年10月会议纪要发布日(受审稿『2026-11-18 发布』)", rp["policy_doc_facts"][0]["published_on"], "2026-11-18")
P.adds("X31", "report.json run.ts_utc", "运行标识(受审稿『降级面开放问句 20261123T235101Z』)", rep["run"]["ts_utc"], "20261123T235101Z")
P.adds("X32", "report.json run.evidence_gate.source_snapshot_id", "证据门源快照(受审稿『全部取自本工单冻结快照 research_snapshot_20261123』)", rep["run"]["evidence_gate"].get("source_snapshot_id"), "research_snapshot_20261123")
P.addb("X33", "report.json evidence_index[*].kind", "证据索引 69 行 kind 全为 snapshot_fact(受审稿『全部取自本工单冻结快照』)", all(r.get("kind") == "snapshot_fact" for r in rep["evidence_index"]), str(sorted(set(str(r.get("kind")) for r in rep["evidence_index"]))))
P.add("X34", F + ".VIX@2026-10-23", "VIX 引擎窗起值两位小数(受审稿『19.45→27.01』『19.45→35.89』)", round(at(SS, "VIX", "2026-10-23"), 2), 19.45, 2)
_dec = []; _eff = []
for e in boj:
    d = J(e, 5000)
    _dec += re.findall(r'"(decision[a-z_]*|decision_on|decided_on)": "(20\d\d-\d\d-\d\d)"', d)
    _eff += re.findall(r'"(effective[a-z_]*|effective_on)": "(20\d\d-\d\d-\d\d)"', d)
print("=== (b2) 日本央行条目日期字段: decision=%s effective=%s" % (_dec, _eff))
P.adds("X35", "release_calendar.json entries[RC-JP-BOJ-TARGET-2026-09].decision*", "日本央行 2026-09 决议日(受审稿『2026-09-18 决议』)", [v for k, v in _dec if v.startswith("2026-09")][0] if any(v.startswith("2026-09") for k, v in _dec) else "NOT FOUND", "2026-09-18")
P.adds("X36", "release_calendar.json entries[RC-JP-BOJ-TARGET-2026-09].effective*", "日本央行 2026-09 生效日(受审稿『2026-09-24 生效』)", [v for k, v in _eff if v.startswith("2026-09")][0] if any(v.startswith("2026-09") for k, v in _eff) else "NOT FOUND", "2026-09-24")
_jp = [m.group(0) for m in re.finditer(r"政策一年窗路径\*\* [^\n]{0,420}", mapmd) if "无担保" in m.group(0)]
P.addb("X37", "MAP_REPORT.md『政策一年窗路径』面板 × snapshot.series_store.JP_POLICY_RATE", "引擎『政策一年窗路径』面板载有日本无担保隔夜拆借利率窗路径(受审稿称 +75bp 与该面板同口径); 独立复算 2025-11 月均 0.478→2026-10 月均 1.227 = +74.9bp", len(_jp) >= 1 and abs((at_month(SS, "JP_POLICY_RATE", "2026-10")[1] - at_month(SS, "JP_POLICY_RATE", "2025-11")[1]) * 100 - 75) < 0.5, (_jp[0][:300] if _jp else "NOT FOUND"))
ms = reg.get("metrics") if isinstance(reg, dict) else reg
_j = [m for m in ms if isinstance(m, dict) and m.get("metric_id") == "JP_REAL_GDP_YOY"] if isinstance(ms, list) else []
P.addb("X38", "metric_registry.json metrics[JP_REAL_GDP_YOY].frequency", "日本实际 GDP 同比为季频(受审稿『JP_REAL_GDP_YOY 仅季频』)", bool(_j) and _j[0].get("frequency") == "quarterly", str(_j[0].get("frequency")) if _j else "NOT FOUND")
_h = re.findall(r"历史[^\n]{0,60}?(0\.\.|0~|0-|0–|至多|最多|≤) ?3", blob_env)
P.addb("X39", "AGENT_SEAT_ENVELOPE.json reader_map_contract", "契约对历史类比段数设 0..3 上限(受审稿『契约允许 0..3 段』)", len(_h) >= 1, ("…" + _h[0] + "…") if _h else "NOT FOUND(待人工读取信封原文)")
P.adds("X40", "report.json agent_judgment.schema_version", "研判档 schema 版本(受审稿 schema_version 1.1)", str(rep["agent_judgment"].get("schema_version")), "1.1")
new = P.pts
for r in new:
    r["file"] = "s10"
ids_new = set(r["id"] for r in new)
keep = [r for r in pts if r["id"] not in ids_new and r["id"] != "X19"]
allpts = keep + new
order = {"pts_a.json": 0, "pts_b.json": 1, "pts_c.json": 2, "pts_d.json": 3, "s06": 4, "s08": 5, "s10": 6}
allpts.sort(key=lambda r: (order.get(r["file"], 9), r["id"]))
json.dump(allpts, open(os.path.join(outdir, "pts_all.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
L = ["| 编号 | 出处(文件+键) | 复算项 | 直算值 | 受审稿值 | 一致 |", "|---|---|---|---|---|---|"]
for r in allpts:
    rv = json.dumps(r.get("report"), ensure_ascii=False) if not isinstance(r.get("report"), str) else r["report"]
    L.append("| %s | %s | %s | %s | %s | %s |" % (r["id"], str(r.get("face", "")).replace("|", "/")[:150], str(r.get("key", "")).replace("|", "/")[:150], str(r.get("calc_str", ""))[:80], str(rv)[:80], "是" if r["ok"] else "**否**"))
open(os.path.join(outdir, "points_table.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n=== 新增/收紧点 ===")
for r in new:
    print(r["id"], "|", str(r.get("calc_str"))[:90], "|", json.dumps(r.get("report"), ensure_ascii=False)[:40], "|", r["ok"], "|", (r.get("note") or "")[:230])
mis = [r["id"] for r in allpts if not r["ok"]]
print("FINAL points=%d mismatches=%d %s" % (len(allpts), len(mis), mis))
