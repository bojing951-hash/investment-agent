import sys
sys.path.insert(0, sys.argv[0].rsplit("/", 1)[0])
from rc_common import *
snap, rep, cal, reg, aj, out = sys.argv[1:7]
c = Ctx(snap, rep, cal, reg, aj, out)
RP = c.rep['research_plan']
def ctx(s, key, k=70):
    p = s.find(key)
    return s[max(0, p - k): p + len(key) + k].replace(chr(10), ' ') if p >= 0 else None
print('== AJ leaves containing 4.03 / 1.42 / 2026-02→ ==')
for path, s in c.leaves:
    for key in ['4.03', '1.42', '2026-02→2026-05', '2026-02→05', '2026-01→2026-04']:
        x = ctx(s, key)
        if x:
            print(path, '|', key, '|', x)
print('== EA / JP series 2025-10..2026-10 ==')
for m in ['EA_HICP_YOY', 'JP_CPI_YOY']:
    print(m, [(d, v) for d, v in zip(c.S[m]['dates'], c.S[m]['values']) if '2025-10' <= d <= '2026-10'])
print('== 3-month rolling changes (unrounded) ==')
for m in ['EA_HICP_YOY', 'JP_CPI_YOY']:
    ds = [d for d in c.S[m]['dates'] if d <= c.asof]
    r = []
    for i in range(3, len(ds)):
        a, b = ds[i - 3], ds[i]
        r.append((round(c.at(m, b) - c.at(m, a), 4), a, b, c.at(m, a), c.at(m, b)))
    r.sort(key=lambda x: -abs(x[0]))
    print(m, 'top5', r[:5])
print('== engine turning_candidates ==')
print(json.dumps(RP['turning_candidates'], ensure_ascii=False)[:2600])
print('== VIX tail ==', [(d, v) for d, v in zip(c.S['VIX']['dates'], c.S['VIX']['values'])][-8:])
