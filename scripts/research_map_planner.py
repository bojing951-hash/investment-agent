# -*- coding: utf-8 -*-
"""Audit-R18: 全球宏观地图问句的确定性研究计划面(零模型编排层)。

「给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、
3个月前和最新一期,分别处于什么增长、通胀和货币政策环境?过去一年最重要
的三个转折…传导机制…历史上哪些时期结构最像,随后3、6、12个月…」一类
问句,旧口径下零词面命中(metrics=[])→降级经济体概览,plan 却 run_ok=True
——答非所问面被当正例放行。本模块给出共享研究计划(取数/报告/验收同一
份,不手填指标代码):

- 地区×维度→注册表指标: 注册表 economy+本模块声明的维度映射(确定性,
  零语义翻译);序列在场性按数据面判定,缺席=如实缺口(检索范围+缺什么+
  影响写进计划),不虚构不编造。
- 三个对照时点(点锚): 「12个月前/3个月前/最新一期」=日历点(研究截止日
  −N 月),与「事件发生后3个月」=事后偏移锚(事件日+3月)**分记两类**
  (kind=point / kind=ex_post),不混同。
- 转折候选: 计划内政策+通胀序列过去 12 个月最大 |3 月变化|确定性排序,
  只作候选面;谁先变/跟进/背离的判断归 Agent 席(reader_map)。
- 点值面: 每指标×每点锚取 ≤锚日的最新有效观测(快照/采集档同通道
  wd.metric_series),水平指数序列同时给派生同比。

零模型纪律不变: 本模块不生成任何判断文字;MAP_REPORT 的总判断/传导/转折
叙述/历史段全部来自 Agent 席 judgment.reader_map,attach 只验结构,
report 段做数值回贴核对(引擎点值 vs 判断叙述中的数字)。"""

import re

# ── 地区×维度指标映射(声明式;入场须注册表在册,否则如实缺口) ────────
# 每格按优先序;「目标/操作/月均」口径注记=任务3央行公告四分面
# (宣布日/生效日/市场利率月均/政策目标)的引擎侧注解。
REGION_DIMENSION_METRICS = {
    'US': {
        'growth': [('US_REAL_GDP', '实际GDP(季频水平)'),
                   ('UNEMPLOYMENT', '失业率(月频)'),
                   ('INDPRO', '工业生产指数(月频水平)')],
        'inflation': [('CPI', 'CPI(月频水平,同比派生)'),
                      ('CORE_CPI', '核心CPI(月频水平,同比派生)'),
                      ('CORE_PCE', '核心PCE(月频水平,同比派生)')],
        'policy': [('DFEDTARU', '联邦基金目标区间上限(政策目标口径)'),
                   ('DFF', '有效联邦基金利率(日频市场利率)')],
    },
    'CN': {
        'growth': [('CN_PMI_MFG', '制造业PMI(月频)'),
                   ('CN_PPI_YOY', 'PPI同比(月频)')],
        'inflation': [('CN_CPI_YOY', 'CPI同比(月频)')],
        'policy': [('CN_OMO_7D', '7天逆回购利率(操作目标口径)'),
                   ('CN_LPR_1Y', 'LPR 1年期(报价基准)')],
    },
    'EA': {
        'growth': [],            # 注册表无欧元区增长指标(如实缺口)
        'inflation': [('EA_HICP_YOY', 'HICP同比(月频)')],
        'policy': [('ECB_MRO', '欧央行主要再融资利率(政策目标口径)'),
                   ('ECB_DFR', '欧央行存款便利利率(操作下限口径)')],
    },
    'JP': {
        'growth': [],            # 注册表无日本增长指标(如实缺口)
        'inflation': [('JP_CPI_TOKYO_YOY', '东京都CPI同比(月频)')],
        'policy': [('JP_POLICY_RATE', '无担保隔夜拆借利率(月均口径——'
                                     '月均≠政策目标宣布值,任务3四分注记)')],
    },
}
# 任务3复算面: 美国十年期 名义/实际/盈亏平衡 三利率同观测日复算
US_RATES_TRIO = ['UST_10Y', 'TIPS_10Y', 'BEI_10Y']

