#!/usr/bin/python3 -I
"""席位产出装配(只读受审件,只写本席目录)。

由复算中间表 + 受审判断档原文装配 PROSE-round1.md 与 VERDICT-round1.json。
「原句」一律按路径从受审判断档/读者报告取原文并断言在场,避免转写失真;
文中引用的数字取自 s10_recompute.py / s18_policy_series.py 的中间表并断言,不凭记忆补数。

用法: s17_write_outputs.py <agent_judgment.json> <recompute_points.json> <recompute_probes.json>
                           <render_check.json> <report.json> <MAP_REPORT.md> <outdir>
                           <policy_series_probe.json> <release_calendar.json> <FULL_REPORT.md>"""
import json
import os
import sys

(ajp, ptsp, prbp, rcpp, repp, mapp, OUT, psp, calp, fullp) = sys.argv[1:11]
aj = json.load(open(ajp, encoding='utf-8'))
PTS = json.load(open(ptsp, encoding='utf-8'))
PR = json.load(open(prbp, encoding='utf-8'))
RC = json.load(open(rcpp, encoding='utf-8'))
rep = json.load(open(repp, encoding='utf-8'))
MAP = open(mapp, encoding='utf-8').read()
FULL = open(fullp, encoding='utf-8').read()
PS = json.load(open(psp, encoding='utf-8'))
CAL = json.load(open(calp, encoding='utf-8'))
AJT = json.dumps(aj, ensure_ascii=False)

CAT_ORDER = ['①截止日', '②锚格', '③同比', '④政策面', '⑤三利率', '⑤资产月窗', '⑥转折候选', '⑦机制链',
             '⑧历史类比', '⑨情景相容', '⑩总判断', '⑪缺席披露', '⑫截止日当日日频', '⑬契约STALE', '⑭交付门', '证据引用']


def need(text, s, label):
    """断言原句在受审文本中逐字在场,返回原句。"""
    assert s in text, '原句不在场: ' + label
    return s


def cut(text, start, end):
    i = text.index(start)
    j = text.index(end, i) + len(end)
    return text[i:j]


# ── 受审判断档结构 ──────────────────────────────────────────────────────────
L = aj['reader_map']['transmission'][0]['links']
l1, l2, l3k = L[0], L[1], L[2]
C = {c['id']: c for c in aj['l3']['contradictions']}
NOTE = aj['quality_gate_notes']
HEAD = aj['reader_map']['headline_conclusion']
REG = {r['region']: r for r in aj['reader_map']['regions']}
TURN = {t['metric_id']: t for t in aj['reader_map']['turnings']}
SC = {s['id']: s for s in aj['l4']['scenarios']}
MC = aj['l3']['mechanism_chains'][0]
MCS = MC['links']
assert MC['id'] == 'M1-JP-RATE-PATH' and len(MCS) == 3
assert [s['evidence_level'] for s in MCS] == ['E1', 'E2', 'E2']
assert aj['reader_map']['transmission'][0]['chain_id'] == 'CH-INFL-RATES-RISKOFF'
assert aj['reader_map']['history_periods'] == []
assert len(NOTE) == 6 and len(L) == 3 and len(REG) == 3 and len(TURN) == 3 and len(SC) == 2

# ── 中间表数字(断言后在文中引用) ────────────────────────────────────────────
P = {p['id']: p for p in PTS}


def val(pid, nd=None):
    p = P[pid]
    assert p['ok'], pid
    v = p['computed']
    return round(v, nd) if (nd is not None and isinstance(v, float)) else v


assert val('P018') == '1.5.0'
assert val('P019') == 2 and val('P020') == 'JP_POLICY_TARGET' and val('P021') is False
assert val('P024') == 1.25 and val('P025') == 1.25 and val('P022') == '2026-09-18' and val('P023') == '2026-09-24' and val('P026') == '2026-10-30'
assert val('P030') == 60 and val('P031') == 66 and val('P034') == 24 and val('P032') == 60 and val('P033') == 66
assert val('P037') is False and val('P038') is False and val('P039') == 'monthly_avg_rate'
assert val('P017') == 0                      # policy_event_clusters.clusters 为空
assert [val('P%d' % i) for i in range(197, 206)] == [0.478, 0.557, 0.728, 0.727, 0.841, 0.978, 0.977, 1.043, 1.227]
assert val('P207', 0) == 67 and val('P208', 0) == 75 and val('P209', 0) == 67 and val('P210', 0) == 75 and val('P211') == 0.478
assert val('P212') == 159.347 and round(val('P214'), 2) == -9.98 and val('P215') == '2026-11-20'
assert val('P221', 0) == -8 and val('P222', 0) == 11 and val('P223', 0) == -19
assert val('P226', 0) == 39 and val('P227', 0) == 53 and val('P228', 0) == -14
assert val('P231', 0) == 91 and val('P232', 0) == 102 and val('P233', 0) == -11
assert val('P216') == 5.04 and val('P241', 0) == 22 and val('P240') == 2.66 and val('P217') == 2.88
assert val('P219') == 2.15 and val('P242') == 2.25 and val('P243') == 2.5
assert val('P244', 2) == -5.51 and val('P261', 2) == -9.36 and val('P263', 2) == -10.35
assert val('P130', 2) == 3.72 and val('P129', 2) == 3.3 and val('P137') is False and val('P146') is False
assert val('P049', 2) == 2.19 and val('P054', 2) == 2.07 and val('P046') == 24408.011 and val('P051') == 24611.077
assert val('P106') == 1.19 and val('P110') == 1.28
assert val('P272') == 'DEGRADED' and val('P273') == 0 and val('P274') is True and val('P275') is True and val('P276') == ['EA_REAL_GDP_YOY']
assert val('P280') == ['CORE_PCE', 'US_REAL_GDP'] and val('P281') is True and val('P282') == 2
assert val('P284') == 83 and val('P285') == 60 and val('P288') == 145 and val('P289') == 120
assert val('P294') == 63 and val('P295') == 19 and val('P296') == 10 and val('P297') == 4 and val('P298') == 5
assert val('P299') == [] and val('P300') == [] and val('P301') == [] and val('P302') == 'E1/E2/E2' and val('P303') == '2/2/2'
assert val('P305') == '2027-02-15/2027-02-15' and val('P306') == 0 and val('P307') == 3
for pid in ('P308', 'P309', 'P310', 'P311', 'P312', 'P313'):
    assert val(pid) is False, pid
assert val('P314') == '2026-10-01' and val('P315') is True and round(val('P316'), 0) == 11
assert len(C['C1-INFL-SYNC']['evidence_refs']) == 5 and len(C['C2-GROWTH-STABLE']['evidence_refs']) == 3 and len(C['C3-JP-POLICY']['evidence_refs']) == 2
assert sum(len(c['evidence_refs']) for c in C.values()) == 10 and sum(len(s['evidence_refs']) for s in MCS) == 4

