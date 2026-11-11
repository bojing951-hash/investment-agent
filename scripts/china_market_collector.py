"""
A股/港股数据采集模块 v2.1
数据源：Tushare（A股主力）+ 腾讯ifzq直连（港股主通道）+ yfinance（港股备用）+ 新浪直连（AH溢价主通道）
2026-10-17修复：恒指/国企yfinance连续4日429限流、东财push2在当前网络直连/代理双双被断
（SSLError/ProxyError）→ 境内源一律直连不走系统代理，境外源(yfinance)保持走代理。
"""

import os
import sys
import json
import re
import time
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from contextlib import contextmanager

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from env_config import TUSHARE_TOKEN

import tushare as ts
import yfinance as yf

# ============ 配置 ============
PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(PROJECT_DIR, 'data')

# tushare pro客户端**惰性初始化**(FIX3-04 CI可移植性): pro_api对空token会回退读
# 本地凭证文件(~/.tushare.yaml),干净机器(CI/新clone)无凭证→模块导入即
# raise 'api init error',离线测试连import都被阻断。改为采集调用点经_pro()取用;
# token在场时行为与原模块级初始化完全一致(同一pro_api同一token)。
_pro_client = None


def _pro():
    global _pro_client
    if _pro_client is None:
        _pro_client = ts.pro_api(TUSHARE_TOKEN)
    return _pro_client


# ============ 方案A限流间隔(W5-RERUN T1/范围D, 2026-11-03) ============
# 实证(FIX3 §六附则/操作者2026-11-01实测): tushare index_daily 对同账号相邻
# 快速连发按"1次/分钟"限流——A_SHARE_INDICES 字典序第2只(399001.SZ)在无
# 间隔连发下必然"频率超限",且SZCI无备源→结构性死路(任何零代码重跑必缺SZCI
# →Gate A core FAIL)。本模块所有 index_daily 调用统一经 _index_daily 发起:
# 全局单调时钟保证任意相邻两次调用(无论成败、无论所在函数)间隔
# ≥ INDEX_DAILY_MIN_INTERVAL_SECONDS;已超出间隔的调用不额外等待。
# 清单/字典序/接口选择/参数/备源回落/import 依赖零变化(仅加间隔)。
INDEX_DAILY_MIN_INTERVAL_SECONDS = 61
_index_daily_last_ts = 0.0


def _index_daily(**kwargs):
    """index_daily 调用闸门(方案A): 相邻调用间隔≥61s;接口与参数零变化。"""
    global _index_daily_last_ts
    wait = INDEX_DAILY_MIN_INTERVAL_SECONDS - (time.monotonic() - _index_daily_last_ts)
    if wait > 0:
        print(f"  ⏳ tushare index_daily 限流间隔(方案A≥61s): 等待{wait:.1f}s")
        time.sleep(wait)
    _index_daily_last_ts = time.monotonic()
    return _pro().index_daily(**kwargs)

# A股指数列表
A_SHARE_INDICES = {
    '000001.SH': '上证指数',
    '399001.SZ': '深证成指',
    '399006.SZ': '创业板指',
    '000300.SH': '沪深300',
    '000905.SH': '中证500',
    '000852.SH': '中证1000',
}

# ============ 方案B东财备源(R049/IA-P0-2-W5-DATASRC-B, 2026-11-04) ============
# 根因(R032 判定件 attempt1_formal_20261104): tushare 同 token index_daily 日配额被
# 外部先在耗尽(判别首调即「5次/天」)→Gate A core 4 项(SHCOMP/SZCI/SH_AMOUNT/
# CN_TOTAL_TURNOVER)结构性缺失。用户实批备源换路;操作者实测: akshare 东财端点
# stock_zh_index_daily_em 免费、无需凭证,完结日 close+amount 可用并与新浪端点交叉
# 一致;旧回落 amount=0 的根因=新浪端点 stock_zh_index_daily 根本没有 amount 列
# (结构性缺陷,非数据源不可用)→旧新浪回落删除,唯一新增通道=东财公开免费端点。
# 纪律: tushare 调用参数/61s 闸门/A_SHARE_INDICES 清单与顺序零变化;零新 token。
# W5-EMWIN(R051, 2026-11-04): 原常量 EM_FALLBACK_MAX_DATE='2026-11-03'(R049 冻结)
# 把 EM 取值行永久钉死 11-03,收盘守卫(要求取值行=运行日)结构性不可满足(R050
# 判定 NV 根因之一,操作者裁定属合同设计缺陷)——经用户方案 B 实批(免费 EM 端点
# 换路,通道后续交易日正常出数=授权固有内容)+操作者裁定动态化: 常量→本函数。
# 阈值 16:10:00 HKT=A股 15:00 收盘后的固定缓冲;前 1 **自然**日(非交易日,周六→周五)。
def _em_max_date(now=None):
    """EM 取值行截止(动态): HKT 已完结交易日——时刻≥16:10:00→当日 ISO,
    否则前 1 自然日 ISO。now 缺省读真实 HKT 钟(UTC+8 无夏令时);仅供测试
    冻结注入。行选择语义(date≤截止,在途行禁用)与 R049 完全一致,仅截止
    随钟动态。"""
    hkt = timezone(timedelta(hours=8))
    if now is None:
        now = datetime.now(hkt)
    elif now.tzinfo is not None:
        now = now.astimezone(hkt)  # aware 输入(任意时区)一律折算 HKT 判定
    cutoff = now.replace(hour=16, minute=10, second=0, microsecond=0)
    return (now.date() if now >= cutoff else now.date() - timedelta(days=1)).isoformat()
EM_MAP = {
    '000001.SH': 'sh000001',
    '399001.SZ': 'sz399001',
    '399006.SZ': 'sz399006',
    '000300.SH': 'sh000300',
    '000905.SH': 'sh000905',
    '000852.SH': 'sh000852',
}


def _em_settled_pairs(df):
    """东财日K完结行选择: [(date_str, 原表行号)] 升序,date≤_em_max_date()
    (在途行禁用)。date 一律字符串化[:10],与端点返回 dtype 无关。"""
    if df is None or len(df) == 0:
        return []
    pairs = sorted(((str(d)[:10], i) for i, d in enumerate(df['date'])),
                   key=lambda p: p[0])
    return [p for p in pairs if p[0] <= _em_max_date()]


def _em_last_settled(df):
    """东财日K取值行: date≤_em_max_date() 的最后一行;无完结行→None。
    返回 (date_str, 行Series)。"""
    settled = _em_settled_pairs(df)
    if not settled:
        return None
    dstr, idx = settled[-1]
    return dstr, df.iloc[idx]


def _fetch_index_em(code, name):
    """F1 指数回落(东财,仅 tushare 异常时经 fetch_a_share_indices 进入):
    返回与 tushare 路径同 schema 的 item + 恰一新增键 via='akshare_em';
    取值行=date≤_em_max_date() 最后一行(在途行禁用);东财失败/无完结行
    →None(该指数如实缺失)。单位披露: EM amount 单位=元(tushare 千元),
    volume 语义=成交量;经 _no_proxy 禁代理直连。"""
    try:
        import akshare as ak
        with _no_proxy():
            df = ak.stock_zh_index_daily_em(symbol=EM_MAP[code])
        settled = _em_settled_pairs(df)
        if not settled:
            print(f"  ⚠️ {name}({code}) 东财回落无完结行(date≤{_em_max_date()})")
            return None
        # 数据批1(#10): 与 tushare 主路同窗语义——series=窗口起点起全序列
        # (EM 端点本就返回全史,按 cn_window_start 过滤);周变化规则不变;
        # YTD 基准=窗内**当年**首个收盘(非窗口首根)。
        win_start = cn_window_start(cn_index_history_period()).replace('-', '')
        win = [p for p in settled if p[0].replace('-', '') >= win_start]
        year = win[-1][0][:4]
        dates = [d for d, _ in win]
        closes = [float(df.iloc[i]['close']) for _, i in win]
        close = closes[-1]
        # 周变化与 tushare 路径同规则(倒数第5收盘;不足5根对比首根)
        week_chg = None
        if len(closes) >= 5:
            prev_close = closes[-5]
            week_chg = round((close - prev_close) / prev_close * 100, 2)
        elif len(closes) >= 2:
            prev_close = closes[0]
            week_chg = round((close - prev_close) / prev_close * 100, 2)
        # YTD 基准=窗内当年首个收盘(纯函数 _ytd_base_close,同 tushare 主路)
        ytd_chg = None
        base = _ytd_base_close(dates, closes, dates[-1].replace('-', ''))
        if base:
            ytd_chg = round((close - base) / base * 100, 2)
        # 东财无 pct_chg 列 → 由前一完结收盘推得(EM同列自洽,非跨源拼接)
        pct_chg = 0.0
        if len(closes) >= 2 and closes[-2] > 0:
            pct_chg = round((close - closes[-2]) / closes[-2] * 100, 2)
        last_d, last_row = _em_last_settled(df)
        return {
            'name': name,
            'close': close,
            'pct_chg': pct_chg,
            'week_chg': week_chg,
            'ytd_chg': ytd_chg,
            'volume': float(last_row.get('volume', 0) or 0),
            'amount': float(last_row.get('amount', 0) or 0),   # 单位: 元
            'date': last_d.replace('-', ''),                    # →YYYYMMDD,同tushare规格
            'series': {'dates': dates, 'values': closes},
            'via': 'akshare_em',
        }
    except Exception as e:
        print(f"  ⚠️ {name}({code}) 东财回落失败: {e}")
        return None

