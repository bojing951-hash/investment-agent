#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R20(2026-11-12): 状态管理整改——一致性检查门+检查点管线(Charter 10 §3)。

历史根因: R15 视角快照滞留至 R19、RESUME 残留已完成任务——状态档纯手写
无机器校验,上下文丢失后新会话可能按过期状态重复开发。本套件锁 R20 落地面:

  A. 合成仓库(全历史 tempdir git repo)六项检查全绿基线——含真实文件形态
     回归(FINAL_ACCEPTANCE 交叉映射表的 AC11/AC12 行不是状态行,不得误伤)。
  B. 变异测试: 逐项突变必致对应检查 FAIL(锁有牙),该绿的突变(纯文档/
     合并提交超前 baseline=容忍类)必须保持绿(不过杀)。
  C. rd_checkpoint 管线: --finalize 盖章(块恰一个/幂等)、先日志后检查点
     顺序强制、--verify 退出码。
  D. 浅克隆降级(CI actions/checkout depth=1 语义): 祖先核验降级注记,
     结构面全量,退出码仍正确;浅克隆上 finalize 拒绝。
  E. 真仓门: 对本仓库跑检查门(浅克隆=SKIP 注记)——自此状态失同步即测试红。

红线: 全部合成 fixture,不碰生产数据;零网络;零真实采集。
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, 'scripts')
sys.path.insert(0, SCRIPTS)
import rd_state_consistency as gate  # noqa: E402

PASS, FAIL = 0, 0
GOAL_BODY = '# PRODUCT_GOAL — fixture\n\n总指令: 全球宏观 AI 研究系统,AC1-AC10。\n'


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}  {detail}")


def _git_env():
    env = dict(os.environ)
    env.update({'GIT_AUTHOR_NAME': 'fixture', 'GIT_AUTHOR_EMAIL': 'f@x',
                'GIT_COMMITTER_NAME': 'fixture', 'GIT_COMMITTER_EMAIL': 'f@x',
                'PYTHONIOENCODING': 'utf-8'})
    return env


def run_gate(repo, state_dir=None):
    """import 面跑门 → Report。"""
    state_dir = state_dir or os.path.join(repo, 'docs', 'autonomous-rd')
    rep = gate.Report()
    gate.run_checks(repo, state_dir, rep)
    return rep


def cli(*args):
    """子进程跑 scripts/ 下脚本 → (rc, stdout)。"""
    p = subprocess.run([sys.executable] + list(args), capture_output=True,
                       text=True, env=_git_env())
    return p.returncode, p.stdout + p.stderr


# ══════════════════════ 夹具 ══════════════════════

