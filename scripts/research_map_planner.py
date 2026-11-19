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
        'growth': [('CN_PMI_MFG', '制造业PMI(月频)')],
        # Audit-R19 任务2: 中国 PPI 归入价格(通胀)维——出厂价格是价格面,
        # 不作增长代理(旧口径挂在增长维=维度误归)。
        'inflation': [('CN_CPI_YOY', 'CPI同比(月频)'),
                      ('CN_PPI_YOY', 'PPI同比(月频,价格维)')],
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
        # Audit-R19 任务2: 隔夜市场利率与央行目标**分别列示**——目标行
        # 声明式入场,注册表/数据面缺席时以 registry_absent 缺口呈现
        # (查过的来源+影响随 gap 注记),不以市场月均冒充宣布值。
        'policy': [('JP_POLICY_RATE', '无担保隔夜拆借利率(月均口径——'
                                     '月均≠政策目标宣布值,任务3四分注记)'),
                   ('JP_POLICY_TARGET', '央行政策目标利率(宣布值口径——'
                                       '与市场月均分别列示)')],
    },
}
# 任务3复算面: 美国十年期 名义/实际/盈亏平衡 三利率同观测日复算
US_RATES_TRIO = ['UST_10Y', 'TIPS_10Y', 'BEI_10Y']

# ── Audit-R19 任务1: 发布纪律(历史对照只用当时已发布的数据) ────────────
# 每指标族按官方常规发布节奏给「观测→首次发布」的推定时滞(天)。推定非逐条
# 实录;规则文本随锚值披露,读者可核。US_REAL_GDP 季度 +29 天以 2026Q3
# (观测 2026-07-01..09-30,发布 2026-10-29)实测锚定。负值=观测月末前发布
# (CN_PMI_MFG: 国家统计局当月月末发布当月值)。
RELEASE_RULES = {
    'CPI':            ('monthly', 13, 'BLS CPI 次月中旬发布(月末+13天,推定)'),
    'CORE_CPI':       ('monthly', 13, 'BLS CPI 次月中旬发布(月末+13天,推定)'),
    'CORE_PCE':       ('monthly', 30, 'BEA 个人收支报告次月末发布(月末+30天,推定)'),
    'UNEMPLOYMENT':   ('monthly', 5, 'BLS 就业形势报告次月首周发布(月末+5天,推定)'),
    'INDPRO':         ('monthly', 15, 'G.17 工业生产次月中旬发布(月末+15天,推定)'),
    'US_REAL_GDP':    ('quarterly', 29, 'BEA GDP 初值季末+29天发布(2026Q3=2026-10-29 实测锚定)'),
    'CN_PMI_MFG':     ('monthly', -1, '国家统计局当月月末发布(月末−1天,推定)'),
    'CN_CPI_YOY':     ('monthly', 9, '国家统计局次月9日前后发布(月末+9天,推定)'),
    'CN_PPI_YOY':     ('monthly', 9, '国家统计局次月9日前后发布(月末+9天,推定)'),
    'EA_HICP_YOY':    ('monthly', 16, 'Eurostat HICP 终值次月中旬发布(月末+16天,推定)'),
    'JP_CPI_TOKYO_YOY': ('monthly', 25, '总务省东京CPI次月下旬发布(月末+25天,推定)'),
    'JP_POLICY_RATE': ('monthly', 5, 'BOJ 月均次月初公布(月末+5天,推定)'),
    'DFF':            ('daily', 1, 'NY Fed 有效联邦基金利率次日发布(+1天,推定)'),
    'DFEDTARU':       ('daily', 0, 'FOMC 目标区间决议日当日公布'),
    'ECB_MRO':        ('daily', 0, 'ECB 决议日当日公布(变更日观测)'),
    'ECB_DFR':        ('daily', 0, 'ECB 决议日当日公布(变更日观测)'),
}
_RELEASE_DEFAULTS = {
    'monthly': (20, '月频官方发布节奏推定(月末+20天)'),
    'quarterly': (35, '季频官方发布节奏推定(季末+35天)'),
    'daily': (1, '日频次日发布推定(+1天)'),
}


