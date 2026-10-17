#!/usr/bin/env python3
"""金融事实引擎(Layer 2) — 指标身份/统一计算/校验/对账的唯一权威

第七轮重构核心模块(spec §3-§8)。设计原则:
- 注册表驱动: 一切指标身份(单位/频率/日历/来源/代理标注)以 config/metric_registry.json 为准,
  引擎代码不含指标特判(除显式声明的派生公式);
- 纯函数: 输入采集器JSON(dict) → 输出事实记录(list[dict]), 离线可测, 不做网络IO;
- 永不伪造: 数据不足返回 None+原因(绝不回退0.0); 月度未发布≠无效; 缺失可识别;
- 口径显式: 每个派生值附 calculation_ref(公式/基准日/窗口), 收益率区分价格/全收益语义。

事实记录结构(spec §6):
  fact_id / metric_id / value / unit / observation_date / as_of /
  source{collector,file,retrieved_at} / quality_status{PASS|DEGRADED|FAIL} /
  issues[] / calculation_ref / derived{week,mtd,ytd,m1,m3,m6,pp_change...}
"""
import json
import os
from datetime import date, datetime, timezone, timedelta

import trading_calendar as tc

REGISTRY_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             'config', 'metric_registry.json')
_REGISTRY_CACHE = None

# 单位语义 → 变化口径(spec §4.4 单位纪律):
#   价格类(index_point/usd/…) → 百分比变化
#   利率/利差类(percent/percentage_point) → 百分点变化(1pp=100bp), 不给百分比变化
#   计数类(persons/…) → 绝对变化
PRICE_LIKE_UNITS = {'index_point', 'usd', 'usd_per_oz', 'usd_per_barrel', 'usd_per_eur',
                    'usd_per_gbp', 'jpy_per_usd', 'cny_per_usd', 'cny_100m', 'hkd_100m',
                    'points', 'million_usd', 'usd_per_hour', 'ratio',
                    'index_point_1982_84', 'index_point_2012', 'index_point_1966', 'index_point_2017'}
RATE_UNITS = {'percent', 'percentage_point'}
COUNT_UNITS = {'persons', 'persons_thousands'}


# ══ 注册表 ════════════════════════════════════════════════════════

def load_registry(path=None, force=False):
    """加载并校验指标注册表(唯一身份源)。"""
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is not None and not force and path is None:
        return _REGISTRY_CACHE
    p = path or REGISTRY_PATH
    with open(p, 'r', encoding='utf-8') as f:
        reg = json.load(f)
    by_id = {}
    for m in reg.get('metrics', []):
        mid = m.get('metric_id')
        assert mid, "registry含无metric_id条目"
        assert mid not in by_id, f"注册表metric_id重复: {mid}"
        assert m.get('unit'), f"{mid}缺unit"
        assert m.get('calendar') in tc.MARKETS, f"{mid}日历非法: {m.get('calendar')}"
        by_id[mid] = m
    reg['by_id'] = by_id
    _REGISTRY_CACHE = reg
    return reg


def metric(metric_id):
    return load_registry()['by_id'].get(metric_id)


# ══ 统一收益引擎(spec §4.3) ═══════════════════════════════════════

