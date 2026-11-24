# -*- coding: utf-8 -*-
"""rc10: 补核(Audit-R32 A round1; 只读)。
用法: /usr/bin/python3 -I rc10_supplement.py <snapshot.json> <run_dir>
覆盖: MAP 历史段逐窗并列细表(81行) / 走位与转折叙述中的月频路径与计数 / FULL_REPORT L1 事实表(48行) /
      类比第4-5名 / 日度相关 / 判断文本在各报告副本的一致性 / Gate A 缺口清单披露 / 日历「无实录条目」陈述。
所有记录 note 带 [rc10] 标记: 重跑前 /usr/bin/python3 -I rc_clean_mark.py '[rc10] '
"""
import sys, os, re, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_lib as L
import rc_points as P

snap = L.load(sys.argv[1]); RUN = sys.argv[2]
cal = L.load(os.path.join(RUN, 'root_overlay', 'config', 'release_calendar.json'))
F = L.Face(snap, cal)
MAP = open(os.path.join(RUN, 'MAP_REPORT.md'), encoding='utf-8').read()
MAPL = MAP.split('\n')
FULL = open(os.path.join(RUN, 'FULL_REPORT.md'), encoding='utf-8').read()
REPM = open(os.path.join(RUN, 'report.md'), encoding='utf-8').read()
aj = L.load(os.path.join(RUN, 'agent_judgment.json'))
rep = L.load(os.path.join(RUN, 'report.json'))

S8 = '⑧历史事后窗(细表)'; S10 = '⑩走位/转折叙述'; S2 = '②/⑬FULL_REPORT-L1事实表'; SA = '⑧历史类比面'
S7 = '⑦日度相关'; ST = '⑩报告间文本一致'; S11 = '⑪诚实缺席/GateA'

_add = P.add


def add10(section, src, computed, reported, ok, note='', where=''):
    _add(section, src, computed, reported, ok, note='[rc10] ' + note, where=where)


P.add = add10


def eq(comp, rep_):
    if isinstance(comp, (list, tuple)) and isinstance(rep_, (list, tuple)):
        return len(comp) == len(rep_) and all(eq(a, b) for a, b in zip(comp, rep_))
    if isinstance(comp, dict) and isinstance(rep_, dict):
        return comp.keys() == rep_.keys() and all(eq(comp[k], rep_[k]) for k in comp)
    return P.eq(comp, rep_)


def chk(section, src, comp, rep_, where):
    P.add(section, src, comp, rep_, eq(comp, rep_), where=where)


def chk_txt(section, src, comp, rep_, ok, where, note=''):
    P.add(section, src, comp, rep_, bool(ok), where=where, note=note)


# ============ A. MAP 历史段逐窗并列细表 ============
ROW = re.compile(r'^\s*\| (经济指标|资产表现) \| (.+?) \| (\d{4}-\d{2}-\d{2}) \| ([0-9.]+) \| (\d{4}-\d{2}-\d{2}) \| ([0-9.]+) '
                 r'\| ([+-][0-9.]+)(pp|%) \| (\S+) \| (.+?) \|\s*$')
LBL = re.compile(r'\(([A-Z0-9_]+)\)\s*$')
PP = ('DFEDTARU', 'UNEMPLOYMENT', 'UST_10Y')
cand = None; k = None; nrow = 0; bad = []
for i, line in enumerate(MAPL):
    if i + 1 < 330:
        continue
    m = re.match(r'^### (\d{4}-\d{2})', line)
    if m:
        cand = m.group(1); continue
    m = re.match(r'^\s*\*\*随后(\d+)个月窗', line)
    if m:
        k = int(m.group(1)); continue
    m = ROW.match(line)
    if not m:
        continue
    grp, lbl, d0, v0, d1, v1, chg, unit = m.groups()[:8]
    name = LBL.search(lbl).group(1)
    a = F.at_or_before(name, L.month_end(cand)); b = F.at_or_before(name, L.month_end(L.add_months(cand, k)))
    c = (b[1] - a[1]) if name in PP else L.pct(a[1], b[1])
    comp = [a[0], a[1], b[0], b[1], round(c, 6)]
    repv = [d0, float(v0), d1, float(v1), float(chg)]
    ok = (a[0] == d0 and b[0] == d1 and P.eq(a[1], float(v0)) and P.eq(b[1], float(v1)) and P.eq(c, float(chg))
          and unit == ('pp' if name in PP else '%'))
    P.add(S8, 'series_store.%s(候选%s, +%d个月; 起止=候选月末/+N月末或之前最近观测)' % (name, cand, k), comp, repv, ok,
          where='MAP_REPORT.md 行%d 逐窗并列细表' % (i + 1))
    nrow += 1
    if not ok:
        bad.append((i + 1, comp, repv))
chk_txt(S8, 'MAP 历史段逐窗并列细表行数(3段×3窗×9行)', nrow, 81, nrow == 81, 'MAP_REPORT.md 历史段细表')
print('A 细表行数', nrow, '不一致行', bad)

