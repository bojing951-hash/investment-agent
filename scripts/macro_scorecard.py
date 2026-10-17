#!/usr/bin/env python3
"""
宏观体制评分卡 v2.0(Layer 4研究引擎,2026-10-17第七轮重构)

基于增长×通胀二维评分系统，量化判断当前宏观体制。

第七轮重构(spec §9 P1):
1. 数据入口=当日研究快照facts(不再自行fetch_fred/yfinance——Layer 4不直连Layer 1,
   指标身份/单位/口径由事实引擎统一,环比同比由引擎m1/m3/m12派生);
2. 缺失如实记录: 每维度输出missing清单,缺失项不计0分、不进总分(spec: missing≠0);
3. 数据不足态: 任一维度可用指标<2 → regime='数据不足不可判',不给体制结论,
   切换确认机制保持上期状态不受数据不足周污染;
4. attribute_regime输出表述为"敏感性分析(反事实分解)"——回答"剔除哪个指标后
   体制映射翻转",不回答"什么导致了通胀/增长"(非经济因果归因);
5. 输出明示: 评分卡=内部模型观点(阈值即模型假设),非客观事实;
   快照data_basis(research_as_of/Gate A)随结果落盘。

保留(结构不变): 阈值与评分档位、体制映射v2.0、两周独立确认规则(ISO周回声剔除)。
"""

import os
import sys
import json
import glob
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

DATA_INSUFFICIENT = "数据不足不可判"
MIN_AVAILABLE_PER_DIM = 2          # 每维度至少2个可用指标才给体制结论
DISCLAIMER = ("评分卡=内部模型观点(阈值为模型假设),非客观事实;"
              "体制结论为二维映射的机械输出,须结合证据分级使用")

# ══════════════════════════════════════════════════════════════════
# 快照接入(Layer 3 → Layer 4唯一数据入口)
# ══════════════════════════════════════════════════════════════════

def load_snapshot(date_str=None, data_dir=None):
    """读取当日研究快照;缺失则退出(缺数据不得喂结论)。"""
    ymd = date_str or datetime.now().strftime('%Y%m%d')
    d = data_dir or os.path.join(ROOT_DIR, 'data', 'daily')
    path = os.path.join(d, f"research_snapshot_{ymd}.json")
    if not os.path.exists(path):
        print(f"❌ 无当日研究快照: {path}(先跑snapshot_builder)")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def fact_of(facts, metric_id):
    for f in facts:
        if isinstance(f, dict) and f.get('metric_id') == metric_id:
            return f
    return None


def _level(fact):
    """水平值输入(如消费者信心/BEI/WTI)。"""
    if not fact:
        return None, None, "快照无该指标事实"
    v = fact.get('value')
    if not isinstance(v, (int, float)):
        return None, None, "事实无有效数值"
    return float(v), fact.get('observation_date'), None


def _derived(fact, period, field):
    """派生变化输入(引擎统一口径: m1/m3/m12;field按单位取pct/pp/abs)。"""
    if not fact:
        return None, None, "快照无该指标事实"
    d = (fact.get('derived') or {}).get(period) or {}
    if d.get('available') is False:
        return None, None, f"引擎判数据不足({d.get('reason', '历史序列不够')})"
    v = d.get(field)
    if not isinstance(v, (int, float)):
        return None, None, f"引擎无{period}期{field}派生"
    return float(v), fact.get('observation_date'), None


def _take(facts, metric_id, extractor):
    """取数三步: 找事实→抽值;失败返回(值,日期,None原因)供missing清单。"""
    return extractor(fact_of(facts, metric_id))


# ══════════════════════════════════════════════════════════════════
# 评分(阈值与档位=v1原样保留;仅数据来源改为快照)
# ══════════════════════════════════════════════════════════════════