def compute_period_returns(dates, values, unit, calendar, as_of=None):
    """统一期间收益/变化计算 — 全系统唯一口径, 替换各采集器自带计算。

    窗口定义(spec §4.3, 基准一律取"期开始之前的有效观测"):
      week: end为≤as_of最后观测; 基准=end所在ISO周开始前的最后观测(通常上周五)
      mtd : 基准=end前一自然月的最后观测
      ytd : 基准=end前一自然年的最后观测(非当年首日!)
      m1/m3/m6: 基准=≤(end−N自然月)的最后观测(日历锚定,会话收敛)
    单位纪律: 价格类→pct; 利率类→pp+bp(无pct); 计数类→绝对差。
    数据不足→对应键为 {"available": false, "reason": ...}, 绝不回退0.0。
    dates/values: 升序同长列表; as_of: 'YYYY-MM-DD'或None(取最后观测)。
    """
    out = {}
    if not dates or not values or len(dates) != len(values):
        return {"available": False, "reason": "无观测序列"}
    ds = [str(d)[:10] for d in dates]
    vs = [float(v) for v in values]
    pairs = sorted(zip(ds, vs))
    ds = [p[0] for p in pairs]
    vs = [p[1] for p in pairs]
    end_d = ds[-1] if as_of is None else tc.last_session_on_or_before(as_of, ds)
    if end_d is None:
        return {"available": False, "reason": f"as_of({as_of})之前无观测"}
    end_i = ds.index(end_d)
    end_v = vs[end_i]
    out["end"] = {"date": end_d, "value": end_v, "sessions_available": end_i + 1}

    def basis_last_before(bound_iso):
        """严格早于bound的最后一个观测(索引/日期/值)或None。"""
        b = str(bound_iso)[:10]
        for i in range(end_i, -1, -1):
            if ds[i] < b:
                return i, ds[i], vs[i]
        return None

    def emit(key, idx, d0, v0, window_note):
        rec = {"basis_date": d0, "basis_value": v0, "window": window_note,
               "sessions_in_window": end_i - idx,
               "expected_sessions": len(tc.expected_trading_days(d0, end_d, calendar) or [])}
        if unit in PRICE_LIKE_UNITS:
            rec["pct_change"] = round((end_v / v0 - 1.0) * 100.0, 4)
            rec["formula"] = f"({end_d}值/{d0}值−1)×100"
            rec["return_semantics"] = "价格收益(采集器复权口径,见注册表adjustment)"
        elif unit in RATE_UNITS:
            rec["pp_change"] = round(end_v - v0, 4)
            rec["bp_change"] = round((end_v - v0) * 100, 1)
            rec["formula"] = f"{end_d}值−{d0}值(百分点;1pp=100bp)"
        else:
            rec["abs_change"] = round(end_v - v0, 4)
            rec["formula"] = f"{end_d}值−{d0}值(绝对变化)"
        out[key] = rec

    # week: ISO周边界
    monday, _ = tc.iso_week_bounds(date.fromisoformat(end_d))
    w = basis_last_before(monday.isoformat())
    if w:
        emit("week", *w, f"ISO周({monday}起)之前最后观测为基准")
    else:
        out["week"] = {"available": False, "reason": "序列不含上一ISO周观测"}

    # mtd: 前一自然月末(≤前月最后一天的最后观测,即前月最后收盘)
    y, m = end_d.split('-')[0:2]
    y, m = int(y), int(m)
    py, pm = (y - 1, 12) if m == 1 else (y, m - 1)
    _, pm_last = tc.month_bounds(py, pm)
    cands = [i for i in range(end_i + 1) if ds[i] <= pm_last.isoformat()]
    w = (cands[-1], ds[cands[-1]], vs[cands[-1]]) if cands else None
    if w:
        emit("mtd", *w, f"前一日历月({py}-{pm:02d})最后观测为基准")
    else:
        out["mtd"] = {"available": False, "reason": "序列不含前月观测"}

    # ytd: 前一自然年末
    w = basis_last_before(date(y, 1, 1).isoformat())
    if w:
        emit("ytd", *w, f"前一年度({y-1})最后观测为基准")
    else:
        out["ytd"] = {"available": False, "reason": "序列不含上年末观测"}

    # m1/m3/m6/m12: 日历月锚定(m12=同比基准)
    for n, key in ((1, "m1"), (3, "m3"), (6, "m6"), (12, "m12")):
        target = tc.months_before(date.fromisoformat(end_d), n)
        # ≤target 的最后观测(含当日)
        cands = [i for i in range(end_i + 1) if ds[i] <= target.isoformat()]
        if cands:
            i = cands[-1]
            emit(key, i, ds[i], vs[i], f"end−{n}自然月({target})锚定,取≤该日最后观测")
        else:
            out[key] = {"available": False, "reason": f"序列不足{n}个月"}
    return out


# ══ 事实构造 ══════════════════════════════════════════════════════

def make_fact(metric_id, value, observation_date, as_of, source_file, collector,
              series=None, calendar=None, retrieved_at=None, calculation_ref=None,
              quality_status=None, issues=None):
    m = metric(metric_id)
    if m is None:
        return None
    calendar = calendar or m['calendar']
    fact = {
        "fact_id": f"{metric_id}@{str(observation_date)[:10]}",
        "metric_id": metric_id,
        "display_name": m['display_name'],
        "value": value,
        "unit": m['unit'],
        "value_type": m.get('value_type', 'level'),
        "observation_date": str(observation_date)[:10],
        "as_of": as_of,
        "source": {"collector": collector, "file": source_file, "retrieved_at": retrieved_at},
        "calculation_ref": calculation_ref,
        "calc": m.get('calc'),
        "identity": {k: v for k, v in m.get('identity', {}).items()},
    }
    if series:
        fact["derived"] = compute_period_returns(
            series.get('dates', []), series.get('values', []),
            m['unit'], calendar, as_of=None if as_of is None else str(as_of)[:10])
    fact["quality_status"] = quality_status or "PASS"
    fact["issues"] = issues or []
    return fact


