#!/usr/bin/python3 -I
"""fold_C45.py <judgment_in.json> <tree> <run_dir> <judgment_out.json> [--expect-new-engine]

Builder revision of the C4 work-order judgment (open question: macro
environment of the US / euro area / China / Japan vs three months ago, on the
degraded install face) after (a) the independent review it received at the
superseded stamp 0f3936d (REVISE: 1 MAJOR / 2 MINOR counted, 7 further MINOR
and 8 NIT) and (b) the engine fix of the policy-window net change (sum of the
change points; carried in the reader report's policy path panel).  Every
number quoted in a replacement sentence is recomputed here from the run's own
frozen inputs (root_overlay snapshot / release calendar / evidence index /
report.json) and asserted before the text is written.  Read-only on the run
directory.  `tree` is the tree whose engine code the helpers are imported from
(read-only).

Folded:
  MAJOR #0  "US and Japan equity declines are close under both calibers" is
             contradicted by the engine window (SPX -5.51% vs NIKKEI225 -9.98%)
  MINOR #1  BEI_10Y window-end value vs latest observation (2.16 / 2.15)
        #2  the FOMC minutes date is not a calendar record (calendar has no
             US policy / minutes entry; it is on the engine policy-document face)
        #3  growth: small cross-economy directional differences exist
        #4  "direction, not level" vs the turning face (different windows)
        #5  two transmission links judged "supports the main explanation" were
             stronger than the evidence; reservations moved into rendered fields
        #6  scenarios: platform state unassigned, "US cuts back to 3.75" outside
             its trigger, inconsistent JP threshold, missing failure form
        #7  scissors chain: the distinguishing metric did not distinguish
        #8  energy price named but never faced off; no components data for C2
        #9  latest-revision vintage of six anchor cells not transcribed
  NIT #10-#17 (wording, bracket with three time points, raw floats, unverified
        holiday note, vague "within three months", the 12-month net change
        sentence rewritten for the fixed engine panel).
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
    """number -> Chinese numerals, e.g. 5.51 -> 五点五一."""
    D = '零一二三四五六七八九'
    t = ('%.' + str(nd) + 'f') % float(x)
    ip, fp = t.split('.')
    return D[int(ip)] + '点' + ''.join(D[int(c)] for c in fp.rstrip('0'))


# ── computed facts (frozen inputs of this run) ─────────────────────────
assert FR.as_of == '2026-11-23'
D = datetime.date
if STRICT:
    assert (R.get('git_head') or '').startswith('8f9055d'), R.get('git_head')

# MAJOR #0: equity declines, engine window vs same-day close caliber
assert FR.val('SPX', '2026-10-23') == 7623.680176 and FR.val('SPX', '2026-11-23') == 7203.850098 \
    and FR.date('SPX', '2026-11-23') == FR.last_date('SPX') == '2026-11-23'
assert FR.val('NIKKEI225', '2026-10-23') == 62693.16 and FR.val('NIKKEI225', '2026-11-23') == 56436.65 \
    and FR.date('NIKKEI225', '2026-11-23') == FR.last_date('NIKKEI225') == '2026-11-20'
SPX_E, NK_E, SH_E = (FR.ret('SPX', '2026-10-23', '2026-11-23'), FR.ret('NIKKEI225', '2026-10-23', '2026-11-23'),
                     FR.ret('SHCOMP', '2026-10-23', '2026-11-23'))
assert ('%.2f|%.2f|%.2f' % (SPX_E, NK_E, SH_E)) == '-5.51|-9.98|-4.11'
assert FR.val('SPX', '2026-11-20') == 6910.390137 and '%.2f' % FR.ret('SPX', '2026-10-23', '2026-11-20') == '-9.36'
assert '%.2f|%.2f|%.2f' % (FR.ret('SHCOMP', '2026-10-23', '2026-11-20'), FR.ret('DAX', '2026-10-23', '2026-11-20'),
                           FR.ret('DAX', '2026-10-23', '2026-11-23')) == '-4.25|-1.50|0.11'
assert round(abs(SPX_E - NK_E), 2) == 4.47 and round(abs(NK_E / SPX_E), 2) == 1.81        # engine window
assert round(abs(FR.ret('SPX', '2026-10-23', '2026-11-20') - NK_E), 2) == 0.62            # close caliber
assert round(abs(SPX_E - SH_E), 2) == 1.40                                               # SPX vs SHCOMP, engine window
assert abs(FR.ret('SPX', '2026-10-23', '2026-11-20')) > 4.25 > 1.50                       # close caliber ordering
assert cn_num(5.51) == '五点五一' and cn_num(9.98) == '九点九八' and cn_num(4.47) == '四点四七' \
    and cn_num(4.11) == '四点一一' and '%.2f' % 1.40 == '1.40'

# NIT #14: raw floats of the VIX levels
assert FR.val('VIX', '2026-10-23') == 19.450001 and FR.val('VIX', '2026-11-23') == 27.01 \
    and FR.val('VIX', '2026-11-20') == 35.889999
assert ('%.2f|%.2f' % (FR.ret('VIX', '2026-10-23', '2026-11-23'), FR.ret('VIX', '2026-10-23', '2026-11-20'))) == '38.87|84.52'

# MINOR #1: BEI_10Y window end vs latest observation
assert FR.val('BEI_10Y', '2026-11-19') == 2.16 and FR.val('BEI_10Y', '2026-11-20') == 2.15 \
    and FR.last_date('BEI_10Y') == '2026-11-20'
E = FR.rep['evidence_index']
assert isinstance(E, list) and len(E) == 69 and isinstance(E[0], dict), (type(E).__name__, len(E))
RK = 'ref' if 'ref' in E[0] else [k for k in E[0] if '@' in str(E[0][k])][0]
REFS = [e[RK] for e in E]
assert 'BEI_10Y@2026-11-20' in REFS and 'TIPS_10Y@2026-11-19' in REFS, (RK, REFS[:2])
assert ss['BEI_10Y']['dates'][-1] == '2026-11-20' == FR.date('BEI_10Y', '2026-11-23')

# MINOR #5: rate decomposition windows and the policy changes inside them
assert round((FR.val('BEI_10Y', '2026-11-19') - FR.val('BEI_10Y', '2026-10-20')) * 100) == -19 \
    and round((FR.val('BEI_10Y', '2026-11-19') - FR.val('BEI_10Y', '2025-11-19')) * 100) == -11
assert round((FR.val('TIPS_10Y', '2026-11-19') - FR.val('TIPS_10Y', '2026-10-20')) * 100) == 11 \
    and round((FR.val('TIPS_10Y', '2026-11-19') - FR.val('TIPS_10Y', '2025-11-19')) * 100) == 102
assert FR.val('TIPS_10Y', '2026-11-19') == 2.88 and FR.last_date('TIPS_10Y') == '2026-11-19'
assert FR.date('BEI_10Y', '2025-11-19') == FR.date('TIPS_10Y', '2025-11-19') == '2025-11-19'
assert FR.date('BEI_10Y', '2026-10-20') == FR.date('TIPS_10Y', '2026-10-20') == '2026-10-20'


def changes(mid):
    return [(ss[mid]['dates'][k], ss[mid]['values'][k - 1], ss[mid]['values'][k])
            for k in range(1, len(ss[mid]['dates'])) if ss[mid]['values'][k] != ss[mid]['values'][k - 1]]


DF_CH = changes('DFEDTARU')
assert DF_CH[-2:] == [('2025-12-11', 4.0, 3.75), ('2026-09-17', 3.75, 4.0)] and FR.last_date('DFEDTARU') == '2026-11-23' \
    and ss['DFEDTARU']['values'][-1] == 4.0
assert not [c for c in DF_CH if '2025-11-23' < c[0] <= '2026-11-23' and c[0] not in ('2025-12-11', '2026-09-17')]   # net 0
assert not [c for c in DF_CH if '2026-10-20' <= c[0] <= '2026-11-19']            # no policy change in the 1-month window
dwp = rmp._policy_window_path(ss['DFEDTARU']['dates'], ss['DFEDTARU']['values'], FR.as_of,
                              metric_id='DFEDTARU', carry_start=True)
assert dwp['window'] == ['2025-11-23', '2026-11-23'] and [e['delta_bp'] for e in dwp['events']] == [-25, 25] \
    and dwp['net_bp'] == 0 and dwp['window_start_value'] == 4.0 \
    and [e['decision_date'] for e in dwp['events']] == ['2025-12-10', '2026-09-16']
cp_ = FR.monthly('CPI')
pp_ = FR.monthly('CN_PPI_YOY')
cc_ = FR.monthly('CN_CPI_YOY')


def yoy(m, d):
    pm = '%04d-%02d' % (int(m[:4]) - 1, int(m[5:7]))
    return (d[m] / d[pm] - 1.0) * 100.0 if pm in d else None


assert round(yoy('2026-07', cp_), 2) == 3.30 and round(yoy('2026-09', cp_), 2) == 3.72      # US CPI 3.30 -> 3.72

# MINOR #2: the minutes date is on the engine policy-document face, not in the calendar
cal = FR.cal['entries']
assert FR.cal.get('version') == '1.5.0' and len(cal) == 18
by_id = [e['entry_id'] for e in cal]
assert len([i for i in by_id if i.startswith('RC-2025SHUTDOWN-')]) == 11 \
    and len([i for i in by_id if i.startswith('RC-EA-HICP-')]) == 3 \
    and len([e for e in cal if e.get('metric_id') == 'JP_POLICY_TARGET']) == 2 \
    and len([e for e in cal if e.get('metric_id') == 'CN_LPR_1Y']) == 2
assert not [e for e in cal if 'FOMC' in json.dumps(e, ensure_ascii=False) or 'ECB' in json.dumps(e, ensure_ascii=False)]
assert not [e for e in cal if (e.get('metric_id') or '') in ('DFEDTARU', 'ECB_DFR', 'ECB_MRO')]
assert not [e for e in cal if (e.get('metric_id') or '') in ('DFEDTARU', 'ECB_DFR', 'ECB_MRO')]
pdf = FR.rep['research_plan'].get('policy_doc_facts') or []
assert len(pdf) == 1 and pdf[0]['published_on'] == '2026-11-18' and pdf[0]['basis'] == 'user_directive' \
    and pdf[0]['kind'] == 'minutes' and 'FOMC 2026年10月会议纪要' in pdf[0]['title']

# MINOR #3: growth readings, three months ago vs latest
gd = FR.monthly('US_REAL_GDP')
assert gd['2026-04'] == 24408.011 and gd['2026-07'] == 24611.077 \
    and round(yoy('2026-04', gd), 4) == 2.1916 and round(yoy('2026-07', gd), 4) == 2.0657
jp_g = FR.monthly('JP_REAL_GDP_YOY')
assert (jp_g['2026-04'], jp_g['2026-07']) == (0.8, 1.16)
ip = FR.monthly('INDPRO')
assert round(yoy('2026-07', ip), 4) == 1.2498 and round(yoy('2026-10', ip), 4) == 2.1497

# MINOR #4: inflation direction depends on the window
core = FR.monthly('CORE_CPI')
assert (round(yoy('2026-05', core), 4), round(yoy('2026-07', core), 4), round(yoy('2026-08', core), 4),
        round(yoy('2026-09', core), 4)) == (2.8229, 2.4665, 2.4462, 2.5658) and yoy('2026-10', core) is None
jc = FR.monthly('JP_CPI_YOY')
assert (jc['2026-07'], jc['2026-10']) == (1.97, 2.44)
tk = FR.monthly('JP_CPI_TOKYO_YOY')
assert (tk['2026-06'], tk['2026-09'], tk['2026-07'], tk['2026-10']) == (1.6, 2.69, 1.85, 2.73)
assert (cc_['2026-07'], cc_['2026-10'], pp_['2026-07'], pp_['2026-10']) == (0.5, 0.7, 3.5, 5.7)
assert '2026-08-01' < '2026-08-23' < '2026-09-01'            # US turning window ends before, Tokyo window ends after the anchor
assert '2026-05' < '2026-08-23' and '2026-06' < '2026-08-23'  # both windows start before the anchor

# MINOR #7 / NIT #17: PPI-CPI scissors
assert round(pp_['2026-07'] - cc_['2026-07'], 1) == 3.0 and round(pp_['2026-10'] - cc_['2026-10'], 1) == 5.0
assert 'CN_CPI_YOY@2026-10-31' in REFS and 'CN_PPI_YOY@2026-10-31' in REFS
assert D(2027, 2, 23) == D(2026, 11, 23) + datetime.timedelta(days=92)     # three calendar months

# MINOR #8: energy prices on the face
assert round(FR.val('WTI_F', '2026-08-21'), 2) == 87.06 and round(FR.val('WTI_F', '2026-11-23'), 2) == 82.02 \
    and FR.date('WTI_F', '2026-08-21') == '2026-08-21' and FR.date('WTI_F', '2026-11-23') == '2026-11-23' \
    and '%.2f' % FR.ret('WTI_F', '2026-08-21', '2026-11-23') == '-5.79'
assert round(FR.val('BRENT_F', '2026-08-21'), 2) == 94.39 and round(FR.val('BRENT_F', '2026-11-23'), 2) == 88.19 \
    and '%.2f' % FR.ret('BRENT_F', '2026-08-21', '2026-11-23') == '-6.57'
wsm = FR.monthly('WTI_SPOT_M')
assert wsm['2026-08'] == 83.9 and wsm['2026-10'] == 102.07 and FR.last_date('WTI_SPOT_M') == '2026-10-01' \
    and '%.2f' % ((wsm['2026-10'] / wsm['2026-08'] - 1.0) * 100.0) == '21.66'
assert 'WTI_F@2026-11-23' in REFS and 'BRENT_F@2026-11-23' in REFS and not [r for r in REFS if 'WTI_SPOT_M' in r]
assert FR.intraday('BRENT_F')[0] is True

# MINOR #9: latest-revision vintage of the anchor cells
cells = {c['metric_id']: c for c in FR.rep['research_plan']['point_values']['cells']}
VS = '事后回顾(最新修订值,非当时首发值)'
for mid in ('US_REAL_GDP', 'JP_REAL_GDP_YOY', 'JP_CPI_YOY'):
    assert cells[mid]['vintage_semantics'] == VS, mid

# policy window (engine fix): net = sum of the change points, start = value in effect at window start
pr = FR.monthly('JP_POLICY_RATE')
wp = rmp._policy_window_path(ss['JP_POLICY_RATE']['dates'], ss['JP_POLICY_RATE']['values'], FR.as_of,
                             metric_id='JP_POLICY_RATE', carry_start=True)
assert wp['window'] == ['2025-11-23', '2026-11-23']
assert (wp['window_start_value'], wp['window_start_observation']) == (0.478, '2025-11-01')
assert (wp['window_end_value'], FR.last_date('JP_POLICY_RATE')) == (1.227, '2026-10-01')
assert len(wp['events']) == 6 and sum(e['delta_bp'] for e in wp['events']) == 75 == wp['net_bp']
assert [e['delta_bp'] for e in wp['events']] == [8, 17, 11, 14, 7, 18]
assert round((pr['2026-10'] - pr['2025-12']) * 100) == 67
assert (pr['2025-11'], pr['2025-12'], pr['2026-01'], pr['2026-07'], pr['2026-08'], pr['2026-10']) == (
    0.478, 0.557, 0.728, 0.978, 0.977, 1.227)
stored = cells['JP_POLICY_RATE'].get('policy_window_path') or {}
if STRICT or stored.get('window_start_observation'):
    assert stored == wp, 'stored policy window differs from the recomputed post-fix window'
else:
    print('NOTE: run dir carries the pre-fix policy window (net %d bp); text quotes the post-fix caliber'
          % stored.get('net_bp'))

# scenario levels / thresholds quoted in the scenario rows
assert ss['DFEDTARU']['values'][-1] == 4.0 and pr['2026-10'] == 1.227 and FR.val('CN_LPR_1Y', '2026-11-23') == 3.0

RM = J['reader_map']
C = {c['id']: c for c in J['l3']['contradictions']}
T = RM['transmission'][0]['links']
LK0 = J['l3']['mechanism_chains'][0]['links']
LK1 = J['l3']['mechanism_chains'][1]['links']
S = {s['id']: s['rows'] for s in J['l4']['scenarios']}
Q = J['quality_gate_notes']
REG = {r['region']: r for r in RM['regions']}
assert list(C) == ['C1-POLICY-DIVERGENCE', 'C2-INFLATION-DIVERGENCE', 'C3-GROWTH-LIMITED', 'C4-EVIDENCE-BOUNDARY']
assert J['l3']['mechanism_chains'][1]['id'] == 'M2-CN-PPI-CPI-SCISSORS'
assert [l['face_off_verdict'] for l in T] == ['支持主解释', '支持主解释', '尚不能区分']
assert [l['distinguishing_metric'] for l in T] == ['TIPS_10Y', 'BEI_10Y', 'VIX']
assert list(S) == ['SCN-A-POLICY-DIVERGENCE-EXTENDS', 'SCN-B-POLICY-CONVERGES']
assert all(r['trigger']['deadline'] == '2027-02-28' for r in S.values())
assert [t['metric_id'] for t in RM['turnings']] == ['JP_POLICY_RATE', 'JP_CPI_TOKYO_YOY', 'CORE_CPI']
assert len(Q) == 10 and Q[0].startswith('证据与口径') and Q[1].startswith('对质面') and Q[2].startswith('证伪面') \
    and Q[6].startswith('政策口径披露')

# ── MAJOR #0: the two calibers do not both show "close" US / Japan declines ─
sub(C['C4-EVIDENCE-BOUNDARY'], 'statement',
    'VIX 上涨百分之八十四点五二，两种口径下美日股指跌幅均相近。',
    'VIX 上涨百分之八十四点五二；收盘口径下美日股指跌幅相近且深于中国与欧洲，但引擎窗(2026-10-23→2026-11-23，止于盘中快照)下'
    '标普500指数下跌百分之五点五一、日经225下跌百分之九点九八，两者跌幅相差四点四七个百分点，并不相近；'
    '标普指数与上证综指(下跌百分之四点一一)的落差仅一点四零个百分点。', 'C4-EVIDENCE-BOUNDARY')
# (a second "标普500" inside one clause leaves a bare "500" token that the text-consistency
#  check binds to SPX — hence "标普指数" for the second mention; see dryverify_judgment5_C4.txt)

# ── NIT #10 / #11: C1 statement wording ─────────────────────────────────
sub(C['C1-POLICY-DIVERGENCE'], 'statement', '政策维是四地中方向最清晰的分化： ',
    '政策维是可比口径下三地中方向最清晰的分化： ', 'C1-POLICY-DIVERGENCE')
sub(C['C1-POLICY-DIVERGENCE'], 'statement', '综上，分化体现在中美、日中之间方向相反(收紧对未变)，',
    '综上，分化体现在中美、日中之间(收紧对未变)，', 'C1-POLICY-DIVERGENCE')

# ── MINOR #3: growth ────────────────────────────────────────────────────
sub(C['C3-GROWTH-LIMITED'], 'statement', '增长维： 可判证据只显示各经济体状态延续，未见经济体之间的方向性分化。',
    '增长维： 可判证据显示各经济体以状态延续为主，经济体之间仅有小幅方向差异(美国 GDP 同比小幅回落、日本回升、'
    '美国工业生产同比上升)，幅度小且指标间不一致。', 'C3-GROWTH-LIMITED')

# ── MINOR #4: inflation direction vs window; same reconciliation in the headline ─
sub(C['C2-INFLATION-DIVERGENCE'], 'statement', '通胀维： 三地读数方向同向(均高于三个月前)，分化体现在水平，即',
    '通胀维： 三个月对照窗内三地读数方向同向(均高于三个月前)，分化体现在水平，即', 'C2-INFLATION-DIVERGENCE')
sub(C['C2-INFLATION-DIVERGENCE'], 'statement', '分化因此体现在水平： 中国CPI远低于美国与日本；方向上未见经济体之间的反向。',
    '分化因此体现在水平： 中国CPI远低于美国与日本；三个月对照窗内方向上未见经济体之间的反向。'
    '转折面所述「美日通胀方向分化」取另一组窗口: 美国核心CPI同比 2026-05→2026-08 回落、东京都CPI同比 2026-06→2026-09 上行，'
    '方向随窗口起止而异；东京都窗口终点 2026-09 落在三个月对照窗之内，美国窗口终点 2026-08 早于三个月前锚。', 'C2-INFLATION-DIVERGENCE')
sub(RM, 'headline_conclusion', '通胀维三地读数均高于三个月前，分化在水平而非方向(日本全国 CPI 同比 2.44%、美国 CPI 最近有效同比 3.72%、'
    '中国CPI 0.7% 而 PPI 5.7%)',
    '通胀维三个月对照窗内三地读数均高于三个月前，分化在水平而非方向(日本全国 CPI 同比 2.44%、美国 CPI 最近有效同比 3.72%、'
    '中国CPI 0.7% 而 PPI 5.7%；转折面的美日方向分化取 2026-05→2026-08 与 2026-06→2026-09 两窗，起点均早于三个月前锚)', 'headline')
sub(RM, 'headline_conclusion', '过去三个月，四地宏观环境的分化最清晰地体现在政策维： ',
    '过去三个月，证据在场的美、中、日三地之间，宏观环境的分化最清晰地体现在政策维： ', 'headline')

# ── MINOR #1: BEI_10Y window end vs latest observation ──────────────────
sub(T[1], 'observed_fact', '变动 -11bp，最新 2.16(观测 2026-11-19)——两个窗口盈亏平衡均回落；',
    '变动 -11bp，窗末 2.16(2026-11-19)，最新观测 2.15(2026-11-20)——两个窗口盈亏平衡均回落；', 'transmission.links[1]')

# ── MINOR #5: two links were judged more strongly than the evidence ────
sub(T[0], 'competing_predicts',
    'TIPS_10Y 不随政策分化系统性上行(近一月或 12 个月窗为零或负)，名义利率变动由盈亏平衡主导。',
    'TIPS_10Y 的变动与政策变动不同步: 政策未变或净变动为零的窗口内实际利率同样上行，或政策上调后实际利率并不上行'
    '(变动由估值与仓位等非政策因素驱动，与政策分化无直接因果)。', 'transmission.links[0]')
sub(T[0], 'observed_fact', '同期十年期名义利率 5.04，近一月名义 -8bp。',
    '同期十年期名义利率 5.04，近一月名义 -8bp。政策面对照: 近一月共同交易日窗内美国政策无变动，12 个月窗内美国政策先降后升净 0'
    '(2025-12-11 生效下调 25 个基点、2026-09-17 生效上调 25 个基点)而 TIPS_10Y +102bp——方向与主解释一致，'
    '但政策净变动为零时实际利率的上行不由政策变动解释，归因与幅度未定。', 'transmission.links[0]')
sub(T[0], 'face_off_verdict', '支持主解释', '尚不能区分', 'transmission.links[0]')
sub(T[0], 'verdict_note',
    '两窗 TIPS_10Y 均为上行分量(+11bp、+102bp)，12 个月窗主导名义 +91bp，合主解释；单月窗名义 -8bp、盈亏平衡降幅大于实际上行幅度，'
    '单月窗不足以单独支持；且 12 个月窗内美国政策先降后升净 0，实际利率上行的政策归因有限——裁定限于方向一致，幅度与归因保留。',
    '两窗 TIPS_10Y 均为上行分量(+11bp、+102bp)，12 个月窗主导名义 +91bp，方向合主解释；但 12 个月窗内美国政策先降后升净 0、'
    '近一月窗内政策无变动，实际利率上行的政策归因有限，单月窗名义 -8bp、盈亏平衡降幅大于实际上行幅度——'
    '主解释(方向)与竞争解释(变动与政策不同步)两侧预期均相容，尚不能区分。', 'transmission.links[0]')
sub(T[1], 'competing_predicts', 'BEI_10Y 在政策收紧窗内走高(近一月与 12 个月窗变动为正)。',
    '若收紧由通胀压力触发，盈亏平衡应随通胀读数走高并推升名义利率；若收紧同时被读作政策可信，盈亏平衡亦可在收紧后回落'
    '——收紧窗内回落不单独排除该解释。', 'transmission.links[1]')
sub(T[1], 'observed_fact', '美国 CPI 最近有效同比 3.72(2026-09)高于 2026-07 的 3.3，中国 PPI 同比 3.5→5.7。',
    '美国 CPI 最近有效同比 3.72(2026-09)高于 2026-07 的 3.3，中国 PPI 同比 3.5→5.7。指标仅覆盖美国国债市场，'
    '不直接度量日本与中国的通胀预期——回落与「因通胀压力收紧且政策可信」相容，尚不能区分。', 'transmission.links[1]')
sub(T[1], 'face_off_verdict', '支持主解释', '尚不能区分', 'transmission.links[1]')
sub(T[1], 'verdict_note',
    '两窗 BEI_10Y 均为负(-19bp、-11bp)，与竞争解释「通胀预期走高」相左，合主解释；盈亏平衡回落亦与「收紧产生反通胀预期效应」相容，'
    '该读法不与主解释冲突；指标仅覆盖美国国债市场，不直接度量日本与中国的通胀预期。',
    '两窗 BEI_10Y 均为负(-19bp、-11bp)，与竞争解释的字面预期「通胀预期走高」相左；但盈亏平衡回落亦与「收紧产生反通胀预期效应」相容，'
    '该读法不与竞争解释冲突；指标仅覆盖美国国债市场，不直接度量日本与中国的通胀预期——尚不能区分。', 'transmission.links[1]')
sub(T[2], 'verdict_note', '引擎窗下 SPX 与 SHCOMP 落差不足两个百分点、11-23 盘中 SPX',
    '引擎窗下美日跌幅落差 4.47 个百分点(不相近)、SPX 与 SHCOMP 落差不足两个百分点、11-23 盘中 SPX', 'transmission.links[2]')
sub(Q, 1, '判断=支持主解释 ×2、尚不能区分 ×1(逐环两侧相容观测与裁定理由见传导面正文)',
    '判断=尚不能区分 ×3(前两环方向与主解释一致但归因未定，逐环两侧相容观测与裁定保留见传导面正文)', 'Q1')

# ── MINOR #6: scenarios ─────────────────────────────────────────────────
SA, SB = S['SCN-A-POLICY-DIVERGENCE-EXTENDS'], S['SCN-B-POLICY-CONVERGES']
sub(SA, 'scenario', '美日与中国之间的政策方向分化延续。',
    '美日与中国之间的政策方向分化延续。两情景互补而不穷尽: 美日不再加码而中国未变的平台态，以及美国转向降息，均不属任一情景。', 'SCN-A.scenario')
sub(SA['falsification'], 'threshold',
    '若 2027-02-28 前 DFEDTARU 上限回落至 3.75 以下 或 JP_POLICY_RATE 月均回落至 1.17 以下，政策分化延续情景被证伪',
    '若至 2027-02-28 DFEDTARU 上限未再上调(未达 4.25，含停在 4 与回落至 3.75 以下) 或 JP_POLICY_RATE 月均回落至 1.17 以下，'
    '政策分化延续情景被证伪', 'SCN-A.falsification')
sub(SB, 'scenario', '美日不再加码(DFEDTARU 上限不再高于 4、JP_POLICY_RATE 月均不再高于 1.227)，中国转向宽松(CN_LPR_1Y 下调至 2.90 或以下)'
    '或美国降回 3.75；政策方向分化收敛。',
    '美日不再加码(DFEDTARU 上限不再高于 4、JP_POLICY_RATE 月均不高于 1.28)，中国转向宽松(CN_LPR_1Y 下调至 2.90 或以下)；'
    '政策方向分化收敛。美国转向降息(上限回落至 3.75 以下)不属于本情景的收敛形态；美日不再加码而中国未变的平台态不属任一情景，'
    '两情景互补而不穷尽。', 'SCN-B.scenario')
sub(SB['trigger'], 'condition', '同时 JP_POLICY_RATE 月均 ≤1.28', '同时 JP_POLICY_RATE 月均低于 1.28(与延续情景的 ≥1.28 互补)', 'SCN-B.trigger')
sub(SB['falsification'], 'threshold', '若 2027-02-28 前 CN_LPR_1Y 仍为 3 且 DFEDTARU 上限 ≥4.25，政策收敛情景被证伪',
    '若至 2027-02-28 触发条件未同时满足(CN_LPR_1Y 未报 2.90 或以下，或其下调时 DFEDTARU 上限高于 4 或 JP_POLICY_RATE 月均不低于 1.28)，'
    '政策收敛情景被证伪', 'SCN-B.falsification')
sub(Q, 2, '在截止日均未满足。', '在截止日均未满足。两情景互补而不穷尽: 美日不再加码而中国未变的平台态不属任一情景(该形态下延续情景因上限未再上调而失效、'
    '收敛情景因中国未下调而失效)；美国转向降息使延续情景失效而不触发收敛情景。', 'Q2')

# ── MINOR #7 / NIT #17: the distinguishing metric must distinguish ─────
sub(LK1[1], 'missing_link_note',
    '区分指标=CN_PPI_YOY(若三个月内 CN_PPI_YOY 回落至 3.0 以下，上游传导假设减弱)。',
    '区分指标=CN_CPI_YOY 相对 CN_PPI_YOY: 若至 2027-02-23 前 CN_CPI_YOY 随 PPI 同向上行(剪刀差收窄)，传导分支增强；'
    '若 PPI 回落而 CPI 仍低位，挤压分支随前提消退；当前剪刀差(2026-07 至 2026-10)由 3.0 扩至 5.0 个百分点，尚无传导迹象。', 'M2.links[1].missing_link_note')
assert 'CN_CPI_YOY@2026-10-31' not in LK1[1]['evidence_refs']
LK1[1]['evidence_refs'].insert(1, 'CN_CPI_YOY@2026-10-31')
LOG.append('[M2.links[1]] evidence_refs (appended): CN_CPI_YOY@2026-10-31')

# ── MINOR #8: competing explanations ────────────────────────────────────
c1ce = C['C1-POLICY-DIVERGENCE']['competing_explanations']
assert c1ce[0].endswith('则政策分化属同一事件的不同幅度，后续美日应继续同步。')
c1ce[0] += '能源价格变量未获对质: 三个月窗内原油期货价格回落而月度现货均价八月低于十月，方向不一致，且证据面无分地区能源价格序列，不足以区分两解释。'
LOG.append('[C1] competing_explanations[0] (appended)\n    + 能源价格变量未获对质: …不足以区分两解释。')
c2ce = C['C2-INFLATION-DIVERGENCE']['competing_explanations']
assert c2ce[1].endswith('则将在数月内向 CPI 传导或挤压下游利润。')
c2ce[1] += '本证据面无通胀分项数据，上述两解释不可区分。'
LOG.append('[C2] competing_explanations[1] (appended)\n    + 本证据面无通胀分项数据，上述两解释不可区分。')

# ── NIT #14: raw floats ─────────────────────────────────────────────────
LK0[2]['text'] = rep(LK0[2]['text'], '19.450001→27.01', '19.45→27.01')
LK0[2]['text'] = rep(LK0[2]['text'], '19.450001→35.889999', '19.45→35.89')
LOG.append('[M1.links[2]] text: raw floats 19.450001→27.01 / 19.450001→35.889999 -> 19.45→27.01 / 19.45→35.89')

# ── NIT #12: "starting point" limited to the candidate window ───────────
sub(RM['turnings'][0], 'first_mover', '是其后持续收紧的起点；',
    '是本候选窗内收紧段的起点，不是本轮收紧的起点——月均在此前已更早抬升，其后 2026-08 微降、2026-09 与 2026-10 再升'
    '(见后续台阶与政策口径披露)；', 'turnings[0]')

# ── NIT #13 + MINOR #9: region US (three time points; revision vintage) ─
sub(REG['US'], 'from_to', '核心CPI 同比 2.47%(2026-07 月)→最近有效 2.57%(2026-09；指数 336.789→339.9；发布 2026-08-13→2026-11-13，引擎推定规则，非日历实录)',
    '核心CPI 同比 2.47%(同比期 2026-07)→最近有效 2.57%(同比期 2026-09；指数水平为最新月 2026-10 的 339.9 对 2026-07 的 336.789；'
    '发布 2026-08-13(2026-07 指数)→2026-11-13(2026-10 指数)，引擎推定规则，非日历实录)', 'regions[US]')
sub(REG['US'], 'from_to', '发布 2026-07-29→2026-10-29，引擎推定规则并含官方实测锚，非日历实录)',
    '发布 2026-07-29→2026-10-29，引擎推定规则并含官方实测锚，非日历实录；最新修订值，事后回顾口径，非当时首发值)', 'regions[US]')
sub(REG['JP'], 'from_to', '发布 2026-08-14→2026-11-14，引擎推定规则，非日历实录；该序列不在本轮证据索引，按降级口径引用)',
    '发布 2026-08-14→2026-11-14，引擎推定规则，非日历实录；最新修订值，事后回顾口径，非当时首发值；该序列不在本轮证据索引，按降级口径引用)',
    'regions[JP]')
sub(REG['JP'], 'from_to', '全国 CPI 同比 1.97→2.44(观测 2026-07→2026-10；发布 2026-08-20→2026-11-20，引擎推定规则，非日历实录)',
    '全国 CPI 同比 1.97→2.44(观测 2026-07→2026-10；发布 2026-08-20→2026-11-20，引擎推定规则，非日历实录；最新修订值，事后回顾口径，非当时首发值)',
    'regions[JP]')

# ── Q0: MINOR #8 numbers, MINOR #9 vintage, NIT #16 holiday note ───────
sub(Q, 0, 'NIKKEI225 止于 2026-11-20 收盘(2026-11-23 无观测，引擎序列未载原因；席位常识为日本当日为勤劳感谢日休市，未经本轮证据面核实)',
    'NIKKEI225 止于 2026-11-20 收盘(2026-11-23 无观测，引擎序列未载原因)', 'Q0 (NIT #16)')
Q[0] += ('能源价格对账(对应政策维矛盾陈述竞争解释一): WTI_F 87.06(2026-08-21)→82.02(2026-11-23)为 -5.79%，'
         'BRENT_F 94.39→88.19 为 -6.57%(11-23 值为盘中快照)，月度现货均价 WTI_SPOT_M 83.9(2026-08)→102.07(2026-10)为 +21.66%'
         '(该序列不在本轮证据索引，按 series_store 直读)——三个月窗内期货回落、月度均价八月低于十月，方向不一致，不足以区分两解释。'
         '口径注记: 美国实际 GDP、日本实际 GDP 同比、日本全国 CPI 同比的锚格值为最新修订族(事后回顾口径，引擎逐格标注)，'
         '三个月前锚的严格历史时点值可能为当期初值，本档未转述首发值。')
LOG.append('[Q0] (appended)\n    + 能源价格对账: WTI_F 87.06→82.02 为 -5.79%，BRENT_F 94.39→88.19 为 -6.57%…；口径注记: 美国实际 GDP、'
           '日本实际 GDP 同比、日本全国 CPI 同比的锚格值为最新修订族(事后回顾口径…)')

# ── NIT #15: the 12-month net change sentence (engine panel fixed) ─────
OLD6 = '近 12 个月净变动依起算点而异: 自窗启月在值(2025-11 月均 0.478)至 2026-10 月均 1.227 为 +75bp，自窗内首个完整观测月(2025-12 月均 0.557)起算为 +67bp' \
       '(2025-12-01 的上调落在窗启之后，前一口径计入)——本工单路径面未载净变动字段，两种口径由席位并列披露，本档以窗启在值口径为准。'
if STRICT or stored.get('window_start_observation'):
    NEW6 = '近 12 个月净变动为 +75bp(窗启时在值 2025-11 月均 0.478→窗末观测 2026-10 月均 1.227，即窗内六个变动点之和，' \
           '与引擎『政策一年窗路径』面板同口径)；仅自窗内首观测(2025-12 月均 0.557)起算为 +67bp，属另一口径、仅作另列。'
else:
    NEW6 = '近 12 个月净变动为 +75bp(窗启时在值 2025-11 月均 0.478→窗末观测 2026-10 月均 1.227，即窗内六个变动点之和)；' \
           '引擎路径面(report.json 政策一年窗路径面板)按窗内首观测起算载 +67bp，席位信封(AGENT_SEAT_ENVELOPE)未载净变动字段，' \
           '两种口径并列披露，本档以窗启在值口径为准。'
sub(Q, 6, OLD6, NEW6, 'Q6 ②')

# ── checks ──────────────────────────────────────────────────────────────
assert [l['face_off_verdict'] for l in T] == ['尚不能区分'] * 3
raw = json.dumps(J, ensure_ascii=False)
assert '支持主解释 ×2' not in raw and '两种口径下美日股指跌幅均相近' not in raw and '勤劳感谢日' not in raw
assert '19.450001' not in raw and '或美国降回 3.75' not in raw and '不再高于 1.227' not in raw
assert J != json.load(open(j_in, encoding='utf-8'))
# untouched faces stay byte-identical to the input
J0 = json.load(open(j_in, encoding='utf-8'))
for k in ('l3',):
    for a, b in zip(J0[k]['mechanism_chains'], J[k]['mechanism_chains']):
        for i, (x, y) in enumerate(zip(a['links'], b['links'])):
            for kk in x:
                if (a['id'], i, kk) not in (('M2-CN-PPI-CPI-SCISSORS', 1, 'missing_link_note'),
                                            ('M2-CN-PPI-CPI-SCISSORS', 1, 'evidence_refs'),
                                            ('M1-POLICY-RATES-ASSETS', 2, 'text')):
                    assert x[kk] == y[kk], (a['id'], i, kk)
        assert a['id'] == b['id'] and a['title'] == b['title'] and len(a['links']) == len(b['links'])
for a, b in zip(J0['reader_map']['regions'], J['reader_map']['regions']):
    assert a['region'] == b['region'] and a['anchor_echo'] == b['anchor_echo']
for i, (a, b) in enumerate(zip(J0['reader_map']['turnings'], J['reader_map']['turnings'])):
    for kk in a:
        if (i, kk) != (0, 'first_mover'):
            assert a[kk] == b[kk], (i, kk)
for i, (a, b) in enumerate(zip(J0['reader_map']['transmission'][0]['links'], J['reader_map']['transmission'][0]['links'])):
    for kk in a:
        if not (i < 2 and kk in ('observed_fact', 'competing_predicts', 'face_off_verdict', 'verdict_note')) \
                and not (i == 2 and kk == 'verdict_note'):
            assert a[kk] == b[kk], (i, kk)
assert {k: v for k, v in J0['reader_map'].items() if k not in ('headline_conclusion', 'turnings', 'regions', 'transmission')} == \
    {k: v for k, v in J['reader_map'].items() if k not in ('headline_conclusion', 'turnings', 'regions', 'transmission')}
for a, b in zip(J0['l3']['contradictions'], J['l3']['contradictions']):
    assert a['id'] == b['id'] and a['evidence_refs'] == b['evidence_refs']
for a, b in zip(J0['l4']['scenarios'], J['l4']['scenarios']):
    assert a['id'] == b['id'] and a['rows']['asset_direction'] == b['rows']['asset_direction'] \
        and a['rows']['sensitive_variables'] == b['rows']['sensitive_variables'] and a['rows']['trigger']['deadline'] == b['rows']['trigger']['deadline']
    assert a['rows']['falsification']['metric_id'] == b['rows']['falsification']['metric_id'] \
        and a['rows']['falsification']['secondary_metric_ids'] == b['rows']['falsification']['secondary_metric_ids']
for k in J0:
    if k not in ('l3', 'l4', 'quality_gate_notes', 'reader_map'):
        assert J0[k] == J[k], k
for i in (3, 4, 5, 7, 8, 9):
    assert J0['quality_gate_notes'][i] == Q[i], i
with open(j_out, 'w', encoding='utf-8') as fh:
    json.dump(J, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
rawb = open(j_out, 'rb').read()
print('wrote', j_out, len(rawb), 'bytes sha16', hashlib.sha256(rawb).hexdigest()[:16], '| run', RID,
      '| git_head', (R.get('git_head') or '')[:12], '| STRICT', STRICT)
print('replacements', len(LOG))
print('\n'.join(LOG))
