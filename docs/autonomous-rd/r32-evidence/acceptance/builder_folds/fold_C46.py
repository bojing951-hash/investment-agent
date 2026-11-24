#!/usr/bin/python3 -I
"""fold_C46.py <judgment_in.json> <tree> <run_dir> <judgment_out.json>

Builder revision of the C4 work-order judgment (open question: macro
environment of the US / euro area / China / Japan vs three months ago, on the
degraded install face) after the independent review it received at the
superseded stamp 8f9055d (round 1, REVISE: 1 MAJOR / 3 MINOR / 1 NIT, 504
points / 3 mismatches, 20 counterexamples; recorded verbatim in the engine
tree).  The input is the judgment exactly as it stood when that review was
made (judgment5_C4.json), already re-bound to this run's round id by
restamp_judgment.py (the work order was re-planned at the new stamp; its
frozen inputs are byte-identical between the two stamps).  Every number
quoted in a replacement sentence is recomputed here from the run's own frozen
inputs (root_overlay snapshot / release calendar / metric registry / evidence
index / report.json) and asserted before the text is written.  Read-only on
the run directory.

Folded (review item numbers as listed in VERDICT-round1.json):
  #0 MAJOR  the energy sentence called the three-month path of oil futures
            and of the monthly spot average "inconsistent in direction";
            the frozen series show futures rising with the spot average up
            to 2026-10-30 and falling only in November -- the "inconsistency"
            was an end-point mismatch (futures window ends on the 11-23
            intraday value, spot monthly average ends in October).  Rewritten
            in the C1 competing explanation and in quality_gate_notes[0],
            with the readings at the two decision dates.
  #1 MINOR  the FOMC minutes entry is on the engine policy-document face,
            not in the frozen calendar (18 entries, none about it)
  #2 MINOR  extending scenario: falsification and trigger did not partition
            the outcome space (JP gap [1.17, 1.28), CN_LPR_1Y listed but
            unused, trigger tied to "after the next Fed decision" against a
            2027-02-28 deadline, 1.17 underived) -- falsification is now the
            complement of the trigger
  #3 MINOR  extending scenario asset direction: "dollar stronger vs CNY and
            JPY" -- USDCNY fell 0.35% in the cited window; direction text
            now states both legs, the two FX series are cited
  #4 NIT    converging scenario: "not above 1.28" vs the trigger's
            "below 1.28"
Operator addition beyond the review (disclosed): both triggers state that the
Japanese monthly mean is the latest one published before the deadline; the
first sentence of quality_gate_notes[0] lists the two oil series beside DXY
as near-24h instruments (their 11-23 values are intraday at the snapshot's
research cut-off instant).
"""
import copy
import json
import os
import sys
sys.path.insert(0, '/tmp/r32-accept/scripts')
import seatlib_r32 as L                                  # noqa: E402

STAMP = os.environ.get('R32_STAMP')          # optional: expected run git_head
j_in, tree, rd, j_out = sys.argv[1:5]
for p in (os.path.join(tree, 'scripts'), os.path.join(tree, 'scripts', 'research_contract')):
    sys.path.insert(0, p)
import research_map_planner as rmp                         # noqa: E402

FR = L.Frozen(rd)
ss = FR.ss
R = FR.rep['run']
RID = R['ts_utc']
if STAMP:
    assert (R.get('git_head') or '').startswith(STAMP), R.get('git_head')
J = copy.deepcopy(json.load(open(j_in, encoding='utf-8')))
assert J['agent_declaration']['produced_by'].count(RID) == 1, RID
LOG = []


def rep(s, old, new, n=1):
    assert s.count(old) == n, ('anchor count', s.count(old), n, old[:48])
    return s.replace(old, new)


def sub(obj, key, old, new, where):
    obj[key] = rep(obj[key], old, new)
    LOG.append('[%s] %s\n    - %s\n    + %s' % (where, key, old, new))


