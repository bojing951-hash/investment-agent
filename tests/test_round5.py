#!/usr/bin/env python3
"""第五轮可靠性修复测试(2026-10-12) — 纯离线,不调用GLM

任务书第九节20项用例(每项含正例/反例)+补充用例+第十节正式运行验收模拟。
全部断言落盘后的JSON状态(非仅返回值)。

  1  GLM宣hit但无观察记录→必拒(P0-1)
  2  GLM引用真实数值但观测日错误→拒(P0-1)
  3  GLM观测日正确但数值错误→拒(P0-1)
  4  touch窗内已触及+其他日期缺失→仍hit(P0-2)
  5  touch未触及但覆盖不足→inconclusive不判miss(P0-2)
  6  仅收盘价不能证明盘中未触及(P0-2)
  7  expiry缺截止日附近价格→inconclusive(P0-2)
  8  非交易日截止按事先确定规则(回溯最近有效交易日,不事后挑有利日期)(P0-2)
  9  缺obs_date的证据不参与星级/评级(P0-3)
  10 obs_date错误或未来→拒(P0-3)
  11 已失效论点未经重新启用条件不得恢复(P0-4)
  12 已验证论点重新开启不得绕过终态规则(P0-4)
  13 同日重跑10次不产生10次新增(P1-1)
  14 旧观测值重引不算新增(P1-1)
  15 修订不算新观察期(P1-1)
  16 关键行情采集失败→受影响预测不更新(P1-2)
  17 非关键新闻失败不阻止行情观察(P1-2)
  18 CPI指数点变化与环比计算正确(P1-3)
  19 论点与观点共用证据日期校验(P0-3)
  20 校验FAIL不改长期状态

运行: ~/AI内容/venv/bin/python3 tests/test_round5.py
"""
import os
import sys
import io
import json
import shutil
import subprocess
import tempfile
import contextlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
# FIX3-04 CI可移植性: 子进程用当前解释器(CI=runner python,本地=venv)。
# 原硬编码~/AI内容/venv路径在干净环境(CI)不存在→子进程直接失败。
PY = sys.executable

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


def block(objs, tag):
    """构造 <!--TAG ... TAG--> 状态块"""
    lines = "\n".join(json.dumps(o, ensure_ascii=False) for o in objs)
    return f"<!--{tag}\n{lines}\n{tag}-->"


import allocation_engine as ae
from report_generator import update_thesis_status, apply_status_updates
from macro_collector import compute_series_changes, SERIES_UNITS
import daily_prediction_observer as dpo
import run_weekly

DAY = '2026-10-14'   # 周三
DAY2 = '2026-10-16'  # 周五


def anchors_at(day, **over):
    a = {
        'macro.data.CCC_OAS.value': {'value': 9.2, 'obs_date': day, 'as_of': day},
        'macro.data.HY_OAS.value': {'value': 5.2, 'obs_date': day, 'as_of': day},
        'macro.data.TIPS_10Y.value': {'value': 2.89, 'obs_date': day, 'as_of': day},
        'macro.data.CPI.value': {'value': 303.0, 'obs_date': '2026-09-15', 'as_of': day},
        'macro.data.UNEMPLOYMENT.value': {'value': 4.4, 'obs_date': '2026-09-30', 'as_of': day},
        'global_market.data.GOLD.close': {'value': 4240.0, 'obs_date': day, 'as_of': day},
        'global_market.data.SPX.close': {'value': 7620.0, 'obs_date': day, 'as_of': day},
        'global_market.data.DXY.close': {'value': 99.9, 'obs_date': day, 'as_of': day},
    }
    a.update(over)
    return a


def gold_pred(pid, **kw):
    p = {'pred_id': pid, 'date_made': '2026-10-02', 'asset': '金', 'deadline': DAY2,
         'direction': '两周内金价触及4400', 'status': 'observing', 'observe_from': '2026-10-02',
         'metric': 'global_market.data.GOLD.close', 'comparator': '>=', 'target': 4400,
         'verify_mode': 'touch', 'price_basis': 'close', 'observations': []}
    p.update(kw)
    return p


_W = ['2026-10-02', '2026-10-05', '2026-10-06', '2026-10-07', '2026-10-08', '2026-10-09',
      '2026-10-12', '2026-10-13', '2026-10-14']  # 10-02~10-14全部9个交易日(us日历)


def full_obs(fill=lambda i, d: 4180 + (i % 4) * 20):
    return [{'obs_date': d, 'value': fill(i, d), 'as_of': d} for i, d in enumerate(_W)]


def views_file(td, preds=None, views=None):
    path = os.path.join(td, 'allocation_views.json')
    data = {'version': '5.0',
            'views': views if views is not None else [
                {'id': 1, 'asset': '美股', 'rating': '标配', 'confidence': 2, 'history': []}],
            'predictions': preds or []}
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    return path


