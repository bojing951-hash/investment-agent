# s26_probe2.py <snap> <report> <cal> <aj>
import sys, json, re
snap = json.load(open(sys.argv[1], encoding='utf-8')); rep = json.load(open(sys.argv[2], encoding='utf-8'))
cal = json.load(open(sys.argv[3], encoding='utf-8')); aj = json.load(open(sys.argv[4], encoding='utf-8'))
S = snap['series_store']; L = []
def walk(o, p):
    if isinstance(o, dict):
        for k, v in o.items(): walk(v, p + '.' + k if p else k)
    elif isinstance(o, list):
        for i, v in enumerate(o): walk(v, p + '[' + str(i) + ']')
    elif isinstance(o, str): L.append((p, o))
walk(aj, '')
CUT = '2026-11-23'
late = {}
for p, s in L:
    for m in re.finditer('[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]', s):
        if m.group(0) > CUT:
            k = m.group(0); e = late.setdefault(k, set()); e.add(p.split('.')[-1] if len(p) < 60 else p[:50])
    for m in re.finditer('(?<![0-9-])(2026-(1[2-9]|[2-9][0-9])|202[7-9]-[0-9][0-9])(?![0-9])', s):
        k = m.group(0) + '(月)'; late.setdefault(k, set()).add(p[:44])
print('AJ dates/months later than cutoff:', {k: len(v) for k, v in sorted(late.items())})
# calendar pending / future entries
ents = cal.get('entries') or cal.get('events') or cal.get('items') or []
if isinstance(cal, dict) and not ents:
    for k, v in cal.items():
        if isinstance(v, list): ents = ents + v
print('cal keys', sorted(cal.keys())[:12], 'n entries', len(ents))
fut = 0; pend = 0
for e in ents:
    t = json.dumps(e, ensure_ascii=False)
    for key in ('effective_date', 'effective', 'decision_date', 'decision', 'publication_date', 'first_publish_on_or_after'):
        v = e.get(key) if isinstance(e, dict) else None
        if isinstance(v, str) and len(v) == 10 and v > CUT: fut += 1
    if isinstance(e, dict) and str(e.get('status', '')).lower() in ('pending', 'scheduled', 'effective_future'): pend += 1
print('calendar entries with date later than cutoff', fut, 'pending', pend)
# rates decomposition identity
rd = rep['research_plan'].get('rates_decomposition'); ut = rep['research_plan'].get('us_rates_trio')
print('rates_decomposition', json.dumps(rd, ensure_ascii=False)[:900])
print('us_rates_trio keys', sorted(ut.keys()) if isinstance(ut, dict) else type(ut).__name__)
print('us_rates_trio', json.dumps(ut, ensure_ascii=False)[:700])
ajr = aj['reader_map'].get('rates_decomposition')
print('AJ reader_map.rates_decomposition', json.dumps(ajr, ensure_ascii=False)[:900])
for d in ('2026-10-20', '2026-11-19', '2026-11-23'):
    row = {}
    for m in ('UST_10Y', 'TIPS_10Y', 'BEI_10Y', 'UST_2Y', 'TIPS_2Y', 'BEI_2Y', 'CURVE_2S10S'):
        if m in S and d in S[m]['dates']: row[m] = S[m]['values'][S[m]['dates'].index(d)]
    print('SS', d, row)
run = rep.get('run') or {}
print('run keys', sorted(run.keys()))
print('evidence_gate', json.dumps(run.get('evidence_gate'), ensure_ascii=False)[:900])
for k in ('blocked_class', 'draft', 'draft_verdict', 'status', 'delivery_gate', 'gate'):
    if k in run: print('run.' + k, json.dumps(run[k], ensure_ascii=False)[:300])
