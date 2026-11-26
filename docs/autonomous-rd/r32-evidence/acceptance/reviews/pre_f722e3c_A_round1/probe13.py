#!/usr/bin/env python3
"""Probe 13: facts structure + selected series checks for rc_d (read-only).

usage: python3 -I probe13.py <snapshot.json> <report.json> <out.txt>
"""
import json
import sys
from collections import Counter

snap = json.load(open(sys.argv[1], encoding="utf-8"))
rep = json.load(open(sys.argv[2], encoding="utf-8"))
out = open(sys.argv[3], "w", encoding="utf-8")


def w(s=""):
    out.write(s + "\n")


facts = snap.get("facts")
w("facts type=%s len=%s" % (type(facts).__name__, len(facts) if hasattr(facts, "__len__") else None))
if isinstance(facts, dict):
    ks = list(facts.keys())
    w("facts keys sample: %s" % ks[:8])
    w("one fact: %s" % json.dumps(facts[ks[0]], ensure_ascii=False)[:600])
    cnt = Counter(str((v.get("metric_id") if isinstance(v, dict) else "?")) for v in facts.values())
else:
    w("one fact: %s" % json.dumps(facts[0], ensure_ascii=False)[:600])
    cnt = Counter(str((v.get("metric_id") if isinstance(v, dict) else "?")) for v in facts)
w("facts by metric: " + json.dumps(dict(sorted(cnt.items())), ensure_ascii=False))
ss = snap["series_store"]
for sid in ("CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY", "CN_NEW_LOANS",
            "USDCNY", "USREC"):
    w("facts[%s]=%s series=%s" % (sid, cnt.get(sid, 0), "present" if sid in ss else "ABSENT"))
s = ss.get("CN_NEW_LOANS")
if s:
    ds = [(d, v) for d, v in zip(s["dates"], s["values"]) if v is not None]
    w("CN_NEW_LOANS n=%d first=%s last=%s last3=%s" % (len(ds), ds[0][0], ds[-1][0], ds[-3:]))
s = ss.get("USDCNY")
ds = [(d, v) for d, v in zip(s["dates"], s["values"]) if v is not None]
w("USDCNY n=%d last=%s" % (len(ds), ds[-1]))


def lob(sid, d):
    b = None
    for dd, v in zip(ss[sid]["dates"], ss[sid]["values"]):
        if v is None:
            continue
        if dd <= d:
            b = (dd, v)
        else:
            break
    return b


def last_in(sid, ym):
    b = None
    for dd, v in zip(ss[sid]["dates"], ss[sid]["values"]):
        if v is None:
            continue
        if dd.startswith(ym):
            b = (dd, v)
    return b


w("=== 12m changes for C1 attack ===")
for sid in ("SPX", "NIKKEI225", "GOLD_F", "DXY", "UST_10Y", "TIPS_10Y", "BEI_10Y", "HY_OAS", "USDJPY", "SHCOMP", "DAX"):
    a = lob(sid, "2025-11-19")
    b = lob(sid, "2026-11-23")
    w("%s: %s -> %s chg_pct=%s chg_abs=%s" % (sid, a, b, None if not (a and b) else round((b[1] / a[1] - 1) * 100, 4),
                                             None if not (a and b) else round(b[1] - a[1], 4)))
w("=== BEI_10Y path (month-end) 2025-11..2026-11 ===")
w(json.dumps({ym: last_in("BEI_10Y", ym) for ym in ["2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04", "2026-05",
                                                      "2026-06", "2026-07", "2026-08", "2026-09", "2026-10", "2026-11"]}))
vals = [(d, v) for d, v in zip(ss["BEI_10Y"]["dates"], ss["BEI_10Y"]["values"]) if v is not None]
w("BEI_10Y full n=%d first=%s min=%s max=%s; last12m min=%s" % (
    len(vals), vals[0], min(vals, key=lambda t: t[1]), max(vals, key=lambda t: t[1]),
    min([t for t in vals if t[0] >= "2025-11-23"], key=lambda t: t[1])))
cp = ss["CORE_PCE"]
cpts = [(d, v) for d, v in zip(cp["dates"], cp["values"]) if v is not None]
idx = {d[:7]: v for d, v in cpts}
yo = {}
for m in sorted(idx):
    y, mm = int(m[:4]), int(m[5:7])
    b = "%04d-%02d" % (y - 1, mm)
    if b in idx:
        yo[m] = round((idx[m] / idx[b] - 1) * 100, 4)
w("CORE_PCE YoY 2025-06..: " + json.dumps({m: v for m, v in yo.items() if m >= "2025-06"}))
w("=== 2022-06 / 2025-03 / 2023-10 month-end windows for C2 / scenarios ===")


def me(sid, ym):
    return last_in(sid, ym)


for cand in ("2022-06", "2025-03", "2023-10"):
    for n in (3, 6, 12):
        y, m = int(cand[:4]), int(cand[5:7])
        tot = y * 12 + (m - 1) + n
        ny, nm = divmod(tot, 12)
        end_ym = "%04d-%02d" % (ny, nm + 1)
        row = {}
        for sid in ("SPX", "DAX", "SHCOMP", "NIKKEI225", "GOLD_F", "DXY"):
            a = me(sid, cand)
            b = me(sid, end_ym)
            row[sid] = None if not (a and b) else [a[0], b[0], round((b[1] / a[1] - 1) * 100, 4)]
        w("%s +%dm (%s): %s" % (cand, n, end_ym, json.dumps(row)))
w("=== research_as_of ===")
w(snap.get("research_as_of"))
w("=== report.md gate lines (via report.json steps) ===")
l1 = rep.get("layers", {}).get("L1_事实层", {})
rows = l1.get("rows") or []
w("L1 rows n=%d; metrics=%s" % (len(rows), sorted({str(r.get("metric_id")) for r in rows})))
out.close()
print("written", sys.argv[3])
