import json, sys
rep = sys.argv[1]
with open(rep) as f: p = json.load(f)
r = p["run"]
print("== run ==")
for k, v in r.items():
    s = json.dumps(v, ensure_ascii=False)
    print(f"  {k}: {s if len(s) < 1500 else s[:1500] + '...'}")
rp = p["research_plan"]
print("== research_plan keys ==")
for k, v in rp.items():
    s = json.dumps(v, ensure_ascii=False)
    print(f"--- {k} ({type(v).__name__}, {len(s)} chars)")
    if k not in ("map_question",):
        print(s if len(s) < 6000 else s[:6000] + "...")
