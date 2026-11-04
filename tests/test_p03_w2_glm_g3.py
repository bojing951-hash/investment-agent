# -*- coding: utf-8 -*-
"""IA-P03-W2-GLM-WP-G3(可反驳条件推导与门禁对接+档案衔接)专项测试。

合同 IA-P03-W2-GLM-WP-G3-AC-v1.0 / DESIGN §七 WP-G3 验收要点行为锁:
- 要点① 推导规则四步用例(可规格化/不可规格化分流): 主张变量化三分类/
  阈值三来源逐源/规格化(spec 五键+窗口默认 task 窗+op·mode 枚举)/步4 区分性
  由 G2 承接(trace 登记)+分流落回(apply: 合入四元组去重+non_spec 转
  limitations)+集成闭环(apply 后整体过 G2 校验器)(T1);
- 要点② 门禁提案测试: 数值校验前置 FAIL→阻断;无触发器且新增证据不足→
  提案被拒+留档(复用 ae._record_proposal);与现行门禁同构断言(常量复用
  身份+≥2 门槛/触发器放行/suspend-resume 放宽行为等价);确信度星级门禁;
  预测候选 spec 校验(T2);
- 要点③ append-only 测试: 结论记录改写被拒(ArchiveImmutable)+交叉引用
  字段校验(task_id|origin_query_id 必携其一/HY- 格式/CR- 格式)+幂等跳过/
  新版本追加原记录不动(T3);
- 要点④ E2E-A 字段映射契约测试: rtm.SCHEMA_MIN_FIELDS 复用实读字面量+
  E2EA_FIELD_MAP 9 行登记+投影逐承接面(task_id 透传/echo 只读回显/history
  追加行/evidence 方向化挂载+direction 三值枚举完整/可规格化子集并入/
  pred_* 预测候选/状态推进=提案制/模式 B 裁剪)(T4);
- 登记参数 echo=常量=登记值(T5);源码边界锁: 零网络/零凭证/零文件读写/
  零原始档字样+复用导入标记(T6)。

数据纪律(R014-D3/R022 沿用): 全部离线合成 fixture=唯一数据源——
GLMResearchInput 与 HypothesisSet 均为内联字面量合成(数值锚点 2.93/4186.7
为 E2E-A 登记窗终值语义的合成复用,不代表任何真实交易日数据);注册表/先验
触发器一律注入合成集,真实 config/metric_registry.json、thesis.json、
allocation_views.json 永不进入测试预期值来源;预期值一律字面量硬编码(不从
被测模块导入计算——自证恒真是 F 反例)。零网络/零新增第三方依赖。
零真实 GLM 调用(集成输入=本地合成 fixture 过 G2 校验器,attempts 注入面
沿 G2 桩纪律,本包清单不含调用面实现)。
"""
import copy
import hashlib
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import glm_conclusion_integrator as gci   # noqa: E402 (被测模块)
import allocation_engine as ae            # noqa: E402 (同构断言/留档复用对照)
import glm_input_assembler as gia         # noqa: E402 (G1 契约 fixture 自检)
import glm_output_validator as gov        # noqa: E402 (G2 校验 fixture 自检/集成闭环)
import research_task_manager as rtm       # noqa: E402 (E2E-A schema 契约同源)

# ══ 合成 fixture(唯一数据源;字面量锚点) ════════════════════════════════════
SNAP_ID = 'research_snapshot_20261102'
SNAP_DIGEST = 'a1b2c3d4e5f60718'
TASK_ID = 'RT-20261020~20261102-RD-DIV-001-ab12cd34'
PHENOMENON = 'TIPS_10Y 实际利率与 GOLD_F 同涨背离'
WIN = {'start': '2026-10-20', 'end': '2026-11-02'}
TODAY = '2026-11-05'

TIPS_FACT = {
    'metric_id': 'TIPS_10Y', 'fact_id': 'TIPS_10Y@2026-10-29', 'value': 2.93,
    'unit': 'percent', 'observation_date': '2026-10-29', 'quality_status': 'PASS',
    'derived': {'week': {'basis_date': '2026-10-22', 'basis_value': 2.20,
                         'pp_change': 0.73, 'bp_change': 73.0}},
}
GOLD_FACT = {
    'metric_id': 'GOLD_F', 'fact_id': 'GOLD_F@2026-10-29', 'value': 4186.7,
    'unit': 'usd', 'observation_date': '2026-10-29', 'quality_status': 'PASS',
    'derived': {'week': {'basis_date': '2026-10-22', 'basis_value': 4161.7,
                         'pct_change': 3.7}},
}
# 合成注册表(来源(ii)注入面;真实 config 不入测试;SPX=未入输入的注册表指标)
REG_SYN = {'SPX': {'metric_id': 'SPX',
                   'validation': {'range': [1000, 30000],
                                  'max_week_pct_move': 25}}}
# 合成结构化先验触发器(来源(iii)注入面;真实 thesis/views 不入测试)
TRIG_SYN = [{'trig_id': 'TH-1', 'metric': 'TIPS_10Y', 'op': '>=', 'target': 3.5},
            {'trig_id': 'VW-1', 'metric': 'GOLD_F', 'op': '>=', 'target': 4300.0}]
MISSING_REF = {'status': 'MISSING', 'reason': '合成fixture显式缺席'}
TRIGGER_FIRED = [{'trig_id': 'INV-1', 'direction': 'invalidation',
                  'status': 'triggered', 'detail': '合成', 'consec': 1, 'sustain': 0}]


