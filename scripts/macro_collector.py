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
    # 第七轮: 评分卡/利率通道输入统一由macro采集器供给(单一来源), 评分卡不再自采FRED
    "UST_5Y": "DGS5",
    "UMCSENT": "UMCSENT",
    "RSAFS": "RSAFS",
    "INDPRO": "INDPRO",
    "JTSJOL": "JTSJOL",
    # Charter6-P1(A2 §2#1): 美国实际GDP(季频,SAAR,2017链式美元,1947+)——
    # 增长结构主锚;案例B六维状态向量增长维输入之一
    "US_REAL_GDP": "GDPC1",
}

# === Charter6-P0(A2 §4-P0, 2026-11-09): 采集窗口参数化 ======================
# 原硬编码2025年初起点(仅约1年窗口)——长序列研究(六维状态向量/
# expanding z-score/十年期对照)需要历史窗口。默认10年;环境变量
# MACRO_HISTORY_YEARS 可覆盖(正整数,非法值回落默认并告警,最小1年)。
# 口径不变: 每次全量重拉(幂等),FRED返回最新修订值,重拉自动修正历史修订
# (A2 §3 结论: 不做增量合并)。纯函数 macro_observation_start 离线可测。
DEFAULT_HISTORY_YEARS = 10


def _history_years():
    """读 MACRO_HISTORY_YEARS 环境变量(每次调用现读,便于测试与运行期覆盖)。"""
    raw = (os.environ.get('MACRO_HISTORY_YEARS') or '').strip()
    if not raw:
        return DEFAULT_HISTORY_YEARS
    try:
        return max(1, int(raw))
    except ValueError:
        print(f"  ⚠️ MACRO_HISTORY_YEARS={raw!r} 非法(须为正整数),"
              f"回落默认{DEFAULT_HISTORY_YEARS}年")
        return DEFAULT_HISTORY_YEARS


def macro_observation_start(now=None):
    """采集窗口起点(纯函数): now 往前 _history_years() 年,返回'YYYY-MM-DD'。

    2月29日无平年对应日时取3月1日(窗口多含一天,无口径影响)。"""
    now = now or datetime.now()
    years = _history_years()
    try:
        start = datetime(now.year - years, now.month, now.day)
    except ValueError:
        start = datetime(now.year - years, 3, 1)
    return start.strftime('%Y-%m-%d')


# === 真实数据修复轮③(2026-11-10): 源端历史窗口上限的如实注记 ============
# 实测(2026-11-10 直连 FRED API+fredgraph 双通道复核): ICE BofA 族系列
# (HY_OAS/BB_OAS/B_OAS/CCC_OAS/IG_OAS=BAMLH*/BAMLC0A0CM)源端仅提供约3年
# 滚动窗(系列元数据 observation_start=2023-11-10,与请求 observation_start
# 无关);DGS10 等其余系列不受影响(10年窗完整,n=2496)。这不是采集器截断,
# 故在系列条目上如实注记 history_note,不冒充完整10年窗。
_SOURCE_HISTORY_NOTE_THRESHOLD_DAYS = 90   # 月频自然滞后≈31天/季频≈92天内不算


def series_history_note(dates, obs_start, threshold_days=None):
    """序列首观测明显晚于采集窗起点→源端历史上限注记(纯函数,离线可测)。

    返回注记字符串或 None。threshold_days 默认90: 月频系列首观测合法滞后
    至多约1个发布周期(月频≤31天/季频GDP≈51-92天),超过则视为源端窗口
    上限(如 ICE BofA 3年滚动授权窗),如实注记供审计,不静默。"""
    from datetime import date as _date
    if not dates:
        return None
    thr = (_SOURCE_HISTORY_NOTE_THRESHOLD_DAYS if threshold_days is None
           else threshold_days)
    try:
        lag = (_date.fromisoformat(dates[0]) - _date.fromisoformat(obs_start)).days
    except (TypeError, ValueError):
        return None
    if lag <= thr:
        return None
    return (f'源端历史自{dates[0]}起(晚于采集窗起点{obs_start}约{lag // 365}年)'
            f'——源侧窗口上限,非采集器截断;序列深度以实际可得为准')

# 信用阈值配置（来自分析框架）
CREDIT_THRESHOLDS = {
    "HY_OAS_WATCH": 3.0,
    "HY_OAS_LEVEL1": 4.0,
    "HY_OAS_LEVEL2": 5.0,
    "CCC_PANIC": 10.0,
}

# 指标发布频率(第四轮P0-3): 变化计算口径由频率决定,不得统一用"第6个观测值之差"冒充周变化
SERIES_FREQ = {
    "FED_FUNDS": "monthly", "CPI": "monthly", "CORE_PCE": "monthly",
    "UNEMPLOYMENT": "monthly", "NFP": "monthly", "CORE_CPI": "monthly",
    "AHE": "monthly", "WTI": "monthly",
    "UST_5Y": "daily",
    "UMCSENT": "monthly", "RSAFS": "monthly", "INDPRO": "monthly", "JTSJOL": "monthly",
    "ICSA": "weekly",
    "US_REAL_GDP": "quarterly",   # Charter6-P1: GDPC1 季频(变化口径=QoQ/YoY)
    # 其余(BAML利差/DGS收益率/DFII/T5YIE/T10Y2Y)=daily
}

