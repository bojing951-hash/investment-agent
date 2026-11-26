#!/usr/bin/python3 -I
"""fold_B7.py <judgment_in.json> <tree> <run_dir> <judgment_out.json>

Builder revision of the B work-order judgment (US / euro-area growth and
inflation versus three months ago) after the independent review it received
at stamp 36499bb (round 1, REVISE: 1 MAJOR / 7 MINOR / 5 NIT; recorded
verbatim in the engine tree as VERDICT-20261123T235121Z-01).  The input is
the judgment exactly as it stood when that review was made (judgment6_B.json,
attached in this run directory).  Every number quoted in a replacement
sentence is recomputed here from the run's own frozen inputs (root_overlay
snapshot / release calendar / report.json) and asserted before the text is
written.  Read-only on the run directory.

Folded:
  MAJOR-1  quality_gate_notes[3]: evidence-reference self-count 19 -> 20
           (contradictions 6+3+2 = 11, chain 1+1+2 = 4, scenario metrics 5;
           distinct references also given)
  MINOR-2  release-day oil sentence: each release day named with its own
           value; interval minimum (2026-11-10, 91.49) noted
  MINOR-3  USDJPY three-month change: window written; reading from the
           engine's "3 months ago" anchor (2026-08-23 -> 2026-08-21) added
  MINOR-4  EURUSD three-month change: window written
  MINOR-5  US walk paragraph: the two contract-STALE series disclosed in the
           rendered text (as the EA paragraph already does)
  MINOR-6  risk-off combination: not synchronous across regions (DAX +0.11%)
  MINOR-7  "no discriminating indicator in this link" narrowed: CURVE_2S10S
           is in the evidence index and bears on one competing branch
  MINOR-8  second competing explanation of C3: failure conditions with
           thresholds; band marked as common to both explanations
  NIT-1    band bounds written exactly (1.197 / 1.257)
  NIT-2    rounded-bp convention noted (chain link and C3 statement)
  NIT-5    C2 competing explanations: observation horizon and thresholds
Not adopted:
  NIT-3    Arabic numerals beside the Chinese numerals in the C3 statement:
           the figures concern JP_POLICY_TARGET / net change, which the text
           consistency alias table does not cover; Arabic figures of an
           un-aliased metric in an L3 statement are bound to that metric's
           latest evidence value, so the Chinese-numeral writing is kept
           (disclosed in quality_gate_notes[5]).
  NIT-4    face_off_verdict wording: contract vocabulary field; the
           elimination-style reasoning and the unfulfilled half of the
           competing explanation are already written into observed_fact and
           verdict_note of that link.
"""
import copy
import datetime as dt
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
OLD = json.load(open(j_in, encoding='utf-8'))
J = copy.deepcopy(OLD)
assert J['agent_declaration']['produced_by'].count(RID) == 1, RID
LOG = []


def rep(s, old, new, n=1):
    assert s.count(old) == n, ('anchor count', s.count(old), n, old[:48])
    return s.replace(old, new)


def sub(obj, key, old, new, where):
    obj[key] = rep(obj[key], old, new)
    LOG.append('[%s] %s\n    - %s\n    + %s' % (where, key, old, new))


def subl(lst, i, old, new, where):
    """sub() for one element of a list (e.g. competing_explanations[i])."""
    lst[i] = rep(lst[i], old, new)
    LOG.append('[%s] [%d]\n    - %s\n    + %s' % (where, i, old, new))


RM = J['reader_map']
CS = J['l3']['contradictions']
CH = J['l3']['mechanism_chains']
TR = RM['transmission']
T0 = TR[0]['links']
SC = J['l4']['scenarios']
QG = J['quality_gate_notes']
rp = FR.rep['research_plan']
cells = {c['metric_id']: c for c in rp['point_values']['cells']}
EI = {x.get('ref') for x in FR.rep.get('evidence_index') or []}

