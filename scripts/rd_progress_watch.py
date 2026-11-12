#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""研发进展漂移顾问(Charter 10 §4.3 防死循环,R21 落地)。

背景: 检查门(rd_state_consistency.py)锁「状态与仓库一致」,但不锁「每轮
是否真的在推进」。Charter 10 §4.3/§七 要求识别——连续多轮无实质进展、重复
修改同一问题、只改文档不改善实际能力。本顾问从 git 历史重建每轮改动面,
给出**非阻塞**预警(漂移是复审信号,不是失败信号;硬门留给一致性门)。

判据(全部来自 git 对象,不读任何自称文档):
  finalize 事件 = 改动过 RESUME.md 中 RD-CHECKPOINT 块行的提交(git log -G)。
  轮次 i 的工作面 = finalize(i-1)…finalize(i) 之间的全部路径改动,分三类:
    code        触及生产代码(*.py / config/**)——实质进展;
    tests-only  只触及 tests/**+docs+*.md(测试数量≠产品能力,Charter §七);
    docs-only   只触及 docs/**+*.md(纯文档轮)。
  预警:
    漂移预警  连续 ≥2 轮非 code(tests-only/docs-only)→ 「连续两轮没有实质
              进展时,必须重新审查根因和技术方案」(§4.3);
    返工预警  同一生产代码文件连续两轮被改 → 根因复审旗标(§4.3 重复修复
              同一个问题);tests/data 不算(每轮新增测试与新采集是常态)。

用法:
  python3 scripts/rd_progress_watch.py [--repo .] [--state-dir docs/autonomous-rd]
                                       [--window 4] [--strict] [--json]
  恒 exit 0(顾问非门);--strict 时有预警 exit 3(供人主动复核用,CI 不用)。
浅克隆/历史不足(<2 个 finalize)→ NOTE 降级注记,不预警。
"""

import argparse
import json
import os
import re
import subprocess
import sys

DEFAULT_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKPOINT_MARK = 'RD-CHECKPOINT v1: json'
BLOCK_RE = re.compile(
    r'<!--\s*RD-CHECKPOINT v1: json\s*(\{.*?\})\s*-->', re.S)
NON_CODE_EXEMPT = ('docs/',)          # 目录豁免前缀(纯文档)
CODE_SUFFIX = ('.py',)                # 生产代码后缀
CODE_PREFIX = ('config/',)            # 生产配置前缀
TESTS_PREFIX = ('tests/',)


def git(repo, *args):
    p = subprocess.run(['git', '-C', repo] + list(args),
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError('git %s 失败: %s'
                           % (' '.join(args), (p.stderr or '').strip()[:160]))
    return p.stdout


def classify(paths):
    """一轮改动面 → code / tests-only / docs-only(空面=docs-only)。"""
    kinds = set()
    for f in paths:
        if f.endswith('.md') or f.startswith(NON_CODE_EXEMPT):
            continue
        if f.startswith(TESTS_PREFIX):
            kinds.add('tests')
        elif f.endswith(CODE_SUFFIX) or f.startswith(CODE_PREFIX):
            kinds.add('code')
        else:  # data/ 等非文档非测试产物: 采集/研究产出=实质,归 code 面
            kinds.add('code')
    if 'code' in kinds:
        return 'code'
    if 'tests' in kinds:
        return 'tests-only'
    return 'docs-only'


def code_files(paths):
    """生产代码文件集(返工预警用;排除 tests)。"""
    out = set()
    for f in paths:
        if f.startswith(TESTS_PREFIX) or f.startswith(NON_CODE_EXEMPT):
            continue
        if f.endswith(CODE_SUFFIX) or f.startswith(CODE_PREFIX) \
                or not f.endswith('.md'):
            out.add(f)
    return out


def finalize_commits(repo, state_dir):
    """[(commit, round)] 按时间升序;round 从该提交树里的检查点块解析。"""
    out = git(repo, 'log', '-G', CHECKPOINT_MARK, '--format=%H',
              '--', os.path.join(state_dir, 'RESUME.md'))
    commits = [c for c in out.split() if c]
    finals = []
    for c in commits[::-1]:  # log 新→旧,反转为旧→新
        blob = git(repo, 'show', '%s:%s' % (c, os.path.join(
            state_dir, 'RESUME.md')))
        m = BLOCK_RE.search(blob)
        if not m:
            continue
        try:
            blk = json.loads(m.group(1))
            finals.append((c, int(blk.get('round', 0))))
        except (ValueError, TypeError):
            continue
    return finals


def analyze(repo, state_dir, window):
    """→ dict(finals=n, rounds=[{round,kind,files}], warnings=[...])。"""
    finals = finalize_commits(repo, state_dir)
    res = {'finals': len(finals), 'rounds': [], 'warnings': []}
    if len(finals) < 2:
        res['note'] = 'finalize 事件 %d 个(<2): 观察窗不足/浅克隆,顾问降级' \
                      % len(finals)
        return res
    intervals = finals[-(window + 1):]  # window 个区间
    for (prev, _), (cur, rnd) in zip(intervals, intervals[1:]):
        paths = git(repo, 'diff', '--name-only', prev, cur).splitlines()
        res['rounds'].append({'round': rnd, 'kind': classify(paths),
                              'files': len(paths),
                              'code_files': sorted(code_files(paths))})
    # 漂移预警: 连续 ≥2 轮非 code
    streak = []
    for r in res['rounds']:
        if r['kind'] == 'code':
            streak = []
        else:
            streak.append(r['round'])
            if len(streak) >= 2:
                res['warnings'].append(
                    '漂移预警: 连续 %d 轮无生产代码进展(R%s)——Charter10 '
                    '§4.3 根因复审,不得为保持运行无意义消耗资源'
                    % (len(streak), '→R'.join(str(s) for s in streak)))
    # 返工预警: 同一生产代码文件连续两轮被改
    for a, b in zip(res['rounds'], res['rounds'][1:]):
        both = set(a['code_files']) & set(b['code_files'])
        if both:
            show = ', '.join(sorted(both)[:3])
            res['warnings'].append(
                '返工预警: R%d→R%d 连续两轮改同一生产文件(%s)——§4.3 重复修复'
                '同一问题?根因复审' % (a['round'], b['round'], show))
    if not res['warnings']:
        res['note'] = '近 %d 轮无漂移/返工预警' % len(res['rounds'])
    return res


def main():
    ap = argparse.ArgumentParser(description='研发进展漂移顾问(非阻塞)')
    ap.add_argument('--repo', default=DEFAULT_REPO)
    ap.add_argument('--state-dir', default=None)
    ap.add_argument('--window', type=int, default=4)
    ap.add_argument('--strict', action='store_true',
                    help='有预警时 exit 3(默认恒 0;CI 不用 strict)')
    ap.add_argument('--json', action='store_true', help='机读输出')
    args = ap.parse_args()
    state_dir = args.state_dir or os.path.join('docs', 'autonomous-rd')
    try:
        res = analyze(args.repo, state_dir, args.window)
    except RuntimeError as e:
        print('NOTE 顾问降级: %s' % e)
        return 0
    if args.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        for r in res['rounds']:
            print('R%-3d %-11s %3d 文件' % (r['round'], r['kind'], r['files']))
        for w in res['warnings']:
            print('⚠ ' + w)
        if 'note' in res:
            print('NOTE ' + res['note'])
    if args.strict and res['warnings']:
        return 3
    return 0


if __name__ == '__main__':
    sys.exit(main())
