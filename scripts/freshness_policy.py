#!/usr/bin/env python3
"""IA-P0-2-W2 统一数据时效策略原语(共享纯函数层)。

解决三处规则分叉(W2-DEF-001/002/003):
  - fact_engine.validate_fact 曾忽略注册表freshness,硬编码7/16/92;
  - data_validator(Gate B) 另有一套prefix规则(macro月度枚举表/rate_economy
    一律月度45/未映射默认14),与Gate A/注册表互不一致;
  - observation_date(观测时点)与release_date(发布时点)语义未分离,存在
    以猜测发布日期制造点时可得性证据的风险。

本模块是唯一时效策略来源的消费端原语:
  build_policy(registry)  注册表(已批准政策)→ 逐指标生效窗口表;缺失/非法窗口
                          fail-loud(FreshnessPolicyError),不得静默回退旧硬编码。
  set_policy/policy_for   生产加载路径(fe.load_registry)注入缓存;fe与da消费同一份。
  canonical_anchor_metric 锚点键→注册表指标canonical映射(镜像snapshot_builder
                          构造规则;映射表lazy引sb单一来源,不复制漂移)。
  verify_anchor_identity  调用方info.metric_id仅作交叉核验不作授权:冲突以canonical
                          为准并披露(UNMAPPED/IDENTITY_CONFLICT fail-closed)。
  assess                  三问分离: A已观测? B as_of时点已发布? C是否新鲜?
                          —— B问仅在事实真实携带release_date时作答,缺失=
                          RELEASE_UNKNOWN(如实标注,绝不编造发布日期);

设计契约(IA-P0-2-W2-DEV §6): 纯Python/零网络/零新DB依赖/不循环导入
(本模块不import fact_engine/data_validator/snapshot_builder于模块级;
映射表在函数内lazy引用sb)。不得改写历史快照/报告/回填release_date。

窗口政策审批记录: 见模块级POLICY_APPROVAL(两轮,2026-10-29,含第一轮45/5
依据算术错误的修正过程——月频45会把BEA/EIA系按时发布数据误判过期,
中国日频5未计入春节/国庆8~9天休市簇)。
"""
import json
import os
import re
from datetime import date, datetime

# ══ 政策审批记录(单一事实源,政策矩阵docs/P0_2_W2_FRESHNESS.*与此一致) ══
POLICY_APPROVAL = {
    'approved_at': '2026-10-29',
    'approved_by': '用户(政策所有者),开发会话内两轮决策',
    'rounds': [
        {'round': 1,
         'decisions': ['月频13项=45', '行情与日频风险资产44项=5', '特殊日频BTC=2/DFF=10/SH_PE=10',
                       '政策目标区间DFEDTARU/DFEDTARL=45'],
         'note': '第一轮批准'},
        {'round': 2,
         'decisions': ['月频13项45→60(修正:BEA/EIA/G.17系正常发布滞后可达~60天,45会误判按时数据过期)',
                       '中国大陆日频8项5→10(修正:春节/国庆休市8~9天,5/7天在节后首日必误报);HK 2项维持5',
                       'MARGIN_BAL 7→10(与大陆日频同一休市日历,一致化)'],
         'note': '第二轮修正第一轮推荐依据中的算术错误后复核批准'},
    ],
    'unchanged_no_conflict': ['利率/利差/TIPS/BEI/实际利率/曲线族=7', 'ICSA=16', 'REAL_SHORT=7'],
}

# 旧引擎硬编码窗(IA-P0-2-W2-DEF-001废除项;仅作政策矩阵与测试对照,不再生效)
LEGACY_ENGINE_WINDOWS = {'daily': 7, 'weekly': 16, 'monthly': 92}
# Gate B旧未映射默认诊断值(第三轮P0-4遗留;仅保留为诊断兼容值,非时效认证)
UNMAPPED_LEGACY_DIAGNOSTIC = 14


class FreshnessPolicyError(Exception):
    """注册表时效窗口缺失/非法——fail-loud,不得静默回退任何默认窗口。"""


# ══ 严格日期原语(与fact_engine.parse_iso_date同语义;不import fe避免环) ══
_ISO_DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def _parse_iso_date(s):
    if not isinstance(s, str) or not _ISO_DATE_RE.fullmatch(s):
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


# FIX1-01(IA-P02-W2-DEF-001)严格时点原语: 研究截止/发布时间允许三种合法形态——
# date/datetime实例、完整ISO日期(YYYY-MM-DD)、**完整**ISO时间戳(整体必须合法,
# 先验证整串再提取日期部分)。绝不以[:10]前缀截断把'2026-10-24INVALID'/
# '2026-10-24T08:00:00垃圾'洗白成合法日期。返回date|None。
_ISO_INSTANT_RE = re.compile(
    r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d{1,6})?(Z|[+-]\d{2}:\d{2})?$')


