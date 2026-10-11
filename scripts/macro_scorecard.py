#!/usr/bin/env python3
"""
宏观体制评分卡 v1.0
基于增长×通胀二维评分系统，量化判断当前宏观体制
"""

import os
import sys
import json
import requests
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from env_config import FRED_API_KEY

def fetch_fred(series_id, limit=5):
    """从FRED获取最新数据"""
    try:
        url = 'https://api.stlouisfed.org/fred/series/observations'
        params = {
            'series_id': series_id,
            'api_key': FRED_API_KEY,
            'file_type': 'json',
            'sort_order': 'desc',
            'limit': limit
        }
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        if 'observations' in data:
            values = []
            for obs in data['observations']:
                if obs['value'] != '.':
                    values.append({
                        'value': float(obs['value']),
                        'date': obs['date']
                    })
            return values
    except Exception as e:
        print(f"  ⚠️ FRED {series_id} 失败: {e}")
    return []

def compute_yoy_change(series_id):
    """计算同比变化率"""
    values = fetch_fred(series_id, limit=15)
    if len(values) >= 13:
        current = values[0]['value']
        year_ago = values[12]['value']
        if year_ago != 0:
            return round((current - year_ago) / year_ago * 100, 2), values[0]['date']
    return None, None

def compute_mom_change(series_id):
    """计算环比变化率"""
    values = fetch_fred(series_id, limit=3)
    if len(values) >= 2:
        current = values[0]['value']
        prev = values[1]['value']
        if prev != 0:
            return round((current - prev) / prev * 100, 2), values[0]['date']
    return None, None

def compute_3m_change(series_id):
    """计算3个月变化"""
    values = fetch_fred(series_id, limit=5)
    if len(values) >= 4:
        current = values[0]['value']
        three_months_ago = values[3]['value']
        return round(current - three_months_ago, 2), values[0]['date']
    return None, None

def score_growth():
    """增长维度评分"""
    print("\n📊 增长维度评分...")
    scores = {}

    # 1. 消费者信心 (UMCSENT)
    vals = fetch_fred('UMCSENT', 3)
    if vals:
        v = vals[0]['value']
        if v < 50: s = -2
        elif v < 60: s = -1
        elif v < 80: s = 0
        elif v < 95: s = 1
        else: s = 2
        scores['consumer_confidence'] = {
            'name': '消费者信心(密歇根)',
            'value': v, 'date': vals[0]['date'], 'score': s,
            'thresholds': '收缩<60 | 扩张>80',
            'distance_to_switch': f"距收缩线: {round(v-60,1)}" if v >= 60 else f"已低于收缩线 {round(60-v,1)}"
        }
        print(f"  ✅ 消费者信心: {v} → 评分 {s:+d}")

    # 2. 失业率3个月变化 (UNRATE)
    change, date = compute_3m_change('UNRATE')
    if change is not None:
        if change > 0.5: s = -2
        elif change > 0.3: s = -1
        elif change > -0.1: s = 0
        elif change > -0.3: s = 1
        else: s = 2
        scores['unemployment_change'] = {
            'name': '失业率3月变化',
            'value': change, 'date': date, 'score': s,
            'unit': '百分点',
            'thresholds': '恶化>+0.3 | 改善<0',
            'distance_to_switch': f"距恶化线: {round(0.3-change,2)}pp" if change <= 0.3 else f"已超恶化线 {round(change-0.3,2)}pp"
        }
        print(f"  ✅ 失业率3m变化: {change:+.2f}pp → 评分 {s:+d}")

    # 3. 零售销售环比 (RSAFS)
    mom, date = compute_mom_change('RSAFS')
    if mom is not None:
        if mom < -1: s = -2
        elif mom < -0.5: s = -1
        elif mom < 0.5: s = 0
        elif mom < 1: s = 1
        else: s = 2
        scores['retail_sales_mom'] = {
            'name': '零售销售环比',
            'value': mom, 'date': date, 'score': s,
            'unit': '%',
            'thresholds': '收缩<-0.5% | 扩张>+0.5%'
        }
        print(f"  ✅ 零售销售MoM: {mom:+.2f}% → 评分 {s:+d}")

    # 4. 工业生产环比 (INDPRO)
    mom, date = compute_mom_change('INDPRO')
    if mom is not None:
        if mom < -1: s = -2
        elif mom < -0.3: s = -1
        elif mom < 0.3: s = 0
        elif mom < 1: s = 1
        else: s = 2
        scores['industrial_production'] = {
            'name': '工业生产环比',
            'value': mom, 'date': date, 'score': s,
            'unit': '%',
            'thresholds': '收缩<-0.3% | 扩张>+0.3%'
        }
        print(f"  ✅ 工业生产MoM: {mom:+.2f}% → 评分 {s:+d}")

    total = sum(item['score'] for item in scores.values())
    print(f"\n  📌 增长总分: {total:+d} (范围 -8 至 +8)")

    return scores, total

