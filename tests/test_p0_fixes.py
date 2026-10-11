#!/usr/bin/env python3
"""P0修复回归测试(2026-10-11) — 纯Python assert,无需pytest
运行: ~/AI内容/venv/bin/python3 tests/test_p0_fixes.py
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


print("=" * 60)
print("P0修复回归测试")
print("=" * 60)

# ── 测试1: 体制切换跨周确认(缺陷六.4) ──────────────────
print("\n[1] macro_scorecard.resolve_transition")
from macro_scorecard import resolve_transition, _prev_distinct_week_file

# 首次运行
r = resolve_transition(None, None, "confirmed", "再通胀")
check("首次运行直接确认", r == ("再通胀", "confirmed", 5), str(r))

# 上周已确认滞胀,本周算出再通胀 → 待确认
r = resolve_transition("滞胀", None, "confirmed", "再通胀")
check("切换信号→待确认且维持旧体制", r == ("滞胀", "pending_confirmation", 3), str(r))

# 上周(不同ISO周)待确认再通胀,本周又算出再通胀 → 确认
r = resolve_transition("滞胀", "再通胀", "pending_confirmation", "再通胀")
check("跨周一致→确认切换", r == ("再通胀", "confirmed", 5), str(r))

# 上周待确认,本周回归旧体制 → 取消
r = resolve_transition("滞胀", "再通胀", "pending_confirmation", "滞胀")
check("回归旧体制→取消切换", r == ("滞胀", "confirmed", 5), str(r))

# 上周待确认A,本周算出第三种B → 重新待确认
r = resolve_transition("滞胀", "再通胀", "pending_confirmation", "衰退")
check("第三体制→重新待确认", r == ("滞胀", "pending_confirmation", 3), str(r))

print("\n[2] _prev_distinct_week_file(同周回声过滤)")
with tempfile.TemporaryDirectory() as td:
    # 模拟: 同一周内周一(Mon 2026-10-05)~周四文件 + 上周四(09-24)文件
    # 2026-10-08是周四,与10-05~10-07同ISO周;09-24是上一ISO周
    names = ["scorecard_20260917.json", "scorecard_20260924.json",
             "scorecard_20261005.json", "scorecard_20261006.json", "scorecard_20261007.json"]
    files = [os.path.join(td, n) for n in names]
    picked = _prev_distinct_week_file(files, "20261008")
    check("忽略同周文件,取上一ISO周", picked.endswith("scorecard_20260924.json"), str(picked))

    picked = _prev_distinct_week_file(files, "20261005")  # 周一:10-05自身已排除?此函数不排今天,但同周过滤兜底
    check("周一运行时取上周文件", picked.endswith("scorecard_20260924.json"), str(picked))

    # 全部同周(极端:系统刚上线连跑3天)
    same_week = [os.path.join(td, n) for n in ("scorecard_20261005.json", "scorecard_20261006.json")]
    check("只有同周文件→按无历史处理", _prev_distinct_week_file(same_week, "20261008") is None)


# ── 测试2: 论点回写门禁(缺陷六.7) ──────────────────
print("\n[3] report_generator._has_numeric_errors")
from report_generator import _has_numeric_errors

check("无警告→放行", _has_numeric_errors([]) is False)
check("样式警告→放行", _has_numeric_errors(["⚠️ A股口径: \"成交额12522亿\" — 必须标注口径"]) is False)
check("数值偏差→拦截", _has_numeric_errors(["❌ SPX收盘: 报告=7765.36, 锚点=7811.54 (偏差0.59% > 容差0.5%)"]) is True)
check("严重错误→拦截", _has_numeric_errors(["🚨 严重错误 VIX: 报告=15.41, 锚点=88.0 (偏差470% — 疑似指标混淆)"]) is True)
check("混合警告含数值错→拦截", _has_numeric_errors([
    "⚠️ A股口径: xx", "❌ 黄金价格: 报告=4165.3, 锚点=4216.3 (偏差1.21% > 容差)"]) is True)


# ── 测试3: 锚点时间元数据(缺陷六.5,集成测试:真实数据) ──────────────────
print("\n[4] data_validator锚点元数据")
from data_validator import extract_anchors_from_data

anchors = extract_anchors_from_data()
check("锚点非空", len(anchors) > 100, f"got {len(anchors)}")
with_asof = sum(1 for v in anchors.values() if v.get('as_of'))
check("全部锚点带采集日as_of", with_asof == len(anchors), f"{with_asof}/{len(anchors)}")
with_obs = sum(1 for v in anchors.values() if v.get('obs_date'))
check("部分锚点带观测日obs_date(月度FRED序列应有)", with_obs > 3, f"got {with_obs}")
unrate = anchors.get('rate_economy.real_economy.UNRATE.value')
check("UNRATE锚点存在且带obs_date", unrate and unrate.get('obs_date'), str(unrate)[:80])


# ── 测试4: 实体经济频率标注(缺陷六.3) ──────────────────
print("\n[5] rate_expectations频率元数据")
import rate_expectations as rex
import inspect
src = inspect.getsource(rex.fetch_real_economy_data)
check("series_map含频率字段", "'Monthly'" in src and "freq" in src)
check("结果含change_period", "change_period" in src)


# ── 测试5: 流水线失败传播(缺陷六.2,源码级检查) ──────────────────
print("\n[6] run_weekly失败退出码")
rw = open(os.path.join(ROOT, 'run_weekly.py')).read()
check("存在sys.exit(1)失败分支", "sys.exit(1)" in rw and "success_count < len(steps)" in rw)


# ── 测试6: 新闻摘要已迁GLM(缺陷六.1,源码级检查) ──────────────────
print("\n[7] news_collector GLM迁移")
nc = open(os.path.join(ROOT, 'scripts', 'news_collector.py')).read()
check("不再引用DEEPSEEK", "DEEPSEEK" not in nc)
check("使用GLM流式", "GLM_MODEL" in nc and "stream=True" in nc)


print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
