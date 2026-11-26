import json, sys
snap_p, ej_p, reg_p = sys.argv[1], sys.argv[2], sys.argv[3]
with open(snap_p) as f: s = json.load(f)
with open(ej_p) as f: e = json.load(f)
with open(reg_p) as f: reg = json.load(f)
for f_ in s["facts"]:
    if "JGB" in f_["metric_id"]:
        print(json.dumps(f_, ensure_ascii=False))
        print()
refs = sorted(set(r["ref"] for r in e))
print("evidence index refs (%d):" % len(refs))
print(refs)
ms = {m["metric_id"]: m for m in reg["metrics"]}
for m in ("JGB10Y","JGB2Y","JGB5Y"):
    x = ms.get(m)
    print(m, "registry:", json.dumps({k: x.get(k) for k in ("status","frequency","source","criticality","freshness","calendar","release_date_available")}, ensure_ascii=False) if x else None)
print("sources_status keys:", list(s["sources_status"].keys()) if isinstance(s["sources_status"], dict) else type(s["sources_status"]))
ss = s["sources_status"]
for k, v in (ss.items() if isinstance(ss, dict) else []):
    if "jp" in k.lower() or "japan" in k.lower():
        print(" ", k, "=", json.dumps(v, ensure_ascii=False)[:700])
