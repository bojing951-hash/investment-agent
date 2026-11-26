#!/usr/bin/python3 -I
"""fold_B5.py <judgment_in.json> <tree> <run_dir> <judgment_out.json> [--expect-new-engine]

Builder revision of the B work-order judgment (US / euro-area growth and
inflation environment vs three months ago, re-phrased question) after (a) the
independent review it received at the superseded stamp 0f3936d (REVISE:
1 MAJOR / 5 MINOR / 10 NIT) and (b) the engine fixes (policy-window net
change = sum of its change points; reader-page Gate A status line; the
"reviewed" wording of the reader report follows the verdict state).  Every
number quoted in a replacement sentence is recomputed here from the run's
own frozen inputs (root_overlay snapshot / release calendar / evidence
index / report.json) and asserted before the text is written.  Read-only on
the run directory.  `tree` is the tree whose engine code the helpers are
imported from (read-only).

Folded:
  MAJOR  #0  S1 falsification was literally untriggerable before 2027-01
             (only one EA HICP release after the cutoff falls before that
             date, and the reading adjacent to it is already 4.0)
  MINOR #1  the cross-over of the US / euro-area inflation ranking is
             historical (2022-07..2023-09), not recent
        #2  the earlier BEI_10Y rise runs from the window low to the peak
        #3  "rate differential still high" is an assumption (no series)
        #4  energy premise vs the on-face oil reading
        #5  "to 2027-01" = release month (2026-12 observation month)
  NIT   #6  which funding-cost series the engine lacks
        #7  % unit on the BOJ target in the headline
        #8  common-window SPX change next to the mixed-endpoint figure
        #9  link 2 has no separating metric
        #10 S1 premise: region reference and assumption marker
        #13 "growth" = hard data
        #14 same-month US / ECB policy changes in the series store
  NIT #15 (Arabic numerals in the L3 statement) is NOT adopted: those
        metrics carry no text alias, so Arabic numerals would leave the
        contract's number binding (unbound token); registered residual.
  NIT #11 (procedural statement) needs no edit; NIT #12 (template wording)
        is an engine fix, not a judgment edit.
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
R = FR.rep['run']
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


def cn_num(x, nd=2):
    """number -> Chinese numerals, e.g. 1.2 -> 一点二, 0.478 -> 零点四七八."""
    D = '零一二三四五六七八九'
    t = ('%.' + str(nd) + 'f') % float(x)
    ip, fp = t.split('.')
    assert ip == '0' or len(ip) == 1, t
    return D[int(ip)] + '点' + ''.join(D[int(c)] for c in fp.rstrip('0'))


def cn_int(n):
    """0..99 -> Chinese numerals (六十, 六十六, 七十五)."""
    D = '零一二三四五六七八九'
    if n < 10:
        return D[n]
    return (D[n // 10] if n >= 20 else '') + '十' + (D[n % 10] if n % 10 else '')


# ── computed facts (frozen inputs of this run) ─────────────────────────
assert FR.as_of == '2026-11-23'
D = datetime.date
ea = FR.monthly('EA_HICP_YOY')
cpi = FR.monthly('CPI')
core = FR.monthly('CORE_CPI')
pr = FR.monthly('JP_POLICY_RATE')

# MAJOR: EA HICP release dates around the cutoff; only one post-cutoff release before 2027-01
pub = {m: rmp._visible_publish('EA_HICP_YOY', 'monthly', m + '-01')[0]
       for m in ('2026-10', '2026-11', '2026-12')}
assert pub == {'2026-10': '2026-11-16', '2026-11': '2026-12-16', '2026-12': '2027-01-16'}
assert pub['2026-10'] <= FR.as_of < pub['2026-11']            # 2026-10 reading is already out
assert ea['2026-10'] == 4.0 and 4.0 >= 3.0                    # the adjacent reading cannot be "below 3.0"
assert FR.last_date('EA_HICP_YOY') == '2026-10-01'
assert '2027-01' > pub['2026-11'] and pub['2026-11'] < '2027-01' <= pub['2026-12']   # exactly one release in (cutoff, 2027-01)
assert pub['2026-12'] <= '2027-02-15'                           # both premise months inside the deadline

# MINOR #1: ranking of the two inflation readings over the comparable months
def yoy(m, d):
    pm = '%04d-%02d' % (int(m[:4]) - 1, int(m[5:7]))
    return (d[m] / d[pm] - 1.0) * 100.0 if pm in d else None


cy = {m: yoy(m, cpi) for m in cpi}
comp = [m for m in sorted(cy) if cy[m] is not None and m in ea]
above = [m for m in comp if round(ea[m], 2) > round(cy[m], 2)]
assert len(comp) == 106 and (comp[0], comp[-1]) == ('2017-11', '2026-09')
assert above == ['2022-%02d' % k for k in range(7, 13)] + ['2023-%02d' % k for k in range(1, 10)] + ['2026-09']
assert not [m for m in comp if '2023-10' <= m <= '2026-08' and m in above]
assert (round(ea['2026-09'], 2), round(cy['2026-09'], 2)) == (3.8, 3.72)
assert cy['2026-10'] is None and FR.last_date('CPI') == '2026-10-01'     # missing base period
assert (round(ea['2026-10'], 2), round(ea['2026-07'], 2)) == (4.0, 2.9) and round(cy['2026-09'], 2) == 3.72 \
    and round(cy['2026-07'], 2) == 3.3 and round(cy['2026-05'], 2) == 4.17

# MINOR #2: earlier BEI_10Y rise = window low -> window peak
b = ss['BEI_10Y']
bw = [(d, v) for d, v in zip(b['dates'], b['values']) if '2026-02-20' <= d <= '2026-05-04']
assert (bw[0][0], bw[-1][0]) == ('2026-02-20', '2026-05-04')
assert min(bw, key=lambda t: t[1]) == ('2026-02-27', 2.25) and max(bw, key=lambda t: t[1]) == ('2026-05-04', 2.5)
assert FR.year_high('BEI_10Y', 2026) == ('2026-05-04', 2.5)
assert FR.val('BEI_10Y', '2026-05-29') == 2.38 and FR.date('BEI_10Y', '2026-05-29') == '2026-05-29'
assert round((2.38 - 2.25) * 100) == 13
assert ('%.2f' % FR.ret('BEI_10Y', '2026-08-19', '2026-11-19')) == '-6.09'          # -14bp (level diff)
assert round((FR.val('BEI_10Y', '2026-11-19') - FR.val('BEI_10Y', '2026-08-19')) * 100) == -14
assert FR.val('BEI_10Y', '2026-11-20') == 2.15 and FR.last_date('BEI_10Y') == '2026-11-20'

# MINOR #3: USDJPY percentile inside the 12-month window
u = ss['USDJPY']
uw = [(d, v) for d, v in zip(u['dates'], u['values']) if '2025-11-23' <= d <= '2026-11-23']
assert uw[-1] == ('2026-11-23', 159.347)
UPCT = round(100.0 * sum(1 for d, v in uw if v < uw[-1][1]) / len(uw))
assert UPCT == 71 and len(uw) == 259

# MINOR #4: oil reading on the evidence face
ei = json.load(open(os.path.join(rd, 'evidence_index.json'), encoding='utf-8'))
assert 'BRENT_F@2026-11-23' in [r['ref'] for r in ei]
assert FR.date('BRENT_F', '2026-11-23') == '2026-11-23'
O1, O3, O12 = FR.ret('BRENT_F', '2026-10-23', '2026-11-23'), FR.ret('BRENT_F', '2026-08-19', '2026-11-23'), \
    FR.ret('BRENT_F', '2025-11-19', '2026-11-23')
assert ('%.2f' % O1, '%.2f' % O3, '%.2f' % O12) == ('-24.44', '-3.74', '38.86')
assert (FR.val('BRENT_F', '2026-08-19'), FR.val('BRENT_F', '2026-10-23'), round(FR.val('BRENT_F', '2026-11-23'), 2)) == (
    91.620003, 116.720001, 88.19)

# policy window (engine fix): net = sum of change points, start = value in effect at window start
s = ss['JP_POLICY_RATE']
wp = rmp._policy_window_path(s['dates'], s['values'], FR.as_of, metric_id='JP_POLICY_RATE',
                             carry_start=True)
assert wp['window'] == ['2025-11-23', '2026-11-23']
assert (wp['window_start_value'], wp['window_start_observation']) == (0.478, '2025-11-01')
assert (wp['window_end_value'], FR.last_date('JP_POLICY_RATE')) == (1.227, '2026-10-01')
assert len(wp['events']) == 6 and sum(e['delta_bp'] for e in wp['events']) == 75 == wp['net_bp']
assert [e['delta_bp'] for e in wp['events']] == [8, 17, 11, 14, 7, 18]
assert round((pr['2026-10'] - pr['2025-12']) * 100) == 67          # from the first in-window observation
assert (pr['2025-12'], pr['2026-01'], pr['2026-06'], pr['2026-07'], pr['2026-09']) == (0.557, 0.728, 0.841, 0.978, 1.043)
cells = {c['metric_id']: c for c in FR.rep['research_plan']['point_values']['cells']}
stored = cells['JP_POLICY_RATE'].get('policy_window_path') or {}
if STRICT or stored.get('window_start_observation'):
    assert stored == wp, 'stored policy window differs from the recomputed post-fix window'
else:
    print('NOTE: run dir carries the pre-fix policy window (net %d bp, window start %s); '
          'text quotes the post-fix caliber' % (stored.get('net_bp'), stored.get('window_start_value')))

# calendar records / day counts / levels quoted in the judgment
cal = FR.cal['entries']
jp_rec = [e for e in cal if e.get('metric_id') == 'JP_POLICY_TARGET']
assert [e['entry_id'] for e in jp_rec] == ['RC-JP-BOJ-TARGET-2026-09', 'RC-JP-BOJ-MAINT-2026-10']
assert (jp_rec[0]['decision_date'], jp_rec[0]['effective_on'], jp_rec[0]['target_value']) == (
    '2026-09-18', '2026-09-24', 1.25)
assert jp_rec[1]['kind'] == 'policy_maintenance' and jp_rec[1]['decision_date'] == '2026-10-30' \
    and 'effective_on' not in jp_rec[1]
assert not [e for e in cal if 'ECB' in e['entry_id'] or 'FOMC-DEC' in e['entry_id']]
assert (D(2026, 11, 23) - D(2026, 9, 24)).days == 60 and (D(2026, 11, 23) - D(2026, 9, 18)).days == 66
assert cn_int(60) == '六十' and cn_int(66) == '六十六' and cn_int(75) == '七十五' and cn_int(67) == '六十七'
assert cn_num(0.478, 3) == '零点四七八' and cn_num(1.227, 3) == '一点二二七'

# NIT #8: common-window SPX change
assert ('%.2f' % FR.ret('SPX', '2026-10-23', '2026-11-19'), '%.2f' % FR.ret('SPX', '2026-10-23', '2026-11-23')) == (
    '-5.87', '-5.51')
# NIT #14: same-month policy changes in the series store (not in this round's evidence index)
assert ('DFEDTARU@2026-11-23' not in [r['ref'] for r in ei]) and ('ECB_DFR@2026-09-16' not in [r['ref'] for r in ei])


def changes(mid):
    return [(ss[mid]['dates'][k], ss[mid]['values'][k - 1], ss[mid]['values'][k])
            for k in range(1, len(ss[mid]['dates'])) if ss[mid]['values'][k] != ss[mid]['values'][k - 1]]


assert changes('DFEDTARU')[-1] == ('2026-09-17', 3.75, 4.0) and changes('ECB_DFR')[-1] == ('2026-09-16', 2.25, 2.5)

RM = J['reader_map']
C = {c['id']: c for c in J['l3']['contradictions']}
T = RM['transmission'][0]['links']
LK = J['l3']['mechanism_chains'][0]['links']
S = {s['id']: s['rows'] for s in J['l4']['scenarios']}
Q = J['quality_gate_notes']
REG = {r['region']: r for r in RM['regions']}
assert list(C) == ['C1-INFL-SYNC', 'C2-GROWTH-STABLE', 'C3-JP-POLICY']
assert [l['face_off_verdict'] for l in T] == ['尚不能区分', '尚不能区分', '支持主解释']
assert [l['distinguishing_metric'] for l in T] == ['BEI_10Y', 'TIPS_10Y', 'TIPS_10Y']
assert list(S) == ['S1-INFL-STICKY', 'S2-INFL-FADE']
assert [t['metric_id'] for t in RM['turnings']] == ['CPI', 'EA_HICP_YOY', 'JP_POLICY_RATE']
assert S['S1-INFL-STICKY']['trigger']['deadline'] == S['S2-INFL-FADE']['trigger']['deadline'] == '2027-02-15'

# ── MAJOR #0: S1 falsification must be observable and triggerable ──────
sub(S['S1-INFL-STICKY']['falsification'], 'threshold',
    '若 2027-01 前发布的 EA_HICP_YOY 同比连续两个月低于 3.0%,通胀粘性假设被证伪',
    '若 2026-12 与 2027-01 两月发布的 EA_HICP_YOY 同比(对应 2026-11、2026-12 观测月,规则发布日 2026-12-16、'
    '2027-01-16,均不晚于期限 2027-02-15)连续两个月低于 3.0%,通胀粘性假设被证伪', 'S1.falsification')

# ── MINOR #5 + NIT #10: scenario premise calibers ──────────────────────
sub(S['S1-INFL-STICKY'], 'scenario',
    '至 2027-01,EA_HICP_YOY 同比维持 3.5% 以上,美国 CORE_PCE 同比维持 3.0% 以上,两地政策面维持紧缩偏向(日本月均中枢不低于当前台阶)。',
    '至 2027-01 发布(即至 2026-12 观测月;2027-01 观测月的规则发布日 2027-02-16 晚于期限 2027-02-15),'
    'EA_HICP_YOY 同比维持 3.5% 以上,美国 CORE_PCE 同比维持 3.0% 以上,美欧政策面维持紧缩偏向'
    '【假设·美欧政策利率不在本问证据面】(日本月均中枢不低于当前台阶)。', 'S1.scenario')
assert rmp._visible_publish('EA_HICP_YOY', 'monthly', '2027-01-01')[0] == '2027-02-16' > '2027-02-15'
sub(S['S2-INFL-FADE'], 'scenario',
    '至 2027-01,EA_HICP_YOY 同比回落至 3.0% 以下',
    '至 2027-01 发布(即至 2026-12 观测月),EA_HICP_YOY 同比回落至 3.0% 以下', 'S2.scenario')

# ── MINOR #1: ranking cross-over is historical ─────────────────────────
sub(C['C1-INFL-SYNC'], 'statement', '两地最新可比同月为九月，更早月份位次有交叉',
    '两地最新可比同月为九月，为 2023-09 以来首个高于美国的可比月份(2022-07 至 2023-09 曾持续高于美国)', 'C1')

# ── MINOR #4: energy premise vs the on-face oil reading ────────────────
# (the L3 statement's numbers are contract-bound to the latest fact of the
#  aliased metric, so historical levels / changes go to the transmission
#  link they bear on, and the statement carries a number-free pointer)
OIL = ('供给侧对账(能源前提 vs 在场读数): 布伦特原油(BRENT_F)近三个月自 2026-08-19 的 91.62 至 2026-11-23 的 88.19 为 -3.74%'
       '(近一月 116.72→88.19 为 -24.44%,11-23 为盘中快照;近 12 个月 +38.86%)——三个月窗内油价微降而两地通胀走高,'
       '对「能源持续传导」前提为反向事实、对「能源基数消退」为同向事实【尚未验证】;该读数不在本环区分指标上,不改裁定。')
c1 = C['C1-INFL-SYNC']
assert c1['statement'].endswith('水平为 2.15(观测 2026-11-20)。')
c1['statement'] = c1['statement'] + '供给侧读数对账见传导面第一环(近三个月布伦特原油微降而两地通胀走高,对「能源持续传导」为反向事实【尚未验证】)。'
LOG.append('[C1] statement (appended)\n    + 供给侧读数对账见传导面第一环(…)')
assert all('BRENT_F' not in r for r in c1['evidence_refs'])

# ── MINOR #2: earlier BEI_10Y rise = low -> peak ───────────────────────
sub(T[0], 'observed_fact', 'BEI_10Y 自 2026-02-27 的 2.25 升至 2026-05-04 的 2.50，合主解释。',
    'BEI_10Y 自 2026-02-27 的 2.25(该上行段 2026-02-20 至 2026-05-04 的低点)升至 2026-05-04 的 2.50'
    '(该段峰值,亦为 2026 年内最高;月末对月末 2026-02-27→2026-05-29 仅 +13bp 至 2.38)，合主解释。', 'transmission[0].links[0]')   # + MINOR #4 (oil) appended below
sub(T[0], 'observed_fact', '升至 2026-05-04 的 2.50(该段峰值,亦为 2026 年内最高;月末对月末 2026-02-27→2026-05-29 仅 +13bp 至 2.38)，合主解释。',
    '升至 2026-05-04 的 2.50(该段峰值,亦为 2026 年内最高;月末对月末 2026-02-27→2026-05-29 仅 +13bp 至 2.38)，合主解释。'
    + OIL, 'transmission[0].links[0]')

# ── MINOR #3 + NIT #6: chain links 2 and 3 ─────────────────────────────
sub(LK[1], 'text', '本引擎无日本融资成本/套息持仓序列,此环为【假设】。',
    '本引擎无日本套息持仓与中长端融资成本(国债收益率)序列——JP_POLICY_RATE 本身为无担保隔夜拆借利率月均,'
    '仅覆盖隔夜一端,此环为【假设】。', 'chain.links[1]')
sub(LK[1], 'missing_link_note', '本引擎无日本套息持仓/融资成本序列,该环为【假设】,缺环待采;',
    '本引擎无日本套息持仓与中长端融资成本(国债收益率)序列,该环为【假设】,缺环待采;', 'chain.links[1].missing_link_note')
sub(LK[2], 'text', '当前 USDJPY 仍处高位而股指已明显回落,组合更接近「风险收缩+利差仍高」的混合态,传导方向证据不单一。',
    '当前 USDJPY 仍处高位(近 12 个月窗内约第 71 百分位)而股指已明显回落,组合更接近「风险收缩+日元仍处低位」的混合态'
    '(「利差仍高」为本问证据面外的【假设】: 无日美利差序列),传导方向证据不单一。', 'chain.links[2]')
assert '71' in LK[2]['text'] and UPCT == 71

# ── NIT #7: % unit in the headline ─────────────────────────────────────
sub(RM, 'headline_conclusion', '日本央行官方政策目标利率约 1.25(2026-09-18 决议',
    '日本央行官方政策目标利率约 1.25%(2026-09-18 决议', 'headline')

# ── NIT #8: common-window figure next to the mixed-endpoint one ────────
sub(T[2], 'observed_fact', '近一月(2026-10-23→2026-11-20/23)SPX 下跌 5.51%、',
    '近一月(2026-10-23→2026-11-20/23)SPX 下跌 5.51%(共同交易日窗 2026-10-23→2026-11-19 为 -5.87%,方向不变)、',
    'transmission[0].links[2]')

# ── NIT #9: link 2 has no separating metric ───────────────────────────
sub(T[1], 'observed_fact', '两解释在区分指标 TIPS_10Y 上的预期方向不分立；',
    '两解释在区分指标 TIPS_10Y 上的预期方向不分立(本环实无可区分指标,TIPS_10Y 仅为对照位)；', 'transmission[0].links[1]')

# ── NIT #13: growth = hard data ────────────────────────────────────────
sub(C['C2-GROWTH-STABLE'], 'statement', '两地增长面大体平稳、并非本期主导变化。',
    '两地硬数据增长面大体平稳、并非本期主导变化(软数据不在本问证据面,未纳入)。', 'C2')

# ── NIT #14: same-month policy changes present in the series store ─────
SMP = ('(快照序列库内另有、未纳入本问证据索引的同月变动: 美联储目标区间上限 3.75→4.00 于 2026-09-17、'
       '欧央行存款便利利率 2.25→2.50 于 2026-09-16,与日本央行 2026-09-18 决议(2026-09-24 生效)同月,不作为本档证据)')
sub(RM['turnings'][2], 'follow_or_diverge', '跨国跟进/背离在政策维度依本问证据不可判;',
    '跨国跟进/背离在政策维度依本问证据不可判' + SMP + ';', 'turnings[JP_POLICY_RATE]')
sub(Q, 4, '跨国政策跟进/背离在政策维度依本问证据不可判。',
    '跨国政策跟进/背离在政策维度依本问证据不可判' + SMP + '。', 'quality_gate_notes[4]')

# ── engine-fix ripple: policy-window net change ────────────────────────
if STRICT:
    sub(C['C3-JP-POLICY'], 'statement',
        '月均口径的 12 个月净变动有两种起算口径: 引擎『政策一年窗路径』面板按窗内首观测起算为正六十七个基点，'
        '按『窗启时在值(2025-11 月均零点四七八)→窗末观测』为正七十五个基点，两种口径本档并列披露(数字见走位面与披露块)。',
        '月均口径的 12 个月净变动为正七十五个基点(『窗启时在值(2025-11 月均零点四七八)→窗末观测(2026-10 月均一点二二七)』,'
        '即窗内六个变动点之和,引擎『政策一年窗路径』面板同口径);仅自窗内首观测(2025-12 月均)起算为正六十七个基点'
        '(数字见走位面与披露块)。', 'C3')
    sub(LK[0], 'text',
        '净变动 +67bp(引擎政策窗口径=窗首尾观测差，自 2025-12 月均起算；按『窗启时在值→窗末观测』口径为 +75bp)',
        '净变动 +75bp(引擎『政策一年窗路径』口径=窗启时在值→窗末观测,即六个变动点之和；仅自窗内首观测 2025-12 月均起算为 +67bp)',
        'chain.links[0]')
    sub(REG['JP'], 'from_to',
        '近 12 个月政策窗净变动 +67bp(引擎政策窗口径=窗首尾观测差，自 2025-12 月均起算；按窗启时在值 2025-11 月均 0.478 起算为 +75bp)',
        '近 12 个月政策窗净变动 +75bp(窗启时在值 2025-11 月均 0.478→窗末 2026-10 月均 1.227,引擎『政策一年窗路径』面板同口径;'
        '仅自窗内首观测 2025-12 月均起算为 +67bp)', 'regions[JP]')
    sub(Q, 4, '①引擎『政策一年窗路径』面板按窗内首观测(2025-12 月均 0.557)→窗末观测计净变动，显示 +67bp；'
              '按『窗启时在值(2025-11 月均 0.478)→窗末观测(2026-10 月均 1.227)』口径为 +75bp，本档两种口径并列披露。',
        '①引擎『政策一年窗路径』面板按『窗启时在值(2025-11 月均 0.478)→窗末观测(2026-10 月均 1.227)』计净变动，'
        '显示 +75bp(等于窗内六个变动点之和)，与本档正文口径一致；仅自窗内首观测(2025-12 月均 0.557)起算为 +67bp'
        '(另一口径,仅作另列)。', 'quality_gate_notes[4]')
    sub(Q, 5, '引擎缺口披露(已登记为待裁定残留，本轮未改引擎): ①政策一年窗路径的净变动口径(见上条①)；',
        '引擎缺口披露(原第①项「政策一年窗路径的净变动口径」已由引擎修复消除——面板现按『窗启时在值→窗末观测』计净变动,'
        '与本档口径一致;余三项为待裁定残留，本轮未改引擎): ', 'quality_gate_notes[5]')

# ── invariants ─────────────────────────────────────────────────────────
old = json.load(open(j_in, encoding='utf-8'))
assert J['agent_declaration'] == old['agent_declaration']
assert J['schema_version'] == old['schema_version']
for a, b in zip(old['l3']['contradictions'], J['l3']['contradictions']):
    assert a['id'] == b['id'] and a['evidence_refs'] == b['evidence_refs'] \
        and a['competing_explanations'] == b['competing_explanations']
for a, b in zip(old['reader_map']['regions'], J['reader_map']['regions']):
    assert a['anchor_echo'] == b['anchor_echo']
for a, b in zip(old['l4']['scenarios'], J['l4']['scenarios']):
    assert a['id'] == b['id']
    for k in ('asset_direction', 'sensitive_variables'):
        assert a['rows'][k] == b['rows'][k], k
    assert a['rows']['trigger']['deadline'] == b['rows']['trigger']['deadline']
    assert a['rows']['falsification']['metric_id'] == b['rows']['falsification']['metric_id'] \
        and a['rows']['falsification']['secondary_metric_ids'] == b['rows']['falsification']['secondary_metric_ids']
for a, b in zip(old['reader_map']['transmission'][0]['links'], T):
    assert a['main_predicts'] == b['main_predicts'] and a['competing_predicts'] == b['competing_predicts'] \
        and a['face_off_verdict'] == b['face_off_verdict'] and a['verdict_note'] == b['verdict_note']
for a, b in zip(old['reader_map']['turnings'], RM['turnings']):
    assert a.get('narrative') == b.get('narrative') and a['first_mover'] == b['first_mover']
assert J != old
with open(j_out, 'w', encoding='utf-8') as fh:
    json.dump(J, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
raw = open(j_out, 'rb').read()
print('wrote', j_out, len(raw), 'bytes sha16', hashlib.sha256(raw).hexdigest()[:16])
print('replacements', len(LOG))
print('\n'.join(LOG))
