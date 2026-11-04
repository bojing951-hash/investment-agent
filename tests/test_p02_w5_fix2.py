# -*- coding: utf-8 -*-
"""IA-P0-2-W5-FIX2 专项测试(IA-P0-2-W5-FIX2-AC-v1.0 T4/F2-AC-01.3/04/06)。

任务: BTC日收盘UTC完整日语义(采集侧)+EXT-BTC"完结vs完结"比较口径(验收侧)。
全部用例真实调用被测代码——采集侧 scripts/global_market_collector.py 的
btc_completed_utc_days_only/__main__产物语义、验收侧 real_data_acceptance.py
的check_btc/btc_utc_day_completed/run_external_checks/main()——不复制被测
算法、不预拼JSON结果;外部API一律Mock(注入fetcher),零真实网络。

R1(在途反例): 取数时刻(UTC)未完整结束的UTC日bar必须整体剔除——该日的
   close/high/low/series任何价格不得被产出为该UTC日收盘;验收侧在途日
   完结vs完结不可满足→NOT_COMPARABLE(数值相等也不得绕过完结性)。
R2(R003回归反例): 2026-10-29T23:00:17Z取到78822.59(在途截断价)曾被记为
   10-29日收盘,与Coinbase完整UTC日收77780.33差1.34%——修复后采集侧不得
   产出该值(剔除在途bar);验收侧同场景①在途时点→NOT_COMPARABLE,
   ②日完结后按完结vs完结比较1.34%>0.5%→FAIL(容差不放宽)。
R3(退化敏感性): 对真实源码文本做最小退化替换后importlib加载,断言退化版
   行为与正确版分离(证明测试非实现同源复制品): ①采集侧删除完结判定
   (在途bar被保留);②验收侧删除在途日NOT_COMPARABLE守卫(在途相等值
   变PASS);③验收侧删除close_meta一致性守卫(口径不一致变PASS)。
R4(完结正例): 取数时刻跨过D+1T00:00:00Z后,该UTC日正常产出收盘,值/来源
   /元数据一致;未来时间戳bar(数据源异常)同样剔除,不采信未来数据。
W(T2错日反例): 比较日D的Coinbase日K缺失而D±1存在(值相等)→NOT_VERIFIED,
   D vs D±1永不静默PASS;close_meta.completed_through_utc≠D→NOT_COMPARABLE;
   naive/aware取数时刻注入等价;日界边界(D+1T00:00:00Z整点已完结)。
E(main端到端,SYNTHETIC fixture+Mock外部): global产物含close_meta时
   EXT-BTC PASS且note/summary携带元数据;close_meta不一致→NOT_COMPARABLE
   (如实披露,不冒充PASS也不阻断其他检查)。
"""
import contextlib
import glob
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
sys.path.insert(0, os.path.join(ROOT, 'tests'))

import real_data_acceptance as rda          # 被测: 验收侧(F2-AC-02)
import global_market_collector as gmc       # 被测: 采集侧(F2-AC-01)
import fixt
from test_p02_w5 import (DAY, OBS, SRC_PATH, make_fact, epoch_of,
                         load_variant, _extend_global_history)
from test_p02_w5_fix1 import _full_facts, _stub_fetchers

COL_SRC_PATH = os.path.join(ROOT, 'scripts', 'global_market_collector.py')

# ── R003确定性场景常数(归因卷宗dev/p0-2-w5-attr@2215f0e实证值) ──
R003_NOW = datetime(2026, 10, 29, 23, 0, 17, tzinfo=timezone.utc)
R003_UTC_PRICE = 78822.59      # 10-29 23:00:17Z在途截断价(曾被误记为日收盘)
COINBASE_1029 = 77780.33       # Coinbase 2026-10-29完整UTC日收盘
SPEC = rda.TOLERANCES['coinbase_btc']