def thesis_file(td, theses):
    path = os.path.join(td, 'thesis.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'theses': theses, 'last_updated': '2026-10-01'}, f, ensure_ascii=False)
    return path


def thesis_entry(tid, status, triggers=None, **kw):
    t = {'id': tid, 'name': f'论点{tid}', 'status': status, 'confidence': 2, 'history': [],
         'quant_triggers': triggers or [], 'related_theses': []}
    t.update(kw)
    return t


print("=" * 64)
print("第五轮可靠性修复 — 20项任务书用例 + 正式运行验收模拟")
print("=" * 64)

# ════════ 1. GLM宣hit但无观察记录→必拒 (P0-1) ════════
print("\n── 1. 无观察记录时GLM文字裁决必拒(P0-1)")
with tempfile.TemporaryDirectory() as td:
    # metric用锚点中不存在的SILVER → 观察窗保持真空(锚点GOLD会经record_observations补录)
    vp = views_file(td, preds=[gold_pred(101, deadline='2026-10-23', observe_from=DAY,
                                         metric='global_market.data.SILVER.close')])
    rep = block([{'id': 1, 'rating': '标配', 'confidence': 2, 'note': 'm'}], 'ALLOCATION_STATUS') \
        + block([{'pred_id': 101, 'status': 'hit', 'note': '银价4450已触及4400(观测日2026-10-15)'}],
                'PREDICTION_STATUS')
    ups = quiet(ae.update_allocation_status, rep, views_path=vp, anchors=anchors_at(DAY), today_str=DAY)
    p = json.load(open(vp))['predictions'][0]
    check("R1 观察窗无记录→GLM hit被拒,保持观察中", p['status'] == 'observing',
          f"{p['status']} {ups}")
    check("R1 拒绝理由明示'不得仅凭文字宣判'",
          any('仅凭文字' in u for u in ups), str(ups))

# ════════ 2. 真实数值+错误日期→拒 (P0-1) ════════
print("\n── 2. GLM引用真实数值但观测日错误→拒(P0-1)")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[gold_pred(102, deadline='2026-10-23',
                                         observations=full_obs())])
    # 窗内真值4200@2026-10-13,但note把日期写成2026-10-15(窗内无此记录)
    rep = block([{'pred_id': 102, 'status': 'hit', 'note': '金价4200(2026-10-15观测)触及走强'}],
                'PREDICTION_STATUS')
    ups = quiet(ae.update_allocation_status, rep, views_path=vp, anchors=anchors_at(DAY), today_str=DAY)
    p = json.load(open(vp))['predictions'][0]
    check("R2 真数值配错日期→拒,保持观察中", p['status'] == 'observing', f"{p['status']} {ups}")
    check("R2 拒绝理由要求数值与观测日同一条记录",
          any('同一条' in u for u in ups), str(ups))

# ════════ 3. 正确日期+错误数值→拒 (P0-1) ════════
print("\n── 3. GLM观测日正确但数值错误→拒(P0-1)")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[gold_pred(103, deadline='2026-10-23',
                                         observations=full_obs())])
    rep = block([{'pred_id': 103, 'status': 'hit', 'note': '金价4500(2026-10-13观测)已达标'}],
                'PREDICTION_STATUS')
    ups = quiet(ae.update_allocation_status, rep, views_path=vp, anchors=anchors_at(DAY), today_str=DAY)
    p = json.load(open(vp))['predictions'][0]
    check("R3 正确日期配虚构数值→拒,保持观察中", p['status'] == 'observing', f"{p['status']} {ups}")
# 补充B1(正例): 引用真实满足条件的记录+引擎一致→hit落盘
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[gold_pred(104, verify_mode='expiry', deadline=DAY,
                                         target=4200,
                                         observations=full_obs())])   # 10-14值4180<4200?→miss
    # 用一个真满足的: target 4100, 10-14值4180≥4100 → 引擎hit; GLM附和
    p104 = gold_pred(104, verify_mode='expiry', deadline=DAY, target=4100,
                     observations=full_obs())
    vp = views_file(td, preds=[p104])
    rep = block([{'pred_id': 104, 'status': 'hit', 'note': '金价4180(2026-10-14观测)≥4100'}],
                'PREDICTION_STATUS')
    ups = quiet(ae.update_allocation_status, rep, views_path=vp, anchors=anchors_at(DAY), today_str=DAY)
    p = json.load(open(vp))['predictions'][0]
    check("R3b(正例) 引擎hit+GLM附和真实记录→hit落盘带审计",
          p['status'] == 'hit' and p.get('resolved_date') == DAY
          and '4180' in p.get('resolved_note', ''), f"{p['status']} {p.get('resolved_note')}")

# ════════ 4. touch窗内已触及+其他日期缺失→仍hit (P0-2) ════════
print("\n── 4. 已触及不受覆盖缺口影响(触及是单调证据)")
p4 = gold_pred(21, price_basis='high', observations=[
    {'obs_date': '2026-10-05', 'value': 4250.0, 'high': 4262.0, 'low': 4241.0},
    {'obs_date': '2026-10-06', 'value': 4280.0, 'high': 4450.0, 'low': 4270.0},   # 盘中触及
    {'obs_date': '2026-10-09', 'value': 4255.0, 'high': 4284.0, 'low': 4249.0},
])
v4 = quiet(ae.evaluate_predictions, {'predictions': [p4]}, today_str=DAY2)
check("R4 窗内一项有效触及即hit(其余交易日缺失不影响)",
      v4 and v4[0][2] == 'hit' and '2026-10-06' in v4[0][3], str(v4))

# ════════ 5. touch未触及+覆盖不足→inconclusive (P0-2) ════════
print("\n── 5. 覆盖不足不判miss(数据缺失≠失败)")
p5 = gold_pred(22, price_basis='high', observations=[
    {'obs_date': '2026-10-05', 'value': 4250.0, 'high': 4262.0, 'low': 4241.0},
    {'obs_date': '2026-10-06', 'value': 4280.0, 'high': 4295.0, 'low': 4270.0},
    {'obs_date': '2026-10-09', 'value': 4255.0, 'high': 4284.0, 'low': 4249.0},
])
v5 = quiet(ae.evaluate_predictions, {'predictions': [p5]}, today_str=DAY2)
check("R5 仅3个交易日最高价且都<4400→inconclusive(黄金touch例)",
      v5 and v5[0][2] == 'inconclusive' and '覆盖不足' in v5[0][3], str(v5))
cov = ae.window_coverage(p5)
check("R5 覆盖体检: 预期11个交易日缺8天,sufficient=False",
      len(cov['expected']) == 11 and len(cov['missing']) == 8 and not cov['sufficient'],
      str(cov))

