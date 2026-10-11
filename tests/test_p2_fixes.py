#!/usr/bin/env python3
"""P2/P3回归测试 v3(2026-10-11第三轮适配) — 配置观点库+引擎+回写
第三轮语义: 评级变更须过门禁(触发器或≥2项验证证据); 确信度上调须星级支撑;
预测touch/expiry双模式+观察窗过滤+引擎权威裁决。
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
print("P2/P3回归测试v3: 配置研究引擎")
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
check("触发器含持续条件(sustain_weeks)", any(t.get('sustain_weeks') for t in qt))

block = ae.render_views_block(views)  # 无锚点 → 全部待验证
check("渲染块含9个资产", all(v['asset'][:2] in block for v in views['views']))
check("渲染块含量表定义", "标配" in block and "评级量表" in block)
check("无锚点时触发器标注待验证", "❓待验证" in block)
check("渲染块含触发器纪律声明", "触发器纪律" in block and "不得当作已发生" in block)
check("渲染块含预测五态跟踪", "预测跟踪" in block and "#1" in block and "未触发" in block)
check("渲染块按预测标注裁决模式(截止日达到)+模式映射完整",
      "截止日达到" in block and set(ae.VERIFY_MODE_CN.values()) == {'观察期内触及', '截止日达到'})
p1 = next(p for p in views['predictions'] if p['pred_id'] == 1)
check("预测#1带机器规格(metric/comparator/target/evidence_ref)",
      all(k in p1 for k in ('metric', 'comparator', 'target', 'evidence_ref')))
check("预测#1带生命周期字段(verify_mode/observations)", p1.get('verify_mode') in ('touch', 'expiry')
      and p1.get('observations') == [])

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

# ── 测试3: 回写门禁(第三轮: 无证据变更被拒+留档; 提前裁决拒绝) ──────────
print("\n[3] 回写: 评级门禁拒绝路径(无证据) + 预测提前裁决拒绝")
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
    anchors = {"macro.data.CCC_OAS.value": {"value": 10.30, "obs_date": "2026-10-10"},
               "global_market.data.GOLD.close": {"value": 4310, "obs_date": "2026-10-10"},
               "global_market.data.SPX.close": {"value": 7580, "obs_date": "2026-10-10"}}
    ae.update_allocation_status(report, views_path=tmp_views, anchors=anchors, today_str='2026-10-11')
    saved = json.load(open(tmp_views))

    v5 = next(v for v in saved['views'] if v['id'] == 5)
    check("id5无证据变更被拒: 仍观望(第三轮门禁)", v5['rating'] == '观望', v5['rating'])
    check("被拒提案留档(评级+确信度各一条)",
          any(p['status'] == 'rejected' and p['to'] == '标配' for p in v5.get('proposals', []))
          and any(p['to'] == '确信度3★' for p in v5.get('proposals', [])), str(v5.get('proposals')))
    check("评级被拒不登记新预测(预测只挂在真实变更上)",
          not any(p['pred_id'] == 3 for p in saved['predictions']),
          f"got {len(saved['predictions'])}条")
    p1 = next(p for p in saved['predictions'] if p['pred_id'] == 1)
    check("预测#1 expiry截止(10-25)未到,GLM提前hit被拒(仍未触发)",
          p1['status'] == 'not_yet_triggered', p1['status'])
    check("备份文件生成", os.path.exists(tmp_views + '.bak'))
    check("last_updated刷新", saved['last_updated'] == '2026-10-11')

# ── 测试3c: 门禁通过路径(≥2项验证证据)→变更+新预测登记 ──────────
print("\n[3c] 回写: 补证据后变更通过 + 规格化新预测登记")
with tempfile.TemporaryDirectory() as td:
    tmp_views = os.path.join(td, 'allocation_views.json')
    shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), tmp_views)
    report = """<!--ALLOCATION_STATUS
{"id":5,"rating":"标配","confidence":3,"note":"避险与通胀对冲证据齐","evidence":[{"metric":"macro.data.CCC_OAS.value","value":10.30,"obs_date":"2026-10-15","mechanism":"信用"},{"metric":"global_market.data.GOLD.close","value":4310,"obs_date":"2026-10-16","mechanism":"避险与估值"},{"metric":"global_market.data.SPX.close","value":7580,"obs_date":"2026-10-16","mechanism":"增长"}],"pred":"若CCC回落至850bp下方则两周内金价回调2%","pred_weeks":2,"pred_metric":"macro.data.CCC_OAS.value","pred_op":"<=","pred_target":8.5,"pred_mode":"touch"}
ALLOCATION_STATUS-->"""
    anchors = {"macro.data.CCC_OAS.value": {"value": 10.30, "obs_date": "2026-10-15"},
               "global_market.data.GOLD.close": {"value": 4310, "obs_date": "2026-10-16"},
               "global_market.data.SPX.close": {"value": 7580, "obs_date": "2026-10-16"}}
    ae.update_allocation_status(report, views_path=tmp_views, anchors=anchors, today_str='2026-10-16')
    saved = json.load(open(tmp_views))
    v5 = next(v for v in saved['views'] if v['id'] == 5)
    check("id5观望→标配经3项验证证据通过", v5['rating'] == '标配')
    check("评级变化单独记录", any(h.startswith('10/16 评级') and '观望→标配' in h for h in v5['history']),
          str(v5['history']))
    check("变更审计走证据路径", '证据3项' in v5['last_change']['via'], str(v5['last_change']))
    new_preds = [p for p in saved['predictions'] if p['pred_id'] == 3]
    check("评级变更行自动登记新预测#3", len(new_preds) == 1, f"got {len(saved['predictions'])}条")
    if new_preds:
        np = new_preds[0]
        check("新预测deadline按周数(10-16+2周)", np['deadline'] == '2026-10-30', np['deadline'])
        check("新预测带量化规格", np.get('metric') == 'macro.data.CCC_OAS.value'
              and np.get('comparator') == '<=' and np.get('target') == 8.5)
        check("新预测touch模式+观察起点", np.get('verify_mode') == 'touch'
              and np.get('observe_from') == '2026-10-16')
        check("新预测状态=观察中且当周已记观测", np['status'] == 'observing'
              and len(np.get('observations', [])) == 1)

# ── 测试3d: 定性预测到期只能研究性回顾(第四轮P0-6: 不入客观命中率) ──────────
print("\n[3d] 定性预测: GLM判hit被拒,只能inconclusive研究回顾")
with tempfile.TemporaryDirectory() as td:
    tmp_views = os.path.join(td, 'allocation_views.json')
    shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), tmp_views)
    report = """<!--ALLOCATION_STATUS
{"id":1,"rating":"标配","confidence":2,"note":"m"}
ALLOCATION_STATUS-->
<!--PREDICTION_STATUS
{"pred_id":2,"status":"hit","note":"HY指数到期周回撤1.2%,未超3%上限(观测日2026-11-06)"}
PREDICTION_STATUS-->"""
    ae.update_allocation_status(report, views_path=tmp_views, today_str='2026-11-08')
    saved = json.load(open(tmp_views))
    p2 = next(p for p in saved['predictions'] if p['pred_id'] == 2)
    check("定性预测#2(无规格)GLM判hit被拒(文字说明≠观察记录)",
          p2['status'] == 'observing', p2['status'])
with tempfile.TemporaryDirectory() as td:
    tmp_views = os.path.join(td, 'allocation_views.json')
    shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), tmp_views)
    report = """<!--ALLOCATION_STATUS
{"id":1,"rating":"标配","confidence":2,"note":"m"}
ALLOCATION_STATUS-->
<!--PREDICTION_STATUS
{"pred_id":2,"status":"inconclusive","note":"研究回顾: HY利差全周期抬升约60bp,方向与预判一致但幅度依赖口径"}
PREDICTION_STATUS-->"""
    ae.update_allocation_status(report, views_path=tmp_views, today_str='2026-11-08')
    saved = json.load(open(tmp_views))
    p2 = next(p for p in saved['predictions'] if p['pred_id'] == 2)
    pp = ae.predictions_in_period(saved, '20261101', '20261130')
    check("定性预测inconclusive研究回顾被接受(单列qualitative,不计命中率)",
          p2['status'] == 'inconclusive' and pp['counts']['qualitative'] == 1
          and pp['counts']['hit'] == 0, f"{p2['status']} {pp['counts']}")

# ── 测试3b: 仅确信度变化(第三轮: 上调须星级支撑) ──────────
print("\n[3b] 仅确信度变化回写(上调过星级被拒/证据支撑通过)")
with tempfile.TemporaryDirectory() as td:
    tmp_views = os.path.join(td, 'allocation_views.json')
    shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), tmp_views)
    report = """<!--ALLOCATION_STATUS
{"id":1,"rating":"标配","confidence":4,"note":"证据增厚,评级不变"}
ALLOCATION_STATUS-->"""
    ae.update_allocation_status(report, views_path=tmp_views, today_str='2026-10-18')
    saved = json.load(open(tmp_views))
    v1 = next(v for v in saved['views'] if v['id'] == 1)
    check("无证据时确信度2→4被拒(程序星级0★)", v1['confidence'] == 2, str(v1.get('confidence')))
    check("确信度被拒留档", any(p['to'] == '确信度4★' for p in v1.get('proposals', [])))
    check("文件确实落盘(last_updated=10-18)", saved['last_updated'] == '2026-10-18')

with tempfile.TemporaryDirectory() as td:
    tmp_views = os.path.join(td, 'allocation_views.json')
    shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), tmp_views)
    report = """<!--ALLOCATION_STATUS
{"id":1,"rating":"标配","confidence":3,"note":"证据增厚","evidence":[{"metric":"macro.data.CCC_OAS.value","value":10.30,"obs_date":"2026-10-17","mechanism":"信用"},{"metric":"global_market.data.SPX.close","value":7580,"obs_date":"2026-10-17","mechanism":"增长"},{"metric":"global_market.data.GOLD.close","value":4310,"obs_date":"2026-10-17","mechanism":"避险与估值"}]}
ALLOCATION_STATUS-->"""
    anchors = {"macro.data.CCC_OAS.value": {"value": 10.30, "obs_date": "2026-10-17"},
               "global_market.data.SPX.close": {"value": 7580, "obs_date": "2026-10-17"},
               "global_market.data.GOLD.close": {"value": 4310, "obs_date": "2026-10-17"}}
    updates = ae.update_allocation_status(report, views_path=tmp_views, anchors=anchors, today_str='2026-10-18')
    saved = json.load(open(tmp_views))
    v1 = next(v for v in saved['views'] if v['id'] == 1)
    check("3项3类证据(3★)支撑确信度2→3通过", v1['confidence'] == 3, str(v1.get('confidence')))
    check("确信度变化单独记录(独立history条目)",
          any(h.startswith('10/18 确信度') and '2★→3★' in h for h in v1['history']), str(v1['history']))
    check("评级未变(仍标配)", v1['rating'] == '标配')
    check("更新摘要含确信度条目", any('确信度' in u for u in updates), str(updates))

# ── 测试4: 非法值拒收 + 无证据裁决拒绝 ──────────
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

# ── 测试5: 量化触发器核验 ──────────
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

# ── 测试6: 到期预测自动裁决 + 周期统计(第三轮: 观察窗过滤) ──────────
print("\n[6] evaluate_predictions / predictions_in_period")
vd = {'predictions': [
    {'pred_id': 1, 'status': 'observing', 'deadline': '2026-10-10', 'observe_from': '2026-10-02',
     'metric': 'global_market.data.GOLD.close', 'comparator': '>=', 'target': 4300,
     'verify_mode': 'expiry'},
    {'pred_id': 2, 'status': 'observing', 'deadline': '2026-10-10', 'observe_from': '2026-10-02',
     'metric': 'global_market.data.SPX.close', 'comparator': '>=', 'target': 7700,
     'verify_mode': 'expiry'},
    {'pred_id': 3, 'status': 'observing', 'deadline': '2026-10-10', 'observe_from': '2026-10-02',
     'metric': 'macro.data.NOSUCH.value', 'comparator': '>=', 'target': 1, 'verify_mode': 'expiry'},
    {'pred_id': 4, 'status': 'observing', 'deadline': '2099-01-01', 'observe_from': '2026-10-02',
     'metric': 'global_market.data.GOLD.close', 'comparator': '>=', 'target': 4300,
     'verify_mode': 'expiry'},
    {'pred_id': 5, 'status': 'not_yet_triggered', 'deadline': '2026-10-10'},
    {'pred_id': 6, 'status': 'observing', 'deadline': '2026-10-10', 'observe_from': '2026-10-02',
     'metric': 'global_market.data.DXY.close', 'comparator': '>=', 'target': 99,
     'verify_mode': 'expiry'},   # 未来数据保护: 锚点观测日晚于deadline
]}
anc = {"global_market.data.GOLD.close": {"value": 4310, "obs_date": "2026-10-09"},
       "global_market.data.SPX.close": {"value": 7580, "obs_date": "2026-10-09"},
       "global_market.data.DXY.close": {"value": 100.5, "obs_date": "2026-10-12"}}
v = ae.evaluate_predictions(vd, anchors=anc, today_str='2026-10-16')
by_id = {pid: (new, note) for pid, old, new, note in v}
check("GOLD 4310≥4300(截止窗内观测) → 自动hit", by_id[1][0] == 'hit', str(by_id.get(1)))
check("SPX 7580<7700 → 自动miss", by_id[2][0] == 'miss', str(by_id.get(2)))
check("无锚点数据 → 无法裁决(不硬判)", by_id[3][0] == 'inconclusive', str(by_id.get(3)))
check("未到期不裁决", 4 not in by_id)
check("未触发状态到期转终态未生效(第三轮: 前提到期未成立)",
      by_id[5][0] == 'not_yet_triggered', str(by_id.get(5)))
check("裁决note引用数值与观测日", '4310' in by_id[1][1] and '2026-10-09' in by_id[1][1], by_id[1][1])
check("锚点观测日晚于deadline(未来数据)→无法裁决",
      by_id[6][0] == 'inconclusive', str(by_id.get(6)))

pp = ae.predictions_in_period(
    {'predictions': [
        {'pred_id': 1, 'deadline': '2026-09-10', 'status': 'hit', 'resolved_date': '2026-09-12'},
        {'pred_id': 2, 'deadline': '2026-09-20', 'status': 'miss', 'resolved_date': '2026-09-25'},
        {'pred_id': 3, 'deadline': '2026-10-25', 'status': 'observing'},
    ]}, '20260901', '20260930')
check("周期内到期2条/裁决2条", len(pp['due']) == 2 and len(pp['resolved']) == 2, str(pp))
check("命中率按周期统计(hit1/miss1)", pp['counts']['hit'] == 1 and pp['counts']['miss'] == 1)
check("10月到期的预测不计入9月", all(p['pred_id'] != 3 for p in pp['due']))

# ── 测试7: v1→v2迁移 ──────────
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
check("预测生命周期字段补全(verify_mode/observations/data_source)",
      legacy['predictions'][0]['verify_mode'] == 'expiry' and legacy['predictions'][0]['observations'] == []
      and legacy['predictions'][0]['data_source'] == 'anchors')

# ── 测试8: 接线检查(report_generator源码级) ──────────
print("\n[8] report_generator接线")
rg = open(os.path.join(ROOT, 'scripts', 'report_generator.py')).read()
check("主流程加载观点库", "allocation_engine.load_views()" in rg)
check("渲染时传入锚点+研究截止时间核验触发器",
      "render_views_block(" in rg and "anchors=latest_anchors" in rg
      and "today_str=datetime.now()" in rg)
check("回写统一研究截止时间(today_str,经apply_status_updates调度)",
      "allocation_engine.update_allocation_status(report, views_path=views_path," in rg
      and "anchors=anchors, today_str=_today" in rg
      and "apply_status_updates(report, classification, anchors=latest_anchors)" in rg)
check("prompt含配置观点库节", "## 配置观点库" in rg)
check("prompt含量表v2规范", "rating只能取" in rg and "不用\"中性\"" in rg)
check("prompt含结构化预测规格", "pred_metric" in rg and "pred_op" in rg)
check("prompt含touch/expiry双模式规范", "pred_mode" in rg and "touch" in rg and "expiry" in rg)
check("prompt含五态裁决规范", "not_yet_triggered" in rg and "无证据" in rg)
check("prompt含证据分级v2程序校验规则", "证据分级v2程序校验" in rg and "evidence" in rg)
check("prompt含评级变更门禁说明", "评级变更门禁" in rg)
check("prompt含研究链路7问", "研究链路要求" in rg and "传导机制" in rg)
check("回写在FAIL门禁else分支内", rg.find("update_thesis_status(report)") < rg.find("allocation_engine.update_allocation_status(report"))
check("校验分级FAIL禁止回写", 'classification == "FAIL"' in rg and "跳过thesis.json与allocation_views.json回写" in rg)

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
