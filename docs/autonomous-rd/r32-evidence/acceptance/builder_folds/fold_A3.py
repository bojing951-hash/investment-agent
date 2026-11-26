#!/usr/bin/python3
"""fold_A3.py <prose_in.json> <faces.json> <run_dir> <out_prose.json> [<struct.json>]

Fold the independent pre-review of the A (global map) judgment into the
seat prose.  Pre-review: fresh-context seat, REVISE at the f722e3c run
(3 MAJOR / 14 MINOR / 16 NIT).  Every number below is recomputed from the
run's own frozen inputs (root_overlay snapshot / calendar / registry); each
replacement is guarded (exactly one occurrence) so a drifted base text fails
loudly instead of silently passing.  Adds `quality_gate_notes` (disclosure
block; no engine code reads it) and scenario roles (rendered by the map
report's scenario table).  Read-only on the run directory.
"""
import copy
import datetime
import json
import os
import re
import sys
sys.path.insert(0, '/tmp/r32-accept/scripts')
import seatlib_r32 as L                                  # noqa: E402

p_in, faces_p, rd, p_out = sys.argv[1:5]
FR = L.Frozen(rd)
AS_OF = FR.as_of
F = json.load(open(faces_p, encoding='utf-8'))
os.environ['IA_CALENDAR_PIN'] = os.path.join(rd, 'root_overlay', 'config',
                                             'release_calendar.json')
TREE = rd.split('/output/research_runs/')[0]
sys.path.insert(0, os.path.join(TREE, 'scripts'))
import research_map_planner as rmp                       # noqa: E402

assert F['report_dir'] == rd, (F['report_dir'], rd)
P = copy.deepcopy(json.load(open(p_in, encoding='utf-8')))
rm = P['reader_map']
D0 = datetime.date.fromisoformat(AS_OF)
CN_NUM = '零一二三四五六七八九'


def rep(s, old, new):
    assert s.count(old) == 1, ('anchor count', s.count(old), old[:48])
    return s.replace(old, new)


def yoy(mid, ym):
    p = FR.monthly(mid)
    k = '%04d-%02d' % (int(ym[:4]) - 1, int(ym[5:7]))
    return None if k not in p or ym not in p else (p[ym] / p[k] - 1) * 100


def visible(mid, day):
    """latest observation of `mid` whose (rule/calendar) publication <= day."""
    p = FR.monthly(mid)
    best = pub = None
    for ym in sorted(p):
        if ym + '-01' > day:
            break
        d, b = rmp._visible_publish(mid, 'monthly', ym + '-01')
        if d and d <= day:
            best, pub = (ym, p[ym]), (d, b)
    return best, pub


def bp(x):
    return '%+d' % int(round(x))


