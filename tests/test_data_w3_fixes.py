# -*- coding: utf-8 -*-
"""IA-DATA-W3(数据线第2包·修复, R010)专项测试——确定性修复的离线行为锁。

任务: IA-DATA-W3-AC-v1.0 §一 W3-AC-01 | 基点: 09bdd93(main, R054文档笔)
被测对象: scripts/china_market_collector.py 的真实函数(fetch_margin 契约键映射/
裸except清零留日志/fetch_valuation 双形态+上证身份对齐)与 scripts/fact_engine.py
的消费链(只读调用,零改动)——不复制被测算法。

数据纪律: 本文件全部为**离线合成 fixture 行为锁**(合同 AC-01(e): 全合成、零网络、
函数级直测)——mock 输入为刻意构造的中性数值(两融余额/PE 量级取注册校验范围内的
中性值),不代表任何真实交易日数据;真实采集证据属 AC-02 证据包,不在本文件冒充。
零网络: akshare/tushare/yfinance 均以 unittest.mock 替换,不发起任何真实调用;
除被测模块外 import 面纯标准库+项目既有依赖(pandas/unittest.mock),零新增第三方。

锁清单(对照 AC-01):
T1 (a)MARGIN_BAL 映射: 成功响应(rzye/rqye)→契约键 margin.balance(两融合计
   ÷1e8 亿元 round2)+原键保留;多交易所先行汇总;引擎链字段契约一致;
   失败路径可归因(日志含指标标识+异常类型)+5日重试语义不变
T2 (c)SH_PE: VALUATION_INDICES 纳入 000001.SH 且与 A_SHARE_INDICES 身份对齐;
   双形态(扁平 pe / 嵌套 pe_ttm)兼容;扁平桥接 valuation.pe+date 恰取上证
   (身份锁: 300 的越界诱饵不冒充);上证失败→不写扁平键;引擎链契约一致
T3 (b)裸except清零: 源级裸 except: 计数=0;腾讯日K/yfinance YTD/新浪rt行解析/
   估值逐只失败四条原静默路径全部留日志(标识+类型)且返回语义零变化
T4 源级冻结锁: A_SHARE_INDICES 成员顺序不变/61s 闸门常量不变/EM_MAP 全覆盖
   (R049/R051 交付物未被本轮削弱的回归证据)
"""
import io
import re
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

# CI 环境不装 akshare(离线套件零真实依赖): 无条件注入确定性 fake(与
# test_p02_w5_datasrc_b.py 同惯例),不论真包是否在场统一覆盖。
_ak_fake = types.ModuleType('akshare')
_ak_fake.stock_zh_index_daily_em = mock.MagicMock(name='stock_zh_index_daily_em')
sys.modules['akshare'] = _ak_fake

import china_market_collector as cmc
import fact_engine as fe


def margin_df(rows):
    """tushare margin 响应形状: 每交易所一行 rzye/rqye(元)——刻意中性数值。"""
    return pd.DataFrame({'rzye': [r[0] for r in rows], 'rqye': [r[1] for r in rows]})


def dailybasic_df(pe_pairs, pe_col='pe_ttm'):
    """tushare index_dailybasic 响应形状(逐指数一行序列): pe 双形态由 pe_col 决定
    ('pe_ttm'=嵌套实测形态/'pe'=扁平旧形态)。pe_pairs: [(date, pe), ...]。"""
    return pd.DataFrame({'trade_date': [p[0] for p in pe_pairs],
                         pe_col: [p[1] for p in pe_pairs],
                         'pb': [1.2] * len(pe_pairs),
                         'turnover_rate': [1.0] * len(pe_pairs),
                         'total_mv': [5e13] * len(pe_pairs)})


