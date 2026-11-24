# -*- coding: utf-8 -*-
"""s00_structure.py — 只读: 打印冻结快照 / report.json 顶层结构(键与规模),不写任何文件。"""
import json, sys

def describe(obj, depth=0, maxdepth=2, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            t = type(v).__name__
            n = len(v) if isinstance(v, (dict, list, str)) else ""
            sample = ""
            if isinstance(v, (int, float, bool)) or v is None:
                sample = repr(v)
            elif isinstance(v, str) and len(v) < 120:
                sample = repr(v)
            elif isinstance(v, list) and v and not isinstance(v[0], (dict, list)) and len(v) < 12:
                sample = repr(v)
            elif isinstance(v, list) and v and isinstance(v[0], dict):
                sample = "item_keys=" + ",".join(list(v[0].keys())[:14])
            print("  " * depth + f"{prefix}{k}: {t}({n}) {sample}")
            if depth < maxdepth and isinstance(v, dict):
                describe(v, depth + 1, maxdepth)

snap_path, rep_path = sys.argv[1], sys.argv[2]
with open(snap_path, encoding="utf-8") as f:
    snap = json.load(f)
print("===== SNAPSHOT top-level =====")
describe(snap, 0, 0)
print("research_as_of:", snap.get("research_as_of"))
print("target_date:", snap.get("target_date"))
for k in ("as_of", "snapshot_date", "generated_at", "collected_at", "version", "schema_version"):
    if k in snap:
        print(k, "=", snap[k])
ss = snap["series_store"]
print("series_store type:", type(ss).__name__, "len:", len(ss))
ks = list(ss.keys()) if isinstance(ss, dict) else []
print("series_store keys (%d):" % len(ks))
print(ks)
print("first series sample key:", ks[0])
print(json.dumps(ss[ks[0]], ensure_ascii=False)[:600])
print("facts type:", type(snap["facts"]).__name__, "len:", len(snap["facts"]))
f0 = snap["facts"]
if isinstance(f0, list):
    print(json.dumps(f0[0], ensure_ascii=False)[:600])
elif isinstance(f0, dict):
    k0 = list(f0.keys())[0]
    print("fact key sample:", k0)
    print(json.dumps(f0[k0], ensure_ascii=False)[:600])
print("gate_a keys:", list(snap["gate_a"].keys()))
print("quality keys:", list(snap["quality"].keys()) if isinstance(snap["quality"], dict) else type(snap["quality"]))

print()
print("===== report.json top-level =====")
with open(rep_path, encoding="utf-8") as f:
    rep = json.load(f)
describe(rep, 0, 0)
print("run keys:", list(rep["run"].keys()))
print("research_plan keys:", list(rep["research_plan"].keys()))
print("layers keys:", list(rep["layers"].keys()))
aj = rep.get("agent_judgment", {})
print("report.agent_judgment keys:", list(aj.keys()))
cv = aj.get("contract_verification", {})
print("contract_verification keys:", list(cv.keys()) if isinstance(cv, dict) else type(cv))
print("steps n:", len(rep.get("steps", [])))
for s in rep.get("steps", []):
    env = s.get("envelope", {}) if isinstance(s, dict) else {}
    print(" step:", s.get("name") or s.get("step") or s.get("id"), "| keys:", list(s.keys())[:10], "| env keys:", list(env.keys())[:16])
