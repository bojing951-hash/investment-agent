# s21_closure.py <snap> <rep> <cal> <reg> <aj> <out_prefix>  -- closure: distinct dates vs verified date set; unanchored value tokens
import sys
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
snap, rep, cal, reg, aj, pre = sys.argv[1:7]
c = Ctx(snap, rep, cal, reg, aj, pre + '_x')
RP = c.rep['research_plan']; A = c.asof
EA = 'EA_HICP_YOY'; JP = 'JP_CPI_YOY'; TK = 'JP_CPI_TOKYO_YOY'; PR = 'JP_POLICY_RATE'
pts = load(pre + '_all.json')['points']
cc = {}
for tg in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'g2a', 'g2b', 'g3a']:
    for x in load(pre + '_' + tg + '.json')['cover']:
        cc.setdefault(x[0], set()).update(range(x[1], x[2]))
VD = set()
VD.add(A); VD.add(RP['question_window']['windows'][0]['from'])
for m in [EA, JP, TK, PR]:
    for d in c.S[m]['dates']:
        if '2024-01' <= d[:7] <= '2026-12':
            VD.add(d); VD.add(c.pub(m, d[:7]))
for x in c.cal['entries']:
    for k in ('decision_date', 'effective_on', 'first_publish_on_or_after', 'final_publish_on', 'obs_from', 'obs_to'):
        if isinstance(x.get(k), str):
            VD.add(x[k])
for m in ['ECB_MRO', 'ECB_DFR', 'JP_POLICY_RATE', 'DFEDTARU', 'DFEDTARL']:
    for d, a_, b_ in c.changes(m):
        VD.add(d)
VD.add(plus(c.last('ECB_MRO')[0], 1))
for m in ['SPX', 'VIX', 'NIKKEI225', 'DAX', 'CAC40', 'EURUSD', 'USDJPY', 'DXY', 'UST_10Y', 'TIPS_10Y', 'BEI_10Y']:
    for d in c.S[m]['dates']:
        if '2026-10-20' <= d <= A:
            VD.add(d)
UT = RP['us_rates_trio']
VD.add(UT['window']['from']); VD.add(UT['window']['to']); VD.add(UT['window_12m']['from']); VD.add(UT['window_12m']['to'])
for r in RP['asset_moves']['rows']:
    VD.add(r['window']['from']); VD.add(r['window']['to'])
for f in RP['policy_doc_facts']:
    for k in ('published_on', 'decision_date', 'effective_on', 'observation_date', 'as_of'):
        if isinstance(f.get(k), str):
            VD.add(f[k])
for ym in ['2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08', '2026-09', '2026-10']:
    d = D(mend(ym))
    while d.weekday() != 4:
        d -= dt.timedelta(days=1)
    VD.add(d.isoformat())
DATE = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')
YM = re.compile('[0-9]{4}-[0-9]{2}(?![0-9-])')
found = {}
for path, s in c.leaves:
    for mt in DATE.finditer(s):
        found.setdefault(mt.group(0), []).append(path)
    for mt in YM.finditer(s):
        found.setdefault(mt.group(0) + '(月)', []).append(path)
unk = {k: v for k, v in found.items() if k.replace('(月)', '') not in VD}
print('distinct 日期/月 in AJ:', len(found), '| 不在已核日期集合:', len(unk))
for k in sorted(unk):
    print('   NOT-IN-SET', k, sorted(set(x.split('[')[0] for x in unk[k]))[:5])
print('verified date set size', len(VD))
# value echo
def pv(t):
    try:
        return round(pnum(t), 6)
    except Exception:
        return None
VALS = set()
for p in pts:
    if not p['ok']:
        continue
    v = pv(p['tok']) if p['tok'] else None
    if v is not None:
        VALS.add(v)
    if isinstance(p['rep'], (int, float)) and not isinstance(p['rep'], bool):
        VALS.add(round(float(p['rep']), 6))
SKIP = ('.id', 'evidence_refs', 'evidence_level', 'schema_version', 'agent_declaration', 'metric_id', 'observation_month', 'anchor', '.region', 'chain_id', '.title', 'sensitive_variables', 'secondary_metric_ids', '.kind', 'window.from', 'window.to', 'window_from', 'window_to')
rows = []; uniq = []
for i, (path, s) in enumerate(c.leaves):
    if any(k in path for k in SKIP):
        continue
    for mt in TOKRE.finditer(s):
        t = mt.group(0)
        if any(k in cc.get(i, ()) for k in range(mt.start(), mt.end())):
            continue
        if DATE.match(t) or YM.match(t) or re.match('[0-9]{4}$', t):
            continue
        v = pv(t)
        ctx = s[max(0, mt.start() - 14): mt.end() + 10].replace(chr(10), ' ')
        rows.append((path, t, ctx))
        if v is None or v not in VALS:
            uniq.append((path, t, ctx))
print('unanchored non-date tokens (excl. ids/refs/declaration):', len(rows), '| 其值从未被任一已核点覆盖:', len(uniq))
for x in uniq:
    print('   UNIQUE', x)
with open(pre + '_echo.txt', 'w', encoding='utf-8') as f:
    for x in rows:
        f.write(x[0] + ' | ' + x[1] + ' | ' + x[2] + chr(10))
print('verified value set size', len(VALS))
