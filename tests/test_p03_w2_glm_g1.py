# -*- coding: utf-8 -*-
"""IA-P03-W2-GLM-WP-G1(结论层输入装配器)专项测试。

合同 IA-P03-W2-GLM-WP-G1-AC-v1.0 / DESIGN §七 WP-G1 验收要点行为锁:
- 要点① 输入契约字段级校验: 九字段 schema/类型/枚举/合同级常量(prompt_contract
  三值)逐项正反向用例(T1/T1c/T11);
- 要点② 禁直读: 装配产物零原始档路径引用(除 facts[].source_file 披露槽位,
  T2b)+ Gate A FAIL/None 拒绝装配(T2)+ 装配器源码级零文件读取/零glob/零网络/
  零凭证+单处接入点豁免标记(T2c);
- 要点③ 缺席登记: 构造缺席指标→absent_registry 如实登记(不填0不造数,T3)+
  四级枚举纯函数直测(T3b);
- 要点④ 快照绑定核验: 篡改快照(值变/声明说谎/计数漂移)后装配拒绝(T4,R5+R2/R3
  双层);
- 模式 B 形态(E2E-B IR 契约): 引用摘要 digest/RESOLVED 接地 fail-closed/缺席
  透传/无IR拒绝(T5-T5d);R1 壳入口(T6);E2E-A schema 契约拒绝(T7);
  登记参数 echo=常量=登记值(R011 三方一致,T8)。

数据纪律(R014-D3/R022/R011 沿用): 全部离线合成 fixture=唯一数据源——合成快照
由注册表 active 集程序化生成(声明经 recompute_gate_a 构建,与 snapshot_builder
写入路径同构),不代表任何真实交易日;预期值一律字面量硬编码(手算/登记规格独立
重导,不从被测模块导入计算——自证恒真是 F 反例)。零网络/零新增第三方依赖。
"""
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import glm_input_assembler as gia          # noqa: E402 (被测模块)
import research_provenance as rp           # noqa: E402 (既有权威机制,fixture 声明构建)

YMDS = '20261104'                          # 合成快照目标日(非真实交易日)
SNAP_ID = 'research_snapshot_' + YMDS
AS_OF = '2026-11-04T23:59:59+08:00'
OBS = '2026-11-03'                         # 合成观测日(≤研究截止)
VAL_TIPS = 2.93                            # 字面量锚点(E2E-A 登记窗终值语义)
VAL_GOLD = 4186.7
RATE_METRIC = 'TIPS_10Y'
GOLD_METRIC = 'GOLD_F'
ABSENT_DATA_METRIC = 'SILVER_F'            # 非核心·非派生输入(移除仅致 DEGRADED)
UNREGISTERED_METRIC = 'JGB_10Y'            # 不在注册表(E2E-B A1 同款示例)


# ══ 合成快照 fixture(唯一数据源;声明与 recompute_gate_a 同构构建) ═══════

def _channel_file(ch):
    return rp.SOURCE_FILE_RULES[ch]['prefix'] + YMDS + '.json'


def build_synthetic_snapshot(value_overrides=None, drop_metrics=()):
    """合成权威快照: 注册表 active 全集各一事实(中性合成值+两字面量锚点),
    通道全 EXACT;gate_a/quality 声明经 rp.recompute_gate_a 构建(与
    snapshot_builder.py 写入路径同构)。fixture 自检: gate_status 回读期望态。"""
    actives = rp.active_registry_metrics()
    overrides = dict(value_overrides or {})
    facts = []
    for i, (mid, m) in enumerate(sorted(actives.items())):
        if mid in drop_metrics:
            continue
        derived = bool(mid in rp._DERIVED_DEPS)
        ch = rp._SOURCE_TO_INPUT.get(m['source']) or 'macro'
        facts.append({
            'fact_id': f'{mid}@{OBS}',
            'metric_id': mid,
            'display_name': m.get('display_name'),
            'value': overrides.get(mid, round(100.0 + 0.25 * i, 4)),
            'unit': m['unit'],
            'value_type': m.get('value_type', 'level'),
            'observation_date': OBS,
            'as_of': AS_OF,
            'source': {'collector': 'fact_engine' if derived else m['source'],
                       'file': _channel_file(ch), 'retrieved_at': None},
            'calculation_ref': '合成fixture派生(compute_derived契约)' if derived else None,
            'calc': m.get('calc'),
            'identity': dict(m.get('identity') or {}),
            'quality_status': 'PASS',
            'issues': [],
        })
    nfp = next((f for f in facts if f['metric_id'] == 'NFP'), None)
    if nfp is not None:
        nfp['derived'] = {'m1': {'abs_change': 12.3}}   # NFP_MOM_K 计算依据镜像
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