IND = PR['INDPRO_path']
assert IND['2026-07'] == 103.1675 and IND['2026-10'] == 103.3954 and IND['2026-09'] == 103.8458
assert IND['2025-07'] == 101.894 and IND['2025-10'] == 101.2195
LC = PR['INDPRO_level_chg_pct']
assert round(LC['2026-07→2026-10'], 2) == 0.22 and round(LC['2026-09→2026-10'], 2) == -0.43 and round(LC['基期 2025-07→2025-10'], 2) == -0.66
IY = PR['INDPRO_yoy']
assert round(IY['2026-07'], 2) == 1.25 and round(IY['2026-10'], 2) == 2.15
SE = PR['us_ea_same_month']
assert SE['2026-07']['EA_HICP_YOY'] == 2.9 and round(SE['2026-07']['US_CPI_yoy'], 2) == 3.30
assert SE['2026-08']['EA_HICP_YOY'] == 3.2 and round(SE['2026-08']['US_CPI_yoy'], 2) == 3.35
assert SE['2026-09']['EA_HICP_YOY'] == 3.8 and round(SE['2026-09']['US_CPI_yoy'], 2) == 3.72
assert SE['2026-10']['EA_HICP_YOY'] == 4.0 and SE['2026-10']['US_CPI_yoy'] is None
_EA = PR['EA_HICP_path']
_CY = PR['CPI_yoy_2026']
_CC = PR['CORE_CPI_yoy_2026']
_CP = PR['CORE_PCE_yoy']
assert round(_EA['2026-10'] - _EA['2026-07'], 2) == 1.1 and _EA['2026-06'] == 2.8 and _EA['2026-02'] == 1.9 and _EA['2026-05'] == 3.2
assert max(v for k, v in _EA.items() if k <= '2026-10') == 4.0
assert round(_CY['2026-09'] - _CY['2026-07'], 2) == 0.41 and round(_CY['2026-05'], 2) == 4.17
assert round(_CC['2026-09'] - _CC['2026-07'], 2) == 0.10 and round(_CC['2026-07'], 2) == 2.47 and round(_CC['2026-09'], 2) == 2.57
assert round(_CP['2026-09'] - _CP['2026-06'], 2) == 0.08 and round(_CP['2026-06'], 2) == 3.04 and round(_CP['2026-09'], 2) == 3.12
PY = PR['pseudo_yoy_adjacent_base_CPI_2026-10']
assert round(PY['基期取 2025-09'], 2) == 4.08 and round(PY['基期取 2025-11'], 2) == 3.82
R12 = PR['ranges_12m']['BEI_10Y']
assert R12['min'] == 2.15 and R12['min_date'] == '2026-11-20' and R12['max'] == 2.5 and R12['max_date'] == '2026-05-04'
assert R12['n'] == 251 and R12['median'] == 2.32
MA = PR['BEI_10Y_month_aligned']
assert round(MA['2026-02-02→2026-05-29']) == 3 and round(MA['2026-02-27→2026-05-29']) == 13 and round(MA['2026-01-30→2026-04-30']) == 10
assert MA['2026-02-27→2026-05-04(判断档所引)'] == 25 and round(MA['2026-02-27→2026-05-27(满三个月)']) == 14
UJ = PR['USDJPY_key']
assert round(UJ['2026-09-17'], 3) == 156.014 and round(UJ['2026-09-18'], 3) == 156.129 and round(UJ['2026-11-23'], 3) == 159.347
assert round(PR['USDJPY_chg_pct']['2026-09-18→2026-11-23'], 2) == 2.06
assert round(PR['SPX_same_close_as_TIPS_10-23→11-19'], 2) == -5.87
assert round(PR['US_REAL_GDP_qq']['2026Q3/Q2 水平环比%'], 2) == 0.83
JPM = PR['JP_POLICY_RATE_monthly']
assert JPM['2026-08'] == 0.977 and JPM['2026-09'] == 1.043 and JPM['2026-10'] == 1.227 and JPM['2026-07'] == 0.978 and JPM['2025-11'] == 0.478
JS = PR['JP_step_bp']
STEPS = [round(JS[k]) for k in ('2025-11→2025-12', '2025-12→2026-01', '2026-05→2026-06', '2026-06→2026-07', '2026-08→2026-09', '2026-09→2026-10')]
assert STEPS == [8, 17, 11, 14, 7, 18], STEPS
UN = PR['UNEMPLOYMENT_2026']
assert UN['2026-07'] == 4.1 and UN['2026-10'] == 4.1 and UN['2026-09'] == 4.2
SR = PR['stale_ratio_EA_REAL_GDP_YOY']
assert SR == {'obs': '2026-07-01', 'days': 145, 'max_lag': 120}
assert PR['EA_REAL_GDP_YOY_registry_lag']['max_calendar_lag_days'] == 120 and PR['US_REAL_GDP_registry_lag']['max_calendar_lag_days'] == 120
assert '2025-10-01' not in PR['CORE_CPI_dates_2025H2'] and '2025-10-01' not in PR['CPI_dates_2025H2']
DR = PR['data_requirements']
assert len(DR) == 9 and all(x['outcome'] == 'insufficient_coverage' and x['window'] == '2026-11-01..2026-11-30' for x in DR)
_nw = [it['spec']['window']['n_in_window'] for it in rep['run']['data_requirements']['items'] if it.get('tier') == 'planned']
assert len(_nw) == 9 and all(x == 0 for x in _nw)
assert PR['quality_counts'] == {'PASS': 72, 'DEGRADED': 9, 'FAIL': 0} and PR['quality_overall'] == 'DEGRADED'
_cs = PR['contract_stats']
assert _cs['checks'] == 9 and _cs['six_fail'] == 0 and _cs['map_fail'] == 0 and _cs['contradicted'] == 0 and len(PR['contract_tokens_verified']) == 9
_pdf = rep['research_plan'].get('policy_doc_facts')
assert len(_pdf) == 1 and _pdf[0]['doc_id'] == 'FOMC-MINUTES-2026-10' and _pdf[0]['published_on'] == '2026-11-18'
assert rep['run_ok'] is True and rep['semantic_review']['required'] is True and rep['semantic_review']['seat_invoked'] is False and rep['semantic_review']['verdict'] is None

# 攻击探针(s18)与冻结日历/快照头
assert PS['snapshot_header'] == {'research_as_of': '2026-11-23T22:53:47+08:00', 'target_date': '20261123', 'series_count': 92, 'timezone': 'Asia/Shanghai'}
assert CAL['version'] == '1.5.0' and len(CAL['entries']) == 18
_pol = [e for e in CAL['entries'] if str(e.get('kind', '')).startswith('policy')]
assert len(_pol) == 2 and all((e.get('metric') or e.get('metric_id')) == 'JP_POLICY_TARGET' for e in _pol)
assert not [e for e in CAL['entries'] if (e.get('metric') or e.get('metric_id')) == 'JP_POLICY_RATE']
assert not [e for e in _pol if e.get('effective_on') and e['effective_on'] > '2026-11-23']
_PX = {m: PS[m] for m in ('DFEDTARU', 'DFEDTARL', 'FED_FUNDS', 'ECB_DFR', 'ECB_MRO')}
assert _PX['DFEDTARU']['values'] == {'2025-11-19': 4.0, '2026-08-19': 3.75, '2026-09-15': 3.75, '2026-09-16': 3.75, '2026-09-17': 4.0, '2026-10-20': 4.0, '2026-11-19': 4.0, '2026-11-23': 4.0}
assert _PX['DFEDTARL']['values'] == {'2025-11-19': 3.75, '2026-08-19': 3.5, '2026-09-15': 3.5, '2026-09-16': 3.5, '2026-09-17': 3.75, '2026-10-20': 3.75, '2026-11-19': 3.75, '2026-11-23': 3.75}
assert _PX['DFEDTARU']['change_points_last8'][-2:] == [['2025-12-11', 3.75], ['2026-09-17', 4.0]]
assert _PX['DFEDTARL']['change_points_last8'][-2:] == [['2025-12-11', 3.5], ['2026-09-17', 3.75]]
assert _PX['ECB_DFR']['change_points_last8'][-2:] == [['2026-06-17', 2.25], ['2026-09-16', 2.5]]
assert _PX['ECB_MRO']['change_points_last8'][-2:] == [['2026-06-17', 2.4], ['2026-09-16', 2.65]]
assert _PX['DFEDTARU']['net_bp'] == {'12m 2025-11-19→2026-11-19': 0.0, '3m 2026-08-19→2026-11-19': 25.0, '1m 2026-10-20→2026-11-19': 0.0}
assert _PX['ECB_DFR']['last'] == '2026-09-16' and _PX['ECB_MRO']['last'] == '2026-09-16'
assert all(v == 1 for v in PS['MAP_L66_literals'].values())

assert len(RC) == 52
_in_map = sum(1 for r in RC if r['in_MAP'])
_in_full = sum(1 for r in RC if r['in_FULL'])
_neither = [r['field'] for r in RC if not r['in_MAP'] and not r['in_FULL']]
assert _in_map == 35 and _in_full == 17 and len(_neither) == 6
assert sorted(f.split('.')[-1] for f in _neither) == ['narrative', 'narrative', 'narrative', 'verdict_note', 'verdict_note', 'verdict_note'], _neither

IND_PTS = [p for p in PTS if not p['structural']]
N_PTS = len(IND_PTS)
N_BAD = sum(1 for p in IND_PTS if not p['ok'])
N_STRUCT = len(PTS) - N_PTS
CATS = {}
for p in IND_PTS:
    c = CATS.setdefault(p['cat'], [0, 0])
    c[0] += 1
    c[1] += (0 if p['ok'] else 1)
CATS = {k: CATS[k] for k in sorted(CATS, key=lambda x: CAT_ORDER.index(x) if x in CAT_ORDER else 99)}
assert N_PTS == 302 and N_BAD == 0 and N_STRUCT == 14
assert sum(1 for p in PTS if p['structural'] and not p['ok']) == 0

# ── 原句(逐字取自受审判断档/读者报告) ───────────────────────────────────────
o_verdict2 = need(l2['face_off_verdict'], '支持主解释', '第2环裁定')
o_comp2 = need(AJT, l2['competing_predicts'], '第2环竞争预期')
o_fact2_tail = l2['observed_fact'][l2['observed_fact'].index('三个月、近一月、12 个月三窗均为'):]
assert o_fact2_tail.endswith('裁定只针对预注册的区分预期。')
o_note_admit = need(l2['observed_fact'], '「通胀走高而盈亏平衡回落」的组合与竞争解释的文字描述亦相容，该描述不构成两侧的区分预期，裁定只针对预注册的区分预期。', '第2环自认相容')
o_ce2 = l2['competing_explanation']
assert '通胀走高而盈亏平衡回落即属此类组合' in o_ce2 and '增长前景、期限溢价或财政供给主导' in o_ce2
o_main2 = l2['causal_hypothesis']
assert '维持紧缩偏向' in o_main2 and o_main2.startswith('【假设】')
o_vn2 = l2['verdict_note']
assert '主导关系稳定' in o_vn2
o_note1 = cut(NOTE[1], '传导面 3 环均给出', '支持主解释 ×2')
assert '冻结日历无美欧决议/生效实录条目' in NOTE[2] and 'E1/E2/E2' in NOTE[2]
assert 'verdict_note 字段不进渲染' in NOTE[5]
assert '非核心缺口 七 项' in NOTE[3] and '非核心降级 八 项' in NOTE[3] and '证据引用共 19 条(矛盾陈述 10、机制链 4、情景 5)' in NOTE[3]
assert '对两处引用标注 STALE' in NOTE[3]
o_l1 = need(l1['observed_fact'], '区分指标 BEI_10Y 在各窗方向不一致', '第1环措辞')
assert '三个月窗 2026-02→2026-05' in l1['observed_fact'] and '2.25 升至 2026-05-04 的 2.50' in l1['observed_fact']
o_c1 = need(C['C1-INFL-SYNC']['statement'],
            '欧元区 EA_HICP_YOY 最新读数明显走高、为美欧两地最高水平(数值与观测月见走位对照)', 'C1 最高水平')
