#!/usr/bin/python3 -I
# -*- coding: utf-8 -*-
"""Independent second-path check (Audit-R32 / N30 / Round-1 seat).

Deliberately shares NO code with s05_recompute.py: a fresh dict of {date: value}
built straight from the frozen snapshot, recomputing the headline numbers of the
judgment. Read-only on all inputs; output only under the seat directory.

usage: /usr/bin/python3 -I s06_independent_check.py <snapshot.json> <report.json> <agent_judgment.json> <out.json>
"""
import datetime as dt
import json
import sys

snap = json.load(open(sys.argv[1], encoding="utf-8"))
rep = json.load(open(sys.argv[2], encoding="utf-8"))
aj = json.load(open(sys.argv[3], encoding="utf-8"))
out = sys.argv[4]


def series(mid):
    s = snap["series_store"][mid]
    return {str(d)[:10]: v for d, v in zip(s["dates"], s["values"]) if v is not None}


def ym(mid, key):
    return series(mid).get(key + "-01")


def pc(a, b):
    return round((b / a - 1.0) * 100.0, 2)


def dd(a, b):
    f = dt.date.fromisoformat
    return (f(b) - f(a)).days


rows = []


def chk(name, expect, got, tol=0.0051):
    ok = (expect == got) if not isinstance(expect, (int, float)) or isinstance(expect, bool) else (abs(float(expect) - float(got)) <= tol)
    rows.append({"item": name, "judgment": expect, "independent": got, "ok": bool(ok)})


# --- inflation readings quoted in the judgment (l3 C1 / M1 link 0 / regions / turnings)
for mid, key, val in [("EA_HICP_YOY", "2026-10", 4.0), ("EA_HICP_YOY", "2026-04", 3.0), ("EA_HICP_YOY", "2025-10", 2.1),
                      ("EA_HICP_YOY", "2026-05", 3.2), ("EA_HICP_YOY", "2026-06", 2.8), ("EA_HICP_YOY", "2026-07", 2.9),
                      ("EA_HICP_YOY", "2026-08", 3.2), ("EA_HICP_YOY", "2026-09", 3.8), ("EA_HICP_YOY", "2026-02", 1.9),
                      ("EA_HICP_YOY", "2026-01", 1.7),
                      ("JP_CPI_YOY", "2026-10", 2.44), ("JP_CPI_YOY", "2026-04", 1.38), ("JP_CPI_YOY", "2025-10", 2.99),
                      ("JP_CPI_YOY", "2026-05", 1.53), ("JP_CPI_YOY", "2026-06", 1.67), ("JP_CPI_YOY", "2026-07", 1.97),
                      ("JP_CPI_YOY", "2026-08", 1.98), ("JP_CPI_YOY", "2026-09", 2.16), ("JP_CPI_YOY", "2026-02", 1.27),
                      ("JP_CPI_YOY", "2025-11", 2.9), ("JP_CPI_YOY", "2025-09", 2.91), ("JP_CPI_YOY", "2025-01", 4.03),
                      ("JP_CPI_TOKYO_YOY", "2026-10", 2.73), ("JP_CPI_TOKYO_YOY", "2026-09", 2.69), ("JP_CPI_TOKYO_YOY", "2026-08", 1.9),
                      ("JP_CPI_TOKYO_YOY", "2026-06", 1.6), ("JP_CPI_TOKYO_YOY", "2026-04", 1.42)]:
    chk("%s@%s" % (mid, key), val, ym(mid, key))

