# -*- coding: utf-8 -*-
# r30_points.py — B' 发布纪律 / H 诚实缺席与门面(引擎面对账)
# 用法: /usr/bin/python3 -I r30_points.py <RUN_DIR> <SNAPSHOT_JSON> <OUT_JSON>
import sys, os, json, re, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from r00_common import *

RUN, SNAP, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
sn = Snap(load(SNAP))
rep = load(os.path.join(RUN, 'report.json'))
aj = load(os.path.join(RUN, 'agent_judgment.json'))
cal = load(os.path.join(RUN, 'root_overlay', 'config', 'release_calendar.json'))
reg = load(os.path.join(RUN, 'root_overlay', 'config', 'metric_registry.json'))
rp = rep['research_plan']
PTS = []
EX = {}
CAT = ['']


def cat(c):
    CAT[0] = c


def P(pid, where, key, comp, rep_, note='', tol=None):
    disp = round(comp, 6) if isinstance(comp, float) else comp
    ok = same(comp, rep_, tol)
    PTS.append({'id': pid, 'cat': CAT[0], 'where': where, 'key': key, 'computed': disp,
                'reported': rep_, 'ok': bool(ok), 'note': note})
    print('%s|%s|%s|comp=%s|rep=%s|%s|%s' % ('OK' if ok else 'XX', pid, CAT[0], disp, rep_, where, note))
    return ok


cut = dt.date(2026, 11, 23)
# ---------------- B' 发布纪律 ----------------
cat("B' 发布纪律")
cells = rp['point_values']['cells']
RULE = {}
for c in cells:
    m = re.search(r'\+(\d+)天', c['anchors']['3个月前'].get('publication_rule', ''))
    RULE[c['metric_id']] = int(m.group(1)) if m else None
EX['rules_days'] = RULE
EX['pv_rules'] = {c['metric_id']: c['anchors']['3个月前'].get('publication_rule') for c in cells}


FREQ = {m.get('metric_id'): m.get('frequency') for m in reg['metrics']}


def pend(sid, obs):
    return period_end(obs, quarterly=(FREQ.get(sid) == 'quarterly'))


def pubdate(sid, obs):
    return pend(sid, obs) + dt.timedelta(days=RULE[sid])


n = 0
for c in cells:
    sid = c['metric_id']
    s = sn.series(sid)
    for lab in ('3个月前', '最新一期'):
        a = c['anchors'][lab]
        asof = D(a['as_of'])
        obs = D(a['observation_date'])
        pub = pubdate(sid, obs)
        n += 1
        P("B'%02d" % n, '%s「%s」观测 %s 的规则发布日(引擎面 publication_date)' % (sid, lab, obs.isoformat()),
          '期间末 %s + %d天 (规则=%s; 注册表频率=%s)' % (pend(sid, obs).isoformat(), RULE[sid], EX['pv_rules'][sid], FREQ.get(sid)), pub.isoformat(), a['publication_date'])
        idx = [i for i, (d_, v) in enumerate(s) if d_ == obs][0]
        nxt = s[idx + 1] if idx + 1 < len(s) else None
        n += 1
        if lab == '最新一期':
            P("B'%02d" % n, '%s「最新一期」= 截止日前最新已发布观测' % sid, '发布纪律: 发布日 ≤ 锚日 且 序列内其后无观测', ((pub <= asof) and (nxt is None)), True)
        else:
            npub = pubdate(sid, nxt[0]) if nxt else None
            P("B'%02d" % n, '%s「3个月前」= 锚日 2026-08-23 当日或之前最新已发布观测' % sid, '发布纪律: 锚观测发布日 ≤ 锚日 且 下一观测发布日 > 锚日',
              ((pub <= asof) and (npub is not None and npub > asof)), True, note='下一观测 %s 发布日 %s' % (nxt[0].isoformat() if nxt else None, npub.isoformat() if npub else None))
