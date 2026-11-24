# -*- coding: utf-8 -*-
# r10b_points.py — C 同比派生 / D 政策口径
# 用法: /usr/bin/python3 -I r10b_points.py <RUN_DIR> <SNAPSHOT_JSON> <OUT_JSON>
import sys, os, json, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from r00_common import *

RUN, SNAP, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
sn = Snap(load(SNAP))
aj = load(os.path.join(RUN, 'agent_judgment.json'))
cal = load(os.path.join(RUN, 'root_overlay', 'config', 'release_calendar.json'))
reg = load(os.path.join(RUN, 'root_overlay', 'config', 'metric_registry.json'))
PTS = []
EX = {}
CAT = ['']


def cat(c):
    CAT[0] = c


def P(pid, where, key, comp, rep, note='', tol=None):
    disp = round(comp, 6) if isinstance(comp, float) else comp
    ok = same(comp, rep, tol)
    PTS.append({'id': pid, 'cat': CAT[0], 'where': where, 'key': key, 'computed': disp,
                'reported': rep, 'ok': bool(ok), 'note': note})
    print('%s|%s|%s|comp=%s|rep=%s|%s|%s' % ('OK' if ok else 'XX', pid, CAT[0], disp, rep, where, note))
    return ok


def rhu(x):
    """四舍五入(半进)到整数。"""
    return int(math.floor(x + 0.5)) if x >= 0 else -int(math.floor(-x + 0.5))


cut = dt.date(2026, 11, 23)

