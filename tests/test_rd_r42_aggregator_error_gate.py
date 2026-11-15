# -*- coding: utf-8 -*-
"""R42 聚合器吞错修复守卫套件(RDG-20261116-012;操作者紧凑波 T-R42-1)。

漏洞: t1t2/t3/t4/r27 四套件的 main() 以 unittest.main(exit=False) 逐类跑,
退出码只由 check() 台账决定——测试方法在到达任何 check() 前抛异常(测级
errors/failures)不进台账 → exit 0 → CI/批跑全绿。实证: main@2798d8a(R40,
CI 43734958311 绿)上 t1t2 test_fail_closed 与 t4 test_d1_schema_mutations
已各带 1 条被吞 ERROR(T1 注册表落盘 96d265e 起 HY_OAS 扩三线→find 多匹配
返 None→TypeError;TH 契约漂移→裸 KeyError),潜伏多轮未被发现——直到
R41 收口用 pytest 口径独立验才暴露。

本套件四节:
  A 模式行为证伪: 同构聚合器夹带一条 erroring 测 → 子进程必须 exit≠0
    (对照: 无异常版 exit 0——证明计数非无条件红);
  B 四文件源面守卫: _run_case/case_errs 在场、exit=False 绝迹(防回退);
  C 两历史潜伏测复活直验: 修复后逐测 0 error 0 failure;
  D TH fail-closed 契约: 缺键→RuntimeError(带键名),不再裸 KeyError。
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

PASSED, FAILED = [], []


def check(name, cond, detail=''):
    (PASSED if cond else FAILED).append((name, detail))
    print(('  ✅ ' if cond else '  ❌ ') + name + (f' [{detail}]' if not cond and detail else ''))


def _run_case(cls):
    """与四套件同构的聚合器(本套件自身亦受其保护)。"""
    from io import StringIO
    suite = unittest.TestLoader().loadTestsFromTestCase(cls)
    res = unittest.TextTestRunner(stream=StringIO(), verbosity=0).run(suite)
    n = len(res.errors) + len(res.failures)
    print(f'   unittest: {res.testsRun} tests, {n} error/failure' if n
          else f'   unittest: {res.testsRun} tests OK')
    return n


FIXTURE_TEMPLATE = '''# -*- coding: utf-8 -*-
import sys
import unittest

PASSED, FAILED = [], []


def check(name, cond, detail=''):
    (PASSED if cond else FAILED).append((name, detail))


def _run_case(cls):
    from io import StringIO
    suite = unittest.TestLoader().loadTestsFromTestCase(cls)
    res = unittest.TextTestRunner(stream=StringIO(), verbosity=0).run(suite)
    return len(res.errors) + len(res.failures)


class TOk(unittest.TestCase):
    def test_ok(self):
        check('ok 判定', True)


__EXTRA_CLS__


def main():
    case_errs = 0
    for cls in (__CLS_TUPLE__,):
        case_errs += _run_case(cls)
    if FAILED or case_errs:
        print('AGG-RED case_errs=%d ledger=%d' % (case_errs, len(FAILED)))
        sys.exit(1)
    print('AGG-GREEN')
    sys.exit(0)


if __name__ == '__main__':
    main()
'''


def _build_fixture(extra_cls, cls_tuple):
    """模板以 __EXTRA_CLS__/__CLS_TUPLE__ 记号拼装(避 .format 与字面
    大括号相撞——§A 首版即因此自伤)。"""
    return (FIXTURE_TEMPLATE
            .replace('__EXTRA_CLS__', extra_cls)
            .replace('__CLS_TUPLE__', cls_tuple))

ERR_CLS = '''
class TBoom(unittest.TestCase):
    def test_boom(self):
        raise KeyError('no.such.key')
'''

GUARD_FILES = [
    'tests/test_arch_reform_t1t2.py',
    'tests/test_arch_reform_t3_series.py',
    'tests/test_arch_reform_t4_claims.py',
    'tests/test_rd_r27_gateb_extractor.py',
]


class TestAPatternBehavior(unittest.TestCase):
    """§A 同构聚合器行为证伪(子进程,真退出码)。"""

    def test_erroring_test_fails_exit(self):
        with tempfile.TemporaryDirectory() as td:
            fp = os.path.join(td, 'agg_fixture.py')
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(_build_fixture(ERR_CLS, 'TOk, TBoom'))
            r = subprocess.run([sys.executable, fp], capture_output=True,
                               text=True, cwd=td, timeout=60)
            check('§A erroring 测→exit≠0(吞错漏洞已封)',
                  r.returncode != 0 and 'case_errs=1' in r.stdout,
                  f'rc={r.returncode} out={r.stdout[-120:]}')

    def test_clean_fixture_passes(self):
        with tempfile.TemporaryDirectory() as td:
            fp = os.path.join(td, 'agg_fixture.py')
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(_build_fixture('', 'TOk'))
            r = subprocess.run([sys.executable, fp], capture_output=True,
                               text=True, cwd=td, timeout=60)
            check('§A 无异常同构夹具→exit 0(计数非无条件红)',
                  r.returncode == 0 and 'AGG-GREEN' in r.stdout,
                  f'rc={r.returncode}')


class TestBSourceGuard(unittest.TestCase):
    """§B 四套件源面守卫: 修复形态在场,旧漏洞形态绝迹。"""

    def test_four_files_guarded(self):
        for rel in GUARD_FILES:
            src = open(os.path.join(ROOT, rel), encoding='utf-8').read()
            check(f'§B {rel.split("/")[-1]}: _run_case+case_errs 在场',
                  '_run_case(' in src and 'case_errs' in src)
            # 守卫锚=脆弱调用形态 'unittest.main(argv'(helper 文档串提及
            # exit=False 属说明文字,不算回退)
            check(f'§B {rel.split("/")[-1]}: unittest.main(argv 调用形态绝迹(防回退)',
                  'unittest.main(argv' not in src)


class TestCRevivedTests(unittest.TestCase):
    """§C 两历史潜伏测复活直验(修复后必须 0 error 0 failure)。"""

    def test_two_latent_tests_alive(self):
        sys.path.insert(0, os.path.join(ROOT, 'tests'))
        import test_arch_reform_t1t2 as m12   # noqa: E402
        import test_arch_reform_t4_claims as m4   # noqa: E402
        from io import StringIO
        loader = unittest.TestLoader()
        runner = unittest.TextTestRunner(stream=StringIO(), verbosity=0)
        r1 = runner.run(loader.loadTestsFromName(
            'TestS2ScorecardEquivalence.test_fail_closed', m12))
        r2 = runner.run(loader.loadTestsFromName(
            'TestD1DeterminismSchema.test_d1_schema_mutations', m4))
        check('§C t1t2 test_fail_closed 复活(0 err 0 fail)',
              len(r1.errors) == 0 and len(r1.failures) == 0,
              f'err={len(r1.errors)} fail={len(r1.failures)}')
        check('§C t4 test_d1_schema_mutations 复活(0 err 0 fail)',
              len(r2.errors) == 0 and len(r2.failures) == 0,
              f'err={len(r2.errors)} fail={len(r2.failures)}')


class TestDTHContract(unittest.TestCase):
    """§D TH fail-closed 契约(R42 兑现)。"""

    def test_th_missing_key_runtimeerror(self):
        import macro_scorecard as ms
        try:
            ms.TH('no.such.key')
            check('§D TH 缺键→RuntimeError', False, '未抛异常')
        except RuntimeError as e:
            check('§D TH 缺键→RuntimeError(带键名)', 'no.such.key' in str(e))
        except KeyError:
            check('§D TH 缺键→RuntimeError', False, '裸 KeyError 回潮')
        try:
            ms.TH('nonexistent.key.2')
            check('§D TH 缺键(第二条)→RuntimeError', False, '未抛异常')
        except RuntimeError:
            check('§D TH 缺键(第二条)→RuntimeError', True)
        check('§D TH 合法键不受影响', ms.TH('hy_oas.warning') == 4.0,
              str(ms.TH('hy_oas.warning')))


def main():
    print('══ R42 聚合器吞错修复守卫套件(RDG-20261116-012)══')
    case_errs = 0
    for cls in (TestAPatternBehavior, TestBSourceGuard, TestCRevivedTests,
                TestDTHContract):
        print(f'── {cls.__name__} ──')
        case_errs += _run_case(cls)
    total, bad = len(PASSED) + len(FAILED), len(FAILED)
    print(f"\n{'='*60}\nR42 守卫: {len(PASSED)} PASS / {len(FAILED)} FAIL + {case_errs} 测级异常 (共{total}判定)")
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
