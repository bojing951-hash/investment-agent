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

保留(结构不变): 阈值与评分档位语义、体制映射v2.0、两周独立确认规则(ISO周回声剔除);
阈值数值自 2026-11-14(架构整改T1)起改读 config/thresholds.json(金融席签字 v1.0),
硬编码常量整族退役,行为与退役前逐值等价(BEI 显示串低侧 1.5 真修除外,冲突#1)。
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

# IA-P1-WP-C(DP-3定值=形态①,P1_DESIGN L30): 维度函数economy参数化。
# 阈值表仅定义于US——非US经济体**不杜撰阈值**(spec §三(a-2): 缺失不以0占位),
# US专属指标逐项如实计缺失,total=None(无评分,区别于0分的"中性"误读),
# 维度可用<2 → 主流程判DATA_INSUFFICIENT,机制复用零新逻辑。
ECONOMY_NAMES = {'US': '美国', 'CN': '中国', 'JP': '日本', 'EA': '欧元区'}
ECONOMY_SCORECARD_PREFIX = 'economy_scorecard_'   # 非US存档前缀(避开US主评分卡glob)

# ══════════════════════════════════════════════════════════════════
# 阈值注册表接入(ARCH-REFORM T1/裁定书 S1 第1项, 2026-11-14)
# 硬编码阈值常量整族退役——if/elif 带边界、distance_to_switch 常量与 thresholds
# 显示串数值全部改读 config/thresholds.json(金融席签字 v1.0,69键)。该文件为
# 唯一阈值权威;本模块不再持有独立数值常量(G2 对账门差集双侧为空)。
# BEI 显示串低侧 1.5 误写 2(冲突#1 实锤)随本波真修——这是唯一的行为变更项。
# ══════════════════════════════════════════════════════════════════

THRESHOLDS_PATH = os.path.join(ROOT_DIR, 'config', 'thresholds.json')

# 本模块消费的注册表键全集(G2 门与代码双侧差集的代码侧锚;增删须同步注册表并重走金融席签字)。
# R41(T8-R2 遗留③,RDG-20261116-011): 平行枚举退役——维度成员键由
# research_contract/scorecard_spec 单源规格表推导(与 text_consistency
# 总分复算同源);本模块另消费 headline 显示键+体制映射键。
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from research_contract.scorecard_spec import (             # noqa: E402
    EXTRA_ENGINE_KEYS, REGIME_THRESHOLD_KEYS, threshold_keys as _spec_keys)
SCORECARD_THRESHOLD_KEYS = tuple(sorted(
    set(_spec_keys()) | set(REGIME_THRESHOLD_KEYS) | set(EXTRA_ENGINE_KEYS)))

_THRESH_CACHE = None


def load_thresholds(path=None):
    """加载签字阈值注册表(缺文件/缺键=fail-closed 明确报错,绝不静默回退硬编码)。"""
    global _THRESH_CACHE
    if path is None and _THRESH_CACHE is not None:
        return _THRESH_CACHE
    with open(path or THRESHOLDS_PATH, 'r', encoding='utf-8') as f:
        doc = json.load(f)
    th = {e['stable_key']: e['value'] for e in doc.get('entries', [])}
    missing = [k for k in SCORECARD_THRESHOLD_KEYS if k not in th]
    if missing:
        raise RuntimeError(f"config/thresholds.json 缺评分卡必需键: {missing}"
                           "(注册表与代码漂移,须对账门 G2 核并重走金融席签字)")
    if path is None:
        _THRESH_CACHE = th
    return th


def TH(key):
    """取签字阈值(唯一入口;测试可 load_thresholds(path=fixture) 后注入 _THRESH_CACHE)。"""
    if _THRESH_CACHE is None:
        load_thresholds()
    return _THRESH_CACHE[key]


def _g(v):
    """显示串数值格式(50.0→'50', -0.5→'-0.5')——与退役前手写字面量逐串等价。"""
    return f"{v:g}"

# ══════════════════════════════════════════════════════════════════
# 快照接入(Layer 3 → Layer 4唯一数据入口)
# ══════════════════════════════════════════════════════════════════

def load_snapshot(date_str=None, data_dir=None):
    """读取当日研究快照;缺失则退出(缺数据不得喂结论)。
    IA-P0-1: 改用research_provenance确定性版本选择——同日多版本取最高修订版
    (_vN),候选损坏明确拒绝;不再盲拼base文件名(旧实现修订版在场时仍读base)。"""
    import research_provenance as rp
    ymd = date_str or datetime.now().strftime('%Y%m%d')
    d = data_dir or os.path.join(ROOT_DIR, 'data', 'daily')
    snap, path_or_reason = rp.select_snapshot(ymd, d)
    if snap is None:
        print(f"❌ 当日研究快照不可用: {path_or_reason}(先跑snapshot_builder)")
        sys.exit(1)
    return snap


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

def score_growth(facts, economy='US'):
    """增长维度评分: 输入=快照facts;返回(得分表, 总分, 缺失清单)。
    IA-P1-WP-C(DP-3): economy参数化——economy='US'(默认)=原口径零回归;
    非US=阈值表无该经济体口径,4项US专属指标逐项如实计缺失,
    返回({}, None, missing)——total=None即"无评分"(禁0占位,spec §三(a-2))。"""
    print("\n📊 增长维度评分(输入=研究快照)...")
    scores, missing = {}, []
    if economy != 'US':
        for key, mid, name in (('consumer_confidence', 'UMCSENT', '消费者信心(密歇根)'),
                               ('unemployment_change', 'UNEMPLOYMENT', '失业率3月变化'),
                               ('retail_sales_mom', 'RSAFS', '零售销售环比'),
                               ('industrial_production', 'INDPRO', '工业生产环比')):
            missing.append({'key': key, 'metric_id': mid, 'name': name,
                            'reason': f'US专属指标({economy}经济体无该口径,阈值表未定义,如实计缺失)'})
            print(f"  ⚠️ {name}缺失: US专属指标({economy}不适用)")
        print(f"\n  📌 增长总分: 无(该经济体阈值口径未定义;可用0项/缺失{len(missing)}项,不以0占位)")
        return scores, None, missing

    # 1. 消费者信心 (UMCSENT, 月频水平;阈值=签字注册表 umcsent.scorecard.*)
    v, date, why = _take(facts, 'UMCSENT', _level)
    if why is None:
        if v < TH('umcsent.scorecard.m50'): s = -2
        elif v < TH('umcsent.scorecard.m60'): s = -1
        elif v < TH('umcsent.scorecard.p80'): s = 0
        elif v < TH('umcsent.scorecard.p95'): s = 1
        else: s = 2
        scores['consumer_confidence'] = {
            'name': '消费者信心(密歇根)', 'value': v, 'date': date, 'score': s,
            'thresholds': f"收缩<{_g(TH('umcsent.scorecard.m60'))} | 扩张>{_g(TH('umcsent.scorecard.p80'))}",
            'distance_to_switch': (f"距收缩线: {round(v-TH('umcsent.scorecard.m60'),1)}"
                                   if v >= TH('umcsent.scorecard.m60')
                                   else f"已低于收缩线 {round(TH('umcsent.scorecard.m60')-v,1)}")
        }
        print(f"  ✅ 消费者信心: {v} → 评分 {s:+d}")
    else:
        missing.append({'key': 'consumer_confidence', 'metric_id': 'UMCSENT',
                        'name': '消费者信心(密歇根)', 'reason': why})
        print(f"  ⚠️ 消费者信心缺失: {why}")

    # 2. 失业率3个月变化 (UNEMPLOYMENT, 引擎m3 pp口径;阈值=unemployment_3m.scorecard.*)
    # 带(+0.1,+0.3]=0 为代码既成口径(裁定#6 canonical,framework 已补行);显示串『改善<0』
    # 的 0=方向性描述非边界值(m03 键 semantic_note: 0 非边界值不入表)。
    v, date, why = _take(facts, 'UNEMPLOYMENT', lambda f: _derived(f, 'm3', 'pp_change'))
    if why is None:
        change = v
        if change > TH('unemployment_3m.scorecard.p05'): s = -2
        elif change > TH('unemployment_3m.scorecard.p03'): s = -1
        elif change > TH('unemployment_3m.scorecard.m01'): s = 0
        elif change > TH('unemployment_3m.scorecard.m03'): s = 1
        else: s = 2
        scores['unemployment_change'] = {
            'name': '失业率3月变化', 'value': change, 'date': date, 'score': s,
            'unit': '百分点',
            'thresholds': f"恶化>+{_g(TH('unemployment_3m.scorecard.p03'))} | 改善<0",
            'distance_to_switch': (f"距恶化线: {round(TH('unemployment_3m.scorecard.p03')-change,2)}pp"
                                   if change <= TH('unemployment_3m.scorecard.p03')
                                   else f"已超恶化线 {round(change-TH('unemployment_3m.scorecard.p03'),2)}pp")
        }
        print(f"  ✅ 失业率3m变化: {change:+.2f}pp → 评分 {s:+d}")
    else:
        missing.append({'key': 'unemployment_change', 'metric_id': 'UNEMPLOYMENT',
                        'name': '失业率3月变化', 'reason': why})
        print(f"  ⚠️ 失业率3m变化缺失: {why}")

    # 3. 零售销售环比 (RSAFS, 引擎m1 pct口径;阈值=rsafs_mom.scorecard.*)
    v, date, why = _take(facts, 'RSAFS', lambda f: _derived(f, 'm1', 'pct_change'))
    if why is None:
        mom = v
        if mom < TH('rsafs_mom.scorecard.m1'): s = -2
        elif mom < TH('rsafs_mom.scorecard.m05'): s = -1
        elif mom < TH('rsafs_mom.scorecard.p05'): s = 0
        elif mom < TH('rsafs_mom.scorecard.p1'): s = 1
        else: s = 2
        scores['retail_sales_mom'] = {
            'name': '零售销售环比', 'value': mom, 'date': date, 'score': s,
            'unit': '%',
            'thresholds': (f"收缩<{_g(TH('rsafs_mom.scorecard.m05'))}%"
                           f" | 扩张>+{_g(TH('rsafs_mom.scorecard.p05'))}%")
        }
        print(f"  ✅ 零售销售MoM: {mom:+.2f}% → 评分 {s:+d}")
    else:
        missing.append({'key': 'retail_sales_mom', 'metric_id': 'RSAFS',
                        'name': '零售销售环比', 'reason': why})
        print(f"  ⚠️ 零售销售环比缺失: {why}")

    # 4. 工业生产环比 (INDPRO, 引擎m1 pct口径;阈值=indpro_mom.scorecard.*,
    #    2026-11-14 起为 framework 增长表第四项——裁定#5 对齐 operative truth)
    v, date, why = _take(facts, 'INDPRO', lambda f: _derived(f, 'm1', 'pct_change'))
    if why is None:
        mom = v
        if mom < TH('indpro_mom.scorecard.m1'): s = -2
        elif mom < TH('indpro_mom.scorecard.m03'): s = -1
        elif mom < TH('indpro_mom.scorecard.p03'): s = 0
        elif mom < TH('indpro_mom.scorecard.p1'): s = 1
        else: s = 2
        scores['industrial_production'] = {
            'name': '工业生产环比', 'value': mom, 'date': date, 'score': s,
            'unit': '%',
            'thresholds': (f"收缩<{_g(TH('indpro_mom.scorecard.m03'))}%"
                           f" | 扩张>+{_g(TH('indpro_mom.scorecard.p03'))}%")
        }
        print(f"  ✅ 工业生产MoM: {mom:+.2f}% → 评分 {s:+d}")
    else:
        missing.append({'key': 'industrial_production', 'metric_id': 'INDPRO',
                        'name': '工业生产环比', 'reason': why})
        print(f"  ⚠️ 工业生产环比缺失: {why}")

    total = sum(item['score'] for item in scores.values())
    print(f"\n  📌 增长总分: {total:+d}(可用{len(scores)}项/缺失{len(missing)}项)")
    return scores, total, missing


def score_inflation(facts, economy='US'):
    """通胀维度评分: 输入=快照facts;返回(得分表, 总分, 缺失清单)。
    IA-P1-WP-C(DP-3): economy参数化,语义同score_growth。"""
    print("\n📊 通胀维度评分(输入=研究快照)...")
    scores, missing = {}, []
    if economy != 'US':
        for key, mid, name in (('core_cpi_yoy', 'CORE_CPI', '核心CPI同比'),
                               ('bei_10y', 'BEI_10Y', 'BEI 10Y(通胀预期)'),
                               ('wti_oil', 'WTI_F', 'WTI油价(期货)'),
                               ('ahe_yoy', 'AHE', '平均时薪同比')):
            missing.append({'key': key, 'metric_id': mid, 'name': name,
                            'reason': f'US专属指标({economy}经济体无该口径,阈值表未定义,如实计缺失)'})
            print(f"  ⚠️ {name}缺失: US专属指标({economy}不适用)")
        print(f"\n  📌 通胀总分: 无(该经济体阈值口径未定义;可用0项/缺失{len(missing)}项,不以0占位)")
        return scores, None, missing

    # 1. 核心CPI同比 (CORE_CPI, 引擎m12 pct口径;阈值=core_cpi.scorecard.*)
    v, date, why = _take(facts, 'CORE_CPI', lambda f: _derived(f, 'm12', 'pct_change'))
    if why is None:
        yoy = v
        if yoy < TH('core_cpi.scorecard.m1'): s = -2
        elif yoy < TH('core_cpi.scorecard.m2'): s = -1
        elif yoy < TH('core_cpi.scorecard.p25'): s = 0
        elif yoy < TH('core_cpi.scorecard.p35'): s = 1
        else: s = 2
        scores['core_cpi_yoy'] = {
            'name': '核心CPI同比', 'value': yoy, 'date': date, 'score': s,
            'unit': '%',
            'thresholds': (f"通缩<{_g(TH('core_cpi.scorecard.m2'))}%"
                           f" | 高通胀>{_g(TH('core_cpi.scorecard.p35'))}%"),
            'distance_to_switch': (f"距高通胀线: {round(TH('core_cpi.scorecard.p35')-yoy,2)}%"
                                   if yoy <= TH('core_cpi.scorecard.p35')
                                   else f"已超高通胀线 {round(yoy-TH('core_cpi.scorecard.p35'),2)}%")
        }
        print(f"  ✅ 核心CPI YoY: {yoy:.2f}% → 评分 {s:+d}")
    else:
        missing.append({'key': 'core_cpi_yoy', 'metric_id': 'CORE_CPI',
                        'name': '核心CPI同比', 'reason': why})
        print(f"  ⚠️ 核心CPI同比缺失: {why}")

    # 2. BEI 10Y (T10YIE, 日频水平;阈值=bei_10y.scorecard.* 四带缘+headline_high)
    # 裁定#1 双级并存: 显示串高通胀线=headline 2.5,评分/距离=band_edge 2.6;
    # 显示串低侧 1.5 原误写 2(冲突#1 实锤),本波真修=唯一行为变更项(TH 化后逐字对齐注册表)。
    v, date, why = _take(facts, 'BEI_10Y', _level)
    if why is None:
        if v < TH('bei_10y.scorecard.m15'): s = -2
        elif v < TH('bei_10y.scorecard.m2'): s = -1
        elif v < TH('bei_10y.scorecard.p23'): s = 0
        elif v < TH('bei_10y.scorecard.p26'): s = 1
        else: s = 2
        scores['bei_10y'] = {
            'name': 'BEI 10Y(通胀预期)', 'value': v, 'date': date, 'score': s,
            'unit': '%',
            'thresholds': (f"低通胀<{_g(TH('bei_10y.scorecard.m15'))}%"
                           f" | 高通胀>{_g(TH('bei_10y.headline_high'))}%"),
            'distance_to_switch': (f"距高通胀线: {round(TH('bei_10y.scorecard.p26')-v,2)}%"
                                   if v <= TH('bei_10y.scorecard.p26') else "已超高通胀线")
        }
        print(f"  ✅ BEI 10Y: {v:.2f}% → 评分 {s:+d}")
    else:
        missing.append({'key': 'bei_10y', 'metric_id': 'BEI_10Y',
                        'name': 'BEI 10Y(通胀预期)', 'reason': why})
        print(f"  ⚠️ BEI 10Y缺失: {why}")

    # 3. WTI油价 (WTI_F期货, 快照事实;阈值=wti_f.scorecard.* 评分带,与能源带 wti_f.energy.* 双体系并存)
    v, date, why = _take(facts, 'WTI_F', _level)
    if why is None:
        if v < TH('wti_f.scorecard.m40'): s = -2
        elif v < TH('wti_f.scorecard.m50'): s = -1
        elif v < TH('wti_f.scorecard.p70'): s = 0
        elif v < TH('wti_f.scorecard.p90'): s = 1
        else: s = 2
        scores['wti_oil'] = {
            'name': 'WTI油价(期货)', 'value': round(v, 2), 'date': date, 'score': s,
            'unit': '美元/桶',
            'thresholds': (f"需求担忧<{_g(TH('wti_f.scorecard.m50'))}"
                           f" | 通胀推升>{_g(TH('wti_f.scorecard.p90'))}"),
            'note': '期货主力口径,与EIA现货月均为两个指标'
        }
        print(f"  ✅ WTI油价(期货): ${v:.2f} → 评分 {s:+d}")
    else:
        missing.append({'key': 'wti_oil', 'metric_id': 'WTI_F',
                        'name': 'WTI油价(期货)', 'reason': why})
        print(f"  ⚠️ WTI油价缺失: {why}")

    # 4. 平均时薪同比 (AHE, 引擎m12 pct口径;阈值=ahe.scorecard.*,
    #    低工资头条线按评分列口径=m3(3.0),表头<2%由 m2 键承载——两键并存非冲突)
    v, date, why = _take(facts, 'AHE', lambda f: _derived(f, 'm12', 'pct_change'))
    if why is None:
        yoy = v
        if yoy < TH('ahe.scorecard.m2'): s = -2
        elif yoy < TH('ahe.scorecard.m3'): s = -1
        elif yoy < TH('ahe.scorecard.p35'): s = 0
        elif yoy < TH('ahe.scorecard.p45'): s = 1
        else: s = 2
        scores['ahe_yoy'] = {
            'name': '平均时薪同比', 'value': yoy, 'date': date, 'score': s,
            'unit': '%',
            'thresholds': (f"低工资<{_g(TH('ahe.scorecard.m3'))}%"
                           f" | 高工资>{_g(TH('ahe.scorecard.p45'))}%")
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
    阈值=签字注册表(2026-11-14 起): 滞胀族界=regime.inflation_total.stagflation_floor,
    增长正负界=regime.growth_total.zero(config/thresholds.json,原硬编码 3/0 退役)。
    """
    if i_total >= TH('regime.inflation_total.stagflation_floor'):
        if g_total > TH('regime.growth_total.zero'):
            regime = "类滞胀"
            desc = (f"增长勉强为正(+{g_total})但通胀压力主导(+{i_total})。"
                    f"通胀水平偏高且具粘性，不符合再通胀(Reflation)定义。"
                    f"本质上仍是滞胀倾向环境，增长端随时可能转负。")
        else:
            regime = "滞胀"
            desc = (f"增长疲软({g_total})叠加高通胀(+{i_total})。"
                    f"经典滞胀格局：央行无法放松，实体承压。")
    else:  # i_total <= 2(stagflation_floor 的整数域补集: ≤+2 ⇔ <3)
        if g_total > TH('regime.growth_total.zero'):
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
                   data_dir=None, economy='US'):
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
    # IA-P1-WP-C: 制度比较按经济体各自独立——US只与US主评分卡比,非US只与
    # 同经济体economy_scorecard_前缀档比(两命名族glob互不匹配,US路径零回归)
    if economy == 'US':
        prev_pattern, prev_today = 'scorecard_*.json', f'scorecard_{today}.json'
    else:
        prev_pattern = f'{ECONOMY_SCORECARD_PREFIX}{economy}_*.json'
        prev_today = f'{ECONOMY_SCORECARD_PREFIX}{economy}_{today}.json'
    existing = sorted(glob.glob(os.path.join(out_dir, prev_pattern)))
    prev_files = [f for f in existing if not f.endswith(prev_today)]
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

    # IA-P1-WP-C(DP-3): 非US才写入economy键——US输出19个legacy键零回归(§零.6-a4)
    if economy != 'US':
        result['economy'] = economy

    base = f'scorecard_{today}' if economy == 'US' \
        else f'{ECONOMY_SCORECARD_PREFIX}{economy}_{today}'
    json_path = os.path.join(out_dir, f'{base}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n💾 JSON已保存: {json_path}")

    # ── Markdown ──
    md = render_markdown(result)
    md_path = os.path.join(out_dir, f'{base}.md')
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
    econ = result.get('economy')   # IA-P1-WP-C: 非US存档带economy键→标题加经济体名前缀
    econ_name = f"{ECONOMY_NAMES.get(econ, econ)} " if econ else ''
    L = [f"# 宏观体制评分卡({econ_name}{result['date']})",
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
    if result['growth_total'] is None:   # IA-P1-WP-C: 非US无评分——如实"无",不以0占位
        L.append(f"\n**增长总分: —(该经济体阈值口径未定义,不计分不折0)**(可用{len(g)}项,缺失{len(gm)}项不计分)")
    else:
        L.append(f"\n**增长总分: {result['growth_total']:+d}**(可用{len(g)}项,缺失{len(gm)}项不计分)")

    L.append("\n## 通胀维度")
    L.append("| 指标 | 最新值 | 观测日 | 评分 | 阈值 |")
    L.append("|---|---|---|---|---|")
    L.extend(_score_rows(i, im))
    if result['inflation_total'] is None:
        L.append(f"\n**通胀总分: —(该经济体阈值口径未定义,不计分不折0)**(可用{len(i)}项,缺失{len(im)}项不计分)")
    else:
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

def main(date_str=None, data_dir=None, economy='US'):
    print("=" * 60)
    print("📊 宏观体制评分卡 v2.0(输入=研究快照)")
    print("=" * 60)
    if economy != 'US':
        print(f"🌍 经济体: {ECONOMY_NAMES.get(economy, economy)}({economy})"
              f"——阈值表仅定义于US,本卡如实记录指标缺席,不给维度评分")

    snapshot = load_snapshot(date_str, data_dir)
    facts = snapshot.get('facts', [])
    data_basis = {
        'snapshot_id': snapshot.get('snapshot_id'),
        'research_as_of': snapshot.get('research_as_of'),
        'gate_a': (snapshot.get('gate_a') or {}).get('status'),
    }
    print(f"📌 数据基础: {data_basis['snapshot_id']}(Gate A: {data_basis['gate_a']})")

    g_scores, g_total, g_missing = score_growth(facts, economy=economy)
    i_scores, i_total, i_missing = score_inflation(facts, economy=economy)

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
                            date_str=date_str, data_dir=data_dir, economy=economy)
    print(f"\n✅ 确认体制: {result['confirmed_regime']}(状态: {result['regime_status']})")
    return result


if __name__ == '__main__':
    main()