# ============ B. 走位/转折叙述 ============
g = [F.at('US_REAL_GDP', d) for d in ('2025-04-01', '2026-04-01', '2026-07-01')]
chk(S10, 'series_store.US_REAL_GDP(2025-04-01/2026-04-01/2026-07-01)', g, [23884.563, 24408.011, 24611.077],
    'MAP_REPORT 美国走位 "水平 23884.563→24408.011→24611.077 十亿美元"')
e = [x for x in cal['entries'] if x.get('entry_id') == 'RC-2025SHUTDOWN-GDP-Q3']
chk_txt(S10, 'release_calendar.entries[RC-2025SHUTDOWN-GDP-Q3](obs_from, first_publish_on_or_after)',
        [e[0]['obs_from'], e[0]['first_publish_on_or_after']] if e else None, ['2025-07-01', '2025-12-23'],
        bool(e) and e[0]['obs_from'] == '2025-07-01' and e[0]['first_publish_on_or_after'] == '2025-12-23',
        '美国走位 "2025 年第三季度 GDP 因 2025 年联邦政府停摆延至 2025-12-23 首发"')
vu = L.visible_latest(F, 'US_REAL_GDP', '2025-11-23'); ve = L.visible_latest(F, 'EA_REAL_GDP_YOY', '2025-11-23'); vj = L.visible_latest(F, 'JP_REAL_GDP_YOY', '2025-11-23')
chk_txt(S10, '12个月前锚 2025-11-23 按发布纪律可见的最新季度观测日: US / EA / JP',
        [vu['obs_date'], ve['obs_date'], vj['obs_date']], ['2025Q2=2025-04-01', '2025Q3=2025-07-01', '2025Q3=2025-07-01'],
        vu['obs_date'] == '2025-04-01' and ve['obs_date'] == '2025-07-01' and vj['obs_date'] == '2025-07-01',
        '美国走位 "12个月前锚前最新已发布季度为 2025Q2…较欧元区、日本同锚早一个季度"')

pm = F.monthly('CN_PMI_MFG')
dif = [round(pm[y] - pm[L.add_months(y, -12)], 2) for y in ('2025-10', '2026-07', '2026-10')]
chk(S10, 'CN_PMI_MFG 指数点差(本月水平−去年同月水平) 2025-10/2026-07/2026-10', dif, [-1.1, -0.1, 0.3],
    '中国走位 "即相差约 -1.1、-0.1、+0.3 个指数点"')
win = [(y, pm[y]) for y in sorted(pm) if '2025-11' <= y <= '2026-10']
above = [(y, v) for y, v in win if v > 50]; flat = [(y, v) for y, v in win if v == 50]; rest = [v for y, v in win if v < 50]
EXP_A = [('2025-12', 50.1), ('2026-03', 50.4), ('2026-04', 50.3), ('2026-06', 50.3), ('2026-09', 50.1)]
chk_txt(S10, 'CN_PMI_MFG 2025-11..2026-10 站上荣枯线(>50)的月份与读数', above, EXP_A, above == EXP_A,
        '中国走位/C1 "2025-12、2026-03、2026-04、2026-06、2026-09 共五个月站上荣枯线(50.1/50.4/50.3/50.3/50.1)"')
chk_txt(S10, 'CN_PMI_MFG 2025-11..2026-10 持平于 50.0 的月份', flat, [('2026-05', 50.0)], flat == [('2026-05', 50.0)],
        '中国走位 "2026-05 持平于 50.0"')
chk_txt(S10, 'CN_PMI_MFG 2025-11..2026-10 其余(<50)月份的读数范围与窗内月数', [min(rest), max(rest), len(win)], [49.0, 49.8, 12],
        min(rest) == 49.0 and max(rest) == 49.8 and len(win) == 12, '中国走位 "其余月份落在 49.0–49.8 之间"')

po = F.series('CN_POLICY_OVERNIGHT')
chk_txt(S10, 'CN_POLICY_OVERNIGHT 序列: 首观测日/末观测日/取值集合/观测数', [po[0][0], po[-1][0], sorted(set(v for d, v in po)), len(po)],
        ['2026-11-02', '2026-11-23', [1.25], 16],
        po[0][0] == '2026-11-02' and po[-1][0] == '2026-11-23' and set(v for d, v in po) == {1.25} and len(po) == 16,
        '中国走位 "12个月前与3个月前锚日前无已发布观测,最新 1.25@2026-11-23(换锚后持平于首个观测值)"')
nb = [sum(1 for d, v in po if d <= a) for a in ('2025-11-23', '2026-08-23')]
chk_txt(S10, 'CN_POLICY_OVERNIGHT 锚日(2025-11-23/2026-08-23)当日及之前观测数', nb, [0, 0], nb == [0, 0], '同上(锚日前无观测)')
o7 = F.series('CN_OMO_7D')
w7 = [v for d, v in o7 if '2025-11-23' <= d <= '2026-11-23']
chk_txt(S10, 'CN_OMO_7D 一年窗(2025-11-23..2026-11-23)内取值集合/窗内观测数/末观测日', [sorted(set(w7)), len(w7), o7[-1][0]], [[1.4], len(w7), '2026-10-30'],
        set(w7) == {1.4} and o7[-1][0] == '2026-10-30', '中国走位/C1 "7天逆回购利率…窗内无变动…末观测 2026-10-30、其后缺观测"')