class T1MarginBalanceMapping(unittest.TestCase):
    """AC-01(a): fetch_margin 成功响应(rzye/rqye)→契约键 balance。"""

    AS_OF = "2026-11-04T21:00:00+08:00"

    def _fetch(self, df_or_exc):
        pro = mock.MagicMock(name='pro')
        if isinstance(df_or_exc, BaseException):
            pro.margin.side_effect = df_or_exc
        else:
            pro.margin.return_value = df_or_exc
        with mock.patch.object(cmc, '_pro', return_value=pro):
            with redirect_stdout(io.StringIO()):
                return cmc.fetch_margin(), pro

    def test_t1a_success_response_maps_to_contract_balance_key(self):
        # 成功响应实含 rzye/rqye → balance=(Σrzye+Σrqye)/1e8 亿元 round2(注册口径)
        r, _ = self._fetch(margin_df([(1.85e12, 5e10), (0.6e12, 1e10)]))
        self.assertIn('balance', r)
        self.assertEqual(r['balance'], round((1.85e12 + 0.6e12 + 5e10 + 1e10) / 1e8, 2))
        # 原键原样保留(旧行为零变化)
        self.assertEqual(r['rzye'], round(1.85e12 + 0.6e12, 2))
        self.assertEqual(r['rqye'], round(5e10 + 1e10, 2))
        self.assertEqual(r['rzye_billion'], round((1.85e12 + 0.6e12) / 1e8, 2))
        self.assertIn('date', r)

    def test_t1b_engine_consumes_balance_field(self):
        # 字段契约一致: fact_engine L364-366 mg.get('balance') → MARGIN_BAL 事实
        r, _ = self._fetch(margin_df([(1.85e12, 5e10), (0.6e12, 1e10)]))
        facts = {f['metric_id']: f for f in fe.normalize_china({'margin': r}, self.AS_OF)}
        self.assertIn('MARGIN_BAL', facts)
        self.assertEqual(facts['MARGIN_BAL']['value'], r['balance'])

    def test_t1c_failure_returns_none_with_attributable_log(self):
        # 反例锁: 不再吞异常——失败路径日志含指标标识(margin)+日期+异常类型/摘要
        pro = mock.MagicMock()
        pro.margin.side_effect = Exception('抱歉,您每天最多访问该接口5次')
        with mock.patch.object(cmc, '_pro', return_value=pro):
            out = io.StringIO()
            with redirect_stdout(out):
                r = cmc.fetch_margin()
        self.assertIsNone(r)
        s = out.getvalue()
        self.assertIn('融资融券(margin)', s)   # 指标标识
        self.assertIn('Exception', s)          # 异常类型
        self.assertIn('5次', s)                # 异常摘要(限流可归因)

    def test_t1d_five_day_retry_semantics_unchanged(self):
        # 重试语义零变化: 逐日回看 5 次(0..4)失败后才放弃
        pro = mock.MagicMock()
        pro.margin.side_effect = Exception('接口限流')
        with mock.patch.object(cmc, '_pro', return_value=pro):
            with redirect_stdout(io.StringIO()):
                r = cmc.fetch_margin()
        self.assertIsNone(r)
        self.assertEqual(pro.margin.call_count, 5)


