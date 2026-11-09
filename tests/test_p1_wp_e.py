# -*- coding: utf-8 -*-
"""IA-P1-WP-E 专项测试(v1.3 续作;CN 面备源切换与宏观接入的离线行为锁)。

任务: IA-P1-WP-E-AC-v1.3 §十三(M 面 (a)(b)(d)) | 基点: BASE-P1E=ee66f3a9(v1.3
同分支续笔,尖端见 REPORT §零.10)
被测对象: scripts/china_market_collector.py(G-P1-11 margin/valuation 备源+
G-P1-14..18 宏观采集的真实函数)与 config/metric_registry.json(v2.3.0,94→102)
——不复制被测算法。

数据纪律: 本文件全部为**离线合成 fixture 行为锁**,合成数值刻意构造(不代表
任何真实交易日行情/真实宏观观测);端点列名锚=akshare 1.18.47 安装包源码离线
实读(REPORT §零.6A),非网络获取。零网络: akshare 以 sys.modules 假模块注入
(逐端点 MagicMock,CI==本地行为一致;tushare 经 mock),零真实调用、零 skip、
零删除断言。预期值全部字面量硬编码(禁自证恒真);合成 fixture=唯一数据源
(R014-D3/R022: 不读 data/daily/ 真实档)。

锁清单:
T1 registry v2.3.0 域化锁(102/101/'2.3.0'/聚合 CN 18;CN8 尾序 append;
   CN_OMO_7D 全字段冻结[frequency='daily'=v1.3 裁决锚+PENDING 身份预注册];
   validate_registry 零问题+evolution_legal;CN 面分类独立重编码;registry↔
   collector 产出键 1:1 映射)
T2 G-P1-11 margin 备源(两所同日配对合计/schema 与主路 1:1+via 恰一新增键/
   次新日配对回落/单所空=无半合计/SSE 失败→None/主路失败→备源切换接线)
T3 G-P1-11 valuation 备源(乐咕完结行选择/在途行禁用/口径 note 披露/
   列漂移→None/主路全失败→扁平桥接键备源接线,嵌套对象不补造)
T4 G-P1-14..17 宏观采集(六端点正取: 七产出键恰等[值/日期/源标签硬编码];
   单端点失败独立容错;列漂移→键缺席不炸)
T5 纯解析函数(_norm_date 多形态/_norm_month/_macro_last 序向无关+NaN 跳行/
   _parse_omo_rows 7天过滤+利率解+去重+today 冻结/fetch_omo_7d 注入面)
T6 源端失败→诚实缺席(全端点失败→{} 零 0 填充;OMO 默认装载器 PENDING→None
   与 registry 身份预注册挂钩[JP_CPI_TOKYO_YOY 同型])

fixture→预期值映射(AC-03.6;逐断言组可追溯):
- sse_margin_df()/szse_margin_df() → T2 t20/t21/t23 恰等字典(两所同日合计算术)
- legu_pe_df() → T3 t30/t32 {'pe','date','via','note'} 恰等
- lpr_df()/jin10_df()/pmi_df()/shrzgm_df()/nfc_df() → T4 t40 七键恰等
- OMO_LINES → T5 t54/t55 解析/冻结/末行;T6 t61 PENDING 缺席
"""
import io
import json
import os
import sys
import types
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts'), os.path.dirname(os.path.abspath(__file__))):
    if p not in sys.path:
        sys.path.insert(0, p)

# CI 环境不装 akshare(离线套件零真实依赖,offline-tests.yml 安装面无 akshare):
# 无条件注入确定性 fake(真包在场也统一覆盖,CI==本地一致;W5-DATASRC-B 先例)。
_ak_fake = types.ModuleType('akshare')
for _fn in ('stock_margin_sse', 'stock_margin_szse', 'stock_market_pe_lg',
            'macro_china_lpr', 'macro_china_cpi_yearly', 'macro_china_ppi_yearly',
            'macro_china_pmi', 'macro_china_shrzgm',
            'macro_china_new_financial_credit'):
    setattr(_ak_fake, _fn, mock.MagicMock(name=_fn))
sys.modules['akshare'] = _ak_fake

