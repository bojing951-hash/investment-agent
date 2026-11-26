import json, sys
snap = sys.argv[1]
n = int(sys.argv[2])
mets = sys.argv[3:]
with open(snap) as f: s = json.load(f)
ss = s["series_store"]
for m in mets:
    if m not in ss:
        print(f"## {m}: NOT IN series_store"); continue
    d = ss[m]["dates"]; v = ss[m]["values"]
    print(f"## {m}: n={len(d)} first={d[0] if d else None} last={d[-1] if d else None} keys={list(ss[m].keys())}")
    # count None / non-finite
    nn = sum(1 for x in v if x is None)
    print(f"   nulls={nn}")
    for i in range(max(0, len(d)-n), len(d)):
        print(f"   {d[i]}  {v[i]!r}")
