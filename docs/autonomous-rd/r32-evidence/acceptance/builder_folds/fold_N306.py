#!/usr/bin/python3 -I
"""fold_N306.py <judgment_in.json> <tree> <run_dir> <judgment_out.json>

Builder revision of the NEW30 work-order judgment (Japan / euro-area
inflation and policy environment over the latest six months) after the
independent review it received at stamp 8f9055d (round 1, UPHELD: 0 MAJOR /
8 MINOR / 10 NIT; recorded verbatim in the X engine tree as
VERDICT-20261123T213353Z-01.json).  The input is the judgment exactly as it
stood when that review was made (judgment5_N30.json), already re-bound to
this run's round id by restamp_judgment.py (the work order was re-planned at
the new stamp; its frozen inputs are the same).  Every number quoted in a
replacement sentence is recomputed here from the run's own frozen inputs
(root_overlay snapshot / release calendar / report.json) and asserted before
the text is written.  Read-only on the run directory.

Folded (reviewer item numbers):
  #0 MINOR  C2: the 2.5% level marked as the series' last observation with
           the DEGRADED status and the not-yet-visible decision face
  #1 MINOR  C1 / JP walk paragraph: the national CPI year-on-year rate is
           the engine's own computation (two base-period files spliced)
  #2 MINOR  C3 / headline / walk paragraphs: sixth evidence gap (euro-area
           government-bond yields absent in the snapshot while the Japanese
           ones are present; none of the five in the evidence index)
  #3 MINOR  turning row: Tokyo CPI series marked as noncore_missing
  #4 MINOR  face-off table: the reasoning behind each "cannot distinguish"
           written into the rendered observed_fact (verdict_note is not
           rendered); noted in quality_gate_notes[1]
  #5 MINOR  C2: registry release semantics versus the engine's
           decision-date convention
  #6/#9     C3: the engine faces disagree on the ECB series (DEGRADED versus
     MINOR/ decision_dated / status=ok); contract STALE on the 2.5% token
     NIT     named
  #7 MINOR  EA walk paragraph: 2026-05-16 inferred release date is a Saturday
  #8 NIT    "two largest single-day jumps" -> within the jump window
  #10 NIT   frozen-calendar coverage limited to the Japan / euro-area face
  #11 NIT   "decision, i.e. effective" -> "decision, effective" (lexical
           change in four places, one of them main_predicts)
  #12 NIT   "in-window monthly path" -> visible path; the 2026-05 reading's
           observation date precedes the window, its release date is inside
  #13 NIT   UST_10Y 5.04% given with its observation date
  #14 NIT   scenario notes: the S1 trigger band and the VIX 25-30 gap
  #15 NIT   chain link title "policy follow-through" -> "same-direction change"
  #16 NIT   Tokyo CPI release wording
  #17 NIT   the 2026-04 dip in the Japanese inflation path noted
Operator adaptations to the reviewer's fix text: #1 and #2 keep the L3
statements free of Arabic figures for un-aliased metrics (the figures are
written in the walk paragraphs instead); #4 condenses each verdict_note; #6
writes the day count in Chinese numerals inside the statement.
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
DASH = '–'


def rep(s, old, new, n=1):
    assert s.count(old) == n, ('anchor count', s.count(old), n, old[:48])
    return s.replace(old, new)


def sub(obj, key, old, new, where):
    obj[key] = rep(obj[key], old, new)
    LOG.append('[%s] %s\n    - %s\n    + %s' % (where, key, old, new))


def app(obj, key, tail, add, where):
    """append `add` to a string field that must end with `tail`."""
    assert obj[key].endswith(tail) and add not in obj[key], (where, obj[key][-60:])
    obj[key] = obj[key] + add
    LOG.append('[%s] %s (append)\n    + %s' % (where, key, add))


RM = J['reader_map']
CS = {c['id']: c for c in J['l3']['contradictions']}
LK = J['l3']['mechanism_chains'][0]['links']
T = RM['transmission'][0]['links']
S = {s['id']: s['rows'] for s in J['l4']['scenarios']}
Q = J['quality_gate_notes']
REG = {r['region']: r for r in RM['regions']}
rp = FR.rep['research_plan']
cells = {c['metric_id']: c for c in rp['point_values']['cells']}
EI = {x.get('ref') for x in FR.rep.get('evidence_index') or []}
cal = FR.cal['entries'] if isinstance(FR.cal, dict) else FR.cal
facts = FR.snap.get('facts') or {}
ga = FR.snap['gate_a']

# ---- structure of the audited version --------------------------------------
assert sorted(CS) == ['C1-INFL-DIVERGE', 'C2-POLICY-SYNC-LEVEL-GAP', 'C3-EVIDENCE-GAPS']
assert len(LK) == 4 and len(T) == 3 and sorted(S) == ['S1-DIVERGE-PERSIST', 'S2-CONVERGE'] and len(Q) == 6
assert sorted(REG) == ['EA', 'JP'] and len(RM['turnings']) == 3 and RM['turnings'][2]['metric_id'] == 'JP_CPI_TOKYO_YOY'
assert FR.as_of == '2026-11-23' and FR.snap.get('snapshot_id') == 'research_snapshot_20261123' and len(EI) == 60
assert [t['distinguishing_metric'] for t in T] == ['EA_HICP_YOY', 'EURUSD', 'VIX'] and [t['face_off_verdict'] for t in T] == ['尚不能区分'] * 3
C1, C2, C3 = CS['C1-INFL-DIVERGE'], CS['C2-POLICY-SYNC-LEVEL-GAP'], CS['C3-EVIDENCE-GAPS']
EA, JP = REG['EA'], REG['JP']

# ---- frozen facts used below ------------------------------------------------
facts_rows = lambda m: [x for x in facts if x.get('metric_id') == m]  # noqa: E731  (facts = flat list of rows)
for m, v in (('ECB_MRO', 2.65), ('ECB_DFR', 2.5)):
    rows = facts_rows(m)
    assert len(rows) == 1 and rows[0]['fact_id'] == '%s@2026-09-16' % m and rows[0]['value'] == v and rows[0]['quality_status'] == 'DEGRADED'
    assert m in ga['noncore_degraded'] and m not in ga['noncore_missing'] and FR.last_date(m) == '2026-09-16'
    reg = FR.registry_metric(m)
    assert reg['freshness']['max_calendar_lag_days'] == 10 and reg['freshness'].get('decision_dated') is True
    assert '无更晚已证实决议不作过期' in reg['freshness']['decision_dated_note'] and '决议公布后生效并当日更新系列' in reg['release_semantics']
    assert cells[m]['anchors']['最新一期']['status'] == 'ok' and cells[m]['anchors']['最新一期']['freshness_basis'] == 'policy_confirmation'
DAYS = (dt.date.fromisoformat(FR.as_of) - dt.date.fromisoformat(FR.last_date('ECB_DFR'))).days
assert DAYS == 68
jgb = {m: facts_rows(m) for m in ('JGB2Y', 'JGB5Y', 'JGB10Y')}
for m, v in (('JGB2Y', 1.853), ('JGB5Y', 2.235), ('JGB10Y', 2.87)):
    assert len(jgb[m]) == 1 and jgb[m][0]['fact_id'] == '%s@2026-11-19' % m and jgb[m][0]['value'] == v and jgb[m][0]['quality_status'] == 'PASS'
for m in ('BUND_10Y', 'BUND_2Y'):
    assert m in ga['noncore_missing'] and not facts_rows(m) and 'READ_FAIL' in ga['noncore_missing_detail'][m] and '非采集遗漏' in ga['noncore_missing_detail'][m]
for m in ('BUND_10Y', 'BUND_2Y', 'JGB2Y', 'JGB5Y', 'JGB10Y'):
    FR.registry_metric(m)
    assert not [r for r in EI if r.startswith(m + '@')]
assert 'JP_CPI_TOKYO_YOY' in ga['noncore_missing'] and not facts_rows('JP_CPI_TOKYO_YOY')
jpc = FR.registry_metric('JP_CPI_YOY')['calc']
assert '各自基期内做严格同月同比后拼接' in jpc and '2026-09=2.16 vs 官方2.1' in jpc
ea_h = FR.monthly('EA_HICP_YOY')
jp_c = FR.monthly('JP_CPI_YOY')
assert [ea_h[k] for k in ('2026-01', '2026-02', '2026-04', '2026-05', '2026-07', '2026-08', '2026-09', '2026-10')] == [1.7, 1.9, 3.0, 3.2, 2.9, 3.2, 3.8, 4.0]
assert (jp_c['2026-03'], jp_c['2026-04'], jp_c['2026-05']) == (1.46, 1.38, 1.53) and round(jp_c['2026-03'] - jp_c['2026-04'], 2) == 0.08
for m, a, b in (('ECB_MRO', 2.15, 2.4), ('ECB_DFR', 2.0, 2.25)):
    assert FR.val(m, '2025-06-11') == a and FR.val(m, '2026-06-16') == a and FR.val(m, '2026-06-17') == b
    w = [(d, v) for d, v in zip(ss[m]['dates'], ss[m]['values']) if '2025-06-11' <= d <= '2026-06-16']
    assert w == [('2025-06-11', a)], (m, w)        # step series (change points only): one level from 2025-06-11 until the 2026-06-17 change
    assert [x for x, _y in zip(ss[m]['dates'], ss[m]['values']) if x > '2026-06-17'] == ['2026-09-16']
assert (dt.date(2026, 6, 17) - dt.date(2025, 6, 11)).days == 371 and (dt.date(2026, 9, 16) - dt.date(2026, 6, 17)).days == 91
assert round(FR.val('ECB_MRO', '2026-06-17') - FR.val('ECB_MRO', '2026-06-16'), 2) == 0.25 and round(FR.val('ECB_MRO', FR.as_of) - FR.val('ECB_MRO', '2026-06-17'), 2) == 0.25   # each change +25bp
tgt = [x for x in cal if x.get('metric_id') == 'JP_POLICY_TARGET']
assert len(tgt) == 2 and tgt[0]['entry_id'] == 'RC-JP-BOJ-TARGET-2026-09' and tgt[0]['decision_date'] == '2026-09-18' and tgt[0]['effective_on'] == '2026-09-24'
assert FR.last_date('UST_10Y') == '2026-11-19' and FR.val('UST_10Y', FR.as_of) == 5.04 and FR.val('ECB_MRO', FR.as_of) == 2.65 and tgt[0]['target_value'] == 1.25
vix = ss['VIX']
assert round(vix['values'][vix['dates'].index('2026-11-20')], 2) == 35.89 and round(vix['values'][-1], 2) == 27.01 and vix['dates'][-1] == FR.as_of
assert round((27.01 / 35.89 - 1) * 100, 1) == -24.7 and round(FR.ret('VIX', '2026-11-20', '2026-11-23'), 1) == -24.7
assert (dt.date(2026, 11, 13) - dt.date(2026, 10, 30)).days == 14 and (dt.date(2026, 11, 13) - dt.date(2026, 9, 16)).days == 58
assert dt.date(2026, 5, 16).weekday() == 5 and rmp._visible_publish('EA_HICP_YOY', 'monthly', '2026-04-01')[0] == '2026-05-16'
assert '月末+16天' in rmp._visible_publish('EA_HICP_YOY', 'monthly', '2026-04-01')[1]
for m, first in (('EA_HICP_YOY', '2026-06-16'), ('JP_CPI_YOY', '2026-06-20')):
    rule = rmp._visible_publish(m, 'monthly', '2026-05-01')
    assert rule[0] == first, (m, rule)
    for ym in ('2026-06', '2026-07', '2026-08', '2026-09', '2026-10'):
        assert '2026-05-23' <= ym + '-01' <= rmp._visible_publish(m, 'monthly', ym + '-01')[0] <= FR.as_of, (m, ym)
    assert FR.last_date(m) == '2026-10-01'
cal_n = [x for x in cal if x.get('metric_id') == 'JP_POLICY_TARGET']
cal_e = [x for x in cal if x.get('metric_id') == 'EA_HICP_YOY']
assert len(cal) == 18 and len(cal_n) == 2 and len(cal_e) == 3 and len(cal) - len(cal_n) - len(cal_e) == 13
xenv = {}
for line in open('/tmp/r32-accept/env5.sh', encoding='utf-8'):
    line = line.strip()
    if line.startswith('export RD_N30='):
        xenv['rd'] = line[len('export RD_N30='):].strip('"')
xver = json.load(open(os.path.join(xenv['rd'], 'report.json'), encoding='utf-8'))['agent_judgment']['contract_verification']['verdicts']
xstale = {(v['metric'], v['token']) for v in xver if v['status'] == 'STALE'}
assert xstale == {('ECB_DFR', '2.5%')}, xstale            # the same-statement review at the previous stamp

# ---- #0: C2, the 2.5% level is the series' last observation ------------------
sub(C2, 'statement', '升至最新水平 2.5%(观测=序列变更日=生效日 2026-09-16)',
    '升至序列末观测水平 2.5%(观测=序列变更日=生效日 2026-09-16;事实行质量状态 DEGRADED——序列止于该日,其后决议面不可见【尚未验证】,详见「证据不足」第②项)', '#0 MINOR')

# ---- #5: registry release semantics versus the engine convention -----------
sub(C2, 'statement', '决议日系引擎按『生效日前上一个周四』惯例自变更日回推、属【推断】而非实录(冻结发布日历对欧央行无实录条目)',
    '决议日系引擎按『生效日前上一个周四』惯例自变更日回推、属【推断】而非实录(冻结发布日历对欧央行无实录条目;注册表该序列 release_semantics 另载决议公布后生效并当日更新系列,'
    '两口径不一,本档以序列变更日=生效日为实证面)', '#5 MINOR')

# ---- #1: the national CPI rate is the engine's own computation --------------
sub(C1, 'statement', '日本全国CPI同比百分之二点四四(观测 2026-10,发布 2026-11-20,引擎推定规则、非日历实录)',
    '日本全国CPI同比百分之二点四四(观测 2026-10,发布 2026-11-20,引擎推定规则、非日历实录;该序列为引擎按注册表口径自算的同比值——双基期档各自同月同比后拼接,非官方公布值直取)', '#1 MINOR')
sub(JP, 'from_to', ';最新读数相比去年同月(2025-10 为 2.99)低 0.55 个百分点',
    ';全国 CPI 同比为引擎按注册表口径自算的同比值(双基期档各自同月同比后拼接;注册表载与官方公布值抽验 2026-09 为 2.16 对官方 2.1),非官方公布值直取;'
    '最新读数相比去年同月(2025-10 为 2.99)低 0.55 个百分点', '#1 MINOR')

# ---- #2: sixth evidence gap (government-bond yields) -------------------------
st = C3['statement']
assert st.count('证据不足') >= 1 and st.count('①日本政策目标宣布值口径不可得') == 1 and '⑤增长与核心通胀背景对照缺席' in st
sub(C3, 'statement', '问句所求「证据不足」面,引擎可核者五项。', '问句所求「证据不足」面,引擎可核者六项。', '#2 MINOR')
sub(C3, 'statement', '另: 东京都CPI序列自 2026-01 起',
    '⑥两地国债收益率期限结构对照不对称: 欧元区两年期与十年期国债收益率在册,当日快照 Gate A 列于缺席名单(事实行缺席,注记=子源缺席——源端不可得或未采,非采集遗漏);'
    '日本端二年、五年、十年期国债收益率事实行在场(观测 2026-11-19,质量状态 PASS),但五条序列均不在本问证据索引,该一维无法对照(指标 id 与数值见走位面)。'
    '另: 东京都CPI序列自 2026-01 起', '#2 MINOR')
HL = RM['headline_conclusion']
assert HL.count('证据不足五项') == 1 and HL.count('五项') == 1
sub(RM, 'headline_conclusion', '证据不足五项: 日本宣布值口径序列不可得', '证据不足六项: 日本宣布值口径序列不可得', '#2 MINOR')
sub(RM, 'headline_conclusion', '增长与核心通胀背景对照缺席(GDP 两序列在册、当日快照事实行缺席,注册表无核心通胀)。',
    '增长与核心通胀背景对照缺席(GDP 两序列在册、当日快照事实行缺席,注册表无核心通胀)、'
    '两地国债收益率期限结构对照不对称(欧元区两年期与十年期在册而当日快照缺席,日本端事实行在场,均不在本问证据索引)。', '#2 MINOR')
app(EA, 'from_to', '高 1.9 个百分点。',
    '国债收益率(市场利率面): BUND_10Y、BUND_2Y 在册,当日快照 Gate A 列于缺席名单(子源缺席,源端不可得或未采,非采集遗漏),事实行缺席、不在本问证据索引。', '#2 MINOR')
app(JP, 'from_to', '点值取自快照序列面、L1 无对应事实行。',
    '国债收益率(市场利率面): JGB2Y、JGB5Y、JGB10Y 当日快照事实行在场(2026-11-19 为 1.853、2.235、2.87,质量状态 PASS),不在本问证据索引;两地期限结构无法对照。', '#2 MINOR')

# ---- #3: turning row, Tokyo series marked ------------------------------------
sub(RM['turnings'][2], 'first_mover', '东京都 CPI 同比(速报先行口径)2026-06→2026-09 由 1.6 升至 2.69(三个月 +1.09 个百分点)。',
    '东京都 CPI 同比(速报先行口径;该序列当日快照 Gate A 列于 noncore_missing,读数取自快照序列面、L1 无对应事实行)2026-06→2026-09 由 1.6 升至 2.69(三个月 +1.09 个百分点)。', '#3 MINOR')

# ---- #4: the reasoning behind each "cannot distinguish" in the rendered face -
for t in T:
    assert t['verdict_note'] and '尚不能区分' in t['verdict_note']     # the first link is appended after the #11 lexical edit
app(T[1], 'observed_fact', '该面不构成检验。',
    '裁定理由: 主解释预期的方向分立未纳入美元端利率(UST_10Y 最新 5.04%(观测 2026-11-19),高于 MRO 2.65% 与 BOJ 目标约 1.25%),利差主导对本月窗同样预期两货币对美元走弱,两解释在该观测上预期未分立;'
    'EURJPY 交叉盘不在证据面,以 EURUSD×USDJPY 推算幅度小(-0.24%/-0.73%)——尚不能区分。', '#4 MINOR')
app(T[2], 'observed_fact', '较 2026-11-20 收盘 -24.7%)。',
    '裁定理由: VIX 跳升时点(2026-11-13→2026-11-20)不与政策日历对齐(自跳升起点计,距最近政策日 2026-10-30 为 14 天、距 ECB 最近生效日 2026-09-16 为 58 天),读数发布主因未获跨地区支持,竞争解释(冲击主导)在时点上占优;'
    '但其『快速回落』预期在本跳升上仅有一个盘中观测(2026-11-23 快照 27.01,较 2026-11-20 收盘 35.89 为 -24.7%),『幅度』判据不能区分政策冲击与流动性冲击——证据倾向竞争解释但不足以裁定,尚不能区分。', '#4 MINOR')
sub(Q, 1, '均附置信注记)。', '均附置信注记;裁定理由摘要已写入各环 observed_fact——verdict_note 字段不进读者报告渲染)。', '#4 MINOR')

# ---- #6 / #9: the engine faces disagree on the ECB series; contract STALE ----
sub(C3, 'statement', '当日快照 Gate A 将该两序列列于降级名单(L1 事实行 quality_status=DEGRADED);',
    '当日快照 Gate A 将该两序列列于降级名单(L1 事实行 quality_status=DEGRADED;注册表 freshness 另设 decision_dated 规则——无更晚已证实决议不作过期,'
    '而研究计划点值格记该锚 status=ok,引擎各面不一,故降级是否成立与其后是否有新决议在引擎面同样不可判);', '#6 MINOR')
sub(C3, 'statement', '在引擎面不可判【尚未验证】。③本窗月度通胀读数的公布时间为推定规则非实录',
    '在引擎面不可判【尚未验证】;引擎契约验证对本档水平对照所引存款便利利率数值串记状态 STALE——数值一致、观测滞后六十八天。③本窗月度通胀读数的公布时间为推定规则非实录', '#9 NIT')

# ---- #7: the inferred release date 2026-05-16 is a Saturday -----------------
sub(EA, 'from_to', '发布 2026-05-16,引擎推定规则、非日历实录', '发布 2026-05-16,周六——引擎月末+16 天推定规则、非日历实录,实际发布日以官方实录为准', '#7 MINOR')

# ---- #8: "two largest single-day jumps" within the jump window ---------------
sub(LK[3], 'text', '为窗内两个最大单日跳升日', '为跳升窗内两个最大单日跳升日', '#8 NIT')
sub(T[2], 'verdict_note', '为窗内两个最大单日跳升日', '为跳升窗内两个最大单日跳升日', '#8 NIT')

# ---- #10: calendar coverage --------------------------------------------------
sub(C3, 'statement', '冻结日历实录仅覆盖日本政策目标两条与三条历史期 EA HICP 快报/终值实录',
    '冻结日历实录于日欧面仅覆盖日本政策目标两条与三条历史期 EA HICP 快报/终值实录', '#10 NIT')

# ---- #11: "decision, i.e. effective" -> "decision, effective" ---------------
for obj, key, where in ((LK[1], 'text', 'l3.mechanism_chains[0].links[1]'), (T[0], 'observed_fact', 'transmission[0].links[0].observed_fact'),
                        (T[0], 'verdict_note', 'transmission[0].links[0].verdict_note'), (T[0], 'main_predicts', 'transmission[0].links[0].main_predicts')):
    assert (dt.date(2026, 9, 24) - dt.date(2026, 9, 18)).days == 6
    obj[key] = rep(obj[key], 'BOJ 2026-09-18 决议即 2026-09-24 生效', 'BOJ 2026-09-18 决议、2026-09-24 生效')
    LOG.append('[#11 NIT] %s.%s\n    - BOJ 2026-09-18 决议即 2026-09-24 生效\n    + BOJ 2026-09-18 决议、2026-09-24 生效%s'
               % (where, key, '  (lexical only: the two dates are unchanged)' if key == 'main_predicts' else ''))

# ---- #12: visible monthly path -----------------------------------------------
sub(EA, 'from_to', '窗内月度路径 3.2(2026-05)→2.8(2026-06)→2.9(2026-07)→3.2(2026-08)→3.8(2026-09)→4.0(2026-10),',
    '窗内可见月度路径 3.2(2026-05)→2.8(2026-06)→2.9(2026-07)→3.2(2026-08)→3.8(2026-09)→4.0(2026-10)'
    '(2026-05 期观测日 2026-05-01 早于窗起 2026-05-23、推定发布日 2026-06-16 在窗内,其余各期观测与发布均在窗内),', '#12 NIT')
sub(JP, 'from_to', '窗内逐月路径 1.53(2026-05)→1.67(2026-06)→1.97(2026-07)→1.98(2026-08)→2.16(2026-09)→2.44(2026-10);',
    '窗内可见逐月路径 1.53(2026-05)→1.67(2026-06)→1.97(2026-07)→1.98(2026-08)→2.16(2026-09)→2.44(2026-10)'
    '(2026-05 期观测日 2026-05-01 早于窗起 2026-05-23、推定发布日 2026-06-20 在窗内,其余各期观测与发布均在窗内);', '#12 NIT')

# ---- #13: UST_10Y observation date ------------------------------------------
sub(LK[2], 'text', 'UST_10Y 最新 5.04%', 'UST_10Y 最新 5.04%(观测 2026-11-19)', '#13 NIT')
sub(T[1], 'verdict_note', 'UST_10Y 最新 5.04%', 'UST_10Y 最新 5.04%(观测 2026-11-19)', '#13 NIT')

# ---- #14: scenario notes -----------------------------------------------------
s1, s2 = S['S1-DIVERGE-PERSIST'], S['S2-CONVERGE']
assert 'HICP 同比维持 3.5% 以上' in s1['scenario'] and 'EA_HICP_YOY 同比 ≥4.0%' in s1['trigger']['condition'] and '收盘高于 30' in s1['trigger']['condition']
assert '收盘低于 25' in s2['trigger']['condition'] and 'VIX' not in s1['falsification']['threshold'] and 'VIX' not in s2['falsification']['threshold']
old14 = '3.0%' + DASH + '3.5% 区间不触发亦不证伪;政策分量'
assert Q[3].count(old14) == 1
sub(Q, 3, old14,
    '3.0%' + DASH + '3.5% 区间不触发亦不证伪;S1 触发阈 4.0% 高于前提水平 3.5%,3.5%' + DASH + '4.0% 区间同属前提成立而不触发;VIX 收盘在 25' + DASH + '30 之间时两情景均不触发(证伪条件均不含 VIX 分量);政策分量',
    '#14 NIT')

# ---- #15: chain link title ---------------------------------------------------
sub(LK[1], 'text', '观察: 政策面跟进——', '观察: 政策面同向变更——', '#15 NIT')

# ---- #16 / #17: JP walk paragraph wording -----------------------------------
sub(JP, 'from_to', '东京都 CPI 同比(中旬速报先行口径)', '东京都 CPI 同比(速报先行口径)', '#16 NIT')
sub(JP, 'from_to', '此后总体回升。', '此后总体回升(2026-03 的 1.46→2026-04 的 1.38 有一次 0.08 个百分点的小幅回落)。', '#17 NIT')

# ---- #4 (continued): first link, appended after the #11 lexical edit --------
app(T[0], 'observed_fact', 'BOJ 2026-09-18 决议、2026-09-24 生效,目标 1.25%。',
    '裁定理由: 读数驱动与程序驱动均与在场观测相容——两次变更前可见读数(决议日前/生效日前两口径)均高于 2026-02 的 1.9,合读数驱动;反向观察同样在场: 两序列自 2025-06-11 至 2026-06-17 维持 2.15/2.0 共 371 天,'
    '其间读数已由 2026-01 的 1.7 升至 2026-04 的 3.0 而未触发变更;两次变更相隔 91 天、各 +25bp,等距等幅路径与『按季程序』相容;欧央行样本仅两次(n=2)——尚不能区分。', '#4 MINOR')


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
    'quality_gate_notes[1]', 'quality_gate_notes[3]',
    'l3.contradictions[0].statement', 'l3.contradictions[1].statement', 'l3.contradictions[2].statement',
    'l3.mechanism_chains[0].links[1].text', 'l3.mechanism_chains[0].links[2].text', 'l3.mechanism_chains[0].links[3].text',
    'reader_map.transmission[0].links[0].observed_fact', 'reader_map.transmission[0].links[0].verdict_note',
    'reader_map.transmission[0].links[0].main_predicts',
    'reader_map.transmission[0].links[1].observed_fact', 'reader_map.transmission[0].links[1].verdict_note',
    'reader_map.transmission[0].links[2].observed_fact', 'reader_map.transmission[0].links[2].verdict_note',
    'reader_map.headline_conclusion', 'reader_map.turnings[2].first_mover',
    'reader_map.regions[0].from_to', 'reader_map.regions[1].from_to',
}
assert changed == expected, sorted(changed ^ expected)
assert J['agent_declaration'] == OLD['agent_declaration']
for t_old, t_new in zip(OLD['reader_map']['transmission'][0]['links'], T):
    assert t_old['face_off_verdict'] == t_new['face_off_verdict'] and t_old['competing_predicts'] == t_new['competing_predicts']
    assert t_new['main_predicts'] == t_old['main_predicts'].replace('BOJ 2026-09-18 决议即 2026-09-24 生效', 'BOJ 2026-09-18 决议、2026-09-24 生效')

with open(j_out, 'w', encoding='utf-8') as fh:
    json.dump(J, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
print('\n'.join(LOG))
print('folded %d edits | in=%s out=%s run=%s git=%s' % (len([x for x in LOG if x.startswith('[')]), j_in, j_out, RID, (R.get('git_head') or '')[:12]))