import china_market_collector as cmc            # noqa: E402

from helpers import baseline_locks as bl        # noqa: E402
import registry_semantics as rsem               # noqa: E402

with open(os.path.join(ROOT, 'config', 'metric_registry.json'), encoding='utf-8') as _f:
    REG = json.load(_f)
METRICS = {m['metric_id']: m for m in REG['metrics']}

# IA-P1-WP-E v1.3(§十三.1/§十三.3): CN 宏观八条目(append 尾序=登记终值表序)
CN8_ORDER = ('CN_LPR_1Y', 'CN_LPR_5Y', 'CN_CPI_YOY', 'CN_PPI_YOY', 'CN_PMI_MFG',
             'CN_SF_FLOW', 'CN_NEW_LOANS', 'CN_OMO_7D')
CN8 = frozenset(CN8_ORDER)
JP4 = frozenset(('JP_POLICY_RATE', 'JGB2Y', 'JGB5Y', 'JGB10Y'))
NEW9 = frozenset(('JP_CPI_TOKYO_YOY', 'NIKKEI225', 'ECB_DFR', 'ECB_MRO',
                  'BUND_10Y', 'BUND_2Y', 'EA_HICP_YOY', 'DAX', 'CAC40'))

# collector 产出键 ↔ registry 条目 1:1(REPORT §零.6A/§零.12;硬编码映射表)
KEY_TO_METRIC = {
    'lpr_1y': 'CN_LPR_1Y', 'lpr_5y': 'CN_LPR_5Y', 'cpi_yoy': 'CN_CPI_YOY',
    'ppi_yoy': 'CN_PPI_YOY', 'pmi_mfg': 'CN_PMI_MFG', 'sf_flow': 'CN_SF_FLOW',
    'new_loans': 'CN_NEW_LOANS', 'omo_7d': 'CN_OMO_7D',
}

# 冻结时钟(被测模块内 datetime.now 同钟冻结;W5-EMWIN 先例): 2026-11-06 10:00
# HKT(盘中)→ _em_max_date()=2026-11-05,一切完结行选择与时钟无关。
_HKT = timezone(timedelta(hours=8))
FROZEN = datetime(2026, 11, 6, 10, 0, 0, tzinfo=_HKT)


def freeze_clock(moment=FROZEN):
    """monkeypatch cmc.datetime 为冻结子类(now/now(tz) 恒返同一时刻)。"""
    class _FrozenDT(datetime):
        @classmethod
        def now(cls, tz=None):
            return moment if tz is not None else moment.replace(tzinfo=None)
    return mock.patch.object(cmc, 'datetime', _FrozenDT)


def ak_returns(**endpoints):
    """逐端点打桩: 值=DataFrame→return_value;值=异常实例→side_effect。
    回收=各测试 addCleanup(mock.patch.stopall) 统一停用。"""
    for name, val in endpoints.items():
        if isinstance(val, BaseException):
            mock.patch('akshare.' + name, side_effect=val).start()
        else:
            mock.patch('akshare.' + name, return_value=val).start()


# ── 合成 fixture(值全发明;结构镜像端点真实列形态,akshare 1.18.47 源码锚) ──
def sse_margin_df(dates=('2026-11-05', '2026-11-04', '2026-11-03'),
                  rzye=None, rqye_amt=None):
    """上交所 stock_margin_sse 形状(元): 信用交易日期/融资余额/融券余量金额…(降序)。
    rzye/rqye_amt 缺省=逐日递减中性值(9.0e11-1.0e9·i / 3.0e10-1.0e8·i)。"""
    n = len(dates)
    rzye = list(rzye) if rzye is not None else [9.0e11 - 1.0e9 * i
                                                for i in range(n)]
    rqye_amt = list(rqye_amt) if rqye_amt is not None else [3.0e10 - 1.0e8 * i
                                                            for i in range(n)]
    return pd.DataFrame({
        '信用交易日期': list(dates),
        '融资余额': rzye,
        '融资买入额': [1.0e11] * n,
        '融券余量': [1.0e9] * n,
        '融券余量金额': rqye_amt,
        '融券卖出量': [1.0e8] * n,
        '融资融券余额': [rzye[i] + rqye_amt[i] for i in range(n)],
    })


