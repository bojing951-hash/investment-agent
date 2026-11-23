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

import bisect
import json
import os
import re

import freshness_policy as _fp   # Audit-R25 任务1: 最新一期锚过期识别(已批准窗口)

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
        'policy': [('CN_POLICY_OVERNIGHT', '隔夜逆回购利率(操作目标口径——'
                                            '2026-11-02 换锚后的政策利率锚)'),
                   ('CN_OMO_7D', '7天逆回购利率(七天工具口径——换锚前为'
                                '操作目标,2026-11-02 起单列)'),
                   ('CN_LPR_1Y', 'LPR 1年期(报价基准,单列)')],
    },
    'EA': {
        # Audit-R20 任务1: 欧元区增长维补齐——EA_REAL_GDP_YOY(FRED
        # CLVMEURSCAB1GQEA19 严格同季同比,1995+)结束「增长维如实缺口」。
        'growth': [('EA_REAL_GDP_YOY', '实际GDP同比(季频,FRED最新修订值'
                                      '→事后回顾口径)')],
        'inflation': [('EA_HICP_YOY', 'HICP同比(月频)')],
        'policy': [('ECB_MRO', '欧央行主要再融资利率(政策目标口径)'),
                   ('ECB_DFR', '欧央行存款便利利率(操作下限口径)')],
    },
    'JP': {
        # Audit-R20 任务1: 日本增长维补齐(JP_REAL_GDP_YOY)+全国CPI列于
        # 东京口径之前(全国=官方主口径,东京=速报先行口径,10个月短窗如实)。
        'growth': [('JP_REAL_GDP_YOY', '实际GDP同比(季频,FRED最新修订值'
                                      '→事后回顾口径)')],
        'inflation': [('JP_CPI_YOY', '全国CPI同比(月频,官方主口径)'),
                      ('JP_CPI_TOKYO_YOY', '东京都CPI同比(月频,速报先行'
                                          '口径;2025基单档→2026-01起)')],
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

# ── Audit-R20 任务2: 政策利率四分面(政策目标/贷款报价/隔夜市场均值分列; ──
# 决定日/生效日/统计窗口结束日三日期分别展示)。值=声明式口径注记;
# 逐锚具体日期由 point_values 按观测日落位(决议日=观测日一类),此处
# 只声明口径,不造日期。
POLICY_FACE = {
    'DFEDTARU': {'face': '政策目标(宣布值)', 'market_seat_label': 'FOMC目标区间上限',
                 'decision': '决议日=生效日前一日(两日会议次日公布;序列值变更日'
                             '=生效日)——2026-09 决议 09-16、生效 09-17',
                 'effective': '生效日=观测日(目标区间自生效日起按新值执行;'
                             '2022-07 决议 07-27→生效 07-28,七月末上限 2.50)',
                 'decision_kind': 'prev_day',
                 'stat_window': None,
                 'market_pair': 'DFF',
                 'market_note': '市场观测=配对 DFF(有效联邦基金利率)同窗观测日'
                                '(生效日 DFF 同日跳变可核: 2026-09-17 '
                                '3.63→3.88)'},
    'DFEDTARL': {'face': '政策目标(宣布值)', 'market_seat_label': 'FOMC目标区间下限',
                 'decision': '决议日=生效日前一日(两日会议次日公布;序列值变更日'
                             '=生效日)——2026-09 决议 09-16、生效 09-17',
                 'effective': '生效日=观测日(目标区间自生效日起按新值执行)',
                 'decision_kind': 'prev_day',
                 'stat_window': None,
                 'market_pair': 'DFF',
                 'market_note': '市场观测=配对 DFF(有效联邦基金利率)同窗观测日'
                                '(生效日 DFF 同日跳变可核: 2026-09-17 '
                                '3.63→3.88)'},
    'DFF': {'face': '隔夜市场均值(有效利率)', 'market_seat_label': 'NY Fed有效联邦基金利率',
            'decision': None,   # 非决议值: 市场成交的有效利率
            'effective': '观测日=交易日次日发布',
            'stat_window': '日',
            'market_self': True,
            'market_note': '市场观测日=本序列观测日(自即市场均值口径;生效日'
                           '跳变与目标变更同日可核)'},
    'CN_POLICY_OVERNIGHT': {'face': '操作目标(隔夜·2026-11-02起新锚)',
                            'market_seat_label': '央行隔夜逆回购中标利率',
                            'decision': '决议日=公告日=观测日(交易日09:20披露)',
                            'effective': '生效日=操作日当日',
                            'decision_kind': 'obs_day',
                            'stat_window': None,
                            'market_note': '隔夜市场利率(DR001类)未入库,'
                                           '市场观测日如实缺席'},
    'CN_OMO_7D': {'face': '七天工具(操作利率)', 'market_seat_label': '央行7天逆回购中标利率',
                  'decision': '决议日=公告日=观测日(交易日09:20披露)',
                  'effective': '生效日=操作日当日',
                  'decision_kind': 'obs_day',
                  'stat_window': None,
                  'market_note': '七天工具口径单列(2026-11-02 换锚前为操作目标锚)'},
    'CN_LPR_1Y': {'face': '贷款报价(报价基准)', 'market_seat_label': 'LPR 1年期报价',
                  'decision': '公布日=观测日(每月20日09:00,节假日顺延'
                              '——Audit-R29 任务3: 官方发布时刻统一 09:00,'
                              '与 release_calendar time=09:00 同口径)',
                  'effective': '生效日=公布日',
                  'decision_kind': 'obs_day',
                  'stat_window': None,
                  'market_note': '报价基准与政策操作目标分列'},
    'ECB_MRO': {'face': '政策目标(宣布值)', 'market_seat_label': 'ECB主要再融资利率',
                'decision': '决议日=生效日前的上一个周四(管委会决议;序列值变更'
                            '日=生效日=决议后首个周三)——2026-09 决议 09-10、'
                            '生效 09-16',
                'effective': '生效日=观测日(ECB惯例: 变更自决议后首个周三生效)',
                'decision_kind': 'prev_thursday',
                'stat_window': None},
    'ECB_DFR': {'face': '政策目标(宣布值·操作下限)', 'market_seat_label': 'ECB存款便利利率',
                'decision': '决议日=生效日前的上一个周四(管委会决议;序列值变更'
                            '日=生效日=决议后首个周三)——2026-09 决议 09-10、'
                            '生效 09-16',
                'effective': '生效日=观测日(ECB惯例: 变更自决议后首个周三生效)',
                'decision_kind': 'prev_thursday',
                'stat_window': None},
    'JP_POLICY_RATE': {'face': '隔夜市场均值(月均)', 'market_seat_label': '无担保隔夜拆借月均',
                       'decision': None,   # 月均≠决议值: BOJ决议目标另列(JP_POLICY_TARGET)
                       'effective': None,
                       'stat_window': '月'},
    # Audit-R26 任务3: BoJ 宣布值口径四分面——决议日只认实录表(间隔无
    # 固定惯例),表外生效日如实「决议日不可推」;市场观测=JP_POLICY_RATE
    # 月均配对(月均=市场观测,只作市场面不作决议证据)。
    'JP_POLICY_TARGET': {'face': '政策目标(宣布值)', 'market_seat_label': 'BOJ政策目标利率',
                         'decision': '决议日=实录表回溯(BOJ_DECISION_HISTORY;'
                                     '2024-03 决议 03-19、生效 03-21)',
                         'effective': '生效日=序列值变更日(宣布值自生效日起适用)',
                         'decision_kind': 'boj_history',
                         'stat_window': None,
                         'market_pair': 'JP_POLICY_RATE',
                         'market_note': '市场观测=配对 JP_POLICY_RATE 月均'
                                        '(月均≠宣布值——只作市场观测,'
                                        '不以月均跳变冒充决议事件)'},
}

# ── Audit-R22 任务2: 政策文件面(叙事源)的发布事实 ─────────────────────────
# 会议纪要=滞后发布的叙事源: 决议事实以决议日公布为准,不以纪要回填;
# 纪要自其发布日起才可作为引用来源(发布前一日不可见)。
POLICY_DOC_FACTS = [
    {'doc_id': 'FOMC-MINUTES-2026-10',
     'kind': 'minutes',
     'title': 'FOMC 2026年10月会议纪要',
     'meeting_month': '2026-10',
     'published_on': '2026-11-18',
     'basis': 'user_directive',
     'note': '10月会议纪要 2026-11-18 发布(纪要发布≠决议日;引用纪要叙事'
             '自 11-18 起可见,决议数值仍以决议日公布为准)',
     'source': 'Audit-R22 验收指令(2026-11-19)'},
]


def policy_doc_visible(doc_id, as_of):
    """政策文件(纪要类)在 as_of 日是否已发布可引: published_on≤as_of。"""
    for d in POLICY_DOC_FACTS:
        if d['doc_id'] == doc_id:
            return bool(as_of and d['published_on'] <= as_of)
    return None   # 未登记文件: 无事实面,如实 None(调用方按无据处理)


# ── Audit-R22 任务2: 同一事件的跨国信号合并 ───────────────────────────────
# 政策变动事件(决议日+幅度)按决议日跨地区聚簇(±CLUSTER_DAYS 日内=同一
# 全球政策事件);簇内逐国分记决议/生效日,月频证据只能说明同步时如实
# 写「先后未定」(同步性主张上限=月频证据分辨率)。
_POLICY_CLUSTER_DAYS = 7


def policy_event_clusters(events):
    """events=[{region, metric_id, date(决议日), delta_bp,...}] → 簇列表。

    每簇={'cluster_id','date_from','date_to','regions':[...],
    'events':[...],'note'}——同簇=同一全球政策事件的多国信号(合并计数,
    三个转折中算一个事件);note 固定携带月频先后未定纪律。"""
    evs = sorted((dict(e) for e in events if e.get('date')),
                 key=lambda e: (e['date'], e.get('region') or '',
                                e.get('metric_id') or ''))
    seen = set()
    dedup = []
    for e in evs:
        key = (e.get('region'), e['date'], e.get('delta_bp'))
        if key in seen:
            continue
        seen.add(key)
        dedup.append(e)
    evs = dedup
    clusters = []
    for e in evs:
        if not clusters:
            clusters.append({'events': [e]})
        else:
            last_to = max(x['date'] for x in clusters[-1]['events'])
            if e['date'] > _dshift(last_to, _POLICY_CLUSTER_DAYS):
                clusters.append({'events': [e]})
            else:
                clusters[-1]['events'].append(e)
    out = []
    for i, c in enumerate(clusters):
        ds = [e['date'] for e in c['events']]
        regions = sorted({e.get('region') or '?' for e in c['events']})
        multi = len(regions) > 1
        out.append({
            'cluster_id': f'POLCLUSTER-{i + 1:02d}',
            'date_from': min(ds), 'date_to': max(ds), 'regions': regions,
            'events': c['events'],
            'same_event_cross_country': multi,
            'note': ('跨国决议日落在±%d日窗内——按同一全球政策事件合并计数'
                     '(逐国决议/生效日分记);月频证据只能说明同步时,先后'
                     '未定' % _POLICY_CLUSTER_DAYS) if multi else
                    '单地区事件(不跨国产合并)',
        })
    return out


def _dshift(iso, days):
    import datetime
    return (datetime.date.fromisoformat(iso)
            + datetime.timedelta(days=days)).isoformat()


def _dnum(iso):
    """ISO 日期→YYYYMMDD 整数(间隔天数用;部分日期按前缀保守取)。"""
    s = str(iso)
    return int(s[:4] + s[5:7] + s[8:10])


def _is_wednesday(iso):
    import datetime
    return datetime.date.fromisoformat(iso).weekday() == 2


def _last_value_change(dates, values, i):
    """≤dates[i] 的最近值变更日(相邻有效观测值不同;全序列扫描)。

    None=起点以来无变更(决议/生效不可推,如实缺席)。日频目标序列的
    观测日多为不变更的打印日——生效日锚在变更日,不在打印日。"""
    for k in range(i, 0, -1):
        a, b = values[k - 1], values[k]
        if a is not None and b is not None and a != b:
            return dates[k]
    return None


def policy_clusters_from_plan(plan):
    """从 point_values 政策行的一年窗路径事件建跨国事件簇(编排层调用)。

    事件键=决议日(decision_date;无决议语义的行如实跳过)——「同一事件」
    按决议日聚,ECB 2026-09-10 与 Fed 2026-09-16 决议落在 ±7 日窗内
    → 同一全球政策事件(合并计数)。逐事件带 effective_date(=序列值
    变更日)供四日期分记。"""
    evs = []
    for c in (plan.get('point_values') or {}).get('cells') or []:
        wp = c.get('policy_window_path') or {}
        for e in wp.get('events') or []:
            if not e.get('decision_date'):
                continue
            evs.append({'region': c.get('region'),
                        'metric_id': c.get('metric_id'),
                        'display_name': c.get('display_name'),
                        'date': e['decision_date'],
                        'effective_date': e.get('date'),
                        'delta_bp': e.get('delta_bp'),
                        'from': e.get('from'), 'to': e.get('to')})
    clusters = policy_event_clusters(evs)
    for cl in clusters:
        for e in cl['events']:
            e['decision_to_effective_days'] = (
                (_dnum(e['effective_date']) - _dnum(e['date']))
                if e.get('effective_date') else None)
    return {'basis': ('同一事件的跨国信号合并: 各政策行一年窗路径事件按'
                      '决议日跨地区聚簇(±%d 日)——同簇=同一全球政策事件,'
                      '三个转折中计一个事件;逐国决议日/生效日分记'
                      '(决议→生效惯例: Fed=次日,ECB=决议后首个周三,'
                      'PBOC=宣布即时)。月频证据只能说明同步时,先后未定。'
                      % _POLICY_CLUSTER_DAYS),
            'clusters': clusters}


# ── Audit-R22 任务4: 历史类比逐窗并列面(经济指标×资产表现) ────────────────
# 每段历史类比(anchor_ym)×随后 3/6/12 月窗: 确定性并列「经济指标与资产
# 表现」,逐行附起止期/数值/单位/来源——与 ex_post 正文同一锚月末→
# 锚+N 月末口径,正文数字可逐位对账。
_HIST_ECON = [('DFEDTARU', 'Fed 目标区间上限', 'rate'),
              ('UNEMPLOYMENT', '美国失业率', 'rate'),
              ('CPI', '美国 CPI(指数)', 'price'),
              ('INDPRO', '美国工业生产(指数)', 'price')]
_HIST_ASSET = [('SPX', '标普500', 'price'), ('UST_10Y', '美债十年期', 'rate'),
               ('DXY', '美元指数', 'price'), ('GOLD_F', '黄金期货', 'price'),
               ('NIKKEI225', '日经225', 'price')]


def _month_end_obs(dates, values, ym):
    """≤ym 月末的最新有效观测(与 judgment_contract._month_last_obs 同口径)。"""
    import bisect
    hi = bisect.bisect_right(dates, ym + '-31')
    j = hi - 1
    while j >= 0 and values[j] is None:
        j -= 1
    return (dates[j], values[j]) if j >= 0 else (None, None)


def _hist_series(mid, rj, snap, root):
    """Audit-R23 任务1: 历史并列面序列解析——冻结源优先。

    冻结源=report.json 的 S4_history_<mid> 信封序列(运行时已定,随
    report 交付);运行快照仅兜底(信封缺席的序列)。由此读者面数字与
    快照在场性/被改无关: 同名快照端点被改不影响任何行;无外部快照仍
    逐位还原。snap=None 且无冻结=如实缺席(不读活数据树冒充运行面)。
    返回 (series|None, basis|None)。"""
    if rj is not None:
        frz = _series_from_report(rj, mid)
        if frz and frz.get('dates'):
            return frz, '冻结源(report.json S4_history 信封)'
    if snap is None:
        return None, None
    s, _err = _series(mid, snap, root)
    return s, ('运行快照' if s and s.get('dates') else None)


# ── Audit-R28 任务3: 历史段地区×维度同步面(同步/分化/缺证) ───────────────
# 每段历史类比按判断截止核对美/中/欧/日,逐地区×维度给同步性标签——
# 确定性面(冻结信封序列+发布纪律),判断叙述(other_regions_sync)引用
# 本面可核。口径=与美国**同维度**方向对照(美国类比标签保留——锚定
# 美国序列的 analog 排序不变,本面是其跨国同步性的证据补齐)。
_HIST_REGION_DIMS = [
    ('US', 'growth', 'US_REAL_GDP', '实际GDP', 'level_yoy'),
    ('US', 'inflation', 'CPI', 'CPI', 'level_yoy'),
    ('US', 'policy', 'DFEDTARU', '目标利率上限', 'level'),
    ('CN', 'growth', 'CN_PMI_MFG', '制造业PMI', 'level'),
    ('CN', 'inflation', 'CN_CPI_YOY', 'CPI同比', 'direct'),
    ('CN', 'policy', 'CN_LPR_1Y', 'LPR(1年)', 'level'),
    ('EA', 'growth', 'EA_REAL_GDP_YOY', 'GDP同比', 'direct'),
    ('EA', 'inflation', 'EA_HICP_YOY', 'HICP同比', 'direct'),
    ('EA', 'policy', 'ECB_MRO', 'MRO利率', 'level'),
    ('JP', 'growth', 'JP_REAL_GDP_YOY', 'GDP同比', 'direct'),
    ('JP', 'inflation', 'JP_CPI_YOY', 'CPI同比', 'direct'),
    ('JP', 'policy', 'JP_POLICY_RATE', '隔夜利率(月均)', 'level'),
]
_HIST_DIM_LABEL = {'growth': '增长', 'inflation': '通胀', 'policy': '货币政策'}


def _hist_region_reading(s, ym, cutoff_end, mid, kind, freq, root=None):
    """≤ym 的**当时可知**读数 → (value, obs_date, pub)|None+原因。

    当时可知=观测月的可见日(_aof_first_pub)≤截止月末;level_yoy=
    水平序列取同比(基期观测同样须已可见);direct/level=原值即读数。
    root 在场→日历实录查询绑该树(Audit-R31 任务2 重放口径)。"""
    months = sorted({d[:7] for d, v in zip(s.get('dates') or [],
                                           s.get('values') or [])
                     if v is not None})[::-1]
    def _vis_obs(m):
        od, ov = _aof_obs_at_month(s, m)
        if od is None:
            return None
        vf, _pub, _b, _n = _aof_first_pub(mid, od, freq, root=root)
        if vf and vf <= cutoff_end:
            return od, ov, vf
        return None
    cur = next((r for m in months if m <= ym for r in [_vis_obs(m)] if r),
               None)
    if cur is None:
        return None, 'no_visible_obs'
    if kind != 'level_yoy':
        return (cur[1], cur[0], cur[2]), None
    # 同月配对基期: 基期月自**实际观测月**回推 12 月(非请求月——
    # 截止月观测常晚于截止公布,实际取到前一月观测,基期须跟观测走)。
    # Audit-R32 任务2: 基期=去年**同月**(季频=同季——季戳+12 月落同季),
    # 与主引擎 m12 同口径(fact_engine Audit-R31 任务3: 13 个月前≠同比);
    # 原实现 m <= base_m 会取到 13 个月前及更早的观测冒充基期。同月
    # 无观测=缺基期即缺证,不以更早观测替代。
    base_m = _shift_months(cur[0][:7] + '-01', 12)[:7]
    base = _vis_obs(base_m)
    if base is None or not base[1] or cur[1] is None:
        # 原因码保持 R30 既档字面(旧档重渲逐字节不变);基期月不入文案。
        return None, 'no_visible_base'
    return (round((cur[1] / base[1] - 1.0) * 100.0, 4),
            cur[0], cur[2]), None


def history_region_sync_face(history_periods, rj, root=None):
    """每段历史类比的地区×维度同步性面(确定性;冻结信封序列)。

    逐段(锚=anchor_ym,判断截止月=judgment_cutoff_ym): 美中欧日×
    增长/通胀/货币政策,两端读数=锚−3月与截止月各自≤该月的最新当时
    可知观测(发布纪律: 可见日≤**各自端点**该月末——Audit-R30 任务2
    起锚−3月端按自己的截止取数,不共用判断截止吃发布面后视;公布日
    随行)。标签:
    同步=与美国同维度方向一致(双持平亦同);分化=方向相反或一端持平
    一端变动;缺证=序列缺席/无可见观测/同比基期不可见——逐项点名缺
    哪条,不以相邻维度冒充。月频分辨率界限同引擎既档: 两端读数仅给
    方向对照,不判先后。"""
    periods = []
    for h in history_periods or []:
        cym = str(h.get('judgment_cutoff_ym') or h.get('anchor_ym') or '')
        aym = str(h.get('anchor_ym') or '')
        if len(cym) != 7:
            continue
        cutoff_end = _aof_month_end(cym)
        prior_m = _shift_months(cym + '-01', 3)[:7]
        # Audit-R30 任务2: 锚−3月端按**自己的**可知截止(该月末)取数
        # ——原实现两端共用判断截止月末,早端吃进 3 个月发布面后视
        # (锚−3月观测常于次月上旬发布,判断截止已可见≠当时可知;
        # as_of 泄漏拦截纪律对两端各自生效)。截止端口径不变。
        prior_end = _aof_month_end(prior_m)
        rows = []
        for eco, dim, mid, label, kind in _HIST_REGION_DIMS:
            s = _series_from_report(rj, mid) if rj is not None else None
            row = {'region': eco, 'dimension': dim, 'metric_id': mid,
                   'label': label,
                   'dimension_label': _HIST_DIM_LABEL.get(dim, dim)}
            if not s or not s.get('dates'):
                row.update(label_sync='缺证',
                           reason='序列不在场(冻结信封无该序列)')
                rows.append(row)
                continue
            freq = s.get('frequency') or 'monthly'
            r1, why1 = _hist_region_reading(s, cym, cutoff_end, mid, kind,
                                            freq, root=root)
            r0, why0 = _hist_region_reading(s, prior_m, prior_end, mid,
                                            kind, freq, root=root)
            row['vintage_note'] = _aof_revision_note(mid)
            if r1 is None or r0 is None:
                row.update(
                    label_sync='缺证',
                    reason=('截止端无可见观测' if r1 is None
                            else f'锚−3月端无可见观测')
                    + (f'({why1})' if r1 is None and why1 else
                       f'({why0})' if why0 else ''))
                rows.append(row)
                continue
            row.update(
                prior_value=r0[0], prior_obs=r0[1], prior_pub=r0[2],
                cutoff_value=r1[0], cutoff_obs=r1[1], cutoff_pub=r1[2])
            rows.append(row)
        # 方向与标签(美国=同维基准;两端读数齐备才判)
        by_key = {(r['region'], r['dimension']): r for r in rows}
        for (eco, dim, mid, label, kind) in _HIST_REGION_DIMS:
            r = by_key.get((eco, dim))
            if r.get('label_sync') == '缺证':
                continue
            def _dir(rr):
                dv = (rr.get('cutoff_value') - rr.get('prior_value'))
                if dv == 0:
                    return '持平'
                return '上行' if dv > 0 else '下行'
            r['direction'] = _dir(r)
            r['delta'] = round(r['cutoff_value'] - r['prior_value'], 4)
            if eco == 'US':
                r['label_sync'] = '基准(美国类比锚)'
                continue
            us = by_key.get(('US', dim)) or {}
            if us.get('label_sync') == '缺证' or not us.get('direction'):
                r['label_sync'] = '缺证'
                r['reason'] = '美国同维基准缺证——无对照方向'
                continue
            if r['direction'] == us['direction']:
                r['label_sync'] = ('同步' if r['direction'] != '持平'
                                   else '同步(双持平)')
            else:
                r['label_sync'] = '分化'
                r['reason'] = (f"美国{us['direction']}vs该地区"
                               f"{r['direction']}")
        periods.append({'anchor_ym': aym, 'cutoff_ym': cym,
                        'rows': rows})
    return {'periods': periods,
            'basis': ('历史段地区×维度同步面: 逐段按判断截止核对美中欧日,'
                      '两端读数=锚−3月与截止月各自的最新当时可知观测'
                      '(可见日≤截止月末,公布日随行);标签=与美国同维度'
                      '方向对照(同步=方向一致,分化=相反或一端持平,'
                      '缺证=序列缺席/无可见观测/基期不可见,逐项点名)。'
                      '美国类比标签保留(analog 锚定美国序列),本面补齐'
                      '跨国同步性证据;月频分辨率只给方向对照不判先后'
                      '(Audit-R28 任务3)')}


def history_window_face(history_periods, snap, root, rj=None):
    """每段历史类比×{3,6,12}月窗的经济×资产并列面(确定性,渲染层调用)。

    history_periods=[{anchor_ym,...}](Agent 席选定,取 anchor_ym 即可)。
    行=指标|起期|起值|止期|止值|变化|单位|来源;rate 族变化=pp,
    price 族变化=%。序列缺席如实入 absent,不以别指标冒充。
    Audit-R23 任务1: rj 在场时冻结源优先(_hist_series)——正确快照/
    无外部快照/同名快照被改三种情况渲染逐字节一致。任务4: 窗口两端
    取到同一条观测(锚后无新观测)时不再整行缺席,入行并注记缺少两期
    数据(变化不可算,不冒充)。"""
    periods = []
    for h in history_periods or []:
        aym = str(h.get('anchor_ym') or '')
        if len(aym) != 7:
            continue
        pd_out = {'anchor_ym': aym, 'windows': {}, 'absent': [],
                  'series_basis': []}
        for horizon in (3, 6, 12):
            # 随后 N 个月(锚+N 月末;_shift_months 正 n=向过去平移,
            # 故取负=向未来)——与 ex_post 正文「随后N个月」同向
            tgt = _shift_months(aym + '-01', -horizon)[:7]
            rows = []
            for mid, label, kind in _HIST_ECON + _HIST_ASSET:
                grp = ('经济指标' if (mid, label, kind) in _HIST_ECON
                       else '资产表现')
                s, s_basis = _hist_series(mid, rj, snap, root)
                if s_basis and (aym, mid, s_basis) not in \
                        pd_out['series_basis']:
                    pd_out['series_basis'].append((aym, mid, s_basis))
                if not s or not s.get('dates'):
                    pd_out['absent'].append(f"{mid}({label})")
                    continue
                d0, v0 = _month_end_obs(s['dates'], s['values'], aym)
                d1, v1 = _month_end_obs(s['dates'], s['values'], tgt)
                if v0 is None or v1 is None:
                    pd_out['absent'].append(f"{mid}({label})@{aym}→{tgt}")
                    continue
                note = None
                if d0 == d1:
                    # 任务4: 两端同一条观测=该窗内无新观测,行保留并注记
                    note = ('窗口两端取到同一条观测'
                            f'({d0}),缺少两期数据——变化不可算')
                try:
                    chg = ((round(v1 - v0, 4) if kind == 'rate'
                            else round((v1 / v0 - 1.0) * 100.0, 4))
                           if isinstance(v0, (int, float))
                           and isinstance(v1, (int, float))
                           and d0 != d1 else None)
                except (TypeError, ZeroDivisionError):
                    chg = None
                rows.append({'group': grp, 'metric_id': mid, 'label': label,
                             'kind': kind,
                             'from_date': d0, 'from_value': v0,
                             'to_date': d1, 'to_value': v1,
                             'change': chg,
                             'change_unit': ('pp' if kind == 'rate' else '%'),
                             'unit': s.get('unit'),
                             'source': s.get('source'),
                             'note': note})
            pd_out['windows'][f'{horizon}m'] = {
                'window_months': horizon, 'target_ym': tgt, 'rows': rows}
        periods.append(pd_out)
    return {'basis': ('历史类比逐窗并列面: 锚月末→锚+N 月末(与 ex_post '
                      '正文同口径);经济指标与资产表现并列,逐行起止期/'
                      '数值/单位/来源,确定性复算零生成;序列源=冻结信封'
                      '优先/运行快照兜底(Audit-R23 任务1)'),
            'periods': periods}


# ── Audit-R23 任务2: 历史类比「当时可知」发布纪律面 ──────────────────
# 指令: 修历史信息截止——逐段按判断截止月重算跨国同步性叙述所引数字:
# 每个关键数字绑定 指标/观测期/值/首次公布日/来源/修订口径;晚于截止日
# 才公布的观测移入事后段,不得充当「当时可知」。发布日=日历实录优先
# (release_calendar.visible_publish_date: 停摆延误/经证实条目),规则
# 推定兜底(_publish_date);EA_HICP 两级发布分记(快报=观测月末(推定)
# 当时可知,终值=次月中旬)。序列源=冻结信封优先(与任务1同口径)。
_AOF_KEY_METRICS = [
    ('CPI', '美国 CPI(指数水平)', ['美国CPI', '美国 CPI']),
    ('CORE_PCE', '美国核心PCE(指数水平)', ['核心PCE']),
    ('INDPRO', '美国工业生产(指数)', ['工业生产', 'INDPRO']),
    ('UNEMPLOYMENT', '美国失业率', ['失业率']),
    ('US_REAL_GDP', '美国实际GDP', ['实际GDP', 'GDP']),
    ('CN_PPI_YOY', '中国PPI同比', ['中国PPI', '中国 PPI']),
    ('CN_CPI_YOY', '中国CPI同比', ['中国CPI', '中国 CPI']),
    ('EA_HICP_YOY', '欧元区HICP同比', ['HICP']),
    ('JP_CPI_YOY', '日本CPI同比', ['日本CPI', '日本 CPI']),
]
_AOF_GDP_FAMILY = {'US_REAL_GDP', 'EA_REAL_GDP_YOY', 'JP_REAL_GDP_YOY'}
_EA_FLASH_METRICS = {'EA_HICP_YOY'}
# Audit-R24 任务2: 事后政策事件面——政策目标利率族(阶梯型,日频但稀疏
# 变更;决议日即观测日的口径随格披露)。隔夜/操作利率(高频波动)不入
# 此面——变更行会淹没事件信号。
# Audit-R26 任务3: 日本隔夜拆借**月均**(JP_POLICY_RATE)移出本面——月均
# 是市场观测不是决议值,月均跳变≠决议事件(2024-03 月均跨决议月漂移曾
# 被当「决议即日」事件入档);政策事件面只收宣布值口径序列。
_AOF_POLICY_METRICS = [
    ('DFEDTARU', '美联储目标区间上限'),
    ('DFEDTARL', '美联储目标区间下限'),
    ('ECB_MRO', '欧央行主要再融资利率'),
    ('ECB_DFR', '欧央行存款便利利率'),
    ('JP_POLICY_TARGET', '日本央行政策目标利率(宣布值口径)'),
    ('CN_LPR_1Y', '中国LPR(1年)'),
]

# Audit-R26 任务3: 日本央行决议/生效实录表(宣布值口径的决议日回溯源)。
# BoJ 决议-生效间隔无固定惯例(2024-03 为决议 03-19、生效 03-21;后续
# 加息间隔各异),不得以回推公式造日期——只认逐条实录;生效日不在表内
# =决议日不可推,如实注记不虚构。新决议经官方公告核验后追加。
BOJ_DECISION_HISTORY = [
    # (生效日, 决议日, 事件注记)
    ('2024-03-21', '2024-03-19',
     '结束负利率: 无担保隔夜拆借目标 0.10(2016-01 负利率—2024-03 '
     '0.10 区间上限;决议 03-19[两日会议次日公布]、生效 03-21——'
     '基准=用户验收指令实录(Audit-R26 任务3回归锚)'),
]


def _boj_decision_of(effective_iso):
    """生效日→(决议日,注记)|None(不在实录表=不可推,不虚构)。"""
    for eff, dec, note in BOJ_DECISION_HISTORY:
        if eff == effective_iso:
            return dec, note
    return None


def _aof_month_end(ym):
    import calendar
    return '%04d-%02d-%02d' % (int(ym[:4]), int(ym[5:7]),
                               calendar.monthrange(int(ym[:4]),
                                                   int(ym[5:7]))[1])


def _aof_first_pub(mid, obs_date, frequency, root=None):
    """→ (visible_from, first_publish, basis, note)。

    visible_from=最早可知日(快报在则取快报);first_publish=本表所用
    发布日(终值/日历实录优先);basis 随格披露。
    Audit-R24 任务2: EA 快报日=日历实录优先(逐期官方实录——快报非
    「月末」恒等式: 2021-05/2022-06 两观测月快报实为次月 1 日),
    无条目回落月末推定并随格披露。
    Audit-R31 任务2 补: root 在场→日历实录查询绑该树 config 日历
    (重放=包内 overlay 日历,不再漏读引擎本地日历;无 root 原语义=
    钉死或引擎默认)。"""
    import release_calendar as rc
    _p = (os.path.join(root, 'config', 'release_calendar.json')
          if root else None)
    rule_pub, rule_txt = _publish_date(mid, frequency, obs_date)
    # 日历实录查询用月首口径(R21/R22 既定调用约定: 条目 obs 窗按
    # <YYYY-MM>-01 匹配;序列观测日多为月末,直传会跳过 user_directive
    # 实录条目而误落 REST-CONSERVATIVE 保守界——九月失业率实录
    # 2025-11-20 须优先于保守界 2026-01-22)。
    pub, basis = rc.visible_publish_date(mid, obs_date[:7] + '-01',
                                         rule_pub, path=_p)
    if mid in _EA_FLASH_METRICS:
        ent = rc.first_publish(mid, obs_date[:7] + '-01', path=_p)
        if ent is not None and ent.get('first_publish'):
            # 逐期实录: 快报日+终值日都来自官方新闻稿编号实录。
            flash = ent['first_publish']
            final = rc.final_publish(mid, obs_date[:7] + '-01', path=_p)
            basis = f"calendar:{ent['entry_id']}({ent['basis']})"
            if final:
                return flash, final, basis, (
                    '快报 %s 当时可知(官方实录);终值 %s(官方实录)'
                    % (flash, final))
            return flash, pub or flash, basis, ''
        flash = _aof_month_end(obs_date[:7])
        if pub is None and flash is None:
            return None, None, basis or 'unavailable', rule_txt or ''
        if flash and (pub is None or flash < pub):
            return flash, pub, 'rule:推定(快报月末)', (
                '快报 %s 当时可知(推定);终值 %s(%s)' % (
                    flash, pub or '—', basis))
    if pub is None:
        return None, None, basis or 'unavailable', rule_txt or ''
    return pub, pub, basis, ''


def _aof_publish_instant(mid, obs_date, root=None):
    """Audit-R28 任务2: 官方发布时刻('HH:MM')|None——日历条目 time 字段
    (官方实录,如中国 LPR 每月20日 09:00)。仅读者面显示;可见性比较
    仍用日期字段(时刻不改变可见性判定口径;推定条目无时刻如实缺席)。"""
    import release_calendar as rc
    _p = (os.path.join(root, 'config', 'release_calendar.json')
          if root else None)
    return rc.publish_instant(mid, obs_date[:7] + '-01', path=_p)


def _aof_revision_note(mid):
    if mid in _AOF_GDP_FAMILY:
        return '事后回顾族(最新修订值,非当时首发值——注册声明)'
    if mid in _EA_FLASH_METRICS:
        return '终值(最新修订);当时快报值可能略异,快报日见注记'
    return '最新修订值(采集口径;首发值可能略异,修订不可回溯)'


def _aof_obs_at_month(series, ym):
    """该月最新非 None 观测 → (obs_date, value) | (None, None)。"""
    d, v = series.get('dates') or [], series.get('values') or []
    best = (None, None)
    for i in range(len(d)):
        if d[i][:7] == ym and v[i] is not None:
            if best[0] is None or d[i] >= best[0]:
                best = (d[i], v[i])
    return best


def history_asof_face(history_periods, rj, root=None):
    """每段历史类比的「当时可知/事后才公布」发布纪律面(确定性)。

    known=截止月末前已可知的最新观测(每数字五字段绑定);aftermath=
    截止月观测晚于截止公布者+截止后 12 月窗内异常延误/采集缺口行。
    序列缺席如实入 absent。零生成零网络,纯文件面。
    Audit-R31 任务2 补: root 在场→日历实录查询绑该树(重放读包内
    overlay 日历,不漏读引擎本地——与任务2「重放统一读冻结输入」
    同口径)。"""
    periods = []
    for h in history_periods or []:
        aym = str(h.get('anchor_ym') or '')
        cym = str(h.get('judgment_cutoff_ym') or aym)
        if len(cym) != 7:
            continue
        cutoff_end = _aof_month_end(cym)
        pd_out = {'anchor_ym': aym, 'cutoff_ym': cym,
                  'cutoff_end': cutoff_end, 'known': [], 'aftermath': [],
                  'absent': []}
        for mid, label, _aliases in _AOF_KEY_METRICS:
            s = _series_from_report(rj, mid) if rj is not None else None
            if not s or not s.get('dates'):
                pd_out['absent'].append(f"{mid}({label})")
                continue
            freq = s.get('frequency') or 'monthly'
            # ── 当时可知: 可见日 ≤ 截止月末的最新观测 ──
            months = sorted({d[:7] for d, v in
                             zip(s['dates'], s['values'])
                             if v is not None and d[:7] <= cym})
            known_row = None
            cutoff_month_row = None
            for ym in months[-4:]:          # 最近 4 个月足够定可见值
                od, ov = _aof_obs_at_month(s, ym)
                if od is None:
                    continue
                vf, pub, basis, note = _aof_first_pub(mid, od, freq,
                                                      root=root)
                row = {'metric_id': mid, 'label': label, 'obs_month': ym,
                       'obs_date': od, 'value': ov,
                       'visible_from': vf, 'first_publish': pub,
                       'publish_instant': _aof_publish_instant(mid, od,
                                                              root=root),
                       'pub_basis': basis, 'source': s.get('source'),
                       'revision_note': _aof_revision_note(mid),
                       'note': note}
                if ym == cym:
                    cutoff_month_row = row
                if vf and vf <= cutoff_end:
                    known_row = row        # 保序推进=最新可见
            if known_row:
                known_row = dict(known_row)
                known_row['visible_at_cutoff'] = True
                pd_out['known'].append(known_row)
            else:
                pd_out['absent'].append(f"{mid}({label})@{cym}(截至截止月"
                                        '无可知观测)')
            # ── 事后段①: 截止月观测晚于截止公布(常见: 中 PPI/日 CPI
            #    次月发布——正文引截止月值即信息截止泄漏,须移事后) ──
            if cutoff_month_row and (
                    (cutoff_month_row.get('visible_from') or '9999') >
                    cutoff_end):
                row = dict(cutoff_month_row)
                row['delay_note'] = (
                    '观测月=截止月,首发 %s 晚于截止 %s——当时不可知,'
                    '移入事后段' % (row.get('visible_from'), cutoff_end))
                pd_out['aftermath'].append(row)
            # ── 事后段②: 截止后 12 月窗内 异常延误(首发日晚于常轨
            #    推定>45天)/采集缺口(应观测月 None)/缺口后恢复发布。
            #    季频指标只走季度观测月(1/4/7/10)——非季月不是缺口;
            #    超出序列末月的未来月未到≠缺口(Audit-R24 任务2 守卫)。 ──
            _is_q = (freq == 'quarterly')
            _last_ym = max((d[:7] for d, v in
                            zip(s['dates'], s['values'])
                            if v is not None), default=None)
            prev_hole = False
            for i in range(1, 13):
                ym = _shift_months(cym + '-01', -i)[:7]
                if _last_ym and ym > _last_ym:
                    break
                if _is_q and int(ym[5:7]) not in (1, 4, 7, 10):
                    prev_hole = False
                    continue
                od, ov = _aof_obs_at_month(s, ym)
                if od is None:
                    pd_out['aftermath'].append({
                        'metric_id': mid, 'label': label, 'obs_month': ym,
                        'obs_date': None, 'value': None,
                        'visible_from': None, 'first_publish': None,
                        'pub_basis': '观测缺席', 'source': s.get('source'),
                        'revision_note': _aof_revision_note(mid),
                        'note': '',
                        'delay_note': '采集缺口(源端无该月观测——停摆期'
                                      '未采集/未发布),如实缺席'})
                    prev_hole = True
                    continue
                vf, pub, basis, note = _aof_first_pub(mid, od, freq,
                                                      root=root)
                late = None
                try:
                    import datetime as _dt
                    normal_pub, _rt = _publish_date(mid, freq, od)
                    beyond = (_dt.date.fromisoformat(pub or vf or od)
                              - _dt.date.fromisoformat(normal_pub)).days
                    if beyond > 45:
                        late = ('发布延误: 首发 %s 晚于常轨推定 %s %d 天'
                                '(>45 容差)——停摆期延误类'
                                % (pub or vf, normal_pub, beyond))
                except (TypeError, ValueError):
                    late = None
                if late or prev_hole:
                    pd_out['aftermath'].append({
                        'metric_id': mid, 'label': label, 'obs_month': ym,
                        'obs_date': od, 'value': ov,
                        'visible_from': vf, 'first_publish': pub,
                        'publish_instant': _aof_publish_instant(mid, od,
                                                               root=root),
                        'pub_basis': basis, 'source': s.get('source'),
                        'revision_note': _aof_revision_note(mid),
                        'note': note,
                        'delay_note': late or (
                            '缺口后恢复发布(前一观测月缺席)')})
                prev_hole = False
        # ── 事后段③(Audit-R24 任务2): 事后政策事件——截止后 12 月窗内
        #    政策目标利率的档位变动(如锚 2016-10 的 2016-12 美联储加息)
        #    属截止后决议,非当时可知,确定性入事后段(决议日≠生效日时
        #    观测日=生效/变更日,如 Fed 次日生效惯例)。 ──
        for pmid, plabel in _AOF_POLICY_METRICS:
            ps = _series_from_report(rj, pmid) if rj is not None else None
            if not ps or not ps.get('dates'):
                continue
            win_end = _shift_months(cym + '-01', -12)
            prev_v = None
            for di, vi in zip(ps['dates'], ps['values']):
                if vi is None:
                    continue
                if prev_v is not None and vi != prev_v and \
                        cutoff_end < di <= win_end:
                    # Audit-R26 任务3: 决议/生效分记入事后政策事件——
                    # POLICY_FACE 决议机制在场则解析决议日(Fed/ECB 惯例
                    # 回推、BoJ 实录表),决议日≠生效日两日分记;无机制
                    # (报价类)按公布日记。观测日=生效/变更日。
                    _pf3 = POLICY_FACE.get(pmid) or {}
                    _pdd3 = _policy_dates(
                        _pf3, di, value_change_date=di) if _pf3 else None
                    _dec3 = (_pdd3 or {}).get('decision')
                    _eff3 = (_pdd3 or {}).get('effective') or di
                    _pb3 = ('决议%s/生效%s(决议≠生效分记)'
                            % (_dec3 or '不可推', _eff3)
                            if _pdd3 else '决议即日(政策目标口径)')
                    pd_out['aftermath'].append({
                        'metric_id': pmid, 'label': plabel,
                        'kind': 'policy_event', 'obs_month': di[:7],
                        'obs_date': di, 'value': vi,
                        'value_from': prev_v,
                        'decision_date': _dec3,
                        'effective_date': _eff3,
                        'visible_from': None, 'first_publish': None,
                        'pub_basis': _pb3,
                        'source': ps.get('source'),
                        'revision_note': '',
                        'note': '',
                        'delay_note': ('事后政策事件: %s→%s(观测日=%s%s,'
                                       '截止 %s 后决议——非当时可知)'
                                       % (prev_v, vi, di,
                                          (f',决议{_dec3}、生效{_eff3}'
                                           if _dec3 and _dec3 != _eff3
                                           else ''),
                                           cutoff_end))})
                prev_v = vi
        periods.append(pd_out)
    return {'basis': ('当时可知面(发布纪律重算): 判断截止月末前已可知的'
                      '最新观测,逐数字绑定 指标/观测期/值/首次公布日/'
                      '来源/修订口径;晚于截止日公布者移入事后段。发布日='
                      '日历实录优先(逐期官方实录: EA 快报/终值、停摆改期)'
                      '/规则推定兜底;EA_HICP 快报与终值两级分记;事后段含'
                      '截止后政策事件(决议非当时可知)。确定性复算零生成'
                      '(Audit-R23 任务2+Audit-R24 任务2)'),
            'periods': periods}


# ── Audit-R20 任务2: 只有最新修订值时标「事后回顾」──────────────────
# 判定基准=注册表 release_semantics 声明(revision_semantics=
# latest_vintage_asof_collected 一族: FRED 全量拉取的 GDP/估值等)。
# 未声明者不标(CPI 等极少修订口径的注册表未声明→如实不标,不扩大)。
def _vintage_semantics(reg_entry):
    rs = (reg_entry or {}).get('release_semantics') or ''
    if 'latest_vintage' in rs:
        return '事后回顾(最新修订值,非当时首发值)'
    return 'as_collected(采集时点值)'

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
    'CN_LPR_1Y':      ('monthly', -11, 'LPR 每月20日09:00公布(观测日=发布日;月末−11天,节假日顺延;Audit-R29 官方时刻)'),
    'CN_OMO_7D':      ('daily', 0, '央行操作室交易日09:20披露交易公告(当日可见)'),
    'CN_POLICY_OVERNIGHT': ('daily', 0, '央行操作室交易日09:20披露交易公告(当日可见;2026-11-02换锚后隔夜行)'),
    'EA_HICP_YOY':    ('monthly', 16, 'Eurostat HICP 终值次月中旬发布(月末+16天,推定)'),
    # Audit-R20 任务1: 四地新增指标的发布节奏(推定规则,随格披露)
    'EA_REAL_GDP_YOY': ('quarterly', 35, 'Eurostat GDP flash 季末+35天(推定;FRED最新修订值→事后回顾)'),
    'JP_CPI_YOY':     ('monthly', 20, '总务省全国CPI次月中旬发布(月末+20天,推定)'),
    # Audit-R32 真跑实中②: 基线「次月下旬(月末+25天)」比官方实录晚约一个月,
    # 且晚于全国口径(+20天)——与「东京速报领先全国」相反,已发布读数被判
    # 锚前不可见、随格披露的公布日期错约一个月。总务省结果页实录: 東京都
    # 区部 2026年10月分(中旬速報値)〔2026年10月30日公表〕、2026年6月分
    # 〔2026年6月26日公表〕→ 速报值当月末发布;取两者中较晚的「月末−1天」
    # 为推定(不早于实录=保守)。
    'JP_CPI_TOKYO_YOY': ('monthly', -1, '总务省东京CPI中旬速报值当月末发布'
                         '(月末−1天,推定;官方实录锚 2026年10月分=2026-10-30、'
                         '6月分=2026-06-26)'),
    'JP_REAL_GDP_YOY': ('quarterly', 45, '内閣府GDP速报季末+45天(推定;FRED最新修订值→事后回顾)'),
    'JP_POLICY_RATE': ('monthly', 5, 'BOJ 月均次月初公布(月末+5天,推定)'),
    'DFF':            ('daily', 1, 'NY Fed 有效联邦基金利率次日发布(+1天,推定)'),
    'DFEDTARU':       ('daily', 0, 'FOMC 目标区间决议日当日公布'),
    'DFEDTARL':       ('daily', 0, 'FOMC 目标区间决议日当日公布'),
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
                   ('货币政策', 'policy'),
                   # Audit-R30 任务3: 裸「政策」词形——「增长、通胀和政策
                   # 哪里分化」并列点名三维,原只识「货币政策」四字形→
                   # 该问句政策维整列漏检(12 组只成 8 组)。「政策」含于
                   # 「货币政策」→两词形同值 policy,无重复维。
                   ('政策', 'policy')]