o_head_ind = need(HEAD, '工业回升', '头条 工业回升')
o_us_ind = need(REG['US']['from_to'], '工业动能回升', '走位 工业动能回升')
o_c3c1 = need(C['C3-JP-POLICY']['competing_explanations'][1], '2026-09 月均 0.977→1.043 仅 +7bp', 'C3 竞争(2)')
o_note3 = need(NOTE[3], '美国 CPI 2026-10 同比缺 2025-10 基期(当月同比不可得)', '披露注 缺基期')
o_turn_ea = need(TURN['EA_HICP_YOY']['narrative'], '其间 2026-06 回落至 2.8 后再度上行', '转折叙述 其间')
o_c2c1 = need(C['C2-GROWTH-STABLE']['competing_explanations'][1], '价格与基数效应或单月波动', 'C2 竞争(2)')
o_c2c0 = need(C['C2-GROWTH-STABLE']['competing_explanations'][0], '增长动能在 2026 年三季度后段重新加速', 'C2 竞争(1)')
assert not o_c2c0.startswith('【假设】')
_others = [x for cid, c in C.items() for i, x in enumerate(c['competing_explanations']) if not (cid == 'C2-GROWTH-STABLE' and i == 0)]
assert len(_others) == 5 and all(x.startswith('【假设】') for x in _others)
o_vn3 = need(l3k['verdict_note'], '本月窗口 TIPS_10Y +11bp 与 SPX -5.51% 同现', '第3环 verdict_note')
assert '+22bp' in l3k['observed_fact'] and 'TIPS_10Y 走低' in l3k['competing_predicts'] and 'TIPS_10Y 走低' in l3k['competing_explanation']
o_s1 = need(SC['S1-INFL-STICKY']['rows']['trigger']['condition'], '2026-12 或 2027-01 发布的', 'S1 触发')
o_s2 = need(SC['S2-INFL-FADE']['rows']['falsification']['threshold'], '2026-12 与 2027-01 两月', 'S2 证伪')
assert SC['S1-INFL-STICKY']['rows']['trigger']['deadline'] == '2027-02-15' == SC['S2-INFL-FADE']['rows']['trigger']['deadline']
assert SC['S1-INFL-STICKY']['rows']['asset_direction']['confidence_tier'] == '有相关证据'
assert SC['S2-INFL-FADE']['rows']['asset_direction']['confidence_tier'] == '纯逻辑推理'
o_us_core = need(REG['US']['from_to'], '→2.57%(2026-09;指数水平 336.789→339.9)', '走位 核心CPI括注')
_ae = {(a['anchor'], a['metric_id']): (a['value'], a['observation_month']) for r in aj['reader_map']['regions'] for a in r['anchor_echo']}
assert _ae[('3个月前', 'CORE_CPI')] == (336.789, '2026-07') and _ae[('最新一期', 'CORE_CPI')] == (339.9, '2026-10')
assert _ae[('3个月前', 'CPI')] == (332.813, '2026-07') and _ae[('最新一期', 'CPI')] == (337.476, '2026-10')
assert _ae[('3个月前', 'CORE_PCE')] == (129.969, '2026-06') and _ae[('最新一期', 'CORE_PCE')] == (130.902, '2026-09')
assert _ae[('3个月前', 'INDPRO')] == (103.1675, '2026-07') and _ae[('最新一期', 'INDPRO')] == (103.3954, '2026-10')
assert _ae[('3个月前', 'UNEMPLOYMENT')] == (4.1, '2026-07') and _ae[('最新一期', 'UNEMPLOYMENT')] == (4.1, '2026-10')
assert _ae[('3个月前', 'US_REAL_GDP')] == (24408.011, '2026-04') and _ae[('最新一期', 'US_REAL_GDP')] == (24611.077, '2026-07')
assert _ae[('3个月前', 'JP_POLICY_RATE')] == (0.978, '2026-07') and _ae[('最新一期', 'JP_POLICY_RATE')] == (1.227, '2026-10')
assert '不以相邻口径冒充宣布值' in REG['JP']['from_to']
o_jp_next = need(REG['JP']['from_to'], '预计次月初前后公布', '走位 JP 次月')
o_fact2_jp = need(l2['observed_fact'], 'JP_POLICY_RATE 月均 2026-09 1.043→2026-10 1.227,日本亦处政策利率抬升通道', '第2环 日本句')
o_map_rule = need(MAP, '判断口径: 预期分立(两解释对同一指标给出不同预期)且引擎面观测在场才可裁;观测缺席或预期未分立=**尚不能区分**(诚实缺省,不以单侧证据裁)。',
                  '读者报告 判断口径')
o_map_row = need(MAP, '| TIPS_10Y | 主解释(紧缩偏向)预期 TIPS_10Y 上行主导名义利率变动 | 竞争解释(期限溢价/供给主导)预期 TIPS_10Y 与 BEI_10Y 组合无稳定主导关系 |', '对质表 第2行')
need(MAP, '该月末完整结果须待数据覆盖后重跑', '读者报告 页眉重跑披露')
need(MAP, '2026-09-01: 0.977→1.043(+7bp)', '政策一年窗路径 变动点')
need(FULL, 'run 门(Audit-R4 条目5): blocked_class=None degraded_ok=False', '完整报告 run 门')
for s in ('0.478', '0.557', '0.728', '0.841', '0.978', '1.043', '1.227'):
    assert any(s in MCS[0]['text'] for s in (s,)) or any(s in st['text'] for st in MCS), '机制链未引 ' + s
assert all(s in MCS[0]['text'] for s in ('0.478', '0.557', '0.728', '0.841', '0.978', '1.043', '1.227'))
assert '2026-04 0.727→2026-07 0.978' in AJT and '此环为【假设】' in MCS[1]['text'] and 'missing_link_note' in MCS[2]
_o_cn = ['一点二五', '六十天', '六十六天', '正六十七个基点', '正七十五个基点', '零点四七八']
assert all(s in C['C3-JP-POLICY']['statement'] for s in _o_cn), 'C3 中文数字写法'

# ── 改句 ───────────────────────────────────────────────────────────────────
f_verdict2 = '尚不能区分'
f_comp2 = ('竞争解释(增长前景/期限溢价/财政供给主导)同样预期 TIPS_10Y 上行主导名义利率变动、可与盈亏平衡回落并存，'
           '两解释在区分指标 TIPS_10Y 上预期方向不分立')
f_fact2_tail = ('三个月、近一月、12 个月三窗均为「实际利率上行、盈亏平衡回落」(实际 +53/+11/+102bp、盈亏平衡 -14/-19/-11bp)，'
                '名义利率上行由实际利率分量主导；但增长前景/期限溢价/财政供给主导同样预期 TIPS_10Y 上行，'
                '两解释在区分指标 TIPS_10Y 上的预期方向不分立(单月窗名义 -8bp 由盈亏平衡 -19bp 主导，亦不构成任一侧的区分证据)——尚不能区分。')
f_vn2 = ('三个月窗实际 +53bp 主导名义 +39bp、12 个月窗实际 +102bp 主导名义 +91bp，名义上行确由实际利率分量主导；'
         '但期限溢价/财政供给/增长前景主导同样预期该组合，两解释在 TIPS_10Y 上预期方向不分立——尚不能区分；'
         '单月窗名义 -8bp(实际 +11bp、盈亏平衡 -19bp)不构成任一侧的区分证据。')
f_note1 = ('传导面 3 环均列出主/竞争两侧预期，其中贴现率渠道环(区分指标 TIPS_10Y 相对 SPX)两侧预期分立且有在场观测，判断=支持主解释 ×1；'
           '另 2 环(BEI_10Y、TIPS_10Y 对名义利率)判断=尚不能区分 ×2')