def build_input(gate='PASS'):
    """合成 GLMResearchInput(模式A;经 gia.validate_input 自检=T0)。"""
    return {
        'contract_version': 'gri-1.0',
        'mode': 'A',
        'snapshot_binding': {
            'snapshot_id': SNAP_ID, 'snapshot_digest': SNAP_DIGEST,
            'gate_a': gate, 'research_as_of': '2026-11-02'},
        'task_ref': {
            'task_id': TASK_ID, 'phenomenon': PHENOMENON,
            'indicators': ['TIPS_10Y', 'GOLD_F', 'JGB_10Y'],
            'window': dict(WIN),
            'detection': {'rule': 'RD-DIV-001', 'score': 65.0},
            'history_tail': []},
        'query_ref': None,
        'evidence_pack': {
            'facts': [copy.deepcopy(TIPS_FACT), copy.deepcopy(GOLD_FACT)],
            'scorecard_summary': dict(MISSING_REF),
            'correlation_ref': dict(MISSING_REF),
            'news_index_ref': dict(MISSING_REF)},
        'absent_registry': [{'metric_id': 'JGB_10Y', 'level': 'ABSENT_REGISTRY',
                             'reason': '指标不在注册表(合成fixture)'}],
        'prior_knowledge': {'theses_block': None, 'views_block': None,
                            'prior_conclusions': []},
        'prompt_contract': {'language': 'zh',
                            'output_schema_version': 'hs-1.0',
                            'counter_evidence_required': True,
                            'min_competing_hypotheses': 2,
                            'numeric_grounding_required': True},
    }


def build_input_mode_b():
    """合成 GLMResearchInput(模式B;query_ref 引用摘要形态)。"""
    inp = build_input()
    inp['mode'] = 'B'
    inp['task_ref'] = None
    inp['absent_registry'] = []
    inp['query_ref'] = {'query_id': 'QB-20261102-001',
                        'question_text': 'TIPS_10Y与GOLD_F为何同涨?',
                        'as_of': '2026-11-02',
                        'metric_bindings_digest': 'b2c3d4e5f60718a9',
                        'derived_ops_digest': 'c3d4e5f60718a9b0'}
    return inp


def build_output():
    """合成 HypothesisSet(模式A七字段;经 gov.validate_output 自检=T0)。"""
    return {
        'hypotheses': [
            {'hypothesis_id': 'HY-20261102-001',
             'statement': ('TIPS_10Y 实际利率升至 2.93 与 GOLD_F 金价 4186.7 '
                           '同涨,流动性共同驱动假设'),
             'supporting_evidence': [
                 {'fact_id': 'TIPS_10Y@2026-10-29', 'metric_id': 'TIPS_10Y',
                  'direction_note': '实际利率周升 0.73(基点 73.0),自 2.20 升至 2.93'}],
             'counter_evidence': [
                 {'fact_id': 'GOLD_F@2026-10-29', 'metric_id': 'GOLD_F',
                  'direction_note': '金价周涨 3.7% 至 4186.7,与利率同涨削弱背离叙事'}],
             'falsifiable_conditions': [
                 {'cond_text': ('若 TIPS_10Y 于观察窗截至 2026-11-02 >= 2.93'
                                '(expiry)则流动性假设可程序反驳(阈值来源:evidence_pack)'),
                  'spec': {'metric': 'TIPS_10Y', 'op': '>=', 'target': 2.93,
                           'mode': 'expiry', 'window': dict(WIN)}}],
             'confidence': 'high',
             'limitations': ['JGB_10Y 缺席(ABSENT_REGISTRY): 日本利率侧交叉验证不可得',
                             '替代解释: HY-20261102-002(美元信用对冲)']},
            {'hypothesis_id': 'HY-20261102-002',
             'statement': ('美元信用对冲假设: GOLD_F 坚挺源于央行购金与美元信用'
                           '担忧,日本利率 JGB_10Y 缺席下实际利率路径次要'),
             'supporting_evidence': [
                 {'fact_id': 'GOLD_F@2026-10-29', 'metric_id': 'GOLD_F',
                  'direction_note': '金价 4186.7 高位,央行购金持续'}],
             'counter_evidence': [
                 {'fact_id': 'TIPS_10Y@2026-10-29', 'metric_id': 'TIPS_10Y',
                  'direction_note': '实际利率 2.93 高位通常压制无息资产'}],
             'falsifiable_conditions': [
                 {'cond_text': ('若 GOLD_F 于观察窗截至 2026-11-02 >= 4186.7'
                                '(expiry)则对冲假设可程序反驳(阈值来源:evidence_pack)'),
                  'spec': {'metric': 'GOLD_F', 'op': '>=', 'target': 4186.7,
                           'mode': 'expiry', 'window': dict(WIN)}}],
             'confidence': 'medium',
             'limitations': ['JGB_10Y 缺席(ABSENT_REGISTRY): 未覆盖日本利率侧证据',
                             '替代解释: HY-20261102-001(流动性共同驱动)']}],
        'phenomenon_echo': PHENOMENON,
        'absent_ack': ['JGB_10Y 缺席(ABSENT_REGISTRY): 指标不在注册表(合成fixture)'],
    }


def legal_set(inp):
    """三合法来源并集(合成注入;断言用,独立于被测模块组装路径)。"""
    return gov.legal_target_numbers(
        inp, registry_targets={1000, 30000, 25},
        prior_trigger_targets=gci.extract_prior_trigger_targets(TRIG_SYN))


def run_fixture_pipeline(inp, out):
    """经 G2 真实管线产 result(集成: G2→G3;attempts=本地合成桩)。"""
    return gov.run_conclusion_pipeline(
        inp, [{'raw': json.dumps(out, ensure_ascii=False)}],
        registry_targets=set(),
        prior_trigger_targets=gci.extract_prior_trigger_targets(TRIG_SYN))