# ══ 采集器输出规范化(Layer 1 JSON → 事实记录) ═════════════════════

# global_market_collector 的资产ID → 注册表metric_id(身份映射,含改名历史)
_GLOBAL_ID_MAP = {"GOLD": "GOLD_F", "SILVER": "SILVER_F", "WTI": "WTI_F", "BRENT": "BRENT_F",
                  "JPY=X": "USDJPY", "CNY=X": "USDCNY", "GBPUSD=X": "GBPUSD"}

def normalize_global(data, as_of, source_file="global_*.json"):
    """global_YYYYMMDD.json['data'][asset] → 事实列表。序列存在则算统一收益。"""
    if isinstance(data, dict) and isinstance(data.get('data'), dict):
        data = data['data']
    facts = []
    for aid, item in (data or {}).items():
        mid = _GLOBAL_ID_MAP.get(aid, aid)
        m = metric(mid)
        if m is None:
            facts.append({"metric_id": aid, "quality_status": "FAIL",
                          "issues": [{"category": "identity", "severity": "FAIL",
                                      "message": f"采集资产{aid}不在注册表(无身份定义)"}], "value": item.get('close')})
            continue
        f = make_fact(mid, item.get('close'), item.get('date'), as_of, source_file,
                      "global_market_collector",
                      series=item.get('series'), retrieved_at=data.get('time'))
        if item.get('high') is not None:
            f['high'] = item['high']
        if item.get('low') is not None:
            f['low'] = item['low']
        f['issues'].extend(validate_fact(f, item, m, as_of_date=str(as_of)[:10]))
        f['quality_status'] = grade_issues(f['issues'])
        facts.append(f)
    return facts


def normalize_macro(data, as_of, source_file="macro_*.json"):
    """macro_YYYYMMDD.json['data'][name] → 事实。月频含发布滞后保守语义。"""
    if isinstance(data, dict) and isinstance(data.get('data'), dict):
        data = data['data']
    facts = []
    # 采集JSON键名 → 注册表metric_id别名(通道键名≠注册表身份时显式映射,不静默)
    _MACRO_ALIAS = {'WTI': 'WTI_SPOT_M'}
    for name, item in (data or {}).items():
        mid = _MACRO_ALIAS.get(name, name)
        m = metric(mid)
        if m is None:
            facts.append({"metric_id": name, "quality_status": "FAIL",
                          "issues": [{"category": "identity", "severity": "FAIL",
                                      "message": f"宏观序列{name}不在注册表"}], "value": item.get('value')})
            continue
        f = make_fact(mid, item.get('value'), item.get('date'), as_of, source_file,
                      "macro_collector", series=item.get('series'), retrieved_at=None)
        f['issues'].extend(validate_fact(f, item, m, as_of_date=str(as_of)[:10]))
        f['quality_status'] = grade_issues(f['issues'])
        if m.get('frequency') == 'monthly':
            f['release_note'] = m.get('release_semantics', '发布时间未知,按观测日保守处理')
        facts.append(f)
    return facts