# ---- structure of the audited version --------------------------------------
assert len(TR) == 1 and len(T0) == 3 and len(CH) == 1 and len(CH[0]['links']) == 3
assert [c['id'] for c in CS] == ['C1-INFL-SYNC', 'C2-GROWTH-STABLE', 'C3-JP-POLICY']
assert CH[0]['id'] == 'M1-JP-RATE-PATH'
assert [s['id'] for s in SC] == ['S1-INFL-STICKY', 'S2-INFL-FADE'] and len(QG) == 6
assert FR.as_of == '2026-11-23' and FR.snap.get('snapshot_id') == 'research_snapshot_20261123' and len(EI) == 63
US = [r for r in RM['regions'] if r['region'] == 'US']
assert len(US) == 1
US = US[0]

# ---- MAJOR-1: reference self-count -----------------------------------------
cs_refs = [r for c in CS for r in c['evidence_refs']]
ch_refs = [r for l in CH[0]['links'] for r in (l.get('evidence_refs') or [])]
sc_refs = [r for s in SC for r in s['rows']['asset_direction']['evidence_refs']]
sc_metrics = {m for s in SC for m in s['rows']['sensitive_variables']} | {r.split('@')[0] for r in sc_refs}
all_refs = set(cs_refs) | set(ch_refs) | set(sc_refs)
assert (len(cs_refs), len(ch_refs), len(sc_metrics), len(all_refs)) == (11, 4, 5, 14)
assert [len(c['evidence_refs']) for c in CS] == [6, 3, 2] and [len(l.get('evidence_refs') or []) for l in CH[0]['links']] == [1, 1, 2]
assert all_refs <= EI
sub(QG, 3, '证据引用共 19 条(矛盾陈述 10、机制链 4、情景 5)，全部解析到本轮冻结快照 research_snapshot_20261123 的证据索引。',
    '证据引用共 20 条(矛盾陈述 11、机制链 4、情景唯一指标 5;三面去重后为 14 条不同引用)，全部解析到本轮冻结快照 research_snapshot_20261123 的证据索引。',
    'MAJOR-1')

# ---- MINOR-2: release-day oil sentence --------------------------------------
b = ss['BRENT_F']
pub_days = ['2026-10-13', '2026-10-16', '2026-10-30', '2026-11-13', '2026-11-16']
oil = {d: b['values'][b['dates'].index(d)] for d in pub_days}
assert [round(oil[d], 2) for d in pub_days] == [105.69, 109.86, 117.64, 95.84, 92.44]
assert min(oil.values()) >= 91.62 and round(min(oil.values()), 2) == 92.44 and round(max(oil.values()), 2) == 117.64
seg = [(d, v) for d, v in zip(b['dates'], b['values']) if '2026-10-13' <= d <= '2026-11-16']
assert len(seg) == 25 and min(seg, key=lambda x: x[1])[0] == '2026-11-10' and round(min(v for _d, v in seg), 2) == 91.49
assert round(FR.val('BRENT_F', '2026-08-19'), 2) == 91.62 and round(oil[pub_days[-1]], 2) == 92.44
pub_known = {rmp._visible_publish(m, 'monthly', ym + '-01')[0] for m, ym in (
    ('CPI', '2026-09'), ('CORE_CPI', '2026-09'), ('EA_HICP_YOY', '2026-09'), ('CORE_PCE', '2026-09'),
    ('CPI', '2026-10'), ('CORE_CPI', '2026-10'), ('EA_HICP_YOY', '2026-10'))}
assert sorted(pub_known) == pub_days, pub_known
sub(T0[0], 'observed_fact',
    '(这些读数的发布日 2026-10-13 至 2026-11-16 的油价在 92.44 至 117.64 之间,均不低于窗启值 91.62)',
    '(这些读数的各个发布日(2026-10-13、2026-10-16、2026-10-30、2026-11-13、2026-11-16)当日油价在 92.44 至 117.64 之间,均不低于窗启值 91.62;'
    '2026-10-13 至 2026-11-16 整段区间内的最低值为 2026-11-10 的 91.49,低于窗启值,但该日不是所列读数的发布日)', 'MINOR-2')

