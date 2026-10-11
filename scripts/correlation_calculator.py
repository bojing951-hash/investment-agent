"""
跨资产相关性计算模块
计算关键资产对的20日滚动相关系数，用于验证：
- 全球联动程度（相关性上升 = 系统性风险）
- 传统关系是否失效（股债、股金）
- 地缘冲击的扩散程度
"""

import os
import sys
import json
import socket
import pandas as pd
from datetime import datetime, timedelta

# --- 代理修复(2026-10-11,与global_market_collector同款) ---
# launchd环境NO_PROXY=*会禁用所有代理,yfinance直连Yahoo会被429限流(国内IP)。
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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(PROJECT_DIR, 'data')

# ============ 需要计算相关性的资产对 ============
CORRELATION_PAIRS = [
    # 股债关系（正相关 = 同涨同跌 = 滞胀/危机信号）
    {'name': '美股-美债', 'a': '^GSPC', 'b': 'TLT', 'a_label': 'SPX', 'b_label': 'TLT',
     'interpretation': '正相关=股债同跌（滞胀/危机），负相关=正常避险'},

    # 股金关系
    {'name': '美股-黄金', 'a': '^GSPC', 'b': 'GC=F', 'a_label': 'SPX', 'b_label': 'GOLD',
     'interpretation': '负相关=黄金避险有效，正相关=流动性主导'},

    # 美元-风险资产
    {'name': '美元-美股', 'a': 'DX-Y.NYB', 'b': '^GSPC', 'a_label': 'DXY', 'b_label': 'SPX',
     'interpretation': '负相关=美元避险/Sell America，正相关=同涨（罕见）'},

    # 美元-黄金
    {'name': '美元-黄金', 'a': 'DX-Y.NYB', 'b': 'GC=F', 'a_label': 'DXY', 'b_label': 'GOLD',
     'interpretation': '负相关=正常，正相关=传统关系失效'},

    # 油价-利率
    {'name': '油价-10Y国债', 'a': 'CL=F', 'b': 'TLT', 'a_label': 'WTI', 'b_label': 'TLT',
     'interpretation': '负相关=油涨债跌（通胀传导），正相关=衰退交易'},

    # 油价-新兴市场
    {'name': '油价-新兴市场', 'a': 'CL=F', 'b': 'EEM', 'a_label': 'WTI', 'b_label': 'EEM',
     'interpretation': '负相关=油价冲击EM，正相关=商品周期'},

    # 美股-欧股（全球联动）
    {'name': '美股-欧股', 'a': '^GSPC', 'b': 'EZU', 'a_label': 'SPX', 'b_label': '欧元区',
     'interpretation': '高正相关=全球联动，低相关=区域分化'},

    # 美股-A股（分化程度）
    {'name': '美股-中国', 'a': '^GSPC', 'b': 'FXI', 'a_label': 'SPX', 'b_label': '中国',
     'interpretation': '低相关=中美脱钩，高相关=全球同步'},

    # VIX-信用（恐慌传导）
    {'name': 'VIX-高收益债', 'a': '^VIX', 'b': 'HYG', 'a_label': 'VIX', 'b_label': 'HYG',
     'interpretation': '强负相关=恐慌卖信用，弱相关=信用独立'},

    # BTC-纳斯达克
    {'name': 'BTC-纳斯达克', 'a': 'BTC-USD', 'b': '^NDX', 'a_label': 'BTC', 'b_label': 'NDX',
     'interpretation': '高正相关=风险资产模式，低相关=独立行情'},
]

