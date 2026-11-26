# s30_gen_prose.py <snap> <reg> <cal> <report> <aj> <all_json> <dir> <out> [dry]  -- assert narrative numbers, assemble PROSE-round1.md (single write)
import sys, json, hashlib, collections, datetime as dt, re
snap = json.load(open(sys.argv[1], encoding='utf-8')); reg = json.load(open(sys.argv[2], encoding='utf-8'))
cal = json.load(open(sys.argv[3], encoding='utf-8')); rep = json.load(open(sys.argv[4], encoding='utf-8'))
aj = json.load(open(sys.argv[5], encoding='utf-8')); allp = json.load(open(sys.argv[6], encoding='utf-8'))
D = sys.argv[7]; out = sys.argv[8]; dry = len(sys.argv) > 9 and sys.argv[9] == 'dry'
S = snap['series_store']; pts = allp['points']
def near(a, b): return abs(float(a) - float(b)) < 1e-9
def at(m, ym):
    for d, v in zip(S[m]['dates'], S[m]['values']):
        if d[:7] == ym: return v
def atd(m, d): return S[m]['values'][S[m]['dates'].index(d)]
def chg(m, a, b):
    s = S[m]; o = []
    for i in range(1, len(s['dates'])):
        if s['values'][i] != s['values'][i - 1] and a < s['dates'][i] <= b: o.append(s['dates'][i])
    return o
# ---- counts quoted in the narrative ----
assert len(pts) == 1277 and sum(1 for p in pts if not p['ok']) == 0
bysec = dict(collections.Counter(p['sec'] for p in pts))
EXP = {chr(0x2460): 64, chr(0x2461): 115, chr(0x2462): 39, chr(0x2463): 144, chr(0x2464): 47, chr(0x2465): 74, chr(0x2466): 106, chr(0x2467): 7, chr(0x2468): 17, chr(0x2469): 47, chr(0x246A): 65, chr(0x246B): 23, chr(0x246C): 23, 'E-日期': 47, 'E-月串': 21, 'E-月日': 10, 'F': 51, 'G': 253, 'MAP': 67, 'N': 57}
assert bysec == EXP, bysec
anch = [p for p in pts if p['tok']]; assert len(anch) == 617 and len(pts) - len(anch) == 660
body = [p for p in anch if p['where'].startswith(('l3', 'l4', 'reader_map', 'quality_gate_notes'))]
assert len(body) == 543 and len(set((p['where'], p['tok']) for p in body)) == 429 and len(set(p['where'] for p in body)) == 46
other = [p for p in anch if not p['where'].startswith(('l3', 'l4', 'reader_map', 'quality_gate_notes'))]
assert sum(1 for p in anch if p['sec'] == 'MAP') == 0 and len(other) == 74
assert sum(1 for p in other if p['where'].startswith('(') and '全文' in p['where']) == 64
assert sum(1 for p in other if p['where'].startswith('agent_declaration')) == 8 and sum(1 for p in other if p['where'].startswith('schema_version')) == 2
NUM = []
def walk(o):
    if isinstance(o, dict):
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
    elif isinstance(o, (int, float)) and not isinstance(o, bool): NUM.append(o)
walk(aj); assert len(NUM) == 33
# ---- values quoted in the narrative ----
for ym, v in (('2025-01', 4.03), ('2025-09', 2.91), ('2025-10', 2.99), ('2026-02', 1.27), ('2026-03', 1.46), ('2026-04', 1.38), ('2026-10', 2.44), ('2026-05', 1.53), ('2026-06', 1.67), ('2026-07', 1.97), ('2026-08', 1.98), ('2026-09', 2.16)):
    assert near(at('JP_CPI_YOY', ym), v), (ym, at('JP_CPI_YOY', ym))
