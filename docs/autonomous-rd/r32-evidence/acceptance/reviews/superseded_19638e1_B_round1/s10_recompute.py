#!/usr/bin/python3 -I
# -*- coding: utf-8 -*-
"""Audit-R32 正式使用验收 · B · Round-1 · 独立语义审查席 逐点复算脚本(只读)

用法:
  /usr/bin/python3 -I s10_recompute.py <snapshot.json> <release_calendar.json>
      <metric_registry.json> <report.json> <agent_judgment.json> <evidence_index.json>
      <MAP_REPORT.md> <CODE_VERSION.json> <outdir>

全部输入只读; 输出 <outdir>/recompute_points.json 与 <outdir>/recompute_probes.json。
每个复算点: 先从冻结快照 series_store / 冻结日历 / report.json 引擎面直算,
再与判断档(agent_judgment.json)文字比对。literal=受审文本里的原文字面, 脚本同时断言
该字面确实出现在受审文本中(防止本席转述失真); cell=引擎格值, 同时断言直算值与格一致。
"""
import json, sys, re, os
import calendar as _cal
import datetime as _dt
from zoneinfo import ZoneInfo

(SNAP, CAL, REG, REP, AJ, EVI, MAPR, CODEV, OUT) = sys.argv[1:10]


def _load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


snap = _load(SNAP)
cal = _load(CAL)
reg = _load(REG)
rep = _load(REP)
aj = _load(AJ)
evi = _load(EVI)
codev = _load(CODEV)
with open(MAPR, encoding='utf-8') as f:
    mapr = f.read()
AJT = json.dumps(aj, ensure_ascii=False)   # 受审判断档全文(序列化文本)

ss = snap['series_store']
regmap = {m['metric_id']: m for m in reg['metrics']}
CUTOFF = '2026-11-23'


def S(m):
    s = ss[m]
    return dict(zip(s['dates'], s['values']))


def v_at(m, d):
    return S(m).get(d)


def month_end(y, m):
    return _dt.date(y, m, _cal.monthrange(y, m)[1])


# 发布纪律: 引擎 RELEASE_RULES(research_map_planner.py 同表), 冻结日历条目优先于推定规则
RULES = {
    'CPI': ('monthly', 13), 'CORE_CPI': ('monthly', 13), 'CORE_PCE': ('monthly', 30),
    'UNEMPLOYMENT': ('monthly', 5), 'INDPRO': ('monthly', 15),
    'US_REAL_GDP': ('quarterly', 29), 'EA_HICP_YOY': ('monthly', 16),
    'EA_REAL_GDP_YOY': ('quarterly', 35), 'JP_POLICY_RATE': ('monthly', 5),
}


def period_end(metric, obs):
    d = _dt.date.fromisoformat(obs)
    if RULES[metric][0] == 'quarterly':
        return month_end(d.year, d.month + 2)
    return month_end(d.year, d.month)


def rule_pub(metric, obs):
    return (period_end(metric, obs) + _dt.timedelta(days=RULES[metric][1])).isoformat()


def cal_pub(metric, obs):
    best = None
    for e in cal['entries']:
        ids = ([e['metric_id']] if e.get('metric_id') else []) + (e.get('metric_ids') or [])
        if metric in ids and e.get('obs_from') and e.get('obs_to') and e['obs_from'] <= obs <= e['obs_to']:
            fp = e.get('first_publish_on_or_after')
            if fp and (best is None or fp > best):
                best = fp
    return best


def pub(metric, obs):
    p = rule_pub(metric, obs)
    c = cal_pub(metric, obs)
    return max(p, c) if c else p


def anchor(metric, as_of):
    """锚格值=发布日≤锚日的最新观测(发布纪律)。"""
    cands = [(d, v) for d, v in zip(ss[metric]['dates'], ss[metric]['values'])
             if v is not None and pub(metric, d) <= as_of]
    return max(cands) if cands else (None, None)


def base_of(obs):
    d = _dt.date.fromisoformat(obs)
    return '%04d-%02d-01' % (d.year - 1, d.month)


def yoy(metric, obs):
    """同比: 只配去年同月/同季基期, 基期缺席返回 None。"""
    base = base_of(obs)
    s = S(metric)
    if obs not in s or base not in s or s[obs] is None or s[base] is None:
        return None
    return (s[obs] / s[base] - 1.0) * 100.0


def latest_valid_yoy(metric, as_of):
    s = S(metric)
    best = None
    for d in sorted(s):
        if s[d] is not None and pub(metric, d) <= as_of and yoy(metric, d) is not None:
            best = d
    return (best, yoy(metric, best)) if best else (None, None)


def pct_chg(m, d0, d1):
    a, b = v_at(m, d0), v_at(m, d1)
    return None if a is None or b is None else (b / a - 1.0) * 100.0


def bp_chg(m, d0, d1):
    a, b = v_at(m, d0), v_at(m, d1)
    return None if a is None or b is None else (b - a) * 100.0


def days_between(a, b):
    return (_dt.date.fromisoformat(b) - _dt.date.fromisoformat(a)).days


# ── 复算点登记 ──────────────────────────────────────────────────────────────
PTS = []


def add(cat, desc, src, comp, repv, nd=None, literal=None, where='aj', cell=None, note=''):
    """comp=直算值; repv=报告/判断档值; nd=小数位(数值比较); literal=受审文本原字面。"""
    if isinstance(comp, str) or isinstance(repv, str) or comp is None or repv is None \
            or (nd is None and not isinstance(comp, (int, float))):
        ok = (comp == repv)
        how = '等值比较'
    else:
        diff = abs(comp - repv)
        if nd is None:
            ok, how = diff < 1e-9, '精确'
        elif diff <= 0.5 * 10 ** (-nd) + 1e-9:
            ok, how = True, '四舍五入一致(差 %.3g)' % diff
        elif diff <= 1.5 * 10 ** (-nd) + 1e-9:
            ok, how = True, '截断/舍入容差内(差 %.3g)' % diff
        else:
            ok, how = False, '偏离(差 %.3g)' % diff
    lit_ok = True
    if literal is not None:
        text = AJT if where == 'aj' else mapr
        lit_ok = (literal in text)
    cell_ok = True
    if cell is not None:
        if isinstance(cell, str) or isinstance(comp, str):
            cell_ok = (cell == comp)
        else:
            cell_ok = abs(cell - comp) <= 0.5 * 10 ** (-(nd if nd is not None else 6)) + 1e-9
    PTS.append({
        'id': 'P%03d' % (len(PTS) + 1), 'cat': cat, 'desc': desc, 'src': src,
        'computed': comp, 'reported': repv, 'engine_cell': cell,
        'ok': bool(ok and lit_ok and cell_ok),
        'value_ok': bool(ok), 'literal_found': lit_ok if literal is not None else None,
        'cell_ok': bool(cell_ok) if cell is not None else None,
        'how': how, 'literal': literal, 'note': note,
    })
    return ok


def _fm(x):
    if isinstance(x, float):
        return ('%.6g' % x)
    return json.dumps(x, ensure_ascii=False)


# ══ ① 研究截止日 ══════════════════════════════════════════════════════════════
K = '①截止日'
ra_iso = snap.get('research_as_of')
add(K, '研究截止时间戳 research_as_of', 'snapshot.research_as_of', ra_iso,
    '2026-11-23T22:53:47+08:00', literal='2026-11-23T22:53:47+08:00')
td = str(snap.get('target_date'))
add(K, '快照 target_date(=研究截止日)', 'snapshot.target_date',
    '%s-%s-%s' % (td[:4], td[4:6], td[6:8]), '2026-11-23', literal='研究截止日=快照版本日 2026-11-23')
add(K, '引擎 cutoff', 'report.json research_plan.cutoff', rep['research_plan'].get('cutoff'), '2026-11-23')
add(K, '引擎 evidence_asof', 'report.json run.evidence_asof', rep['run'].get('evidence_asof'), '2026-11-23')
add(K, '引擎 ts_utc(运行号)', 'report.json run.ts_utc', rep['run'].get('ts_utc'), '20261123T145819Z')
add(K, '代码印章 run.git_head', 'report.json run.git_head', rep['run'].get('git_head'),
    '19638e1487e1e5729b9645ce621c3435d0635d08')
add(K, '安装树 CODE_VERSION.git_head', 'CODE_VERSION.json git_head', codev.get('git_head'),
    '19638e1487e1e5729b9645ce621c3435d0635d08')
ra = _dt.datetime.fromisoformat(ra_iso)
for zone, label, exp in [('America/New_York', '纽约', '09:53'), ('Europe/Berlin', '法兰克福', '15:53'),
                         ('Asia/Tokyo', '东京', '23:53'), ('Asia/Shanghai', '上海', '22:53')]:
    loc = ra.astimezone(ZoneInfo(zone))
    add(K, '截止时点当地时间·' + label, 'snapshot.research_as_of → zoneinfo ' + zone,
        loc.strftime('%H:%M'), exp, literal='%s %s' % (label, exp))
all_dates = sorted(set(re.findall(r'\d{4}-\d{2}-\d{2}', AJT)))
late = [d for d in all_dates if d > CUTOFF]
add(K, '判断档全文中晚于截止日的日期集合(只允许情景期限)', 'agent_judgment.json 全文正则',
    ','.join(late), '2027-02-15')
add(K, '判断档引用的最大观测日', 'agent_judgment.json 全文正则',
    max(d for d in all_dates if d <= CUTOFF), '2026-11-23')
pdf = rep['research_plan'].get('policy_doc_facts') or []
add(K, 'FOMC 纪要文档事实发布日', 'report.json research_plan.policy_doc_facts[0].published_on',
    pdf[0].get('published_on') if pdf else None, '2026-11-18', literal='2026-11-18 发布')
