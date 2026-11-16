# -*- coding: utf-8 -*-
"""R43 pytest 口径四件套收口守卫(RDG-20261116-012 残余⑦;操作者紧凑波)。

病灶: e2e_frozen14/e2e_orig14/p01_fix1/p01_fix2 四件=模块级线性脚本
(整件逻辑 import 时跑),其内 `run_weekly.main()` 裸调→argparse 读真
sys.argv——直跑(argv[1:]=[] 全可选参数)过;pytest 收集时
argv[1:]=[文件,-q]→unrecognized→SystemExit(2) 被捕 code=2→台账
未落→`ledger['steps']` NoneType 下标崩=collection error。潜伏陈年
(a457453 同在),R42 双口径终验才现形。

修: run_weekly.main(argv=None)+parse_args(argv)(None=CLI 原行为零差;
revision_chain 的 sys.argv 猴补路由不受影响)+五调用点显式 argv=[]。

本套件三节:
  A 伪 pytest 口径子进程复现: 以 pytest 形态 argv 导入四件模块→rc==0
    (修前此形态必崩=NoneType;不依赖 pytest 安装,CI 安全);
  B 源面守卫: 四件裸调形态绝迹+run_weekly argv 参数化在场(防回退);
  C 直跑口径(CI 口径)保持: 四件 `python3 tests/x.py` rc==0。
"""
import os
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

PASSED, FAILED = [], []


def check(name, cond, detail=''):
    (PASSED if cond else FAILED).append((name, detail))
    print(('  ✅ ' if cond else '  ❌ ') + name + (f' [{detail}]' if not cond and detail else ''))


def _run_case(cls):
    from io import StringIO
    suite = unittest.TestLoader().loadTestsFromTestCase(cls)
    res = unittest.TextTestRunner(stream=StringIO(), verbosity=0).run(suite)
    n = len(res.errors) + len(res.failures)
    print(f'   unittest: {res.testsRun} tests, {n} error/failure' if n
          else f'   unittest: {res.testsRun} tests OK')
    return n


CALIBER_FILES = [
    'test_e2e_frozen14.py',
    'test_e2e_orig14.py',
    'test_p01_fix1.py',
    'test_p01_fix2.py',
]

# 与真实 pytest 收集时等价的导入形态: 外来 argv + 模块全量执行。
# (真 pytest 下 sys.argv=['pytest','-q','tests/x.py'] 顺序不一,取同族
# 形态即可——argparse 只关心 argv[1:] 里有位置参数)
SIM_IMPORT = (
    "import sys; sys.argv=['pytest','tests/%(f)s','-q'];"
    " sys.path.insert(0,'tests'); import %(m)s"
)


class TestAFakePytestCaliber(unittest.TestCase):
    """§A 伪 pytest 口径: 外来 argv 形态下导入四件模块,子进程真退出码。"""

    def test_four_modules_import_clean_under_foreign_argv(self):
        for fn in CALIBER_FILES:
            mod = fn[:-3]
            code = SIM_IMPORT % {'f': fn, 'm': mod}
            r = subprocess.run([sys.executable, '-c', code], capture_output=True,
                               text=True, cwd=ROOT, timeout=600)
            check(f'§A {fn} 伪 pytest argv 导入 rc=0(修前 NoneType 崩)',
                  r.returncode == 0, f'rc={r.returncode} {r.stderr[-120:]}')