# ════════ 6. 仅收盘不能证明盘中未触及 (P0-2) ════════
print("\n── 6. 只有收盘价→盘中口径不判miss")
p6 = gold_pred(23, price_basis='high', observations=[
    {'obs_date': d, 'value': 4200 + i * 5} for i, d in enumerate(
        ['2026-10-02', '2026-10-05', '2026-10-06', '2026-10-07', '2026-10-08',
         '2026-10-09', '2026-10-12', '2026-10-13', '2026-10-14', '2026-10-15', '2026-10-16'])])
v6 = quiet(ae.evaluate_predictions, {'predictions': [p6]}, today_str=DAY2)
check("R6 全窗口只有收盘价(无high)→inconclusive",
      v6 and v6[0][2] == 'inconclusive' and '无法证明盘中未触及' in v6[0][3], str(v6))

# ════════ 7. expiry缺截止日附近价格→inconclusive (P0-2) ════════
print("\n── 7. 截止日附近无有效观测→inconclusive")
p7 = gold_pred(24, verify_mode='expiry', observations=[
    {'obs_date': d, 'value': 4300 + i} for i, d in enumerate(
        ['2026-10-02', '2026-10-05', '2026-10-06'])])   # 最近观测10-06,距截止10-16>4天
v7 = quiet(ae.evaluate_predictions, {'predictions': [p7]}, today_str=DAY2)
check("R7 有效截止交易日当日无观测→inconclusive不硬判(第六轮P0-3严格口径)",
      v7 and v7[0][2] == 'inconclusive' and '无' in v7[0][3] and '有效观测' in v7[0][3], str(v7))

# ════════ 8. 非交易日截止按事先确定规则 (P0-2) ════════
print("\n── 8. 非交易日截止=回溯最近有效交易日(预定义,不事后挑)")
check("R8a settlement(周六10-31,us)=周五10-30",
      ae.settlement_date('2026-10-31', 'us') == '2026-10-30')
p8 = gold_pred(25, verify_mode='expiry', comparator='<=', target=4300, deadline='2026-10-31',
               observations=[{'obs_date': '2026-10-29', 'value': 4250.0},   # 周四:满足<=4300
                             {'obs_date': '2026-10-30', 'value': 4340.0}])  # 周五:不满足
v8 = quiet(ae.evaluate_predictions, {'predictions': [p8]}, today_str='2026-10-31')
check("R8b 周六截止按周五4340裁决→miss(不回挑满足条件的周四4250)",
      v8 and v8[0][2] == 'miss' and '2026-10-30' in v8[0][3] and '4250' not in v8[0][3], str(v8))
check("R8c 加密资产7×24无回溯(settlement=截止日本身)",
      ae.settlement_date('2026-10-31', 'crypto') == '2026-10-31')

# ════════ 9. 缺obs_date证据不参与星级/评级 (P0-3) ════════
print("\n── 9. 缺obs_date的证据整项拒收(P0-3)")
anch = anchors_at(DAY)
ev_nodate = [{'metric': 'macro.data.CCC_OAS.value', 'value': 9.2},
             {'metric': 'macro.data.HY_OAS.value', 'value': 5.2},
             {'metric': 'macro.data.TIPS_10Y.value', 'value': 2.89}]
v9, r9 = quiet(ae.verify_evidence_items, ev_nodate, anch, DAY)
check("R9a 三项缺obs_date证据全部拒收", len(v9) == 0 and len(r9) == 3
      and all('缺obs_date' in r[0] for r in r9), f"{v9} {r9}")
star9, _ = ae.star_level_from_evidence(v9)
check("R9b 星级=0(无有效证据)", star9 == 0)
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, views=[{'id': 5, 'asset': '贵金属', 'rating': '观望', 'confidence': 2,
                                'history': []}])
    rep = block([{'id': 5, 'rating': '标配', 'confidence': 3, 'note': 'x',
                  'evidence': ev_nodate}], 'ALLOCATION_STATUS')
    ups = quiet(ae.update_allocation_status, rep, views_path=vp, anchors=anch, today_str=DAY)
    v = json.load(open(vp))['views'][0]
    check("R9c 评级变更被拒维持观望(证据全部无效)",
          v['rating'] == '观望' and any('缺obs_date' in str(pr.get('reason'))
                                        for pr in v.get('proposals', [])), str(v.get('proposals')))
    check("R9d 台账不写无效证据(防虚构入档)", not v.get('evidence_ledger'),
          str(v.get('evidence_ledger')))

# ════════ 10. obs_date错误或未来→拒 (P0-3) ════════
print("\n── 10. obs_date错误/未来→拒(P0-3)")
v10a, r10a = quiet(ae.verify_evidence_items,
                   [{'metric': 'macro.data.CCC_OAS.value', 'value': 9.2, 'obs_date': DAY}],
                   {'macro.data.CCC_OAS.value': {'value': 9.2, 'obs_date': '2026-10-10',
                                                 'as_of': DAY}}, DAY)
check("R10a 引用采集日as_of替代观测日→拒", len(v10a) == 0 and '观测日不符' in r10a[0][0],
      f"{v10a} {r10a}")
v10b, r10b = quiet(ae.verify_evidence_items,
                   [{'metric': 'macro.data.CCC_OAS.value', 'value': 9.2, 'obs_date': '2026-10-20'}],
                   anch, DAY)
check("R10b 引用未来日期(10-20>研究截止10-14)→拒", len(v10b) == 0, f"{v10b} {r10b}")
v10c, r10c = quiet(ae.verify_evidence_items,
                   [{'metric': 'macro.data.CCC_OAS.value', 'value': 9.2, 'obs_date': '2026-10-20'}],
                   {'macro.data.CCC_OAS.value': {'value': 9.2, 'obs_date': '2026-10-20',
                                                 'as_of': DAY}}, DAY)