NOW_AFTER_1031 = datetime(2026, 10, 31, 1, 0, 0, tzinfo=timezone.utc)
# 10-31完结后的运行时刻(≥2026-11-01T00:00:00Z,对应正式重跑真实时窗)
NOW_LATE = datetime(2026, 11, 1, 13, 30, 0, tzinfo=timezone.utc)


def hist_of(bars):
    """bars=[(iso_day, close, high, low)]→tz-aware UTC日K DataFrame。"""
    import pandas as pd
    idx = pd.DatetimeIndex([pd.Timestamp(d, tz='UTC') for d, _, _, _ in bars])
    return pd.DataFrame({'Close': [c for _, c, _, _ in bars],
                         'High': [h for _, _, h, _ in bars],
                         'Low': [l for _, _, _, l in bars]}, index=idx)


def hist_r003():
    """R003场景: 10-28/10-29完结,10-29在途取数时10-30尚不存在的未来形态
    (未来时间戳bar一并给出,验证未来数据不被采信)。"""
    return hist_of([('2026-10-28', 81267.59, 81300.0, 81000.0),
                    ('2026-10-29', R003_UTC_PRICE, 81771.26, 78569.82),
                    ('2026-10-30', 70000.0, 71000.0, 69000.0)])


def btc_fact(value, od):
    return make_fact('BTC', value, od, 'usd')


def candle(od, close):
    return {od: {'close': close, 'start_ts': epoch_of(od)}}


def meta(ct, retrieved='2026-10-31T01:00:00+00:00'):
    return {'source': 'yfinance:BTC-USD(daily,UTC日K)',
            'retrieved_at_utc': retrieved,
            'semantics': 'completed_utc_daily_close_only',
            'completed_through_utc': ct,
            'dropped_incomplete_utc_days': []}