def build_fixture(base, stamped=True):
    """合成仓库: C0=代码提交, C1=状态档提交(盖章态或波中态)。

    stamped=True  → C1 含检查点块+baseline 机器行(轮末盖章态,门应全绿);
    stamped=False → C1 无块无机器行(波中态,供 C 节 finalize 实验)。
    返回 dict(repo, sd, c0, c1, goal_sha)。
    """
    repo = os.path.join(base, 'repo')
    sd = os.path.join(repo, 'docs', 'autonomous-rd')
    os.makedirs(sd)
    g = lambda *a: subprocess.run(['git', '-C', repo] + list(a),
                                  capture_output=True, text=True,
                                  env=_git_env()).stdout.strip()
    g('init', '-b', 'main')
    open(os.path.join(repo, 'engine.py'), 'w').write('x = 1\n')
    open(os.path.join(sd, 'PRODUCT_GOAL.md'), 'w',
         encoding='utf-8').write(GOAL_BODY)
    for n in ('CURRENT_STATE.md', 'RESUME.md', 'ITERATION_LOG.md',
              'FINAL_ACCEPTANCE.md'):
        open(os.path.join(sd, n), 'w', encoding='utf-8').write('# %s v0\n' % n)
    g('add', '-A')
    g('commit', '-m', 'C0 code+goal')
    c0 = g('rev-parse', 'HEAD')
    goal_sha = hashlib.sha256(GOAL_BODY.encode()).hexdigest()[:16]

    blk = ('<!-- RD-CHECKPOINT v1: json %s -->' % json.dumps({
        'round': 1, 'date': '2026-11-12 00:00 HKT', 'branch': 'main',
        'commit': c0, 'baseline': c0, 'goal_sha': goal_sha,
        'completed_ids': ['T-R1-1'], 'next_task': 'R2 下一任务fixture',
        'next_round': 2}, ensure_ascii=False))
    cs = (
        '# CURRENT_STATE — fixture\n\n> 引用行\n\n'
        '## 权威快照: fixture R1 收口\n'
        + ('> baseline=%s (机器行: rd_checkpoint.py 维护,勿手改)\n' % c0
           if stamped else '')
        + '- **真实进度**: R1 波次毕(fixture)\n\n'
        '### 任务台账\n\n'
        '> 台账只收活任务(进行中/待合并);已毕只进日志/存档。\n\n'
        '| ID | 状态 | Git证据 | 说明 |\n|---|---|---|---|\n'
        '| T-R1-1 | 待合并 | %s | fixture 波次 |\n\n'
        '### [历史快照·fixture]\n\n旧文。\n\n'
        '## 快照: 更旧\n\n旧文。\n' % c0[:10])
    resume = (
        '# RESUME — fixture\n\n'
        '## 恢复步骤\n\n1. 读状态\n\n'
        '## 下一步(fixture R1 收口后)\n\n1. R2 下一任务fixture\n\n'
        + (blk + '\n\n' if stamped else '')
        + '## 下一步存档\n\n1. [已毕·R0] 老任务(存档区允许标记)\n')
    log = (
        '# ITERATION_LOG — fixture\n\n'
        '| 日期 | 轮/章程 | 交付 | tag@SHA | 验收 |\n|---|---|---|---|---|\n'
        '| 11-12 | R1 状态波(T-R1-1) | gate fixture | dev/x@%s | 6/6 |\n'
        % c0[:10])
    fa = (
        '# FINAL_ACCEPTANCE — fixture\n\n'
        '## 验收矩阵(fixture)\n\n'
        '| # | 验收项 | 状态 | 证据 | 复核 |\n|---|---|---|---|---|\n'
        '| AC1 | 全景 | PASS | x | y |\n'
        '| AC2 | 机构 | PARTIAL | x | y |\n\n'
        '## 交叉映射(fixture)\n\n'
        '| 启动指令 | 本矩阵 | 说明 |\n|---|---|---|\n'
        '| AC7 研究地图 | (并入 AC1) | x |\n'
        '| AC11 可追溯 | AC8 | — |\n'
        '| AC12 合规 | AC10 | — |\n')
    open(os.path.join(sd, 'CURRENT_STATE.md'), 'w', encoding='utf-8').write(cs)
    open(os.path.join(sd, 'RESUME.md'), 'w', encoding='utf-8').write(resume)
    open(os.path.join(sd, 'ITERATION_LOG.md'), 'w', encoding='utf-8').write(log)
    open(os.path.join(sd, 'FINAL_ACCEPTANCE.md'), 'w', encoding='utf-8').write(fa)
    g('add', '-A')
    g('commit', '-m', 'C1 state docs')
    return {'repo': repo, 'sd': sd, 'c0': c0, 'c1': g('rev-parse', 'HEAD'),
            'goal_sha': goal_sha}


def fresh(mutate=None, stamped=True):
    """每用例独立夹具(隔离文件突变),可注入 mutate(sd, fx) 改写后重提交。"""
    base = tempfile.mkdtemp(prefix='rd_r20_')
    fx = build_fixture(base, stamped=stamped)
    if mutate:
        mutate(fx['sd'], fx)
        subprocess.run(['git', '-C', fx['repo'], 'add', '-A'],
                       capture_output=True, env=_git_env())
        subprocess.run(['git', '-C', fx['repo'], 'commit', '-m', 'mut'],
                       capture_output=True, env=_git_env())
    return fx


