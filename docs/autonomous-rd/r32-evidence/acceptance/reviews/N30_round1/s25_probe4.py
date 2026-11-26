# s25_probe4.py <snap> <report> <aj>
import sys, json, hashlib
snap = json.load(open(sys.argv[1], encoding='utf-8')); rep = json.load(open(sys.argv[2], encoding='utf-8'))
ga = snap['gate_a']
print('gate_a.status', ga.get('status'))
print('gate_a.note', str(ga.get('note'))[:700])
det = ga.get('noncore_missing_detail')
print('detail type', type(det).__name__)
if isinstance(det, dict):
    for k in ('JP_CPI_TOKYO_YOY', 'EA_REAL_GDP_YOY', 'JP_REAL_GDP_YOY', 'BUND_10Y'):
        print('  ', k, '=>', json.dumps(det.get(k), ensure_ascii=False)[:420])
elif isinstance(det, list):
    for x in det:
        if 'TOKYO' in json.dumps(x, ensure_ascii=False) or 'GDP' in json.dumps(x, ensure_ascii=False):
            print('  ', json.dumps(x, ensure_ascii=False)[:420])
print('research_as_of', snap.get('research_as_of'), 'target', snap.get('target_date'), 'tz', snap.get('timezone'), 'sid', snap.get('snapshot_id'))
for k in ('core_fail', 'core_missing', 'illegal_quality', 'noncore_fail'):
    print(k, json.dumps(ga.get(k), ensure_ascii=False)[:200])
h = hashlib.sha256(open(sys.argv[3], 'rb').read()).hexdigest()
print('aj sha256', h)
rd = rep.get('research_plan', {})
print('rp keys', sorted(rd.keys())[:30])
for it in rd.get('point_values', {}).get('cells', [])[:0]:
    pass
pv = rd.get('point_values', {})
print('pv keys', sorted(pv.keys()))
for c in pv.get('cells', []):
    if c.get('metric_id') in ('JP_CPI_TOKYO_YOY', 'ECB_MRO', 'ECB_DFR', 'JP_CPI_YOY'):
        print('  cell', json.dumps(c, ensure_ascii=False)[:330])
for it in rd.get('data_requirements', {}).get('items', []):
    if it.get('metric_id') in ('JP_CPI_TOKYO_YOY', 'ECB_MRO'):
        print('  dr', json.dumps(it, ensure_ascii=False)[:420])
print('report keys', sorted(rep.keys()))
print('notes', json.dumps(rep.get('notes'), ensure_ascii=False)[:300])
sr = rep.get('semantic_review')
print('semantic_review', json.dumps(sr, ensure_ascii=False)[:300])
