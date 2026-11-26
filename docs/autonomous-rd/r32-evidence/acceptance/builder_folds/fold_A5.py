#!/usr/bin/python3 -I
"""fold_A5.py <judgment_in.json> <tree> <run_dir> <judgment_out.json> --expect-new-engine

Builder revision of the A work-order judgment (the map question) after (a) the
independent review it received at the superseded stamp 19638e1 (UPHELD with 0
MAJOR / 9 MINOR / 11 NIT) and (b) the engine fix of the policy-window net
change (sum of the change points, carried in the reader report's policy path
panel).  The fold requires the fixed engine stamp (8f9055d).  Every number
quoted in a replacement sentence is recomputed here from the run's own frozen
inputs (root_overlay snapshot / release calendar / evidence index /
report.json) and asserted before the text is written.  Read-only on the run
directory.  `tree` is the tree whose engine code the helpers are imported from
(read-only).

Folded (pre-review item numbers):
  MINOR #0  two face-off verdicts were weaker than the pre-registered
             distinguishing-metric faces: link 1 (BRENT_F) supports the main
             explanation, link 4 (USDJPY) supports the competing explanation;
             the daily co-movement face of NIT #9 is folded into link 4
        #1  the "tightening despite falling inflation" argument was applied to
             all three central banks; local inflation visible at each decision
             is now stated per bank under the engine publication rule
        #2  real-rate / equity co-movement is a near-window fact; the 12-month
             window contrast is disclosed
        #3  the lead words of the three history sync texts covered inflation
             only; the engine region x dimension sync face is now written out
        #4  scenario triggers pointed at a release calendar that has no Fed /
             ECB record
        #5  the exchange-rate leg of C3 is checkable (USDCNY window)
        #6  "US-EU-CN inflation resonance" — the China leg is PPI; CN CPI flat
        #7  latest-revision vintage of the GDP anchor cells not transcribed
        #8  engine candidate delta (-0.3767) vs unrounded (-0.3768)
  NIT #9-#15 (daily co-movement, Sunday publication rule dates, "one of the
        highest", PMI year-on-year caliber, INDPRO trough, "accelerated",
        lead word vs candidate-face caliber), #16-#19 (reference count scope,
        US GDP anchor one quarter earlier after the 2025 shutdown, weekend
        rule dates, BEI threshold basis).
  Engine fix ripple: the policy one-year window path now sums the change
  points (ECB_DFR / ECB_MRO +50bp, JP_POLICY_RATE +75bp) — the caliber note
  and the JP / EA regional texts follow the fixed panel.
"""
import copy
import datetime
import hashlib
import json
import os
import sys
sys.path.insert(0, '/tmp/r32-accept/scripts')
import seatlib_r32 as L                                  # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith('--')]
STRICT = '--expect-new-engine' in sys.argv[1:]
j_in, tree, rd, j_out = args[:4]
for p in (os.path.join(tree, 'scripts'), os.path.join(tree, 'scripts', 'research_contract')):
    sys.path.insert(0, p)
import research_map_planner as rmp                      # noqa: E402

assert STRICT, 'fold_A5 quotes the fixed policy-window panel: run it with --expect-new-engine'
FR = L.Frozen(rd)
ss = FR.ss
R = FR.rep['run']
P = FR.rep['research_plan']
RID = R['ts_utc']
J = copy.deepcopy(json.load(open(j_in, encoding='utf-8')))
assert J['agent_declaration']['produced_by'].count(RID) == 1, RID
LOG = []


def rep(s, old, new, n=1):
    assert s.count(old) == n, ('anchor count', s.count(old), n, old[:48])
    return s.replace(old, new)


def sub(obj, key, old, new, where):
    obj[key] = rep(obj[key], old, new)
    LOG.append('[%s] %s\n    - %s\n    + %s' % (where, key, old, new))


D = '零一二三四五六七八九'


def cn_num(x, nd=2):
    """number -> Chinese numerals, e.g. 5.51 -> 五点五一."""
    t = ('%.' + str(nd) + 'f') % float(x)
    ip, fp = t.split('.')
    return D[int(ip)] + '点' + ''.join(D[int(c)] for c in fp.rstrip('0'))


def cn_int(x):
    """integer 0..999 -> Chinese numerals, e.g. 125 -> 一百二十五."""
    x = int(x)
    if x < 10:
        return D[x]
    if x < 100:
        t, o = divmod(x, 10)
        return ('' if t == 1 else D[t]) + '十' + (D[o] if o else '')
    h, r = divmod(x, 100)
    return D[h] + '百' + ('' if r == 0 else ('零' + D[r]) if r < 10 else cn_int(r))


RM = J['reader_map']
L3 = J['l3']
CS = L3['contradictions']
CH = L3['mechanism_chains']
TR = RM['transmission']
T0, T1 = TR[0]['links'], TR[1]['links']
TN, TS = RM['turnings'], RM['turning_supplement']
HP = RM['history_periods']
REG = {r['region']: r for r in RM['regions']}
SC = J['l4']['scenarios']
Q = J['quality_gate_notes']
assert [c['id'] for c in CS] == ['C1', 'C2', 'C3']
assert [c['id'] for c in CH] == ['M1', 'M2'] and [len(c['links']) for c in CH] == [4, 2]
assert [t['chain_id'] for t in TR] == ['TR1', 'TR2'] and [len(t['links']) for t in TR] == [3, 1]
assert [t['metric_id'] for t in TN] == ['CPI', 'INDPRO', 'JP_CPI_YOY'] and len(TS) == 1
assert [h['anchor_ym'] for h in HP] == ['2025-03', '2022-06', '2023-10']
assert sorted(REG) == ['CN', 'EA', 'JP', 'US'] and len(SC) == 2 and len(Q) == 6

# ── computed facts (frozen inputs of this run) ─────────────────────────
assert FR.as_of == '2026-11-23'
if STRICT:
    assert (R.get('git_head') or '').startswith('8f9055d'), R.get('git_head')
DT = datetime.date
assert FR.snap['research_as_of'] == '2026-11-23T22:53:47+08:00' and FR.snap['snapshot_id'] == 'research_snapshot_20261123'
mp = FR.monthly


def yoy(m, d):
    pm = '%04d-%02d' % (int(m[:4]) - 1, int(m[5:7]))
    return (d[m] / d[pm] - 1.0) * 100.0 if pm in d else None


# #6: the China leg of the "resonance" is PPI; CN CPI flat in the window
cn = mp('CN_CPI_YOY')
assert [cn[k] for k in ('2026-02', '2026-03', '2026-04', '2026-05')] == [1.3, 1.0, 1.2, 1.2]
assert cn_num(1.0) == '一点' and cn_num(1.3) == '一点三'          # the low end 1.0 is written 一点零 (zero kept) in the prose
cp, cc, ec, jc = mp('CN_PPI_YOY'), mp('CPI'), mp('EA_HICP_YOY'), mp('JP_CPI_YOY')
ci = yoy('2026-05', cc)
assert '%.4f' % yoy('2026-02', cc) == '2.4340' and '%.2f' % ci == '4.17' \
    and [ec[k] for k in ('2026-02', '2026-05')] == [1.9, 3.2] and [cp[k] for k in ('2026-02', '2026-05')] == [-0.9, 3.9]
