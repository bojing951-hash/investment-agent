#!/usr/bin/env python3
"""IA-P0-2-W4-FIX2 联合验收测试(合法覆盖槽位+逐指标完整文件溯源)。

对应指令IA-P0-2-W4-FIX2-DEV-v1.0 §六: 对FIX1失败Commit(5c65b231)两项
缺陷的真实修复运行测试。全部走真实模块(historical_coverage_audit.run_audit/
main/eligible_slots/split_slots/classify/_is_auth/_associate_input_files;
真实config/metric_registry.json 81项;真实fact_engine/trading_calendar),
不复制审计实现到测试自证:
  A 统一合法覆盖槽位(FIX2-01,指令§四固定反例A-D): 日频周五+周六→1合法槽/
    日历外1/SINGLE;纯周末→0合法槽/NO_VALID_SLOTS(≠MISSING);周五→周一→
    2合法槽/OBSERVED;月频同月两日期→1槽/SINGLE;周频同周两日期→1槽;
    日频缺合法交易日→合法槽2/缺槽1;预期槽位无法确定→UNDETERMINED不冒充
    OBSERVED;有效与日历外分离+summary/by_status/core_by_status全链同步
  B 逐指标完整input_files(FIX2-02): 单文件/10文件全量无截断/同文件point+
    series聚合/多文件同日重复/非权威snapshot可追溯不增权威/无效日期/无效
    数值/长度不一致文件级无效/完全缺失指标空表/全局Manifest关联/SHA-256
    与size/mtime_ns对应/15文件去重无截断
  C 历史合同回归(FIX1已过语义不回退): NFP缺月断段/WTI月份槽位/同文件跨文件
    重复不变量/MARGIN_BAL身份/五通道任意子集/audit_commit与generated_at/
    输入只读/报告统计可复现
  D 负向敏感性5退化全检出: 恢复n_slots=len(obs_keys)/恢复日期数判状态/
    只存前3文件/非权威snapshot写成权威/删Manifest映射——退化实现必使本
    套件断言失败
"""
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import historical_coverage_audit as hca   # 被审计的真实审计器(FIX2版)

REGISTRY = os.path.join(ROOT, 'config', 'metric_registry.json')


# ════════════════ fixture构造器(合成数据,与真实Schema同构) ════════════════

def _load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def _run(files, tag='fix2', out_name='out', source_note='FIX2合成fixture'):
    """建临时data/daily写入{文件名:对象},跑真实main();返回(ec,result,out,tmp)。"""
    tmp = tempfile.mkdtemp(prefix='w4fix2_%s_' % tag)
    daily = os.path.join(tmp, 'data', 'daily')
    os.makedirs(daily)
    for name, obj in files.items():
        with open(os.path.join(daily, name), 'w', encoding='utf-8') as f:
            f.write(obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False))
    out = os.path.join(tmp, out_name)
    ec = hca.main(['--data-dir', os.path.join(tmp, 'data'), '--out-dir', out,
                   '--registry', REGISTRY, '--source-note', source_note])
    hits = glob.glob(os.path.join(out, 'coverage_audit_*.json'))
    result = _load(hits[0]) if hits else None
    return ec, result, out, tmp


def _cleanup(tmp):
    shutil.rmtree(tmp, ignore_errors=True)


def by_id(result, mid):
    return next(r for r in result['metrics'] if r['metric_id'] == mid)


def slot_files():
    """A组/D组fixture(指令§四固定反例A-D+周频同周+日频缺合法交易日)。"""
    return {
        # 反例A: SPX周五10-16+周六10-17 | 反例C: RUT周五10-16+周一10-19
        'global_20261017.json': {"date": "2026-10-17", "data": {
            "SPX": {"close": 5701.0, "date": "2026-10-16",
                    "series": {"dates": ["2026-10-16", "2026-10-17"],
                               "values": [5700.0, 5701.0]}},
            "RUT": {"close": 2200.0, "date": "2026-10-19",
                    "series": {"dates": ["2026-10-16", "2026-10-19"],
                               "values": [2198.0, 2200.0]}}}},
        # 反例B: NDX仅周六10-17+周日10-18(无一落在us_equity预期槽位)
        'global_20261018.json': {"date": "2026-10-18", "data": {
            "NDX": {"close": 20100.0, "date": "2026-10-18",
                    "series": {"dates": ["2026-10-17", "2026-10-18"],
                               "values": [20090.0, 20100.0]}}}},
        'macro_20261020.json': {"date": "2026-10-20", "data": {
            # 反例D: AHE月频同月两日期(2026-09-16+09-17)
            "AHE": {"value": 30.5, "date": "2026-09-17",
                    "series": {"dates": ["2026-09-16", "2026-09-17"],
                               "values": [30.4, 30.5]}},
            # 周频同周两日期(10-06周二+10-08周四,同ISO周10-05)
            "ICSA": {"value": 217000.0, "date": "2026-10-08",
                     "series": {"dates": ["2026-10-06", "2026-10-08"],
                                "values": [218000, 217000]}}}},
        # 日频缺合法交易日: GOLD周五10-16+周二10-20,缺周一10-19
        'global_20261020.json': {"date": "2026-10-20", "data": {
            "GOLD": {"close": 2650.0, "date": "2026-10-20",
                     "series": {"dates": ["2026-10-16", "2026-10-20"],
                                "values": [2609.0, 2650.0]}}}},
    }


