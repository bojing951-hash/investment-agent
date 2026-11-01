# -*- coding: utf-8 -*-
"""IA-P0-2-W5 专项测试(真实数据验收脚本重构: 八项外部对照独立结构化+
金融计算独立复算+三态综合结果)。

任务: IA-P0-2-W5-DEV-v1.0 §六 | 基线: W4封版 7c004c65(dev/p0-2-w5)
全部用例真实调用被测脚本 real_data_acceptance 的 check_*/independent_
period_returns/recompute_check/evaluate_overall/main()——不复制被测算法、
不预拼JSON结果;外部API一律Mock(注入fetcher或mock requests),零真实网络。

A组(外部对照): UST百分点差bp口径+三期限各自观测日;SPX同观测日强制
   (最近一条≠目标日→NOT_VERIFIED);GOLD_F(PAXG现货代理)与WTI_F(FRED现货)
   恒NOT_COMPARABLE不得按容差证明;SHCOMP同日+收盘口径(盘中/错日→
   NOT_VERIFIED);BTC UTC日K边界+USD计价;外部不可达→NOT_VERIFIED留诊断;
   requests层Mock解析与api_key脱敏。
B组(金融计算): independent_period_returns跨ISO周/前月末非交易日/上年末
   非交易日锚定与输入校验(重复/乱序/非法日期/非法数值);recompute_check
   真实快照一致PASS+篡改引擎值/基准日期/期末→FAIL+单位纪律+单侧缺失+
   双方无基准INSUFFICIENT_HISTORY。
C组(整体状态): 覆盖达标PASS/exit0;任一FAIL→FAIL/exit2;外部全不可达→
   NOT_VERIFIED/exit3(不得整体PASS);--skip-external恒NOT_VERIFIED;
   UST证据缺失→NOT_VERIFIED;NOT_COMPARABLE不填补覆盖。
D组(负向敏感性6项退化注入,§六.D): 对真实源码文本做最小退化替换后
   importlib加载,断言退化版行为与正确版分离——证明本套件对"恢复旧缺陷"
   敏感,非测试与实现同源复制品: FRED取最新值/黄金宽容差PASS/WTI期现直
   PASS/美债量纲错(相对%冒充bp)/全部SKIP仍exit0宣称PASS/复算不核对基准
   日期。
E组(main端到端,SYNTHETIC fixture+Mock外部): 离线诊断exit3+模式留痕;
   外部全不可达exit3+URL脱敏+无密钥泄漏;全比对通过→PASS/exit0+证据落盘;
   Gate A FAIL严格阻断exit2;--data-day指定缺源日exit1。
"""
import contextlib
import glob
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
sys.path.insert(0, os.path.join(ROOT, 'tests'))

import real_data_acceptance as rda   # 被测的真实验收脚本(W5版)
import fixt

DAY = '20261024'                       # 与历史套件同一固定研究日
OBS = '2026-10-23'                     # fixt.obs_for(DAY)
SRC_PATH = os.path.join(ROOT, 'scripts', 'real_data_acceptance.py')


def make_fact(mid, value, obs, unit, derived=None):
    return {'metric_id': mid, 'value': value, 'observation_date': obs,
            'unit': unit, 'derived': derived or {}}


def epoch_of(iso):
    return int(datetime.fromisoformat(iso).replace(tzinfo=timezone.utc).timestamp())