# 港股（主通道腾讯直连，yfinance备用）
HK_INDICES = {
    '^HSI': '恒生指数',
    '^HSCE': '恒生国企',
}

# 腾讯ifzq日K代码（2026-10-17验证：收盘值与yfinance逐分一致）
HK_TX_CODE = {
    '^HSI': 'hkHSI',
    '^HSCE': 'hkHSCEI',
}

# ============ 境内源直连工具（2026-10-17修复） ============
# requests默认trust_env=True会读取macOS系统代理(scutil --proxy → 127.0.0.1:7890),
# launchd 07:00运行时经Clash出境: 出口IP被Yahoo限流(429)、东财push2直接被断连
# (SSLError/ProxyError, 且本机直连东财也不通——该通道已整体不可用)。
# 对策: 境内端点(腾讯/新浪)一律直连——raw HTTP用直连会话, akshare调用临时禁用代理。

def _direct_session():
    """直连会话: trust_env=False同时无视环境变量代理与macOS系统代理"""
    s = requests.Session()
    s.trust_env = False
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
    return s

@contextmanager
def _no_proxy():
    """临时禁用requests代理读取(akshare内部请求无法注入session,只能patch模块级getproxies)。
    只包裹境内akshare调用; 严禁包住yfinance——境外源依赖代理出境。"""
    orig = requests.utils.getproxies
    requests.utils.getproxies = lambda: {}
    try:
        yield
    finally:
        requests.utils.getproxies = orig

# 需要估值数据的指数
# IA-DATA-W3(AC-01c, 2026-11-04): 000001.SH(上证指数)纳入估值名单——注册 SH_PE
# 语义=上证指数整体PE(TTM),原名单仅300/500/1000,上证身份缺席(R008 断点③:
# A_SHARE_INDICES 含 000001.SH 而本名单不含)。与 A_SHARE_INDICES 在上证身份上
# 对齐(既有 300/500/1000 成员与顺序零变化,仅首位新增上证)。
VALUATION_INDICES = {
    '000001.SH': '上证指数',
    '000300.SH': '沪深300',
    '000905.SH': '中证500',
    '000852.SH': '中证1000',
}
# SH_PE 扁平桥接的权威身份(注册口径=上证;300/500/1000 不冒充,身份纪律)
SH_PE_IDENTITY = '000001.SH'

def get_trade_dates():
    """获取日期范围"""
    today = datetime.now()
    end_date = today.strftime('%Y%m%d')
    start_date_week = (today - timedelta(days=10)).strftime('%Y%m%d')
    start_date_year = f'{today.year}0101'
    return end_date, start_date_week, start_date_year

# === 数据批1(#10 CN 股指深窗,2026-11-10): 历史窗口参数化 =====================
# 原硬编码 start_date=当年0101 → 指数 series 恒为年内浅窗(台账#10 缺口:
# CN 股指序列仅 2026-01 起)。镜像 global_market_collector Charter6-P0 同款:
# env CN_INDEX_HISTORY_PERIOD(合法集=env_config.HISTORY_PERIOD_LEGAL),默认
# '10y';'ytd'=旧行为精确保留。61s 限流闸门(_index_daily)零变化——窗口加宽
# 只加大单次响应,不增加调用次数。
_CN_PERIOD_DAYS = {'1d': 1, '5d': 5, '1mo': 31, '3mo': 92, '6mo': 183}
_CN_PERIOD_YEARS = {'1y': 1, '2y': 2, '5y': 5, '10y': 10}
_CN_FLOOR_DATE = '19901219'   # 上证基日(1990-12-19);各指数以源端实际可得为准

# Charter8(HK 深度补拉, 2026-11-10): 港股指数深窗与 A 股同档≈10年。
# 腾讯 ifzq 按 bar 数取数(2600根≈10年);WAF 对大 count 可能 501 拦截→
# 上层转 yfinance 深窗备源(见 _fetch_hk_yfinance)。env 可覆盖,非法回落。
def hk_history_bars():
    """港股指数日K bar 数(纯函数,现读 env HK_INDEX_HISTORY_BARS)。"""
    raw = os.environ.get('HK_INDEX_HISTORY_BARS')
    if raw is None or not str(raw).strip():
        return 2600
    try:
        n = int(str(raw).strip())
    except ValueError:
        print(f"  ⚠️ HK_INDEX_HISTORY_BARS 非整数({raw!r}),回落默认 2600")
        return 2600
    if n < 60:
        print(f"  ⚠️ HK_INDEX_HISTORY_BARS={n} 过小(<60 不足以算周变化),回落 2600")
        return 2600
    return n


def cn_index_history_period():
    """CN 指数历史窗口解析(纯函数,现读 env;空白→默认'10y',非法→告警回落)。"""
    from env_config import HISTORY_PERIOD_LEGAL, resolve_history_period
    period, fallback = resolve_history_period(
        os.environ.get('CN_INDEX_HISTORY_PERIOD'), '10y')
    if fallback:
        print(f"  ⚠️ CN_INDEX_HISTORY_PERIOD 非法(合法集 "
              f"{'/'.join(HISTORY_PERIOD_LEGAL)}),回落默认 10y")
    return period


def cn_window_start(period, today=None):
    """窗口起点 YYYYMMDD(纯函数,离线可测)。

    'ytd'→当年0101(旧行为);'max'→上证基日下限;'Nd/Nmo'→自然日回退;
    'Ny'→年回退(月末日不前移——指数日频无月末语义,年回退取同月日)。"""
    t = today or datetime.now()
    if period == 'ytd':
        return f'{t.year}0101'
    if period == 'max':
        return _CN_FLOOR_DATE
    if period in _CN_PERIOD_DAYS:
        return (t - timedelta(days=_CN_PERIOD_DAYS[period])).strftime('%Y%m%d')
    if period in _CN_PERIOD_YEARS:
        try:
            return t.replace(year=t.year - _CN_PERIOD_YEARS[period]).strftime('%Y%m%d')
        except ValueError:                    # 2/29 润日 → 3/1 同义
            return (t.replace(year=t.year - _CN_PERIOD_YEARS[period],
                              day=28)).strftime('%Y%m%d')
    return f'{t.year}0101'


def _ytd_base_close(trade_dates, closes, last_date_yyyymmdd):
    """YTD 基准收盘(纯函数,数据批1#10 深窗修正)。

    基准=**当年**首个收盘(深窗下序列首根是 N 年前,不得当年初基准);
    当年无行(如 max 窗被源端截断)→退回序列首根并保持非完整YTD语义。
    trade_dates=YYYYMMDD 字符串序列(升序),closes 同长。"""
    year = str(last_date_yyyymmdd)[:4]
    for d, c in zip(trade_dates, closes):
        if str(d).startswith(year):
            return float(c)
    return float(closes[0]) if closes else None