DIMENSION_WORDS = [('增长', 'growth'), ('通胀', 'inflation'),
                   ('货币政策', 'policy')]
MAP_SHAPE_WORDS = ('地图', '转折', '传导', '结构最像', '环境')
_DIM_LABEL = {'growth': '增长', 'inflation': '通胀', 'policy': '货币政策'}
_REGION_LABEL = {'US': '美国', 'CN': '中国', 'EA': '欧元区', 'JP': '日本'}

# 点锚词形: 最新一期/最新/当前 | N个月前 | 一年前(=12个月前)
_POINT_LATEST_RE = re.compile(r'最新(?:一期|数据)?|当前')
_POINT_MONTHS_RE = re.compile(
    r'(?P<num>[0-9]+|[一二两三四五六七八九十]+)\s*个?\s*月\s*前')
_POINT_YEARS_RE = re.compile(r'(?P<num>[0-9]+|[一二两三四五六七八九十]+)\s*年\s*前')
# 事后偏移: 随后/之后/其后 的 N(、M、K)?个月
_EXPOST_RE = re.compile(
    r'(?:随后|之后|其后)(?P<list>(?:\s*[0-9一二两三四五六七八九十]+\s*[、,，和及]\s*)*'
    r'\s*[0-9一二两三四五六七八九十]+\s*个?\s*月)')
_FW_TRANS = str.maketrans('０１２３４５６７８９．', '0123456789.')
_NUM_MAP = {'一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6,
            '七': 7, '八': 8, '九': 9, '十': 10}


def _norm_q(q):
    """全角→半角数字翻译(与 orchestrator._norm_question 同坐标语义,
    1:1 替换保位置——跨度可直接回投原问题坐标系)。"""
    return (q or '').translate(_FW_TRANS)


def consumed_time_spans(question):
    """点锚/事后偏移词形的字符区间(规范化副本坐标)。

    供 _question_window/_evaluate_data_requirements 作覆盖集: 这些时间
    分量是点/事后语义(已被本模块消费),不是范围词形也不是残缺数量
    ——只对地图问句透传,非地图问句口径零变化。"""
    qn = _norm_q(question)
    spans = []
    for rx in (_POINT_MONTHS_RE, _POINT_YEARS_RE, _EXPOST_RE):
        for m in rx.finditer(qn):
            spans.append((m.start(), m.end()))
    return spans


def _cn_num(tok):
    tok = (tok or '').strip()
    if tok.isdigit():
        return int(tok)
    if tok in _NUM_MAP:
        return _NUM_MAP[tok]
    if tok.startswith('十') and len(tok) == 2:
        return 10 + _NUM_MAP.get(tok[1], 0)
    if tok.endswith('十') and len(tok) == 2:
        return _NUM_MAP.get(tok[0], 1) * 10
    if len(tok) == 3 and tok[1] == '十':
        return _NUM_MAP.get(tok[0], 1) * 10 + _NUM_MAP.get(tok[2], 0)
    return None


def _shift_months(iso_date, n):
    """研究时点平移 N 月(与 orchestrator._shift_months 同语义: 日夹紧到月末)。"""
    import calendar
    y, m, d = int(iso_date[:4]), int(iso_date[5:7]), int(iso_date[8:10])
    tot = y * 12 + (m - 1) - n
    y2, m2 = tot // 12, tot % 12 + 1
    return '%04d-%02d-%02d' % (y2, m2, min(d, calendar.monthrange(y2, m2)[1]))


def detect_map_question(question, ent):
    """地图问句形判(严格,防误触发): ≥2 个在册经济体 + ≥2 个维度词 +
    任一形状词。不满足=完全走既有口径(零回归)。"""
    q = question or ''
    ecos = [e for e in (ent.get('economies') or [])
            if e in REGION_DIMENSION_METRICS]
    dims = {d for w, d in DIMENSION_WORDS if w in q}
    return len(ecos) >= 2 and len(dims) >= 2 and any(w in q for w in MAP_SHAPE_WORDS)


