# -*- coding: utf-8 -*-
"""rc09: 日频取值 / 利率三分解 / HY_OAS / 布伦特 / 情景阈值 / 证据引用 / 历史类比面(引擎事后块基点直算+月末口径+符号一致率+差异清单完整性)。
用法: /usr/bin/python3 -I rc09_daily_analog.py <snapshot.json> <run_dir>
"""
import sys, os, json, math, re, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_lib as L
import rc_points as P

snap = L.load(sys.argv[1]); RUN = sys.argv[2]
F = L.Face(snap)
rep = L.load(os.path.join(RUN, 'report.json'))
aj = L.load(os.path.join(RUN, 'agent_judgment.json'))
evi = L.load(os.path.join(RUN, 'evidence_index.json'))
S5 = '⑤三利率分解/资产窗'; S7 = '⑦传导环数字'; S9 = '⑨情景阈值/期限'; S8 = '⑧历史类比面'; S12 = '⑫时点标注'; SM = '杂项(引用/日历/结构)'


_add = P.add


def add9(section, src, computed, reported, ok, note='', where=''):
    _add(section, src, computed, reported, ok, note='[rc09] ' + note, where=where)


P.add = add9  # 本脚本全部记录带 [rc09] 标记, 重跑前用 rc_clean_mark.py '[rc09] ' 整体撤除


def eql(comp, rep_):
    if isinstance(comp, (list, tuple)) and isinstance(rep_, (list, tuple)):
        return len(comp) == len(rep_) and all(eql(a, b) for a, b in zip(comp, rep_))
    return P.eq(comp, rep_)


def chk(section, src, comp, rep_, where):
    P.add(section, src, comp, rep_, eql(comp, rep_), where=where)


def chk_txt(section, src, comp, rep_, ok, where):
    P.add(section, src, comp, rep_, bool(ok), where=where)


def at(m, d):
    return F.at(m, d)


# ---------------- 三利率分解 ----------------
T = {m: {'2025-11-19': at(m, '2025-11-19'), '2026-10-20': at(m, '2026-10-20'), '2026-11-19': at(m, '2026-11-19'), '2026-11-20': at(m, '2026-11-20')}
     for m in ('UST_10Y', 'TIPS_10Y', 'BEI_10Y')}
print('rates', T)
chk(S5, 'series_store.UST_10Y@2025-11-19 / @2026-11-19', [T['UST_10Y']['2025-11-19'], T['UST_10Y']['2026-11-19']], [4.13, 5.04], 'M1.step3 "十年期美债名义+91bp"(端点)')
chk(S5, 'series_store.TIPS_10Y@2025-11-19 / @2026-11-19', [T['TIPS_10Y']['2025-11-19'], T['TIPS_10Y']['2026-11-19']], [1.86, 2.88], 'M1.step3 "实际(TIPS_10Y) 2.88"')
chk(S5, 'series_store.BEI_10Y@2025-11-19 / @2026-11-19 / @2026-11-20', [T['BEI_10Y']['2025-11-19'], T['BEI_10Y']['2026-11-19'], T['BEI_10Y']['2026-11-20']], [2.27, 2.16, 2.15], 'M1.step3 "BEI_10Y 2.16@2026-11-19(最新 2.15@2026-11-20)" / TR1.step2 "2.27→2.16"')
nom = round((T['UST_10Y']['2026-11-19'] - T['UST_10Y']['2025-11-19']) * 100)
real = round((T['TIPS_10Y']['2026-11-19'] - T['TIPS_10Y']['2025-11-19']) * 100)
bei = round((T['BEI_10Y']['2026-11-19'] - T['BEI_10Y']['2025-11-19']) * 100)
chk(S5, '12个月窗 2025-11-19→2026-11-19 名义/实际/盈亏平衡 (bp)', [nom, real, bei], [91, 102, -11], 'M1.step3 / TR1.step3 / C1 "名义+91bp=实际+102bp+盈亏平衡-11bp"')
chk(S5, '恒等残差 名义-实际-盈亏平衡 (bp)', nom - real - bei, 0, 'M1.step3 "恒等残差0"')
rd = aj['reader_map']['rates_decomposition']
c1 = round((T['UST_10Y']['2026-11-19'] - T['UST_10Y']['2026-10-20']) * 100)
c2 = round((T['TIPS_10Y']['2026-11-19'] - T['TIPS_10Y']['2026-10-20']) * 100)
c3 = round((T['BEI_10Y']['2026-11-19'] - T['BEI_10Y']['2026-10-20']) * 100)
chk(S5, '近1个月 2026-10-20→2026-11-19 名义/实际/盈亏平衡 (bp)', [c1, c2, c3], [rd['nominal_bp'], rd['real_bp'], rd['bei_bp']], 'reader_map.rates_decomposition(nominal_bp/real_bp/bei_bp) / TR1.step3 "实际+11个基点、盈亏平衡-19个基点"')
chk_txt(S5, 'rates_decomposition 窗口字段', [rd['window_from'], rd['window_to']], ['2026-10-20', '2026-11-19'], [rd['window_from'], rd['window_to']] == ['2026-10-20', '2026-11-19'], 'reader_map.rates_decomposition.window_from/window_to')
chk(S5, 'series_store.TIPS_10Y 2026-08-19→2026-11-19 (bp)', round((T['TIPS_10Y']['2026-11-19'] - at('TIPS_10Y', '2026-08-19')) * 100), 53, 'M1.step4 / TR1.step3 "2026-08-19→2026-11-19 +53bp"')
chk(S7, 'series_store.BEI_10Y@2026-02-27 → @2026-05-04', [at('BEI_10Y', '2026-02-27'), at('BEI_10Y', '2026-05-04')], [2.25, 2.50], 'TR1.step2 "收紧前(2026-02-27→2026-05-04)自 2.25 升至 2.50"')
chk(S7, 'series_store.BEI_10Y@2026-06-10 / @2026-10-23', [at('BEI_10Y', '2026-06-10'), at('BEI_10Y', '2026-10-23')], [2.34, 2.34], 'TR1.step2 "首次加息决议前日 2026-06-10 已回落至 2.34 / 2026-10-23 2.34"')
w = F.window('BEI_10Y', '2026-06-17', '2026-11-23')
lo = min(x[1] for x in w); hi = max(x[1] for x in w)
chk_txt(S7, 'series_store.BEI_10Y 2026-06-17..2026-11-20 区间', [lo, hi], [2.15, 2.40], eql([lo, hi], [2.15, 2.40]), 'TR1.step2 "收紧后(2026-06-17 起)区间 2.15–2.40"')
chk(S7, '日历日 2026-10-23→2026-11-20', L.days('2026-10-23', '2026-11-20'), 28, 'TR1.step2 "28 个日历日"')
chk(S7, 'series_store.VIX@2026-10-23 → @2026-11-23', [at('VIX', '2026-10-23'), at('VIX', '2026-11-23')], [19.45, 27.01], 'M1.step4 / TR1.step3 "VIX 19.45→27.01"')
# DFF 三时点锚值(受审稿括注)与变动点实际值
dffa = [at('DFF', '2025-11-22'), at('DFF', '2026-08-22'), at('DFF', '2026-11-19')]
chk(S7, 'series_store.DFF 三时点锚值 @2025-11-22/@2026-08-22/@2026-11-19', dffa, [3.88, 3.63, 3.88], 'TR1.step2 "(DFF 3.88→3.63→3.88)"')
P.add(SM, 'series_store.DFF 变动点实际值 2025-12-10→2025-12-11→2026-09-17', [at('DFF', '2025-12-10'), at('DFF', '2025-12-11'), at('DFF', '2026-09-17')], '受审稿括注 3.88→3.63→3.88', 'NA',
      note='变动点实际值 3.89→3.64→3.88; 受审稿括注与三时点锚值一致、与变动点值相差 1bp(EFFR 日度波动)', where='TR1.step2 口径注记(MINOR 候选)')

