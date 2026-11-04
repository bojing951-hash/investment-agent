# -*- coding: utf-8 -*-
"""IA-P03-W1(P0-3 首包·E2E-A 确定性研究底座)专项测试。

合同 IA-P03-W1-E2EA-AC-v1.0 确定性子项(AC-01/02/03)行为锁:
- AC-01 历史查询与跨频率对齐: 登记接入点(macro=normalize_macro 转递 /
  global=快照 series_store)、窗口截取、缺值缺席不填0、ISO 周/自然月网格化
  (与 fact_engine week/mtd 基准同构)、区间变动单位纪律(利率 pp→bp / 价格 pct)、
  滚动相关;
- AC-02 背离检测器三情形: 在场触发(移动条件临界恰触发=含等号 / 相关条件
  rho=+1.0)、不在场不触发(正常负相关 rho=-1.0)、次临界不触发;
  冻结参数 echo=代码常量=登记值(60/0.30/25.0/2.0 字面量);
- AC-03 任务 schema 最低字段集(可增不可减)/falsifiable_conditions 非空/
  append-only 幂等跳过/异指纹新版本追加/同参 task_id 确定性;
- E2E-A 编排(合成采集档走**真实接入链**: resolve_inputs+normalize_macro+
  build_snapshot(write=False).series_store)端到端: 触发→建任务→装配→落档→
  档内直读;重放→幂等跳过+既有档字节不变;不触发→无任务档+如实输出。

数据纪律: 全部为离线合成 fixture(数值刻意中性构造,在注册表 validation 范围
内),不代表任何真实交易日;真实回放证据属 AC-04 证据包,不在本文件冒充。
**预期值一律字面量硬编码**(手算,不从被测模块导入计算——自证恒真是 F 反例)。
零网络/零新增第三方依赖: import 面纯标准库+项目既有模块;三新模块源码级
零网络锁(见 T9)。
"""
import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import anomaly_detector as ad                    # noqa: E402
import research_history_query as rhq             # noqa: E402
import research_task_manager as rtm              # noqa: E402
import fact_engine as fe                         # noqa: E402 (口径一致性引用)

# ══ 合成序列构造(130 个连续日历日;手算锚点全部登记于各断言) ═══════════
BASE = date(2026, 1, 5)          # 周一
N = 130
D = [(BASE + timedelta(days=i)).isoformat() for i in range(N)]
START, END = D[69], D[129]       # 2026-03-15 ~ 2026-05-14(窗口内 61 共同观测)
AS_OF = '2026-05-15T23:59:59+08:00'
SOURCE_YMD = '20260515'


def vals_move_exact():
    """情形①/③(在场+临界恰触发): 阶跃构造——i<70 平坦 2.20/4000,
    i>=70 阶跃至 2.45/4080 并保持。
    手算锚点: i>=70 的每行 chg_r_bp=round((2.45−2.20)×100,1)=25.0
    (恰=RATE_BP_THRESHOLD,含等号),chg_g_pct=round((4080/4000−1)×100,4)=2.0
    (恰=GOLD_PCT_THRESHOLD);i=69 行窗口差分全零(vx=0→rho=None)且 chg=0
    →不触发;首触发行=D[70],窗口内 60 行触发。"""
    r = [2.20] * 70 + [2.45] * 60
    g = [4000.0] * 70 + [4080.0] * 60
    return r, g


def vals_move_below():
    """次临界不触发: r 仅末端抬升至 2.44(+24.0bp<25),g 自 i=100 起持久抬升
    至 4080(窗口末端 chg_g_pct 恰=2.0 达标但利率条件 24.0<25→联合不满足);
    末端行 rho=两不同位置孤立脉冲相关=−1/(60−1)=−0.0169(|rho|<0.30)
    →全窗零触发(金条件单达标不构成触发,联合判定式锁)。"""
    r = [2.20] * 130
    r[129] = 2.44
    g = [4000.0] * 100 + [4080.0] * 30
    return r, g


