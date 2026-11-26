#!/usr/bin/env python3
"""Seat script: extract engine deterministic faces from report.json into a readable dump.
Read-only on inputs. Usage:
  python3 -I extract_engine_face.py <report.json> <out.txt>
"""
import json
import sys


def dump(title, obj, limit_list=None):
    print(f"\n===== {title} =====")
    if limit_list is not None and isinstance(obj, list) and len(obj) > limit_list:
        obj = obj[:limit_list]
    print(json.dumps(obj, ensure_ascii=False, indent=1, default=str))


def main():
    rep_p, out_p = sys.argv[1], sys.argv[2]
    with open(rep_p, encoding="utf-8") as f:
        rep = json.load(f)
    orig = sys.stdout
    sys.stdout = open(out_p, "w", encoding="utf-8")
    try:
        run = rep["run"]
        dump("run.evidence_gate", run["evidence_gate"])
        dump("run.frozen_inputs", run["frozen_inputs"])
        dump("run.data_requirements", run["data_requirements"])
        dump("run.degradation_policy", run.get("degradation_policy"))
        rp = rep["research_plan"]
        for k in ["regions", "dimensions", "metrics", "context_metrics", "point_anchors",
                  "question_window", "ex_post_offsets", "dimension_gaps", "cutoff",
                  "as_of_declared", "point_values", "turning_candidates", "us_rates_trio",
                  "asset_moves", "policy_event_clusters", "policy_doc_facts"]:
            dump(f"research_plan.{k}", rp.get(k))
        dump("layers keys", list(rep["layers"].keys()))
        l1 = rep["layers"]["L1_事实层"]
        dump("L1 keys", list(l1.keys()))
        for k in l1:
            if k != "rows":
                v = l1[k]
                s = json.dumps(v, ensure_ascii=False)
                print(f"\nL1.{k} = {s[:2000]}")
        dump("L1.rows", l1["rows"])
        aj = rep["agent_judgment"]
        for k in aj:
            if k in ("contract_verification", "validation", "reader_map_faces"):
                dump(f"agent_judgment.{k}", aj[k])
            else:
                print(f"\nagent_judgment.{k} = {json.dumps(aj[k], ensure_ascii=False)[:500]}")
        dump("notes", rep["notes"])
        dump("evidence_index[0:3]", rep["evidence_index"][:3])
    finally:
        sys.stdout.close()
        sys.stdout = orig


if __name__ == "__main__":
    main()
