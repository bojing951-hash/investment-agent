#!/usr/bin/env python3
"""第四轮研究可靠性修复测试(2026-10-12) — 任务书第九节20项测试 + 四周端到端

每项断言都可证伪: 给定构造输入,断言引擎/校验器/回写器的确定性行为。
纯离线,不调用GLM(真实GLM冒烟单独由test_glm_live.py执行并单独统计)。
四周端到端使用同一份状态连续推进,不中途重新初始化。

运行: ~/AI内容/venv/bin/python3 tests/test_round4.py
"""
import os
import sys
import io
import json
import shutil
import tempfile
import contextlib
from datetime import date, datetime

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
from macro_collector import compute_series_changes
import report_generator as rg

print("=" * 60)
print("第四轮研究可靠性修复测试(20项 + 端到端)")
print("=" * 60)

# ════════ 公共fixture ════════
def anchors_at(day, **over):
    a = {
        'macro.data.CCC_OAS.value': {'value': 10.12, 'obs_date': day, 'as_of': day},
        'macro.data.CPI.value': {'value': 328.4, 'obs_date': '2026-09-15', 'as_of': day},
        'macro.data.TIPS_10Y.value': {'value': 2.89, 'obs_date': day, 'as_of': day},
        'macro.data.HY_OAS.value': {'value': 5.20, 'obs_date': day, 'as_of': day},
        'macro.data.IG_OAS.value': {'value': 1.42, 'obs_date': day, 'as_of': day},
        'global_market.data.GOLD.close': {'value': 4180, 'obs_date': day, 'as_of': day},
        'global_market.data.SPX.close': {'value': 7650, 'obs_date': day, 'as_of': day},
        'global_market.data.DXY.close': {'value': 99.9, 'obs_date': day, 'as_of': day},
    }
    a.update(over)
    return a

def status_block(rows, tag='THESIS_STATUS'):
    lines = [f'<!--{tag}']
    lines += [json.dumps(r, ensure_ascii=False) for r in rows]
    lines.append(f'{tag}-->')
    return '\n'.join(lines)

# ════════ 测试1: 同周重复运行10次只计1观察周 (P0-1) ════════
print("\n── 1. 同一ISO周重复运行10次,观察周只+1 (P0-1)")
views = {'views': [{'id': 1, 'quant_triggers': [
    {'trig_id': 'T1', 'direction': 'downgrade', 'metric': 'macro.data.CCC_OAS.value',
     'op': '>=', 'target': 10.0, 'sustain_weeks': 3}]}]}
# 2026-10-12(周一)~10-16(周五) 同属ISO 2026-W42,连跑10次
for i, d in enumerate(['2026-10-12', '2026-10-13', '2026-10-14', '2026-10-15', '2026-10-16',
                       '2026-10-12', '2026-10-14', '2026-10-16', '2026-10-13', '2026-10-15']):
    rows = quiet(ae.evaluate_quant_triggers, views, anchors_at(d), today_str=d, persist=True)
st = views['views'][0]['trigger_state']['T1']
check("同周10次运行后consec仍为1", st['consec'] == 1, str(st))
check("同周10次运行status为sustaining(3周条件未满)",
      rows[1][0]['status'] == 'sustaining', str(rows[1][0]))

# ════════ 测试2: 连续三个有效ISO周才触发三周条件 (P0-1) ════════
print("\n── 2. 连续三个有效ISO周才触发三周条件 (P0-1)")
views2 = {'views': [{'id': 1, 'quant_triggers': [
    {'trig_id': 'T1', 'direction': 'downgrade', 'metric': 'macro.data.CCC_OAS.value',
     'op': '>=', 'target': 10.0, 'sustain_weeks': 3}]}]}
W1, W2, W3, W4 = '2026-10-09', '2026-10-16', '2026-10-23', '2026-10-30'  # W41~W44连续
r1 = quiet(ae.evaluate_quant_triggers, views2, anchors_at(W1), today_str=W1, persist=True)[1]
r2 = quiet(ae.evaluate_quant_triggers, views2, anchors_at(W2), today_str=W2, persist=True)[1]
r3 = quiet(ae.evaluate_quant_triggers, views2, anchors_at(W3), today_str=W3, persist=True)[1]
check("第1周: 连续第1周(持续确认中)", r1[0]['consec'] == 1 and r1[0]['status'] == 'sustaining', str(r1[0]))
check("第2周: 连续第2周(仍未触发)", r2[0]['consec'] == 2 and r2[0]['status'] == 'sustaining', str(r2[0]))
check("第3周: 连续第3周→已触发", r3[0]['consec'] == 3 and r3[0]['status'] == 'triggered', str(r3[0]))
# 中途数据缺失一周(W44无数据): 不推进不重置; 条件明确不满足→清零
r4 = quiet(ae.evaluate_quant_triggers, views2, anchors_at(
    W4, **{'macro.data.CCC_OAS.value': None}), today_str=W4, persist=True)[1]
check("第4周数据缺失: 不推进不重置(连续周数保持3)", r4[0]['consec'] == 3 and r4[0]['status'] == 'unverifiable', str(r4[0]))
r5 = quiet(ae.evaluate_quant_triggers, views2, anchors_at(
    W4, **{'macro.data.CCC_OAS.value': {'value': 9.2, 'obs_date': W4, 'as_of': W4}}),
    today_str=W4, persist=True)[1]
check("第4周条件明确不满足→清零重新起算", r5[0]['consec'] == 0 and r5[0]['status'] == 'not_triggered', str(r5[0]))

# ════════ 测试3: 跨年ISO周 (P0-1) ════════
print("\n── 3. 跨年ISO周正确(2026-W53→2027-W01连续,跳到W02重置)")
# 2026-12-31属ISO 2026-W53; 2027-01-08属ISO 2027-W01 (跨年相邻周)
check("_prev_iso_week(2027-W01)==2026-W53",
      ae._prev_iso_week(ae._iso_week_key('2027-01-08')) == ae._iso_week_key('2026-12-31'),
      f"{ae._prev_iso_week(ae._iso_week_key('2027-01-08'))} vs {ae._iso_week_key('2026-12-31')}")
views3 = {'views': [{'id': 1, 'quant_triggers': [
    {'trig_id': 'T1', 'direction': 'downgrade', 'metric': 'macro.data.CCC_OAS.value',
     'op': '>=', 'target': 10.0, 'sustain_weeks': 3}]}]}
quiet(ae.evaluate_quant_triggers, views3, anchors_at('2026-12-25'), today_str='2026-12-25', persist=True)  # W52
r2 = quiet(ae.evaluate_quant_triggers, views3, anchors_at('2026-12-31'), today_str='2026-12-31', persist=True)[1]  # W53
r3 = quiet(ae.evaluate_quant_triggers, views3, anchors_at('2027-01-08'), today_str='2027-01-08', persist=True)[1]  # 2027-W01
check("2026-W52→2026-W53→2027-W01跨年连续(consec=3)",
      r3[0]['consec'] == 3 and r3[0]['status'] == 'triggered', str(r3[0]))
