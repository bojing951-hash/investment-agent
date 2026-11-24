#!/usr/bin/env python3
"""Probe 12: judgment faces for the six checks (l3/l4/reader_map), run/gate faces, series checks for sections ⑨-⑬.

usage: python3 -I probe12.py <snapshot.json> <report.json> <agent_judgment.json> <out.txt>
"""
import json
import sys

snap = json.load(open(sys.argv[1], encoding="utf-8"))
rep = json.load(open(sys.argv[2], encoding="utf-8"))
aj = json.load(open(sys.argv[3], encoding="utf-8"))
out = open(sys.argv[4], "w", encoding="utf-8")


def w(s=""):
    out.write(s + "\n")


def pj(obj, limit=6000, indent=None):
    w(json.dumps(obj, ensure_ascii=False, indent=indent)[:limit])


w("=== snapshot research_as_of / gate_a / quality ===")
for k in ("research_as_of", "as_of", "target_date", "snapshot_id", "timezone", "generated_at", "collected_at"):
    if k in snap:
        w("snap.%s = %s" % (k, snap[k]))
w("top keys: " + str(list(snap.keys())))
pj(snap.get("gate_a"), 8000, 1)
q = snap.get("quality")
if isinstance(q, dict):
    w("quality keys: " + str(list(q.keys())))
    for k, v in q.items():
        w("  quality.%s: %s" % (k, json.dumps(v, ensure_ascii=False)[:1200]))
ss = snap["series_store"]
w("series n=%d" % len(ss))
w("=== series presence for gate lists ===")
for sid in ("BUND_10Y", "BUND_2Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY",
            "JP_REAL_GDP_YOY", "CN_SF_FLOW", "ECB_DFR", "ECB_MRO", "JTSJOL", "M2SL", "SPX_EPS", "SPX_PE_TTM",
            "US_REAL_GDP", "JP_POLICY_TARGET", "JGB10Y", "JGB2Y", "UST_2Y", "USREC"):
    s = ss.get(sid)
    if s is None:
        w("%s: ABSENT" % sid)
    else:
        ds = [d for d, v in zip(s["dates"], s["values"]) if v is not None]
        w("%s: n=%d first=%s last=%s" % (sid, len(ds), ds[0] if ds else None, ds[-1] if ds else None))

w("=== report.json run block ===")
run = rep.get("run") or {}
for k, v in run.items():
    w("run.%s: %s" % (k, json.dumps(v, ensure_ascii=False)[:900]))
w("=== steps gate_a ===")
from collections import Counter
cnt = Counter()
for st in rep["steps"]:
    env = st.get("envelope") or {}
    ga = env.get("gate_a")
    stat = ga.get("status") if isinstance(ga, dict) else ga
    cnt[str(stat)] += 1
w(str(dict(cnt)) + " n_steps=%d" % len(rep["steps"]))
for st in rep["steps"]:
    env = st.get("envelope") or {}
    ga = env.get("gate_a")
    if isinstance(ga, dict):
        w("step %s gate_a keys=%s" % (st.get("step"), list(ga.keys())))
        w(json.dumps(ga, ensure_ascii=False)[:1500])
        break
w("=== research_plan.dimension_gaps / policy_doc_facts ===")
rp = rep.get("research_plan") or {}
pj(rp.get("dimension_gaps"), 4000, 1)
w("=== contract_verification ===")
cv = (rep.get("agent_judgment") or {}).get("contract_verification")
if isinstance(cv, dict):
    w("cv keys: " + str(list(cv.keys())))
    for k, v in cv.items():
        if k != "verdicts":
            w("cv.%s: %s" % (k, json.dumps(v, ensure_ascii=False)[:600]))
    vs = cv.get("verdicts") or []
    w("n verdicts=%d" % len(vs))
    c2 = Counter((v.get("verdict") or v.get("status") or "?") for v in vs if isinstance(v, dict))
    w(str(dict(c2)))
    for v in vs:
        if isinstance(v, dict) and str(v.get("verdict") or v.get("status")) not in ("OK", "PASS", "MATCH"):
            w("  " + json.dumps(v, ensure_ascii=False)[:500])

w("=== agent_judgment.json ===")
w("keys: " + str(list(aj.keys())))
pj(aj.get("agent_declaration"), 3000, 1)
l3 = aj.get("l3") or {}
w("l3 keys: " + str(list(l3.keys())))
for k, v in l3.items():
    w("--- l3.%s" % k)
    pj(v, 12000, 1)
l4 = aj.get("l4") or {}
w("l4 keys: " + str(list(l4.keys())))
for k, v in l4.items():
    w("--- l4.%s" % k)
    pj(v, 8000, 1)
rm = aj.get("reader_map") or {}
w("reader_map keys: " + str(list(rm.keys())))
for k in ("headline_conclusion", "transmission", "turnings", "turning_supplement", "confrontation", "scenarios"):
    if k in rm:
        w("--- reader_map.%s" % k)
        pj(rm[k], 9000, 1)
for k in rm:
    if k not in ("headline_conclusion", "transmission", "turnings", "turning_supplement", "confrontation", "scenarios",
                 "history_periods", "regions", "asset_returns_echo", "rates_decomposition"):
        w("--- reader_map.%s" % k)
        pj(rm[k], 2500, 1)

w("=== series checks ===")


def path(sid, ym0, ym1):
    s = ss.get(sid)
    d = {dd[:7]: v for dd, v in zip(s["dates"], s["values"]) if v is not None and ym0 <= dd[:7] <= ym1}
    return d


def exact(sid, d):
    s = ss.get(sid)
    for dd, v in zip(s["dates"], s["values"]):
        if dd == d:
            return v
    return None


w("CN_PMI_MFG 2025-10..2026-10: " + json.dumps(path("CN_PMI_MFG", "2025-10", "2026-10")))
for m in ("2024-10", "2024-11", "2024-12", "2025-10", "2025-11", "2025-12", "2026-09", "2026-10"):
    w("CPI level %s = %s" % (m, exact("CPI", m + "-01")))
cpi = path("CPI", "2025-01", "2026-10")
w("CPI YoY 2025-06..2026-10: " + json.dumps({m: round((cpi[m] / cpi["%04d-%02d" % (int(m[:4]) - 1, int(m[5:7]))] - 1) * 100, 4)
                                            for m in sorted(cpi) if m >= "2025-06" and "%04d-%02d" % (int(m[:4]) - 1, int(m[5:7])) in cpi}))
for sid in ("SPX", "SHCOMP", "DAX", "NIKKEI225", "VIX", "DXY", "GOLD_F", "UST_10Y", "BRENT_F", "USDJPY", "TIPS_10Y",
            "BEI_10Y", "HY_OAS", "DFEDTARU", "DFF", "CN_POLICY_OVERNIGHT", "CN_OMO_7D", "USDEUR", "EURUSD"):
    s = ss.get(sid)
    if s is None:
        w("%s ABSENT" % sid)
        continue
    ds = [(d, v) for d, v in zip(s["dates"], s["values"]) if v is not None]
    w("%s last3=%s" % (sid, ds[-3:]))
w("series ids: " + ",".join(sorted(ss.keys())))
out.close()
print("written", sys.argv[4])