def szse_margin_df(rzye=6.0e11, rqye=1.0e10):
    """深交所 stock_margin_szse(date) 形状(元;单日全市场一行)。"""
    return pd.DataFrame({
        '融资买入额': [4.0e11], '融资余额': [rzye], '融券卖出量': [5.0e8],
        '融券余量': [8.0e8], '融券余额': [rqye], '融资融券余额': [rzye + rqye],
    })


def legu_pe_df(dates=('2026-11-06', '2026-11-05', '2026-11-04'),
               pes=(14.60, 14.55, 14.50)):
    """乐咕 stock_market_pe_lg('上证') 形状: 日期/指数/平均市盈率(首行=在途行)。"""
    return pd.DataFrame({'日期': list(dates), '指数': ['上证'] * len(dates),
                         '平均市盈率': list(pes)})


def lpr_df():
    """东财 macro_china_lpr 形状: TRADE_DATE/LPR1Y/LPR5Y(乱序+最新行 NaN→跳行锁)。"""
    return pd.DataFrame({
        'TRADE_DATE': ['2026-10-20', '2026-10-19', '2026-09-20'],
        'LPR1Y': [float('nan'), 3.0, 3.1],
        'LPR5Y': [float('nan'), 3.5, 3.6],
        'RATE_1': [3.0, 3.0, 3.1], 'RATE_2': [3.5, 3.5, 3.6],
    })


def jin10_cpi_df():
    """金十 macro_china_cpi_yearly 形状: 商品/日期/今值/预测值/前值(乱序)。"""
    return pd.DataFrame({'商品': ['CPI'] * 3,
                         '日期': ['2026-09-10', '2026-10-10', '2026-08-09'],
                         '今值': [0.4, 0.5, 0.3], '预测值': [0.45, 0.48, 0.32],
                         '前值': [0.3, 0.4, 0.2]})


def jin10_ppi_df():
    return pd.DataFrame({'商品': ['PPI'] * 2,
                         '日期': ['2026-09-10', '2026-10-10'],
                         '今值': [-2.3, -2.1], '预测值': [-2.2, -2.0],
                         '前值': [-2.4, -2.3]})


def pmi_df():
    """东财 macro_china_pmi 形状: 月份(中文)/制造业-指数…(乱序)。"""
    return pd.DataFrame({'月份': ['2026年9月', '2026年10月', '2026年8月'],
                         '制造业-指数': [49.7, 50.1, 49.2],
                         '制造业-同比增长': [0.0] * 3,
                         '非制造业-指数': [51.0, 50.8, 51.2],
                         '非制造业-同比增长': [0.0] * 3})


def shrzgm_df():
    return pd.DataFrame({'月份': ['2026年9月', '2026年8月', '2026年10月'],
                         '社会融资规模增量': [30000.0, 25000.0, 22000.0],
                         '其中-人民币贷款': [8000.0, 7000.0, 8000.0]})


def nfc_df():
    return pd.DataFrame({'月份': ['2026年10月', '2026年9月'],
                         '当月': [8000.0, 9000.0], '当月-同比增长': [0.0] * 2,
                         '当月-环比增长': [0.0] * 2, '累计': [81000.0, 73000.0],
                         '累计-同比增长': [0.0] * 2})


OMO_LINES = [
    '中国人民银行2026年11月5日公告: 以利率招标方式开展了300亿元7天期逆回购操作,中标利率1.5',
    '中国人民银行2026年11月4日公告: 以利率招标方式开展了500亿元7天期逆回购操作,中标利率1.5',
    '中国人民银行2026年11月4日公告: 以利率招标方式开展了200亿元14天期逆回购操作,中标利率1.6',
    '中国人民银行2026年11月3日公告: 以利率招标方式开展了100亿元7天期逆回购操作,利率未披露',
    '中国人民银行2026年11月6日公告: 以利率招标方式开展了400亿元7天期逆回购操作,中标利率为1.45%',
]


