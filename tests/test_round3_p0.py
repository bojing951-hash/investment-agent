#!/usr/bin/env python3
"""第三轮P0单元测试(2026-10-11) — 评级门禁/证据分级v2程序校验/触发器v3/预测生命周期/数据新鲜度

对应任务书的P0-1~P0-4,每项断言都可证伪: 给定构造输入,断言引擎的确定性行为。
纯离线,不调用GLM。

运行: ~/AI内容/venv/bin/python3 tests/test_round3_p0.py
"""
import os
import sys
import io
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

print("=" * 60)
print("第三轮P0单元测试")
print("=" * 60)

# ════════ 测试用公共fixture ════════
ANCHORS = {
    'macro.data.CCC_OAS.value': {'value': 10.12, 'obs_date': '2026-10-09', 'as_of': '2026-10-09'},
    'macro.data.TIPS_10Y.value': {'value': 2.89, 'obs_date': '2026-10-09', 'as_of': '2026-10-09'},
    'macro.data.HY_OAS.value': {'value': 5.20, 'obs_date': '2026-10-08', 'as_of': '2026-10-09'},
    'global_market.data.SPX.close': {'value': 7650, 'obs_date': '2026-10-09', 'as_of': '2026-10-09'},
    'global_market.data.GOLD.close': {'value': 4180, 'obs_date': '2026-10-09', 'as_of': '2026-10-09'},
    'global_market.data.DXY.close': {'value': 99.9, 'obs_date': '2026-10-09', 'as_of': '2026-10-09'},
    'rate_economy.real_economy.UNRATE.value': {'value': 4.2, 'obs_date': '2026-09-01', 'as_of': '2026-10-09'},
}

def base_views():
    return {'version': '3.0', 'last_updated': '2026-10-02', 'views': [
        {'id': 1, 'asset': '美股测', 'rating': '标配', 'confidence': 2, 'history': [],
         'quant_triggers': [
             {'trig_id': 'T1', 'direction': 'downgrade',
              'metric': 'macro.data.CCC_OAS.value', 'op': '>=', 'target': 10.0, 'unit': '%'}]},
        {'id': 5, 'asset': '黄金测', 'rating': '观望', 'confidence': 2, 'history': [],
         'quant_triggers': []},
    ], 'predictions': []}

def alloc_block(objs):
    lines = ['<!--ALLOCATION_STATUS'] + [json.dumps(o, ensure_ascii=False) for o in objs] + ['ALLOCATION_STATUS-->']
    return '\n'.join(lines)

def pred_block(objs):
    lines = ['<!--PREDICTION_STATUS'] + [json.dumps(o, ensure_ascii=False) for o in objs] + ['PREDICTION_STATUS-->']
    return '\n'.join(lines)

def run_update(views_data, report_text, anchors=None, today='2026-10-09'):
    """临时文件上跑 update_allocation_status,返回(更新后的views, updates列表)"""
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, 'views.json')
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(views_data, f, ensure_ascii=False)
        ups = quiet(ae.update_allocation_status, report_text, views_path=p,
                    anchors=anchors if anchors is not None else ANCHORS, today_str=today)
        with open(p, encoding='utf-8') as f:
            return json.load(f), ups

def ev(metric, value, obs='2026-10-09', mech=None, contrary=False, explained=False):
    d = {'metric': metric, 'value': value, 'obs_date': obs}
    if mech:
        d['mechanism'] = mech
    if contrary:
        d['contrary'] = True
    if explained:
        d['explained'] = True
    return d

# ════════════════════════════════════════════════════════════
print("\n[A] 数据新鲜度与状态更新门禁 (P0-4)")
# ════════════════════════════════════════════════════════════
check("A1 逐指标频率规则: .close=5天", dv.freshness_rule_for('global_market.data.SPX.close')[0] == 5)
check("A2 macro.data=7天", dv.freshness_rule_for('macro.data.TIPS_10Y.value')[0] == 7)
check("A3 rate_economy=45天(月度含发布滞后)",
      dv.freshness_rule_for('rate_economy.real_economy.UNRATE.value')[0] == 45)
check("A4 china非收盘键=7天(收盘价由.close规则覆盖为5天)",
      dv.freshness_rule_for('china.data.南向资金净流入')[0] == 7
      and dv.freshness_rule_for('china.data.上证.close')[0] == 5)
check("A5 scorecard=10天", dv.freshness_rule_for('scorecard.total')[0] == 10)
check("A6 未命中模式默认14天", dv.freshness_rule_for('other.foo')[0] == 14)
check("A7 月度指标滞后38天仍新鲜(≤45)",
      dv.is_fresh_anchor('rate_economy.real_economy.UNRATE.value',
                         {'obs_date': '2026-09-01'}, '2026-10-09'))
check("A8 日频行情滞后6天=过期",
      not dv.is_fresh_anchor('global_market.data.SPX.close',
                             {'obs_date': '2026-10-03'}, '2026-10-09'))
check("A9 日频行情滞后4天=新鲜",
      dv.is_fresh_anchor('global_market.data.SPX.close',
                         {'obs_date': '2026-10-05'}, '2026-10-09'))
check("A10 无观测日的锚点不判新鲜(第四轮修正: 缺观测日→待验证,不得默认通过)",
      not dv.is_fresh_anchor('x.y', {'value': 1}, '2026-10-09'))
check("A10b 观测日在未来(研究截止之后)→不新鲜(待验证)",
      not dv.is_fresh_anchor('global_market.data.SPX.close',
                             {'obs_date': '2026-10-20'}, '2026-10-09'))
check("A10c 月度CPI滞后30天仍新鲜(第四轮修正: 不再套macro统一7天规则)",
      dv.is_fresh_anchor('macro.data.CPI.value', {'obs_date': '2026-09-10'}, '2026-10-09'))