MAJOR = {
    'severity': 'MAJOR',
    'where': ('agent_judgment.json reader_map.transmission[CH-INFL-RATES-RISKOFF].links[1](区分指标 TIPS_10Y)的 face_off_verdict / '
              'competing_predicts / observed_fact 末段 / verdict_note;连带 quality_gate_notes[1];读者面 MAP_REPORT.md「主解释 vs 竞争解释(对质表)」TIPS_10Y 第 1 行'),
    'note': ('对质裁定「支持主解释」超出证据(规程 §4:竞争解释须在列且真正竞争、同证据可容纳、非稻草人,且两解释在区分指标上的预言方向须确实不同;'
             '§3⑩:对质表判断须与该行观测及报告自述口径一致)。'
             '①同环竞争解释原文「' + o_ce2 + '」——按名义=实际+盈亏平衡的恒等关系,「通胀走高而盈亏平衡回落」而名义利率上行时,'
             '上行只能来自实际分量,即该解释对区分指标 TIPS_10Y 的推论同样是实际上行主导;预注册的竞争预期「' + o_comp2 + '」不是该解释文字的推论,属稻草人。'
             '判断档自己在同环注中写明「' + o_note_admit + '」——即承认两解释预期未分立,却仍依自设的「预注册区分预期」作单侧裁定。'
             '②读者报告自述裁定口径(MAP_REPORT.md「判断口径」行):「' + o_map_rule + '」——本环预期未分立,按该口径只能是尚不能区分。'
             '③主解释前件(央行紧缩偏向)本环未举证,但证据面对其并非空白:冻结快照 series_store.DFEDTARU/DFEDTARL 于 2026-09-17 由 3.75/3.50 升至 4.00/3.75(+25bp),'
             'ECB_DFR/ECB_MRO 于 2026-09-16 由 2.25/2.40 升至 2.50/2.65(+25bp);读者报告政策表注亦载「Fed…2026-09 决议 09-16→生效 09-17」'
             '「ECB…2026-09 决议 09-10→生效 09-16」,另载「本问计划指标面未纳入美欧政策利率序列」;且 12 个月窗端点(2025-11-19→2026-11-19)'
             'DFEDTARU 4.00→4.00 净变动为 0(其间 2025-12-11 降至 3.75)而同窗 TIPS_10Y +102bp——该窗对主解释并无独特支持。'
             '前件成立与否都不改变①②:两解释在区分指标上预期未分立,单侧裁定不成立。'
             '④三窗数字本身直算无误(近一月 2026-10-20→2026-11-19 实际 +11bp/盈亏平衡 -19bp/名义 -8bp;三个月 2026-08-19→2026-11-19 +53/-14/+39bp;'
             '12 个月 2025-11-19→2026-11-19 +102/-11/+91bp;出处 series_store.TIPS_10Y/BEI_10Y/UST_10Y),问题只在裁定与竞争预期的写法;'
             'verdict_note 称「主导关系稳定」亦未计入单月窗名义变动由盈亏平衡主导(-19bp 对 +11bp)。'
             '⑤连带 quality_gate_notes[1]「3 环均给出…不同预期」与计数「尚不能区分 ×1、支持主解释 ×2」随之不实。'),
    'original': o_comp2 + '(face_off_verdict: ' + o_verdict2 + ')',
    'fix': f_comp2 + '(face_off_verdict: ' + f_verdict2 + ')',
}

MUST_FIX = [
    '【传导链第 2 环 face_off_verdict】原句: 「' + o_verdict2 + '」 → 改句: 「' + f_verdict2 + '」',
    '【传导链第 2 环 competing_predicts】原句: 「' + o_comp2 + '」 → 改句: 「' + f_comp2 + '」',
    '【传导链第 2 环 observed_fact 末段】原句: 「' + o_fact2_tail + '」 → 改句: 「' + f_fact2_tail + '」',
    '【传导链第 2 环 verdict_note(与裁定同步)】原句: 「' + o_vn2 + '」 → 改句: 「' + f_vn2 + '」',
    '【quality_gate_notes[1]】原句: 「' + o_note1 + '」 → 改句: 「' + f_note1 + '」',
]

MINORS = [
    {
        'severity': 'MINOR',
        'where': 'agent_judgment.json reader_map.transmission[0].links[0](区分指标 BEI_10Y) observed_fact 首段与 face_off_verdict',
        'note': ('「区分指标 BEI_10Y 在各窗方向不一致」与本问三窗不符:近一月(2026-10-20→2026-11-19)-19bp、三个月(2026-08-19→2026-11-19)-14bp、'
                 '12 个月(2025-11-19→2026-11-19)-11bp 方向一致向下(series_store.BEI_10Y),最新 2.15(2026-11-20)为 12 个月窗内最低'
                 '(截至最新观测的 365 天窗 2025-11-20..2026-11-20 内 251 个有效观测,区间 2.15–2.50,中位 2.32);「不一致」只在与本问窗口之外的 2026-02→2026-05 段(2026-02-27 2.25→2026-05-04 2.50,+25bp)并列时出现,'
                 '且该段两端取的是局部低点与 12 个月高点(按月对齐的替代端点:2026-02-02→2026-05-29 约 +3bp、2026-01-30→2026-04-30 约 +10bp、'
                 '2026-02-27→2026-05-29 约 +13bp、2026-02-27→2026-05-27 约 +14bp)。'
                 '按预注册两侧预期(主=走高或维持高位;竞争=走低或持平),本问三窗均合竞争解释;「尚不能区分」所依据的另一根支柱是 L3 竞争解释中「同比数月内自行回落」一半尚未兑现——'
                 '那是关于通胀读数而非区分指标的预期。裁定偏保守、未超出证据,但与第 2 环的裁定尺度不对称(两处不对称均有利于主解释)。不改变头条结论,列 MINOR。'),
        'original': o_l1,
        'fix': ('区分指标 BEI_10Y 在本问三窗方向一致向下(近一月 -19bp、三个月 -14bp、12 个月 -11bp，最新 2.15 为 12 个月窗最低)，'
                '均合竞争解释「走低或持平」;更早的 2026-02→2026-05 上行段(2.25→2.50)合主解释——尚不能区分'),
    },
    {
        'severity': 'MINOR',
        'where': 'agent_judgment.json l3.contradictions[C1-INFL-SYNC].statement',
        'note': ('「为美欧两地最高水平」是跨月比较:欧元区 EA_HICP_YOY 取 2026-10(4.0),美国 CPI 同比最近有效为 2026-09(3.7173,2026-10 缺基期)。'
                 '同月口径下 2026-09 为 3.8 对 3.72(成立,差 0.08 个百分点),但 2026-07 为 2.9 对 3.30、2026-08 为 3.2 对 3.35(美国更高)'
                 '(series_store.EA_HICP_YOY 与 CPI 同比直算)——该位次是三个月窗内才发生的交叉,建议注明口径。'),
        'original': o_c1,
        'fix': ('欧元区 EA_HICP_YOY 最新读数明显走高、水平高于美国(数值与观测月见走位对照;两地最新可比同月 2026-09: 欧元区 3.8、美国 3.72;'
                '2026-07 与 2026-08 美国更高,位次在窗内交叉)'),
    },
    {
        'severity': 'MINOR',
        'where': 'agent_judgment.json reader_map.headline_conclusion 与 regions[US].from_to(「工业回升」/「工业动能回升」);l3.contradictions[C2-GROWTH-STABLE]',
        'note': ('「工业回升」依赖同比(1.25→2.15)而水平端点仅 +0.22%(INDPRO 2026-07 103.1675→2026-10 103.3954),'
                 '其中 2026-09→2026-10 环比 -0.43%(103.8458→103.3954),且同比基期同期下行(2025-07 101.894→2025-10 101.2195,-0.66%),同比抬升含基数效应'
                 '(series_store.INDPRO);判断档仅在 C2 竞争解释(2)中以假设形式提及。结论「增长面大体平稳」不受影响。'),
        'original': o_head_ind,
        'fix': '工业生产同比回升(水平较 3 个月前 +0.22%，2026-10 环比回落 0.43%，同比抬升含基数效应)',
    },
    {
        'severity': 'MINOR',
        'where': 'agent_judgment.json quality_gate_notes(数据面披露块)',
        'note': ('report.json run.data_requirements.items 显示 9 个计划指标对任务窗口 2026-11-01..2026-11-30 的 spec.window.n_in_window 均为 0、'
                 'outcome 均为 insufficient_coverage(截止日 2026-11-23 尚无 11 月观测);读者报告页眉已披露「该月末完整结果须待数据覆盖后重跑」,'
                 '但判断档 6 条披露注均未提及。建议补一句。'),
        'original': '',
        'fix': '补充: 「任务窗口 2026年11月 的 9 个计划指标在截止日窗内观测数为 0(均为覆盖不足)，本档以截止日前最新已发布观测与 3 个月前锚作答，11 月完整结果须待数据覆盖后重跑」',
    },
    {
        'severity': 'MINOR',
        'where': 'agent_judgment.json l3.contradictions[C3-JP-POLICY].competing_explanations[1]',
        'note': ('「2026-09 月均 0.977→1.043 仅 +7bp」中 0.977 是 2026-08 月均(series_store.JP_POLICY_RATE[2026-08-01]=0.977;[2026-09-01]=1.043),'
                 '写法沿用了引擎政策路径面板的变动点记法(MAP_REPORT.md 政策一年窗路径行「2026-09-01: 0.977→1.043(+7bp)」)。数值与 +7bp 无误,'
                 '月份标注易误读为 9 月月均自 0.977 变至 1.043。'),
        'original': o_c3c1,
        'fix': '2026-08 月均 0.977→2026-09 月均 1.043 仅 +7bp',
    },
    {
        'severity': 'MINOR',
        'where': 'agent_judgment.json quality_gate_notes(数据面/契约 STALE 披露);reader_map.regions[EA].from_to',
        'note': ('披露不对称两项:①EA_REAL_GDP_YOY 最新观测 2026-07-01 距截止日 145 天,注册表 freshness.max_calendar_lag_days=120(约 1.2 倍),'
                 '与按 STALE 披露的 US_REAL_GDP(同为 2026-07-01 观测、145 天、上限 120 天)同龄同倍数,但判断档只在 Gate A 非核心缺口清单中提及该指标,未按同一过期口径披露;'
                 '②「2026-10 同比不可得(缺 2025-10 基期)」只对 CPI 披露,CORE_CPI 同样缺 2025-10 观测'
                 '(series_store.CORE_CPI dates: 2025-09-01 之后直接为 2025-11-01),走位文字只以「最近有效 2026-09」带过。'),
        'original': o_note3,
        'fix': '美国 CPI 与核心 CPI 2026-10 同比均缺 2025-10 基期(当月同比不可得)',
    },
]

