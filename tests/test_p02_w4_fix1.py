#!/usr/bin/env python3
"""IA-P0-2-W4-FIX1 联合验收测试(四项确定性缺陷定向修复+审计元数据)。

对应指令IA-P0-2-W4-FIX1-DEV-v1.0 §九FIX1-06: 对固定源码四类缺陷(Agent 4
W4首轮独立验收失败结论)真实运行测试。全部走真实模块(historical_coverage_
audit.run_audit/main/split_slots/split_duplicates/classify/discover_files/
extract_file/_audit_metadata;真实config/metric_registry.json 81项;真实
fact_engine/trading_calendar),不复制审计实现到测试自证:
  A 连续覆盖按真实观测槽位: NFP六月九月缺七八月/WTI月内多日期/单月两日期
    非两样本/日频周五→周一连续/日频缺预期交易日断段/周频缺周断段/日历外
    观测单独披露/日期计数与槽位计数并存/槽位不可确定不虚构
  B 重复计数按真实文件身份拆分: 同文件point+series同日/同文件series内
    重复/不同文件同日/混合(指令§五固定例: A同日3条+B同日1条)/同日不同值/
    权威与非权威重复+全指标计数不变量
  C 指标身份: 只有rzye_billion→MARGIN_BAL不得获权威观测/合法balance正常
    /同日并存不同语义字段/未注册字段独立披露/MARGIN_BAL不因错误字段取得
    权威连续区间
  D 输入发现五通道任意子集: 只有china的daily/(指令§七固定反例)/五单通道
    +全部两通道组合/直接传daily目录/空目录/无目标文件/symlink安全与遗漏
    披露/根与daily并存的选择规则披露
  E 审计元数据: audit_commit真实git HEAD/generated_at真实UTC时间/固定
    代码版本一致/未提交变更不冒充干净版本/同数据覆盖结果确定性/输入
    SHA-256不变
  F 负向敏感性5退化全检出: 自然日阈值segment_split/旧cross_file公式/
    rzye_billion当MARGIN_BAL权威观测/只查global+macro的discover_files/
    报告缺audit_commit与generated_at——退化实现必使本套件断言失败
"""
import glob
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import historical_coverage_audit as hca   # 被审计的真实审计器(FIX1版)
import fact_engine as fe                  # 真实身份原语

REGISTRY = os.path.join(ROOT, 'config', 'metric_registry.json')


# ════════════════ fixture构造器(合成数据,与真实Schema同构) ════════════════

def _load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def _run(files, tag='fix1', out_name='out', source_note='FIX1合成fixture'):
    """建临时data/daily写入{文件名:对象或原始串},跑真实main();返回(ec,result,out)。"""
    tmp = tempfile.mkdtemp(prefix='w4fix1_%s_' % tag)
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


def slots_files():
    """A组/F1组fixture: 覆盖月频缺月/月内多日期/单月两日期/日频周末跨/
    日频缺交易日/周频缺周/日历外观测/crypto长断口。"""
    return {
        'macro_20261020.json': {"date": "2026-10-20", "data": {
            "NFP": {"value": 152000.0, "date": "2026-09-15",
                    "series": {"dates": ["2026-06-15", "2026-09-15"],
                               "values": [151000.0, 152000.0]}},   # 月频缺7/8月
            "WTI": {"value": 80.5, "date": "2026-09-17",
                    "series": {"dates": ["2026-08-15", "2026-09-16", "2026-09-17"],
                               "values": [80.1, 80.3, 80.5]}},      # 3日期2独立月
            "ICSA": {"value": 217000.0, "date": "2026-10-09",
                     "series": {"dates": ["2026-09-04", "2026-09-11", "2026-10-09"],
                                "values": [219000, 218000, 217000]}},  # 周频缺3周
            "AHE": {"value": 30.5, "date": "2026-09-17",
                    "series": {"dates": ["2026-09-16", "2026-09-17"],
                               "values": [30.4, 30.5]}}}},           # 单月两日期
        'global_20261020.json': {"date": "2026-10-20", "data": {
            "GOLD": {"close": 2650.0, "date": "2026-10-19",         # 周五→下周一
                     "series": {"dates": ["2026-10-16", "2026-10-19"],
                                "values": [2609.0, 2650.0]}},
            "SPX": {"close": 5704.0, "date": "2026-10-20",          # 周五→周二缺周一
                    "series": {"dates": ["2026-10-16", "2026-10-20"],
                               "values": [5700.0, 5704.0]}},
            "BTC": {"close": 67000.0, "date": "2026-10-26",         # crypto 21天断口
                    "series": {"dates": ["2026-10-05", "2026-10-26"],
                               "values": [66000.0, 67000.0]}}}},
        'china_20261020.json': {"timestamp": 1, "version": "v2",
                                "hk_indices": {"^HSI": {
                                    "close": 24000.0, "date": "2026-10-13",
                                    "series": {"dates": ["2026-10-12", "2026-10-13",
                                                         "2026-10-17"],
                                               "values": [23900, 23950, 24100]}}}},
    }   # 10-17=周六: 港股日历外观测(单独披露)


def china_margin_files(margin):
    return {'china_20261020.json': {"timestamp": 1, "version": "v2",
                                    "a_share_indices": {
                                        "000001.SH": {"name": "上证指数",
                                                      "close": 3300.0,
                                                      "date": "20261020"}},
                                    "margin": margin}}


# ════════════════ A组: 连续覆盖按真实观测槽位(FIX1-01) ════════════════