assert cp['2026-10'] == 5.7 and ec['2026-10'] == 4.0 and cn['2026-10'] == 0.7
assert [ec[k] for k in ('2026-01', '2026-06', '2026-07', '2026-08', '2026-09')] == [1.7, 2.8, 2.9, 3.2, 3.8]

# #0 / #1: BRENT_F window and core CPI
b0, b3, b5, b6 = (FR.val('BRENT_F', d) for d in ('2026-02-27', '2026-03-31', '2026-05-29', '2026-06-30'))
assert (FR.date('BRENT_F', '2026-02-27'), FR.date('BRENT_F', '2026-05-29')) == ('2026-02-27', '2026-05-29')
assert '%.2f|%.2f|%.2f|%.2f' % (b0, b3, b5, b6) == '72.48|118.35|92.05|72.92'
assert '%.2f' % FR.ret('BRENT_F', '2026-02-27', '2026-05-29') == '27.00' and b0 < b6 < b5          # 2026-06 end back near the window start
assert max((v, d) for d, v in zip(ss['BRENT_F']['dates'], ss['BRENT_F']['values']) if '2026-01-01' <= d <= '2026-11-23') == (118.349998, '2026-03-31')
assert FR.val('BRENT_F', '2026-10-23') == 116.720001 and FR.val('BRENT_F', '2026-11-23') == 88.190002
kc, kp = mp('CORE_CPI'), mp('CORE_PCE')
assert '%.2f|%.2f' % (yoy('2026-02', kc), yoy('2026-05', kc)) == '2.47|2.82'
assert round(yoy('2026-08', kc) - yoy('2026-05', kc), 4) == -0.3768 \
    and round(round(yoy('2026-08', kc), 4) - round(yoy('2026-05', kc), 4), 4) == -0.3767   # #8 (four-decimal endpoints)
assert '%.2f|%.2f' % (yoy('2026-05', kp), yoy('2026-07', kp)) == '3.16|3.00' \
    and yoy('2026-07', kp) < yoy('2026-06', kp) < yoy('2026-05', kp)

# #2: real rate / equity co-movement by window
W = {}
for d0, d1 in (('2025-11-19', '2026-11-19'), ('2026-10-20', '2026-11-19'), ('2026-08-19', '2026-11-19')):
    assert all(FR.date(m, d0) == d0 and FR.date(m, d1) == d1 for m in ('SPX', 'NIKKEI225', 'DAX', 'TIPS_10Y')), (d0, d1)
    W[(d0, d1)] = (round((FR.val('TIPS_10Y', d1) - FR.val('TIPS_10Y', d0)) * 100),
                   '%.2f' % FR.ret('SPX', d0, d1), '%.2f' % FR.ret('NIKKEI225', d0, d1), '%.2f' % FR.ret('DAX', d0, d1))
K12, K1M, K3M = W[('2025-11-19', '2026-11-19')], W[('2026-10-20', '2026-11-19')], W[('2026-08-19', '2026-11-19')]
assert K12 == (102, '8.03', '22.47', '9.93') and K1M == (11, '-6.96', '-7.23', '0.63') and K3M == (53, '-6.90', '-9.00', '-2.41')
assert FR.val('TIPS_10Y', '2025-11-19') == 1.86 and FR.val('TIPS_10Y', '2026-11-19') == 2.88
K12T = ('实际利率 +102bp 与 SPX %s、NIKKEI225 %s、DAX %s 同向上行' % K12[1:])

# #5: the exchange-rate leg (USDCNY, common 12-month caliber)
assert FR.date('USDCNY', '2025-11-19') == '2025-11-19' and FR.date('USDCNY', '2026-11-19') == '2026-11-19'
assert (FR.val('USDCNY', '2025-11-19'), FR.val('USDCNY', '2026-11-19')) == (7.1075, 6.6676) \
    and '%.2f' % FR.ret('USDCNY', '2025-11-19', '2026-11-19') == '-6.19'

# #12 / #13 / #15: PMI year-on-year caliber, INDPRO trough, candidate face
pmi = mp('CN_PMI_MFG')
PMI = []
for a, b in (('2024-10', '2025-10'), ('2025-07', '2026-07'), ('2025-10', '2026-10')):
    PMI.append(('%.1f' % yoy(b, pmi), '%+.1f' % (pmi[b] - pmi[a]), pmi[a], pmi[b]))
assert [p[:2] for p in PMI] == [('-2.2', '-1.1'), ('-0.2', '-0.1'), ('0.6', '+0.3')], PMI
ip = mp('INDPRO')
# candidate window endpoints 2025-11 -> 2026-02; the series trough (0.69) is 2026-03, inside the 12-month window
assert '%.4f|%.4f|%.2f' % (yoy('2025-11', ip), yoy('2026-02', ip), yoy('2026-03', ip)) == '1.7543|0.7972|0.69' \
    and min((v, k) for k, v in ((k, yoy(k, ip)) for k in ip if '2025-11' <= k <= '2026-10'))[1] == '2026-03' \
    and yoy('2026-10', ip) > 2.14
CAND = {c['metric_id']: c for c in (P.get('turning_candidates') or {}).get('candidates')}
assert CAND['CN_PMI_MFG']['delta'] == 3.4005 and CAND['INDPRO']['delta'] == -0.9571 and CAND['CORE_CPI']['delta'] == -0.3767
assert max(CAND[m]['delta'] for m in ('INDPRO', 'CN_PMI_MFG')) == 3.4005
assert (CAND['CN_PMI_MFG']['value_before'], CAND['CN_PMI_MFG']['value_after']) == (-2.3904, 1.0101) \
    and CAND['CN_PMI_MFG']['unit'] == '同比%(派生于水平序列,严格同基期)' and CAND['CORE_CPI']['delta'] == round(CAND['CORE_CPI']['value_after'] - CAND['CORE_CPI']['value_before'], 4)

# #19: BEI_10Y threshold basis
below = [(d, v) for d, v in zip(ss['BEI_10Y']['dates'], ss['BEI_10Y']['values']) if v < 1.8]
assert below[-1] == ('2020-11-30', 1.77) and ss['BEI_10Y']['dates'][-1] == '2026-11-20' and ss['BEI_10Y']['values'][-1] == 2.15
assert round((2.15 - 1.8) * 100) == 35

# #7 / #17: GDP anchor cells (latest revision) and the shutdown-delayed 2025Q3 GDP
cells = {c['metric_id']: c for c in P['point_values']['cells']}
VS = '事后回顾(最新修订值,非当时首发值)'
for mid, vals in (('US_REAL_GDP', ('23884.563', '24408.011', '24611.077')), ('EA_REAL_GDP_YOY', ('1.11', '1.19', '1.28')),
                  ('JP_REAL_GDP_YOY', ('0.63', '0.8', '1.16'))):
    c = cells[mid]
    assert c['vintage_semantics'] == VS, (mid, c.get('vintage_semantics'))
    assert tuple(L.n(c['anchors'][a]['value']) for a in ('12个月前', '3个月前', '最新一期')) == vals, mid
    assert all(c['anchors'][a]['vintage'] == VS for a in c['anchors']), mid
