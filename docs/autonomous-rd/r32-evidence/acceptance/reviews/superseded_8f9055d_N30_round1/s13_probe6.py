import json, sys
SNAP = json.load(open(sys.argv[1], encoding="utf-8"))
SS = SNAP["series_store"]
def ser(mid):
    s = SS[mid]
    return {str(d)[:10]: v for d, v in zip(s["dates"], s["values"]) if v is not None}
FTL, FTU = ser("DFEDTARL"), ser("DFEDTARU")
print("types", type(SS["DFEDTARL"]["dates"][0]).__name__, repr(SS["DFEDTARL"]["dates"][0]))
print([d for d in sorted(FTL) if d >= "2026-09-15"][:4])
print(FTL.get("2026-09-16"), FTL.get("2026-09-17"), FTL.get("2026-09-15"), FTL.get("2026-09-18"))
ks = sorted(FTL)
print("n", len(ks), "last", ks[-3:], [FTL[k] for k in ks[-3:]])
# all change points in 2026
prev = None
for k in ks:
    if k >= "2025-11-01" and prev is not None and FTL[k] != prev[1]:
        print("change", prev[0], "->", k, prev[1], "->", FTL[k])
    prev = (k, FTL[k])
