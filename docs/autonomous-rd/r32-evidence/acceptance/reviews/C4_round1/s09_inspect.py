#!/usr/bin/python3 -I
# s09: 数字全量扫描暴露的 9 个日期与若干转述句的出处结构查看(只读, 仅打印)
import sys, os, json, re
snap_p, rep_p, cal_p, reg_p, aj_p, mapmd_p, env_p = sys.argv[1:8]
snap = json.load(open(snap_p, encoding="utf-8")); rep = json.load(open(rep_p, encoding="utf-8"))
cal = json.load(open(cal_p, encoding="utf-8")); reg = json.load(open(reg_p, encoding="utf-8"))
mapmd = open(mapmd_p, encoding="utf-8").read(); env = json.load(open(env_p, encoding="utf-8"))
SS = snap["series_store"]; rp = rep["research_plan"]
def J(o, n=900):
    s = json.dumps(o, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "…"
print("## gate_a.noncore_missing_detail")
for x in snap["gate_a"].get("noncore_missing_detail", []):
    print("  ", J(x, 420))
print("## CN_OMO_7D cells")
for c in rp["point_values"]["cells"]:
    if c["metric_id"] in ("CN_OMO_7D",):
        print("  ", J(c, 1500))
print("## us_rates_trio:", J(rp.get("us_rates_trio"), 1100))
print("## asset_moves keys:", list(rp.get("asset_moves", {}).keys()))
for k, v in rp.get("asset_moves", {}).items():
    if not isinstance(v, (list, dict)):
        print("   ", k, "=", v)
print("## evidence_index sample row:", J(rep["evidence_index"][0], 500))
srcs = set()
for r in rep["evidence_index"]:
    for k in ("snapshot_id", "snapshot", "source", "source_id"):
        if k in r:
            srcs.add((k, str(r[k])))
print("   evidence_index source-ish values:", sorted(srcs)[:8])
print("## calendar JP BOJ entries")
for e in cal["entries"]:
    if "BOJ" in str(e.get("id")):
        print("  ", J(e, 700))
print("## run.degradation_policy / evidence_gate:", J(rep["run"].get("degradation_policy"), 700), "|", J(rep["run"].get("evidence_gate"), 500))
blob = json.dumps(rep, ensure_ascii=False) + json.dumps(snap.get("notes"), ensure_ascii=False) + json.dumps(snap.get("run_note", ""), ensure_ascii=False)
for kw in ("干净安装", "历史补全"):
    i = blob.find(kw)
    print("## kw", kw, "found" if i >= 0 else "NOT FOUND", "|", blob[max(0, i - 120):i + 160].replace("\\n", " ") if i >= 0 else "")
print("## policy_doc_facts:", J(rp.get("policy_doc_facts"), 500))
print("## rep.agent_judgment.schema_version:", rep["agent_judgment"].get("schema_version"), "| run.ts_utc:", rep["run"].get("ts_utc"))
ms = reg.get("metrics") or reg
if isinstance(ms, list):
    for m in ms:
        if m.get("metric_id") == "JP_REAL_GDP_YOY":
            print("## registry JP_REAL_GDP_YOY:", J({k: m.get(k) for k in ("metric_id", "frequency", "unit", "display_name")}, 400))
else:
    m = ms.get("JP_REAL_GDP_YOY") if isinstance(ms, dict) else None
    print("## registry JP_REAL_GDP_YOY:", J(m, 500) if m else "n/a; registry keys %s" % list(reg.keys())[:8])
print("## envelope.reader_map_contract:", J(env.get("reader_map_contract"), 1500))
for kw in ("一年窗路径", "近30日", "政策分化"):
    for m in list(re.finditer(re.escape(kw), mapmd))[:2]:
        print("## MAP_REPORT ctx[%s]: …%s…" % (kw, mapmd[max(0, m.start() - 60):m.end() + 200].replace("\n", " ⏎ ")))
