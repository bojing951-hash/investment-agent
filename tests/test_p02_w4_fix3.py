#!/usr/bin/env python3
"""IA-P0-2-W4-FIX3 联合验收测试(已注册异常Schema溯源+父目录symlink越界阻断
+近期历史合法槽位口径)。

对应指令IA-P0-2-W4-FIX3-DEV-v1.0 §七: 对FIX2最终失败Commit(94fb144)三项
确定性缺陷的真实修复运行测试。全部走真实模块(historical_coverage_audit的
main/run_audit/discover_files/extract_file/summarize/PathBoundaryError;
真实config/metric_registry.json 81项;真实fact_engine/trading_calendar),
不复制审计实现到测试自证:
  A Schema溯源(FIX3-01,指令§四固定例A-F): Global SPX字符串/Macro NFP数组/
    China SHCOMP字符串/已注册别名GOLD非对象→归到指标身份+input_files
    (record_schema:not_object)+保留Manifest关联+不伪造observation_date/
    不增权威历史;未注册UNKNOWN_X仍走unmapped;合法正向路径不受影响
  B 路径安全(FIX3-02,指令§五强制测试): daily目录symlink外指→fail-closed
    INVALID_PATH退出2/不读越界字节/不生成报告/不写输入侧;文件symlink跳过
    披露;相似前缀兄弟目录不因前缀比较误通过;正常daily(/tmp符号链接前缀下)
    不误拒;china-only五通道子集;拒绝后无报告写入;越界正文未被读取(canary)
  C 近期历史(FIX3-03,指令§六固定反例): NDX纯周末→NO_VALID_SLOTS不入
    findings2;SPX单合法交易日→SINGLE且入合法短历史;正常短跨度OBSERVED入;
    日历不可确定UNDETERMINED不入;有效日期+日历外远端异常日期不扩大正式
    跨度(raw span≥30仍按有效槽位跨度入);MD与JSON findings2一致
  D 历史合同回归(FIX1/FIX2已过语义不回退): 合法槽位/连续区间不变量/重复
    拆分不变量/MARGIN_BAL身份/完整input_files/五通道子集/audit_commit+
    generated_at/输入只读SHA
  E 负向敏感性3退化必检出: _file_event_bad退化为no-op(溯源丢失)/
    discover_files退化为跟随父symlink(越界被当有效输入)/summarize恢复
    uniq+span旧判据(近期历史口径回退)——退化实现必使本套件断言失败
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

import historical_coverage_audit as hca   # 被审计的真实审计器(FIX3版)

REGISTRY = os.path.join(ROOT, 'config', 'metric_registry.json')
SCHEMA_V = 'w4-coverage-audit/1.3'


# ════════════════ fixture构造器(合成数据,与真实Schema同构) ════════════════

def _load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def _run(files, tag='fix3', source_note='FIX3合成fixture'):
    """建临时data/daily写入{文件名:对象},跑真实main();返回(ec,result,out,tmp)。"""
    tmp = tempfile.mkdtemp(prefix='w4fix3_%s_' % tag)
    daily = os.path.join(tmp, 'data', 'daily')
    os.makedirs(daily)
    for name, obj in files.items():
        with open(os.path.join(daily, name), 'w', encoding='utf-8') as f:
            f.write(obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False))
    out = os.path.join(tmp, 'out')
    ec = hca.main(['--data-dir', os.path.join(tmp, 'data'), '--out-dir', out,
                   '--registry', REGISTRY, '--source-note', source_note])
    hits = glob.glob(os.path.join(out, 'coverage_audit_*.json'))
    result = _load(hits[0]) if hits else None
    return ec, result, out, tmp


def _cleanup(tmp):
    shutil.rmtree(tmp, ignore_errors=True)


def by_id(result, mid):
    return next(r for r in result['metrics'] if r['metric_id'] == mid)


def schema_files():
    """A组fixture(指令§四固定例A-F): 三通道Schema异常+别名+未注册+合法正向。"""
    return {
        # 例A: Global SPX字符串 | 例D: 已注册别名GOLD非对象 | 未注册UNKNOWN_X |
        # 例F: 合法正向RUT
        'global_20261020.json': {"date": "2026-10-20", "data": {
            "SPX": "not_an_object",
            "UNKNOWN_X": {"close": 1.0, "date": "2026-10-16"},
            "GOLD": 12345,
            "RUT": {"close": 2200.0, "date": "2026-10-16"}}},
        # 例B: Macro NFP数组
        'macro_20261020.json': {"date": "2026-10-20", "data": {
            "NFP": [1, 2, 3]}},
        # 例C: China SHCOMP字符串(a_share_indices的000001.SH归入SHCOMP无效来源)
        'china_20261020.json': {"date": "2026-10-20",
                                "a_share_indices": {"000001.SH": "invalid"}},
        # rate通道current_rates已注册键FEDFUNDS非对象(已注册分支)
        'rate_economy_20261020.json': {"date": "2026-10-20",
                                       "current_rates": {"FEDFUNDS": "bad"}},
    }


def recent_files():
    """C组fixture(指令§六固定反例): NDX纯周末/SPX单合法日+日历外远端/
    RUT正常短跨度/VIX单日。"""
    return {
        # NDX仅周六10-17+周日10-18(无一落在us_equity预期槽位);
        # SPX合法2026-10-16(周五)+日历外远端2026-01-03(周六)
        'global_20261017.json': {"date": "2026-10-17", "data": {
            "NDX": {"close": 20100.0, "date": "2026-10-18",
                    "series": {"dates": ["2026-10-17", "2026-10-18"],
                               "values": [20090.0, 20100.0]}},
            "SPX": {"close": 5700.0, "date": "2026-10-16",
                    "series": {"dates": ["2026-01-03", "2026-10-16"],
                               "values": [5000.0, 5700.0]}}}},
        # RUT相邻两合法交易日(正常短跨度) | VIX单合法交易日
        'global_20261016.json': {"date": "2026-10-16", "data": {
            "RUT": {"close": 2200.0, "date": "2026-10-15",
                    "series": {"dates": ["2026-10-15", "2026-10-16"],
                               "values": [2198.0, 2200.0]}},
            "VIX": {"close": 15.0, "date": "2026-10-16"}}},
    }


def dreg_files():
    """D组fixture: 合法槽位断段/同文件+跨文件重复/MARGIN_BAL身份。"""
    return {
        'global_20261020.json': {"date": "2026-10-20", "data": {
            "GOLD": {"close": 2650.0, "date": "2026-10-16",
                     "series": {"dates": ["2026-10-16", "2026-10-20"],
                                "values": [2609.0, 2650.0]}}}},
        # 跨文件同日重复(10-16)
        'global_20261019.json': {"date": "2026-10-19", "data": {
            "GOLD": {"close": 2609.0, "date": "2026-10-16"}}},
        'china_20261020.json': {"timestamp": 1, "version": "v2",
                                "margin": {"date": "20261020",
                                           "rzye_billion": 18500.0}},
    }


def findings2(res):
    return res['findings']['2_哪些指标只有最近数据']['metrics']


# ════════════════ A组: 已注册异常Schema逐指标溯源(FIX3-01) ════════════════

class TestASchemaAttribution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ec, cls.result, cls.out, cls.tmp = _run(schema_files(), tag='schema')

    @classmethod
    def tearDownClass(cls):
        _cleanup(cls.tmp)

    def _schema_entry(self, mid, relpath):
        r = by_id(self.result, mid)
        hits = [e for e in r['input_files'] if e['relpath'] == relpath]
        return r, hits

    # A1: Global SPX字符串→归SPX指标(不进unmapped),文件级schema事件+无有效观测
    def test_a1_global_spx_string(self):
        r, hits = self._schema_entry('SPX', 'daily/global_20261020.json')
        self.assertEqual(self.ec, 0)
        self.assertEqual(len(hits), 1)
        e = hits[0]
        self.assertEqual(e['channel'], 'global')
        self.assertIn('record', e['record_types'])
        self.assertIn('record_schema:not_object', e['invalid_reasons'])
        self.assertFalse(e['valid_observation_contributed'])
        self.assertEqual(e['valid_records'], 0)
        self.assertEqual(r['status'], 'MISSING')   # 无有效观测不冒充覆盖

    # A2: Macro NFP数组→归NFP指标,同口径
    def test_a2_macro_nfp_array(self):
        r, hits = self._schema_entry('NFP', 'daily/macro_20261020.json')
        self.assertEqual(len(hits), 1)
        self.assertIn('record_schema:not_object', hits[0]['invalid_reasons'])
        self.assertEqual(r['status'], 'MISSING')

    # A3: China SHCOMP字符串→归SHCOMP无效来源(000001.SH不进未注册清单)
    def test_a3_china_shcomp_string(self):
        r, hits = self._schema_entry('SHCOMP', 'daily/china_20261020.json')
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]['channel'], 'china')
        self.assertIn('record_schema:not_object', hits[0]['invalid_reasons'])
        self.assertEqual(r['status'], 'MISSING')

    # A4: 已注册别名GOLD非对象→别名先解析再判结构,归GOLD_F
    def test_a4_alias_gold_non_object(self):
        r, hits = self._schema_entry('GOLD_F', 'daily/global_20261020.json')
        self.assertEqual(len(hits), 1)
        self.assertIn('record_schema:not_object', hits[0]['invalid_reasons'])
        self.assertEqual(r['status'], 'MISSING')

    # A5: 未注册UNKNOWN_X→仍走unmapped(身份与结构两类不再互混)
    def test_a5_unknown_x_unmapped(self):
        keys = {(u['channel'], u['raw_key']) for u in self.result['unmapped_records']}
        self.assertIn(('global', 'UNKNOWN_X'), keys)
        self.assertNotIn(('global', 'SPX'), keys)
        self.assertNotIn(('global', 'GOLD'), keys)
        self.assertNotIn(('macro', 'NFP'), keys)
        self.assertNotIn(('china', '000001.SH'), keys)
        self.assertNotIn(('rate_economy', 'current_rates:FEDFUNDS'), keys)
        self.assertEqual([m['metric_id'] for m in self.result['metrics']
                          if m['metric_id'] == 'UNKNOWN_X'], [])

    # A6: 合法正向路径不受影响(RUT正常point观测)
    def test_a6_positive_path_untouched(self):
        r = by_id(self.result, 'RUT')
        self.assertEqual(r['status'], 'SINGLE_OBSERVATION')
        self.assertEqual(r['coverage']['total_unique_observations'], 1)
        e = [x for x in r['input_files'] if x['relpath'] == 'daily/global_20261020.json']
        self.assertEqual(len(e), 1)
        self.assertEqual(e[0]['invalid_reasons'], [])
        self.assertTrue(e[0]['valid_observation_contributed'])
        self.assertEqual(e[0]['record_types'], ['point'])

    # A7: 不伪造observation_date/数值/权威历史(五项Schema异常指标全核)
    def test_a7_no_fabricated_observations(self):
        for mid in ('SPX', 'GOLD_F', 'NFP', 'SHCOMP', 'FED_FUNDS'):
            r = by_id(self.result, mid)
            c = r['coverage']
            self.assertEqual(c['total_unique_observations'], 0, mid)
            # 无权威观测日→无预期窗: observed_slots=None(不以0冒充已认证空窗)
            self.assertIsNone(c['observed_slots'], mid)
            self.assertEqual(c['unique_observation_slots'], 0, mid)
            self.assertEqual(c['continuous_segments'], [], mid)
            self.assertIsNone(c['first_observation_date'], mid)
            self.assertIsNone(c['last_observation_date'], mid)
            self.assertEqual(r['counts']['authority_raw_records'], 0, mid)
            self.assertGreaterEqual(r['counts']['invalid_date_records'], 1, mid)

    # A8: rate通道已注册分支(current_rates FEDFUNDS)同口径拆分
    def test_a8_rate_current_rates_registered(self):
        r, hits = self._schema_entry('FED_FUNDS', 'daily/rate_economy_20261020.json')
        self.assertEqual(len(hits), 1)
        self.assertIn('record_schema:not_object', hits[0]['invalid_reasons'])
        self.assertEqual(r['status'], 'MISSING')

    # A9: 保留Manifest关联(SHA/size/mtime齐备+关联零问题)+schema 1.3
    def test_a9_manifest_association_kept(self):
        mfile = glob.glob(os.path.join(self.out, 'input_manifest_*.json'))[0]
        sha_by_rel = {e['relpath']: e['sha256']
                      for e in _load(mfile)['files']}
        for mid, rel in (('SPX', 'daily/global_20261020.json'),
                         ('GOLD_F', 'daily/global_20261020.json'),
                         ('NFP', 'daily/macro_20261020.json'),
                         ('SHCOMP', 'daily/china_20261020.json'),
                         ('FED_FUNDS', 'daily/rate_economy_20261020.json')):
            e = [x for x in by_id(self.result, mid)['input_files']
                 if x['relpath'] == rel]
            self.assertEqual(len(e), 1, mid)
            self.assertEqual(e[0]['manifest_sha256'], sha_by_rel[rel], mid)
            self.assertEqual(e[0]['manifest_association'], 'ok', mid)
            self.assertIsNotNone(e[0]['size'], mid)
            self.assertIsNotNone(e[0]['mtime_ns'], mid)
        self.assertEqual(self.result['integrity']['input_files_association_problems'], [])
        self.assertEqual(self.result['schema_version'], SCHEMA_V)


# ════════════════ B组: 父目录symlink越界阻断(FIX3-02) ════════════════

class TestBPathBoundary(unittest.TestCase):
    """全部真实文件系统构造(临时目录),无生产/私人路径,无敏感内容。"""

    def _mk(self, prefix):
        t = tempfile.mkdtemp(prefix=prefix)
        self.addCleanup(shutil.rmtree, t, ignore_errors=True)
        return t

    def _run_main(self, data_dir, out, capture=True):
        buf = io.StringIO()
        stdout, sys.stdout = sys.stdout, buf
        try:
            ec = hca.main(['--data-dir', data_dir, '--out-dir', out,
                           '--registry', REGISTRY])
        finally:
            sys.stdout = stdout
        return ec, buf.getvalue()

    # B1: daily目录symlink外指→fail-closed: INVALID_PATH退出2,不写任何输出
    def test_b1_daily_dir_symlink_rejected(self):
        t = self._mk('w4fix3_b1_')
        data = os.path.join(t, 'allowed', 'data')
        os.makedirs(data)
        outside = os.path.join(t, 'outside')
        os.makedirs(outside)
        with open(os.path.join(outside, 'global_20261020.json'), 'w') as f:
            json.dump({"date": "2026-10-20",
                       "data": {"SPX": {"close": 5700.0, "date": "2026-10-16"}}}, f)
        os.symlink(outside, os.path.join(data, 'daily'))
        out = os.path.join(t, 'out')
        ec, printed = self._run_main(data, out)
        self.assertEqual(ec, 2)
        self.assertFalse(os.path.exists(out))   # 非法路径下不创建/不写入
        self.assertEqual(glob.glob(os.path.join(t, '**', 'coverage_audit_*'),
                                   recursive=True), [])
        self.assertEqual(glob.glob(os.path.join(t, '**', 'input_manifest_*'),
                                   recursive=True), [])
        self.assertEqual(glob.glob(os.path.join(t, '**', 'audit_execution_*'),
                                   recursive=True), [])
        self.assertIn('路径边界拒绝', printed)
        self.assertIn('INVALID_PATH', printed)
        self.assertIn('符号链接', printed)

    # B2: 文件symlink→跳过并披露,正常daily文件不受影响(FIX3保留FIX1行为)
    def test_b2_file_symlink_skipped_disclosed(self):
        t = self._mk('w4fix3_b2_')
        daily = os.path.join(t, 'data', 'daily')
        os.makedirs(daily)
        with open(os.path.join(daily, 'china_20261020.json'), 'w') as f:
            json.dump({"date": "2026-10-20",
                       "a_share_indices": {"000001.SH": {"close": 3300.0,
                                                         "date": "2026-10-16"}}}, f)
        os.symlink('/etc/hostname', os.path.join(daily, 'global_20261020.json'))
        out = os.path.join(t, 'out')
        ec, _ = self._run_main(os.path.join(t, 'data'), out)
        self.assertEqual(ec, 0)
        res = _load(glob.glob(os.path.join(out, 'coverage_audit_*.json'))[0])
        self.assertEqual(res['audit_status'], 'COMPLETED')
        self.assertEqual(res['input']['excluded']['symlink_skipped'],
                         ['daily/global_20261020.json'])
        self.assertEqual(by_id(res, 'SHCOMP')['status'], 'SINGLE_OBSERVATION')

    # B3: discover_files单元级——真实路径越出授权根即raise(消息含双方realpath)
    def test_b3_discover_files_raises_outside_root(self):
        t = self._mk('w4fix3_b3_')
        data = os.path.join(t, 'allowed', 'data')
        os.makedirs(data)
        outside = os.path.join(t, 'outside')
        os.makedirs(outside)
        with open(os.path.join(outside, 'global_20261020.json'), 'w') as f:
            json.dump({"date": "2026-10-20", "data": {}}, f)
        os.symlink(outside, os.path.join(data, 'daily'))
        with self.assertRaises(hca.PathBoundaryError) as cm:
            hca.discover_files(data)
        self.assertIn(os.path.realpath(outside), str(cm.exception))
        self.assertIn(os.path.realpath(data), str(cm.exception))

    # B4: 相似前缀兄弟目录(allowed_evil)不因前缀比较误通过(commonpath语义)
    def test_b4_prefix_similar_sibling_rejected(self):
        t = self._mk('w4fix3_b4_')
        data = os.path.join(t, 'allowed', 'data')
        os.makedirs(data)
        evil = os.path.join(t, 'allowed_evil')
        os.makedirs(evil)
        with open(os.path.join(evil, 'global_20261020.json'), 'w') as f:
            json.dump({"date": "2026-10-20",
                       "data": {"SPX": {"close": 5700.0, "date": "2026-10-16"}}}, f)
        os.symlink(evil, os.path.join(data, 'daily'))
        self.assertTrue(os.path.realpath(evil).startswith(
            os.path.realpath(data)[:len(os.path.realpath(data)) - 5]))
        with self.assertRaises(hca.PathBoundaryError):
            hca.discover_files(data)   # startswith实现会误放行,commonpath拒绝
        out = os.path.join(t, 'out')
        ec, _ = self._run_main(data, out)
        self.assertEqual(ec, 2)
        self.assertFalse(os.path.exists(out))

    # B5: 正常daily(输入根含符号路径前缀,如macOS /tmp→/private/tmp)不误拒
    def test_b5_normal_daily_completes(self):
        t = self._mk('w4fix3_b5_')       # tempfile根本身位于符号链接前缀之下
        daily = os.path.join(t, 'data', 'daily')
        os.makedirs(daily)
        with open(os.path.join(daily, 'global_20261020.json'), 'w') as f:
            json.dump({"date": "2026-10-20",
                       "data": {"SPX": {"close": 5700.0, "date": "2026-10-16"}}}, f)
        self.assertNotEqual(os.path.realpath(t), t)   # 前提: 根确经符号路径
        out = os.path.join(t, 'out')
        ec, _ = self._run_main(os.path.join(t, 'data'), out)
        self.assertEqual(ec, 0)
        res = _load(glob.glob(os.path.join(out, 'coverage_audit_*.json'))[0])
        self.assertEqual(res['audit_status'], 'COMPLETED')
        self.assertEqual(by_id(res, 'SPX')['status'], 'SINGLE_OBSERVATION')

    # B6: china-only五通道子集仍有效(FIX1-04语义在FIX3下不回退)
    def test_b6_china_only_subset(self):
        t = self._mk('w4fix3_b6_')
        daily = os.path.join(t, 'data', 'daily')
        os.makedirs(daily)
        with open(os.path.join(daily, 'china_20261020.json'), 'w') as f:
            json.dump({"timestamp": 1, "version": "v2",
                       "a_share_indices": {"000001.SH": {"name": "上证指数",
                                                         "close": 3300.0,
                                                         "date": "20261020"}}}, f)
        out = os.path.join(t, 'out')
        ec, _ = self._run_main(os.path.join(t, 'data'), out)
        self.assertEqual(ec, 0)
        res = _load(glob.glob(os.path.join(out, 'coverage_audit_*.json'))[0])
        self.assertEqual(res['audit_status'], 'COMPLETED')
        self.assertEqual(len(res['metrics']), 81)
        self.assertEqual(res['input']['by_channel']['china'], 1)

    # B7: 拒绝后零新增——allowed/outside两侧均不写入任何文件
    def test_b7_no_writes_after_rejection(self):
        t = self._mk('w4fix3_b7_')
        data = os.path.join(t, 'allowed', 'data')
        os.makedirs(data)
        outside = os.path.join(t, 'outside')
        os.makedirs(outside)
        with open(os.path.join(outside, 'global_20261020.json'), 'w') as f:
            f.write('{"date":"2026-10-20","data":{"SPX":{"close":1,"date":"2026-10-16"}}}')
        os.symlink(outside, os.path.join(data, 'daily'))

        def snap(root):
            return sorted(
                (p, os.stat(os.path.join(dp, p)).st_mtime_ns)
                for dp, _dn, fn in os.walk(root) for p in fn
                if not os.path.islink(os.path.join(dp, p)))

        before = snap(data) + snap(outside)
        ec, _ = self._run_main(data, os.path.join(t, 'out'))
        self.assertEqual(ec, 2)
        self.assertEqual(before, snap(data) + snap(outside))   # 输入侧零改动
        self.assertFalse(os.path.exists(os.path.join(t, 'out')))

    # B8: 越界正文未被读取(canary扫描: 拒绝路径下无任何产出含越界文件内容)
    def test_b8_outside_bytes_not_read(self):
        t = self._mk('w4fix3_b8_')
        data = os.path.join(t, 'allowed', 'data')
        os.makedirs(data)
        outside = os.path.join(t, 'outside')
        os.makedirs(outside)
        canary = 'FIX3_CANARY_9d1f_不读越界正文'
        with open(os.path.join(outside, 'global_20261020.json'), 'w') as f:
            f.write('{"date":"2026-10-20","data":{"SPX":"%s"}}' % canary)
        os.symlink(outside, os.path.join(data, 'daily'))
        out = os.path.join(t, 'out')
        ec, _ = self._run_main(data, out)
        self.assertEqual(ec, 2)
        leaks = set()
        for p in glob.glob(os.path.join(t, '**', '*'), recursive=True):
            if os.path.isfile(p) and not os.path.islink(p):
                try:
                    with open(p, encoding='utf-8', errors='ignore') as f:
                        if canary in f.read():
                            leaks.add(os.path.realpath(p))
                except OSError:
                    pass
        # 唯一含canary的文件=越界源文件本身(realpath去重符号链接视图),
        # 无任何审计产出(报告/清单/日志)包含越界正文
        self.assertEqual(sorted(leaks),
                         [os.path.realpath(os.path.join(outside,
                                                        'global_20261020.json'))])


# ════════════════ C组: 近期历史合法槽位口径(FIX3-03) ════════════════

class TestCRecentHistory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ec, cls.result, cls.out, cls.tmp = _run(recent_files(), tag='recent')

    @classmethod
    def tearDownClass(cls):
        _cleanup(cls.tmp)

    # C1: NDX纯周末→NO_VALID_SLOTS/0槽/无段,不入findings2
    def test_c1_ndx_weekend_only_excluded(self):
        n = by_id(self.result, 'NDX')
        self.assertEqual(n['status'], 'NO_VALID_SLOTS')
        self.assertEqual(n['coverage']['observed_slots'], 0)
        self.assertEqual(n['coverage']['continuous_segments'], [])
        self.assertNotIn('NDX', findings2(self.result))

    # C2: SPX单合法交易日→SINGLE_OBSERVATION保持,且入合法短历史
    def test_c2_spx_single_valid_day_included(self):
        s = by_id(self.result, 'SPX')
        self.assertEqual(s['status'], 'SINGLE_OBSERVATION')
        self.assertEqual(s['coverage']['observed_slots'], 1)
        self.assertIn('SPX', findings2(self.result))

    # C3: 正常短跨度(相邻两合法交易日)→OBSERVED且入findings2
    def test_c3_normal_short_span_included(self):
        r = by_id(self.result, 'RUT')
        self.assertEqual(r['status'], 'OBSERVED')
        self.assertEqual(r['coverage']['observed_slots'], 2)
        self.assertIn('RUT', findings2(self.result))

    # C4: 预期槽位无法确定→UNDETERMINED不入findings2(对照: 可认证时同款
    #     单日观测为SINGLE且入)——只经expected_slots注入缝,不改判据本身
    def test_c4_undetermined_excluded(self):
        def unavailable(freq, first, last, calendar):
            return None, None, '日历限制注记', '观察窗不可解析(测试注入)'

        files = {'global_20261020.json': {"date": "2026-10-20", "data": {
            "GOLD": {"close": 2650.0, "date": "2026-10-16"}}}}
        ec, res, _out, tmp = _run(files, tag='c4a')
        try:
            self.assertIn('GOLD_F', findings2(res))       # 基线: 可认证→入
        finally:
            _cleanup(tmp)
        tmp = tempfile.mkdtemp(prefix='w4fix3_c4b_')
        try:
            daily = os.path.join(tmp, 'data', 'daily')
            os.makedirs(daily)
            for name, obj in files.items():
                with open(os.path.join(daily, name), 'w', encoding='utf-8') as f:
                    json.dump(obj, f)
            with mock.patch.object(hca, 'expected_slots', unavailable):
                ec = hca.main(['--data-dir', os.path.join(tmp, 'data'),
                               '--out-dir', os.path.join(tmp, 'out'),
                               '--registry', REGISTRY])
            res2 = _load(glob.glob(os.path.join(tmp, 'out',
                                                'coverage_audit_*.json'))[0])
            g = by_id(res2, 'GOLD_F')
            self.assertEqual(ec, 0)
            self.assertEqual(g['status'], 'UNDETERMINED')
            self.assertNotIn('GOLD_F', findings2(res2))
        finally:
            _cleanup(tmp)

    # C5: 有效日期+日历外远端异常日期——raw span≥30但有效槽位跨度=0:
    #     远端异常日期不得扩大正式跨度(仍判近期),extra完整披露
    def test_c5_far_outlier_does_not_expand_span(self):
        s = by_id(self.result, 'SPX')
        c = s['coverage']
        self.assertEqual(c['total_unique_observations'], 2)
        self.assertGreaterEqual(c['observation_span_days'], 30)   # 描述性原始字段
        self.assertGreaterEqual(c['extra_observations_beyond_calendar'], 1)
        self.assertEqual(len(c['continuous_segments']), 1)
        self.assertEqual(c['continuous_segments'][0]['slots'], 1)
        self.assertIn('SPX', findings2(self.result))   # 按有效槽位跨度(0<30)判

    # C6: MD与JSON一致(findings2指标清单逐项对应)
    def test_c6_md_matches_json(self):
        md_path = glob.glob(os.path.join(self.out, 'coverage_audit_*.md'))[0]
        with open(md_path, encoding='utf-8') as f:
            md = f.read()
        i = md.find('2_哪些指标只有最近数据')
        self.assertGreaterEqual(i, 0)
        section = md[i:i + 600]
        for mid in findings2(self.result):
            self.assertIn(mid, section)
        self.assertNotIn('NDX', section.split('3_哪些指标')[0])


# ════════════════ D组: 历史合同回归(FIX1/FIX2语义不回退) ════════════════

class TestDHistoricalRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ec, cls.result, cls.out, cls.tmp = _run(dreg_files(), tag='dreg')

    @classmethod
    def tearDownClass(cls):
        _cleanup(cls.tmp)

    # D1: 合法覆盖槽位(10-16+10-20缺10-19→2槽/缺1/2段)
    def test_d1_eligible_slots(self):
        g = by_id(self.result, 'GOLD_F')
        c = g['coverage']
        self.assertEqual(c['unique_observation_slots'], 2)
        self.assertEqual(c['observed_slots'], 2)
        self.assertEqual(c['missing_slots_count'], 1)
        self.assertEqual(len(c['continuous_segments']), 2)
        self.assertEqual(g['status'], 'OBSERVED')

    # D2: 连续区间不变量(槽位和=合法槽位=唯一槽位)
    def test_d2_segment_invariant(self):
        for r in self.result['metrics']:
            c = r['coverage']
            n = c['unique_observation_slots']
            if n is not None:
                self.assertEqual(
                    n, sum(s['slots'] for s in c['continuous_segments']),
                    r['metric_id'])
                self.assertLessEqual(c['longest_continuous_segment_slots'],
                                     n, r['metric_id'])

    # D3: 重复拆分不变量(权威原始=唯一观测日+同文件额外+跨文件额外)
    def test_d3_duplicate_split_invariant(self):
        g = by_id(self.result, 'GOLD_F')
        cnt = g['counts']
        self.assertGreaterEqual(cnt['same_file_extra_duplicate_records'], 1)
        self.assertGreaterEqual(cnt['cross_file_duplicate_records'], 1)
        self.assertEqual(cnt['authority_raw_records'],
                         cnt['unique_observation_dates']
                         + cnt['same_file_extra_duplicate_records']
                         + cnt['cross_file_duplicate_records'])

    # D4: MARGIN_BAL身份(仅rzye_billion不得获权威,identity_mismatch披露)
    def test_d4_margin_bal_identity(self):
        m = by_id(self.result, 'MARGIN_BAL')
        self.assertEqual(m['status'], 'MISSING')
        self.assertEqual(m['coverage']['total_unique_observations'], 0)
        rzye = [u for u in self.result['unmapped_records']
                if u['raw_key'] == 'margin:rzye_billion']
        self.assertTrue(rzye and 'identity_mismatch' in rzye[0]['note'])

    # D5: 完整input_files(两个贡献文件全列,无截断,均标记有效贡献)
    def test_d5_input_files_complete(self):
        g = by_id(self.result, 'GOLD_F')
        rels = [e['relpath'] for e in g['input_files']]
        self.assertEqual(sorted(rels), ['daily/global_20261019.json',
                                        'daily/global_20261020.json'])
        self.assertTrue(all(e['valid_observation_contributed']
                            for e in g['input_files']))

    # D6: 五通道子集各自有效(global+macro+china三通道fixture→逐通道计数)
    def test_d6_channel_subset(self):
        self.assertEqual(self.result['input']['by_channel'],
                         {'global': 2, 'macro': 0, 'china': 1,
                          'rate_economy': 0, 'research_snapshot': 0})
        self.assertEqual(self.result['audit_status'], 'COMPLETED')

    # D7: audit_commit=真实git HEAD+generated_at真实UTC
    def test_d7_audit_metadata(self):
        head = subprocess.run(['git', '-C', ROOT, 'rev-parse', 'HEAD'],
                              capture_output=True, text=True).stdout.strip()
        self.assertRegex(self.result['audit_commit'], r'^[0-9a-f]{40}$')
        if head:
            self.assertEqual(self.result['audit_commit'], head)
        self.assertRegex(self.result['generated_at'],
                         r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00$')

    # D8: 输入只读——审计后逐文件SHA-256与Manifest一致(输入未被修改)
    def test_d8_inputs_readonly(self):
        mfile = glob.glob(os.path.join(self.out, 'input_manifest_*.json'))[0]
        sha_by_rel = {e['relpath']: e['sha256'] for e in _load(mfile)['files']}
        for rel, sha in sha_by_rel.items():
            with open(os.path.join(self.tmp, 'data', rel), 'rb') as f:
                self.assertEqual(hashlib.sha256(f.read()).hexdigest(), sha, rel)


# ════════════════ E组: 负向敏感性(3退化必被检出) ════════════════

class TestENegativeSensitivity(unittest.TestCase):
    """证明: 把FIX3任一修复退化回旧实现,A/B/C组断言会失败(而非继续通过)。"""

    # E1: _file_event_bad退化为no-op(Schema溯源丢失)→A1/A9断言失败
    def test_e1_schema_traceability_degrade_detected(self):
        files = schema_files()
        tmp = tempfile.mkdtemp(prefix='w4fix3_e1_')
        try:
            daily = os.path.join(tmp, 'data', 'daily')
            os.makedirs(daily)
            for name, obj in files.items():
                with open(os.path.join(daily, name), 'w', encoding='utf-8') as f:
                    json.dump(obj, f)
            with mock.patch.object(hca, '_file_event_bad',
                                   lambda *a, **k: None):
                ec = hca.main(['--data-dir', os.path.join(tmp, 'data'),
                               '--out-dir', os.path.join(tmp, 'out'),
                               '--registry', REGISTRY])
            res = _load(glob.glob(os.path.join(tmp, 'out',
                                               'coverage_audit_*.json'))[0])
            s = by_id(res, 'SPX')
            self.assertEqual(ec, 0)
            # 退化后果: 文件未登记input_files(A1的len(hits)==1失败)且无
            # record_schema:not_object原因(A1/A9失败)——必被检出
            self.assertEqual([e for e in s['input_files']
                              if e['relpath'] == 'daily/global_20261020.json'], [])
            self.assertEqual(
                [e for e in s['input_files']
                 if 'record_schema:not_object' in e['invalid_reasons']], [])
        finally:
            _cleanup(tmp)

    # E2: discover_files退化为跟随父symlink(越界被当有效输入)→B1断言失败
    def test_e2_parent_symlink_follow_degrade_detected(self):
        t = tempfile.mkdtemp(prefix='w4fix3_e2_')
        try:
            data = os.path.join(t, 'allowed', 'data')
            os.makedirs(data)
            outside = os.path.join(t, 'outside')
            os.makedirs(outside)
            with open(os.path.join(outside, 'global_20261020.json'), 'w') as f:
                json.dump({"date": "2026-10-20",
                           "data": {"SPX": {"close": 5700.0,
                                            "date": "2026-10-16"}}}, f)
            os.symlink(outside, os.path.join(data, 'daily'))
            orig = hca.discover_files

            def follow_parent(data_dir):   # 旧缺陷: 解析父symlink继续执行
                rp = os.path.realpath(os.path.join(os.path.realpath(data_dir),
                                                   'daily'))
                return orig(rp)

            with mock.patch.object(hca, 'discover_files', follow_parent):
                ec = hca.main(['--data-dir', data, '--out-dir', os.path.join(t, 'out'),
                               '--registry', REGISTRY])
            # 退化后果: 越界文件被读取并输出COMPLETED(B1的ec==2/无报告失败)
            self.assertEqual(ec, 0)
            self.assertNotEqual(glob.glob(os.path.join(t, 'out',
                                                       'coverage_audit_*.json')), [])
        finally:
            _cleanup(t)

    # E3: summarize恢复uniq+span旧判据(近期历史口径回退)→C1/C5断言失败
    def test_e3_recent_only_old_criteria_degrade_detected(self):
        orig = hca.summarize
        tmax = hca.THRESHOLDS['recent_only_span_days_max']

        def old_judgment(metrics, unmapped_list=()):
            summary, findings = orig(metrics, unmapped_list)
            old = [r['metric_id'] for r in metrics
                   if r['coverage']['total_unique_observations'] >= 1
                   and r['coverage']['observation_span_days'] is not None
                   and r['coverage']['observation_span_days'] < tmax]
            findings['2_哪些指标只有最近数据']['metrics'] = old
            return summary, findings

        tmp = tempfile.mkdtemp(prefix='w4fix3_e3_')
        try:
            daily = os.path.join(tmp, 'data', 'daily')
            os.makedirs(daily)
            for name, obj in recent_files().items():
                with open(os.path.join(daily, name), 'w', encoding='utf-8') as f:
                    json.dump(obj, f)
            with mock.patch.object(hca, 'summarize', old_judgment):
                ec = hca.main(['--data-dir', os.path.join(tmp, 'data'),
                               '--out-dir', os.path.join(tmp, 'out'),
                               '--registry', REGISTRY])
            res = _load(glob.glob(os.path.join(tmp, 'out',
                                               'coverage_audit_*.json'))[0])
            f2 = findings2(res)
            self.assertEqual(ec, 0)
            # 退化后果: NDX(纯周末)被误入/SPX(远端异常日期撑大raw span)被误出
            self.assertIn('NDX', f2)          # C1的NotIn失败
            self.assertNotIn('SPX', f2)       # C5的In失败——必被检出
        finally:
            _cleanup(tmp)


if __name__ == '__main__':
    unittest.main(verbosity=2)
