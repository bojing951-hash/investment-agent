#!/usr/bin/python3 -I
import sys, json
snap = json.load(open(sys.argv[1], encoding="utf-8"))
print("research_as_of", snap["research_as_of"], "target_date", snap["target_date"], "tz", snap["timezone"])
print("quality", json.dumps(snap["quality"], ensure_ascii=False))
print("gate_a", json.dumps(snap["gate_a"], ensure_ascii=False)[:3000])
print("notes", json.dumps(snap["notes"], ensure_ascii=False))
for mid in ["CPI", "JP_POLICY_RATE", "SPX"]:
    s = snap["series_store"][mid]
    print(mid, list(s.keys()), len(s["dates"]), s["dates"][:3], s["values"][:3], s["dates"][-3:], s["values"][-3:])
print("facts[0..3]", json.dumps(snap["facts"][:3], ensure_ascii=False))
print("fed_futures_curve[0]", json.dumps(snap["fed_futures_curve"][0], ensure_ascii=False))
print("series_store_clean.CPI", json.dumps(snap["series_store_clean"]["CPI"], ensure_ascii=False)[:800])