print('B OMO7D 窗内观测数', len(w7))
lpr = F.series('CN_LPR_1Y')
wl = [v for d, v in lpr if '2025-11-23' <= d <= '2026-11-23']
chk_txt(S10, 'CN_LPR_1Y 一年窗内取值集合/窗启时在值(2025-11-20)', [sorted(set(wl)), F.at_or_before('CN_LPR_1Y', '2025-11-23')], [[3.0], ('2025-11-20', 3.0)],
        set(wl) == {3.0} and F.at_or_before('CN_LPR_1Y', '2025-11-23') == ('2025-11-20', 3.0), '中国走位 "LPR_1Y 3.0→3.0→3.0 窗内持平"')

h = F.monthly('EA_HICP_YOY')
HY = ['2026-%02d' % i for i in range(1, 11)]
chk(S10, 'EA_HICP_YOY 2026-01..2026-10', [round(h[y], 2) for y in HY], [1.7, 1.9, 2.6, 3.0, 3.2, 2.8, 2.9, 3.2, 3.8, 4.0],
    '欧元区走位 "自2026-01低点1.7连续上行至2026-05的3.2，2026-06回落至2.8后自2026-07再度上行…最新4.0"')
inc = {y: round(h[y] - h[L.add_months(y, -1)], 2) for y in ('2026-07', '2026-08', '2026-09', '2026-10')}
chk(S10, 'EA_HICP_YOY 月度增量 2026-07..2026-10', inc, {'2026-07': 0.1, '2026-08': 0.3, '2026-09': 0.6, '2026-10': 0.2},
    '欧元区走位 "2026-08至10月度增量 +0.3/+0.6/+0.2，均高于7月的 +0.1"')
lowh = min((h[y], y) for y in h if '2025-11' <= y <= '2026-10')[1]
mono = all(h[HY[i + 1]] > h[HY[i]] for i in range(0, 4))
chk_txt(S10, 'EA_HICP_YOY: 窗内(2025-11..2026-10)低点月 / 2026-01→05 逐月上行 / 03增量 vs 02增量',
        [lowh, mono, round(h['2026-03'] - h['2026-02'], 2), round(h['2026-02'] - h['2026-01'], 2)], ['2026-01', True, 0.7, 0.2],
        lowh == '2026-01' and mono and P.eq(h['2026-03'] - h['2026-02'], 0.7) and P.eq(h['2026-02'] - h['2026-01'], 0.2),
        '欧元区走位 "低点1.7…(2026-03起加速)" / 转折表 "HICP 低点在 2026-01"')

j = F.monthly('JP_POLICY_RATE')
JX = {'2025-10': 0.477, '2025-11': 0.478, '2025-12': 0.557, '2026-01': 0.728, '2026-05': 0.727, '2026-06': 0.841, '2026-07': 0.978,
      '2026-08': 0.977, '2026-09': 1.043, '2026-10': 1.227}
chk(S10, 'JP_POLICY_RATE 月均(受审稿逐个引用的月份)', {y: j[y] for y in JX}, JX,
    '日本走位/传导链2/政策一年窗路径(0.477/0.478/0.557/0.728/0.727/0.841/0.978/0.977/1.043/1.227)')
JY = ['2025-%02d' % i for i in (11, 12)] + ['2026-%02d' % i for i in range(1, 11)]
steps = []; tiny = []
for a, b in zip(JY, JY[1:]):
    d = (j[b] - j[a]) * 100
    if round(d) != 0:
        steps.append((b, int(round(d))))
    elif abs(d) > 1e-9:
        tiny.append((b, round(d, 2)))
chk_txt(S10, 'JP_POLICY_RATE 窗内步进(四舍五入后 bp≠0 的月份)', steps,
        [('2025-12', 8), ('2026-01', 17), ('2026-06', 11), ('2026-07', 14), ('2026-09', 7), ('2026-10', 18)], steps == [('2025-12', 8), ('2026-01', 17), ('2026-06', 11), ('2026-07', 14), ('2026-09', 7), ('2026-10', 18)],
        '传导链2 "月度步进 +8/+17/+11/+14/+7/+18 个基点，分别落在 2025-12、2026-01、2026-06、2026-07、2026-09、2026-10"')
chk_txt(S10, 'JP_POLICY_RATE 舍入级微变月份(|Δ|<1bp)', tiny, [('2026-04', -0.1), ('2026-08', -0.1)], tiny == [('2026-04', -0.1), ('2026-08', -0.1)],
        '传导链2 "另有 2026-04 与 2026-08 各约零点一个基点的舍入变动"')
