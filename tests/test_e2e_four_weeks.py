#!/usr/bin/env python3
"""端到端四周模拟测试(第二轮审查第五项, 2026-10-11) — 纯离线,不调用GLM

固定fixture回放4周演化,覆盖完整闭环: 数据装配(锚点提取)→模拟模型输出→验证分级
→状态更新(thesis/allocation/prediction)→报告生成(月报/季报数据块)。

场景剧本(与 tests/fixtures/e2e 一一对应):
  W1(09-25) 初始观点全维持; 另有反例报告(数值错误+前值当现值)→FAIL→禁止回写
  W2(10-02) 仅确信度2→3(评级不变) → 必须落盘(第二轮#10回归)
  W3(10-09) CCC 10.12破10.0 → 引擎核验触发器T1已触发; 美股降级+带量化规格的新预测;
            黄金观望→标配(定性升级,渲染须标注待验证)
  W4(10-16) 预测#1(GOLD≥4300)GLM裁决hit带证据; 预测#3(SPX≥7700,今日到期)GLM漏裁
            → 引擎按锚点自动miss; 9月月报(已完结,非预览,观测日去重,覆盖披露);
            Q3季报整季聚合(非3时点); 12-25提前季报问题回归

运行: ~/AI内容/venv/bin/python3 tests/test_e2e_four_weeks.py
"""
import os
import sys
import io
import json
import glob
import shutil
import tempfile
import contextlib
from datetime import date, datetime

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
    """执行并吞掉stdout打印(校验器/引擎的进度输出)"""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = fn(*a, **kw)
    return r

print("=" * 60)
print("E2E四周模拟(离线fixture)")
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

# 每周独立沙盒: views/thesis从仓库config拷入临时目录,互不污染
def fresh_sandbox(td):
    views = os.path.join(td, 'allocation_views.json')
    thesis = os.path.join(td, 'thesis.json')
    shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), views)
    shutil.copy(os.path.join(ROOT, 'config', 'thesis.json'), thesis)
    return views, thesis

def run_week(week, td, views, thesis):
    """模拟report_generator主流程: 锚点→校验分级→(FAIL则跳过)→回写"""
    data_dir = os.path.join(FIX, f'{week}_data')
    anchors = quiet(data_validator.extract_anchors_from_data, data_dir)
    report_path = os.path.join(td, REPORTS[week])
    shutil.copy(os.path.join(FIX, 'reports', REPORTS[week]), report_path)
    warnings = quiet(data_validator.validate_report, report_path, anchors)
    classification, reason = data_validator.classify_result(
        True, True, warnings, _has_numeric_errors(warnings))
    if classification == 'FAIL':
        return classification, warnings, anchors
    quiet(update_thesis_status, open(report_path).read(), thesis_path=thesis,
          today_str=dict(WEEKS)[week])
    quiet(ae.update_allocation_status, open(report_path).read(),
          views_path=views, anchors=anchors, today_str=dict(WEEKS)[week])
    return classification, warnings, anchors

# ════════ W1: 初始周 ════════
print("\n[W1] 2026-09-25 初始观点 + 反例报告FAIL门禁")
with tempfile.TemporaryDirectory() as td:
    views, thesis = fresh_sandbox(td)
    cls, warnings, anchors = run_week('w1', td, views, thesis)
    check("W1校验分级PASS", cls == 'PASS', f"{cls} {warnings}")
    check("W1锚点含CCC现值与前值", anchors.get('macro.data.CCC_OAS.value', {}).get('value') == 9.46
          and anchors.get('macro.data.CCC_OAS.prev', {}).get('value') == 9.40)
    check("W1锚点TIPS带观测日", anchors.get('macro.data.TIPS_10Y.value', {}).get('obs_date') == '2026-09-24')
    saved = json.load(open(views))
    v1 = next(v for v in saved['views'] if v['id'] == 1)
    check("W1全维持: id1仍标配2★", v1['rating'] == '标配' and v1['confidence'] == 2)
    check("W1维持也落盘(history有维持条目+last_updated)",
          any('维持' in h for h in v1['history']) and saved['last_updated'] == '2026-09-25')
    check("W1 thesis回写", json.load(open(thesis))['last_updated'] == '2026-09-25')

    # 反例: 数值错误+前值当现值 → FAIL → 回写被跳过(状态不变)
    bad_path = os.path.join(td, 'bad.md')
    shutil.copy(os.path.join(FIX, 'reports', 'bad_report_20260925.md'), bad_path)
    bw = quiet(data_validator.validate_report, bad_path, anchors)
    bcls, _ = data_validator.classify_result(True, True, bw, _has_numeric_errors(bw))
    check("反例报告分级FAIL", bcls == 'FAIL', f"{bcls} {bw}")
    check("反例含严重偏差错误(12.52 vs 9.46)", any('严重错误' in w for w in bw), str(bw))
    check("反例含前值当现值拦截(TIPS 2.93当现值)", any('前值当现值' in w for w in bw), str(bw))
    # 模拟主门禁: FAIL→不调用回写
    before = open(views).read()
    if bcls != 'FAIL':
        quiet(ae.update_allocation_status, open(bad_path).read(), views_path=views)
    check("FAIL时观点库未被反例污染", open(views).read() == before)

