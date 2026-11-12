#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""研发状态一致性检查门(Charter 10 §3.1/§3.2,R20 落地)。

历史失同步根因(R15 视角快照滞留至 R19)= 状态档靠手写、无机器校验。
本脚本把「状态与仓库一致」变成可执行判据:任一项 FAIL 即退出码 1,
CI 与检查点管线(rd_checkpoint.py)都以此为硬门;恢复入口(RESUME 步骤0)
以此为「状态可信,准予开发」的判据。

用法:
  python3 scripts/rd_state_consistency.py [--repo PATH] [--state-dir PATH] [--quiet]
    --repo      Git 仓库/工作树路径(默认: 本脚本所在仓库根)
    --state-dir 状态档目录(默认: <repo>/docs/autonomous-rd)
    --quiet     只打印失败项与总结

六项检查(全部 PASS → 退出码 0):
  ① 基线一致   CURRENT_STATE 第一个 `## ` 节必须是 `## 权威快照`(唯一权威入口
               置顶);该节须含 `baseline=<sha>` 机器行;该提交须存在、是 HEAD
               祖先,且 main 尖端被 baseline 包含。main 超前 baseline 的提交只
               容忍四类: 合并提交 / 纯文档提交(改动全在 docs/** 或 *.md)/
               台账证据提交的后裔(该提交在证据链内)/ 检查点块 commit 的祖先
               (本轮工作面)——历史失同步(R15 快照滞留到 R19)在此硬失败。
  ② RESUME 健全 活动区(第一个 `## 下一步(` 节)不得含 已毕·/[已毕]/待操作者
               合并(已完成任务只进存档与日志);队列项 [进行中·R<n>] 的 n
               必须 > 日志最大轮(≤ = 已完成任务滞留待办,R15→R19 失同步实
               形态,FAIL);须恰有一个 RD-CHECKPOINT v1 块,json 合法、字段
               齐全,commit 存在且为 HEAD 祖先;轮次关系: 日志max ≤
               block.round ≤ 台账max+1;block.baseline 与 ①解析值一致;
               next_round ≥ round+1。
  ③ 台账规范   `| T-R<n>-<seq> | 状态 | Git证据 | 说明 |` 行: ID 唯一、格式
               合法,状态 ∈ {进行中, 待合并}(已毕=只进日志/存档,留台账即
               失败);待合并必须有真实存在的证据提交;进行中证据若填则须真实
               存在。权威快照节须含 `### 任务台账` 子节。
  ④ 验收矩阵   FINAL_ACCEPTANCE「验收矩阵」节内 AC 行状态列 ∈ {PASS,PARTIAL,
               FAIL,NOT_VERIFIED}(只扫该节——交叉映射表里的 AC11/AC12 行
               不是验收状态行)。
  ⑤ 日志-台账  ITERATION_LOG 须有轮次行;台账行轮次纪律: 进行中必须 > 日志
               最大轮(≤ 即已完成任务回流待办),待合并必须 == 日志最大轮
               (刚收口本轮、待操作者合并;偏旧=波次滞留失同步,偏新=未收口
               先称毕);检查点块 completed_ids 必须出现在同轮日志行内。
  ⑥ 目标完整   PRODUCT_GOAL.md 在场且 sha256[:16] 与检查点块 goal_sha 一致
               ——最终目标被任何一方改动都会在此硬失败(用户授权改动须同步
               更新检查点,防目标漂移/防静默删改)。

浅克隆降级(CI actions/checkout 默认 depth=1): 祖先关系与历史对象核验降级
为「存在性/结构」核验并显式注记「浅克隆降级」——结构面(枚举/标记/块解析/
goal_sha)在 CI 仍全量生效;本地开发树(全历史)六项全量。

波次纪律: 基线/容忍语义假设波次串行(一轮开发→合并→下一轮)。交错合并会
使 main 超前 baseline 的提交落入不容忍类——检查门失败即正确信号(需重新
收口对账),不是误报。
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

DEFAULT_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SNAPSHOT_HEADING = re.compile(r'^## 权威快照', re.M)
FIRST_H2 = re.compile(r'^## ', re.M)
HEADING_BOUND = re.compile(r'^#{2,3} ', re.M)
BASELINE_EQ = re.compile(r'baseline=([0-9a-f]{7,40})')
LEDGER_HEADING = '### 任务台账'
# | ID | 状态 | Git证据 | 说明 |
LEDGER_ROW = re.compile(
    r'^\|\s*(T-R(\d+)-(\d+))\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*$',
    re.M)
ACTIVE_HEADING = re.compile(r'^## 下一步\(', re.M)
ANY_HEADING = re.compile(r'^## ', re.M)
FORBIDDEN_ACTIVE_MARKERS = ('已毕·', '[已毕]', '待操作者合并')
CHECKPOINT_MARK = 'RD-CHECKPOINT v1: json'
CHECKPOINT_BLOCK = re.compile(
    r'<!--\s*RD-CHECKPOINT v1: json\s*(\{.*?\})\s*-->', re.S)
SHA_TOKEN = re.compile(r'\b[0-9a-f]{7,40}\b')
LOG_ROW_ROUND = re.compile(r'^\|\s*\d{1,2}-\d{1,2}\s*\|\s*([^|]*)\|')
MATRIX_HEADING = re.compile(r'^## 验收矩阵', re.M)
AC_ROW = re.compile(r'^\|\s*(AC\d+)\s*\|([^|]*)\|\s*([^|]*?)\s*\|', re.M)
AC_STATUSES = ('PASS', 'PARTIAL', 'FAIL', 'NOT_VERIFIED')
LEDGER_STATUSES = ('进行中', '待合并')  # 台账只收活任务;已毕只进日志/存档
BLOCK_KEYS = ('round', 'date', 'branch', 'commit', 'completed_ids',
              'next_task', 'next_round', 'baseline', 'goal_sha')
CHECK_ORDER = ('①', '②', '③', '④', '⑤', '⑥')
CHECK_NAMES = {'①': '基线一致', '②': 'RESUME健全', '③': '台账规范',
               '④': '验收矩阵', '⑤': '日志-台账', '⑥': '目标完整'}


class GitError(Exception):
    pass


def git(repo, *args):
    p = subprocess.run(['git', '-C', repo] + list(args),
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise GitError('git %s 失败: %s' % (' '.join(args),
                                            (p.stderr or p.stdout).strip()[:200]))
    return p.stdout


def commit_exists(repo, sha):
    p = subprocess.run(['git', '-C', repo, 'cat-file', '-e', sha + '^{commit}'],
                       capture_output=True, text=True)
    return p.returncode == 0


def is_ancestor(repo, a, b):
    """a 是 b 的祖先(或 a==b)则 True。"""
    p = subprocess.run(['git', '-C', repo, 'merge-base', '--is-ancestor', a, b],
                       capture_output=True, text=True)
    return p.returncode == 0


def is_shallow(repo):
    try:
        return git(repo, 'rev-parse', '--is-shallow-repository').strip() == 'true'
    except GitError:
        return False


def section(text, start_re):
    """从首个匹配 start_re 的行取到下一个 ^## 或 ^### 标题(不含)。"""
    m = start_re.search(text)
    if not m:
        return None
    for hm in HEADING_BOUND.finditer(text, m.end()):
        return text[m.start():hm.start()]
    return text[m.start():]


def zone(text, start_re):
    """从首个匹配 start_re 的行取到下一个 ^## 标题(不含,### 子节保留在内)。"""
    m = start_re.search(text)
    if not m:
        return None
    for hm in ANY_HEADING.finditer(text, m.end()):
        return text[m.start():hm.start()]
    return text[m.start():]


def active_section(resume_text):
    """RESUME 第一个 `## 下一步(` 节(到下一个 ^## 标题,不含)。"""
    m = ACTIVE_HEADING.search(resume_text)
    if not m:
        return None
    for hm in ANY_HEADING.finditer(resume_text, m.end()):
        return resume_text[m.start():hm.start()]
    return resume_text[m.start():]


def parse_ledger(cs_text):
    """→ [(id, round_int, seq, status, evidence, note)]"""
    out = []
    for m in LEDGER_ROW.finditer(cs_text):
        out.append((m.group(1), int(m.group(2)), m.group(3),
                    m.group(4).strip(), m.group(5).strip(), m.group(6).strip()))
    return out


def parse_log_rounds(log_text):
    """→ [(round_int, row_text)](无 R 编号的行跳过)"""
    out = []
    for line in log_text.splitlines():
        m = LOG_ROW_ROUND.match(line)
        if not m:
            continue
        rm = re.search(r'\bR(\d+)\b', m.group(1))
        if rm:
            out.append((int(rm.group(1)), line))
    return out


class Report(object):
    def __init__(self):
        self.fails = {}
        self.notes = {}
        self.shallow = False

    def fail(self, check, msg):
        self.fails.setdefault(check, []).append(msg)

    def note(self, check, msg):
        self.notes.setdefault(check, []).append(msg)

    def summary(self, quiet):
        lines = []
        if self.shallow:
            lines.append('(浅克隆: ①② 的祖先/历史对象核验降级为存在性核验,'
                         '结构面全量生效)')
        for c in CHECK_ORDER:
            if c in self.fails:
                for msg in self.fails[c]:
                    lines.append('%s%s FAIL: %s' % (c, CHECK_NAMES[c], msg))
            elif not quiet:
                extra = '; '.join(self.notes.get(c, [])) or '—'
                lines.append('%s%s PASS  %s' % (c, CHECK_NAMES[c], extra))
        npass = len(CHECK_ORDER) - len(self.fails)
        lines.append('── 总结: %d/%d PASS%s' % (npass, len(CHECK_ORDER),
                    '' if npass == len(CHECK_ORDER)
                    else '(检查门拒绝——禁止开发,先按 Charter 10 §3.2 对账恢复)'))
        return '\n'.join(lines) + '\n'


def is_tolerated(repo, c, ledger_ev, blk_commit):
    """main 超前 baseline 的单个提交是否属容忍类(方向: 该提交在状态已知链内)。"""
    parents = git(repo, 'rev-list', '--parents', '-n', '1', c).split()
    if len(parents) >= 3:  # 自身 + ≥2 父 = 合并提交
        return True
    files = git(repo, 'diff-tree', '--no-commit-id', '--name-only', '-r',
                c).splitlines()
    if files and all(f.startswith('docs/') or f.endswith('.md') for f in files):
        return True
    for ev in ledger_ev:                # c 是某证据提交的祖先(在证据链内)
        if is_ancestor(repo, c, ev):
            return True
    if blk_commit and is_ancestor(repo, c, blk_commit):  # c 在本轮工作面内
        return True
    return False


def run_checks(repo, state_dir, rep):
    sh = is_shallow(repo)
    rep.shallow = sh

    def anc_ok(a, b, check, what):
        """祖先核验;浅克隆降级为注记跳过(存在性另行核)。"""
        if sh:
            rep.note(check, '浅克隆降级: %s 祖先核验跳过' % what)
            return True
        return is_ancestor(repo, a, b)

    def obj_ok(sha, check, what):
        if commit_exists(repo, sha):
            return True
        if sh:
            rep.note(check, '浅克隆降级: %s 历史对象不在场,跳过' % what)
            return True
        return False

    sd = lambda name: os.path.join(state_dir, name)

    for name in ('CURRENT_STATE.md', 'RESUME.md', 'ITERATION_LOG.md',
                 'FINAL_ACCEPTANCE.md', 'PRODUCT_GOAL.md'):
        if not os.path.isfile(sd(name)):
            rep.fail('①', '状态档缺失: %s' % name)
            return

    read = lambda name: open(sd(name), encoding='utf-8').read()
    cs = read('CURRENT_STATE.md')
    resume = read('RESUME.md')
    log = read('ITERATION_LOG.md')
    fa = read('FINAL_ACCEPTANCE.md')

    head = git(repo, 'rev-parse', 'HEAD').strip()
    main_sha = None
    for ref in ('main', 'origin/main'):
        p = subprocess.run(['git', '-C', repo, 'rev-parse', '--verify', '--quiet',
                            ref + '^{commit}'], capture_output=True, text=True)
        if p.returncode == 0:
            main_sha = p.stdout.strip()
            break
    rep.note('①', 'HEAD=%s main=%s' % (head[:9],
             main_sha[:9] if main_sha else '无'))

    snap = section(cs, SNAPSHOT_HEADING)
    ledger = parse_ledger(cs)
    log_rows = parse_log_rounds(log)
    log_max = max((r for r, _ in log_rows), default=None)
    ledger_max = max((row[1] for row in ledger), default=None)
    active = active_section(resume)

    # 检查点块解析(①②⑤⑥ 共用;解析失败只记 ②,块保持 None)
    blk = None
    n_marks = resume.count(CHECKPOINT_MARK)
    if n_marks == 1:
        m = CHECKPOINT_BLOCK.search(resume)
        if m:
            try:
                blk = json.loads(m.group(1))
            except ValueError as e:
                rep.fail('②', '检查点块 json 解析失败: %s' % e)
        else:
            rep.fail('②', '检查点块注释不闭合(<!-- … -->)')
    elif n_marks == 0:
        rep.fail('②', '无 RD-CHECKPOINT v1 检查点块')
    else:
        rep.fail('②', 'RD-CHECKPOINT 块出现 %d 次(须恰一个)' % n_marks)

    # ═══ ① 基线一致 ═══
    if snap is None:
        rep.fail('①', 'CURRENT_STATE 无 `## 权威快照` 节')
    else:
        h2 = FIRST_H2.search(cs)
        if h2 and not cs[h2.start():].startswith('## 权威快照'):
            rep.fail('①', '权威快照节未置顶(第一个 `## ` 节=「%s…」,'
                     '须为 `## 权威快照`)' % cs[h2.start() + 3:h2.start() + 13])
        bm = BASELINE_EQ.search(snap)
        if not bm:
            rep.fail('①', '权威快照节缺 `baseline=<sha>` 机器行')
        elif not obj_ok(bm.group(1), '①', 'baseline=%s' % bm.group(1)[:12]):
            rep.fail('①', 'baseline=%s 不是仓库中的提交' % bm.group(1)[:12])
        else:
            try:
                base = git(repo, 'rev-parse',
                           bm.group(1) + '^{commit}').strip()
            except GitError:
                if sh:  # 浅克隆对象不在场但存在性已降级通过: 短链解析一并降级
                    rep.note('①', '浅克隆降级: baseline 短链解析跳过(对象不在场)')
                    base = bm.group(1)
                else:
                    raise
            if not anc_ok(base, head, '①', 'baseline→HEAD'):
                rep.fail('①', 'baseline=%s 不是 HEAD(%s) 的祖先'
                         % (base[:9], head[:9]))
            if main_sha is None:
                rep.fail('①', '无法解析 main 引用(本地 main/origin/main 均缺)')
            elif main_sha == base or (not sh and is_ancestor(repo, main_sha, base)):
                rep.note('①', 'baseline=%s(含 main 尖端)' % base[:9])
            elif sh:
                rep.note('①', '浅克隆降级: main 超前 baseline 的容忍类核验跳过')
            else:
                ledger_ev = []
                for _, _, _, _, ev, _ in ledger:
                    ledger_ev.extend(SHA_TOKEN.findall(ev))
                blk_commit = str(blk.get('commit')) if blk else None
                delta = git(repo, 'rev-list', '%s..%s' % (base, main_sha)).split()
                bad = [c for c in delta
                       if not is_tolerated(repo, c, ledger_ev, blk_commit)]
                if bad:
                    show = ', '.join(c[:9] for c in bad[:3])
                    rep.fail('①', 'main 超前 baseline %d 个提交中 %d 个不容忍'
                             '(非合并/非纯文档/不在证据链/不在工作面;如 %s…)'
                             '——状态失同步,先对账' % (len(delta), len(bad), show))
                else:
                    rep.note('①', 'baseline=%s(main 超前 %d 提交均属容忍类)'
                             % (base[:9], len(delta)))

    # ═══ ② RESUME 健全 ═══
    if active is None:
        rep.fail('②', 'RESUME 无活动区 `## 下一步(` 节')
    else:
        for marker in FORBIDDEN_ACTIVE_MARKERS:
            if marker in active:
                rep.fail('②', '活动区含已完成标记「%s」(已完成任务只进存档/日志)'
                         % marker)
        # 滞留进行中标记: 已入日志轮次的队列项仍挂 [进行中·R<n>](R15/R19 失同步
        # 的实际形态之一 = 已完成任务留在待办);n ≤ 日志最大轮即 FAIL。
        if log_max is not None:
            for tm in re.finditer(r'\[进行中·R(\d+)\]', active):
                if int(tm.group(1)) <= log_max:
                    rep.fail('②', '活动区队列项仍挂 [进行中·R%d] 但 R%d ≤ 日志'
                             '已记最大轮 R%d——已完成任务滞留待办,先归档入存档节'
                             % (int(tm.group(1)), int(tm.group(1)), log_max))
        if blk is not None:
            missing = [k for k in BLOCK_KEYS if k not in blk]
            if missing:
                rep.fail('②', '检查点块缺字段: %s' % ','.join(missing))
            else:
                bc = str(blk['commit'])
                if not re.fullmatch(r'[0-9a-f]{7,40}', bc):
                    rep.fail('②', '块 commit 字段非 sha: %r' % bc[:20])
                elif not obj_ok(bc, '②', '块 commit=%s' % bc[:12]):
                    rep.fail('②', '块 commit=%s 不在仓库中' % bc[:12])
                elif not anc_ok(bc, head, '②', '块 commit→HEAD'):
                    rep.fail('②', '块 commit=%s 不是 HEAD(%s) 的祖先——状态可疑'
                             % (bc[:9], head[:9]))
                if not str(blk.get('next_task', '')).strip():
                    rep.fail('②', '块 next_task 为空')
                for k in ('branch', 'date'):
                    if not str(blk.get(k, '')).strip():
                        rep.fail('②', '块 %s 为空' % k)
                if not isinstance(blk.get('completed_ids'), list) \
                        or not all(isinstance(x, str) for x in blk['completed_ids']) \
                        or not blk['completed_ids']:
                    rep.fail('②', '块 completed_ids 须为非空字符串数组')
                try:
                    br = int(blk['round'])
                    nr = int(blk['next_round'])
                except (TypeError, ValueError):
                    br = nr = None
                    rep.fail('②', '块 round/next_round 非整数: %r/%r'
                             % (blk.get('round'), blk.get('next_round')))
                if br is not None:
                    if log_max is not None and log_max > br:
                        rep.fail('②', '日志最大轮 R%d > 块 round R%d(日志越过检查点)'
                                 % (log_max, br))
                    if ledger_max is not None and ledger_max > br + 1:
                        rep.fail('②', '台账最大轮 R%d 超前块 round R%d 一轮以上'
                                 % (ledger_max, br))
                    if nr is not None and nr < br + 1:
                        rep.fail('②', '块 next_round R%d < round R%d+1' % (nr, br))
                bb = str(blk.get('baseline', ''))
                base_m = BASELINE_EQ.search(snap) if snap else None
                if base_m and re.fullmatch(r'[0-9a-f]{7,40}', bb):
                    if not (bb.startswith(base_m.group(1))
                            or base_m.group(1).startswith(bb)):
                        rep.fail('②', '块 baseline=%s 与权威快照 baseline=%s 不一致'
                                 % (bb[:9], base_m.group(1)[:9]))
                if not rep.fails.get('②'):
                    rep.note('②', '块 R%s commit=%s next=%s…'
                             % (blk.get('round'), str(blk['commit'])[:9],
                                str(blk['next_task'])[:12]))

    # ═══ ③ 台账规范(台账子节用 zone 判在场——快照区的 ### 子节属快照区) ═══
    snap_zone = zone(cs, SNAPSHOT_HEADING)
    if snap_zone is None or LEDGER_HEADING not in snap_zone:
        rep.fail('③', '权威快照节缺 `%s` 子节' % LEDGER_HEADING)
    ids = [row[0] for row in ledger]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        rep.fail('③', '台账 ID 重复: %s' % ','.join(dup))
    n_progr = 0
    for tid, rnd, seq, status, ev, note in ledger:
        if status not in LEDGER_STATUSES:
            rep.fail('③', '%s 状态非法: %r(台账只收: %s;已毕只进日志/存档)'
                     % (tid, status, '/'.join(LEDGER_STATUSES)))
            continue
        if status == '待合并' and not SHA_TOKEN.findall(ev):
            rep.fail('③', '%s 待合并但 Git证据列为空' % tid)
        for s in SHA_TOKEN.findall(ev):
            if not obj_ok(s, '③', '%s 证据 %s' % (tid, s[:12])):
                rep.fail('③', '%s 证据提交 %s 不在仓库中' % (tid, s[:12]))
        if status == '进行中':
            n_progr += 1
    if not rep.fails.get('③'):
        rep.note('③', '台账 %d 行(进行中 %d)' % (len(ledger), n_progr))

    # ═══ ④ 验收矩阵(只扫「验收矩阵」节——交叉映射表非状态行) ═══
    mx = section(fa, MATRIX_HEADING)
    if mx is None:
        rep.fail('④', 'FINAL_ACCEPTANCE 无 `## 验收矩阵` 节')
    else:
        ac_rows = AC_ROW.findall(mx)
        if not ac_rows:
            rep.fail('④', '验收矩阵节无 AC 矩阵行')
        else:
            for ac, _name, status in ac_rows:
                if status.strip() not in AC_STATUSES:
                    rep.fail('④', '%s 状态非法: %r(合法: %s)'
                             % (ac, status.strip(), '/'.join(AC_STATUSES)))
            if not rep.fails.get('④'):
                rep.note('④', 'AC 行 %d,状态全合法' % len(ac_rows))

    # ═══ ⑤ 日志-台账 ═══
    if log_max is None:
        rep.fail('⑤', 'ITERATION_LOG 无轮次行')
    else:
        for tid, rnd, seq, status, ev, note in ledger:
            if status == '进行中' and rnd <= log_max:
                rep.fail('⑤', '台账行 %s(R%d·进行中) ≤ 日志已记最大轮 R%d——'
                         '已完成任务回流待办' % (tid, rnd, log_max))
            elif status == '待合并' and rnd != log_max:
                dirn = '波次滞留失同步(先对账: 合并或收口)' if rnd < log_max \
                    else '未收口先称毕(先补日志行)'
                rep.fail('⑤', '台账行 %s(R%d·待合并) ≠ 日志最大轮 R%d——%s'
                         % (tid, rnd, log_max, dirn))
        if blk is not None and 'completed_ids' in blk:
            try:
                br = int(blk['round'])
                rows_txt = '\n'.join(t for r, t in log_rows if r == br)
                if not rows_txt:
                    rep.fail('⑤', '块 round=R%d 在 ITERATION_LOG 无对应行' % br)
                else:
                    for tid in blk['completed_ids']:
                        if tid not in rows_txt:
                            rep.fail('⑤', '块 completed_ids 含 %s 但 R%d 日志行未登记'
                                     % (tid, br))
            except (TypeError, ValueError):
                pass
        if not rep.fails.get('⑤'):
            rep.note('⑤', '日志最大轮 R%d;台账无回流/无滞留' % log_max)

    # ═══ ⑥ 目标完整 ═══
    cur = hashlib.sha256(open(sd('PRODUCT_GOAL.md'), 'rb').read()).hexdigest()[:16]
    if blk is not None and 'goal_sha' in blk:
        if str(blk['goal_sha']) != cur:
            rep.fail('⑥', 'PRODUCT_GOAL.md sha256[:16]=%s ≠ 检查点 goal_sha=%s'
                     '——最终目标被改动(仅用户可改;用户授权改动须同步更新检查点)'
                     % (cur, blk['goal_sha']))
        else:
            rep.note('⑥', 'PRODUCT_GOAL sha=%s 与检查点一致' % cur)
    elif blk is not None:
        rep.note('⑥', '检查点块无 goal_sha 字段(② 已记缺字段)')


def main():
    ap = argparse.ArgumentParser(description='研发状态一致性检查门(R20)')
    ap.add_argument('--repo', default=DEFAULT_REPO,
                    help='Git 仓库/工作树路径(默认: 本脚本所在仓库根)')
    ap.add_argument('--state-dir', default=None,
                    help='状态档目录(默认: <repo>/docs/autonomous-rd)')
    ap.add_argument('--quiet', action='store_true', help='只打印失败项与总结')
    args = ap.parse_args()
    state_dir = args.state_dir or os.path.join(args.repo, 'docs', 'autonomous-rd')
    rep = Report()
    print('════ RD 状态一致性检查门(Charter 10 §3.1/§3.2·R20) ════')
    print('repo=%s state-dir=%s' % (args.repo, state_dir))
    try:
        run_checks(args.repo, state_dir, rep)
    except GitError as e:
        rep.fail('①', 'git 操作失败: %s' % e)
    sys.stdout.write(rep.summary(args.quiet))
    sys.exit(0 if not rep.fails else 1)


if __name__ == '__main__':
    main()
