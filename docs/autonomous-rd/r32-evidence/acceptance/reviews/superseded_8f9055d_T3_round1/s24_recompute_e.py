#!/usr/bin/python3 -I
"""Recompute part E: statement-level Chinese-numeral magnitudes not yet tied to a row literal.
Each row recomputes the value from the snapshot/registry/calendar and requires the Chinese phrase to be
present verbatim in the contradiction statements. Phrases already covered by an OK row literal are listed
under "already_covered" and not counted twice.

Read-only. Args: <snapshot.json> <agent_judgment.json> <metric_registry.json> <out_dir>
"""
import datetime as dt
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("s10_common", os.path.join(HERE, "s10_common.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

snap, jd, reg, out_dir = C.load_json(sys.argv[1]), C.load_json(sys.argv[2]), C.load_json(sys.argv[3]), sys.argv[4]
ss = snap["series_store"]
regm = {m["metric_id"]: m for m in reg["metrics"]}
ST = [jd["l3"]["contradictions"][i]["statement"] for i in range(3)]
ALLST = "\n".join(ST)
lits = []
for part in "ABCD":
    for r in json.load(open(os.path.join(out_dir, "recompute_points_%s.json" % part), "r", encoding="utf-8"))["rows"]:
        if r.get("ok") and r.get("lit"):
            lits.append((r["id"], r["lit"]))
B = C.Book("E")
ea, jp = C.monthly(ss, "EA_HICP_YOY"), C.monthly(ss, "JP_CPI_YOY")
tk, pr = C.monthly(ss, "JP_CPI_TOKYO_YOY"), C.monthly(ss, "JP_POLICY_RATE")


def chg(mid, day):
    ds, vs = C.series(ss, mid)
    k = ds.index(day)
    j = k - 1
    while vs[j] == vs[k]:
        j -= 1
    return [ds[j], ds[k], vs[j], vs[k], C.rnd(C.bp(vs[k], vs[j]), 2)]


CAND = [
    ("E001", "C1 日本最新读数", "series_store.JP_CPI_YOY @2026-10", jp["2026-10"], 2.44, "最新读数百分之二点四四", 0),
    ("E002", "C1 欧元区最新读数", "series_store.EA_HICP_YOY @2026-10", ea["2026-10"], 4.0, "最新读数百分之四点零", 0),
    ("E003", "C1 东京最新读数", "series_store.JP_CPI_TOKYO_YOY @2026-10", tk["2026-10"], 2.73, "最新读数百分之二点七三", 0),
    ("E004", "C1 日本基期读数", "series_store.JP_CPI_YOY @2025-10", jp["2025-10"], 2.99, "去年同月(2025-10)为百分之二点九九", 0),
    ("E005", "C1 欧元区基期读数", "series_store.EA_HICP_YOY @2025-10", ea["2025-10"], 2.1, "去年同月(2025-10)为百分之二点一", 0),
    ("E006", "C1 日本同比差", "JP_CPI_YOY 2026-10 − 2025-10", C.rnd(jp["2026-10"] - jp["2025-10"], 2), -0.55, "回落约零点五五个百分点", 0),
    ("E007", "C1 欧元区同比差", "EA_HICP_YOY 2026-10 − 2025-10", C.rnd(ea["2026-10"] - ea["2025-10"], 2), 1.9, "抬升一点九个百分点", 0),
    ("E008", "C2 欧央行 2026-06-17 上调幅度", "ECB_MRO 2026-06-17 变更", chg("ECB_MRO", "2026-06-17")[4], 25, "各二十五个基点", 1),
    ("E009", "C2 欧央行 2026-09-16 上调幅度", "ECB_MRO 2026-09-16 变更", chg("ECB_MRO", "2026-09-16")[4], 25, "各二十五个基点", 1),
    ("E010", "C2 欧央行 MRO 现值", "series_store.ECB_MRO @2026-09-16", C.val_at(ss, "ECB_MRO", "2026-09-16"), 2.65, "最新生效水平为 二点六五", 1),
    ("E011", "C2 日本月均六个月前锚", "series_store.JP_POLICY_RATE @2026-04", pr["2026-04"], 0.727, "六个月前锚前值为零点七二七", 1),
    ("E012", "C2 日本月均最新", "series_store.JP_POLICY_RATE @2026-10", pr["2026-10"], 1.227, "2026-10 月均一点二二七", 1),
    ("E013", "C2 日本月均近12月起点", "series_store.JP_POLICY_RATE @2025-11", pr["2025-11"], 0.478, "自 2025-11 月均零点四七八", 1),
    ("E014", "C2 维持后天数", "2026-10-30→2026-11-23", (dt.date(2026, 11, 23) - dt.date(2026, 10, 30)).days, 24, "二十四天内", 1),
    ("E015", "C2/C3 观测滞后", "2026-09-16→2026-11-23", (dt.date(2026, 11, 23) - dt.date(2026, 9, 16)).days, 68, "距截止六十八天", 1),
    ("E016", "C3 注册表新鲜度阈", "metric_registry.ECB_MRO.freshness.max_calendar_lag_days",
     regm["ECB_MRO"]["freshness"]["max_calendar_lag_days"], 10, "超过注册表新鲜度阈十天", 2),
    ("E017", "C3 注册表新鲜度阈(DFR)", "metric_registry.ECB_DFR.freshness.max_calendar_lag_days",
     regm["ECB_DFR"]["freshness"]["max_calendar_lag_days"], 10, "注册表新鲜度阈十天", 2),
]
already = []
for cid, where, src, comp, rep, lit, si in CAND:
    cov = [rid for rid, l in lits if lit in l or l in lit]
    add_id = cid if not cov else cid + "X"
    B.add(add_id, "E-陈述层中文数字", where, src, comp, rep, lit=lit, text=ST[si],
          note=("已由 %s 的字面覆盖,不重复计数" % ",".join(cov)) if cov else "")
    if cov:
        already.append({"phrase": lit, "rows": cov})
p = B.save(out_dir)
bad = [(r["id"], r["computed"], r["reported"], r["lit_found"]) for r in B.rows if not r["ok"]]
print("PART E: points=%d ok=%d mismatch=%d | already covered=%d" % (len(B.rows), B.n_ok(), len(B.rows) - B.n_ok(), len(already)))
for r in B.rows:
    print("  ", r["id"], r["ok"], "|", r["where"], "|", r["computed"], "|", r["reported"], "| lit", r["lit_found"])
for b in bad:
    print("  MISMATCH", b)