NITS = [
    {
        'severity': 'NIT',
        'where': 'agent_judgment.json reader_map.turnings[EA_HICP_YOY].narrative(该字段不进读者报告渲染)',
        'note': '「其间 2026-06 回落至 2.8」:2026-06 在 2026-02→2026-05 上行段之后,应为「其后」(同条 follow_or_diverge 的写法正确;series_store.EA_HICP_YOY[2026-06-01]=2.8)。',
        'original': o_turn_ea,
        'fix': '其后 2026-06 回落至 2.8 后再度上行',
    },
    {
        'severity': 'NIT',
        'where': 'agent_judgment.json l3.contradictions[C2-GROWTH-STABLE].competing_explanations[1]',
        'note': 'INDPRO 为物量指数,「价格与基数效应」中的「价格」不适用。',
        'original': o_c2c1,
        'fix': '基数效应或单月波动',
    },
    {
        'severity': 'NIT',
        'where': 'agent_judgment.json l3.contradictions[C2-GROWTH-STABLE].competing_explanations[0]',
        'note': '该条无【假设】标记(其余 5 条并列解释均有);「2026 年三季度后段」而所引最新读数为 2026-10(四季度)。',
        'original': o_c2c0,
        'fix': '【假设】…增长动能重新加速(所引最新读数为 2026-10)',
    },
    {
        'severity': 'NIT',
        'where': 'agent_judgment.json reader_map.transmission[0].links[2].verdict_note(该字段不进渲染)',
        'note': ('verdict_note 写「本月窗口 TIPS_10Y +11bp 与 SPX -5.51% 同现」:+11bp 是 2026-10-20→2026-11-19 窗,SPX -5.51% 是 2026-10-23→2026-11-23 窗;'
                 'observed_fact 用的是同窗起点的 +22bp(2026-10-23→2026-11-19)。两数各自无误,窗口不同。'),
        'original': o_vn3,
        'fix': '本月窗口 TIPS_10Y +22bp(2026-10-23→2026-11-19)与 SPX -5.51%(2026-10-23→2026-11-23)同现',
    },
    {
        'severity': 'NIT',
        'where': '读者报告渲染(引擎面,供操作席参考,非判断档缺陷)',
        'note': ('reader_map.turnings[*].narrative 三个字段在 MAP_REPORT.md / FULL_REPORT.md / report.md 均未渲染'
                 '(逐字段字面核对 52 个判断文字字段:MAP 35 个、FULL 17 个、两份皆无 6 个=3 个 verdict_note+3 个 narrative);'
                 '判断档披露注⑤③只说明 verdict_note 不进渲染。narrative 中的限定语因此到不了读者。'),
        'original': '',
        'fix': '',
    },
    {
        'severity': 'NIT',
        'where': 'agent_judgment.json l4.scenarios(S1 触发条件与 S2 证伪阈值)',
        'note': 'S1 用发布月口径(「2026-12 或 2027-01 发布的」),S2 用裸月份(「2026-12 与 2027-01 两月」);建议统一为发布月或观测月并写明。',
        'original': o_s1 + ' / ' + o_s2,
        'fix': '',
    },
    {
        'severity': 'NIT',
        'where': 'agent_judgment.json reader_map.regions[US].from_to',
        'note': '「核心 CPI 同比 2.47%(2026-07)→2.57%(2026-09;指数水平 336.789→339.9)」括注的指数水平是 2026-07→2026-10(anchor_echo),与同比的 2026-09 不同月,建议标注月份。',
        'original': o_us_core,
        'fix': '→2.57%(2026-09;指数水平 2026-07 336.789→2026-10 339.9)',
    },
    {
        'severity': 'NIT',
        'where': 'agent_judgment.json reader_map.regions[JP].from_to',
        'note': '「预计次月初前后公布」在冻结日历无对应条目(18 条中无 JP_POLICY_RATE 发布节奏条目),属未经证据面支撑的预期;无害,建议删去或标【假设】。',
        'original': o_jp_next,
        'fix': '',
    },
    {
        'severity': 'NIT',
        'where': 'agent_judgment.json reader_map.transmission[0].links[1].observed_fact',
        'note': '美国利率环内插入「JP_POLICY_RATE 月均…日本亦处政策利率抬升通道」与本环区分指标无关。',
        'original': o_fact2_jp,
        'fix': '',
    },
    {
        'severity': 'NIT',
        'where': 'agent_judgment.json l3.contradictions[C3-JP-POLICY].statement',
        'note': ('关键数字用中文数字(一点二五/六十天/六十六天/正六十七个基点/正七十五个基点/零点四七八),'
                 '不在契约面 9 个阿拉伯数字 token 之列(contract_verification.stats checks=9),只能人工复算'
                 '(本席已逐个复算一致:P025/P032/P033/P209–P211);判断档披露注⑤②只自述了文本一致性别名表的缺口,未说明中文数字写法不被绑定。'),
        'original': '',
        'fix': '',
    },
]
ITEMS = [MAJOR] + MINORS + NITS
N_MAJOR = sum(1 for x in ITEMS if x['severity'] == 'MAJOR')
N_MINOR = sum(1 for x in ITEMS if x['severity'] == 'MINOR')
N_NIT = sum(1 for x in ITEMS if x['severity'] == 'NIT')
for x in ITEMS:
    if x['severity'] == 'MAJOR':
        assert x['original'] and x['fix']
    if x['original']:
        frag = x['original'].split(' / ')[0].replace('(face_off_verdict: ' + o_verdict2 + ')', '')
        assert frag in AJT or frag in MAP, '原句不在受审文本: ' + x['where']

ATTACKS = [
    ('反方攻击 1(C1-INFL-SYNC)', '美国 CPI 2026-10 同比是否以相邻月基期凑数冒充?',
     '否。判断档明写「因缺上年同月基期观测不可得」;series_store.CPI 无 2025-10-01 观测(P137);若以相邻基期硬算为 4.08(基期取 2025-09)或 3.82(基期取 2025-11),'
     '判断档中均无此二数;所引最近有效同比 3.72=series_store 直算 3.7173(2026-09,P130)。'),
    ('反方攻击 2(C1-INFL-SYNC)', '「欧元区为两地最高水平」是否与序列相左?',
     '部分成立。同月口径 2026-07(欧元区 2.9/美国 3.30)与 2026-08(3.2/3.35)美国更高,仅 2026-09(3.8/3.72)起欧元区居首;原句未注明跨月与窗内交叉→列 MINOR,非 MAJOR(最新读数位次属实)。'),
    ('反方攻击 3(C1-INFL-SYNC)', '「同步走高、欧元区幅度更大」是否只成立于一侧?',
     '否。欧元区 2.9→4.0(+1.1 个百分点,2026-07→2026-10),美国 CPI 同比 3.30→3.72(+0.41,2026-07→2026-09)、核心 CPI 2.47→2.57(+0.10)、核心 PCE 3.04→3.12(+0.08,2026-06→2026-09);成立。'),
    ('反方攻击 4(C2-GROWTH-STABLE)', '增长面是否实际走弱而被写成平稳?',
     '否。美国实际 GDP 同比 2.19→2.07、水平 2026Q3 较 Q2 +0.83%,失业率 4.1→4.1(其间 2026-09 为 4.2),欧元区 GDP 同比 1.19→1.28;「大体平稳」成立。'
     '但 INDPRO 2026-10 环比 -0.43%、同比抬升含基数效应(基期 2025-07→2025-10 -0.66%),「工业回升」披露不足→列 MINOR。'),
    ('反方攻击 5(C3-JP-POLICY)', '官方目标 1.25 是否为序列值冒充?距上次调整天数是否按错日起算?',
     '否。JP_POLICY_TARGET 不在注册表与 series_store(P037/P038),1.25 仅出自冻结日历 RC-JP-BOJ-TARGET-2026-09.target_value(P024);'
     '生效日 2026-09-24→截止日 60 天、决议日 2026-09-18→66 天、维持会 2026-10-30→24 天(P030/P031/P034),逐日直算一致;月均口径 1.227 另列并注明非宣布值(P039/P205)。'),
    ('反方攻击 6(C3-JP-POLICY)', '12 个月净变动 +67bp/+75bp 是否与月均序列不符?',
     '否。2025-12 0.557→2026-10 1.227=+67.0bp(P207);2025-11 0.478→1.227=+74.9bp(P208);六级台阶(引擎变动点记法 +8/+17/+11/+14/+7/+18bp)与月均序列逐月差(7.9/17.1/11.4/13.7/6.6/18.4bp)取整一致。'),
    ('反方攻击 7(机制链 M1-JP-RATE-PATH)', '加息后日元是否走强而与「USDJPY 仍处高位」相左?E2 环是否以事实位措辞出现?',
     '否。USDJPY 决议日 2026-09-18 156.129→2026-11-23 159.347(+2.06%),与判断档「USDJPY 仍处高位」一致;第 2、3 环归 E2 并明写【假设】与缺环注记(引擎无融资成本/套息序列);'
     '链结论「传导方向证据不单一」与 USDJPY 上行、NIKKEI225 -9.98%(P214)的组合相称。'),
    ('反方攻击 8(传导链第 1 环 BEI_10Y)', '「尚不能区分」是否掩盖了本问三窗一致合竞争解释?',
     '部分成立:三窗 -19/-14/-11bp(P223/P228/P233)同向且 2.15 为 12 个月窗最低;「各窗方向不一致」措辞不准确,更早上行段端点取极值点(+25bp,月对齐替代端点约 +3~+14bp)→列 MINOR(裁定方向保守,未超出证据)。'),
    ('反方攻击 9(传导链第 2 环 TIPS_10Y 对名义利率)', '竞争预期是否稻草人、主解释前件是否有证据?',
     '成立:竞争解释原文同样容纳「通胀走高而盈亏平衡回落」组合,预注册的「无稳定主导关系」非其推论;冻结日历无美欧决议条目(P019–P021)、政策事件簇为空(P017);'
     '快照内美欧政策利率序列显示 2026-09-17、2026-09-16 各 +25bp(前件有支持,但本环未引用)→裁定「支持主解释」超出证据,列 MAJOR。'),
    ('反方攻击 10(传导链第 3 环 TIPS_10Y 对 SPX)', '同现是否等于因果、窗口是否错配?',
     '竞争解释原文对「增长担忧」与「仓位/流动性冲击」两变体均预期 TIPS_10Y 走低,与观测 +22bp(2026-10-23→2026-11-19,P241)/+11bp(P222)/+53bp(P227)相反,预期分立且观测在场,裁定成立;'
     'SPX 取同日收盘口径(2026-10-23→2026-11-19)为 -5.87%,方向不变;流动性叠加的限定已在 observed_fact 写明。无 MAJOR。'),
    ('反方攻击 11(情景 S1/S2)', '触发条件在截止日是否已触发或前提已被证伪?',
     '否。EA_HICP_YOY 2026-10=4.0 未达 S1 触发 4.2(P308),CORE_PCE 同比 3.12 未达 3.2(P309),TIPS_10Y 2.88 未高于 3.0(P310);S1 证伪条件(连续两月低于 3.0)未满足(P311);'
     'S2 触发(连续两月回落且 ≤3.4、BEI_10Y<2.0)未满足(P312/P313);S2 证伪所需 2026-12/2027-01 两月尚未发布(P314);期限 2027-02-15 在截止日后=待决(P305)。'),
    ('反方攻击 12(总判断/读者报告)', '判断文字在读者报告中是否被改动,或与数值面冲突?',
     '52 个判断文字字段逐字核对:MAP_REPORT.md 35 个、FULL_REPORT.md 17 个在位,未发现改写;6 个未渲染(3 个 verdict_note=判断档已披露;3 个 turnings.narrative=未披露,属引擎渲染面)。'
     '对质表第 2 行「支持主解释」即 MAJOR 所在;头条结论的数值与方向均与复算一致。'),
    ('反方攻击 13(对本席 MAJOR 的反向检验·传导链第 2 环)', '美欧央行若在窗内加息,主解释是否即获支持、裁定应否成立?',
     '前件有支持: 快照内 DFEDTARU/DFEDTARL 2026-09-17 +25bp、ECB_DFR/ECB_MRO 2026-09-16 +25bp(三个月窗 DFEDTARU +25bp);但 12 个月窗 DFEDTARU 4.00→4.00 净变动 0 而同窗 TIPS_10Y +102bp,'
     '且前件成立并不使两侧在区分指标上的预期分立——MAJOR 结论不变;本席初稿「前件在证据面无记录」的表述经此检验更正为「本环未引用」。'),
]

