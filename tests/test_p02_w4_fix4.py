# -*- coding: utf-8 -*-
"""IA-P0-2-W4-FIX4 专项测试(两项确定性缺陷: 输入根symlink授权保护+文件提取
失败状态传播)。

任务: IA-P0-2-W4-FIX4-DEV-v1.0 §六 | 基线: FIX3最终失败Commit 45db462
全部用例真实调用被审计工具的main()/run_audit()/discover_files()/extract_file()
与正式报告函数——不复制被测算法、不预拼JSON结果。

A组8: 输入根路径授权(真实目录成功/输入根symlink默认拒绝/daily外指拒绝/
     文件级symlink跳过/相似前缀/跨平台临时目录/越权目标零读取+canary/
     拒绝后无成功审计)。
B组11: 提取执行状态(正常成功/JSON解析失败SKIPPED/数字data/非空列表data
     (§5.3固定反例)/非法字符串data/合法空data/一文件全失败/两文件部分失败/
     两文件全失败/单文件中途异常原子性/已注册单指标Schema仍正常记录)。
C组8: 正式报告(readable与extract_status独立/failed_files完整/状态-退出码
     一致/Manifest保留失败文件/81项不虚增/SHA-256可追溯/Markdown披露/
     JSON与日志一致)。
D组10: 历史合同继承(FIX3 Schema溯源/FIX3近期历史/FIX2槽位不变量/FIX2完整
     input_files/FIX1连续段/FIX1重复拆分/MARGIN_BAL/五通道/commit与UTC/
     输入只读)。
E组4: 负向敏感性退化注入(恢复realpath自动授权根symlink/恢复readable唯一
     成功判定(全失败仍COMPLETED)/删除提取错误传播/部分失败仍COMPLETED)。
"""
import glob
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import historical_coverage_audit as hca   # 被审计的真实审计器(FIX4版)

REGISTRY = os.path.join(ROOT, 'config', 'metric_registry.json')
N_METRICS = 81


# ════════════════ 公共工具(真实main()/真实文件系统) ════════════════

def _load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def _write(daily, name, payload):
    with open(os.path.join(daily, name), 'w', encoding='utf-8') as f:
        f.write(payload if isinstance(payload, str)
                else json.dumps(payload, ensure_ascii=False))


def _run_main(data_dir, out, extra=()):
    buf = io.StringIO()
    stdout, sys.stdout = sys.stdout, buf
    try:
        ec = hca.main(['--data-dir', data_dir, '--out-dir', out,
                       '--registry', REGISTRY] + list(extra))
    finally:
        sys.stdout = stdout
    return ec, buf.getvalue()


def _run(files, tag='fix4', source_note='FIX4合成fixture'):
    """建临时data/daily写入{文件名:内容},跑真实main();返回(ec,result,out,tmp)。"""
    tmp = tempfile.mkdtemp(prefix='w4fix4_%s_' % tag)
    daily = os.path.join(tmp, 'data', 'daily')
    os.makedirs(daily)
    for name, payload in files.items():
        _write(daily, name, payload)
    out = os.path.join(tmp, 'out')
    ec = hca.main(['--data-dir', os.path.join(tmp, 'data'), '--out-dir', out,
                   '--registry', REGISTRY, '--source-note', source_note])
    hits = glob.glob(os.path.join(out, 'coverage_audit_*.json'))
    result = _load(hits[0]) if hits else None
    if result is not None:
        # 报告JSON不含manifest键(体积);逐文件条目在input_manifest_*.json
        mfs = glob.glob(os.path.join(out, 'input_manifest_*.json'))
        result['_manifest_files'] = (_load(mfs[0])['files'] if mfs else [])
    return ec, result, out, tmp


def by_id(result, mid):
    return next(r for r in result['metrics'] if r['metric_id'] == mid)


def manifest_of(result, relpath):
    return next(e for e in result['_manifest_files'] if e['relpath'] == relpath)


# ════════════════ fixture(与真实采集Schema同构的合成数据) ════════════════

G_OK = {"date": "2026-10-20", "data": {"SPX": {"close": 5700.0,
                                               "date": "2026-10-16"}}}
G_LIST = {"date": "2026-10-20", "data": ["SPX"]}                       # §5.3固定反例
G_STR = {"date": "2026-10-20", "data": "invalid"}
G_EMPTY_STR = {"date": "2026-10-20", "data": ""}
G_FALSE = {"date": "2026-10-20", "data": False}
G_EMPTY = {"date": "2026-10-20", "data": {}}                          # §5.7合法空
G_NUM = {"date": "2026-10-20", "data": 12345}
G_SCHEMA = {"date": "2026-10-20", "data": {"SPX": "not_an_object",
                                            "GOLD": 12345}}
M_LIST = {"date": "2026-10-20", "data": ["CPI"]}
M_MIDWAY = {"date": "2026-10-20",
            "data": {"CPI": {"date": "2026-10-20", "value": 3.0}},
            "derived": "oops"}     # data合法处理后才失败=中途异常(§5.6)
BAD_JSON = '{"date": "2026-10-20", "data": {'


# ════════════════ A组: 输入根路径授权(FIX4-01) ════════════════