def rebuild_declarations(snap):
    """变体快照重算声明(保持声明↔重算一致;篡改类变体不走此函数)。"""
    core = {k: snap[k] for k in ('facts', 'sources_status', 'research_as_of',
                                 'target_date')}
    rec = rp.recompute_gate_a(core)
    snap['quality'] = {'counts': rec['counts'], 'overall': rec['overall']}
    snap['gate_a'] = {'status': rec['effective'],
                      'core_missing': rec['core_missing'],
                      'core_fail': rec['core_fail'],
                      'noncore_fail': rec['noncore_fail'],
                      'noncore_missing': rec['noncore_missing'],
                      'note': '合成fixture声明(recompute_gate_a构建)'}
    return snap


def spec_digest(obj):
    """登记规格独立重导引用摘要(sha256 前16位,canonical JSON)——测试侧
    按登记规格重算,不导入被测模块 _digest_ref(禁自证恒真)。"""
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode('utf-8')).hexdigest()[:16]


def build_synthetic_task(indicators=(RATE_METRIC, GOLD_METRIC)):
    """合成 E2E-A schema 任务档(10 最低字段齐备;history 7 条→尾部5条可测)。"""
    return {
        'task_id': 'RT-2026-06-30~2026-09-30-RD-DIV-001-feed0001',
        'created_at': '2026-10-30T05:30:00+00:00',
        'phenomenon': '实际利率(TIPS_10Y)与黄金(GOLD_F)背离: 合成任务档fixture'
                      '(窗口2026-06-30~2026-09-30,RD-DIV-001触发)',
        'status': 'active',
        'indicators': list(indicators),
        'window': {'start': '2026-06-30', 'end': '2026-09-30',
                   'source_date': '20260930',
                   'alignment': {'rule': '共同观测日内连接(升序交集)',
                                 'n_common': 65},
                   'common_observations': 65},
        'detection': {'rule_id': 'RD-DIV-001',
                      'frozen_params': {'rolling_window': 60,
                                        'corr_threshold': 0.30,
                                        'rate_bp_threshold': 25.0,
                                        'gold_pct_threshold': 2.0},
                      'triggered': True,
                      'trigger_points': [{'date': '2026-08-21', 'rho': -0.32,
                                          'chg_r_bp': 12.5, 'chg_g_pct': 0.8}],
                      'trigger_stats': {'summary': {
                          'n_scored': 65, 'n_triggered': 16,
                          'first_trigger_date': '2026-08-21',
                          'rho_min': -0.3202, 'rho_max': -0.0735},
                          'series': []}},
        'evidence': {'data_access_points': {'rate': 'macro标准化层(合成)',
                                            'gold': 'global标准化层(合成)'},
                     'computation_ref': '合成fixture(无真实计算)'},
        'falsifiable_conditions': [
            '反驳条件A(合成): 若窗口内滚动相关恢复显著负值,背离判定不成立。',
            '反驳条件B(合成): 若金价区间变动转负而利率续升,现象消解。',
            '反驳条件C(合成): 若控制变量引入后相关性恢复,主题必要性不成立。'],
        'history': [{'ts': f'2026-10-30T05:3{i}:00+00:00', 'from': None,
                     'to': 'pending', 'note': f'note{i}'} for i in range(7)],
    }


