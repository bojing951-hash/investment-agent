"""
A股/港股数据采集模块 v2.0
数据源：Tushare（A股主力）+ yfinance（港股）+ akshare（成交额）
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta

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

# 港股（用 yfinance）
HK_INDICES = {
    '^HSI': '恒生指数',
    '^HSCE': '恒生国企',
}

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
            # 获取近10天日线（算周变化）
            df = pro.index_daily(ts_code=code, start_date=start_week, end_date=end_date)
            if df is None or len(df) == 0:
                print(f"  ⚠️ {name}({code}): 无数据")
                continue

            df = df.sort_values('trade_date')
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
            try:
                df_year = pro.index_daily(ts_code=code, start_date=start_year, end_date=end_date)
                if df_year is not None and len(df_year) > 0:
                    df_year = df_year.sort_values('trade_date')
                    year_start = float(df_year.iloc[0]['close'])
                    ytd_chg = round((close - year_start) / year_start * 100, 2)
            except:
                pass

            results[code] = {
                'name': name,
                'close': close,
                'pct_chg': float(latest.get('pct_chg', 0)),
                'week_chg': week_chg,
                'ytd_chg': ytd_chg,
                'volume': float(latest.get('vol', 0)),
                'amount': float(latest.get('amount', 0)),
                'date': str(latest['trade_date']),
            }
            print(f"  ✅ {name}: {close} (周{week_chg:+.2f}%)" if week_chg else f"  ✅ {name}: {close}")

        except Exception as e:
            print(f"  ❌ {name}({code}): {e}")

    return results

def fetch_hk_indices():
    """采集港股指数（yfinance）"""
    print("\n📈 采集港股指数...")
    results = {}

    for ticker, name in HK_INDICES.items():
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period='1mo')
            if hist.empty:
                print(f"  ⚠️ {name}: 无数据")
                continue

            close = round(float(hist['Close'].iloc[-1]), 2)

            # 周变化
            week_chg = None
            if len(hist) >= 5:
                prev = float(hist['Close'].iloc[-5])
                week_chg = round((close - prev) / prev * 100, 2)

            # YTD
            ytd_chg = None
            try:
                hist_ytd = data.history(period='ytd')
                if len(hist_ytd) > 0:
                    year_start = float(hist_ytd['Close'].iloc[0])
                    ytd_chg = round((close - year_start) / year_start * 100, 2)
            except:
                pass

            results[ticker] = {
                'name': name,
                'close': close,
                'week_chg': week_chg,
                'ytd_chg': ytd_chg,
                'date': str(hist.index[-1].date()),
            }
            print(f"  ✅ {name}: {close} (周{week_chg:+.2f}%)" if week_chg else f"  ✅ {name}: {close}")

        except Exception as e:
            print(f"  ❌ {name}: {e}")

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

    # 方案2: akshare (注意: volume是股数不是金额)
    try:
        import akshare as ak
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

def fetch_ah_premium():
    """采集恒生AH股溢价指数（HSAHP）"""
    print("\n📊 采集AH溢价指数...")

    # 方案1: 东方财富港股指数历史数据
    try:
        import akshare as ak
        df = ak.stock_hk_index_daily_em(symbol="HSAHP")
        if df is not None and len(df) > 0:
            latest = df.iloc[-1]
            close = float(latest['latest']) if 'latest' in df.columns else float(latest['close'])
            date_val = str(latest['date'])

            if close > 100 and close < 200:  # 合理性校验
                signal = '港股极度便宜' if close > 140 else '港股偏便宜' if close > 130 else '溢价正常' if close > 120 else '溢价收敛，港股不再便宜'
                result = {
                    'index_name': '恒生AH股溢价指数(HSAHP)',
                    'date': date_val,
                    'close': round(close, 2),
                    'signal': signal,
                    'interpretation': f'AH溢价 {close:.1f}，>100表示A股相对H股有溢价'
                }
                print(f"  ✅ AH溢价指数(HSAHP): {close:.2f} ({signal})")
                return result
            else:
                print(f"  ⚠️ 东财HSAHP值异常: {close}，尝试备用方案")
    except Exception as e:
        print(f"  ⚠️ 东财方式失败: {e}")

    # 方案2: 新浪港股指数实时数据
    try:
        import akshare as ak
        df = ak.stock_hk_index_spot_sina()
        if df is not None and len(df) > 0:
            # 查找包含"AH"和"溢价"的行
            ah_rows = df[df['名称'].str.contains('AH|溢价', na=False)]
            if len(ah_rows) > 0:
                row = ah_rows.iloc[0]
                close = float(row['最新价'])
                if close > 100 and close < 200:
                    signal = '港股极度便宜' if close > 140 else '港股偏便宜' if close > 130 else '溢价正常' if close > 120 else '溢价收敛'
                    result = {
                        'index_name': f"{row['名称']}",
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'close': round(close, 2),
                        'signal': signal,
                        'interpretation': f'AH溢价 {close:.1f}，>100表示A股相对H股有溢价'
                    }
                    print(f"  ✅ AH溢价指数(新浪): {close:.2f} ({signal})")
                    return result
    except Exception as e:
        print(f"  ⚠️ 新浪方式失败: {e}")

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
    print("📊 A股/港股数据采集 v2.0")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("数据源: Tushare + yfinance + akshare")
    print("=" * 60)

    all_data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'version': '2.0',
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
