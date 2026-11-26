# -*- coding: utf-8 -*-
"""rc15: 收尾补记——位置专属的剩余数字核对(Audit-R32 A round1; 只读)。
用法: /usr/bin/python3 -I rc15_final_supplement.py <snapshot.json> <run_dir>
背景: rc14/rc14b 全量数字清点显示, 受审稿若干位置的数字此前只有"他处同值"的台账记录
      (如 C1 最新水平清单、C3 最新读数、情景段所引历史事后窗、美国 25bp 升降、
      政策一年窗路径口径、日本央行日历条目、转折候选面排序、turnings[1] 跟进面)。
      本脚本逐位置从只读面直算后再比对, 使每个位置都有自己的出处记录。
      另核对几条此前未单列的定性/半定量陈述(两度上调、持续上行、未再越过高点、
      2026-03 同月跳升、2025-01 高点 4.03 等)。
所有记录 note 带 [rc15] 标记: 重跑前 /usr/bin/python3 -I rc_clean_mark.py '[rc15] '
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_lib as L
import rc_points as P

json_dumps = json.dumps
snap = L.load(sys.argv[1]); RUN = sys.argv[2]
cal = L.load(os.path.join(RUN, 'root_overlay', 'config', 'release_calendar.json'))
F = L.Face(snap, cal)
aj = L.load(os.path.join(RUN, 'agent_judgment.json'))
rep = L.load(os.path.join(RUN, 'report.json'))
CUT = '2026-11-23'
W0, W1 = '2025-11-23', '2026-11-23'          # 引擎『政策一年窗路径』窗

_add = P.add
P.add = lambda section, src, computed, reported, ok, note='', where='': _add(
    section, src, computed, reported, ok, note='[rc15] ' + note, where=where)

S_T = '⑩走位/转折叙述'; S_P = '④政策面'; S_S = '⑨情景阈值/期限'
S_Y = '①③同比路径(月频)'; S_X = '杂项(引用/日历/结构)'; S_H = '⑧历史事后窗'
c1, c2, c3 = aj['l3']['contradictions']
rm = aj['reader_map']


def yoy(name, ym):
    """水平序列严格同月去年比 -> float 或 None"""
    r = L.yoy_level(F, name, ym)
    return None if r[0] is None else r[0]


def chg_points(name, d0, d1):
    """窗 [d0,d1] 内序列值对其前值的变动点 [(date, from, to, delta_bp)]"""
    s = F.series(name)
    return [(s[i][0], s[i - 1][1], s[i][1], round((s[i][1] - s[i - 1][1]) * 100))
            for i in range(1, len(s)) if s[i][1] != s[i - 1][1] and d0 <= s[i][0] <= d1]


def month_end_ret(name, c, k):
    """月末口径事后窗: 候选月末(含)前最后观测 → 候选月+k 月月末(含)前最后观测 的 % 变化"""
    a = F.at_or_before(name, L.month_end(c)); b = F.at_or_before(name, L.month_end(L.add_months(c, k)))
    return round(L.pct(a[1], b[1]), 2), a[0], b[0]


# ============ (A) C1 证据面最新水平清单 ============
refs1 = dict(x.split('@') for x in c1['evidence_refs'])
pairs = re.findall(r'([A-Z][A-Z_0-9]+) 水平为 (-?[0-9]+(?:\.[0-9]+)?)', c1['statement'])
print('C1 levels', pairs)
for name, val in pairs:
    d, v = F.at_or_before(name, CUT)
    pub, basis = L.release_date(F, name, d)
    rd = refs1.get(name)
    same = (rd is None) or (rd[:7] == d[:7])
    P.add('②/⑬点值格', 'snapshot.series_store.%s 截止日前最近观测(值/观测日) + C1.evidence_refs 标签日期 + 规则发布日' % name,
          {'obs_date': d, 'value': v, 'ref_label': rd, 'pub_date': pub, 'basis': basis},
          {'value': float(val), 'ref_label': rd, 'obs_upto': '2026-11-23'},
          P.eq(v, float(val)) and same and pub <= CUT,
          note=('C1「%s 水平为 %s」逐位核对' % (name, val)) + ('' if rd is None else ('; 引用标签日期=观测日' if rd == d else '; 引用标签日期 %s 与序列观测日 %s 同月不同日(受审稿质量注记⑤④已披露: 月末标签/月初观测)' % (rd, d))),
          where='agent_judgment.l3.contradictions[0].statement 证据面最新水平清单 / MAP_REPORT 主线综合')

# ============ (B) C1 半定量陈述 ============
ups = [x for x in chg_points('ECB_DFR', W0, W1) if x[3] > 0]
P.add(S_P, 'ECB_DFR 一年窗(2025-11-23..2026-11-23)内上调变动点', ups, 'ECB_DFR 两度上调',
      len(ups) == 2, note='C1「ECB_DFR 两度上调」: 窗内上调变动点 %d 处, 无下调' % len(ups),
      where='agent_judgment.l3.contradictions[0].statement')

jp = [(d, v) for d, v in F.series('JP_POLICY_RATE') if '2025-11-01' <= d <= CUT]
jdiff = [(jp[i][0], round((jp[i][1] - jp[i - 1][1]) * 100, 1)) for i in range(1, len(jp))]
P.add(S_P, 'JP_POLICY_RATE 月均 2025-11..2026-10 逐月变动(bp) 最小值/上调月数/舍入级微降处',
      {'min_bp': min(x[1] for x in jdiff), 'n_up_ge_1bp': sum(1 for x in jdiff if x[1] >= 1), 'rounding_dips': [x for x in jdiff if -0.5 < x[1] < 0]},
      'JP_POLICY_RATE 持续上行',
      min(x[1] for x in jdiff) >= -0.5 and sum(1 for x in jdiff if x[1] >= 1) >= 6,
      note='C1「JP_POLICY_RATE 持续上行」: 月均口径逐月变动最小 %s bp(仅舍入级微降), 上调≥1bp 月数 %d' % (min(x[1] for x in jdiff), sum(1 for x in jdiff if x[1] >= 1)),
      where='agent_judgment.l3.contradictions[0].statement')

e = {n: (F.at(n, '2025-11-19'), F.at(n, '2026-11-19')) for n in ('UST_10Y', 'TIPS_10Y', 'BEI_10Y')}
P.add(S_Y, 'series_store UST_10Y/TIPS_10Y/BEI_10Y @2025-11-19→@2026-11-19', e, 'UST_10Y 与 TIPS_10Y 上行而 BEI_10Y 回落',
      e['UST_10Y'][1] > e['UST_10Y'][0] and e['TIPS_10Y'][1] > e['TIPS_10Y'][0] and e['BEI_10Y'][1] < e['BEI_10Y'][0],
      note='C1 方向陈述(12 个月共同交易日窗): 名义 %s→%s、实际 %s→%s、盈亏平衡 %s→%s' % (
          e['UST_10Y'][0], e['UST_10Y'][1], e['TIPS_10Y'][0], e['TIPS_10Y'][1], e['BEI_10Y'][0], e['BEI_10Y'][1]),
      where='agent_judgment.l3.contradictions[0].statement')

a = {n: (F.at_or_before(n, '2026-10-23'), F.at_or_before(n, CUT)) for n in ('SPX', 'NIKKEI225', 'GOLD_F', 'DXY', 'VIX')}
okA = all(a[n][1][1] < a[n][0][1] for n in ('SPX', 'NIKKEI225', 'GOLD_F')) and all(a[n][1][1] > a[n][0][1] for n in ('DXY', 'VIX'))
P.add('⑤资产窗', 'series_store SPX/NIKKEI225/GOLD_F/DXY/VIX 2026-10-23→截止日前最近观测',
      {n: [a[n][0], a[n][1], round(L.pct(a[n][0][1], a[n][1][1]), 2)] for n in a}, 'SPX 与 NIKKEI225 与 GOLD_F 近月收缩而 DXY 与 VIX 走高', okA,
      note='C1 方向陈述(近月窗): ' + '; '.join('%s %s' % (n, round(L.pct(a[n][0][1], a[n][1][1]), 2)) for n in a),
      where='agent_judgment.l3.contradictions[0].statement')

cp = {ym: yoy('CORE_PCE', ym) for ym in ('2025-09', '2026-05', '2026-06', '2026-07', '2026-08', '2026-09')}
ci = {ym: yoy('CPI', ym) for ym in ('2025-09', '2025-11', '2026-01', '2026-05', '2026-06', '2026-07', '2026-08', '2026-09', '2026-10')}
after_c = [ci[y] for y in ci if y > '2026-05' and ci[y] is not None]
after_p = [cp[y] for y in cp if y > '2026-05' and cp[y] is not None]
P.add(S_Y, 'CPI/CORE_PCE 同比: 2026-09 vs 一年前(2025-09); 2026-05 值; 2026-05 之后各观测月最大值; 2026-10 同比',
      {'CPI_2026-09': round(ci['2026-09'], 2), 'CPI_2025-09': round(ci['2025-09'], 2), 'CPI_2026-05': round(ci['2026-05'], 4), 'CPI_after_max': round(max(after_c), 4),
       'PCE_2026-09': round(cp['2026-09'], 2), 'PCE_2025-09': round(cp['2025-09'], 2), 'PCE_2026-05': round(cp['2026-05'], 2), 'PCE_after_max': round(max(after_p), 2), 'CPI_2026-10': ci['2026-10']},
      '同比较一年前走高(2026-05 见顶后回落、未再越过高点)',
      ci['2026-09'] > ci['2025-09'] and cp['2026-09'] > cp['2025-09'] and max(after_c) < ci['2026-05'] and max(after_p) < cp['2026-05'],
      note='C1 括注核对: CPI 同比 %.2f→%.2f、CORE_PCE 同比 %.2f→%.2f(较一年前走高); 2026-05 之后最大值 CPI %.4f / PCE %.2f 均低于 2026-05 高点; CPI 2026-10 同比=%s' % (
          ci['2025-09'], ci['2026-09'], cp['2025-09'], cp['2026-09'], max(after_c), max(after_p), ci['2026-10']),
      where='agent_judgment.l3.contradictions[0].statement / regions[US].from_to')

# ============ (C) C3 最新读数与定性陈述 ============
for name, val in (('CN_PPI_YOY', 5.7), ('CN_CPI_YOY', 0.7), ('CN_PMI_MFG', 49.3)):
    d, v = F.at_or_before(name, CUT)
    P.add('②/⑬点值格', 'snapshot.series_store.%s 截止日前最近观测(值/观测日)' % name, [d, v], [val, '2026-10'],
          P.eq(v, val) and d[:7] == '2026-10', note='C3「最新读数: %s 为 %s; 观测月 2026-10」' % (name, val),
          where='agent_judgment.l3.contradictions[2].statement 最新读数括注')
on = F.series('CN_POLICY_OVERNIGHT')
P.add(S_P, 'CN_POLICY_OVERNIGHT 全序列观测数/首末观测日/取值集合', [len(on), on[0][0], on[-1][0], sorted(set(v for _, v in on))],
      ['新锚持平于其首个观测水平', '2026-11-02', 1.25],
      len(set(v for _, v in on)) == 1 and on[0][0] == '2026-11-02' and on[0][1] == 1.25,
      note='C3「政策利率锚于2026-11-02切换为隔夜利率工具后新锚持平于其首个观测水平」: 全部 %d 个观测同为 1.25' % len(on),
      where='agent_judgment.l3.contradictions[2].statement / quality_gate_notes[4]②')
lpr = F.window('CN_LPR_1Y', W0, CUT)
P.add(S_P, 'CN_LPR_1Y 一年窗内观测数/取值集合 + 截止日前最近观测', [len(lpr), sorted(set(v for _, v in lpr)), F.at_or_before('CN_LPR_1Y', CUT)],
      'CN_LPR_1Y …窗内持平', len(set(v for _, v in lpr)) == 1 and lpr[0][1] == 3.0,
      note='C3「CN_LPR_1Y 与 7天逆回购利率窗内持平」LPR 一腿: 窗内 %d 个观测均为 3.0; 最新观测 2026-11-20(未列入 Gate A 缺口/降级)' % len(lpr),
      where='agent_judgment.l3.contradictions[2].statement / evidence_refs CN_LPR_1Y@2026-11-20')
pp, cc = F.at_or_before('CN_PPI_YOY', CUT)[1], F.at_or_before('CN_CPI_YOY', CUT)[1]
P.add(S_Y, 'CN_PPI_YOY 最新 − CN_CPI_YOY 最新 (pp)', round(pp - cc, 2), 'PPI 与 CPI 剪刀差大', round(pp - cc, 2) >= 4.0,
      note='C3 解释A「PPI 与 CPI 剪刀差大」: %.1f − %.1f = %.1fpp' % (pp, cc, pp - cc),
      where='agent_judgment.l3.contradictions[2].competing_explanations[0]')

# ============ (D) 「4.17」舍入 ============
P.add(S_Y, 'CPI 同比 2026-05 直算值 → 保留两位', [round(ci['2026-05'], 4), round(ci['2026-05'], 2)], [4.1666, 4.17],
      P.eq(ci['2026-05'], 4.1666, 5e-5) and round(ci['2026-05'], 2) == 4.17,
      note='M1.step2/TR1.step2「2026-05 高点 4.17」为 4.1666 的两位小数舍入(同一观测两种显示精度, 一致)',
      where='agent_judgment.l3.mechanism_chains[0].links[1].text / reader_map.transmission[0].links[1]')

# ============ (E) 情景段所引历史事后窗(月末口径) ============
st = [s for s in rep['steps'] if s.get('step') == 'S6_analog'][0]
top = st['envelope']['data']['top']
sc = {s['id']: s for s in aj['l4']['scenarios']}
scn1 = sc['SCN1']['rows']['asset_direction']['direction']
scn2 = sc['SCN2']['rows']['asset_direction']['direction']
for name, repv in (('SPX', -5.28), ('GOLD_F', -7.49), ('DXY', 7.10)):
    v, d0, d1 = month_end_ret(name, '2022-06', 3)
    P.add(S_H, 'series_store.%s 月末口径 2022-06→2022-09 (%%)' % name, [v, d0, d1], [repv, '月末口径'],
          P.eq(v, repv), note='SCN1「2022-06相似段三个月窗」%s' % name + ('' if '%.2f' % repv in scn1 else '(受审稿句内未找到该数!)'),
          where='agent_judgment.l4.scenarios[SCN1].rows.asset_direction.direction')
v, d0, d1 = month_end_ret('SPX', '2022-06', 12)
P.add(S_H, 'series_store.SPX 月末口径 2022-06→2023-06 (%)', [v, d0, d1], [17.57, '月末口径'], P.eq(v, 17.57),
      note='SCN1「同段十二个月窗 SPX 转正(+17.57%)」', where='agent_judgment.l4.scenarios[SCN1].rows.asset_direction.direction')
for name, repv in (('GOLD_F', 48.83), ('DXY', -4.08), ('SPX', 16.33)):
    v, d0, d1 = month_end_ret(name, '2025-03', 12)
    P.add(S_H, 'series_store.%s 月末口径 2025-03→2026-03 (%%)' % name, [v, d0, d1], [repv, '月末口径'],
          P.eq(v, repv), note='SCN2「2025-03相似段十二个月窗」%s' % name,
          where='agent_judgment.l4.scenarios[SCN2].rows.asset_direction.direction')
d0 = top[0]['dims']
sh = {k: round(d0[k]['contribution_share'] * 100, 1) for k in d0}
P.add(S_H, 'report.json steps[S6_analog].envelope.data.top[0](2025-03).dims.*.contribution_share (%)', sh, [42.1, 40.7],
      sh['volatility'] == 42.1 and sh['rates'] == 40.7 and '42.1%+40.7%' in scn2,
      note='SCN2「相似度主要由波动维与利率维支撑(42.1%%+40.7%%)」: 波动 %s / 利率 %s / 通胀 %s / 估值 %s / 增长 %s / 信用 %s' % (
          sh['volatility'], sh['rates'], sh['inflation'], sh['valuation'], sh['growth'], sh['credit']),
      where='agent_judgment.l4.scenarios[SCN2].rows.asset_direction.direction')
P.add(S_H, '2025-03 段十二个月事后窗(至 2026-03-31) 与本轮研究窗(2025-11-23 起)的重叠日数',
      L.days(W0, L.month_end(L.add_months('2025-03', 12))) + 1, '事后窗与本轮早段重叠', L.days(W0, L.month_end(L.add_months('2025-03', 12))) + 1 > 60,
      note='SCN2「事后窗与本轮早段重叠,样本非独立」: 重叠 %d 天' % (L.days(W0, L.month_end(L.add_months('2025-03', 12))) + 1),
      where='agent_judgment.l4.scenarios[SCN2].rows.asset_direction.direction')
P.add(S_S, 'SCN1 前提/触发/证伪阈值(CPI>3 / ≥3.5 / <2.5 且 CORE_PCE<2.8)与 SCN2 证伪阈值(BEI_10Y<1.8): 席位自设参数, 无数据真值; 与截止日读数的相容性见 #552/#553',
      {'CPI_2026-09': round(ci['2026-09'], 2), 'CORE_PCE_2026-09': round(cp['2026-09'], 2), 'BEI_10Y_2026-11-20': F.at('BEI_10Y', '2026-11-20')},
      [3, 3.5, 2.5, 2.8, 1.8], 'NA',
      note='登记项(参数性数字, 非数据读数): 各阈值在截止日读数(CPI 3.72 / CORE_PCE 3.12 / BEI_10Y 2.15)与高点(CPI 4.17 / CORE_PCE 3.16)之间的位置合理, 可观测; 不计入比对点',
      where='agent_judgment.l4.scenarios[SCN1|SCN2].rows')

# ============ (F) 美国政策: DFEDTARU 变动点 ============
tu = chg_points('DFEDTARU', W0, W1)
P.add(S_P, 'series_store.DFEDTARU 一年窗内变动点(date, from, to, delta_bp)', tu,
      [['2025-12-11', 4.0, 3.75, -25], ['2026-09-17', 3.75, 4.0, 25]],
      [(x[0], x[1], x[2], x[3]) for x in tu] == [('2025-12-11', 4.0, 3.75, -25), ('2026-09-17', 3.75, 4.0, 25)],
      note='US from_to「降25个基点(目标区间上限 4.0→3.75)…回升25个基点(3.75→4.0)」; 净变 %dbp' % sum(x[3] for x in tu),
      where='agent_judgment.reader_map.regions[US].from_to / turnings[*].follow_or_diverge / headline_conclusion')
P.add(S_P, 'DFEDTARU 变动点生效日的上一个日历日(引擎惯例: 决议日=生效日前一日) 与其星期',
      [[x[0], L.shift_days(x[0], -1), L.weekday(L.shift_days(x[0], -1))] for x in tu], [['2025-12-11', '2025-12-10', 3], ['2026-09-17', '2026-09-16', 3]],
      all(L.shift_days(x[0], -1) == y[1] and L.weekday(y[1]) == 3 for x, y in zip(tu, [('2025-12-11', '2025-12-10', 3), ('2026-09-17', '2026-09-16', 3)])),
      note='「2025-12-10决议、2025-12-11生效」「2026-09-16决议、2026-09-17生效」: 生效日前一日均为星期三; 与引擎 policy_face.decision_kind=prev_day 及 policy_event_clusters(2025-12-10 / 2026-09-16)一致',
      where='agent_judgment.reader_map.regions[US].from_to / M1.step2')

# ============ (G) 政策一年窗路径口径对照 ============
for name, main, alt, sv in (('ECB_DFR', 50, 25, 2.0), ('ECB_MRO', 50, 25, 2.15), ('JP_POLICY_RATE', 75, 67, 0.478)):
    s = F.series(name)
    idx = [i for i, (d, v) in enumerate(s) if W0 <= d <= W1]
    cp = chg_points(name, W0, W1)
    net_cp = round(sum(x[3] for x in cp))
    start_val = s[idx[0] - 1][1] if idx[0] > 0 else s[idx[0]][1]
    alt_bp = round((s[idx[-1]][1] - s[idx[0]][1]) * 100)
    P.add(S_P, 'series_store.%s 一年窗: 变动点之和(bp) / 窗启时在值(窗内首观测的前值) / 窗内首观测值→窗末观测值(bp)' % name,
          {'net_change_points_bp': net_cp, 'window_start_value': start_val, 'alt_first_obs_to_last_bp': alt_bp, 'n_change_points': len(cp)},
          {'panel_net_bp': main, 'alt_bp': alt, 'start_value': sv},
          net_cp == main and alt_bp == alt and P.eq(start_val, sv),
          note='quality_gate_notes[4]①「本轮显示 %s +%dbp…另一口径为 +%dbp」逐位核对(变动点 %d 处)' % (name, main, alt, len(cp)),
          where='agent_judgment.quality_gate_notes[4] / EA from_to 口径注记 / JP from_to / M2.step1')

# ============ (H) 日本央行日历条目 ============
ent = {e['entry_id']: e for e in cal['entries']}
a_ = ent['RC-JP-BOJ-TARGET-2026-09']; b_ = ent['RC-JP-BOJ-MAINT-2026-10']
comp = [a_['decision_date'], a_['effective_on'], a_['target_value'], a_['kind'], b_['decision_date'], b_['kind'], b_['target_value']]
repv = ['2026-09-18', '2026-09-24', 1.25, 'policy_decision', '2026-10-30', 'policy_maintenance', 1.25]
texts = (aj['l3']['mechanism_chains'][1]['links'][0]['text'] + aj['quality_gate_notes'][2] + rm['regions'][3]['from_to']
         + rm['turnings'][2]['follow_or_diverge'] + rm['turning_supplement'][0]['follow_or_diverge'])
P.add(S_P, 'root_overlay/config/release_calendar.json entries[RC-JP-BOJ-TARGET-2026-09 / RC-JP-BOJ-MAINT-2026-10]: decision_date/effective_on/target_value/kind',
      comp, repv, comp == repv and '决议2026-09-18' in texts and '生效2026-09-24' in texts and '2026-10-30' in texts and cal['version'] == '1.5.0',
      note='「发布日历实录载政策决议2026-09-18(生效2026-09-24,目标水平 1.25)」与「2026-10-30 确认维持决议」逐字段核对; 日历版本 %s' % cal['version'],
      where='agent_judgment.l3.mechanism_chains[1].links[0].text / quality_gate_notes[2] / regions[JP].from_to / turnings[2] / turning_supplement')
POLICY_METRICS = ('DFEDTARU', 'DFF', 'ECB_MRO', 'ECB_DFR')
pol = [e for e in cal['entries'] if e.get('kind') in ('policy_decision', 'policy_maintenance')]
fed_ecb_policy = [e['entry_id'] for e in pol if e.get('metric_id') in POLICY_METRICS or e.get('decision_date')]
rel_us = [e['entry_id'] for e in cal['entries'] if not e.get('kind') and str(e.get('batch_id', '')).startswith('BLS') or (not e.get('kind') and 'SHUTDOWN' in e['entry_id'])]
rel_ea = [e['entry_id'] for e in cal['entries'] if not e.get('kind') and e.get('metric_id') == 'EA_HICP_YOY']
rel_cn = [e['entry_id'] for e in cal['entries'] if not e.get('kind') and e.get('metric_id') == 'CN_LPR_1Y']
fed_ecb_policy = [e['entry_id'] for e in pol if e.get('metric_id') in POLICY_METRICS]
P.add(S_P, 'release_calendar.json: 政策类条目(kind=policy_decision/policy_maintenance)清单; 其中 metric 属美联储/欧央行(DFEDTARU/DFF/ECB_MRO/ECB_DFR)的条目数; 数据发布类条目数(美国停摆批次/HICP/LPR)',
      {'policy_entries': [[e['entry_id'], e.get('metric_id')] for e in pol], 'fed_ecb_policy_entries': fed_ecb_policy,
       'release_entries': {'US_shutdown': len(rel_us), 'EA_HICP': len(rel_ea), 'CN_LPR': len(rel_cn), 'total': len(cal['entries']) - len(pol)}},
      '冻结发布日历无美联储与欧央行实录条目', len(pol) == 2 and fed_ecb_policy == [] and all(e.get('metric_id') == 'JP_POLICY_TARGET' for e in pol),
      note='quality_gate_notes[2]/SCN 触发条件「冻结发布日历无美联储与欧央行实录条目」: 日历 18 条中政策类仅日本央行 2 条, 美联储/欧央行政策决议实录 0 条(成立); 另有数据发布类 %d 条(美国停摆批次 %d、HICP %d、LPR %d), 其中 RC-2025SHUTDOWN-INDPRO-SEP 注记引用美联储改期公告(统计发布, 非政策决议)——措辞可更精确为「无两家政策决议实录条目」, 列 NIT' % (
          len(cal['entries']) - len(pol), len(rel_us), len(rel_ea), len(rel_cn)),
      where='agent_judgment.quality_gate_notes[2] / l4.scenarios[*].rows.trigger.condition')
P.add(S_P, 'ECB 第二次决议 2026-09-10 与 BOJ 决议 2026-09-18 的先后(决议日粒度)',
      L.days('2026-09-10', '2026-09-18'), 'ECB 09-10 早于 BOJ 09-18', L.days('2026-09-10', '2026-09-18') == 8,
      note='turning_supplement「决议日粒度 ECB 09-10 早于 BOJ 09-18」: 相隔 8 天(欧央行决议日为引擎回推【推断】, 受审稿已标注)',
      where='agent_judgment.reader_map.turning_supplement[0].follow_or_diverge')
P.add(S_P, '2026 年 9 月收紧决议计数: EA(2026-06-17/2026-09-16 生效 +25bp)、US(2026-09-17 生效 +25bp)、JP(日历 2026-09-18 决议)',
      {'EA': [x[0] for x in chg_points('ECB_DFR', W0, W1)], 'US': [x[0] for x in tu if x[3] > 0], 'JP_calendar': [a_['decision_date']]},
      '2026-09 三次收紧决议', len([x for x in chg_points('ECB_DFR', W0, W1) if x[0][:7] == '2026-09'] + [x for x in tu if x[0][:7] == '2026-09']) + 1 == 3,
      note='M1.step2「2026-09 三次收紧决议时点」: 欧央行 09-10、美联储 09-16、日本央行 09-18',
      where='agent_judgment.l3.mechanism_chains[0].links[1].text')

# ============ (I) 转折候选面排序 ============
cands = rep['research_plan']['turning_candidates']['candidates']
growth = sorted([c for c in cands if c['dimension'] == 'growth'], key=lambda c: -abs(c['delta']))
top_all = max(cands, key=lambda c: abs(c['delta']))
usea = max([c for c in cands if c['region'] in ('US', 'EA')], key=lambda c: abs(c['delta']))
P.add(S_T, 'report.json research_plan.turning_candidates.candidates: 增长维按|delta|排序 / 全体首位 / 美欧最大',
      {'growth_rank': [(c['metric_id'], c['delta']) for c in growth], 'top_all': [top_all['metric_id'], top_all['delta']], 'top_US_EA': [usea['metric_id'], usea['delta']]},
      {'growth_rank1': ['CN_PMI_MFG', 3.40], 'top_all': ['CN_PPI_YOY', 4.8], 'top_US_EA': ['CPI', 1.7326]},
      growth[0]['metric_id'] == 'CN_PMI_MFG' and P.eq(growth[0]['delta'], 3.40) and top_all['metric_id'] == 'CN_PPI_YOY' and P.eq(top_all['delta'], 4.8)
      and usea['metric_id'] == 'CPI' and P.eq(usea['delta'], 1.7326),
      note='turnings[1]「中国制造业PMI居增长维候选面首位，增量3.40；候选面全体首位为中国PPI同比，增量4.8」/ turnings[0]「候选面最大美欧值」: 增长维候选 %s; 3.4005 的两位小数舍入=3.40' % [(c['metric_id'], c['delta']) for c in growth],
      where='agent_judgment.reader_map.turnings[1].first_mover / turnings[0].first_mover')

# ============ (J) turnings[1].follow_or_diverge 所引数字 ============
gdp = {n: {ym: F.at(n, ym + '-01') for ym in ('2025-07', '2026-04', '2026-07')} for n in ('EA_REAL_GDP_YOY', 'JP_REAL_GDP_YOY')}
un = {ym: F.at_or_before('UNEMPLOYMENT', L.month_end(ym))[1] for ym in ('2025-09', '2026-10')}
ip = {ym: yoy('INDPRO', ym) for ym in ('2025-08', '2026-07', '2026-10')}
P.add(S_T, 'series_store EA_REAL_GDP_YOY / JP_REAL_GDP_YOY @2025-07/2026-04/2026-07; UNEMPLOYMENT 2025-09→2026-10; INDPRO 同比 2025-08/2026-07/2026-10',
      {'EA': list(gdp['EA_REAL_GDP_YOY'].values()), 'JP': list(gdp['JP_REAL_GDP_YOY'].values()), 'UNEMP': [un['2025-09'], un['2026-10']],
       'INDPRO_yoy': [round(ip['2025-08'], 2), round(ip['2026-07'], 2), round(ip['2026-10'], 2)]},
      {'EA': [1.11, 1.19, 1.28], 'JP': [0.63, 0.80, 1.16], 'UNEMP': [4.4, 4.1], 'INDPRO_yoy': [1.19, 1.25, 2.15]},
      list(gdp['EA_REAL_GDP_YOY'].values()) == [1.11, 1.19, 1.28] and list(gdp['JP_REAL_GDP_YOY'].values()) == [0.63, 0.8, 1.16] and un == {k: v for k, v in (('2025-09', 4.4), ('2026-10', 4.1))}
      and P.eq(ip['2025-08'], 1.19) and P.eq(ip['2026-07'], 1.25) and P.eq(ip['2026-10'], 2.15),
      note='turnings[1]「欧元区GDP同比同期缓升(1.11→1.28)、日本GDP同比回升(0.63→1.16,观测 2025-07→2026-04→2026-07)、美国失业率改善(4.4→4.1)…其后2026-10同比回到2.15」(EA/JP GDP 同比为 Gate A 非核心缺口项的存量观测)',
      where='agent_judgment.reader_map.turnings[1].follow_or_diverge / regions[US|EA|JP].from_to')

# ============ (K) turnings[2] / turnings[0] 路径陈述 ============
jpm = F.monthly('JP_CPI_YOY')
seg = {ym: jpm[ym] for ym in jpm if '2025-01' <= ym <= '2026-02'}
ups_j = [ym for ym in seg if ym > '2025-01' and jpm[ym] > jpm[L.add_months(ym, -1)]]
hk = max(seg, key=seg.get)
P.add('⑥转折路径', 'series_store JP_CPI_YOY 2025-01..2026-02: 高点月/值; 低点月/值; 其间逐月上行的月份',
      {'high_ym': hk, 'high': jpm[hk], 'low_ym': min(seg, key=seg.get), 'low': jpm[min(seg, key=seg.get)], 'mom_up_months': ups_j},
      {'high_ym': '2025-01', 'high': 4.03, 'low_ym': '2026-02', 'low': 1.27, 'mom_up_months': ['2025-09', '2025-10']},
      hk == '2025-01' and P.eq(jpm[hk], 4.03) and min(seg, key=seg.get) == '2026-02' and P.eq(jpm['2026-02'], 1.27) and ups_j == ['2025-09', '2025-10'],
      note='turnings[2]「自 2025-01 高点 4.03 至 2026-02 低点 1.27 总体下行，其间 2025-09、2025-10 小幅回升」',
      where='agent_judgment.reader_map.turnings[2].first_mover')
jump = {}
for name, fn in (('CPI', lambda ym: yoy('CPI', ym)), ('EA_HICP_YOY', lambda ym: F.at('EA_HICP_YOY', ym + '-01')), ('CN_PPI_YOY', lambda ym: F.at('CN_PPI_YOY', ym + '-01'))):
    path = {ym: fn(ym) for ym in ('2026-01', '2026-02', '2026-03', '2026-04', '2026-05')}
    inc = {ym: round(path[ym] - path[L.add_months(ym, -1)], 4) for ym in ('2026-03', '2026-04', '2026-05')}
    jump[name] = {'path': {k: round(v, 4) for k, v in path.items()}, 'inc': inc, 'max_inc_month': max(inc, key=inc.get)}
def hist_pct(name, fn):
    """2026-03 月度增量在该序列全部历史月度增量绝对值中的百分位; 以及 2026-02..2026-05 是否逐月上行"""
    mm = F.monthly(name)
    ys = {ym: v for ym in mm if (v := fn(ym)) is not None}
    ch = [(ym, ys[ym] - ys[L.add_months(ym, -1)]) for ym in ys if L.add_months(ym, -1) in ys]
    x = abs(dict(ch)['2026-03'])
    pct = 100.0 * sum(1 for _, c in ch if abs(c) <= x) / len(ch)
    path = [ys[y] for y in ('2026-02', '2026-03', '2026-04', '2026-05')]
    mono = all(path[i] < path[i + 1] for i in range(3))
    return {'inc_2026-03': round(dict(ch)['2026-03'], 4), 'hist_from': ch[0][0], 'n_changes': len(ch), 'pct_of_abs_inc': round(pct, 1), 'monotone_0205': mono}


hist = {n: hist_pct(n, fn) for n, fn in (('CPI', lambda ym: yoy('CPI', ym)), ('EA_HICP_YOY', lambda ym: F.at('EA_HICP_YOY', ym + '-01')), ('CN_PPI_YOY', lambda ym: F.at('CN_PPI_YOY', ym + '-01')))}
okJ = all(h['monotone_0205'] and h['inc_2026-03'] >= 0.5 and h['pct_of_abs_inc'] >= 85 for h in hist.values())
P.add('⑥转折路径', 'CPI 同比/EA_HICP_YOY/CN_PPI_YOY: 2026-02..2026-05 逐月是否上行; 2026-03 月度增量; 该增量在序列全部历史月度增量绝对值中的百分位',
      {'paths': {n: jump[n]['path'] for n in jump}, 'inc_2026-03..05': {n: jump[n]['inc'] for n in jump}, 'hist': hist},
      '2026-02 起三序列同向上行、2026-03 同月大幅跳升', okJ,
      note=('turnings[0]: 三序列 2026-02→05 均逐月上行; 2026-03 增量 CPI %s / HICP %s / 中国PPI %s, 居各自历史月度增量绝对值的第 %s 百分位(均≥85)——「同月大幅跳升」成立; '
            '中国PPI 该段最大增量为 2026-04(+2.3), 受审稿未称 2026-03 为各序列最大增量') % (
          hist['CPI']['inc_2026-03'], hist['EA_HICP_YOY']['inc_2026-03'], hist['CN_PPI_YOY']['inc_2026-03'],
          [hist[n]['pct_of_abs_inc'] for n in hist]),
      where='agent_judgment.reader_map.turnings[0].first_mover')

# ============ (L) 质量注记⑤⑧ CORE_CPI 候选面舍入 ============
cc5, cc8 = yoy('CORE_CPI', '2026-05'), yoy('CORE_CPI', '2026-08')
P.add(S_X, 'CORE_CPI 同比 2026-05/2026-08 未舍入差 与 四位小数端点相减',
      {'yoy_2026-05': cc5, 'yoy_2026-08': cc8, 'unrounded_diff': round(cc8 - cc5, 4), 'rounded_endpoints_diff': round(round(cc8, 4) - round(cc5, 4), 4)},
      {'candidate_delta': -0.3767, 'unrounded_diff': -0.3768}, P.eq(cc8 - cc5, -0.3768, 5e-5) and P.eq(round(cc8, 4) - round(cc5, 4), -0.3767, 5e-5),
      note='quality_gate_notes[5]⑧「美国核心CPI同比 2026-05→2026-08 记 -0.3767，未舍入差为 -0.3768」逐位核对',
      where='agent_judgment.quality_gate_notes[5]⑧ / report.json turning_candidates CORE_CPI')

# ============ (M) 证据索引标签日期 vs 序列观测日 ============
evi = L.load(os.path.join(RUN, 'evidence_index.json'))
lab = {r['ref'].split('@')[0]: r['ref'].split('@')[1] for r in evi if isinstance(r, dict) and '@' in str(r.get('ref', ''))}
P.add(S_X, 'evidence_index.json 中 CN_PPI_YOY/CN_CPI_YOY/CPI/EA_HICP_YOY/JP_POLICY_RATE 的引用标签日期 vs series_store 最新观测日',
      {n: [lab.get(n), F.last(n)[0]] for n in ('CN_PPI_YOY', 'CN_CPI_YOY', 'CPI', 'EA_HICP_YOY', 'JP_POLICY_RATE')},
      {'CN_PPI_YOY': ['2026-10-31', '2026-10-01'], 'CN_CPI_YOY': ['2026-10-31', '2026-10-01']},
      lab.get('CN_PPI_YOY') == '2026-10-31' and F.last('CN_PPI_YOY')[0] == '2026-10-01' and lab.get('CN_CPI_YOY') == '2026-10-31' and F.last('CN_CPI_YOY')[0] == '2026-10-01',
      note='quality_gate_notes[5]④「证据索引对 CN_PPI_YOY、CN_CPI_YOY 的引用标签日期为观测月末(2026-10-31)而序列观测日为月初(2026-10-01)」属实(同一观测两个日期标签, 同月)',
      where='agent_judgment.quality_gate_notes[5]④ / C1/C3 evidence_refs')

print('tally', P.tally())
