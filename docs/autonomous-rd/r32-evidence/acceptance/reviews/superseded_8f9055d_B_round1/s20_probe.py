import json, sys
rep = json.load(open(sys.argv[1]))
pv = rep["research_plan"]["point_values"]
print(type(pv), list(pv.keys())[:20] if isinstance(pv, dict) else len(pv))
for k, v in pv.items():
    print("KEY", k, type(v), (list(v.keys())[:20] if isinstance(v, dict) else (v[:3] if isinstance(v, list) else v)))