def expect_fail(key, name, mutate, msg_sub=None, stamped=True):
    base = tempfile.mkdtemp(prefix='rd_r20_')
    fx = build_fixture(base, stamped=stamped)
    files = ['CURRENT_STATE.md', 'RESUME.md', 'ITERATION_LOG.md',
             'FINAL_ACCEPTANCE.md', 'PRODUCT_GOAL.md']
    before = {f: open(os.path.join(fx['sd'], f), 'rb').read() for f in files}
    mutate(fx['sd'], fx)
    after = {f: open(os.path.join(fx['sd'], f), 'rb').read() for f in files}
    changed = [f for f in files if before[f] != after[f]]
    # 反假绿: 突变必须真实改动(状态档或仓内其他文件,如 B4 的代码提交)
    # 且不得把任何状态档清空(空文件导致的红=错因)
    pstat = subprocess.run(['git', '-C', fx['repo'], 'status', '--porcelain'],
                           capture_output=True, text=True,
                           env=_git_env()).stdout.strip()
    if not changed and not pstat:
        check(name, False, '突变零改动(无效突变)')
        return
    emptied = [f for f in changed if not after[f].strip()]
    if emptied:
        check(name, False, '突变把状态档清空: %s' % ','.join(emptied))
        return
    subprocess.run(['git', '-C', fx['repo'], 'add', '-A'],
                   capture_output=True, env=_git_env())
    subprocess.run(['git', '-C', fx['repo'], 'commit', '-m', 'mut'],
                   capture_output=True, env=_git_env())
    rep = run_gate(fx['repo'])
    msgs = rep.fails.get(key, [])
    ok = key in rep.fails and (msg_sub is None or
                               any(msg_sub in m for m in msgs))
    check(name, ok, 'fails=%s' % json.dumps(rep.fails, ensure_ascii=False))


def rewrite(name):
    def deco(fn):
        def wrapped(sd, fx):
            p = os.path.join(sd, name)
            text = open(p, encoding='utf-8').read()
            open(p, 'w', encoding='utf-8').write(fn(text, fx))
        return wrapped
    return deco


# ══════════════════════ A. 全绿基线 ══════════════════════

def sec_a():
    print('── A. 合成仓库六检全绿基线 ──')
    fx = fresh()
    rep = run_gate(fx['repo'])
    check('A1 六项全 PASS', not rep.fails,
          json.dumps(rep.fails, ensure_ascii=False))
    check('A2 ①注记含容忍类(main 超前 baseline=纯文档提交)',
          any('容忍' in n for n in rep.notes.get('①', [])),
          str(rep.notes.get('①')))
    check('A3 门入口退出码 0', cli(os.path.join(SCRIPTS,
          'rd_state_consistency.py'), '--repo', fx['repo'], '--quiet')[0] == 0)
    # 真实形态回归: FINAL_ACCEPTANCE 交叉映射行(AC11/AC12)不误伤已在夹具内
    check('A4 交叉映射 AC11/AC12 行未误伤(④ 只认矩阵节)',
          '④' not in rep.fails and not rep.fails)


# ══════════════════════ B. 变异锁牙 ══════════════════════

