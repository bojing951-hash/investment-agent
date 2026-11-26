#!/usr/bin/python3 -I
"""Misc recompute: analog dims/diffs, gate A lists, evidence ref counts, visibility claims, scenario thresholds.
usage: s15b_misc.py <snapshot> <report.json> <agent_judgment.json> <release_calendar.json>"""
import sys
import json
import datetime as dt
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import lib  # seat-owned

snap, rep, aj, cal = (lib.load_json(p) for p in sys.argv[1:5])
st = lib.Store(snap)
N = [0, 0]
MIS = []


def cmp(tag, mine, claim, nd=2):
    N[0] += 1
    if isinstance(mine, (int, float)) and isinstance(claim, (int, float)):
        ok = abs(round(mine, nd) - round(claim, nd)) <= 1e-9
    else:
        ok = mine == claim
    if not ok:
        N[1] += 1
        MIS.append("%s mine=%s claim=%s" % (tag, mine, claim))
    print("   %-58s mine=%-30s claim=%-24s %s" % (tag, mine, claim, "OK" if ok else "<<< MISMATCH"))
    return ok


def info(tag, mine):
    print("   %-58s mine=%s   (info)" % (tag, mine))


def wd(d):
    return dt.date(int(d[:4]), int(d[5:7]), int(d[8:10])).strftime("%a")


def mend(ym):
    y, m = int(ym[:4]), int(ym[5:7])
    nm_y, nm_m = (y, m + 1) if m < 12 else (y + 1, 1)
    return (dt.date(nm_y, nm_m, 1) - dt.timedelta(days=1)).isoformat()


def yoy(mid, ym):
    v = st.at(mid, ym + "-01")
    b = st.at(mid, lib.shift_months(ym + "-01", -12))
    return None if (v is None or b in (None, 0)) else (v / b - 1.0) * 100.0


jud = aj.get("judgment") or aj
print("### ⑪ Gate A vs judgment quality note (report.json gate + snapshot gate_a)")
ga = snap["gate_a"]
cmp("core_missing count", len(ga["core_missing"]), 0, nd=0)
cmp("noncore_missing list (7)", ga["noncore_missing"], ["BUND_10Y", "BUND_2Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"])
cmp("noncore_degraded list (8)", ga["noncore_degraded"], ["CN_SF_FLOW", "ECB_DFR", "ECB_MRO", "JTSJOL", "M2SL", "SPX_EPS", "SPX_PE_TTM", "US_REAL_GDP"])
have = [m for m in ga["noncore_missing"] if st.has(m)]
cmp("missing metrics with stock observations in series_store (5)", have, ["CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"])
for m in have:
    info("%s last obs" % m, st.on_or_before(m, "2026-11-23"))
cmp("JP_POLICY_TARGET in series_store", st.has("JP_POLICY_TARGET"), False)
reg = lib.load_json(sys.argv[5]) if len(sys.argv) > 5 else None
if reg:
    s = json.dumps(reg, ensure_ascii=False)
    cmp("JP_POLICY_TARGET in metric registry", "JP_POLICY_TARGET" in s, False)
cmp("JGB series in series_store", [k for k in snap["series_store"] if "JGB" in k.upper()], [])
jf = [f["fact_id"] for f in snap["facts"] if "JGB" in f["metric_id"].upper()]
cmp("JGB single-point facts", len(jf), 3, nd=0)
info("JGB facts", jf)

print("### evidence_refs counts (judgment)")
l3 = jud["l3"]["contradictions"]
n3 = sum(len(c.get("evidence_refs") or []) for c in l3)
def _sc_refs(sc):
    out = []
    for rv in (sc.get("rows") or {}).values():
        if isinstance(rv, dict):
            out += rv.get("evidence_refs") or []
    return out
n4 = sum(len(_sc_refs(sc)) for sc in jud.get("l4", {}).get("scenarios", []) or [])
n_ch = 0
for ch in jud["l3"].get("mechanism_chains") or []:
    for lk in ch.get("links") or []:
        n_ch += len(lk.get("evidence_refs") or [])
