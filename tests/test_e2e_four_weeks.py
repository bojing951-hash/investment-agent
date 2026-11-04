#!/usr/bin/env python3
"""端到端四周连续模拟测试(第三轮P1重写, 2026-10-11) — 纯离线,不调用GLM

第三轮要求: 四周使用同一份状态持续更新,不得每周重置观点库。
本文件与旧版的区别: 整个四周共用一个沙盒(tempdir)+同一份views/thesis,
W2看到W1的状态、W3看到W1+W2的累计状态(含触发器连续周数、被拒提案、观察记录)。

场景剧本(与 tests/fixtures/e2e 一一对应):
  W1(09-25) 初始观点全维持(历史/触发器状态起算); 反例报告→FAIL→禁止回写
  W2(10-02) 评级不变+确信度2→3,附3项结构化证据(3类机制→程序星级3★支撑)
  W3(10-09) CCC 10.12破10.0→T1已触发→美股降级(经门禁);
            黄金升级提案无结构化证据→被拒+留档; TIPS持续三周≥2.5→T3持续触发;
            新预测touch模式登记; pred1定性前提兑现→转观察(观察期起算,截止日不变)
  W4(10-16) 黄金补交4项证据→升级经门禁通过(提案标记superseded);
            pred3 touch模式提前命中(SPX 7580≤7600); pred1 expiry未到期GLM提前hit→被拒;
            9月月报(已完结)+Q3季报(整季聚合); 12-25提前季报回归

运行: ~/AI内容/venv/bin/python3 tests/test_e2e_four_weeks.py
"""
import os
import sys
import io
import json
import shutil
import tempfile
import contextlib
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
FIX = os.path.join(ROOT, 'tests', 'fixtures', 'e2e')

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

print("=" * 60)
print("E2E四周连续模拟(单沙盒单状态,离线fixture)")
print("=" * 60)

import data_validator
import allocation_engine as ae
from report_generator import (_has_numeric_errors, update_thesis_status,
                              pending_completed_month, pending_completed_quarter)
import monthly_review as mr
import quarterly_outlook as qo

WEEKS = [('w1', '2026-09-25'), ('w2', '2026-10-02'),
         ('w3', '2026-10-09'), ('w4', '2026-10-16')]
REPORTS = {'w1': 'weekly_report_20260925.md', 'w2': 'weekly_report_20261002.md',
           'w3': 'weekly_report_20261009.md', 'w4': 'weekly_report_20261016.md'}


def run_week(week, td, views, thesis):
    """模拟report_generator主流程: 锚点→校验分级→(FAIL则跳过)→回写。
    连续性关键: views/thesis为同一沙盒文件,每周在其上周状态上继续更新。"""
    data_dir = os.path.join(FIX, f'{week}_data')
    anchors = quiet(data_validator.extract_anchors_from_data, data_dir)
    # IA-P0-1-FIX1: 旧版提取路径(extract_anchors_from_data)无quality字段——本套件
    # 被测对象是四周状态连续性,fixture统一注入quality='PASS'对齐新schema
    # (真实生产锚点由快照链携带quality;此处不注入会让FIX-04引擎防御把全部
    # 预测观察误判为质量不明而跳过,偏离本套件的测试意图)。
    for _a in anchors.values():
        if isinstance(_a, dict) and 'quality' not in _a:
            _a['quality'] = 'PASS'
    report_path = os.path.join(td, REPORTS[week])
    shutil.copy(os.path.join(FIX, 'reports', REPORTS[week]), report_path)
    warnings = quiet(data_validator.validate_report, report_path, anchors)
    classification, reason = data_validator.classify_result(
        True, True, warnings, _has_numeric_errors(warnings))
    if classification == 'FAIL':
        return classification, warnings, anchors
    # 第四轮P0-4: 论点回写与配置观点共用同一批锚点(与主流程apply_status_updates一致)
    quiet(update_thesis_status, open(report_path).read(), thesis_path=thesis,
          anchors=anchors, today_str=dict(WEEKS)[week])
    quiet(ae.update_allocation_status, open(report_path).read(),
          views_path=views, anchors=anchors, today_str=dict(WEEKS)[week])
    return classification, warnings, anchors


def view(saved, vid):
    return next(v for v in saved['views'] if v['id'] == vid)


def pred(saved, pid):
    return next(p for p in saved['predictions'] if p['pred_id'] == pid)


