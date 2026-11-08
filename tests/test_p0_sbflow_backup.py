# -*- coding: utf-8 -*-
"""IA-P0-SB-FLOW-BACKUP 专项测试(R058;南向资金东财EM备源修复的离线行为锁)。

任务: IA-P0-SB-FLOW-BACKUP-AC-v1.0 §一 SBF-AC-01/§二 SBF-AC-02 | 基点: 02565b9(R057 merge)
被测对象: scripts/china_market_collector.py(fetch_southbound 主路零变化+_fetch_southbound_em
回落)与 scripts/fact_engine.py(SB_FLOW 来源标签两值制)的真实函数——不复制被测算法。

数据纪律: 本文件全部为**离线 mock 行为锁**,mock 输入为刻意构造的中性数值,不代表任何
真实交易日资金流;真实端点锚定证据(2026-11-05 实测: hist_em 南向 11-04=-32.7717亿/
11-03=+234.2024亿,南向=港股通沪+港股通深 逐分恰等差0.000000)属证据包脱敏 console,
不在本文件冒充。零网络: akshare 以 sys.modules fake 注入(CI 不装 akshare,本地真包亦
被统一覆盖,保证 CI==本地行为一致);tushare 经 mock.patch cmc._pro 替换。

锁清单:
T1 主路回归(tushare 成功路径零变化: 键集/值/无source键/EM不触发;权限拒→回落接管
   不抛未捕获;空返回 df None 与 len==0 两态→回落接管)
T2 EM 回落契约(fixture 三态: 正常=单位×100锁/在途行禁用/日期YYYYMMDD/5日累计/
   north键缺席/schema恰一新增键source;异常→None;空=无行与全在途→None;
   取值行NaN→None;<5完结行无5日键;FROZEN_POST 窗口推进)
T3 fact_engine 标签两值制(source='akshare_em'→channel='akshare_em'+东财calc;
   缺source键(=tushare主路/历史)→channel='tushare'+Tushare calc,旧'eastmoney'
   冒充标签废除;net_buy legacy分支零改动;/100 换算往返锁含真实锚定值复算)
T4 降级如实(主路异常+EM异常→None;主路空+EM空→None;逐次print如实记录三行在场)
T5 源级冻结锁(主路调用参数形态零变化;新通道在场;fact_engine 'eastmoney' 零出现;
   real_data_acceptance.py sha256 冻结零改动锁)

R051 freeze_clock 惯例沿用: 行选择测试一律经冻结时钟注入,被测 _em_max_date/
_em_settled_pairs/_fetch_southbound_em/fetch_southbound 全程真实代码,仅钟被冻结。
"""
import hashlib
import io
import sys
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
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
_ak_fake.stock_hsgt_hist_em = mock.MagicMock(name='stock_hsgt_hist_em')
sys.modules['akshare'] = _ak_fake

import china_market_collector as cmc
import fact_engine as fe


def tushare_hsgt_df(dates, souths, norths):
    """tushare moneyflow_hsgt 形状: trade_date(YYYYMMDD str)/south_money/north_money(百万)。
    数值为刻意中性值,不冒充真实资金流。"""
    return pd.DataFrame({'trade_date': dates, 'south_money': souths, 'north_money': norths})


def em_hsgt_df(rows):
    """akshare stock_hsgt_hist_em(南向资金) 形状: 日期/当日成交净买额(亿港元)等。
    rows: [(date_str, 当日成交净买额, 历史累计净买额)]——刻意中性数值。"""
    return pd.DataFrame({'日期': [r[0] for r in rows],
                         '当日成交净买额': [r[1] for r in rows],
                         '买入成交额': [r[1] * 10.0 for r in rows],
                         '卖出成交额': [r[1] * 11.0 for r in rows],
                         '历史累计净买额': [r[2] for r in rows]})


# R051 W5-EMWIN 惯例: 冻结时钟注入(锚点+monkeypatch助手)——行选择测试时钟无关化。
_HKT = timezone(timedelta(hours=8))
FROZEN_AM = datetime(2026, 11, 4, 10, 0, 0, tzinfo=_HKT)    # 盘中→截止=2026-11-03
FROZEN_POST = datetime(2026, 11, 4, 16, 10, 0, tzinfo=_HKT)  # 收盘后阈值点→截止=2026-11-04