SIX = [
    ('C1-INFL-SYNC', [
        '证据相关性: 相符。EA_HICP_YOY、CPI、CORE_CPI、CORE_PCE、BEI_10Y 均为问句「通胀环境」的在册序列;5 条证据引用全部解析到冻结快照(P296/P299–P301)。',
        '支持度: 「同步走高、欧元区幅度更大」与直算相符(欧元区 +1.1 个百分点;美国 CPI 同比 +0.41、核心 CPI +0.10、核心 PCE +0.08 个百分点);'
        '「为美欧两地最高水平」属跨月比较(MINOR);「headline 强于核心」相符(3.72 对 2.57)。',
        '竞争解释: 2 条,均为【假设】条件式(成本/进口持续传导 对 一次性基数/扰动),对「同比是否自行回落」给出不同预期,属真正竞争;第 2 条已纳入近一月 BEI_10Y -19bp 的反向事实。',
        '反对证据: 美国 2026-10 同比缺基期(已披露);BEI_10Y 三窗下行(已在竞争解释与传导链第 1 环披露)。',
        '结论是否超出证据: 否。',
        '证伪条件可观测性: 由情景 S1/S2 承担,指标在册、阈值可观测(见情景项)。',
    ]),
    ('C2-GROWTH-STABLE', [
        '证据相关性: 相符。US_REAL_GDP、UNEMPLOYMENT、INDPRO 为问句「增长环境」的在册序列;3 条证据引用全部解析(P296/P299–P301)。',
        '支持度: 「大体平稳、并非主导变化」相符(美国 GDP 同比 2.19%→2.07%、欧元区 1.19%→1.28%,变动在 0.1 个百分点量级,远小于通胀端欧元区 +1.1 个百分点)。',
        '竞争解释: 2 条(制造业周期回暖 对 基数效应/单月波动),方向相反,属真正竞争。',
        '反对证据: INDPRO 2026-10 环比 -0.43% 与同比基期下行未在正文披露(仅以竞争解释(2)的假设形式出现)→ MINOR。',
        '结论是否超出证据: 否。',
        '证伪条件可观测性: 描述性陈述,不适用。',
    ]),
    ('C3-JP-POLICY', [
        '证据相关性: 相符。JP_POLICY_RATE 月均在册;官方目标仅见冻结日历条目,判断档已分列且不以相邻口径冒充(走位文字明写「不以相邻口径冒充宣布值」)。',
        '支持度: 目标 1.25、决议/生效/维持三日期、60/66/24 天、+67/+75bp 全部直算一致;「官方目标与市场口径相互印证」成立(1.25 对月均 1.227)。',
        '竞争解释: 2 条——(1) 月均台阶含均值效应与季节性;(2) 须以决议日历为准、下月是否有新决议未验证。是对「月均读数=连续上调」读法的有效约束,属真正竞争。',
        '反对证据: 决议后 USDJPY 上行(+2.06%)已在机制链第 3 环披露;无未披露的反向事实。',
        '结论是否超出证据: 否。',
        '证伪条件可观测性: 「下月是否有新决议尚未验证」可由冻结日历后续条目观测。',
    ]),
    ('机制链 M1-JP-RATE-PATH', [
        '证据级: E1/E2/E2 标注与内容相称(第 1 环全为月均序列直算值;第 2 环明写【假设】与缺环注记;第 3 环为资产面观测+条件推断,并附多因子缺环注记)。',
        '环内数字: 第 1 环 0.478/0.557/0.728/0.841/0.978/1.043/1.227、+67/+75bp,第 3 环 USDJPY 159.35、NIKKEI225 -9.98%,全部回贴一致(P197–P199、P201–P208、P212–P215);'
        '另核判断档他处所引 0.727(2026-04,转折候选面)与 0.977(2026-08,C3 竞争解释),一致(P200/P203)。',
        '竞争解释/反对证据: 「若加息传导单一成立,应见 USDJPY 走低」被 USDJPY 高位(决议日以来 +2.06%)否定,链结论如实收为「混合态、证据不单一」。',
        '结论是否超出证据: 否。',
        '证伪条件可观测性: 链内给出可观测对照(USDJPY 方向与股指),未单设情景。',
    ]),
    ('传导链 CH-INFL-RATES-RISKOFF(读者对质面)', [
        '第 1 环(BEI_10Y): 预期分立(走高/高位 对 走低/持平),观测在场;本问三窗同向合竞争解释,更早 2026-02→2026-05 段合主解释;裁定「尚不能区分」保守、首句措辞与行内观测部分不符(MINOR),未超出证据。',
        '第 2 环(TIPS_10Y 对名义利率): 预期不分立(竞争解释原文同样容纳「通胀走高而盈亏平衡回落」);主解释前件本环未举证(快照内美欧政策利率序列 2026-09 各 +25bp 可作支持,但 12 个月窗 DFEDTARU 净变动 0);'
        '裁定「支持主解释」超出证据 → MAJOR。',
        '第 3 环(TIPS_10Y 对 SPX): 预期分立(TIPS 上行 对 走低),观测在场(TIPS_10Y: 本月窗 +22bp(2026-10-23→2026-11-19)、近一月窗 +11bp(2026-10-20→2026-11-19)、三个月窗 +53bp(2026-08-19→2026-11-19);'
        'SPX 同起点窗: 2026-10-23→2026-11-23 为 -5.51%、2026-10-23→2026-11-19 为 -5.87%、2026-08-19→2026-11-20 为 -10.35%),流动性叠加已标注;裁定成立。',
    ]),
    ('情景 S1-INFL-STICKY / S2-INFL-FADE', [
        '两情景方向互补(延续 对 回落),非孤证;阈值指标 EA_HICP_YOY/CORE_PCE/BEI_10Y/TIPS_10Y 均在册;期限 2027-02-15 在截止日后(P305)。',
        '与截止日读数相容: 均未触发、亦未被证伪(见反方攻击 11);S1 所需核心 PCE 后续同比基期在场=可观测(P315)。',
        'S2 的置信档标「纯逻辑推理」偏保守(三窗 BEI_10Y 下行实为其相关证据),无害。',
    ]),
]

