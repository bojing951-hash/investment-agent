# s10h_index.py <snap> <rep> <cal> <reg> <aj> <out> -- evidence_index rows: every ref resolves on the read-only face
import sys, json
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
c = Ctx(*sys.argv[1:7])
ei = c.rep['evidence_index']
st = c.rep.get('steps')
c.diag.append('steps type ' + type(st).__name__ + ' n ' + str(len(st)))
names = []
for s in (st if isinstance(st, list) else []):
    names.append(str(s.get('name') or s.get('step') or s.get('id')))
c.diag.append('step names ' + json.dumps(names, ensure_ascii=False)[:600])
s3 = [s for s in (st if isinstance(st, list) else []) if 'S3' in json.dumps(s, ensure_ascii=False)[:400]]
c.diag.append('S3 candidates ' + str(len(s3)))
s3txt = ' '.join(json.dumps(s, ensure_ascii=False) for s in s3)
L1 = json.dumps(c.rep['layers'].get('L1_事实层'), ensure_ascii=False)
nf = 0; ne = 0
for r in ei:
    ref = str(r.get('ref')); m = r.get('metric_id'); kind = r.get('kind')
    d = ref.split('@')[1] if '@' in ref else ''
    if kind == 'snapshot_fact':
        ok = (m in c.S) and (d in c.S[m]['dates']) and (c.at(m, d) is not None)
        c.ok('G', 'evidence_index ' + ref + ' -> series_store 该日有值', ok, (m, d, c.at(m, d) if (m in c.S and d in c.S[m]['dates']) else None))
        nf += 1
    elif kind == 's3_envelope':
        ok = (m in s3txt) or (m in L1)
        c.ok('G', 'evidence_index ' + ref + ' (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场', ok, m)
        ne += 1
c.diag.append('index rows fact=' + str(nf) + ' s3=' + str(ne))
c.save('h')
