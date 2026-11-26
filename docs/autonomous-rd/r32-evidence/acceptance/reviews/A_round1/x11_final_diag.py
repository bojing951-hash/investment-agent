# -*- coding: utf-8 -*-
"""x11: 出稿前只读诊断(Audit-R32 A round1)。用法: /usr/bin/python3 -I x11_final_diag.py <run_dir> <snapshot.json> <points.jsonl>"""
import sys, os, re, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_lib as L
R, SNAP, PTS = sys.argv[1:4]
def load(p):
    return json.load(open(p, encoding='utf-8'))
cal = load(os.path.join(R, 'root_overlay', 'config', 'release_calendar.json'))
snap = load(SNAP); F = L.Face(snap, cal)
aj = load(os.path.join(R, 'agent_judgment.json')); rep = load(os.path.join(R, 'report.json'))
recs = [json.loads(l) for l in open(PTS, encoding='utf-8') if l.strip()]
OKM = {True: 'T', False: 'F', 'NA': 'NA'}
print('=== L3 titles')
for i, c in enumerate(aj['l3']['contradictions']):
    print(i, 'id=', c.get('id'), '| title=', c.get('title'), '| keys=', list(c.keys()))
    for e in c.get('explanations', []):
        print('   expl', e.get('id') or e.get('label'), list(e.keys()))
for ci, ch in enumerate(aj['l3']['mechanism_chains']):
    print('== M%d %s' % (ci + 1, ch.get('title')))
    for lk in ch['links']:
        print('  [step %s %s] %s' % (lk.get('step'), lk.get('evidence_level'), lk.get('text')))
for ci, ch in enumerate(aj['reader_map']['transmission']):
    print('== TR%d %s' % (ci + 1, ch.get('title')))
    for lk in ch['links']:
        for k in ('title', 'observed_fact', 'causal_hypothesis', 'competing_explanation'):
            print('  [step %s] %s: %s' % (lk.get('step'), k, lk.get(k)))
print('== headline:', aj['reader_map']['headline_conclusion'])
print('== quality_gate_notes[3]:', aj['quality_gate_notes'][3][:700])
print('=== NA records')
for i, r in enumerate(recs):
    if r['ok'] == 'NA':
        print('#%d | %s | %s | computed=%s | reported=%s | note=%s' % (i, r.get('section'), str(r.get('src'))[:150], json.dumps(r.get('computed'), ensure_ascii=False)[:110], json.dumps(r.get('reported'), ensure_ascii=False)[:90], str(r.get('note'))[:230]))
IDX = [('c1_levels', 885, 895), ('ecb_two', 896, 896), ('jprate_path', 897, 897), ('rates_12m', 898, 898), ('near_assets', 899, 899),
       ('cpi_pce_after', 900, 900), ('c3_latest', 901, 903), ('overnight', 904, 904), ('lpr', 905, 905), ('scissors', 906, 906),
       ('scn1_hist', 908, 911), ('scn2_hist', 912, 914), ('dims', 915, 915), ('overlap', 916, 916), ('scen_thr', 917, 917),
       ('dfedtaru', 918, 918), ('dec_dates', 919, 919), ('panel_conv', 920, 922), ('boj_fields', 923, 923), ('pol_entries', 924, 924),
       ('ecb_boj', 925, 925), ('sep_dec', 926, 926), ('cand_rank', 927, 927), ('turn1', 928, 928), ('jpcpi_high', 929, 929),
       ('turn0_jump', 930, 930), ('core_diff', 931, 931), ('ev_labels', 932, 932),
       ('asset_win', 332, 344), ('cpi_path', 354, 358), ('cn_ppi', 400, 407), ('pmi', 415, 418), ('tokyo', 430, 438), ('omo', 449, 454),
       ('gaps', 490, 495), ('decomp', 508, 515), ('dist_metrics', 544, 544), ('scen', 547, 555), ('coverage', 579, 579), ('sign_agree', 581, 583),
       ('c2', 686, 687), ('omo_win', 779, 779), ('rc11', 854, 869), ('rc13', 870, 877), ('rc12', 878, 884)]
print('=== IDX ranges')
for nm, lo, hi in IDX:
    print('--- %s #%d-#%d' % (nm, lo, hi))
    for i in range(lo, hi + 1):
        r = recs[i]
        print('  #%d %s | %s | %s' % (i, OKM.get(r['ok'], '?'), r.get('section'), str(r.get('src'))[:100]))