def subl(lst, i, old, new, where):
    lst[i] = rep(lst[i], old, new)
    LOG.append('[%s]\n    - %s\n    + %s' % (where, old, new))


# ── computed facts (frozen inputs of this run) ─────────────────────────
assert FR.as_of == '2026-11-23' and RID == '20261123T235101Z'
assert FR.snap.get('research_as_of') == '2026-11-23T22:58:11+08:00'
E = FR.rep['evidence_index']
assert isinstance(E, list) and len(E) == 69 and isinstance(E[0], dict)
RK = 'ref' if 'ref' in E[0] else [k for k in E[0] if '@' in str(E[0][k])][0]
REFS = [e[RK] for e in E]

# #0 MAJOR: oil futures vs the monthly spot average, three-month window
OIL = {}
for mid in ('WTI_F', 'BRENT_F'):
    d, v = ss[mid]['dates'], ss[mid]['values']
    a = FR.val(mid, '2026-08-21')
    assert FR.date(mid, '2026-08-21') == '2026-08-21' and FR.last_date(mid) == FR.date(mid, '2026-11-23') == '2026-11-23'
    r = {day: FR.ret(mid, '2026-08-21', day) for day in ('2026-09-16', '2026-09-18', '2026-10-30', '2026-11-23')}
    r['10-30→11-23'] = FR.ret(mid, '2026-10-30', '2026-11-23')
    means = {}
    for dt, x in zip(d, v):
        if dt[:7] in ('2026-08', '2026-09', '2026-10', '2026-11'):
            means.setdefault(dt[:7], []).append(x)
    means = {k: (sum(x) / len(x), len(x)) for k, x in means.items()}
    below = [dt for dt, x in zip(d, v) if '2026-08-21' <= dt <= '2026-11-23' and x < a]
    OIL[mid] = dict(a=a, v={day: FR.val(mid, day) for day in ('2026-09-16', '2026-09-18', '2026-10-30', '2026-11-23')}, r=r, means=means, below=below)
    print('%s anchor %.4f | ' % (mid, a) + ' '.join('%s %.4f (%+.2f%% vs anchor)' % (k, x, r[k]) for k, x in OIL[mid]['v'].items())
          + ' | 10-30->11-23 %+.2f%%' % r['10-30→11-23'] + ' | month means ' + str({k: round(m[0], 4) for k, m in sorted(means.items())})
          + ' | obs below anchor: %d, first %s' % (len(below), below[0]))
assert '%.2f' % OIL['WTI_F']['a'] == '87.06' and '%.2f' % OIL['BRENT_F']['a'] == '94.39'
assert ['%.2f' % OIL['WTI_F']['v'][k] for k in ('2026-09-16', '2026-09-18', '2026-10-30', '2026-11-23')] == ['102.43', '100.30', '104.12', '82.02']
assert ['%.2f' % OIL['BRENT_F']['v'][k] for k in ('2026-10-30', '2026-11-23')] == ['117.64', '88.19']
assert ['%.2f' % OIL['WTI_F']['r'][k] for k in ('2026-09-16', '2026-09-18', '2026-10-30', '2026-11-23', '10-30→11-23')] == ['17.65', '15.21', '19.60', '-5.79', '-21.23']
assert ['%.2f' % OIL['BRENT_F']['r'][k] for k in ('2026-10-30', '2026-11-23', '10-30→11-23')] == ['24.63', '-6.57', '-25.03']
# every observation from 1 September to the end of October is above the three-month anchor
for mid in OIL:
    b = OIL[mid]['below']
    assert all(x.startswith(('2026-08', '2026-11')) for x in b), (mid, b)
    assert all(OIL[mid]['a'] < x for dt, x in zip(ss[mid]['dates'], ss[mid]['values']) if '2026-09-01' <= dt <= '2026-10-31'), mid
