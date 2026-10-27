#!/usr/bin/env python3
"""真实GLM API冒烟测试(第三轮, 2026-10-11重写)

默认跳过(不花token、不依赖网络)。显式开启:
  RUN_GLM_LIVE=1 ~/AI内容/venv/bin/python3 tests/test_glm_live.py

测试内容(最小代价端到端切片,非完整周报):
  1. 用真实锚点渲染观点块(触发器核验+预测生命周期) → 拼进精简prompt
  2. GLM真实调用输出1条带结构化evidence的ALLOCATION_STATUS行
  3. 回写门禁链路真实跑通(临时副本,不碰真实研究状态):
     无论GLM说什么,落盘结果必须与门禁的确定性预测一致
     (评级变更=触发器或足量验证证据;确信度上调≤程序星级;证据台账只含验证通过项)
  4. 无证据裁决必须被拒(与模型输出无关的硬门禁)
与离线E2E互为补充: 离线测逻辑,在线测模型遵从性+门禁确定性。
不修改真实研究状态: 一切回写在tempdir副本上进行。
"""
import os
import sys
import io
import json
import glob
import shutil
import tempfile
import contextlib
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

if os.environ.get('RUN_GLM_LIVE') != '1':
    print("⏭️ 跳过(设置 RUN_GLM_LIVE=1 以运行真实GLM冒烟测试)")
    sys.exit(0)

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
print("真实GLM API冒烟测试(RUN_GLM_LIVE=1, 第三轮格式)")
print("=" * 60)

from data_validator import extract_anchors_from_data
import allocation_engine as ae
from report_generator import load_prompt, _call_glm

# ── 1. 真实锚点 + 观点渲染(触发器核验/预测生命周期) ──
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    anchors = extract_anchors_from_data()
anchor_files = sorted(p for p in glob.glob(os.path.join(ROOT, 'data', 'daily', 'anchors_*.json'))
                      if not p.endswith('.meta.json'))   # IA-P0-1: 排除来源meta侧挂
if anchor_files:
    with open(anchor_files[-1], encoding='utf-8') as f:
        anchors = json.load(f)   # 用保存的完整锚点(带obs_date)更真实
check("锚点可用(含观测日元数据)", len(anchors) > 20
      and any(v.get('obs_date') for v in anchors.values()))
views = ae.load_views()
block = ae.render_views_block(views, anchors=anchors)
check("真实锚点渲染观点块(触发器核验+预测跟踪)", len(block) > 400 and "❓待验证" in block
      and "预测跟踪" in block)

# ── 2. 真实GLM调用(精简输入,只要1条带evidence的状态行) ──
system_prompt = load_prompt('system_prompt.md')
user_prompt = f"""以下是当前配置观点库(触发器状态由程序核验):

{block[:3500]}

请只输出以下内容,不要其他文字:
1. 针对资产"贵金属(黄金)"(id=5)输出ALLOCATION_STATUS格式的一行JSON(HTML注释内):
<!--ALLOCATION_STATUS
{{"id":5,"rating":"...","confidence":N,"note":"≤40字","evidence":[{{"metric":"macro.data.TIPS_10Y.value","value":N,"obs_date":"...","mechanism":"利率与流动性"}},...]}}
ALLOCATION_STATUS-->
rating只能取: 超配/标配/低配/观望。evidence数组须引用上方锚点中TIPS_10Y/GOLD等指标的真实数值与观测日(程序将逐项核验,虚构会被拒收)。
2. 一句话说明评级理由(≤50字),如引用触发器须按引擎核验结果如实标注"已触发/待验证/持续确认中"。"""

print("\n🤖 调用GLM(真实API, max_tokens=2500)...")
md = _call_glm(system_prompt, user_prompt, max_tokens=2500)
check("GLM返回内容", len(md.strip()) > 50, md[:100])
print(f"--- GLM输出 ---\n{md[:700]}\n----------------")

# ── 3. 回写门禁链路(临时副本): 结果与门禁预测确定性一致 ──
today = datetime.now().strftime('%Y-%m-%d')
objs = ae._parse_status_block(md, 'ALLOCATION_STATUS')
o5 = next((o for o in objs if o.get('id') == 5), None)
check("GLM状态块可解析(含id=5行)", o5 is not None, md[:200])

