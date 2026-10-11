#!/usr/bin/env python3
"""P4回归测试 v2(2026-10-11第二轮重构) — 月报/季报触发与数据装配
v2要点: 触发=期间结束后第一个周五(非"月末最后一个周五"); 未完结期间→【预览】;
bp/pp单位; 观测日去重; 覆盖披露; 整季聚合; 周期内预测统计。
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
print("P4回归测试v2: 月报/季报(期间结束后触发)")
print("=" * 60)

# ── 测试1: 触发条件判定(v2: 期间自然结束后第一个周五) ──────────────────
print("\n[1] pending_completed_month/quarter")
from report_generator import pending_completed_month, pending_completed_quarter

def d(y, m, dd):
    return datetime(y, m, dd)

# 2026年10月周五: 2,9,16,23,30
check("10-02(9月后第一个周五)→月报202609", pending_completed_month(d(2026, 10, 2)) == '202609')
check("10-02(Q3后第一个周五)→季报2026Q3", pending_completed_quarter(d(2026, 10, 2)) == '2026Q3')
check("10-09(第二周)→None(9月已复盘过)", pending_completed_month(d(2026, 10, 9)) is None)
check("10-30(10月未结束)→None(不再月末提前出报)", pending_completed_month(d(2026, 10, 30)) is None)
check("10-30→季报None", pending_completed_quarter(d(2026, 10, 30)) is None)
check("10-31(周六)→None", pending_completed_month(d(2026, 10, 31)) is None)
check("10-16(月中周五)→None", pending_completed_month(d(2026, 10, 16)) is None)
# 第二轮专项: 2026-12-25是12月最后一个周五,Q4还剩6天 → 不得提前生成Q4季报/12月月报
check("12-25(2026)月报→None(12月未完结)", pending_completed_month(d(2026, 12, 25)) is None)
check("12-25(2026)季报→None(Q4未完结,原缺陷提前出Q4季报)", pending_completed_quarter(d(2026, 12, 25)) is None)
check("2027-01-01→月报202612+季报2026Q4(期间后第一个周五)",
      pending_completed_month(d(2027, 1, 1)) == '202612'
      and pending_completed_quarter(d(2027, 1, 1)) == '2026Q4')
check("11-06→月报202610(10月已完结)", pending_completed_month(d(2026, 11, 6)) == '202610')
check("11-06→季报None(11月非季初月)", pending_completed_quarter(d(2026, 11, 6)) is None)

# ── 测试2: 月度数据装配(真实数据优先,缺失用E2E fixture,第二轮#20) ──────────────────
print("\n[2] monthly_review.build_data_block")
import glob as _glob
import monthly_review as mr

real = os.path.join(ROOT, 'data', 'daily')
fixdir = os.path.join(ROOT, 'tests', 'fixtures', 'e2e', 'w4_data')
data_dir = real if _glob.glob(os.path.join(real, 'global_2026*.json')) else fixdir
ym = '202609'
block, series, ctx, preview = mr.build_data_block(ym, data_dir=data_dir)
check("提取到≥5个月度序列", len(series) >= 5, f"got {len(series)}: {list(series)}")
if series:
    sample = next(iter(series.values()))
    check("序列含月初/月末/高低", all(k in sample for k in ('first', 'last', 'min', 'max')))
else:
    check("序列含月初/月末/高低", False, "无序列")
check("202609已完结→非预览", preview is False)
check("收益率/利差变化以bp报告", any(s['chg_str'].endswith('bp') for s in series.values()),
      str({k: v['chg_str'] for k, v in series.items()}))
check("价格变化以%报告", any(s['chg_str'].endswith('%') for s in series.values()))
check("数据块含覆盖披露节", "数据覆盖与缺口" in block)
check("数据块区分采集日/观测日", "采集日" in block and "观测日" in block)
check("预测统计按统计周期", "本月到期" in block and "本月裁决" in block)
check("正式报告不含【预览】", "【预览】" not in block)

# 当月(未完结) → 预览
ym_now = datetime.now().strftime('%Y%m')
block_now, _, _, preview_now = mr.build_data_block(ym_now, data_dir=data_dir)
check("当月未完结→预览模式", preview_now is True and "【预览】" in block_now)

# 月度序列观测日去重(fixture精确版见test_e2e;此处真实数据: 期内可含1-2个合法月度观测)
unrate = series.get('失业率UNRATE')
if unrate:
    check("月度序列观测数合法(按观测日去重,1-2个)", 1 <= unrate['obs_count'] <= 2, str(unrate))
else:
    check("月度序列存在(真实数据UNRATE亦应去重)", '失业率UNRATE' in series or data_dir == real)

# ── 测试3: 季度数据装配(整季聚合,非3时点) ──────────────────
print("\n[3] quarterly_outlook.build_data_block")
import quarterly_outlook as qo

months = qo.quarter_months('2026Q3')
check("Q3月份列表", months == ['202607', '202608', '202609'], str(months))
check("Q3已完结判定", qo.quarter_is_complete('2026Q3', __import__('datetime').date(2026, 10, 16)) is True)
check("Q4未完结判定", qo.quarter_is_complete('2026Q4', __import__('datetime').date(2026, 12, 25)) is False)
qblock, qpreview = qo.build_data_block('2026Q3', data_dir=data_dir)
check("Q3季报非预览", qpreview is False)
check("整季区间表(季初→季末/季内极值,非3时点)", "整季区间" in qblock and "季内最低" in qblock)
check("各月末水平表", "各月末水平" in qblock)
check("各月体制快照", "各月体制快照" in qblock and "202609" in qblock)
check("评级轨迹", "配置观点评级轨迹" in qblock)
check("周期内预测统计", "本季预测到期与裁决" in qblock)
q4block, q4preview = qo.build_data_block('2026Q4', data_dir=data_dir)
check("当季未完结→季报预览", q4preview is True and "【预览】" in q4block)

# ── 测试4: 提示词与接线 ──────────────────
print("\n[4] 提示词与report_generator接线")
from report_generator import load_prompt
mp = load_prompt('monthly_review_prompt.md')
qp = load_prompt('quarterly_outlook_prompt.md')
check("月报提示词含回溯纪律", "不得只复制周报" in mp)
check("月报提示词含单位纪律", "bp" in mp and "pp" in mp)
check("季报提示词含战略层定位", "季度展望" in qp and "战略" in qp)

rg = open(os.path.join(ROOT, 'scripts', 'report_generator.py')).read()
check("周报主流程挂月报钩子(期间结束后)", "monthly_review.py" in rg and "pending_completed_month()" in rg)
check("月报钩子显式传月份", "'--month', done_month" in rg)
check("周报主流程挂季报钩子(期间结束后)", "quarterly_outlook.py" in rg and "pending_completed_quarter()" in rg)
check("季报钩子显式传季度", "'--quarter', done_quarter" in rg)
check("旧'月末最后周五'触发已废除", "is_last_friday_of_month" not in rg and "is_last_friday_of_quarter" not in rg)
check("附加报告失败不影响周报", "周报不受影响" in rg)

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
