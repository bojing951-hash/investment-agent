#!/usr/bin/env python3
"""Seat-owned read-only extractor for a few research_plan discipline fields and step notes.
Usage: python3 -I extract_misc2.py <report.json>
"""
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as fh:
    rep = json.load(fh)
rp = rep["research_plan"]
for k in ("anchor_semantics_note", "asof_discipline", "turning_supplement_discipline", "cross_face_consistency",
          "question_summary", "map_question", "consumed_time_spans", "dimension_source", "ex_post_offsets", "regions", "metrics", "context_metrics"):
    print("== research_plan.%s" % k)
    print(json.dumps(rp.get(k), ensure_ascii=False, indent=1)[:3000])
print("== point_values.policy_face / absent / asset_universe")
print(json.dumps({k: v for k, v in rp["point_values"].items() if k != "cells"}, ensure_ascii=False, indent=1)[:4000])
print("== policy_event_clusters / policy_doc_facts / dimension_gaps / point_anchors")
for k in ("policy_event_clusters", "policy_doc_facts", "dimension_gaps", "point_anchors"):
    print("-- %s" % k)
    print(json.dumps(rp.get(k), ensure_ascii=False, indent=1)[:2500])
print("== steps notes (agent_face_note / note / gate) for S6, S7, S8, S10, S11, S1, S2")
for s in rep["steps"]:
    if s["step"] in ("S1_decompose", "S2_doctor", "S6_analog", "S7_mode_gate", "S8_grounded_qa", "S9_views_lint", "S10_selfcheck", "S11_archive", "S3_overview_JP"):
        print("--", s["step"], "executed=%s ok=%s semantic_ok=%s exit=%s gate=%s dur=%s" % (s["executed"], s["ok"], s.get("semantic_ok"), s.get("exit_code"), s.get("gate"), s.get("duration_ms")))
        print("   argv=%s" % (s.get("argv"),))
        print("   agent_face_note=%s" % (s.get("agent_face_note"),))
        print("   note=%s" % (s.get("note"),))
        print("   deterministic_face=%s" % (json.dumps(s.get("deterministic_face"), ensure_ascii=False)[:600],))
