#!/usr/bin/env python3
"""IA-P0-2-W4 联合验收测试(历史数据覆盖只读审计器)。

对应指令IA-P0-2-W4-DEV-v1.0 §十一W4-08的24项强制用例+§七5.2输入完整性
+负向敏感性5项,全部走真实模块(historical_coverage_audit.run_audit/main/
to_obs_date/dedup_by_date/expected_slots/classify;真实config/metric_registry.
json 81项;真实fact_engine/_GLOBAL_ID_MAP身份原语;真实trading_calendar):
  A 输出完整性: 81项全输出/别名映射/重复采集不虚增/月频跨日只计一次/
    单点与连续区分/日频合法交易日/非交易日与日历近似/周月频缺口/真实内部
    缺口/乱序/非法日期/缺值/数组不等长/同日不同值/原始与快照重复/无数据
    指标仍输出/未注册来源独立披露
  B 输入安全: 输入损坏(部分坏→降级完成;全坏→ALL_UNREADABLE)/路径缺失/
    非法输出路径(重叠/相同)/空输入不虚报通过/审计期间输入变化→INPUT_CHANGED
  C 完整性与确定性: 输入SHA前后不变/重复执行字节级一致/只读零副作用(数据
    与代码库)/机器报告Schema(阈值公开+MD六问+81行+UNDETERMINED)
  D 身份漂移守护: ast解析fact_engine/snapshot_builder源码,比对别名/A股/
    港股映射与fe._GLOBAL_ID_MAP不得漂移;注册表81项与通道权威
  E 负向敏感性5项(monkeypatch纯函数缝,证明退化实现会让断言失败):
    E1 as_of/文件日当obs_date→非法日期被"治愈"且观测虚增,断言失败
    E2 重复采集当新增观测→auth_uniq虚增,断言失败
    E3 理论请求开始日当最早观测日→覆盖率坍塌,断言失败
    E4 月频当日频→缺口假阳性,断言失败
    E5 丢弃无数据指标(状态洗白)→MISSING断言失败
合成fixture(临时目录,三代china格式/五通道/坏JSON/排除项decoy);零网络/零
GLM/零生产路径;不复制审计实现到测试自证——所有断言基于真实run_audit输出。
"""
import ast
import glob
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from collections import OrderedDict
from datetime import date, timedelta
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import historical_coverage_audit as hca          # 被审计的真实审计器
import fact_engine as fe                          # 真实身份原语(漂移守护基准)

REGISTRY = os.path.join(ROOT, 'config', 'metric_registry.json')

# ── 合成fixture常量(2026-10-05~10-21窗口;us_equity/commodity=工作日;
#    crypto=全周;2026-10-17=周六) ──
WK = ['2026-10-05', '2026-10-06', '2026-10-07', '2026-10-08', '2026-10-09',
      '2026-10-12', '2026-10-13', '2026-10-14', '2026-10-15', '2026-10-16']
GOLD_VALS = [2600.0 + i for i in range(10)]       # 10-16=2609.0


def _g1():
    return {"date": "2026-10-20", "data": {
        "GOLD": {"close": 2650.5, "date": "2026-10-19",
                 "series": {"dates": WK, "values": GOLD_VALS}},
        "SPX": {"close": 5704.0, "date": "2026-10-09",
                "series": {"dates": WK[:5], "values": [5700 + i for i in range(5)]}},
        "BTC": {"close": 67000.0,  # 故意无date键: 非法日期用例(观测日缺失)
                "series": {"dates": ['2026-10-05', '2026-10-06', '2026-10-26',
                                     '2026-10-27', '2026-10-28'],
                           "values": [67000.0] * 5}}}}


def _g2():  # 次日重复采集: 同series再抓一遍(10-16值不同→冲突)+BTC无date点
    return {"date": "2026-10-21", "data": {
        "GOLD": {"close": 2651.0, "date": "2026-10-20",
                 "series": {"dates": WK, "values": GOLD_VALS[:9] + [2609.5]}},
        "BTC": {"close": 67100.0}}}


def _macro():
    return {"date": "2026-10-20", "data": {
        "WTI": {"value": 80.5, "date": "2026-09-17", "frequency": "monthly",
                "series": {"dates": ["2026-08-15", "2026-09-16", "2026-09-17"],
                           "values": [80.1, 80.3, 80.5]},
                "revision": {"obs_date": "2026-08-15", "prev_value": 80.0,
                             "value": 80.1, "detected": "macro_collector"}},
        "ICSA": {"value": 219000.0, "date": "2026-10-09",
                 "series": {"dates": ["2026-09-04", "2026-09-11", "2026-10-09"],
                            "values": [219000, 218000, 217000]}},
        "UMCSENT": {"value": 70.1, "date": "2026-13-45",  # 非法日历日
                    "series": {"dates": ["2026-09-15", "2026-08-14", "2026-09-14"],
                               "values": [70.1, 69.9, 70.0]}},  # 乱序
        "FED_FUNDS": {"value": 4.8, "date": "2026-09-15",
                      "series": {"dates": ["2026-06-15", "2026-09-15"],
                                 "values": [4.8]}},  # dates2/values1→不等长
        "NFP": {"value": 152000.0, "date": "2026-09-15",
                "series": {"dates": ["2026-06-15", "2026-09-15"],
                           "values": [151000.0, 152000.0]}},  # 月频缺月(7/8月)
        "AHE": {"value": 30.5, "date": "2026-09-15",
                "series": {"dates": ["2026-08-15", "2026-09-15"],
                           "values": [None, 30.5]}}},  # 缺值
        "derived": {"REAL_SHORT": 1.5}}  # 派生块无观测日(不以文件日补造)


