#!/usr/bin/env python3
"""P4回归测试(2026-10-11) — 月报/季报触发与数据装配
运行: ~/AI内容/venv/bin/python3 tests/test_p4_fixes.py
"""
import os
import sys
from datetime import datetime

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


print("=" * 60)
print("P4回归测试: 月报/季报")
print("=" * 60)

# ── 测试1: 触发条件判定 ──────────────────
print("\n[1] is_last_friday_of_month/quarter")
from report_generator import is_last_friday_of_month, is_last_friday_of_quarter

def d(y, m, dd):
    return datetime(y, m, dd)

# 2026年10月: 周五=2,9,16,23,30
check("10-30(月末最后周五)→True", is_last_friday_of_month(d(2026, 10, 30)) is True)
check("10-16(月中周五)→False", is_last_friday_of_month(d(2026, 10, 16)) is False)
check("10-31(周六)→False", is_last_friday_of_month(d(2026, 10, 31)) is False)
check("12-25(2026季末最后周五)→True月报", is_last_friday_of_month(d(2026, 12, 25)) is True)
check("12-25→季报True", is_last_friday_of_quarter(d(2026, 12, 25)) is True)
check("10-30(非季末月)→季报False", is_last_friday_of_quarter(d(2026, 10, 30)) is False)
check("09-25(2026季末月最后周五)→季报True", is_last_friday_of_quarter(d(2026, 9, 25)) is True)
check("08-28(8月最后周五)→季报False", is_last_friday_of_quarter(d(2026, 8, 28)) is False)

# ── 测试2: 月度数据装配(真实数据) ──────────────────
print("\n[2] monthly_review.build_data_block")
import monthly_review as mr

ym = datetime.now().strftime('%Y%m')
block, series, ctx = mr.build_data_block(ym)
check("提取到≥5个月度序列", len(series) >= 5, f"got {len(series)}: {list(series)}")
if series:
    sample = next(iter(series.values()))
    check("序列含月初/月末/高低", all(k in sample for k in ('first', 'last', 'min', 'max')))
else:
    check("序列含月初/月末/高低", False, "无序列")
check("月变化百分比计算", any(s.get('chg_pct') is not None for s in series.values()))
check("评分卡时间线非空", len(ctx['scorecard_timeline']) >= 1)
check("周报索引含10月期", any('2026' in w for w in ctx['weekly_reports']))
check("数据块含表格头", "月变化%" in block and "体制评分卡时间线" in block)

spx = series.get('SPX标普500')
if spx:
    check(f"SPX月区间合理({spx['first']}→{spx['last']})", 5000 < spx['last'] < 15000)
else:
    check("SPX序列存在", False, "SPX标普500缺失")

# ── 测试3: 季度数据装配(真实数据) ──────────────────
print("\n[3] quarterly_outlook.build_data_block")
import quarterly_outlook as qo

months = qo.quarter_months()
check("Q4月份列表", months == ['202610', '202611', '202612'], str(months))
check("Q4季度编号", (int(months[0][4:6]) - 1) // 3 + 1 == 4)
qblock = qo.build_data_block()
check("季报数据块含各月体制快照", "体制快照" in qblock and "202610" in qblock)
check("季报数据块含各月末资产水平表", "各月末关键资产水平" in qblock)
check("季报数据块含评级轨迹", "配置观点评级轨迹" in qblock)
check("季报数据块含预测命中统计", "预测命中统计" in qblock)

# ── 测试4: 提示词与接线 ──────────────────
print("\n[4] 提示词与report_generator接线")
from report_generator import load_prompt
mp = load_prompt('monthly_review_prompt.md')
qp = load_prompt('quarterly_outlook_prompt.md')
check("月报提示词含回溯纪律", "月度复盘" in mp and "不得只复制周报" in mp)
check("季报提示词含战略层定位", "季度展望" in qp and "战略" in qp)

rg = open(os.path.join(ROOT, 'scripts', 'report_generator.py')).read()
check("周报主流程挂月报钩子", "monthly_review.py" in rg and "is_last_friday_of_month()" in rg)
check("周报主流程挂季报钩子", "quarterly_outlook.py" in rg and "is_last_friday_of_quarter()" in rg)
check("附加报告失败不影响周报", "周报不受影响" in rg)

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