# ══ T1 registry v2.3.0 域化锁 ═══════════════════════════════════════════
class T1RegistryV230(unittest.TestCase):

    def test_t01_counts_version_aggregate(self):
        # IA-P1-WP-E v1.3 域化(§十三.1): 94+8→102/93+8→101/2.2.0→2.3.0/CN 10→18
        self.assertEqual(len(REG['metrics']), 102)
        self.assertEqual(REG['version'], '2.4.0')  # A-fin(2026-11-09) 时间键登记 2.3.0→2.4.0
        self.assertEqual(sum(1 for m in REG['metrics']
                             if m.get('status') == 'active'), 101)
        agg = {}
        for m in REG['metrics']:
            agg[m['economy']] = agg.get(m['economy'], 0) + 1
        self.assertEqual(agg, {'US': 49, 'CN': 18, 'HK': 4, 'JP': 8,
                               'EA': 11, 'GLOBAL': 12})

    def test_t02_cn8_tail_order_and_common_fields(self):
        self.assertEqual(tuple(m['metric_id'] for m in REG['metrics'][-8:]),
                         CN8_ORDER)                       # append 尾序=终值表序
        for mid in CN8_ORDER:
            m = METRICS[mid]
            self.assertEqual(m['source'], 'china_market_collector', mid)
            self.assertEqual(m['calendar'], 'cn', mid)
            self.assertEqual(m['economy'], 'CN', mid)
            self.assertEqual(m['economy_rule'], 'P1:calendar=cn', mid)
            self.assertEqual(m['market_seat'], 'onshore_local', mid)
            self.assertEqual(m['status'], 'active', mid)
            self.assertEqual(m['criticality'], 'important', mid)  # 非 core,分级不动
            self.assertEqual(m['value_type'], 'level', mid)

    def test_t03_omo_entry_full_field_freeze(self):
        # D11 全字段冻结(硬编码=磁盘实况);frequency='daily'=v1.3 处置章 §十三.2
        # 裁决锚;source_symbol='PENDING'=身份预注册(JP_CPI_TOKYO_YOY 先例形态)
        self.assertEqual(METRICS['CN_OMO_7D'], {
            'metric_id': 'CN_OMO_7D',
            'display_name': '央行7天期逆回购利率',
            'source': 'china_market_collector',
            'source_symbol': 'PENDING',
            'asset_class': 'policy_rate',
            'frequency': 'daily',
            'observation_period_kind': 'calendar_day',
            'release_date_available': True,
            'unit': 'percent',
            'calendar': 'cn',
            'economy': 'CN',
            'economy_rule': 'P1:calendar=cn',
            'market_seat': 'onshore_local',
            'criticality': 'important',
            'status': 'active',
            'identity': {'instrument': 'macro_series', 'adjustment': 'none'},
            'value_type': 'level',
            'calc': ('人民银行公开市场业务交易公告 7 天期逆回购中标利率(操作利率,'
                     '有效利率口径);akshare 1.18.47 无逆回购接口→条目=身份预注册,'
                     '公告行解析函数已随包交付(可注入纯函数),源接线=PENDING'),
            'validation': {'range': [0.5, 5], 'max_week_abs_move': 1.0},
            'freshness': {'max_calendar_lag_days': 10},
            'release_semantics': ("央行操作室每交易日 09:20 前后披露交易公告(决议日"
                                  "不定期);frequency='daily'=IA-P1-WP-E v1.3 裁决"
                                  '(有效利率形态,ECB_DFR 先例),决议日语义由本注记'
                                  '承载、不扩 FREQUENCY_VALUES;源未接线,数据缺席按'
                                  ' L58 纪律处理'),
        })

    def test_t04_semantics_evolution_vintage(self):
        self.assertEqual(rsem.validate_registry(REG), [])   # 零 error 零 review
        ok, why = bl.evolution_legal()
        self.assertTrue(ok, why)
        self.assertEqual(bl.vintage_additions(), JP4 | NEW9 | CN8)  # 21=4+9+8
        self.assertEqual(bl.BASELINE_VINTAGE_IDS & CN8, set())      # 不与冻结81撞名

    def test_t05_cn_classification_reencode(self):
        # t1b 独立重编码的 CN 面(P1 首中→CN;非 etf/商品/fx 族→onshore_local)
        for mid in CN8_ORDER:
            m = METRICS[mid]
            eco = 'CN' if m['calendar'] == 'cn' else None
            self.assertEqual(eco, m['economy'], mid)
            self.assertTrue(m['economy_rule'].startswith('P1:'), mid)
            self.assertEqual(m['market_seat'], 'onshore_local', mid)

    def test_t06_registry_collector_key_mapping(self):
        # registry 条目 ↔ collector 产出键 1:1(§十三.3);源符号端点段∈被调端点集
        self.assertEqual(set(KEY_TO_METRIC), set(CN8_ORDER) and
                         {'lpr_1y', 'lpr_5y', 'cpi_yoy', 'ppi_yoy', 'pmi_mfg',
                          'sf_flow', 'new_loans', 'omo_7d'})
        self.assertEqual(set(KEY_TO_METRIC.values()), set(CN8))
        endpoints_called = {fn for fn in dir(_ak_fake)
                            if not fn.startswith('_')}
        for mid in CN8_ORDER:
            sym = METRICS[mid]['source_symbol']
            if sym == 'PENDING':
                self.assertEqual(mid, 'CN_OMO_7D')       # 唯一身份预注册
                continue
            self.assertIn(sym.split('.')[0], endpoints_called, mid)  # 端点接线一致
        # identity 分型: flow 两条无 identity(SB_FLOW 先例),宏观六条 macro_series
        for mid in ('CN_SF_FLOW', 'CN_NEW_LOANS'):
            self.assertNotIn('identity', METRICS[mid], mid)
        for mid in set(CN8_ORDER) - {'CN_SF_FLOW', 'CN_NEW_LOANS'}:
            self.assertEqual(METRICS[mid]['identity'],
                             {'instrument': 'macro_series', 'adjustment': 'none'}, mid)