w = dv.stale_anchor_warning('global_market.data.SPX.close', {'obs_date': '2026-10-01'}, '2026-10-09')
check("A11 过期警告含规则上限与不得作当前证据", w and '不得作为当前有效证据' in w and '5天' in w, str(w))
check("A12 新鲜锚点无警告", dv.stale_anchor_warning('global_market.data.SPX.close',
      {'obs_date': '2026-10-08'}, '2026-10-09') is None)

# ════════════════════════════════════════════════════════════
print("\n[B] 证据分级v2程序校验 (P0-3)")
# ════════════════════════════════════════════════════════════
# 三周三个ISO观察期: 09-25(W39)/10-02(W40)/10-09(W41)
FIVE = [
    ev('macro.data.CCC_OAS.value', 10.12, '2026-10-09'),          # 信用
    ev('macro.data.TIPS_10Y.value', 2.89, '2026-10-02'),          # 利率与流动性(改观测日构造跨期,此处仅星级函数输入)
    ev('global_market.data.SPX.close', 7650, '2026-09-25'),       # 增长
    ev('global_market.data.GOLD.close', 4180, '2026-10-09'),      # 避险与估值
    ev('global_market.data.DXY.close', 99.9, '2026-10-02'),       # 资金流
]
s, d = ae.star_level_from_evidence([FIVE[0]])
check("B1 1项证据→1★", s == 1, f"{s} {d}")
s, _ = ae.star_level_from_evidence(FIVE[:2])
check("B2 2项1类机制→2★", s == 2)
s, _ = ae.star_level_from_evidence(FIVE[:3])
check("B3 3项3类机制→3★(3★门槛=3项且2类)", s == 3)
s, _ = ae.star_level_from_evidence(FIVE[:3])
check("B3b 3项仅落同一观察期→仍3★(3★不要求跨期)", s == 3)
s, _ = ae.star_level_from_evidence(FIVE[:4])
check("B4 4项3类跨2观察期→4★", s == 4, f"star={s}")
FIVE_X = FIVE + [ev('macro.data.CCC_OAS.value', 10.12, '2026-10-09', contrary=True, explained=True)]
s, d = ae.star_level_from_evidence(FIVE_X[:5] + [FIVE_X[5]])
check("B5 5项3类跨3期+含已解释反证→5★", s == 5, f"{s} {d}")
s, _ = ae.star_level_from_evidence(FIVE)
check("B6 5项3类跨3期无反证→5★(第四轮修正: 5★不要求存在反证)", s == 5, f"star={s}")
s, d = ae.star_level_from_evidence(FIVE + [ev('macro.data.TIPS_10Y.value', 2.89, '2026-10-09', contrary=True)])
check("B7 存在未解释重大反证→封顶3★", s == 3 and '未解释反证' in d, f"{s} {d}")
s, _ = ae.star_level_from_evidence([FIVE[0]] * 4)
check("B8 同一指标重复引用4次只计1项(1★)", s == 1, f"star={s}")
same_week = [ev('macro.data.CCC_OAS.value', 10.12, '2026-10-09'),
             ev('macro.data.TIPS_10Y.value', 2.89, '2026-10-09'),
             ev('global_market.data.SPX.close', 7650, '2026-10-09'),
             ev('global_market.data.GOLD.close', 4180, '2026-10-09')]
s, d = ae.star_level_from_evidence(same_week)
check("B9 同一月度值连引四周≠4个观察期: 全落同一ISO周→仅3★(4★须跨2期)",
      s == 3, f"star={s} {d}")
check("B10 mechanism_of显式声明优先", ae.mechanism_of('macro.data.X.value', '信用') == '信用')
check("B11 mechanism_of按指标ID推断: CCC→信用", ae.mechanism_of('macro.data.CCC_OAS.value') == '信用')
check("B12 mechanism_of: TIPS→利率与流动性", ae.mechanism_of('macro.data.TIPS_10Y.value') == '利率与流动性')
check("B13 mechanism_of: GOLD→避险与估值", ae.mechanism_of('global_market.data.GOLD.close') == '避险与估值')
check("B14 mechanism_of: 未知指标回退增长", ae.mechanism_of('foo.bar') == '增长')

v, r = ae.verify_evidence_items([ev('macro.data.CCC_OAS.value', 10.12)], ANCHORS, '2026-10-09')
check("B15 数值/观测日吻合的证据通过", len(v) == 1 and not r)
v, r = ae.verify_evidence_items([ev('macro.data.CCC_OAS.value', 9.99)], ANCHORS, '2026-10-09')
check("B16 数值不符→拒", not v and '数值不符' in r[0][0])
v, r = ae.verify_evidence_items([ev('macro.data.CCC_OAS.value', 10.12, obs='2026-09-01')], ANCHORS, '2026-10-09')
check("B17 观测日不符→拒", not v and '观测日不符' in r[0][0])
v, r = ae.verify_evidence_items([ev('macro.data.FAKE.value', 1.0)], ANCHORS, '2026-10-09')
check("B18 指标不在锚点中→拒(虚构证据嫌疑)", not v and '虚构' in r[0][0])
stale_anchors = dict(ANCHORS)
stale_anchors['global_market.data.SPX.close'] = {'value': 7650, 'obs_date': '2026-09-25', 'as_of': '2026-10-09'}
v, r = ae.verify_evidence_items(
    [ev('global_market.data.SPX.close', 7650, obs='2026-09-25')], stale_anchors, '2026-10-09')
check("B19 数据过期(日频滞后14天>5天)→不得作当前证据", not v and '过期' in r[0][0], str(r))
v, r = ae.verify_evidence_items([ev('macro.data.CCC_OAS.value', 1012)], ANCHORS, '2026-10-09')
check("B20 bp形态(1012↔10.12%)容差内通过", len(v) == 1, str(r))
v, r = ae.verify_evidence_items([ev('macro.data.CCC_OAS.value', 10.12)], None, '2026-10-09')
check("B21 无锚点→证据全部拒收(无锚点即无证据)", not v and '锚点' in r[0][0])

