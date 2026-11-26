#!/usr/bin/python3
"""fold_B4.py <judgment_in.json> <run_dir> <judgment_out.json>

Builder revision of the B work-order judgment (US/EA three-month comparison
+ BOJ policy level/duration) after the independent review it received at the
superseded stamp 19638e1 (REVISE: 1 MAJOR / 6 MINOR / 10 NIT).  The work
order was re-planned at the final stamp; the frozen inputs are the same
collection, so every number quoted in a replacement sentence is recomputed
here from the run's own frozen inputs (root_overlay snapshot / registry) and
asserted before the text is written.  Read-only on the run directory.

Must-fix (MAJOR): transmission link with distinguishing metric TIPS_10Y
against the nominal yield — the face-off verdict "supports the main
explanation" exceeded the evidence, because the competing explanation (growth
outlook / term premium / fiscal supply) implies the same observation under
nominal = real + breakeven; verdict becomes "cannot yet distinguish".
Also folded: the MINOR precision/disclosure items and the NIT wording items
of that review that the evidence face supports.
"""
import copy
import datetime
import json
import sys
sys.path.insert(0, '/tmp/r32-accept/scripts')
import seatlib_r32 as L                                  # noqa: E402

j_in, rd, j_out = sys.argv[1:4]
FR = L.Frozen(rd)
D0 = datetime.date.fromisoformat(FR.as_of)
J = copy.deepcopy(json.load(open(j_in, encoding='utf-8')))
assert J['agent_declaration']['produced_by'].count('20261123T193157Z') == 1
LOG = []


def rep(s, old, new, n=1):
    assert s.count(old) == n, ('anchor count', s.count(old), n, old[:48])
    return s.replace(old, new)


def sub(obj, key, old, new, where):
    obj[key] = rep(obj[key], old, new)
    LOG.append('[%s] %s\n    - %s\n    + %s' % (where, key, old if len(old) < 400 else old[:400] + '…',
                                              new if len(new) < 400 else new[:400] + '…'))


def sub_list(obj, key, idx, old, new, where):
    lst = obj[key]
    lst[idx] = rep(lst[idx], old, new)
    LOG.append('[%s] %s[%d]\n    - %s\n    + %s' % (where, key, idx, old, new))


def monthly(mid):
    return FR.monthly(mid)


def yoy(p, ym):
    k = '%04d-%02d' % (int(ym[:4]) - 1, int(ym[5:7]))
    return None if k not in p or ym not in p else (p[ym] / p[k] - 1) * 100


# ── computed facts (frozen inputs of this run) ─────────────────────────
rep_run = FR.rep
TRIO3 = ('UST_10Y', 'TIPS_10Y', 'BEI_10Y')
COM = sorted(set.intersection(*(set(FR.ss[m]['dates']) for m in TRIO3)))
TO = '2026-11-19'
assert TO in COM
D3 = max(d for d in COM if d <= '2026-08-19')
assert D3 == '2026-08-19'
D1 = max(d for d in COM if d <= '2026-10-20')
assert D1 == '2026-10-20'
CHG = {}
for name, d0 in (('3m', D3), ('1m', D1), ('12m', '2025-11-19')):
    CHG[name] = {m: round((FR.val(m, TO) - FR.val(m, d0)) * 100) for m in TRIO3}
    assert CHG[name]['UST_10Y'] == CHG[name]['TIPS_10Y'] + CHG[name]['BEI_10Y']
assert CHG['3m'] == {'UST_10Y': 39, 'TIPS_10Y': 53, 'BEI_10Y': -14}, CHG['3m']
assert CHG['1m'] == {'UST_10Y': -8, 'TIPS_10Y': 11, 'BEI_10Y': -19}, CHG['1m']
assert CHG['12m'] == {'UST_10Y': 91, 'TIPS_10Y': 102, 'BEI_10Y': -11}, CHG['12m']
assert FR.val('BEI_10Y', D3) == 2.30 and FR.val('BEI_10Y', TO) == 2.16
assert FR.val('BEI_10Y', '2026-11-20') == 2.15 and FR.last_date('BEI_10Y') == '2026-11-20'
win = [(d, v) for d, v in zip(FR.ss['BEI_10Y']['dates'], FR.ss['BEI_10Y']['values'])
       if '2025-11-19' < d <= '2026-11-20']
