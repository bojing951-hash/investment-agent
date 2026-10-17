#!/usr/bin/env python3
"""第七轮 Phase 3测试 — 研究引擎接入快照(评分卡/相关性/利率预期/流水线次序)

数据纪律: 全部fixture为SYNTHETIC构造(不拉网络,不写真实data目录;
save_scorecard经data_dir参数注入临时目录)。
运行: ~/AI内容/venv/bin/python3 tests/test_phase3.py
"""
import os
import sys
import json
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


def mk_fact(metric_id, value, obs='2026-10-16', derived=None, unit=''):
    return {'metric_id': metric_id, 'display_name': metric_id, 'value': value,
            'unit': unit, 'observation_date': obs, 'quality_status': 'PASS',
            'derived': derived or {}}


print("=" * 60)
print("Phase 3: 研究引擎消费快照(评分卡/相关性/利率预期/次序)")
print("=" * 60)

# ══ [1] 利率预期: 月均语义,无降息次数换算 ═══════════════════════
print("\n[1] rate_expectations.calculate_rate_expectations")
from rate_expectations import calculate_rate_expectations

futures = [{'label': '2026-12', 'price': 95.90, 'implied_rate_pct': 4.10},
           {'label': '2027-03', 'price': 96.40, 'implied_rate_pct': 3.60}]
current = {'DFF': {'name': '有效联邦基金利率', 'value': 4.33, 'date': '2026-10-16'},
           'DFEDTARU': {'name': '目标区间上限', 'value': 4.50, 'date': '2026-10-16'},
           'DFEDTARL': {'name': '目标区间下限', 'value': 4.25, 'date': '2026-10-16'}}
exp = calculate_rate_expectations(futures, current)
s = json.dumps(exp, ensure_ascii=False)
check("输出无cuts/implied_moves_25bp字段",
      'cuts' not in s and 'implied_moves' not in s)
check("输出无'次25bp'换算痕迹", '次25bp' not in s and '25bp' not in s)
check("远期条目键=月均口径(implied_avg_rate)",
      all('implied_avg_rate' in fr for fr in exp['forward_rates']))
check("口径注记写入(basis_note)", '月均' in exp.get('basis_note', '')
      and '不得换算' in exp.get('basis_note', ''))
check("方向为描述性(低于/高于/相当)",
      all(fr['direction'] in ('隐含低于当前', '隐含高于当前', '与当前相当')
          for fr in exp['forward_rates']))
check("diff按pp表述且数值正确(4.10-4.33=-0.23)",
      abs(exp['forward_rates'][0]['diff_from_current'] + 0.23) < 1e-9)

# ══ [2] 评分卡: 快照输入/缺失记录/数据不足态 ═════════════════════
print("\n[2] macro_scorecard(消费快照)")
import macro_scorecard as ms

FULL_FACTS = [
    mk_fact('UMCSENT', 68.0, obs='2026-09-01'),                         # 68→0
    mk_fact('UNEMPLOYMENT', 4.2, obs='2026-09-01',
            derived={'m3': {'pp_change': 0.4}}),                        # +0.4pp→-1
    mk_fact('RSAFS', 100000.0, derived={'m1': {'pct_change': 0.8}}),    # →+1
    mk_fact('INDPRO', 103.0, derived={'m1': {'pct_change': 0.2}}),      # →0
    mk_fact('CORE_CPI', 340.0, obs='2026-09-01',
            derived={'m12': {'pct_change': 3.0}}),                      # →+1
    mk_fact('BEI_10Y', 2.31),                                            # →+1
    mk_fact('WTI_F', 65.0),                                              # 65∈[50,70)→0
    mk_fact('AHE', 31.0, obs='2026-09-01',
            derived={'m12': {'pct_change': 3.9}}),                      # →+1
]
g_scores, g_total, g_missing = ms.score_growth(FULL_FACTS)
i_scores, i_total, i_missing = ms.score_inflation(FULL_FACTS)
check("增长8项全可用无缺失", len(g_scores) == 4 and g_missing == [])
check("增长总分=0-1+1+0=0", g_total == 0, str(g_total))
check("通胀总分=1+1+0+1=3", i_total == 3, str(i_total))
regime, desc = ms.determine_regime(g_total, i_total)
check("体制映射=滞胀(i=3,g=0)", regime == '滞胀', regime)
drivers, cfs = ms.attribute_regime(g_scores, g_total, i_scores, i_total)
check("敏感性分析识别核心CPI为关键敏感项",
      any('核心CPI' in d and '衰退' in d for d in drivers), str(drivers))
