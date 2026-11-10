#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P1-GAP08 验收件: 快照接线 F1/F2/F6 + 来源映射 F3 + R47-F1/F3 消费面。

覆盖(合同 IA-P1-GAP08-WIRING-AC-v1.1 步骤8):
- F1: build_snapshot facts 级 jp/ea/japan 接线(在场景约+缺源来源级缺失如实);
- F2: series_store 增 NIKKEI225/DAX/CAC40({dates,values} 形态,值直通零造数);
- F3: _SOURCE_TO_INPUT 三键落地——来源在场而指标缺席=采集遗漏、来源文件缺失=
  来源级缺失,均入 noncore_missing(自 boundary 转入,boundary 清空);
- F6: jp 对账输入消费(有 japan 对手方→source-diff 3 条;无对手方→不伪造);
- R47-F1: RT- 任务 economy 条件写(恰单经济体→顶层键;跨经济体→不写键);
- R47-F3: rhq economy 过滤维度(ECONOMIES=registry 值域/payload echo/过滤不命中
  如实空窗/japan_rate_collector flat 无序列无接入点)。

数据纪律: 合成值显式标注[示意](fixture 值=fixt.py 权威映射,不冒充真实采集);
registry 只读实取标注[实取](config/metric_registry.json, 免登记只读面)。
期望值独立手算(禁自证: 不 import 实现侧计算结果作期望值)。零网络。
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
import research_task_manager as rtm    # noqa: E402
import research_history_query as rhq   # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixt                            # noqa: E402

# 13 新指标(权属: japan_rate_collector×4 / jp_market_collector×2 /
# ea_market_collector×7)——与 WP-B 验收件同一独立重编码
JP13 = ('JP_POLICY_RATE', 'JGB2Y', 'JGB5Y', 'JGB10Y',
        'JP_CPI_TOKYO_YOY', 'NIKKEI225',
        'ECB_DFR', 'ECB_MRO', 'BUND_10Y', 'BUND_2Y', 'EA_HICP_YOY', 'DAX', 'CAC40')

YMD = '20261106'                        # [示意] 周五快照日(与 WP-B 验收件同日)
OBS = fixt.obs_for(YMD)                 # = 2026-11-05
P7 = fixt.pday(OBS, 7)                  # = 2026-10-29
AS_OF = fixt.as_of_for(YMD)

# [示意] fixture→期望值映射(fixt.py 权威映射面, 手抄独立登记)
JP_F1_EXPECT = {                        # F1 接线后快照新增事实(恰 10 = jp1+ea5+japan4)
    'NIKKEI225': (38000.0, 'jp_market_collector'),
    'ECB_DFR': (2.00, 'ea_market_collector'),
    'ECB_MRO': (3.15, 'ea_market_collector'),
    'BUND_10Y': (2.60, 'ea_market_collector'),
    'BUND_2Y': (2.30, 'ea_market_collector'),
    'EA_HICP_YOY': (2.2, 'ea_market_collector'),
    'JP_POLICY_RATE': (0.100, 'japan_rate_collector'),
    'JGB2Y': (0.500, 'japan_rate_collector'),
    'JGB5Y': (0.900, 'japan_rate_collector'),
    'JGB10Y': (1.200, 'japan_rate_collector'),
}


def _snap(td, drop=(), global_ea_idx=False):
    """7通道 fixture 快照(drop=删除指定采集档; global_ea_idx=global 档补
    DAX/CAC40 行情——数据批1通道转正后两条目权威来源=global_market_collector,
    F2 的 DAX/CAC40 键须齐备形态驱动;ea 档不再承载两键)。"""
    fixt.write_collectors(td, YMD)
    if global_ea_idx:
        p = fixt.collector_payloads(YMD, OBS)
        glob = copy.deepcopy(p['global'])
        glob['data']['DAX'] = {'close': 21000.0, 'date': OBS,
                               'series': {'dates': [P7, OBS],
                                          'values': [20500.0, 21000.0]}}
        glob['data']['CAC40'] = {'close': 8100.0, 'date': OBS,
                                 'series': {'dates': [P7, OBS],
                                            'values': [8000.0, 8100.0]}}
        glob['count'] = len(glob['data'])
        with open(os.path.join(td, f'global_{YMD}.json'), 'w',
                  encoding='utf-8') as f:
            json.dump(glob, f, ensure_ascii=False)
    for name in drop:
        os.remove(os.path.join(td, f'{name}_{YMD}.json'))
    return sb.build_snapshot(target_ymd=YMD, data_dir=td, out_dir=td,
                             trusted_root=td, as_of=AS_OF)


