#!/usr/bin/env python3
"""
利率预期采集模块 v2.0(Layer 1采集器,2026-10-17第七轮重构)
- 联邦基金期货隐含利率（yfinance）
- 当前联邦基金利率（FRED）
- 语义修正(spec §5): 期货价格隐含的是**合约日历月的月均**有效利率(100−价格),
  与当前时点利率之差只作方向性参考;**不得**将差值除以0.25换算为"降息次数"
  (月均含会议日历结构与概率加权,整除换算在数学上不成立——v1的cuts_25bp已删除)。
"""

import os
import sys
import json
import glob
import time
import requests
from datetime import datetime, timedelta

# 项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from env_config import FRED_API_KEY

def _load_cached_futures(max_age_days=7, data_dir=None):
    """429限流兜底: 从最近的rate_economy_*.json读取上次成功的期货曲线。
    只接受7日内带有效价格的行;返回(rows, 原始日期)或(None, None)。"""
    daily_dir = data_dir or os.path.join(ROOT_DIR, 'data', 'daily')
    candidates = sorted(glob.glob(os.path.join(daily_dir, 'rate_economy_*.json')), reverse=True)
    for path in candidates[:14]:
        try:
            with open(path, encoding='utf-8') as fh:
                prev = json.load(fh)
            rows = [r for r in (prev.get('fed_funds_futures') or [])
                    if isinstance(r.get('price'), (int, float)) and r.get('ticker')]
            if not rows:
                continue
            gen_date = str(prev.get('date') or '')
            try:
                age = (datetime.now() - datetime.strptime(gen_date, '%Y%m%d')).days
            except ValueError:
                continue
            if age < 0 or age > max_age_days:
                continue
            return rows, gen_date
        except Exception:
            continue
    return None, None


def fetch_fed_funds_futures(max_rounds=3, data_dir=None):
    """通过yfinance获取联邦基金期货价格，计算隐含利率。
    2026-10-21 P1修复(连续多日429×11全军覆没):
    ① 主力ZQ=F优先(Gate A核心只依赖它); ② 整轮重试+退避(20s/45s,只补缺失合约);
    ③ 主力仍缺→7日内缓存曲线兜底(整条曲线同源,不与当日部分合约混搭,各行带source标记)。"""
    import yfinance as yf

    print("\n📊 采集联邦基金期货隐含利率...")

    # 近月和远月期货合约
    # ZQ=F 是活跃月合约
    futures_tickers = {
        'ZQ=F': '近月(活跃月)',
    }

    # 生成未来9个月的合约代码
    # Yahoo Finance 格式: ZQ{月代码}{两位年份}.CBT
    # 例: ZQK26.CBT = 2026年5月, ZQM26.CBT = 2026年6月
    now = datetime.now()
    month_codes = {1:'F', 2:'G', 3:'H', 4:'J', 5:'K', 6:'M',
                   7:'N', 8:'Q', 9:'U', 10:'V', 11:'X', 12:'Z'}

    seen_months = set()
    for i in range(0, 10):
        target = now + timedelta(days=30*i)
        month_key = (target.year, target.month)
        if month_key in seen_months:
            continue
        seen_months.add(month_key)

        month_code = month_codes[target.month]
        year_code = str(target.year)[-2:]  # 两位年份: 26, 27
        ticker = f"ZQ{month_code}{year_code}.CBT"
        label = target.strftime('%Y年%m月')
        futures_tickers[ticker] = label

    # 主力合约先采(核心依赖),月份合约随后
    order = ['ZQ=F'] + [t for t in futures_tickers if t != 'ZQ=F']
    backoffs = [0, 20, 45]  # 首轮立即,二三轮退避后只补缺失
    results_map = {}

    for rnd in range(max_rounds):
        missing = [t for t in order if t not in results_map]
        if not missing:
            break
        if backoffs[rnd]:
            print(f"  ⏳ 第{rnd+1}轮重试(退避{backoffs[rnd]}s后,剩余缺失 {len(missing)} 个合约)...")
            time.sleep(backoffs[rnd])
        for ticker in missing:
            label = futures_tickers[ticker]
            try:
                hist = yf.Ticker(ticker).history(period='5d')
                if hist is not None and len(hist) > 0:
                    price = float(hist['Close'].iloc[-1])
                    implied_rate = round(100 - price, 4)
                    results_map[ticker] = {
                        'ticker': ticker,
                        'label': label,
                        'price': round(price, 4),
                        'implied_rate_pct': implied_rate,
                        'date': str(hist.index[-1].date()),
                        'source': 'yfinance',
                    }
                    print(f"  ✅ {label} ({ticker}): 价格 {price:.4f} → 隐含利率 {implied_rate:.4f}%")
                else:
                    print(f"  ⚠️ {label} ({ticker}): 无数据")
            except Exception as e:
                print(f"  ⚠️ {label} ({ticker}): {e}")
            time.sleep(1.0)  # 逐合约间隔,避免连发触发限流

    results = [results_map[t] for t in order if t in results_map]

    # 主力缺失 → 缓存兜底(曲线整体换用缓存,保持同源同日,不混搭)
    if 'ZQ=F' not in results_map:
        cached, cache_date = _load_cached_futures(data_dir=data_dir)
        if cached:
            print(f"  ⚠️ 主力ZQ=F实时采集失败(疑似限流)→ 启用 {cache_date} 缓存曲线兜底 "
                  f"({len(cached)}个合约,各行观测日见date字段,source=cache标记)")
            results = [dict(r, source=f'cache:{cache_date}') for r in cached]
        else:
            print("  ❌ ZQ实时采集与缓存兜底均失败——今日期货曲线缺失,Gate A将如实记FAIL")

    return results

