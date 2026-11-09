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
from datetime import datetime, timedelta, time, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from env_config import (DATA_DIR, HISTORY_PERIOD_LEGAL,
                        resolve_history_period)

# === Charter6-P0(A2 §4-P0, 2026-11-09): 历史窗口参数化 ======================
# 原硬编码1年窗口(fetch_all默认值+__main__调用点)——默认改10年供长序列
# 研究(六维状态向量/expanding z-score 需要完整历史);环境变量
# GLOBAL_HISTORY_PERIOD 可覆盖(yfinance period语法: 1y/2y/5y/10y/max/...,
# 空白回落默认)。复权口径不变: history() 显式 auto_adjust=True(除权除息
# 调整收盘,唯一口径,不允许yfinance默认值漂移)。全量重拉幂等,不做增量
# 合并(A2 §3);旧档清理见 scripts/data_retention.py(90天全量+月度归档)。
# Charter6 收尾(A2 延期③, 2026-11-10): 非法值经 env_config.
# resolve_history_period 校验回落默认并告警,不再直通 yfinance。
DEFAULT_HISTORY_PERIOD = '10y'


def global_history_period():
    """历史窗口解析(纯函数,每次调用现读环境变量,便于测试与运行期覆盖)。

    空白→默认'10y';非法值(不在 env_config.HISTORY_PERIOD_LEGAL)→告警
    回落默认(延期③: 不直通 yfinance;告警打在本模块,env_config 零 print)。"""
    period, fallback = resolve_history_period(
        os.environ.get('GLOBAL_HISTORY_PERIOD'), DEFAULT_HISTORY_PERIOD)
    if fallback:
        print(f"  ⚠️ GLOBAL_HISTORY_PERIOD 非法(合法集 "
              f"{'/'.join(HISTORY_PERIOD_LEGAL)}),"
              f"回落默认 {DEFAULT_HISTORY_PERIOD}")
    return period

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

# ══ BTC日收盘UTC完整日语义(IA-P0-2-W5-FIX2-AC-v1.0 F2-AC-01,2026-11-01) ══
# 背景(R003归因,dev/p0-2-w5-attr@2215f0e): 每日07:00(UTC+8)=前一日23:00 UTC
# 定时采集时,yfinance BTC-USD日K最后一根是**当日在途UTC日K**,其Close为23:00
# 时点市价(截断价),曾被记作该UTC日的日收盘——实测2026-10-30 07:00:17(UTC+8)
# 即2026-10-29 23:00:17Z取到78822.59被记为2026-10-29收盘,与Coinbase完整
# UTC日收77780.33差1.34%(该日最后一小时真实跌幅)。
# 修复语义: BTC日收盘仅引用**取数时刻(UTC)前已完整结束的UTC日K**;日K时间戳D
# (UTC,实测索引tz=UTC)代表区间[D 00:00:00Z, D+1 00:00:00Z),仅当
# retrieved_at_utc ≥ D+1 00:00:00Z该日已完结;在途日K的任何价格(Close/High/
# Low)不得被写入/标注为任何UTC日的日收盘——在途bar整体剔除,close/high/low/
# date/series及全部派生指标均以完结日K为基础。仅BTC适用(注册表calendar=
# crypto仅BTC);其他资产采集口径不变。
BTC_ASSET_ID = "BTC"
BTC_CLOSE_SOURCE = "yfinance:BTC-USD(daily,UTC日K)"


def btc_completed_utc_days_only(hist, retrieved_at=None):
    """剔除BTC日K中取数时刻(UTC)尚未完结的UTC日bar(F2-AC-01)。

    参数: hist=yfinance BTC-USD日线DataFrame(索引tz-aware,实测UTC;naive
    按UTC解释); retrieved_at=取数时刻datetime(缺省=当前UTC时刻;naive按UTC
    解释——供测试注入确定性时点,如R003场景2026-10-29T23:00:17Z)。
    返回: (filtered_hist, close_meta)。close_meta随采集产物持久化:
      source=来源标识; retrieved_at_utc=取数时刻(UTC ISO);
      semantics='completed_utc_daily_close_only'; bar_utc_window=日K区间语义;
      completed_through_utc=保留的最后已完结UTC日(ISO);
      dropped_incomplete_utc_days=被剔除在途日(ISO列表)。
    未来时间戳bar(数据源异常)同样剔除——不采信未来数据为已完结日。"""
    now = retrieved_at if retrieved_at is not None else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    idx = hist.index
    idx_utc = idx.tz_convert('UTC') if idx.tz is not None else idx.tz_localize('UTC')
    keep, dropped = [], []
    for i, ts in enumerate(idx_utc):
        day_end = datetime.combine(ts.date() + timedelta(days=1), time.min,
                                   tzinfo=timezone.utc)
        if day_end <= now:
            keep.append(i)
        else:
            dropped.append(ts.date().isoformat())
    filtered = hist.iloc[keep]
    meta = {
        'source': BTC_CLOSE_SOURCE,
        'retrieved_at_utc': now.astimezone(timezone.utc).isoformat(timespec='seconds'),
        'semantics': 'completed_utc_daily_close_only',
        'bar_utc_window': '[D 00:00:00Z, D+1 00:00:00Z)',
        'completed_through_utc': idx_utc[keep[-1]].date().isoformat() if keep else None,
        'dropped_incomplete_utc_days': dropped,
    }
    return filtered, meta

def fetch_all(period=None):
    """批量获取所有资产的历史收盘价，返回一个字典：{资产ID: DataFrame}

    period 缺省时取 global_history_period()(Charter6-P0: env
    GLOBAL_HISTORY_PERIOD,默认'10y');显式传参优先(测试/单次窗口用)。"""
    if period is None:
        period = global_history_period()
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

    # 第七轮Layer2(2026-10-17): 附加原始收盘序列 — 事实引擎统一计算
    # 周变化/MTD/YTD(期前收盘基准+交易日历口径),替代本函数的固定偏移口径。
    # 旧字段保留以兼容既有消费者,但快照以下游事实引擎输出为准。
    tail = close.tail(400)
    series = {"dates": [str(d.date()) for d in tail.index],
              "values": [round(float(v), 6) for v in tail.values]}

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
        "series": series,
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
    print(f"历史窗口: {global_history_period()}(GLOBAL_HISTORY_PERIOD 可覆盖)")

    all_data, failed = fetch_all()

    print("\n计算指标...")
    results = {}
    btc_close_meta = None
    for asset_id, hist in all_data.items():
        if asset_id == BTC_ASSET_ID:
            # W5-FIX2 F2-AC-01: BTC日收盘仅引用已完结UTC日K——在途日K整体剔除,
            # 其任何价格不进入close/high/low/date/series;元数据随产物持久化
            hist, btc_close_meta = btc_completed_utc_days_only(hist)
            if btc_close_meta['dropped_incomplete_utc_days']:
                print(f"  ⛔ BTC剔除在途UTC日K: "
                      f"{','.join(btc_close_meta['dropped_incomplete_utc_days'])}"
                      f"(取数{btc_close_meta['retrieved_at_utc']},仅保留已完结日≤"
                      f"{btc_close_meta['completed_through_utc']})")
        m = calc_metrics(asset_id, hist)
        if m:
            results[asset_id] = m
    if btc_close_meta is not None and BTC_ASSET_ID in results:
        results[BTC_ASSET_ID]['close_meta'] = btc_close_meta

    print(f"计算完成: {len(results)} 个资产")

    save_results(results)

    print("=" * 50)
    print("✅ 全球行情采集模块完成")