def _gate(facts, ss):
    return rp.recompute_gate_a({'facts': facts, 'sources_status': ss,
                                'research_as_of': AS_OF, 'target_date': YMD})


# ══ F1: build_snapshot facts 级 jp/ea/japan 接线 ═════════════════════
class TestF1SnapshotWiring(unittest.TestCase):

    def test_g01_jp_ea_japan_facts_wired(self):
        """[示意] 7通道齐备→快照 facts 含 10 新事实, 值/权属/批次绑定全对
        (source.file=具体批次文件名, Gate A 第二层批次比对面)。"""
        with tempfile.TemporaryDirectory() as td:
            snap = _snap(td)
        by_id = {f['metric_id']: f for f in snap['facts']}
        self.assertEqual(set(JP_F1_EXPECT), set(JP13) & set(by_id))
        ffile = {'jp_market_collector': f'jp_{YMD}.json',
                 'ea_market_collector': f'ea_{YMD}.json',
                 'japan_rate_collector': f'japan_{YMD}.json'}
        for mid, (v, collector) in JP_F1_EXPECT.items():
            f = by_id[mid]
            self.assertEqual(f['value'], v, mid)
            self.assertEqual(f['source']['collector'], collector, mid)
            self.assertEqual(f['source']['file'], ffile[collector], mid)
            self.assertNotEqual(f['quality_status'], 'FAIL', mid)
        # japan 面(flat 形态适配)恰 4 事实, 观测日=档内 observations
        self.assertEqual(sum(1 for f in snap['facts']
                             if f['source']['collector'] == 'japan_rate_collector'), 4)
        # fixture 诚实缺席(jp inflation/ea prices 节键不出现)不产事实不填 0
        self.assertNotIn('JP_CPI_TOKYO_YOY', by_id)
        self.assertFalse(any(f.get('value') == 0 and f['metric_id'] in JP13
                             for f in snap['facts']))

    def test_g02_missing_source_honest_disclosure(self):
        """[示意] 缺源: jp/ea/japan 档整体缺席→MISSING+零事实+13 指标
        来源级缺失入 noncore_missing(不产 boundary 边界记录, 不造数据)。"""
        with tempfile.TemporaryDirectory() as td:
            snap = _snap(td, drop=('jp', 'ea', 'japan'))
            ss = snap['sources_status']
            for ch in ('jp', 'ea', 'japan'):
                self.assertEqual(ss[ch], {'status': 'MISSING'}, ch)
            ids = {f['metric_id'] for f in snap['facts']}
            self.assertTrue(ids.isdisjoint(set(JP13)))
            ga = snap['gate_a']
            self.assertEqual(set(JP13), set(JP13) & set(ga['noncore_missing']))
            self.assertEqual(ga['noncore_missing_detail']['NIKKEI225'],
                             '来源文件缺失(jp:MISSING)')
            self.assertEqual(ga['noncore_missing_detail']['JGB5Y'],
                             '来源文件缺失(japan:MISSING)')
            self.assertEqual(ga.get('noncore_missing_boundary', []), [])
            self.assertEqual(ga['status'], 'DEGRADED')    # 非核心缺失→至少降级