assert '%.2f|%.2f' % (OIL['WTI_F']['means']['2026-08'][0], OIL['WTI_F']['means']['2026-10'][0]) == '82.45|96.94'
assert OIL['WTI_F']['means']['2026-08'][1] == 21 and OIL['WTI_F']['means']['2026-10'][1] == 22      # full calendar months
# month means of the daily futures values: August -> September -> October rise, November (to the 23rd) falls back
assert OIL['WTI_F']['means']['2026-08'][0] < OIL['WTI_F']['means']['2026-09'][0] < OIL['WTI_F']['means']['2026-10'][0] \
    and OIL['WTI_F']['means']['2026-11'][0] < OIL['WTI_F']['means']['2026-09'][0]
assert OIL['BRENT_F']['means']['2026-08'][0] < OIL['BRENT_F']['means']['2026-09'][0] < OIL['BRENT_F']['means']['2026-10'][0] \
    and OIL['BRENT_F']['means']['2026-11'][0] < OIL['BRENT_F']['means']['2026-09'][0]
# the observations below the anchor after 2026-08-21: six at the end of August, then from 2026-11-09 onwards
assert [x[:7] for x in OIL['WTI_F']['below']] == ['2026-08'] * 6 + ['2026-11'] * 9, OIL['WTI_F']['below']
assert [x[:7] for x in OIL['BRENT_F']['below']] == ['2026-08'] * 6 + ['2026-11'] * 9, OIL['BRENT_F']['below']
assert all(x.startswith('2026-11') for x in OIL['WTI_F']['below'] if x >= '2026-09-01') \
    and min(x for x in OIL['WTI_F']['below'] if x >= '2026-09-01') == '2026-11-09' == min(x for x in OIL['BRENT_F']['below'] if x >= '2026-09-01')
assert OIL['WTI_F']['below'][0] == OIL['BRENT_F']['below'][0] == '2026-08-24' and OIL['WTI_F']['below'][5] == OIL['BRENT_F']['below'][5] == '2026-08-31'
assert FR.intraday('BRENT_F')[0] is True and FR.intraday('WTI_F')[0] is False      # seat helper marks only Brent
wsm = FR.monthly('WTI_SPOT_M')
assert wsm['2026-08'] == 83.9 and wsm['2026-10'] == 102.07 and FR.last_date('WTI_SPOT_M') == '2026-10-01' \
    and '%.2f' % ((wsm['2026-10'] / wsm['2026-08'] - 1.0) * 100.0) == '21.66'
assert wsm['2026-09'] == 97.31                                                      # spot average rises in September too
assert 'WTI_F@2026-11-23' in REFS and 'BRENT_F@2026-11-23' in REFS and not [r for r in REFS if 'WTI_SPOT_M' in r]

# decision dates on the frozen face: US from the engine policy-event cluster, JP from the calendar record
DF_CH = [(ss['DFEDTARU']['dates'][k], ss['DFEDTARU']['values'][k - 1], ss['DFEDTARU']['values'][k])
         for k in range(1, len(ss['DFEDTARU']['dates'])) if ss['DFEDTARU']['values'][k] != ss['DFEDTARU']['values'][k - 1]]
assert DF_CH[-2:] == [('2025-12-11', 4.0, 3.75), ('2026-09-17', 3.75, 4.0)] and ss['DFEDTARU']['values'][-1] == 4.0
dwp = rmp._policy_window_path(ss['DFEDTARU']['dates'], ss['DFEDTARU']['values'], FR.as_of,
                              metric_id='DFEDTARU', carry_start=True)
assert [e['decision_date'] for e in dwp['events']] == ['2025-12-10', '2026-09-16']
cal = FR.cal['entries']
assert FR.cal.get('version') == '1.5.0' and len(cal) == 18
boj = [e for e in cal if e['entry_id'] == 'RC-JP-BOJ-TARGET-2026-09']
assert len(boj) == 1 and boj[0]['decision_date'] == '2026-09-18' and boj[0]['effective_on'] == '2026-09-24'
assert FR.date('WTI_F', '2026-09-16') == '2026-09-16' and FR.date('WTI_F', '2026-09-18') == '2026-09-18'