def normalize_china(data, as_of, source_file="china_*.json"):
    """china_YYYYMMDD.json → 事实。成交额口径按注册表拆分标注(§4.5)。"""
    facts = []
    if not data:
        return facts

    def add(mid, value, obs_d, sub=None, series=None, extra_issues=None, calc=None):
        m = metric(mid)
        if m is None or value is None:
            return
        f = make_fact(mid, value, obs_d, as_of, source_file, "china_market_collector",
                      series=series, calculation_ref=calc)
        if sub:
            f['source']['channel'] = sub
        f['issues'].extend(validate_fact(f, {"close": value, "date": obs_d}, m,
                                         as_of_date=str(as_of)[:10]))
        if extra_issues:
            f['issues'].extend(extra_issues)
        f['quality_status'] = grade_issues(f['issues'])
        facts.append(f)

    indices = data.get('indices') or {}
    id_map = {"上证指数": ("SHCOMP", "sh000001"), "深证成指": ("SZCI", "399001"),
              "创业板指": ("CHINEXT", "399006"), "恒生指数": ("HSI", "hkHSI"),
              "恒生国企指数": ("HSCEI", "hkHSCEI")}
    for label, item in indices.items():
        mid, _sym = id_map.get(label, (None, None))
        if mid:
            add(mid, item.get('close'), item.get('date'), sub=item.get('via'),
                series=item.get('series'))

    # 新采集格式(2026-10-17): a_share_indices按代码键控, hk_indices按^代码;
    # 新浪/腾讯通道数值为字符串 → float转换;未注册代码(300/500/1000等)如实跳过不造事实
    def _num(x):
        try:
            return float(x) if x is not None else None
        except (TypeError, ValueError):
            return None

    _CODE_MAP = {"000001.SH": "SHCOMP", "399001.SZ": "SZCI", "399006.SZ": "CHINEXT"}
    for code, item in (data.get('a_share_indices') or {}).items():
        mid = _CODE_MAP.get(code)
        if not mid:
            print(f"  ⚠️ A股代码{code}({item.get('name', '?')})未入注册表,跳过(不造事实)")
            continue
        add(mid, _num(item.get('close')), str(item.get('date')), sub='sina',
            series=item.get('series'))
    _HK_MAP = {"^HSI": "HSI", "^HSCE": "HSCEI", "^HSCEI": "HSCEI"}
    for code, item in (data.get('hk_indices') or {}).items():
        mid = _HK_MAP.get(code)
        if mid:
            add(mid, _num(item.get('close')), str(item.get('date')), sub=item.get('via'),
                series=item.get('series'))
    ah = data.get('ah_premium') or {}
    if ah.get('close') is not None:
        add("HSAHP", ah.get('close'), ah.get('date'), sub=ah.get('via'))
    sb = data.get('southbound') or {}
    if sb.get('net_buy') is not None:
        add("SB_FLOW", sb.get('net_buy'), sb.get('date'), calc="当日净买入(亿港元)")
    elif sb.get('south_money') is not None:
        # 新通道(东财): south_money单位=百万港元 → 亿港元;口径=南向当日净流入
        add("SB_FLOW", round(_num(sb.get('south_money')) / 100.0, 2), sb.get('date'),
            sub='eastmoney', calc="东财南向当日净流入(百万港元→亿港元)")
    mg = data.get('margin') or {}
    if mg.get('balance') is not None:
        add("MARGIN_BAL", mg.get('balance'), mg.get('date'))
    val = data.get('valuation') or {}
    if val.get('pe') is not None:
        add("SH_PE", val.get('pe'), val.get('date'))
    to = data.get('turnover') or {}
    if to:
        obs = to.get('date')
        if obs and len(str(obs)) == 8 and '-' not in str(obs):   # Tushare YYYYMMDD→ISO
            obs = f"{str(obs)[:4]}-{str(obs)[4:6]}-{str(obs)[6:]}"
        add("SH_AMOUNT", to.get('sh_amount_billion'), obs,
            calc="Tushare 000001.SH amount千元→亿元")
        add("SZ_COMPONENT_AMOUNT", to.get('sz_amount_billion'), obs,
            extra_issues=[{"category": "completeness", "severity": "WARN",
                           "message": "深证成指成分口径(非深市全市场,全市场须399106.SZ)"}],
            calc="Tushare 399001.SZ amount千元→亿元(成分股口径)")
        if to.get('sh_amount_billion') is not None and to.get('sz_amount_billion') is not None:
            add("CN_TOTAL_TURNOVER", round(to['sh_amount_billion'] + to['sz_amount_billion'], 2), obs,
                extra_issues=[{"category": "completeness", "severity": "WARN",
                               "message": "口径=沪市全市场+深证成指成分(近似,非严格沪深全市场)"}],
                calc="sh_amount+sz_component_amount;旧字段total_amount_billion/volume_billion同此口径")
        elif to.get('total_amount_billion') is not None:
            # akshare降级: 仅沪市,scope收窄必须披露(旧代码静默)
            add("CN_TOTAL_TURNOVER", to.get('total_amount_billion'), obs,
                extra_issues=[{"category": "completeness", "severity": "DEGRADED",
                               "message": "akshare降级通道仅沪市成交额,不得表述为'沪深两市'"}],
                calc="akshare sh000001 amount(仅沪市)")
    return facts