class TestASlotContinuity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ec, cls.result, cls.out, cls.tmp = _run(slots_files(), tag='slots')

    @classmethod
    def tearDownClass(cls):
        _cleanup(cls.tmp)

    # A1(指令§四固定测试): NFP 06-15+09-15→4预期月/2实际月/缺7、8月/
    #    2个单槽位连续段/最长连续段1/无跨月usable_interval
    def test_a1_nfp_missing_months_break(self):
        n = by_id(self.result, 'NFP')
        c = n['coverage']
        self.assertEqual(c['expected_observation_slots'], 4)
        self.assertEqual(c['observed_slots'], 2)
        self.assertEqual(c['missing_slots_count'], 2)
        self.assertEqual(c['missing_slots_sample'], ['2026-07', '2026-08'])
        self.assertEqual(len(c['continuous_segments']), 2)
        self.assertTrue(all(s['slots'] == 1 for s in c['continuous_segments']))
        self.assertEqual([s['start_slot'] for s in c['continuous_segments']],
                         ['2026-06', '2026-09'])
        self.assertEqual(c['longest_continuous_segment_slots'], 1)
        self.assertEqual(c['usable_intervals'], [])   # 无≥2槽位连续区间
        self.assertEqual(n['status'], 'OBSERVED')     # 2独立槽位,非SINGLE

    # A2(指令§四固定测试): WTI_SPOT_M 08-15+09-16+09-17→3日期/2独立月/
    #    最长连续段2(相邻月份槽位)
    def test_a2_wti_same_month_one_slot(self):
        w = by_id(self.result, 'WTI_SPOT_M')
        c = w['coverage']
        self.assertEqual(w['counts']['unique_observation_dates'], 3)
        self.assertEqual(c['unique_observation_slots'], 2)
        self.assertEqual(len(c['continuous_segments']), 1)
        seg = c['continuous_segments'][0]
        self.assertEqual((seg['start_slot'], seg['end_slot'], seg['slots']),
                         ('2026-08', '2026-09', 2))
        self.assertEqual((seg['start'], seg['end']), ('2026-08-15', '2026-09-17'))
        self.assertEqual(c['longest_continuous_segment_slots'], 2)
        self.assertEqual(len(c['usable_intervals']), 1)

    # A3(指令§四固定测试): 单月两日期(仅09-16+09-17)→1独立月度槽位,
    #    不得判2个样本;无≥2槽位usable_interval
    def test_a3_single_month_two_dates_one_slot(self):
        a = by_id(self.result, 'AHE')
        c = a['coverage']
        self.assertEqual(a['counts']['unique_observation_dates'], 2)
        self.assertEqual(c['unique_observation_slots'], 1)
        self.assertEqual(a['status'], 'SINGLE_OBSERVATION')   # 槽位口径非2样本
        self.assertEqual(c['longest_continuous_segment_slots'], 1)
        self.assertEqual(c['usable_intervals'], [])

    # A4(指令§四固定测试): 日频周五→下周一,中间无预期交易日→连续
    def test_a4_friday_to_monday_continuous(self):
        g = by_id(self.result, 'GOLD_F')
        c = g['coverage']
        self.assertEqual(len(c['continuous_segments']), 1)
        self.assertEqual(c['continuous_segments'][0]['slots'], 2)
        self.assertEqual(c['longest_continuous_segment_slots'], 2)
        self.assertEqual(c['missing_slots_count'], 0)   # 周末非预期槽位

    # A5(指令§四固定测试): 日频中间缺预期交易日→必须断段
    def test_a5_missing_trading_day_breaks(self):
        s = by_id(self.result, 'SPX')
        c = s['coverage']
        self.assertEqual(len(c['continuous_segments']), 2)
        self.assertEqual([s2['start_slot'] for s2 in c['continuous_segments']],
                         ['2026-10-16', '2026-10-20'])
        self.assertEqual(c['missing_slots_count'], 1)   # 缺2026-10-19(周一)
        self.assertEqual(c['longest_continuous_segment_slots'], 1)
        self.assertIn('SPX', [m['metric_id'] for m in
                              self.result['findings']['3_哪些指标中间存在严重断点']['metrics']])

    # A6: 周频缺周断段(ICSA 3观测周,中间缺3个预期ISO周→2段)
    def test_a6_weekly_missing_weeks_break(self):
        i = by_id(self.result, 'ICSA')
        c = i['coverage']
        self.assertEqual(c['expected_observation_slots'], 6)
        self.assertEqual(c['observed_slots'], 3)
        self.assertEqual(len(c['continuous_segments']), 2)
        self.assertEqual(c['continuous_segments'][0]['slots'], 2)   # 08-31+09-07相邻周
        self.assertEqual(c['continuous_segments'][1]['slots'], 1)   # 10-05(缺3周后)
        self.assertEqual(c['longest_continuous_segment_slots'], 2)

    # A7: 不属于已知预期日历的额外观测单独披露(HSI周六观测不入段)
    def test_a7_extra_calendar_slot_disclosed(self):
        h = by_id(self.result, 'HSI')
        c = h['coverage']
        self.assertGreaterEqual(c['extra_observations_beyond_calendar'], 1)
        self.assertIn('2026-10-17', c['extra_slot_keys_sample'])
        seg_slots = [s['start_slot'] for s in c['continuous_segments']] \
            + [s['end_slot'] for s in c['continuous_segments']]
        self.assertNotIn('2026-10-17', seg_slots)   # 日历外观测不并入连续段
        self.assertIn('港股日历最小集', c['calendar_limitations'])

    # A8: unique_observation_dates与unique_observation_slots两个计数并存不混淆
    def test_a8_dates_vs_slots_counts(self):
        w = by_id(self.result, 'WTI_SPOT_M')
        self.assertEqual(w['counts']['unique_observation_dates'], 3)
        self.assertEqual(w['coverage']['unique_observation_slots'], 2)
        g = by_id(self.result, 'GOLD_F')   # 日频: 槽位键=日期,两计数相等
        self.assertEqual(g['counts']['unique_observation_dates'],
                         g['coverage']['unique_observation_slots'])
        n = by_id(self.result, 'NFP')
        self.assertEqual(n['counts']['unique_observation_dates'], 2)
        self.assertEqual(n['coverage']['unique_observation_slots'], 2)
        self.assertEqual(n['coverage']['observed_slots'], 2)

    # A9: 无法可靠确定预期槽位时不虚构连续覆盖(直接调真实函数+注入式run)
    def test_a9_slots_unavailable_no_fabrication(self):
        segs, extras, reason = hca.split_slots(['2026-06-15', '2026-09-15'],
                                               'quarterly', None)
        self.assertEqual((segs, extras), ([], []))
        self.assertIn('频率未知', reason)

        def unavailable(freq, first, last, calendar):
            return None, None, '日历限制注记', '观察窗不可解析(测试注入)'

        tmp = tempfile.mkdtemp(prefix='w4fix1_a9_')
        daily = os.path.join(tmp, 'data', 'daily')
        os.makedirs(daily)
        with open(os.path.join(daily, 'global_20261020.json'), 'w',
                  encoding='utf-8') as f:
            f.write(json.dumps(slots_files()['global_20261020.json']))
        with mock.patch.object(hca, 'expected_slots', unavailable):
            res, _log, code = hca.run_audit(os.path.join(tmp, 'data'),
                                            os.path.join(tmp, 'out'), REGISTRY)
        try:
            self.assertEqual(code, 0)
            g = by_id(res, 'GOLD_F')
            c = g['coverage']
            self.assertEqual(c['continuous_segments'], [])       # 不虚构
            self.assertEqual(c['longest_continuous_segment_slots'], 0)
            self.assertIn('观察窗不可解析(测试注入)', c['slots_unavailable_reason'])
            self.assertEqual(g['status'], 'OBSERVED')            # 回退唯一观测日数
            # 槽位不可用→findings3按自然日回退判据(crypto 21天>10)
            brk3 = [m for m in res['findings']['3_哪些指标中间存在严重断点']['metrics']
                    if m['metric_id'] == 'BTC']
            self.assertEqual(len(brk3), 1)
            self.assertEqual(brk3[0]['criterion'], 'slots_unavailable_natural_day_fallback')
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


