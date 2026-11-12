#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""研发检查点管线(Charter 10 §3.2,R20 落地)。

把「每轮结束后的状态收口」从纯手工变成半自动硬门:
  人工完成 prose 面(能力矩阵/未解决问题/研发日志行/权威快照 prose)
  → 本管线 --finalize 盖机器面(检查点块+baseline 机器行,取值=实际 Git)
  → 立即跑一致性检查门(rd_state_consistency.py)
  → 门红=状态与仓库矛盾,禁止收口进入下一轮(§3.2 原文)。

用法:
  python3 scripts/rd_checkpoint.py --verify [--repo P] [--state-dir D]
      只跑检查门(恢复入口步骤0 同款;退出码 0/1)。
  python3 scripts/rd_checkpoint.py --show [--repo P] [--state-dir D]
      打印当前检查点块+Git 事实+检查门结果(人读)。
  python3 scripts/rd_checkpoint.py --finalize --round N --next-round M \
      --next-task "下一任务一句话" [--completed-ids T-Rn-1,T-Rn-2] \
      [--repo P] [--state-dir D]
      盖章收口(幂等: 重跑覆盖旧块,块数恒 1)。

--finalize 纪律:
  * 先决: ITERATION_LOG 必须已有 R<N> 行(§3.2 顺序=日志在前,检查点在后),
    没有则拒绝(exit 1,提示先补日志行)——防「先称毕后补账」。
  * 取值: commit/baseline = 调用时的 HEAD(=本轮代码提交;文档改动尚未提交,
    随后与盖章同落一个 docs 提交,门在提交后仍绿=自洽)。
  * goal_sha = PRODUCT_GOAL.md sha256[:16](防目标漂移,检查门⑥ 互锁)。
  * 台账(### 任务台账)与快照 prose 为人工面——本管线不改,只经检查门校验。

时间戳: HKT(UTC+8),仓库时区纪律(CLAUDE.md)。
"""

import argparse
import datetime
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rd_state_consistency as gate  # noqa: E402


def now_hkt():
    t = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    return t.strftime('%Y-%m-%d %H:%M HKT')


def goal_sha(state_dir):
    with open(os.path.join(state_dir, 'PRODUCT_GOAL.md'), 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def block_line(blk):
    return '<!-- RD-CHECKPOINT v1: json %s -->' % json.dumps(
        blk, ensure_ascii=False, separators=(', ', ': '))


def insert_into_active(resume_text, line):
    """把检查点块插到 RESUME 活动区末尾(下一个 ^## 标题前;无则文末)。"""
    m = gate.ACTIVE_HEADING.search(resume_text)
    if not m:
        raise SystemExit('RESUME 无 `## 下一步(` 活动区, refuse finalize')
    for hm in gate.ANY_HEADING.finditer(resume_text, m.end()):
        i = hm.start()
        return resume_text[:i].rstrip() + '\n\n' + line + '\n\n' + resume_text[i:]
    return resume_text.rstrip() + '\n\n' + line + '\n'


def stamp_baseline(cs_text, sha):
    """权威快照节内 baseline 机器行: 有则替换,无则插到节标题行后。"""
    m = gate.SNAPSHOT_HEADING.search(cs_text)
    if not m:
        raise SystemExit('CURRENT_STATE 无 `## 权威快照` 节, refuse finalize')
    end = None
    for hm in gate.HEADING_BOUND.finditer(cs_text, m.end()):
        end = hm.start()
        break
    seg = cs_text[m.start():end] if end is not None else cs_text[m.start():]
    new_line = 'baseline=%s' % sha
    if gate.BASELINE_EQ.search(seg):
        seg2 = gate.BASELINE_EQ.sub(new_line, seg, count=1)
    else:
        # 插在节标题行之后,带人读注记
        first_nl = seg.find('\n')
        note = '\n> baseline=%s (机器行: rd_checkpoint.py 维护,勿手改)' % sha
        seg2 = seg[:first_nl] + note + seg[first_nl:]
    return cs_text[:m.start()] + seg2 + (cs_text[end:] if end is not None else '')


def cmd_finalize(args, state_dir):
    repo = args.repo
    if gate.is_shallow(repo):
        print('refuse: 浅克隆无完整历史,--finalize 须在全量开发树运行')
        return 1
    head = gate.git(repo, 'rev-parse', 'HEAD').strip()
    branch = gate.git(repo, 'rev-parse', '--abbrev-ref', 'HEAD').strip()
    log_text = open(os.path.join(state_dir, 'ITERATION_LOG.md'),
                    encoding='utf-8').read()
    log_rounds = [r for r, _ in gate.parse_log_rounds(log_text)]
    if args.round not in log_rounds:
        print('refuse: ITERATION_LOG 无 R%d 行——按 §3.2 顺序先追加研发日志行,'
              '再 finalize(防先称毕后补账)' % args.round)
        return 1
    if args.next_round < args.round + 1:
        print('refuse: next_round R%d < round R%d+1' % (args.next_round, args.round))
        return 1
    if not args.next_task.strip():
        print('refuse: --next-task 为空')
        return 1
    completed = [x.strip() for x in (args.completed_ids or '').split(',')
                 if x.strip()]
    if not completed:
        print('refuse: --completed-ids 为空(本轮至少收口一个任务 ID)')
        return 1

    blk = {
        'round': args.round,
        'date': now_hkt(),
        'branch': branch,
        'commit': head,
        'baseline': head,
        'goal_sha': goal_sha(state_dir),
        'completed_ids': completed,
        'next_task': args.next_task.strip(),
        'next_round': args.next_round,
    }
    line = block_line(blk)

    # ── RESUME: 盖检查点块(恰一个;已有一个=幂等覆盖) ──
    rp = os.path.join(state_dir, 'RESUME.md')
    resume_text = open(rp, encoding='utf-8').read()
    n = resume_text.count(gate.CHECKPOINT_MARK)
    if n == 1:
        resume_text = gate.CHECKPOINT_BLOCK.sub(
            lambda _m: line, resume_text, count=1)
    elif n == 0:
        resume_text = insert_into_active(resume_text, line)
    else:
        print('refuse: RESUME 已有 %d 个检查点块(须 ≤1),人工清理后再来' % n)
        return 1
    open(rp, 'w', encoding='utf-8').write(resume_text)

    # ── CURRENT_STATE: baseline 机器行(有则换,无则插) ──
    cp = os.path.join(state_dir, 'CURRENT_STATE.md')
    cs_text = open(cp, encoding='utf-8').read()
    open(cp, 'w', encoding='utf-8').write(stamp_baseline(cs_text, head))

    print('盖章完成: round=R%d commit=%s branch=%s goal_sha=%s'
          % (args.round, head[:9], branch, blk['goal_sha']))
    print('提醒: 能力矩阵/未解决问题/快照 prose 为人工面,本管线不校验内容——'
          '按 §3.2 清单确认已完成。')
    return None  # 继续跑门


def run_gate(repo, state_dir, quiet=False):
    rep = gate.Report()
    gate.run_checks(repo, state_dir, rep)
    sys.stdout.write(rep.summary(quiet))
    return 0 if not rep.fails else 1


def main():
    ap = argparse.ArgumentParser(description='研发检查点管线(R20)')
    ap.add_argument('--repo', default=gate.DEFAULT_REPO,
                    help='Git 仓库/工作树路径(默认: 本脚本所在仓库根)')
    ap.add_argument('--state-dir', default=None,
                    help='状态档目录(默认: <repo>/docs/autonomous-rd)')
    sub = ap.add_mutually_exclusive_group(required=True)
    sub.add_argument('--verify', action='store_true', help='只跑检查门')
    sub.add_argument('--show', action='store_true', help='打印检查点+Git事实+门')
    sub.add_argument('--finalize', action='store_true', help='盖章收口+跑门')
    ap.add_argument('--round', type=int, help='本轮轮次号(finalize)')
    ap.add_argument('--next-round', type=int, help='下一轮轮次号(finalize)')
    ap.add_argument('--next-task', default='', help='下一任务一句话(finalize)')
    ap.add_argument('--completed-ids', default='',
                    help='逗号分隔的本轮任务 ID(finalize)')
    ap.add_argument('--quiet', action='store_true', help='门只打印失败项')
    args = ap.parse_args()
    state_dir = args.state_dir or os.path.join(args.repo, 'docs',
                                               'autonomous-rd')
    print('════ RD 检查点管线(Charter 10 §3.2·R20) ════')
    print('repo=%s state-dir=%s' % (args.repo, state_dir))
    rc = None
    try:
        if args.finalize:
            if args.round is None or args.next_round is None:
                print('refuse: --finalize 须同时给 --round 与 --next-round')
                sys.exit(1)
            rc = cmd_finalize(args, state_dir)
        if args.show:
            resume = open(os.path.join(state_dir, 'RESUME.md'),
                          encoding='utf-8').read()
            m = gate.CHECKPOINT_BLOCK.search(resume)
            print('检查点块: %s' % (json.dumps(
                json.loads(m.group(1)), ensure_ascii=False, indent=1
            ) if m else '(无)'))
            print('HEAD=%s branch=%s shallow=%s' % (
                gate.git(args.repo, 'rev-parse', '--short', 'HEAD').strip(),
                gate.git(args.repo, 'rev-parse', '--abbrev-ref', 'HEAD').strip(),
                gate.is_shallow(args.repo)))
    except gate.GitError as e:
        print('git 操作失败: %s' % e)
        sys.exit(1)
    sys.exit(run_gate(args.repo, state_dir, args.quiet) if rc is None else rc)


if __name__ == '__main__':
    main()