def _fred_observations(series_id, limit=5, tries=3):
    """FRED观测序列,带指数退避重试(2026-10-21: PAYEMS/NFP曾单序列瞬时失败,
    当日其余FRED全部正常——瞬时抖动不应直接变成Gate A core缺失)。"""
    last_err = None
    url = "https://api.stlouisfed.org/fred/series/observations"
    for i in range(tries):
        try:
            resp = requests.get(url, params={
                'series_id': series_id,
                'api_key': FRED_API_KEY,
                'file_type': 'json',
                'sort_order': 'desc',
                'limit': limit,
            }, timeout=15)
            data = resp.json()
            if data.get('observations'):
                return data['observations']
            last_err = f"空观测({str(data)[:80]})"
        except Exception as e:
            last_err = str(e)
        if i < tries - 1:
            wait = 3 * (i + 1)
            print(f"    ⏳ {series_id} 第{i+1}次失败({last_err[:60]}),{wait}s后重试...")
            time.sleep(wait)
    print(f"  ⚠️ {series_id}: {tries}次尝试均失败——{last_err}")
    return []


def fetch_current_fed_rate():
    """从FRED获取当前联邦基金有效利率"""

    print("\n📊 采集当前联邦基金利率...")

    series_map = {
        'FEDFUNDS': '联邦基金有效利率(月)',
        'DFF': '联邦基金有效利率(日)',
        'DFEDTARU': '联邦基金目标上限',
        'DFEDTARL': '联邦基金目标下限',
    }

    results = {}

    for series_id, name in series_map.items():
        for obs in _fred_observations(series_id):
            if obs.get('value') not in (None, '.', ''):
                results[series_id] = {
                    'name': name,
                    'value': float(obs['value']),
                    'date': obs['date']
                }
                print(f"  ✅ {name}: {obs['value']}% ({obs['date']})")
                break

    return results

