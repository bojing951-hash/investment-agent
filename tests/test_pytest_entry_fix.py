#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R2 pytest 三入口回归(修复面: tests/conftest.py 收集钩子).

缺陷复现(修复前): `pytest tests/test_x.py` 单文件入口 rc=3
INTERNALERROR——pytest 8.x 的 pytest_collect_file 非 firstresult 且
python 插件对命令行直给 .py 绕过 python_files 匹配(isinitpath 分支)
→ 同一文件两个收集器(SuiteFile+Module), Module 收集期 import →
脚本套件模块级执行+尾部 sys.exit → INTERNALERROR, 通过/失败不可分。
`-k` 筛选与排除套件显式路径直入同根因面。

本套件两分支:
- pytest 在场(本地开发面+CI, offline-tests.yml 已装 pytest): 行为级
  验证——三入口 rc/收集数/无 INTERNALERROR/失败传播/排除契约;
- pytest 缺席(兜底面): 结构级验证——conftest.py 三钩子与判定单一
  事实源在场, 防修复静默消失。(CI 面套件真值=offline-tests.yml 的
  python3 直跑, 与适配器子进程面同构。)

E6 恰执行一次以**副作用计数器文件**为判据(临时套件经环境变量
ZZ_E6_COUNTER 追加计数, env 沿 E套件→pytest→ScriptSuiteItem 子进程
链继承): 双收集器=真双执行=计数 2, 与 pytest 对失败输出的渲染次数
无关(py3.11/3.12 或 CI 环境下 FAILURES 摘要可重复渲染同一行——
渲染次数≠执行次数, 旧判据误杀即此因, 2026-11-20 run 44670255565)。
"""
import glob
import importlib.util
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = 'tests/test_audit_r1_f02_gate.py'
PASS, FAIL = [], []


def check(name, cond, detail=''):
    (PASS if cond else FAIL).append(name)
    mark = '✅' if cond else '❌'
    print(f'  {mark} {name}' + (f' — {detail}' if detail and not cond else ''))


def pytest_available():
    return importlib.util.find_spec('pytest') is not None


def run_pytest(args):
    return subprocess.run(
        [sys.executable, '-m', 'pytest'] + args, cwd=REPO,
        capture_output=True, text=True, timeout=1800)


def behavioral():
    print('分支: pytest 在场(行为级)')
    out = lambda r: (r.stdout or '') + (r.stderr or '')

    # E1 单文件收集: 唯一收集器+不导入原文(修复前=INTERNALERROR rc=3)
    r = run_pytest([TARGET, '--collect-only', '-q'])
    o = out(r)
    check('E1 单文件收集 rc=0', r.returncode == 0, o[-300:])
    check('E1 收集恰 1 项', '1 test collected' in o, o[-300:])
    check('E1 无 INTERNALERROR', 'INTERNALERROR' not in o)
    check('E1 收集期未导入套件原文(无 F02 横幅)',
          'F02 独立审查四态门回归' not in o)

    # E2 单文件真跑: 恰一次执行(双收集器=双执行=2 passed, 修复前炸)
    r = run_pytest([TARGET, '-q'])
    o = out(r)
    check('E2 单文件真跑 rc=0', r.returncode == 0, o[-300:])
    check('E2 恰 1 passed(无双收集器双执行)', '1 passed' in o, o[-300:])

    # E3 -k 筛选: 选中恰 1 项, 其余 deselect
    r = run_pytest(['tests/', '-k', 'f02_gate', '--collect-only', '-q'])
    o = out(r)
    hits = [ln for ln in o.splitlines() if ln.endswith('::' + os.path.basename(TARGET))]
    check('E3 -k 筛选 rc=0 且选中恰 1 项', r.returncode == 0 and len(hits) == 1,
          o[-300:])
    check('E3 无 INTERNALERROR', 'INTERNALERROR' not in o)

    # E4 目录面: 收集数=磁盘 test_*.py 数-排除件, 无 INTERNALERROR
    r = run_pytest(['tests/', '--collect-only', '-q'])
    o = out(r)
    n_disk = len(glob.glob(os.path.join(REPO, 'tests', 'test_*.py'))) - 1  # -live
    m = None
    for ln in o.splitlines():
        if ln.strip().endswith('collected') or 'tests collected' in ln:
            try:
                m = int(ln.strip().split()[0])
            except (ValueError, IndexError):
                pass
    check('E4 目录收集数=磁盘套件数-排除件',
          r.returncode == 0 and m == n_disk, f'collected={m} disk={n_disk}')
    check('E4 排除件不在目录收集面', 'test_model_live.py::' not in o)

    # E5 排除契约: 显式路径直入=可见跳过, 不导入不执行不 INTERNALERROR
    r = run_pytest(['tests/test_model_live.py', '-q'])
    o = out(r)
    check('E5 排除件单文件 rc=0 且 1 skipped',
          r.returncode == 0 and '1 skipped' in o, o[-300:])
    check('E5 排除件未被导入执行',
          'RUN_MODEL_LIVE' not in o and 'INTERNALERROR' not in o)

    # E6 失败传播(临时套件, finally 清理): rc=1 非零真相上浮;
    # 恰执行一次=副作用计数器(env 传路径), 与渲染次数解耦(见模块 docstring)
    tmp = os.path.join(REPO, 'tests', 'test_zz_entryfix_fail_tmp.py')
    counter = os.path.join(
        tempfile.gettempdir(), f'zz_e6_counter_{os.getpid()}.txt')

    def _ran_count():
        if not os.path.exists(counter):
            return 0
        with open(counter, encoding='utf-8') as f:
            return f.read().count('RAN')

    def _summary(o):
        return next((l for l in o.splitlines() if 'failed' in l), '')[:80]

    try:
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(
                'import os, sys\n'
                'with open(os.environ["ZZ_E6_COUNTER"], "a",'
                ' encoding="utf-8") as f:\n'
                '    f.write("RAN\\n")\n'
                'print("ZZ-ENTRYFIX-FAIL-RAN")\n'
                'sys.exit(7)\n')
        os.environ['ZZ_E6_COUNTER'] = counter
        if os.path.exists(counter):
            os.remove(counter)
        r = run_pytest(['tests/test_zz_entryfix_fail_tmp.py', '-q'])
        o = out(r)
        n = _ran_count()
        check('E6 单文件失败 rc=1', r.returncode == 1, o[-300:])
        check('E6 退出码 7 上浮', '套件退出码 7' in o)
        check('E6 恰执行一次', n == 1,
              f'执行次数={n}(计数器副作用) 汇总行: {_summary(o)}')
        if os.path.exists(counter):
            os.remove(counter)
        r = run_pytest(['tests/', '-k', 'zz_entryfix_fail_tmp', '-q'])
        o = out(r)
        n = _ran_count()
        check('E6 -k 筛选下失败 rc=1', r.returncode == 1, o[-300:])
        check('E6 -k 筛选下恰执行一次', n == 1,
              f'执行次数={n}(计数器副作用) 汇总行: {_summary(o)}')
    finally:
        os.environ.pop('ZZ_E6_COUNTER', None)
        for p in (tmp, counter):
            if os.path.exists(p):
                os.remove(p)


def structural():
    print('分支: pytest 缺席(CI 直跑面, 结构级; 行为级入口=NOT_APPLICABLE)')
    conf = open(os.path.join(REPO, 'tests', 'conftest.py'),
                encoding='utf-8').read()
    ini = open(os.path.join(REPO, 'pytest.ini'), encoding='utf-8').read()
    check('S1 makemodule 拦截面在场',
          'def pytest_pycollect_makemodule' in conf)
    check('S2 初始路径让位防双收集器', 'isinitpath' in conf)
    check('S3 排除契约三钩子齐(ignore+替身+判定)',
          'def pytest_ignore_collect' in conf
          and 'class ExcludedFile' in conf and '_is_script_suite' in conf)
    check('S4 哨兵模式停用默认收集', '*_pytest_native.py' in ini)
    print('  (CI 面套件真值=offline-tests.yml python3 直跑; pytest 入口'
          '须本地 pytest 在场验证——见本套件 behavioral 分支)')


print('════════ Audit-R2 pytest 三入口回归 ════════')
if pytest_available():
    behavioral()
else:
    structural()
print(f'\n判定: {len(PASS)} PASS / {len(FAIL)} FAIL')
if FAIL:
    print('失败项:', ', '.join(FAIL))
sys.exit(0 if not FAIL else 1)
