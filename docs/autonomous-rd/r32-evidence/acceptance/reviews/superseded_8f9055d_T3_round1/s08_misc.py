#!/usr/bin/python3 -I
"""Misc read-only probes. Args: <report.json> <snapshot.json> <registry.json>"""
import json
import sys

rep = json.load(open(sys.argv[1], "r", encoding="utf-8"))
snap = json.load(open(sys.argv[2], "r", encoding="utf-8"))
reg = json.load(open(sys.argv[3], "r", encoding="utf-8"))
print("PYOK")
for st in rep["steps"]:
    if st.get("step") in ("S6_analog", "S7_mode_gate", "S10_selfcheck", "S1_decompose", "S8_grounded_qa"):
        env = st.get("envelope") or {}
        print("STEP", st.get("step"), "keys", list(st.keys()))
        for k, v in env.items():
            if k == "data":
                for kk, vv in v.items():
                    s = json.dumps(vv, ensure_ascii=False)
                    print("   data.%s: %s len=%d :: %s" % (kk, type(vv).__name__, len(s), s[:700]))
            else:
                s = json.dumps(v, ensure_ascii=False)
                print("   %s: %s" % (k, s[:300]))
        df = st.get("deterministic_face")
        if df is not None and st.get("step") != "S8_grounded_qa":
            s = json.dumps(df, ensure_ascii=False)
            print("   deterministic_face len", len(s), "::", s[:600])
print("=== gate_a keys", list(snap["gate_a"].keys()))
for k, v in snap["gate_a"].items():
    print("  ", k, "=", json.dumps(v, ensure_ascii=False)[:900])
print("=== quality", json.dumps(snap["quality"], ensure_ascii=False)[:1500])
print("=== series_store n", len(snap["series_store"]))
print("has DFEDTARU", "DFEDTARU" in snap["series_store"], "DFEDTARL", "DFEDTARL" in snap["series_store"], "EURJPY", "EURJPY" in snap["series_store"])
print("=== registry full ECB_MRO")
for m in reg["metrics"]:
    if m["metric_id"] in ("ECB_MRO", "JP_CPI_YOY", "JP_POLICY_RATE", "JP_CPI_TOKYO_YOY", "EA_HICP_YOY"):
        print(json.dumps(m, ensure_ascii=False)[:2600])
        print()
print("registry version", reg.get("version"), "top keys", list(reg.keys()))