# ════════ 唯一沙盒: 四周连续推进 ════════
STATE = {}   # 跨周检查用
with tempfile.TemporaryDirectory() as td:
    views = os.path.join(td, 'allocation_views.json')
    thesis = os.path.join(td, 'thesis.json')
    shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), views)
    shutil.copy(os.path.join(ROOT, 'config', 'thesis.json'), thesis)

    # ════════ W1: 初始周 ════════
    print("\n[W1] 2026-09-25 初始观点 + 反例报告FAIL门禁")
    cls, warnings, anchors = run_week('w1', td, views, thesis)
    check("W1校验分级PASS", cls == 'PASS', f"{cls} {warnings}")
    check("W1锚点含CCC现值与前值", anchors.get('macro.data.CCC_OAS.value', {}).get('value') == 9.46
          and anchors.get('macro.data.CCC_OAS.prev', {}).get('value') == 9.40)
    check("W1锚点TIPS带观测日", anchors.get('macro.data.TIPS_10Y.value', {}).get('obs_date') == '2026-09-24')
    saved = json.load(open(views))
    v1 = view(saved, 1)
    check("W1全维持: id1仍标配2★", v1['rating'] == '标配' and v1['confidence'] == 2)
    check("W1维持也落盘(history有维持条目+last_updated)",
          any('维持' in h for h in v1['history']) and saved['last_updated'] == '2026-09-25')
    check("W1 thesis回写", json.load(open(thesis))['last_updated'] == '2026-09-25')
    # 触发器状态起算: W1 TIPS 2.92≥2.5 → T3连续第1周(持续确认中,3周才触发)
    ts5 = view(saved, 5).get('trigger_state', {}).get('T3', {})
    check("W1 T3(TIPS≥2.5持续3周)连续第1周", ts5.get('consec') == 1, str(ts5))

    # 反例: 数值错误+前值当现值 → FAIL → 回写被跳过(状态不变)
    bad_path = os.path.join(td, 'bad.md')
    shutil.copy(os.path.join(FIX, 'reports', 'bad_report_20260925.md'), bad_path)
    bw = quiet(data_validator.validate_report, bad_path, anchors)
    bcls, _ = data_validator.classify_result(True, True, bw, _has_numeric_errors(bw))
    check("反例报告分级FAIL", bcls == 'FAIL', f"{bcls} {bw}")
    check("反例含严重偏差错误(12.52 vs 9.46)", any('严重错误' in w for w in bw), str(bw))
    check("反例含前值当现值拦截(TIPS 2.93当现值)", any('前值当现值' in w for w in bw), str(bw))
    before = open(views).read()
    if bcls != 'FAIL':
        quiet(ae.update_allocation_status, open(bad_path).read(), views_path=views)
    check("FAIL时观点库未被反例污染", open(views).read() == before)

    # ════════ W2: 评级不变+确信度上调(证据支撑) ════════
    print("\n[W2] 2026-10-02 评级不变,确信度2→3(3项结构化证据→3★)")
    cls, warnings, anchors = run_week('w2', td, views, thesis)
    check("W2校验分级PASS", cls == 'PASS', f"{cls} {warnings}")
    saved = json.load(open(views))
    v1 = view(saved, 1)
    check("W2 id1确信度2→3已回写(证据星级3★支撑)", v1['confidence'] == 3, str(v1.get('confidence')))
    check("W2 id1评级不变(标配)", v1['rating'] == '标配')
    check("W2 确信度变化单独记录", any(h.startswith('10/2 确信度') and '2★→3★' in h for h in v1['history']),
          str(v1['history']))
    check("W2 证据台账留档(evidence_ledger)", view(saved, 1).get('evidence_ledger')
          and view(saved, 1)['evidence_ledger'][-1]['star_max'] >= 3)
    ts5 = view(saved, 5).get('trigger_state', {}).get('T3', {})
    check("W2 T3连续第2周(TIPS 2.90≥2.5,持续确认中)", ts5.get('consec') == 2, str(ts5))

    # ════════ W3: 触发降级(经门禁) + 无证据升级被拒 + touch预测登记 ════════
    print("\n[W3] 2026-10-09 T1触发→降级经门禁; 无证据升级被拒留档; T3持续3周触发")
    # 渲染层: 用W3锚点+连续状态核验触发器(T3应显示第3/3周→已触发)
    anchors3 = quiet(data_validator.extract_anchors_from_data, os.path.join(FIX, 'w3_data'))
    views_data = ae.load_views(views)
    trig = quiet(ae.evaluate_quant_triggers, views_data, anchors3, '2026-10-09')
    t1_3 = next(r for r in trig[3] if r['trig_id'] == 'T1')
    check("W3 触发器T1(CCC 10.12≥10.0)引擎核验=已触发", t1_3['status'] == 'triggered', str(t1_3))
    t3_5 = next(r for r in trig[5] if r['trig_id'] == 'T3')
    check("W3 T3持续条件第3周满额→已触发(非'持续确认中')", t3_5['status'] == 'triggered'
          and t3_5['consec'] == 3, str(t3_5))
    block = quiet(ae.render_views_block, views_data, '2026-10-09', anchors3)
    check("W3 渲染块含'✅已触发'", "✅已触发" in block)
    check("W3 渲染块标注待验证条件", "❓待验证" in block)

    cls, warnings, anchors = run_week('w3', td, views, thesis)
    check("W3校验分级PASS", cls == 'PASS', f"{cls} {warnings}")
    saved = json.load(open(views))
    v1, v5 = view(saved, 1), view(saved, 5)
    check("W3 id1评级标配→低配(经触发器门禁)", v1['rating'] == '低配')
    check("W3 评级变更审计留档(last_change含via/证据)",
          v1.get('last_change', {}).get('via', '').startswith('触发器')
          and v1['last_change'].get('from') == '标配' and v1['last_change'].get('to') == '低配',
          str(v1.get('last_change')))
    check("W3 评级变化单独记录", any(h.startswith('10/9 评级') and '标配→低配' in h for h in v1['history']),
          str(v1['history']))
    check("W3 id5无证据升级被拒: 仍观望", v5['rating'] == '观望', v5['rating'])
    pr = (v5.get('proposals') or [None])[-1]
    check("W3 被拒提案留档(含原因)", pr and pr['status'] == 'rejected' and pr['to'] == '标配'
          and '无引擎核验' in pr['reason'], str(pr))
    check("W3 提案未写评级(区别于正式变更)", v5['rating'] == '观望' and not any(
        h.startswith('10/9 评级') for h in v5['history']), str(v5['history']))
    new_p = max(saved['predictions'], key=lambda p: p['pred_id'])
    check("W3 新预测#3登记,touch模式,deadline=两周后",
          new_p['pred_id'] == 3 and new_p['deadline'] == '2026-10-23'
          and new_p.get('verify_mode') == 'touch', f"{new_p.get('pred_id')} {new_p.get('deadline')} {new_p.get('verify_mode')}")
    check("W3 新预测带量化规格+观察起点", new_p.get('metric') == 'global_market.data.SPX.close'
          and new_p.get('comparator') == '<=' and new_p.get('target') == 7600
          and new_p.get('observe_from') == '2026-10-09', str(new_p))
    check("W3 新预测状态=观察中(W3当周已记录SPX观测)",
          new_p['status'] == 'observing' and len(new_p.get('observations', [])) == 1,
          str(new_p.get('observations')))
    p1 = pred(saved, 1)
    check("W3 pred1定性前提兑现→转观察中(观察期自今日,截止日不变)",
          p1['status'] == 'observing' and p1.get('observe_from') == '2026-10-09'
          and p1['deadline'] == '2026-10-25', str({k: p1.get(k) for k in ('status', 'observe_from', 'deadline')}))

    # ════════ W4: 证据升级(经门禁) + touch提前命中 + expiry提前裁决被拒 + 月/季报 ════════
    print("\n[W4] 2026-10-16 补证据升级经门禁; touch提前命中; expiry提前hit被拒; 月报季报")
    cls, warnings, anchors = run_week('w4', td, views, thesis)
    check("W4校验分级PASS", cls == 'PASS', f"{cls} {warnings}")
    saved = json.load(open(views))
    v5 = view(saved, 5)
    check("W4 id5观望→标配(4项证据经门禁通过)", v5['rating'] == '标配')
    check("W4 升级审计含证据路径", '证据' in v5.get('last_change', {}).get('via', '')
          and len(v5['last_change'].get('evidence', [])) >= 2, str(v5.get('last_change', {}).get('via')))
    check("W4 被拒提案标记superseded", any(pr.get('status') == 'superseded' for pr in v5.get('proposals', [])),
          str(v5.get('proposals')))
    check("W4 id5确信度2→3(证据星级≥3)", v5['confidence'] == 3)
    p1, p2, p3 = pred(saved, 1), pred(saved, 2), pred(saved, 3)
    check("W4 pred3 touch模式提前命中(SPX 7580≤7600,截止10-23未到)",
          p3['status'] == 'hit' and '7580' in p3.get('resolved_note', '')
          and '触及' in p3.get('resolved_note', ''),
          f"{p3['status']} {p3.get('resolved_note')}")
    check("W4 pred3裁决引用观察窗内观测", any(o['obs_date'] == '2026-10-16' for o in p3.get('observations', [])),
          str(p3.get('observations')))
    check("W4 pred1 expiry未到期GLM提前hit被拒(仍观察中)",
          p1['status'] == 'observing' and p1['deadline'] == '2026-10-25',
          f"{p1['status']} {p1.get('resolved_note', '')}")
    check("W4 pred1观察期数据已记录(GOLD 4310)", any(o['value'] == 4310 for o in p1.get('observations', [])),
          str(p1.get('observations')))
    check("W4 pred2仍观察中(未到期)", p2['status'] == 'observing')
    # 连续性: W4状态包含W1以来的完整历史
    v1 = view(saved, 1)
    check("W4 连续状态: id1历史含W1维持/W2确信度/W3评级四类轨迹",
          any('维持' in h for h in v1['history']) and any(h.startswith('10/2') for h in v1['history'])
          and any(h.startswith('10/9 评级') for h in v1['history']) and any(h.startswith('10/16') for h in v1['history']),
          str(v1['history']))
    check("W4 连续状态: T1连续第2周(10.12→10.30)",
          view(saved, 1).get('trigger_state', {}).get('T1', {}).get('consec') == 2,
          str(view(saved, 1).get('trigger_state')))

    # ── 9月月报(期间已完结) ──
    block, series, ctx, preview = mr.build_data_block('202609', data_dir=os.path.join(FIX, 'w4_data'),
                                                      views_path=views)
    check("月报非预览(9月已完结)", preview is False)
    check("月报数据块含【预览】排除(正式)", "【预览】" not in block)
    check("月报含覆盖披露节", "数据覆盖与缺口" in block)
    check("月报收益率变化以bp计", any('bp' in s['chg_str'] for s in series.values()),
          str({k: v['chg_str'] for k, v in series.items()}))
    unrate = series.get('失业率UNRATE')
    check("月度序列观测日去重(UNRATE多个采集文件→1个观测)",
          unrate and unrate['obs_count'] == 1, str(unrate))

    # 当月未完结 → 预览模式
    # (IA-P0-2-W4-FIX4最小语义修订,场景与断言不变: 旧写法依赖真实时钟把
    #  '202610'当作"当前未完结月"——2026-11-01起 month_is_complete('202610')
    #  恒为True,该断言在任何晚于10月的时刻必假(纯日历时滞,与被测逻辑无关)。
    #  修订=把评估时钟固定在期间内(2026-10-31),使"期间未完结→预览"场景
    #  确定性可复现;依据见docs/P0_2_W4_FIX4_DELIVERY.md回归节。)
    from unittest import mock as _mock
    from datetime import date as _date

    class _FixedDate(_date):
        @classmethod
        def today(cls):
            return cls(2026, 10, 31)

    with _mock.patch.object(mr, 'date', _FixedDate):
        block_now, _, _, preview_now = mr.build_data_block('202610', data_dir=os.path.join(FIX, 'w4_data'),
                                                           views_path=views)
    check("当月未完结→预览模式", preview_now is True and "【预览】" in block_now)

    # ── Q3季报(整季聚合) ──
    qblock, qpreview = quiet(qo.build_data_block, '2026Q3', None, views)
    check("Q3季报非预览", qpreview is False)
    check("Q3整季区间表(非3时点)", "整季区间" in qblock and "季内最低" in qblock)
    check("Q3各月末水平表", "各月末水平" in qblock and "202607" in qblock and "202609" in qblock)
    check("Q3预测统计按周期", "本季预测到期与裁决" in qblock)
    check("12-26不再触发季报(Q4未完结)", pending_completed_quarter(datetime(2026, 12, 26)) is None)
    check("12-26也不触发月报(12月未完结)", pending_completed_month(datetime(2026, 12, 26)) is None)
    check("2027-01-02(季末后第一个周六)→2026Q4+202612双触发",
          pending_completed_quarter(datetime(2027, 1, 2)) == '2026Q4'
          and pending_completed_month(datetime(2027, 1, 2)) == '202612')
    check("10-03→9月月报+Q3季报双触发",
          pending_completed_month(datetime(2026, 10, 3)) == '202609'
          and pending_completed_quarter(datetime(2026, 10, 3)) == '2026Q3')

    # 当季未完结 → 季报预览
    qb_now, qprev_now = quiet(qo.build_data_block, '2026Q4', None, views)
    check("当季未完结→季报预览模式", qprev_now is True and "【预览】" in qb_now)

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
