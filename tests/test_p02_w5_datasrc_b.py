# -*- coding: utf-8 -*-
"""IA-P0-2-W5-DATASRC-B 专项测试(R049;方案B东财备源修复的离线行为锁)。

任务: IA-P0-2-W5-DATASRC-B-AC-v1.0 §三 B-AC-01~04 | 基点: cebc4af(R032 尖端)
被测对象: scripts/china_market_collector.py(F1 指数回落/F2 成交额回落重写)与
scripts/fact_engine.py(F3 恰两处诚实标签)的真实函数——不复制被测算法。

数据纪律: 本文件全部为**离线 mock 行为锁**(合同 B-AC-04 明示"可新增离线 mock 测试
锁: date≤20261103 行选择、÷1e8 单位、via/source 标记"),mock 输入为刻意构造的
中性数值,不代表任何真实交易日行情;真实端点取值证据(3608.10/10876.99/
8108.29/8926.08/17034.37)属证据包双端点实取 console,不在本文件冒充。
零网络: akshare/tushare 均以 unittest.mock 替换,不发起任何真实调用。

锁清单:
T1 F1 tushare先行零变化(成功路径 via='tushare'+EM不触发;空数据无异常仍不回落)
T2 F1 EM回落契约(在途行 date>2026-11-03 禁用/无完结行→None/失败→None/
   schema= tushare键∪{via}恰一新增/week·ytd·pct推导/截止日常量锁)
T3 F2 成交额(方案1零变化: 千元÷1e5且无source键;方案2 EM双取: 元÷1e8 round2/
   在途行禁用/source='akshare_em'/EM失败→None旧新浪回落已删无第三方案)
T4 F3 诚实标签(via透传akshare_em·缺省sina/东财calc分支/缺source原字符串保留/
   旧elif降级分支不变)
T5 源级冻结锁(旧新浪回落调用已删/A_SHARE_INDICES成员顺序不变/61s闸门不变/
   EM_MAP全覆盖)
"""
import io
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock

import pandas as pd

import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import types

# CI 环境不装 akshare(离线套件零真实依赖): 无条件注入确定性 fake,
# 不论真包是否在场统一覆盖,保证 CI==本地行为一致;
# 真实端点证据在证据包 console,不在测试(见文件头声明)。
_ak_fake = types.ModuleType('akshare')
_ak_fake.stock_zh_index_daily_em = mock.MagicMock(name='stock_zh_index_daily_em')
sys.modules['akshare'] = _ak_fake

import china_market_collector as cmc
import fact_engine as fe


def tushare_df(dates, closes):
    """tushare index_daily 形状: trade_date(YYYYMMDD str)/close/pct_chg/vol/amount(千元)。"""
    return pd.DataFrame({'trade_date': dates, 'close': closes,
                         'pct_chg': [0.5] * len(dates), 'vol': [1000.0] * len(dates),
                         'amount': [200000.0] * len(dates)})


def em_df(rows):
    """东财 stock_zh_index_daily_em 形状: date(YYYY-MM-DD str)/open/close/high/low/volume/amount(元)。

    rows: [(date, close, amount)]——刻意中性数值,不冒充真实行情。
    """
    return pd.DataFrame({'date': [r[0] for r in rows],
                         'open': [r[1] * 0.99 for r in rows],
                         'close': [r[1] for r in rows],
                         'high': [r[1] * 1.01 for r in rows],
                         'low': [r[1] * 0.98 for r in rows],
                         'volume': [12345.0 for r in rows],
                         'amount': [r[2] for r in rows]})