# 受审稿自述的发布日
P("B'37", 'C2 competing「观测月 2026-11、2026-12 …自 2026-12-15、2027-01-15 可见」(INDPRO 月末+15)', '2026-11-30 + 15天', pubdate('INDPRO', dt.date(2026, 11, 1)).isoformat(), '2026-12-15')
P("B'38", '同上(2026-12 观测月)', '2026-12-31 + 15天', pubdate('INDPRO', dt.date(2026, 12, 1)).isoformat(), '2027-01-15')
P("B'39", '传导环1「发布日 2026-10-13」= CPI 2026-09 观测规则发布日', '2026-09-30 + 13天', pubdate('CPI', dt.date(2026, 9, 1)).isoformat(), '2026-10-13')
P("B'40", '「2026-10-16」= EA_HICP_YOY 2026-09 观测规则发布日', '2026-09-30 + 16天', pubdate('EA_HICP_YOY', dt.date(2026, 9, 1)).isoformat(), '2026-10-16')
P("B'41", '「2026-10-30」= CORE_PCE 2026-09 观测规则发布日', '2026-09-30 + 30天', pubdate('CORE_PCE', dt.date(2026, 9, 1)).isoformat(), '2026-10-30')
P("B'42", '「2026-11-13」= CPI 2026-10 观测规则发布日', '2026-10-31 + 13天', pubdate('CPI', dt.date(2026, 10, 1)).isoformat(), '2026-11-13')
P("B'43", '「2026-11-16」= EA_HICP_YOY 2026-10 观测规则发布日', '2026-10-31 + 16天', pubdate('EA_HICP_YOY', dt.date(2026, 10, 1)).isoformat(), '2026-11-16')
P("B'44", '五日期均不晚于截止日 2026-11-23(截止日前已发布)', 'max(五发布日) ≤ 2026-11-23', (max(D(x) for x in ('2026-10-13', '2026-10-16', '2026-10-30', '2026-11-13', '2026-11-16')) <= cut), True)
# 冻结日历: 是否存在覆盖上述锚观测的改期条目(发布纪律以日历条目为准)
calobs = []


def walk_cal(o):
    if isinstance(o, dict):
        if any(k in o for k in ('first_publish_on_or_after', 'publish_on', 'published_on', 'release_date')) or 'metrics' in o or 'metric_ids' in o:
            calobs.append(o)
        for v in o.values():
            walk_cal(v)
    elif isinstance(o, list):
        for v in o:
            walk_cal(v)


walk_cal(cal)
EX['cal_entries_compact'] = [{k: v for k, v in e.items() if k in ('id', 'entry_id', 'code', 'kind', 'metrics', 'metric_ids', 'observation_window', 'obs_from', 'obs_to', 'first_publish_on_or_after', 'publish_on', 'decision_date', 'effective_on', 'target_value', 'source')} for e in cal.get('entries', [])]
hits = find_dicts_with_value(cal, 'RC-2025SHUTDOWN-REST-CONSERVATIVE')
cons = hits[0][1] if hits else {}
EX['cal_conservative'] = cons
cjson = json.dumps(cons, ensure_ascii=False)
P("B'45", 'US from_to「冻结日历保守界条目以 2026-01-22 为该月(2025-10)联邦统计的可见界」', 'release_calendar RC-2025SHUTDOWN-REST-CONSERVATIVE.first_publish_on_or_after', cons.get('first_publish_on_or_after'), '2026-01-22')
P("B'46", '同上(条目覆盖 CPI/CORE_CPI/CORE_PCE 且观测窗含 2025-10)', '条目 metrics 与 observation_window 文本', (('CPI' in cjson) and ('CORE_CPI' in cjson) and ('CORE_PCE' in cjson) and ('2025-10-31' in cjson or '2025-10' in cjson)), True)
P("B'47", 'quality_gate_notes[2]「冻结发布日历 v1.5.0」', 'release_calendar.version', 'v' + str(cal.get('version')).lstrip('v'), 'v1.5.0')