def score_inflation():
    """通胀维度评分"""
    print("\n📊 通胀维度评分...")
    scores = {}

    # 1. 核心CPI同比 (CPILFESL)
    yoy, date = compute_yoy_change('CPILFESL')
    if yoy is not None:
        if yoy < 1: s = -2
        elif yoy < 2: s = -1
        elif yoy < 2.5: s = 0
        elif yoy < 3.5: s = 1
        else: s = 2
        scores['core_cpi_yoy'] = {
            'name': '核心CPI同比',
            'value': yoy, 'date': date, 'score': s,
            'unit': '%',
            'thresholds': '通缩<2% | 高通胀>3.5%',
            'distance_to_switch': f"距高通胀线: {round(3.5-yoy,2)}%" if yoy <= 3.5 else f"已超高通胀线 {round(yoy-3.5,2)}%"
        }
        print(f"  ✅ 核心CPI YoY: {yoy:.2f}% → 评分 {s:+d}")

    # 2. BEI 10Y (T10YIE)
    vals = fetch_fred('T10YIE', 3)
    if vals:
        v = vals[0]['value']
        if v < 1.5: s = -2
        elif v < 2: s = -1
        elif v < 2.3: s = 0
        elif v < 2.6: s = 1
        else: s = 2
        scores['bei_10y'] = {
            'name': 'BEI 10Y(通胀预期)',
            'value': v, 'date': vals[0]['date'], 'score': s,
            'unit': '%',
            'thresholds': '低通胀<2% | 高通胀>2.5%',
            'distance_to_switch': f"距高通胀线: {round(2.6-v,2)}%" if v <= 2.6 else f"已超高通胀线"
        }
        print(f"  ✅ BEI 10Y: {v:.2f}% → 评分 {s:+d}")

    # 3. WTI油价 (用yfinance实时价)
    try:
        import yfinance as yf
        oil = yf.Ticker('CL=F')
        hist = oil.history(period='5d')
        if hist is not None and len(hist) > 0:
            v = float(hist['Close'].iloc[-1])
            if v < 40: s = -2
            elif v < 50: s = -1
            elif v < 70: s = 0
            elif v < 90: s = 1
            else: s = 2
            scores['wti_oil'] = {
                'name': 'WTI油价',
                'value': round(v, 2), 'date': str(hist.index[-1].date()), 'score': s,
                'unit': '美元/桶',
                'thresholds': '需求担忧<50 | 通胀推升>90'
            }
            print(f"  ✅ WTI油价: ${v:.2f} → 评分 {s:+d}")
    except Exception as e:
        print(f"  ⚠️ WTI油价: {e}")

    # 4. 平均时薪同比 (CES0500000003)
    yoy, date = compute_yoy_change('CES0500000003')
    if yoy is not None:
        if yoy < 2: s = -2
        elif yoy < 3: s = -1
        elif yoy < 3.5: s = 0
        elif yoy < 4.5: s = 1
        else: s = 2
        scores['ahe_yoy'] = {
            'name': '平均时薪同比',
            'value': yoy, 'date': date, 'score': s,
            'unit': '%',
            'thresholds': '低工资<3% | 高工资>4.5%'
        }
        print(f"  ✅ 平均时薪 YoY: {yoy:.2f}% → 评分 {s:+d}")

    total = sum(item['score'] for item in scores.values())
    print(f"\n  📌 通胀总分: {total:+d} (范围 -8 至 +8)")

    return scores, total