add(K, 'FOMC 纪要文档事实 doc_id', 'research_plan.policy_doc_facts[0].doc_id',
    pdf[0].get('doc_id') if pdf else None, 'FOMC-MINUTES-2026-10', literal='FOMC-MINUTES-2026-10')
add(K, '纪要发布日≤截止日', 'policy_doc_facts[0].published_on vs cutoff',
    (pdf[0]['published_on'] <= CUTOFF) if pdf else None, True)
add(K, '政策事件簇为空', 'research_plan.policy_event_clusters.clusters',
    len((rep['research_plan'].get('policy_event_clusters') or {}).get('clusters') or []), 0, 0,
    literal='政策事件簇为空')

# ══ ④ 政策面(冻结日历) ═════════════════════════════════════════════════════════
K = '④政策面'
pol = [e for e in cal['entries'] if e.get('kind') in ('policy_decision', 'policy_maintenance')]
dec = [e for e in pol if e.get('entry_id') == 'RC-JP-BOJ-TARGET-2026-09'][0]
mnt = [e for e in pol if e.get('entry_id') == 'RC-JP-BOJ-MAINT-2026-10'][0]
add(K, '日历版本', 'release_calendar.json version', cal.get('version'), '1.5.0',
    literal='冻结发布日历 v1.5.0')
add(K, '政策类日历条目数', 'release_calendar.json entries[kind∈policy_*]', len(pol), 2, 0,
    literal='发布日历政策条目仅 2 条、均为日本央行实录')
add(K, '政策类条目全部为日本央行(JP_POLICY_TARGET)', 'entries[kind∈policy_*].metric_id',
    ','.join(sorted(set(e.get('metric_id') for e in pol))), 'JP_POLICY_TARGET')
add(K, '无美欧决议/生效实录条目', 'entries[kind∈policy_*] 是否含 US/EA 指标',
    any(e.get('metric_id') not in ('JP_POLICY_TARGET',) for e in pol), False,
    literal='冻结日历无美欧决议/生效实录条目')
add(K, '日本央行决议日', 'calendar RC-JP-BOJ-TARGET-2026-09.decision_date', dec.get('decision_date'),
    '2026-09-18', literal='2026-09-18 决议')
add(K, '日本央行生效日', 'calendar RC-JP-BOJ-TARGET-2026-09.effective_on', dec.get('effective_on'),
    '2026-09-24', literal='2026-09-24 生效')
add(K, '日本央行目标水平', 'calendar RC-JP-BOJ-TARGET-2026-09.target_value', dec.get('target_value'),
    1.25, 2, literal='官方政策目标利率约 1.25(2026-09-18 决议')
add(K, '日本央行目标水平(判断档中文数字写法)', 'calendar target_value vs 判断档「约一点二五」',
    dec.get('target_value'), 1.25, 2, literal='日本央行政策目标利率约一点二五,2026-09-18 决议、2026-09-24 生效')
add(K, '维持会议日期', 'calendar RC-JP-BOJ-MAINT-2026-10.decision_date', mnt.get('decision_date'),
    '2026-10-30', literal='2026-10-30 会议确认维持不变(RC-JP-BOJ-MAINT-2026-10)')
add(K, '维持条目目标值不变', 'calendar RC-JP-BOJ-MAINT-2026-10.target_value', mnt.get('target_value'),
    1.25, 2, literal='2026-10-30 会议确认维持不变')
add(K, '维持条目无生效日', 'calendar RC-JP-BOJ-MAINT-2026-10.effective_on', mnt.get('effective_on'),
    None, literal='维持条目无生效日')
add(K, '决议条目 first_publish=决议日', 'calendar RC-JP-BOJ-TARGET-2026-09.first_publish_on_or_after',
    dec.get('first_publish_on_or_after'), dec.get('decision_date'))
add(K, '距上次调整·按生效日(天)', '截止日 − RC-JP-BOJ-TARGET-2026-09.effective_on',
    days_between(dec['effective_on'], CUTOFF), 60, 0, literal='距上次调整按生效日 60 天')
add(K, '距上次调整·按决议日(天)', '截止日 − decision_date',
    days_between(dec['decision_date'], CUTOFF), 66, 0, literal='按决议日 66 天')
add(K, '距上次调整·按生效日(中文数字写法)', '截止日 − effective_on',
    days_between(dec['effective_on'], CUTOFF), 60, 0, literal='距上次调整按生效日六十天、按决议日六十六天')
add(K, '距上次调整·按决议日(中文数字写法)', '截止日 − decision_date',
    days_between(dec['decision_date'], CUTOFF), 66, 0, literal='按决议日六十六天')
add(K, '距维持会议(天)', '截止日 − RC-JP-BOJ-MAINT-2026-10.decision_date',
    days_between(mnt['decision_date'], CUTOFF), 24, 0, where='map',
    literal='| 日本 | 1.25 | — | 2026-09-18 | 2026-09-24 | 2026-10-30 | 2026-10-30 | 60天 | 66天 | 24天 |')
add(K, '生效日落在 2026-09 最后一周', 'calendar effective_on 所在月余天数',
    days_between(dec['effective_on'], '2026-09-30') + 1, 7, 0, literal='落在 2026-09 最后一周')
add(K, '决议生效后首个整月=2026-10', 'calendar effective_on → 下一整月', '2026-10', '2026-10',
    literal='次月为决议生效后首个整月')
add(K, 'JP_POLICY_TARGET 不在注册表', 'metric_registry.json metrics', 'JP_POLICY_TARGET' in regmap, False,
    literal='宣布目标序列 JP_POLICY_TARGET 在引擎注册表不可得')
add(K, 'JP_POLICY_TARGET 不在 series_store', 'snapshot.series_store', 'JP_POLICY_TARGET' in ss, False,
    literal='不以相邻口径冒充')
add(K, 'JP_POLICY_RATE 口径=月均(非目标宣布值)', 'metric_registry JP_POLICY_RATE.value_type',
    regmap.get('JP_POLICY_RATE', {}).get('value_type'), 'monthly_avg_rate',
    literal='该序列为无担保隔夜拆借利率月均口径,非政策目标宣布值')
add(K, 'JP_POLICY_TARGET 缺口=registry_absent', 'research_plan.dimension_gaps',
    (rep['research_plan'].get('dimension_gaps') or [{}])[0].get('gap'), 'registry_absent')

# ══ ② 点值锚格(9 指标 × 2 锚) ═════════════════════════════════════════════════
K = '②锚格'
ANCH = {'3个月前': '2026-08-23', '最新一期': '2026-11-23'}
pa = rep['research_plan'].get('point_anchors') or []
add(K, '锚「3个月前」as_of', 'research_plan.point_anchors',
    [a.get('as_of') for a in pa if a.get('label') == '3个月前'][0], '2026-08-23')
add(K, '锚「最新一期」as_of', 'research_plan.point_anchors',
    [a.get('as_of') for a in pa if a.get('label') == '最新一期'][0], '2026-11-23')
add(K, '锚点数=2(无 12 个月前锚)', 'research_plan.point_anchors', len(pa), 2, 0)
cells = {c['metric_id']: c for c in rep['research_plan']['point_values']['cells']}
add(K, '点值格数', 'research_plan.point_values.cells', len(cells), 9, 0, literal='点值格(9格)')
echo = {}
for r in aj['reader_map']['regions']:
    for e in r['anchor_echo']:
        echo[(e['metric_id'], e['anchor'])] = e
VALIT = {
    ('CPI', '最新一期'): '最新报 337.476(观测 2026-10', ('CORE_CPI', '最新一期'): 'CORE_CPI 报 339.9(观测 2026-10)',
    ('CORE_PCE', '最新一期'): 'CORE_PCE 报 130.902(观测 2026-09)',
    ('CPI', '3个月前'): '3 个月前锚前值 332.813,观测 2026-07',
    ('CORE_CPI', '3个月前'): '指数水平 336.789→339.9',
    ('CORE_PCE', '3个月前'): '指数水平 129.969→130.902',
    ('US_REAL_GDP', '最新一期'): '最新报 24611.077(观测 2026-07 季)',
    ('US_REAL_GDP', '3个月前'): 'GDP 水平 24408.011→24611.077',
    ('UNEMPLOYMENT', '最新一期'): 'UNEMPLOYMENT 最新报 4.1(观测 2026-10)',
    ('UNEMPLOYMENT', '3个月前'): '其 3 个月前锚前值为 4.1(观测 2026-07)',
    ('INDPRO', '最新一期'): 'INDPRO 报 103.3954(观测 2026-10)',
    ('INDPRO', '3个月前'): '3 个月前锚前值为 103.1675(观测 2026-07)',
    ('EA_REAL_GDP_YOY', '最新一期'): '2026Q3 为 1.28%', ('EA_REAL_GDP_YOY', '3个月前'): '2026Q2 为 1.19%',
    ('EA_HICP_YOY', '最新一期'): 'HICP 同比 2.9%(2026-07)→4.0%(2026-10)',
    ('EA_HICP_YOY', '3个月前'): 'HICP 同比 2.9%(2026-07)→4.0%(2026-10)',
    ('JP_POLICY_RATE', '最新一期'): '最新一期(2026-10)为 1.227%',
    ('JP_POLICY_RATE', '3个月前'): '3 个月前锚(2026-07)为 0.978%',
}
ND = {'INDPRO': 4, 'CPI': 3, 'CORE_CPI': 3, 'CORE_PCE': 3, 'US_REAL_GDP': 3, 'UNEMPLOYMENT': 1,
      'EA_HICP_YOY': 1, 'EA_REAL_GDP_YOY': 2, 'JP_POLICY_RATE': 3}
