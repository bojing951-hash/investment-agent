# -*- coding: utf-8 -*-
"""Product Convergence Phase 3 守卫: 一键研究 MVP 单入口三段式。

可移植性纪律: CI 净树无本地快照(untracked 数据)——plan 段 run_ok=False
是**诚实降级**(no_snapshot 如实报错),守卫不伪造绿:
- §B attach 在失败底座上必须走 MINOR-4 拒收(blocked=run_ok_false),
  或(数据在场的本机)对无效 judgment 给 violations 拒收——两分支都是
  attached=False+诚实理由,任何「无效输入却 attached=True」=红。
- 真链全绿(run_ok=True+L3/L4 produced=True)的验收证据在
  PRODUCT_CONVERGENCE_PHASE3_PROGRESS.md(mvp_run4 实证,真实数据注入缝),
  本守卫只锁结构面与诚实降级面。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

PASSED, FAILED = [], []


def check(name, cond, detail=''):
    (PASSED if cond else FAILED).append((name, detail))
    print(('  ✅ ' if cond else '  ❌ ') + name + (f' [{detail}]' if not cond and detail else ''))


def _cli(argv, timeout=240):
    return subprocess.run([sys.executable, 'ia_cli.py'] + argv,
                          cwd=ROOT, capture_output=True, text=True, timeout=timeout)


class TestAEntrySurface(unittest.TestCase):
    """§A 三段式入口与参数面在档。"""

    def test_help(self):
        r = _cli(['research-one', '--help'])
        check('§A research-one --help rc=0', r.returncode == 0, r.stderr[-100:])
        for token in ('plan', 'attach', 'report', '--engine-root', '--judgment'):
            check(f'§A 参数面含 {token}', token in r.stdout)


class TestBHonestChain(unittest.TestCase):
    """§B 净树面三段式: 结构工件齐+无效输入永不半落位。"""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix='pc3_guard_')
        cls.q = 'SPX 与 VIX 的风险开关结构: 相关性与年内位置'
        r = _cli(['research-one', '--stage', 'plan', '--question', cls.q,
                  '--out-dir', cls.tmp])
        cls.plan = json.loads(r.stdout)
        cls.rd = cls.plan['data']['report_dir']

    def test_b1_plan_artifacts(self):
        d = self.plan['data']
        check('§B1 plan emit 结构(ok/run_ok 键在场)',
              isinstance(d.get('run_ok'), bool) and 'report_dir' in d)
        for f in ('report.json', 'evidence_index.json', 'views_digest.json',
                  'AGENT_SEAT_ENVELOPE.json'):
            check(f'§B1 工件 {f} 在场', os.path.exists(os.path.join(self.rd, f)))
        ev = json.load(open(os.path.join(self.rd, 'evidence_index.json'),
                            encoding='utf-8'))
        check('§B1 evidence_index 为 list', isinstance(ev, list))
        vd = json.load(open(os.path.join(self.rd, 'views_digest.json'),
                            encoding='utf-8'))
        check('§B1 views_digest note 如实(在场/缺席二态)',
              isinstance(vd.get('note'), str) and
              (vd['note'].startswith('views 库在场')
               or vd['note'].startswith('views 库不可读')))

    def test_b2_envelope_shape(self):
        env = json.load(open(os.path.join(self.rd, 'AGENT_SEAT_ENVELOPE.json'),
                             encoding='utf-8'))
        check('§B2 工单 role/read_first/produce/then/discipline 五键',
              all(k in env for k in ('role', 'read_first', 'produce',
                                     'then', 'discipline')))
        check('§B2 纪律红线含禁 produced 造假',
              any('produced' in s for s in env['discipline']))
        abs_paths = [p.split('#')[0].strip() for p in env['read_first']
                     if p.startswith('/')]
        check('§B2 read_first 绝对路径全存在',
              all(os.path.exists(p) for p in abs_paths), str(abs_paths))

    def test_b3_attach_never_half_lands(self):
        bad = os.path.join(self.tmp, 'bad_judgment.json')
        json.dump({'schema_version': 'bogus'}, open(bad, 'w', encoding='utf-8'))
        r = _cli(['research-one', '--stage', 'attach',
                  '--report-dir', self.rd, '--judgment', bad])
        d = json.loads(r.stdout)['data']
        check('§B3 无效输入 attached=False', d.get('attached') is False)
        honest = (d.get('blocked') == 'run_ok_false') or \
                 (d.get('validation_passed') is False and d.get('violations'))
        check('§B3 拒收理由诚实(MINOR-4 拦|violations 在档)', honest,
              json.dumps(d, ensure_ascii=False)[:120])

    def test_b4_report_stage_renders(self):
        r = _cli(['research-one', '--stage', 'report', '--report-dir', self.rd])
        env = json.loads(r.stdout)
        d = env['data']
        fp = d.get('full_report')
        check('§B4 FULL_REPORT.md 生成', fp and os.path.exists(fp))
        txt = open(fp, encoding='utf-8').read()
        check('§B4 问题行非空', '- 问题: ' in txt and 'None' not in
              txt.split('- 问题: ')[1].split('\n')[0])
        check('§B4 L1 事实表头', '## L1 事实层' in txt)
        rj = json.load(open(os.path.join(self.rd, 'report.json'),
                            encoding='utf-8'))
        l3 = rj['layers']['L3_AI推断层']['produced']
        check('§B4 ok 与 produced 同步(不冒认)',
              env['ok'] == bool(l3 and rj['layers']['L4_条件情景层']['produced']))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)


def main():
    print('══ Product Convergence Phase 3 守卫 ══')
    errs = 0
    for cls in (TestAEntrySurface, TestBHonestChain):
        from io import StringIO
        print(f'── {cls.__name__} ──')
        res = unittest.TextTestRunner(stream=StringIO(), verbosity=0).run(
            unittest.TestLoader().loadTestsFromTestCase(cls))
        n = len(res.errors) + len(res.failures)
        print(f'   unittest: {res.testsRun} tests, {n} error/failure' if n
              else f'   unittest: {res.testsRun} tests OK')
        errs += n
    print(f"\n{'='*56}\nPhase 3 守卫: {len(PASSED)} PASS / {len(FAILED)} FAIL + {errs} 测级异常")
    if FAILED or errs:
        for n, d in FAILED:
            print(f'  ❌ {n} [{d}]')
        sys.exit(1)
    print('全部通过 ✅')
    sys.exit(0)


if __name__ == '__main__':
    main()