def fetch_a_share_indices():
    """采集A股指数数据"""
    print("\n📈 采集A股指数...")
    end_date, start_week, start_year = get_trade_dates()
    period = cn_index_history_period()
    window_start = cn_window_start(period)
    print(f"  历史窗口: {period}(start={window_start};CN_INDEX_HISTORY_PERIOD 可覆盖)")
    results = {}

    for code, name in A_SHARE_INDICES.items():
        try:
            # 数据批1(#10): 单次拉取 window_start 起全序列(原=年初至今),
            # 附加原始series供事实引擎统一口径计算(周/MTD/YTD=期前收盘基准)
            df_year = _index_daily(ts_code=code, start_date=window_start, end_date=end_date)
            if df_year is None or len(df_year) == 0:
                print(f"  ⚠️ {name}({code}): 无数据")
                continue
            df = df_year.sort_values('trade_date')
            latest = df.iloc[-1]
            close = float(latest['close'])

            # 周变化
            week_chg = None
            if len(df) >= 5:
                prev_close = float(df.iloc[-5]['close'])
                week_chg = round((close - prev_close) / prev_close * 100, 2)
            elif len(df) >= 2:
                prev_close = float(df.iloc[0]['close'])
                week_chg = round((close - prev_close) / prev_close * 100, 2)

            # YTD: 基准=窗口内**当年首个**收盘(纯函数 _ytd_base_close;
            # 深窗下 df.iloc[0] 是 N 年前,不得再当年初基准——数据批1#10 修正)
            ytd_chg = None
            year_start = _ytd_base_close(list(df['trade_date']),
                                         list(df['close']),
                                         str(latest['trade_date']))
            if year_start:
                ytd_chg = round((close - year_start) / year_start * 100, 2)

            dates = [f"{str(d)[:4]}-{str(d)[4:6]}-{str(d)[6:]}" for d in df['trade_date']]
            closes = [float(v) for v in df['close']]
            results[code] = {
                'name': name,
                'close': close,
                'pct_chg': float(latest.get('pct_chg', 0)),
                'week_chg': week_chg,
                'ytd_chg': ytd_chg,
                'volume': float(latest.get('vol', 0)),
                'amount': float(latest.get('amount', 0)),
                'date': str(latest['trade_date']),
                'series': {'dates': dates, 'values': closes},
                'via': 'tushare',
            }
            print(f"  ✅ {name}: {close} (周{week_chg:+.2f}%)" if week_chg else f"  ✅ {name}: {close}")

        except Exception as e:
            print(f"  ❌ {name}({code}): {e}")
            # F1(R049 B-AC-01): tushare 异常→东财回落;上方 tushare 先行路径零变化。
            item = _fetch_index_em(code, name)
            if item is not None:
                results[code] = item
                wc = item.get('week_chg')
                tag = f" (周{wc:+.2f}%)" if wc is not None else ""
                print(f"  ✅ {name}: {item['close']}{tag} [东财回落 akshare_em]")

    return results

def _hk_metrics_from_daily(dates, closes):
    """由日收盘序列计算指标——与yfinance口径一致:
    week_chg对比倒数第5根收盘, ytd对比当年首个交易日收盘。纯函数便于离线测试。"""
    close = round(float(closes[-1]), 2)
    week_chg = None
    if len(closes) >= 5:
        prev = float(closes[-5])
        week_chg = round((close - prev) / prev * 100, 2)
    year = str(datetime.now().year)
    ytd_chg = None
    year_first = next((c for dt, c in zip(dates, closes) if str(dt)[:4] == year), None)
    if year_first:
        ytd_chg = round((close - year_first) / year_first * 100, 2)
    return {'close': close, 'week_chg': week_chg, 'ytd_chg': ytd_chg, 'date': str(dates[-1])[:10]}

def _tx_kline_rows(code, bars=None, retries=2):
    """腾讯ifzq日K直连,返回升序[(date, close), ...];失败返回[]。

    bars: Charter8(HK深度补拉)——默认取 hk_history_bars()(≈10年,与
    A股深窗 CN_INDEX_HISTORY_PERIOD=10y 同档);腾讯 WAF 对大 count 请求
    可能 501 拦截(2026-11-10 实测 >320 被拦),拦→[]→上层转 yfinance 深窗
    备源,不降级凑短窗。"""
    if bars is None:
        bars = hk_history_bars()
    for attempt in range(retries + 1):
        try:
            r = _direct_session().get(
                'https://ifzq.gtimg.cn/appstock/app/fqkline/get',
                params={'param': f'{code},day,,,{bars},qfq'}, timeout=15)
            d = (r.json().get('data') or {}).get(code) or {}
            days = d.get('day') or d.get('qfqday') or []
            rows = [(x[0], float(x[2])) for x in days if len(x) >= 3]
            if rows:
                return rows
        except Exception as e:
            # IA-DATA-W3(AC-01b): 原静默吞异常→留日志(标识+类型),重试语义零变化
            print(f"  ⚠️ 腾讯日K({code})第{attempt + 1}次失败: {type(e).__name__}: {str(e)[:80]}")
            if attempt < retries:
                time.sleep(2)
    return []

def _fetch_hk_tencent(ticker, name):
    """方案1: 腾讯ifzq日K直连(2026-10-17: 恒指/国企连续4日429断供后的可靠主通道)"""
    code = HK_TX_CODE.get(ticker)
    if not code:
        return None
    rows = _tx_kline_rows(code)
    if not rows:
        return None
    m = _hk_metrics_from_daily([d for d, _ in rows], [c for _, c in rows])
    # 第七轮Layer2: 附加原始序列(事实引擎统一口径)
    m['series'] = {'dates': [str(d)[:10] for d, _ in rows],
                   'values': [float(c) for _, c in rows]}
    m['name'] = name
    return m

def _fetch_hk_yfinance(ticker, name, retries=1):
    """方案2: yfinance(走系统代理出境)。429限流时重试1次,仍失败交回调用方。

    Charter8(HK 深度补拉, 2026-11-10): 1mo→10y 深窗(与腾讯主路
    hk_history_bars()≈10年同档;腾讯 WAF 拦大 count 时的兜底路径);
    删 tail(400) 截断与额外 ytd 请求——指标改由 _hk_metrics_from_daily
    从全序列统一计算(与腾讯主路同口径),series 全量直通。"""
    last_err = None
    for attempt in range(retries + 1):
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period='10y')
            if hist.empty:
                return None
            dates = [str(d.date()) for d in hist.index]
            closes = [float(v) for v in hist['Close'].values]
            m = _hk_metrics_from_daily(dates, closes)
            return {'name': name, 'close': m['close'], 'week_chg': m['week_chg'],
                    'ytd_chg': m['ytd_chg'], 'date': m['date'],
                    'series': {'dates': dates,
                               'values': [round(v, 6) for v in closes]}}
        except Exception as e:
            last_err = e
            time.sleep(15)
    if last_err:
        # Charter8: 补异常类型(与腾讯主路"标识+类型"纪律一致,AC-01b)
        print(f"  ⚠️ {name} yfinance失败({type(last_err).__name__}: {str(last_err)[:70]})")
    return None

def fetch_hk_indices():
    """采集港股指数: 腾讯直连(主) → yfinance(备) 双通道"""
    print("\n📈 采集港股指数...")
    results = {}

    for ticker, name in HK_INDICES.items():
        result = _fetch_hk_tencent(ticker, name)
        src = '腾讯直连'
        if result is None:
            print(f"  ⚠️ {name} 腾讯直连失败,转yfinance")
            result = _fetch_hk_yfinance(ticker, name)
            src = 'yfinance'
        if result is None:
            print(f"  ❌ {name}: 双通道均失败")
            continue
        results[ticker] = result
        wc = result.get('week_chg')
        tag = f" (周{wc:+.2f}%)" if wc is not None else ""
        print(f"  ✅ {name}: {result['close']}{tag} [{src}]")

    return results