YOYABLE = ('US_REAL_GDP', 'INDPRO', 'CPI', 'CORE_CPI', 'CORE_PCE')
for m in ['US_REAL_GDP', 'UNEMPLOYMENT', 'INDPRO', 'CPI', 'CORE_CPI', 'CORE_PCE',
          'EA_REAL_GDP_YOY', 'EA_HICP_YOY', 'JP_POLICY_RATE']:
    for lab, as_of in ANCH.items():
        od, ov = anchor(m, as_of)
        c = cells[m]['anchors'][lab]
        e = echo.get((m, lab), {})
        add(K, '%s·%s·观测日' % (m, lab), 'series_store.%s + 发布纪律(锚 %s)' % (m, as_of),
            od, c.get('observation_date'), cell=e.get('observation_month', '') and e.get('observation_month') + '-01',
            note='判断档 anchor_echo.observation_month=%s' % e.get('observation_month'))
        add(K, '%s·%s·值' % (m, lab), 'series_store.%s[%s]' % (m, od), ov, c.get('value'), ND[m],
            cell=e.get('value'), literal=VALIT.get((m, lab)))
        add(K, '%s·%s·发布日(规则 %s)' % (m, lab, RULES[m][1]),
            'period_end+rule, 日历条目优先', pub(m, od), c.get('publication_date'))
        add(K, '%s·%s·发布日≤锚日' % (m, lab), 'pub vs as_of', pub(m, od) <= as_of, True)
        y = yoy(m, od) if m in YOYABLE else None
        if m in YOYABLE:
            add(K, '%s·%s·同比' % (m, lab), 'series_store.%s 同比(基期 %s)' % (m, base_of(od)), y,
                c.get('derived_yoy_pct'), 2, note='同比数字在判断档正文中的字面比对见 ③同比')
            if y is None:
                add(K, '%s·%s·同比缺基期状态' % (m, lab), 'series_store.%s 基期 %s 在场?' % (m, base_of(od)),
                    'no_same_period_base', c.get('yoy_status'),
                    literal='同比派生口径 2026-10 因缺上年同月基期观测不可得' if m == 'CPI' else None)

# ══ ③ 同比(判断档文字里的每个同比数) ═════════════════════════════════════════
K = '③同比'
add(K, 'CPI 同比@2026-07', 'series_store.CPI 同比', yoy('CPI', '2026-07-01'), 3.3, 2, literal='CPI 同比 3.3%(2026-07)')
add(K, 'CPI 同比@2026-09(最近有效)', 'series_store.CPI 同比', yoy('CPI', '2026-09-01'), 3.72, 2,
    literal='最近有效 3.72%(2026-09')
lv_d, lv_v = latest_valid_yoy('CPI', CUTOFF)
add(K, 'CPI 最近有效同比月份', 'series_store.CPI + 发布纪律', lv_d, '2026-09-01', literal='最近有效 3.72%(2026-09')
add(K, 'CPI 同比@2026-02', 'series_store.CPI 同比', yoy('CPI', '2026-02-01'), 2.434, 3, literal='由 2.434 升至 4.1666')
add(K, 'CPI 同比@2026-05(4位)', 'series_store.CPI 同比', yoy('CPI', '2026-05-01'), 4.1666, 4, literal='由 2.434 升至 4.1666')
add(K, 'CPI 同比@2026-05(2位)', 'series_store.CPI 同比', yoy('CPI', '2026-05-01'), 4.17, 2, literal='2026-05 高点 4.17')
add(K, 'CPI 三个月上行幅度(2026-02→2026-05)', 'series_store.CPI 同比差', yoy('CPI', '2026-05-01') - yoy('CPI', '2026-02-01'),
    1.7326, 4, literal='三个月上行 1.7326 个百分点')
cp26 = {d: yoy('CPI', d) for d in sorted(S('CPI')) if d.startswith('2026') and yoy('CPI', d) is not None}
add(K, 'CPI 同比 2026 年内高点月份', 'series_store.CPI 同比(argmax 2026)', max(cp26, key=cp26.get), '2026-05-01',
    literal='2026-05 高点')
add(K, 'CPI 同比@2026-10 不可得(2025-10 基期缺席)', 'series_store.CPI[2025-10-01]',
    '2025-10-01' in S('CPI'), False, literal='2026-10 同比因缺上年同月基期观测不可得')
add(K, 'CPI「回升」: 2026-09 > 2026-08', 'series_store.CPI 同比', yoy('CPI', '2026-09-01') > yoy('CPI', '2026-08-01'), True,
    literal='美国 CPI 同比 2026-09 回升至 3.72')
add(K, 'CORE_CPI 同比@2026-07', 'series_store.CORE_CPI 同比', yoy('CORE_CPI', '2026-07-01'), 2.47, 2,
    literal='核心 CPI 同比 2.47%(2026-07)')
add(K, 'CORE_CPI 同比@2026-09(最近有效)', 'series_store.CORE_CPI 同比', yoy('CORE_CPI', '2026-09-01'), 2.57, 2,
    literal='→2.57%(2026-09')
lv_d, _ = latest_valid_yoy('CORE_CPI', CUTOFF)
add(K, 'CORE_CPI 最近有效同比月份', 'series_store.CORE_CPI + 发布纪律', lv_d, '2026-09-01', literal='2.57%(2026-09')
add(K, 'CORE_CPI 同比@2026-02', 'series_store.CORE_CPI 同比', yoy('CORE_CPI', '2026-02-01'), 2.4725, 4,
    literal='同比自 2.4725 升至 2.8229')
add(K, 'CORE_CPI 同比@2026-05', 'series_store.CORE_CPI 同比', yoy('CORE_CPI', '2026-05-01'), 2.8229, 4,
    literal='同比自 2.4725 升至 2.8229')
add(K, 'CORE_CPI 同比@2026-08', 'series_store.CORE_CPI 同比', yoy('CORE_CPI', '2026-08-01'), 2.4462, 4,
    literal='同比自 2.8229 回落至 2.4462')
add(K, 'CORE_CPI 同比@2026-09(4位)', 'series_store.CORE_CPI 同比', yoy('CORE_CPI', '2026-09-01'), 2.5658, 4,
    literal='其后 2026-09 回升至 2.5658')
add(K, 'CORE_CPI 同比@2026-10 基期缺席', 'series_store.CORE_CPI[2025-10-01]',
    '2025-10-01' in S('CORE_CPI'), False)
add(K, 'CORE_PCE 同比@2026-06', 'series_store.CORE_PCE 同比', yoy('CORE_PCE', '2026-06-01'), 3.04, 2,
    literal='核心 PCE 同比 3.04%(2026-06)')
add(K, 'CORE_PCE 同比@2026-09', 'series_store.CORE_PCE 同比', yoy('CORE_PCE', '2026-09-01'), 3.12, 2,
    literal='→3.12%(2026-09')
add(K, 'INDPRO 同比@2026-07', 'series_store.INDPRO 同比', yoy('INDPRO', '2026-07-01'), 1.25, 2,
    literal='工业生产同比 1.25%(2026-07)')
add(K, 'INDPRO 同比@2026-10', 'series_store.INDPRO 同比', yoy('INDPRO', '2026-10-01'), 2.15, 2,
    literal='→2.15%(2026-10)')
add(K, 'US_REAL_GDP 同比@2026-04(Q2)', 'series_store.US_REAL_GDP 同比(去年同季)', yoy('US_REAL_GDP', '2026-04-01'),
    2.19, 2, literal='实际 GDP 同比 2026Q2 为 2.19%')
add(K, 'US_REAL_GDP 同比@2026-07(Q3)', 'series_store.US_REAL_GDP 同比(去年同季)', yoy('US_REAL_GDP', '2026-07-01'),
    2.07, 2, literal='2026Q3 为 2.07%')
add(K, 'US_REAL_GDP 同比文字(2.19→2.07)', 'series_store.US_REAL_GDP 同比',
    '%s→%s' % (('%.2f' % yoy('US_REAL_GDP', '2026-04-01')), ('%.2f' % yoy('US_REAL_GDP', '2026-07-01'))),
    '2.19→2.07', literal='(2.19→2.07,引擎派生口径)')
add(K, 'INDPRO 同比文字(1.25→2.15)', 'series_store.INDPRO 同比',
    '%s→%s' % (('%.2f' % yoy('INDPRO', '2026-07-01')), ('%.2f' % yoy('INDPRO', '2026-10-01'))),
    '1.25→2.15', literal='(1.25→2.15,引擎派生口径)')
# 季度同比的基期确为去年同季(而非相邻季)
add(K, 'US_REAL_GDP Q2 同比基期=去年同季(2025Q2)且在场', 'series_store.US_REAL_GDP[2025-04-01]',
    '2025-04-01' in S('US_REAL_GDP'), True, note='基期值 %.3f' % S('US_REAL_GDP')['2025-04-01'])
add(K, 'US_REAL_GDP Q3 同比基期=去年同季(2025Q3)且在场', 'series_store.US_REAL_GDP[2025-07-01]',
    '2025-07-01' in S('US_REAL_GDP'), True, note='基期值 %.3f' % S('US_REAL_GDP')['2025-07-01'])

# ══ ⑥ 转折候选面 ═══════════════════════════════════════════════════════════════
K = '⑥转折候选'
tc = rep['research_plan'].get('turning_candidates') or {}
cands = tc.get('candidates') or []
add(K, '候选池规模', 'research_plan.turning_candidates.candidates', len(cands), 7, 0, literal='候选池7、top3')
add(K, 'top_n_expected', 'research_plan.turning_candidates.top_n_expected', tc.get('top_n_expected'), 3, 0,
    literal='候选池7、top3')