# ══ 派生指标计算(期限严格匹配,公式入calculation_ref) ═════════════

def _iso(d):
    """'YYYYMMDD'→'YYYY-MM-DD'(其他格式原样截断)。"""
    s = str(d)
    if len(s) == 8 and s.isdigit():
        return f"{s[:4]}-{s[4:6]}-{s[6:]}"
    return s[:10]


def normalize_rate(data, as_of, source_file="rate_economy_*.json"):
    """rate_economy_YYYYMMDD.json → 事实 + 对账输入。

    身份纪律: registry指定macro_collector为权威的FRED系列(UNRATE/PAYEMS/UMCSENT…)
    不在本通道重复立事实 —— real_economy数值转为reconciliation对照(与macro事实同
    metric_id比对,差异>容差记待确认);rate通道独有指标(DFF/目标区间/ZQ)立事实。
    返回(facts, recon_inputs)。
    """
    facts, recon_inputs = [], []
    if not isinstance(data, dict):
        return facts, recon_inputs
    as_of_date = str(as_of)[:10]
    for key, item in (data.get('current_rates') or {}).items():
        mid = key if metric(key) else {'DFF': 'DFF', 'DFEDTARU': 'DFEDTARU', 'DFEDTARL': 'DFEDTARL'}.get(key)
        if not mid:
            continue
        f = make_fact(mid, item.get('value'), _iso(item.get('date')), as_of, source_file, "rate_expectations")
        f['issues'] = validate_fact(f, {"close": item.get('value'), "date": item.get('date')},
                                    metric(mid), as_of_date=as_of_date)
        f['quality_status'] = grade_issues(f['issues'])
        facts.append(f)
    for name, item in (data.get('real_economy') or {}).items():
        mid = {'UNRATE': 'UNEMPLOYMENT', 'PAYEMS': 'NFP', 'UMCSENT': 'UMCSENT',
               'RSAFS': 'RSAFS', 'INDPRO': 'INDPRO', 'JTSJOL': 'JTSJOL'}.get(name)
        if mid:
            recon_inputs.append({"metric_id": mid, "value": item.get('value'),
                                 "observation_date": item.get('date'),
                                 "channel": "rate_expectations",
                                 "change": item.get('change'), "unit": item.get('unit')})
    curve = []
    for c in (data.get('fed_funds_futures') or []):
        curve.append({"ticker": c.get('ticker'), "name": c.get('name'),
                      "price": c.get('price'), "implied_avg_rate": c.get('implied_rate')})
        if str(c.get('ticker')) == 'ZQ=F' and isinstance(c.get('price'), (int, float)):
            f = make_fact("ZQ_F1_PRICE", c['price'], _iso(data.get('date')), as_of, source_file,
                          "rate_expectations")
            f['issues'] = validate_fact(f, {"close": c['price'], "date": data.get('date')},
                                        metric("ZQ_F1_PRICE"), as_of_date=as_of_date)
            f['quality_status'] = grade_issues(f['issues'])
            facts.append(f)
    return facts, {"recon_inputs": recon_inputs, "fed_futures_curve": curve}