assert min(win, key=lambda x: x[1]) == ('2026-11-20', 2.15) and len(win) == 251
assert FR.val('BEI_10Y', '2026-02-27') == 2.25 and FR.val('BEI_10Y', '2026-05-04') == 2.50
assert round((FR.val('TIPS_10Y', TO) - FR.val('TIPS_10Y', '2026-10-23')) * 100) == 22
# three windows all real-up / breakeven-down
for name in CHG:
    assert CHG[name]['TIPS_10Y'] > 0 > CHG[name]['BEI_10Y']
# inflation readings behind the "not yet fallen" half
ea = monthly('EA_HICP_YOY')
assert (ea['2026-07'], ea['2026-08'], ea['2026-09'], ea['2026-10']) == (2.9, 3.2, 3.8, 4.0)
cy = {ym: yoy(monthly('CPI'), ym) for ym in monthly('CPI')}
assert round(cy['2026-07'], 2) == 3.30 and round(cy['2026-08'], 2) == 3.35 and round(cy['2026-09'], 2) == 3.72
assert cy['2026-07'] > ea['2026-07'] and cy['2026-08'] > ea['2026-08'] and cy['2026-09'] < ea['2026-09']
assert yoy(monthly('CPI'), '2026-10') is None and yoy(monthly('CORE_CPI'), '2026-10') is None
assert '2025-10-01' not in FR.ss['CORE_CPI']['dates'] and '2025-10-01' not in FR.ss['CPI']['dates']
assert max(v for k, v in ea.items() if k.startswith('2026')) == 4.0
# industrial production: yoy up, level almost flat, base effect
ip = monthly('INDPRO')
assert (round(yoy(ip, '2026-07'), 2), round(yoy(ip, '2026-10'), 2)) == (1.25, 2.15)
assert round((ip['2026-10'] / ip['2026-07'] - 1) * 100, 2) == 0.22
assert round((ip['2026-10'] / ip['2026-09'] - 1) * 100, 2) == -0.43
assert round((ip['2025-10'] / ip['2025-07'] - 1) * 100, 2) == -0.66
# BOJ uncollateralised overnight monthly averages
jp = monthly('JP_POLICY_RATE')
assert (jp['2026-08'], jp['2026-09'], jp['2026-10']) == (0.977, 1.043, 1.227)
assert round((jp['2026-09'] - jp['2026-08']) * 100) == 7 and round((jp['2026-10'] - jp['2026-09']) * 100) == 18
# EA GDP yoy: observation age vs registry freshness ceiling
reg_ea = next(m for m in FR.reg['metrics'] if m.get('metric_id') == 'EA_REAL_GDP_YOY')
assert reg_ea['freshness']['max_calendar_lag_days'] == 120
assert FR.last_date('EA_REAL_GDP_YOY') == '2026-07-01'
assert (D0 - datetime.date(2026, 7, 1)).days == 145
# task-window coverage of the planned metrics
items = rep_run['run']['data_requirements']['items']
zero = [it for it in items if it['spec']['window']['n_in_window'] == 0
        and it.get('outcome') == 'insufficient_coverage']
assert len(items) == 9 and len(zero) == 9
w = items[0]['spec']['window']
assert (w['start'], w['end']) == ('2026-11-01', '2026-11-30')
# the plan's metric face carries no US / EA policy-rate series
pms = {it['metric_id'] for it in items}
assert not any(m in pms for m in ('DFEDTARU', 'ECB_DFR', 'ECB_MRO', 'EFFR', 'DFF'))
# planned US/EA policy decisions are not in the frozen calendar (only BOJ records)
# (already disclosed by the judgment; the main-explanation premise note relies on it)

T = J['reader_map']['transmission'][0]['links']
assert [l['distinguishing_metric'] for l in T] == ['BEI_10Y', 'TIPS_10Y', 'TIPS_10Y']

# ── MAJOR: link 1 (TIPS_10Y against the nominal yield) ─────────────────
sub(T[1], 'face_off_verdict', '支持主解释', '尚不能区分', 'transmission[0].links[1]')
sub(T[1], 'competing_predicts',
    '竞争解释(期限溢价/供给主导)预期 TIPS_10Y 与 BEI_10Y 组合无稳定主导关系',
    '竞争解释(增长前景/期限溢价/财政供给主导)同样预期 TIPS_10Y 上行并可与盈亏平衡回落并存，'
    '两解释在区分指标 TIPS_10Y 上预期方向不分立', 'transmission[0].links[1]')