def _publish_date(metric_id, frequency, obs_date):
    """观测日→首次发布日(推定规则)。返回 (publish_date, rule_text)。

    monthly: 观测月末+days;quarterly(季首观测): 季末+days;daily: +days。
    days<0 = 当月月末前发布(月末+负天数)。"""
    import calendar
    if not obs_date:
        return None, None
    kind, days, rule = RELEASE_RULES.get(
        metric_id, (None, None, None))
    freq = (frequency or kind or 'monthly')
    if kind is None:
        days, rule = _RELEASE_DEFAULTS.get(
            freq, _RELEASE_DEFAULTS['monthly'])
        kind = freq
    y, m, d = int(obs_date[:4]), int(obs_date[5:7]), int(obs_date[8:10])
    if kind == 'quarterly' or (kind != 'daily' and d == 1 and m in (1, 4, 7, 10)
                               and metric_id == 'US_REAL_GDP'):
        q_end_m = m + 2                       # 季首观测→季末
        last = calendar.monthrange(y, q_end_m)[1]
        base = '%04d-%02d-%02d' % (y, q_end_m, last)
    elif kind == 'daily':
        base = obs_date
    else:                                     # monthly: 观测月末
        last = calendar.monthrange(y, m)[1]
        base = '%04d-%02d-%02d' % (y, m, last)
    import datetime
    b = datetime.date.fromisoformat(base)
    return (b + datetime.timedelta(days=days)).isoformat(), rule

DIMENSION_WORDS = [('增长', 'growth'), ('通胀', 'inflation'),
                   ('货币政策', 'policy')]

# Audit-R19 任务3: 传导图须从冲击连到指标与资产——引擎侧资产指标全集
# (在场性按快照 series_store 判定,plan 的 asset_universe 只列在场者)。
ASSET_UNIVERSE = ['UST_2Y', 'UST_5Y', 'UST_10Y', 'UST_30Y', 'TIPS_5Y',
                  'TIPS_10Y', 'BEI_5Y', 'BEI_10Y', 'CURVE_2S10S', 'SPX',
                  'NDX', 'RUT', 'DAX', 'CAC40', 'NIKKEI225', 'HSI', 'SHCOMP',
                  'DXY', 'EURUSD', 'USDJPY', 'USDCNY', 'GOLD_F', 'SILVER_F',
                  'BRENT_F', 'HY_OAS', 'IG_OAS', 'BB_OAS', 'B_OAS',
                  'CCC_OAS', 'VIX']
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
                                         f'注册表 economy={eco} 面+快照 '
                                         f'series_store+采集档通道)——{mid} '
                                         f'历史序列与元数据均不可得,该格以'
                                         f'「数据不可得」呈现(影响: '
                                         f'{_REGION_LABEL[eco]}'
                                         f'{_DIM_LABEL[dim]}环境该口径三时点'
                                         f'对照不可判,不以相邻口径冒充),'
                                         f'不虚构'})
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
    """派生同比(严格同基期: 月度配去年同月/季度配去年同季)。

    Audit-R19 任务1: 基期观测日必须==观测日−12 月(同月/同季),缺基期=None
    ——不再取「最近前值」(旧口径 13 个月变化会被标成同比)。"""
    if idx is None:
        return None
    d0 = dates[idx]
    target = _shift_months(d0, 12)
    j = _obs_at(dates, values, target)
    if j is None or j >= idx or dates[j] != target:
        return None                       # 基期月缺席≠最近前值可替
    base, cur = values[j], values[idx]
    try:
        if base and base > 0:
            return round((cur / base - 1.0) * 100.0, 2)
    except (TypeError, ZeroDivisionError):
        pass
    return None