TIPS_FACT_PROJ = {
    'metric_id': 'TIPS_10Y', 'fact_id': 'TIPS_10Y@' + OBS, 'value': 2.93,
    'unit': 'percent', 'observation_date': OBS, 'quality_status': 'PASS',
    'source_file': 'macro_' + YMDS + '.json',
}
GOLD_FACT_PROJ = {
    'metric_id': 'GOLD_F', 'fact_id': 'GOLD_F@' + OBS, 'value': 4186.7,
    'unit': 'usd_per_oz', 'observation_date': OBS, 'quality_status': 'PASS',
    'source_file': 'global_' + YMDS + '.json',
}


class FixtureSanity(unittest.TestCase):
    """fixture 自检: 合成快照经既有权威机制回读为期望门禁态(非被测模块)。"""

    def test_base_snapshot_gate_pass(self):
        snap = build_synthetic_snapshot()
        self.assertEqual(rp.gate_status(snap), ('PASS', ''))

    def test_degraded_variant_gate_degraded(self):
        snap = rebuild_declarations(
            build_synthetic_snapshot(drop_metrics=(ABSENT_DATA_METRIC,)))
        self.assertEqual(rp.gate_status(snap)[0], 'DEGRADED')


class T1_ModeAInputContract(unittest.TestCase):
    """要点①: 模式 A 九字段字段级校验(正向全量,字面量断言)。"""

    def setUp(self):
        self.snap = build_synthetic_snapshot(
            {RATE_METRIC: VAL_TIPS, GOLD_METRIC: VAL_GOLD})
        self.task = build_synthetic_task()
        self.inp = gia.assemble_mode_a(self.snap, self.task)

    def test_nine_fields_and_literals(self):
        self.assertEqual(sorted(self.inp), sorted([
            'contract_version', 'mode', 'snapshot_binding', 'task_ref',
            'query_ref', 'evidence_pack', 'absent_registry', 'prior_knowledge',
            'prompt_contract']))
        self.assertEqual(self.inp['contract_version'], 'gri-1.0')
        self.assertEqual(self.inp['mode'], 'A')
        self.assertIsNone(self.inp['query_ref'])
        sb = self.inp['snapshot_binding']
        self.assertEqual(sb['snapshot_id'], SNAP_ID)
        self.assertEqual(sb['gate_a'], 'PASS')
        self.assertEqual(sb['research_as_of'], AS_OF)
        self.assertEqual(sb['snapshot_digest'],
                         hashlib.sha256(json.dumps(
                             self.snap, ensure_ascii=False,
                             sort_keys=True).encode('utf-8')).hexdigest()[:16])
        self.assertEqual(self.inp['prompt_contract'], {
            'language': 'zh', 'output_schema_version': 'hs-1.0',
            'counter_evidence_required': True,
            'min_competing_hypotheses': 2,
            'numeric_grounding_required': True})
        self.assertEqual(self.inp['prior_knowledge'],
                         {'theses_block': None, 'views_block': None,
                          'prior_conclusions': []})
        self.assertEqual(self.inp['evidence_pack']['scorecard_summary'],
                         {'status': 'MISSING',
                          'reason': 'scorecard_summary未提供(装配期如实登记缺席)'})
        self.assertEqual(gia.validate_input(self.inp), [])

    def test_task_ref_echo(self):
        t = self.inp['task_ref']
        self.assertEqual(t['task_id'], 'RT-2026-06-30~2026-09-30-RD-DIV-001-feed0001')
        self.assertEqual(t['phenomenon'], self.task['phenomenon'])
        self.assertEqual(t['indicators'], [RATE_METRIC, GOLD_METRIC])
        self.assertEqual(t['window'], {'start': '2026-06-30', 'end': '2026-09-30'})
        self.assertEqual(t['detection'], self.task['detection'])
        self.assertEqual(len(t['history_tail']), 5)          # HISTORY_TAIL_MAX
        self.assertEqual([h['note'] for h in t['history_tail']],
                         ['note2', 'note3', 'note4', 'note5', 'note6'])

    def test_facts_verbatim_projection(self):
        """数值零旁路(机制4): 事实投影与 fixture 字面量逐位相等。"""
        self.assertEqual(self.inp['evidence_pack']['facts'],
                         [TIPS_FACT_PROJ, GOLD_FACT_PROJ])
        self.assertEqual(self.inp['absent_registry'], [])