def vals_corr_divergence():
    """情形①b(相关性条件触发): Δr 与 Δg 同相交替(rho=+1.0>=0.30)而区间
    变动远低于移动阈值(chg_r_bp=0.6bp, chg_g_pct≈0.7435%)。"""
    r = [2.20 + 0.0001 * i + 0.001 * (i % 2) for i in range(N)]
    g = [4000.0 + 0.5 * i + 1.0 * (i % 2) for i in range(N)]
    return r, g


def vals_normal_negative():
    """情形②(不在场): Δr 与 Δg 反相交替(rho=-1.0),区间变动=0 → 不触发。"""
    r = [2.20 + 0.001 * (i % 2) for i in range(N)]
    g = [4000.0 + 1.0 * ((i + 1) % 2) for i in range(N)]
    return r, g


def synth_macro_doc(rates):
    return {'date': '2026-05-15',
            'data': {'TIPS_10Y': {'value': rates[-1], 'date': D[-1],
                                  'frequency': 'daily',
                                  'series': {'dates': list(D), 'values': list(rates)}}}}


def synth_global_doc(golds):
    return {'date': '2026-05-15', 'time': '2026-05-15T21:00:00+08:00', 'count': 1,
            'data': {'GOLD': {'asset_id': 'GOLD', 'close': golds[-1], 'high': None,
                              'low': None, 'week_chg': None, 'mtd_chg': None,
                              'ytd_chg': None, 'vs_50d': None, 'vs_200d': None,
                              'date': D[-1],
                              'series': {'dates': list(D), 'values': list(golds)}}}}


def write_synth_day(root, rates, golds, ymd=SOURCE_YMD):
    dd = os.path.join(root, 'data', 'daily')
    os.makedirs(dd, exist_ok=True)
    mp = os.path.join(dd, f'macro_{ymd}.json')
    gp = os.path.join(dd, f'global_{ymd}.json')
    with open(mp, 'w', encoding='utf-8') as f:
        json.dump(synth_macro_doc(rates), f, ensure_ascii=False)
    with open(gp, 'w', encoding='utf-8') as f:
        json.dump(synth_global_doc(golds), f, ensure_ascii=False)
    return dd, mp, gp


def load_pair(dd, root, rates=None, golds=None):
    rate = rhq.load_metric_series('TIPS_10Y', SOURCE_YMD, as_of=AS_OF,
                                  data_dir=dd, trusted_root=root)
    gold = rhq.load_metric_series('GOLD_F', SOURCE_YMD, as_of=AS_OF,
                                  data_dir=dd, trusted_root=root)
    return rate, gold