def fetch_price_data(ticker, days=60):
    """获取价格数据"""
    try:
        end = datetime.now()
        start = end - timedelta(days=days)
        data = yf.Ticker(ticker)
        hist = data.history(start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
        if hist.empty:
            return None
        return hist['Close']
    except:
        return None

def calculate_correlations():
    """计算所有资产对的相关性"""
    print("\n📊 计算跨资产相关性...")
    print(f"   资产对数: {len(CORRELATION_PAIRS)}")
    print(f"   窗口: 20日滚动\n")

    results = []

    for pair in CORRELATION_PAIRS:
        name = pair['name']

        # 获取价格
        price_a = fetch_price_data(pair['a'])
        price_b = fetch_price_data(pair['b'])

        if price_a is None or price_b is None:
            print(f"  ❌ {name}: 数据不足")
            results.append({
                'name': name,
                'a_label': pair['a_label'],
                'b_label': pair['b_label'],
                'corr_20d': None,
                'corr_5d': None,
                'interpretation': pair['interpretation'],
                'signal': '数据不足',
            })
            continue

        # 对齐日期
        df = pd.DataFrame({'a': price_a, 'b': price_b}).dropna()

        if len(df) < 20:
            print(f"  ⚠️ {name}: 数据不足20天")
            results.append({
                'name': name,
                'a_label': pair['a_label'],
                'b_label': pair['b_label'],
                'corr_20d': None,
                'corr_5d': None,
                'interpretation': pair['interpretation'],
                'signal': '数据不足',
            })
            continue

        # 计算日收益率
        returns = df.pct_change().dropna()

        # 20日相关性
        corr_20d = round(float(returns['a'].tail(20).corr(returns['b'].tail(20))), 3)

        # 5日相关性（近期变化）
        corr_5d = round(float(returns['a'].tail(5).corr(returns['b'].tail(5))), 3) if len(returns) >= 5 else None

        # 生成信号
        abs_corr = abs(corr_20d)
        if abs_corr > 0.7:
            strength = '强'
        elif abs_corr > 0.4:
            strength = '中等'
        else:
            strength = '弱'

        direction = '正相关' if corr_20d > 0 else '负相关'
        signal = f"{strength}{direction} ({corr_20d})"

        # 趋势（5日 vs 20日）
        trend = ''
        if corr_5d is not None:
            diff = corr_5d - corr_20d
            if abs(diff) > 0.2:
                trend = ' ↑加强' if diff > 0 else ' ↓减弱'

        results.append({
            'name': name,
            'a_label': pair['a_label'],
            'b_label': pair['b_label'],
            'corr_20d': corr_20d,
            'corr_5d': corr_5d,
            'interpretation': pair['interpretation'],
            'signal': signal + trend,
        })

        c5_display = f"{corr_5d:+.3f}" if corr_5d is not None else "N/A"
        print(f"  ✅ {name}: 20D={corr_20d:+.3f}, 5D={c5_display} → {signal}{trend}")

    return results

def generate_markdown(results):
    """生成Markdown报告"""
    lines = []
    lines.append("## 跨资产相关性矩阵")
    lines.append(f"计算时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"方法: 日收益率，20日滚动窗口")
    lines.append("")
    lines.append("| 资产对 | 20日相关性 | 5日相关性 | 信号 | 含义 |")
    lines.append("|--------|-----------|----------|------|------|")

    for r in results:
        c20 = f"{r['corr_20d']:+.3f}" if r['corr_20d'] is not None else 'N/A'
        c5 = f"{r['corr_5d']:+.3f}" if r['corr_5d'] is not None else 'N/A'
        lines.append(f"| {r['name']} | {c20} | {c5} | {r['signal']} | {r['interpretation']} |")

    lines.append("")

    # 关键发现
    lines.append("### 关键发现")

    for r in results:
        if r['corr_20d'] is None:
            continue

        c = r['corr_20d']
        name = r['name']

        # 股债同跌（正相关 > 0.3）
        if name == '美股-美债' and c > 0.3:
            lines.append(f"- ⚠️ **股债同跌信号**: {name}相关性 {c:+.3f}，传统避险逻辑失效，指向滞胀/危机")

        # 美元黄金正相关（传统关系失效）
        if name == '美元-黄金' and c > 0.2:
            lines.append(f"- ⚠️ **美元-黄金传统关系失效**: 相关性 {c:+.3f}，正常应为负相关")

        # 油价冲击新兴市场
        if name == '油价-新兴市场' and c < -0.3:
            lines.append(f"- ⚠️ **油价冲击EM**: {name}相关性 {c:+.3f}，油涨EM跌，能源冲击传导中")

        # 全球联动上升
        if name == '美股-欧股' and abs(c) > 0.7:
            lines.append(f"- ⚠️ **全球高度联动**: {name}相关性 {c:+.3f}，系统性风险上升")

        # 中美脱钩
        if name == '美股-中国' and abs(c) < 0.3:
            lines.append(f"- 📌 **中美市场脱钩**: {name}相关性 {c:+.3f}，走势独立")

        # VIX传导信用
        if name == 'VIX-高收益债' and c < -0.5:
            lines.append(f"- ⚠️ **恐慌传导信用**: {name}相关性 {c:+.3f}，VIX飙升压制信用市场")

    lines.append("")
    return '\n'.join(lines)

def save_results(results, markdown):
    """保存结果"""
    date_str = datetime.now().strftime('%Y%m%d')
    daily_dir = os.path.join(DATA_DIR, 'daily')
    os.makedirs(daily_dir, exist_ok=True)

    # JSON
    json_path = os.path.join(daily_dir, f'correlation_{date_str}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Markdown
    md_path = os.path.join(daily_dir, f'correlation_{date_str}.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"\n💾 已保存:")
    print(f"  JSON: {json_path} ({os.path.getsize(json_path)} 字节)")
    print(f"  MD: {md_path} ({os.path.getsize(md_path)} 字节)")

# ============ 主程序 ============
if __name__ == '__main__':
    print("=" * 60)
    print("📈 跨资产相关性计算")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    results = calculate_correlations()
    markdown = generate_markdown(results)
    save_results(results, markdown)

    # 预览
    print("\n" + "=" * 60)
    print("📖 相关性矩阵预览:")
    print("=" * 60)
    print(markdown)

    print("\n🎉 相关性计算完成！")