class T2ShPeValuation(unittest.TestCase):
    """AC-01(c): 上证身份对齐 + 双形态兼容 + 扁平桥接恰取上证。"""

    AS_OF = "2026-11-04T21:00:00+08:00"

    def _fetch(self, df_by_code_or_exc):
        pro = mock.MagicMock(name='pro')

        def _by_code(ts_code=None, **kw):
            v = df_by_code_or_exc.get(ts_code)
            if isinstance(v, BaseException):
                raise v
            return v
        pro.index_dailybasic.side_effect = lambda **kw: _by_code(**kw)
        with mock.patch.object(cmc, '_pro', return_value=pro):
            out = io.StringIO()
            with redirect_stdout(out):
                return cmc.fetch_valuation(), out.getvalue()

    def test_t2a_valuation_indices_identity_aligned(self):
        # 000001.SH 纳入估值名单首位;既有 300/500/1000 成员与顺序零变化
        self.assertEqual(list(cmc.VALUATION_INDICES),
                         ['000001.SH', '000300.SH', '000905.SH', '000852.SH'])
        self.assertIn('000001.SH', cmc.A_SHARE_INDICES)   # 与价格通道身份对齐
        self.assertEqual(cmc.SH_PE_IDENTITY, '000001.SH')

    def test_t2b_nested_pe_ttm_form_produces_both_shapes(self):
        # 嵌套形态: 产物含 per-index 嵌套对象(原格式保留)+ 扁平 pe/date(引擎契约)
        v, _ = self._fetch({c: dailybasic_df([('20261103', 15.0), ('20261104', 14.5)])
                            for c in cmc.VALUATION_INDICES})
        for c in cmc.VALUATION_INDICES:
            self.assertIn(c, v)
            self.assertEqual(v[c]['pe_ttm'], 14.5)
        self.assertEqual(v['pe'], 14.5)          # 扁平桥接=上证 pe_ttm
        self.assertEqual(v['date'], '20261104')

    def test_t2c_flat_pe_form_supported(self):
        # 扁平形态: 载荷 pe 列(无 pe_ttm)→_pe_value 取 pe;嵌套 pe_ttm 回退 0(原语义)
        v, _ = self._fetch({c: dailybasic_df([('20261103', 13.0)], pe_col='pe')
                            for c in cmc.VALUATION_INDICES})
        self.assertEqual(v['pe'], 13.0)
        self.assertEqual(v['000001.SH']['pe_ttm'], 0)   # 原嵌套语义零变化

    def test_t2d_flat_pe_identity_is_sh_not_decoy(self):
        # 身份锁: 000300 越界诱饵(999)不冒充上证——扁平 pe 恰取 000001.SH
        dfs = {c: dailybasic_df([('20261104', 20.0)]) for c in cmc.VALUATION_INDICES}
        dfs['000300.SH'] = dailybasic_df([('20261104', 999.0)])
        dfs['000001.SH'] = dailybasic_df([('20261104', 15.0)])
        v, _ = self._fetch(dfs)
        self.assertEqual(v['pe'], 15.0)

    def test_t2e_sh_failure_writes_no_flat_keys(self):
        # 上证失败→不写扁平键(如实缺失,不以 300/500/1000 冒充);其余嵌套照采
        dfs = {c: dailybasic_df([('20261104', 12.0)])
               for c in cmc.VALUATION_INDICES if c != '000001.SH'}
        dfs['000001.SH'] = RuntimeError('每天最多访问该接口5次')
        v, s = self._fetch(dfs)
        self.assertNotIn('pe', v)
        self.assertNotIn('date', v)
        self.assertIn('000300.SH', v)
        self.assertIn('000001.SH', s)   # 失败留痕(标识+类型)
        self.assertIn('RuntimeError', s)

    def test_t2f_engine_consumes_flat_pe(self):
        # 字段契约一致: fact_engine L367-369 val.get('pe') → SH_PE 事实
        v, _ = self._fetch({c: dailybasic_df([('20261104', 14.5)])
                            for c in cmc.VALUATION_INDICES})
        facts = {f['metric_id']: f for f in fe.normalize_china({'valuation': v}, self.AS_OF)}
        self.assertIn('SH_PE', facts)
        self.assertEqual(facts['SH_PE']['value'], v['pe'])
        self.assertEqual(facts['SH_PE']['observation_date'], '2026-11-04')

    def test_t2g_pe_value_helper_vectors(self):
        # _pe_value 双形态向量: 扁平 pe 优先→嵌套 pe_ttm→双缺 None→不可数值化 None
        self.assertEqual(cmc._pe_value({'pe': 12.34}), 12.34)
        self.assertEqual(cmc._pe_value({'pe_ttm': 9.87}), 9.87)
        self.assertEqual(cmc._pe_value({'pe': None, 'pe_ttm': 8.8}), 8.8)
        self.assertIsNone(cmc._pe_value({}))
        with redirect_stdout(io.StringIO()) as out:
            self.assertIsNone(cmc._pe_value({'pe': 'abc'}))
        self.assertIn('估值PE取值失败', out.getvalue())   # 不可数值化亦留痕