# ---------------- H 诚实缺席与门面 ----------------
cat('H 诚实缺席与门面')
ga = sn.sn.get('gate_a', {})
P('H01', 'quality_gate_notes[3]「Gate A=DEGRADED」', 'snapshot.gate_a.status', ga.get('status'), 'DEGRADED')
P('H02', '「核心缺口 零 项」', 'len(snapshot.gate_a.core_missing)', len(ga.get('core_missing', [])), 0)
P('H03', '「非核心缺口 七 项(BUND_10Y、BUND_2Y、CN_OMO_7D、CN_POLICY_OVERNIGHT、EA_REAL_GDP_YOY、JP_CPI_TOKYO_YOY、JP_REAL_GDP_YOY)」', 'snapshot.gate_a.noncore_missing', ','.join(sorted(ga.get('noncore_missing', []))), ','.join(sorted(['BUND_10Y', 'BUND_2Y', 'CN_OMO_7D', 'CN_POLICY_OVERNIGHT', 'EA_REAL_GDP_YOY', 'JP_CPI_TOKYO_YOY', 'JP_REAL_GDP_YOY'])))
P('H04', '「非核心降级 八 项(CN_SF_FLOW、ECB_DFR、ECB_MRO、JTSJOL、M2SL、SPX_EPS、SPX_PE_TTM、US_REAL_GDP)」', 'snapshot.gate_a.noncore_degraded', ','.join(sorted(ga.get('noncore_degraded', []))), ','.join(sorted(['CN_SF_FLOW', 'ECB_DFR', 'ECB_MRO', 'JTSJOL', 'M2SL', 'SPX_EPS', 'SPX_PE_TTM', 'US_REAL_GDP'])))
allg = set(ga.get('noncore_missing', [])) | set(ga.get('noncore_degraded', [])) | set(ga.get('core_missing', [])) | set(ga.get('core_fail', [])) | set(ga.get('noncore_fail', []))
P('H05', 'US from_to「该序列(CORE_PCE)不在 Gate A 缺口或降级名单」', 'snapshot.gate_a 各名单', ('CORE_PCE' not in allg), True)
P('H06', 'US from_to「Gate A 列于非核心降级名单」(US_REAL_GDP)', 'snapshot.gate_a.noncore_degraded', ('US_REAL_GDP' in ga.get('noncore_degraded', [])), True)
P('H07', 'quality_gate_notes[3]「本档引用的非核心缺口指标 一 项(EA_REAL_GDP_YOY)」', '计划指标 ∩ noncore_missing', ','.join(sorted(set(rp.get('metrics', [])) & set(ga.get('noncore_missing', [])))), 'EA_REAL_GDP_YOY')
P('H08', '「在序列库内有存量观测(最新观测 2026-07-01，距截止日 145 天)」', 'series_store.EA_REAL_GDP_YOY.dates[-1]', sn.last('EA_REAL_GDP_YOY')[0].isoformat(), '2026-07-01')
P('H09', 'US from_to「最新观测 2026-07-01 距截止日 145 天」', '2026-11-23 − 2026-07-01', (cut - dt.date(2026, 7, 1)).days, 145)
P('H10', 'US from_to「超过注册表最大日历滞后 120 天」', 'metric_registry.US_REAL_GDP.freshness.max_calendar_lag_days', {m.get('metric_id'): m for m in reg['metrics']}['US_REAL_GDP']['freshness']['max_calendar_lag_days'], 120)
P('H11', 'quality_gate_notes[3]「为注册表最大日历滞后 120 天的 1.2 倍」', '145 ÷ 120', 145 / 120.0, 1.2)
P('H12', 'US from_to「最新观测 2026-09-01 距截止日 83 天」', '2026-11-23 − 2026-09-01', (cut - dt.date(2026, 9, 1)).days, 83)
P('H13', '「超过注册表最大日历滞后 60 天」', 'metric_registry.CORE_PCE.freshness.max_calendar_lag_days', {m.get('metric_id'): m for m in reg['metrics']}['CORE_PCE']['freshness']['max_calendar_lag_days'], 60)
P('H14', 'quality_gate_notes[3]「60 天的 1.4 倍」', '83 ÷ 60', 83 / 60.0, 1.4)
P('H15', 'quality_gate_notes[3]「EA_REAL_GDP_YOY …与 US_REAL_GDP 同龄同倍数」', '两序列最新观测日相同且注册表滞后上限相同', (sn.last('EA_REAL_GDP_YOY')[0] == sn.last('US_REAL_GDP')[0] and {m.get('metric_id'): m for m in reg['metrics']}['EA_REAL_GDP_YOY']['freshness']['max_calendar_lag_days'] == 120), True)
mets = rp.get('metrics', [])
tw = {m: len(sn.win(m, dt.date(2026, 11, 1), dt.date(2026, 11, 30))) for m in mets}
P('H16', 'quality_gate_notes[3]「任务窗口(2026-11-01..2026-11-30)内 9 个计划指标的观测数均为 0」', 'series_store 各计划指标 2026-11 观测数', ','.join('%s=%d' % (k, v) for k, v in tw.items()), ','.join('%s=0' % k for k in mets))
# 证据引用
l3 = aj['l3']
refs = {'contradictions': [], 'mechanism': [], 'scenarios': []}
for c in l3['contradictions']:
    refs['contradictions'] += c.get('evidence_refs', [])