# ════════════════════════════════════════════════════════════
print("\n[C] 触发器v3: 复合/持续/首次跨越 (P0-1)")
# ════════════════════════════════════════════════════════════
st, det = ae._eval_condition({'metric': 'macro.data.CCC_OAS.value', 'op': '>=', 'target': 10.0}, ANCHORS)
check("C1 单指标10.12>=10.0→触发", st == 'triggered' and '✅满足' in det)
st, _ = ae._eval_condition({'metric': 'macro.data.CCC_OAS.value', 'op': '>=', 'target': 11.0}, ANCHORS)
check("C2 未达阈值→未触发", st == 'not_triggered')
st, _ = ae._eval_condition({'metric': 'macro.data.NOPE.value', 'op': '>=', 'target': 1.0}, ANCHORS)
check("C3 无当日锚点→待验证(不猜)", st == 'unverifiable')
st, _ = ae._eval_condition_set({'all': [
    {'metric': 'macro.data.CCC_OAS.value', 'op': '>=', 'target': 10.0},
    {'metric': 'macro.data.TIPS_10Y.value', 'op': '>=', 'target': 2.5}]}, ANCHORS)
check("C4 AND: 两条件均满足→触发", st == 'triggered')
st, _ = ae._eval_condition_set({'all': [
    {'metric': 'macro.data.CCC_OAS.value', 'op': '>=', 'target': 10.0},
    {'metric': 'macro.data.TIPS_10Y.value', 'op': '<', 'target': 2.5}]}, ANCHORS)
check("C5 AND: 一项明确不满足→整体不满足", st == 'not_triggered')
st, _ = ae._eval_condition_set({'all': [
    {'metric': 'macro.data.CCC_OAS.value', 'op': '>=', 'target': 10.0},
    {'metric': 'macro.data.NOPE.value', 'op': '>=', 'target': 1.0}]}, ANCHORS)
check("C6 AND: 一项待验证一项满足→整体待验证(不猜)", st == 'unverifiable')
st, _ = ae._eval_condition_set({'any': [
    {'metric': 'macro.data.TIPS_10Y.value', 'op': '<', 'target': 2.5},
    {'metric': 'macro.data.CCC_OAS.value', 'op': '>=', 'target': 10.0}]}, ANCHORS)
check("C7 OR: 任一满足→触发", st == 'triggered')
st, _ = ae._eval_condition_set({'any': [
    {'metric': 'macro.data.TIPS_10Y.value', 'op': '<', 'target': 2.5},
    {'metric': 'macro.data.CCC_OAS.value', 'op': '>=', 'target': 11.0}]}, ANCHORS)
check("C8 OR: 全部明确不满足→不满足", st == 'not_triggered')
st, _ = ae._eval_condition_set({'any': [
    {'metric': 'macro.data.NOPE.value', 'op': '>=', 'target': 1.0},
    {'metric': 'macro.data.CCC_OAS.value', 'op': '>=', 'target': 11.0}]}, ANCHORS)
check("C9 OR: 一项待验证一项不满足→待验证", st == 'unverifiable')

# 持续条件(sustain_weeks) + 连续状态跨周持久化
def sustain_views():
    return {'views': [{'id': 5, 'asset': '金', 'quant_triggers': [
        {'trig_id': 'T3', 'direction': 'downgrade', 'metric': 'macro.data.TIPS_10Y.value',
         'op': '>=', 'target': 2.5, 'sustain_weeks': 3}]}], 'predictions': []}

vd = sustain_views()
r1 = ae.evaluate_quant_triggers(vd, ANCHORS, '2026-10-09', persist=True)[5][0]
check("C10 持续条件第1周→持续确认中(首次跨越,不算已触发)",
      r1['status'] == 'sustaining' and r1['consec'] == 1 and '首次跨越' in r1['detail'], str(r1))
r2 = ae.evaluate_quant_triggers(vd, ANCHORS, '2026-10-16', persist=True)[5][0]
check("C11 第2周→持续确认中2/3", r2['status'] == 'sustaining' and r2['consec'] == 2)
r3 = ae.evaluate_quant_triggers(vd, ANCHORS, '2026-10-23', persist=True)[5][0]
check("C12 第3周满额→已触发(非持续确认中)", r3['status'] == 'triggered' and r3['consec'] == 3)
# 中断一周(连续性断档>10天)→重新从1计
r4 = ae.evaluate_quant_triggers(vd, ANCHORS, '2026-11-13', persist=True)[5][0]
check("C13 断档3周后→连续性重置,重新首跨(consec=1)",
      r4['consec'] == 1 and r4['status'] == 'sustaining', str(r4))
vd2 = sustain_views()
before = json.dumps(vd2)
ae.evaluate_quant_triggers(vd2, ANCHORS, '2026-10-09', persist=False)
check("C14 渲染路径(persist=False)不改动观点库状态", json.dumps(vd2) == before)
# 阈值回落一周再上穿: 不满足周清零
vd3 = sustain_views()
ae.evaluate_quant_triggers(vd3, ANCHORS, '2026-10-09', persist=True)          # 1
low = dict(ANCHORS); low['macro.data.TIPS_10Y.value'] = dict(ANCHORS['macro.data.TIPS_10Y.value'], value=2.3)
ae.evaluate_quant_triggers(vd3, low, '2026-10-16', persist=True)              # 回落→0
r5 = ae.evaluate_quant_triggers(vd3, ANCHORS, '2026-10-23', persist=True)[5][0]
check("C15 中途回落一周→连续计数清零,再上穿重新首跨", r5['consec'] == 1 and r5['status'] == 'sustaining', str(r5))