class TestARootAuthorization(unittest.TestCase):

    def _mk(self, prefix):
        t = tempfile.mkdtemp(prefix=prefix)
        self.addCleanup(shutil.rmtree, t, ignore_errors=True)
        return t

    # A1: 真实目录(非symlink)正常完成——授权后直接传真实路径不误拒(§4.3)
    def test_a1_real_dir_completes(self):
        t = self._mk('w4fix4_a1_')
        daily = os.path.join(t, 'data', 'daily')
        os.makedirs(daily)
        _write(daily, 'global_20261020.json', G_OK)
        out = os.path.join(t, 'out')
        ec, _ = _run_main(os.path.join(t, 'data'), out)
        self.assertEqual(ec, 0)
        res = _load(glob.glob(os.path.join(out, 'coverage_audit_*.json'))[0])
        self.assertEqual(res['audit_status'], 'COMPLETED')
        self.assertEqual(by_id(res, 'SPX')['status'], 'SINGLE_OBSERVATION')

    # A2: 输入根本身为symlink→默认拒绝(exit2/INVALID_PATH/零输出/提示真实目录)
    def test_a2_input_root_symlink_rejected(self):
        t = self._mk('w4fix4_a2_')
        real = os.path.join(t, 'real_data')
        os.makedirs(os.path.join(real, 'daily'))
        _write(os.path.join(real, 'daily'), 'global_20261020.json', G_OK)
        alias = os.path.join(t, 'alias')
        os.symlink(real, alias)
        self.assertTrue(os.path.islink(alias))      # 前提: 显式symlink入口
        out = os.path.join(t, 'out')
        ec, printed = _run_main(alias, out)
        self.assertEqual(ec, 2)
        self.assertFalse(os.path.exists(out))
        self.assertEqual(glob.glob(os.path.join(t, '**', 'coverage_audit_*'),
                                   recursive=True), [])
        self.assertIn('输入数据根为符号链接', printed)
        self.assertIn('目标目录授权未经确认', printed)
        self.assertIn(os.path.realpath(alias), printed)   # 披露目标,供人工确认

    # A3: daily/子目录外指symlink→整体拒绝(FIX3-02语义在FIX4下不回退)
    def test_a3_daily_symlink_rejected(self):
        t = self._mk('w4fix4_a3_')
        data = os.path.join(t, 'data')
        os.makedirs(data)
        outside = os.path.join(t, 'outside')
        os.makedirs(outside)
        _write(outside, 'global_20261020.json', G_OK)
        os.symlink(outside, os.path.join(data, 'daily'))
        ec, printed = _run_main(data, os.path.join(t, 'out'))
        self.assertEqual(ec, 2)
        self.assertIn('路径边界拒绝', printed)

    # A4: 文件级symlink→跳过并披露,同目录真实文件正常计入
    def test_a4_file_symlink_skipped(self):
        t = self._mk('w4fix4_a4_')
        daily = os.path.join(t, 'data', 'daily')
        os.makedirs(daily)
        _write(daily, 'china_20261020.json',
               {"date": "2026-10-20",
                "a_share_indices": {"000001.SH": {"close": 3300.0,
                                                  "date": "2026-10-16"}}})
        os.symlink('/etc/hostname', os.path.join(daily, 'global_20261020.json'))
        out = os.path.join(t, 'out')
        ec, _ = _run_main(os.path.join(t, 'data'), out)
        self.assertEqual(ec, 0)
        res = _load(glob.glob(os.path.join(out, 'coverage_audit_*.json'))[0])
        self.assertEqual(res['input']['excluded']['symlink_skipped'],
                         ['daily/global_20261020.json'])
        self.assertEqual(by_id(res, 'SHCOMP')['status'], 'SINGLE_OBSERVATION')

    # A5: 相似前缀兄弟目录(commonpath语义,不因startswith误放行)
    def test_a5_prefix_sibling_rejected(self):
        t = self._mk('w4fix4_a5_')
        data = os.path.join(t, 'allowed', 'data')
        os.makedirs(data)
        evil = os.path.join(t, 'allowed_evil')
        os.makedirs(evil)
        _write(evil, 'global_20261020.json', G_OK)
        os.symlink(evil, os.path.join(data, 'daily'))
        with self.assertRaises(hca.PathBoundaryError):
            hca.discover_files(data)
        ec, _ = _run_main(data, os.path.join(t, 'out'))
        self.assertEqual(ec, 2)

    # A6: 跨平台临时目录——不依赖OS路径别名(如macOS /tmp→/private/tmp,
    # Linux /tmp为真实目录);测试沙箱基础路径无论是否symlink祖先,输入根
    # 本身非symlink即正常执行(FIX3 CI run#1a教训的确定性版本)
    def test_a6_cross_platform_tmpdir(self):
        t = self._mk('w4fix4_a6_')            # 真实目录(两OS下均非末组件symlink)
        daily = os.path.join(t, 'data', 'daily')
        os.makedirs(daily)
        _write(daily, 'global_20261020.json', G_OK)
        out = os.path.join(t, 'out')
        ec, _ = _run_main(os.path.join(t, 'data'), out)
        self.assertEqual(ec, 0)
        res = _load(glob.glob(os.path.join(out, 'coverage_audit_*.json'))[0])
        self.assertEqual(res['audit_status'], 'COMPLETED')
        # discover_files单元级: 真实根不触发FIX4-01(祖先别名不影响末组件判定)
        files, base, excluded, by_ch = hca.discover_files(os.path.join(t, 'data'))
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['channel'], 'global')

    # A7: §4.4固定负向——test/alias→real-data/(含canary正文):
    # 传alias→拒绝/不读real-data正文/不COMPLETED/不写输入与目标目录/退出码非零
    def test_a7_alias_target_not_read_canary(self):
        t = self._mk('w4fix4_a7_')
        real = os.path.join(t, 'real-data')
        os.makedirs(os.path.join(real, 'daily'))
        canary = 'FIX4_CANARY_a71f_未经授权目标不得读取'
        _write(os.path.join(real, 'daily'), 'global_20261020.json',
               {"date": "2026-10-20", "data": {"SPX": {"close": 1.0,
                                                      "date": "2026-10-16",
                                                      "note": canary}}})
        alias = os.path.join(t, 'alias')
        os.symlink(real, alias)
        out = os.path.join(t, 'out')
        ec, printed = _run_main(alias, out)
        self.assertNotEqual(ec, 0)
        self.assertIn('INVALID_PATH', printed)
        self.assertFalse(os.path.exists(out))                 # 不写目标目录
        # canary扫描: 整棵临时树中唯一含canary的文件=越界源文件本身
        leaks = set()
        for p in glob.glob(os.path.join(t, '**', '*'), recursive=True):
            if os.path.isfile(p) and not os.path.islink(p):
                try:
                    with open(p, encoding='utf-8', errors='ignore') as f:
                        if canary in f.read():
                            leaks.add(os.path.realpath(p))
                except OSError:
                    pass
        self.assertEqual(sorted(leaks),
                         [os.path.realpath(os.path.join(real, 'daily',
                                                        'global_20261020.json'))])
        # 输入侧零改动(拒绝前后SHA一致)
        src = os.path.join(real, 'daily', 'global_20261020.json')
        with open(src, 'rb') as f:
            h = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(ec, 2)
        with open(src, 'rb') as f:
            self.assertEqual(hashlib.sha256(f.read()).hexdigest(), h)

    # A8: 路径拒绝后无成功审计——全树无任何coverage/manifest/log产出
    def test_a8_no_successful_audit_after_rejection(self):
        t = self._mk('w4fix4_a8_')
        real = os.path.join(t, 'real_data')
        os.makedirs(os.path.join(real, 'daily'))
        _write(os.path.join(real, 'daily'), 'global_20261020.json', G_OK)
        alias = os.path.join(t, 'alias')
        os.symlink(real, alias)
        _run_main(alias, os.path.join(t, 'out'))
        for pat in ('coverage_audit_*', 'input_manifest_*', 'audit_execution_*'):
            self.assertEqual(glob.glob(os.path.join(t, '**', pat),
                                       recursive=True), [],
                             '拒绝路径下不得存在产出: %s' % pat)


