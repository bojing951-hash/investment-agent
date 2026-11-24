# s10_probe.py <cal> <reg> <snap>
import sys, json
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
cal = load(sys.argv[1]); reg = load(sys.argv[2]); snap = load(sys.argv[3])
print('CAL keys', list(cal.keys()))
for k in cal:
    if k != 'entries' and k != 'batches':
        print(' ', k, '=', json.dumps(cal[k], ensure_ascii=False)[:300])
print('n entries', len(cal['entries']), 'n batches', len(cal.get('batches', [])))
for e in cal['entries']:
    s = json.dumps(e, ensure_ascii=False)
    if any(x in s for x in ['JP', 'EA_', 'ECB', 'HICP', 'CPI', 'BOJ']):
        print(' ENT', s[:700])
print('REG type', type(reg).__name__, (list(reg.keys()) if isinstance(reg, dict) else len(reg)))
rl = reg.get('metrics') if isinstance(reg, dict) else reg
for r in rl:
    if r.get('metric_id') in ['EA_HICP_YOY', 'JP_CPI_YOY', 'JP_CPI_TOKYO_YOY', 'JP_POLICY_RATE', 'ECB_MRO', 'ECB_DFR', 'EA_REAL_GDP_YOY', 'BUND_10Y', 'BUND_2Y']:
        print(' REG', json.dumps(r, ensure_ascii=False)[:1500])
print('economies', sorted(set(str(r.get('economy')) for r in rl)))
for eco in ['JP', 'EA']:
    print(eco, [r.get('metric_id') for r in rl if r.get('economy') == eco])
print('SNAP top keys', list(snap.keys()))
print('research_as_of', snap.get('research_as_of'), 'target_date', snap.get('target_date'))
print('GATE_A', json.dumps(snap.get('gate_a'), ensure_ascii=False)[:3000])
f = [x for x in snap['facts'] if x.get('metric_id') in ('ECB_DFR', 'JP_CPI_TOKYO_YOY')]
print('FACT sample', json.dumps(f, ensure_ascii=False)[:1500])
print('ids in facts', sorted(set(x.get('metric_id') for x in snap['facts'])))
print('SS JP_POLICY_TARGET' , 'JP_POLICY_TARGET' in snap['series_store'])
print('py', sys.version)