class T1TushareFirst(unittest.TestCase):
    """F1: tushare 先行路径零变化;EM 仅在 tushare 抛异常时进入。"""

    def test_t1a_success_path_via_tushare_and_em_not_called(self):
        em = mock.patch('akshare.stock_zh_index_daily_em').start()
        self.addCleanup(mock.patch.stopall)
        with mock.patch.object(cmc, '_index_daily',
                               return_value=tushare_df(['20260105', '20260106', '20260107',
                                                        '20260108', '20260109', '20261103'],
                                                       [100.0, 101.0, 102.0, 103.0, 104.0, 110.0])):
            out = io.StringIO()
            with redirect_stdout(out):
                res = cmc.fetch_a_share_indices()
        item = res['000001.SH']
        self.assertEqual(item['via'], 'tushare')
        self.assertEqual(item['date'], '20261103')
        self.assertEqual(item['close'], 110.0)
        em.assert_not_called()

    def test_t1b_empty_df_no_exception_still_no_fallback(self):
        em = mock.patch('akshare.stock_zh_index_daily_em').start()
        self.addCleanup(mock.patch.stopall)
        empty = pd.DataFrame({'trade_date': [], 'close': [], 'pct_chg': [], 'vol': [], 'amount': []})
        with mock.patch.object(cmc, '_index_daily', return_value=empty):
            with redirect_stdout(io.StringIO()):
                res = cmc.fetch_a_share_indices()
        self.assertNotIn('000001.SH', res)
        em.assert_not_called()

    def test_t1c_exception_triggers_em_fallback(self):
        em = mock.patch('akshare.stock_zh_index_daily_em').start()
        em.return_value = em_df([('2026-10-30', 100.0, 1.0), ('2026-11-03', 105.0, 2.0),
                                 ('2026-11-04', 999.0, 3.0)])
        self.addCleanup(mock.patch.stopall)
        with mock.patch.object(cmc, '_index_daily', side_effect=RuntimeError('频率超限')):
            with redirect_stdout(io.StringIO()):
                res = cmc.fetch_a_share_indices()
        # 全部6只指数 tushare 异常→逐只恰一次 EM 回落,顺序=A_SHARE_INDICES 字典序
        self.assertEqual([c[1]['symbol'] for c in em.call_args_list],
                         ['sh000001', 'sz399001', 'sz399006',
                          'sh000300', 'sh000905', 'sh000852'])
        self.assertEqual(em.call_count, 6)
        for code in cmc.A_SHARE_INDICES:
            self.assertEqual(res[code]['via'], 'akshare_em', code)


class T2IndexEmFallbackContract(unittest.TestCase):
    """F1: 东财回落契约——行选择/标记/schema/推导/常量。"""

    def _fallback(self, rows):
        with mock.patch('akshare.stock_zh_index_daily_em', return_value=em_df(rows)):
            return cmc._fetch_index_em('000001.SH', '上证指数')

    def test_t2a_inflight_row_excluded(self):
        item = self._fallback([('2026-10-31', 100.0, 1.0), ('2026-11-03', 105.0, 2.5),
                               ('2026-11-04', 999.0, 9.9)])  # 在途行
        self.assertEqual(item['date'], '20261103')       # YYYYMMDD 同 tushare 规格
        self.assertEqual(item['close'], 105.0)
        self.assertEqual(item['series']['dates'][-1], '2026-11-03')
        self.assertNotIn('2026-11-04', item['series']['dates'])

    def test_t2b_no_settled_row_returns_none(self):
        with redirect_stdout(io.StringIO()):
            self.assertIsNone(self._fallback([('2026-11-04', 1.0, 1.0)]))

    def test_t2c_em_failure_returns_none(self):
        with mock.patch('akshare.stock_zh_index_daily_em', side_effect=IOError('断连')):
            with redirect_stdout(io.StringIO()):
                self.assertIsNone(cmc._fetch_index_em('000001.SH', '上证指数'))

    def test_t2d_schema_exactly_tushare_keys_plus_via(self):
        with mock.patch.object(cmc, '_index_daily',
                               return_value=tushare_df(['20260105', '20260106', '20260107',
                                                        '20260108', '20260109', '20261103'],
                                                       [100.0, 101.0, 102.0, 103.0, 104.0, 110.0])):
            with redirect_stdout(io.StringIO()):
                tu = cmc.fetch_a_share_indices()['000001.SH']
        em_item = self._fallback([('2026-01-05', 100.0, 1.0), ('2026-01-06', 101.0, 1.0),
                                  ('2026-01-07', 102.0, 1.0), ('2026-01-08', 103.0, 1.0),
                                  ('2026-01-09', 104.0, 1.0), ('2026-11-03', 110.0, 2.0)])
        self.assertEqual(set(em_item.keys()), (set(tu.keys()) - {'via'}) | {'via'})
        self.assertEqual(tu['via'], 'tushare')
        self.assertEqual(em_item['via'], 'akshare_em')

    def test_t2e_week_ytd_pct_derivation(self):
        # 2026年窗 [100,110,120,130,140,200]: week基准=closes[-5]=110(同tushare
        # df.iloc[-5])→(200-110)/110=81.82; ytd=(200-100)/100=100.0;
        # pct=(200-140)/140=42.86;另含2025尾行验证计算窗取值行当年(90.0不入基准)
        rows = [('2025-12-31', 90.0, 1.0),
                ('2026-01-05', 100.0, 1.0), ('2026-01-06', 110.0, 1.0),
                ('2026-01-07', 120.0, 1.0), ('2026-01-08', 130.0, 1.0),
                ('2026-01-09', 140.0, 1.0), ('2026-11-03', 200.0, 2.0)]
        item = self._fallback(rows)
        self.assertEqual(item['week_chg'], 81.82)
        self.assertEqual(item['ytd_chg'], 100.0)
        self.assertEqual(item['pct_chg'], 42.86)
        self.assertEqual(item['series']['dates'][0], '2026-01-05')  # 年窗序列

    def test_t2f_cutoff_constant_frozen(self):
        self.assertEqual(cmc.EM_FALLBACK_MAX_DATE, '2026-11-03')