# ════════ W2: 仅确信度变化(第二轮#10回归) ════════
print("\n[W2] 2026-10-02 仅确信度上调 → 必须落盘")
with tempfile.TemporaryDirectory() as td:
    views, thesis = fresh_sandbox(td)
    cls, warnings, anchors = run_week('w2', td, views, thesis)
    check("W2校验分级PASS", cls == 'PASS', f"{cls} {warnings}")
    saved = json.load(open(views))
    v1 = next(v for v in saved['views'] if v['id'] == 1)
    check("W2 id1确信度2→3已回写", v1['confidence'] == 3, str(v1.get('confidence')))
    check("W2 id1评级不变(标配)", v1['rating'] == '标配')
    check("W2 确信度变化单独记录", any(h.startswith('10/2 确信度') and '2★→3★' in h for h in v1['history']),
          str(v1['history']))
    check("W2 落盘last_updated刷新", saved['last_updated'] == '2026-10-02')

# ════════ W3: 触发器核验+降级+新预测 ════════
print("\n[W3] 2026-10-09 CCC破线 → 引擎核验触发+降级+带规格新预测")
with tempfile.TemporaryDirectory() as td:
    views, thesis = fresh_sandbox(td)
    # 渲染层: 用W3锚点核验触发器
    anchors3 = quiet(data_validator.extract_anchors_from_data, os.path.join(FIX, 'w3_data'))
    views_data = ae.load_views(views)
    trig = ae.evaluate_quant_triggers(views_data, anchors3)
    t1 = next(r for r in trig[3] if r['trig_id'] == 'T1')
    check("W3 触发器T1(CCC 10.12≥10.0)引擎核验=已触发", t1['status'] == 'triggered', str(t1))
    block = ae.render_views_block(views_data, anchors=anchors3)
    check("W3 渲染块含'✅已触发'", "✅已触发" in block)
    check("W3 渲染块标注待验证条件", "❓待验证" in block)

    cls, warnings, anchors = run_week('w3', td, views, thesis)
    check("W3校验分级PASS", cls == 'PASS', f"{cls} {warnings}")
    saved = json.load(open(views))
    v1 = next(v for v in saved['views'] if v['id'] == 1)
    v5 = next(v for v in saved['views'] if v['id'] == 5)
    check("W3 id1评级标配→低配", v1['rating'] == '低配')
    check("W3 评级变化单独记录", any(h.startswith('10/9 评级') and '标配→低配' in h for h in v1['history']),
          str(v1['history']))
    check("W3 id5观望→标配(定性升级)", v5['rating'] == '标配')
    new_p = max(saved['predictions'], key=lambda p: p['pred_id'])
    check("W3 新预测#3登记,deadline=一周后", new_p['pred_id'] == 3 and new_p['deadline'] == '2026-10-16',
          f"{new_p.get('pred_id')} {new_p.get('deadline')}")
    check("W3 新预测带量化规格", new_p.get('metric') == 'global_market.data.SPX.close'
          and new_p.get('comparator') == '>=' and new_p.get('target') == 7700, str(new_p))
    check("W3 新预测状态=观察中", new_p['status'] == 'observing')