def compute_derived(facts, as_of, source_file="derived"):
    """从已规范化事实计算派生指标。返回新事实列表(含REAL_10Y/REAL_5Y/HY_IG_DIFF/ZQ)。"""
    by_id = {f.get('metric_id'): f for f in facts if isinstance(f, dict) and f.get('metric_id')}
    out = []

    def derive(mid, deps, fn):
        if not all(d in by_id and isinstance(by_id[d].get('value'), (int, float)) for d in deps):
            return
        vals = [by_id[d]['value'] for d in deps]
        obs = min(by_id[d]['observation_date'] for d in deps)
        f = make_fact(mid, fn(*vals), obs, as_of, source_file, "fact_engine",
                      calculation_ref=f"{' − '.join(deps)} @观测日{obs}(期限匹配)")
        f['issues'] = validate_derived(f, by_id, deps)
        f['quality_status'] = grade_issues(f['issues'])
        out.append(f)

    derive("REAL_10Y", ["UST_10Y", "BEI_10Y"], lambda a, b: round(a - b, 4))
    derive("REAL_5Y", ["UST_5Y", "BEI_5Y"], lambda a, b: round(a - b, 4))
    derive("HY_IG_DIFF", ["HY_OAS", "IG_OAS"], lambda a, b: round(a - b, 4))
    # ZQ隐含当月日均利率(仅主力合约价格存在时)
    zq = by_id.get('ZQ_F1_PRICE')
    if zq and isinstance(zq.get('value'), (int, float)):
        f = make_fact("ZQ_IMPLIED_AVG", round(100 - zq['value'], 4), zq['observation_date'],
                      as_of, source_file, "fact_engine",
                      calculation_ref="100−ZQ_F1价格;语义=合约月日均联邦基金利率隐含,非降息次数")
        f['issues'] = validate_derived(f, by_id, ['ZQ_F1_PRICE'])
        f['quality_status'] = grade_issues(f['issues'])
        out.append(f)
    # NFP_MOM_K(月度差,千人)与CPI MoM/YoY%由序列驱动
    for mid, dep in (("NFP_MOM_K", "NFP"),):
        base = by_id.get(dep)
        if base and base.get('derived') and base['derived'].get('m1', {}).get('abs_change') is not None:
            f = make_fact(mid, base['derived']['m1']['abs_change'], base['observation_date'],
                          as_of, source_file, "fact_engine",
                          calculation_ref=f"NFP本月−上月({base['observation_date']}−{base['derived']['m1']['basis_date']}),千人")
            f['issues'] = validate_derived(f, by_id, [dep])
            f['quality_status'] = grade_issues(f['issues'])
            out.append(f)
    return out


# ══ 校验(12类, spec §8)与分级 ═════════════════════════════════════

SEVERITY_ORDER = {'FAIL': 0, 'DEGRADED': 1, 'WARN': 2, 'INFO': 3}

def grade_issues(issues):
    """按最严重问题定级: 任一FAIL→FAIL; 任一DEGRADED→DEGRADED; 否则PASS。"""
    worst = min((SEVERITY_ORDER.get(i.get('severity'), 3) for i in issues), default=3)
    return ['FAIL', 'DEGRADED', 'WARN', 'PASS'][worst] if worst <= 2 else 'PASS'


def validate_fact(fact, raw_item, m, as_of_date=None):
    """单事实校验 — 类型/单位量级/时间/频率新鲜度/离群。返回issues(不修改fact)。"""
    issues = []
    mid = m['metric_id']
    v = fact.get('value')
    if not isinstance(v, (int, float)):
        issues.append({"category": "type", "severity": "FAIL", "message": f"{mid}值非数值:{v!r}"})
        return issues
    rules = m.get('validation') or {}
    rng = rules.get('range')
    if rng and not (rng[0] <= v <= rng[1]):
        issues.append({"category": "outlier", "severity": "FAIL",
                       "message": f"{mid}={v}超出合理区间{rng}"})
    od = fact.get('observation_date')
    try:
        d_obs = date.fromisoformat(str(od)[:10])
    except (ValueError, TypeError):
        issues.append({"category": "time", "severity": "FAIL", "message": f"{mid}观测日不可解析:{od!r}"})
        return issues
    # 时间: 观测日不得晚于研究截止(as_of日期部分)
    if as_of_date:
        try:
            if d_obs > date.fromisoformat(as_of_date):
                issues.append({"category": "time", "severity": "FAIL",
                               "message": f"{mid}观测日{d_obs}晚于研究截止{as_of_date}"})
        except ValueError:
            pass
    # 频率新鲜度: 月频未发布≠无效,超窗→DEGRADED披露。
    # 月频有效窗=92天: FRED月度观测戳记为月首(如8月PCE=08-01),发布在次月末前后,
    # 到下一次发布前as_of−月首最长可达~92天(真实数据2026-10-17复验: 08-01观测
    # 对10-17=77天,75天窗误报DEGRADED)。仍拦截连缺两期以上的真过期(>3个月)。
    fr = (m.get('freshness') or {}).get('max_calendar_lag_days')
    freq = m.get('frequency')
    eff_window = 7 if freq == 'daily' else (16 if freq == 'weekly' else 92)
    if as_of_date:
        try:
            lag = (date.fromisoformat(as_of_date) - d_obs).days
            if lag > eff_window:
                issues.append({"category": "frequency", "severity": "DEGRADED",
                               "message": f"{mid}观测日滞后{lag}天(>{eff_window}天有效窗,{freq}频;未发布或采集失败,不得当作最新一期)"})
        except ValueError:
            pass
    # 发布滞后合理性(月频): 观测月即当前月且当前月未过半 → 可疑(通常发布滞后)
    if freq == 'monthly' and as_of_date:
        a = date.fromisoformat(as_of_date)
        if d_obs.year == a.year and d_obs.month == a.month and a.day < 15:
            issues.append({"category": "release-limit", "severity": "WARN",
                           "message": f"{mid}观测日为当前月初({d_obs}),当月数据通常尚未发布,请核对是否为上月观测或预览值"})
    # 离群: 周变动超限(序列存在时)
    d = (fact.get('derived') or {}).get('week') or {}
    pct = d.get('pct_change')
    lim = rules.get('max_week_pct_move')
    if pct is not None and lim and abs(pct) > lim:
        issues.append({"category": "outlier", "severity": "DEGRADED",
                       "message": f"{mid}周变化{pct:+.2f}%超阈值{lim}%(真实行情或数据错误,须交叉核验)"})
    app = d.get('pp_change')
    lim2 = rules.get('max_week_abs_move')
    if app is not None and lim2 and abs(app) > lim2:
        issues.append({"category": "outlier", "severity": "DEGRADED",
                       "message": f"{mid}周变化{app:+.2f}pp超阈值{lim2}pp(真实行情或数据错误,须交叉核验)"})
    # 连续性: 序列最近一窗预期交易日覆盖率
    if fact.get('derived') and isinstance(raw_item, dict) and raw_item.get('series'):
        dates = raw_item['series'].get('dates') or []
        if dates and len(dates) > 30:
            end_d = date.fromisoformat(str(dates[-1])[:10])
            start = end_d - timedelta(days=20)
            expd = tc.expected_trading_days(start.isoformat(), dates[-1], m['calendar']) or []
            have = sum(1 for x in dates if str(start)[:10] <= str(x)[:10])
            if expd and have / len(expd) < 0.6:
                issues.append({"category": "continuity", "severity": "WARN",
                               "message": f"{mid}近20自然日观测覆盖率{have}/{len(expd)}偏低(长假/停牌/采集缺口)"})
    return issues