# --- derived inflation statements
chk("EA gap latest 4.0-2.44", 1.56, round(ym("EA_HICP_YOY", "2026-10") - ym("JP_CPI_YOY", "2026-10"), 2))
chk("EA yoy change 4.0-2.1", 1.9, round(ym("EA_HICP_YOY", "2026-10") - ym("EA_HICP_YOY", "2025-10"), 2))
chk("JP yoy change 2.44-2.99", -0.55, round(ym("JP_CPI_YOY", "2026-10") - ym("JP_CPI_YOY", "2025-10"), 2))
chk("EA from 2026-06", 1.2, round(ym("EA_HICP_YOY", "2026-10") - ym("EA_HICP_YOY", "2026-06"), 2))
chk("JP from 2026-06", 0.77, round(ym("JP_CPI_YOY", "2026-10") - ym("JP_CPI_YOY", "2026-06"), 2))
chk("EA from 2026-05", 0.8, round(ym("EA_HICP_YOY", "2026-10") - ym("EA_HICP_YOY", "2026-05"), 2))
chk("JP from 2026-05", 0.91, round(ym("JP_CPI_YOY", "2026-10") - ym("JP_CPI_YOY", "2026-05"), 2))
gaps = [round(ym("EA_HICP_YOY", "2026-%02d" % m) - ym("JP_CPI_YOY", "2026-%02d" % m), 2) for m in range(5, 11)]
chk("EA-JP monthly gap range 0.93-1.67", [0.93, 1.67], [min(gaps), max(gaps)])
chk("2026-09 gap national/tokyo vs EA", [-1.64, -1.11], [round(ym("JP_CPI_YOY", "2026-09") - 3.8, 2), round(ym("JP_CPI_TOKYO_YOY", "2026-09") - 3.8, 2)])
ea12 = [ym("EA_HICP_YOY", "2025-%02d" % m) for m in (11, 12)] + [ym("EA_HICP_YOY", "2026-%02d" % m) for m in range(1, 11)]
ym12 = ["2025-11", "2025-12"] + ["2026-%02d" % m for m in range(1, 11)]
chk("EA latest is 12-month max", True, ea12[-1] == max(ea12))
chk("EA 12-month min at 2026-01 = 1.7", ["2026-01", 1.7], [ym12[ea12.index(min(ea12))], min(ea12)])
jp12 = [ym("JP_CPI_YOY", "2025-%02d" % m) for m in (11, 12)] + [ym("JP_CPI_YOY", "2026-%02d" % m) for m in range(1, 11)]
chk("JP 12-month min at 2026-02 = 1.27", ["2026-02", 1.27], [ym12[jp12.index(min(jp12))], min(jp12)])

# --- policy
ecb = series("ECB_MRO")
chg = sorted(ecb)
chk("ECB_MRO last obs", "2026-09-16", chg[-1])
chk("ECB_MRO value at last obs", 2.65, ecb[chg[-1]])
dfr = series("ECB_DFR")
chk("ECB_DFR value at last obs", 2.5, dfr[sorted(dfr)[-1]])
chk("ECB_MRO 2025-06-11=2.15", 2.15, ecb.get("2025-06-11"))
chk("ECB_DFR 2025-06-11=2.0", 2.0, dfr.get("2025-06-11"))
chk("ECB_MRO 2026-06-17=2.4", 2.4, ecb.get("2026-06-17"))
chk("ECB_DFR 2026-06-17=2.25", 2.25, dfr.get("2026-06-17"))
chk("ECB last obs -> cutoff days", 68, dd("2026-09-16", "2026-11-23"))
chk("ECB hold 2025-06-11 -> 2026-06-17 days", 371, dd("2025-06-11", "2026-06-17"))
chk("ECB two changes apart days", 91, dd("2026-06-17", "2026-09-16"))
chk("ECB eff 09-16 -> BOJ eff 09-24 days", 8, dd("2026-09-16", "2026-09-24"))
chk("BOJ decision 09-18 -> cutoff-less: 10-30 -> cutoff days", 24, dd("2026-10-30", "2026-11-23"))
jpr = {k: ym("JP_POLICY_RATE", k) for k in ["2025-11", "2025-12"] + ["2026-%02d" % m for m in range(1, 11)]}
chk("JP_POLICY_RATE monthly path", [0.478, 0.557, 0.728, 0.728, 0.728, 0.727, 0.727, 0.841, 0.978, 0.977, 1.043, 1.227], [jpr[k] for k in sorted(jpr)])
chk("JP 6m anchor-to-anchor bp", 50, round((jpr["2026-10"] - jpr["2026-04"]) * 100, 1))
chk("JP four in-window steps sum bp", 50, round(((jpr["2026-06"] - jpr["2026-05"]) + (jpr["2026-07"] - jpr["2026-06"]) + (jpr["2026-09"] - jpr["2026-08"]) + (jpr["2026-10"] - jpr["2026-09"])) * 100, 0))
chk("JP 12m 0.478 -> 1.227 bp", 75, round((jpr["2026-10"] - jpr["2025-11"]) * 100, 0))
chk("level gap MRO 2.65 - 1.25", 1.4, round(2.65 - 1.25, 2))
chk("level gap DFR 2.5 - 1.25", 1.25, round(2.5 - 1.25, 2))