# ══ T1: AC-01 历史查询(登记接入点) ═══════════════════════════════════
class T1HistoryQueryAccessPoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = cls._tmp.name
        r, g = vals_move_exact()
        cls.dd, cls.mp, cls.gp = write_synth_day(cls.root, r, g)
        cls.rate, cls.gold = load_pair(cls.dd, cls.root)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_t1a_macro_series_via_normalized_layer(self):
        # 接入点=normalize_macro 转递: 身份/单位/质量经事实引擎确认
        p = self.rate
        self.assertEqual(p['unit'], 'percent')                      # registry 字面量
        self.assertEqual(p['frequency'], 'daily')
        self.assertIn('normalize_macro', p['source']['access_point'])
        self.assertEqual(p['source']['file'], 'macro_20260515.json')
        self.assertEqual(p['observation_date'], D[-1])
        self.assertEqual(p['value'], 2.45)                          # 手算: 末端值
        self.assertEqual(p['dates'][0], '2026-01-05')
        self.assertEqual(p['values'][0], 2.20)                      # 手算: 窗口前平坦值
        self.assertEqual(p['values'][-1], 2.45)
        # source.sha256 = 独立重算(不经被测函数)
        with open(self.mp, 'rb') as f:
            self.assertEqual(p['source']['sha256'],
                             hashlib.sha256(f.read()).hexdigest())

    def test_t1b_global_series_via_snapshot_store(self):
        # 接入点=快照历史序列(series_store;旧ID GOLD→GOLD_F 映射)
        p = self.gold
        self.assertEqual(p['metric_id'], 'GOLD_F')
        self.assertEqual(p['unit'], 'usd_per_oz')                   # registry 字面量
        self.assertIn('series_store', p['source']['access_point'])
        self.assertEqual(p['source']['file'], 'global_20260515.json')
        self.assertEqual(p['value'], 4080.0)                        # 档 close 字面量
        self.assertEqual(p['dates'][0], '2026-01-05')
        self.assertEqual(p['values'][0], 4000.0)
        self.assertEqual(p['values'][-1], 4080.0)
        with open(self.gp, 'rb') as f:
            self.assertEqual(p['source']['sha256'],
                             hashlib.sha256(f.read()).hexdigest())

    def test_t1c_registry_unit_classification_lock(self):
        # 口径一致性: 检测所用两指标的注册表单位落入 fact_engine 单位分类
        # (利率→RATE_UNITS;价格→PRICE_LIKE_UNITS)——预期为 registry 字面量
        self.assertEqual(fe.metric('TIPS_10Y')['unit'], 'percent')
        self.assertIn(fe.metric('TIPS_10Y')['unit'], fe.RATE_UNITS)
        self.assertEqual(fe.metric('GOLD_F')['unit'], 'usd_per_oz')
        self.assertIn(fe.metric('GOLD_F')['unit'], fe.PRICE_LIKE_UNITS)

    def test_t1d_missing_values_dropped_not_zero_filled(self):
        # 缺值如实缺席(剔除+登记),绝不填0
        dates = ['2026-01-05', '2026-01-06', '2026-01-07', '2026-01-08']
        values = [1.0, None, 'garbage', 2.0]
        d, v, clean = rhq._clean_series(dates, values)
        self.assertEqual(d, ['2026-01-05', '2026-01-08'])
        self.assertEqual(v, [1.0, 2.0])
        self.assertEqual(clean, {'n_missing_dropped': 2, 'n_observations': 2})

    def test_t1e_window_query_with_lookback(self):
        win = rhq.query_window(self.rate, START, END, lookback=60)
        self.assertEqual(win['coverage']['n_window'], 61)           # 手算: 69..129
        self.assertEqual(win['coverage']['n_lookback'], 60)
        self.assertEqual(win['dates'][0], D[9])                     # 69-60=9
        self.assertEqual(win['dates'][-1], D[129])
        self.assertEqual(win['coverage']['window_first'], D[69])

    def test_t1f_window_query_empty_window_honest(self):
        win = rhq.query_window(self.rate, '2027-01-01', '2027-12-31')
        self.assertEqual(win['dates'], [])
        self.assertEqual(win['coverage']['n_window'], 0)
        self.assertIn('不填0', win['coverage']['note'])

    def test_t1g_unknown_metric_rejected(self):
        with self.assertRaises(ValueError):
            rhq.load_metric_series('NOT_A_METRIC', SOURCE_YMD, data_dir=self.dd,
                                   trusted_root=self.root)