# 指标单位语义(第五轮P1-3): kind决定变化口径 — 指数点变化与百分比变化是两个不同
# 的量(CPI 300→303是3点,环比1.0%是另一含义),不得混用或互相冒充:
#   index  水平值(指数/小时薪): 同时给点数变化(chg)与百分比变化(pct),各自标注
#   rate   利率/利差/失业率(%): 变化用百分点(1百分点=100bp),不给百分比变化
#   count  就业人数/申请人数:   变化用人数(千人/人),百分比变化无意义不给
#   price  价格序列(油价):     同时给价格变化与百分比变化
SERIES_UNITS = {
    "CPI": ("index", "指数点(1982-84=100)"),
    "CORE_CPI": ("index", "指数点(1982-84=100)"),
    "CORE_PCE": ("index", "指数点(2017=100)"),
    "AHE": ("index", "美元/小时"),
    "FED_FUNDS": ("rate", "%"),
    "UNEMPLOYMENT": ("rate", "%(失业率)"),
    "HY_OAS": ("rate", "%(利差)"), "BB_OAS": ("rate", "%(利差)"),
    "B_OAS": ("rate", "%(利差)"), "CCC_OAS": ("rate", "%(利差)"),
    "IG_OAS": ("rate", "%(利差)"),
    "UST_2Y": ("rate", "%"), "UST_10Y": ("rate", "%"), "UST_30Y": ("rate", "%"),
    "TIPS_5Y": ("rate", "%"), "TIPS_10Y": ("rate", "%"),
    "BEI_5Y": ("rate", "%"), "BEI_10Y": ("rate", "%"),
    "CURVE_2S10S": ("rate", "百分点(2s10s斜率)"),
    "NFP": ("count", "千人(非农就业)"),
    "ICSA": ("count", "人(初请失业金)"),
    "WTI": ("price", "美元/桶"),
    "UMCSENT": ("index", "指数点(1966=100)"),
    "RSAFS": ("index", "百万美元"),
    "INDPRO": ("index", "指数点(2017=100)"),
    "JTSJOL": ("count", "千人(职位空缺)"),
    "US_REAL_GDP": ("index", "十亿美元(2017年链式,SAAR)"),
}
# 各kind的变化单位标签(chg字段附_chg_unit,程序与报告据此区分口径)
_CHG_UNIT_BY_KIND = {
    "index": "点", "rate": "百分点(1个百分点=100bp)",
    "count": "人数", "price": "美元",
}


def compute_series_changes(dates, values, freq, unit=None):
    """按频率计算变化(纯函数,离线可测)。unit=(kind, label)来自SERIES_UNITS。

    daily:   week_chg = 最新值 − 约1周前(5~10个自然日内最近的)观测值
    weekly:  week_chg = 最新值 − 上一期(≥5天前最近)观测值
    monthly: mom_chg = 最新值 − 上一期月度观测; yoy_chg = 最新值 − 约12个月前观测
             (不产week_chg — 月度序列没有"周变化"这个口径)
    quarterly(Charter6-P1): qoq_chg = 最新值 − 上一期季度观测; yoy_chg = 约4季前
             (季频无周/月变化口径;GDPC1 举例)
    单位语义(第五轮P1-3): 所有派生指标标注 unit/chg_unit/from/formula;
    index/price类同时产百分比变化(mom_pct/yoy_pct/week_pct=(v/v0−1)×100),
    rate类变化一律百分点(不给百分比变化),count类变化一律人数。
    dates为'YYYY-MM-DD'字符串列表(升序), values为对应float列表。"""
    from datetime import date
    out = {}
    if not dates or len(values) < 2 or len(dates) != len(values):
        return out
    kind, ulabel = unit if unit else (None, None)
    chg_unit = _CHG_UNIT_BY_KIND.get(kind)
    if ulabel:
        out["unit"] = ulabel
    latest_d, latest_v = dates[-1], float(values[-1])
    d_last = date.fromisoformat(latest_d)

    def _pick(days_min, days_max):
        """取距最新观测 days_min~days_max 自然日内最近的那个观测(索引,日期,值)。"""
        best = None
        for i in range(len(dates) - 2, -1, -1):
            lag = (d_last - date.fromisoformat(dates[i])).days
            if days_min <= lag <= days_max:
                return i, dates[i], float(values[i])
            if lag > days_max:
                break
        return best

    def _emit(chg_field, d0, v0, period_cn):
        """写入一条变化记录: 点数/水平变化(+百分比变化,仅index/price)+窗口元数据。"""
        out[chg_field] = round(latest_v - v0, 4)
        out[f"{chg_field}_from"] = d0
        out[f"{chg_field}_formula"] = f"{latest_d}值−{d0}值({period_cn})"
        if chg_unit:
            out[f"{chg_field}_unit"] = chg_unit
        if kind in ("index", "price") and abs(v0) > 1e-12:
            pf = f"{chg_field.rsplit('_chg', 1)[0]}_pct" if chg_field.endswith('_chg') else f"{chg_field}_pct"
            out[pf] = round((latest_v / v0 - 1.0) * 100.0, 4)
            out[f"{pf}_from"] = d0
            out[f"{pf}_formula"] = f"({latest_d}值/{d0}值−1)×100({period_cn}百分比)"

    if freq == "monthly":
        prev = _pick(21, 45)     # 上一期月度观测
        yoy = _pick(330, 400)    # 约12个月前
        if prev:
            i, d0, v0 = prev
            out["prev"] = round(v0, 4)
            _emit("mom_chg", d0, v0, "月度环比")
        if yoy:
            i, d0, v0 = yoy
            _emit("yoy_chg", d0, v0, "同比")
    elif freq == "quarterly":
        # Charter6-P1(A2 §2#1): 季频系列(GDPC1)——QoQ=上一季观测(自然日滞后
        # 约88~95天取最近),YoY=约4季前(330~400天取最近);口径与月频分支同构
        prev = _pick(70, 110)    # 上一期季度观测
        yoy = _pick(330, 400)    # 约4个季度前
        if prev:
            i, d0, v0 = prev
            out["prev"] = round(v0, 4)
            _emit("qoq_chg", d0, v0, "季度环比")
        if yoy:
            i, d0, v0 = yoy
            _emit("yoy_chg", d0, v0, "同比")
    elif freq == "weekly":
        prev = _pick(5, 14)      # 上一期周度观测
        if prev:
            i, d0, v0 = prev
            out["prev"] = round(v0, 4)
            _emit("week_chg", d0, v0, "周度环比")
    else:  # daily
        prev = _pick(5, 10)      # 约1周前(5个交易日的自然日近似)
        if prev:
            i, d0, v0 = prev
            out["prev"] = round(v0, 4)
            _emit("week_chg", d0, v0, "约一周,交易日口径")
    return out