mx = max(v for v in S['JP_CPI_YOY']['values'] if v is not None)
assert near(mx, 4.31) and [d[:7] for d, v in zip(S['JP_CPI_YOY']['dates'], S['JP_CPI_YOY']['values']) if v == mx] == ['2023-01']
for ym, v in (('2025-10', 2.1), ('2026-05', 3.2), ('2026-06', 2.8), ('2026-07', 2.9), ('2026-08', 3.2), ('2026-09', 3.8), ('2026-10', 4.0), ('2026-04', 3.0)):
    assert near(at('EA_HICP_YOY', ym), v), (ym, at('EA_HICP_YOY', ym))
for ym, v in (('2025-11', 0.478), ('2026-04', 0.727), ('2026-07', 0.978), ('2026-08', 0.977), ('2026-09', 1.043), ('2026-10', 1.227)):
    assert near(at('JP_POLICY_RATE', ym), v), (ym, at('JP_POLICY_RATE', ym))
assert chg('ECB_MRO', '2025-11-23', '2026-11-23') == ['2026-06-17', '2026-09-16'] and chg('ECB_DFR', '2025-11-23', '2026-11-23') == ['2026-06-17', '2026-09-16']
for ym, v in (('2026-04', 1.42), ('2026-06', 1.6), ('2026-09', 2.69), ('2026-10', 2.73)):
    assert near(at('JP_CPI_TOKYO_YOY', ym), v), (ym, at('JP_CPI_TOKYO_YOY', ym))
for d, v in (('2026-11-13', 19.30), ('2026-11-16', 22.91), ('2026-11-17', 25.46), ('2026-11-18', 24.56), ('2026-11-19', 28.44), ('2026-11-20', 35.89), ('2026-11-23', 27.01)):
    assert abs(atd('VIX', d) - v) < 0.006, d
rl = reg.get('metrics') if isinstance(reg, dict) else reg
RM = {r.get('metric_id'): r for r in rl}
lag = (dt.date(2026, 11, 23) - dt.date(2026, 9, 16)).days
for m in ('ECB_MRO', 'ECB_DFR'):
    assert lag == 68 and RM[m]['freshness']['max_calendar_lag_days'] == 10, (m, lag, RM[m]['freshness'])
assert 'JP_POLICY_TARGET' not in RM
ga = snap['gate_a']; assert ga['status'] == 'DEGRADED' and len(ga['noncore_missing']) == 7 and len(ga['noncore_degraded']) == 8
assert 'JP_CPI_TOKYO_YOY' in ga['noncore_missing'] and 'ECB_DFR' in ga['noncore_degraded']
qw = json.dumps(rep['research_plan']['question_window'], ensure_ascii=False); assert '2026-05-23' in qw and '2026-11-23' in qw
hd = aj['reader_map']['headline_conclusion']; q = aj['quality_gate_notes']
assert '距截止 六十八 天' in hd and '距截止 68 天' in q[4] and '两情景五行齐备' in q[3]
assert '自 2025-01 高点 4.03 总体回落' in aj['reader_map']['regions'][1]['from_to']
assert hashlib.sha256(open(sys.argv[5], 'rb').read()).hexdigest().startswith('b82bf46df353a653')
# contract verification / delivery gate / rates / echo / calendar / post-cutoff dates
cv = rep['agent_judgment']['contract_verification']['verdicts']
assert len(cv) == 5 and [v['status'] for v in cv].count('VERIFIED') == 4
nv = [v for v in cv if v['status'] != 'VERIFIED']; assert len(nv) == 1 and nv[0]['status'] == 'STALE' and nv[0]['metric'] == 'ECB_DFR' and nv[0]['token'] == '2.5%' and near(nv[0]['value'], 2.5) and near(nv[0]['expected'], 2.5)
eg = rep['run']['evidence_gate']['counts']
assert eg['facts_kept'] == 105 and eg['facts_dropped'] == 0 and eg['facts_excluded_version'] == 0 and 'blocked_class' not in rep['run']
ut = rep['research_plan']['us_rates_trio']; rd = aj['reader_map']['rates_decomposition']
assert [rd['window_from'], rd['window_to']] == [ut['window']['from'], ut['window']['to']] == ['2026-10-20', '2026-11-19']
bp = {k: round((atd(k, '2026-11-19') - atd(k, '2026-10-20')) * 100, 3) for k in ('UST_10Y', 'TIPS_10Y', 'BEI_10Y')}
assert bp == {'UST_10Y': -8.0, 'TIPS_10Y': 11.0, 'BEI_10Y': -19.0} and near(rd['nominal_bp'], bp['UST_10Y']) and near(rd['real_bp'], bp['TIPS_10Y']) and near(rd['bei_bp'], bp['BEI_10Y'])
assert near(atd('TIPS_10Y', '2026-11-19') + atd('BEI_10Y', '2026-11-19'), atd('UST_10Y', '2026-11-19')) and near(atd('UST_10Y', '2026-10-20'), 5.12) and near(atd('TIPS_10Y', '2026-10-20'), 2.77) and near(atd('BEI_10Y', '2026-10-20'), 2.35)
echo = {e['metric_id']: e for e in aj['reader_map']['asset_returns_echo']}
for m, v in (('NIKKEI225', -9.98), ('DAX', 0.11), ('SPX', -5.51), ('VIX', 38.87)):
    e = echo[m]; assert near(round((atd(m, e['window']['to']) / atd(m, e['window']['from']) - 1.0) * 100.0, 2), v) and e['window']['from'] == '2026-10-23' and e['window_months'] == 1
