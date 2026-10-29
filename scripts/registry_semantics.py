#!/usr/bin/env python3
"""注册表金融语义一致性验证(IA-P0-2-W1-03) — 纯函数,离线,零网络。

定位与边界(W1-AC):
- 本模块检查 config/metric_registry.json 的**字段结构合法性**与**已确认的金融
  工具语义矛盾**(股票≠ETF、指数≠个股、利率/利差量纲不混淆、来源枚举封闭)。
- 事实级来源授权/批次一致性仍由 research_provenance.fact_source_problems
  等既有链执行——本模块不重复、不替代(W1 不改 Gate 行为)。
- 真实金融数据数值准确性不在本模块能力范围(报告如实声明,不伪造PASS)。

规则分两级:
- error : 确定性矛盾/非法结构。经fact_engine.load_registry接入生产加载路径,
  出现即抛RegistrySemanticsError(fail-loud,不静默使用已确认非法配置)。
- review: 尚不能机器判定的组合(未确认asset_class/value_type/instrument组合)。
  只诊断不拦截——不编造枚举值,不把"没见过"伪装成"非法",也不伪装成已认证。

设计约束:
- 只依赖标准库;不读生产数据;不发起网络;输入即注册表dict(或路径)。
- 封闭集合均为**有金融含义的确认集**(逐条注明依据),不是从当前配置
  自动生成的"全部现状皆合法"枚举;未确认组合一律进review。
- KNOWN_UNITS/KNOWN_CALENDARS/KNOWN_SOURCES 分别镜像
  fact_engine单位纪律(§4.4 PRICE_LIKE/RATE/COUNT)、trading_calendar.MARKETS、
  research_provenance._AUTHORIZED_COLLECTORS(+deprecated遗留'macro_collector(derived)')
  ——为避免运行时循环依赖在本地维护镜像,tests/test_p02_w1.py A6节
  强制三方逐元素相等(漂移即测试红)。
"""
import json
import os

__all__ = [
    'RegistrySemanticsError', 'validate_registry', 'registry_semantic_errors',
    'registry_semantic_reviews', 'assert_registry_semantics', 'load_registry_json',
    'KNOWN_UNITS', 'KNOWN_CALENDARS', 'KNOWN_SOURCES', 'KNOWN_INSTRUMENTS',
    'ETF_ASSET_CLASSES', 'INSTRUMENT_BY_CLASS', 'UNIT_BY_CLASS',
    'NOT_VERIFIED_HERE',
]


class RegistrySemanticsError(ValueError):
    """注册表存在已确认的语义/结构非法配置——生产加载必须失败(fail-loud)。"""


# ── 封闭集合(每条附金融依据;镜像源见模块docstring) ──────────────────

# 单位全集 = fact_engine价格类(index_point/usd/…) ∪ 利率类(percent/percentage_point)
# ∪ 计数类(persons/persons_thousands)。利率水平=percent、利差/斜率=percentage_point
# 是"水平vs变化"的量纲纪律:混用会把百分点变化误当百分比收益率。
KNOWN_UNITS = frozenset({
    # 价格/点位类(fact_engine.PRICE_LIKE_UNITS镜像)
    'index_point', 'usd', 'usd_per_oz', 'usd_per_barrel', 'usd_per_eur',
    'usd_per_gbp', 'jpy_per_usd', 'cny_per_usd', 'cny_100m', 'hkd_100m',
    'points', 'million_usd', 'usd_per_hour', 'ratio',
    'index_point_1982_84', 'index_point_2012', 'index_point_1966', 'index_point_2017',
    # 利率类(fact_engine.RATE_UNITS镜像)
    'percent', 'percentage_point',
    # 计数类(fact_engine.COUNT_UNITS镜像)
    'persons', 'persons_thousands',
})

# 交易日历全集 = trading_calendar.MARKETS镜像(us_equity/us_rates/commodity/cn/hk/fx/crypto)。
KNOWN_CALENDARS = frozenset({'us_equity', 'us_rates', 'commodity', 'cn', 'hk', 'fx', 'crypto'})