def sec_b():
    print('── B. 变异测试(逐项突变必红/容忍类不误杀) ──')
    expect_fail('①', 'B1 baseline 机器行被删→①红',
                rewrite('CURRENT_STATE.md')
                (lambda t, fx: re.sub(r'^> baseline=\S+.*\n', '', t,
                                      flags=re.M)))
    expect_fail('①', 'B2 baseline=不存在提交→①红',
                rewrite('CURRENT_STATE.md')
                (lambda t, fx: t.replace(fx['c0'], 'deadbee001')))
    expect_fail('①', 'B3 权威快照未置顶(R15 滞留形态)→①红',
                rewrite('CURRENT_STATE.md')
                (lambda t, fx: '## 历史快照·R15 滞留\n\n过期快照置顶=事故形态\n\n'
                 + t))

    def b4(sd, fx):
        open(os.path.join(fx['repo'], 'engine2.py'), 'w').write('y=2\n')
    expect_fail('①', 'B4 main 超前 baseline 含非文档提交→①红',
                b4, msg_sub='不容忍')

    def b5(sd, fx):
        open(os.path.join(sd, 'NOTE.md'), 'w', encoding='utf-8').write('n\n')
    fx = fresh(b5)
    check('B5 main 超前 baseline=纯文档提交→①仍绿(容忍类不误杀)',
          not run_gate(fx['repo']).fails)

    def b6(sd, fx):
        env = _git_env()
        subprocess.run(['git', '-C', fx['repo'], 'checkout', '-b', 'side'],
                       capture_output=True, env=env)
        open(os.path.join(sd, 'SIDE.md'), 'w', encoding='utf-8').write('s\n')
        subprocess.run(['git', '-C', fx['repo'], 'add', '-A'],
                       capture_output=True, env=env)
        subprocess.run(['git', '-C', fx['repo'], 'commit', '-m', 'side docs'],
                       capture_output=True, env=env)
        subprocess.run(['git', '-C', fx['repo'], 'checkout', 'main'],
                       capture_output=True, env=env)
        subprocess.run(['git', '-C', fx['repo'], 'merge', '--no-ff', 'side',
                        '-m', 'merge side'], capture_output=True, env=env)
    fx = fresh(b6)
    check('B6 main 超前 baseline=纯文档分支合并→①仍绿(合并+文档两类容忍)',
          not run_gate(fx['repo']).fails)

    expect_fail('②', 'B7 活动区含「已毕·」→②红',
                rewrite('RESUME.md')
                (lambda t, fx: t.replace('1. R2 下一任务fixture',
                                          '1. [已毕·R1] 已完成任务混入活动区')))
    expect_fail('②', 'B8 活动区含「待操作者合并」→②红',
                rewrite('RESUME.md')
                (lambda t, fx: t.replace('1. R2 下一任务fixture',
                                          '波次毕,待操作者合并')))
    expect_fail('②', 'B9 检查点块被删→②红',
                rewrite('RESUME.md')
                (lambda t, fx: re.sub(r'<!-- RD-CHECKPOINT.*?-->\n*', '', t)))
    expect_fail('②', 'B10 检查点块重复→②红',
                rewrite('RESUME.md')
                (lambda t, fx: t.replace(
                    '<!-- RD-CHECKPOINT', '<!-- RD-CHECKPOINT', 1)
                    + re.search(r'<!-- RD-CHECKPOINT.*?-->', t, re.S).group(0)
                    + '\n'))
    expect_fail('②', 'B11 块 json 破损→②红',
                rewrite('RESUME.md')
                (lambda t, fx: re.sub(r'\{.*?\}', '{"round": 1', t)))
    expect_fail('②', 'B12 块 commit=不存在提交→②红',
                rewrite('RESUME.md')
                (lambda t, fx: t.replace(fx['c0'], 'deadbee002')))
    expect_fail('②', 'B13 日志越过检查点(R2 行在场,块仍 R1)→②红',
                rewrite('ITERATION_LOG.md')
                (lambda t, fx: t + '| 11-12 | R2 越轮 | x | y | z |\n'))
    expect_fail('②', 'B14 块 next_round < round+1→②红',
                rewrite('RESUME.md')
                (lambda t, fx: t.replace('"next_round": 2', '"next_round": 1')))
    expect_fail('②', 'B15 块缺字段 goal_sha→②红',
                rewrite('RESUME.md')
                (lambda t, fx: t.replace('"goal_sha": "%s", ' % fx['goal_sha'],
                                          '')))
    expect_fail('③', 'B16 台账状态=已毕仍留→③红',
                rewrite('CURRENT_STATE.md')
                (lambda t, fx: t.replace('| 待合并 |', '| 已毕 |')))
    expect_fail('③', 'B17 台账状态非法(TODO)→③红',
                rewrite('CURRENT_STATE.md')
                (lambda t, fx: t.replace('| 待合并 |', '| TODO |')))
    expect_fail('③', 'B18 待合并证据列空→③红',
                rewrite('CURRENT_STATE.md')
                (lambda t, fx: re.sub(r'\| T-R1-1 \| 待合并 \| [0-9a-f]+ \|',
                                      '| T-R1-1 | 待合并 | — |', t)))
    expect_fail('③', 'B19 台账 ID 重复→③红',
                rewrite('CURRENT_STATE.md')
                (lambda t, fx: t
                    + '| T-R1-1 | 待合并 | %s | 重复行 |\n' % fx['c0'][:10]))
    expect_fail('③', 'B20 台账证据提交不存在→③红',
                rewrite('CURRENT_STATE.md')
                (lambda t, fx: t.replace(fx['c0'][:10], 'deadbee003')))
    expect_fail('③', 'B21 快照节缺「### 任务台账」子节→③红',
                rewrite('CURRENT_STATE.md')
                (lambda t, fx: t.replace('### 任务台账', '### 别的子节')))
    expect_fail('④', 'B22 矩阵状态非法(EXECUTED)→④红',
                rewrite('FINAL_ACCEPTANCE.md')
                (lambda t, fx: t.replace('| PASS |', '| EXECUTED |')))
    expect_fail('⑤', 'B23 进行中行轮次≤日志max(回流待办)→⑤红',
                rewrite('CURRENT_STATE.md')
                (lambda t, fx: t + '| T-R1-2 | 进行中 | — | 回流行 |\n'),
                msg_sub='回流')
    expect_fail('⑤', 'B24 待合并行波次滞留(轮次<日志max)→⑤红',
                rewrite('ITERATION_LOG.md')
                (lambda t, fx: t + '| 11-12 | R2 下一波 | x | y | z |\n'),
                msg_sub='滞留')
    expect_fail('⑤', 'B25 块 completed_ids 未在日志行登记→⑤红',
                rewrite('RESUME.md')
                (lambda t, fx: t.replace('T-R1-1', 'T-R1-9')))
    expect_fail('⑤', 'B26 待合并轮次>日志max(未收口先称毕)→⑤红',
                rewrite('CURRENT_STATE.md')
                (lambda t, fx: t + '| T-R2-1 | 待合并 | %s | 超前称毕 |\n'
                        % fx['c0'][:10]), msg_sub='未收口')
    expect_fail('⑥', 'B27 块 goal_sha 与档不一致→⑥红',
                rewrite('RESUME.md')
                (lambda t, fx: t.replace(fx['goal_sha'], '0000000000000000')))
    expect_fail('⑥', 'B28 PRODUCT_GOAL 被改(目标漂移)→⑥红',
                rewrite('PRODUCT_GOAL.md')
                (lambda t, fx: t + '\n被篡改\n'))