# Audit-R29 任务2: 隐含比较维度——问宏观环境/分化「体现在哪些维度」而不点
# 名任何维度词形时,按声明式全维族(增长+通胀+货币政策)展开: 环境问句
# 的「维度」语义=三族对照(与地图注册表同族),不虚构新维;证据不足的
# 维度由缺口面逐项如实标注(问句本就要求)。仅当句段含经济体且无任何
# 显式维度词形时触发(有显式词形=用户已点名,不扩)。
_IMPLICIT_DIM_CUE_RE = re.compile(
    r'宏观环境|宏观基本面|(?:明显)?分化|哪些维度|什么维度')
_IMPLICIT_DIM_ALL = ['growth', 'inflation', 'policy']


def implicit_dimension_expansion(seg):
    """句段隐含维度展开: 命中环境/分化线索且无显式维度→全维族;
    否则空表(调用方口径零变化)。确定性词形,零语义翻译。"""
    if _IMPLICIT_DIM_CUE_RE.search(seg or ''):
        if not any(w in (seg or '') for w, _d in DIMENSION_WORDS):
            return list(_IMPLICIT_DIM_ALL)
    return []
# Audit-R27 任务1: 政策维子问词形——「日本央行政策利率处于什么水平」
# 一类子问不含「货币政策」四字;句段(。？！；切分)内命中任一触发词
# 即该句段判 policy 维(句段作用域,不摊到无该子问的句段/地区)。
_POLICY_DIM_EXTRA = ('政策利率', '央行', '加息', '降息', '降准', 'LPR',
                     '逆回购', '利率水平')