def load_variant(name, old, new, count=1):
    """真实源码文本→最小退化替换→importlib加载(证明测试非复制品)。"""
    src = open(SRC_PATH, encoding='utf-8').read()
    assert src.count(old) == count, f'{name}: 锚点计数{src.count(old)}≠{count}'
    d = tempfile.mkdtemp(prefix=f'w5-variant-{name}-')
    p = os.path.join(d, 'rda_variant.py')
    with open(p, 'w', encoding='utf-8') as f:
        f.write(src.replace(old, new))
    spec = importlib.util.spec_from_file_location(f'rda_var_{name}', p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class W5AExternalChecks(unittest.TestCase):
    """A组: 八项外部对照独立结构化(W5-02)。"""

    def test_a1_ust_bp_semantics_and_per_tenor_dates(self):
        # 百分点差口径: 4.50 vs 4.47 → 3.00bp → PASS(相对%口径为0.67)
        f = make_fact('UST_10Y', 4.50, OBS, 'percent')
        rows = {OBS: {'2 Yr': '4.20', '10 Yr': '4.47', '30 Yr': '4.65'}}
        r = rda.check_ust('UST_10Y', f, rows, '10 Yr', rda.TOLERANCES['treasury_ust'])
        self.assertEqual(r['verdict'], 'PASS')
        self.assertAlmostEqual(r['comparison']['difference_bp'], 3.0, places=6)
        # 超差: 4.50 vs 4.40 → 10bp → FAIL(真实差异,不得放宽容差)
        r = rda.check_ust('UST_10Y', f, {OBS: {'10 Yr': '4.40'}}, '10 Yr',
                          rda.TOLERANCES['treasury_ust'])
        self.assertEqual(r['verdict'], 'FAIL')
        self.assertAlmostEqual(r['comparison']['difference_bp'], 10.0, places=6)

    def test_a2_ust_per_tenor_observation_dates(self):
        # 2Y观测日≠10Y观测日: 各自匹配,不得用10Y日期行代替2Y
        f2 = make_fact('UST_2Y', 4.20, '2026-10-22', 'percent')
        rows = {'2026-10-23': {'2 Yr': '4.21', '10 Yr': '4.47', '30 Yr': '4.65'}}
        r = rda.check_ust('UST_2Y', f2, rows, '2 Yr', rda.TOLERANCES['treasury_ust'])
        self.assertEqual(r['verdict'], 'NOT_VERIFIED')
        self.assertIn('日期不匹配', r['note'])
        rows2 = {'2026-10-22': {'2 Yr': '4.20'}}
        self.assertEqual(rda.check_ust('UST_2Y', f2, rows2, '2 Yr',
                                       rda.TOLERANCES['treasury_ust'])['verdict'],
                         'PASS')

    def test_a3_spx_same_observation_day_required(self):
        f = make_fact('SPX', 7720.39, '2026-10-29', 'index_point')
        spec = rda.TOLERANCES['fred_spx']
        # FRED只有最近一条(10-28)≠目标日(10-29) → NOT_VERIFIED,不得取最新值
        r = rda.check_spx(f, [('2026-10-28', 7700.0)], spec)
        self.assertEqual(r['verdict'], 'NOT_VERIFIED')
        self.assertEqual(r['external']['available_dates'], ['2026-10-28'])
        # 同观测日 → 容差内PASS
        r = rda.check_spx(f, [('2026-10-29', 7725.0)], spec)
        self.assertEqual(r['verdict'], 'PASS')
        # 同观测日但超差 → FAIL
        r = rda.check_spx(f, [('2026-10-29', 7500.0)], spec)
        self.assertEqual(r['verdict'], 'FAIL')

    def test_a4_gold_not_comparable(self):
        # PAXG现货代理(偏差0.92%<旧1%容差)仍NOT_COMPARABLE——旧版按1%判PASS
        # 的固定反例: 容差不解决工具身份(现货代币≠COMEX期货)
        f = make_fact('GOLD_F', 2700.0, '2026-10-29', 'usd_per_oz')
        paxg = {'2026-10-29': {'close': 2725.0, 'start_ts': epoch_of('2026-10-29')}}
        r = rda.check_gold_f(f, paxg, rda.TOLERANCES['paxg_gold'])
        self.assertEqual(r['verdict'], 'NOT_COMPARABLE')
        self.assertAlmostEqual(r['comparison']['reference_deviation_pct'], 0.92,
                               places=6)
        self.assertIn('期货', r['note'])
        # 参考源无该日 → NOT_VERIFIED(参考对照无法执行,非PASS)
        r = rda.check_gold_f(f, {}, rda.TOLERANCES['paxg_gold'])
        self.assertEqual(r['verdict'], 'NOT_VERIFIED')

    def test_a5_wti_not_comparable(self):
        # FRED现货(DCOILWTICO)偏差1.53%<旧2%容差仍NOT_COMPARABLE——期现口径
        # 不同,不得放宽容差代替金融身份验证
        f = make_fact('WTI_F', 71.50, '2026-10-29', 'usd_per_barrel')
        r = rda.check_wti_f(f, [('2026-10-29', 70.42)],
                            rda.TOLERANCES['fred_wti_spot'])
        self.assertEqual(r['verdict'], 'NOT_COMPARABLE')
        self.assertAlmostEqual(r['comparison']['reference_deviation_pct'], 1.53,
                               places=2)
        r = rda.check_wti_f(f, [('2026-10-28', 70.42)],
                            rda.TOLERANCES['fred_wti_spot'])
        self.assertEqual(r['verdict'], 'NOT_VERIFIED')

    def test_a6_shcomp_date_and_close_basis(self):
        f = make_fact('SHCOMP', 3270.15, '2026-10-29', 'index_point')
        spec = rda.TOLERANCES['sina_shcomp']
        # 新浪快照日期≠目标观测日 → NOT_VERIFIED(实时快照不能证明历史收盘)
        r = rda.check_shcomp(f, {'close': 3270.2, 'date': '2026-10-30',
                                 'time': '15:30:00'}, '20261029', spec)
        self.assertEqual(r['verdict'], 'NOT_VERIFIED')
        self.assertIn('日期', r['note'])
        # 同日但为当日盘中(10:30) → NOT_VERIFIED(实时价非收盘口径)
        r = rda.check_shcomp(f, {'close': 3270.2, 'date': '2026-10-29',
                                 'time': '10:30:00'}, '20261029', spec)
        self.assertEqual(r['verdict'], 'NOT_VERIFIED')
        # 同日盘中无时间字段 → NOT_VERIFIED
        r = rda.check_shcomp(f, {'close': 3270.2, 'date': '2026-10-29',
                                 'time': None}, '20261029', spec)
        self.assertEqual(r['verdict'], 'NOT_VERIFIED')
        # 同日且收盘口径(15:30后) → PASS;超差 → FAIL
        r = rda.check_shcomp(f, {'close': 3272.0, 'date': '2026-10-29',
                                 'time': '15:30:00'}, '20261029', spec)
        self.assertEqual(r['verdict'], 'PASS')
        r = rda.check_shcomp(f, {'close': 3300.0, 'date': '2026-10-29',
                                 'time': '15:30:00'}, '20261029', spec)
        self.assertEqual(r['verdict'], 'FAIL')
        # 历史日(非当日)同日收盘 → 正常比较
        r = rda.check_shcomp(f, {'close': 3272.0, 'date': '2026-10-29',
                                 'time': '00:00:00'}, '20261030', spec)
        self.assertEqual(r['verdict'], 'PASS')

    def test_a7_btc_utc_daily_boundary(self):
        f = make_fact('BTC', 71000.0, '2026-10-29', 'usd')
        spec = rda.TOLERANCES['coinbase_btc']
        ts = epoch_of('2026-10-29')            # UTC日界00:00Z
        good = {'2026-10-29': {'close': 71300.0, 'start_ts': ts}}
        r = rda.check_btc(f, good, spec)
        self.assertEqual(r['verdict'], 'PASS')
        self.assertEqual(r['external']['utc_window'][:10], '2026-10-29')
        # K线起点非UTC日界(偏移3600s) → NOT_VERIFIED(日界口径不可证)
        bad = {'2026-10-29': {'close': 71300.0, 'start_ts': ts + 3600}}
        self.assertEqual(rda.check_btc(f, bad, spec)['verdict'], 'NOT_VERIFIED')
        # 无该UTC日K → NOT_VERIFIED(字符串日期相同不跳过日界判断)
        self.assertEqual(rda.check_btc(f, {'2026-10-28': {'close': 71000.0,
                                     'start_ts': epoch_of('2026-10-28')}},
                                       spec)['verdict'], 'NOT_VERIFIED')
        # 非USD计价 → NOT_VERIFIED
        self.assertEqual(rda.check_btc(make_fact('BTC', 71000.0, '2026-10-29',
                                                 'cny'), good,
                                       spec)['verdict'], 'NOT_VERIFIED')

    def test_a8_unreachable_sources_are_not_verified(self):
        # 外部获取失败: 如实NOT_VERIFIED+诊断,不编造不冒充
        f = make_fact('UST_10Y', 4.50, OBS, 'percent')
        r = rda.check_ust('UST_10Y', f, {}, '10 Yr', rda.TOLERANCES['treasury_ust'])
        self.assertEqual(r['verdict'], 'NOT_VERIFIED')
        self.assertIn('不可达', r['note'])
        self.assertEqual(rda.check_spx(make_fact('SPX', 7720.0, OBS, 'index_point'),
                                       [], rda.TOLERANCES['fred_spx'])['verdict'],
                         'NOT_VERIFIED')
        self.assertEqual(rda.check_shcomp(make_fact('SHCOMP', 3270.0, OBS,
                                                    'index_point'), None, DAY,
                                          rda.TOLERANCES['sina_shcomp'])['verdict'],
                         'NOT_VERIFIED')
        self.assertEqual(rda.check_btc(make_fact('BTC', 71000.0, OBS, 'usd'), {},
                                       rda.TOLERANCES['coinbase_btc'])['verdict'],
                         'NOT_VERIFIED')
        # 快照侧缺指标 → SKIPPED(不算PASS)
        self.assertEqual(rda.check_ust('UST_10Y', None, {}, '10 Yr',
                                       rda.TOLERANCES['treasury_ust'])['verdict'],
                         'SKIPPED')

    def _resp(self, text, url='https://x.test/', status=200, json_data=None):
        return mock.Mock(text=text, status_code=status, url=url,
                         raise_for_status=lambda: None,
                         json=lambda: json_data)

    def test_a9_fetchers_parse_and_redact(self):
        # requests层Mock: 真实fetcher的解析与api_key脱敏
        with mock.patch.object(rda.requests, 'get') as g:
            g.return_value = self._resp(
                'Date,1 Mo,2 Yr,3 Mo,10 Yr,30 Yr\n'
                '10/29/2026,4.1,4.20,4.3,4.47,4.65\n'
                '10/28/2026,4.1,4.19,4.3,4.46,4.64\n',
                url='https://home.treasury.gov/...csv')
            rows, ev, raw = rda.fetch_treasury_ust(2026, {'2026-10-29'})
        self.assertEqual(set(rows), {'2026-10-29'})
        self.assertEqual(rows['2026-10-29']['10 Yr'], '4.47')
        self.assertEqual(ev['http_status'], 200)
        self.assertIn('body_sha256', ev)
        self.assertTrue(raw)
        # FRED: 观测降序+缺值'.'过滤;URL密钥脱敏
        fred_json = {'observations': [
            {'date': '2026-10-29', 'value': '7725.0'},
            {'date': '2026-10-28', 'value': '.'},
            {'date': '2026-10-27', 'value': '7700.0'}]}
        with mock.patch.object(rda.requests, 'get') as g:
            g.return_value = self._resp(
                json.dumps(fred_json), json_data=fred_json,
                url='https://api.stlouisfed.org/fred/series/observations'
                    '?api_key=SECRETKEY123&series_id=SP500')
            obs, ev, raw = rda.fetch_fred_obs('SP500', 'SECRETKEY123')
        self.assertEqual(obs, [('2026-10-29', 7725.0), ('2026-10-27', 7700.0)])
        self.assertNotIn('SECRETKEY123', ev['url'])
        self.assertIn('***REDACTED***', ev['url'])
        # Coinbase: UTC日K解析
        cb_json = [[epoch_of('2026-10-29'), 1, 2, 3, 71300.0, 100]]
        with mock.patch.object(rda.requests, 'get') as g:
            g.return_value = self._resp(json.dumps(cb_json), json_data=cb_json,
                                        url='https://api.exchange.coinbase.com/'
                                            'products/BTC-USD/candles')
            out, ev, _ = rda.fetch_coinbase_candles('BTC-USD', '2026-10-29',
                                                    '2026-10-30')
        self.assertEqual(out['2026-10-29']['close'], 71300.0)
        self.assertEqual(out['2026-10-29']['start_ts'] % 86400, 0)
        # 新浪: GBK快照解析(字段3=价,30=日期,31=时间)
        parts = ['上证', '3268', '3265', '3270.15'] + ['0'] * 26 + \
                ['2026-10-29', '15:30:00']
        with mock.patch.object(rda.requests, 'get') as g:
            g.return_value = self._resp(
                'var hq_str_sh000001="' + ','.join(parts) + '";',
                url='https://hq.sinajs.cn/list=sh000001')
            q, ev, _ = rda.fetch_sina_index('sh000001')
        self.assertEqual(q, {'close': 3270.15, 'date': '2026-10-29',
                             'time': '15:30:00'})

    def test_a10_fetcher_error_paths(self):
        # HTTP异常/超时 → 空数据+错误诊断证据,不编造
        with mock.patch.object(rda.requests, 'get',
                               side_effect=TimeoutError('connect timeout')):
            rows, ev, raw = rda.fetch_treasury_ust(2026, {'2026-10-29'})
        self.assertEqual(rows, {})
        self.assertIn('error', ev)
        self.assertIsNone(raw)
        with mock.patch.object(rda.requests, 'get',
                               side_effect=TimeoutError('x')):
            obs, ev, raw = rda.fetch_fred_obs('SP500', 'K')
        self.assertEqual(obs, [])
        self.assertIn('error', ev)


class W5BRecompute(unittest.TestCase):
    """B组: 独立复算independent_period_returns+recompute_check(W5-03)。"""

    def test_b1_iso_week_across_year_end(self):
        # 跨年ISO周: 2027-01-02(周六)属2026-W53,周一起始=2026-12-28
        out = rda.independent_period_returns(
            ['2025-12-26', '2026-12-24', '2026-12-31', '2027-01-02'],
            [100.0, 110.0, 120.0, 132.0], '2027-01-02')
        self.assertEqual(out['week']['basis_date'], '2026-12-24')
        self.assertAlmostEqual(out['week']['pct_change'],
                               (132.0 / 110.0 - 1) * 100, places=4)
        self.assertEqual(out['mtd']['basis_date'], '2026-12-31')
        self.assertEqual(out['ytd']['basis_date'], '2026-12-31')
        # 年初第一周: 2026-01-02(周五)属W01(周一起始2025-12-29)→基准12-26
        out = rda.independent_period_returns(
            ['2025-12-26', '2025-12-31', '2026-01-02'], [100.0, 105.0, 110.0],
            '2026-01-02')
        self.assertEqual(out['week']['basis_date'], '2025-12-26')
        self.assertEqual(out['mtd']['basis_date'], '2025-12-31')
        self.assertEqual(out['ytd']['basis_date'], '2025-12-31')

    def test_b2_month_start_and_year_start_on_non_sessions(self):
        # 前月末非交易日(2026-03-01为周日)→mtd基准=02-27(严格期前)
        out = rda.independent_period_returns(
            ['2025-12-31', '2026-02-26', '2026-02-27', '2026-03-02', '2026-03-03'],
            [100.0, 120.0, 121.0, 122.0, 123.0], '2026-03-03')
        self.assertEqual(out['mtd']['basis_date'], '2026-02-27')
        self.assertAlmostEqual(out['mtd']['pct_change'],
                               (123.0 / 121.0 - 1) * 100, places=4)
        self.assertEqual(out['ytd']['basis_date'], '2025-12-31')
        # 上年末非交易日(01-01为假日): 无2025观测→ytd=None(如实不足)
        out2 = rda.independent_period_returns(
            ['2026-02-27', '2026-03-03'], [121.0, 123.0], '2026-03-03')
        self.assertIsNone(out2['ytd'])
        # 序列无≤obs观测
        self.assertIsNone(rda.independent_period_returns(
            ['2026-01-05'], [1.0], '2026-01-04')['obs'])

    def test_b3_input_validation(self):
        with self.assertRaises(ValueError):      # 重复日期
            rda.independent_period_returns(['2026-01-05', '2026-01-05'],
                                            [1.0, 2.0], '2026-01-06')
        with self.assertRaises(ValueError):      # 长度不等
            rda.independent_period_returns(['2026-01-05'], [1.0, 2.0],
                                           '2026-01-06')
        with self.assertRaises(ValueError):      # 非法日期(非真实日历日)
            rda.independent_period_returns(['2026-13-40'], [1.0], '2026-01-06')
        with self.assertRaises(ValueError):      # 非字符串日期
            rda.independent_period_returns([20260105], [1.0], '2026-01-06')
        for bad in (None, True, '12'):           # 非法数值(bool/None/字符串)
            with self.assertRaises(ValueError):
                rda.independent_period_returns(['2026-01-05'], [bad],
                                               '2026-01-06')
        # 乱序输入可算(排序后与正序等价)
        a = rda.independent_period_returns(['2026-01-07', '2026-01-03'],
                                           [110.0, 100.0], '2026-01-07')
        b = rda.independent_period_returns(['2026-01-03', '2026-01-07'],
                                           [100.0, 110.0], '2026-01-07')
        self.assertEqual(a, b)
        self.assertEqual(a['close'], 110.0)

    def _snap_fixture(self):
        snap = fixt.real_snapshot(DAY)
        return snap, {f['metric_id']: f for f in snap['facts']}, \
            snap.get('series_store') or {}

    def test_b4_real_fixture_recompute_pass(self):
        # 真实fixture快照: 引擎derived与独立复算逐期一致(含基准日期核对);
        # fixture序列仅2观测(10-16/10-23)→mtd/ytd双方均无期前基准=INSUFFICIENT
        snap, facts, store = self._snap_fixture()
        r = rda.recompute_check('SPX', facts['SPX'], store['SPX'])
        self.assertEqual(r['verdict'], 'PASS')
        self.assertEqual(r['periods']['week']['status'], 'PASS')
        eng = facts['SPX']['derived']['week']
        self.assertEqual(r['periods']['week']['independent']['basis_date'],
                         eng['basis_date'])
        for p in ('mtd', 'ytd'):
            self.assertEqual(r['periods'][p]['status'], 'INSUFFICIENT_HISTORY',
                             f'{p}: {r["periods"][p]}')
        self.assertIn('独立复算与引擎一致', r['note'])

    def test_b5_tamper_detection(self):
        snap, facts, store = self._snap_fixture()
        import copy
        f = copy.deepcopy(facts['SPX'])
        r0 = rda.recompute_check('SPX', f, store['SPX'])
        pct = f['derived']['week']['pct_change']
        # ① 篡改引擎周收益值+0.5pp → FAIL
        f2 = copy.deepcopy(f)
        f2['derived']['week']['pct_change'] = pct + 0.5
        self.assertEqual(rda.recompute_check('SPX', f2, store['SPX'])['verdict'],
                         'FAIL')
        # ② 基准日期不一致(值保留) → FAIL(不核对基准日期的复算不算复算)
        f3 = copy.deepcopy(f)
        f3['derived']['week']['basis_date'] = '2099-12-31'
        r3 = rda.recompute_check('SPX', f3, store['SPX'])
        self.assertEqual(r3['verdict'], 'FAIL')
        self.assertIn('基准日期不一致', r3['note'])
        # ③ 期末观测日与序列不一致 → FAIL
        f4 = copy.deepcopy(f)
        f4['observation_date'] = '2026-10-20'
        r4 = rda.recompute_check('SPX', f4, store['SPX'])
        self.assertEqual(r4['verdict'], 'FAIL')
        self.assertIn('期末不一致', r4['note'])
        # 基线本身PASS(对照)
        self.assertEqual(r0['verdict'], 'PASS')

    def test_b6_unit_discipline_and_sided_availability(self):
        # 单位纪律: 利率类(percent)不得机械套用价格百分比公式 → FAIL拒算
        f = make_fact('UST_10Y', 4.5, OBS, 'percent', derived={
            'week': {'pct_change': 1.0, 'basis_date': '2026-10-23'}})
        r = rda.recompute_check('UST_10Y', f, {'dates': ['2026-10-23'],
                                               'values': [4.5]})
        self.assertEqual(r['verdict'], 'FAIL')
        self.assertIn('单位纪律', r['note'])
        # 单侧可算: 引擎有值而序列无基准 → FAIL(非成功复算)
        f = make_fact('SPX', 4800.0, '2026-10-24', 'index_point', derived={
            'week': {'pct_change': 1.0, 'basis_date': '2026-10-23',
                     'basis_value': 4752.0}})
        r = rda.recompute_check('SPX', f, {'dates': ['2026-10-24'],
                                           'values': [4800.0]})
        self.assertEqual(r['periods']['week']['status'], 'FAIL')
        self.assertIn('单侧', r['note'])
        # 反向: 序列有期前基准(10-16早于周一起始10-19)而引擎available=False
        # → 单侧可算 → FAIL
        f2 = make_fact('SPX', 4800.0, '2026-10-23', 'index_point', derived={
            'week': {'available': False, 'reason': 'x'}})
        r = rda.recompute_check('SPX', f2, {'dates': ['2026-10-16', '2026-10-23'],
                                            'values': [4752.0, 4800.0]})
        self.assertEqual(r['periods']['week']['status'], 'FAIL')
        # 双方均无基准(单期观测) → INSUFFICIENT_HISTORY(不得写成成功复算)
        f3 = make_fact('SPX', 4800.0, '2026-10-24', 'index_point', derived={
            'week': {'available': False}, 'mtd': {'available': False},
            'ytd': {'available': False}})
        r = rda.recompute_check('SPX', f3, {'dates': ['2026-10-24'],
                                            'values': [4800.0]})
        self.assertEqual(r['verdict'], 'INSUFFICIENT_HISTORY')


def _ext(mid, verdict):
    return {'check': f'{mid}外部核验', 'metric_id': mid, 'category': 'external',
            'verdict': verdict}


def _rc(mid, verdict):
    return {'check': f'{mid}复算', 'metric_id': mid, 'category': 'recompute',
            'verdict': verdict}


def _healthy_lists():
    ext = [_ext('UST_2Y', 'PASS'), _ext('UST_10Y', 'PASS'),
           _ext('UST_30Y', 'PASS'), _ext('BTC', 'PASS'), _ext('SPX', 'PASS'),
           _ext('SHCOMP', 'PASS'), _ext('GOLD_F', 'NOT_COMPARABLE'),
           _ext('WTI_F', 'NOT_COMPARABLE')]
    rc = [_rc('SPX', 'PASS'), _rc('GOLD_F', 'PASS'), _rc('SHCOMP', 'PASS'),
          _rc('HSI', 'PASS')]
    return ext, rc


class W5COverall(unittest.TestCase):
    """C组: 综合结果三态与退出码(W5-04)。"""

    def test_c1_full_coverage_pass(self):
        ext, rc = _healthy_lists()
        o = rda.evaluate_overall(ext, rc, skip_external=False)
        self.assertEqual(o['overall'], 'PASS')
        self.assertEqual(o['exit_code'], 0)
        self.assertEqual(o['coverage']['ust_pass'], 3)
        self.assertEqual(o['coverage']['market_pass'], 3)
        self.assertEqual(o['coverage']['external_pass_total'], 6)
        self.assertEqual(o['coverage']['recompute_pass'], 4)
        self.assertEqual(o['distribution']['NOT_COMPARABLE'], 2)

    def test_c2_any_fail_blocks(self):
        ext, rc = _healthy_lists()
        ext[1] = _ext('UST_10Y', 'FAIL')
        o = rda.evaluate_overall(ext, rc, skip_external=False)
        self.assertEqual((o['overall'], o['exit_code']), ('FAIL', 2))
        self.assertIn('1项FAIL', o['reasons'][0])

    def test_c3_all_external_unreachable_not_verified(self):
        # 全部外部不可达(NOT_VERIFIED)→不得整体PASS
        ext = [_ext(m, 'NOT_VERIFIED') for m in
               ('UST_2Y', 'UST_10Y', 'UST_30Y', 'BTC', 'SPX', 'SHCOMP',
                'GOLD_F', 'WTI_F')]
        rc = [_rc('SPX', 'PASS'), _rc('GOLD_F', 'PASS'), _rc('SHCOMP', 'PASS'),
              _rc('HSI', 'PASS')]
        o = rda.evaluate_overall(ext, rc, skip_external=False)
        self.assertEqual((o['overall'], o['exit_code']), ('NOT_VERIFIED', 3))
        joined = ' '.join(o['reasons'])
        self.assertIn('利率类(UST)无任何', joined)
        self.assertIn('不足2项', joined)

    def test_c4_skip_external_never_passes(self):
        # --skip-external: 即使复算全PASS也恒NOT_VERIFIED(离线诊断≠核验结论)
        ext, rc = _healthy_lists()
        o = rda.evaluate_overall([], rc, skip_external=True)
        self.assertEqual((o['overall'], o['exit_code']), ('NOT_VERIFIED', 3))
        self.assertIn('离线诊断', o['reasons'][0])

    def test_c5_missing_ust_evidence_not_verified(self):
        # UST全部不可达但市场3项PASS+复算4 PASS: 利率证据缺失→NOT_VERIFIED
        ext, rc = _healthy_lists()
        for i in (0, 1, 2):
            ext[i] = _ext(('UST_2Y', 'UST_10Y', 'UST_30Y')[i], 'NOT_VERIFIED')
        o = rda.evaluate_overall(ext, rc, skip_external=False)
        self.assertEqual((o['overall'], o['exit_code']), ('NOT_VERIFIED', 3))
        self.assertIn('利率证据缺失', ' '.join(o['reasons']))

    def test_c6_not_comparable_does_not_fill_coverage(self):
        # NOT_COMPARABLE/NOT_VERIFIED不算PASS: 覆盖不满足→NOT_VERIFIED
        ext, rc = _healthy_lists()
        ext[5] = _ext('SHCOMP', 'NOT_VERIFIED')      # 市场=2,外部总=5 仍PASS
        o = rda.evaluate_overall(ext, rc, skip_external=False)
        self.assertEqual(o['overall'], 'PASS')
        ext[4] = _ext('SPX', 'NOT_COMPARABLE')       # 市场=1,外部总=4→不足
        o = rda.evaluate_overall(ext, rc, skip_external=False)
        self.assertEqual((o['overall'], o['exit_code']), ('NOT_VERIFIED', 3))


class W5DNegativeSensitivity(unittest.TestCase):
    """D组: 6项退化注入(§六.D)——恢复旧缺陷的变体必须与本套件断言分离。"""

    def _gold_wti_inputs(self):
        return (make_fact('GOLD_F', 2700.0, '2026-10-29', 'usd_per_oz'),
                {'2026-10-29': {'close': 2725.0, 'start_ts': 0}},
                make_fact('WTI_F', 71.50, '2026-10-29', 'usd_per_barrel'))

    def test_d1_fred_latest_value_regression_caught(self):
        # 退化: SPX取FRED最近一条(不校日期) → 本应NOT_VERIFIED的场景变PASS
        f = make_fact('SPX', 7720.39, '2026-10-29', 'index_point')
        obs = [('2026-10-28', 7700.0)]
        spec = rda.TOLERANCES['fred_spx']
        self.assertEqual(rda.check_spx(f, obs, spec)['verdict'], 'NOT_VERIFIED')
        m = load_variant(
            'd1',
            "exact = next(((d, v) for d, v in fred_obs if d == od), None)\n",
            "exact = fred_obs[0] if fred_obs else None\n")
        self.assertEqual(m.check_spx(f, obs, spec)['verdict'], 'PASS')

    def test_d2_d3_gold_wti_tolerance_whitewash_caught(self):
        # 退化: 黄金/WTI按容差直接PASS → NOT_COMPARABLE被洗白为PASS
        f_gold, paxg, f_wti = self._gold_wti_inputs()
        m = load_variant(
            'd23',
            "               'NOT_COMPARABLE', note)",
            "               'PASS', note)")
        self.assertEqual(rda.check_gold_f(f_gold, paxg,
                                          rda.TOLERANCES['paxg_gold'])['verdict'],
                         'NOT_COMPARABLE')
        self.assertEqual(m.check_gold_f(f_gold, paxg,
                                        m.TOLERANCES['paxg_gold'])['verdict'],
                         'PASS')
        self.assertEqual(rda.check_wti_f(f_wti, [('2026-10-29', 70.42)],
                                         rda.TOLERANCES['fred_wti_spot'])['verdict'],
                         'NOT_COMPARABLE')
        self.assertEqual(m.check_wti_f(f_wti, [('2026-10-29', 70.42)],
                                       m.TOLERANCES['fred_wti_spot'])['verdict'],
                         'PASS')

    def test_d4_ust_dimension_error_caught(self):
        # 退化: bp百分点差被换成相对百分比 → 本应FAIL(10bp)的场景变PASS
        f = make_fact('UST_10Y', 4.50, OBS, 'percent')
        rows = {OBS: {'10 Yr': '4.40'}}
        spec = rda.TOLERANCES['treasury_ust']
        self.assertEqual(rda.check_ust('UST_10Y', f, rows, '10 Yr',
                                       spec)['verdict'], 'FAIL')
        m = load_variant(
            'd4',
            "    diff_bp = round(abs(o['value'] - ext) * 100, 2)",
            "    diff_bp = round(abs(o['value'] - ext) / abs(ext) * 100, 2)")
        self.assertEqual(m.check_ust('UST_10Y', f, rows, '10 Yr',
                                     m.TOLERANCES['treasury_ust'])['verdict'],
                         'PASS')

    def test_d5_all_skip_exit0_whitewash_caught(self):
        # 退化: --skip-external返回PASS/exit0 → 正确版必须NOT_VERIFIED/3
        _, rc = _healthy_lists()
        self.assertEqual(rda.evaluate_overall([], rc, True)['exit_code'], 3)
        m = load_variant(
            'd5',
            """        return {'overall': 'NOT_VERIFIED', 'exit_code': 3, 'distribution': dist,
                'coverage': None,
                'reasons': ['离线诊断模式(--skip-external): 真实外部核验未执行,'
                            '不得获得真实外部核验通过结论']}""",
            """        return {'overall': 'PASS', 'exit_code': 0, 'distribution': dist,
                'coverage': None,
                'reasons': ['离线诊断模式(--skip-external): 真实外部核验未执行,'
                            '不得获得真实外部核验通过结论']}""")
        self.assertEqual(m.evaluate_overall([], rc, True)['exit_code'], 0)

    def test_d6_recompute_without_basis_date_check_caught(self):
        # 退化: 复算不核对基准日期 → 基准日期不一致仍PASS
        snap = fixt.real_snapshot(DAY)
        import copy
        facts = {f['metric_id']: f for f in snap['facts']}
        f = copy.deepcopy(facts['SPX'])
        store = snap.get('series_store') or {}
        self.assertEqual(rda.recompute_check('SPX', f, store['SPX'])['verdict'],
                         'PASS')
        f2 = copy.deepcopy(f)
        f2['derived']['week']['basis_date'] = '2099-12-31'
        self.assertEqual(rda.recompute_check('SPX', f2, store['SPX'])['verdict'],
                         'FAIL')
        m = load_variant(
            'd6',
            """            if er.get('basis_date') and iv.get('basis_date') \\
                    and er['basis_date'] != iv['basis_date']:""",
            "            if False:")
        self.assertEqual(m.recompute_check('SPX', f2, store['SPX'])['verdict'],
                         'PASS')


class W5EMainE2E(unittest.TestCase):
    """E组: main()端到端(SYNTHETIC fixture+Mock外部API,零真实网络)。"""

    def _run(self, td, out_sub, extra, fetchers_factory=None, day=DAY):
        fake_now = f'{DAY[:4]}-{DAY[4:6]}-{DAY[6:]}T08:00:00'

        class _DT(datetime):
            @classmethod
            def now(cls, tz=None):
                return cls.fromisoformat(fake_now)

        out = io.StringIO()
        argv = ['rda', '--data-dir', td, '--out-dir', os.path.join(td, out_sub),
                '--data-day', day, '--trusted-root', td] + extra
        patches = [mock.patch.object(sys, 'argv', argv),
                   mock.patch.object(rda, 'datetime', _DT),
                   contextlib.redirect_stdout(out)]
        if fetchers_factory is not None:
            patches.append(mock.patch.object(rda, 'default_fetchers',
                                             fetchers_factory))
        with contextlib.ExitStack() as st:
            for p in patches:
                st.enter_context(p)
            try:
                rda.main()
                rc = 0
            except SystemExit as e:
                rc = e.code
        j = sorted(glob.glob(os.path.join(td, out_sub, 'real_acceptance_*.json')))
        return rc, out.getvalue(), (json.load(open(j[-1])) if j else None), \
            os.path.join(td, out_sub)

    def test_e1_skip_external_offline_diagnostic(self):
        with tempfile.TemporaryDirectory(prefix='w5-e1-') as td:
            fixt.write_collectors(td, DAY)
            rc, out, rep, _ = self._run(td, 'acc', ['--skip-external'])
            self.assertEqual(rc, 3)
            self.assertEqual(rep['overall'], 'NOT_VERIFIED')
            self.assertEqual(rep['acceptance_mode'],
                             'offline_diagnostic(--skip-external)')
            self.assertIn('离线诊断', rep['reasons'][0])
            checks = {c['check']: c['verdict'] for c in rep['checks']}
            self.assertEqual(checks.get('Gate A状态'), 'PASS')   # 历史合同
            self.assertGreaterEqual(
                sum(1 for c in rep['checks'] if c['verdict'] == 'PASS'
                    and c['category'] == 'recompute'), 2)
            # 外部结果为空+证据为空(离线不产生外部结论)
            self.assertEqual(rep['external_results'], [])
            self.assertEqual(rep['external_evidence'], [])

    def test_e2_all_sources_unreachable_redaction(self):
        with tempfile.TemporaryDirectory(prefix='w5-e2-') as td:
            fixt.write_collectors(td, DAY)

            def factory(key):
                def _ev(u):
                    return {'source': 'stub', 'url': u,
                            'fetched_at_utc': '2026-10-24T00:00:00'}
                return {
                    'treasury': lambda y, w: ({}, _ev('https://t.gov/x'),
                                              None),
                    'coinbase': lambda p, s, e: ({}, _ev('https://c.io/' + p),
                                                 None),
                    'sina': lambda c: (None, _ev('https://s.cn/' + c), None),
                    'fred': lambda sid: ([], _ev(
                        'https://api.stlouisfed.org/fred/series/observations'
                        '?api_key=RAWKEY42&series_id=' + sid), None),
                }
            rc, out, rep, outdir = self._run(td, 'acc', [], factory)
            self.assertEqual(rc, 3)
            self.assertEqual(rep['overall'], 'NOT_VERIFIED')
            for r in rep['external_results']:
                self.assertEqual(r['verdict'], 'NOT_VERIFIED', r['check'])
            # 密钥不写入证据(URL脱敏),且失败诊断保留
            blob = json.dumps(rep, ensure_ascii=False)
            self.assertNotIn('RAWKEY42', blob)
            self.assertIn('***REDACTED***', blob)
            self.assertTrue(all(e.get('url') for e in rep['external_evidence']))
            # 原始正文未落盘(获取失败无raw)
            self.assertEqual(rep['external_evidence_files'], [])
            self.assertFalse(glob.glob(os.path.join(outdir, 'evidence', '*')))

    def test_e3_full_match_pass_with_evidence(self):
        with tempfile.TemporaryDirectory(prefix='w5-e3-') as td:
            fixt.write_collectors(td, DAY)
            snap = fixt.real_snapshot(DAY)          # 同一确定性fixture取基准
            facts = {f['metric_id']: f for f in snap['facts']}

            def factory(key):
                def _ev(u):
                    return {'source': 'stub', 'url': u,
                            'fetched_at_utc': '2026-10-24T00:00:00',
                            'http_status': 200}
                ust = {m: facts[m] for m in ('UST_2Y', 'UST_10Y', 'UST_30Y')
                       if m in facts}
                want_dates = {str(f['observation_date'])[:10] for f in
                              ust.values()}

                def treasury(year, want):
                    rows = {d: {'2 Yr': str(ust['UST_2Y']['value']),
                                '10 Yr': str(ust['UST_10Y']['value']),
                                '30 Yr': str(ust['UST_30Y']['value'])}
                            for d in want}
                    return rows, _ev('https://t.gov/curve'), 'raw-treasury'

                def coinbase(product, s, e):
                    mid = 'BTC' if product == 'BTC-USD' else 'GOLD_F'
                    f = facts.get(mid)
                    if not f:
                        return {}, _ev('https://c.io/' + product), 'raw'
                    od = str(f['observation_date'])[:10]
                    return {od: {'close': f['value'],
                                 'start_ts': epoch_of(od)}}, \
                        _ev('https://c.io/' + product), f'raw-{product}'

                def sina(c):
                    f = facts.get('SHCOMP')
                    od = str(f['observation_date'])[:10]
                    return {'close': f['value'], 'date': od,
                            'time': '15:30:00'}, _ev('https://s.cn/' + c), \
                        'raw-sina'

                def fred(sid):
                    mid = 'SPX' if sid == 'SP500' else 'WTI_F'
                    f = facts.get(mid)
                    od = str(f['observation_date'])[:10]
                    return ([(od, f['value'])],
                            _ev('https://api.stlouisfed.org/fred/series/'
                                'observations?api_key=RAWKEY42&series_id=' + sid),
                            f'raw-{sid}')

                return {'treasury': treasury, 'coinbase': coinbase,
                        'sina': sina, 'fred': fred}

            rc, out, rep, outdir = self._run(td, 'acc', [], factory)
            self.assertEqual(rc, 0)
            self.assertEqual(rep['overall'], 'PASS')
            self.assertGreaterEqual(rep['coverage']['ust_pass'], 1)
            self.assertGreaterEqual(rep['coverage']['market_pass'], 2)
            self.assertGreaterEqual(rep['coverage']['external_pass_total'], 4)
            self.assertGreaterEqual(rep['coverage']['recompute_pass'], 2)
            verdicts = {r['check']: r['verdict'] for r in rep['external_results']}
            self.assertEqual(verdicts.get('GOLD_F外部核验'), 'NOT_COMPARABLE')
            self.assertEqual(verdicts.get('WTI_F外部核验'), 'NOT_COMPARABLE')
            # 证据落盘(Git外out-dir)+URL脱敏+报告无密钥
            self.assertTrue(glob.glob(os.path.join(outdir, 'evidence', '*.txt')))
            blob = json.dumps(rep, ensure_ascii=False)
            self.assertNotIn('RAWKEY42', blob)
            self.assertIn('***REDACTED***', blob)
            # 快照与输入证据字段(W5-05)
            self.assertEqual(rep['data']['data_day'], DAY)
            self.assertTrue(rep['snapshot']['gate_a']['status'] in
                            ('PASS', 'DEGRADED'))
            self.assertIn('sha256', rep['snapshot']['sources_status']['global'])

    def test_e4_gate_a_fail_blocks(self):
        with tempfile.TemporaryDirectory(prefix='w5-e4-') as td:
            fixt.write_collectors(td, DAY, break_metric='SPX')   # 核心坏→FAIL
            rc, out, rep, _ = self._run(td, 'acc', ['--skip-external'])
            self.assertEqual(rc, 2)
            self.assertIn('Gate A=FAIL', out)
            self.assertIsNone(rep)      # 阻断: 不产验收报告

    def test_e5_data_day_missing_sources_exit1(self):
        with tempfile.TemporaryDirectory(prefix='w5-e5-') as td:
            fixt.write_collectors(td, DAY)
            # 指定缺源日(20261022无任何文件)→exit 1,不产报告
            rc, out, rep, _ = self._run(td, 'acc', ['--skip-external'],
                                        day='20261022')
            self.assertEqual(rc, 1)
            self.assertIn('四源不齐', out)
            self.assertIsNone(rep)


if __name__ == '__main__':
    unittest.main(verbosity=2)