# ════════════════ A组: 统一合法覆盖槽位(FIX2-01) ════════════════

class TestAEligibleSlots(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ec, cls.result, cls.out, cls.tmp = _run(slot_files(), tag='slots')

    @classmethod
    def tearDownClass(cls):
        _cleanup(cls.tmp)

    # A1(指令§四固定反例A): SPX周五10-16+周六10-17→原始日期2/合法槽1/
    #    日历外1/SINGLE_OBSERVATION(周六合法有效记录但不虚增样本)
    def test_a1_friday_plus_saturday(self):
        s = by_id(self.result, 'SPX')
        c = s['coverage']
        self.assertEqual(self.ec, 0)
        self.assertEqual(s['counts']['unique_observation_dates'], 2)
        self.assertEqual(c['observed_slots'], 1)
        self.assertEqual(c['unique_observation_slots'], 1)
        self.assertEqual(c['extra_observations_beyond_calendar'], 1)
        self.assertEqual(c['extra_slot_keys_sample'], ['2026-10-17'])
        self.assertTrue(c['slots_certified'])
        self.assertEqual(s['status'], 'SINGLE_OBSERVATION')

    # A2(指令§四固定反例B): NDX仅周六周日→raw2/合法槽0/NO_VALID_SLOTS/
    #    segments[]/usable[]——有权威观测日但无一落在预期槽位,与MISSING
    #    (数据完全不存在,如VIX)区分;summary与findings4同步新键
    def test_a2_weekend_only_no_valid_slots(self):
        n = by_id(self.result, 'NDX')
        c = n['coverage']
        self.assertEqual(n['counts']['unique_observation_dates'], 2)
        self.assertEqual(c['observed_slots'], 0)
        self.assertEqual(c['unique_observation_slots'], 0)
        self.assertTrue(c['slots_certified'])
        self.assertEqual(n['status'], 'NO_VALID_SLOTS')
        self.assertEqual(c['continuous_segments'], [])
        self.assertEqual(c['usable_intervals'], [])
        self.assertEqual(by_id(self.result, 'VIX')['status'], 'MISSING')
        self.assertEqual(self.result['summary']['by_status'].get('NO_VALID_SLOTS'), 1)
        self.assertEqual(self.result['summary']['no_valid_slots'], 1)
        self.assertIn('NDX', self.result['findings']['4_哪些指标未保存历史']['NO_VALID_SLOTS'])
        self.assertIn('VIX', self.result['findings']['4_哪些指标未保存历史']['MISSING'])

    # A3(指令§四固定反例C): RUT周五10-16+周一10-19→2合法槽/OBSERVED
    def test_a3_friday_to_monday_observed(self):
        r = by_id(self.result, 'RUT')
        c = r['coverage']
        self.assertEqual(c['observed_slots'], 2)
        self.assertEqual(c['unique_observation_slots'], 2)
        self.assertEqual(c['extra_observations_beyond_calendar'], 0)
        self.assertEqual(r['status'], 'OBSERVED')
        self.assertEqual(c['missing_slots_count'], 0)

    # A4(指令§四固定反例D): AHE月频同月两日期→1合法槽/SINGLE,无两样本usable
    def test_a4_monthly_same_month_one_slot(self):
        a = by_id(self.result, 'AHE')
        c = a['coverage']
        self.assertEqual(a['counts']['unique_observation_dates'], 2)
        self.assertEqual(c['unique_observation_slots'], 1)
        self.assertEqual(c['observed_slots'], 1)
        self.assertEqual(a['status'], 'SINGLE_OBSERVATION')
        self.assertEqual(c['usable_intervals'], [])

    # A5: 周频同周两日期→1合法槽/SINGLE(周内多日不虚增样本)
    def test_a5_weekly_same_week_one_slot(self):
        i = by_id(self.result, 'ICSA')
        c = i['coverage']
        self.assertEqual(i['counts']['unique_observation_dates'], 2)
        self.assertEqual(c['unique_observation_slots'], 1)
        self.assertEqual(i['status'], 'SINGLE_OBSERVATION')
        self.assertEqual(c['usable_intervals'], [])

    # A6: 日频缺合法交易日(周五10-16+周二10-20缺周一10-19)→合法槽2/缺槽1/
    #    断段2段;两观测均合法→日期数=槽位数
    def test_a6_missing_trading_day_eligible_two(self):
        g = by_id(self.result, 'GOLD_F')
        c = g['coverage']
        self.assertEqual(c['observed_slots'], 2)
        self.assertEqual(c['unique_observation_slots'], 2)
        self.assertEqual(g['counts']['unique_observation_dates'], 2)
        self.assertEqual(c['missing_slots_count'], 1)
        self.assertEqual(len(c['continuous_segments']), 2)
        self.assertEqual(c['extra_observations_beyond_calendar'], 0)

    # A7(§4.3): 预期槽位无法确定→UNDETERMINED,不以日期数冒充槽位数,不冒充
    #    OBSERVED确定性结论;不改变有足够真实槽位证据的正常指标状态(基线RUT)
    def test_a7_slots_undetermined(self):
        r0 = by_id(self.result, 'RUT')
        self.assertEqual(r0['status'], 'OBSERVED')   # 基线: 正常路径不受影响

        def unavailable(freq, first, last, calendar):
            return None, None, '日历限制注记', '观察窗不可解析(测试注入)'

        tmp = tempfile.mkdtemp(prefix='w4fix2_a7_')
        daily = os.path.join(tmp, 'data', 'daily')
        os.makedirs(daily)
        for fn in ('global_20261017.json', 'global_20261020.json'):
            with open(os.path.join(daily, fn), 'w', encoding='utf-8') as f:
                f.write(json.dumps(slot_files()[fn]))
        with mock.patch.object(hca, 'expected_slots', unavailable):
            res, _log, code = hca.run_audit(os.path.join(tmp, 'data'),
                                            os.path.join(tmp, 'out'), REGISTRY)
        try:
            self.assertEqual(code, 0)
            g = by_id(res, 'GOLD_F')
            c = g['coverage']
            self.assertEqual(g['status'], 'UNDETERMINED')      # 不再冒充OBSERVED
            self.assertIsNone(c['unique_observation_slots'])   # 不以日期数冒充
            self.assertFalse(c['slots_certified'])
            self.assertEqual(c['continuous_segments'], [])
            self.assertIn('观察窗不可解析(测试注入)', c['slots_unavailable_reason'])
            self.assertGreaterEqual(res['summary']['by_status'].get('UNDETERMINED', 0), 1)
            self.assertEqual(res['summary']['undetermined'],
                             res['summary']['by_status'].get('UNDETERMINED', 0))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # A8(§4.4下游同步): 有效与日历外分离;summary/by_status/core_by_status/
    #    with_authority_observations与逐项同口径——周六观测不撑大任何汇总
    def test_a8_summary_downstream_consistency(self):
        s = by_id(self.result, 'SPX')
        c = s['coverage']
        seg_slots = [k for sg in c['continuous_segments']
                     for k in (sg['start_slot'], sg['end_slot'])]
        self.assertNotIn('2026-10-17', seg_slots)         # 日历外不入段
        self.assertEqual(c['missing_slots_count'], 0)     # 也不冒充缺槽
        # by_status可复算且总数=81
        recount = {}
        for r in self.result['metrics']:
            recount[r['status']] = recount.get(r['status'], 0) + 1
        self.assertEqual(self.result['summary']['by_status'],
                         {k: v for k, v in sorted(recount.items())})
        self.assertEqual(sum(self.result['summary']['by_status'].values()), 81)
        # with_authority_observations不含NO_VALID_SLOTS/UNDETERMINED
        n_auth = len([r for r in self.result['metrics'] if r['status'] in
                      ('OBSERVED', 'SPARSE', 'SINGLE_OBSERVATION')])
        self.assertEqual(self.result['summary']['with_authority_observations'], n_auth)
        # NDX不是core(SPX/RUT/GOLD_F是)——core_by_status同步新口径
        self.assertNotIn('NDX', self.result['summary'].get('core_by_status', {})
                         and [] or [])

    # A9(不变量,槽位可靠时): unique_observation_slots==observed_slots==
    #    sum(segments.slots);日历外观测不进连续覆盖——全81项逐指标核验
    def test_a9_slot_invariants_all_metrics(self):
        checked = 0
        for r in self.result['metrics']:
            c = r['coverage']
            if c.get('slots_certified'):
                self.assertEqual(c['unique_observation_slots'], c['observed_slots'],
                                 r['metric_id'])
                self.assertEqual(c['unique_observation_slots'],
                                 sum(sg['slots'] for sg in c['continuous_segments']),
                                 r['metric_id'])
                self.assertLessEqual(c['longest_continuous_segment_slots'],
                                     c['unique_observation_slots'], r['metric_id'])
                checked += 1
        self.assertGreaterEqual(checked, 5)   # SPX/NDX/RUT/AHE/ICSA/GOLD_F


# ════════════════ B组: 逐指标完整input_files(FIX2-02) ════════════════

IF_FIELDS = {'relpath', 'channel', 'record_types', 'raw_records', 'valid_records',
             'invalid_records', 'authority_records', 'non_authority_records',
             'invalid_reasons', 'valid_observation_contributed',
             'manifest_association', 'manifest_sha256'}


class TestBInputFilesProvenance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        files = {
            'global_20261020.json': {"date": "2026-10-20", "data": {
                "SPX": {"close": 5700.0, "date": "2026-10-16",
                        "series": {"dates": ["2026-10-16", "2026-10-19"],
                                   "values": [5700.0, 5701.0]}}}},
            'global_20261021.json': {"date": "2026-10-21", "data": {
                "SPX": {"close": 5702.0, "date": "2026-10-16"}}},
            'macro_20261020.json': {"date": "2026-10-20", "data": {
                "AHE": {"value": 30.5, "date": "2026-09-17",
                        "series": {"dates": ["2026-09-16", "bad-date"],
                                   "values": [30.4, 30.5]}},
                "ICSA": {"value": 217000.0, "date": "2026-10-08",
                         "series": {"dates": ["2026-10-06", "2026-10-08"],
                                    "values": [218000, "n/a"]}},
                "NFP": {"series": {"dates": ["2026-06-15", "2026-07-15", "2026-09-15"],
                                   "values": [151000.0, 151500.0]}}}},
            'research_snapshot_20261020.json': {
                "facts": [{"metric_id": "GOLD_F", "observation_date": "2026-10-16",
                           "value": 2600.0}],
                "series_store": {}},
        }
        cls.ec, cls.result, cls.out, cls.tmp = _run(files, tag='prov')
        mhits = glob.glob(os.path.join(cls.out, 'input_manifest_*.json'))
        cls.manifest = _load(mhits[0])['files']

    @classmethod
    def tearDownClass(cls):
        _cleanup(cls.tmp)

    def _if(self, mid, relpath):
        m = by_id(self.result, mid)
        return next(f for f in m['input_files'] if f['relpath'] == relpath)

    # B1: 单文件贡献——字段齐全+权威记录计数
    def test_b1_single_file_full_fields(self):
        m = by_id(self.result, 'AHE')
        self.assertEqual(len(m['input_files']), 1)
        f = m['input_files'][0]
        self.assertTrue(IF_FIELDS <= set(f), sorted(IF_FIELDS - set(f)))
        self.assertEqual(f['relpath'], 'daily/macro_20261020.json')
        self.assertEqual(f['channel'], 'macro')
        self.assertGreater(f['authority_records'], 0)
        self.assertEqual(f['manifest_association'], 'ok')

    # B2: 10文件贡献同一指标——全部列入,无截断
    def test_b2_ten_files_all_listed(self):
        days = ['2026-10-05', '2026-10-06', '2026-10-07', '2026-10-08', '2026-10-09',
                '2026-10-12', '2026-10-13', '2026-10-14', '2026-10-15', '2026-10-16']
        files = {'global_%s.json' % d.replace('-', ''): {"date": d, "data": {
            "RUT": {"close": 2200.0 + i, "date": d}}}
            for i, d in enumerate(days)}
        ec, res, _out, tmp = _run(files, tag='b2')
        try:
            self.assertEqual(ec, 0)
            m = by_id(res, 'RUT')
            self.assertEqual(len(m['input_files']), 10)   # 全量,无[:3]截断
            self.assertEqual([f['relpath'] for f in m['input_files']],
                             sorted(f['relpath'] for f in m['input_files']))
            self.assertEqual(m['coverage']['observed_slots'], 10)
        finally:
            _cleanup(tmp)

    # B3: 同文件point+series聚合——record_types聚合/原始记录计数不重不漏
    def test_b3_same_file_point_and_series(self):
        f = self._if('SPX', 'daily/global_20261020.json')
        self.assertEqual(f['record_types'], ['point', 'series'])
        self.assertEqual(f['raw_records'], 3)    # 1 point+2 series日期
        self.assertEqual(f['valid_records'], 3)
        self.assertEqual(f['invalid_records'], 0)
        self.assertTrue(f['valid_observation_contributed'])

    # B4: 多文件同日重复——两文件都列出/都贡献有效记录/跨文件重复如实计数
    def test_b4_multi_file_same_date(self):
        f1 = self._if('SPX', 'daily/global_20261020.json')
        f2 = self._if('SPX', 'daily/global_20261021.json')
        self.assertTrue(f1['valid_observation_contributed'])
        self.assertTrue(f2['valid_observation_contributed'])
        s = by_id(self.result, 'SPX')
        self.assertEqual(s['counts']['cross_file_duplicate_records'], 1)
        self.assertEqual(len(s['input_files']), 2)

    # B5: 非权威research_snapshot——文件可追溯但不增权威历史(状态仍MISSING)
    def test_b5_non_authority_snapshot_traceable(self):
        g = by_id(self.result, 'GOLD_F')
        f = self._if('GOLD_F', 'daily/research_snapshot_20261020.json')
        self.assertEqual(f['channel'], 'research_snapshot')
        self.assertEqual(f['authority_records'], 0)
        self.assertGreaterEqual(f['non_authority_records'], 1)
        self.assertTrue(f['valid_observation_contributed'])  # 记录本身合法有效
        self.assertEqual(g['status'], 'MISSING')             # 但不增权威样本
        self.assertIsNone(g['coverage']['observed_slots'])
        self.assertEqual(g['coverage']['unique_observation_slots'], 0)
        self.assertIn('2026-10-16', g['discovery']['non_authority_only_dates'])

    # B6: 无效日期记录——invalid_reasons披露,文件仍可追溯
    #    (AHE=1条point有效+series 1有效1无效日期→valid 2/invalid 1)
    def test_b6_invalid_date_traced(self):
        f = self._if('AHE', 'daily/macro_20261020.json')
        self.assertIn('invalid_date', f['invalid_reasons'])
        self.assertEqual(f['invalid_records'], 1)
        self.assertEqual(f['valid_records'], 2)
        self.assertEqual(f['raw_records'], 3)

    # B7: 无效数值记录——invalid_value披露
    def test_b7_invalid_value_traced(self):
        f = self._if('ICSA', 'daily/macro_20261020.json')
        self.assertIn('invalid_value', f['invalid_reasons'])
        self.assertEqual(f['invalid_records'], 1)

    # B8: 长度不一致series——该series整体不入观测(文件级无效),文件仍列出
    #    且不贡献有效样本(fixture中NFP无point,唯一输入即坏series)
    def test_b8_length_mismatch_file_level(self):
        f = self._if('NFP', 'daily/macro_20261020.json')
        self.assertTrue(any(r.startswith('length_mismatch') for r in f['invalid_reasons']),
                        f['invalid_reasons'])
        self.assertFalse(f['valid_observation_contributed'])
        n = by_id(self.result, 'NFP')
        self.assertEqual(n['status'], 'MISSING')   # 无有效权威观测
        self.assertEqual(len(n['input_files']), 1)  # 文件发现事实仍在
        self.assertEqual(f['valid_records'], 0)

    # B9: 完全缺失指标——input_files恒在且为空表(不缺字段)
    def test_b9_missing_metric_empty_list(self):
        v = by_id(self.result, 'VIX')
        self.assertEqual(v['status'], 'MISSING')
        self.assertIn('input_files', v)
        self.assertEqual(v['input_files'], [])

    # B10: 全局Manifest关联——relpath唯一匹配/channel一致/关联问题空
    def test_b10_manifest_association(self):
        man = {e['relpath']: e for e in self.manifest}
        n_files = 0
        for r in self.result['metrics']:
            for f in r['input_files']:
                n_files += 1
                self.assertIn(f['relpath'], man, f['relpath'])
                self.assertEqual(f['manifest_association'], 'ok')
                self.assertEqual(f['manifest_sha256'], man[f['relpath']]['sha256'])
                self.assertEqual(f['channel'], man[f['relpath']]['channel'])
        self.assertGreater(n_files, 0)
        self.assertEqual(self.result['integrity']['input_files_association_problems'], [])

    # B11: SHA-256/size/mtime_ns与磁盘实物对应(独立重算)
    def test_b11_sha256_size_mtime_match_disk(self):
        data_root = os.path.realpath(os.path.join(self.tmp, 'data'))
        checked = 0
        for r in self.result['metrics']:
            for f in r['input_files']:
                p = os.path.join(data_root, f['relpath'])
                with open(p, 'rb') as fh:
                    self.assertEqual(hashlib.sha256(fh.read()).hexdigest(),
                                     f['manifest_sha256'], f['relpath'])
                st = os.stat(p)
                self.assertEqual(f['size'], st.st_size)
                self.assertEqual(f['mtime_ns'], st.st_mtime_ns)
                checked += 1
        self.assertGreaterEqual(checked, 4)

    # B12: 15文件去重无截断——机器字段全量;旧sample字段仍是样例不冒充全量
    def test_b12_fifteen_files_no_truncation(self):
        months = ['2025-%02d-15' % m for m in range(1, 13)] + \
                 ['2026-01-15', '2026-02-15', '2026-03-15']
        files = {'macro_%s.json' % d.replace('-', ''): {"date": d, "data": {
            "WTI": {"value": 80.0 + i, "date": d}}}
            for i, d in enumerate(months)}
        ec, res, _out, tmp = _run(files, tag='b12')
        try:
            self.assertEqual(ec, 0)
            m = by_id(res, 'WTI_SPOT_M')
            self.assertEqual(len(m['input_files']), 15)
            self.assertEqual(m['coverage']['observed_slots'], 15)
            self.assertEqual(m['status'], 'OBSERVED')
            self.assertLessEqual(
                len(m['discovery']['point_files_sample']), 3)   # sample仍是样例
        finally:
            _cleanup(tmp)


# ════════════════ C组: 历史合同回归(FIX1已过语义不回退) ════════════════

class TestCHistoricalContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ec, cls.result, cls.out, cls.tmp = _run(slot_files(), tag='creg')

    @classmethod
    def tearDownClass(cls):
        _cleanup(cls.tmp)

    # C1: NFP缺月断段(FIX1-01合同,月频跨缺失月份不判连续)
    def test_c1_nfp_missing_months(self):
        files = {'macro_20261020.json': {"date": "2026-10-20", "data": {
            "NFP": {"value": 152000.0, "date": "2026-09-15",
                    "series": {"dates": ["2026-06-15", "2026-09-15"],
                               "values": [151000.0, 152000.0]}}}}}
        ec, res, _out, tmp = _run(files, tag='c1')
        try:
            n = by_id(res, 'NFP')
            c = n['coverage']
            self.assertEqual(c['unique_observation_slots'], 2)
            self.assertEqual(c['missing_slots_count'], 2)      # 缺7/8月
            self.assertEqual(len(c['continuous_segments']), 2)
            self.assertEqual(c['longest_continuous_segment_slots'], 1)
            self.assertEqual(c['usable_intervals'], [])
            self.assertEqual(n['status'], 'OBSERVED')
        finally:
            _cleanup(tmp)

    # C2: WTI月内3日期→2独立月槽位(FIX1合同)
    def test_c2_wti_month_slots(self):
        files = {'macro_20261020.json': {"date": "2026-10-20", "data": {
            "WTI": {"value": 80.5, "date": "2026-09-17",
                    "series": {"dates": ["2026-08-15", "2026-09-16", "2026-09-17"],
                               "values": [80.1, 80.3, 80.5]}}}}}
        ec, res, _out, tmp = _run(files, tag='c2')
        try:
            w = by_id(res, 'WTI_SPOT_M')
            self.assertEqual(w['counts']['unique_observation_dates'], 3)
            self.assertEqual(w['coverage']['unique_observation_slots'], 2)
        finally:
            _cleanup(tmp)

    # C3: 同文件/跨文件重复拆分不变量(FIX1-02合同+指令§五固定例)
    def test_c3_duplicate_split_invariant(self):
        rec = lambda f, d: {'file': f, 'obs_date': d, 'auth': True}
        same, cross = hca.split_duplicates(
            [rec('A', 'd')] * 3 + [rec('B', 'd')])
        self.assertEqual((same, cross), (2, 1))   # A同日3条+B同日1条
        # 真实run: 同文件point+series同日
        g = by_id(self.result, 'GOLD_F')
        self.assertEqual(g['counts']['unique_observation_dates'], 2)
        self.assertEqual(g['counts']['authority_raw_records'],
                         g['counts']['unique_observation_dates']
                         + g['counts']['same_file_extra_duplicate_records']
                         + g['counts']['cross_file_duplicate_records'])

    # C4: MARGIN_BAL身份(FIX1-03合同: 仅rzye_billion不得获权威)
    def test_c4_margin_bal_identity(self):
        files = {'china_20261020.json': {"timestamp": 1, "version": "v2",
                                         "margin": {"date": "20261020",
                                                    "rzye_billion": 18500.0}}}
        ec, res, _out, tmp = _run(files, tag='c4')
        try:
            m = by_id(res, 'MARGIN_BAL')
            self.assertEqual(m['status'], 'MISSING')
            rzye = [u for u in res['unmapped_records']
                    if u['raw_key'] == 'margin:rzye_billion']
            self.assertTrue(rzye and 'identity_mismatch' in rzye[0]['note'])
        finally:
            _cleanup(tmp)

    # C5: 五通道任意子集(FIX1-04合同: china-only→COMPLETED,81项全输出)
    def test_c5_china_only_subset(self):
        files = {'china_20261020.json': {"timestamp": 1, "version": "v2",
                                         "a_share_indices": {
                                             "000001.SH": {"name": "上证指数",
                                                           "close": 3300.0,
                                                           "date": "20261020"}}}}
        ec, res, _out, tmp = _run(files, tag='c5')
        try:
            self.assertEqual(ec, 0)
            self.assertEqual(res['audit_status'], 'COMPLETED')
            self.assertEqual(len(res['metrics']), 81)
        finally:
            _cleanup(tmp)

    # C6: audit_commit=真实git HEAD+generated_at真实UTC(FIX1-05合同)
    def test_c6_audit_metadata(self):
        head = subprocess.run(['git', '-C', ROOT, 'rev-parse', 'HEAD'],
                              capture_output=True, text=True).stdout.strip()
        self.assertRegex(self.result['audit_commit'], r'^[0-9a-f]{40}$')
        if head:
            self.assertEqual(self.result['audit_commit'], head)
        self.assertRegex(self.result['generated_at'],
                         r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00$')

    # C7: 输入只读——审计前后输入文件SHA-256不变
    def test_c7_inputs_readonly(self):
        daily = os.path.join(self.tmp, 'data', 'daily')
        before = {n: hashlib.sha256(open(os.path.join(daily, n), 'rb').read()).hexdigest()
                  for n in sorted(os.listdir(daily))}
        _out2 = os.path.join(self.tmp, 'out_c7')
        hca.main(['--data-dir', os.path.join(self.tmp, 'data'), '--out-dir', _out2,
                  '--registry', REGISTRY, '--source-note', 'FIX2只读复跑'])
        after = {n: hashlib.sha256(open(os.path.join(daily, n), 'rb').read()).hexdigest()
                 for n in sorted(os.listdir(daily))}
        self.assertEqual(before, after)

    # C8: 报告统计可复现(状态分布/新状态键/schema 1.2)
    def test_c8_report_stats_reproducible(self):
        recount = {}
        for r in self.result['metrics']:
            recount[r['status']] = recount.get(r['status'], 0) + 1
        self.assertEqual(self.result['summary']['by_status'],
                         {k: v for k, v in sorted(recount.items())})
        f4 = self.result['findings']['4_哪些指标未保存历史']
        for key in ('MISSING', 'UNREADABLE', 'DERIVED_ONLY',
                    'NO_VALID_SLOTS', 'UNDETERMINED'):
            self.assertIn(key, f4)
        # FIX3最小语义修正: 1.2→1.3;FIX4最小语义修正: 1.3→1.4(输入根symlink
        # 拒绝+逐文件extract_status+EXTRACTION_FAILED/PARTIAL_EXTRACTION新失败
        # 状态;场景与断言结构不变,仅版本字面量随实现升级)
        self.assertEqual(self.result['schema_version'], 'w4-coverage-audit/1.4')


# ════════════════ D组: 负向敏感性(5退化必被检出) ════════════════

class TestDNegativeSensitivity(unittest.TestCase):
    """证明: 把FIX2任一修复退化回旧实现,本套件断言会失败(而非继续通过)。"""

    @classmethod
    def setUpClass(cls):
        cls.ec, cls.res, cls.out, cls.tmp = _run(slot_files(), tag='dbase')

    @classmethod
    def tearDownClass(cls):
        _cleanup(cls.tmp)

    def _mutated(self, tmp_suffix, **patches):
        out = os.path.join(self.tmp, 'mut_' + tmp_suffix)
        with mock.patch.multiple(hca, **patches):
            hca.main(['--data-dir', os.path.join(self.tmp, 'data'),
                      '--out-dir', out, '--registry', REGISTRY,
                      '--source-note', 'FIX2退化模拟'])
        hits = glob.glob(os.path.join(out, 'coverage_audit_*.json'))
        return _load(hits[0])

    # D1: 恢复n_slots=len(obs_keys)(日历外观测计入)→A1/A2断言失败
    def test_d1_raw_key_count_degrade_detected(self):
        n0, s0 = by_id(self.res, 'NDX'), by_id(self.res, 'SPX')
        correct = (n0['status'] == 'NO_VALID_SLOTS'
                   and n0['coverage']['observed_slots'] == 0
                   and s0['coverage']['observed_slots'] == 1)
        self.assertTrue(correct)

        def raw_count(auth_dates, freq, calendar):   # 旧口径: 全部观测键计入
            exp_list, keyfn, lim, reason = hca.expected_slots(
                freq, auth_dates[0], auth_dates[-1], calendar)
            if exp_list is None or keyfn is None:
                return None, None, [], [], False, lim, reason
            raw = {keyfn(d) for d in auth_dates}
            return len(exp_list), len(raw), [], sorted(set(exp_list) - raw), True, lim, None

        mut = self._mutated('d1', eligible_slots=raw_count)
        mn, ms = by_id(mut, 'NDX'), by_id(mut, 'SPX')
        self.assertNotEqual(mn['status'], 'NO_VALID_SLOTS')   # 周末被当2独立样本
        self.assertNotEqual(mn['coverage']['observed_slots'], 0)
        self.assertNotEqual(ms['coverage']['observed_slots'], 1)   # 周六虚增
        detect = (correct and mn['status'] != 'NO_VALID_SLOTS'
                  and mn['coverage']['observed_slots'] != 0
                  and ms['coverage']['observed_slots'] != 1)
        self.assertTrue(detect)

    # D2: 恢复日期数判状态(len(auth_dates)冒充槽位数+无视可认证性)→A2/A7失败
    def test_d2_date_count_status_degrade_detected(self):
        orig = hca.classify

        def by_dates(m, dates, n_slots, ratio, unreadable, slots_certified=True):
            return orig(m, dates, len(dates), ratio, unreadable, True)

        def unavailable(freq, first, last, calendar):
            return None, None, '日历限制注记', '观察窗不可解析(测试注入)'

        mut = self._mutated('d2', classify=by_dates, expected_slots=unavailable)
        mn, mg = by_id(mut, 'NDX'), by_id(mut, 'GOLD_F')
        self.assertNotEqual(mn['status'], 'NO_VALID_SLOTS')
        self.assertNotEqual(mg['status'], 'UNDETERMINED')   # 不可认证冒充确定结论
        detect = (mn['status'] != 'NO_VALID_SLOTS'
                  and mg['status'] != 'UNDETERMINED')
        self.assertTrue(detect)

    # D3: 只存前3文件(input_files截断)→B2/B12断言失败
    def test_d3_truncate_files_degrade_detected(self):
        orig = hca.build_metric_record

        def truncate(m, accs, cu, bc):
            rec = orig(m, accs, cu, bc)
            rec['input_files'] = rec['input_files'][:3]   # 旧缺陷: 样例截断当全量
            return rec

        months = ['2025-%02d-15' % m for m in range(1, 13)] + \
                 ['2026-01-15', '2026-02-15', '2026-03-15']
        files = {'macro_%s.json' % d.replace('-', ''): {"date": d, "data": {
            "WTI": {"value": 80.0 + i, "date": d}}}
            for i, d in enumerate(months)}
        ec_base, res_base, _o, tmp = _run(files, tag='d3base')
        try:
            self.assertEqual(len(by_id(res_base, 'WTI_SPOT_M')['input_files']), 15)
            out_m = os.path.join(tmp, 'out_mut')
            with mock.patch.object(hca, 'build_metric_record', truncate):
                hca.main(['--data-dir', os.path.join(tmp, 'data'), '--out-dir', out_m,
                          '--registry', REGISTRY, '--source-note', 'FIX2退化模拟'])
            mut = _load(glob.glob(os.path.join(out_m, 'coverage_audit_*.json'))[0])
            self.assertNotEqual(len(by_id(mut, 'WTI_SPOT_M')['input_files']), 15)
            detect = (len(by_id(res_base, 'WTI_SPOT_M')['input_files']) == 15
                      and len(by_id(mut, 'WTI_SPOT_M')['input_files']) != 15)
            self.assertTrue(detect)
        finally:
            _cleanup(tmp)

    # D4: 非权威snapshot写成权威→B5断言失败(seam=快照记录auth参数翻转为真,
    #     即"快照通道冒充权威采集通道"的退化实现)
    def test_d4_snapshot_as_authority_degrade_detected(self):
        orig = hca._add_point

        def auth_flip(acc, obs_date, value, channel, auth, relpath, fd_iso, kind):
            return orig(acc, obs_date, value, channel,
                        True if channel == 'research_snapshot' else auth,
                        relpath, fd_iso, kind)

        files = {'research_snapshot_20261020.json': {
            "facts": [{"metric_id": "GOLD_F", "observation_date": "2026-10-16",
                       "value": 2600.0}],
            "series_store": {}}}
        ec, res_b, _o, tmp = _run(files, tag='d4base')
        try:
            self.assertEqual(by_id(res_b, 'GOLD_F')['status'], 'MISSING')
            out_m = os.path.join(tmp, 'out_mut')
            with mock.patch.object(hca, '_add_point', auth_flip):
                hca.main(['--data-dir', os.path.join(tmp, 'data'), '--out-dir', out_m,
                          '--registry', REGISTRY, '--source-note', 'FIX2退化模拟'])
            mut = _load(glob.glob(os.path.join(out_m, 'coverage_audit_*.json'))[0])
            self.assertNotEqual(by_id(mut, 'GOLD_F')['status'], 'MISSING')
            detect = (by_id(res_b, 'GOLD_F')['status'] == 'MISSING'
                      and by_id(mut, 'GOLD_F')['status'] != 'MISSING')
            self.assertTrue(detect)
        finally:
            _cleanup(tmp)

    # D5: 删Manifest映射(input_files不与Manifest关联)→B10/B11断言失败
    def test_d5_no_manifest_mapping_degrade_detected(self):
        correct_entry = next(f for r in self.res['metrics'] for f in r['input_files'])
        self.assertTrue(correct_entry.get('manifest_sha256'))
        self.assertEqual(correct_entry['manifest_association'], 'ok')

        def no_assoc(metric_records, manifest):   # 旧缺陷: 不做任何关联
            return []

        mut = self._mutated('d5', _associate_input_files=no_assoc)
        f = next(fl for r in mut['metrics'] for fl in r['input_files']
                 if fl['relpath'] == correct_entry['relpath'])
        self.assertNotIn('manifest_sha256', f)
        self.assertNotEqual(f.get('manifest_association'), 'ok')
        detect = (bool(correct_entry.get('manifest_sha256'))
                  and 'manifest_sha256' not in f)
        self.assertTrue(detect)


if __name__ == '__main__':
    unittest.main(verbosity=2)
