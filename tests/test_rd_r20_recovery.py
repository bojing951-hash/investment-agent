#!/usr/bin/env python3
"""R20(2026-11-12): 上下文丢失恢复验收(Charter 10 §3.3)。

成功标准(章程原文): 「一个完全没有此前聊天上下文的新 Agent,能够准确恢复
当前研发状态并继续工作。」本套件以隔离子解释器(python -I,无站点注入、
无本测试模块可依赖)模拟该新 Agent,其唯一信息面 = 仓库状态档 + git 本体:

  R1 正例: 按 RESUME 恢复步骤走——读 PRODUCT_GOAL 锚句 → 读 RD-CHECKPOINT
     块 → `git rev-parse HEAD` 亲核(不盲信文档,块 commit 须存在且为 HEAD
     祖先) → 读 CURRENT_STATE 台账/ITERATION_LOG → 不重做已完成
     (completed_ids 不回流)、不丢未完成、最终目标锚句完整 → RECOVERY-OK。
  R2 反例·陈旧状态拒启: 块 commit 改不存在 sha → 须拒启(码3,先对账),
     不得带着可疑状态开工。
  R3 反例·已完成任务回流: completed_id 注回活动区 → 须拒(码4,不重做已完成)。
  R4 反例·最终目标漂移: PRODUCT_GOAL 被替换(锚句全失) → 须拒(码5)。

反例全部在 tempdir 状态副本上做;真状态档零改动。
正例依赖 R20 检查点已收口(块在场);未收口时 R1 如实红。
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(ROOT, 'docs', 'autonomous-rd')

PASS, FAIL = 0, 0


def check(name, cond, detail=''):
    global PASS, FAIL
    mark = '✅' if cond else '❌'
    print(f"  {mark} {name}" + (f" — {detail}" if detail and not cond else ''))
    PASS, FAIL = PASS + (1 if cond else 0), FAIL + (0 if cond else 1)


# 模拟「完全没有此前聊天上下文的新 Agent」: 隔离子解释器,只读状态档+git。
AGENT_SRC = r'''
import json, os, re, subprocess, sys
repo, state_dir = sys.argv[1], sys.argv[2]
def die(code, why):
    print('RECOVERY-REFUSED: ' + why)
    sys.exit(code)

pg = open(os.path.join(state_dir, 'PRODUCT_GOAL.md'), encoding='utf-8').read()
for anchor in ('全球宏观经济与金融市场研究', '最终产品目标', 'AC10'):
    if anchor not in pg:
        die(5, '最终目标锚句缺失: ' + anchor)

res = open(os.path.join(state_dir, 'RESUME.md'), encoding='utf-8').read()
m = re.search(r'<!--\s*RD-CHECKPOINT v1: json\s*(\{.*?\})\s*-->', res, re.S)
if not m:
    die(6, 'RESUME 无 RD-CHECKPOINT 块')
try:
    blk = json.loads(m.group(1))
except ValueError:
    die(6, '检查点块 json 不合法')

head = subprocess.run(['git', '-C', repo, 'rev-parse', 'HEAD'],
                      capture_output=True, text=True).stdout.strip()
c = str(blk.get('commit', ''))
exists = subprocess.run(['git', '-C', repo, 'cat-file', '-e', c + '^{commit}'],
                        capture_output=True).returncode == 0
ancestor = subprocess.run(
    ['git', '-C', repo, 'merge-base', '--is-ancestor', c, head],
    capture_output=True).returncode == 0
if not (re.fullmatch(r'[0-9a-f]{7,40}', c) and exists and ancestor):
    die(3, '检查点 commit=%s 与 HEAD=%s 不相容(不存在/非祖先)——状态可疑,'
       '先对账再开工' % (c[:9], head[:9]))

cs = open(os.path.join(state_dir, 'CURRENT_STATE.md'), encoding='utf-8').read()
if '## 权威快照' not in cs:
    die(7, 'CURRENT_STATE 无权威快照节')
ledger = re.findall(r'^\|\s*(T-R\d+-\d+)\s*\|\s*([^|]+?)\s*\|', cs, re.M)

am = re.search(r'^## 下一步\(.*$', res, re.M)
if not am:
    die(8, 'RESUME 无活动区 ## 下一步(')
ends = [h.start() for h in re.finditer(r'^## ', res[am.end():], re.M)]
active = res[am.start():am.end() + ends[0]] if ends else res[am.start():]
# 检查点块=机器元数据(内含 completed_ids),不是队列 prose——扫描前剥离
active = re.sub(r'<!--\s*RD-CHECKPOINT v1: json\s*\{.*?\}\s*-->', '', active,
                flags=re.S)

log = open(os.path.join(state_dir, 'ITERATION_LOG.md'),
           encoding='utf-8').read()
for tid in blk.get('completed_ids', []):
    if tid in active:
        die(4, '已完成任务 %s 回流活动区——不得重做已完成' % tid)
    if any(rid == tid for rid, _ in ledger):
        die(4, '已完成任务 %s 回流台账' % tid)
    if tid not in log:
        die(4, '已完成任务 %s 未入日志(状态矛盾)' % tid)
inflight = [rid for rid, st in ledger if st.strip() in ('进行中', '待合并')]
next_task = str(blk.get('next_task', '')).strip()
if not inflight and not next_task:
    die(9, '无在途任务且检查点无下一任务——未完成工作丢失?')
print('RECOVERY-OK round=%s next=%s inflight=%d head=%s'
      % (blk.get('round'), next_task[:40], len(inflight), head[:9]))
'''


def run_agent(state_dir):
    p = subprocess.run([sys.executable, '-I', '-c', AGENT_SRC, ROOT, state_dir],
                       capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def mut(name, fn):
    path = os.path.join(tmp, 'state', name)
    text = open(path, encoding='utf-8').read()
    open(path, 'w', encoding='utf-8').write(fn(text))


print('═' * 64)
print('R20 恢复验收: 无上下文新Agent恢复(正例)+ 三类拒启(反例)')
print('═' * 64)

# ── R1 正例: 真状态恢复 ──
rc, out = run_agent(STATE_DIR)
check('R1 无上下文恢复成功(rc=0+RECOVERY-OK+下一任务)', rc == 0
      and 'RECOVERY-OK' in out and 'next=' in out,
      'rc=%d out=%s' % (rc, out[:300]))
check('R1a 恢复的下一任务=队列阶段二', '阶段二' in out, out[:200])

# ── R2 反例: 陈旧检查点(拒启) ──
tmp = tempfile.mkdtemp(prefix='r20rec_')
shutil.copytree(STATE_DIR, os.path.join(tmp, 'state'))
mut('RESUME.md', lambda t: re.sub(r'"commit":\s*"[0-9a-f]+"',
                                  '"commit": "' + 'e' * 40 + '"', t, count=1))
rc, out = run_agent(os.path.join(tmp, 'state'))
check('R2 块commit不存在→拒启码3+先对账', rc == 3 and 'RECOVERY-REFUSED' in out
      and '对账' in out, 'rc=%d out=%s' % (rc, out[:200]))
shutil.rmtree(tmp)

# ── R3 反例: 已完成任务回流活动区 ──
tmp = tempfile.mkdtemp(prefix='r20rec_')
shutil.copytree(STATE_DIR, os.path.join(tmp, 'state'))
blk_ids = re.findall(r'"completed_ids":\s*\[([^\]]*)\]',
                     open(os.path.join(tmp, 'state', 'RESUME.md'),
                          encoding='utf-8').read())
probe = blk_ids[0].strip('"') if blk_ids and blk_ids[0].strip('"') else 'T-R20-1'
mut('RESUME.md', lambda t: re.sub(
    r'(^## 下一步\(.*\n)',
    r'\g<1>9. [已毕·R20] 回流探针 %s(不应出现在活动区)。\n' % probe,
    t, count=1, flags=re.M))
rc, out = run_agent(os.path.join(tmp, 'state'))
check('R3 已完成任务回流→拒启码4+不重做', rc == 4 and 'RECOVERY-REFUSED' in out
      and ('回流' in out or '重做' in out), 'rc=%d out=%s' % (rc, out[:200]))
shutil.rmtree(tmp)

# ── R4 反例: 最终目标漂移 ──
tmp = tempfile.mkdtemp(prefix='r20rec_')
shutil.copytree(STATE_DIR, os.path.join(tmp, 'state'))
mut('PRODUCT_GOAL.md', lambda t: '# 目标\n\n做一个能挣钱的数据看板。\n')
rc, out = run_agent(os.path.join(tmp, 'state'))
check('R4 最终目标锚句缺失→拒启码5', rc == 5 and 'RECOVERY-REFUSED' in out
      and '锚句缺失' in out, 'rc=%d out=%s' % (rc, out[:200]))
shutil.rmtree(tmp)

print(f"\nR20 恢复验收: {PASS} pass / {FAIL} fail")
sys.exit(0 if FAIL == 0 else 1)