# 来源全集 = research_provenance._AUTHORIZED_COLLECTORS键
# (global_market_collector/macro_collector/china_market_collector/
#  rate_expectations/fact_engine(derived)) ∪ deprecated遗留
# 'macro_collector(derived)'(REAL_SHORT,_SOURCE_TO_INPUT仍映射macro通道)。
# 采集器与注册表source的符号级映射核验见 docs/P0_2_W1_REGISTRY_AUDIT.json(开发期人工核验)。
KNOWN_SOURCES = frozenset({
    'global_market_collector', 'macro_collector', 'china_market_collector',
    'rate_expectations', 'fact_engine(derived)', 'macro_collector(derived)',
})

# 工具身份词汇表(W1-01审计确认):个股/ETF/指数/期货连续/现货加密/利率序列/
# 宏观序列/聚合/派生。未知值=拼写级错误(本模块自有的封闭词汇,非"现状枚举")。
KNOWN_INSTRUMENTS = frozenset({
    'single_stock', 'etf', 'index', 'futures_front_continuous', 'spot_crypto',
    'index_rate_series', 'macro_series', 'aggregate', 'derived',
})

# ETF类别全集:instrument='etf'只属于这四类——ETF身份具有排他性,
# 个股/指数/期货冒用etf身份即身份伪造(W1-02三项缺陷的机器可检形式)。
ETF_ASSET_CLASSES = frozenset({
    'bond_etf', 'country_etf_proxy', 'spot_commodity_etf', 'commodity_futures_etf',
})

# asset_class → 合法instrument集合:
#  - required: 市场交易工具类——instrument为身份定义的必要组成,缺失即身份不完整;
#  - optional: 统计序列/流量/存量类——FRED系列与通道派生量可不带instrument
#    (历史兼容结构,缺失不构成错误);在场时仍须属于该类合法集合。
# 依据(逐类金融语义):
#   single_stock→single_stock:个股是发行人权益凭证,不是基金份额(W1-02);
#   equity_index/volatility_index/fx_index/spread_index→index:指数是一篮子/统计
#     读数,不是可交割单只工具(VIX为统计量,标注index+calc说明非价格);
#   *_etf四类→etf:基金份额;
#   commodity_futures→futures_front_continuous:主力连续合约(含展期),非现货;
#   fed_futures→{futures_front_continuous(ZQ_F1_PRICE),derived(ZQ_IMPLIED_AVG)};
#   crypto→spot_crypto:现货指数化报价(7×24);
#   rates/宏观类:统计序列,按频发布。
INSTRUMENT_BY_CLASS = {
    'single_stock': ('required', frozenset({'single_stock'})),
    'equity_index': ('required', frozenset({'index'})),
    'volatility_index': ('required', frozenset({'index'})),
    'fx_index': ('required', frozenset({'index'})),
    'spread_index': ('required', frozenset({'index'})),
    'bond_etf': ('required', frozenset({'etf'})),
    'country_etf_proxy': ('required', frozenset({'etf'})),
    'spot_commodity_etf': ('required', frozenset({'etf'})),
    'commodity_futures_etf': ('required', frozenset({'etf'})),
    'commodity_futures': ('required', frozenset({'futures_front_continuous'})),
    'fed_futures': ('required', frozenset({'futures_front_continuous', 'derived'})),
    'crypto': ('required', frozenset({'spot_crypto'})),
    'rates_yield': ('optional', frozenset({'index_rate_series'})),
    'real_rate': ('optional', frozenset({'index_rate_series', 'derived'})),
    'inflation_expectation': ('optional', frozenset({'index_rate_series'})),
    'credit_spread': ('optional', frozenset({'index_rate_series', 'derived'})),
    'curve_slope': ('optional', frozenset({'index_rate_series'})),
    'policy_rate': ('optional', frozenset({'macro_series', 'index_rate_series'})),
    'macro_index': ('optional', frozenset({'macro_series'})),
    'macro_rate': ('optional', frozenset({'macro_series'})),
    'macro_count': ('optional', frozenset({'macro_series'})),
    'macro_price': ('optional', frozenset({'macro_series'})),
    'macro_count_derived': ('optional', frozenset({'macro_series'})),
    'sentiment': ('optional', frozenset({'macro_series'})),
    'volume_amount': ('optional', frozenset({'aggregate'})),
    'fx_rate': ('optional', frozenset()),          # 汇率即工具本身,无需二级身份
    'flow': ('optional', frozenset()),             # 流量统计
    'leverage': ('optional', frozenset()),         # 存量统计
    'valuation': ('optional', frozenset()),        # 比率统计
}

