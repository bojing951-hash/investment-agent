# s26_probe.py <snap> <report> <aj>
import sys, json
snap = json.load(open(sys.argv[1], encoding='utf-8')); rep = json.load(open(sys.argv[2], encoding='utf-8')); aj = json.load(open(sys.argv[3], encoding='utf-8'))
S = snap['series_store']
ei = rep['evidence_index']
print(type(ei).__name__, len(ei))
rows = ei if isinstance(ei, list) else list(ei.values())
for r in rows[:2]: print('ROW', json.dumps(r, ensure_ascii=False)[:700])
kinds = {}
for r in rows: kinds[r.get('kind')] = kinds.get(r.get('kind'), 0) + 1
print('kinds', kinds)
s3 = [r for r in rows if r.get('kind') == 's3_envelope'][:1]
print('S3ROW', json.dumps(s3, ensure_ascii=False)[:900])
ly = rep.get('layers')
print('layers type', type(ly).__name__, (list(ly.keys()) if isinstance(ly, dict) else len(ly)))
if isinstance(ly, dict):
    for k, v in ly.items():
        print('  layer', k, type(v).__name__, (list(v.keys())[:12] if isinstance(v, dict) else len(v)))
