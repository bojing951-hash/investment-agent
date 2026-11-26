import json, sys
SNAP = json.load(open(sys.argv[1], encoding="utf-8"))
SS = SNAP["series_store"]
cands = [k for k in SS if any(t in k for t in ("FED", "US_POLICY", "FEDFUNDS", "DFF", "DGS", "US_"))]
print("cands", cands)
for k in cands:
    s = SS[k]
    pts = [(str(d)[:10], v) for d, v in zip(s["dates"], s["values"])]
    tail = [p for p in pts if p[0] >= "2026-08-20" and p[1] is not None]
    print("==", k, "n=", len(pts), "last=", pts[-1], "meta keys=", [m for m in s if m not in ("dates", "values")])
    print("   tail:", tail[:60])
    print("   meta:", {m: s[m] for m in s if m not in ("dates", "values")})