for mc in l3['mechanism_chains']:
    for lk in mc['links']:
        refs['mechanism'] += lk.get('evidence_refs', [])
for s in aj['l4']['scenarios']:
    refs['scenarios'] += s['rows'].get('asset_direction', {}).get('evidence_refs', [])
allrefs = refs['contradictions'] + refs['mechanism'] + refs['scenarios']
idx = set(e.get('ref') for e in rep['evidence_index'])
P('H17', 'quality_gate_notes[3]「证据引用共 20 条」', 'agent_judgment evidence_refs 总数', len(allrefs), 20)
P('H18', '「(矛盾陈述 11、机制链 4、情景唯一指标 5」', '三面引用数', '%d/%d/%d' % (len(refs['contradictions']), len(refs['mechanism']), len(refs['scenarios'])), '11/4/5')
P('H19', '「三面去重后为 14 条不同引用」', '去重引用数', len(set(allrefs)), 14)
P('H20', '「全部解析到本轮冻结快照 … 的证据索引」', 'evidence_index(63 行) 包含全部去重引用', set(allrefs) <= idx, True, note='缺=%s' % sorted(set(allrefs) - idx))
P('H21', 'agent_declaration「证据索引(63行)」', 'len(report.evidence_index)', len(rep['evidence_index']), 63)
P('H22', 'agent_declaration「点值格(9格)」', 'len(research_plan.point_values.cells)', len(cells), 9)
P('H23', 'agent_declaration「候选池7、top3」(候选池)', 'len(research_plan.turning_candidates.candidates)', len(rp['turning_candidates']['candidates']), 7)
P('H24', '同上(top3)', 'turning_candidates.top_n_expected', rp['turning_candidates'].get('top_n_expected'), 3)
cands = rp['turning_candidates']['candidates']
mx = max(cands, key=lambda c: abs(c['delta']))
P('H25', 'turnings[0]「候选池内最大单段变动」(CPI 1.7326)', '候选池 |delta| 最大者', '%s@%s' % (mx['metric_id'], mx['delta']), 'CPI@1.7326')
gm = [c for c in cands if c['dimension'] == 'growth']
mg = max(gm, key=lambda c: abs(c['delta']))
P('H26', 'turnings[1]「增长维候选池内最大的三个月变化」', 'growth 维 |delta| 最大者', mg['metric_id'], 'INDPRO')
for c in cands:
    k = '%s@%s' % (c['metric_id'], c['to_ym'])
    y0, y1 = yoy(sn, c['metric_id'], D(c['from_date'])), yoy(sn, c['metric_id'], D(c['to_date']))
    if c['metric_id'] == 'EA_HICP_YOY':
        y0, y1 = sn.val(c['metric_id'], D(c['from_date'])), sn.val(c['metric_id'], D(c['to_date']))
    if c['metric_id'] in ('JP_POLICY_RATE', 'UNEMPLOYMENT'):
        y0, y1 = sn.val(c['metric_id'], D(c['from_date'])), sn.val(c['metric_id'], D(c['to_date']))
    P('H27 %s' % k, '候选池端点值(引擎同比空间)直算', 'series_store.%s %s→%s' % (c['metric_id'], c['from_date'], c['to_date']), '%.4f→%.4f' % (y0, y1), '%.4f→%.4f' % (c['value_before'], c['value_after']))
