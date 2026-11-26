#!/usr/bin/python3 -I
"""fold_T36.py <judgment_in.json> <tree> <run_dir> <judgment_out.json>

Builder revision of the T3 work-order judgment (euro area / Japan official
policy targets, pending decisions and inflation year on year) after the
independent review it received at stamp 8f9055d (round 1, UPHELD: 0 MAJOR /
7 MINOR / 9 NIT, 396 points / 0 mismatches; the reviewer's final file is
recorded verbatim in the engine tree as VERDICT-20261123T213336Z-02, revision
2 -- revision 1 had been registered from the same reviewer's interim file
before its completion and is superseded, both records stay in the tree).  The
input is the judgment exactly as it stood when that review was made
(judgment5_T3.json), already re-bound to this run's round id by
restamp_judgment.py (the work order was re-planned at the new stamp; its
frozen inputs are the same).  Every number quoted in a
replacement sentence is recomputed here from the run's own frozen inputs
(root_overlay snapshot / release calendar / metric registry / report.json)
and asserted before the text is written.  Read-only on the run directory.

Folded (review item numbers as listed in VERDICT-round1.json):
  MINOR-1  ECB series: the registry's decision-driven freshness basis is
           set beside the lag basis (two bases coexist)
  MINOR-2  mechanism link 3: US policy-rate caliber (fed funds target range)
           beside the market-yield caliber; the row has no test power in the
           one-month window (pointer to an unrendered note replaced by the
           reason itself)
  MINOR-3  EA HICP publication: presumed final-release date, first release
           earlier by the two-tier form of the calendar records
  MINOR-4  headline / walk: the Japan tightening direction carries 【推断】
  MINOR-5  readings visible before a decision are latest-vintage values
  MINOR-6  single-day readings beside the jump-window cumulative reading
  MINOR-7  the six-month (question-window) cross-rate reading beside the
           one-month window: synthetic EURJPY -5.20% while the visible
           policy level gap is unchanged (added in the reviewer's final file)
  NIT-1    4.03 is a local high (not a one-year high: it is 22 months old)
  NIT-2    "about 1.25%" everywhere (calendar record wording)
  NIT-4    scenario S1 asset direction: the cited observations are compatible
           but their attribution is undecided (written into the direction
           text; the confidence tier itself is fixed by the contract to
           three values, so the reviewer's tier wording was not taken)
  NIT-5..9 wording and disclosure additions
Not adopted:
  NIT-3    verdict word stays 尚不能区分 (the tendency note lives in
           verdict_note, which the reader report does not render -- engine
           residual already registered; no judgment text can fix rendering)
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
    """sub() for one element of a list."""
    lst[i] = rep(lst[i], old, new)
    LOG.append('[%s] [%d]\n    - %s\n    + %s' % (where, i, old, new))


CS = J['l3']['contradictions']
MC = J['l3']['mechanism_chains'][0]
ML = MC['links']
RM = J['reader_map']
REG = RM['regions']
TR = RM['transmission'][0]['links']
TN = RM['turnings']
QG = J['quality_gate_notes']
assert [c['id'] for c in CS] == ['C1-INFL-DIVERGE', 'C2-POLICY-SYNC', 'C3-ECB-VISIBILITY']
assert MC['id'] == 'M1-INFL-POLICY-ASSET' and [l['step'] for l in ML] == [1, 2, 3, 4]
assert [r['region'] for r in REG] == ['EA', 'JP'] and len(TR) == 3 and len(TN) == 3
assert FR.as_of == '2026-11-23' and J['agent_declaration']['attribution'] == 'ai_inferred'
EI = [str(r['ref']) for r in json.load(open(os.path.join(rd, 'evidence_index.json'), encoding='utf-8'))]
assert len(EI) == 60 and 'DFEDTARL' not in ' '.join(EI) and 'DFEDTARU' not in ' '.join(EI) and 'UST_10Y@2026-11-19' in EI
print('evidence index rows', len(EI), '| fed funds in index:', [x for x in EI if 'DFEDTAR' in x], '| UST_10Y in index:', [x for x in EI if x.startswith('UST_10Y')])
ents = FR.cal.get('entries') if isinstance(FR.cal, dict) else FR.cal
cells = {c['metric_id']: c for c in FR.rep['research_plan']['point_values']['cells']}

# ---- facts shared by several items ------------------------------------------------
jc = FR.monthly('JP_CPI_YOY')
assert jc['2026-10'] == 2.44 and jc['2025-10'] == 2.99 and round(jc['2026-10'] - jc['2025-10'], 2) == -0.55
ser = sorted(jc.items())
assert max(ser, key=lambda kv: kv[1]) == ('2023-01', 4.31) and jc['2025-01'] == 4.03
assert all(v < 4.03 for k, v in ser if k > '2025-01')                       # local high since 2025-01
last12 = [kv for kv in ser if kv[0] >= '2025-11']
assert sum(1 for k, v in last12[:-1] if v < last12[-1][1]) == 10 and len(last12) == 12
assert round(jc['2026-10'] - jc['2026-09'], 2) == 0.28 and round(jc['2026-10'] - jc['2026-07'], 2) == 0.47 and round(jc['2026-10'] - jc['2026-04'], 2) == 1.06
jr = FR.monthly('JP_POLICY_RATE')
assert jr['2025-11'] == 0.478 and jr['2026-10'] == 1.227 and jr['2026-04'] == 0.727

# ---- MINOR-1: two freshness bases for the ECB series --------------------------------
for mid in ('ECB_MRO', 'ECB_DFR'):
    fr_ = FR.registry_metric(mid)['freshness']
    assert fr_['max_calendar_lag_days'] == 10 and fr_['decision_dated'] is True
    assert '无更晚已证实决议不作过期' in fr_['decision_dated_note'] and '观测日=政策最后确认/变更日' in fr_['decision_dated_note']
    a = cells[mid]['anchors']['最新一期']
    assert a['status'] == 'ok' and a.get('freshness_basis') == 'policy_confirmation' and a['observation_date'] == '2026-09-16'
    assert FR.last_date(mid) == '2026-09-16' and mid in (FR.snap.get('gate_a') or {}).get('noncore_degraded', [])
sub(CS[2], 'statement', 'L1 事实行 quality_status=DEGRADED;发布日历(',
    'L1 事实行 quality_status=DEGRADED;注册表对两序列另注决策驱动口径(观测日=政策最后确认/变更日,无更晚已证实决议不作过期),'
    '引擎点值格据此标 ok——两面口径并存,本档不以 degraded 推断有新决议,亦不以现值推断无新决议;发布日历(', 'MINOR-1')
sub(REG[0], 'from_to', '序列止于 2026-09-16(距截止 68 天,Gate A 列 degraded),其后决议面不可见【尚未验证】。',
    '序列止于 2026-09-16(距截止 68 天,Gate A 列 degraded;注册表另注决策驱动口径,点值格据此标 ok,两面并存),其后决议面不可见【尚未验证】。', 'MINOR-1')
sub(J['quality_gate_notes'], 4, '欧央行序列止于 2026-09-16(距截止 68 天,超注册表 10 天新鲜度阈,Gate A 列 degraded)',
    '欧央行序列止于 2026-09-16(距截止 68 天,超注册表 10 天新鲜度阈,Gate A 列 degraded;注册表同处另注决策驱动口径——'
    '观测日=政策最后确认/变更日,无更晚已证实决议不作过期,点值格据此标 ok,两面口径并列)', 'MINOR-1')

# ---- MINOR-2: US policy-rate caliber + no test power in the one-month window ---------
assert FR.last_date('DFEDTARL') == '2026-11-23' and FR.val('DFEDTARL', FR.as_of) == 3.75
assert FR.last_date('DFEDTARU') == '2026-11-23' and FR.val('DFEDTARU', FR.as_of) == 4.0
assert FR.last_date('UST_10Y') == '2026-11-19' and FR.val('UST_10Y', FR.as_of) == 5.04
assert FR.val('ECB_MRO', FR.as_of) == 2.65 and 3.75 > 2.65 and 3.75 > 1.25
sub(ML[2], 'text', '但该预期未纳入美元端利率(UST_10Y 最新 5.04%,高于 MRO 2.65% 与 BOJ 目标约 1.25%),利差主导对本月窗同样预期两货币对美元走弱;',
    '但该预期未纳入美元端利率(美元端政策利率口径: 快照序列面联邦基金目标区间 3.75%–4.00%,DFEDTARL/DFEDTARU 2026-11-23 观测,不在本轮证据索引;'
    'UST_10Y 最新 5.04% 为市场收益率口径,非政策利率),美元端政策利率同样高于 MRO 2.65% 与 BOJ 目标约 1.25%,利差主导对本月窗同样预期两货币对美元走弱;', 'MINOR-2')
sub(ML[2], 'text', '两解释在该观测上预期未分立——尚不能区分(置信有限;',
    '两解释在该观测上预期未分立——本行在本月窗对两解释无检验力,尚不能区分(置信有限;', 'MINOR-2')
sub(TR[1], 'causal_hypothesis', '该预期未纳入美元端利率——见裁定理由)',
    '该预期未纳入美元端利率: 美元端政策利率同样高于两地,利差主导对本月窗亦预期两货币对美元走弱,故本月窗两解释预期相同、无检验力)', 'MINOR-2')
sub(TR[1], 'verdict_note', '两解释在区分指标 EURUSD 上预期未分立——尚不能区分。置信有限:',
    '两解释在区分指标 EURUSD 上预期未分立——本月窗对两解释无检验力,尚不能区分。置信有限:', 'MINOR-2')

# ---- MINOR-3: EA HICP publication date is the presumed final-release date -------------
ea_hicp = [e for e in ents if e.get('metric_id') == 'EA_HICP_YOY']
assert sorted((e['first_publish_on_or_after'], e['final_publish_on']) for e in ea_hicp) == [
    ('2021-06-01', '2021-06-17'), ('2022-07-01', '2022-07-19'), ('2025-04-01', '2025-04-16')]
for e in ea_hicp:                       # flash on day 1 of the next month, final mid-month of that same month
    om = e['obs_to'][:7]
    nm = '%04d-%02d' % (int(om[:4]) + int(om[5:]) // 12, int(om[5:]) % 12 + 1)
    assert e['first_publish_on_or_after'] == nm + '-01' and e['final_publish_on'][:7] == nm and e['final_publish_on'] > e['first_publish_on_or_after'], e
rs = FR.registry_metric('EA_HICP_YOY')['release_semantics']
assert 'Eurostat月度HICP(次月中旬终值)' in rs and 'revision_semantics=latest_vintage_asof_collected' in rs
a = cells['EA_HICP_YOY']['anchors']['最新一期']
assert a['publication_date'] == '2026-11-16' and a['observation_date'] == '2026-10-01' and '推定' in a['publication_rule']
sub(CS[0], 'statement', '欧元区HICP同比最新读数百分之四点零(观测 2026-10,发布 2026-11-16,引擎推定规则、非日历实录)',
    '欧元区HICP同比最新读数百分之四点零(观测 2026-10,发布 2026-11-16 为引擎推定规则下的终值日,按冻结日历所载 EA HICP 实录的两档形态'
    '(次月首日快报+月中终值),该读数的首发不在该终值日;非日历实录)', 'MINOR-3')
sub(REG[0], 'from_to', '发布 2026-11-16,引擎推定规则、非日历实录。',
    '发布 2026-11-16 为引擎推定规则下的终值日(冻结日历所载 EA HICP 实录为次月首日快报+月中终值两档,首发不在该日),非日历实录。', 'MINOR-3')
sub(RM, 'headline_conclusion', '欧元区 HICP 同比 4.0%(观测 2026-10,发布 2026-11-16,推定规则)',
    '欧元区 HICP 同比 4.0%(观测 2026-10,推定终值发布日 2026-11-16,推定规则)', 'MINOR-3')

# ---- MINOR-4: Japan tightening direction is an inference -----------------------------
boj = [e for e in ents if e.get('metric_id') == 'JP_POLICY_TARGET']
assert sorted(e['entry_id'] for e in boj) == ['RC-JP-BOJ-MAINT-2026-10', 'RC-JP-BOJ-TARGET-2026-09']
assert all('约1.25%' in e['note'] and e['target_value'] == 1.25 for e in boj)
assert all(not any(k in e for k in ('previous_value', 'prior_target_value', 'prev_value', 'previous_target')) for e in boj)   # records carry no prior value
assert FR.registry_metric('JP_POLICY_TARGET') is None
sub(RM, 'headline_conclusion', '两地政策利率同向收紧——日本央行政策目标 1.25%(',
    '两地政策利率同向收紧——日本端方向为【推断】(实录无前值,依据月均市场利率台阶 0.478→1.227): 日本央行政策目标约 1.25%(', 'MINOR-4')
sub(REG[1], 'from_to', '2026-10-30 会议确认维持不变(无新调整、无生效变动)——注册表无 JP_POLICY_TARGET',
    '2026-10-30 会议确认维持不变(无新调整、无生效变动;日本端「收紧」方向依据月均市场利率台阶,实录无前值,属【推断】)——注册表无 JP_POLICY_TARGET', 'MINOR-4')

# ---- MINOR-5: latest-vintage readings ------------------------------------------------
assert cells['EA_HICP_YOY']['vintage_semantics'] == '事后回顾(最新修订值,非当时首发值)'
sub(TR[0], 'main_predicts', '生效日前可见 2026-08=3.2(发布日 2026-09-16 与生效日同日,先后时刻不可分)',
    '生效日前可见 2026-08=3.2(发布日 2026-09-16 与生效日同日,先后时刻不可分;读数为快照最新修订值,非当时首发值)', 'MINOR-5')
sub(TR[0], 'verdict_note', '故并列决议日前/生效日前两口径): 2026-06-17 生效前:',
    '故并列决议日前/生效日前两口径;读数为快照最新修订值,非当时首发值,修订量级参见注册表该序列的发布语义说明): 2026-06-17 生效前:', 'MINOR-5')

# ---- MINOR-6: single-day readings beside the cumulative window ------------------------


def day_chg(mid, day):
    d, v = ss[mid]['dates'], ss[mid]['values']
    i = d.index(day)
    return round((v[i] / v[i - 1] - 1) * 100, 2)


x1120 = {m: day_chg(m, '2026-11-20') for m in ('NIKKEI225', 'SPX', 'DAX', 'CAC40')}
x1116 = {m: day_chg(m, '2026-11-16') for m in ('NIKKEI225', 'SPX', 'DAX', 'CAC40')}
assert x1120 == {'NIKKEI225': -5.06, 'SPX': -3.7, 'DAX': -2.6, 'CAC40': -1.89}, x1120
assert x1116 == {'NIKKEI225': -2.42, 'SPX': -1.92, 'DAX': -0.57, 'CAC40': -0.2}, x1116
jump = {}                                                                   # largest single-day drop inside the jump window
for m in ('NIKKEI225', 'SPX', 'DAX', 'CAC40'):
    for day in ('2026-11-16', '2026-11-17', '2026-11-18', '2026-11-19', '2026-11-20'):
        if day in ss[m]['dates']:
            jump[(m, day)] = day_chg(m, day)
assert min(jump, key=jump.get) == ('NIKKEI225', '2026-11-20') and jump[('NIKKEI225', '2026-11-20')] == -5.06
assert x1120['NIKKEI225'] < x1120['SPX'] < x1120['DAX'] < x1120['CAC40']
assert x1116['DAX'] > x1116['SPX'] and x1116['CAC40'] > x1116['SPX']
cum = {m: round((ss[m]['values'][ss[m]['dates'].index('2026-11-20')] / ss[m]['values'][ss[m]['dates'].index('2026-11-13')] - 1) * 100, 2)
       for m in ('NIKKEI225', 'SPX', 'DAX', 'CAC40')}                  # jump-window cumulative change
assert cum == {'NIKKEI225': -7.7, 'SPX': -8.61, 'DAX': -7.28, 'CAC40': -5.27}, cum
assert all(cum[m] > cum['SPX'] for m in ('NIKKEI225', 'DAX', 'CAC40'))   # no region deeper than the US inside the jump window
SINGLE = ('读数发布主因未获跨地区支持(按跳升窗内累计跌幅判读;单日看 2026-11-20 NIKKEI225 -5.06% 深于 SPX -3.70%,为窗内四地最大单日跌幅,'
          '与全局冲击相容,不足以区分发布主因与全局冲击)')
sub(ML[3], 'text', '读数发布主因未获跨地区支持', SINGLE, 'MINOR-6')
sub(TR[2], 'verdict_note', '读数发布主因未获跨地区支持', SINGLE, 'MINOR-6')

# ---- MINOR-7: six-month (question-window) cross reading beside the one-month window ------
common = sorted(set(ss['EURUSD']['dates']) & set(ss['USDJPY']['dates']))


def at(mid, day):
    d, v = ss[mid]['dates'], ss[mid]['values']
    i = max(k for k, x in enumerate(d) if x <= day)
    return d[i], v[i]


start = [x for x in common if x <= '2026-05-23'][-1]                    # question window: last six months from 2026-05-23
assert start == '2026-05-22'
e0, u0 = at('EURUSD', start)[1], at('USDJPY', start)[1]
e1, u1 = at('EURUSD', '2026-11-20')[1], at('USDJPY', '2026-11-20')[1]
pc = lambda a, b: round((b / a - 1) * 100, 2)                            # noqa: E731
x0, x1 = e0 * u0, e1 * u1
assert (round(x0, 4), round(x1, 4)) == (184.7972, 175.1941) and pc(x0, x1) == -5.2 and pc(e0, e1) == -5.61 and pc(u0, u1) == 0.43
d_mro, v_mro = ss['ECB_MRO']['dates'], ss['ECB_MRO']['values']
chg = [(d_mro[i], v_mro[i - 1], v_mro[i]) for i in range(1, len(d_mro)) if v_mro[i] != v_mro[i - 1] and d_mro[i] >= '2026-01-01']
assert chg == [('2026-06-17', 2.15, 2.4), ('2026-09-16', 2.4, 2.65)] and at('ECB_MRO', start) == ('2025-06-11', 2.15)
assert jr['2026-05'] == 0.727 and jr['2026-10'] == 1.227
g0, g1 = round(2.15 - jr['2026-05'], 3), round(2.65 - jr['2026-10'], 3)
assert (g0, g1) == (1.423, 1.423) and round(2.65 - 2.15, 2) == 0.5 and round(jr['2026-10'] - jr['2026-05'], 2) == 0.5
SIX_OBS = ('问句窗六个月(2026-05-22 收盘→2026-11-20 收盘): 合成交叉盘由 184.80 降至 175.19(-5.20%;腿: EURUSD -5.61%、USDJPY +0.43%)。')
sub(TR[1], 'observed_fact', '幅度小;本月窗两地政策水平差未变,利差假说对交叉盘方向无明确预期,该面不构成检验。',
    '幅度小;本月窗两地政策水平差未变,利差假说对交叉盘方向无明确预期,该面不构成检验。' + SIX_OBS, 'MINOR-7')
sub(ML[2], 'text', '幅度小,利差渠道未获检验亦未被否定)',
    '幅度小;本月窗利差渠道未获检验亦未被否定。并列' + SIX_OBS +
    '同期可见的两地政策水平差未变——MRO 2.15%(2026-06-17 变更前)减日本政策利率 2026-05 月均 0.727% 得 1.423 个百分点,'
    'MRO 2.65%(2026-09-16 起)减 2026-10 月均 1.227% 得 1.423 个百分点,欧央行两度上调合计 0.5 个百分点、日本政策利率月均亦抬升 0.5 个百分点;'
    '利差渠道解释不了这段下跌,美元端主导解释对两腿分立(欧元深跌、日元近平)亦无预期,两解释对该读数均无明确预期,仍不构成检验)', 'MINOR-7')
sub(TR[1], 'verdict_note', '幅度小,利差渠道未获检验亦未被否定。',
    '幅度小;本月窗利差渠道未获检验亦未被否定。并列' + SIX_OBS +
    '同期可见的两地政策水平差未变(MRO 减日本政策利率月均: 2.15−0.727=1.423 → 2.65−1.227=1.423 个百分点)——'
    '利差渠道解释不了六个月窗的交叉盘下跌,但美元端主导解释对两腿分立亦无预期,两解释对该读数均无明确预期,仍不构成检验;『未被否定』只在本月窗内成立。', 'MINOR-7')

# ---- NIT-1: local high, not a one-year high -------------------------------------------
sub(ML[0], 'text', 'JP_CPI_YOY 自 2025-01 高点 4.03 回落(非逐月单调,',
    'JP_CPI_YOY 自 2025-01 的局部高点 4.03 回落(此后至最新观测月未再越过;全序列最高为 2023-01 的 4.31;非逐月单调,', 'NIT-1')
sub(REG[1], 'from_to', '——自 2025-01 高点 4.03 回落(2025-09、2025-10 两度小幅回升至 2.91、2.99)',
    '——自 2025-01 的局部高点 4.03 回落(全序列最高为 2023-01 的 4.31;2025-09、2025-10 两度小幅回升至 2.91、2.99)', 'NIT-1')

# ---- NIT-2: "about 1.25%" in every field ---------------------------------------------


def all_strings(o, p=''):
    """(dotted path, string) for every string leaf; path like '.l3.contradictions[0].statement'."""
    if isinstance(o, dict):
        for k, v in o.items():
            for pp, s in all_strings(v, p + '.' + k):
                yield pp, s
    elif isinstance(o, list):
        for i, v in enumerate(o):
            for pp, s in all_strings(v, '%s[%d]' % (p, i)):
                yield pp, s
    elif isinstance(o, str):
        yield p, o


def set_path(root, path, value):
    toks = [t for t in path.replace('[', '.').replace(']', '').split('.') if t]
    cur = root
    for t in toks[:-1]:
        cur = cur[int(t)] if isinstance(cur, list) else cur[t]
    last = toks[-1]
    if isinstance(cur, list):
        cur[int(last)] = value
    else:
        cur[last] = value


n_before = sum(s.count('目标 1.25%') for _p, s in all_strings(J))
assert n_before == 3 and '目标约约' not in json.dumps(J, ensure_ascii=False)      # the headline occurrence was folded under MINOR-4
sub(REG[1], 'from_to', '政策目标利率 1.25%,2026-09-18 决议', '政策目标利率约 1.25%,2026-09-18 决议', 'NIT-2')
for p, s in list(all_strings(J)):
    if '目标 1.25%' in s:
        new = s.replace('目标 1.25%', '目标约 1.25%')
        set_path(J, p, new)
        LOG.append('[NIT-2] %s\n    - 目标 1.25%%\n    + 目标约 1.25%% (x%d)' % (p.lstrip('.'), s.count('目标 1.25%')))
assert sum(s.count('目标 1.25%') + s.count('目标利率 1.25%') for _p, s in all_strings(J)) == 0
assert sum(s.count('目标约 1.25%') + s.count('目标利率约 1.25%') for _p, s in all_strings(J)) >= n_before + 3   # + headline, walk, and the MINOR-2 link text

# ---- NIT-4..9 ---------------------------------------------------------------------------
# NIT-4 (reviewer's suggested tier wording): the contract fixes the three confidence tiers
# ('有历史相似证据', '有相关证据', '纯逻辑推理') -- the tier stays; the caveat goes into the direction text.
assert J['l4']['scenarios'][0]['id'] == 'S1-STICKY-TIGHTEN'
S1 = J['l4']['scenarios'][0]['rows']['asset_direction']
assert S1['confidence_tier'] == '有相关证据' and S1['evidence_refs'] == ['NIKKEI225@2026-11-20', 'VIX@2026-11-23']
sub(S1, 'direction', '波动率维持高位;此为方向性推演,非幅度预测',
    '波动率维持高位;此为方向性推演,非幅度预测(所引两项为同窗方向观察,与该方向相容但归因未定,不构成支持性证据)', 'NIT-4')
assert TN[1]['metric_id'] == 'EA_HICP_YOY' and TN[1]['date'] == '2026-05'
assert FR.level_before('ECB_MRO', '2026-06-17')[0] < '2026-06-17' and FR.val('ECB_MRO', '2026-06-17') == 2.4
sub(TN[1], 'follow_or_diverge', '——跟进方向一致,月频先后未定。',
    '——跟进方向一致;生效日 2026-06-17 晚于转折段终点月 2026-05,读数可见性与决议时点的先后未定。', 'NIT-5')
n_ref = sum(s.count('点值取自快照序列面、L1 无对应事实行') for _p, s in all_strings(J))
assert n_ref == 2 and 'JP_CPI_TOKYO_YOY' in (FR.snap.get('gate_a') or {}).get('noncore_missing', [])
sub(CS[0], 'statement', '点值取自快照序列面、L1 无对应事实行', '点值取自快照序列面、仅作参考,L1 无对应事实行', 'NIT-6')
sub(REG[1], 'from_to', '点值取自快照序列面、L1 无对应事实行', '点值取自快照序列面、仅作参考,L1 无对应事实行', 'NIT-6')
l1 = {(r.get('metric_id')): r for r in (FR.rep['layers'].get('L1_事实层') or {}).get('rows', [])}
assert l1['JP_POLICY_RATE']['quality_status'] == 'WARN' and l1['JP_POLICY_RATE']['observation_date'] == '2026-10-01'
a = cells['JP_POLICY_RATE']['anchors']['最新一期']
assert a['publication_date'] == '2026-11-05' and a['observation_date'] == '2026-10-01' and '推定' in a['publication_rule']
sub(CS[1], 'statement', '最新一期报 1.227%,六个月前锚前值为零点七二七',
    '最新一期报 1.227%(观测月 2026-10,推定发布日 2026-11-05,L1 quality_status=WARN),六个月前锚前值为零点七二七', 'NIT-7')
sub(J['quality_gate_notes'], 5, '本档陈述层对无别名指标的数值一律用中文数字表述',
    '本档三条矛盾陈述正文对无别名指标的数值一律用中文数字表述', 'NIT-8')
sub(CS[0], 'statement', '去年同月(2025-10)为百分之二点九九,回落约零点五五个百分点;',
    '去年同月(2025-10)为百分之二点九九,回落约零点五五个百分点(回落仅相对去年同月成立: 近十二个月中其余十一个月里有十个月读数低于最新值,'
    '较一、三、六个月前分别高零点二八、零点四七、一点零六,总体处于回升段);', 'NIT-9')

with open(j_out, 'w', encoding='utf-8') as fh:
    json.dump(J, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
print('\n'.join(LOG))
print('folded %d edits | in=%s out=%s run=%s git=%s' % (len([x for x in LOG if x.startswith('[')]), j_in, j_out, RID, (R.get('git_head') or '')[:12]))