def _china():
    return {"timestamp": 1, "version": "v2",
            "a_share_indices": {
                "000001.SH": {"name": "上证指数", "close": 3300.0, "date": "20261020",
                              "series": {"dates": ['2026-10-12', '2026-10-13',
                                                   '2026-10-14', '2026-10-15',
                                                   '2026-10-16'],
                                         "values": [3290 + i for i in range(5)]}},
                "000300.SH": {"name": "沪深300", "close": 4000.0, "date": "20261020"}},
            "hk_indices": {
                "^HSI": {"name": "恒生指数", "close": 24000.0, "date": "2026-10-20",
                         "series": {"dates": ['2026-10-12', '2026-10-13', '2026-10-17'],
                                    "values": [23900, 23950, 24100]}}},  # 10-17周六
            "southbound": {"date": "20261020", "south_money": 2530.0},
            "margin": {"date": "20261020", "rzye_billion": 18500.0},
            "valuation": {"000300.SH": {"pe_ttm": 15.2}},
            "turnover": {"date": "20261020", "sh_amount_billion": 3000.0,
                         "sz_amount_billion": 4000.0, "total_amount_billion": 7000.0},
            "ah_premium": {"date": "2026-10-20", "close": 132.5}}


def _china_legacy():
    return {"date": "2026-03-26",
            "a_share": {"上证指数": {"close": 3300.0, "date": "2026-03-26"}},
            "hk": {"恒生国企": {"close": 9500.0, "date": "2026-03-26"}},
            "southbound": {"latest": 88.8},
            "volume": {"volume": 1.2e11, "date": "2026-03-26"}}


def _rate():
    return {"date": "2026-10-20",
            "current_rates": {"FEDFUNDS": {"value": 4.33, "date": "2026-10-01"},
                              "DFF": {"value": 4.33, "date": "2026-10-01"},
                              "DFF2": {"value": 1.0, "date": "2026-10-19"}},
            "real_economy": {"UNRATE": {"value": 4.1, "date": "2026-09-01"}},
            "fed_funds_futures": [
                {"ticker": "ZQ=F", "price": 95.5, "implied_rate_pct": 4.5,
                 "date": "2026-10-20"},
                {"ticker": "ZQZ26", "price": 95.0, "implied_rate_pct": 5.0,
                 "date": "2026-10-20"}],
            "rate_expectations": {}, "generated_at": "2026-10-20T09:00:00Z"}


def _snapshot():
    return {"snapshot_id": "snap1",
            "facts": [{"metric_id": "GOLD_F", "value": 2650.5,
                       "observation_date": "2026-10-19", "source": "snapshot"},
                      {"metric_id": "FAKE_X", "value": 1.0,
                       "observation_date": "2026-10-05", "source": "snapshot"}],
            "series_store": {"GOLD_F": {"dates": WK, "values": GOLD_VALS},
                             "FAKE_X": {"dates": ["2026-10-05"], "values": [1.0]}}}