# ---------------- C 同比派生 ----------------
cat('C 同比派生')
g2 = yoy(sn, 'US_REAL_GDP', '2026-04-01')
g3 = yoy(sn, 'US_REAL_GDP', '2026-07-01')
P('C01', 'US from_to「实际 GDP 同比 2026Q2 为 2.19%」', 'series_store.US_REAL_GDP: 2026-04-01 值 ÷ 2025-04-01 值 − 1', g2, 2.19)
P('C02', 'US from_to「2026Q3 为 2.07%」', 'series_store.US_REAL_GDP: 2026-07-01 值 ÷ 2025-07-01 值 − 1', g3, 2.07)
P('C03', 'C2 competing「实际 GDP 同比的小幅回落(2.19→2.07)」(方向须为回落)', '派生 GDP 同比 2026Q3 < 2026Q2', (g3 < g2) if (g2 is not None and g3 is not None) else None, True, note='未取整差=%.4fpp' % ((g3 - g2) if (g2 is not None and g3 is not None) else float('nan')))
P('C04', 'US from_to「失业率…(中间 2026-09 为 4.2)」', sn.key('UNEMPLOYMENT', '2026-09-01'), sn.val('UNEMPLOYMENT', '2026-09-01'), 4.2)
P('C05', 'US from_to「工业生产同比 1.25%(2026-07)」', 'series_store.INDPRO: 2026-07-01 ÷ 2025-07-01 − 1', yoy(sn, 'INDPRO', '2026-07-01'), 1.25)
P('C06', 'US from_to「→2.15%(2026-10)」', 'series_store.INDPRO: 2026-10-01 ÷ 2025-10-01 − 1', yoy(sn, 'INDPRO', '2026-10-01'), 2.15)
a, b = sn.val('INDPRO', '2026-07-01'), sn.val('INDPRO', '2026-10-01')
P('C07', 'US from_to「指数水平 103.1675→103.3954，仅 +0.22%」', 'series_store.INDPRO 2026-10-01 ÷ 2026-07-01 − 1', pct(a, b), 0.22)
P('C08', 'US from_to「2026-10 环比 -0.43%」', 'series_store.INDPRO 2026-10-01 ÷ 2026-09-01 − 1', pct(sn.val('INDPRO', '2026-09-01'), b), -0.43)
P('C09', 'US from_to「上年 2025-07→2025-10 基数下行 0.66%」', 'series_store.INDPRO 2025-10-01 ÷ 2025-07-01 − 1', pct(sn.val('INDPRO', '2025-07-01'), sn.val('INDPRO', '2025-10-01')), -0.66)
P('C10', 'US from_to「CPI 同比 3.3%(2026-07)」', 'series_store.CPI 2026-07-01 ÷ 2025-07-01 − 1', yoy(sn, 'CPI', '2026-07-01'), 3.3)
P('C11', '「→最近有效 3.72%(2026-09)」', 'series_store.CPI 2026-09-01 ÷ 2025-09-01 − 1', yoy(sn, 'CPI', '2026-09-01'), 3.72)
P('C12', '「2026-10 同比因缺上年同月基期观测不可得——2025-10 为序列库缺采」(2025-10 无观测)', sn.key('CPI', '2025-10-01'), sn.val('CPI', '2025-10-01'), None)
P('C13', '同上(CORE_CPI 2025-10 无观测)', sn.key('CORE_CPI', '2025-10-01'), sn.val('CORE_CPI', '2025-10-01'), None)
P('C14', '「最近有效同比」= 2026-09 (CPI 2026-10 同比不可得)', 'CPI 2026-10 同比派生', yoy(sn, 'CPI', '2026-10-01'), None)
P('C15', 'US from_to「核心 CPI 同比 2.47%(2026-07)」', 'series_store.CORE_CPI 2026-07-01 ÷ 2025-07-01 − 1', yoy(sn, 'CORE_CPI', '2026-07-01'), 2.47)
P('C16', '「→2.57%(2026-09)」', 'series_store.CORE_CPI 2026-09-01 ÷ 2025-09-01 − 1', yoy(sn, 'CORE_CPI', '2026-09-01'), 2.57)
P('C17', 'US from_to「核心 PCE 同比 3.04%(2026-06)」', 'series_store.CORE_PCE 2026-06-01 ÷ 2025-06-01 − 1', yoy(sn, 'CORE_PCE', '2026-06-01'), 3.04)
P('C18', '「→3.12%(2026-09)」', 'series_store.CORE_PCE 2026-09-01 ÷ 2025-09-01 − 1', yoy(sn, 'CORE_PCE', '2026-09-01'), 3.12)
# 路径(供阅读)
path = {}
for sid in ['CPI', 'CORE_CPI', 'CORE_PCE', 'INDPRO']:
    d = dt.date(2025, 1, 1)
    path[sid] = {}
    while d <= dt.date(2026, 10, 1):
        path[sid][d.isoformat()] = None if yoy(sn, sid, d) is None else round(yoy(sn, sid, d), 4)
        d = add_months(d, 1)