# ══ T2 G-P1-11 margin 备源 ══════════════════════════════════════════════
class T2MarginBackup(unittest.TestCase):

    def test_t20_same_date_pairing_aggregate(self):
        # 两所同日合计: rzye=9.0e11+6.0e11/rqye=3.0e10+1.0e10;schema 与主路 1:1+via
        self.addCleanup(mock.patch.stopall)
        ak_returns(stock_margin_sse=sse_margin_df(),
                   stock_margin_szse=szse_margin_df())
        with freeze_clock():
            out = io.StringIO()
            with redirect_stdout(out):
                res = cmc._fetch_margin_em()
        self.assertEqual(res, {'date': '20261105', 'rzye': 1.5e12,
                               'rqye': 4.0e10, 'rzye_billion': 15000.0,
                               'balance': 15400.0, 'via': 'akshare_em'})

    def test_t21_fallback_to_older_common_date(self):
        # 最新日深交所空(未出数)→次新共同日配对(不以单所半合计冒充)
        self.addCleanup(mock.patch.stopall)
        szse = mock.MagicMock(name='stock_margin_szse')
        szse.side_effect = [pd.DataFrame(), szse_margin_df()]
        mock.patch('akshare.stock_margin_sse',
                   return_value=sse_margin_df(('2026-11-05', '2026-11-04'))).start()
        mock.patch('akshare.stock_margin_szse', szse).start()
        with freeze_clock():
            out = io.StringIO()
            with redirect_stdout(out):
                res = cmc._fetch_margin_em()
        self.assertEqual(res, {'date': '20261104', 'rzye': 1.499e12,
                               'rqye': 3.99e10, 'rzye_billion': 14990.0,
                               'balance': 15389.0, 'via': 'akshare_em'})

    def test_t22a_sse_failure_none(self):
        self.addCleanup(mock.patch.stopall)
        ak_returns(stock_margin_sse=OSError('synthetic net down'))
        with freeze_clock():
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertIsNone(cmc._fetch_margin_em())

    def test_t22b_no_common_date_none(self):
        # 深交所逐候选日全空→无两所同日配对→None(数据不足不填0)
        self.addCleanup(mock.patch.stopall)
        ak_returns(stock_margin_sse=sse_margin_df(('2026-11-05',)),
                   stock_margin_szse=pd.DataFrame())
        with freeze_clock():
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertIsNone(cmc._fetch_margin_em())

    def test_t23_main_path_failure_switches_to_backup(self):
        # 主路(tushare margin)逐日全失败→备源切换接线(要点①断点修复面)
        self.addCleanup(mock.patch.stopall)
        ak_returns(stock_margin_sse=sse_margin_df(),
                   stock_margin_szse=szse_margin_df())
        pro = mock.MagicMock(name='pro')
        pro.margin.side_effect = OSError('synthetic tushare quota')
        with mock.patch.object(cmc, '_pro', return_value=pro):
            with freeze_clock():
                out = io.StringIO()
                with redirect_stdout(out):
                    res = cmc.fetch_margin()
        self.assertEqual(res['via'], 'akshare_em')
        self.assertEqual(res['balance'], 15400.0)
        self.assertEqual(res['date'], '20261105')