# ══════════════════════ C. 检查点管线 ══════════════════════

def sec_c():
    print('── C. rd_checkpoint 管线 ──')
    ck = os.path.join(SCRIPTS, 'rd_checkpoint.py')
    # 波中态(无块无机器行)→ finalize 盖章 → 门绿
    fx = fresh(stamped=False)
    rc, out = cli(ck, '--finalize', '--round', '1', '--next-round', '2',
                  '--next-task', 'R2 下一任务fixture', '--completed-ids',
                  'T-R1-1', '--repo', fx['repo'])
    check('C1 波中态 finalize→盖章后门绿(exit 0)', rc == 0, out[-500:])
    resume = open(os.path.join(fx['sd'], 'RESUME.md'), encoding='utf-8').read()
    check('C2 盖章后块恰一个',
          resume.count(gate.CHECKPOINT_MARK) == 1)
    cs = open(os.path.join(fx['sd'], 'CURRENT_STATE.md'),
              encoding='utf-8').read()
    check('C3 baseline 机器行=HEAD 盖入',
          ('baseline=%s' % fx['c1']) in cs, cs[:200])
    # 幂等: 重跑仍一个块,门仍绿
    rc2, out2 = cli(ck, '--finalize', '--round', '1', '--next-round', '2',
                    '--next-task', 'R2 下一任务fixture', '--completed-ids',
                    'T-R1-1', '--repo', fx['repo'])
    resume2 = open(os.path.join(fx['sd'], 'RESUME.md'),
                   encoding='utf-8').read()
    check('C4 finalize 幂等(重跑仍恰一块+门绿)',
          rc2 == 0 and resume2.count(gate.CHECKPOINT_MARK) == 1, out2[-300:])
    # 先日志后检查点: 日志无 R5 行 → refuse
    rc3, out3 = cli(ck, '--finalize', '--round', '5', '--next-round', '6',
                    '--next-task', 'x', '--completed-ids', 'T-R5-1',
                    '--repo', fx['repo'])
    check('C5 日志无对应轮次行→refuse(exit 1+提示)',
          rc3 == 1 and 'refuse' in out3, out3[-300:])
    # --verify 退出码面
    rc4, _ = cli(ck, '--verify', '--repo', fx['repo'])
    check('C6 --verify 盖章态 exit 0', rc4 == 0)
    fx2 = fresh(stamped=False)
    rc5, out5 = cli(ck, '--verify', '--repo', fx2['repo'])
    check('C7 --verify 波中态(无块)exit 1', rc5 == 1 and '检查点块' in out5)