class T3TurnoverContract(unittest.TestCase):
    """F2: 方案1 零变化 + 方案2 EM 双取重写(旧新浪回落删除)。"""

    def test_t3a_scheme1_unchanged_no_source_key(self):
        em = mock.patch('akshare.stock_zh_index_daily_em').start()
        self.addCleanup(mock.patch.stopall)
        df_sh = tushare_df(['20261030', '20261103'], [3600.0, 3610.0])
        df_sh['amount'] = [8.10829e9, 8.10829e9]      # 千元口径
        df_sz = tushare_df(['20261030', '20261103'], [10800.0, 10880.0])
        df_sz['amount'] = [8.92608e9, 8.92608e9]
        with mock.patch.object(cmc, '_index_daily', side_effect=[df_sh, df_sz]):
            with redirect_stdout(io.StringIO()):
                r = cmc.fetch_turnover()
        self.assertNotIn('source', r)                  # 方案1产物无 source 键
        self.assertEqual(r['date'], '20261103')
        self.assertEqual(r['sh_amount_billion'], round(8.10829e9 / 1e5, 2))   # 千元→亿元 ÷1e5
        self.assertEqual(r['sz_amount_billion'], round(8.92608e9 / 1e5, 2))
        em.assert_not_called()

    def _em_side_effect(self, sh_rows, sz_rows):
        return [em_df(sh_rows), em_df(sz_rows)]

    def test_t3b_scheme2_em_dual_fetch(self):
        sh_rows = [('2026-11-02', 3638.0, 8.474591e11), ('2026-11-03', 3608.1, 123456789012.34),
                   ('2026-11-04', 9999.0, 9.9e11)]     # 在途行
        sz_rows = [('2026-11-02', 11010.0, 9.362363e11), ('2026-11-03', 10876.99, 100000000000.0),
                   ('2026-11-04', 9999.0, 9.9e11)]
        with mock.patch.object(cmc, '_index_daily', side_effect=RuntimeError('频率超限')):
            with mock.patch('akshare.stock_zh_index_daily_em',
                            side_effect=self._em_side_effect(sh_rows, sz_rows)) as em:
                with redirect_stdout(io.StringIO()) as out:
                    r = cmc.fetch_turnover()
        self.assertEqual([c[1]['symbol'] for c in em.call_args_list],
                         ['sh000001', 'sz399001'])      # 双取
        self.assertEqual(r['source'], 'akshare_em')
        self.assertEqual(r['date'], '20261103')          # 在途行禁用+YYYYMMDD同方案1
        self.assertEqual(r['sh_amount_billion'], 1234.57)  # ÷1e8 round2 单位锁
        self.assertEqual(r['sz_amount_billion'], 1000.0)
        self.assertEqual(r['total_amount_billion'], round(1234.57 + 1000.0, 2))
        self.assertIn('成交额', r['label'])

    def test_t3c_em_failure_returns_none_no_sina_fallback(self):
        with mock.patch.object(cmc, '_index_daily', side_effect=RuntimeError('频率超限')):
            with mock.patch('akshare.stock_zh_index_daily_em', side_effect=IOError('断连')):
                with redirect_stdout(io.StringIO()):
                    r = cmc.fetch_turnover()
        self.assertIsNone(r)   # 旧新浪回落已删,无第三方案

    def test_t3d_all_inflight_returns_none(self):
        rows = [('2026-11-04', 1.0, 1.0)]
        with mock.patch.object(cmc, '_index_daily', side_effect=RuntimeError('频率超限')):
            with mock.patch('akshare.stock_zh_index_daily_em',
                            side_effect=self._em_side_effect(rows, rows)):
                with redirect_stdout(io.StringIO()):
                    self.assertIsNone(cmc.fetch_turnover())


