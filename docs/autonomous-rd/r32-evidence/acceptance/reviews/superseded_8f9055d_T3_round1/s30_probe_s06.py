#!/usr/bin/python3 -I
"""Probe: show supplement S06 and locate the registry phrases used in the findings.
Read-only. Args: <out_dir> <metric_registry.json>
"""
import json
import os
import sys

out_dir, regp = sys.argv[1], sys.argv[2]
S = json.load(open(os.path.join(out_dir, "supplement.json"), "r", encoding="utf-8"))
for s in S:
    if s["id"] == "S06":
        print(json.dumps(s, ensure_ascii=False, indent=1))
reg = json.load(open(regp, "r", encoding="utf-8"))
regm = {m["metric_id"]: m for m in reg["metrics"]}
m = regm["EA_HICP_YOY"]
print("EA_HICP_YOY keys:", sorted(m.keys()))
for k, v in m.items():
    t = json.dumps(v, ensure_ascii=False)
    print("  [%s] len=%d :: %s" % (k, len(t), t[:900]))
for q in ("HICP流程对近月含回溯修订", "2025-12 值1.9→2.0", "latest_vintage_asof_collected", "决策驱动政策目标序列",
          "观测日=政策最后确认/变更日", "无更晚已证实决议不作过期", "利率长期不变≠数据停更", "终值"):
    hits = []
    for mid, mm in regm.items():
        for k, v in mm.items():
            t = json.dumps(v, ensure_ascii=False)
            if q in t:
                i = t.find(q)
                hits.append((mid, k, t[max(0, i - 80):i + len(q) + 120]))
    print("QUOTE", q, "->", len(hits), "hit(s)")
    for h in hits[:4]:
        print("     ", h)
