#!/usr/bin/python3 -I
"""s02: 只读抽取 report.json 引擎面到席位目录中间表(仅供席位复核)."""
import json, sys
rp_path, out_dir = sys.argv[1], sys.argv[2]
rp = json.load(open(rp_path, encoding="utf-8"))
def dump(name, obj):
    with open(f"{out_dir}/{name}", "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    print(name, "written; top keys:", list(obj.keys()) if isinstance(obj, dict) else type(obj).__name__)
dump("x_run.json", rp["run"])
dump("x_research_plan.json", rp["research_plan"])
dump("x_agent_judgment_meta.json", {k: v for k, v in rp["agent_judgment"].items()})
dump("x_semantic_review.json", rp["semantic_review"])
dump("x_notes.json", rp["notes"])
# steps: index, name, keys
steps = rp["steps"]
summary = []
for i, s in enumerate(steps):
    d = {"i": i}
    for k, v in s.items():
        if isinstance(v, (dict, list)):
            d[k] = f"<{type(v).__name__} len={len(v)}>" + (f" keys={list(v.keys())}" if isinstance(v, dict) and len(v) < 40 else "")
        else:
            d[k] = v
    summary.append(d)
dump("x_steps_summary.json", summary)
for row in summary:
    print(row)
dump("x_L1.json", rp["layers"]["L1_事实层"])
dump("x_L3.json", rp["layers"]["L3_AI推断层"])
dump("x_L4.json", rp["layers"]["L4_条件情景层"])