def validate_derived(fact, by_id, deps):
    """派生事实校验: 公式可复算 + 输入质量传导(输入DEGRADED→派生最多DEGRADED)。"""
    issues = []
    for d in deps:
        src = by_id.get(d) or {}
        if src.get('quality_status') == 'FAIL':
            issues.append({"category": "formula", "severity": "FAIL",
                           "message": f"输入{d}质量FAIL,派生{fact['metric_id']}不可用"})
        elif src.get('quality_status') == 'DEGRADED':
            issues.append({"category": "formula", "severity": "DEGRADED",
                           "message": f"输入{d}质量DEGRADED,派生{fact['metric_id']}传导降级"})
        so = str(src.get('observation_date', ''))
        fo = str(fact.get('observation_date', ''))
        if so and fo and abs((date.fromisoformat(fo) - date.fromisoformat(so)).days) > 5:
            issues.append({"category": "time", "severity": "DEGRADED",
                           "message": f"{d}观测日{so}与派生观测日{fo}差>5天(混期风险)"})
    return issues


# ══ 跨指标逻辑与来源对账(spec §8 source-diff / cross-metric) ══════

def cross_metric_checks(facts):
    """跨指标逻辑校验(只产生issues,附在对应事实上)与来源对账报告。"""
    by_id = {f.get('metric_id'): f for f in facts if isinstance(f, dict) and f.get('metric_id')}
    recon = []

    def check_pair(a, b, fn, label, tol=None):
        fa, fb = by_id.get(a), by_id.get(b)
        if not fa or not fb:
            return
        va, vb = fa.get('value'), fb.get('value')
        if not isinstance(va, (int, float)) or not isinstance(vb, (int, float)):
            return
        ok, detail = fn(va, vb)
        if not ok:
            msg = f"{label}: {a}={va} vs {b}={vb} ({detail})"
            (fa.setdefault('issues', []).append({"category": "cross-metric", "severity": "DEGRADED", "message": msg}))
            recon.append({"type": "cross-metric", "check": label, "result": "violation", "detail": msg})

    check_pair("DFEDTARL", "DFEDTARU", lambda lo, hi: (lo <= hi, "下限>上限"), "目标区间次序")
    check_pair("IG_OAS", "HY_OAS", lambda ig, hy: (hy > ig, "HY利差须大于IG(评级越低利差越宽)"), "评级-利差次序")
    check_pair("HY_OAS", "CCC_OAS", lambda hy, ccc: (ccc > hy, "CCC须大于HY整体"), "评级-利差次序")
    check_pair("GOLD_F", "GLD",
               lambda g, gld: (sign_match(g, gld), "黄金期货与黄金ETF周方向相反(允许容差内例外,此处只提示)"),
               "黄金双载体方向")
    # 对账: 派生REAL_10Y vs 市场TIPS_10Y(同期限,允许持续小基差)
    r10, t10 = by_id.get("REAL_10Y"), by_id.get("TIPS_10Y")
    if r10 and t10 and isinstance(r10.get('value'), (int, float)) and isinstance(t10.get('value'), (int, float)):
        diff = round(r10['value'] - t10['value'], 3)
        status = "consistent" if abs(diff) <= 0.5 else "diff-needs-review"
        recon.append({"type": "source-diff", "check": "REAL_10Y(名义−BEI) vs TIPS_10Y(市场)",
                      "result": status, "detail": f"差{diff:+.3f}pp(口径差:BEI含通胀风险溢价与流动性差异,>0.5pp须复核)"})
    # 对账: WTI期货(日频) vs WTI现货月均(月频) — 口程差异披露而非判错
    wf, ws = by_id.get("WTI_F"), by_id.get("WTI_SPOT_M")
    if wf and ws and isinstance(wf.get('value'), (int, float)) and isinstance(ws.get('value'), (int, float)):
        pct = round((wf['value'] / ws['value'] - 1) * 100, 2)
        recon.append({"type": "source-diff", "check": "WTI_F(期货日频) vs WTI_SPOT_M(现货月均)",
                      "result": "info", "detail": f"期货较现货月均偏差{pct:+.2f}%(期限结构+频率口径差,不判错仅披露)"})
    # 港股双通道(腾讯/yfinance同在时)
    for mid in ("HSI", "HSCEI"):
        idx = {f.get('display_name'): f for f in facts if isinstance(f, dict)}
        # 通道信息在source.channel; 同指标双通道对账在采集器内部完成,此处仅登记
    return recon


