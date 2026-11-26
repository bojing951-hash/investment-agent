# -*- coding: utf-8 -*-
"""只读: 数据需求逐项 outcome。用法: python3 -I s09b_dr_items.py <work_dir_with_run_data_requirements.json>"""
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    dr = json.load(f)
for it in dr['items']:
    sp = it.get('spec', {})
    print(it['metric_id'], "| tier", it.get('tier'), "| outcome", json.dumps(it.get('outcome'), ensure_ascii=False)[:300], "| outcome_basis", json.dumps(it.get('outcome_basis'), ensure_ascii=False)[:400])
    print("     basis:", it.get('basis'))
    print("     spec keys:", list(sp.keys()), "| frequency", sp.get('frequency'), "| min_cov", sp.get('min_coverage'))