class T1c_ValidateInputNegative(unittest.TestCase):
    """要点①: 字段级校验负向(破坏各字段须报问题,禁静默放行)。"""

    def setUp(self):
        snap = build_synthetic_snapshot({RATE_METRIC: VAL_TIPS})
        self.inp = gia.assemble_mode_a(snap, build_synthetic_task(
            (RATE_METRIC,)))

    def test_missing_top_field(self):
        bad = copy.deepcopy(self.inp)
        del bad['prompt_contract']
        self.assertTrue(gia.validate_input(bad))

    def test_prompt_contract_constant_drift(self):
        bad = copy.deepcopy(self.inp)
        bad['prompt_contract']['min_competing_hypotheses'] = 1
        probs = gia.validate_input(bad)
        self.assertTrue(any('min_competing_hypotheses须=2(合同级)' in p
                            for p in probs), probs)
        bad2 = copy.deepcopy(self.inp)
        bad2['prompt_contract']['counter_evidence_required'] = False
        self.assertTrue(gia.validate_input(bad2))

    def test_digest_shape_and_gate_value(self):
        bad = copy.deepcopy(self.inp)
        bad['snapshot_binding']['snapshot_digest'] = 'xyz'
        self.assertTrue(gia.validate_input(bad))
        bad2 = copy.deepcopy(self.inp)
        bad2['snapshot_binding']['gate_a'] = 'FAIL'
        self.assertTrue(gia.validate_input(bad2))

    def test_absent_level_enum(self):
        bad = copy.deepcopy(self.inp)
        bad['absent_registry'].append({'metric_id': 'X', 'level': 'ABSENT_FOO',
                                       'reason': 'r'})
        self.assertTrue(gia.validate_input(bad))

    def test_mode_mismatch(self):
        bad = copy.deepcopy(self.inp)
        bad['query_ref'] = {'query_id': 'q'}
        self.assertTrue(gia.validate_input(bad))

    def test_hidden_missing_ref(self):
        bad = copy.deepcopy(self.inp)
        bad['evidence_pack']['correlation_ref'] = None
        self.assertTrue(gia.validate_input(bad))


class T2_GateRefusal(unittest.TestCase):
    """要点②(b): Gate A FAIL/None 拒绝装配(fail-closed,沿装配器拒绝语义)。"""

    def test_gate_fail_refuses(self):
        snap = rebuild_declarations(build_synthetic_snapshot(
            drop_metrics=(GOLD_METRIC,)))     # 核心缺失→FAIL(声明如实)
        self.assertEqual(rp.gate_status(snap)[0], 'FAIL')
        with self.assertRaises(gia.AssemblyRefused) as cm:
            gia.assemble_mode_a(snap, build_synthetic_task())
        self.assertIn('Gate A', str(cm.exception))

    def test_gate_illegal_none_refuses(self):
        snap = build_synthetic_snapshot()
        snap['quality']['counts']['PASS'] += 1   # 计数漂移→声明↔重算矛盾→None
        self.assertIsNone(rp.gate_status(snap)[0])
        with self.assertRaises(gia.AssemblyRefused) as cm:
            gia.assemble_mode_a(snap, build_synthetic_task())
        self.assertIn('Gate A', str(cm.exception))


