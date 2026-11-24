import json, sys
snap = sys.argv[1]
with open(snap) as f: s = json.load(f)
ga = s["gate_a"]
for k, v in ga.items():
    print(f"--- gate_a.{k}: {json.dumps(v, ensure_ascii=False)[:3000]}")
print("== quality ==", json.dumps(s["quality"], ensure_ascii=False)[:2000])
print("== notes ==", json.dumps(s["notes"], ensure_ascii=False)[:3000])
print("== series_store_notes ==", json.dumps(s["series_store_notes"], ensure_ascii=False)[:3000])
print("== series_provenance ==", json.dumps(s["series_provenance"], ensure_ascii=False)[:3000])
print("== sources_status ==", json.dumps(s["sources_status"], ensure_ascii=False)[:4000])
ss = s["series_store"]
print("series_store ids:", sorted(ss))
print("series_store_clean ids:", sorted(s["series_store_clean"]))
print("fed_futures_curve:", json.dumps(s["fed_futures_curve"], ensure_ascii=False)[:1500])