def parse_instant(value):
    """严格时点解析(日期级兼容接口): date→自身; datetime→date部分; str须为
    完整ISO日期或完整ISO时间戳(YYYY-MM-DD[T ]HH:MM:SS[.ffffff][Z|±HH:MM])。
    其余(带任意后缀/前缀空白/部分时间/非字符串)一律None——不得截断救活非法输入。

    FIX2-02注意: 本函数返回date,天然丢失时分秒与UTC偏移——只可用于
    "研究日期/观测日"等日粒度语义;**发布时刻vs研究截止的点时先后判断**
    必须用parse_temporal_value+compare_release_availability(精度保持原语),
    不得先经本函数降精度后再比较(那会把同日08:00截止/20:00发布误判为
    "发布不晚于截止")。"""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        return None
    s = value
    if _ISO_DATE_RE.fullmatch(s):
        try:
            return date.fromisoformat(s)
        except ValueError:
            return None
    if _ISO_INSTANT_RE.fullmatch(s):
        try:
            return datetime.fromisoformat(s.replace('Z', '+00:00')).date()
        except ValueError:
            return None
    return None


# FIX2-02(IA-P02-W2-FIX1-DEF-002)精度保持时点原语: parse_instant返回date,
# 完整时间戳的时分秒与UTC偏移被丢弃——同日"研究截止08:00/发布20:00"经日期
# 比较会被错误判为"发布不晚于截止"。本组原语在parse_instant同一整串验证
# 口径之上**保留精度**再作点时比较,绝不把datetime降级成date后比先后。
_ISO_INSTANT_TZ_RE = re.compile(
    r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d{1,6})?(?P<tz>Z|[+-]\d{2}:\d{2})?$')


def _tv_bad(raw, error):
    return {'ok': False, 'raw': raw, 'date': None, 'precision': None,
            'tz_aware': None, 'utc_offset': None, 'instant': None,
            'error': error}


def _fmt_offset(td):
    """timedelta UTC偏移→'+HH:MM'字符串(整分粒度;ISO偏移无秒级)。"""
    total = int(td.total_seconds())
    sign = '+' if total >= 0 else '-'
    total = abs(total)
    return f"{sign}{total // 3600:02d}:{(total % 3600) // 60:02d}"


def parse_temporal_value(value):
    """精度保持时点解析(FIX2-02): 与parse_instant同一整串验证口径(绝不
    [:10]截断洗白),但**不丢精度**。返回dict:
      ok            解析成功与否(False=非法输入,绝不猜/补/洗白)
      raw           原始输入(原样保留)
      date          日历日期部分(date|None)
      precision     'DATE_ONLY' | 'DATETIME'
      tz_aware      是否携带明确时区(datetime实例/字符串时间戳按tz后缀)
      utc_offset    '+HH:MM'/'Z'→'+00:00'(tz_aware时) | None
      instant       datetime本体(DATETIME时;naive=无时区定义,不得假设时区)
      error         非法原因(ok=False时)
    合法形态: date实例(DATE_ONLY)/datetime实例(DATETIME)/完整ISO日期/
    完整ISO时间戳(T或空格分隔,±HH:MM须带冒号,Z=UTC,时区可省=naive)。"""
    if isinstance(value, bool):
        return _tv_bad(value, f'非日期类型:{type(value).__name__}')
    if isinstance(value, datetime):
        aware = value.tzinfo is not None and value.utcoffset() is not None
        return {'ok': True, 'raw': value, 'date': value.date(),
                'precision': 'DATETIME', 'tz_aware': aware,
                'utc_offset': _fmt_offset(value.utcoffset()) if aware else None,
                'instant': value, 'error': None}
    if isinstance(value, date):
        return {'ok': True, 'raw': value, 'date': value, 'precision': 'DATE_ONLY',
                'tz_aware': False, 'utc_offset': None, 'instant': None,
                'error': None}
    if not isinstance(value, str):
        return _tv_bad(value, f'非字符串/日期类型:{type(value).__name__}')
    s = value
    if _ISO_DATE_RE.fullmatch(s):
        try:
            return {'ok': True, 'raw': s, 'date': date.fromisoformat(s),
                    'precision': 'DATE_ONLY', 'tz_aware': False,
                    'utc_offset': None, 'instant': None, 'error': None}
        except ValueError:
            return _tv_bad(value, f'假日历日期:{s}')
    m = _ISO_INSTANT_TZ_RE.fullmatch(s)
    if m:
        try:
            dt = datetime.fromisoformat(s.replace('Z', '+00:00'))
        except ValueError:
            return _tv_bad(value, f'非法时刻(假日历/时刻越界):{s}')
        tz_sfx = m.group('tz')
        aware = tz_sfx is not None
        return {'ok': True, 'raw': s, 'date': dt.date(), 'precision': 'DATETIME',
                'tz_aware': aware,
                'utc_offset': ('+00:00' if tz_sfx == 'Z' else tz_sfx)
                if aware else None,
                'instant': dt, 'error': None}
    return _tv_bad(value, '非完整ISO日期/时间戳(带后缀/前后缀空白/部分时间/'
                          '无冒号时差)——整串验证,不得截断救活')


