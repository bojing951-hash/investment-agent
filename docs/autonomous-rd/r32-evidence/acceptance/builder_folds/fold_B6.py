#!/usr/bin/python3 -I
"""fold_B6.py <judgment_in.json> <tree> <run_dir> <judgment_out.json>

Builder revision of the B work-order judgment (US / euro-area growth and
inflation versus three months ago) after the independent review it received
at stamp 8f9055d (round 1, REVISE: 2 MAJOR / 4 MINOR / 11 NIT; recorded
verbatim in the engine tree as VERDICT-20261123T213320Z-01).  The input is
the judgment exactly as it stood when that review was made (judgment5_B.json),
already re-bound to this run's round id by restamp_judgment.py (the work
order was re-planned at the new stamp; its frozen inputs are the same).
Every number quoted in a replacement sentence is recomputed here from the
run's own frozen inputs (root_overlay snapshot / release calendar / seat
envelope / report.json) and asserted before the text is written.  Read-only
on the run directory.

Folded:
  MAJOR-1  supply-side reconciliation: the 3-month oil change (-3.74%) is a
           window-end plunge; in the observation months being explained oil
           and inflation moved together (monthly means, release-day levels)
  MAJOR-2  BEI_10Y face-off row: expectations split and observations are in
           evidence -> verdict 支持竞争解释 (two caveats kept as notes)
  MINOR-1   turnings: US CPI and EA HICP in the same window are one round of
           events; the second slot is now the INDPRO turning (growth), so
           the three turnings are three independent events
  MINOR-2   JGB link note: snapshot facts hold JGB point values
  MINOR-3   USDJPY 1-month change written into the mechanism link
  MINOR-4   scenario thresholds: buffer bands stated explicitly
  NIT-1/2/3/4/5/6/8/9/10/11  wording and evidence additions
Not adopted:
  NIT-7    EA_REAL_GDP_YOY@2026-07-01 is not in this work order's evidence
           index (63 refs; the only EA ref is EA_HICP_YOY@2026-10-01); the
           reading is cited in the walk face under the degraded disclosure.
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
    """sub() for one element of a list (e.g. competing_explanations[i])."""
    lst[i] = rep(lst[i], old, new)
    LOG.append('[%s] [%d]\n    - %s\n    + %s' % (where, i, old, new))


def yoy_series(mid):
    s = ss[mid]
    mon = {ym: v for ym, _d, v in rmp._monthly_series_for_turning(s['dates'], s['values'], s.get('unit'))}
    return {k: round((mon[k] / mon[str(int(k[:4]) - 1) + k[4:]] - 1) * 100, 4)
            for k in sorted(mon) if str(int(k[:4]) - 1) + k[4:] in mon}


def mmean(mid, ym):
    vs = [v for d, v in zip(ss[mid]['dates'], ss[mid]['values']) if d[:7] == ym]
    return sum(vs) / len(vs)


RM = J['reader_map']
CS = J['l3']['contradictions']
CH = J['l3']['mechanism_chains']
TR = RM['transmission']
T0 = TR[0]['links']
TN = RM['turnings']
SC = J['l4']['scenarios']
QG = J['quality_gate_notes']
assert len(TR) == 1 and len(T0) == 3 and len(CH) == 1 and len(CH[0]['links']) == 3
assert CS[0]['id'] == 'C1-INFL-SYNC' and CS[2]['id'] == 'C3-JP-POLICY' and CH[0]['id'] == 'M1-JP-RATE-PATH'
assert [t['metric_id'] for t in TN] == ['CPI', 'EA_HICP_YOY', 'JP_POLICY_RATE']
assert [s['id'] for s in SC] == ['S1-INFL-STICKY', 'S2-INFL-FADE'] and len(QG) == 6
assert not RM.get('turning_supplement')

# ── computed facts (frozen inputs of this run) ─────────────────────────
assert FR.as_of == '2026-11-23' and FR.snap['snapshot_id'] == 'research_snapshot_20261123'
rp = FR.rep['research_plan']
cells = {c['metric_id']: c for c in rp['point_values']['cells']}
EI = {x.get('ref') for x in FR.rep.get('evidence_index') or []}

# MAJOR-1: oil path inside the 3-month window and in the observation months
b = ss['BRENT_F']
w = [(d, v) for d, v in zip(b['dates'], b['values']) if '2026-08-19' <= d <= FR.as_of]
w0 = w[0][1]
assert w[0][0] == '2026-08-19' and round(w0, 2) == 91.62 and w[-1] == (FR.as_of, b['values'][-1]) and round(w[-1][1], 2) == 88.19
assert len(w) == 68 and sum(1 for _d, v in w if v >= w0) == 61
assert max(w, key=lambda x: x[1])[0] == '2026-10-30' and round(max(v for _d, v in w), 2) == 117.64
assert round(FR.val('BRENT_F', '2026-10-23'), 2) == 116.72 and round((FR.val('BRENT_F', '2026-10-23') / w0 - 1) * 100, 2) == 27.40
assert round(FR.ret('BRENT_F', '2026-08-19', FR.as_of), 2) == -3.74 and round(FR.ret('BRENT_F', '2026-10-23', FR.as_of), 2) == -24.44
assert round(FR.ret('BRENT_F', '2025-11-19', FR.as_of), 2) == 38.86
mm = {k: mmean('BRENT_F', k) for k in ('2025-10', '2026-07', '2026-09', '2026-10')}
assert [round(mm[k], 2) for k in ('2026-07', '2026-09', '2026-10', '2025-10')] == [84.51, 102.26, 108.34, 63.95]
assert round((mm['2026-09'] / mm['2026-07'] - 1) * 100, 1) == 21.0 and round((mm['2026-10'] / mm['2026-07'] - 1) * 100, 1) == 28.2
assert round((mm['2026-10'] / mm['2025-10'] - 1) * 100, 1) == 69.4
anc = {m: cells[m]['anchors']['最新一期'] for m in ('CPI', 'CORE_PCE', 'EA_HICP_YOY')}
assert anc['CPI']['publication_date'] == '2026-11-13' and anc['EA_HICP_YOY']['publication_date'] == '2026-11-16' \
    and anc['CORE_PCE']['publication_date'] == '2026-10-30'
assert '月末+13天' in anc['CPI']['publication_basis'] and '月末+16天' in anc['EA_HICP_YOY']['publication_basis']
# the 2026-09 readings of CPI / EA HICP under the same publication rule
d_cpi_sep = (dt.date(2026, 9, 30) + dt.timedelta(days=13)).isoformat()
d_hicp_sep = (dt.date(2026, 9, 30) + dt.timedelta(days=16)).isoformat()
assert (d_cpi_sep, d_hicp_sep) == ('2026-10-13', '2026-10-16')
pub_days = ['2026-10-13', '2026-10-16', '2026-10-30', '2026-11-13', '2026-11-16']
oil = {d: b['values'][b['dates'].index(d)] for d in pub_days}
assert all(d in b['dates'] for d in pub_days)
assert [round(oil[d], 2) for d in pub_days] == [105.69, 109.86, 117.64, 95.84, 92.44]
assert min(oil.values()) >= w0 and round(min(oil.values()), 2) == 92.44 and round(max(oil.values()), 2) == 117.64
eh = FR.monthly('EA_HICP_YOY')
assert eh['2026-08'] < eh['2026-09'] < eh['2026-10']                    # inflation rising in 2026-09 / 2026-10
cy = yoy_series('CPI')
assert cy['2026-08'] < cy['2026-09'] and round(cy['2026-09'], 2) == 3.72 and round(cy['2026-05'], 2) == 4.17
sub(T0[0], 'observed_fact',
    '近 12 个月 +38.86%)——三个月窗内油价微降而两地通胀走高,对「能源持续传导」前提为反向事实、对「能源基数消退」为同向事实【尚未验证】;该读数不在本环区分指标上,不改裁定。',
    '近 12 个月 +38.86%),但该端点差来自窗末急跌: 窗内先升至 2026-10-23 的 116.72(较窗启 +27.40%)、窗内高点 117.64(2026-10-30),'
    '窗内 68 个观测中 61 个不低于窗启值;按序列库日值计的月均 2026-07 84.51→2026-09 102.26(+21.0%)→2026-10 108.34(+28.2%),'
    '2026-10 月均较 2025-10 月均 63.95 高 69.4%——在本问所解释的 2026-09/2026-10 观测月,油价与两地通胀同向走高,不构成对「能源持续传导」的反向事实;'
    '油价回落发生在 11 月、晚于上述观测月(这些读数的发布日 2026-10-13 至 2026-11-16 的油价在 92.44 至 117.64 之间,均不低于窗启值 91.62),'
    '只对此后读数构成「能源基数消退」的同向前瞻事实【尚未验证】;该读数不在本环区分指标上,不改裁定。', 'MAJOR-1')
sub(CS[0], 'statement',
    '供给侧读数对账见传导面第一环(近三个月布伦特原油微降而两地通胀走高,对「能源持续传导」为反向事实【尚未验证】)。',
    '供给侧读数对账见传导面第一环(近三个月布伦特原油端点微降系窗末急跌所致;在通胀观测月口径下油价月均走高、与两地通胀同向,'
    '不构成对「能源持续传导」的反向事实,十一月回落仅为对此后读数的前瞻事实【尚未验证】)。', 'MAJOR-1')

# MAJOR-2: BEI_10Y face-off row
be = ss['BEI_10Y']
w12 = [(d, v) for d, v in zip(be['dates'], be['values']) if d >= '2025-11-19']
assert be['dates'][-1] == '2026-11-20' and be['values'][-1] == 2.15 and min(v for _d, v in w12) == 2.15 \
    and sum(1 for _d, v in w12 if v == 2.15) == 1 and max(v for _d, v in w12) == 2.50
for d0 in ('2025-11-19', '2026-08-19', '2026-10-20'):
    assert FR.val('BEI_10Y', d0) > 2.15                                  # all three windows point down
assert FR.val('BEI_10Y', '2026-02-27') == 2.25 and FR.val('BEI_10Y', '2026-05-04') == 2.50
assert max(v for k, v in eh.items() if k.startswith('2026')) == 4.0 and eh['2026-10'] == 4.0
QG[1] = rep(QG[1],
            '另 2 环(区分指标 BEI_10Y；TIPS_10Y 相对名义利率——两解释在该指标上预期方向不分立)判断=尚不能区分 ×2',
            '另 2 环中, BEI_10Y 环两侧预期分立(走高或维持高位 对 走低或持平)且有在场观测(本问三窗方向一致向下、最新水平为十二个月窗内最低)，判断=支持竞争解释 ×1;'
            'TIPS_10Y 相对名义利率环两解释在该指标上预期方向不分立，判断=尚不能区分 ×1')
LOG.append('[MAJOR-2] quality_gate_notes[1]\n    - (see judgment5_B.json)\n    + %s' % QG[1][-170:])
sub(T0[0], 'observed_fact',
    '——合竞争解释中「盈亏平衡不必然走高」一半，但其「通胀读数数月内自行回落」一半尚未兑现；相反方向的证据来自更早的通胀上行段(三个月窗 2026-02→2026-05): '
    'BEI_10Y 自 2026-02-27 的 2.25(该上行段 2026-02-20 至 2026-05-04 的低点)升至 2026-05-04 的 2.50(该段峰值,亦为 2026 年内最高;月末对月末 2026-02-27→2026-05-29 仅 +13bp 至 2.38)，合主解释。',
    '——按判断口径(预期分立且引擎面观测在场),本环区分指标上的在场观测支持竞争解释「走低或持平」、不合主解释「走高或维持高位」;'
    '两点限定如实注记: 竞争解释的另一半(通胀读数数月内自行回落)为前瞻含义,截至截止日尚未兑现(欧元区 2026-10 读数 4.0 为年内新高；'
    '美国 CPI 同比 2026-09 回升至 3.72，仍低于 2026-05 的 4.17);更早的通胀上行段(三个月窗 2026-02→2026-05) BEI_10Y 自 2026-02-27 的 2.25 升至 2026-05-04 的 2.50,'
    '合主解释,但属另一事件窗,不改本窗裁定。', 'MAJOR-2')
assert T0[0]['face_off_verdict'] == '尚不能区分'
T0[0]['face_off_verdict'] = '支持竞争解释'
LOG.append('[MAJOR-2] transmission[0].links[0].face_off_verdict\n    - 尚不能区分\n    + 支持竞争解释')
old_vn = T0[0]['verdict_note']
assert old_vn.startswith('本问三窗方向一致向下') and old_vn.endswith('——尚不能区分。')
T0[0]['verdict_note'] = ('本问三窗方向一致向下(三个月窗 -14bp、近一月 -19bp、12 个月窗 -11bp),均合竞争解释「走低或持平」、不合主解释「走高或维持高位」——支持竞争解释;'
                         '竞争解释「通胀读数数月内自行回落」的一半尚未兑现(欧元区 2026-10 读数 4.0 为年内新高)与更早的 2026-02-27→2026-05-04 上行段合主解释,'
                         '均作限定注记,不改本窗裁定。')
LOG.append('[MAJOR-2] transmission[0].links[0].verdict_note\n    - %s\n    + %s' % (old_vn, T0[0]['verdict_note']))

# MINOR-1: three independent turnings
env = json.load(open(FR.report_dir + '/AGENT_SEAT_ENVELOPE.json', encoding='utf-8'))
tc = {(c.get('metric_id'), c.get('to_ym')): c for c in env['reader_map_contract']['engine_faces']['turning_candidates_top9']}
ind_c = tc[('INDPRO', '2026-02')]
assert (ind_c['dimension'], ind_c['from_ym'], ind_c['value_before'], ind_c['value_after']) == ('growth', '2025-11', 1.7543, 0.7972) \
    and round(ind_c['delta'], 4) == -0.9571
iy = yoy_series('INDPRO')
assert iy['2025-11'] == 1.7543 and iy['2026-02'] == 0.7972
path = {k: iy[k] for k in sorted(iy) if '2025-11' <= k <= '2026-10'}
assert min(path, key=path.get) == '2026-03' and round(path['2026-03'], 4) == 0.6861 and round(iy['2026-10'], 2) == 2.15
um = FR.monthly('UNEMPLOYMENT')
assert um['2025-11'] == 4.5 and um['2026-02'] == 4.4
gd = cells['EA_REAL_GDP_YOY']['anchors']
assert gd['3个月前']['value'] == 1.19 and gd['最新一期']['value'] == 1.28
sub(TN[0], 'follow_or_diverge',
    '美欧通胀同月抬升、月频证据先后未定;日本端属政策利率维度,未在通胀维同步。',
    '美欧通胀同月抬升、月频证据先后未定(同维度同窗,计为同一轮事件,不另列一行);其后欧元区读数 2026-06 回落至 2.8，2026-07 为 2.9、2026-10 为 4.0(越过 2026-05 的 3.2);'
    '日本端属政策利率维度,未在通胀维同步。', 'MINOR-1')
assert eh['2026-05'] == 3.2 and eh['2026-06'] == 2.8 and eh['2026-07'] == 2.9 and eh['2026-10'] == 4.0
sub(TN[0], 'narrative', '不可归因到具体成分】。',
    '不可归因到具体成分】。欧元区 HICP 同比同窗上行 1.3 个百分点(2026-02→2026-05 由 1.9 升至 3.2)，并延续为欧元区当前环境的主导变化(2026-10 达 4.0)。', 'MINOR-1')
old_ea = TN[1]
assert (old_ea['date'], old_ea['value_before'], old_ea['value_after']) == ('2026-05', 1.9, 3.2)
TN[1] = {
    'date': '2026-02', 'metric_id': 'INDPRO', 'before_date': '2025-11', 'value_before': 1.7543, 'value_after': 0.7972,
    'first_mover': '美国工业生产同比在 2025-11→2026-02 由 1.7543 降至 0.7972(引擎同比空间,三个月变动 -0.9571),为增长维候选池内最大的三个月变化;'
                   '同一窗口美国失业率由 4.5 降至 4.4(2026-02),就业端未同向走弱。',
    'follow_or_diverge': '欧元区端: 本问证据面无欧元区工业生产序列(缺该项,增长维月频证据对欧元区不可判);欧元区实际 GDP 同比为季频且按降级口径引用,'
                         '引擎点值面读数仅微幅变动(数值见走位对照),不足以判定跟进或背离。',
    'narrative': '美国工业生产同比回落: 三个月下降 0.9571 个百分点,2026-03 见底后回升,至 2026-10 为 2.15(见走位对照);'
                 '窗口(2025-11→2026-02)止于通胀转折窗(2026-02→2026-05)的起点月份,两窗仅在该月相接。',
}
LOG.append('[MINOR-1] reader_map.turnings[1]  EA_HICP_YOY@2026-05 (same round as CPI@2026-05) -> INDPRO@2026-02 (growth)\n    + %s' % json.dumps(TN[1], ensure_ascii=False))
assert [(t['metric_id'], t['date']) for t in TN] == [('CPI', '2026-05'), ('INDPRO', '2026-02'), ('JP_POLICY_RATE', '2026-07')]
eps, picks = rmp.turning_merge_and_picks(TN, list(tc.values()))
assert len(eps) == 3 and picks == [], (len(eps), picks)

# MINOR-2: JGB point values in snapshot facts
facts = FR.snap.get('facts') or {}
def fval(mid):
    rows = facts.get(mid) if isinstance(facts, dict) else [x for x in facts if x.get('metric_id') == mid]
    return {r['observation_date']: r['value'] for r in rows}
assert (fval('JGB2Y')['2026-11-19'], fval('JGB5Y')['2026-11-19'], fval('JGB10Y')['2026-11-19']) == (1.853, 2.235, 2.87)
assert not any(m in ss for m in ('JGB2Y', 'JGB5Y', 'JGB10Y')) and not any(r.startswith('JGB') for r in EI)
sub(CH[0]['links'][1], 'missing_link_note',
    '本引擎无日本套息持仓与中长端融资成本(国债收益率)序列,该环为【假设】,缺环待采;可核环节仅政策利率路径本身(E1)。',
    '本问证据面未纳入日本套息持仓与日本国债收益率(快照事实面仅有 2026-11-19 点值 JGB 2/5/10 年 1.853/2.235/2.87,序列库无历史、未入证据索引),该环为【假设】;'
    '可核环节仅政策利率路径本身(E1)。', 'MINOR-2')

# MINOR-3 + NIT-9: USDJPY changes and history position
u = ss['USDJPY']
assert u['dates'][0] == '2016-11-23' and len(u['dates']) == 2601 and u['dates'][-1] == FR.as_of and round(u['values'][-1], 2) == 159.35
assert round(FR.val('USDJPY', '2026-10-23'), 3) == 156.494 and round(FR.ret('USDJPY', '2026-10-23', FR.as_of), 2) == 1.82 \
    and round(FR.ret('USDJPY', '2026-08-19', FR.as_of), 2) == -0.13
assert round(100.0 * sum(1 for v in u['values'] if v <= u['values'][-1]) / len(u['values']), 1) == 96.6
uw = [v for d, v in zip(u['dates'], u['values']) if d >= '2025-11-19']
assert round(100.0 * sum(1 for v in uw if v <= u['values'][-1]) / len(uw)) == 71
sub(CH[0]['links'][2], 'text', '当前 USDJPY 仍处高位(近 12 个月窗内约第 71 百分位)而股指已明显回落',
    '当前 USDJPY 报 159.35、近一月(2026-10-23→2026-11-23)不降反升 1.82%(三个月 -0.13%),'
    '仍处高位(近 12 个月窗内约第 71 百分位、序列库全史 2016-11-23 起约第 96.6 百分位)而股指已明显回落', 'MINOR-3')

# MINOR-4: buffer bands between scenario statements and their thresholds
sub(SC[0]['rows'], 'scenario', 'EA_HICP_YOY 同比维持 3.5% 以上,美国 CORE_PCE 同比维持 3.0% 以上',
    'EA_HICP_YOY 同比维持 3.5% 以上(证伪线为 3.0%,3.0% 至 3.5% 之间为缓冲带),美国 CORE_PCE 同比维持 3.0% 以上', 'MINOR-4')
sub(SC[0]['rows']['falsification'], 'threshold', '连续两个月低于 3.0%,通胀粘性假设被证伪',
    '连续两个月低于 3.0%(情景陈述的界为 3.5%,3.0% 至 3.5% 之间为缓冲带——情景陈述在该带内不成立但未达证伪线),通胀粘性假设被证伪', 'MINOR-4')
sub(SC[1]['rows'], 'scenario', 'EA_HICP_YOY 同比回落至 3.0% 以下,美国 CORE_PCE 同比回落至 2.8% 以下',
    'EA_HICP_YOY 同比回落至 3.0% 以下(触发线为 3.4%,3.0% 至 3.4% 之间为缓冲带),美国 CORE_PCE 同比回落至 2.8% 以下', 'MINOR-4')
sub(SC[1]['rows']['trigger'], 'condition', 'EA_HICP_YOY 同比连续两个月回落且最新值 ≤3.4%,同时 BEI_10Y 低于 2.0%',
    'EA_HICP_YOY 同比连续两个月回落且最新值 ≤3.4%(至情景陈述的界 3.0% 之间为缓冲带),同时 BEI_10Y 低于 2.0%', 'MINOR-4')
sub(SC[1]['rows']['falsification'], 'threshold', '同比均不低于 4.0%,一次性因素假设被证伪',
    '同比均不低于 4.0%(情景陈述的界为 3.0%,3.0% 至 4.0% 之间为缓冲带——在该带内既未触发也未证伪),一次性因素假设被证伪', 'MINOR-4')

# NIT-1: competing explanation aligned with competing_predicts (growth fears only)
assert '增长担忧主导' in T0[2]['competing_predicts']
sub(T0[2], 'competing_explanation', '若风险收缩由增长担忧或仓位/流动性冲击主导,则应见避险买盘压低利率',
    '若风险收缩由增长担忧主导(仓位/流动性冲击至多放大跌幅,不必然带来避险买盘),则应见避险买盘压低利率', 'NIT-1')

# NIT-2 / NIT-4: US walk face (unemployment path; missing 2025-10 base)
RG = [r for r in RM['regions'] if '失业率 4.1%(2026-07)持平至 4.1%(2026-10)' in r.get('from_to', '')]
assert len(RG) == 1
assert [um[k] for k in ('2026-07', '2026-08', '2026-09', '2026-10')] == [4.1, 4.1, 4.2, 4.1]
sub(RG[0], 'from_to', '失业率 4.1%(2026-07)持平至 4.1%(2026-10)', '失业率 4.1%(2026-07)至 4.1%(2026-10)两锚持平(中间 2026-09 为 4.2)', 'NIT-2')
cpd = ss['CPI']
assert not any(d.startswith('2025-10') for d in cpd['dates']) and any(d.startswith('2025-09') for d in cpd['dates']) \
    and any(d.startswith('2025-11') for d in cpd['dates'])
ents = FR.cal.get('entries') if isinstance(FR.cal, dict) else FR.cal
if isinstance(ents, dict):
    ents = list(ents.values())
conv = [e for e in ents if e.get('entry_id') == 'RC-2025SHUTDOWN-REST-CONSERVATIVE']
assert len(conv) == 1 and 'CPI' in (conv[0].get('metric_ids') or []) and conv[0].get('obs_to') == '2025-10-31' \
    and conv[0].get('first_publish_on_or_after') == '2026-01-22'
sub(RG[0], 'from_to', '2026-10 同比因缺上年同月基期观测不可得,指数水平 332.813→337.476)',
    '2026-10 同比因缺上年同月基期观测不可得——2025-10 为序列库缺采,冻结日历保守界条目以 2026-01-22 为该月联邦统计的可见界;指数水平 332.813→337.476)', 'NIT-4')
sub(CS[0], 'statement', '同比派生口径 2026-10 因缺上年同月基期观测不可得,最近有效同比见走位对照)',
    '同比派生口径 2026-10 因缺上年同月基期观测不可得(2025-10 为序列库缺采,非上年同月未发布),最近有效同比见走位对照)', 'NIT-4')

# NIT-3 / NIT-10: headline (calendar verification coverage; snapshot-time sensitivity)
dec = max(e.get('decision_date') for e in ents if e.get('decision_date'))
assert dec == '2026-10-30' and (dt.date.fromisoformat(FR.as_of) - dt.date.fromisoformat(dec)).days == 24
assert round(FR.ret('SPX', '2026-11-20', FR.as_of), 2) == 4.25 and ss['SPX']['dates'][-1] == FR.as_of
HL = RM['headline_conclusion']
assert HL.count('距上次调整按生效日 60 天、按决议日 66 天;近一月') == 1 and HL.count('11-23 值为盘中快照(非收盘价))。') == 1
HL = rep(HL, '距上次调整按生效日 60 天、按决议日 66 天;近一月',
         '距上次调整按生效日 60 天、按决议日 66 天(日历核验覆盖止于 2026-10-30,其后至截止日的 24 天引擎日历无条目);近一月')
HL = rep(HL, '11-23 值为盘中快照(非收盘价))。', '11-23 值为盘中快照(非收盘价),幅度对快照时点敏感)。')
RM['headline_conclusion'] = HL
LOG.append('[NIT-3/NIT-10] reader_map.headline_conclusion\n    + …%s' % HL[-230:])

# NIT-5 / NIT-6 / NIT-8: L3 statements and explanations
e = ss['EURUSD']
assert e['dates'][-1] == FR.as_of and e['values'][-1] == 1.093972 and round(FR.ret('EURUSD', '2026-08-19', FR.as_of), 2) == -5.52
ew = [v for d, v in zip(e['dates'], e['values']) if d >= '2025-11-19']
assert min(ew) == e['values'][-1] and sum(1 for v in ew if v == min(ew)) == 1 and 'EURUSD@2026-11-23' in EI
subl(CS[0]['competing_explanations'], 0, '(弱欧元放大输入压力)',
    '(弱欧元放大输入压力;弱欧元一项有在场读数——欧元兑美元 2026-11-23 为 1.093972,近 12 个月窗最低,三个月 -5.52%,11-23 为盘中快照)', 'NIT-5')
assert 'EURUSD@2026-11-23' not in CS[0]['evidence_refs']
CS[0]['evidence_refs'].append('EURUSD@2026-11-23')
LOG.append('[NIT-5] l3.contradictions[0].evidence_refs\n    + EURUSD@2026-11-23')
assert round(eh['2026-09'], 1) == 3.8 and round(cy['2026-09'], 4) == 3.7173
sub(CS[0], 'statement', '水平高于美国(数值与观测月见走位对照;',
    '水平高于美国(最新可比同月仅略高、幅度很小,且 HICP 与 CPI 口径不同;数值与观测月见走位对照;', 'NIT-6')
sub(CS[1], 'statement', '两地硬数据增长面大体平稳、并非本期主导变化(软数据不在本问证据面,未纳入)。',
    '两地硬数据增长面大体平稳、并非本期主导变化(软数据不在本问证据面,未纳入;口径注记: 此处工业生产按指数水平表述,与通胀的同比口径不同,'
    '其同比口径的三个月变动见走位对照)。', 'NIT-8')

# NIT-11: observable band for "next month's mean stays near the current level"
jr = FR.monthly('JP_POLICY_RATE')
assert jr['2026-10'] == 1.227
flat = [round(abs(jr[b] - jr[a]), 4) for a, b in (('2026-02', '2026-03'), ('2026-03', '2026-04'), ('2026-04', '2026-05'), ('2026-07', '2026-08'))]
assert max(flat) <= 0.001 and round(1.227 - 0.03, 2) == 1.20 and round(1.227 + 0.03, 2) == 1.26
subl(CS[2]['competing_explanations'], 0, '下月月均应维持当前水平附近。',
    '下月月均应维持当前水平附近(本解释下的可观察带宽: 2026-11 月均落在 1.20 至 1.26 之间,即较 2026-10 月均上下不超过 0.03——'
    '2026-02 至 2026-05 与 2026-08 的相邻月均差均不超过 0.001,取更宽的带作容差;读数跌破带下沿则本解释不成立)。', 'NIT-11')

with open(j_out, 'w', encoding='utf-8') as fh:
    json.dump(J, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
print('\n'.join(LOG))
print('folded %d edits | in=%s out=%s run=%s git=%s' % (len([x for x in LOG if x.startswith('[')]), j_in, j_out, RID, (R.get('git_head') or '')[:12]))