# ══ T3 G-P1-11 valuation 备源 ═══════════════════════════════════════════
class T3ValuationBackup(unittest.TestCase):

    def test_t30_legu_settled_row_and_scope(self):
        # 完结行=date≤2026-11-05(在途 11-06 禁用);范围仅扁平桥接键+口径 note
        self.addCleanup(mock.patch.stopall)
        ak_returns(stock_market_pe_lg=legu_pe_df())
        with freeze_clock():
            out = io.StringIO()
            with redirect_stdout(out):
                res = cmc._fetch_valuation_em()
        self.assertEqual(res['pe'], 14.55)
        self.assertEqual(res['date'], '20261105')
        self.assertEqual(res['via'], 'akshare_legu')
        self.assertIn('乐咕', res['note'])            # 口径差异如实披露
        self.assertIn('近似', res['note'])

    def test_t31_column_drift_none(self):
        # 列漂移(无平均市盈率列)/空表→None(如实缺席)
        self.addCleanup(mock.patch.stopall)
        ak_returns(stock_market_pe_lg=pd.DataFrame({'日期': [], '指数': []}))
        with freeze_clock():
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertIsNone(cmc._fetch_valuation_em())
        ak_returns(stock_market_pe_lg=legu_pe_df(
            ('2026-11-05',), (14.55,)).drop(columns=['平均市盈率']))
        with freeze_clock():
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertIsNone(cmc._fetch_valuation_em())

    def test_t32_main_path_failure_flat_bridge_fallback(self):
        # 主路 index_dailybasic 全失败→扁平桥接键备源;嵌套 per-index 对象不补造
        self.addCleanup(mock.patch.stopall)
        ak_returns(stock_market_pe_lg=legu_pe_df())
        pro = mock.MagicMock(name='pro')
        pro.index_dailybasic.side_effect = OSError('synthetic tushare down')
        with mock.patch.object(cmc, '_pro', return_value=pro):
            with freeze_clock():
                out = io.StringIO()
                with redirect_stdout(out):
                    res = cmc.fetch_valuation()
        self.assertEqual(set(res), {'pe', 'date', 'via', 'note'})
        self.assertEqual(res['pe'], 14.55)
        self.assertEqual(res['date'], '20261105')