chk_txt(S10, 'JP_POLICY_RATE 净变动: 2025-11→2026-10 / 2025-12→2026-10 / 窗内是否存在 ≤-1bp 的步进 / 首个上调步进月',
        [round((j['2026-10'] - j['2025-11']) * 100), round((j['2026-10'] - j['2025-12']) * 100), any(bp <= -1 for _, bp in steps), steps[0][0]],
        [75, 67, False, '2025-12'],
        round((j['2026-10'] - j['2025-11']) * 100) == 75 and round((j['2026-10'] - j['2025-12']) * 100) == 67
        and not any(bp <= -1 for _, bp in steps) and steps[0][0] == '2025-12',
        '日本走位/传导链2 "净 +75 个基点(自 2025-12 起 +67bp)…在美欧通胀同窗回升(2026-02起)之前已开始上调、窗内未回撤"')

jg = sorted(k for k in F.ss if 'JGB' in k)
jf = [f for f in snap['facts'] if f['metric_id'].startswith('JGB')]
chk_txt(S10, 'JGB: series_store 内序列数 / facts 内单点事实(指标@观测日)', [len(jg), sorted('%s@%s' % (f['metric_id'], f['observation_date']) for f in jf)],
        [0, ['JGB10Y@2026-11-19', 'JGB2Y@2026-11-19', 'JGB5Y@2026-11-19']], len(jg) == 0 and sorted('%s@%s' % (f['metric_id'], f['observation_date']) for f in jf) == ['JGB10Y@2026-11-19', 'JGB2Y@2026-11-19', 'JGB5Y@2026-11-19'],
        '传导链2 "JGB 收益率历史序列不在引擎(单点观测)"')

c = F.monthly('JP_CPI_YOY')
JX = {'2025-01': 4.03, '2025-09': 2.91, '2025-10': 2.99, '2025-11': 2.9, '2025-12': 2.13, '2026-01': 1.51, '2026-02': 1.27,
      '2026-03': 1.46, '2026-04': 1.38, '2026-05': 1.53, '2026-07': 1.97, '2026-10': 2.44}
chk(S10, 'JP_CPI_YOY(受审稿逐个引用的月份)', {y: c[y] for y in JX}, JX,
    '转折表 "月末路径 2025-11 2.9→2025-12 2.13→2026-01 1.51→2026-02 1.27…2026-03 1.46、2026-04 1.38…2026-07 1.97→2026-10 2.44" / "自 2025-01 高点 4.03"')
seg = [(c[y], y) for y in c if '2025-01' <= y <= '2026-02']
mx = max(seg)[1]; mn = min(seg)[1]
reb = all(c[y] > c[L.add_months(y, -1)] for y in ('2025-09', '2025-10'))
chk_txt(S10, 'JP_CPI_YOY 2025-01..2026-02 段内高点月/低点月; 2025-09、2025-10 是否环比回升; 2024-01..2026-10 最小值',
        [mx, mn, reb, round(min(c[y] for y in c if y >= '2024-01'), 2)], ['2025-01', '2026-02', True, 1.27],
        mx == '2025-01' and mn == '2026-02' and reb and P.eq(min(c[y] for y in c if y >= '2024-01'), 1.27),
        '转折表 "自 2025-01 高点 4.03 至 2026-02 低点 1.27 总体下行，其间 2025-09、2025-10 小幅回升"')
tk = F.monthly('JP_CPI_TOKYO_YOY')
TK = {'2026-05': 1.3, '2026-06': 1.6, '2026-07': 1.85, '2026-08': 1.9, '2026-09': 2.69, '2026-10': 2.73}
chk(S10, 'JP_CPI_TOKYO_YOY(受审稿逐个引用的月份)', {y: tk[y] for y in TK}, TK, '日本走位/转折表 "东京CPI 1.85→2.73…2026-06→09 自1.6升至2.69…2026-08 的1.9"')
r9 = L.release_date(F, 'JP_CPI_TOKYO_YOY', '2026-09-01'); r8 = L.release_date(F, 'JP_CPI_TOKYO_YOY', '2026-08-01')
chk_txt(S10, 'JP_CPI_TOKYO_YOY 规则发布日: 2026-09 观测 / 2026-08 观测(及 2026-08-30 星期)', [r9[0], r8[0], L.weekday('2026-08-30')],
        ['2026-09-29', '2026-08-30', '星期日'], r9[0] == '2026-09-29' and r8[0] == '2026-08-30' and L.weekday('2026-08-30') == 7,
        '转折表 "东京CPI 2026-09值推定首发于 2026-09-29…2026-08 的1.9，推定发布 2026-08-31 前后；规则值 2026-08-30 为星期日"')