# #1 MINOR: the minutes entry is on the engine policy-document face, not in the calendar
assert not [e for e in cal if 'FOMC' in json.dumps(e, ensure_ascii=False) or 'MINUTES' in json.dumps(e, ensure_ascii=False)
            or '纪要' in json.dumps(e, ensure_ascii=False) or '2026-11-18' in json.dumps(e, ensure_ascii=False)]
assert not [e for e in cal if (e.get('metric_id') or '') in ('DFEDTARU', 'DFEDTARL', 'DFF')]
pdf = FR.rep['research_plan'].get('policy_doc_facts') or []
assert len(pdf) == 1 and pdf[0]['published_on'] == '2026-11-18' and pdf[0]['basis'] == 'user_directive' \
    and pdf[0]['kind'] == 'minutes' and 'FOMC 2026年10月会议纪要' in pdf[0]['title']

# #2 MINOR / #4 NIT: levels the scenario thresholds are derived from
pr = FR.monthly('JP_POLICY_RATE')
assert ss['DFEDTARU']['values'][-1] == 4.0 and pr['2026-10'] == 1.227 and FR.val('CN_LPR_1Y', '2026-11-23') == 3.0 \
    and FR.last_date('JP_POLICY_RATE') == '2026-10-01' and FR.last_date('CN_LPR_1Y') == '2026-11-20'
assert not [c for c in DF_CH if '2026-10-20' <= c[0] <= '2026-11-23']

# #3 MINOR: both legs of the dollar in the engine month window
assert FR.val('USDCNY', '2026-10-23') == 6.6779 and FR.val('USDCNY', '2026-11-23') == 6.6542 \
    and '%.2f' % FR.ret('USDCNY', '2026-10-23', '2026-11-23') == '-0.35'
assert FR.val('USDJPY', '2026-10-23') == 156.494003 and FR.val('USDJPY', '2026-11-23') == 159.347 \
    and '%.2f' % FR.ret('USDJPY', '2026-10-23', '2026-11-23') == '1.82'
assert FR.last_date('USDCNY') == FR.last_date('USDJPY') == '2026-11-23'
assert 'USDJPY@2026-11-23' in REFS and 'USDCNY@2026-11-23' in REFS and 'DXY@2026-11-23' in REFS \
    and 'TIPS_10Y@2026-11-19' in REFS and 'VIX@2026-11-23' in REFS

RM = J['reader_map']
C = {c['id']: c for c in J['l3']['contradictions']}
S = {s['id']: s['rows'] for s in J['l4']['scenarios']}
Q = J['quality_gate_notes']
assert list(C) == ['C1-POLICY-DIVERGENCE', 'C2-INFLATION-DIVERGENCE', 'C3-GROWTH-LIMITED', 'C4-EVIDENCE-BOUNDARY']
assert list(S) == ['SCN-A-POLICY-DIVERGENCE-EXTENDS', 'SCN-B-POLICY-CONVERGES']
assert all(r['trigger']['deadline'] == '2027-02-28' for r in S.values())
assert len(Q) == 10 and Q[0].startswith('证据与口径') and Q[2].startswith('证伪面')
C1CE = C['C1-POLICY-DIVERGENCE']['competing_explanations']
assert len(C1CE) == 2 and C1CE[0].startswith('【假设】若美日收紧是对同一全球冲击(能源价格、通胀预期)的同向反应')
SA, SB = S['SCN-A-POLICY-DIVERGENCE-EXTENDS'], S['SCN-B-POLICY-CONVERGES']

