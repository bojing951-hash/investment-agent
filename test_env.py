"""环境验证脚本 - 测试所有依赖和API连接"""
import sys
print(f"Python版本: {sys.version}")
print("=" * 50)

# 测试1：核心库导入
tests_passed = 0
tests_total = 0

libs = [
    ("yfinance", "yfinance"),
    ("tushare", "tushare"),
    ("fredapi", "fredapi"),
    ("pandas", "pandas"),
    ("numpy", "numpy"),
    ("requests", "requests"),
    ("bs4", "beautifulsoup4"),
    ("openai", "openai"),
    ("feedparser", "feedparser"),
    ("tabulate", "tabulate"),
]

for import_name, display_name in libs:
    tests_total += 1
    try:
        __import__(import_name)
        print(f"  ✅ {display_name}")
        tests_passed += 1
    except ImportError:
        print(f"  ❌ {display_name} - 未安装")

print("=" * 50)

# 测试2：yfinance数据拉取
tests_total += 1
try:
    import yfinance as yf
    spy = yf.Ticker("SPY")
    hist = spy.history(period="5d")
    if len(hist) > 0:
        print(f"  ✅ yfinance数据拉取正常 - SPY最新收盘: {hist['Close'].iloc[-1]:.2f}")
        tests_passed += 1
    else:
        print(f"  ❌ yfinance返回空数据")
except Exception as e:
    print(f"  ❌ yfinance数据拉取失败: {e}")

# 测试3：tushare连接
tests_total += 1
try:
    import tushare as ts
    from env_config import TUSHARE_TOKEN
    if "在这里填入" in TUSHARE_TOKEN:
        print(f"  ⚠️ tushare token未配置，跳过连接测试")
    else:
        pro = ts.pro_api(TUSHARE_TOKEN)
        df = pro.trade_cal(exchange='SSE', start_date='20260101', end_date='20260110')
        if len(df) > 0:
            print(f"  ✅ tushare连接正常 - 获取到{len(df)}条交易日历数据")
            tests_passed += 1
        else:
            print(f"  ❌ tushare返回空数据")
except Exception as e:
    print(f"  ❌ tushare连接失败: {e}")

# 测试4：FRED连接
tests_total += 1
try:
    from fredapi import Fred
    from env_config import FRED_API_KEY
    if "在这里填入" in FRED_API_KEY:
        print(f"  ⚠️ FRED API key未配置，跳过连接测试")
    else:
        fred = Fred(api_key=FRED_API_KEY)
        hy_spread = fred.get_series('BAMLH0A0HYM2', observation_start='2026-03-01')
        if len(hy_spread) > 0:
            print(f"  ✅ FRED连接正常 - HY OAS最新值: {hy_spread.iloc[-1]:.2f}")
            tests_passed += 1
        else:
            print(f"  ❌ FRED返回空数据")
except Exception as e:
    print(f"  ❌ FRED连接失败: {e}")

# 测试5：DeepSeek API连接
tests_total += 1
try:
    from openai import OpenAI
    from env_config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
    if "在这里填入" in DEEPSEEK_API_KEY:
        print(f"  ⚠️ DeepSeek API key未配置，跳过连接测试")
    else:
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "回复OK两个字母"}],
            max_tokens=10
        )
        reply = response.choices[0].message.content.strip()
        print(f"  ✅ DeepSeek API连接正常 - 回复: {reply}")
        tests_passed += 1
except Exception as e:
    print(f"  ❌ DeepSeek API连接失败: {e}")

print("=" * 50)
print(f"测试结果: {tests_passed}/{tests_total} 通过")
if tests_passed == tests_total:
    print("🎉 环境完全就绪！可以开始开发。")
else:
    print("⚠️ 部分测试未通过，请检查上面的错误信息。")
