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
        # 与 tushare 路径同窗语义: df_year=当年序列(start_date=年初)→ 周变化/YTD/
        # pct/series 全部取**取值行当年**窗口(跨年历史不入计算,与 tushare item 同构)
        year = settled[-1][0][:4]
        yr = [p for p in settled if p[0][:4] == year]
        dates = [d for d, _ in yr]
        closes = [float(df.iloc[i]['close']) for _, i in yr]
        close = closes[-1]
        # 周变化与 tushare 路径同规则(倒数第5收盘;不足5根对比首根)
        week_chg = None
        if len(closes) >= 5:
            prev_close = closes[-5]
            week_chg = round((close - prev_close) / prev_close * 100, 2)
        elif len(closes) >= 2:
            prev_close = closes[0]
            week_chg = round((close - prev_close) / prev_close * 100, 2)
        # YTD 基准=当年首个收盘(同 tushare df_year 首行)
        ytd_chg = None
        if closes and closes[0]:
            ytd_chg = round((close - closes[0]) / closes[0] * 100, 2)
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

def fetch_a_share_indices():
    """采集A股指数数据"""
    print("\n📈 采集A股指数...")
    end_date, start_week, start_year = get_trade_dates()
    results = {}

    for code, name in A_SHARE_INDICES.items():
        try:
            # 第七轮: 单次拉取年初至今全序列(原为近10天+年初两次调用),
            # 附加原始series供事实引擎统一口径计算(周/MTD/YTD=期前收盘基准)
            df_year = _index_daily(ts_code=code, start_date=start_year, end_date=end_date)
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

            # YTD：获取年初数据
            ytd_chg = None
            year_start = float(df.iloc[0]['close'])
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

def _tx_kline_rows(code, bars=320, retries=2):
    """腾讯ifzq日K直连,返回升序[(date, close), ...];失败返回[]。
    320根约15个月,足够覆盖周变化与YTD计算。"""
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
    """方案2: yfinance(走系统代理出境)。429限流时重试1次,仍失败交回调用方。"""
    last_err = None
    for attempt in range(retries + 1):
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period='1mo')
            if hist.empty:
                return None
            close = round(float(hist['Close'].iloc[-1]), 2)
            week_chg = None
            if len(hist) >= 5:
                prev = float(hist['Close'].iloc[-5])
                week_chg = round((close - prev) / prev * 100, 2)
            ytd_chg = None
            try:
                hist_ytd = data.history(period='ytd')
                if len(hist_ytd) > 0:
                    year_start = float(hist_ytd['Close'].iloc[0])
                    ytd_chg = round((close - year_start) / year_start * 100, 2)
            except Exception as e:
                # IA-DATA-W3(AC-01b): 原静默pass→留日志;ytd_chg=None 语义零变化
                print(f"  ⚠️ {name} yfinance YTD获取失败: {type(e).__name__}: {str(e)[:60]}")
            tail = hist['Close'].tail(400)
            return {'name': name, 'close': close, 'week_chg': week_chg,
                    'ytd_chg': ytd_chg, 'date': str(hist.index[-1].date()),
                    'series': {'dates': [str(d.date()) for d in tail.index],
                               'values': [round(float(v), 6) for v in tail.values]}}
        except Exception as e:
            last_err = e
            time.sleep(15)
    if last_err:
        print(f"  ⚠️ {name} yfinance失败({str(last_err)[:80]})")
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

def fetch_southbound():
    """采集南向资金"""
    print("\n💰 采集南向资金...")
    end_date, start_week, _ = get_trade_dates()

    try:
        df = _pro().moneyflow_hsgt(start_date=start_week, end_date=end_date)
        if df is None or len(df) == 0:
            print("  ⚠️ 无南向资金数据")
            return None

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

    print("  ⚠️ 融资融券数据暂不可用")
    return None

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
    print("\n🎉 采集完成！")
