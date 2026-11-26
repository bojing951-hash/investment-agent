import json, sys
rep = sys.argv[1]
with open(rep) as f: p = json.load(f)
rp = p["research_plan"]
pv = rp["point_values"]
print("point_values keys:", list(pv.keys()))
for c in pv["cells"]:
    print("###", c["region"], c["dimension"], c["metric_id"], "|", c.get("display_name"), "| vintage:", c.get("vintage_semantics"))
    for an, a in c["anchors"].items():
        print("   ", an, json.dumps(a, ensure_ascii=False))
for k in pv:
    if k != "cells":
        print(k, "=", json.dumps(pv[k], ensure_ascii=False)[:800])
aj = p["agent_judgment"]
print("== agent_judgment (report.json) keys ==", list(aj.keys()))
for k, v in aj.items():
    if k == "contract_verification":
        continue
    s = json.dumps(v, ensure_ascii=False)
    print(f"  {k}: {s if len(s) < 600 else s[:600]+'...'}")
cv = aj.get("contract_verification")
print("== contract_verification ==")
print(json.dumps(cv, ensure_ascii=False, indent=1)[:9000])
