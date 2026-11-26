#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""架构整改 T3 回归套件(2026-11-14,PHASE3-PLAN 工单T3: series_store 补
HY_OAS/CURVE_2S10S 周报路径序列通道)。

覆盖:
  A  merge_macro_series 单元面: 新档入 store(HY_OAS/CURVE_2S10S 形态合规值
     逐字)/既有键先占不覆盖/形态不合规(等长破坏/空/非对象)诚实跳过/
     history_note 平节携带·不携带·防孤儿/权属门(未注册键+非 macro source 键
     拒入;history_source 臂放行 DFF=R25 双通道先例;通道别名 WTI→WTI_SPOT_M
     =fe._MACRO_ALIAS 单一权威)/store 键权属纯度全称断言;
  B  新鲜度窗(build_snapshot 全链,窗继承 resolve_inputs 的 macro 档 7 自然日):
     EXACT/窗内 FALLBACK(lag=7)入档·注记随行,窗外(lag=8)与档缺席→macro 键
     诚实缺席零造数·平节不发;
  C  端到端(既有 snapshot_builder 测试 fixture 模式=tests/fixt.py 合成采集档
     →build_snapshot 全链): 既有五池 40 键零回归+macro 18 键逐字入 store
     +序列值形态纯净({'dates','values'}不混注记)+无序列月频键诚实缺席
     +无 history_note 时平节不发+Gate A 状态不因 T3 改变(gate 输入=facts/
     sources_status,与 store 无关)+快照 JSON 可序列化;
  D  查询面回归: research_history_query.load_metric_series(HY_OAS/CURVE_2S10S)
     接入点 A(macro 档经标准化层)不受 T3 影响,同目录真跑可查询。