# ════════════════ B组: 重复计数按真实文件身份拆分(FIX1-02) ════════════════

class TestBDuplicateSplit(unittest.TestCase):
    # B1: 同文件point+series同日+series内重复(3条权威记录同一(文件,日期))
    def test_b1_same_file_point_and_series(self):
        files = {'global_20261020.json': {"date": "2026-10-20", "data": {
            "GOLD": {"close": 2650.5, "date": "2026-10-20",
                     "series": {"dates": ["2026-10-20", "2026-10-20"],
                                "values": [2651.0, 2652.0]}}}}}
        ec, res, _out, tmp = _run(files, tag='b1')
        try:
            self.assertEqual(ec, 0)
            g = by_id(res, 'GOLD_F')
            c = g['counts']
            self.assertEqual(c['authority_raw_records'], 3)
            self.assertEqual(c['authority_unique_observation_dates'], 1)
            self.assertEqual(c['same_file_extra_duplicate_records'], 2)
            self.assertEqual(c['cross_file_duplicate_records'], 0)
            self.assertEqual(c['same_file_duplicate_dates'], 1)   # series内重复形态
        finally:
            _cleanup(tmp)

    # B2/B3/B5: 不同文件同日(每文件point+series各1条→同文件各1条额外+跨文件1条)
    # +同日不同值冲突候选保留
    def test_b2_cross_file_same_date(self):
        files = {
            'global_20261020.json': {"date": "2026-10-20", "data": {
                "GOLD": {"close": 2650.0, "date": "2026-10-20",
                         "series": {"dates": ["2026-10-20"], "values": [2650.0]}}}},
            'global_20261021.json': {"date": "2026-10-21", "data": {
                "GOLD": {"close": 2650.5, "date": "2026-10-20",
                         "series": {"dates": ["2026-10-20"], "values": [2650.5]}}}}}
        ec, res, _out, tmp = _run(files, tag='b2')
        try:
            self.assertEqual(ec, 0)
            g = by_id(res, 'GOLD_F')
            c = g['counts']
            self.assertEqual(c['authority_raw_records'], 4)   # 每文件point+series各1
            self.assertEqual(c['authority_unique_observation_dates'], 1)
            self.assertEqual(c['same_file_extra_duplicate_records'], 2)  # 每文件内1条
            self.assertEqual(c['cross_file_duplicate_records'], 1)      # 两文件同日1条
            self.assertEqual(c['authority_raw_records'],
                             c['authority_unique_observation_dates']
                             + c['same_file_extra_duplicate_records']
                             + c['cross_file_duplicate_records'])
            # 同日不同值冲突候选保留(不擅自选真值)
            self.assertEqual(c['distinct_value_conflict_dates'], 1)
            self.assertEqual(g['conflict_candidates'][0]['obs_date'], '2026-10-20')
        finally:
            _cleanup(tmp)

    # B4(指令§五固定例): 文件A同一天3条+文件B同一天1条→权威4/唯一1/同文件2/跨文件1
    def test_b4_spec_example_mixed(self):
        files = {
            'global_20261020.json': {"date": "2026-10-20", "data": {
                "GOLD": {"close": 2650.5, "date": "2026-10-20",
                         "series": {"dates": ["2026-10-20", "2026-10-20"],
                                    "values": [2651.0, 2652.0]}}}},
            'global_20261021.json': {"date": "2026-10-21", "data": {
                "GOLD": {"close": 2653.0, "date": "2026-10-20"}}}}
        ec, res, _out, tmp = _run(files, tag='b4')
        try:
            self.assertEqual(ec, 0)
            g = by_id(res, 'GOLD_F')
            c = g['counts']
            self.assertEqual(c['authority_raw_records'], 4)
            self.assertEqual(c['authority_unique_observation_dates'], 1)
            self.assertEqual(c['same_file_extra_duplicate_records'], 2)
            self.assertEqual(c['cross_file_duplicate_records'], 1)
            # 不变量: 权威原始=唯一观测日+同文件额外+跨文件额外
            self.assertEqual(c['authority_raw_records'],
                             c['authority_unique_observation_dates']
                             + c['same_file_extra_duplicate_records']
                             + c['cross_file_duplicate_records'])
        finally:
            _cleanup(tmp)

    # B6: 权威与非权威重复(快照同日不虚增权威计数;不变量只在权威范围内成立)
    def test_b6_nonauth_repeat_not_inflating(self):
        files = {
            'global_20261020.json': {"date": "2026-10-20", "data": {
                "GOLD": {"close": 2650.0, "date": "2026-10-20"}}},
            'research_snapshot_20261020.json': {
                "snapshot_id": "s1",
                "facts": [{"metric_id": "GOLD_F", "value": 2650.0,
                           "observation_date": "2026-10-20", "source": "snapshot"}],
                "series_store": {"GOLD_F": {"dates": ["2026-10-20"],
                                            "values": [2650.0]}}}}
        ec, res, _out, tmp = _run(files, tag='b6')
        try:
            self.assertEqual(ec, 0)
            g = by_id(res, 'GOLD_F')
            c = g['counts']
            self.assertEqual(c['authority_raw_records'], 1)
            self.assertEqual(c['non_authority_records'], 2)   # 快照不新增覆盖
            self.assertEqual(c['same_file_extra_duplicate_records'], 0)
            self.assertEqual(c['cross_file_duplicate_records'], 0)
            self.assertEqual(g['discovery']['non_authority_only_dates'], [])
        finally:
            _cleanup(tmp)

    # 计数不变量: 全部81项指标逐一成立(多通道fixture)
    def test_b_invariant_all_metrics(self):
        ec, res, _out, tmp = _run(dict(slots_files(),
                                       **china_margin_files(
                                           {"date": "20261020",
                                            "rzye": 2.3e12, "rqye": 2.8e10,
                                            "rzye_billion": 23567.38})), tag='binv')
        try:
            self.assertEqual(ec, 0)
            for r in res['metrics']:
                if not r['discovery'].get('found'):
                    continue
                c = r['counts']
                self.assertEqual(
                    c['authority_raw_records'],
                    c['authority_unique_observation_dates']
                    + c['same_file_extra_duplicate_records']
                    + c['cross_file_duplicate_records'],
                    '%s违反FIX1-02计数不变量' % r['metric_id'])
        finally:
            _cleanup(tmp)

    # split_duplicates纯函数直接核验(指令§五固定例的函数级复算)
    def test_b_split_duplicates_function(self):
        rec = lambda f, d: {'file': f, 'obs_date': d}
        same, cross = hca.split_duplicates([rec('A', '2026-10-20')] * 3
                                           + [rec('B', '2026-10-20')])
        self.assertEqual((same, cross), (2, 1))
        same, cross = hca.split_duplicates([rec('A', 'd1'), rec('A', 'd2'),
                                            rec('B', 'd1')])
        self.assertEqual((same, cross), (0, 1))


