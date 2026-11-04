# -*- coding: utf-8 -*-
"""IA-P03-W2-GLM-WP-G2(结构化输出契约与校验器)专项测试。

合同 IA-P03-W2-GLM-WP-G2-AC-v1.0 / DESIGN §七 WP-G2 验收要点行为锁:
- 要点① schema 正向用例: 模式A七字段全量/模式B裁剪三字段/解析器围栏与注释
  包裹容忍/假设-证据映射表字面量(T1/T1b);
- 要点② 负向敏感性: counter_evidence 空/数值不在输入证据包(含数值被改写)/
  竞争假设无区分性判据/缺席未承接(absent_ack+limitations)——各须被拒(T2);
- 要点③ 阈值取值约束: 编造 target 被拒+三合法来源((i)证据包/(ii)注册表/
  (iii)先验触发器注入)逐一通过+注册表字段族提取(T3);
- 要点④ 失败三径状态机: 径1重试(瞬态/解析/校验失败→反馈+线性退避计划表)→
  径2降级(gate DEGRADED/缺席在场→义务强制受纳)→径3缺席登记(重试耗尽/
  费用熔断即时/未知类fail-closed→缺席事件,状态不推进)全路径(T4);
- 数值抽取豁免族直测(T5);登记参数 echo=常量=登记值+G1 模块复用身份(T6);
- 源码边界锁: 零网络/零凭证/零文件读取/零原始档字样+复用导入标记(T7)。

数据纪律(R014-D3/R022 沿用): 全部离线合成 fixture=唯一数据源——GLMResearchInput
与 HypothesisSet 均为内联字面量合成(数值锚点 2.93/4186.7 为 E2E-A 登记窗终值
语义的合成复用,不代表任何真实交易日数据);注册表/先验触发器一律注入合成集,
真实 config/metric_registry.json、thesis.json 永不进入测试预期值来源;预期值
一律字面量硬编码(不从被测模块导入计算——自证恒真是 F 反例)。零网络/零新增
第三方依赖。零真实 GLM 调用(attempts=本地合成桩,注入面)。
"""
import copy
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import glm_output_validator as gov      # noqa: E402 (被测模块)
import glm_input_assembler as gia       # noqa: E402 (G1 契约复用对照/fixture 自检)
import research_provenance as rp        # noqa: E402 (T3 monkeypatch 注入面)

# ══ 合成 fixture(唯一数据源;字面量锚点) ════════════════════════════════════
SNAP_ID = 'research_snapshot_20261029'
SNAP_DIGEST = 'a1b2c3d4e5f60718'
VAL_TIPS = 2.93
VAL_GOLD = 4186.7

TIPS_FACT = {
    'metric_id': 'TIPS_10Y', 'fact_id': 'TIPS_10Y@2026-10-29', 'value': 2.93,
    'unit': 'percent', 'observation_date': '2026-10-29', 'quality_status': 'PASS',
    'source_file': 'macro_20261029.json',
    'derived': {'end': {'date': '2026-10-29', 'value': 2.93,
                        'sessions_available': 5},
                'week': {'basis_date': '2026-10-22', 'basis_value': 2.20,
                         'pp_change': 0.73, 'bp_change': 73.0}},
}
GOLD_FACT = {
    'metric_id': 'GOLD_F', 'fact_id': 'GOLD_F@2026-10-29', 'value': 4186.7,
    'unit': 'usd', 'observation_date': '2026-10-29', 'quality_status': 'PASS',
    'source_file': 'global_20261029.json',
    'derived': {'week': {'basis_date': '2026-10-22', 'basis_value': 4161.7,
                         'pct_change': 3.7}},
}
# 合成注册表阈值(来源(ii)注入面;真实 config 不入测试)
REG_SYN = {'SPX': {'metric_id': 'SPX',
                   'validation': {'range': [1000, 30000],
                                  'max_week_pct_move': 25}}}
REG_TARGETS = {1000, 30000, 25}
PRIOR_TRIGGERS = [4.5, 4300]           # 来源(iii)合成先验触发器(thesis/views 语义)

MISSING_REF = {'status': 'MISSING', 'reason': '合成fixture显式缺席'}