class TestBSourceGuard(unittest.TestCase):
    """§B 源面守卫: 修复形态在场,裸调形态绝迹。"""

    def test_bare_calls_extinct(self):
        for fn in CALIBER_FILES:
            src = open(os.path.join(ROOT, 'tests', fn), encoding='utf-8').read()
            check(f'§B {fn}: 裸调 run_weekly.main() 形态绝迹',
                  '\nrun_weekly.main()\n' not in src
                  and ' run_weekly.main()\n' not in src.replace('run_weekly.main(argv=[])', ''))
            check(f'§B {fn}: 显式 argv=[] 调用在场',
                  'run_weekly.main(argv=[])' in src)
            # 尾行条件退出形态防回退: 0 支冗余摘除后 pytest 收集不再被打断
            check(f'§B {fn}: sys.exit(1 if FAIL else 0) 形态绝迹(红支保留)',
                  'sys.exit(1 if FAIL else 0)' not in src
                  and 'if FAIL:\n    sys.exit(1)' in src)

    def test_run_weekly_parameterized(self):
        src = open(os.path.join(ROOT, 'run_weekly.py'), encoding='utf-8').read()
        check('§B run_weekly: def main(argv=None) 在场',
              'def main(argv=None):' in src)
        check('§B run_weekly: parse_args(argv) 在场(不再裸读 sys.argv)',
              'ap.parse_args(argv)' in src)
        # 兼容面: revision_chain 的 sys.argv 猴补路由依赖 argv=None→sys.argv
        rc_src = open(os.path.join(ROOT, 'tests', 'test_revision_chain.py'),
                      encoding='utf-8').read()
        check('§B 兼容: revision_chain sys.argv 猴补路由面未改',
              "sys.argv = ['run_weekly.py']" in rc_src)


class TestDRound6X6Argv(unittest.TestCase):
    """§D R44 追修: test_round6 X6 三处 rw.main() 裸调→argv=[](R43 同族,
    R43 修复面漏件——其时净验脚本 pytest 口径 rc 取自管道尾(tail)=空洞绿,
    167 件真分类后唯一真红即此件;口径空洞与追修均如实入档 R44 行)。"""

    def test_round6_import_clean_under_foreign_argv(self):
        code = SIM_IMPORT % {'f': 'test_round6.py', 'm': 'test_round6'}
        r = subprocess.run([sys.executable, '-c', code], capture_output=True,
                           text=True, cwd=ROOT, timeout=600)
        check('§D test_round6 伪 pytest argv 导入 rc=0(X6 修前三败)',
              r.returncode == 0, f'rc={r.returncode} {r.stderr[-120:]}')

    def test_round6_source_forms(self):
        src = open(os.path.join(ROOT, 'tests', 'test_round6.py'),
                   encoding='utf-8').read()
        check('§D test_round6: 裸调 rw.main() 形态绝迹',
              'rw.main()\n' not in src and ' rw.main() ' not in src)
        check('§D test_round6: 显式 rw.main(argv=[]) 三处在场',
              src.count('rw.main(argv=[])') == 3, str(src.count('rw.main(argv=[])')))


class TestCDirectCaliber(unittest.TestCase):
    """§C 直跑口径(CI 口径=python3 tests/x.py)保持绿。"""

    def test_four_files_direct_run(self):
        for fn in CALIBER_FILES:
            r = subprocess.run([sys.executable, os.path.join(ROOT, 'tests', fn)],
                               capture_output=True, text=True, timeout=600)
            check(f'§C {fn} 直跑 rc=0(CI 口径保持)',
                  r.returncode == 0, f'rc={r.returncode}')


def main():
    print('══ R43 pytest 口径四件套收口守卫(RDG-20261116-012 残余⑦)══')
    case_errs = 0
    for cls in (TestAFakePytestCaliber, TestBSourceGuard, TestCDirectCaliber, TestDRound6X6Argv):
        print(f'── {cls.__name__} ──')
        case_errs += _run_case(cls)
    total, bad = len(PASSED) + len(FAILED), len(FAILED)
    print(f"\n{'='*60}\nR43 守卫: {len(PASSED)} PASS / {len(FAILED)} FAIL + {case_errs} 测级异常 (共{total}判定)")
    if FAILED or case_errs:
        for n, d in FAILED:
            print(f'  ❌ {n} [{d}]')
        if case_errs:
            print(f'  ❌ 测级异常×{case_errs}(unittest errors/failures,见上方逐类行)')
        sys.exit(1)
    print('全部通过 ✅')
    sys.exit(0)


if __name__ == '__main__':
    main()