info("contradiction refs / mechanism-chain refs / scenario refs", (n3, n_ch, n4))
cmp("L3 refs incl. mechanism chains (judgment: 41)", n3 + n_ch, 41, nd=0)
cmp("L3 + L4 refs (judgment: 50)", n3 + n_ch + n4, 50, nd=0)
allrefs = []
for c in l3:
    allrefs += c.get("evidence_refs") or []
for ch in jud["l3"].get("mechanism_chains") or []:
    for lk in ch.get("links") or []:
        allrefs += lk.get("evidence_refs") or []
for sc in jud.get("l4", {}).get("scenarios") or []:
    allrefs += _sc_refs(sc)
cmp("distinct refs (20)", len(set(allrefs)), 20, nd=0)
bad = []
for ref in set(allrefs):
    mid, d = ref.split("@")
    if not st.has(mid):
        bad.append((ref, "metric absent"))
        continue
    v = st.at(mid, d)
    if v is None and mid in ("CN_PPI_YOY", "CN_CPI_YOY") and d == "2026-10-31":
        v = st.at(mid, "2026-10-01")  # judgment quality note 4: label = observation month-end, series date = month start
    if v is None:
        bad.append((ref, "no obs on that date"))
cmp("every L3/L4 ref resolves to an observation in series_store (metric@date)", bad, [])
cmp("L3 competing explanations per statement (3/2/3)", [len(c.get("competing_explanations") or []) for c in l3], [3, 2, 3])

print("### ⑧ analog dims / diffs for 2022-06 and 2023-10 (report.json steps[61] S6_analog)")
s6 = None
for s in rep["steps"]:
    if s.get("step") == "S6_analog":
        s6 = s["envelope"]["data"]
top = s6["top"]
info("top list length", len(top))
CLAIM = {1: {"ym": "2022-06", "dist": 0.7918, "pct": 1.37, "shares": {"rates": 51.9, "valuation": 33.6, "inflation": 11.4, "volatility": 3.0},
             "diffs": [("TIPS_10Y_d12m", -1.74, "候选期高于当前"), ("CURVE_2S10S_d12m", 1.43, "当前高于候选期"), ("CURVE_2S10S_level", 1.25, "当前高于候选期"), ("SPX_PE_TTM_level", 1.17, "当前高于候选期")]},
         2: {"ym": "2023-10", "dist": 1.0542, "pct": 30.14, "shares": {"volatility": 60.1, "valuation": 21.2, "rates": 11.0, "inflation": 7.7},
             "diffs": [("SPX_RV21", 1.57, "当前高于候选期"), ("VIX_level", 1.37, "当前高于候选期"), ("SPX_PE_TTM_level", 1.24, "当前高于候选期"), ("CURVE_2S10S_d12m", -1.01, "候选期高于当前")]}}
for i, c in CLAIM.items():
    t = top[i]
    info("top[%d] keys" % i, sorted(t.keys()))
    cmp("top[%d] month" % i, t.get("month") or t.get("anchor_month") or t.get("candidate_month"), c["ym"])
    cmp("top[%d] distance" % i, round(t["distance"], 4), c["dist"], nd=4)
    cmp("top[%d] percentile" % i, round(t["distance_percentile"], 2), c["pct"])
    sh = {k: round(100 * v["contribution_share"], 1) for k, v in t["dims"].items() if v.get("contribution_share")}
    info("top[%d] contribution shares pct" % i, sh)
    for k, v in c["shares"].items():
        cmp("top[%d] share %s" % (i, k), sh.get(k), v, nd=1)
    for k, v in t.items():
        if isinstance(v, (list, dict)) and k not in ("dims", "aftermath", "missing_features") :
            s = json.dumps(v, ensure_ascii=False)
            if any(x in s for x in [dd[0] for dd in c["diffs"]]):
                info("top[%d].%s" % (i, k), s[:1500])
    info("top[%d] missing_features" % i, t.get("missing_features"))