# ════════════════ B组: 提取执行状态(FIX4-02) ════════════════

class TestBExtractionStatus(unittest.TestCase):

    # B1: 正常JSON正常提取——COMPLETED/exit0/manifest extract_status=SUCCESS
    def test_b1_normal_extract_success(self):
        ec, res, out, tmp = _run({'global_20261020.json': G_OK}, 'b1')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(ec, 0)
        self.assertEqual(res['audit_status'], 'COMPLETED')
        self.assertEqual(res['extraction']['files_extracted'], 1)
        self.assertEqual(res['extraction']['files_failed'], 0)
        self.assertEqual(manifest_of(res, 'daily/global_20261020.json')
                         ['extract_status'], 'SUCCESS')
        self.assertEqual(by_id(res, 'SPX')['status'], 'SINGLE_OBSERVATION')

    # B2: JSON解析失败→readable=False+extract_status=SKIPPED(从未尝试),
    # ALL_UNREADABLE退出2,失败报告仍写(ALL_UNREADABLE本就在写报告集合)
    def test_b2_json_parse_failure_skipped(self):
        ec, res, out, tmp = _run({'global_20261020.json': BAD_JSON}, 'b2')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(ec, 2)
        self.assertEqual(res['audit_status'], 'ALL_UNREADABLE')
        me = manifest_of(res, 'daily/global_20261020.json')
        self.assertFalse(me['readable'])
        self.assertEqual(me['extract_status'], 'SKIPPED')
        self.assertIn('error', me)
        self.assertEqual(sorted(os.listdir(out)),
                         ['audit_execution_%s.log' % res['run_id'],
                          'coverage_audit_%s.json' % res['run_id'],
                          'coverage_audit_%s.md' % res['run_id'],
                          'input_manifest_%s.json' % res['run_id']])

    # B3: 合法JSON但data为数字→提取失败(EXTRACTION_FAILED)
    def test_b3_data_number_fails(self):
        ec, res, out, tmp = _run({'global_20261020.json': G_NUM}, 'b3')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(ec, 2)
        self.assertEqual(res['audit_status'], 'EXTRACTION_FAILED')
        me = manifest_of(res, 'daily/global_20261020.json')
        self.assertTrue(me['readable'])
        self.assertEqual(me['extract_status'], 'FAILED')
        self.assertIn('data字段非对象', me['extract_error'])

    # B4: §5.3固定反例 data=["SPX"]——readable=True/FAILED/≠COMPLETED/
    # exit≠0/extract_error+SHA+失败原因+执行日志齐备
    def test_b4_nonempty_list_data_fixed_counterexample(self):
        ec, res, out, tmp = _run({'global_20261020.json': G_LIST}, 'b4')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertNotEqual(ec, 0)
        self.assertNotEqual(res['audit_status'], 'COMPLETED')
        self.assertEqual(res['audit_status'], 'EXTRACTION_FAILED')
        self.assertEqual(res['exit_code'], ec)
        me = manifest_of(res, 'daily/global_20261020.json')
        self.assertTrue(me['readable'])                    # JSON可解析≠提取成功
        self.assertEqual(me['extract_status'], 'FAILED')
        self.assertTrue(me['extract_error'])
        ff = res['extraction']['failed_files']
        self.assertEqual(len(ff), 1)
        self.assertEqual(ff[0]['relpath'], 'daily/global_20261020.json')
        self.assertEqual(ff[0]['sha256'], me['sha256'])    # 可复核输入指纹
        with open(os.path.join(out, 'audit_execution_%s.log' % res['run_id']),
                  encoding='utf-8') as f:
            log = f.read()
        self.assertIn('提取失败', log)
        self.assertIn('global_20261020.json', log)

    # B5: 非法字符串data("invalid"/""/False)——falsy垃圾不得当合法空对象
    def test_b5_invalid_string_data_fails(self):
        for tag, payload in (('str', G_STR), ('empty_str', G_EMPTY_STR),
                             ('false', G_FALSE)):
            with self.subTest(case=tag):
                ec, res, out, tmp = _run({'global_20261020.json': payload},
                                         'b5_' + tag)
                self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
                self.assertEqual(ec, 2)
                self.assertEqual(res['audit_status'], 'EXTRACTION_FAILED')
                me = manifest_of(res, 'daily/global_20261020.json')
                self.assertTrue(me['readable'])
                self.assertEqual(me['extract_status'], 'FAILED')

    # B6: 合法空data={}——成功提取零观测(§5.7),COMPLETED/exit0
    def test_b6_legal_empty_data_success(self):
        ec, res, out, tmp = _run({'global_20261020.json': G_EMPTY}, 'b6')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(ec, 0)
        self.assertEqual(res['audit_status'], 'COMPLETED')
        self.assertEqual(res['extraction']['files_extracted'], 1)
        self.assertEqual(res['extraction']['files_failed'], 0)
        self.assertEqual(by_id(res, 'SPX')['status'], 'MISSING')

    # B7: 一文件全失败→EXTRACTION_FAILED(macro通道)
    def test_b7_single_file_all_fail(self):
        ec, res, out, tmp = _run({'macro_20261020.json': M_LIST}, 'b7')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(ec, 2)
        self.assertEqual(res['audit_status'], 'EXTRACTION_FAILED')
        self.assertEqual(res['extraction']['files_extracted'], 0)
        self.assertEqual(res['extraction']['files_failed'], 1)
        self.assertEqual(res['extraction']['failed_files'][0]['relpath'],
                         'daily/macro_20261020.json')

    # B8: 两文件部分失败→PARTIAL_EXTRACTION/exit≠0;成功文件数据不丢失,
    # 失败文件不出现在任何指标input_files(文件级原子性)
    def test_b8_partial_two_files(self):
        ec, res, out, tmp = _run({'global_20261020.json': G_OK,
                                  'macro_20261020.json': M_MIDWAY}, 'b8')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertNotEqual(ec, 0)
        self.assertEqual(res['audit_status'], 'PARTIAL_EXTRACTION')
        self.assertEqual(res['extraction']['files_extracted'], 1)
        self.assertEqual(res['extraction']['files_failed'], 1)
        spx = by_id(res, 'SPX')
        self.assertEqual(spx['status'], 'SINGLE_OBSERVATION')   # 正常global不丢失
        spx_files = [f['relpath'] for f in spx.get('input_files', [])]
        self.assertIn('daily/global_20261020.json', spx_files)
        for m in res['metrics']:       # 失败macro不出现在任何指标溯源
            for f in m.get('input_files', []):
                self.assertNotEqual(f['relpath'], 'daily/macro_20261020.json')

    # B9: 两文件全失败→EXTRACTION_FAILED,零指标获得观测
    def test_b9_two_files_all_fail(self):
        ec, res, out, tmp = _run({'global_20261020.json': G_LIST,
                                  'macro_20261020.json': M_LIST}, 'b9')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(ec, 2)
        self.assertEqual(res['audit_status'], 'EXTRACTION_FAILED')
        self.assertEqual(res['extraction']['files_failed'], 2)
        self.assertEqual({f['relpath'] for f in res['extraction']['failed_files']},
                         {'daily/global_20261020.json', 'daily/macro_20261020.json'})
        with_auth = [m for m in res['metrics']
                     if m['status'] in ('OBSERVED', 'SPARSE', 'SINGLE_OBSERVATION')]
        self.assertEqual(with_auth, [])

    # B10: 单文件处理中途异常(§5.6)——data先合法处理,derived再失败:
    # 该文件全部部分结果(CPI观测)必须丢弃,不作为已认证覆盖数据
    def test_b10_midfile_exception_atomicity(self):
        ec, res, out, tmp = _run({'macro_20261020.json': M_MIDWAY}, 'b10')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(ec, 2)
        self.assertEqual(res['audit_status'], 'EXTRACTION_FAILED')
        me = manifest_of(res, 'daily/macro_20261020.json')
        self.assertEqual(me['extract_status'], 'FAILED')
        cpi = by_id(res, 'CPI')
        self.assertEqual(cpi['status'], 'MISSING')     # 中途已提取的CPI被丢弃
        self.assertEqual(cpi.get('input_files', []), [])
        self.assertEqual(cpi['coverage']['total_unique_observations'], 0)

    # B11: 已注册指标单条Schema异常仍是文件内事件,不影响文件提取成功
    # (FIX3-01语义在FIX4下不回退: schema事件≠提取失败)
    def test_b11_registered_schema_event_still_success(self):
        ec, res, out, tmp = _run({'global_20261020.json': G_SCHEMA}, 'b11')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(ec, 0)
        self.assertEqual(res['audit_status'], 'COMPLETED')
        self.assertEqual(res['extraction']['files_failed'], 0)
        me = manifest_of(res, 'daily/global_20261020.json')
        self.assertEqual(me['extract_status'], 'SUCCESS')
        spx = by_id(res, 'SPX')
        self.assertEqual(spx['status'], 'MISSING')
        fe = next(f for f in spx['input_files']
                  if f['relpath'] == 'daily/global_20261020.json')
        self.assertIn('record_schema:not_object', fe['invalid_reasons'])
        self.assertFalse(fe['valid_observation_contributed'])
        self.assertEqual(len(fe['manifest_sha256']), 64)   # Manifest关联保留