def detect_revisions(name, results, today_str):
    """历史数据修订检测(第四轮P0-3): 与上一采集日文件比对 — 同一观测日数值变化即修订,
    记录{obs_date, prev_value, value, detected}; 无历史文件时标注数据限制,不伪造。"""
    import glob as _glob
    prev_files = sorted(_glob.glob(os.path.join(DATA_DIR, "daily", "macro_*.json")))
    prev_files = [p for p in prev_files if os.path.basename(p) != f"macro_{today_str}.json"]
    if not prev_files:
        return None
    try:
        with open(prev_files[-1], 'r', encoding='utf-8') as f:
            old = json.load(f)
        old_item = (old.get('data') or {}).get(name) or {}
    except Exception:
        return None
    new_item = results.get(name) or {}
    old_d, new_d = old_item.get('date'), new_item.get('date')
    old_v, new_v = old_item.get('value'), new_item.get('value')
    if old_d and new_d == old_d and isinstance(old_v, (int, float)) and isinstance(new_v, (int, float)) \
            and abs(new_v - old_v) > 1e-9:
        return {"obs_date": new_d, "prev_value": old_v, "value": new_v, "detected": today_str}
    return None


def fetch_all_macro():
    """采集所有FRED数据(第四轮P0-3: 按系列频率分别计算变化,附窗口元数据与修订检测)"""
    results = {}
    today_str = datetime.now().strftime('%Y%m%d')
    obs_start = macro_observation_start()
    print(f"  📅 FRED采集窗口: observation_start={obs_start}"
          f"(MACRO_HISTORY_YEARS={_history_years()})")
    for name, series_id in FRED_SERIES.items():
        try:
            data = fred.get_series(series_id, observation_start=obs_start)
            clean = data.dropna()
            if len(clean) > 0:
                latest = float(clean.iloc[-1])
                latest_date = clean.index[-1].strftime('%Y-%m-%d')
                freq = SERIES_FREQ.get(name, 'daily')
                dates = [d.strftime('%Y-%m-%d') for d in clean.index]
                values = [float(v) for v in clean.values]
                item = {"value": round(latest, 4), "date": latest_date, "frequency": freq}
                # 第七轮Layer2: 附加原始序列(事实引擎统一计算收益/环比,替代各处自带口径)
                item["series"] = {"dates": dates, "values": values}
                # 修复轮③: 源端历史上限如实注记(ICE BofA族3年滚动窗等)
                note = series_history_note(dates, obs_start)
                if note:
                    item["history_note"] = note
                    print(f"  ⚠️ {name}: {note}")
                item.update(compute_series_changes(dates, values, freq,
                                                   unit=SERIES_UNITS.get(name)))
                rev = detect_revisions(name, {name: item}, today_str)
                if rev:
                    item["revision"] = rev
                results[name] = item
                chg_disp = item.get('week_chg', item.get('mom_chg'))
                print(f"  ✅ {name:15s}: {latest:.4f} ({freq},变化{chg_disp:+.4f})" if isinstance(chg_disp, (int, float))
                      else f"  ✅ {name:15s}: {latest:.4f} ({freq})")
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
