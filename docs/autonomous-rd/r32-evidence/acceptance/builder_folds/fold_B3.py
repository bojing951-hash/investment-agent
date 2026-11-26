#!/usr/bin/python3
"""fold_B3.py <judgment_in.json> <faces.json> <run_dir> <judgment_out.json>

Operator text review of the B (US/EA three-month comparison + BOJ policy
level/duration) judgment after the A fold-in: same defect classes, same
treatment.  Every number is recomputed from the run's own frozen inputs
(root_overlay snapshot / calendar / registry); each replacement is guarded
(exactly one occurrence, or an asserted count) so a drifted base text fails
loudly.  Adds `quality_gate_notes` (disclosure block; no engine code reads
it).  Read-only on the run directory.
"""
import copy
import datetime
import json
import os
import sys
sys.path.insert(0, '/tmp/r32-accept/scripts')
import seatlib_r32 as L                                  # noqa: E402

j_in, faces_p, rd, j_out = sys.argv[1:5]
FR = L.Frozen(rd)
AS_OF = FR.as_of
F = json.load(open(faces_p, encoding='utf-8'))
J = copy.deepcopy(json.load(open(j_in, encoding='utf-8')))
assert F['report_dir'] == rd, (F['report_dir'], rd)
D0 = datetime.date.fromisoformat(AS_OF)
CN_NUM = '零一二三四五六七八九'


def rep(s, old, new, n=1):
    assert s.count(old) == n, ('anchor count', s.count(old), n, old[:48])
    return s.replace(old, new)


def yoy(mid, ym):
    p = FR.monthly(mid)
    k = '%04d-%02d' % (int(ym[:4]) - 1, int(ym[5:7]))
    return None if k not in p or ym not in p else (p[ym] / p[k] - 1) * 100


def bp(x):
    return '%+d' % int(round(x))