# ============ R058 SB_FLOW 备源回落登记(IA-P0-SB-FLOW-BACKUP-AC-v1.0) ============
# 现状(R010 登记): tushare moneyflow_hsgt 对本 token 返回「没有接口访问权限」
# (权限类拒,结构性)→ southbound 恒缺(source-persist)。经用户 L0-5 决策二
# (2026-11-05)+预授权③(东财免费公开源),仿 R049 EM 备源模式增设回落路:
# - 接口(登记冻结): akshare v1.18.64 stock_hsgt_hist_em(symbol='南向资金')
#   (datacenter-web.eastmoney.com, RPT_MUTUAL_DEAL_HISTORY, MUTUAL_TYPE=006,
#   免费公开零凭证);淘汰 stock_hsgt_fund_flow_summary_em——仅当日快照,无带
#   日期历史序列,无法做完结行选择与近5日累计。
# - 字段映射(登记冻结): 日期→YYYYMMDD(同 tushare 规格);当日成交净买额
#   (单位=亿港元,2026-11-05 实测锚定: 南向=港股通沪+港股通深 逐分恰等差
#   0.000000)×100→south_money(百万港元,tushare 路径现行口径);近5完结行
#   合计同系数→south_5d_total;north_* 键缺席如实(EM 北向净买披露 2024-08
#   起停止,summary 端点沪股通/深股通成交净买额实测恒0——不伪造)。
# - 回落条件(登记冻结): 主路三态失败(异常含权限拒/df None/len(df)==0)→
#   进入回落,逐次 print 如实记录;取值行=日期≤_em_max_date()(R051 动态
#   截止,复用 _em_settled_pairs,在途行禁用);回落无完结行/取值行NaN/异常
#   →None(=现行 source-persist 语义,如实缺失,禁假值禁重试凑数)。
# - 诚实标签: 主路产物零改动(不添 source 键);回落产物恰一新增键
#   source='akshare_em'(禁冒充 tushare);fact_engine 侧两值制见
#   scripts/fact_engine.py SB_FLOW 区登记。
def _fetch_southbound_em():
    """南向资金备源回落(东财港股通,akshare,免费公开,R058 登记)。
    仅经 fetch_southbound 在主路权限拒/空返回/异常后进入;返回
    {date(YYYYMMDD), south_money(百万港元), source='akshare_em',
     [south_5d_total(百万港元)]};north_* 不产(披露停止,缺席如实);
    无完结行/取值行缺值/异常→None。"""
    try:
        import akshare as ak
        with _no_proxy():
            df = ak.stock_hsgt_hist_em(symbol='南向资金')
        # 完结行选择复用 R049/R051 冻结 helper(列名桥接: 日期→date)
        settled = _em_settled_pairs(df.rename(columns={'日期': 'date'}))
        if not settled:
            print(f"  ⚠️ 东财南向回落无完结行(date≤{_em_max_date()})")
            return None
        last_d, idx = settled[-1]
        # 单位换算(登记冻结): 亿港元×100→百万港元(tushare 现行口径)
        vals = [pd.to_numeric(df.iloc[i]['当日成交净买额'], errors='coerce')
                for _, i in settled]
        net_yi = vals[-1]
        if pd.isna(net_yi):
            print(f"  ⚠️ 东财南向回落取值行({last_d})当日成交净买额缺失")
            return None
        result = {
            'date': last_d.replace('-', ''),                # 同 tushare 规格
            'south_money': round(float(net_yi) * 100.0, 2),
            'source': 'akshare_em',                          # 恰一新增键,禁冒充
        }
        if len(settled) >= 5:   # 近5完结行累计(同 tushare 路径语义,skipna)
            result['south_5d_total'] = round(
                float(sum(v for v in vals[-5:] if not pd.isna(v))) * 100.0, 2)
        print(f"  ✅ 南向资金(akshare-em): {result['south_money']:.2f} 百万 [{last_d}]")
        return result
    except Exception as e:
        print(f"  ⚠️ 东财南向回落失败: {e}")
        return None

def fetch_southbound():
    """采集南向资金: tushare(主) → 东财EM(备,R058)双通道"""
    print("\n💰 采集南向资金...")
    end_date, start_week, _ = get_trade_dates()

    try:
        df = _pro().moneyflow_hsgt(start_date=start_week, end_date=end_date)
        if df is None or len(df) == 0:
            print("  ⚠️ 无南向资金数据")
        else:
            # 确保数值列为数字类型
            for col in ['south_money', 'north_money']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            df = df.sort_values('trade_date')
            latest = df.iloc[-1]

            south = latest.get('south_money', 0)
            north = latest.get('north_money', 0)

            result = {
                'date': str(latest['trade_date']),
                'south_money': round(float(south), 2) if pd.notna(south) else 0,
                'north_money': round(float(north), 2) if pd.notna(north) else 0,
            }

            # 计算近5日累计
            if len(df) >= 5:
                recent = df.tail(5)
                result['south_5d_total'] = round(float(recent['south_money'].sum(skipna=True)), 2)
                result['north_5d_total'] = round(float(recent['north_money'].sum(skipna=True)), 2)

            print(f"  ✅ 南向资金: {result['south_money']:.2f} 百万")
            print(f"  ✅ 北向资金: {result['north_money']:.2f} 百万")
            return result

    except Exception as e:
        print(f"  ❌ 南向资金: {e}")

    # R058 备源回落(登记见上方): 主路权限拒/空返回/异常→东财EM,逐次如实记录
    print("  ↪️ 南向主路失败/空,转东财EM回落(akshare)")
    return _fetch_southbound_em()

def _fetch_margin_em():
    """G-P1-11 融资融券备源(IA-P1-WP-E, 2026-11-06): tushare 主路不可用→东财
    akshare 两所 margin(上交所 stock_margin_sse+深交所 stock_margin_szse)
    **同一信用交易日期**配对合计(两所同日合计口径,与主路 margin(trade_date)
    汇总同构);产出键与主路 1:1(date/rzye/rqye/rzye_billion/balance,元口径)
    +via='akshare_em' 恰一新增键(诚实源标签,禁冒充 tushare);单所数据缺席/
    配对窗内无共同日→None(如实缺席不填0,不以单所半合计冒充两所口径)。
    SSE 完结行按 _em_max_date() 截止择新,至多 3 候选日逐一配对(深交所单日
    查询,调用有界)。"""
    import akshare as ak
    try:
        with _no_proxy():
            end = datetime.now().strftime('%Y%m%d')
            start = (datetime.now() - timedelta(days=14)).strftime('%Y%m%d')
            sse = ak.stock_margin_sse(start_date=start, end_date=end)
    except Exception as e:
        print(f"  ❌ 融资融券备源上交所(stock_margin_sse): {type(e).__name__}: {str(e)[:120]}")
        return None
    if sse is None or len(sse) == 0 or '信用交易日期' not in getattr(sse, 'columns', []):
        print("  ⚠️ 融资融券备源: 上交所无数据/列漂移")
        return None
    cand = sorted({str(d)[:10].replace('-', '') for d in sse['信用交易日期']
                   if str(d)[:10].replace('-', '') <= _em_max_date().replace('-', '')},
                  reverse=True)[:3]
    for ymd in cand:
        try:
            with _no_proxy():
                szse = ak.stock_margin_szse(date=ymd)
            if szse is None or len(szse) == 0:
                continue
            sse_rows = sse[sse['信用交易日期'].astype(str).str.replace('-', '')
                          .str[:8] == ymd]
            if len(sse_rows) == 0:
                continue
            sse_row = sse_rows.iloc[-1]
            rzye = float(sse_row['融资余额']) + float(szse['融资余额'].sum())
            rqye = float(sse_row['融券余量金额']) + float(szse['融券余额'].sum())
            result = {
                'date': ymd,
                'rzye': round(rzye, 2),
                'rqye': round(rqye, 2),
                'rzye_billion': round(rzye / 1e8, 2),
                'balance': round((rzye + rqye) / 1e8, 2),
                'via': 'akshare_em',
            }
            print(f"  ✅ 融资融券备源(东财两所同日合计): balance={result['balance']} 亿元 ({ymd})")
            return result
        except Exception as e:
            print(f"  ❌ 融资融券备源深交所@{ymd}: {type(e).__name__}: {str(e)[:120]}")
            continue
    print("  ⚠️ 融资融券备源: 无两所同日配对(数据不足,如实缺席)")
    return None


def fetch_margin():
    """采集融资融券数据"""
    print("\n💳 采集融资融券...")

    # 尝试最近几天（可能有延迟）
    for days_back in range(0, 5):
        try:
            date = (datetime.now() - timedelta(days=days_back)).strftime('%Y%m%d')
            df = _pro().margin(trade_date=date)
            if df is not None and len(df) > 0:
                # 汇总所有交易所
                total_rzye = df['rzye'].sum()  # 融资余额
                total_rqye = df['rqye'].sum()  # 融券余额

                result = {
                    'date': date,
                    'rzye': round(float(total_rzye), 2),       # 融资余额（元）
                    'rqye': round(float(total_rqye), 2),       # 融券余额（元）
                    'rzye_billion': round(float(total_rzye) / 1e8, 2),  # 亿元
                    # IA-DATA-W3(AC-01a, 2026-11-04): 引擎/快照契约键 margin.balance
                    # (fact_engine L364-366 读 mg.get('balance');snapshot_builder 锚
                    # 'china.margin.balance')。口径=两融余额合计(融资rzye+融券rqye)
                    # ÷1e8→亿元,与注册 unit=cny_100m「融资融券余额存量(亿元)」同口径;
                    # 公式授权=IA-DATA-W3-AC-v1.0 §一(a)冻结合同(操作者代批,取代
                    # R008 §1.4-2a「须合同确认」的前置)。rzye/rqye/rzye_billion 原样保留。
                    'balance': round((float(total_rzye) + float(total_rqye)) / 1e8, 2),
                }
                print(f"  ✅ 融资余额: {result['rzye_billion']:.2f} 亿元 ({date})")
                return result
        except Exception as e:
            # IA-DATA-W3(AC-01b): 原裸 except:continue 吞异常(R008 U-1 根因)→
            # 具体异常类型+指标标识+日期留日志,失败可归因;重试语义零变化。
            print(f"  ❌ 融资融券(margin)@{date}: {type(e).__name__}: {str(e)[:120]}")
            continue

    # IA-P1-WP-E(G-P1-11, 2026-11-06): margin 备源切换——tushare 主路全失败→
    # 东财 akshare 两所备源(_fetch_margin_em);备源亦不可用→None(当日该节
    # 键缺席,不填0,§三(c) L81 纪律)。
    print("  ↪️ 融资融券主路不可用,转东财 akshare 备源")
    return _fetch_margin_em()