GATE14 = ('交付门: FULL_REPORT.md 载「run 门(Audit-R4 条目5): blocked_class=None degraded_ok=False」,report.json run_ok=true、'
          'semantic_review.required=true(理由 l3_qualitative_inference / l4_conditional_scenarios)且 seat_invoked=false、verdict=null——即裁决缺席状态,无草稿判定。'
          '判断档对相关缺口的披露与序列面/冻结日历一致: 缺数(9 个计划指标 11 月窗口覆盖不足→引擎 notes 列为「地图计划指标缺数(披露不阻断)」);'
          '缺官方记录(JP_POLICY_TARGET 注册表缺席 P037/P038,冻结日历无美欧决议条目 P019–P021);过期(契约 STALE 2 项=CORE_PCE 83 天/上限 60 天、US_REAL_GDP 145 天/上限 120 天,P280–P290);'
          '降级(Gate A=DEGRADED,核心缺口 0、非核心缺口 7、非核心降级 8,逐项一致 P272–P275)。'
          '未发现把缺席写成「无变化」、或把序列值写成官方宣布目标的情形(JP 月均 1.227 与官方目标 1.25 分列)。')
assert '地图计划指标缺数(披露不阻断' in json.dumps(rep['notes'], ensure_ascii=False)
assert rep['semantic_review']['reasons'] == ['l3_qualitative_inference', 'l4_conditional_scenarios']


def fmt(x, n=120):
    if x is None:
        return '—'
    if x is True:
        return 'True'
    if x is False:
        return 'False'
    if isinstance(x, float):
        s = '%.6g' % x
    elif isinstance(x, (list, dict)):
        s = json.dumps(x, ensure_ascii=False)
    else:
        s = str(x)
    s = s.replace('|', '\\|').replace('\n', ' ')
    return s if len(s) <= n else s[:n] + '…'


# ── 复算清单表 ─────────────────────────────────────────────────────────────
rows = []
for cat in CAT_ORDER + [c for c in sorted(set(p['cat'] for p in PTS)) if c not in CAT_ORDER]:
    grp = [p for p in PTS if p['cat'] == cat]
    if not grp:
        continue
    gind = [p for p in grp if not p['structural']]
    rows.append('\n**%s** — 独立复算 %d 点(偏离 %d)' % (cat, len(gind), sum(1 for p in gind if not p['ok'])))
    rows.append('')
    rows.append('| 编号 | 复算点 | 出处键 | 直算值 | 报告值/受审字面 | 比对方式 | 结果 |')
    rows.append('|---|---|---|---|---|---|---|')
    for p in grp:
        rep_col = fmt(p['reported'], 60)
        if p.get('literal'):
            rep_col += '；字面「' + fmt(p['literal'], 70) + '」'
        if p.get('cell_ok') is not None and p.get('engine_cell') is not None:
            rep_col += '；锚格回显/引擎格=' + fmt(p['engine_cell'], 30)
        if p.get('note'):
            rep_col += '；注: ' + fmt(p['note'], 80)
        res = '一致' if p['ok'] else '**偏离**'
        if p['structural']:
            res = '一致(结构性自检,不计入)' if p['ok'] else '**偏离(结构性自检)**'
        rows.append('| %s | %s | %s | %s | %s | %s | %s |' % (
            p['id'], fmt(p['desc'], 90), fmt(p['src'], 70), fmt(p['computed'], 50), rep_col, fmt(p['how'], 40), res))
    rows.append('')
TABLE = '\n'.join(rows)

_STRIP = ['①截止日', '②锚格', '③同比', '④政策面', '⑤三利率', '⑤资产月窗', '⑥转折候选', '⑦机制链', '⑨情景相容', '⑪缺席披露', '⑬契约STALE']
CAT_SUM = '、'.join('%s %d' % (k, v[0]) for k, v in CATS.items())
for s in _STRIP:
    CAT_SUM = CAT_SUM.replace(s + ' ', s[1:] + ' ', 1)

NOTES = (
    '独立零上下文席(B,Round-1)裁决 REVISE:MAJOR 1 条、MINOR %d 条、NIT %d 条。'
    '抽核:独立复算 %d 点(另有 %d 项结构性自检,直算值与比对值同源,不计入),从冻结快照 series_store(92 条序列)、冻结日历 v1.5.0(18 条)、'
    'report.json 引擎面直算后与判断档及 MAP/FULL 读者报告文字逐点比对,数值/日期/方向偏离 %d。分项: %s。'
    '命中要点:9 指标×2 锚的值/观测月/发布日/同比 18 格全部一致;同比基期均为去年同月/同季,CPI 与核心 CPI 2026-10 缺 2025-10 基期处如实标不可得;'
    '日本央行目标 1.25 仅出自冻结日历条目,距上次调整按生效日 60 天/按决议日 66 天/距维持 24 天,月均净变动 +67bp/+75bp 两口径与六级台阶一致;'
    '三利率恒等三窗残差 0;资产月窗与盘中快照标注、Gate A 清单、STALE(CORE_PCE 83 天/US_REAL_GDP 145 天)披露、19 条证据引用全部属实;'
    '判断文字 52 个字段逐字核对,46 个在读者报告在位,6 个未渲染(3 个 verdict_note=判断档已披露,3 个 turnings.narrative=未披露,属引擎渲染面)。'
    '唯一 MAJOR:传导链第 2 环(区分指标 TIPS_10Y)对质裁定「支持主解释」超出证据——同环竞争解释原文同样容纳「实际利率上行、盈亏平衡回落」的组合,'
    '预注册的「无稳定主导关系」不是该解释的推论(稻草人),两解释预期未分立,违反读者报告自述口径「预期未分立=尚不能区分」;'
    '主解释前件(央行紧缩偏向)本环未举证(快照内美欧政策利率序列显示 2026-09-17、2026-09-16 各 +25bp,但 12 个月窗 DFEDTARU 净变动 0);'
    '必修=改判「尚不能区分」并同步改写竞争预期、观测尾段、verdict_note 与 quality_gate_notes[1] 计数。'
    'MINOR:第 1 环「各窗方向不一致」措辞与极值端点选择(本问三窗 -19/-14/-11bp 同向)、C1「最高水平」为跨月比较(2026-07、2026-08 美国更高)、'
    '「工业回升」未披露 2026-10 环比 -0.43%% 与基数效应、9 个计划指标 11 月窗口覆盖不足未入判断档披露、「0.977」实为 2026-08 月均、'
    'EA 实际 GDP 同比同龄未按 STALE 口径披露且核心 CPI 缺基期未披露。'
    '头条结论(增长大体平稳、通胀同步走高且欧元区幅度更大、日本央行目标约 1.25、距上次调整 60/66 天、近一月风险收缩组合)的数值与方向均经复算成立,不受上述 MAJOR 影响。'
) % (N_MINOR, N_NIT, N_PTS, N_STRUCT, N_BAD, CAT_SUM)

assert 'MAJOR 1 条' in NOTES and N_MAJOR == 1 and '-0.43% 与' in NOTES and '%%' not in NOTES

VERDICT = {
    'seat': 'semantic-audit-seat',
    'reviewer': 'independent-zero-context-seat-r32-b-round1',
    'verdict': 'REVISE',
    'overall': 'REVISE',
    'notes': NOTES,
    'items': ITEMS,
    'must_fix': MUST_FIX,
    'counterexamples_sought': ['%s: %s→%s' % (a, b, c) for a, b, c in ATTACKS],
    'recompute_points': N_PTS,
    'recompute_mismatches': N_BAD,
    'mismatch_details': [],
    'audited_at': '2026-11-24',
}
js = json.dumps(VERDICT, ensure_ascii=False, indent=1)
back = json.loads(js)
assert list(back.keys()) == ['seat', 'reviewer', 'verdict', 'overall', 'notes', 'items', 'must_fix', 'counterexamples_sought',
                             'recompute_points', 'recompute_mismatches', 'mismatch_details', 'audited_at']
assert back['verdict'] in ('UPHELD', 'REVISE') and back['recompute_points'] == 302 and back['recompute_mismatches'] == 0
assert len(back['must_fix']) == 5 and len(back['counterexamples_sought']) >= 7
assert all(sorted(x.keys()) == ['fix', 'note', 'original', 'severity', 'where'] for x in back['items'])
with open(os.path.join(OUT, 'VERDICT-round1.json'), 'w', encoding='utf-8') as f:
    f.write(js + '\n')

# ── PROSE ──────────────────────────────────────────────────────────────────
H = []
H.append('# Audit-R32 正式使用验收 · B · Round-1 · 独立语义审查记录')
H.append('')
H.append('- 席位: semantic-audit-seat(零上下文;reviewer=independent-zero-context-seat-r32-b-round1);裁决日 2026-11-24。')
H.append('- **裁决: REVISE** — MAJOR %d 条 / MINOR %d 条 / NIT %d 条。' % (N_MAJOR, N_MINOR, N_NIT))
H.append('- 复算规模: 独立复算 **%d 点 / 偏离 %d**(另有 %d 项结构性自检全部一致,不计入;中间表共 %d 行)。' % (N_PTS, N_BAD, N_STRUCT, len(PTS)))
H.append('- 受审对象: 受审运行目录下 agent_judgment.json 全文(l3 / l4 / reader_map / quality_gate_notes / agent_declaration)'
         '与读者报告 MAP_REPORT.md / FULL_REPORT.md 中的判断文字。')