def _delta_hours(later, earlier):
    """两个aware时刻的差(later−earlier),人读"+12.5小时"式。"""
    h = (later - earlier).total_seconds() / 3600.0
    return f"{h:+g}小时"


def compare_release_availability(release, as_of):
    """发布时刻 vs 研究截止的统一可得性比较(FIX2-02核心原语;Gate A/Gate B/
    事实引擎共用,不得各自降精度重比)。

    返回{verdict, granularity, release, as_of, detail}:
      RELEASED_BEFORE      发布先于截止,可作点时证据——granularity='INSTANT'
                           (双方aware时刻,绝对先后已证)或'DAY'(跨日,仅证
                           "截止日之前已发布",不证同日内具体时刻先后)
      RELEASED_AFTER       发布晚于截止(NOT_AVAILABLE_AT_AS_OF,硬拒)——
                           INSTANT(绝对时刻已证晚于)/DAY(跨日,任何时区解释
                           下均晚于)
      UNVERIFIED_SAME_DAY  同一名义日且精度不足以证明先后: 按日粒度视为可得
                           (历史兼容,不FAIL既有数据)但**不得认证点时可得**
      UNVERIFIED_TZ        涉及无时区时刻且名义日期相邻: 任何时区解释下先后
                           均可能翻转——同样不认证(不硬拒亦不认证)
      INVALID_RELEASE / INVALID_AS_OF  输入非法(整串验证口径同parse_instant)

    语义(IA-P0-2-W2-FIX2 §5.4):
      A 双aware完整时间戳→转绝对时刻比较,正确处理不同UTC偏移;
      B 双日期级→保留历史日粒度比较并标明DAY(不证明同日时刻先后);
      C 一日期一时间戳→跨日可保守判定;同日=精度不足→UNVERIFIED_SAME_DAY;
      D aware/naive混合或含naive时刻→绝不把naive当UTC/HKT/本机时区:
        名义日期相同→UNVERIFIED_SAME_DAY;相差≥2日(任何±14h时区解释都
        无法翻转先后)→DAY判定并披露时区未定义;相邻→UNVERIFIED_TZ;
      E 非法输入→INVALID_*。
    保守映射契约(§5.5): UNVERIFIED_*不得默认当PASS认证点时可得,亦不得把
    全部既有数据判FAIL——它是"可得但未认证"的显式披露态。"""
    r = parse_temporal_value(release)
    a = parse_temporal_value(as_of)
    out = {'verdict': None, 'granularity': None,
           'release': release, 'as_of': as_of, 'detail': ''}
    if not r['ok']:
        out.update(verdict='INVALID_RELEASE',
                   detail=f"release非法:{r['error']}")
        return out
    if not a['ok']:
        out.update(verdict='INVALID_AS_OF', detail=f"as_of非法:{a['error']}")
        return out
    # A: 双aware完整时间戳→绝对时刻比较(UTC偏移已包含在instant内)
    if r['precision'] == 'DATETIME' and a['precision'] == 'DATETIME' \
            and r['tz_aware'] and a['tz_aware']:
        if r['instant'] <= a['instant']:
            rel_txt = '等于' if r['instant'] == a['instant'] else \
                f"早于(差{_delta_hours(a['instant'], r['instant'])})"
            out.update(verdict='RELEASED_BEFORE', granularity='INSTANT',
                       detail=f"绝对时刻比较: 发布{r['raw']} {rel_txt} 截止{a['raw']}")
        else:
            out.update(verdict='RELEASED_AFTER', granularity='INSTANT',
                       detail=f"绝对时刻比较: 发布{r['raw']} 晚于 截止{a['raw']}"
                              f"(差{_delta_hours(r['instant'], a['instant'])})")
        return out
    # B/C/D: 至少一侧非aware时刻——只能按名义日期作日粒度判断
    tz_undefined = (r['precision'] == 'DATETIME' and not r['tz_aware']) \
        or (a['precision'] == 'DATETIME' and not a['tz_aware'])
    dd = (a['date'] - r['date']).days
    if dd == 0:
        why = '时刻精度不足' if not tz_undefined else '时刻精度不足且时区未定义'
        out.update(verdict='UNVERIFIED_SAME_DAY', granularity='DAY',
                   detail=f"同一名义日{r['date'].isoformat()}: {why},不能证明"
                          f"发布先于研究截止——按日粒度可得(历史兼容),不认证点时可得")
        return out
    if tz_undefined and abs(dd) == 1:
        out.update(verdict='UNVERIFIED_TZ', granularity='DAY',
                   detail=f"名义日期相邻({r['date'].isoformat()} vs "
                          f"{a['date'].isoformat()})且含无时区时刻——任何时区"
                          f"解释下先后均可能,不可证明亦不可硬拒(不认证点时可得)")
        return out
    rel_desc = f"发布{r['date'].isoformat()}" + (f"({r['raw']})" if r['precision'] == 'DATETIME' else '')
    as_desc = f"截止{a['date'].isoformat()}" + (f"({a['raw']})" if a['precision'] == 'DATETIME' else '')
    if dd > 0:
        out.update(verdict='RELEASED_BEFORE', granularity='DAY',
                   detail=f"日粒度比较: {rel_desc} 早于 {as_desc}"
                          + (';涉无时区时刻,按名义日期判定' if tz_undefined else ''))
    else:
        out.update(verdict='RELEASED_AFTER', granularity='DAY',
                   detail=f"日粒度比较: {rel_desc} 晚于 {as_desc}"
                          + (';涉无时区时刻,按名义日期判定' if tz_undefined else ''))
    return out


