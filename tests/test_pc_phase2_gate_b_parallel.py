# -*- coding: utf-8 -*-
"""Phase 2 守卫: 并行迁移框架判据防漂+首测工件在档。"""
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

PASSED, FAILED = [], []


def check(name, cond, detail=''):
    (PASSED if cond else FAILED).append((name, detail))
    print(('  ✅ ' if cond else '  ❌ ') + name + (f' [{detail}]' if not cond and detail else ''))


class TestAMigrationCriteriaFixed(unittest.TestCase):
    """§A 判据先固定后测量: MC1-MC4 文本锚防漂(改判据=须过目标完整性理由线)。"""

    def test_criteria_anchored(self):
        src = open(os.path.join(ROOT, 'scripts', 'gate_b_parallel_harness.py'),
                   encoding='utf-8').read()
        check('§A MC1 真错零容忍锚',
              "'MC1': '新面 CONTRA 全簇裁定真错=0(裁定档在档,本件计数对照)'" in src)
        check('§A MC2 裁定基锚(裸计数不可比如实注记)',
              "'MC2': '裁定基对比" in src and '裸计数不可比' in src)
        check('§A MC3 连续期锚', "'MC3': '连续 ≥2 期真实周报满足 MC1+MC2'" in src)
        check('§A MC4 独立席锚', "'MC4': '独立席复核 MC1 裁定档记录在场'" in src)
        check('§A 只测量不迁移红线', '达标才迁' in src and '不提前替换' in src)

    def test_harness_runnable(self):
        r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts',
                           'gate_b_parallel_harness.py'), '--help'],
                           capture_output=True, text=True, timeout=60)
        check('§A harness --help rc=0', r.returncode == 0, r.stderr[-100:])


class TestBFirstMeasurementArtifact(unittest.TestCase):
    """§B 三报首测工件在档+结构可核。"""

    def test_artifact(self):
        p = os.path.join(ROOT, 'audit', 'gate_b_parallel', 'parallel_result.json')
        check('§B parallel_result.json 在档', os.path.exists(p))
        if os.path.exists(p):
            d = json.load(open(p, encoding='utf-8'))
            check('§B 三报对照', len(d.get('comparison', [])) == 3, str(len(d.get('comparison', []))))
            check('§B 判据入档', set(d.get('migration_criteria', {})) == {'MC1', 'MC2', 'MC3', 'MC4'})
            check('§B 快照溯源在场', all('snapshot_used' in r for r in d['comparison']))
            check('§B MC2 待评位(裁定基,不冒称过)', all(
                r.get('adjudicated_pass') == 'PENDING(须裁定档,MC1 同源)'
                for r in d.get('MC2_per_report', [])))


class TestCAuditR1F08InputParity(unittest.TestCase):
    """§C Audit-R1 F08 输入对齐: 旧面锚点支持每报告一 vintage,不再循环外一次性提取。"""

    def test_f08_faces(self):
        src = open(os.path.join(ROOT, 'scripts', 'gate_b_parallel_harness.py'),
                   encoding='utf-8').read()
        check('§C --anchors-data 参在场', "'--anchors-data'" in src)
        check('§C 每报告锚点注入(extract_anchors_from_data(data_dir))',
              'extract_anchors_from_data(anchor_dirs[i])' in src)
        check('§C 行内 anchors_used 溯源', "'anchors_used': anchors_src" in src)
        check('§C 缺省单一 vintage 如实注记(输入错代披露)',
              'single_live_vintage' in src and '输入错代' in src)
        check('§C 数量校验(1 或 1:1)', '须与报告数' in src)
        r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts',
                           'gate_b_parallel_harness.py'), '--help'],
                           capture_output=True, text=True, timeout=60)
        check('§C harness --help rc=0', r.returncode == 0, r.stderr[-100:])


class TestDAuditR2InputFaces(unittest.TestCase):
    """§D Audit-R2 条目8: 同源比较输入三件套(版本/哈希/日期)+单位基随行。"""

    def test_d_source_anchors(self):
        src = open(os.path.join(ROOT, 'scripts', 'gate_b_parallel_harness.py'),
                   encoding='utf-8').read()
        check('§D 输入三件套函数(_input_face: sha256+bytes+id/as_of)',
              "def _input_face(path, *, kind)" in src and "'input_id': ident" in src)
        check('§D 快照面随行', "'snapshot_face': _input_face(snap_path, kind='snapshot')" in src)
        check('§D 锚点面哈希(序列化锚点字典)',
              "'anchors_sha256':" in src)
        check('§D 单位基随行(registry sha256)', "'units_basis': registry_face" in src)
        check('§D 同源判据注记(全同才同源)',
              '全同才称同源' in src)
        check('§D 迁移保持 pending(裁定前不迁)',
              'PENDING(须裁定档' in src)

    def test_d_input_face_functional(self):
        import tempfile
        sys.path.insert(0, os.path.join(ROOT, 'scripts'))
        import gate_b_parallel_harness as gb
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False,
                                         encoding='utf-8') as f:
            json.dump({'snapshot_id': 'snap_test_v1', 'research_as_of': '2026-11-12',
                       'series_store': {}}, f)
            p = f.name
        try:
            face = gb._input_face(p, kind='snapshot')
            import hashlib
            expect = hashlib.sha256(open(p, 'rb').read()).hexdigest()
            check('§D _input_face 哈希与文件一致', face['sha256'] == expect)
            check('§D _input_face 版本/日期自述',
                  face['input_id'] == 'snap_test_v1' and face['as_of'] == '2026-11-12',
                  str(face))
            check('§D _input_face 字节数在场', face['bytes'] > 0)
        finally:
            os.unlink(p)
        reg = gb._registry_face()
        check('§D _registry_face sha256 在场(单位基可考)',
              reg.get('sha256') not in (None, ''), str(reg.get('sha256'))[:12])


def main():
    print('══ Product Convergence Phase 2 守卫 ══')
    errs = 0
    for cls in (TestAMigrationCriteriaFixed, TestBFirstMeasurementArtifact,
                    TestCAuditR1F08InputParity, TestDAuditR2InputFaces):
        from io import StringIO
        print(f'── {cls.__name__} ──')
        res = unittest.TextTestRunner(stream=StringIO(), verbosity=0).run(
            unittest.TestLoader().loadTestsFromTestCase(cls))
        n = len(res.errors) + len(res.failures)
        print(f'   unittest: {res.testsRun} tests, {n} error/failure' if n
              else f'   unittest: {res.testsRun} tests OK')
        errs += n
    print(f"\n{'='*56}\nPhase 2 守卫: {len(PASSED)} PASS / {len(FAILED)} FAIL + {errs} 测级异常")
    if FAILED or errs:
        for n, d in FAILED:
            print(f'  ❌ {n} [{d}]')
        sys.exit(1)
    print('全部通过 ✅')
    sys.exit(0)


if __name__ == '__main__':
    main()