# ════════════════ C组: 正式报告与退出码(FIX4-02 5.8) ════════════════

class TestCReports(unittest.TestCase):

    # C1: readable与extract_status独立——同一次审计中两种组合并存:
    # readable=True+FAILED(列表data)与readable=False+SKIPPED(坏JSON)
    def test_c1_readable_vs_extract_status_independent(self):
        ec, res, out, tmp = _run({'global_20261020.json': G_LIST,
                                  'china_20261020.json': BAD_JSON}, 'c1')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(ec, 2)
        me_g = manifest_of(res, 'daily/global_20261020.json')
        me_c = manifest_of(res, 'daily/china_20261020.json')
        self.assertTrue(me_g['readable'])
        self.assertEqual(me_g['extract_status'], 'FAILED')
        self.assertFalse(me_c['readable'])
        self.assertEqual(me_c['extract_status'], 'SKIPPED')
        # 提取失败≠不可读: extraction只统计可读文件(2 attempted之一FAILED)
        self.assertEqual(res['extraction']['files_attempted'], 1)
        self.assertEqual(res['extraction']['files_failed'], 1)

    # C2: extraction_failed_files完整(逐文件relpath/channel/sha256/原因)
    def test_c2_failed_files_complete(self):
        ec, res, out, tmp = _run({'global_20261020.json': G_LIST,
                                  'macro_20261020.json': M_LIST}, 'c2')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        ff = res['extraction']['failed_files']
        self.assertEqual(len(ff), 2)
        for e in ff:
            self.assertIn(e['relpath'], ('daily/global_20261020.json',
                                         'daily/macro_20261020.json'))
            self.assertTrue(e['sha256'])            # 40+位输入指纹可复核
            self.assertEqual(len(e['sha256']), 64)
            self.assertTrue(e['extract_error'])
            self.assertTrue(e['channel'])

    # C3: audit_status与退出码一致(六状态映射;NO_INPUT/INVALID_PATH同查)
    def test_c3_status_exit_consistency(self):
        cases = []
        # COMPLETED/0
        ec, res, out, tmp = _run({'global_20261020.json': G_OK}, 'c3a')
        cases.append((res['audit_status'], ec, 'COMPLETED', 0))
        shutil.rmtree(tmp, ignore_errors=True)
        # PARTIAL_EXTRACTION/2
        ec, res, out, tmp = _run({'global_20261020.json': G_OK,
                                  'macro_20261020.json': M_LIST}, 'c3b')
        cases.append((res['audit_status'], ec, 'PARTIAL_EXTRACTION', 2))
        shutil.rmtree(tmp, ignore_errors=True)
        # EXTRACTION_FAILED/2
        ec, res, out, tmp = _run({'global_20261020.json': G_LIST}, 'c3c')
        cases.append((res['audit_status'], ec, 'EXTRACTION_FAILED', 2))
        shutil.rmtree(tmp, ignore_errors=True)
        # ALL_UNREADABLE/2
        ec, res, out, tmp = _run({'global_20261020.json': BAD_JSON}, 'c3d')
        cases.append((res['audit_status'], ec, 'ALL_UNREADABLE', 2))
        shutil.rmtree(tmp, ignore_errors=True)
        # INVALID_PATH/2(根symlink)与NO_INPUT/2(空通道)
        for got_status, got_ec, expected_st, expected_ec in cases:
            with self.subTest(status=expected_st):
                self.assertEqual(got_status, expected_st)
                self.assertEqual(got_ec, expected_ec)
        t = tempfile.mkdtemp(prefix='w4fix4_c3e_')
        self.addCleanup(shutil.rmtree, t, ignore_errors=True)
        real = os.path.join(t, 'r')
        os.makedirs(os.path.join(real, 'daily'))
        _write(os.path.join(real, 'daily'), 'global_20261020.json', G_OK)
        alias = os.path.join(t, 'alias')
        os.symlink(real, alias)
        ec, printed = _run_main(alias, os.path.join(t, 'out'))
        self.assertEqual(ec, 2)
        self.assertIn('INVALID_PATH', printed)
        t2 = tempfile.mkdtemp(prefix='w4fix4_c3f_')
        self.addCleanup(shutil.rmtree, t2, ignore_errors=True)
        os.makedirs(os.path.join(t2, 'data', 'daily'))
        ec, printed = _run_main(os.path.join(t2, 'data'), os.path.join(t2, 'out'))
        self.assertEqual(ec, 2)
        self.assertIn('NO_INPUT', printed)
        self.assertFalse(os.path.exists(os.path.join(t2, 'out')))

    # C4: Manifest保留失败文件(不静默删除;SHA/size/mtime/readable齐备)
    def test_c4_manifest_retains_failed_files(self):
        ec, res, out, tmp = _run({'global_20261020.json': G_LIST}, 'c4')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        me = manifest_of(res, 'daily/global_20261020.json')
        self.assertTrue(me['readable'])
        self.assertEqual(me['extract_status'], 'FAILED')
        for k in ('sha256', 'size', 'mtime_ns', 'channel', 'collector'):
            self.assertIn(k, me)
        mf = _load(glob.glob(os.path.join(out, 'input_manifest_*.json'))[0])
        self.assertIn('extract_status', mf['files'][0])

    # C5: 81项不虚增——失败状态下指标数仍=注册表数,无伪造指标
    def test_c5_no_metric_inflation(self):
        for tag, files in (('allfail', {'global_20261020.json': G_LIST}),
                           ('partial', {'global_20261020.json': G_OK,
                                        'macro_20261020.json': M_LIST})):
            with self.subTest(case=tag):
                ec, res, out, tmp = _run(files, 'c5_' + tag)
                self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
                self.assertEqual(len(res['metrics']), N_METRICS)
                self.assertEqual(res['registry']['metric_count'], N_METRICS)

    # C6: 文件SHA-256可追溯——failed_files与Manifest的SHA==测试复算的真实文件哈希
    def test_c6_sha_traceable(self):
        ec, res, out, tmp = _run({'global_20261020.json': G_LIST}, 'c6')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        with open(os.path.join(tmp, 'data', 'daily', 'global_20261020.json'),
                  'rb') as f:
            real_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(res['extraction']['failed_files'][0]['sha256'], real_hash)
        self.assertEqual(manifest_of(res, 'daily/global_20261020.json')['sha256'],
                         real_hash)

    # C7: Markdown明确披露提取不完整(计数/失败文件/状态/退出码/禁用声明)
    def test_c7_markdown_disclosure(self):
        ec, res, out, tmp = _run({'global_20261020.json': G_OK,
                                  'macro_20261020.json': M_LIST}, 'c7')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        with open(glob.glob(os.path.join(out, 'coverage_audit_*.md'))[0],
                  encoding='utf-8') as f:
            md = f.read()
        self.assertIn('PARTIAL_EXTRACTION', md)
        self.assertIn('提取不完整', md)
        self.assertIn('macro_20261020.json', md)
        self.assertIn('提取失败=1', md)
        self.assertIn('退出码(exit_code): 2', md)
        self.assertIn('不得当COMPLETED使用', md)

    # C8: JSON与执行日志状态一致(末行状态-退出码;提取失败行)
    def test_c8_json_log_consistency(self):
        ec, res, out, tmp = _run({'global_20261020.json': G_LIST}, 'c8')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        with open(os.path.join(out, 'audit_execution_%s.log' % res['run_id']),
                  encoding='utf-8') as f:
            log = f.read()
        self.assertIn('audit_status=EXTRACTION_FAILED exit_code=2', log)
        self.assertIn('提取失败文件1个', log)
        self.assertIn('daily/global_20261020.json', log)
        self.assertEqual(res['audit_status'], 'EXTRACTION_FAILED')
        self.assertEqual(res['exit_code'], 2)
        self.assertEqual(res['extraction']['files_failed'], 1)