def determine_regime(g_total, i_total):
    """
    体制映射 v2.0：
    - 通胀总分 ≤ +2 且增长 > 0 → 再通胀 (Reflation)
    - 通胀总分 ≤ +2 且增长 ≤ 0 → 衰退 (Recession)
    - 通胀总分 ≥ +3 且增长 ≤ 0 → 滞胀 (Stagflation)
    - 通胀总分 ≥ +3 且增长 > 0 → 类滞胀 (Stagflation-lite)
    注：类滞胀 = 增长尚可但通胀压力主导，不应与再通胀混淆
    """
    if i_total >= 3:
        if g_total > 0:
            regime = "类滞胀"
            desc = (f"增长勉强为正(+{g_total})但通胀压力主导(+{i_total})。"
                    f"通胀水平偏高且具粘性，不符合再通胀(Reflation)定义。"
                    f"本质上仍是滞胀倾向环境，增长端随时可能转负。")
        else:
            regime = "滞胀"
            desc = (f"增长疲软({g_total})叠加高通胀(+{i_total})。"
                    f"经典滞胀格局：央行无法放松，实体承压。")
    else:  # i_total <= 2
        if g_total > 0:
            regime = "再通胀"
            desc = (f"增长回升(+{g_total})伴随温和通胀(+{i_total})。"
                    f"符合Reflation经典定义：产出缺口收窄，物价温和上行。")
        else:
            regime = "衰退"
            desc = (f"增长走弱({g_total})且通胀低迷(+{i_total})。"
                    f"需求不足主导，关注央行宽松空间。")

    return regime, desc

def resolve_transition(prev_confirmed, prev_pending, prev_status, current_regime):
    """体制切换裁决(2026-10-11 P0修复: 提取为纯函数,可单元测试)

    规则不变: 新体制须在两个不同观察周被独立计算出来才确认。
    调用方必须保证 prev_* 来自上一个不同的ISO周(见 _prev_distinct_week_file)。
    """
    if not prev_confirmed:
        return current_regime, "confirmed", 5                      # 首次运行

    if prev_status == 'pending_confirmation':
        if current_regime == prev_pending:
            return current_regime, "confirmed", 5                  # 连续两周一致→确认
        elif current_regime == prev_confirmed:
            return prev_confirmed, "confirmed", 5                  # 回归原体制→取消
        else:
            return prev_confirmed, "pending_confirmation", 3       # 第三种→重新待确认
    elif current_regime != prev_confirmed:
        return prev_confirmed, "pending_confirmation", 3           # 首次出现切换信号
    else:
        return current_regime, "confirmed", 5                      # 维持


def _prev_distinct_week_file(files, today_str):
    """从按时间排序的评分卡文件里,找最近一个"不同ISO周"的文件。

    P0修复核心: 流水线每天跑,评分卡每日一份。原逻辑取"上一个文件",
    周一出现信号、周二同样的月度数据重复计算同一体制,即被当作"连续两周一致"→
    两个自然日就完成"两周验证"。现在同周文件一律视为回声,只与上周(或更早)比对。
    """
    from datetime import date
    t = date(int(today_str[:4]), int(today_str[4:6]), int(today_str[6:8]))
    t_week = t.isocalendar()[1]
    t_year = t.isocalendar()[0]
    for f in reversed(files):
        try:
            d = date(int(f[-13:-9]), int(f[-9:-7]), int(f[-7:-5]))
            iso = d.isocalendar()
            if (iso[0], iso[1]) != (t_year, t_week):
                return f
        except ValueError:
            continue
    return None


