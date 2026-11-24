# s10g3b_xreport.py <snap> <rep> <cal> <reg> <aj> <out> <map> <full> <report>  -- cross-report consistency (diag only)
import sys, re, json
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
c = Ctx(*sys.argv[1:7])
tx = {'MAP': open(sys.argv[7], encoding='utf-8').read(), 'FULL': open(sys.argv[8], encoding='utf-8').read(), 'REPORT': open(sys.argv[9], encoding='utf-8').read()}
aj = c.aj
keys = [('headline', aj['reader_map']['headline_conclusion'])]
def lng(d):
    return max((v for v in d.values() if isinstance(v, str)), key=len)
for i, x in enumerate(aj['l3']['contradictions']):
    keys.append(('C%d.statement' % (i + 1), x['statement']))
    for j, y in enumerate(x['competing_explanations']):
        keys.append(('C%d.ce%d' % (i + 1, j), y if isinstance(y, str) else lng(y)))
for j, l in enumerate(aj['l3']['mechanism_chains'][0]['links']):
    keys.append(('M1.%d.text' % j, l['text']))
for i, s in enumerate(aj['l4']['scenarios']):
    for k, v in s['rows'].items():
        if isinstance(v, str):
            keys.append(('S%d.%s' % (i + 1, k), v))
        elif isinstance(v, dict):
            for k2, v2 in v.items():
                if isinstance(v2, str):
                    keys.append(('S%d.%s.%s' % (i + 1, k, k2), v2))
for i, t in enumerate(aj['reader_map']['turnings']):
    for k in ('first_mover', 'follow_or_diverge', 'narrative'):
        keys.append(('T%d.%s' % (i, k), t[k]))
for i, t in enumerate(aj['reader_map']['transmission'][0]['links']):
    for k, v in t.items():
        if isinstance(v, str):
            keys.append(('TR%d.%s' % (i, k), v))
keys.append(('hist', aj['reader_map']['history_zero_case_note']))
for i, q in enumerate(aj['quality_gate_notes']):
    keys.append(('qgn%d' % i, q))
ajtok = set(m.group(0) for _, s in c.leaves for m in TOKRE.finditer(s))
for nm, t in tx.items():
    miss = [k for k, s in keys if s not in t]
    c.diag.append(nm + ': chars=' + str(len(t)) + ' lines=' + str(t.count(chr(10))) + ' | keys=' + str(len(keys)) + ' verbatim=' + str(len(keys) - len(miss)) + ' missing=' + json.dumps(miss))
    uniq = {}
    for m in TOKRE.finditer(t):
        g = m.group(0)
        if g not in ajtok and g not in uniq:
            uniq[g] = t[max(0, m.start() - 34): m.end() + 20].replace(chr(10), ' ')
    c.diag.append(nm + ': numeric tokens total=' + str(sum(1 for _ in TOKRE.finditer(t))) + ' distinct-not-in-AJ=' + str(len(uniq)))
    open(c.out + '_g3b_' + nm + '_diff.txt', 'w', encoding='utf-8').write(chr(10).join(k + ' :: ' + v for k, v in uniq.items()))
c.save('g3b')