path['EA_HICP_YOY'] = {a.isoformat(): v for a, v in sn.series('EA_HICP_YOY') if a >= dt.date(2025, 1, 1)}
path['UNEMPLOYMENT'] = {a.isoformat(): v for a, v in sn.series('UNEMPLOYMENT') if a >= dt.date(2025, 1, 1)}
path['US_REAL_GDP'] = {a.isoformat(): v for a, v in sn.series('US_REAL_GDP') if a >= dt.date(2025, 1, 1)}
path['EA_REAL_GDP_YOY'] = {a.isoformat(): v for a, v in sn.series('EA_REAL_GDP_YOY') if a >= dt.date(2025, 1, 1)}
EX['paths'] = path
y08c = yoy(sn, 'CPI', '2026-08-01')
y09c = yoy(sn, 'CPI', '2026-09-01')
P('C19', '传导环1「美国 CPI 同比 2026-09 回升至 3.72」(回升=高于 2026-08)', '派生 CPI 同比 2026-08 < 2026-09', (y08c < y09c), True, note='2026-08=%.4f 2026-09=%.4f' % (y08c, y09c))
P('C20', '传导环1「仍低于 2026-05 高点 4.17」', 'series_store.CPI 2026-05-01 ÷ 2025-05-01 − 1', yoy(sn, 'CPI', '2026-05-01'), 4.17)
P('C21', 'turnings[0]「CPI 同比 2026-02 2.434」', 'series_store.CPI 2026-02-01 ÷ 2025-02-01 − 1', yoy(sn, 'CPI', '2026-02-01'), 2.434)
P('C22', 'turnings[0]「2026-05 4.1666」', 'series_store.CPI 2026-05-01 ÷ 2025-05-01 − 1', yoy(sn, 'CPI', '2026-05-01'), 4.1666)
P('C23', 'turnings[0] narrative「三个月上行 1.7326 个百分点」', 'C22 − C21', (yoy(sn, 'CPI', '2026-05-01') - yoy(sn, 'CPI', '2026-02-01')), 1.7326)
P('C24', '「CORE_CPI 同比 2026-02 2.4725」', 'series_store.CORE_CPI 2026-02-01 ÷ 2025-02-01 − 1', yoy(sn, 'CORE_CPI', '2026-02-01'), 2.4725)
P('C25', '「2026-05 2.8229」', 'series_store.CORE_CPI 2026-05-01 ÷ 2025-05-01 − 1', yoy(sn, 'CORE_CPI', '2026-05-01'), 2.8229)
P('C26', '「2026-08 2.4462」', 'series_store.CORE_CPI 2026-08-01 ÷ 2025-08-01 − 1', yoy(sn, 'CORE_CPI', '2026-08-01'), 2.4462)
P('C27', '「2026-09 回升至 2.5658」', 'series_store.CORE_CPI 2026-09-01 ÷ 2025-09-01 − 1', yoy(sn, 'CORE_CPI', '2026-09-01'), 2.5658)
P('C28', 'turnings[1]「INDPRO 同比 2025-11 1.7543」', 'series_store.INDPRO 2025-11-01 ÷ 2024-11-01 − 1', yoy(sn, 'INDPRO', '2025-11-01'), 1.7543)
P('C29', '「2026-02 0.7972」', 'series_store.INDPRO 2026-02-01 ÷ 2025-02-01 − 1', yoy(sn, 'INDPRO', '2026-02-01'), 0.7972)
P('C30', '「三个月变动 -0.9571」', 'C29 − C28', (yoy(sn, 'INDPRO', '2026-02-01') - yoy(sn, 'INDPRO', '2025-11-01')), -0.9571)
ip = {a: yoy(sn, 'INDPRO', a) for a, _ in sn.series('INDPRO') if dt.date(2026, 1, 1) <= a <= dt.date(2026, 10, 1)}
trough = min(ip, key=lambda k: ip[k])
P('C31', 'turnings[1]「2026-03 见底后回升」(2026-01..10 同比最低月)', 'INDPRO 同比路径', trough.isoformat(), '2026-03-01')
P('C32', 'turnings[1]「同一窗口美国失业率由 4.5 降至 4.4(2026-02)」', sn.key('UNEMPLOYMENT', '2025-11-01'), sn.val('UNEMPLOYMENT', '2025-11-01'), 4.5)
P('C33', '同上(2026-02 为 4.4)', sn.key('UNEMPLOYMENT', '2026-02-01'), sn.val('UNEMPLOYMENT', '2026-02-01'), 4.4)
ea = {a: v for a, v in sn.series('EA_HICP_YOY')}
P('C34', 'EA from_to「自 2026-02 的 1.9」', sn.key('EA_HICP_YOY', '2026-02-01'), ea.get(dt.date(2026, 2, 1)), 1.9)
P('C35', '「抬升至 2026-05 的 3.2」', sn.key('EA_HICP_YOY', '2026-05-01'), ea.get(dt.date(2026, 5, 1)), 3.2)
P('C36', '「2026-06 回落至 2.8」', sn.key('EA_HICP_YOY', '2026-06-01'), ea.get(dt.date(2026, 6, 1)), 2.8)
P('C37', 'turnings[0]「欧元区 HICP 同比同窗上行 1.3 个百分点」', 'C35 − C34', (ea[dt.date(2026, 5, 1)] - ea[dt.date(2026, 2, 1)]), 1.3)
y26 = {a: v for a, v in ea.items() if a.year == 2026}
mx = max(y26.values())
P('C38', '「2026-10 的 4.0，读数为年内新高」', 'EA_HICP_YOY 2026-01..10 最大值及月份', '%s@%s' % (mx, ','.join(sorted(a.isoformat()[:7] for a, v in y26.items() if v == mx))), '4.0@2026-10')
P('C39', '同上(年内新高须严格高于 2026-09)', 'EA_HICP_YOY 2026-10 > 2026-09', (ea[dt.date(2026, 10, 1)] > ea[dt.date(2026, 9, 1)]), True, note='2026-09=%s' % ea.get(dt.date(2026, 9, 1)))
P('C40', 'EA from_to「HICP 同比 2.9%(2026-07)→4.0%(2026-10),三个月上行 1.1 个百分点」', 'EA_HICP_YOY 2026-10 − 2026-07', (ea[dt.date(2026, 10, 1)] - ea[dt.date(2026, 7, 1)]), 1.1)
# 美欧逐月对比(美国 CPI 同比为派生口径)
us = {}
d = dt.date(2017, 11, 1)
while d <= dt.date(2026, 10, 1):
    yv = yoy(sn, 'CPI', d)
    if yv is not None:
        us[d] = yv
    d = add_months(d, 1)