# EM fixture: 5 完结行(中性值,亿港元)+ 1 在途行(999=哨兵,误入选值即断言红)
EM_ROWS = [('2026-10-28', 1.0, 5.0), ('2026-10-29', 2.0, 5.0), ('2026-10-30', 3.0, 5.0),
           ('2026-11-02', 4.0, 5.0), ('2026-11-03', 30.5, 5.0), ('2026-11-04', 999.0, 5.0)]


def freeze_clock(moment):
    """monkeypatch cmc.datetime 为冻结子类: now()/now(tz)恒返同一时刻(aware 原样,
    naive 去tzinfo)——被测模块内所有真实 datetime.now 调用同钟冻结,零代码打桩。"""
    class _FrozenDT(datetime):
        @classmethod
        def now(cls, tz=None):
            return moment if tz is not None else moment.replace(tzinfo=None)
    return mock.patch.object(cmc, 'datetime', _FrozenDT)


def _tushare_pro(df=None, side_effect=None):
    """cmc._pro 替身: 返回 moneyflow_hsgt 可控的假 pro 客户端。"""
    pro = mock.MagicMock(name='pro_client')
    if side_effect is not None:
        pro.moneyflow_hsgt.side_effect = side_effect
    else:
        pro.moneyflow_hsgt.return_value = df
    return mock.patch.object(cmc, '_pro', return_value=pro)


class T1TushareFirst(unittest.TestCase):
    """主路(tushare moneyflow_hsgt)零变化;权限拒/空返回→EM 回落接管(不抛未捕获)。"""

    def test_t1a_success_path_unchanged_and_em_not_called(self):
        em = mock.patch('akshare.stock_hsgt_hist_em').start()
        self.addCleanup(mock.patch.stopall)
        df = tushare_hsgt_df(['20261028', '20261029', '20261030', '20261102', '20261103', '20261103'],
                             [100.0, 200.0, 300.0, 400.0, 500.0, 600.0],
                             [10.0, 20.0, 30.0, 40.0, 50.0, 60.0])
        with _tushare_pro(df=df):
            out = io.StringIO()
            with redirect_stdout(out):
                res = cmc.fetch_southbound()
        # 基线行为锁: 同键同值,date=最后一行,south_money/north_money 原样 round2
        self.assertEqual(res['date'], '20261103')
        self.assertEqual(res['south_money'], 600.0)
        self.assertEqual(res['north_money'], 60.0)
        self.assertEqual(res['south_5d_total'], 2000.0)   # 近5行 200+300+400+500+600
        self.assertEqual(res['north_5d_total'], 200.0)    # 20+30+40+50+60
        self.assertNotIn('source', res)                   # 主路产物零改动(不添 source 键)
        em.assert_not_called()                            # 主路成功→EM 不触发

    def test_t1b_permission_denied_falls_back_no_uncaught(self):
        em = mock.patch('akshare.stock_hsgt_hist_em').start()
        em.return_value = em_hsgt_df(EM_ROWS)
        self.addCleanup(mock.patch.stopall)
        with _tushare_pro(side_effect=Exception('抱歉,您没有接口访问权限')):
            with freeze_clock(FROZEN_AM):
                out = io.StringIO()
                with redirect_stdout(out):
                    res = cmc.fetch_southbound()          # 不得抛未捕获异常
        self.assertEqual(res['source'], 'akshare_em')     # 回落接管
        self.assertEqual(res['south_money'], 3050.0)      # 30.5亿×100(中性值)
        self.assertEqual(res['date'], '20261103')
        self.assertIn('转东财EM回落', out.getvalue())      # 逐次如实记录: 转场行在场
        self.assertIn('没有接口访问权限', out.getvalue())  # 主路失败原因如实落日志

    def test_t1c_empty_df_none_and_len0_both_fall_back(self):
        for empty in (None, pd.DataFrame({'trade_date': [], 'south_money': [], 'north_money': []})):
            with self.subTest(empty=type(empty).__name__):
                em = mock.patch('akshare.stock_hsgt_hist_em').start()
                em.return_value = em_hsgt_df(EM_ROWS)
                self.addCleanup(mock.patch.stopall)
                with _tushare_pro(df=empty):
                    with freeze_clock(FROZEN_AM):
                        with redirect_stdout(io.StringIO()):
                            res = cmc.fetch_southbound()
                self.assertEqual(res['source'], 'akshare_em')   # 空返回两态→回落接管
                self.assertEqual(res['south_money'], 3050.0)