def parse_point_anchors(question, cutoff_iso):
    """三个对照时点(日历点锚)。返回按 N 降序(12月前→3月前→最新)。

    「N个月前」= 研究截止日−N 月的日历点——与「事件发生后N个月」(事后
    偏移,事件日+N 月)分记两类,见 parse_ex_post_offsets。"""
    q = question or ''
    months = set()
    for m in _POINT_MONTHS_RE.finditer(q):
        n = _cn_num(m.group('num'))
        if n and 1 <= n <= 120:
            months.add(n)
    for m in _POINT_YEARS_RE.finditer(q):
        n = _cn_num(m.group('num'))
        if n and 1 <= n <= 10:
            months.add(n * 12)
    anchors = [{'kind': 'point', 'label': f'{n}个月前',
                'as_of': _shift_months(cutoff_iso, n), 'months_before': n}
               for n in sorted(months, reverse=True)]
    if _POINT_LATEST_RE.search(q):
        anchors.append({'kind': 'point', 'label': '最新一期',
                        'as_of': cutoff_iso, 'months_before': 0})
    return anchors


def parse_ex_post_offsets(question):
    """历史事后窗偏移(「随后3、6、12个月」→[3,6,12])。锚在事件日
    (转折日/历史类比基准日),向**前**看——与日历点锚(截止日−N月)分记。"""
    out = []
    for m in _EXPOST_RE.finditer(question or ''):
        for tok in re.findall(r'[0-9一二两三四五六七八九十]+', m.group('list')):
            n = _cn_num(tok)
            if n and 1 <= n <= 60 and n not in [x['months'] for x in out]:
                out.append({'kind': 'ex_post', 'months': n,
                            'anchored_on': '事件日(转折/历史类比基准)向前后移'})
    out.sort(key=lambda x: x['months'])
    return out


def plan_map(question, ent, reg_by_id, cutoff_iso):
    """共享研究计划本体: 地区×维度指标+在场性/缺口、点锚、事后窗。"""
    ecos = [e for e in (ent.get('economies') or [])
            if e in REGION_DIMENSION_METRICS]
    dims = [d for w, d in DIMENSION_WORDS if w in (question or '')]
    regions, metrics, gaps = {}, [], []
    for eco in ecos:
        regions[eco] = {'label': _REGION_LABEL[eco], 'dimensions': {}}
        for dim in dims:
            cells = []
            for mid, mnote in REGION_DIMENSION_METRICS[eco].get(dim, []):
                m = reg_by_id.get(mid)
                if m is None:
                    gaps.append({'region': eco, 'dimension': dim,
                                 'metric_id': mid,
                                 'gap': 'registry_absent',
                                 'note': f'计划指标 {mid} 不在注册表(检索范围='
                                         f'注册表 economy={eco} 面)——该格以'
                                         f'缺口呈现,不虚构'})
                    continue
                cells.append({'metric_id': mid,
                              'display_name': m.get('display_name'),
                              'face_note': mnote,
                              'frequency': m.get('frequency'),
                              'unit': m.get('unit')})
                if mid not in metrics:
                    metrics.append(mid)
            if not cells:
                gaps.append({'region': eco, 'dimension': dim,
                             'metric_id': None, 'gap': 'no_registry_metric',
                             'note': f'注册表检索范围(economy={eco})无'
                                     f'{_DIM_LABEL[dim]}维度指标——该格'
                                     f'环境对照缺席(影响: {_REGION_LABEL[eco]}'
                                     f'{_DIM_LABEL[dim]}环境三时点对照不可判,'
                                     f'总判断适用范围相应缩小)'})
            regions[eco]['dimensions'][dim] = cells
    plan = {
        'map_question': True,
        'shared_by': '取数(plan 指标并入 S4/数据需求面)/报告(MAP_REPORT '
                     '对照表与数值回贴)/验收(同一份 plan 判据)——不手填指标代码',
        'regions': regions,
        'dimensions': dims,
        'metrics': metrics,
        'context_metrics': [m for m in US_RATES_TRIO],
        'point_anchors': parse_point_anchors(question, cutoff_iso),
        'ex_post_offsets': parse_ex_post_offsets(question),
        'anchor_semantics_note': '「N个月前」=日历点锚(研究截止日−N月);'
                                 '「事件发生后N个月」=事后偏移锚(事件日+N月) '
                                 '——两类分记,前者用于三时点对照,后者用于'
                                 '转折/历史类比的随后 3/6/12 月事后窗',
        'dimension_gaps': gaps,
        'cutoff': cutoff_iso,
        'consumed_time_spans': consumed_time_spans(question),
    }
    return plan


