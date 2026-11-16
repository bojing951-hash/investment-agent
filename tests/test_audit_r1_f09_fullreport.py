# -*- coding: utf-8 -*-
"""Audit-R1 F09 守卫: FULL_REPORT 完整装配 + 单命令全自动链(--stage auto)。

可移植性纪律(同 pc3): CI 净树无本地快照——plan/auto 的 run_ok=False 是
诚实降级,守卫锁结构面与诚实暂停/截链面,不伪造绿;真实面(本机 /tmp 在场
的已落位 run)只做在场性检查,缺席=如实 SKIP 不冒充。
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

PASSED, FAILED = [], []


def check(name, cond, detail=''):
    (PASSED if cond else FAILED).append((name, detail))
    print(('  ✅ ' if cond else '❌ ') + name + (f' [{detail}]' if not cond and detail else ''))


def _cli(argv, timeout=300):
    return subprocess.run([sys.executable, 'ia_cli.py'] + argv,
                          cwd=ROOT, capture_output=True, text=True, timeout=timeout)


class TestAFullAssembly(unittest.TestCase):
    """§A report 段=完整装配: L1/L2/L3/L4/证据索引/四态全节+未落位如实。"""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix='f09_guard_')
        r = _cli(['research-one', '--stage', 'plan', '--question',
                  'SPX 与 VIX 的风险开关结构', '--out-dir', cls.tmp])
        cls.rd = json.loads(r.stdout)['data']['report_dir']
        rr = _cli(['research-one', '--stage', 'report', '--report-dir', cls.rd])
        cls.rc, cls.out = rr.returncode, json.loads(rr.stdout)

    def test_a1_sections(self):
        md = open(os.path.join(self.rd, 'FULL_REPORT.md'), encoding='utf-8').read()
        for sec in ('## L1 事实层', '## L2 机构观点层', '## L3 AI 推断层(Agent 席真产·全文内联)',
                    '## L4 条件情景层(Agent 席真产·全文内联)', '## 证据索引',
                    # Audit-R2 后节题扩为「四态+绑定面」;Audit-R4 再扩
                    # 「+Audit-R4 贯通面」(run 门分级/record_health/
                    # FULL_REPORT 副本核验并入)——断言随装配面更新
                    '## 质量状态(Audit-R1 F02 四态+Audit-R2 绑定面'
                    '+Audit-R4 贯通面)'):
            check(f'§A1 节在场: {sec}', sec in md)
        check('§A1 未落位如实(净树 L3/L4 无判断→不冒充)',
              '(未落位' in md)
        check('§A1 四态行齐(generated/machine_verified/review/deliverable)',
              all(k in md for k in ('generated:', 'machine_verified:',
                                    'review:', 'deliverable(可交付):')))
        check('§A1 未落位→ok=false+warnings',
              self.rc == 1 and self.out['ok'] is False
              and any('L3/L4' in w for w in (self.out.get('warnings') or [])))


class TestBAutoChain(unittest.TestCase):
    """§B auto 段: 单命令全自动链+Agent Native 暂停点+诚实截链。"""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix='f09_auto_')
        r = _cli(['research-one', '--stage', 'auto', '--question',
                  'SPX 与 VIX 的风险开关结构', '--out-dir', cls.tmp])
        cls.pause = json.loads(r.stdout)
        cls.pause_rc = r.returncode
        cls.rd = cls.pause['data']['chain'][0]['report_dir']

    def test_b1_pause_point(self):
        d = self.pause['data']
        chain = d.get('chain') or []
        check('§B1 judgment 缺席→停 plan 段(ok=false,rc=1)',
              self.pause_rc == 1 and self.pause['ok'] is False)
        check('§B1 链含 plan 段', chain and chain[0].get('stage') == 'plan')
        check('§B1 暂停点段(Agent Native,不代写)',
              any(c.get('stage') == 'pause' and '暂停点' in str(c.get('note'))
                  for c in chain))
        check('§B1 next 指令面(携 judgment 续链)', 'judgment' in str(d.get('next')))

    def test_b2_attach_failure_cuts_chain(self):
        # 无效 judgment 文件→attach 段诚实截链(净树=失败底座拒收/校验拒收)
        bad = os.path.join(self.tmp, 'bad_judgment.json')
        json.dump({'l3': {}, 'l4': {}}, open(bad, 'w', encoding='utf-8'))
        r = _cli(['research-one', '--stage', 'auto', '--question',
                  'SPX 与 VIX 的风险开关结构', '--out-dir', self.tmp,
                  '--judgment', bad])
        out = json.loads(r.stdout)
        chain = out['data'].get('chain') or []
        att = [c for c in chain if c.get('stage') == 'attach']
        check('§B2 无效 judgment→attached=false(诚实截链,rc=1)',
              r.returncode == 1 and att and att[0].get('ok') is False)
        check('§B2 截链后不进 report 段',
              not any(c.get('stage') == 'report' for c in chain))


class TestCRealFace(unittest.TestCase):
    """§C 真实面(本机已落位 run 在场时): L3/L4 全文内联+修订标记入正文。"""

    def test_c1_inlined_when_present(self):
        rd = '/tmp/phase4_blind/20261116T053623Z_GOLD_F_黄金与美国长期实际利率_REAL_10Y_及美元指数_DXY_的传'
        if not os.path.exists(os.path.join(rd, 'report.json')):
            check('§C 真实面缺席=如实 SKIP(净树/异机不冒充)', True)
            return
        _cli(['research-one', '--stage', 'report', '--report-dir', rd])
        md = open(os.path.join(rd, 'FULL_REPORT.md'), encoding='utf-8').read()
        check('§C CON 全文内联(### CON- 在场)', '### CON-' in md)
        check('§C 机制链全文内联(### 机制链 在场)', '### 机制链' in md)
        check('§C 情景全文内联(### SCN- 在场)', '### SCN-' in md)
        check('§C 证伪/触发五行面内联(证伪: 指标= 在场)', '证伪: 指标=' in md)
        check('§C 证据索引表行数>0', md.count('| ') > 10)


def main():
    print('════════════════════════════════════════════════════════════════')
    print('Audit-R1 F09 守卫: FULL_REPORT 完整装配 + --stage auto 全自动链')
    print('════════════════════════════════════════════════════════════════')
    errs = 0
    for cls in (TestAFullAssembly, TestBAutoChain, TestCRealFace):
        from io import StringIO
        buf = sys.stderr
        sys.stderr = StringIO()
        try:
            suite = unittest.TestLoader().loadTestsFromTestCase(cls)
            res = unittest.TextTestRunner(stream=StringIO()).run(suite)
            errs += len(res.failures) + len(res.errors)
        finally:
            sys.stderr = buf
    print()
    if FAILED:
        print('失败项:')
        for n, d in FAILED:
            print('  -', n, d)
    print('════════════════════════════════════════════════════════════════')
    print(f'F09 判定: {len(PASSED)} PASS / {len(FAILED)} FAIL')
    sys.exit(0 if (not FAILED and not errs) else 1)


if __name__ == '__main__':
    main()