print("### publication-visibility claims (TR1 link 2 / M1 step 2) — rule dates from planner RELEASE_RULES + weekday")
RULE = {"CPI": 13, "CORE_PCE": 30, "EA_HICP_YOY": 16, "JP_CPI_YOY": 20}
for mid, ym, exp_pub, exp_wd in [("CPI", "2026-04", "2026-05-13", None), ("CPI", "2026-05", "2026-06-13", "Sat"), ("CPI", "2026-07", "2026-08-13", None),
                                 ("CPI", "2026-08", "2026-09-13", "Sun"), ("CPI", "2026-09", "2026-10-13", None), ("CORE_PCE", "2026-07", "2026-08-30", "Sun"),
                                 ("EA_HICP_YOY", "2026-04", "2026-05-16", None), ("EA_HICP_YOY", "2026-07", "2026-08-16", None), ("EA_HICP_YOY", "2026-08", "2026-09-16", None),
                                 ("JP_CPI_YOY", "2026-07", "2026-08-20", None)]:
    pub = (lib.ymd(mend(ym)) + dt.timedelta(days=RULE[mid])).isoformat()
    cmp("%s %s rule publication date" % (mid, ym), pub, exp_pub)
    if exp_wd:
        cmp("%s %s rule date weekday" % (mid, ym), wd(pub), exp_wd)
    else:
        info("%s %s rule date weekday" % (mid, ym), wd(pub))


def vis(mid, ym, limit):
    pub = (lib.ymd(mend(ym)) + dt.timedelta(days=RULE[mid])).isoformat()
    return pub <= limit


def latest_visible_yoy(mid, limit):
    ym = limit[:7]
    for _ in range(40):
        if st.at(mid, ym + "-01") is not None and vis(mid, ym, limit):
            return ym, round(yoy(mid, ym), 2) if mid in ("CPI", "CORE_PCE") else round(st.at(mid, ym + "-01"), 2)
        ym = lib.shift_months(ym + "-01", -1)[:7]
    return None


for mid, limit, exp_ym, exp_v in [("CPI", "2026-06-11", "2026-04", 3.78), ("CPI", "2026-09-10", "2026-07", 3.30), ("CPI", "2026-09-16", "2026-08", 3.35), ("CPI", "2026-09-18", "2026-08", 3.35),
                                  ("CORE_PCE", "2026-09-16", "2026-07", 3.00), ("EA_HICP_YOY", "2026-06-11", "2026-04", 3.0), ("EA_HICP_YOY", "2026-09-10", "2026-07", 2.9), ("JP_CPI_YOY", "2026-09-18", "2026-07", 1.97)]:
    r = latest_visible_yoy(mid, limit)
    cmp("%s latest visible obs month before %s" % (mid, limit), r[0] if r else None, exp_ym)
    cmp("%s latest visible value before %s" % (mid, limit), r[1] if r else None, exp_v)
cmp("CPI 2026-09 yoy published after the Sept decisions (2026-10-13 > 2026-09-18)", vis("CPI", "2026-09", "2026-09-18"), False)
cmp("EA HICP 2026-08 not visible at 2026-09-10", vis("EA_HICP_YOY", "2026-08", "2026-09-10"), False)
cmp("EA HICP 2026-08 visible at 2026-09-16", vis("EA_HICP_YOY", "2026-08", "2026-09-16"), True)
cmp("CPI 2026-05 yoy 4.17", round(yoy("CPI", "2026-05"), 2), 4.17)
cmp("CPI 2026-09 yoy 3.72", round(yoy("CPI", "2026-09"), 2), 3.72)
cmp("CPI 2026-10 yoy missing base", yoy("CPI", "2026-10"), None)
cmp("CPI 2026-11 yoy base (2025-11 level) present", st.at("CPI", "2025-11-01") is not None, True)
cmp("CPI 2025-10 level absent", st.at("CPI", "2025-10-01"), None)
cmp("CORE_PCE 2026-05 yoy 3.16", round(yoy("CORE_PCE", "2026-05"), 2), 3.16)
cmp("CORE_PCE 2026-07 yoy 3.00", round(yoy("CORE_PCE", "2026-07"), 2), 3.00)
cmp("CORE_PCE 2026-09 yoy 3.12", round(yoy("CORE_PCE", "2026-09"), 2), 3.12)
cmp("CORE_CPI 2026-02 yoy 2.47", round(yoy("CORE_CPI", "2026-02"), 2), 2.47)
cmp("CORE_CPI 2026-05 yoy 2.82", round(yoy("CORE_CPI", "2026-05"), 2), 2.82)