OLD_TAIL = ('三个月、近一月、12 个月三窗均为「实际利率上行、盈亏平衡回落」，不合竞争解释「无稳定主导关系」的预期，'
            '这是「实际利率为名义利率主导上行分量」的证据来源；单月窗内名义利率下行、盈亏平衡变动幅度大于实际利率，'
            '单看单月窗不足以支持该主张。注: 「通胀走高而盈亏平衡回落」的组合与竞争解释的文字描述亦相容，'
            '该描述不构成两侧的区分预期，裁定只针对预注册的区分预期。')
NEW_TAIL = ('三个月、近一月、12 个月三窗均为「实际利率上行、盈亏平衡回落」(实际利率 +53/+11/+102bp、盈亏平衡 -14/-19/-11bp)：'
            '三个月窗与 12 个月窗的名义利率上行由实际利率分量主导；但增长前景、期限溢价或财政供给主导的解释同样预期'
            '实际利率(TIPS_10Y)上行并可与盈亏平衡回落并存——按「名义=实际+盈亏平衡」恒等式，通胀读数走高而盈亏平衡回落、'
            '名义利率仍上行时，上行只能来自实际分量——两解释在区分指标 TIPS_10Y 上的预期方向不分立；'
            '单月窗名义利率 -8bp 由盈亏平衡 -19bp 主导，亦不构成任一侧的区分证据——尚不能区分。')
sub(T[1], 'observed_fact', OLD_TAIL, NEW_TAIL, 'transmission[0].links[1]')
# NIT: the JP monthly-average sentence sat in the US rates link (not its distinguishing metric)
sub(T[1], 'observed_fact',
    ';JP_POLICY_RATE 月均 2026-09 1.043→2026-10 1.227,日本亦处政策利率抬升通道。与本问同口径的三个月窗',
    '。与本问同口径的三个月窗', 'transmission[0].links[1]')
OLD_VN = ('三个月窗实际 +53bp 主导名义 +39bp、12 个月窗实际 +102bp 主导名义 +91bp，合主解释；三窗均为实际上行、盈亏平衡回落，'
          '主导关系稳定；单月窗 TIPS_10Y +11bp 为唯一上行分量但幅度小于盈亏平衡 -19bp(名义 -8bp)，单月窗不足以单独支持'
          '——裁定基于三个月窗与 12 个月窗，单月窗证据有限。')
NEW_VN = ('三个月窗实际 +53bp 主导名义 +39bp、12 个月窗实际 +102bp 主导名义 +91bp，两窗名义上行确由实际利率分量主导；'
          '但期限溢价/财政供给/增长前景主导同样预期该组合，两解释在 TIPS_10Y 上的预期方向不分立——尚不能区分；'
          '单月窗名义 -8bp(实际 +11bp、盈亏平衡 -19bp)不构成任一侧的区分证据；'
          '主解释前件(央行紧缩偏向)在本环证据面未举证(本问计划指标面未纳入美欧政策利率序列)。')
sub(T[1], 'verdict_note', OLD_VN, NEW_VN, 'transmission[0].links[1]')
Q = J['quality_gate_notes']
sub(Q, 1,
    '传导面 3 环均给出主/竞争两侧对同一区分指标的不同预期，判断=尚不能区分 ×1、支持主解释 ×2(',
    '传导面 3 环均列出主/竞争两侧预期: 贴现率渠道环(区分指标 TIPS_10Y 相对 SPX)两侧预期分立且有在场观测，'
    '判断=支持主解释 ×1；另 2 环(区分指标 BEI_10Y；TIPS_10Y 相对名义利率——两解释在该指标上预期方向不分立)'
    '判断=尚不能区分 ×2(', 'quality_gate_notes[1]')

# ── MINOR: link 0 windows are all one direction; same-month rank; industrial production;
#    coverage / staleness / missing-base disclosures; month labels ─────────
sub(T[0], 'observed_fact',
    '区分指标 BEI_10Y 在各窗方向不一致: 与本问同口径的三个月窗(2026-08-19→2026-11-19)自 2.30 回落至 2.16(-14bp)，'
    '近一月共同交易日窗(2026-10-20→2026-11-19)变动 -19bp、12 个月窗(2025-11-19→2026-11-19)变动 -11bp，'
    '最新 2.15(观测 2026-11-20)，而通胀读数仍处高位',
    '区分指标 BEI_10Y 在本问三窗方向一致向下: 与本问同口径的三个月窗(2026-08-19→2026-11-19)自 2.30 回落至 2.16(-14bp)，'
    '近一月共同交易日窗(2026-10-20→2026-11-19)变动 -19bp、12 个月窗(2025-11-19→2026-11-19)变动 -11bp，'
    '最新 2.15(观测 2026-11-20，12 个月窗内最低)，均合竞争解释「走低或持平」，而通胀读数仍处高位',
    'transmission[0].links[0]')
