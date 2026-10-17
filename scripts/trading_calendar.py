#!/usr/bin/env python3
"""交易交易日历(Layer 2 金融事实引擎组件) — 全系统唯一日历权威

来源: 2026-10-17 从 allocation_engine.py:685-800 抽取(原第五轮P0-2实现,已有测试覆盖),
allocation_engine 反向 import 保持兼容。新增 us_rates/fx/commodity 市场与
收益引擎所需的期界辅助函数(ISO周边界/期内最后交易日/前N月锚定)。

安全原则(继承): 只把"确定不交易"的日子排除 — 宁可多预期一天(判inconclusive),
绝不漏掉真实交易日(防止假miss/假覆盖完整)。无法确定的组合保守视为交易日。

日历口径注册表:
  us_equity  NYSE规则(周末+固定节+浮动节,周末顺延) — SPX/NDX/个股/ETF/VIX
  us_rates   美债与FRED日频序列 — 近似按NYSE(DGS/DFII/T5YIE为日历日发布,无交易所结算;
             FRED日频序列在非NYSE日无新观测,该近似与实际一致)
  commodity  CME商品期货 — 近似按NYSE(CME个别半日/全日交易的差异影响<1个自然日,
             对周度窗口无实质影响;标注为近似)
  cn         A股 — 周末 + 中国长假块(仅2026精确,其余年份保守只除周末)
  hk         港股 — 最小集(周末+01-01+12-25,保守:少排除一个假日只影响窗口标注精度)
  fx         全球外汇 — 周一至周五(24/5,节假日近似为全工作日)
  crypto     7×24 全天候
"""
import calendar as _calmod
from datetime import date, timedelta

__all__ = ['MARKETS', 'is_trading_day', 'expected_trading_days', 'prev_trading_day',
           'last_trading_day_on_or_before', 'last_session_on_or_before',
           'iso_week_bounds', 'month_bounds', 'year_bounds', 'months_before',
           'snap_to_session', 'sessions_between']

MARKETS = ('us_equity', 'us_rates', 'commodity', 'cn', 'hk', 'fx', 'crypto')

_CN_HOLIDAY_BLOCKS = {
    2026: {'01-01', '01-02',                # 元旦
           '02-16', '02-17', '02-18', '02-19', '02-20',  # 春节核心周(除夕2-16,初一2-17)
           '04-06',                          # 清明(4-5为周日,顺延观测)
           '05-01', '05-04', '05-05',        # 劳动节
           '06-19',                          # 端午
           '09-25',                          # 中秋
           '10-01', '10-02', '10-05', '10-06', '10-07'},  # 国庆(10-03/04为周末)
}
_US_HOLIDAY_CACHE = {}


def _nth_weekday(y, m, weekday, n):
    """当月第n个星期weekday(0=周一…6=周日)"""
    first = date(y, m, 1)
    return first + timedelta(days=(weekday - first.weekday()) % 7 + 7 * (n - 1))


def _last_weekday(y, m, weekday):
    last = date(y, m, _calmod.monthrange(y, m)[1])
    return last - timedelta(days=(last.weekday() - weekday) % 7)