ug = mp('US_REAL_GDP')
assert '%.2f|%.2f|%.2f' % (yoy('2025-04', ug), yoy('2026-04', ug), yoy('2026-07', ug)) == '2.42|2.19|2.07'
ENT = FR.cal.get('entries') or []
SH = [e for e in ENT if e.get('entry_id') == 'RC-2025SHUTDOWN-GDP-Q3']
assert len(ENT) == 18 and len([e for e in ENT if str(e.get('entry_id') or '').startswith('RC-2025SHUTDOWN-')]) == 11 and len(SH) == 1
SH = SH[0]
assert (SH['metric_id'], SH['obs_from'], SH['not_published_as_of'], SH['first_publish_on_or_after'], SH['basis']) == \
    ('US_REAL_GDP', '2025-07-01', '2025-12-22', '2025-12-23', 'user_directive')
assert '停摆' in SH['note'] and '2025-12-23' in SH['note']
assert not [e for e in ENT if str(e.get('metric_id') or '').upper().startswith(('FED', 'ECB', 'FOMC', 'DFEDTAR'))
             or 'FOMC' in str(e.get('entry_id') or '')]                                   # #4
assert cells['US_REAL_GDP']['anchors']['12个月前']['observation_date'] == '2025-04-01'                    # 2025Q2
assert cells['EA_REAL_GDP_YOY']['anchors']['12个月前']['observation_date'] == '2025-07-01' \
    and cells['JP_REAL_GDP_YOY']['anchors']['12个月前']['observation_date'] == '2025-07-01'    # 2025Q3
assert FR.cal.get('version') == '1.5.0'


def changes(mid):
    return [(ss[mid]['dates'][k], ss[mid]['values'][k - 1], ss[mid]['values'][k])
            for k in range(1, len(ss[mid]['dates'])) if ss[mid]['values'][k] != ss[mid]['values'][k - 1]]


# engine fix: policy one-year window path = sum of the change points (stored cell path == recomputed)
WP, OTHER = {}, {}
for mid in ('DFEDTARU', 'ECB_DFR', 'ECB_MRO', 'JP_POLICY_RATE'):
    wp = rmp._policy_window_path(ss[mid]['dates'], ss[mid]['values'], FR.as_of, metric_id=mid, carry_start=True)
    assert wp['window'] == ['2025-11-23', '2026-11-23']
    assert (cells[mid].get('policy_window_path') or {}) == wp, mid                       # stored == recomputed
    assert wp['net_bp'] == sum(e['delta_bp'] for e in wp['events']) == round((wp['window_end_value'] - wp['window_start_value']) * 100)
    ds, vs = ss[mid]['dates'], ss[mid]['values']
    iw = next(i for i in range(len(ds)) if ds[i] >= wp['window'][0])
    OTHER[mid] = round((vs[-1] - vs[iw]) * 100)                                            # first in-window observation caliber
    WP[mid] = wp
assert [e['decision_date'] for e in WP['DFEDTARU']['events']] == ['2025-12-10', '2026-09-16'] \
    and [e['delta_bp'] for e in WP['DFEDTARU']['events']] == [-25, 25] and WP['DFEDTARU']['net_bp'] == 0
for mid in ('ECB_DFR', 'ECB_MRO'):
    assert [(e['date'], e['decision_date'], e['delta_bp']) for e in WP[mid]['events']] == \
        [('2026-06-17', '2026-06-11', 25), ('2026-09-16', '2026-09-10', 25)] and WP[mid]['net_bp'] == 50
    assert WP[mid]['window_start_observation'] == '2025-06-11' and FR.last_date(mid) == '2026-09-16'
assert (WP['ECB_DFR']['window_start_value'], WP['ECB_DFR']['window_end_value']) == (2.0, 2.5) \
    and (WP['ECB_MRO']['window_start_value'], WP['ECB_MRO']['window_end_value']) == (2.15, 2.65)
assert [e['delta_bp'] for e in WP['JP_POLICY_RATE']['events']] == [8, 17, 11, 14, 7, 18] and WP['JP_POLICY_RATE']['net_bp'] == 75
assert (WP['JP_POLICY_RATE']['window_start_value'], WP['JP_POLICY_RATE']['window_start_observation'],
        WP['JP_POLICY_RATE']['window_end_value'], FR.last_date('JP_POLICY_RATE')) == (0.478, '2025-11-01', 1.227, '2026-10-01')
assert OTHER == {'DFEDTARU': 0, 'ECB_DFR': 25, 'ECB_MRO': 25, 'JP_POLICY_RATE': 67}, OTHER
pr = mp('JP_POLICY_RATE')
assert (pr['2025-11'], pr['2025-12'], pr['2026-10']) == (0.478, 0.557, 1.227) and round((pr['2026-10'] - pr['2025-12']) * 100) == 67

# #9: daily co-movement of SPX and USDJPY in the near window (intraday snapshot caliber)


def series_map(mid):
    return dict(zip(ss[mid]['dates'], ss[mid]['values']))


spx, uj = series_map('SPX'), series_map('USDJPY')
BASE = '2026-10-23'
DAYS = sorted(d for d in spx if d > BASE and d <= '2026-11-23' and d in uj)
assert len(DAYS) == 21 and DAYS[0] == '2026-10-26' and DAYS[-1] == '2026-11-23'
assert len([d for d in spx if d > BASE and d <= '2026-11-23']) == len([d for d in uj if d > BASE and d <= '2026-11-23']) == 21
prev = BASE
RS, RU = [], []
for d in DAYS:
    RS.append(spx[d] / spx[prev] - 1)
    RU.append(uj[d] / uj[prev] - 1)
    prev = d
_n = len(RS)
_mr, _mu = sum(RS) / _n, sum(RU) / _n
CORR = (sum((a - _mr) * (b - _mu) for a, b in zip(RS, RU))
        / (sum((a - _mr) ** 2 for a in RS) ** 0.5 * sum((b - _mu) ** 2 for b in RU) ** 0.5))
assert '%.2f' % CORR == '0.19'
DN = sorted([(d, a, b) for d, a, b in zip(DAYS, RS, RU) if a < 0], key=lambda x: x[1])
UP = [(d, a, b) for d, a, b in zip(DAYS, RS, RU) if a > 0]
assert len(DN) == 12 and len(UP) == 9


def comp(xs):
    p = 1.0
    for x in xs:
        p *= (1 + x)
    return (p - 1) * 100


assert (sum(1 for x in DN if x[2] < 0), sum(1 for x in DN if x[2] > 0)) == (9, 3)
assert (sum(1 for x in UP if x[2] > 0), sum(1 for x in UP if x[2] < 0)) == (7, 2)
assert ('%.2f' % comp([x[2] for x in DN]), '%.2f' % comp([x[2] for x in UP])) == ('0.16', '1.66')
assert [x[0] for x in DN[:4]] == ['2026-11-05', '2026-11-20', '2026-11-19', '2026-11-16']
assert ['%+.2f' % (x[2] * 100) for x in DN[:4]] == ['-0.07', '+0.20', '-0.08', '-0.06']
assert max(abs(x[2]) for x in DN[:4]) < 0.0021
assert ('%.2f' % FR.ret('SPX', BASE, '2026-11-23'), '%.2f' % FR.ret('USDJPY', BASE, '2026-11-23')) == ('-5.51', '1.82') \
    and (uj[BASE], uj[DAYS[-1]]) == (156.494003, 159.347)