# ---------------- HY_OAS ----------------
hy = F.series('HY_OAS'); latest = hy[-1]
chk_txt(S7, 'series_store.HY_OAS 最新观测', latest, ('2026-11-19', 3.52), eql(latest, ('2026-11-19', 3.52)), 'M1.step4 / TR1.step3 "3.52pp@2026-11-19"')
mx = max(hy, key=lambda x: x[1])
chk_txt(S7, 'series_store.HY_OAS 序列高点', mx, ('2025-04-07', 4.61), eql(mx, ('2025-04-07', 4.61)), 'M1.step4 "2025-04-07 序列高点 4.61"')
vals = sorted(v for _, v in hy)
pct_le = 100.0 * sum(1 for v in vals if v <= latest[1]) / len(vals)
chk(S7, 'HY_OAS 最新读数在库内百分位(<=口径, n=%d)' % len(vals), round(pct_le), 92, 'M1.step4 "处引擎三年历史约第 92 百分位"')
ge = [x for x in hy[:-1] if x[1] >= latest[1]]
chk_txt(S7, 'HY_OAS 库内上一次不低于最新读数的观测', ge[-1] if ge else None, ('2025-05-09', 3.53), ge[-1] == ('2025-05-09', 3.53), 'M1.step4 "预警级=升破 2025-05-09 的 3.53(库内上一次不低于最新读数)" / TR1.step3 "为 2025-05-09 以来最高"')
chk(S7, 'HY_OAS 序列高点距最新读数 (bp)', round((4.61 - 3.52) * 100), 109, 'M1.step4 "距最新读数 109 个基点"')
chk(S7, 'HY_OAS 近1周 ISO周口径(基准 2026-11-13) pp', round(latest[1] - at('HY_OAS', '2026-11-13'), 2), 0.29, 'TR1.step3')
chk(S7, 'HY_OAS 严格7日口径(2026-11-12→11-19) pp', round(latest[1] - at('HY_OAS', '2026-11-12'), 2), 0.32, 'TR1.step3')
chk(S7, 'HY_OAS 近12个月(2025-11-19→2026-11-19) pp', round(latest[1] - at('HY_OAS', '2025-11-19'), 2), 0.35, 'TR1.step3')
chk_txt(S7, 'series_store.HY_OAS 序列起点', hy[0][0], '2023-11-21', hy[0][0] == '2023-11-21', 'TR1.step3 "引擎序列(自 2023-11-21 起)" / M1.step4 "三年历史"')
chk_txt(S7, 'HY_OAS 2026-11-13 为星期五(ISO周基准)', L.weekday('2026-11-13'), 5, L.weekday('2026-11-13') == 5, 'TR1.step3 "ISO 周口径，基准 2026-11-13"')
chk_txt(S7, 'HY_OAS 2026-11-19 距 2026-11-12 为 7 日', L.days('2026-11-12', '2026-11-19'), 7, L.days('2026-11-12', '2026-11-19') == 7, 'TR1.step3 "严格 7 日口径"')