# ══ T2: AC-01 跨频率对齐与基本计算(字面量) ═══════════════════════════
class T2AlignmentAndComputations(unittest.TestCase):

    def test_t2a_iso_week_alignment_last_observation(self):
        # 登记规则: ISO 周代表=该周内最后有效观测
        payload = {'dates': ['2026-01-05', '2026-01-07', '2026-01-09', '2026-01-12'],
                   'values': [100.0, 102.0, 105.0, 103.0]}
        w = rhq.align_to_iso_week(payload)
        # 周1(01-05周一起): 01-05/07/09 → 代表=01-09 值105;周2: 01-12 值103
        self.assertEqual(w['dates'], ['2026-01-09', '2026-01-12'])
        self.assertEqual(w['values'], [105.0, 103.0])

    def test_t2b_month_alignment_last_observation(self):
        payload = {'dates': ['2026-01-30', '2026-02-01', '2026-02-27'],
                   'values': [10.0, 20.0, 30.0]}
        m = rhq.align_to_month(payload)
        self.assertEqual(m['dates'], ['2026-01-30', '2026-02-27'])
        self.assertEqual(m['values'], [10.0, 30.0])

    def test_t2c_inner_join_common_observations(self):
        pa = {'dates': ['2026-01-05', '2026-01-06', '2026-01-07'], 'values': [1.0, 2.0, 3.0]}
        pb = {'dates': ['2026-01-06', '2026-01-07', '2026-01-08'], 'values': [4.0, 5.0, 6.0]}
        common, va, vb = rhq.inner_join(pa, pb)
        self.assertEqual(common, ['2026-01-06', '2026-01-07'])
        self.assertEqual(va, [2.0, 3.0])
        self.assertEqual(vb, [4.0, 5.0])

    def test_t2d_interval_change_rate_bp(self):
        # 利率类: pp+bp;基准=严格早于 start 的最后观测(fact_engine 同口径)
        dates = ['2026-06-29', '2026-06-30', '2026-09-30']
        values = [2.10, 2.20, 2.93]
        out = rhq.interval_change(dates, values, 'percent',
                                  start='2026-06-30', end='2026-09-30')
        self.assertEqual(out['basis_date'], '2026-06-29')   # 不取 start 当日 06-30
        self.assertEqual(out['pp_change'], 0.83)            # 手算 2.93−2.10
        self.assertEqual(out['bp_change'], 83.0)            # ×100

    def test_t2e_interval_change_price_pct(self):
        dates = ['2026-06-29', '2026-06-30', '2026-09-30']
        values = [3950.0, 4000.0, 4080.0]
        out = rhq.interval_change(dates, values, 'usd_per_oz',
                                  start='2026-06-30', end='2026-09-30')
        self.assertEqual(out['basis_date'], '2026-06-29')
        self.assertEqual(out['pct_change'], 3.2911)         # 手算 (4080/3950−1)×100

    def test_t2f_interval_change_insufficient_data_honest(self):
        out = rhq.interval_change(['2026-09-30'], [2.0], 'percent',
                                  start='2026-06-30', end='2026-09-30')
        self.assertIs(out.get('available'), False)
        self.assertIn('基准', out['reason'])

    def test_t2g_pearson_literals(self):
        # 完全线性关系 rho=±1(浮点路径有 ~1e-16 抖动,以 1e-12 容差锁字面量)
        self.assertAlmostEqual(rhq.pearson([1.0, 2.0, 3.0], [2.0, 4.0, 6.0]),
                               1.0, places=12)
        self.assertAlmostEqual(rhq.pearson([1.0, 2.0, 3.0], [6.0, 4.0, 2.0]),
                               -1.0, places=12)
        self.assertIsNone(rhq.pearson([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]))  # 零方差→None
        self.assertIsNone(rhq.pearson([1.0, 2.0], [3.0, 4.0]))            # n<3→None

    def test_t2h_rolling_correlation_literal(self):
        # Δa=[1,2,3,4], Δb=[2,4,6,8](严格成比例)→ window=3 每窗 rho=1.0
        dates = ['d0', 'd1', 'd2', 'd3', 'd4']
        a = [0.0, 1.0, 3.0, 6.0, 10.0]
        b = [0.0, 2.0, 6.0, 12.0, 20.0]
        out = rhq.rolling_correlation(dates, a, b, window=3)
        self.assertEqual(out, [('d3', 1.0), ('d4', 1.0)])