# ── 点值面(每指标×每点锚: ≤锚日最新有效观测) ──────────────────────────

def _series(mid, snap, root):
    import workbench_data as wd
    return wd.metric_series(mid, snapshot=snap, root=root)


def _obs_at(dates, values, as_of):
    """≤as_of 的最新观测(二分;无= None)。"""
    import bisect
    i = bisect.bisect_right(dates, as_of)
    if i == 0:
        return None
    return i - 1


def _derive_yoy(dates, values, idx):
    """水平序列在 idx 处的派生同比(找 ~12 月前最近观测;不可得=None)。"""
    if idx is None:
        return None
    d0 = dates[idx]
    target = _shift_months(d0, 12)
    j = _obs_at(dates, values, target)
    if j is None or j >= idx:
        return None
    base, cur = values[j], values[idx]
    try:
        if base and base > 0:
            return round((cur / base - 1.0) * 100.0, 2)
    except (TypeError, ZeroDivisionError):
        return None
    return None


def point_values(plan, snap, root):
    """对照点值: per region/dimension/metric × anchor。

    序列可得→逐锚取值(水平指数附派生同比);序列不可得→ face='absent'
    + 缺什么注记(不编造)。返回 {'cells': [...], 'absent': [...]}。"""
    cells, absent = [], []
    mids = list(dict.fromkeys(plan['metrics'] + plan.get('context_metrics', [])))
    series_cache = {}
    for mid in mids:
        s, _err = _series(mid, snap, root)
        series_cache[mid] = s
    for eco, rface in plan['regions'].items():
        for dim, mlist in rface['dimensions'].items():
            for cell in mlist:
                mid = cell['metric_id']
                s = series_cache.get(mid)
                if not s or not s.get('dates'):
                    absent.append({
                        'region': eco, 'dimension': dim, 'metric_id': mid,
                        'display_name': cell.get('display_name'),
                        'gap': 'series_absent',
                        'note': f'{cell.get("display_name") or mid} 历史序列'
                                f'不可得(检索范围=快照 series_store+注册表 '
                                f'history_source 采集档通道)——三时点对照该行'
                                f'以「数据不可得」呈现,禁以现值冒充锚值'})
                    continue
                dates, values = s['dates'], s['values']
                unit = s.get('unit') or ''
                level_series = _is_level_unit(unit)
                row = {'region': eco, 'dimension': dim, 'metric_id': mid,
                       'display_name': cell.get('display_name'),
                       'unit': unit, 'face_note': cell.get('face_note'),
                       'source': s.get('source'), 'anchors': {}}
                for a in plan['point_anchors']:
                    i = _obs_at(dates, values, a['as_of'])
                    if i is None:
                        row['anchors'][a['label']] = {
                            'status': 'no_observation_on_or_before_anchor',
                            'as_of': a['as_of']}
                        continue
                    v = {'status': 'ok', 'as_of': a['as_of'],
                         'observation_date': dates[i],
                         'value': values[i]}
                    if level_series:
                        v['derived_yoy_pct'] = _derive_yoy(dates, values, i)
                        v['value_kind'] = 'level(同比须用 derived_yoy_pct)'
                    row['anchors'][a['label']] = v
                cells.append(row)
    return {'cells': cells, 'absent': absent}


# ── 转折候选(确定性排序;判断归 Agent) ─────────────────────────────────

def _is_level_unit(unit):
    """水平序列判定(同比派生适用): 指数点/GDP 级——百分比/利率/PMI
    扩散指数原值即环境读数,不做同比。"""
    u = str(unit or '')
    return u.startswith('index_point') or u == 'billion_usd'


