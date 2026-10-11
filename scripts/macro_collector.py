"""
宏观数据采集模块
数据源：FRED API
"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from env_config import FRED_API_KEY, DATA_DIR

from fredapi import Fred
fred = Fred(api_key=FRED_API_KEY)

# 所有FRED数据系列
FRED_SERIES = {
    "HY_OAS": "BAMLH0A0HYM2",
    "BB_OAS": "BAMLH0A1HYBB",
    "B_OAS": "BAMLH0A2HYB",
    "CCC_OAS": "BAMLH0A3HYC",
    "IG_OAS": "BAMLC0A0CM",
    "UST_2Y": "DGS2",
    "UST_10Y": "DGS10",
    "UST_30Y": "DGS30",
    "TIPS_5Y": "DFII5",
    "TIPS_10Y": "DFII10",
    "BEI_5Y": "T5YIE",
    "BEI_10Y": "T10YIE",
    "CURVE_2S10S": "T10Y2Y",
    "FED_FUNDS": "FEDFUNDS",
    "CPI": "CPIAUCSL",
    "CORE_PCE": "PCEPILFE",
    "UNEMPLOYMENT": "UNRATE",
    "NFP": "PAYEMS",
    "CORE_CPI": "CPILFESL",
    "AHE": "CES0500000003",
    "ICSA": "ICSA",
    "WTI": "WTISPLC",
}

# 信用阈值配置（来自分析框架）
CREDIT_THRESHOLDS = {
    "HY_OAS_WATCH": 3.0,
    "HY_OAS_LEVEL1": 4.0,
    "HY_OAS_LEVEL2": 5.0,
    "CCC_PANIC": 10.0,
}


def fetch_all_macro():
    """采集所有FRED数据"""
    results = {}
    for name, series_id in FRED_SERIES.items():
        try:
            data = fred.get_series(series_id, observation_start='2025-01-01')
            clean = data.dropna()
            if len(clean) > 0:
                latest = float(clean.iloc[-1])
                latest_date = clean.index[-1].strftime('%Y-%m-%d')

                # 计算周变化（对比5个数据点前）
                prev = float(clean.iloc[-6]) if len(clean) > 5 else float(clean.iloc[0])
                if prev != 0:
                    week_chg = latest - prev
                else:
                    week_chg = 0.0

                results[name] = {
                    "value": round(latest, 4),
                    "prev": round(prev, 4),
                    "week_chg": round(week_chg, 4),
                    "date": latest_date,
                }
                print(f"  ✅ {name:15s}: {latest:.4f} (变化{week_chg:+.4f})")
            else:
                print(f"  ⚠️ {name}: 空数据")
        except Exception as e:
            print(f"  ❌ {name}: {str(e)[:50]}")
    return results


def check_thresholds(results):
    """检查信用阈值"""
    alerts = []

    if "HY_OAS" in results:
        hy = results["HY_OAS"]["value"]
        dist_to_400 = CREDIT_THRESHOLDS["HY_OAS_LEVEL1"] - hy

        if hy >= CREDIT_THRESHOLDS["HY_OAS_LEVEL2"]:
            alerts.append(f"🔴🔴 HY OAS {hy}% >= 5.0% 系统性去杠杆阈值!")
        elif hy >= CREDIT_THRESHOLDS["HY_OAS_LEVEL1"]:
            alerts.append(f"🔴 HY OAS {hy}% >= 4.0% 被动卖出阈值!")
        elif hy >= CREDIT_THRESHOLDS["HY_OAS_WATCH"]:
            alerts.append(f"🟡 HY OAS {hy}% 进入关注区间, 距400bp还有{dist_to_400:.2f}%")
        else:
            alerts.append(f"🟢 HY OAS {hy}% 正常")

    if "CCC_OAS" in results:
        ccc = results["CCC_OAS"]["value"]
        if ccc >= CREDIT_THRESHOLDS["CCC_PANIC"]:
            alerts.append(f"🔴 CCC利差 {ccc}% >= 10% 违约恐慌!")
        else:
            alerts.append(f"🟢 CCC利差 {ccc}% 正常")

    return alerts


def calc_derived(results):
    """计算衍生指标"""
    derived = {}

    # 实际利率 = 名义利率 - 盈亏平衡通胀
    if "UST_10Y" in results and "BEI_10Y" in results:
        real_10y = results["UST_10Y"]["value"] - results["BEI_10Y"]["value"]
        derived["REAL_10Y"] = round(real_10y, 4)

    if "UST_2Y" in results and "BEI_5Y" in results:
        real_short = results["UST_2Y"]["value"] - results["BEI_5Y"]["value"]
        derived["REAL_SHORT"] = round(real_short, 4)

    # HY vs IG利差之差
    if "HY_OAS" in results and "IG_OAS" in results:
        hy_ig_diff = results["HY_OAS"]["value"] - results["IG_OAS"]["value"]
        derived["HY_IG_DIFF"] = round(hy_ig_diff, 4)

    return derived


def save_macro(results, alerts, derived):
    """保存宏观数据"""
    today_str = datetime.now().strftime('%Y%m%d')
    output = {
        "date": today_str,
        "data": results,
        "alerts": alerts,
        "derived": derived,
    }
    path = os.path.join(DATA_DIR, "daily", f"macro_{today_str}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"数据已保存: {path}")


if __name__ == "__main__":
    print(f"宏观数据采集 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    results = fetch_all_macro()

    print("\n" + "=" * 60)
    print("📊 信用阈值检查:")
    alerts = check_thresholds(results)
    for a in alerts:
        print(f"  {a}")

    print("\n📐 衍生指标:")
    derived = calc_derived(results)
    for k, v in derived.items():
        print(f"  {k}: {v}")

    save_macro(results, alerts, derived)

    print("=" * 60)
    print("✅ 宏观数据采集完成")