class T2EmFallbackContract(unittest.TestCase):
    """东财回落契约——fixture 三态(正常/异常/空)+单位/行选择/schema 锁。"""

    def _fallback(self, rows=None, moment=FROZEN_AM):
        rows = EM_ROWS if rows is None else rows
        with freeze_clock(moment), \
             mock.patch('akshare.stock_hsgt_hist_em', return_value=em_hsgt_df(rows)):
            return cmc._fetch_southbound_em()

    def test_t2a_normal_state_full_contract(self):
        res = self._fallback()
        self.assertEqual(res['date'], '20261103')            # 在途行 11-04 禁用;YYYYMMDD 规格
        self.assertEqual(res['south_money'], 3050.0)         # 30.5亿港元 ×100 → 百万港元(单位锁)
        self.assertEqual(res['source'], 'akshare_em')        # 恰一新增键,禁冒充 tushare
        self.assertEqual(res['south_5d_total'], 4050.0)      # (1+2+3+4+30.5)亿 ×100
        self.assertNotIn('north_money', res)                 # 北向披露停止,键缺席如实
        self.assertNotIn('north_5d_total', res)
        self.assertEqual(set(res.keys()), {'date', 'south_money', 'source', 'south_5d_total'})

    def test_t2b_exception_state_returns_none(self):
        with mock.patch('akshare.stock_hsgt_hist_em', side_effect=IOError('断连')):
            with redirect_stdout(io.StringIO()):
                self.assertIsNone(cmc._fetch_southbound_em())

    def test_t2c_empty_state_no_rows_and_all_inflight(self):
        for rows in ([], [('2026-11-04', 1.0, 5.0)]):
            with self.subTest(rows=rows):
                with redirect_stdout(io.StringIO()):
                    self.assertIsNone(self._fallback(rows=rows))

    def test_t2d_last_settled_value_nan_returns_none(self):
        rows = [('2026-11-02', 4.0, 5.0), ('2026-11-03', float('nan'), 5.0)]
        with redirect_stdout(io.StringIO()):
            self.assertIsNone(self._fallback(rows=rows))

    def test_t2e_under5_settled_rows_no_5d_key(self):
        rows = [('2026-11-02', 4.0, 5.0), ('2026-11-03', 30.5, 5.0)]
        res = self._fallback(rows=rows)
        self.assertEqual(set(res.keys()), {'date', 'south_money', 'source'})
        self.assertEqual(res['south_money'], 3050.0)

    def test_t2f_post_cutoff_window_advances(self):
        res = self._fallback(moment=FROZEN_POST)             # 16:10:00→截止 2026-11-04
        self.assertEqual(res['date'], '20261104')
        self.assertEqual(res['south_money'], 99900.0)        # 999亿×100(哨兵值入选值行)
        self.assertEqual(res['south_5d_total'], 103850.0)    # (2+3+4+30.5+999)亿×100


class T3HonestTwoValueLabels(unittest.TestCase):
    """fact_engine SB_FLOW 来源标签两值制(tushare/akshare_em,禁冒充)。"""

    AS_OF = "2026-11-04T08:00:00+08:00"

    def _facts(self, data):
        return {f['metric_id']: f for f in fe.normalize_china(data, self.AS_OF)}

    def test_t3a_em_source_label(self):
        by = self._facts({'southbound': {'date': '20261103', 'south_money': 3050.0,
                                         'source': 'akshare_em'}})
        f = by['SB_FLOW']
        self.assertEqual(f['source']['channel'], 'akshare_em')
        self.assertEqual(f['calculation_ref'], '东财南向当日净流入(百万港元→亿港元)')
        self.assertEqual(f['value'], 30.5)

    def test_t3b_missing_source_labeled_tushare_not_eastmoney(self):
        by = self._facts({'southbound': {'date': '20261103', 'south_money': 55187.11}})
        f = by['SB_FLOW']
        self.assertEqual(f['source']['channel'], 'tushare')   # 缺source键=tushare主路/历史
        self.assertNotEqual(f['source']['channel'], 'eastmoney')  # 旧一刀切冒充标签废除
        self.assertEqual(f['calculation_ref'], 'Tushare南向当日净流入(百万港元→亿港元)')
        self.assertEqual(f['value'], 551.87)                  # /100 换算锁(fixt.py 先例值)

    def test_t3c_net_buy_legacy_branch_unchanged(self):
        by = self._facts({'southbound': {'date': '20261103', 'net_buy': 12.34}})
        f = by['SB_FLOW']
        self.assertEqual(f['value'], 12.34)                   # 原值入事实(已是亿港元)
        self.assertEqual(f['calculation_ref'], '当日净买入(亿港元)')
        self.assertNotIn('channel', f['source'])             # 无sub基线行为: 无channel键

    def test_t3d_conversion_roundtrip_with_anchor_value(self):
        # 真实锚定值复算锁(证据包 2026-11-05 实测: -32.7717亿→-3277.17百万→-32.77)
        by = self._facts({'southbound': {'date': '20261104', 'south_money': -3277.17,
                                         'source': 'akshare_em'}})
        self.assertEqual(by['SB_FLOW']['value'], -32.77)
        self.assertEqual(by['SB_FLOW']['source']['channel'], 'akshare_em')


