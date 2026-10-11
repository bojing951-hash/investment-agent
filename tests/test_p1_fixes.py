#!/usr/bin/env python3
"""P1增强回归测试(2026-10-11) — 纯Python assert,无需pytest
运行: ~/AI内容/venv/bin/python3 tests/test_p1_fixes.py
覆盖: 体制归因 / 提示词配置化 / 校验时点检查
"""
import os
import sys
from datetime import date

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
print("P1增强回归测试")
print("=" * 60)

# ── 测试1: 体制归因(反事实分解) ──────────────────
print("\n[1] macro_scorecard.attribute_regime")
from macro_scorecard import attribute_regime

# 构造: 通胀+4 核心CPI(+2)单独就能决定高通胀侧
g = {'retail': {'name': '零售', 'score': 1}}
i = {'cpi': {'name': '核心CPI', 'score': 2}, 'bei': {'name': 'BEI', 'score': 2}}
drivers, cfs = attribute_regime(g, 1, i, 4)
# 基准: i=4>=3, g=1>0 → 类滞胀。剔除核心CPI→i=2,仍>0 → 再通胀(翻转→关键驱动)
# (第二轮#18修复: 原"或True"恒真断言已删除,改为可证伪断言)
check("单指标可翻转→识别出关键驱动", len(drivers) >= 1, str(drivers))
check("核心CPI(+2)是关键驱动", any('核心CPI' in d and '再通胀' in d for d in drivers), str(drivers))
check("反事实清单覆盖全部指标", len(cfs) == len(g) + len(i), f"got {len(cfs)}")

# 无单一指标可翻转的稳健情形: 增长两指标(+1+1)、通胀四指标(各+1),
# 剔除任一后增长仍>0且通胀仍≥3 → 体制不变 → 无关键驱动
g2 = {'r1': {'name': 'R1', 'score': 1}, 'r2': {'name': 'R2', 'score': 1}}
i2 = {'a': {'name': 'A', 'score': 1}, 'b': {'name': 'B', 'score': 1},
      'c': {'name': 'C', 'score': 1}, 'd': {'name': 'D', 'score': 1}}
drivers2, _ = attribute_regime(g2, 2, i2, 4)
check("多指标共同支撑→无关键驱动", drivers2 == [], str(drivers2))

# 真实数据冒烟: 今天的评分卡JSON应含regime_drivers字段(无真实数据时用E2E fixture,第二轮#20)
import json, glob
sc_files = sorted(glob.glob(os.path.join(ROOT, 'data', 'daily', 'scorecard_*.json')))
if not sc_files:
    sc_files = sorted(glob.glob(os.path.join(ROOT, 'tests', 'fixtures', 'e2e', 'w4_data', 'scorecard_*.json')))
if sc_files:
    sc = json.load(open(sc_files[-1]))
    check("最新评分卡含归因字段", 'regime_drivers' in sc, sc_files[-1])
else:
    check("评分卡文件存在", False, "无scorecard_*.json")

# ── 测试2: 提示词配置化(2026-10-11第二轮: 角色统一为跨资产策略师,删除账户管理职责) ──────────────────
print("\n[2] 提示词热加载")
from report_generator import load_prompt

