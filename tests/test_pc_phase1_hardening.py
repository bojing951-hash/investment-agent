# -*- coding: utf-8 -*-
"""Product Convergence Phase 1 工程硬约束守卫(G0 落地面)。"""
import os
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

PASSED, FAILED = [], []


def check(name, cond, detail=''):
    (PASSED if cond else FAILED).append((name, detail))
    print(('  ✅ ' if cond else '  ❌ ') + name + (f' [{detail}]' if not cond and detail else ''))


def _rc(cmd):
    return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=300)


class TestAAssets(unittest.TestCase):
    """§A Phase 1 资产在场+可执行。"""

    def test_assets(self):
        for rel in ('scripts/target_integrity_guard.py', 'tests/test_target_integrity.py',
                    'docs/autonomous-rd/TARGET_INTEGRITY_REGISTRY.json',
                    'docs/autonomous-rd/TARGET_PROTECTION_PREP.md',
                    'scripts/product_acceptance_runner.py',
                    'scripts/complexity_baseline.py',
                    'docs/autonomous-rd/COMPLEXITY_BASELINE.md',
                    'docs/autonomous-rd/REGRESSION_CATALOG.md',
                    'docs/autonomous-rd/CODEBASE_SIMPLIFICATION_BACKLOG.md'):
            check(f'§A {os.path.basename(rel)} 在场', os.path.exists(os.path.join(ROOT, rel)))
        r = _rc('python3 scripts/product_acceptance_runner.py --help')
        check('§A 验收 runner --help rc=0', r.returncode == 0, r.stderr[-120:])


class TestBGates(unittest.TestCase):
    """§B 门行为: 完整性绿+复杂度基线内。"""

    def test_gates(self):
        r = _rc('python3 scripts/target_integrity_guard.py --check')
        check('§B 目标完整性 --check 绿', r.returncode == 0, r.stdout[-150:])
        r2 = _rc('python3 scripts/complexity_baseline.py --check')
        check('§B 复杂度基线内(--check)', r2.returncode == 0, r2.stdout[-150:])


class TestCBacklogDiscipline(unittest.TestCase):
    """§C 简化纪律: backlog 只登记 DEFERRED(禁执行痕迹)。"""

    def test_backlog_deferred_only(self):
        src = open(os.path.join(ROOT, 'docs/autonomous-rd',
                                'CODEBASE_SIMPLIFICATION_BACKLOG.md'), encoding='utf-8').read()
        check('§C backlog 全条目 DEFERRED',
              src.count('| DEFERRED') >= 5 and 'IN-PROGRESS' not in src and 'DONE' not in src)


def main():
    print('══ Product Convergence Phase 1 守卫 ══')
    errs = 0
    for cls in (TestAAssets, TestBGates, TestCBacklogDiscipline):
        from io import StringIO
        print(f'── {cls.__name__} ──')
        res = unittest.TextTestRunner(stream=StringIO(), verbosity=0).run(
            unittest.TestLoader().loadTestsFromTestCase(cls))
        n = len(res.errors) + len(res.failures)
        print(f'   unittest: {res.testsRun} tests, {n} error/failure' if n
              else f'   unittest: {res.testsRun} tests OK')
        errs += n
    print(f"\n{'='*56}\nPhase 1 守卫: {len(PASSED)} PASS / {len(FAILED)} FAIL + {errs} 测级异常")
    if FAILED or errs:
        for n, d in FAILED:
            print(f'  ❌ {n} [{d}]')
        sys.exit(1)
    print('全部通过 ✅')
    sys.exit(0)


if __name__ == '__main__':
    main()
