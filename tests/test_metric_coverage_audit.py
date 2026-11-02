# -*- coding: utf-8 -*-
"""IA-DATA-W2 专项测试(IA-DATA-W2-AC-v1.0 W2-AC-02 范围B)。

被测对象: scripts/metric_coverage_audit.py(只读覆盖审计工具)。
全部 fixture 为 tempfile 合成 registry/数据档(自造小 JSON),零网络、
零真实 data/daily 引用、零真实 registry 路径引用。

覆盖面(W2-AC-02):
  M组 四类可区分机械情形(逐项真对照工具输出):
     M1 字段在且非空 → PRESENT(含 global/macro 别名映射 GOLD→GOLD_F、WTI→WTI_SPOT_M);
     M2 字段在但 null → PRESENT_NULL(叶键null)与 PATH_NULL(途中节点null,如 southbound:null);
     M3 文件在而字段缺席 → KEY_ABSENT(MARGIN_BAL 引擎期望 balance 而采集端只写 rzye 系
        ——工具须同时给出 collector_success_keys 机械对照;SH_PE 同理给 valuation 探针);
     M4 数据面缺席 → FILE_ABSENT(通道文件整体不在窗口);
  W组 窗口历史: 多文件按日期排序,新档缺席而旧档在场逐文件如实登记(FED_FUNDS);
  X组 派生依赖: DERIVED_READY/DERIVED_BLOCKED(NFP_MOM_K 序列面附加事实);
  Y组 弃用档: macro 顶层 derived 字典(macro_derived_dict);
  C组 退出码语义: 正常=0;registry 缺失/坏JSON/无metrics/坏数据目录=2+stderr;
  R组 负向敏感性(repo R3 惯例,文本级最小退化+importlib加载退化副本):
     R1 null盲化(叶null误报PRESENT → M2 断言必红);
     R2 途中null误判KEY_ABSENT(PATH_NULL/KEY_ABSENT 两情形分离被破坏 → 断言必红)。
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, 'scripts', 'metric_coverage_audit.py')
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import metric_coverage_audit as mca  # noqa: E402


def _write(path, text):
    Path(path).write_text(text, encoding='utf-8')
    return path


def _wjson(path, obj):
    return _write(path, json.dumps(obj, ensure_ascii=False))


# ── 合成 registry(仅工具消费字段: metric_id/source/source_symbol/status) ──
def make_registry():
    def entry(mid, source, sym=None, status='active'):
        return {'metric_id': mid, 'source': source, 'source_symbol': sym or mid,
                'status': status, 'frequency': 'daily'}
    return {'version': 'test-1', 'metrics': [
        entry('SPX', 'global_market_collector', '^GSPC'),
        entry('GOLD_F', 'global_market_collector', 'GC=F'),
        entry('UST_2Y', 'macro_collector', 'DGS2'),
        entry('UST_10Y', 'macro_collector', 'DGS10'),
        entry('BEI_10Y', 'macro_collector', 'T10YIE'),
        entry('WTI_SPOT_M', 'macro_collector', 'WTISPLC'),
        entry('NFP', 'macro_collector', 'PAYEMS'),
        entry('NFP_MOM_K', 'macro_collector', 'PAYEMS(derived)'),
        entry('FED_FUNDS', 'macro_collector', 'FEDFUNDS'),
        entry('REAL_SHORT', 'macro_collector(derived)', 'UST_2Y−BEI_5Y',
              status='deprecated'),
        entry('REAL_10Y', 'fact_engine(derived)', 'UST_10Y−BEI_10Y'),
        entry('DFF', 'rate_expectations', 'DFF'),
        entry('ZQ_F1_PRICE', 'rate_expectations', 'ZQ=F'),
        entry('SHCOMP', 'china_market_collector', '000001.SH'),
        entry('HSI', 'china_market_collector', 'hkHSI'),
        entry('SB_FLOW', 'china_market_collector', 'southbound'),
        entry('MARGIN_BAL', 'china_market_collector', 'margin'),
        entry('SH_PE', 'china_market_collector', 'valuation'),
        entry('SH_AMOUNT', 'china_market_collector', '000001.SH.amount'),
        entry('CN_TOTAL_TURNOVER', 'china_market_collector', '000001.SH+399001.SZ'),
        entry('MYSTERY', 'nonexistent_collector', '???'),
    ]}


GLOBAL_DOC = {
    'date': '20260102', 'time': '07:00:00', 'count': 2,
    'data': {
        'SPX': {'close': 6000.25, 'date': '2026-01-01'},
        'GOLD': {'close': None, 'date': '2026-01-01'},          # M2 叶键null
    },
}

MACRO_DOC = {
    'date': '20260102',
    'data': {
        'UST_2Y': {'value': 4.2, 'date': '2026-01-01'},
        'UST_10Y': {'value': 4.5, 'date': '2026-01-01'},
        'BEI_10Y': {'value': 2.3, 'date': '2026-01-01'},
        'WTI': {'value': 78.9, 'date': '2025-12-01'},            # 引擎别名→WTI_SPOT_M
        'NFP': {'value': 160000.0, 'date': '2025-12-01',
                'series': {'dates': ['2025-11-01', '2025-12-01'],
                           'values': [159900.0, 160000.0]}},
        # FED_FUNDS 键整体缺席 → M3(采集端单系列失败时不写键)
    },
    'alerts': [],
    'derived': {'REAL_SHORT': 1.9},                              # Y组 弃用档
}

MACRO_DOC_OLD = {
    'date': '20260101',
    'data': {
        'FED_FUNDS': {'value': 4.33, 'date': '2025-11-01'},      # W组 旧档在场
    },
    'alerts': [],
    'derived': {},
}

CHINA_DOC = {
    'timestamp': '2026-01-02 07:00:00', 'version': '2.1',
    'a_share_indices': {},                                       # M3 容器在键缺席(SHCOMP)
    'hk_indices': {'^HSI': {'close': 20000.0, 'date': '2026-01-02',
                            'series': {'dates': ['2026-01-02'],
                                       'values': [20000.0]}}},
    'southbound': None,                                          # M2 途中节点null(SB_FLOW)
    'margin': {'date': '20260102', 'rzye': 1.85e12, 'rqye': 3.0e10,
               'rzye_billion': 18500.0},                         # M3 无balance+采集键在场
    'valuation': {'000300.SH': {'pe_ttm': 12.3, 'pb': 1.4}},     # M3 无扁平pe/无000001.SH
    'turnover': {'date': '20260102', 'scope': 'test',
                 'sh_amount_billion': 6000.0, 'sz_amount_billion': 4000.0,
                 'total_amount_billion': 10000.0, 'volume_billion': 10000.0},
    'ah_premium': None,
}

RATE_DOC = {
    'date': '20260102',
    'fed_funds_futures': [
        {'ticker': 'ZQ=F', 'label': '近月', 'price': 96.5,
         'implied_rate_pct': 3.5, 'date': '2026-01-01', 'source': 'yfinance'},
        {'ticker': 'ZQH26.CBT', 'label': '2026年3月', 'price': 96.8,
         'implied_rate_pct': 3.2, 'date': '2026-01-01', 'source': 'yfinance'},
    ],
    'current_rates': {'DFF': {'name': '有效', 'value': 4.33, 'date': '2026-01-01'}},
    'real_economy': {}, 'rate_expectations': None,
}


def make_data_dir(base, with_global=True, with_macro=True, with_macro_old=True,
                  with_china=True, with_rate=True):
    d = Path(base)
    d.mkdir(parents=True, exist_ok=True)
    if with_global:
        _wjson(d / 'global_20260102.json', GLOBAL_DOC)
    if with_macro:
        _wjson(d / 'macro_20260102.json', MACRO_DOC)
    if with_macro_old:
        _wjson(d / 'macro_20260101.json', MACRO_DOC_OLD)
    if with_china:
        _wjson(d / 'china_20260102.json', CHINA_DOC)
    if with_rate:
        _wjson(d / 'rate_economy_20260102.json', RATE_DOC)
    # 非通道文件: 不入窗不解释
    _write(d / 'global_20260102.md', '# 全球资产数据 20260102\n')
    return d


def run_cli(*args):
    return subprocess.run([sys.executable, SCRIPT] + list(args),
                          capture_output=True, text=True)


class _AuditBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.reg = _wjson(os.path.join(self._tmp.name, 'registry.json'),
                          make_registry())
        self.data = make_data_dir(os.path.join(self._tmp.name, 'daily'))
        self.out = os.path.join(self._tmp.name, 'audit.json')
        r = run_cli('--registry', self.reg, '--data-dir',
                    str(self.data), '--out', self.out)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.rep = json.loads(Path(self.out).read_text(encoding='utf-8'))
        self.by_id = {m['metric_id']: m for m in self.rep['metrics']}

    def tearDown(self):
        self._tmp.cleanup()

    def newest(self, mid):
        files = self.by_id[mid]['files']
        self.assertTrue(files, '%s 应有窗口文件事实' % mid)
        return files[-1]


class TestMechanicalStates(_AuditBase):
    """M组+W组+X组+Y组: 四类可区分情形与窗口/派生/弃用档(真对照工具输出)。"""

    def test_m1_present_non_null_with_aliases(self):
        # 字段在且非空: 直名+两处别名(WTI→WTI_SPOT_M;GOLD→GOLD_F 的null形态见M2)
        self.assertEqual(self.by_id['SPX']['state'], 'PRESENT')
        self.assertEqual(self.newest('SPX')['value'], 6000.25)
        self.assertEqual(self.by_id['WTI_SPOT_M']['state'], 'PRESENT')
        self.assertEqual(self.newest('WTI_SPOT_M')['value'], 78.9)
        self.assertEqual(self.by_id['DFF']['state'], 'PRESENT')
        self.assertEqual(self.newest('DFF')['value'], 4.33)
        self.assertEqual(self.by_id['ZQ_F1_PRICE']['state'], 'PRESENT')
        self.assertEqual(self.newest('ZQ_F1_PRICE')['value'], 96.5)
        self.assertEqual(self.newest('ZQ_F1_PRICE')['observation_date'], '2026-01-01')
        self.assertEqual(self.by_id['HSI']['state'], 'PRESENT')
        self.assertEqual(self.by_id['SH_AMOUNT']['state'], 'PRESENT')
        self.assertEqual(self.newest('SH_AMOUNT')['value'], 6000.0)
        # CN_TOTAL_TURNOVER 主路径=sh+sz
        cn = self.by_id['CN_TOTAL_TURNOVER']
        self.assertEqual(cn['state'], 'PRESENT')
        self.assertEqual(cn['value'], 10000.0)
        self.assertEqual(cn.get('calc'), 'sh_amount_billion+sz_amount_billion')

    def test_m2_leaf_null_vs_path_null(self):
        # 字段在但null,两种机械形态须可区分:
        gold = self.by_id['GOLD_F']
        self.assertEqual(gold['state'], 'PRESENT_NULL')       # 叶键在,值为null
        self.assertIsNone(self.newest('GOLD_F').get('value'))
        sb = self.by_id['SB_FLOW']
        self.assertEqual(sb['state'], 'PATH_NULL')            # 途中节点southbound=null
        self.assertEqual(self.newest('SB_FLOW')['absent_key'], 'southbound')

    def test_m3_key_absent_with_collector_side_contrast(self):
        # 文件在而字段缺席: SHCOMP(容器空)、FED_FUNDS(键缺席)、
        # MARGIN_BAL/SH_PE(引擎期望键缺席而采集端成功键在场——映射断裂的机械对照)
        self.assertEqual(self.by_id['SHCOMP']['state'], 'KEY_ABSENT')
        self.assertEqual(self.newest('SHCOMP')['absent_key'], '000001.SH')
        self.assertEqual(self.by_id['FED_FUNDS']['state'], 'KEY_ABSENT')
        self.assertEqual(self.newest('FED_FUNDS')['absent_key'], 'FED_FUNDS')
        mg = self.by_id['MARGIN_BAL']
        self.assertEqual(mg['state'], 'KEY_ABSENT')
        self.assertEqual(self.newest('MARGIN_BAL')['absent_key'], 'balance')
        self.assertEqual(mg['files'][-1]['collector_success_keys'],
                         {'rzye': True, 'rqye': True, 'rzye_billion': True})
        pe = self.by_id['SH_PE']
        self.assertEqual(pe['state'], 'KEY_ABSENT')
        self.assertEqual(self.newest('SH_PE')['absent_key'], 'pe')
        probe = pe['files'][-1]['collector_side_codes']
        self.assertEqual(probe['container_keys'], ['000300.SH'])
        self.assertFalse(probe['has_000001SH'])
        self.assertEqual(probe['pe_ttm_values'], {'000300.SH': 12.3})

    def test_m4_file_absent(self):
        # 数据面缺席: 移除全部通道文件后各通道指标=FILE_ABSENT
        with tempfile.TemporaryDirectory() as tmp:
            empty = Path(tmp) / 'none'
            empty.mkdir()
            out = os.path.join(tmp, 'a.json')
            r = run_cli('--registry', self.reg, '--data-dir',
                        str(empty), '--out', out)
            self.assertEqual(r.returncode, 0, r.stderr)
            rep = json.loads(Path(out).read_text(encoding='utf-8'))
            by_id = {m['metric_id']: m for m in rep['metrics']}
            self.assertEqual(by_id['SPX']['state'], 'FILE_ABSENT')
            self.assertEqual(by_id['DFF']['state'], 'FILE_ABSENT')
            self.assertEqual(by_id['SHCOMP']['state'], 'FILE_ABSENT')
            # 单通道缺席不影响在场通道
            d2 = make_data_dir(os.path.join(tmp, 'only_global'),
                               with_macro=False, with_macro_old=False,
                               with_china=False, with_rate=False)
            out2 = os.path.join(tmp, 'a2.json')
            r2 = run_cli('--registry', self.reg, '--data-dir',
                         str(d2), '--out', out2)
            self.assertEqual(r2.returncode, 0, r2.stderr)
            rep2 = json.loads(Path(out2).read_text(encoding='utf-8'))
            by2 = {m['metric_id']: m for m in rep2['metrics']}
            self.assertEqual(by2['SPX']['state'], 'PRESENT')
            self.assertEqual(by2['HSI']['state'], 'FILE_ABSENT')
            self.assertEqual(by2['REAL_10Y']['state'], 'DERIVED_BLOCKED')

    def test_w_window_history_per_file(self):
        # 窗口多文件: 新档缺席而旧档在场,逐文件事实须如实(不因旧档在场而报PRESENT)
        ff = self.by_id['FED_FUNDS']
        self.assertEqual(len(ff['files']), 2)
        dates = [f['date'] for f in ff['files']]
        self.assertEqual(dates, ['20260101', '20260102'])      # 升序,新档在后
        self.assertEqual(ff['files'][0]['state'], 'PRESENT')
        self.assertEqual(ff['files'][0]['value'], 4.33)
        self.assertEqual(ff['state'], 'KEY_ABSENT')            # 以最新档定态

    def test_x_derived_and_deprecated(self):
        r10 = self.by_id['REAL_10Y']
        self.assertEqual(r10['mapping_kind'], 'dependency')
        self.assertEqual(r10['dep_states'],
                         {'UST_10Y': 'PRESENT', 'BEI_10Y': 'PRESENT'})
        self.assertEqual(r10['state'], 'DERIVED_READY')
        nm = self.by_id['NFP_MOM_K']
        self.assertEqual(nm['state'], 'DERIVED_READY')
        self.assertEqual(nm['dep_states'], {'NFP': 'PRESENT'})
        self.assertEqual(nm['dep_series_len_latest'], 2)
        rs = self.by_id['REAL_SHORT']
        self.assertEqual(rs['mapping_kind'], 'macro_derived_dict')
        self.assertEqual(rs['state'], 'PRESENT')
        self.assertEqual(rs['value'], 1.9)
        self.assertEqual(rs['registry_status'], 'deprecated')
        # 未知来源: 如实 MAPPING_UNRESOLVED,不猜测
        self.assertEqual(self.by_id['MYSTERY']['state'], 'MAPPING_UNRESOLVED')

    def test_summary_internal_consistency(self):
        # 汇总与逐指标事实互证(计数=逐条数出,不引用工具自报数当唯一证据)
        rep = self.rep
        states = [m['state'] for m in rep['metrics']]
        self.assertEqual(len(states), len(make_registry()['metrics']))
        for st in set(states):
            self.assertEqual(rep['summary']['state_counts'][st],
                             states.count(st), st)
        expect_non_present = sorted(
            m['metric_id'] for m in rep['metrics']
            if m['state'] not in ('PRESENT', 'DERIVED_READY'))
        self.assertEqual(sorted(rep['summary']['non_present']), expect_non_present)
        # 窗口文件: 4通道json入窗,md不入
        files = sorted(f['file'] for ch in rep['window']['by_channel'].values()
                       for f in ch)
        self.assertEqual(files, ['china_20260102.json', 'global_20260102.json',
                                 'macro_20260101.json', 'macro_20260102.json',
                                 'rate_economy_20260102.json'])
        self.assertEqual(rep['window']['ignored_nonchannel_json'], [])
        # registry 摘要
        self.assertEqual(rep['registry']['metric_count'],
                         len(make_registry()['metrics']))
        self.assertEqual(rep['registry']['status_counts']['active'], 20)
        self.assertEqual(rep['registry']['status_counts']['deprecated'], 1)


class TestExitSemantics(unittest.TestCase):
    """C组: 退出码语义——正常0,异常输入非0并报错(语义见 DELIVERY §用法)。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.reg = _wjson(os.path.join(self._tmp.name, 'registry.json'),
                          make_registry())
        self.data = make_data_dir(os.path.join(self._tmp.name, 'daily'))

    def tearDown(self):
        self._tmp.cleanup()

    def test_normal_exit_0_stdout_json(self):
        r = run_cli('--registry', self.reg, '--data-dir', str(self.data))
        self.assertEqual(r.returncode, 0, r.stderr)
        rep = json.loads(r.stdout)
        self.assertEqual(rep['schema_version'], 1)
        self.assertIn('generated_utc', rep)

    def test_missing_registry_exit_2(self):
        r = run_cli('--registry', os.path.join(self._tmp.name, 'nope.json'),
                    '--data-dir', str(self.data))
        self.assertEqual(r.returncode, 2)
        self.assertIn('不存在', r.stderr)

    def test_malformed_registry_json_exit_2(self):
        bad = _write(os.path.join(self._tmp.name, 'bad.json'), '{not json')
        r = run_cli('--registry', bad, '--data-dir', str(self.data))
        self.assertEqual(r.returncode, 2)
        self.assertIn('解析失败', r.stderr)

    def test_registry_without_metrics_exit_2(self):
        bad = _wjson(os.path.join(self._tmp.name, 'nometrics.json'),
                     {'version': 'x'})
        r = run_cli('--registry', bad, '--data-dir', str(self.data))
        self.assertEqual(r.returncode, 2)
        self.assertIn('metrics', r.stderr)

    def test_missing_data_dir_exit_2(self):
        r = run_cli('--registry', self.reg,
                    '--data-dir', os.path.join(self._tmp.name, 'missing_dir'))
        self.assertEqual(r.returncode, 2)
        self.assertIn('数据目录', r.stderr)

    def test_no_args_exit_2(self):
        r = run_cli()
        self.assertEqual(r.returncode, 2)
        self.assertTrue(r.stderr.strip())