# #1 / #18: local inflation visible at each decision (engine publication rule) and weekend rule dates


def visible(mid, day):
    p = FR.monthly(mid)
    best = pub = None
    for ym in sorted(p):
        if ym + '-01' > day:
            break
        d, b = rmp._visible_publish(mid, 'monthly', ym + '-01')
        if d and d <= day:
            best, pub = (ym, p[ym]), (d, b)
    return best, pub


def pub(mid, ym):
    return rmp._visible_publish(mid, 'monthly', ym + '-01')[0]


VIS = {(m, d): visible(m, d) for m, d in (('EA_HICP_YOY', '2026-06-11'), ('EA_HICP_YOY', '2026-09-10'), ('JP_CPI_YOY', '2026-09-18'),
                                          ('CORE_PCE', '2026-09-16'), ('CPI', '2026-09-16'), ('CPI', '2026-09-18'))}
assert VIS[('EA_HICP_YOY', '2026-06-11')][0] == ('2026-04', 3.0) and VIS[('EA_HICP_YOY', '2026-06-11')][1][0] == '2026-05-16'
assert VIS[('EA_HICP_YOY', '2026-09-10')][0] == ('2026-07', 2.9) and VIS[('EA_HICP_YOY', '2026-09-10')][1][0] == '2026-08-16'
assert VIS[('JP_CPI_YOY', '2026-09-18')][0] == ('2026-07', 1.97) and VIS[('JP_CPI_YOY', '2026-09-18')][1][0] == '2026-08-20'
assert VIS[('CORE_PCE', '2026-09-16')][0][0] == '2026-07' and VIS[('CORE_PCE', '2026-09-16')][1][0] == '2026-08-30'
assert VIS[('CPI', '2026-09-16')][0][0] == '2026-08' and VIS[('CPI', '2026-09-16')][1][0] == '2026-09-13'
assert pub('EA_HICP_YOY', '2026-08') == '2026-09-16' and pub('CPI', '2026-05') == '2026-06-13' and pub('CPI', '2026-08') == '2026-09-13' \
    and pub('JP_CPI_TOKYO_YOY', '2026-08') == '2026-08-30' and pub('JP_CPI_TOKYO_YOY', '2026-09') == '2026-09-29'
assert '%.2f' % yoy('2026-07', kp) == '3.00' and ec['2026-06'] == 2.8 and ec['2026-04'] == 3.0 and jc['2026-06'] < jc['2026-07']
assert yoy('2026-07', kp) < yoy('2026-05', kp) and ec['2026-07'] < ec['2026-05'] and ec['2026-07'] > ec['2026-06']
assert yoy('2026-07', kc) < yoy('2026-05', kc) and jc['2026-07'] < jc['2026-10']
assert [DT.fromisoformat(d).strftime('%a') for d in ('2026-06-13', '2026-09-13', '2026-08-30')] == ['Sat', 'Sun', 'Sun']
assert [DT.fromisoformat(d).strftime('%a') for d in ('2026-05-13', '2026-08-13', '2026-08-16', '2026-08-20', '2026-05-16')] == ['Wed', 'Thu', 'Sun', 'Thu', 'Sat']
assert ec['2026-08'] == 3.2 and mp('JP_CPI_TOKYO_YOY')['2026-08'] == 1.9
assert DT.fromisoformat('2026-06-13').toordinal() + 1 == DT.fromisoformat('2026-06-14').toordinal()       # rule day -> "around" the next weekday

# #16: reference counts
refs_l3 = [r for c in CS for r in c['evidence_refs']] + [r for ch_ in CH for lk in ch_['links'] for r in (lk.get('evidence_refs') or [])]
refs_l4 = [r for sc in SC for r in sc['rows']['asset_direction']['evidence_refs']]
assert (len(refs_l3), len(refs_l4), len(refs_l3) + len(refs_l4), len(set(refs_l3 + refs_l4))) == (41, 9, 50, 20)
E = FR.rep['evidence_index']
RK = 'ref' if 'ref' in E[0] else [k for k in E[0] if '@' in str(E[0][k])][0]
assert len(E) == 72 and set(refs_l3 + refs_l4) <= {e[RK] for e in E}

# #3: engine region x dimension sync face
face = rmp.history_region_sync_face(HP, FR.rep, root=tree)
FP = {p['anchor_ym']: p for p in face['periods']}
R3, NAME = ('CN', 'EA', 'JP'), {'CN': '中国', 'EA': '欧元区', 'JP': '日本'}
DIMN = (('growth', '增长维'), ('inflation', '通胀维'), ('policy', '政策维'))


def join(xs):
    return xs[0] if len(xs) == 1 else '、'.join(xs[:-1]) + '与' + xs[-1]


def dim_text(per, d):
    rows = [r for r in per['rows'] if r['dimension'] == d]
    assert len(rows) == 4
    lab = {r['region']: r['label_sync'] for r in rows}
    us = [r for r in rows if r['region'] == 'US'][0]
    assert us['label_sync'] == '基准(美国类比锚)'
    sync = [NAME[g] + ('同步(双持平)' if lab[g] == '同步(双持平)' else '同步') for g in R3 if lab[g].startswith('同步')]
    div = [NAME[g] + '分化' for g in R3 if lab[g] == '分化']
    assert len(sync) + len(div) == 3
    if len(sync) == 3:
        t = '三地均同步'
    elif len(div) == 3:
        t = '三地均分化'
    else:
        t = '、'.join(sync) + '、' + join(div)
    if d == 'policy' and us['direction'] == '上行':
        assert all(r['direction'] == '持平' for r in rows if r['region'] != 'US') and us['delta'] == 1.25
        t += '，美国上行%s个基点、三地持平' % cn_int(round(us['delta'] * 100))
    return t


EXPECT = {
    '2025-03': ('部分同步', 3, {'growth': '日本同步、中国分化与欧元区分化', 'inflation': '日本同步、中国分化与欧元区分化',
                           'policy': '中国同步(双持平)、欧元区分化与日本分化'}),
    '2022-06': ('同步', 5, {'growth': '欧元区同步、日本同步、中国分化', 'inflation': '三地均同步',
                        'policy': '三地均分化，美国上行一百二十五个基点、三地持平'}),
    '2023-10': ('不同步', 1, {'growth': '中国同步、欧元区分化与日本分化', 'inflation': '三地均分化', 'policy': '三地均分化'}),
}
assert cn_int(125) == '一百二十五' and cn_int(3) == '三' and cn_int(5) == '五' and cn_int(1) == '一'
PREFIX = {}
for h in HP:
    ym = h['anchor_ym']
    per = FP[ym]
    assert per['cutoff_ym'] == ym and len(per['rows']) == 12
    lead, n_syn, exp = EXPECT[ym]
    got = {d: dim_text(per, d) for d, _ in DIMN}
    assert got == exp, (ym, got)
    assert sum(1 for r in per['rows'] if r['region'] != 'US' and r['label_sync'].startswith('同步')) == n_syn
    assert h['other_regions_sync'].startswith(lead + ': ')
    PREFIX[ym] = '%s(引擎『地区×维度同步面』九格中%s格同步——%s): ' % (
        lead, cn_int(n_syn), '；'.join('%s: %s' % (dl, got[d]) for d, dl in DIMN))