# asset_class → 合法单位集合(量纲纪律;仅对"多成员且量纲统一"的确认类立法,
# 单成员/基期各异类(macro_index/sentiment/valuation/flow/leverage/volume_amount/
# macro_price)只做KNOWN_UNITS结构校验,不编造"全部同单位"伪规则):
#   利率水平类→percent;利差/斜率类→percentage_point(1pp=100bp);
#   汇率→方向编码单位(报价方向入unit名,防USDJPY/EURUSD方向倒置无从检查);
#   指数读数→index_point;美元计价证券→usd;商品期货→usd_per_oz/usd_per_barrel;
#   联邦基金期货→points(价格)/percent(隐含利率);
#   就业计数→persons/persons_thousands(千人换算须显式)。
UNIT_BY_CLASS = {
    'rates_yield': frozenset({'percent'}),
    'real_rate': frozenset({'percent'}),
    'inflation_expectation': frozenset({'percent'}),
    'policy_rate': frozenset({'percent'}),
    'credit_spread': frozenset({'percentage_point'}),
    'curve_slope': frozenset({'percentage_point'}),
    'fx_rate': frozenset({'usd_per_eur', 'usd_per_gbp', 'jpy_per_usd', 'cny_per_usd'}),
    'equity_index': frozenset({'index_point'}),
    'volatility_index': frozenset({'index_point'}),
    'fx_index': frozenset({'index_point'}),
    'spread_index': frozenset({'index_point'}),
    'single_stock': frozenset({'usd'}),
    'bond_etf': frozenset({'usd'}),
    'country_etf_proxy': frozenset({'usd'}),
    'spot_commodity_etf': frozenset({'usd'}),
    'commodity_futures_etf': frozenset({'usd'}),
    'crypto': frozenset({'usd'}),
    'commodity_futures': frozenset({'usd_per_oz', 'usd_per_barrel'}),
    'fed_futures': frozenset({'points', 'percent'}),
    'macro_count': frozenset({'persons', 'persons_thousands'}),
    'macro_count_derived': frozenset({'persons_thousands'}),
    'macro_rate': frozenset({'percent'}),
}

# status词汇:fe.snapshot_quality_grade/rp.core_metric_ids/active_metric_defs
# 以字面'active'过滤——拼写漂移会把core指标静默逐出Gate A统计,必须error。
STATUS_VALUES = frozenset({'active', 'deprecated'})
# criticality词汇:'core'为Gate A分级权威;未知值=静默降级,必须error。
CRITICALITY_VALUES = frozenset({'core', 'important', 'context'})
# value_type词汇:make_fact缺省'level';rp.fact_structure_problems逐字比对
# 事实与注册表——新值需人工核定语义,未知→review(不拦截未来合法扩展)。
VALUE_TYPE_VALUES = frozenset({
    'level', 'yield_or_spread_level', 'monthly_avg_rate', 'daily_effective_rate',
    'target_band', 'derived_rate', 'derived_spread', 'daily_net_flow',
    'outstanding_balance', 'daily_turnover', 'contract_implied_monthly_average',
})
FREQUENCY_VALUES = frozenset({'daily', 'weekly', 'monthly'})

# ── IA-P02-W1-FIX1-02: 已确认官方序列身份→单位(独立权威映射) ──
# 本映射独立于被验证的注册表(绝不从当前配置生成"期望值",否则注册表与校验
# 会共同携带同一错误——W1首轮CORE_PCE误标index_point_2012即为实例)。
# 证据:FRED官方序列页2026-10-29核验(docs/P0_2_W1_REGISTRY_AUDIT.json
# official_units_evidence);范围仅限已获权威依据的序列,不为扩规则做81项外部研究。
OFFICIAL_FRED_INDEX_UNITS = {
    # FRED series → 官方单位(注册表unit词汇)
    'PCEPILFE': 'index_point_2017',    # BEA链式核心PCE物价指数 Index 2017=100 SA Monthly
    'CPIAUCSL': 'index_point_1982_84',  # BLS CPI-U全项 Index 1982-1984=100 SA Monthly
    'CPILFESL': 'index_point_1982_84',  # BLS CPI-U除食品能源 Index 1982-1984=100 SA Monthly
    'INDPRO': 'index_point_2017',      # Fed G.17工业生产总指数 Index 2017=100 SA Monthly
    'UMCSENT': 'index_point_1966',     # 密歇根大学消费者信心 Index 1966:Q1=100 NSA Monthly
}
# 指标身份绑定:已确认 metric_id ↔ 官方序列。更换source_symbol属身份变更,
# 需独立授权并同步更新本映射——不得仅因新序列自身单位合法而自动放行。
OFFICIAL_METRIC_SERIES = {
    'CORE_PCE': 'PCEPILFE',
    'CPI': 'CPIAUCSL',
    'CORE_CPI': 'CPILFESL',
    'INDPRO': 'INDPRO',
    'UMCSENT': 'UMCSENT',
}
# 采集器单位说明须包含的基期子串(注册表unit ↔ 采集器SERIES_UNITS标签同步约束)。
OFFICIAL_UNIT_LABELS = {
    'index_point_2017': '2017=100',
    'index_point_1982_84': '1982-84=100',
    'index_point_1966': '1966=100',
}