# Audit-R19 任务3: 传导图须从冲击连到指标与资产——引擎侧资产指标全集
# (在场性按快照 series_store 判定,plan 的 asset_universe 只列在场者)。
ASSET_UNIVERSE = ['UST_2Y', 'UST_5Y', 'UST_10Y', 'UST_30Y', 'TIPS_5Y',
                  'TIPS_10Y', 'BEI_5Y', 'BEI_10Y', 'CURVE_2S10S', 'SPX',
                  'NDX', 'RUT', 'DAX', 'CAC40', 'NIKKEI225', 'HSI', 'SHCOMP',
                  'DXY', 'EURUSD', 'USDJPY', 'USDCNY', 'GOLD_F', 'SILVER_F',
                  'BRENT_F', 'HY_OAS', 'IG_OAS', 'BB_OAS', 'B_OAS',
                  'CCC_OAS', 'VIX']
# Audit-R29 任务2: 「宏观基本面」与「宏观环境」同族(隐含全维族线索
# 见 _IMPLICIT_DIM_CUE_RE),形状词相应补「基本面」——否则同族问句
# 检测与计划两套口径(隐含展开吃到、形判漏检)。
MAP_SHAPE_WORDS = ('地图', '转折', '传导', '结构最像', '环境', '基本面',
                   # Audit-R30 任务3: 「哪里分化」的分化词形——R29 隐含
                   # 维度线索已认 (?:明显)?分化,形判词面漏同族(检测与
                   # 计划两套口径之续修);OPEN2=环境/NEW2=基本面词形
                   # 不受影响。
                   '分化')
_DIM_LABEL = {'growth': '增长', 'inflation': '通胀', 'policy': '货币政策'}
_REGION_LABEL = {'US': '美国', 'CN': '中国', 'EA': '欧元区', 'JP': '日本'}

# 点锚词形: 最新一期/最新/当前 | N个月前 | 一年前(=12个月前)
# Audit-R27 任务1: 显式年月(YYYY年M月)与比较结构(相比/对比…)——
# 「2026年11月,…相比3个月前各有什么变化」的当期端点由两者落位。
_POINT_LATEST_RE = re.compile(r'最新(?:一期|数据)?|当前')
_POINT_MONTHS_RE = re.compile(
    r'(?P<num>[0-9]+|[一二两三四五六七八九十]+)\s*个?\s*月\s*前')
_POINT_YEARS_RE = re.compile(r'(?P<num>[0-9]+|[一二两三四五六七八九十]+)\s*年\s*前')
_POINT_EXPLICIT_YM_RE = re.compile(
    r'(?P<y>[0-9]{4})\s*年\s*(?P<m>[0-9]{1,2})\s*月')