if o5 is not None:
    views_before = json.load(open(os.path.join(ROOT, 'config', 'allocation_views.json')))
    v5_before = next(v for v in views_before['views'] if v['id'] == 5)
    # 门禁的确定性预测(与update路径同函数计算,但断言的是不变式而非循环)
    verified, _rej = ae.verify_evidence_items(o5.get('evidence'), anchors, today)
    supporting, _ctry, _unexp, _neu = ae.split_evidence_direction(verified)
    new_support = ae.new_supporting_metrics(v5_before, supporting, today)
    trig = {r['trig_id']: r for r in ae.evaluate_quant_triggers(views_before, anchors, today)[5]}
    proposed = str(o5.get('rating', ''))
    old_rating = v5_before['rating']
    if proposed in ae.ALLOWED_RATINGS and proposed != old_rating:
        direction = ae._change_direction(old_rating, proposed)
        min_ev = 1 if direction in ('suspend', 'resume') else ae.MIN_EVIDENCE_FOR_RATING_CHANGE
        fired = any(r['status'] == 'triggered' and r['direction'] == direction
                    for r in trig.values())
        with tempfile.TemporaryDirectory() as td:
            tmp_views = os.path.join(td, 'allocation_views.json')
            shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), tmp_views)
            with contextlib.redirect_stdout(io.StringIO()):
                ae.update_allocation_status(md, views_path=tmp_views, anchors=anchors, today_str=today)
            saved = json.load(open(tmp_views))
            v5 = next(v for v in saved['views'] if v['id'] == 5)
            if fired or len(new_support) >= min_ev:
                check(f"门禁条件满足(触发器{fired}/新增独立证据{len(new_support)}项)→提议评级被采纳",
                      v5['rating'] == proposed, f"{v5['rating']} vs {proposed}")
            else:
                check(f"门禁条件不足(触发器{fired}/新增独立证据{len(new_support)}项)→评级保留+提案留档",
                      v5['rating'] == old_rating
                      and any(p['status'] == 'rejected' for p in v5.get('proposals', [])),
                      f"{v5['rating']} {v5.get('proposals')}")
            # 不变式: 任何已发生的评级变更必有审计记录
            if v5['rating'] != old_rating:
                check("变更审计齐备(date/from/to/via/evidence)",
                      all(k in v5.get('last_change', {}) for k in ('date', 'from', 'to', 'via')))
    else:
        check("GLM维持原评级(或量表外被忽略)", proposed == old_rating or proposed not in ae.ALLOWED_RATINGS,
              proposed)

    # 不变式: 确信度上调不超过程序星级; 台账只含验证通过的证据
    with tempfile.TemporaryDirectory() as td:
        tmp_views = os.path.join(td, 'allocation_views.json')
        shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), tmp_views)
        with contextlib.redirect_stdout(io.StringIO()):
            ae.update_allocation_status(md, views_path=tmp_views, anchors=anchors, today_str=today)
        saved = json.load(open(tmp_views))
        v5 = next(v for v in saved['views'] if v['id'] == 5)
        star, _ = ae.star_level_from_evidence(verified)
        if isinstance(o5.get('confidence'), int) and o5['confidence'] > v5_before['confidence']:
            check(f"确信度上调未超过程序星级(GLM要{o5['confidence']}★,程序星级{star}★)",
                  v5['confidence'] <= max(star, v5_before['confidence']),
                  f"落盘{v5['confidence']}★")
        if verified:
            check("证据台账只记录验证通过的项", v5['evidence_ledger'][-1]['verified'] == len(verified))
        else:
            check("无证据通过时不产生台账(防虚构证据入档)", not v5.get('evidence_ledger'),
                  str(v5.get('evidence_ledger')))

# ── 4. 无证据裁决必须被拒(硬门禁,与模型无关) ──
with tempfile.TemporaryDirectory() as td:
    tmp_views = os.path.join(td, 'allocation_views.json')
    shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), tmp_views)
    bad = '<!--PREDICTION_STATUS\n{"pred_id":2,"status":"hit","note":""}\nPREDICTION_STATUS-->'
    with contextlib.redirect_stdout(io.StringIO()):
        ae.update_allocation_status(bad, views_path=tmp_views, today_str=today)
    saved = json.load(open(tmp_views))
    p2 = next(p for p in saved['predictions'] if p['pred_id'] == 2)
    check("无证据hit裁决被程序拒绝(与模型无关的硬门禁)", p2['status'] == 'observing')

# ── 5. 真实研究状态未被改动 ──
real = open(os.path.join(ROOT, 'config', 'allocation_views.json')).read()
check("真实观点库未被冒烟测试修改", '"version": "3.0"' in real and json.loads(real)['last_updated'] == '2026-10-11')

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