ents = cal['entries']; assert len(ents) == 18
fut = 0
for e in ents:
    for key in ('effective_date', 'effective', 'decision_date', 'decision', 'publication_date', 'first_publish_on_or_after'):
        v = e.get(key) if isinstance(e, dict) else None
        if isinstance(v, str) and len(v) == 10 and v > '2026-11-23': fut += 1
assert fut == 0
STR = []
def walks(o):
    if isinstance(o, dict):
        for v in o.values(): walks(v)
    elif isinstance(o, list):
        for v in o: walks(v)
    elif isinstance(o, str): STR.append(o)
walks(aj); assert len(STR) == 183
late = set()
for s in STR:
    for m in re.finditer('[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]', s):
        if m.group(0) > '2026-11-23': late.add(m.group(0))
    for m in re.finditer('(?<![0-9-])[0-9][0-9][0-9][0-9]-(0[1-9]|1[0-2])(?![0-9])', s):
        if m.group(0) > '2026-11': late.add(m.group(0) + '(月)')
assert late == {'2026-11-24', '2026-11-30', '2026-12(月)', '2027-01(月)', '2027-02(月)', '2027-02-15'}, late
# ---- appendix table ----
def cl(x, n):
    s = x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)
    s = s.replace('|', '¦').replace(chr(10), ' ')
    return (s[:n] + '…') if len(s) > n else s
L = ['| # | 节 | 出处(文件+键) | 直算值 | 受审稿值 / 文内 token | 一致 |', '|---|---|---|---|---|---|']
for i, p in enumerate(pts, 1):
    L.append('| ' + str(i) + ' | ' + p['sec'] + ' | ' + cl(p['src'], 90) + ' | ' + cl(p['comp'], 70) + ' | ' + cl(p['rep'], 50) + (' / ' + cl(p['tok'], 24) if p['tok'] else '') + ' | ' + ('是' if p['ok'] else '否') + ' |')
parts = [open(D + '/s30_p' + str(i) + '.md', encoding='utf-8').read() for i in range(1, 6)]
text = ''.join(parts) + chr(10).join(L) + chr(10)
assert text.count(chr(10)) > 1280 and text.startswith('# Audit-R32')
print('VALID ok | table rows', len(pts), '| prose bytes', len(text.encode('utf-8')), '| lines', text.count(chr(10)), '| numeric leaves', len(NUM), '| late dates', sorted(late))
if dry:
    print('DRY RUN - not written')
else:
    with open(out, 'w', encoding='utf-8') as f:
        f.write(text)
    print('WRITTEN', out)
