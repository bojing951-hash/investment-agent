#!/usr/bin/python3 -I
"""② Point-anchor cell recompute (independent of the engine planner).
usage: s10_cells.py <snapshot> <calendar> <judgment.json> <report.json>
Visibility = frozen calendar entries first, else month-end+N-day rule (N taken from a
static table typed by the seat from the publication cadence the claims rest on)."""
import sys
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import lib  # seat-owned

snap, cal, jud, rep = (lib.load_json(p) for p in sys.argv[1:5])
st = lib.Store(snap)
cutoff = snap["target_date"]
asof = snap["research_as_of"]
print("research_as_of=%s target_date=%s" % (asof, cutoff))

RULE_DAYS = {  # month-end + N days (negative = before month end)
    "CPI": 13, "CORE_CPI": 13, "CORE_PCE": 30, "INDPRO": 15, "UNEMPLOYMENT": 5,
    "CN_PMI_MFG": -1, "CN_CPI_YOY": 9, "CN_PPI_YOY": 9, "EA_HICP_YOY": 16,
    "EA_REAL_GDP_YOY": 35, "JP_REAL_GDP_YOY": 45, "JP_CPI_YOY": 20, "JP_CPI_TOKYO_YOY": -1,
    "JP_POLICY_RATE": 5,
}
QUARTERLY = {"US_REAL_GDP", "EA_REAL_GDP_YOY", "JP_REAL_GDP_YOY"}
entries = cal["entries"]


def month_end(d):
    nxt = lib.shift_months(d[:7] + "-01", 1)
    return lib.shift_months(nxt, 0)[:-3] + "01"


def rule_pub(mid, obs):
    if mid == "US_REAL_GDP":
        return lib.shift_months(lib.shift_months(obs, 3)[:-2] + "01", 0)  # placeholder, replaced below
    n = RULE_DAYS[mid]
    first_next = lib.shift_months(obs[:7] + "-01", 1)
    # month end of obs month = first_next - 1 day
    import datetime as dtm
    me = (dtm.date(int(first_next[:4]), int(first_next[5:7]), int(first_next[8:10])) - dtm.timedelta(days=1))
    return (me + dtm.timedelta(days=n)).isoformat()