check("R10c 锚点本身为未来数据(发布异常)→拒,不默认新鲜",
      len(v10c) == 0 and ('未来' in r10c[0][0] or '观测日' in r10c[0][0]), f"{v10c} {r10c}")

# ════════ 11. 已失效论点未经重新启用条件不得恢复 (P0-4) ════════
print("\n── 11. 已失效论点重新启用门禁(P0-4)")
inv_trig = [{'trig_id': 'T2-INV1', 'direction': 'invalidation',
             'metric': 'macro.data.CCC_OAS.value', 'op': '>=', 'target': 10.0}]
ev2 = [{'metric': 'macro.data.CCC_OAS.value', 'value': 9.2, 'obs_date': DAY, 'mechanism': '信用'},
       {'metric': 'macro.data.HY_OAS.value', 'value': 5.2, 'obs_date': DAY, 'mechanism': '信用'}]
with tempfile.TemporaryDirectory() as td:
    tp = thesis_file(td, [thesis_entry(3, '已失效', inv_trig)])
    rep = block([{'id': 3, 'status': '进行中', 'confidence': 2, 'note': '企稳',
                  'evidence': ev2[:1]}], 'THESIS_STATUS')
    quiet(update_thesis_status, rep, thesis_path=tp, anchors=anchors_at(DAY), today_str=DAY)
    t = json.load(open(tp))['theses'][0]
    check("R11a 已失效+仅1项新增证据→重新启用被拒,保持已失效",
          t['status'] == '已失效' and any('重新启用' in str(pr.get('reason'))
                                          for pr in t.get('proposals', [])),
          f"{t['status']} {t.get('proposals')}")
with tempfile.TemporaryDirectory() as td:
    tp = thesis_file(td, [thesis_entry(3, '已失效', inv_trig)])
    rep = block([{'id': 3, 'status': '进行中', 'confidence': 2, 'note': '两项独立新证据',
                  'evidence': ev2}], 'THESIS_STATUS')
    quiet(update_thesis_status, rep, thesis_path=tp, anchors=anchors_at(DAY), today_str=DAY)
    t = json.load(open(tp))['theses'][0]
    check("R11b ≥2项新增独立证据+原失效条件复核未触发(CCC9.2<10)→恢复进行中",
          t['status'] == '进行中' and '重新启用' in t.get('last_change', {}).get('via', ''),
          f"{t['status']} {t.get('last_change')}")
    check("R11b 审计含from/to/完整状态变化记录",
          t['last_change'].get('from') == '已失效' and t['last_change'].get('to') == '进行中')
with tempfile.TemporaryDirectory() as td:
    tp = thesis_file(td, [thesis_entry(3, '已失效', inv_trig)])
    rep = block([{'id': 3, 'status': '进行中', 'confidence': 2, 'note': 'x', 'evidence': ev2}],
                'THESIS_STATUS')
    quiet(update_thesis_status, rep, thesis_path=tp,
          anchors=anchors_at(DAY, **{'macro.data.CCC_OAS.value':
                                     {'value': 10.12, 'obs_date': DAY, 'as_of': DAY}}),
          today_str=DAY)
    t = json.load(open(tp))['theses'][0]
    check("R11c 原失效条件仍在触发(CCC10.12≥10)→即使2项新证据也拒绝恢复",
          t['status'] == '已失效' and any('复核仍在触发' in str(pr.get('reason'))
                                          for pr in t.get('proposals', [])),
          f"{t['status']} {t.get('proposals')}")

# ════════ 12. 已验证论点重新开启不得绕过终态规则 (P0-4) ════════
print("\n── 12. 已验证论点重开门禁(P0-4)")
ver_trig = [{'trig_id': 'T5-INV1', 'direction': 'invalidation',
             'metric': 'global_market.data.DXY.close', 'op': '>=', 'target': 105.0}]
ev_ctry = [{'metric': 'macro.data.CCC_OAS.value', 'value': 9.2, 'obs_date': DAY,
            'mechanism': '信用', 'contrary': True},
           {'metric': 'macro.data.HY_OAS.value', 'value': 5.2, 'obs_date': DAY,
            'mechanism': '信用', 'contrary': True}]
with tempfile.TemporaryDirectory() as td:
    tp = thesis_file(td, [thesis_entry(5, '已验证', ver_trig)])
    rep = block([{'id': 5, 'status': '进行中', 'confidence': 2, 'note': '重开'}], 'THESIS_STATUS')
    quiet(update_thesis_status, rep, thesis_path=tp, anchors=anchors_at(DAY), today_str=DAY)
    t = json.load(open(tp))['theses'][0]
    check("R12a 已验证无触发器无反证→重开被拒,保持已验证",
          t['status'] == '已验证' and any('重新开启' in str(pr.get('reason'))
                                          for pr in t.get('proposals', [])),
          f"{t['status']} {t.get('proposals')}")
with tempfile.TemporaryDirectory() as td:
    tp = thesis_file(td, [thesis_entry(5, '已验证', ver_trig)])
    rep = block([{'id': 5, 'status': '进行中', 'confidence': 2, 'note': '两项独立反证',
                  'evidence': ev_ctry}], 'THESIS_STATUS')
    quiet(update_thesis_status, rep, thesis_path=tp, anchors=anchors_at(DAY), today_str=DAY)
    t = json.load(open(tp))['theses'][0]
    check("R12b ≥2项新增独立反证→重开经门禁(进行中,反证记入审计)",
          t['status'] == '进行中' and '重新开启' in t.get('last_change', {}).get('via', '')
          and '反证' in t['last_change'].get('via', ''), f"{t['status']} {t.get('last_change')}")