CANDLIT = {
    'CPI': ('由 2.434 升至 4.1666', '由 2.434 升至 4.1666'),
    'EA_HICP_YOY': ('由 1.9 升至 3.2', '由 1.9 升至 3.2'),
    'JP_POLICY_RATE': ('2026-04 0.727→2026-07 0.978', '2026-04 0.727→2026-07 0.978'),
    'CORE_CPI': ('同比自 2.8229 回落至 2.4462', '同比自 2.8229 回落至 2.4462'),
    'INDPRO': (None, None), 'CORE_PCE': (None, None), 'UNEMPLOYMENT': (None, None),
}
for c in cands:
    m = c['metric_id']
    if m in ('EA_HICP_YOY', 'JP_POLICY_RATE', 'UNEMPLOYMENT'):      # 水平/比率型序列
        vb, va = v_at(m, c['from_date']), v_at(m, c['to_date'])
    else:                                                           # 水平序列的派生同比
        vb, va = yoy(m, c['from_date']), yoy(m, c['to_date'])
    lit = CANDLIT.get(m, (None, None))
    add(K, '%s 候选前值@%s' % (m, c['from_ym']), 'series_store.%s' % m, vb, c.get('value_before'), 4,
        literal=lit[0], note='候选面(引擎确定性); 判断档引用该段' if lit[0] else '候选面(引擎确定性), 判断档未引用该段数字')
    add(K, '%s 候选后值@%s' % (m, c['to_ym']), 'series_store.%s' % m, va, c.get('value_after'), 4, literal=lit[1],
        note='候选面(引擎确定性)' if not lit[1] else '判断档引用该段')
    add(K, '%s 候选变动幅' % m, 'series_store.%s 后值−前值' % m, (va - vb), c.get('delta'), 4)
mx = max(cands, key=lambda c: abs(c.get('delta') or 0))
add(K, '候选池内最大单段变动=CPI', 'turning_candidates.candidates argmax|delta|', mx['metric_id'], 'CPI',
    literal='为候选池内最大单段变动')
add(K, '候选池内最大单段变动幅', 'turning_candidates.candidates max|delta|', abs(mx['delta']), 1.7326, 4)
add(K, 'CPI 与 EA_HICP 候选同窗(2026-02→2026-05)', 'turning_candidates',
    (cands[0]['from_ym'], cands[0]['to_ym']) == (cands[1]['from_ym'], cands[1]['to_ym']), True,
    literal='美欧通胀同月抬升、月频证据先后未定')
add(K, 'JP 候选窗=2026-04→2026-07', 'turning_candidates',
    '%s→%s' % ([c for c in cands if c['metric_id'] == 'JP_POLICY_RATE'][0]['from_ym'],
               [c for c in cands if c['metric_id'] == 'JP_POLICY_RATE'][0]['to_ym']),
    '2026-04→2026-07', literal='2026-04 0.727→2026-07 0.978')
add(K, 'CORE_CPI 候选窗=2026-05→2026-08', 'turning_candidates',
    '%s→%s' % ([c for c in cands if c['metric_id'] == 'CORE_CPI'][0]['from_ym'],
               [c for c in cands if c['metric_id'] == 'CORE_CPI'][0]['to_ym']),
    '2026-05→2026-08', literal='2026-05→2026-08 同比自 2.8229 回落至 2.4462')
ea = S('EA_HICP_YOY')
add(K, 'EA_HICP_YOY@2026-02', 'series_store.EA_HICP_YOY', ea.get('2026-02-01'), 1.9, 1, literal='自 2026-02 的 1.9 抬升至 2026-05 的 3.2')
add(K, 'EA_HICP_YOY@2026-05', 'series_store.EA_HICP_YOY', ea.get('2026-05-01'), 3.2, 1, literal='自 2026-02 的 1.9 抬升至 2026-05 的 3.2')
add(K, 'EA_HICP_YOY@2026-06', 'series_store.EA_HICP_YOY', ea.get('2026-06-01'), 2.8, 1, literal='2026-06 回落至 2.8')
add(K, 'EA_HICP_YOY 三个月上行(2.9→4.0)', 'series_store.EA_HICP_YOY', ea.get('2026-10-01') - ea.get('2026-07-01'),
    1.1, 1, literal='三个月上行 1.1 个百分点')
add(K, 'EA_HICP_YOY 2026-02→2026-05 上行', 'series_store.EA_HICP_YOY', ea.get('2026-05-01') - ea.get('2026-02-01'),
    1.3, 1, literal='三个月上行 1.3 个百分点')
ea26 = {d: v for d, v in ea.items() if d.startswith('2026') and v is not None}
add(K, 'EA_HICP_YOY 2026 年内新高月份=2026-10', 'series_store.EA_HICP_YOY argmax(2026)',
    max(ea26, key=ea26.get), '2026-10-01', literal='读数为年内新高')
add(K, 'EA_HICP_YOY 2026-10 越过 2026-05 的 3.2', 'series_store.EA_HICP_YOY', ea.get('2026-10-01') > ea.get('2026-05-01'), True,
    literal='越过 2026-05 的 3.2')
add(K, '「为美欧两地最高水平」同月成立: EA(2026-09) > US CPI 同比(2026-09)', 'series_store EA_HICP_YOY vs CPI 同比',
    ea.get('2026-09-01') > yoy('CPI', '2026-09-01'), True, literal='为美欧两地最高水平',
    note='EA 最新为 2026-10, 其同月美国同比不可得(缺 2025-10 基期), 同月对照只能做到 2026-09; 逐月同月对照见探针')
add(K, '「读数水平低于欧元区」对最新有效同月成立: US CPI 同比(2026-09) < EA(2026-09)', 'series_store CPI 同比 vs EA_HICP_YOY',
    yoy('CPI', '2026-09-01') < ea.get('2026-09-01'), True, literal='但读数水平低于欧元区')
eg = S('EA_REAL_GDP_YOY')
add(K, 'EA_REAL_GDP_YOY@2026-04', 'series_store.EA_REAL_GDP_YOY', eg.get('2026-04-01'), 1.19, 2, literal='2026Q2 为 1.19%')
add(K, 'EA_REAL_GDP_YOY@2026-07', 'series_store.EA_REAL_GDP_YOY', eg.get('2026-07-01'), 1.28, 2, literal='2026Q3 为 1.28%')
add(K, 'EA_REAL_GDP_YOY 序列末观测=2026-07-01', 'series_store.EA_REAL_GDP_YOY.dates[-1]',
    ss['EA_REAL_GDP_YOY']['dates'][-1], '2026-07-01', literal='最新观测 2026-07-01')

# ══ ⑦ 机制链 M1(政策利率路径) ═════════════════════════════════════════════════
K = '⑦机制链'
J = S('JP_POLICY_RATE')
for d, rv, lit in [('2025-11-01', 0.478, '自 2025-11 的 0.478'), ('2025-12-01', 0.557, '经 2025-12 的 0.557 抬升至 2026-10 的 1.227'),
                   ('2026-01-01', 0.728, '2026-01 0.728'), ('2026-04-01', 0.727, '2026-04 0.727→2026-07 0.978'),
                   ('2026-06-01', 0.841, '2026-06 0.841'), ('2026-07-01', 0.978, '3 个月前锚前值为 0.978(观测 2026-07)'),
                   ('2026-08-01', 0.977, '2026-09 月均 0.977→1.043 仅 +7bp'),
                   ('2026-09-01', 1.043, '2026-09 月均 0.977→1.043 仅 +7bp'),
                   ('2026-10-01', 1.227, 'JP_POLICY_RATE 月均最新一期(观测 2026-10)报 1.227%')]:
    add(K, 'JP_POLICY_RATE 月均@%s' % d[:7], 'series_store.JP_POLICY_RATE[%s]' % d, J.get(d), rv, 3, literal=lit)
inwin = [d for d in sorted(J) if J[d] is not None and '2025-11-23' <= d <= CUTOFF]
add(K, '政策一年窗内首观测=2025-12-01', 'series_store.JP_POLICY_RATE 窗[2025-11-23..2026-11-23]',
    inwin[0], '2025-12-01', literal='自 2025-12 月均起算')
add(K, '政策窗净变动·引擎口径(窗首尾观测差)', '(J[2026-10]−J[2025-12])×100', (J['2026-10-01'] - J['2025-12-01']) * 100,
    67, 0, literal='净变动 +67bp')
add(K, '政策窗净变动·窗启时在值口径', '(J[2026-10]−J[2025-11])×100', (J['2026-10-01'] - J['2025-11-01']) * 100,
    75, 0, literal='为 +75bp')
add(K, '政策窗净变动·中文数字写法(六十)', '(J[2026-10]−J[2025-12])×100', (J['2026-10-01'] - J['2025-12-01']) * 100,
    67, 0, literal='为正六十七个基点')
add(K, '政策窗净变动·中文数字写法(七十五)', '(J[2026-10]−J[2025-11])×100', (J['2026-10-01'] - J['2025-11-01']) * 100,
    75, 0, literal='为正七十五个基点')
add(K, '窗启时在值(中文数字写法零点四七八)', 'series_store.JP_POLICY_RATE[2025-11-01]', J.get('2025-11-01'), 0.478, 3,
    literal='2025-11 月均零点四七八')
add(K, 'USDJPY@2026-11-23', 'series_store.USDJPY[2026-11-23]', v_at('USDJPY', '2026-11-23'), 159.35, 2,
    literal='USDJPY 水平为 159.35(观测 2026-11-23')
add(K, 'USDJPY@2026-11-23(机制链)', 'series_store.USDJPY[2026-11-23]', v_at('USDJPY', '2026-11-23'), 159.35, 2,
    literal='USDJPY 最新报 159.35(观测 2026-11-23')
add(K, 'NIKKEI225 近一月涨跌幅(10-23→11-20)', 'series_store.NIKKEI225', pct_chg('NIKKEI225', '2026-10-23', '2026-11-20'),
    -9.98, 2, literal='NIKKEI225 近一月(2026-10-23→2026-11-20)下跌 9.98%')
add(K, 'NIKKEI225 序列末观测=2026-11-20', 'series_store.NIKKEI225.dates[-1]', ss['NIKKEI225']['dates'][-1],
    '2026-11-20', literal='NIKKEI225 止于 2026-11-20 收盘')