print("### policy date conventions (TR1 link 2)")
for eff, dec in [("2026-06-17", "2026-06-11"), ("2026-09-16", "2026-09-10")]:
    e = lib.ymd(eff)
    cmp("ECB decision = previous Thursday of %s" % eff, (e - dt.timedelta(days=((e.weekday() - 3) % 7) or 7)).isoformat(), dec)
for eff, dec in [("2026-09-17", "2026-09-16"), ("2025-12-11", "2025-12-10")]:
    cmp("Fed decision = effective minus 1 day of %s" % eff, (lib.ymd(eff) - dt.timedelta(days=1)).isoformat(), dec)
cmp("ECB_DFR 2026-06-17", st.at("ECB_DFR", "2026-06-17"), 2.25)
cmp("ECB_DFR 2026-09-16", st.at("ECB_DFR", "2026-09-16"), 2.5)
_ob = st.on_or_before("ECB_DFR", "2026-06-16")
info("ECB_DFR latest obs on/before 2026-06-16 (change-point series)", _ob)
cmp("ECB_DFR level in force before 2026-06-17", _ob[1] if _ob else None, 2.0)
_ob2 = st.on_or_before("ECB_DFR", "2026-11-23")
cmp("ECB_DFR policy-window net change (2.0 -> 2.5) bp", round((_ob2[1] - 2.0) * 100), 50, nd=0)
_ob3 = st.on_or_before("ECB_MRO", "2026-11-23")
_ob4 = st.on_or_before("ECB_MRO", "2025-11-23")
cmp("ECB_MRO policy-window net change bp", round((_ob3[1] - _ob4[1]) * 100), 50, nd=0)
info("DFF path 2025-12-10/11, 2026-09-16/17", [st.at("DFF", d) for d in ["2025-12-10", "2025-12-11", "2026-09-16", "2026-09-17"]])
info("DFF 2025-11-21..27 (before the 11-28 print)", st.in_range("DFF", "2025-11-17", "2025-11-28"))
cmp("DFF change 2025-12-11 (bp)", round((st.at("DFF", "2025-12-11") - st.at("DFF", "2025-12-10")) * 100), -25, nd=0)
cmp("DFF change 2026-09-17 (bp)", round((st.at("DFF", "2026-09-17") - st.at("DFF", "2026-09-16")) * 100), 25, nd=0)
cmp("DFEDTARU 2025-12-11 ->", st.at("DFEDTARU", "2025-12-11"), 3.75)
cmp("DFEDTARU 2026-09-17 ->", st.at("DFEDTARU", "2026-09-17"), 4.0)
info("DFEDTARU value before 2025-10-30 cut", st.on_or_before("DFEDTARU", "2025-10-29"))
info("DFF value before the 2025-10-30 cut (2025-10-29)", st.on_or_before("DFF", "2025-10-29"))

print("### BOJ calendar entries (frozen calendar)")
ents = cal["entries"]
boj = [e for e in ents if e.get("metric_id") == "JP_POLICY_TARGET"]
cmp("BOJ entries count", len(boj), 2, nd=0)
d = [e for e in boj if e.get("kind") == "policy_decision"][0]
cmp("BOJ decision date", d["decision_date"], "2026-09-18")
cmp("BOJ effective date", d["effective_on"], "2026-09-24")
cmp("BOJ target_value", d["target_value"], 1.25)
m = [e for e in boj if e.get("kind") == "policy_maintenance"][0]
info("BOJ maintenance entry", {k: m.get(k) for k in ("decision_date", "target_value", "first_publish_on_or_after")})
info("calendar has Fed/ECB decision entries", [e["entry_id"] for e in ents if any(x in json.dumps(e, ensure_ascii=False) for x in ["DFEDTARU", "ECB_DFR", "ECB_MRO", "FOMC"])])
cmp("Fed minutes entry published 2026-11-18", [(e.get("release") or e.get("metric_id"), e.get("published_on") or e.get("first_publish_on_or_after")) for e in ents if "MINUTES" in json.dumps(e, ensure_ascii=False).upper() or "纪要" in json.dumps(e, ensure_ascii=False)], [])