class T3NoSilentExceptions(unittest.TestCase):
    """AC-01(b): 裸 except 清零,静默异常路径全部留日志且返回语义零变化。"""

    def test_t3a_no_bare_except_in_source(self):
        with open(ROOT + '/scripts/china_market_collector.py', encoding='utf-8') as f:
            src = f.read()
        bare = [ln for ln in src.splitlines() if re.match(r'^\s*except\s*:', ln)]
        self.assertEqual(bare, [])   # 裸 except: 计数=0(注释行不匹配行首模式)

    def test_t3b_tx_kline_failure_logs_code_and_type(self):
        class _Boom:
            def get(self, *a, **k):
                raise OSError('断连')
        with mock.patch.object(cmc, '_direct_session', return_value=_Boom()):
            out = io.StringIO()
            with redirect_stdout(out):
                rows = cmc._tx_kline_rows('hkHSI', bars=5, retries=0)
        self.assertEqual(rows, [])                     # 返回语义零变化
        s = out.getvalue()
        self.assertIn('hkHSI', s)                      # 指标标识
        self.assertIn('OSError', s)                    # 异常类型

    def test_t3c_sina_rt_parse_failure_logs(self):
        out = io.StringIO()
        with redirect_stdout(out):
            r = cmc._parse_sina_rt_line('var hq_str_rt_hkHSAHP="a,b,c,d,e,f,x,h"')
        self.assertIsNone(r)                           # 解析契约零变化
        self.assertIn('新浪rt行解析失败', out.getvalue())
        self.assertIn('ValueError', out.getvalue())

    def test_t3d_yfinance_ytd_failure_logs_and_keeps_result(self):
        # Charter8(HK 深度补拉, 2026-11-10)机制迁移: 1mo+单独ytd请求 → 单次
        # 10y 全序列,ytd/week 统一由 _hk_metrics_from_daily 从序列计算
        # (独立ytd请求的失败面已随机制删除)。锁面迁移不减: ①单请求纪律
        # (恰一次 history 调用,period='10y');②ytd=当年首收盘基准的独立
        # 手算期望;③异常路径仍带标识+类型留日志(AC-01b 纪律保持)。
        hist = pd.DataFrame({'Close': [100.0, 101.0, 102.0, 103.0, 104.0, 105.0]},
                            index=pd.DatetimeIndex(pd.date_range('2026-10-27', periods=6)))
        calls = []

        class _FakeTicker:
            def __init__(self, symbol):
                pass

            def history(self, period):
                calls.append(period)
                return hist
        with mock.patch.object(cmc.yf, 'Ticker', _FakeTicker):
            out = io.StringIO()
            with redirect_stdout(out):
                r = cmc._fetch_hk_yfinance('^HSI', '恒生指数', retries=0)
        self.assertIsNotNone(r)
        self.assertEqual(calls, ['10y'])               # 单请求纪律(无第二次ytd调用)
        # ytd 手算: 当年(2026)首个收盘=100.0, 末值105.0 → +5.0%
        self.assertEqual(r['ytd_chg'], round((105.0 / 100.0 - 1) * 100, 2))
        self.assertEqual(r['week_chg'], round((105.0 / 101.0 - 1) * 100, 2))
        self.assertEqual(r['series']['dates'][0], '2026-10-27')

        # 异常路径: history 抛错 → None + 标识+类型留日志(AC-01b 保持)
        class _BoomTicker:
            def __init__(self, symbol):
                pass

            def history(self, period):
                raise OSError('429 Too Many Requests')
        with mock.patch.object(cmc.yf, 'Ticker', _BoomTicker):
            out2 = io.StringIO()
            with redirect_stdout(out2):
                r2 = cmc._fetch_hk_yfinance('^HSI', '恒生指数', retries=0)
        self.assertIsNone(r2)
        self.assertIn('恒生指数', out2.getvalue())      # 指标标识
        self.assertIn('OSError', out2.getvalue())      # 异常类型

    def test_t3e_valuation_per_index_failure_logs_code_and_type(self):
        pro = mock.MagicMock()

        def _by_code(ts_code=None, **kw):
            if ts_code == '000300.SH':
                raise RuntimeError('频率超限')
            return dailybasic_df([('20261104', 12.0)])
        pro.index_dailybasic.side_effect = lambda **kw: _by_code(**kw)
        with mock.patch.object(cmc, '_pro', return_value=pro):
            out = io.StringIO()
            with redirect_stdout(out):
                v = cmc.fetch_valuation()
        self.assertNotIn('000300.SH', v)
        self.assertIn('000905.SH', v)
        s = out.getvalue()
        self.assertIn('000300.SH', s)
        self.assertIn('RuntimeError', s)


class T4SourceFreezeLocks(unittest.TestCase):
    """回归锁: 本轮修复未削弱基点内 R007(61s 闸门)与 R049/R051(EM 回落)交付物。"""

    def test_t4a_a_share_indices_frozen(self):
        self.assertEqual(list(cmc.A_SHARE_INDICES),
                         ['000001.SH', '399001.SZ', '399006.SZ',
                          '000300.SH', '000905.SH', '000852.SH'])

    def test_t4b_throttle_gate_frozen(self):
        self.assertEqual(cmc.INDEX_DAILY_MIN_INTERVAL_SECONDS, 61)

    def test_t4c_em_map_still_covers_all(self):
        self.assertEqual(set(cmc.EM_MAP), set(cmc.A_SHARE_INDICES))


if __name__ == '__main__':
    unittest.main(verbosity=2)