with tempfile.TemporaryDirectory() as td:
    tp = thesis_file(td, [thesis_entry(5, '已验证', ver_trig)])
    rep = block([{'id': 5, 'status': '待观察', 'confidence': 2, 'note': '触发器'}], 'THESIS_STATUS')
    quiet(update_thesis_status, rep, thesis_path=tp,
          anchors=anchors_at(DAY, **{'global_market.data.DXY.close':
                                     {'value': 106.0, 'obs_date': DAY, 'as_of': DAY}}),
          today_str=DAY)
    t = json.load(open(tp))['theses'][0]
    check("R12c invalidation触发器引擎核验已触发(DXY106≥105)→重开经触发器路径",
          t['status'] == '待观察' and 'invalidation触发器' in t.get('last_change', {}).get('via', ''),
          f"{t['status']} {t.get('last_change')}")

# ════════ 13. 同日重跑10次不产生10次新增 (P1-1) ════════
print("\n── 13. 同日重跑10次(P1-1)")
ev3 = [{'metric': 'macro.data.CCC_OAS.value', 'value': 9.2, 'obs_date': DAY, 'mechanism': '信用'},
       {'metric': 'macro.data.HY_OAS.value', 'value': 5.2, 'obs_date': DAY, 'mechanism': '信用'},
       {'metric': 'macro.data.TIPS_10Y.value', 'value': 2.89, 'obs_date': DAY,
        'mechanism': '利率与流动性'}]
rep3 = block([{'id': 1, 'rating': '低配', 'confidence': 2, 'note': 'x', 'evidence': ev3}],
             'ALLOCATION_STATUS')
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td)
    for _ in range(10):
        quiet(ae.update_allocation_status, rep3, views_path=vp, anchors=anch, today_str=DAY)
    v = json.load(open(vp))['views'][0]
    led = v.get('evidence_ledger') or []
    check("R13a 同批数据同日跑10次: 评级只变更一次(标配→低配)",
          v['rating'] == '低配' and v.get('last_change', {}).get('from') == '标配', v['rating'])
    check("R13b 台账10条(幂等留痕)但第2条起new_support为空",
          len(led) == 10 and all(not e.get('new_support') for e in led[1:]),
          str([e.get('new_support') for e in led]))
with tempfile.TemporaryDirectory() as td:
    # 反向: 首次仅1项证据被拒,同日再跑9次不得累积错误满足
    rep1ev = block([{'id': 1, 'rating': '低配', 'confidence': 2, 'note': 'x',
                     'evidence': ev3[:1]}], 'ALLOCATION_STATUS')
    vp = views_file(td)
    for _ in range(10):
        quiet(ae.update_allocation_status, rep1ev, views_path=vp, anchors=anch, today_str=DAY)
    v = json.load(open(vp))['views'][0]
    check("R13c 1项证据连跑10次仍不满足≥2门槛(不累积错误满足)",
          v['rating'] == '标配' and (v.get('proposals') or [{}])[-1].get('repeat') == 10,
          f"{v['rating']} {v.get('proposals')}")
with tempfile.TemporaryDirectory() as td:
    # 阶梯攻击: 第1次升级落地后,同日用同批证据再提进一步升级→拒
    vp = views_file(td)
    quiet(ae.update_allocation_status, rep3, views_path=vp, anchors=anch, today_str=DAY)
    rep_up = block([{'id': 1, 'rating': '超配', 'confidence': 2, 'note': 'x', 'evidence': ev3}],
                   'ALLOCATION_STATUS')
    quiet(ae.update_allocation_status, rep_up, views_path=vp, anchors=anch, today_str=DAY)
    v = json.load(open(vp))['views'][0]
    check("R13d 同日同批证据不得推动第二次评级变更(阶梯攻击被拒)",
          v['rating'] == '低配', v['rating'])
    # 论点路径同样适用
    tp = thesis_file(td, [thesis_entry(1, '进行中')])
    rep_t = block([{'id': 1, 'status': '已验证', 'confidence': 2, 'note': 'x', 'evidence': ev3}],
                  'THESIS_STATUS')
    for _ in range(10):
        quiet(update_thesis_status, rep_t, thesis_path=tp, anchors=anch, today_str=DAY)
    t = json.load(open(tp))['theses'][0]
    hist_today = [h for h in t['history'] if h.startswith('10/14')]
    check("R13e 论点同日10次: 终态只落一次,history同日单条(替换不堆积)",
          t['status'] == '已验证' and len(hist_today) == 1
          and t.get('last_change', {}).get('from') == '进行中',
          f"{t['status']} {hist_today}")

# ════════ 14. 旧观测值重引不算新增 (P1-1) ════════
print("\n── 14. 旧值重引不算新增(P1-1)")
v14 = {'evidence_ledger': [{'date': '2026-09-24',
                            'obs_pairs': [('macro.data.CCC_OAS.value', '2026-09-24')]}]}
sup14 = [{'metric': 'macro.data.CCC_OAS.value', 'obs_date': '2026-09-24'}]
check("R14 (CCC,09-24)已记录→重引不是新增",
      ae.new_supporting_metrics(v14, sup14) == set())
sup14b = [{'metric': 'macro.data.CCC_OAS.prev', 'obs_date': '2026-09-24'}]
check("R14b 同基底不同字段(prev)重引同样不算新增(一致身份规则)",
      ae.new_supporting_metrics(v14, sup14b) == set())

# ════════ 15. 修订不算新观察期 (P1-1) ════════
print("\n── 15. 修订不算新观察期(P1-1)")
v15 = {'evidence_ledger': [{'date': '2026-09-24',
                            'obs_pairs': [('macro.data.CPI.value', '2026-09-15')]}]}