# ════════════════ D组: 历史合同继承(FIX1~FIX3语义零回退) ════════════════

class TestDHistoricalRegression(unittest.TestCase):

    # D1: FIX3-01 Schema溯源——别名GOLD非对象→归GOLD_F指标身份+input_files
    def test_d1_fix3_schema_attribution(self):
        ec, res, out, tmp = _run({'global_20261020.json': G_SCHEMA}, 'd1')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(ec, 0)
        gold = by_id(res, 'GOLD_F')
        fe = next(f for f in gold['input_files']
                  if f['relpath'] == 'daily/global_20261020.json')
        self.assertIn('record_schema:not_object', fe['invalid_reasons'])
        self.assertEqual(gold['status'], 'MISSING')
        self.assertEqual(res['integrity']['input_files_association_problems'], [])

    # D2: FIX3-03近期历史——合法短跨度入findings2(口径不回退)
    def test_d2_fix3_recent_history(self):
        ec, res, out, tmp = _run(
            {'global_20261016.json': {"date": "2026-10-16", "data": {
                "SPX": {"close": 5700.0, "date": "2026-10-16",
                        "series": {"dates": ["2026-10-15", "2026-10-16"],
                                   "values": [5699.0, 5700.0]}}}}}, 'd2')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(ec, 0)
        self.assertIn('SPX', res['findings']['2_哪些指标只有最近数据']['metrics'])
        self.assertEqual(by_id(res, 'SPX')['status'], 'OBSERVED')

    # D3: FIX2-01槽位不变量——observed_slots==unique_observation_slots,
    # sum(continuous_segments.slots)==observed_slots(非None指标)
    def test_d3_fix2_slot_invariants(self):
        ec, res, out, tmp = _run(
            {'global_20261016.json': {"date": "2026-10-16", "data": {
                "SPX": {"close": 5700.0, "date": "2026-10-16",
                        "series": {"dates": ["2026-10-15", "2026-10-16"],
                                   "values": [5699.0, 5700.0]}}}}}, 'd3')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        c = by_id(res, 'SPX')['coverage']
        self.assertEqual(c['observed_slots'], c['unique_observation_slots'])
        self.assertEqual(sum(s['slots'] for s in c['continuous_segments']),
                         c['observed_slots'])

    # D4: FIX2-02完整input_files——两文件供SPX,逐文件全列+SHA关联
    def test_d4_fix2_full_input_files(self):
        ec, res, out, tmp = _run(
            {'global_20261016.json': {"date": "2026-10-16", "data": {
                "SPX": {"close": 5700.0, "date": "2026-10-16"}}},
             'global_20261015.json': {"date": "2026-10-15", "data": {
                 "SPX": {"close": 5699.0, "date": "2026-10-15"}}}}, 'd4')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        spx = by_id(res, 'SPX')
        rels = sorted(f['relpath'] for f in spx['input_files'])
        self.assertEqual(rels, ['daily/global_20261015.json',
                                'daily/global_20261016.json'])
        for f in spx['input_files']:
            self.assertEqual(len(f['manifest_sha256']), 64)

    # D5: FIX1连续段——4连续交易日→longest_continuous_segment_slots=4
    def test_d5_fix1_continuous_segments(self):
        ec, res, out, tmp = _run(
            {'global_20261016.json': {"date": "2026-10-16", "data": {
                "GOLD": {"close": 2650.0, "date": "2026-10-16",
                         "series": {"dates": ["2026-10-13", "2026-10-14",
                                              "2026-10-15", "2026-10-16"],
                                    "values": [2647.0, 2648.0, 2649.0,
                                               2650.0]}}}}}, 'd5')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        c = by_id(res, 'GOLD_F')['coverage']
        self.assertEqual(c['longest_continuous_segment_slots'], 4)
        self.assertEqual(c['unique_observation_slots'], 4)

    # D6: FIX1重复拆分——同文件同日重复→same_file_dup计数,unique<raw
    def test_d6_fix1_dup_splitting(self):
        ec, res, out, tmp = _run(
            {'global_20261016.json': {"date": "2026-10-16", "data": {
                "SPX": {"close": 5700.0, "date": "2026-10-16",
                        "series": {"dates": ["2026-10-16", "2026-10-16"],
                                   "values": [5700.0, 5700.0]}}}}}, 'd6')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        d = by_id(res, 'SPX')['counts']
        c = by_id(res, 'SPX')['coverage']
        self.assertGreaterEqual(d['same_file_extra_duplicate_records'], 1)
        self.assertLess(c['total_unique_observations'], d['raw_records'])

    # D7: FIX1-03 MARGIN_BAL身份——仅rzye_billion不获权威观测,键经unmapped披露
    def test_d7_margin_bal_identity(self):
        ec, res, out, tmp = _run(
            {'china_20261020.json': {"date": "2026-10-20",
                                     "margin": {"date": "20261020",
                                                "rzye_billion": 18500.0}}}, 'd7')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(ec, 0)
        self.assertEqual(by_id(res, 'MARGIN_BAL')['status'], 'MISSING')
        keys = [u['raw_key'] for u in res['unmapped_records']]
        self.assertIn('margin:rzye_billion', keys)

    # D8: 五通道文件全部发现与提取(通道计数=1/1/1/1/1)
    def test_d8_five_channels(self):
        ec, res, out, tmp = _run(
            {'global_20261020.json': G_OK,
             'macro_20261020.json': {"date": "2026-10-20",
                                     "data": {"CPI": {"date": "2026-10-20",
                                                      "value": 3.0}},
                                     "derived": {}},
             'china_20261020.json': {"date": "2026-10-20",
                                     "a_share_indices": {"000001.SH": {
                                         "close": 3300.0,
                                         "date": "2026-10-16"}}},
             'rate_economy_20261020.json': {"date": "2026-10-20",
                                            "current_rates": {"FEDFUNDS": {
                                                "date": "2026-10-20",
                                                "value": 4.3}},
                                            "real_economy": {},
                                            "fed_funds_futures": []},
             'research_snapshot_20261020.json': {"facts": [],
                                                 "series_store": {}}}, 'd8')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(ec, 0)
        self.assertEqual(res['input']['by_channel'],
                         {'global': 1, 'china': 1, 'macro': 1,
                          'rate_economy': 1, 'research_snapshot': 1})
        self.assertEqual(res['extraction']['files_extracted'], 5)
        self.assertEqual(res['extraction']['files_failed'], 0)

    # D9: audit_commit=git HEAD且generated_at为真实UTC(含+00:00)
    def test_d9_commit_and_utc(self):
        ec, res, out, tmp = _run({'global_20261020.json': G_OK}, 'd9')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        head = subprocess.run(['git', '-C', ROOT, 'rev-parse', 'HEAD'],
                              capture_output=True, text=True).stdout.strip()
        self.assertEqual(res['audit_commit'], head)
        self.assertTrue(res['generated_at'].endswith('+00:00'))
        self.assertEqual(res['schema_version'], 'w4-coverage-audit/1.4')

    # D10: 输入只读——审计前后输入文件SHA-256不变
    def test_d10_input_readonly(self):
        ec, res, out, tmp = _run({'global_20261020.json': G_OK,
                                  'macro_20261020.json': M_LIST}, 'd10')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(ec, 2)   # PARTIAL也须只读
        for e in res['_manifest_files']:
            p = os.path.join(tmp, 'data', e['relpath'])
            with open(p, 'rb') as f:
                self.assertEqual(hashlib.sha256(f.read()).hexdigest(),
                                 e['sha256'], e['relpath'])
        self.assertFalse(res['integrity']['input_changed_during_audit'])


