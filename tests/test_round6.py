#!/usr/bin/env python3
"""第六轮最终可靠性补丁测试(2026-10-12) — 纯离线,不调用GLM

任务书第五节20项强制回归用例 + 对抗补充。全部断言落盘后的JSON状态
或函数真实行为(非源码字符串匹配)。临时目录沙盒,不污染真实状态文件。

  1  过期数据跳过后不写入(P0-1: GOLD stale / SPX正常 / PARTIAL / 日志说明原因)
  2  未来观测日不写入(P0-1)
  3  缺失观测日不写入(P0-1: 不得以采集日替代实际观测日)
  4  过期前提数据不激活(P0-1)
  5  单资产失败只隔离受影响预测(P0-1)
  6  同日重跑幂等(P0-1)
  7  截止日后前提兑现不重激活(P0-2: 终态+不顺延+无新观察期)
  8  有效期内前提触发正确转观察中(P0-2正例)
  9  终态预测不被每日观察任务重开(P0-2)
  10 expiry结算日缺数据不得用前一日价格(P0-3: 4350/4320在,10-16缺→inconclusive)
  11 expiry命中(10-16=4310→hit)
  12 expiry证伪(10-16=4340→miss)
  13 非交易日截止映射(周六→周五10-30;再缺不回退10-29)
  14 结算数据缺失不挑有利价格(全链路: GLM拿前一日满足值也被拒)
  15 GLM不得用错误结算日翻案(P0-3)
  16 touch提前命中不被Expiry修复破坏
  17 touch覆盖不足不判miss
  18 月度/季度统计不把缺数据当失败(inconclusive不计入hit/miss)
  19 既有预测JSON兼容升级(final标记向后兼容)
  20 FAIL不改长期状态

对抗补充: X1 crypto自然日结算 / X2 GLM终态翻案被拒 / X3 绕过观察器直调
record_observations的防御 / X4 未触发终态落final后不可重开 / X5 同批数据
连续四周端到端(前提触发→观察→到期裁决→终态封存→重跑不变)。

运行: ~/AI内容/venv/bin/python3 tests/test_round6.py
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
    """静默执行并捕获stdout — 返回(结果, 输出文本)"""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = fn(*a, **kw)
    return r, buf.getvalue()


def block(objs, tag):
    lines = "\n".join(json.dumps(o, ensure_ascii=False) for o in objs)
    return f"<!--{tag}\n{lines}\n{tag}-->"


import allocation_engine as ae
from report_generator import apply_status_updates
import daily_prediction_observer as dpo

TODAY = '2026-10-20'   # 周二


def anchors(**over):
    a = {
        'global_market.data.GOLD.close': {'value': 4240.0, 'obs_date': TODAY, 'as_of': TODAY},
        'global_market.data.GOLD.high': {'value': 4262.0, 'obs_date': TODAY, 'as_of': TODAY},
        'global_market.data.GOLD.low': {'value': 4218.0, 'obs_date': TODAY, 'as_of': TODAY},
        'global_market.data.SPX.close': {'value': 7620.0, 'obs_date': TODAY, 'as_of': TODAY},
        'macro.data.CCC_OAS.value': {'value': 9.2, 'obs_date': TODAY, 'as_of': TODAY},
        'macro.data.TIPS_10Y.value': {'value': 2.89, 'obs_date': TODAY, 'as_of': TODAY},
    }
    a.update(over)
    return a


def gold_pred(pid, **kw):
    p = {'pred_id': pid, 'date_made': '2026-10-06', 'asset': '金', 'deadline': '2026-10-30',
         'direction': '金价观察', 'status': 'observing', 'observe_from': '2026-10-06',
         'metric': 'global_market.data.GOLD.close', 'comparator': '>=', 'target': 4400,
         'verify_mode': 'touch', 'price_basis': 'close', 'observations': []}
    p.update(kw)
    return p


def cond_pred(pid, deadline='2026-10-30', premise_target=9.0, **kw):
    """带前提规格的条件预测: 前提CCC_OAS>=target兑现才开始结果观察"""
    p = {'pred_id': pid, 'date_made': '2026-10-06', 'asset': '金', 'deadline': deadline,
         'direction': '若信用利差走阔金价上涨', 'status': 'not_yet_triggered',
         'metric': 'global_market.data.GOLD.close', 'comparator': '>=', 'target': 4400,
         'verify_mode': 'touch', 'price_basis': 'close', 'observations': [],
         'premise': {'metric': 'macro.data.CCC_OAS.value', 'op': '>=', 'target': premise_target}}
    p.update(kw)
    return p


def views_file(td, preds=None):
    path = os.path.join(td, 'allocation_views.json')
    data = {'version': '6.0',
            'views': [{'id': 5, 'asset': '贵金属', 'rating': '标配', 'confidence': 2,
                       'history': []}],
            'predictions': preds or []}
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    return path


print("=" * 64)
print("第六轮最终可靠性补丁 — 20项任务书用例 + 对抗补充")
print("=" * 64)

# ════════ 1. 过期数据跳过后不写入 (P0-1) ════════
print("\n── 1. 过期锚点: 跳过预测且不写入观察历史(P0-1)")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[
        gold_pred(1, observe_from=TODAY),           # 目标指标=GOLD(过期)
        cond_pred(2, deadline='2026-10-22'),        # 前提指标=CCC(当日,值9.2>=9→应激活)
        {'pred_id': 3, 'date_made': '2026-10-06', 'asset': '股', 'deadline': '2026-10-30',
         'direction': 'SPX观察', 'status': 'observing', 'observe_from': '2026-10-06',
         'metric': 'global_market.data.SPX.close', 'comparator': '<=', 'target': 7600,
         'verify_mode': 'touch', 'observations': []},
    ])
    stale = anchors(**{'global_market.data.GOLD.close': {'value': 4240.0, 'obs_date': '2026-10-10',
                                                         'as_of': TODAY},
                       'global_market.data.GOLD.high': {'value': 4262.0, 'obs_date': '2026-10-10',
                                                        'as_of': TODAY},
                       'global_market.data.GOLD.low': {'value': 4218.0, 'obs_date': '2026-10-10',
                                                       'as_of': TODAY}})
    (ch, n, st), log = quiet(dpo.observe, views_path=vp, anchors=stale, today_str=TODAY,
                             anchors_date=TODAY.replace('-', ''))
    saved = json.load(open(vp))
    pg = next(p for p in saved['predictions'] if p['pred_id'] == 1)
    pc = next(p for p in saved['predictions'] if p['pred_id'] == 2)
    ps = next(p for p in saved['predictions'] if p['pred_id'] == 3)
    check("N1a GOLD观测日10-10过期→预测#1跳过(无新观察)",
          st == 'PARTIAL' and pg['observations'] == [], f"{st} {pg['observations']}")
    check("N1b 日志准确说明GOLD跳过原因(过期/新鲜度)",
          '预测#1' in log and ('新鲜度' in log or '采集失败' in log), log[-300:])
    check("N1c SPX当日数据照常记录(单资产失败不阻断其他)",
          any(o['obs_date'] == TODAY for o in ps['observations']), str(ps['observations']))
    check("N1d 前提指标(CCC)当日有效→预测#2正常激活,不受GOLD问题影响",
          pc['status'] == 'observing' and pc.get('observe_from') == TODAY, str(pc.get('status')))

# ════════ 2. 未来观测日不写入 (P0-1) ════════
print("\n── 2. 未来观测日不写入(P0-1)")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[gold_pred(11)])
    fut = anchors(**{'global_market.data.GOLD.close': {'value': 4240.0, 'obs_date': '2026-10-25',
                                                       'as_of': TODAY}})
    (ch, n, st), log = quiet(dpo.observe, views_path=vp, anchors=fut, today_str=TODAY,
                             anchors_date=TODAY.replace('-', ''))
    pg = json.load(open(vp))['predictions'][0]
    check("N2 观测日10-25>今日10-20→不写入,留跳过日志",
          pg['observations'] == [] and st == 'PARTIAL' and '未来' in log,
          f"{st} {pg['observations']} | {log[-200:]}")

# ════════ 3. 缺失观测日不写入 (P0-1) ════════
print("\n── 3. 缺失obs_date不写入(不得以采集日替代实际观测日)")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[gold_pred(12)])
    nod = anchors(**{'global_market.data.GOLD.close': {'value': 4240.0, 'as_of': TODAY}})
    (ch, n, st), log = quiet(dpo.observe, views_path=vp, anchors=nod, today_str=TODAY,
                             anchors_date=TODAY.replace('-', ''))
    pg = json.load(open(vp))['predictions'][0]
    check("N3 锚点无obs_date→不写入(引擎不得以today补盖观测日)",
          pg['observations'] == [] and 'obs_date' not in log or (
              pg['observations'] == [] and '观测日' in log),
          f"{pg['observations']} | {log[-200:]}")
    check("N3b 落盘JSON中不存在以采集日冒充观测日的记录",
          all(o.get('obs_date') != TODAY for o in pg['observations']))

# ════════ 4. 过期前提数据不激活 (P0-1) ════════
print("\n── 4. 过期前提锚点不激活条件预测(P0-1)")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[cond_pred(13, deadline='2026-10-22')])
    stale_prem = anchors(**{'macro.data.CCC_OAS.value': {'value': 9.5, 'obs_date': '2026-10-05',
                                                         'as_of': TODAY}})
    (ch, n, st), log = quiet(dpo.observe, views_path=vp, anchors=stale_prem, today_str=TODAY,
                             anchors_date=TODAY.replace('-', ''))
    pc = json.load(open(vp))['predictions'][0]
    check("N4 前提锚点观测日10-05(超新鲜度窗)且值9.5已满足→仍不激活",
          pc['status'] == 'not_yet_triggered' and 'observe_from' not in pc
          and pc['observations'] == [], str({k: pc.get(k) for k in ('status', 'observe_from')}))

# ════════ 5. 单资产失败只隔离受影响预测 (P0-1) ════════
print("\n── 5. 单资产采集失败只隔离受影响预测")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[gold_pred(14), {'pred_id': 15, 'date_made': '2026-10-06',
                                               'asset': '股', 'deadline': '2026-10-30',
                                               'direction': 'SPX', 'status': 'observing',
                                               'observe_from': '2026-10-06',
                                               'metric': 'global_market.data.SPX.close',
                                               'comparator': '<=', 'target': 7600,
                                               'verify_mode': 'touch', 'observations': [
                                                   {'obs_date': '2026-10-19', 'value': 7610.0}]}])
    a5 = anchors()
    for k in list(a5):
        if k.startswith('global_market.data.GOLD'):
            del a5[k]   # GOLD本轮整个资产缺失
    (ch, n, st), log = quiet(dpo.observe, views_path=vp, anchors=a5, today_str=TODAY,
                             anchors_date=TODAY.replace('-', ''))
    saved = json.load(open(vp))
    pg = next(p for p in saved['predictions'] if p['pred_id'] == 14)
    ps = next(p for p in saved['predictions'] if p['pred_id'] == 15)
    check("N5a GOLD资产缺失→预测#14跳过,既有观察历史不被清空/污染",
          st == 'PARTIAL' and pg['observations'] == [], f"{st} {pg['observations']}")
    check("N5b SPX预测照常新增当日观测(前日记录保留)",
          [o['obs_date'] for o in ps['observations']] == ['2026-10-19', TODAY],
          str(ps['observations']))

# ════════ 6. 同日重跑幂等 (P0-1) ════════
print("\n── 6. 同日重跑幂等(不产生重复观察)")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[gold_pred(16)])
    a6 = anchors()
    for _ in range(5):
        (ch, n, st), _ = quiet(dpo.observe, views_path=vp, anchors=a6, today_str=TODAY,
                               anchors_date=TODAY.replace('-', ''))
    pg = json.load(open(vp))['predictions'][0]
    check("N6 同批锚点同日跑5次: 仍只1条观察,第2次起无变更",
          len(pg['observations']) == 1, str(pg['observations']))

# ════════ 7. 截止日后前提兑现不重激活 (P0-2) ════════
print("\n── 7. 过期条件预测: 前提10-20才兑现(截止10-15)→保持未触发终态")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[cond_pred(17, deadline='2026-10-15')])
    a7 = anchors()   # CCC 9.2>=9 满足,obs_date=10-20(晚于截止)
    (ch, n, st), log = quiet(dpo.observe, views_path=vp, anchors=a7, today_str=TODAY,
                             anchors_date=TODAY.replace('-', ''))
    pc = json.load(open(vp))['predictions'][0]
    check("N7a 前提10-20兑现晚于截止10-15→不转observing,无observe_from",
          pc['status'] == 'not_yet_triggered' and 'observe_from' not in pc, str(pc.get('status')))
    check("N7b 截止日不顺延(deadline仍为10-15)",
          pc['deadline'] == '2026-10-15', pc.get('deadline'))
    check("N7c 截止日后无结果观察写入(observations为空)",
          pc['observations'] == [], str(pc['observations']))
    check("N7d 日志说明不激活原因(截止日不顺延)",
          '不顺延' in log, log[-200:])
    # 周报引擎终态化后,每日任务亦不得重开
    rep = block([{'pred_id': 17, 'status': 'not_yet_triggered', 'note': '前提未兑现'}],
                'PREDICTION_STATUS')
    quiet(ae.update_allocation_status, rep, views_path=vp, anchors=a7, today_str=TODAY)
    pc = json.load(open(vp))['predictions'][0]
    check("N7e 周报终态化(引擎到期未触发)→final标记落盘",
          pc.get('final') is True and pc['status'] == 'not_yet_triggered', str(pc.get('final')))
    a7b = anchors(**{'macro.data.CCC_OAS.value': {'value': 9.5, 'obs_date': '2026-10-14',
                                                  'as_of': '2026-10-21'}})  # 窗内迟到的触发
    (ch2, _, _), _ = quiet(dpo.observe, views_path=vp, anchors=a7b, today_str='2026-10-21',
                           anchors_date='20261021')
    pc = json.load(open(vp))['predictions'][0]
    check("N7f 终态后即使发现窗内(10-14)前提记录,每日任务也不得重开",
          pc['status'] == 'not_yet_triggered' and 'observe_from' not in pc
          and ch2 == [], f"{pc.get('status')} {ch2}")

# ════════ 8. 有效期内前提触发正确转观察中 (P0-2正例) ════════
print("\n── 8. 窗内前提触发→正确进入观察(P0-2正例)")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[cond_pred(18, deadline='2026-10-28')])
    a8 = anchors(**{'macro.data.CCC_OAS.value': {'value': 9.5, 'obs_date': '2026-10-15',
                                                 'as_of': '2026-10-16'}})
    (ch, n, st), _ = quiet(dpo.observe, views_path=vp, anchors=a8, today_str='2026-10-16',
                           anchors_date='20261016')
    pc = json.load(open(vp))['predictions'][0]
    check("N8a 前提10-15兑现(≤截止10-28)→转观察中,observe_from=前提观测日",
          pc['status'] == 'observing' and pc.get('observe_from') == '2026-10-15'
          and pc.get('premise_triggered_date') == '2026-10-15',
          str({k: pc.get(k) for k in ('status', 'observe_from', 'premise_triggered_date')}))
    check("N8b 前提观测日≠采集日(10-15≠10-16),结果观察期自前提观测日起",
          pc.get('observe_from') == '2026-10-15' and pc.get('observe_from') != '2026-10-16')

# ════════ 9. 终态预测不被每日观察任务重开 (P0-2) ════════
print("\n── 9. 终态预测不被每日任务重开/重复裁决")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[
        gold_pred(19, status='hit', resolved_date='2026-10-10',
                  resolved_note='金价4450(2026-10-10观测)触及',
                  observations=[{'obs_date': '2026-10-10', 'value': 4450.0}]),
        {'pred_id': 20, 'date_made': '2026-10-01', 'asset': '股', 'deadline': '2026-10-15',
         'direction': '旧记录(无final字段)', 'status': 'miss', 'resolved_date': '2026-10-16',
         'resolved_note': '到期未达', 'metric': 'global_market.data.SPX.close',
         'comparator': '>=', 'target': 8000, 'verify_mode': 'expiry',
         'observations': [{'obs_date': '2026-10-15', 'value': 7500.0}]},
    ])
    before = json.load(open(vp))
    (ch, n, st), _ = quiet(dpo.observe, views_path=vp, anchors=anchors(), today_str=TODAY,
                           anchors_date=TODAY.replace('-', ''))
    after = json.load(open(vp))
    p19 = next(p for p in after['predictions'] if p['pred_id'] == 19)
    p20 = next(p for p in after['predictions'] if p['pred_id'] == 20)
    check("N9a 已hit终态预测: 每日任务不追加观察不改状态",
          p19['status'] == 'hit' and len(p19['observations']) == 1
          and p19['resolved_date'] == '2026-10-10', str(p19.get('resolved_date')))
    check("N9b 旧miss记录(无final字段)同样不被重开,历史观察保留",
          p20['status'] == 'miss' and len(p20['observations']) == 1
          and p20['resolved_date'] == '2026-10-16', str(p20))
    check("N9c 终态预测不产生任何观察变更(ch为空或不含#19/#20)",
          all('#19' not in c and '#20' not in c for c in ch), str(ch))

# ════════ 10-12. expiry严格结算口径 (P0-3) ════════
print("\n── 10. 结算日缺数据不得用前一日价格(P0-3)")
sp = {'pred_id': 21, 'date_made': '2026-10-06', 'asset': '股', 'deadline': '2026-10-16',
      'direction': 'SPX到期收4330下', 'status': 'observing', 'observe_from': '2026-10-06',
      'metric': 'global_market.data.SPX.close', 'comparator': '<=', 'target': 4330,
      'verify_mode': 'expiry', 'price_basis': 'close'}
v = quiet(ae.evaluate_predictions, {'predictions': [dict(sp, observations=[
    {'obs_date': '2026-10-14', 'value': 4350.0},
    {'obs_date': '2026-10-15', 'value': 4320.0}])]}, today_str='2026-10-16')[0][0]
check("N10 10-14=4350/10-15=4320在但10-16缺→inconclusive(不拿4320判hit)",
      v[2] == 'inconclusive' and '4320' not in v[3] and '不得以前一交易日' in v[3], str(v))
print("\n── 11. expiry命中")
v = quiet(ae.evaluate_predictions, {'predictions': [dict(sp, observations=[
    {'obs_date': '2026-10-14', 'value': 4350.0},
    {'obs_date': '2026-10-16', 'value': 4310.0}])]}, today_str='2026-10-16')[0][0]
check("N11 10-16=4310≤4330→hit(按结算日当日值)",
      v[2] == 'hit' and '4310' in v[3], str(v))
print("\n── 12. expiry证伪")
v = quiet(ae.evaluate_predictions, {'predictions': [dict(sp, observations=[
    {'obs_date': '2026-10-15', 'value': 4320.0},
    {'obs_date': '2026-10-16', 'value': 4340.0}])]}, today_str='2026-10-16')[0][0]
check("N12 10-16=4340>4330→miss(前一日4320满足不算)",
      v[2] == 'miss' and '4340' in v[3], str(v))

# ════════ 13. 非交易日截止映射 (P0-3) ════════
print("\n── 13. 非交易日截止=预定义回溯交易日(不进一步回退)")
sat = {'pred_id': 22, 'date_made': '2026-10-06', 'asset': '股', 'deadline': '2026-10-31',
       'direction': 'SPX月底收4300下', 'status': 'observing', 'observe_from': '2026-10-06',
       'metric': 'global_market.data.SPX.close', 'comparator': '<=', 'target': 4300,
       'verify_mode': 'expiry', 'price_basis': 'close'}
check("N13a settlement(周六2026-10-31,us)=周五10-30",
      ae.settlement_date('2026-10-31', 'us') == '2026-10-30')
v = quiet(ae.evaluate_predictions, {'predictions': [dict(sat, observations=[
    {'obs_date': '2026-10-29', 'value': 4250.0}])]}, today_str='2026-10-31')[0][0]
check("N13b 只有10-29(周四)观测,10-30缺→inconclusive(不回退用10-29裁决)",
      v[2] == 'inconclusive' and '10-30' in v[3], str(v))
v = quiet(ae.evaluate_predictions, {'predictions': [dict(sat, observations=[
    {'obs_date': '2026-10-29', 'value': 4250.0},
    {'obs_date': '2026-10-30', 'value': 4340.0}])]}, today_str='2026-10-31')[0][0]
check("N13c 10-30=4340>4300→miss(周六截止按周五价,周四4250不算)",
      v[2] == 'miss' and '4340' in v[3] and '4250' not in v[3], str(v))

# ════════ 14. 结算数据缺失不挑有利价格(全链路含GLM) (P0-3) ════════
print("\n── 14. 全链路: GLM拿前一日满足值也被拒(P0-3)")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[dict(sp, observations=[
        {'obs_date': '2026-10-14', 'value': 4350.0},
        {'obs_date': '2026-10-15', 'value': 4320.0}])])
    rep = block([{'pred_id': 21, 'status': 'hit',
                  'note': 'SPX 4320<=4330(观测日2026-10-15)到期达标'}], 'PREDICTION_STATUS')
    ups, _ = quiet(ae.update_allocation_status, rep, views_path=vp, anchors=anchors(),
                   today_str='2026-10-16')
    p21 = json.load(open(vp))['predictions'][0]
    check("N14 Python判inconclusive时,GLM引前一日(10-15)真实记录判hit→拒,落inconclusive",
          p21['status'] == 'inconclusive' and p21.get('final') is True
          and any('被拒' in u or 'inconclusive' in u for u in ups), f"{p21['status']} {ups}")

# ════════ 15. GLM不得用错误结算日翻案 (P0-3) ════════
print("\n── 15. GLM引用错误结算日→拒(P0-3)")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[dict(sp, observations=[
        {'obs_date': '2026-10-15', 'value': 4320.0},
        {'obs_date': '2026-10-16', 'value': 4310.0}])])   # 结算日当日有值
    rep = block([{'pred_id': 21, 'status': 'miss',
                  'note': 'SPX 4320(观测日2026-10-15)超4330→证伪'}], 'PREDICTION_STATUS')
    ups, _ = quiet(ae.update_allocation_status, rep, views_path=vp, anchors=anchors(),
                   today_str='2026-10-16')
    p21 = json.load(open(vp))['predictions'][0]
    check("N15 引擎hit(10-16=4310)时,GLM拿10-15判miss→拒(引擎优先+结算日口径一致)",
          p21['status'] == 'hit' and any('不可覆盖' in u for u in ups), f"{p21['status']} {ups}")

# ════════ 16. touch提前命中不被破坏 (P1-3) ════════
print("\n── 16. touch提前命中保留(Expiry修复不影响touch)")
p16 = gold_pred(23, price_basis='high', deadline='2026-10-30', observations=[
    {'obs_date': '2026-10-13', 'value': 4250.0, 'high': 4262.0, 'low': 4241.0},
    {'obs_date': '2026-10-14', 'value': 4280.0, 'high': 4450.0, 'low': 4270.0},  # 盘中触及
])
v = quiet(ae.evaluate_predictions, {'predictions': [p16]}, today_str='2026-10-14')[0][0]
check("N16 touch窗内high 4450≥4400→提前hit(其余日期缺失不影响)",
      v[2] == 'hit' and '2026-10-14' in v[3], str(v))

# ════════ 17. touch覆盖不足不判miss (P1) ════════
print("\n── 17. touch覆盖不足→inconclusive(缺数据≠失败)")
p17 = gold_pred(24, price_basis='high', deadline='2026-10-16', observe_from='2026-10-02',
                observations=[{'obs_date': d, 'value': 4250.0 + i * 5, 'high': 4255.0 + i * 5}
                              for i, d in enumerate(['2026-10-05', '2026-10-06', '2026-10-09'])])
v = quiet(ae.evaluate_predictions, {'predictions': [p17]}, today_str='2026-10-16')[0][0]
check("N17 仅3个交易日high且都<4400→inconclusive(覆盖不足不判miss)",
      v[2] == 'inconclusive' and ('覆盖' in v[3] or '无法证明' in v[3]), str(v))

# ════════ 18. 月度/季度统计不把缺数据当失败 (P1-7) ════════
print("\n── 18. 统计口径: inconclusive不计入hit/miss")
stat_preds = {'predictions': [
    {'pred_id': 31, 'deadline': '2026-10-16', 'status': 'inconclusive',
     'resolved_date': '2026-10-16', 'metric': 'global_market.data.SPX.close',
     'comparator': '<=', 'target': 4330, 'verify_mode': 'expiry'},
    {'pred_id': 32, 'deadline': '2026-10-16', 'status': 'hit', 'resolved_date': '2026-10-16',
     'metric': 'm', 'comparator': '>=', 'target': 1},
    {'pred_id': 33, 'deadline': '2026-10-16', 'status': 'observing'},
]}
counts = quiet(ae.predictions_in_period, stat_preds, '2026-10-01', '2026-10-31')[0]['counts']
check("N18 结算数据缺失的inconclusive不计入hit/miss(数据缺失≠预测失败)",
      counts['inconclusive'] == 1 and counts['hit'] == 1 and counts['miss'] == 0, str(counts))

# ════════ 19. 既有预测JSON兼容升级 (P0-2) ════════
print("\n── 19. 旧JSON无损升级(final向后兼容)")
old_style = {'version': '4.0', 'predictions': [
    {'pred_id': 41, 'date_made': '2026-09-01', 'asset': '金', 'deadline': '2026-09-15',
     'direction': '旧命中', 'status': 'hit', 'resolved_date': '2026-09-15',
     'resolved_note': 'ok', 'metric': 'global_market.data.GOLD.close',
     'comparator': '>=', 'target': 4000, 'verify_mode': 'touch',
     'observations': [{'obs_date': '2026-09-10', 'value': 4050.0}]},
    {'pred_id': 42, 'date_made': '2026-10-01', 'asset': '股', 'deadline': '2026-10-30',
     'direction': '进行中', 'status': 'observing', 'observe_from': '2026-10-01',
     'metric': 'global_market.data.SPX.close', 'comparator': '>=', 'target': 7000,
     'verify_mode': 'expiry', 'observations': []},
]}
snap = json.dumps(old_style, ensure_ascii=False, sort_keys=True)
ae._migrate_views(old_style)
check("N19a 旧终态(hit)补final=True,非终态(observing)不加final",
      old_style['predictions'][0].get('final') is True
      and 'final' not in old_style['predictions'][1], str(old_style['predictions'][0].get('final')))
restored = json.loads(snap)
old_style2 = json.loads(snap)
ae._migrate_views(old_style2)
core_same = all(old_style2['predictions'][i].get(k) == restored['predictions'][i].get(k)
                for i in range(2)
                for k in ('status', 'resolved_date', 'observations', 'deadline', 'metric'))
check("N19b 升级只加字段不改变既有内容(状态/历史/观察全保留)",
      core_same, 'field drift')
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=restored['predictions'])
    data = json.load(open(vp))
    (ch, n, st), _ = quiet(dpo.observe, views_path=vp, anchors=anchors(), today_str=TODAY,
                           anchors_date=TODAY.replace('-', ''))
    saved = json.load(open(vp))
    p41 = next(p for p in saved['predictions'] if p['pred_id'] == 41)
    p42 = next(p for p in saved['predictions'] if p['pred_id'] == 42)
    check("N19c 升级后系统正常处理: 旧hit不被重开,进行中照常记录",
          p41['status'] == 'hit' and len(p41['observations']) == 1
          and any(o['obs_date'] == TODAY for o in p42['observations']),
          f"{p41['status']} {len(p41['observations'])}")

# ════════ 20. FAIL不改长期状态 (P1-10) ════════
print("\n── 20. 校验FAIL不写任何长期状态")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[gold_pred(43)])
    tp = os.path.join(td, 'thesis.json')
    with open(tp, 'w', encoding='utf-8') as f:
        json.dump({'theses': [{'id': 1, 'name': 'T1', 'status': '进行中', 'confidence': 2,
                               'history': [], 'quant_triggers': [], 'related_theses': []}],
                   'last_updated': '2026-10-01'}, f)
    before_v, before_t = open(vp).read(), open(tp).read()
    rep = block([{'id': 5, 'rating': '超配', 'confidence': 5, 'note': 'x'}], 'ALLOCATION_STATUS') \
        + block([{'pred_id': 43, 'status': 'hit', 'note': '虚构4450(2026-10-20)'}],
                'PREDICTION_STATUS')
    r, _ = quiet(apply_status_updates, rep, 'FAIL', anchors=anchors(), today_str=TODAY,
                 thesis_path=tp, views_path=vp)
    check("N20 FAIL→观点/论点/预测状态一字节不改",
          open(vp).read() == before_v and open(tp).read() == before_t)

# ══════════════════════════════════════════════════════════════════
# 对抗补充
# ══════════════════════════════════════════════════════════════════
print("\n── X1. crypto 7×24自然日结算(周六截止=周六当日)")
btc = {'pred_id': 51, 'date_made': '2026-10-20', 'asset': '币', 'deadline': '2026-10-31',
       'direction': 'BTC月底收10万上', 'status': 'observing', 'observe_from': '2026-10-20',
       'metric': 'global_market.data.BTC.close', 'comparator': '>=', 'target': 100000,
       'verify_mode': 'expiry', 'price_basis': 'close'}
check("X1a settlement(周六,crypto)=周六当日(不套用us日历)",
      ae.settlement_date('2026-10-31', 'crypto') == '2026-10-31')
v = quiet(ae.evaluate_predictions, {'predictions': [dict(btc, observations=[
    {'obs_date': '2026-10-31', 'value': 101000.0}])]}, today_str='2026-10-31')[0][0]
check("X1b 周六(10-31)当日有值→正常裁决hit",
      v[2] == 'hit' and '101000' in v[3], str(v))

print("\n── X2. GLM终态翻案被拒(P0-2)")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[gold_pred(52, status='hit', final=True,
                                         resolved_date='2026-10-10',
                                         resolved_note='4450触及',
                                         observations=[{'obs_date': '2026-10-10',
                                                        'value': 4450.0}])])
    rep = block([{'pred_id': 52, 'status': 'miss', 'note': '重新评估为证伪4450(2026-10-10)'}],
                'PREDICTION_STATUS')
    ups, _ = quiet(ae.update_allocation_status, rep, views_path=vp, anchors=anchors(),
                   today_str=TODAY)
    p52 = json.load(open(vp))['predictions'][0]
    check("X2 final hit预测被GLM改判miss→拒(终态不得翻案)",
          p52['status'] == 'hit' and any('终态' in u and '被拒' in u for u in ups),
          f"{p52['status']} {ups}")

print("\n── X3. 绕过观察器直调record_observations的防御(P0-1)")
views_x3 = {'predictions': [gold_pred(53, observe_from=TODAY)]}
anch_bad = {'global_market.data.GOLD.close': {'value': 4240.0, 'as_of': TODAY}}   # 无obs_date
ch, out = quiet(ae.record_observations, views_x3, anch_bad, TODAY)
check("X3a 直调引擎(无观察器过滤): 缺obs_date锚点仍不写入",
      views_x3['predictions'][0]['observations'] == [] and '不写入' in out, out[-150:])
anch_fut = {'global_market.data.GOLD.close': {'value': 4240.0, 'obs_date': '2026-10-25',
                                              'as_of': TODAY}}
ch, out = quiet(ae.record_observations, views_x3, anch_fut, TODAY)
check("X3b 直调引擎: 未来观测日仍不写入", views_x3['predictions'][0]['observations'] == [])
anch_old = {'global_market.data.GOLD.close': {'value': 4240.0, 'obs_date': '2026-10-01',
                                              'as_of': TODAY}}
ch, out = quiet(ae.record_observations, views_x3, anch_old, TODAY)
check("X3c 直调引擎: 超新鲜度窗仍不写入", views_x3['predictions'][0]['observations'] == [])

print("\n── X4. 未触发终态跨周不被GLM重开(P0-2)")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[cond_pred(54, deadline='2026-10-15')])
    # 第1周: 到期未触发→引擎终态化(落final)
    quiet(ae.update_allocation_status,
          block([{'pred_id': 54, 'status': 'not_yet_triggered', 'note': '前提未兑现'}],
                'PREDICTION_STATUS'),
          views_path=vp, anchors=anchors(), today_str='2026-10-16')
    # 第2周: GLM改判"转观察中"(前提兑现)
    ups, _ = quiet(ae.update_allocation_status,
                   block([{'pred_id': 54, 'status': 'observing', 'note': '前提10-20兑现'}],
                         'PREDICTION_STATUS'),
                   views_path=vp, anchors=anchors(), today_str=TODAY)
    p54 = json.load(open(vp))['predictions'][0]
    check("X4 终态未触发预测被GLM'转观察中'→拒(不被重新开启)",
          p54['status'] == 'not_yet_triggered' and p54.get('final') is True, str(p54.get('status')))

print("\n── X5. 连续状态端到端: 前提触发→观察→到期裁决→终态封存→重跑不变")
with tempfile.TemporaryDirectory() as td:
    vp = views_file(td, preds=[cond_pred(55, deadline='2026-10-16')])
    # 10-08: 前提兑现(CCC 9.5@10-08)→转观察
    a = anchors(**{'macro.data.CCC_OAS.value': {'value': 9.5, 'obs_date': '2026-10-08',
                                                'as_of': '2026-10-08'}})
    quiet(dpo.observe, views_path=vp, anchors=a, today_str='2026-10-08', anchors_date='20261008')
    p55 = json.load(open(vp))['predictions'][0]
    check("X5a 前提窗内兑现→observing+observe_from=2026-10-08",
          p55['status'] == 'observing' and p55.get('observe_from') == '2026-10-08')
    # 10-09~10-16: 每日观察(金10-12采集失败跳过)
    path = [4240, 4455, 4460, None, 4470, 4480]
    for d, v in zip(['2026-10-09', '2026-10-13', '2026-10-14', '2026-10-15', '2026-10-16'],
                    [4240, 4455, 4460, 4470, 4480]):
        a = anchors(**{'global_market.data.GOLD.close': {'value': float(v), 'obs_date': d,
                                                         'as_of': d}})
        if d == '2026-10-15':   # 当日GOLD采集失败: 用10-14旧锚点文件
            a = anchors(**{'global_market.data.GOLD.close': {'value': 4460.0,
                                                             'obs_date': '2026-10-14',
                                                             'as_of': '2026-10-15'}})
            quiet(dpo.observe, views_path=vp, anchors=a, today_str=d, anchors_date='20261014')
            continue
        quiet(dpo.observe, views_path=vp, anchors=a, today_str=d, anchors_date=d.replace('-', ''))
    p55 = json.load(open(vp))['predictions'][0]
    check("X5b 观察记录=前提日起4条有效日(10-15失败日不写入,10-08前提日本身无目标锚点)",
          [o['obs_date'] for o in p55['observations']] ==
          ['2026-10-09', '2026-10-13', '2026-10-14', '2026-10-16'], str(p55['observations']))
    # 10-16(到期日,周五): 周报裁决 — touch模式,10-13盘中high未及,close 4480≥4400
    quiet(ae.update_allocation_status,
          block([{'id': 5, 'rating': '标配', 'confidence': 2, 'note': '维持'}],
                'ALLOCATION_STATUS'), views_path=vp, anchors=anchors(), today_str='2026-10-16')
    p55 = json.load(open(vp))['predictions'][0]
    check("X5c 到期裁决hit(10-16收盘4480≥4400)且落final",
          p55['status'] == 'hit' and p55.get('final') is True, str(p55.get('status')))
    snap = open(vp).read()
    # 次日(10-17)与次周(10-20)再跑每日任务+周报: 状态不变
    for d in ('2026-10-17', '2026-10-20'):
        quiet(dpo.observe, views_path=vp, anchors=anchors(), today_str=d,
              anchors_date=d.replace('-', ''))
        quiet(ae.update_allocation_status,
              block([{'pred_id': 55, 'status': 'miss', 'note': '重新评估: 未触及4400'}],
                    'PREDICTION_STATUS'), views_path=vp, anchors=anchors(), today_str=d)
    after = json.load(open(vp))['predictions'][0]
    check("X5d 终态封存后重复运行(每日+周报+GLM翻案)状态与审计日期不变",
          after['status'] == 'hit' and after['resolved_date'] == '2026-10-16'
          and len(after['observations']) == 4, str({k: after.get(k) for k in ('status', 'resolved_date')}))

print("\n── X6. run_weekly汇总路径回归(2026-10-13真实调度发现的解包崩溃)")
import run_weekly as rw
# launchd真实运行发现: run_pipeline改3元组(第五轮P1-2)后,汇总计数行仍按2元组
# 解包→ValueError→exit 1 — 10步全部成功却报关键失败。本用例锁死汇总路径行为。
fake = [('1/10 a', True, True), ('4/10 b', False, False), ('9/10 c', True, True)]
_orig_rp = rw.run_pipeline
rw.run_pipeline = lambda steps, script_dir=None: fake
try:
    buf = io.StringIO()
    code = 'no-exit'
    with contextlib.redirect_stdout(buf):
        try:
            rw.main()
        except SystemExit as e:
            code = e.code
    out = buf.getvalue()
    check("X6a 非关键失败: 汇总完成不崩溃(2/10),降级公示,不判失败退出",
          '2/10' in out and '非关键步骤降级运行' in out and code != 1,
          f"exit={code} | {out[-160:]}")
    rw.run_pipeline = lambda steps, script_dir=None: [('1/10 a', False, True),
                                                      ('4/10 b', True, False)]
    code2 = 'no-exit'
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            rw.main()
        except SystemExit as e:
            code2 = e.code
    check("X6b 关键失败: exit 1(失败不被静默吞掉)", code2 == 1, str(code2))
    rw.run_pipeline = lambda steps, script_dir=None: [('1/10 a', True, True)]
    code3 = 'no-exit'
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            rw.main()
        except SystemExit as e:
            code3 = e.code
    check("X6c 全部成功: 正常完成不异常退出", code3 == 'no-exit' or code3 == 0, str(code3))
finally:
    rw.run_pipeline = _orig_rp

print("\n" + "=" * 64)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 64)
sys.exit(0 if FAIL == 0 else 1)