# ══ folds ══════════════════════════════════════════════════════════════
FLAT = '中国CPI同比同窗持平于一点零至一点三'
# ── #6 / #15: headline ─────────────────────────────────────────────────
sub(RM, 'headline_conclusion', '美欧中通胀在2026-02至2026-05同窗共振回升(月频分辨率下先后未定)',
    '美欧通胀与中国生产价格(PPI)在2026-02至2026-05同窗共振回升(美国CPI、欧元区HICP、中国PPI；%s，消费价格未共振；月频分辨率下先后未定)' % FLAT,
    'headline')

# ── #5: C1 statement (asset leg = near-window fact; carry-trade leg of C unsupported) ─
C1 = CS[0]
sub(C1, 'statement', '『通胀再加速→政策再收紧→实际利率上行→风险资产收缩』的同向共动',
    '『通胀再加速→政策再收紧→实际利率上行→风险资产收缩』的同向共动(其中资产收缩一腿属于近月窗口的事实，全年窗口内股指并未下行，窗口对照披露见机制链资产环)',
    'C1.statement')
sub(C1, 'statement', '当前证据不足以在它们之间裁决——区分依赖',
    '当前证据不足以在它们之间裁决(其中解释C 的套息平仓一腿在同窗未获区分指标面支持，见传导面竞争链；其技术面一腿不可检验)——区分依赖',
    'C1.statement')
sub(C1['competing_explanations'], 0, '通胀再加速(2026-02至2026-05三地共振)迫使央行再收紧',
    '通胀再加速(2026-02至2026-05美欧消费价格与中国生产价格同窗共振)迫使央行再收紧', 'C1.competing_explanations[0]')
sub(C1['competing_explanations'], 2, '且 HY_OAS 应保持平稳(非信用事件)',
    '且 HY_OAS 应保持平稳(非信用事件)；同窗核验(见传导面竞争链): 该解释的套息平仓一腿未获区分指标面支持，技术面一腿不可检验',
    'C1.competing_explanations[2]')
sub(CS[2]['competing_explanations'], 2, CS[2]['competing_explanations'][2],
    '解释C: 汇率/资本流动目标约束政策选择——引擎面无中国资本流动序列,该解释当前不可裁决,标注【尚未验证】；'
    '汇率腿的可见事实: USDCNY 12 个月 -6.19%(7.1075→6.6676，共同口径 2025-11-19→2026-11-19)，人民币窗内升值，'
    '不支持『贬值/外流压力制约加息』的读法', 'C3.competing_explanations[2]')

# ── #6 / #1 / #2: mechanism chains ─────────────────────────────────────
L1_ = CH[0]['links']
sub(L1_[0], 'text', '2026-02→2026-05 美欧中通胀同窗回升(美国CPI同比2.434→4.1666、EA_HICP_YOY 1.9→3.2、CN_PPI_YOY -0.9→3.9),此后至最新观测月:',
    '2026-02→2026-05 美欧通胀与中国生产价格同窗回升(美国CPI同比2.434→4.1666、EA_HICP_YOY 1.9→3.2、CN_PPI_YOY -0.9→3.9，%s、消费价格未共振),此后至最新观测月:' % FLAT,
    'M1.links[0]')
sub(L1_[1], 'text', '——『因通胀续升而收紧』与 9 月决议前的可见数据不完全吻合，动机环证据减弱(仍不可验证)。',
    '——『因通胀续升而收紧』对美联储与欧央行第二次决议前的可见数据不完全吻合(美联储另见核心 PCE 同比: 2026-07 观测 3.00，低于 2026-05 高点 3.16；'
    '欧央行 2026-09-10 决议前最近可见 HICP 为 2026-07 观测 2.9，自 2026-06 的 2.8 回升、低于 2026-05 高点 3.2，'
    '2026-08 观测 3.2 按引擎规则推定发布于 2026-09-16、决议时点尚未可见)，对日本央行则未见该矛盾'
    '(2026-09-18 决议前最近可见日本CPI为 2026-07 观测 1.97，处回升段，与收紧动机相容但同样不可验证)'
    '——三家的动机归因均不可由本引擎数据验证，对美联储与欧央行的动机环证据减弱。', 'M1.links[1]')
sub(L1_[3], 'text', '的机制相容;但资产与利率只有共动事实',
    '的机制相容(此共动限于近窗: 共同交易日 2026-10-20→2026-11-19 TIPS_10Y +11bp 对 SPX -6.96%、2026-08-19→2026-11-19 +53bp 对 -6.90%；'
    '而12个月窗 2025-11-19→2026-11-19 ' + K12T + '，12个月窗内未见『实际利率上行伴随股指下行』，共动方向随窗口而异);但资产与利率只有共动事实',
    'M1.links[3]')
PANEL_OLD = '自 2025-12 月均 0.557 起为 +67 个基点，引擎『政策一年窗路径』面板按窗内首观测起算、显示 +67bp)'
PANEL_NEW = '自 2025-12 月均 0.557 起为 +67 个基点，属另一口径)'
sub(CH[1]['links'][0], 'text', PANEL_OLD, PANEL_NEW, 'M2.links[0]')

# ── #0: link 1 face-off (BRENT_F distinguishes: main prediction holds) ──
sub(T0[0], 'observed_fact', '中国PPI -0.9→3.9 同窗回升;此后',
    '中国PPI -0.9→3.9 同窗回升(美国CPI、欧元区HICP与中国PPI三序列，%s、消费价格未共振);此后' % FLAT, 'TR1.L1')
sub(T0[0], 'observed_fact', '(三地同窗共振,月频分辨率下先后未定)',
    '(共振指 2026-02至2026-05 窗的美欧消费价格与中国生产价格三序列，月频分辨率下先后未定)', 'TR1.L1')
sub(T0[0], 'causal_hypothesis',
    '对质注记: 主解释预期『同窗显著上行』——月末口径 2026-02 72.48→2026-05 92.05(首尾 +27.00%)相容；'
    '竞争解释预期『大体持平而核心CPI独立走高』——核心CPI同比同窗 2.47→2.82 亦相容，且布伦特 03 冲至 118.35 后于 05 回落至首月末附近(未持平)'
    '——两侧各有相容观测，尚不能区分。',
    '对质注记(按预注册窗 2026-02至2026-05 的区分指标面裁定): 主解释预期『同窗显著上行』成立——月末 72.48→92.05(首尾 +27.00%，2026-03 冲至 118.35)；'
    '竞争解释预期『大体持平』未获支持——窗末较窗启高 27.00%，至 2026-06 月末 72.92 才回到窗启水平附近；'
    '核心CPI同比同窗 2.47→2.82 对两解释均相容，不构成区分观测。裁定限于区分指标面: 竞争解释中『核心通胀独立走高』一腿仍相容，'
    '能源价格向消费价格的因果传导不可由本引擎验证(证据级E3不变)。注: 对质表『已有观测』列为引擎当前面(最新观测与近30日变化: 2026-10-23→2026-11-23 116.72→88.19)，不是本环预注册窗。',
    'TR1.L1')
sub(T0[0], 'face_off_verdict', '尚不能区分', '支持主解释', 'TR1.L1')

