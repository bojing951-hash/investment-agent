import json, sys
snap = json.load(open(sys.argv[1]))
S = snap["series_store"]
def ser(m): return dict((a, b) for a, b in zip(S[m]["dates"], S[m]["values"]) if b is not None)
def v(m, d): return ser(m).get(d)
def yoy(m, ym):
    c = v(m, ym + "-01"); b = v(m, "%04d-%s-01" % (int(ym[:4]) - 1, ym[5:]))
    return None if c is None or b is None else (c / b - 1) * 100
def pct(a, b): return (b / a - 1) * 100
print("CPI yoy chg 2026-07→09 pp: %.4f" % (yoy("CPI", "2026-09") - yoy("CPI", "2026-07")))
print("CORE_CPI yoy chg 07→09 pp: %.4f" % (yoy("CORE_CPI", "2026-09") - yoy("CORE_CPI", "2026-07")))
print("CORE_PCE yoy chg 06→09 pp: %.4f" % (yoy("CORE_PCE", "2026-09") - yoy("CORE_PCE", "2026-06")))
print("INDPRO yoy chg 07→10 pp: %.4f" % (yoy("INDPRO", "2026-10") - yoy("INDPRO", "2026-07")))
print("CPI level chg 07→10 pct: %.4f" % pct(v("CPI", "2026-07-01"), v("CPI", "2026-10-01")))
print("CORE_CPI level chg 07→10 pct: %.4f" % pct(v("CORE_CPI", "2026-07-01"), v("CORE_CPI", "2026-10-01")))
print("CORE_PCE level chg 06→09 pct: %.4f" % pct(v("CORE_PCE", "2026-06-01"), v("CORE_PCE", "2026-09-01")))
print("INDPRO level chg 07→10 pct: %.4f" % pct(v("INDPRO", "2026-07-01"), v("INDPRO", "2026-10-01")))
print("EA HICP yoy 07→09 pp: %.2f ; 07→10 pp: %.2f" % (v("EA_HICP_YOY", "2026-09-01") - v("EA_HICP_YOY", "2026-07-01"), v("EA_HICP_YOY", "2026-10-01") - v("EA_HICP_YOY", "2026-07-01")))
print("EA vs US 2026-09 gap pp: %.4f" % (v("EA_HICP_YOY", "2026-09-01") - yoy("CPI", "2026-09")))
F = {f["fact_id"]: f for f in snap["facts"]}
for k in ("JGB2Y@2026-11-19", "JGB5Y@2026-11-19", "JGB10Y@2026-11-19", "UST_10Y@2026-11-19", "EURUSD@2026-11-23", "USDJPY@2026-11-23"):
    f = F.get(k); print("FACT", k, None if f is None else (f.get("value"), f.get("quality") or f.get("quality_flag"), {a: f[a] for a in f if a not in ("value",)}))
print("UST10Y-JGB10Y spread bp: %.1f" % ((v("UST_10Y", "2026-11-19") - F["JGB10Y@2026-11-19"]["value"]) * 100))
print("JP Oct avg vs target: %.1f bp below" % ((1.25 - v("JP_POLICY_RATE", "2026-10-01")) * 100))
print("USDJPY 10-23→11-23: %+.2f%% (%.3f→%.3f); 08-19→11-23: %+.2f%% (%.3f→%.3f)" % (pct(v("USDJPY", "2026-10-23"), v("USDJPY", "2026-11-23")), v("USDJPY", "2026-10-23"), v("USDJPY", "2026-11-23"), pct(v("USDJPY", "2026-08-19"), v("USDJPY", "2026-11-23")), v("USDJPY", "2026-08-19"), v("USDJPY", "2026-11-23")))
print("EURUSD 08-19→11-23: %+.2f%% (%.5f→%.6f); 10-23→11-23: %+.2f%%" % (pct(v("EURUSD", "2026-08-19"), v("EURUSD", "2026-11-23")), v("EURUSD", "2026-08-19"), v("EURUSD", "2026-11-23"), pct(v("EURUSD", "2026-10-23"), v("EURUSD", "2026-11-23"))))
print("SPX 11-20 close→11-23 intraday: %+.2f%%" % pct(v("SPX", "2026-11-20"), v("SPX", "2026-11-23")))
print("BRENT 08-19→10-30 peak: %+.2f%%; 10-30→11-23: %+.2f%%" % (pct(v("BRENT_F", "2026-08-19"), v("BRENT_F", "2026-10-30")), pct(v("BRENT_F", "2026-10-30"), v("BRENT_F", "2026-11-23"))))
print("BEI 12m window n and first/last:", len([1 for d in ser("BEI_10Y") if "2025-11-20" <= d <= "2026-11-20"]))
print("fact count", len(snap["facts"]), "keys of a fact:", sorted(F["SPX@2026-11-23"].keys()))