class T0_FixtureSanity(unittest.TestCase):
    """fixture 自检: 合成输入/输出经 G1/G2 既有权威校验器回读=合法契约。"""

    def test_input_passes_g1_contract(self):
        self.assertEqual(gia.validate_input(build_input()), [])

    def test_output_passes_g2_contract(self):
        inp = build_input()
        self.assertEqual(gov.validate_output(
            inp, build_output(), registry_targets=set(),
            prior_trigger_targets=set()), [])


class T1_DerivationRules(unittest.TestCase):
    """要点①: §五(1) 推导规则四步(可规格化/不可规格化分流)。"""

    def _inp(self):
        return build_input()

    def test_step1_variableize_three_classes(self):
        hyp = {'statement': 'TIPS_10Y 与 GOLD_F 同涨,SPX 未入输入,JGB_10Y 缺席'}
        v = gci.variableize_claim(hyp, self._inp(), registry_metrics=REG_SYN)
        self.assertEqual(v['present'], ['TIPS_10Y', 'GOLD_F'])
        self.assertEqual(v['absent'], ['JGB_10Y'])
        self.assertEqual(v['registered_not_in_input'], ['SPX'])

    def test_step2_thresholds_source_i_per_metric_order(self):
        thr = gci.legal_thresholds_for('TIPS_10Y', self._inp(),
                                       registry_metrics=REG_SYN)
        self.assertEqual(thr['evidence_pack'], [2.93, 0.73, 73.0, 2.20])
        thr_g = gci.legal_thresholds_for('GOLD_F', self._inp(),
                                         registry_metrics=REG_SYN)
        self.assertEqual(thr_g['evidence_pack'], [4186.7, 3.7, 4161.7])

    def test_step2_thresholds_source_ii_registry(self):
        thr = gci.legal_thresholds_for('SPX', self._inp(),
                                       registry_metrics=REG_SYN)
        self.assertEqual(thr['registry'], [1000, 30000, 25])
        self.assertEqual(thr['evidence_pack'], [])

    def test_step2_thresholds_source_iii_prior_triggers(self):
        thr = gci.legal_thresholds_for('TIPS_10Y', self._inp(),
                                       registry_metrics={},
                                       prior_triggers=TRIG_SYN)
        self.assertEqual(thr['prior_triggers'], [3.5])
        thr_g = gci.legal_thresholds_for('GOLD_F', self._inp(),
                                         registry_metrics={},
                                         prior_triggers=TRIG_SYN)
        self.assertEqual(thr_g['prior_triggers'], [4300.0])

    def test_step3_specification_form_and_window_default(self):
        d = gci.derive_falsifiable_conditions(
            {'statement': 'TIPS_10Y 上行'}, self._inp(),
            registry_metrics=REG_SYN, prior_triggers=TRIG_SYN)
        self.assertEqual(len(d['spec_conditions']), 1)
        c = d['spec_conditions'][0]
        self.assertEqual(c['spec'], {'metric': 'TIPS_10Y', 'op': '>=',
                                     'target': 2.93, 'mode': 'expiry',
                                     'window': dict(WIN)})   # 窗口默认=task窗
        self.assertIn('TIPS_10Y', c['cond_text'])
        self.assertIn('2.93', c['cond_text'])

    def test_step3_op_mode_enums_rejected(self):
        with self.assertRaises(ValueError):
            gci.derive_falsifiable_conditions({'statement': 'x'}, self._inp(),
                                              op='==')
        with self.assertRaises(ValueError):
            gci.derive_falsifiable_conditions({'statement': 'x'}, self._inp(),
                                              mode='span')

    def test_step4_distinctiveness_deferred_trace(self):
        d = gci.derive_falsifiable_conditions(
            {'statement': 'TIPS_10Y 上行'}, self._inp(), registry_metrics=REG_SYN)
        last = d['trace'][-1]
        self.assertEqual(last['step'], 'distinctiveness')
        self.assertEqual(last['status'], 'deferred-to-g2-validator')

    def test_derive_nonspecifiable_absent_metric_flow(self):
        hyp = {'statement': '日本利率 JGB_10Y 缺席下黄金坚挺'}
        d = gci.derive_falsifiable_conditions(hyp, self._inp(),
                                              registry_metrics=REG_SYN)
        self.assertEqual(d['spec_conditions'], [])
        self.assertEqual(len(d['non_specifiable']), 1)
        ns = d['non_specifiable'][0]
        self.assertEqual(ns['metric_id'], 'JGB_10Y')
        self.assertIn('不可程序裁决', ns['declaration'])

    def test_derive_nonspecifiable_no_legal_threshold_flow(self):
        hyp = {'statement': 'TIPS_10Y 上行'}
        d = gci.derive_falsifiable_conditions(
            hyp, self._inp(), threshold_source='registry',
            registry_metrics={})       # 在场但来源(ii) 无该指标阈值
        self.assertEqual(d['spec_conditions'], [])
        self.assertEqual(d['non_specifiable'][0]['metric_id'], 'TIPS_10Y')
        self.assertIn('不可规格化', d['non_specifiable'][0]['declaration'])

    def test_derive_never_fabricates_thresholds(self):
        inp = self._inp()
        legal = legal_set(inp)
        hyp = {'statement': 'TIPS_10Y 与 GOLD_F 同涨,SPX 未入输入,JGB_10Y 缺席'}
        for src in ('auto', 'evidence_pack', 'registry', 'prior_triggers'):
            d = gci.derive_falsifiable_conditions(
                hyp, inp, threshold_source=src, registry_metrics=REG_SYN,
                prior_triggers=TRIG_SYN)
            for c in d['spec_conditions']:
                self.assertIn(c['spec']['target'], legal,
                              f'{src} 来源外阈值=编造')

    def test_derive_cond_text_grounded(self):
        inp = self._inp()
        legal = legal_set(inp)
        d = gci.derive_falsifiable_conditions(
            {'statement': 'TIPS_10Y 与 GOLD_F 同涨'}, inp,
            registry_metrics=REG_SYN, prior_triggers=TRIG_SYN)
        for c in d['spec_conditions']:
            nums = gov.extract_numeric_tokens(c['cond_text'])
            self.assertTrue(all(n in legal for n in nums))

    def test_derive_registered_not_in_input_noted(self):
        hyp = {'statement': 'SPX 风险偏好支持流动性假设'}
        d = gci.derive_falsifiable_conditions(hyp, self._inp(),
                                              registry_metrics=REG_SYN)
        self.assertEqual(d['spec_conditions'], [])
        self.assertEqual(d['non_specifiable'], [])
        self.assertEqual(len(d['derivation_notes']), 1)
        self.assertIn('SPX', d['derivation_notes'][0])

    def test_apply_derived_conditions_merge_and_dedup(self):
        inp = self._inp()
        out = build_output()
        h1 = copy.deepcopy(out['hypotheses'][0])
        d = gci.derive_falsifiable_conditions(h1, inp,
                                              registry_metrics=REG_SYN)
        applied = gci.apply_derived_conditions(h1, d)
        # TIPS 条件四元组与既有相同→去重跳过;GOLD_F 条件为新增
        self.assertEqual(len(applied['falsifiable_conditions']), 2)
        quads = [tuple(applied['falsifiable_conditions'][i]['spec'][k]
                       for k in ('metric', 'op', 'target', 'mode'))
                 for i in range(2)]
        self.assertEqual(quads, [('TIPS_10Y', '>=', 2.93, 'expiry'),
                                  ('GOLD_F', '>=', 4186.7, 'expiry')])
        self.assertEqual(len(h1['falsifiable_conditions']), 1)   # 入参不改

    def test_apply_nonspec_to_limitations(self):
        inp = self._inp()
        h2 = copy.deepcopy(build_output()['hypotheses'][1])
        d = gci.derive_falsifiable_conditions(h2, inp,
                                              registry_metrics=REG_SYN)
        applied = gci.apply_derived_conditions(h2, d)
        self.assertEqual(len(applied['limitations']),
                         len(h2['limitations']) + 1)
        self.assertIn('不可程序裁决', applied['limitations'][-1])
        self.assertIn('JGB_10Y', applied['limitations'][-1])

    def test_integrated_applied_output_passes_g2(self):
        """集成闭环(步4 承接形态): 推导+分流落回后的整体输出过 G2 校验器。"""
        inp = self._inp()
        out = build_output()
        for i, h in enumerate(out['hypotheses']):
            d = gci.derive_falsifiable_conditions(h, inp,
                                                  registry_metrics=REG_SYN)
            out['hypotheses'][i] = gci.apply_derived_conditions(h, d)
        probs = gov.validate_output(
            inp, out, registry_targets={1000, 30000, 25},
            prior_trigger_targets=gci.extract_prior_trigger_targets(TRIG_SYN))
        self.assertEqual(probs, [])

    def test_extract_prior_trigger_targets(self):
        self.assertEqual(gci.extract_prior_trigger_targets(TRIG_SYN),
                         {3.5, 4300.0})
        self.assertEqual(gci.extract_prior_trigger_targets(None), set())
        self.assertEqual(
            gci.extract_prior_trigger_targets(
                [{'trig_id': 'X', 'metric': 'M', 'op': '>=',
                  'target': 'non-numeric'}]), set())