anch_rev = {'macro.data.CPI.value': {'value': 303.4, 'obs_date': '2026-09-15', 'as_of': DAY}}
ev15 = [{'metric': 'macro.data.CPI.value', 'value': 303.4, 'obs_date': '2026-09-15'}]
v15v, r15 = quiet(ae.verify_evidence_items, ev15, anch_rev, DAY)
check("R15a 修订后数值照常通过数值核验(同一观测期)", len(v15v) == 1, f"{v15v} {r15}")
check("R15b 同一观测期(CPI,09-15)数值修订不算新增观察",
      ae.new_supporting_metrics(v15, v15v) == set())

# ════════ 16. 关键采集失败不更新受影响预测 (P1-2) ════════
print("\n── 16. 采集失败门禁(P1-2)")
obs_pred_gold = gold_pred(31, deadline='2026-10-30', observe_from='2026-10-19',
                          observations=[])
obs_pred_spx = {'pred_id': 32, 'date_made': '2026-10-19', 'asset': '股', 'deadline': '2026-10-30',
                'direction': 'SPX两周内跌破7600', 'status': 'observing', 'observe_from': '2026-10-19',
                'metric': 'global_market.data.SPX.close', 'comparator': '<=', 'target': 7600,
                'verify_mode': 'touch', 'observations': []}
# IA-P0-1-FIX1: 锚点schema新增quality字段(FIX-04)——fixture补quality='PASS',
# 不改变既有断言语义(被测行为是观察幂等/部分缺失,不是质量门禁本身)。
day_anchors = lambda d, gold=None, spx=None: {
    'global_market.data.GOLD.close': {'value': (gold or (4210.0, 4240.0, 4180.0))[0],
                                      'obs_date': d, 'as_of': d, 'quality': 'PASS'},
    'global_market.data.GOLD.high': {'value': (gold or (4210.0, 4240.0, 4180.0))[1],
                                     'obs_date': d, 'as_of': d, 'quality': 'PASS'},
    'global_market.data.GOLD.low': {'value': (gold or (4210.0, 4240.0, 4180.0))[2],
                                    'obs_date': d, 'as_of': d, 'quality': 'PASS'},
    'global_market.data.SPX.close': {'value': (spx or (7640.0,))[0], 'obs_date': d, 'as_of': d,
                                     'quality': 'PASS'},
}
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[dict(obs_pred_gold), dict(obs_pred_spx)])
    before = open(vp).read()
    # 关键失败: 锚点文件是昨天的(本轮采集失败)
    ch, n, st = quiet(dpo.observe, views_path=vp, anchors=day_anchors('2026-10-19'),
                      today_str='2026-10-20', anchors_date='20261019')
    check("R16a 锚点非当日(采集失败)→关键FAIL,不写任何观察",
          st == 'FAIL' and ch == [] and open(vp).read() == before, f"{st} {ch}")
    # 部分缺失: 当日锚点缺GOLD(该资产采集失败)→只跳过金,SPX照常
    ch, n, st = quiet(dpo.observe, views_path=vp,
                      anchors={'global_market.data.SPX.close': {'value': 7640.0,
                                                                'obs_date': '2026-10-20',
                                                                'as_of': '2026-10-20',
                                                                'quality': 'PASS'}},
                      today_str='2026-10-20', anchors_date='20261020')
    saved = json.load(open(vp))
    pg = next(p for p in saved['predictions'] if p['pred_id'] == 31)
    ps = next(p for p in saved['predictions'] if p['pred_id'] == 32)
    check("R16b 当日锚点缺GOLD→金预测跳过(无新观测),状态PARTIAL",
          st == 'PARTIAL' and pg['observations'] == [], f"{st} {pg['observations']}")
    check("R16c SPX预测不受其他资产缺失影响照常记录",
          any(o['obs_date'] == '2026-10-20' for o in ps['observations']), str(ps['observations']))
    check("R16d 观察记录绑定实际观测日与本轮采集(obs_date+retrieved_at)",
          all(o['obs_date'] == '2026-10-20' and o.get('retrieved_at') == '2026-10-20'
              for o in ps['observations']), str(ps['observations']))
# CLI退出码: 采集失败→exit 2
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[dict(obs_pred_gold)])
    ap = os.path.join(td, 'anchors_20261021.json')
    json.dump(day_anchors('2026-10-21'), open(ap, 'w'))
    r = subprocess.run([PY, os.path.join(ROOT, 'scripts', 'daily_prediction_observer.py'),
                        '--views', vp, '--anchors', ap, '--today', '2026-10-22'],
                       capture_output=True, text=True)
    check("R16e 陈旧锚点CLI退出码=2(关键失败经退出码上报)",
          r.returncode == 2 and '不得以旧数据充当本期观察' in r.stdout,
          f"exit={r.returncode} {r.stdout[-200:]}")

# ════════ 17. 非关键新闻失败不阻止行情观察 (P1-2) ════════
print("\n── 17. 非关键失败降级(P1-2)")
with tempfile.TemporaryDirectory() as td:
    # run_pipeline不向脚本传参 → 观察桩用自身目录下的marker.txt留痕
    for name, code in [('a_collect.py', 'print("ok")'), ('news.py', 'print("news fail");exit(1)'),
                       ('z_observer.py',
                        'import pathlib;pathlib.Path(__file__).with_name("marker.txt").write_text("ran");print("obs ok")')]:
        with open(os.path.join(td, name), 'w') as f:
            f.write(code + '\n')
    marker = os.path.join(td, 'marker.txt')
    steps = [('全球采集', 'a_collect.py', True), ('新闻', 'news.py', False),
             ('预测观察', 'z_observer.py', True)]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        results = run_weekly.run_pipeline(steps, script_dir=td)
    crit_failed = [n for n, ok, c in results if not ok and c]
    check("R17a 新闻(非关键)失败: 后续观察步骤照常执行", os.path.exists(marker), buf.getvalue()[-200:])
    check("R17b 无关键失败→流水线判定成功(退出码0路径)",
          not crit_failed and all(ok for n, ok, c in results if c), str(results))
    with open(os.path.join(td, 'a_collect.py'), 'w') as f:
        f.write('print("collect fail");exit(1)\n')
    os.remove(marker)
    with contextlib.redirect_stdout(buf):
        results2 = run_weekly.run_pipeline(steps, script_dir=td)
    crit_failed2 = [n for n, ok, c in results2 if not ok and c]
    check("R17c 关键采集失败→判定失败(退出码1路径)且不阻断记录后续步骤",
          crit_failed2 == ['全球采集'] and os.path.exists(marker), str(results2))