# ══ T3: AC-02 检测器三情形(冻结参数;字面量) ═════════════════════════
class T3DetectorThreeCases(unittest.TestCase):

    def test_t3a_params_echo_equals_registered_constants(self):
        # echo=代码常量=报告登记值(全部手写字面量——登记值见 P03_W1_E2EA_REPORT §参数冻结)
        self.assertEqual(ad.echo_params(), {
            'rule_id': 'RD-DIV-001', 'rolling_window': 60,
            'corr_threshold': 0.30, 'rate_bp_threshold': 25.0,
            'gold_pct_threshold': 2.0, 'thresholds_inclusive': True,
            'stats_rounding': {'rho': 4, 'chg_r_bp': 1, 'chg_g_pct': 4}})

    def test_t3b_divergence_present_move_condition_boundary_triggers(self):
        # ①在场+③临界: 阶跃后每窗口行恰 25.0bp 与 2.0%(含等号)→触发;
        # 窗口首行(i=69,阶跃前)全零差分窗→rho=None 且 chg=0→不触发
        r, g = vals_move_exact()
        res = ad.detect_divergence(D, r, D, g, START, END)
        self.assertTrue(res['triggered'])
        self.assertEqual(res['summary']['n_common'], 61)
        self.assertEqual(res['summary']['n_scored'], 61)
        self.assertEqual(res['summary']['first_trigger_date'], D[70])
        self.assertEqual(res['summary']['n_triggered'], 60)      # D[70..129]
        first = res['series'][0]                                 # 窗口首行 D[69]
        self.assertEqual(first['date'], D[69])
        self.assertEqual(first['chg_r_bp'], 0.0)
        self.assertIsNone(first['rho'])                          # 全零差分窗→None
        self.assertFalse(first['triggered'])
        last = res['series'][-1]
        self.assertEqual(last['date'], D[129])
        self.assertEqual(last['chg_r_bp'], 25.0)      # 手算恰=阈值(含等号)
        self.assertEqual(last['chg_g_pct'], 2.0)      # 手算恰=阈值(含等号)
        self.assertTrue(last['cond_move'])
        self.assertEqual(last['rho'], 1.0)            # 同日同跳=完全相关(round4)

    def test_t3c_subthreshold_move_does_not_trigger(self):
        # 次临界: 末端 chg_g_pct 恰 2.0(达标)但 chg_r_bp=24.0<25→联合不满足;
        # 两不同位置孤立脉冲 rho=−1/59=−0.0169(<0.30)→全窗零触发
        r, g = vals_move_below()
        res = ad.detect_divergence(D, r, D, g, START, END)
        self.assertFalse(res['triggered'])
        self.assertEqual(res['summary']['n_triggered'], 0)
        last = res['series'][-1]
        self.assertEqual(last['chg_r_bp'], 24.0)      # 手算: 2.44−2.20
        self.assertEqual(last['chg_g_pct'], 2.0)      # 手算: 4080/4000(达标)
        self.assertFalse(last['cond_move'])           # 联合条件缺一不可
        self.assertEqual(last['rho'], -0.0169)        # 手算: −1/(60−1) round4

    def test_t3d_divergence_present_correlation_condition_triggers(self):
        # ①在场(相关性路径): rho=+1.0>=0.30,而区间变动远低于移动阈值
        r, g = vals_corr_divergence()
        res = ad.detect_divergence(D, r, D, g, START, END)
        self.assertTrue(res['triggered'])
        self.assertEqual(res['series'][-1]['rho'], 1.0)
        self.assertTrue(res['series'][-1]['cond_corr'])
        self.assertFalse(res['series'][-1]['cond_move'])
        self.assertEqual(res['summary']['n_triggered'], 61)   # 窗口内全部行

    def test_t3e_normal_negative_correlation_no_trigger(self):
        # ②不在场: rho=-1.0(正常负相关)+零区间变动 → 不触发
        r, g = vals_normal_negative()
        res = ad.detect_divergence(D, r, D, g, START, END)
        self.assertFalse(res['triggered'])
        self.assertEqual(res['series'][-1]['rho'], -1.0)
        self.assertEqual(res['series'][-1]['chg_r_bp'], 0.0)
        self.assertEqual(res['summary']['n_triggered'], 0)

    def test_t3f_insufficient_common_observations_honest(self):
        r, g = vals_move_exact()
        res = ad.detect_divergence(D, r, D, g, '2026-01-05', '2026-01-10')
        self.assertFalse(res['triggered'])
        self.assertEqual(res['series'], [])
        self.assertIn('不造点', res['summary']['reason'])

    def test_t3g_detector_pure_no_io(self):
        # 检测器无文件IO/网络: 源码级锁(零 open(/网络 import)
        src = open(os.path.join(ROOT, 'scripts', 'anomaly_detector.py'),
                   encoding='utf-8').read()
        self.assertNotIn('open(', src)
        for banned in ('requests', 'urllib', 'socket', 'http'):
            self.assertNotIn(banned, src)