class T2_GateBProposals(unittest.TestCase):
    """要点②: 门禁提案(数值校验前置+同构门禁+被拒留档)。"""

    def _proposal(self, **kw):
        inp = build_input()
        out = build_output()
        base = dict(kind='thesis_status', hypothesis=out['hypotheses'][0],
                    target_id='TH-9', change_to='已失效',
                    new_support_metrics=['TIPS_10Y'], trigger_rows=[],
                    today_iso=TODAY)
        base.update(kw)
        return gci.build_gate_b_proposal(
            inp, out, registry_targets=set(),
            prior_trigger_targets=set(), **base)

    def test_numeric_prefail_blocks_proposal(self):
        inp = build_input()
        out = build_output()
        out['hypotheses'][0]['statement'] = '实际利率升至 2.94(数值改写,不在证据包)'
        p = gci.build_gate_b_proposal(inp, out, kind='thesis_status',
                                      change_to='已失效',
                                      new_support_metrics=['TIPS_10Y', 'GOLD_F'],
                                      today_iso=TODAY, registry_targets=set(),
                                      prior_trigger_targets=set())
        self.assertTrue(p['blocked'])
        self.assertEqual(p['numeric_gate']['combined'], 'FAIL')
        self.assertTrue(p['numeric_gate']['validation_problems'])
        accepted, reason = gci.evaluate_gate_b(p)
        self.assertFalse(accepted)
        self.assertIn('数值校验前置FAIL', reason)

    def test_gate_degraded_combined_not_blocked(self):
        inp = build_input(gate='DEGRADED')
        out = build_output()
        for h in out['hypotheses']:      # 径2 义务: 降级承接标记
            h['limitations'] = list(h['limitations']) + ['Gate A DEGRADED: 数据降级影响已承接']
        p = gci.build_gate_b_proposal(inp, out, kind='thesis_status',
                                      change_to='已失效',
                                      new_support_metrics=['TIPS_10Y', 'GOLD_F'],
                                      today_iso=TODAY, registry_targets=set(),
                                      prior_trigger_targets=set())
        self.assertFalse(p['blocked'])
        self.assertEqual(p['numeric_gate']['combined'], 'DEGRADED')
        self.assertTrue(gci.evaluate_gate_b(p)[0])

    def test_thesis_terminal_no_trigger_insufficient_rejected(self):
        p = self._proposal()             # 无触发器+1 项新增证据
        accepted, reason = gci.evaluate_gate_b(p)
        self.assertFalse(accepted)
        self.assertIn('终态判定', reason)
        self.assertIn('≥2', reason)

    def test_thesis_terminal_rejected_recorded_via_ae(self):
        p = self._proposal()
        accepted, reason = gci.evaluate_gate_b(p)
        self.assertFalse(accepted)
        thesis = {'id': 'TH-9', 'status': '进行中'}
        entry = gci.record_rejected_proposal(thesis, p, reason, TODAY)
        self.assertEqual(entry['status'], 'rejected')
        self.assertEqual(thesis['proposals'][0]['to'], '已失效')
        self.assertIn('终态判定', thesis['proposals'][0]['reason'])

    def test_thesis_terminal_two_new_support_accepted(self):
        p = self._proposal(new_support_metrics=['TIPS_10Y', 'GOLD_F'])
        accepted, reason = gci.evaluate_gate_b(p)
        self.assertTrue(accepted)
        self.assertIn('新增独立支持证据2项', reason)

    def test_thesis_terminal_trigger_fired_accepted(self):
        p = self._proposal(trigger_rows=TRIGGER_FIRED)
        accepted, reason = gci.evaluate_gate_b(p)
        self.assertTrue(accepted)
        self.assertIn('invalidation触发器', reason)
        self.assertIn('INV-1', reason)

    def test_thesis_process_status_allowed(self):
        p = self._proposal(change_to='待观察')
        accepted, reason = gci.evaluate_gate_b(p)
        self.assertTrue(accepted)
        self.assertIn('过程状态调整', reason)

    def test_confidence_above_star_rejected(self):
        p = self._proposal(kind='thesis_confidence', change_to=4, star_max=3)
        accepted, reason = gci.evaluate_gate_b(p)
        self.assertFalse(accepted)
        self.assertIn('不足以授予4★', reason)

    def test_confidence_within_star_accepted(self):
        p = self._proposal(kind='thesis_confidence', change_to=3, star_max=3)
        self.assertTrue(gci.evaluate_gate_b(p)[0])

    def test_confidence_star_missing_fail_closed(self):
        p = self._proposal(kind='thesis_confidence', change_to=3, star_max=None)
        accepted, reason = gci.evaluate_gate_b(p)
        self.assertFalse(accepted)
        self.assertIn('fail-closed', reason)

    def test_view_rating_insufficient_rejected(self):
        p = self._proposal(kind='view_rating', change_to='超配',
                           current='标配', new_support_metrics=['TIPS_10Y'])
        accepted, reason = gci.evaluate_gate_b(p)
        self.assertFalse(accepted)
        self.assertIn('upgrade', reason)

    def test_view_rating_two_support_accepted(self):
        p = self._proposal(kind='view_rating', change_to='超配',
                           current='标配',
                           new_support_metrics=['TIPS_10Y', 'GOLD_F'])
        self.assertTrue(gci.evaluate_gate_b(p)[0])

    def test_view_rating_suspend_relaxed_to_one(self):
        p = self._proposal(kind='view_rating', change_to='观望',
                           current='标配', new_support_metrics=['TIPS_10Y'])
        accepted, reason = gci.evaluate_gate_b(p)
        self.assertTrue(accepted)
        self.assertIn('direction=suspend', reason)

    def test_view_rating_trigger_fired_accepted(self):
        p = self._proposal(kind='view_rating', change_to='超配',
                           current='标配',
                           trigger_rows=[{'trig_id': 'UP-1', 'direction':
                                          'upgrade', 'status': 'triggered'}])
        accepted, reason = gci.evaluate_gate_b(p)
        self.assertTrue(accepted)
        self.assertIn('upgrade触发器', reason)

    def test_gate_constants_shared_with_ae(self):
        """与现行门禁同构断言: 判定常量=ae 同一登记值(复用非复制)。"""
        self.assertEqual(gci.RATING_CHANGE_MIN_EVIDENCE,
                         ae.MIN_EVIDENCE_FOR_RATING_CHANGE)
        self.assertEqual(gci.RATING_CHANGE_MIN_EVIDENCE, 2)
        self.assertEqual(gci.PROPOSAL_DEDUP_DAYS, ae.PROPOSAL_DEDUP_DAYS)
        # 方向语义复用: ae._change_direction 同一函数族
        self.assertEqual(ae._change_direction('标配', '观望'), 'suspend')
        self.assertEqual(ae._change_direction('标配', '超配'), 'upgrade')

    def test_rejected_proposal_dedup_repeat(self):
        """留档复用语义(ae._record_proposal): 同向重提→repeat 累计不新增条目。"""
        p = self._proposal()
        view = {'id': 5, 'rating': '标配'}
        e1 = gci.record_rejected_proposal(view, p, 'r1', TODAY)
        self.assertEqual(e1['repeat'], 1)   # 首登 repeat=1(须在第二次调用前断言:
        # ae._record_proposal 返回的是留档条目本体, 去重命中原地累加 repeat)
        e2 = gci.record_rejected_proposal(view, p, 'r2', TODAY)
        self.assertEqual(e2['repeat'], 2)
        self.assertEqual(len(view['proposals']), 1)

    def test_prediction_candidate_incomplete_rejected(self):
        p = self._proposal(kind='prediction_candidate',
                           change_to={'pred_metric': 'GOLD_F', 'pred_op': '>=',
                                      'pred_mode': 'expiry'})   # 缺 pred_target
        accepted, reason = gci.evaluate_gate_b(p)
        self.assertFalse(accepted)
        self.assertIn("['pred_target']", reason)

    def test_prediction_candidate_complete_accepted(self):
        p = self._proposal(kind='prediction_candidate',
                           change_to={'pred_metric': 'GOLD_F', 'pred_op': '>=',
                                      'pred_target': 4300.0,
                                      'pred_mode': 'expiry'})
        accepted, reason = gci.evaluate_gate_b(p)
        self.assertTrue(accepted)
        self.assertIn('not_yet_triggered', reason)

    def test_proposal_kind_validated(self):
        with self.assertRaises(ValueError):
            self._proposal(kind='deploy_live')


