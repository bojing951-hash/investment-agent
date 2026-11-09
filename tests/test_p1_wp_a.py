#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P1-WP-A v1.3 验收件(实现轮): DESIGN §六 L169 验收要点①③。

要点① registry economy 字段与 P1-P8(v1.3 域=P1-P10)规则一致性逐条断言
  + 负向(规则未命中条目拒入)——规则表自 INVENTORY a.3 L39-47 逐字独立重编码
  于本文件(硬编码期望,禁自证: 不 import 实现侧脚本的计算结果);
要点③ 新采集器离线测试(源失败→MISSING/READ_FAIL 不填0)——raw 注入/零网络。

数据纪律: 全部合成 fixture 值发明并显式标注,不冒充真实;真实档面=步骤⑪
真实采集(白名单域),不在本文件冒充。定值源=docs/P1_WP_A_REPORT.md §零.12。
"""
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import ea_market_collector as ea      # noqa: E402
import historical_coverage_audit as hca  # noqa: E402
import jp_market_collector as jp      # noqa: E402
import registry_semantics as rsem     # noqa: E402
import research_provenance as rp      # noqa: E402
import trading_calendar as tc         # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixt                                          # noqa: E402
from helpers import baseline_locks as bl             # noqa: E402

with open(os.path.join(ROOT, 'config', 'metric_registry.json'), encoding='utf-8') as _f:
    REG = json.load(_f)
METRICS = {m['metric_id']: m for m in REG['metrics']}
NEW9 = ('JP_CPI_TOKYO_YOY', 'NIKKEI225', 'ECB_DFR', 'ECB_MRO', 'BUND_10Y',
        'BUND_2Y', 'EA_HICP_YOY', 'DAX', 'CAC40')
# IA-P1-WP-E v1.3(§十三.1 从属锁域化迁移): CN 宏观八条目(G-P1-14..18,
# P1_REPORT WP-E §零.6A 终值表;append 于 metrics 数组尾)
CN8 = ('CN_LPR_1Y', 'CN_LPR_5Y', 'CN_CPI_YOY', 'CN_PPI_YOY', 'CN_PMI_MFG',
       'CN_SF_FLOW', 'CN_NEW_LOANS', 'CN_OMO_7D')

# ══ 要点①: P1-P10 规则表(INVENTORY a.3 L39-47 逐字独立重编码+P9/P10)════
def classify(m):
    """按序首中即定;返回 (economy, 规则序号) 或 (None, None)=未归类拒入。"""
    cal, ac = m.get('calendar'), m.get('asset_class')
    sym = m.get('source_symbol') or ''
    if cal == 'cn':                                   # P1
        return 'CN', 'P1'
    if cal == 'hk':                                   # P2
        return 'HK', 'P2'
    if cal == 'us_rates':                             # P3
        return 'US', 'P3'
    if ac == 'fed_futures':                           # P4(先于P7)
        return 'US', 'P4'
    if cal == 'fx':                                   # P5 按非美元腿
        if sym == 'JPY=X':
            return 'JP', 'P5'
        if sym == 'CNY=X':
            return 'CN', 'P5'
        if sym == 'EURUSD=X':
            return 'EA', 'P5'
        return 'GLOBAL', 'P5'
    if ac == 'country_etf_proxy':                     # P6 按代理目标
        if sym == 'EWJ':
            return 'JP', 'P6'
        if sym in ('EZU', 'FEZ', 'EWG'):
            return 'EA', 'P6'
        if sym == 'FXI':
            return 'CN', 'P6'
        return 'GLOBAL', 'P6'
    if cal in ('commodity', 'crypto') or ac in ('spot_commodity_etf',
                                                'commodity_futures_etf'):  # P7
        return 'GLOBAL', 'P7'
    if cal == 'us_equity':                            # P8(R2 操作读法)
        return 'US', 'P8'
    if cal == 'japan':                                # P9(v1.3 补读)
        return 'JP', 'P9'
    if cal == 'ea':                                   # P10(v1.3 补读)
        return 'EA', 'P10'
    return None, None


def seat(m):
    """S1-S4(REPORT §零.12②): S1 etf代理→offshore;S2 商品/加密/Fed期货/
    fx族→global;其余→onshore_local。"""
    cal, ac = m.get('calendar'), m.get('asset_class')
    if ac == 'country_etf_proxy':
        return 'offshore_proxy'
    if cal in ('commodity', 'crypto', 'fx') or ac in ('fed_futures', 'fx_rate',
                                                      'fx_index'):
        return 'global'
    return 'onshore_local'


# ══ 合成 fixture(值全发明;结构镜像源端真实形态)═════════════════════════
SYN_MOF = (
    '2026年11月 中途経過\r\n'
    'Date,1Y,2Y,3Y,4Y,5Y,10Y,20Y,30Y,40Y\r\n'
    '2026/11/2,0.49,1.870,1.980,2.090,2.240,2.830,3.09,3.19,3.29\r\n'
    '2026/11/4,0.51,1.891,2.000,2.110,2.269,2.855,3.11,3.21,3.31\r\n'
    '※末尾コメント行\r\n'
).encode('shift_jis')
SYN_FRED_POLICY = (
    'observation_date,IRSTCI01JPM156N\r\n'
    '2026-07-01,0.860\r\n'
    '2026-08-01,.\r\n'
    '2026-09-01,0.743\r\n'
).encode('utf-8')
SYN_FRED_NIKKEI = (
    'observation_date,NIKKEI225\r\n'
    '2026-10-30,38250.0\r\n'
    '2026-11-02,38100.5\r\n'
    '2026-11-04,38000.25\r\n'
).encode('utf-8')
SYN_ECB_DFR = (
    'KEY,FREQ,TIME_PERIOD,OBS_VALUE\r\n'
    'FM.B.U2.EUR.4F.KR.DFR.LEV,D,2026-11-02,2.00\r\n'
    'FM.B.U2.EUR.4F.KR.DFR.LEV,D,2026-11-03,\r\n'
    'FM.B.U2.EUR.4F.KR.DFR.LEV,D,2026-11-04,2.00\r\n'
).encode('utf-8')
SYN_ECB_MRO = (
    'KEY,FREQ,TIME_PERIOD,OBS_VALUE\r\n'
    'FM.B.U2.EUR.4F.KR.MRR_FR.LEV,D,2026-11-03,3.15\r\n'
    'FM.B.U2.EUR.4F.KR.MRR_FR.LEV,D,2026-11-04,3.15\r\n'
).encode('utf-8')
SYN_ECB_HICP = (
    'KEY,FREQ,TIME_PERIOD,OBS_VALUE\r\n'
    'ICP.M.U2.N.000000.4.ANR,M,2026-08,2.4\r\n'
    'ICP.M.U2.N.000000.4.ANR,M,2026-09,2.2\r\n'
).encode('utf-8')
SYN_BBK10 = (
    'TIME_PERIOD,OBS_VALUE\r\n2026-11-03,2.62\r\n2026-11-04,2.60\r\n'
).encode('utf-8')
SYN_BBK2 = (
    'TIME_PERIOD,OBS_VALUE\r\n2026-11-03,2.35\r\n2026-11-04,2.30\r\n'
).encode('utf-8')
SYN_BBK_META_OK_10 = ('{"title":"Wertpapierrenditen mit einer '
                      'Restlaufzeit von 9 bis 10 Jahren"}').encode('utf-8')
SYN_BBK_META_OK_2 = ('{"title":"Wertpapierrenditen mit einer '
                     'Restlaufzeit von 1 bis 2 Jahren"}').encode('utf-8')
SYN_BBK_META_BAD = ('{"title":"Wertpapierrenditen mit einer '
                    'Restlaufzeit von 5 bis 10 Jahren"}').encode('utf-8')
SYN_BAD = b'not-a-valid-csv'


# ══ T1 要点①: economy 规则一致性(逐条)+聚合+负向 ═══════════════════════
class TestEconomyRules(unittest.TestCase):
    """验收要点①: registry economy/economy_rule/market_seat 与 P1-P10+S1-S4
    独立重编码逐条一致;负向=规则未命中条目 classify→None(拒入)。"""

    def test_t1a_counts_version_aggregate(self):
        # IA-P1-WP-E v1.3 域化(§十三.1 从属锁迁移,同型不弱化):
        # 94+8→102 / 93+8→101 / 2.2.0→2.3.0 / 聚合 CN 10→18(其余键不动)
        self.assertEqual(len(REG['metrics']), 106)  # Charter6-P2: +SPX_CAPE/SPX_PE_TTM/SPX_PB
        self.assertEqual(REG['version'], '2.6.0')  # Charter6-P2(2026-11-09) 估值面 2.5.0→2.6.0
        self.assertEqual(sum(1 for m in REG['metrics']
                             if m.get('status') == 'active'), 104)  # Charter6-P2: +SPX_CAPE/SPX_PE_TTM
        agg = {}
        for m in REG['metrics']:
            agg[m['economy']] = agg.get(m['economy'], 0) + 1
        # 定值=REPORT §零.12⑥(85 实测聚合+P9×2+P10×7)+CN 宏观八条目(P1:calendar=cn)
        # Charter6-P2: US 50→52(+SPX_CAPE/SPX_PE_TTM;SPX_PB=unavailable不计)
        self.assertEqual(agg, {'US': 53, 'CN': 18, 'HK': 4, 'JP': 8,
                               'EA': 11, 'GLOBAL': 12})

    def test_t1b_per_entry_rule_consistency(self):
        """逐条断言: economy==classify 结果且 economy_rule 前缀==命中规则序。"""
        checked = set()
        for m in REG['metrics']:
            eco, p = classify(m)
            self.assertIsNotNone(eco, f"规则未命中但已入表: {m['metric_id']}")
            self.assertEqual(m['economy'], eco, m['metric_id'])
            self.assertTrue(m['economy_rule'].startswith(p + ':'),
                            f"{m['metric_id']}: {m['economy_rule']} !~ {p}")
            self.assertEqual(m['market_seat'], seat(m), m['metric_id'])
            self.assertIn(m['economy'], ('US', 'CN', 'JP', 'EA', 'HK', 'GLOBAL'))
            self.assertIn(m['market_seat'],
                         ('onshore_local', 'offshore_proxy', 'global'))
            checked.add(p)
        self.assertEqual(checked, {'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7',
                                   'P8', 'P9', 'P10'},
                         '全规则面(P1-P10)逐条覆盖自检')

    def test_t1c_spot_checks(self):
        """代表性条目硬编码期望(INVENTORY b.2 行级权威+P9/P10)。"""
        for mid, eco, p in (('SPX', 'US', 'P8'), ('UST_10Y', 'US', 'P3'),
                            ('SHCOMP', 'CN', 'P1'), ('HSI', 'HK', 'P2'),
                            ('USDJPY', 'JP', 'P5'), ('EURUSD', 'EA', 'P5'),
                            ('USDCNY', 'CN', 'P5'), ('DXY', 'GLOBAL', 'P5'),
                            ('EWJ', 'JP', 'P6'), ('EZU', 'EA', 'P6'),
                            ('FXI', 'CN', 'P6'), ('EEM', 'GLOBAL', 'P6'),
                            ('BTC', 'GLOBAL', 'P7'), ('WTI_F', 'GLOBAL', 'P7'),
                            ('ZQ_F1_PRICE', 'US', 'P4'),
                            ('JP_POLICY_RATE', 'JP', 'P9'),
                            ('NIKKEI225', 'JP', 'P9'),
                            ('ECB_DFR', 'EA', 'P10'),
                            ('EA_HICP_YOY', 'EA', 'P10')):
            self.assertEqual(METRICS[mid]['economy'], eco, mid)
            self.assertTrue(METRICS[mid]['economy_rule'].startswith(p + ':'),
                            mid)
        self.assertEqual(METRICS['EWJ']['market_seat'], 'offshore_proxy')
        self.assertEqual(METRICS['SHCOMP']['market_seat'], 'onshore_local')
        self.assertEqual(METRICS['GOLD_F']['market_seat'], 'global')
        self.assertEqual(METRICS['USDJPY']['market_seat'], 'global')

    def test_t1d_negative_unclassified_rejected(self):
        """负向: 规则未命中(日历/资产类均无规则可依)→classify=None 拒入,
        待人工裁决——不入表不默认归属(禁'其余→US'兜底吃掉未登记日历)。"""
        for fake in (
                {'calendar': 'mars_equity', 'asset_class': 'equity_index',
                 'source_symbol': 'X'},
                {'calendar': 'sg', 'asset_class': 'warp_drive',
                 'source_symbol': 'X'},      # 非四经济体日历且无特殊资产类
                {'calendar': None, 'asset_class': None,
                 'source_symbol': None},
        ):
            eco, p = classify(fake)
            self.assertIsNone(eco, fake)
            self.assertIsNone(p, fake)
        # 且现役注册表零未归类(与 t1b 呼应的独立计数式复核)
        n_unclassified = sum(1 for m in REG['metrics']
                             if classify(m)[0] is None)
        self.assertEqual(n_unclassified, 0)

    def test_t1e_twelve_candidate_disposition(self):
        """12 候选落点(§零.12④): 复用3(禁同概念双注册)+新注册9 append 尾。"""
        self.assertNotIn('BOJ_POLICY_RATE', METRICS)          # ≡JP_POLICY_RATE
        self.assertNotIn('JGB_10Y', METRICS)                  # →JGB10Y
        self.assertNotIn('JGB_2Y', METRICS)                   # →JGB2Y
        # IA-P1-WP-E v1.3 域化(§十三.1 同族同型迁移,第10断言位·如实登记见
        # WP-E REPORT §零.13): CN 宏观八条目 append 于数组尾→NEW9 尾块前移,
        # 块内连续性与序仍锁([-17:-8]);CN8 尾序新锁([-8:],锁面净增强)。
        self.assertEqual(tuple(m['metric_id'] for m in REG['metrics'][-17:-8]),
                         NEW9)                                # append 尾序(WP-A 时点)
        self.assertEqual(tuple(m['metric_id'] for m in REG['metrics'][-8:]),
                         CN8)                                 # append 尾序(WP-E)
        self.assertEqual(METRICS['JP_POLICY_RATE']['source_symbol'],
                         'IRSTCI01JPM156N')                   # 复用概念同源
        for mid in NEW9:
            self.assertIn(METRICS[mid]['source'],
                          ('jp_market_collector', 'ea_market_collector'))
            self.assertEqual(METRICS[mid]['status'], 'active')

    def test_t1f_field_semantics_documents_economy(self):
        for k in ('economy', 'economy_rule', 'market_seat'):
            self.assertIn(k, REG['field_semantics'])


# ══ T2 通道登记链+运行态锁(v1.2 轮 §零.8 全修复面自检)══════════════════
class TestChannelRegistrationChain(unittest.TestCase):

    def test_t2a_source_file_rules_jp_ea(self):
        self.assertEqual(rp.SOURCE_FILE_RULES['jp'],
                         {'prefix': 'jp_', 'max_fallback_days': 5})
        self.assertEqual(rp.SOURCE_FILE_RULES['ea'],
                         {'prefix': 'ea_', 'max_fallback_days': 5})
        self.assertIn('japan_rate_collector', rp._AUTHORIZED_COLLECTORS)
        self.assertIn('jp_market_collector', rp._AUTHORIZED_COLLECTORS)
        self.assertIn('ea_market_collector', rp._AUTHORIZED_COLLECTORS)

    def test_t2b_a6_mirrors(self):
        self.assertIn('ea', tc.MARKETS)
        self.assertIn('ea', rsem.KNOWN_CALENDARS)
        self.assertEqual(rsem.KNOWN_CALENDARS, frozenset(tc.MARKETS))
        self.assertIn('jp_market_collector', rsem.KNOWN_SOURCES)
        self.assertIn('ea_market_collector', rsem.KNOWN_SOURCES)

    def test_t2c_d7_source_to_input_wired(self):
        """GAP08-F3 (j) 涟漪勘正: _SOURCE_TO_INPUT 三键已接线(原断言=接线前
        "无 jp/ea/japan 键"边界冻结态,前后值 1:1 登记 GAP08 DELIVERY §五);
        缺席口径自 boundary 转 noncore_missing;SOURCE_CHANNELS 冻结不动。"""
        for k, ch in (('japan_rate_collector', 'japan'),
                      ('jp_market_collector', 'jp'),
                      ('ea_market_collector', 'ea')):
            self.assertEqual(rp._SOURCE_TO_INPUT.get(k), ch)
        self.assertEqual(rp.SOURCE_CHANNELS,
                         ('global', 'macro', 'china', 'rate_economy'))

    def test_t2d_runtime_lock_dicts(self):
        self.assertEqual(hca.REGISTRY_SOURCE_CHANNEL['jp_market_collector'], 'jp')
        self.assertEqual(hca.REGISTRY_SOURCE_CHANNEL['ea_market_collector'], 'ea')
        ok, why = bl.evolution_legal()
        self.assertTrue(ok, why)
        # IA-P1-WP-E v1.3 域化(§十三.1): vintage 13→21(∪CN 宏观八条目)
        self.assertEqual(set(bl.vintage_additions()),
                         {'JP_POLICY_RATE', 'JGB2Y', 'JGB5Y', 'JGB10Y'}
                         | set(NEW9) | set(CN8)
                         | {'US_REAL_GDP', 'SPX_CAPE', 'SPX_PE_TTM',
                            'SPX_PB'})  # Charter6-P1 §2#1 + P2 §2#5/#6

    def test_t2e_run_weekly_thirteen_steps(self):
        src = open(os.path.join(ROOT, 'run_weekly.py'), encoding='utf-8').read()
        self.assertEqual(src.count('/15'), 15)  # Charter6-P0: 13→14;P2: +Shiller→15
        # MW-V1(2026-11-08 章程校准): jp/ea 自尾部 12/13 挪到快照前 7/8(当日档
        # 进当日快照),japan_rate_collector(JGB/日政策利率权属)纳管为第 6 步;
        # 预测观察步骤(原 11/13)按 PRODUCT-GOAL.md 2026-11-08 勘误下线。
        self.assertIn('"6/15 日本利率与国债曲线(japan_)", "japan_rate_collector.py", False',
                      src)
        self.assertIn('"7/15 日本市场数据采集(jp_)", "jp_market_collector.py", False',
                      src)
        self.assertIn('"8/15 欧元区市场数据采集(ea_)", "ea_market_collector.py", False',
                      src)
        # Charter6-P2(2026-11-09): 第9步=Shiller估值采集(快照前,当日档进当日快照)
        self.assertIn(
            '"9/15 Shiller估值采集(shiller_)", "shiller_collector.py", False', src)
        # Charter6-P0(2026-11-09): 尾步=日档保留策略(非关键;P2起=15/15)
        self.assertIn(
            '"15/15 日档保留策略(90天全量+月度归档)", "data_retention.py", False', src)
        # 快照构建仍在全部采集通道之后(步骤号大于 japan/jp/ea)
        self.assertLess(src.find('日本市场数据采集(jp_)'), src.find('研究快照构建'))
        self.assertLess(src.find('欧元区市场数据采集(ea_)'), src.find('研究快照构建'))
        self.assertLess(src.find('Shiller估值采集'), src.find('研究快照构建'))
        # 预测观察退出自动调度(模块与历史档案保留,仅不在 steps 内)
        self.assertNotIn('"daily_prediction_observer.py"', src)
        # 关键采集器集零变化(4,japan/jp/ea 非关键)
        self.assertNotIn('"jp_market_collector.py"]', src)
        i = src.find('_critical_collectors = [')
        j = src.find(']', i)
        crit = src[i:j]
        for c in ('global_market_collector.py', 'china_market_collector.py',
                  'macro_collector.py', 'rate_expectations.py'):
            self.assertIn(c, crit)
        self.assertNotIn('jp_market_collector', crit)
        self.assertNotIn('ea_market_collector', crit)
        self.assertNotIn('japan_rate_collector', crit)

    def test_t2f_fixture_seven_channels(self):
        """fixt 7 通道全覆盖(红-4 修复面): write_collectors 落盘 jp_/ea_ 档。"""
        with tempfile.TemporaryDirectory() as td:
            fixt.write_collectors(td, '20261102')
            for name in ('global', 'macro', 'china', 'rate_economy', 'japan',
                         'jp', 'ea'):
                p = os.path.join(td, f'{name}_20261102.json')
                self.assertTrue(os.path.exists(p), name)
            jpd = json.load(open(os.path.join(td, 'jp_20261102.json'),
                                 encoding='utf-8'))
            self.assertIn('policy_rates', jpd)
            self.assertNotIn('inflation', jpd)   # 诚实缺席形态沿真实档
            ead = json.load(open(os.path.join(td, 'ea_20261102.json'),
                                 encoding='utf-8'))
            self.assertNotIn('prices', ead)      # DAX/CAC40 诚实缺席


# ══ T3 要点③: jp_market_collector 离线(raw 注入,零网络)════════════════
class TestJpCollectorOffline(unittest.TestCase):

    def test_t3a_full_success_payload(self):
        p, n = jp.build_payload(
            run_date=__import__('datetime').date(2026, 11, 5),
            mof_raw=SYN_MOF, fred_policy_raw=SYN_FRED_POLICY,
            fred_nikkei_raw=SYN_FRED_NIKKEI)
        self.assertEqual(n, 4)
        self.assertEqual(p['date'], '20261105')
        # jgb 节: 末行值+prev=次新行;JGB5Y 不入 a-2 面
        self.assertEqual(p['jgb']['JGB_10Y'],
                         {'value': 2.855, 'unit': 'percent',
                          'date': '2026-11-04', 'prev_value': 2.830})
        self.assertEqual(p['jgb']['JGB_2Y'],
                         {'value': 1.891, 'unit': 'percent',
                          'date': '2026-11-04', 'prev_value': 1.870})
        self.assertNotIn('JGB_5Y', p['jgb'])
        # policy_rates: FRED '.' 行跳过,末值 0.743,prev=0.860
        self.assertEqual(p['policy_rates']['BOJ_POLICY_RATE'],
                         {'value': 0.743, 'unit': 'percent',
                          'date': '2026-09-01', 'prev_value': 0.860})
        # prices: NIKKEI 末值/series 全量;high/low=null(非0)
        nk = p['prices']['NIKKEI225']
        self.assertEqual(nk['close'], 38000.25)
        self.assertEqual(nk['date'], '2026-11-04')
        self.assertIsNone(nk['high'])
        self.assertIsNone(nk['low'])
        self.assertEqual(nk['series'],
                         {'2026-10-30': 38250.0, '2026-11-02': 38100.5,
                          '2026-11-04': 38000.25})
        # 诚实缺席: inflation 节键不出现(禁0占位),sources_status 如实
        self.assertNotIn('inflation', p)
        self.assertEqual(p['sources_status']['JP_CPI_TOKYO']['status'],
                         'MISSING')
        for st in p['sources_status'].values():
            self.assertIn(st['status'], ('EXACT', 'READ_FAIL', 'MISSING'))
        self.assertTrue(any('JP_CPI_TOKYO' in a for a in p['alerts']))

    def test_t3b_source_failure_missing_not_zero(self):
        """要点③核心: 源失败→节缺席+READ_FAIL+alerts,不填0。"""
        p, n = jp.build_payload(
            run_date=__import__('datetime').date(2026, 11, 5),
            mof_raw=SYN_BAD, fred_policy_raw=SYN_BAD,
            fred_nikkei_raw=SYN_BAD)
        self.assertEqual(n, 0)
        self.assertNotIn('jgb', p)
        self.assertNotIn('policy_rates', p)
        self.assertNotIn('prices', p)
        for src in ('MOF_JGBCME', 'FRED_POLICY', 'FRED_NIKKEI225'):
            self.assertEqual(p['sources_status'][src]['status'], 'READ_FAIL')
        # 全系列缺席→main exit 1 不落盘
        with mock.patch.object(jp, 'build_payload',
                               return_value=(p, 0)), \
                tempfile.TemporaryDirectory() as td:
            self.assertEqual(jp.main(['--data-dir', td]), 1)
            self.assertEqual(os.listdir(td), [])

    def test_t3c_network_never_in_tests(self):
        """要点③离线性: 全 raw 注入下 _http_get 零调用(mock 计数=0)。"""
        with mock.patch.object(jp.jrc, '_http_get',
                               side_effect=AssertionError('网络出站')) as g:
            jp.build_payload(
                run_date=__import__('datetime').date(2026, 11, 5),
                mof_raw=SYN_MOF, fred_policy_raw=SYN_FRED_POLICY,
                fred_nikkei_raw=SYN_FRED_NIKKEI)
            self.assertEqual(g.call_count, 0)

    def test_t3d_partial_failure_single_source(self):
        """单源失败不阻断另一源(B3 D10 语义)。"""
        p, n = jp.build_payload(
            run_date=__import__('datetime').date(2026, 11, 5),
            mof_raw=SYN_MOF, fred_policy_raw=SYN_BAD,
            fred_nikkei_raw=SYN_FRED_NIKKEI)
        self.assertEqual(n, 3)
        self.assertIn('jgb', p)
        self.assertNotIn('policy_rates', p)
        self.assertIn('prices', p)

    def test_t3e_save_daily_roundtrip(self):
        p, _n = jp.build_payload(
            run_date=__import__('datetime').date(2026, 11, 5),
            mof_raw=SYN_MOF, fred_policy_raw=SYN_FRED_POLICY,
            fred_nikkei_raw=SYN_FRED_NIKKEI)
        with tempfile.TemporaryDirectory() as td:
            path = jp.save_daily(td, p)
            self.assertEqual(os.path.basename(path), 'jp_20261105.json')
            back = json.load(open(path, encoding='utf-8'))
            self.assertEqual(back['jgb']['JGB_10Y']['value'], 2.855)


# ══ T4 要点③: ea_market_collector 离线(raw 注入,零网络)════════════════
class TestEaCollectorOffline(unittest.TestCase):

    def _build(self, **kw):
        base = dict(run_date=__import__('datetime').date(2026, 11, 5),
                    ecb_dfr_raw=SYN_ECB_DFR, ecb_mro_raw=SYN_ECB_MRO,
                    ecb_hicp_raw=SYN_ECB_HICP, bbk10_raw=SYN_BBK10,
                    bbk2_raw=SYN_BBK2, bbk10_meta_raw=SYN_BBK_META_OK_10,
                    bbk2_meta_raw=SYN_BBK_META_OK_2)
        base.update(kw)
        return ea.build_payload(**base)

    def test_t4a_full_success_payload(self):
        p, n = self._build()
        self.assertEqual(n, 5)
        self.assertEqual(p['date'], '20261105')
        self.assertEqual(p['policy_rates']['ECB_DFR'],
                         {'value': 2.00, 'unit': 'percent',
                          'date': '2026-11-04', 'prev_value': 2.00})
        self.assertEqual(p['policy_rates']['ECB_MRO']['value'], 3.15)
        self.assertEqual(p['bund']['BUND_10Y'],
                         {'value': 2.60, 'unit': 'percent',
                          'date': '2026-11-04', 'prev_value': 2.62})
        self.assertEqual(p['bund']['BUND_2Y']['value'], 2.30)
        # HICP 月频: 月期→当月首日表示+change/freq
        hicp = p['inflation']['EA_HICP_YOY']
        self.assertEqual(hicp['value'], 2.2)
        self.assertEqual(hicp['date'], '2026-09-01')
        self.assertEqual(hicp['prev_value'], 2.4)
        self.assertEqual(hicp['change'], round(2.2 - 2.4, 4))
        self.assertEqual(hicp['change_period'], 'MoM')
        self.assertEqual(hicp['freq'], 'Monthly')
        # 诚实缺席: prices 节键不出现(禁0占位)
        self.assertNotIn('prices', p)
        self.assertEqual(p['sources_status']['DAX']['status'], 'MISSING')
        self.assertEqual(p['sources_status']['CAC40']['status'], 'MISSING')
        self.assertTrue(any('DAX' in a for a in p['alerts']))

    def test_t4b_bbk2_meta_fail_honest_absence(self):
        """候选键口径核验未通过→BUND_2Y 诚实缺席(宁缺席不猜口径)。"""
        p, n = self._build(bbk2_meta_raw=SYN_BBK_META_BAD)
        self.assertEqual(n, 4)
        self.assertNotIn('BUND_2Y', p.get('bund', {}))
        self.assertIn('BUND_10Y', p['bund'])
        self.assertTrue(any('口径核验未通过' in a for a in p['alerts']))

    def test_t4c_source_failure_missing_not_zero(self):
        p, n = self._build(ecb_dfr_raw=SYN_BAD, ecb_mro_raw=SYN_BAD,
                           ecb_hicp_raw=SYN_BAD, bbk10_raw=SYN_BAD,
                           bbk2_raw=SYN_BAD)
        self.assertEqual(n, 0)
        for sec in ('policy_rates', 'bund', 'inflation', 'prices'):
            self.assertNotIn(sec, p)
        for src in ('ECB_FM_DFR', 'ECB_FM_MRO', 'ECB_ICP_HICP',
                    'BBK_WU3146', 'BBK_WU3141'):
            self.assertEqual(p['sources_status'][src]['status'], 'READ_FAIL')
        with mock.patch.object(ea, 'build_payload',
                               return_value=(p, 0)), \
                tempfile.TemporaryDirectory() as td:
            self.assertEqual(ea.main(['--data-dir', td]), 1)
            self.assertEqual(os.listdir(td), [])

    def test_t4d_partial_failure_single_source(self):
        p, n = self._build(bbk10_raw=SYN_BAD)
        self.assertEqual(n, 4)
        self.assertNotIn('BUND_10Y', p.get('bund', {}))
        self.assertIn('policy_rates', p)
        self.assertIn('inflation', p)

    def test_t4e_sdmx_month_period_and_missing_values(self):
        rows, alerts = ea.parse_sdmx_csv(SYN_ECB_DFR)
        self.assertEqual(rows, [('2026-11-02', 2.00), ('2026-11-04', 2.00)])
        self.assertEqual(alerts, [])          # 空值行跳过非告警

    def test_t4f_network_never_in_tests(self):
        with mock.patch.object(ea, '_http_get',
                               side_effect=AssertionError('网络出站')) as g:
            p, n = self._build()
            self.assertEqual(n, 5)
            self.assertEqual(g.call_count, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