def _easter(y):
    """复活节周日(匿名格雷高利算法,只用于推耶稣受难日=复活节-2天)"""
    a = y % 19
    b, c = divmod(y, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    return date(y, (h + l - 7 * m + 114) // 31, ((h + l - 7 * m + 114) % 31) + 1)


def _us_holidays(y):
    if y in _US_HOLIDAY_CACHE:
        return _US_HOLIDAY_CACHE[y]
    raw = {date(y, 1, 1), _nth_weekday(y, 1, 0, 3), _nth_weekday(y, 2, 0, 3),
           _easter(y) - timedelta(days=2), _last_weekday(y, 5, 0), date(y, 6, 19),
           date(y, 7, 4), _nth_weekday(y, 9, 0, 1), _nth_weekday(y, 11, 3, 4),
           date(y, 12, 25)}
    out = set()
    for d in raw:                      # 周六→周五休市,周日→周一休市(NYSE惯例)
        out.add(d - timedelta(days=1) if d.weekday() == 5
                else d + timedelta(days=1) if d.weekday() == 6 else d)
    _US_HOLIDAY_CACHE[y] = out
    return out


def is_trading_day(d, market):
    """d为date或'YYYY-MM-DD'。crypto全天候;其余周末一律非交易日;
    节假日按市场日历;无法确定的(日,市场)组合保守视为交易日(宁可inconclusive不假miss)。"""
    try:
        dt = d if isinstance(d, date) else date.fromisoformat(str(d)[:10])
    except ValueError:
        return True
    if market == 'crypto':
        return True
    if dt.weekday() >= 5:
        return False
    md = dt.strftime('%m-%d')
    if market in ('us_equity', 'us_rates', 'futures', 'us', 'commodity'):
        return dt not in _us_holidays(dt.year)
    if market == 'cn':
        return md not in _CN_HOLIDAY_BLOCKS.get(dt.year, set())
    if market == 'hk':
        return md not in ('01-01', '12-25')
    if market == 'fx':
        return True
    return True


def expected_trading_days(start, end, market, upto=None):
    """观察窗[start,end]内该市场的预期交易日清单(upto: 只统计到该日,渲染用)。
    返回None表示窗口本身无法确定 → 覆盖不可判(不得假装完整)。"""
    try:
        s = date.fromisoformat(str(start)[:10])
        e = date.fromisoformat(str(end)[:10])
        if upto is not None:
            e = min(e, date.fromisoformat(str(upto)[:10]))
    except ValueError:
        return None
    if e < s:
        return []
    days, cur = [], s
    while cur <= e:
        if is_trading_day(cur, market):
            days.append(cur.isoformat())
        cur += timedelta(days=1)
    return days


# ══ 收益引擎期界辅助 ══════════════════════════════════════════════

def last_trading_day_on_or_before(d, market):
    """≤d 的最近预期交易日(按日历推,不依赖实际观测)。"""
    try:
        dt = d if isinstance(d, date) else date.fromisoformat(str(d)[:10])
    except ValueError:
        return None
    for _ in range(14):
        if is_trading_day(dt, market):
            return dt
        dt -= timedelta(days=1)
    return None


def last_session_on_or_before(d, dates):
    """实际观测序列 dates(升序ISO串)中 ≤d 的最后一个观测日(实际数据驱动)。"""
    ds = str(d)[:10]
    prior = [x for x in dates if str(x)[:10] <= ds]
    return str(prior[-1])[:10] if prior else None


def prev_trading_day(d, market):
    """严格早于 d 的最近预期交易日。"""
    try:
        dt = (d if isinstance(d, date) else date.fromisoformat(str(d)[:10])) - timedelta(days=1)
    except ValueError:
        return None
    for _ in range(14):
        if is_trading_day(dt, market):
            return dt
        dt -= timedelta(days=1)
    return None


def iso_week_bounds(d):
    """d 所在 ISO 周的周一/周日(date对)。"""
    dt = d if isinstance(d, date) else date.fromisoformat(str(d)[:10])
    monday = dt - timedelta(days=dt.weekday())
    return monday, monday + timedelta(days=6)


def month_bounds(y, m):
    """自然月边界。"""
    last = _calmod.monthrange(y, m)[1]
    return date(y, m, 1), date(y, m, last)


def year_bounds(y):
    return date(y, 1, 1), date(y, 12, 31)


def months_before(d, n):
    """d 减 n 个自然月(日历锚定,月末日自动收敛,如3-31−1月→2-28/29)。"""
    dt = d if isinstance(d, date) else date.fromisoformat(str(d)[:10])
    y, m = dt.year, dt.month - n
    while m <= 0:
        m += 12
        y -= 1
    day = min(dt.day, _calmod.monthrange(y, m)[1])
    return date(y, m, day)


def sessions_between(dates, start, end):
    """dates 中落在(start,end]区间(ISO串,含端不含起)的观测数。"""
    s, e = str(start)[:10], str(end)[:10]
    return sum(1 for x in dates if s < str(x)[:10] <= e)