# ---------------- 布伦特 ----------------
bme = {}
for d, v in F.series('BRENT_F'):
    bme[d[:7]] = (d, v)
chk(S7, 'series_store.BRENT_F 月末 2026-02 / 2026-03 / 2026-05 / 2026-06', [bme['2026-02'][1], bme['2026-03'][1], bme['2026-05'][1], bme['2026-06'][1]], [72.48, 118.35, 92.05, 72.92], 'TR1.step1 "月末 2026-02 72.48→2026-03 118.35→2026-05 92.05 / 至 2026-06 月末 72.92"')
chk(S7, 'BRENT_F 月末 2026-02→2026-05 %', round(L.pct(bme['2026-02'][1], bme['2026-05'][1]), 2), 27.00, 'TR1.step1 "首尾 +27.00%"')
gaps = [(ym, bme[ym][0], L.days(bme[ym][0], L.month_end(ym))) for ym in ('2026-02', '2026-03', '2026-05', '2026-06')]
print('BRENT 月末观测:', gaps)
chk_txt(S7, 'BRENT_F 月末口径: 各月末最后观测距自然月末天数(≤4 天=周末/节假日缺口)', max(g[2] for g in gaps), 4, max(g[2] for g in gaps) <= 4, 'TR1.step1 "月末" 口径(观测日 %s)' % gaps)
chk(S7, 'series_store.BRENT_F@2026-11-23 / @2026-10-23', [at('BRENT_F', '2026-11-23'), at('BRENT_F', '2026-10-23')], [88.19, 116.72], 'TR1.step1 "BRENT_F 水平88.19@2026-11-23 / 近30日 116.72→88.19"')
chk(S7, 'BRENT_F 当月至今(2026-10月末→2026-11-23) %', round(L.pct(bme['2026-10'][1], at('BRENT_F', '2026-11-23')), 2), -25.03, 'TR1.step1 "当月至今-25.03%"')

# ---------------- 截止日时点 / 末观测日 ----------------
last = {m: F.last(m) for m in ('SPX', 'DAX', 'CAC40', 'VIX', 'GOLD_F', 'DXY', 'BRENT_F', 'USDJPY', 'USDCNY', 'SHCOMP', 'NIKKEI225', 'UST_10Y', 'TIPS_10Y', 'BEI_10Y', 'HY_OAS', 'DFF')}
print('last obs', last)
INTRA = ('SPX', 'DAX', 'CAC40', 'VIX', 'GOLD_F', 'DXY', 'BRENT_F', 'USDJPY')
chk_txt(S12, '盘中/近24小时品种末观测日=截止日 2026-11-23', {m: last[m][0] for m in INTRA}, {m: '2026-11-23' for m in INTRA},
      all(last[m][0] == '2026-11-23' for m in INTRA), 'quality_gate_notes "SPX、DAX、CAC40、VIX 及近 24 小时交易品种(GOLD_F、DXY、BRENT_F)与外汇的当日值为盘中快照"')
chk_txt(S12, '末观测日 SHCOMP / NIKKEI225', [last['SHCOMP'][0], last['NIKKEI225'][0]], ['2026-11-23', '2026-11-20'], [last['SHCOMP'][0], last['NIKKEI225'][0]] == ['2026-11-23', '2026-11-20'], 'quality_gate_notes "NIKKEI225 止于 2026-11-20 收盘、SHCOMP 为 2026-11-23 收盘"')
chk_txt(S12, '末观测日 UST_10Y/TIPS_10Y/DFF/HY_OAS / BEI_10Y', [last['UST_10Y'][0], last['TIPS_10Y'][0], last['DFF'][0], last['HY_OAS'][0], last['BEI_10Y'][0]],
      ['2026-11-19', '2026-11-19', '2026-11-19', '2026-11-19', '2026-11-20'],
      [last[m][0] for m in ('UST_10Y', 'TIPS_10Y', 'DFF', 'HY_OAS', 'BEI_10Y')] == ['2026-11-19', '2026-11-19', '2026-11-19', '2026-11-19', '2026-11-20'], 'M1.step3 "共同交易日 2025-11-19→2026-11-19" / 口径注记')
rao = snap.get('research_as_of')
t = dt.datetime.fromisoformat(rao); utc = t.astimezone(dt.timezone.utc)
ny = utc.astimezone(dt.timezone(dt.timedelta(hours=-5))).strftime('%H:%M')
ff = utc.astimezone(dt.timezone(dt.timedelta(hours=1))).strftime('%H:%M')
tk = utc.astimezone(dt.timezone(dt.timedelta(hours=9))).strftime('%H:%M')
chk_txt(S12, 'research_as_of 换算 纽约(EST)/法兰克福(CET)/东京(JST)', [rao, ny, ff, tk], [rao, '09:53', '15:53', '23:53'], [ny, ff, tk] == ['09:53', '15:53', '23:53'], 'quality_gate_notes "纽约 09:53、法兰克福 15:53、东京 23:53、上海 22:53"')
chk_txt(S12, '截止日 2026-11-23 星期(1=周一)', L.weekday('2026-11-23'), 1, L.weekday('2026-11-23') == 1, '截止时点东京 23:53 JST 已过当日收盘; 纽约 09:53 EST 与法兰克福 15:53 CET 常规时段内')

# ---------------- 证据引用 ----------------
refs = []
for c in aj['l3']['contradictions']:
    for r in c.get('evidence_refs', []):
        refs.append((c['id'], r))