class T2b_NoRawArchivePaths(unittest.TestCase):
    """要点②(a): 装配产物零原始档路径引用(除 facts[].source_file 披露槽位)。"""

    def setUp(self):
        snap = build_synthetic_snapshot({RATE_METRIC: VAL_TIPS,
                                         GOLD_METRIC: VAL_GOLD})
        self.inp = gia.assemble_mode_a(snap, build_synthetic_task())

    def _walk_strings(self, obj):
        if isinstance(obj, str):
            yield obj
        elif isinstance(obj, dict):
            for k, v in obj.items():
                yield from self._walk_strings(k)
                yield from self._walk_strings(v)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                yield from self._walk_strings(v)

    def test_zero_path_references(self):
        strings = list(self._walk_strings(self.inp))
        with_sep = [s for s in strings if '/' in s or '\\' in s]
        self.assertEqual(with_sep, [])
        self.assertEqual([s for s in strings if 'data' + '/daily' in s], [])
        self.assertEqual([s for s in strings if '*' in s or '?' in s], [])
        # 披露槽位: 仅规范 basename 逐字透传(机制2),无路径成分
        srcs = {f['source_file'] for f in self.inp['evidence_pack']['facts']}
        self.assertEqual(srcs, {'macro_' + YMDS + '.json',
                                'global_' + YMDS + '.json'})


class T2c_SourceBoundaryLock(unittest.TestCase):
    """要点②(机制1): 装配器源码级边界锁(沿 E2E-A T6 先例)。"""

    def test_source_locks(self):
        path = os.path.join(ROOT, 'scripts', 'glm_input_assembler.py')
        with open(path, 'r', encoding='utf-8') as f:
            src = f.read()
        self.assertEqual(src.count('ACCESS_POINT_EXEMPT'), 1)
        self.assertNotIn('open(', src)                       # 零文件直开
        self.assertIsNone(re.search(r'\bimport\s+glob\b|\bglob\.', src))
        self.assertIsNone(re.search(
            r'\bimport\s+(requests|urllib|http|socket|ssl)\b|'
            r'\bfrom\s+(requests|urllib|http|socket|ssl)\b', src))
        self.assertNotIn('os.environ', src)                  # 零凭证面
        self.assertNotIn('API_KEY', src)
        self.assertNotIn('daily', src)                       # 零原始档目录字样


class T3_AbsentRegistry(unittest.TestCase):
    """要点③: 缺席指标如实登记(absent_registry 非空·零填0·零编造)。"""

    def test_absent_registered_not_zero_filled(self):
        snap = rebuild_declarations(build_synthetic_snapshot(
            {RATE_METRIC: VAL_TIPS}, drop_metrics=(ABSENT_DATA_METRIC,)))
        task = build_synthetic_task(
            (RATE_METRIC, UNREGISTERED_METRIC, ABSENT_DATA_METRIC))
        inp = gia.assemble_mode_a(snap, task)
        self.assertEqual(inp['snapshot_binding']['gate_a'], 'DEGRADED')
        facts = inp['evidence_pack']['facts']
        self.assertEqual([f['metric_id'] for f in facts], [RATE_METRIC])
        self.assertEqual([f['value'] for f in facts], [2.93])
        self.assertEqual(inp['absent_registry'], [
            {'metric_id': 'JGB_10Y', 'level': 'ABSENT_REGISTRY',
             'reason': '指标不在注册表(无身份定义): JGB_10Y'},
            {'metric_id': 'SILVER_F', 'level': 'ABSENT_DATA',
             'reason': '快照facts无该metric_id事实: SILVER_F'}])
        # 零填0断言: 缺席指标不得以任何数值形态出现(0/近似/编造)
        for mid in (UNREGISTERED_METRIC, ABSENT_DATA_METRIC):
            self.assertNotIn(mid, [f['metric_id'] for f in facts])
        self.assertEqual(gia.validate_input(inp), [])