class T4DegradationHonest(unittest.TestCase):
    """降级标记规范: 回落失败=如实 None(source-persist 语义沿用),禁假值禁凑数。"""

    def test_t4a_main_exc_em_exc_returns_none(self):
        with _tushare_pro(side_effect=Exception('没有接口访问权限')):
            with mock.patch('akshare.stock_hsgt_hist_em', side_effect=IOError('断连')):
                out = io.StringIO()
                with redirect_stdout(out):
                    res = cmc.fetch_southbound()             # 不抛未捕获
        self.assertIsNone(res)
        # 逐次如实记录三行在场: 主路❌ → 转场↪️ → 回落失败⚠️
        self.assertIn('❌ 南向资金', out.getvalue())
        self.assertIn('转东财EM回落', out.getvalue())
        self.assertIn('东财南向回落失败', out.getvalue())

    def test_t4b_main_empty_em_empty_returns_none(self):
        empty = pd.DataFrame({'trade_date': [], 'south_money': [], 'north_money': []})
        with _tushare_pro(df=empty):
            with mock.patch('akshare.stock_hsgt_hist_em', return_value=em_hsgt_df([])):
                out = io.StringIO()
                with redirect_stdout(out):
                    self.assertIsNone(cmc.fetch_southbound())
        self.assertIn('无南向资金数据', out.getvalue())       # 主路空返回如实记录
        self.assertIn('东财南向回落', out.getvalue())


class T5SourceFreezeLocks(unittest.TestCase):
    """源级冻结锁: 主路调用零变化/新通道在场/冒充标签废除/验收脚本零触碰。"""

    def test_t5a_main_path_call_form_unchanged(self):
        with open(ROOT + '/scripts/china_market_collector.py', encoding='utf-8') as fh:
            src = fh.read()
        self.assertIn('_pro().moneyflow_hsgt(start_date=start_week, end_date=end_date)', src)
        self.assertIn('ak.stock_hsgt_hist_em(symbol=\'南向资金\')', src)   # 唯一新通道

    def test_t5b_eastmoney_impersonation_label_eradicated(self):
        with open(ROOT + '/scripts/fact_engine.py', encoding='utf-8') as fh:
            src = fh.read()
        self.assertNotIn('eastmoney', src)                   # 旧一刀切标签零残留
        self.assertIn("'akshare_em'", src)                   # 两值制落地
        self.assertIn("'tushare'", src)

    def test_t5c_real_data_acceptance_untouched(self):
        # 零改动锁: sha256 与冻结值一致(AC §七反例3)。
        # v1.1(2026-11-09)显式再冻结一次: 第三轮 WI3(P0-4 密钥卫生)授权把脱敏
        # 参数族从 api_key= 扩到 api_key/apikey/token/key=(负向后顾挡 mid-word),
        # 属规格内变更——新冻结值=变更后文件;后续无授权变更仍必须红面。
        with open(ROOT + '/scripts/real_data_acceptance.py', 'rb') as fh:
            blob = fh.read()
        self.assertEqual(hashlib.sha256(blob).hexdigest(),
                         '30c5aadf4d3e550b055cface116c9eea86170ef24e6a04cd23ecd8d3a82cd95f')


if __name__ == '__main__':
    unittest.main(verbosity=2)