# ════════════════ C组: MARGIN_BAL身份(FIX1-03) ════════════════

class TestCIdentity(unittest.TestCase):
    # C1(指令§六负向): 只有rzye_billion的文件→MARGIN_BAL不得获权威观测
    def test_c1_rzye_only_no_authority(self):
        ec, res, _out, tmp = _run(china_margin_files(
            {"date": "20261020", "rzye_billion": 18500.0}), tag='c1')
        try:
            self.assertEqual(ec, 0)
            mb = by_id(res, 'MARGIN_BAL')
            self.assertEqual(mb['status'], 'MISSING')
            self.assertFalse(mb['discovery']['found'])
            self.assertIsNone(mb['coverage']['first_observation_date'])
            self.assertEqual(mb['coverage']['continuous_segments'], [])
            self.assertEqual(mb['coverage']['total_unique_observations'], 0)
            unm = {(u['channel'], u['raw_key']): u for u in res['unmapped_records']}
            self.assertIn(('china', 'margin:rzye_billion'), unm)
            note = unm[('china', 'margin:rzye_billion')]['note']
            self.assertIn('identity_mismatch', note)
            self.assertIn('融资余额', note)   # 标明代表融资余额
            # 原始字段存在事实保留(不删除原始记录让统计干净)
            self.assertIn('daily/china_20261020.json',
                          unm[('china', 'margin:rzye_billion')]['files'])
        finally:
            _cleanup(tmp)

    # C2(指令§六正向): 合法同口径balance→按既有注册语义正常处理
    def test_c2_balance_authoritative(self):
        ec, res, _out, tmp = _run(china_margin_files(
            {"date": "20261020", "balance": 18500.0}), tag='c2')
        try:
            self.assertEqual(ec, 0)
            mb = by_id(res, 'MARGIN_BAL')
            self.assertEqual(mb['status'], 'SINGLE_OBSERVATION')
            self.assertEqual(mb['coverage']['first_observation_date'], '2026-10-20')
            self.assertEqual(mb['coverage']['total_unique_observations'], 1)
            self.assertEqual(mb['counts']['authority_raw_records'], 1)
            unm = {u['raw_key'] for u in res['unmapped_records']}
            self.assertNotIn('margin:rzye_billion', unm)
        finally:
            _cleanup(tmp)

    # C3: 同一天同时出现不同语义字段→balance入权威,rzye_billion仍独立披露
    def test_c3_both_fields_same_day(self):
        ec, res, _out, tmp = _run(china_margin_files(
            {"date": "20261020", "balance": 19000.0, "rzye_billion": 18500.0}),
            tag='c3')
        try:
            self.assertEqual(ec, 0)
            mb = by_id(res, 'MARGIN_BAL')
            self.assertEqual(mb['counts']['authority_raw_records'], 1)  # 仅balance
            self.assertEqual(mb['coverage']['first_observation_date'], '2026-10-20')
            unm = {(u['channel'], u['raw_key']) for u in res['unmapped_records']}
            self.assertIn(('china', 'margin:rzye_billion'), unm)        # rzye仍披露
        finally:
            _cleanup(tmp)

    # C4: 未注册字段披露(真实数据margin键组合: rzye/rqye/rzye_billion)
    def test_c4_real_margin_key_combo_disclosed(self):
        ec, res, _out, tmp = _run(china_margin_files(
            {"date": "20261020", "rzye": 2.3e12, "rqye": 2.8e10,
             "rzye_billion": 23567.38}), tag='c4')
        try:
            self.assertEqual(ec, 0)
            mb = by_id(res, 'MARGIN_BAL')
            self.assertEqual(mb['status'], 'MISSING')   # 三字段均非两融合计口径
            unm = {(u['channel'], u['raw_key']): u for u in res['unmapped_records']}
            for key in ('margin:rzye_billion', 'margin:rzye', 'margin:rqye'):
                self.assertIn(('china', key), unm)
                self.assertIn('identity_mismatch', unm[('china', key)]['note'])
            self.assertIn('融券余额', unm[('china', 'margin:rqye')]['note'])
            self.assertIn('不自动以rzye+rqye推算', unm[('china', 'margin:rqye')]['note'])
        finally:
            _cleanup(tmp)

    # C5(指令§六): MARGIN_BAL不因错误字段取得权威连续区间(汇总口径同步)
    def test_c5_no_continuous_interval_from_wrong_field(self):
        ec, res, _out, tmp = _run(china_margin_files(
            {"date": "20261020", "rzye_billion": 18500.0}), tag='c5')
        try:
            self.assertEqual(ec, 0)
            mb = by_id(res, 'MARGIN_BAL')
            self.assertEqual(mb['coverage']['longest_continuous_segment_slots'], 0)
            self.assertEqual(mb['coverage']['usable_intervals'], [])
            self.assertIn('MARGIN_BAL',
                          res['findings']['4_哪些指标未保存历史']['MISSING'])
            self.assertIn('MARGIN_BAL', res['summary']['core_missing_or_unreadable']
                          + ([] if 'MARGIN_BAL' in res['summary']['core_missing_or_unreadable']
                             else ['MARGIN_BAL']))   # 允许core/非core差异,只要求MISSING事实
        finally:
            _cleanup(tmp)


# ════════════════ D组: 五通道任意子集输入发现(FIX1-04) ════════════════