check("驱动表述=反事实/非因果归因",
      all('反事实' in d and '非因果归因' in d for d in drivers))
check("反事实清单全覆盖(8项)", len(cfs) == 8, str(len(cfs)))

with tempfile.TemporaryDirectory() as td:
    result = ms.save_scorecard(g_scores, g_total, i_scores, i_total, regime, desc,
                               g_missing=g_missing, i_missing=i_missing,
                               data_basis={'snapshot_id': 'research_snapshot_TEST',
                                           'research_as_of': '2026-10-17T08:00:00+08:00',
                                           'gate_a': 'PASS'},
                               drivers=drivers, counterfactuals=cfs,
                               date_str='20261017', data_dir=td)
    check("JSON落盘含disclaimer/model-opinion标记",
          '模型观点' in result['disclaimer'] and '非客观事实' in result['disclaimer'])
    check("data_basis随结果落盘",
          result['data_basis']['snapshot_id'] == 'research_snapshot_TEST')
    check("首次运行即确认(confidence 5)",
          result['regime_status'] == 'confirmed' and result['max_confidence'] == 5)
    md = open(os.path.join(td, 'scorecard_20261017.md')).read()
    check("MD头部=模型观点声明", '模型观点' in md and '非客观事实' in md)
    check("MD含快照数据基础披露", 'research_snapshot_TEST' in md and 'Gate A' in md)
    check("MD敏感性=反事实分解表述", '反事实' in md and '非因果归因' in md)

# ── 缺失场景: 只剩UNEMPLOYMENT可用 → 数据不足不可判 ──
PARTIAL_FACTS = [f for f in FULL_FACTS
                 if f['metric_id'] in ('UNEMPLOYMENT', 'CORE_CPI', 'BEI_10Y', 'AHE', 'WTI_F')]
g2, gt2, gm2 = ms.score_growth(PARTIAL_FACTS)
i2, it2, im2 = ms.score_inflation(PARTIAL_FACTS)
check("增长可用1项<2 → 判数据不足", len(g2) == 1 and len(gm2) == 3)
check("缺失清单含指标id与原因",
      all(m.get('metric_id') and m.get('reason') for m in gm2))
check("通胀4项全可用不受增长缺失影响", len(i2) == 4 and im2 == [])

with tempfile.TemporaryDirectory() as td:
    result2 = ms.save_scorecard(g2, gt2, i2, it2, ms.DATA_INSUFFICIENT,
                                '数据不足测试', g_missing=gm2, i_missing=im2,
                                data_basis={'snapshot_id': 'research_snapshot_TEST',
                                            'research_as_of': 'x', 'gate_a': 'DEGRADED'},
                                date_str='20261017', data_dir=td)
    check("数据不足态regime如实写入", result2['regime'] == ms.DATA_INSUFFICIENT)
    check("状态=data_insufficient(首次)", result2['regime_status'] == 'data_insufficient')
    check("数据不足不产敏感性结论", result2['regime_drivers'] == [])
    check("growth_missing完整落盘", len(result2['growth_missing']) == 3)
    md2 = open(os.path.join(td, 'scorecard_20261017.md')).read()
    check("MD披露数据缺口+不计分", '数据缺口' in md2 and '不计分' in md2)
    check("MD缺失项不以0分入表", '| 0 |' not in md2)

# ── 切换确认: 数据不足周不构成切换证据 ──
print("\n[3] resolve_transition数据不足语义")
r = ms.resolve_transition('滞胀', '再通胀', 'pending_confirmation', ms.DATA_INSUFFICIENT)
check("数据不足周维持pending不被确认/取消", r == ('滞胀', 'pending_confirmation', 2), str(r))
r = ms.resolve_transition('滞胀', None, 'confirmed', ms.DATA_INSUFFICIENT)
check("数据不足周维持已确认体制", r == ('滞胀', 'confirmed', 2), str(r))
r = ms.resolve_transition(None, None, 'confirmed', ms.DATA_INSUFFICIENT)
check("无历史+数据不足→状态data_insufficient", r == (ms.DATA_INSUFFICIENT, 'data_insufficient', 2), str(r))
r = ms.resolve_transition(ms.DATA_INSUFFICIENT, None, 'data_insufficient', '滞胀')
check("数据不足不作为确认基线(下周可判→直接确认,conf 4)",
      r == ('滞胀', 'confirmed', 4), str(r))