class T3b_ClassifyAbsenceFourLevels(unittest.TestCase):
    """要点③(四级枚举完整): classify_absence 纯函数四级直测。"""

    def setUp(self):
        self.snap = build_synthetic_snapshot({RATE_METRIC: VAL_TIPS})

    def test_registry_level(self):
        self.assertEqual(
            gia.classify_absence(UNREGISTERED_METRIC, self.snap),
            ('ABSENT_REGISTRY', '指标不在注册表(无身份定义): JGB_10Y'))

    def test_source_level(self):
        snap = {'facts': [], 'sources_status': {
            'rate_economy': {'status': 'READ_FAIL', 'error': '合成'}}}
        level, reason = gia.classify_absence('ZQ_F1_PRICE', snap)
        self.assertEqual(level, 'ABSENT_SOURCE')
        self.assertIn('rate_economy:READ_FAIL', reason)

    def test_data_level(self):
        snap = build_synthetic_snapshot(drop_metrics=(ABSENT_DATA_METRIC,))
        level, reason = gia.classify_absence(ABSENT_DATA_METRIC, snap)
        self.assertEqual(level, 'ABSENT_DATA')
        self.assertIn('快照facts无该metric_id事实', reason)

    def test_window_level_and_present(self):
        snap = {'facts': [{'metric_id': RATE_METRIC,
                           'fact_id': RATE_METRIC + '@' + OBS, 'value': 2.93,
                           'derived': {'week': {'available': False,
                                                'reason': '序列不含上一ISO周观测'}}}],
                'sources_status': {}}
        level, reason = gia.classify_absence(RATE_METRIC, snap,
                                             required_window='m6')
        self.assertEqual(level, 'ABSENT_WINDOW')
        self.assertIn('m6', reason)
        self.assertIsNone(gia.classify_absence(RATE_METRIC, self.snap))


class T4_SnapshotBindingTamper(unittest.TestCase):
    """要点④: 篡改快照后装配拒绝(R5 内容摘要层+R2 声明重算层)。"""

    def test_value_tamper_digest_mismatch(self):
        snap = build_synthetic_snapshot({RATE_METRIC: VAL_TIPS,
                                         GOLD_METRIC: VAL_GOLD})
        declared = gia.assemble_mode_a(
            snap, build_synthetic_task())['snapshot_binding']['snapshot_digest']
        tampered = rebuild_declarations(build_synthetic_snapshot(
            {RATE_METRIC: 9.99, GOLD_METRIC: VAL_GOLD}))
        self.assertEqual(rp.gate_status(tampered)[0], 'PASS')  # 值变不改变门禁
        with self.assertRaises(gia.AssemblyRefused) as cm:
            gia.assemble_mode_a(tampered, build_synthetic_task(),
                                expected_snapshot_digest=declared)
        self.assertIn('摘要不一致', str(cm.exception))

    def test_declaration_lie_refuses_without_expected(self):
        snap = rebuild_declarations(build_synthetic_snapshot(
            drop_metrics=(GOLD_METRIC,)))                     # 核心缺失→重算FAIL
        snap['gate_a']['status'] = 'PASS'                     # 声明说谎
        self.assertIsNone(rp.gate_status(snap)[0])
        with self.assertRaises(gia.AssemblyRefused) as cm:
            gia.assemble_mode_a(snap, build_synthetic_task())  # 无 declared 亦拒
        self.assertIn('Gate A', str(cm.exception))


