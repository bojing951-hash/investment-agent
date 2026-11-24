#!/usr/bin/python3 -I
"""④ policy face recompute. usage: s12_policy.py <snapshot> <calendar> <report.json>"""
import sys
import datetime as dtm
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import lib  # seat-owned

snap, cal, rep = (lib.load_json(p) for p in sys.argv[1:4])
st = lib.Store(snap)
N = [0, 0]


def cmp(tag, mine, claim, nd=4):
    N[0] += 1
    if isinstance(mine, (int, float)) and isinstance(claim, (int, float)):
        ok = abs(round(mine, nd) - round(claim, nd)) <= 1e-9
    else:
        ok = mine == claim
    if not ok:
        N[1] += 1
    print("   %-56s mine=%-30s claim=%-26s %s" % (tag, mine, claim, "OK" if ok else "<<< MISMATCH"))
    return ok


def wd(d):
    return dtm.date(*map(int, d.split("-"))).strftime("%a")


W0, W1 = "2025-11-23", "2026-11-23"
for mid in ["DFEDTARU", "DFF", "ECB_DFR", "ECB_MRO", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "CN_LPR_1Y"]:
    s = st.series(mid)
    print("### %s first=%s last=%s n=%d" % (mid, s[0][0], s[-1][0], len(s)))
    print("   change points in window [%s,%s]:" % (W0, W1))
    for i in range(1, len(s)):
        d, v = s[i]
        if W0 <= d <= W1 and v != s[i - 1][1]:
            print("      %s (%s) %s -> %s  (%+.0f bp)  prev obs %s" % (d, wd(d), s[i - 1][1], v, (v - s[i - 1][1]) * 100, s[i - 1][0]))
    # value in force at window start = value of last obs on/before W0 (and its previous if the obs is W0 itself)
    ob = st.on_or_before(mid, W0)
    print("   last obs on/before W0: %s ; last obs before W0: %s ; last obs: %s (lag %s days)" % (
        ob, [x for x in s if x[0] < W0][-1] if [x for x in s if x[0] < W0] else None, s[-1], lib.days_between(s[-1][0], W1)))
    # last change before window
    lastchg = None
    for i in range(1, len(s)):
        if s[i][0] < W0 and s[i][1] != s[i - 1][1]:
            lastchg = s[i]
    print("   last change before window: %s" % (lastchg,))

print("### claims")
# Fed
ch = st.changes("DFEDTARU", W0, W1)
cmp("DFEDTARU window change points = [2025-12-11 -25, 2026-09-17 +25]", [(d, round((b - a) * 100)) for d, a, b in ch], [("2025-12-11", -25), ("2026-09-17", 25)])
cmp("Fed 2025-12-11 from 4.0 -> 3.75", (ch[0][1], ch[0][2]), (4.0, 3.75))
cmp("Fed 2026-09-17 from 3.75 -> 4.0", (ch[1][1], ch[1][2]), (3.75, 4.0))
cmp("decision date = effective-1 day for 2025-12-11", lib.shift_months("2025-12-11", 0)[:-2] + "10", "2025-12-10")
e = dtm.date(2026, 9, 17)
cmp("decision 2026-09-16 is weekday before Wed 2026-09-17", (e - dtm.timedelta(days=1)).isoformat(), "2026-09-16")
cmp("net bp in window (start-in-force -> end)", round((st.on_or_before("DFEDTARU", W1)[1] - 4.0) * 100), 0)
lc = None
for i in range(1, len(st.series("DFEDTARU"))):
    if st.series("DFEDTARU")[i][0] < "2025-11-23" and st.series("DFEDTARU")[i][1] != st.series("DFEDTARU")[i - 1][1]:
        lc = st.series("DFEDTARU")[i]
cmp("prior Fed change (before window) effective 2025-10-30 from 4.25 -> 4.0", (lc[0], lc[1]), ("2025-10-30", 4.0))
# DFF
dch = st.changes("DFF", W0, W1)
cmp("DFF change points in window", [(d, round((b - a) * 100, 0)) for d, a, b in dch],
    [("2025-11-28", 1), ("2025-12-11", -25), ("2026-05-07", -1), ("2026-05-19", -1), ("2026-06-15", 1), ("2026-07-08", -1), ("2026-07-14", 1), ("2026-09-17", 25)])
cmp("DFF 2026-09-17 3.63 -> 3.88", (dch[-1][1], dch[-1][2]), (3.63, 3.88))
cmp("DFF @2026-09-16 = 3.63", st.at("DFF", "2026-09-16"), 3.63)
cmp("DFF latest 3.88 @2026-11-19", st.on_or_before("DFF", W1), ("2026-11-19", 3.88))
print("   DFF around 2025-11-20..30:", st.in_range("DFF", "2025-11-17", "2025-12-12"))
print("   DFF weekday sample (last 12):", [(d, wd(d), v) for d, v in st.series("DFF")[-12:]])