# ── #0 MAJOR: energy prices -- the two series move together up to October ──
OLD_CE = '能源价格变量未获对质: 三个月窗内原油期货价格回落而月度现货均价八月低于十月，方向不一致，且证据面无分地区能源价格序列，不足以区分两解释。'
NEW_CE = ('能源价格变量未获对质: 三个月窗内原油期货截至 10 月底上升、11 月回落——WTI_F 87.06(2026-08-21)→104.12(2026-10-30，+19.60%)'
          '→82.02(2026-11-23 盘中快照，较三个月前锚 -5.79%、较 10-30 回落 21.23%)，BRENT_F 94.39→117.64(+24.63%)→88.19(-6.57%，较 10-30 回落 25.03%)；'
          '月度现货均价 WTI_SPOT_M 83.9(2026-08)→102.07(2026-10)为 +21.66%，与期货截至 10-30 的变动同向(期货日值按自然月均值: WTI_F 2026-08 82.45→2026-10 96.94)；'
          '期货窗止于 11-23 盘中而现货月均价止于 10 月，端点不同，不构成方向不一致。美日两次决议时点(2026-09-16、2026-09-18)WTI_F 较三个月前锚高 17.65%、15.21%，'
          '与同一全球冲击的读法相容，但各自独立的读法对此并无相反预期；证据面无分地区能源价格序列，不足以区分两解释。')
subl(C1CE, 0, OLD_CE, NEW_CE, 'C1.competing_explanations[0]')

OLD_Q0 = ('WTI_F 87.06(2026-08-21)→82.02(2026-11-23)为 -5.79%，BRENT_F 94.39→88.19 为 -6.57%(11-23 值为盘中快照)，'
          '月度现货均价 WTI_SPOT_M 83.9(2026-08)→102.07(2026-10)为 +21.66%(该序列不在本轮证据索引，按 series_store 直读)——'
          '三个月窗内期货回落、月度均价八月低于十月，方向不一致，不足以区分两解释。')
NEW_Q0 = ('WTI_F 87.06(2026-08-21)→104.12(2026-10-30，+19.60%)→82.02(2026-11-23 为 -5.79%，较 10-30 回落 21.23%)，'
          'BRENT_F 94.39→117.64(+24.63%)→88.19(-6.57%，较 10-30 回落 25.03%)，两油种 11-23 值为盘中快照'
          '(快照研究截止时点 2026-11-23T22:58:11+08:00 即纽约 09:58，两合约当日结算时刻均在其后——交易所结算时刻属公开制度事实，引擎序列本身不载盘中标注)，'
          '月度现货均价 WTI_SPOT_M 83.9(2026-08)→102.07(2026-10)为 +21.66%(该序列不在本轮证据索引，按 series_store 直读)——'
          '截至 10-30 期货与现货同向上升，期货 9 月初至 10 月底的观测全部高于三个月前锚，11-09 起再度跌破该锚(8 月底曾短暂低于该锚)；'
          '期货窗(止于 11-23 盘中)与现货月均价窗(止于 10 月)端点不同，不构成方向不一致；证据面无分地区能源价格序列，不足以区分两解释。'
          '期货日值按自然月均值: WTI_F 2026-08 82.45、2026-10 96.94；美日决议时点(2026-09-16、2026-09-18)WTI_F 为 102.43、100.30，较三个月前锚 +17.65%、+15.21%，'
          '与同一全球冲击的读法相容，但各自独立的读法对此并无相反预期。')
subl(Q, 0, OLD_Q0, NEW_Q0, 'quality_gate_notes[0]')

# operator addition: the two oil series are near-24h instruments as well
subl(Q, 0, '近 24 小时交易品种(DXY)的当日值为盘中快照(非收盘价)',
     '近 24 小时交易品种(DXY、WTI_F、BRENT_F)的当日值为盘中快照(非收盘价)', 'quality_gate_notes[0] (operator addition)')

# ── #1 MINOR: where the minutes entry lives ─────────────────────────────
subl(Q, 2, '冻结日历无美国政策条目)，日历内仅有 FOMC 2026年10月会议纪要条目(2026-11-18 发布，纪要发布≠决议日)。',
     '冻结日历无美国政策条目，亦无美国会议纪要条目)；引擎政策文档事实面载有 FOMC 2026年10月会议纪要条目(2026-11-18 发布，引擎所记依据为工单指令，纪要发布≠决议日)。',
     'quality_gate_notes[2]')