# ══ F2: series_store 三键 ═══════════════════════════════════════════
class TestF2SeriesStore(unittest.TestCase):

    def test_g03_store_three_keys_values_pass_through(self):
        """[示意] store 增 NIKKEI225/DAX/CAC40: {dates,values} 形态+值直通
        (与档内 series 逐值全等, 升序); global 池既有键零回归。
        数据批1(2026-11-10): DAX/CAC40 改经 global 档驱动(通道转正),
        值期望不变——迁移=承载文件换, 语义零变化。"""
        with tempfile.TemporaryDirectory() as td:
            snap = _snap(td, global_ea_idx=True)
            store = snap['series_store']
            self.assertEqual(store['NIKKEI225'],
                             {'dates': [P7, OBS], 'values': [37800.0, 38000.0]})
            self.assertEqual(store['DAX'],
                             {'dates': [P7, OBS], 'values': [20500.0, 21000.0]})
            self.assertEqual(store['CAC40'],
                             {'dates': [P7, OBS], 'values': [8000.0, 8100.0]})
            # 值直通复核: 档内 series 逐值回读比对(零改写零造数)
            with open(os.path.join(td, f'global_{YMD}.json'),
                      encoding='utf-8') as f:
                glob_raw = json.load(f)
            for mid in ('DAX', 'CAC40'):
                arch = glob_raw['data'][mid]['series']
                self.assertEqual({'dates': store[mid]['dates'],
                                  'values': store[mid]['values']}, arch, mid)
            self.assertIn('SPX', store)                  # global 池不受影响