# ══ ⑤ 三利率分解 ═══════════════════════════════════════════════════════════════
K = '⑤三利率'
W1 = ('2026-10-20', '2026-11-19')
W3 = ('2026-08-19', '2026-11-19')
W12 = ('2025-11-19', '2026-11-19')
trio = rep['research_plan'].get('us_rates_trio') or {}
for m, rv, lit in [('UST_10Y', 5.04, '美国十年期名义利率 2026-11-19 报 5.04%'),
                   ('TIPS_10Y', 2.88, 'TIPS_10Y 2.66→2.88'),
                   ('BEI_10Y', 2.16, '自 2.30 回落至 2.16(-14bp)')]:
    add(K, '%s 期末水平@2026-11-19' % m, 'series_store.%s[2026-11-19]' % m, v_at(m, '2026-11-19'), rv, 2,
        literal=lit, cell=(trio.get('levels_at_to') or {}).get(m))
add(K, 'BEI_10Y@2026-11-20', 'series_store.BEI_10Y[2026-11-20]', v_at('BEI_10Y', '2026-11-20'), 2.15, 2,
    literal='BEI_10Y 水平为 2.15(观测 2026-11-20)')
add(K, '期末水平恒等 名义=实际+盈亏平衡@2026-11-19', 'series_store 三序列[2026-11-19]',
    v_at('TIPS_10Y', '2026-11-19') + v_at('BEI_10Y', '2026-11-19') - v_at('UST_10Y', '2026-11-19'), 0.0, 2)
for lab, W, rN, rR, rB, litN, litR, litB in [
    ('近一月', W1, -8, 11, -19, '变动 -8bp', '(TIPS_10Y)+11bp', '(BEI_10Y)-19bp'),
    ('三个月', W3, 39, 53, -14, '名义 +39bp', '实际 +53bp', '盈亏平衡 -14bp'),
    ('12个月', W12, 91, 102, -11, '名义 +91bp', '实际 +102bp', '盈亏平衡 -11bp')]:
    cN, cR, cB = (bp_chg('UST_10Y', *W), bp_chg('TIPS_10Y', *W), bp_chg('BEI_10Y', *W))
    add(K, '%s窗 名义 Δbp(%s→%s)' % (lab, W[0], W[1]), 'series_store.UST_10Y', cN, rN, 0, literal=litN,
        cell=(trio.get('chg_bp') if lab == '近一月' else trio.get('chg_bp_12m') or {}).get('UST_10Y')
        if lab in ('近一月', '12个月') else None)
    add(K, '%s窗 实际 Δbp' % lab, 'series_store.TIPS_10Y', cR, rR, 0, literal=litR,
        cell=(trio.get('chg_bp') if lab == '近一月' else trio.get('chg_bp_12m') or {}).get('TIPS_10Y')
        if lab in ('近一月', '12个月') else None)
    add(K, '%s窗 盈亏平衡 Δbp' % lab, 'series_store.BEI_10Y', cB, rB, 0, literal=litB,
        cell=(trio.get('chg_bp') if lab == '近一月' else trio.get('chg_bp_12m') or {}).get('BEI_10Y')
        if lab in ('近一月', '12个月') else None)
    add(K, '%s窗 恒等残差 名义−(实际+盈亏平衡)' % lab, 'series_store 三序列', cN - (cR + cB), 0.0, 1,
        literal='(残差 0)' if lab in ('三个月', '12个月') else None)
    lvl = {'UST_10Y': v_at('UST_10Y', W[1]), 'TIPS_10Y': v_at('TIPS_10Y', W[1]), 'BEI_10Y': v_at('BEI_10Y', W[1])}
    add(K, '%s窗 端点恒等(两日各自 名义=实际+BEI)' % lab, 'series_store 三序列@%s' % W[0],
        (v_at('UST_10Y', W[0]) - v_at('TIPS_10Y', W[0]) - v_at('BEI_10Y', W[0])),
        0.0, 2, note='窗起日 %s 三序列同日在场且恒等成立' % W[0])
add(K, 'BEI_10Y 窗起值@2026-10-20', 'series_store.BEI_10Y[2026-10-20]',
    v_at('BEI_10Y', '2026-10-20'), 2.16 - (-19) / 100.0, 2,
    note='期末水平 2.16 − 判断档变动 −19bp 的反推端点值')
add(K, 'TIPS_10Y 窗起值@2026-10-20', 'series_store.TIPS_10Y[2026-10-20]',
    v_at('TIPS_10Y', '2026-10-20'), 2.88 - 11 / 100.0, 2)
add(K, 'UST_10Y 窗起值@2026-10-20', 'series_store.UST_10Y[2026-10-20]',
    v_at('UST_10Y', '2026-10-20'), 5.04 - (-8) / 100.0, 2)
add(K, 'BEI_10Y 三个月窗起值 2.30@2026-08-19', 'series_store.BEI_10Y[2026-08-19]', v_at('BEI_10Y', '2026-08-19'),
    2.30, 2, literal='自 2.30 回落至 2.16(-14bp)')
add(K, 'TIPS_10Y@2026-10-23', 'series_store.TIPS_10Y[2026-10-23]', v_at('TIPS_10Y', '2026-10-23'), 2.66, 2,
    literal='同窗 TIPS_10Y 2.66→2.88(+22bp')
add(K, 'TIPS_10Y 10-23→11-19 Δbp', 'series_store.TIPS_10Y', bp_chg('TIPS_10Y', '2026-10-23', '2026-11-19'), 22, 0,
    literal='2.66→2.88(+22bp')
add(K, 'BEI_10Y@2026-02-27', 'series_store.BEI_10Y[2026-02-27]', v_at('BEI_10Y', '2026-02-27'), 2.25, 2,
    literal='BEI_10Y 自 2026-02-27 的 2.25 升至 2026-05-04 的 2.50')
add(K, 'BEI_10Y@2026-05-04', 'series_store.BEI_10Y[2026-05-04]', v_at('BEI_10Y', '2026-05-04'), 2.50, 2,
    literal='BEI_10Y 自 2026-02-27 的 2.25 升至 2026-05-04 的 2.50')

# ══ ⑤ 资产月窗 ═════════════════════════════════════════════════════════════════
K = '⑤资产月窗'
am = {r['metric_id']: r for r in (rep['research_plan'].get('asset_moves') or {}).get('rows', [])}
ec = {e['metric_id']: e for e in aj['reader_map'].get('asset_returns_echo', [])}
for m, d0, d1, rv, lit in [
        ('SPX', '2026-10-23', '2026-11-23', -5.51, 'SPX 下跌 5.51%'),
        ('NIKKEI225', '2026-10-23', '2026-11-20', -9.98, 'NIKKEI225 下跌 9.98%'),
        ('GOLD_F', '2026-10-23', '2026-11-23', -8.05, 'GOLD_F 下跌 8.05%'),
        ('DXY', '2026-10-23', '2026-11-23', 2.23, 'DXY 上涨 2.23%'),
        ('VIX', '2026-10-23', '2026-11-23', 38.87, 'VIX 上涨 38.87%')]:
    add(K, '%s 近一月涨跌幅(%s→%s)' % (m, d0, d1), 'series_store.%s' % m, pct_chg(m, d0, d1), rv, 2,
        literal=lit, cell=(am.get(m) or {}).get('chg_pct'))
    add(K, '%s 窗末日=%s' % (m, d1), 'series_store.%s.dates[-1] / 引擎窗' % m,
        (am.get(m) or {}).get('window', {}).get('to'), d1, cell=(ec.get(m) or {}).get('window', {}).get('to'))
    add(K, '%s 窗起日=2026-10-23' % m, 'series_store.%s[2026-10-23] 在场' % m, '2026-10-23' in S(m), True)
add(K, 'VIX 窗起值 19.45', 'series_store.VIX[2026-10-23]', v_at('VIX', '2026-10-23'), 19.45, 2, literal='(19.45→27.01')
add(K, 'VIX 窗末值 27.01', 'series_store.VIX[2026-11-23]', v_at('VIX', '2026-11-23'), 27.01, 2, literal='(19.45→27.01')
add(K, '同日收盘口径 SPX 10-23→11-20', 'series_store.SPX', pct_chg('SPX', '2026-10-23', '2026-11-20'), -9.36, 2,
    literal='标普500指数 -9.36%')
add(K, '同日收盘口径 VIX 10-23→11-20', 'series_store.VIX', pct_chg('VIX', '2026-10-23', '2026-11-20'), 84.52, 2,
    literal='VIX +84.52%')
add(K, '三个月收盘口径 SPX 08-19→11-20', 'series_store.SPX', pct_chg('SPX', '2026-08-19', '2026-11-20'), -10.35, 2,
    literal='标普500指数 -10.35%')
add(K, '三个月收盘口径 VIX 08-19→11-20', 'series_store.VIX', pct_chg('VIX', '2026-08-19', '2026-11-20'), 141.03, 2,
    literal='VIX +141.03%(14.89→35.89)')
add(K, 'VIX 三个月窗起值 14.89', 'series_store.VIX[2026-08-19]', v_at('VIX', '2026-08-19'), 14.89, 2,
    literal='VIX +141.03%(14.89→35.89)')
add(K, 'VIX 三个月窗末值 35.89', 'series_store.VIX[2026-11-20]', v_at('VIX', '2026-11-20'), 35.89, 2,
    literal='VIX +141.03%(14.89→35.89)')
add(K, 'SPX 11-23 值为序列末观测(盘中)', 'series_store.SPX.dates[-1]', ss['SPX']['dates'][-1], '2026-11-23',
    literal='11-23 值为盘中快照(非收盘价)')