def qe_pub(obs, n):
    import datetime as dtm, calendar as _cal
    m = int(obs[5:7]); qe_m = 3 * ((m - 1) // 3) + 3
    qe = dtm.date(int(obs[:4]), qe_m, _cal.monthrange(int(obs[:4]), qe_m)[1])
    return (qe + dtm.timedelta(days=n)).isoformat()


def gdp_pub(obs):
    # quarter-end + 29 days (US BEA advance) -- the rule the engine states (2026Q3 = 2026-10-29)
    import datetime as dtm
    m = int(obs[5:7])
    qe_m = 3 * ((m - 1) // 3) + 3          # last month of the quarter holding obs month
    qe = dtm.date(int(obs[:4]), qe_m, 1) + dtm.timedelta(days=-1)  # first day of qe_m minus 1 = last day of prior month; fix below
    qe = dtm.date(int(obs[:4]), qe_m, 1)
    import calendar as _cal
    qe = dtm.date(int(obs[:4]), qe_m, _cal.monthrange(int(obs[:4]), qe_m)[1])  # quarter-end day
    return (qe + dtm.timedelta(days=29)).isoformat()


def calendar_pub(mid, obs):
    best = None
    for e in entries:
        ids = e.get("metric_ids") or [e.get("metric_id")]
        if mid in ids and e["obs_from"] <= obs <= e["obs_to"]:
            if best is None or e["obs_from"] > best["obs_from"]:
                best = e
    if best is None:
        return None, None
    return best["first_publish_on_or_after"], best.get("entry_id")


def pub_date(mid, obs):
    cp, eid = calendar_pub(mid, obs)
    if cp is not None:
        return cp, "cal:" + eid
    if mid in QUARTERLY:
        if mid == "US_REAL_GDP":
            return gdp_pub(obs), "rule:QE+29"
        return qe_pub(obs, RULE_DAYS[mid]), "rule:QE+%d" % RULE_DAYS[mid]
    if mid in RULE_DAYS:
        return rule_pub(mid, obs), "rule:ME+%d" % RULE_DAYS[mid]
    return None, "daily/none"


ANCHORS = [("12个月前", "2025-11-23"), ("3个月前", "2026-08-23"), ("最新一期", "2026-11-23")]
METRICS = rep["research_plan"]["metrics"]

# judgment anchor echo
echo = {}
for reg in jud["reader_map"]["regions"]:
    for a in reg["anchor_echo"]:
        echo[(a["metric_id"], a["anchor"])] = a

cells = {(c["metric_id"]): c for c in rep["research_plan"]["point_values"]["cells"]}
n_pts = 0
n_mis = 0
rows = []


def cmp(tag, mine, theirs, nd=4, tol=0.0):
    global n_pts, n_mis
    n_pts += 1
    if theirs is None and mine is None:
        ok = True
    elif mine is None or theirs is None:
        ok = False
    elif isinstance(mine, (int, float)) and isinstance(theirs, (int, float)):
        ok = abs(round(mine, nd) - round(theirs, nd)) <= tol
    else:
        ok = (mine == theirs)
    if not ok:
        n_mis += 1
    print("   %-34s mine=%-28s claim=%-28s %s" % (tag, mine, theirs, "OK" if ok else "<<< MISMATCH"))
    return ok


for mid in METRICS:
    print("=" * 110)
    c = cells.get(mid, {})
    for an, ad in ANCHORS:
        eng = c.get("anchors", {}).get(an, {})
        if mid in QUARTERLY or mid in RULE_DAYS:
            s = st.series(mid)
            pick = None
            for d, v in s:
                if d > ad:
                    break
                p, basis = pub_date(mid, d)
                if p is not None and p <= ad:
                    pick = (d, v, p, basis)
            if pick is None:
                print("[%s/%s] no published observation on/before anchor; engine status=%s" % (mid, an, eng.get("status")))
                n_pts += 1
                if eng.get("status", "").startswith("no_published"):
                    print("   -> consistent (both absent)")
                else:
                    n_mis += 1
                    print("   -> MISMATCH: engine says %s" % json.dumps(eng, ensure_ascii=False)[:200] if False else "   -> MISMATCH: engine status ok")
                continue
            d, v, p, basis = pick
            print("[%s/%s] anchor %s -> obs %s val %s pub %s (%s)" % (mid, an, ad, d, v, p, basis))
            cmp("  obs_date", d, eng.get("observation_date"))
            cmp("  value", v, eng.get("value"), nd=4)
            cmp("  pub_date", p, eng.get("publication_date"))
            e = echo.get((mid, an))
            if e is not None:
                cmp("  echo.value", v, e["value"], nd=4)
                cmp("  echo.obs_month", d[:7], e.get("observation_month"))
            else:
                print("   (no anchor_echo row in judgment for %s/%s)" % (mid, an))
            if mid in QUARTERLY or mid in ("CPI", "CORE_CPI", "CORE_PCE", "INDPRO"):
                # yoy from level
                base = st.at(mid, lib.shift_months(d, -12))
                if mid == "US_REAL_GDP":
                    y = lib.pct_change(base, v) if base is not None else None
                    cmp("  yoy_pct(derived)", None if y is None else round(y, 2), eng.get("derived_yoy_pct"), nd=2, tol=0.005)
                elif mid in ("EA_REAL_GDP_YOY", "JP_REAL_GDP_YOY"):
                    pass
                else:
                    y = lib.pct_change(base, v) if base is not None else None
                    cmp("  yoy_pct(derived)", None if y is None else round(y, 2), eng.get("derived_yoy_pct"), nd=2, tol=0.005)
                    cmp("  yoy_status", "ok" if y is not None else "no_base", "ok" if eng.get("derived_yoy_pct") is not None else "no_base")
        else:
            # daily / policy series: latest obs <= anchor
            pick = st.on_or_before(mid, ad)
            eng_status = eng.get("status")
            print("[%s/%s] anchor %s -> latest obs on/before: %s ; engine: obs=%s val=%s status=%s" % (
                mid, an, ad, pick, eng.get("observation_date"), eng.get("value"), eng_status))
            if eng_status and eng_status.startswith("no_published"):
                n_pts += 1
                if pick is None:
                    print("   -> consistent (series has no obs on/before anchor)")
                else:
                    n_mis += 1
                    print("   -> CHECK: series has obs %s but engine says none published" % (pick,))
                continue
            if pick is None:
                n_pts += 1
                n_mis += 1
                print("   -> MISMATCH: series has no obs but engine ok")
                continue
            # publication for daily series = obs date (DFF +1)
            pub = pick[0] if mid != "DFF" else lib.shift_months(pick[0], 0)
            import datetime as dtm
            if mid == "DFF":
                pub = (dtm.date(*map(int, pick[0].split("-"))) + dtm.timedelta(days=1)).isoformat()
            if pub <= ad:
                cmp("  obs_date", pick[0], eng.get("observation_date"))
                cmp("  value", pick[1], eng.get("value"), nd=4)
                e = echo.get((mid, an))
                if e is not None:
                    cmp("  echo.value", pick[1], e["value"], nd=4)
                    cmp("  echo.obs_month", pick[0][:7], e.get("observation_month"))
                else:
                    print("   (no anchor_echo row in judgment for %s/%s)" % (mid, an))
            else:
                prev = None
                for d, v in st.series(mid):
                    if d < pick[0]:
                        prev = (d, v)
                print("   latest obs not yet published at anchor (pub %s > anchor %s); engine obs=%s val=%s" % (
                    pub, ad, eng.get("observation_date"), eng.get("value")))
                n_pts += 1
                if eng.get("observation_date") == (prev[0] if prev else None):
                    print("   -> OK (engine used previous published obs %s)" % (prev,))
                else:
                    n_mis += 1
                    print("   -> MISMATCH")

print("=" * 110)
print("POINTS=%d MISMATCHES=%d" % (n_pts, n_mis))
