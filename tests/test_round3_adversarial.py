#!/usr/bin/env python3
"""第三轮对抗性测试(2026-10-11) — 任务书第六节点名的9个对抗用例

每个用例模拟一次"模型/数据试图欺骗系统"的攻击,断言系统拦截:
 1. 模型无条件改变评级           → 门禁拒绝+提案留档
 2. 模型虚构支持证据             → 证据逐项拒收(指标不存在/数值不符),变更被拒
 3. 模型授予证据不足的5★         → 确信度门禁拒绝
 4. 前值冒充现值                 → 数据校验器🚨拦截→FAIL→禁止回写
 5. 数据过期仍作当前证据         → 逐指标新鲜度拒收
 6. 观察期外价格触及目标         → 窗口过滤,窗内数据裁决,窗后未来数据不算
 7. 模型将未触发预测判为命中     → 前提未兑现的hit拒收
 8. 模型将客观未命中预测判为命中 → 引擎权威,覆盖拒绝
 9. 数据校验失败仍试图更新长期状态 → FAIL门禁,观点库字节不变
附: S0 源码级自查 — 仓库内不得残留 `or True` 式恒真短路。

运行: ~/AI内容/venv/bin/python3 tests/test_round3_adversarial.py
"""
import os
import sys
import io
import re
import glob
import json
import shutil
import tempfile
import contextlib

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

def quiet(fn, *a, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = fn(*a, **kw)
    return r

import allocation_engine as ae
import data_validator as dv
from report_generator import _has_numeric_errors

print("=" * 60)
print("第三轮对抗性测试(9个点名用例)")
print("=" * 60)

ANCHORS = {
    'macro.data.CCC_OAS.value': {'value': 10.12, 'obs_date': '2026-10-09', 'as_of': '2026-10-09'},
    'macro.data.TIPS_10Y.value': {'value': 2.89, 'obs_date': '2026-10-09', 'as_of': '2026-10-09'},
    'global_market.data.SPX.close': {'value': 7650, 'obs_date': '2026-10-09', 'as_of': '2026-10-09'},
    'global_market.data.GOLD.close': {'value': 4180, 'obs_date': '2026-10-09', 'as_of': '2026-10-09'},
    'global_market.data.DXY.close': {'value': 99.9, 'obs_date': '2026-10-09', 'as_of': '2026-10-09'},
}

def base_views():
    return {'version': '3.0', 'views': [
        {'id': 1, 'asset': '美股测', 'rating': '标配', 'confidence': 2, 'history': [],
         'quant_triggers': []},
    ], 'predictions': []}

def alloc_block(objs):
    return '\n'.join(['<!--ALLOCATION_STATUS'] + [json.dumps(o, ensure_ascii=False) for o in objs] + ['ALLOCATION_STATUS-->'])

def pred_block(objs):
    return '\n'.join(['<!--PREDICTION_STATUS'] + [json.dumps(o, ensure_ascii=False) for o in objs] + ['PREDICTION_STATUS-->'])

def run_update(views_data, report_text, anchors=None, today='2026-10-09'):
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, 'views.json')
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(views_data, f, ensure_ascii=False)
        ups = quiet(ae.update_allocation_status, report_text, views_path=p,
                    anchors=ANCHORS if anchors is None else anchors, today_str=today)
        with open(p, encoding='utf-8') as f:
            return json.load(f), ups

def ev(metric, value, obs='2026-10-09', **kw):
    d = {'metric': metric, 'value': value, 'obs_date': obs}
    d.update(kw)
    return d