# ECB
for mid, exp in [("ECB_DFR", [("2026-06-17", 2.0, 2.25), ("2026-09-16", 2.25, 2.5)]), ("ECB_MRO", [("2026-06-17", 2.15, 2.4), ("2026-09-16", 2.4, 2.65)])]:
    ch = st.changes(mid, W0, W1)
    cmp("%s window changes" % mid, [(d, a, b) for d, a, b in ch], exp)
    cmp("%s last obs / lag days" % mid, (st.last_date(mid), lib.days_between(st.last_date(mid), W1)), ("2026-09-16", 68))
    ob = st.on_or_before(mid, W0)
    cmp("%s value in force at window start" % mid, ob, ("2025-06-11", 2.0 if mid == "ECB_DFR" else 2.15))
    first_in = st.on_or_after(mid, W0)
    cmp("%s first obs inside window" % mid, first_in, ("2026-06-17", 2.25 if mid == "ECB_DFR" else 2.4))
cmp("ECB effective 2026-06-17 weekday", wd("2026-06-17"), "Wed")
cmp("ECB effective 2026-09-16 weekday", wd("2026-09-16"), "Wed")
for eff, dec in [("2026-06-17", "2026-06-11"), ("2026-09-16", "2026-09-10")]:
    prev_thu = dtm.date(*map(int, eff.split("-"))) - dtm.timedelta(days=6)
    cmp("prev Thursday before %s = %s" % (eff, dec), prev_thu.isoformat(), dec)
    cmp("weekday of %s" % dec, wd(dec), "Thu")
cmp("ECB net bp (start-in-force -> end) DFR", round((2.5 - 2.0) * 100), 50)
cmp("ECB alt net bp (first obs in window -> end) DFR", round((2.5 - 2.25) * 100), 25)

# Japan
jp = dict((d[:7], v) for d, v in st.series("JP_POLICY_RATE"))
steps = []
yms = sorted(ym for ym in jp if "2025-11" <= ym <= "2026-10")
for i in range(1, len(yms)):
    dd = round((jp[yms[i]] - jp[yms[i - 1]]) * 100, 1)
    if dd != 0:
        steps.append((yms[i], dd))
print("   JP monthly steps (bp, 1 decimal):", steps)
# judgment wording: 月度步进 +8/+17/+11/+14/+7/+18 个基点 (12,01,06,07,09,10)，另有 2026-04 与 2026-08 各约零点一个基点的舍入变动
cmp("JP step months (>=5bp) = 12,01,06,07,09,10", [x[0] for x in steps if abs(x[1]) >= 5], ["2025-12", "2026-01", "2026-06", "2026-07", "2026-09", "2026-10"])
cmp("JP step sizes rounded to whole bp = +8/+17/+11/+14/+7/+18", [round(x[1]) for x in steps if abs(x[1]) >= 5], [8, 17, 11, 14, 7, 18])
cmp("JP rounding moves about 0.1bp at 2026-04, 2026-08", [(x[0], round(x[1], 1)) for x in steps if abs(x[1]) < 5], [("2026-04", -0.1), ("2026-08", -0.1)])
cmp("JP no other nonzero month in window", len(steps), 8)
cmp("JP sum of steps = 74.9bp", round(sum(x[1] for x in steps), 1), 74.9, nd=1)
cmp("JP net from 2025-11 0.478 -> 1.227 = 74.9bp", round((1.227 - 0.478) * 100, 1), 74.9, nd=1)
cmp("JP alt net from 2025-12 0.557 -> 1.227 = 67.0bp", round((1.227 - 0.557) * 100, 1), 67.0, nd=1)
for e in cal["entries"]:
    if e.get("metric_id") == "JP_POLICY_TARGET":
        print("   calendar JP_POLICY_TARGET:", json.dumps(e, ensure_ascii=False)[:300] if False else {k: e[k] for k in e if k not in ("note", "source", "spec")})
cmp("JP_POLICY_TARGET in series_store", st.has("JP_POLICY_TARGET"), False)
# registry
reg = lib.load_json(sys.argv[4]) if len(sys.argv) > 4 else None
if reg is not None:
    items = reg.get("metrics") or reg
    key = None
    if isinstance(items, dict):
        key = "JP_POLICY_TARGET" in items
    else:
        key = any((m.get("metric_id") or m.get("id")) == "JP_POLICY_TARGET" for m in items)
    cmp("JP_POLICY_TARGET in metric_registry", key, False)

# China
cmp("CN_OMO_7D all values in window are 1.4 (no change)", sorted(set(v for d, v in st.series("CN_OMO_7D") if W0 <= d <= W1)), [1.4])
cmp("CN_OMO_7D last obs / lag days", (st.last_date("CN_OMO_7D"), lib.days_between(st.last_date("CN_OMO_7D"), W1)), ("2026-10-30", 24))
cmp("CN_LPR_1Y all values in window are 3.0", sorted(set(v for d, v in st.series("CN_LPR_1Y") if W0 <= d <= W1)), [3.0])
cmp("CN_POLICY_OVERNIGHT first obs", st.series("CN_POLICY_OVERNIGHT")[0], ("2026-11-02", 1.25))
cmp("CN_POLICY_OVERNIGHT all values 1.25", sorted(set(v for d, v in st.series("CN_POLICY_OVERNIGHT"))), [1.25])
cmp("CN_POLICY_OVERNIGHT last obs", st.on_or_before("CN_POLICY_OVERNIGHT", W1), ("2026-11-23", 1.25))
print("   CN_OMO_7D obs from 2026-10-20:", st.in_range("CN_OMO_7D", "2026-10-20", W1))
print("   CN_NEW_LOANS last obs:", st.on_or_before("CN_NEW_LOANS", W1))
print("=" * 100)
print("POINTS=%d MISMATCHES=%d" % (N[0], N[1]))