H.append('- 只读面: 冻结快照 research_snapshot_20261123.json(series_store 92 条序列;research_as_of 2026-11-23T22:53:47+08:00)、'
         '冻结日历 release_calendar.json v1.5.0(18 条)、metric_registry.json、report.json 引擎面、evidence_index.json(63 条);'
         '代码印章 19638e1487e1e5729b9645ce621c3435d0635d08。')
H.append('- 方法: 自写脚本 s10_recompute.py(/usr/bin/python3 -I,路径作参数传入)按注册表发布节奏与日历条目优先规则重建锚点、同比、'
         '发布日,从 series_store 直算三利率分解与资产月窗,再与判断档字面/锚格回显/引擎面比对;原句一律按路径取自受审判断档并断言在场。'
         '未联网、未运行任何写操作、未委派子代理;未读取规程 §2 所列任何目录。')
H.append('- 脚本与中间表(同目录,供操作席复核): s00–s09b/s11/s12(只读结构探查与引擎面抽取)、s10_recompute.py(主复算)、'
         's13_jstruct.py/s14_render_check.py/s15_calendar.py/s16_run_keys.py(结构与渲染核对)、s18_policy_series.py(政策利率序列攻击探针)、'
         's17_write_outputs.py(本件装配);work/recompute_points.json(逐点)、work/recompute_probes.json(探针)、work/policy_series_probe.json(攻击探针)、'
         'work/render_check.json、work/face_*.json 与 work/env_*.json(引擎面抽取)。')
H.append('')
H.append('## 一、复算清单(逐点)')
H.append('')
H.append('出处键图例: `series_store.*` / `snapshot.*` = research_snapshot_20261123.json(series_store 指该文件顶层 series_store);'
         '`calendar …` / `release_calendar.json …` = root_overlay/config/release_calendar.json;`metric_registry …` = root_overlay/config/metric_registry.json;'
         '`report.json …` / `research_plan.*` / `contract_verification.*` / `run.*` = report.json;`agent_judgment.json …` / `l3.*` / `l4.*` / `reader_map.*` = agent_judgment.json;'
         '「字面」=受审判断档或读者报告中的原字面;「锚格回显/引擎格」=reader_map.regions[*].anchor_echo 的值或引擎点值格。')
H.append('')
H.append('分项: %s。' % CAT_SUM)
H.append('')
H.append('⑧历史类比: 判断档 history_periods 为空(零段呈现,history_zero_case_note 已说明),不适用;⑫截止日当日日频观测的时点说明并入 ①/⑤ 核对;⑩ 见第三节,⑭ 见第二节末。')
H.append('')
H.append(TABLE)
H.append('## 二、工单专项核验(规程 §3 末项)与交付门缺口(⑭)')
H.append('')
H.append('| 对象 | 3 个月前锚 | 最新一期锚 | 变化方向 | 出处 |')
H.append('|---|---|---|---|---|')
H.append('| 美国·增长 | 实际 GDP 同比 2.19%@2026Q2(水平 24408.011);失业率 4.1@2026-07;工业生产同比 1.25%@2026-07(水平 103.1675) '
         '| 2.07%@2026Q3(24611.077);4.1@2026-10;2.15%@2026-10(103.3954) | GDP 同比微降;失业率持平;工业同比回升(水平端点 +0.22%) '
         '| series_store.US_REAL_GDP / UNEMPLOYMENT / INDPRO |')
H.append('| 美国·通胀 | CPI 同比 3.30%@2026-07(指数 332.813);核心 CPI 同比 2.47%@2026-07(336.789);核心 PCE 同比 3.04%@2026-06(129.969) '
         '| 3.72%@2026-09(指数 337.476@2026-10,同比缺基期);2.57%@2026-09(339.9@2026-10);3.12%@2026-09(130.902) | 同向上行 '
         '| series_store.CPI / CORE_CPI / CORE_PCE |')
H.append('| 欧元区·增长 | 实际 GDP 同比 1.19%@2026Q2 | 1.28%@2026Q3 | 微升 | series_store.EA_REAL_GDP_YOY |')
H.append('| 欧元区·通胀 | HICP 同比 2.9%@2026-07 | 4.0%@2026-10 | 上行 1.1 个百分点 | series_store.EA_HICP_YOY |')
H.append('| 日本·政策利率 | 月均 0.978@2026-07 | 月均 1.227@2026-10;官方目标 1.25(2026-09-18 决议、2026-09-24 生效、2026-10-30 确认维持) '
         '| 上行;距上次调整 60 天(按生效日)/66 天(按决议日)/距维持 24 天 '
         '| series_store.JP_POLICY_RATE;calendar RC-JP-BOJ-TARGET-2026-09 / RC-JP-BOJ-MAINT-2026-10 |')
H.append('')
H.append('日本政策利率水平的口径分列核对: 官方目标(JP_POLICY_TARGET,注册表与 series_store 均无,仅见冻结日历 target_value=1.25)与'
         '市场月均(JP_POLICY_RATE,value_type=monthly_avg_rate)在判断档与读者报告政策四分面表中分列,无相邻口径冒充;待生效决定=无(日历政策类条目仅 2 条,生效日均不晚于截止日)。')
H.append('')
H.append(GATE14)
H.append('')
H.append('补充(攻击探针,不计入复算点): 冻结快照内美欧政策利率序列 series_store.DFEDTARU/DFEDTARL 于 2026-09-17 由 3.75/3.50 升至 4.00/3.75,'
         'ECB_DFR/ECB_MRO 于 2026-09-16 由 2.25/2.40 升至 2.50/2.65(变更点直算);12 个月窗端点 2025-11-19→2026-11-19 DFEDTARU 4.00→4.00 净变动 0,'
         '三个月窗 2026-08-19→2026-11-19 +25bp。该两组序列不在本问 9 个计划指标内(读者报告转折候选面载「本问计划指标面未纳入美欧政策利率序列」)。')
H.append('')
H.append('## 三、六查逐项结论(规程 §4)')
H.append('')
for name, bullets in SIX:
    H.append('**%s**' % name)
    H.append('')
    for b in bullets:
        H.append('- ' + b)
    H.append('')
H.append('## 四、反方攻击记录')
H.append('')
for a, b, c in ATTACKS:
    H.append('- **%s** %s → %s' % (a, b, c))
H.append('')
H.append('## 五、问题清单')
H.append('')
H.append('### MAJOR(%d)' % N_MAJOR)
H.append('')
H.append('1. **%s**' % MAJOR['where'])
H.append('')
for seg in MAJOR['note'].split('。'):
    if seg.strip():
        H.append('   - ' + seg.strip() + '。')
H.append('')
H.append('   必修(原句 → 改句):')
H.append('')
for i, m in enumerate(MUST_FIX, 1):
    H.append('   %d. %s' % (i, m))
H.append('')
H.append('### MINOR(%d)' % N_MINOR)
H.append('')
for i, x in enumerate(MINORS, 1):
    H.append('%d. **%s** — %s' % (i, x['where'], x['note']))
    if x['original'] or x['fix']:
        H.append('   - 原句: 「%s」' % x['original'] if x['original'] else '   - (原句: 无,属应补未补的披露)')
        H.append('   - 改句: 「%s」' % x['fix'])
H.append('')
H.append('### NIT(%d)' % N_NIT)
H.append('')
for i, x in enumerate(NITS, 1):
    H.append('%d. **%s** — %s' % (i, x['where'], x['note']))
    if x['original'] or x['fix']:
        if x['original']:
            H.append('   - 原句: 「%s」' % x['original'])
        if x['fix']:
            H.append('   - 改句: 「%s」' % x['fix'])
H.append('')
H.append('## 六、裁决')
H.append('')
H.append('**REVISE**(MAJOR 1 条)。数值/日期/方向层面 %d 点独立复算零偏离,两锚、同比基期、政策面口径与天数、三利率恒等、'
         '资产月窗、Gate A 与 STALE 披露均属实;但传导链第 2 环的对质裁定「支持主解释」建立在稻草人式的竞争预期之上'
         '(竞争解释原文与观测相容、两解释在 TIPS_10Y 上预期未分立),违反读者报告自述的「预期未分立=尚不能区分」口径,属结论超出证据。'
         '按「只改必修句」原则给出 5 处原句→改句,改句中的数字(三窗实际 +53/+11/+102bp、盈亏平衡 -14/-19/-11bp、名义 -8bp)均取自只读证据面。'
         'MINOR/NIT 如实列出,不构成阻断。' % N_PTS)
H.append('')
PROSE = '\n'.join(H) + '\n'
with open(os.path.join(OUT, 'PROSE-round1.md'), 'w', encoding='utf-8') as f:
    f.write(PROSE)

print('recompute_points=%d mismatches=%d structural=%d | MAJOR=%d MINOR=%d NIT=%d' % (N_PTS, N_BAD, N_STRUCT, N_MAJOR, N_MINOR, N_NIT))
print('CAT_SUM:', CAT_SUM)
print('wrote', os.path.join(OUT, 'PROSE-round1.md'), len(PROSE), 'chars')
print('wrote', os.path.join(OUT, 'VERDICT-round1.json'), len(js), 'chars')