_POINT_COMPARE_RE = re.compile(r'相比|对比|相较|较之|比起')
# Audit-R30 任务3: 问句时间窗词形「过去/近/最近 N 个月」——窗语义(范围
# 两端=窗起+当期),非「N个月前」点语义;原零解析→网格锚空、所问
# 时间窗在地图面被丢弃。与 _question_window 的 relative_months 同
# 词形(数据需求窗同源);此处落窗起锚+当期锚+question_window 披露。
_POINT_WINDOW_RE = re.compile(
    r'(?:过去|近|最近)\s*(?P<num>[0-9]+|[一二两三四五六七八九十]+)\s*个?\s*月')
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
    任一形状词。不满足=完全走既有口径(零回归)。

    Audit-R29 任务2: 维度词形含隐含展开——「宏观环境/分化…哪些维度」
    型问句无显式维度词形时按全维族判(与 _clause_region_dimension_
    requests 同一展开,检测与计划不两套口径);经济体侧由 orchestrator
    简称枚举守卫先行补齐(ent.economies)。"""
    q = question or ''
    ecos = [e for e in (ent.get('economies') or [])
            if e in REGION_DIMENSION_METRICS]
    dims = {d for w, d in DIMENSION_WORDS if w in q}
    if not dims:
        dims = set(implicit_dimension_expansion(q))
    return len(ecos) >= 2 and len(dims) >= 2 and any(w in q for w in MAP_SHAPE_WORDS)


def parse_question_windows(question, cutoff_iso):
    """问句时间窗(Audit-R30 任务3): 「过去/近/最近 N 个月」→窗列表。

    每窗 {'months': N, 'from': 研究截止日−N月, 'to': 研究截止日,
    'source': 原词形}。窗语义=范围(两端=窗起+当期),与点锚(「N个
    月前」)、事后偏移(「随后N个月」)分记三类;调用方(plan_map)
    落 question_window 披露+窗起入点锚对照,数据需求窗由
    _question_window 同词形解析(relative_months,单一扫描器口径
    不变)。数量守卫与点锚一致(1..120;中文数量经 _cn_num)。"""
    q = question or ''
    wins = []
    for m in _POINT_WINDOW_RE.finditer(q):
        n = _cn_num(m.group('num'))
        if n and 1 <= n <= 120:
            wins.append({'months': n,
                         'from': _shift_months(cutoff_iso, n),
                         'to': cutoff_iso,
                         'source': m.group(0)})
    return wins


def parse_point_anchors(question, cutoff_iso):
    """对照时点(日历点锚)。返回按 months_before 降序(12月前→3月前→最新)。

    「N个月前」= 研究截止日−N 月的日历点——与「事件发生后N个月」(事后
    偏移,事件日+N 月)分记两类,见 parse_ex_post_offsets。

    Audit-R27 任务1: 显式年月与比较结构落位——
    - 「YYYY年M月」= 显式期锚: =研究截止月→**当期锚**(label 统一
      「最新一期」,键 months_before=0,附 explicit_period 供披露);
      早于截止月 1..120 月→历史点锚(label=原年月);晚于截止=未来
      不取(不虚构未来时点);
    - 比较结构(「…相比N个月前各有什么变化」)隐含当期端点: 存在
      N个月前锚且问句含相比/对比一类词而「最新一期/当前」词形缺席
      时补当期锚——对照表恒有当期列与所请求的历史列并列(同一时点
      多指标不替代另一时点)。
    Audit-R30 任务3: 时间窗词形(「过去/近/最近 N 个月」)落位——窗起
    (=截止日−N月)入点锚对照(带 window_start 标记),窗端=当期锚
    (问句问窗内分化→当期状态即窗端读数);窗自身随 plan 的
    question_window 披露。"""
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
    _cy, _cm = int(cutoff_iso[:4]), int(cutoff_iso[5:7])
    _explicit_cur = False
    _explicit_hist = []
    _seen_ym = set()
    for m in _POINT_EXPLICIT_YM_RE.finditer(q):
        y, mo = int(m.group('y')), int(m.group('m'))
        if not (1 <= mo <= 12):
            continue
        n = (_cy * 12 + _cm) - (y * 12 + mo)
        if n == 0:
            _explicit_cur = True
        elif 1 <= n <= 120 and (y, mo) not in _seen_ym:
            _seen_ym.add((y, mo))
            _explicit_hist.append(
                {'kind': 'point', 'label': f'{y}年{mo}月',
                 'as_of': _shift_months(cutoff_iso, n),
                 'months_before': n, 'explicit_period': f'{y:04d}-{mo:02d}'})
    _wins = parse_question_windows(q, cutoff_iso)
    _win_months = {w['months'] for w in _wins}
    months |= _win_months    # 窗起=截止日−N月,入点锚对照
    anchors = [{'kind': 'point', 'label': f'{n}个月前',
                'as_of': _shift_months(cutoff_iso, n), 'months_before': n}
               for n in sorted(months, reverse=True)]
    anchors += sorted(_explicit_hist, key=lambda a: -a['months_before'])
    for a in anchors:        # 窗起标记(点锚恰=窗起时同一锚兼两职,如实)
        if a.get('months_before') in _win_months and a['kind'] == 'point':
            a.setdefault(
                'window_start',
                '问句时间窗窗起(%s)' % next(
                    w['source'] for w in _wins
                    if w['months'] == a['months_before']))
    _wants_current = (_POINT_LATEST_RE.search(q) or _explicit_cur
                      or (months and _POINT_COMPARE_RE.search(q))
                      or bool(_wins))
    if _wants_current and not any(a['months_before'] == 0
                                  for a in anchors):
        _cur = {'kind': 'point', 'label': '最新一期',
                'as_of': cutoff_iso, 'months_before': 0}
        if _explicit_cur:
            _cur['explicit_period'] = f'{_cy:04d}-{_cm:02d}'
        anchors.append(_cur)
    anchors.sort(key=lambda a: -a['months_before'])
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


def _clause_region_dimension_requests(question, ecos):
    """Audit-R27 任务1: 句段作用域的 地区×维度 请求集合。

    问句按 。？！?！;；\n 切段,段内命中的地区(区名词形)×段内命中的
    维度(增长/通胀/货币政策+政策子问词形)才入计划——「日本央行政策
    利率」子问只请求 JP×policy,不以全域全维网格摊大检索面;同一时点
    多指标不替代另一时点,另一时点/另一维的指标也不替代本子问。
    全部句段都无地区或无维度(词形分置两段一类)→回退全域全维笛卡尔
    (与旧口径一致,零回归)。返回 [(region, dimension), ...] 保序。"""
    segs = re.split(r'[。？！?！;；\n]', _norm_q(question or ''))
    out = []
    import workbench_data as _wd
    for seg in segs:
        if not seg.strip():
            continue
        seg_ecos = [e for e in ecos
                    if _REGION_LABEL.get(e) and _REGION_LABEL[e] in seg]
        # Audit-R29 任务2: 句段内简称枚举(与 orchestrator 同一守卫助手;
        # 「美、欧、中、日四地」句段不再漏检地区)
        for code in _wd.economy_abbrev_hits(seg):
            if code in ecos and code not in seg_ecos:
                seg_ecos.append(code)
        seg_dims = []
        for w, d in DIMENSION_WORDS:
            if w in seg and d not in seg_dims:
                seg_dims.append(d)
        if 'policy' not in seg_dims and any(
                w in seg for w in _POLICY_DIM_EXTRA):
            seg_dims.append('policy')
        if not seg_dims and seg_ecos:
            # Audit-R29 任务2: 隐含比较维度展开(环境/分化型问句→全维族;
            # 与 detect_map_question 同一展开函数,检测/计划共源)
            for d in implicit_dimension_expansion(seg):
                if d not in seg_dims:
                    seg_dims.append(d)
        for eco in seg_ecos:
            for dim in seg_dims:
                if (eco, dim) not in out:
                    out.append((eco, dim))
    return out


def plan_map(question, ent, reg_by_id, cutoff_iso):
    """共享研究计划本体: 地区×维度指标+在场性/缺口、点锚、事后窗。

    Audit-R27 任务1: 地区×维度网格改句段作用域请求(_clause_region_
    dimension_requests)——问句实际请求的组才入计划(他组不摊检索面,
    也不因他组数据在而掩盖本组缺口);词形分置无法成段请求时回退
    全域全维(旧口径)。"""
    ecos = [e for e in (ent.get('economies') or [])
            if e in REGION_DIMENSION_METRICS]
    # Audit-R30 任务3: 裸「政策」与「货币政策」同值 policy——保序去重,
    # 词形并列命中不产生重复维(下游 regions/dimensions/网格按维消费)。
    dims = []
    for _w, _d in DIMENSION_WORDS:
        if _w in (question or '') and _d not in dims:
            dims.append(_d)
    if 'policy' not in dims and any(
            w in (question or '') for w in _POLICY_DIM_EXTRA):
        dims.append('policy')
    _requests = _clause_region_dimension_requests(question, ecos)
    if not _requests:
        _requests = [(e, d) for e in ecos for d in dims]
    # Audit-R29 任务2: 隐含展开是否实际触发(句段含经济体+环境/分化线索+
    # 零显式维度)——dimension_source 披露用,与句段请求同一判据
    _implicit_fired = False
    if not dims:
        import workbench_data as _wd
        for seg in re.split(r'[。？！?！;；\n]', _norm_q(question or '')):
            if not seg.strip() or implicit_dimension_expansion(seg) != _IMPLICIT_DIM_ALL:
                continue
            if (any(_REGION_LABEL.get(e) and _REGION_LABEL[e] in seg
                    for e in ecos)
                    or any(c in ecos
                           for c in _wd.economy_abbrev_hits(seg))):
                _implicit_fired = True
                break
    regions, metrics, gaps = {}, [], []
    for eco in ecos:
        regions[eco] = {'label': _REGION_LABEL[eco], 'dimensions': {}}
    for eco, dim in _requests:
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
                          'unit': m.get('unit'),
                          # R20 任务2: 序列修订口径(事后回顾标记的
                          # 判定基准=注册表声明,见 _vintage_semantics)
                          'vintage_semantics': _vintage_semantics(m),
                          # R20 任务2: 政策四分面口径注记(目标/报价/
                          # 市场均值+决定日/生效日/统计窗口三日期声明)
                          'policy_face': POLICY_FACE.get(mid)})
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
        # Audit-R25 任务3: 原问逐字入计划——plan/工单/报告/归档同一份原文
        # (后续任何摘写只在 question_summary,不回写本键);MAP 头与
        # ARCHIVE_MANIFEST 同源引用,验收=逐字节比对 run.question。
        'question_verbatim': question,
        'question_summary': (
            '内部摘要(非原文): 地区%s×维度%s@%s,三时点对照+转折+传导+'
            '历史类比;仅供检索/日志,交付与验收以 question_verbatim 为准'
            % ('/'.join(sorted(regions)),
               '、'.join(sorted({d for _e, d in _requests}) or dims),
               cutoff_iso)),
        # Audit-R29 任务2: 维度来源披露——显式词形 / 隐含全维族展开 /
        # 句段零命中回退全域全维,三态随计划落档(读者可核网格为何如此)。
        'dimension_source': (
            'implicit_macro_environment(问句无显式维度词形,按环境/分化'
            '线索展开全维族 增长+通胀+货币政策;证据不足维度由缺口面'
            '逐项标注)' if _implicit_fired else
            ('explicit_words' if _requests else 'fallback_full_grid')),
        # Audit-R23 任务2: 新代码面标记——历史段「当时可知」发布纪律契约
        # (as_of 泄漏拦截)自本标记起生效;旧档无标记不追溯(原文复放必须
        # 通过),新运行计划必带。
        'asof_discipline': 'r23',
        # Audit-R24 任务4: 新代码面标记——并项补选「交还判断席」契约
        # (turning_supplement 逐项: 谁先变/何时/从多少到多少/跟进或背离,
        # 分辨率界限与跨国证据缺口如实注记)自本标记起生效;旧档无标记
        # 不追溯(原文复放必须通过)。
        'turning_supplement_discipline': 'r24',
        # Audit-R25 任务3: 新代码面标记——首页/转折表/传导链先后顺序与
        # 因果证据一致性契约(日期次序主张自洽+跨面不矛盾/传导链区分
        # 指标引擎绑定/转折表指标同源)自本标记起生效;旧档无标记不追溯。
        'cross_face_consistency': 'r25',
        'shared_by': '取数(plan 指标并入 S4/数据需求面)/报告(MAP_REPORT '
                     '对照表与数值回贴)/验收(同一份 plan 判据)——不手填指标代码',
        'regions': regions,
        'dimensions': dims,
        'metrics': metrics,
        'context_metrics': [m for m in US_RATES_TRIO],
        'point_anchors': parse_point_anchors(question, cutoff_iso),
        # Audit-R30 任务3: 问句时间窗(「过去/近/最近 N 个月」)随计划
        # 落档——窗起入点锚对照(window_start 标记)+窗端=当期锚;
        # 数据需求窗由 _question_window 同词形解析(relative_months,
        # 单一扫描器口径),两面对同一窗。无窗词形=None(零回归)。
        'question_window': (
            {'windows': parse_question_windows(question, cutoff_iso)}
            if parse_question_windows(question, cutoff_iso) else None),
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


def _visible_publish(mid, freq, obs_date):
    """Audit-R20 任务2: 发布日统一入口——日历条目(停摆/延误实录)优先,
    RELEASE_RULES 推定兜底。返回 (publish_date|None, basis_text);
    basis 保留具体规则文本(随格披露,读者可核)。
    Audit-R22 任务1: 条目挂批(batch_id)时 basis 带批号——同批指标的
    可见性整批一致(CPI+核心CPI 同稿/一次补发两月),读者可按批核。
    Audit-R25 任务2: 月/季频观测日统一月首口径查日历(与 _aof_first_pub
    同一约定, R21/R22 既定调用约定在发布纪律面全量贯通)——条目 obs 窗
    按 <YYYY-MM>-01 匹配;序列观测日多为月末,直传会跳过实录条目而误落
    推定兜底(欧元区 2025-03 HICP 月末观测 → 须命中速报 2025-04-01
    实录,而非月末推定)。日/周频不归一(逐日实录窗按原观测日匹配)。"""
    import release_calendar as rc
    _cal_obs = (obs_date[:7] + '-01'
                if freq in ('monthly', 'quarterly') and obs_date
                else obs_date)
    rule_iso, rule_text = _publish_date(mid, freq, obs_date)
    ent = rc.first_publish(mid, _cal_obs)
    if ent is not None:
        batch = f";batch={ent['batch_id']}" if ent.get('batch_id') else ''
        return (ent['first_publish'],
                f"calendar:{ent['entry_id']}({ent['basis']}{batch})")
    if rule_iso:
        return rule_iso, (rule_text or 'rule:推定')
    return None, 'unavailable'


def _policy_dates(face, obs_date, market_date=None, value_change_date=None,
                  metric_id=None, as_of=None, calendar_path=None):
    """政策四分面的四日期落位(R21 任务2: 决议日/生效日/市场观测日/
    统计窗口终点分列)。声明式口径(决议日=观测日一类)按观测日落具体
    日期;统计窗口=月→观测月末、日→观测日;市场观测日=配对市场序列
    (market_pair)锚窗内最新观测日,由 point_values 传入(序列面在场才
    落位)。None=该面无此日期(市场均值无决议日),如实缺席。

    Audit-R22 任务2: 决议/生效分记须以**值变更日**为生效日——观测日只是
    序列最新打印,未必是变更日(最新锚的日频打印几乎从不是)。调用方传
    value_change_date=全序列内 ≤obs_date 的最近值变更日;决议日按
    decision_kind 自生效日回推(Fed=前一交易日、ECB=上一周四)。

    Audit-R28 任务2: 官方记录优先——metric_id+as_of 在场时先查
    policy_decision_state(日历 kind=policy_decision/policy_maintenance
    条目): 记录在场则决议/生效/官方目标/最近维持/距上次调整(按生效日)
    逐项落位并带溯源,惯例回推仅当无记录;记录缺席走既有口径不变。"""
    if not face:
        return None
    out = {'face': face.get('face'), 'market_seat_label': face.get('market_seat_label'),
           'decision_note': face.get('decision'), 'effective_note': face.get('effective'),
           'market_note': face.get('market_note'),
           'decision': obs_date if face.get('decision') else None,
           'effective': obs_date if face.get('effective') else None}
    if metric_id and as_of:
        try:
            import freshness_policy as _fp_r28
            _st = _fp_r28.policy_decision_state(
                metric_id, as_of, calendar_path=calendar_path)
        except Exception:
            _st = None
        if _st and _st.get('present'):
            out.update(
                decision=_st.get('last_decision'),
                effective=_st.get('last_effective'),
                official_target=_st.get('official_target'),
                # Audit-R30 任务2: 已公告待生效决议随面——as_of 早于
                # 生效日时当前面=旧目标(或无已生效决议在档),新目标
                # 落 pending_adjustments 待生效(09-24 切换)。
                pending_adjustments=_st.get('pending_adjustments'),
                pending_target=_st.get('pending_target'),
                pending_effective_on=_st.get('pending_effective_on'),
                official_basis='calendar:%s(%s)' % (
                    (_st.get('records') or [{}])[0].get('entry_id'),
                    (_st.get('records') or [{}])[0].get('basis')),
                last_maintenance=_st.get('last_maintenance'),
                confirmed_through=_st.get('last_confirmed_on'),
                days_since_adjustment=_st.get('days_since_adjustment'),
                days_since_decision=_st.get('days_since_decision'),
                days_since_maintenance=_st.get('days_since_maintenance'),
                decision_note=(str(face.get('decision') or '')
                               + ';官方记录(Audit-R28 任务2): 距上次调整'
                                 '按**生效日**计算(目标水平自生效日起'
                                 '实际执行;决议日为公告面,两日分记)'))
            return out
    # Audit-R22 任务2: 决议/生效分记(数据面语义=序列值变更日为生效日)。
    # Fed 目标: 决议=生效前一日(两日会议次日公布);ECB: 决议=生效前
    # 上一个周四(变更自决议后首个周三生效,变更日恒为周三)。
    dk = face.get('decision_kind')
    if dk == 'boj_history':
        # Audit-R26 任务3: BoJ 决议/生效分记——生效日=序列值变更日(与
        # Fed/ECB 同「数据面语义」),决议日**只认实录表**(间隔无固定
        # 惯例,回推会造日期);表内无该生效日=决议日不可推,如实注记。
        eff = value_change_date or (
            obs_date if _boj_decision_of(obs_date) else None)
        if eff is None:
            out['decision'] = None
            out['effective'] = None
            out['decision_note'] = (str(face.get('decision') or '')
                                    + ';当前值自序列在场期无变更实录'
                                      '——决议/生效日不可推,不虚构')
        else:
            out['effective'] = eff
            _rec = _boj_decision_of(eff)
            if _rec:
                out['decision'] = _rec[0]
                out['decision_note'] = (str(face.get('decision') or '')
                                        + f';实录: 决议{_rec[0]}、生效'
                                          f'{eff}')
                if _rec[1]:
                    out['decision_note'] += f'({_rec[1]})'
            else:
                out['decision'] = None
                out['decision_note'] = (str(face.get('decision') or '')
                                        + f';生效{eff}不在决议实录表'
                                          '(BOJ_DECISION_HISTORY)——决议日'
                                          '不可推,如实缺席')
    elif dk in ('prev_day', 'prev_thursday'):
        eff = value_change_date or (
            obs_date if dk == 'prev_thursday'
            and _is_wednesday(obs_date) else None)
        if dk == 'prev_thursday' and eff and not _is_wednesday(eff):
            out['decision_note'] = (str(face.get('decision') or '')
                                    + ';⚠️ 变更日非周三=不规则生效日,'
                                      '决议日不可推,按观测日记')
            eff = None
        if eff is None:
            # 序列自起点无值变更(或变更日不规则): 决议/生效不可推
            out['decision'] = None
            out['effective'] = None
            out['decision_note'] = (str(face.get('decision') or '')
                                    + ';当前值自序列在场期无变更实录'
                                      '(或观测日非变更日且无可回溯变更)'
                                      '——决议/生效日不可推,不虚构')
        elif dk == 'prev_day':
            out['decision'] = _dshift(eff, -1)
            out['effective'] = eff
            if eff != obs_date:
                out['decision_note'] = (str(face.get('decision') or '')
                                        + f';当前值由该决议设定——观测日'
                                          f'{obs_date}为序列打印日非变更日')
        else:
            out['decision'] = _dshift(eff, -6)
            out['effective'] = eff
            if eff != obs_date:
                out['decision_note'] = (str(face.get('decision') or '')
                                        + f';当前值由该决议设定——观测日'
                                          f'{obs_date}为序列打印日非变更日')
    if face.get('market_self'):
        out['market_observation'] = obs_date
    elif market_date:
        out['market_observation'] = market_date
    else:
        out['market_observation'] = None
    sw = face.get('stat_window')
    if sw == '月':
        import calendar
        y, m = int(obs_date[:4]), int(obs_date[5:7])
        out['stat_window_end'] = '%04d-%02d-%02d' % (
            y, m, calendar.monthrange(y, m)[1])
    elif sw == '日':
        out['stat_window_end'] = obs_date
    else:
        out['stat_window_end'] = None
    return out


def _policy_window_path(dates, values, cutoff, months=12, metric_id=None):
    """政策序列一年窗路径(R21 任务2;R22 任务2 决议/生效分记): 窗=
    [截止−12个月,截止]内的变动点(窗内相邻观测值不同)逐点实录(日期/
    前后值/bp+决议日)与净变动——「先降 25bp 再升 25bp 净变动为零」
    一类事实须整窗可复算,禁以窗首尾两点差冒充路径(先降后升净零时
    首尾差恰掩盖全部路径)。无变动→events=[]+net_bp=0;窗内无观测→
    None(不编造)。事件 date=序列值变更日(=生效日),decision_date=
    按 POLICY_FACE[metric_id].decision_kind 推(观测日=生效日语义)。"""
    w0 = _shift_months(cutoff, months)
    idx = [k for k, d in enumerate(dates) if w0 <= d <= cutoff]
    if not idx:
        return None
    dk = (POLICY_FACE.get(metric_id) or {}).get('decision_kind')
    events = []
    # 变动点按其自身观测日(=生效日)归属窗口: 窗内首观测的前值允许在
    # 窗启之前(隔月决议序列的现实形态)——否则窗启后首场降息会被漏记,
    # 先降后升的路径从第一格就失真。dates 升序+窗口为日期区间→idx 为
    # 连续索引段,k1-1 要么同在窗内、要么恰在窗启前一格。
    for k1 in idx:
        k0 = k1 - 1
        if k0 < 0:
            continue   # 序列首观测无前值,其自身变动无从定起
        v0, v1 = values[k0], values[k1]
        if v0 is None or v1 is None or v0 == v1:
            continue
        dbp = round((v1 - v0) * 100)
        if dbp == 0:
            continue   # 月均舍入噪声(值差<0.5bp)不是变动点
        ev = {'date': dates[k1], 'from': v0, 'to': v1, 'delta_bp': dbp}
        if dk == 'prev_day':
            ev['decision_date'] = _dshift(dates[k1], -1)
        elif dk == 'prev_thursday':
            import datetime as _dt
            if _dt.date.fromisoformat(dates[k1]).weekday() == 2:
                ev['decision_date'] = _dshift(dates[k1], -6)
        events.append(ev)
    start_v, end_v = values[idx[0]], values[idx[-1]]
    return {'window': [w0, cutoff], 'events': events,
            'window_start_value': start_v, 'window_end_value': end_v,
            'net_bp': round((end_v - start_v) * 100),
            'note': ('窗=[研究截止−12个月,研究截止](_shift_months 正参='
                     '回看,与 ex_post_windows 反向同源);events=窗内观测'
                     '对其前值的变动点(date=序列值变更日=生效日,'
                     'decision_date=决议日;前值可在窗启前一格);net_bp='
                     '窗首尾观测差(bp)。政策路径月频证据只能支持同步时,'
                     '先后未定须在正文如实写明;决议日/生效日/市场观测日/'
                     '统计窗口终点分列见 policy_dates。')}


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
                       'source': s.get('source'), 'anchors': {},
                       'vintage_semantics': cell.get('vintage_semantics'),
                       'policy_face': cell.get('policy_face')}
                if cell.get('policy_face'):
                    wp = _policy_window_path(dates, values, plan['cutoff'],
                                             metric_id=mid)
                    if wp:
                        row['policy_window_path'] = wp
                for a in plan['point_anchors']:
                    # 发布纪律(R20 任务2: 日历实录条目优先,规则推定兜底):
                    # 只取「观测日≤锚日且发布日≤锚日」的最新观测
                    i = None
                    blocked_by = None
                    for k in range(len(dates) - 1, -1, -1):
                        if dates[k] > a['as_of']:
                            continue
                        pub_iso, basis = _visible_publish(mid, freq, dates[k])
                        if pub_iso is None or pub_iso <= a['as_of']:
                            i = k
                            break
                        if basis.startswith('calendar:'):
                            blocked_by = (dates[k], pub_iso, basis)
                    if i is None:
                        no_pub = {
                            'status': 'no_published_observation_on_or_before_'
                                      'anchor',
                            'as_of': a['as_of'],
                            'note': '锚日前无「已发布」观测(发布日=日历实录'
                                    '条目优先+推定规则兜底)'}
                        if blocked_by:
                            # R20 任务2: 停摆/延误实录——锚前最近观测被
                            # 日历条目判不可见,如实披露是哪条延误
                            no_pub['calendar_blocked_observation'] = blocked_by[0]
                            no_pub['calendar_first_publish'] = blocked_by[1]
                            no_pub['publication_basis'] = blocked_by[2]
                            no_pub['note'] += (f';最近观测{blocked_by[0]}被'
                                               f'{blocked_by[2]}判锚前不可见'
                                               f'(最早可见{blocked_by[1]})')
                        row['anchors'][a['label']] = no_pub
                        continue
                    pub_iso, basis = _visible_publish(mid, freq, dates[i])
                    v = {'status': 'ok', 'as_of': a['as_of'],
                         'observation_date': dates[i],
                         'publication_date': pub_iso,
                         'publication_rule': basis,
                         'publication_basis': basis,
                         'vintage': cell.get('vintage_semantics'),
                         'value': values[i]}
                    # Audit-R26 任务2: 三日期分记——统计期末(月/季频自观测
                    # 日按期首约定推到期末;发布日期=publication_date 在场;
                    # 政策最后确认日=decision_dated 序列的观测日,下方面
                    # 另记)。期末入锚供读者区分「期初约定的观测日」与
                    # 「统计期结束」。
                    _pe = _fp._period_end_for(
                        _fp.parse_instant(dates[i]) if dates[i] else None,
                        freq) if freq in ('monthly', 'quarterly') else None
                    if _pe is not None:
                        v['period_end'] = _pe.isoformat()
                    # Audit-R25 任务1: 最新一期锚按指标发布频率识别过期
                    # (EA HICP 停 2025-12、as_of 2026-11 → 滞后>月频窗口
                    # 必须标过期并显示末观测日;历史锚不适用——滞后是
                    # 时点差不是采集缺陷;未注册=无已批准窗口,不作判断)。
                    # Audit-R26 任务2: 窗口自**统计期末**起算+决策驱动
                    # 政策序列按政策最后确认纪律(无更晚已证实决议≠过期)。
                    if a.get('months_before') == 0:
                        _pol = _fp.policy_for(mid) or {}
                        _confirmed = None
                        if _pol.get('decision_dated'):
                            _cal_p = (os.path.join(root, 'config',
                                                   'release_calendar.json')
                                      if root else None)
                            _confirmed = _fp.confirmed_policy_decision_after(
                                mid, dates[i], a['as_of'],
                                calendar_path=_cal_p)
                        fo = _fp.assess_observation_freshness(
                            mid, dates[i], a['as_of'],
                            confirmed_later_decision=_confirmed)
                        if _pol.get('decision_dated'):
                            v['policy_confirm_date'] = dates[i]
                            v['freshness_basis'] = fo.get(
                                'freshness_basis', 'policy_confirmation')
                        if fo['status'] == 'STALE':
                            v['freshness'] = 'stale'
                            v['freshness_lag_days'] = fo['lag_days']
                            v['freshness_window_days'] = fo['window']
                            if fo.get('period_end'):
                                v['freshness_period_end'] = \
                                    fo['period_end']
                                v['freshness_period_lag_days'] = \
                                    fo.get('period_lag_days')
                            if fo.get('freshness_basis') == \
                                    'policy_confirmation':
                                v['freshness_note'] = (
                                    f'按政策最后确认纪律识别为过期: '
                                    f'最后确认{dates[i]}后已有更晚决议证实'
                                    f'({(_confirmed or "")[:10]}首发≤'
                                    f'{a["as_of"]})而数据未反映——最新一期'
                                    f'=确证过期,如实显示最后确认日,不当当期')
                            else:
                                v['freshness_note'] = (
                                    f'按发布频率识别为过期'
                                    f'({fo["frequency"]}频): '
                                    f'末观测{dates[i]}滞后{fo["lag_days"]}天>'
                                    f'{fo["window"]}天窗口'
                                    f'(统计期末{fo.get("period_end")}后'
                                    f'{fo.get("period_lag_days")}天>'
                                    f'{fo["window"]}天已批准窗口)'
                                    f'——最新一期=过期数据,如实显示末观测日,'
                                    f'不当当期')
                        elif fo['status'] == 'UNVERIFIED':
                            # Audit-R27 任务1: 第三态——无更晚已证实决议且
                            # 无证实间隔超决策周期上限: 本地日历未收录≠
                            # 未发生,现值是否仍有效无法核验(未核验≠过期:
                            # 不虚构更晚决议,亦不判新鲜)。
                            v['freshness'] = 'unverified'
                            v['freshness_lag_days'] = fo['lag_days']
                            v['unconfirmed_span_days'] = fo.get(
                                'unconfirmed_span_days', fo['lag_days'])
                            v['decision_cycle_bound_days'] = fo.get(
                                'decision_cycle_bound_days')
                            v['freshness_note'] = (
                                f'按政策确认纪律无法核验: 最后确认'
                                f'{dates[i]}后{v["unconfirmed_span_days"]}天'
                                f'无已证实决议(超决策周期上限'
                                f'{v["decision_cycle_bound_days"]}天——本地'
                                f'日历未收录≠未发生,现值可能已调整而数据'
                                f'未反映)——标未核验,不以未证实间隔判过期'
                                f'亦不判新鲜')
                    pf_cfg = cell.get('policy_face') or {}
                    mdate = None
                    mp = pf_cfg.get('market_pair')
                    if mp:
                        mser = series_cache.get(mp)
                        if mser and mser.get('dates'):
                            k = bisect.bisect_right(mser['dates'], a['as_of']) - 1
                            if k >= 0:
                                mdate = mser['dates'][k]
                    pdates = _policy_dates(
                        pf_cfg, dates[i], market_date=mdate,
                        value_change_date=(
                            _last_value_change(dates, values, i)
                            if pf_cfg.get('decision_kind') else None),
                        metric_id=cell.get('metric_id'), as_of=a['as_of'],
                        calendar_path=(
                            os.path.join(root, 'config',
                                         'release_calendar.json')
                            if root else None))
                    if pdates:
                        v['policy_dates'] = pdates
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
                # Audit-R30 任务2: 同一期重复观测披露——不同时点锚落位
                # 同一观测日(月频序列隔月锚/稀疏序列)时逐锚注明「与某锚
                # 同一观测,无新增观测」,不把同一读数当两个时点的独立
                # 证据(缺精确基期→缺证同理已在 yoy_status)。
                _by_obs = {}
                for _lb, _av in row['anchors'].items():
                    _od = _av.get('observation_date') if \
                        isinstance(_av, dict) else None
                    if _od:
                        _by_obs.setdefault(_od, []).append(_lb)
                for _od, _lbs in _by_obs.items():
                    if len(_lbs) > 1:
                        for _lb in _lbs:
                            _others = '/'.join(
                                sorted(l for l in _lbs if l != _lb))
                            row['anchors'][_lb].setdefault(
                                'duplicate_observation_note',
                                '与%s为同一观测(%s),无新增观测'
                                % (_others, _od))
                cells.append(row)
    asset_universe = [k for k in ASSET_UNIVERSE
                      if k in (snap.get('series_store') or {})]
    return {'cells': cells, 'absent': absent,
            'asset_universe': asset_universe}


def stale_only_groups(point_values, planned_pairs):
    """Audit-R26 任务2: 「只剩确证过期值」的必要维度组集合(阻断/渲染共源)。

    组内最新一期(months_before==0)ok 锚全部 freshness=stale → 入列;
    任一非过期 ok 锚在场即不入列(过期格标注不改组级)。历史锚过期=
    时点差非缺陷,不参与。返回 sorted [(region,dimension),...]。"""
    latest_ok, latest_stale = {}, {}
    for c in (point_values or {}).get('cells') or []:
        g = (c.get('region'), c.get('dimension'))
        la = (c.get('anchors') or {}).get('最新一期') or {}
        if la.get('status') == 'ok':
            latest_ok[g] = latest_ok.get(g, 0) + 1
            if la.get('freshness') == 'stale':
                latest_stale[g] = latest_stale.get(g, 0) + 1
    return sorted(g for g in (planned_pairs or ())
                  if latest_ok.get(g)
                  and latest_stale.get(g, 0) == latest_ok[g])


def current_period_groups(point_values, planned_pairs,
                          has_current_anchor=True):
    """Audit-R27 任务1: 当期缺失/未核验组集合(阻断/渲染共源)。

    按所请求的不同时间点统计覆盖——同一时点多个指标不能替代另一个
    时点(他时点 ok 不补当期缺口):
    - missing: 组内「最新一期」锚零 ok(全部不可得/停摆延误)——当期
      缺失,历史锚 ok 不改判;
    - unverified: 组内当期 ok 锚全部 freshness=unverified(决策序列无
      更晚已证实决议且无证实间隔超决策周期上限)——现值无法核验;
      任一非 unverified 的当期 ok 锚在场即不入列。
    - stale_mix(R28 任务2): 组内当期 ok 锚全为「过期或未核验」且两类
      并存(必需当期只有过期与未核验值的混合形态)——单一类判定
      (all-stale→R26 类/all-unverified→R27 类)各自遗漏的混合缺口,
      交付草稿并逐格点名。
    计划无当期锚(纯历史点问句,如「2024年6月相比2023年6月」)不判
    (当期非所请求时点,返回空)。返回 {'missing': sorted, 'unverified':
    sorted, 'stale_mix': sorted},与 blocked_class_of 的 map_current_
    period_missing / map_current_period_unverified / map_current_
    period_stale_mix 同源同判。"""
    if not has_current_anchor:
        return {'missing': [], 'unverified': [], 'stale_mix': []}
    cur_ok, cur_unver, cur_stale = {}, {}, {}
    for c in (point_values or {}).get('cells') or []:
        g = (c.get('region'), c.get('dimension'))
        la = (c.get('anchors') or {}).get('最新一期') or {}
        if la.get('status') == 'ok':
            cur_ok[g] = cur_ok.get(g, 0) + 1
            if la.get('freshness') == 'unverified':
                cur_unver[g] = cur_unver.get(g, 0) + 1
            elif la.get('freshness') == 'stale':
                cur_stale[g] = cur_stale.get(g, 0) + 1
    return {
        'missing': sorted(g for g in (planned_pairs or [])
                          if cur_ok.get(g, 0) == 0),
        'unverified': sorted(g for g in (planned_pairs or [])
                             if cur_ok.get(g, 0)
                             and cur_unver.get(g, 0) == cur_ok[g]),
        'stale_mix': sorted(
            g for g in (planned_pairs or [])
            if cur_ok.get(g, 0)
            and cur_unver.get(g, 0) and cur_stale.get(g, 0)
            and cur_unver.get(g, 0) + cur_stale.get(g, 0) == cur_ok[g])}


# ── Audit-R28 任务2: 政策官方记录面(缺官方目标=点名缺口交付草稿) ─────────
# 各地区「官方政策目标」代表口径(问句指定央行目标水平时,交付判定须
# 官方记录或可推惯例至少其一在场;两者皆缺=缺官方目标)。
_OFFICIAL_TARGET_METRICS = {'US': 'DFEDTARU', 'EA': 'ECB_MRO',
                            'JP': 'JP_POLICY_TARGET', 'CN': 'CN_LPR_1Y'}
# 问句「指定官方目标」判定的两族词形: 地区央行/政策目标词 + 水平/调整
# 问句词——两族同时在问句在场且指向同一地区,该地区才落「用户指定的
# 官方目标」要求(只问「货币政策环境」不触发——环境≠目标水平,旧例
# A 类问句不得因本类新缺口改判)。
_OFFICIAL_ASK_REGION_WORDS = {
    'JP': ('日本央行', '日银', 'BOJ', '日本政策利率', '日本央行政策利率'),
    'US': ('美联储', 'Fed', 'FOMC', '美国政策利率'),
    'EA': ('欧央行', 'ECB', '欧洲央行', '欧元区政策利率'),
    'CN': ('人民银行', 'PBOC', '中国央行', 'LPR', '中国政策利率'),
}
_OFFICIAL_ASK_LEVEL_WORDS = ('处于什么水平', '什么水平', '水平如何',
                              '是多少', '多少', '多高', '多低',
                              '距.*调整', '调整.*多久', '距离上次调整',
                              '目标利率', '利率目标', '官方目标')
# Audit-R32 任务2: 指代形(「两地央行…各处于什么水平」)回指绑定用——
# 地区 plain 名(全文点名)与指代计数词(含「央行」的小句内)
_OFFICIAL_REGION_PLAIN = {
    'JP': ('日本',), 'EA': ('欧元区', '欧洲'),
    'US': ('美国', '美联储'), 'CN': ('中国',)}
_OFFICIAL_DEICTIC_WORDS = ('两地', '两国', '两家', '各自', '各处于', '各为',
                           '二者', '两者', '各方', '各地')


def question_official_target_regions(question):
    """问句点名「官方政策目标」的地区集合(确定性词形判定)。

    判定=地区央行/目标词族 ∩ 水平/调整问句词族(正则搜索)同时在场。
    空集=问句未指定官方目标(如只问「货币政策环境」)——缺官方目标
    类不触发,不因新增缺口改判旧问句。

    Audit-R32 任务2: 指代形补绑——「日本和欧元区的…: 两地央行当前
    官方政策目标利率各处于什么水平」以「两地央行」回指前文点名的经济
    体,原词族(日本央行/欧央行…)在场性判空→问句明确要求官方目标而
    要求面为空(缺口判定整段关闭)。规则: 含「央行」+水平词的小句内无
    显式地区央行词形而带指代计数词(两地/两国/两家/各自…)时,绑定到
    问句全文以**地区 plain 名**点名的经济体(日本/欧元区/美国/中国);
    显式词形命中优先(「日本央行政策利率处于什么水平」只绑 JP,不因
    全文另有「美国」而扩绑)。"""
    import re as _re_r28
    q = str(question or '')
    if not q:
        return set()
    level = any(
        _re_r28.search(w, q) for w in _OFFICIAL_ASK_LEVEL_WORDS)
    if not level:
        return set()
    req = {eco for eco, words in _OFFICIAL_ASK_REGION_WORDS.items()
           if any(w in q for w in words)}
    if '央行' in q:
        named = {eco for eco, words in _OFFICIAL_REGION_PLAIN.items()
                 if any(w in q for w in words)}
        for clause in _re_r28.split(r'[,，。;；:?？\n]', q):
            if '央行' not in clause:
                continue
            if any(w in clause
                   for words in _OFFICIAL_ASK_REGION_WORDS.values()
                   for w in words):
                continue                       # 显式词形小句=已绑
            if any(w in clause for w in _OFFICIAL_DEICTIC_WORDS):
                req |= named
    return req


def official_policy_record_face(point_values, planned_pairs, cutoff,
                                question=None, calendar_path=None):
    """Audit-R28 任务2: 政策官方记录面(rows+gaps;阻断/渲染共源)。

    对计划内政策维度地区逐一取官方记录(freshness_policy.policy_
    decision_state,纯日历文件面): 记录在场→决议/生效/官方目标/最近
    维持/距上次调整(按生效日)逐项入 rows;记录缺席→回退「序列+惯例」
    可推性判定(当期 ok 锚的 policy_dates 决议日与生效日均可推=可推)。
    gaps 只对**问句指定官方目标**的地区判(question_official_target_
    regions 非空且该地区在列——「用户指定的官方目标」缺口才阻断;
    未点名地区记录缺席如实不入 rows,不触发缺口)。gaps 非空与
    blocked_class_of 的 map_official_target_missing 同源同判。"""
    import freshness_policy as _fp_opr
    rows, gaps = [], []
    derivable = set()
    for c in (point_values or {}).get('cells') or []:
        if c.get('dimension') != 'policy':
            continue
        la = (c.get('anchors') or {}).get('最新一期') or {}
        if la.get('status') != 'ok':
            continue
        pdd = c.get('policy_dates') or {}
        if pdd.get('decision') and pdd.get('effective'):
            derivable.add(c.get('region'))
    pol_regions = sorted({eco for eco, dim in (planned_pairs or ())
                          if dim == 'policy'})
    required = question_official_target_regions(question)
    for eco in pol_regions:
        mid = _OFFICIAL_TARGET_METRICS.get(eco)
        if not mid:
            continue
        st = _fp_opr.policy_decision_state(mid, cutoff,
                                           calendar_path=calendar_path)
        if st.get('present'):
            _row = {
                'region': eco, 'metric_id': mid,
                'label': _REGION_LABEL.get(eco, eco),
                'official_target': st.get('official_target'),
                'pending_adjustments': st.get('pending_adjustments'),
                'pending_target': st.get('pending_target'),
                'pending_effective_on': st.get('pending_effective_on'),
                'decision': st.get('last_decision'),
                'effective': st.get('last_effective'),
                'last_maintenance': st.get('last_maintenance'),
                'confirmed_through': st.get('last_confirmed_on'),
                'days_since_adjustment': st.get('days_since_adjustment'),
                'days_since_decision': st.get('days_since_decision'),
                'days_since_maintenance': st.get('days_since_maintenance'),
                'records': st.get('records')}
            # Audit-R31 任务3: 问句点名当前官方目标而 as_of 时点无已生效
            # 决议、仅有待生效公告→当前值**缺证**明标(不得以待生效值
            # 冒充当前官方目标;生效日起才入官方目标列)。
            if (eco in required and _row['official_target'] is None
                    and st.get('pending_target') is not None):
                # 待生效决议的决议日取自待生效条目(仅有待生效公告时
                # last_decision=None——无已生效决议,不得写成「决议日 None」)
                _pdec = next((p.get('decision_date') for p in
                              (st.get('pending_adjustments') or [])
                              if isinstance(p, dict)
                              and p.get('decision_date')), None)
                _row['current_target_missing_evidence'] = True
                _row['pending_decision'] = _pdec
                _row['current_target_missing_note'] = (
                    '当前官方目标缺证——研究时点 %s 无已生效决议在档,'
                    '仅有待生效公告(目标 %s,决议日 %s,生效日 %s);'
                    '待生效值不得写成当时已生效的官方目标'
                    % (cutoff, st.get('pending_target'),
                       _pdec or st.get('last_decision'),
                       st.get('pending_effective_on')))
                # Audit-R32 任务2: 行级缺口——R31 只落行标记不落 gaps,
                # blocked_class_of 读 gaps 判→「问现行官方目标×只有待
                # 生效公告」仍按正稿交付/可归档(行标记与交付判定不同判)。
                # 同一缺口入 gaps: 行级缺口/首页草稿/正式归档拒绝同判。
                gaps.append({
                    'region': eco, 'metric_id': mid,
                    'label': _REGION_LABEL.get(eco, eco),
                    'gap': 'current_target_missing_evidence',
                    'pending_target': st.get('pending_target'),
                    'pending_decision': _pdec,
                    'pending_effective_on': st.get('pending_effective_on'),
                    'note': _row['current_target_missing_note']})
            rows.append(_row)
        elif eco in required and eco not in derivable:
            gaps.append({
                'region': eco, 'metric_id': mid,
                'label': _REGION_LABEL.get(eco, eco),
                'note': (f'{_REGION_LABEL.get(eco, eco)}官方政策目标'
                         f'({mid})无官方记录(日历无 policy_decision/'
                         'policy_maintenance 条目)且序列面决议/生效日'
                         '不可推——问句指定官方目标时现值无官方口径可依,'
                         '不以市场序列值冒充宣布目标;补录官方决议实录后'
                         '重跑转正(Audit-R28 任务2)')})
    return {'rows': rows, 'gaps': gaps,
            'required_regions': sorted(required)}


def missing_core_groups(point_values, planned_pairs):
    """Audit-R26 验收: 核心维度组零 ok 格集合(阻断/渲染共源)。

    与 agent_judgment.blocked_class_of 的 map_core_dimension_missing
    同源同判(R20 既档语义): 组内任一锚 status=ok 即有格;全部缺席/不可得
    → 整组缺数=交付草稿。返回 sorted [(region,dimension),...]。"""
    ok_pairs = set()
    for c in (point_values or {}).get('cells') or []:
        g = (c.get('region'), c.get('dimension'))
        if any(a.get('status') == 'ok'
               for a in (c.get('anchors') or {}).values()):
            ok_pairs.add(g)
    return sorted(set(planned_pairs or ()) - ok_pairs)


def sparse_anchor_groups(point_values, planned_pairs):
    """Audit-R26 验收: 锚覆盖不足组集合(阻断/渲染共源)。

    与 blocked_class_of 的 map_anchor_coverage_insufficient 同源同判
    (R21 反例③): 组内 ok 锚<2 且存在未经日历证实延误的空锚——「仅存
    最新单点」不构成三时点对照满足。返回 sorted [(region,dimension),...]。"""
    ok_anchor_n, gap_unverified = {}, {}
    for c in (point_values or {}).get('cells') or []:
        g = (c.get('region'), c.get('dimension'))
        for a in (c.get('anchors') or {}).values():
            if a.get('status') == 'ok':
                ok_anchor_n[g] = ok_anchor_n.get(g, 0) + 1
            elif not a.get('calendar_blocked_observation'):
                gap_unverified[g] = gap_unverified.get(g, 0) + 1
    return sorted(g for g in (planned_pairs or ())
                  if ok_anchor_n.get(g, 0) < 2 and gap_unverified.get(g, 0))


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
                    pd_iso, _r = _visible_publish(mid, freq, probe)
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


# ── Audit-R20 任务3: 读者正文复算面(同一组可复算事实的确定性部分) ──────

def _trio_window(series, common, d1, days_back, min_span_days=None):
    """共同交易日窗: d1 与距 d1−days_back 天最近的共同交易日 d0(≤界日
    侧),Δ(bp) 与恒等残差。None=窗不可开(端点不足)。
    R21 任务3: min_span_days=窗跨度充足界——d0 侧历史不足时(如只剩两个
    相邻共同交易日),窗实际跨度远短于意图跨度,数字会冒充月度/年度变化;
    该情形 span_status='insufficient_history',调用方须显示历史不足、
    不出数。"""
    import datetime
    target = (datetime.date.fromisoformat(d1)
              - datetime.timedelta(days=days_back)).isoformat()
    cand = [d for d in common if d <= target] or common[:-1]
    d0 = min(cand, key=lambda d: abs((datetime.date.fromisoformat(d)
                                      - datetime.date.fromisoformat(target)).days))
    span = (datetime.date.fromisoformat(d1)
            - datetime.date.fromisoformat(d0)).days
    span_status = 'ok'
    if min_span_days is not None and span < min_span_days:
        span_status = 'insufficient_history'
    chg = {}
    for mid in US_RATES_TRIO:
        try:
            chg[mid] = round((float(series[mid][d1])
                              - float(series[mid][d0])) * 100.0, 2)
        except (TypeError, ValueError):
            return None
    return {
        'window': {'from': d0, 'to': d1, 'calendar_days_between': span},
        'span_status': span_status,
        'chg_bp': chg,
        'decomposition': (f"十年期名义 Δ{chg['UST_10Y']:+g}bp = "
                          f"实际 Δ{chg['TIPS_10Y']:+g}bp + 盈亏平衡 "
                          f"Δ{chg['BEI_10Y']:+g}bp"),
        'identity_residual_bp': round(
            chg['UST_10Y'] - (chg['TIPS_10Y'] + chg['BEI_10Y']), 2),
    }


def us_rates_trio_face(snap, root, window_days=45, cutoff=None):
    """美国十年期三利率**共同交易日**复算: 名义=实际+盈亏平衡 的对账面。

    R19 缺陷: 正文利率分解用了三个序列各自的最新观测日(非同日),分量的
    和与名义变化对不上。本面只在三序列**共同交易日**上取值;月度窗=最近
    共同交易日 d1 与距 d1−30 天最近的共同交易日 d0,Δ(bp)=d1−d0,
    identity_residual_bp = ΔUST −(ΔTIPS+ΔBEI)(同日同窗,读者可逐位核)。
    R20: 另附 12 个月窗(d1−365 最近共同日)——地图问句的年headline
    「名义+100bp=实际+107bp+盈亏平衡−7bp」一类年窗数字同样须共同日
    同窗对账(年窗恒等残差逐位披露)。
    Audit-R31 任务1: cutoff 在场=问题声明研究时点——d1 与窗口取
    「≤cutoff 的最近共同日」(历史研究不吃快照当前面;None=序列最新,
    既有口径零回归)。"""
    import datetime
    series = {}
    for mid in US_RATES_TRIO:
        s, _err = _series(mid, snap, root)
        if not s or not s.get('dates'):
            return {'status': 'absent',
                    'note': f'{mid} 序列不可得——三利率共同交易日复算缺席'
                            f'(检索范围=快照 series_store 采集档通道)'}
        series[mid] = {d: v for d, v in zip(s['dates'], s['values'])}
    common = sorted(set(series[US_RATES_TRIO[0]])
                    & set(series[US_RATES_TRIO[1]])
                    & set(series[US_RATES_TRIO[2]]))
    if cutoff:
        # R31: 时点约束先落位(时点晚于序列末日=取序列末日,不虚构未来)
        common = [d for d in common if d <= cutoff] or common
    horizon = [d for d in common
               if d >= (datetime.date.fromisoformat(common[-1])
                        - datetime.timedelta(days=window_days)).isoformat()]
    if len(common) < 2:
        return {'status': 'absent', 'note': '共同交易日不足两日,无法开月度窗'}
    d1 = common[-1]
    mwin = _trio_window(series, common, d1, 30, min_span_days=15)
    if mwin is None:
        return {'status': 'absent', 'note': '月度窗端点不可开'}
    ywin = _trio_window(series, common, d1, 365, min_span_days=183)
    if mwin['span_status'] == 'insufficient_history':
        return {'status': 'insufficient_history',
                'kind': '共同交易日三利率分解',
                'window': mwin['window'],
                'levels_at_to': {mid: series[mid][d1] for mid in US_RATES_TRIO},
                'note': (f"月度窗历史不足: 共同交易日仅覆盖 "
                         f"{mwin['window']['calendar_days_between']} 个日历日"
                         f"(意图 30 天窗,充足界≥15 天)——月度与年度利率变化"
                         f"均标历史不足,不出数,不以相邻交易日差冒充月度变化"
                         f"(年度窗同源同判)。"),
                'recent_common_days': horizon[-10:]}
    out = {
        'status': 'ok', 'kind': '共同交易日三利率分解',
        'window': mwin['window'],
        'levels_at_to': {mid: series[mid][d1] for mid in US_RATES_TRIO},
        'chg_bp': mwin['chg_bp'],
        'decomposition': mwin['decomposition'],
        'identity_residual_bp': mwin['identity_residual_bp'],
        'identity_note': '名义=实际+盈亏平衡 的恒等残差(同日同窗;非零=源端'
                         '口径差,逐位披露不吸收)',
        'recent_common_days': horizon[-10:],
    }
    if ywin is not None:
        out['window_12m'] = ywin['window']
        if ywin['span_status'] == 'insufficient_history':
            out['window_12m_status'] = 'insufficient_history'
            out['window_12m_note'] = (
                f"年度窗历史不足: 共同交易日跨度仅 "
                f"{ywin['window']['calendar_days_between']} 个日历日"
                f"(意图 365 天窗,充足界≥183 天)——年度利率变化标历史不足,"
                f"不出数。")
        else:
            out['chg_bp_12m'] = ywin['chg_bp']
            out['decomposition_12m'] = ywin['decomposition']
            out['identity_residual_bp_12m'] = ywin['identity_residual_bp']
    return out


# 读者正文资产变化面: 四地股基准+VIX+美元/黄金/美债(月度窗,两端实测日)
ASSET_MOVE_METRICS = ['SPX', 'SHCOMP', 'DAX', 'NIKKEI225', 'VIX', 'DXY',
                      'GOLD_F', 'UST_10Y']


def _nearest_obs_idx(dates, target):
    """距 target 最近的观测下标(两侧均可,平局取前)。

    R20 真实 VIX 工单回归: 「月涨38.07%」一类的 N 月窗基准日,界日
    (截止日−N 月)常落周末——取「≤界日最新」会把 33 天前当一个月前,
    取最近邻(界日前 2 天 vs 后 1 天)才是读者口径的整月。窗口端点
    日期随行披露,选哪端读者可自核。"""
    import bisect
    i_le = _obs_at(dates, [0] * len(dates), target)
    i_gt = bisect.bisect_right(dates, target)
    if i_le is None:
        return i_gt if i_gt < len(dates) else None
    if i_gt >= len(dates):
        return i_le
    from datetime import date
    t = date.fromisoformat(target)
    d_le = abs((date.fromisoformat(dates[i_le]) - t).days)
    d_gt = abs((date.fromisoformat(dates[i_gt]) - t).days)
    return i_gt if d_gt < d_le else i_le


def asset_move_rows(series_map, cutoff, months=1,
                    metrics=None):
    """纯函数: {mid: {'dates','values'}} × 截止日 → N 月变化行。

    契约层(judgment_contract 资产回报回贴)与本面(asset_move_face)
    同一算术源——叙述里的回报数字在哪复算都逐位一致。"""
    target = _shift_months(cutoff, months)
    rows, absent = [], []
    for mid in (metrics or ASSET_MOVE_METRICS):
        s = series_map.get(mid) or {}
        dates, values = s.get('dates') or [], s.get('values') or []
        if not dates:
            absent.append(mid)
            continue
        i1 = _obs_at(dates, values, cutoff)
        i0 = _nearest_obs_idx(dates, target)
        if i1 is None or i0 is None or i1 == i0:
            absent.append(mid)
            continue
        v0, v1 = float(values[i0]), float(values[i1])
        if not v0:
            absent.append(mid)
            continue
        rows.append({'metric_id': mid,
                     'window': {'from': dates[i0], 'to': dates[i1]},
                     'from_value': values[i0], 'to_value': values[i1],
                     'chg_pct': round((v1 / v0 - 1.0) * 100.0, 2),
                     'chg_abs': round(v1 - v0, 4)})
    return {'status': 'ok', 'window_months': months,
            'window_rule': f'≤{cutoff} 最新观测 vs 最近于{target} 的观测'
                           f'(界日无观测取最近邻;两端实际观测日随行披露)',
            'rows': rows, 'absent': absent}


def asset_move_face(snap, root, months=1, cutoff=None):
    """关键资产 N 个月变化(读者可核): 窗=≤截止日最新观测 vs 最近于
    (截止日−N月)的观测(界日无观测取最近邻),两端实际观测日随行披露——
    「月涨38.07%」一类正文数字必须有可复算窗口(R19 缺陷: 只给数字不
    给窗口,读者无法核)。R20: 截止日=研究计划 cutoff 显式传入(契约回贴
    同参复算——缺席时以快照 as_of 前 10 位兜底,两界面同一算术源)。"""
    import datetime
    cutoff = str(cutoff or snap.get('as_of') or snap.get('date')
                 or datetime.date.today().isoformat())[:10]
    series_map = {}
    for mid in ASSET_MOVE_METRICS:
        s, _err = _series(mid, snap, root)
        if s and s.get('dates'):
            series_map[mid] = s
    out = asset_move_rows(series_map, cutoff, months=months)
    out['absent'] = [m for m in ASSET_MOVE_METRICS
                     if m not in series_map] + out.get('absent', [])
    return out


def turning_merge_and_picks(turnings, cand, need=3):
    """R23 任务4 同轮并项 + R24 任务4 补选交还(纯函数)。

    同维度且观测窗重叠的转折=同一轮事件并为一项;并项后不足 need 项时
    由引擎按候选面证据分补选独立转折(窗口不与已用重叠为硬条件,优先
    不同维度、再按 |Δ| 降序)。渲染面与判断契约(judgment_contract
    check17)同源调用——补选项交还判断席时,席位看到的补选集合与读者
    表中「引擎补选」行逐项一致。"""
    cand_by_key = {(c.get('metric_id'), str(c.get('to_ym'))): c
                   for c in (cand or [])}

    def _t_ym(t):
        return str(t.get('date') or '')[:7]

    def _t_win_months(cc):
        out, ym0 = set(), str((cc or {}).get('from_ym') or '')
        ym1 = str((cc or {}).get('to_ym') or '')
        if len(ym0) == 7:
            for i in range(0, 13):
                m = _shift_months(ym0 + '-01', -i)[:7]
                if ym1 and m > ym1:
                    break
                out.add(m)
        return out

    episodes = []
    for t in (turnings or []):
        cc = cand_by_key.get((t.get('metric_id'), _t_ym(t)))
        dim = (cc or {}).get('dimension') or ''
        wm = _t_win_months(cc)
        for ep in episodes:
            if dim and ep['dim'] == dim and (ep['months'] & wm):
                ep['turnings'].append(t)
                ep['months'] |= wm
                break
        else:
            episodes.append({'dim': dim, 'months': set(wm),
                             'turnings': [t]})
    _used_keys = {(t.get('metric_id'), _t_ym(t)) for t in (turnings or [])}
    _used_months = set()
    for ep in episodes:
        _used_months |= ep['months']
    _used_dims = {ep['dim'] for ep in episodes if ep['dim']}
    picks = []
    if len(episodes) < need:
        _pool = [c for c in (cand or [])
                 if (c.get('metric_id'), str(c.get('to_ym')))
                 not in _used_keys
                 and not (_t_win_months(c) & _used_months)
                 and c.get('delta') is not None]
        _pool.sort(key=lambda c: (c.get('dimension') in _used_dims,
                                  -abs(c.get('delta') or 0)))
        picks = _pool[:need - len(episodes)]
    return episodes, picks


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


def _series_from_report(rj, mid):
    """report.json 步骤面取序列(与 judgment_contract.build_face 同源口径,
    本模块不反向依赖契约以免环)。"""
    for st in rj.get('steps') or []:
        nm = st.get('step') or ''
        if nm.startswith('S4_history_') and nm[11:] == mid:
            return ((st.get('envelope') or {}).get('data') or {}).get('series')
    return None


def _distinguishing_obs(rj, cutoff, metric_id):
    """区分性观测(R21 任务4): 传导链「能区分竞争解释的指标」须给出
    读者可见的观测——引擎当前面(最新观测+近30日变化),非仅指标名。
    序列不在场→None(如实缺席,不编数)。"""
    m = re.search(r'[A-Z][A-Z0-9_]{1,20}', str(metric_id or ''))
    if not m or not cutoff:
        return None
    ser = _series_from_report(rj, m.group(0))
    if not ser or not ser.get('dates'):
        return None
    dates, values = ser['dates'], ser['values']
    k1 = bisect.bisect_right(dates, cutoff) - 1
    if k1 < 0 or values[k1] is None:
        return None
    v1 = values[k1]
    import datetime
    back = (datetime.date.fromisoformat(cutoff)
            - datetime.timedelta(days=30)).isoformat()
    k0 = bisect.bisect_right(dates, back) - 1
    if not isinstance(v1, (int, float)):
        return f"(引擎当前面: {dates[k1]}={v1})"
    _unit = str(ser.get('unit') or '')
    _is_pct_level = ('%' in _unit or 'percent' in _unit.lower()
                     or str(ser.get('unit_family') or '') == 'rate')
    # Audit-R24 任务3: 30日窗两端取到同一观测(序列停更/最新观测早于
    # 窗界)——窗口内无新观测,不以 0 变化冒充;另列最近两期的实际变化
    # (单位随序列族: 百分比水平=bp,指数水平=指数点+%),读者可核。
    if k0 == k1:
        j = k1 - 1
        while j >= 0 and values[j] is None:
            j -= 1
        if j >= 0 and isinstance(values[j], (int, float)) and values[j]:
            pv = values[j]
            dc = v1 - pv
            _tail24 = (f"Δ{dc * 100:+g}bp" if _is_pct_level else
                       f"Δ{dc:+g} 指数点({dc / pv * 100:+.2f}%)")
            return (f"(引擎当前面: {dates[k1]}={v1:g};近30日窗口内无新观测"
                    f"——最近两期 {dates[j]}={pv:g}→{dates[k1]}={v1:g},"
                    f"{_tail24})")
        return (f"(引擎当前面: {dates[k1]}={v1:g};近30日窗口内无新观测)")
    if k0 >= 0 and isinstance(values[k0], (int, float)) and values[k0]:
        v0 = values[k0]
        chg = v1 - v0
        if _is_pct_level:
            # Audit-R23 任务4: 百分比水平序列(利率/盈亏平衡/同比率)的
            # 近30日变化=百分点,按基点表述并带两端值与方向词
            # (2.35→2.19 写为「下降16bp」,不再误标 % 或只给相对幅)。
            bp = round(chg * 100)
            direction = '上升' if bp > 0 else ('下降' if bp < 0 else '持平')
            return (f"(引擎当前面: {dates[k1]}={v1:g},"
                    f"近30日{v0:g}→{v1:g},{direction}{abs(bp):g}bp)")
        # Audit-R24 任务3: 指数水平序列的变化按「指数点」记法(水平差),
        # 相对幅另列括号——CPI 266.614→271.903 写「+5.289 指数点
        # (+1.98%)」,不再把水平差误标 % (Δ5.289% 会与 +1.98% 相混)。
        return (f"(引擎当前面: {dates[k1]}={v1:g},"
                f"近30日{v0:g}→{v1:g},{chg:+g} 指数点"
                f"({chg / v0 * 100:+.2f}%))")
    return f"(引擎当前面: {dates[k1]}={v1:g})"


def render_map_report(rj, judgment_doc, review_state=None, root=None):
    """MAP_REPORT.md 正文(读者可直读可核查: 关键数字附来源/单位/实际观测日)。

    装配面=report.json research_plan(共享计划+点值+转折候选)+Agent 席
    judgment.reader_map 原文;零生成——总判断/走位/传导叙述/转折判断/历史段
    全部来自 reader_map(attach 契约已验非空+数值经 judgment_contract 回贴
    核对),引擎只排表与落来源。

    Audit-R22 任务4: root 在场时按运行快照(snapshot_id 定位,不跨快照
    取数)确定性渲染——首页三件(总判断/四地三时点表/证据最充分传导速览)、
    主解释vs竞争解释对质表、历史类比逐窗经济×资产并列面。快照不在场=
    该面如实缺席注记,不虚构。"""
    rp = rj.get('research_plan') or {}
    rm = (judgment_doc or {}).get('reader_map') or {}
    pv = rp.get('point_values') or {}
    run = rj.get('run') or {}
    # 运行快照(报告段按 snapshot_id 定位;缺席→历史并列面如实缺席)
    _snap_r = None
    _snap_note = None
    if root:
        _sid = (((rj.get('layers') or {}).get('L1_事实层') or {})
                or {}).get('snapshot_id')
        _sp = (os.path.join(root, 'data', 'daily', f'{_sid}.json')
               if _sid else None)
        if _sp and os.path.isfile(_sp):
            try:
                with open(_sp, encoding='utf-8') as _f:
                    _snap_r = json.load(_f)
            except (OSError, ValueError) as _e:
                _snap_note = f'快照文件不可读({_sp}: {type(_e).__name__})'
        else:
            _snap_note = (f'运行快照文件不在场({_sid or "snapshot_id缺席"}'
                          '——历史并列面不跨快照取数,如实缺席)')
    lines = ['# 全球宏观经济变化地图(读者报告)', '']
    lines.append(f"- 问题: {run.get('question')}")
    lines.append(f"- 研究截止日: {rp.get('cutoff')} | 快照: "
                 f"{(rj.get('layers', {}).get('L1_事实层', {}) or {}).get('snapshot_id')}"
                 f" | 运行: {run.get('ts_utc')} | 代码: {run.get('git_head')}")
    # Audit-R31 任务1: 问题声明研究时点披露——计划/取数/覆盖/政策/报告
    # 全链绑定时点;与快照 target_date 不一致=如实点名(历史研究不吃
    # 快照当前面,发布纪律下只取「观测日≤时点且发布日≤时点」数据)。
    _asd = rp.get('as_of_declared')
    _eg_hdr = run.get('evidence_gate') or {}
    _r32_hdr = isinstance(_eg_hdr, dict) and bool(_eg_hdr.get('as_of'))
    # r32 报告 as_of_declared 恒在场(含未声明形,basis=None)——声明形才渲
    # 本行;旧档(无 evidence_gate)条件不变=字节不变
    if _asd and (_asd.get('basis') or not _r32_hdr):
        _diff = (';与快照 target_date %s 不一致,以问题声明为准'
                 % _asd.get('snapshot_target_date')
                 if _asd.get('differs_from_snapshot') else '')
        lines.append(f"- 研究时点口径: {_asd.get('basis')}{_diff}——"
                     "本报告全部窗口/锚点/政策面绑定该时点(数据=当时"
                     "已发布面,后来发布的数据不回填)")
    # Audit-R32 任务1: 请求月末 vs 实际覆盖日(月末未到=只交截至实际日期
    # 的结果)+证据口径行——只在 r32 字段在场时渲染(旧档重渲字节不变)
    if isinstance(_asd, dict) and _asd.get('clamped_to_coverage'):
        lines.append(
            f"- 请求月末/实际覆盖日: 请求 {_asd.get('requested_month_end')}"
            f" | 快照实际覆盖 {_asd.get('actual_coverage_date')} | 研究"
            f"截止日={_asd.get('as_of')}——月末未到/数据未到,本报告=截至"
            "实际日期的结果(非请求月末的完整结果)")
    elif (_r32_hdr and isinstance(_asd, dict)
          and _asd.get('bare_year_month')):
        lines.append(
            f"- 研究截止日口径: 问句含裸年月 {_asd.get('bare_year_month')} "
            f"但相对回看约束非单一(不按时点化合并,R31 既档口径)——研究"
            f"截止日=快照版本日 {_asd.get('as_of')}(不晚于该年月;该月末"
            "完整结果须待数据覆盖后重跑)")
    if isinstance(_eg_hdr, dict) and _eg_hdr.get('as_of'):
        _c_hdr = _eg_hdr.get('counts') or {}
        lines.append(
            f"- 证据口径(r32): 截止日 {_eg_hdr.get('as_of')} | 源快照 "
            f"{_eg_hdr.get('source_snapshot_id')}(版本日 "
            f"{_eg_hdr.get('source_target_date')}) | 事实: 保留 "
            f"{_c_hdr.get('facts_kept')} / 重建 {_c_hdr.get('facts_rebuilt')}"
            f" / 剔除 {_c_hdr.get('facts_dropped')}+版本 "
            f"{_c_hdr.get('facts_excluded_version')} | 序列剔观测 "
            f"{_c_hdr.get('series_observations_dropped')}"
            + (' | 历史截止视图: 晚观测/晚发布/当时不可得数据版本不入'
               '证据面;历史类比的事后结果已标注(事后≠当时可知,事后≠预测)'
               if _eg_hdr.get('historical_view') else ' | 快照版本日口径'))
    lines.append('- 口径: 三个对照时点=日历点锚(截止日−12月/−3月/最新一期);'
                 '「随后3、6、12个月」=事件后偏移(转折/类比基准日+N月)'
                 '——两类时间含义不同,分记不混同')
    lines.append('- 分工: 表格与数值=引擎确定性面(每格附实际观测日);'
                 '判断文字=Agent 席 reader_map 原文(attribution=ai_inferred,'
                 '经独立语义审查)')
    lines.append('')
    # ── Audit-R26 验收: 数据面缺口三类 → 首页明确标草稿(渲染/阻断共源) ──
    _planned0 = {
        (_eco, _dim)
        for _eco, _rf in (rp.get('regions') or {}).items()
        for _dim in ((_rf.get('dimensions') or {}) or {})}
    _miss_groups = missing_core_groups(pv, _planned0)
    if _miss_groups:
        _mg = '、'.join(f"{g[0]}×{g[1]}" for g in _miss_groups)
        lines.append(f"> ⚠ **草稿(非正式)**: 核心维度组缺数(零 ok 格)——{_mg}。"
                     f"缺数格如实「数据不可得」并随行缺口注记(检索范围"
                     f"披露);补数后重跑转正。正式归档对草稿拒绝"
                     f"(map_core_dimension_missing)。")
        lines.append('')
    # ── Audit-R27 任务1: 当期缺失/未核验 → 首页明确标草稿(同三侧共源) ──
    _has_cur0 = any((a.get('months_before') or 0) == 0
                    for a in (rp.get('point_anchors') or []))
    _cur0 = current_period_groups(pv, _planned0, has_current_anchor=_has_cur0)
    if _cur0['missing']:
        _cg = '、'.join(f"{g[0]}×{g[1]}" for g in _cur0['missing'])
        lines.append(f"> ⚠ **草稿(非正式)**: 必要维度**当期**缺数(当期锚"
                     f"零 ok 格)——{_cg}。按所请求时间点统计覆盖: 同一时点"
                     f"多个指标不能替代另一个时点,历史锚 ok 不补当期缺口;"
                     f"补数后重跑转正。正式归档对草稿拒绝"
                     f"(map_current_period_missing)。")
        lines.append('')
    if _cur0['unverified']:
        _ug = '、'.join(f"{g[0]}×{g[1]}" for g in _cur0['unverified'])
        lines.append(f"> ⚠ **草稿(非正式)**: 必要维度当期值**无法核验**——"
                     f"{_ug}。当期 ok 锚全部未核验(无更晚已证实决议且无"
                     f"证实间隔超决策周期上限——本地日历未收录≠未发生);"
                     f"核验(补录决议实录)后重跑转正。正式归档对草稿拒绝"
                     f"(map_current_period_unverified)。")
        lines.append('')
    # ── Audit-R28 任务2: 当期「过期+未核验」混合 → 首页草稿横幅 ──
    if _cur0.get('stale_mix'):
        _xg = '、'.join(f"{g[0]}×{g[1]}" for g in _cur0['stale_mix'])
        lines.append(f"> ⚠ **草稿(非正式)**: 必要维度当期只有**过期与未"
                     f"核验值的混合**——{_xg}。当期 ok 锚全部为过期或未"
                     f"核验(单一类判定各自遗漏的混合形态): 过期格逐格"
                     f"见⚠标注,未核验格见核验锚注记;补数/核验后重跑"
                     f"转正。正式归档对草稿拒绝(map_current_period_"
                     f"stale_mix)。")
        lines.append('')
    # ── Audit-R28 任务2: 缺官方目标(问句指定官方目标而无官方记录) ──
    try:
        _opr = official_policy_record_face(
            pv, _planned0, rp.get('cutoff'), question=run.get('question'),
            calendar_path=(os.path.join(root, 'config',
                                        'release_calendar.json')
                           if root else None))
    except Exception:
        _opr = {'rows': [], 'gaps': []}
    if _opr['gaps']:
        _og = '、'.join(f"{g['label']}({g['metric_id']})" for g in
                        _opr['gaps'])
        # Audit-R32 任务2: 「问现行官方目标×只有待生效公告」=行级缺口与
        # 首页草稿同判——文案分记(待生效≠无实录;待生效值不得冒充现值)
        _pend = [g for g in _opr['gaps']
                 if g.get('gap') == 'current_target_missing_evidence']
        _nogap = [g for g in _opr['gaps']
                  if g.get('gap') != 'current_target_missing_evidence']
        _segs = []
        if _nogap:
            _segs.append(
                '、'.join(f"{g['label']}({g['metric_id']})" for g in _nogap)
                + ': 日历无政策决议/维持实录条目,序列面决议/生效日亦不可推,'
                  '现值无官方口径可依(不以市场序列值冒充宣布目标);补录官方'
                  '决议实录后重跑转正')
        if _pend:
            _p0 = _pend[0]
            _pn = str(_p0.get('note') or '')
            _pdetail = ('研究时点 ' + _pn.split('研究时点 ', 1)[1].split(';', 1)[0]
                        if '研究时点 ' in _pn else
                        f"待生效目标 {_p0.get('pending_target')}"
                        f"(生效日 {_p0.get('pending_effective_on')})")
            _segs.append(
                '、'.join(f"{g['label']}({g['metric_id']})" for g in _pend)
                + f": **当前官方政策目标缺证(仅有待生效公告)**——{_pdetail};"
                  '待生效值不得写成当时已生效的官方目标,不以市场序列值'
                  '冒充宣布目标;生效日之后重跑,或改问「已公布待生效决定」'
                  '转正')
        lines.append(f"> ⚠ **草稿(非正式)**: **缺官方政策目标**——"
                     f"{'; '.join(_segs)}。正式归档对草稿拒绝"
                     f"(map_official_target_missing)。")
        lines.append('')
    _sparse_groups = sparse_anchor_groups(pv, _planned0)
    if _sparse_groups:
        _gg = '、'.join(f"{g[0]}×{g[1]}" for g in _sparse_groups)
        lines.append(f"> ⚠ **草稿(非正式)**: 必要维度锚覆盖不足(ok 锚<2 且"
                     f"空锚无经证实延误依据)——{_gg}。「仅存最新单点」不构成"
                     f"三时点对照满足;补数后重跑转正。正式归档对草稿拒绝"
                     f"(map_anchor_coverage_insufficient)。")
        lines.append('')
    # ── Audit-R26 任务2: 必要维度只剩确证过期值 → 首页明确标草稿 ──
    _stale_groups = stale_only_groups(pv, _planned0)
    if _stale_groups:
        _sg = '、'.join(f"{g[0]}×{g[1]}" for g in _stale_groups)
        lines.append(f"> ⚠ **草稿(非正式)**: 必要维度只剩确证过期值——{_sg}。"
                     f"过期值按统计期末/政策最后确认纪律确证(逐格见⚠过期"
                     f"标注与末观测日);补数后重跑转正。正式归档对草稿拒绝"
                     f"(map_core_dimension_stale)。")
        lines.append('')

    # 一句总判断
    lines += ['## 一句总判断', '', str(rm.get('headline_conclusion') or
                                      '(缺席——attach 契约应已拦截)'), '']
    _trio0 = rp.get('us_rates_trio') or {}
    if _trio0.get('chg_bp_12m') is not None:
        lines.append(f"> 年度判断的同窗年度美债分解: "
                     f"{_trio0.get('decomposition_12m')}"
                     f"(窗口 {(_trio0.get('window_12m') or {}).get('from')}"
                     f"..{(_trio0.get('window_12m') or {}).get('to')};"
                     f"月度窗另列见下文三利率分解节)")
        lines.append('')

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
        hindsight = (c.get('vintage_semantics') or '').startswith('事后回顾')
        for a in anchors:
            v = (c.get('anchors') or {}).get(a) or {}
            if v.get('status') != 'ok':
                cb = v.get('calendar_blocked_observation')
                vals.append(f'数据不可得(停摆延误,最早可见'
                            f'{v.get("calendar_first_publish")})' if cb
                            else '数据不可得')
                continue
            obs = str(v.get('observation_date'))[:7]
            mark = 'Δ事后回顾 ' if hindsight else ''
            if v.get('freshness') == 'stale':
                if v.get('freshness_basis') == 'policy_confirmation':
                    stale = (f"⚠过期:政策最后确认"
                             f"{v.get('policy_confirm_date')}"
                             f"(已有更晚已证实决议而数据未反映)")
                else:
                    stale = (f"⚠过期:末观测{v.get('observation_date')}"
                             f"(滞后{v.get('freshness_lag_days')}天>"
                             f"{v.get('freshness_window_days')}天窗口)"
                             # R26 任务2: 统计期末口径独立成组(括号对完整,
                             # 末观测四要素token保持连续)
                             + (f"(统计期末{v.get('freshness_period_end')}后"
                                f"{v.get('freshness_period_lag_days')}天>"
                                f"{v.get('freshness_window_days')}天已批准窗口)"
                                if v.get('freshness_period_end') else ''))
            elif v.get('freshness') == 'unverified':
                # Audit-R27 任务1: 未核验(≠过期)——无更晚已证实决议且
                # 无证实间隔超决策周期上限,现值是否仍有效无法核验。
                stale = (f"⚠未核验:最后确认{v.get('policy_confirm_date')}"
                         f"后{v.get('unconfirmed_span_days')}天无已证实"
                         f"决议(超决策周期上限"
                         f"{v.get('decision_cycle_bound_days')}天,本地日历"
                         f"未收录≠未发生)")
            else:
                stale = ''
            if v.get('value_kind', '').startswith('level'):
                yoy = v.get('derived_yoy_pct')
                if yoy is not None:
                    vals.append(f"{mark}{_fmt_val(v.get('value'))}"
                                f'(同比≈{yoy:g}%,观测{obs}{stale})')
                elif v.get('yoy_status') == 'no_same_period_base':
                    lv = v.get('latest_valid_yoy') or {}
                    extra = (f";最近有效同比≈{lv.get('yoy_pct'):g}%@"
                             f"{str(lv.get('observation_date'))[:7]}"
                             if lv.get('yoy_pct') is not None else '')
                    vals.append(f"{mark}{_fmt_val(v.get('value'))}"
                                f'(同比不可得: 缺基期{extra},观测{obs}{stale})')
                else:
                    vals.append(f"{mark}{_fmt_val(v.get('value'))}"
                                f'(观测{obs}{stale})')
            else:
                vals.append(f"{mark}{_fmt_val(v.get('value'))}"
                            f'(观测{obs}{stale})')
        eco = c.get('region') or ''
        # Audit-R23 收口(NIT-4): 口径注自身已含指标名时不再叠套
        # 「制造业PMI(月频)」→ 不渲染成「制造业PMI(制造业PMI(月频))」
        _dn, _fn = c.get('display_name') or '', c.get('face_note') or ''
        _fn_core = _fn.split('(')[0].strip()
        _metric_cell = (f"{_dn}{_fn[len(_fn_core):].strip()}"
                        if _fn_core and _fn_core in _dn
                        else f"{_dn}({_fn})")
        lines.append(f"| {eco} | {c.get('dimension')} | "
                     f"{_metric_cell} | "
                     + ' | '.join(vals) + f" | {c.get('unit')} |")
    for ab in pv.get('absent') or []:
        lines.append(f"| {ab.get('region')} | {ab.get('dimension')} | "
                     f"{ab.get('display_name')} | " + ' | '.join(['数据不可得']
                     * len(anchors)) + ' | — |')
    lines.append('')
    # ── Audit-R27 任务1: 按时点统计覆盖(组级 ok 计数逐锚披露) ──
    if anchors:
        _cov_cells = []
        for _al in anchors:
            _okg = set()
            for c in pv.get('cells') or []:
                va = (c.get('anchors') or {}).get(_al) or {}
                if va.get('status') == 'ok':
                    _okg.add((c.get('region'), c.get('dimension')))
            _cov_cells.append(f"{_al}={len(_okg)}/{len(_planned0)}组ok")
        lines.append(f"> 按时点统计覆盖(组级——同一时点多个指标不能替代"
                     f"另一个时点,逐锚分开计数): {';'.join(_cov_cells)}。")
        lines.append('')
    lines.append('> 缺数格说明(检索范围+影响): ')
    for ab in pv.get('absent') or []:
        lines.append(f"> - {ab.get('note')}")
    for g in rp.get('dimension_gaps') or []:
        lines.append(f"> - {g.get('note')}")
    lines.append('')
    # ── Audit-R26 任务2: 逐组覆盖与实际数据来源(每指标: 三锚状态+最新
    #    一期统计期末+发布日期(推定基准)+来源=注册表权威采集器)──
    _reg_src = {}
    try:
        _reg_p = os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))),
            'config', 'metric_registry.json')
        with open(_reg_p, encoding='utf-8') as _rf:
            for _m in (json.load(_rf).get('metrics') or []):
                _reg_src[_m.get('metric_id')] = _m.get('source')
    except (OSError, ValueError):
        pass
    lines += ['## 逐组覆盖与实际数据来源', '',
              '| 地区×维度 | 指标 | ' + ' | '.join(anchors)
              + ' | 统计期末 | 发布日期 | 来源 |',
              '|---|---|' + '---|' * (len(anchors) + 3)]
    for c in rows:
        _cov = []
        for a in anchors:
            v = (c.get('anchors') or {}).get(a) or {}
            if v.get('status') == 'ok':
                _cov.append('⚠过期' if v.get('freshness') == 'stale'
                            else ('⚠未核验'
                                  if v.get('freshness') == 'unverified'
                                  else 'ok'))
            elif v.get('calendar_blocked_observation'):
                _cov.append('停摆延误')
            else:
                _cov.append('不可得')
        _lv = (c.get('anchors') or {}).get('最新一期') or {}
        _pe = _lv.get('period_end') or '—'
        _pd = (_lv.get('publication_date') or '—') + \
            (f"({_lv.get('publication_basis')})"
             if _lv.get('publication_basis') and
             _lv.get('publication_date') else '')
        _src = _reg_src.get(c.get('metric_id')) or c.get('source') or '—'
        lines.append(f"| {c.get('region')}×{c.get('dimension')} | "
                     f"{c.get('display_name')} | " + ' | '.join(_cov)
                     + f" | {_pe} | {_pd} | {_src} |")
    for ab in pv.get('absent') or []:
        lines.append(f"| {ab.get('region')}×{ab.get('dimension')} | "
                     f"{ab.get('display_name')} | 不可得 | 不可得 | 不可得 "
                     f"| — | — | 序列缺席 |")
    lines.append('')
    lines.append('> 口径: 覆盖=三锚格状态(ok/⚠过期=确证过期仍如实显示末观测'
                 '/⚠未核验=无更晚已证实决议且间隔超决策周期上限,现值有效'
                 '性无法核验/不可得/停摆延误=日历实录证实的延误);统计期末='
                 '月频观测月末/季频观测季季末(发布滞后自期末起算);发布日期'
                 '=日历实录优先+推定规则兜底(括注基准);来源=注册表权威'
                 '采集器。')
    lines.append('')

    # ── Audit-R22 任务4: 首页三件之三——证据最充分传导速览(证据分排序:
    # 区分指标观测在场的环数;全文详版见「证据最充分的传导机制」节) ──
    _chains = rm.get('transmission') or []
    _cut0 = str(rp.get('cutoff') or '')
    _scored = []
    for _i, _ch in enumerate(_chains):
        _sc = sum(1 for _lk in (_ch.get('links') or [])
                  if _distinguishing_obs(rj, _cut0,
                                         _lk.get('distinguishing_metric')))
        _scored.append((_sc, -len(_ch.get('links') or []), _i, _ch))
    _scored.sort(key=lambda t: (-t[0], t[1], t[2]))
    if _scored and _scored[0][0] > 0:
        _best = _scored[0][3]
        lines += ['## 证据最充分的传导(首页速览)', '']
        lines.append(f"**{_best.get('chain_name') or _best.get('name') or '传导链'}**"
                     f"(区分指标观测在场 {_scored[0][0]}"
                     f'/{len(_best.get("links") or [])} 环——按引擎面证据分排序,'
                     '竞争链全文见后)')
        _flow = []
        for _lk in _best.get('links') or []:
            _short = str(_lk.get('observed_fact') or '')
            # Audit-R23 任务4: 整句入链不截断——原 [:40] 把数字拦腰截断
            # (如「美国CPI同比 2.434→4.」),指标名/数字/单位须完整。
            _flow.append(_short.split('。')[0])
        lines.append('')
        lines.append('→ '.join(f'**{t}**' for t in _flow if t))
        lines.append('')
        lines.append('每环的因果假设/竞争解释/区分指标与已有观测——'
                     '见后文传导图节与「主解释 vs 竞争解释」对质表。')
        lines.append('')

    # 政策四分面(R21 任务2: 政策目标/贷款报价/隔夜市场均值分开标明;
    # 决议日/生效日/市场观测日/统计窗口终点四日期分记)
    pol_rows = [c for c in rows if c.get('policy_face')]
    if pol_rows:
        lines += ['## 政策口径四分面(目标/报价/市场均值分列;四日期分记)', '']
        lines.append('| 地区 | 指标 | 口径 | 锚 | 值 | 决议/公布日 | 生效日 | '
                     '市场观测日 | 统计窗口结束日 |')
        lines.append('|---|---|---|---|---|---|---|---|---|')
        for c in pol_rows:
            pf = c['policy_face']
            for a in anchors:
                v = (c.get('anchors') or {}).get(a) or {}
                if v.get('status') != 'ok':
                    continue
                pdd = v.get('policy_dates') or {}
                dnote = pdd.get('decision_note')
                dtxt = (f"{pdd.get('decision')}({dnote})" if dnote
                        else (pdd.get('decision') or '—'))
                if pdd.get('effective') and not pdd.get('decision') \
                        and pf.get('decision_kind') == 'boj_history':
                    dtxt = '未核验(实录表无该值变更月,不以回推造日期)'
                # Audit-R27 任务1: 「距离上次调整过了多久」可核——生效日
                # 附距研究截止天数(序列值变更日=生效日,数据面语义)。
                _eff = pdd.get('effective')
                _etxt = _eff or '—'
                if _eff and a == '最新一期':
                    try:
                        import datetime as _dt_r27
                        _d_eff = _dt_r27.date.fromisoformat(str(_eff)[:10])
                        _d_as = _dt_r27.date.fromisoformat(
                            str(v.get('as_of'))[:10])
                        _etxt = (f"{_eff}(距研究截止"
                                 f"{(_d_as - _d_eff).days}天)")
                    except ValueError:
                        pass
                mnote = pdd.get('market_note')
                mtxt = (f"{pdd.get('market_observation')}({mnote})" if mnote
                        else (pdd.get('market_observation') or '—'))
                lines.append(
                    f"| {c.get('region')} | {c.get('display_name')} | "
                    f"{pf.get('face')} | {a} | {_fmt_val(v.get('value'))} | "
                    f"{dtxt} | "
                    f"{_etxt} | "
                    f"{mtxt} | "
                    f"{pdd.get('stat_window_end') or '—'} |")
        lines.append('')
        lines.append('> 注: 决议日≠生效日时两日分记(Fed 事后次日生效: 2026-09 '
                     '决议 09-16→生效 09-17;2025-12 决议 12-10→生效 12-11;'
                     '2022-07 决议 07-27→生效 07-28,七月末上限 2.50;ECB '
                     '决议后首个周三生效: 2026-09 决议 09-10→生效 09-16;'
                     'PBOC 逆回购中标价公布即时生效;BoJ 决议日只认实录表'
                     '(BOJ_DECISION_HISTORY: 2024-03 决议 03-19→生效 03-21,'
                     '表外生效日如实「决议日不可推」))。序列值变更日=生效日,'
                     '决议日由央行公告惯例自生效日回推(DFEDTARU/DFEDTARL/'
                     'DFF 一族;ECB_MRO/ECB_DFR 观测日全为周三=生效日)。'
                     '「—」=该口径无此日期(如隔夜市场月均无决议日),如实'
                     '缺席不以别日冒充;LPR 为报价基准(每月20日公布)与政策'
                     '操作目标分列。市场观测日=配对市场序列(决议序列锚窗内'
                     '最新观测)——决议与市场观测不同日时两日分记,不以决议日'
                     '冒充市场观测日。')
        # ── Audit-R28 任务2: 政策官方记录面(决议/生效/维持/距上次调整) ──
        # 官方记录独立于序列面在场——宣布值口径序列缺席(如 JP_POLICY_
        # TARGET registry_absent)时,官方决议实录仍可回答「目标水平/
        # 距上次调整」;记录缺席且序列惯例不可推=缺口(首页草稿横幅)。
        try:
            _opr2 = official_policy_record_face(
                pv, _planned0, rp.get('cutoff'),
                question=run.get('question'),
                calendar_path=(os.path.join(root, 'config',
                                            'release_calendar.json')
                               if root else None))
        except Exception:
            _opr2 = {'rows': [], 'gaps': []}
        if _opr2['rows']:
            lines += ['', '**政策官方记录面(日历实录: 决议/生效/最近维持/'
                          '距上次调整)**', '',
                      '| 地区 | 官方目标 | 待生效 | 最近决议日 | 生效日 | '
                      '最近确认维持 | 核验覆盖截止 | 距上次调整(按生效日) | '
                      '距决议 | 距维持 | 溯源 |',
                      '|---|---|---|---|---|---|---|---|---|---|---|']
            for r in _opr2['rows']:
                _rec = (r.get('records') or [{}])[0]
                _pend = ('—' if not r.get('pending_target') else
                         f"{_fmt_val(r.get('pending_target'))}@"
                         f"{r.get('pending_effective_on')}(待生效)")
                _tgt = (_fmt_val(r.get('official_target'))
                        if not r.get('current_target_missing_evidence')
                        else '缺证(仅有待生效公告)')
                lines.append(
                    f"| {r['label']} | {_tgt}"
                    f" | {_pend}"
                    f" | {r.get('decision') or '—'} | "
                    f"{r.get('effective') or '—'} | "
                    f"{r.get('last_maintenance') or '—'} | "
                    f"{r.get('confirmed_through') or '—'} | "
                    f"{r.get('days_since_adjustment')}"
                    f"天 | {r.get('days_since_decision')}天 | "
                    f"{r.get('days_since_maintenance') or '—'}天 | "
                    f"{_rec.get('entry_id')}({_rec.get('basis')}) |")
                if r.get('current_target_missing_note'):
                    lines.append(f"  - ⚠ {r['label']}: "
                                 f"{r['current_target_missing_note']}")
            lines.append('')
            lines.append('> 注: 距上次调整**按生效日**计算(目标水平自生效'
                         '日起实际执行;决议日是公告面,两日分记)。确认维持'
                         '不改变目标水平,但刷新核验覆盖截止(R28 任务2: '
                         '确认维持也更新核验日期)。**待生效**(Audit-R30 '
                         '任务2): 研究时点早于生效日的已公告决议——当前'
                         '官方目标仍为旧值(无已生效决议在档则如实空缺),'
                         '新目标自生效日起才入「官方目标」列(09-24 切换'
                         '口径)。官方记录与四分面序列值互核: 记录目标与'
                         '序列现值冲突时以缺口/过期纪律另判,不以任一面'
                         '静默覆盖。')
        # 政策一年窗路径(R21 任务2: 先降后升净零一类路径须整窗可复算)
        for c in pol_rows:
            wp = c.get('policy_window_path')
            if not wp:
                continue
            ev = wp.get('events') or []
            ev_txt = (';'.join(f"{e.get('date')}: {e.get('from')}→"
                               f"{e.get('to')}({e.get('delta_bp'):+d}bp)"
                               for e in ev) or '窗内无变动')
            lines.append(f"- **政策一年窗路径** {c.get('display_name')}: "
                         f"窗 {wp.get('window')[0]}..{wp.get('window')[1]},"
                         f"变动点 {ev_txt},净变动 "
                         f"**{wp.get('net_bp'):+d}bp**"
                         f"({wp.get('window_start_value')}→"
                         f"{wp.get('window_end_value')})。"
                         f"{wp.get('note')}")
            # Audit-R22 任务2: 事件行补决议日→生效日间隔(逐事件可核)
            for e in ev:
                if e.get('decision_date'):
                    lines.append(
                        f"  - 事件 {e.get('date')}(生效): 决议日 "
                        f"{e.get('decision_date')}→生效日 {e.get('date')}"
                        f"({e.get('decision_note') or '决议→生效分记'})")
        # ── Audit-R22 任务2: 跨国政策事件簇(同一事件合并计数) ──
        pec = rp.get('policy_event_clusters') or {}
        if pec.get('clusters'):
            lines += ['', '**跨国政策事件簇(同一事件的跨国信号合并)**', '',
                      pec.get('basis') or '', '',
                      '| 簇 | 决议日区间 | 地区 | 事件(决议→生效,Δbp) |'
                      ' 跨国同一事件 |', '|---|---|---|---|---|']
            for cl in pec['clusters']:
                ev_txt = ';'.join(
                    f"{e.get('display_name') or e.get('metric_id')} "
                    f"{e.get('date')}→{e.get('effective_date')}"
                    f"({(e.get('delta_bp') or 0):+d}bp)"
                    for e in cl.get('events') or [])
                lines.append(
                    f"| {cl.get('cluster_id')} | {cl.get('date_from')}.."
                    f"{cl.get('date_to')} | {'/'.join(cl.get('regions') or [])}"
                    f" | {ev_txt} | "
                    f"{'是' if cl.get('same_event_cross_country') else '否'} |")
            lines.append('')
        pdf = rp.get('policy_doc_facts') or []
        if pdf:
            lines += ['**政策文档事实(公告/纪要发布日)**', '',
                      '| 文档 | 发布日 | 口径 |', '|---|---|---|']
            for d in pdf:
                lines.append(f"| {d.get('title')}({d.get('doc_id')}) | "
                             f"{d.get('published_on')} | {d.get('basis')}: "
                             f"{str(d.get('note') or '')[:80]} |")
            lines.append('')
        lines.append('')

    # 美债三利率共同交易日分解(任务3复算面;R21 任务4: 年度判断=同窗年度
    # 分解打头,月度另列;两窗任一历史不足即显示历史不足不出数)
    trio = rp.get('us_rates_trio') or {}
    if trio.get('status') == 'ok':
        w = trio.get('window') or {}
        lines += ['## 美债三利率分解(共同交易日复算)', '']
        if trio.get('chg_bp_12m') is not None:
            wy = trio.get('window_12m') or {}
            lines.append(f"- **年度窗(年度判断同窗)**: 计算窗口 "
                         f"**{wy.get('from')} → {wy.get('to')}**"
                         f"(间隔{wy.get('calendar_days_between')}个日历日),"
                         f"十年期分解 **{trio.get('decomposition_12m')}**"
                         f"(恒等残差 "
                         f"{trio.get('identity_residual_bp_12m'):+g}bp)")
        elif trio.get('window_12m_status') == 'insufficient_history':
            lines.append(f"- 年度窗: **历史不足**——{trio.get('window_12m_note')}")
        lines.append(f"- 月度窗(另列): 计算窗口 **{w.get('from')} → {w.get('to')}**"
                     f"(间隔{w.get('calendar_days_between')}个日历日),"
                     f"十年期分解 **{trio.get('decomposition')}**"
                     f"(恒等残差 {trio.get('identity_residual_bp'):+g}bp,"
                     f"{trio.get('identity_note')})")
        lines.append(f"- 期末水平: 名义 {(_fmt_val((trio.get('levels_at_to') or {}).get('UST_10Y')))}"
                     f" / 实际 {(_fmt_val((trio.get('levels_at_to') or {}).get('TIPS_10Y')))}"
                     f" / 盈亏平衡 {(_fmt_val((trio.get('levels_at_to') or {}).get('BEI_10Y')))}"
                     f" (%)")
        lines.append('- 三序列各自最新观测日不同时,以**共同交易日**为准——'
                     '分量与名义才可逐位对账(读者可核)。')
        lines.append('')
    elif trio.get('status') == 'insufficient_history':
        lines += ['## 美债三利率分解(共同交易日复算)', '',
                  f"- **历史不足**: {trio.get('note')}", '']
    elif trio.get('status') == 'absent':
        lines += ['## 美债三利率分解(共同交易日复算)', '',
                  f"- 缺席: {trio.get('note')}", '']

    # 关键资产月度变化(任务3: 正文数字必须带可复算窗口)
    am = rp.get('asset_moves') or {}
    if am.get('status') == 'ok':
        lines += ['## 关键资产月度变化(含计算窗口)', '',
                  f"窗口规则: {am.get('window_rule')}", '',
                  '| 资产 | 计算窗口 | 起→末 | 变化 |', '|---|---|---|---|']
        for r in am.get('rows') or []:
            w = r.get('window') or {}
            lines.append(f"| {r.get('metric_id')} | {w.get('from')}.."
                         f"{w.get('to')} | {_fmt_val(r.get('from_value'))}→"
                         f"{_fmt_val(r.get('to_value'))} | "
                         f"{r.get('chg_pct'):+g}%({r.get('chg_abs'):+g}) |")
        if am.get('absent'):
            lines.append('')
            lines.append(f"> 缺席(序列或窗口端点不可得): "
                         f"{', '.join(map(str, am['absent']))}")
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
            dm = lk.get('distinguishing_metric')
            dobs = _distinguishing_obs(rj, str(rp.get('cutoff') or ''), dm)
            lines.append(f"   - 能区分解释的指标: {dm}"
                         + (f" {dobs}" if dobs else
                            '(引擎面无该序列观测——如实缺席)'))
        lines.append('')

    # ── Audit-R22 任务4: 主解释 vs 竞争解释对质表(同一指标的不同预期/
    # 已有观测/判断;预期分立且观测在场才可裁,证据不足=尚不能区分) ──
    _fo_rows = []
    for ch in rm.get('transmission') or []:
        for lk in ch.get('links') or []:
            if not lk.get('competing_explanation'):
                continue                      # 无竞争解释=非对质面
            dm = lk.get('distinguishing_metric')
            dobs = _distinguishing_obs(rj, str(rp.get('cutoff') or ''), dm)
            mp_, cp_ = lk.get('main_predicts'), lk.get('competing_predicts')
            if mp_ and cp_ and dobs:
                verdict = lk.get('face_off_verdict') or '尚不能区分'
            else:
                verdict = '尚不能区分'
            _fo_rows.append((dm, mp_, cp_, dobs, verdict))
    if _fo_rows:
        lines += ['## 主解释 vs 竞争解释(对质表)', '',
                  '| 区分指标 | 主解释预期 | 竞争解释预期 | 已有观测'
                  ' | 判断 |', '|---|---|---|---|---|']
        for dm, mp_, cp_, dobs, verdict in _fo_rows:
            lines.append(f"| {dm or '—'} | "
                         f"{mp_ or '(预期未写明——如实缺席)'} | "
                         f"{cp_ or '(预期未写明——如实缺席)'} | "
                         f"{dobs or '(引擎面无观测)'} | {verdict} |")
        lines.append('')
        lines.append('> 判断口径: 预期分立(两解释对同一指标给出不同预期)'
                     '且引擎面观测在场才可裁;观测缺席或预期未分立='
                     '**尚不能区分**(诚实缺省,不以单侧证据裁)。')
        lines.append('')

    # 情景面(任务3: 两个情景的触发与失效方向分别展示——L4 结构面渲染)
    l4sc = ((judgment_doc or {}).get('l4') or {}).get('scenarios') or []
    if l4sc:
        lines += ['## 情景(触发与失效方向分别验证)', '']
        lines.append('| 情景 | 角色 | 资产方向 | 触发条件(期限) | '
                     '失效方向(证伪阈值) | 证伪指标 |')
        lines.append('|---|---|---|---|---|---|')
        for sc in l4sc:
            rws = sc.get('rows') or {}
            ad = rws.get('asset_direction') or {}
            trig = rws.get('trigger') or {}
            fals = rws.get('falsification') or {}
            svars = '；'.join(str(x) for x in
                             (rws.get('sensitive_variables') or []))
            dir_txt = ad.get('direction') or '—'
            if svars:
                dir_txt += f"({svars})"
            trig_txt = trig.get('condition') or '—'
            if trig.get('deadline'):
                trig_txt += f"(期限 {trig.get('deadline')})"
            lines.append(
                f"| {sc.get('id')} | {sc.get('role') or '—'} | "
                f"{dir_txt} | {trig_txt} | "
                f"{fals.get('threshold') or '—'} | "
                f"{fals.get('metric_id') or '—'} |")
        lines.append('')
        lines.append('> 注: 两情景方向互补;触发=条件到达即验证,失效=证伪'
                     '阈值到达即推翻——不对称结果须如实更新判断(假设非预测,'
                     '条件式表述)。')
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

    # ── Audit-R23 任务4: 同轮事件并项——同维度且观测窗重叠的转折=同一
    # 轮事件(如 2026-05 中美再通胀信号: CN_PPI 与 CPI 窗口重叠),并为一
    # 项计;并项后不足三项时由引擎按候选面证据分补选独立转折(窗口不与
    # 已用重叠+维度不同,|Δ| 降序)——补选行明确标注「引擎补选·非判断
    # 席」,不冒充判断。判断席原转折全数保留在 agent_judgment 档。 ──
    def _t_ym(t):
        return str(t.get('date') or '')[:7]

    # R23 任务4 并项 + R24 任务4 补选交还: 并项/补选逻辑与判断契约
    # (judgment_contract check17)同源调用本纯函数——席位交还面与读者
    # 表逐项一致;补选行的「谁先变/跟进或背离」优先取判断席交还的
    # turning_supplement(无则如实标「判断席未述」)。
    episodes, _engine_picks = turning_merge_and_picks(
        rm.get('turnings') or [], cand)
    _supp24 = {(str(s.get('metric_id')), str(s.get('to_ym'))): s
               for s in (rm.get('turning_supplement') or [])
               if isinstance(s, dict)}
    _merged_note_seen = False
    for ep in episodes:
        ts_ = sorted(ep['turnings'], key=lambda t: str(t.get('date') or ''))
        merged = len(ts_) > 1
        mid_txt = '+'.join(sorted({str(t.get('metric_id'))
                                    for t in ts_}))
        if merged:
            mid_txt += '(同轮事件并项)'
            _merged_note_seen = True
        vals_txt = ';'.join(
            f"{_fmt_val(t.get('value_before'))}→"
            f"{_fmt_val(t.get('value_after'))}" for t in ts_)
        _wins = []
        for t in ts_:
            cc = cand_by_key.get((t.get('metric_id'), _t_ym(t)))
            w_ = (f"{cc.get('from_ym')}..{cc.get('to_ym')}" if cc
                  else (f"{str(t.get('before_date'))[:7]}..{_t_ym(t)}"
                        if t.get('before_date') else '—'))
            if w_ not in _wins:
                _wins.append(w_)
        date_txt = '/'.join(sorted({str(t.get('date')) or '—'
                                    for t in ts_}))
        lines.append(f"| {date_txt} | {mid_txt} | {vals_txt} | "
                     f"{'/'.join(_wins)} | "
                     f"{';'.join(str(t.get('first_mover') or '—') for t in ts_)} | "
                     f"{';'.join(str(t.get('follow_or_diverge') or '—') for t in ts_)} |")
    # 并项后不足三项 → 引擎按现有证据补选独立转折(确定性,可核):
    # 窗口不与已用重叠为硬条件(独立事件);优先不同维度,同维度不同窗
    # 亦可为独立轮次(候选面维度并不仅两三种);|Δ| 降序。
    # Audit-R24 任务4: 补选项交还判断席——席位在 reader_map.
    # turning_supplement 逐项写明 谁先变/跟进或背离(月频分辨率界限/
    # 缺哪项跨国证据如实注记),渲染面优先取席位交还面,无则如实标
    # 「判断席未述」(旧档兼容;新代码面起由 check17 强制)。
    for c in _engine_picks:
        sn = _supp24.get((str(c.get('metric_id')), str(c.get('to_ym'))))
        _fm24 = str((sn or {}).get('first_mover') or '').strip()
        _fd24 = str((sn or {}).get('follow_or_diverge') or '').strip()
        _res24 = str((sn or {}).get('resolution_note') or '').strip()
        _gap24 = str((sn or {}).get('evidence_gap') or '').strip()
        _fm_txt = _fm24 or '—(判断席未述此转折)'
        _fd_txt = _fd24 or '—'
        if sn and (_res24 or _gap24):
            _fd_txt += ('(分辨率/证据: '
                        + '；'.join(x for x in (_res24, _gap24) if x) + ')')
        lines.append(f"| {c.get('to_ym')}(引擎补选·非判断席) | "
                     f"{c.get('metric_id')}({c.get('region')}/"
                     f"{c.get('dimension')},候选面 |Δ| 降序) | "
                     f"{_fmt_val(c.get('value_before'))}→"
                     f"{_fmt_val(c.get('value_after'))} | "
                     f"{c.get('from_ym')}..{c.get('to_ym')} | "
                     f"{_fm_txt} | {_fd_txt} |")
    lines.append('')
    if _merged_note_seen or _engine_picks:
        lines.append('> 并项与补选口径: 同维度且观测窗重叠的转折=同一轮'
                     '事件并为一项(如同一轮五月再通胀的中美信号);并项后'
                     '不足三项时按候选面证据分补选独立转折——窗口不与已'
                     '用重叠为硬条件(独立事件),优先不同维度、再按 |Δ| '
                     '降序,标注「引擎补选·非判断席」——判断席原转折全数'
                     '在 agent_judgment 档,不因渲染并项丢失。Audit-R24 '
                     '任务4: 补选项交还判断席(turning_supplement 逐项'
                     '写明 谁先变/何时/从多少到多少/哪些经济体跟进或背离;'
                     '月频无法判先后写明分辨率,缺跨国证据写明缺哪项)。')
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

    # 关键数字与来源(附发布日期——Audit-R19 任务1;R20: 日历实录条目优先;
    # R22 任务1: 发布批次对账——同批指标可见性整批一致,逐批注记)
    lines += ['## 关键数字与来源(实际观测日+发布日期+发布批次)', '']
    lines.append('| 指标 | 锚 | 值 | 单位 | 实际观测日 | 发布日期(日历实录/规则推定) | 来源 |')
    lines.append('|---|---|---|---|---|---|---|')
    _pub_batches = {}
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
            if 'batch=' in str(rule):
                _pub_batches.setdefault(
                    str(rule).split('batch=')[-1].rstrip(')'), set()).add(
                    f"{c.get('metric_id')}@{str(v.get('observation_date'))[:7]}")
            vin = ('(事后回顾)' if (c.get('vintage_semantics')
                                   or '').startswith('事后回顾') else '')
            lines.append(f"| {c.get('metric_id')} | {a} | "
                         f"{_fmt_val(v.get('value'))}{vin} | {c.get('unit')} | "
                         f"{v.get('observation_date')} | {pub_txt} | "
                         f"{src_txt} |")
    lines.append('')
    if _pub_batches:
        lines.append('> 发布批次对账(batch=同一份官方发布事件,同批指标'
                     '可见性整批一致——同批多指标/一次补发两月按批核): ')
        import release_calendar as _rc2
        for bid, members in sorted(_pub_batches.items()):
            bd = next((x for x in ((_rc2._load_doc() or {})
                                   .get('batches') or [])
                       if x.get('batch_id') == bid), {})
            lines.append(f"> - {bid}: {bd.get('agency')}·{bd.get('release')}"
                         f"(首发 {bd.get('published_on')},补发 "
                         f"{bd.get('backfill_months')} 月)——本报告引用 "
                         f"{', '.join(sorted(members))}")
        lines.append('')
    lines.append('> 修订口径: 标 Δ事后回顾/事后回顾 的值=注册声明最新修订族'
                 '(当时不可见,历史对照只作回顾);未标=采集时点族。历史值'
                 '经过修订就在引用处标明——本表即引用处。')
    lines.append('')

    # 历史类比(匹配区间/判断截止月/事后窗三面分记——Audit-R19 任务4;
    # R20 任务3: 零段时写明检索范围与原因,不以空白交差)
    lines += ['## 历史上结构最像的时期(可验证;≤3段)', '']
    if not (rm.get('history_periods') or []):
        zero_note = rm.get('history_zero_case_note')
        lines.append(f"- **零段类比**——检索范围与原因: {zero_note}"
                     if zero_note else
                     '- **零段类比**——检索范围=四地地图计划指标序列全历史'
                     '(增长/通胀/政策三维在场序列,analog 六维状态类比引擎'
                     '覆盖面);本次未给出类比段(Reader 席未提供零段原因'
                     '注记,如实披露)。')
        lines.append('')
    for h in rm.get('history_periods') or []:
        tag = '(美国类比——锚定美国序列)' if h.get('us_analog') else \
            '(非美国类比——须在样本注记写明锚定序列)'
        lines.append(f"### {h.get('period_label')} {tag}")
        mw = h.get('match_window') or {}
        if mw.get('start_ym') and mw.get('end_ym'):
            lines.append(f"- 匹配区间: {mw.get('start_ym')}..{mw.get('end_ym')}"
                         f"(判断截止月 {h.get('judgment_cutoff_ym') or '—'};"
                         "匹配只用当时已发布数据)")
        lines.append(f"- 相似点: {h.get('similarity')}")
        lines.append(f"- 关键差异: {h.get('difference')}")
        lines.append(f"- 当时同步性(其他经济体): {h.get('other_regions_sync')}")
        # ── Audit-R28 任务3: 地区×维度同步面(引擎确定性,冻结信封)——
        #    逐段核对美中欧日,同步/分化/缺证标签+公布日+数据版本绑定;
        #    判断叙述引用本面可核(缺证项点名,不以相邻维度冒充)。 ──
        try:
            rsf = history_region_sync_face([h], rj, root=root)
            rsp = (rsf.get('periods') or [{}])[0]
        except Exception:
            rsp = {}
        if rsp.get('rows'):
            lines.append('- **地区×维度同步面(引擎确定性——与美国同维'
                         '方向对照;公布日/数据版本随行)**:')
            lines.append('')
            lines.append('  | 维度 | 地区 | 指标 | 锚−3月(观测/公布) | '
                         '截止(观测/公布) | 读数变化 | 同步性 |')
            lines.append('  |---|---|---|---|---|---|---|')
            for r in rsp['rows']:
                if r.get('label_sync') == '缺证':
                    p_txt = c_txt = chg = '—'
                else:
                    p_txt = (f"{r.get('prior_value'):g} @ "
                             f"{r.get('prior_obs')}(公布 "
                             f"{r.get('prior_pub')})")
                    c_txt = (f"{r.get('cutoff_value'):g} @ "
                             f"{r.get('cutoff_obs')}(公布 "
                             f"{r.get('cutoff_pub')})")
                    _u = ('pp' if r['dimension'] == 'policy' else '')
                    chg = (f"{r.get('delta'):+g}{_u}"
                           f"({r.get('direction')})")
                lines.append(
                    f"  | {r['dimension_label']} | {r['region']} | "
                    f"{r['label']}({r['metric_id']}) | {p_txt} | {c_txt} | "
                    f"{chg} | {r['label_sync']}"
                    + (f"——{r.get('reason')}" if r.get('reason') else '')
                    + ' |')
            lines.append('')
            lines.append(f"  > {rsf.get('basis')}。数据版本="
                         '冻结信封最新修订口径(首发值可能略异,修订不可'
                         '回溯,逐行随 vintage 注记)。')
        # ── Audit-R23 任务2: 当时可知面(发布纪律重算,确定性)——同步性
        # 叙述所引数字逐个绑定 指标/观测期/值/首次公布日/来源/修订口径;
        # 晚于截止日才公布的移入事后段(信息截止可核,正文引用须对账)。 ──
        try:
            aof = history_asof_face([h], rj, root=root)
            aop = (aof.get('periods') or [{}])[0]
        except Exception:
            aop = {}
        if aop.get('known'):
            lines.append('- **当时可知面(发布纪律重算——引擎确定性)**:')
            lines.append('')
            lines.append('  | 指标 | 观测期(最新可见) | 值 | 首次公布日'
                         ' | 当时可知? | 来源 | 修订口径 |')
            lines.append('  |---|---|---|---|---|---|---|')
            for r in aop['known']:
                pub_txt = str(r.get('visible_from') or '—')
                if r.get('first_publish') and \
                        r.get('first_publish') != r.get('visible_from'):
                    pub_txt += f"(终值 {r.get('first_publish')})"
                # Audit-R28 任务2: 官方发布时刻随日历实录披露(如 LPR
                # 每月20日 09:00)——各表统一读官方发布时间,推定条目
                # 无时刻如实缺席。
                if r.get('publish_instant'):
                    pub_txt += (f" {r['publish_instant']}"
                                '(官方实录时刻)')
                note_txt = (f";{r.get('note')}" if r.get('note') else '')
                lines.append(
                    f"  | {r.get('label')}({r.get('metric_id')}) | "
                    f"{r.get('obs_month')} | {_fmt_val(r.get('value'))} | "
                    f"{pub_txt}({r.get('pub_basis')}){note_txt} | 是 | "
                    f"{r.get('source') or '—'} | "
                    f"{r.get('revision_note')} |")
            lines.append('')
            lines.append(f"  > 截止月={aop.get('cutoff_ym')}(月末 "
                         f"{aop.get('cutoff_end')});known=可见日≤截止月末"
                         '的最新观测。')
            if aop.get('aftermath'):
                lines.append('- **截止日后才公布/截止后决议(事后段——'
                             '不得充当当时可知)**:')
                lines.append('')
                lines.append('  | 指标 | 观测期 | 值 | 首次发布日 | '
                             '延误/注记 | 来源 |')
                lines.append('  |---|---|---|---|---|---|')
                for r in aop['aftermath']:
                    pub_txt = str(r.get('visible_from')
                                  or r.get('pub_basis') or '—')
                    if r.get('publish_instant'):
                        pub_txt += (f" {r['publish_instant']}"
                                    '(官方实录时刻)')
                    val_txt = _fmt_val(r.get('value'))
                    if r.get('kind') == 'policy_event':
                        val_txt = (f"{_fmt_val(r.get('value_from'))}→"
                                   f"{_fmt_val(r.get('value'))}"
                                   f"(事后政策事件)")
                        pub_txt = str(r.get('obs_date'))
                    lines.append(
                        f"  | {r.get('label')}({r.get('metric_id')}) | "
                        f"{r.get('obs_month')} | "
                        f"{val_txt} | {pub_txt} | "
                        f"{r.get('delay_note') or '—'} | "
                        f"{r.get('source') or '—'} |")
                lines.append('')
            if aop.get('absent'):
                lines.append(f"  > 当时可知面缺席项(序列不在场,不冒充): "
                             f"{', '.join(aop['absent'])}")
                lines.append('')
        ex = h.get('ex_post') or {}
        aym = str(h.get('anchor_ym') or '')
        exp_win = ex_post_windows(aym) if len(aym) == 7 else {}
        lines.append('- 随后结果(事后实际——与当时同步性分开,事后陈述非预测):')
        for k, lbl in (('3m', '随后3个月'), ('6m', '随后6个月'),
                       ('12m', '随后12个月')):
            exp_m = exp_win.get(k)
            exp_txt = f"(锚{aym}+{k[:-1]}月→{exp_m})" if exp_m else ''
            lines.append(f"  - {lbl}{exp_txt}: {ex.get(k)}")
        # Audit-R32 任务1: 历史类比的事后结果明确标注(候选相似期由事后
        # 全窗口数据筛得;其后表现=事后实际,当时不可知,亦非预测)——
        # 只在 r32 证据口径在场的报告上渲染(旧档重渲逐字节不变)
        if isinstance(run.get('evidence_gate'), dict) and \
                (run.get('evidence_gate') or {}).get('as_of'):
            lines.append(
                '  > **事后结果标注**: 候选相似期=事后以全窗口数据筛得'
                '(相似度用到候选期之后的数据);候选期**之后**的经济与资产'
                '表现为事后实际结果——当时不可知,亦非对本次的预测;引用须以'
                '「事后实际」措辞,不得表述为当时可知或预测(纪律17)。')
        sn = h.get('sample_note') or h.get('data_note')
        if sn:
            lines.append(f"- 样本注记: {sn}")
        # ── Audit-R22 任务4 + Audit-R23 任务1: 逐窗并列面(经济指标×资产
        # 表现,确定性复算;与 ex_post 正文同一锚月末→锚+N 月末口径,数字
        # 可逐位对账)。序列源=冻结信封优先/运行快照兜底——无外部快照
        # 仍逐位还原,同名快照端点被改不影响任何行。 ──
        if len(aym) == 7:
            hwf = history_window_face([h], _snap_r, root, rj=rj)
            hwp = (hwf.get('periods') or [{}])[0]
            _any_rows = any((w or {}).get('rows') for w in
                            (hwp.get('windows') or {}).values())
            if _any_rows:
                lines.append('- 逐窗并列(经济指标×资产表现,'
                             '起止期/数值/单位/来源——确定性复算;'
                             '序列源=report.json 冻结信封优先,运行快照'
                             '兜底):')
                for k in ('3m', '6m', '12m'):
                    w = hwp['windows'].get(k) or {}
                    rows_w = w.get('rows') or []
                    if not rows_w:
                        continue
                    lines.append('')
                    lines.append(f"  **随后{k[:-1]}个月窗**"
                                 f"(锚{aym}月末→{w.get('target_ym')}月末):")
                    lines.append('')
                    lines.append('  | 组 | 指标 | 起期 | 起值 | 止期 | 止值 |'
                                 ' 变化 | 单位 | 来源 |')
                    lines.append('  |---|---|---|---|---|---|---|---|---|')
                    for r in rows_w:
                        ch_ = r.get('change')
                        ch_txt = (f"{ch_:+g}{r.get('change_unit')}"
                                  if isinstance(ch_, (int, float))
                                  else ('—(' + str(r.get('note') or '')
                                        + ')' if r.get('note') else '—'))
                        lines.append(
                            f"  | {r.get('group')} | {r.get('label')}"
                            f"({r.get('metric_id')}) | {r.get('from_date')}"
                            f" | {_fmt_val(r.get('from_value'))} | "
                            f"{r.get('to_date')} | "
                            f"{_fmt_val(r.get('to_value'))} | {ch_txt} | "
                            f"{r.get('unit') or '—'} | "
                            f"{r.get('source') or '—'} |")
                if hwp.get('absent'):
                    lines.append('')
                    lines.append(f"  > 并列面缺席项(序列/窗端点不可得,"
                                 f"不冒充): {', '.join(hwp['absent'])}")
                lines.append('')
            else:
                lines.append(f"- 逐窗并列面: **缺席**——{_snap_note or '冻结信封与运行快照均不在场'}"
                             '(经济×资产并列表须 report.json S4 冻结信封'
                             '或运行快照在场,不跨快照取数/不读活树冒充)')
                lines.append('')
        lines.append('')

    # ── Audit-R27 任务4: 随包重放面(完整运行 SHA/原问/裁决链/地图摘要/
    #    一条可执行重放命令)——确定性装配在场事实,零新增生成。 ──
    _run27 = (rj.get('run') or {}) if isinstance(rj, dict) else {}
    _sha27 = str(_run27.get('git_head') or '')
    lines += ['## 重放(随包可执行)', '',
              '- 完整运行 SHA: `%s`(来源 %s;CODE_VERSION.json 印章'
              '可核)' % (_sha27 or '(未记录)',
                         _run27.get('git_head_source') or '—'),
              '- 原问: 本目录 `question_verbatim.txt`(report 段落盘,'
              '字节=run.question)',
              '- 裁决链: `audit/semantic_review/<实录日期>/` 下本 runts '
              '裁决档——REVISE→UPHELD 时**两条记录都在链**(各绑当时 '
              'map_report_sha256),逐档可核',
              '- 地图摘要: 旁挂 `MAP_REPORT.sha256`(本文件 sha256 锚)',
              '- 重放命令(在交付树根执行;产物落新 run 目录,不改本档):',
              '',
              '```',
              'python3 ia_cli.py research-one --stage auto '
              '--question-file <本运行档目录>/question_verbatim.txt',
              '```',
              '']

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