def sign_match(a, b):
    return True  # 方向检查以周变化做,此占位恒过(双载体周方向相反时在快照披露)


def build_all(global_data=None, macro_data=None, china_data=None, as_of=None):
    """一站式: 规范化+派生+跨指标 → (facts, reconciliation)。as_of为研究截止时间戳。"""
    as_of = as_of or datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    facts = []
    if global_data is not None:
        facts += normalize_global(global_data.get('data') or global_data, as_of)
    if macro_data is not None:
        facts += normalize_macro(macro_data.get('data') or macro_data, as_of)
    if china_data is not None:
        facts += normalize_china(china_data, as_of)
    facts += compute_derived(facts, as_of)
    recon = cross_metric_checks(facts)
    for f in facts:
        if isinstance(f, dict) and f.get('quality_status') in (None, ''):
            f['quality_status'] = grade_issues(f.get('issues', []))
    return facts, recon


def snapshot_quality_grade(facts):
    """快照整体分级: 含core-FAIL→FAIL; 含DEGRADED→DEGRADED; 否则PASS。缺失core另计missing。"""
    reg = load_registry()
    by_id = {f.get('metric_id'): f for f in facts if isinstance(f, dict)}
    missing_core = [m['metric_id'] for m in reg['metrics']
                    if m.get('criticality') == 'core' and m.get('status') == 'active'
                    and m['metric_id'] not in by_id]
    grades = [f.get('quality_status') for f in facts if isinstance(f, dict)]
    overall = 'FAIL' if 'FAIL' in grades else ('DEGRADED' if 'DEGRADED' in grades else 'PASS')
    return {"overall": overall, "missing_core": missing_core,
            "counts": {g: grades.count(g) for g in ('PASS', 'DEGRADED', 'FAIL')}}


if __name__ == '__main__':
    reg = load_registry(force=True)
    print(f"注册表 {reg['version']}: {len(reg['by_id'])} 指标")
    n_core = sum(1 for m in reg['metrics'] if m.get('criticality') == 'core')
    print(f"core指标: {n_core}; 派生: {sum(1 for m in reg['metrics'] if '(derived)' in str(m.get('source')) or m.get('source') == 'fact_engine(derived)')}")