cy = {y: L.yoy_level(F, 'CPI', y)[0] for y in ['2025-%02d' % i for i in range(11, 13)] + ['2026-%02d' % i for i in range(1, 11)]}
pp_ = F.monthly('CN_PPI_YOY')
PPI = {'2025-10': -2.1, '2025-11': -2.2, '2026-02': -0.9, '2026-05': 3.9, '2026-06': 4.1, '2026-07': 3.5, '2026-10': 5.7}
chk(S10, 'CN_PPI_YOY(受审稿逐个引用的月份)', {y: pp_[y] for y in PPI}, PPI, '中国走位/转折表 "-2.1→3.5→5.7…-0.9→3.9…2026-07 由 4.1 回落至 3.5"')
lows = [min((cy[y], y) for y in cy if cy[y] is not None and '2025-11' <= y <= '2026-10')[1], lowh,
        min((pp_[y], y) for y in pp_ if '2025-11' <= y <= '2026-10')[1]]
decl = [y for y in sorted(pp_) if '2025-12' <= y <= '2026-10' and pp_[y] < pp_[L.add_months(y, -1)]]
chk_txt(S10, '三序列窗内(2025-11..2026-10)低点月: CPI同比 / HICP / PPI; PPI 自低点后环比回落的月份',
        lows + [decl], ['2026-01', '2026-01', '2025-11', ['2026-07']],
        lows == ['2026-01', '2026-01', '2025-11'] and decl == ['2026-07'],
        '转折表 "美国 CPI 同比与欧元区 HICP 低点均在 2026-01、中国 PPI 低点在 2025-11…其间仅 2026-07 由 4.1 回落至 3.5"',
        note='PPI 低点 2025-11 为12个月窗内低点(前月 2025-10=-2.1、2025-09=-2.3 更早更低), 属窗口内口径')
jump = [round(cy['2026-03'] - cy['2026-02'], 2), round(h['2026-03'] - h['2026-02'], 2), round(pp_['2026-03'] - pp_['2026-02'], 2)]
M5 = ['2026-%02d' % i for i in range(1, 6)]
up2 = [all(cy[M5[i + 1]] > cy[M5[i]] for i in range(4)), all(h[M5[i + 1]] > h[M5[i]] for i in range(4)), all(pp_[M5[i + 1]] > pp_[M5[i]] for i in range(4))]
chk_txt(S10, '三序列(CPI同比/HICP/PPI)自 2026-01 至 2026-05 是否逐月上行("2026-02 起同向上行") / 2026-03 同月环比增量', [up2, jump], [[True, True, True], [0.85, 0.7, 1.4]],
        up2 == [True, True, True] and P.eq(jump[0], 0.85) and P.eq(jump[1], 0.7) and P.eq(jump[2], 1.4),
        '转折表 "2026-02 起三序列同向上行、2026-03 同月大幅跳升"')
highc = max((v, y) for y, v in cy.items() if v is not None)[1]
chk_txt(S10, 'CPI 同比窗内高点月', highc, '2026-05', highc == '2026-05', '多处 "2026-05 高点 4.17/4.1666"')
cc = F.monthly('CN_CPI_YOY')
chk_txt(S10, 'CN_CPI_YOY 2026-02..2026-05 取值范围(同窗持平于一点零至一点三)', [round(min(cc[y] for y in ('2026-02', '2026-03', '2026-04', '2026-05')), 2), round(max(cc[y] for y in ('2026-02', '2026-03', '2026-04', '2026-05')), 2)],
        [1.0, 1.3], min(cc[y] for y in ('2026-02', '2026-03', '2026-04', '2026-05')) == 1.0 and max(cc[y] for y in ('2026-02', '2026-03', '2026-04', '2026-05')) == 1.3,
        'C1/传导链1 "中国CPI同比同窗持平于一点零至一点三"')
print('B 2026-02 三序列增量', jump)

m2 = L.yoy_level(F, 'CN_PMI_MFG', '2026-02'); m5 = L.yoy_level(F, 'CN_PMI_MFG', '2026-05')
chk_txt(S10, '转折候选面 CN_PMI_MFG 2026-02→2026-05 同比%(基期=去年同月) 及 Δ', [round(m2[0], 4), m2[1], round(m5[0], 4), m5[1], round(m5[0] - m2[0], 4)],
        [-2.3904, '2025-02', 1.0101, '2025-05', 3.4005], P.eq(m2[0], -2.3904) and m2[1] == '2025-02' and P.eq(m5[0], 1.0101) and m5[1] == '2025-05' and P.eq(m5[0] - m2[0], 3.4005),
        '转折表/候选面 "同比%口径 -2.3904→1.0101 (Δ 3.4005)"')
chk_txt(S10, '转折候选面 CN_CPI_YOY 2026-01→2026-04 及 Δ', [cc['2026-01'], cc['2026-04'], round(cc['2026-04'] - cc['2026-01'], 2)], [0.2, 1.2, 1.0],
        cc['2026-01'] == 0.2 and cc['2026-04'] == 1.2 and P.eq(cc['2026-04'] - cc['2026-01'], 1.0), '候选面 "CN_CPI_YOY 2026-01..2026-04 0.2→1.2 (Δ 1.0)"')

