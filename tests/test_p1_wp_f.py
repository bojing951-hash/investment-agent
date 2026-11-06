#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P1-WP-F 验收件: DESIGN §六 L174 + §八.1 L212-L217 验收要点①②③+范围3查询面。

① 比较视图=纯快照/事实/评分卡消费面,零直读采集档【测试】——毒丸负向:
   采集档在场(含毒丸标记)与缺席两变体视图逐字节等值+毒丸标记零出现;
② 四经济体并置+缺席如实【测试】——US(总分 int)/CN/JP(总分 None→数据不足)/
   EA(评分卡缺席→未生成行在场,禁跳行);关键事实缺席→「无数据」不填0;
   EA 评分卡缺席而快照事实在场=关键事实仍如实呈现(评分卡与事实两源独立);
③ 既有 US 面零回归【测试/CI】——视图构建对 fixture daily/ 只读(sha256 前后
   不变+目录清单不变,零评分卡写入);全套件级零回归=本地 CI 逐套件记录;
范围3 查询比较面(L199)——comparison_query 逐经济体 economy 过滤(W-1/W-2 型):
   命中=窗口/不命中=上游如实空窗语义/payload 缺席=「无数据」。

数据纪律(R014-D3/R022): 合成 fixture=唯一数据源(全部 tempfile 临时目录,零读
真实 data/daily/);期望值独立手算硬编码[示意],禁自证(不 import 实现侧计算结果
充当期望);零网络零 GLM 零凭证零第三方新依赖。定值源=docs/P1_WP_F_REPORT.md §零.5/§零.6。
fixture→期望值映射: 本文件 make_fixture_* 工厂(逐断言组可追溯,DELIVERY 漂移
维护专节登记表同源)。
"""
import hashlib
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import economy_comparison_view as ecv    # noqa: E402  (被测模块=IA-P1-WP-F 交付件)

YMD = '20990101'                    # [示意] 合成观察日(与真实日历无关)
POISON = 'POISON_XR71_MARKER'       # [示意] 采集档毒丸标记(直读即泄漏)

DISCLAIMER_LITERAL = ("评分卡=内部模型观点(阈值为模型假设),非客观事实;"
                      "体制结论为二维映射的机械输出,须结合证据分级使用")  # macro_scorecard L32-33 实读

# ══ 合成 fixture 工厂(唯一数据源;全部[示意]) ═══════════════════════════

def _us_scorecard():
    return {'date': YMD, 'growth_total': 2, 'inflation_total': 3,
            'regime': 'Reflation', 'confirmed_regime': 'Reflation',
            'regime_status': 'confirmed', 'economy_note': 'fixture'}

def _nonus_scorecard(econ):
    # 非 US 真实形态(macro_scorecard L594-L606: 阈值仅 US→维度空→total=None,
    # regime=数据不足不可判, regime_status=data_insufficient)
    return {'date': YMD, 'growth_total': None, 'inflation_total': None,
            'regime': '数据不足不可判', 'confirmed_regime': '数据不足不可判',
            'regime_status': 'data_insufficient', 'economy': econ}

def _snapshot_facts(with_ea=True):
    facts = [
        {'metric_id': 'DFEDTARL', 'value': 3.75, 'observation_date': '2098-12-20'},
        {'metric_id': 'CPI', 'value': 320.5, 'observation_date': '2098-12-15',
         'derived': {'m12': {'available': True, 'pct_change': 2.6}}},
        {'metric_id': 'CN_LPR_1Y', 'value': 3.1, 'observation_date': '2098-12-20'},
        {'metric_id': 'CN_CPI_YOY', 'value': 0.3, 'observation_date': '2098-12-09'},
        {'metric_id': 'JP_POLICY_RATE', 'value': 0.5, 'observation_date': '2098-12-18'},
        {'metric_id': 'JP_CPI_TOKYO_YOY', 'value': 1.8, 'observation_date': '2098-11-29'},
    ]
    if with_ea:
        facts += [{'metric_id': 'ECB_DFR', 'value': 2.0, 'observation_date': '2098-12-15'},
                  {'metric_id': 'EA_HICP_YOY', 'value': 2.2, 'observation_date': '2098-12-31'}]
    return facts

def _series_store(with_eurusd=True):
    # 收益率手工构造[示意]: NIKKEI 日收益 [0.10,0.05,-0.02], USDJPY=2×→corr=+1;
    # DAX 日收益 [0.02,-0.01,0.015], EURUSD=-1×→corr=-1(手算,非模块生成)
    store = {
        'NIKKEI225': {'dates': ['2099-01-02', '2099-01-03', '2099-01-04', '2099-01-05'],
                      'values': [100, 110.0, 115.5, 113.19]},
        'USDJPY': {'dates': ['2099-01-02', '2099-01-03', '2099-01-04', '2099-01-05'],
                   'values': [150, 180.0, 198.0, 190.08]},
        'DAX': {'dates': ['2099-01-02', '2099-01-03', '2099-01-04', '2099-01-05'],
                'values': [2000, 2040.0, 2019.6, 2049.894]},
    }
    if with_eurusd:
        store['EURUSD'] = {'dates': ['2099-01-02', '2099-01-03', '2099-01-04', '2099-01-05'],
                           'values': [1.1, 1.078, 1.08878, 1.0724483]}
    return store

def make_fixture(with_collectors=False, with_ea_scorecard=False, with_ea_facts=True,
                 with_snapshot=True, with_eurusd=True):
    """合成 fixture 工厂: 返回 (data_root, daily_dir)——唯一数据源,零真实档。"""
    data_root = tempfile.mkdtemp(prefix='p1wpf_')
    daily = os.path.join(data_root, 'daily')
    os.makedirs(daily)
    with open(os.path.join(daily, f'scorecard_{YMD}.json'), 'w', encoding='utf-8') as f:
        json.dump(_us_scorecard(), f)
    for econ in ('CN', 'JP') + (('EA',) if with_ea_scorecard else ()):
        with open(os.path.join(daily, f'economy_scorecard_{econ.lower()}_{YMD}.json'),
                  'w', encoding='utf-8') as f:
            json.dump(_nonus_scorecard(econ), f)
    if with_snapshot:
        snap = {'snapshot_id': f'research_snapshot_{YMD}', 'target_date': YMD,
                'facts': _snapshot_facts(with_ea_facts),
                'series_store': _series_store(with_eurusd)}
        with open(os.path.join(daily, f'research_snapshot_{YMD}.json'), 'w',
                  encoding='utf-8') as f:
            json.dump(snap, f)
    if with_collectors:
        # 毒丸采集档(要点①负向): 若视图直读采集档,毒丸标记必泄漏进产物
        for ch in ('global', 'china', 'jp', 'ea', 'macro', 'rate_economy'):
            with open(os.path.join(daily, f'{ch}_{YMD}.json'), 'w', encoding='utf-8') as f:
                json.dump({'data': {'poison': POISON}}, f)
    return data_root, daily

def _sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


# ══ 要点① 零直读采集档(毒丸负向+双变体等值) ═══════════════════════════

class TestAcceptance1ZeroDirectRead(unittest.TestCase):

    def test_collector_presence_changes_nothing(self):
        """采集档在场/缺席两变体→视图逐字节等值(剔除墙钟 generated_at)。"""
        root_a, _ = make_fixture(with_collectors=True)
        root_b, _ = make_fixture(with_collectors=False)
        try:
            va = ecv.build_comparison_view(YMD, data_dir=root_a)
            vb = ecv.build_comparison_view(YMD, data_dir=root_b)
            va.pop('generated_at'), vb.pop('generated_at')
            self.assertEqual(json.dumps(va, sort_keys=True, ensure_ascii=False),
                             json.dumps(vb, sort_keys=True, ensure_ascii=False))
        finally:
            import shutil
            shutil.rmtree(root_a, ignore_errors=True)
            shutil.rmtree(root_b, ignore_errors=True)

    def test_poison_marker_never_leaks(self):
        """毒丸标记零出现于视图 dict 与渲染 md(直读即红)。"""
        root, _ = make_fixture(with_collectors=True)
        try:
            view = ecv.build_comparison_view(YMD, data_dir=root)
            md = ecv.render_comparison_markdown(view)
            self.assertNotIn(POISON, json.dumps(view, ensure_ascii=False))
            self.assertNotIn(POISON, md)
        finally:
            import shutil
            shutil.rmtree(root, ignore_errors=True)

    def test_module_source_offline(self):
        """静态面: 被测模块源码零网络库 import(AC-05.4)。"""
        src_path = os.path.join(ROOT, 'scripts', 'economy_comparison_view.py')
        with open(src_path, 'r', encoding='utf-8') as f:
            src = f.read()
        for banned in ('import requests', 'import urllib', 'import socket',
                       'import http', 'subprocess'):
            self.assertNotIn(banned, src, f"被测模块含禁用面: {banned}")


# ══ 要点② 四经济体并置+缺席如实 ═════════════════════════════════════

class TestAcceptance2SideBySideHonestAbsence(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root, cls.daily = make_fixture()   # EA 评分卡缺席/EA 事实在场
        cls.view = ecv.build_comparison_view(YMD, data_dir=cls.root)
        cls.md = ecv.render_comparison_markdown(cls.view)

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_four_rows_never_skipped(self):
        """四行恒在场(EA 评分卡缺席也不跳行);行序=US/CN/JP/EA。"""
        self.assertEqual([r['economy'] for r in self.view['economies']],
                         ['US', 'CN', 'JP', 'EA'])

    def test_us_row_int_totals(self):
        row = next(r for r in self.view['economies'] if r['economy'] == 'US')
        self.assertEqual(row['scorecard']['growth_cell'], '+2')
        self.assertEqual(row['scorecard']['inflation_cell'], '+3')
        self.assertEqual(row['scorecard']['regime_cell'], 'Reflation')
        self.assertEqual(row['scorecard']['status_cell'], '本期在场;已确认')
        self.assertIn('| 美国(US) | +2 | +3 | Reflation | 本期在场;已确认 |', self.md)

    def test_nonus_rows_data_insufficient_not_zero(self):
        """非 US 总分=None(无评分,阈值仅 US)→「数据不足」单元格,禁 0 占位。"""
        for econ, name in (('CN', '中国'), ('JP', '日本')):
            row = next(r for r in self.view['economies'] if r['economy'] == econ)
            self.assertEqual(row['scorecard']['growth_cell'], '数据不足')
            self.assertEqual(row['scorecard']['inflation_cell'], '数据不足')
            self.assertEqual(row['scorecard']['regime_cell'], '数据不足不可判')
            self.assertEqual(row['scorecard']['status_cell'], '本期在场;数据不足')
            self.assertIn(f"| {name}({econ}) | 数据不足 | 数据不足 | 数据不足不可判 | 本期在场;数据不足 |",
                          self.md)

    def test_absent_scorecard_row_present_un_generated(self):
        row = next(r for r in self.view['economies'] if r['economy'] == 'EA')
        self.assertFalse(row['scorecard']['present'])
        self.assertEqual(row['scorecard']['status_cell'], '未生成(当日评分卡不存在)')
        self.assertIn('| 欧元区(EA) | 未生成 | 未生成 | 未生成 | 未生成(当日评分卡不存在) |',
                      self.md)
        self.assertIn('| 欧元区(EA) |', self.md)   # 禁跳过整行(两表均在场)

    def test_key_facts_grounded_literals(self):
        """关键事实行: 数值+metric@观测日接地标识(§四 L134)——期望值手算硬编码。"""
        expected = {
            'US': ('3.75%(DFEDTARL@2098-12-20)', '+2.60%(CPI@2098-12-15)'),
            'CN': ('3.10%(CN_LPR_1Y@2098-12-20)', '+0.30%(CN_CPI_YOY@2098-12-09)'),
            'JP': ('0.50%(JP_POLICY_RATE@2098-12-18)', '+1.80%(JP_CPI_TOKYO_YOY@2098-11-29)'),
            'EA': ('2.00%(ECB_DFR@2098-12-15)', '+2.20%(EA_HICP_YOY@2098-12-31)'),
        }
        for r in self.view['economies']:
            pol, inf = expected[r['economy']]
            self.assertIn(f"| {pol} |", self.md)
            self.assertIn(f"| {inf} |", self.md)

    def test_key_facts_absent_honest_no_data(self):
        """关键事实缺席变体: 「无数据」+原因,available=False/value=None(禁 0)。"""
        root, _ = make_fixture(with_ea_facts=False)
        try:
            view = ecv.build_comparison_view(YMD, data_dir=root)
            md = ecv.render_comparison_markdown(view)
            ea = next(r for r in view['economies'] if r['economy'] == 'EA')
            self.assertFalse(ea['key_facts']['policy_rate']['available'])
            self.assertIsNone(ea['key_facts']['policy_rate']['value'])
            self.assertFalse(ea['key_facts']['inflation_yoy']['available'])
            self.assertIsNone(ea['key_facts']['inflation_yoy']['value'])
            self.assertIn('无数据(快照无ECB_DFR有效事实)', md)
            self.assertIn('无数据(快照无EA_HICP_YOY有效事实)', md)
            self.assertNotIn('0.00%(ECB_DFR', md)      # 禁 0 占位
        finally:
            import shutil
            shutil.rmtree(root, ignore_errors=True)

    def test_disclaimer_carried_no_investment_advice(self):
        """DISCLAIMER 口径逐字沿用(macro_scorecard L32-33)+不构成投资建议文案。"""
        self.assertEqual(self.view['disclaimer'], DISCLAIMER_LITERAL)
        self.assertIn(DISCLAIMER_LITERAL, self.md)
        self.assertIn('不构成投资建议', self.md)


# ══ 要点③ US 面零回归(offline 面;套件级=本地 CI 逐套件) ═══════════════

class TestAcceptance3USFaceZeroRegression(unittest.TestCase):

    def test_view_build_read_only_over_daily(self):
        """视图构建对 daily/ 只读: 全目录 sha256 清单前后一致+零新档写入。"""
        root, daily = make_fixture()
        try:
            before = {n: _sha256(os.path.join(daily, n)) for n in sorted(os.listdir(daily))}
            view = ecv.build_comparison_view(YMD, data_dir=root)
            ecv.render_comparison_markdown(view)
            after = {n: _sha256(os.path.join(daily, n)) for n in sorted(os.listdir(daily))}
            self.assertEqual(before, after)
            self.assertIn(f'scorecard_{YMD}.json', before)   # US 主评分卡确在场被消费
        finally:
            import shutil
            shutil.rmtree(root, ignore_errors=True)

    def test_us_scorecard_bytes_unchanged(self):
        root, daily = make_fixture()
        try:
            p = os.path.join(daily, f'scorecard_{YMD}.json')
            h0 = _sha256(p)
            for _ in range(2):
                ecv.build_comparison_view(YMD, data_dir=root)
            self.assertEqual(_sha256(p), h0)
        finally:
            import shutil
            shutil.rmtree(root, ignore_errors=True)


# ══ 范围2 跨域对呈现(DP-F3①零新增) ═════════════════════════════════

class TestCrossDomainPairs(unittest.TestCase):

    def test_registered_parameters_frozen(self):
        """登记定值一致性(§零.5/§零.6=R011 纪律: 登记=常量;禁跑后漂移):
        经济体集/关键事实八映射/跨域对恰两元组——期望值=REPORT 登记字面量。"""
        self.assertEqual(ecv.COMPARISON_ECONOMIES, ('US', 'CN', 'JP', 'EA'))
        self.assertEqual(ecv.KEY_FACTS,
                         {'US': {'policy_rate': 'DFEDTARL', 'inflation_yoy': 'CPI',
                                 'inflation_field': 'derived_m12_pct'},
                          'CN': {'policy_rate': 'CN_LPR_1Y', 'inflation_yoy': 'CN_CPI_YOY',
                                 'inflation_field': 'value'},
                          'JP': {'policy_rate': 'JP_POLICY_RATE', 'inflation_yoy': 'JP_CPI_TOKYO_YOY',
                                 'inflation_field': 'value'},
                          'EA': {'policy_rate': 'ECB_DFR', 'inflation_yoy': 'EA_HICP_YOY',
                                 'inflation_field': 'value'}})
        self.assertEqual(tuple(ecv.CROSS_DOMAIN_PAIRS),
                         (('NIKKEI225', 'USDJPY'), ('DAX', 'EURUSD')))   # DP-F3①恰两对

    def test_exactly_two_existing_pairs(self):
        """恰呈现既有两跨域对(PAIRS L49/L51),零新增;corr=手算 ±1。"""
        root, _ = make_fixture()
        try:
            view = ecv.build_comparison_view(YMD, data_dir=root)
            pairs = view['cross_domain_pairs']
            self.assertEqual({(p['a'], p['b']) for p in pairs},
                             {('NIKKEI225', 'USDJPY'), ('DAX', 'EURUSD')})
            by_pair = {(p['a'], p['b']): p for p in pairs}
            nk, dax = by_pair[('NIKKEI225', 'USDJPY')], by_pair[('DAX', 'EURUSD')]
            self.assertAlmostEqual(nk['corr_20d'], 1.0, delta=1e-9)   # 收益 2×联动
            self.assertAlmostEqual(dax['corr_20d'], -1.0, delta=1e-9)  # 收益 -1×联动
            for p in (nk, dax):
                self.assertEqual(p['n_20d'], 3)
                self.assertEqual(p['window_first'], '2099-01-03')
                self.assertEqual(p['window_last'], '2099-01-05')
                self.assertIn('跨域配对', p['disclosure'])
            self.assertEqual(view['cross_domain_missing'], [])
            md = ecv.render_comparison_markdown(view)
            self.assertIn('日经225 vs 美元/日元', md)
            self.assertIn('德国DAX vs 欧元/美元', md)
        finally:
            import shutil
            shutil.rmtree(root, ignore_errors=True)

    def test_series_absent_honest_missing(self):
        """序列缺席变体: 该对进缺席披露(如实列示),不造数。"""
        root, _ = make_fixture(with_eurusd=False)
        try:
            view = ecv.build_comparison_view(YMD, data_dir=root)
            self.assertEqual({(p['a'], p['b']) for p in view['cross_domain_pairs']},
                             {('NIKKEI225', 'USDJPY')})
            self.assertTrue(any('序列缺失' in m for m in view['cross_domain_missing']))
        finally:
            import shutil
            shutil.rmtree(root, ignore_errors=True)

    def test_snapshot_absent_no_data_section(self):
        """快照缺席变体: 跨域节整体「无数据」,评分卡行仍独立呈现(消费面不中断)。"""
        root, _ = make_fixture(with_snapshot=False)
        try:
            view = ecv.build_comparison_view(YMD, data_dir=root)
            self.assertFalse(view['data_basis']['snapshot_available'])
            self.assertEqual(view['cross_domain_pairs'], [])
            self.assertTrue(any('快照缺席' in m for m in view['cross_domain_missing']))
            self.assertIn('无数据', ecv.render_comparison_markdown(view))
            self.assertEqual(len(view['economies']), 4)
            for r in view['economies']:
                kf = r['key_facts']
                self.assertFalse(kf['policy_rate']['available'])
                self.assertFalse(kf['inflation_yoy']['available'])
        finally:
            import shutil
            shutil.rmtree(root, ignore_errors=True)


# ══ 范围3 查询比较面(W-1/W-2 型;复用上游 query_window economy 过滤) ═══

class TestComparisonQuery(unittest.TestCase):

    @staticmethod
    def _payloads():
        # [示意] W-1 型: 政策利率序列双经济体并置查询
        return {
            'US': {'metric_id': 'DFEDTARL', 'economy': 'US',
                   'dates': ['2098-12-01', '2098-12-15', '2099-01-02', '2099-01-03'],
                   'values': [1.0, 2.0, 3.0, 4.0]},
            'EA': {'metric_id': 'ECB_DFR', 'economy': 'EA',
                   'dates': ['2098-12-01', '2098-12-20', '2099-01-02', '2099-01-05'],
                   'values': [10.0, 11.0, 12.0, 13.0]},
        }

    def test_windows_hardcoded(self):
        out = ecv.comparison_query(self._payloads(), '2098-12-15', '2099-01-03',
                                   economies=('US', 'EA'))
        self.assertEqual(out['US']['values'], [2.0, 3.0, 4.0])        # 手算硬编码
        self.assertEqual(out['US']['coverage']['n_window'], 3)
        self.assertEqual(out['US']['coverage']['window_first'], '2098-12-15')
        self.assertEqual(out['US']['coverage']['window_last'], '2099-01-03')
        self.assertEqual(out['EA']['values'], [11.0, 12.0])
        self.assertEqual(out['EA']['coverage']['n_window'], 2)
        self.assertEqual(out['EA']['coverage']['window_first'], '2098-12-20')
        self.assertEqual(out['EA']['coverage']['window_last'], '2099-01-02')

    def test_economy_filter_miss_honest_empty(self):
        """W-2 型缺经济体: payload 在场但 economy 不匹配→上游如实空窗(不造点)。"""
        mismatched = {'metric_id': 'JP_POLICY_RATE', 'economy': 'JP',   # 请求 EA/实际 JP
                      'dates': ['2098-12-15', '2099-01-02'], 'values': [7.0, 8.0]}
        out = ecv.comparison_query({'EA': mismatched}, '2098-12-15', '2099-01-03',
                                   economies=('EA',))
        self.assertEqual(out['EA']['dates'], [])
        self.assertEqual(out['EA']['values'], [])
        self.assertFalse(out['EA']['coverage']['economy_filter']['matched'])
        self.assertIn('economy 过滤不命中', out['EA']['coverage']['note'])
        self.assertEqual(out['EA']['coverage']['economy_filter']['metric_economy'], 'JP')

    def test_missing_payload_no_data(self):
        out = ecv.comparison_query({}, '2098-12-15', '2099-01-03',
                                   economies=('JP',))
        self.assertIn('无数据', out['JP']['coverage']['note'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
