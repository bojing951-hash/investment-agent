import json, sys
rep = json.load(open(sys.argv[1])); snap = json.load(open(sys.argv[2]))
cv = rep["agent_judgment"]["contract_verification"]
for v in cv["verdicts"]:
    print("VERDICT", v.get("status"), "|", v.get("metric"), "|", v.get("value"), "|", (v.get("note") or "")[:160])
print("STATS", cv.get("stats"))
for k in cv:
    if k not in ("verdicts", "stats"):
        print("KEY", k, json.dumps(cv[k], ensure_ascii=False)[:500])
S = snap["series_store"]
d = S["BRENT_F"]["dates"]; vv = S["BRENT_F"]["values"]
for a, b in vv_ if False else []: pass
print("BRENT 2026-10-15..2026-11-23:")
print("; ".join("%s=%.2f" % (x, y) for x, y in zip(d, vv) if "2026-10-15" <= x <= "2026-11-23" and y is not None))
print("BRENT 2026-08-10..2026-08-31:")
print("; ".join("%s=%.2f" % (x, y) for x, y in zip(d, vv) if "2026-08-10" <= x <= "2026-08-31" and y is not None))
win = [(x, y) for x, y in zip(d, vv) if "2026-08-19" <= x <= "2026-11-23" and y is not None]
below = [x for x, y in win if y < 91.62]
print("first below 91.62:", below[:3], "count below:", len(below), "of", len(win))
print("days >= 91.62 in window:", sum(1 for x, y in win if y >= 91.62))
# oil on publication dates
for dt in ("2026-09-11", "2026-10-15", "2026-11-13", "2026-11-16", "2026-08-13", "2026-08-16"):
    i = d.index(dt) if dt in d else None
    print("BRENT on", dt, vv[i] if i is not None else None)
