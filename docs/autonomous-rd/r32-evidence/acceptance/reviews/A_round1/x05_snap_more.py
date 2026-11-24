import json, sys
p = sys.argv[1]
d = json.load(open(p, encoding='utf-8'))
ss = d['series_store']
print('ALL SERIES KEYS:', sorted(ss.keys()))
print()
print('== timezone', d['timezone'], 'target_date', d['target_date'])
print('== sources_status')
print(json.dumps(d['sources_status'], ensure_ascii=False, indent=1)[:5000])
print('== series_store_notes')
print(json.dumps(d['series_store_notes'], ensure_ascii=False, indent=1)[:5000])
print('== series_provenance keys')
sp = d['series_provenance']
for k, v in sp.items():
    print(k, type(v).__name__, (len(v) if hasattr(v,'__len__') else v))
    if isinstance(v, dict):
        kk = list(v.keys())
        print('   keys:', kk[:100])
        if kk:
            print('   sample:', kk[0], json.dumps(v[kk[0]], ensure_ascii=False)[:1500])
print('== series_store_clean keys', list(d['series_store_clean'].keys()))
