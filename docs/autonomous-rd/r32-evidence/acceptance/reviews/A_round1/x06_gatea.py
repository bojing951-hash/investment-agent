import json, sys
p = sys.argv[1]
d = json.load(open(p, encoding='utf-8'))
print('== gate_a')
ga = d['gate_a']
for k, v in ga.items():
    if isinstance(v, (dict, list)) and len(json.dumps(v)) > 1500:
        print(f'-- {k}: {type(v).__name__} len={len(v)}')
        if isinstance(v, list):
            for it in v:
                print('    ', json.dumps(it, ensure_ascii=False)[:400])
        else:
            print('    ', json.dumps(v, ensure_ascii=False)[:3000])
    else:
        print(f'-- {k}:', json.dumps(v, ensure_ascii=False))
print('== quality')
print(json.dumps(d['quality'], ensure_ascii=False, indent=1)[:6000])
print('== notes')
print(json.dumps(d['notes'], ensure_ascii=False, indent=1)[:3000])
print('== reconciliation')
print(json.dumps(d['reconciliation'], ensure_ascii=False, indent=1)[:3000])
print('== facts sample (first 5)')
for f in d['facts'][:5]:
    print(json.dumps(f, ensure_ascii=False)[:800])
print('facts keys union:', sorted({k for f in d['facts'] for k in f.keys()}))