gt = sorted(k for k in us if k in ea and ea[k] > us[k])
EX['ea_gt_us'] = [k.isoformat()[:7] for k in gt]
rng1 = [k for k in gt if dt.date(2022, 7, 1) <= k <= dt.date(2023, 9, 1)]
P('C41', 'C1「2022-07 至 2023-09 曾持续高于美国」(该区间 15 个月全部 EA>US)', 'EA_HICP_YOY[m] > 派生 CPI 同比[m] 的月份数(2022-07..2023-09)', len(rng1), 15)
rng2 = [k for k in gt if dt.date(2023, 10, 1) <= k <= dt.date(2026, 8, 1)]
P('C42', 'C1「为 2023-09 以来首个高于美国的可比月份」(2023-10..2026-08 无 EA>US)', '2023-10..2026-08 中 EA>US 月份数', len(rng2), 0)
m09 = (ea[dt.date(2026, 9, 1)] - us[dt.date(2026, 9, 1)]) if dt.date(2026, 9, 1) in us else None
P('C43', 'C1「最新可比同月(九月)欧元区高于美国」', 'EA_HICP_YOY 2026-09 > 派生 CPI 同比 2026-09', (m09 > 0) if m09 is not None else None, True, note='幅度=%.4fpp; EA=%s US=%s' % (m09 if m09 is not None else float('nan'), ea.get(dt.date(2026, 9, 1)), r(us.get(dt.date(2026, 9, 1)), 4)))
P('C44', 'C1「仅略高、幅度很小」(幅度 ≤ 0.3pp 为判据)', '同上', (m09 <= 0.3) if m09 is not None else None, True)
P('C45', '2026-10 无美国可比同比(两地上月不可比)', '派生 CPI 同比 2026-10', yoy(sn, 'CPI', '2026-10-01'), None)
dci = yoy(sn, 'CPI', '2026-09-01') - yoy(sn, 'CPI', '2026-07-01')
dcc = yoy(sn, 'CORE_CPI', '2026-09-01') - yoy(sn, 'CORE_CPI', '2026-07-01')
P('C46', 'C1「美国 headline 与核心口径同向上行」(2026-07→2026-09)', '派生同比差 2026-09−2026-07: CPI>0 且 CORE_CPI>0', (dci > 0 and dcc > 0), True, note='CPI 差=%.4fpp, CORE 差=%.4fpp' % (dci, dcc))
hcg = yoy(sn, 'CPI', '2026-09-01') - yoy(sn, 'CORE_CPI', '2026-09-01')
P('C47', 'US from_to「headline 强于核心」(2026-09: 3.72 > 2.57)', 'CPI 同比 − CORE_CPI 同比 (pp, 2026-09) > 0', (hcg > 0), True, note='差=%.4fpp' % hcg)
P('C48', 'EA from_to「实际 GDP 同比 2026Q2 为 1.19%」', sn.key('EA_REAL_GDP_YOY', '2026-04-01'), sn.val('EA_REAL_GDP_YOY', '2026-04-01'), 1.19)
P('C49', '「2026Q3 为 1.28%」', sn.key('EA_REAL_GDP_YOY', '2026-07-01'), sn.val('EA_REAL_GDP_YOY', '2026-07-01'), 1.28)