views4 = {'views': [{'id': 1, 'quant_triggers': [
    {'trig_id': 'T1', 'direction': 'downgrade', 'metric': 'macro.data.CCC_OAS.value',
     'op': '>=', 'target': 10.0, 'sustain_weeks': 3}]}]}
quiet(ae.evaluate_quant_triggers, views4, anchors_at('2026-12-31'), today_str='2026-12-31', persist=True)
r5 = quiet(ae.evaluate_quant_triggers, views4, anchors_at('2027-01-15'), today_str='2027-01-15', persist=True)[1]
check("跳过2027-W01直接到W02→重置为1(中间观察周缺失不得自动认定连续)",
      r5[0]['consec'] == 1 and r5[0]['status'] == 'sustaining', str(r5[0]))

# ════════ 测试4: 重复证据不能触发评级变化 (P0-2) ════════
print("\n── 4. 同一底层指标衍生值(.value+.prev)不得算2项独立证据")
with tempfile.TemporaryDirectory() as td:
    vp = os.path.join(td, 'allocation_views.json')
    views5 = {'version': '4.0', 'last_updated': '2026-10-02', 'views': [
        {'id': 1, 'asset': '美股', 'rating': '标配', 'confidence': 2, 'history': [],
         'quant_triggers': [], 'key_metrics': []}]}
    json.dump(views5, open(vp, 'w'), ensure_ascii=False)
    day = '2026-10-12'
    dup_ev = [
        {'metric': 'macro.data.CCC_OAS.value', 'value': 10.12, 'obs_date': day, 'mechanism': '信用'},
        {'metric': 'macro.data.CCC_OAS.prev', 'value': 10.02, 'obs_date': day, 'mechanism': '信用'},
    ]
    report = status_block([{'id': 1, 'rating': '低配', 'confidence': 2,
                            'note': '重复证据', 'evidence': dup_ev}], 'ALLOCATION_STATUS')
    quiet(ae.update_allocation_status, report, views_path=vp,
          anchors=anchors_at(day), today_str=day)
    saved = json.load(open(vp))
    v1 = saved['views'][0]
    check("评级维持标配(同基底指标只计1项,不满足≥2项新增门禁)", v1['rating'] == '标配', v1['rating'])
    check("被拒提案留档", any(p.get('status') == 'rejected' for p in v1.get('proposals', [])))
    star, _ = ae.star_level_from_evidence(quiet(ae.verify_evidence_items, dup_ev, anchors_at(day), day)[0])
    check("程序星级仅1★(按底层指标去重)", star == 1, f"star={star}")

# ════════ 测试5: 反对证据不能增加支持数量 (P0-2) ════════
print("\n── 5. 反对证据(contrary)不计入支持数量/升级门槛")
day = '2026-10-12'
ev = [
    {'metric': 'macro.data.CCC_OAS.value', 'value': 10.12, 'obs_date': day, 'mechanism': '信用'},
    {'metric': 'macro.data.HY_OAS.value', 'value': 5.20, 'obs_date': day, 'mechanism': '信用', 'contrary': True},
]
verified, _ = quiet(ae.verify_evidence_items, ev, anchors_at(day), day)
supporting, contrary, unexplained, neutral_ev = ae.split_evidence_direction(verified)
check("支持证据=1项,反对证据=1项", len(supporting) == 1 and len(contrary) == 1)
check("new_supporting_metrics不含反对证据",
      'macro.data.HY_OAS' not in ae.new_supporting_metrics({'views': []} if False else {}, supporting, day))
with tempfile.TemporaryDirectory() as td:
    vp = os.path.join(td, 'allocation_views.json')
    views6 = {'version': '4.0', 'views': [
        {'id': 1, 'asset': '美股', 'rating': '标配', 'confidence': 2, 'history': [],
         'quant_triggers': [], 'key_metrics': []}]}
    json.dump(views6, open(vp, 'w'), ensure_ascii=False)
    report = status_block([{'id': 1, 'rating': '低配', 'confidence': 2,
                            'note': '1支持+1反对凑数', 'evidence': ev}], 'ALLOCATION_STATUS')
    quiet(ae.update_allocation_status, report, views_path=vp,
          anchors=anchors_at(day), today_str=day)
    v1 = json.load(open(vp))['views'][0]
    check("1项支持+1项反对不能过≥2项新增门禁,评级维持", v1['rating'] == '标配', v1['rating'])

# ════════ 测试6: 旧证据不能冒充新增 (P0-2) ════════
print("\n── 6. 同一指标旧值再次引用不算新增(第二周重引同观测日)")
with tempfile.TemporaryDirectory() as td:
    vp = os.path.join(td, 'allocation_views.json')
    views7 = {'version': '4.0', 'views': [
        {'id': 1, 'asset': '美股', 'rating': '标配', 'confidence': 2, 'history': [],
         'quant_triggers': [], 'key_metrics': []}]}
    json.dump(views7, open(vp, 'w'), ensure_ascii=False)
    d1, d2 = '2026-10-05', '2026-10-12'
    ev = [{'metric': 'macro.data.CCC_OAS.value', 'value': 10.12, 'obs_date': '2026-10-05', 'mechanism': '信用'},
          {'metric': 'macro.data.HY_OAS.value', 'value': 5.20, 'obs_date': '2026-10-05', 'mechanism': '信用'}]
    rep = status_block([{'id': 1, 'rating': '低配', 'confidence': 3,
                         'note': 'w1', 'evidence': ev}], 'ALLOCATION_STATUS')
    quiet(ae.update_allocation_status, rep, views_path=vp, anchors=anchors_at(d1), today_str=d1)
    v1 = json.load(open(vp))['views'][0]
    check("第一周2项新增证据→评级变更通过", v1['rating'] == '低配', v1['rating'])
    # 第二周: 本周未发布新一期,锚点观测日仍是10-05(7天内仍新鲜),同观测日旧值再次引用
    anch_old = anchors_at(d2, **{
        'macro.data.CCC_OAS.value': {'value': 10.12, 'obs_date': '2026-10-05', 'as_of': d2},
        'macro.data.HY_OAS.value': {'value': 5.20, 'obs_date': '2026-10-05', 'as_of': d2}})
    rep2 = status_block([{'id': 1, 'rating': '超配', 'confidence': 3,
                          'note': 'w2重引旧值', 'evidence': ev}], 'ALLOCATION_STATUS')
    quiet(ae.update_allocation_status, rep2, views_path=vp, anchors=anch_old, today_str=d2)
    v1b = json.load(open(vp))['views'][0]
    check("第二周旧值重引→新增0项,反向变更被拒,维持低配", v1b['rating'] == '低配', v1b['rating'])
    # 但新一期观测(新obs_date)算新增
    ev3 = [{'metric': 'macro.data.CCC_OAS.value', 'value': 10.12, 'obs_date': '2026-10-09', 'mechanism': '信用'},
           {'metric': 'macro.data.HY_OAS.value', 'value': 5.20, 'obs_date': '2026-10-09', 'mechanism': '信用'}]
    anch_new = anchors_at(d2, **{
        'macro.data.CCC_OAS.value': {'value': 10.12, 'obs_date': '2026-10-09', 'as_of': d2},
        'macro.data.HY_OAS.value': {'value': 5.20, 'obs_date': '2026-10-09', 'as_of': d2}})
    rep3 = status_block([{'id': 1, 'rating': '超配', 'confidence': 3,
                          'note': 'w2新一期数据', 'evidence': ev3}], 'ALLOCATION_STATUS')
    quiet(ae.update_allocation_status, rep3, views_path=vp, anchors=anch_new, today_str=d2)
    v1c = json.load(open(vp))['views'][0]
    check("同一指标新一期观测日算新增信息→变更通过", v1c['rating'] == '超配', v1c['rating'])