def _latest_valid_yoy(dates, values, idx):
    """idx 之前最近一个「同基期在場」观测的 (observation_date, yoy_pct)。

    Audit-R19 任务1: 缺基期标不可得时可另列最近有效同比及月份——本函数
    给那个「最近有效」(不虚构,逐点用严格基期复算)。"""
    for k in range(idx, -1, -1):
        y = _derive_yoy(dates, values, k)
        if y is not None:
            return {'observation_date': dates[k], 'yoy_pct': y}
    return None


def point_values(plan, snap, root):
    """对照点值: per region/dimension/metric × anchor。

    Audit-R19 任务1 双纪律:
    - 发布纪律: 锚值=发布日≤锚日的最新观测(_publish_date 推定规则随格披露)
      ——历史对照只用当时已发布的数据;
    - 同比基期纪律: 月度同比只配去年同月/季度只配去年同季,缺基期=
      yoy_status='no_same_period_base'+derived_yoy_pct=None+另列最近有效
      同比及月份(latest_valid_yoy)——13 个月变化不得写成同比。
    序列不可得→ absent+缺什么注记(不编造)。返回
    {'cells': [...], 'absent': [...], 'asset_universe': [...]}。"""
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
                freq = s.get('frequency') or cell.get('frequency')
                level_series = _is_level_unit(unit)
                row = {'region': eco, 'dimension': dim, 'metric_id': mid,
                       'display_name': cell.get('display_name'),
                       'unit': unit, 'face_note': cell.get('face_note'),
                       'source': s.get('source'), 'anchors': {}}
                for a in plan['point_anchors']:
                    # 发布纪律: 只取「观测日≤锚日且发布日≤锚日」的最新观测
                    i = None
                    for k in range(len(dates) - 1, -1, -1):
                        if dates[k] > a['as_of']:
                            continue
                        pd_iso, _rule = _publish_date(mid, freq, dates[k])
                        if pd_iso is None or pd_iso <= a['as_of']:
                            i = k
                            break
                    if i is None:
                        row['anchors'][a['label']] = {
                            'status': 'no_published_observation_on_or_before_'
                                      'anchor',
                            'as_of': a['as_of'],
                            'note': '锚日前无「已发布」观测(发布日按推定规则)'}
                        continue
                    pub_iso, rule = _publish_date(mid, freq, dates[i])
                    v = {'status': 'ok', 'as_of': a['as_of'],
                         'observation_date': dates[i],
                         'publication_date': pub_iso,
                         'publication_rule': rule,
                         'value': values[i]}
                    if level_series:
                        yoy = _derive_yoy(dates, values, i)
                        v['derived_yoy_pct'] = yoy
                        v['value_kind'] = 'level(同比须用 derived_yoy_pct)'
                        if yoy is None:
                            base_ym = _shift_months(dates[i], 12)
                            v['yoy_status'] = 'no_same_period_base'
                            v['yoy_note'] = (
                                f'同比不可得: 缺{base_ym[:7]}基期观测'
                                f'(月度同比只配去年同月/季度只配去年同季,'
                                f'不以最近前值代基期)')
                            lv = _latest_valid_yoy(dates, values, i)
                            if lv:
                                v['latest_valid_yoy'] = lv
                        else:
                            v['yoy_status'] = 'ok'
                    row['anchors'][a['label']] = v
                cells.append(row)
    asset_universe = [k for k in ASSET_UNIVERSE
                      if k in (snap.get('series_store') or {})]
    return {'cells': cells, 'absent': absent,
            'asset_universe': asset_universe}


# ── 转折候选(确定性排序;判断归 Agent) ─────────────────────────────────

def _is_level_unit(unit):
    """水平序列判定(同比派生适用): 指数点/GDP 级——百分比/利率/PMI
    扩散指数原值即环境读数,不做同比。"""
    u = str(unit or '')
    return u.startswith('index_point') or u == 'billion_usd'