# ── #1 / #18: link 2 (local inflation visible at each decision) ────────
sub(T0[1], 'observed_fact', '2026-05 高点 4.17(推定发布 2026-06-13)。',
    '2026-05 高点 4.17(推定发布 2026-06-13 前后；规则值为星期六)。', 'TR1.L2')
sub(T0[1], 'observed_fact', '(3.35，推定发布 2026-09-13)；',
    '(3.35，推定发布 2026-09-13 前后；规则值为星期日)；', 'TR1.L2')
TAIL2 = '决议后发布的 2026-09 观测回升至 3.72(仍低于高点 4.17；2026-10 同比缺基期不可得)。'
sub(T0[1], 'observed_fact', TAIL2,
    TAIL2 + '核心 PCE 同比的决议前最近可见: 美联储 2026-09-16 为 2026-07 观测 3.00(推定发布 2026-08-30，低于 2026-05 高点 3.16)。'
    '欧元区与日本本地通胀(按引擎发布规则): 欧央行 2026-06-11 决议前最近可见 HICP 2026-04 观测 3.0(推定发布 2026-05-16，处上行段)，'
    '2026-09-10 决议前最近可见 2026-07 观测 2.9(推定发布 2026-08-16；自 2026-06 的 2.8 回升，低于 2026-05 高点 3.2；'
    '2026-08 观测 3.2 推定发布 2026-09-16，决议时点尚未可见)；日本央行 2026-09-18 决议前最近可见日本CPI 2026-07 观测 1.97(推定发布 2026-08-20，处回升段)。',
    'TR1.L2')
sub(T0[1], 'causal_hypothesis', '且决议时点前已可见的美国 CPI 同比已自高点回落(见观察事实)，动机环证据减弱。',
    '且决议时点前已可见的美国 CPI 与核心 PCE 同比、以及欧元区 HICP 均低于各自 2026-05 高点(见观察事实)，对美联储决议与欧央行第二次决议的动机环证据减弱；'
    '日本央行决议前可见的本地区通胀处回升段，与收紧动机相容但同样不可验证。', 'TR1.L2')

# ── #2: link 3 window contrast ─────────────────────────────────────────
TAIL3 = '属非信用事件级，但相对自身三年历史并不温和。'
sub(T0[2], 'observed_fact', TAIL3,
    TAIL3 + ' 窗口对照(共同交易日): 12个月窗 2025-11-19→2026-11-19 实际利率(TIPS_10Y) +102bp 的同时 SPX +8.03%、NIKKEI225 +22.47%、DAX +9.93%'
    '——12个月窗内股指与实际利率同向上行，资产收缩一腿只见于近窗(近1个月 2026-10-20→2026-11-19 TIPS_10Y +11bp 对 SPX -6.96%、'
    '近3个月 2026-08-19→2026-11-19 +53bp 对 -6.90%)。', 'TR1.L3')
sub(T0[2], 'causal_hypothesis', '同时容纳增长担忧的进入。 对质注记:',
    '同时容纳增长担忧的进入。窗口限定: 『实际利率上行压制风险资产』只是近1至3个月窗的相容读法，12个月窗内(2025-11-19→2026-11-19)%s，共动方向随窗口而异。 对质注记:' % K12T,
    'TR1.L3')

# ── #0 / #9: link 4 face-off (daily co-movement folded in) ────────────
sub(T1[0], 'observed_fact', PANEL_OLD, PANEL_NEW, 'TR2.L1')
sub(T1[0], 'causal_hypothesis', '竞争解释所需的『时间上解耦』须以逐日共动面核验，本档未做——尚不能区分。',
    '竞争解释预期的『时间上解耦』经逐日共动面补核(2026-10-26至2026-11-23 共 21 个交易日，以 2026-10-23 观测为基，逐日变动按共同交易日计): '
    '仅见弱同向耦合——相关系数 0.19；标普500指数下跌的 12 日中美元兑日元同跌 9 日、上涨 3 日，上涨的 9 日中同涨 7 日；'
    '标普下跌日美元兑日元复合累计 +0.16%、上涨日 +1.66%(两类交易日均累计走强)；'
    '四个最大单日跌幅(2026-11-05、2026-11-20、2026-11-19、2026-11-16)当日美元兑日元为 -0.07%、+0.20%、-0.08%、-0.06%'
    '——风险资产收缩日的日元波动幅度微小，未见套息平仓式的日元走强。'
    '裁定(限本环预注册窗的区分指标面): 主解释的同窗预期未获支持(窗内 SPX -5.51% 而 USDJPY +1.82%，满足本环预注册的证伪形态)，对质表判断记『支持竞争解释』；'
    '竞争解释的字面预期(时间上解耦)在逐日面只见弱耦合、未获完全确认，不等于确认美国国内定价的因果，整环证据级E3不变。', 'TR2.L1')
sub(T1[0], 'face_off_verdict', '尚不能区分', '支持竞争解释', 'TR2.L1')

# ── #6 / #15 / #12 / #13: turnings ─────────────────────────────────────
sub(TN[0], 'first_mover', '通胀维最大转折=美国CPI同比', '通胀维美欧最大转折=美国CPI同比', 'turnings[0]')
sub(TN[0], 'first_mover', '——三地同窗共振(2026-02 起三地同向上行、',
    '——美欧消费价格与中国生产价格同窗共振(%s，未参与共振；2026-02 起三序列同向上行、' % FLAT, 'turnings[0]')
sub(TN[0], 'follow_or_diverge', '欧元区与中国同向同窗(共振);', '欧元区与中国同向同窗(共振；中国为生产价格口径，消费价格未共振);', 'turnings[0]')
sub(TN[1], 'first_mover', '增长维最大单指标转折=美国工业生产同比自1.7543折半至0.7972(2025-11→2026-02);',
    '增长维美欧最大单指标转折=美国工业生产同比自1.7543折半至0.7972(2025-11→2026-02，引擎候选窗端点；序列同比低点为 2026-03 的 0.69)'
    '(候选面全体首位为中国制造业PMI，增量3.40);', 'turnings[1]')
sub(TN[1], 'first_mover', '(候选窗2026-02→2026-05,z口径 -2.3904→1.0101,候选面原值;',
    '(候选窗2026-02→2026-05,同比%口径 -2.3904→1.0101，取引擎候选面原值；转折表口径栏标签『z口径』为渲染层文案;', 'turnings[1]')
sub(TN[2], 'first_mover', '早于美欧中上行共振起点(2026-02)』', '早于美欧消费价格与中国生产价格上行共振起点(2026-02)』', 'turnings[2]')
sub(TN[2], 'first_mover', '恰为美欧中共振起点月', '恰为美欧消费价格与中国生产价格共振起点月', 'turnings[2]')

# ── #10 / #18: turning supplement ──────────────────────────────────────
sub(TS[0], 'first_mover', '相对美欧中共振窗(2026-02→2026-05)', '相对美欧消费价格与中国生产价格共振窗(2026-02→2026-05)', 'turning_supplement[0]')
sub(TS[0], 'resolution_note', '(当时可见的最近东京读数为 2026-08 的1.9,推定发布2026-08-30)',
    '(当时可见的最近东京读数为 2026-08 的1.9，推定发布 2026-08-31 前后；规则值 2026-08-30 为星期日)', 'turning_supplement[0]')