sp = load_prompt('system_prompt.md')
check("系统提示词为跨资产策略师角色(第二轮#4)", "全球宏观首席研究员兼跨资产策略师" in sp, sp[:60])
check("声明不管理真实账户不执行交易", "不管理真实账户" in sp and "不执行交易" in sp)
check("含六步研究流程", "核对时点" in sp and "检查反证" in sp and "提出配置倾向" in sp)
check("秘书角色与账户职责已移除", "秘书" not in sp and "下单" not in sp and "未获取用户确认" not in sp)
check("含证据分级v2门槛", "【证据分级v2】" in sp and "5★" in sp and "3类机制" in sp)
check("含反证封顶与缺失不评级", "最高3★" in sp and "不评级" in sp)
check("含禁止用语v2清单", "【禁止用语v2】" in sp and "板上钉钉" in sp and "risk-free" in sp)
check("含数值绑定纪律", "指标ID" in sp and "不得将相关性直接解释为因果关系" in sp)
check("含配置建议要素", "宏观依据" in sp and "传导机制" in sp and "无充分新增证据时允许维持原观点" in sp)
check("保留输出语言/格式尾部", "输出语言：中文" in sp and "输出格式：Markdown" in sp)
mp = load_prompt('monthly_review_prompt.md')
qp = load_prompt('quarterly_outlook_prompt.md')
check("月报提示词同为策略师+显式免责", "跨资产策略师" in mp and "不管理真实账户" in mp and "不执行交易" in mp)
check("月报提示词无下单/审批类指令", "下单" not in mp and "审批" not in mp)
check("月报提示词含bp/pp单位纪律", "bp" in mp and "pp" in mp)
check("月报提示词含预览纪律", "【预览】" in mp)
check("季报提示词同为策略师+显式免责", "跨资产策略师" in qp and "不管理真实账户" in qp and "不执行交易" in qp)
check("季报提示词无下单/审批类指令", "下单" not in qp and "审批" not in qp)
sc_txt = load_prompt('style_constraints.md')
check("硬性约束10条完整", "完美验证" in sc_txt and "30Y收益率" in sc_txt and "10." in sc_txt)
check("硬约束挂接证据分级v2", "证据分级v2" in sc_txt and "禁止用语v2" in sc_txt)

# ── 测试3: 校验时点检查 ──────────────────
print("\n[3] data_validator时点检查")
from data_validator import _obs_staleness_warning, _report_date_from_path

rd = date(2026, 10, 9)
fresh = {'value': 6000, 'obs_date': '2026-10-08'}
stale = {'value': 6000, 'obs_date': '2026-09-25'}
monthly = {'value': 4.2, 'obs_date': '2026-09-01'}
check("日频新鲜→无警告", _obs_staleness_warning('global_market.data.SPX.close', fresh, rd) is None)
w = _obs_staleness_warning('global_market.data.SPX.close', stale, rd)
check("日频滞后14天→警告", w is not None and '时点滞后' in w and '14' in w, str(w))
check("月度FRED序列免检", _obs_staleness_warning('rate_economy.real_economy.UNRATE.value', monthly, rd) is None)
check("无obs_date免检", _obs_staleness_warning('global_market.data.SPX.close', {'value': 1}, rd) is None)
check("文件名解析报告日", _report_date_from_path('/x/weekly_report_20261009.md') == rd)

# ── 测试4: 禁止用语v2校验(绝对/必然豁免逻辑) ──────────────────
print("\n[4] data_validator禁语v2")
from data_validator import forbidden_phrases_in

def _phrases(text):
    return [p for p, _ in forbidden_phrases_in(text)]

check("v1禁语仍在清单", "完美验证" in _phrases("完美验证"))
check("v2新增词命中", "板上钉钉" in _phrases("板上钉钉") and "零风险" in _phrases("零风险套利"))
check("英文禁语命中", "guaranteed" in _phrases("this is guaranteed"))
check("'绝对收益'豁免", _phrases("黄金是绝对收益资产,绝对估值偏低") == [])
check("裸'绝对'命中", any(p.startswith("绝对") for p in _phrases("这是绝对的机会")))
check("'必然'命中", "必然" in _phrases("必然上涨"))
check("干净文本零命中", _phrases("本周SPX上涨2%,有一定支撑(3★),绝对收益策略跑赢") == [])

# 警告为⚠️级,不得触发回写拦截(_has_numeric_errors只认🚨和❌数值类)
from report_generator import _has_numeric_errors
check("时点警告不拦截回写", _has_numeric_errors([w]) is False if w else True)

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
