# s24_probe2.py <snap> <rep> <aj> <map_report>
import sys, json
snap = json.load(open(sys.argv[1], encoding='utf-8'))
rep = json.load(open(sys.argv[2], encoding='utf-8'))
aj = json.load(open(sys.argv[3], encoding='utf-8'))
mp = open(sys.argv[4], encoding='utf-8').read().split('\n')
S = snap['series_store'] if 'series_store' in snap else snap.get('series', snap)
def get(m):
    s = S[m]
    return s
out = []
for m in ('EA_HICP_YOY', 'JP_CPI_YOY', 'JP_CPI_TOKYO_YOY', 'JP_POLICY_RATE', 'ECB_MRO', 'ECB_DFR'):
    s = get(m)
    ds = s['dates']; vs = s['values']
    out.append(m + ' first=' + str(ds[0]) + ' n=' + str(len(ds)) + ' last=' + str(ds[-1]))
    row = []
    for d, v in zip(ds, vs):
        if d >= '2025-10-01':
            row.append(d[:10] + '=' + str(v))
    out.append('   ' + ' '.join(row))
L0 = aj['reader_map']['transmission'][0]['links'][0]
out.append('LINK0 verdict_note: ' + L0['verdict_note'])
out.append('LINK0 main_predicts: ' + L0['main_predicts'])
out.append('LINK0 competing: ' + L0['competing_predicts'])
out.append('----- MAP lines 104-152')
for i in range(103, min(152, len(mp))):
    if mp[i].strip():
        out.append('L%d: %s' % (i + 1, mp[i][:420]))
ei = rep['evidence_index']
out.append('evidence_index n=%d keys=%s' % (len(ei), sorted(ei[0].keys())))
out.append('sample: ' + json.dumps(ei[:3], ensure_ascii=False))
out.append('kinds: ' + json.dumps(sorted(set(str(x.get('kind')) for x in ei)), ensure_ascii=False))
dr = rep['run']['data_requirements']
out.append('data_requirements: ' + json.dumps(dr, ensure_ascii=False)[:1500])
out.append('report.notes: ' + json.dumps(rep.get('notes'), ensure_ascii=False)[:1500])
open(sys.argv[5], 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('written', len(out))
