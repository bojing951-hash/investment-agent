import json, sys
snap = json.load(open(sys.argv[1])); rep = json.load(open(sys.argv[2]))
S = snap["series_store"]
def ser(m): return [(a, b) for a, b in zip(S[m]["dates"], S[m]["values"]) if b is not None]
u = ser("USDJPY"); cur = dict(u)["2026-11-23"]
print("USDJPY n=%d first=%s last=%s cur=%s" % (len(u), u[0][0], u[-1][0], cur))
for y in range(2022, 2027):
    ys = [v for d, v in u if d.startswith(str(y))]
    if ys: print(" year", y, "n=%d min=%.3f max=%.3f last=%.3f" % (len(ys), min(ys), max(ys), ys[-1]))
allv = [v for _, v in u]
print(" full-history percentile of current: <=%.1f%% (n=%d), range %.3f..%.3f" % (sum(1 for v in allv if v <= cur) / len(allv) * 100, len(allv), min(allv), max(allv)))
for m in ("SPX", "VIX", "GOLD_F", "DXY", "BRENT_F", "EURUSD", "NIKKEI225", "BEI_10Y", "TIPS_10Y", "UST_10Y", "JP_POLICY_RATE", "CPI", "EA_HICP_YOY"):
    x = ser(m); print("%-14s n=%d first=%s last=%s" % (m, len(x), x[0][0], x[-1][0]))
# CPI base months present
c = dict(ser("CPI"))
print("CPI 2025 months present:", [k for k in sorted(c) if k.startswith("2025")])
cc = dict(ser("CORE_CPI")); print("CORE_CPI 2025 present:", [k for k in sorted(cc) if k.startswith("2025")])
un = dict(ser("UNEMPLOYMENT")); print("UNEMPLOYMENT 2025 present:", [k for k in sorted(un) if k.startswith("2025")])
ip = dict(ser("INDPRO")); print("INDPRO 2025-08..2026-02:", [(k[:7], ip[k]) for k in sorted(ip) if "2025-08" <= k <= "2026-02-01"])
# shutdown entries in the calendar
cal = json.load(open(sys.argv[3]))
for e in cal["entries"]:
    if "SHUTDOWN" in e["entry_id"]:
        print("CAL", json.dumps(e, ensure_ascii=False)[:700])
# evidence index metrics list
ev = json.load(open(sys.argv[4]))
print("EVID metrics:", sorted(set(r["metric_id"] for r in ev)))
print("EVID sample row:", json.dumps(ev[0], ensure_ascii=False)[:300])
# INDPRO candidate & pool order
for c in rep["research_plan"]["turning_candidates"]["candidates"]:
    print("CAND", c.get("region"), c.get("dimension"), c["metric_id"], c["from_ym"], c["to_ym"], c["value_before"], c["value_after"], c["delta"])
print(json.dumps({k: v for k, v in rep["research_plan"]["turning_candidates"].items() if k != "candidates"}, ensure_ascii=False)[:1500])