for mc in aj['l3']['mechanism_chains']:
    for lk in mc['links']:
        for r in lk.get('evidence_refs', []):
            refs.append((mc['id'] + '.' + str(lk['step']), r))
l4refs = []
for s in aj['l4']['scenarios']:
    for r in s['rows']['asset_direction'].get('evidence_refs', []):
        l4refs.append((s['id'], r))
allrefs = refs + l4refs
evset = set(x['ref'] for x in evi); factset = set(F.facts.keys())
print('L3 refs', len(refs), sorted(refs))
print('L4 refs', len(l4refs))
chk_txt(SM, 'L3 证据引用条数 / 去重项数', [len(refs), len(set(r for _, r in refs))], [41, 20], len(refs) == 41 and len(set(r for _, r in refs)) == 20, 'quality_gate_notes "L3 证据引用共 41 条"')
chk_txt(SM, 'L3+L4 证据引用条数 / 去重项数', [len(allrefs), len(set(r for _, r in allrefs))], [50, 20], len(allrefs) == 50 and len(set(r for _, r in allrefs)) == 20, 'quality_gate_notes "连同 L4 共 50 条、去重 20 项"')
chk_txt(SM, 'L3+L4 引用全部在证据索引(72行)内', sorted(r for _, r in set(allrefs) if r not in evset), [], all(r in evset for _, r in allrefs), 'evidence_refs ↔ evidence_index.json')
chk_txt(SM, 'L3+L4 引用全部在快照 facts 内', sorted(r for _, r in set(allrefs) if r not in factset), [], all(r in factset for _, r in allrefs), 'evidence_refs ↔ snapshot.facts(fact_id)')
chk_txt(SM, '证据索引行数', len(evi), 72, len(evi) == 72, 'agent_declaration / quality_gate_notes')
bad = []; monthlab = []
for _, r in sorted(set(allrefs)):
    m, d = r.split('@')
    f = F.facts.get(r)
    v = F.at(m, d)
    if v is None:
        v2 = F.at_or_before(m, d)
        monthlab.append((r, v2))
        v = v2[1] if v2 else None
    fv = f.get('value') if f else None
    if v is None or fv is None or not P.eq(v, fv):  # 容差按事实值显示精度(快照 facts 为序列值的舍入)
        bad.append((r, fv, v))
chk_txt(SM, '引用 fact 值 = series_store 同日(或同观测月内最近)观测值 逐条', bad, [], bad == [], 'snapshot.facts[*].value 回贴 series_store')
print('月末标签引用(观测日为月初):', monthlab)
ces = aj['l3']['contradictions']
ncx = [len(c.get('competing_explanations', c.get('competing', []))) for c in ces]
chk_txt(SM, '三条矛盾陈述并列解释数', ncx, [3, 2, 3], ncx == [3, 2, 3], 'quality_gate_notes "L3 三条矛盾陈述各并列 3、2、3 种解释"')
nlink = sum(len(m['links']) for m in aj['l3']['mechanism_chains'])
ntr = sum(len(c.get('links', [])) for c in aj['reader_map']['transmission'])
ntr_ok = all(lk.get('main_predicts') and lk.get('competing_predicts') and lk.get('distinguishing_metric') and lk.get('face_off_verdict') for c in aj['reader_map']['transmission'] for lk in c.get('links', []))
dms = [lk.get('distinguishing_metric') for c in aj['reader_map']['transmission'] for lk in c.get('links', [])]
vds = [lk.get('face_off_verdict') for c in aj['reader_map']['transmission'] for lk in c.get('links', [])]
print('transmission links', ntr, dms, vds)
chk_txt(SM, 'L3 机制链条数 / 链内环数(M1=4,M2=2) ; 传导面对质环数(TR1=3,TR2=1)', [len(aj['l3']['mechanism_chains']), nlink, ntr], [2, 6, 4], len(aj['l3']['mechanism_chains']) == 2 and nlink == 6 and ntr == 4, 'quality_gate_notes "传导面 4 环"')
chk_txt(SM, '传导面 4 环均给出主/竞争两侧预期+区分指标+裁定', [ntr_ok, dms], [True, ['BRENT_F', 'BEI_10Y', 'BEI_10Y', 'USDJPY']], ntr_ok is True and dms == ['BRENT_F', 'BEI_10Y', 'BEI_10Y', 'USDJPY'], 'quality_gate_notes "传导面 4 环均给出主/竞争两侧对同一区分指标的不同预期"')
chk_txt(SM, '对质裁定序列', vds, ['支持主解释', '尚不能区分', '尚不能区分', '支持竞争解释'], vds == ['支持主解释', '尚不能区分', '尚不能区分', '支持竞争解释'], 'quality_gate_notes "第1环…支持主解释、第2环与第3环…尚不能区分、竞争链第4环…支持竞争解释"')
dm_ok = all((m in F.ss) and len(F.series(m)) > 0 for m in set(dms))
chk_txt(SM, '被点名的区分指标(BRENT_F/BEI_10Y/USDJPY)在证据面在场', sorted(set(dms)), ['BEI_10Y', 'BRENT_F', 'USDJPY'], dm_ok, 'TR1.step1/2/3, TR2.step1 distinguishing_metric 可观测性')

# ---------------- 核心CPI 显示层舍入注记 ----------------
a5 = L.yoy_level(F, 'CORE_CPI', '2026-05')[0]; a8 = L.yoy_level(F, 'CORE_CPI', '2026-08')[0]
chk_txt(SM, 'CORE_CPI 同比 2026-05→2026-08 四位小数端点差 / 未舍入差', [round(round(a8, 4) - round(a5, 4), 4), round(a8 - a5, 4)], [-0.3767, -0.3768],
      P.eq(round(round(a8, 4) - round(a5, 4), 4), -0.3767) and P.eq(round(a8 - a5, 4), -0.3768), 'quality_gate_notes ⑧')