# ════════ 测试7: 月度CPI不受7天规则 (P0-3) ════════
print("\n── 7. 月频CPI观测日30天前仍新鲜(按发布周期+滞后)")
a = {'macro.data.CPI.value': {'value': 328.4, 'obs_date': '2026-09-15', 'as_of': '2026-10-12'}}
check("CPI(月频)30天前观测→新鲜",
      dv.is_fresh_anchor('macro.data.CPI.value', a['macro.data.CPI.value'], '2026-10-12') is True)
a2 = {'macro.data.CPI.value': {'value': 328.4, 'obs_date': '2026-08-10', 'as_of': '2026-10-12'}}
check("CPI观测超过月度窗口(63天)→过期",
      dv.is_fresh_anchor('macro.data.CPI.value', a2['macro.data.CPI.value'], '2026-10-12') is False)
a3 = {'macro.data.ICSA.value': {'value': 221000, 'obs_date': '2026-10-08', 'as_of': '2026-10-12'}}
check("周频ICSA 4天前观测→新鲜",
      dv.is_fresh_anchor('macro.data.ICSA.value', a3['macro.data.ICSA.value'], '2026-10-12') is True)

# ════════ 测试8: 缺失观测日期不能默认通过新鲜度 (P0-3) ════════
print("\n── 8. 缺失/非法观测日期→不得默认新鲜")
check("无obs_date→不新鲜", dv.is_fresh_anchor('macro.data.CCC_OAS.value',
      {'value': 10.12, 'as_of': '2026-10-12'}, '2026-10-12') is False)
check("非法obs_date→不新鲜", dv.is_fresh_anchor('macro.data.CCC_OAS.value',
      {'value': 10.12, 'obs_date': 'not-a-date', 'as_of': '2026-10-12'}, '2026-10-12') is False)
check("未来obs_date→不新鲜(进待验证)", dv.is_fresh_anchor('macro.data.CCC_OAS.value',
      {'value': 10.12, 'obs_date': '2026-10-20', 'as_of': '2026-10-12'}, '2026-10-12') is False)
# 缺观测日期的证据项: 第五轮P0-3收紧 — obs_date必填,缺失整项拒收,
# 不得省略后由程序以锚点观测日补全(日期引用是模型责任)
day = '2026-10-12'
ev = [{'metric': 'macro.data.CCC_OAS.value', 'value': 10.12, 'mechanism': '信用'}]
verified, rejects = quiet(ae.verify_evidence_items, ev, anchors_at(day), day)
check("缺obs_date的证据项整项拒收(第五轮P0-3收紧,不再程序补全)",
      len(verified) == 0 and len(rejects) == 1 and '缺obs_date' in rejects[0][0],
      f"{verified} {rejects}")
ev2 = [{'metric': 'macro.data.CCC_OAS.value', 'value': 10.12, 'obs_date': '2026-10-11', 'mechanism': '信用'}]
v2, r2 = quiet(ae.verify_evidence_items, ev2, anchors_at(day), day)
check("模型自称观测日与锚点不符→拒", len(v2) == 0 and '观测日不符' in r2[0][0], f"{v2} {r2}")

# ════════ 测试9: FRED月频不能以五观测值之差冒充周变化 (P0-3) ════════
print("\n── 9. 月频序列只产mom/yoy变化,不产伪week_chg")
m_dates = ['2025-09-15', '2026-06-15', '2026-07-15', '2026-08-15', '2026-09-15', '2026-10-15']
m_vals = [313.0, 320.0, 321.5, 323.0, 326.0, 328.4]
out = compute_series_changes(m_dates, m_vals, 'monthly')
check("月频无week_chg字段", 'week_chg' not in out, str(out.keys()))
check("月频有mom_chg且带起始观测日", 'mom_chg' in out and out.get('mom_chg_from') == '2026-09-15')
check("月频有同比变化(起始观测日=约12个月前)", 'yoy_chg' in out and out.get('yoy_chg_from') == '2025-09-15')
check("mom_chg公式=最新-上期(328.4-326.0=2.4)", abs(out['mom_chg'] - 2.4) < 1e-6, str(out.get('mom_chg')))
d_dates = ['2026-10-02', '2026-10-05', '2026-10-08', '2026-10-09', '2026-10-12']
d_vals = [10.02, 10.04, 10.08, 10.09, 10.12]
outd = compute_series_changes(d_dates, d_vals, 'daily')
check("日频week_chg=最新-约一周前观测(10.12-10.05=0.08,窗口5~10自然日取最近)",
      abs(outd['week_chg'] - 0.08) < 1e-6, str(outd))
check("日频week_chg带起始观测日", outd.get('week_chg_from') == '2026-10-05')

# ════════ 测试10: 宏观论点不能绕过证据分级上调5★ (P0-4) ════════
print("\n── 10. 论点确信度上调须过证据分级(无证据→5★被拒)")
with tempfile.TemporaryDirectory() as td:
    tp = os.path.join(td, 'thesis.json')
    shutil.copy(os.path.join(ROOT, 'config', 'thesis.json'), tp)
    day = '2026-10-12'
    rep = status_block([{'id': 5, 'status': '待观察', 'confidence': 5, 'note': '模型自称确信'}])
    quiet(rg.update_thesis_status, rep, thesis_path=tp, anchors=anchors_at(day), today_str=day)
    t5 = [t for t in json.load(open(tp))['theses'] if t['id'] == 5][0]
    check("无证据上调5★被拒(维持2★)", t5['confidence'] == 2, str(t5['confidence']))
    check("确信度提案留档", any('确信度' in str(p.get('to', '')) for p in t5.get('proposals', [])))
    # 终态判定同样不能绕过: 已验证无触发器/无新增证据→拒
    rep2 = status_block([{'id': 5, 'status': '已验证', 'confidence': 2, 'note': '模型宣判'}])
    quiet(rg.update_thesis_status, rep2, thesis_path=tp, anchors=anchors_at(day), today_str=day)
    t5b = [t for t in json.load(open(tp))['theses'] if t['id'] == 5][0]
    check("无触发器/新增证据的'已验证'被拒,保留待观察", t5b['status'] == '待观察', t5b['status'])

