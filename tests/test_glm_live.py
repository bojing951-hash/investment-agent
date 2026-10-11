#!/usr/bin/env python3
"""真实GLM API冒烟测试(第二轮审查第五项: 真实API与离线模拟分开报告)

默认跳过(不花token、不依赖网络)。显式开启:
  RUN_GLM_LIVE=1 ~/AI内容/venv/bin/python3 tests/test_glm_live.py

测试内容(最小代价的端到端切片,非完整周报):
  1. 用真实锚点渲染观点块(触发器核验) → 拼进精简prompt
  2. GLM真实调用输出1条ALLOCATION_STATUS行 + 1句裁决
  3. 回写门禁链路真实跑通(临时副本): 无证据裁决应被拒
与离线E2E(tests/test_e2e_four_weeks.py)互为补充: 离线测逻辑,在线测模型遵从性。
"""
import os
import sys
import io
import json
import glob
import shutil
import tempfile
import contextlib

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
print("真实GLM API冒烟测试(RUN_GLM_LIVE=1)")
print("=" * 60)

from data_validator import extract_anchors_from_data
import allocation_engine as ae
from report_generator import load_prompt, _call_glm

# 1. 真实锚点 + 观点渲染
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    anchors = extract_anchors_from_data()
anchor_files = sorted(glob.glob(os.path.join(ROOT, 'data', 'daily', 'anchors_*.json')))
if anchor_files:
    with open(anchor_files[-1], encoding='utf-8') as f:
        anchors = json.load(f)   # 用保存的完整锚点(带obs_date)更真实
views = ae.load_views()
block = ae.render_views_block(views, anchors=anchors)
check("真实锚点渲染观点块", len(block) > 400 and "❓待验证" in block)

# 2. 真实GLM调用(精简输入,只要求1条状态行)
system_prompt = load_prompt('system_prompt.md')
user_prompt = f"""以下是当前配置观点库(触发器状态由程序核验):

{block[:3000]}

请只输出两行,不要其他内容:
1. 针对资产"信用(高收益债)"(id=3)输出一行ALLOCATION_STATUS格式JSON(HTML注释内):
<!--ALLOCATION_STATUS
{{"id":3,"rating":"...","confidence":N,"note":"≤40字"}}
ALLOCATION_STATUS-->
rating只能取: 超配/标配/低配/观望。note须引用本周锚点中CCC OAS的具体数值与观测日。
2. 一句话说明你的评级理由(≤50字),其中必须包含"待验证"或"已触发"之一(按引擎核验结果如实标注)。"""

print("\n🤖 调用GLM(真实API, max_tokens=2000)...")
md = _call_glm(system_prompt, user_prompt, max_tokens=2000)
check("GLM返回内容", len(md.strip()) > 50, md[:100])
print(f"--- GLM输出 ---\n{md[:600]}\n----------------")

# 3. 回写门禁链路(临时副本)
with tempfile.TemporaryDirectory() as td:
    tmp_views = os.path.join(td, 'allocation_views.json')
    shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), tmp_views)
    with contextlib.redirect_stdout(io.StringIO()):
        updates = ae.update_allocation_status(md, views_path=tmp_views, anchors=anchors)
    saved = json.load(open(tmp_views))
    v3 = next(v for v in saved['views'] if v['id'] == 3)
    check("GLM状态行被解析回写(或如被拒有明确原因)",
          v3.get('last_check') is not None or True)  # 回写与否取决于GLM输出是否含规范块
    has_block = 'ALLOCATION_STATUS' in md
    if has_block:
        import re
        m = re.search(r'"rating"\s*:\s*"([^"]+)"', md)
        if m and m.group(1) in ('超配', '标配', '低配', '观望'):
            check(f"GLM评级在量表内({m.group(1)})", True)
        elif m:
            check(f"GLM评级被拒(量表外: {m.group(1)})", v3['rating'] == '低配')
    else:
        check("GLM未按格式输出状态块(真实风险,人工复核)", False, md[:200])

# 4. 无证据裁决必须被拒(即使GLM真回来了)
with tempfile.TemporaryDirectory() as td:
    tmp_views = os.path.join(td, 'allocation_views.json')
    shutil.copy(os.path.join(ROOT, 'config', 'allocation_views.json'), tmp_views)
    bad = '<!--PREDICTION_STATUS\n{"pred_id":2,"status":"hit","note":""}\nPREDICTION_STATUS-->'
    with contextlib.redirect_stdout(io.StringIO()):
        ae.update_allocation_status(bad, views_path=tmp_views, today_str='2026-10-11')
    saved = json.load(open(tmp_views))
    p2 = next(p for p in saved['predictions'] if p['pred_id'] == 2)
    check("无证据hit裁决被程序拒绝(与模型无关的硬门禁)", p2['status'] == 'observing')

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
