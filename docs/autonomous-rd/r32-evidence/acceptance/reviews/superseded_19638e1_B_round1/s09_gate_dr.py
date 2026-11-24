# -*- coding: utf-8 -*-
"""只读: 快照 gate_a / quality / data_requirements。用法: python3 -I s09_gate_dr.py <snapshot> <work_dir>"""
import json, sys, os
snap_p, work = sys.argv[1], sys.argv[2]
with open(snap_p, 'r', encoding='utf-8') as f:
    snap = json.load(f)
print("### snapshot.gate_a")
print(json.dumps(snap['gate_a'], ensure_ascii=False, indent=1))
print("### snapshot.quality")
print(json.dumps(snap['quality'], ensure_ascii=False, indent=1))
print("### snapshot.notes")
print(json.dumps(snap['notes'], ensure_ascii=False, indent=1))
print("### snapshot.reconciliation")
print(json.dumps(snap['reconciliation'], ensure_ascii=False, indent=1)[:4000])
with open(os.path.join(work, 'run_data_requirements.json'), 'r', encoding='utf-8') as f:
    dr = json.load(f)
print("### run.data_requirements frozen_at", dr.get('frozen_at'))
items = dr.get('items')
print("items type", type(items).__name__, "n", len(items))
it0 = items[0] if isinstance(items, list) else list(items.values())[0]
print("item keys", list(it0.keys()))
for it in (items if isinstance(items, list) else items.values()):
    print("  ", json.dumps({k: it.get(k) for k in it if k not in ('gap_detail','note','detail')}, ensure_ascii=False)[:700])
print("optional_face:", json.dumps(dr.get('optional_face'), ensure_ascii=False)[:1500])