# ══ T4: AC-03 任务结构与档案追加性 ═══════════════════════════════════
class T4TaskSchemaAndArchive(unittest.TestCase):

    @staticmethod
    def _detection(triggered=True):
        r, g = (vals_move_exact() if triggered else vals_normal_negative())
        return ad.detect_divergence(D, r, D, g, START, END)

    @staticmethod
    def _payloads():
        rate = {'metric_id': 'TIPS_10Y', 'unit': 'percent', 'quality_status': 'PASS',
                'observation_date': D[-1], 'value': 2.45,
                'series_clean': {'n_missing_dropped': 0, 'n_observations': 130},
                'source': {'access_point': 'AP_RATE', 'file': 'macro_x.json',
                           'file_date': '20260515', 'exact': True, 'sha256': 'a' * 64}}
        gold = {'metric_id': 'GOLD_F', 'unit': 'usd_per_oz', 'quality_status': 'PASS',
                'observation_date': D[-1], 'value': 4080.0,
                'series_clean': {'n_missing_dropped': 0, 'n_observations': 130},
                'source': {'access_point': 'AP_GOLD', 'file': 'global_x.json',
                           'file_date': '20260515', 'exact': True, 'sha256': 'b' * 64}}
        return rate, gold

    def test_t4a_schema_min_fields_all_present(self):
        # 最低字段集(可增不可减)逐项在场;falsifiable 非空;history 追加式非空
        det = self._detection()
        task = rtm.build_task(START, END, det, *self._payloads())
        for field in ['task_id', 'created_at', 'phenomenon', 'status', 'indicators',
                      'window', 'detection', 'evidence', 'falsifiable_conditions',
                      'history']:
            self.assertIn(field, task, f"schema 缺最低字段 {field}")
        self.assertTrue(task['falsifiable_conditions'])
        self.assertGreaterEqual(len(task['falsifiable_conditions']), 3)
        self.assertTrue(all(task['falsifiable_conditions']))
        self.assertTrue(task['history'])
        # created_at 为 UTC ISO(带 +00:00/Z)
        self.assertIn('+00:00', task['created_at'])
        # 证据含数据质量状态(AC-03 F 反例锁)
        for mid in ('TIPS_10Y', 'GOLD_F'):
            self.assertIn('quality_status', task['evidence']['data_quality'][mid])
        # detection 含规则+冻结参数+触发统计
        self.assertEqual(task['detection']['rule_id'], 'RD-DIV-001')
        self.assertEqual(task['detection']['frozen_params']['rolling_window'], 60)
        self.assertIn('series', task['detection']['trigger_stats'])

    def test_t4b_task_id_deterministic_and_param_sensitive(self):
        det = self._detection()
        rate, gold = self._payloads()
        t1 = rtm.build_task(START, END, det, rate, gold)
        t2 = rtm.build_task(START, END, det, rate, gold)
        self.assertEqual(t1['task_id'], t2['task_id'])       # 同参确定性
        det2 = self._detection()
        det2['params'] = dict(det2['params'])
        det2['params']['rate_bp_threshold'] = 30.0
        t3 = rtm.build_task(START, END, det2, rate, gold)
        self.assertNotEqual(t1['task_id'], t3['task_id'])    # 参数敏感

    def test_t4c_archive_append_only_idempotent_skip(self):
        det = self._detection()
        task = rtm.build_task(START, END, det, *self._payloads())
        with tempfile.TemporaryDirectory() as td:
            s1, p1 = rtm.save_task(task, td)
            self.assertEqual(s1, 'written')
            with open(p1, 'rb') as f:
                sha_before = hashlib.sha256(f.read()).hexdigest()
            s2, p2 = rtm.save_task(task, td)                 # 同 task_id 重放
            self.assertEqual(s2, 'skipped-idempotent')
            self.assertEqual(p1, p2)
            with open(p1, 'rb') as f:
                sha_after = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(sha_before, sha_after)          # 字节不变
            self.assertEqual(len([n for n in os.listdir(td)]), 1)   # 零新增

    def test_t4d_archive_new_version_on_different_fingerprint(self):
        det = self._detection()
        task = rtm.build_task(START, END, det, *self._payloads())
        task2 = rtm.build_task(START, END, det, *self._payloads())
        task2['detection']['frozen_params'] = dict(task2['detection']['frozen_params'])
        task2['detection']['frozen_params']['rate_bp_threshold'] = 30.0  # 异指纹
        with tempfile.TemporaryDirectory() as td:
            _, p1 = rtm.save_task(task, td)
            with open(p1, 'rb') as f:
                sha1 = hashlib.sha256(f.read()).hexdigest()
            s2, p2 = rtm.save_task(task2, td)
            self.assertEqual(s2, 'written-new-version')
            self.assertTrue(p2.endswith('__v2.json'))
            self.assertNotEqual(p1, p2)
            with open(p1, 'rb') as f:
                self.assertEqual(hashlib.sha256(f.read()).hexdigest(), sha1)  # 原档不动
            self.assertEqual(sorted(os.listdir(td)),
                             sorted([os.path.basename(p1), os.path.basename(p2)]))

    def test_t4e_detection_series_append_only_sequenced(self):
        det = self._detection()
        with tempfile.TemporaryDirectory() as td:
            p1 = rtm.save_detection_series(det, START, END, td)
            p2 = rtm.save_detection_series(det, START, END, td)
            self.assertTrue(p1.endswith('_001.json'))
            self.assertTrue(p2.endswith('_002.json'))        # 永不覆盖
            with open(p1, encoding='utf-8') as f:
                doc = json.load(f)
            self.assertEqual(len(doc['series']), 61)         # 窗口内逐期序列


