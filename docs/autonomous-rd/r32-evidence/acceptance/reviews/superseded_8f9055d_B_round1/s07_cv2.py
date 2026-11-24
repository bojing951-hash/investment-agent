import json, sys
rep = sys.argv[1]
with open(rep) as f: p = json.load(f)
aj = p["agent_judgment"]
cv = aj["contract_verification"]
print("cv keys:", list(cv.keys()))
for k, v in cv.items():
    if k in ("verdicts",): continue
    print(f"--- {k}")
    print(json.dumps(v, ensure_ascii=False, indent=1)[:7000])
print("== semantic_review ==")
print(json.dumps(p["semantic_review"], ensure_ascii=False, indent=1)[:2500])
print("== layers keys ==", list(p["layers"].keys()))
for k in p["layers"]:
    v = p["layers"][k]
    print(k, type(v).__name__, (list(v.keys()) if isinstance(v, dict) else len(v)))