# ---- MINOR-3: USDJPY three-month window -------------------------------------
u = ss['USDJPY']
assert u['dates'][-1] == FR.as_of and u['values'][-1] == 159.347
assert FR.date('USDJPY', '2026-08-19') == '2026-08-19' and FR.val('USDJPY', '2026-08-19') == 159.550003
assert FR.date('USDJPY', '2026-08-23') == '2026-08-21' and FR.val('USDJPY', '2026-08-21') == 158.882996
assert cells['CPI']['anchors']['3个月前']['as_of'] == '2026-08-23'
assert round((159.347 / 159.550003 - 1) * 100, 2) == -0.13 and round((159.347 / 158.882996 - 1) * 100, 2) == 0.29
sub(CH[0]['links'][2], 'text', '(三个月 -0.13%)',
    '(三个月 2026-08-19→2026-11-23 为 -0.13%;按 3 个月前锚 2026-08-23 的最近观测 2026-08-21 起算为 +0.29%,两口径下日元均未走强)', 'MINOR-3')

# ---- MINOR-4: EURUSD three-month window -------------------------------------
e = ss['EURUSD']
assert e['dates'][-1] == FR.as_of and e['values'][-1] == 1.093972 and FR.val('EURUSD', '2026-08-19') == 1.157943
assert round((1.093972 / 1.157943 - 1) * 100, 2) == -5.52
subl(CS[0]['competing_explanations'], 0, '三个月 -5.52%,11-23 为盘中快照)', '三个月(2026-08-19→2026-11-23)-5.52%,11-23 为盘中快照)', 'MINOR-4')

# ---- MINOR-5: the two contract-STALE series written into the US paragraph ----
cv = FR.rep['agent_judgment']['contract_verification']
stale = {(v['metric'], v['token']) for v in cv['verdicts'] if v['status'] == 'STALE'}
assert stale == {('CORE_PCE', '130.902'), ('US_REAL_GDP', '24611.077')}, stale
ga = FR.snap['gate_a']
assert 'CORE_PCE' not in ga['noncore_degraded'] and 'CORE_PCE' not in ga['noncore_missing'] and 'US_REAL_GDP' in ga['noncore_degraded']
lag = {}
for m, want in (('CORE_PCE', (60, '2026-09-01', 83)), ('US_REAL_GDP', (120, '2026-07-01', 145))):
    mx = FR.registry_metric(m)['freshness']['max_calendar_lag_days']
    last = FR.last_date(m)
    days = (dt.date.fromisoformat(FR.as_of) - dt.date.fromisoformat(last)).days
    assert (mx, last, days) == want, (m, mx, last, days)
    lag[m] = (mx, last, days)
sub(US, 'from_to', '指数水平 129.969→130.902)。',
    '指数水平 129.969→130.902;最新观测 2026-09-01 距截止日 83 天,超过注册表最大日历滞后 60 天,为截止日前最新已发布观测,引擎契约标注 STALE——数值一致、观测滞后超过注册表节奏,'
    '按降级口径引用(该序列不在 Gate A 缺口或降级名单))。', 'MINOR-5')
sub(US, 'from_to', 'GDP 水平 24408.011→24611.077 billion_usd,最新修订口径),',
    'GDP 水平 24408.011→24611.077 billion_usd,最新修订口径;最新观测 2026-07-01 距截止日 145 天,超过注册表最大日历滞后 120 天,为截止日前最新已发布观测,引擎契约标注 STALE——数值一致、观测滞后超过注册表节奏,'
    'Gate A 列于非核心降级名单,按降级口径引用),', 'MINOR-5')

# ---- MINOR-6: risk-off combination not synchronous across regions -----------
dax = [r for r in rp['asset_moves']['rows'] if r['metric_id'] == 'DAX']
assert len(dax) == 1 and dax[0]['window'] == {'from': '2026-10-23', 'to': '2026-11-23'} and dax[0]['chg_pct'] == 0.11
assert ss['DAX']['dates'][-1] == FR.as_of and round((ss['DAX']['values'][-1] / dax[0]['from_value'] - 1) * 100, 2) == 0.11
assert '德法股指' in QG[0] and 'DAX@2026-11-23' in EI
sub(T0[2], 'observed_fact', '——股金同跌而美元与波动率齐升的风险收缩组合。',
    '——股金同跌而美元与波动率齐升的风险收缩组合(非全区域同步: 引擎资产月窗同窗 DAX +0.11%,持平未跌;DAX 的 11-23 值同为盘中快照)。', 'MINOR-6')