# ══ 策略构建与缓存 ═══════════════════════════════════════════════

_POLICY = None


def build_policy(registry):
    """注册表metrics → {metric_id: {window,frequency,calendar,basis}}。
    每个条目必须携带正整数max_calendar_lag_days(W2起为已批准生效政策,
    非声明性元数据)——缺失/非法即FreshnessPolicyError点名拒绝。"""
    out = {}
    problems = []
    for m in (registry or {}).get('metrics', []):
        mid = m.get('metric_id')
        fr = m.get('freshness') if isinstance(m.get('freshness'), dict) else None
        w = fr.get('max_calendar_lag_days') if fr else None
        if not isinstance(w, int) or isinstance(w, bool) or w <= 0:
            problems.append(f"{mid}:max_calendar_lag_days={w!r}(须正整数)")
            continue
        freq = m.get('frequency')
        if freq not in ('daily', 'weekly', 'monthly'):
            problems.append(f"{mid}:frequency={freq!r}非法(无法解释时效窗)")
            continue
        out[mid] = {'window': w, 'frequency': freq,
                    'calendar': m.get('calendar'),
                    'source': m.get('source'),   # FIX1-03: 锚点家族↔权威来源绑定用
                    'basis': 'registry(approved)'}
    if problems:
        raise FreshnessPolicyError(
            "W2-FRESHNESS-POLICY-INVALID: 注册表时效窗口不完整/非法 — "
            + "; ".join(problems)
            + " (不得静默回退旧7/16/92硬编码;补全注册表freshness后重试)")
    return out


def set_policy(policy):
    """生产路径(fe.load_registry)注入已构建策略;测试可注入受控策略。"""
    global _POLICY
    _POLICY = policy


# 默认注册表路径(与fact_engine.REGISTRY_PATH同一文件;不import fe避免环,
# 自行推导)。Gate B侧调用方(报告校验/观察器/配置引擎)可能在与fe不同的
# 进程/导入序下使用本模块——策略未被显式注入时惰性自载默认注册表,
# 保证fe与dv消费的始终是同一份已批准政策(fe注入的自定义注册表优先)。
_DEFAULT_REGISTRY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'config', 'metric_registry.json')


def _load_default_policy():
    global _POLICY
    with open(_DEFAULT_REGISTRY_PATH, 'r', encoding='utf-8') as f:
        reg = json.load(f)
    _POLICY = build_policy(reg)
    return _POLICY


def policy_for(metric_id):
    """查当前生效策略;未注入时惰性自载默认注册表(与fe.load_registry同一文件)。
    未注册指标返回None(消费方必须显式处理,不得默认任意窗口)。"""
    if _POLICY is None:
        _load_default_policy()
    return _POLICY.get(metric_id)


def current_policy():
    return _POLICY


# ══ 锚点键→注册表指标 canonical映射(镜像snapshot_builder构造规则) ══
# 映射表lazy引用sb模块级单一来源(_GLOBAL_OLD_ID/_CHINA_LABEL/_RATE_OLD_NAME),
# 不复制副本防两处漂移;china特殊键在sb内为函数局部表,此处镜像并经
# test_p02_w2对sb.build_anchors真实输出的全键回环锁定。