add(K, 'rates_decomposition.nominal_bp', 'reader_map.rates_decomposition vs 直算',
    bp_chg('UST_10Y', *W1), aj['reader_map']['rates_decomposition']['nominal_bp'], 1)
add(K, 'rates_decomposition.real_bp', 'reader_map.rates_decomposition vs 直算',
    bp_chg('TIPS_10Y', *W1), aj['reader_map']['rates_decomposition']['real_bp'], 1)
add(K, 'rates_decomposition.bei_bp', 'reader_map.rates_decomposition vs 直算',
    bp_chg('BEI_10Y', *W1), aj['reader_map']['rates_decomposition']['bei_bp'], 1)
add(K, 'rates_decomposition 窗端点', 'reader_map.rates_decomposition vs 引擎 us_rates_trio.window',
    '%s→%s' % (aj['reader_map']['rates_decomposition']['window_from'], aj['reader_map']['rates_decomposition']['window_to']),
    '%s→%s' % (trio.get('window', {}).get('from'), trio.get('window', {}).get('to')))

# ══ ⑪ 诚实缺席 / Gate A ═══════════════════════════════════════════════════════
K = '⑪缺席披露'
ga = snap.get('gate_a', {})
add(K, 'Gate A 状态', 'snapshot.gate_a.status', ga.get('status'), 'DEGRADED', literal='Gate A=DEGRADED')
add(K, '核心缺口项数', 'snapshot.gate_a.core_missing', len(ga.get('core_missing') or []), 0, 0, literal='核心缺口 零 项')
nm = ga.get('noncore_missing') or []
JNM = ['BUND_10Y', 'BUND_2Y', 'CN_OMO_7D', 'CN_POLICY_OVERNIGHT', 'EA_REAL_GDP_YOY', 'JP_CPI_TOKYO_YOY', 'JP_REAL_GDP_YOY']
add(K, '非核心缺口清单(逐项一致)', 'snapshot.gate_a.noncore_missing', sorted(nm) == sorted(JNM), True,
    literal='非核心缺口 七 项(BUND_10Y、BUND_2Y、CN_OMO_7D、CN_POLICY_OVERNIGHT、EA_REAL_GDP_YOY、JP_CPI_TOKYO_YOY、JP_REAL_GDP_YOY)')
ndg = ga.get('noncore_degraded') or []
JND = ['CN_SF_FLOW', 'ECB_DFR', 'ECB_MRO', 'JTSJOL', 'M2SL', 'SPX_EPS', 'SPX_PE_TTM', 'US_REAL_GDP']
add(K, '非核心降级清单(逐项一致)', 'snapshot.gate_a.noncore_degraded', sorted(ndg) == sorted(JND), True,
    literal='非核心降级 八 项(CN_SF_FLOW、ECB_DFR、ECB_MRO、JTSJOL、M2SL、SPX_EPS、SPX_PE_TTM、US_REAL_GDP)')
cited = set()
for r_ in aj['reader_map']['regions']:
    for e_ in r_['anchor_echo']:
        cited.add(e_['metric_id'])
for c_ in aj['l3']['contradictions']:
    cited |= set(x.split('@')[0] for x in c_.get('evidence_refs', []))
for mc_ in aj['l3'].get('mechanism_chains', []):
    for lk_ in mc_['links']:
        cited |= set(x.split('@')[0] for x in lk_.get('evidence_refs', []))
for sc_ in aj['l4']['scenarios']:
    cited |= set(x.split('@')[0] for x in sc_['rows']['asset_direction'].get('evidence_refs', []))
add(K, '判断档引用的非核心缺口指标集合', 'agent_judgment(点值回显+证据引用) ∩ gate_a.noncore_missing',
    sorted(cited & set(nm)), ['EA_REAL_GDP_YOY'],
    literal='本档引用的非核心缺口指标 一 项(EA_REAL_GDP_YOY)在序列库内有存量观测')
add(K, 'EA_REAL_GDP_YOY 在 series_store 有存量观测', 'snapshot.series_store.EA_REAL_GDP_YOY',
    any(v is not None for v in ss['EA_REAL_GDP_YOY']['values']), True, literal='在序列库内有存量观测')
add(K, '非核心缺口七项中不在 series_store 的序列', 'snapshot.series_store',
    [m for m in nm if m not in ss], ['BUND_10Y', 'BUND_2Y'],
    note='其余五项在库内有存量观测(判断档披露块④已概括披露该引擎缺口), 见探针')
add(K, '计划指标中 US_REAL_GDP 属非核心降级', 'snapshot.gate_a.noncore_degraded', 'US_REAL_GDP' in ndg, True)

# ══ ⑬ 契约验证非 VERIFIED 项 ══════════════════════════════════════════════════
K = '⑬契约STALE'
cvv = rep['agent_judgment'].get('contract_verification') or {}
verd = cvv.get('verdicts') or []
stale = [x for x in verd if x.get('status') == 'STALE']
add(K, 'STALE 项指标集合', 'report.json agent_judgment.contract_verification.verdicts[status=STALE].metric',
    sorted(set(x.get('metric') for x in stale)), ['CORE_PCE', 'US_REAL_GDP'],
    literal='引擎契约对两处引用标注 STALE')
add(K, '契约 STALE 项数值与期望一致', 'contract_verification.verdicts[STALE].value==expected',
    all(x.get('value') == x.get('expected') for x in stale), True, literal='数值一致')
add(K, '契约面非 VERIFIED 项恰 2 项(与判断档「对两处引用标注 STALE」的项数一致)', 'contract_verification.verdicts 中非 VERIFIED 项数',
    len([x for x in verd if x.get('status') != 'VERIFIED']), 2, 0, literal='引擎契约对两处引用标注 STALE')
add(K, 'CORE_PCE 观测日', 'series_store.CORE_PCE.dates[-1]', ss['CORE_PCE']['dates'][-1], '2026-09-01',
    literal='CORE_PCE(观测 2026-09-01，距截止日 83 天')
add(K, 'CORE_PCE 观测距截止日天数', '截止日 − 2026-09-01', days_between('2026-09-01', CUTOFF), 83, 0,
    literal='距截止日 83 天')
add(K, 'CORE_PCE 注册表最大日历滞后', 'metric_registry CORE_PCE.max_calendar_lag_days',
    regmap.get('CORE_PCE', {}).get('freshness', {}).get('max_calendar_lag_days'), 60, 0, literal='最大日历滞后 60 天的 1.4 倍')
add(K, 'CORE_PCE 滞后倍数', '83/60', days_between('2026-09-01', CUTOFF) / regmap['CORE_PCE']['freshness']['max_calendar_lag_days'],
    1.4, 1, literal='60 天的 1.4 倍')
add(K, 'US_REAL_GDP 观测日', 'series_store.US_REAL_GDP.dates[-1]', ss['US_REAL_GDP']['dates'][-1], '2026-07-01',
    literal='US_REAL_GDP(观测 2026-07-01，距截止日 145 天')
add(K, 'US_REAL_GDP 观测距截止日天数', '截止日 − 2026-07-01', days_between('2026-07-01', CUTOFF), 145, 0,
    literal='距截止日 145 天')
add(K, 'US_REAL_GDP 注册表最大日历滞后', 'metric_registry US_REAL_GDP.max_calendar_lag_days',
    regmap.get('US_REAL_GDP', {}).get('freshness', {}).get('max_calendar_lag_days'), 120, 0, literal='最大日历滞后 120 天的 1.2 倍')
add(K, 'US_REAL_GDP 滞后倍数', '145/120', days_between('2026-07-01', CUTOFF) / regmap['US_REAL_GDP']['freshness']['max_calendar_lag_days'],
    1.2, 1, literal='120 天的 1.2 倍')
add(K, 'CORE_PCE 最新观测=截止日前最新已发布(发布日 2026-10-30≤截止日)',
    'series_store.CORE_PCE + 发布纪律', pub('CORE_PCE', '2026-09-01'), '2026-10-30',
    literal='两者均为该序列在截止日前的最新已发布观测')
add(K, 'US_REAL_GDP 发布日', 'series_store.US_REAL_GDP + 发布纪律(季末+29)', pub('US_REAL_GDP', '2026-07-01'), '2026-10-29')
add(K, 'CORE_PCE 2026-10 观测不在序列(故最新为 2026-09)', 'series_store.CORE_PCE[2026-10-01]',
    '2026-10-01' in S('CORE_PCE'), False)

# ══ 证据引用解析 ════════════════════════════════════════════════════════════════
K = '证据引用'
refs = []
for c in aj['l3']['contradictions']:
    for r in c.get('evidence_refs', []):
        refs.append(('L3', c['id'], r))
for mc in aj['l3'].get('mechanism_chains', []):
    for lk in mc.get('links', []):
        for r in lk.get('evidence_refs', []):
            refs.append(('M', mc['id'], r))
for sc in aj['l4'].get('scenarios', []):
    for r in sc['rows'].get('asset_direction', {}).get('evidence_refs', []):
        refs.append(('S', sc['id'], r))
evset = set(e['ref'] for e in evi)
add(K, '证据索引行数', 'evidence_index.json', len(evi), 63, 0, literal='证据索引(63行)')
add(K, '证据引用总数', 'agent_judgment.json 全部 evidence_refs', len(refs), 19, 0, literal='证据引用共 19 条')
add(K, '矛盾陈述证据引用数', 'l3.contradictions[*].evidence_refs', len([r for r in refs if r[0] == 'L3']), 10, 0,
    literal='(矛盾陈述 10、机制链 4、情景 5)')
add(K, '机制链证据引用数', 'l3.mechanism_chains[*].links[*].evidence_refs', len([r for r in refs if r[0] == 'M']), 4, 0,
    literal='(矛盾陈述 10、机制链 4、情景 5)')
add(K, '情景证据引用数', 'l4.scenarios[*].asset_direction.evidence_refs', len([r for r in refs if r[0] == 'S']), 5, 0,
    literal='(矛盾陈述 10、机制链 4、情景 5)')