# ════════ 18. CPI指数点变化与环比计算正确 (P1-3) ════════
print("\n── 18. 单位语义(P1-3)")
out18 = compute_series_changes(['2026-08-15', '2026-09-15'], [300.0, 303.0], 'monthly',
                               unit=('index', '指数点(1982-84=100)'))
check("R18a CPI 300→303: mom_chg=3.0点(不是'3%')",
      out18.get('mom_chg') == 3.0 and out18.get('mom_chg_unit') == '点', str(out18))
check("R18b 环比百分比另列: mom_pct=1.0%且公式含×100",
      out18.get('mom_pct') == 1.0 and '×100' in out18.get('mom_pct_formula', '')
      and '(2026-09-15值/2026-08-15值' in out18.get('mom_pct_formula', ''), str(out18))
out18b = compute_series_changes(['2026-08-31', '2026-09-30'], [4.2, 4.4], 'monthly',
                                unit=('rate', '%(失业率)'))
check("R18c 失业率4.2→4.4: 变化0.2百分点,不产百分比变化",
      out18b.get('mom_chg') == 0.2 and '百分点' in out18b.get('mom_chg_unit', '')
      and 'mom_pct' not in out18b, str(out18b))
out18c = compute_series_changes(['2026-08-15', '2026-09-15'], [158000.0, 160500.0], 'monthly',
                                unit=('count', '千人(非农就业)'))
check("R18d 非农就业+2500按人数计,不产百分比",
      out18c.get('mom_chg') == 2500.0 and out18c.get('mom_chg_unit') == '人数'
      and 'mom_pct' not in out18c, str(out18c))
out18d = compute_series_changes(['2026-10-05', '2026-10-12'], [9.40, 9.46], 'daily',
                                unit=('rate', '%(利差)'))
check("R18e 日频利差周变化+0.06按百分点(1个百分点=100bp)",
      out18d.get('week_chg') == 0.06 and '百分点' in out18d.get('week_chg_unit', ''), str(out18d))
check("R18f 单位注册表覆盖CPI(指数)/UNEMPLOYMENT(率)/NFP(人数)/CCC_OAS(利差)",
      SERIES_UNITS.get('CPI', (None,))[0] == 'index'
      and SERIES_UNITS.get('UNEMPLOYMENT', (None,))[0] == 'rate'
      and SERIES_UNITS.get('NFP', (None,))[0] == 'count'
      and SERIES_UNITS.get('CCC_OAS', (None,))[0] == 'rate')

# ════════ 19. 论点与观点共用证据日期校验 (P0-3) ════════
print("\n── 19. thesis与views共用同一套证据规则(P0-3)")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td)
    tp = thesis_file(td, [thesis_entry(1, '进行中')])
    rep = block([{'id': 1, 'rating': '低配', 'confidence': 3, 'note': 'x',
                  'evidence': ev_nodate}], 'ALLOCATION_STATUS') \
        + block([{'id': 1, 'status': '已验证', 'confidence': 3, 'note': 'x',
                  'evidence': ev_nodate}], 'THESIS_STATUS')
    tu = quiet(update_thesis_status, rep, thesis_path=tp, anchors=anch, today_str=DAY)
    quiet(ae.update_allocation_status, rep, views_path=vp, anchors=anch, today_str=DAY)
    t = json.load(open(tp))['theses'][0]
    v = json.load(open(vp))['views'][0]
    check("R19a 论点侧: 缺obs_date证据不支撑终态(保持进行中,台账不写)",
          t['status'] == '进行中' and not t.get('evidence_ledger'),
          f"{t['status']} {t.get('evidence_ledger')}")
    check("R19b 观点侧: 同一证据不支撑确信度上调(保持2★,台账不写)",
          v['confidence'] == 2 and not v.get('evidence_ledger'),
          f"{v} ")
    check("R19c 双侧拒绝原因都明示缺obs_date",
          any('缺obs_date' in str(pr.get('reason')) for pr in t.get('proposals', []))
          and any('缺obs_date' in str(pr.get('reason')) for pr in v.get('proposals', [])),
          f"{t.get('proposals')} {v.get('proposals')}")

# ════════ 20. 校验FAIL不改长期状态 ════════
print("\n── 20. FAIL门禁(不污染长期记忆)")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td)
    tp = thesis_file(td, [thesis_entry(1, '进行中')])
    before_v, before_t = open(vp).read(), open(tp).read()
    rep = block([{'id': 1, 'rating': '低配', 'confidence': 5, 'note': 'x', 'evidence': ev3}],
                'ALLOCATION_STATUS')
    tu, blocked = quiet(apply_status_updates, rep, 'FAIL', anchors=anch, today_str=DAY,
                        thesis_path=tp, views_path=vp)
    check("R20 FAIL→两个长期状态文件一字节不改",
          blocked is True and open(vp).read() == before_v and open(tp).read() == before_t)