chk(S7, 'CORE_CPI 同比 2026-02 / 2026-05', [L.yoy_level(F, 'CORE_CPI', '2026-02')[0], a5], [2.47, 2.82], 'TR1.step1 "核心CPI同比同窗 2.47→2.82"')

# ---------------- 情景阈值 ----------------
below = [(d, v) for d, v in F.series('BEI_10Y') if v < 1.8]
chk_txt(S9, 'series_store.BEI_10Y 库内最近一次低于 1.8', below[-1], ('2020-11-30', 1.77), below[-1] == ('2020-11-30', 1.77), 'SCN2 证伪阈值依据')
chk(S9, 'BEI_10Y 最新 2.15 较 1.77 (bp)', round((at('BEI_10Y', '2026-11-20') - 1.77) * 100), 38, 'SCN2 "低 38 个基点"')
chk(S9, 'BEI_10Y 最新 2.15 较阈值 1.8 (bp)', round((at('BEI_10Y', '2026-11-20') - 1.8) * 100), 35, 'SCN2 "高 35 个基点"')
sc = {s['id']: s['rows'] for s in aj['l4']['scenarios']}
chk_txt(S9, '两情景期限', [sc['SCN1']['trigger']['deadline'], sc['SCN2']['trigger']['deadline']], ['2027-02-28', '2027-02-28'], [sc['SCN1']['trigger']['deadline'], sc['SCN2']['trigger']['deadline']] == ['2027-02-28', '2027-02-28'], 'quality_gate_notes "期限均为 2027-02-28"')
pub = {}
for mk, ym in (('CPI', '2026-12'), ('CORE_PCE', '2026-12'), ('CPI', '2027-01')):
    pub['%s@%s' % (mk, ym)] = L.release_date(F, mk, L.month_end(ym))[0]
print('期限前发布:', pub)
chk_txt(S9, 'SCN1 触发/证伪所涉观测的规则发布日均早于期限 2027-02-28', pub, 'CPI 2026-12 / CORE_PCE 2026-12 / CPI 2027-01', all(v < '2027-02-28' for v in pub.values()), 'SCN1 触发(2026-11或2026-12月CPI)/证伪(CPI<2.5 且 CORE_PCE<2.8 持续两个月)可观测性')
cpi_vis = L.visible_latest(F, 'CPI', '2026-11-23'); pce_vis = L.visible_latest(F, 'CORE_PCE', '2026-11-23')
cy = [L.yoy_level(F, 'CPI', m)[0] for m in ('2026-05', '2026-07', '2026-08', '2026-09', '2026-10', '2026-11')]
print('CPI yoy 05/07/08/09/10/11', cy, 'latest visible', cpi_vis, 'PCE', pce_vis, (L.yoy_level(F, 'CORE_PCE', pce_vis['obs_date'][:7])[0] if pce_vis else None))
cpi9 = L.yoy_level(F, 'CPI', '2026-09')[0]; pce7 = L.yoy_level(F, 'CORE_PCE', '2026-07')[0]
pce9 = L.yoy_level(F, 'CORE_PCE', '2026-09')[0]
chk_txt(S9, 'SCN1 触发(CPI同比继续≥3.5)/证伪(CPI<2.5 且 CORE_PCE<2.8) 与截止日读数相容(未证伪; 触发所涉 2026-11/12 观测尚未发布)', [round(cpi9, 2), round(pce7, 2), round(pce9, 2)], [3.72, 3.00, 3.12],
      (cpi9 >= 3.5 and cpi9 >= 2.5 and pce7 >= 2.8 and pce9 >= 2.8) and eql([round(cpi9, 2), round(pce7, 2), round(pce9, 2)], [3.72, 3.00, 3.12]), 'SCN1 trigger/falsification ↔ TR1.step1 "2026-07 3.00 → 2026-09 3.12" / TR1.step2 "2026-09 观测回升至 3.72"')
chk_txt(S9, 'SCN2 证伪(BEI_10Y<1.8) 在截止日未成立; 触发所涉 2025-10 基期缺席', [at('BEI_10Y', '2026-11-20'), L.yoy_level(F, 'CPI', '2026-10')[1]], [2.15, 'no_same_period_base'], at('BEI_10Y', '2026-11-20') > 1.8 and L.yoy_level(F, 'CPI', '2026-10')[0] is None, 'SCN2 "(2026-10 同比待 2025-10 基期补齐)"')
mon = F.monthly('CPI')
chk_txt(S9, 'SCN1 注 "2026-10 同比待 2025-10 基期补齐；2026-11 起同比不受此缺基期影响": CPI 基期 2025-10 缺席 / 2025-11、2025-12 在场', [mon.get('2025-10'), mon.get('2025-11') is not None, mon.get('2025-12') is not None], [None, True, True],
      mon.get('2025-10') is None and mon.get('2025-11') is not None and mon.get('2025-12') is not None, 'SCN1 falsification.threshold / SCN2 trigger.condition')