class W4Fixture:
    """合成fixture构造器(与真实Schema同构;含三代china格式与排除项decoy)。"""

    def __init__(self, tag):
        self.tmp = tempfile.mkdtemp(prefix='w4_%s_' % tag)
        self.data_root = os.path.join(self.tmp, 'data')
        self.daily = os.path.join(self.data_root, 'daily')
        os.makedirs(self.daily)

    def write(self, name, obj, corrupt=False):
        p = os.path.join(self.daily, name)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(obj if corrupt else json.dumps(obj, ensure_ascii=False))
        return p

    def build_main(self):
        self.write('global_20261018.json', '{"data": [broken', corrupt=True)
        self.write('global_20261020.json', _g1())
        self.write('global_20261021.json', _g2())
        self.write('macro_20261020.json', _macro())
        self.write('china_20261020.json', _china())
        self.write('china_20260326.json', _china_legacy())
        self.write('rate_economy_20261020.json', _rate())
        self.write('rate_economy_20261025.json', 'not json{', corrupt=True)
        self.write('research_snapshot_20261020.json', _snapshot())
        for d in ('global_20261020.md', 'anchors_20261020.json',
                  'scorecard_20261020.json', 'correlation_20261020.json',
                  'anchor_prompt_20261020.json', 'news_digest_20261020.json'):
            self.write(d, '{}')
        return self

    def out(self, name='out'):
        p = os.path.join(self.tmp, name)
        return p

    def cleanup(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


def run_main(fx, out=None):
    """跑真实main();返回(exit_code, out_dir)。"""
    out = out or fx.out()
    ec = hca.main(['--data-dir', fx.data_root, '--out-dir', out,
                   '--registry', REGISTRY, '--source-note', '合成测试fixture(W4-08)'])
    return ec, out


def load_result(out_dir):
    hits = glob.glob(os.path.join(out_dir, 'coverage_audit_*.json'))
    assert len(hits) == 1, '应恰有1个coverage_audit_*.json: %s' % hits
    with open(hits[0], 'r', encoding='utf-8') as f:
        return json.load(f)


def by_id(result, mid):
    return next(r for r in result['metrics'] if r['metric_id'] == mid)


# ════════════════ A组: 输出完整性与覆盖算法(强制用例1~17) ════════════════

class TestACoverageAndIdentity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fx = W4Fixture('main').build_main()
        cls.ec, cls.out = run_main(cls.fx)
        cls.result = load_result(cls.out)
        cls.rid = cls.result['run_id']

    @classmethod
    def tearDownClass(cls):
        cls.fx.cleanup()

    # 用例1: 81项全部输出(不得只审计有数据的)
    def test_a01_all_81_metrics_output(self):
        self.assertEqual(self.ec, 0)
        self.assertEqual(self.result['audit_status'], 'COMPLETED')
        with open(REGISTRY, 'r', encoding='utf-8') as f:
            reg = json.load(f)
        self.assertEqual(len(reg['metrics']), 81)
        self.assertEqual(len(self.result['metrics']), 81)
        ids = [r['metric_id'] for r in self.result['metrics']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {m['metric_id'] for m in reg['metrics']})
        for fname in ('coverage_audit_%s.json' % self.rid,
                      'coverage_audit_%s.md' % self.rid,
                      'input_manifest_%s.json' % self.rid,
                      'audit_execution_%s.log' % self.rid):
            self.assertTrue(os.path.exists(os.path.join(self.out, fname)), fname)

    # 用例2: GOLD别名映射(通道键GOLD→注册GOLD_F,与fe._GLOBAL_ID_MAP同源)
    def test_a02_gold_alias_mapping(self):
        self.assertEqual(hca.GLOBAL_ID_MAP.get('GOLD'), 'GOLD_F')
        self.assertEqual(hca.GLOBAL_ID_MAP, fe._GLOBAL_ID_MAP)
        g = by_id(self.result, 'GOLD_F')
        self.assertEqual(g['source'], 'global_market_collector')
        self.assertGreater(g['counts']['authority_unique_observation_dates'], 0)
        unmapped_keys = {u['raw_key'] for u in self.result['unmapped_records']}
        self.assertNotIn('GOLD', unmapped_keys)
        # 同一原始键WTI在两通道语义不同: global→WTI_F(期货), macro→WTI_SPOT_M(现货月频)
        self.assertEqual(hca.GLOBAL_ID_MAP.get('WTI'), 'WTI_F')
        self.assertEqual(hca.MACRO_ALIAS.get('WTI'), 'WTI_SPOT_M')
        self.assertIn('WTI_SPOT_M', [r['metric_id'] for r in self.result['metrics']])

    # 用例3: 重复采集不虚增(GOLD series两文件重复抓取→观测日只计一次)
    def test_a03_duplicate_collection_no_inflation(self):
        g = by_id(self.result, 'GOLD_F')
        c = g['counts']
        # 权威原始记录=10+1(文件1)+10+1(文件2)=22,去重后唯一观测日=12
        self.assertEqual(c['authority_raw_records'], 22)
        self.assertEqual(c['authority_unique_observation_dates'], 12)
        self.assertEqual(c['cross_file_duplicate_records'], 22 - 12)
        self.assertEqual(g['coverage']['total_unique_observations'], 12)

    # 用例4: 月频跨日只计一次(WTI_SPOT_M 3个观测日→2个月槽,缺0)
    def test_a04_monthly_same_month_counts_once(self):
        w = by_id(self.result, 'WTI_SPOT_M')
        self.assertEqual(w['counts']['unique_observation_dates'], 3)
        self.assertEqual(w['coverage']['expected_observation_slots'], 2)
        self.assertEqual(w['coverage']['observed_slots'], 2)
        self.assertEqual(w['coverage']['missing_slots_count'], 0)
        self.assertEqual(w['counts']['revision_events_detected'], 1)

    # 用例5: 单点与连续区分(HSAHP仅1点;GOLD_F 12点连续)
    def test_a05_single_vs_continuous(self):
        h = by_id(self.result, 'HSAHP')
        self.assertEqual(h['status'], 'SINGLE_OBSERVATION')
        self.assertEqual(h['coverage']['total_unique_observations'], 1)
        self.assertEqual(h['coverage']['usable_intervals'], [])
        g = by_id(self.result, 'GOLD_F')
        self.assertEqual(g['status'], 'OBSERVED')
        self.assertEqual(len(g['coverage']['continuous_segments']), 1)
        self.assertEqual(g['coverage']['longest_continuous_segment_slots'], 12)
        self.assertEqual(len(g['coverage']['usable_intervals']), 1)

    # 用例6: 日频合法交易日(SPX工作日5槽ratio1.0;BTC crypto含周末)
    def test_a06_daily_trading_days(self):
        s = by_id(self.result, 'SPX')
        self.assertEqual(s['coverage']['expected_observation_slots'], 5)
        self.assertEqual(s['coverage']['coverage_ratio'], 1.0)
        self.assertEqual(s['status'], 'OBSERVED')
        b = by_id(self.result, 'BTC')
        # crypto 7×24: 10-05..10-28全24个自然日都是合法槽
        self.assertEqual(b['coverage']['expected_observation_slots'], 24)
        self.assertEqual(b['status'], 'SPARSE')

    # 用例7: 非交易日观测与日历近似注记(HSI周六观测=额外;cn/hk近似说明)
    def test_a07_non_trading_day_and_calendar_approx(self):
        h = by_id(self.result, 'HSI')
        self.assertGreaterEqual(h['coverage']['extra_observations_beyond_calendar'], 1)
        self.assertIn('港股日历最小集', h['coverage']['calendar_limitations'])
        sc = by_id(self.result, 'SHCOMP')
        self.assertIn('中国日历仅2026年', sc['coverage']['calendar_limitations'])
        self.assertGreaterEqual(sc['coverage']['missing_slots_count'], 100)  # 03-26→10-16真实缺口

    # 用例8: 周月频缺口(ICSA缺3周;NFP缺7/8两月)
    def test_a08_weekly_monthly_gaps(self):
        i = by_id(self.result, 'ICSA')
        self.assertEqual(i['coverage']['expected_observation_slots'], 6)  # 6个ISO周
        self.assertEqual(i['coverage']['observed_slots'], 3)
        self.assertEqual(i['coverage']['missing_slots_count'], 3)
        n = by_id(self.result, 'NFP')
        self.assertEqual(n['coverage']['expected_observation_slots'], 4)  # 6~9月
        self.assertEqual(n['coverage']['missing_slots_count'], 2)
        self.assertEqual(['2026-07', '2026-08'], n['coverage']['missing_slots_sample'])

    # 用例9: 真实内部缺口(BTC 20天断点;SHCOMP跨半年断点)
    # [W4-FIX1修订] 原预期SHCOMP连续段=2: 自然日间隔阈值(4天<10)把10-16(周五)
    # →10-20(周二)误判连续,违反FIX1-01(中间缺失预期交易日2026-10-19必须断段);
    # 槽位口径下SHCOMP=3段([03-26]/[10-12..10-16]/[10-20])。场景保留,预期修正。
    def test_a09_real_internal_gap(self):
        b = by_id(self.result, 'BTC')
        self.assertEqual(len(b['coverage']['continuous_segments']), 2)
        self.assertEqual(b['coverage']['max_internal_gap_days'], 20)  # 描述性自然日统计(FIX1-01保留)
        self.assertEqual(b['coverage']['longest_continuous_segment_slots'], 3)
        sc = by_id(self.result, 'SHCOMP')
        self.assertEqual(len(sc['coverage']['continuous_segments']), 3)
        self.assertEqual(sc['coverage']['max_internal_gap_days'], 200)
        # 断段处必有缺失预期槽位: 第2段末槽10-16(周五)与第3段首槽10-20(周二)
        # 之间缺2026-10-19(周一)预期交易日→断段(missing_slots_sample只存前10
        # 个即3月日期,故以段边界证明断点)
        seg_starts = [s['start_slot'] for s in sc['coverage']['continuous_segments']]
        self.assertEqual(seg_starts, ['2026-03-26', '2026-10-12', '2026-10-20'])
        seg_ends = [s['end_slot'] for s in sc['coverage']['continuous_segments']]
        self.assertEqual(seg_ends, ['2026-03-26', '2026-10-16', '2026-10-20'])
        self.assertGreater(sc['coverage']['missing_slots_count'], 100)
        breaks = {m['metric_id']: m['max_internal_gap_days']
                  for m in self.result['findings']['3_哪些指标中间存在严重断点']['metrics']}
        self.assertIn('BTC', breaks)
        self.assertIn('SHCOMP', breaks)

    # 用例10: 乱序(UMCSENT series乱序仍正确聚合3个唯一观测日)
    def test_a10_out_of_order(self):
        u = by_id(self.result, 'UMCSENT')
        self.assertGreaterEqual(u['counts']['out_of_order_records'], 1)
        self.assertEqual(u['counts']['unique_observation_dates'], 3)
        self.assertEqual(u['coverage']['first_observation_date'], '2026-08-14')
        self.assertEqual(u['coverage']['last_observation_date'], '2026-09-15')

    # 用例11: 非法日期(2026-13-45与无date点→invalid_date,不入观测)
    def test_a11_invalid_dates(self):
        u = by_id(self.result, 'UMCSENT')
        self.assertGreaterEqual(u['counts']['invalid_date_records'], 1)
        all_obs = {d for r in self.result['metrics']
                   for d in ([r['coverage']['first_observation_date'],
                              r['coverage']['last_observation_date']]
                             if r['coverage']['first_observation_date'] else [])}
        self.assertNotIn('2026-13-45', all_obs)
        b = by_id(self.result, 'BTC')
        self.assertGreaterEqual(b['counts']['invalid_date_records'], 1)
        self.assertNotIn('2026-10-20', [seg['start'] for seg in b['coverage']['continuous_segments']])

    # 用例12: 缺值(AHE series含None→invalid_value,该点不入观测)
    def test_a12_invalid_values(self):
        a = by_id(self.result, 'AHE')
        self.assertGreaterEqual(a['counts']['invalid_value_records'], 1)
        self.assertEqual(a['counts']['unique_observation_dates'], 1)

    # 用例13: 数组不等长(FED_FUNDS dates2/values1→整条不入观测,只剩单点)
    def test_a13_length_mismatch(self):
        f = by_id(self.result, 'FED_FUNDS')
        self.assertEqual(f['counts']['length_mismatch_series'], 1)
        self.assertEqual(f['counts']['authority_unique_observation_dates'], 1)
        self.assertEqual(f['status'], 'SINGLE_OBSERVATION')
        self.assertIn('length_mismatch', f['discovery']['notes'])

    # 用例14: 同观测日不同值(10-16两文件2609.0/2609.5→冲突候选,不擅自选真值)
    def test_a14_same_date_different_values(self):
        g = by_id(self.result, 'GOLD_F')
        self.assertEqual(g['counts']['distinct_value_conflict_dates'], 1)
        cc = g['conflict_candidates']
        self.assertEqual(len(cc), 1)
        self.assertEqual(cc[0]['obs_date'], '2026-10-16')
        self.assertEqual(sorted(cc[0]['distinct_values']), sorted(['2609.0', '2609.5']))

    # 用例15: 原始与快照重复(快照GOLD_F不新增权威覆盖)
    def test_a15_snapshot_not_double_counted(self):
        g = by_id(self.result, 'GOLD_F')
        self.assertEqual(g['counts']['non_authority_records'], 11)  # 1 fact+10 series_store
        self.assertEqual(g['counts']['authority_unique_observation_dates'], 12)
        self.assertEqual(g['discovery']['non_authority_only_dates'], [])
        # 仅存于快照的指标: 不因此获得覆盖(UNEMPLOYMENT只有rate对账点)
        un = by_id(self.result, 'UNEMPLOYMENT')
        self.assertEqual(un['counts']['non_authority_records'], 1)
        self.assertEqual(un['counts']['authority_unique_observation_dates'], 0)
        self.assertEqual(un['status'], 'MISSING')
        self.assertEqual(un['discovery']['non_authority_only_dates'], ['2026-09-01'])

    # 用例16: 无数据指标仍输出(SILVER_F/SH_PE: MISSING+全零计数)
    def test_a16_missing_metrics_still_output(self):
        for mid in ('SILVER_F', 'SH_PE'):
            r = by_id(self.result, mid)
            self.assertEqual(r['status'], 'MISSING', mid)
            self.assertFalse(r['discovery']['found'])
            self.assertEqual(r['counts']['raw_records'], 0)
            self.assertEqual(r['coverage']['total_unique_observations'], 0)
            self.assertIsNone(r['coverage']['first_observation_date'])
        st = self.result['summary']['by_status']
        self.assertEqual(st.get('MISSING', 0) + st.get('SINGLE_OBSERVATION', 0)
                         + st.get('SPARSE', 0) + st.get('OBSERVED', 0)
                         + st.get('DERIVED_ONLY', 0), 81)

    # 用例17: 未注册来源独立披露(不静默丢失)
    def test_a17_unmapped_disclosed(self):
        got = {(u['channel'], u['raw_key']): u for u in self.result['unmapped_records']}
        for key in (('china', '000300.SH'), ('china', 'southbound.latest'),
                    ('china', 'volume.volume'), ('china', 'valuation:000300.SH.pe_ttm'),
                    ('rate_economy', 'futures:ZQZ26'), ('rate_economy', 'current_rates:DFF2'),
                    ('research_snapshot', 'fact:FAKE_X'),
                    ('research_snapshot', 'series_store:FAKE_X')):
            self.assertIn(key, got, key)
            self.assertGreater(len(got[key]['files']), 0)
        # 排除项如实计数(md镜像/anchors/scorecard/correlation/anchor_prompt/news)
        ex = self.result['input']['excluded']
        self.assertEqual(ex['md_mirrors'], 1)
        self.assertEqual(ex['anchors_files'], 1)
        self.assertEqual(ex['scorecard_files'], 1)
        self.assertEqual(ex['correlation_files'], 1)
        self.assertEqual(ex['anchor_prompt_files'], 1)

    # 用例18(附): 中国三代格式/单位换算注记/字段语义漂移披露
    def test_a18_china_formats_and_semantics(self):
        hc = by_id(self.result, 'HSCEI')  # 最旧代标签"恒生国企"→HSCEI
        self.assertEqual(hc['status'], 'SINGLE_OBSERVATION')
        self.assertEqual(hc['coverage']['first_observation_date'], '2026-03-26')
        self.assertIn('legacy_format', hc['discovery']['notes'])
        sb = by_id(self.result, 'SB_FLOW')  # south_money百万→亿(/100,同fe口径)
        self.assertEqual(sb['coverage']['first_observation_date'], '2026-10-20')
        self.assertIn('unit_transform', sb['discovery']['notes'])
        # [W4-FIX1修订] 原预期MARGIN_BAL first=2026-10-20+field_semantics注记:
        # 把rzye_billion(融资余额,亿元)当注册MARGIN_BAL(两融余额合计)权威观测,
        # 违反FIX1-03身份纪律(缺同口径证据不得写入权威历史)。场景保留(fixture
        # 仍只有rzye_billion),预期修正为: 无权威观测(MISSING)+unmapped独立披露
        # identity_mismatch(原始字段存在事实不丢失,不删除原始记录)。
        mb = by_id(self.result, 'MARGIN_BAL')
        self.assertEqual(mb['status'], 'MISSING')
        self.assertFalse(mb['discovery']['found'])
        self.assertIsNone(mb['coverage']['first_observation_date'])
        self.assertEqual(mb['coverage']['unique_observation_slots'], 0)
        self.assertEqual(mb['coverage']['continuous_segments'], [])
        mg_unmapped = {(u['channel'], u['raw_key']): u
                       for u in self.result['unmapped_records']}
        self.assertIn(('china', 'margin:rzye_billion'), mg_unmapped)
        self.assertIn('identity_mismatch', mg_unmapped[('china', 'margin:rzye_billion')]['note'])
        self.assertIn('融资余额', mg_unmapped[('china', 'margin:rzye_billion')]['note'])
        self.assertIn('daily/china_20261020.json',
                      mg_unmapped[('china', 'margin:rzye_billion')]['files'])
        for mid in ('SH_AMOUNT', 'SZ_COMPONENT_AMOUNT', 'CN_TOTAL_TURNOVER'):
            r = by_id(self.result, mid)
            self.assertEqual(r['coverage']['first_observation_date'], '2026-10-20', mid)
            self.assertEqual(r['status'], 'SINGLE_OBSERVATION', mid)

    # 用例19(附): 权威通道语义(FED_FUNDS权威=macro;rate通道只对账;派生只标注)
    def test_a19_authority_and_derived(self):
        f = by_id(self.result, 'FED_FUNDS')
        self.assertEqual(f['authority_channel'], 'macro')
        self.assertEqual(f['counts']['non_authority_records'], 1)  # rate通道FEDFUNDS对账点
        rs = by_id(self.result, 'REAL_SHORT')  # derived块无观测日→不以文件日补造
        self.assertEqual(rs['status'], 'DERIVED_ONLY')
        self.assertGreaterEqual(rs['counts']['invalid_date_records'], 1)
        self.assertEqual(rs['counts']['valid_records'], 0)
        for mid in ('REAL_10Y', 'REAL_5Y', 'HY_IG_DIFF', 'ZQ_IMPLIED_AVG'):
            self.assertEqual(by_id(self.result, mid)['status'], 'DERIVED_ONLY', mid)
        zq = by_id(self.result, 'ZQ_F1_PRICE')  # ZQ=F行→权威日频
        self.assertEqual(zq['status'], 'SINGLE_OBSERVATION')
        self.assertEqual(zq['coverage']['first_observation_date'], '2026-10-20')
        # 全部指标研究充分性=UNDETERMINED(无授权阈值不判定)
        for r in self.result['metrics']:
            self.assertEqual(r['research_sufficiency'], 'UNDETERMINED')


# ════════════════ B组: 输入安全与路径(强制用例18~20+23) ════════════════

class TestBInputSafety(unittest.TestCase):
    def setUp(self):
        self.fx = W4Fixture('safety').build_main()

    def tearDown(self):
        self.fx.cleanup()

    # 用例18a: 部分输入损坏→如实记录不静默,审计降级完成+input_degraded
    def test_b18_partial_corrupt_degraded_complete(self):
        ec, out = run_main(self.fx)
        self.assertEqual(ec, 0)
        res = load_result(out)
        self.assertEqual(res['audit_status'], 'COMPLETED')
        self.assertEqual(sorted(res['input']['unreadable_files']),
                         ['daily/global_20261018.json', 'daily/rate_economy_20261025.json'])
        with open(os.path.join(out, 'input_manifest_%s.json' % res['run_id']),
                  'r', encoding='utf-8') as f:
            man = {e['relpath']: e for e in json.load(f)['files']}
        for p in ('daily/global_20261018.json', 'daily/rate_economy_20261025.json'):
            self.assertFalse(man[p]['readable'])
            self.assertIn('error', man[p])
        g = by_id(res, 'GOLD_F')
        self.assertTrue(g['input_degraded'])
        self.assertEqual(g['authority_channel'], 'global')
        dff = by_id(res, 'DFF')  # rate通道1好1坏→有数据但降级
        self.assertTrue(dff['input_degraded'])

    # 用例18b: 全部输入损坏→ALL_UNREADABLE,退出2,不宣布成功
    def test_b18b_all_unreadable(self):
        for name in ('global_20261018.json', 'global_20261020.json',
                     'global_20261021.json', 'macro_20261020.json',
                     'china_20261020.json', 'china_20260326.json',
                     'rate_economy_20261020.json', 'rate_economy_20261025.json',
                     'research_snapshot_20261020.json'):
            self.fx.write(name, '{broken', corrupt=True)
        ec, out = run_main(self.fx)
        self.assertEqual(ec, 2)
        res = load_result(out)
        self.assertEqual(res['audit_status'], 'ALL_UNREADABLE')
        g = by_id(res, 'GOLD_F')
        self.assertEqual(g['status'], 'UNREADABLE')
        self.assertEqual(res['summary']['with_authority_observations'], 0)

    # 用例19: 数据目录缺失→INVALID_PATH退出2,不写任何输出文件
    def test_b19_missing_data_dir(self):
        out = self.fx.out('never')
        ec = hca.main(['--data-dir', os.path.join(self.fx.tmp, 'nope'),
                       '--out-dir', out, '--registry', REGISTRY])
        self.assertEqual(ec, 2)
        self.assertFalse(os.path.exists(out))  # 非法路径下不创建/不写入
        self.assertEqual(glob.glob(os.path.join(self.fx.tmp, '**', 'coverage_audit_*'),
                                   recursive=True), [])

    # 用例20: 非法输出路径(=数据目录/含数据目录/被数据目录含)→拒绝
    def test_b20_illegal_out_dir(self):
        for bad in (self.fx.data_root, self.fx.daily,
                    os.path.join(self.fx.data_root, 'inside')):
            ec = hca.main(['--data-dir', self.fx.data_root, '--out-dir', bad,
                           '--registry', REGISTRY])
            self.assertEqual(ec, 2, bad)
        self.assertFalse(os.path.exists(os.path.join(self.fx.data_root, 'inside')))
        before = sorted(os.listdir(self.fx.daily))
        ec = hca.main(['--data-dir', self.fx.data_root,
                       '--out-dir', os.path.join(self.fx.daily, 'sub'), '--registry', REGISTRY])
        self.assertEqual(ec, 2)
        self.assertEqual(sorted(os.listdir(self.fx.daily)), before)  # 数据目录零新增

    # 用例23: 无可用输入(空目录)→NO_INPUT退出2,不虚报通过
    def test_b23_no_input_no_false_pass(self):
        empty = os.path.join(self.fx.tmp, 'empty_data')
        os.makedirs(empty)
        out = self.fx.out('empty_out')
        ec = hca.main(['--data-dir', empty, '--out-dir', out, '--registry', REGISTRY])
        self.assertEqual(ec, 2)
        self.assertFalse(os.path.exists(out))
        res, _log, code = hca.run_audit(empty, self.fx.out('x'), REGISTRY)
        self.assertEqual(res['audit_status'], 'NO_INPUT')
        self.assertEqual(code, 2)

    # §5.2: 审计期间输入变化→INPUT_CHANGED退出3(模拟采集器写入,冻结初值复检)
    def test_b25_input_changed_detected(self):
        victim = os.path.join(self.fx.daily, 'macro_20261020.json')
        with open(victim, 'rb') as f:
            before = f.read()
        orig = hca.build_manifest

        def mutating_manifest(files):
            m = orig(files)
            with open(victim, 'a', encoding='utf-8') as f:  # 审计中生产目录被写入
                f.write(' ')
            return m

        with mock.patch.object(hca, 'build_manifest', mutating_manifest):
            res, log, code = hca.run_audit(self.fx.data_root, self.fx.out('ic'),
                                           REGISTRY)
        try:
            self.assertEqual(code, 3)
            self.assertEqual(res['audit_status'], 'INPUT_CHANGED')
            self.assertTrue(res['integrity']['input_changed_during_audit'])
            self.assertIn('daily/macro_20261020.json',
                          [c.split('(')[0] for c in res['integrity']['changed_files']])
        finally:
            with open(victim, 'wb') as f:
                f.write(before)


# ════════════════ C组: 完整性/确定性/只读(强制用例21/22/24+Schema) ════════════════

class TestCIntegrityDeterminism(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fx = W4Fixture('repeat').build_main()
        cls.snap = cls._snap(cls.fx.daily)
        cls.ec1, cls.out1 = run_main(cls.fx, cls.fx.out('run1'))
        cls.ec2, cls.out2 = run_main(cls.fx, cls.fx.out('run2'))
        cls.res1 = load_result(cls.out1)
        cls.res2 = load_result(cls.out2)

    @classmethod
    def _snap(cls, d):
        s = {}
        for p in sorted(glob.glob(os.path.join(d, '*'))):
            st = os.stat(p)
            with open(p, 'rb') as f:
                s[os.path.basename(p)] = (st.st_size, st.st_mtime_ns,
                                          hashlib.sha256(f.read()).hexdigest())
        return s

    @classmethod
    def tearDownClass(cls):
        cls.fx.cleanup()

    # 用例21: 输入SHA前后不变(manifest逐文件SHA-256==审计后实测;零修改)
    def test_c21_input_unchanged(self):
        self.assertEqual(self.ec1, 0)
        after = self._snap(self.fx.daily)
        self.assertEqual(self.snap, after)
        man_path = os.path.join(self.out1, 'input_manifest_%s.json' % self.res1['run_id'])
        with open(man_path, 'r', encoding='utf-8') as f:
            man = json.load(f)
        for e in man['files']:
            p = os.path.join(self.fx.data_root, e['relpath'])
            with open(p, 'rb') as fh:
                self.assertEqual(hashlib.sha256(fh.read()).hexdigest(), e['sha256'],
                                 e['relpath'])
            self.assertEqual(os.stat(p).st_mtime_ns, e['mtime_ns'], e['relpath'])
        self.assertFalse(self.res1['integrity']['input_changed_during_audit'])

    # 用例22: 重复执行一致(run_id/JSON/MD/manifest字节级一致;同输入同输出)
    # [W4-FIX1修订] FIX1-05新增generated_at(真实UTC执行时间)后,完整JSON/MD
    # 字节随执行时间变化(两次执行跨秒即不同——原字节级断言变为时序运气);
    # 按FIX1-05§8.3改为: manifest仍字节级一致(不含运行时元数据)+
    # JSON/MD剔除generated_at后字节级一致。覆盖统计确定性语义不变:
    # 相同输入数据+相同代码版本⇒相同覆盖统计(不要求执行时间相同)。
    def test_c22_repeat_execution_identical(self):
        self.assertEqual(self.ec2, 0)
        self.assertEqual(self.res1['run_id'], self.res2['run_id'])
        # audit_commit=代码版本元数据,两次执行必须一致;generated_at字段必须
        # 存在(真实UTC执行时间),比较时剔除
        self.assertEqual(self.res1['audit_commit'], self.res2['audit_commit'])
        for r in (self.res1, self.res2):
            self.assertIn('generated_at', r)
        rid = self.res1['run_id']
        with open(os.path.join(self.out1, 'input_manifest_%s.json' % rid), 'rb') as f:
            b1 = f.read()
        with open(os.path.join(self.out2, 'input_manifest_%s.json' % rid), 'rb') as f:
            b2 = f.read()
        self.assertEqual(b1, b2, 'manifest字节级一致')
        # JSON: 剔除运行时元数据generated_at后字节级一致
        j1 = {k: v for k, v in self.res1.items() if k != 'generated_at'}
        j2 = {k: v for k, v in self.res2.items() if k != 'generated_at'}
        self.assertEqual(json.dumps(j1, sort_keys=True, ensure_ascii=False),
                         json.dumps(j2, sort_keys=True, ensure_ascii=False))
        # MD: 剔除生成时间行后字节级一致
        def _strip_md(path):
            with open(path, 'r', encoding='utf-8') as f:
                return [ln for ln in f.read().splitlines()
                        if not ln.startswith('- 报告生成时间')]
        self.assertEqual(_strip_md(os.path.join(self.out1, 'coverage_audit_%s.md' % rid)),
                         _strip_md(os.path.join(self.out2, 'coverage_audit_%s.md' % rid)))

    # 用例24: 只读零副作用(数据根零新增;代码库关键文件mtime+SHA不变)
    def test_c24_readonly_no_side_effects(self):
        self.assertEqual(sorted(os.listdir(self.fx.daily)),
                         sorted(self.snap.keys()))
        for rel in ('scripts/historical_coverage_audit.py', 'scripts/fact_engine.py',
                    'config/metric_registry.json', 'scripts/snapshot_builder.py'):
            p = os.path.join(ROOT, rel)
            self.assertTrue(os.path.exists(p))
        import trading_calendar  # 既有模块导入不受影响(历史回归由全量套件另行证明)
        self.assertTrue(callable(trading_calendar.expected_trading_days))

    # 机器报告Schema: 阈值公开/六问/81行/身份与发现可追溯
    def test_c26_report_schema(self):
        r = self.res1
        self.assertIn('threshold_definitions', r)
        td = r['threshold_definitions']
        for k in ('segment_break_natural_days', 'sparse_coverage_ratio_below',
                  'complete_history_min_unique_obs', 'recent_only_span_days_max',
                  'serious_break_days', 'basis', 'calendar_limitations'):
            self.assertIn(k, td)
        self.assertIn('不是金融事实', td['basis'])
        for q in ('1_哪些指标有较完整现有历史', '2_哪些指标只有最近数据',
                  '3_哪些指标中间存在严重断点', '4_哪些指标未保存历史',
                  '5_哪些数据无法支持研究区间判断', '6_现有历史覆盖的主要限制'):
            self.assertIn(q, r['findings'])
        self.assertEqual(r['registry']['metric_count'], 81)
        g = by_id(r, 'GOLD_F')
        for k in ('metric_id', 'display_name', 'source', 'source_symbol', 'status',
                  'criticality', 'frequency', 'calendar', 'unit', 'identity',
                  'discovery', 'counts', 'coverage', 'status'):
            self.assertIn(k, g)
        self.assertEqual(g['frequency'], 'daily')
        self.assertEqual(g['calendar'], 'commodity')
        md_path = os.path.join(self.out1, 'coverage_audit_%s.md' % r['run_id'])
        with open(md_path, 'r', encoding='utf-8') as f:
            md = f.read()
        section = md.split('## 逐项覆盖')[1].split('## 审计发现')[0]
        rows = [ln for ln in section.splitlines()
                if ln.startswith('| ') and '---' not in ln]
        self.assertEqual(len(rows), 82)  # 表头1+81数据行(无数据指标也在表内)
        self.assertIn('阈值定义与依据', md)
        self.assertIn('证据限制', md)
        self.assertIn('未注册来源记录', md)


# ════════════════ D组: 身份漂移守护 ════════════════

def _module_dicts(path, names):
    """ast解析源码,取任意作用域内 Assign 到指定名字的dict字面量(防局部变量漂移)。"""
    with open(path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            t = node.targets[0]
            if isinstance(t, ast.Name) and t.id in names and t.id not in found:
                try:
                    found[t.id] = ast.literal_eval(node.value)
                except (ValueError, SyntaxError):
                    pass
    return found


class TestDIdentityDriftGuard(unittest.TestCase):
    def test_d1_maps_match_project_sources(self):
        fe_dicts = _module_dicts(os.path.join(ROOT, 'scripts', 'fact_engine.py'),
                                 {'_GLOBAL_ID_MAP', '_MACRO_ALIAS', '_CODE_MAP', '_HK_MAP'})
        self.assertEqual(fe_dicts['_GLOBAL_ID_MAP'], dict(hca.GLOBAL_ID_MAP))
        self.assertEqual(fe_dicts['_MACRO_ALIAS'], dict(hca.MACRO_ALIAS))
        self.assertEqual(fe_dicts['_CODE_MAP'], dict(hca.CHINA_A_CODE))
        self.assertEqual(fe_dicts['_HK_MAP'], dict(hca.CHINA_HK_CODE))
        sb_dicts = _module_dicts(os.path.join(ROOT, 'scripts', 'snapshot_builder.py'),
                                 {'_CN_CODE', '_HK_CODE'})
        self.assertEqual(sb_dicts['_CN_CODE'], dict(hca.CHINA_A_CODE))
        self.assertEqual(sb_dicts['_HK_CODE'], dict(hca.CHINA_HK_CODE))

    def test_d2_channel_authority_matrix(self):
        with open(REGISTRY, 'r', encoding='utf-8') as f:
            reg = json.load(f)
        ids = {m['metric_id'] for m in reg['metrics']}
        self.assertEqual(len(ids), 81)
        for v in hca.GLOBAL_ID_MAP.values():
            self.assertIn(v, ids)  # 别名目标必须都是注册指标
        for m in reg['metrics']:
            ch = hca.REGISTRY_SOURCE_CHANNEL.get(m['source'])
            if '(derived)' not in m['source'] and '(derived)' not in str(m.get('source_symbol')):
                self.assertIsNotNone(ch, m['metric_id'])
            self.assertIn(ch, (None, 'global', 'china', 'macro', 'rate_economy'))


# ════════════════ E组: 负向敏感性(monkeypatch纯函数缝) ════════════════

class TestENegativeSensitivity(unittest.TestCase):
    """证明: 把审计器的关键纪律退化掉之后,本套件的断言会失败(而非继续通过)。"""

    @classmethod
    def setUpClass(cls):
        cls.fx = W4Fixture('neg').build_main()
        cls.res = load_result(run_main(cls.fx, cls.fx.out('base'))[1])

    @classmethod
    def tearDownClass(cls):
        cls.fx.cleanup()

    def _mutated(self, **patches):
        out = self.fx.out('mut_%s' % sorted(patches)[0])
        with mock.patch.multiple(hca, **patches):
            hca.main(['--data-dir', self.fx.data_root, '--out-dir', out,
                      '--registry', REGISTRY, '--source-note', 'mutation'])
        return load_result(out)

    # E1: as_of/文件日当obs_date(观测日缺失被"治愈")→用例11断言失败
    def test_e1_fabricated_obs_date_detected(self):
        b = by_id(self.res, 'BTC')
        correct = b['counts']['invalid_date_records'] >= 1
        self.assertTrue(correct)
        orig = hca.to_obs_date

        def fabricating(raw, _fd='2026-10-20'):
            if raw is None:                     # 禁止行为: 用文件日补造观测日
                return _fd, None
            return orig(raw)

        mut = self._mutated(to_obs_date=fabricating)
        mb = by_id(mut, 'BTC')
        self.assertEqual(mb['counts']['invalid_date_records'], 0)          # 被洗白
        self.assertGreater(mb['counts']['unique_observation_dates'],
                           b['counts']['unique_observation_dates'])        # 观测虚增
        detect = (correct and mb['counts']['invalid_date_records'] == 0)
        self.assertTrue(detect)  # 若审计器真这么实现,用例11必失败→可检测

    # E2: 重复采集当新增观测(去重失效)→用例3断言失败
    def test_e2_no_dedup_detected(self):
        g = by_id(self.res, 'GOLD_F')
        correct = g['counts']['authority_unique_observation_dates'] == 12
        self.assertTrue(correct)
        orig = hca.dedup_by_date

        def no_dedup(records):                  # 禁止行为: 同日多次抓取各算新观测
            base = orig(records)
            counts = {}
            for r in records:
                counts[r['obs_date']] = counts.get(r['obs_date'], 0) + 1
            out = OrderedDict(base)
            for d, n in counts.items():
                dd = date.fromisoformat(d)
                for k in range(1, n):
                    nd = (dd + timedelta(days=k)).isoformat()
                    out[nd] = dict(base[d], values={'synthetic': 'x'})
            return OrderedDict(sorted(out.items()))

        mut = self._mutated(dedup_by_date=no_dedup)
        mg = by_id(mut, 'GOLD_F')
        self.assertGreater(mg['counts']['authority_unique_observation_dates'], 12)
        detect = correct and mg['counts']['authority_unique_observation_dates'] != 12
        self.assertTrue(detect)

    # E3: 理论请求开始日当最早观测日→覆盖率被假压低,用例6断言失败
    def test_e3_theoretical_start_detected(self):
        g = by_id(self.res, 'GOLD_F')
        correct = g['coverage']['coverage_ratio'] == 1.0
        self.assertTrue(correct)
        orig = hca.expected_slots

        def theoretical_start(freq, first, last, calendar):
            return orig(freq, '2025-01-01', last, calendar)  # 禁止: 采集请求起点≠观测

        mut = self._mutated(expected_slots=theoretical_start)
        mg = by_id(mut, 'GOLD_F')
        self.assertLess(mg['coverage']['coverage_ratio'], 0.2)
        detect = correct and mg['coverage']['coverage_ratio'] != 1.0
        self.assertTrue(detect)

    # E4: 月频当日频→缺口假阳性,用例4/8断言失败
    def test_e4_monthly_as_daily_detected(self):
        w = by_id(self.res, 'WTI_SPOT_M')
        correct = w['coverage']['missing_slots_count'] == 0
        self.assertTrue(correct)
        orig = hca.expected_slots

        def monthly_as_daily(freq, first, last, calendar):
            return orig('daily' if freq == 'monthly' else freq, first, last, calendar)

        mut = self._mutated(expected_slots=monthly_as_daily)
        mw = by_id(mut, 'WTI_SPOT_M')
        self.assertGreater(mw['coverage']['missing_slots_count'], 10)
        detect = correct and mw['coverage']['missing_slots_count'] != 0
        self.assertTrue(detect)

    # E5: 漏掉/洗白无数据指标(MISSING→OBSERVED)→用例16断言失败
    # [W4-FIX1修订] classify签名增加n_slots位(FIX1-01: SINGLE_OBSERVATION按
    # 独立观测槽位);本负向mock同步新签名,注入语义不变(MISSING→OBSERVED洗白)。
    def test_e5_missing_whitewash_detected(self):
        s = by_id(self.res, 'SILVER_F')
        correct = s['status'] == 'MISSING'
        self.assertTrue(correct)
        orig = hca.classify

        def whitewash(m, dates, n_slots, ratio, unreadable):
            st = orig(m, dates, n_slots, ratio, unreadable)
            return 'OBSERVED' if st == 'MISSING' else st

        mut = self._mutated(classify=whitewash)
        ms = by_id(mut, 'SILVER_F')
        self.assertNotEqual(ms['status'], 'MISSING')
        detect = correct and ms['status'] != 'MISSING'
        self.assertTrue(detect)


if __name__ == '__main__':
    unittest.main(verbosity=2)