# 如实声明本模块**不**验证的内容(供审计报告引用,不伪造覆盖):
NOT_VERIFIED_HERE = [
    '真实金融数值准确性(价格/利率/计数与外部市场的一致性)——W1范围外',
    '时效政策与有效期窗口数值(freshness仅查结构合法性;语义归W2)',
    '采集器运行时实际符号表与source_symbol的一致性(开发期人工核验;FIX1后5项'
    '官方指数序列的基期标签已有机器同步检查collector_official_unit_problems,其余仍人工)',
    '未确认asset_class/instrument组合的金融正当性(标review,待人工或后续工作包)',
    '新闻/情绪与业务模块口径(W3~W5范围)',
]


def load_registry_json(path):
    """读取注册表JSON文件(纯文件读取;调用方负责路径可信性)。"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _num_ok(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def validate_registry(reg):
    """校验注册表dict → 结构化问题列表(可能为空)。

    每条: {'metric_id','rule','severity','field','message'}
    severity: 'error'=确定性非法(生产加载拒绝);'review'=待人工核定(不拦截)。
    空列表仅代表"已定义规则内无矛盾",不等于金融事实认证(NOT_VERIFIED_HERE)。
    """
    probs = []

    def add(mid, rule, severity, field, message):
        probs.append({'metric_id': mid, 'rule': rule, 'severity': severity,
                      'field': field, 'message': message})

    if not isinstance(reg, dict) or not isinstance(reg.get('metrics'), list):
        return [{'metric_id': None, 'rule': 'R-REGISTRY-SHAPE', 'severity': 'error',
                 'field': 'metrics', 'message': '注册表顶层须为dict且metrics为list'}]

    seen = set()
    for m in reg['metrics']:
        mid = m.get('metric_id') if isinstance(m, dict) else None
        # ── 结构(确定性) ──
        if not isinstance(m, dict):
            add(None, 'R-ENTRY-TYPE', 'error', None, f'条目非对象:{type(m).__name__}')
            continue
        if not isinstance(mid, str) or not mid.strip():
            add(None, 'R-ID', 'error', 'metric_id', f'metric_id缺失/非字符串:{mid!r}')
            mid = None
        elif mid in seen:
            add(mid, 'R-ID-DUP', 'error', 'metric_id', f'metric_id重复:{mid}(身份唯一性破坏)')
        else:
            seen.add(mid)
        for fld in ('display_name', 'unit', 'source', 'source_symbol'):
            v = m.get(fld)
            if not isinstance(v, str) or not v.strip():
                add(mid, 'R-FIELD-STR', 'error', fld, f'{fld}缺失/非非空字符串:{v!r}')
        if not isinstance(m.get('asset_class'), str) or not m.get('asset_class', '').strip():
            add(mid, 'R-FIELD-STR', 'error', 'asset_class',
                f"asset_class缺失/非非空字符串:{m.get('asset_class')!r}")
        # ── 封闭集合(确定性) ──
        unit, source = m.get('unit'), m.get('source')
        source_symbol = m.get('source_symbol')
        if isinstance(unit, str) and unit not in KNOWN_UNITS:
            add(mid, 'R-UNIT-ENUM', 'error', 'unit',
                f"unit={unit!r}不在引擎单位纪律全集内(价格/利率/计数三类量纲之外)")
        cal = m.get('calendar')
        if isinstance(cal, str) and cal not in KNOWN_CALENDARS:
            add(mid, 'R-CALENDAR-ENUM', 'error', 'calendar',
                f"calendar={cal!r}不在trading_calendar.MARKETS内")
        if isinstance(source, str) and source not in KNOWN_SOURCES:
            add(mid, 'R-SOURCE-ENUM', 'error', 'source',
                f"source={source!r}不是已授权采集通道/派生来源(无法解释的来源)")
        # ── IA-P02-W1-FIX1-03: 关键字段类型拦截 ──
        # 非字符串/空串/缺失曾在isinstance(str)守卫下静默绕过枚举判断
        # (status=123等)——Gate A按字面'active'过滤,类型违规会把核心指标
        # 静默逐出统计,必须确定性error。类型检查先于语义使用。
        for fld, allowed, tname in (('status', STATUS_VALUES, 'R-STATUS-TYPE'),
                                    ('criticality', CRITICALITY_VALUES, 'R-CRITICALITY-TYPE'),
                                    ('frequency', FREQUENCY_VALUES, 'R-FREQUENCY-TYPE')):
            v = m.get(fld)
            if not isinstance(v, str) or not v.strip():
                add(mid, tname, 'error', fld,
                    f"{fld}缺失/非非空字符串:{v!r}(类型{type(v).__name__};"
                    f'须为非空字符串且∈{sorted(allowed)})')
            elif v not in allowed:
                add(mid, tname.replace('-TYPE', '-ENUM'), 'error', fld,
                    f"{fld}={v!r}非法(须∈{sorted(allowed)};status='active'为Gate A过滤字面值,"
                    'criticality未知=Gate A静默降级风险)')
        # ── IA-P02-W1-FIX1-02: 官方序列身份与单位(独立权威映射,期望值不由注册表生成) ──
        if mid in OFFICIAL_METRIC_SERIES:
            official_sym = OFFICIAL_METRIC_SERIES[mid]
            sym = m.get('source_symbol')
            if sym != official_sym:
                add(mid, 'R-OFFICIAL-SERIES', 'error', 'source_symbol',
                    f"{mid}已确认官方身份绑定source_symbol={official_sym!r},"
                    f'实际={sym!r}——更换底层序列属指标身份变更,需独立授权并同步'
                    '更新OFFICIAL_METRIC_SERIES,不得仅因新序列自身单位合法而放行')
        if isinstance(source_symbol, str) and source_symbol in OFFICIAL_FRED_INDEX_UNITS:
            official_unit = OFFICIAL_FRED_INDEX_UNITS[source_symbol]
            if unit != official_unit:
                add(mid, 'R-OFFICIAL-UNIT', 'error', 'unit',
                    f'source_symbol={source_symbol}官方单位期望={official_unit!r},'
                    f'实际unit={unit!r}(FRED官方基期2026-10-29核验;'
                    '标注修复≠数值重新定基)')
        # ── identity(工具身份) ──
        ident = m.get('identity')
        cls = m.get('asset_class') if isinstance(m.get('asset_class'), str) else None
        if ident is not None and not isinstance(ident, dict):
            add(mid, 'R-IDENTITY-TYPE', 'error', 'identity', f'identity非对象:{type(ident).__name__}')
            ident = None
        instrument = ident.get('instrument') if isinstance(ident, dict) else None
        if instrument is not None and (not isinstance(instrument, str) or not instrument.strip()):
            add(mid, 'R-INSTRUMENT-TYPE', 'error', 'identity.instrument',
                f'instrument非非空字符串:{instrument!r}')
            instrument = None
        if isinstance(instrument, str) and instrument not in KNOWN_INSTRUMENTS:
            add(mid, 'R-INSTRUMENT-ENUM', 'error', 'identity.instrument',
                f"instrument={instrument!r}不在工具身份词汇表内"
                f"(已知:{sorted(KNOWN_INSTRUMENTS)})")
        spec = INSTRUMENT_BY_CLASS.get(cls) if cls else None
        if spec is not None:
            mode, allowed = spec
            if mode == 'required' and instrument is None:
                add(mid, 'R-INSTRUMENT-REQUIRED', 'error', 'identity.instrument',
                    f"{cls}类市场工具必须声明identity.instrument(合法值{sorted(allowed)})")
            elif instrument is not None and instrument not in allowed:
                add(mid, 'R-INSTRUMENT-CLASS', 'error', 'identity.instrument',
                    f"{cls}类instrument={instrument!r}非法(该类合法值{sorted(allowed)};"
                    '工具身份与类别矛盾)')
        elif cls is not None and instrument is not None:
            add(mid, 'R-COMBINATION-UNCONFIRMED', 'review', 'identity.instrument',
                f"asset_class={cls!r}未建立instrument规则,组合({cls},{instrument!r})"
                '需人工金融语义核定')
        # ETF身份排他性(W1-02缺陷的一般形式):etf身份只属于ETF类别
        if instrument == 'etf' and cls is not None and cls not in ETF_ASSET_CLASSES:
            add(mid, 'R-ETF-EXCLUSIVITY', 'error', 'identity.instrument',
                f"{cls}不得持有etf工具身份(ETF类别={sorted(ETF_ASSET_CLASSES)});"
                '个股冒用etf身份即身份伪造(W1-02三项同类缺陷)')
        # 具名缺陷规则(冗余但显式:审计/测试可直接按rule定位)
        if cls == 'single_stock' and instrument == 'etf':
            add(mid, 'R-STOCK-NOT-ETF', 'error', 'identity.instrument',
                'single_stock指标的instrument不得为etf——个股是发行人权益凭证,'
                '不是基金份额(IA-P0-2-W1-02已确认缺陷形态)')
        if isinstance(ident, dict):
            if 'is_proxy' in ident and not isinstance(ident['is_proxy'], bool):
                add(mid, 'R-PROXY-TYPE', 'error', 'identity.is_proxy',
                    f"is_proxy非布尔:{ident['is_proxy']!r}")
            if ident.get('is_proxy') is True:
                po = ident.get('proxy_of')
                if not isinstance(po, str) or not po.strip():
                    add(mid, 'R-PROXY-TARGET', 'error', 'identity.proxy_of',
                        'is_proxy=true必须给出非空proxy_of(代理对象不可追溯)')
        # ── 量纲纪律(确定性;仅对已确认类) ──
        if cls in UNIT_BY_CLASS and isinstance(unit, str) and unit not in UNIT_BY_CLASS[cls]:
            add(mid, 'R-UNIT-DIMENSION', 'error', 'unit',
                f"{cls}类unit={unit!r}违反量纲纪律(该类合法值{sorted(UNIT_BY_CLASS[cls])};"
                '利率水平=percent、利差/斜率=percentage_point、计数带千人换算等)')
        # ── validation/freshness结构(结构合法性;政策数值不动——W2) ──
        val = m.get('validation')
        if val is not None:
            if not isinstance(val, dict):
                add(mid, 'R-VALIDATION-TYPE', 'error', 'validation',
                    f'validation非对象:{type(val).__name__}')
            else:
                rng = val.get('range')
                if rng is not None:
                    ok = (isinstance(rng, (list, tuple)) and len(rng) == 2
                          and all(_num_ok(x) for x in rng) and rng[0] < rng[1])
                    if not ok:
                        add(mid, 'R-VALIDATION-RANGE', 'error', 'validation.range',
                            f'range须为[lo,hi]数值对且lo<hi:{rng!r}')
                for k in ('max_week_pct_move', 'max_week_abs_move'):
                    if k in val and not (_num_ok(val[k]) and val[k] > 0):
                        add(mid, 'R-VALIDATION-THRESHOLD', 'error', f'validation.{k}',
                            f'{k}须为正数:{val[k]!r}')
        fr = m.get('freshness')
        if fr is not None:
            if not isinstance(fr, dict):
                add(mid, 'R-FRESHNESS-TYPE', 'error', 'freshness',
                    f'freshness非对象:{type(fr).__name__}')
            else:
                lag = fr.get('max_calendar_lag_days')
                if not isinstance(lag, int) or isinstance(lag, bool) or lag <= 0:
                    add(mid, 'R-FRESHNESS-STRUCT', 'error', 'freshness.max_calendar_lag_days',
                        f'max_calendar_lag_days须为正整数:{lag!r}(时效窗口政策本身归W2,本规则只查结构)')
        # IA-P02-W1-FIX1-03: value_type——在场则必须为非空字符串(非法类型=确定性
        # 结构error);合法字符串但未确认词汇→维持review(不擅自升error)。
        # 允许缺失的历史兼容依据:fact_engine.make_fact第210行 m.get('value_type','level')
        # 缺省'level'——"可选字段"不等于"允许显式提供非法类型"。
        vt = m.get('value_type')
        if 'value_type' in m and (not isinstance(vt, str) or not vt.strip()):
            add(mid, 'R-VALUETYPE-TYPE', 'error', 'value_type',
                f'value_type非非空字符串:{vt!r}(类型{type(vt).__name__};'
                '该字段可选,但在场即须为非空字符串;缺失时make_fact缺省level)')
        elif isinstance(vt, str) and vt not in VALUE_TYPE_VALUES:
            add(mid, 'R-VALUETYPE-ENUM', 'review', 'value_type',
                f"value_type={vt!r}不在已确认词汇内(新增语义需人工核定,不拦截)")
        if cls is not None and cls not in INSTRUMENT_BY_CLASS:
            add(mid, 'R-ASSETCLASS-UNCONFIRMED', 'review', 'asset_class',
                f"asset_class={cls!r}未建立语义规则(需人工核定类别正当性)")
    return probs


def collector_official_unit_problems(reg, series_units):
    """IA-P02-W1-FIX1-02: 注册表官方指数单位 ↔ 采集器SERIES_UNITS标签同步校验。

    纯函数(采集器单位表由调用方传入,本模块不import采集器,保持零第三方依赖)。
    对每个官方身份绑定指标:注册表unit映射的基期子串必须出现在采集器单位说明中。
    返回结构化问题列表(非空=采集器说明与已确认官方口径脱节,如2012标签残留)。
    """
    probs = []
    by_id = {m.get('metric_id'): m for m in reg.get('metrics', [])
             if isinstance(m, dict)}
    for mid, sym in OFFICIAL_METRIC_SERIES.items():
        m = by_id.get(mid)
        if m is None:
            continue
        label_frag = OFFICIAL_UNIT_LABELS.get(m.get('unit'))
        if label_frag is None:
            continue  # 非指数基期保护范围(注册表侧R-OFFICIAL-UNIT另行拦截)
        entry = series_units.get(mid)
        label = entry[1] if isinstance(entry, tuple) and len(entry) > 1 else entry
        if not isinstance(label, str) or label_frag not in label:
            probs.append({
                'metric_id': mid, 'rule': 'R-OFFICIAL-UNIT-SYNC',
                'severity': 'error', 'field': 'SERIES_UNITS[unit_label]',
                'message': (f'{mid}注册表unit={m.get("unit")!r}要求采集器单位说明含'
                            f'{label_frag!r},实际SERIES_UNITS标签={label!r}'
                            '——与已确认官方口径脱节')})
    return probs


def registry_semantic_errors(reg):
    """error级问题子集(生产加载据此拒绝)。"""
    return [p for p in validate_registry(reg) if p['severity'] == 'error']


def registry_semantic_reviews(reg):
    """review级问题子集(诊断输出,不拦截)。"""
    return [p for p in validate_registry(reg) if p['severity'] == 'review']


def assert_registry_semantics(reg, source_desc='registry'):
    """error级问题非空时抛RegistrySemanticsError(消息含metric_id+rule+说明)。

    fact_engine.load_registry()的生产接入点:已确认非法的配置不得静默进入
    事实构造;review级不在此抛出(未确认≠非法)。
    """
    errs = registry_semantic_errors(reg)
    if errs:
        lines = [f"  [{p['rule']}] {p['metric_id']}.{p['field']}: {p['message']}"
                 for p in errs]
        raise RegistrySemanticsError(
            f"指标注册表存在{len(errs)}项已确认语义/结构非法配置({source_desc}),拒绝加载:\n"
            + "\n".join(lines))
    return True


if __name__ == '__main__':
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'config', 'metric_registry.json')
    problems = validate_registry(load_registry_json(path))
    errs = [p for p in problems if p['severity'] == 'error']
    revs = [p for p in problems if p['severity'] == 'review']
    print(f"注册表语义验证: {len(problems)}条问题 (error={len(errs)}, review={len(revs)})")
    for p in errs:
        print(f"  ❌ [{p['rule']}] {p['metric_id']}.{p['field']}: {p['message']}")
    for p in revs:
        print(f"  🔍 [{p['rule']}] {p['metric_id']}.{p['field']}: {p['message']}")
    if not errs:
        print("已定义规则内无确定性矛盾(不构成金融数据准确性认证,见NOT_VERIFIED_HERE)")