b_now = F.at('BRENT_F', '2026-11-23'); b_30 = F.at('BRENT_F', '2026-10-23')
chk(S10, 'BRENT_F 2026-10-23→2026-11-23: 指数点差 / %', [round(b_now - b_30, 2), round(L.pct(b_30, b_now), 2)], [-28.53, -24.44],
    '传导链1/对质表 "近30日116.72→88.19,-28.53 指数点(-24.44%)"')
sw = {'PPI(3个月前→最新)': pp_['2026-10'] - pp_['2026-07'], 'PPI(12个月前→最新)': pp_['2026-10'] - pp_['2025-10'],
      'CPI同比(12个月前→窗内高点)': round(cy['2026-05'] - cy['2025-11'], 2), 'HICP(12个月前→最新)': round(h['2026-10'] - h['2025-11'], 2),
      'JP_CPI(12个月前→窗内低点→最新)': round(c['2026-02'] - c['2025-11'], 2)}
chk_txt(S10, '四地价格摆动幅度对照(pp): 是否 PPI 最大', sw, 'PPI 最大(12个月前→最新 7.8pp)',
        max(sw, key=sw.get) == 'PPI(12个月前→最新)' and P.eq(sw['PPI(12个月前→最新)'], 7.8), '中国走位 "为四地最大价格摆动"')
mx4 = max(h['2026-10'], cy['2026-09'], cc['2026-10'], c['2026-10'], tk['2026-10'])
chk_txt(S10, '四地消费价格同比最新有效读数: HICP 4.0 / CPI 3.72(2026-09) / CN 0.7 / JP全国 2.44 / 东京 2.73', [h['2026-10'], round(cy['2026-09'], 2), cc['2026-10'], c['2026-10'], tk['2026-10']],
        [4.0, 3.72, 0.7, 2.44, 2.73], mx4 == h['2026-10'], '欧元区走位 "最新4.0为四地消费价格通胀的最高读数"')

# 日历「无实录条目」陈述
ecb = [x for x in cal['entries'] if x.get('metric_id') in ('ECB_DFR', 'ECB_MRO') or (isinstance(x.get('metric_ids'), list) and set(x['metric_ids']) & {'ECB_DFR', 'ECB_MRO'})]
fut = [x for x in cal['entries'] if (x.get('first_publish_on_or_after') or '') > '2026-11-23' and (x.get('metric_id') in ('DFEDTARU', 'ECB_DFR', 'DFF') or (isinstance(x.get('metric_ids'), list) and set(x['metric_ids']) & {'DFEDTARU', 'ECB_DFR', 'DFF'}))]
chk_txt(S10, 'release_calendar.entries: ECB_DFR/ECB_MRO 实录条目数 / 截止日后才发布的 Fed·ECB 决议条目数 / 日历版本', [len(ecb), len(fut), cal.get('version')],
        [0, 0, 'v1.5.0'], len(ecb) == 0 and len(fut) == 0, '欧元区走位/传导链1 "冻结发布日历无欧央行实录条目" / 情景表 "冻结发布日历暂无两家实录条目"')

# ============ C. FULL_REPORT L1 事实表 ============
n1 = 0
for i, line in enumerate(FULL.split('\n')):
    m = re.match(r'^\| ([A-Z0-9_]+) \| ([0-9.]+) \| (\S+) \| (\d{4}-\d{2}-\d{2}) \| (PASS|WARN|DEGRADED|FAIL) \| ([A-Z0-9_]+@\d{4}-\d{2}-\d{2}) \|$', line)
    if not m:
        continue
    name, val, unit, obs, q, ref = m.groups()
    f = F.facts.get(ref)
    comp = [f['value'], f['observation_date'], f['quality_status']] if f else None
    repv = [float(val), obs, q]
    ok = f is not None and f['metric_id'] == name and P.eq(f['value'], float(val)) and f['observation_date'] == obs and f['quality_status'] == q
    P.add(S2, 'snapshot.facts[%s](value/observation_date/quality_status)' % ref, comp, repv, ok, where='FULL_REPORT.md L1 事实层 行%d' % (i + 1))
    n1 += 1
chk_txt(S2, 'FULL_REPORT L1 事实表行数(行11-57)', n1, 47, n1 == 47, 'FULL_REPORT.md L1 事实层')

# ============ D. 类比第4-5名 ============
an = None
for s in rep['steps']:
    e = s.get('envelope') or {}
    d = e.get('data') if isinstance(e, dict) else None
    if isinstance(d, dict) and 'top' in d and 'candidates' in d:
        an = d