# ---------------- D 政策口径 ----------------
cat('D 政策口径')
hits = find_dicts_with_value(cal, 'RC-JP-BOJ-TARGET-2026-09')
e = hits[0][1] if hits else {}
EX['cal_jp_target'] = e
P('D01', 'C3「2026-09-18 决议」', 'release_calendar RC-JP-BOJ-TARGET-2026-09.decision_date', e.get('decision_date'), '2026-09-18')
P('D02', 'C3「2026-09-24 生效」', 'release_calendar RC-JP-BOJ-TARGET-2026-09.effective_on', e.get('effective_on'), '2026-09-24')
P('D03', 'C3「日本央行政策目标利率约一点二五」', 'release_calendar RC-JP-BOJ-TARGET-2026-09.target_value', e.get('target_value'), 1.25)
hits2 = find_dicts_with_value(cal, 'RC-JP-BOJ-MAINT-2026-10')
e2 = hits2[0][1] if hits2 else {}
EX['cal_jp_maint'] = e2
P('D04', 'C3「2026-10-30 会议确认维持不变」', 'release_calendar RC-JP-BOJ-MAINT-2026-10.decision_date', e2.get('decision_date'), '2026-10-30')
P('D05', 'quality_gate_notes[2]「维持条目无生效日」', 'RC-JP-BOJ-MAINT-2026-10.effective_on', e2.get('effective_on'), None)
P('D06', 'C3「距上次调整按生效日六十天」', '2026-11-23 − 2026-09-24', (cut - dt.date(2026, 9, 24)).days, 60)
P('D07', 'C3「按决议日六十六天」', '2026-11-23 − 2026-09-18', (cut - dt.date(2026, 9, 18)).days, 66)
P('D08', 'headline「其后至截止日的 24 天引擎日历无条目」', '2026-11-23 − 2026-10-30', (cut - dt.date(2026, 10, 30)).days, 24)
pk = []


def walk(o):
    if isinstance(o, dict):
        if str(o.get('kind', '')).startswith('policy'):
            pk.append(o)
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(cal)
EX['cal_policy_entries'] = pk
P('D09', 'turnings[2]「发布日历政策条目仅 2 条、均为日本央行实录」', 'release_calendar: kind 以 policy 开头的条目数', len(pk), 2)
P('D10', 'quality_gate_notes[2]「冻结日历无美欧决议/生效实录条目」', 'release_calendar: 全部政策条目均含 JP/日本', all(('JP' in json.dumps(x, ensure_ascii=False)) or ('日本' in json.dumps(x, ensure_ascii=False)) for x in pk), True)
jpm = {}
m = dt.date(2025, 11, 1)
while m <= dt.date(2026, 10, 1):
    jpm[m] = sn.val('JP_POLICY_RATE', m)
    m = add_months(m, 1)
EX['jp_monthly'] = {k.isoformat(): v for k, v in jpm.items()}
claims = [('2025-11', 0.478, 'M1环1「2025-11 的 0.478(窗启时在值)」'), ('2025-12', 0.557, 'M1环1「经 2025-12 的 0.557」'),
          ('2026-01', 0.728, '「2026-01 0.728」'), ('2026-06', 0.841, '「2026-06 0.841」'), ('2026-07', 0.978, '「2026-07 0.978」'),
          ('2026-08', 0.977, 'C3「2026-08 月均 0.977」'), ('2026-09', 1.043, '「2026-09 1.043」'), ('2026-10', 1.227, '「2026-10 1.227」')]