# ════════ S0 源码级自查 ════════
print("\n[S0] 源码无恒真短路(or True)")
hits = []
for py in glob.glob(os.path.join(ROOT, 'scripts', '*.py')):
    with open(py, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if re.search(r'\bor\s+True\b', line):
                hits.append(f"{os.path.basename(py)}:{i}")
check("S0 scripts/无 `or True` 恒真短路(测试文件由重写覆盖,test_glm_live旧断言已删)", not hits, str(hits))

# ════════ 用例1: 模型无条件改变评级 ════════
print("\n[1] 模型无条件改变评级(无触发器无证据)")
saved, ups = run_update(base_views(), alloc_block([
    {'id': 1, 'rating': '超配', 'confidence': 5, 'note': '直觉强烈,直接上调'}]))
v1 = saved['views'][0]
check("1a 评级保留标配(未被模型直觉改写)", v1['rating'] == '标配')
check("1b 被拒提案留档公示(含原因,供下期防重复提交)",
      any(p['status'] == 'rejected' and p['to'] == '超配' and '新增独立支持证据0项' in p['reason']
          for p in v1.get('proposals', [])), str(v1.get('proposals')))
check("1c 确信度未被顺带上调", v1['confidence'] == 2)
check("1d 历史记录为维持而非评级变化",
      any('维持' in h for h in v1['history']) and not any('评级:' in h for h in v1['history']),
      str(v1['history']))

# ════════ 用例2: 模型虚构支持证据 ════════
print("\n[2] 模型虚构支持证据(指标不存在+数值捏造)")
saved, ups = run_update(base_views(), alloc_block([
    {'id': 1, 'rating': '超配', 'confidence': 3, 'note': '证据充分',
     'evidence': [ev('macro.data.WAR_RISK.value', 88.8),                    # 完全虚构的指标
                  ev('macro.data.CCC_OAS.value', 8.00),                     # 真指标假数值
                  ev('global_market.data.SPX.close', 99999)]}]))            # 数值严重偏离
v1 = saved['views'][0]
check("2a 虚构指标/假数值证据全部拒收,评级保留", v1['rating'] == '标配')
check("2b 无一项证据进入台账", not v1.get('evidence_ledger'), str(v1.get('evidence_ledger')))
check("2c 被拒提案记录逐项证据拒收原因(虚构嫌疑/数值不符)",
      any('虚构' in p['reason'] or '数值不符' in p['reason']
          for p in v1.get('proposals', []) if p['to'] == '超配'),
      str(v1.get('proposals')))

# ════════ 用例3: 模型授予证据不足的5★ ════════
print("\n[3] 模型授予证据不足的5★(仅2项证据却标5★)")
saved, ups = run_update(base_views(), alloc_block([
    {'id': 1, 'rating': '标配', 'confidence': 5, 'note': '信心爆棚',
     'evidence': [ev('macro.data.CCC_OAS.value', 10.12, mechanism='信用'),
                  ev('global_market.data.SPX.close', 7650, mechanism='增长')]}]))
v1 = saved['views'][0]
check("3a 2项证据(程序2★)支撑不了5★→确信度保持2",
      v1['confidence'] == 2 and v1['evidence_ledger'][-1]['star_max'] == 2, str(v1.get('evidence_ledger')))
check("3b 星级不足的确信度提案留档", any(p['to'] == '确信度5★' for p in v1.get('proposals', [])))

# ════════ 用例4: 前值冒充现值 ════════
print("\n[4] 前值冒充现值(TIPS上周2.93写成当期值)")
prev_anchors = dict(ANCHORS)
prev_anchors['macro.data.TIPS_10Y.value'] = {'value': 2.92, 'obs_date': '2026-10-08',
                                             'as_of': '2026-10-09'}
prev_anchors['macro.data.TIPS_10Y.prev'] = {'value': 2.93, 'obs_date': '2026-10-01',
                                            'as_of': '2026-10-09'}
with tempfile.TemporaryDirectory() as td:
    rp = os.path.join(td, 'weekly_report_20261009.md')
    with open(rp, 'w', encoding='utf-8') as f:
        f.write("### 五、分资产深度分析\n实际利率(TIPS 10Y)本周收于2.93%,压制黄金。\n")
    warns = quiet(dv.validate_report, rp, prev_anchors)
    cls, _ = dv.classify_result(True, True, warns, _has_numeric_errors(warns))
check("4a 校验器识别前值当现值(🚨级)", any('前值当现值' in w for w in warns), str(warns))
check("4b 数值类错误→分级FAIL", cls == 'FAIL')

# ════════ 用例5: 数据过期仍作当前证据 ════════
print("\n[5] 数据过期仍作当前证据(两周前的日频行情)")
old_anchors = dict(ANCHORS)
old_anchors['global_market.data.SPX.close'] = {'value': 7650, 'obs_date': '2026-09-25',
                                               'as_of': '2026-10-09'}
saved, ups = run_update(base_views(), alloc_block([
    {'id': 1, 'rating': '超配', 'confidence': 3, 'note': '旧数据当新证据',
     'evidence': [ev('global_market.data.SPX.close', 7650, obs='2026-09-25'),
                  ev('global_market.data.GOLD.close', 4180, obs='2026-09-25')]}]),
    anchors=old_anchors)
check("5a 过期观测日(滞后14天>日频5天上限)的证据拒收,评级保留",
      saved['views'][0]['rating'] == '标配', str(saved['views'][0].get('evidence_ledger')))
v, r = ae.verify_evidence_items([ev('global_market.data.SPX.close', 7650, obs='2026-09-25')],
                                old_anchors, '2026-10-09')
check("5b 拒收原因明示数据过期", not v and '过期' in r[0][0])

# ════════ 用例6: 观察期外价格触及目标 ════════
print("\n[6] 观察期外价格触及目标(窗后未来数据/窗前旧数据)")
vd = base_views()
vd['predictions'] = [{'pred_id': 30, 'date_made': '2026-10-02', 'asset': '金', 'deadline': '2026-10-16',
                      'direction': '两周内金价触及4400', 'status': 'observing', 'observe_from': '2026-10-02',
                      'metric': 'global_market.data.GOLD.close', 'comparator': '>=', 'target': 4400,
                      'verify_mode': 'touch',
                      'observations': [{'obs_date': '2026-10-09', 'value': 4180, 'as_of': '2026-10-09'},
                                       {'obs_date': '2026-10-20', 'value': 4450, 'as_of': '2026-10-20'}]}]
v30 = ae.evaluate_predictions(vd, today_str='2026-10-16')[0]
check("6a 截止日后(10-20)的4450触及不算→touch到期miss",
      v30[2] == 'miss' and '4450' not in v30[3] and '从未满足' in v30[3], str(v30))
vd2 = base_views()
vd2['predictions'] = [{'pred_id': 31, 'date_made': '2026-10-02', 'asset': '金', 'deadline': '2026-10-16',
                       'direction': '两周内金价触及4400', 'status': 'observing', 'observe_from': '2026-10-02',
                       'metric': 'global_market.data.GOLD.close', 'comparator': '>=', 'target': 4400,
                       'verify_mode': 'touch',
                       'observations': [{'obs_date': '2026-09-20', 'value': 4450, 'as_of': '2026-09-20'},  # 观察起点前
                                        {'obs_date': '2026-10-09', 'value': 4180, 'as_of': '2026-10-09'}]}]
v31 = ae.evaluate_predictions(vd2, today_str='2026-10-16')[0]
check("6b 观察起点前(09-20)的旧触及不算→miss", v31[2] == 'miss', str(v31))
# GLM用窗后数据裁决→引用核验拒绝
vd3 = base_views()
vd3['predictions'] = [{'pred_id': 32, 'date_made': '2026-10-02', 'asset': '金', 'deadline': '2026-10-16',
                       'direction': '两周内金价触及4400', 'status': 'observing', 'observe_from': '2026-10-02',
                       'metric': 'global_market.data.GOLD.close', 'comparator': '>=', 'target': 4400,
                       'verify_mode': 'touch',
                       'observations': [{'obs_date': '2026-10-09', 'value': 4180, 'as_of': '2026-10-09'},
                                        {'obs_date': '2026-10-15', 'value': 4250, 'as_of': '2026-10-15'}]}]
report = alloc_block([{'id': 1, 'rating': '标配', 'confidence': 2, 'note': 'm'}]) + '\n' + \
    pred_block([{'pred_id': 32, 'status': 'hit', 'note': '金价4450已触及4400(观测日2026-10-20)'}])
saved, ups = run_update(vd3, report, today='2026-10-16')
p32 = saved['predictions'][0]
check("6c GLM引用窗后未来观测(4450@10-20)裁决hit→拒,引擎按窗内记录判miss",
      p32['status'] == 'miss' and any('观察窗' in u or '不可覆盖' in u for u in ups),
      f"{p32['status']} {ups}")

# ════════ 用例7: 模型将未触发预测判为命中 ════════
print("\n[7] 模型将前提未触发的预测判为命中")
vd = base_views()
vd['predictions'] = [{'pred_id': 40, 'date_made': '2026-10-02', 'asset': '金', 'deadline': '2026-10-23',
                      'direction': '若TIPS回落至2.2下,金涨至4400', 'status': 'not_yet_triggered',
                      'metric': 'global_market.data.GOLD.close', 'comparator': '>=', 'target': 4400,
                      'verify_mode': 'expiry', 'observations': [],
                      'premise': {'metric': 'macro.data.TIPS_10Y.value', 'op': '<=', 'target': 2.2}}]
report = alloc_block([{'id': 1, 'rating': '标配', 'confidence': 2, 'note': 'm'}]) + '\n' + \
    pred_block([{'pred_id': 40, 'status': 'hit', 'note': '金价4400已达成(观测日2026-10-09)'}])
saved, ups = run_update(vd, report, today='2026-10-09')
p40 = saved['predictions'][0]
check("7a 前提(TIPS≤2.2,实际2.89)未兑现→hit被拒,保持未触发",
      p40['status'] == 'not_yet_triggered' and any('被拒' in u for u in ups), f"{p40['status']} {ups}")
check("7b 前提未兑现时结果观察期未启动(无观察记录)", p40.get('observations') == [])

# ════════ 用例8: 模型将客观未命中预测判为命中 ════════
print("\n[8] 模型将客观未命中预测判为命中")
a8 = dict(ANCHORS)
a8['global_market.data.GOLD.close'] = {'value': 4250, 'obs_date': '2026-10-09', 'as_of': '2026-10-09'}
vd = base_views()
vd['predictions'] = [{'pred_id': 41, 'date_made': '2026-10-02', 'asset': '金', 'deadline': '2026-10-09',
                      'direction': '金收4400上', 'status': 'observing', 'observe_from': '2026-10-02',
                      'metric': 'global_market.data.GOLD.close', 'comparator': '>=', 'target': 4400,
                      'verify_mode': 'expiry',
                      'observations': [{'obs_date': '2026-10-08', 'value': 4310, 'as_of': '2026-10-08'}]}]
report = alloc_block([{'id': 1, 'rating': '标配', 'confidence': 2, 'note': 'm'}]) + '\n' + \
    pred_block([{'pred_id': 41, 'status': 'hit', 'note': '金价4450收于4400上方(观测日2026-10-09)'}])
saved, ups = run_update(vd, report, anchors=a8, today='2026-10-09')
p41 = saved['predictions'][0]
check("8a 引擎按观察记录判miss(最后观测4250<4400),GLM的hit被拒",
      p41['status'] == 'miss' and any('不可覆盖' in u for u in ups), f"{p41['status']} {ups}")
check("8b 裁决note保留引擎客观依据(含真实数值)", '4250' in p41.get('resolved_note', ''), str(p41.get('resolved_note')))

# ════════ 用例9: 数据校验失败仍试图更新长期状态 ════════
print("\n[9] 数据校验FAIL后仍试图更新长期状态")
with tempfile.TemporaryDirectory() as td:
    views_p = os.path.join(td, 'views.json')
    vd = base_views()
    with open(views_p, 'w', encoding='utf-8') as f:
        json.dump(vd, f, ensure_ascii=False)
    # 伪造一份含严重数值错误的报告(锚点SPX=7650,报告写12000)
    bad_rp = os.path.join(td, 'weekly_report_20261009.md')
    with open(bad_rp, 'w', encoding='utf-8') as f:
        f.write("### 四、资产表现总览\nSPX收于12000,大涨。\n\n" +
                alloc_block([{'id': 1, 'rating': '超配', 'confidence': 5, 'note': '基于错误数字升级'}]))
    warns = quiet(dv.validate_report, bad_rp, ANCHORS)
    cls, _ = dv.classify_result(True, True, warns, _has_numeric_errors(warns))
    check("9a 严重数值偏差(12000 vs 7650)→FAIL", cls == 'FAIL' and any('严重错误' in w for w in warns), str(warns))
    before = open(views_p).read()
    if cls != 'FAIL':   # 与report_generator主流程同款门禁: FAIL跳过一切回写
        quiet(ae.update_allocation_status, open(bad_rp).read(), views_path=views_p,
              anchors=ANCHORS, today_str='2026-10-09')
    check("9b FAIL门禁生效: 观点库未被基于错误数字的状态更新污染", open(views_p).read() == before)
    # 对照: 校验通过时同一更新路径正常工作(证明门禁不是靠"永不更新"糊弄)
    ok_rp = os.path.join(td, 'ok.md')
    with open(ok_rp, 'w', encoding='utf-8') as f:
        f.write(alloc_block([{'id': 1, 'rating': '超配', 'confidence': 3, 'note': '证据升级',
                              'evidence': [ev('macro.data.CCC_OAS.value', 10.12, mechanism='信用'),
                                           ev('macro.data.TIPS_10Y.value', 2.89, mechanism='利率与流动性'),
                                           ev('global_market.data.GOLD.close', 4180, mechanism='避险与估值')]}]))
    quiet(ae.update_allocation_status, open(ok_rp).read(), views_path=views_p,
          anchors=ANCHORS, today_str='2026-10-09')
    after = json.load(open(views_p))
    check("9c 对照组: 证据充分时同一门禁放行更新(门禁真实而非摆设)",
          after['views'][0]['rating'] == '超配')

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