# --- market month windows (same-day close 10-23 -> 11-20) and cutoff-day intraday
# the judgment states VIX percentages with ONE decimal (+84.5%, -24.7%) -> tolerance 0.051 for those two
for mid, a, b, e, tol in [("SPX", "2026-10-23", "2026-11-20", -9.36, 0.006), ("NIKKEI225", "2026-10-23", "2026-11-20", -9.98, 0.006), ("DAX", "2026-10-23", "2026-11-20", -1.50, 0.006),
                          ("CAC40", "2026-10-23", "2026-11-20", 1.86, 0.006), ("VIX", "2026-10-23", "2026-11-20", 84.5, 0.051), ("EURUSD", "2026-10-23", "2026-11-20", -2.24, 0.006),
                          ("USDJPY", "2026-10-23", "2026-11-20", 2.05, 0.006), ("DXY", "2026-10-23", "2026-11-20", 1.96, 0.006), ("SPX", "2026-10-23", "2026-11-23", -5.51, 0.006),
                          ("DAX", "2026-10-23", "2026-11-23", 0.11, 0.006), ("VIX", "2026-10-23", "2026-11-23", 38.87, 0.006), ("EURUSD", "2026-10-23", "2026-11-23", -2.51, 0.006),
                          ("USDJPY", "2026-10-23", "2026-11-23", 1.82, 0.006), ("DXY", "2026-10-23", "2026-11-23", 2.23, 0.006)]:
    s = series(mid)
    chk("%s %s->%s pct" % (mid, a, b), e, pc(s[a], s[b]), tol)
v = series("VIX")
# raw VIX values are float32-like (19.450001 ...): the judgment prints two decimals
chk("VIX 10-23 / 11-13 / 11-20 / 11-23 levels (2 decimals)", [19.45, 19.30, 35.89, 27.01], [round(v["2026-10-23"], 2), round(v["2026-11-13"], 2), round(v["2026-11-20"], 2), round(v["2026-11-23"], 2)])
chk("VIX 11-23 vs 11-20 pct (one decimal in the judgment)", -24.7, round(pc(v["2026-11-20"], v["2026-11-23"]), 1))
for d_, e in [("2026-11-16", 18.70), ("2026-11-20", 26.20)]:
    prev = max(x for x in v if x < d_)
    chk("VIX daily pct %s (prev %s)" % (d_, prev), e, pc(v[prev], v[d_]))
for mid, e in [("SPX", -8.61), ("NIKKEI225", -7.70), ("DAX", -7.28), ("CAC40", -5.27)]:
    s = series(mid)
    chk("%s 11-13->11-20 pct" % mid, e, pc(s["2026-11-13"], s["2026-11-20"]))
chk("VIX 11-04->11-05 pct", 69.66, pc(v["2026-11-04"], v["2026-11-05"]))
chk("VIX 11-11 vs 11-05 pct", -37.93, pc(v["2026-11-05"], v["2026-11-11"]))
sp = series("SPX")
nk = series("NIKKEI225")
chk("SPX 11-05 daily pct", -4.36, pc(sp[max(x for x in sp if x < "2026-11-05")], sp["2026-11-05"]))
chk("NIKKEI225 11-06 daily pct", -5.96, pc(nk["2026-11-05"], nk["2026-11-06"]))
chk("VIX jump start -> 10-30 days", 14, dd("2026-10-30", "2026-11-13"))
chk("VIX jump start -> ECB 09-16 days", 58, dd("2026-09-16", "2026-11-13"))
chk("VIX jump end -> 10-30 days", 21, dd("2026-10-30", "2026-11-20"))
chk("VIX jump end -> ECB 09-16 days", 65, dd("2026-09-16", "2026-11-20"))
eu, uj = series("EURUSD"), series("USDJPY")
x1 = eu["2026-10-23"] * uj["2026-10-23"]
x2 = eu["2026-11-20"] * uj["2026-11-20"]
x3 = eu["2026-11-23"] * uj["2026-11-23"]
chk("EURJPY synth 10-23 / 11-20 / 11-23", [175.61, 175.19, 174.32], [round(x1, 2), round(x2, 2), round(x3, 2)], 0.006)
chk("EURJPY synth pct 11-20 vs 10-23", -0.24, pc(x1, x2))
chk("EURJPY synth pct 11-23 vs 10-23", -0.73, pc(x1, x3))
u = series("UST_10Y")
chk("UST_10Y last obs / value", ["2026-11-19", 5.04], [max(u), u[max(u)]])
n, r, b = series("UST_10Y"), series("TIPS_10Y"), series("BEI_10Y")
dn = round((n["2026-11-19"] - n["2026-10-20"]) * 100)
dr = round((r["2026-11-19"] - r["2026-10-20"]) * 100)
db = round((b["2026-11-19"] - b["2026-10-20"]) * 100)
chk("US 10Y trio monthly window bp (nominal/real/bei)", [-8.0, 11.0, -19.0], [dn, dr, db])
ff_l, ff_u = series("DFEDTARL"), series("DFEDTARU")
chk("Fed funds target band at cutoff", [3.75, 4.0], [ff_l["2026-11-23"], ff_u["2026-11-23"]])
fc = sorted(d for d in ff_u if d > "2026-09-01" and ff_u[d] != ff_u[sorted(x for x in ff_u if x < d)[-1]])
chk("Fed last change date in series", ["2026-09-17"], fc[-1:])