# ── #2 MINOR: extending scenario -- falsification = complement of the trigger ──
sub(SA['falsification'], 'threshold',
    '若至 2027-02-28 DFEDTARU 上限未再上调(未达 4.25，含停在 4 与回落至 3.75 以下) 或 JP_POLICY_RATE 月均回落至 1.17 以下，政策分化延续情景被证伪',
    '若至 2027-02-28 触发条件未同时满足(DFEDTARU 上限未达 4.25，或 JP_POLICY_RATE 月均低于 1.28，或 CN_LPR_1Y 不再为 3)，政策分化延续情景被证伪',
    'SCN-A.falsification')
sub(SA['trigger'], 'condition',
    '下次美联储决议后 DFEDTARU 上限 ≥4.25 且 日本月均 JP_POLICY_RATE ≥1.28，同时 CN_LPR_1Y 仍为 3',
    '至 2027-02-28 DFEDTARU 上限 ≥4.25 且 JP_POLICY_RATE 月均 ≥1.28，同时 CN_LPR_1Y 仍为 3(证伪条件为本条件的补集)',
    'SCN-A.trigger')
subl(Q, 2, '在截止日均未满足。',
     '在截止日均未满足。延续情景的证伪条件与触发条件互为补集(含中国 LPR 一项)；两情景的日本月均阈值同取 1.28，月均以期限前已发布的最新值为准。',
     'quality_gate_notes[2]')
# operator addition (both triggers): which monthly mean
sub(SA['trigger'], 'condition', 'JP_POLICY_RATE 月均 ≥1.28，同时', 'JP_POLICY_RATE 月均 ≥1.28(以期限前已发布的最新月均为准)，同时', 'SCN-A.trigger (operator addition)')
sub(SB['trigger'], 'condition', '同时 JP_POLICY_RATE 月均低于 1.28(与延续情景的 ≥1.28 互补)',
    '同时 JP_POLICY_RATE 月均低于 1.28(与延续情景的 ≥1.28 互补；月均同以期限前已发布的最新值为准)', 'SCN-B.trigger (operator addition)')

# ── #4 NIT: converging scenario wording = its trigger ────────────────────
sub(SB, 'scenario', 'JP_POLICY_RATE 月均不高于 1.28', 'JP_POLICY_RATE 月均低于 1.28', 'SCN-B.scenario')

# ── #3 MINOR: extending scenario asset direction -- both legs of the dollar ──
sub(SA['asset_direction'], 'direction', '风险资产承压且美元指数(DXY)相对人民币与日元偏强。',
    '风险资产承压且美元偏强(对日元走强: 同窗 USDJPY 156.494→159.347 为 +1.82%；对人民币并未走强: 同窗 USDCNY 6.6779→6.6542 为 -0.35%)。',
    'SCN-A.asset_direction')
assert SA['asset_direction']['evidence_refs'] == ['DXY@2026-11-23', 'TIPS_10Y@2026-11-19', 'VIX@2026-11-23']
SA['asset_direction']['evidence_refs'] = ['DXY@2026-11-23', 'USDJPY@2026-11-23', 'USDCNY@2026-11-23', 'TIPS_10Y@2026-11-19', 'VIX@2026-11-23']
LOG.append('[SCN-A.asset_direction] evidence_refs\n    - ["DXY@2026-11-23", "TIPS_10Y@2026-11-19", "VIX@2026-11-23"]\n'
           '    + ["DXY@2026-11-23", "USDJPY@2026-11-23", "USDCNY@2026-11-23", "TIPS_10Y@2026-11-19", "VIX@2026-11-23"]')