# ════════════════════════════════════════════════════════════
print("\n[D] 评级变更门禁 (P0-1)")
# ════════════════════════════════════════════════════════════
# D1 无条件变更(无触发无证据)→拒+留档
saved, ups = run_update(base_views(), alloc_block([{'id': 1, 'rating': '超配', 'confidence': 2, 'note': '想升级'}]))
v1 = saved['views'][0]
check("D1 模型无条件改变评级→保留原评级", v1['rating'] == '标配')
pr = v1['proposals'][-1]
check("D1b 候选提案留档(含被拒原因)", pr['status'] == 'rejected' and pr['to'] == '超配'
      and '新增独立支持证据0项' in pr['reason'], str(pr))

# D2 同向触发器已触发→放行
saved, ups = run_update(base_views(), alloc_block([{'id': 1, 'rating': '低配', 'confidence': 2, 'note': 'CCC破线'}]))
v1 = saved['views'][0]
check("D2 引擎核验已触发的同向触发器→变更放行", v1['rating'] == '低配')
check("D2b 审计记录via=触发器+旧/新评级+证据", v1['last_change']['via'].startswith('触发器T1')
      and v1['last_change']['from'] == '标配' and v1['last_change']['to'] == '低配'
      and 'date' in v1['last_change'], str(v1.get('last_change')))

# D3 反向触发器触发≠放行(T1是downgrade,提超配是upgrade)
saved, _ = run_update(base_views(), alloc_block([{'id': 1, 'rating': '超配', 'confidence': 2, 'note': '逆向'}]))
check("D3 反向触发器(降级触发)不授权升级→保留标配", saved['views'][0]['rating'] == '标配')

# D4 ≥2项验证证据(无触发)→放行
saved, _ = run_update(base_views(), alloc_block([{'id': 1, 'rating': '超配', 'confidence': 3, 'note': '证据升级',
    'evidence': [ev('macro.data.CCC_OAS.value', 10.12, mech='信用'),
                 ev('global_market.data.SPX.close', 7650, mech='增长'),
                 ev('macro.data.TIPS_10Y.value', 2.89, mech='利率与流动性')]}]))
v1 = saved['views'][0]
check("D4 3项程序验证证据(无触发)→升级放行", v1['rating'] == '超配')
check("D4b via=证据路径且审计含证据明细", '证据3项' in v1['last_change']['via']
      and len(v1['last_change']['evidence']) == 3)

# D5 仅1项证据→拒(需≥2)
saved, _ = run_update(base_views(), alloc_block([{'id': 1, 'rating': '超配', 'confidence': 2, 'note': '单项',
    'evidence': [ev('macro.data.CCC_OAS.value', 10.12)]}]))
check("D5 仅1项验证证据(无触发)→拒,保留标配", saved['views'][0]['rating'] == '标配')

# D6 转观望(suspend)放宽为1项
saved, _ = run_update(base_views(), alloc_block([{'id': 1, 'rating': '观望', 'confidence': 2, 'note': '暂停表态',
    'evidence': [ev('macro.data.CCC_OAS.value', 10.12)]}]))
check("D6 转观望仅需1项证据→放行", saved['views'][0]['rating'] == '观望')

# D7 自观望恢复(resume): 0证据拒, 1证据放行
saved, _ = run_update(base_views(), alloc_block([{'id': 5, 'rating': '标配', 'confidence': 2, 'note': '恢复'}]))
check("D7 自观望恢复0证据→拒(不得借降级触发器直接放行)", saved['views'][1]['rating'] == '观望')
saved, _ = run_update(base_views(), alloc_block([{'id': 5, 'rating': '标配', 'confidence': 2, 'note': '恢复',
    'evidence': [ev('global_market.data.GOLD.close', 4180, mech='避险与估值')]}]))
check("D7b 自观望恢复1项证据→放行", saved['views'][1]['rating'] == '标配')

# D8 被拒提案21天内去重(不每周新增同一提案)
vd = base_views()
saved1, _ = run_update(vd, alloc_block([{'id': 1, 'rating': '超配', 'confidence': 2, 'note': '第一次'}]))
vd2 = saved1
saved2, _ = run_update(vd2, alloc_block([{'id': 1, 'rating': '超配', 'confidence': 2, 'note': '第二次'}]),
                       today='2026-10-16')
v1 = saved2['views'][0]
same = [p for p in v1['proposals'] if p['to'] == '超配']
check("D8 同向提案21天内去重(只累计repeat不新增条目)", len(same) == 1 and same[0]['repeat'] == 2, str(same))

# D9 同向提案在后续通过门禁时标记superseded; 反向旧提案不标
# (证据用10-16当周新鲜锚点: 上周的日频行情观测日已过期,不得作当前证据)
d9_anchors = {'macro.data.CCC_OAS.value': {'value': 10.12, 'obs_date': '2026-10-16', 'as_of': '2026-10-16'},
              'global_market.data.SPX.close': {'value': 7650, 'obs_date': '2026-10-16', 'as_of': '2026-10-16'},
              'global_market.data.GOLD.close': {'value': 4180, 'obs_date': '2026-10-16', 'as_of': '2026-10-16'}}
saved3, _ = run_update(saved2, alloc_block([{'id': 1, 'rating': '超配', 'confidence': 2, 'note': '补证据升级',
    'evidence': [ev('macro.data.CCC_OAS.value', 10.12, obs='2026-10-16'),
                 ev('global_market.data.SPX.close', 7650, obs='2026-10-16'),
                 ev('global_market.data.GOLD.close', 4180, obs='2026-10-16')]}]),
                       anchors=d9_anchors, today='2026-10-16')
v1 = saved3['views'][0]
check("D9 同向变更(超配)通过→旧超配被拒提案标superseded", v1['rating'] == '超配'
      and any(p['status'] == 'superseded' and p['to'] == '超配' for p in v1['proposals']), str(v1.get('proposals')))