for i, (ym, v, w) in enumerate(claims):
    dd = D(ym + '-01')
    P('D%02d' % (11 + i), w, sn.key('JP_POLICY_RATE', dd), jpm.get(dd), v)
P('D19', 'turnings[2]「2026-04 0.727」', sn.key('JP_POLICY_RATE', '2026-04-01'), jpm.get(dt.date(2026, 4, 1)), 0.727)
for i, ym in enumerate(['2026-02', '2026-03', '2026-04', '2026-05']):
    dd = D(ym + '-01')
    P('D%02d' % (20 + i), 'C3「2026-02 至 2026-05 …相邻月均差均不超过 0.001」(%s 对 2026-01)' % ym,
      'series_store.JP_POLICY_RATE %s − 2026-01' % ym, jpm.get(dd), jpm.get(dt.date(2026, 1, 1)), tol=0.0010001)
P('D24', 'C3「2026-08 …相邻月均差均不超过 0.001」(2026-08 对 2026-07)', 'series_store.JP_POLICY_RATE 2026-08 − 2026-07', jpm.get(dt.date(2026, 8, 1)), jpm.get(dt.date(2026, 7, 1)), tol=0.0010001)
ms = sorted(jpm)
diffs = {ms[i]: (jpm[ms[i]] - jpm[ms[i - 1]]) * 100.0 for i in range(1, len(ms))}
EX['jp_diffs_bp'] = {k.isoformat(): round(v, 6) for k, v in diffs.items()}
steps = {k: v for k, v in diffs.items() if abs(v) >= 0.5}
P('D25', 'C3「窗内六个变动点」', 'JP_POLICY_RATE 相邻月均差(bp), |差|≥0.5 计为变动点', len(steps), 6, note='变动点月=%s' % ','.join(k.isoformat()[:7] for k in steps))
P('D26', 'M1环1「六步直和 75.1bp」', '各变动点月均差之和(bp, 全精度)', sum(steps.values()), 75.1)
P('D27', 'M1环1「窗启至窗末端点差 74.9bp」', '(1.227 − 0.478) × 100', (jpm[dt.date(2026, 10, 1)] - jpm[dt.date(2025, 11, 1)]) * 100.0, 74.9)
P('D28', 'M1环1「均取整为 +75bp」(变动点取整 bp 之和)', 'Σ round(变动点月均差)', float(sum(rhu(v) for v in steps.values())), 75)
P('D29', '「仅自窗内首观测(2025-12 月均)起算为 +67bp」', '(1.227 − 0.557) × 100', (jpm[dt.date(2026, 10, 1)] - jpm[dt.date(2025, 12, 1)]) * 100.0, 67)
P('D30', 'turnings[2]「2026-01 +17bp」', 'JP_POLICY_RATE 2026-01 − 2025-12 (bp)', diffs.get(dt.date(2026, 1, 1)), 17)
P('D31', 'turnings[2]「2026-06 +11bp」', 'JP_POLICY_RATE 2026-06 − 2026-05 (bp)', diffs.get(dt.date(2026, 6, 1)), 11)
P('D32', '「2026-09 1.043(+7bp)」', 'JP_POLICY_RATE 2026-09 − 2026-08 (bp)', diffs.get(dt.date(2026, 9, 1)), 7)
P('D33', '「2026-10 1.227(+18bp)」', 'JP_POLICY_RATE 2026-10 − 2026-09 (bp)', diffs.get(dt.date(2026, 10, 1)), 18)
st26 = [k for k in steps if k.year == 2026 and k <= dt.date(2026, 7, 1)]
P('D34', 'turnings[2]「2026-07 为 2026 年内第三个上行月均台阶」', '2026 年内至 2026-07 的变动点序号', len(st26), 3)
P('D35', 'C3「已见台阶均不小于 0.066」', 'min(变动点月均差, bp)', (min(steps.values()) >= 0.066 - 1e-9), True, note='min=%.6f' % min(steps.values()))
flats = [abs(round(v / 100.0, 6)) for v in diffs.values() if abs(v) < 0.5]  # 单位: 百分点
P('D36', 'C3「持平月份的相邻月均差均不超过 0.001」(12 个月窗内非变动点月份, 单位百分点)', 'max(|非变动点相邻月均差|, pp)', (max(flats) <= 0.001 + 1e-12) if flats else None, True, note='max=%.6f pp; 非变动点月数=%d' % (max(flats) if flats else -1, len(flats)))
P('D37', 'C3「2026-10 月均 1.227 较目标水平 1.25 低 0.023」', '1.25 − 1.227', 1.25 - jpm[dt.date(2026, 10, 1)], 0.023)
P('D38', 'C3「可观察带宽 1.197」', '1.227 − 0.03', jpm[dt.date(2026, 10, 1)] - 0.03, 1.197)
P('D39', 'C3「至 1.257」', '1.227 + 0.03', jpm[dt.date(2026, 10, 1)] + 0.03, 1.257)
P('D40', 'C3「次月为决议生效后首个整月」(2026-09-24 生效 → 2026-10 为首个整月)', '日历推理: 生效日所在月 2026-09 非整月, 次月 2026-10 整月', (D(e.get('effective_on')) < dt.date(2026, 10, 1)), True)