for t, cm, dl, pl, c1, c2 in ((an['top'][3], '2021-02', 1.284945, 69.863, ('rates', 72.0), ('volatility', 18.4)),
                              (an['top'][4], '2020-01', 1.357685, 71.2329, ('rates', 68.3), ('volatility', 14.6))):
    top2 = [list(x) for x in sorted(((k, round(v['contribution_share'] * 100, 1)) for k, v in t['dims'].items()), key=lambda x: -x[1])[:2]]
    P.add(SA, 'report.json steps[analog].top[%d]: candidate_month/distance/distance_percentile/前2贡献维(%%, 舍入1位)' % (t['rank'] - 1),
          [t['candidate_month'], t['distance'], t['distance_percentile'], top2], [cm, dl, pl, [list(c1), list(c2)]],
          t['candidate_month'] == cm and P.eq(t['distance'], dl) and P.eq(t['distance_percentile'], pl) and top2 == [list(c1), list(c2)],
          where='FULL_REPORT.md 历史相似结构(读者版) rank %d' % t['rank'])

# ============ E. 日度相关 ============
gd = dict(F.series('US_REAL_GDP')); un = dict(F.series('UNEMPLOYMENT'))
common = sorted(d for d in gd if d in un)
xs = []; ys = []
for a, b in zip(common, common[1:]):
    xs.append(L.pct(gd[a], gd[b])); ys.append(un[b] - un[a])


def pear(xs, ys):
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return cov / math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))


pr = pear(xs, ys)
print('E 日度相关: 共同观测日', len(common), common[0], common[-1], '对数', len(xs), 'pearson %.6f' % pr)
P.add(S7, 'series_store.US_REAL_GDP(环比%%)×UNEMPLOYMENT(差分) 在共同观测日上的 pearson(共同窗 %s..%s)' % (common[0][:7], common[-1][:7]),
      [round(pr, 4), len(xs), common[0][:7], common[-1][:7]], [-0.8936, 37, '2017-01', '2026-07'],
      P.eq(pr, -0.8936) and len(xs) == 37 and common[0][:7] == '2017-01' and common[-1][:7] == '2026-07',
      where='FULL_REPORT.md 日度相关(引擎确定性面·读者版)')

# ============ F. 判断文本在各报告副本的一致性 ============


def strings(o, path='', skip_title=False):
    if isinstance(o, dict):
        for k, v in o.items():
            if skip_title and k == 'title':
                continue  # 标题标签字段: 报告不逐字渲染(单列计数)
            for x in strings(v, path + '.' + k, skip_title):
                yield x
    elif isinstance(o, list):
        for i, v in enumerate(o):
            for x in strings(v, path + '[%d]' % i, skip_title):
                yield x
    elif isinstance(o, str) and len(o) >= 12:
        yield path, o


for key, doc, nm in (('l3', FULL, 'FULL_REPORT.md'), ('l4', FULL, 'FULL_REPORT.md'), ('l3', REPM, 'report.md'), ('l4', REPM, 'report.md'),
                     ('reader_map', MAP, 'MAP_REPORT.md'), ('quality_gate_notes', MAP, 'MAP_REPORT.md(仅计数披露)')):
    ss = list(strings(aj[key], key, skip_title=True))
    miss = [(p, s) for p, s in ss if s not in doc]
    print('F %s -> %s: 字符串 %d, 未逐字出现 %d' % (key, nm, len(ss), len(miss)))
    for p, s in miss[:40]:
        print('    MISS', p, '|', s[:150].replace('\n', ' '))
    if key in ('l3', 'l4', 'reader_map'):
        chk_txt(ST, 'agent_judgment.%s 正文类字符串字段(不含 title 标签)在 %s 中逐字出现: 字段数/未出现数' % (key, nm), [len(ss), len(miss)], [len(ss), 0],
                len(miss) == 0, '%s 内联的 %s 文本' % (nm, key))
    else:
        P.add(ST, 'agent_judgment.%s 六条注记在三份报告中逐字渲染条数(观察项, 非数值比对)' % key, sum(1 for n in aj[key] if n in MAP or n in FULL or n in REPM), '非比对项', 'NA',
              where='MAP_REPORT.md / FULL_REPORT.md / report.md(注记仅存于 agent_judgment.json)')
ti = [x for x in strings(aj['l3'], 'l3') if x[0].endswith('.title')] + [x for x in strings(aj['l4'], 'l4') if x[0].endswith('.title')] + [x for x in strings(aj['reader_map'], 'reader_map') if x[0].endswith('.title')]
tin = sum(1 for _, v in ti if v in MAP or v in FULL or v in REPM)
print('F title 标签字段 %d 个, 其中逐字出现在任一报告 %d 个' % (len(ti), tin))
chk_txt(ST, 'agent_judgment 的 title 标签字段: 总数 / 逐字出现在任一报告的数量', [len(ti), tin], [len(ti), tin], True,
        '标签字段(非正文); 未渲染者=%s' % [p for p, v in ti if v not in MAP and v not in FULL and v not in REPM])

# ============ H. agent_declaration.basis 计数与类比簇独立性 ============
env = L.load(os.path.join(RUN, 'AGENT_SEAT_ENVELOPE.json'))
chk_txt(ST, 'agent_declaration.basis "证据索引(72行)": evidence_index.json 行数 / 工单 evidence_index_rows', [len(L.load(os.path.join(RUN, 'evidence_index.json'))), env['evidence_index_rows']], [72, 72],
        len(L.load(os.path.join(RUN, 'evidence_index.json'))) == 72 and env['evidence_index_rows'] == 72, 'agent_judgment.agent_declaration.basis')
