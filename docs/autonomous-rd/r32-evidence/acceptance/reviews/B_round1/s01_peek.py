#!/usr/bin/python3 -I
"""s01: 只读查看 series_store 单条 / facts 条目 / gate_a / quality 的结构."""
import json, sys
snap = json.load(open(sys.argv[1], encoding="utf-8"))
ss = snap["series_store"]
for mid in ["CPI", "JP_POLICY_RATE", "EA_HICP_YOY", "SPX"]:
    e = ss[mid]
    print(mid, "keys=", list(e.keys()))
    for k, v in e.items():
        if isinstance(v, list):
            print("   ", k, "len", len(v), "head", v[:3], "tail", v[-4:])
        else:
            print("   ", k, repr(v)[:300])
print("facts[0]=", json.dumps(snap["facts"][0], ensure_ascii=False))
print("facts keys union=", sorted({k for f in snap["facts"] for k in f}))
print("n facts", len(snap["facts"]))
print("gate_a=", json.dumps(snap["gate_a"], ensure_ascii=False, indent=1)[:6000])
print("quality=", json.dumps(snap["quality"], ensure_ascii=False))
print("notes=", json.dumps(snap["notes"], ensure_ascii=False))
print("sources_status=", json.dumps(snap["sources_status"], ensure_ascii=False))