add(K, '全部引用均在证据索引', 'agent_judgment evidence_refs vs evidence_index.json',
    [r[2] for r in refs if r[2] not in evset], [], literal='全部解析到本轮冻结快照')
add(K, '全部引用观测日≤截止日', 'agent_judgment evidence_refs', [r[2] for r in refs if r[2].split('@')[1] > CUTOFF], [])
unres = []
for _, _, r in refs:
    m, d = r.split('@')
    if m not in ss or d not in S(m) or S(m).get(d) is None:
        unres.append(r)
add(K, '全部引用在 series_store 该日有值', 'agent_judgment evidence_refs vs snapshot.series_store', unres, [])
add(K, '机制链证据级标注', 'l3.mechanism_chains[0].links[*].evidence_level',
    '/'.join(lk.get('evidence_level') for lk in aj['l3']['mechanism_chains'][0]['links']), 'E1/E2/E2',
    literal='机制链三环证据分级 E1/E2/E2')
add(K, '各矛盾陈述并列解释数', 'l3.contradictions[*].competing_explanations',
    '/'.join(str(len(c.get('competing_explanations', []))) for c in aj['l3']['contradictions']), '2/2/2',
    literal='各并列 2、2、2 种解释')
add(K, '情景数', 'l4.scenarios', len(aj['l4'].get('scenarios', [])), 2, 0)
add(K, '情景期限', 'l4.scenarios[*].rows.trigger.deadline',
    '/'.join(sc['rows']['trigger']['deadline'] for sc in aj['l4']['scenarios']), '2027-02-15/2027-02-15',
    literal='期限均为 2027-02-15')
add(K, '历史段数=0', 'reader_map.history_periods', len(aj['reader_map'].get('history_periods', [])), 0, 0)
add(K, '转折数', 'reader_map.turnings', len(aj['reader_map'].get('turnings', [])), 3, 0)

# ══ ⑨ 情景与截止日读数相容(数值比较) ══════════════════════════════════════════
K = '⑨情景相容'
add(K, 'S1 触发: EA_HICP_YOY 4.0 未达阈值 4.2', 'series_store.EA_HICP_YOY[2026-10-01]', ea.get('2026-10-01') >= 4.2, False,
    literal='EA_HICP_YOY 同比 ≥4.2%')
add(K, 'S1 触发: CORE_PCE 同比 3.12 未达阈值 3.2', 'series_store.CORE_PCE 同比@2026-09', yoy('CORE_PCE', '2026-09-01') >= 3.2, False,
    literal='CORE_PCE 同比 ≥3.2%')
add(K, 'S1 触发: TIPS_10Y 2.88 未高于 3.0', 'series_store.TIPS_10Y[2026-11-19]', v_at('TIPS_10Y', '2026-11-19') > 3.0, False,
    literal='TIPS_10Y 高于 3.0%')
add(K, 'S1 证伪: EA 近两月未连续低于 3.0', 'series_store.EA_HICP_YOY[2026-09,2026-10]',
    (ea.get('2026-09-01') < 3.0 and ea.get('2026-10-01') < 3.0), False, literal='连续两个月低于 3.0%')
add(K, 'S2 触发: EA 未连续两月回落', 'series_store.EA_HICP_YOY[2026-08..2026-10]',
    (ea.get('2026-09-01') < ea.get('2026-08-01') and ea.get('2026-10-01') < ea.get('2026-09-01')), False,
    literal='EA_HICP_YOY 同比连续两个月回落')
add(K, 'S2 触发: BEI_10Y 2.15 未低于 2.0', 'series_store.BEI_10Y[2026-11-20]', v_at('BEI_10Y', '2026-11-20') < 2.0, False,
    literal='BEI_10Y 低于 2.0%')
add(K, 'S2 证伪阈值所用月份(2026-12/2027-01)在截止日后=可观测未决', 'series_store.EA_HICP_YOY.dates[-1]',
    ss['EA_HICP_YOY']['dates'][-1], '2026-10-01', literal='2026-12 与 2027-01 两月 EA_HICP_YOY 同比均不低于 4.0%')
add(K, 'S1 所需 CORE_PCE 后续同比基期(2025-10/2025-11)在场=可观测', 'series_store.CORE_PCE[2025-10-01,2025-11-01]',
    ('2025-10-01' in S('CORE_PCE')) and ('2025-11-01' in S('CORE_PCE')), True)
add(K, 'S2 所述方向与近一月观察相反(实际利率 +11bp)', 'series_store.TIPS_10Y 10-20→11-19',
    bp_chg('TIPS_10Y', '2026-10-20', '2026-11-19'), 11, 0, literal='实际利率 +11bp 而风险资产回落')

# ── 探针(六查/反方攻击用; 非逐点比对) ───────────────────────────────────────
PR = {}