# ══ T5: E2E-A 编排(合成采集档→真实接入链→端到端) ═══════════════════
class T5E2EOrchestrationSynthetic(unittest.TestCase):

    def test_t5a_triggered_run_creates_task_archive_readable_in_file(self):
        r, g = vals_move_exact()
        with tempfile.TemporaryDirectory() as root:
            dd, mp, gp = write_synth_day(root, r, g)
            od = os.path.join(root, 'data', 'research')
            out = io.StringIO()
            with redirect_stdout(out):
                det, path, status = rtm.run_e2e(START, END, SOURCE_YMD, data_dir=dd,
                                                out_dir=od, trusted_root=root,
                                                as_of=AS_OF)
            self.assertTrue(det['triggered'])
            self.assertEqual(status, 'written')
            logs = out.getvalue()
            self.assertIn('"rolling_window": 60', logs)       # 参数 echo 入日志
            self.assertIn('TRIGGERED', logs)
            self.assertTrue(os.path.exists(path))
            with open(path, encoding='utf-8') as f:
                task = json.load(f)                            # 档内直读
            self.assertEqual(task['status'], 'active')
            self.assertEqual(task['indicators'], ['TIPS_10Y', 'GOLD_F'])
            sw = task['evidence']['series_window']
            self.assertEqual(len(sw['common_dates']), 61)      # 窗口内共同观测
            self.assertEqual(sw['TIPS_10Y'][-1], 2.45)         # 真实序列值直读
            self.assertEqual(sw['GOLD_F'][-1], 4080.0)
            ts = task['detection']['trigger_stats']['series']
            self.assertEqual(ts[-1]['chg_r_bp'], 25.0)         # 真实计算结果直读
            self.assertEqual(ts[-1]['date'], D[129])
            self.assertEqual(task['evidence']['source_artifacts'][0]['sha256'],
                             hashlib.sha256(open(mp, 'rb').read()).hexdigest())
            self.assertEqual(task['evidence']['data_quality']['TIPS_10Y']
                             ['quality_status'], 'PASS')
            self.assertEqual([h['to'] for h in task['history']],
                             ['pending', 'active'])            # 状态机迁移记录
            series_files = [n for n in os.listdir(od) if n.startswith('detection_series_')]
            self.assertEqual(len(series_files), 1)

    def test_t5b_replay_same_window_idempotent_archive_unchanged(self):
        r, g = vals_move_exact()
        with tempfile.TemporaryDirectory() as root:
            dd, _, _ = write_synth_day(root, r, g)
            od = os.path.join(root, 'data', 'research')
            with redirect_stdout(io.StringIO()):
                _, path1, s1 = rtm.run_e2e(START, END, SOURCE_YMD, data_dir=dd,
                                           out_dir=od, trusted_root=root, as_of=AS_OF)
            sha1 = hashlib.sha256(open(path1, 'rb').read()).hexdigest()
            out2 = io.StringIO()
            with redirect_stdout(out2):
                _, path2, s2 = rtm.run_e2e(START, END, SOURCE_YMD, data_dir=dd,
                                           out_dir=od, trusted_root=root, as_of=AS_OF)
            # 同 task_id 重放→登记规则=幂等跳过,既有档零写入
            self.assertEqual(s1, 'written')
            self.assertEqual(s2, 'skipped-idempotent')
            self.assertEqual(path1, path2)
            self.assertEqual(hashlib.sha256(open(path1, 'rb').read()).hexdigest(), sha1)
            self.assertIn('skipped-idempotent', out2.getvalue())
            # 新增仅 detection_series 新档(序号002),任务档唯一
            names = os.listdir(od)
            self.assertEqual(len([n for n in names if n.startswith('RT-')]), 1)
            self.assertEqual(len([n for n in names if n.startswith('detection_series_')]), 2)

    def test_t5c_not_triggered_honest_no_task_archive(self):
        r, g = vals_normal_negative()
        with tempfile.TemporaryDirectory() as root:
            dd, _, _ = write_synth_day(root, r, g)
            od = os.path.join(root, 'data', 'research')
            out = io.StringIO()
            with redirect_stdout(out):
                det, path, status = rtm.run_e2e(START, END, SOURCE_YMD, data_dir=dd,
                                                out_dir=od, trusted_root=root,
                                                as_of=AS_OF)
            self.assertFalse(det['triggered'])
            self.assertIsNone(path)
            logs = out.getvalue()
            self.assertIn('NOT TRIGGERED', logs)
            self.assertIn('情形(c)', logs)                    # 分流说明如实
            names = os.listdir(od)
            self.assertEqual([n for n in names if n.startswith('RT-')], [])
            self.assertEqual(len([n for n in names
                                  if n.startswith('detection_series_')]), 1)


