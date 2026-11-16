# -*- coding: utf-8 -*-
"""目标完整性守卫套件(Product Convergence Phase 1 / G0)。

守护形态: ①真校验跑 guard --check(未登记变更→红) ②行为证伪(临时篡改被保护件
副本语境→check 必红;复原→绿) ③注册表/保护清单同步守卫(清单文件集=注册表键集)
④guard 源面自守卫(GUARDED 四件+--reason 必填逻辑在场,防守卫被掏空)。
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


def _guard(*extra):
    return subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'target_integrity_guard.py')]
                          + list(extra), capture_output=True, text=True, timeout=60)


class TestAGuardGreen(unittest.TestCase):
    """§A 基线: 当前树目标/验收契约与登记一致。"""

    def test_check_green(self):
        r = _guard('--check')
        check('§A guard --check 绿(基线一致)', r.returncode == 0, r.stdout[-200:])


class TestBTamperProof(unittest.TestCase):
    """§B 行为证伪: 未登记变更必红,复原即绿(临时副本内做,不动真件)。"""

    def test_tamper_detected(self):
        target = os.path.join(ROOT, 'docs', 'autonomous-rd', 'ACCEPTANCE_CRITERIA.md')
        backup = target + '.guardtest_bak'
        os.replace(target, backup)
        try:
            with open(target, 'w', encoding='utf-8') as f:
                f.write(open(backup, encoding='utf-8').read() + '\n<!-- 篡改探针 -->\n')
            r = _guard('--check')
            check('§B 未登记变更→--check 红', r.returncode != 0 and '已变更' in r.stdout,
                  f'rc={r.returncode}')
        finally:
            if os.path.exists(target):
                os.remove(target)
            os.replace(backup, target)
        r2 = _guard('--check')
        check('§B 复原→绿(探针无残留)', r2.returncode == 0, r2.stdout[-200:])


class TestCRegistrySync(unittest.TestCase):
    """§C 注册表与保护清单同步+四件全登记。"""

    def test_registry_covers_guarded(self):
        import json
        reg = json.load(open(os.path.join(ROOT, 'docs', 'autonomous-rd',
                                          'TARGET_INTEGRITY_REGISTRY.json'), encoding='utf-8'))
        guarded = ['docs/autonomous-rd/PRODUCT_GOAL.md', 'docs/autonomous-rd/FINAL_ACCEPTANCE.md',
                   'docs/autonomous-rd/ACCEPTANCE_CRITERIA.md',
                   'docs/autonomous-rd/CHARTER_PRODUCT_CONVERGENCE.md']
        for g in guarded:
            check(f'§C {g.split("/")[-1]} 已登记', g in reg and 'sha256' in reg[g])
        extra = [k for k in reg if k not in guarded and not k.startswith('_')]
        check('§C 注册表无未保护孤儿键', extra == [], str(extra))


class TestDSourceGuard(unittest.TestCase):
    """§D 守卫源面自守卫: 保护清单四件+理由必填逻辑在场,防掏空。"""

    def test_guard_not_gutted(self):
        src = open(os.path.join(ROOT, 'scripts', 'target_integrity_guard.py'), encoding='utf-8').read()
        check('§D 保护清单含 PRODUCT_GOAL', "'docs/autonomous-rd/PRODUCT_GOAL.md'" in src)
        check('§D 保护清单含 FINAL_ACCEPTANCE', "'docs/autonomous-rd/FINAL_ACCEPTANCE.md'" in src)
        check('§D 保护清单含 ACCEPTANCE_CRITERIA', "'docs/autonomous-rd/ACCEPTANCE_CRITERIA.md'" in src)
        check('§D 保护清单含 CHARTER_PRODUCT_CONVERGENCE',
              "'docs/autonomous-rd/CHARTER_PRODUCT_CONVERGENCE.md'" in src)
        check('§D --update 拒绝空理由', 'refuse: --reason 必填' in src)


def main():
    print('══ Product Convergence 目标完整性守卫(Phase 1 / G0)══')
    case_errs = 0
    for cls in (TestAGuardGreen, TestBTamperProof, TestCRegistrySync, TestDSourceGuard):
        print(f'── {cls.__name__} ──')
        case_errs += _run_case(cls)
    total = len(PASSED) + len(FAILED)
    print(f"\n{'='*60}\n目标完整性守卫: {len(PASSED)} PASS / {len(FAILED)} FAIL + {case_errs} 测级异常 (共{total}判定)")
    if FAILED or case_errs:
        for n, d in FAILED:
            print(f'  ❌ {n} [{d}]')
        if case_errs:
            print(f'  ❌ 测级异常×{case_errs}')
        sys.exit(1)
    print('全部通过 ✅')
    sys.exit(0)


if __name__ == '__main__':
    main()
