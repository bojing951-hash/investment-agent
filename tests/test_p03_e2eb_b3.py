# -*- coding: utf-8 -*-
"""IA-P03-E2EB-WP-B3 专项测试(R023;日本利率数据身份与获取的离线行为锁)。

任务: IA-P03-E2EB-WP-B3-AC-v1.4 案A回做版 §一 B3-AC-01..§二 B3-AC-02
基点: 04ead6d(R058 merge;分支 dev/p03-e2eb-b3)
被测对象: scripts/japan_rate_collector.py(真实函数,raw 注入解析) +
  config/metric_registry.json(81→85) + research_provenance(通道登记) +
  registry_semantics/trading_calendar(双侧同步) + snapshot_builder(零改动派生)。

数据纪律: 本文件全部为**离线合成 fixture 行为锁**,合成数值刻意构造,不代表任何
真实交易日行情;真实端点锚定(2026-11-05 实测: MOF jgbcme 2026-11-04 收盘
2Y=1.891/5Y=2.269/10Y=2.855;FRED IRSTCI01JPM156N 2026-09 月均=1.043)在合成
fixture 中以同值复刻作为解析预期(锚定值仅作期望常量,不冒充网络获取),原始回执
在证据包 real/ 目录,不在本文件冒充采集。零网络: 全部 fetch 经 raw= 注入或
mock _http_get;零 skip;零删除断言。

锁清单:
T1 注册表身份(102/101/v2.3.0[IA-P1-WP-A v1.3 域化: 85+9;IA-P1-WP-E v1.3 域化:
   94+8];四条目全字段硬编码冻结;
   registry_semantics 零错;A6 双侧镜像;与 R057 冻结 81 条目 ID 不相交;
   vintage_additions 恰为日本四条目∪P1 新九条目∪CN 宏观八条目∪Charter6-P1 US_REAL_GDP(22))
T2 通道登记(SOURCE_FILE_RULES japan 精确;sb.SOURCES 含 japan 且由规则表派生;
   canonical_source_file 接受/跨通道拒/坏日期拒/路径成分拒;SOURCE_CHANNELS 基线
   四通道冻结不动;_AUTHORIZED_COLLECTORS 在场;_SOURCE_TO_INPUT 无 japan 键=D7
   边界记录语义钉死)
T3 japan 日历(MARKETS 含 japan 且=rsem.KNOWN_CALENDARS;01-01/12-25 假;周末假;
   2026-11-03 文化日保守 True;正常营业日 True)
T4 采集器离线解析(shift_jis 列头映射取最后合法行=合成锚定值精确;FRED '.' 缺失
   跳过取最后有值行;无有效行→None+alerts;build_payload 四系列精确/单源失败
   容错/双源失败 n==0 且 main exit 1 不落盘;期限列坏值→缺席+alert;原子写往返;
   JGB_TENORS 映射冻结)
T5 一致性与真实档锁(注册表↔采集器↔日历三方一致;data/daily/japan_20261105.json
   真实档值/观测日/sha256 全文冻结;沙箱 sb.build_snapshot 集成:japan EXACT+
   其余通道 MISSING+gate_a FAIL(core_missing)——通道登记经生产 resolve 链证明,
   全程零生产触碰;过期超回退窗→MISSING 负向)
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import date
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts'), os.path.dirname(os.path.abspath(__file__))):
    if p not in sys.path:
        sys.path.insert(0, p)

from helpers import baseline_locks as bl          # noqa: E402
import japan_rate_collector as jrc                # noqa: E402
import registry_semantics as rsem                 # noqa: E402
import research_provenance as rp                  # noqa: E402
import snapshot_builder as sb                     # noqa: E402
import trading_calendar as tc                     # noqa: E402

with open(os.path.join(ROOT, 'config', 'metric_registry.json'), encoding='utf-8') as _f:
    REG = json.load(_f)
METRICS = {m['metric_id']: m for m in REG['metrics']}   # 注册表为列表,按id索引
JP4 = {'JP_POLICY_RATE', 'JGB2Y', 'JGB5Y', 'JGB10Y'}
# IA-P1-WP-A v1.3: 新九条目(REPORT §零.12④;append 于 metrics 数组尾)
NEW9 = {'JP_CPI_TOKYO_YOY', 'NIKKEI225', 'ECB_DFR', 'ECB_MRO', 'BUND_10Y',
        'BUND_2Y', 'EA_HICP_YOY', 'DAX', 'CAC40'}
# IA-P1-WP-E v1.3(§十三.1 从属锁域化迁移): CN 宏观八条目(G-P1-14..18,
# REPORT §零.6A 终值表;append 于 metrics 数组尾)
CN8 = {'CN_LPR_1Y', 'CN_LPR_5Y', 'CN_CPI_YOY', 'CN_PPI_YOY', 'CN_PMI_MFG',
       'CN_SF_FLOW', 'CN_NEW_LOANS', 'CN_OMO_7D'}

# ---- 真实档冻结指纹(2026-11-05 采集落盘实测,证据包 real/ 原始回执) ----
REAL_JAPAN_FILE = os.path.join(ROOT, 'data', 'daily', 'japan_20261105.json')
REAL_JAPAN_SHA256 = ('6bba4718759ba12546499c1bdc510a11'
                     '57b87f9462408e14071967d29e14e7f1')
# D12 真实锚定: MOF 2026-11-04 收盘 / FRED 2026-09 月均
ANCHOR_JGB = {'JGB2Y': 1.891, 'JGB5Y': 2.269, 'JGB10Y': 2.855}
ANCHOR_JGB_OBS = '2026-11-04'
ANCHOR_POLICY = 1.043
ANCHOR_POLICY_OBS = '2026-09-01'

# ---- 合成 fixture(离线;锚定值复刻为期望常量,结构镜像源端真实形态) ----
MOF_BYTES = (
    '2026年11月 中途経過\r\n'                       # 当月标题行
    'Date,1Y,2Y,3Y,4Y,5Y,10Y,20Y,30Y,40Y\r\n'      # 列头(期限名驱动映射)
    '2026/11/2,0.50,1.880,1.990,2.100,2.250,2.840,3.10,3.20,3.30\r\n'
    '2026/11/4,0.51,1.891,2.000,2.110,2.269,2.855,3.11,3.21,3.31\r\n'
    '※末尾コメント行\r\n'                          # 末行注释(Shift_JIS可编码,无数据)
).encode('shift_jis')
MOF_BYTES_CORRUPT_10Y = (
    'Date,1Y,2Y,5Y,10Y\r\n'
    '2026/11/4,0.51,1.891,2.269,XX\r\n'
).encode('shift_jis')
FRED_BYTES = (
    'observation_date,IRSTCI01JPM156N\r\n'
    '2026-07-01,0.860\r\n'
    '2026-08-01,.\r\n'                              # FRED 缺失值标记须跳过
    '2026-09-01,1.043\r\n'
).encode('utf-8')


def _sha256_file(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


class T1RegistryIdentity(unittest.TestCase):
    """B3-AC-01: 注册表 81→85,四条目身份全字段冻结。"""

    def test_t01_counts_and_version(self):
        # IA-P1-WP-E v1.3 域化(§十三.1 从属锁迁移,同型不弱化):
        # 94+8→102 / 93+8→101 / 2.2.0→2.3.0
        self.assertEqual(len(REG['metrics']), 110, '指标总数须恰为110(85+9+8+1+3Charter6+2P2-3+2数据批1)')  # 数据批1: +SPX_EPS/M2SL
        self.assertEqual(sum(1 for m in REG['metrics']
                             if m.get('status') == 'active'), 108)  # 数据批1 +SPX_EPS/M2SL
        self.assertEqual(REG['version'], '2.8.0', '版本号须为2.8.0(数据批1 2026-11-10)')

    def test_t02_four_entries_full_field_freeze(self):
        # D11 全字段冻结(硬编码逐字段=磁盘实况,任何漂移即红);
        # IA-P1-WP-A v1.3: +economy/economy_rule/market_seat 三字段(P9/JP/onshore);
        # A-fin(2026-11-09): +observation_period_kind/release_date_available
        self.assertEqual(METRICS['JP_POLICY_RATE'], {
            'metric_id': 'JP_POLICY_RATE',
            'display_name': '日本无担保隔夜拆借利率(月均)',
            'source': 'japan_rate_collector',
            'source_symbol': 'IRSTCI01JPM156N',
            'asset_class': 'policy_rate',
            'frequency': 'monthly',
            'observation_period_kind': 'calendar_month',
            'release_date_available': False,
            'unit': 'percent',
            'calendar': 'japan',
            'economy': 'JP',
            'economy_rule': 'P9:calendar=japan',
            'market_seat': 'onshore_local',
            'criticality': 'important',
            'status': 'active',
            'identity': {'instrument': 'macro_series', 'adjustment': 'none'},
            'value_type': 'monthly_avg_rate',
            'calc': ('FRED系列IRSTCI01JPM156N最新观测(日本无担保隔夜拆借利率'
                     '月均,OECD/BOJ口径;政策利率operative信号,与BOJ决议目标值'
                     '口径不同,决议值变更时点见release_semantics)'),
            'validation': {'range': [-0.5, 2]},
            'freshness': {'max_calendar_lag_days': 60,
                          'note': '月频:观测日=统计期(月),发布滞后4-6周属正常,'
                                  '未发布≠数据缺失'},
            'release_semantics': ('FRED月频系列发布日不可得;BOJ决议目标值经'
                                  '金融政策决定会议公布(无固定时刻),本指标为月均 '
                                  'operative 利率而非决议值,按观测月+滞后窗口保守标注'),
        })
        for tenor, disp, calc in (
                ('JGB2Y', '2年期日债收益率', '2年期'),
                ('JGB5Y', '5年期日债收益率', '5年期'),
                ('JGB10Y', '10年期日债收益率', '10年期')):
            self.assertEqual(METRICS[tenor], {
                'metric_id': tenor,
                'display_name': disp,
                'source': 'japan_rate_collector',
                'source_symbol': tenor.replace('JGB', ''),
                'asset_class': 'rates_yield',
                'frequency': 'daily',
                'observation_period_kind': 'trading_day',
                'release_date_available': True,
                'unit': 'percent',
                'calendar': 'japan',
                'economy': 'JP',
                'economy_rule': 'P9:calendar=japan',
                'market_seat': 'onshore_local',
                'criticality': 'important',
                'status': 'active',
                'identity': {'instrument': 'index_rate_series',
                             'adjustment': 'none'},
                'value_type': 'yield_or_spread_level',
                'calc': (f'MOF日本国债收益率曲线(jgbcme){calc}最新收盘观测'
                         '(每营业日发布,非营业日无新观测)'),
                'validation': {'range': [-0.5, 15], 'max_week_abs_move': 1.0},
                'freshness': {'max_calendar_lag_days': 7},
                'release_semantics': ('MOF每营业日收盘后发布当日曲线(约19:00 '
                                      'JST);发布时点不可得,按观测日保守处理'
                                      '(观测日≤研究截止即视为可用,发布晚于观测日'
                                      '的风险见快照披露)'),
            }, tenor)

    def test_t03_rsem_zero_errors(self):
        self.assertEqual(rsem.validate_registry(REG), [],
                         'registry_semantics 须零错零待核')

    def test_t04_a6_mirrors_double_side(self):
        # A6b/A6c 双侧同步(镜像 test_p02_w1.py 惯例)
        self.assertEqual(rsem.KNOWN_CALENDARS, frozenset(tc.MARKETS),
                         'A6b: rsem.KNOWN_CALENDARS==tc.MARKETS')
        self.assertEqual(
            rsem.KNOWN_SOURCES,
            frozenset(rp._AUTHORIZED_COLLECTORS) | {'macro_collector(derived)'},
            'A6c: rsem.KNOWN_SOURCES==rp._AUTHORIZED_COLLECTORS∪derived')
        self.assertIn('japan', rsem.KNOWN_CALENDARS)
        self.assertIn('japan_rate_collector', rsem.KNOWN_SOURCES)
        self.assertIn('japan_rate_collector', rp._AUTHORIZED_COLLECTORS)

    def test_t05_disjoint_from_frozen_81(self):
        # R057 冻结基线 ID 集与新增四条目不相交(命名冲突预防 D1)
        self.assertEqual(JP4 & set(bl.BASELINE_VINTAGE_IDS), set(),
                         '日本四条目不得与R057冻结81条目撞名')

    def test_t06_vintage_additions_exact(self):
        # IA-P1-WP-A v1.3 域化: additions 4→13(日本四条目∪P1 新九条目);
        # IA-P1-WP-E v1.3 域化(§十三.1): 13→21(∪CN 宏观八条目)
        self.assertEqual(set(bl.vintage_additions()), JP4 | NEW9 | CN8
                         | {'US_REAL_GDP', 'SPX_CAPE', 'SPX_PE_TTM', 'SPX_PB'}
                         | {'SOFR', 'WALCL'}   # Charter7 P2-3: +2=27(流动性维)
                         | {'SPX_EPS', 'M2SL'},  # 数据批1(2026-11-10): +2=29
                         'vintage_additions 须恰为…∪US_REAL_GDP∪Shiller三条目∪P2-3∪数据批1(29)')


class T2ChannelRegistration(unittest.TestCase):
    """B3-AC-01: japan 通道登记与文件身份规则;基线四通道域冻结不动。"""

    def test_t10_source_file_rules_exact(self):
        self.assertEqual(rp.SOURCE_FILE_RULES.get('japan'),
                         {'prefix': 'japan_', 'max_fallback_days': 5})
        chans = {ch for ch, _pat, _lag in sb.SOURCES}
        self.assertIn('japan', chans, 'sb.SOURCES 须由规则表派生出 japan')
        jp = [(ch, pat, lag) for ch, pat, lag in sb.SOURCES if ch == 'japan']
        self.assertEqual(jp, [('japan', 'japan_*.json', 5)])

    def test_t11_canonical_accept(self):
        self.assertEqual(rp.canonical_source_file('japan', 'japan_20261105.json'),
                         '20261105')
        self.assertEqual(rp.canonical_source_file('japan', 'japan_20260101.json'),
                         '20260101')

    def test_t12_canonical_rejects(self):
        # 跨通道文件不可冒充 japan 身份
        self.assertIsNone(rp.canonical_source_file(
            'japan', 'china_20261105.json'))
        self.assertIsNone(rp.canonical_source_file(
            'japan', 'macro_20261105.json'))
        # 伪装前后缀/非json/坏日历日期(20261399 月13日)/路径成分
        self.assertIsNone(rp.canonical_source_file(
            'japan', 'japan_20261105.json.bak'))
        self.assertIsNone(rp.canonical_source_file(
            'japan', 'xjapan_20261105.json'))
        self.assertIsNone(rp.canonical_source_file(
            'japan', 'japan_20261399.json'))
        self.assertIsNone(rp.canonical_source_file(
            'japan', '/etc/japan_20261105.json'))
        self.assertIsNone(rp.canonical_source_file(
            'japan', '../daily/japan_20261105.json'))

    def test_t13_source_channels_frozen(self):
        # D6: 迭代域冻结为基线四通道(历史快照无 japan 键,在场中性不回溯)
        self.assertEqual(rp.SOURCE_CHANNELS,
                         ('global', 'macro', 'china', 'rate_economy'))

    def test_t14_source_to_input_no_japan(self):
        # D7: source→input 映射有意不加 japan→非核心缺席走边界记录
        # (noncore_missing_boundary),不进 noncore_missing,不影响 gate。
        self.assertNotIn('japan', rp._SOURCE_TO_INPUT)
        # 但事实层 source 必须可识别为已授权采集器(不存在未登记来源)
        self.assertIn('japan_rate_collector', rp._AUTHORIZED_COLLECTORS)


class T3JapanCalendar(unittest.TestCase):
    """japan 日历最小集(D3): 01-01/12-25 假;其余自然日营业。"""

    def test_t20_markets(self):
        self.assertIn('japan', tc.MARKETS)

    def test_t21_days(self):
        self.assertFalse(tc.is_trading_day(date(2026, 1, 1), 'japan'))
        self.assertFalse(tc.is_trading_day(date(2026, 12, 25), 'japan'))
        self.assertFalse(tc.is_trading_day(date(2026, 11, 7), 'japan'))  # 周六
        self.assertFalse(tc.is_trading_day(date(2026, 11, 8), 'japan'))  # 周日
        # 2026-11-03 文化日(火): 最小集保守不识别→True(宁多勿漏,D3)
        self.assertTrue(tc.is_trading_day(date(2026, 11, 3), 'japan'))
        self.assertTrue(tc.is_trading_day(date(2026, 11, 4), 'japan'))
        self.assertTrue(tc.is_trading_day(date(2026, 11, 5), 'japan'))


class T4CollectorOffline(unittest.TestCase):
    """B3-AC-02: 采集器解析/容错/落盘全离线锁(raw 注入,零网络)。"""

    def test_t30_fetch_mof_jgb_anchor(self):
        obs, out, alerts = jrc.fetch_mof_jgb(MOF_BYTES)
        self.assertEqual(obs, ANCHOR_JGB_OBS)      # 取最后合法数据行
        self.assertEqual(out, ANCHOR_JGB)
        self.assertEqual(alerts, [])

    def test_t31_fetch_mof_no_valid_rows(self):
        obs, out, alerts = jrc.fetch_mof_jgb(b'no,header\nonly,text\n')
        self.assertIsNone(obs)
        self.assertEqual(out, {})
        self.assertTrue(alerts, '须有如实告警')

    def test_t32_fetch_fred_anchor_and_dot_skip(self):
        obs, v, alerts = jrc.fetch_fred_policy_rate(FRED_BYTES)
        self.assertEqual(obs, ANCHOR_POLICY_OBS)   # '.'行跳过取最后有值行
        self.assertEqual(v, ANCHOR_POLICY)
        self.assertEqual(alerts, [])

    def test_t33_fetch_fred_all_missing(self):
        raw = ('observation_date,IRSTCI01JPM156N\r\n'
               '2026-08-01,.\r\n').encode('utf-8')
        obs, v, alerts = jrc.fetch_fred_policy_rate(raw)
        self.assertIsNone(obs)
        self.assertIsNone(v)
        self.assertTrue(alerts)

    def test_t34_build_payload_full(self):
        payload, n = jrc.build_payload(run_date=date(2026, 11, 5),
                                       mof_raw=MOF_BYTES, fred_raw=FRED_BYTES)
        self.assertEqual(n, 4)
        self.assertEqual(payload['date'], '20261105')
        self.assertEqual(payload['data'],
                         dict(ANCHOR_JGB, JP_POLICY_RATE=ANCHOR_POLICY))
        self.assertEqual(payload['observations'],
                         {'JGB2Y': ANCHOR_JGB_OBS, 'JGB5Y': ANCHOR_JGB_OBS,
                          'JGB10Y': ANCHOR_JGB_OBS,
                          'JP_POLICY_RATE': ANCHOR_POLICY_OBS})
        self.assertEqual(payload['alerts'], [])
        self.assertIn('mof.go.jp', payload['sources']['JGB']['url'])
        self.assertIn('fred.stlouisfed.org',
                      payload['sources']['JP_POLICY_RATE']['url'])

    def test_t35_mof_source_fail_partial(self):
        # 单源失败不阻断另一源(诚实降级,不伪造缺席系列)
        def _fail_mof(url, src='mof'):
            if src == 'mof':
                raise OSError('synthetic mof outage')
            return FRED_BYTES
        with mock.patch.object(jrc, '_http_get', side_effect=_fail_mof):
            payload, n = jrc.build_payload(run_date=date(2026, 11, 5))
        self.assertEqual(n, 1)
        self.assertEqual(list(payload['data']), ['JP_POLICY_RATE'])
        self.assertTrue(any('MOF' in a for a in payload['alerts']),
                        payload['alerts'])

    def test_t36_fred_source_fail_partial(self):
        def _fail_fred(url, src='mof'):
            if src == 'fred':
                raise OSError('synthetic fred outage')
            return MOF_BYTES
        with mock.patch.object(jrc, '_http_get', side_effect=_fail_fred):
            payload, n = jrc.build_payload(run_date=date(2026, 11, 5))
        self.assertEqual(n, 3)
        self.assertEqual(set(payload['data']), set(ANCHOR_JGB))
        self.assertTrue(any('FRED' in a for a in payload['alerts']))

    def test_t37_all_fail_no_file_exit1(self):
        with mock.patch.object(jrc, '_http_get',
                               side_effect=OSError('synthetic net down')):
            payload, n = jrc.build_payload(run_date=date(2026, 11, 5))
        self.assertEqual(n, 0, '全部系列缺席时不得有任何系列冒充')
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.object(jrc, '_http_get',
                                   side_effect=OSError('synthetic net down')):
                rc = jrc.main(['--data-dir', td])
            self.assertEqual(rc, 1, '全部缺席→exit 1')
            self.assertEqual(os.listdir(td), [], '不得落盘空壳文件')

    def test_t38_corrupt_tenor_missing_with_alert(self):
        obs, out, alerts = jrc.fetch_mof_jgb(MOF_BYTES_CORRUPT_10Y)
        self.assertEqual(obs, ANCHOR_JGB_OBS)
        self.assertNotIn('JGB10Y', out)
        self.assertEqual({k: v for k, v in out.items() if k != 'JGB10Y'},
                         {'JGB2Y': 1.891, 'JGB5Y': 2.269})
        self.assertTrue(any('10Y' in a for a in alerts), alerts)
        self.assertTrue(any('关键期限缺席' in a for a in alerts))

    def test_t39_save_daily_roundtrip_atomic(self):
        payload, _n = jrc.build_payload(run_date=date(2026, 11, 5),
                                        mof_raw=MOF_BYTES, fred_raw=FRED_BYTES)
        with tempfile.TemporaryDirectory() as td:
            path = jrc.save_daily(td, payload)
            self.assertEqual(os.path.basename(path), 'japan_20261105.json')
            self.assertEqual(sorted(os.listdir(td)),
                             ['japan_20261105.json'], '不得残留 .tmp')
            with open(path, encoding='utf-8') as f:
                self.assertEqual(json.load(f), payload)

    def test_t40_jgb_tenors_map_frozen(self):
        self.assertEqual(jrc.JGB_TENORS,
                         {'2Y': 'JGB2Y', '5Y': 'JGB5Y', '10Y': 'JGB10Y'})


class T5ConsistencyAndRealFile(unittest.TestCase):
    """三方一致性 + 真实档全文冻结 + 沙箱生产链集成(零生产触碰)。"""

    def test_t50_registry_collector_calendar_consistency(self):
        for mid in JP4:
            m = METRICS[mid]
            self.assertEqual(m['source'], 'japan_rate_collector', mid)
            self.assertEqual(m['calendar'], 'japan', mid)
            self.assertEqual(m['status'], 'active', mid)
            self.assertEqual(m['criticality'], 'important',
                             f'{mid} 非核心(D5 禁 core)')
        self.assertEqual({METRICS[m]['frequency'] for m in JP4},
                         {'daily', 'monthly'})
        self.assertEqual({METRICS[m]['unit'] for m in JP4}, {'percent'})
        self.assertEqual(list(jrc.JGB_TENORS.values()),
                         ['JGB2Y', 'JGB5Y', 'JGB10Y'])

    def test_t51_real_file_lock(self):
        with open(REAL_JAPAN_FILE, encoding='utf-8') as f:
            real = json.load(f)
        self.assertEqual(real['date'], '20261105')
        self.assertEqual(real['data'],
                         dict(ANCHOR_JGB, JP_POLICY_RATE=ANCHOR_POLICY))
        self.assertEqual(real['observations'],
                         {'JGB2Y': ANCHOR_JGB_OBS, 'JGB5Y': ANCHOR_JGB_OBS,
                          'JGB10Y': ANCHOR_JGB_OBS,
                          'JP_POLICY_RATE': ANCHOR_POLICY_OBS})
        self.assertEqual(real['alerts'], [], '真实档零告警(两源均成功)')
        self.assertTrue(real['fetched_at'].startswith('2026-11-05T'))
        self.assertEqual(_sha256_file(REAL_JAPAN_FILE), REAL_JAPAN_SHA256)

    def test_t52_sandbox_build_snapshot_integration(self):
        # 沙箱: 仅 japan 真实档副本→生产 resolve/build 链:
        # japan=EXACT(sha256一致), 基线四通道=MISSING, gate_a=FAIL(core_missing)
        with tempfile.TemporaryDirectory() as td:
            shutil.copy2(REAL_JAPAN_FILE, td)
            snap = sb.build_snapshot(target_ymd='20261105', data_dir=td,
                                     out_dir=td, trusted_root=td)
            st = snap['sources_status']
            self.assertEqual(st['japan']['status'], 'EXACT')
            self.assertEqual(st['japan']['file'], 'japan_20261105.json')
            self.assertEqual(st['japan']['sha256'], REAL_JAPAN_SHA256)
            for ch in rp.SOURCE_CHANNELS:
                self.assertEqual(st[ch]['status'], 'MISSING', ch)
            self.assertEqual(snap['gate_a']['status'], 'FAIL')
            self.assertTrue(snap['gate_a']['core_missing'])
            # digest 可复算(canonical JSON 确定性)
            self.assertEqual(rp.digest_snapshot(snap),
                             rp.digest_snapshot(json.loads(
                                 json.dumps(snap))))

    def test_t53_sandbox_stale_beyond_fallback_missing(self):
        # 负向: 目标日 20261111,仅 20261105 档(超 5 自然日回退窗)→MISSING
        with tempfile.TemporaryDirectory() as td:
            stale = os.path.join(td, 'japan_20261111.json')
            shutil.copy2(REAL_JAPAN_FILE, stale)
            with open(stale, encoding='utf-8') as f:
                payload = json.load(f)
            payload['date'] = '20261105'   # 内容日期=档名日期回退窗起点
            with open(stale, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=1)
            os.rename(stale, os.path.join(td, 'japan_20261105.json'))
            snap = sb.build_snapshot(target_ymd='20261111', data_dir=td,
                                     out_dir=td, trusted_root=td)
            self.assertEqual(snap['sources_status']['japan']['status'],
                             'MISSING')


if __name__ == '__main__':
    unittest.main(verbosity=2)