_GM_FIELDS = ('close', 'week_chg', 'mtd_chg', 'ytd_chg', 'pct_change', 'change', 'high', 'low')
_CN_DATA_FIELDS = ('close', 'week_chg', 'ytd_chg')
_MACRO_FIELDS = ('value', 'prev', 'mom_chg', 'mom_pct', 'yoy_chg', 'yoy_pct')
_CN_SPECIAL = {'china.ah_premium.close': 'HSAHP',
               'china.turnover.sh_amount_billion': 'SH_AMOUNT',
               'china.turnover.sz_amount_billion': 'SZ_COMPONENT_AMOUNT',
               'china.turnover.total_amount_billion': 'CN_TOTAL_TURNOVER',
               'china.turnover.volume_billion': 'CN_TOTAL_TURNOVER',
               'china.southbound.net_buy': 'SB_FLOW',
               'china.margin.balance': 'MARGIN_BAL',
               'china.valuation.pe': 'SH_PE'}
_DERIVED_KEYS = {'macro.derived.REAL_10Y': 'REAL_10Y',
                 'macro.derived.REAL_5Y': 'REAL_5Y',
                 'macro.derived.HY_IG_DIFF': 'HY_IG_DIFF',
                 'rate_economy.fed_funds_futures.implied_rate': 'ZQ_IMPLIED_AVG'}
_CUR_RATE = {'DFF', 'DFEDTARU', 'DFEDTARL'}
_REAL_ECO_FIELDS = ('value', 'prev_value')

# FIX1-03(IA-P02-W2-DEF-003)锚点家族↔注册表权威来源绑定: 指标在注册表中存在
# ≠该指标可从任意采集通道生成。每个锚点家族只授权其对应权威来源的指标
# (依据sb.build_anchors实际构造分支+metric_registry.source字段):
#   global_market → global_market_collector(yfinance行情族)
#   china_index/china_special → china_market_collector
#   macro → macro_collector(NFP_MOM_K虽source=macro_collector但asset_class=
#     macro_count_derived,sb从不为它发macro.data锚点,不在授权内)
#   derived → fact_engine(derived)(REAL_10Y/REAL_5Y/HY_IG_DIFF/ZQ_IMPLIED_AVG)
#   rate_current → rate_expectations(DFF/DFEDTARU/DFEDTARL)
#   rate_real_economy → macro_collector(经_RATE_OLD_NAME显式兼容映射的宏观事实,
#     sb取macro事实挂旧键名,单一来源仍是macro_collector)
#   futures_curve → rate_expectations(ZQ_F1_PRICE)/fact_engine(derived)
#     (ZQ_IMPLIED_AVG,sb从快照曲线直接构造)
# 匹配失败→SOURCE_MISMATCH→UNVERIFIED(身份不可认证,fail-closed)。
_FAMILY_SOURCES = {
    'global_market': frozenset({'global_market_collector'}),
    'china_index': frozenset({'china_market_collector'}),
    'china_special': frozenset({'china_market_collector'}),
    'macro': frozenset({'macro_collector'}),
    'derived': frozenset({'fact_engine(derived)'}),
    'rate_current': frozenset({'rate_expectations'}),
    'rate_real_economy': frozenset({'macro_collector'}),
    'futures_curve': frozenset({'rate_expectations', 'fact_engine(derived)'}),
}


def _source_mismatch_note(pol, mid, family):
    """指标已注册但注册表权威来源不属于该锚点家族→SOURCE_MISMATCH说明
    (canonical_anchor_metric返回mid=None,verify_anchor_identity判UNVERIFIED)。"""
    allowed = _FAMILY_SOURCES.get(family)
    src = (pol.get(mid) or {}).get('source')
    if allowed is None or src in allowed:
        return None
    return (f"SOURCE_MISMATCH: {mid}注册表权威来源={src!r}不属于锚点家族{family!r}"
            f"的授权来源{sorted(allowed)}——指标在注册表存在≠该通道可生成,"
            f"跨通道锚点身份不可认证")


def _sb_tables():
    import snapshot_builder as sb   # lazy: 避免模块级环(fe→fp, sb→fe)
    return sb._GLOBAL_OLD_ID, sb._CHINA_LABEL, sb._RATE_OLD_NAME


