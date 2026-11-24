import json, sys
snap = sys.argv[1]
cal = sys.argv[2]
reg = sys.argv[3]
rep = sys.argv[4]
with open(snap) as f: s = json.load(f)
print("== snapshot top keys ==")
for k, v in s.items():
    t = type(v).__name__
    if isinstance(v, (dict, list)):
        print(f"  {k}: {t} len={len(v)}")
    else:
        print(f"  {k}: {t} = {v!r}")
print("research_as_of:", s.get("research_as_of"))
print("target_date:", s.get("target_date"))
ss = s.get("series_store")
print("series_store type:", type(ss).__name__, "n=", len(ss))
k0 = list(ss.keys())[:3]
for k in k0:
    print("  key sample:", k, "->", type(ss[k]).__name__, (list(ss[k].keys()) if isinstance(ss[k], dict) else None))
ga = s.get("gate_a")
print("== gate_a keys ==")
if isinstance(ga, dict):
    for k, v in ga.items():
        if isinstance(v, (dict, list)):
            print(f"  {k}: {type(v).__name__} len={len(v)}")
        else:
            print(f"  {k}: {v!r}")
with open(cal) as f: c = json.load(f)
print("== calendar top keys ==")
for k, v in c.items():
    if isinstance(v, (dict, list)):
        print(f"  {k}: {type(v).__name__} len={len(v)}")
    else:
        print(f"  {k}: {v!r}")
with open(reg) as f: r = json.load(f)
print("== registry top keys ==")
for k, v in r.items():
    if isinstance(v, (dict, list)):
        print(f"  {k}: {type(v).__name__} len={len(v)}")
    else:
        print(f"  {k}: {v!r}")
with open(rep) as f: p = json.load(f)
print("== report.json top keys ==")
for k, v in p.items():
    if isinstance(v, (dict, list)):
        print(f"  {k}: {type(v).__name__} len={len(v)}")
    else:
        print(f"  {k}: {v!r}" if len(str(v)) < 300 else f"  {k}: {str(v)[:300]}...")
