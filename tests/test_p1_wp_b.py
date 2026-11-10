#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P1-WP-B 验收件: DESIGN §六 L170 验收要点①②③ + 技术要点(Gate A 对新指标裁决)。

① 新通道事实构造+口径(week/MTD/YTD 对 jp/ea 日历)+数据不足路径——
   normalize_jp/normalize_ea 合成 fixture(raw 注入, 零网络), 期望值手算硬编码;
② 快照 sources_status 含 jp/ea 键的构建测试(含缺源 MISSING)——
   真实 build_snapshot + fixt 7 通道 canon 构造;
③ 既有 US 面输出零回归(W-3 对照)——7通道 vs 基线4通道快照 US 面全等;
④ Gate A 对新指标裁决——rp.recompute_gate_a: 在场计数/缺席边界/坏值 noncore_fail。

数据纪律: 合成值全部显式发明并标注[示意], 不冒充真实; 真实档面
(data/daily/jp_20261105.json, ea_20261105.json, WP-A 步骤⑪ 交付)只读引用并
标注[实取]。期望值独立手算, 禁自证(不 import 实现侧计算结果)。
定值源=docs/P1_WP_B_REPORT.md §零.8/§零.11。
"""
import copy
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import fact_engine as fe               # noqa: E402
import research_provenance as rp       # noqa: E402
import snapshot_builder as sb          # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixt                            # noqa: E402

# 13 新指标(6 JP + 7 EA; 权属: japan_rate_collector×4 / jp_market_collector×2 /
# ea_market_collector×7)——独立重编码, 与注册表实测对齐
JP13 = ('JP_POLICY_RATE', 'JGB2Y', 'JGB5Y', 'JGB10Y',
        'JP_CPI_TOKYO_YOY', 'NIKKEI225',
        'ECB_DFR', 'ECB_MRO', 'BUND_10Y', 'BUND_2Y', 'EA_HICP_YOY', 'DAX', 'CAC40')

AS_OF_SYN = '2026-01-09T08:00:00+08:00'          # [示意] 周五 2026-01-09 研究截止

# [示意] jp_ 档合成形态(镜像 a-2: policy_rates/jgb/inflation/prices; series=
# date→value 字典)——数值全部发明, 处于注册表合法域内
JP_SYN = {
    "date": "20260109",
    "generated_at": "2026-01-09T08:00:00Z",
    "fetched_at": "2026-01-09T08:00:00Z",
    "sources_status": {},
    "policy_rates": {"BOJ_POLICY_RATE": {"value": 1.043, "unit": "percent",
                                         "date": "2025-12-01", "prev_value": 0.977}},
    "jgb": {"JGB_10Y": {"value": 2.855, "unit": "percent",
                        "date": "2026-01-08", "prev_value": 2.817},
            "JGB_2Y": {"value": 1.891, "unit": "percent",
                       "date": "2026-01-08", "prev_value": 1.88}},
    "inflation": {"JP_CPI_TOKYO_YOY": {"value": 2.2, "unit": "percent",
                                       "date": "2025-12-01", "prev_value": 2.4,
                                       "change": -0.2, "change_period": "MoM",
                                       "freq": "Monthly"}},
    "prices": {"NIKKEI225": {"close": 52000.0, "date": "2026-01-09",
                             "high": None, "low": None,
                             "series": {"2025-12-30": 50000.0,
                                        "2026-01-05": 51000.0,
                                        "2026-01-09": 52000.0}}},
    "observations": {}, "sources": {}, "alerts": [],
}

# [示意] ea_ 档合成形态(7 指标齐备; DAX/CAC40 prices 节带 series)
EA_SYN = {
    "date": "20260109",
    "generated_at": "2026-01-09T08:00:00Z",
    "fetched_at": "2026-01-09T08:00:00Z",
    "sources_status": {},
    "policy_rates": {"ECB_DFR": {"value": 2.00, "unit": "percent",
                                  "date": "2026-01-08", "prev_value": 2.00},
                     "ECB_MRO": {"value": 2.65, "unit": "percent",
                                 "date": "2026-01-08", "prev_value": 2.40}},
    "bund": {"BUND_10Y": {"value": 2.82, "unit": "percent",
                          "date": "2026-01-08", "prev_value": 2.80},
             "BUND_2Y": {"value": 2.31, "unit": "percent",
                         "date": "2026-01-08", "prev_value": 2.35}},
    "inflation": {"EA_HICP_YOY": {"value": 2.2, "unit": "percent",
                                  "date": "2025-12-01", "prev_value": 2.4}},
    "prices": {"DAX": {"close": 21000.0, "date": "2026-01-09",
                       "high": None, "low": None,
                       "series": {"2026-01-02": 20000.0, "2026-01-09": 21000.0}},
               "CAC40": {"close": 8100.0, "date": "2026-01-09",
                         "high": None, "low": None,
                         "series": {"2026-01-02": 8000.0, "2026-01-09": 8100.0}}},
    "observations": {}, "sources": {}, "alerts": [],
}

YMD = '20261106'                                  # [示意] 周五快照日
OBS = fixt.obs_for(YMD)                           # = 2026-11-05
AS_OF = fixt.as_of_for(YMD)

_SS_MIN = {'global': {'status': 'EXACT', 'file': 'global_20261106.json',
                      'file_date': '20261106'},
           'macro': {'status': 'EXACT', 'file': 'macro_20261106.json',
                     'file_date': '20261106'},
           'china': {'status': 'EXACT', 'file': 'china_20261106.json',
                     'file_date': '20261106'},
           'rate_economy': {'status': 'EXACT',
                            'file': 'rate_economy_20261106.json',
                            'file_date': '20261106'},
           'japan': {'status': 'EXACT', 'file': 'japan_20261106.json',
                     'file_date': '20261106'},
           'jp': {'status': 'EXACT', 'file': 'jp_20261106.json',
                  'file_date': '20261106'},
           'ea': {'status': 'EXACT', 'file': 'ea_20261106.json',
                  'file_date': '20261106'}}


def _gate_payload(facts, sources_status=None):
    return {'facts': facts, 'sources_status': sources_status or _SS_MIN,
            'research_as_of': AS_OF, 'target_date': YMD}


def _japan_facts():
    """[示意] japan 通道(B3 flat 形态)4 事实手工构造——镜像 japan_rate_collector
    fixture 值(fixt L201-203: JGB2Y=0.500/JGB5Y=0.900/JGB10Y=1.200/
    JP_POLICY_RATE=0.100@obs)。"""
    out = []
    for mid, v in (('JP_POLICY_RATE', 0.100), ('JGB2Y', 0.500),
                   ('JGB5Y', 0.900), ('JGB10Y', 1.200)):
        f = fe.make_fact(mid, v, OBS, AS_OF, 'japan_20261106.json',
                         'japan_rate_collector')
        f['issues'] = fe.validate_fact(
            f, {'close': v, 'date': OBS}, fe.metric(mid), as_of_date=AS_OF)
        f['quality_status'] = fe.grade_issues(f['issues'])
        out.append(f)
    return out


def _us_face_facts(payloads):
    """fixt 基线4通道 → 镜像 build_snapshot L273-306 真实调用面
    (具体批次文件名传入 normalize_*; rate_economy→normalize_rate;
    compute_derived 派生)——Gate A 第二层批次比对要求 source.file=具体文件名。"""
    facts = []
    facts += fe.normalize_global(payloads['global'].get('data') or {}, AS_OF,
                                 'global_20261106.json')
    facts += fe.normalize_macro(payloads['macro'].get('data') or {}, AS_OF,
                                'macro_20261106.json')
    facts += fe.normalize_china(payloads['china'], AS_OF, 'china_20261106.json')
    rfacts, _rinfo = fe.normalize_rate(payloads['rate_economy'], AS_OF,
                                       'rate_economy_20261106.json')
    facts += rfacts
    facts += fe.compute_derived(facts, AS_OF)
    return facts


def _us_jp_ea_facts(payloads):
    """fixt 7通道构造 → US 面 + jp/ea 事实集合。"""
    jf, _r = fe.normalize_jp(payloads['jp'], AS_OF, 'jp_20261106.json')
    ef, _r2 = fe.normalize_ea(payloads['ea'], AS_OF, 'ea_20261106.json')
    return _us_face_facts(payloads) + jf + ef


# ══ 要点①: normalize_jp ═════════════════════════════════════════════
class TestNormalizeJp(unittest.TestCase):

    def test_t01_identity_and_ownership_split(self):
        """[示意] 权属拆分: jp_market_collector 系列立事实, B3 权属进对账输入。"""
        facts, recon = fe.normalize_jp(JP_SYN, AS_OF_SYN, 'jp_20260109.json')
        by_id = {f['metric_id']: f for f in facts}
        self.assertEqual(set(by_id), {'NIKKEI225', 'JP_CPI_TOKYO_YOY'})
        nk, cpi = by_id['NIKKEI225'], by_id['JP_CPI_TOKYO_YOY']
        self.assertEqual(nk['value'], 52000.0)
        self.assertEqual(nk['unit'], 'index_point')
        self.assertEqual(nk['observation_date'], '2026-01-09')
        self.assertEqual(nk['source']['collector'], 'jp_market_collector')
        self.assertEqual(nk['source']['file'], 'jp_20260109.json')
        self.assertEqual(nk['quality_status'], 'PASS')
        self.assertEqual(cpi['value'], 2.2)
        self.assertEqual(cpi['unit'], 'percent')
        self.assertEqual(cpi['observation_date'], '2025-12-01')
        # 月频无release_date→RELEASE_UNKNOWN WARN(点时可得性如实披露)
        self.assertEqual(cpi['quality_status'], 'WARN')
        self.assertTrue(any(i['category'] == 'release' for i in cpi['issues']))
        self.assertEqual({r['metric_id'] for r in recon},
                         {'JP_POLICY_RATE', 'JGB10Y', 'JGB2Y'})

    def test_t02_ownership_isomorphism_no_duplicate_facts(self):
        """[示意] 同构 normalize_rate: 注册权属他通道的系列不立事实(real_economy 先例)。"""
        facts, recon = fe.normalize_jp(JP_SYN, AS_OF_SYN)
        fact_ids = {f['metric_id'] for f in facts}
        for mid in ('JP_POLICY_RATE', 'JGB10Y', 'JGB2Y'):
            self.assertNotIn(mid, fact_ids, mid)
        rmap = {r['metric_id']: r for r in recon}
        self.assertEqual(rmap['JP_POLICY_RATE'],
                         {'metric_id': 'JP_POLICY_RATE', 'value': 1.043,
                          'observation_date': '2025-12-01', 'channel': 'jp',
                          'prev_value': 0.977, 'unit': 'percent'})
        self.assertEqual(rmap['JGB10Y']['value'], 2.855)
        self.assertEqual(rmap['JGB2Y']['prev_value'], 1.88)

    def test_t03_nikkei_windows_on_japan_calendar(self):
        """[示意] week/MTD/YTD 对 japan 日历(01-01 假日排除), 手算字面量。"""
        facts, _ = fe.normalize_jp(JP_SYN, AS_OF_SYN)
        d = {f['metric_id']: f for f in facts}['NIKKEI225']['derived']
        w = d['week']
        self.assertEqual(w['basis_date'], '2025-12-30')
        self.assertEqual(w['basis_value'], 50000.0)
        self.assertEqual(w['pct_change'], 4.0)          # 52000/50000−1
        self.assertEqual(w['sessions_in_window'], 2)
        # japan 日历 2025-12-30..2026-01-09 预期交易日=8(01-01 假日排除;
        # 12-30,12-31,01-02,01-05..01-09)
        self.assertEqual(w['expected_sessions'], 8)
        self.assertNotIn('pp_change', w)                # index_point→pct 口径
        self.assertEqual(d['mtd']['pct_change'], 4.0)   # 前月末基准=2025-12-30
        self.assertEqual(d['ytd']['pct_change'], 4.0)   # 上年末基准=2025-12-30
        self.assertFalse(d['m1']['available'])
        self.assertIn('序列不足1个月', d['m1']['reason'])

    def test_t04_insufficient_data_paths(self):
        """[示意] 数据不足: 单观测→七个窗口全部不可用+原因, 绝不回退0。"""
        jp = copy.deepcopy(JP_SYN)
        jp['prices']['NIKKEI225']['series'] = {"2026-01-09": 52000.0}
        facts, _ = fe.normalize_jp(jp, AS_OF_SYN)
        nk = {f['metric_id']: f for f in facts}['NIKKEI225']
        self.assertEqual(nk['value'], 52000.0)
        self.assertEqual(nk['quality_status'], 'PASS')
        d = nk['derived']
        for k in ('week', 'mtd', 'ytd', 'm1', 'm3', 'm6', 'm12'):
            self.assertFalse(d[k]['available'], k)
        self.assertIn('序列不含上一ISO周观测', d['week']['reason'])
        self.assertIn('序列不含前月观测', d['mtd']['reason'])
        self.assertIn('序列不含上年末观测', d['ytd']['reason'])

    def test_t05_unregistered_key_fail_diagnostic(self):
        """[示意] deny-by-default: 未注册键→FAIL诊断记录(不冒充研究事实)。"""
        jp = copy.deepcopy(JP_SYN)
        jp['prices']['TOPIX'] = {"close": 25000.0, "date": "2026-01-09",
                                 "high": None, "low": None}
        facts, _ = fe.normalize_jp(jp, AS_OF_SYN)
        diag = [f for f in facts if f['metric_id'] == 'TOPIX']
        self.assertEqual(len(diag), 1)
        self.assertEqual(diag[0]['quality_status'], 'FAIL')
        self.assertEqual(diag[0]['issues'][0]['category'], 'identity')
        self.assertIn('不在注册表', diag[0]['issues'][0]['message'])
        self.assertEqual(diag[0]['value'], 25000.0)
        # 诊断记录不入有效研究事实计数(FAIL计数=0; PASS=NIKKEI225 真实事实)
        g = fe.snapshot_quality_grade(facts)
        self.assertEqual(g['counts'], {'PASS': 1, 'DEGRADED': 0, 'FAIL': 0})
        rec = rp.recompute_gate_a(_gate_payload(facts))
        self.assertTrue(any('TOPIX' in s for s in rec['non_research_facts']))

    def test_t06_inflation_null_honest_absence(self):
        """[示意] inflation=null(真实首档形态)→不产 CPI 事实不填 0(§三(a-2) L58)。"""
        jp = copy.deepcopy(JP_SYN)
        jp['inflation'] = None
        facts, recon = fe.normalize_jp(jp, AS_OF_SYN)
        ids = {f['metric_id'] for f in facts}
        self.assertEqual(ids, {'NIKKEI225'})
        self.assertFalse(any(f.get('value') == 0 for f in facts))
        self.assertEqual(len(recon), 3)                 # policy/jgb 照常对账


# ══ 要点①: normalize_ea ═════════════════════════════════════════════
class TestNormalizeEa(unittest.TestCase):

    def test_t07_seven_metrics_identity(self):
        """[示意] EA 7 指标齐备→7 事实(键名即注册表id, 零别名), 对账输入恒空。"""
        facts, recon = fe.normalize_ea(EA_SYN, AS_OF_SYN, 'ea_20260109.json')
        by_id = {f['metric_id']: f for f in facts}
        self.assertEqual(set(by_id), {'ECB_DFR', 'ECB_MRO', 'BUND_10Y', 'BUND_2Y',
                                      'EA_HICP_YOY', 'DAX', 'CAC40'})
        self.assertEqual(recon, [])
        expect = {'ECB_DFR': (2.00, '2026-01-08', 'percent', 'PASS'),
                  'ECB_MRO': (2.65, '2026-01-08', 'percent', 'PASS'),
                  'BUND_10Y': (2.82, '2026-01-08', 'percent', 'PASS'),
                  'BUND_2Y': (2.31, '2026-01-08', 'percent', 'PASS'),
                  'EA_HICP_YOY': (2.2, '2025-12-01', 'percent', 'WARN'),
                  'DAX': (21000.0, '2026-01-09', 'index_point', 'PASS'),
                  'CAC40': (8100.0, '2026-01-09', 'index_point', 'PASS')}
        for mid, (v, od, unit, qs) in expect.items():
            f = by_id[mid]
            self.assertEqual(f['value'], v, mid)
            self.assertEqual(f['observation_date'], od, mid)
            self.assertEqual(f['unit'], unit, mid)
            self.assertEqual(f['quality_status'], qs, mid)
            self.assertEqual(f['source']['collector'], 'ea_market_collector', mid)
            self.assertEqual(f['source']['file'], 'ea_20260109.json', mid)

    def test_t08_dax_price_unit_semantics(self):
        """[示意] DAX index_point→pct_change(无 pp_change), ea 日历手算。"""
        facts, _ = fe.normalize_ea(EA_SYN, AS_OF_SYN)
        d = {f['metric_id']: f for f in facts}['DAX']['derived']
        w = d['week']
        self.assertEqual(w['basis_date'], '2026-01-02')
        self.assertEqual(w['pct_change'], 5.0)          # 21000/20000−1
        self.assertEqual(w['sessions_in_window'], 1)
        # ea 日历 2026-01-02..2026-01-09 预期交易日=6(01-02,01-05..01-09)
        self.assertEqual(w['expected_sessions'], 6)
        self.assertNotIn('pp_change', w)

    def test_t09_honest_absence_real_first_archive_shape(self):
        """[示意] 镜像真实首档形态(仅 policy_rates.ECB_MRO)→1 事实, 其余诚实缺席。"""
        ea = {"date": "20260109", "fetched_at": "2026-01-09T08:00:00Z",
              "policy_rates": {"ECB_MRO": {"value": 2.65, "unit": "percent",
                                           "date": "2026-01-08",
                                           "prev_value": 2.40}}}
        facts, recon = fe.normalize_ea(ea, AS_OF_SYN, 'ea_20260109.json')
        self.assertEqual([f['metric_id'] for f in facts], ['ECB_MRO'])
        self.assertEqual(facts[0]['value'], 2.65)
        self.assertEqual(facts[0]['quality_status'], 'PASS')
        self.assertEqual(recon, [])


# ══ 要点①③: build_all 扩展与向后兼容 ═══════════════════════════════
class TestBuildAll(unittest.TestCase):

    def setUp(self):
        self.p = fixt.collector_payloads(YMD, OBS)

    def test_t10_extension_us_jp_ea_coexist(self):
        """[示意] jp_data/ea_data 入参: US 与 jp/ea 事实共存于一次构建。"""
        facts, _recon = fe.build_all(global_data=self.p['global'],
                                     macro_data=self.p['macro'],
                                     china_data=self.p['china'],
                                     as_of=AS_OF,
                                     jp_data=self.p['jp'], ea_data=self.p['ea'])
        ids = {f['metric_id'] for f in facts}
        self.assertIn('SPX', ids)                       # US 面在场
        self.assertIn('NIKKEI225', ids)
        self.assertIn('ECB_MRO', ids)
        self.assertEqual(ids & set(JP13),
                         {'NIKKEI225', 'ECB_DFR', 'ECB_MRO', 'BUND_10Y',
                          'BUND_2Y', 'EA_HICP_YOY'})    # 2 jp + 5 ea( fixture
        # DAX/CAC40 诚实缺席, JP_CPI 诚实缺席)

    def test_t11_backward_compatible_signature(self):
        """[示意] 原签名(4位置参数)调用零破坏——既有测试面兼容。"""
        facts, recon = fe.build_all(self.p['global'], self.p['macro'],
                                    self.p['china'], AS_OF)
        self.assertIsInstance(facts, list)
        self.assertIsInstance(recon, list)
        ids = {f['metric_id'] for f in facts}
        self.assertTrue(ids.isdisjoint(set(JP13)))

    def test_t12_no_fabricated_recon_records(self):
        """[示意] jp 对账输入无 japan 对手方事实→不伪造 source-diff 记录(F6)。"""
        _jfacts, jrecon = fe.normalize_jp(self.p['jp'], AS_OF, 'jp_20261106.json')
        self.assertEqual(len(jrecon), 3)
        _facts, recon = fe.build_all(global_data=self.p['global'],
                                     macro_data=self.p['macro'],
                                     china_data=self.p['china'], as_of=AS_OF,
                                     jp_data=self.p['jp'])
        blob = json.dumps(recon, ensure_ascii=False)
        for mid in ('JP_POLICY_RATE', 'JGB10Y', 'JGB2Y'):
            self.assertNotIn(mid, blob, mid)            # 无对手方=无对账结论


# ══ 技术要点④: Gate A 对新指标裁决 ══════════════════════════════════
class TestGateA(unittest.TestCase):

    def setUp(self):
        self.p = fixt.collector_payloads(YMD, OBS)

    def test_t13_present_pass_counted_missing_flipped(self):
        """[示意] 在场→计数与缺席判定; GAP08-F3 映射落地后缺席自 boundary
        转入 noncore_missing——japan 事实补齐→13 指标缺席收敛至 fixture
        诚实缺席的 3 项(DAX/CAC40/JP_CPI, 采集遗漏口径)。"""
        facts = _us_jp_ea_facts(self.p)
        rec1 = rp.recompute_gate_a(_gate_payload(facts))
        present1 = {f['metric_id'] for f in facts}
        self.assertEqual(set(JP13) - present1,
                         {'JP_POLICY_RATE', 'JGB2Y', 'JGB5Y', 'JGB10Y',
                          'JP_CPI_TOKYO_YOY', 'DAX', 'CAC40'})
        for mid in JP13:
            if mid in present1:
                self.assertNotIn(mid, rec1['noncore_missing'], mid)
            else:
                self.assertIn(mid, rec1['noncore_missing'], mid)  # F3 翻转面
        b1 = [b for b in rec1.get('noncore_missing_boundary', [])
              if any(mid in b for mid in JP13)]
        # GAP08 前=7(japan 权属4+诚实缺席3)走 boundary;F3 后边界清空
        self.assertEqual(len(b1), 0)
        rec2 = rp.recompute_gate_a(_gate_payload(facts + _japan_facts()))
        b2 = [b for b in rec2.get('noncore_missing_boundary', [])
              if any(mid in b for mid in JP13)]
        self.assertEqual(len(b2), 0)   # GAP08 前=3→现 noncore_missing
        # fixture 诚实缺席: DAX/CAC40(ea prices 节键不出现)+
        # JP_CPI_TOKYO_YOY(jp inflation 节键不出现)→采集遗漏
        self.assertEqual(set(JP13) & set(rec2['noncore_missing']),
                         {'JP_CPI_TOKYO_YOY', 'DAX', 'CAC40'})
        for mid in JP13:
            self.assertNotIn(mid, rec2['noncore_fail'], mid)
        self.assertEqual(rec2['core_missing'], [])
        present = {f['metric_id'] for f in facts} | {'JP_POLICY_RATE', 'JGB2Y',
                                                     'JGB5Y', 'JGB10Y'}
        self.assertEqual(set(JP13) - present,
                         {'JP_CPI_TOKYO_YOY', 'DAX', 'CAC40'})

    def test_t14_absent_noncore_missing_after_mapping(self):
        """[示意] 缺席→GAP08-F3 映射后=noncore_missing 采集遗漏(来源文件在场);
        GAP08 前=13 条'无法映射采集通道'boundary 记录(前后值登记 DELIVERY §五)。"""
        rec = rp.recompute_gate_a(_gate_payload(_us_face_facts(self.p)))
        boundary = [b for b in rec.get('noncore_missing_boundary', [])
                    if any(mid in b for mid in JP13)]
        self.assertEqual(len(boundary), 0)             # 前=13(无法映射采集通道)
        self.assertEqual(set(JP13), set(rec['noncore_missing']) & set(JP13))
        self.assertEqual(rec['noncore_missing_detail']['NIKKEI225'],
                         '来源文件在场而指标缺席(采集遗漏)')
        self.assertEqual(rec['noncore_missing_detail']['ECB_MRO'],
                         '来源文件在场而指标缺席(采集遗漏)')

    def test_t15_bad_value_noncore_fail(self):
        """[示意] 坏值(超注册表 range)→合法 FAIL→noncore_fail, effective≤DEGRADED。"""
        p = copy.deepcopy(self.p)
        p['jp']['prices']['NIKKEI225']['close'] = 999999.0
        facts = _us_jp_ea_facts(p) + _japan_facts()
        rec = rp.recompute_gate_a(_gate_payload(facts))
        self.assertIn('NIKKEI225', rec['noncore_fail'])
        self.assertGreaterEqual(rec['counts']['FAIL'], 1)
        self.assertEqual(rec['effective'], 'DEGRADED')  # 非核心FAIL降级披露


# ══ 要点②③: 快照 sources_status 与 W-3 零回归 ═══════════════════════
class TestSnapshotSourcesStatus(unittest.TestCase):

    def _snap(self, td, drop=()):
        fixt.write_collectors(td, YMD)
        for name in drop:
            os.remove(os.path.join(td, f'{name}_{YMD}.json'))
        return sb.build_snapshot(target_ymd=YMD, data_dir=td, out_dir=td,
                                 trusted_root=td, as_of=AS_OF)

    def test_t16_sources_status_jp_ea_keys(self):
        """[示意] 真实 build_snapshot: sources_status 含 jp/ea 键(EXACT);
        GAP08-F3+F1 后缺席=3 项 noncore_missing(fixture 诚实缺席,
        快照级), gate DEGRADED(前=13 条 boundary+PASS)。"""
        with tempfile.TemporaryDirectory() as td:
            snap = self._snap(td)
            ss = snap['sources_status']
            self.assertEqual(ss['jp']['status'], 'EXACT')
            self.assertEqual(ss['jp']['file'], 'jp_20261106.json')
            self.assertEqual(ss['jp']['file_date'], '20261106')
            self.assertEqual(ss['ea']['status'], 'EXACT')
            self.assertEqual(ss['ea']['file'], 'ea_20261106.json')
            self.assertEqual(ss['japan']['status'], 'EXACT')
            boundary = snap['gate_a'].get('noncore_missing_boundary', [])
            self.assertEqual(len(boundary), 0)         # 前=13;F3 后转入缺失清单
            self.assertEqual(set(JP13) & set(snap['gate_a']['noncore_missing']),
                             {'JP_CPI_TOKYO_YOY', 'DAX', 'CAC40'})
            self.assertEqual(snap['gate_a']['status'], 'DEGRADED')

    def test_t17_missing_ea_source(self):
        """[示意] 缺源: ea 文件缺席→sources_status['ea']={'status':'MISSING'}。"""
        with tempfile.TemporaryDirectory() as td:
            snap = self._snap(td, drop=('ea',))
            ss = snap['sources_status']
            self.assertEqual(ss['ea'], {'status': 'MISSING'})
            self.assertEqual(ss['jp']['status'], 'EXACT')   # 他通道不受影响

    def test_t18_w3_us_face_zero_regression(self):
        """[示意] W-3 对照: 7通道 vs 基线4通道(无 jp_/ea_/japan_)——
        US 面 facts/quality/noncore_missing 全等;GAP08-F1 接线后 7通道恰
        多 10 条 jp/ea/japan 事实, gate 同级 DEGRADED(F3 缺席披露口径
        翻转, 非 US 面劣化), 差异仅新增通道来源键。"""
        def _us(fls):
            return [f for f in fls if f['metric_id'] not in JP13]
        with tempfile.TemporaryDirectory() as tda, \
                tempfile.TemporaryDirectory() as tdb:
            snapa = self._snap(tda)
            snapb = self._snap(tdb, drop=('jp', 'ea', 'japan'))
            self.assertEqual(_us(snapa['facts']), _us(snapb['facts']))
            self.assertEqual(fe.snapshot_quality_grade(_us(snapa['facts'])),
                             fe.snapshot_quality_grade(_us(snapb['facts'])))
            self.assertEqual(len(snapa['facts']) - len(_us(snapa['facts'])), 10)
            self.assertEqual(snapa['gate_a']['status'],
                             snapb['gate_a']['status'])   # 均 DEGRADED(前均 PASS)
            self.assertEqual([m for m in snapa['gate_a']['noncore_missing']
                              if m not in JP13],
                             [m for m in snapb['gate_a']['noncore_missing']
                              if m not in JP13])
            self.assertEqual(set(JP13) & set(snapa['gate_a']['noncore_missing']),
                             {'JP_CPI_TOKYO_YOY', 'DAX', 'CAC40'})
            self.assertEqual(set(JP13) & set(snapb['gate_a']['noncore_missing']),
                             set(JP13))                    # 4通道=来源级缺失13项
            for ch in ('global', 'macro', 'china', 'rate_economy'):
                self.assertEqual(snapa['sources_status'][ch],
                                 snapb['sources_status'][ch], ch)
            self.assertEqual(snapa['sources_status']['jp']['status'], 'EXACT')
            # 通道键恒在场: 文件缺席→MISSING(如实, 不静默隐藏通道)
            self.assertEqual(snapb['sources_status']['jp'], {'status': 'MISSING'})
            self.assertEqual(snapb['sources_status']['ea'], {'status': 'MISSING'})
            self.assertEqual(snapb['sources_status']['japan'], {'status': 'MISSING'})


# ══ (e) 触面锁 + 真实首档[实取] ═════════════════════════════════════
class TestRegistryAndRealArchive(unittest.TestCase):

    def test_t19_registry_single_field_bump(self):
        """[实取] NIKKEI225 range=[5000,150000] 单字段调整锁(其余字段/版本零变化)。"""
        with open(os.path.join(ROOT, 'config', 'metric_registry.json'),
                  encoding='utf-8') as f:
            reg = json.load(f)
        m = {x['metric_id']: x for x in reg['metrics']}['NIKKEI225']
        self.assertEqual(m['validation']['range'], [5000, 150000])
        self.assertEqual(m['validation']['max_week_pct_move'], 25)
        self.assertEqual(m['calendar'], 'japan')
        self.assertEqual(m['source'], 'jp_market_collector')
        # IA-P1-WP-E v1.3 域化(§十三.1 从属锁迁移): 2.2.0→2.3.0/94→102
        # (WP-B 单字段≠版本变更原则不变;本值=WP-E 结构变更[+8 条目]所递增)
        # Charter6-P2(2026-11-09): 2.5.0→2.6.0(+SPX_CAPE/SPX_PE_TTM/SPX_PB)
        self.assertEqual(reg['version'], '2.6.0')
        self.assertEqual(len(reg['metrics']), 106)  # Charter6-P2: +SPX_CAPE/SPX_PE_TTM/SPX_PB
        # 上限余量=同侪带中段(SPX 3.96×/NDX 2.13×先例; REPORT §零.11.1)
        self.assertGreater(m['validation']['range'][1], 61077.9)

    def test_t20_real_first_archive_smoke(self):
        """[实取] WP-A 真实首档冒烟: jp_20261105(NIKKEI=61077.9 PASS+对账3条)/
        ea_20261105(ECB_MRO=2.65, 滞后50天→DEGRADED 如实降级)。"""
        jp_path = os.path.join(ROOT, 'data', 'daily', 'jp_20261105.json')
        ea_path = os.path.join(ROOT, 'data', 'daily', 'ea_20261105.json')
        if not (os.path.isfile(jp_path) and os.path.isfile(ea_path)):
            self.skipTest('真实首档缺席(WP-A 步骤⑪ 交付物)')
        with open(jp_path, encoding='utf-8') as f:
            jpf, jpr = fe.normalize_jp(json.load(f), '2026-11-05T20:00:00+08:00',
                                       'jp_20261105.json')
        by_id = {x['metric_id']: x for x in jpf}
        self.assertEqual(by_id['NIKKEI225']['value'], 61077.9)
        self.assertEqual(by_id['NIKKEI225']['observation_date'], '2026-11-05')
        self.assertEqual(by_id['NIKKEI225']['quality_status'], 'PASS')
        self.assertNotIn('JP_CPI_TOKYO_YOY', by_id)     # inflation=null 诚实缺席
        self.assertEqual({r['metric_id'] for r in jpr},
                         {'JP_POLICY_RATE', 'JGB10Y', 'JGB2Y'})
        rmap = {r['metric_id']: r['value'] for r in jpr}
        self.assertEqual(rmap['JP_POLICY_RATE'], 1.043)
        self.assertEqual(rmap['JGB10Y'], 2.855)
        self.assertEqual(rmap['JGB2Y'], 1.891)
        with open(ea_path, encoding='utf-8') as f:
            eaf, ear = fe.normalize_ea(json.load(f), '2026-11-05T20:00:00+08:00',
                                       'ea_20261105.json')
        self.assertEqual([x['metric_id'] for x in eaf], ['ECB_MRO'])
        mro = eaf[0]
        self.assertEqual(mro['value'], 2.65)
        self.assertEqual(mro['observation_date'], '2026-09-16')
        self.assertEqual(mro['quality_status'], 'DEGRADED')
        self.assertTrue(any('滞后50天' in i['message'] for i in mro['issues']))
        self.assertEqual(ear, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