def build_input_mode_a(gate='PASS', absent=True):
    """合成 GLMResearchInput(模式A;经 gia.validate_input 自检=T0)。"""
    indicators = ['TIPS_10Y', 'GOLD_F'] + (['JGB_10Y'] if absent else [])
    return {
        'contract_version': 'gri-1.0',
        'mode': 'A',
        'snapshot_binding': {
            'snapshot_id': SNAP_ID, 'snapshot_digest': SNAP_DIGEST,
            'gate_a': gate, 'research_as_of': '2026-10-29'},
        'task_ref': {
            'task_id': 'RT-20261029-001',
            'phenomenon': 'TIPS_10Y 实际利率与 GOLD_F 同涨背离',
            'indicators': indicators,
            'window': {'start': '2026-06-30', 'end': '2026-09-30'},
            'detection': {'rule': 'RD-DIV-001', 'score': 65.0},
            'history_tail': []},
        'query_ref': None,
        'evidence_pack': {
            'facts': [copy.deepcopy(TIPS_FACT), copy.deepcopy(GOLD_FACT)],
            'scorecard_summary': dict(MISSING_REF),
            'correlation_ref': dict(MISSING_REF),
            'news_index_ref': dict(MISSING_REF)},
        'absent_registry': ([{'metric_id': 'JGB_10Y',
                              'level': 'ABSENT_REGISTRY',
                              'reason': '指标不在注册表(合成fixture)'}]
                            if absent else []),
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
    inp = build_input_mode_a(absent=False)
    inp['mode'] = 'B'
    inp['task_ref'] = None
    inp['query_ref'] = {'query_id': 'QB-20261029-001',
                        'question_text': 'TIPS_10Y与GOLD_F为何背离?',
                        'as_of': '2026-10-29',
                        'metric_bindings_digest': 'b2c3d4e5f60718a9',
                        'derived_ops_digest': 'c3d4e5f60718a9b0'}
    return inp


def build_valid_output_mode_a(absent=True):
    """合成 HypothesisSet(模式A全量七字段;两竞争假设,判据四元组相异)。"""
    return {
        'hypotheses': [
            {'hypothesis_id': 'HY-20261029-001',
             'statement': '实际利率上行压制黄金: TIPS_10Y 周内升至2.93,持有黄金机会成本上升',
             'supporting_evidence': [
                 {'fact_id': 'TIPS_10Y@2026-10-29', 'metric_id': 'TIPS_10Y',
                  'direction_note': 'TIPS_10Y 自2.20升至2.93,周+73bp'}],
             'counter_evidence': [
                 {'fact_id': 'GOLD_F@2026-10-29', 'metric_id': 'GOLD_F',
                  'direction_note': '同期GOLD_F周涨3.7%,与利率压制方向相悖'}],
             'falsifiable_conditions': [
                 {'cond_text': '若TIPS_10Y升至4.5上方,黄金应承压',
                  'spec': {'metric': 'TIPS_10Y', 'op': '>=', 'target': 4.5,
                           'mode': 'expiry',
                           'window': {'start': '2026-06-30',
                                      'end': '2026-09-30'}}}],
             'confidence': 'high',
             'limitations': ['缺席指标JGB_10Y未纳入本假设证据面(缺席如实登记)',
                             '未覆盖的替代解释见HY-20261029-002']},
            {'hypothesis_id': 'HY-20261029-002',
             'statement': '避险需求主导: 金价4186.7上行与避险买盘同升,利率敏感度下降',
             'supporting_evidence': [
                 {'fact_id': 'GOLD_F@2026-10-29', 'metric_id': 'GOLD_F',
                  'direction_note': 'GOLD_F 现值4186.7,周+3.7%'}],
             'counter_evidence': [
                 {'fact_id': 'TIPS_10Y@2026-10-29', 'metric_id': 'TIPS_10Y',
                  'direction_note': '实际利率2.93高位,传统定价框架构成反证'}],
             'falsifiable_conditions': [
                 {'cond_text': '若GOLD_F回落至4300下方,避险主导解释弱化',
                  'spec': {'metric': 'GOLD_F', 'op': '<=', 'target': 4300,
                           'mode': 'touch',
                           'window': {'start': '2026-06-30',
                                      'end': '2026-09-30'}}}],
             'confidence': 'medium',
             'limitations': ['缺席指标JGB_10Y相关传导未覆盖(缺席如实登记)',
                             '未覆盖的替代解释见HY-20261029-001']},
        ],
        'phenomenon_echo': 'TIPS_10Y 实际利率与 GOLD_F 同涨背离(现象复述)',
        'absent_ack': (['JGB_10Y 缺席(ABSENT_REGISTRY: 不在注册表)']
                       if absent else []),
    }


def build_valid_output_mode_b():
    """合成模式B裁剪版(§六: phenomenon_echo+grounded解释+absent_ack)。"""
    return {
        'phenomenon_echo': '问题: TIPS_10Y与GOLD_F为何背离?',
        'explanation': 'TIPS_10Y 周内自2.20升至2.93(+73bp);GOLD_F 同期4186.7,'
                       '周+3.7%——背离可由避险需求解释',
        'absent_ack': [],
    }


def valid_out_with_degraded_ack(absent=True):
    out = build_valid_output_mode_a(absent=absent)
    for h in out['hypotheses']:
        h['limitations'].append(
            '输入Gate A=DEGRADED,证据面降级影响已逐项承接(降级径承接义务)')
    return out


def _v(inp, out):
    """校验便捷入口(注入合成来源(ii)(iii);真实 config 永不入测试)。"""
    return gov.validate_output(inp, out, registry_targets=REG_TARGETS,
                               prior_trigger_targets=PRIOR_TRIGGERS)


EVIDENCE_MAP_LITERAL = {
    'snapshot_id': SNAP_ID,
    'snapshot_digest': SNAP_DIGEST,
    'rows': [
        {'hypothesis_id': 'HY-20261029-001', 'fact_id': 'TIPS_10Y@2026-10-29',
         'metric_id': 'TIPS_10Y', 'direction': 'support',
         'quality_status': 'PASS', 'snapshot_id': SNAP_ID,
         'snapshot_digest': SNAP_DIGEST},
        {'hypothesis_id': 'HY-20261029-001', 'fact_id': 'GOLD_F@2026-10-29',
         'metric_id': 'GOLD_F', 'direction': 'counter',
         'quality_status': 'PASS', 'snapshot_id': SNAP_ID,
         'snapshot_digest': SNAP_DIGEST},
        {'hypothesis_id': 'HY-20261029-002', 'fact_id': 'GOLD_F@2026-10-29',
         'metric_id': 'GOLD_F', 'direction': 'support',
         'quality_status': 'PASS', 'snapshot_id': SNAP_ID,
         'snapshot_digest': SNAP_DIGEST},
        {'hypothesis_id': 'HY-20261029-002', 'fact_id': 'TIPS_10Y@2026-10-29',
         'metric_id': 'TIPS_10Y', 'direction': 'counter',
         'quality_status': 'PASS', 'snapshot_id': SNAP_ID,
         'snapshot_digest': SNAP_DIGEST},
    ],
}

ECHO_LITERAL = {
    'output_schema_version': 'hs-1.0',
    'hypothesis_fields': ['hypothesis_id', 'statement', 'supporting_evidence',
                          'counter_evidence', 'falsifiable_conditions',
                          'confidence', 'limitations'],
    'top_level_fields': ['hypotheses', 'phenomenon_echo', 'absent_ack'],
    'mode_b_fields': ['phenomenon_echo', 'explanation', 'absent_ack'],
    'evidence_ref_fields': ['fact_id', 'metric_id', 'direction_note'],
    'condition_fields': ['cond_text', 'spec'],
    'spec_fields': ['metric', 'op', 'target', 'mode', 'window'],
    'spec_required_fields': ['metric', 'op', 'target', 'mode'],
    'spec_ops': ['>', '>=', '<', '<='],
    'spec_modes': ['touch', 'expiry'],
    'confidence_enum': ['high', 'medium', 'low'],
    'directions': ['support', 'counter', 'neutral'],
    'non_specifiable_marker': '不可程序裁决',
    'degraded_ack_markers': ['DEGRADED', '降级'],
    'transient_error_kinds': ['network', 'risk_control', 'stream_interrupted'],
    'cost_breaker_kind': 'cost_breaker',
    'registry_threshold_keys': ['range', 'max_week_pct_move'],
    'derived_value_keys': ['value', 'pct_change', 'pp_change', 'bp_change',
                           'abs_change', 'basis_value'],
    'max_retries': 3,
    'backoff_linear_base': 1.0,
    'outcome_accepted': 'ACCEPTED',
    'outcome_accepted_downgraded': 'ACCEPTED_DOWNGRADED',
    'outcome_absent_registered': 'ABSENT_REGISTERED',
}


# ══ T0 fixture 自检(合成输入经 G1 契约回读=合法 GLMResearchInput) ══════════
class T0_FixtureSanity(unittest.TestCase):
    def test_mode_a_input_passes_g1_contract(self):
        self.assertEqual(gia.validate_input(build_input_mode_a()), [])

    def test_mode_b_input_passes_g1_contract(self):
        self.assertEqual(gia.validate_input(build_input_mode_b()), [])


# ══ T1 要点①: schema 正向用例 ═══════════════════════════════════════════════
class T1_SchemaPositive(unittest.TestCase):
    def test_valid_mode_a_output_passes(self):
        self.assertEqual(
            _v(build_input_mode_a(), build_valid_output_mode_a()), [])

    def test_valid_mode_a_pure_input_passes(self):
        inp = build_input_mode_a(absent=False)
        self.assertEqual(
            _v(inp, build_valid_output_mode_a(absent=False)), [])

    def test_valid_mode_b_output_passes(self):
        self.assertEqual(
            _v(build_input_mode_b(), build_valid_output_mode_b()), [])

    def test_evidence_map_rows_literal(self):
        emap = gov.build_hypothesis_evidence_map(
            build_input_mode_a(), build_valid_output_mode_a(),
            registry_targets=REG_TARGETS, prior_trigger_targets=PRIOR_TRIGGERS)
        self.assertEqual(emap, EVIDENCE_MAP_LITERAL)

    def test_evidence_map_mode_b_returns_none(self):
        self.assertIsNone(gov.build_hypothesis_evidence_map(
            build_input_mode_b(), build_valid_output_mode_b(),
            registry_targets=REG_TARGETS, prior_trigger_targets=PRIOR_TRIGGERS))

    def test_evidence_map_invalid_output_raises(self):
        out = build_valid_output_mode_a()
        out['hypotheses'][0]['counter_evidence'] = []
        with self.assertRaises(gov.InvalidOutput):
            gov.build_hypothesis_evidence_map(
                build_input_mode_a(), out, registry_targets=REG_TARGETS,
                prior_trigger_targets=PRIOR_TRIGGERS)


# ══ T1b 解析面容忍(DESIGN L82: 围栏/注释包裹容忍,字段缺失不容忍) ═══════════
class T1b_ParserTolerance(unittest.TestCase):
    def test_parse_bare_json(self):
        obj, err = gov.parse_hypothesis_set('{"a": 1}')
        self.assertEqual(obj, {'a': 1})
        self.assertIsNone(err)

    def test_parse_fenced_json(self):
        obj, err = gov.parse_hypothesis_set('```json\n{"a": 1}\n```')
        self.assertEqual(obj, {'a': 1})
        self.assertIsNone(err)

    def test_parse_comment_wrapped(self):
        obj, err = gov.parse_hypothesis_set('<!--\n{"a": 1}\n-->')
        self.assertEqual(obj, {'a': 1})
        self.assertIsNone(err)

    def test_parse_fence_inside_comment(self):
        obj, err = gov.parse_hypothesis_set('<!-- ```json {"a": 1}``` -->')
        self.assertEqual(obj, {'a': 1})
        self.assertIsNone(err)

    def test_parse_non_dict_top_rejected(self):
        obj, err = gov.parse_hypothesis_set('[1, 2]')
        self.assertIsNone(obj)
        self.assertIn('单一JSON对象', err)

    def test_parse_garbage_rejected(self):
        obj, err = gov.parse_hypothesis_set('不是JSON')
        self.assertIsNone(obj)
        self.assertIn('JSON解析失败', err)

    def test_parse_empty_rejected(self):
        obj, err = gov.parse_hypothesis_set('   ')
        self.assertIsNone(obj)
        self.assertIn('空', err)


# ══ T2 要点②: 负向敏感性用例(各须被拒) ═════════════════════════════════════
class T2_NegativeSensitivity(unittest.TestCase):
    def _inp(self):
        return build_input_mode_a()

    def _out(self):
        return build_valid_output_mode_a()

    @staticmethod
    def _join(probs):
        return ' | '.join(probs)

    def test_counter_evidence_empty_rejected(self):
        out = self._out()
        out['hypotheses'][0]['counter_evidence'] = []
        probs = _v(self._inp(), out)
        self.assertIn('counter_evidence为空', self._join(probs))

    def test_statement_value_not_in_evidence_pack_rejected(self):
        out = self._out()
        out['hypotheses'][0]['statement'] = (
            '实际利率上行: TIPS_10Y 周内升至9.99(编造值)')
        probs = _v(self._inp(), out)
        self.assertIn('statement数值不在输入证据包', self._join(probs))

    def test_direction_note_rewritten_value_rejected(self):
        out = self._out()
        out['hypotheses'][0]['supporting_evidence'][0]['direction_note'] = (
            'TIPS_10Y 自2.20升至2.94(数值被改写)')
        probs = _v(self._inp(), out)
        self.assertIn('direction_note数值不在输入证据包', self._join(probs))

    def test_no_distinctiveness_rejected(self):
        out = self._out()
        out['hypotheses'][1]['falsifiable_conditions'][0] = {
            'cond_text': '若TIPS_10Y升至4.5上方(与竞争假设同判据)',
            'spec': {'metric': 'TIPS_10Y', 'op': '>=', 'target': 4.5,
                     'mode': 'expiry',
                     'window': {'start': '2026-06-30', 'end': '2026-09-30'}}}
        probs = _v(self._inp(), out)
        self.assertIn('竞争性不足', self._join(probs))
        self.assertIn('仅措辞不同而无判据区分', self._join(probs))

    def test_absent_not_acked_rejected(self):
        out = self._out()
        out['absent_ack'] = []
        probs = _v(self._inp(), out)
        self.assertIn('absent_ack未逐项复述缺席指标', self._join(probs))
        self.assertIn('JGB_10Y', self._join(probs))

    def test_absent_not_in_limitations_rejected(self):
        out = self._out()
        out['hypotheses'][0]['limitations'] = [
            '未覆盖的替代解释见HY-20261029-002']
        probs = _v(self._inp(), out)
        self.assertIn('limitations未承接缺席指标', self._join(probs))

    def test_fact_id_not_in_input_rejected(self):
        out = self._out()
        out['hypotheses'][0]['supporting_evidence'][0]['fact_id'] = \
            'UST_10Y@2026-10-29'
        probs = _v(self._inp(), out)
        self.assertIn('fact_id不在输入证据包', self._join(probs))

    def test_metric_id_mismatch_rejected(self):
        out = self._out()
        out['hypotheses'][0]['supporting_evidence'][0]['metric_id'] = 'GOLD_F'
        probs = _v(self._inp(), out)
        self.assertIn('metric_id与在场事实身份不符', self._join(probs))

    def test_hypothesis_id_format_rejected(self):
        out = self._out()
        out['hypotheses'][0]['hypothesis_id'] = 'HY-20261029-1'
        probs = _v(self._inp(), out)
        self.assertIn('hypothesis_id格式非法', self._join(probs))

    def test_hypothesis_id_cross_date_rejected(self):
        out = self._out()
        out['hypotheses'][1]['hypothesis_id'] = 'HY-20261030-002'
        probs = _v(self._inp(), out)
        self.assertIn('同日序列', self._join(probs))

    def test_hypothesis_id_duplicate_rejected(self):
        out = self._out()
        out['hypotheses'][1]['hypothesis_id'] = 'HY-20261029-001'
        probs = _v(self._inp(), out)
        self.assertIn('hypothesis_id集内重复', self._join(probs))

    def test_single_hypothesis_rejected(self):
        out = self._out()
        out['hypotheses'] = out['hypotheses'][:1]
        probs = _v(self._inp(), out)
        self.assertIn('竞争假设数不足', self._join(probs))

    def test_confidence_high_with_nonspec_rejected(self):
        out = self._out()
        out['hypotheses'][0]['falsifiable_conditions'].append(
            {'cond_text': '若日本央行制度转向', 'spec': None})
        out['hypotheses'][0]['limitations'].append(
            '不可程序裁决: 制度变化类条件无法规格化,如实区分')
        probs = _v(self._inp(), out)
        self.assertIn('confidence=high但存在不可程序核验条件',
                      self._join(probs))
        self.assertNotIn('未声明不可程序裁决条件', self._join(probs))

    def test_nonspec_with_declaration_allowed(self):
        out = self._out()
        out['hypotheses'][0]['falsifiable_conditions'].append(
            {'cond_text': '若日本央行制度转向', 'spec': None})
        out['hypotheses'][0]['limitations'].append(
            '不可程序裁决: 制度变化类条件无法规格化,如实区分')
        out['hypotheses'][0]['confidence'] = 'medium'
        self.assertEqual(_v(self._inp(), out), [])

    def test_nonspec_without_declaration_rejected(self):
        out = self._out()
        out['hypotheses'][1]['falsifiable_conditions'].append(
            {'cond_text': '若日本央行制度转向', 'spec': None})
        probs = _v(self._inp(), out)
        self.assertIn('未声明不可程序裁决条件', self._join(probs))

    def test_target_null_with_declaration_allowed(self):
        out = self._out()
        out['hypotheses'][0]['falsifiable_conditions'].append(
            {'cond_text': '若政策转向(阈值未定)',
             'spec': {'metric': 'TIPS_10Y', 'op': '>=', 'target': None,
                      'mode': 'expiry'}})
        out['hypotheses'][0]['limitations'].append(
            '不可程序裁决: 目标阈值未定,待先验触发器登记后规格化')
        out['hypotheses'][0]['confidence'] = 'medium'
        self.assertEqual(_v(self._inp(), out), [])

    def test_target_null_without_declaration_rejected(self):
        out = self._out()
        out['hypotheses'][0]['falsifiable_conditions'].append(
            {'cond_text': '若政策转向(阈值未定)',
             'spec': {'metric': 'TIPS_10Y', 'op': '>=', 'target': None,
                      'mode': 'expiry'}})
        out['hypotheses'][0]['confidence'] = 'medium'
        probs = _v(self._inp(), out)
        self.assertIn('未声明不可程序裁决条件', self._join(probs))

    def test_target_string_invalid_rejected(self):
        out = self._out()
        out['hypotheses'][0]['falsifiable_conditions'][0]['spec']['target'] = \
            '4.5'
        probs = _v(self._inp(), out)
        self.assertIn('spec.target非法(须数值或null)', self._join(probs))

    def test_absent_involvement_high_conf_rejected(self):
        out = self._out()
        out['hypotheses'][0]['statement'] = (
            'JGB_10Y缺席下实际利率上行压制黄金: TIPS_10Y 周内升至2.93')
        probs = _v(self._inp(), out)
        self.assertIn('实质字段涉及缺席指标JGB_10Y', self._join(probs))

    def test_supporting_empty_non_low_rejected(self):
        out = self._out()
        out['hypotheses'][0]['supporting_evidence'] = []
        out['hypotheses'][0]['confidence'] = 'medium'
        probs = _v(self._inp(), out)
        self.assertIn('supporting_evidence为空仅容confidence=low',
                      self._join(probs))

    def test_supporting_empty_low_allowed(self):
        out = self._out()
        out['hypotheses'][0]['supporting_evidence'] = []
        out['hypotheses'][0]['confidence'] = 'low'
        self.assertEqual(_v(self._inp(), out), [])

    def test_extra_top_level_field_rejected(self):
        out = self._out()
        out['generated_at'] = '2026-10-29T12:00:00Z'
        probs = _v(self._inp(), out)
        self.assertIn('顶层含schema外字段', self._join(probs))

    def test_missing_top_level_field_rejected(self):
        out = self._out()
        del out['absent_ack']
        probs = _v(self._inp(), out)
        self.assertIn('顶层缺必备字段', self._join(probs))

    def test_missing_seven_field_rejected(self):
        out = self._out()
        del out['hypotheses'][0]['confidence']
        probs = _v(self._inp(), out)
        self.assertIn('缺七字段', self._join(probs))

    def test_degraded_without_ack_rejected(self):
        inp = build_input_mode_a(gate='DEGRADED')
        probs = _v(inp, self._out())
        self.assertIn('未承接Gate A降级影响面', self._join(probs))

    def test_degraded_with_ack_allowed(self):
        inp = build_input_mode_a(gate='DEGRADED', absent=False)
        self.assertEqual(_v(inp, valid_out_with_degraded_ack(absent=False)),
                         [])

    def test_alternative_pointer_missing_rejected(self):
        out = self._out()
        out['hypotheses'][0]['limitations'] = [
            '缺席指标JGB_10Y未纳入本假设证据面(缺席如实登记)']
        probs = _v(self._inp(), out)
        self.assertIn('缺未覆盖替代解释指针', self._join(probs))

    def test_spec_metric_not_present_rejected(self):
        out = self._out()
        out['hypotheses'][0]['falsifiable_conditions'][0]['spec']['metric'] = \
            'JGB_10Y'
        probs = _v(self._inp(), out)
        self.assertIn('spec.metric不在输入在场指标集', self._join(probs))

    def test_spec_op_invalid_rejected(self):
        out = self._out()
        out['hypotheses'][0]['falsifiable_conditions'][0]['spec']['op'] = '!='
        probs = _v(self._inp(), out)
        self.assertIn('spec.op非法', self._join(probs))

    def test_spec_mode_invalid_rejected(self):
        out = self._out()
        out['hypotheses'][0]['falsifiable_conditions'][0]['spec']['mode'] = \
            'eod'
        probs = _v(self._inp(), out)
        self.assertIn('spec.mode非法', self._join(probs))

    def test_phenomenon_echo_missing_rejected(self):
        out = self._out()
        out['phenomenon_echo'] = '与任务无关的复述(答非所问)'
        probs = _v(self._inp(), out)
        self.assertIn('未复述任务现象原文', self._join(probs))

    def test_mode_b_hypotheses_rejected(self):
        out = build_valid_output_mode_b()
        out['hypotheses'] = build_valid_output_mode_a()['hypotheses']
        probs = _v(build_input_mode_b(), out)
        self.assertIn('不得携带hypotheses', self._join(probs))

    def test_mode_b_ungrounded_number_rejected(self):
        out = build_valid_output_mode_b()
        out['explanation'] += ';编造幅度5000'
        probs = _v(build_input_mode_b(), out)
        self.assertIn('explanation数值不在输入证据包', self._join(probs))

    def test_mode_b_echo_missing_rejected(self):
        out = build_valid_output_mode_b()
        out['phenomenon_echo'] = '无关回答'
        probs = _v(build_input_mode_b(), out)
        self.assertIn('未复述查询问题原文', self._join(probs))


# ══ T3 要点③: 阈值取值约束(编造被拒+三合法来源通过+registry 引用) ══════════
class T3_ThresholdProvenance(unittest.TestCase):
    @staticmethod
    def _join(probs):
        return ' | '.join(probs)

    def test_fabricated_target_rejected(self):
        out = build_valid_output_mode_a()
        out['hypotheses'][0]['falsifiable_conditions'][0]['spec']['target'] = \
            3.5
        probs = _v(build_input_mode_a(), out)
        self.assertIn('编造阈值,校验器拒绝', self._join(probs))

    def test_source_i_evidence_value_allowed(self):
        out = build_valid_output_mode_a()
        out['hypotheses'][0]['falsifiable_conditions'][0]['spec']['target'] = \
            2.93
        self.assertEqual(_v(build_input_mode_a(), out), [])

    def test_source_ii_registry_allowed(self):
        out = build_valid_output_mode_a()
        out['hypotheses'][0]['falsifiable_conditions'][0]['spec']['target'] = \
            25
        self.assertEqual(_v(build_input_mode_a(), out), [])

    def test_source_iii_prior_trigger_allowed(self):
        out = build_valid_output_mode_a()
        out['hypotheses'][0]['falsifiable_conditions'][0]['spec']['target'] = \
            4300
        self.assertEqual(_v(build_input_mode_a(), out), [])

    def test_registry_extraction_from_synthetic_registry(self):
        orig = rp.active_registry_metrics
        rp.active_registry_metrics = lambda: copy.deepcopy(REG_SYN)
        try:
            self.assertEqual(gov.registry_legal_targets(),
                             {1000, 30000, 25})
        finally:
            rp.active_registry_metrics = orig

    def test_registry_extraction_only_pointnamed_families(self):
        reg = {'X': {'metric_id': 'X',
                     'validation': {'range': [1, 2]},
                     'freshness': {'max_calendar_lag_days': 5}}}
        orig = rp.active_registry_metrics
        rp.active_registry_metrics = lambda: copy.deepcopy(reg)
        try:
            self.assertEqual(gov.registry_legal_targets(), {1, 2})
        finally:
            rp.active_registry_metrics = orig


# ══ T4 要点④: 失败三径状态机(重试→降级→缺席登记全路径) ═════════════════════
class T4_FailurePaths(unittest.TestCase):
    @staticmethod
    def _run(inp, attempts, **kw):
        return gov.run_conclusion_pipeline(
            inp, attempts, registry_targets=REG_TARGETS,
            prior_trigger_targets=PRIOR_TRIGGERS, **kw)

    @staticmethod
    def _raw(out):
        return {'raw': json.dumps(out, ensure_ascii=False)}

    def test_retry_then_accepted(self):
        bad_parse = {'raw': '前缀噪声 不是JSON'}
        bad_valid = build_valid_output_mode_a()
        bad_valid['hypotheses'][0]['counter_evidence'] = []
        inp = build_input_mode_a()
        res = self._run(inp, [bad_parse, {'raw': json.dumps(bad_valid)},
                              self._raw(build_valid_output_mode_a())])
        self.assertEqual(res['outcome'], 'ACCEPTED_DOWNGRADED')
        self.assertEqual(res['attempts_used'], 3)
        self.assertEqual([t['kind'] for t in res['trace']],
                         ['parse', 'validation', 'ok'])
        self.assertIn('counter_evidence', res['trace'][1]['feedback'])
        self.assertEqual(res['trace'][0]['backoff_s'], 1.0)
        self.assertEqual(res['trace'][1]['backoff_s'], 2.0)
        self.assertEqual(res['evidence_map']['rows'],
                         EVIDENCE_MAP_LITERAL['rows'])

    def test_pure_accepted_no_absent(self):
        inp = build_input_mode_a(absent=False)
        res = self._run(inp, [self._raw(build_valid_output_mode_a(False))])
        self.assertEqual(res['outcome'], 'ACCEPTED')
        self.assertEqual(res['attempts_used'], 1)

    def test_degraded_outcome_downgraded(self):
        inp = build_input_mode_a(gate='DEGRADED', absent=False)
        res = self._run(inp, [self._raw(
            valid_out_with_degraded_ack(absent=False))])
        self.assertEqual(res['outcome'], 'ACCEPTED_DOWNGRADED')

    def test_absent_registered_after_retries_exhausted(self):
        res = self._run(build_input_mode_a(),
                        [{'raw': 'x'}, {'raw': 'y'}, {'raw': 'z'}])
        self.assertEqual(res['outcome'], 'ABSENT_REGISTERED')
        self.assertIsNone(res['validated_output'])
        ev = res['absence_event']
        self.assertEqual(ev['task_id'], 'RT-20261029-001')
        self.assertIsNone(ev['origin_query_id'])
        self.assertEqual(ev['snapshot_id'], SNAP_ID)
        self.assertEqual(ev['snapshot_digest'], SNAP_DIGEST)
        self.assertIn('连续重试失败', ev['failure_reason'])
        self.assertEqual(ev['attempts_used'], 3)
        self.assertFalse(ev['task_status_advanced'])
        self.assertFalse(ev['conclusion_produced'])
        self.assertEqual(len(res['trace']), 3)

    def test_validation_persistent_failure_absent_registered(self):
        bad = build_valid_output_mode_a()
        bad['hypotheses'][0]['counter_evidence'] = []
        att = {'raw': json.dumps(bad)}
        res = self._run(build_input_mode_a(), [att, dict(att), dict(att)])
        self.assertEqual(res['outcome'], 'ABSENT_REGISTERED')
        self.assertIn('连续重试失败', res['absence_event']['failure_reason'])
        self.assertIn('counter_evidence', res['trace'][0]['feedback'])

    def test_cost_breaker_immediate_absent(self):
        res = self._run(build_input_mode_a(),
                        [{'error': '额度耗尽', 'kind': 'cost_breaker'},
                         self._raw(build_valid_output_mode_a())])
        self.assertEqual(res['outcome'], 'ABSENT_REGISTERED')
        self.assertEqual(res['attempts_used'], 1)
        self.assertIn('费用熔断', res['absence_event']['failure_reason'])
        self.assertEqual(len(res['trace']), 1)

    def test_unknown_kind_fail_closed(self):
        res = self._run(build_input_mode_a(),
                        [{'error': '怪异失败', 'kind': 'weird'}])
        self.assertEqual(res['outcome'], 'ABSENT_REGISTERED')
        self.assertIn('未知失败类', res['absence_event']['failure_reason'])

    def test_transient_error_retry_then_ok(self):
        res = self._run(build_input_mode_a(),
                        [{'error': '网络中断', 'kind': 'network'},
                         self._raw(build_valid_output_mode_a())])
        self.assertEqual(res['outcome'], 'ACCEPTED_DOWNGRADED')
        self.assertEqual(res['attempts_used'], 2)
        self.assertEqual(res['trace'][0]['kind'], 'network')

    def test_attempts_exhausted_short_absent(self):
        res = self._run(build_input_mode_a(), [{'raw': '仅一次且失败'}])
        self.assertEqual(res['outcome'], 'ABSENT_REGISTERED')
        self.assertEqual(res['attempts_used'], 1)

    def test_retry_cap_limits_attempts(self):
        res = self._run(build_input_mode_a(),
                        [{'raw': 'a'}, {'raw': 'b'}, {'raw': 'c'},
                         self._raw(build_valid_output_mode_a())])
        self.assertEqual(res['outcome'], 'ABSENT_REGISTERED')
        self.assertEqual(res['attempts_used'], 3)   # 第4次不被消费(上限3)

    def test_mode_b_absent_event(self):
        res = self._run(build_input_mode_b(), [{'raw': '失败'}])
        ev = res['absence_event']
        self.assertEqual(ev['origin_query_id'], 'QB-20261029-001')
        self.assertIsNone(ev['task_id'])

    def test_mode_b_pipeline_accepted(self):
        res = self._run(build_input_mode_b(),
                        [self._raw(build_valid_output_mode_b())])
        self.assertEqual(res['outcome'], 'ACCEPTED')
        self.assertIsNone(res['evidence_map'])
        self.assertEqual(res['validated_output'], build_valid_output_mode_b())

    def test_invalid_input_rejected_at_entry(self):
        bad = build_input_mode_a()
        del bad['prompt_contract']
        with self.assertRaises(gov.InvalidResearchInput):
            gov.run_conclusion_pipeline(bad, [self._raw(
                build_valid_output_mode_a())])


# ══ T5 数值抽取豁免族直测(登记 REPORT §二.2) ═══════════════════════════════
class T5_NumericExtraction(unittest.TestCase):
    def test_extract_mixed_text(self):
        self.assertEqual(
            gov.extract_numeric_tokens(
                'TIPS_10Y 自2.20升至2.93(+73bp),4,186.7美元;'
                'HY-20261029-001 于2026-10-29观测,2026年6月后生效'),
            [2.2, 2.93, 73.0, 4186.7])

    def test_extract_signed_and_units(self):
        self.assertEqual(
            gov.extract_numeric_tokens('-0.5pp 与 +3.7% 与73bp'),
            [-0.5, 3.7, 73.0])

    def test_extract_ignores_identifiers(self):
        self.assertEqual(gov.extract_numeric_tokens(
            'UST_10Y 与 NFP_MOM_K 与 RT-20261029-001'), [])


# ══ T6 登记参数 echo=常量=登记值(R011 三方一致)+复用身份 ═══════════════════
class T6_EchoAndReuse(unittest.TestCase):
    def test_echo_params_literal(self):
        self.assertEqual(gov.echo_params(), ECHO_LITERAL)

    def test_output_schema_version_follows_g1(self):
        self.assertEqual(gov.OUTPUT_SCHEMA_VERSION, 'hs-1.0')
        self.assertEqual(gov.OUTPUT_SCHEMA_VERSION,
                         gia.OUTPUT_SCHEMA_VERSION_DEFAULT)

    def test_spec_enums_literal(self):
        self.assertEqual(gov.SPEC_OPS, ('>', '>=', '<', '<='))
        self.assertEqual(gov.SPEC_MODES, ('touch', 'expiry'))
        self.assertEqual(gov.CONFIDENCE_ENUM, ('high', 'medium', 'low'))
        self.assertEqual(gov.MAX_RETRIES, 3)

    def test_g1_module_reuse_identity(self):
        self.assertIs(gov.gia, gia)      # 复用调用(同一模块对象),非复制分叉


# ══ T7 源码边界锁(零网络/零凭证/零文件读取/零原始档字样+复用标记) ═══════════
class T7_SourceBoundaryLock(unittest.TestCase):
    def test_source_boundary_lock(self):
        src_path = os.path.join(ROOT, 'scripts', 'glm_output_validator.py')
        with open(src_path, encoding='utf-8') as fh:
            src = fh.read()
        for pattern in ('http', 'requests', 'socket', 'urllib', 'os.environ',
                        'API_KEY', 'api_key', 'open(', 'glob(', 'data/daily',
                        'launchd', 'subprocess'):
            self.assertNotIn(pattern, src, f'源码含禁用模式: {pattern}')
        self.assertIn('import glm_input_assembler as gia', src)   # G1 复用
        self.assertIn('import research_provenance as rp', src)    # rp 复用
        self.assertIn('rp.active_registry_metrics', src)           # 注册表经rp


if __name__ == '__main__':
    unittest.main(verbosity=2)
