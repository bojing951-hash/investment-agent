#!/usr/bin/env python3
"""P2/P3回归测试 v2(2026-10-11第二轮重构) — 配置观点库+引擎+回写
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
print("P2/P3回归测试v2: 配置研究引擎")
print("=" * 60)

import allocation_engine as ae

# ── 测试1: 观点库结构v2与渲染 ──────────────────
print("\n[1] allocation_views.json结构与渲染(量表v2)")
views = ae.load_views()
check("观点库可加载", views is not None)
check("9资产观点齐全", len(views.get('views', [])) == 9, f"got {len(views.get('views', []))}")
check("量表=超配/标配/低配/观望(无'中性')", views.get('ratings_scale') == ['超配', '标配', '低配', '观望'],
      str(views.get('ratings_scale')))
check("各观点评级都在量表内", all(v.get('rating') in views['ratings_scale'] for v in views['views']))
check("无观点残留'中性'评级", all(v.get('rating') != '中性' for v in views['views']))
check("每个观点有触发器与失效条件", all(v.get('triggers') and v.get('invalidation') for v in views['views']))
check("每个观点有history", all(isinstance(v.get('history'), list) and v['history'] for v in views['views']))
qt = [t for v in views['views'] for t in v.get('quant_triggers', [])]
check(f"量化触发器存在且规格完整(共{len(qt)}条)",
      len(qt) >= 4 and all(t.get('metric') and t.get('op') in ae.COMPARATORS
                           and isinstance(t.get('target'), (int, float)) for t in qt))

block = ae.render_views_block(views)  # 无锚点 → 全部待验证
check("渲染块含9个资产", all(v['asset'][:2] in block for v in views['views']))
check("渲染块含量表定义", "标配" in block and "评级量表" in block)
check("无锚点时触发器标注待验证", "❓待验证" in block)
check("渲染块含触发器纪律声明", "触发器纪律" in block and "不得当作已发生" in block)
check("渲染块含预测五态跟踪", "预测跟踪" in block and "#1" in block and "未触发" in block)
p1 = next(p for p in views['predictions'] if p['pred_id'] == 1)
check("预测#1带机器规格(metric/comparator/target/evidence_ref)",
      all(k in p1 for k in ('metric', 'comparator', 'target', 'evidence_ref')))

# ── 测试2: 到期预测扫描(v2状态) ──────────────────
print("\n[2] due_predictions(五态)")
fake = {'predictions': [
    {'pred_id': 1, 'status': 'observing', 'deadline': '2020-01-01'},
    {'pred_id': 2, 'status': 'not_yet_triggered', 'deadline': '2020-01-01'},  # 未触发到期也须裁决
    {'pred_id': 3, 'status': 'observing', 'deadline': '2099-01-01'},
    {'pred_id': 4, 'status': 'hit', 'deadline': '2020-01-01'},   # 已裁决不算
    {'pred_id': 5, 'status': 'miss', 'deadline': '2020-01-01'},
]}
due = ae.due_predictions(fake, today_str='2026-10-11')
check("观察中/未触发且过期者入选", [p['pred_id'] for p in due] == [1, 2], str(due))

real_due = ae.due_predictions(views, today_str='2026-10-11')
check("真实库当前无到期预测", [p['pred_id'] for p in real_due] == [], str(real_due))

# ── 测试3: 回写(评级/确信度分记+带规格新预测+证据裁决) ──────────────────
print("\n[3] 回写: 评级与确信度分别记录+规格化新预测+带证据裁决")
with tempfile.TemporaryDirectory() as td:
    tmp_views = os.path.join(td, 'allocation_views.json')
    shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), tmp_views)

    report = """### 八、论点追踪