class T3_ConclusionArchive(unittest.TestCase):
    """要点③: append-only 结论记录+交叉引用字段校验。"""

    def _record(self, inp=None, out=None, seq=1, outcome_payload=None):
        inp = inp or build_input()
        if outcome_payload is not None:
            result = {'outcome': 'ACCEPTED_DOWNGRADED',
                      'validated_output': outcome_payload,
                      'absence_event': None}
        else:
            result = run_fixture_pipeline(inp, out or build_output())
        return gci.build_conclusion_record(
            inp, result, gate_b_results=[
                {'hypothesis_id': 'HY-20261102-001', 'kind': 'thesis_status',
                 'accepted': False, 'reason': '终态判定门禁不足(合成)'}],
            seq=seq, today_iso=TODAY)

    def test_pipeline_result_outcome_is_downgraded(self):
        """集成前置: fixture(absent_registry 非空)经 G2 真实管线=径2 受纳。"""
        result = run_fixture_pipeline(build_input(), build_output())
        self.assertEqual(result['outcome'], 'ACCEPTED_DOWNGRADED')

    def test_append_written(self):
        rec = self._record()
        archive = {}
        status, _ = gci.append_conclusion_record(rec, archive)
        self.assertEqual(status, 'written')
        self.assertEqual(len(archive['conclusions']), 1)

    def test_append_idempotent_skip(self):
        rec = self._record()
        archive = {}
        gci.append_conclusion_record(rec, archive)
        s2, _ = gci.append_conclusion_record(dict(rec), archive)
        self.assertEqual(s2, 'skipped-idempotent')
        self.assertEqual(len(archive['conclusions']), 1)

    def test_append_new_version_original_untouched(self):
        rec1 = self._record(seq=1)
        out2 = build_output()
        out2['hypotheses'][0]['statement'] = (
            'TIPS_10Y 实际利率升至 2.93 与 GOLD_F 金价 4186.7 同涨'
            '(修订陈述)')           # 同过 G2;output_digest 随内容变化
        rec2 = self._record(out=out2, seq=1)
        self.assertEqual(rec2['conclusion_id'], rec1['conclusion_id'])
        self.assertNotEqual(rec2['output_digest'], rec1['output_digest'])
        archive = {}
        gci.append_conclusion_record(rec1, archive)
        before = copy.deepcopy(archive['conclusions'][0])
        status, new = gci.append_conclusion_record(rec2, archive)
        self.assertEqual(status, 'written-new-version')
        self.assertEqual(new['conclusion_id'], 'CR-20261105-001__v2')
        self.assertEqual(len(archive['conclusions']), 2)
        self.assertEqual(archive['conclusions'][0], before)   # 原记录不动

    def test_record_rewrite_rejected(self):
        rec = self._record()
        archive = {}
        gci.append_conclusion_record(rec, archive)
        with self.assertRaises(gci.ArchiveImmutable):
            gci.mutate_conclusion_record(archive, rec['conclusion_id'],
                                         {'outcome': 'ACCEPTED'})

    def test_cross_ref_required_both_missing(self):
        inp = build_input()
        inp['task_ref'] = None
        inp['query_ref'] = None
        with self.assertRaises(gci.InvalidConclusionRecord):
            gci.build_conclusion_record(
                inp, run_fixture_pipeline(build_input(), build_output()),
                today_iso=TODAY)

    def test_cross_ref_bad_prefixes(self):
        inp = build_input()
        inp['task_ref']['task_id'] = 'XX-20261102-001'
        with self.assertRaises(gci.InvalidConclusionRecord):
            gci.build_conclusion_record(
                inp, run_fixture_pipeline(build_input(), build_output()),
                today_iso=TODAY)
        inp_b = build_input_mode_b()
        inp_b['query_ref']['query_id'] = 'RT-20261102-001'
        with self.assertRaises(gci.InvalidConclusionRecord):
            gci.build_conclusion_record(
                inp_b, {'outcome': 'ACCEPTED', 'validated_output':
                        {'phenomenon_echo': 'x', 'explanation': 'y',
                         'absent_ack': []}}, today_iso=TODAY)

    def test_hypothesis_id_format_checked(self):
        inp = build_input()
        out = build_output()
        out['hypotheses'][0]['hypothesis_id'] = 'BAD-1'
        with self.assertRaises(gci.InvalidConclusionRecord):
            gci.build_conclusion_record(
                inp, {'outcome': 'ACCEPTED', 'validated_output': out,
                      'absence_event': None}, today_iso=TODAY)

    def test_conclusion_id_format_checked(self):
        archive = {}
        with self.assertRaises(gci.InvalidConclusionRecord):
            gci.append_conclusion_record(
                {'conclusion_id': 'CR-bad', 'task_id': 'RT-1',
                 'origin_query_id': None, 'output_digest': 'd' * 16},
                archive)

    def test_conclusion_record_fields_and_binding(self):
        rec = self._record()
        self.assertEqual(set(rec.keys()),
                         {'conclusion_id', 'hypothesis_ids', 'task_id',
                          'origin_query_id', 'snapshot_id', 'snapshot_digest',
                          'outcome', 'output_digest', 'gate_b_verdicts',
                          'falsifiable_spec_count', 'created_at'})
        self.assertEqual(rec['conclusion_id'], 'CR-20261105-001')
        self.assertEqual(rec['task_id'], TASK_ID)
        self.assertIsNone(rec['origin_query_id'])
        self.assertEqual(rec['snapshot_id'], SNAP_ID)
        self.assertEqual(rec['snapshot_digest'], SNAP_DIGEST)
        self.assertEqual(rec['outcome'], 'ACCEPTED_DOWNGRADED')
        self.assertEqual(rec['hypothesis_ids'],
                         ['HY-20261102-001', 'HY-20261102-002'])
        self.assertEqual(rec['falsifiable_spec_count'], 2)
        # output_digest 独立复算(标准库,非被测模块导入)
        expect = hashlib.sha256(json.dumps(
            build_output(), ensure_ascii=False, sort_keys=True)
            .encode('utf-8')).hexdigest()[:16]
        self.assertEqual(rec['output_digest'], expect)
        self.assertEqual(len(rec['output_digest']), 16)
        self.assertEqual(rec['gate_b_verdicts'][0]['accepted'], False)