saved3b, _ = run_update(base_views(), alloc_block([{'id': 1, 'rating': '超配', 'confidence': 2, 'note': '先拒'}]), today='2026-10-02')
saved3c, _ = run_update(saved3b, alloc_block([{'id': 1, 'rating': '低配', 'confidence': 2, 'note': '后触发降级'}]), today='2026-10-09')
v1c = saved3c['views'][0]
check("D9b 反向变更(低配)落地不使被拒的超配提案superseded(留公示期自然过期)",
      v1c['rating'] == '低配' and all(p['status'] == 'rejected' for p in v1c['proposals']), str(v1c.get('proposals')))

# D10 确信度上调不得超过程序星级
saved, _ = run_update(base_views(), alloc_block([{'id': 1, 'rating': '标配', 'confidence': 5, 'note': '想上5★',
    'evidence': [ev('macro.data.CCC_OAS.value', 10.12), ev('global_market.data.SPX.close', 7650)]}]))
v1 = saved['views'][0]
check("D10 证据仅2项(2★)时确信度→5★被拒", v1['confidence'] == 2
      and any(p['to'] == '确信度5★' for p in v1['proposals']), str(v1.get('proposals')))

# D11 确信度下调自由
saved, _ = run_update(base_views(), alloc_block([{'id': 1, 'rating': '标配', 'confidence': 1, 'note': '下调'}]))
check("D11 确信度下调不受星级门禁", saved['views'][0]['confidence'] == 1)

# D12 评级不变+确信度变化合法单独记录
saved, _ = run_update(base_views(), alloc_block([{'id': 1, 'rating': '标配', 'confidence': 3, 'note': '证据增厚',
    'evidence': [ev('macro.data.CCC_OAS.value', 10.12, mech='信用'),
                 ev('global_market.data.SPX.close', 7650, mech='增长'),
                 ev('macro.data.TIPS_10Y.value', 2.89, mech='利率与流动性')]}]))
v1 = saved['views'][0]
check("D12 评级不变+确信度2→3(3项3类=3★)→放行", v1['rating'] == '标配' and v1['confidence'] == 3)
check("D12b 确信度变化单独记录为'确信度'条目",
      any(h.startswith('10/9 确信度') and '2★→3★' in h for h in v1['history']), str(v1['history']))
check("D12c 证据台账留档", v1['evidence_ledger'][-1]['star_max'] == 3, str(v1.get('evidence_ledger')))

# D13 关键证据缺失封顶2★(观点key_metrics未覆盖)
vd = base_views()
vd['views'][0]['key_metrics'] = ['macro.data.CCC_OAS.value']
saved, _ = run_update(vd, alloc_block([{'id': 1, 'rating': '标配', 'confidence': 4, 'note': '缺关键证据',
    'evidence': [ev('global_market.data.SPX.close', 7650, mech='增长'),
                 ev('global_market.data.GOLD.close', 4180, mech='避险与估值'),
                 ev('global_market.data.DXY.close', 99.9, mech='资金流')]}]))
v1 = saved['views'][0]
check("D13 关键证据(CCC)缺失→确信度封顶2★,4★被拒", v1['confidence'] == 2
      and '关键证据缺失' in v1['evidence_ledger'][-1]['desc'], str(v1.get('evidence_ledger')))

# D14 嵌套evidence数组的ALLOCATION_STATUS行可解析(回归: 曾被扁平正则拆碎)
saved, _ = run_update(base_views(), alloc_block([{'id': 1, 'rating': '标配', 'confidence': 3, 'note': 'x',
    'evidence': [ev('macro.data.CCC_OAS.value', 10.12), ev('global_market.data.SPX.close', 7650),
                 ev('macro.data.TIPS_10Y.value', 2.89)]}]))
check("D14 嵌套evidence行完整解析(证据台账非空)", saved['views'][0].get('evidence_ledger'))

# ════════════════════════════════════════════════════════════
print("\n[E] 预测全生命周期 (P0-2)")
# ════════════════════════════════════════════════════════════
def pred_views(preds):
    return {'views': base_views()['views'], 'predictions': preds}

# E1 前提规格程序判定: 未兑现→不启动观察期
vd = pred_views([{'pred_id': 10, 'date_made': '2026-10-02', 'asset': '金', 'deadline': '2026-10-25',
                  'direction': '若TIPS回落至2.2下,两周内GOLD涨至4400', 'status': 'not_yet_triggered',
                  'metric': 'global_market.data.GOLD.close', 'comparator': '>=', 'target': 4400,
                  'verify_mode': 'expiry', 'observations': [],
                  'premise': {'metric': 'macro.data.TIPS_10Y.value', 'op': '<=', 'target': 2.2}}])
ae.record_observations(vd, ANCHORS, '2026-10-09')
p = vd['predictions'][0]
check("E1 前提(TIPS≤2.2)未兑现→保持未触发,无观察记录",
      p['status'] == 'not_yet_triggered' and p['observations'] == [])

# E2 前提兑现→转观察中,observe_from=前提观测日,截止日不变
prem_ok = dict(ANCHORS)
prem_ok['macro.data.TIPS_10Y.value'] = dict(ANCHORS['macro.data.TIPS_10Y.value'], value=2.15, obs_date='2026-10-08')
ae.record_observations(vd, prem_ok, '2026-10-09')
p = vd['predictions'][0]
check("E2 前提程序确认→转观察中,观察期自前提观测日起,截止日不顺延",
      p['status'] == 'observing' and p['observe_from'] == '2026-10-08'
      and p['deadline'] == '2026-10-25' and p['premise_triggered_date'] == '2026-10-08', str(p.get('observe_from')))