print("### misc series facts quoted in TR links / C1")
cmp("BEI_10Y 2026-06-10 = 2.34", st.at("BEI_10Y", "2026-06-10"), 2.34)
cmp("BRENT_F 2026-06 month-end 72.92", round(st.month_last("BRENT_F", "2026-06")[1], 2), 72.92)
cmp("BRENT_F 2026-02 month-end 72.48", round(st.month_last("BRENT_F", "2026-02")[1], 2), 72.48)
hh = [(d[:7], v) for d, v in st.in_range("EA_HICP_YOY", "2025-11-01", "2026-11-23")]
cmp("EA HICP 2026-10 is window max (4.0)", max(hh, key=lambda x: x[1]), ("2026-10", 4.0))
pp = [(d[:7], v) for d, v in st.in_range("CN_PPI_YOY", "2025-11-01", "2026-11-23")]
cmp("CN PPI 2026-10 is window max (5.7)", max(pp, key=lambda x: x[1]), ("2026-10", 5.7))
cmp("CN PPI window min", min(pp, key=lambda x: x[1]), ("2025-11", -2.2))
_cc = st.in_range("CN_CPI_YOY", "2025-10-01", "2026-11-23")
cmp("CN CPI window min (anchor 12m ago 2025-10 = 0.2)", min(_cc, key=lambda t: t[1])[1], 0.2)
cmp("CN CPI window max date/value", max(_cc, key=lambda t: t[1]), ("2026-02-01", 1.3))
cmp("CN CPI 3m-ago anchor (2026-07 = 0.5)", st.at("CN_CPI_YOY", "2026-07-01"), 0.5)
cmp("CN PPI swing pp (window min->max)", round(5.7 - (-2.2), 1), 7.9, nd=1)
sw = {"CN_PPI_YOY": 7.9}
for mid in ["CPI", "CORE_PCE", "CORE_CPI"]:
    vals = [(d[:7], yoy(mid, d[:7])) for d, v in st.series(mid) if "2025-11-01" <= d <= "2026-10-31"]
    vals = [x for x in vals if x[1] is not None]
    sw[mid] = round(max(v for m, v in vals) - min(v for m, v in vals), 2)
for mid in ["EA_HICP_YOY", "JP_CPI_YOY", "CN_CPI_YOY", "JP_CPI_TOKYO_YOY"]:
    vals = [(d[:7], v) for d, v in st.in_range(mid, "2025-11-01", "2026-10-31")]
    sw[mid] = round(max(v for m, v in vals) - min(v for m, v in vals), 2)
info("price-metric swings over the window (pp)", sw)
cmp("largest price swing among listed price metrics is CN_PPI_YOY", max(sw, key=sw.get), "CN_PPI_YOY")
cmp("CPI yoy latest (2026-09) vs year-earlier (2025-09): higher", yoy("CPI", "2026-09") > yoy("CPI", "2025-09"), True)
info("CPI yoy 2025-09 / 2026-09", (round(yoy("CPI", "2025-09"), 4), round(yoy("CPI", "2026-09"), 4)))
info("CORE_PCE yoy 2025-08/09 vs 2026-08/09", [None if yoy("CORE_PCE", ym) is None else round(yoy("CORE_PCE", ym), 4) for ym in ["2025-08", "2025-09", "2026-08", "2026-09"]])
ov = st.series("CN_POLICY_OVERNIGHT")
cmp("CN overnight: first obs", ov[0], ("2026-11-02", 1.25))
cmp("CN overnight: all values 1.25", sorted(set(v for d, v in ov)), [1.25])
cmp("CN overnight: last obs", ov[-1], ("2026-11-23", 1.25))
cmp("CN_OMO_7D window values", sorted(set(v for d, v in st.in_range("CN_OMO_7D", "2025-11-01", "2026-11-23"))), [1.4])
cmp("CN_LPR_1Y window values", sorted(set(v for d, v in st.in_range("CN_LPR_1Y", "2025-11-01", "2026-11-23"))), [3.0])
cmp("CN_NEW_LOANS last obs", st.on_or_before("CN_NEW_LOANS", "2026-11-23")[0][:7], "2026-10")