class T4_E2EAFieldMapContract(unittest.TestCase):
    """要点④: E2E-A 字段映射契约测试(rtm.SCHEMA_MIN_FIELDS 契约同源)。"""

    def test_schema_min_fields_reused_literal(self):
        self.assertEqual(rtm.SCHEMA_MIN_FIELDS,
                         ['task_id', 'created_at', 'phenomenon', 'status',
                          'indicators', 'window', 'detection', 'evidence',
                          'falsifiable_conditions', 'history'])

    def test_field_map_nine_rows_literal(self):
        self.assertEqual(len(gci.E2EA_FIELD_MAP), 9)
        rows = {r[0]: r for r in gci.E2EA_FIELD_MAP}
        self.assertIn('task_ref.task_id', rows)
        self.assertEqual(rows['task_ref.task_id'][1], 'task_id')
        self.assertIn('statement', rows)
        self.assertEqual(rows['statement'][1], 'history(追加记录文本)')
        self.assertIn('任务状态推进(pending→active→concluded→tracking)', rows)

    def _proj(self, **kw):
        inp = build_input()
        out = build_output()
        base = dict(evidence_map=None, proposals=(), gate_results=(),
                    today_iso=TODAY)
        base.update(kw)
        return gci.build_e2ea_projection(inp, out, **base)

    def test_projection_task_id_passthrough(self):
        self.assertEqual(self._proj()['task_id'], TASK_ID)

    def test_projection_echo_fields_verbatim(self):
        echo = self._proj()['echo_fields']
        inp = build_input()
        tref = inp['task_ref']
        self.assertEqual(echo['phenomenon'], tref['phenomenon'])
        self.assertEqual(echo['indicators'], tref['indicators'])
        self.assertEqual(echo['window'], tref['window'])
        self.assertEqual(echo['detection'], tref['detection'])

    def test_projection_history_append_lines(self):
        lines = self._proj()['history_append_lines']
        self.assertEqual(len(lines), 2)
        self.assertIn('[HY-20261102-001]', lines[0])
        self.assertIn('流动性共同驱动假设', lines[0])
        self.assertIn('confidence=high', lines[0])
        self.assertIn('JGB_10Y', lines[0])

    def test_projection_evidence_refs_directional(self):
        refs = self._proj()['evidence_refs']
        self.assertEqual(len(refs), 4)
        dirs = {r['direction'] for r in refs}
        self.assertEqual(dirs, {'support', 'counter'})
        for r in refs:
            self.assertEqual(r['quality_status'], 'PASS')
            self.assertEqual(r['snapshot_id'], SNAP_ID)
            self.assertEqual(r['snapshot_digest'], SNAP_DIGEST)
            self.assertIn(r['fact_id'],
                          ('TIPS_10Y@2026-10-29', 'GOLD_F@2026-10-29'))

    def test_projection_direction_enum_three_values(self):
        inp = build_input()
        out = build_output()
        emap = {'snapshot_id': SNAP_ID, 'snapshot_digest': SNAP_DIGEST,
                'rows': [{'hypothesis_id': 'HY-20261102-001',
                          'fact_id': 'TIPS_10Y@2026-10-29',
                          'metric_id': 'TIPS_10Y', 'direction': 'neutral',
                          'quality_status': 'PASS', 'snapshot_id': SNAP_ID,
                          'snapshot_digest': SNAP_DIGEST}]}
        proj = gci.build_e2ea_projection(inp, out, evidence_map=emap)
        self.assertEqual(proj['evidence_refs'][0]['direction'], 'neutral')
        emap_bad = copy.deepcopy(emap)
        emap_bad['rows'][0]['direction'] = 'up'
        with self.assertRaises(ValueError):
            gci.build_e2ea_projection(inp, out, evidence_map=emap_bad)

    def test_projection_conditions_merge_specifiable_subset(self):
        merge = self._proj()['falsifiable_conditions_merge']
        self.assertEqual(len(merge), 2)
        for m in merge:
            self.assertEqual(set(m['spec'].keys()),
                             {'metric', 'op', 'target', 'mode', 'window'})
        self.assertEqual(merge[0]['spec']['metric'], 'TIPS_10Y')
        self.assertEqual(merge[1]['spec']['metric'], 'GOLD_F')

    def test_projection_prediction_candidates_fields(self):
        cands = self._proj()['prediction_candidates']
        self.assertEqual(len(cands), 2)
        c0 = cands[0]
        self.assertEqual(set(c0.keys()),
                         {'source_hypothesis_id', 'pred_metric', 'pred_op',
                          'pred_target', 'pred_mode', 'window',
                          'initial_status'})
        self.assertEqual(c0['pred_metric'], 'TIPS_10Y')
        self.assertEqual(c0['pred_op'], '>=')
        self.assertEqual(c0['pred_target'], 2.93)
        self.assertEqual(c0['pred_mode'], 'expiry')
        self.assertEqual(c0['initial_status'], 'not_yet_triggered')
        self.assertEqual(c0['window'], dict(WIN))

    def test_projection_status_is_proposal(self):
        sp = self._proj(
            proposals=[{'kind': 'thesis_status', 'change_to': '已验证'}])['status_proposal']
        self.assertIn('提案', sp['current_status_note'])
        self.assertIn('pending→active→concluded→tracking',
                      sp['current_status_note'])
        self.assertEqual(sp['proposals'][0]['change_to'], '已验证')

    def test_projection_mode_b_trimmed(self):
        inp = build_input_mode_b()
        out = {'phenomenon_echo': 'TIPS_10Y与GOLD_F为何同涨? ……',
               'explanation': '接地解释(合成)', 'absent_ack': []}
        proj = gci.build_e2ea_projection(inp, out)
        self.assertEqual(set(proj.keys()),
                         {'origin_query_id', 'conclusions', 'mode_b_note'})
        self.assertEqual(proj['origin_query_id'], 'QB-20261102-001')
        self.assertIn('promoted_to_task_id', proj['mode_b_note'])

    def test_projection_covers_schema_min_fields(self):
        """契约承接: 最低字段集 10 字段中 9 个有映射行承接;created_at 任务侧权威。"""
        covered = {'task_id',                     # 投影 task_id 透传
                   'phenomenon', 'indicators', 'window', 'detection',  # echo
                   'history',                     # history_append_lines+conclusions
                   'evidence',                    # evidence_refs
                   'falsifiable_conditions',      # conditions_merge
                   'status'}                      # status_proposal(提案制)
        self.assertEqual(set(rtm.SCHEMA_MIN_FIELDS) - {'created_at'},
                         covered)


