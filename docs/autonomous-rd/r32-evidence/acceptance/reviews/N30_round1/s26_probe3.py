# s26_probe3.py <aj> <all_json> <report> <snap>
import sys, json
aj = json.load(open(sys.argv[1], encoding='utf-8')); allp = json.load(open(sys.argv[2], encoding='utf-8'))
rep = json.load(open(sys.argv[3], encoding='utf-8')); snap = json.load(open(sys.argv[4], encoding='utf-8'))
NUM = []
def walk(o, p):
    if isinstance(o, dict):
        for k, v in o.items(): walk(v, p + '.' + k if p else k)
    elif isinstance(o, list):
        for i, v in enumerate(o): walk(v, p + '[' + str(i) + ']')
    elif isinstance(o, (int, float)) and not isinstance(o, bool): NUM.append((p, o))
    elif isinstance(o, bool): NUM.append((p + ' (bool)', o))
walk(aj, '')
print('numeric/bool leaves', len(NUM))
srcs = ' '.join(str(p['src']) for p in allp['points'])
import collections
kinds = collections.Counter()
for p, v in NUM:
    key = '.'.join(x.split('[')[0] for x in p.replace(' (bool)', '').split('.')[-3:])
    kinds[(key, str(p['src']) if False else '')] += 1
for k, n in sorted(kinds.items()): print('  ', n, k[0], '| in src text:', sum(1 for s in srcs.split(' ') if k[0].split('.')[-1] in s))
for p, v in NUM:
    if 'anchor_echo' in p or 'asset_returns_echo' in p or 'turnings' in p or 'rates_decomposition' in p or 'bool' in p:
        pass
others = [(p, v) for p, v in NUM if not ('anchor_echo' in p or 'asset_returns_echo' in p or 'turnings[' in p or 'rates_decomposition' in p)]
print('others n', len(others))
for p, v in others[:60]: print('   O', p, '=', v)
print('asset_returns_echo', json.dumps(aj['reader_map']['asset_returns_echo'], ensure_ascii=False)[:900])
for t in aj['reader_map']['turnings']:
    print('turning', t.get('date'), t.get('metric_id'), t.get('before_date'), t.get('value_before'), t.get('value_after'), [k for k in t if k not in ('date', 'metric_id', 'before_date', 'value_before', 'value_after', 'first_mover', 'follow_or_diverge', 'narrative')])