def score_growth(facts):
    """增长维度评分: 输入=快照facts;返回(得分表, 总分, 缺失清单)。"""
    print("\n📊 增长维度评分(输入=研究快照)...")
    scores, missing = {}, []

    # 1. 消费者信心 (UMCSENT, 月频水平)
    v, date, why = _take(facts, 'UMCSENT', _level)
    if why is None:
        if v < 50: s = -2
        elif v < 60: s = -1
        elif v < 80: s = 0
        elif v < 95: s = 1
        else: s = 2
        scores['consumer_confidence'] = {
            'name': '消费者信心(密歇根)', 'value': v, 'date': date, 'score': s,
            'thresholds': '收缩<60 | 扩张>80',
            'distance_to_switch': f"距收缩线: {round(v-60,1)}" if v >= 60 else f"已低于收缩线 {round(60-v,1)}"
        }
        print(f"  ✅ 消费者信心: {v} → 评分 {s:+d}")
    else:
        missing.append({'key': 'consumer_confidence', 'metric_id': 'UMCSENT',
                        'name': '消费者信心(密歇根)', 'reason': why})
        print(f"  ⚠️ 消费者信心缺失: {why}")

    # 2. 失业率3个月变化 (UNEMPLOYMENT, 引擎m3 pp口径)
    v, date, why = _take(facts, 'UNEMPLOYMENT', lambda f: _derived(f, 'm3', 'pp_change'))
    if why is None:
        change = v
        if change > 0.5: s = -2
        elif change > 0.3: s = -1
        elif change > -0.1: s = 0
        elif change > -0.3: s = 1
        else: s = 2
        scores['unemployment_change'] = {
            'name': '失业率3月变化', 'value': change, 'date': date, 'score': s,
            'unit': '百分点',
            'thresholds': '恶化>+0.3 | 改善<0',
            'distance_to_switch': f"距恶化线: {round(0.3-change,2)}pp" if change <= 0.3 else f"已超恶化线 {round(change-0.3,2)}pp"
        }
        print(f"  ✅ 失业率3m变化: {change:+.2f}pp → 评分 {s:+d}")
    else:
        missing.append({'key': 'unemployment_change', 'metric_id': 'UNEMPLOYMENT',
                        'name': '失业率3月变化', 'reason': why})
        print(f"  ⚠️ 失业率3m变化缺失: {why}")

    # 3. 零售销售环比 (RSAFS, 引擎m1 pct口径)
    v, date, why = _take(facts, 'RSAFS', lambda f: _derived(f, 'm1', 'pct_change'))
    if why is None:
        mom = v
        if mom < -1: s = -2
        elif mom < -0.5: s = -1
        elif mom < 0.5: s = 0
        elif mom < 1: s = 1
        else: s = 2
        scores['retail_sales_mom'] = {
            'name': '零售销售环比', 'value': mom, 'date': date, 'score': s,
            'unit': '%', 'thresholds': '收缩<-0.5% | 扩张>+0.5%'
        }
        print(f"  ✅ 零售销售MoM: {mom:+.2f}% → 评分 {s:+d}")
    else:
        missing.append({'key': 'retail_sales_mom', 'metric_id': 'RSAFS',
                        'name': '零售销售环比', 'reason': why})
        print(f"  ⚠️ 零售销售环比缺失: {why}")

    # 4. 工业生产环比 (INDPRO, 引擎m1 pct口径)
    v, date, why = _take(facts, 'INDPRO', lambda f: _derived(f, 'm1', 'pct_change'))
    if why is None:
        mom = v
        if mom < -1: s = -2
        elif mom < -0.3: s = -1
        elif mom < 0.3: s = 0
        elif mom < 1: s = 1
        else: s = 2
        scores['industrial_production'] = {
            'name': '工业生产环比', 'value': mom, 'date': date, 'score': s,
            'unit': '%', 'thresholds': '收缩<-0.3% | 扩张>+0.3%'
        }
        print(f"  ✅ 工业生产MoM: {mom:+.2f}% → 评分 {s:+d}")
    else:
        missing.append({'key': 'industrial_production', 'metric_id': 'INDPRO',
                        'name': '工业生产环比', 'reason': why})
        print(f"  ⚠️ 工业生产环比缺失: {why}")

    total = sum(item['score'] for item in scores.values())
    print(f"\n  📌 增长总分: {total:+d}(可用{len(scores)}项/缺失{len(missing)}项)")
    return scores, total, missing