d1 = sc['SCN1']['asset_direction']['direction']; d2 = sc['SCN2']['asset_direction']['direction']
chk_txt(S9, '两情景方向互补', ['SCN1: 股指承压/GOLD_F 受压/DXY 偏强/VIX 抬升', 'SCN2: 股指修复/GOLD_F 走强/DXY 转弱'], 'SCN1=承压·DXY偏强 / SCN2=修复·DXY转弱',
      ('股指(SPX/NIKKEI225)倾向承压' in d1 and 'DXY 偏强' in d1) and ('股指倾向修复' in d2 and 'DXY 转弱' in d2), 'L4 两情景资产方向互补(文字核对)')

# ---------------- 历史类比面 ----------------
an = None
for s in rep['steps']:
    e = s.get('envelope') or {}
    d = e.get('data') if isinstance(e, dict) else None
    if isinstance(d, dict) and 'top' in d and 'candidates' in d:
        an = d
top = an['top']
hp = aj['reader_map']['history_periods']
LABEL = {h['anchor_ym']: h for h in hp}
chk_txt(S8, '有效候选数', an['candidates']['valid'], 74, an['candidates']['valid'] == 74, 'history_periods[0].period_label "74个有效候选" / similarity')
chk_txt(S8, 'TOP-N 独立簇数', an['dispersion']['n_independent_clusters'], 5, an['dispersion']['n_independent_clusters'] == 5 and an['candidates']['n_independent_clusters_topN'] == 5, 'period_label "TOP-5独立簇"')
CN = {'growth': '增长', 'inflation': '通胀', 'rates': '利率', 'credit': '信用', 'volatility': '波动', 'valuation': '估值'}


def label(k):
    if k.endswith('_d12m'):
        return k[:-5] + ' 12月变化'
    if k == 'SPX_rv21':
        return 'SPX 21日已实现波动'
    if k == 'SPX_CAPE_level':
        return 'SPX CAPE'
    if k.endswith('_level'):
        return k[:-6] + '水平'
    if k == 'ICSA_4w_avg':
        return 'ICSA 4周均值'
    return k


for i, t in enumerate(top[:3]):
    cand = t['candidate_month']; h = LABEL[cand]
    chk(S8, 'report.json steps[analog].top[%d].distance' % i, t['distance'], float(re.search(r'距离([0-9.]+)', h['period_label']).group(1)), 'history_periods[%d].period_label' % i)
    chk(S8, 'top[%d].distance_percentile' % i, t['distance_percentile'], float(re.search(r'分位([0-9.]+)', h['period_label']).group(1)), 'history_periods[%d].period_label' % i)
    rk = int(re.search(r'独立簇第([0-9]+)', h['period_label']).group(1))
    chk_txt(S8, 'top[%d].rank ↔ "TOP-5独立簇第N"' % i, t['rank'], rk, t['rank'] == rk, 'history_periods[%d].period_label' % i)
    contrib = {CN[k]: round(v['contribution_share'] * 100, 1) for k, v in t['dims'].items() if v['contribution_share'] >= 0.005}
    got = {n: float(v) for n, v in re.findall(r'([一-龥]+)([0-9.]+)%', h['similarity'])}
    chk_txt(S8, 'top[%d].dims 贡献份额(%%, 舍入1位; <0.5%% 维不列)' % i, contrib, got, contrib == got, 'history_periods[%d].similarity' % i)
    big = sorted(((label(k), '候选期高于当前' if v['gap'] < 0 else '当前高于候选期', round(abs(v['gap']), 2)) for k, v in t['features_detail'].items() if abs(v['gap']) > 1.0), key=lambda x: -x[2])
    listed = [(a.strip(), b, float(c[1:])) for a, b, c in re.findall(r'([A-Z][A-Z0-9_]*(?: ?[^(),；、]*?))\((候选期高于当前|当前高于候选期),([+-][0-9.]+)\)', h['difference'])]
    chk_txt(S8, 'top[%d].features_detail |gap|>1 清单(完整性/方向/数值/降序)' % i, big, listed, big == listed, 'history_periods[%d].difference "差异>1σ逐维点名"' % i)
    miss = t['missing_features']
    chk_txt(S8, 'top[%d].missing_features ↔ 信用维缺席注记' % i, sorted(set(miss.values())), ['hist_17<36'] if 'hist_17<36' in miss.values() else ['no_value_at_candidate_month'],
          (('HY序列历史17个月<36' in h['difference']) if 'hist_17<36' in miss.values() else ('候选月无HY观测' in h['difference'])), 'history_periods[%d].difference 信用维注记' % i)
    chk_txt(S8, 'history_periods[%d].match_window / aftermath_obs_months / judgment_cutoff_ym' % i,
          [h['match_window'], h['aftermath_obs_months'], h['judgment_cutoff_ym']],
          [{'start_ym': L.add_months(cand, -11), 'end_ym': cand}, [L.add_months(cand, k) for k in (3, 6, 12)], cand],
          h['match_window'] == {'start_ym': L.add_months(cand, -11), 'end_ym': cand} and h['aftermath_obs_months'] == [L.add_months(cand, k) for k in (3, 6, 12)] and h['judgment_cutoff_ym'] == cand,
          'history_periods[%d] (特征窗=锚前12个月)' % i)
    print('top', i, cand, 'dist', t['distance'], 'pct', t['distance_percentile'], 'contrib', contrib, '|gap|>1:', big)