def transitions(sid):
    s = sn.series(sid)
    out = []
    for i in range(1, len(s)):
        if s[i][1] != s[i - 1][1]:
            out.append((s[i][0].isoformat(), s[i - 1][1], s[i][1]))
    return out


tr = transitions('DFEDTARU')
EX['dfedtaru_trans'] = tr[-5:]
lt = tr[-1] if tr else None
P('D41', '「美联储目标区间上限 3.75→4.00 于 2026-09-17」', 'series_store.DFEDTARU 最近一次变动(首现日, 旧值→新值)', '%s %s→%s' % lt, '2026-09-17 3.75→4.0')
tr2 = transitions('ECB_DFR')
EX['ecb_dfr_trans'] = tr2[-5:]
lt2 = tr2[-1] if tr2 else None
P('D42', '「欧央行存款便利利率 2.25→2.50 于 2026-09-16」', 'series_store.ECB_DFR 最近一次变动', '%s %s→%s' % lt2, '2026-09-16 2.25→2.5')
facts = sn.sn.get('facts', [])
jg = [f for f in facts if 'JGB' in json.dumps(f, ensure_ascii=False)]
EX['jgb_facts'] = jg
vals = sorted([f.get('value') for f in jg if isinstance(f.get('value'), (int, float))])
P('D43', 'M1环2「快照事实面仅有 2026-11-19 点值 JGB 2/5/10 年 1.853/2.235/2.87」', 'snapshot.facts[JGB*].value', ','.join(str(v) for v in vals), '1.853,2.235,2.87')
P('D44', '同上(点值日期均为 2026-11-19)', 'snapshot.facts[JGB*].observation_date', ','.join(sorted({str(f.get('observation_date') or '') for f in jg})), '2026-11-19')
P('D45', 'M1环2「序列库无历史」(series_store 无 JGB 序列)', 'series_store 键', (not any(k.startswith('JGB') for k in sn.ids())), True)
P('D46', '「宣布目标序列 JP_POLICY_TARGET 在引擎注册表不可得」', 'metric_registry 文本检索', ('JP_POLICY_TARGET' in json.dumps(reg, ensure_ascii=False)), False)
last_u = sn.last('USDJPY')
P('D47', 'C3「USDJPY 水平为 159.35(观测 2026-11-23)」', sn.key('USDJPY', last_u[0]), round(last_u[1], 2), 159.35)
P('D48', 'C3「JP_POLICY_RATE 12 个月窗: 2025-11-23..2026-11-23」(截止日 − 1 年)', '2026-11-23 − 1 年', minus_year(cut).isoformat(), '2025-11-23')

json.dump({'points': PTS, 'extra': EX}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('POINTS', len(PTS), 'MISMATCH', sum(1 for p in PTS if not p['ok']))