def score_inflation(facts):
    """通胀维度评分: 输入=快照facts;返回(得分表, 总分, 缺失清单)。"""
    print("\n📊 通胀维度评分(输入=研究快照)...")
    scores, missing = {}, []

    # 1. 核心CPI同比 (CORE_CPI, 引擎m12 pct口径)
    v, date, why = _take(facts, 'CORE_CPI', lambda f: _derived(f, 'm12', 'pct_change'))
    if why is None:
        yoy = v
        if yoy < 1: s = -2
        elif yoy < 2: s = -1
        elif yoy < 2.5: s = 0
        elif yoy < 3.5: s = 1
        else: s = 2
        scores['core_cpi_yoy'] = {
            'name': '核心CPI同比', 'value': yoy, 'date': date, 'score': s,
            'unit': '%', 'thresholds': '通缩<2% | 高通胀>3.5%',
            'distance_to_switch': f"距高通胀线: {round(3.5-yoy,2)}%" if yoy <= 3.5 else f"已超高通胀线 {round(yoy-3.5,2)}%"
        }
        print(f"  ✅ 核心CPI YoY: {yoy:.2f}% → 评分 {s:+d}")
    else:
        missing.append({'key': 'core_cpi_yoy', 'metric_id': 'CORE_CPI',
                        'name': '核心CPI同比', 'reason': why})
        print(f"  ⚠️ 核心CPI同比缺失: {why}")

    # 2. BEI 10Y (T10YIE, 日频水平)
    v, date, why = _take(facts, 'BEI_10Y', _level)
    if why is None:
        if v < 1.5: s = -2
        elif v < 2: s = -1
        elif v < 2.3: s = 0
        elif v < 2.6: s = 1
        else: s = 2
        scores['bei_10y'] = {
            'name': 'BEI 10Y(通胀预期)', 'value': v, 'date': date, 'score': s,
            'unit': '%', 'thresholds': '低通胀<2% | 高通胀>2.5%',
            'distance_to_switch': f"距高通胀线: {round(2.6-v,2)}%" if v <= 2.6 else "已超高通胀线"
        }
        print(f"  ✅ BEI 10Y: {v:.2f}% → 评分 {s:+d}")
    else:
        missing.append({'key': 'bei_10y', 'metric_id': 'BEI_10Y',
                        'name': 'BEI 10Y(通胀预期)', 'reason': why})
        print(f"  ⚠️ BEI 10Y缺失: {why}")

    # 3. WTI油价 (WTI_F期货, 快照事实;不再自行yfinance)
    v, date, why = _take(facts, 'WTI_F', _level)
    if why is None:
        if v < 40: s = -2
        elif v < 50: s = -1
        elif v < 70: s = 0
        elif v < 90: s = 1
        else: s = 2
        scores['wti_oil'] = {
            'name': 'WTI油价(期货)', 'value': round(v, 2), 'date': date, 'score': s,
            'unit': '美元/桶', 'thresholds': '需求担忧<50 | 通胀推升>90',
            'note': '期货主力口径,与EIA现货月均为两个指标'
        }
        print(f"  ✅ WTI油价(期货): ${v:.2f} → 评分 {s:+d}")
    else:
        missing.append({'key': 'wti_oil', 'metric_id': 'WTI_F',
                        'name': 'WTI油价(期货)', 'reason': why})
        print(f"  ⚠️ WTI油价缺失: {why}")

    # 4. 平均时薪同比 (AHE, 引擎m12 pct口径)
    v, date, why = _take(facts, 'AHE', lambda f: _derived(f, 'm12', 'pct_change'))
    if why is None:
        yoy = v
        if yoy < 2: s = -2
        elif yoy < 3: s = -1
        elif yoy < 3.5: s = 0
        elif yoy < 4.5: s = 1
        else: s = 2
        scores['ahe_yoy'] = {
            'name': '平均时薪同比', 'value': yoy, 'date': date, 'score': s,
            'unit': '%', 'thresholds': '低工资<3% | 高工资>4.5%'
        }
        print(f"  ✅ 平均时薪 YoY: {yoy:.2f}% → 评分 {s:+d}")
    else:
        missing.append({'key': 'ahe_yoy', 'metric_id': 'AHE',
                        'name': '平均时薪同比', 'reason': why})
        print(f"  ⚠️ 平均时薪同比缺失: {why}")

    total = sum(item['score'] for item in scores.values())
    print(f"\n  📌 通胀总分: {total:+d}(可用{len(scores)}项/缺失{len(missing)}项)")
    return scores, total, missing


# ══════════════════════════════════════════════════════════════════
# 体制映射与切换确认(逻辑=v1原样;新增数据不足态)
# ══════════════════════════════════════════════════════════════════

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

    第七轮新增: 数据不足周(current_regime=数据不足不可判)不构成任何切换证据——
    既不确认新体制也不取消待确认,上期状态原样延续,置信度降档为2。
    """
    if current_regime == DATA_INSUFFICIENT:
        if not prev_confirmed:
            return DATA_INSUFFICIENT, "data_insufficient", 2
        return prev_confirmed, prev_status, 2

    if not prev_confirmed or prev_confirmed == DATA_INSUFFICIENT:
        # 首次运行→直接确认;上期为数据不足态→不作为确认基线,
        # 本周可判即确认(置信度4:缺一周独立复现证据)
        return current_regime, "confirmed", 5 if not prev_confirmed else 4

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
    """敏感性分析(反事实分解;2026-10-11 P1引入,第七轮明确表述边界) —
    逐项剔除单个指标后重算体制映射,映射翻转的指标即"关键敏感项"。
    返回(驱动列表, 全部反事实列表)。

    表述边界: 本分解回答"哪个指标把总分推过映射线"(算术敏感性),
    **不**回答"什么导致了通胀/增长"(经济因果)。
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
                drivers.append(f"{s['name']}({s['score']:+d}): 反事实剔除后体制映射变为[{cf}] — 关键敏感项(算术敏感性,非因果归因)")
    return drivers, counterfactuals