def canonical_anchor_metric(anchor_key):
    """锚点键→(metric_id|None, family, note)。
    只接受显式构造语法(逐段精确匹配),绝不以任意子串包含关系授权;
    metric必须存在于当前注册表策略,否则UNMAPPED。"""
    if not isinstance(anchor_key, str):
        return None, 'invalid', '锚点键非字符串'
    try:
        gm, cn_label, rate_old = _sb_tables()
    except ImportError as e:   # pragma: no cover - 环境异常须显式失败
        raise FreshnessPolicyError(f"W2-ANCHOR-MAP-UNAVAILABLE: 无法加载sb映射表:{e}")
    pol = _POLICY if _POLICY is not None else _load_default_policy()
    parts = anchor_key.split('.')
    # global_market.data.<数据键>.<字段> — 数据键经_GLOBAL_OLD_ID反查注册表ID
    if len(parts) == 4 and parts[0] == 'global_market' and parts[1] == 'data' \
            and parts[3] in _GM_FIELDS:
        rev = {v: k for k, v in gm.items()}
        mid = rev.get(parts[2], parts[2])
        if mid not in pol:
            return None, 'global_market', f"global_market数据键{parts[2]!r}未注册"
        mm = _source_mismatch_note(pol, mid, 'global_market')
        if mm:
            return None, 'global_market', mm
        return mid, 'global_market', f"global_market数据键{parts[2]!r}→注册表{mid}"
    # china.data.<中文label>.<字段> — label经_CHINA_LABEL反查
    if len(parts) == 4 and parts[0] == 'china' and parts[1] == 'data' \
            and parts[3] in _CN_DATA_FIELDS:
        rev = {v: k for k, v in cn_label.items()}
        mid = rev.get(parts[2])
        if not mid or mid not in pol:
            return None, 'china_index', f"china指数label{parts[2]!r}未注册"
        mm = _source_mismatch_note(pol, mid, 'china_index')
        if mm:
            return None, 'china_index', mm
        return mid, 'china_index', f"china指数label{parts[2]!r}→注册表{mid}"
    # china特殊键(镜像sb._CN_ANCHOR_KEY构造)
    if anchor_key in _CN_SPECIAL:
        mid = _CN_SPECIAL[anchor_key]
        if mid not in pol:
            return None, 'china_special', f"{anchor_key}目标{mid}未注册"
        mm = _source_mismatch_note(pol, mid, 'china_special')
        if mm:
            return None, 'china_special', mm
        return mid, 'china_special', f"china特殊锚点→注册表{mid}"
    # macro.data.<metric_id>.<字段>
    if len(parts) == 4 and parts[0] == 'macro' and parts[1] == 'data' \
            and parts[3] in _MACRO_FIELDS:
        if parts[2] not in pol:
            return None, 'macro', f"macro序列{parts[2]!r}未注册"
        mm = _source_mismatch_note(pol, parts[2], 'macro')
        if mm:
            return None, 'macro', mm
        return parts[2], 'macro', "macro序列键=注册表ID"
    # macro.derived.<id>
    if anchor_key in _DERIVED_KEYS:
        mid = _DERIVED_KEYS[anchor_key]
        if mid not in pol:
            return None, 'derived', f"派生锚点目标{mid}未注册"
        mm = _source_mismatch_note(pol, mid, 'derived')
        if mm:
            return None, 'derived', mm
        return mid, 'derived', f"派生锚点→注册表{mid}"
    # rate_economy.current_rates.<DFF|DFEDTARU|DFEDTARL>.value (日频!非月度)
    if len(parts) == 4 and parts[0] == 'rate_economy' and parts[1] == 'current_rates' \
            and parts[2] in _CUR_RATE and parts[3] == 'value':
        if parts[2] not in pol:
            return None, 'rate_current', f"current_rates目标{parts[2]}未注册"
        mm = _source_mismatch_note(pol, parts[2], 'rate_current')
        if mm:
            return None, 'rate_current', mm
        return parts[2], 'rate_current', "current_rates=注册表ID(日频)"
    # rate_economy.real_economy.<旧名>.<value|prev_value> — 经_RATE_OLD_NAME反查
    if len(parts) == 4 and parts[0] == 'rate_economy' and parts[1] == 'real_economy' \
            and parts[3] in _REAL_ECO_FIELDS:
        rev = {v: k for k, v in rate_old.items()}
        mid = rev.get(parts[2], parts[2])
        if mid not in pol:
            return None, 'rate_real_economy', f"real_economy旧名{parts[2]!r}未注册"
        mm = _source_mismatch_note(pol, mid, 'rate_real_economy')
        if mm:
            return None, 'rate_real_economy', mm
        return mid, 'rate_real_economy', f"real_economy旧名{parts[2]!r}→注册表{mid}"
    # rate_economy.fed_funds_futures.<i>.<price|implied_rate> — 期货曲线点
    # (sb直接构造,无obs_date;映射到对应注册表ID但时间元数据缺失=无法判龄)
    if len(parts) == 4 and parts[0] == 'rate_economy' and parts[1] == 'fed_funds_futures' \
            and parts[2].isdigit() and parts[3] in ('price', 'implied_rate'):
        mid = 'ZQ_F1_PRICE' if parts[3] == 'price' else 'ZQ_IMPLIED_AVG'
        if mid not in pol:
            return None, 'futures_curve', f"曲线点目标{mid}未注册"
        mm = _source_mismatch_note(pol, mid, 'futures_curve')
        if mm:
            return None, 'futures_curve', mm
        return mid, 'futures_curve', f"曲线点锚点→{mid}(sb构造无obs_date,判龄须补元数据)"
    return None, 'unmapped', '锚点键不匹配任何已注册构造语法'