class _DegradedBase(unittest.TestCase):
    """R组基类: 对被测源码文本做最小退化替换后 importlib 加载退化副本。"""

    _seq = 0

    def _load_degraded(self, replacements):
        _DegradedBase._seq += 1
        src = Path(SCRIPT).read_text(encoding='utf-8')
        for old, new in replacements:
            self.assertIn(old, src, '退化锚点不存在: %r' % old)
            src = src.replace(old, new)
        p = tempfile.NamedTemporaryFile(
            'w', suffix='_degraded_mca.py', delete=False, encoding='utf-8')
        p.write(src)
        p.close()
        spec = importlib.util.spec_from_file_location(
            'degraded_mca_%d' % _DegradedBase._seq, p.name)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod, p.name


class TestNegativeSensitivity(_DegradedBase):
    def _audit_fixture(self, mod):
        """同 fixture 小审计(registry+data 各一档),返回 {metric_id: state}。"""
        with tempfile.TemporaryDirectory() as tmp:
            reg = _wjson(os.path.join(tmp, 'registry.json'), make_registry())
            data = make_data_dir(os.path.join(tmp, 'daily'))
            rep = mod.build_audit(reg, str(data))
            return {m['metric_id']: m['state'] for m in rep['metrics']}

    def test_r1_null_blindness_detected(self):
        # 退化: 叶键null误报PRESENT(AC固定反例: null情形误报"非空可得"必须变红)。
        # 演示: 对退化版同款审计输出施加M2现有断言(assertEqual PRESENT_NULL)必raise。
        mod, path = self._load_degraded(
            [("    if node is None:\n        return ('PRESENT_NULL', None, path[-1])",
              "    if False:\n        return ('PRESENT_NULL', None, path[-1])")])
        try:
            states_ok = self._audit_fixture(mca)
            states_bad = self._audit_fixture(mod)
            # 正确版: 合成null叶 → PRESENT_NULL(M2断言在正确版上绿)
            self.assertEqual(states_ok['GOLD_F'], 'PRESENT_NULL')
            # 退化版: 同输入误报 PRESENT —— M2现有断言施加于退化输出必红
            self.assertEqual(states_bad['GOLD_F'], 'PRESENT')
            with self.assertRaises(AssertionError):
                self.assertEqual(states_bad['GOLD_F'], 'PRESENT_NULL')
        finally:
            os.unlink(path)

    def test_r2_path_null_vs_key_absent_separation(self):
        # 退化: 途中节点null被误判KEY_ABSENT(PATH_NULL/KEY_ABSENT两情形分离被破坏)
        mod, path = self._load_degraded([
            ("        if node is None:\n            return ('PATH_NULL', None, path[i - 1] if i else None)",
             "        if False:\n            return ('PATH_NULL', None, path[i - 1] if i else None)"),
            ("        if not isinstance(node, dict):\n            return ('PATH_NULL', None, key)",
             "        if not isinstance(node, dict):\n            return ('KEY_ABSENT', None, key)"),
        ])
        try:
            states_ok = self._audit_fixture(mca)
            states_bad = self._audit_fixture(mod)
            # 正确版: southbound=null→PATH_NULL; valuation{}无pe→KEY_ABSENT(两态分离)
            self.assertEqual(states_ok['SB_FLOW'], 'PATH_NULL')
            self.assertEqual(states_ok['SH_PE'], 'KEY_ABSENT')
            # 退化版: 途中null被吞成KEY_ABSENT —— M2现有断言施加于退化输出必红
            self.assertEqual(states_bad['SB_FLOW'], 'KEY_ABSENT')
            with self.assertRaises(AssertionError):
                self.assertEqual(states_bad['SB_FLOW'], 'PATH_NULL')
            # 分离破坏不影响SH_PE本就KEY_ABSENT的情形(退化仅吞并null态)
            self.assertEqual(states_bad['SH_PE'], 'KEY_ABSENT')
        finally:
            os.unlink(path)


if __name__ == '__main__':
    unittest.main(verbosity=2)