cov = {k: v['coverage'] for k, v in an['state_vector'].items() if isinstance(v, dict)}
EXPC = {'growth': 0.17, 'inflation': 0.33, 'rates': 0.75, 'credit': 0.5, 'volatility': 1.0, 'valuation': 0.5}
chk_txt(S8, 'state_vector 维度覆盖 growth/inflation/rates/credit/volatility/valuation', cov, EXPC, all(P.eq(cov[k], v) for k, v in EXPC.items()), 'sample_note "增长维覆盖0.17/通胀0.33/信用0.5"')
chk_txt(S8, '特征窗月数 / 锚月', [an['feature_window_months'], an['anchor_month']], [12, '2026-11'], an['feature_window_months'] == 12 and an['anchor_month'] == '2026-11', 'sample_note "当前特征窗(2025-12至2026-11)"')
sa = an['dispersion']['topN_aftermath_sign_agreement']
chk_txt(S8, 'TOP-N 事后符号一致率=1.0 的键', sorted(k for k, v in sa.items() if v == 1.0), ['GOLD_F_12m', 'GOLD_F_6m', 'SPX_12m', 'SPX_6m'], sorted(k for k, v in sa.items() if v == 1.0) == ['GOLD_F_12m', 'GOLD_F_6m', 'SPX_12m', 'SPX_6m'], 'sample_note "GOLD_F 与 SPX 六个月与十二个月窗符号一致"')
chk_txt(S8, 'TOP-N 事后符号一致率: 其余各窗取值集合', sorted(set(v for v in sa.values() if v != 1.0)), [0.6, 0.8], sorted(set(v for v in sa.values() if v != 1.0)) == [0.6, 0.8], 'sample_note "其余各窗零点六至零点八"')
chk_txt(S8, '一致率面序列集合', sorted(set(k.rsplit('_', 1)[0] for k in sa)), ['DXY', 'GOLD_F', 'SPX', 'UST_10Y'], set(k.rsplit('_', 1)[0] for k in sa) == {'DXY', 'GOLD_F', 'SPX', 'UST_10Y'}, 'sample_note "一致率面仅含 DXY、GOLD_F、SPX、UST_10Y 四类"')


# --- 引擎事后块口径(次月首日起首个观测→候选月+N 月末界内最后观测) 从 series_store 直算 ---
def engine_after(cand, m, s):
    start = L.add_months(cand, 1) + '-01'
    end = L.month_end(L.add_months(cand, m))
    w = F.window(s, start, end)
    if not w:
        return None, None, None
    a = w[0][1]; b = w[-1][1]
    return ((b - a) if s == 'UST_10Y' else L.pct(a, b)), w[0][0], w[-1][0]


recomputed = {}; wbad = []
for t in top:
    cand = t['candidate_month']
    for s in ('SPX', 'UST_10Y', 'DXY', 'GOLD_F'):
        for m in ('1m', '3m', '6m', '12m'):
            v, d0, d1 = engine_after(cand, int(m[:-1]), s)
            recomputed[(cand, s, m)] = v
            P.add(S8, 'series_store.%s 引擎事后块口径 %s: %s→%s' % (s, cand, d0, d1), round(v, 6) if v is not None else None, t['aftermath'][s][m],
                  P.eq(round(v, 6) if v is not None else None, t['aftermath'][s][m]), where='report.json steps[analog].top[%s].aftermath.%s.%s' % (cand, s, m))
            ew = t['aftermath'][s + '_window'][m]
            if not (ew['start'] <= d0 <= d1 <= ew['end']):
                wbad.append((cand, s, m, d0, d1, ew))
chk_txt(S8, '事后块实际起止观测日落于引擎窗口界内', wbad, [], wbad == [], 'report.json top[*].aftermath.*_window')
for s in ('SPX', 'UST_10Y', 'DXY', 'GOLD_F'):
    for m in ('1m', '3m', '6m', '12m'):
        vals = [recomputed[(t['candidate_month'], s, m)] for t in top]
        signs = [(v > 0) - (v < 0) for v in vals]
        # 引擎规则(analog_engine.py L812-815, 只读核对): npos=count(v>0); agree=max(npos, n-npos)/n  (恰为 0 计入非正一侧)
        npos = sum(1 for v in vals if v > 0)
        agree = max(npos, len(vals) - npos) / float(len(vals))
        P.add(S8, 'TOP-5 独立簇事后符号一致率独立重算(引擎规则: 恰为0计非正侧) %s_%s' % (s, m), round(agree, 2), sa['%s_%s' % (s, m)], P.eq(round(agree, 2), sa['%s_%s' % (s, m)]), note='signs=%s' % signs, where='report.json dispersion.topN_aftermath_sign_agreement')
        strict = max(signs.count(1), signs.count(-1)) / float(len(signs))
        if P.eq(round(strict, 2), round(agree, 2)) is False:
            P.add(S8, '同格严格符号口径(0 不计入任一侧) %s_%s' % (s, m), round(strict, 2), sa['%s_%s' % (s, m)], 'NA', note='恰为0的事后块在严格口径下不计入一致侧; 受审稿 "其余各窗零点六至零点八" 在两种口径下均成立', where='report.json dispersion.topN_aftermath_sign_agreement')
cm = [t['candidate_month'] for t in top]
gapsm = sorted(abs((int(a[:4]) - int(b[:4])) * 12 + (int(a[5:7]) - int(b[5:7]))) for i, a in enumerate(cm) for b in cm[i + 1:])
chk_txt(S8, 'TOP-5 候选月两两相差(月) ≥12', gapsm, None, min(gapsm) >= 12, 'candidates.cluster_dedup "候选月相差<12 个月=同簇"  TOP-5=%s' % cm)
# 月末口径(受审稿) vs 引擎口径
diffs = []
for t in top[:3]:
    cand = t['candidate_month']; h = LABEL[cand]
    for m in ('3m', '6m', '12m'):
        for name, val in re.findall(r'(DFEDTARU|UNEMPLOYMENT|CPI|INDPRO|SPX|NIKKEI225|DAX|SHCOMP|GOLD_F|DXY|UST_10Y) ([+-][0-9.]+)', h['ex_post'][m]):
            if name in ('SPX', 'UST_10Y', 'DXY', 'GOLD_F'):
                diffs.append((cand, m, name, round(float(val) - recomputed[(cand, name, m)], 2)))