# E3 观察记录: 去重+最新采集覆盖
vd = pred_views([{'pred_id': 11, 'date_made': '2026-10-02', 'asset': '股', 'deadline': '2026-10-23',
                  'direction': 'SPX跌破7600', 'status': 'observing', 'observe_from': '2026-10-02',
                  'metric': 'global_market.data.SPX.close', 'comparator': '<=', 'target': 7600,
                  'verify_mode': 'touch', 'observations': []}])
a1 = dict(ANCHORS)
ae.record_observations(vd, a1, '2026-10-09')   # SPX 7650 obs 10-09
a2 = dict(ANCHORS); a2['global_market.data.SPX.close'] = dict(
    ANCHORS['global_market.data.SPX.close'], value=7580, obs_date='2026-10-09', as_of='2026-10-10')
ae.record_observations(vd, a2, '2026-10-10')   # 同观测日修正值
p = vd['predictions'][0]
check("E3 同观测日去重(最新采集覆盖,不重复累计)",
      len(p['observations']) == 1 and p['observations'][0]['value'] == 7580, str(p['observations']))

# E4 touch模式提前命中(截止前)
verdicts = ae.evaluate_predictions(vd, today_str='2026-10-10')
v10 = next(v for v in verdicts if v[0] == 11)
check("E4 touch模式观察期内触及→提前判hit(无需等截止)",
      v10[2] == 'hit' and '触及' in v10[3] and '7580' in v10[3], str(v10))

# E5 touch到期未触及→miss
vd2 = pred_views([{'pred_id': 12, 'date_made': '2026-10-02', 'asset': '股', 'deadline': '2026-10-16',
                   'direction': 'SPX跌破7000', 'status': 'observing', 'observe_from': '2026-10-02',
                   'metric': 'global_market.data.SPX.close', 'comparator': '<=', 'target': 7000,
                   'verify_mode': 'touch',
                   # 第五轮P0-2: touch判miss须窗口覆盖充分 — 补齐窗内全部11个交易日
                   'observations': [{'obs_date': d, 'value': 7620 + (i % 3) * 15, 'as_of': d}
                                    for i, d in enumerate(['2026-10-02', '2026-10-05', '2026-10-06',
                                                           '2026-10-07', '2026-10-08', '2026-10-09',
                                                           '2026-10-12', '2026-10-13', '2026-10-14',
                                                           '2026-10-15', '2026-10-16'])]}])
verdicts = ae.evaluate_predictions(vd2, today_str='2026-10-16')
v12 = next(v for v in verdicts if v[0] == 12)
check("E5 touch到期从未触及(窗口覆盖充分)→miss", v12[2] == 'miss' and '从未满足' in v12[3], str(v12))

# E6 expiry未到期→不裁决
vd3 = pred_views([{'pred_id': 13, 'date_made': '2026-10-02', 'asset': '股', 'deadline': '2026-10-23',
                   'direction': 'SPX收于7500上', 'status': 'observing', 'observe_from': '2026-10-02',
                   'metric': 'global_market.data.SPX.close', 'comparator': '>=', 'target': 7500,
                   'verify_mode': 'expiry',
                   'observations': [{'obs_date': '2026-10-09', 'value': 7650, 'as_of': '2026-10-09'}]}])
check("E6 expiry截止日未到→引擎不提前裁决",
      not ae.evaluate_predictions(vd3, today_str='2026-10-16'))

# E7 expiry到期按窗内最后观测裁决
vd3['predictions'][0]['deadline'] = '2026-10-16'
vd3['predictions'][0]['observations'].append({'obs_date': '2026-10-16', 'value': 7480, 'as_of': '2026-10-16'})
v13 = ae.evaluate_predictions(vd3, today_str='2026-10-16')[0]
check("E7 expiry按截止窗内最后观测(7480<7500)→miss", v13[2] == 'miss' and '截止日水平' in v13[3], str(v13))

# E8 观察窗外数据不参与裁决(禁止未来数据)
vd4 = pred_views([{'pred_id': 14, 'date_made': '2026-10-02', 'asset': '股', 'deadline': '2026-10-16',
                   'direction': 'SPX两周内触及7000下', 'status': 'observing', 'observe_from': '2026-10-02',
                   'metric': 'global_market.data.SPX.close', 'comparator': '<=', 'target': 7000,
                   'verify_mode': 'touch',
                   # 第五轮P0-2: 窗内补齐全部11个交易日(覆盖充分),窗前/窗后数据仍不参与
                   'observations': [{'obs_date': '2026-09-25', 'value': 6900, 'as_of': '2026-09-25'}]   # 窗前
                                    + [{'obs_date': d, 'value': 7630 + (i % 3) * 10, 'as_of': d}
                                       for i, d in enumerate(['2026-10-02', '2026-10-05', '2026-10-06',
                                                              '2026-10-07', '2026-10-08', '2026-10-09',
                                                              '2026-10-12', '2026-10-13', '2026-10-14',
                                                              '2026-10-15', '2026-10-16'])]
                                    + [{'obs_date': '2026-10-20', 'value': 6800, 'as_of': '2026-10-20'}]}])  # 窗后(未来)
v14 = ae.evaluate_predictions(vd4, today_str='2026-10-16')[0]
check("E8 窗前6900与窗后6800都不算→touch到期miss(区间仅窗内7630~7650)",
      v14[2] == 'miss' and '7650' in v14[3] and '6900' not in v14[3] and '6800' not in v14[3], str(v14))
# expiry版本: 窗内最后观测决定,窗后未来值不覆盖
vd5 = pred_views([{'pred_id': 15, 'date_made': '2026-10-02', 'asset': '股', 'deadline': '2026-10-16',
                   'direction': 'SPX收7000上', 'status': 'observing', 'observe_from': '2026-10-02',
                   'metric': 'global_market.data.SPX.close', 'comparator': '>=', 'target': 7000,
                   'verify_mode': 'expiry',
                   'observations': [{'obs_date': '2026-10-15', 'value': 7600, 'as_of': '2026-10-15'},
                                    {'obs_date': '2026-10-20', 'value': 5000, 'as_of': '2026-10-20'}]}])