sub(T[0], 'verdict_note',
    '各窗方向不一致: 三个月窗 -14bp、近一月 -19bp 合竞争解释，更早的 2026-02-27→2026-05-04 上行段合主解释'
    '——尚不能区分；竞争解释的「自行回落」一半尚未兑现。',
    '本问三窗方向一致向下: 三个月窗 -14bp、近一月 -19bp、12 个月窗 -11bp，均合竞争解释「走低或持平」；'
    '更早的 2026-02-27→2026-05-04 上行段(2.25→2.50)合主解释，且竞争解释「通胀读数数月内自行回落」的一半尚未兑现'
    '(欧元区 2026-10 读数 4.0 为年内新高)——尚不能区分。', 'transmission[0].links[0]')
sub(T[2], 'verdict_note', '本月窗口 TIPS_10Y +11bp 与 SPX -5.51% 同现,',
    '本月窗口 TIPS_10Y +22bp(2026-10-23→2026-11-19)与 SPX -5.51%(2026-10-23→2026-11-23)同现,',
    'transmission[0].links[2]')

C = {c['id']: c for c in J['l3']['contradictions']}
sub(C['C1-INFL-SYNC'], 'statement',
    '最新读数明显走高、为美欧两地最高水平(数值与观测月见走位对照)',
    '最新读数明显走高、水平高于美国(数值与观测月见走位对照;两地最新可比同月为九月，更早月份位次有交叉)',
    'C1-INFL-SYNC.statement')
sub(C['C1-INFL-SYNC'], 'statement', '但读数水平低于欧元区。', '但读数水平在最新可比同月低于欧元区。',
    'C1-INFL-SYNC.statement')
assert len(C['C2-GROWTH-STABLE']['competing_explanations']) == 2
sub_list(C['C2-GROWTH-STABLE'], 'competing_explanations', 0,
         '若美国工业生产同比回升(1.25→2.15,引擎派生口径)代表制造业周期回暖,则增长动能在 2026 年三季度后段重新加速,失业率低位与此相容。',
         '【假设】若美国工业生产同比回升(1.25→2.15,引擎派生口径)代表制造业周期回暖,则增长动能已重新加速'
         '(所引最新读数为 2026-10)，失业率低位与此相容。', 'C2-GROWTH-STABLE')
sub_list(C['C2-GROWTH-STABLE'], 'competing_explanations', 1, '主要为价格与基数效应或单月波动', '主要为基数效应或单月波动',
         'C2-GROWTH-STABLE')
assert len(C['C3-JP-POLICY']['competing_explanations']) == 2
sub_list(C['C3-JP-POLICY'], 'competing_explanations', 1, '2026-09 月均 0.977→1.043 仅 +7bp',
         '2026-08 月均 0.977→2026-09 月均 1.043，仅 +7bp', 'C3-JP-POLICY')
sub_list(C['C3-JP-POLICY'], 'competing_explanations', 0, '下月月均(预计次月初前后公布)应维持当前水平附近',
         '下月月均应维持当前水平附近', 'C3-JP-POLICY')

RM = J['reader_map']
sub(RM, 'headline_conclusion', '失业率走平、工业回升;', '失业率走平、工业生产同比回升(水平变化很小);', 'headline')
REG = {r['region']: r for r in RM['regions']}
sub(REG['US'], 'from_to', '增长环境大体平稳、边际略缓、工业动能回升: ', '增长环境大体平稳、边际略缓、工业生产同比回升: ',
    'regions[US]')
sub(REG['US'], 'from_to', '工业生产同比 1.25%(2026-07)→2.15%(2026-10)。',
    '工业生产同比 1.25%(2026-07)→2.15%(2026-10;指数水平 103.1675→103.3954，仅 +0.22%，其中 2026-10 环比 -0.43%，'
    '同比抬升含基数效应: 上年 2025-07→2025-10 基数下行 0.66%)。', 'regions[US]')
sub(REG['US'], 'from_to',
    '核心 CPI 同比 2.47%(2026-07)→2.57%(2026-09;指数水平 336.789→339.9)',
    '核心 CPI 同比 2.47%(2026-07)→2.57%(2026-09;2026-10 同比同样缺上年同月基期观测，'
    '指数水平 2026-07 336.789→2026-10 339.9)', 'regions[US]')
