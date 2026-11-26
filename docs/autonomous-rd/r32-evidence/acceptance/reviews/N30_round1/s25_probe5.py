# s25_probe5.py <aj>
import sys, json, re
aj = json.load(open(sys.argv[1], encoding='utf-8'))
L = []
def walk(o, p):
    if isinstance(o, dict):
        for k, v in o.items(): walk(v, p + '.' + k if p else k)
    elif isinstance(o, list):
        for i, v in enumerate(o): walk(v, p + '[' + str(i) + ']')
    elif isinstance(o, str): L.append((p, o))
walk(aj, '')
def sents(p):
    for path, s in L:
        if path == p:
            return re.split('(?<=[。;；])', s)
    return []
def show(p, kws, lim=420):
    for x in sents(p):
        if any(k in x for k in kws):
            print('[' + p + ']', x[:lim])
show('l3.contradictions[0].statement', ['东京'], 700)
show('l3.contradictions[2].statement', ['欧央行', '东京'], 520)
for path, s in L:
    if path.startswith('reader_map.turnings') and path.endswith('narrative'):
        print('[' + path + ']', s[:620])
    if path.startswith('reader_map.regions') and '2025-01' in s:
        i = s.find('2025-01'); print('[' + path + ']', s[max(0, i - 40): i + 150])
    if path.startswith('reader_map.asset_returns_echo') and '东京' in s:
        i = s.find('东京'); print('[' + path + ']', s[max(0, i - 60): i + 110])
    if 'confidence_tier' in path: print('[' + path + ']', s)
    if path.startswith('quality_gate_notes'):
        if '五行' in s: i = s.find('五行'); print('[' + path + ']', s[max(0, i - 70): i + 60])
        if '21' in s: i = s.find('21'); print('[' + path + ']', s[max(0, i - 90): i + 60])
    if path == 'reader_map.headline_conclusion':
        for k in ('六十八', '东京'):
            i = s.find(k)
            if i >= 0: print('[' + path + ']', s[max(0, i - 50): i + 60])
print('region keys', [k for k in aj['reader_map']['regions'][1].keys()])
print('echo keys', [k for k in aj['reader_map']['asset_returns_echo'][0].keys()])
print('nleaves', len(L), 'walk paths sample', [p for p, s in L if p.startswith('reader_map.transmission[0].links[0]')])