v15 = ae.evaluate_predictions(vd5, today_str='2026-10-16')[0]
check("E9 expiry裁决用窗内最后观测(7600),窗后暴跌5000不算→hit",
      v15[2] == 'hit' and '7600' in v15[3] and '5000' not in v15[3], str(v15))

# E10 前提至截止日未成立→终态未触发
vd6 = pred_views([{'pred_id': 16, 'date_made': '2026-10-02', 'asset': '金', 'deadline': '2026-10-16',
                   'direction': '若TIPS≤2.2,金涨', 'status': 'not_yet_triggered',
                   'metric': 'global_market.data.GOLD.close', 'comparator': '>=', 'target': 4400,
                   'verify_mode': 'expiry', 'observations': [],
                   'premise': {'metric': 'macro.data.TIPS_10Y.value', 'op': '<=', 'target': 2.2}}])
v16 = ae.evaluate_predictions(vd6, today_str='2026-10-16')[0]
check("E10 前提至截止日未成立→未触发(终态),截止日不顺延",
      v16[2] == 'not_yet_triggered' and '未生效' in v16[3], str(v16))

# E11 窗内无数据→无法裁决(不硬判)
vd7 = pred_views([{'pred_id': 17, 'date_made': '2026-10-02', 'asset': '股', 'deadline': '2026-10-16',
                   'direction': 'SPX跌', 'status': 'observing', 'observe_from': '2026-10-02',
                   'metric': 'global_market.data.SPX.close', 'comparator': '<=', 'target': 7000,
                   'verify_mode': 'touch', 'observations': []}])
v17 = ae.evaluate_predictions(vd7, today_str='2026-10-16', anchors={})[0]
check("E11 观察窗内无观测→无法裁决(数据缺失不硬判)", v17[2] == 'inconclusive' and '无' in v17[3]
      and '观测记录' in v17[3])

# ════════════════════════════════════════════════════════════
print("\n[F] 裁决权威序: 引擎>GLM (P0-2,经update路径)")
# ════════════════════════════════════════════════════════════
# F1 GLM把引擎客观miss改判hit→拒
# (锚点SPX=7450: record_observations补录当天观测后,窗内最后观测7450<7500→引擎客观miss)
f1_anchors = dict(ANCHORS)
f1_anchors['global_market.data.SPX.close'] = {'value': 7450, 'obs_date': '2026-10-09', 'as_of': '2026-10-09'}
vd = pred_views([{'pred_id': 20, 'date_made': '2026-10-02', 'asset': '股', 'deadline': '2026-10-09',
                  'direction': 'SPX收7500上', 'status': 'observing', 'observe_from': '2026-10-02',
                  'metric': 'global_market.data.SPX.close', 'comparator': '>=', 'target': 7500,
                  'verify_mode': 'expiry',
                  'observations': [{'obs_date': '2026-10-08', 'value': 7480, 'as_of': '2026-10-08'}]}])
report = alloc_block([{'id': 1, 'rating': '标配', 'confidence': 2, 'note': 'm'}]) + '\n' + \
    pred_block([{'pred_id': 20, 'status': 'hit', 'note': 'SPX 7650收于7500上方(观测日2026-10-09)'}])
saved, ups = run_update(vd, report, anchors=f1_anchors, today='2026-10-09')
p = saved['predictions'][0]
check("F1 GLM把引擎客观miss(7450<7500)改判hit→拒,引擎miss生效",
      p['status'] == 'miss' and any('不可覆盖' in u or '拒绝' in u for u in ups), f"{p['status']} {ups}")

# F2 GLM对expiry未到期提前hit→拒
vd = pred_views([{'pred_id': 21, 'date_made': '2026-10-02', 'asset': '金', 'deadline': '2026-10-25',
                  'direction': '金涨至4400', 'status': 'observing', 'observe_from': '2026-10-02',
                  'metric': 'global_market.data.GOLD.close', 'comparator': '>=', 'target': 4400,
                  'verify_mode': 'expiry',
                  'observations': [{'obs_date': '2026-10-09', 'value': 4310, 'as_of': '2026-10-09'}]}])
report = alloc_block([{'id': 1, 'rating': '标配', 'confidence': 2, 'note': 'm'}]) + '\n' + \
    pred_block([{'pred_id': 21, 'status': 'hit', 'note': '金价4310已上4400(观测日2026-10-09)'}])
saved, ups = run_update(vd, report, today='2026-10-09')
p = saved['predictions'][0]
check("F2 expiry截止(10-25)未到,GLM提前hit→拒,仍观察中",
      p['status'] == 'observing' and any('不得提前' in u for u in ups), f"{p['status']} {ups}")

# F3 GLM引用观察窗外的数值裁决touch→拒(引用核验)
vd = pred_views([{'pred_id': 22, 'date_made': '2026-10-02', 'asset': '金', 'deadline': '2026-10-23',
                  'direction': '金触及4400', 'status': 'observing', 'observe_from': '2026-10-02',
                  'metric': 'global_market.data.GOLD.close', 'comparator': '>=', 'target': 4400,
                  'verify_mode': 'touch',
                  'observations': [{'obs_date': '2026-10-09', 'value': 4180, 'as_of': '2026-10-09'}]}])
report = alloc_block([{'id': 1, 'rating': '标配', 'confidence': 2, 'note': 'm'}]) + '\n' + \
    pred_block([{'pred_id': 22, 'status': 'hit', 'note': '金价4410已触及4400(观测日2026-10-10)'}])