# ════════ 测试11: 无重大反证时满足条件仍允许5★ (P0-5) ════════
print("\n── 11. 5项/3类机制/跨3观察期且无反证→允许5★(不要求存在反证)")
# 混频构造: 日频(本周)/周频(16天内)/月频(45天内)各在其新鲜度窗口内,
# 跨3个ISO观察期(09-15=月度观测 / 09-26=周度观测 / 10-12=当日)
ev = [
    {'metric': 'macro.data.CCC_OAS.value', 'value': 10.12, 'obs_date': '2026-10-09', 'mechanism': '信用'},
    {'metric': 'macro.data.HY_OAS.value', 'value': 5.20, 'obs_date': '2026-10-09', 'mechanism': '信用'},
    {'metric': 'macro.data.TIPS_10Y.value', 'value': 2.89, 'obs_date': '2026-10-09', 'mechanism': '利率与流动性'},
    {'metric': 'macro.data.ICSA.value', 'value': 221000, 'obs_date': '2026-09-26', 'mechanism': '增长'},
    {'metric': 'macro.data.CPI.value', 'value': 328.4, 'obs_date': '2026-09-15', 'mechanism': '通胀'},
]
multi = {
    'macro.data.CCC_OAS.value': {'value': 10.12, 'obs_date': '2026-10-09', 'as_of': '2026-10-12'},
    'macro.data.HY_OAS.value': {'value': 5.20, 'obs_date': '2026-10-09', 'as_of': '2026-10-12'},
    'macro.data.TIPS_10Y.value': {'value': 2.89, 'obs_date': '2026-10-09', 'as_of': '2026-10-12'},
    'macro.data.ICSA.value': {'value': 221000, 'obs_date': '2026-09-26', 'as_of': '2026-10-12'},
    'macro.data.CPI.value': {'value': 328.4, 'obs_date': '2026-09-15', 'as_of': '2026-10-12'},
    'macro.data.IG_OAS.value': {'value': 1.42, 'obs_date': '2026-10-09', 'as_of': '2026-10-12'},
}
verified, _ = quiet(ae.verify_evidence_items, ev, multi, '2026-10-12')
star, desc = ae.star_level_from_evidence(verified)
check("5项3类3观察期无反证→5★", star == 5, f"star={star} {desc}")
# 该证据也可支撑论点确信度上调到5
with tempfile.TemporaryDirectory() as td:
    tp = os.path.join(td, 'thesis.json')
    shutil.copy(os.path.join(ROOT, 'config', 'thesis.json'), tp)
    rep = status_block([{'id': 5, 'status': '待观察', 'confidence': 5,
                         'note': '5项独立证据', 'evidence': ev}])
    quiet(rg.update_thesis_status, rep, thesis_path=tp, anchors=multi, today_str='2026-10-12')
    t5 = [t for t in json.load(open(tp))['theses'] if t['id'] == 5][0]
    check("证据充分的5★上调被接受", t5['confidence'] == 5, str(t5['confidence']))

# ════════ 测试12: 重大反证未解决时执行星级限制 (P0-5) ════════
print("\n── 12. 存在未解释重大反证→封顶3★")
ev_c = ev + [{'metric': 'macro.data.IG_OAS.value', 'value': 1.42,
              'obs_date': '2026-10-09', 'mechanism': '信用', 'contrary': True}]
verified, _ = quiet(ae.verify_evidence_items, ev_c, multi, '2026-10-12')
star2, _ = ae.star_level_from_evidence(verified)
check("同上证据+未解释反证→封顶3★", star2 == 3, f"star={star2}")
# 反证被解释(explained=true)不触发封顶
ev_e = ev + [{'metric': 'macro.data.IG_OAS.value', 'value': 1.42,
              'obs_date': '2026-10-09', 'mechanism': '信用', 'contrary': True, 'explained': True}]
verified3, _ = quiet(ae.verify_evidence_items, ev_e, multi, '2026-10-12')
star3, _ = ae.star_level_from_evidence(verified3)
check("反证已解释→不封顶(仍5★)", star3 == 5, f"star={star3}")
with tempfile.TemporaryDirectory() as td:
    tp = os.path.join(td, 'thesis.json')
    shutil.copy(os.path.join(ROOT, 'config', 'thesis.json'), tp)
    rep = status_block([{'id': 5, 'status': '待观察', 'confidence': 5,
                         'note': '有未解释反证', 'evidence': ev_c}])
    quiet(rg.update_thesis_status, rep, thesis_path=tp, anchors=multi, today_str='2026-10-12')
    t5 = [t for t in json.load(open(tp))['theses'] if t['id'] == 5][0]
    check("论点确信度上调超过封顶星级→整笔被拒(维持2★,不静默改判3★)",
          t5['confidence'] == 2 and any('确信度' in str(pr.get('to', '')) for pr in t5.get('proposals', [])),
          str(t5['confidence']))

# ════════ 测试13: 黄金周二盘中触及周五回落 touch仍正确 (P0-6) ════════
print("\n── 13. touch模式: 周二盘中high触及,周五回落→仍hit")
pred = {'pred_id': 21, 'view_id': 5, 'metric': 'global_market.data.GOLD.close',
        'comparator': '>=', 'target': 4300.0, 'verify_mode': 'touch', 'price_basis': 'high',
        'date_made': '2026-10-05', 'observe_from': '2026-10-05', 'deadline': '2026-10-16',
        'status': 'observing', 'text': '黄金两周内盘中触及4300',
        'observations': [
            {'obs_date': '2026-10-05', 'value': 4250.0, 'high': 4262.0, 'low': 4241.0},
            {'obs_date': '2026-10-06', 'value': 4280.0, 'high': 4310.0, 'low': 4270.0},   # 周二盘中触及
            {'obs_date': '2026-10-09', 'value': 4255.0, 'high': 4284.0, 'low': 4249.0},   # 周五回落
        ]}
v = quiet(ae.evaluate_predictions, {'predictions': [dict(pred)]}, today_str='2026-10-07')
check("观察期内(10-07)提前hit(10-06盘中high 4310≥4300)",
      v and v[0][2] == 'hit' and '2026-10-06' in v[0][3], str(v))
v2 = quiet(ae.evaluate_predictions, {'predictions': [dict(pred)]}, today_str='2026-10-16')
check("到期日(10-16)裁决仍hit,周五回落不推翻盘中触及",
      v2 and v2[0][2] == 'hit' and v2[0][3].find('触及') >= 0, str(v2))
