"""
2026-10-17 数据通道修复回归测试
背景: 恒生指数/恒生国企yfinance连续4日429限流; 东财push2在当前网络直连/代理双双不可达
(SSLError→ProxyError)。修复: 港股指数改腾讯ifzq日K直连为主通道(yfinance降级备用),
AH溢价改新浪rt直连为主通道(akshare新浪日K/东财禁代理为备用)。境内源一律直连不走系统代理。
全部为离线纯逻辑测试,不发起网络请求。
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))

PASS = 0
FAIL = 0

def check(cond, name):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}")

print("=" * 60)
print("数据通道修复测试 (2026-10-17)")
print("=" * 60)

import requests
import china_market_collector as cmc

# --- D1: 直连会话禁用代理(trust_env=False同时无视环境变量与macOS系统代理) ---
s = cmc._direct_session()
check(s.trust_env is False, "D1 直连会话trust_env=False")

# --- D2: _no_proxy临时禁用并恢复requests代理读取 ---
orig = requests.utils.getproxies
with cmc._no_proxy():
    inside = requests.utils.getproxies()
restored_ok = requests.utils.getproxies is orig
check(inside == {} and restored_ok, "D2 _no_proxy生效且退出后恢复原getproxies")

# --- D3: 日收盘序列→指标(跨年边界: ytd取当年首个收盘, week取倒数第5根) ---
dates = ['2025-12-29', '2025-12-30', '2025-12-31', '2026-01-02', '2026-01-05',
         '2026-01-06', '2026-01-07', '2026-01-08', '2026-01-09', '2026-01-12']
closes = [100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0, 180.0, 200.0]
m = cmc._hk_metrics_from_daily(dates, closes)
# close=200, week=(200-150)/150=33.33(倒数第5根=下标5的150), ytd=(200-130)/130=53.85(取2026年首个收盘130)
check(m == {'close': 200.0, 'week_chg': 33.33, 'ytd_chg': 53.85, 'date': '2026-01-12'},
      f"D3 指标计算含跨年YTD (got {m})")

# --- D4: 不足5根 → week_chg=None但close/ytd仍可用 ---
m4 = cmc._hk_metrics_from_daily(['2026-01-02', '2026-01-05', '2026-01-06'], [130.0, 140.0, 150.0])
check(m4['week_chg'] is None and m4['close'] == 150.0 and m4['ytd_chg'] is not None,
      "D4 不足5根周变化为None,其余指标正常")

# --- D5: 周涨幅恰为0时返回0.0而非None ---
m5 = cmc._hk_metrics_from_daily(
    ['2026-01-02', '2026-01-05', '2026-01-06', '2026-01-07', '2026-01-08'],
    [100.0, 110.0, 120.0, 130.0, 100.0])
check(m5['week_chg'] == 0.0, "D5 周涨幅0.0不是None")

# --- D6: 序列全在上一年 → ytd=None ---
m6 = cmc._hk_metrics_from_daily(
    ['2025-12-01', '2025-12-02', '2025-12-03', '2025-12-04', '2025-12-05'],
    [100.0, 101.0, 102.0, 103.0, 104.0])
year_now = str(__import__('datetime').datetime.now().year)
if all(d[:4] != year_now for d in ['2025-12-01']):
    check(m6['ytd_chg'] is None, "D6 无当年数据时ytd=None")

# --- D7: 新浪rt行解析(HSAHP实测格式,2026-10-16真实值) ---
line_hsahp = 'var hq_str_rt_hkHSAHP="HSAHP,HSAHP,127.5600,128.1200,128.9800,127.2700,128.5600,0.4400,0.3434,0.0000,0.0000,0.0000,0,0.0000,0.0000,0.0000,0.0000,2026/10/16,16:08:38,,,,,,";'
p7 = cmc._parse_sina_rt_line(line_hsahp)
check(p7 == {'close': 128.56, 'prev_close': 128.12, 'date': '2026-10-16'},
      f"D7 新浪rt行解析HSAHP (got {p7})")

# --- D8: 新浪rt行解析(HSI实测格式,含52周高低位字段偏移) ---
line_hsi = 'var hq_str_rt_hkHSI="HSI,恒生指数,24321.450,24062.721,24392.300,24087.230,24186.830,124.110,0.520,0.000,0.000,178207245.133,10834829288,0.000,0.000,28056.100,22518.000,2026/10/16,16:08:38,,,,,,",'
p8 = cmc._parse_sina_rt_line(line_hsi)
check(p8 == {'close': 24186.83, 'prev_close': 24062.721, 'date': '2026-10-16'},
      f"D8 新浪rt行解析HSI含字段偏移 (got {p8})")

# --- D9: 非法行 → None ---
check(cmc._parse_sina_rt_line('var x=1;') is None and cmc._parse_sina_rt_line('') is None,
      "D9 非法行返回None")

# --- D10: AH溢价分层信号阈值(140/130/120) ---
check(cmc._ah_signal(145) == '港股极度便宜' and cmc._ah_signal(135) == '港股偏便宜'
      and cmc._ah_signal(125) == '溢价正常' and cmc._ah_signal(118) == '溢价收敛，港股不再便宜',
      "D10 AH溢价四档信号阈值")

# --- D11: AH结果结构(与data_assembler消费的schema一致) ---
r11 = cmc._ah_result(128.56, '2026-10-16', '测试')
check(r11['index_name'] == '恒生AH股溢价指数(HSAHP)' and r11['close'] == 128.56
      and r11['date'] == '2026-10-16' and r11['signal'] == '溢价正常'
      and 'interpretation' in r11, "D11 AH结果schema不变")

# --- D12: 港股腾讯代码映射覆盖两个断供指数 ---
check(cmc.HK_TX_CODE.get('^HSI') == 'hkHSI' and cmc.HK_TX_CODE.get('^HSCE') == 'hkHSCEI',
      "D12 腾讯代码映射覆盖^HSI/^HSCE")

# --- D13: 新主通道产出schema与原yfinance通道一致 ---
m13 = cmc._hk_metrics_from_daily(dates, closes)
check(set(m13.keys()) == {'close', 'week_chg', 'ytd_chg', 'date'}, "D13 港股指标字段集不变")

print("\n" + "=" * 60)
print(f"结果: {PASS} 通过, {FAIL} 失败")
print("=" * 60)
sys.exit(1 if FAIL else 0)