# ══ F3: 来源映射三键(boundary→noncore_missing 口径翻转) ═════════════
class TestF3SourceMappingFlip(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as td:
            cls.snap = _snap(td)
        cls.ss = cls.snap['sources_status']

    def test_g04_source_present_metric_absent(self):
        """[示意] 来源文件在场而指标缺席=采集遗漏(US 面 facts+7通道在场
        sources_status 重算: 13 指标全入 noncore_missing, boundary 清空)。"""
        facts = [f for f in self.snap['facts'] if f['metric_id'] not in JP13]
        rec = _gate(facts, self.ss)
        self.assertEqual(set(JP13), set(JP13) & set(rec['noncore_missing']))
        for mid in JP13:
            self.assertEqual(rec['noncore_missing_detail'][mid],
                             '来源文件在场而指标缺席(采集遗漏)', mid)
        self.assertEqual([b for b in rec.get('noncore_missing_boundary', [])
                          if any(mid in b for mid in JP13)], [])
        self.assertEqual(rec['effective'], 'DEGRADED')

    def test_g05_source_missing_honest(self):
        """[示意] 来源文件缺失=来源级缺失(同 facts, jp/ea/japan 置 MISSING
        重算: 理由串如实区分, 不因映射键在场而虚构采集遗漏)。"""
        ss = dict(self.ss)
        for ch in ('jp', 'ea', 'japan'):
            ss[ch] = {'status': 'MISSING'}
        facts = [f for f in self.snap['facts'] if f['metric_id'] not in JP13]
        rec = _gate(facts, ss)
        self.assertEqual(set(JP13), set(JP13) & set(rec['noncore_missing']))
        self.assertEqual(rec['noncore_missing_detail']['NIKKEI225'],
                         '来源文件缺失(jp:MISSING)')
        # 数据批1(2026-11-10)通道转正迁移: DAX 权威来源自 ea→global
        # (global_market_collector)——仅置 ea=MISSING 不再使 DAX 报来源级
        # 缺失(global 档在场⇒采集遗漏口径,通道归属如实);补强化反例:
        # 连 global 一并 MISSING 时 DAX 报来源级缺失(global 面)
        self.assertEqual(rec['noncore_missing_detail']['DAX'],
                         '来源文件在场而指标缺席(采集遗漏)')
        self.assertEqual(rec['noncore_missing_detail']['JGB10Y'],
                         '来源文件缺失(japan:MISSING)')
        self.assertEqual(rec['effective'], 'DEGRADED')
        ss2 = dict(ss)
        ss2['global'] = {'status': 'MISSING'}
        rec2 = _gate(facts, ss2)
        self.assertEqual(rec2['noncore_missing_detail']['DAX'],
                         '来源文件缺失(global:MISSING)')


# ══ F6: jp 对账输入消费 ═════════════════════════════════════════════
class TestF6Reconciliation(unittest.TestCase):

    def test_g06_with_japan_counterpart_consistent(self):
        """[示意] japan 档在场→jp 对账输入逐条消费: 3 条 source-diff
        (fixture 值两通道相等→consistent, 差+0.0000, 观测日相同无附注)。"""
        with tempfile.TemporaryDirectory() as td:
            snap = _snap(td)
        recs = [r for r in snap['reconciliation']
                if 'jp通道 vs japan通道采集' in str(r.get('check', ''))]
        got = {str(r['check']).split()[-1]: r for r in recs}
        self.assertEqual(set(got), {'JP_POLICY_RATE', 'JGB10Y', 'JGB2Y'})
        for mid, r in got.items():
            self.assertEqual(r['type'], 'source-diff', mid)
            self.assertEqual(r['result'], 'consistent', mid)
            self.assertNotIn('观测日不同', r['detail'], mid)
        self.assertIn('jp=0.1 japan=0.1', got['JP_POLICY_RATE']['detail'])

    def test_g07_without_japan_counterpart_no_fabrication(self):
        """[示意] japan 档缺席( jp 对账输入在场而无对手方)→不伪造
        source-diff(F6 判定=当次事实集存在 japan 通道事实)。"""
        with tempfile.TemporaryDirectory() as td:
            snap = _snap(td, drop=('japan',))
            self.assertEqual(snap['sources_status']['jp']['status'], 'EXACT')
        blob = json.dumps(snap['reconciliation'], ensure_ascii=False)
        self.assertNotIn('jp通道 vs japan通道采集', blob)
        for mid in ('JP_POLICY_RATE', 'JGB10Y', 'JGB2Y'):
            self.assertNotIn(mid, blob, mid)            # 无对手方=无对账结论


# ══ R47-F1: RT- 任务 economy 条件写 ════════════════════════════════
class TestR47F1TaskEconomy(unittest.TestCase):

    def test_g08_task_economy_derivation(self):
        """[示意] 指标族经济体派生: 恰单值→该值; 跨经济体/零注册/零值→None。"""
        self.assertEqual(rtm._task_economy(['NIKKEI225', 'JGB10Y']), 'JP')
        self.assertEqual(rtm._task_economy(['TIPS_10Y', 'UST_10Y']), 'US')
        self.assertIsNone(rtm._task_economy(['TIPS_10Y', 'GOLD_F']))   # US×GLOBAL
        self.assertIsNone(rtm._task_economy([]))
        self.assertIsNone(rtm._task_economy(['ZZZ_UNREGISTERED']))

    def test_g09_build_task_conditional_write(self):
        """[示意] 默认任务(TIPS_10Y US+GOLD_F GLOBAL)→不写 economy 键;
        同经济体指标族(UST_10Y+UST_2Y, 经模块级指标替换)→写 economy=US;
        schema 最低字段集不受条件写影响。"""
        det = {'rule_id': 'RD-DIV-001',
               'params': {'rolling_window': 20, 'corr_threshold': 0.5,
                          'rate_bp_threshold': 50, 'gold_pct_threshold': 2.0},
               'triggered': False, 'trigger_points': [],
               'alignment': {'rule': '日频共同观测日内连接', 'n_common': 0},
               'summary': {'n_common': 0, 'n_scored': 0, 'n_triggered': 0,
                           'last': None},
               'series': []}
        pay = {'source': {'access_point': 'ap', 'file': 'f.json',
                          'file_date': YMD, 'sha256': 'x'},
               'quality_status': 'PASS', 'observation_date': OBS,
               'unit': 'percent', 'value': 1.0, 'series_clean': {}}
        task = rtm.build_task('2026-10-01', '2026-10-31', det,
                              dict(pay), dict(pay))
        self.assertNotIn('economy', task)                # 跨经济体=如实无单维度
        for k in rtm.SCHEMA_MIN_FIELDS:
            self.assertIn(k, task, k)
        orig = (rtm.RATE_METRIC, rtm.GOLD_METRIC)
        try:
            rtm.RATE_METRIC, rtm.GOLD_METRIC = 'UST_10Y', 'UST_2Y'
            task2 = rtm.build_task('2026-10-01', '2026-10-31', det,
                                   dict(pay), dict(pay))
        finally:
            rtm.RATE_METRIC, rtm.GOLD_METRIC = orig
        self.assertEqual(task2['economy'], 'US')
        self.assertEqual(task2['indicators'], ['UST_10Y', 'UST_2Y'])


# ══ R47-F3: rhq economy 过滤维度+覆盖面 ════════════════════════════
class TestR47F3RhqEconomy(unittest.TestCase):

    def test_g10_economies_equal_registry_domain(self):
        """[实取] ECONOMIES(rt- 侧 RT_ECONOMIES 同集)=registry economy
        字段实测值域(只读重算, 免登记只读面)。"""
        with open(os.path.join(ROOT, 'config', 'metric_registry.json'),
                  encoding='utf-8') as f:
            reg = json.load(f)
        econs = {m.get('economy') for m in reg['metrics']
                 if isinstance(m.get('economy'), str) and m.get('economy')}
        self.assertEqual(econs, set(rhq.ECONOMIES))
        self.assertEqual(set(rtm.RT_ECONOMIES), set(rhq.ECONOMIES))

    def test_g11_payload_economy_echo_and_jp_access(self):
        """[示意] payload 附 economy echo; jp 通道价格序列经快照接入点载入
        (jp_/ea_ 档禁直读), macro 通道既有接入点不变。"""
        with tempfile.TemporaryDirectory() as td:
            fixt.write_collectors(td, YMD)
            nk = rhq.load_metric_series('NIKKEI225', YMD, data_dir=td,
                                        trusted_root=td, as_of=AS_OF)
            tips = rhq.load_metric_series('TIPS_10Y', YMD, data_dir=td,
                                          trusted_root=td, as_of=AS_OF)
        self.assertEqual(nk['economy'], 'JP')
        self.assertEqual(nk['unit'], 'index_point')
        self.assertIn('series_store', nk['source']['access_point'])
        self.assertEqual(nk['source']['file'], f'jp_{YMD}.json')
        self.assertEqual(nk['dates'], [P7, OBS])
        self.assertEqual(nk['values'], [37800.0, 38000.0])
        self.assertEqual(tips['economy'], 'US')
        self.assertIn('normalize_macro', tips['source']['access_point'])
        self.assertIsNotNone(tips['quality_status'])

    def test_g12_query_window_economy_filter(self):
        """[示意] economy 过滤: 命中=正常窗口; 不命中=如实空窗+披露(不造点);
        None=不过滤(既有行为)。"""
        with tempfile.TemporaryDirectory() as td:
            fixt.write_collectors(td, YMD)
            nk = rhq.load_metric_series('NIKKEI225', YMD, data_dir=td,
                                        trusted_root=td, as_of=AS_OF)
        w_hit = rhq.query_window(nk, P7, OBS, economy='JP')
        self.assertEqual(w_hit['dates'], [P7, OBS])
        self.assertEqual(w_hit['coverage']['n_window'], 2)
        w_none = rhq.query_window(nk, P7, OBS, economy=None)
        self.assertEqual(w_none['coverage']['n_window'], 2)
        w_miss = rhq.query_window(nk, P7, OBS, economy='US')
        self.assertEqual(w_miss['dates'], [])
        self.assertEqual(w_miss['values'], [])
        cov = w_miss['coverage']
        self.assertEqual(cov['n_window'], 0)
        self.assertEqual(cov['economy_filter'],
                         {'requested': 'US', 'metric_economy': 'JP',
                          'matched': False})
        self.assertIn('过滤不命中', cov['note'])

    def test_g13_japan_rate_no_series_access_point(self):
        """[示意] japan_rate_collector 类=flat 单点无序列→无历史查询接入点
        (ValueError 如实, 不绕开快照直读 japan_ 档)。"""
        with self.assertRaises(ValueError) as cm:
            rhq.load_metric_series('JGB10Y', YMD)
        self.assertIn('japan_rate_collector', str(cm.exception))
        self.assertIn('无历史查询接入点', str(cm.exception))


if __name__ == '__main__':
    unittest.main(verbosity=2)