# 反例: 全窗口盘中从未触及(有完整high数据)→miss
# 第五轮P0-2: 判miss须窗口覆盖充分 — 补齐10-05~10-16全部10个交易日观测
pred_no = dict(pred)
pred_no['observations'] = [
    {'obs_date': '2026-10-05', 'value': 4250.0, 'high': 4262.0, 'low': 4241.0},
    {'obs_date': '2026-10-06', 'value': 4280.0, 'high': 4295.0, 'low': 4270.0},
    {'obs_date': '2026-10-07', 'value': 4260.0, 'high': 4275.0, 'low': 4252.0},
    {'obs_date': '2026-10-08', 'value': 4270.0, 'high': 4288.0, 'low': 4261.0},
    {'obs_date': '2026-10-09', 'value': 4255.0, 'high': 4284.0, 'low': 4249.0},
    {'obs_date': '2026-10-12', 'value': 4240.0, 'high': 4256.0, 'low': 4233.0},
    {'obs_date': '2026-10-13', 'value': 4245.0, 'high': 4260.0, 'low': 4238.0},
    {'obs_date': '2026-10-14', 'value': 4250.0, 'high': 4268.0, 'low': 4242.0},
    {'obs_date': '2026-10-15', 'value': 4248.0, 'high': 4264.0, 'low': 4240.0},
    {'obs_date': '2026-10-16', 'value': 4252.0, 'high': 4270.0, 'low': 4245.0},
]
v3 = quiet(ae.evaluate_predictions, {'predictions': [pred_no]}, today_str='2026-10-16')
check("有完整high数据+窗口覆盖充分且从未盘中触及→miss(可证明)",
      v3 and v3[0][2] == 'miss', str(v3))
# 第五轮P0-2反例: 同样从未触及,但只取得3个交易日观测→覆盖不足,不得判miss
pred_sparse = dict(pred_no)
pred_sparse['observations'] = pred_sparse['observations'][:3]
v3s = quiet(ae.evaluate_predictions, {'predictions': [pred_sparse]}, today_str='2026-10-16')
check("仅3个交易日观测(缺7天)→覆盖不足inconclusive,不判miss",
      v3s and v3s[0][2] == 'inconclusive' and '覆盖不足' in v3s[0][3], str(v3s))

# ════════ 测试14: 只有收盘价不能证明盘中未触及 (P0-6) ════════
print("\n── 14. 只有收盘价(无盘中high/low)→high口径不判miss")
pred_only_close = dict(pred)
pred_only_close['observations'] = [
    {'obs_date': '2026-10-05', 'value': 4250.0},
    {'obs_date': '2026-10-06', 'value': 4280.0},
    {'obs_date': '2026-10-09', 'value': 4255.0},
]
v4 = quiet(ae.evaluate_predictions, {'predictions': [pred_only_close]}, today_str='2026-10-16')
check("缺盘中数据→inconclusive不判miss",
      v4 and v4[0][2] == 'inconclusive' and '无法证明盘中未触及' in v4[0][3], str(v4))
# close口径不受影响: 收盘价数据完整(第五轮P0-2: 仍须窗口覆盖充分)即可判
pred_close_basis = dict(pred)
pred_close_basis['price_basis'] = 'close'
pred_close_basis['comparator'] = '>='
pred_close_basis['target'] = 4300.0
pred_close_basis['observations'] = [dict(o) for o in pred_no['observations']]
v5 = quiet(ae.evaluate_predictions, {'predictions': [pred_close_basis]}, today_str='2026-10-16')
check("close口径只看收盘价(全程<4300且覆盖充分→miss)",
      v5 and v5[0][2] == 'miss', str(v5))

# ════════ 测试15: 观察期外数据必须拒绝 (P0-6) ════════
print("\n── 15. 观察窗外的观测不得用于裁决")
pred_out = dict(pred)
pred_out['verify_mode'] = 'expiry'
pred_out['price_basis'] = 'close'
pred_out['observe_from'] = '2026-10-05'
pred_out['deadline'] = '2026-10-09'
pred_out['observations'] = [
    {'obs_date': '2026-10-02', 'value': 4350.0},   # 窗口前(达标也不算)
    {'obs_date': '2026-10-08', 'value': 4250.0},   # 窗口内
]
v6 = quiet(ae.evaluate_predictions, {'predictions': [pred_out]}, today_str='2026-10-09')
check("窗口前4350≥4300不得判hit,按窗口内10-08收盘判miss",
      v6 and v6[0][2] == 'miss' and '4350' not in v6[0][3], str(v6))
pred_fut = dict(pred_out)
pred_fut['observations'] = [{'obs_date': '2026-10-08', 'value': 4250.0},
                            {'obs_date': '2026-10-15', 'value': 4360.0}]  # 截止日后
v7 = quiet(ae.evaluate_predictions, {'predictions': [pred_fut]}, today_str='2026-10-09')
check("截止日后的数据不得用于裁决(仍按10-08判miss)",
      v7 and v7[0][2] == 'miss', str(v7))

# ════════ 测试16: GLM虚构数字不能覆盖程序裁决 (P0-6) ════════
print("\n── 16. GLM引用观察记录中不存在的数值→裁决被拒")
with tempfile.TemporaryDirectory() as td:
    vp = os.path.join(td, 'allocation_views.json')
    data = {'version': '4.0', 'views': [
        {'id': 5, 'asset': '贵金属', 'rating': '标配', 'confidence': 2, 'history': [],
         'quant_triggers': [], 'key_metrics': []}],
        'predictions': [dict(pred, verify_mode='expiry', price_basis='close',
                             deadline='2026-10-09')]}
    json.dump(data, open(vp, 'w'), ensure_ascii=False)
    rep = (status_block([{'id': 5, 'rating': '标配', 'confidence': 2, 'note': '维持'}],
                        'ALLOCATION_STATUS')
           + '\n' + status_block([{'pred_id': 21, 'status': 'hit',
                                   'note': 'GOLD 4350>=4300(观测日2026-10-08)'}],
                                 'PREDICTION_STATUS'))
    quiet(ae.update_allocation_status, rep, views_path=vp,
          anchors=anchors_at('2026-10-12'), today_str='2026-10-12')
    p21 = json.load(open(vp))['predictions'][0]
    check("观察记录只有4250,GLM的4350为虚构→hit被拒,引擎miss生效",
          p21['status'] == 'miss', str(p21.get('status')) + ' ' + str(p21.get('note', ''))[:80])

# ════════ 测试17: 缺观察数据标无法裁决 (P0-6) ════════
print("\n── 17. 到期但无观察记录→inconclusive(不硬判)")
pred_nodata = dict(pred)
pred_nodata['verify_mode'] = 'expiry'
pred_nodata['price_basis'] = 'close'
pred_nodata['deadline'] = '2026-10-09'
pred_nodata['observations'] = []
v8 = quiet(ae.evaluate_predictions, {'predictions': [pred_nodata]}, today_str='2026-10-12')
check("无观察数据→inconclusive", v8 and v8[0][2] == 'inconclusive', str(v8))
# 定性预测(无可计算规格)只能研究性回顾,不得hit/miss
pred_qual = dict(pred)
del pred_qual['metric'], pred_qual['comparator'], pred_qual['target']
pred_qual['text'] = '黄金将因避险需求走强'
v9 = quiet(ae.evaluate_predictions, {'predictions': [pred_qual]}, today_str='2026-10-16')
check("定性预测不进客观裁决(引擎不判hit/miss)", not v9 or all(x[2] not in ('hit', 'miss') for x in v9), str(v9))
pred_qual_resolved = dict(pred_qual)
pred_qual_resolved.update({'status': 'inconclusive', 'resolved_date': '2026-10-16'})  # 研究性回顾落定
counts = quiet(ae.predictions_in_period,
               {'predictions': [pred_qual_resolved]}, '2026-10-01', '2026-10-31')