def _monthly_series_for_turning(dates, values, unit):
    """转折探测用月序列: 水平序列转**同比空间**(指数漂移≠转折,同比
    变化才是环境转折),其余原样月末最新。

    Audit-R19 任务1: 同比空间的基期=严格去年同月(ym−12 整月对齐),
    缺基期该月不出数——不以最近前值代基期(13 个月变化不是同比)。"""
    mon = _monthly_last(dates, values)
    if not _is_level_unit(unit):
        return mon
    by_ym = {ym: v for ym, _d, v in mon}
    out = []
    for ym, d, v in mon:
        tgt = _shift_months(ym + '-01', 12)[:7]
        base = by_ym.get(tgt)
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
    """过去 12 个月 增长+通胀+政策 三维序列最大 |3 月变化| 排序(候选面)。

    Audit-R19 任务3: 增长、通胀和政策都进入候选池(旧口径硬编码
    policy+inflation→增长转折零候选);每指标取其最大窗口一候选。
    只列引擎确定性算得出的事实(序列/前后值/日期);「谁先变/跟进/背离」
    的判断=Agent 席 reader_map.turnings(须引用此候选面或如实说明偏离)。
    候选窗端点月按发布纪律过滤(发布日>研究截止日的月不入窗)。"""
    cutoff = plan['cutoff']
    y0 = cutoff[:7]
    months_back = []
    for k in range(13):
        months_back.append(_shift_months(f'{y0}-01', k)[ :7])
    window = set(months_back)
    cands = []
    seen_mid = set()
    for eco, rface in plan['regions'].items():
        for dim in ('growth', 'inflation', 'policy'):
            for cell in rface['dimensions'].get(dim, []):
                mid = cell['metric_id']
                if mid in seen_mid:
                    continue
                seen_mid.add(mid)
                s, _err = _series(mid, snap, root)
                if not s or not s.get('dates'):
                    continue
                freq = s.get('frequency') or cell.get('frequency')
                pub_ok = set()
                for ym in window:
                    probe = None
                    for dd in s['dates']:
                        if dd[:7] == ym:
                            probe = dd
                    if probe is None:
                        continue
                    pd_iso, _r = _publish_date(mid, freq, probe)
                    if pd_iso is None or pd_iso <= cutoff:
                        pub_ok.add(ym)
                mon = [(ym, d, v) for ym, d, v in _monthly_series_for_turning(
                    s['dates'], s['values'], s.get('unit'))
                    if ym in pub_ok]
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
                                 'unit': ('同比%(派生于水平序列,严格同基期)'
                                          if _is_level_unit(s.get('unit'))
                                          else s.get('unit'))})
                    cands.append(best)
    cands.sort(key=lambda c: (-abs(c['delta']), c['metric_id']))
    return {'basis': '过去12个月(研究截止日)内 3 个月滚动变化绝对值最大者;'
                     '增长/通胀/政策三维全部进入候选池(每指标一候选,窗端点'
                     '已按发布纪律过滤);确定性计算,仅作候选——三个转折的'
                     '取舍与谁先变判断归 Agent 席 reader_map(三转折须为不同'
                     '事件,同一转折不得重复计数)',
            'candidates': cands[:max(top_n * 3, 9)], 'top_n_expected': top_n}


