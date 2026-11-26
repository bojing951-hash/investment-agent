#!/usr/bin/python3 -I
"""席位自写探针 s14a: report.json 中与转折候选/历史类比/情景相关的引擎面键(只读)."""
import json
import re
import sys

rep = json.load(open(sys.argv[1], "r", encoding="utf-8"))
print("top keys:", list(rep.keys()))
rp = rep.get("research_plan", {})
print("research_plan keys:", list(rp.keys()))
tc = rp.get("turning_candidates", {})
print("turning_candidates keys:", list(tc.keys()))
for k, v in tc.items():
    if k != "candidates":
        print(" ", k, "=", json.dumps(v, ensure_ascii=False)[:300])
# 候选相关步骤
for key in ("steps", "pipeline_steps", "step_summary", "run_steps"):
    if key in rep:
        for st in rep[key]:
            s = json.dumps(st, ensure_ascii=False)
            if "turning" in s or "候选" in s or "analog" in s or "类比" in s:
                print(key, "->", s[:700])
# analog 面
for key in rep:
    if "analog" in key.lower() or "history" in key.lower():
        print("analog/history key:", key, json.dumps(rep[key], ensure_ascii=False)[:600])
def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, path + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o[:3]):
            walk(v, path + f"[{i}]")
    elif isinstance(o, str) and len(o) < 400 and re.search(r"turning|候选池|analog|历史类比", o):
        print("TXT", path, "=", o[:380])
walk(rp)
