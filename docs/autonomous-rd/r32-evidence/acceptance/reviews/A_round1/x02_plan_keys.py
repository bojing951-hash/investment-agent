import json, sys
p = sys.argv[1]
d = json.load(open(p, encoding='utf-8'))
rp = d['research_plan']
for k in ['regions','dimensions','metrics','context_metrics','point_anchors','ex_post_offsets','dimension_gaps','cutoff','consumed_time_spans','as_of_declared']:
    print('==', k)
    print(json.dumps(rp[k], ensure_ascii=False, indent=1)[:6000])
print('== point_values keys')
print(list(rp['point_values'].keys()))
for k,v in rp['point_values'].items():
    print('---', k, type(v).__name__, len(v) if hasattr(v,'__len__') else v)
    if isinstance(v, list) and v:
        print(json.dumps(v[0], ensure_ascii=False)[:1500])
    elif isinstance(v, dict):
        kk = list(v.keys())
        print(kk[:40])
print('== turning_candidates keys')
print(json.dumps({k:(type(v).__name__, len(v) if hasattr(v,'__len__') else v) for k,v in rp['turning_candidates'].items()}, ensure_ascii=False))
print('== us_rates_trio keys')
print(json.dumps({k:(type(v).__name__, len(v) if hasattr(v,'__len__') else v) for k,v in rp['us_rates_trio'].items()}, ensure_ascii=False))
print('== asset_moves keys')
print(json.dumps({k:(type(v).__name__, len(v) if hasattr(v,'__len__') else v) for k,v in rp['asset_moves'].items()}, ensure_ascii=False))
print('== policy_event_clusters keys')
print(json.dumps({k:(type(v).__name__, len(v) if hasattr(v,'__len__') else v) for k,v in rp['policy_event_clusters'].items()}, ensure_ascii=False))
print('== policy_doc_facts')
print(json.dumps(rp['policy_doc_facts'], ensure_ascii=False)[:3000])
