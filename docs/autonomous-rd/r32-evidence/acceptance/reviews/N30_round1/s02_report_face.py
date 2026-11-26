# -*- coding: utf-8 -*-
"""s02_report_face.py — 只读抽取 report.json 引擎面。"""
import json, sys
rep_path = sys.argv[1]
rep = json.load(open(rep_path, encoding="utf-8"))
def J(x, n=None):
    s = json.dumps(x, ensure_ascii=False, indent=1)
    return s if n is None else s[:n]
run = rep["run"]
print("===== run =====")
for k in ("question","ts_utc","git_head","git_head_source","git_diff_sha256","evidence_asof","degradation_policy","archive_requested"):
    print(k, "=", J(run.get(k)))
print("evidence_gate =", J(run.get("evidence_gate"), 2500))
print("frozen_inputs =", J(run.get("frozen_inputs"), 3000))
print("data_requirements =", J(run.get("data_requirements"), 6000))
rp = rep["research_plan"]
print("\n===== research_plan =====")
for k in ("map_question","question_verbatim","question_summary","dimension_source","asof_discipline","turning_supplement_discipline","cross_face_consistency","shared_by","regions","dimensions","metrics","context_metrics","point_anchors","question_window","ex_post_offsets","anchor_semantics_note","dimension_gaps","cutoff","consumed_time_spans","as_of_declared"):
    print(f"--- {k} =", J(rp.get(k), 5000))
print("\n--- point_values =", J(rp.get("point_values"), 14000))
print("\n--- turning_candidates =", J(rp.get("turning_candidates"), 8000))
print("\n--- us_rates_trio =", J(rp.get("us_rates_trio"), 4000))
print("\n--- asset_moves =", J(rp.get("asset_moves"), 8000))
print("\n--- policy_event_clusters =", J(rp.get("policy_event_clusters"), 5000))
print("\n--- policy_doc_facts =", J(rp.get("policy_doc_facts"), 3000))
print("\n===== semantic_review =====")
print(J(rep.get("semantic_review"), 1500))
aj = rep["agent_judgment"]
print("\n===== report.agent_judgment (meta) =====")
for k in ("attached","attached_at","judgment_file","schema_version","validation","run_ok_at_attach","allow_failed_run"):
    print(k, "=", J(aj.get(k), 2500))
print("reader_map_faces =", J(aj.get("reader_map_faces"), 2500))
print("\n===== contract_verification =====")
cv = aj["contract_verification"]
for k in ("version","verdict","stats","six_checks","map_checks","unresolved_unbound"):
    print(f"--- {k} =", J(cv.get(k), 9000))
print("--- verdicts (all) =", J(cv.get("verdicts"), 20000))