def fetch_real_economy_data():
    """从FRED获取实体经济关键指标"""

    print("\n📊 采集实体经济指标...")

    series_map = {
        # (名称, 单位, 频率) — P0修复: 以下FRED序列全部为月度发布,
        # change是"上一月度观测→最新月度观测"的跨度,不得当作周变化解读
        'UMCSENT': ('密歇根消费者信心', 'index', 'Monthly'),
        'RSAFS': ('零售销售(十亿美元)', 'billions', 'Monthly'),
        'PAYEMS': ('非农就业(千人)', 'thousands', 'Monthly'),
        'INDPRO': ('工业生产指数', 'index', 'Monthly'),
        'UNRATE': ('失业率', 'pct', 'Monthly'),
        'JTSJOL': ('职位空缺(千个)', 'thousands', 'Monthly'),
    }

    results = {}

    for series_id, (name, unit, freq) in series_map.items():
        values = []
        for obs in _fred_observations(series_id, limit=3):
            if obs.get('value') not in (None, '.', ''):
                values.append({
                    'value': float(obs['value']),
                    'date': obs['date']
                })

        if values:
            latest = values[0]
            prev = values[1] if len(values) > 1 else None

            change = None
            if prev:
                change = round(latest['value'] - prev['value'], 2)

            results[series_id] = {
                'name': name,
                'value': latest['value'],
                'date': latest['date'],
                'prev_value': prev['value'] if prev else None,
                'change': change,
                'change_period': f"{prev['date']}→{latest['date']}" if prev else None,
                'unit': unit,
                'freq': freq
            }

            change_str = f" (变化: {'+' if change > 0 else ''}{change})" if change else ""
            print(f"  ✅ {name}: {latest['value']}{change_str} ({latest['date']})")

    return results

def calculate_rate_expectations(futures, current_rate):
    """计算市场利率预期"""
    print("\n📊 计算利率预期...")

    if not futures or not current_rate:
        print("  ⚠️ 数据不足，无法计算预期")
        return None

    # 获取当前联邦基金目标区间
    upper = current_rate.get('DFEDTARU', {}).get('value', None)
    lower = current_rate.get('DFEDTARL', {}).get('value', None)
    effective = current_rate.get('DFF', {}).get('value', None) or current_rate.get('FEDFUNDS', {}).get('value', None)

    if upper and lower:
        target_mid = round((upper + lower) / 2, 4)
        target_range = f"{lower:.2f}% - {upper:.2f}%"
    else:
        target_mid = effective
        target_range = f"{effective:.2f}%"

    print(f"  当前目标区间: {target_range}")
    print(f"  当前有效利率: {effective:.2f}%")

    expectations = {
        'current_target_range': target_range,
        'current_effective_rate': effective,
        'target_midpoint': target_mid,
        'forward_rates': [],
        'basis_note': '期货隐含=合约日历月月均有效利率(100-价格);对比基准为当前时点利率;'
                      '月均口径vs时点口径,不得换算为降息/加息次数',
        'market_view': ''
    }

    # 去重并排序
    seen = set()
    unique_futures = []
    for f in futures:
        key = f['label']
        if key not in seen:
            seen.add(key)
            unique_futures.append(f)

    # 计算每个月的隐含水平与方向性差异
    # (第七轮: 删除cuts_25bp=diff/0.25的伪精确换算——隐含为月均口径,不可折算次数)
    for f in unique_futures:
        implied = f['implied_rate_pct']
        diff_from_current = round(implied - (effective or target_mid), 4)

        entry = {
            'month': f['label'],
            'implied_avg_rate': implied,
            'diff_from_current': diff_from_current,
            'direction': ('隐含低于当前' if diff_from_current < -0.10
                          else '隐含高于当前' if diff_from_current > 0.10 else '与当前相当')
        }
        expectations['forward_rates'].append(entry)
        print(f"  {f['label']}: 月均隐含 {implied:.2f}% (vs当前 {diff_from_current:+.2f}pp) → {entry['direction']}")

    # 最远月隐含水平 vs 当前的方向性描述(仅描述,不折算次数)
    if expectations['forward_rates']:
        furthest = expectations['forward_rates'][-1]

        if furthest['diff_from_current'] < -0.50:
            expectations['market_view'] = '远月隐含显著低于当前(月均口径)'
        elif furthest['diff_from_current'] < -0.10:
            expectations['market_view'] = '远月隐含温和低于当前(月均口径)'
        elif furthest['diff_from_current'] > 0.50:
            expectations['market_view'] = '远月隐含显著高于当前(月均口径)'
        elif furthest['diff_from_current'] > 0.10:
            expectations['market_view'] = '远月隐含温和高于当前(月均口径)'
        else:
            expectations['market_view'] = '远月隐含与当前基本持平(月均口径)'

    print(f"\n  📌 市场总体判断: {expectations['market_view']}")

    return expectations

