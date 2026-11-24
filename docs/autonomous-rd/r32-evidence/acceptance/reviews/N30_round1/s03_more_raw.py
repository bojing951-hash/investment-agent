# -*- coding: utf-8 -*-
"""s03_more_raw.py — 只读: 受审版本指纹 + 事实行告警 + 注册表 EA/JP 面 + S6/S8 信封 + 索引/信封文件。"""
import json, sys, hashlib
run_dir, reg_path = sys.argv[1], sys.argv[2]
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()
print("===== 受审版本指纹 =====")
for f in ("agent_judgment.json", "report.json", "root_overlay/data/daily/research_snapshot_20261123.json",
          "root_overlay/config/release_calendar.json", "root_overlay/config/metric_registry.json", "MAP_REPORT.md", "FULL_REPORT.md", "report.md"):
    print(f, sha(run_dir + "/" + f)[:16])

snap = json.load(open(run_dir + "/root_overlay/data/daily/research_snapshot_20261123.json", encoding="utf-8"))
rep = json.load(open(run_dir + "/report.json", encoding="utf-8"))
reg = json.load(open(reg_path, encoding="utf-8"))

print("\n===== fact rows (full) for WARN/DEGRADED plan metrics =====")
for f in snap["facts"]:
    if f["metric_id"] in ("JP_CPI_YOY", "EA_HICP_YOY", "JP_POLICY_RATE", "ECB_DFR", "ECB_MRO"):
        print(json.dumps(f, ensure_ascii=False)[:2600])
        print()

print("===== reconciliation =====")
print(json.dumps(snap.get("reconciliation"), ensure_ascii=False)[:3000])
print("notes:", json.dumps(snap.get("notes"), ensure_ascii=False))
print("series_store_clean keys:", list(snap["series_store_clean"].keys()))

print("\n===== registry: economy EA/JP metrics =====")
ms = reg["metrics"]
print("n=", len(ms), "type=", type(ms).__name__)
for m in ms:
    if str(m.get("economy", "")).upper() in ("EA", "JP"):
        print(" ", m["metric_id"], "|", m.get("display_name"), "|", m.get("criticality"), "|", m.get("status"), "| freq", m.get("frequency"))
ids = [m["metric_id"] for m in ms]
for k in ("JP_POLICY_TARGET", "JP_CORE_CPI_YOY", "EA_CORE_HICP_YOY", "EA_HICP_CORE_YOY", "JP_CPI_CORE_YOY", "CORE_CPI"):
    print(" registry has", k, ":", k in ids)
print(" ids containing CORE/HICP/CPI:", [i for i in ids if "CORE" in i or "HICP" in i or "CPI" in i])
print(" ids containing POLICY/TARGET:", [i for i in ids if "POLICY" in i or "TARGET" in i or "ECB" in i or "BOJ" in i])
print(" field_semantics:", json.dumps(reg.get("field_semantics"), ensure_ascii=False)[:1500])

print("\n===== steps: S6_analog / S8 / S3_changes / S5 envelopes (data keys + head) =====")
for st in rep["steps"]:
    if st.get("step") in ("S6_analog", "S8_grounded_qa", "S3_changes", "S5_compare", "S2_doctor", "S3_overview_EA", "S3_overview_JP"):
        env = st.get("envelope", {})
        print("---", st["step"], "| ok", st.get("ok"), "| semantic_ok", st.get("semantic_ok"), "| note", st.get("note"))
        d = env.get("data", {})
        print("   data keys:", list(d.keys()) if isinstance(d, dict) else type(d).__name__)
        print("   warnings:", json.dumps(env.get("warnings"), ensure_ascii=False)[:600])
        for k, v in (d.items() if isinstance(d, dict) else []):
            s = json.dumps(v, ensure_ascii=False)
            print(f"   data.{k}: {s[:900]}")

def find(obj, targets, path=""):
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out += find(v, targets, path + "." + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:400]):
            out += find(v, targets, path + f"[{i}]")
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        if any(abs(obj - t) < 1e-9 for t in targets):
            out.append((path, obj))
    return out
s6 = [s for s in rep["steps"] if s.get("step") == "S6_analog"][0]["envelope"]
print("\nS6 search 1871 / 74 / 0.727212:", find(s6, [1871, 74, 0.727212])[:30])

print("\n===== L1 rows in report.json =====")
l1 = rep["layers"]["L1_事实层"]
print("L1 keys:", list(l1.keys()))
for r in l1.get("rows", []):
    print("  ", json.dumps(r, ensure_ascii=False)[:300])

print("\n===== evidence_index.json =====")
ei = json.load(open(run_dir + "/evidence_index.json", encoding="utf-8"))
print(type(ei).__name__, list(ei.keys()) if isinstance(ei, dict) else len(ei))
rows = ei if isinstance(ei, list) else ei.get("rows", ei.get("items", []))
print("n rows:", len(rows))
refs = [r.get("ref") for r in rows]
print("snapshot_fact refs:", [x for x in refs if x.startswith("snapshot_fact")])
for k in ("BUND_10Y", "BUND_2Y", "JGB2Y", "JGB5Y", "JGB10Y", "DFEDTARU", "DFEDTARL", "EA_REAL_GDP_YOY", "JP_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "DXY", "CAC40"):
    print("  in evidence index:", k, any(x.startswith(k + "@") for x in refs))
rep_refs = [e["ref"] for e in rep["evidence_index"]]
print("report.evidence_index n:", len(rep_refs), "| identical to evidence_index.json:", rep_refs == refs)

print("\n===== views_digest.json =====")
print(open(run_dir + "/views_digest.json", encoding="utf-8").read())
print("\n===== AGENT_SEAT_ENVELOPE.json (keys + head) =====")
ase = json.load(open(run_dir + "/AGENT_SEAT_ENVELOPE.json", encoding="utf-8"))
print("keys:", list(ase.keys()))
for k, v in ase.items():
    s = json.dumps(v, ensure_ascii=False)
    print(f"  {k}: {s[:1100]}")
print("\n===== MAP_REPORT.sha256 =====")
print(open(run_dir + "/MAP_REPORT.sha256", encoding="utf-8").read(), "| actual:", sha(run_dir + "/MAP_REPORT.md"))
