# -*- coding: utf-8 -*-
"""只读: 抽取 report.json 引擎面到本席 work 目录并打印。
用法: python3 -I s07_engine_face.py <report_json> <out_dir>"""
import json, sys, os
p = sys.argv[1]; out = sys.argv[2]
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
os.makedirs(out, exist_ok=True)
def dump(name, obj, maxlen=None):
    s = json.dumps(obj, ensure_ascii=False, indent=1)
    with open(os.path.join(out, name), 'w', encoding='utf-8') as f:
        f.write(s)
    return s
rp = d['research_plan']
print("### run (scalar + small)")
r = d['run']
for k in ['question','ts_utc','archive_requested','git_head','git_head_source','git_diff_sha256','evidence_asof']:
    print("  ", k, "=", repr(r.get(k)))
print("  evidence_gate =", json.dumps(r.get('evidence_gate'), ensure_ascii=False)[:3000])
print("  degradation_policy =", json.dumps(r.get('degradation_policy'), ensure_ascii=False)[:1500])
print("  frozen_inputs =", json.dumps(r.get('frozen_inputs'), ensure_ascii=False))
dr = r.get('data_requirements')
print("  data_requirements type", type(dr).__name__, (list(dr.keys()) if isinstance(dr, dict) else len(dr)))
dump('run_data_requirements.json', dr)
print("\n### research_plan small fields")
for k in ['map_question','question_verbatim','question_summary','dimension_source','asof_discipline','turning_supplement_discipline','cross_face_consistency','shared_by','regions','dimensions','metrics','context_metrics','point_anchors','question_window','ex_post_offsets','anchor_semantics_note','dimension_gaps','cutoff','consumed_time_spans','as_of_declared','policy_event_clusters','policy_doc_facts']:
    print("  ", k, "=", json.dumps(rp.get(k), ensure_ascii=False))
print("\n### point_values.cells")
pv = rp['point_values']
for c in pv.get('cells', []):
    print("  ", json.dumps(c, ensure_ascii=False))
print("  absent =", json.dumps(pv.get('absent'), ensure_ascii=False))
print("\n### turning_candidates")
print(json.dumps(rp.get('turning_candidates'), ensure_ascii=False, indent=1))
print("\n### us_rates_trio")
print(json.dumps(rp.get('us_rates_trio'), ensure_ascii=False, indent=1))
print("\n### asset_moves")
print(json.dumps(rp.get('asset_moves'), ensure_ascii=False, indent=1))
print("\n### agent_judgment (engine part)")
aj = d['agent_judgment']
for k in ['attached','attached_at','judgment_file','schema_version','run_ok_at_attach','allow_failed_run','reader_map_faces']:
    print("  ", k, "=", json.dumps(aj.get(k), ensure_ascii=False)[:1500])
print("  validation =", json.dumps(aj.get('validation'), ensure_ascii=False)[:4000])
cv = aj.get('contract_verification')
dump('contract_verification.json', cv)
print("  contract_verification bytes", len(json.dumps(cv, ensure_ascii=False)))
print(json.dumps(cv, ensure_ascii=False, indent=1)[:12000])
print("\n### semantic_review")
print(json.dumps(d.get('semantic_review'), ensure_ascii=False, indent=1))
print("\n### notes", json.dumps(d.get('notes'), ensure_ascii=False))
print("### fanout", json.dumps(d.get('fanout'), ensure_ascii=False))
print("### run_ok", d.get('run_ok'), "schema", d.get('schema_version'), "pipeline", d.get('pipeline_version'))