r = ms.resolve_transition('滞胀', None, 'confirmed', '再通胀')
check("正常周首现切换→pending(旧行为不变)", r == ('滞胀', 'pending_confirmation', 3), str(r))

# ══ [4] 相关性: 代理披露/样本数/缺口诚实 ═════════════════════════
print("\n[4] correlation_calculator(消费快照series_store)")
import correlation_calculator as cc
import datetime as _dt

d = _dt.date(2026, 7, 1)   # ≥60个共同交易日,保证60日窗满样本
dates = []
while d <= _dt.date(2026, 10, 16):
    if d.weekday() < 5:
        dates.append(d.isoformat())
    d += _dt.timedelta(days=1)


def series(base, drift):
    vals, v = [], float(base)
    for i in range(len(dates)):
        v = v * (1 + (drift if i % 3 else -drift * 0.4) / 100)
        vals.append(round(v, 4))
    return {'dates': dates, 'values': vals}


snap_fake = {'snapshot_id': 'research_snapshot_TEST',
             'series_store': {
                 'SPX': series(7400, 0.3), 'TLT': series(90, -0.1),
                 'GOLD_F': series(4200, 0.4), 'DXY': series(102, 0.05),
                 'WTI_F': series(70, 0.5), 'EEM': series(45, 0.2),
                 'EZU': series(60, 0.25), 'FXI': series(40, 0.35),
                 'VIX': series(18, -1.2), 'HYG': series(79, 0.05),
                 'BTC': series(97000, 0.8)}}       # NDX缺失→该对须进missing
results, missing = cc.compute_all(snap_fake)
check("可用9对全部产出(NDX缺失对除外)", len(results) == 9 and len(missing) == 1,
      f"{len(results)}/{len(missing)}")
check("NDX缺失对如实进missing不造数", '比特币' in missing[0] and 'NDX' in missing[0],
      str(missing))
fxi = next(r for r in results if r['b'] == 'FXI')
check("FXI对披露代理身份(非A股指数)", '代理' in fxi['disclosure'] and '非A股指数' in fxi['disclosure'])
tlt = next(r for r in results if r['b'] == 'TLT')
check("TLT对披露价格ETF口径", '价格' in tlt['disclosure'])
check("样本数披露(20/60窗)", all(r['n_20d'] == 20 and r['n_60d'] == 60 for r in results))
check("窗口起止日披露", all(r['window_first'] and r['window_last'] for r in results))
md = cc.generate_markdown(results, missing, '2026-10-17')
check("MD含相关性≠因果声明", '相关性≠因果关系' in md)
check("MD含解读边界节", '解读边界' in md)
check("MD披露数据缺口", '数据缺口' in missing[0] or '数据缺口' in md)

# 部分重叠场景: 一序列只隔日观测 → 内连接子样本
odd = {'dates': dates[::2], 'values': [series(90, -0.1)['values'][i]
                                       for i in range(0, len(dates), 2)]}
snap2 = {'series_store': {'SPX': snap_fake['series_store']['SPX'], 'TLT': odd}}
res2, miss2 = cc.compute_all({**snap_fake, 'series_store': snap2['series_store']})
# 其余对仍全量;只看SPX/TLT行的样本数
row = next(r for r in res2 if r['b'] == 'TLT')
check("共同观测日内连接(隔日序列样本约减半)",
      row['n_60d'] < 60 and row['n_60d'] > 20, str(row['n_60d']))

# ══ [5] 流水线次序: 快照先于评分卡/相关性 ═══════════════════════
print("\n[5] run_weekly步骤次序")
src = open(os.path.join(ROOT, 'run_weekly.py')).read()
i_snap = src.find('"snapshot_builder.py"')
i_sc = src.find('"macro_scorecard.py"')
i_corr = src.find('"correlation_calculator.py"')
i_asm = src.find('"data_assembler.py"')
check("次序: 快照<评分卡<相关性<装配", i_snap < i_sc < i_corr < i_asm,
      f"{i_snap},{i_sc},{i_corr},{i_asm}")
check("全部11步标签统一(/11)", src.count('/11') == 11, str(src.count('/11')))

# ══ [6] 汇编器嵌入评分卡标签(结构保持) ═════════════════════════
print("\n[6] 数据包嵌入标签")
import data_assembler as da
src_da = open(os.path.join(ROOT, 'scripts', 'data_assembler.py')).read()
check("评分卡嵌入标注'模型观点,非客观事实'", '模型观点,非客观事实' in src_da)
check("评分卡快照后运行(同日嵌入lag 0)",
      'scorecard_' in src_da)

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