def verify_anchor_identity(anchor_key, info=None):
    """锚点身份核验(FIX1-03收紧): canonical键映射+**来源家族绑定**为准,
    info.metric_id仅交叉核验不作授权。返回{status, reason, metric_id, family,
    basis, caller_metric_id, conflict}:
      MAPPED     键语法匹配+指标注册+注册表权威来源属于该锚点家族+无身份冲突;
      UNMAPPED   键不匹配任何已注册构造语法/指标未注册;
      UNVERIFIED 身份不可认证——SOURCE_MISMATCH(指标注册但权威来源不属于该
                 锚点家族,如global_market.data.CPI.close)或IDENTITY_CONFLICT
                 (caller声称metric_id与canonical不符)。二者均fail-closed,
                 不得仅记录conflict后继续返回可认证身份(W2-FIX1 §7.4)。"""
    mid, family, note = canonical_anchor_metric(anchor_key)
    caller = (info or {}).get('metric_id') if isinstance(info, dict) else None
    out = {'status': None, 'reason': None, 'metric_id': mid,
           'family': family, 'basis': note, 'caller_metric_id': caller,
           'conflict': None}
    if mid is None:
        if isinstance(note, str) and note.startswith('SOURCE_MISMATCH'):
            out.update(status='UNVERIFIED', reason='source_mismatch')
        else:
            out.update(status='UNMAPPED', reason='unmapped')
        return out
    if caller and caller != mid:
        out.update(status='UNVERIFIED', reason='identity_conflict')
        out['conflict'] = (f"caller声称metric_id={caller!r}与canonical={mid!r}不符"
                           f"——锚点键与声明身份冲突,身份无法认证(FIX1-03: 冲突=UNVERIFIED,"
                           f"不再以canonical继续授予时效认证)")
        return out
    out.update(status='MAPPED', reason='mapped')
    return out


# ══ 三问分离判定原语 ═════════════════════════════════════════════