# ══════════════════════ D. 浅克隆降级 ══════════════════════

def sec_d():
    print('── D. 浅克隆降级(CI depth=1 语义) ──')
    fx = fresh()
    base = os.path.dirname(fx['repo'])
    shallow = os.path.join(base, 'shallow')
    subprocess.run(['git', 'clone', '--depth', '1', '--branch', 'main',
                    'file://' + fx['repo'], shallow],
                   capture_output=True, env=_git_env())
    check('D0 前置: 克隆确为浅克隆', gate.is_shallow(shallow))
    rc, out = cli(os.path.join(SCRIPTS, 'rd_state_consistency.py'),
                  '--repo', shallow)
    check('D1 浅克隆门仍绿(结构面全量)', rc == 0, out[-400:])
    check('D2 降级显式注记', '浅克隆' in out, out[-400:])
    ck = os.path.join(SCRIPTS, 'rd_checkpoint.py')
    rc2, out2 = cli(ck, '--finalize', '--round', '1', '--next-round', '2',
                    '--next-task', 'x', '--completed-ids', 'T-R1-1',
                    '--repo', shallow)
    check('D3 浅克隆上 finalize 拒绝', rc2 == 1 and 'refuse' in out2,
          out2[-200:])


# ══════════════════════ E. 真仓门 ══════════════════════

def sec_e():
    print('── E. 真仓门(本仓库状态一致性 ratchet) ──')
    if gate.is_shallow(ROOT):
        print('  ⏭ E1/E2 SKIP: 真仓为浅克隆(CI 语义),结构面由 CI 自身运行覆盖')
        return
    rc, out = cli(os.path.join(SCRIPTS, 'rd_state_consistency.py'),
                  '--repo', ROOT)
    check('E1 真仓六项全 PASS(状态与仓库一致)', rc == 0, out[-600:])
    check('E2 真仓总结行 6/6', '6/6 PASS' in out, out[-200:])


def main():
    print('════ R20 状态一致性检查门+检查点管线 套件 ════')
    for sec in (sec_a, sec_b, sec_c, sec_d, sec_e):
        sec()
    print(f"\n{'='*60}\nR20 套件总结: PASS={PASS} FAIL={FAIL}")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == '__main__':
    main()
