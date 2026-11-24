#!/usr/bin/env python3
"""Probe report.json engine faces (read-only).

usage: python3 -I probe3.py <report.json> <out.txt>
"""
import json
import sys

rep_path, out_path = sys.argv[1:3]
rep = json.load(open(rep_path, "r", encoding="utf-8"))
out = open(out_path, "w", encoding="utf-8")


def w(s=""):
    out.write(s + "\n")


def short(obj, n=1500):
    return json.dumps(obj, ensure_ascii=False)[:n]


run = rep["run"]
w("=== run ===")
for k, v in run.items():
    w(f"{k}: {short(v, 800)}")

rp = rep["research_plan"]
w("\n=== research_plan keys ===")
for k, v in rp.items():
    if isinstance(v, (dict, list)):
        w(f"{k}: {type(v).__name__} len={len(v)}")
    else:
        w(f"{k}: {short(v, 600)}")

w("\n--- point_anchors ---")
w(short(rp["point_anchors"], 2000))
w("\n--- regions ---")
w(short(rp["regions"], 3000))
w("\n--- metrics ---")
w(short(rp["metrics"], 6000))
w("\n--- question_window ---")
w(short(rp["question_window"], 1000))
w("\n--- ex_post_offsets ---")
w(short(rp["ex_post_offsets"], 1000))
w("\n--- anchor_semantics_note ---")
w(short(rp["anchor_semantics_note"], 1000))
w("\n--- dimension_gaps ---")
w(short(rp["dimension_gaps"], 3000))
w("\n--- cutoff ---")
w(short(rp["cutoff"], 1000))
w("\n--- consumed_time_spans ---")
w(short(rp["consumed_time_spans"], 3000))
w("\n--- as_of_declared ---")
w(short(rp["as_of_declared"], 1000))
w("\n--- map_question / question_summary / dimension_source / asof_discipline / cross_face_consistency ---")
w(short(rp["map_question"], 1500))
w(short(rp["question_summary"], 1500))
w(short(rp["dimension_source"], 1500))
w(short(rp["asof_discipline"], 1500))
w(short(rp["cross_face_consistency"], 1500))

w("\n--- point_values ---")
w(short(rp["point_values"], 12000))
w("\n--- turning_candidates ---")
w(short(rp["turning_candidates"], 6000))
w("\n--- us_rates_trio ---")
w(short(rp["us_rates_trio"], 6000))
w("\n--- asset_moves ---")
w(short(rp["asset_moves"], 6000))
w("\n--- policy_event_clusters ---")
w(short(rp["policy_event_clusters"], 6000))
w("\n--- policy_doc_facts ---")
w(short(rp["policy_doc_facts"], 3000))

w("\n=== layers keys ===")
for lk, lv in rep["layers"].items():
    w(f"{lk}: {type(lv).__name__} keys={list(lv.keys())[:30] if isinstance(lv, dict) else ''}")
l1 = rep["layers"]["L1_事实层"]
w("\n--- L1 rows[0] ---")
w(short(l1["rows"][0], 1500))
w(f"L1 rows n={len(l1['rows'])}")

aj = rep["agent_judgment"]
w("\n=== report.agent_judgment ===")
for k, v in aj.items():
    w(f"{k}: {short(v, 1500)}")

w("\n=== semantic_review ===")
w(short(rep["semantic_review"], 2000))

w("\n=== steps (name, status, envelope keys) ===")
for i, st in enumerate(rep["steps"]):
    name = st.get("name") or st.get("step") or st.get("id")
    env = st.get("envelope")
    keys = list(env.keys())[:25] if isinstance(env, dict) else type(env).__name__
    w(f"[{i}] {name} keys={list(st.keys())[:12]} envelope_keys={keys}")

w("\n=== fanout / notes / evidence_index[0] ===")
w(short(rep["fanout"], 500))
w(short(rep["notes"], 2000))
w(short(rep["evidence_index"][0], 800))
out.close()
print("written", out_path)