def _monthly_series_for_turning(dates, values, unit):
    """转折探测用月序列: 水平序列转**同比空间**(指数漂移≠转折,同比
    变化才是环境转折),其余原样月末最新。"""
    mon = _monthly_last(dates, values)
    if not _is_level_unit(unit):
        return mon
    out = []
    for ym, d, v in mon:
        tgt = _shift_months(ym + '-01', 12)
        base = None
        for ym2, d2, v2 in mon:
            if ym2 <= tgt[:7]:
                base = v2
        if base:
            try:
                out.append((ym, d, round((float(v) / float(base) - 1.0)
                                         * 100.0, 4)))
            except (TypeError, ZeroDivisionError, ValueError):
                continue
    return out

def _monthly_last(dates, values):
    """日频→月末最新观测(月频序列原样)。返回 [(ym, date, value)]。"""
    out, seen = [], {}
    for d, v in zip(dates, values):
        ym = d[:7]
        seen[ym] = (d, v)
    for ym in sorted(seen):
        d, v = seen[ym]
        out.append((ym, d, v))
    return out


def turning_candidates(plan, snap, root, top_n=3):
    """过去 12 个月政策+通胀序列最大 |3 月变化| 排序(候选面)。

    只列引擎确定性算得出的事实(序列/前后值/日期);「谁先变/跟进/背离」
    的判断=Agent 席 reader_map.turnings(须引用此候选面或如实说明偏离)。"""
    cutoff = plan['cutoff']
    y0 = cutoff[:7]
    import sys as _sys
    months_back = []
    for k in range(13):
        months_back.append(_shift_months(f'{y0}-01', k)[ :7])
    window = set(months_back)
    cands = []
    seen_mid = set()
    for eco, rface in plan['regions'].items():
        for dim in ('policy', 'inflation'):
            for cell in rface['dimensions'].get(dim, []):
                mid = cell['metric_id']
                if mid in seen_mid:
                    continue
                seen_mid.add(mid)
                s, _err = _series(mid, snap, root)
                if not s or not s.get('dates'):
                    continue
                mon = [(ym, d, v) for ym, d, v in _monthly_series_for_turning(
                    s['dates'], s['values'], s.get('unit')) if ym in window]
                if len(mon) < 4:
                    continue
                best = None
                for i in range(len(mon) - 3):
                    ym_a, d_a, v_a = mon[i]
                    ym_b, d_b, v_b = mon[i + 3]
                    try:
                        delta = float(v_b) - float(v_a)
                    except (TypeError, ValueError):
                        continue
                    if best is None or abs(delta) > abs(best['delta']):
                        best = {'from_ym': ym_a, 'to_ym': ym_b,
                                'from_date': d_a, 'to_date': d_b,
                                'value_before': v_a, 'value_after': v_b,
                                'delta': round(delta, 4)}
                if best and best['delta'] != 0:
                    best.update({'region': eco, 'dimension': dim,
                                 'metric_id': mid,
                                 'display_name': cell.get('display_name'),
                                 'unit': ('同比%(派生于水平序列)'
                                          if _is_level_unit(s.get('unit'))
                                          else s.get('unit'))})
                    cands.append(best)
    cands.sort(key=lambda c: (-abs(c['delta']), c['metric_id']))
    return {'basis': '过去12个月(研究截止日)内 3 个月滚动变化绝对值最大者;'
                     '确定性计算,仅作候选——三个转折的取舍与谁先变判断归 '
                     'Agent 席 reader_map',
            'candidates': cands[:max(top_n * 3, 9)], 'top_n_expected': top_n}


# ── 读者报告渲染(任务2结构;确定性装配零生成,L3 文字归 Agent) ─────────

_DIM_ORDER = {'growth': 0, 'inflation': 1, 'policy': 2}


def _fmt_val(v):
    if v is None:
        return '数据不可得'
    if isinstance(v, float):
        return f'{v:g}'
    return str(v)