print("### ⑨ scenario thresholds vs cutoff readings")
cmp("SCN1 trigger: latest CPI yoy (2026-09) >= 3.5 (not yet triggered for 2026-11/12; pending)", round(yoy("CPI", "2026-09"), 2), 3.72)
cmp("SCN1 falsification not met: CPI yoy >= 2.5", yoy("CPI", "2026-09") >= 2.5, True)
cmp("SCN1 falsification not met: CORE_PCE yoy >= 2.8", yoy("CORE_PCE", "2026-09") >= 2.8, True)
cmp("SCN2 falsification not met: BEI_10Y latest >= 1.8", st.on_or_before("BEI_10Y", "2026-11-23"), ("2026-11-20", 2.15))
cmp("SCN2 falsification arithmetic: 2.15 - 1.77 (bp)", round((2.15 - 1.77) * 100), 38, nd=0)
cmp("SCN2 threshold distance: 2.15 - 1.80 (bp)", round((2.15 - 1.80) * 100), 35, nd=0)
cmp("M1 step 4 falsification not met: HY_OAS latest < 4.61", st.on_or_before("HY_OAS", "2026-11-23")[1] < 4.61, True)
for sc in jud["l4"]["scenarios"]:
    cmp("%s deadline" % sc["id"], sc["rows"]["trigger"]["deadline"], "2027-02-28")
    info("%s trigger condition" % sc["id"], sc["rows"]["trigger"]["condition"][:120])

print("### ① cutoff / ⑫ time conversions")
asof = snap["research_as_of"]
cmp("snapshot research_as_of", asof, "2026-11-23T22:53:47+08:00")
cmp("snapshot target_date", snap["target_date"], "20261123")
t = dt.datetime(2026, 11, 23, 22, 53, 47, tzinfo=dt.timezone(dt.timedelta(hours=8)))
for name, off, exp in [("New York (EST, UTC-5)", -5, "09:53"), ("Frankfurt (CET, UTC-1)", 1, "15:53"), ("Tokyo (JST, UTC+9)", 9, "23:53"), ("Shanghai (CST, UTC+8)", 8, "22:53")]:
    cmp("cutoff in %s" % name, (t + dt.timedelta(hours=off) - t.utcoffset()).strftime("%H:%M"), exp)
late = []
for mid in ["UST_10Y", "TIPS_10Y", "BEI_10Y", "SPX", "DAX", "CAC40", "NIKKEI225", "VIX", "HY_OAS", "USDJPY", "USDCNY", "DXY", "GOLD_F", "BRENT_F", "SHCOMP", "DFF", "JP_POLICY_RATE", "CN_PPI_YOY", "CN_CPI_YOY", "CN_PMI_MFG", "ECB_DFR", "CN_LPR_1Y", "CN_POLICY_OVERNIGHT"]:
    if st.last_date(mid) > "2026-11-23":
        late.append((mid, st.last_date(mid)))
cmp("no cited daily series has observations after the cutoff date", late, [])
maxd = max(st.last_date(m) for m in snap["series_store"])
cmp("latest observation date anywhere in series_store <= cutoff", maxd <= "2026-11-23", True)
info("latest observation date anywhere", maxd)
info("weekday 2026-11-23", wd("2026-11-23"))
print("=" * 100)
print("POINTS=%d MISMATCHES=%d" % (N[0], N[1]))
for m in MIS:
    print("MISMATCH:", m)