def _pe_value(row):
    """PE 取值双形态兼容(IA-DATA-W3 AC-01c): 扁平 pe 键(旧产物/部分载荷形态)
    或嵌套 pe_ttm 键(tushare index_dailybasic 实测形态)择一取值;均缺席/不可
    数值化→None(如实缺失,不造 0)。"""
    for k in ('pe', 'pe_ttm'):
        v = row.get(k)
        if v is not None:
            try:
                return round(float(v), 2)
            except (TypeError, ValueError) as e:
                print(f"  ⚠️ 估值PE取值失败(键={k}): {type(e).__name__}: {str(e)[:60]}")
                return None
    return None


def _fetch_valuation_em():
    """G-P1-11 估值备源(IA-P1-WP-E, 2026-11-06): tushare 估值主路无上证 PE
    可取→乐咕 akshare stock_market_pe_lg('上证')「平均市盈率」完结行(date≤
    _em_max_date(),在途行禁用)。范围仅限 SH_PE 扁平桥接 pe/date 两键(+via/
    note 口径披露),嵌套 per-index 对象不越域补造(身份纪律: 300/500/1000
    不冒充);无完结行/值不可数值化→None(如实缺席不填0)。
    口径披露: 乐咕=上证主板平均市盈率,注册 SH_PE=上证整体 PE(TTM) 近似
    代理,口径差异经 note 键如实标注,禁静默混同。"""
    import akshare as ak
    try:
        with _no_proxy():
            df = ak.stock_market_pe_lg(symbol='上证')
        # 完结行选择(乐咕列=「日期」,与东财 date 列名不同→就地选择,不改共享
        # 助手 _em_settled_pairs 的既有契约): date≤_em_max_date(),在途行禁用
        if df is None or len(df) == 0 or '日期' not in getattr(df, 'columns', []):
            print("  ⚠️ 估值备源: 乐咕无数据/列漂移")
            return None
        settled = sorted(((str(d)[:10], i) for i, d in enumerate(df['日期'])),
                         key=lambda p: p[0])
        settled = [p for p in settled if p[0] <= _em_max_date()]
        if not settled:
            print(f"  ⚠️ 估值备源: 乐咕无完结行(date≤{_em_max_date()})")
            return None
        d, idx = settled[-1]
        try:
            pe = round(float(df.iloc[idx]['平均市盈率']), 2)
        except (TypeError, ValueError):
            print(f"  ⚠️ 估值备源: 乐咕平均市盈率不可数值化: {df.iloc[idx]['平均市盈率']!r}")
            return None
        return {
            'pe': pe,
            'date': d.replace('-', ''),
            'via': 'akshare_legu',
            'note': '乐咕上证主板平均市盈率(近似口径;注册 SH_PE=上证整体PE(TTM),口径差异如实披露)',
        }
    except Exception as e:
        print(f"  ❌ 估值备源(stock_market_pe_lg): {type(e).__name__}: {str(e)[:120]}")
        return None


def fetch_valuation():
    """采集指数估值（PE/PB）"""
    print("\n📊 采集指数估值...")
    end_date, start_week, _ = get_trade_dates()
    results = {}
    sh_flat = {}   # SH_PE 扁平桥接键(pe/date),上证成功且 PE 可取时填充

    for code, name in VALUATION_INDICES.items():
        try:
            df = _pro().index_dailybasic(ts_code=code, start_date=start_week, end_date=end_date)
            if df is None or len(df) == 0:
                print(f"  ⚠️ {name}: 无估值数据")
                continue

            df = df.sort_values('trade_date')
            latest = df.iloc[-1]

            results[code] = {
                'name': name,
                'date': str(latest['trade_date']),
                'pe_ttm': round(float(latest.get('pe_ttm', 0)), 2),
                'pb': round(float(latest.get('pb', 0)), 2),
                'turnover_rate': round(float(latest.get('turnover_rate', 0)), 2),
                'total_mv': round(float(latest.get('total_mv', 0)), 2),
            }
            # IA-DATA-W3(AC-01c): 扁平桥接——引擎/快照契约键 valuation.pe+date
            # (fact_engine L367-369 只读扁平 pe;snapshot_builder 锚
            # 'china.valuation.pe')。身份纪律: 一律取上证(SH_PE_IDENTITY,
            # 注册 SH_PE=上证整体PE TTM),pe 取值经 _pe_value 兼容扁平 pe/嵌套
            # pe_ttm 两形态;上证失败或 PE 不可取→不写扁平键(如实缺失,不以
            # 300/500/1000 冒充)。嵌套 per-index 对象原样保留(两形态并存)。
            if code == SH_PE_IDENTITY:
                pe = _pe_value(latest)
                if pe is not None:
                    sh_flat = {'pe': pe, 'date': str(latest['trade_date'])}
            print(f"  ✅ {name}: PE={results[code]['pe_ttm']}, PB={results[code]['pb']}")

        except Exception as e:
            print(f"  ❌ {name}({code})估值: {type(e).__name__}: {str(e)[:120]}")

    if sh_flat:
        results.update(sh_flat)
        print(f"  ✅ 上证PE(扁平桥接 valuation.pe): {sh_flat['pe']} ({sh_flat['date']})")
    else:
        # IA-P1-WP-E(G-P1-11, 2026-11-06): SH_PE 扁平桥接键备源——主路无上证
        # PE 可取→乐咕备源(_fetch_valuation_em);备源亦不可用→扁平键缺席
        # (当日该键缺席,不填0,不以 300/500/1000 冒充上证身份)。
        print("  ↪️ 主路无上证PE,转乐咕 akshare 备源")
        em = _fetch_valuation_em()
        if em is not None:
            results.update(em)
            print(f"  ✅ 上证PE(备源扁平桥接 valuation.pe): {em['pe']} ({em['date']})")

    return results

def fetch_turnover():
    """采集沪深两市成交额"""
    print("\n📊 采集A股成交额...")

    # 方案1: Tushare指数日线 — amount字段单位千元
    try:
        today = datetime.now().strftime('%Y%m%d')
        # 查最近5个交易日
        df = _index_daily(ts_code='000001.SH', start_date=(datetime.now() - timedelta(days=10)).strftime('%Y%m%d'), end_date=today)
        if df is not None and len(df) > 0:
            latest = df.sort_values('trade_date').iloc[-1]
            sh_amount = float(latest.get('amount', 0))  # 千元
            sh_date = str(latest['trade_date'])

            # 同时获取深证成指成交额
            df2 = _index_daily(ts_code='399001.SZ', start_date=(datetime.now() - timedelta(days=10)).strftime('%Y%m%d'), end_date=today)
            sz_amount = 0
            if df2 is not None and len(df2) > 0:
                latest2 = df2.sort_values('trade_date').iloc[-1]
                sz_amount = float(latest2.get('amount', 0))

            total_billion = round((sh_amount + sz_amount) / 1e5, 2)  # 千元→亿元: ÷1e5
            sh_billion = round(sh_amount / 1e5, 2)
            sz_billion = round(sz_amount / 1e5, 2)

            result = {
                'date': sh_date,
                # 2026-10-17口径修正: 深侧来自399001.SZ深证成指(成分口径),
                # 非深市全市场(全市场须399106.SZ) — scope如实标注,不得写"沪深两市"
                'scope': '沪市全市场+深证成指成分(近似沪深两市)',
                'sh_amount_billion': sh_billion,
                'sz_amount_billion': sz_billion,
                'total_amount_billion': total_billion,
                'volume_billion': total_billion,  # 兼容旧字段名
                'label': f'成交额(近似两市): {total_billion:.0f}亿 (沪{sh_billion:.0f}全市场+深{sz_billion:.0f}成指成分)',
            }
            print(f"  ✅ 沪深两市成交额: {total_billion:.2f} 亿 (沪{sh_billion:.0f}+深{sz_billion:.0f})")
            return result
    except Exception as e:
        print(f"  ⚠️ Tushare成交额失败: {e}")

    # 方案2: 东财EM双取(R049 B-AC-02)——旧新浪回落(ak.stock_zh_index_daily)已删除:
    # 该端点根本没有 amount 列,回落 amount 恒=0(结构性缺陷,非数据源不可用)。
    # 本方案双取 sh000001+sz399001(禁代理直连),取值行 date≤_em_max_date()
    # (在途行禁用),amount 单位=元 → ÷1e8 round2 得亿元;source 标记=akshare_em
    # (禁冒充 tushare);口径与方案1一致(沪市全市场+深证成指成分)。
    try:
        import akshare as ak
        with _no_proxy():
            df_sh = ak.stock_zh_index_daily_em(symbol='sh000001')
            df_sz = ak.stock_zh_index_daily_em(symbol='sz399001')
        sh_row = _em_last_settled(df_sh)
        sz_row = _em_last_settled(df_sz)
        if sh_row is None or sz_row is None:
            print(f"  ⚠️ 东财成交额回落无完结行(date≤{_em_max_date()})")
            return None
        sh_date, sh_last = sh_row
        sz_date, sz_last = sz_row
        sh_amount = float(sh_last['amount'])  # 元
        sz_amount = float(sz_last['amount'])  # 元
        sh_billion = round(sh_amount / 1e8, 2)
        sz_billion = round(sz_amount / 1e8, 2)
        total_billion = round(sh_billion + sz_billion, 2)

        result = {
            'date': sh_date.replace('-', ''),  # 同方案1规格(YYYYMMDD)
            # 口径与方案1一致(深侧=399001成指成分,非深市全市场)
            'scope': '沪市全市场+深证成指成分(近似沪深两市)',
            'sh_amount_billion': sh_billion,
            'sz_amount_billion': sz_billion,
            'total_amount_billion': total_billion,
            'volume_billion': total_billion,  # 兼容旧字段名
            'source': 'akshare_em',
            'label': f'成交额(近似两市): {total_billion:.0f}亿 (沪{sh_billion:.0f}全市场+深{sz_billion:.0f}成指成分)',
        }
        print(f"  ✅ 成交额(akshare-em): sh≈{sh_billion:.2f} sz≈{sz_billion:.2f} total≈{total_billion:.2f} 亿")
        return result
    except Exception as e:
        print(f"  ⚠️ 东财成交额回落失败: {e}")

    return None