def cn_count(k):
    if k < 10:
        return CN_NUM[k]
    if k < 20:
        return '十' + (CN_NUM[k - 10] if k > 10 else '')
    return CN_NUM[k // 10] + '十' + (CN_NUM[k % 10] if k % 10 else '')


# ── computed facts ──────────────────────────────────────────────────────
WIN0 = (D0 - datetime.timedelta(days=365)).isoformat()
TRIO = F['us_rates_trio']
W1, W12 = TRIO['window'], TRIO['window_12m']
assert W12 == {'from': '2025-11-19', 'to': '2026-11-19', 'calendar_days_between': 365}
C1B, C12 = TRIO['chg_bp'], TRIO['chg_bp_12m']
assert (C1B['UST_10Y'], C1B['TIPS_10Y'], C1B['BEI_10Y']) == (-8.0, 11.0, -19.0)
assert (C12['UST_10Y'], C12['TIPS_10Y'], C12['BEI_10Y']) == (91.0, 102.0, -11.0)
BEI, TIPS = 'BEI_10Y', 'TIPS_10Y'
bei_up_d0, bei_up_d1 = '2026-02-27', '2026-05-04'              # 通胀上行段内的低/高点
_pre = [(d, v) for d, v in zip(FR.ss[BEI]['dates'], FR.ss[BEI]['values']) if '2026-02-01' <= d <= '2026-06-10']
assert min(_pre, key=lambda x: x[1])[0] == bei_up_d0 and max(_pre, key=lambda x: x[1])[0] == bei_up_d1
bei_up_v0, bei_up_v1 = FR.val(BEI, bei_up_d0), FR.val(BEI, bei_up_d1)
assert (bei_up_v0, bei_up_v1) == (2.25, 2.50)
assert FR.val(BEI, W12['from']) == 2.27 and FR.val(BEI, W12['to']) == 2.16
bei_last_d, bei_last = FR.last_date(BEI), FR.val(BEI, AS_OF)
assert bei_last_d == '2026-11-20' and bei_last == 2.15
tips_m_bp = round((FR.val(TIPS, W12['to']) - FR.val(TIPS, '2026-10-23')) * 100)
assert tips_m_bp == 22 and FR.val(TIPS, '2026-10-23') == 2.66 and FR.val(TIPS, W12['to']) == 2.88
# 与本问同口径的三个月窗(三序列共同交易日)
TRIO3 = ('UST_10Y', TIPS, BEI)
COM = sorted(set.intersection(*(set(FR.ss[m]['dates']) for m in TRIO3)))
D3 = max(d for d in COM if d <= '2026-08-19')
assert D3 == '2026-08-19' and W12['to'] == '2026-11-19'
V0 = {m: FR.val(m, D3) for m in TRIO3}
V1 = {m: FR.val(m, W12['to']) for m in TRIO3}
CHG3 = {m: round((V1[m] - V0[m]) * 100) for m in TRIO3}
assert CHG3 == {'UST_10Y': 39, 'TIPS_10Y': 53, 'BEI_10Y': -14}, CHG3
assert CHG3['UST_10Y'] == CHG3[TIPS] + CHG3[BEI]                # 残差 0
assert CHG3[TIPS] > CHG3['UST_10Y'] > 0 > CHG3[BEI]             # 名义上行全部来自实际利率
# inflation paths (index -> yoy)
cc = {ym: yoy('CORE_CPI', ym) for ym in FR.monthly('CORE_CPI')}
cy = {ym: yoy('CPI', ym) for ym in FR.monthly('CPI')}
ea = FR.monthly('EA_HICP_YOY')
assert round(cc['2026-02'], 4) == 2.4725 and round(cc['2026-05'], 4) == 2.8229
assert round(cc['2026-08'], 4) == 2.4462 and round(cc['2026-09'], 4) == 2.5658
assert round(cy['2026-02'], 3) == 2.434 and round(cy['2026-05'], 4) == 4.1666
assert round(cy['2026-07'], 2) == 3.30 and round(cy['2026-09'], 2) == 3.72 and yoy('CPI', '2026-10') is None
assert [ea[k] for k in ('2026-02', '2026-05', '2026-06', '2026-07', '2026-08', '2026-10')] == [1.9, 3.2, 2.8, 2.9, 3.2, 4.0]
assert max(v for k, v in ea.items() if k.startswith('2026')) == 4.0 == ea['2026-10']   # 年内新高
# Japan policy path
JP = FR.monthly('JP_POLICY_RATE')
CELLS = {c['metric_id']: c for c in FR.rep['research_plan']['point_values']['cells']}
wp = CELLS['JP_POLICY_RATE']['policy_window_path']
assert wp['net_bp'] == 67 and wp['window_start_value'] == 0.557 and wp['window_end_value'] == 1.227
jp_carry, jp_last = JP['2025-11'], JP['2026-10']
assert (jp_carry, JP['2025-12'], jp_last) == (0.478, 0.557, 1.227)
assert round((jp_last - jp_carry) * 100) == 75 and round((jp_last - JP['2025-12']) * 100) == 67
cal = FR.cal
ent = cal.get('entries') or []
pol_ent = [e for e in ent if str(e.get('kind', '')).startswith('policy')]
assert len(pol_ent) == 2 and all('JP' in e['entry_id'] for e in pol_ent)   # 冻结日历的政策实录仅日本两条,无美欧决议/生效条目
pol = {e['kind']: e for e in pol_ent}
assert set(pol) == {'policy_decision', 'policy_maintenance'}
# 美国端只有会议纪要文档事实(工单冻结面 policy_doc_facts),纪要发布≠决议日
ENV = json.load(open(os.path.join(rd, 'AGENT_SEAT_ENVELOPE.json'), encoding='utf-8'))
PDF = ENV['reader_map_contract']['engine_faces']['policy_doc_facts']
assert [(d['doc_id'], d['kind'], d['meeting_month'], d['published_on']) for d in PDF] == [
    ('FOMC-MINUTES-2026-10', 'minutes', '2026-10', '2026-11-18')]
assert (pol['policy_decision']['entry_id'], pol['policy_decision']['decision_date'],
        pol['policy_decision']['effective_on'], pol['policy_decision']['target_value']) == (
    'RC-JP-BOJ-TARGET-2026-09', '2026-09-18', '2026-09-24', 1.25)
assert (pol['policy_maintenance']['entry_id'], pol['policy_maintenance']['decision_date'],
        pol['policy_maintenance']['target_value']) == ('RC-JP-BOJ-MAINT-2026-10', '2026-10-30', 1.25)
assert pol['policy_maintenance'].get('effective_on') is None                 # 维持条目无生效日,正文不得挂"生效"
d_eff = (D0 - datetime.date.fromisoformat('2026-09-24')).days
d_dec = (D0 - datetime.date.fromisoformat('2026-09-18')).days
assert (d_eff, d_dec) == (60, 66)
# STALE-labelled citations are the newest published observations of their series
assert FR.last_date('CORE_PCE') == '2026-09-01' and FR.last_date('US_REAL_GDP') == '2026-07-01'
stale_txt = []
for mid in ('CORE_PCE', 'US_REAL_GDP'):
    reg = FR.registry_metric(mid)
    lag = (D0 - datetime.date.fromisoformat(FR.last_date(mid))).days
    mx = ((reg.get('freshness') or {}).get('max_calendar_lag_days'))
    assert isinstance(mx, int) and 1.0 <= lag / mx < 2.0, (mid, lag, mx)       # 一级陈旧: 滞后<2倍注册表节奏
    stale_txt.append('%s(观测 %s，距截止日 %d 天，为注册表最大日历滞后 %d 天的 %.1f 倍)'
                     % (mid, FR.last_date(mid), lag, mx, lag / mx))
# assets (intraday snapshot vs same-day close)
AB = L.asset_block(FR, '2026-10-23')
CLOSE = AB['close_day']
assert CLOSE == '2026-11-20' and AB['equity']['SPX']['intraday'][0] and AB['vix_intraday'][0]
AM = {r['metric_id']: r for r in F['asset_moves']['rows']}
assert AM['SPX']['window'] == {'from': '2026-10-23', 'to': AS_OF} and AM['NIKKEI225']['window']['to'] == CLOSE
assert round(AB['equity']['SPX']['ret'], 2) == -9.36 and round(AB['vix_month_close'], 2) == 84.52


def close_ret(m, d_from, d_to):
    """同日收盘口径变动: 两端取各自不晚于目标日的最后收盘观测。"""
    s = FR.ss[m]
    a = max(d for d in s['dates'] if d <= d_from)
    b = max(d for d in s['dates'] if d <= d_to)
    return a, b, FR.val(m, a), FR.val(m, b), (FR.val(m, b) / FR.val(m, a) - 1) * 100


R3 = {m: close_ret(m, '2026-08-19', CLOSE) for m in ('SPX', 'VIX')}
assert (R3['SPX'][0], R3['SPX'][1]) == ('2026-08-19', CLOSE) and round(R3['SPX'][4], 2) == -10.35
assert (R3['VIX'][0], R3['VIX'][1]) == ('2026-08-19', CLOSE) and round(R3['VIX'][4], 2) == 141.03
assert round(R3['VIX'][2], 2) == 14.89 and round(R3['VIX'][3], 2) == 35.89
# faces
assert len(F['evidence_index']) == 63 and len(CELLS) == 9
CAND = F['turning_candidates']['candidates']
assert len(CAND) == 7 and F['turning_candidates']['top_n_expected'] == 3
assert sorted((c['metric_id'], c.get('date') or c.get('to_ym')) for c in CAND) == sorted(
    [('CPI', '2026-05'), ('EA_HICP_YOY', '2026-05'), ('INDPRO', '2026-02'), ('CORE_CPI', '2026-08'),
     ('JP_POLICY_RATE', '2026-07'), ('CORE_PCE', '2026-02'), ('UNEMPLOYMENT', '2026-08')])
GA = FR.snap.get('gate_a') or {}
ncm, ncd = GA.get('noncore_missing') or [], GA.get('noncore_degraded') or []
assert GA.get('status') == 'DEGRADED' and not (GA.get('core_missing') or []) and len(ncm) == 7 and len(ncd) == 8
ncm_cited = [m for m in ncm if m in ('EA_REAL_GDP_YOY',)]
assert ncm_cited == ['EA_REAL_GDP_YOY'] and FR.last_date('EA_REAL_GDP_YOY') == '2026-07-01'
print('stale', stale_txt)
print('ncm', ncm, '| ncd', ncd, '| cited-with-store-data', ncm_cited)

# ── texts ───────────────────────────────────────────────────────────────
rm = J['reader_map']
SNAP_OLD = '当日实时快照'
n_snap = json.dumps(J, ensure_ascii=False).count(SNAP_OLD)
assert n_snap == 4, n_snap                                     # headline, C3, chain link 2, M1 step 3


def fix_snapshot(s):
    return s.replace('(观测 2026-11-23,当日实时快照,非收盘价)', '(观测 2026-11-23，盘中快照、非收盘价)').replace(
        '11-23 值为当日实时快照(非收盘价)', '11-23 值为盘中快照(非收盘价)')


J['agent_declaration']['basis'] = rep(
    J['agent_declaration']['basis'], '转折候选面(top3)', '转折候选面(候选池%d、top%d)'
    % (len(CAND), F['turning_candidates']['top_n_expected']))

C = J['l3']['contradictions']
assert [c['id'] for c in C] == ['C1-INFL-SYNC', 'C2-GROWTH-STABLE', 'C3-JP-POLICY']
C[0]['statement'] = fix_snapshot(C[0]['statement'])
C[2]['statement'] = fix_snapshot(C[2]['statement'])
C[2]['statement'] = rep(
    C[2]['statement'], '距上次调整按生效日六十天、按决议日六十六天(约两个月)。',
    '距上次调整按生效日六十天、按决议日六十六天(约两个月)。月均口径的 12 个月净变动有两种起算口径: 引擎『政策一年窗路径』面板按窗内首观测起算为正%s个基点，'
    '按『窗启时在值(2025-11 月均零点%s)→窗末观测』为正%s个基点，两种口径本档并列披露(数字见走位面与披露块)。'
    % (cn_count(round((jp_last - JP['2025-12']) * 100)),
       ''.join(CN_NUM[int(ch)] for ch in ('%.3f' % jp_carry).split('.')[1]),
       cn_count(round((jp_last - jp_carry) * 100))))      # 矛盾陈述内不带阿拉伯数字(与"约一点二五"同惯例)

M = J['l3']['mechanism_chains']
assert [m['id'] for m in M] == ['M1-JP-RATE-PATH'] and len(M[0]['links']) == 3
m0, m2 = M[0]['links'][0], M[0]['links'][2]
m0['text'] = rep(
    m0['text'], '观察: JP_POLICY_RATE 月均自 2025-11(政策窗启前一格,值 0.478)经 2025-12 的 0.557 抬升至 2026-10 的 1.227,'
    '近 12 个月政策窗(2025-11-23..2026-11-23)净变动 +67bp(引擎政策窗口径=窗首尾观测差),',
    '观察: JP_POLICY_RATE 月均自 2025-11 的 0.478(窗启时在值)经 2025-12 的 0.557 抬升至 2026-10 的 1.227，'
    '近 12 个月政策窗(2025-11-23..2026-11-23)净变动 +67bp(引擎政策窗口径=窗首尾观测差，自 2025-12 月均起算；'
    '按『窗启时在值→窗末观测』口径为 +75bp)，')
m2['text'] = fix_snapshot(m2['text'])

# headline / regions
assert 'HICP 同比至 2026-10 达 4.0%' in rm['headline_conclusion']
rm['headline_conclusion'] = fix_snapshot(rm['headline_conclusion'])
RG = {r['region']: r for r in rm['regions']}
assert sorted(RG) == ['EA', 'JP', 'US']
RG['EA']['from_to'] = rep(
    RG['EA']['from_to'], '且自 2026-02 的 1.9 抬升至 2026-05 的 3.2 后未回落,读数为年内新高。',
    '且自 2026-02 的 1.9 抬升至 2026-05 的 3.2，2026-06 回落至 2.8 后再度上行至 2026-10 的 4.0，读数为年内新高。')
RG['JP']['from_to'] = rep(
    RG['JP']['from_to'], '近 12 个月政策窗净变动 +67bp(引擎政策窗口径)。',
    '近 12 个月政策窗净变动 +67bp(引擎政策窗口径=窗首尾观测差，自 2025-12 月均起算；按窗启时在值 2025-11 月均 0.478 起算为 +75bp)。')

# transmission chain
TR = rm['transmission']
assert len(TR) == 1 and len(TR[0]['links']) == 3
L0, L1, L2 = TR[0]['links']
for lk in (L0, L1, L2):
    lk['observed_fact'] = fix_snapshot(lk['observed_fact'])
# link 0: BEI 两段方向相反 → 尚不能区分(verdict_note 不渲染,理由写入渲染面)
assert L0['face_off_verdict'] == '支持竞争解释' and L0['distinguishing_metric'] == BEI
INFL_UP = ('2026-02', '2026-05')                               # 转折候选的三个月窗(before_date→date),非"自低点"
assert cy[INFL_UP[1]] == max(v for k, v in cy.items() if k >= '2026-01' and v is not None) and cy[INFL_UP[1]] > cy[INFL_UP[0]]
assert ea[INFL_UP[1]] == max(v for k, v in ea.items() if '2026-01' <= k < '2026-06') and ea[INFL_UP[1]] > ea[INFL_UP[0]]
L0['observed_fact'] += (
    '区分指标 BEI_10Y 在各窗方向不一致: 与本问同口径的三个月窗(%s→%s)自 %s 回落至 %s(%sbp)，近一月共同交易日窗(%s→%s)变动 %sbp、'
    '12 个月窗(%s→%s)变动 %sbp，最新 %s(观测 %s)，而通胀读数仍处高位(欧元区 2026-10 达 %s、为年内新高；美国 CPI 同比 2026-09 回升至 %s，'
    '仍低于 2026-05 高点 %s)——合竞争解释中「盈亏平衡不必然走高」一半，但其「通胀读数数月内自行回落」一半尚未兑现；'
    '相反方向的证据来自更早的通胀上行段(三个月窗 %s→%s): BEI_10Y 自 %s 的 %s 升至 %s 的 %s，合主解释。'
    % (D3, W12['to'], L.f2(V0[BEI]), L.f2(V1[BEI]), bp(CHG3[BEI]), W1['from'], W1['to'], bp(C1B[BEI]),
       W12['from'], W12['to'], bp(C12[BEI]), L.f2(bei_last), bei_last_d, '%.1f' % ea['2026-10'],
       L.f2(cy['2026-09']), L.f2(cy['2026-05']), INFL_UP[0], INFL_UP[1], bei_up_d0, L.f2(bei_up_v0), bei_up_d1, L.f2(bei_up_v1)))
L0['face_off_verdict'] = '尚不能区分'
L0['verdict_note'] = ('各窗方向不一致: 三个月窗 %sbp、近一月 %sbp 合竞争解释，更早的 %s→%s 上行段合主解释——尚不能区分；'
                      '竞争解释的「自行回落」一半尚未兑现。'
                      % (bp(CHG3[BEI]), bp(C1B[BEI]), bei_up_d0, bei_up_d1))
# link 1: 主解释的支持来自三个月窗与 12 个月窗(渲染面补齐;单月窗盈亏平衡幅度更大须披露)
assert L1['face_off_verdict'] == '支持主解释' and L1['distinguishing_metric'] == TIPS
assert all(ch[TIPS] > 0 > ch[BEI] for ch in (CHG3, C1B, C12))            # 三窗均为"实际上行、盈亏平衡回落"
assert CHG3[TIPS] > CHG3['UST_10Y'] and C12['TIPS_10Y'] > C12['UST_10Y']  # 名义上行的两窗: 实际分量幅度超过名义变动
L1['observed_fact'] += (
    '与本问同口径的三个月窗(%s→%s)名义 %sbp=实际 %sbp+盈亏平衡 %sbp(残差 0)，12 个月窗(%s→%s)名义 +%.0fbp=实际 +%.0fbp+盈亏平衡 %.0fbp(残差 0)'
    '——两窗名义上行均由实际利率主导(实际分量幅度超过名义变动)；三个月、近一月、12 个月三窗均为「实际利率上行、盈亏平衡回落」，'
    '不合竞争解释「无稳定主导关系」的预期，这是「实际利率为名义利率主导上行分量」的证据来源；'
    '单月窗内名义利率下行、盈亏平衡变动幅度大于实际利率，单看单月窗不足以支持该主张。'
    '注: 「通胀走高而盈亏平衡回落」的组合与竞争解释的文字描述亦相容，该描述不构成两侧的区分预期，裁定只针对预注册的区分预期。'
    % (D3, W12['to'], bp(CHG3['UST_10Y']), bp(CHG3[TIPS]), bp(CHG3[BEI]), W12['from'], W12['to'],
       C12['UST_10Y'], C12['TIPS_10Y'], C12['BEI_10Y']))
L1['verdict_note'] = ('三个月窗实际 %sbp 主导名义 %sbp、12 个月窗实际 +%.0fbp 主导名义 +%.0fbp，合主解释；三窗均为实际上行、盈亏平衡回落，'
                      '主导关系稳定；单月窗 TIPS_10Y %sbp 为唯一上行分量但幅度小于盈亏平衡 %sbp(名义 %sbp)，单月窗不足以单独支持'
                      '——裁定基于三个月窗与 12 个月窗，单月窗证据有限。'
                      % (bp(CHG3[TIPS]), bp(CHG3['UST_10Y']), C12['TIPS_10Y'], C12['UST_10Y'],
                         bp(C1B['TIPS_10Y']), bp(C1B[BEI]), bp(C1B['UST_10Y'])))
# link 2: 同日收盘口径对照 + 同窗 TIPS
assert L2['face_off_verdict'] == '支持主解释' and L2['distinguishing_metric'] == TIPS
L2['observed_fact'] += (
    '同窗 TIPS_10Y %s→%s(+%dbp，2026-10-23→2026-11-19)；同日收盘口径(2026-10-23→%s): 标普500指数 %s、VIX %s；'
    '三个月收盘口径(%s→%s): 标普500指数 %s、VIX %s(%s→%s)，同窗 TIPS_10Y +%dbp(利率序列止于 %s)。'
    'VIX 的涨幅幅度提示流动性/仓位因素可能叠加，单月窗不能完全区分。'
    % (L.f2(FR.val(TIPS, '2026-10-23')), L.f2(FR.val(TIPS, W12['to'])), tips_m_bp, CLOSE,
       L.sgn2(AB['equity']['SPX']['ret']), L.sgn2(AB['vix_month_close']),
       R3['SPX'][0], R3['SPX'][1], L.sgn2(R3['SPX'][4]), L.sgn2(R3['VIX'][4]),
       '%.2f' % R3['VIX'][2], '%.2f' % R3['VIX'][3], CHG3[TIPS], W12['to']))

# turnings
TU = {('%s@%s' % (t['metric_id'], t['date'])): t for t in rm['turnings']}
assert sorted(TU) == ['CPI@2026-05', 'EA_HICP_YOY@2026-05', 'JP_POLICY_RATE@2026-07']
TU['CPI@2026-05']['narrative'] = rep(
    TU['CPI@2026-05']['narrative'],
    '同期核心口径(2026-05→2026-08)反向由 2.8229 回落至 2.4462,提示该段 headline 波动主要由非核心分项贡献'
    '【假设: 引擎无分项构成数据,不可归因到具体成分】。',
    '同窗核心口径亦同向上行(2026-02→2026-05 同比自 %s 升至 %s，涨幅小于 headline)。'
    '候选池另载核心口径转折 CORE_CPI@2026-08(2026-05→2026-08 同比自 %s 回落至 %s，其后 2026-09 回升至 %s)，'
    '该段晚于 headline 上行段，不构成「headline 上行段由非核心分项主导」的证据'
    '【假设: 引擎无分项构成数据，不可归因到具体成分】。'
    % ('%.4f' % cc['2026-02'], '%.4f' % cc['2026-05'], '%.4f' % cc['2026-05'], '%.4f' % cc['2026-08'], '%.4f' % cc['2026-09']))
TU['EA_HICP_YOY@2026-05']['follow_or_diverge'] = rep(
    TU['EA_HICP_YOY@2026-05']['follow_or_diverge'],
    '该转折后欧元区读数延续——2026-07 为 2.9、2026-10 为 4.0,未见回落。',
    '该转折后欧元区读数 2026-06 回落至 2.8，其后 2026-07 为 2.9、2026-10 为 4.0(越过 2026-05 的 3.2)。')
TU['EA_HICP_YOY@2026-05']['narrative'] = rep(
    TU['EA_HICP_YOY@2026-05']['narrative'], '三个月上行 1.3 个百分点,并延续为当前环境的主导变化(2026-10 达 4.0)。',
    '三个月上行 1.3 个百分点(其间 2026-06 回落至 2.8 后再度上行)，并延续为当前环境的主导变化(2026-10 达 4.0)。')
for t in rm['turnings']:
    for k in ('first_mover', 'follow_or_diverge', 'narrative'):
        t[k] = fix_snapshot(t[k])

# ── quality_gate_notes (disclosure block; no engine code reads it) ──────
fo = [lk['face_off_verdict'] for ch in TR for lk in ch['links'] if lk.get('competing_explanation')]
assert sorted(fo) == sorted(['支持主解释', '支持主解释', '尚不能区分']), fo


def _refs(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == 'evidence_refs' and isinstance(v, list):
                yield from v
            else:
                yield from _refs(v)
    elif isinstance(o, list):
        for v in o:
            yield from _refs(v)


ALL_REFS = list(_refs(J))
ev_total = len(ALL_REFS)
ev_c = sum(len(c.get('evidence_refs') or []) for c in C)
ev_m = sum(len(lk.get('evidence_refs') or []) for lk in M[0]['links'])
ev_s = len(list(_refs(J['l4'])))
assert ev_total == ev_c + ev_m + ev_s and not list(_refs(J['reader_map'])) and not list(_refs(J['agent_declaration']))
EVREFS = {r['ref'] for r in F['evidence_index']}
assert all(r in EVREFS for r in ALL_REFS), [r for r in ALL_REFS if r not in EVREFS]   # 全部解析到冻结证据索引
SC = J['l4']['scenarios']
assert [s['rows']['trigger']['deadline'] for s in SC] == ['2027-02-15'] * 2 and len(SC) == 2
assert [lk['evidence_level'] for lk in M[0]['links']] == ['E1', 'E2', 'E2']
tzs = {z: FR._local(z).strftime('%H:%M') for z in ('America/New_York', 'Europe/Berlin', 'Asia/Tokyo', 'Asia/Shanghai')}
assert FR.snap.get('snapshot_id') == 'research_snapshot_20261123'
J['quality_gate_notes'] = [
    '证据与口径: 研究截止日=快照版本日 %s(research_as_of %s；截止时点纽约 %s、法兰克福 %s、东京 %s、上海 %s)。'
    '截止时点美股与德法股指常规时段进行中，SPX、VIX、GOLD_F、DXY 与外汇的当日值均为截止时点的盘中快照(非收盘价)；'
    'NIKKEI225 止于 %s 收盘。同日收盘口径对照(%s→%s): 标普500指数 %s、VIX %s。'
    % (AS_OF, FR.snap['research_as_of'], tzs['America/New_York'], tzs['Europe/Berlin'], tzs['Asia/Tokyo'],
       tzs['Asia/Shanghai'], FR.last_date('NIKKEI225'), '2026-10-23', CLOSE,
       L.sgn2(AB['equity']['SPX']['ret']), L.sgn2(AB['vix_month_close'])),
    '对质面: 传导面 %d 环均给出主/竞争两侧对同一区分指标的不同预期，判断=尚不能区分 ×%d、支持主解释 ×%d'
    '(逐环两侧相容观测与裁定所依据的窗口见传导面正文；verdict_note 字段不进渲染，理由已写入 observed_fact)。'
    '竞争解释: L3 三条矛盾陈述各并列 %s 种解释。'
    % (len(fo), sum(1 for v in fo if v == '尚不能区分'), sum(1 for v in fo if v == '支持主解释'),
       '、'.join(str(len(c['competing_explanations'])) for c in C)),
    '证伪面: 两情景各给出可观测触发条件与失效阈值，期限均为 %s；日本央行决议 %s(生效 %s，目标水平 %s)与 %s 会议确认维持取自冻结发布日历 v%s 实录'
    '(维持条目无生效日，正文不为其挂生效日)；冻结日历无美欧决议/生效实录条目，美国端仅有会议纪要文档事实 %s(%s，%s 发布；纪要发布≠决议日)。'
    '机制链三环证据分级 %s，两处 E2 环的区分指标与缺环注记见机制链正文。'
    % (SC[0]['rows']['trigger']['deadline'], pol['policy_decision']['decision_date'],
       pol['policy_decision']['effective_on'], L.n(pol['policy_decision']['target_value']),
       pol['policy_maintenance']['decision_date'], cal.get('version'),
       PDF[0]['doc_id'], PDF[0]['title'], PDF[0]['published_on'], '/'.join(lk['evidence_level'] for lk in M[0]['links'])),
    '数据面: Gate A=%s——核心缺口 %s 项、非核心缺口 %s 项(%s)、非核心降级 %s 项(%s)；'
    '本档引用的非核心缺口指标 %s 项(%s)在序列库内有存量观测(最新观测 %s)，按降级口径引用。'
    '美国 CPI 2026-10 同比缺 2025-10 基期(当月同比不可得)。引擎契约对两处引用标注 STALE(数值一致、观测滞后超过注册表节奏，须披露): %s，'
    '两者均为该序列在截止日前的最新已发布观测。证据引用共 %d 条(矛盾陈述 %d、机制链 %d、情景 %d)，全部解析到本轮冻结快照 %s 的证据索引。'
    % (GA.get('status'), cn_count(len(GA.get('core_missing') or [])), cn_count(len(ncm)), '、'.join(ncm),
       cn_count(len(ncd)), '、'.join(ncd), cn_count(len(ncm_cited)), '、'.join(ncm_cited),
       FR.last_date('EA_REAL_GDP_YOY'), '；'.join(stale_txt), ev_total, ev_c, ev_m, ev_s, FR.snap.get('snapshot_id')),
    '政策口径披露: ①引擎『政策一年窗路径』面板按窗内首观测(2025-12 月均 0.557)→窗末观测计净变动，显示 +67bp；'
    '按『窗启时在值(2025-11 月均 0.478)→窗末观测(2026-10 月均 1.227)』口径为 +75bp，本档两种口径并列披露。'
    '②官方目标(JP_POLICY_TARGET)序列不在注册表，目标水平 1.25 仅见于冻结发布日历实录；在册序列 JP_POLICY_RATE 为无担保隔夜拆借月均口径，非目标宣布值。'
    '③本问计划指标面未纳入美欧政策利率序列，跨国政策跟进/背离在政策维度依本问证据不可判。',
    '引擎缺口披露(已登记为待裁定残留，本轮未改引擎): ①政策一年窗路径的净变动口径(见上条①)；'
    '②文本一致性别名表未收录 EA_HICP_YOY 等部分计划指标——本档矛盾陈述对这些指标以不带数字的写法表述，走位/转折/传导面的数字以独立席位复算为准；'
    '③传导链接的 verdict_note 字段不进渲染(裁定理由须写入 observed_fact)；④Gate A 非核心缺口清单列入有序列库存量观测的指标(正文按降级口径披露)。',
]

_qgn = J.pop('quality_gate_notes')                              # 披露块自身也含"盘中快照"字样,计数时剔除
assert json.dumps(J, ensure_ascii=False).count(SNAP_OLD) == 0
assert json.dumps(J, ensure_ascii=False).count('盘中快照') == n_snap
J['quality_gate_notes'] = _qgn
json.dump(J, open(j_out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('wrote', j_out, '| evidence refs', ev_total, ev_c, ev_m, ev_s)
print('face-offs', fo, '| snapshot wording replaced in', n_snap, 'fields')
print('BEI up', bei_up_d0, bei_up_v0, '->', bei_up_d1, bei_up_v1, '| 1m', C1B, '| 12m', C12, '| tips since 10-23 +%dbp' % tips_m_bp)
print('jp', jp_carry, JP['2025-12'], '->', jp_last, 'net dec/carry 67/75 | days eff/dec', d_eff, d_dec)
