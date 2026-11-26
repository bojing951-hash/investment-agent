#!/usr/bin/python3
"""fold_T35.py <judgment_in.json> <tree> <run_dir> <judgment_out.json> [--expect-new-engine]

Builder revision of the T3 work-order judgment (Japan / euro area inflation and
policy environment, official target rates, pending decisions, year-on-year
comparison) after (a) the independent review it received at the superseded
stamp 0f3936d (REVISE: 6 MAJOR rows in 2 classes / 5 MINOR / 5 NIT) and (b)
the engine fixes (policy-window net change = sum of its change points; actual
anchor labels; reader-page Gate A status line).  Every number quoted in a
replacement sentence is recomputed here from the run's own frozen inputs
(root_overlay snapshot / release calendar / report.json) and asserted before
the text is written.  Read-only on the run directory.  `tree` is the
acceptance tree whose engine code the run used (publish-rule and
policy-window helpers are imported from it read-only).

Folded:
  MAJOR-A  #0  euro-area trough month (2026-01 1.7, not 2026-02 1.9)
  MAJOR-B  #1-#5  EURUSD face-off: the main explanation's direction-split
               prediction left out the dollar-side rate (above both regions'
               rates), so both explanations predict both currencies weakening
               against the dollar in this window -> cannot separate; verdict
               note, observed fact (cross rate synthesizable from the two
               legs), chain link, face-off counts
  MINOR    #6  headline direction caliber (year-on-year only)
           #7  UST_10Y is a market yield; policy caliber = Fed band (not in
               this round's evidence index)
           #8  S2 falsification threshold looser than its premise level
           #9  Japan's tightening direction rests on the market-rate steps
               (inference); decisions after 2026-10-30 not in the record
           #10 FOMC minutes record (published inside the VIX jump window)
  NIT      #11 who turns first depends on the ordering caliber
           #12 "spliced" -> registry wording
           #13 "sustained decline" is not monotone
           #14 VIX close-basis precedent inside the window
  engine   #15 reader-page Gate A status line (engine fix, not a judgment edit)

Also folded from the sibling NEW30 work order's round-1 review, where the
same text appears in this judgment: release-day checks inside the jump
window, ECB leg of the policy component not verifiable until the calendar
carries ECB records, sensitivity of the "2.9 below the 3.2 peak" reverse
observation to the release-pattern shape, scenario falsification symmetry
for the Japan leg, attribution markers on the chain's link 4.
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

FR = L.Frozen(rd)
ss = FR.ss
RID = FR.rep['run']['ts_utc']
J = copy.deepcopy(json.load(open(j_in, encoding='utf-8')))
assert J['agent_declaration']['produced_by'].count(RID) == 1, RID
LOG = []


def rep(s, old, new, n=1):
    assert s.count(old) == n, ('anchor count', s.count(old), n, old[:48])
    return s.replace(old, new)


def sub(obj, key, old, new, where):
    obj[key] = rep(obj[key], old, new)
    LOG.append('[%s] %s\n    - %s\n    + %s' % (where, key, old, new))


def pct(a, b):
    return (b / a - 1.0) * 100.0


def dchg(mid, day):
    """daily % change at the observation dated `day` vs its previous observation."""
    assert FR.date(mid, day) == day, (mid, day, FR.date(mid, day))
    return pct(FR.val(mid, FR.prev_obs_date(mid, day)), FR.val(mid, day))


def cn_num(x, nd=2):
    """number -> Chinese numerals, e.g. 1.2 -> 一点二, 0.77 -> 零点七七, 1.25 -> 一点二五."""
    D = '零一二三四五六七八九'
    t = ('%.' + str(nd) + 'f') % float(x)
    ip, fp = t.split('.')
    assert ip == '0' or len(ip) == 1, t
    out = D[int(ip)] + '点' + ''.join(D[int(c)] for c in fp.rstrip('0'))
    return out


# ── computed facts (frozen inputs of this run) ─────────────────────────
assert FR.as_of == '2026-11-23'
ea = FR.monthly('EA_HICP_YOY')
jp = FR.monthly('JP_CPI_YOY')
pr = FR.monthly('JP_POLICY_RATE')
assert (ea['2026-10'], ea['2026-09'], ea['2026-08'], ea['2026-07'], ea['2026-06'], ea['2026-05']) == (4.0, 3.8, 3.2, 2.9, 2.8, 3.2)

# MAJOR-A: trough month of the euro-area series
w12 = {k: v for k, v in ea.items() if '2025-11' <= k <= '2026-10'}
assert min(w12, key=w12.get) == '2026-01' and ea['2026-01'] == 1.7 and ea['2026-02'] == 1.9
assert min((v, k) for k, v in ea.items() if k >= '2025-01')[1] == '2026-01'          # also the 2025-to-date trough
assert ea['2026-10'] == max(w12.values())                                            # latest = 12-month high
assert ea['2026-05'] == 3.2 and ea['2026-06'] == 2.8 and ea['2026-04'] == 3.0 and ea['2025-10'] == 2.1
# MINOR #6: both series rose from the six-month-ago anchor (2026-04)
assert jp['2026-04'] == 1.38 and jp['2026-10'] == 2.44 and ea['2026-04'] == 3.0

# policy window (engine fix): net = sum of change points, start = value in effect at window start
s = ss['JP_POLICY_RATE']
wp = rmp._policy_window_path(s['dates'], s['values'], FR.as_of, metric_id='JP_POLICY_RATE',
                             carry_start=True)
assert wp['window'] == ['2025-11-23', '2026-11-23']
assert wp['window_start_value'] == 0.478 and wp['window_start_observation'] == '2025-11-01'
assert wp['window_end_value'] == 1.227 and FR.last_date('JP_POLICY_RATE') == '2026-10-01'
assert len(wp['events']) == 6 and sum(e['delta_bp'] for e in wp['events']) == 75 == wp['net_bp']
assert [e['delta_bp'] for e in wp['events']] == [8, 17, 11, 14, 7, 18]
assert round((pr['2026-10'] - pr['2025-11']) * 100) == 75          # "近 12 个月月均 … 约 +75bp"
assert (pr['2026-09'], pr['2026-10'], pr['2026-04'], pr['2026-07']) == (1.043, 1.227, 0.727, 0.978)
assert jp['2026-05'] == 1.53 and jp['2025-10'] == 2.99                         # turnings text already in the judgment
cells = {c['metric_id']: c for c in FR.rep['research_plan']['point_values']['cells']}
stored = cells['JP_POLICY_RATE'].get('policy_window_path') or {}
if STRICT or stored.get('window_start_observation'):
    assert stored == wp, 'stored policy window differs from the recomputed post-fix window'
else:
    print('NOTE: run dir carries the pre-fix policy window (net %d bp, window start %s); '
          'text quotes the post-fix caliber' % (stored.get('net_bp'), stored.get('window_start_value')))
assert cn_num(0.478, 3) == '零点四七八' and cn_num(1.227, 3) == '一点二二七'

# policy levels / calendar records (JP two records; ECB none)
cal = FR.cal['entries']
jp_rec = [e for e in cal if e.get("metric_id") == "JP_POLICY_TARGET"]
assert [e['entry_id'] for e in jp_rec] == ['RC-JP-BOJ-TARGET-2026-09', 'RC-JP-BOJ-MAINT-2026-10']
tg = jp_rec[0]
assert (tg['decision_date'], tg['effective_on'], tg['kind'], tg['target_value']) == (
    '2026-09-18', '2026-09-24', 'policy_decision', 1.25)
assert jp_rec[1]['kind'] == 'policy_maintenance' and jp_rec[1]['decision_date'] == '2026-10-30' \
    and 'effective_on' not in jp_rec[1] and all(e['basis'] == 'user_directive' for e in jp_rec)
assert not [e for e in cal if e.get("metric_id") in ('ECB_MRO', 'ECB_DFR') or 'ECB' in e['entry_id']]
ea_rec = [e for e in cal if e.get("metric_id") == "EA_HICP_YOY"]
assert [e['entry_id'] for e in ea_rec] == ['RC-EA-HICP-2021M05', 'RC-EA-HICP-2022M06', 'RC-EA-HICP-2025M03']
D = datetime.date
assert (D(2026, 11, 23) - D(2026, 10, 30)).days == 24
assert FR.last_date('ECB_MRO') == FR.last_date('ECB_DFR') == '2026-09-16'
assert FR.val('ECB_MRO', FR.as_of) == 2.65 and FR.val('ECB_DFR', FR.as_of) == 2.5


def visible_flash(decision):
    ym = None
    for k in sorted(ea):
        nxt = k[:4] + '-%02d' % (int(k[5:7]) % 12 + 1) if k[5:7] != '12' else str(int(k[:4]) + 1) + '-01'
        if nxt <= decision:
            ym = k
    return ym, ea[ym]


assert visible_flash('2026-06-11') == ('2026-05', 3.2) and visible_flash('2026-09-10') == ('2026-08', 3.2)
assert rmp._visible_publish('EA_HICP_YOY', 'monthly', '2026-07-01')[0] == '2026-08-16'
assert rmp._visible_publish('EA_HICP_YOY', 'monthly', '2026-08-01')[0] == '2026-09-16'
assert rmp._visible_publish('EA_HICP_YOY', 'monthly', '2026-10-01')[0] == '2026-11-16'
assert rmp._visible_publish('JP_CPI_YOY', 'monthly', '2026-10-01')[0] == '2026-11-20'
assert rmp._visible_publish('EA_HICP_YOY', 'monthly', '2026-12-01')[0] == '2027-01-16'   # both before the 2027-02-15 deadline
assert rmp._visible_publish('JP_CPI_YOY', 'monthly', '2026-12-01')[0] == '2027-01-20'

# VIX close-basis precedent, release days inside the jump window, FOMC minutes record
assert (FR.val('VIX', '2026-11-04'), FR.val('VIX', '2026-11-05'), FR.val('VIX', '2026-11-11')) == (16.610001, 28.18, 17.49)
assert len([d for d in ss['VIX']['dates'] if '2026-11-05' < d <= '2026-11-11']) == 4
P1, P2 = pct(16.610001, 28.18), pct(28.18, 17.49)
assert '%.2f' % P1 == '69.66' and '%.2f' % P2 == '-37.93'
assert '%.2f' % dchg('SPX', '2026-11-05') == '-4.36'
assert ('%.2f' % dchg('NIKKEI225', '2026-11-05'), '%.2f' % dchg('NIKKEI225', '2026-11-06')) == ('-1.79', '-5.96')
assert FR.prev_obs_date('VIX', '2026-11-13') == '2026-11-12' and '2026-11-05' > '2026-10-23'
JUMP = {m: FR.ret(m, '2026-11-13', '2026-11-20') for m in ('SPX', 'NIKKEI225', 'DAX', 'CAC40')}
assert tuple('%.2f' % JUMP[m] for m in ('SPX', 'NIKKEI225', 'DAX', 'CAC40')) == ('-8.61', '-7.70', '-7.28', '-5.27')
assert all(JUMP[m] > JUMP['SPX'] for m in ('NIKKEI225', 'DAX', 'CAC40'))   # no regional drop deeper than the US
V = ss['VIX']
daily = {d: pct(V['values'][k - 1], V['values'][k]) for k, d in enumerate(V['dates']) if '2026-11-13' <= d <= '2026-11-20' and k}
assert ('%.2f' % daily['2026-11-16'], '%.2f' % daily['2026-11-20']) == ('18.70', '26.20')
assert sorted(daily, key=lambda d: -daily[d])[:2] == ['2026-11-20', '2026-11-16']
FXD = max(abs(dchg(m, d)) for m in ('EURUSD', 'USDJPY') for d in ('2026-11-16', '2026-11-20'))
assert '%.2f' % FXD == '0.23'
assert (FR.val('VIX', '2026-11-13'), FR.val('VIX', '2026-11-20')) == (19.299999, 35.889999)
assert ((D(2026, 11, 13) - D(2026, 10, 30)).days, (D(2026, 11, 13) - D(2026, 9, 16)).days) == (14, 58)
assert ((D(2026, 11, 20) - D(2026, 10, 30)).days, (D(2026, 11, 20) - D(2026, 9, 16)).days) == (21, 65)
pdf = FR.rep['research_plan'].get('policy_doc_facts') or []
assert [(d['doc_id'], d['kind'], d['published_on']) for d in pdf] == [('FOMC-MINUTES-2026-10', 'minutes', '2026-11-18')]
assert '2026-11-13' <= '2026-11-18' <= '2026-11-20'              # minutes published inside the jump window
assert ['%.2f' % FR.val('VIX', d) for d in ('2026-11-18', '2026-11-19', '2026-11-20')] == ['24.56', '28.44', '35.89']

# USD leg of the rate differential (MAJOR-B): dollar-side rate above both regions' rates
assert FR.last_date('UST_10Y') == '2026-11-19' and FR.val('UST_10Y', FR.as_of) == 5.04
for m, hi in (('DFEDTARU', 4.0), ('DFEDTARL', 3.75)):
    assert FR.last_date(m) == FR.as_of and ss[m]['values'][-1] == hi
    assert not [k for k in range(1, len(ss[m]['dates'])) if ss[m]['values'][k] != ss[m]['values'][k - 1]
                and ss[m]['dates'][k] > '2026-09-17']            # no change point inside the one-month window
assert 4.0 > FR.val('ECB_MRO', FR.as_of) and 5.04 > FR.val('ECB_MRO', FR.as_of)

# NIT #13 path shape
assert (jp['2025-01'], jp['2025-08'], jp['2025-09'], jp['2025-10'], jp['2025-11'], jp['2026-02'], jp['2025-07']) == (
    4.03, 2.72, 2.91, 2.99, 2.9, 1.27, 3.1)
assert min((v, k) for k, v in jp.items() if k >= '2025-01')[1] == '2026-02'

# NIT #11 ordering calibers: trough months vs engine candidate-face turning dates
cands = FR.rep['research_plan']['turning_candidates']['candidates']
cm = {c['metric_id']: c for c in cands}
assert cm['JP_CPI_YOY']['to_ym'] == '2026-02' and cm['EA_HICP_YOY']['to_ym'] == '2026-05'
assert (cm['JP_CPI_YOY']['from_ym'], cm['JP_CPI_YOY']['value_before'], cm['JP_CPI_YOY']['value_after']) == ('2025-11', 2.9, 1.27)
assert (cm['EA_HICP_YOY']['from_ym'], cm['EA_HICP_YOY']['value_after']) == ('2026-02', 3.2)
assert ea['2025-11'] == 2.1

# #14 cross rate from the two on-face series
X0 = FR.val('EURUSD', '2026-10-23') * FR.val('USDJPY', '2026-10-23')
X1 = FR.val('EURUSD', '2026-11-20') * FR.val('USDJPY', '2026-11-20')
X2 = FR.val('EURUSD', '2026-11-23') * FR.val('USDJPY', '2026-11-23')
assert FR.date('EURUSD', '2026-11-23') == '2026-11-23' and FR.date('USDJPY', '2026-11-20') == '2026-11-20'
assert ('%.2f' % X0, '%.2f' % X1, '%.2f' % X2) == ('175.61', '175.19', '174.32')
assert X1 < X0 and X2 < X0
assert ('%.2f' % pct(X0, X1), '%.2f' % pct(X0, X2)) == ('-0.24', '-0.73')

RM = J['reader_map']
C = {c['id']: c for c in J['l3']['contradictions']}
T = RM['transmission'][0]['links']
LK = J['l3']['mechanism_chains'][0]['links']
S = {s['id']: s for s in J['l4']['scenarios']}
Q = J['quality_gate_notes']
REG = {r['region']: r for r in RM['regions']}
assert [c['id'] for c in J['l3']['contradictions']] == ['C1-INFL-DIVERGE', 'C2-POLICY-SYNC', 'C3-ECB-VISIBILITY']
assert [l['distinguishing_metric'] for l in T] == ['EA_HICP_YOY', 'EURUSD', 'VIX']
assert [l['face_off_verdict'] for l in T] == ['尚不能区分', '支持竞争解释', '尚不能区分']
assert [t['metric_id'] for t in RM['turnings']] == ['JP_CPI_YOY', 'EA_HICP_YOY', 'JP_POLICY_RATE']
assert list(S) == ['S1-STICKY-TIGHTEN', 'S2-INFL-FADE']

# ── engine-fix ripple: policy-window net change ────────────────────────
sub(REG['JP'], 'from_to',
    '近 12 个月月均由 2025-11 的 0.478 升至 2026-10 的 1.227,约 +75bp;引擎政策窗净 +67bp,窗口 2025-11-23..2026-11-23)',
    '近 12 个月月均由 2025-11 的 0.478 升至 2026-10 的 1.227,约 +75bp;引擎政策一年窗路径同口径——窗启时在值 0.478(2025-11 月均)'
    '→窗末 1.227(2026-10 月均),净 +75bp=六个变动点之和,窗口 2025-11-23..2026-11-23)', 'regions[JP]')
sub(Q, 4, 'JP_POLICY_RATE=月均市场口径≠宣布值(近 12 个月与引擎政策窗两种净变动口径并列)',
    'JP_POLICY_RATE=月均市场口径≠宣布值(净变动两种口径并列: 六个月锚间为一口径,近 12 个月月均与引擎政策一年窗路径为同口径'
    '——窗启时在值→窗末,等于变动点之和)', 'quality_gate_notes[4]')

# ── MAJOR-A #0: trough month ────────────────────────────────────────────
sub(REG['EA'], 'from_to',
    '路径: 2026-02 谷底 1.9→2026-05 3.2→2026-06 2.8→2026-10 4.0,最新读数为近十二个月最高',
    '路径: 2026-01 谷底 1.7→2026-02 1.9→2026-05 3.2→2026-06 2.8→2026-10 4.0,最新读数为近十二个月最高', 'regions[EA]')

# ── MAJOR-B #1-#5 (+#7): EURUSD face-off verdict ───────────────────────
sub(T[1], 'causal_hypothesis', '(高政策利率货币相对走强)。',
    '(高政策利率货币相对走强;该预期未纳入美元端利率——见裁定理由)。', 'transmission[0].links[1]')
sub(T[1], 'observed_fact', 'EURJPY 交叉盘不在证据面,利差假说的直接检验(欧元相对日元走强)不可做。',
    'EURJPY 交叉盘序列不在证据面,但可由同日 EURUSD×USDJPY 两腿合成: 由 2026-10-23 的约 175.61 降至 2026-11-20 的约 175.19'
    '(-0.24%)、2026-11-23 盘中约 174.32(-0.73%),幅度小;本月窗两地政策水平差未变,利差假说对交叉盘方向无明确预期,'
    '该面不构成检验。', 'transmission[0].links[1]')
assert T[1]['face_off_verdict'] == '支持竞争解释'
T[1]['face_off_verdict'] = '尚不能区分'
LOG.append('[transmission[0].links[1]] face_off_verdict\n    - 支持竞争解释\n    + 尚不能区分')
sub(T[1], 'verdict_note',
    '本月窗两种口径(至 2026-11-20 收盘、至 2026-11-23 盘中快照)一致: 欧元与日元同对美元走弱并同向随美元指数,主解释预期的『方向分立』未出现、'
    '竞争解释(美元全局主导)的预期出现——支持竞争解释。置信有限: 仅一个月窗;主解释的预期未纳入美元端利率(UST_10Y 最新 5.04%);'
    'EURJPY 交叉盘缺席致利差渠道不可直接检验,方向对质仅限对美元口径。',
    '本月窗两种口径(至 2026-11-20 收盘、至 2026-11-23 盘中快照)一致: 欧元与日元同对美元走弱并同向随美元指数;但主解释预期的『方向分立』'
    '未纳入美元端利率——引擎面美元端利率高于两地(UST_10Y 最新 5.04%,市场收益率口径;快照序列面联邦基金目标区间 3.75%–4.00%,'
    'DFEDTARL/DFEDTARU 2026-11-23 观测,不在本轮证据索引),利差主导解释对本月窗同样预期两货币对美元走弱,两解释在区分指标 EURUSD 上'
    '预期未分立——尚不能区分。置信有限: 仅一个月窗、窗内三地均无政策利率变动点(序列面最近变动: 欧央行 2026-09-16 生效、美联储 '
    '2026-09-17 生效;日央行 2026-09-18 决议 2026-09-24 生效,2026-10-30 会议为维持不变);EURJPY 交叉盘序列不在证据面,由同日 '
    'EURUSD×USDJPY 两腿合成的交叉盘至 2026-11-20 约 -0.24%、至 2026-11-23 约 -0.73%,幅度小,利差渠道未获检验亦未被否定。',
    'transmission[0].links[1]')
sub(Q, 1, '支持主解释 0·支持竞争解释 1·尚不能区分 2', '支持主解释 0·支持竞争解释 0·尚不能区分 3', 'quality_gate_notes[1]')
sub(LK[2], 'text',
    '传导【假设】: 若政策利差主导汇率,两地同向收紧但水平差(MRO 2.65% vs BOJ 目标 1.25%)应体现于 EURUSD/USDJPY 方向分立——'
    '本月窗两口径下两货币同对美元走弱、同向随美元指数,方向分立未出现,美元全局主导的竞争解释在本月窗获支持'
    '(置信有限;EURJPY 交叉盘不在证据面,利差渠道不可直接检验)。',
    '传导【假设】: 若政策利差主导汇率,两地同向收紧但水平差(MRO 2.65% vs BOJ 目标 1.25%)应体现于 EURUSD/USDJPY 方向分立——'
    '但该预期未纳入美元端利率(UST_10Y 最新 5.04%,高于 MRO 2.65% 与 BOJ 目标约 1.25%),利差主导对本月窗同样预期两货币对美元走弱;'
    '本月窗两口径下两货币同对美元走弱、同向随美元指数,两解释在该观测上预期未分立——尚不能区分'
    '(置信有限;EURJPY 交叉盘不在证据面,以 EURUSD×USDJPY 推算: 2026-10-23 收盘 175.61→2026-11-20 收盘 175.19(-0.24%)、'
    '至 2026-11-23 盘中 174.32(较 10-23 -0.73%),幅度小,利差渠道未获检验亦未被否定)。', 'chain[0].links[2]')

# ── MINOR #6: headline direction caliber ───────────────────────────────
sub(RM, 'headline_conclusion', '2026 年 11 月,日本与欧元区通胀环境方向相反——',
    '2026 年 11 月,日本与欧元区通胀同比相比去年同月方向相反(较六个月前锚两地读数均上行)——', 'headline')

# ── MINOR #8: S2 falsification threshold vs premise; Japan-leg symmetry ─
S1, S2 = S['S1-STICKY-TIGHTEN']['rows'], S['S2-INFL-FADE']['rows']
for R in (S1, S2):
    for k in ('trigger', 'falsification'):
        assert R[k]['condition' if k == 'trigger' else 'threshold'].count('以决议实录核验') == 1
assert '2026-12 观测月读数低于 3.0%(前提水平)' in S2['trigger']['condition']
ECB_LEG = '以决议实录核验(冻结日历对欧央行零条实录,欧央行分量须待日历补录后方可核验;日本端两条实录可核)'
sub(S1['falsification'], 'threshold', '以决议实录核验', ECB_LEG, 'S1.falsification')
sub(S1['trigger'], 'condition', '以决议实录核验', ECB_LEG, 'S1.trigger')
sub(S2['falsification'], 'threshold',
    '「以一次性因素为主、回落至 3.0% 以下」的前提被证伪;政策分量(按兵不动)不设数值触发,以决议实录核验',
    '「以一次性因素为主、回落至 3.0% 以下」的前提被证伪(证伪阈值 3.5% 较前提水平放宽,3.0%–3.5% 区间不触发亦不证伪);'
    '或 2026-12 观测月日本全国 CPI 同比不低于 2.0%,收敛情景的日本端分量同样被证伪;政策分量(按兵不动)不设数值触发,'
    '以决议实录核验(冻结日历对欧央行零条实录,欧央行分量须待日历补录后方可核验;日本端两条实录可核)', 'S2.falsification')
sub(S2['trigger'], 'condition',
    '2026-12 观测月读数低于 3.0%(前提水平),同时 VIX 在该读数入档日前最近一个交易日收盘低于 25;政策分量(ECB 按兵不动/BOJ 维持)不设数值触发,以决议实录核验',
    '2026-12 观测月读数低于 3.0%(前提水平),且 2026-12 观测月 JP_CPI_YOY 同比低于 2.0%(日本端分量前提水平),'
    '同时 VIX 在两读数均入档之日前最近一个交易日收盘低于 25;政策分量(ECB 按兵不动/BOJ 维持)不设数值触发,'
    '以决议实录核验(冻结日历对欧央行零条实录,欧央行分量须待日历补录后方可核验;日本端两条实录可核)', 'S2.trigger')
sub(Q, 3, '证伪阈值与前提水平对齐(3.5%);政策分量(再上调/按兵不动)不设数值触发,以决议实录核验。',
    'S1 证伪阈值与前提水平对齐(3.5%);S2 证伪阈值(3.5%)较前提水平(3.0% 以下)放宽,3.0%–3.5% 区间不触发亦不证伪;'
    '政策分量(再上调/按兵不动)不设数值触发,以决议实录核验(冻结日历对欧央行零条实录,欧央行分量须待日历补录后方可核验;'
    '日本端两条实录可核)。', 'quality_gate_notes[3]')

# ── MINOR #9: Japan's tightening direction is an inference; post-2026-10-30 record gap ──
sub(C['C2-POLICY-SYNC'], 'statement', '2026-10-30 会议确认维持不变(无新调整、无生效变动)',
    '2026-10-30 会议确认维持不变(无新调整、无生效变动);日本端「收紧」方向依据月均市场利率台阶(自 2025-11 月均零点四七八升至 '
    '2026-10 月均一点二二七),实录无前值,属【推断】;2026-10-30 至研究截止二十四天内的后续决议面不在实录【尚未验证】', 'C2')

# ── MINOR #10 (+#14, release days, attribution marker): VIX link ───────
PREC = ('2026-11-04→11-05 VIX 收盘 16.61→28.18(+69.66%),至 11-11 回落至 17.49(四个交易日,较 11-05 -37.93%),'
        '同期 SPX 11-05 -4.36%,下一交易日 NIKKEI225 11-06 -5.96%,与「冲击主导、快速回落」相容')
REL = ('跳升窗内含两条推定读数发布日(2026-11-16、2026-11-20,当日 VIX +18.70%/+26.20%,为窗内两个最大单日跳升日),'
       '但窗内四地股指跌幅均不深于美股(2026-11-13→2026-11-20: SPX -8.61%、NIKKEI225 -7.70%、DAX -7.28%、CAC40 -5.27%),'
       '两日欧元、日元对美元单日变动幅度不超过 0.23%,读数发布主因未获跨地区支持')
FOMC = ('同页引擎面另列 FOMC 2026年10月会议纪要 2026-11-18 发布(纪要发布≠决议日;美国端政策日历事件),落在跳升窗内,'
        '发布当日及其后两个交易日 VIX 收盘 24.56、28.44、35.89,属第三类候选驱动,本对质(两地政策日历 vs 数据发布)不裁')
sub(T[2], 'verdict_note', '距 ECB 最近生效日 2026-09-16 58 天。',
    '距 ECB 最近生效日 2026-09-16 58 天(两距均自跳升起点 2026-11-13 计,至跳升终点 2026-11-20 为 21 天、65 天);'
    + REL + ';' + FOMC + '。', 'transmission[0].links[2]')
sub(T[2], 'verdict_note',
    '但其『快速回落』预期仅有一个盘中观测(2026-11-23 快照 27.01,较 2026-11-20 收盘 -24.7%,非收盘),',
    '但其『快速回落』预期在本跳升上仅有一个盘中观测(2026-11-23 快照 27.01,较 2026-11-20 收盘 -24.7%,非收盘),'
    '同窗另有一次收盘口径先例——' + PREC + ';', 'transmission[0].links[2]')
sub(LK[3], 'text',
    '两种叙事均相容;VIX 跳升时点',
    '两种叙事均相容【假设·归因】;同窗先例: ' + PREC + ';' + REL + ';'
    '引擎面另列 FOMC 2026年10月会议纪要 2026-11-18 发布,落在跳升窗内,属第三类候选驱动【假设·归因】;VIX 跳升时点',
    'chain[0].links[3]')

# ── sensitivity of the "2.9 below the 3.2 peak" reverse observation (link 0 verdict note) ──
sub(T[0], 'verdict_note',
    '且第二次变更的决议日前可见读数 2.9 低于 2026-05 峰值 3.2。',
    '且第二次变更的决议日前可见读数 2.9 低于 2026-05 峰值 3.2——该条对发布规则形态敏感: 若按冻结日历所载 EA HICP 历史实录的'
    '「次月首日快报+月中终值」两档形态计,两次变更决议日前可见读数为 2026-05 的 3.2 与 2026-08 的 3.2,此条反向观察不成立'
    '(另一条 371 天反向观察不受影响)。', 'transmission[0].links[0]')
assert (D(2026, 6, 17) - D(2025, 6, 11)).days == 371

# ── NIT #11: ordering calibers ─────────────────────────────────────────
sub(RM['turnings'][0], 'follow_or_diverge', ';月频下谁先转折不可判。',
    ';按谷底月欧元区(2026-01)先于日本(2026-02)一个月转入上行,按引擎候选面转折日(区间终点月)则为日本(2026-02)先于欧元区'
    '(2026-05)——两种排序口径不同,以口径为准。', 'turnings[JP_CPI]')

# ── NIT #12: registry wording ──────────────────────────────────────────
sub(LK[0], 'text', 'spliced', '拼接', 'chain[0].links[0]')
sub(Q, 4, 'spliced', '拼接', 'quality_gate_notes[4]')

# ── NIT #13: path shape is not monotone ────────────────────────────────
sub(LK[0], 'text', 'JP_CPI_YOY 自 2025-01 高点 4.03 持续回落,经 2025-07 的 3.1 至 2026-02 的 1.27,此后总体回升(非逐月单调)至 2026-10 的 2.44。',
    'JP_CPI_YOY 自 2025-01 高点 4.03 回落(非逐月单调,2025-09、2025-10 两度小幅回升至 2.91、2.99),经 2025-07 的 3.1 至 2026-02 的 '
    '1.27,此后总体回升至 2026-10 的 2.44。', 'chain[0].links[0]')
sub(REG['JP'], 'from_to', '自 2025-01 高点 4.03 持续回落至 2026-02 的 1.27,此后总体回升',
    '自 2025-01 高点 4.03 回落(2025-09、2025-10 两度小幅回升至 2.91、2.99)至 2026-02 的 1.27,此后总体回升', 'regions[JP]')

# ── engine residual ⑤ (anchor-label hard-coding) is fixed at the new stamp ──
if STRICT:
    sub(Q, 5, '引擎缺口披露(非本档判断问题,五项): ', '引擎缺口披露(非本档判断问题,四项): ', 'quality_gate_notes[5]')
    sub(Q, 5, ';⑤引擎报告文字「三个对照时点=截止日−12月/−3月」与本问 6 个月前锚不一致(引擎渲染残留,本档按点值格实际锚表述)。',
        '。', 'quality_gate_notes[5]')

# ── invariants ─────────────────────────────────────────────────────────
old = json.load(open(j_in, encoding='utf-8'))
assert J['agent_declaration'] == old['agent_declaration']
assert J['schema_version'] == old['schema_version']
for a, b in zip(old['l3']['contradictions'], J['l3']['contradictions']):
    assert a['id'] == b['id'] and a['evidence_refs'] == b['evidence_refs'] and a['competing_explanations'] == b['competing_explanations']
for a, b in zip(old['reader_map']['regions'], J['reader_map']['regions']):
    assert a['anchor_echo'] == b['anchor_echo']
for a, b in zip(old['l4']['scenarios'], J['l4']['scenarios']):
    assert a['id'] == b['id'] and a['rows']['sensitive_variables'] == b['rows']['sensitive_variables'] \
        and a['rows']['scenario'] == b['rows']['scenario']
assert S['S1-STICKY-TIGHTEN']['rows']['trigger']['condition'] != old['l4']['scenarios'][0]['rows']['trigger']['condition']
assert [l['face_off_verdict'] for l in T] == ['尚不能区分', '尚不能区分', '尚不能区分']
assert [l['face_off_verdict'] for l in old['reader_map']['transmission'][0]['links']] == ['尚不能区分', '支持竞争解释', '尚不能区分']
for a, b in zip(old['reader_map']['transmission'][0]['links'], T):
    assert a['main_predicts'] == b['main_predicts'] and a['competing_predicts'] == b['competing_predicts']   # pre-registered predictions unchanged
for a, b in zip(old['reader_map']['turnings'], RM['turnings']):
    assert a.get('narrative') == b.get('narrative')
assert J != old
with open(j_out, 'w', encoding='utf-8') as fh:
    json.dump(J, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
raw = open(j_out, 'rb').read()
print('wrote', j_out, len(raw), 'bytes sha16', hashlib.sha256(raw).hexdigest()[:16])
print('replacements', len(LOG))
print('\n'.join(LOG))