class T5_EchoParams(unittest.TestCase):
    """登记参数 echo=常量=登记值(R011 三方一致;REPORT §二 登记表)。"""

    def test_echo_params_literal(self):
        self.assertEqual(gci.echo_params(), {
            'derivation_steps': ['variableize', 'threshold', 'specification',
                                 'distinctiveness'],
            'threshold_sources': ['evidence_pack', 'registry',
                                  'prior_triggers'],
            'spec_keys': ['metric', 'op', 'target', 'mode', 'window'],
            'spec_ops': ['>', '>=', '<', '<='],
            'spec_modes': ['touch', 'expiry'],
            'non_specifiable_marker': '不可程序裁决',
            'proposal_kinds': ['thesis_status', 'thesis_confidence',
                               'view_rating', 'view_confidence',
                               'prediction_candidate'],
            'thesis_terminal_states': ['已失效', '已验证'],
            'rating_change_min_evidence': 2,
            'proposal_dedup_days': 21,
            'pred_initial_status': 'not_yet_triggered',
            'pred_candidate_spec_keys': ['pred_metric', 'pred_op',
                                         'pred_target', 'pred_mode'],
            'directions': ['support', 'counter', 'neutral'],
            'outcomes': ['ACCEPTED', 'ACCEPTED_DOWNGRADED',
                         'ABSENT_REGISTERED'],
            'e2ea_map_rows': 9,
            'default_derive_op': '>=',
            'default_derive_mode': 'expiry',
            'threshold_source_precedence': ['evidence_pack', 'registry',
                                            'prior_triggers'],
            'derived_window_order': ['week', 'mtd', 'ytd'],
            'conditions_per_metric': 1,
            'conclusion_fingerprint_keys': ['conclusion_id', 'output_digest'],
            'archive_replay_policy': ('idempotent-skip on identical '
                                      'fingerprint; new record appended on '
                                      'different fingerprint; existing '
                                      'records never rewritten'),
            'gate_b_blocked_classification': 'FAIL',
            'output_digest_len': 16,
            'e2ea_conclusions_key': 'conclusions',
            'prior_trigger_keys': ['trig_id', 'metric', 'op', 'target'],
        })