def _parse_sina_rt_line(line):
    """解析hq.sinajs.cn的rt_hkXXX行 → {close, prev_close, date}或None。
    格式: var hq_str_rt_hkHSI="HSI,恒生指数,开,昨收,高,低,现价,涨跌,涨跌%,...,日期,时间,...";
    字段序在HSI/HSAHP间存在52周高低位差,故日期用正则提取而非固定下标。"""
    try:
        if '"' not in line:
            return None
        p = line.split('"')[1].split(',')
        close, prev = float(p[6]), float(p[3])
        m = re.search(r'(\d{4})/(\d{2})/(\d{2})', line)
        if close <= 0 or not m:
            return None
        return {'close': close, 'prev_close': prev,
                'date': f"{m.group(1)}-{m.group(2)}-{m.group(3)}"}
    except Exception as e:
        # IA-DATA-W3(AC-01b): 原静默return None→留日志(标识+类型),解析契约零变化
        print(f"  ⚠️ 新浪rt行解析失败(rt_hk): {type(e).__name__}: {str(e)[:60]}")
        return None

def _ah_signal(close):
    """AH溢价分层信号(阈值与原逻辑一致)"""
    if close > 140:
        return '港股极度便宜'
    if close > 130:
        return '港股偏便宜'
    if close > 120:
        return '溢价正常'
    return '溢价收敛，港股不再便宜'

def _ah_result(close, date, via):
    signal = _ah_signal(close)
    print(f"  ✅ AH溢价指数(HSAHP): {close:.2f} ({signal}) [{via}]")
    return {
        'index_name': '恒生AH股溢价指数(HSAHP)',
        'date': date,
        'close': round(close, 2),
        'signal': signal,
        'interpretation': f'AH溢价 {close:.1f}，>100表示A股相对H股有溢价',
    }

def fetch_ah_premium():
    """采集恒生AH股溢价指数(HSAHP): 新浪rt直连(主) → 新浪日K(备) → 东财(末选保留)
    2026-10-17修复: 东财push2当前网络不可达; 原新浪spot方案列表里根本没有AH溢价行(从未生效)"""
    print("\n📊 采集AH溢价指数...")

    # 方案1: 新浪rt_hkHSAHP直连(需Referer,GBK编码)
    try:
        r = _direct_session().get('https://hq.sinajs.cn/list=rt_hkHSAHP',
                                  headers={'Referer': 'https://finance.sina.com.cn'},
                                  timeout=10)
        r.encoding = 'gbk'
        parsed = _parse_sina_rt_line(r.text)
        if parsed and 100 < parsed['close'] < 200:
            return _ah_result(parsed['close'], parsed['date'], '新浪直连')
        if parsed:
            print(f"  ⚠️ 新浪HSAHP值异常: {parsed['close']}，尝试备用方案")
    except Exception as e:
        print(f"  ⚠️ 新浪直连失败: {str(e)[:80]}")

    # 方案2: akshare新浪日K(禁代理直连)
    try:
        import akshare as ak
        with _no_proxy():
            df = ak.stock_hk_index_daily_sina(symbol="HSAHP")
        if df is not None and len(df) > 0:
            latest = df.iloc[-1]
            close = float(latest['close'])
            date = pd.to_datetime(latest['date']).strftime('%Y-%m-%d')
            if 100 < close < 200:
                return _ah_result(close, date, '新浪日K')
            print(f"  ⚠️ 新浪日KHSAHP值异常: {close}，尝试备用方案")
    except Exception as e:
        print(f"  ⚠️ 新浪日K失败: {str(e)[:80]}")

    # 方案3: 东财akshare(禁代理;当前网络不可达,保留给东财可达的部署环境)
    try:
        import akshare as ak
        with _no_proxy():
            df = ak.stock_hk_index_daily_em(symbol="HSAHP")
        if df is not None and len(df) > 0:
            latest = df.iloc[-1]
            close = float(latest['latest']) if 'latest' in df.columns else float(latest['close'])
            if 100 < close < 200:
                return _ah_result(close, str(latest['date'])[:10], '东财')
            print(f"  ⚠️ 东财HSAHP值异常: {close}")
    except Exception as e:
        print(f"  ⚠️ 东财方式失败: {str(e)[:80]}")

    print("  ❌ AH溢价指数采集失败")
    return None

# ============ IA-P1-WP-E G-P1-14..18 CN 宏观采集(2026-11-06) ============
# 免费公开源经 akshare(DESIGN §三(b) L73 预授权③直用面);境内端点一律
# _no_proxy() 直连(2026-10-17 修复纪律);逐端点独立 try/except 容错——单端点
# 失败仅该键缺席(§三(c) L81 降级→MISSING 披露,不填0)。月频指标观测日=
# 统计期(月),未发布≠缺失(§三(c) L82,registry freshness 60 天窗)。端点列
# 锚与口径=REPORT §零.6A 终值表(akshare 1.18.47 安装包源码离线实读)。
# 产出键与 registry 新增 8 条目 1:1: lpr_1y/lpr_5y/cpi_yoy/ppi_yoy/pmi_mfg/
# sf_flow/new_loans/omo_7d;各值 {'date','value','source'} 诚实源标签。

def _norm_month(s):
    """中文月份列归一: '2026年10月'→'2026-10';不可解析→None(如实弃行)。"""
    m = re.search(r'(\d{4})\s*年\s*(\d{1,2})', str(s))
    return '%s-%02d' % (m.group(1), int(m.group(2))) if m else None


def _tushare_monthly_last(df, col):
    """tushare 月度宏观行选(R6-D1 纯函数,零网络可注入): month='YYYYMM' 行中
    取 col 有值的最大月→('YYYY-MM-DD' 月末观测日, float)。语义同 _macro_last:
    NaN/不可数值化/月份不可归一跳行,返回序向不依赖;无有值行→None。"""
    if df is None or len(df) == 0:
        return None
    import calendar
    best = None
    for _, row in df.iterrows():
        m = re.fullmatch(r'(\d{4})(\d{2})', str(row.get('month') or '').strip())
        if not m or not 1 <= int(m.group(2)) <= 12:
            continue
        v = row.get(col)
        if v is None:
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if fv != fv:                      # NaN→如实跳行
            continue
        ym = (m.group(1), m.group(2))
        if best is None or ym > (best[0], best[1]):
            best = (m.group(1), m.group(2), fv)
    if best is None:
        return None
    y, mo = int(best[0]), int(best[1])
    return ('%04d-%02d-%02d' % (y, mo, calendar.monthrange(y, mo)[1]), best[2])


