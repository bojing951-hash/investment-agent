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
from datetime import datetime, timedelta
from contextlib import contextmanager

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from env_config import TUSHARE_TOKEN

import tushare as ts
import yfinance as yf

# ============ 配置 ============
PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(PROJECT_DIR, 'data')

pro = ts.pro_api(TUSHARE_TOKEN)

# A股指数列表
A_SHARE_INDICES = {
    '000001.SH': '上证指数',
    '399001.SZ': '深证成指',
    '399006.SZ': '创业板指',
    '000300.SH': '沪深300',
    '000905.SH': '中证500',
    '000852.SH': '中证1000',
}

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
VALUATION_INDICES = {
    '000300.SH': '沪深300',
    '000905.SH': '中证500',
    '000852.SH': '中证1000',
}

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
            df_year = pro.index_daily(ts_code=code, start_date=start_year, end_date=end_date)
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
            }
            print(f"  ✅ {name}: {close} (周{week_chg:+.2f}%)" if week_chg else f"  ✅ {name}: {close}")

        except Exception as e:
            print(f"  ❌ {name}({code}): {e}")

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
        except Exception:
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
            except Exception:
                pass
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
        df = pro.moneyflow_hsgt(start_date=start_week, end_date=end_date)
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
            df = pro.margin(trade_date=date)
            if df is not None and len(df) > 0:
                # 汇总所有交易所
                total_rzye = df['rzye'].sum()  # 融资余额
                total_rqye = df['rqye'].sum()  # 融券余额

                result = {
                    'date': date,
                    'rzye': round(float(total_rzye), 2),       # 融资余额（元）
                    'rqye': round(float(total_rqye), 2),       # 融券余额（元）
                    'rzye_billion': round(float(total_rzye) / 1e8, 2),  # 亿元
                }
                print(f"  ✅ 融资余额: {result['rzye_billion']:.2f} 亿元 ({date})")
                return result
        except:
            continue

    print("  ⚠️ 融资融券数据暂不可用")
    return None

def fetch_valuation():
    """采集指数估值（PE/PB）"""
    print("\n📊 采集指数估值...")
    end_date, start_week, _ = get_trade_dates()
    results = {}

    for code, name in VALUATION_INDICES.items():
        try:
            df = pro.index_dailybasic(ts_code=code, start_date=start_week, end_date=end_date)
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
            print(f"  ✅ {name}: PE={results[code]['pe_ttm']}, PB={results[code]['pb']}")

        except Exception as e:
            print(f"  ❌ {name}: {e}")

    return results

def fetch_turnover():
    """采集沪深两市成交额"""
    print("\n📊 采集A股成交额...")

    # 方案1: Tushare指数日线 — amount字段单位千元
    try:
        pro = ts.pro_api(TUSHARE_TOKEN)
        today = datetime.now().strftime('%Y%m%d')
        # 查最近5个交易日
        df = pro.index_daily(ts_code='000001.SH', start_date=(datetime.now() - timedelta(days=10)).strftime('%Y%m%d'), end_date=today)
        if df is not None and len(df) > 0:
            latest = df.sort_values('trade_date').iloc[-1]
            sh_amount = float(latest.get('amount', 0))  # 千元
            sh_date = str(latest['trade_date'])

            # 同时获取深证成指成交额
            df2 = pro.index_daily(ts_code='399001.SZ', start_date=(datetime.now() - timedelta(days=10)).strftime('%Y%m%d'), end_date=today)
            sz_amount = 0
            if df2 is not None and len(df2) > 0:
                latest2 = df2.sort_values('trade_date').iloc[-1]
                sz_amount = float(latest2.get('amount', 0))

            total_billion = round((sh_amount + sz_amount) / 1e4, 2)  # 千元→亿元 (÷1000再×10=÷1e4... 不对)
            # 千元 → 亿元: ÷ 1e5
            sh_billion = round(sh_amount / 1e5, 2)
            sz_billion = round(sz_amount / 1e5, 2)
            total_billion = round((sh_amount + sz_amount) / 1e5, 2)

            result = {
                'date': sh_date,
                'scope': '沪深两市',
                'sh_amount_billion': sh_billion,
                'sz_amount_billion': sz_billion,
                'total_amount_billion': total_billion,
                'volume_billion': total_billion,  # 兼容旧字段名
                'label': f'沪深两市成交额: {total_billion:.0f}亿 (沪{sh_billion:.0f}+深{sz_billion:.0f})',
            }
            print(f"  ✅ 沪深两市成交额: {total_billion:.2f} 亿 (沪{sh_billion:.0f}+深{sz_billion:.0f})")
            return result
    except Exception as e:
        print(f"  ⚠️ Tushare成交额失败: {e}")

    # 方案2: akshare (注意: volume是股数不是金额; 境内源禁代理直连)
    try:
        import akshare as ak
        with _no_proxy():
            df = ak.stock_zh_index_daily(symbol='sh000001')
        if df is not None and len(df) > 0:
            latest = df.iloc[-1]
            # akshare的amount字段才是成交额，volume是成交量(股数)
            amount = float(latest.get('amount', 0))
            if amount > 0:
                # amount单位是元
                amount_billion = round(amount / 1e8, 2)
            else:
                # 如果amount为0，说明数据源有问题，跳过
                print(f"  ⚠️ akshare amount为0，跳过")
                return None

            result = {
                'date': str(latest.name.date()) if hasattr(latest.name, 'date') else str(latest.name),
                'volume_billion': amount_billion,
                'total_amount_billion': amount_billion,
            }
            print(f"  ✅ 上证成交额(akshare): {amount_billion:.2f} 亿")
            return result
    except Exception as e:
        print(f"  ⚠️ akshare成交额: {e}")

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
    except Exception:
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