check("定性预测单独计数(qualitative),不计入hit/miss",
      counts['counts'].get('qualitative') == 1 and counts['counts'].get('hit', 0) == 0, str(counts))

# ════════ 测试18: 同批数据重复运行不重复增加观察记录 (P0-6) ════════
print("\n── 18. record_observations幂等(同批锚点重跑不加记录)")
views_obs = {'version': '4.0', 'views': [], 'predictions': [
    {'pred_id': 31, 'view_id': 5, 'metric': 'global_market.data.GOLD.close',
     'comparator': '>=', 'target': 4300.0, 'verify_mode': 'touch', 'price_basis': 'high',
     'date_made': '2026-10-05', 'deadline': '2026-10-30', 'status': 'observing',
     'observations': []}]}
anch = anchors_at('2026-10-12',
                  **{'global_market.data.GOLD.close': {'value': 4260.0, 'obs_date': '2026-10-12', 'as_of': '2026-10-12'},
                     'global_market.data.GOLD.high': {'value': 4272.0, 'obs_date': '2026-10-12', 'as_of': '2026-10-12'},
                     'global_market.data.GOLD.low': {'value': 4248.0, 'obs_date': '2026-10-12', 'as_of': '2026-10-12'}})
quiet(ae.record_observations, views_obs, anch, '2026-10-12')
n1 = len(views_obs['predictions'][0]['observations'])
quiet(ae.record_observations, views_obs, anch, '2026-10-12')   # 同批重跑
n2 = len(views_obs['predictions'][0]['observations'])
check("同批锚点重跑记录数不变", n1 == 1 and n2 == 1, f"{n1}->{n2}")
check("观察记录带盘中高低与来源", all(
    k in views_obs['predictions'][0]['observations'][0] for k in ('value', 'high', 'low', 'obs_date')), str(views_obs['predictions'][0]['observations']))
quiet(ae.record_observations, views_obs, anchors_at(
    '2026-10-13', **{'global_market.data.GOLD.close': {'value': 4255.0, 'obs_date': '2026-10-13', 'as_of': '2026-10-13'},
                     'global_market.data.GOLD.high': {'value': 4266.0, 'obs_date': '2026-10-13', 'as_of': '2026-10-13'},
                     'global_market.data.GOLD.low': {'value': 4250.0, 'obs_date': '2026-10-13', 'as_of': '2026-10-13'}}),
    '2026-10-13')
n3 = len(views_obs['predictions'][0]['observations'])
check("新一观测日新增记录(不因幂等而丢数据)", n3 == 2, f"n3={n3}")

# ════════ 测试19: 数据验证失败不污染两个长期状态文件 (P0-4) ════════
print("\n── 19. 校验分级FAIL→thesis.json与allocation_views.json都不修改")
with tempfile.TemporaryDirectory() as td:
    tp = os.path.join(td, 'thesis.json')
    vp = os.path.join(td, 'allocation_views.json')
    shutil.copy(os.path.join(ROOT, 'config', 'thesis.json'), tp)
    shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), vp)
    before_t = open(tp, 'rb').read()
    before_v = open(vp, 'rb').read()
    rep = (status_block([{'id': 2, 'status': '已失效', 'confidence': 1, 'note': 'FAIL周不得回写'}])
           + '\n' + status_block([{'id': 3, 'rating': '超配', 'confidence': 5, 'note': 'FAIL周不得回写'}],
                                 'ALLOCATION_STATUS'))
    thesis_updates, blocked = quiet(rg.apply_status_updates, rep, 'FAIL',
                                    anchors=anchors_at('2026-10-12'), today_str='2026-10-12',
                                    thesis_path=tp, views_path=vp)
    check("FAIL→返回被阻断标记", blocked is True)
    check("thesis.json字节不变", open(tp, 'rb').read() == before_t)
    check("allocation_views.json字节不变", open(vp, 'rb').read() == before_v)
    # PASS路径正常回写(非退化)
    thesis_updates2, blocked2 = quiet(rg.apply_status_updates, rep.replace('已失效', '进行中').replace('超配', '标配').replace('"confidence":5', '"confidence":2'),
                                      'PASS', anchors=anchors_at('2026-10-12'), today_str='2026-10-12',
                                      thesis_path=tp, views_path=vp)
    after_t = json.load(open(tp))
    check("PASS→thesis.json正常回写(last_updated推进)", not blocked2 and after_t['last_updated'] == '2026-10-12',
          after_t.get('last_updated'))
    check("_has_numeric_errors仍识别数值类错误", rg._has_numeric_errors(['🚨 数值错误: 偏差超容差']) is True
          and rg._has_numeric_errors(['⚠️ 样式警告']) is False)

# ════════ 测试20: 周报月报季报不功能退化 (P1) ════════
print("\n── 20. 周报/月报/季报功能不退化")
import monthly_review as mr
import quarterly_outlook as qo
check("月报触发: 10月第一个周五(10-02)复盘9月",
      rg.pending_completed_month(datetime(2026, 10, 2)) == '202609',
      str(rg.pending_completed_month(datetime(2026, 10, 2))))
check("季报触发: 10月第一个周五复盘Q3",
      rg.pending_completed_quarter(datetime(2026, 10, 2)) == '2026Q3')
check("第二周五不触发月报", rg.pending_completed_month(datetime(2026, 10, 9)) is None)
check("月末最后一个周五不提前触发(10-30仍None)",
      rg.pending_completed_month(datetime(2026, 10, 30)) is None
      and rg.pending_completed_quarter(datetime(2026, 10, 30)) is None)
check("1月第一周五复盘上季Q4跨年",
      rg.pending_completed_quarter(datetime(2027, 1, 1)) == '2026Q4',
      str(rg.pending_completed_quarter(datetime(2027, 1, 1))))
for mod, fn in ((mr, 'gather_month_series'), (mr, 'coverage_report'),
                (qo, 'gather_quarter_series'), (qo, 'build_data_block')):
    check(f"{mod.__name__}.{fn}仍存在且可调用", callable(getattr(mod, fn, None)))
# 周报结构: 解析完整9行论点块+9行观点块回写(功能级,非源码字符串)
with tempfile.TemporaryDirectory() as td:
    tp = os.path.join(td, 'thesis.json')
    shutil.copy(os.path.join(ROOT, 'config', 'thesis.json'), tp)
    rows = [{'id': i, 'status': '待观察', 'confidence': 1, 'note': f't{i}'} for i in range(1, 10)]
    quiet(rg.update_thesis_status, status_block(rows), thesis_path=tp,
          anchors=anchors_at('2026-10-12'), today_str='2026-10-12')
    tdata = json.load(open(tp))
    tags = [h.rsplit(' ', 2)[0] for t in tdata['theses'] for h in t['history'][-1:]]
    check("9个论点全部回写history", all(f"10/12" in (t['history'][-1] if t.get('history') else '') for t in tdata['theses'])
          and len(tdata['theses']) == 9)
    check("9论点结构保留(名称/规则/关联齐全)",
          all(t.get('name') and 'invalidation_rules' in t for t in tdata['theses']))