def load_collector_variant(name, old, new, count=1):
    """采集侧源码文本→最小退化替换→importlib加载(R3退化敏感性)。"""
    src = open(COL_SRC_PATH, encoding='utf-8').read()
    assert src.count(old) == count, \
        f'{name}: 锚点计数{src.count(old)}≠{count}'
    d = tempfile.mkdtemp(prefix=f'w5fix2-gmc-{name}-')
    p = os.path.join(d, 'gmc_variant.py')
    with open(p, 'w', encoding='utf-8') as f:
        f.write(src.replace(old, new))
    spec = importlib.util.spec_from_file_location(f'gmc_var_{name}', p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class F2R1InFlightDropped(unittest.TestCase):
    """R1: 在途UTC日bar必须整体剔除,任何价格不得产出为该日收盘。"""

    def test_r1a_in_flight_bar_dropped_whole(self):
        f, m = gmc.btc_completed_utc_days_only(hist_r003(), R003_NOW)
        self.assertEqual([str(d.date()) for d in f.index], ['2026-10-28'])
        self.assertEqual(m['dropped_incomplete_utc_days'],
                         ['2026-10-29', '2026-10-30'])
        self.assertEqual(m['completed_through_utc'], '2026-10-28')
        # 在途bar的close/high/low任何值都不得留在产物里
        for col in ('Close', 'High', 'Low'):
            self.assertNotIn(R003_UTC_PRICE if col == 'Close' else 81771.26,
                             f[col].tolist())

    def test_r1b_meta_persisted_fields(self):
        _, m = gmc.btc_completed_utc_days_only(hist_r003(), R003_NOW)
        self.assertEqual(m['source'], gmc.BTC_CLOSE_SOURCE)
        self.assertEqual(m['semantics'], 'completed_utc_daily_close_only')
        self.assertEqual(m['bar_utc_window'], '[D 00:00:00Z, D+1 00:00:00Z)')
        self.assertEqual(m['retrieved_at_utc'], '2026-10-29T23:00:17+00:00')

    def test_r1c_naive_index_interpreted_as_utc(self):
        # naive索引按UTC解释: 同一取数时刻,drop决策与tz-aware索引一致
        import pandas as pd
        h = hist_r003()
        h.index = h.index.tz_localize(None)
        f2, m2 = gmc.btc_completed_utc_days_only(h, R003_NOW)
        self.assertEqual(m2['dropped_incomplete_utc_days'],
                         ['2026-10-29', '2026-10-30'])

    def test_r1d_acceptance_in_flight_not_comparable(self):
        # 验收侧: 在途UTC日无完结收盘→NOT_COMPARABLE
        r = rda.check_btc(btc_fact(R003_UTC_PRICE, '2026-10-29'),
                          candle('2026-10-29', COINBASE_1029), SPEC,
                          now_utc=R003_NOW)
        self.assertEqual(r['verdict'], 'NOT_COMPARABLE')
        self.assertIn('未完整结束', r['note'])
        self.assertTrue(r['external']['in_flight_utc_day'])

    def test_r1e_equal_values_do_not_bypass_completion(self):
        # 在途日即使双侧数值恰好相等,也不得以"数值一致"绕过完结性
        r = rda.check_btc(btc_fact(R003_UTC_PRICE, '2026-10-29'),
                          candle('2026-10-29', R003_UTC_PRICE), SPEC,
                          now_utc=R003_NOW)
        self.assertEqual(r['verdict'], 'NOT_COMPARABLE')


class F2R2R003Regression(unittest.TestCase):
    """R2: R003场景(78822.59在途截断vs 77780.33完整UTC日收,差1.34%)。"""

    def test_r2a_collector_never_emits_in_flight_as_close(self):
        # 修复前: 78822.59被记为2026-10-29日收盘(与Coinbase差1.34%)
        # 修复后: 该bar整体剔除,10-29不产出收盘
        f, m = gmc.btc_completed_utc_days_only(hist_r003(), R003_NOW)
        dates = [str(d.date()) for d in f.index]
        self.assertNotIn('2026-10-29', dates)
        self.assertNotIn(R003_UTC_PRICE, f['Close'].tolist())
        self.assertIn('2026-10-29', m['dropped_incomplete_utc_days'])

    def test_r2b_acceptance_in_flight_scene_not_comparable(self):
        # 同场景验收侧①: 运行时刻仍在10-29内→完结vs完结不可满足
        r = rda.check_btc(btc_fact(R003_UTC_PRICE, '2026-10-29'),
                          candle('2026-10-29', COINBASE_1029), SPEC,
                          now_utc=R003_NOW)
        self.assertEqual(r['verdict'], 'NOT_COMPARABLE')

    def test_r2c_acceptance_completed_scene_fails_at_1_34(self):
        # 同场景验收侧②: 日完结后按完结vs完结比较,1.34%>0.5%→FAIL
        # (容差冻结不放宽——真实差异必须如实FAIL)
        r = rda.check_btc(btc_fact(R003_UTC_PRICE, '2026-10-29'),
                          candle('2026-10-29', COINBASE_1029), SPEC,
                          now_utc=NOW_AFTER_1031, close_meta=meta('2026-10-29'))
        self.assertEqual(r['verdict'], 'FAIL')
        self.assertAlmostEqual(r['comparison']['difference_pct'], 1.34,
                               places=2)
        self.assertEqual(r['comparison']['tolerance_pct'], 0.5)


class F2R3DegradationSensitivity(unittest.TestCase):
    """R3: 退化注入——删除完结判定/守卫的变体必须与正确版行为分离。"""

    def test_r3a_collector_completion_removed_keeps_in_flight(self):
        # 退化: 采集侧删除完结判定(if day_end<=now→if True)
        old = "        if day_end <= now:"
        m = load_collector_variant('r3a', old, "        if True:")
        f_real, m_real = gmc.btc_completed_utc_days_only(hist_r003(), R003_NOW)
        f_var, m_var = m.btc_completed_utc_days_only(hist_r003(), R003_NOW)
        # 正确版剔除在途/未来bar;退化版全部保留(旧行为复活)
        self.assertEqual(m_real['dropped_incomplete_utc_days'],
                         ['2026-10-29', '2026-10-30'])
        self.assertEqual(m_var['dropped_incomplete_utc_days'], [])
        self.assertIn(R003_UTC_PRICE, f_var['Close'].tolist())

    def test_r3b_acceptance_inflight_guard_removed(self):
        # 退化: 验收侧删除在途日NOT_COMPARABLE守卫→在途相等值变PASS
        old = "    if not btc_utc_day_completed(od, now_utc):"
        m = load_variant('r3b', old, "    if False:")
        f = btc_fact(R003_UTC_PRICE, '2026-10-29')
        cand = candle('2026-10-29', R003_UTC_PRICE)
        self.assertEqual(
            rda.check_btc(f, cand, SPEC, now_utc=R003_NOW)['verdict'],
            'NOT_COMPARABLE')
        self.assertEqual(
            m.check_btc(f, cand, m.TOLERANCES['coinbase_btc'],
                        now_utc=R003_NOW)['verdict'],
            'PASS')

    def test_r3c_acceptance_close_meta_guard_removed(self):
        # 退化: 验收侧删除close_meta一致性守卫→口径不一致变PASS
        old = ("    if close_meta is not None and "
               "close_meta.get('completed_through_utc') != od:")
        m = load_variant('r3c', old, "    if False:")
        f = btc_fact(77430.0, '2026-10-31')
        cand = candle('2026-10-31', 77430.0)
        bad = meta('2026-10-30')          # 采集完结口径≠比较日
        # 运行时刻取10-31完结之后→NOT_COMPARABLE只能来自close_meta守卫
        self.assertEqual(
            rda.check_btc(f, cand, SPEC, now_utc=NOW_LATE,
                          close_meta=bad)['verdict'],
            'NOT_COMPARABLE')
        self.assertEqual(
            m.check_btc(f, cand, m.TOLERANCES['coinbase_btc'],
                        now_utc=NOW_LATE, close_meta=bad)['verdict'],
            'PASS')


class F2R4CompletedPositive(unittest.TestCase):
    """R4: 完结UTC日正常产出收盘+未来时间戳bar剔除(不采信未来数据)。"""

    def test_r4a_completed_day_emitted_with_meta(self):
        # 取数时刻2026-10-31T01:00Z: 10-30已完结→正常产出
        h = hist_of([('2026-10-29', 77180.42, 77300.0, 77000.0),
                     ('2026-10-30', 77198.21, 77350.0, 76900.0),
                     ('2026-11-02', 78000.0, 78100.0, 77900.0)])  # 未来bar
        f, m = gmc.btc_completed_utc_days_only(h, NOW_AFTER_1031)
        self.assertEqual([str(d.date()) for d in f.index],
                         ['2026-10-29', '2026-10-30'])
        self.assertAlmostEqual(f['Close'].iloc[-1], 77198.21, places=2)
        self.assertEqual(m['completed_through_utc'], '2026-10-30')
        self.assertEqual(m['dropped_incomplete_utc_days'], ['2026-11-02'])

    def test_r4b_exact_day_boundary(self):
        # D+1T00:00:00Z整点=已完结;提前1秒=未完结(机械规则无模糊带)
        self.assertTrue(rda.btc_utc_day_completed(
            '2026-10-30', datetime(2026, 10, 31, 0, 0, 0,
                                   tzinfo=timezone.utc)))
        self.assertFalse(rda.btc_utc_day_completed(
            '2026-10-30', datetime(2026, 10, 30, 23, 59, 59,
                                   tzinfo=timezone.utc)))

    def test_r4c_naive_now_injected_like_test_mock(self):
        # naive取数时刻按UTC解释(测试注入确定性时点的既有mock形态)
        self.assertTrue(rda.btc_utc_day_completed('2026-10-30',
                                                  datetime(2026, 10, 31, 3, 0)))
        self.assertFalse(rda.btc_utc_day_completed('2026-10-30',
                                                   datetime(2026, 10, 30, 23, 0)))

    def test_r4d_acceptance_completed_pass_with_meta_proof(self):
        # 完结日+同日K+close_meta一致→PASS,且note携带元数据证明
        r = rda.check_btc(btc_fact(77423.98, '2026-10-31'),
                          candle('2026-10-31', 77423.98), SPEC,
                          now_utc=NOW_LATE,
                          close_meta=meta('2026-10-31'))
        self.assertEqual(r['verdict'], 'PASS')
        self.assertEqual(r['comparison']['difference_pct'], 0.0)
        self.assertIn('completed_through=2026-10-31', r['note'])
        self.assertIn('yfinance:BTC-USD', r['note'])

    def test_r4e_acceptance_no_meta_disclosed_not_blocked(self):
        # 旧采集产物无close_meta→不阻断,如实披露(仍可PASS/FAIL)
        r = rda.check_btc(btc_fact(77423.98, '2026-10-31'),
                          candle('2026-10-31', 77423.98), SPEC,
                          now_utc=NOW_LATE)
        self.assertEqual(r['verdict'], 'PASS')
        self.assertIn('无close_meta', r['note'])


class F2WWrongDayAndGuards(unittest.TestCase):
    """W: T2错日反例——D vs D±1永不静默PASS;close_meta口径守卫。"""

    def test_w1_neighbor_day_equal_values_not_verified(self):
        # 比较日10-31的K缺失,仅10-30/11-01存在且值恰好相等→NOT_VERIFIED
        f = btc_fact(77430.0, '2026-10-31')
        spec = SPEC
        cand = {'2026-10-30': {'close': 77430.0,
                               'start_ts': epoch_of('2026-10-30')},
                '2026-11-01': {'close': 77430.0,
                               'start_ts': epoch_of('2026-11-01')}}
        r = rda.check_btc(f, cand, spec, now_utc=NOW_LATE,
                          close_meta=meta('2026-10-31'))
        self.assertEqual(r['verdict'], 'NOT_VERIFIED')
        self.assertIn('Coinbase无2026-10-31', r['note'])

    def test_w2_close_meta_mismatch_not_comparable(self):
        # 采集完结口径(10-30)≠比较日(10-31)→NOT_COMPARABLE,外部侧留痕
        r = rda.check_btc(btc_fact(77430.0, '2026-10-31'),
                          candle('2026-10-31', 77423.98), SPEC,
                          now_utc=NOW_LATE, close_meta=meta('2026-10-30'))
        self.assertEqual(r['verdict'], 'NOT_COMPARABLE')
        self.assertEqual(r['external']['collector_completed_through_utc'],
                         '2026-10-30')

    def test_w3_non_utc_day_start_candle_not_verified(self):
        # K线起点非UTC日界00:00Z→日K口径不可证(守卫顺序: 完结性之后仍生效)
        ts_off = epoch_of('2026-10-31') + 3600
        r = rda.check_btc(btc_fact(77430.0, '2026-10-31'),
                          {'2026-10-31': {'close': 77423.98,
                                          'start_ts': ts_off}}, SPEC,
                          now_utc=NOW_LATE, close_meta=meta('2026-10-31'))
        self.assertEqual(r['verdict'], 'NOT_VERIFIED')
        self.assertIn('非UTC日界', r['note'])

    def test_w4_comparison_day_rule_constant_frozen(self):
        # 机械规则常数冻结: 无人工挑选比较日+双侧完结性(合同级口径披露)
        rule = rda.BTC_COMPARISON_DAY_RULE
        self.assertIn('机械透传', rule)
        self.assertIn('无人工挑选', rule)
        self.assertIn('NOT_COMPARABLE', rule)
        self.assertIn('completed_through_utc', rule)

    def test_w5_run_external_checks_threads_meta(self):
        # run_external_checks透传close_meta: 一致→PASS且note含元数据;
        # 不一致→NOT_COMPARABLE(不影响其余七项检查)
        facts = _full_facts()
        log = []
        res, _, _ = rda.run_external_checks(
            facts, _stub_fetchers(facts), DAY, log=log,
            btc_close_meta=meta(OBS))
        btc = next(r for r in res if r['metric_id'] == 'BTC')
        self.assertEqual(btc['verdict'], 'PASS')
        self.assertIn(f'completed_through={OBS}', btc['note'])
        self.assertEqual(btc['check_id'], 'EXT-BTC')
        self.assertTrue(any('[A2-meta]' in ln and 'completed_through='
                            in ln for ln in log))
        log2 = []
        res2, _, _ = rda.run_external_checks(
            facts, _stub_fetchers(facts), DAY, log=log2,
            btc_close_meta=meta('2026-10-22'))
        btc2 = next(r for r in res2 if r['metric_id'] == 'BTC')
        self.assertEqual(btc2['verdict'], 'NOT_COMPARABLE')
        others = {r['metric_id']: r['verdict'] for r in res2
                  if r['metric_id'] != 'BTC'}
        self.assertEqual(others.get('SPX'), 'PASS')   # 其余检查不受影响


def _inject_btc_close_meta(daily_dir, ymd, m):
    """向global采集fixture注入BTC close_meta(模拟W5-FIX2后采集产物)。"""
    p = os.path.join(daily_dir, f'global_{ymd}.json')
    obj = json.load(open(p))
    obj['data']['BTC']['close_meta'] = m
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False)