# ══════════════════════════════════════════════════════════════════
# 第十节 正式运行验收模拟: 每日采集→观察→(周度)校验→论点→观点→预测裁决
# 同一份研究状态连续推进;失败隔离;时间一致
# ══════════════════════════════════════════════════════════════════
print("\n── 正式运行验收模拟(单沙盒连续状态,第十节)")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[dict(obs_pred_gold), dict(obs_pred_spx)])
    tp = thesis_file(td, [thesis_entry(1, '进行中'),
                          thesis_entry(2, '待观察', inv_trig)])
    # ── 每日采集→观察(Mon 10-19 ~ Fri 10-23),金每日小幅走高但始终<4400 ──
    week_days = ['2026-10-19', '2026-10-20', '2026-10-21', '2026-10-22', '2026-10-23']
    gold_path = [4240, 4252, 4261, 4270, 4281]
    for i, d in enumerate(week_days):
        g = (gold_path[i], gold_path[i] + 22, gold_path[i] - 18)
        if d == '2026-10-22':   # 当天全球采集失败: 只有前一天的锚点文件
            ch, n, st = quiet(dpo.observe, views_path=vp, anchors=day_anchors('2026-10-21', gold=(gold_path[i - 1], gold_path[i - 1] + 22, gold_path[i - 1] - 18)),
                              today_str=d, anchors_date='20261021')
            check(f"day{d} 采集失败→关键FAIL不写观察", st == 'FAIL' and ch == [])
            continue
        ch, n, st = quiet(dpo.observe, views_path=vp, anchors=day_anchors(d, gold=g),
                          today_str=d, anchors_date=d.replace('-', ''))
        if d == '2026-10-20':   # 同日幂等重跑
            ch2, _, st2 = quiet(dpo.observe, views_path=vp, anchors=day_anchors(d, gold=g),
                                today_str=d, anchors_date=d.replace('-', ''))
            check(f"day{d} 同日重跑幂等(无重复观测)", ch2 == [] and st2 == 'PASS', str(ch2))
    saved = json.load(open(vp))
    pg = next(p for p in saved['predictions'] if p['pred_id'] == 31)
    ps = next(p for p in saved['predictions'] if p['pred_id'] == 32)
    check("模拟A 4个成功交易日各记录1条金观察(10-22失败日无记录)",
          [o['obs_date'] for o in pg['observations']] ==
          ['2026-10-19', '2026-10-20', '2026-10-21', '2026-10-23'], str(pg['observations']))
    check("模拟B 盘中高/低随观察一并记录(high口径可裁)",
          all('high' in o for o in pg['observations']), str(pg['observations'][:1]))
    # ── 周五周报环节: 同批锚点→PASS→论点+观点+预测裁决 ──
    fri_anchors = day_anchors('2026-10-23', gold=(gold_path[4], gold_path[4] + 22, gold_path[4] - 18))
    fri_anchors.update({'macro.data.CCC_OAS.value': {'value': 9.2, 'obs_date': '2026-10-23',
                                                     'as_of': '2026-10-23'}})
    rep_w = block([{'id': 1, 'rating': '标配', 'confidence': 2, 'note': '维持',
                    'evidence': [{'metric': 'macro.data.CCC_OAS.value', 'value': 9.2,
                                  'obs_date': '2026-10-23', 'mechanism': '信用'}]},
                  ], 'ALLOCATION_STATUS') \
        + block([{'pred_id': 31, 'status': 'hit', 'note': '金价4281(2026-10-23观测)触及4400'}],
                'PREDICTION_STATUS') \
        + block([{'id': 1, 'status': '进行中', 'confidence': 2, 'note': '信用回稳',
                  'evidence': [{'metric': 'macro.data.CCC_OAS.value', 'value': 9.2,
                                'obs_date': '2026-10-23', 'mechanism': '信用'}]},
                 {'id': 2, 'status': '待观察', 'confidence': 2, 'note': '维持'}], 'THESIS_STATUS')
    tu, blocked = quiet(apply_status_updates, rep_w, 'PASS', anchors=fri_anchors,
                        today_str='2026-10-23', thesis_path=tp, views_path=vp)
    saved = json.load(open(vp))
    pg = next(p for p in saved['predictions'] if p['pred_id'] == 31)
    th = json.load(open(tp))
    check("模拟C GLM虚构hit(4281从未≥4400)被拒,预测保持观察中",
          pg['status'] == 'observing', pg['status'])
    check("模拟D 论点与观点共用同一批锚点与截止(时间一致,双侧last_updated=10-23)",
          th['last_updated'] == '2026-10-23' and saved['last_updated'] == '2026-10-23')
    check("模拟E 论点#2的失效触发器每周核验并落盘trigger_state(CCC9.2未触发)",
          'T2-INV1' in (th['theses'][1].get('trigger_state') or {})
          and th['theses'][1]['status'] == '待观察',
          str(th['theses'][1].get('trigger_state')))
    check("模拟F 全部观察记录观测日≤研究截止10-23(无未来数据)",
          all(o['obs_date'] <= '2026-10-23' for p in saved['predictions']
              for o in p.get('observations', [])))
    # ── 失败隔离: FAIL周报不污染已推进的状态 ──
    snap_v, snap_t = open(vp).read(), open(tp).read()
    bad_rep = block([{'id': 1, 'rating': '超配', 'confidence': 5, 'note': 'x'}], 'ALLOCATION_STATUS')
    quiet(apply_status_updates, bad_rep, 'FAIL', anchors=fri_anchors, today_str='2026-10-23',
          thesis_path=tp, views_path=vp)
    check("模拟G 校验FAIL不污染已推进的连续状态",
          open(vp).read() == snap_v and open(tp).read() == snap_t)

print("\n" + "=" * 64)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 64)
sys.exit(0 if FAIL == 0 else 1)
