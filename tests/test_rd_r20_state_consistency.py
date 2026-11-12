#!/usr/bin/env python3
"""R20(2026-11-12): 研发状态一致性检查门套件(Charter 10 §3.1/§3.2)。

历史失同步根因(R15 快照滞留到 R19)= 状态档手写、无机器校验。本套件锁
scripts/rd_state_consistency.py 六项检查的正反两面:

  C1  正例: 真仓库真状态 → rc=0,①~⑥ 全 PASS(依赖 R20 检查点已 finalize;
      未 finalize 前运行本套件 C1 会如实红=狗粮负例)。
  C2  ① 反例: baseline=不存在提交 → FAIL「不是仓库中的提交」。
  C3  ① 反例: baseline=存在但非 HEAD 祖先(commit-tree 现造悬空根提交,
      只增对象不动作何引用,CI 一次性环境无害)→ FAIL「不是 HEAD 的祖先」。
  C4  ② 反例: 活动区注入 [已毕·R19] → FAIL「已完成标记」。
  C4b ② 反例: 活动区注入滞留 [进行中·R19] 标记(R19 已入日志;R15→R19
      失同步实际形态)→ FAIL「滞留待办」。
  C5  ② 反例: 删除 RD-CHECKPOINT 块 → FAIL「无 RD-CHECKPOINT」。
  C9  ② 反例: 块 commit 改不存在 sha → FAIL「不在仓库中」。
  C6  ③ 反例: 台账注入重复 ID(T-R21-9×2,轮次取 21 防污染②⑤)+ 已毕行
      (T-R21-8;台账只收进行中/待合并)→ FAIL「ID 重复」+「状态非法」。
  C7  ④ 反例: AC1 状态列改 EXECUTED → FAIL「状态非法」。
  C8  ⑤ 反例: 台账回流 T-R19-1(19 ≤ 日志已记 R20)→ FAIL「回流待办」。
  C10 ⑥ 反例: PRODUCT_GOAL 改一字(sha 变) → FAIL「goal_sha」(防目标漂移,
      与恢复验收 R4 的 Agent 侧拒启互为表里)。

所有反例在 tempdir 状态副本上做,真状态档零改动。
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKER = os.path.join(ROOT, 'scripts', 'rd_state_consistency.py')
STATE_DIR = os.path.join(ROOT, 'docs', 'autonomous-rd')

PASS, FAIL = 0, 0


def check(name, cond, detail=''):
    global PASS, FAIL
    mark = '✅' if cond else '❌'
    print(f"  {mark} {name}" + (f" — {detail}" if detail and not cond else ''))
    PASS, FAIL = PASS + (1 if cond else 0), FAIL + (0 if cond else 1)


def run_checker(state_dir):
    p = subprocess.run([sys.executable, CHECKER, '--repo', ROOT,
                        '--state-dir', state_dir],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def mut_state(tmp, name, fn):
    path = os.path.join(tmp, 'state', name)
    text = open(path, encoding='utf-8').read()
    open(path, 'w', encoding='utf-8').write(fn(text))


def fresh_copy():
    tmp = tempfile.mkdtemp(prefix='r20chk_')
    shutil.copytree(STATE_DIR, os.path.join(tmp, 'state'))
    return tmp


print('═' * 64)
print('R20 一致性检查门: 六项正反两面(真状态只读,反例走 tempdir 副本)')
print('═' * 64)

# ── C1 正例: 真仓库真状态 ──
rc, out = run_checker(STATE_DIR)
check('C1 真状态六项全绿 rc=0', rc == 0
      and all(c in out for c in ('①基线一致 PASS', '②RESUME健全 PASS',
                                 '③台账规范 PASS', '④验收矩阵 PASS',
                                 '⑤日志-台账 PASS', '⑥目标完整 PASS'))
      and '6/6 PASS' in out,
      'rc=%d\n%s' % (rc, out[-600:]))

# ── C2 ① baseline=不存在提交 ──
tmp = fresh_copy()
mut_state(tmp, 'CURRENT_STATE.md',
          lambda t: re.sub(r'baseline=[0-9a-f]{7,40}',
                           'baseline=' + 'deadbeef' * 5, t, count=1))
rc, out = run_checker(os.path.join(tmp, 'state'))
check('C2 ① baseline 不存在→FAIL', rc != 0 and '①基线一致 FAIL' in out
      and '不是仓库中的提交' in out, 'rc=%d' % rc)
shutil.rmtree(tmp)

# ── C3 ① baseline=非祖先(现造悬空根提交) ──
# -c 内联身份: CI runner 无全局 git 身份,裸 commit-tree 会
# "Author identity unknown"→悬空提交造不出(实测 CI 红根因之一)
p = subprocess.run(['git', '-C', ROOT,
                    '-c', 'user.name=rd20-test', '-c', 'user.email=rd20@test',
                    'commit-tree', 'HEAD^{tree}',
                    '-m', 'r20-neg-orphan'], capture_output=True, text=True)
orphan = p.stdout.strip()
check('C3 前置: 悬空提交已造', bool(re.fullmatch(r'[0-9a-f]{40}', orphan or '')),
      p.stderr[:150])
tmp = fresh_copy()
mut_state(tmp, 'CURRENT_STATE.md',
          lambda t: re.sub(r'baseline=[0-9a-f]{7,40}',
                           'baseline=' + orphan, t, count=1))
rc, out = run_checker(os.path.join(tmp, 'state'))
check('C3 ① baseline 非 HEAD 祖先→FAIL', rc != 0
      and '不是 HEAD' in out and '祖先' in out, 'rc=%d' % rc)
shutil.rmtree(tmp)

# ── C4 ② 活动区注入已完成标记 ──
tmp = fresh_copy()
mut_state(tmp, 'RESUME.md', lambda t: re.sub(
    r'(^## 下一步\(.*\n)', r'\g<1>9. [已毕·R19] 注入探针(不应出现在活动区)。\n',
    t, count=1, flags=re.M))
rc, out = run_checker(os.path.join(tmp, 'state'))
check('C4 ② 活动区已毕标记→FAIL', rc != 0 and '②RESUME健全 FAIL' in out
      and '已完成标记' in out, 'rc=%d' % rc)
shutil.rmtree(tmp)

# ── C4b ② 滞留进行中标记(已入日志轮次) ──
tmp = fresh_copy()
mut_state(tmp, 'RESUME.md', lambda t: re.sub(
    r'(^## 下一步\(.*\n)',
    r'\g<1>9. **[进行中·R19] 旧任务未归档探针**。\n',
    t, count=1, flags=re.M))
rc, out = run_checker(os.path.join(tmp, 'state'))
check('C4b ② 已入日志轮次仍挂进行中→FAIL', rc != 0 and '滞留待办' in out,
      'rc=%d out=%s' % (rc, out[:400]))
shutil.rmtree(tmp)

# ── C5 ② 检查点块删除 ──
tmp = fresh_copy()
mut_state(tmp, 'RESUME.md',
          lambda t: re.sub(r'<!--\s*RD-CHECKPOINT v1: json\s*\{.*?\}\s*-->',
                           '', t, flags=re.S))
rc, out = run_checker(os.path.join(tmp, 'state'))
check('C5 ② 无检查点块→FAIL', rc != 0 and '无 RD-CHECKPOINT' in out,
      'rc=%d' % rc)
shutil.rmtree(tmp)

# ── C9 ② 块 commit 指向不存在提交 ──
tmp = fresh_copy()
mut_state(tmp, 'RESUME.md',
          lambda t: re.sub(r'"commit":\s*"[0-9a-f]+"',
                           '"commit": "' + 'e' * 40 + '"', t, count=1))
rc, out = run_checker(os.path.join(tmp, 'state'))
check('C9 ② 块 commit 不在仓库→FAIL', rc != 0 and '不在仓库中' in out,
      'rc=%d' % rc)
shutil.rmtree(tmp)

# ── C6 ③ 台账重复 ID + 已毕行 ──
tmp = fresh_copy()
def add_rows(t):
    rows = ('| T-R21-9 | 进行中 | — | 探针(重复ID甲) |\n'
            '| T-R21-9 | 进行中 | — | 探针(重复ID乙) |\n'
            '| T-R21-8 | 已毕 | — | 探针(已毕只进日志/存档) |\n')
    return re.sub(r'(^\| ID \| 状态 \| Git证据 \| 说明 \|\n\|---\|---\|---\|---\|\n)',
                  r'\g<1>' + rows, t, count=1, flags=re.M)
mut_state(tmp, 'CURRENT_STATE.md', add_rows)
rc, out = run_checker(os.path.join(tmp, 'state'))
check('C6 ③ ID重复+已毕行→FAIL', rc != 0 and 'ID 重复' in out
      and '状态非法' in out and '已毕' in out, 'rc=%d' % rc)
shutil.rmtree(tmp)

# ── C7 ④ 验收矩阵非法状态 ──
tmp = fresh_copy()
mut_state(tmp, 'FINAL_ACCEPTANCE.md',
          lambda t: re.sub(r'^(\| AC1 \|[^|]+\|) PASS \|', r'\g<1> EXECUTED |',
                           t, count=1, flags=re.M))
rc, out = run_checker(os.path.join(tmp, 'state'))
check('C7 ④ AC 状态 EXECUTED→FAIL', rc != 0 and '④验收矩阵 FAIL' in out
      and 'EXECUTED' in out and '状态非法' in out, 'rc=%d' % rc)
shutil.rmtree(tmp)

# ── C8 ⑤ 已入日志轮次任务回流台账 ──
tmp = fresh_copy()
def add_stale(t):
    row = '| T-R19-1 | 进行中 | — | 回流探针(R19 已入日志) |\n'
    return re.sub(r'(^\| ID \| 状态 \| Git证据 \| 说明 \|\n\|---\|---\|---\|---\|\n)',
                  r'\g<1>' + row, t, count=1, flags=re.M)
mut_state(tmp, 'CURRENT_STATE.md', add_stale)
rc, out = run_checker(os.path.join(tmp, 'state'))
check('C8 ⑤ 已完成回流待办→FAIL', rc != 0 and '⑤日志-台账 FAIL' in out
      and '回流待办' in out, 'rc=%d' % rc)
shutil.rmtree(tmp)

# ── C10 ⑥ 最终目标漂移(sha 变) ──
tmp = fresh_copy()
mut_state(tmp, 'PRODUCT_GOAL.md', lambda t: t + '\n(漂移注入)\n')
rc, out = run_checker(os.path.join(tmp, 'state'))
check('C10 ⑥ PRODUCT_GOAL 改动→FAIL', rc != 0 and '⑥目标完整 FAIL' in out
      and 'goal_sha' in out, 'rc=%d' % rc)
shutil.rmtree(tmp)

print(f"\nR20 一致性检查门: {PASS} pass / {FAIL} fail")
sys.exit(0 if FAIL == 0 else 1)