# 观点块渲染不退化
views_cfg = json.load(open(os.path.join(ROOT, 'config', 'allocation_views.json')))
block = quiet(ae.render_views_block, views_cfg, '2026-10-12', anchors=anchors_at('2026-10-12'))
check("render_views_block仍渲染全部资产观点",
      block and all(v['asset'][:2] in block for v in views_cfg['views'][:9]))

# ════════ 附加B: 中立证据/采集日替代观测日/关键传导指标(第四轮复审补) ════════
print("\n── 附加B1. 中立证据(neutral)不计入支持数量")
day = '2026-10-12'
ev_n = [
    {'metric': 'macro.data.CCC_OAS.value', 'value': 10.12, 'obs_date': day, 'mechanism': '信用'},
    {'metric': 'macro.data.HY_OAS.value', 'value': 5.20, 'obs_date': day, 'mechanism': '信用', 'neutral': True},
    {'metric': 'macro.data.TIPS_10Y.value', 'value': 2.89, 'obs_date': day, 'mechanism': '利率与流动性', 'stance': 'neutral'},
]
verified, _r = quiet(ae.verify_evidence_items, ev_n, anchors_at(day), day)
supporting, contrary, unexplained, neutral_ev = ae.split_evidence_direction(verified)
check("中立项数值真实性照常验证(3项全过)", len(verified) == 3 and not _r, f"{verified} {_r}")
check("中立项不计入支持(支持=1,中立=2)", len(supporting) == 1 and len(neutral_ev) == 2,
      f"supporting={len(supporting)} neutral={len(neutral_ev)}")
star, _ = ae.star_level_from_evidence(verified)
check("中立项不抬高星级(1支持项→1★)", star == 1, f"star={star}")
with tempfile.TemporaryDirectory() as td:
    vp = os.path.join(td, 'allocation_views.json')
    views_n = {'version': '4.0', 'views': [
        {'id': 1, 'asset': '美股', 'rating': '标配', 'confidence': 2, 'history': [],
         'quant_triggers': [], 'key_metrics': []}]}
    json.dump(views_n, open(vp, 'w'), ensure_ascii=False)
    rep = status_block([{'id': 1, 'rating': '低配', 'confidence': 2,
                         'note': '1支持+2中立', 'evidence': ev_n}], 'ALLOCATION_STATUS')
    quiet(ae.update_allocation_status, rep, views_path=vp, anchors=anchors_at(day), today_str=day)
    v1 = json.load(open(vp))['views'][0]
    check("1项支持+2项中立不能过≥2项新增门禁,评级维持", v1['rating'] == '标配', v1['rating'])
    led = v1.get('evidence_ledger', [])
    check("台账分别记录支持数与中立数", led and led[-1]['supporting'] == 1 and led[-1]['neutral'] == 2,
          str(led[-1] if led else None))

print("\n── 附加B2. 采集日(as_of)不得替代观测日被模型引用")
anch_b = anchors_at(day)  # CCC obs_date=10-12 as_of=10-12 → 构造 obs≠as_of 的锚点
anch_b['macro.data.CCC_OAS.value'] = {'value': 10.12, 'obs_date': '2026-10-10', 'as_of': day}
ev_b = [{'metric': 'macro.data.CCC_OAS.value', 'value': 10.12, 'obs_date': day, 'mechanism': '信用'}]
v_b, r_b = quiet(ae.verify_evidence_items, ev_b, anch_b, day)
check("模型引用采集日(10-12)冒充观测日(锚点真值10-10)→拒",
      len(v_b) == 0 and '观测日不符' in r_b[0][0] and '采集日' in r_b[0][0], f"{v_b} {r_b}")
ev_ok = [{'metric': 'macro.data.CCC_OAS.value', 'value': 10.12, 'obs_date': '2026-10-10', 'mechanism': '信用'}]
v_ok, _r2 = quiet(ae.verify_evidence_items, ev_ok, anch_b, day)
check("引用锚点真观测日(10-10)→过,且台账记录真观测日",
      len(v_ok) == 1 and v_ok[0]['obs_date'] == '2026-10-10', f"{v_ok}")

print("\n── 附加B3. 证据未触及资产关键传导指标→保留候选提案(P0-2.4)")
with tempfile.TemporaryDirectory() as td:
    vp = os.path.join(td, 'allocation_views.json')
    views_k = {'version': '4.0', 'views': [
        {'id': 3, 'asset': '信用', 'rating': '低配', 'confidence': 3, 'history': [],
         'quant_triggers': [], 'key_metrics': ['macro.data.CCC_OAS.value']}]}
    json.dump(views_k, open(vp, 'w'), ensure_ascii=False)
    offkey = [{'metric': 'macro.data.TIPS_10Y.value', 'value': 2.89, 'obs_date': day, 'mechanism': '利率与流动性'},
              {'metric': 'macro.data.HY_OAS.value', 'value': 5.20, 'obs_date': day, 'mechanism': '信用'}]
    rep = status_block([{'id': 3, 'rating': '标配', 'confidence': 3,
                         'note': '宏观事实≠配置方向', 'evidence': offkey}], 'ALLOCATION_STATUS')
    quiet(ae.update_allocation_status, rep, views_path=vp, anchors=anchors_at(day), today_str=day)
    v3 = json.load(open(vp))['views'][0]
    check("2项新增证据但均未触及CCC(信用关键传导指标)→降为候选提案,评级维持低配",
          v3['rating'] == '低配'
          and any('关键传导指标' in str(pr.get('reason', '')) for pr in v3.get('proposals', [])),
          f"{v3['rating']} {v3.get('proposals')}")
    onkey = offkey + [{'metric': 'macro.data.CCC_OAS.value', 'value': 10.12, 'obs_date': day, 'mechanism': '信用'}]
    # 第五轮P1-1: 同日重跑时早前已计入的(指标,观测日)不再是新增 —
    # 正向路径用全新沙盒验证(同批3项证据一次计入)
    with tempfile.TemporaryDirectory() as td2:
        vp2 = os.path.join(td2, 'allocation_views.json')
        json.dump(views_k, open(vp2, 'w', encoding='utf-8'), ensure_ascii=False)
        rep2 = status_block([{'id': 3, 'rating': '标配', 'confidence': 3,
                              'note': '含关键指标', 'evidence': onkey}], 'ALLOCATION_STATUS')
        quiet(ae.update_allocation_status, rep2, views_path=vp2, anchors=anchors_at(day), today_str=day)
        v3b = json.load(open(vp2))['views'][0]
        check("含关键传导指标(CCC)的足量证据→变更通过", v3b['rating'] == '标配', v3b['rating'])
    # 反例(第五轮P1-1): 同日第二次运行,同批证据不重复计入 — 只剩CCC新增1项<2→被拒
    rep3 = status_block([{'id': 3, 'rating': '标配', 'confidence': 3,
                          'note': '同日重跑', 'evidence': onkey}], 'ALLOCATION_STATUS')
    quiet(ae.update_allocation_status, rep3, views_path=vp, anchors=anchors_at(day), today_str=day)
    v3c = json.load(open(vp))['views'][0]
    check("同日重跑同批证据不再重复计为新增(维持低配)",
          v3c['rating'] == '低配', v3c['rating'])
    check("未定义key_metrics的观点不受该规则限制(由星级门禁把关)",
          ae._key_engaged({'key_metrics': None}, set()) is True)