def ex_post_windows(anchor_ym, months=(3, 6, 12)):
    """历史类比/转折的事后窗基准月: 锚月+N 月(日历月平移)。

    Audit-R19 任务4: 锚 2022-06 时 3/6/12 个月须分别到 2022-09、2022-12、
    2023-06——本函数是唯一的窗口算术源(引擎/契约/渲染三面同源)。"""
    out = {}
    for m in months:
        out[f'{m}m'] = _shift_months(f'{anchor_ym}-01', -m)[:7]
    return out


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
                if yoy is not None:
                    vals.append(_fmt_val(v.get('value')) + f'(同比≈{yoy:g}%)')
                elif v.get('yoy_status') == 'no_same_period_base':
                    lv = v.get('latest_valid_yoy') or {}
                    extra = (f";最近有效同比≈{lv.get('yoy_pct'):g}%@"
                             f"{str(lv.get('observation_date'))[:7]}"
                             if lv.get('yoy_pct') is not None else '')
                    vals.append(_fmt_val(v.get('value'))
                                + f'(同比不可得: 缺基期{extra})')
                else:
                    vals.append(_fmt_val(v.get('value')))
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

    # 三个转折(按实际事件/发布日期排序;观测窗口单列)
    lines += ['## 过去一年的三个转折(按日期)', '']
    cand_by_key = {}
    cand = (rp.get('turning_candidates') or {}).get('candidates') or []
    for c in cand:
        cand_by_key[(c.get('metric_id'), str(c.get('to_ym')))] = c
    lines.append('| 日期 | 指标 | 前值→后值 | 观测窗口 | 谁先变 | 跟进/背离 |')
    lines.append('|---|---|---|---|---|---|')
    turn_rows = sorted(rm.get('turnings') or [],
                       key=lambda t: str(t.get('date') or ''))
    for t in turn_rows:
        mid, ym = t.get('metric_id'), str(t.get('date') or '')[:7]
        cc = cand_by_key.get((mid, ym))
        win = (f"{cc.get('from_ym')}..{cc.get('to_ym')}" if cc
               else (f"{str(t.get('before_date'))[:7]}..{ym}"
                     if t.get('before_date') else '—'))
        lines.append(f"| {t.get('date')} | {t.get('metric_id')} | "
                     f"{_fmt_val(t.get('value_before'))}→"
                     f"{_fmt_val(t.get('value_after'))} | {win} | "
                     f"{t.get('first_mover')} | {t.get('follow_or_diverge')} |")
    lines.append('')
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

    # 关键数字与来源(附发布日期——Audit-R19 任务1)
    lines += ['## 关键数字与来源(实际观测日+发布日期)', '']
    lines.append('| 指标 | 锚 | 值 | 单位 | 实际观测日 | 发布日期(推定规则) | 来源 |')
    lines.append('|---|---|---|---|---|---|---|')
    for c in rows:
        for a in anchors:
            v = (c.get('anchors') or {}).get(a) or {}
            if v.get('status') != 'ok':
                continue
            src = c.get('source')
            src_txt = src if isinstance(src, str) else (
                (src or {}).get('source') or (src or {}).get('file') or '—')
            pub = v.get('publication_date') or '—'
            rule = v.get('publication_rule')
            pub_txt = f"{pub}({rule})" if rule else pub
            lines.append(f"| {c.get('metric_id')} | {a} | "
                         f"{_fmt_val(v.get('value'))} | {c.get('unit')} | "
                         f"{v.get('observation_date')} | {pub_txt} | "
                         f"{src_txt} |")
    lines.append('')

    # 历史类比(匹配区间/判断截止月/事后窗三面分记——Audit-R19 任务4)
    lines += ['## 历史上结构最像的时期(可验证;≤3段)', '']
    for h in rm.get('history_periods') or []:
        tag = '(美国指标类比——锚定美国序列)' if h.get('us_analog') else ''
        lines.append(f"### {h.get('period_label')} {tag}")
        mw = h.get('match_window') or {}
        if mw.get('start_ym') and mw.get('end_ym'):
            lines.append(f"- 匹配区间: {mw.get('start_ym')}..{mw.get('end_ym')}"
                         f"(判断截止月 {h.get('judgment_cutoff_ym') or '—'};"
                         "匹配只用当时已发布数据)")
        lines.append(f"- 相似点: {h.get('similarity')}")
        lines.append(f"- 关键差异: {h.get('difference')}")
        lines.append(f"- 其他经济体是否同步: {h.get('other_regions_sync')}")
        ex = h.get('ex_post') or {}
        aym = str(h.get('anchor_ym') or '')
        exp_win = ex_post_windows(aym) if len(aym) == 7 else {}
        for k, lbl in (('3m', '随后3个月'), ('6m', '随后6个月'),
                       ('12m', '随后12个月')):
            exp_m = exp_win.get(k)
            exp_txt = f"(锚{aym}+{k[:-1]}月→{exp_m})" if exp_m else ''
            lines.append(f"- {lbl}{exp_txt}: {ex.get(k)}")
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