数据纪律: 全合成 tmpdir fixture+真实注册表(权属门=真门非 mock);零
/Users/cast 绝对路径依赖、零 LIVE 树读取、零网络(CI 干净克隆安全)。
"""
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts'), os.path.join(ROOT, 'tests')):
    if p not in sys.path:
        sys.path.insert(0, p)

import fact_engine as fe            # noqa: E402
import snapshot_builder as sb       # noqa: E402
import research_history_query as rhq  # noqa: E402
import fixt                         # noqa: E402

PASSED, FAILED = [], []


def check(name, cond, detail=''):
    (PASSED if cond else FAILED).append((name, detail))
    print(('  ✅ ' if cond else '  ❌ ') + name + (f' [{detail}]' if not cond and detail else ''))


def _run_case(cls):
    """R42(RDG-20261116-012): 逐类跑 unittest 且 errors/failures 计入退出码——
    旧 unittest.main(exit=False) 只以 check() 台账定退出,测级异常被吞(exit 0)。"""
    from io import StringIO
    suite = unittest.TestLoader().loadTestsFromTestCase(cls)
    res = unittest.TextTestRunner(stream=StringIO(), verbosity=0).run(suite)
    n = len(res.errors) + len(res.failures)
    print(f'   unittest: {res.testsRun} tests, {n} error/failure' if n
          else f'   unittest: {res.testsRun} tests OK')
    return n


# ── 合成序列常量(升序 6 点;值任选合法域内,不冒充真实采集) ──
D6 = ['2026-11-09', '2026-11-10', '2026-11-11', '2026-11-12', '2026-11-13', '2026-11-14']
V_HY = [5.35, 5.32, 5.28, 5.30, 5.26, 5.20]
V_CURVE = [0.28, 0.25, 0.31, 0.33, 0.29, 0.30]
V_UST = [4.31, 4.30, 4.26, 4.28, 4.27, 4.28]
V_DFF = [4.33, 4.33, 4.33, 4.33, 4.33, 4.33]
V_WTI = [71.8, 71.5, 71.2, 71.0, 71.4, 71.3]
NOTE_HY = ('源端历史自2023-11-14起(晚于采集窗起点2016-11-14约7年)——'
           '源侧窗口上限,非采集器截断;序列深度以源端为准')


def _ser(vals):
    return {'dates': D6[:len(vals)], 'values': vals}


def _macro_raw(items):
    return {'macro': {'date': '20261114', 'data': dict(items)}}


def _full_items():
    """A 组合成 macro data: 合规 5 键 + 权属/形态反例各若干(全真实注册身份)。"""
    return {
        'HY_OAS': {'value': 5.20, 'date': '2026-11-13', 'frequency': 'daily',
                   'series': _ser(V_HY), 'history_note': NOTE_HY},
        'CURVE_2S10S': {'value': 0.30, 'date': '2026-11-13', 'frequency': 'daily',
                        'series': _ser(V_CURVE)},
        'UST_10Y': {'value': 4.28, 'date': '2026-11-13', 'frequency': 'daily',
                    'series': _ser(V_UST)},
        # DFF: registry source=rate_expectations+history_source=macro_collector
        # (R25 双通道先例)——门=history_source 优先回落 source,应放行
        'DFF': {'value': 4.33, 'date': '2026-11-13', 'frequency': 'daily',
                'series': _ser(V_DFF)},
        # 通道别名: 档内键 WTI→注册表 WTI_SPOT_M(fe._MACRO_ALIAS 单一权威)
        'WTI': {'value': 71.3, 'date': '2026-10-31', 'frequency': 'monthly',
                'series': _ser(V_WTI)},
        # 权属门反例①: 注册表在场但 source=japan_rate_collector(非 macro)
        'BOJ_POLICY_RATE': {'value': 0.5, 'date': '2026-11-13',
                            'series': _ser([0.5] * 6)},
        # 权属门反例②: 未注册键
        'FAKE_X': {'value': 1.0, 'date': '2026-11-13', 'series': _ser([1.0] * 6)},
        # 形态反例①: 等长破坏(dates 6/values 5)——携带注记,验证防孤儿
        'SOFR': {'value': 4.3, 'date': '2026-11-13', 'frequency': 'daily',
                 'series': {'dates': D6, 'values': [4.3] * 5},
                 'history_note': 'sofr窗注记(序列未入档→注记不得入平节)'},
        # 形态反例②: 空
        'ICSA': {'value': 221000.0, 'date': '2026-11-12', 'frequency': 'weekly',
                 'series': {'dates': [], 'values': []}},
        # 形态反例③: series 非对象
        'TIPS_5Y': {'value': 2.35, 'date': '2026-11-13', 'frequency': 'daily',
                    'series': 'not-a-dict'},
    }


# R9-01 统一有效观测规则: 等长破坏不再整段拒绝——短侧配对(前 5 对)
# +登记入档;SOFR(dates6/values5)入 store 为 5 有效观测。
EXPECT_A = {'HY_OAS', 'CURVE_2S10S', 'UST_10Y', 'DFF', 'WTI_SPOT_M', 'SOFR'}


class TestAMergeUnit(unittest.TestCase):
    """A: merge_macro_series 单元面(纯函数,tmpdir 零依赖)。"""

    def test_a1_gate_and_membership(self):
        store, notes = {}, {}
        notes = sb.merge_macro_series(store, _macro_raw(_full_items()))
        check('A1 放行键集恰=合规 macro 序列(泛化门,无白名单)',
              set(store) == EXPECT_A, f"got={sorted(store)}")
        check('A1 WTI 别名归位: 档键 WTI 不入 store', 'WTI' not in store)
        check('A1 注册表身份 WTI_SPOT_M 在 store', 'WTI_SPOT_M' in store)
        check('A1 未注册键 FAKE_X 拒入', 'FAKE_X' not in store)
        check('A1 非 macro source 键 BOJ_POLICY_RATE 拒入(权属门)',
              'BOJ_POLICY_RATE' not in store)
        check('A1 history_source 臂放行 DFF(事实权威 rate/历史序列 macro)',
              'DFF' in store)

    def test_a2_values_verbatim(self):
        store = {}
        sb.merge_macro_series(store, _macro_raw(_full_items()))
        check('A2 HY_OAS 序列值逐字相等(dates+values 全等)',
              store.get('HY_OAS') == {'dates': D6, 'values': V_HY})
        check('A2 CURVE_2S10S 序列值逐字相等',
              store.get('CURVE_2S10S') == {'dates': D6, 'values': V_CURVE})
        check('A2 UST_10Y 序列值逐字相等',
              store.get('UST_10Y') == {'dates': D6, 'values': V_UST})
        check('A2 序列值形态纯净: 键恰为 {dates,values} 不混注记',
              all(set(v.keys()) == {'dates', 'values'} for v in store.values()))

    def test_a3_shape_invalid_skipped(self):
        store = {}
        sb.merge_macro_series(store, _macro_raw(_full_items()))
        check('A3 等长破坏(SOFR dates6/values5)→ 短侧配对入档 5 有效'
              '(R9-01 统一规则,不整段拒绝)',
              store.get('SOFR') == {'dates': D6[:5], 'values': [4.3] * 5})
        check('A3 空序列(ICSA)诚实跳过', 'ICSA' not in store)
        check('A3 series 非对象(TIPS_5Y)诚实跳过', 'TIPS_5Y' not in store)

    def test_a4_preempt_no_overwrite(self):
        sentinel = {'dates': ['2020-01-01'], 'values': [1.23]}
        store = {'UST_10Y': dict(sentinel), 'HY_OAS': dict(sentinel)}
        notes = sb.merge_macro_series(store, _macro_raw(_full_items()))
        check('A4 store 既有键先占不覆盖(UST_10Y 哨兵原样)',
              store['UST_10Y'] == sentinel, str(store['UST_10Y']))
        check('A4 先占键的注记不得入平节(HY_OAS 未经本通道入档)',
              'HY_OAS' not in notes)

    def test_a5_notes_flat_section(self):
        store = {}
        notes = sb.merge_macro_series(store, _macro_raw(_full_items()))
        check('A5 history_note 随序列入平节(HY_OAS 逐字)',
              notes.get('HY_OAS') == NOTE_HY)
        check('A5 无注记键不入平节(CURVE_2S10S/UST_10Y/DFF/WTI_SPOT_M)',
              set(notes) == {'HY_OAS', 'SOFR'}, f"got={sorted(notes)}")
        check('A5 短侧配对入档序列的注记随入平节(R9-01: 序列入档'
              '注记不孤儿,SOFR)', notes.get('SOFR') is not None)

    def test_a6_no_macro_channel(self):
        store = {'SPX': {'dates': ['2026-11-13'], 'values': [7659.44]}}
        notes = sb.merge_macro_series(store, {})
        check('A6 raw 无 macro 键→零产出(窗内无档=序列缺席的单元面)',
              notes == {} and set(store) == {'SPX'})
        notes2 = sb.merge_macro_series(store, {'macro': 'not-a-dict'})
        check('A6 macro 节非对象→零产出不炸', notes2 == {} and set(store) == {'SPX'})

    def test_a7_ownership_purity(self):
        store = {}
        sb.merge_macro_series(store, _macro_raw(_full_items()))
        bad = [k for k, v in store.items()
               if not ((fe.metric(k) or {}).get('history_source')
                       or (fe.metric(k) or {}).get('source')) == 'macro_collector']
        check('A7 store 全称纯度: 每键注册表在册且 (history_source|source)'
              '==macro_collector', bad == [], str(bad))


class TestBFreshnessWindow(unittest.TestCase):
    """B: 新鲜度窗继承 resolve_inputs macro 档窗(rp.SOURCE_FILE_RULES=7 自然日)。"""

    def _build(self, files, target='20261114'):
        with tempfile.TemporaryDirectory() as td:
            for fname, obj in files.items():
                with open(os.path.join(td, fname), 'w', encoding='utf-8') as f:
                    json.dump(obj, f, ensure_ascii=False)
            snap = sb.build_snapshot(target_ymd=target, data_dir=td, out_dir=td,
                                     trusted_root=td,
                                     as_of='2026-11-14T08:00:00+08:00',
                                     write=False)
            return snap

    def _macro_file(self):
        return {'date': '20261114', 'data': {
            'HY_OAS': {'value': 5.20, 'date': '2026-11-13', 'frequency': 'daily',
                       'series': _ser(V_HY), 'history_note': NOTE_HY},
            'CURVE_2S10S': {'value': 0.30, 'date': '2026-11-13',
                            'frequency': 'daily', 'series': _ser(V_CURVE)}}}

    def test_b1_exact_and_in_window_fallback(self):
        snap = self._build({'macro_20261114.json': self._macro_file()})
        st = snap['sources_status']['macro']
        check('B1 当日档 EXACT', st['status'] == 'EXACT', str(st))
        store = snap.get('series_store') or {}
        check('B1 EXACT 档→HY_OAS/CURVE_2S10S 入 store',
              {'HY_OAS', 'CURVE_2S10S'} <= set(store))
        check('B1 注记平节随行',
              (snap.get('series_store_notes') or {}).get('HY_OAS') == NOTE_HY)
        # 窗内 fallback: lag=7 == max_fallback_days(macro 通道)仍可用
        snap2 = self._build({'macro_20261107.json': self._macro_file()})
        st2 = snap2['sources_status']['macro']
        check('B2 lag=7(=macro 窗上限)FALLBACK 可用',
              st2['status'] == 'FALLBACK' and st2.get('lag_days') == 7, str(st2))
        store2 = snap2.get('series_store') or {}
        check('B2 窗内回退档→两序列仍入 store',
              {'HY_OAS', 'CURVE_2S10S'} <= set(store2))

    def test_b3_out_of_window_absent(self):
        snap = self._build({'macro_20261106.json': self._macro_file()})  # lag=8>7
        st = snap['sources_status']['macro']
        check('B3 lag=8(>macro 窗)→通道 MISSING(过期档不冒充)', st['status'] == 'MISSING',
              str(st))
        store = snap.get('series_store') or {}
        check('B3 窗外档→macro 键诚实缺席零造数',
              'HY_OAS' not in store and 'CURVE_2S10S' not in store)
        check('B3 窗外档→注记平节不发', 'series_store_notes' not in snap)

    def test_b4_no_macro_file(self):
        snap = self._build({'global_20261114.json': {'date': '20261114', 'data': {
            'SPX': {'close': 7659.44, 'date': '2026-11-13',
                    'series': {'dates': ['2026-11-12', '2026-11-13'],
                               'values': [7650.0, 7659.44]}}}}})
        check('B4 macro 档缺席→键缺席零造数',
              'HY_OAS' not in (snap.get('series_store') or {}))
        check('B4 macro 档缺席→注记平节不发', 'series_store_notes' not in snap)
        check('B4 既有 global 池不受影响(SPX 在 store)',
              'SPX' in (snap.get('series_store') or {}))


# 既有五池基线(tests/fixt.py 合成研究日;T3 前=40 键,实测锚定)
BASE_POOLS = {'AAPL', 'BRENT_F', 'BTC', 'CHINEXT', 'DXY', 'EEM', 'EURUSD', 'EWG',
              'EWJ', 'EWU', 'EZU', 'FEZ', 'FXI', 'GBPUSD', 'GLD', 'GOLD_F', 'HSCEI',
              'HSI', 'HYG', 'IEF', 'INDA', 'LQD', 'MSFT', 'NDX', 'NIKKEI225', 'NVDA',
              'RUT', 'SHCOMP', 'SHY', 'SILVER_F', 'SPX', 'SPX_CAPE', 'SPX_PE_TTM',
              'SZCI', 'TLT', 'USDCNY', 'USDJPY', 'USO', 'VIX', 'WTI_F'}
YMD = '20261106'


class TestCEndToEnd(unittest.TestCase):
    """C: fixt 合成采集档→build_snapshot 全链(既有 snapshot 测试 fixture 模式)。"""

    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        cls.dir = cls.td.name
        fixt.write_collectors(cls.dir, YMD)
        cls.snap = sb.build_snapshot(target_ymd=YMD, data_dir=cls.dir,
                                     out_dir=cls.dir, trusted_root=cls.dir,
                                     as_of=fixt.as_of_for(YMD), write=False)
        cls.store = cls.snap.get('series_store') or {}
        cls.payload = fixt.collector_payloads(YMD, fixt.obs_for(YMD))

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def test_c1_baseline_pools_no_regression(self):
        check('C1 既有五池 40 键全在场(T3 纯增量)',
              BASE_POOLS <= set(self.store),
              str(sorted(BASE_POOLS - set(self.store))))

    def test_c2_macro_pool_verbatim(self):
        md = self.payload['macro']['data']
        macro_keys = {k for k, v in md.items()
                      if isinstance(v, dict) and isinstance(v.get('series'), dict)}
        expect = {(fe._MACRO_ALIAS.get(k, k)) for k in macro_keys} & set(self.store)
        # fixt macro 带序列键: 15 日频 + CPI/NFP/US_REAL_GDP = 18(实测锚定)
        check('C2 macro 池 18 键入 store(泛化: 非仅工单两键)',
              len(expect) == 18, f'n={len(expect)}')
        bad = [k for k in expect if self.store[k] != md[
            next(m for m in macro_keys if fe._MACRO_ALIAS.get(m, m) == k)]['series']]
        check('C2 全部 macro 序列逐字相等(值零改写零造数)', bad == [], str(bad))
        check('C2 工单两键在场: HY_OAS/CURVE_2S10S',
              {'HY_OAS', 'CURVE_2S10S'} <= set(self.store))

    def test_c3_honest_absence(self):
        check('C3 fixture 无序列的 macro 键诚实缺席(UNEMPLOYMENT 无 series 不入)',
              'UNEMPLOYMENT' not in self.store)

    def test_c4_notes_section(self):
        check('C4 无 history_note 的研究日→平节不发(fixt macro 无注记)',
              'series_store_notes' not in self.snap)

    def test_c5_gate_unchanged(self):
        # gate 输入=facts/sources_status(recompute_gate_a),与 store 无关;
        # 本断言钉住 fixture 既有降级不被 T3 改变
        check('C5 Gate A 状态不因 T3 改变(fixt 研究日=DEGRADED 既有值)',
              self.snap['gate_a']['status'] == 'DEGRADED',
              self.snap['gate_a']['status'])

    def test_c6_serializable(self):
        try:
            json.dumps(self.snap, ensure_ascii=False)
            ok = True
        except Exception as e:  # pragma: no cover
            ok = False
        check('C6 快照整体 JSON 可序列化(新平节无不可序列化类型)', ok)


class TestDQueryRegression(unittest.TestCase):
    """D: 查询面回归——接入点 A(research_history_query)不受 T3 影响。"""

    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        cls.dir = cls.td.name
        fixt.write_collectors(cls.dir, YMD)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def test_d1_hy_oas_queryable(self):
        p = rhq.load_metric_series('HY_OAS', YMD, data_dir=self.dir,
                                   trusted_root=self.dir)
        check('D1 HY_OAS 经登记接入点 A 可查询(n=6 全史)',
              len(p['dates']) == 6, f"n={len(p['dates'])}")
        check('D1 单位/身份=注册表权威(percentage_point)',
              p['unit'] == 'percentage_point', p['unit'])

    def test_d2_curve_queryable(self):
        p = rhq.load_metric_series('CURVE_2S10S', YMD, data_dir=self.dir,
                                   trusted_root=self.dir)
        check('D2 CURVE_2S10S 经登记接入点 A 可查询(n=6 全史)',
              len(p['dates']) == 6, f"n={len(p['dates'])}")


def main():
    print('══ 架构整改 T3 回归套件(series_store 补 macro 通道)══')
    case_errs = 0
    for cls in (TestAMergeUnit, TestBFreshnessWindow, TestCEndToEnd,
                TestDQueryRegression):
        print(f'── {cls.__name__} ──')
        case_errs += _run_case(cls)
    total, bad = len(PASSED) + len(FAILED), len(FAILED)
    print(f"\n{'='*60}\nT3 回归: {len(PASSED)} PASS / {len(FAILED)} FAIL (共{total}判定)")
    if FAILED or case_errs:
        for n, d in FAILED:
            print(f"  ❌ {n} [{d}]")
        if case_errs:
            print(f'  ❌ 测级异常×{case_errs}(unittest errors/failures,见上方逐类行)')
        sys.exit(1)
    print('全部通过 ✅')
    sys.exit(0)


if __name__ == '__main__':
    main()