# ══ T6: AC-01/AC-06 源码级边界锁(禁直开原始档/零网络) ═══════════════
class T6SourceBoundaryLocks(unittest.TestCase):

    MODULES = ['research_history_query.py', 'anomaly_detector.py',
               'research_task_manager.py']

    def _src(self, name):
        with open(os.path.join(ROOT, 'scripts', name), encoding='utf-8') as f:
            return f.read()

    def test_t6a_no_data_daily_path_or_glob_in_new_modules(self):
        # 新模块不出现采集目录字样/采集档文件名模式/自行 glob——文件选择一律
        # 经 resolve_inputs 规范核验(目录缺省复用 snapshot_builder 权威常量)
        for name in self.MODULES:
            src = self._src(name)
            self.assertNotIn('daily', src, f'{name} 出现采集目录字样')
            for pat in ('macro_*', 'global_*', 'china_*', 'rate_economy_*',
                        'glob.glob', 'glob('):
                self.assertNotIn(pat, src, f'{name} 出现 {pat}')

    def test_t6b_history_query_single_open_is_marked_exemption(self):
        # research_history_query 的唯一 open(=macro 通道经标准化层转递读取,
        # 必须带 ACCESS_POINT_EXEMPT 登记(合同 AC-01 豁免句)
        src = self._src('research_history_query.py')
        lines = [ln for ln in src.splitlines() if 'open(' in ln]
        self.assertEqual(len(lines), 1)
        self.assertIn('ACCESS_POINT_EXEMPT', lines[0])

    def test_t6c_zero_network_imports(self):
        for name in self.MODULES:
            src = self._src(name)
            for banned in ('import requests', 'import urllib', 'import socket',
                           'import http', 'subprocess', 'import akshare',
                           'import yfinance', 'import pandas'):
                self.assertNotIn(banned, src, f'{name} 触网/新增依赖: {banned}')

    def test_t6d_task_manager_open_calls_only_own_archives(self):
        # 任务管理器 open( 仅限自产档案读写: save_task 读旧档/写tmp、
        # save_detection_series 写tmp、_sha256_file 读档——目标路径均由
        # out_dir 参数派生,无任何采集档文件名
        src = self._src('research_task_manager.py')
        opens = [ln.strip() for ln in src.splitlines() if 'open(' in ln]
        self.assertEqual(len(opens), 4, f"open( 计数登记=4,实际: {opens}")
        for ln in opens:
            for banned in ('macro', 'global_', 'china', 'rate_economy'):
                self.assertNotIn(banned, ln)


if __name__ == '__main__':
    unittest.main(verbosity=2)