# ---- MINOR-7: narrowing "no discriminating indicator in this link" -----------
for m, a, z in (('CURVE_2S10S', 0.46, 0.28), ('UST_2Y', 4.19, 4.76), ('UST_10Y', 4.65, 5.04)):
    assert FR.date(m, '2026-08-19') == '2026-08-19' and FR.date(m, '2026-11-19') == '2026-11-19'
    assert FR.val(m, '2026-08-19') == a and FR.val(m, '2026-11-19') == z and ('%s@2026-11-%s' % (m, '20' if m == 'CURVE_2S10S' else '19')) in EI
assert round((4.76 - 4.19) * 100) == 57 and round((5.04 - 4.65) * 100) == 39 and FR.last_date('CURVE_2S10S') == '2026-11-20'
sub(T0[1], 'observed_fact', '(本环实无可区分指标,TIPS_10Y 仅为对照位)',
    '(TIPS_10Y 仅为对照位;证据索引内的曲线形状指标 CURVE_2S10S 同窗(2026-08-19→2026-11-19)自 0.46 降至 0.28,近端 UST_2Y +57bp 的幅度大于 UST_10Y +39bp——近端领涨、曲线趋平,'
    '对竞争解释中「期限溢价或财政供给主导」一支(其预期为长端利率上行更多、曲线趋陡)或有区分力,本环未以该指标裁定)', 'MINOR-7')

# ---- MINOR-8 / NIT-1: policy-rate explanations ------------------------------
jr = FR.monthly('JP_POLICY_RATE')
assert (jr['2026-08'], jr['2026-09'], jr['2026-10']) == (0.977, 1.043, 1.227)
wp = rmp._policy_window_path(ss['JP_POLICY_RATE']['dates'], ss['JP_POLICY_RATE']['values'], FR.as_of, metric_id='JP_POLICY_RATE', carry_start=True)
ev = wp['events']
steps = [x['to'] - x['from'] for x in ev]
assert len(ev) == 6 and round(min(steps) * 100, 1) == 6.6 and round(sum(steps) * 100, 1) == 75.1
flat = [round(abs(jr[y] - jr[x]), 4) for x, y in (('2026-02', '2026-03'), ('2026-03', '2026-04'), ('2026-04', '2026-05'), ('2026-07', '2026-08'))]
assert max(flat) <= 0.001
cal = FR.cal['entries'] if isinstance(FR.cal, dict) else FR.cal
tgt = [x for x in cal if x.get('metric_id') == 'JP_POLICY_TARGET' and x.get('decision_date') == '2026-09-18']
assert len(tgt) == 1 and tgt[0]['entry_id'] == 'RC-JP-BOJ-TARGET-2026-09' and tgt[0]['target_value'] == 1.25 and tgt[0]['effective_on'] == '2026-09-24'
assert round(1.25 - 1.227, 3) == 0.023 and round(1.227 - 0.03, 3) == 1.197 and round(1.227 + 0.03, 3) == 1.257
subl(CS[2]['competing_explanations'], 1, '之后暂无新条目,下月是否有新决议尚未验证。',
    '之后暂无新条目,下月是否有新决议尚未验证;本解释的失效条件【假设】: 其后无新决议条目而月均再现台阶(相邻月均变动达到 0.03 或以上;持平月份的相邻月均差均不超过 0.001,已见台阶均不小于 0.066),'
    '或决议生效次月月均偏离新目标水平超过 0.03(本次 2026-10 月均 1.227 较目标水平 1.25 低 0.023,在容差内)。带宽 1.20 至 1.26 对两解释同向,只作共同下限;两解释的区分观测=其后是否出现新的决议条目。',
    'MINOR-8')
subl(CS[2]['competing_explanations'], 0, '2026-11 月均落在 1.20 至 1.26 之间,即较 2026-10 月均上下不超过 0.03——',
    '2026-11 月均落在 1.197 至 1.257 之间(两位小数显示约 1.20 至 1.26),即较 2026-10 月均 1.227 上下不超过 0.03——', 'NIT-1')