sub(REG['EA'], 'from_to', '(季观测 2026-04→2026-07,最新修订口径);',
    '(季观测 2026-04→2026-07,最新修订口径;最新观测距截止日 145 天，超过注册表最大日历滞后 120 天，按降级口径引用);',
    'regions[EA]')
sub(REG['JP'], 'from_to', '次月月均尚未发布(预计次月初前后公布),此后', '次月月均尚未发布,此后', 'regions[JP]')
TN = {t['metric_id']: t for t in RM['turnings']}
sub(TN['EA_HICP_YOY'], 'narrative', '其间 2026-06 回落至 2.8 后再度上行', '其后 2026-06 回落至 2.8 后再度上行', 'turnings[EA]')

sub(Q, 3, '美国 CPI 2026-10 同比缺 2025-10 基期(当月同比不可得)。',
    '美国 CPI 与核心 CPI 2026-10 同比均缺 2025-10 基期(当月同比不可得)。任务窗口(2026-11-01..2026-11-30)内 9 个计划指标的'
    '观测数均为 0(引擎判定均为覆盖不足——截止日 2026-11-23 尚无 11 月观测)，本档以截止日前最新已发布观测与 3 个月前锚作答，'
    '11 月完整结果须待数据覆盖后重跑。', 'quality_gate_notes[3]')
sub(Q, 3, '在序列库内有存量观测(最新观测 2026-07-01)，按降级口径引用。',
    '在序列库内有存量观测(最新观测 2026-07-01，距截止日 145 天，超过注册表最大日历滞后 120 天——与 US_REAL_GDP 同龄同倍数，'
    '按同一过期口径披露)，按降级口径引用。', 'quality_gate_notes[3]')
sub(Q, 5, '②文本一致性别名表未收录 EA_HICP_YOY 等部分计划指标——本档矛盾陈述对这些指标以不带数字的写法表述，'
          '走位/转折/传导面的数字以独立席位复算为准；',
    '②文本一致性别名表未收录 EA_HICP_YOY 等部分计划指标——本档矛盾陈述对这些指标以不带数字的写法表述，'
    '走位/转折/传导面的数字以独立席位复算为准；矛盾陈述中部分关键数字(日本央行目标水平与净变动)以中文数字书写，'
    '不在契约面阿拉伯数字绑定之列，同样只能人工复算；', 'quality_gate_notes[5]')
sub(Q, 5, '③传导链接的 verdict_note 字段不进渲染(裁定理由须写入 observed_fact)',
    '③传导链接的 verdict_note 字段与转折面的 narrative 字段不进渲染(裁定理由须写入 observed_fact)',
    'quality_gate_notes[5]')

S = {s['id']: s for s in J['l4']['scenarios']}
sub(S['S2-INFL-FADE']['rows']['falsification'], 'threshold', '若 2026-12 与 2027-01 两月 EA_HICP_YOY 同比均不低于 4.0%',
    '若 2026-12 与 2027-01 两月发布的 EA_HICP_YOY 同比均不低于 4.0%', 'S2.falsification')

# ── invariants ─────────────────────────────────────────────────────────
old = json.load(open(j_in, encoding='utf-8'))
assert J['agent_declaration'] == old['agent_declaration']
assert J['schema_version'] == old['schema_version']
for c_old, c_new in zip(old['l3']['contradictions'], J['l3']['contradictions']):
    assert c_old['id'] == c_new['id'] and c_old['evidence_refs'] == c_new['evidence_refs']
for a, b in zip(old['reader_map']['regions'], J['reader_map']['regions']):
    assert a['anchor_echo'] == b['anchor_echo']
for a, b in zip(old['l4']['scenarios'], J['l4']['scenarios']):
    assert a['id'] == b['id'] and a['rows']['trigger'] == b['rows']['trigger'] \
        and a['rows']['sensitive_variables'] == b['rows']['sensitive_variables']
assert [l['face_off_verdict'] for l in T] == ['尚不能区分', '尚不能区分', '支持主解释']
assert '支持主解释 ×2' not in json.dumps(J, ensure_ascii=False)
assert J != old
with open(j_out, 'w', encoding='utf-8') as fh:
    json.dump(J, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
import hashlib  # noqa: E402
raw = open(j_out, 'rb').read()
print('wrote', j_out, len(raw), 'bytes sha16', hashlib.sha256(raw).hexdigest()[:16])
print('replacements', len(LOG))
print('\n'.join(LOG))