def build_synthetic_query():
    """合成 E2E-B StructuredResearchQuery IR(契约: P03_E2EB_DESIGN.md §三(a))。"""
    return {
        'query_id': 'QB-20261104-001',
        'created_at': '2026-11-04T20:00:00+08:00',
        'mode': 'B',
        'question_text': '实际利率与黄金最近的背离怎么看?',
        'as_of': '2026-11-04',
        'target_snapshot_id': SNAP_ID,
        'metric_bindings': [
            {'binding_id': 'MB-1', 'metric_id': RATE_METRIC, 'role': 'level',
             'window': None, 'field': 'value', 'status': 'RESOLVED',
             'absence_reason': None,
             'provenance': {'metric_id': RATE_METRIC, 'snapshot_id': SNAP_ID,
                            'fact_id': RATE_METRIC + '@' + OBS,
                            'observation_date': OBS, 'quality_status': 'PASS',
                            'calculation_ref': None}},
            {'binding_id': 'MB-2', 'metric_id': UNREGISTERED_METRIC,
             'role': 'level', 'window': None, 'field': 'value',
             'status': 'ABSENT_REGISTRY',
             'absence_reason': 'E2查无身份(合成IR fixture)', 'provenance': None},
            {'binding_id': 'MB-3', 'metric_id': 'SHCOMP',
             'role': 'derived_window', 'window': 'm6', 'field': 'pct_change',
             'status': 'ABSENT_WINDOW',
             'absence_reason': '序列不足6个月(合成IR fixture)',
             'provenance': None}],
        'derived_operations': [
            {'op_id': 'OP-1', 'op_type': 'spread', 'operands': ['MB-1'],
             'formula': 'UST_10Y − UST_2Y', 'unit': 'percentage_point',
             'status': 'COMPUTED', 'result': 0.52,
             'calculation_ref': '合成fixture'}],
        'unresolved_entities': [],
        'answer_constraints': {'grounding_required': True,
                               'no_data_policy': 'report_absence'},
    }


class T5_ModeB(unittest.TestCase):
    """模式 B 形态: 引用摘要/接地投影/缺席透传(E2E-B WP-B1/B2 未落地,
    按缺席登记路径处理——绑定级缺席透传,查询级无IR拒绝)。"""

    def setUp(self):
        self.snap = build_synthetic_snapshot({RATE_METRIC: VAL_TIPS})
        self.query = build_synthetic_query()

    def test_mode_b_assembly(self):
        inp = gia.assemble_mode_b(self.snap, self.query)
        self.assertEqual(inp['mode'], 'B')
        self.assertIsNone(inp['task_ref'])
        qr = inp['query_ref']
        self.assertEqual(sorted(qr), sorted([
            'query_id', 'question_text', 'as_of', 'metric_bindings_digest',
            'derived_ops_digest']))
        self.assertEqual(qr['query_id'], 'QB-20261104-001')
        self.assertEqual(qr['question_text'], '实际利率与黄金最近的背离怎么看?')
        self.assertEqual(qr['as_of'], '2026-11-04')
        self.assertEqual(qr['metric_bindings_digest'],
                         spec_digest(self.query['metric_bindings']))
        self.assertEqual(qr['derived_ops_digest'],
                         spec_digest(self.query['derived_operations']))
        self.assertEqual(inp['evidence_pack']['facts'], [TIPS_FACT_PROJ])
        self.assertEqual(inp['absent_registry'], [
            {'metric_id': 'JGB_10Y', 'level': 'ABSENT_REGISTRY',
             'reason': 'E2查无身份(合成IR fixture)'},
            {'metric_id': 'SHCOMP', 'level': 'ABSENT_WINDOW',
             'reason': '序列不足6个月(合成IR fixture)'}])
        self.assertEqual(gia.validate_input(inp), [])

    def test_ungrounded_resolved_refuses(self):
        q = copy.deepcopy(self.query)
        q['metric_bindings'][0]['provenance']['fact_id'] = \
            RATE_METRIC + '@2026-12-31'
        with self.assertRaises(gia.AssemblyRefused) as cm:
            gia.assemble_mode_b(self.snap, q)
        self.assertIn('接地失败', str(cm.exception))

    def test_binding_snapshot_mismatch_refuses(self):
        q = copy.deepcopy(self.query)
        q['metric_bindings'][0]['provenance']['snapshot_id'] = \
            'research_snapshot_20261101'
        with self.assertRaises(gia.AssemblyRefused) as cm:
            gia.assemble_mode_b(self.snap, q)
        self.assertIn('快照失配', str(cm.exception))

    def test_binding_metric_identity_mismatch_refuses(self):
        q = copy.deepcopy(self.query)
        q['metric_bindings'][0]['metric_id'] = GOLD_METRIC   # 绑定身份≠事实身份
        with self.assertRaises(gia.AssemblyRefused) as cm:
            gia.assemble_mode_b(self.snap, q)
        self.assertIn('身份不符', str(cm.exception))

    def test_no_ir_refuses(self):
        with self.assertRaises(gia.AssemblyRefused) as cm:
            gia.assemble_mode_b(self.snap, None)
        self.assertIn('WP-B1', str(cm.exception))

    def test_target_snapshot_mismatch_refuses(self):
        q = copy.deepcopy(self.query)
        q['target_snapshot_id'] = 'research_snapshot_20261101'
        with self.assertRaises(gia.AssemblyRefused) as cm:
            gia.assemble_mode_b(self.snap, q)
        self.assertIn('绑定快照失配', str(cm.exception))