class F2EMainE2E(unittest.TestCase):
    """E: main()端到端——close_meta经global产物→快照→EXT-BTC全链路。"""

    def _run(self, td, out_sub, extra, factory=None, day=DAY):
        fake_now = f'{DAY[:4]}-{DAY[4:6]}-{DAY[6:]}T08:00:00'

        class _DT(datetime):
            @classmethod
            def now(cls, tz=None):
                return cls.fromisoformat(fake_now)

        outroot = tempfile.mkdtemp(prefix='w5fix2-e-out-')
        outdir = os.path.join(outroot, out_sub)
        out = io.StringIO()
        argv = ['rda', '--data-dir', td, '--out-dir', outdir,
                '--data-day', day, '--trusted-root', td] + extra
        patches = [mock.patch.object(sys, 'argv', argv),
                   mock.patch.object(rda, 'datetime', _DT),
                   contextlib.redirect_stdout(out)]
        if factory is not None:
            patches.append(mock.patch.object(rda, 'default_fetchers',
                                             factory))
        with contextlib.ExitStack() as st:
            for p in patches:
                st.enter_context(p)
            try:
                rda.main()
                rc = 0
            except SystemExit as e:
                rc = e.code
        j = sorted(glob.glob(os.path.join(outdir, 'real_acceptance_*.json')))
        return rc, out.getvalue(), (json.load(open(j[-1])) if j else None), outdir

    def _factory(self):
        """stub外部全匹配(值取自同一确定性fixture快照,零真实网络)。"""
        snap = fixt.real_snapshot(DAY)
        facts = {f['metric_id']: f for f in snap['facts']}

        def _ev(u):
            return {'source': 'stub', 'url': u,
                    'fetched_at_utc': '2026-10-24T00:00:00',
                    'http_status': 200}

        def treasury(year, want):
            rows = {d: {'2 Yr': str(facts['UST_2Y']['value']),
                        '10 Yr': str(facts['UST_10Y']['value']),
                        '30 Yr': str(facts['UST_30Y']['value'])} for d in want}
            return rows, _ev('https://t.gov/curve'), 'raw-treasury'

        def coinbase(product, s, e):
            mid = 'BTC' if product == 'BTC-USD' else 'GOLD_F'
            f = facts.get(mid)
            if not f:
                return {}, _ev('https://c.io/' + product), None
            od = str(f['observation_date'])[:10]
            return {od: {'close': f['value'], 'start_ts': epoch_of(od)}}, \
                _ev('https://c.io/' + product), f'raw-{product}'

        def sina(c):
            f = facts['SHCOMP']
            od = str(f['observation_date'])[:10]
            return {'close': f['value'], 'date': od, 'time': '15:30:00'}, \
                _ev('https://s.cn/' + c), 'raw-sina'

        def fred(sid):
            mid = 'SPX' if sid == 'SP500' else 'WTI_F'
            f = facts[mid]
            od = str(f['observation_date'])[:10]
            return ([(od, f['value'])],
                    _ev('https://api.stlouisfed.org/fred/series/'
                        'observations?series_id=' + sid), f'raw-{sid}')

        return lambda key: {'treasury': treasury, 'coinbase': coinbase,
                            'sina': sina, 'fred': fred}

    def test_e1_close_meta_consistent_pass(self):
        with tempfile.TemporaryDirectory(prefix='w5fix2-e1-') as td:
            fixt.write_collectors(td, DAY)
            _extend_global_history(td, DAY, {
                'SPX': {'2025-12-31': 6800.0, '2026-09-30': 7300.0},
                'GOLD': {'2025-12-31': 3300.0, '2026-09-30': 3550.0}})
            _inject_btc_close_meta(td, DAY, meta(OBS))
            rc, out, rep, _ = self._run(td, 'acc', [], self._factory())
            self.assertEqual(rc, 0)
            self.assertEqual(rep['overall'], 'PASS')
            btc = next(r for r in rep['external_results']
                       if r['metric_id'] == 'BTC')
            self.assertEqual(btc['verdict'], 'PASS')
            self.assertIn(f'completed_through={OBS}', btc['note'])
            # 全链路: global产物close_meta→main读取→summary披露
            cal = rep['btc_close_caliber']
            self.assertEqual(cal['close_meta']['completed_through_utc'], OBS)
            self.assertEqual(cal['comparison_day_rule'],
                             rda.BTC_COMPARISON_DAY_RULE)
            self.assertIn('global_', cal['close_meta_provenance'])
            self.assertIn('读取global输入', out)
            self.assertIn('[A2-meta]', out)

    def test_e2_close_meta_mismatch_not_comparable(self):
        with tempfile.TemporaryDirectory(prefix='w5fix2-e2-') as td:
            fixt.write_collectors(td, DAY)
            _extend_global_history(td, DAY, {
                'SPX': {'2025-12-31': 6800.0, '2026-09-30': 7300.0},
                'GOLD': {'2025-12-31': 3300.0, '2026-09-30': 3550.0}})
            _inject_btc_close_meta(td, DAY, meta('2026-10-22'))  # ≠obs
            rc, out, rep, _ = self._run(td, 'acc', [], self._factory())
            btc = next(r for r in rep['external_results']
                       if r['metric_id'] == 'BTC')
            self.assertEqual(btc['verdict'], 'NOT_COMPARABLE')
            self.assertIn('不一致', btc['note'])
            # 如实披露但不冒充: summary保留不一致的close_meta原值
            self.assertEqual(
                rep['btc_close_caliber']['close_meta']
                    ['completed_through_utc'],
                '2026-10-22')
            # 不阻断其他检查: SPX/SHCOMP照常PASS,整体仍PASS(无FAIL项)
            v = {r['metric_id']: r['verdict'] for r in rep['external_results']}
            self.assertEqual(v.get('SPX'), 'PASS')
            self.assertEqual(v.get('SHCOMP'), 'PASS')
            self.assertEqual(rep['overall'], 'PASS')


if __name__ == '__main__':
    unittest.main(verbosity=2)