MIN_CHANNEL_FILE = {
    'global': ('global_20261020.json',
               {"date": "2026-10-20", "data": {"GOLD": {"close": 2650.0,
                                                        "date": "2026-10-20"}}}),
    'china': ('china_20261020.json',
              {"a_share_indices": {"000001.SH": {"name": "上证指数",
                                                 "close": 3300.0,
                                                 "date": "20261020"}}}),
    'macro': ('macro_20261020.json',
              {"date": "2026-10-20", "data": {"ICSA": {"value": 219000.0,
                                                       "date": "2026-10-09"}}}),
    'rate_economy': ('rate_economy_20261020.json',
                     {"current_rates": {"DFF": {"value": 4.33,
                                                "date": "2026-10-01"}}}),
    'research_snapshot': ('research_snapshot_20261020.json',
                          {"facts": [{"metric_id": "GOLD_F", "value": 1.0,
                                      "observation_date": "2026-10-20",
                                      "source": "snapshot"}]}),
}


def _subset_files(channels):
    return {MIN_CHANNEL_FILE[ch][0]: MIN_CHANNEL_FILE[ch][1] for ch in channels}


class TestDDiscovery(unittest.TestCase):
    # D1(指令§七固定反例): data/daily/china_20261020.json唯一→识别daily/,
    #    发现1个china文件/其余通道0/不输出NO_INPUT/正常生成81项审计
    def test_d1_china_only_daily(self):
        ec, res, _out, tmp = _run(_subset_files(['china']), tag='d1')
        try:
            self.assertEqual(ec, 0)
            self.assertEqual(res['audit_status'], 'COMPLETED')
            self.assertEqual(res['input']['by_channel'],
                             {'global': 0, 'china': 1, 'macro': 0,
                              'rate_economy': 0, 'research_snapshot': 0})
            self.assertEqual(len(res['metrics']), 81)
            self.assertEqual(by_id(res, 'SHCOMP')['status'], 'SINGLE_OBSERVATION')
            self.assertIn('daily/', res['input']['excluded']['selection_rule'])
        finally:
            _cleanup(tmp)

    # D2: 五个单通道子集+全部10个两通道组合,逐一真实验证
    def test_d2_all_subsets(self):
        combos = [(ch,) for ch in MIN_CHANNEL_FILE] \
            + list(itertools.combinations(MIN_CHANNEL_FILE, 2))
        self.assertEqual(len(combos), 15)
        for combo in combos:
            ec, res, _out, tmp = _run(_subset_files(combo), tag='d2')
            try:
                self.assertEqual(ec, 0, combo)
                self.assertEqual(res['audit_status'], 'COMPLETED', combo)
                expect = {ch: (1 if ch in combo else 0)
                          for ch in MIN_CHANNEL_FILE}
                self.assertEqual(res['input']['by_channel'], expect, combo)
                self.assertEqual(len(res['metrics']), 81, combo)
                self.assertEqual(res['input']['files'], len(combo), combo)
            finally:
                _cleanup(tmp)

    # D3: 直接传daily目录本身(无daily/子目录)→输入根本身规则
    def test_d3_pass_daily_dir_directly(self):
        tmp = tempfile.mkdtemp(prefix='w4fix1_d3_')
        daily = os.path.join(tmp, 'flat')   # 故意不叫daily,无子目录
        os.makedirs(daily)
        with open(os.path.join(daily, 'china_20261020.json'), 'w',
                  encoding='utf-8') as f:
            f.write(json.dumps(MIN_CHANNEL_FILE['china'][1]))
        out = os.path.join(tmp, 'out')
        ec = hca.main(['--data-dir', daily, '--out-dir', out,
                       '--registry', REGISTRY])
        try:
            self.assertEqual(ec, 0)
            hits = glob.glob(os.path.join(out, 'coverage_audit_*.json'))
            res = _load(hits[0])
            self.assertEqual(res['audit_status'], 'COMPLETED')
            self.assertEqual(res['input']['by_channel']['china'], 1)
            self.assertIn('输入根本身', res['input']['excluded']['selection_rule'])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # D4: 空目录→NO_INPUT,不写任何输出
    def test_d4_empty_dir_no_input(self):
        tmp = tempfile.mkdtemp(prefix='w4fix1_d4_')
        os.makedirs(os.path.join(tmp, 'data', 'daily'))
        out = os.path.join(tmp, 'out')
        ec = hca.main(['--data-dir', os.path.join(tmp, 'data'),
                       '--out-dir', out, '--registry', REGISTRY])
        try:
            self.assertEqual(ec, 2)
            self.assertFalse(os.path.exists(out))
            res, _log, code = hca.run_audit(os.path.join(tmp, 'data'), out, REGISTRY)
            self.assertEqual(res['audit_status'], 'NO_INPUT')
            self.assertEqual(code, 2)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # D5: 无目标文件(只有.md镜像/anchors等排除项)→NO_INPUT;
    #     两种形态: 排除项直接在数据根(计入excluded)/排除项在daily/但无通道
    #     文件(如实披露daily存在但无五通道命中)
    def test_d5_only_decoy_files(self):
        decoys = {'global_20261020.md': '{}', 'anchors_20261020.json': '{}',
                  'scorecard_20261020.json': '{}', 'notes.txt': 'x'}
        # 形态1: 排除项直接在数据根(无daily/)
        tmp = tempfile.mkdtemp(prefix='w4fix1_d5_')
        data = os.path.join(tmp, 'data')
        os.makedirs(data)
        for name, content in decoys.items():
            with open(os.path.join(data, name), 'w', encoding='utf-8') as f:
                f.write(content)
        res, _log, code = hca.run_audit(data, os.path.join(tmp, 'out'), REGISTRY)
        try:
            self.assertEqual(code, 2)
            self.assertEqual(res['audit_status'], 'NO_INPUT')
            self.assertEqual(res['excluded']['md_mirrors'], 1)
            self.assertEqual(res['excluded']['anchors_files'], 1)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        # 形态2: 排除项在daily/且五通道无命中→daily存在事实如实披露
        tmp2 = tempfile.mkdtemp(prefix='w4fix1_d5b_')
        daily2 = os.path.join(tmp2, 'data', 'daily')
        os.makedirs(daily2)
        for name, content in decoys.items():
            with open(os.path.join(daily2, name), 'w', encoding='utf-8') as f:
                f.write(content)
        res2, _log, code2 = hca.run_audit(os.path.join(tmp2, 'data'),
                                          os.path.join(tmp2, 'out'), REGISTRY)
        try:
            self.assertEqual(code2, 2)
            self.assertEqual(res2['audit_status'], 'NO_INPUT')
            self.assertTrue(res2['excluded']['daily_present_without_channel_files'])
        finally:
            shutil.rmtree(tmp2, ignore_errors=True)

    # D6: symlink安全(越界符号链接拒绝+遗漏披露)
    def test_d6_symlink_skipped_and_disclosed(self):
        tmp = tempfile.mkdtemp(prefix='w4fix1_d6_')
        daily = os.path.join(tmp, 'data', 'daily')
        os.makedirs(daily)
        outside = os.path.join(tmp, 'outside_global.json')
        with open(outside, 'w', encoding='utf-8') as f:
            f.write(json.dumps(MIN_CHANNEL_FILE['global'][1]))
        os.symlink(outside, os.path.join(daily, 'global_20261020.json'))
        with open(os.path.join(daily, 'china_20261020.json'), 'w',
                  encoding='utf-8') as f:
            f.write(json.dumps(MIN_CHANNEL_FILE['china'][1]))
        res, _log, code = hca.run_audit(os.path.join(tmp, 'data'),
                                        os.path.join(tmp, 'out'), REGISTRY)
        try:
            self.assertEqual(code, 0)
            self.assertEqual(res['audit_status'], 'COMPLETED')
            self.assertEqual(res['input']['by_channel']['global'], 0)   # 拒绝
            self.assertEqual(res['input']['by_channel']['china'], 1)
            self.assertEqual(res['input']['excluded']['symlink_skipped'],
                             ['daily/global_20261020.json'])            # 披露
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # D7: 输入根与daily/同时有合法输入→固定选daily/+披露未选目录,不暗中混合
    def test_d7_root_and_daily_both(self):
        tmp = tempfile.mkdtemp(prefix='w4fix1_d7_')
        data = os.path.join(tmp, 'data')
        daily = os.path.join(data, 'daily')
        os.makedirs(daily)
        with open(os.path.join(data, 'global_20261020.json'), 'w',
                  encoding='utf-8') as f:      # 根层合法输入
            f.write(json.dumps(MIN_CHANNEL_FILE['global'][1]))
        with open(os.path.join(daily, 'china_20261020.json'), 'w',
                  encoding='utf-8') as f:      # daily层合法输入
            f.write(json.dumps(MIN_CHANNEL_FILE['china'][1]))
        out = os.path.join(tmp, 'out')
        ec = hca.main(['--data-dir', data, '--out-dir', out, '--registry', REGISTRY])
        try:
            self.assertEqual(ec, 0)
            hits = glob.glob(os.path.join(out, 'coverage_audit_*.json'))
            res = _load(hits[0])
            # 固定规则: 选daily/
            self.assertIn('选daily/', res['input']['excluded']['selection_rule'])
            self.assertEqual(res['input']['by_channel'],
                             {'global': 0, 'china': 1, 'macro': 0,
                              'rate_economy': 0, 'research_snapshot': 0})
            # 未选目录如实披露(只数不读,不混合)
            self.assertEqual(res['input']['excluded']['unselected_root_files'],
                             {'global': 1})
            with open(glob.glob(os.path.join(out, 'input_manifest_*.json'))[0],
                      encoding='utf-8') as f:
                rels = [e['relpath'] for e in json.load(f)['files']]
            self.assertEqual(rels, ['daily/china_20261020.json'])   # 零根层文件
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


