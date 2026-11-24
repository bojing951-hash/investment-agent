#!/usr/bin/python3 -I
"""fold_A6.py <judgment_in.json> <tree> <run_dir> <judgment_out.json>

Builder revision of the A work-order judgment (global macro change map:
US / China / euro area / Japan, 12 months ago / 3 months ago / latest)
after the independent review it received at stamp 8f9055d (round 1,
REVISE: 3 MAJOR / 4 MINOR / 4 NIT; recorded verbatim in the engine tree as
VERDICT-20261123T213303Z-01).  The input is the judgment exactly as it
stood when that review was made (judgment5_A.json), already re-bound to
this run's round id by restamp_judgment.py (the work order was re-planned
at the new stamp; its frozen inputs are the same).  Every number quoted in
a replacement sentence is recomputed here from the run's own frozen inputs
(root_overlay snapshot / release calendar / seat envelope / report.json)
and asserted before the text is written.  Read-only on the run directory.

Folded:
  MAJOR-1  scenario 2 falsification threshold: the distance from the last
           reading to the 2020-11-30 low is 38 bp; 35 bp is the distance
           from the last reading to the 1.8 threshold (two distances mixed)
  MAJOR-2  turning 1 first mover: China PPI did not rise every month after
           its low (2026-07 fell 4.1 -> 3.5)
  MAJOR-3  turning 2 first mover: the top candidate overall is China PPI
           (4.8); China manufacturing PMI is first only within growth
  MINOR-1  explanation B: the 1-month decomposition fits only one leg
  MINOR-2  HY_OAS falsification level: warning level 3.53 added
  MINOR-3  transmission 2 link 1: the window directions the face-off rests
           on are written into the observed fact
  MINOR-4  "7-day reverse repo unchanged" carries its observation endpoint
  NIT-2    "back to the pre-cut level" names the 2025-12 cut
  NIT-3    % signs on the 12-month equity changes; HY_OAS unit label
  NIT-4    BOJ 2026-10-30 maintenance decision cited
Not adopted:
  NIT-1    evidence-ref labels CN_PPI_YOY@2026-10-31 / CN_CPI_YOY@2026-10-31
           are the evidence index's own labels (engine residual); changing
           them in the judgment would break the reference binding.
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


RM = J['reader_map']
CS = J['l3']['contradictions']
CH = J['l3']['mechanism_chains']
TR = RM['transmission']
T0, T1 = TR[0]['links'], TR[1]['links']
TN = RM['turnings']
SC = J['l4']['scenarios']
assert [c['id'] for c in CS] == ['C1', 'C2', 'C3'] and [c['id'] for c in CH] == ['M1', 'M2']
assert [t['chain_id'] for t in TR] == ['TR1', 'TR2'] and len(CH[0]['links']) == 4 and len(CH[1]['links']) == 2
assert [t['metric_id'] for t in TN] == ['CPI', 'INDPRO', 'JP_CPI_YOY'] and [s['id'] for s in SC] == ['SCN1', 'SCN2']

# ── computed facts (frozen inputs of this run) ─────────────────────────
assert FR.as_of == '2026-11-23' and FR.snap['snapshot_id'] == 'research_snapshot_20261123'
mp = FR.monthly

# MAJOR-1: BEI_10Y distance to the last sub-1.8 reading vs to the threshold
b = ss['BEI_10Y']
low = [(d, v) for d, v in zip(b['dates'], b['values']) if d <= FR.as_of and v < 1.8][-1]
last_d, last_v = b['dates'][-1], b['values'][-1]
assert low == ('2020-11-30', 1.77) and (last_d, last_v) == ('2026-11-20', 2.15)
assert round((last_v - low[1]) * 100) == 38 and round((last_v - 1.8) * 100) == 35
assert FR.date('BEI_10Y', FR.as_of) == '2026-11-20'
sub(SC[1]['rows']['falsification'], 'threshold', '较最新读数 2.15(2026-11-20)低 35 个基点',
    '较最新读数 2.15(2026-11-20)低 38 个基点(该读数较阈值 1.8 高 35 个基点)', 'MAJOR-1')

# MAJOR-2: China PPI path after its in-window low
cp = mp('CN_PPI_YOY')
months = ['2025-11', '2025-12', '2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06',
          '2026-07', '2026-08', '2026-09', '2026-10']
assert [cp[k] for k in months] == [-2.2, -1.9, -1.4, -0.9, 0.5, 2.8, 3.9, 4.1, 3.5, 3.8, 5.0, 5.7]
assert min(cp[k] for k in months) == cp['2025-11']                      # in-window low = 2025-11
rises = [(a, b_) for a, b_ in zip(months, months[1:]) if cp[b_] < cp[a]]
assert rises == [('2026-06', '2026-07')] and cp['2026-06'] == 4.1 and cp['2026-07'] == 3.5 and cp['2026-10'] == 5.7
sub(TN[0], 'first_mover', '中国 PPI 低点在 2025-11 且此后连升',
    '中国 PPI 低点在 2025-11，此后总体上行(至 2026-10 的 5.7；其间仅 2026-07 由 4.1 回落至 3.5)', 'MAJOR-2')

# MAJOR-3: candidate face ranking (seat envelope, engine face)
env = json.load(open(os.path.join(FR.report_dir, 'AGENT_SEAT_ENVELOPE.json'), encoding='utf-8'))
top9 = env['reader_map_contract']['engine_faces']['turning_candidates_top9']
assert (top9[0]['metric_id'], top9[0]['dimension'], top9[0]['from_ym'], top9[0]['to_ym']) == \
    ('CN_PPI_YOY', 'inflation', '2026-02', '2026-05')
assert (top9[0]['value_before'], top9[0]['value_after'], top9[0]['delta']) == (-0.9, 3.9, 4.8)
first_growth = [c for c in top9 if c['dimension'] == 'growth'][0]
assert first_growth['metric_id'] == 'CN_PMI_MFG' and top9[1]['metric_id'] == 'CN_PMI_MFG'
assert '%.2f' % first_growth['delta'] == '3.40' and '%.1f' % top9[0]['delta'] == '4.8'
sub(TN[1], 'first_mover', '(候选面全体首位为中国制造业PMI，增量3.40)',
    '(中国制造业PMI居增长维候选面首位，增量3.40；候选面全体首位为中国PPI同比，增量4.8)', 'MAJOR-3')

# MINOR-1: explanation B vs the 1-month decomposition (TIPS_10Y up, BEI_10Y down)
def common_change(mid, d0, d1):
    a, b_ = FR.val(mid, d0), FR.val(mid, d1)
    return round((b_ - a) * 100)


assert common_change('TIPS_10Y', '2026-10-20', '2026-11-19') == 11 \
    and common_change('BEI_10Y', '2026-10-20', '2026-11-19') == -19
assert T0[2]['face_off_verdict'] == '尚不能区分'
ce = CS[0]['competing_explanations']
ce[1] = rep(ce[1], '近1个月分解(实际+11bp、盈亏平衡-19bp)与该解释相容',
            '近1个月分解(实际+11bp、盈亏平衡-19bp)与该解释的盈亏平衡一腿相容、与实际利率一腿相左, 整体仅部分相容')
LOG.append('[MINOR-1] l3.contradictions[0].competing_explanations[1]\n    - 近1个月分解(实际+11bp、盈亏平衡-19bp)与该解释相容\n'
           '    + 近1个月分解(实际+11bp、盈亏平衡-19bp)与该解释的盈亏平衡一腿相容、与实际利率一腿相左, 整体仅部分相容')
CS[0]['competing_explanations'] = ce

# MINOR-2: HY_OAS levels
h = ss['HY_OAS']
assert FR.val('HY_OAS', '2025-05-09') == 3.53 and FR.date('HY_OAS', '2025-05-09') == '2025-05-09'
after = [(d, v) for d, v in zip(h['dates'], h['values']) if d > '2025-05-09']
assert max(after, key=lambda x: x[1]) == ('2026-11-19', 3.52)             # nothing since 2025-05-09 is at/above the latest reading
assert len([1 for d, v in after if v >= 3.52]) == 1 and h['dates'][-1] == '2026-11-19' and h['values'][-1] == 3.52 \
    and FR.val('HY_OAS', '2025-05-09') >= h['values'][-1]
assert max(zip(h['values'], h['dates'])) == (4.61, '2025-04-07') and round((4.61 - 3.52) * 100) == 109
sub(CH[0]['links'][3], 'text', '证伪观察=HY_OAS 升破 4.61 的序列高点(量化阈值，【假设】的可观察形态)。',
    '证伪观察分两级: 预警级=HY_OAS 升破 2025-05-09 的 3.53(库内上一次不低于最新读数的水平)，失效级=升破 4.61 的序列高点'
    '(距最新读数 109 个基点，单用偏松；量化阈值，【假设】的可观察形态)。', 'MINOR-2')
sub(T0[2], 'main_predicts', 'HY_OAS 不升破序列高点(非信用事件级)',
    'HY_OAS 不升破序列高点(非信用事件级；预警级=升破 2025-05-09 的 3.53，失效级=升破 4.61)', 'MINOR-2')
sub(T0[2], 'competing_predicts', 'HY_OAS 走阔', 'HY_OAS 走阔(升破预警级 3.53 起)', 'MINOR-2')

# MINOR-3: window directions behind the TR2 link-1 face-off (intraday snapshot caliber)
def series_map(mid):
    return dict(zip(ss[mid]['dates'], ss[mid]['values']))


spx, uj = series_map('SPX'), series_map('USDJPY')
assert round(FR.ret('SPX', '2026-10-23', '2026-11-23'), 2) == -5.51 and FR.date('SPX', '2026-10-23') == '2026-10-23'
assert FR.date('USDJPY', '2026-10-23') == '2026-10-23' and FR.date('SPX', '2026-11-23') == '2026-11-23'
u0 = FR.val('USDJPY', '2026-10-23')
assert round(u0, 2) == 156.49 and round(FR.val('USDJPY', '2026-11-23'), 2) == 159.35
assert round((FR.val('USDJPY', '2026-11-23') / u0 - 1.0) * 100, 2) == 1.82
BASE = '2026-10-23'
DAYS = sorted(d for d in spx if d > BASE and d <= '2026-11-23' and d in uj)
assert len(DAYS) == 21 and DAYS[0] == '2026-10-26' and DAYS[-1] == '2026-11-23'
prev = BASE
RS, RU = [], []
for d in DAYS:
    RS.append(spx[d] / spx[prev] - 1)
    RU.append(uj[d] / uj[prev] - 1)
    prev = d
_n = len(RS)
_mr, _mu = sum(RS) / _n, sum(RU) / _n
CORR = (sum((a - _mr) * (b_) for a, b_ in zip(RS, RU))
        / (sum((a - _mr) ** 2 for a in RS) ** 0.5 * sum((b_ - _mu) ** 2 for b_ in RU) ** 0.5))
assert '%.2f' % CORR == '0.19'
DN = [1 for a, b_ in zip(RS, RU) if a < 0 and b_ < 0]
UPP = [1 for a, b_ in zip(RS, RU) if a > 0 and b_ > 0]
NDN = len([a for a in RS if a < 0])
assert NDN == 12 and len(DN) == 9 and len(UPP) == 7 and len(DN) + len(UPP) == 16
sub(T1[0], 'observed_fact', 'USDJPY 水平159.35@2026-11-23(2026-11-23 盘中快照、非收盘价);',
    'USDJPY 水平159.35@2026-11-23(2026-11-23 盘中快照、非收盘价)；对质所依据的窗内方向(2026-10-23→2026-11-23，'
    '盘中快照口径): 标普500指数 -5.51% 而美元兑日元 +1.82%(156.49→159.35)，逐日面(2026-10-26 至 2026-11-23 共 21 个交易日)'
    '两者日变动相关系数 0.19、同向 16 日(标普500指数下跌的 12 日中美元兑日元同跌 9 日)；', 'MINOR-3')

# MINOR-4: the 7-day reverse repo has no observation after 2026-10-30
assert FR.last_date('CN_OMO_7D') == '2026-10-30' and FR.as_of == '2026-11-23'
sub(RM, 'headline_conclusion', '中国未跟进加息(7天逆回购利率与LPR窗内无变动；2026-11-02起',
    '中国未跟进加息(7天逆回购利率与LPR窗内无变动——7天逆回购末观测2026-10-30、其后至截止日缺观测；2026-11-02起', 'MINOR-4')
sub(CS[2], 'statement', 'CN_LPR_1Y 与 7天逆回购利率窗内持平、',
    'CN_LPR_1Y 与 7天逆回购利率窗内持平(7天逆回购末观测 2026-10-30，其后缺观测)、', 'MINOR-4')
sub(T0[1], 'observed_fact', '中国央行未跟进加息(7天逆回购利率与 LPR 窗内无变动；',
    '中国央行未跟进加息(7天逆回购利率与 LPR 窗内无变动，7天逆回购末观测 2026-10-30、其后缺观测；', 'MINOR-4')
sub(TN[0], 'follow_or_diverge', '中国未跟进(7天逆回购与 LPR 窗内无变动，2026-11-02 起',
    '中国未跟进(7天逆回购与 LPR 窗内无变动，7天逆回购末观测 2026-10-30、其后缺观测，2026-11-02 起', 'MINOR-4')
sub(TN[2], 'follow_or_diverge', '背离者=中国(7天逆回购 1.4 与 LPR 3.0 窗内无变动，2026-11-02 起',
    '背离者=中国(7天逆回购 1.4 与 LPR 3.0 窗内无变动，7天逆回购末观测 2026-10-30、其后缺观测，2026-11-02 起', 'MINOR-4')

# NIT-2: the cut DFF came back to = the 2025-12-11 cut (plateau 3.89 just before it; 3.88 since 2026-09-17)
d = ss['DFF']
i_cut = d['dates'].index('2025-12-11')
assert d['values'][i_cut] == 3.64 and d['values'][i_cut - 1] == 3.89 and d['dates'][i_cut - 1] == '2025-12-10' \
    and d['values'][-1] == 3.88 and d['dates'][-1] <= FR.as_of
pre = [(dd, v) for dd, v in zip(d['dates'], d['values']) if '2025-11-28' <= dd <= '2025-12-10']
assert pre[0][1] == 3.89 and pre[-1][1] == 3.89 and len({v for _dd, v in pre}) == 1   # plateau before the cut = 3.89
post = [(dd, v) for dd, v in zip(d['dates'], d['values']) if dd > '2025-12-10']
assert max(v for _dd, v in post) == 3.88 and [dd for dd, v in post if v == 3.88][0] == '2026-09-17'   # back near the plateau since 2026-09-17
# (the pre-cut plateau 3.89 is deliberately not written as a figure: the deterministic verifier binds
#  every DFF figure in the statement to the latest evidence value 3.88)
sub(CS[0], 'statement', 'DFF 回到降息前水平、', 'DFF 回到 2025-12 降息前的台阶附近(现 3.88)、', 'NIT-2')

# NIT-3: % signs on the 12-month equity changes; HY_OAS unit label
for mid, want in (('SPX', 8.03), ('NIKKEI225', 22.47), ('DAX', 9.93)):
    assert round(FR.ret(mid, '2025-11-19', '2026-11-19'), 2) == want, mid
assert (FR.registry_metric('HY_OAS') or {}).get('unit') == 'percentage_point'
sub(CH[0]['links'][3], 'text', '与 SPX 8.03、NIKKEI225 22.47、DAX 9.93 同向上行',
    '与 SPX +8.03%、NIKKEI225 +22.47%、DAX +9.93% 同向上行', 'NIT-3')
sub(T0[2], 'causal_hypothesis', '与 SPX 8.03、NIKKEI225 22.47、DAX 9.93 同向上行',
    '与 SPX +8.03%、NIKKEI225 +22.47%、DAX +9.93% 同向上行', 'NIT-3')
sub(CH[0]['links'][3], 'text', '(当前 3.52pp，低于 2025-04-07 序列高点 4.61',
    '(当前 3.52pp(注册表单位为百分点)，低于 2025-04-07 序列高点 4.61', 'NIT-3')
sub(T0[2], 'observed_fact', 'HY_OAS 水平 3.52pp@2026-11-19:', 'HY_OAS 水平 3.52pp(百分点)@2026-11-19:', 'NIT-3')

# NIT-4: BOJ 2026-10-30 maintenance decision (frozen release calendar)
ents = FR.cal.get('entries') if isinstance(FR.cal, dict) else FR.cal
if isinstance(ents, dict):
    ents = list(ents.values())
by_id = {e.get('entry_id'): e for e in ents or []}
assert by_id['RC-JP-BOJ-TARGET-2026-09']['decision_date'] == '2026-09-18' \
    and by_id['RC-JP-BOJ-MAINT-2026-10']['decision_date'] == '2026-10-30'
sub(CH[1]['links'][0], 'text', '发布日历实录载政策决议2026-09-18(生效2026-09-24);USDJPY 水平159.35',
    '发布日历实录载政策决议2026-09-18(生效2026-09-24);另载 2026-10-30 会议确认维持政策目标利率不变'
    '(确认维持不改变目标水平，只更新核验覆盖截止);USDJPY 水平159.35', 'NIT-4')
sub(TN[2], 'follow_or_diverge', '发布日历实录载政策决议2026-09-18(生效2026-09-24,目标水平 1.25)',
    '发布日历实录载政策决议2026-09-18(生效2026-09-24,目标水平 1.25)与 2026-10-30 确认维持决议', 'NIT-4')

with open(j_out, 'w', encoding='utf-8') as fh:
    json.dump(J, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
print('\n'.join(LOG))
print('folded %d edits | in=%s out=%s run=%s git=%s' % (len([x for x in LOG if x.startswith('[')]), j_in, j_out, RID, (R.get('git_head') or '')[:12]))
