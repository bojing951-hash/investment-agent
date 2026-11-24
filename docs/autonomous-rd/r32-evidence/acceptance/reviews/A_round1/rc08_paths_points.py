# -*- coding: utf-8 -*-
"""rc08: 月频路径/政策面/杂项 逐点直算并登记(此前 rc04/rc05 仅打印目核, 本脚本把目核项逐点落账)。
用法: /usr/bin/python3 -I rc08_paths_points.py <snapshot.json> <release_calendar.json> <run_dir>
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_lib as L
import rc_points as P

snap = L.load(sys.argv[1]); cal = L.load(sys.argv[2]); RUN = sys.argv[3]
F = L.Face(snap, cal)
S1 = '①③同比路径(月频)'; S4 = '④政策面'; S6 = '⑥转折路径'; S9 = '⑨情景阈值/期限'; S11 = '⑪诚实缺席'; S12 = '⑫时点标注'
S8 = '⑧历史类比面'; SM = '杂项(引用/日历/结构)'


def yl(m, ym):
    return L.yoy_level(F, m, ym)[0]


def mv(m, ym):
    return F.monthly(m).get(ym)


def chk(section, src, comp, rep, where):
    P.add(section, src, comp, rep, P.eq(comp, rep), where=where)


def chk_txt(section, src, comp, rep, *args):
    # 用法 A: (section, src, comp, rep, ok, where); 用法 B: (section, src, comp, rep, where) -> ok = (comp == rep)
    if len(args) == 2:
        ok, where = args
    elif len(args) == 1:
        where = args[0]
        ok = (comp == rep)
    else:
        raise TypeError('chk_txt bad arity')
    P.add(section, src, comp, rep, bool(ok), where=where)


# ---------------- 美国: CPI / CORE_CPI / CORE_PCE / INDPRO / UNEMPLOYMENT ----------------
CPI = {'2025-09': 3.02, '2026-02': 2.434, '2026-04': 3.78, '2026-05': 4.1666, '2026-07': 3.30, '2026-08': 3.35, '2026-09': 3.72}
for ym, e in CPI.items():
    chk(S1, 'snapshot.series_store.CPI 水平严格同月去年比 %s' % ym, round(yl('CPI', ym), 4), e, 'US from_to / M1.step1-2 / turnings[0]')
y = {k: yl('CPI', k) for k in sorted(F.monthly('CPI'))}
win = {k: v for k, v in y.items() if '2025-11' <= k <= '2026-10' and v is not None}
low = min(win, key=win.get); hi = max(win, key=win.get)
chk_txt(S6, 'CPI 同比 12 个月窗(2025-11..2026-10)低点月', low, '2026-01', low == '2026-01', 'turnings[0] "美国 CPI 同比…低点均在 2026-01"')
chk_txt(S6, 'CPI 同比 12 个月窗高点月', hi, '2026-05', hi == '2026-05', 'M1.step2 "2026-05 高点 4.17"')
chk_txt(S1, 'CPI 同比 2026-09 vs 一年前(2025-09): 3.72 > 3.02', {'2025-09': round(y['2025-09'], 2), '2026-09': round(y['2026-09'], 2)},
      '较一年前走高', y['2026-09'] > y['2025-09'], 'C1 "CPI…同比较一年前走高"')
chk_txt(S1, 'CPI 2026-10 同比基期 2025-10 观测', {'2025-10_obs': mv('CPI', '2025-10'), '2025-11_obs': mv('CPI', '2025-11'), '2025-12_obs': mv('CPI', '2025-12')},
      {'2025-10_obs': None, '2025-11_obs': '在场', '2025-12_obs': '在场'},
      mv('CPI', '2025-10') is None and mv('CPI', '2025-11') is not None and mv('CPI', '2025-12') is not None,
      'from_to "最新2026-10缺2025-10基期" / SCN1 "2026-11 起同比不受此缺基期影响"')
P.add(S1, 'CPI 同比 2026-02→2026-03 增量(受审稿无数字, 仅直算登记)', round(y['2026-03'] - y['2026-02'], 2), '同月大幅跳升(无数字)', 'NA', where='turnings[0] "2026-03 同月大幅跳升"')
cc = {'2026-02': 2.47, '2026-05': 2.82}
for ym, e in cc.items():
    chk(S1, 'snapshot.series_store.CORE_CPI 同比 %s' % ym, round(yl('CORE_CPI', ym), 2), e, 'TR1.step1')
c5 = yl('CORE_CPI', '2026-05'); c8 = yl('CORE_CPI', '2026-08')
chk(SM, 'CORE_CPI 同比 2026-05→2026-08 四位小数端点差', round(round(c8, 4) - round(c5, 4), 4), -0.3767, 'quality_gate_notes ⑧(显示层舍入)')
chk(SM, 'CORE_CPI 同比 2026-05→2026-08 未舍入差', round(c8 - c5, 4), -0.3768, 'quality_gate_notes ⑧(未舍入差)')
pce = {'2025-08': 2.85, '2026-05': 3.16, '2026-06': 3.04, '2026-07': 3.00, '2026-09': 3.12}
for ym, e in pce.items():
    chk(S1, 'snapshot.series_store.CORE_PCE 同比 %s' % ym, round(yl('CORE_PCE', ym), 2), e, 'US from_to / M1.step1')
yp = {k: yl('CORE_PCE', k) for k in sorted(F.monthly('CORE_PCE'))}
after = {k: v for k, v in yp.items() if '2026-06' <= k <= '2026-10'}
chk_txt(S1, 'CORE_PCE 同比 2026-05 为高点且其后未再越过', {'max_2026-05..10': max(yp[k] for k in yp if '2026-05' <= k <= '2026-10'),
      'max_after_2026-05': (max(after, key=after.get), round(max(after.values()), 2))},
      {'max_2026-05..10': round(yp['2026-05'], 2), 'not_exceeded': True},
      yp['2026-05'] >= max(yp[k] for k in yp if '2026-05' <= k <= '2026-10') and max(after.values()) < yp['2026-05'],
      '"2026-05 见顶后回落、未再越过高点"')
ind = {'2025-08': 1.19, '2025-11': 1.7543, '2026-02': 0.7972, '2026-03': 0.69, '2026-07': 1.25, '2026-10': 2.15}
for ym, e in ind.items():
    chk(S1, 'snapshot.series_store.INDPRO 同比 %s' % ym, round(yl('INDPRO', ym), 4), e, 'US from_to / turnings[1]')
yi = {k: v for k, v in ((k, yl('INDPRO', k)) for k in F.monthly('INDPRO')) if '2025-11' <= k <= '2026-10' and v is not None}
lo = min(yi, key=yi.get)
chk_txt(S6, 'INDPRO 同比 12 个月窗低点月', {'min_month': lo, 'value': round(yi[lo], 2)}, {'min_month': '2026-03', 'value': 0.69},
      lo == '2026-03' and P.eq(yi[lo], 0.69), 'turnings[1] "序列同比低点为 2026-03 的 0.69"')
un = {'2025-09': 4.4, '2026-07': 4.1, '2026-10': 4.1}
for ym, e in un.items():
    chk(S1, 'snapshot.series_store.UNEMPLOYMENT %s' % ym, mv('UNEMPLOYMENT', ym), e, 'US from_to')

# ---------------- 欧元区 HICP ----------------
hicp = {'2025-10': 2.1, '2026-01': 1.7, '2026-02': 1.9, '2026-04': 3.0, '2026-05': 3.2, '2026-06': 2.8, '2026-07': 2.9,
        '2026-08': 3.2, '2026-10': 4.0}
for ym, e in hicp.items():
    chk(S1, 'snapshot.series_store.EA_HICP_YOY %s' % ym, mv('EA_HICP_YOY', ym), e, 'EA from_to / M1.step1-2 / turnings[0]')
h = F.monthly('EA_HICP_YOY')
hw = {k: v for k, v in h.items() if '2025-11' <= k <= '2026-10'}
chk_txt(S6, 'HICP 12 个月窗低点月', min(hw, key=hw.get), '2026-01', min(hw, key=hw.get) == '2026-01', 'turnings[0] "欧元区 HICP 低点在 2026-01"')
inc = {'07': round(h['2026-07'] - h['2026-06'], 1), '08': round(h['2026-08'] - h['2026-07'], 1), '09': round(h['2026-09'] - h['2026-08'], 1),
       '10': round(h['2026-10'] - h['2026-09'], 1)}
chk(S1, 'HICP 月度增量 2026-07', inc['07'], 0.1, 'EA from_to "7月的 +0.1"')
chk(S1, 'HICP 月度增量 2026-08/09/10', [inc['08'], inc['09'], inc['10']], [0.3, 0.6, 0.2], 'EA from_to "2026-08至10月度增量 +0.3/+0.6/+0.2"')
mono = all(h[k] < h[L.add_months(k, 1)] for k in ('2026-01', '2026-02', '2026-03', '2026-04'))
chk_txt(S1, 'HICP 2026-01→2026-05 连续上行', mono, '连续上行', mono, 'EA from_to "自2026-01低点1.7连续上行至2026-05的3.2"')
incs = [round(h[L.add_months(k, 1)] - h[k], 1) for k in ('2025-12', '2026-01', '2026-02', '2026-03', '2026-04')]
chk_txt(S1, 'HICP 月度增量 2025-12→2026-01 … 2026-04→2026-05', incs, [-0.3, 0.2, 0.7, 0.4, 0.2], incs == [-0.3, 0.2, 0.7, 0.4, 0.2], 'EA from_to "2026-03起加速"(2026-02→03 跃升 0.7, 其前增量 -0.3/+0.2)')
h36 = {k: v for k, v in h.items() if '2023-11' <= k <= '2026-10'}
ge = [k for k in sorted(h) if k < '2026-10' and h[k] >= h['2026-10']]
chk_txt(S1, 'HICP 2026-10=4.0 为近 36 个月(2023-11..2026-10)最高; 此前最后一次 >=4.0 的月份',
      {'max_36m': max(h36.values()), 'argmax_36m': max(h36, key=h36.get), 'last_ge_4.0_before': (ge[-1] if ge else None), 'window_max': max(hw.values())},
      {'max_36m': 4.0, 'argmax_36m': '2026-10', 'window_max': 4.0},
      max(h36, key=h36.get) == '2026-10' and max(hw.values()) == 4.0, 'C1 "EA_HICP_YOY 升至本轮最高"')

# ---------------- 中国 PPI / CPI / PMI ----------------
ppi = {'2025-10': -2.1, '2026-02': -0.9, '2026-05': 3.9, '2026-06': 4.1, '2026-07': 3.5, '2026-10': 5.7}
for ym, e in ppi.items():
    chk(S1, 'snapshot.series_store.CN_PPI_YOY %s' % ym, mv('CN_PPI_YOY', ym), e, 'CN from_to / M1.step1 / turnings[0]')
pp = F.monthly('CN_PPI_YOY')
pw = {k: v for k, v in pp.items() if '2025-11' <= k <= '2026-10'}
chk_txt(S6, 'CN_PPI_YOY 12 个月窗低点月', min(pw, key=pw.get), '2025-11', min(pw, key=pw.get) == '2025-11', 'turnings[0] "中国 PPI 低点在 2025-11"')
decl = [k for k in sorted(pw) if k > '2025-11' and pw[k] < pw[L.add_months(k, -1)]]
chk_txt(S6, 'CN_PPI_YOY 自 2025-11 低点至 2026-10 的回落月', decl, ['2026-07'], decl == ['2026-07'], 'turnings[0] "其间仅 2026-07 由 4.1 回落至 3.5"')
ge = [k for k in sorted(pp) if k < '2026-10' and pp[k] >= pp['2026-10']]
neg = [k for k in sorted(pp) if '2021-01' <= k <= '2026-10' and pp[k] < 0]
trough = min((pp[k], k) for k in pp if '2023-01' <= k <= '2025-12')
chk_txt(S1, 'CN_PPI_YOY 2026-10=5.7 为本轮新高(上一次 >=5.7 的月份; 2023 年以来最低)',
      {'last_ge_5.7_before': (ge[-1] if ge else None), 'trough_since_2023': [trough[1], trough[0]], 'window_max': max(pw.values())},
      {'last_ge_5.7_before': '<2023-01', 'trough_since_2023': '深负值', 'window_max': 5.7},
      (not ge or ge[-1] < '2023-01') and max(pw.values()) == 5.7, 'C1 "CN_PPI_YOY 自负转正并续创本轮新高" / C3 "自深负值区间升至本轮高点"')
ccpi = {'2025-10': 0.2, '2026-07': 0.5, '2026-10': 0.7}
for ym, e in ccpi.items():
    chk(S1, 'snapshot.series_store.CN_CPI_YOY %s' % ym, mv('CN_CPI_YOY', ym), e, 'CN from_to')
rng = [mv('CN_CPI_YOY', k) for k in ('2026-02', '2026-03', '2026-04', '2026-05')]
chk_txt(S1, 'CN_CPI_YOY 2026-02..05 同窗区间', [min(rng), max(rng)], [1.0, 1.3], min(rng) >= 1.0 and max(rng) <= 1.3, '"中国CPI同比同窗持平于一点零至一点三"')
sw = {'US_CPI': round(max(v for k, v in y.items() if '2025-11' <= k <= '2026-09') - min(win.values()), 2),
      'EA_HICP': round(max(hw.values()) - min(hw.values()), 2),
      'CN_PPI': round(max(pw.values()) - min(pw.values()), 2),
      'CN_PPI_since_trough': round(max(pw.values()) - trough[0], 2),
      'JP_CPI': round(max(F.monthly('JP_CPI_YOY').get(k, -99) for k in pw) - min(F.monthly('JP_CPI_YOY').get(k, 99) for k in pw), 2)}
chk_txt(S1, '四地 12 个月窗价格摆动(最高-最低)', sw, {'largest': 'CN_PPI'}, sw['CN_PPI'] > sw['US_CPI'] and sw['CN_PPI'] > sw['EA_HICP'] and sw['CN_PPI'] > sw['JP_CPI'],
      'C3 "四大经济体最大价格摆动" / CN from_to "为四地最大价格摆动"')
pm = F.monthly('CN_PMI_MFG')
pmv = {'2025-10': 49.0, '2026-07': 49.2, '2026-10': 49.3}
for ym, e in pmv.items():
    chk(S1, 'snapshot.series_store.CN_PMI_MFG %s' % ym, pm[ym], e, 'CN from_to')
pmy = {'2025-10': -2.2, '2026-07': -0.2, '2026-10': 0.6}
for ym, e in pmy.items():
    chk(S1, 'CN_PMI_MFG 指数水平同比 %s' % ym, round(yl('CN_PMI_MFG', ym), 1), e, 'CN from_to "同比口径…-2.2→-0.2→0.6%"')
ptdiff = {'2025-10': round(pm['2025-10'] - pm['2024-10'], 1), '2026-07': round(pm['2026-07'] - pm['2025-07'], 1), '2026-10': round(pm['2026-10'] - pm['2025-10'], 1)}
chk(S1, 'CN_PMI_MFG 同月指数点差', [ptdiff['2025-10'], ptdiff['2026-07'], ptdiff['2026-10']], [-1.1, -0.1, 0.3], 'CN from_to "相差约 -1.1、-0.1、+0.3 个指数点"')
pw_ = {k: v for k, v in pm.items() if '2025-11' <= k <= '2026-10'}
above = sorted(k for k, v in pw_.items() if v > 50.0)
chk_txt(S1, 'CN_PMI_MFG 2025-11..2026-10 站上荣枯线的月份', above, ['2025-12', '2026-03', '2026-04', '2026-06', '2026-09'], above == ['2025-12', '2026-03', '2026-04', '2026-06', '2026-09'], 'C1 "共五个月站上荣枯线"')
chk(S1, 'CN_PMI_MFG 五个月读数', [pm[k] for k in above], [50.1, 50.4, 50.3, 50.3, 50.1], 'CN from_to "(50.1/50.4/50.3/50.3/50.1)"')
rest = sorted(v for k, v in pw_.items() if k not in above)
chk_txt(S1, 'CN_PMI_MFG 其余月份: 2026-05 持平于 50.0; 余在 49.0–49.8', {'2026-05': pm['2026-05'], 'others_min': min(v for k, v in pw_.items() if k not in above and k != '2026-05'),
      'others_max': max(v for k, v in pw_.items() if k not in above and k != '2026-05')},
      {'2026-05': 50.0, 'others_min': 49.0, 'others_max': 49.8}, pm['2026-05'] == 50.0 and 49.0 <= min(v for k, v in pw_.items() if k not in above and k != '2026-05') and max(v for k, v in pw_.items() if k not in above and k != '2026-05') <= 49.8,
      'C1 / CN from_to')
chk(S6, 'CN_PMI_MFG 候选窗 2026-02→2026-05 同比(引擎候选面原值)', [round(yl('CN_PMI_MFG', '2026-02'), 4), round(yl('CN_PMI_MFG', '2026-05'), 4)], [-2.3904, 1.0101], 'turnings[1]')

# ---------------- 日本 CPI / 东京 CPI / 政策利率 ----------------
jc = F.monthly('JP_CPI_YOY')
jcv = {'2025-01': 4.03, '2025-11': 2.9, '2025-12': 2.13, '2026-01': 1.51, '2026-02': 1.27, '2026-03': 1.46, '2026-04': 1.38,
       '2026-07': 1.97, '2026-10': 2.44, '2025-10': 2.99}
for ym, e in jcv.items():
    chk(S1, 'snapshot.series_store.JP_CPI_YOY %s' % ym, jc[ym], e, 'JP from_to / turnings[2] / M1.step2')
r = {'2025-09': round(jc['2025-09'] - jc['2025-08'], 2), '2025-10': round(jc['2025-10'] - jc['2025-09'], 2)}
chk_txt(S1, '日本CPI 2025-09、2025-10 小幅回升(月度增量)', r, {'2025-09': '>0', '2025-10': '>0'}, r['2025-09'] > 0 and r['2025-10'] > 0 and r['2025-09'] <= 0.5 and r['2025-10'] <= 0.5, 'turnings[2]')
mono_down = all(jc[k] > jc[L.add_months(k, 1)] for k in ('2025-11', '2025-12', '2026-01'))
chk_txt(S6, '日本CPI 2025-11→2026-02 逐月下行', mono_down, True, 'turnings[2] "月末路径 2.9→2.13→1.51→1.27"')
jw = {k: v for k, v in jc.items() if '2025-11' <= k <= '2026-10'}
chk_txt(S6, '日本CPI 12 个月窗低点', min(jw, key=jw.get), '2026-02', min(jw, key=jw.get) == '2026-02', 'turnings[2] "2026-02 低点 1.27"')
rise_from = [k + '→' + L.add_months(k, 1) for k in ('2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08', '2026-09') if jc[L.add_months(k, 1)] <= jc[k]]
chk_txt(S6, '日本CPI 2026-03..2026-10 中未逐月上行的月份间隔', rise_from, ['2026-03→2026-04'], rise_from == ['2026-03→2026-04'], 'turnings[2] "持续回升自 2026-05 起" / supplement "回升起点(2026-03)"')
tk = F.monthly('JP_CPI_TOKYO_YOY')
for ym, e in {'2026-06': 1.6, '2026-07': 1.85, '2026-08': 1.9, '2026-09': 2.69, '2026-10': 2.73}.items():
    chk(S1, 'snapshot.series_store.JP_CPI_TOKYO_YOY %s' % ym, tk[ym], e, 'JP from_to / turning_supplement')
chk_txt(S11, 'JP_CPI_TOKYO_YOY 首个观测月(12个月前锚 2025-11-23 前无已发布观测)', F.first('JP_CPI_TOKYO_YOY'), ('2026-01-01', 1.6), F.first('JP_CPI_TOKYO_YOY')[0] == '2026-01-01', 'JP from_to')
jr = F.monthly('JP_POLICY_RATE')
for ym, e in {'2025-10': 0.477, '2025-11': 0.478, '2025-12': 0.557, '2026-07': 0.978, '2026-10': 1.227}.items():
    chk(S4, 'snapshot.series_store.JP_POLICY_RATE 月均 %s' % ym, jr[ym], e, 'JP from_to / M2.step1')
steps = [(L.add_months('2025-11', i), round((jr[L.add_months('2025-11', i)] - jr[L.add_months('2025-11', i - 1)]) * 100, 1)) for i in range(1, 12)]
print('JP_POLICY_RATE 步进(bp):', steps)
chk(S4, 'JP_POLICY_RATE 月度步进(bp) 2025-12..2026-10', [s for _, s in steps], [7.9, 17.1, 0.0, 0.0, -0.1, 0.0, 11.4, 13.7, -0.1, 6.6, 18.4],
      'M2.step1 "+8/+17/+11/+14/+7/+18; 2026-04 与 2026-08 各约0.1bp"')
steps_round = [int(round(s)) if abs(s) >= 0.5 else 0 for s in (x for _, x in steps)]
chk_txt(S4, 'JP_POLICY_RATE 步进(取整bp, 舍入步记0)', steps_round, [8, 17, 0, 0, 0, 0, 11, 14, 0, 7, 18], steps_round == [8, 17, 0, 0, 0, 0, 11, 14, 0, 7, 18], 'M2.step1')
chk(S4, 'JP_POLICY_RATE 窗内净变动 2025-11→2026-10 (bp, 取整)', round((jr['2026-10'] - jr['2025-11']) * 100), 75, 'JP from_to "净 +75 个基点"(0.478→1.227=74.9bp)')
chk(S4, 'JP_POLICY_RATE 自 2025-12 起 (bp)', round((jr['2026-10'] - jr['2025-12']) * 100, 1), 67.0, 'JP from_to "自 2025-12 月均 0.557 起 +67bp"')
first_in_win = min(k for k in jr if F.at('JP_POLICY_RATE', k + '-01') is not None and k + '-01' > '2025-11-19')
chk_txt(S4, 'JP_POLICY_RATE 窗内(>2025-11-19)首个观测月', first_in_win, '2025-12', first_in_win == '2025-12', 'quality_gate_notes "自窗内首个观测起算的另一口径 +67bp"')

# ---------------- 中国政策面 ----------------
chk_txt(S4, 'CN_OMO_7D 末观测/滞后天数/三锚值', {'last': F.last('CN_OMO_7D'), 'lag_days': L.days(F.last('CN_OMO_7D')[0], '2026-11-23'),
      'distinct': sorted(set(F.ss['CN_OMO_7D']['values'])), 'after_last': [d for d in F.ss['CN_OMO_7D']['dates'] if d > '2026-10-30']},
      {'last': ('2026-10-30', 1.4), 'lag_days': 24, 'distinct': [1.4], 'after_last': []},
      F.last('CN_OMO_7D') == ('2026-10-30', 1.4) and L.days('2026-10-30', '2026-11-23') == 24 and sorted(set(F.ss['CN_OMO_7D']['values'])) == [1.4],
      'CN from_to "末观测2026-10-30滞后24天" / C1 "其后缺观测"')
for a, lab, eobs in (('2025-11-23', '12个月前', '2025-11'), ('2026-08-23', '3个月前', '2026-08'), ('2026-11-23', '最新', '2026-10')):  # [rc16] expected=受审稿所写观测月(比对口径=观测月+数值, 结论不变)
    v = F.at_or_before('CN_OMO_7D', a)
    chk_txt(S4, 'CN_OMO_7D 锚日前最近观测 %s' % lab, (v[0], v[1]) if v else None, (eobs, 1.4), v is not None and P.eq(v[1], 1.4) and v[0][:7] == eobs[:7], 'CN from_to "7天逆回购利率 1.4→1.4→1.4(观测 2025-11→2026-08→2026-10)"')
po = F.series('CN_POLICY_OVERNIGHT')
chk_txt(S4, 'CN_POLICY_OVERNIGHT 首观测/末观测/取值', {'first': po[0], 'last': po[-1], 'distinct': sorted(set(v for _, v in po)), 'n': len(po)},
      {'first': ('2026-11-02', 1.25), 'last': ('2026-11-23', 1.25), 'distinct': [1.25]},
      po[0] == ('2026-11-02', 1.25) and po[-1] == ('2026-11-23', 1.25) and sorted(set(v for _, v in po)) == [1.25],
      'CN from_to "隔夜逆回购利率…最新 1.25@2026-11-23(持平于首个观测值)" / quality_gate_notes ②')
chk_txt(S11, 'CN_POLICY_OVERNIGHT 在 12个月前/3个月前锚日前无观测', [F.at_or_before('CN_POLICY_OVERNIGHT', a) for a in ('2025-11-23', '2026-08-23')],
      [None, None], all(F.at_or_before('CN_POLICY_OVERNIGHT', a) is None for a in ('2025-11-23', '2026-08-23')), 'CN from_to "12个月前与3个月前锚日前无已发布观测"')
for a, e in (('2025-11-23', ('2025-11-20', 3.0)), ('2026-08-23', ('2026-08-20', 3.0)), ('2026-11-23', ('2026-11-20', 3.0))):
    v = F.at_or_before('CN_LPR_1Y', a)
    chk_txt(S4, 'CN_LPR_1Y 锚日前最近观测 %s' % a, v, e, v is not None and P.eq(v[1], 3.0), 'CN from_to "LPR_1Y 3.0→3.0→3.0(观测 2025-11→2026-08→2026-11)"')
lpr_w = [(d, v) for d, v in F.series('CN_LPR_1Y') if '2025-11-19' <= d <= '2026-11-23']
chk_txt(S4, 'CN_LPR_1Y 窗内取值集合(窗内持平)', sorted(set(v for _, v in lpr_w)), [3.0], sorted(set(v for _, v in lpr_w)) == [3.0], 'CN from_to "窗内持平"')

# ---------------- 欧央行 / 美联储 ----------------
d = F.series('ECB_DFR'); m = F.series('ECB_MRO')
chg = [(d[i][0], d[i - 1][1], d[i][1]) for i in range(1, len(d)) if d[i][1] != d[i - 1][1] and d[i][0] >= '2025-11-19']
chgw = [(d[i][0], d[i - 1][1], d[i][1]) for i in range(1, len(d)) if d[i][1] != d[i - 1][1] and d[i][0] >= '2025-06-01']
print('ECB_DFR change points since 2025-06:', chgw, 'in window:', chg)
chk_txt(S4, 'ECB_DFR 窗内(>=2025-11-19)变动点', chg, [('2026-06-17', 2.0, 2.25), ('2026-09-16', 2.25, 2.5)], chg == [('2026-06-17', 2.0, 2.25), ('2026-09-16', 2.25, 2.5)], 'M1.step2 / EA from_to')
chgm = [(m[i][0], m[i - 1][1], m[i][1]) for i in range(1, len(m)) if m[i][1] != m[i - 1][1] and m[i][0] >= '2025-11-19']
chk_txt(S4, 'ECB_MRO 窗内变动点', chgm, [('2026-06-17', 2.15, 2.4), ('2026-09-16', 2.4, 2.65)], chgm == [('2026-06-17', 2.15, 2.4), ('2026-09-16', 2.4, 2.65)], 'EA from_to "主要再融资利率 2.15→2.65"')
for a, e in (('2025-11-23', 2.0), ('2026-08-23', 2.25), ('2026-11-23', 2.5)):
    v = F.at_or_before('ECB_DFR', a)
    chk_txt(S4, 'ECB_DFR 锚日前最近观测 %s' % a, v[1] if v else None, e, v is not None and P.eq(v[1], e), 'EA from_to "存款便利利率 2.0→2.25→2.5"')
chk_txt(S4, 'ECB_DFR 窗启时在值(2025-11-19)', F.at_or_before('ECB_DFR', '2025-11-19'), ('2025-06-11', 2.0), F.at_or_before('ECB_DFR', '2025-11-19') == ('2025-06-11', 2.0), 'EA from_to "窗启时在值 2.0，2025-06-11 起生效"')
chk_txt(S4, 'ECB_DFR 自窗内首个观测起算净变动(bp)', round((d[-1][1] - [x for x in d if x[0] > '2025-11-19'][0][1]) * 100, 1), 25.0, P.eq(round((d[-1][1] - [x for x in d if x[0] > '2025-11-19'][0][1]) * 100, 1), 25.0), 'EA from_to "另一口径为 +25bp"')
chk_txt(S4, 'ECB 两条序列末观测与滞后', {'DFR': F.last('ECB_DFR'), 'MRO': F.last('ECB_MRO'), 'lag': L.days('2026-09-16', '2026-11-23')},
      {'DFR': ('2026-09-16', 2.5), 'MRO': ('2026-09-16', 2.65), 'lag': 68}, F.last('ECB_DFR') == ('2026-09-16', 2.5) and F.last('ECB_MRO') == ('2026-09-16', 2.65) and L.days('2026-09-16', '2026-11-23') == 68,
      'EA from_to "止于 2026-09-16(滞后68天)"')
wd = {k: L.weekday(k) for k in ('2025-12-10', '2025-12-11', '2026-06-11', '2026-06-17', '2026-09-10', '2026-09-16', '2026-09-17', '2026-09-18', '2026-09-24', '2026-10-30', '2026-11-23', '2026-11-20', '2026-11-19', '2026-10-23', '2026-06-13', '2026-09-13', '2026-08-30', '2026-05-13', '2026-08-13', '2026-05-16', '2026-08-16', '2026-08-20', '2026-09-29', '2026-08-31', '2026-06-10', '2026-02-27', '2026-05-04', '2026-10-30', '2025-05-09', '2025-04-07', '2025-11-13')}
print('weekday (1=Mon..7=Sun):', wd)
chk_txt(S4, '决议日=生效日惯例核对(星期)', {'2025-12-10': wd['2025-12-10'], '2025-12-11': wd['2025-12-11'], '2026-09-16': wd['2026-09-16'], '2026-09-17': wd['2026-09-17'],
      '2026-06-11': wd['2026-06-11'], '2026-06-17': wd['2026-06-17'], '2026-09-10': wd['2026-09-10'], '2026-09-16': wd['2026-09-16'],
      '2026-09-18': wd['2026-09-18'], '2026-09-24': wd['2026-09-24']},
      {'Fed 决议=生效前一日': '12-10→12-11 / 09-16→09-17', 'ECB 决议=生效前上一个周四': '06-11(周四)→06-17(周三) / 09-10(周四)→09-16(周三)', 'BOJ': '09-18→09-24'},
      L.days('2025-12-10', '2025-12-11') == 1 and L.days('2026-09-16', '2026-09-17') == 1 and wd['2026-06-17'] == 3 and wd['2026-06-11'] == 4
      and L.shift_days('2026-06-17', -3) == '2026-06-14' and L.shift_days('2026-06-14', -3) == '2026-06-11' and wd['2026-09-16'] == 3 and wd['2026-09-10'] == 4
      and L.days('2026-09-10', '2026-09-16') == 6 and L.days('2026-06-11', '2026-06-17') == 6 and L.days('2026-09-18', '2026-09-24') == 6,
      'M1.step2 / EA from_to / 证伪面(决议日回推惯例)')
chk_txt(SM, '发布规则值的星期(6-13 星期六 / 9-13 星期日 / 8-30 星期日)', {'2026-06-13': wd['2026-06-13'], '2026-09-13': wd['2026-09-13'], '2026-08-30': wd['2026-08-30']},
      {'2026-06-13': '星期六', '2026-09-13': '星期日', '2026-08-30': '星期日'}, wd['2026-06-13'] == 6 and wd['2026-09-13'] == 7 and wd['2026-08-30'] == 7,
      'M1.step2 / turning_supplement')
for mtr, obs, e in (('CPI', '2026-04', '2026-05-13'), ('CPI', '2026-07', '2026-08-13'), ('CPI', '2026-08', '2026-09-13'), ('CPI', '2026-05', '2026-06-13'),
                    ('CORE_PCE', '2026-07', '2026-08-30'), ('EA_HICP_YOY', '2026-04', '2026-05-16'), ('EA_HICP_YOY', '2026-07', '2026-08-16'),
                    ('EA_HICP_YOY', '2026-08', '2026-09-16'), ('JP_CPI_YOY', '2026-07', '2026-08-20'), ('JP_CPI_TOKYO_YOY', '2026-09', '2026-09-29'),
                    ('JP_CPI_TOKYO_YOY', '2026-08', '2026-08-30')):
    rd = L.release_date(F, mtr, obs + '-01')[0]
    chk(SM, '发布规则 %s 观测 %s' % (mtr, obs), rd, e, 'M1.step2 / turning_supplement "推定发布"')
# 决议时点可见 CPI
for asof, e_obs, e_val in (('2026-06-11', '2026-04-01', 3.78), ('2026-09-10', '2026-07-01', 3.30), ('2026-09-16', '2026-08-01', 3.35), ('2026-09-18', '2026-08-01', 3.35)):
    v = L.visible_latest(F, 'CPI', asof)
    chk_txt(S4, 'CPI 决议时点(发布纪律)最近可见观测 %s' % asof, {'obs': v['obs_date'], 'yoy': round(yl('CPI', v['obs_date'][:7]), 2), 'pub': v['pub_date']},
          {'obs': e_obs, 'yoy': e_val}, v['obs_date'] == e_obs and P.eq(round(yl('CPI', v['obs_date'][:7]), 2), e_val), 'M1.step2')
for mtr, asof, e_obs, e_val in (('CORE_PCE', '2026-09-16', '2026-07-01', 3.00), ('EA_HICP_YOY', '2026-06-11', '2026-04-01', 3.0),
                                ('EA_HICP_YOY', '2026-09-10', '2026-07-01', 2.9), ('JP_CPI_YOY', '2026-09-18', '2026-07-01', 1.97),
                                ('JP_CPI_TOKYO_YOY', '2026-09-18', '2026-08-01', 1.9)):
    v = L.visible_latest(F, mtr, asof)
    val = round(yl('CORE_PCE', v['obs_date'][:7]), 2) if mtr == 'CORE_PCE' else v['value']
    chk_txt(S4, '%s 决议时点(发布纪律)最近可见观测 %s' % (mtr, asof), {'obs': v['obs_date'], 'value': val, 'pub': v['pub_date']},
          {'obs': e_obs, 'value': e_val}, v['obs_date'] == e_obs and P.eq(val, e_val), 'M1.step2 / turning_supplement')
fu = F.series('DFEDTARU'); ff = F.series('DFF')
chgf = [(fu[i][0], fu[i - 1][1], fu[i][1]) for i in range(1, len(fu)) if fu[i][1] != fu[i - 1][1] and fu[i][0] >= '2025-11-19']
chk_txt(S4, 'DFEDTARU 窗内(>=2025-11-19)变动点', chgf, [('2025-12-11', 4.0, 3.75), ('2026-09-17', 3.75, 4.0)], chgf == [('2025-12-11', 4.0, 3.75), ('2026-09-17', 3.75, 4.0)], 'US from_to')
pre = F.at_or_before('DFF', '2025-12-10')
chk_txt(S4, 'DFF 2025-12 降息前台阶(2025-12-10 当日或之前)', pre, ('2025-12-10', 3.89), pre is not None and 3.87 <= pre[1] <= 3.89, 'C1 "DFF 回到 2025-12 降息前的台阶附近(现 3.88)"')
chk_txt(S4, 'DFEDTARU 按(含)锚日填充 2025-11-23/2026-08-23/2026-11-23', [F.at('DFEDTARU', k) for k in ('2025-11-23', '2026-08-23', '2026-11-23')], [4.0, 3.75, 4.0],
      [F.at('DFEDTARU', k) for k in ('2025-11-23', '2026-08-23', '2026-11-23')] == [4.0, 3.75, 4.0], 'US from_to 渲染注记')
print('DFEDTARU obs dates near anchors:', [(k, F.at('DFEDTARU', k)) for k in ('2025-11-22', '2025-11-23', '2025-11-24', '2026-08-22', '2026-08-23', '2026-08-24')])
print('DFF anchors:', [F.at_or_before('DFF', k) for k in ('2025-11-23', '2026-08-23', '2026-11-23')])

# ---------------- 冻结日历: BOJ 实录 / 版本 ----------------
print('calendar version:', cal.get('version'), 'n entries', len(cal['entries']))
boj = [e for e in cal['entries'] if 'JP_POLICY' in json.dumps(e) or 'BOJ' in json.dumps(e, ensure_ascii=False) or '日本' in json.dumps(e, ensure_ascii=False)]
for e in boj:
    print('BOJ entry:', json.dumps(e, ensure_ascii=False)[:600])
fedcal = [e for e in cal['entries'] if 'FOMC' in json.dumps(e, ensure_ascii=False) or '美联储' in json.dumps(e, ensure_ascii=False) or 'DFEDTAR' in json.dumps(e)]
ecbcal = [e for e in cal['entries'] if 'ECB' in json.dumps(e, ensure_ascii=False) or '欧央行' in json.dumps(e, ensure_ascii=False)]
print('Fed calendar entries:', len(fedcal), [ (e.get('entry_id'), e.get('decision_date'), e.get('obs_from')) for e in fedcal][:12])
print('ECB calendar entries:', len(ecbcal), [(e.get('entry_id'), e.get('decision_date'), e.get('obs_from')) for e in ecbcal][:12])
gdp = [e for e in cal['entries'] if 'US_REAL_GDP' in (e.get('metric_ids') or [e.get('metric_id')]) and (e.get('obs_from') or '').startswith('2025-07')]
for e in gdp:
    print('US GDP Q3-2025 entry:', json.dumps(e, ensure_ascii=False)[:500])

# ---------------- 序列库结构: 诚实缺席 ----------------
keys = sorted(F.ss.keys())
print('n series', len(keys))
chk_txt(S11, 'series_store 不含 JGB 收益率历史序列', [k for k in keys if 'JGB' in k], [], len([k for k in keys if 'JGB' in k]) == 0, 'M2.step1 "JGB 收益率历史序列不在引擎(单点观测)"')
chk_txt(S11, 'series_store 不含中国利率预期/资本流动序列', [k for k in keys if k.startswith('CN_')], 'no CN rate-expectation / capital-flow series',
      not any(('CN' in k and ('EXPECT' in k or 'OIS' in k or 'FLOW' in k.upper() and k != 'CN_SF_FLOW')) for k in keys), 'C3 "引擎面无中国利率预期序列…无中国资本流动序列"')
chk_txt(SM, 'CN_NEW_LOANS 最新观测月', F.last('CN_NEW_LOANS')[0][:7], '2026-10', F.last('CN_NEW_LOANS')[0][:7] == '2026-10', 'C3')
chk_txt(S11, 'JP_POLICY_TARGET 不在序列库', 'JP_POLICY_TARGET' in F.ss, False, 'JP_POLICY_TARGET' not in F.ss, 'JP from_to "计划指标 JP_POLICY_TARGET 不在注册表"')
jgbfacts = [f for f in snap.get('facts', []) if 'JGB' in json.dumps(f, ensure_ascii=False)]
print('JGB facts:', [(f.get('fact_id'), f.get('value'), f.get('date') or f.get('as_of')) for f in jgbfacts])
hy = F.series('HY_OAS')
hy_at_c = [x for x in hy if x[0] <= '2025-03-31']
chk_txt(S8, 'HY_OAS 截至 2025-03-31 的月度观测数(候选月 2025-03)', len(set(d[:7] for d, _ in hy_at_c)), 17, len(set(d[:7] for d, _ in hy_at_c)) == 17, 'history_periods[0].difference "HY序列历史17个月<36"')
chk_txt(S8, 'HY_OAS 首个观测日(2022-06/2023-10 候选月无 HY 观测)', hy[0][0], '>2023-10', hy[0][0] > '2023-10-31', 'history_periods[1..2].difference "信用维候选月无HY观测"')
print('tally', P.tally())
