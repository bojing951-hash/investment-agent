#!/usr/bin/python3
"""fold_N305.py <judgment_in.json> <tree> <run_dir> <judgment_out.json> [--expect-new-engine]

Builder revision of the NEW30 work-order judgment (Japan / euro area inflation
and policy environment, last six months) after (a) the independent review it
received at the superseded stamp 0f3936d (UPHELD: 0 MAJOR / 7 MINOR / 10 NIT
— precision and disclosure items) and (b) the engine fix that makes the
policy-window net change equal the sum of its change points (window start =
value in effect at window start).  The work order is re-planned at the new
stamp; the frozen inputs are the same collection, so every number quoted in a
replacement sentence is recomputed here from the run's own frozen inputs
(root_overlay snapshot / release calendar / report.json) and asserted before
the text is written.  Read-only on the run directory.  `tree` is the
acceptance tree whose engine code the run used (publish-rule and
policy-window helpers are imported from it read-only).

Folded: reviewer items #0-#16 of VERDICT-round1 at 0f3936d (same-caliber
policy gap, VIX close-basis precedent, release-day checks inside the jump
window, scenario falsification symmetry, candidate-selection reason,
revision-vintage scope, Tokyo publish-rule caveat, cross-rate arithmetic,
policy-level caliber, calendar record count) and the policy-window net
change (+75bp = sum of six change points; the pre-fix report carried +67bp).

Builder fixes beyond that review's items (disclosed in the acceptance
receipt): (1) the EURUSD face-off verdict changes from "supports the
competing explanation" to "cannot separate" — the reasoning is the one the
sibling T3 work order's round-1 review raised as MAJOR class B on an
identical link (the main explanation's direction-split prediction left out
the dollar-side rate, which is above both regions' rates, so both
explanations predict both currencies weakening against the dollar in this
window); (2) the FOMC minutes record the engine itself lists (published
inside the VIX jump window) is named as a third candidate driver the
face-off does not adjudicate.  Pre-registered prediction texts are left
unchanged and the correction is explained in the verdict notes.
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
tk = FR.monthly('JP_CPI_TOKYO_YOY')
pr = FR.monthly('JP_POLICY_RATE')
assert (ea['2026-10'], ea['2026-09'], ea['2026-08'], ea['2026-07'], ea['2026-06'], ea['2026-05']) == (4.0, 3.8, 3.2, 2.9, 2.8, 3.2)
assert (jp['2026-10'], jp['2026-09'], jp['2026-08'], jp['2026-07'], jp['2026-06'], jp['2026-05']) == (2.44, 2.16, 1.98, 1.97, 1.67, 1.53)

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
cells = {c['metric_id']: c for c in FR.rep['research_plan']['point_values']['cells']}
stored = cells['JP_POLICY_RATE'].get('policy_window_path') or {}
if STRICT or stored.get('window_start_observation'):
    assert stored == wp, 'stored policy window differs from the recomputed post-fix window'
else:
    print('NOTE: run dir carries the pre-fix policy window (net %d bp, window start %s); '
          'text quotes the post-fix caliber' % (stored.get('net_bp'), stored.get('window_start_value')))
# six-month anchors between 2026-04 and 2026-10: 0.727 -> 1.227 (+50bp)
assert pr['2026-04'] == 0.727 and round((pr['2026-10'] - pr['2026-04']) * 100) == 50

# #0 GDP rows: in the registry, listed by Gate A as missing, series face has readings
det = FR.snap['gate_a']['noncore_missing_detail']
for m, v, n in (('EA_REAL_GDP_YOY', 1.28, 123), ('JP_REAL_GDP_YOY', 1.16, 127)):
    assert '采集器已取到而事实未生成' in det[m]
    assert m in FR.snap['gate_a']['noncore_missing']
    assert FR.registry_metric(m) is not None
    assert len(ss[m]['dates']) == n and ss[m]['dates'][-1] == '2026-07-01' and ss[m]['values'][-1] == v
GDP_TXT = '序列面存有至 2026-07 期读数(欧元区%s、日本%s),按 Gate A 不取用' % (
    cn_num(1.28), cn_num(1.16))

# #1 / #15 / #16 policy level, rhythm and calendar records
cal = FR.cal['entries']
jp_rec = [e for e in cal if e.get("metric_id") == "JP_POLICY_TARGET"]
assert [e['entry_id'] for e in jp_rec] == ['RC-JP-BOJ-TARGET-2026-09', 'RC-JP-BOJ-MAINT-2026-10']
assert all(e['basis'] == 'user_directive' and e['target_value'] == 1.25 for e in jp_rec)
tg = jp_rec[0]
assert (tg['decision_date'], tg['effective_on'], tg['kind']) == ('2026-09-18', '2026-09-24', 'policy_decision')
assert jp_rec[1]['kind'] == 'policy_maintenance' and 'effective_on' not in jp_rec[1]
D = datetime.date
assert (D(2026, 9, 24) - D(2026, 9, 16)).days == 8 and (D(2026, 9, 18) - D(2026, 9, 10)).days == 8
assert (D(2026, 9, 18) - D(2026, 9, 16)).days == 2
assert FR.last_date('ECB_MRO') == FR.last_date('ECB_DFR') == '2026-09-16'
assert FR.val('ECB_MRO', FR.as_of) == 2.65 and FR.val('ECB_DFR', FR.as_of) == 2.5
assert cn_num(2.65 - 1.25) == '一点四' and cn_num(2.5 - 1.25) == '一点二五'

# #3 / #12 calendar records: three historical EA HICP flash/final records, none for this window,
# zero for the ECB
ea_rec = [e for e in cal if e.get("metric_id") == "EA_HICP_YOY"]
assert [e['entry_id'] for e in ea_rec] == ['RC-EA-HICP-2021M05', 'RC-EA-HICP-2022M06', 'RC-EA-HICP-2025M03']
for e in ea_rec:
    fp = D.fromisoformat(e['first_publish_on_or_after'])
    assert fp.day == 1 and (fp.year, fp.month) == (int(e['obs_from'][:4]) + (int(e['obs_from'][5:7]) == 12),
                                                  int(e['obs_from'][5:7]) % 12 + 1)
    assert e['obs_from'] < '2026-05-01'
assert not [e for e in cal if e.get("metric_id") in ('ECB_MRO', 'ECB_DFR') or 'ECB' in e['entry_id']]
assert FR.cal['version'] == '1.5.0' and len(cal) == 18
# sensitivity of the "2.9 below the 3.2 peak" observation to the release-pattern shape:
# flash on the 1st of the next month -> latest visible before each back-cast decision date
def visible_flash(decision):
    ym = None
    for k in sorted(ea):
        nxt = k[:4] + '-%02d' % (int(k[5:7]) % 12 + 1) if k[5:7] != '12' else str(int(k[:4]) + 1) + '-01'
        if nxt <= decision:
            ym = k
    return ym, ea[ym]
assert visible_flash('2026-06-11') == ('2026-05', 3.2) and visible_flash('2026-09-10') == ('2026-08', 3.2)
# engine rule (mid-next-month final value): 2026-07=2.9 visible before the back-cast 2026-09-10
assert rmp._visible_publish('EA_HICP_YOY', 'monthly', '2026-07-01')[0] == '2026-08-16'
assert rmp._visible_publish('EA_HICP_YOY', 'monthly', '2026-08-01')[0] == '2026-09-16'
assert rmp._visible_publish('EA_HICP_YOY', 'monthly', '2026-10-01')[0] == '2026-11-16'
assert rmp._visible_publish('JP_CPI_YOY', 'monthly', '2026-10-01')[0] == '2026-11-20'
assert (D(2026, 6, 17) - D(2025, 6, 11)).days == 371

# #2 / #5 / #7 VIX close-basis precedent, release days inside the jump window
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
# policy-day distances in the verdict note are counted from the jump start 2026-11-13
assert ((D(2026, 11, 13) - D(2026, 10, 30)).days, (D(2026, 11, 13) - D(2026, 9, 16)).days) == (14, 58)
assert ((D(2026, 11, 20) - D(2026, 10, 30)).days, (D(2026, 11, 20) - D(2026, 9, 16)).days) == (21, 65)

# #6 turning candidates
cands = FR.rep['research_plan']['turning_candidates']['candidates']
c0 = cands[0]
assert (c0['metric_id'], c0['from_ym'], c0['to_ym'], c0['value_before'], c0['value_after'], c0['delta']) == (
    'JP_CPI_YOY', '2025-11', '2026-02', 2.9, 1.27, -1.63)
assert all(abs(c['delta']) <= 1.63 for c in cands) and len(cands) == 4
assert (jp['2025-11'], jp['2026-02']) == (2.9, 1.27)
assert [t['metric_id'] for t in J['reader_map']['turnings']] == ['EA_HICP_YOY', 'JP_POLICY_RATE', 'JP_CPI_TOKYO_YOY']

# #8 vintage semantics of the point-value cells
for m, want in (('EA_HICP_YOY', '事后回顾'), ('JP_CPI_YOY', '事后回顾'), ('JP_CPI_TOKYO_YOY', 'as_collected'),
                ('JP_POLICY_RATE', 'as_collected'), ('ECB_MRO', 'as_collected'), ('ECB_DFR', 'as_collected')):
    assert cells[m]['vintage_semantics'].startswith(want), (m, cells[m]['vintage_semantics'])

# #9 path shape
assert (jp['2025-01'], jp['2025-08'], jp['2025-09'], jp['2025-10'], jp['2026-02']) == (4.03, 2.72, 2.91, 2.99, 1.27)

# #10 window membership of the 2026-05 observation
assert FR.date('EA_HICP_YOY', '2026-05-31') == '2026-05-01' < '2026-05-23'
assert rmp._visible_publish('EA_HICP_YOY', 'monthly', '2026-05-01')[0] == '2026-06-16'
assert ['2026-06-16' <= rmp._visible_publish('EA_HICP_YOY', 'monthly', ym + '-01')[0] <= FR.as_of
         for ym in ('2026-06', '2026-07', '2026-08', '2026-09', '2026-10')] == [True] * 5

# #11 Tokyo publish rule vs the engine's own official anchors (last Fridays)
tpub = {ym: rmp._visible_publish('JP_CPI_TOKYO_YOY', 'monthly', ym + '-01')[0]
        for ym in ('2026-06', '2026-08', '2026-09', '2026-10')}
assert tpub == {'2026-06': '2026-06-29', '2026-08': '2026-08-30', '2026-09': '2026-09-29', '2026-10': '2026-10-30'}
assert D(2026, 8, 30).weekday() == 6 and D(2026, 6, 26).weekday() == 4 and D(2026, 10, 30).weekday() == 4
assert D(2026, 6, 26) == max(d for d in (D(2026, 6, x) for x in range(1, 31)) if d.weekday() == 4)
assert D(2026, 10, 30) == max(d for d in (D(2026, 10, x) for x in range(1, 32)) if d.weekday() == 4)
assert tk['2026-08'] == 1.9 and tk['2026-09'] == 2.69
assert '2026-08-28' < '2026-09-18' < '2026-09-25'      # last-Friday pattern: conclusion unchanged
assert max(d for d in (D(2026, 8, x) for x in range(1, 32)) if d.weekday() == 4).isoformat() == '2026-08-28'
assert max(d for d in (D(2026, 9, x) for x in range(1, 31)) if d.weekday() == 4).isoformat() == '2026-09-25'

# #13 momentum sensitivity to the start month
assert cn_num(ea['2026-10'] - ea['2026-06']) == '一点二' and cn_num(jp['2026-10'] - jp['2026-06']) == '零点七七'
assert cn_num(ea['2026-10'] - ea['2026-05']) == '零点八' and cn_num(jp['2026-10'] - jp['2026-05']) == '零点九一'
assert cn_num(ea['2026-10'] - ea['2026-04']) == '一点' and cn_num(jp['2026-10'] - jp['2026-04']) == '一点零六'

# #14 cross rate from the two on-face series
X0 = FR.val('EURUSD', '2026-10-23') * FR.val('USDJPY', '2026-10-23')
X1 = FR.val('EURUSD', '2026-11-20') * FR.val('USDJPY', '2026-11-20')
X2 = FR.val('EURUSD', '2026-11-23') * FR.val('USDJPY', '2026-11-23')
assert FR.date('EURUSD', '2026-11-23') == '2026-11-23' and FR.date('USDJPY', '2026-11-20') == '2026-11-20'
assert ('%.2f' % X0, '%.2f' % X1, '%.2f' % X2) == ('175.61', '175.19', '174.32')
assert X1 < X0 and X2 < X0
assert ('%.2f' % pct(X0, X1), '%.2f' % pct(X0, X2)) == ('-0.24', '-0.73')

# USD leg of the rate differential (same reasoning as the sibling T3 work order's
# round-1 review, MAJOR class B): the main explanation's "direction split"
# prediction left out the dollar-side rate
assert FR.last_date('UST_10Y') == '2026-11-19' and FR.val('UST_10Y', FR.as_of) == 5.04
for m, hi in (('DFEDTARU', 4.0), ('DFEDTARL', 3.75)):
    assert FR.last_date(m) == FR.as_of and ss[m]['values'][-1] == hi
    assert not [k for k in range(1, len(ss[m]['dates'])) if ss[m]['values'][k] != ss[m]['values'][k - 1]
                and ss[m]['dates'][k] > '2026-09-17']            # no change point inside the one-month window
assert FR.val('ECB_MRO', FR.as_of) < 4.0 and 5.04 > FR.val('ECB_MRO', FR.as_of)   # dollar-side rate above both
pdf = FR.rep['research_plan'].get('policy_doc_facts') or []
assert [(d['doc_id'], d['kind'], d['published_on']) for d in pdf] == [('FOMC-MINUTES-2026-10', 'minutes', '2026-11-18')]
assert '2026-11-13' <= '2026-11-18' <= '2026-11-20'              # minutes published inside the jump window

RM = J['reader_map']
C = {c['id']: c for c in J['l3']['contradictions']}
T = RM['transmission'][0]['links']
LK = J['l3']['mechanism_chains'][0]['links']
S = {s['id']: s for s in J['l4']['scenarios']}
Q = J['quality_gate_notes']
REG = {r['region']: r for r in RM['regions']}
assert [c['id'] for c in J['l3']['contradictions']] == ['C1-INFL-DIVERGE', 'C2-POLICY-SYNC-LEVEL-GAP', 'C3-EVIDENCE-GAPS']
assert [l['distinguishing_metric'] for l in T] == ['EA_HICP_YOY', 'EURUSD', 'VIX']
assert [l['face_off_verdict'] for l in T] == ['尚不能区分', '支持竞争解释', '尚不能区分']

# ── engine-fix ripple: policy-window net change ────────────────────────
sub(REG['JP'], 'from_to',
    '近 12 个月月均由 2025-11 的 0.478 升至 2026-10 的 1.227,约 +75bp;引擎政策窗净 +67bp,窗口 2025-11-23..2026-11-23)',
    '近 12 个月月均由 2025-11 的 0.478 升至 2026-10 的 1.227,约 +75bp;引擎政策一年窗路径同口径——窗启时在值 0.478(2025-11 月均)'
    '→窗末 1.227(2026-10 月均),净 +75bp=六个变动点之和,窗口 2025-11-23..2026-11-23)', 'regions[JP]')
sub(Q, 4, 'JP_POLICY_RATE=月均市场口径≠宣布值(六个月锚间、近 12 个月与引擎政策窗三种净变动口径并列)',
    'JP_POLICY_RATE=月均市场口径≠宣布值(净变动两种口径并列: 六个月锚间为一口径,近 12 个月月均与引擎政策一年窗路径为同口径'
    '——窗启时在值→窗末,等于变动点之和)', 'quality_gate_notes[4]')

# ── #0 GDP background rows: fact rows missing, series present ──────────
sub(C['C3-EVIDENCE-GAPS'], 'statement',
    '⑤增长与核心通胀背景缺席: EA_REAL_GDP_YOY、JP_REAL_GDP_YOY 在册但列于快照缺席名单,两地「政策环境」无法对照增长背景;',
    '⑤增长与核心通胀背景对照缺席: EA_REAL_GDP_YOY、JP_REAL_GDP_YOY 在册,但当日快照 Gate A 列于缺席名单'
    '(事实行缺席,注记=采集器已取到而事实未生成;' + GDP_TXT + '),两地「政策环境」无法对照增长背景;', 'C3⑤')
# ── #8 revision-vintage scope (C3④, headline, note)
sub(C['C3-EVIDENCE-GAPS'], 'statement',
    '④月度数值为事后回顾口径(最新修订值,非当时首发值),当时信息集不可重构。',
    '④欧元区 HICP 与日本全国 CPI 月度数值为事后回顾口径(最新修订值,非当时首发值),东京 CPI 与月均拆借利率为采集时点值'
    '(是否首发值未核),当时信息集不可重构。', 'C3④')
sub(Q, 4, '月度值为事后回顾修订口径。', '欧元区 HICP 与日本全国 CPI 月度值为事后回顾修订口径(东京 CPI 与月均拆借利率为采集时点值)。',
    'quality_gate_notes[4]')
sub(RM, 'headline_conclusion',
    '月度值为事后回顾修订口径、增长与核心通胀背景序列缺席(GDP 两序列在册但快照缺席,注册表无核心通胀)。',
    '欧元区 HICP 与日本全国 CPI 月度值为事后回顾修订口径、增长与核心通胀背景对照缺席'
    '(GDP 两序列在册、当日快照事实行缺席,注册表无核心通胀)。', 'headline')
# ── #3 calendar records (C3③) / #16 record count (C3①)
sub(C['C3-EVIDENCE-GAPS'], 'statement',
    '③通胀公布时间为推定规则非实录(Eurostat/总务省全国/东京都/BOJ 月均各有推定规则,随报告表格层披露;日历实录仅覆盖日本政策目标两条)。',
    '③本窗月度通胀读数的公布时间为推定规则非实录(Eurostat/总务省全国/东京都/BOJ 月均各有推定规则,随报告表格层披露;'
    '冻结日历实录仅覆盖日本政策目标两条与三条历史期 EA HICP 快报/终值实录,观测月 2021-05、2022-06、2025-03,均不覆盖本窗月份;'
    '东京都推定规则给出的部分月份推定日与引擎自列官方实录锚的「当月最后一个周五」形态不完全一致,可见性结论不受影响)。', 'C3③')
sub(C['C3-EVIDENCE-GAPS'], 'statement',
    '对照以月均市场口径替代+发布日历实录单条(user_directive 基础)。',
    '对照以月均市场口径替代+发布日历实录两条(目标值决议一条、维持确认一条,均 user_directive 基础)。', 'C3①')
# ── #1 same-caliber policy rhythm / #15 policy-level caliber (C2)
sub(C['C2-POLICY-SYNC-LEVEL-GAP'], 'statement',
    '日央行 2026-09-18 决议即 2026-09-24 生效在后,相隔两天,日级日期可排(欧央行决议日仅惯例回推,不参与排序);',
    '日央行 2026-09-18 决议(2026-09-24 生效)在后,同口径相隔八天(生效日对生效日;按引擎回推的决议日计亦为八天),'
    '日级日期可排(欧央行决议日仅惯例回推,不参与排序);', 'C2')
sub(C['C2-POLICY-SYNC-LEVEL-GAP'], 'statement',
    '水平对照: 最新政策利率欧元区高于日本约一点二五个百分点(DFR 二点五 vs BOJ 目标约一点二五)。',
    '水平对照: 最新政策利率欧元区高于日本——按 MRO 计约一点四、按 DFR 计约一点二五个百分点'
    '(二点六五/二点五 vs BOJ 目标约一点二五)。', 'C2')
# ── JP tightening direction is an inference; post-2026-10-30 record gap (same finding as the sibling
# T3 work order's round-1 review, MINOR #9) ──
assert (D(2026, 11, 23) - D(2026, 10, 30)).days == 24
assert cn_num(0.478, 3) == '零点四七八' and cn_num(1.227, 3) == '一点二二七'
sub(C['C2-POLICY-SYNC-LEVEL-GAP'], 'statement', '2026-10-30 会议确认维持不变。',
    '2026-10-30 会议确认维持不变;日本端「收紧」方向依据月均市场利率台阶(自 2025-11 月均零点四七八升至 2026-10 月均一点二二七),'
    '实录无前值,属【推断】;2026-10-30 至研究截止二十四天内的后续决议面不在实录【尚未验证】。', 'C2')
# ── #13 momentum sensitivity (C1)
sub(C['C1-INFL-DIVERGE'], 'statement',
    '均约一个百分点——「水平与同比方向分化、窗内动量不分化」。',
    '均约一个百分点(起点=六个月前锚;自 2026-06 期起算则为欧元区一点二个百分点对日本零点七七个百分点,'
    '自 2026-05 期起算为欧元区零点八对日本零点九一,快慢互换)——「水平与同比方向分化、窗内动量不分化」。', 'C1')
# ── #4 / #12 scenario falsification symmetry and verifiability of the policy leg
S1, S2 = S['S1-DIVERGE-PERSIST']['rows'], S['S2-CONVERGE']['rows']
for R in (S1, S2):
    for k in ('trigger', 'falsification'):
        assert R[k]['condition' if k == 'trigger' else 'threshold'].count('以决议实录核验') == 1
sub(S1['falsification'], 'threshold', '以决议实录核验',
    '以决议实录核验(欧央行分量须待发布日历补录 ECB 实录后方可核验)', 'S1.falsification')
sub(S1['trigger'], 'condition', '以决议实录核验',
    '以决议实录核验(欧央行分量须待发布日历补录 ECB 实录后方可核验)', 'S1.trigger')
sub(S2['falsification'], 'threshold',
    '若观测月 2026-11 与 2026-12 两月 EA_HICP_YOY 同比均不低于 3.5%(未回落),「以一次性因素为主、回落至 3.0% 以下」的前提被证伪;',
    '若观测月 2026-11 与 2026-12 两月 EA_HICP_YOY 同比均不低于 3.5%(未回落),「以一次性因素为主、回落至 3.0% 以下」的前提被证伪;'
    '或两月日本全国 CPI 同比均不低于 2.0%,或两月两地水平差(欧元区减日本)均不低于 1.0 个百分点,收敛情景的日本端/水平差分量同样被证伪;',
    'S2.falsification')
sub(S2['falsification'], 'threshold', '以决议实录核验',
    '以决议实录核验(欧央行分量须待发布日历补录 ECB 实录后方可核验)', 'S2.falsification')
sub(S2['trigger'], 'condition',
    '(均为前提水平,且各自较 2026-11 观测月回落),同时 VIX 在该读数入档日前最近一个交易日收盘低于 25;',
    '(均为前提水平,且各自较 2026-11 观测月回落,且两地水平差(欧元区减日本)不超过 1.0 个百分点),'
    '同时 VIX 在该读数入档日前最近一个交易日收盘低于 25;', 'S2.trigger')
sub(S2['trigger'], 'condition', '以决议实录核验',
    '以决议实录核验(欧央行分量须待发布日历补录 ECB 实录后方可核验)', 'S2.trigger')
sub(Q, 3, '政策分量(再上调/按兵不动)不设数值触发,以决议实录核验。',
    '政策分量(再上调/按兵不动)不设数值触发,以决议实录核验(冻结日历对欧央行零条实录,欧央行分量须待日历补录后方可核验;'
    '日本端两条实录可核)。', 'quality_gate_notes[3]')
# ── S2 falsification threshold looser than its premise level (same finding as the sibling T3 work
# order's round-1 review, MINOR #8): disclosed, design unchanged ──
assert '回落至 3.0% 以下' in S['S2-CONVERGE']['rows']['scenario'] and '不低于 3.5%' in S2['falsification']['threshold']
assert '低于 3.0%' in S2['trigger']['condition']
sub(Q, 3, '证伪阈值与前提水平对齐(3.5%/2.0%/水平差 1.5 个百分点);政策分量',
    'S1 证伪阈值与前提水平对齐(3.5%/2.0%/水平差 1.5 个百分点);S2 证伪阈值(3.5%)较前提水平(3.0% 以下)放宽,3.0%–3.5% 区间不触发亦不证伪;'
    '政策分量', 'quality_gate_notes[3]')
# ── #3 sensitivity of the reverse observation (link 0 verdict note)
sub(T[0], 'verdict_note',
    '且第二次变更的决议日前可见读数 2.9 低于 2026-05 峰值 3.2。',
    '且第二次变更的决议日前可见读数 2.9 低于 2026-05 峰值 3.2——该条对发布规则形态敏感: 若按冻结日历所载 EA HICP 历史实录的'
    '「次月首日快报+月中终值」两档形态计,两次变更决议日前可见读数为 2026-05 的 3.2 与 2026-08 的 3.2,此条反向观察不成立'
    '(另一条 371 天反向观察不受影响)。', 'transmission[0].links[0]')
# ── #2 / #5 / #7 VIX link: close-basis precedent, release days, attribution marker
PREC = ('2026-11-04→11-05 VIX 收盘 16.61→28.18(+69.66%),至 11-11 回落至 17.49(四个交易日,较 11-05 -37.93%),'
        '同期 SPX 11-05 -4.36%,下一交易日 NIKKEI225 11-06 -5.96%,与「冲击主导、快速回落」相容')
REL = ('跳升窗内含两条推定读数发布日(2026-11-16、2026-11-20,当日 VIX +18.70%/+26.20%,为窗内两个最大单日跳升日),'
       '但窗内四地股指跌幅均不深于美股(2026-11-13→2026-11-20: SPX -8.61%、NIKKEI225 -7.70%、DAX -7.28%、CAC40 -5.27%),'
       '两日欧元、日元对美元单日变动幅度不超过 0.23%,读数发布主因未获跨地区支持')
# engine-side policy-document record (minutes, not a decision) inside the jump window
FOMC = ('同页引擎面另列 FOMC 2026年10月会议纪要 2026-11-18 发布(纪要发布≠决议日;美国端政策日历事件),落在跳升窗内,'
        '属第三类候选驱动,本对质(两地政策日历 vs 数据发布)不裁')
sub(T[2], 'verdict_note',
    '但其『快速回落』预期仅有一个盘中观测(2026-11-23 快照 27.01,较 2026-11-20 收盘 -24.7%,非收盘),',
    '但其『快速回落』预期在本跳升上仅有一个盘中观测(2026-11-23 快照 27.01,较 2026-11-20 收盘 -24.7%,非收盘),'
    '同窗另有一次收盘口径先例——' + PREC + ';', 'transmission[0].links[2]')
sub(T[2], 'verdict_note', '距 ECB 最近生效日 2026-09-16 58 天。',
    '距 ECB 最近生效日 2026-09-16 58 天(两距均自跳升起点 2026-11-13 计,至跳升终点 2026-11-20 为 21 天、65 天);'
    + REL + ';' + FOMC + '。', 'transmission[0].links[2]')
sub(LK[3], 'text',
    '两种叙事均相容;VIX 跳升时点',
    '两种叙事均相容【假设·归因】;同窗先例: ' + PREC + ';' + REL + ';'
    '引擎面另列 FOMC 2026年10月会议纪要 2026-11-18 发布,落在跳升窗内,属第三类候选驱动【假设·归因】;VIX 跳升时点',
    'chain[0].links[3]')
# ── #10 window membership of the 2026-05 observation (chain link 0)
sub(LK[0], 'text', '窗内(2026-05..2026-10 月度值)',
    '2026-05..2026-10 月度值(2026-05 期观测日在窗起 2026-05-23 之前、推定发布日在窗内;2026-06..2026-10 期在窗内)', 'chain[0].links[0]')
# ── #14 cross rate from the two on-face series
sub(LK[2], 'text',
    '传导【假设】: 若政策利差主导汇率,两地同向收紧但水平差(MRO 2.65% vs BOJ 目标 1.25%)应体现于 EURUSD/USDJPY 方向分立——'
    '本月窗两口径下两货币同对美元走弱、同向随美元指数,方向分立未出现,美元全局主导的竞争解释在本月窗获支持'
    '(置信有限;EURJPY 交叉盘不在证据面,利差渠道不可直接检验)。',
    '传导【假设】: 若政策利差主导汇率,两地同向收紧但水平差(MRO 2.65% vs BOJ 目标 1.25%)应体现于 EURUSD/USDJPY 方向分立——'
    '但该预期未纳入美元端利率(UST_10Y 最新 5.04%,高于 MRO 2.65% 与 BOJ 目标约 1.25%),利差主导对本月窗同样预期两货币对美元走弱;'
    '本月窗两口径下两货币同对美元走弱、同向随美元指数,两解释在该观测上预期未分立——尚不能区分'
    '(置信有限;EURJPY 交叉盘不在证据面,以 EURUSD×USDJPY 推算: 2026-10-23 收盘 175.61→2026-11-20 收盘 175.19(-0.24%)、'
    '至 2026-11-23 盘中 174.32(较 10-23 -0.73%),幅度小,利差渠道未获检验亦未被否定)。', 'chain[0].links[2]')
# ── #14 cross rate from the two on-face series; EURUSD face-off verdict corrected ──
# (USD-side rate left out of the main explanation's prediction — same finding as the
# sibling T3 work order's round-1 review, MAJOR class B): both explanations predict
# both currencies weakening against the dollar in this window -> cannot separate
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
# ── #6 candidate not adopted as a turning
sub(RM['turnings'][0], 'follow_or_diverge', '——跟进方向一致,月频先后未定。',
    '——跟进方向一致,月频先后未定。引擎候选面另列日本全国 CPI 2025-11→2026-02(2.9→1.27,三个月 -1.63 个百分点)为幅度最大候选,'
    '未列入三转折: 该回落主要发生在六个月窗(起 2026-05-23)之前,谷底已在走位中写明。', 'turnings[EA]')
# ── #9 path shape (JP walk)
sub(REG['JP'], 'from_to', '自 2025-01 高点 4.03 持续回落至 2026-02 的 1.27,此后总体回升。',
    '自 2025-01 高点 4.03 总体回落(2025-09、2025-10 两月小幅回升至 2.91、2.99)至 2026-02 的 1.27,此后总体回升。', 'regions[JP]')
# ── #11 Tokyo publish rule caveat
sub(RM['turnings'][2], 'follow_or_diverge', '(推定发布 2026-08-30)。',
    '(推定发布 2026-08-30;该推定日落在周日,与引擎自列官方实录锚 2026-06-26、2026-10-30 的当月最后一个周五形态不完全一致,'
    '可见性结论不受影响)。', 'turnings[Tokyo]')

# ── invariants ─────────────────────────────────────────────────────────
old = json.load(open(j_in, encoding='utf-8'))
assert J['agent_declaration'] == old['agent_declaration']
assert J['schema_version'] == old['schema_version']
for a, b in zip(old['l3']['contradictions'], J['l3']['contradictions']):
    assert a['id'] == b['id'] and a['evidence_refs'] == b['evidence_refs'] and a['competing_explanations'] == b['competing_explanations']
for a, b in zip(old['reader_map']['regions'], J['reader_map']['regions']):
    assert a['anchor_echo'] == b['anchor_echo']
for a, b in zip(old['l4']['scenarios'], J['l4']['scenarios']):
    assert a['id'] == b['id'] and a['rows']['sensitive_variables'] == b['rows']['sensitive_variables']
assert S['S1-DIVERGE-PERSIST']['rows']['trigger']['condition'] != old['l4']['scenarios'][0]['rows']['trigger']['condition']  # policy-leg note added
assert [l['face_off_verdict'] for l in T] == ['尚不能区分', '尚不能区分', '尚不能区分']
assert [l['face_off_verdict'] for l in old['reader_map']['transmission'][0]['links']] == ['尚不能区分', '支持竞争解释', '尚不能区分']
for a, b in zip(old['reader_map']['transmission'][0]['links'], T):
    assert a['main_predicts'] == b['main_predicts'] and a['competing_predicts'] == b['competing_predicts']   # pre-registered predictions unchanged
for k in ('narrative',):
    for a, b in zip(old['reader_map']['turnings'], RM['turnings']):
        assert a[k] == b[k]
assert J != old
with open(j_out, 'w', encoding='utf-8') as fh:
    json.dump(J, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
raw = open(j_out, 'rb').read()
print('wrote', j_out, len(raw), 'bytes sha16', hashlib.sha256(raw).hexdigest()[:16])
print('replacements', len(LOG))
print('\n'.join(LOG))