class T6_R1Shell(unittest.TestCase):
    """R1 壳入口: 标准化层快照选择(research_snapshot_*.json)→核心装配同构。"""

    def test_shell_equals_core(self):
        snap = build_synthetic_snapshot({RATE_METRIC: VAL_TIPS,
                                         GOLD_METRIC: VAL_GOLD})
        task = build_synthetic_task()
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, 'research_snapshot_' + YMDS + '.json'),
                      'w', encoding='utf-8') as f:
                json.dump(snap, f, ensure_ascii=False)
            via_shell = gia.assemble(YMDS, td, mode='A', task=task)
        self.assertEqual(via_shell, gia.assemble_mode_a(snap, task))

    def test_no_snapshot_refuses(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(gia.AssemblyRefused) as cm:
                gia.assemble(YMDS, td, mode='A', task=build_synthetic_task())
        self.assertIn('R1', str(cm.exception))


class T7_TaskSchemaContract(unittest.TestCase):
    """E2E-A 任务 schema 契约(可增不可减): 最低字段缺失拒绝装配。"""

    def setUp(self):
        self.snap = build_synthetic_snapshot()

    def test_missing_min_field_refuses(self):
        task = build_synthetic_task()
        del task['falsifiable_conditions']
        with self.assertRaises(gia.AssemblyRefused) as cm:
            gia.assemble_mode_a(self.snap, task)
        self.assertIn('falsifiable_conditions', str(cm.exception))

    def test_empty_indicators_refuses(self):
        task = build_synthetic_task(())
        with self.assertRaises(gia.AssemblyRefused) as cm:
            gia.assemble_mode_a(self.snap, task)
        self.assertIn('indicators', str(cm.exception))


class T8_EchoParams(unittest.TestCase):
    """R011 纪律: echo=代码常量=REPORT §二 登记值(三方一致,字面量)。"""

    def test_echo_equals_registered_literals(self):
        self.assertEqual(gia.echo_params(), {
            'contract_version': 'gri-1.0',
            'mode_enum': ['A', 'B'],
            'absent_levels': ['ABSENT_REGISTRY', 'ABSENT_SOURCE',
                              'ABSENT_DATA', 'ABSENT_WINDOW'],
            'evidence_fact_fields': ['metric_id', 'fact_id', 'value', 'unit',
                                     'observation_date', 'quality_status',
                                     'derived', 'source_file'],
            'task_ref_fields': ['task_id', 'phenomenon', 'indicators',
                                'window', 'detection', 'history_tail'],
            'query_ref_fields': ['query_id', 'question_text', 'as_of',
                                 'metric_bindings_digest',
                                 'derived_ops_digest'],
            'prompt_contract_keys': ['language', 'output_schema_version',
                                     'counter_evidence_required',
                                     'min_competing_hypotheses',
                                     'numeric_grounding_required'],
            'min_competing_hypotheses': 2,
            'counter_evidence_required': True,
            'numeric_grounding_required': True,
            'prompt_language_default': 'zh',
            'output_schema_version_default': 'hs-1.0',
            'history_tail_max': 5,
            'ref_digest_len': 16})


if __name__ == '__main__':
    unittest.main(verbosity=2)