class T6_SourceBoundaryLock(unittest.TestCase):
    """源码边界锁: 零网络/零凭证/零文件读写/零原始档字样+复用导入标记。"""

    def test_source_boundary_lock(self):
        src_path = os.path.join(ROOT, 'scripts', 'glm_conclusion_integrator.py')
        with open(src_path, 'r', encoding='utf-8') as f:
            src = f.read()
        for banned in ('import requests', 'urllib', 'socket', 'http.client',
                       'GLM_API_KEY', 'api_key', 'sk-', 'data/daily',
                       'data\\daily', 'os.listdir', 'glob.', 'subprocess',
                       'os.system', 'shutil', 'open(', 'write('):
            self.assertNotIn(banned, src, f'边界锁违规: {banned}')
        for required in ('import allocation_engine as ae',
                         'import glm_output_validator as gov',
                         'import research_provenance as rp',
                         'import research_task_manager as rtm',
                         'ae.MIN_EVIDENCE_FOR_RATING_CHANGE',
                         'ae._record_proposal(', 'ae._change_direction(',
                         'rp.combine_gates(', 'gov.validate_output(',
                         'gov.SPEC_OPS', 'rtm.STATUS_FLOW'):
            self.assertIn(required, src, f'复用标记缺失: {required}')


if __name__ == '__main__':
    unittest.main()