<!--ALLOCATION_STATUS
{"id":5,"rating":"标配","confidence":3,"note":"类滞胀确认,通胀对冲回归","pred":"若CCC回落至850bp下方则两周内金价回调2%","pred_weeks":2,"pred_metric":"macro.data.CCC_OAS.value","pred_op":"<=","pred_target":8.5}
{"id":1,"rating":"标配","confidence":2,"note":"拉锯"}
ALLOCATION_STATUS-->
<!--PREDICTION_STATUS
{"pred_id":1,"status":"hit","note":"金价4310≥4300(观测日2026-10-16)"}
PREDICTION_STATUS-->
"""
    anchors = {"macro.data.CCC_OAS.value": {"value": 10.30, "obs_date": "2026-10-15"},
               "global_market.data.GOLD.close": {"value": 4310, "obs_date": "2026-10-16"},
               "global_market.data.SPX.close": {"value": 7580, "obs_date": "2026-10-16"}}
    ae.update_allocation_status(report, views_path=tmp_views, anchors=anchors, today_str='2026-10-11')
    saved = json.load(open(tmp_views))

    v5 = next(v for v in saved['views'] if v['id'] == 5)
    check("id5观望→标配已回写", v5['rating'] == '标配')
    check("评级变化单独记录", any(h.startswith('10/11 评级') and '观望→标配' in h for h in v5['history']),
          str(v5['history']))
    new_preds = [p for p in saved['predictions'] if p['pred_id'] == 3]
    check("评级变更行自动登记新预测#3", len(new_preds) == 1, f"got {len(saved['predictions'])}条")
    if new_preds:
        np = new_preds[0]
        check("新预测deadline按周数(10-11+2周)", np['deadline'] == '2026-10-25', np['deadline'])
        check("新预测带量化规格", np.get('metric') == 'macro.data.CCC_OAS.value'
              and np.get('comparator') == '<=' and np.get('target') == 8.5)
        check("新预测状态=观察中", np['status'] == 'observing')
    p1 = next(p for p in saved['predictions'] if p['pred_id'] == 1)
    check("预测#1带数值证据hit裁决回写", p1['status'] == 'hit' and '4310' in p1['resolved_note'])
    check("备份文件生成", os.path.exists(tmp_views + '.bak'))
    check("last_updated刷新", saved['last_updated'] == '2026-10-11')

# ── 测试3b: 仅确信度变化也必须落盘(第二轮#10回归) ──────────────────
print("\n[3b] 仅确信度变化回写(缺陷#10回归)")
with tempfile.TemporaryDirectory() as td:
    tmp_views = os.path.join(td, 'allocation_views.json')
    shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), tmp_views)
    report = """<!--ALLOCATION_STATUS
{"id":1,"rating":"标配","confidence":4,"note":"证据增厚,评级不变"}
ALLOCATION_STATUS-->"""
    updates = ae.update_allocation_status(report, views_path=tmp_views, today_str='2026-10-18')
    saved = json.load(open(tmp_views))
    v1 = next(v for v in saved['views'] if v['id'] == 1)
    check("确信度2→4已回写", v1['confidence'] == 4, str(v1.get('confidence')))
    check("确信度变化单独记录(独立history条目)",
          any(h.startswith('10/18 确信度') and '2★→4★' in h for h in v1['history']), str(v1['history']))
    check("评级未变(仍标配)", v1['rating'] == '标配')
    check("文件确实落盘(last_updated=10-18)", saved['last_updated'] == '2026-10-18')
    check("更新摘要含确信度条目", any('确信度' in u for u in updates), str(updates))

# ── 测试4: 非法值拒收 + 无证据裁决拒绝 ──────────────────
print("\n[4] 非法值防护与证据门禁(第二轮#12)")
with tempfile.TemporaryDirectory() as td:
    tmp_views = os.path.join(td, 'allocation_views.json')
    shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), tmp_views)
    bad = """<!--ALLOCATION_STATUS
{"id":1,"rating":"梭哈","confidence":9,"note":"越界值"}
{"id":2,"rating":"中性","confidence":3,"note":"v1旧量表词应被拒"}
{"id":99,"rating":"超配","confidence":3,"note":"不存在的id"}
ALLOCATION_STATUS-->
<!--PREDICTION_STATUS
{"pred_id":2,"status":"hit","note":""}
{"pred_id":2,"status":"miss"}
PREDICTION_STATUS-->"""
    ae.update_allocation_status(bad, views_path=tmp_views, today_str='2026-10-11')
    saved = json.load(open(tmp_views))
    v1 = next(v for v in saved['views'] if v['id'] == 1)
    v2 = next(v for v in saved['views'] if v['id'] == 2)
    check("非法评级被拒", v1['rating'] == '标配')
    check("'中性'按v1旧词拒收(量表统一)", v2['rating'] == '低配')
    check("越界确信度被拒", v1['confidence'] == 2)
    p2 = next(p for p in saved['predictions'] if p['pred_id'] == 2)
    check("无note的hit裁决被拒", p2['status'] == 'observing', p2['status'])
    check("缺note字段的miss裁决被拒", p2['status'] == 'observing')

with tempfile.TemporaryDirectory() as td:
    tmp_views = os.path.join(td, 'allocation_views.json')
    shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), tmp_views)
    no_num = """<!--PREDICTION_STATUS
{"pred_id":2,"status":"hit","note":"感觉对了"}
PREDICTION_STATUS-->"""
    ae.update_allocation_status(no_num, views_path=tmp_views, today_str='2026-10-11')
    saved = json.load(open(tmp_views))
    p2 = next(p for p in saved['predictions'] if p['pred_id'] == 2)
    check("note无具体数值的裁决被拒(证据须引用数值)", p2['status'] == 'observing', p2['status'])

# ── 测试5: 量化触发器核验 ──────────────────
print("\n[5] evaluate_quant_triggers")
anchors_hit = {"macro.data.CCC_OAS.value": {"value": 10.12, "obs_date": "2026-10-08"}}
trig = ae.evaluate_quant_triggers(views, anchors_hit)
t3 = next(r for r in trig[3] if r['trig_id'] == 'T1')
check("CCC 10.12≥10.0 → 已触发", t3['status'] == 'triggered', str(t3))
check("核验详情含观测日", '2026-10-08' in t3['detail'], t3['detail'])
trig2 = ae.evaluate_quant_triggers(views, {"macro.data.CCC_OAS.value": {"value": 9.46, "obs_date": "2026-09-24"}})
t3b = next(r for r in trig2[3] if r['trig_id'] == 'T1')
check("CCC 9.46<10.0 → 未触发", t3b['status'] == 'not_triggered', str(t3b))
trig3 = ae.evaluate_quant_triggers(views, {})  # 无任何锚点
t3c = next(r for r in trig3[3] if r['trig_id'] == 'T1')
check("无锚点 → 待验证(不得声称已触发)", t3c['status'] == 'unverifiable', str(t3c))
t2 = next((r for r in trig3[5] if r['trig_id'] == 'T2'), None)
check("TIPS触发器无锚点 → 待验证", t2 and t2['status'] == 'unverifiable')

# ── 测试6: 到期预测自动裁决 + 周期统计 ──────────────────
print("\n[6] evaluate_predictions / predictions_in_period")
vd = {'predictions': [
    {'pred_id': 1, 'status': 'observing', 'deadline': '2026-10-10',
     'metric': 'global_market.data.GOLD.close', 'comparator': '>=', 'target': 4300},
    {'pred_id': 2, 'status': 'observing', 'deadline': '2026-10-10',
     'metric': 'global_market.data.SPX.close', 'comparator': '>=', 'target': 7700},
    {'pred_id': 3, 'status': 'observing', 'deadline': '2026-10-10',
     'metric': 'macro.data.NOSUCH.value', 'comparator': '>=', 'target': 1},
    {'pred_id': 4, 'status': 'observing', 'deadline': '2099-01-01',
     'metric': 'global_market.data.GOLD.close', 'comparator': '>=', 'target': 4300},
    {'pred_id': 5, 'status': 'not_yet_triggered', 'deadline': '2026-10-10'},
]}
anc = {"global_market.data.GOLD.close": {"value": 4310, "obs_date": "2026-10-16"},
       "global_market.data.SPX.close": {"value": 7580, "obs_date": "2026-10-16"}}
v = ae.evaluate_predictions(vd, anc, today_str='2026-10-16')
by_id = {pid: (new, note) for pid, old, new, note in v}
check("GOLD 4310≥4300 → 自动hit", by_id[1][0] == 'hit', str(by_id.get(1)))
check("SPX 7580<7700 → 自动miss", by_id[2][0] == 'miss', str(by_id.get(2)))
check("无锚点数据 → 无法裁决(不硬判)", by_id[3][0] == 'inconclusive', str(by_id.get(3)))
check("未到期不裁决", 4 not in by_id)
check("未触发状态不自动裁决(留给GLM)", 5 not in by_id)
check("裁决note引用数值与观测日", '4310' in by_id[1][1] and '2026-10-16' in by_id[1][1], by_id[1][1])

pp = ae.predictions_in_period(
    {'predictions': [
        {'pred_id': 1, 'deadline': '2026-09-10', 'status': 'hit', 'resolved_date': '2026-09-12'},
        {'pred_id': 2, 'deadline': '2026-09-20', 'status': 'miss', 'resolved_date': '2026-09-25'},
        {'pred_id': 3, 'deadline': '2026-10-25', 'status': 'observing'},
    ]}, '20260901', '20260930')
check("周期内到期2条/裁决2条", len(pp['due']) == 2 and len(pp['resolved']) == 2, str(pp))
check("命中率按周期统计(hit1/miss1)", pp['counts']['hit'] == 1 and pp['counts']['miss'] == 1)
check("10月到期的预测不计入9月", all(p['pred_id'] != 3 for p in pp['due']))

# ── 测试7: v1→v2迁移 ──────────────────
print("\n[7] v1数据迁移")
legacy = {"ratings_scale": ["超配", "标配", "中性", "低配", "观望"],
          "views": [{"id": 1, "asset": "美股", "rating": "中性", "confidence": 2, "history": []}],
          "predictions": [{"pred_id": 1, "status": "open", "deadline": "2026-10-25"},
                          {"pred_id": 2, "status": "expired", "deadline": "2026-09-25"}]}
changed = ae._migrate_views(legacy)
check("迁移标记changed", changed is True)
check("'中性'→'标配'", legacy['views'][0]['rating'] == '标配')
check("量表迁移", legacy['ratings_scale'] == ['超配', '标配', '低配', '观望'])
check("open→observing", legacy['predictions'][0]['status'] == 'observing')
check("expired→inconclusive", legacy['predictions'][1]['status'] == 'inconclusive')

# ── 测试8: 接线检查(report_generator源码级) ──────────────────
print("\n[8] report_generator接线")
rg = open(os.path.join(ROOT, 'scripts', 'report_generator.py')).read()
check("主流程加载观点库", "allocation_engine.load_views()" in rg)
check("渲染时传入锚点核验触发器", "render_views_block(views_data, anchors=latest_anchors)" in rg)
check("prompt含配置观点库节", "## 配置观点库" in rg)
check("prompt含量表v2规范", "rating只能取" in rg and "不用\"中性\"" in rg)
check("prompt含结构化预测规格", "pred_metric" in rg and "pred_op" in rg)
check("prompt含五态裁决规范", "not_yet_triggered" in rg and "无证据" in rg)
check("回写在FAIL门禁else分支内", rg.find("update_thesis_status(report)") < rg.find("allocation_engine.update_allocation_status(report"))
check("校验分级FAIL禁止回写", 'classification == "FAIL"' in rg and "跳过thesis.json与allocation_views.json回写" in rg)

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
