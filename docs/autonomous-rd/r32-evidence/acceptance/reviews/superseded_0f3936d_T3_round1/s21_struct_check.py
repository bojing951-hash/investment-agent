#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只读结构核对面(不读 report.json 的 semantic_review 取值): 打印复算脚本所依赖的键结构与少量取值。
usage: s21_struct_check.py <snapshot.json> <report.json> <agent_judgment.json> <evidence_index.json>"""
import json
import sys

snap, rep, aj, ev = (json.load(open(p, "r", encoding="utf-8")) for p in sys.argv[1:5])


def short(x, n=140):
    s = json.dumps(x, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "…"


print("scenario_ids:", [s["id"] for s in aj["l4"]["scenarios"]])
print("scenario rows keys:", sorted(aj["l4"]["scenarios"][0]["rows"].keys()))
print("S1 falsification:", short(aj["l4"]["scenarios"][0]["rows"]["falsification"]))
print("S2 falsification:", short(aj["l4"]["scenarios"][1]["rows"]["falsification"]))
print("S1 trigger:", short(aj["l4"]["scenarios"][0]["rows"]["trigger"]))
print("S2 trigger:", short(aj["l4"]["scenarios"][1]["rows"]["trigger"]))
tc = rep["research_plan"]["turning_candidates"]
print("turning_candidates keys:", sorted(tc.keys()))
for c in tc["candidates"]:
    print("  cand:", short(c, 260))
print("turnings[0] keys:", sorted(aj["reader_map"]["turnings"][0].keys()))
for t in aj["reader_map"]["turnings"]:
    print("  turning:", t["metric_id"], t["before_date"], t["date"], t["value_before"], t["value_after"])
cv = rep["agent_judgment"]["contract_verification"]
print("cv keys:", sorted(cv.keys()))
for v in cv["verdicts"]:
    print("  cv:", short(v, 300))
print("cv verdict:", cv.get("verdict"), "| six_checks:", short(cv.get("six_checks"), 400))
st = [s for s in rep["steps"] if s.get("step") == "S6_analog"]
print("steps ids:", [s.get("step") for s in rep["steps"]])
if st:
    d6 = st[0]["envelope"]["data"]
    print("S6 data keys:", sorted(d6.keys()), "| candidates:", short(d6["candidates"]), "| top0:", short(d6["top"][0]))
g = snap["gate_a"]
print("gate_a keys:", sorted(g.keys()))
for k in ("status", "core_missing", "core_fail", "noncore_fail", "noncore_missing", "noncore_degraded"):
    print("  ", k, "=", short(g.get(k)))
print("  noncore_missing_detail keys:", sorted((g.get("noncore_missing_detail") or {}).keys()))
print("  nmd Tokyo:", short((g.get("noncore_missing_detail") or {}).get("JP_CPI_TOKYO_YOY")))
f = [x for x in snap["facts"] if x["fact_id"] == "ECB_DFR@2026-09-16"][0]
print("ECB_DFR fact issues:", short(f.get("issues"), 400), "| quality:", f.get("quality_status"))
cells = rep["research_plan"]["point_values"]["cells"]
c0 = cells[0]
print("cell keys:", sorted(c0.keys()))
print("policy_window_path MRO:", short([c["policy_window_path"] for c in cells if c["metric_id"] == "ECB_MRO"], 500))
print("policy_window_path JP_POLICY_RATE:", short([c["policy_window_path"] for c in cells if c["metric_id"] == "JP_POLICY_RATE"], 500))
print("anchors keys:", sorted(c0["anchors"].keys()), "| status:", c0["anchors"]["最新一期"]["status"])
print("ev rows:", len(ev), "| keys:", sorted(ev[0].keys()))
print("ev metrics with FED/DFEDTAR/DFF:", sorted({r.get("metric_id") for r in ev if r.get("metric_id") and ("FED" in r.get("metric_id") or "DFF" in r.get("metric_id"))}))
print("ev metric_ids:", sorted({r.get("metric_id") for r in ev if r.get("metric_id")}))
print("dimension_gaps:", short(rep["research_plan"].get("dimension_gaps")))
print("research_as_of:", snap.get("research_as_of"), "| target_date:", snap.get("target_date"))
print("SS has DFEDTARU/DFEDTARL/DFF:", [m in snap["series_store"] for m in ("DFEDTARU", "DFEDTARL", "DFF")])
print("history_periods:", aj["reader_map"].get("history_periods"), "| history_zero_case_note:", short(aj["reader_map"].get("history_zero_case_note"), 200))
for l in aj["reader_map"]["transmission"][0]["links"]:
    print("link verdict:", l["face_off_verdict"], "| metric:", l.get("distinguishing_metric"))