# 契约
cv = rep['agent_judgment']['contract_verification']
vs = cv['verdicts']
stale = sorted('%s@%s' % (v['metric'], ('2026-09-01' if v['metric'] == 'CORE_PCE' else '2026-07-01')) for v in vs if v['status'] == 'STALE')
P('H28', 'quality_gate_notes[3]「引擎契约对两处引用标注 STALE」', 'report.agent_judgment.contract_verification.verdicts[status=STALE]', len(stale), 2)
P('H29', '「CORE_PCE(观测 2026-09-01…」「US_REAL_GDP(观测 2026-07-01…」', 'STALE 项指标', ','.join(sorted(v['metric'] for v in vs if v['status'] == 'STALE')), 'CORE_PCE,US_REAL_GDP')
P('H30', 'STALE 项数值与期望一致(「数值一致、观测滞后超过注册表节奏」)', 'STALE 项 value == expected', all(v['value'] == v['expected'] for v in vs if v['status'] == 'STALE'), True)
P('H31', '契约裁定总数与整体裁定', 'stats.checks / verdict', '%d/%s' % (cv['stats']['checks'], cv['verdict']), '9/VERIFIED')
dg = rp.get('dimension_gaps', [])
P('H32', 'JP from_to「JP_POLICY_TARGET 注册表不可得」', 'research_plan.dimension_gaps', ','.join('%s:%s' % (d['metric_id'], d['gap']) for d in dg), 'JP_POLICY_TARGET:registry_absent')
P('H33', 'turnings[2]「政策事件簇为空」', 'research_plan.policy_event_clusters.clusters', len(rp['policy_event_clusters']['clusters']), 0)
pdf = rp.get('policy_doc_facts', [])
P('H34', 'turnings[2]「FOMC 2026年10月会议纪要 2026-11-18 发布」', 'research_plan.policy_doc_facts', ','.join('%s:%s' % (d['doc_id'], d['published_on']) for d in pdf), 'FOMC-MINUTES-2026-10:2026-11-18')
P('H35', 'quality_gate_notes[3]「11 月完整结果须待数据覆盖后重跑」之前提: 截止日 2026-11-23 早于 11 月观测月终了', '日历: 2026-11-30 > 2026-11-23', (dt.date(2026, 11, 30) > cut), True)
# 引擎 us_rates_trio / asset_moves 对账(引擎面 vs 受审稿 echo)
urt = rp['us_rates_trio']
rd = aj['reader_map']['rates_decomposition']
P('H36', 'reader_map.rates_decomposition 窗口', 'research_plan.us_rates_trio.window', '%s→%s' % (urt['window']['from'], urt['window']['to']), '%s→%s' % (rd['window_from'], rd['window_to']))
P('H37', 'rates_decomposition nominal_bp', 'us_rates_trio.chg_bp.UST_10Y', urt['chg_bp']['UST_10Y'], rd['nominal_bp'])
P('H38', 'real_bp', 'us_rates_trio.chg_bp.TIPS_10Y', urt['chg_bp']['TIPS_10Y'], rd['real_bp'])
P('H39', 'bei_bp', 'us_rates_trio.chg_bp.BEI_10Y', urt['chg_bp']['BEI_10Y'], rd['bei_bp'])
P('H40', '引擎 12 个月窗 +91/+102/−11 与受审稿一致', 'us_rates_trio.chg_bp_12m', ','.join(str(int(urt['chg_bp_12m'][k])) for k in ('UST_10Y', 'TIPS_10Y', 'BEI_10Y')), '91,102,-11')
am = {r_['metric_id']: r_ for r_ in rp['asset_moves']['rows']}
for e in aj['reader_map']['asset_returns_echo']:
    r_ = am.get(e['metric_id'])
    P('H41 %s' % e['metric_id'], 'asset_returns_echo 与引擎资产月窗一致(%s)' % e['metric_id'], 'research_plan.asset_moves.rows[%s]' % e['metric_id'], '%s|%s→%s' % (r_['chg_pct'], r_['window']['from'], r_['window']['to']), '%s|%s→%s' % (e['chg_pct'], e['window']['from'], e['window']['to']))
P('H42', 'asset_moves 引擎面端点值与 series_store 一致(8 行)', 'asset_moves.rows from/to_value', all(abs(r_['from_value'] - sn.val(r_['metric_id'], D(r_['window']['from']))) < 1e-6 and abs(r_['to_value'] - sn.val(r_['metric_id'], D(r_['window']['to']))) < 1e-6 for r_ in am.values()), True)
P('H43', 'point_anchors 两锚日', 'research_plan.point_anchors', ','.join('%s:%s' % (a['label'], a['as_of']) for a in rp['point_anchors']), '3个月前:2026-08-23,最新一期:2026-11-23')
P('H44', '3 个月前锚 = 截止日 − 3 个月', '2026-11-23 − 3 月', add_months(cut, -3).isoformat(), '2026-08-23')

json.dump({'points': PTS, 'extra': EX}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('POINTS', len(PTS), 'MISMATCH', sum(1 for p in PTS if not p['ok']))