# ════════ W4: 预测双轨裁决 + 月报 + 季报 ════════
print("\n[W4] 2026-10-16 GLM带证据hit + 引擎自动miss + 9月月报 + Q3季报")
with tempfile.TemporaryDirectory() as td:
    views, thesis = fresh_sandbox(td)
    # 先重放W3建立状态(预测#3依赖W3的评级变更)
    shutil.copy(os.path.join(ROOT, 'config', 'thesis.json'), thesis)
    anchors = quiet(data_validator.extract_anchors_from_data, os.path.join(FIX, 'w3_data'))
    w3_report = open(os.path.join(FIX, 'reports', 'weekly_report_20261009.md')).read()
    quiet(ae.update_allocation_status, w3_report, views_path=views, anchors=anchors, today_str='2026-10-09')

    cls, warnings, anchors = run_week('w4', td, views, thesis)
    check("W4校验分级PASS", cls == 'PASS', f"{cls} {warnings}")
    saved = json.load(open(views))
    p1 = next(p for p in saved['predictions'] if p['pred_id'] == 1)
    p3 = next(p for p in saved['predictions'] if p['pred_id'] == 3)
    check("W4 预测#1 GLM裁决hit(带数值证据)",
          p1['status'] == 'hit' and '4310' in p1.get('resolved_note', ''), f"{p1['status']} {p1.get('resolved_note')}")
    check("W4 预测#3 GLM漏裁→引擎自动miss",
          p3['status'] == 'miss' and '引擎自动裁决' in p3.get('resolved_note', ''),
          f"{p3['status']} {p3.get('resolved_note')}")
    check("W4 预测#3裁决引用锚点数值(7580)", '7580' in p3.get('resolved_note', ''), p3.get('resolved_note'))
    check("W4 预测#2仍观察中(未到期)", next(p for p in saved['predictions'] if p['pred_id'] == 2)['status'] == 'observing')

    # ── 9月月报(期间已完结) ──
    block, series, ctx, preview = mr.build_data_block('202609', data_dir=os.path.join(FIX, 'w4_data'),
                                                      views_path=views)
    check("月报非预览(9月已完结)", preview is False)
    check("月报数据块含【预览】排除(正式)", "【预览】" not in block)
    check("月报含覆盖披露节", "数据覆盖与缺口" in block)
    check("月报收益率变化以bp计", any('bp' in s['chg_str'] for s in series.values()),
          str({k: v['chg_str'] for k, v in series.items()}))
    check("月报价格变化以%计", any(s['chg_str'].endswith('%') for s in series.values()))
    unrate = series.get('失业率UNRATE')
    check("月度序列观测日去重(UNRATE 3个采集文件→1个观测)",
          unrate and unrate['obs_count'] == 1, str(unrate))
    check("月报预测统计按周期(9月无到期)", "本月到期0条" in block or "到期0" in block,
          [l for l in block.split('\n') if '到期' in l])

    # 当月未完结 → 预览模式
    block_now, _, _, preview_now = mr.build_data_block('202610', data_dir=os.path.join(FIX, 'w4_data'),
                                                       views_path=views)
    check("当月未完结→预览模式", preview_now is True and "【预览】" in block_now)

    # ── Q3季报(整季聚合) ──
    qblock, qpreview = quiet(qo.build_data_block, '2026Q3', None, views)
    check("Q3季报非预览", qpreview is False)
    check("Q3整季区间表(非3时点)", "整季区间" in qblock and "季内最低" in qblock)
    check("Q3各月末水平表", "各月末水平" in qblock and "202607" in qblock and "202609" in qblock)
    check("Q3预测统计按周期", "本季预测到期与裁决" in qblock)
    # 2026-12-25提前季报问题回归(第五项)
    check("12-25不再触发季报(Q4未完结)", pending_completed_quarter(datetime(2026, 12, 25)) is None)
    check("12-25也不触发月报(12月未完结)", pending_completed_month(datetime(2026, 12, 25)) is None)
    check("2027-01-01(季末后第一个周五)→2026Q4+202612双触发",
          pending_completed_quarter(datetime(2027, 1, 1)) == '2026Q4'
          and pending_completed_month(datetime(2027, 1, 1)) == '202612')
    check("10-02→9月月报+Q3季报双触发",
          pending_completed_month(datetime(2026, 10, 2)) == '202609'
          and pending_completed_quarter(datetime(2026, 10, 2)) == '2026Q3')

    # 当季未完结 → 季报预览
    qb_now, qprev_now = quiet(qo.build_data_block, '2026Q4', None, views)
    check("当季未完结→季报预览模式", qprev_now is True and "【预览】" in qb_now)

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