def cn_count(k):
    if k < 10:
        return CN_NUM[k]
    if k < 20:
        return '十' + (CN_NUM[k - 10] if k > 10 else '')
    return CN_NUM[k // 10] + '十' + (CN_NUM[k % 10] if k % 10 else '')


def cn_dec(x):
    i, d = ('%.1f' % x).split('.')
    return CN_NUM[int(i)] + '点' + CN_NUM[int(d)]


# ── computed facts ──────────────────────────────────────────────────────
WIN0 = (D0 - datetime.timedelta(days=365)).isoformat()          # window start day
W0M = WIN0[:7]
# US core PCE (index -> yoy)
cp = {ym: yoy('CORE_PCE', ym) for ym in FR.monthly('CORE_PCE')}
cp_win = {ym: v for ym, v in cp.items() if ym >= W0M and v is not None}
cp_last_ym = max(cp_win)
cp_hi_ym = max(cp_win, key=cp_win.get)
cp_after = {ym: v for ym, v in cp_win.items() if ym > cp_hi_ym}
cp_lo_ym = min(cp_after, key=cp_after.get)
assert cp_win[cp_last_ym] < cp_win[cp_hi_ym] and cp_hi_ym == '2026-05'
# US CPI yoy (index -> yoy), rule-based publication
cy = {ym: yoy('CPI', ym) for ym in FR.monthly('CPI')}
cy_win = {ym: v for ym, v in cy.items() if ym >= W0M and v is not None}
cy_hi_ym = max(cy_win, key=cy_win.get)
cy_trough_ym = min(((ym, v) for ym, v in cy_win.items() if ym <= '2026-05'),
                   key=lambda x: x[1])[0]
cy_pub = {ym: rmp._visible_publish('CPI', 'monthly', ym + '-01') for ym in cy_win}
RULE = {ym: d for ym, (d, b) in cy_pub.items() if '推定' in b}   # rule-based releases only
assert set(cy_win) - set(RULE) <= {'2025-09', '2025-11'}          # calendar-recorded shutdown releases
assert yoy('CPI', '2026-10') is None
# EA HICP / CN PPI / CN PMI / Brent / core CPI
ea = FR.monthly('EA_HICP_YOY')
ea_win = {ym: v for ym, v in ea.items() if ym >= W0M}
ea_lo_ym = min(((ym, v) for ym, v in ea_win.items() if ym <= '2026-05'),
               key=lambda x: x[1])[0]
ea_hi1 = max(ym for ym in ea_win if ym <= '2026-05')
ea_06, ea_last_ym = '2026-06', max(ea_win)
assert all(ea_win[b] >= ea_win[a] for a, b in zip(sorted(ea_win), sorted(ea_win)[1:])
           if a >= ea_06)
pp = FR.monthly('CN_PPI_YOY')
pp_win = {ym: v for ym, v in pp.items() if ym >= W0M}
pp_trough_ym = min(pp_win, key=pp_win.get)
pp_hi1 = max(ym for ym in pp_win if ym <= '2026-05')
pp_after = {ym: v for ym, v in pp_win.items() if ym > pp_hi1}
pp_lo_ym = min(pp_after, key=pp_after.get)
pp_last_ym = max(pp_win)
assert all(pp_win[ym] > pp_win[pp_trough_ym] for ym in pp_win if ym > pp_trough_ym)
pm = FR.monthly('CN_PMI_MFG')
pm_win = {ym: v for ym, v in pm.items() if ym >= W0M}
pm_above = [ym for ym in sorted(pm_win) if pm_win[ym] > 50]
pm_flat = [ym for ym in sorted(pm_win) if pm_win[ym] == 50]
pm_below = [ym for ym in sorted(pm_win) if pm_win[ym] < 50]
assert pm_above == ['2025-12', '2026-03', '2026-04', '2026-06', '2026-09']
assert pm_win['2026-07'] < 50 and pm_win['2026-10'] < 50
assert pm_flat == ['2026-05'] and pm_below                      # 线下区间(中文数位,用于矛盾陈述)
PM_REST_TXT = '%s 持平于%s，余在%s至%s之间' % (
    pm_flat[0], cn_count(int(pm_win[pm_flat[0]])),
    cn_count(int(min(pm_win[ym] for ym in pm_below))) + '点' + CN_NUM[int(round((min(pm_win[ym] for ym in pm_below) % 1) * 10))],
    cn_count(int(max(pm_win[ym] for ym in pm_below))) + '点' + CN_NUM[int(round((max(pm_win[ym] for ym in pm_below) % 1) * 10))])
br = FR.monthly('BRENT_F')
br_02, br_03, br_05 = '2026-02', '2026-03', '2026-05'
br_hi = max((ym for ym in br if br_02 <= ym <= br_05), key=lambda ym: br[ym])
br_chg = (br[br_05] / br[br_02] - 1) * 100
cc = {ym: yoy('CORE_CPI', ym) for ym in FR.monthly('CORE_CPI')}
# Japan policy rate monthly path (obs dated month-first)
JP = FR.monthly('JP_POLICY_RATE')
jp_seq = sorted(k for k in JP if k + '-01' >= WIN0)             # obs dated month-first
jp_carry_day = FR.date('JP_POLICY_RATE', WIN0)
jp_carry_ym, jp_carry = jp_carry_day[:7], FR.val('JP_POLICY_RATE', WIN0)
assert jp_carry_ym not in jp_seq                          # carry-in is pre-window
jp_first_in, jp_last_ym = jp_seq[0], jp_seq[-1]
jp_last = JP[jp_last_ym]
steps = [(b, (JP[b] - JP[a]) * 100) for a, b in zip([jp_carry_ym] + jp_seq, jp_seq)]
sig = [(ym, int(round(v))) for ym, v in steps if abs(v) >= 0.5]
noise = [ym for ym, v in steps if 0 < abs(v) < 0.5]
net_dec = round((jp_last - JP[jp_first_in]) * 100)
net_carry = round((jp_last - jp_carry) * 100)
assert jp_carry_ym == '2025-11' and jp_first_in == '2025-12' and jp_last_ym == '2026-10'
assert [v for _ym, v in sig] == [8, 17, 11, 14, 7, 18] and noise == ['2026-04', '2026-08']
assert net_dec == 67 and net_carry == 75
jpc = FR.monthly('JP_CPI_YOY')
j25 = {ym: v for ym, v in jpc.items() if '2025-01' <= ym <= '2026-02'}
jpc_hi_ym, jpc_lo_ym = max(j25, key=j25.get), min(j25, key=j25.get)
assert jpc_hi_ym == '2025-01' and jpc_lo_ym == '2026-02' and len(j25) == 14
jpc_up = [b for a, b in zip(sorted(j25), sorted(j25)[1:]) if j25[b] > j25[a]]
assert jpc_up == ['2025-09', '2025-10']               # the only upticks in the decline
jpc_11 = jpc['2025-11']
# ECB / Fed decision events (engine faces) + BOJ (frozen calendar records)
EV = [e for c in F['policy_event_clusters']['clusters'] for e in c['events']]
ecb = sorted((e for e in EV if e['metric_id'] == 'ECB_DFR'), key=lambda e: e['date'])
fed = sorted((e for e in EV if e['metric_id'] == 'DFEDTARU'), key=lambda e: e['date'])
assert len(ecb) == 2 and len(fed) == 2
ECB1, ECB2, FED1, FED2 = ecb[0], ecb[1], fed[0], fed[1]
assert [ECB2['from'], ECB2['to']] == [ECB1['to'], ECB1['to'] + 0.25]
assert not FR.ecb_calendar_records()
CAL = FR.cal
pol_entries = [e for e in CAL.get('entries') or []
               if e.get('kind') in ('policy_decision', 'policy_maintenance')]
assert {e.get('metric_id') for e in pol_entries} == {'JP_POLICY_TARGET'}
BOJ = max((e for e in pol_entries if e.get('kind') == 'policy_decision'
           and e.get('decision_date') <= AS_OF), key=lambda e: e['decision_date'])
BOJ_D, BOJ_E, BOJ_T = BOJ['decision_date'], BOJ['effective_on'], BOJ['target_value']
assert BOJ_E <= AS_OF
for e in EV:
    assert AS_OF >= e['effective_date']
ecb_last = FR.last_date('ECB_DFR')
ecb_lag = (D0 - datetime.date.fromisoformat(ecb_last)).days
mro_carry = FR.val('ECB_MRO', WIN0)
mro_last = FR.ss['ECB_MRO']['values'][-1]
dfr_carry = FR.val('ECB_DFR', WIN0)
dfr_last = FR.ss['ECB_DFR']['values'][-1]
# 起生效日=窗启时在值这一段连续取值的起点(自窗启日向前回溯到上一次变动之后)
_d_dfr, _v_dfr = FR.ss['ECB_DFR']['dates'], FR.ss['ECB_DFR']['values']
_i0 = max(i for i, d in enumerate(_d_dfr) if d <= WIN0)
assert _v_dfr[_i0] == dfr_carry
_i_prev = max(i for i in range(_i0) if _v_dfr[i] != dfr_carry)
dfr_carry_from = _d_dfr[_i_prev + 1]
assert all(v == dfr_carry for v in _v_dfr[_i_prev + 1:_i0 + 1])
CELLS = {c['metric_id']: c for c in FR.rep['research_plan']['point_values']['cells']}


def panel_net(mid):
    return (CELLS[mid].get('policy_window_path') or {}).get('net_bp')


assert panel_net('ECB_DFR') == 25 and round((dfr_last - dfr_carry) * 100) == 50
assert panel_net('ECB_MRO') == 25 and round((mro_last - mro_carry) * 100) == 50
assert panel_net('JP_POLICY_RATE') == net_dec == 67 and net_carry == 75
A1, A2 = CELLS['DFEDTARU']['anchors'], CELLS['DFF']['anchors']
ORDER = ['12个月前', '3个月前', '最新一期']
TA = [A1[k]['observation_date'] for k in ORDER]
TD = [A2[k]['observation_date'] for k in ORDER]
assert TA == ['2025-11-23', '2026-08-23', '2026-11-23'] and TD == ['2025-11-22', '2026-08-22', '2026-11-19']
# China anchor switch
omo_last = FR.last_date('CN_OMO_7D')
ovo = FR.ss['CN_POLICY_OVERNIGHT']
ovo_first, ovo_last = ovo['dates'][0], ovo['dates'][-1]
assert ovo_first == '2026-11-02' and ovo_last == AS_OF and len(set(ovo['values'])) == 1
ovo_val = ovo['values'][-1]
omo_val = FR.ss['CN_OMO_7D']['values'][-1]
assert len(set(FR.ss['CN_OMO_7D']['values'])) == 1
lpr_val = FR.val('CN_LPR_1Y', AS_OF)
assert FR.val('CN_LPR_1Y', WIN0) == lpr_val == 3.0
nl_last_ym = max(FR.monthly('CN_NEW_LOANS'))
# BEI_10Y points
BEI = 'BEI_10Y'
bei_d, bei_v = FR.ss[BEI]['dates'], FR.ss[BEI]['values']
TRIO = F['us_rates_trio']
W12, W1 = TRIO['window_12m'], TRIO['window']
bei_a, bei_b = FR.val(BEI, W12['from']), FR.val(BEI, W12['to'])
bei_12m_bp = TRIO['chg_bp_12m'][BEI]
assert round((bei_b - bei_a) * 100) == bei_12m_bp == -11
bei_last_d, bei_last = FR.date(BEI, AS_OF), FR.val(BEI, AS_OF)
pre = [(d, v) for d, v in zip(bei_d, bei_v) if '2026-02-01' <= d <= ECB1['date']]
bei_up_d0 = min(pre, key=lambda x: x[1])[0]
bei_up_d1 = max(pre, key=lambda x: x[1])[0]
assert bei_up_d0 < bei_up_d1
bei_up_v0, bei_up_v1 = dict(pre)[bei_up_d0], dict(pre)[bei_up_d1]
eve_day = (datetime.date.fromisoformat(ECB1['date'])
           - datetime.timedelta(days=1)).isoformat()        # last close before the decision
bei_eve_d, bei_eve = FR.date(BEI, eve_day), FR.val(BEI, eve_day)
assert bei_eve_d == eve_day
post = [(d, v) for d, v in zip(bei_d, bei_v) if ECB1['effective_date'] <= d <= AS_OF]
bei_post_min, bei_post_max = min(v for _d, v in post), max(v for _d, v in post)
# HY_OAS
hy_d, hy_v = FR.ss['HY_OAS']['dates'], FR.ss['HY_OAS']['values']
hy_last_d, hy_last = hy_d[-1], hy_v[-1]
hy_first = hy_d[0]
hy_max_d, hy_max = max(zip(hy_d, hy_v), key=lambda x: x[1])
hy3 = [(d, v) for d, v in zip(hy_d, hy_v)
       if d >= (datetime.date.fromisoformat(hy_last_d)
                - datetime.timedelta(days=3 * 365)).isoformat()]
hy_pct = int(round(100.0 * sum(1 for _d, v in hy3 if v < hy_last) / len(hy3)))
hy_since = max(d for d, v in zip(hy_d, hy_v) if d < hy_last_d and v >= hy_last)
hy_iso = [d for d in hy_d if datetime.date.fromisoformat(d).isocalendar()[:2]
          != datetime.date.fromisoformat(hy_last_d).isocalendar()[:2]][-1]
hy_ld = datetime.date.fromisoformat(hy_last_d)
hy_w = hy_last - FR.val('HY_OAS', hy_iso)
hy_7 = hy_last - FR.val('HY_OAS', (hy_ld - datetime.timedelta(days=7)).isoformat())
hy_12 = hy_last - FR.val('HY_OAS', (hy_ld - datetime.timedelta(days=365)).isoformat())
assert FR.date('HY_OAS', (hy_ld - datetime.timedelta(days=7)).isoformat()) == '2026-11-12'
# asset window (engine rows) + close caliber
AM = {r['metric_id']: r for r in F['asset_moves']['rows']}
W0 = AM['SPX']['window']['from']
assert all(r['window']['from'] == W0 for r in AM.values())
AB = L.asset_block(FR, W0)
FB = L.fx_block(FR, W0)
CLOSE = AB['close_day']
assert CLOSE < AS_OF and FR.last_date('SPX') == AS_OF
INTRA = [m for m in AM if FR.intraday(m)[0]]
assert {'SPX', 'DAX', 'VIX', 'GOLD_F', 'DXY'} <= set(INTRA)
assert not FR.intraday('SHCOMP')[0] and FR.last_date('SHCOMP') == AS_OF
assert FR.last_date('NIKKEI225') < AS_OF and not FR.intraday('NIKKEI225')[0]
for m in ('SPX', 'DAX'):
    assert abs(AB['equity'][m]['ret_now'] - AM[m]['chg_pct']) < 0.011, m
assert abs(AB['equity']['NIKKEI225']['ret'] - AM['NIKKEI225']['chg_pct']) < 0.011
vix0, vix1 = FR.val('VIX', W0), FR.val('VIX', AS_OF)
assert abs((vix1 / vix0 - 1) * 100 - AM['VIX']['chg_pct']) < 0.011
# gate A
GA = FR.snap.get('gate_a') or {}
ncm = list(GA.get('noncore_missing') or [])
ncd = list(GA.get('noncore_degraded') or [])
ncm_have = [m for m in ncm if (FR.ss.get(m) or {}).get('dates')]
assert GA.get('status') == 'DEGRADED' and not GA.get('core_missing')
assert len(ncm) == 7 and len(ncd) == 8 and len(ncm_have) == 5
NCM_NAME = {'CN_OMO_7D': ('CN', '7天逆回购利率'), 'CN_POLICY_OVERNIGHT': ('CN', '隔夜逆回购利率'),
            'EA_REAL_GDP_YOY': ('EA', '实际GDP同比'), 'JP_REAL_GDP_YOY': ('JP', '实际GDP同比'),
            'JP_CPI_TOKYO_YOY': ('JP', '东京CPI')}                  # cited under display names
assert set(ncm_have) == set(NCM_NAME)
for _m in ncm_have:                                   # ...and each is cited in its region row
    _reg, _name = NCM_NAME[_m]
    assert _name in rm['regions'][_reg]['from_to'], _m

# ── headline ────────────────────────────────────────────────────────────
H = rm['headline_conclusion']
H = rep(H, '决议2026-06-11生效2026-06-17、决议2026-09-10生效2026-09-16)、',
        '决议%s生效%s、决议%s生效%s；决议日系引擎回推【推断】)、'
        % (ECB1['date'], ECB1['effective_date'], ECB2['date'], ECB2['effective_date']))
H = rep(H, ',中国按兵不动(背离);',
        ',中国未跟进加息(7天逆回购利率与LPR窗内无变动；%s起政策利率锚切换为隔夜逆回购利率)(背离);' % ovo_first)
H = rep(H, '风险资产收缩(标普500指数下跌5.51%、VIX升38.87%),',
        '风险资产收缩(标普500指数下跌%s%%、VIX升%s%%，均为%s盘中快照、非收盘价),'
        % (L.f2(-AM['SPX']['chg_pct']), L.f2(AM['VIX']['chg_pct']), AS_OF))
rm['headline_conclusion'] = H

# ── regions ─────────────────────────────────────────────────────────────
RG = rm['regions']
RG['US']['from_to'] = rep(
    RG['US']['from_to'],
    '核心PCE同比 2.85→3.04→3.12(观测 2025-08→2026-06→2026-09)逐点走高。',
    '核心PCE同比 2.85→3.04→3.12(观测 2025-08→2026-06→2026-09)三点走高，'
    '月度同比自%s高点%s回落后部分回升(%s %s → %s %s)，未再越过高点。'
    % (cp_hi_ym, L.f2(cp_win[cp_hi_ym]), cp_lo_ym, L.f2(cp_win[cp_lo_ym]),
       cp_last_ym, L.f2(cp_win[cp_last_ym])))
RG['US']['from_to'] = rep(
    RG['US']['from_to'], '全年净变0而方向由宽松转回收紧(决议日=生效日前一日,引擎政策面按惯例推定)。',
    '窗内净变0(窗内一降一升各25个基点)而方向由宽松转回收紧(决议日=生效日前一日,引擎政策面按惯例推定)。'
    '渲染注记: 引擎点值面 DFEDTARU 行的日期为锚日(该序列按日历日填充: %s)，'
    '同区 DFF 行为实际观测日(%s)，两行日期相差数日属渲染口径、非数据冲突。'
    % ('/'.join(TA), '/'.join(TD)))

RG['CN']['from_to'] = rep(
    RG['CN']['from_to'],
    ';序列2026年春季一度回升至荣枯线上方、至2026-07观测回落至49.2(月度序列事实,幅度温和,未构成趋势性转折)。',
    ';序列于 %s 共%s个月站上荣枯线(%s)%s，其余月份落在 %s–%s 之间(月度序列事实,幅度温和,未构成趋势性转折)。'
    % ('、'.join(pm_above), cn_count(len(pm_above)),
       '/'.join(L.n(pm_win[ym]) for ym in pm_above),
       ('，%s 持平于 %s' % ('、'.join(pm_flat), L.n(pm_win[pm_flat[0]]))) if pm_flat else '',
       L.n(min(pm_win[ym] for ym in pm_below)), L.n(max(pm_win[ym] for ym in pm_below))))
RG['CN']['from_to'] = rep(
    RG['CN']['from_to'],
    '如实显示)全年无变动;LPR_1Y 3.0→3.0→3.0(观测 2025-11→2026-08→2026-11)持平;',
    '如实显示)窗内无变动;LPR_1Y 3.0→3.0→3.0(观测 2025-11→2026-08→2026-11)窗内持平;')
RG['CN']['from_to'] = rep(
    RG['CN']['from_to'],
    '最新 1.25@2026-11-23——政策利率全年按兵不动,与美欧日的收紧方向背离。',
    '最新 %s@%s(换锚后持平于首个观测值)——换锚后原工具无新观测，『政策利率全年不变』对现行锚不可核；'
    '可陈述的是中国未跟进加息(7天逆回购利率与LPR窗内无变动)，与美欧日的收紧方向背离。'
    % (L.n(ovo_val), ovo_last))

RG['EA']['from_to'] = rep(
    RG['EA']['from_to'],
    '两段上行(2026-03至05与2026-08至10),最新4.0为四地最高通胀读数之一。',
    '自%s低点%s连续上行至%s的%s(2026-03起加速)，%s回落至%s后自2026-07再度上行(2026-08至10加速)，最新%s为四地最高通胀读数之一。'
    % (ea_lo_ym, L.n(ea_win[ea_lo_ym]), ea_hi1, L.n(ea_win[ea_hi1]), ea_06,
       L.n(ea_win[ea_06]), L.n(ea_win[ea_last_ym])))
RG['EA']['from_to'] = rep(
    RG['EA']['from_to'],
    '决议2026-09-10生效2026-09-16(+25个基点),政策方向由中性转收紧(决议日/生效日引擎面在册)。',
    '决议%s生效%s(+25个基点；存款便利利率 %s→%s，主要再融资利率 %s→%s)，政策方向由中性转收紧'
    '(生效日=序列变更日；决议日系引擎按『生效日前上一个周四』惯例自变更日回推【推断】，冻结发布日历无欧央行实录条目)。'
    '口径注记: 引擎『政策一年窗路径』面板按窗内首观测→窗末观测计净变动，显示净 +25bp(%s→%s)，'
    '漏计窗启时在值至首个窗内观测的升幅；按『窗启时在值→窗末观测』口径，窗内净变动为 +50bp'
    '(窗启时在值 %s，%s 起生效)，与两次生效各 +25bp 之和一致；欧央行两条利率序列止于 %s(滞后%s天)。'
    % (ECB2['date'], ECB2['effective_date'], L.n(dfr_carry), L.n(dfr_last),
       L.n(mro_carry), L.n(mro_last), L.n(ECB1['to']), L.n(ECB2['to']),
       L.n(dfr_carry), dfr_carry_from, ecb_last, ecb_lag))

JP_STEP_OLD = ('(窗内净+67个基点;月度步进 +17/+11/+14/+7/+18个基点,另有两个月各约零点一个基点的舍入变动)')
JP_STEP_NEW = ('(窗内净 +%d 个基点；月度步进 %s 个基点，分别落在 %s，另有 %s 各约零点一个基点的舍入变动；'
               '自 %s 月均 %s 起为 +%d 个基点，引擎『政策一年窗路径』面板按窗内首观测起算、显示 +%dbp)'
               % (net_carry, '/'.join('+%d' % v for _ym, v in sig), '、'.join(ym for ym, _v in sig),
                  ' 与 '.join(noise), jp_first_in, L.n(JP[jp_first_in]), net_dec, panel_net('JP_POLICY_RATE')))
JP_FROM_OLD_A = 'JP_POLICY_RATE 月均自2025-12的0.557步进升至2026-10的1.227'
JP_FROM_NEW_A = 'JP_POLICY_RATE 月均自 %s 的 %s(窗启时在值)步进升至 %s 的 %s' % (
    jp_carry_ym, L.n(jp_carry), jp_last_ym, L.n(jp_last))
RG['JP']['from_to'] = rep(
    RG['JP']['from_to'],
    '窗内自2025-12月均0.557升至2026-10月均1.227净+67个基点',
    '窗内自 %s 月均 %s(窗启时在值)升至 %s 月均 %s 净 +%d 个基点(自 2025-12 月均 0.557 起 +67bp；'
    '引擎『政策一年窗路径』面板按窗内首观测起算，显示净 +67bp)'
    % (jp_carry_ym, L.n(jp_carry), jp_last_ym, L.n(jp_last), net_carry))

# ── transmission ────────────────────────────────────────────────────────
TR = rm['transmission']
T00, T01, T02 = TR[0]['links']
T10 = TR[1]['links'][0]
assert len(TR[0]['links']) == 3 and len(TR[1]['links']) == 1
CP_AFTER_TXT = ('此后美国核心PCE同比自 %s 高点 %s 回落后部分回升(%s %s → %s %s，未再越过高点)'
               % (cp_hi_ym, L.f2(cp_win[cp_hi_ym]), cp_lo_ym, L.f2(cp_win[cp_lo_ym]),
                  cp_last_ym, L.f2(cp_win[cp_last_ym])))
assert [L.f2(br[k]) for k in (br_02, br_03, br_05)] == ['72.48', '118.35', '92.05']
T00['observed_fact'] = rep(
    T00['observed_fact'],
    '此后美国CORE_PCE同比至2026-09续升至3.12、欧元区HICP至2026-10续升至4.0、中国PPI至2026-10续升至5.7(三地同窗共振,月频分辨率下先后未定)。',
    '%s、欧元区HICP %s回落至 %s 后升至 %s@%s、中国PPI %s回落至 %s 后升至 %s@%s(三地同窗共振,月频分辨率下先后未定)。'
    '同窗供给侧读数: 布伦特原油(BRENT_F)月末 %s %s→%s %s→%s %s(首尾 %s；%s 冲至 %s)，美国核心CPI同比 %s %s→%s %s。'
    % (CP_AFTER_TXT, ea_06, L.n(ea_win[ea_06]), L.n(ea_win[ea_last_ym]), ea_last_ym,
       pp_lo_ym, L.n(pp_win[pp_lo_ym]), L.n(pp_win[pp_last_ym]), pp_last_ym,
       br_02, L.f2(br[br_02]), br_03, L.f2(br[br_03]), br_05, L.f2(br[br_05]),
       L.sgn2(br_chg), br_hi[5:], L.f2(br[br_hi]), br_02, L.f2(cc[br_02]), br_05, L.f2(cc[br_05])))
T00['causal_hypothesis'] = rep(
    T00['causal_hypothesis'], '当日实时快照、非收盘价;', '当日盘中快照、非收盘价；')
T00['causal_hypothesis'] = rep(
    T00['causal_hypothesis'], '通胀同窗内冲高后回落,当月至今-25.03%)',
    '通胀同窗内冲高后回落，首尾 %s，当月至今-25.03%%)' % L.sgn2(br_chg))
T00['causal_hypothesis'] = rep(
    T00['causal_hypothesis'], '该归因环不可由本引擎直接验证,证据级E3。',
    '该归因环不可由本引擎直接验证,证据级E3。对质注记: 主解释预期『同窗显著上行』——月末口径 %s %s→%s %s(首尾 %s)相容；'
    '竞争解释预期『大体持平而核心CPI独立走高』——核心CPI同比同窗 %s→%s 亦相容，且布伦特 %s 冲至 %s 后于 %s 回落至首月末附近(未持平)'
    '——两侧各有相容观测，尚不能区分。'
    % (br_02, L.f2(br[br_02]), br_05, L.f2(br[br_05]), L.sgn2(br_chg),
       L.f2(cc[br_02]), L.f2(cc[br_05]), br_hi[5:], L.f2(br[br_hi]), br_05[5:]))

# policy link: China wording + visible-CPI disclosure at decision time
T01['observed_fact'] = rep(
    T01['observed_fact'], '中国央行未跟进(全年无变动)。',
    '中国央行未跟进加息(7天逆回购利率与 LPR 窗内无变动；%s 起政策利率锚切换为隔夜逆回购利率，换锚后原工具无新观测)。'
    % ovo_first)
vis_rows = []
for tag, day in (('欧央行', ECB1['date']), ('欧央行', ECB2['date']), ('美联储', FED2['date']),
                 ('日本央行', BOJ_D)):
    obs, pub = visible('CPI', day)
    assert '推定' in pub[1] and cy[obs[0]] < cy[cy_hi_ym]
    assert RULE[obs[0]] == pub[0]
    vis_rows.append((day, tag, obs[0], pub[0]))
assert cy_pub[cy_hi_ym][0] == RULE[cy_hi_ym]
groups = {}
for day, tag, ym, pub in vis_rows:
    groups.setdefault((ym, pub), []).append((day, tag))
assert list(groups) == [('2026-04', cy_pub['2026-04'][0]), ('2026-07', cy_pub['2026-07'][0]),
                        ('2026-08', cy_pub['2026-08'][0])]


def dec(day, tag):
    return '%s %s%s' % (tag, day, ('(生效 %s)' % BOJ_E) if tag == '日本央行' else '')


vis_txt = '；'.join('%s 决议前最近可见为 %s 观测(%s，推定发布 %s)'
                   % (' 与 '.join(dec(d, t) for d, t in who), ym, L.f2(cy[ym]), pub)
                   for (ym, pub), who in groups.items())
# 最新可见观测(决议之后发布): 同比再度回升但未越过高点——与"决议前已回落"一并披露
cy_last_ym = max(ym for ym in cy_win if cy[ym] is not None)
_vis_last = visible('CPI', AS_OF)
assert cy_last_ym == '2026-09' and _vis_last[0][0] == '2026-10' and _vis_last[1][0] <= AS_OF   # 最新可见观测=2026-10(指数),同比不可得
assert cy[cy_last_ym] > cy['2026-08'] and cy[cy_last_ym] < cy[cy_hi_ym]
assert yoy('CPI', '2026-10') is None
CY_AFTER_TXT = '决议后发布的 %s 观测回升至 %s(仍低于高点 %s；2026-10 同比缺基期不可得)。' % (
    cy_last_ym, L.f2(cy[cy_last_ym]), L.f2(cy[cy_hi_ym]))
T01['observed_fact'] += (('决议时点前按引擎发布规则已可见的美国 CPI 同比: %s；2026-05 高点 %s(推定发布 %s)。'
                          + CY_AFTER_TXT +
                          '欧央行决议日系引擎按『生效日前上一个周四』惯例自生效日回推【推断】，冻结发布日历无欧央行实录条目。')
                         % (vis_txt, L.f2(cy[cy_hi_ym]), cy_pub[cy_hi_ym][0]))
T01_OLD = ('【假设】央行因通胀再加速而收紧——时序上政策变动月(2026-06起)在通胀转折月(至2026-05)之后=时序事实,'
           '但动机归因不可由数据验证,证据级E3;市场层面 BEI_10Y 12个月回落11个基点、水平2.15@2026-11-20,'
           '说明市场并未为持续性通胀定价,政策收紧与市场通胀预期存在方向分歧。')
T01['causal_hypothesis'] = rep(
    T01['causal_hypothesis'], T01_OLD,
    '【假设】央行因通胀再加速而收紧——时序上政策变动月(2026-06起)在通胀转折月(至2026-05)之后=时序事实,'
    '但动机归因不可由数据验证,证据级E3；且决议时点前已可见的美国 CPI 同比已自高点回落(见观察事实)，动机环证据减弱。'
    '市场层面 BEI_10Y 12个月(共同交易日 %s→%s)回落 %d 个基点(%s→%s)、最新 %s@%s，说明市场并未为持续性通胀持续定价；'
    '但收紧前(%s→%s)BEI_10Y 自 %s 升至 %s，与主解释相容。'
    '对质注记: 收紧前上行段合主解释(市场与央行同向定价通胀)；首次加息决议前日 %s 已回落至 %s，'
    '收紧后(%s 起)区间 %s–%s，近一个月(%s→%s，%d 个日历日)自 %s 回落至 %s，合竞争解释(政策续紧而 BEI_10Y 不升)'
    '——窗口内方向前后相反，尚不能区分。'
    % (W12['from'], W12['to'], abs(bei_12m_bp), L.f2(bei_a), L.f2(bei_b), L.f2(bei_last), bei_last_d,
       bei_up_d0, bei_up_d1, L.f2(bei_up_v0), L.f2(bei_up_v1), bei_eve_d, L.f2(bei_eve),
       ECB1['effective_date'], L.f2(bei_post_min), L.f2(bei_post_max),
       FR.date(BEI, W0), bei_last_d,
       (datetime.date.fromisoformat(bei_last_d) - datetime.date.fromisoformat(FR.date(BEI, W0))).days,
       L.f2(FR.val(BEI, W0)), L.f2(bei_last)))
assert T01['face_off_verdict'] == '支持竞争解释'
T01['face_off_verdict'] = '尚不能区分'

T02['observed_fact'] = rep(
    T02['observed_fact'],
    'VIX 自19.45升至27.01(+38.87%;11-23 值为当日实时快照(非收盘价));HY_OAS 水平3.52pp@2026-11-19仍温和(近1周走阔0.29pp,非信用事件级)。',
    'VIX 自%s升至%s(+%s%%);口径: 标普500指数、DAX、GOLD_F、DXY、VIX 止于 %s 盘中快照(截止时点美股与德法股指常规时段进行中，非收盘价)，'
    'SHCOMP 为 %s 收盘，NIKKEI225 止于 %s 收盘；同日收盘口径(%s→%s): 标普500指数 %s、DAX %s、CAC40 %s、NIKKEI225 %s、VIX %s。'
    'HY_OAS 水平 %spp@%s: 低于引擎序列(自 %s 起)高点 %s 的 %s，但处约第 %d 百分位、为 %s 以来最高；'
    '近 1 周走阔 %spp(ISO 周口径，基准 %s；严格 7 日口径 +%spp)、近 12 个月走阔 %spp——属非信用事件级，但相对自身三年历史并不温和。'
    % (L.n(vix0), L.n(vix1), L.f2(AM['VIX']['chg_pct']), AS_OF, AS_OF, FR.last_date('NIKKEI225'),
       W0, CLOSE, L.sgn2(AB['equity']['SPX']['ret']), L.sgn2(AB['equity']['DAX']['ret']),
       L.sgn2(AB['equity']['CAC40']['ret']), L.sgn2(AB['equity']['NIKKEI225']['ret']),
       L.sgn2(AB['vix_month_close']), L.f2(hy_last), hy_last_d, hy_first, hy_max_d, L.f2(hy_max),
       hy_pct, hy_since, L.f2(hy_w), hy_iso, L.f2(hy_7), L.f2(hy_12)))
T02['causal_hypothesis'] += (
    ' 对质注记: 近 1 个月(共同交易日 %s→%s)TIPS_10Y %sbp(合主解释『实际利率续升』)、BEI_10Y %sbp'
    '(合竞争解释『盈亏平衡下行』)；HY_OAS 近 1 周走阔但未破前高(两侧各有相容观测)——尚不能区分。'
    % (W1['from'], W1['to'], bp(TRIO['chg_bp']['TIPS_10Y']), bp(TRIO['chg_bp'][BEI])))
T02['competing_explanation'] = rep(
    T02['competing_explanation'], 'HY_OAS 温和。', 'HY_OAS 保持非信用事件级(不升破序列高点)。')
T02['main_predicts'] = rep(
    T02['main_predicts'], 'HY_OAS 温和', 'HY_OAS 不升破序列高点(非信用事件级)')
T10['observed_fact'] = rep(
    T10['observed_fact'], '(当日实时快照、非收盘价)', '(%s 盘中快照、非收盘价)' % AS_OF)

T10['observed_fact'] = rep(
    T10['observed_fact'], JP_FROM_OLD_A + JP_STEP_OLD, JP_FROM_NEW_A + JP_STEP_NEW)
ux = FB['fx']['USDJPY']
T10['causal_hypothesis'] += (
    ' 对质注记: 同窗(%s→%s，盘中快照口径)主解释预期『风险资产收缩与日元走强同现』未获支持——SPX %s 而 USDJPY 未走低(%s→%s，%s)，'
    '套息平仓渠道的分量应下调；竞争解释所需的『时间上解耦』须以逐日共动面核验，本档未做——尚不能区分。'
    % (W0, AS_OF, L.sgn2(AM['SPX']['chg_pct']), L.f2(ux['from']), L.f2(ux['now']), L.sgn2(ux['ret_now'])))

# ── L3 contradictions ───────────────────────────────────────────────────
C0, C1, C2 = P['l3']['contradictions']
assert [C0['id'], C1['id'], C2['id']] == ['C1', 'C2', 'C3']
C0['statement'] = rep(
    C0['statement'], 'CPI 与 CORE_PCE 同比走高、',
    'CPI 与 CORE_PCE 同比较一年前走高(2026-05 见顶后回落、未再越过高点)、')
C0['statement'] = rep(
    C0['statement'], 'CN_PMI_MFG 于2026年春季一度回升至荣枯线上方后回落至线下、',
    'CN_PMI_MFG 于 %s 及 %s 共%s个月站上荣枯线、其余月份不高于荣枯线(%s)、'
    % ('、'.join(ym for ym in pm_above if ym.startswith('2025')),
       '、'.join(ym for ym in pm_above if ym.startswith('2026')), cn_count(len(pm_above)),
       PM_REST_TXT))
C0['statement'] = rep(
    C0['statement'], 'CN_PMI_MFG 水平为 49.3。',
    'CN_PMI_MFG 水平为 49.3。其中 VIX 与 USDJPY 为 %s 盘中快照(非收盘价)。'
    '数据面披露: 本轮 Gate A 判 DEGRADED——核心缺口%s项、非核心缺口%s项、非核心降级%s项，'
    '缺口指标中有%s项在序列库内仍有存量观测并被本档按存量观测引用(属采集步骤降级口径，逐项见质量注记)。'
    % (AS_OF, cn_count(len(GA.get('core_missing') or [])), cn_count(len(ncm)),
       cn_count(len(ncd)), cn_count(len(ncm_have))))
if len(sys.argv) > 5:
    _S = json.load(open(sys.argv[5], encoding='utf-8'))
    _ex = {h['anchor_ym']: h['ex_post'] for h in _S['history_periods']}
    _m = re.search(r'SHCOMP ([+\-][0-9.]+)%', _ex['2023-10']['3m'])
    assert _m and _m.group(1).startswith('-'), _m
C1['statement'] = rep(
    C1['statement'], '2025-03、2023-10段风险资产与 GOLD_F 各窗普遍走强而 DXY 走弱',
    '2025-03、2023-10段风险资产与 GOLD_F 多数窗走强(2023-10段上证指数三个月窗为负，属例外)而 DXY 走弱')
AGR = F['analog']['dispersion']['topN_aftermath_sign_agreement']
AGR_FAMILIES = sorted({k.rsplit('_', 1)[0] for k in AGR})
agr_full = sorted({k.rsplit('_', 1)[0] for k, v in AGR.items()
                   if v == 1.0 and k.endswith(('_6m', '_12m'))})
agr_rest = [v for k, v in AGR.items() if k.rsplit('_', 1)[0] not in agr_full]
assert AGR_FAMILIES == ['DXY', 'GOLD_F', 'SPX', 'UST_10Y'] and agr_full == ['GOLD_F', 'SPX']
assert (min(agr_rest), max(agr_rest)) == (0.6, 0.8)
AGR_TXT = ('%s 六个月与十二个月窗符号一致(一致率面仅含 %s 四类)，其余各窗%s至%s'
           % (' 与 '.join(agr_full), '、'.join(AGR_FAMILIES), cn_dec(min(agr_rest)), cn_dec(max(agr_rest))))
C1['statement'] = rep(
    C1['statement'], 'TOP-N事后符号一致率: 股指六个月、十二个月窗满一致,其余各窗零点六至一点零。',
    'TOP-N事后符号一致率: %s。' % AGR_TXT)
C1['statement'] = rep(
    C1['statement'], '分歧出现=结论降级为描述性)。',
    '分歧出现=结论降级为描述性)。所附四项引用为四项资产的当前水平锚点(供对照，不承载历史段数字)；'
    '历史段事后数字取自相似检索面事后块，按自然月末口径，事后结果≠预测。')
C2['statement'] = rep(
    C2['statement'],
    '而 CN_LPR_1Y 全年持平、政策利率锚于2026-11-02切换为隔夜利率工具,即生产价格大幅上行而政策利率不动。',
    '而 CN_LPR_1Y 与 7天逆回购利率窗内持平、政策利率锚于%s切换为隔夜利率工具后新锚持平于其首个观测水平,'
    '即生产价格大幅上行而政策利率未上调。' % ovo_first)
C2['statement'] = rep(
    C2['statement'], '引擎面无中国利率预期序列与信贷/内需序列,三种解释不可区分,标注【尚未验证】。',
    '引擎面无中国利率预期序列;信贷/内需侧仅有 CN_NEW_LOANS(月频，最新观测月 %s)等少量事实，'
    '不足以在三种解释间裁决,三种解释不可区分,标注【尚未验证】。' % nl_last_ym)

# ── L3 mechanism chains ─────────────────────────────────────────────────
M0 = P['l3']['mechanism_chains'][0]['links']
M1 = P['l3']['mechanism_chains'][1]['links']
assert len(M0) == 4 and len(M1) == 2
M0[0]['text'] = rep(
    M0[0]['text'],
    '此后美国 CORE_PCE 同比续升至3.12@2026-09、EA_HICP_YOY 续升至4.0@2026-10、CN_PPI_YOY 续升至5.7@2026-10。',
    '此后至最新观测月: 美国 CORE_PCE 同比自 %s 高点 %s 回落后部分回升(%s %s → %s %s，未再越过高点)、'
    'EA_HICP_YOY %s回落至 %s 后升至 %s@%s、CN_PPI_YOY %s回落至 %s 后升至 %s@%s。'
    % (cp_hi_ym, L.f2(cp_win[cp_hi_ym]), cp_lo_ym, L.f2(cp_win[cp_lo_ym]), cp_last_ym,
       L.f2(cp_win[cp_last_ym]), ea_06, L.n(ea_win[ea_06]), L.n(ea_win[ea_last_ym]), ea_last_ym,
       pp_lo_ym, L.n(pp_win[pp_lo_ym]), L.n(pp_win[pp_last_ym]), pp_last_ym))
M0[1]['text'] = rep(
    M0[1]['text'], 'ECB 决议2026-06-11生效2026-06-17、决议2026-09-10生效2026-09-16;',
    'ECB 决议%s生效%s、决议%s生效%s(决议日系引擎回推【推断】);'
    % (ECB1['date'], ECB1['effective_date'], ECB2['date'], ECB2['effective_date']))
sep_groups = [(ym, who) for (ym, _p), who in groups.items() if who[0][0] >= '2026-09-01']
jun_groups = [(ym, who) for (ym, _p), who in groups.items() if who[0][0] < '2026-09-01']
assert len(sep_groups) == 2 and len(jun_groups) == 1
assert sum(len(w) for _y, w in sep_groups) == 3                      # three September decisions
sep_txt = '；'.join('%s 决议前最近可见 %s 观测 %s'
                    % (' 与 '.join(dec(d, t) for d, t in who), ym, L.f2(cy[ym]))
                    for ym, who in sep_groups)
jun_ym, jun_who = jun_groups[0]
assert jun_ym == '2026-04' and cy['2026-04'] > cy['2026-03']       # still on the rising leg
M0[1]['text'] = rep(
    M0[1]['text'], '动机环被证伪)。',
    '动机环被证伪)。须披露: 按引擎发布规则，2026-09 三次收紧决议时点前已可见的美国 CPI 同比已自 2026-05 高点 %s 回落'
    '(%s)，%s 决议前最近可见 %s 观测 %s 仍处上行段'
    '——『因通胀续升而收紧』与 9 月决议前的可见数据不完全吻合，动机环证据减弱(仍不可验证)。'
    % (L.f2(cy[cy_hi_ym]), sep_txt,
       ' 与 '.join(dec(d, t) for d, t in jun_who), jun_ym, L.f2(cy[jun_ym])))
M0[1]['text'] = rep(M0[1]['text'], '动机环证据减弱(仍不可验证)。',
                    '动机环证据减弱(仍不可验证)。' + CY_AFTER_TXT)
M0[2]['text'] = rep(
    M0[2]['text'], 'BEI_10Y 2.16@2026-11-19(共同交易日)',
    'BEI_10Y %s@2026-11-19(共同交易日；最新 %s@%s)' % (L.f2(bei_b), L.f2(bei_last), bei_last_d))
M0[3]['text'] = rep(
    M0[3]['text'], 'VIX 19.45→27.01(11-23 值为当日实时快照(非收盘价))',
    'VIX %s→%s(其中 SPX、GOLD_F、DXY、VIX 为 %s 盘中快照、非收盘价；同日收盘口径 %s→%s 标普500指数 %s、VIX %s)'
    % (L.n(vix0), L.n(vix1), AS_OF, W0, CLOSE, L.sgn2(AB['equity']['SPX']['ret']), L.sgn2(AB['vix_month_close'])))
M0[3]['text'] = rep(
    M0[3]['text'], '若为利率驱动,HY_OAS 应保持温和(非信用驱动),证伪观察=HY_OAS 快速走阔至危机水平。',
    '若为利率驱动，HY_OAS 应保持非信用事件级(当前 %spp，低于 %s 序列高点 %s，但处引擎三年历史约第 %d 百分位)，'
    '证伪观察=HY_OAS 升破 %s 的序列高点(量化阈值，【假设】的可观察形态)。'
    % (L.f2(hy_last), hy_max_d, L.f2(hy_max), hy_pct, L.f2(hy_max)))
M1[0]['text'] = rep(
    M1[0]['text'],
    'JP_POLICY_RATE(无担保隔夜拆借月均)自2025-12月均0.557步进升至2026-10月均1.227' + JP_STEP_OLD,
    'JP_POLICY_RATE(无担保隔夜拆借月均)自 %s 月均 %s(窗启时在值)步进升至 %s 月均 %s' % (
        jp_carry_ym, L.n(jp_carry), jp_last_ym, L.n(jp_last)) + JP_STEP_NEW)
M1[0]['text'] = rep(
    M1[0]['text'], '(当日实时快照、非收盘价)', '(%s 盘中快照、非收盘价)' % AS_OF)

# ── turnings / supplement / history ─────────────────────────────────────
TU = rm['turnings']
K1, K2 = 'CPI@2026-05', 'JP_CPI_YOY@2026-02'
TU[K1]['first_mover'] = rep(
    TU[K1]['first_mover'], '(2026-03起三地序列同月转向)',
    '(2026-02 起三地同向上行、2026-03 同月大幅跳升；低点月并不完全一致——美国 CPI 同比与欧元区 HICP 低点均在 %s、'
    '中国 PPI 低点在 %s 且此后连升)' % (cy_trough_ym, pp_trough_ym))
assert cy_trough_ym == ea_lo_ym == '2026-01'
TU[K1]['first_mover'] = rep(
    TU[K1]['first_mover'], '日本节奏背离: 先回落(',
    '日本节奏背离(另计为第三转折，方向相反，不计入本转折的上行共振): 先回落(')
TU[K1]['follow_or_diverge'] = rep(
    TU[K1]['follow_or_diverge'],
    '与2026-09-10(生效2026-09-16)两次加息、',
    '与%s(生效%s)两次加息(决议日系引擎回推【推断】)、' % (ECB2['date'], ECB2['effective_date']))
TU[K1]['follow_or_diverge'] = rep(
    TU[K1]['follow_or_diverge'], '中国未跟进(7天逆回购与LPR全年无变动)',
    '中国未跟进(7天逆回购与 LPR 窗内无变动，%s 起政策利率锚切换为隔夜逆回购)' % ovo_first)
TU[K2]['first_mover'] = rep(
    TU[K2]['first_mover'],
    '——这是12个月窗内最早的通胀转折:日本下行起点(2025-11)早于美欧中上行共振起点(2026-02),起点先后可判(日本先变、方向向下);'
    '但日本回落完成月(2026-02)恰为美欧中共振起点月,衔接处的精确先后在月频分辨率下未定。',
    '——日本全国CPI同比的下行段早于本窗即已开始(自 %s 高点 %s 至 %s 低点 %s 总体下行，其间 %s 小幅回升)，'
    '窗内自 2025-11 的 %s 起只是该下行段的尾段: '
    '『日本下行起点(2025-11)早于美欧中上行共振起点(2026-02)』属窗口边缘效应，不足以支撑日本先变的实质先后主张；'
    '可陈述的仅为窗内两段在时间上先后相接，且日本回落完成月(2026-02)恰为美欧中共振起点月，'
    '衔接处的精确先后在月频分辨率下先后未定。'
    % (jpc_hi_ym, L.n(j25[jpc_hi_ym]), jpc_lo_ym, L.n(j25[jpc_lo_ym]), '、'.join(jpc_up), L.n(jpc_11)))
TU[K2]['follow_or_diverge'] = rep(
    TU[K2]['follow_or_diverge'],
    '隔夜利率月均自2025-12的0.557步进升至2026-10的1.227(净+67个基点)',
    '隔夜利率月均自 %s 的 %s(窗启时在值)步进升至 2026-10 的 %s(净 +%d 个基点；自 2025-12 的 %s 起为 +%d 个基点)'
    % (jp_carry_ym, L.n(jp_carry), L.n(jp_last), net_carry, L.n(JP[jp_first_in]), net_dec))
TU[K2]['follow_or_diverge'] = rep(
    TU[K2]['follow_or_diverge'], '目标水平1.25%)', '目标水平 %s)' % L.n(BOJ_T))
TU[K2]['follow_or_diverge'] = rep(
    TU[K2]['follow_or_diverge'], '决议2026-09-10/生效09-16各+25个基点)',
    '决议%s/生效%s各+25个基点，决议日系引擎回推【推断】)'
    % (ECB2['date'], ECB2['effective_date'][5:]))
TU[K2]['follow_or_diverge'] = rep(
    TU[K2]['follow_or_diverge'],
    '背离者=中国(7天逆回购1.4与LPR 3.0全年无变动,2026-11-02起政策利率锚切换为隔夜逆回购,最新1.25@2026-11-23)。',
    '背离者=中国(7天逆回购 %s 与 LPR %s 窗内无变动，%s 起政策利率锚切换为隔夜逆回购，最新 %s@%s——未跟进加息)。'
    % (L.n(omo_val), L.n(lpr_val), ovo_first, L.n(ovo_val), ovo_last))
SUP = rm['turning_supplement']['JP_CPI_TOKYO_YOY@2026-09']
SUP['follow_or_diverge'] = rep(
    SUP['follow_or_diverge'], '(决议日粒度 ECB 09-10 早于 BOJ 09-18,先后可判)',
    '(决议日粒度 ECB 09-10 早于 BOJ 09-18,先后可判；欧央行决议日系引擎回推【推断】)')

# ── operator text review after the first rebuilt pass ────────────────────
# 日本通胀"回升时点晚于美欧"的说法与序列不符: 全国口径低点(2026-02)与美欧共振起点同月，
# 持续回升自 2026-05 起、恰与美欧同比自高点回落重叠；"滞后约一个季度"只对东京口径成立。
tk = FR.monthly('JP_CPI_TOKYO_YOY')
tk_lo_ym = min((ym for ym in tk if '2026-01' <= ym <= '2026-09'), key=tk.get)
assert tk_lo_ym == '2026-05'
_tk_up = sorted(y for y in tk if y >= tk_lo_ym)
assert all(tk[b] > tk[a] for a, b in zip(_tk_up, _tk_up[1:]))
jp_lo_ym = min((ym for ym in jpc if '2025-11' <= ym <= '2026-10'), key=jpc.get)
assert jp_lo_ym == '2026-02' == jpc_lo_ym
assert jpc['2026-03'] > jpc['2026-02'] and jpc['2026-04'] < jpc['2026-03']
assert all(jpc[b] > jpc[a] for a, b in zip(['2026-05', '2026-06', '2026-07', '2026-08', '2026-09'],
                                           ['2026-06', '2026-07', '2026-08', '2026-09', '2026-10']))
assert cy['2026-06'] < cy['2026-05'] and ea['2026-06'] < ea['2026-05']      # 美欧同比自 2026-05 高点回落
TU[K2]['first_mover'] = rep(
    TU[K2]['first_mover'], '——日本全国CPI同比的下行段早于本窗即已开始(',
    '——日本全国CPI同比的下行段在本窗开启前即已开始(')
TU[K2]['follow_or_diverge'] = rep(
    TU[K2]['follow_or_diverge'], ',回升时点晚于美欧共振窗(至2026-05)。',
    '(全国口径 2026-03 小幅回升至 %s、2026-04 回落至 %s，持续回升自 2026-05 起——与美欧同比自 2026-05 高点回落重叠、方向相反)。'
    % (L.n(jpc['2026-03']), L.n(jpc['2026-04'])))
TU[K2]['follow_or_diverge'] = rep(
    TU[K2]['follow_or_diverge'], '回补2025-12-11生效的降息,全年净0)', '回补2025-12-11生效的降息,窗内净0)')
TU[K1]['follow_or_diverge'] = rep(
    TU[K1]['follow_or_diverge'], '后同向(回升段,时点晚于美欧)', '后同向(回升段，自 2026-02 低点起)')
SUP['first_mover'] = rep(
    SUP['first_mover'], '相对美欧中共振窗(2026-02→2026-05),日本回升段晚约3个月(滞后同向)。',
    '相对美欧中共振窗(2026-02→2026-05)，东京口径的上行起点(2026-06)晚约一个季度，'
    '全国口径的回升起点(2026-03)则与共振窗起点相邻——『滞后同向』只对东京口径成立。')
SUP['first_mover'] = rep(
    SUP['first_mover'], '——日本通胀回升段的区域先行读数。', '——日本通胀回升段的区域口径读数(东京)。')
SUP['follow_or_diverge'] = rep(
    SUP['follow_or_diverge'], '日本通胀与美欧上行方向同向但时点滞后;',
    '日本通胀与美欧上行方向同向(东京口径滞后约一个季度、全国口径回升起点与美欧共振窗起点相邻);')
rm['history_periods']['2025-03']['sample_note'] = rep(
    rm['history_periods']['2025-03']['sample_note'],
    'TOP-N事后符号一致率: 股指六个月、十二个月窗满一致,其余各窗零点六至一点零',
    'TOP-N事后符号一致率: %s' % AGR_TXT)
rm['history_periods']['2023-10']['other_regions_sync'] = rep(
    rm['history_periods']['2023-10']['other_regions_sync'], '(月末快报口径,当日可见)',
    '(月末快报口径,当日可见；所引数值为引擎序列的最新修订值，与首发快报值可能有差异，修订史不可回溯)')

# ── L4 scenarios ────────────────────────────────────────────────────────
S1, S2 = P['l4']['scenarios']
assert [S1['id'], S2['id']] == ['SCN1', 'SCN2']
S1['role'], S2['role'] = '基准情景', '反例情景'
S1['rows']['scenario'] = rep(
    S1['rows']['scenario'], '中国继续按兵不动', '中国维持政策利率不变(未跟进加息)')
S1['rows']['falsification']['threshold'] = rep(
    S1['rows']['falsification']['threshold'], '美国CPI同比(2025-10基期补齐后)回落至2.5以下',
    '美国CPI同比回落至2.5以下(2026-10 同比待 2025-10 基期补齐后再核；2026-11 起同比不受此缺基期影响)')
S1['rows']['asset_direction']['direction'] += '所引 %s 资产值为盘中快照(非收盘价)。' % AS_OF
S2['rows']['trigger']['condition'] = rep(
    S2['rows']['trigger']['condition'], '或美国CPI同比连续两个月回落',
    '或美国CPI同比自 2026-11 观测月起连续两个月回落(2026-10 同比待 2025-10 基期补齐)')
S2['rows']['asset_direction']['direction'] += '所引 %s 资产值为盘中快照(非收盘价)。' % AS_OF
for sc in (S1, S2):
    assert '日本' not in json.dumps(sc['rows'], ensure_ascii=False)

# ── quality_gate_notes (disclosure block; no engine code reads it) ──────
fo = [lk['face_off_verdict'] for ch in TR for lk in ch['links'] if lk.get('competing_explanation')]
assert len(fo) == 4 and set(fo) == {'尚不能区分'}
ev_total = sum(len(c.get('evidence_refs') or []) for c in P['l3']['contradictions']) + \
    sum(len(lk.get('evidence_refs') or []) for ch in P['l3']['mechanism_chains'] for lk in ch['links'])
tzs = {z: FR._local(z).strftime('%H:%M') for z in ('America/New_York', 'Europe/Berlin', 'Asia/Tokyo', 'Asia/Shanghai')}
close_txt = '、'.join('%s %s' % (('标普500指数' if m == 'SPX' else m), L.sgn2(AB['equity'][m]['ret']))
                     for m in ('SPX', 'DAX', 'CAC40', 'NIKKEI225')) + '、VIX %s' % L.sgn2(AB['vix_month_close'])
P['quality_gate_notes'] = [
    '证据与口径: 研究截止日=快照版本日 %s(research_as_of %s；截止时点纽约 %s、法兰克福 %s、东京 %s、上海 %s)。'
    '截止时点美股与德法股指常规时段进行中，SPX、DAX、CAC40、VIX 及近 24 小时交易品种(GOLD_F、DXY、BRENT_F)与外汇的当日值为盘中快照(非收盘价)；'
    'NIKKEI225 止于 %s 收盘、SHCOMP 为 %s 收盘。同日收盘口径对照(%s→%s): %s。'
    '四地三时点对照的月频指标按观测月取值，日频指标按锚日前最近观测取值。'
    % (AS_OF, FR.snap['research_as_of'], tzs['America/New_York'], tzs['Europe/Berlin'],
       tzs['Asia/Tokyo'], tzs['Asia/Shanghai'], FR.last_date('NIKKEI225'), FR.last_date('SHCOMP'),
       W0, CLOSE, close_txt),
    '对质面: 传导面 %d 环均给出主/竞争两侧对同一区分指标的不同预期，判断=尚不能区分 ×%d(逐环两侧相容观测见传导面正文)。'
    '竞争解释: L3 三条矛盾陈述各并列 %s 种解释。'
    % (len(fo), sum(1 for v in fo if v == '尚不能区分'),
       '、'.join(str(len(c['competing_explanations'])) for c in P['l3']['contradictions'])),
    '证伪面: 两情景各给出可观测触发条件与失效阈值，期限均为 %s；日本央行决议 %s(生效 %s，目标水平 %s)取自冻结发布日历 v%s 实录；'
    '美联储决议日=生效日前一日、欧央行决议日=生效日前上一个周四，均为引擎按惯例回推【推断】，冻结发布日历无美联储与欧央行实录条目。'
    'E2/E3 环的证伪指标与阈值见机制链正文。'
    % (S1['rows']['trigger']['deadline'], BOJ_D, BOJ_E, L.n(BOJ_T), CAL.get('version')),
    '数据面: Gate A=%s——核心缺口 %s 项、非核心缺口 %s 项(%s)、非核心降级 %s 项(%s)；'
    '缺口指标中 %s 项在序列库内有存量观测(%s)，本档按存量观测引用并按过期/降级口径披露，属采集步骤降级口径。'
    '美国 CPI 2026-10 同比缺 2025-10 基期(当月同比不可得)。证据引用共 %d 条，全部取自本轮冻结快照 %s。'
    % (GA.get('status'), cn_count(len(GA.get('core_missing') or [])), cn_count(len(ncm)), '、'.join(ncm),
       cn_count(len(ncd)), '、'.join(ncd), cn_count(len(ncm_have)), '、'.join(ncm_have),
       ev_total, FR.snap.get('snapshot_id')),
    '政策口径披露: ①引擎『政策一年窗路径』面板按窗内首观测→窗末观测计净变动，对阶梯序列漏计窗启时在值的升幅——面板值 ECB_DFR +25bp、'
    'ECB_MRO +25bp、JP_POLICY_RATE +%dbp；按『窗启时在值→窗末观测』口径为 +50bp、+50bp、+%dbp，本档正文采用后者并保留面板值。'
    '②中国政策利率锚 %s 自 7 天逆回购利率切换为隔夜逆回购利率(新锚 %s)，新锚在 12 个月前与 3 个月前锚日无观测，换锚后原工具无新观测。'
    '③中国 7 天逆回购利率末观测 %s(滞后 %d 天)，为采集缺口下的过期口径。'
    % (panel_net('JP_POLICY_RATE'), net_carry, ovo_first, L.n(ovo_val), omo_last,
       (D0 - datetime.date.fromisoformat(omo_last)).days),
    '引擎缺口披露(已登记为待裁定残留，本轮未改引擎): ①政策一年窗路径的净变动口径(见上条①)；'
    '②点值面 DFEDTARU 行日期为锚日(日历日填充)、同区 DFF 行为实际观测日，两行日期相差数日属渲染口径；'
    '③文本一致性别名表未收录 ECB_MRO、JP_CPI_YOY、EA_HICP_YOY、JP_CPI_TOKYO_YOY、JP_POLICY_TARGET、DFEDTARU、CN_OMO_7D、CN_POLICY_OVERNIGHT，'
    '且含机构引用词的子句数字不回贴——本档矛盾陈述对这些指标以中文数位或不带数字的写法表述，传导/走位/转折面的数字以独立席位复算为准；'
    '④证据索引对 CN_PPI_YOY、CN_CPI_YOY 的引用标签日期为观测月末(2026-10-31)而序列观测日为月初(2026-10-01)，同一观测两个日期标签；'
    '⑤转折表第二行口径栏的单位标签(『z口径』栏显示同比百分数)为渲染层文案；'
    '⑥Gate A 非核心缺口清单列入有序列库存量观测的指标(正文按过期/降级口径披露)；'
    '⑦历史相似段事后窗按自然月末口径(非交易日)，事后结果≠预测；欧央行利率序列止于 %s。' % ecb_last,
]

json.dump(P, open(p_out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('wrote', p_out)
print('face-offs', fo)
print('ev_total', ev_total, '| ncm_have', ncm_have)
print('hy', hy_last_d, hy_last, 'pct', hy_pct, 'since', hy_since, 'iso', hy_iso, L.f2(hy_w), L.f2(hy_7), L.f2(hy_12))
print('jp', jp_carry_ym, jp_carry, '->', jp_last_ym, jp_last, sig, noise, net_dec, net_carry)
print('vis', vis_rows)
print('close', CLOSE, close_txt)
print('cp', {k: round(v, 2) for k, v in sorted(cp_win.items())})
print('cy', {k: round(v, 2) for k, v in sorted(cy_win.items())})
print('ea', ea_win)
print('pp', pp_win)
print('pm', pm_win)
print('br', {k: round(br[k], 2) for k in sorted(br) if k >= '2026-01'}, round(br_chg, 2), br_hi)
print('cc', {k: (round(v, 2) if v is not None else None) for k, v in sorted(cc.items()) if k >= '2026-01'})
print('AGR', AGR_TXT)