# ---- NIT-2: rounded-bp convention -------------------------------------------
assert round((wp['window_end_value'] - wp['window_start_value']) * 100, 1) == 74.9 and sum(x['delta_bp'] for x in ev) == wp['net_bp'] == 75
assert round((jr['2026-10'] - jr['2025-12']) * 100) == 67 and jr['2025-11'] == 0.478
sub(CH[0]['links'][0], 'text', '即六个变动点之和；仅自窗内首观测 2025-12 月均起算为 +67bp)',
    '即六个变动点之和(取整 bp 口径: 六步直和 75.1bp、窗启至窗末端点差 74.9bp,均取整为 +75bp)；仅自窗内首观测 2025-12 月均起算为 +67bp)', 'NIT-2')
sub(CS[2], 'statement', '即窗内六个变动点之和,引擎『政策一年窗路径』面板同口径)',
    '即窗内六个变动点之和(取整基点口径),引擎『政策一年窗路径』面板同口径)', 'NIT-2')

# ---- NIT-5: C2 competing explanations, horizon and thresholds ---------------
mon = {ym: v for ym, _d, v in rmp._monthly_series_for_turning(ss['INDPRO']['dates'], ss['INDPRO']['values'], ss['INDPRO'].get('unit'))}
yoy = {k: (mon[k] / mon[str(int(k[:4]) - 1) + k[4:]] - 1) * 100 for k in mon if str(int(k[:4]) - 1) + k[4:] in mon}
assert round(yoy['2026-07'], 2) == 1.25 and round(yoy['2026-10'], 2) == 2.15
assert rmp._visible_publish('INDPRO', 'monthly', '2026-11-01')[0] == '2026-12-15' and rmp._visible_publish('INDPRO', 'monthly', '2026-12-01')[0] == '2027-01-15'
subl(CS[1]['competing_explanations'], 0, '则增长动能已重新加速(所引最新读数为 2026-10)，失业率低位与此相容。',
    '则增长动能已重新加速(所引最新读数为 2026-10)，失业率低位与此相容(本解释的可观察期限与阈值【假设】: 观测月 2026-11、2026-12 两期读数,按引擎推定发布规则分别自 2026-12-15、2027-01-15 可见;'
    '两期同比均不低于 2.15%(2026-10 水平)则本解释成立,两期均低于 1.25%(2026-07 水平)则本解释不成立;其余情形不裁定)。', 'NIT-5')
subl(CS[1]['competing_explanations'], 1, '更代表主趋势。',
    '更代表主趋势(本解释的可观察期限与阈值【假设】: 同上两期读数;两期同比均低于 1.25%(2026-07 水平)则本解释成立,两期均不低于 2.15%(2026-10 水平)则本解释不成立;其余情形不裁定)。', 'NIT-5')


# ---- invariants: only the listed fields differ from the audited version ------
def diff_paths(a, b, path=''):
    if isinstance(a, dict) and isinstance(b, dict):
        assert set(a) == set(b), path
        out = []
        for k in a:
            out += diff_paths(a[k], b[k], '%s.%s' % (path, k) if path else k)
        return out
    if isinstance(a, list) and isinstance(b, list):
        assert len(a) == len(b), path
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff_paths(x, y, '%s[%d]' % (path, i))
        return out
    return [] if a == b else [path]


changed = set(diff_paths(OLD, J))
expected = {
    'quality_gate_notes[3]',
    'reader_map.transmission[0].links[0].observed_fact', 'reader_map.transmission[0].links[1].observed_fact',
    'reader_map.transmission[0].links[2].observed_fact', 'reader_map.regions[0].from_to',
    'l3.mechanism_chains[0].links[0].text', 'l3.mechanism_chains[0].links[2].text',
    'l3.contradictions[0].competing_explanations[0]',
    'l3.contradictions[1].competing_explanations[0]', 'l3.contradictions[1].competing_explanations[1]',
    'l3.contradictions[2].competing_explanations[0]', 'l3.contradictions[2].competing_explanations[1]',
    'l3.contradictions[2].statement',
}
assert changed == expected, sorted(changed ^ expected)
assert J != OLD and J['agent_declaration'] == OLD['agent_declaration']

with open(j_out, 'w', encoding='utf-8') as fh:
    json.dump(J, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
print('\n'.join(LOG))
print('folded %d edits | in=%s out=%s run=%s git=%s' % (len([x for x in LOG if x.startswith('[')]), j_in, j_out, RID, (R.get('git_head') or '')[:12]))
