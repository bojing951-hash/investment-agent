#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P1-WP-C 验收件: DESIGN §六 L171 验收要点①②③。

① 维度扩展单测+DATA_INSUFFICIENT 负向【测试】——score_growth/score_inflation
   economy 参数化(DP-3): 非US如实缺失(不杜撰阈值/不以0占位)+US零回归+负向敏感度;
② 数据包经济体节渲染快照测试【测试】——build_markdown「经济体观察」节:
   四经济体行序/五列/缺席披露/通道披露/节位置;
③ Gate B 对新锚点全量核验用例【测试/CI】——build_anchors对USDJPY/EURUSD(global
   支路,自动覆盖)锚点族+身份核验MAPPED;NIKKEI225/DAX(facts接线延后=无锚点,
   WP-B F1)域外锚点fail-closed=UNVERIFIED(SOURCE_MISMATCH)——负向敏感度。

数据纪律: 合成值全部显式发明并标注[示意], 不冒充真实; 期望值独立手算硬编码,
禁自证(不 import 实现侧计算结果充当期望); 零网络零GLM零凭证(t13对_call_glm
打桩捕获prompt, 不触网)。定值源=docs/P1_WP_C_REPORT.md §零.6/§零.7。
"""
import json
import os
import sys
import tempfile
import types
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import correlation_calculator as cc    # noqa: E402
import data_assembler as da            # noqa: E402
import data_validator as dv            # noqa: E402
import fact_engine as fe               # noqa: E402
import freshness_policy as fp          # noqa: E402
import macro_scorecard as ms           # noqa: E402
import snapshot_builder as sb          # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixt                            # noqa: E402

YMD = '20260109'                       # [示意] 周五研究日(与WP-B套件同日)
LEGACY_KEYS = {'date', 'disclaimer', 'data_basis', 'growth_scores', 'growth_total',
               'growth_missing', 'inflation_scores', 'inflation_total',
               'inflation_missing', 'regime', 'regime_description',
               'confirmed_regime', 'regime_status', 'max_confidence',
               'pending_regime', 'regime_drivers', 'regime_counterfactuals',
               'regime_switch_rule', 'sensitivity_note'}


def _fact(mid, value, obs, derived=None):
    """[示意] 最小合成fact(仅含被测消费字段)。"""
    f = {'metric_id': mid, 'value': value, 'observation_date': obs}
    if derived:
        f['derived'] = derived
    return f


def _us_full_facts():
    """[示意] US全量合成facts——期望得分独立手算:
    增长: UMCSENT 75.0水平→0(60≤v<80) | UNEMPLOYMENT m3 pp +0.20→0(>-0.1且≤0.3)
          | RSAFS m1 pct +0.75→1(0.5≤v<1) | INDPRO m1 pct +0.20→0(<0.3) ⇒ 总分+1
    通胀: CORE_CPI m12 pct 2.20→0(2≤v<2.5) | BEI_10Y 2.45水平→1(2.3≤v<2.6)
          | WTI_F 75.0水平→1(70≤v<90) | AHE m12 pct 4.00→1(3.5≤v<4.5) ⇒ 总分+3"""
    return [
        _fact('UMCSENT', 75.0, '2025-12-01'),
        _fact('UNEMPLOYMENT', 4.2, '2025-12-01',
              {'m3': {'pp_change': 0.20}}),
        _fact('RSAFS', 745021.0, '2025-12-01',
              {'m1': {'pct_change': 0.75}}),
        _fact('INDPRO', 103.95, '2025-12-01',
              {'m1': {'pct_change': 0.20}}),
        _fact('CORE_CPI', 306.0, '2025-12-01',
              {'m12': {'pct_change': 2.20}}),
        _fact('BEI_10Y', 2.45, '2026-01-08'),
        _fact('WTI_F', 75.0, '2026-01-08'),
        _fact('AHE', 37.81, '2025-12-01',
              {'m12': {'pct_change': 4.00}}),
    ]


def _build_day(root, ymd=YMD):
    """fixture齐备研究日(真实路径): 7通道采集+真实build_snapshot落盘。"""
    daily = os.path.join(root, 'data', 'daily')
    os.makedirs(daily, exist_ok=True)
    fixt.write_collectors(daily, ymd)
    snap = sb.build_snapshot(target_ymd=ymd, data_dir=daily, out_dir=daily,
                             trusted_root=root, as_of=fixt.as_of_for(ymd))
    return snap, os.path.join(root, 'data'), daily


class T01T03NonUSEconomyHonestMissing(unittest.TestCase):
    """要点①: 非US经济体维度评分=如实缺失+DATA_INSUFFICIENT(不杜撰/不0占位)。"""

    def test_01_growth_non_us_honest_missing(self):
        for econ in ('JP', 'EA', 'CN'):
            scores, total, missing = ms.score_growth(_us_full_facts(), economy=econ)
            self.assertEqual(scores, {}, f"{econ}: 非US增长维度不得给任何得分")
            self.assertIsNone(total, f"{econ}: 非US增长总分=None(无评分,非0)")
            self.assertEqual([m['metric_id'] for m in missing],
                             ['UMCSENT', 'UNEMPLOYMENT', 'RSAFS', 'INDPRO'])
            for m in missing:
                self.assertIn(econ, m['reason'])
                self.assertIn('如实计缺失', m['reason'])

    def test_03_inflation_non_us_honest_missing(self):
        for econ in ('JP', 'EA', 'CN'):
            scores, total, missing = ms.score_inflation(_us_full_facts(), economy=econ)
            self.assertEqual(scores, {})
            self.assertIsNone(total)
            self.assertEqual([m['metric_id'] for m in missing],
                             ['CORE_CPI', 'BEI_10Y', 'WTI_F', 'AHE'])
            for m in missing:
                self.assertIn(econ, m['reason'])

    def test_02_us_zero_regression(self):
        facts = _us_full_facts()
        # 默认调用(既有签名形态)与显式economy='US'逐键相等
        d_scores, d_total, d_missing = ms.score_growth(facts)
        e_scores, e_total, e_missing = ms.score_growth(facts, economy='US')
        self.assertEqual((d_scores, d_total, d_missing), (e_scores, e_total, e_missing))
        # 硬编码期望值(手算, 见_us_full_facts文档)
        self.assertEqual({k: v['score'] for k, v in e_scores.items()},
                         {'consumer_confidence': 0, 'unemployment_change': 0,
                          'retail_sales_mom': 1, 'industrial_production': 0})
        self.assertEqual(e_total, 1)
        self.assertEqual(e_missing, [])
        i_scores, i_total, i_missing = ms.score_inflation(facts, economy='US')
        self.assertEqual({k: v['score'] for k, v in i_scores.items()},
                         {'core_cpi_yoy': 0, 'bei_10y': 1, 'wti_oil': 1, 'ahe_yoy': 1})
        self.assertEqual(i_total, 3)
        self.assertEqual(i_missing, [])
        # 部分缺失路径零回归: 只给UMCSENT ⇒ 可用1项<2, 其余进missing(US既有机制)
        p_scores, p_total, p_missing = ms.score_growth([_fact('UMCSENT', 75.0, '2025-12-01')])
        self.assertEqual({k: v['score'] for k, v in p_scores.items()},
                         {'consumer_confidence': 0})
        self.assertEqual(p_total, 0)
        self.assertEqual([m['metric_id'] for m in p_missing],
                         ['UNEMPLOYMENT', 'RSAFS', 'INDPRO'])


class T04NegativeSensitivity(unittest.TestCase):
    """要点①负向: 注入真实缺陷(破坏economy卫语句)→诚实形态断言必然变红。"""

    def test_04_sabotage_guard_makes_honest_assertions_fail(self):
        src_path = os.path.join(ROOT, 'scripts', 'macro_scorecard.py')
        with open(src_path, 'r', encoding='utf-8') as f:
            src = f.read()
        needle = "    if economy != 'US':\n        for key, mid, name in (('consumer_confidence'"
        self.assertIn(needle, src, "score_growth卫语句不在场——实现已漂移,人工核查")
        bad = src.replace(needle, "    if False:\n        for key, mid, name in (('consumer_confidence'", 1)
        self.assertNotEqual(bad, src)
        mod = types.ModuleType('ms_sabotaged')
        mod.__file__ = src_path
        exec(compile(bad, src_path, 'exec'), mod.__dict__)
        # 被破坏实现: 非US也走US阈值路径(=杜撰口径) → t01的诚实断言必红
        scores, total, missing = mod.score_growth(_us_full_facts(), economy='JP')
        self.assertNotEqual(scores, {}, "缺陷未生效: 破坏件仍返回空得分")
        self.assertIsInstance(total, int)
        self.assertEqual(len(missing), 0)
        # 交叉证明: 破坏件输出==US口径输出(证明卫语句是唯一分叉点)
        us_scores, us_total, _ = mod.score_growth(_us_full_facts(), economy='US')
        self.assertEqual((scores, total), (us_scores, us_total))


class T05T06MainArchiveAndRender(unittest.TestCase):
    """要点①/存档面: main(economy=)存档命名/键面/渲染标题; US零回归。"""

    def test_05_main_economy_archive_naming_and_keys(self):
        with tempfile.TemporaryDirectory() as root:
            snap, data_root, daily = _build_day(root)
            # ── 非US(JP): economy_scorecard_JP_{ymd}.json/.md ──
            res_jp = ms.main(date_str=YMD, data_dir=daily, economy='JP')
            jp_json = os.path.join(daily, f'economy_scorecard_JP_{YMD}.json')
            jp_md = os.path.join(daily, f'economy_scorecard_JP_{YMD}.md')
            self.assertTrue(os.path.isfile(jp_json), "非US JSON存档命名不符")
            self.assertTrue(os.path.isfile(jp_md), "非US MD存档命名不符")
            with open(jp_json, 'r', encoding='utf-8') as f:
                jp = json.load(f)
            self.assertEqual(set(jp.keys()), LEGACY_KEYS | {'economy'})
            self.assertEqual(jp['economy'], 'JP')
            self.assertIsNone(jp['growth_total'])
            self.assertIsNone(jp['inflation_total'])
            self.assertEqual(len(jp['growth_missing']), 4)
            self.assertEqual(len(jp['inflation_missing']), 4)
            self.assertEqual(jp['regime'], ms.DATA_INSUFFICIENT)
            self.assertEqual(jp['regime_status'], 'data_insufficient')
            self.assertEqual(jp['confirmed_regime'], ms.DATA_INSUFFICIENT)
            self.assertEqual(res_jp['economy'], 'JP')
            # JP运行不得生成US主评分卡(命名族隔离)
            self.assertFalse(os.path.exists(os.path.join(daily, f'scorecard_{YMD}.json')))
            # ── US(默认调用形态=既有e2e签名): scorecard_{ymd}.json/.md, 19键无economy ──
            res_us = ms.main(date_str=YMD, data_dir=daily)
            us_json = os.path.join(daily, f'scorecard_{YMD}.json')
            us_md = os.path.join(daily, f'scorecard_{YMD}.md')
            self.assertTrue(os.path.isfile(us_json))
            self.assertTrue(os.path.isfile(us_md))
            with open(us_json, 'r', encoding='utf-8') as f:
                us = json.load(f)
            self.assertEqual(set(us.keys()), LEGACY_KEYS, "US键面须恰=19 legacy键")
            self.assertNotIn('economy', us)
            # fixture面: UMCSENT(68.0→0分)可用1项, 其余月频无序列→缺失 ⇒ 数据不足
            self.assertEqual(us['regime'], ms.DATA_INSUFFICIENT)
            self.assertEqual(us['regime_status'], 'data_insufficient')
            self.assertEqual(us['max_confidence'], 2,
                             "US首跑遇数据不足: 首次运行路径置信度=2(JP档不得被当作上期)")
            # US存档在JP档在场时不被污染: 增长分恰=UMCSENT单项
            self.assertEqual({k: v['score'] for k, v in us['growth_scores'].items()},
                             {'consumer_confidence': 0})
            self.assertEqual(us['growth_total'], 0)
            self.assertEqual(len(us['growth_missing']), 3)
            self.assertNotIn('economy', res_us)

    def test_06_render_titles(self):
        with tempfile.TemporaryDirectory() as root:
            _snap, _dr, daily = _build_day(root)
            ms.main(date_str=YMD, data_dir=daily, economy='JP')
            ms.main(date_str=YMD, data_dir=daily)
            with open(os.path.join(daily, f'economy_scorecard_JP_{YMD}.md'),
                      'r', encoding='utf-8') as f:
                jp_md = f.read()
            self.assertTrue(jp_md.startswith(f"# 宏观体制评分卡(日本 {YMD})"),
                            "非US标题须含经济体名前缀")
            self.assertIn("**增长总分: —(该经济体阈值口径未定义,不计分不折0)**", jp_md)
            with open(os.path.join(daily, f'scorecard_{YMD}.md'), 'r', encoding='utf-8') as f:
                us_md = f.read()
            self.assertTrue(us_md.startswith(f"# 宏观体制评分卡({YMD})"),
                            "US标题零回归(无前缀)")


class T07T08DataPackEconomySection(unittest.TestCase):
    """要点②: 数据包「经济体观察」节渲染快照测试。"""

    def _day_with_archives(self):
        tmp = tempfile.TemporaryDirectory()
        root = tmp.name
        snap, data_root, daily = _build_day(root)
        ms.main(date_str=YMD, data_dir=daily)               # US主评分卡(JSON在场)
        ms.main(date_str=YMD, data_dir=daily, economy='JP')  # JP档(JSON在场)
        md = da.build_markdown(snap, YMD, data_dir=data_root, trusted_root=root)
        return tmp, md

    def test_07_section_present_position_rows(self):
        tmp, md = self._day_with_archives()
        with tmp:
            self.assertIn('## 经济体观察', md)
            self.assertIn('> 阈值表仅定义于美国(US)评分口径;', md)
            self.assertIn('| 经济体 | 增长 | 通胀 | 制度 | 数据状态 |', md)
            # 节位置: 中国市场之后、联邦基金期货之前
            i_cn = md.index('## 中国市场')
            i_econ = md.index('## 经济体观察')
            i_ff = md.index('## 联邦基金期货')
            self.assertTrue(i_cn < i_econ < i_ff, "经济体节位置=中国市场后/联邦基金期货前")
            # 四行: 行序US,CN,JP,EA; US/JP档在场, CN/EA未生成如实标注
            self.assertIn('| 美国(US) | +0 | +0 | 数据不足不可判 | 本期在场;数据不足 |', md)
            self.assertIn('| 中国(CN) | 未生成 | 未生成 | 未生成 | 未生成(当日评分卡不存在) |', md)
            self.assertIn('| 日本(JP) | 数据不足 | 数据不足 | 数据不足不可判 | 本期在场;数据不足 |', md)
            self.assertIn('| 欧元区(EA) | 未生成 | 未生成 | 未生成 | 未生成(当日评分卡不存在) |', md)
            rows = [ln for ln in md.splitlines()
                    if ln.startswith('| 美国(US) |') or ln.startswith('| 中国(CN) |')
                    or ln.startswith('| 日本(JP) |') or ln.startswith('| 欧元区(EA) |')]
            self.assertEqual([r.split('|')[1].strip() for r in rows],
                             ['美国(US)', '中国(CN)', '日本(JP)', '欧元区(EA)'],
                             "行序须=US,CN,JP,EA")

    def test_08_disclosure_lines(self):
        tmp, md = self._day_with_archives()
        with tmp:
            # 静态注册表覆盖披露(活跃计数, registry v2.2.0实测: US48/CN10/JP8/EA11)
            self.assertIn('注册表覆盖(静态披露,config/metric_registry.json economy字段活跃计数): '
                          '美国(US)=48项; 中国(CN)=18项; 日本(JP)=8项; 欧元区(EA)=11项', md)
            # JP/EA通道披露(快照顶层sources_status; 通道名 japan/jp/ea)
            self.assertIn('日本通道披露: japan=EXACT(japan_%s.json), jp=EXACT(jp_%s.json)'
                          % (YMD, YMD), md)
            self.assertIn('通道事实未接线进快照facts(上游WP-B F1延后面)', md)
            self.assertIn('欧元区通道披露: ea=EXACT(ea_%s.json)' % YMD, md)
            # US主评分卡glob不被非US档污染: 主评分卡节仍取到当日US档
            self.assertIn(f'## 宏观体制评分卡(本期{YMD};模型观点,非客观事实)', md)


class T09T10GateBAnchors(unittest.TestCase):
    """要点③: Gate B对新锚点全量核验——在族MAPPED + 域外fail-closed(负向)。"""

    def test_09_new_pair_anchors_in_family(self):
        with tempfile.TemporaryDirectory() as root:
            snap, _dr, daily = _build_day(root)
            anchors = sb.build_anchors(snap, YMD)
            # USDJPY/EURUSD经global支路自动覆盖(锚点=build_anchors按快照事实生成,零改动)
            self.assertIn('global_market.data.JPY=X.close', anchors)
            self.assertIn('global_market.data.EURUSD.close', anchors)
            self.assertEqual(anchors['global_market.data.JPY=X.close']['metric_id'], 'USDJPY')
            self.assertEqual(anchors['global_market.data.JPY=X.close']['value'], 152.4)  # fixt值
            self.assertEqual(anchors['global_market.data.EURUSD.close']['metric_id'], 'EURUSD')
            self.assertEqual(anchors['global_market.data.EURUSD.close']['value'], 1.163)
            # Gate B锚点身份核验: canonical映射+来源家族绑定 → MAPPED
            for key, mid in (('global_market.data.JPY=X.close', 'USDJPY'),
                             ('global_market.data.EURUSD.close', 'EURUSD')):
                v = fp.verify_anchor_identity(key, anchors[key])
                self.assertEqual(v['status'], 'MAPPED', f"{key}: {v}")
                self.assertEqual(v['metric_id'], mid)
                self.assertEqual(v['family'], 'global_market')
            # 锚点prompt块(Gate B消费面)含两新对锚点键
            block = dv.generate_anchor_prompt_block(anchors)
            self.assertIn('JPY=X', block)
            self.assertIn('EURUSD', block)
            # NIKKEI225/DAX facts未接线(WP-B F1) ⇒ 快照不产其锚点(诚实缺席,非伪造)
            self.assertFalse([k for k in anchors if 'NIKKEI225' in k or 'DAX' in k],
                             "facts未接线的指标不得出现锚点")

    def test_10_out_of_family_anchor_fail_closed(self):
        # 负向敏感度: NIKKEI225/DAX已注册但权威来源非global_market家族
        # → 以global_market形态请求锚点身份 ⇒ SOURCE_MISMATCH→UNVERIFIED(fail-closed)
        for key in ('global_market.data.NIKKEI225.close',
                    'global_market.data.DAX.close'):
            v = fp.verify_anchor_identity(key)
            self.assertEqual(v['status'], 'UNVERIFIED', f"{key}: {v}")
            self.assertEqual(v['reason'], 'source_mismatch')
            self.assertIsNone(v['metric_id'], "域外锚点不得返回可认证身份")
        # 反例锁定fail-closed语义: 同形键但家族内来源(USDJPY旧键)仍MAPPED——
        # 机器正确性=拒绝越族而非拒绝一切
        v = fp.verify_anchor_identity('global_market.data.JPY=X.close')
        self.assertEqual(v['status'], 'MAPPED')
        self.assertEqual(v['metric_id'], 'USDJPY')


class T11T12CorrelationPairs(unittest.TestCase):
    """相关性新对: PAIRS登记面 + 全链路计算(合成series_store, 硬编码期望)。"""

    OLD_10 = [('SPX', 'TLT'), ('SPX', 'GOLD_F'), ('DXY', 'SPX'), ('DXY', 'GOLD_F'),
              ('WTI_F', 'TLT'), ('WTI_F', 'EEM'), ('SPX', 'EZU'), ('SPX', 'FXI'),
              ('VIX', 'HYG'), ('BTC', 'NDX')]

    def test_11_pairs_registration(self):
        self.assertEqual(len(cc.PAIRS), 12)
        self.assertEqual([(p['a'], p['b']) for p in cc.PAIRS[:10]], self.OLD_10,
                         "既有10对顺序与配对零变化")
        self.assertEqual(cc.PAIRS[10], {
            'a': 'NIKKEI225', 'b': 'USDJPY', 'label': '日经225 vs 美元/日元',
            'disclosure': '跨域配对(IA-P1-WP-C新增): 日经225为日元计价股指,'
                          '与USDJPY汇率同表仅示联动,描述统计非因果'})
        self.assertEqual(cc.PAIRS[11], {
            'a': 'DAX', 'b': 'EURUSD', 'label': '德国DAX vs 欧元/美元',
            'disclosure': '跨域配对(IA-P1-WP-C新增): DAX为欧元区股指,'
                          '与EURUSD汇率同表仅示联动,描述统计非因果'})

    def test_12_new_pair_full_chain(self):
        # [示意] 4共同观测日⇒3收益样本; USDJPY收益≡0.1×NIKKEI收益(手算构造),
        # EURUSD收益≡-0.1×DAX收益 ⇒ 皮尔逊=+1.0/-1.0(比例序列的数学性质,非自证)
        D = ['2026-11-02', '2026-11-03', '2026-11-04', '2026-11-05']
        nik = {'dates': D, 'values': [38000.0, 41800.0, 39900.0, 43890.0]}
        dax = {'dates': D, 'values': [19000.0, 20900.0, 19950.0, 21945.0]}

        def _scaled(base, k):
            vals, cur = [float(base)], float(base)
            for i in range(1, len(D)):
                r = nik['values'][i] / nik['values'][i - 1] - 1.0
                cur = cur * (1.0 + k * r)
                vals.append(cur)
            return {'dates': D, 'values': vals}

        store = {'NIKKEI225': nik, 'DAX': dax,
                 'USDJPY': _scaled(150.0, 0.1), 'EURUSD': _scaled(1.16, -0.1)}
        results, missing = cc.compute_all({'series_store': store})
        self.assertEqual([r['label'] for r in results],
                         ['日经225 vs 美元/日元', '德国DAX vs 欧元/美元'])
        self.assertEqual(len(missing), 10, "旧10对无序列⇒如实序列缺失")
        r1, r2 = results
        self.assertEqual((r1['a'], r1['b']), ('NIKKEI225', 'USDJPY'))
        self.assertAlmostEqual(r1['corr_20d'], 1.0, places=10)
        self.assertAlmostEqual(r1['corr_60d'], 1.0, places=10)
        self.assertEqual((r1['n_20d'], r1['n_60d']), (3, 3))
        self.assertEqual((r1['window_first'], r1['window_last']),
                         ('2026-11-03', '2026-11-05'))
        self.assertEqual((r2['a'], r2['b']), ('DAX', 'EURUSD'))
        self.assertAlmostEqual(r2['corr_20d'], -1.0, places=10)
        self.assertAlmostEqual(r2['corr_60d'], -1.0, places=10)
        # markdown渲染: 新对行+口径披露
        md = cc.generate_markdown(results, missing, '2026-11-05')
        self.assertIn('| 日经225 vs 美元/日元 | +1.00 | 3 | +1.00 | 3 | '
                      '2026-11-03~2026-11-05 |', md)
        self.assertIn('| 德国DAX vs 欧元/美元 | -1.00 | 3 | -1.00 | 3 | '
                      '2026-11-03~2026-11-05 |', md)
        self.assertIn('- 日经225 vs 美元/日元: 跨域配对(IA-P1-WP-C新增)', md)
        self.assertIn('- 标普500 vs 20+年国债ETF: 序列缺失(SPX不在快照series_store)', md)
        # 新对序列缺失分支(真实运行面形态: series_store无NIKKEI/DAX, WP-B F2)
        results2, missing2 = cc.compute_all({'series_store': {}})
        self.assertEqual(results2, [])
        self.assertIn('日经225 vs 美元/日元: 序列缺失(NIKKEI225不在快照series_store)', missing2)
        self.assertIn('德国DAX vs 欧元/美元: 序列缺失(DAX不在快照series_store)', missing2)


class T13ReportTemplateZeroDiff(unittest.TestCase):
    """报告模板零改动判定的实测固化(DESIGN L128: 数据包新节自动进入prompt)。"""

    def test_13_prompt_embeds_economy_section_without_template_change(self):
        import report_generator as rg
        tmp = tempfile.TemporaryDirectory()
        captured = {}

        def fake_glm(system_prompt, user_prompt, **kw):
            captured['usr'] = user_prompt
            return 'X' * 600                       # ≥500字符⇒首试即返回, 零重试零sleep

        orig = rg._call_glm
        rg._call_glm = fake_glm
        try:
            with tmp:
                snap, data_root, daily = _build_day(tmp.name)
                ms.main(date_str=YMD, data_dir=daily)
                data_pack = da.build_markdown(snap, YMD, data_dir=data_root,
                                              trusted_root=tmp.name)
                out = rg.generate_report(data_pack)
        finally:
            rg._call_glm = orig
        self.assertIsNotNone(out)
        self.assertIn('## 经济体观察', captured['usr'],
                      "数据包经济体节须原样进入GLM prompt(自动传导=零模板改动的判定依据)")
        self.assertIn('| 经济体 | 增长 | 通胀 | 制度 | 数据状态 |', captured['usr'])
        i_data = captured['usr'].index('## 本周市场数据')
        i_econ = captured['usr'].index('## 经济体观察')
        self.assertTrue(i_data < i_econ, "经济体节须落在数据包嵌入区内")


class T14ExistingChainCompat(unittest.TestCase):
    """CI兼容回归: 既有链路(fixt.build_full_day=采集→快照→装配→锚点→prompt)
    在含经济体节的装配输出上正常运行(既有e2e调用形态零破坏)。"""

    def test_14_build_full_day_with_new_section(self):
        tmp = tempfile.TemporaryDirectory()
        with tmp:
            snap, snap_path, paths = fixt.build_full_day(tmp.name, YMD)
            pack = open(paths['pack'], 'r', encoding='utf-8').read()
            self.assertIn('## 经济体观察', pack)
            # build_full_day只写scorecard_{ymd}.md(无JSON)⇒US行如实"未生成"
            self.assertIn('| 美国(US) | 未生成 | 未生成 | 未生成 | 未生成(当日评分卡不存在) |', pack)
            anchors = json.load(open(paths['anchors'], 'r', encoding='utf-8'))
            self.assertIn('global_market.data.JPY=X.close', anchors)
            prompt = open(paths['prompt'], 'r', encoding='utf-8').read()
            self.assertIn('EURUSD', prompt)
            # GAP08-F3 口径翻转: 13 新指标缺席自 boundary 转 noncore_missing
            # →快照级 DEGRADED(前=PASS;缺席如实披露, 非 US 面劣化)
            self.assertEqual(snap['gate_a']['status'], 'DEGRADED')


if __name__ == '__main__':
    unittest.main(verbosity=2)