# ── #3: history sync lead words ────────────────────────────────────────
for h in HP:
    lead = EXPECT[h['anchor_ym']][0]
    sub(h, 'other_regions_sync', lead + ': ', PREFIX[h['anchor_ym']], 'history[%s].other_regions_sync' % h['anchor_ym'])

# ── #7 / #17 / #11 / #12: regional texts ──────────────────────────────
VINT = '(最新修订值、事后回顾口径，非当时首发值'
sub(REG['US'], 'from_to', '即2025Q2→2026Q2→2026Q3)温和放缓;失业率',
    '即2025Q2→2026Q2→2026Q3)温和放缓%s；12个月前锚前最新已发布季度为 2025Q2——2025 年第三季度 GDP 因 2025 年联邦政府停摆延至 2025-12-23 首发，'
    '冻结发布日历实录，较欧元区、日本同锚早一个季度);失业率' % VINT, 'regions[US]')
sub(REG['CN'], 'from_to', '同比口径 -2.2→-0.2→+0.61)',
    '同比口径为指数水平的同比: %s→%s→%s%%，即相差约 %s、%s、%s 个指数点)' % (PMI[0][0], PMI[1][0], PMI[2][0], PMI[0][1], PMI[1][1], PMI[2][1]),
    'regions[CN]')
sub(REG['EA'], 'from_to', '即2025Q3→2026Q2→2026Q3)缓步加速。', '即2025Q3→2026Q2→2026Q3)缓步加速%s)。' % VINT, 'regions[EA]')
sub(REG['EA'], 'from_to', '(2026-08至10加速)', '(2026-08至10月度增量 +0.3/+0.6/+0.2，均高于7月的 +0.1)', 'regions[EA]')
sub(REG['EA'], 'from_to', '最新4.0为四地最高通胀读数之一', '最新4.0为四地消费价格通胀的最高读数(中国PPI同月5.7为生产价格口径)', 'regions[EA]')
sub(REG['EA'], 'from_to',
    '口径注记: 引擎『政策一年窗路径』面板按窗内首观测→窗末观测计净变动，显示净 +25bp(2.25→2.5)，漏计窗启时在值至首个窗内观测的升幅；'
    '按『窗启时在值→窗末观测』口径，窗内净变动为 +50bp(窗启时在值 2.0，2025-06-11 起生效)，与两次生效各 +25bp 之和一致；欧央行两条利率序列止于 2026-09-16(滞后68天)。',
    '口径注记: 引擎『政策一年窗路径』面板按窗内变动点之和计净变动(即『窗启时在值→窗末观测』)，显示净 +50bp(窗启时在值 2.0，2025-06-11 起生效；'
    '窗内变动点 2026-06-17 与 2026-09-16 各 +25bp)，与两次生效各 +25bp 之和一致；自窗内首个观测起算的另一口径为 +25bp，仅作另列；'
    '欧央行两条利率序列止于 2026-09-16(滞后68天)。', 'regions[EA]')
assert (DT.fromisoformat('2026-11-23') - DT.fromisoformat('2026-09-16')).days == 68
sub(REG['JP'], 'from_to', '即2025Q3→2026Q2→2026Q3)持续加速。', '即2025Q3→2026Q2→2026Q3)持续加速%s)。' % VINT, 'regions[JP]')
sub(REG['JP'], 'from_to', '(自 2025-12 月均 0.557 起 +67bp；引擎『政策一年窗路径』面板按窗内首观测起算，显示净 +67bp)',
    '(自 2025-12 月均 0.557 起 +67bp，属另一口径)', 'regions[JP]')

# ── #4 / #19: scenarios ────────────────────────────────────────────────
TRIG_OLD, TRIG_NEW = '(决议日见发布日历实录)', '(生效日=DFEDTARU/ECB_DFR 序列变更日，决议日按引擎惯例自生效日回推【推断】；冻结发布日历暂无两家实录条目)'
for i in range(2):
    sub(SC[i]['rows']['trigger'], 'condition', TRIG_OLD, TRIG_NEW, 'scenarios[%d].trigger' % i)
sub(SC[1]['rows']['falsification'], 'threshold', 'BEI_10Y 跌破1.8且继续下行——',
    'BEI_10Y 跌破1.8且继续下行(阈值依据: 库内最近一次低于 1.8 为 2020-11-30 的 1.77，较最新读数 2.15(2026-11-20)低 35 个基点，作深跌确认线)——',
    'scenarios[1].falsification')

# ── quality notes ──────────────────────────────────────────────────────
END0 = '四地三时点对照的月频指标按观测月取值，日频指标按锚日前最近观测取值。'
Q[0] = rep(Q[0], END0, END0 + '口径注记: 美国实际 GDP 与欧元区、日本实际 GDP 同比的三时点锚格值为最新修订族(事后回顾口径，引擎逐格标注)，'
         '严格历史时点值可能为当期初值，本档未转述首发值；美国 12 个月前锚前最新已发布季度为 2025Q2——2025 年第三季度 GDP 因 2025 年联邦政府停摆延至 2025-12-23 首发'
         '(冻结发布日历实录)。')
LOG.append('[Q0] (appended)\n    + 口径注记: …最新修订族…；2025Q3 GDP 延至 2025-12-23 首发')
sub(Q, 1, '判断=尚不能区分 ×4(逐环两侧相容观测见传导面正文)',
    '判断=主链第1环(冲击环，区分指标 BRENT_F)支持主解释、第2环(政策环)与第3环(利率环→资产环)尚不能区分、竞争链第4环(日本溢出，区分指标 USDJPY)支持竞争解释'
    '(裁定限于各环预注册窗的区分指标面，因果传导仍为【假设】；逐环两侧相容观测与裁定理由见传导面正文)', 'Q1')
sub(Q, 3, '证据引用共 41 条，全部取自本轮冻结快照 research_snapshot_20261123。',
    'L3 证据引用共 41 条(连同 L4 共 50 条、去重 20 项)，全部取自本轮冻结快照 research_snapshot_20261123。', 'Q3')
sub(Q, 4, '①引擎『政策一年窗路径』面板按窗内首观测→窗末观测计净变动，对阶梯序列漏计窗启时在值的升幅——面板值 ECB_DFR +25bp、ECB_MRO +25bp、JP_POLICY_RATE +67bp；'
    '按『窗启时在值→窗末观测』口径为 +50bp、+50bp、+75bp，本档正文采用后者并保留面板值。',
    '①引擎『政策一年窗路径』面板按窗内变动点之和计净变动(即『窗启时在值→窗末观测』)，本轮显示 ECB_DFR +50bp、ECB_MRO +50bp、JP_POLICY_RATE +75bp，'
    '与各生效日逐次变动之和一致，本档正文采用该口径；自窗内首个观测起算的另一口径为 +25bp、+25bp、+67bp，仅作另列。', 'Q4 ①')
sub(Q, 5, '引擎缺口披露(已登记为待裁定残留，本轮未改引擎): ①政策一年窗路径的净变动口径(见上条①)；',
    '引擎缺口披露(①已在本轮代码修正并验证；其余已登记为待裁定残留，本轮未改引擎): ①政策一年窗路径的净变动口径——本轮代码改为按窗内变动点之和计净变动，'
    '点值格存储路径与重算逐位一致(上条①的口径对照据此改写)；', 'Q5 header')