class T4HonestLabels(unittest.TestCase):
    """F3: fact_engine 恰两处诚实标签的行为锁。"""

    AS_OF = "2026-11-04T08:00:00+08:00"

    def _facts(self, data):
        return {f['metric_id']: f for f in fe.normalize_china(data, self.AS_OF)}

    def test_t4a_via_passthrough_and_default_sina(self):
        data = {'a_share_indices': {
            '000001.SH': {'name': '上证指数', 'close': 3608.10, 'date': '20261103',
                          'via': 'akshare_em'},
            '399001.SZ': {'name': '深证成指', 'close': 10876.99, 'date': '20261103'}}}
        by = self._facts(data)
        self.assertEqual(by['SHCOMP']['source']['channel'], 'akshare_em')
        self.assertEqual(by['SZCI']['source']['channel'], 'sina')   # 无via→旧行为不变

    def test_t4b_em_calc_branch(self):
        data = {'turnover': {'date': '20261103', 'sh_amount_billion': 8108.29,
                             'sz_amount_billion': 8926.08, 'total_amount_billion': 17034.37,
                             'source': 'akshare_em'}}
        by = self._facts(data)
        self.assertIn('东财 元→亿元', by['SH_AMOUNT']['calculation_ref'])
        self.assertIn('东财 元→亿元', by['SZ_COMPONENT_AMOUNT']['calculation_ref'])
        self.assertIn('东财 元→亿元', by['CN_TOTAL_TURNOVER']['calculation_ref'])
        self.assertEqual(by['CN_TOTAL_TURNOVER']['value'], 17034.37)
        self.assertEqual(by['SH_AMOUNT']['observation_date'], '2026-11-03')

    def test_t4c_missing_source_keeps_original_strings(self):
        data = {'turnover': {'date': '20261103', 'sh_amount_billion': 8000.0,
                             'sz_amount_billion': 9000.0, 'total_amount_billion': 17000.0}}
        by = self._facts(data)
        self.assertEqual(by['SH_AMOUNT']['calculation_ref'],
                         'Tushare 000001.SH amount千元→亿元')
        self.assertEqual(by['SZ_COMPONENT_AMOUNT']['calculation_ref'],
                         'Tushare 399001.SZ amount千元→亿元(成分股口径)')
        self.assertEqual(by['CN_TOTAL_TURNOVER']['calculation_ref'],
                         'sh_amount+sz_component_amount;旧字段total_amount_billion/volume_billion同此口径')

    def test_t4d_old_degraded_elif_branch_unchanged(self):
        data = {'turnover': {'date': '20261103', 'total_amount_billion': 8000.0}}
        f = next(iter(fe.normalize_china(data, self.AS_OF)))
        self.assertEqual(f['metric_id'], 'CN_TOTAL_TURNOVER')
        self.assertEqual(f['calculation_ref'], 'akshare sh000001 amount(仅沪市)')
        self.assertEqual(f['quality_status'], 'DEGRADED')


class T5SourceFreezeLocks(unittest.TestCase):
    """源级冻结锁: 旧新浪回落删除 + 不可变项未被动。"""

    def test_t5a_sina_fallback_call_deleted(self):
        src = open(ROOT + '/scripts/china_market_collector.py', encoding='utf-8').read()
        self.assertNotIn('ak.stock_zh_index_daily(', src)      # 旧新浪回落调用已删
        self.assertIn('ak.stock_zh_index_daily_em(', src)      # 唯一新通道=东财

    def test_t5b_a_share_indices_members_and_order_frozen(self):
        self.assertEqual(list(cmc.A_SHARE_INDICES),
                         ['000001.SH', '399001.SZ', '399006.SZ',
                          '000300.SH', '000905.SH', '000852.SH'])

    def test_t5c_gate_interval_frozen(self):
        self.assertEqual(cmc.INDEX_DAILY_MIN_INTERVAL_SECONDS, 61)

    def test_t5d_em_map_covers_all_indices(self):
        self.assertEqual(set(cmc.EM_MAP), set(cmc.A_SHARE_INDICES))


if __name__ == '__main__':
    unittest.main(verbosity=2)