def render_map_report(rj, judgment_doc, review_state=None):
    """MAP_REPORT.md 正文(读者可直读可核查: 关键数字附来源/单位/实际观测日)。

    装配面=report.json research_plan(共享计划+点值+转折候选)+Agent 席
    judgment.reader_map 原文;零生成——总判断/走位/传导叙述/转折判断/历史段
    全部来自 reader_map(attach 契约已验非空+数值经 judgment_contract 回贴
    核对),引擎只排表与落来源。"""
    rp = rj.get('research_plan') or {}
    rm = (judgment_doc or {}).get('reader_map') or {}
    pv = rp.get('point_values') or {}
    run = rj.get('run') or {}
    lines = ['# 全球宏观经济变化地图(读者报告)', '']
    lines.append(f"- 问题: {run.get('question')}")
    lines.append(f"- 研究截止日: {rp.get('cutoff')} | 快照: "
                 f"{(rj.get('layers', {}).get('L1_事实层', {}) or {}).get('snapshot_id')}"
                 f" | 运行: {run.get('ts_utc')} | 代码: {run.get('git_head')}")
    lines.append('- 口径: 三个对照时点=日历点锚(截止日−12月/−3月/最新一期);'
                 '「随后3、6、12个月」=事件后偏移(转折/类比基准日+N月)'
                 '——两类时间含义不同,分记不混同')
    lines.append('- 分工: 表格与数值=引擎确定性面(每格附实际观测日);'
                 '判断文字=Agent 席 reader_map 原文(attribution=ai_inferred,'
                 '经独立语义审查)')
    lines.append('')

    # 一句总判断
    lines += ['## 一句总判断', '', str(rm.get('headline_conclusion') or
                                      '(缺席——attach 契约应已拦截)'), '']

    # 四地三时点对照表
    lines += ['## 四地三时点环境对照', '']
    anchors = [a['label'] for a in rp.get('point_anchors') or []]
    lines.append('| 地区 | 维度 | 指标(口径) | ' + ' | '.join(anchors)
                 + ' | 单位 |')
    lines.append('|---|---|---|' + '---|' * len(anchors) + '---|')
    rows = sorted(pv.get('cells') or [],
                  key=lambda c: (c.get('region') or '',
                                 _DIM_ORDER.get(c.get('dimension'), 9),
                                 c.get('metric_id') or ''))
    for c in rows:
        vals = []
        for a in anchors:
            v = (c.get('anchors') or {}).get(a) or {}
            if v.get('status') != 'ok':
                vals.append('数据不可得')
            elif v.get('value_kind', '').startswith('level'):
                yoy = v.get('derived_yoy_pct')
                vals.append(_fmt_val(v.get('value'))
                            + (f'(同比≈{yoy:g}%)' if yoy is not None else ''))
            else:
                vals.append(_fmt_val(v.get('value')))
        eco = c.get('region') or ''
        lines.append(f"| {eco} | {c.get('dimension')} | "
                     f"{c.get('display_name')}({c.get('face_note')}) | "
                     + ' | '.join(vals) + f" | {c.get('unit')} |")
    for ab in pv.get('absent') or []:
        lines.append(f"| {ab.get('region')} | {ab.get('dimension')} | "
                     f"{ab.get('display_name')} | " + ' | '.join(['数据不可得']
                     * len(anchors)) + ' | — |')
    lines.append('')
    lines.append('> 缺数格说明(检索范围+影响): ')
    for ab in pv.get('absent') or []:
        lines.append(f"> - {ab.get('note')}")
    for g in rp.get('dimension_gaps') or []:
        lines.append(f"> - {g.get('note')}")
    lines.append('')

    # 各地区环境走位
    lines += ['## 各地区环境走位(从什么环境走到什么环境)', '']
    for r in rm.get('regions') or []:
        lines.append(f"### {_REGION_LABEL.get(r.get('region'), r.get('region'))}")
        lines.append(str(r.get('from_to') or '(缺席)'))
        lines.append('')

    # 传导图(文字)
    lines += ['## 证据最充分的传导机制(有文字的传导图)', '']
    for ch in rm.get('transmission') or []:
        lines.append(f"### {ch.get('chain_name') or ch.get('name') or '传导链'}")
        links = ch.get('links') or []
        for i, lk in enumerate(links):
            arrow = '→ ' if i else '① '
            lines.append(f"{arrow}**{lk.get('observed_fact')}**")
            lines.append(f"   - 因果假设: {lk.get('causal_hypothesis')}")
            lines.append(f"   - 竞争解释: {lk.get('competing_explanation')}")
            lines.append(f"   - 能区分解释的指标: {lk.get('distinguishing_metric')}")
        lines.append('')

    # 三个转折
    lines += ['## 过去一年的三个转折(按日期)', '']
    lines.append('| 日期 | 指标 | 前值→后值 | 谁先变 | 跟进/背离 |')
    lines.append('|---|---|---|---|---|')
    for t in rm.get('turnings') or []:
        lines.append(f"| {t.get('date')} | {t.get('metric_id')} | "
                     f"{_fmt_val(t.get('value_before'))}→"
                     f"{_fmt_val(t.get('value_after'))} | "
                     f"{t.get('first_mover')} | {t.get('follow_or_diverge')} |")
    lines.append('')
    cand = (rp.get('turning_candidates') or {}).get('candidates') or []
    if cand:
        lines.append('<details><summary>引擎转折候选面(确定性排序,判断依据可核)</summary>')
        lines.append('')
        lines.append('| 地区 | 维度 | 指标 | 窗口 | 前值→后值 | Δ |')
        lines.append('|---|---|---|---|---|---|')
        for c in cand:
            lines.append(f"| {c.get('region')} | {c.get('dimension')} | "
                         f"{c.get('metric_id')} | {c.get('from_ym')}.."
                         f"{c.get('to_ym')} | {c.get('value_before')}→"
                         f"{c.get('value_after')} | {c.get('delta')} |")
        lines.append('')
        lines.append('</details>')
        lines.append('')

    # 关键数字与来源
    lines += ['## 关键数字与来源(实际观测日)', '']
    lines.append('| 指标 | 锚 | 值 | 单位 | 实际观测日 | 来源 |')
    lines.append('|---|---|---|---|---|---|')
    for c in rows:
        for a in anchors:
            v = (c.get('anchors') or {}).get(a) or {}
            if v.get('status') != 'ok':
                continue
            src = c.get('source')
            src_txt = src if isinstance(src, str) else (
                (src or {}).get('source') or (src or {}).get('file') or '—')
            lines.append(f"| {c.get('metric_id')} | {a} | "
                         f"{_fmt_val(v.get('value'))} | {c.get('unit')} | "
                         f"{v.get('observation_date')} | {src_txt} |")
    lines.append('')

    # 历史类比
    lines += ['## 历史上结构最像的时期(可验证;≤3段)', '']
    for h in rm.get('history_periods') or []:
        tag = '(美国指标类比——锚定美国序列)' if h.get('us_analog') else ''
        lines.append(f"### {h.get('period_label')} {tag}")
        lines.append(f"- 相似点: {h.get('similarity')}")
        lines.append(f"- 关键差异: {h.get('difference')}")
        lines.append(f"- 其他经济体是否同步: {h.get('other_regions_sync')}")
        ex = h.get('ex_post') or {}
        lines.append(f"- 随后3个月(事件后+3月): {ex.get('3m')}")
        lines.append(f"- 随后6个月: {ex.get('6m')}")
        lines.append(f"- 随后12个月: {ex.get('12m')}")
        if h.get('data_note'):
            lines.append(f"- 样本注记: {h.get('data_note')}")
        lines.append('')

    # 语义审查面
    lines += ['## 语义审查', '']
    if review_state:
        if review_state.get('verdict'):
            lines.append(f"- 席位已裁: {review_state.get('verdict')}"
                         f"(裁决链 {review_state.get('verdicts_n')} 档)")
        else:
            lines.append('- 独立席位待裁(review required)')
    else:
        lines.append('- 独立席位待裁')
    lines.append('')
    lines.append('---')
    lines.append('渲染纪律: 本件只装配在场事实(引擎确定性面)与 Agent 席判断原文,'
                 '零新增生成;数值与判断的核对面=attach 契约(judgment_contract '
                 'reader_map 数值回贴)+独立语义审查席。')
    return '\n'.join(lines) + '\n'