chk_txt(ST, 'agent_declaration.basis "点值格(22格)": MAP 三时点表数据行数 / 工单 point_values_cells', [len([l for l in MAPL[15:47] if l.startswith('|')]) - 2, env['reader_map_contract']['engine_faces']['point_values_cells']], [22, 22],
        len([l for l in MAPL[15:47] if l.startswith('|')]) - 2 == 22 and env['reader_map_contract']['engine_faces']['point_values_cells'] == 22, '同上')
tms = sorted(int(t['candidate_month'][:4]) * 12 + int(t['candidate_month'][5:7]) for t in an['top'][:5])
ind = all(b - a >= 12 for a, b in zip(tms, tms[1:]))
print('H top5 候选月', [t['candidate_month'] for t in an['top'][:5]], '两两间隔>=12月', ind, '; dispersion.n_independent_clusters', an['dispersion'].get('n_independent_clusters'))
chk_txt(SA, 'agent_declaration "TOP-5独立簇": 前5名候选月两两间隔≥12个月; 引擎 dispersion.n_independent_clusters', [ind, an['dispersion'].get('n_independent_clusters')], [True, 5],
        ind and an['dispersion'].get('n_independent_clusters') == 5, 'MAP_REPORT.md 历史段标题("TOP-5独立簇第N") / agent_declaration.basis')

# ============ G. Gate A 缺口清单披露 ============
ga = snap['gate_a']
qg = [n for n in aj['quality_gate_notes'] if 'Gate A=DEGRADED' in n]
qg = qg[0] if qg else ''
mmiss = re.search(r'非核心缺口 (\S+) 项\(([^)]*)\)', qg); mdeg = re.search(r'非核心降级 (\S+) 项\(([^)]*)\)', qg)
mcore = re.search(r'核心缺口 (\S+) 项', qg); mstock = re.search(r'存量观测\(([^)]*)\)', qg)
NUM = {'零': 0, '一': 1, '两': 2, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
lm = mmiss.group(2).split('、') if mmiss else None; ld = mdeg.group(2).split('、') if mdeg else None; ls_ = mstock.group(1).split('、') if mstock else None
stock = [x for x in ga['noncore_missing'] if x in F.ss]
chk_txt(S11, 'quality_gate_notes "非核心缺口 七 项(…)": 项数与清单 ↔ snapshot.gate_a.noncore_missing',
        [NUM.get(mmiss.group(1), -1) if mmiss else None, lm], [len(ga['noncore_missing']), ga['noncore_missing']],
        bool(mmiss) and NUM.get(mmiss.group(1)) == len(ga['noncore_missing']) and lm == ga['noncore_missing'], 'agent_judgment.quality_gate_notes(数据面) / MAP_REPORT 数据门行')
chk_txt(S11, 'quality_gate_notes "非核心降级 八 项(…)": 项数与清单 ↔ snapshot.gate_a.noncore_degraded',
        [NUM.get(mdeg.group(1), -1) if mdeg else None, ld], [len(ga['noncore_degraded']), ga['noncore_degraded']],
        bool(mdeg) and NUM.get(mdeg.group(1)) == len(ga['noncore_degraded']) and ld == ga['noncore_degraded'], '同上')
chk_txt(S11, 'quality_gate_notes "核心缺口 零 项" ↔ snapshot.gate_a.core_missing; gate_a.status', [NUM.get(mcore.group(1), -1) if mcore else None, ga['status']],
        [0, 'DEGRADED'], bool(mcore) and NUM.get(mcore.group(1)) == 0 and ga['core_missing'] == [] and ga['status'] == 'DEGRADED', '同上')
chk_txt(S11, 'quality_gate_notes "缺口指标中 五 项在序列库内有存量观测(…)": 清单 ↔ gate_a.noncore_missing ∩ series_store', [ls_, len(ls_) if ls_ else None],
        [stock, 5], bool(mstock) and ls_ == stock and len(stock) == 5, '同上(存量观测引用的过期/降级披露)')
mline = [l for l in MAPL if l.startswith('- 数据门(Gate A')]
mm2 = re.search(r'非核心缺席 (.*?) \| 非核心降级 (.*?)——', mline[0]) if mline else None
chk_txt(S11, 'MAP_REPORT 数据门行 非核心缺席/非核心降级 清单 ↔ snapshot.gate_a', [mm2.group(1).split('、'), mm2.group(2).split('、')] if mm2 else None,
        [ga['noncore_missing'], ga['noncore_degraded']], bool(mm2) and mm2.group(1).split('、') == ga['noncore_missing'] and mm2.group(2).split('、') == ga['noncore_degraded'],
        'MAP_REPORT.md 数据门(Gate A)行')

print('tally', P.tally())