def assess(metric_id, obs_date, as_of, release_date=None):
    """统一时效判定(纯函数): 三问分离,结构化诊断,未知绝不转为有效。

    A 已观测?   obs_date存在且为完整ISO真实日历日期,且不晚于as_of;
    B as_of时点已发布? 仅当真实release_date在场才作答: release≤as_of=OK,
                release>as_of=RELEASE_AFTER_AS_OF(点时不可得,不得作当前证据);
                缺失=RELEASE_UNKNOWN(如实标注,不伪造); release<obs=INVALID;
    C 是否新鲜? lag=as_of−obs ≤ 已批准窗口(registry(approved))。
    FIX1-01: as_of与release_date接受date/datetime/完整ISO日期/**完整**ISO时间戳
    (整串先验证再取日期,绝不[:10]截断);obs_date仍须纯日期(经济观测日语义)。
    FIX2-02: B问先后比较经compare_release_availability精度保持判定——双aware
    时刻比绝对先后;同日精度不足=POINT_IN_TIME_UNCERTIFIED(可得但不认证点时)。
    返回verdict dict(fresh=bool;status∈FRESH/STALE/NOT_OBSERVED/INVALID_DATE/
    FUTURE_DATE/UNREGISTERED/NOT_AVAILABLE_AT_AS_OF/INVALID_RELEASE)。"""
    v = {'metric_id': metric_id, 'obs_date': None, 'as_of': None,
         'lag_days': None, 'window': None, 'frequency': None,
         'observed': {'status': 'MISSING'}, 'point_in_time': {'status': 'RELEASE_UNKNOWN'},
         'fresh': False, 'status': None, 'reasons': []}
    pol = policy_for(metric_id)
    if pol is None:
        v.update(status='UNREGISTERED', fresh=False,
                 reasons=[f"指标{metric_id!r}不在已批准时效策略(未注册或策略未加载)——未知策略不得视为有效"])
        return v
    v['window'], v['frequency'] = pol['window'], pol['frequency']
    a = parse_instant(as_of) if as_of is not None else None
    if a is None:
        v.update(status='INVALID_DATE', fresh=False, reasons=['as_of缺失或非完整ISO日期'])
        return v
    v['as_of'] = a.isoformat()
    o = _parse_iso_date(obs_date) if obs_date is not None else None
    if o is None:
        v['observed'] = {'status': 'INVALID' if obs_date is not None else 'MISSING'}
        v.update(status='NOT_OBSERVED' if obs_date is None else 'INVALID_DATE',
                 fresh=False,
                 reasons=[f"观测日缺失或非完整ISO真实日期:{obs_date!r}(不得以当前日期替代非法输入)"])
        return v
    v['obs_date'] = o.isoformat()
    v['observed'] = {'status': 'OK'}
    # FIX1-02可追踪性: 滞后天数在B问前先算好——点时不可得早退时也能看到
    # "lag≤窗但as_of时点不可得"的完整对照(Agent4反例的叙事结构)
    v['lag_days'] = (a - o).days
    if o > a:
        v.update(status='FUTURE_DATE', fresh=False,
                 reasons=[f"观测日{o}晚于研究截止{a}(未来数据,非法时点)"])
        return v
    # B问: 点时可得性——只对真实携带的release_date作答,缺失即如实UNKNOWN。
    # FIX2-02: 先后比较统一经compare_release_availability(精度保持原语):
    #   双aware完整时间戳→绝对时刻比较(UTC偏移正确处理);
    #   同日且精度不足/涉无时区时刻相邻→UNVERIFIED(按日粒度可得,历史兼容,
    #     但**不认证点时可得**——绝不虚报"已验证在研究截止前发布");
    #   跨日→日粒度判定。绝不把完整时间戳先降成date再比先后(同日
    #   08:00截止/20:00发布不再被洗白为"发布不晚于截止")。
    if release_date is not None:
        cmp = compare_release_availability(release_date, as_of)
        rtv = parse_temporal_value(release_date)
        if cmp['verdict'] == 'INVALID_RELEASE':
            v['point_in_time'] = {'status': 'INVALID', 'release_date': release_date}
            v.update(status='INVALID_RELEASE', fresh=False,
                     reasons=[f"release_date非完整ISO日期:{release_date!r}"
                              f"({cmp['detail']})"])
            return v
        rel_raw = release_date if isinstance(release_date, str) else \
            release_date.isoformat()
        if rtv['date'] < o:
            v['point_in_time'] = {'status': 'RELEASE_BEFORE_OBS',
                                  'release_date': rel_raw}
            v.update(status='INVALID_RELEASE', fresh=False,
                     reasons=[f"release_date{rtv['date']}早于观测日{o}"
                              f"(发布先于观测,语义非法)"])
            return v
        if cmp['verdict'] == 'RELEASED_AFTER':
            v['point_in_time'] = {'status': 'RELEASE_AFTER_AS_OF',
                                  'release_date': rel_raw,
                                  'granularity': cmp['granularity'],
                                  'detail': cmp['detail']}
            v.update(status='NOT_AVAILABLE_AT_AS_OF', fresh=False,
                     reasons=[f"已知发布{rel_raw}晚于研究截止{as_of!r}"
                              f"({cmp['detail']})——as_of时点该值不可得,"
                              f"不得作当前证据"])
            return v
        if cmp['verdict'] == 'RELEASED_BEFORE':
            v['point_in_time'] = {'status': 'OK', 'release_date': rel_raw,
                                  'granularity': cmp['granularity'],
                                  'detail': cmp['detail']}
        else:   # UNVERIFIED_SAME_DAY / UNVERIFIED_TZ(§5.5保守映射: 披露非失败)
            v['point_in_time'] = {'status': 'POINT_IN_TIME_UNCERTIFIED',
                                  'release_date': rel_raw, 'granularity': 'DAY',
                                  'detail': cmp['detail']}
    else:
        v['point_in_time'] = {'status': 'RELEASE_UNKNOWN',
                              'note': '采集端不携带release_date——如实标注未知,不伪造点时证据;新鲜度按观测滞后窗判定'}
    # C问: 观测滞后 vs 已批准窗口
    lag = v['lag_days']
    if lag > pol['window']:
        v.update(status='STALE', fresh=False,
                 reasons=[f"观测日滞后{lag}天>{pol['window']}天已批准窗口({pol['frequency']}频;未发布或采集失败,不得当作最新一期)"])
        return v
    v.update(status='FRESH', fresh=True, reasons=[
        f"观测日滞后{lag}天≤{pol['window']}天已批准窗口({pol['frequency']}频)"])
    return v