print('月末口径 vs 引擎口径差异:', diffs)
mx = max(abs(x[3]) for x in diffs)
sg = []
for t in top[:3]:
    for s in ('SPX', 'UST_10Y', 'DXY', 'GOLD_F'):
        d0 = L.add_months(t['candidate_month'], 1) + '-01'
        a = F.at_or_before(s, L.month_end(t['candidate_month'])); b = next((x for x in F.series(s) if x[0] >= d0), None)
        if a and b:
            sg.append((t['candidate_month'], s, a[0], b[0], round((b[1] / a[1] - 1) * 100, 4)))
print('起点观测差(月末最后观测 vs 次月首日起首个观测) %:', sg)
sgp = [x for x in sg if x[1] in ('SPX', 'DXY', 'GOLD_F')]
mxs = round(max(abs(x[4]) for x in sgp), 2)
print('价格类起点差 最大绝对差 %:', mxs)
P.add(S8, '起点观测差(价格类 SPX/DXY/GOLD_F, 候选3期): 月末口径起点(候选月末最后观测) vs 引擎起点(锚后首个观测) 最大绝对差 %', mxs, '约1个百分点', abs(mxs - 1.0) <= 0.5, note='带「约」字量级表述按正负50%%容差比对; max=%r' % (max(sgp, key=lambda x: abs(x[4])),), where='history_periods[*].ex_post.{3m,6m,12m} 括注 "引擎事后块起点为锚后首个观测,两口径数值可差约1个百分点"(起点差)')
ust2 = []
for t in top[:3]:
    c = t['candidate_month']
    a = F.at_or_before('UST_10Y', L.month_end(c)); b = next(x for x in F.series('UST_10Y') if x[0] >= L.add_months(c, 1) + '-01')
    ust2.append((c, a[0], b[0], round(b[1] - a[1], 2)))  # UST_10Y 序列值本身以 % 计, 差即 pp
print('UST_10Y 起点差(pp):', ust2)
P.add(S8, '起点观测差(UST_10Y, 候选3期, pp)', [u[3] for u in ust2], [-0.06, -0.10, -0.11], eql([u[3] for u in ust2], [-0.06, -0.10, -0.11]), note='UST_10Y 起点差以 pp 计', where='history_periods[*].ex_post 括注(起点差; 利率类)')
over = sorted([x for x in diffs if abs(x[3]) > 1.05], key=lambda x: -abs(x[3]))
print('两口径结果差 >1.05pp 的格:', over)
chk_txt(S8, '受审稿月末口径与引擎事后块口径之差: SPX/UST_10Y/DXY/GOLD_F×3期×3窗=36 格收益/变动差 最大绝对差 (pp; 约=正负50%量级容差)', mx, '约1个百分点', abs(mx - 1.0) <= 0.5,
      'history_periods[*].ex_post 括注 "两口径数值可差约1个百分点"(结果数值差; 超过1.05pp的格数=%d/36: %s; NIT)' % (len(over), over))
# C2 陈述: 事后路径分歧(月末口径表逻辑)
ME = {}
for cand in ('2025-03', '2022-06', '2023-10'):
    for m in ('3', '6', '12'):
        for s in ('SPX', 'NIKKEI225', 'DAX', 'SHCOMP', 'GOLD_F', 'DXY'):
            a = F.at_or_before(s, L.month_end(cand)); b = F.at_or_before(s, L.month_end(L.add_months(cand, int(m))))
            ME[(cand, s, m)] = L.pct(a[1], b[1])
q1 = all(ME[('2022-06', s, '3')] < 0 for s in ('DAX', 'SHCOMP', 'SPX', 'NIKKEI225')) and all(ME[('2022-06', s, '12')] > 0 for s in ('DAX', 'SPX', 'NIKKEI225')) and ME[('2022-06', 'SHCOMP', '12')] < 0
q2 = all(ME[(c, s, m)] > 0 for c in ('2025-03', '2023-10') for s in ('SPX', 'NIKKEI225', 'DAX', 'GOLD_F') for m in ('3', '6', '12')) and all(ME[(c, 'DXY', m)] < 0 for c in ('2025-03', '2023-10') for m in ('3', '6', '12')) \
     and all(ME[('2025-03', 'SHCOMP', m)] > 0 for m in ('3', '6', '12')) and ME[('2023-10', 'SHCOMP', '3')] < 0 and ME[('2023-10', 'SHCOMP', '6')] > 0 and ME[('2023-10', 'SHCOMP', '12')] > 0
chk_txt(S8, 'C2 "2022-06段股指三个月窗普遍收缩(DAX、SHCOMP、SPX、NIKKEI225 均为负)而十二个月窗除 SHCOMP 外转正"', q1, True, q1 is True, 'C2.statement')
chk_txt(S8, 'C2 "2025-03、2023-10段风险资产与 GOLD_F 多数窗走强(2023-10段上证三个月窗为负，属例外)而 DXY 走弱"', q2, True, q2 is True, 'C2.statement')
print('tally', P.tally())