print('=== sections')
for i, r in enumerate(recs):
    s = str(r.get('section', ''))
    if any(k in s for k in ('⑦传导环数字', '⑦日度相关', '⑨情景', '⑪', '⑫时点', '⑩报告间')):
        print('  #%d %s | %s | %s' % (i, OKM.get(r['ok'], '?'), s, str(r.get('src'))[:100]))
ga = snap['gate_a']
print('=== gate_a keys:', list(ga.keys()))
for k in ('noncore_missing', 'noncore_degraded'):
    print(k, ga.get(k))
    for m in ga.get(k) or []:
        s = snap['series_store'].get(m)
        print('   ', m, 'n=', (len(s['dates']) if s else None), 'last=', (s['dates'][-1] if s and s['dates'] else None))
def y(name, ym):
    t = L.yoy_level(F, name, ym)
    return None if t[0] is None else round(t[0], 4)
for ym in ('2026-04', '2026-05', '2026-06', '2026-07', '2026-08', '2026-09', '2026-10'):
    print(ym, 'CPI yoy', y('CPI', ym), 'CORE_PCE yoy', y('CORE_PCE', ym), 'CORE_CPI yoy', y('CORE_CPI', ym), 'HICP', F.monthly('EA_HICP_YOY').get(ym))
print('visible registry @2026-09-10', L.visible_latest(F, 'EA_HICP_YOY', '2026-09-10'))
print('visible registry @2026-06-11', L.visible_latest(F, 'EA_HICP_YOY', '2026-06-11'))
print('release 2026-08', L.release_date(F, 'EA_HICP_YOY', '2026-08-01'), 'month_end', L.month_end('2026-08'), L.weekday(L.month_end('2026-08')))
pp = F.monthly('CN_PPI_YOY')
print('CN_PPI min', min((v, k) for k, v in pp.items() if v is not None), '2025-11', pp.get('2025-11'), 'n', len(pp))
jp = F.monthly('JP_CPI_YOY')
print('JP_CPI 2026-01..09', [(k, jp.get(k)) for k in ('2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08', '2026-09')])
for d in ('2026-02-27', '2026-05-04', '2026-06-10', '2026-10-23', '2026-11-20'):
    print('BEI', d, F.at('BEI_10Y', d))
w = F.window('BEI_10Y', '2026-06-17', '2026-11-23')
print('BEI from 2026-06-17 min/max', min(v for _, v in w), max(v for _, v in w), 'n', len(w))
rt = open(os.path.join(R, 'report.json'), encoding='utf-8').read()
print('prior review ids in report.json:', [(x, x in rt) for x in ('f722e3c', '19638e1', '8f9055d')])
cv = rep['agent_judgment']['contract_verification']
for k in ('verdicts', 'six_checks', 'map_checks'):
    print('cv.%s[0] =' % k, json.dumps(cv[k][0], ensure_ascii=False)[:420])
print('=== sweep heads')
for fn in ('mid_rc14_out.txt', 'mid_rc14b_out.txt'):
    p = os.path.join(os.path.dirname(os.path.abspath(PTS)), fn)
    ls = open(p, encoding='utf-8').read().split('\n')
    print(fn, 'lines', len(ls)); print('\n'.join(l[:230] for l in ls[:7])); print('   ...tail:'); print('\n'.join(l[:230] for l in ls[-4:]))
def mt(p):
    return datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime('%m-%d %H:%M:%S')
aud = ['MAP_REPORT.md', 'FULL_REPORT.md', 'report.md', 'agent_judgment.json', 'report.json', 'evidence_index.json', 'views_digest.json',
       'AGENT_SEAT_ENVELOPE.json', 'question_verbatim.txt', 'MAP_REPORT.sha256', 'root_overlay/config/release_calendar.json',
       'root_overlay/data/daily/research_snapshot_20261123.json']
print('=== mtimes audited:', [(f.split('/')[-1], mt(os.path.join(R, f))) for f in aud], '| snapshot(install):', mt(SNAP))
sd = os.path.dirname(os.path.abspath(PTS))
fs = sorted((os.path.getmtime(os.path.join(sd, f)), f) for f in os.listdir(sd))
print('seat files n=%d first3=%s last3=%s' % (len(fs), [(f, datetime.datetime.fromtimestamp(t).strftime('%m-%d %H:%M:%S')) for t, f in fs[:3]], [(f, datetime.datetime.fromtimestamp(t).strftime('%m-%d %H:%M:%S')) for t, f in fs[-3:]]))
print('outputs exist:', os.path.exists(os.path.join(sd, 'PROSE-round1.md')), os.path.exists(os.path.join(sd, 'VERDICT-round1.json')))
