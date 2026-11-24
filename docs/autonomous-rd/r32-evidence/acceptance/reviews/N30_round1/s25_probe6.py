# s25_probe6.py <aj> <MAP> <FULL>
import sys, json
aj = json.load(open(sys.argv[1], encoding='utf-8'))
t2 = aj['reader_map']['turnings'][2]
for k, v in t2.items():
    print('T2.' + k, '=>', json.dumps(v, ensure_ascii=False)[:520])
r1 = aj['reader_map']['regions'][1]
print('R1.from_to len', len(r1['from_to']))
i = r1['from_to'].find('东京都 CPI'); print('R1.from_to tail', r1['from_to'][i:i + 330])
print('R1.anchor_echo', json.dumps(r1['anchor_echo'], ensure_ascii=False)[:700])
ts = aj['reader_map'].get('turning_supplement')
print('turning_supplement', json.dumps(ts, ensure_ascii=False)[:600])
mp = open(sys.argv[2], encoding='utf-8').read().split(chr(10))
for n, l in enumerate(mp, 1):
    if ('东京' in l and ('Gate' in l or 'noncore' in l or '事实行' in l or '序列面' in l)) or 'noncore_missing' in l:
        print('MAP L' + str(n), l.strip()[:330])
fl = open(sys.argv[3], encoding='utf-8').read().split(chr(10))
for n, l in enumerate(fl, 1):
    if 'noncore_missing' in l or ('东京' in l and ('序列面' in l or '事实行' in l)):
        print('FULL L' + str(n), l.strip()[:260])