# ════════ 附加: 非交易日截止日按最近收盘裁决 ════════
print("\n── 附加A. 截止日为周六→按最近(周五)收盘裁决")
pred_sat = dict(pred)
pred_sat.update({'verify_mode': 'expiry', 'price_basis': 'close', 'observe_from': '2026-10-05',
                 'deadline': '2026-10-10',   # 周六
                 'observations': [{'obs_date': '2026-10-08', 'value': 4310.0},
                                  {'obs_date': '2026-10-09', 'value': 4305.0}]})
va = quiet(ae.evaluate_predictions, {'predictions': [pred_sat]}, today_str='2026-10-12')
check("周六截止→取周五(10-09)收盘4305≥4300判hit",
      va and va[0][2] == 'hit' and '2026-10-09' in va[0][3], str(va))

# ════════ 端到端: 同一状态连续四周(论点触发器+确信度,正确与错误案例) ════════
print("\n── E2E: 论点#1(T1-INV1实际利率≥2.5持续3周)同一状态连续四周")
with tempfile.TemporaryDirectory() as td:
    tp = os.path.join(td, 'thesis.json')
    shutil.copy(os.path.join(ROOT, 'config', 'thesis.json'), tp)
    FRIDAYS = ['2026-10-09', '2026-10-16', '2026-10-23', '2026-10-30']  # W41~W44

    # W1: 实际利率2.61,模型宣判已失效→应被拒(连续仅1周,不足3周)
    # (GOLD锚点抬到4350,避开T1-INV3黄金≤4200触发器,单测T1-INV1路径)
    def inv_anchors(day, tips):
        return anchors_at(day, **{
            'macro.data.TIPS_10Y.value': {'value': tips, 'obs_date': day, 'as_of': day},
            'global_market.data.GOLD.close': {'value': 4350, 'obs_date': day, 'as_of': day}})
    a1 = inv_anchors(FRIDAYS[0], 2.61)
    rep1 = status_block([{'id': 1, 'status': '已失效', 'confidence': 1, 'note': '利率2.61三周'}])
    quiet(rg.update_thesis_status, rep1, thesis_path=tp, anchors=a1, today_str=FRIDAYS[0])
    t1 = [t for t in json.load(open(tp))['theses'] if t['id'] == 1][0]
    check("W1宣判失效被拒(连续1/3周)", t1['status'] == '待观察', t1['status'])

    # W2: 2.62持续第二周; 同周重复运行不重复计
    a2 = inv_anchors(FRIDAYS[1], 2.62)
    rep2 = status_block([{'id': 1, 'status': '已失效', 'confidence': 1, 'note': '利率2.62两周'}])
    quiet(rg.update_thesis_status, rep2, thesis_path=tp, anchors=a2, today_str=FRIDAYS[1])
    quiet(rg.update_thesis_status, rep2, thesis_path=tp, anchors=a2, today_str=FRIDAYS[1])  # 同周重跑
    t1 = [t for t in json.load(open(tp))['theses'] if t['id'] == 1][0]
    check("W2宣判失效仍被拒(连续2/3周,同周重跑不加)", t1['status'] == '待观察', t1['status'])
    check("W2 trigger_state连续2周", t1['trigger_state']['T1-INV1']['consec'] == 2, str(t1['trigger_state']))

    # W3: 2.58第三周→触发器满3周,模型宣判失效→通过
    a3 = inv_anchors(FRIDAYS[2], 2.58)
    rep3 = status_block([{'id': 1, 'status': '已失效', 'confidence': 1, 'note': '利率三周≥2.5'}])
    quiet(rg.update_thesis_status, rep3, thesis_path=tp, anchors=a3, today_str=FRIDAYS[2])
    t1 = [t for t in json.load(open(tp))['theses'] if t['id'] == 1][0]
    check("W3触发器满3周→已失效落地(via=触发器)",
          t1['status'] == '已失效' and 'T1-INV1' in t1['last_change']['via'], str(t1.get('last_change')))
    check("W3 last_change审计完整(from/to/date/evidence)",
          all(k in t1['last_change'] for k in ('date', 'from', 'to', 'via', 'evidence')))

    # W4: 实际利率回落2.4→条件明确不满足,consec清零;关联论点提示不自动改评级
    a4 = inv_anchors(FRIDAYS[3], 2.40)
    rep4 = status_block([{'id': 1, 'status': '待观察', 'confidence': 1, 'note': '利率回落'}])
    quiet(rg.update_thesis_status, rep4, thesis_path=tp, anchors=a4, today_str=FRIDAYS[3])
    t1 = [t for t in json.load(open(tp))['theses'] if t['id'] == 1][0]
    check("W4利率回落→consec清零", t1['trigger_state']['T1-INV1']['consec'] == 0, str(t1['trigger_state']))
    # 已失效是已落地事实,不因W4回升而自动复活(过程状态回待观察是允许的研究判断,此处模型未提出)
    hist_line = t1['history'][-1]
    check("W4 history记录当周状态", '10/30' in hist_line, hist_line)

    # 反例贯穿: 论点#5无触发器,连续四周宣判已验证,前两周证据不足全被拒
    tp2 = os.path.join(td, 'thesis2.json')
    shutil.copy(os.path.join(ROOT, 'config', 'thesis.json'), tp2)
    ev_old = [{'metric': 'macro.data.CCC_OAS.value', 'value': 10.12, 'obs_date': '2026-10-09', 'mechanism': '信用'}]
    for wk in FRIDAYS:
        rep = status_block([{'id': 5, 'status': '已验证', 'confidence': 2,
                             'note': '重复旧证据', 'evidence': ev_old}])
        anch_wk = anchors_at('2026-10-09')  # 观测日始终10-09(旧值)
        quiet(rg.update_thesis_status, rep, thesis_path=tp2, anchors=anch_wk, today_str=wk)
    t5 = [t for t in json.load(open(tp2))['theses'] if t['id'] == 5][0]
    check("反例: 四周重复引用同一旧值→始终无法升级已验证", t5['status'] == '待观察', t5['status'])
    check("反例: 被拒提案留档且repeat累计",
          any(p.get('repeat', 1) >= 4 for p in t5.get('proposals', [])), str(t5.get('proposals')))

# ════════ 汇总 ════════
print("\n" + "=" * 60)
print(f"结果: {PASS} 通过, {FAIL} 失败")
print("=" * 60)
sys.exit(1 if FAIL else 0)