END5 = '欧央行利率序列止于 2026-09-16。'
Q[5] = rep(Q[5], END5, END5 + '⑧转折候选面的变动量按四位小数端点相减显示(如美国核心CPI同比 2026-05→2026-08 记 -0.3767，未舍入差为 -0.3768)，属显示层舍入。')
LOG.append('[Q5] (appended)\n    + ⑧转折候选面的变动量…显示层舍入')

# ── checks ──────────────────────────────────────────────────────────────
assert [l['face_off_verdict'] for l in T0] == ['支持主解释', '尚不能区分', '尚不能区分'] and T1[0]['face_off_verdict'] == '支持竞争解释'
for lk in T0 + T1:
    assert lk['face_off_verdict'] in ('支持主解释', '支持竞争解释', '尚不能区分')
raw = json.dumps(J, ensure_ascii=False)
for bad in ('尚不能区分 ×4', '美欧中', '三地同窗共振', '阶梯', '〖厂商名〗', '〖厂商名〗', '面板按窗内首观测', '面板按窗内首观测→窗末观测', '漏计',
            '本档未做', '决议日见发布日历实录', '最高通胀读数之一', 'z口径 -2.3904', '不可检验,标注【尚未验证】', '通胀维最大转折=', '增长维最大单指标转折='):
    assert bad not in raw, bad
assert J != json.load(open(j_in, encoding='utf-8'))
        # the shutdown-delayed quarter is not an anchor quarter of the US cell: written in words, never as a 2025Q3 token in the US text
assert '2025Q3' not in REG['US']['from_to'] and '2025Q3' in REG['EA']['from_to'] and '2025Q3' in REG['JP']['from_to']
# untouched faces stay byte-identical to the input
J0 = json.load(open(j_in, encoding='utf-8'))
for a, b in zip(J0['l3']['mechanism_chains'], J['l3']['mechanism_chains']):
    assert a['id'] == b['id'] and a['title'] == b['title'] and len(a['links']) == len(b['links'])
    for i, (x, y) in enumerate(zip(a['links'], b['links'])):
        for kk in x:
            if (a['id'], i, kk) not in (('M1', 0, 'text'), ('M1', 1, 'text'), ('M1', 3, 'text'), ('M2', 0, 'text')):
                assert x[kk] == y[kk], (a['id'], i, kk)
        assert set(x) == set(y)
for a, b in zip(J0['l3']['contradictions'], J['l3']['contradictions']):
    assert a['id'] == b['id'] and a['evidence_refs'] == b['evidence_refs'] and set(a) == set(b)
    for i, (x, y) in enumerate(zip(a['competing_explanations'], b['competing_explanations'])):
        if (a['id'], i) not in (('C1', 0), ('C1', 2), ('C3', 2)):
            assert x == y, (a['id'], i)
    assert len(a['competing_explanations']) == len(b['competing_explanations'])
    if a['id'] != 'C1':
        assert a['statement'] == b['statement'], a['id']
for ti, (ca, cb) in enumerate(zip(J0['reader_map']['transmission'], J['reader_map']['transmission'])):
    assert ca['chain_id'] == cb['chain_id'] and ca['title'] == cb['title'] and len(ca['links']) == len(cb['links'])
    for i, (x, y) in enumerate(zip(ca['links'], cb['links'])):
        for kk in x:
            if not (ti == 0 and i == 0 and kk in ('observed_fact', 'causal_hypothesis', 'face_off_verdict')) \
                    and not (ti == 0 and i == 1 and kk in ('observed_fact', 'causal_hypothesis')) \
                    and not (ti == 0 and i == 2 and kk in ('observed_fact', 'causal_hypothesis')) \
                    and not (ti == 1 and i == 0 and kk in ('observed_fact', 'causal_hypothesis', 'face_off_verdict')):
                assert x[kk] == y[kk], (ti, i, kk)
        assert set(x) == set(y)
for a, b in zip(J0['reader_map']['regions'], J['reader_map']['regions']):
    assert a['region'] == b['region'] and a['anchor_echo'] == b['anchor_echo'] and set(a) == set(b)
for i, (a, b) in enumerate(zip(J0['reader_map']['turnings'], J['reader_map']['turnings'])):
    for kk in a:
        if not (i == 0 and kk in ('first_mover', 'follow_or_diverge')) and not (i in (1, 2) and kk == 'first_mover'):
            assert a[kk] == b[kk], (i, kk)
for a, b in zip(J0['reader_map']['turning_supplement'], J['reader_map']['turning_supplement']):
    for kk in a:
        if kk not in ('first_mover', 'resolution_note'):
            assert a[kk] == b[kk], kk
for a, b in zip(J0['reader_map']['history_periods'], J['reader_map']['history_periods']):
    for kk in a:
        if kk != 'other_regions_sync':
            assert a[kk] == b[kk], kk
assert {k: v for k, v in J0['reader_map'].items() if k not in ('headline_conclusion', 'turnings', 'turning_supplement', 'regions', 'transmission', 'history_periods')} == \
    {k: v for k, v in J['reader_map'].items() if k not in ('headline_conclusion', 'turnings', 'turning_supplement', 'regions', 'transmission', 'history_periods')}
for a, b in zip(J0['l4']['scenarios'], J['l4']['scenarios']):
    assert a['id'] == b['id'] and a['role'] == b['role']
    for kk in a['rows']:
        if kk not in ('trigger', 'falsification'):
            assert a['rows'][kk] == b['rows'][kk], kk
    assert a['rows']['trigger']['deadline'] == b['rows']['trigger']['deadline']
    assert a['rows']['falsification']['metric_id'] == b['rows']['falsification']['metric_id'] \
        and a['rows']['falsification']['secondary_metric_ids'] == b['rows']['falsification']['secondary_metric_ids']
assert J0['l4'] == {**J0['l4'], 'scenarios': J0['l4']['scenarios']} and {k: v for k, v in J0['l4'].items() if k != 'scenarios'} == \
    {k: v for k, v in J['l4'].items() if k != 'scenarios'}
assert J0['quality_gate_notes'][2] == Q[2]
for k in J0:
    if k not in ('l3', 'l4', 'quality_gate_notes', 'reader_map'):
        assert J0[k] == J[k], k
for k in J0['l3']:
    if k not in ('contradictions', 'mechanism_chains'):
        assert J0['l3'][k] == J['l3'][k], k
with open(j_out, 'w', encoding='utf-8') as fh:
    json.dump(J, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
rawb = open(j_out, 'rb').read()
print('wrote', j_out, len(rawb), 'bytes sha16', hashlib.sha256(rawb).hexdigest()[:16], '| run', RID,
      '| git_head', (R.get('git_head') or '')[:12], '| STRICT', STRICT)
print('replacements', len(LOG))
print('\n'.join(LOG))
print('=== residual contexts')
for w in ('面板', '首观测', '+67', '三地', '尚不能区分', '最大', '不可检验'):
    for m in __import__('re').finditer(__import__('re').escape(w), raw):
        print('  [%s] …%s…' % (w, raw[max(0, m.start() - 28):m.end() + 28].replace('\n', ' ')))
