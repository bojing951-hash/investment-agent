"""
全球行情数据采集模块
数据源：yfinance
"""

import os
import socket

# --- 代理修复(2026-09-30) ---
# 根因: launchd环境的NO_PROXY=*会禁用所有代理,导致yfinance直连Yahoo被429限流(国内IP)。
# 修复: 若本机代理(127.0.0.1:7890)在线,则强制走代理;否则回退直连。
def _setup_proxy():
    proxy = os.environ.get("YF_PROXY", "http://127.0.0.1:7890")
    host, _, port = proxy.rpartition(":")
    host = host.replace("http://", "").replace("https://", "")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((host, int(port)))
        online = True
    except Exception:
        online = False
    if online:
        # NO_PROXY=*会让requests忽略HTTP(S)_PROXY,必须先清除
        for var in ("NO_PROXY", "no_proxy"):
            os.environ.pop(var, None)
        os.environ["HTTP_PROXY"] = proxy
        os.environ["HTTPS_PROXY"] = proxy
        print(f"🌐 代理在线,走 {proxy}")
    else:
        for var in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "NO_PROXY", "no_proxy"):
            os.environ.pop(var, None)
        print("⚠️ 本地代理不在线,尝试直连(Yahoo可能429限流)")

_setup_proxy()

import yfinance as yf
import pandas as pd
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from env_config import DATA_DIR

# 资产监控列表：key=资产ID, value=yfinance的ticker代码
WATCHLIST = {
    # 美股指数
    "SPX": "^GSPC",
    "NDX": "^NDX",
    "RUT": "^RUT",
    # 美股个股
    "NVDA": "NVDA",
    "AAPL": "AAPL",
    "MSFT": "MSFT",
    # 利率
    "TLT": "TLT",
    "HYG": "HYG",
    # 汇率
    "DXY": "DX-Y.NYB",
    "EURUSD": "EURUSD=X",
    # 商品
    "GOLD": "GC=F",
    "SILVER": "SI=F",
    "WTI": "CL=F",
    "BRENT": "BZ=F",
    # 国际
    "EEM": "EEM",
    # 加密
    "BTC": "BTC-USD",
    # 波动率
    "VIX": "^VIX",
    # --- 欧洲 ---
    "EZU": "EZU",
    "FEZ": "FEZ",
    "EWU": "EWU",
    "EWG": "EWG",
    # --- 亚太 ---
    "EWJ": "EWJ",
    "INDA": "INDA",
    "FXI": "FXI",
    # --- 外汇补充 ---
    "GBPUSD=X": "GBPUSD=X",
    "JPY=X": "JPY=X",
    "CNY=X": "CNY=X",
    # --- 债券补充 ---
    "IEF": "IEF",
    "SHY": "SHY",
    "LQD": "LQD",
    # --- 商品补充 ---
    "GLD": "GLD",
    "USO": "USO",
}

def fetch_all(period="1y"):
    """批量获取所有资产的历史收盘价，返回一个字典：{资产ID: DataFrame}"""
    all_data = {}
    failed = []

    for asset_id, ticker_symbol in WATCHLIST.items():
        hist = None
        # 每个资产最多尝试2次(Yahoo偶发429/超时)
        for attempt in (1, 2):
            try:
                ticker = yf.Ticker(ticker_symbol)
                hist = ticker.history(period=period, auto_adjust=True)
                if not hist.empty:
                    break
                print(f"  ⚠️ {asset_id}: 空数据 (第{attempt}次)")
            except Exception as e:
                print(f"  ❌ {asset_id} (第{attempt}次): {str(e)[:80]}")
                hist = None
            if attempt == 1:
                import time
                time.sleep(5)
        if hist is not None and not hist.empty:
            all_data[asset_id] = hist
            latest = hist['Close'].iloc[-1]
            print(f"  ✅ {asset_id}: {latest:.2f}")
        else:
            failed.append(asset_id)

    print(f"\n采集完成: {len(all_data)}/{len(WATCHLIST)} 成功")
    if failed:
        print(f"失败: {', '.join(failed)}")

    return all_data, failed

def calc_metrics(asset_id, hist):
    """计算单个资产的周变化、MTD、YTD、均线信号"""
    close = hist['Close']
    if len(close) < 2:
        return None

    today = close.iloc[-1]
    today_date = close.index[-1]

    # 周变化（5个交易日前）
    if len(close) > 5:
        week_ago = close.iloc[-6]
        week_chg = (today / week_ago - 1) * 100
    else:
        week_chg = 0.0

    # MTD（本月第一个交易日）
    month_start = close[close.index.month == today_date.month]
    if len(month_start) > 1:
        mtd_chg = (today / month_start.iloc[0] - 1) * 100
    else:
        mtd_chg = 0.0

    # YTD（本年第一个交易日）
    year_start = close[close.index.year == today_date.year]
    if len(year_start) > 1:
        ytd_chg = (today / year_start.iloc[0] - 1) * 100
    else:
        ytd_chg = 0.0

    # 50日和200日均线
    ma50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else None
    ma200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else None

    vs_50d = "🟢" if (ma50 and today > ma50) else ("🔴" if ma50 else "—")
    vs_200d = "🟢" if (ma200 and today > ma200) else ("🔴" if ma200 else "—")

    # 当日盘中高/低(第四轮P0-6): touch预测盘中触及判定需要,收盘价不能证明盘中未触及
    high = round(float(hist['High'].iloc[-1]), 2) if 'High' in hist else None
    low = round(float(hist['Low'].iloc[-1]), 2) if 'Low' in hist else None

    return {
        "asset_id": asset_id,
        "close": round(float(today), 2),
        "high": high,
        "low": low,
        "week_chg": round(float(week_chg), 2),
        "mtd_chg": round(float(mtd_chg), 2),
        "ytd_chg": round(float(ytd_chg), 2),
        "vs_50d": vs_50d,
        "vs_200d": vs_200d,
        "date": str(today_date.date()),
    }

def save_results(results):
    """将采集结果保存为JSON和Markdown两种格式"""
    today_str = datetime.now().strftime('%Y%m%d')

    # 保存JSON
    json_path = os.path.join(DATA_DIR, "daily", f"global_{today_str}.json")
    output = {
        "date": today_str,
        "time": datetime.now().strftime('%H:%M:%S'),
        "count": len(results),
        "data": results,
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # 保存Markdown表格
    md_path = os.path.join(DATA_DIR, "daily", f"global_{today_str}.md")
    lines = [
        f"# 全球资产数据 {today_str}",
        "",
        f"| 资产 | 收盘 | 周变化 | MTD | YTD | 50D | 200D |",
        f"|------|------|--------|-----|-----|-----|------|",
    ]
    for aid, m in results.items():
        lines.append(
            f"| {aid} | {m['close']} | {m['week_chg']:+.2f}% | "
            f"{m['mtd_chg']:+.2f}% | {m['ytd_chg']:+.2f}% | "
            f"{m['vs_50d']} | {m['vs_200d']} |"
        )
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"JSON已保存: {json_path}")
    print(f"MD已保存: {md_path}")

if __name__ == "__main__":
    print(f"全球行情采集 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    all_data, failed = fetch_all(period="1y")

    print("\n计算指标...")
    results = {}
    for asset_id, hist in all_data.items():
        m = calc_metrics(asset_id, hist)
        if m:
            results[asset_id] = m

    print(f"计算完成: {len(results)} 个资产")

    save_results(results)

    print("=" * 50)
    print("✅ 全球行情采集模块完成")