saved, ups = run_update(vd, report, today='2026-10-09')
p = saved['predictions'][0]
check("F3 GLM touch裁决引用窗内记录外的数值(4410≠4180)→拒",
      p['status'] == 'observing' and any('观察窗' in u for u in ups), f"{p['status']} {ups}")

# F4 前提规格已程序触发,GLM改判未触发→拒
vd = pred_views([{'pred_id': 23, 'date_made': '2026-10-02', 'asset': '金', 'deadline': '2026-10-25',
                  'direction': '若TIPS≤2.2金涨', 'status': 'not_yet_triggered',
                  'metric': 'global_market.data.GOLD.close', 'comparator': '>=', 'target': 4400,
                  'verify_mode': 'expiry', 'observations': [],
                  'premise': {'metric': 'macro.data.TIPS_10Y.value', 'op': '<=', 'target': 3.5}}])
report = alloc_block([{'id': 1, 'rating': '标配', 'confidence': 2, 'note': 'm'}]) + '\n' + \
    pred_block([{'pred_id': 23, 'status': 'not_yet_triggered', 'note': '前提未兑现,继续等待'}])
saved, ups = run_update(vd, report, today='2026-10-09')
p = saved['predictions'][0]
check("F4 前提(TIPS≤3.5)已被程序确认触发,GLM改判未触发→拒,转观察中",
      p['status'] == 'observing' and any('不得改判' in u or '程序确认' in u for u in ups), f"{p['status']} {ups}")

# F5 引擎已终态(前提至截止未成立),GLM转观察中→拒
vd = pred_views([{'pred_id': 24, 'date_made': '2026-09-25', 'asset': '金', 'deadline': '2026-10-09',
                  'direction': '若TIPS≤2.2金涨', 'status': 'not_yet_triggered',
                  'metric': 'global_market.data.GOLD.close', 'comparator': '>=', 'target': 4400,
                  'verify_mode': 'expiry', 'observations': [],
                  'premise': {'metric': 'macro.data.TIPS_10Y.value', 'op': '<=', 'target': 2.2}}])
report = alloc_block([{'id': 1, 'rating': '标配', 'confidence': 2, 'note': 'm'}]) + '\n' + \
    pred_block([{'pred_id': 24, 'status': 'observing', 'note': '前提本周兑现,开始观察'}])
saved, ups = run_update(vd, report, today='2026-10-09')
p = saved['predictions'][0]
check("F5 前提到截止日未程序成立(终态),GLM再转观察中→拒(截止日不顺延)",
      p['status'] == 'not_yet_triggered' and any('终态' in u or '不顺延' in u for u in ups), f"{p['status']} {ups}")

# F6 GLM与引擎一致→正常应用,不重复
vd = pred_views([{'pred_id': 25, 'date_made': '2026-10-02', 'asset': '股', 'deadline': '2026-10-09',
                  'direction': 'SPX收7500上', 'status': 'observing', 'observe_from': '2026-10-02',
                  'metric': 'global_market.data.SPX.close', 'comparator': '>=', 'target': 7500,
                  'verify_mode': 'expiry',
                  'observations': [{'obs_date': '2026-10-08', 'value': 7650, 'as_of': '2026-10-08'}]}])
report = alloc_block([{'id': 1, 'rating': '标配', 'confidence': 2, 'note': 'm'}]) + '\n' + \
    pred_block([{'pred_id': 25, 'status': 'hit', 'note': 'SPX 7650≥7500(观测日2026-10-08)'}])
saved, ups = run_update(vd, report, today='2026-10-09')
p = saved['predictions'][0]
check("F6 GLM裁决与引擎一致(hit)→正常落盘", p['status'] == 'hit' and p['resolved_date'] == '2026-10-09')

# F7 无证据裁决(hit但note无数值)→拒 (截止未到,引擎无裁决,走GLM补位前的证据检查)
vd = pred_views([{'pred_id': 26, 'date_made': '2026-10-02', 'asset': '股', 'deadline': '2026-10-23',
                  'direction': 'SPX跌', 'status': 'observing', 'observe_from': '2026-10-02',
                  'metric': 'global_market.data.SPX.close', 'comparator': '<=', 'target': 7000,
                  'verify_mode': 'touch', 'observations': []}])
report = alloc_block([{'id': 1, 'rating': '标配', 'confidence': 2, 'note': 'm'}]) + '\n' + \
    pred_block([{'pred_id': 26, 'status': 'hit', 'note': '已明显跌破'}])
saved, ups = run_update(vd, report, today='2026-10-16')
p = saved['predictions'][0]
check("F7 GLM hit无数值证据→拒收", p['status'] == 'observing' and any('无数值' in u or '无证据' in u for u in ups),
      f"{p['status']} {ups}")

# F8 评级变更行附带完整规格预测→登记生命周期字段(含前提规格)
report = alloc_block([{'id': 1, 'rating': '低配', 'confidence': 2, 'note': 'T1降级',
                       'pred': '信用压制两周内SPX触7400', 'pred_weeks': 2,
                       'pred_metric': 'global_market.data.SPX.close', 'pred_op': '<=', 'pred_target': 7400,
                       'pred_mode': 'touch', 'pred_premise_metric': 'macro.data.CCC_OAS.value',
                       'pred_premise_op': '>=', 'pred_premise_target': 10.0}])
saved, ups = run_update(base_views(), report, today='2026-10-09')
np_ = saved['predictions'][-1]
check("F8 触发降级行登记新预测: touch模式+前提规格,当周前提已满足→程序即转观察中",
      np_['verify_mode'] == 'touch' and np_['status'] == 'observing'
      and np_['premise'] == {'metric': 'macro.data.CCC_OAS.value', 'op': '>=', 'target': 10.0}
      and np_['observe_from'] == '2026-10-09' and np_['deadline'] == '2026-10-23',
      f"{np_.get('status')} {np_.get('premise')}")

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