# ════════════════ E组: 负向敏感性(退化注入必被检出) ════════════════

class TestENegativeSensitivity(unittest.TestCase):

    def _mk(self, prefix):
        t = tempfile.mkdtemp(prefix=prefix)
        self.addCleanup(shutil.rmtree, t, ignore_errors=True)
        return t

    # E1: 恢复realpath自动授权根symlink(等价退化: FIX4-01门禁失效)→
    # audit经symlink入口自动跟随目标并COMPLETED(A2/A7断言必失败=敏感)
    def test_e1_reverted_root_symlink_follows(self):
        t = self._mk('w4fix4_e1_')
        real = os.path.join(t, 'real_data')
        os.makedirs(os.path.join(real, 'daily'))
        _write(os.path.join(real, 'daily'), 'global_20261020.json', G_OK)
        alias = os.path.join(t, 'alias')
        os.symlink(real, alias)
        real_islink = os.path.islink
        alias_norm = os.path.normpath(os.path.abspath(alias))

        def lying_islink(p):
            if os.path.normpath(os.path.abspath(p)) == alias_norm:
                return False          # 模拟"恢复realpath自动授权"的旧实现
            return real_islink(p)

        with mock.patch.object(os.path, 'islink', new=lying_islink):
            ec, printed = _run_main(alias, os.path.join(t, 'out'))
        # 退化态实测: 目标被自动跟随,COMPLETED读取——安全缺陷行为;证明
        # 正常路径下A2/A7的"拒绝"断言真实依赖FIX4-01检查(非偶然通过)
        self.assertEqual(ec, 0)
        res = _load(glob.glob(os.path.join(t, 'out',
                                           'coverage_audit_*.json'))[0])
        self.assertEqual(res['audit_status'], 'COMPLETED')
        self.assertEqual(by_id(res, 'SPX')['status'], 'SINGLE_OBSERVATION')

    # E2: 恢复readable唯一成功判定(退化: 提取失败不改状态)→全部提取失败
    # 仍COMPLETED/exit0(B4/B7/B9必失败=敏感)
    def test_e2_reverted_readable_only_allfail_completed(self):
        orig = hca.run_audit

        def degraded(*a, **k):
            r, lg, code = orig(*a, **k)
            if r.get('audit_status') in ('EXTRACTION_FAILED',
                                         'PARTIAL_EXTRACTION'):
                r['audit_status'] = 'COMPLETED'
                r['exit_code'] = 0
                code = 0
            return r, lg, code

        with mock.patch.object(hca, 'run_audit', degraded):
            ec, res, out, tmp = _run({'global_20261020.json': G_LIST,
                                      'macro_20261020.json': M_LIST}, 'e2')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(ec, 0)                    # 退化态: 错误地成功
        self.assertEqual(res['audit_status'], 'COMPLETED')

    # E3: 删除提取错误传播(退化: 剥离extraction块与manifest提取字段)→
    # 失败状态仍在但无文件级诊断(C2/C4/C7必失败=敏感)
    def test_e3_removed_extraction_disclosure(self):
        orig = hca.run_audit

        def degraded(*a, **k):
            r, lg, code = orig(*a, **k)
            r.pop('extraction', None)
            for e in r.get('manifest', []):
                e.pop('extract_status', None)
                e.pop('extract_error', None)
            return r, lg, code

        with mock.patch.object(hca, 'run_audit', degraded):
            ec, res, out, tmp = _run({'global_20261020.json': G_LIST}, 'e3')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(ec, 2)                    # 状态保留但诊断被删
        self.assertEqual(res['audit_status'], 'EXTRACTION_FAILED')
        self.assertNotIn('extraction', res)
        mf = _load(glob.glob(os.path.join(out, 'input_manifest_*.json'))[0])
        self.assertNotIn('extract_status', mf['files'][0])
        with open(glob.glob(os.path.join(out, 'coverage_audit_*.md'))[0],
                  encoding='utf-8') as f:
            md = f.read()
        self.assertNotIn('提取执行状态', md)

    # E4: 部分提取失败仍COMPLETED(退化同E2,部分场景)→B8必失败=敏感
    def test_e4_reverted_partial_completed(self):
        orig = hca.run_audit

        def degraded(*a, **k):
            r, lg, code = orig(*a, **k)
            if r.get('audit_status') == 'PARTIAL_EXTRACTION':
                r['audit_status'] = 'COMPLETED'
                r['exit_code'] = 0
                code = 0
            return r, lg, code

        with mock.patch.object(hca, 'run_audit', degraded):
            ec, res, out, tmp = _run({'global_20261020.json': G_OK,
                                      'macro_20261020.json': M_LIST}, 'e4')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.assertEqual(ec, 0)                    # 退化态: 部分失败冒充成功
        self.assertEqual(res['audit_status'], 'COMPLETED')


if __name__ == '__main__':
    unittest.main(verbosity=2)