def attribute_regime(g_scores, g_total, i_scores, i_total):
    """体制归因(P1, 2026-10-11): 反事实分解 — 逐项剔除单个指标后重算体制,
    体制发生翻转的指标即为"关键驱动"。返回(驱动列表, 全部反事实列表)。

    用途: 周报"体制判断依据"不再只有总分,还能回答"是哪个指标把总分推过线"。
    """
    base_regime, _ = determine_regime(g_total, i_total)
    drivers, counterfactuals = [], []
    for dim, scores, total in (('增长', g_scores, g_total), ('通胀', i_scores, i_total)):
        for key, s in scores.items():
            ng = total - s['score'] if dim == '增长' else g_total
            ni = total - s['score'] if dim == '通胀' else i_total
            cf, _ = determine_regime(ng, ni)
            counterfactuals.append({'indicator': s['name'], 'dimension': dim,
                                    'score': s['score'], 'regime_without': cf})
            if cf != base_regime:
                drivers.append(f"{s['name']}({s['score']:+d}): 剔除后体制变为[{cf}] — 关键驱动")
    return drivers, counterfactuals


def save_scorecard(g_scores, g_total, i_scores, i_total, regime, desc):
    today = datetime.now().strftime('%Y%m%d')
    data_dir = os.path.join(ROOT_DIR, 'data', 'daily')
    os.makedirs(data_dir, exist_ok=True)

    # === 切换确认机制 v2.0 ===
    # 核心修正：区分 confirmed_regime（已确认体制）和 regime（当期计算值）
    # 解决 "滞胀→类滞胀(pending)→类滞胀" 被误判为"切换取消"的bug

    import glob

    prev_confirmed_regime = None   # 上一期已确认的体制
    prev_pending_regime = None     # 上一期待确认的新体制
    prev_status = "confirmed"

    # 查找上一观察周(不同ISO周)的评分卡;同周文件视为回声,不参与"连续两周"判定
    existing = sorted(glob.glob(os.path.join(data_dir, 'scorecard_*.json')))
    prev_files = [f for f in existing if not f.endswith(f'scorecard_{today}.json')]
    prev_file = _prev_distinct_week_file(prev_files, today)

    if prev_file:
        try:
            with open(prev_file, 'r', encoding='utf-8') as f:
                prev_data = json.load(f)
            prev_confirmed_regime = prev_data.get('confirmed_regime', prev_data.get('regime'))
            prev_pending_regime = prev_data.get('pending_regime')
            prev_status = prev_data.get('regime_status', 'confirmed')
            print(f"📋 上观察周({os.path.basename(prev_file)[-13:-5]}): 已确认={prev_confirmed_regime}"
                  + (f", 待确认={prev_pending_regime}" if prev_status == 'pending_confirmation' else ""))
        except Exception as e:
            print(f"⚠️ 读取上期评分卡失败: {e}")
    else:
        print("📋 无上周评分卡(同周回声文件已忽略),按首次运行处理")

    # 切换判断(纯函数,规则见 resolve_transition 文档)
    confirmed_regime, regime_status, max_confidence = resolve_transition(
        prev_confirmed_regime, prev_pending_regime, prev_status, regime)

    if not prev_file or not prev_confirmed_regime:
        print(f"🆕 首次评分: {regime}")
    elif regime_status == 'confirmed' and regime != prev_confirmed_regime:
        print(f"✅ 体制切换确认: {prev_confirmed_regime} → {regime} (两个不同观察周一致)")
    elif regime_status == 'confirmed' and prev_status == 'pending_confirmation':
        print(f"↩️ 体制切换取消: 回归 {prev_confirmed_regime} (待确认体制未获跨周验证)")
    elif regime_status == 'pending_confirmation':
        print(f"⏳ 体制切换待确认: {prev_confirmed_regime} → {regime} (确信度上限3★,需下一观察周验证)")
    else:
        print(f"📌 体制维持: {regime}")

    # 构建结果
    # 体制归因(P1): 反事实分解,标注哪些指标是当前体制的关键驱动
    drivers, counterfactuals = attribute_regime(g_scores, g_total, i_scores, i_total)

    result = {
        'date': today,
        'growth_scores': g_scores,
        'growth_total': g_total,
        'inflation_scores': i_scores,
        'inflation_total': i_total,
        'regime': regime,                        # 当期计算值
        'confirmed_regime': confirmed_regime,    # 已确认体制（对外输出用这个）
        'regime_status': regime_status,
        'regime_description': desc,
        'max_confidence': max_confidence,
        'pending_regime': regime if regime_status == 'pending_confirmation' else None,
        'regime_drivers': drivers,               # P1: 关键驱动指标(剔除后体制翻转)
        'regime_counterfactuals': counterfactuals,  # P1: 全部"剔除单指标"反事实结果
        'regime_switch_rule': '体制切换需连续两周数据支持。首次出现切换信号时标记为待确认(max 3★)，已确认体制保持不变，连续两周一致后正式切换。'
    }

    # JSON 保存
    json_path = os.path.join(data_dir, f'scorecard_{today}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"💾 JSON: {json_path} ({os.path.getsize(json_path)} bytes)")

    # Markdown 保存
    pending_note = f"\n> ⏳ 本期评分卡计算结果为 [{regime}]，与已确认体制 [{confirmed_regime}] 不同，进入待确认期。需下周继续指向 [{regime}] 才能正式切换。\n" if regime_status == 'pending_confirmation' else ""
    status_label = "✅ 已确认" if regime_status == "confirmed" else "⏳ 待确认中"
    confidence_note = f"(确信度上限: {max_confidence}★)" if max_confidence < 5 else ""

    md = f"""# 宏观体制评分卡 ({today})

## 当前体制: {confirmed_regime} {status_label} {confidence_note}
{desc}
{pending_note}

### 切换规则
{result['regime_switch_rule']}

### 体制归因（反事实分解：剔除单指标后体制是否翻转）
"""
    if drivers:
        for d in drivers:
            md += f"- {d}\n"
    else:
        md += "- 无单一指标足以单独决定当前体制（体制由多指标共同支撑，稳健性较高）\n"
    md += "\n"

    md += f"""
## 增长维度 (总分: {g_total})
| 指标 | 当前值 | 变化 | 评分 | 阈值说明 |
|------|--------|------|------|----------|
"""
    for s in g_scores.values():
        md += f"| {s['name']} | {s.get('value','N/A')} | {s.get('change','N/A')} | {s['score']:+d} | {s.get('thresholds','')} |\n"

    md += f"""
## 通胀维度 (总分: {i_total})
| 指标 | 当前值 | 变化 | 评分 | 阈值说明 |
|------|--------|------|------|----------|
"""
    for s in i_scores.values():
        md += f"| {s['name']} | {s.get('value','N/A')} | {s.get('change','N/A')} | {s['score']:+d} | {s.get('threshold','')} |\n"

    if prev_confirmed_regime and regime != confirmed_regime:
        md += f"""
## 体制切换记录
- 已确认体制: {confirmed_regime}
- 本期计算: {regime}
- 切换状态: {status_label}
- 说明: 首次切换信号需连续两周验证，确信度上限{max_confidence}★
"""

    md_path = os.path.join(data_dir, f'scorecard_{today}.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"📄 MD: {md_path} ({os.path.getsize(md_path)} bytes)")

    # 控制台摘要
    print(f"\n{'='*50}")
    print(f"📊 宏观体制评分卡 v2.0")
    print(f"{'='*50}")
    print(f"增长总分: {g_total:+d}  |  通胀总分: {i_total:+d}")
    print(f"当期计算: {regime}")
    print(f"已确认体制: {confirmed_regime} ({status_label})")
    if drivers:
        print(f"关键驱动: {'; '.join(drivers)}")
    if regime_status == 'pending_confirmation':
        print(f"⏳ 待确认体制: {regime} (需下周验证)")
    if max_confidence < 5:
        print(f"⚠️  确信度上限: {max_confidence}★ (待确认期间)")
    print(f"{'='*50}")

if __name__ == '__main__':
    print("=" * 60)
    print("📊 宏观体制评分卡 v2.0")
    print("=" * 60)

    growth_scores, growth_total = score_growth()
    inflation_scores, inflation_total = score_inflation()
    regime, desc = determine_regime(growth_total, inflation_total)

    save_scorecard(growth_scores, growth_total, inflation_scores, inflation_total, regime, desc)

    print("\n✅ 评分卡生成完成!")