# ── checks ──────────────────────────────────────────────────────────────
raw = json.dumps(J, ensure_ascii=False)
for gone in ('方向不一致，且证据面', '月度均价八月低于十月', '回落至 1.17', '下次美联储决议后', '不高于 1.28', '相对人民币与日元偏强', '日历内仅有'):
    assert gone not in raw, gone
# the phrase survives only in its negation (twice, in the rewritten sentences) and in the VIX link's unrelated use
assert raw.count('方向不一致') == 3 and raw.count('不构成方向不一致') == 2 and raw.count('与政策分化方向不一致') == 1
assert SA['falsification']['secondary_metric_ids'] == ['JP_POLICY_RATE', 'CN_LPR_1Y']
assert all(x in SA['trigger']['condition'] for x in ('DFEDTARU', 'JP_POLICY_RATE', 'CN_LPR_1Y'))
assert all(x in SA['falsification']['threshold'] for x in ('DFEDTARU', 'JP_POLICY_RATE', 'CN_LPR_1Y'))
assert J != json.load(open(j_in, encoding='utf-8'))
# untouched faces stay byte-identical to the input
J0 = json.load(open(j_in, encoding='utf-8'))
assert J0['l3']['mechanism_chains'] == J['l3']['mechanism_chains']
for k in J0['l3']:
    if k not in ('contradictions',):
        assert J0['l3'][k] == J['l3'][k], k
for a, b in zip(J0['l3']['contradictions'], J['l3']['contradictions']):
    assert {k: v for k, v in a.items() if k != 'competing_explanations'} == {k: v for k, v in b.items() if k != 'competing_explanations'}, a['id']
    assert len(a['competing_explanations']) == len(b['competing_explanations'])
    for i, (x, y) in enumerate(zip(a['competing_explanations'], b['competing_explanations'])):
        if (a['id'], i) != ('C1-POLICY-DIVERGENCE', 0):
            assert x == y, (a['id'], i)
assert J0['reader_map'] == J['reader_map']
for a, b in zip(J0['l4']['scenarios'], J['l4']['scenarios']):
    assert {k: v for k, v in a.items() if k != 'rows'} == {k: v for k, v in b.items() if k != 'rows'}
    assert a['rows']['sensitive_variables'] == b['rows']['sensitive_variables']
    assert a['rows']['trigger']['deadline'] == b['rows']['trigger']['deadline']
    assert a['rows']['asset_direction']['confidence_tier'] == b['rows']['asset_direction']['confidence_tier']
    assert a['rows']['falsification']['metric_id'] == b['rows']['falsification']['metric_id']
    assert a['rows']['falsification']['secondary_metric_ids'] == b['rows']['falsification']['secondary_metric_ids']
assert J0['l4']['scenarios'][1]['rows']['asset_direction'] == J['l4']['scenarios'][1]['rows']['asset_direction']
assert J0['l4']['scenarios'][1]['rows']['falsification'] == J['l4']['scenarios'][1]['rows']['falsification']
assert J0['l4']['scenarios'][0]['rows']['scenario'] == J['l4']['scenarios'][0]['rows']['scenario']
for k in J0['l4']:
    if k != 'scenarios':
        assert J0['l4'][k] == J['l4'][k], k
for k in J0:
    if k not in ('l3', 'l4', 'quality_gate_notes'):
        assert J0[k] == J[k], k
for i in range(10):
    if i not in (0, 2):
        assert J0['quality_gate_notes'][i] == Q[i], i
for r in SA['asset_direction']['evidence_refs']:
    assert r in REFS, r
with open(j_out, 'w', encoding='utf-8') as fh:
    json.dump(J, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
rawb = open(j_out, 'rb').read()
print('wrote', j_out, len(rawb), 'bytes sha16', __import__('hashlib').sha256(rawb).hexdigest()[:16], '| run', RID,
      '| git_head', (R.get('git_head') or '')[:12], '| STAMP', STAMP)
print('replacements', len(LOG))
print('\n'.join(LOG))
