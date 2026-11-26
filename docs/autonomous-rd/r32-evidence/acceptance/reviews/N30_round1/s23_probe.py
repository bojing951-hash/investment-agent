# s23_probe.py <snap> <rep> <cal> <reg> <aj>
import sys
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
c = Ctx(*sys.argv[1:6], '/tmp/r32-accept/review6/N30_round1/s10_probe2')
RP = c.rep['research_plan']
def find(o, s, path=''):
    out = []
    if isinstance(o, dict):
        for k, v in o.items():
            out += find(v, s, path + '.' + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            out += find(v, s, path + '[' + str(i) + ']')
    elif isinstance(o, str):
        if s in o:
            out.append((path, o[:90]))
    return out
for s in ['2026-06-26', '2025-11-23', '最后', 'last_friday', 'last Friday']:
    r = find(c.reg, s)
    print('REG has', s, len(r))
    for x in r[:6]:
        print('    ', x)
for s in ['2026-06-26', '2025-11-23', '12m', 'months', 'freshness']:
    r = find(RP, s)
    print('RP has', s, len(r))
    for x in r[:8]:
        print('    ', x)
print('REG ECB_MRO keys', sorted(c.RM['ECB_MRO'].keys()))
print('REG ECB_MRO freshness', c.RM['ECB_MRO'].get('freshness'), '| release_semantics', str(c.RM['ECB_MRO'].get('release_semantics'))[:300])
print('REG ECB_DFR freshness', c.RM['ECB_DFR'].get('freshness'))
infl = [(m, r.get('economy'), r.get('family'), r.get('dimension')) for m, r in c.RM.items() if r.get('economy') in ('JP', 'EA') and re.search('CPI|HICP|INFL|CORE', m)]
print('REG JP/EA inflation-like', infl)
print('REG JP/EA all ids', sorted(m for m, r in c.RM.items() if r.get('economy') in ('JP', 'EA')))
print('Facts JGB', [(f.get('metric_id'), f.get('observation_date'), f.get('value'), f.get('quality_status')) for f in c.F if 'JGB' in str(f.get('metric_id'))])
print('Facts BUND', [(f.get('metric_id'), f.get('observation_date')) for f in c.F if 'BUND' in str(f.get('metric_id'))])
for f in c.F[0:1]:
    print('Fact keys', sorted(f.keys()))
cal = c.cal
print('CAL keys', sorted(cal.keys()))
for e in cal['entries']:
    if 'HICP' in str(e.get('metric_id')) or 'HICP' in str(e.get('series_id')):
        print('CAL EA', {k: e.get(k) for k in e if k not in ('note', 'notes', 'source_note')})
st = c.rep['steps']
for s_ in st:
    env = s_.get('envelope') or {}
    if 'S6' in str(s_.get('name', '')) or 'S6' in str(env.get('step', '')) or 'analog' in str(s_.get('name', '')).lower():
        d = env.get('data') or {}
        print('S6 step name', s_.get('name'), 'env keys', sorted(env.keys())[:12])
        print('S6 data keys', sorted(d.keys()) if isinstance(d, dict) else type(d))
        cd = d.get('candidates') if isinstance(d, dict) else None
        if isinstance(cd, dict):
            print('S6 candidates keys', sorted(cd.keys()))
            for k, v in cd.items():
                print('     ', k, str(v)[:200])
        for k, v in (d.items() if isinstance(d, dict) else []):
            if k != 'candidates':
                print('   S6', k, str(v)[:220])
qw = RP['question_window']
print('QW keys', sorted(qw.keys()))
for w in qw['windows']:
    print('QW window', w)
