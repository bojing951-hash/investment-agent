#!/usr/bin/env python3
"""IA-P03-W2-GLM-WP-G4 测试(全合成桩,零真实出站)

覆盖 DESIGN §七 WP-G4 验收要点可离线验证面+合同 AC-03 全部生效项:
- 熔断机制合成测试(AC-03.8,阈值=合同冻结字面量 5/60/5.00/120 硬编码断言);
- 调用面测试边界(AC-03.7): 一切用例经 client_factory 显式依赖注入合成桩,
  零真实出站(桩注入点登记 REPORT §二.4=scripts/glm_conclusion_client.py
  call_glm_once 的 client_factory 参数+run_live_conclusion 的 breaker 参数);
- 六槽位 prompt(DESIGN §四(1) L126-131)/编排(G2 管线复用)/落档(G3 复用)
  /门控默认跳过(tests/test_glm_live.py:31-33 模式)/脱敏/禁直读边界。

数据纪律(R014-D3/R022 沿用): 合成 fixture=唯一数据源(合成快照经
rp.recompute_gate_a 声明构建,数值全发明,不代表真实交易日);预期值一律
字面量硬编码(禁自证恒真);不读 data/daily/ 真实档。漂移维护策略见
docs/P03_W2_GLM_G4_DELIVERY.md 专节;fixture→预期值映射登记同处。
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import types
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import glm_conclusion_client as gcc          # 被测模块
import glm_input_assembler as gia            # G1 复用(fixture 装配)
import glm_output_validator as gov           # G2 复用(权威校验)
import glm_conclusion_integrator as gci      # G3 复用(落档)
import research_provenance as rp             # 既有权威机制(fixture 声明构建)

SRC_PATH = os.path.join(ROOT, 'scripts', 'glm_conclusion_client.py')
with open(SRC_PATH, encoding='utf-8') as _fh:
    MODULE_SOURCE = _fh.read()

# ══ 合成 fixture 字面量(唯一数据源;数值全发明,非真实交易日) ═════════════
YMDS = '20261104'
SNAP_ID = 'research_snapshot_' + YMDS
AS_OF = '2026-11-04T23:59:59+08:00'
OBS = '2026-11-03'
VAL_TIPS = 1.87          # 本包发明锚点(G1 fixture 用 2.93,此处独立)
VAL_GOLD = 3912.5        # 本包发明锚点(G1 fixture 用 4186.7,此处独立)
RATE_METRIC = 'TIPS_10Y'
GOLD_METRIC = 'GOLD_F'
ABSENT_DATA_METRIC = 'SILVER_F'      # 非核心·非派生(移除仅致 DEGRADED)
PHENOMENON = ('实际利率(TIPS_10Y)与黄金(GOLD_F)背离: 合成fixture任务现象'
              '(窗口2026-06-30~2026-09-30,RD-DIV-001触发)')
CRED_SENTINEL = 'SENTINEL-KEY-abcdef1234'   # 脱敏canary(非真实凭证)
TODAY = '2026-11-05'

# 熔断冻结字面量(合同 §七.5;测试侧硬编码,禁由实现推导——自证恒真禁)
FROZEN_CB1 = 5
FROZEN_CB2 = 60
FROZEN_CB3 = 5.00
FROZEN_CB4 = 120
MECH_FAMILIES = ['增长', '通胀', '利率与流动性', '信用', '避险与估值',
                 '供应与库存', '资金流']   # allocation_engine.py:104 同源独立誊写


def _channel_file(ch):
    return rp.SOURCE_FILE_RULES[ch]['prefix'] + YMDS + '.json'


def build_synthetic_snapshot(value_overrides=None, drop_metrics=()):
    """合成权威快照(与 G1 测试同构构建路径;数值本包独立发明)。"""
    actives = rp.active_registry_metrics()
    overrides = dict(value_overrides or {})
    facts = []
    for i, (mid, m) in enumerate(sorted(actives.items())):
        if mid in drop_metrics:
            continue
        derived = bool(mid in rp._DERIVED_DEPS)
        ch = rp._SOURCE_TO_INPUT.get(m['source']) or 'macro'
        facts.append({
            'fact_id': f'{mid}@{OBS}', 'metric_id': mid,
            'display_name': m.get('display_name'),
            'value': overrides.get(mid, round(100.0 + 0.25 * i, 4)),
            'unit': m['unit'],
            'value_type': m.get('value_type', 'level'),
            'observation_date': OBS, 'as_of': AS_OF,
            'source': {'collector': 'fact_engine' if derived else m['source'],
                       'file': _channel_file(ch), 'retrieved_at': None},
            'calculation_ref': '合成fixture派生(compute_derived契约)'
                               if derived else None,
            'calc': m.get('calc'), 'identity': dict(m.get('identity') or {}),
            'quality_status': 'PASS', 'issues': [],
        })
    nfp = next((f for f in facts if f['metric_id'] == 'NFP'), None)
    if nfp is not None:
        nfp['derived'] = {'m1': {'abs_change': 12.3}}
    core = {
        'snapshot_id': SNAP_ID, 'research_as_of': AS_OF, 'target_date': YMDS,
        'timezone': 'Asia/Shanghai',
        'sources_status': {ch: {'status': 'EXACT', 'file': _channel_file(ch),
                                'file_date': YMDS}
                           for ch in rp.SOURCE_CHANNELS},
        'fed_futures_curve': [], 'facts': facts, 'reconciliation': [],
    }
    rec = rp.recompute_gate_a(core)
    snap = dict(core)
    snap['quality'] = {'counts': rec['counts'], 'overall': rec['overall']}
    snap['gate_a'] = {'status': rec['effective'],
                      'core_missing': rec['core_missing'],
                      'core_fail': rec['core_fail'],
                      'noncore_fail': rec['noncore_fail'],
                      'noncore_missing': rec['noncore_missing'],
                      'note': '合成fixture声明(recompute_gate_a构建)'}
    snap['notes'] = ['合成fixture: 全部数值中性构造,不代表真实交易日']
    return snap


def build_synthetic_task(indicators=(RATE_METRIC, GOLD_METRIC)):
    """合成 E2E-A schema 任务档(与 G1 测试同构;文本本包独立)。"""
    return {
        'task_id': 'RT-2026-06-30~2026-09-30-RD-DIV-001-feed0042',
        'created_at': '2026-11-04T09:30:00+00:00',
        'phenomenon': PHENOMENON,
        'status': 'active',
        'indicators': list(indicators),
        'window': {'start': '2026-06-30', 'end': '2026-09-30',
                   'source_date': '20260930',
                   'alignment': {'rule': '共同观测日内连接(升序交集)',
                                 'n_common': 64},
                   'common_observations': 64},
        'detection': {'rule_id': 'RD-DIV-001',
                      'frozen_params': {'rolling_window': 60,
                                        'corr_threshold': 0.30,
                                        'rate_bp_threshold': 25.0,
                                        'gold_pct_threshold': 2.0},
                      'triggered': True,
                      'trigger_points': [{'date': '2026-08-19', 'rho': -0.30,
                                          'chg_r_bp': 11.7, 'chg_g_pct': 0.9}],
                      'trigger_stats': {'summary': {
                          'n_scored': 64, 'n_triggered': 15,
                          'first_trigger_date': '2026-08-19',
                          'rho_min': -0.3011, 'rho_max': -0.0702},
                          'series': []}},
        'evidence': {'data_access_points': {
            'rate': 'macro标准化层(合成)', 'gold': 'global标准化层(合成)'},
            'computation_ref': '合成fixture(无真实计算)'},
        'falsifiable_conditions': [
            '反驳条件A(合成): 若窗口内滚动相关恢复显著负值,背离判定不成立。',
            '反驳条件B(合成): 若金价区间变动转负而利率续升,现象消解。'],
        'history': [{'ts': f'2026-11-04T09:3{i}:00+00:00', 'from': None,
                     'to': 'pending', 'note': f'note{i}'} for i in range(7)],
    }


def build_full_inp():
    """全指标在场输入(gate PASS,absent_registry 空)。"""
    snap = build_synthetic_snapshot(
        {RATE_METRIC: VAL_TIPS, GOLD_METRIC: VAL_GOLD})
    return gia.assemble_mode_a(snap, build_synthetic_task())


def build_absent_inp():
    """缺席在场输入(SILVER_F 缺席 ABSENT_DATA,gate DEGRADED)。"""
    snap = build_synthetic_snapshot(
        {RATE_METRIC: VAL_TIPS, GOLD_METRIC: VAL_GOLD},
        drop_metrics=(ABSENT_DATA_METRIC,))
    task = build_synthetic_task(
        (RATE_METRIC, GOLD_METRIC, ABSENT_DATA_METRIC))
    return gia.assemble_mode_a(snap, task)


def build_valid_output(absent=False, variant=0):
    """合成合法 HypothesisSet(过 gov.validate_output;数值全接地 fixture 值)。

    variant=1: 陈述/置信微变(同 conclusion_id 不同 output_digest → 档案版本化)。"""
    stmt2 = ('避险与央行购金主导: GOLD_F 报3912.5,利率敏感度阶段性下降'
             if variant == 0 else
             '避险溢价主导(变体): GOLD_F 报3912.5,对利率上行钝化')
    lim_a = ['未覆盖的替代解释见HY-20261104-002']
    lim_b = ['未覆盖的替代解释见HY-20261104-001']
    if absent:
        lim_a = [f'缺席指标{ABSENT_DATA_METRIC}未纳入证据面(缺席如实登记,'
                 f'数据面降级DEGRADED影响链完整性)'] + lim_a
        lim_b = [f'缺席指标{ABSENT_DATA_METRIC}相关传导未覆盖(缺席如实登记,'
                 f'数据面降级DEGRADED影响链完整性)'] + lim_b
    return {
        'hypotheses': [
            {'hypothesis_id': 'HY-20261104-001',
             'statement': '实际利率回升压制黄金估值: TIPS_10Y 报1.87,'
                          '机会成本抬升',
             'supporting_evidence': [
                 {'fact_id': f'{RATE_METRIC}@{OBS}', 'metric_id': RATE_METRIC,
                  'direction_note': 'TIPS_10Y 现值1.87,处近期高位'}],
             'counter_evidence': [
                 {'fact_id': f'{GOLD_METRIC}@{OBS}', 'metric_id': GOLD_METRIC,
                  'direction_note': 'GOLD_F 同日报3912.5,坚挺与压制方向相悖'}],
             'falsifiable_conditions': [
                 {'cond_text': '若TIPS_10Y升至1.87上方,黄金应承压',
                  'spec': {'metric': RATE_METRIC, 'op': '>=', 'target': 1.87,
                           'mode': 'expiry',
                           'window': {'start': '2026-06-30',
                                      'end': '2026-09-30'}}}],
             'confidence': 'medium', 'limitations': lim_a},
            {'hypothesis_id': 'HY-20261104-002',
             'statement': stmt2,
             'supporting_evidence': [
                 {'fact_id': f'{GOLD_METRIC}@{OBS}', 'metric_id': GOLD_METRIC,
                  'direction_note': 'GOLD_F 报3912.5,趋势动能仍在'}],
             'counter_evidence': [
                 {'fact_id': f'{RATE_METRIC}@{OBS}', 'metric_id': RATE_METRIC,
                  'direction_note': 'TIPS_10Y 报1.87,传统实际利率框架反证'}],
             'falsifiable_conditions': [
                 {'cond_text': '若GOLD_F回落至3912.5下方,避险主导解释弱化',
                  'spec': {'metric': GOLD_METRIC, 'op': '<=', 'target': 3912.5,
                           'mode': 'touch',
                           'window': {'start': '2026-06-30',
                                      'end': '2026-09-30'}}}],
             'confidence': 'medium', 'limitations': lim_b},
        ],
        'phenomenon_echo': PHENOMENON + '(现象复述)',
        'absent_ack': ([f'{ABSENT_DATA_METRIC} 缺席(ABSENT_DATA: 事实缺席)']
                       if absent else []),
    }


# ══ 合成桩(显式依赖注入面;零真实出站) ═══════════════════════════════════

class _Usage:
    def __init__(self, p, c):
        self.prompt_tokens, self.completion_tokens = p, c
        self.total_tokens = p + c


class _Event:
    def __init__(self, content=None, usage=None):
        self.choices = ([types.SimpleNamespace(
            delta=types.SimpleNamespace(content=content))] if content is not
            None else [])
        self.usage = usage


def ok_call(text, usage=None):
    """成功响应事件序列(usage 缺省 None→费用按下限)。"""
    return [_Event(content=text)] + ([_Event(usage=usage)] if usage else [])


class _ScriptedCompletions:
    def __init__(self, owner):
        self.owner = owner

    def create(self, **kwargs):
        self.owner.prompts.append(kwargs.get('messages'))
        i = len(self.owner.consumed)
        if i >= len(self.owner.specs):
            raise AssertionError('合成桩出站超出脚本(意外第%d次调用)' % (i + 1))
        spec = self.owner.specs[i]
        self.owner.consumed.append(spec)
        if isinstance(spec, Exception):
            raise spec
        if isinstance(spec, str):        # 文本spec=成功HTTP响应(坏正文→解析失败径)
            return iter([_Event(content=spec)])
        return iter(list(spec))


class StubFactory:
    """桩注入点实现: client_factory=StubFactory(specs)——specs 每项=事件序列
    或异常;consumed/prompts 供断言(出站计数与回注内容)。"""

    def __init__(self, specs):
        self.specs = list(specs)
        self.consumed = []
        self.prompts = []

    def __call__(self):
        return types.SimpleNamespace(
            chat=types.SimpleNamespace(
                completions=_ScriptedCompletions(self)))


class CanaryFactory:
    """零出站金丝雀: 被调用即测试失败(证明门控先于任何 client 构造)。"""

    def __call__(self):
        raise AssertionError('真实出站路径被触达(门控未先行)')


class _SaveEnv(unittest.TestCase):
    """环境补丁基类: 统一 RUN_GLM_LIVE=1+GLM_API_KEY=SENTINEL(canary 值)。"""

    def setUp(self):
        self._saved = {k: os.environ.get(k)
                       for k in (gcc.LIVE_GATE_ENV, gcc.CREDENTIAL_ENV)}
        os.environ[gcc.LIVE_GATE_ENV] = '1'
        os.environ[gcc.CREDENTIAL_ENV] = CRED_SENTINEL
        self.tmpdir = tempfile.mkdtemp(prefix='g4_test_')

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# ══ T0 fixture 自检 ════════════════════════════════════════════════════════

class T0_FixtureSanity(unittest.TestCase):
    def test_base_snapshot_gate_pass(self):
        snap = build_synthetic_snapshot()
        self.assertEqual(rp.gate_status(snap), ('PASS', ''))

    def test_absent_variant_gate_degraded_and_absent_registered(self):
        snap = build_synthetic_snapshot(drop_metrics=(ABSENT_DATA_METRIC,))
        self.assertEqual(rp.gate_status(snap)[0], 'DEGRADED')
        inp = build_absent_inp()
        absent = {a['metric_id']: a['level'] for a in inp['absent_registry']}
        self.assertEqual(absent.get(ABSENT_DATA_METRIC), 'ABSENT_DATA')

    def test_assembled_inputs_pass_g1_contract(self):
        self.assertEqual(gia.validate_input(build_full_inp()), [])
        self.assertEqual(gia.validate_input(build_absent_inp()), [])

    def test_valid_output_fixture_passes_g2(self):
        self.assertEqual(
            gov.validate_output(build_full_inp(), build_valid_output()), [])
        self.assertEqual(
            gov.validate_output(build_absent_inp(),
                                build_valid_output(absent=True)), [])


# ══ T1 熔断机制合成测试(AC-03.8;阈值=冻结字面量硬编码) ═══════════════════

class T1_CircuitBreaker(_SaveEnv):
    def test_echo_frozen_literals(self):
        echo = gcc.echo_params()
        self.assertEqual(echo['cb1_max_consecutive_failures'], 5)
        self.assertEqual(echo['cb2_max_outbound_per_segment'], 60)
        self.assertEqual(echo['cb3_daily_cost_cap_usd'], 5.00)
        self.assertEqual(echo['cb4_timeout_seconds'], 120)

    def test_cb1_trips_exactly_at_5th_failure(self):
        brk = gcc.CircuitBreaker(day_utc='2026-11-05')
        for i in range(4):                      # 前4次不熔断
            brk.note_failure('network', 0.02)
            self.assertIsNone(brk.state()['tripped'],
                              f'第{i + 1}次失败不应熔断(阈值={FROZEN_CB1})')
        st = brk.note_failure('network', 0.02)  # 恰第5次
        self.assertEqual(st['tripped'], 'CB-1')
        allowed, why = brk.outbound_allowed()
        self.assertFalse(allowed)
        self.assertIn('TRIPPED-CB-1', why)

    def test_cb1_no_6th_outbound_via_orchestrator(self):
        stub = StubFactory([ConnectionError('合成网络错误')] * 6)
        brk = gcc.CircuitBreaker(day_utc='2026-11-05')
        inp = build_full_inp()
        r1 = gcc.run_live_conclusion(
            inp, client_factory=stub, breaker=brk, today_iso=TODAY)
        r2 = gcc.run_live_conclusion(
            inp, client_factory=stub, breaker=brk, today_iso=TODAY)
        self.assertEqual(len(stub.consumed), 5,
                         '恰5次出站后熔断,禁第6次出站尝试')
        self.assertEqual(r1['attempts_used'], 3)   # =RETRY_BUDGET(gov.MAX_RETRIES)
        self.assertEqual(r2['attempts_used'], 2)   # 第4/5次失败→TRIPPED→停
        self.assertTrue(r2['blocked_reason'].startswith('TRIPPED-CB-1'))

    def test_cb2_soft_stop_at_60(self):
        brk = gcc.CircuitBreaker(day_utc='2026-11-05')
        for _ in range(FROZEN_CB2):
            brk.note_outbound()
        allowed, why = brk.outbound_allowed()
        self.assertFalse(allowed)
        self.assertIn('CB-2', why)
        self.assertIn('60', why)

    def test_cb2_orchestrator_zero_new_outbound_at_cap(self):
        stub = StubFactory([ok_call(json.dumps(build_valid_output()))])
        brk = gcc.CircuitBreaker(day_utc='2026-11-05')
        for _ in range(FROZEN_CB2):
            brk.note_outbound()
        r = gcc.run_live_conclusion(
            build_full_inp(), client_factory=stub, breaker=brk,
            today_iso=TODAY)
        self.assertEqual(len(stub.consumed), 0, '达60后零新出站')
        self.assertEqual(r['attempts_used'], 0)
        self.assertIn('CB-2', r['blocked_reason'])

    def test_cb3_trips_at_5usd_exact(self):
        brk = gcc.CircuitBreaker(day_utc='2026-11-05')
        brk.note_success(2.49)
        brk.note_success(2.50)                    # 累计4.99 → 不熔断
        self.assertIsNone(brk.state()['tripped'])
        brk.note_success(0.01)                    # 累计5.00 → TRIPPED
        self.assertEqual(brk.state()['tripped'], 'CB-3')

    def test_cb4_boundary_strictly_greater(self):
        self.assertEqual(gcc.classify_elapsed(120.0), 'ok')
        self.assertEqual(gcc.classify_elapsed(119.9), 'ok')
        self.assertEqual(gcc.classify_elapsed(120.01), 'cb4_timeout')

    def test_cb4_delay_counts_into_cb1(self):
        brk = gcc.CircuitBreaker(day_utc='2026-11-05')
        for elapsed in (121.0, 150.0, 130.5, 999.0, 120.5):
            self.assertEqual(gcc.classify_elapsed(elapsed), 'cb4_timeout')
            brk.note_failure('cb4_timeout', 0.02)
        self.assertEqual(brk.state()['tripped'], 'CB-1',
                         'CB-4延迟>120s计失败并入CB-1连续计数,5次即熔断')

    def test_tripped_no_auto_retry_zero_outbound(self):
        brk = gcc.CircuitBreaker(day_utc='2026-11-05')
        for _ in range(5):
            brk.note_failure('network')
        stub = StubFactory([ok_call('{}')] * 3)
        r = gcc.run_live_conclusion(
            build_full_inp(), client_factory=stub, breaker=brk,
            today_iso=TODAY)
        self.assertEqual(len(stub.consumed), 0, 'TRIPPED后无自动重试')
        self.assertEqual(r['attempts_used'], 0)

    def test_manual_reset_semantics(self):
        brk = gcc.CircuitBreaker(day_utc='2026-11-05')
        for _ in range(5):
            brk.note_failure('network', 0.02)
        brk.note_outbound()
        st = brk.reset()                          # 显式人工动作
        self.assertIsNone(st['tripped'])
        self.assertEqual(st['consecutive_failures'], 0)
        self.assertEqual(st['outbound_count'], 1,
                         '复位不清段出站计数(CB-2累计语义保留)')
        self.assertEqual(st['day_cost_usd'], 0.1,
                         '复位不清日费用累计(CB-3累计语义保留)')

    def test_auth_failure_counts_conservatively(self):
        brk = gcc.CircuitBreaker(day_utc='2026-11-05')
        for _ in range(5):
            brk.note_failure('auth_error', 0.02)
        self.assertEqual(brk.state()['tripped'], 'CB-1',
                         '登记决策: 一切失败类保守入CB-1计数')


# ══ T2 调用点合成桩(费用估算/失败分类/脱敏) ═════════════════════════════

class T2_ClientStub(_SaveEnv):
    def test_success_raw_usage_cost(self):
        stub = StubFactory([ok_call('{"k": 1}', usage=_Usage(1000, 2000))])
        r = gcc.call_glm_once('sys', 'usr', client_factory=stub)
        self.assertTrue(r['ok'])
        self.assertEqual(r['raw'], '{"k": 1}')
        self.assertEqual(r['usage']['prompt_tokens'], 1000)
        self.assertEqual(r['usage']['completion_tokens'], 2000)
        self.assertEqual(r['cost_est_usd'], 0.021,
                         '1000*3.0/1e6+2000*9.0/1e6=0.003+0.018=0.021(字面量)')

    def test_cost_floor_without_usage(self):
        stub = StubFactory([ok_call('text')])
        r = gcc.call_glm_once('sys', 'usr', client_factory=stub)
        self.assertEqual(r['cost_est_usd'], 0.02, '用量缺席按下限0.02(字面量)')

    def test_empty_stream_is_stream_interrupted(self):
        stub = StubFactory([[_Event(usage=_Usage(10, 10))]])
        r = gcc.call_glm_once('sys', 'usr', client_factory=stub)
        self.assertFalse(r['ok'])
        self.assertEqual(r['kind'], 'stream_interrupted')
        self.assertEqual(r['cost_est_usd'], 0.02)

    def test_exception_classified_network(self):
        stub = StubFactory([ConnectionError('合成连接中断')])
        r = gcc.call_glm_once('sys', 'usr', client_factory=stub)
        self.assertFalse(r['ok'])
        self.assertEqual(r['kind'], 'network')
        self.assertIn('ConnectionError', r['error'])

    def test_risk_control_classification(self):
        class RiskErr(Exception):
            status_code = 1301
        stub = StubFactory([RiskErr('内容风控(合成)')])
        r = gcc.call_glm_once('sys', 'usr', client_factory=stub)
        self.assertEqual(r['kind'], 'risk_control')

    def test_auth_error_classification(self):
        class AuthErr(Exception):
            status_code = 401
        stub = StubFactory([AuthErr('无效凭证(合成)')])
        r = gcc.call_glm_once('sys', 'usr', client_factory=stub)
        self.assertEqual(r['kind'], 'auth_error')

    def test_redaction_strips_credential_value(self):
        stub = StubFactory([
            RuntimeError(f'请求失败 header含 {CRED_SENTINEL} (合成)')])
        r = gcc.call_glm_once('sys', 'usr', client_factory=stub)
        self.assertFalse(r['ok'])
        self.assertNotIn(CRED_SENTINEL, r['error'])
        self.assertIn(gcc._REDACTED, r['error'])


# ══ T3 六槽位 prompt(DESIGN §四(1) L126-131) ═════════════════════════════

class T3_PromptSixSlots(_SaveEnv):
    def build(self, absent=False, feedback=None):
        inp = build_absent_inp() if absent else build_full_inp()
        legal = {VAL_TIPS, VAL_GOLD}      # 注入合法数值集(不依赖真实registry)
        return gcc.build_prompt(inp, feedback=feedback, legal_targets=legal)

    def test_slot1_phenomenon_window_indicators(self):
        _, user = self.build()
        self.assertIn(PHENOMENON, user)
        self.assertIn('2026-06-30', user)
        self.assertIn('2026-09-30', user)
        self.assertIn(RATE_METRIC, user)
        self.assertIn(GOLD_METRIC, user)

    def test_slot2_all_seven_mechanism_families(self):
        _, user = self.build()
        for fam in MECH_FAMILIES:
            self.assertIn(fam, user, f'机制族提示缺 {fam}')
        self.assertIn('两个不同机制族', user)

    def test_slot3_competition_mandate(self):
        _, user = self.build()
        self.assertIn('至少 2 个相互竞争假设', user)
        self.assertIn('区分性判据', user)
        self.assertIn('仅措辞不同而无判据区分', user)

    def test_slot4_counter_evidence_mandate(self):
        _, user = self.build()
        self.assertIn('counter_evidence', user)
        self.assertIn('必须列为', user)
        self.assertIn('而非省略或重新解释为支持', user)
        self.assertIn('不存在无反方证据的合法输出', user)

    def test_slot5_numeric_grounding_legal_numbers(self):
        _, user = self.build()
        self.assertIn('数值接地', user)
        self.assertIn('1.87', user)
        self.assertIn('3912.5', user)
        self.assertIn('合法数值清单', user)
        self.assertIn('不可程序裁决', user)

    def test_slot6_absent_items_and_empty_in_empty_out(self):
        _, user_abs = self.build(absent=True)
        self.assertIn(ABSENT_DATA_METRIC, user_abs)
        self.assertIn('ABSENT_DATA', user_abs)
        _, user_full = self.build()
        self.assertIn('空进空出', user_full)

    def test_schema_block_field_names(self):
        _, user = self.build()
        for f in ('"hypotheses"', '"hypothesis_id"', '"statement"',
                  '"supporting_evidence"', '"counter_evidence"',
                  '"falsifiable_conditions"', '"cond_text"', '"spec"',
                  '"confidence"', '"limitations"', '"phenomenon_echo"',
                  '"absent_ack"', '"metric"', '"op"', '"target"', '"mode"',
                  '"window"'):
            self.assertIn(f, user, f'schema块缺字段 {f}')
        self.assertIn('">=|>|<|<="', user)
        self.assertIn('touch|expiry', user)

    def test_feedback_slot_injection(self):
        _, user = self.build(feedback='校验失败回注修正: 竞争性不足(合成)')
        self.assertIn('径1反馈回注', user)
        self.assertIn('校验失败回注修正: 竞争性不足(合成)', user)
        _, user_plain = self.build()
        self.assertNotIn('径1反馈回注', user_plain)

    def test_mode_b_prompt(self):
        inp = build_full_inp()
        inp = dict(inp)
        inp['mode'] = 'B'
        inp['task_ref'] = None
        inp['query_ref'] = {
            'query_id': 'QB-20261104-001',
            'question_text': 'TIPS_10Y与GOLD_F为何背离?',
            'as_of': OBS, 'metric_bindings_digest': 'a1b2c3d4e5f60718',
            'derived_ops_digest': 'b2c3d4e5f60718a9'}
        self.assertEqual(gia.validate_input(inp), [])
        _, user = gcc.build_prompt(inp, legal_targets={VAL_TIPS, VAL_GOLD})
        self.assertIn('TIPS_10Y与GOLD_F为何背离?', user)
        self.assertIn('"explanation"', user)
        self.assertIn('"phenomenon_echo"', user)


# ══ T4 执行段编排(G2 管线/G3 落档复用) ═══════════════════════════════════

class T4_Orchestrator(_SaveEnv):
    def run_case(self, specs, *, inp=None, breaker=None, seq=1, archive=None,
                 variant=None, absent=False):
        inp = inp if inp is not None else (
            build_absent_inp() if absent else build_full_inp())
        out = build_valid_output(absent=absent) if variant is None \
            else build_valid_output(absent=absent, variant=variant)
        stub = StubFactory([ok_call(json.dumps(out)) if sp == 'VALID' else sp
                            for sp in specs])
        log = os.path.join(self.tmpdir, 'usage.jsonl')
        r = gcc.run_live_conclusion(
            inp, client_factory=stub, breaker=breaker, seq=seq,
            today_iso=TODAY, archive=archive, usage_log_path=log)
        return r, stub, log

    def test_accepted_first_try(self):
        archive = {gcc.ARCHIVE_KEY: []}
        r, stub, log = self.run_case(['VALID'], archive=archive)
        self.assertEqual(r['pipeline']['outcome'], 'ACCEPTED')
        self.assertEqual(r['attempts_used'], 1)
        self.assertEqual(r['archive_status'], 'written')
        self.assertRegex(r['conclusion_record']['conclusion_id'],
                         r'^CR-20261105-001$')
        self.assertIsNone(r['breaker']['tripped'])
        self.assertEqual(len(archive[gcc.ARCHIVE_KEY]), 1)
        with open(log, encoding='utf-8') as fh:
            lines = [json.loads(x) for x in fh if x.strip()]
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0]['ok'])
        self.assertEqual(lines[0]['attempt'], 1)
        self.assertNotIn(CRED_SENTINEL, json.dumps(lines))

    def test_accepted_downgraded_with_absent(self):
        r, _, _ = self.run_case(['VALID'], absent=True)
        self.assertEqual(r['pipeline']['outcome'], 'ACCEPTED_DOWNGRADED')
        self.assertEqual(r['grounding']['outcome'], 'ACCEPTED_DOWNGRADED')
        self.assertIn('gov.validate_output', r['grounding']['enforced_by'])

    def test_feedback_retry_then_accepted(self):
        r, stub, _ = self.run_case(['这不是JSON(合成坏响应)', 'VALID'])
        self.assertEqual(r['attempts_used'], 2)
        self.assertEqual(r['pipeline']['outcome'], 'ACCEPTED')
        self.assertEqual(len(stub.prompts), 2)
        second_user = stub.prompts[1][1]['content']
        self.assertIn('径1反馈回注', second_user)
        self.assertIn('解析失败', second_user)
        first_user = stub.prompts[0][1]['content']
        self.assertNotIn('径1反馈回注', first_user)

    def test_transient_then_success(self):
        r, _, _ = self.run_case([ConnectionError('合成瞬态失败'), 'VALID'])
        self.assertEqual(r['attempts_used'], 2)
        self.assertEqual(r['pipeline']['outcome'], 'ACCEPTED')

    def test_retry_exhaustion_absent_registered(self):
        r, stub, _ = self.run_case(['坏响应A(合成)', '坏响应B(合成)',
                               '坏响应C(合成)'])
        self.assertEqual(r['attempts_used'], 3,
                         '重试预算=gov.MAX_RETRIES(3)字面量')
        self.assertEqual(len(stub.consumed), 3, '禁第4次出站')
        self.assertEqual(r['pipeline']['outcome'], 'ABSENT_REGISTERED')
        self.assertEqual(r['conclusion_record']['outcome'],
                         'ABSENT_REGISTERED')
        self.assertIsNone(r['blocked_reason'])

    def test_pretripped_zero_outbound_absent(self):
        brk = gcc.CircuitBreaker(day_utc='2026-11-05')
        for _ in range(5):
            brk.note_failure('network')
        r, stub, _ = self.run_case(['VALID'], breaker=brk)
        self.assertEqual(len(stub.consumed), 0)
        self.assertEqual(r['attempts_used'], 0)
        self.assertEqual(r['pipeline']['outcome'], 'ABSENT_REGISTERED')
        self.assertIn('TRIPPED-CB-1', r['blocked_reason'])

    def test_archive_idempotent_replay(self):
        archive = {gcc.ARCHIVE_KEY: []}
        r1, _, _ = self.run_case(['VALID'], archive=archive)
        r2, _, _ = self.run_case(['VALID'], archive=archive)
        self.assertEqual(r1['archive_status'], 'written')
        self.assertEqual(r2['archive_status'], 'skipped-idempotent')
        self.assertEqual(len(archive[gcc.ARCHIVE_KEY]), 1)

    def test_archive_versioning_on_digest_change(self):
        archive = {gcc.ARCHIVE_KEY: []}
        r1, _, _ = self.run_case(['VALID'], archive=archive, variant=0)
        r2, _, _ = self.run_case(['VALID'], archive=archive, variant=1)
        self.assertEqual(r1['archive_status'], 'written')
        self.assertEqual(r2['archive_status'], 'written-new-version')
        self.assertTrue(archive[gcc.ARCHIVE_KEY][-1]['conclusion_id'].endswith(
            '__v2'), '同id不同digest→新版本追加(原记录字节不动)')
        self.assertTrue(archive[gcc.ARCHIVE_KEY][0]['conclusion_id'].endswith(
            '001'), '原记录保留')


# ══ T5 门控/边界/脱敏落盘/结构面 ═══════════════════════════════════════════

class T5_GatesAndBoundaries(_SaveEnv):
    def test_gate_refused_without_run_env(self):
        os.environ.pop(gcc.LIVE_GATE_ENV, None)
        with self.assertRaises(gcc.LiveGateRefused):
            gcc.run_live_conclusion(build_full_inp(),
                                    client_factory=CanaryFactory())

    def test_gate_refused_without_credential(self):
        os.environ.pop(gcc.CREDENTIAL_ENV, None)
        with self.assertRaises(gcc.LiveGateRefused):
            gcc.run_live_conclusion(build_full_inp(),
                                    client_factory=CanaryFactory())

    def test_cli_default_skip_zero_outbound(self):
        env = {k: v for k, v in os.environ.items()
               if k not in (gcc.LIVE_GATE_ENV, gcc.CREDENTIAL_ENV)}
        p = subprocess.run(
            [sys.executable, SRC_PATH, '--live-smoke'],
            capture_output=True, text=True, env=env, cwd=ROOT, timeout=60)
        self.assertEqual(p.returncode, 0)
        self.assertIn('跳过', p.stdout)
        self.assertIn('RUN_GLM_LIVE', p.stdout)

    def test_module_source_no_data_daily_reference(self):
        self.assertNotIn('data/daily', MODULE_SOURCE,
                         '禁直读原始采集档(AC-07.1)')

    def test_module_source_no_top_level_openai(self):
        for line in MODULE_SOURCE.splitlines():
            if line.startswith(('import openai', 'from openai')):
                self.fail('openai 须惰性 import(函数体内),禁模块级')

    def test_module_source_no_network_stdlib_client(self):
        for pat in ('import requests', 'import urllib', 'import socket',
                    'import http.client'):
            self.assertNotIn(pat, MODULE_SOURCE)

    def test_usage_log_file_credential_free(self):
        stub = StubFactory([
            RuntimeError(f'失败信息含凭证 {CRED_SENTINEL} (合成)')] * 3)
        log = os.path.join(self.tmpdir, 'usage2.jsonl')
        gcc.run_live_conclusion(build_full_inp(), client_factory=stub,
                                today_iso=TODAY, usage_log_path=log)
        with open(log, encoding='utf-8') as fh:
            blob = fh.read()
        self.assertNotIn(CRED_SENTINEL, blob)
        self.assertIn(gcc._REDACTED, blob)
        self.assertEqual(blob.count('\n'), 3)

    def test_registry_row_alias_only(self):
        row = gcc.render_registry_row(
            1, face='F1-合成', purpose='要点①(合成)',
            outbound_count=2, cost_usd=0.04,
            breaker_state=gcc.CircuitBreaker(day_utc=TODAY).state(),
            ts_utc='2026-11-05T00:00:00Z',
            approval_ref='PENDING-APPROVALS.md(合成)')
        self.assertIn('G4-CRED-001', row)
        self.assertIn(gcc.CREDENTIAL_ENV, row)
        self.assertNotIn(CRED_SENTINEL, row)
        self.assertIn('未触发', row)


# ══ T6 真实路径前置(零凭证=零出站,fail-closed) ═══════════════════════════

class T6_RealPathGuard(_SaveEnv):
    def test_no_credential_means_zero_outbound(self):
        os.environ.pop(gcc.CREDENTIAL_ENV, None)
        r = gcc.call_glm_once('sys', 'usr')   # 真实路径分支,凭证缺席即拒
        self.assertFalse(r['ok'])
        self.assertEqual(r['kind'], 'auth_error')
        self.assertIn('零凭证零出站', r['error'])
        self.assertEqual(r['cost_est_usd'], 0.02)


if __name__ == '__main__':
    unittest.main(verbosity=2)