def save_results(futures, current_rate, real_economy, expectations):
    """保存结果"""
    today = datetime.now().strftime('%Y%m%d')
    output_dir = os.path.join(ROOT_DIR, 'data', 'daily')
    os.makedirs(output_dir, exist_ok=True)

    # JSON
    result = {
        'date': today,
        'fed_funds_futures': futures,
        'current_rates': current_rate,
        'real_economy': real_economy,
        'rate_expectations': expectations,
        'generated_at': datetime.now().isoformat()
    }

    json_path = os.path.join(output_dir, f'rate_economy_{today}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n💾 JSON已保存: {json_path} ({os.path.getsize(json_path)} bytes)")

    # Markdown摘要
    md_lines = [
        f"# 利率预期与实体经济 ({today})",
        "",
        "## 联邦基金利率",
    ]

    if current_rate:
        for k, v in current_rate.items():
            md_lines.append(f"- {v['name']}: {v['value']}% ({v['date']})")

    if expectations:
        md_lines.append(f"\n## 利率预期(月均口径)")
        md_lines.append(f"- 当前目标区间: {expectations['current_target_range']}")
        md_lines.append(f"- 远月方向: **{expectations['market_view']}**")
        md_lines.append(f"- 口径注记: {expectations.get('basis_note', '')}")
        if expectations['forward_rates']:
            md_lines.append(f"- 各月隐含(合约=该日历月月均有效利率):")
            for fr in expectations['forward_rates']:
                md_lines.append(f"  - {fr['month']}: 月均 {fr['implied_avg_rate']:.2f}% "
                                f"({fr['diff_from_current']:+.2f}pp, {fr['direction']})")

    if real_economy:
        md_lines.append(f"\n## 实体经济指标")
        for k, v in real_economy.items():
            freq_tag = f"[{v.get('freq', '?')}]" if v.get('freq') else ""
            if v.get('change'):
                change_str = (f" (变化: {'+' if v['change'] > 0 else ''}{v['change']}"
                              + (f", 区间{v['change_period']}" if v.get('change_period') else "") + ")")
            else:
                change_str = ""
            md_lines.append(f"- {v['name']}{freq_tag}: {v['value']}{change_str} (观测日: {v['date']})")

    md_path = os.path.join(output_dir, f'rate_economy_{today}.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    print(f"💾 MD已保存: {md_path} ({os.path.getsize(md_path)} bytes)")

    return json_path, md_path

if __name__ == '__main__':
    print("=" * 60)
    print("📈 利率预期与实体经济采集器 v1.0")
    print("=" * 60)

    # Step 1: 联邦基金期货
    futures = fetch_fed_funds_futures()

    # Step 2: 当前利率
    current_rate = fetch_current_fed_rate()

    # Step 3: 实体经济
    real_economy = fetch_real_economy_data()

    # Step 4: 计算预期
    expectations = calculate_rate_expectations(futures, current_rate)

    # Step 5: 保存
    json_path, md_path = save_results(futures, current_rate, real_economy, expectations)

    print("\n" + "=" * 60)
    print("✅ 采集完成!")
    print("=" * 60)