# ══════════════════════════════════════════════════════════════════
# 落盘(JSON+MD;data_dir参数供离线fixture测试注入)
# ══════════════════════════════════════════════════════════════════

def save_scorecard(g_scores, g_total, i_scores, i_total, regime, desc,
                   g_missing=None, i_missing=None, data_basis=None,
                   drivers=None, counterfactuals=None, date_str=None,
                   data_dir=None):
    today = date_str or datetime.now().strftime('%Y%m%d')
    out_dir = data_dir or os.path.join(ROOT_DIR, 'data', 'daily')
    os.makedirs(out_dir, exist_ok=True)
    g_missing, i_missing = g_missing or [], i_missing or []
    drivers, counterfactuals = drivers or [], counterfactuals or []

    # === 切换确认机制 v2.0 ===
    prev_confirmed_regime = None   # 上一期已确认的体制
    prev_pending_regime = None     # 上一期待确认的新体制
    prev_status = "confirmed"

    # 查找上一观察周(不同ISO周)的评分卡;同周文件视为回声,不参与"连续两周"判定
    existing = sorted(glob.glob(os.path.join(out_dir, 'scorecard_*.json')))
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

    # 切换判断(纯函数,规则见 resolve_transition 文档;数据不足周不构成切换证据)
    confirmed_regime, regime_status, max_confidence = resolve_transition(
        prev_confirmed_regime, prev_pending_regime, prev_status, regime)

    pending_regime = regime if regime_status == 'pending_confirmation' else None

    result = {
        'date': today,
        'disclaimer': DISCLAIMER,
        'data_basis': data_basis or {},
        'growth_scores': g_scores,
        'growth_total': g_total,
        'growth_missing': g_missing,
        'inflation_scores': i_scores,
        'inflation_total': i_total,
        'inflation_missing': i_missing,
        'regime': regime,
        'regime_description': desc,
        'confirmed_regime': confirmed_regime,
        'regime_status': regime_status,
        'max_confidence': max_confidence,
        'pending_regime': pending_regime,
        'regime_drivers': drivers,
        'regime_counterfactuals': counterfactuals,
        'regime_switch_rule': '新体制须在两个不同ISO观察周被独立计算才确认;同周重复=回声;数据不足周不构成切换证据',
        'sensitivity_note': '敏感性分析=反事实分解(剔除单指标看映射是否翻转),算术敏感性而非经济因果归因',
    }

    json_path = os.path.join(out_dir, f'scorecard_{today}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n💾 JSON已保存: {json_path}")

    # ── Markdown ──
    md = render_markdown(result)
    md_path = os.path.join(out_dir, f'scorecard_{today}.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"💾 MD已保存: {md_path}")

    return result


def _score_rows(scores, missing):
    rows = []
    for key, s in scores.items():
        unit = s.get('unit', '')
        val = f"{s['value']}{unit}" if unit else f"{s['value']}"
        rows.append(f"| {s['name']} | {val} | {s.get('date', '')} | {s['score']:+d} | {s.get('thresholds', '')} |")
    for m in missing:
        rows.append(f"| {m['name']} | —(缺失) | — | 不计分 | 缺失不折算为0({m['reason']}) |")
    return rows


def render_markdown(result):
    g, i = result['growth_scores'], result['inflation_scores']
    gm, im = result['growth_missing'], result['inflation_missing']
    L = [f"# 宏观体制评分卡({result['date']})",
         "",
         f"> ⚠️ {result['disclaimer']}",
         f"> 数据基础: 研究快照 {result.get('data_basis', {}).get('snapshot_id', '?')}"
         f" | 研究截止 {result.get('data_basis', {}).get('research_as_of', '?')}"
         f" | Gate A {result.get('data_basis', {}).get('gate_a', '?')}",
         ""]

    L.append("## 增长维度")
    L.append("| 指标 | 最新值 | 观测日 | 评分 | 阈值 |")
    L.append("|---|---|---|---|---|")
    L.extend(_score_rows(g, gm))
    L.append(f"\n**增长总分: {result['growth_total']:+d}**(可用{len(g)}项,缺失{len(gm)}项不计分)")

    L.append("\n## 通胀维度")
    L.append("| 指标 | 最新值 | 观测日 | 评分 | 阈值 |")
    L.append("|---|---|---|---|---|")
    L.extend(_score_rows(i, im))
    L.append(f"\n**通胀总分: {result['inflation_total']:+d}**(可用{len(i)}项,缺失{len(im)}项不计分)")

    L.append("\n## 体制判断(二维映射输出)")
    if result['regime'] == DATA_INSUFFICIENT:
        all_missing = [m['name'] for m in gm] + [m['name'] for m in im]
        L.append(f"**{DATA_INSUFFICIENT}** — 可用指标不足{MIN_AVAILABLE_PER_DIM}项/维度,"
                 f"缺失: {'、'.join(all_missing) or '无'}。本周期不给体制结论,"
                 f"上期确认态不被数据不足周改变。")
    else:
        L.append(f"**{result['regime']}** — {result['regime_description']}")
    status_names = {'confirmed': '已确认', 'pending_confirmation': '待确认(须下周独立复现)',
                    'data_insufficient': '数据不足'}
    L.append(f"- 确认状态: {status_names.get(result['regime_status'], result['regime_status'])}"
             f"(置信度{result['max_confidence']}/5)")
    L.append(f"- 已确认体制: {result['confirmed_regime']}"
             + (f"; 待确认: {result['pending_regime']}" if result['pending_regime'] else ""))

    if result['regime_drivers']:
        L.append("\n## 敏感性分析(反事实分解,非因果归因)")
        L.append(f"> {result['sensitivity_note']}")
        for d in result['regime_drivers']:
            L.append(f"- {d}")

    if gm or im:
        L.append("\n## 数据缺口(如实披露;缺失项不计分不折0)")
        for m in gm + im:
            L.append(f"- [{m['metric_id']}] {m['name']}: {m['reason']}")

    return "\n".join(L) + "\n"


# ══════════════════════════════════════════════════════════════════

def main(date_str=None, data_dir=None):
    print("=" * 60)
    print("📊 宏观体制评分卡 v2.0(输入=研究快照)")
    print("=" * 60)

    snapshot = load_snapshot(date_str, data_dir)
    facts = snapshot.get('facts', [])
    data_basis = {
        'snapshot_id': snapshot.get('snapshot_id'),
        'research_as_of': snapshot.get('research_as_of'),
        'gate_a': (snapshot.get('gate_a') or {}).get('status'),
    }
    print(f"📌 数据基础: {data_basis['snapshot_id']}(Gate A: {data_basis['gate_a']})")

    g_scores, g_total, g_missing = score_growth(facts)
    i_scores, i_total, i_missing = score_inflation(facts)

    # 数据不足判定: 任一维度可用<2 → 不给体制结论(spec §9)
    if len(g_scores) < MIN_AVAILABLE_PER_DIM or len(i_scores) < MIN_AVAILABLE_PER_DIM:
        regime = DATA_INSUFFICIENT
        short_g = '、'.join(m['name'] for m in g_missing)
        short_i = '、'.join(m['name'] for m in i_missing)
        desc = (f"数据不足不可判: 增长可用{len(g_scores)}项(缺{short_g}),"
                f"通胀可用{len(i_scores)}项(缺{short_i})。"
                f"缺失指标不得以0分或插值冒充,本周不出体制结论。")
        drivers, counterfactuals = [], []
        print(f"\n⚠️ {regime}(增长可用{len(g_scores)}/通胀可用{len(i_scores)})")
    else:
        regime, desc = determine_regime(g_total, i_total)
        drivers, counterfactuals = attribute_regime(g_scores, g_total, i_scores, i_total)
        print(f"\n📌 当期体制映射: {regime}")

    result = save_scorecard(g_scores, g_total, i_scores, i_total, regime, desc,
                            g_missing=g_missing, i_missing=i_missing,
                            data_basis=data_basis, drivers=drivers,
                            counterfactuals=counterfactuals,
                            date_str=date_str, data_dir=data_dir)
    print(f"\n✅ 确认体制: {result['confirmed_regime']}(状态: {result['regime_status']})")
    return result


if __name__ == '__main__':
    main()