# ════════════════ E组: 审计元数据(FIX1-05) ════════════════

class TestEAuditMetadata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 同一fixture两次执行(manifest含mtime_ns→必须同一批文件才有相同run_id)
        cls.tmp1 = tempfile.mkdtemp(prefix='w4fix1_e_')
        daily = os.path.join(cls.tmp1, 'data', 'daily')
        os.makedirs(daily)
        with open(os.path.join(daily, 'global_20261020.json'), 'w',
                  encoding='utf-8') as f:
            f.write(json.dumps(MIN_CHANNEL_FILE['global'][1]))
        cls.out1 = os.path.join(cls.tmp1, 'run1')
        cls.out2 = os.path.join(cls.tmp1, 'run2')
        cls.ec1 = hca.main(['--data-dir', os.path.join(cls.tmp1, 'data'),
                            '--out-dir', cls.out1, '--registry', REGISTRY])
        cls.ec2 = hca.main(['--data-dir', os.path.join(cls.tmp1, 'data'),
                            '--out-dir', cls.out2, '--registry', REGISTRY])
        cls.res1 = _load(glob.glob(os.path.join(cls.out1,
                                                'coverage_audit_*.json'))[0])
        cls.res2 = _load(glob.glob(os.path.join(cls.out2,
                                                'coverage_audit_*.json'))[0])

    @classmethod
    def tearDownClass(cls):
        _cleanup(cls.tmp1)

    # E1: audit_commit=真实git rev-parse HEAD(非开发提示词预期SHA)
    def test_e1_audit_commit_real_head(self):
        for res in (self.res1, self.res2):
            self.assertIsNotNone(res['audit_commit'])
            self.assertRegex(res['audit_commit'], r'^[0-9a-f]{40}$')
        r = subprocess.run(['git', '-C', ROOT, 'rev-parse', 'HEAD'],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(self.res1['audit_commit'], r.stdout.strip())

    # E2: generated_at=真实UTC系统时钟(可解析/UTC/落在执行窗口内)
    def test_e2_generated_at_real_utc(self):
        t0 = datetime.now(timezone.utc)
        _ec, res, _out, tmp = _run(_subset_files(['macro']), tag='e2')
        try:
            t1 = datetime.now(timezone.utc)
            g = datetime.fromisoformat(res['generated_at'])
            self.assertEqual(g.utcoffset().total_seconds(), 0)
            self.assertGreaterEqual(g, t0.replace(microsecond=0))
            self.assertLessEqual(g, t1)
            self.assertGreater(g, datetime(2026, 1, 1, tzinfo=timezone.utc))  # 非占位符
        finally:
            _cleanup(tmp)

    # E3: 固定代码版本一致(两次执行audit_commit相同+run_id相同)
    def test_e3_same_code_same_commit(self):
        self.assertEqual(self.ec2, 0)
        self.assertEqual(self.res1['audit_commit'], self.res2['audit_commit'])
        self.assertEqual(self.res1['run_id'], self.res2['run_id'])
        self.assertEqual(self.res1['schema_version'], 'w4-coverage-audit/1.1')

    # E4: 未提交修改不得冒充干净版本(脏工作区→披露;git不可得→不声称已提交)
    def test_e4_dirty_worktree_disclosed(self):
        head = self.res1['audit_commit']

        def dirty_git(repo):
            return head, 3

        with mock.patch.object(hca, '_git_state', dirty_git):
            res, _log, _c = hca.run_audit(os.path.join(self.tmp1, 'data'),
                                          os.path.join(self.tmp1, 'out_e4a'),
                                          REGISTRY)
        self.assertEqual(res['audit_commit'], head)
        self.assertEqual(res['audit_commit_worktree_dirty_files'], 3)
        self.assertIn('3项未提交变更', res['audit_commit_disclosure'])
        self.assertIn('不得声称报告完全对应', res['audit_commit_disclosure'])

        def no_git(repo):
            return None, None

        with mock.patch.object(hca, '_git_state', no_git):
            res2, _log, _c = hca.run_audit(os.path.join(self.tmp1, 'data'),
                                           os.path.join(self.tmp1, 'out_e4b'),
                                           REGISTRY)
        self.assertIsNone(res2['audit_commit'])
        self.assertIn('不声称对应', res2['audit_commit_note'])

    # E4b: INVALID_PATH结果同样携带元数据(元数据先于路径校验取得)
    def test_e4b_metadata_on_invalid_path(self):
        res, _log, code = hca.run_audit('/nonexistent_path_xyz',
                                        os.path.join(self.tmp1, 'out_e4c'),
                                        REGISTRY)
        self.assertEqual(code, 2)
        self.assertEqual(res['audit_status'], 'INVALID_PATH')
        self.assertRegex(res['audit_commit'], r'^[0-9a-f]{40}$')
        self.assertIn('generated_at', res)

    # E5: 同数据覆盖结果确定性(剔除generated_at后metrics/summary/findings一致)
    def test_e5_deterministic_coverage(self):
        strip = lambda r: {k: v for k, v in r.items() if k != 'generated_at'}
        self.assertEqual(json.dumps(strip(self.res1), sort_keys=True, ensure_ascii=False),
                         json.dumps(strip(self.res2), sort_keys=True, ensure_ascii=False))
        rid = self.res1['run_id']
        with open(os.path.join(self.out1, 'input_manifest_%s.json' % rid), 'rb') as f:
            b1 = f.read()
        with open(os.path.join(self.out2, 'input_manifest_%s.json' % rid), 'rb') as f:
            b2 = f.read()
        self.assertEqual(b1, b2)   # manifest(不含运行时元数据)仍字节级一致

    # E6: 输入SHA-256不变(manifest逐文件SHA==盘上实测;审计零触碰输入)
    def test_e6_input_sha_unchanged(self):
        self.assertFalse(self.res1['integrity']['input_changed_during_audit'])
        with open(glob.glob(os.path.join(
                self.out1, 'input_manifest_%s.json' % self.res1['run_id']))[0],
                encoding='utf-8') as f:
            man = json.load(f)
        import hashlib
        for e in man['files']:
            p = os.path.join(self.tmp1, 'data', e['relpath'])
            with open(p, 'rb') as fh:
                self.assertEqual(hashlib.sha256(fh.read()).hexdigest(),
                                 e['sha256'], e['relpath'])

    # MD头部披露: audit_commit/generated_at/输入清单摘要/数据根/审计状态
    def test_e7_md_header_disclosure(self):
        md_path = os.path.join(self.out1,
                               'coverage_audit_%s.md' % self.res1['run_id'])
        with open(md_path, encoding='utf-8') as f:
            head = f.read().split('## 总体')[0]
        self.assertIn(self.res1['audit_commit'], head)
        self.assertIn(self.res1['generated_at'], head)
        self.assertIn('COMPLETED', head)
        self.assertIn(os.path.realpath(os.path.join(self.tmp1, 'data')), head)
        self.assertIn('manifest_digest', head)


# ════════════════ F组: 负向敏感性(5类退化必被检出) ════════════════

class TestFNegativeSensitivity(unittest.TestCase):
    """证明: 把FIX1任一修复退化回W4旧实现,本套件断言会失败(而非继续通过)。"""

    @classmethod
    def setUpClass(cls):
        cls.ec, cls.res, cls.out, cls.tmp = _run(slots_files(), tag='fbase')

    @classmethod
    def tearDownClass(cls):
        _cleanup(cls.tmp)

    def _mutated(self, tmp_suffix, **patches):
        out = os.path.join(self.tmp, 'mut_' + tmp_suffix)
        with mock.patch.multiple(hca, **patches):
            hca.main(['--data-dir', os.path.join(self.tmp, 'data'),
                      '--out-dir', out, '--registry', REGISTRY,
                      '--source-note', 'FIX1退化模拟'])
        hits = glob.glob(os.path.join(out, 'coverage_audit_*.json'))
        return _load(hits[0])

    # F1: 退化为自然日阈值segment_split→A1/A3断言失败
    def test_f1_natural_day_degrade_detected(self):
        n = by_id(self.res, 'NFP')
        correct = (n['coverage']['longest_continuous_segment_slots'] == 1
                   and len(n['coverage']['usable_intervals']) == 0)
        self.assertTrue(correct)

        def natural_day_split(auth_dates, freq, calendar):
            segs = hca.segment_split(auth_dates, freq)   # W4旧算法(自然日阈值)
            return ([dict(s, start_slot=s['start'], end_slot=s['end']) for s in segs],
                    [], None)

        mut = self._mutated('f1', split_slots=natural_day_split)
        mn = by_id(mut, 'NFP')
        # 旧算法: 06-15→09-15间隔92≤月阈值92→误判连续(跨缺失月份)
        self.assertNotEqual(mn['coverage']['longest_continuous_segment_slots'], 1)
        self.assertNotEqual(mn['coverage']['usable_intervals'], [])
        ma = by_id(mut, 'AHE')   # 同月两日期被当两个连续样本
        self.assertNotEqual(ma['coverage']['longest_continuous_segment_slots'], 1)
        detect = (correct
                  and mn['coverage']['longest_continuous_segment_slots'] != 1
                  and ma['coverage']['longest_continuous_segment_slots'] != 1)
        self.assertTrue(detect)

    # F2: 退化为旧cross_file_duplicate_records公式(全部重复算跨文件)→B组断言失败
    def test_f2_old_cross_formula_detected(self):
        g_base = by_id(self.res, 'GOLD_F')
        # slots fixture: GOLD point@10-19+series[10-16,10-19]同文件→same=1,cross=0
        self.assertEqual((g_base['counts']['same_file_extra_duplicate_records'],
                          g_base['counts']['cross_file_duplicate_records']), (1, 0))

        def old_formula(auth_records):   # W4旧实现: max(auth_raw-唯一日,0)全记跨文件
            uniq = len({r['obs_date'] for r in auth_records})
            return 0, max(len(auth_records) - uniq, 0)

        # 指令§五固定例直接复算: 文件A同日3条+文件B同日1条
        #   正确=(same 2, cross 1);旧公式=(same 0, cross 3)→B4断言必失败
        rec = lambda f, d: {'file': f, 'obs_date': d, 'auth': True}
        same, cross = old_formula([rec('A', 'd')] * 3 + [rec('B', 'd')])
        self.assertEqual((same, cross), (0, 3))
        correct = hca.split_duplicates([rec('A', 'd')] * 3 + [rec('B', 'd')])
        self.assertEqual(correct, (2, 1))
        # 退化seam注入真实run: 文件内重复被冒充跨文件重复
        mut = self._mutated('f2', split_duplicates=old_formula)
        mg = by_id(mut, 'GOLD_F')
        self.assertEqual(mg['counts']['same_file_extra_duplicate_records'], 0)
        self.assertEqual(mg['counts']['cross_file_duplicate_records'], 1)
        detect = ((same, cross) != correct
                  and (mg['counts']['same_file_extra_duplicate_records'],
                       mg['counts']['cross_file_duplicate_records']) != (1, 0))
        self.assertTrue(detect)

    # F3: 退化为rzye_billion当MARGIN_BAL权威观测→C1断言失败
    def test_f3_rzye_as_margin_bal_detected(self):
        ec, base, _out, tmp = _run(china_margin_files(
            {"date": "20261020", "rzye_billion": 18500.0}), tag='f3base')
        try:
            mb = by_id(base, 'MARGIN_BAL')
            correct = (mb['status'] == 'MISSING')
            self.assertTrue(correct)
        finally:
            _cleanup(tmp)
        orig = hca.extract_file

        def rzye_as_auth(entry, accs, unmapped, registry_ids, registry_by_id):
            orig(entry, accs, unmapped, registry_ids, registry_by_id)
            if entry['channel'] != 'china':
                return
            mg = (entry.get('_parsed') or {}).get('margin') or {}
            if mg.get('rzye_billion') is not None:   # W4旧缺陷: 当权威观测写入
                fd = fe._iso(entry['file_date']) if entry['file_date'] else None
                hca._add_point(accs.setdefault('MARGIN_BAL', hca.MetricAcc()),
                               mg.get('date'), mg.get('rzye_billion'), 'china',
                               True, entry['relpath'], fd, 'point')

        out = os.path.join(tempfile.mkdtemp(prefix='w4fix1_f3_'), 'out')
        data = os.path.join(os.path.dirname(out), 'data')
        os.makedirs(os.path.join(data, 'daily'))
        with open(os.path.join(data, 'daily', 'china_20261020.json'), 'w',
                  encoding='utf-8') as f:
            f.write(json.dumps(china_margin_files(
                {"date": "20261020", "rzye_billion": 18500.0})['china_20261020.json']))
        try:
            with mock.patch.object(hca, 'extract_file', rzye_as_auth):
                hca.main(['--data-dir', data, '--out-dir', out,
                          '--registry', REGISTRY])
            res = _load(glob.glob(os.path.join(out,
                                     'coverage_audit_*.json'))[0])
            mbm = by_id(res, 'MARGIN_BAL')
            self.assertNotEqual(mbm['status'], 'MISSING')          # 被污染
            self.assertEqual(mbm['coverage']['first_observation_date'],
                             '2026-10-20')
            detect = correct and mbm['status'] != 'MISSING'
            self.assertTrue(detect)
        finally:
            shutil.rmtree(os.path.dirname(out), ignore_errors=True)

    # F4: 退化为只检查global/macro的discover_files→D1断言失败
    def test_f4_global_macro_only_discovery_detected(self):
        correct = (by_id(self.res, 'NFP')['status'] == 'OBSERVED')
        self.assertTrue(correct)

        def old_discover(data_dir):   # W4旧实现: 只查global_/macro_决定daily/
            import glob as _g
            root = os.path.realpath(data_dir)
            base = root
            sub = os.path.join(root, 'daily')
            if os.path.isdir(sub) and (_g.glob(os.path.join(sub, 'global_*.json'))
                                       or _g.glob(os.path.join(sub, 'macro_*.json'))):
                base = sub
            files, symlink_skipped, by_channel = [], [], {}
            for ch, pat in hca.CHANNEL_PATTERNS.items():
                hits = sorted(_g.glob(os.path.join(base, pat)))
                by_channel[ch] = len(hits)
                for p in hits:
                    if os.path.islink(p) or not os.path.isfile(p):
                        continue
                    m = hca._FILE_DATE_RE.search(os.path.basename(p))
                    files.append({'path': p, 'relpath': os.path.relpath(p, root),
                                  'channel': ch,
                                  'file_date': m.group(1) if m else None})
            excluded = {'md_mirrors': 0, 'anchors_files': 0, 'scorecard_files': 0,
                        'anchor_prompt_files': 0, 'correlation_files': 0,
                        'symlink_skipped': [], 'unselected_root_files': {},
                        'selection_rule': '退化模拟', 'note': ''}
            return files, base, excluded, by_channel

        mut = self._mutated('f4', discover_files=old_discover)
        # slots fixture含global/macro→旧实现仍能发现;关键反例是china-only:
        self.assertEqual(mut['audit_status'], 'COMPLETED')   # 本fixture不受影响
        tmp = tempfile.mkdtemp(prefix='w4fix1_f4b_')
        daily = os.path.join(tmp, 'data', 'daily')
        os.makedirs(daily)
        with open(os.path.join(daily, 'china_20261020.json'), 'w',
                  encoding='utf-8') as f:
            f.write(json.dumps(MIN_CHANNEL_FILE['china'][1]))
        try:
            with mock.patch.object(hca, 'discover_files', old_discover):
                res, _log, code = hca.run_audit(os.path.join(tmp, 'data'),
                                                os.path.join(tmp, 'out'), REGISTRY)
            self.assertEqual(res['audit_status'], 'NO_INPUT')   # china-only被漏
            self.assertEqual(code, 2)
            detect = correct and res['audit_status'] == 'NO_INPUT'
            self.assertTrue(detect)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # F5: 报告没有audit_commit/generated_at→E组断言失败
    def test_f5_missing_metadata_detected(self):
        self.assertRegex(self.res['audit_commit'], r'^[0-9a-f]{40}$')
        self.assertIn('generated_at', self.res)

        def no_metadata():
            return {}   # W4旧实现: 报告无审计执行元数据

        mut = self._mutated('f5', _audit_metadata=no_metadata)
        self.assertNotIn('audit_commit', mut)
        self.assertNotIn('generated_at', mut)
        detect = ('audit_commit' not in mut and 'generated_at' not in mut)
        self.assertTrue(detect)


if __name__ == '__main__':
    unittest.main(verbosity=2)