# ══ T4 G-P1-14..17 宏观采集(六端点) ═════════════════════════════════════
class T4MacroEndpoints(unittest.TestCase):

    def _run_fetch_macro(self):
        out = io.StringIO()
        with redirect_stdout(out):
            return cmc.fetch_macro()

    def test_t40_all_endpoints_positive(self):
        # 七产出键恰等(值/日期/源标签全硬编码);omo_7d=默认装载器 PENDING→缺席
        self.addCleanup(mock.patch.stopall)
        ak_returns(macro_china_lpr=lpr_df(),
                   macro_china_cpi_yearly=jin10_cpi_df(),
                   macro_china_ppi_yearly=jin10_ppi_df(),
                   macro_china_pmi=pmi_df(),
                   macro_china_shrzgm=shrzgm_df(),
                   macro_china_new_financial_credit=nfc_df())
        with freeze_clock():
            out = self._run_fetch_macro()
        self.assertEqual(set(out), {'lpr_1y', 'lpr_5y', 'cpi_yoy', 'ppi_yoy',
                                    'pmi_mfg', 'sf_flow', 'new_loans'})
        self.assertEqual(out['lpr_1y'], {'date': '2026-10-19', 'value': 3.0,
                                         'source': 'akshare_em'})   # NaN 最新行跳过
        self.assertEqual(out['lpr_5y'], {'date': '2026-10-19', 'value': 3.5,
                                         'source': 'akshare_em'})
        self.assertEqual(out['cpi_yoy'], {'date': '2026-10-10', 'value': 0.5,
                                          'source': 'akshare_jin10'})
        self.assertEqual(out['ppi_yoy'], {'date': '2026-10-10', 'value': -2.1,
                                          'source': 'akshare_jin10'})
        self.assertEqual(out['pmi_mfg'], {'date': '2026-10', 'value': 50.1,
                                          'source': 'akshare_em'})
        self.assertEqual(out['sf_flow'], {'date': '2026-10', 'value': 22000.0,
                                          'source': 'akshare_mofcom'})
        self.assertEqual(out['new_loans'], {'date': '2026-10', 'value': 8000.0,
                                            'source': 'akshare_em'})

    def test_t41_single_endpoint_failure_independent(self):
        # 单端点失败仅该键缺席,其余六键不受影响(§三(c) L81 独立容错)
        self.addCleanup(mock.patch.stopall)
        ak_returns(macro_china_lpr=lpr_df(),
                   macro_china_cpi_yearly=OSError('synthetic rate-limit'),
                   macro_china_ppi_yearly=jin10_ppi_df(),
                   macro_china_pmi=pmi_df(),
                   macro_china_shrzgm=shrzgm_df(),
                   macro_china_new_financial_credit=nfc_df())
        with freeze_clock():
            out = self._run_fetch_macro()
        self.assertNotIn('cpi_yoy', out)
        self.assertEqual(set(out) - {'cpi_yoy'},
                         {'lpr_1y', 'lpr_5y', 'ppi_yoy', 'pmi_mfg', 'sf_flow',
                          'new_loans'})

    def test_t42_column_drift_key_absent(self):
        # 列漂移(金十表无今值列)→该键缺席不炸(端点列锚漂移=如实缺席)
        self.addCleanup(mock.patch.stopall)
        drift = jin10_cpi_df().drop(columns=['今值'])
        ak_returns(macro_china_lpr=lpr_df(), macro_china_cpi_yearly=drift,
                   macro_china_ppi_yearly=jin10_ppi_df(), macro_china_pmi=pmi_df(),
                   macro_china_shrzgm=shrzgm_df(),
                   macro_china_new_financial_credit=nfc_df())
        with freeze_clock():
            out = self._run_fetch_macro()
        self.assertNotIn('cpi_yoy', out)
        self.assertEqual(out['ppi_yoy']['value'], -2.1)