def rng(m, end):
    """序列在 end 之前 12 个月窗内的取值范围与分位。"""
    s = S(m)
    dt = _dt.date.fromisoformat(end)
    lo = (dt - _dt.timedelta(days=365)).isoformat()
    items = [(dd, v) for dd, v in s.items() if lo <= dd <= end and v is not None]
    vals = sorted(v for _, v in items)
    return {'n': len(vals), 'min': vals[0], 'min_date': min(dd for dd, v in items if v == vals[0]),
            'max': vals[-1], 'max_date': min(dd for dd, v in items if v == vals[-1]),
            'median': vals[len(vals) // 2],
            'pct_rank_of_end_value': sum(1 for v in vals if v <= s[end]) / len(vals)}


PR['ranges_12m'] = {m: rng(m, ss[m]['dates'][-1]) for m in
                    ['BEI_10Y', 'TIPS_10Y', 'UST_10Y', 'USDJPY', 'EURUSD', 'DXY', 'VIX', 'UNEMPLOYMENT', 'JP_POLICY_RATE']}
b = S('BEI_10Y')
PR['BEI_10Y_2026_02_05'] = {d: b[d] for d in sorted(b) if '2026-01-28' <= d <= '2026-06-02'}
PR['BEI_10Y_month_aligned'] = {
    '2026-01-30→2026-04-30': bp_chg('BEI_10Y', '2026-01-30', '2026-04-30'),
    '2026-02-02→2026-05-29': bp_chg('BEI_10Y', '2026-02-02', '2026-05-29'),
    '2026-02-27→2026-05-29': bp_chg('BEI_10Y', '2026-02-27', '2026-05-29'),
    '2026-02-27→2026-05-04(判断档所引)': bp_chg('BEI_10Y', '2026-02-27', '2026-05-04'),
    '2026-02-27→2026-05-27(满三个月)': bp_chg('BEI_10Y', '2026-02-27', '2026-05-27'),
}
ip = S('INDPRO')
PR['INDPRO_path'] = {d[:7]: ip[d] for d in sorted(ip) if d >= '2025-06-01'}
PR['INDPRO_yoy'] = {d[:7]: round(yoy('INDPRO', d), 4) for d in sorted(ip) if d >= '2025-06-01' and yoy('INDPRO', d) is not None}
PR['INDPRO_level_chg_pct'] = {
    '2026-07→2026-10': pct_chg('INDPRO', '2026-07-01', '2026-10-01'),
    '2026-09→2026-10': pct_chg('INDPRO', '2026-09-01', '2026-10-01'),
    '基期 2025-07→2025-10': pct_chg('INDPRO', '2025-07-01', '2025-10-01'),
}
PR['CPI_yoy_2026'] = {d[:7]: round(yoy('CPI', d), 4) for d in sorted(S('CPI')) if d.startswith('2026') and yoy('CPI', d) is not None}
PR['CORE_CPI_yoy_2026'] = {d[:7]: round(yoy('CORE_CPI', d), 4) for d in sorted(S('CORE_CPI')) if d.startswith('2026') and yoy('CORE_CPI', d) is not None}
PR['CORE_PCE_yoy'] = {d[:7]: round(yoy('CORE_PCE', d), 4) for d in sorted(S('CORE_PCE')) if d >= '2025-11-01' and yoy('CORE_PCE', d) is not None}
PR['EA_HICP_path'] = {d[:7]: v for d, v in sorted(ea.items()) if d.startswith('2026')}
PR['us_ea_same_month'] = {
    ym: {'EA_HICP_YOY': ea.get(ym + '-01'), 'US_CPI_yoy': (round(yoy('CPI', ym + '-01'), 2) if yoy('CPI', ym + '-01') is not None else None),
         'US_CORE_CPI_yoy': (round(yoy('CORE_CPI', ym + '-01'), 2) if yoy('CORE_CPI', ym + '-01') is not None else None),
         'US_CORE_PCE_yoy': (round(yoy('CORE_PCE', ym + '-01'), 2) if yoy('CORE_PCE', ym + '-01') is not None else None)}
    for ym in ['2026-05', '2026-06', '2026-07', '2026-08', '2026-09', '2026-10']}
PR['noncore_missing_stock'] = {
    m: {'in_series_store': m in ss,
        'n_obs': (sum(1 for v in ss[m]['values'] if v is not None) if m in ss else 0),
        'last_obs': (ss[m]['dates'][-1] if m in ss else None)} for m in nm}
PR['pseudo_yoy_adjacent_base_CPI_2026-10'] = {
    '基期取 2025-09': (S('CPI')['2026-10-01'] / S('CPI')['2025-09-01'] - 1) * 100,
    '基期取 2025-11': (S('CPI')['2026-10-01'] / S('CPI')['2025-11-01'] - 1) * 100}
u = S('USDJPY')
PR['USDJPY_key'] = {d: u.get(d) for d in ['2026-09-17', '2026-09-18', '2026-09-23', '2026-09-24', '2026-09-25',
                                           '2026-10-30', '2026-10-23', '2026-11-20', '2026-11-23'] if d in u}
ud = sorted(u)
PR['USDJPY_nearest'] = {
    '决议前一日(≤09-17)': max(d for d in ud if d <= '2026-09-17'),
    '生效后首交易日(≥09-24)': min(d for d in ud if d >= '2026-09-24')}
PR['USDJPY_chg_pct'] = {
    '2026-09-18→2026-11-23': pct_chg('USDJPY', '2026-09-18', '2026-11-23') if '2026-09-18' in u else None,
    '2026-09-24→2026-11-23': pct_chg('USDJPY', '2026-09-24', '2026-11-23') if '2026-09-24' in u else None,
    '2026-10-23→2026-11-23': pct_chg('USDJPY', '2026-10-23', '2026-11-23'),
    '2026-08-19→2026-11-23': pct_chg('USDJPY', '2026-08-19', '2026-11-23')}
PR['EURUSD_chg_pct'] = {'2026-08-19→2026-11-23': pct_chg('EURUSD', '2026-08-19', '2026-11-23'),
                        '2026-10-23→2026-11-23': pct_chg('EURUSD', '2026-10-23', '2026-11-23')}
PR['SPX_same_close_as_TIPS_10-23→11-19'] = pct_chg('SPX', '2026-10-23', '2026-11-19')
PR['common_days'] = {
    'UST_10Y 末观测': ss['UST_10Y']['dates'][-1], 'TIPS_10Y 末观测': ss['TIPS_10Y']['dates'][-1],
    'BEI_10Y 末观测': ss['BEI_10Y']['dates'][-1],
    '三序列共同末交易日': max(set(ss['UST_10Y']['dates']) & set(ss['TIPS_10Y']['dates']) & set(ss['BEI_10Y']['dates']))}
PR['UNEMPLOYMENT_2026'] = {d[:7]: v for d, v in sorted(S('UNEMPLOYMENT').items()) if d.startswith('2026')}
PR['US_REAL_GDP_qq'] = {
    '2026Q3/Q2 水平环比%': pct_chg('US_REAL_GDP', '2026-04-01', '2026-07-01'),
    '2026Q3/Q2 年化%': ((S('US_REAL_GDP')['2026-07-01'] / S('US_REAL_GDP')['2026-04-01']) ** 4 - 1) * 100}
PR['JP_step_bp'] = {('%s→%s' % (a[:7], c[:7])): round((J[c] - J[a]) * 100, 1)
                    for a, c in zip(sorted(J), sorted(J)[1:]) if a >= '2025-10-01'}
up2026 = [c[:7] for a, c in zip(sorted(J), sorted(J)[1:]) if c.startswith('2026') and c <= '2026-07-01' and J[c] > J[a]]
PR['JP_up_steps_2026_until_07'] = up2026
PR['JP_POLICY_RATE_monthly'] = {d[:7]: v for d, v in sorted(J.items()) if d >= '2025-10-01'}
PR['CORE_CPI_dates_2025H2'] = [d for d in ss['CORE_CPI']['dates'] if '2025-07-01' <= d <= '2026-01-01']
PR['CPI_dates_2025H2'] = [d for d in ss['CPI']['dates'] if '2025-07-01' <= d <= '2026-01-01']
PR['EA_REAL_GDP_YOY_registry_lag'] = regmap.get('EA_REAL_GDP_YOY', {}).get('freshness', {})
PR['US_REAL_GDP_registry_lag'] = regmap.get('US_REAL_GDP', {}).get('freshness', {})
PR['TIPS_10Y_common_day_vs_SPX'] = {'TIPS 10-20→11-19': bp_chg('TIPS_10Y', '2026-10-20', '2026-11-19'),
                                    'SPX 10-20→11-19': pct_chg('SPX', '2026-10-20', '2026-11-19')}
PR['HY_OAS'] = {d: S('HY_OAS').get(d) for d in ['2026-10-23', ss['HY_OAS']['dates'][-1]]}
PR['daily_counts_3m_window'] = {}
for m in ['TIPS_10Y', 'BEI_10Y']:
    ds = [d for d in sorted(S(m)) if '2026-08-19' <= d <= '2026-11-19']
    ch = [(S(m)[d1] - S(m)[d0]) for d0, d1 in zip(ds, ds[1:])]
    PR['daily_counts_3m_window'][m] = {'n_days': len(ds), 'n_up': sum(1 for x in ch if x > 0), 'n_down': sum(1 for x in ch if x < 0)}
# 三个月内「TIPS 上行 且 BEI 下行」的共同交易日数(链2 主张「主导关系稳定」的逐日核对)
cd = sorted(set(d for d in S('TIPS_10Y') if '2026-08-19' < d <= '2026-11-19') & set(d for d in S('BEI_10Y') if '2026-08-19' < d <= '2026-11-19'))
both = 0
for d in cd:
    pd_ = max(x for x in S('TIPS_10Y') if x < d)
    pe = max(x for x in S('BEI_10Y') if x < d)
    if pd_ in S('BEI_10Y') and pe in S('TIPS_10Y'):
        both += 1
PR['common_daily_pairs_3m'] = {'n': len(cd), 'note': '共同交易日数(TIPS/BEI 序列逐日对齐口径的粗略计数)', 'pairs': both}
PR['stale_ratio_EA_REAL_GDP_YOY'] = {
    'obs': ss['EA_REAL_GDP_YOY']['dates'][-1], 'days': days_between(ss['EA_REAL_GDP_YOY']['dates'][-1], CUTOFF),
    'max_lag': regmap.get('EA_REAL_GDP_YOY', {}).get('freshness', {}).get('max_calendar_lag_days')}
PR['daily_last_obs_carry_label'] = {m: ss[m]['dates'][-1] for m in
                                    ['SPX', 'VIX', 'GOLD_F', 'DXY', 'USDJPY', 'EURUSD', 'DAX', 'CAC40', 'NIKKEI225',
                                     'UST_10Y', 'TIPS_10Y', 'BEI_10Y', 'HY_OAS', 'NDX', 'RUT', 'SHCOMP', 'HSI']}
PR['data_requirements'] = [
    {'metric_id': it.get('metric_id'), 'tier': it.get('tier'), 'outcome': it.get('outcome'),
     'window': (it.get('spec') or {}).get('window', {}).get('start') + '..' + (it.get('spec') or {}).get('window', {}).get('end')}
    for it in (rep['run'].get('data_requirements') or {}).get('items', [])]
PR['snapshot_series_count'] = len(ss)
PR['quality_counts'] = snap['quality']['counts']
PR['quality_overall'] = snap['quality'].get('overall')
PR['contract_stats'] = cvv.get('stats')
PR['contract_six_checks'] = cvv.get('six_checks')
PR['contract_map_checks'] = cvv.get('map_checks')
PR['contract_tokens_verified'] = [(x.get('item'), x.get('token'), x.get('status')) for x in verd]
PR['US_REAL_GDP_base_values'] = {'2025Q2': S('US_REAL_GDP').get('2025-04-01'), '2025Q3': S('US_REAL_GDP').get('2025-07-01')}
PR['gate_a_note'] = ga.get('note')

# ── 结构性自检标记: 引擎面/日历内部一致性或判断档自身结构计数, 直算值与比对值同源,
#    不属于「证据面直算 ↔ 报告/判断档文字」的独立复算, 不计入 recompute_points ──
STRUCT_DESCS = {
    '引擎 cutoff', '引擎 evidence_asof', '引擎 ts_utc(运行号)', '代码印章 run.git_head', '安装树 CODE_VERSION.git_head',
    '决议条目 first_publish=决议日', 'JP_POLICY_TARGET 缺口=registry_absent', '锚「3个月前」as_of', '锚「最新一期」as_of',
    '锚点数=2(无 12 个月前锚)', 'rates_decomposition 窗端点', '情景数', '历史段数=0', '转折数'}
for p in PTS:
    p['structural'] = p['desc'] in STRUCT_DESCS
assert sum(1 for p in PTS if p['structural']) == len(STRUCT_DESCS), '结构性自检标记数与清单不符'

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, 'recompute_points.json'), 'w', encoding='utf-8') as f:
    json.dump(PTS, f, ensure_ascii=False, indent=1)
with open(os.path.join(OUT, 'recompute_probes.json'), 'w', encoding='utf-8') as f:
    json.dump(PR, f, ensure_ascii=False, indent=1, default=str)

# ── 摘要 ─────────────────────────────────────────────────────────────────────
cats = {}
for p in PTS:
    c = cats.setdefault(p['cat'], {'n': 0, 'bad': 0, 'n_ind': 0, 'bad_ind': 0})
    c['n'] += 1
    c['bad'] += (0 if p['ok'] else 1)
    if not p['structural']:
        c['n_ind'] += 1
        c['bad_ind'] += (0 if p['ok'] else 1)
IND = [p for p in PTS if not p['structural']]
print('TOTAL rows=%d | recompute_points(independent)=%d mismatches=%d | structural=%d bad=%d' % (
    len(PTS), len(IND), sum(1 for p in IND if not p['ok']),
    len(PTS) - len(IND), sum(1 for p in PTS if p['structural'] and not p['ok'])))
for k in sorted(cats):
    print('  %s n=%d bad=%d | independent n=%d bad=%d' % (k, cats[k]['n'], cats[k]['bad'], cats[k]['n_ind'], cats[k]['bad_ind']))
for p in PTS:
    if not p['ok']:
        print('MISMATCH', p['id'], p['cat'], p['desc'], '| computed=', _fm(p['computed']), '| reported=',
              _fm(p['reported']), '| cell=', _fm(p['engine_cell']), '| lit=', p['literal_found'], '|', p['how'])
print('sample:')
for p in PTS[:6] + PTS[-6:]:
    print(' ', p['id'], p['ok'], p['desc'], _fm(p['computed']), _fm(p['reported']))
