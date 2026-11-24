import json, sys
J = json.load(open(sys.argv[1], encoding="utf-8"))
l3 = J["l3"]
print("=== LKS[0] text ===")
print(l3["mechanism_chains"][0]["links"][0]["text"])
def leaves(o, p, out):
    if isinstance(o, dict):
        for k, v in o.items(): leaves(v, p + [k], out)
    elif isinstance(o, list):
        for i, v in enumerate(o): leaves(v, p + [i], out)
    else:
        out.append((p, o))
LV = []; leaves(J, [], LV)
for d in ("2026-09-16", "2026-09-17", "2026-05-16", "2026-05-23", "2026-08-30"):
    print("=== leaves containing", d, "===")
    for p, v in LV:
        if isinstance(v, str) and d in v:
            i = v.find(d)
            print(p, "::", v[max(0, i - 110): i + 130].replace("\n", " "))