# --- scenario arithmetic vs cutoff readings
chk("S1 premise levels compatible with cutoff readings: EA>=3.5, JP>=2.0, gap>=1.5", [True, True, True], [ym("EA_HICP_YOY", "2026-10") >= 3.5, ym("JP_CPI_YOY", "2026-10") >= 2.0, round(ym("EA_HICP_YOY", "2026-10") - ym("JP_CPI_YOY", "2026-10"), 2) >= 1.5])
chk("S1 trigger threshold EA>=4.0 equals the latest reading (not yet met/failed before 2026-11 reading)", 4.0, ym("EA_HICP_YOY", "2026-10"))
chk("S2 falsification side (two months >=3.5) not yet met: latest EA 4.0 >= 3.5", True, ym("EA_HICP_YOY", "2026-10") >= 3.5)
import datetime as _dt
_e = _dt.date


def pub(month_end_offset_day, y, m):
    # engine rule: month end + offset days
    nm = _e(y + (m == 12), (m % 12) + 1, 1)
    return str(nm - _dt.timedelta(days=1) + _dt.timedelta(days=month_end_offset_day))


chk("publication of 2026-11 / 2026-12 obs by engine rule (EA +16d, JP +20d) all before deadline 2027-02-15",
    [True, True, True, True],
    [pub(16, 2026, 11) < "2027-02-15", pub(20, 2026, 11) < "2027-02-15", pub(16, 2026, 12) < "2027-02-15", pub(20, 2026, 12) < "2027-02-15"])
chk("those publication dates", ["2026-12-16", "2026-12-20", "2027-01-16", "2027-01-20"], [pub(16, 2026, 11), pub(20, 2026, 11), pub(16, 2026, 12), pub(20, 2026, 12)])
chk("EA 2026-04 reading publication by rule (+16d) = 2026-05-16", "2026-05-16", pub(16, 2026, 4))
chk("JP 2026-04 reading publication by rule (+20d) = 2026-05-20", "2026-05-20", pub(20, 2026, 4))

# --- analog face quoted in history note
an = [x for x in rep["steps"] if x.get("step") == "S6_analog"][0]["envelope"]["data"]
chk("analog scanned / valid", [1871, 74], [an["candidates"]["scanned"], an["candidates"]["valid"]])
chk("analog TOP1 month / distance", ["2025-03", 0.727], [an["top"][0]["candidate_month"], round(an["top"][0]["distance"], 3)], 0.0006)

# --- contract verification face
cv = (rep.get("agent_judgment") or {}).get("contract_verification") or {}
vs = cv.get("verdicts") or []
from collections import Counter
cnt = Counter(x.get("status") for x in vs)
if vs:
    chk("contract token verdicts: 5 tokens, VERIFIED 4 / STALE 1", [5, {"VERIFIED": 4, "STALE": 1}], [len(vs), dict(cnt)])
    st = [x for x in vs if x.get("status") == "STALE"]
    chk("the single STALE token is ECB_DFR 2.5% and value==expected", [1, "ECB_DFR", "2.5%", True],
        [len(st), st[0].get("metric"), st[0].get("token"), st[0].get("value") == st[0].get("expected")] if st else [0, None, None, False])
    chk("STALE token expected value == last ECB_DFR observation", 2.5, dfr[sorted(dfr)[-1]] if st and st[0].get("expected") is not None else None)
    chk("contract six_checks count / all VERIFIED", [16, 16], [len(cv.get("six_checks") or []), len([x for x in (cv.get("six_checks") or []) if x.get("status") == "VERIFIED"])])
else:
    rows.append({"item": "contract verdicts (not found in report.agent_judgment)", "judgment": None, "independent": list(cv.keys())[:8], "ok": False})

n_ok = sum(1 for x in rows if x["ok"])
json.dump({"n": len(rows), "ok": n_ok, "mismatch": len(rows) - n_ok, "rows": rows}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print({"n": len(rows), "ok": n_ok, "mismatch": len(rows) - n_ok})
for x in rows:
    if not x["ok"]:
        print("MISMATCH", json.dumps(x, ensure_ascii=False))
