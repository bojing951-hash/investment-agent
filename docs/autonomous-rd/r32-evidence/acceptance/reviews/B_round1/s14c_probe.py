#!/usr/bin/python3 -I
"""席位自写探针 s14c: S6_analog 引擎面的候选结构(只读)."""
import json
import sys

rep = json.load(open(sys.argv[1], "r", encoding="utf-8"))
st = [s for s in rep["steps"] if s.get("step") == "S6_analog"][0]
data = st["envelope"]["data"]
print("data keys:", list(data.keys()))
for k, v in data.items():
    s = json.dumps(v, ensure_ascii=False)
    print(f"-- {k}: {s[:520]}")