# ============ tushare 月度宏观跨进程响应缓存(R10, 2026-11-12) ============
# 实证(RESUME 2②/P2 台账"R10 候选"): tushare cn_cpi/cn_ppi 同 api 1 次/分
# 限流(与 index_daily 同族,FIX3 §六附则)。午夜窗自采与流水线=两个独立进程,
# 同分钟各拉一次→第二次必限流拒→cpi_yoy/ppi_yoy 假性缺席→Gate A 误拒
# (生产 07:00 单跑不受影响)。_index_daily 闸门(方案A)是进程内单调钟,护不
# 到跨进程——故加文件级响应缓存: 成功且可解析的响应按 api 落 data/cache/,
# TTL 内(默认600s;月度数据发布周期≥28天,窗口保守)复用免二次直连。
# 纪律: 缓存只做同窗去重,不做陈旧回退——直连失败仍如实缺席(禁0填充不变);
# 缓存读/写任何失败=透明跳过,绝不影响采集主路。
TUSHARE_MONTHLY_CACHE_TTL_SECONDS = 600
TUSHARE_MONTHLY_CACHE_DIR = os.path.join(DATA_DIR, 'cache')


def _monthly_cache_path(api_name):
    """缓存档路径(R10): data/cache/tushare_monthly_{api}.json。api 名白名单
    校验(现役仅 cn_cpi/cn_ppi 两面)防路径注入;目录经模块常量注入=测试密闭。"""
    if api_name not in ('cn_cpi', 'cn_ppi'):
        raise ValueError('unknown monthly api: %r' % (api_name,))
    return os.path.join(TUSHARE_MONTHLY_CACHE_DIR,
                        'tushare_monthly_%s.json' % api_name)


