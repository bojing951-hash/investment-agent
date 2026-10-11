#!/usr/bin/env python3
"""P2/P3回归测试(2026-10-11) — 配置观点库+引擎+回写
运行: ~/AI内容/venv/bin/python3 tests/test_p2_fixes.py
"""
import os
import sys
import json
import shutil
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
print("P2/P3回归测试: 配置研究引擎")
print("=" * 60)

import allocation_engine as ae

# ── 测试1: 观点库结构与渲染 ──────────────────
print("\n[1] allocation_views.json结构与渲染")
views = ae.load_views()
check("观点库可加载", views is not None)
check("9资产观点齐全", len(views.get('views', [])) == 9, f"got {len(views.get('views', []))}")
scale = set(views.get('ratings_scale', []))
check("评级都在量表内", all(v.get('rating') in scale for v in views['views']))
check("每个观点有触发器与失效条件", all(v.get('triggers') and v.get('invalidation') for v in views['views']))
check("每个观点有history", all(isinstance(v.get('history'), list) and v['history'] for v in views['views']))

block = ae.render_views_block(views)
check("渲染块含9个资产", all(v['asset'][:2] in block for v in views['views']))
check("渲染块含评级表头", "评级" in block and "确信度" in block)
check("渲染块含预测跟踪", "预测跟踪" in block and "#1" in block)

# ── 测试2: 到期预测扫描 ──────────────────
print("\n[2] due_predictions")
fake = {'predictions': [
    {'pred_id': 1, 'status': 'open', 'deadline': '2020-01-01'},   # 早就到期
    {'pred_id': 2, 'status': 'open', 'deadline': '2099-01-01'},   # 远未到期
    {'pred_id': 3, 'status': 'hit', 'deadline': '2020-01-01'},    # 已裁决不算
]}
due = ae.due_predictions(fake, today_str='2026-10-11')
check("仅open且过期者入选", [p['pred_id'] for p in due] == [1], str(due))

real_due = ae.due_predictions(views, today_str='2026-10-11')
check("真实库当前无到期预测", [p['pred_id'] for p in real_due] == [], str(real_due))

# ── 测试3: ALLOCATION_STATUS回写(临时副本,不动真实库) ──────────────────
print("\n[3] 回写: 评级变更+新预测登记+预测裁决")
with tempfile.TemporaryDirectory() as td:
    tmp_views = os.path.join(td, 'allocation_views.json')
    shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), tmp_views)

    report = """### 八、论点追踪
...
<!--THESIS_STATUS
{"id":1,"status":"待观察","confidence":1,"note":"x"}
THESIS_STATUS-->
<!--ALLOCATION_STATUS
{"id":1,"rating":"标配","confidence":3,"note":"类滞胀确认风险偏好修复","pred":"若CCC回落至850bp下方则SPX两周内创新高","pred_weeks":2}
{"id":5,"rating":"标配","confidence":2,"note":"通胀对冲需求回归"}
ALLOCATION_STATUS-->
<!--PREDICTION_STATUS
{"pred_id":1,"status":"hit","note":"类滞胀10/16获确认,金价10/20收复4300"}
PREDICTION_STATUS-->
"""
    updates = ae.update_allocation_status(report, views_path=tmp_views)
    saved = json.load(open(tmp_views))

    v1 = next(v for v in saved['views'] if v['id'] == 1)
    check("评级中性→标配已回写", v1['rating'] == '标配')
    check("确信度2→3已回写", v1['confidence'] == 3)
    check("history追加且含新评级", any('标配' in h for h in v1['history']))

    new_preds = [p for p in saved['predictions'] if p.get('date_made')]
    check("评级变更行自动登记新预测", len(saved['predictions']) == 3, f"got {len(saved['predictions'])}")
    newest = max(saved['predictions'], key=lambda p: p['pred_id'])
    check("新预测id顺延+deadline按周数", newest['pred_id'] == 3 and newest['deadline'] == '2026-10-25',
          f"id={newest['pred_id']} deadline={newest['deadline']}")
    check("新预测open状态", newest['status'] == 'open')

    p1 = next(p for p in saved['predictions'] if p['pred_id'] == 1)
    check("到期预测hit裁决回写", p1['status'] == 'hit' and p1.get('resolved_date') == '2026-10-11')

    check("备份文件生成", os.path.exists(tmp_views + '.bak'))
    check("last_updated刷新", saved['last_updated'] == '2026-10-11')

# ── 测试4: 非法值拒收 ──────────────────
print("\n[4] 非法值防护")
with tempfile.TemporaryDirectory() as td:
    tmp_views = os.path.join(td, 'allocation_views.json')
    shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), tmp_views)
    bad = """<!--ALLOCATION_STATUS
{"id":1,"rating":"梭哈","confidence":9,"note":"越界值"}
{"id":99,"rating":"超配","confidence":3,"note":"不存在的id"}
ALLOCATION_STATUS-->"""
    ae.update_allocation_status(bad, views_path=tmp_views)
    saved = json.load(open(tmp_views))
    v1 = next(v for v in saved['views'] if v['id'] == 1)
    check("非法评级被拒", v1['rating'] == '中性')
    check("越界确信度被拒", v1['confidence'] == 2)

# ── 测试5: 接线检查(report_generator源码级) ──────────────────
print("\n[5] report_generator接线")
rg = open(os.path.join(ROOT, 'scripts', 'report_generator.py')).read()
check("主流程加载观点库", "allocation_engine.load_views()" in rg)
check("prompt含配置观点库节", "## 配置观点库" in rg)
check("prompt含ALLOCATION_STATUS规范", "ALLOCATION_STATUS" in rg and "rating只能取" in rg)
check("prompt含PREDICTION_STATUS规范", "PREDICTION_STATUS" in rg)
check("回写在数值门禁else分支内", rg.find("update_thesis_status(report)") < rg.find("allocation_engine.update_allocation_status(report)"))
check("观点库回写前有数值门禁", "_has_numeric_errors(warnings)" in rg)

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
