#!/usr/bin/python3 -I
"""Recompute part D (sweep closure): every (metric, month/date, value) pair quoted in the judgment's
claim-bearing texts is recomputed from the snapshot and compared with the judgment literal. Pairs that
an already-OK row of parts A/B/C covers (same metric + same month/date in the row's computation label
+ same value) are listed under "already_covered" and not counted twice.

Read-only. Args: <snapshot.json> <agent_judgment.json> <metric_registry.json> <out_dir>
"""
import datetime as dt
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("s10_common", os.path.join(HERE, "s10_common.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

snap, jd, reg, out_dir = (C.load_json(sys.argv[1]), C.load_json(sys.argv[2]), C.load_json(sys.argv[3]),
                          sys.argv[4])
ss = snap["series_store"]
regm = {m["metric_id"]: m for m in reg["metrics"]}
ALLTXT = C.all_text({k: v for k, v in jd.items() if k != "contract_verification"})
B = C.Book("D")
add = B.add


def flatnums(x, sink):
    if isinstance(x, bool):
        return
    if isinstance(x, (int, float)):
        sink.append(round(abs(float(x)), 4))
    elif isinstance(x, str):
        for m in re.findall(r"-?\d+(?:\.\d+)?", x):
            try:
                sink.append(round(abs(float(m)), 4))
            except ValueError:
                pass
    elif isinstance(x, (list, tuple)):
        for y in x:
            flatnums(y, sink)
    elif isinstance(x, dict):
        for y in x.values():
            flatnums(y, sink)


existing = []
for part in "ABC":
    existing += json.load(open(os.path.join(out_dir, "recompute_points_%s.json" % part), "r",
                               encoding="utf-8"))["rows"]


def covered_by(mid, key, value):
    for r in existing:
        if not r.get("ok"):
            continue
        s = json.dumps(r, ensure_ascii=False)
        if mid in s and key in s:
            nums = []
            flatnums(r.get("computed"), nums)
            flatnums(r.get("reported"), nums)
            if round(abs(float(value)), 4) in nums:
                return r["id"]
    return None


# (metric, key in series, month/date literal as quoted, value as quoted, literal as quoted)
PAIRS = [
    # M1 step 1 / T2 / TL1 (EA HICP path)
    ("EA_HICP_YOY", "2025-11", "2025-11", "2.1", "2025-11 2.1"),
    ("EA_HICP_YOY", "2026-01", "2026-01", "1.7", "2026-01 的 1.7"),
    ("EA_HICP_YOY", "2026-02", "2026-02", "1.9", "2026-02 的 1.9"),
    ("EA_HICP_YOY", "2026-04", "2026-04", "3.0", "2026-04=3.0"),
    ("EA_HICP_YOY", "2026-05", "2026-05", "3.2", "2026-05 的 3.2"),
    ("EA_HICP_YOY", "2026-06", "2026-06", "2.8", "2026-06 2.8"),
    ("EA_HICP_YOY", "2026-07", "2026-07", "2.9", "2026-07=2.9"),
    ("EA_HICP_YOY", "2026-08", "2026-08", "3.2", "2026-08=3.2"),
    ("EA_HICP_YOY", "2026-09", "2026-09", "3.8", "2026-09 3.8"),
    ("EA_HICP_YOY", "2026-10", "2026-10", "4.0", "2026-10 4.0"),
    # JP CPI path
    ("JP_CPI_YOY", "2025-01", "2025-01", "4.03", "2025-01 高点 4.03"),
    ("JP_CPI_YOY", "2025-07", "2025-07", "3.1", "2025-07 的 3.1"),
    ("JP_CPI_YOY", "2025-09", "2025-09", "2.91", "2025-09"),
    ("JP_CPI_YOY", "2025-10", "2025-10", "2.99", "2.99"),
    ("JP_CPI_YOY", "2025-11", "2025-11", "2.9", "2025-11→2026-02 由 2.9 降至 1.27"),
    ("JP_CPI_YOY", "2026-02", "2026-02", "1.27", "2026-02 1.27"),
    ("JP_CPI_YOY", "2026-03", "2026-03", "1.46", "2026-03 1.46"),
    ("JP_CPI_YOY", "2026-04", "2026-04", "1.38", "2026-04 1.38"),
    ("JP_CPI_YOY", "2026-05", "2026-05", "1.53", "2026-05 1.53"),
    ("JP_CPI_YOY", "2026-06", "2026-06", "1.67", "2026-06 1.67"),
    ("JP_CPI_YOY", "2026-07", "2026-07", "1.97", "2026-07 1.97"),
    ("JP_CPI_YOY", "2026-08", "2026-08", "1.98", "2026-08 1.98"),
    ("JP_CPI_YOY", "2026-09", "2026-09", "2.16", "2026-09 2.16"),
    ("JP_CPI_YOY", "2026-10", "2026-10", "2.44", "2026-10 2.44"),
    ("JP_CPI_TOKYO_YOY", "2026-04", "2026-04", "1.42", "1.42%"),
    ("JP_CPI_TOKYO_YOY", "2026-10", "2026-10", "2.73", "2.73%"),
    # JP policy monthly average path
    ("JP_POLICY_RATE", "2025-11", "2025-11", "0.478", "0.478"),
    ("JP_POLICY_RATE", "2026-01", "2026-01", "0.728", "2026-01 0.728"),
    ("JP_POLICY_RATE", "2026-04", "2026-04", "0.727", "0.727"),
    ("JP_POLICY_RATE", "2026-06", "2026-06", "0.841", "2026-06 0.841"),
    ("JP_POLICY_RATE", "2026-07", "2026-07", "0.978", "0.978"),
    ("JP_POLICY_RATE", "2026-08", "2026-08", "0.977", "2026-08 0.977"),
    ("JP_POLICY_RATE", "2026-09", "2026-09", "1.043", "1.043"),
    ("JP_POLICY_RATE", "2026-10", "2026-10", "1.227", "1.227"),
]
already = []
n_new = 0
for i, (mid, key, qlit, qval, lit) in enumerate(PAIRS):
    v = C.mv(ss, mid, key)
    cid = "D%03d" % (i + 1)
    cov = covered_by(mid, key, float(qval))
    if cov:
        already.append({"metric": mid, "month": key, "value": v, "row": cov})
        cid = "D%03dX" % (i + 1)
    add(cid, "D-月度点值对", "判断档月度路径点值", "series_store.%s @%s" % (mid, key), v, float(qval),
        lit=lit, text=ALLTXT, note=("已由 %s 覆盖,不重复计数" % cov) if cov else "")
    if not cov:
        n_new += 1

# ---- extra pairs not of month form
EXTRA = [
    ("ECB_MRO", "2025-06-11", "2.15", "2.15% 升至最新一期锚(观测 2026-09-16)的 2.65%"),
    ("ECB_MRO", "2026-09-16", "2.65", "2.65%"),
    ("ECB_DFR", "2025-06-11", "2.0", "由 2.0% 升至 2.5%"),
    ("ECB_DFR", "2026-09-16", "2.5", "2.5%"),
    ("USDJPY", "2026-11-23", "159.35", "159.35"),
    ("SPX", "2026-11-23", "7203.85", "7203.85"),
    ("VIX", "2026-11-23", "27.01", "27.01"),
    ("UST_10Y", "2026-11-19", "5.04", "5.04%"),
    ("EURUSD", "2026-10-23", "1.1221", "1.1221"),
    ("EURUSD", "2026-11-20", "1.0970", "1.0970"),
    ("USDJPY", "2026-10-23", "156.494", "156.494"),
    ("USDJPY", "2026-11-20", "159.707", "159.707"),
    ("DXY", "2026-10-23", "101.81", "101.81"),
    ("DXY", "2026-11-20", "103.81", "103.81"),
    ("DXY", "2026-11-23", "104.079", "104.079"),
    ("EURUSD", "2026-11-23", "1.0940", "1.0940"),
    ("USDJPY", "2026-11-23", "159.347", "159.347"),
    ("NIKKEI225", "2026-11-20", "56436.65", "56436.65"),
    ("DAX", "2026-11-23", "25209.45", "25209.45"),
    ("VIX", "2026-11-13", "19.30", "11-13 19.30"),
    ("VIX", "2026-11-16", "22.91", "11-16 22.91"),
    ("VIX", "2026-11-17", "25.46", "11-17 25.46"),
    ("VIX", "2026-11-18", "24.56", "11-18 24.56"),
    ("VIX", "2026-11-19", "28.44", "11-19 28.44"),
    ("VIX", "2026-11-20", "35.89", "11-20 35.89"),
    ("VIX", "2026-11-04", "16.61", "16.61→28.18"),
    ("VIX", "2026-11-05", "28.18", "16.61→28.18"),
    ("VIX", "2026-11-11", "17.49", "17.49"),
]
for j, (mid, day, qval, lit) in enumerate(EXTRA):
    v = C.val_at(ss, mid, day)
    cid = "D1%02d" % (j + 1)
    cov = covered_by(mid, day, float(qval))
    if cov:
        already.append({"metric": mid, "date": day, "value": v, "row": cov})
        cid = "D1%02dX" % (j + 1)
    add(cid, "D-日频点值对", "判断档日频点值", "series_store.%s @%s" % (mid, day), v, float(qval),
        lit=lit, text=ALLTXT, note=("已由 %s 覆盖,不重复计数" % cov) if cov else "")
    if not cov:
        n_new += 1

# ---- sweep leftovers that are not (metric, date) pairs
mo = C.monthly(ss, "JP_POLICY_RATE")
yms = sorted(k for k in mo if "2025-11" <= k <= "2026-10")
add("D200", "D-窗长", "JP 走位「近 12 个月月均由 2025-11 的 0.478 升至 2026-10 的 1.227」", "JP_POLICY_RATE 月度观测数 2025-11..2026-10",
    [len(yms), yms[0], yms[-1]], [12, "2025-11", "2026-10"], lit="近 12 个月月均由 2025-11 的 0.478 升至 2026-10 的 1.227", text=ALLTXT)
mv = []
for mid in ("EURUSD", "USDJPY"):
    ds, vs = C.series(ss, mid)
    for day in ("2026-11-16", "2026-11-20"):
        k = ds.index(day)
        mv.append([mid, day, C.rnd(C.pct(vs[k], vs[k - 1]), 4)])
add("D201", "D-单日变动", "M1-4/TL3「两日欧元、日元对美元单日变动幅度不超过 0.23%」", "EURUSD/USDJPY 2026-11-16、2026-11-20 单日变动%",
    [mv, C.rnd(max(abs(x[2]) for x in mv), 2)], [4, 0.23], ok=(len(mv) == 4 and C.rnd(max(abs(x[2]) for x in mv), 2) <= 0.23),
    lit="单日变动幅度不超过 0.23%", text=ALLTXT, note=json.dumps(mv, ensure_ascii=False))
fed = []
for mid in ("DFEDTARU", "DFEDTARL"):
    ds, vs = C.series(ss, mid)
    k = len(vs) - 1
    while k > 0 and vs[k - 1] == vs[k]:
        k -= 1
    fed.append([mid, ds[k], vs[k], C.last_obs(ss, mid)])
add("D202", "D-美联储变动点", "TL2「美联储 2026-09-17 生效」", "DFEDTARU/DFEDTARL 最近变动日", fed,
    [[("DFEDTARU", "2026-09-17"), ("DFEDTARL", "2026-09-17")][0][1], [("DFEDTARU", "2026-09-17"), ("DFEDTARL", "2026-09-17")][1][1]],
    ok=all(x[1] == "2026-09-17" for x in fed), lit="美联储 2026-09-17 生效", text=ALLTXT,
    note=json.dumps(fed, ensure_ascii=False))
ea = C.monthly(ss, "EA_HICP_YOY")
win = {k: ea[k] for k in sorted(ea) if "2025-11" <= k <= "2026-10"}
mx = max(win, key=lambda k: win[k])
add("D203", "D-近十二个月最高", "T2 叙事「最新读数为近十二个月最高」", "EA_HICP_YOY 2025-11..2026-10 最大值月",
    [mx, win[mx], len(win)], ["2026-10", 4.0, 12], lit="最新读数为近十二个月最高", text=ALLTXT)
calc = regm["JP_CPI_YOY"].get("calc")
add("D204", "D-口径文字", "M1-1「(新基优先,重叠差>0.10pp 告警)」", "metric_registry.JP_CPI_YOY.calc 含 0.10 告警阈",
    [bool(re.search(r"0\.10", str(calc))), "新基优先" in str(calc)], [True, True],
    lit="重叠差>0.10pp 告警", text=ALLTXT, note="registry calc: " + str(calc))
print("registry JP_CPI_YOY.calc =", calc)
print("already covered pairs:", len(already), "| new pair rows:", n_new)
p = B.save(out_dir)
json.dump({"already_covered": already}, open(os.path.join(out_dir, "recompute_points_D_covered.json"), "w",
                                          encoding="utf-8"), ensure_ascii=False, indent=1)
bad = [(r["id"], r["src"], r["computed"], r["reported"], r["lit_found"]) for r in B.rows if not r["ok"]]
print("PART D: points=%d ok=%d mismatch=%d" % (len(B.rows), B.n_ok(), len(B.rows) - B.n_ok()))
for b in bad:
    print("  MISMATCH", b)
print(p)