# ══ T5 纯解析函数 ════════════════════════════════════════════════════════
class T5PureParsers(unittest.TestCase):

    def test_t50_norm_date_forms(self):
        self.assertEqual(cmc._norm_date('2026-10-10'), '2026-10-10')
        self.assertEqual(cmc._norm_date('2026/10/8'), '2026-10-08')
        self.assertEqual(cmc._norm_date('2026年10月10日'), '2026-10-10')
        self.assertEqual(cmc._norm_date('2026年10月'), '2026-10')     # 月粒度
        self.assertEqual(cmc._norm_date('2026-10'), '2026-10')
        self.assertIsNone(cmc._norm_date('不解析行'))
        self.assertIsNone(cmc._norm_date(None))

    def test_t51_norm_month_forms(self):
        self.assertEqual(cmc._norm_month('2026年10月'), '2026-10')
        self.assertEqual(cmc._norm_month('2026年1月'), '2026-01')     # 补零
        self.assertIsNone(cmc._norm_month('2026-10'))                 # 须中文月份形态
        self.assertIsNone(cmc._norm_month('N/A'))

    def test_t52_macro_last_order_independent(self):
        # 乱序+NaN 值行+不可数值化行→取最大有值归一日期(端点返回序向不依赖)
        df = pd.DataFrame({'TRADE_DATE': ['2026-10-01', '2026-11-01', '2026-09-01',
                                          '2026-12-01'],
                           'V': ['x', float('nan'), 3.0, 4.0]})
        self.assertEqual(cmc._macro_last(df, 'TRADE_DATE', 'V'),
                         ('2026-12-01', 4.0))
        self.assertIsNone(cmc._macro_last(pd.DataFrame(), 'TRADE_DATE', 'V'))
        self.assertIsNone(cmc._macro_last(df, '缺席列', 'V'))

    def test_t53_macro_last_month(self):
        df = pd.DataFrame({'月份': ['2026年9月', '2026年10月'], 'V': [1.0, 2.0]})
        self.assertEqual(cmc._macro_last_month(df, '月份', 'V'), ('2026-10', 2.0))
        self.assertIsNone(cmc._macro_last_month(df, '月份', '缺席'))

    def test_t54_parse_omo_rows(self):
        # 7天过滤(14天行剔)/无中标利率行剔/同日去重/升序;today 冻结剔未来行
        got = cmc._parse_omo_rows(OMO_LINES)
        self.assertEqual(got, [('2026-11-04', 1.5), ('2026-11-05', 1.5),
                               ('2026-11-06', 1.45)])   # '为1.45%' 形态可解
        self.assertEqual(cmc._parse_omo_rows(OMO_LINES, today='2026-11-05'),
                         [('2026-11-04', 1.5), ('2026-11-05', 1.5)])
        self.assertEqual(cmc._parse_omo_rows(OMO_LINES, today='2026-11-04'),
                         [('2026-11-04', 1.5)])
        self.assertEqual(cmc._parse_omo_rows([]), [])
        self.assertEqual(cmc._parse_omo_rows(['无关公告行']), [])

    def test_t55_fetch_omo_7d_injected(self):
        # 注入面: 无 today→末行(11-06/1.45);冻结 today→11-05/1.5;源标签 pboc_omo
        self.assertEqual(cmc.fetch_omo_7d(rows=OMO_LINES),
                         {'date': '2026-11-06', 'value': 1.45,
                          'source': 'pboc_omo'})
        self.assertEqual(cmc.fetch_omo_7d(rows=OMO_LINES, today='2026-11-05'),
                         {'date': '2026-11-05', 'value': 1.5,
                          'source': 'pboc_omo'})
        self.assertIsNone(cmc.fetch_omo_7d(rows=['无关公告行']))


# ══ T6 源端失败→诚实缺席(DESIGN 要点② 注入面) ═══════════════════════════
class T6SourceFailureHonestAbsence(unittest.TestCase):

    def test_t60_all_endpoints_fail_empty_dict(self):
        # 全端点失败→{}(逐键缺席,零 0 填充,无异常上抛)
        self.addCleanup(mock.patch.stopall)
        ak_returns(macro_china_lpr=OSError('synthetic down'),
                   macro_china_cpi_yearly=OSError('synthetic down'),
                   macro_china_ppi_yearly=OSError('synthetic down'),
                   macro_china_pmi=OSError('synthetic down'),
                   macro_china_shrzgm=OSError('synthetic down'),
                   macro_china_new_financial_credit=OSError('synthetic down'))
        with freeze_clock():
            out = io.StringIO()
            with redirect_stdout(out):
                res = cmc.fetch_macro()
        self.assertEqual(res, {})
        self.assertIn('PENDING', out.getvalue())        # OMO 缺席有披露

    def test_t61_omo_default_loader_pending_none(self):
        # 默认装载器=PENDING 披露返回 None(零网络零造数);与 registry 身份预注册
        # (CN_OMO_7D active+source_symbol='PENDING')挂钩=JP_CPI_TOKYO_YOY 同型
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertIsNone(cmc._omo_rows_default())
            self.assertIsNone(cmc.fetch_omo_7d())
        self.assertIn('PENDING', out.getvalue())
        self.assertEqual(METRICS['CN_OMO_7D']['source_symbol'], 'PENDING')
        self.assertEqual(METRICS['CN_OMO_7D']['status'], 'active')
        self.assertEqual(METRICS['JP_CPI_TOKYO_YOY']['source_symbol'], 'PENDING')


if __name__ == '__main__':
    unittest.main(verbosity=2)