def _cache_load_rows(path, now_ts, ttl=TUSHARE_MONTHLY_CACHE_TTL_SECONDS):
    """读月度响应缓存(纯文件面,零网络): {'fetched_at','rows'} 且 0≤age≤ttl
    →rows(list[dict]);其余(缺档/坏JSON/rows 非list或空/fetched_at 坏值/
    超龄/钟偏未来)→None。零异常外泄。"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            obj = json.load(f)
        rows = obj.get('rows')
        fetched_at = obj.get('fetched_at')
        if (isinstance(rows, list) and rows
                and isinstance(fetched_at, (int, float))
                and 0 <= now_ts - float(fetched_at) <= ttl):
            return rows
    except Exception:
        pass
    return None


def _cache_save_rows(path, df, now_ts):
    """写月度响应缓存(尽力而为): DataFrame→records(NaN→None,JSON 严格可序列
    化)+fetched_at,先写 .tmp.{pid} 再 os.replace 原子换名(两进程并发写=后写
    者胜,两者皆合法)。任何失败→False,不外泄不影响主路。"""
    try:
        rows = df.astype(object).where(df.notna(), None).to_dict('records')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = '%s.tmp.%d' % (path, os.getpid())
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump({'fetched_at': now_ts, 'rows': rows}, f,
                      ensure_ascii=False)
        os.replace(tmp, path)
        return True
    except Exception:
        return False


MOFCOM_SHRZGM_URL = 'https://data.mofcom.gov.cn/datamofcom/front/gnmy/shrzgmQuery'


def _shrzgm_rows():
    """社融增量源端直取(R9,2026-11-12;商务部 mofcom POST;curl 子进程)。

    为何不经 akshare.macro_china_shrzgm(): 本机 python ssl 栈=LibreSSL 2.8.3,
    与 mofcom TLS 协商即断(SSLError 'No cipher can be selected'/握手 EOF,
    2026-11-12 实测;curl 走 LibreSSL 3.3.6 可通)——同一端点经系统 curl 取
    (零第三方依赖,curl=系统工具;境内源 --noproxy 直连与 _no_proxy 同理)。
    失败(非 0/空响应/非 JSON 数组)→None,调用方如实缺席。"""
    import subprocess
    try:
        r = subprocess.run(['curl', '-s', '--noproxy', '*', '-X', 'POST',
                            MOFCOM_SHRZGM_URL, '--max-time', '25'],
                           capture_output=True, timeout=35)
        if r.returncode != 0 or not r.stdout:
            return None
        rows = json.loads(r.stdout.decode('utf-8'))
        return rows if isinstance(rows, list) else None
    except Exception:
        return None


def _shrzgm_last(rows):
    """mofcom 社融行选(R9 纯函数,零网络可注入): rows(list[dict])中取
    tiosfs(社会融资规模增量,亿元;键序↔akshare 1.18.47 macro_china_shrzgm
    列序:date/ndbab/entrustloan/forcloan/rmblaon/bibae/tiosfs/sfinfe/
    trustloan)有值的最大 date('YYYYMM')→('YYYY-MM', float)。语义同
    _macro_last_month: NaN/不可数值化/月份不可归一跳行,序向不依赖;
    无有值行→None。"""
    if not rows:
        return None
    best = None
    for row in rows:
        m = re.fullmatch(r'(\d{4})(\d{2})', str(row.get('date') or '').strip())
        if not m or not 1 <= int(m.group(2)) <= 12:
            continue
        v = row.get('tiosfs')
        if v is None:
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if fv != fv:
            continue
        ym = m.group(1) + '-' + m.group(2)
        if best is None or ym > best[0]:
            best = (ym, fv)
    return best


def _norm_date(s):
    """宏观日期列归一(序向/格式不依赖): 'YYYY-MM-DD'/'YYYY/M/D'/'2026年10月
    10日'→'YYYY-MM-DD';月粒度('2026年10月'/'2026-10')→'YYYY-MM'(观测日=
    统计期,月频语义);不可解析→None。"""
    s = str(s).strip()
    m = re.search(r'(\d{4})\s*[-/年]\s*(\d{1,2})(?:\s*[-/月]\s*(\d{1,2})\s*日?)?', s)
    if not m:
        return None
    y, mo, d = m.group(1), int(m.group(2)), m.group(3)
    return '%s-%02d-%02d' % (y, mo, int(d)) if d else '%s-%02d' % (y, mo)


def _macro_last(df, date_col, value_col):
    """宏观序列最新有值观测(全行扫描取最大归一日期,端点返回序向不依赖;
    值不可数值化/NaN/日期不可归一→跳行;全无有值行→None)。"""
    if df is None or len(df) == 0:
        return None
    best = None
    for _, row in df.iterrows():
        d = _norm_date(row.get(date_col))
        v = row.get(value_col)
        if d is None or v is None:
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if fv != fv:                      # NaN(金十端点未发布行形态)→如实跳行
            continue
        if best is None or d > best[0]:
            best = (d, fv)
    return best


def _macro_last_month(df, month_col, value_col):
    """月度宏观序列最新有值观测(月份列 '2026年10月' 形态→'YYYY-MM' 归一;
    语义同 _macro_last: NaN/不可数值化跳行,序向不依赖)。"""
    if df is None or len(df) == 0:
        return None
    best = None
    for _, row in df.iterrows():
        d = _norm_month(row.get(month_col))
        v = row.get(value_col)
        if d is None or v is None:
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if fv != fv:
            continue
        if best is None or d > best[0]:
            best = (d, fv)
    return best


def _parse_omo_rows(lines, today=None):
    """央行公开市场业务交易公告行纯解析(G-P1-18;可注入零网络): 行序列中
    过滤 7 天期逆回购操作行→[(日期, 利率)] 升序去重。行形锚(公告短语形态,
    测试合成 fixture 同构): '2026年11月5日 …7天期逆回购操作…中标利率1.80'。
    today='YYYY-MM-DD' 给出→仅取观测行≤今日(测试冻结钟);无'7天'/'逆回购'
    词对/利率不可解→该行跳过(如实缺席);无有效行→[]。"""
    rows = {}
    for line in lines:
        s = str(line)
        if ('7天' not in s) or ('逆回购' not in s):
            continue
        d = _norm_date(s)
        m = re.search(r'中标利率[^0-9]{0,6}([0-9]+(?:\.[0-9]+)?)', s)
        if d is None or m is None:
            continue
        if today is not None and d > today:
            continue
        rows[d] = float(m.group(1))
    return [(d, rows[d]) for d in sorted(rows)]


def _omo_rows_default():
    """G-P1-18 源默认装载器: 免费公开现成接口缺席(akshare 1.18.47 源码 grep
    逆回购零命中[实取·离线])→PENDING 披露返回 None(禁造数禁网络;接线留
    后续轮,操作者排程面)。"""
    print("  ⏳ CN_OMO_7D 源未接线(PENDING): 公告装载待后续轮接线,本节如实缺席")
    return None


def fetch_omo_7d(rows=None, today=None):
    """G-P1-18 采集点: rows=公告行序列注入(纯解析面);rows=None→默认装载器
    (_omo_rows_default)。返回 {'date','value','source':'pboc_omo'} 或 None。"""
    if rows is None:
        rows = _omo_rows_default()
        if rows is None:
            return None
    parsed = _parse_omo_rows(rows, today=today)
    if not parsed:
        return None
    d, v = parsed[-1]
    return {'date': d, 'value': round(v, 2), 'source': 'pboc_omo'}


def fetch_macro():
    """采集 CN 宏观序列(G-P1-14..17+G-P1-18 装配点;IA-P1-WP-E): 返回 dict,
    产出键与 registry 新增 8 条目 1:1(lpr_1y/lpr_5y/cpi_yoy/ppi_yoy/pmi_mfg/
    sf_flow/new_loans/omo_7d);逐端点容错,单端点失败→该键缺席(禁 0 填充)。"""
    print("\n🏦 采集 CN 宏观序列...")
    import akshare as ak
    out = {}

    # G-P1-14 LPR(东财;TRADE_DATE/LPR1Y/LPR5Y 列锚)
    try:
        with _no_proxy():
            df = ak.macro_china_lpr()
        for key, col in (('lpr_1y', 'LPR1Y'), ('lpr_5y', 'LPR5Y')):
            got = _macro_last(df, 'TRADE_DATE', col)
            if got is not None:
                out[key] = {'date': got[0], 'value': round(got[1], 2),
                            'source': 'akshare_em'}
                print(f"  ✅ {key}: {out[key]['value']} ({out[key]['date']})")
            else:
                print(f"  ⚠️ {key}: 无有值行(macro_china_lpr.{col})")
    except Exception as e:
        print(f"  ❌ LPR(macro_china_lpr): {type(e).__name__}: {str(e)[:120]}")

    # G-P1-15 CPI/PPI 同比(R6-D1 换源: 金十 macro_china_cpi/ppi_yearly 停更于
    # 2025-08[R5 盘点;akshare 1.18.47 金十族实测 cpi 尾 2008-02/ppi 尾 2006-01/
    # cpi_monthly 尾 2025-09 皆死]→tushare pro cn_cpi.nt_yoy/cn_ppi.ppi_yoy
    # (现有 token/现有依赖;月度→月末观测日;失败=如实缺席,不回退停更源)。
    # R10 跨进程缓存: TTL 内复用成功响应免同分钟双耗限流(见缓存节注释);
    # 仅缓存"可解析"响应(got 非 None),列漂移/空表不入缓存。
    for key, api_name, col in (('cpi_yoy', 'cn_cpi', 'nt_yoy'),
                               ('ppi_yoy', 'cn_ppi', 'ppi_yoy')):
        try:
            cache_path = _monthly_cache_path(api_name)
            cached = _cache_load_rows(cache_path, time.time())
            if cached is not None:
                df = pd.DataFrame(cached, columns=['month', col])
                got = _tushare_monthly_last(df, col)
                if got is not None:
                    print(f"  ♻️ {key}: tushare 月度缓存命中"
                          f"(age≤{TUSHARE_MONTHLY_CACHE_TTL_SECONDS}s,免同分钟限流直连)")
            else:
                with _no_proxy():
                    df = getattr(_pro(), api_name)(
                        start_date='20200101', end_date=datetime.now().strftime('%Y%m%d'))
                got = _tushare_monthly_last(df, col)
                if got is not None:
                    _cache_save_rows(cache_path, df, time.time())
            if got is not None:
                out[key] = {'date': got[0], 'value': round(got[1], 2),
                            'source': 'tushare_pro'}
                print(f"  ✅ {key}: {out[key]['value']} ({out[key]['date']})")
            else:
                print(f"  ⚠️ {key}: 无有值行({api_name}.{col})")
        except Exception as e:
            print(f"  ❌ {key}({api_name}): {type(e).__name__}: {str(e)[:120]}")

    # G-P1-16 制造业 PMI(东财;月份/制造业-指数 列锚,中文月份归一)
    try:
        with _no_proxy():
            df = ak.macro_china_pmi()
        got = _macro_last_month(df, '月份', '制造业-指数')
        if got is not None:
            out['pmi_mfg'] = {'date': got[0], 'value': round(got[1], 2),
                              'source': 'akshare_em'}
            print(f"  ✅ pmi_mfg: {out['pmi_mfg']['value']} ({out['pmi_mfg']['date']})")
        else:
            print("  ⚠️ pmi_mfg: 无有值行(macro_china_pmi.制造业-指数)")
    except Exception as e:
        print(f"  ❌ PMI(macro_china_pmi): {type(e).__name__}: {str(e)[:120]}")

    # G-P1-17 社融增量(商务部 mofcom 直取 R9;date='YYYYMM'/tiosfs 列锚)
    try:
        got = _shrzgm_last(_shrzgm_rows())
        if got is not None:
            out['sf_flow'] = {'date': got[0], 'value': round(got[1], 2),
                              'source': 'mofcom_direct'}
            print(f"  ✅ sf_flow: {out['sf_flow']['value']} ({out['sf_flow']['date']})")
        else:
            print("  ⚠️ sf_flow: 无有值行(mofcom.shrzgmQuery.tiosfs)")
    except Exception as e:
        print(f"  ❌ 社融(mofcom.shrzgmQuery): {type(e).__name__}: {str(e)[:120]}")

    # G-P1-17 新增人民币贷款(东财;月份/当月 列锚)
    try:
        with _no_proxy():
            df = ak.macro_china_new_financial_credit()
        got = _macro_last_month(df, '月份', '当月')
        if got is not None:
            out['new_loans'] = {'date': got[0], 'value': round(got[1], 2),
                                'source': 'akshare_em'}
            print(f"  ✅ new_loans: {out['new_loans']['value']} ({out['new_loans']['date']})")
        else:
            print("  ⚠️ new_loans: 无有值行(macro_china_new_financial_credit.当月)")
    except Exception as e:
        print(f"  ❌ 新增贷款(macro_china_new_financial_credit): {type(e).__name__}: {str(e)[:120]}")

    # G-P1-18 7天逆回购(无现成接口→身份预注册;公告行纯解析可注入)
    try:
        got = fetch_omo_7d()
        if got is not None:
            out['omo_7d'] = got
            print(f"  ✅ omo_7d: {got['value']} ({got['date']})")
    except Exception as e:
        print(f"  ❌ omo_7d: {type(e).__name__}: {str(e)[:120]}")

    return out

def save_data(all_data):
    """保存数据"""
    date_str = datetime.now().strftime('%Y%m%d')
    daily_dir = os.path.join(DATA_DIR, 'daily')
    os.makedirs(daily_dir, exist_ok=True)

    filepath = os.path.join(daily_dir, f'china_{date_str}.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    size = os.path.getsize(filepath)
    print(f"\n💾 数据已保存: {filepath} ({size} 字节)")
    return filepath

# ============ 主程序 ============
if __name__ == '__main__':
    print("=" * 60)
    print("📊 A股/港股数据采集 v2.1")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("数据源: Tushare + 腾讯/新浪直连 + yfinance(备) + akshare")
    print("=" * 60)

    all_data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'version': '2.1',
    }

    # 1. A股指数
    all_data['a_share_indices'] = fetch_a_share_indices()

    # 2. 港股指数
    all_data['hk_indices'] = fetch_hk_indices()

    # 3. 南向资金
    all_data['southbound'] = fetch_southbound()

    # 4. 融资融券（新增）
    all_data['margin'] = fetch_margin()

    # 5. 指数估值（新增）
    all_data['valuation'] = fetch_valuation()

    # 6. 成交额
    all_data['turnover'] = fetch_turnover()

    # 7. AH溢价（新增）
    all_data['ah_premium'] = fetch_ah_premium()

    # 8. CN宏观序列(IA-P1-WP-E G-P1-14..18 新增)
    all_data['macro'] = fetch_macro()

    # 保存
    save_data(all_data)

    # 汇总
    print("\n" + "=" * 60)
    print("📋 采集汇总")
    print("=" * 60)
    a_count = len(all_data.get('a_share_indices', {}))
    hk_count = len(all_data.get('hk_indices', {}))
    print(f"  A股指数: {a_count} 个")
    print(f"  港股指数: {hk_count} 个")
    print(f"  南向资金: {'✅' if all_data.get('southbound') else '❌'}")
    print(f"  融资融券: {'✅' if all_data.get('margin') else '❌'}")
    print(f"  指数估值: {'✅' if all_data.get('valuation') else '❌'}")
    print(f"  成交额:   {'✅' if all_data.get('turnover') else '❌'}")
    print(f"  AH溢价:   {'✅' if all_data.get('ah_premium') else '❌'}")
    print(f"  CN宏观:   {len(all_data.get('macro') or {})} 项")
    print("\n🎉 采集完成！")
