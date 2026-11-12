#!/usr/bin/env python3
"""R21(2026-11-12): 防死循环顾问 + finalize 协议加固套件(Charter 10 §4.3)。

背景: R20 事故(fbc8f18 盖章后又落代码提交 6de30f5,合并后工作面容忍类
过期 → ①基线红)暴露 finalize 必须是分支最后一笔;同时 Charter 10 §4.3
要求识别「连续多轮无实质进展/重复修复同一问题」。本套件锁:

  A. 分类单元: classify/code_files 的三分(code/tests-only/docs-only)与
     tests/、docs/ 豁免。
  B. 合成仓库: 两个连续 docs-only 轮 → 漂移预警;连续两轮改同一生产文件 →
     返工预警;干净历史零预警。
  C. 降级面: 单 finalize(观察窗不足)不预警恒 exit 0;--strict 有预警
     exit 3;--window 截断;--json 机读。
  D. finalize 协议事故弧(R20 事故类回归锁,复用 R20 门夹具):
     盖章→门绿 → 再落代码提交 → ①基线红(工作面容忍过期) → 重新盖章
     (幂等) → 门绿=对账自愈。即「finalize 后不得再有代码提交;若发生,
     门红拦截,重盖章即治愈」全程机证。

跑法: python3 tests/test_rd_r21_deadloop.py  → exit 0/1(PASS/FAIL 计数)
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, '..', 'scripts')
FAILURES = []


def check(name, cond, detail=''):
    print('%s %s%s' % ('✅' if cond else '❌', name,
                       ('  ← ' + str(detail)[:220]) if not cond else ''))
    if not cond:
        FAILURES.append(name)


def load(mod_name, path):
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


watch = load('rd_progress_watch',
             os.path.join(SCRIPTS, 'rd_progress_watch.py'))

_git_env = dict(os.environ)
_git_env.update({'GIT_AUTHOR_NAME': 'fixture', 'GIT_AUTHOR_EMAIL': 'f@x',
                 'GIT_COMMITTER_NAME': 'fixture',
                 'GIT_COMMITTER_EMAIL': 'f@x', 'PYTHONIOENCODING': 'utf-8'})


def g(repo, *a):
    p = subprocess.run(['git', '-C', repo] + list(a), capture_output=True,
                       text=True, env=_git_env)
    return p.returncode, p.stdout + p.stderr


def build_repo(base):
    """合成仓库骨架 + 状态档(只喂顾问,不跑门;轮号经检查点块给)。"""
    repo = os.path.join(base, 'repo')
    sd = os.path.join(repo, 'docs', 'autonomous-rd')
    os.makedirs(sd)
    g(repo, 'init', '-b', 'main')
    open(os.path.join(sd, 'RESUME.md'), 'w', encoding='utf-8').write(
        '# RESUME fixture\n\n## 下一步(fixture)\n\n1. x\n')
    g(repo, 'add', '-A')
    g(repo, 'commit', '-m', 'C0 base')
    return repo, sd


def finalize(repo, sd, rnd, extra_write=None):
    """落一笔改动(extra_write 回调) + 替换检查点块 + 提交 = 一个 finalize 事件。"""
    if extra_write:
        extra_write(repo)
    rp = os.path.join(sd, 'RESUME.md')
    text = open(rp, encoding='utf-8').read()
    line = '<!-- RD-CHECKPOINT v1: json %s -->' % json.dumps(
        {'round': rnd, 'date': '2026-11-12 00:00 HKT', 'branch': 'main',
         'commit': '0' * 40, 'baseline': '0' * 40, 'goal_sha': '0' * 16,
         'completed_ids': ['T-R%d-1' % rnd], 'next_task': 'x',
         'next_round': rnd + 1}, ensure_ascii=False)
    text = re.sub(r'<!-- RD-CHECKPOINT v1: json \{.*?\} -->', line, text,
                  flags=re.S) if 'RD-CHECKPOINT v1' in text \
        else text.rstrip() + '\n\n' + line + '\n'
    open(rp, 'w', encoding='utf-8').write(text)
    g(repo, 'add', '-A')
    g(repo, 'commit', '-m', 'finalize R%d' % rnd)


def write(path, body):
    def fn(repo):
        os.makedirs(os.path.dirname(path(repo)) or repo, exist_ok=True)
        open(path(repo), 'w', encoding='utf-8').write(body)
    return fn


def sec_a():
    print('── A. 分类单元 ──')
    check('A1 docs-only 分类',
          watch.classify(['docs/a.md', 'README.md']) == 'docs-only')
    check('A2 tests-only 分类',
          watch.classify(['tests/t.py', 'docs/a.md']) == 'tests-only')
    check('A3 code 分类(脚本)',
          watch.classify(['scripts/x.py', 'docs/a.md']) == 'code')
    check('A4 code 分类(数据/产物面)',
          watch.classify(['data/daily/x.json']) == 'code')
    check('A5 code_files 排除 tests/docs',
          watch.code_files(['scripts/x.py', 'tests/t.py', 'docs/a.md',
                            'engine.py']) == {'scripts/x.py', 'engine.py'})


def sec_b():
    print('── B. 合成仓库: 漂移/返工预警 ──')
    base = tempfile.mkdtemp(prefix='rd_r21_b_')
    try:
        repo, sd = build_repo(base)
        r = lambda *p: os.path.join(repo, *p)
        # 5 个 finalize → 4 个区间(区间归属=后一 final 的轮):
        # R12 docs-only → R13 docs-only(连续两轮=漂移) → R14 code →
        # R15 code 改同一 scripts/x.py(返工)
        finalize(repo, sd, 11, write(lambda repo: r('docs', 'N0.md'), 'n'))
        finalize(repo, sd, 12, write(lambda repo: r('docs', 'N1.md'), 'n'))
        finalize(repo, sd, 13, write(lambda repo: r('docs', 'N2.md'), 'n'))
        finalize(repo, sd, 14, write(lambda repo: r('scripts', 'x.py'), 'x=1'))
        finalize(repo, sd, 15, write(lambda repo: r('scripts', 'x.py'), 'x=2'))
        res = watch.analyze(repo, os.path.join('docs', 'autonomous-rd'), 8)
        kinds = [(x['round'], x['kind']) for x in res['rounds']]
        check('B1 四区间分类齐全',
              kinds == [(12, 'docs-only'), (13, 'docs-only'),
                        (14, 'code'), (15, 'code')], kinds)
        drift = [w for w in res['warnings'] if '漂移预警' in w]
        rework = [w for w in res['warnings'] if '返工预警' in w]
        check('B2 连续两轮 docs-only → 漂移预警(§4.3 根因复审)',
              len(drift) == 1 and 'R12→R13' in drift[0], res['warnings'])
        check('B3 同一生产文件连续两轮 → 返工预警',
              len(rework) == 1 and 'R14→R15' in rework[0]
              and 'scripts/x.py' in rework[0], res['warnings'])
    finally:
        shutil.rmtree(base, ignore_errors=True)

    base = tempfile.mkdtemp(prefix='rd_r21_b2_')
    try:
        repo, sd = build_repo(base)
        r = lambda *p: os.path.join(repo, *p)
        finalize(repo, sd, 21, write(lambda repo: r('scripts', 'a.py'), 'a'))
        finalize(repo, sd, 22, write(lambda repo: r('scripts', 'b.py'), 'b'))
        res = watch.analyze(repo, os.path.join('docs', 'autonomous-rd'), 8)
        check('B4 干净历史零预警(不同文件两轮 code)',
              res['warnings'] == [] and res['rounds'][0]['kind'] == 'code',
              res.get('note'))
    finally:
        shutil.rmtree(base, ignore_errors=True)


def sec_c():
    print('── C. 降级面与退出码 ──')
    base = tempfile.mkdtemp(prefix='rd_r21_c_')
    try:
        repo, sd = build_repo(base)
        finalize(repo, sd, 31)
        res = watch.analyze(repo, os.path.join('docs', 'autonomous-rd'), 8)
        check('C1 单 finalize=观察窗不足,降级不预警',
              res['warnings'] == [] and '观察窗不足' in res.get('note', ''),
              res)
    finally:
        shutil.rmtree(base, ignore_errors=True)

    base = tempfile.mkdtemp(prefix='rd_r21_c2_')
    try:
        repo, sd = build_repo(base)
        r = lambda *p: os.path.join(repo, *p)
        finalize(repo, sd, 11, write(lambda repo: r('docs', 'N0.md'), 'n'))
        finalize(repo, sd, 12, write(lambda repo: r('docs', 'N1.md'), 'n'))
        finalize(repo, sd, 13, write(lambda repo: r('docs', 'N2.md'), 'n'))
        finalize(repo, sd, 14, write(lambda repo: r('scripts', 'x.py'), 'x=1'))
        finalize(repo, sd, 15, write(lambda repo: r('scripts', 'x.py'), 'x=2'))
        wp = os.path.join(SCRIPTS, 'rd_progress_watch.py')
        # 默认恒 exit 0(顾问非门)
        p0 = subprocess.run(
            [sys.executable, wp, '--repo', repo], capture_output=True,
            text=True, env=_git_env)
        check('C2 顾问恒 exit 0(预警≠失败,硬门在一致性门)',
              p0.returncode == 0 and '漂移预警' in p0.stdout, p0.returncode)
        # --strict 有预警 exit 3
        p3 = subprocess.run(
            [sys.executable, wp, '--repo', repo, '--strict'],
            capture_output=True, text=True, env=_git_env)
        check('C3 --strict 有预警 exit 3', p3.returncode == 3, p3.returncode)
        # --window 2 只看最近两区间(R14,R15): 漂移预警消失,返工仍在
        p2 = subprocess.run(
            [sys.executable, wp, '--repo', repo, '--window', '2', '--json'],
            capture_output=True, text=True, env=_git_env)
        j = json.loads(p2.stdout)
        check('C4 --window 截断(仅 R14,R15,漂移预警出窗)',
              [x['round'] for x in j['rounds']] == [14, 15]
              and not [w for w in j['warnings'] if '漂移' in w]
              and [w for w in j['warnings'] if '返工' in w], j['rounds'])
        check('C5 --json 机读可解析', isinstance(j.get('rounds'), list))
    finally:
        shutil.rmtree(base, ignore_errors=True)


def sec_d():
    print('── D. finalize 协议事故弧(R20 事故类回归锁) ──')
    sys.path.insert(0, HERE)
    t20 = load('t20_fixture',
               os.path.join(HERE, 'test_rd_r20_state_checkpoint.py'))
    base = tempfile.mkdtemp(prefix='rd_r21_d_')
    try:
        fx = t20.build_fixture(base, stamped=False)  # 波中态
        repo, sd = fx['repo'], fx['sd']
        ck = os.path.join(SCRIPTS, 'rd_checkpoint.py')
        env = _git_env
        # 1) finalize → 门绿
        p1 = subprocess.run(
            [sys.executable, ck, '--finalize', '--round', '1',
             '--next-round', '2', '--next-task', 'R2 x', '--completed-ids',
             'T-R1-1', '--repo', repo, '--quiet'],
            capture_output=True, text=True, env=env)
        check('D1 盖章后门绿', p1.returncode == 0, (p1.stdout + p1.stderr)[-300:])
        check('D1b 盖章后顾问随行播报(非阻塞)',
              '漂移顾问' in p1.stdout, p1.stdout[-200:])
        # 2) 盖章后再落代码提交(R20 事故形态) → ①基线红
        open(os.path.join(repo, 'engine2.py'), 'w').write('y=2\n')
        g(repo, 'add', '-A')
        g(repo, 'commit', '-m', 'code after finalize (incident shape)')
        gate = load('t21_gate', os.path.join(SCRIPTS,
                                             'rd_state_consistency.py'))
        rep = gate.Report()
        gate.run_checks(repo, sd, rep)
        f1 = rep.fails.get('①', [])
        check('D2 盖章后代码提交 → ①基线红(工作面容忍过期=事故被门拦截)',
              bool(f1) and any('不容忍' in m for m in f1), rep.fails)
        # 3) 重新盖章(幂等) → 门绿=对账自愈
        p3 = subprocess.run(
            [sys.executable, ck, '--finalize', '--round', '1',
             '--next-round', '2', '--next-task', 'R2 x', '--completed-ids',
             'T-R1-1', '--repo', repo, '--quiet'],
            capture_output=True, text=True, env=env)
        check('D3 重新盖章 → 门绿(finalize=分支最后一笔纪律的对账自愈)',
              p3.returncode == 0, (p3.stdout + p3.stderr)[-300:])
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main():
    print('═══ R21 防死循环+finalize 协议加固套件 ═══')
    for sec in (sec_a, sec_b, sec_c, sec_d):
        sec()
    total = 18  # A×5 + B×4 + C×5 + D×4(与本文件 check() 调用数一致)
    print('\n判定 %d/%d, FAIL=%d' % (total - len(FAILURES), total,
                                    len(FAILURES)))
    return 1 if FAILURES else 0


if __name__ == '__main__':
    sys.exit(main())
