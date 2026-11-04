#!/usr/bin/env python3
"""IA-P03-W2-GLM-WP-G3: GLM 研究结论层 可反驳条件推导与门禁对接+档案衔接(结论整合模块)

合同 IA-P03-W2-GLM-WP-G3-AC-v1.0 / DESIGN §五(docs/P03_W2_GLM_DESIGN.md:152-190):
- (1) 推导规则四步(L154-161): 主张变量化→阈值三来源(证据包/注册表/先验触发器)
  →条件规格化(op/mode 与现行预测规格对齐,窗口默认=task_ref.window)→区分性检查
  (步4 由 G2 校验器承接,四元组判据禁复制分叉,trace 登记 deferred);
- (2) Gate B 三态提案路径(L163-169): 论点(终态/确信度)/观点(评级/确信度)/预测候选
  ——GLM 假设永不直接写状态;门禁判定与现行门禁同构(复用 allocation_engine 常量
  [MIN_EVIDENCE_FOR_RATING_CHANGE 等]与 _record_proposal/_change_direction 机制);
  数值校验前置=G2 校验器(结构化数值接地,零容差)×rp.combine_gates(B4 合成),
  FAIL→阻断提案(apply_status_updates FAIL 语义同构);
- (3) append-only 结论记录+ID 交叉引用(L171-175): 记录含 hypothesis_ids/
  task_id|origin_query_id(必携其一)/snapshot_id+snapshot_digest/输出全文摘要/
  门禁裁决结果;写入后不可改不可删;重放=幂等跳过或新记录追加(登记,沿 E2E-A
  rtm.REPLAY_POLICY 先例);
- (4) E2E-A 任务 schema 字段映射(L177-190,9 行): rtm.SCHEMA_MIN_FIELDS 契约同源
  (复用导入);task_ref 只读回显不回写;状态推进=提案(经门禁)。

G2 预留承接(glm_output_validator REPORT §二.3 登记):
- 来源(iii) 先验触发器结构化注入面: extract_prior_trigger_targets→数值集,
  喂 G2 legal_target_numbers(prior_trigger_targets=…);
- direction 枚举三值完整性(support/counter/neutral): 投影层值域校验承接。

零真实 GLM/LLM 调用、零凭证、零付费、零网络出站(设计对象≠设计手段;真实调用属
WP-G4,执行前置=用户批准凭证/费用 PENDING 未批)。零文件读写/零glob/零算术旁路
(档案=注入面 dict,生产持久化属编排层;阈值=三来源逐位投影)。import 面纯标准库+
项目既有模块(allocation_engine/glm_output_validator/research_provenance/
research_task_manager 复用调用,禁复制分叉)。
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import allocation_engine as ae        # noqa: E402 (门禁常量/提案留档/方向语义 复用调用)
import glm_output_validator as gov    # noqa: E402 (G2 校验/合法来源/枚举 复用调用)
import research_provenance as rp      # noqa: E402 (B4 combine_gates 复用调用)
import research_task_manager as rtm   # noqa: E402 (E2E-A schema/状态机 契约同源)

# ══ 契约常量(DESIGN 明示值/既有登记值沿用;登记=常量=echo 三方一致,REPORT §二.1) ══
DERIVATION_STEPS = ('variableize', 'threshold', 'specification', 'distinctiveness')
THRESHOLD_SOURCES = ('evidence_pack', 'registry', 'prior_triggers')   # DESIGN L157
SPEC_KEYS = tuple(gov.SPEC_FIELDS)                    # (metric,op,target,mode,window)
SPEC_OPS = gov.SPEC_OPS                               # 复用引用(禁复制分叉)
SPEC_MODES = gov.SPEC_MODES                           # 复用引用
NON_SPECIFIABLE_MARKER = gov.NON_SPECIFIABLE_MARKER   # '不可程序裁决'(DESIGN L161)
PROPOSAL_KINDS = ('thesis_status', 'thesis_confidence',
                  'view_rating', 'view_confidence', 'prediction_candidate')
THESIS_TERMINAL_STATES = ('已失效', '已验证')          # report_generator.py:1137 语义
THESIS_TRIGGER_DIRECTIONS = {'已失效': 'invalidation', '已验证': 'upgrade'}
RATING_CHANGE_MIN_EVIDENCE = ae.MIN_EVIDENCE_FOR_RATING_CHANGE   # 复用引用(=2)
PROPOSAL_DEDUP_DAYS = ae.PROPOSAL_DEDUP_DAYS           # 复用引用(=21)
PRED_INITIAL_STATUS = 'not_yet_triggered'              # ae.PRED_STATUSES 之首
PRED_CANDIDATE_SPEC_KEYS = ('pred_metric', 'pred_op', 'pred_target', 'pred_mode')
CONCLUSION_ID_PREFIX = 'CR-'                           # §六 L207 ID 族(登记型扩展)
DIRECTIONS = gov.DIRECTIONS          # (support,counter,neutral) 三值完整承接(G2留G3)
OUTCOMES = (gov.OUTCOME_ACCEPTED, gov.OUTCOME_ACCEPTED_DOWNGRADED,
            gov.OUTCOME_ABSENT_REGISTERED)             # G2 三结局透传
E2EA_MAP_ROWS = 9                                     # DESIGN §五(4) 表 L181-189

# ══ 实现登记值(DESIGN 未定值,本包登记;运行后禁回改,REPORT §二.2) ═════════
DEFAULT_DERIVE_OP = '>='            # 推导参数非猜测(方向判定=NLP 面,留编排层)
DEFAULT_DERIVE_MODE = 'expiry'      # report_generator.py:526 expiry 缺省同款
THRESHOLD_SOURCE_PRECEDENCE = ('evidence_pack', 'registry', 'prior_triggers')
_DERIVED_WINDOW_ORDER = ('week', 'mtd', 'ytd')         # 来源(i) 派生窗口固定序
CONDITIONS_PER_METRIC = 1                              # 每 metric 默认 1 条
CONCLUSION_FINGERPRINT_KEYS = ('conclusion_id', 'output_digest')
ARCHIVE_REPLAY_POLICY = ('idempotent-skip on identical fingerprint; '
                         'new record appended on different fingerprint; '
                         'existing records never rewritten')
GATE_B_BLOCKED_CLASSIFICATION = 'FAIL'   # 数值校验前置失败→阻断(B9 同构)
OUTPUT_DIGEST_LEN = 16                # sha256 前16位(G1 REF_DIGEST_LEN/R5 同风格)
E2EA_CONCLUSIONS_KEY = 'conclusions'  # DESIGN L188 登记型扩展子结构键名
PRIOR_TRIGGER_KEYS = ('trig_id', 'metric', 'op', 'target')   # 结构化触发器最小契约

_HY_ID_RE = re.compile(r'^HY-\d{8}-\d{3}$')            # DESIGN L97
_CR_ID_RE = re.compile(r'^CR-\d{8}-\d{3}(?:__v\d+)?$')  # 同日序列+版本后缀
_RT_PREFIX_RE = re.compile(r'^RT-')                     # E2E-A 任务(rtm.py:53 形态)
_QB_PREFIX_RE = re.compile(r'^QB-')                     # E2E-B 查询(§六 L207)

# E2E-A 字段映射表(DESIGN §五(4) L181-189 逐行登记;9 行,登记=常量=测试契约)
E2EA_FIELD_MAP = (
    ('task_ref.task_id', 'task_id', '回写外键(标识符透传)'),
    ('task_ref其余字段', 'phenomenon/indicators/window/detection',
     '只读回显(echo),不回写——防参数漂移'),
    ('statement', 'history(追加记录文本)', '假设陈述作为结论记录追加进任务历史'),
    ('supporting_evidence/counter_evidence', 'evidence',
     '证据引用方向化挂载;快照标识=fact_id/snapshot_id,数据质量状态=quality_status透传'),
    ('falsifiable_conditions(可规格化子集)', 'falsifiable_conditions(非空)',
     '假设级条件并入任务级条件集(任务级非空约束由首个升级的假设满足)'),
    ('falsifiable_conditions.spec', '(无对应最低字段;预测候选落allocation_views侧)',
     '条件规格→预测候选,经预测门禁独立落档'),
    ('confidence/limitations', 'history(追加记录属性)',
     '辅助标注随结论记录入档,不参与门禁'),
    ('hypothesis_id', '(无对应最低字段;「可增不可减」条款允许实现期增设)',
     '结论记录标识;实现包增设 conclusions 子结构承接(登记型扩展)'),
    ('任务状态推进(pending→active→concluded→tracking)', 'status+history',
     '本层证据装配完成=任务active的组成部分;反驳条件触发→concluded/tracking的'
     '提案(经门禁,不直接改状态)'),
)


class InvalidConclusionRecord(Exception):
    """结论记录非法(交叉引用缺失/ID 格式非法): fail-closed 拒绝入档。"""


class ArchiveImmutable(Exception):
    """append-only 档案改写被拒: 结论记录写入后不可改不可删(DESIGN §五(3) L173)。"""


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def echo_params():
    """登记参数 echo(R011 纪律: 登记=常量=echo 三方一致)。"""
    return {
        'derivation_steps': list(DERIVATION_STEPS),
        'threshold_sources': list(THRESHOLD_SOURCES),
        'spec_keys': list(SPEC_KEYS),
        'spec_ops': list(SPEC_OPS),
        'spec_modes': list(SPEC_MODES),
        'non_specifiable_marker': NON_SPECIFIABLE_MARKER,
        'proposal_kinds': list(PROPOSAL_KINDS),
        'thesis_terminal_states': list(THESIS_TERMINAL_STATES),
        'rating_change_min_evidence': RATING_CHANGE_MIN_EVIDENCE,
        'proposal_dedup_days': PROPOSAL_DEDUP_DAYS,
        'pred_initial_status': PRED_INITIAL_STATUS,
        'pred_candidate_spec_keys': list(PRED_CANDIDATE_SPEC_KEYS),
        'directions': list(DIRECTIONS),
        'outcomes': list(OUTCOMES),
        'e2ea_map_rows': E2EA_MAP_ROWS,
        'default_derive_op': DEFAULT_DERIVE_OP,
        'default_derive_mode': DEFAULT_DERIVE_MODE,
        'threshold_source_precedence': list(THRESHOLD_SOURCE_PRECEDENCE),
        'derived_window_order': list(_DERIVED_WINDOW_ORDER),
        'conditions_per_metric': CONDITIONS_PER_METRIC,
        'conclusion_fingerprint_keys': list(CONCLUSION_FINGERPRINT_KEYS),
        'archive_replay_policy': ARCHIVE_REPLAY_POLICY,
        'gate_b_blocked_classification': GATE_B_BLOCKED_CLASSIFICATION,
        'output_digest_len': OUTPUT_DIGEST_LEN,
        'e2ea_conclusions_key': E2EA_CONCLUSIONS_KEY,
        'prior_trigger_keys': list(PRIOR_TRIGGER_KEYS),
    }


# ══ §五(1) 步0.5: 先验触发器结构化注入面(G2 预留承接) ═══════════════════

def extract_prior_trigger_targets(prior_triggers):
    """结构化触发器列表 → 阈值数值集(合法来源(iii);G2 legal_target_numbers 的
    prior_trigger_targets 注入参数的编排层构造面)。

    prior_triggers 每项含 PRIOR_TRIGGER_KEYS 字段族(trig_id/metric/op/target);
    只取数值型 target(DESIGN L157(iii): 论点 quant_triggers/观点 triggers 的
    既有触发器阈值)。测试一律注入合成集(确定性,R014-D3 漂移防护)。"""
    targets = set()
    for t in prior_triggers or []:
        if isinstance(t, dict) and _num(t.get('target')):
            targets.add(t['target'])
    return targets


# ══ §五(1) 推导规则四步(步1-3 推导;步4 区分性由 G2 校验器承接) ═══════════

def variableize_claim(hypothesis, inp, *, registry_metrics=None):
    """步1 主张变量化(DESIGN L156): statement 中指标三分类。

    返回 {'present': [在场 metric_id…(保 facts 序)], 'absent': [登记缺席…],
    'registered_not_in_input': [注册表内但未入输入…(不产条件不引入,登记 notes)]}
    ——条件的 metric 面=在场∪登记缺席(禁引入 absent_registry 之外的指标:
    由构造满足——推导只对 present 产条件、只对 absent 产 limitations 义务)。"""
    stmt = (hypothesis or {}).get('statement') or ''
    if not isinstance(stmt, str):
        stmt = str(stmt)
    facts = [f for f in ((inp.get('evidence_pack') or {}).get('facts')) or []
             if isinstance(f, dict)]
    absent_ids = [a.get('metric_id') for a in inp.get('absent_registry') or []
                  if isinstance(a, dict)]
    present, seen = [], set()
    for f in facts:
        mid = f.get('metric_id')
        if isinstance(mid, str) and mid in stmt and mid not in seen:
            present.append(mid)
            seen.add(mid)
    absent = [m for m in absent_ids if isinstance(m, str) and m in stmt]
    not_in_input = []
    if registry_metrics is None:
        registry_metrics = rp.active_registry_metrics()   # 复用调用
    for mid in registry_metrics:
        if isinstance(mid, str) and mid in stmt and mid not in seen \
                and mid not in absent:
            not_in_input.append(mid)
    return {'present': present, 'absent': absent,
            'registered_not_in_input': sorted(not_in_input)}


def legal_thresholds_for(metric_id, inp, *, registry_metrics=None,
                         prior_triggers=None):
    """步2 阈值取值约束(DESIGN L157): 该指标的三来源合法阈值(逐源带标记,保序)。

    (i) evidence_pack: 该指标事实 value+派生窗口值(week/mtd/ytd 固定序×
    gov._DERIVED_VALUE_KEYS 字段族——与 G2 接地集同源,复用引用禁复制);
    (ii) registry: validation.range 端点+max_week_pct_move(gov.
    REGISTRY_THRESHOLD_KEYS 点名两族,不扩展);
    (iii) prior_triggers: 注入触发器中 metric 匹配项的 target。"""
    out = {'evidence_pack': [], 'registry': [], 'prior_triggers': []}
    for f in ((inp.get('evidence_pack') or {}).get('facts')) or []:
        if isinstance(f, dict) and f.get('metric_id') == metric_id:
            if _num(f.get('value')):
                out['evidence_pack'].append(f['value'])
            for w in _DERIVED_WINDOW_ORDER:
                wrec = (f.get('derived') or {}).get(w)
                if isinstance(wrec, dict):
                    for k in gov._DERIVED_VALUE_KEYS:   # 复用引用(禁复制分叉)
                        if _num(wrec.get(k)):
                            out['evidence_pack'].append(wrec[k])
            break
    if registry_metrics is None:
        registry_metrics = rp.active_registry_metrics()   # 复用调用
    m = registry_metrics.get(metric_id) or {}
    val = m.get('validation') or {}
    rng = val.get('range')
    if isinstance(rng, (list, tuple)):
        for v in list(rng)[:2]:
            if _num(v):
                out['registry'].append(v)
    if _num(val.get('max_week_pct_move')):
        out['registry'].append(val['max_week_pct_move'])
    for t in prior_triggers or []:
        if isinstance(t, dict) and t.get('metric') == metric_id \
                and _num(t.get('target')):
            out['prior_triggers'].append(t['target'])
    return out


def _default_window(inp):
    tref = inp.get('task_ref')
    if isinstance(tref, dict) and isinstance(tref.get('window'), dict):
        w = tref['window']
        return {'start': w.get('start'), 'end': w.get('end')}
    return None     # 模式 B 无 task_ref: spec.window 缺省 None(G2 容忍)


def derive_falsifiable_conditions(hypothesis, inp, *, op=None, mode=None,
                                  threshold_source='auto',
                                  registry_metrics=None, prior_triggers=None,
                                  task_window=None):
    """§五(1) 推导规则(步1-3 全流程+步4 登记;确定性纯函数)。

    返回 {'spec_conditions': [{cond_text, spec}…], 'non_specifiable':
    [{metric_id, declaration}…], 'derivation_notes': […], 'trace': […]}。
    - 每 present metric 产 CONDITIONS_PER_METRIC 条条件;阈值按
      THRESHOLD_SOURCE_PRECEDENCE(auto)或指定来源取首个数值——三来源之外的
      数值不产生(编造阈值=0 条,DESIGN L157 校验器拒绝的推导侧镜像);
    - absent metric 主张→non_specifiable(declaration 含不可程序裁决标记,
      apply 时转 limitations 声明,DESIGN L156/L161);
    - present 但所选来源全空→该 metric 计 non_specifiable(在场而无可取阈值=
      不可规格化,如实分流不编造)。
    op/mode=推导参数(缺省 DEFAULT_DERIVE_OP/MODE;方向判定=NLP 面留编排层)。"""
    op = op or DEFAULT_DERIVE_OP
    mode = mode or DEFAULT_DERIVE_MODE
    if op not in SPEC_OPS:
        raise ValueError(f'op 非法(枚举{SPEC_OPS}): {op!r}')
    if mode not in SPEC_MODES:
        raise ValueError(f'mode 非法(枚举{SPEC_MODES}): {mode!r}')
    stmt = (hypothesis or {}).get('statement') or ''
    win = task_window if task_window is not None else _default_window(inp)
    win_desc = f"{win.get('start')}~{win.get('end')}" if isinstance(win, dict) \
        else '(任务窗缺省)'
    step1 = variableize_claim(hypothesis, inp, registry_metrics=registry_metrics)
    spec_conditions, non_specifiable = [], []
    trace = [{'step': 'variableize',
              'present': step1['present'], 'absent': step1['absent'],
              'registered_not_in_input': step1['registered_not_in_input']}]
    absent_reasons = {a.get('metric_id'): a.get('reason')
                      for a in inp.get('absent_registry') or []
                      if isinstance(a, dict)}
    for mid in step1['absent']:
        non_specifiable.append({
            'metric_id': mid,
            'declaration': (f'{mid}相关主张不可程序裁决(指标缺席输入,该条件'
                            f'不可推导转limitations声明;缺席原因:'
                            f'{absent_reasons.get(mid, "未注明")})')})
    for mid in step1['present']:
        thr = legal_thresholds_for(mid, inp, registry_metrics=registry_metrics,
                                   prior_triggers=prior_triggers)
        trace.append({'step': 'threshold', 'metric': mid, 'sources': {
            k: list(v) for k, v in thr.items()}})
        src = threshold_source
        if src == 'auto':
            src = next((s for s in THRESHOLD_SOURCE_PRECEDENCE if thr[s]), None)
        candidates = thr.get(src) if src in THRESHOLD_SOURCES else []
        if not candidates:
            non_specifiable.append({
                'metric_id': mid,
                'declaration': (f'{mid}主张不可程序裁决(在场但三来源无可取'
                                '阈值,不可规格化,如实分流不编造阈值)')})
            continue
        for tgt in candidates[:CONDITIONS_PER_METRIC]:
            spec = {'metric': mid, 'op': op, 'target': tgt, 'mode': mode}
            spec['window'] = win
            spec_conditions.append({
                'cond_text': (f'若 {mid} 于窗口{win_desc} {op} {tgt}'
                              f'({mode}语义)成立,则本假设该主张可程序反驳'
                              f'(阈值来源:{src})'),
                'spec': spec})
            trace.append({'step': 'specification', 'metric': mid,
                          'source': src, 'target': tgt, 'op': op, 'mode': mode})
    notes = [f'注册表指标 {m} 出现在 statement 但未入输入(不在场且非登记缺席,'
             f'不产条件不引入,DESIGN L156)' for m in step1['registered_not_in_input']]
    trace.append({'step': 'distinctiveness', 'status': 'deferred-to-g2-validator',
                  'note': '区分性判据由 G2 校验器承接(四元组(metric,op,target,'
                          'mode)两两不全同,glm_output_validator.py:482-493),'
                          '本模块禁复制分叉;集成断言=apply 后过 G2 校验'})
    return {'spec_conditions': spec_conditions,
            'non_specifiable': non_specifiable,
            'derivation_notes': notes, 'trace': trace}


def _spec_quad(spec):
    return (spec.get('metric'), spec.get('op'), spec.get('target'),
            spec.get('mode'))


def apply_derived_conditions(hypothesis, derivation):
    """分流落回假设(DESIGN L156/L161): 推导条件合入(四元组等值去重)+
    non_specifiable 逐条转 limitations 声明条目。返回新假设 dict(不改入参)。"""
    h = dict(hypothesis or {})
    conds = list(h.get('falsifiable_conditions') or [])
    known = {_spec_quad(c.get('spec')) for c in conds
             if isinstance(c, dict) and isinstance(c.get('spec'), dict)}
    for c in derivation.get('spec_conditions') or []:
        if _spec_quad(c['spec']) not in known:
            conds.append({'cond_text': c['cond_text'], 'spec': c['spec']})
            known.add(_spec_quad(c['spec']))
    h['falsifiable_conditions'] = conds
    lims = list(h.get('limitations') or [])
    for ns in derivation.get('non_specifiable') or []:
        lims.append(ns['declaration'])
    h['limitations'] = lims
    return h


# ══ §五(2) Gate B 三态提案路径(数值校验前置+同构门禁+留档复用) ═══════════

def build_gate_b_proposal(inp, validated_output, *, kind, hypothesis=None,
                          target_id=None, change_to=None, current=None,
                          new_support_metrics=(), trigger_rows=(),
                          star_max=None, registry_targets=None,
                          prior_trigger_targets=None, today_iso=None):
    """构造 Gate B 提案(数值校验前置先行;GLM 假设永不直接写状态,DESIGN L165)。

    前置双层(DESIGN L169):
    ① gov.validate_output(G2 结构化数值接地,零容差)=B1-B3 md 报告面的结构化
       等价(B1-B3 对象=md 文件+锚点,HypothesisSet 无 md 载体——判定依据登记
       REPORT §一.2);
    ② rp.combine_gates(gate_a, gate_b)(B4 复用调用)——gate_b=①有问题→FAIL。
    合成 FAIL→blocked 提案(不进门禁判定,apply_status_updates FAIL 语义同构)。"""
    if kind not in PROPOSAL_KINDS:
        raise ValueError(f'proposal kind 非法(枚举{PROPOSAL_KINDS}): {kind!r}')
    probs = gov.validate_output(inp, validated_output,
                                registry_targets=registry_targets,
                                prior_trigger_targets=prior_trigger_targets)
    gate_b = GATE_B_BLOCKED_CLASSIFICATION if probs else 'PASS'
    gate_a = (inp.get('snapshot_binding') or {}).get('gate_a')
    combined = rp.combine_gates(gate_a, gate_b)          # B4 复用调用
    blocked = combined == GATE_B_BLOCKED_CLASSIFICATION
    return {
        'kind': kind,
        'hypothesis_id': (hypothesis or {}).get('hypothesis_id'),
        'target_id': target_id,
        'change_to': change_to,
        'current': current,
        'new_support_metrics': list(new_support_metrics),
        'trigger_rows': list(trigger_rows),
        'star_max': star_max,
        'today_iso': today_iso,
        'numeric_gate': {'validation_problems': probs[:5], 'gate_a': gate_a,
                         'gate_b': gate_b, 'combined': combined},
        'blocked': blocked,
        'block_reason': ('数值校验前置FAIL(输出未过G2校验),阻断提案——'
                         'apply_status_updates FAIL 语义(结论中数值与锚点'
                         '不符→阻断回写)') if blocked else None,
    }


def evaluate_gate_b(proposal):
    """确定性门禁判定(与现行门禁同构;常量复用 ae.* 引用,禁复制字面量)。

    返回 (accepted: bool, reason: str)。同构基准:
    - thesis_status 终态: report_generator.py:1137-1168(invalidation/upgrade
      触发器 fired 或 ≥MIN_EVIDENCE_FOR_RATING_CHANGE 新增独立支持证据);
      过程状态=允许+记录审计(L1169-1175 同构);
    - thesis_confidence/view_confidence: 上调须 ≤star_max
      (report_generator.py:1177-1188 同构;star_max 缺席→fail-closed);
    - view_rating: allocation_engine.py:1262-1269(同向触发器 fired 或
      ≥MIN_EVIDENCE_FOR_RATING_CHANGE;suspend/resume 放宽 1——方向复用
      ae._change_direction);
    - prediction_candidate: spec 完整性(键全/op·mode 枚举/target 数值非 null),
      初始 PRED_INITIAL_STATUS,裁决与生命周期沿既有引擎门禁(B8)。"""
    if proposal.get('blocked'):
        return False, proposal.get('block_reason') or '数值校验前置FAIL,提案阻断'
    kind = proposal.get('kind')
    trig = [r for r in proposal.get('trigger_rows') or []
            if isinstance(r, dict) and r.get('status') == 'triggered']
    new_sup = proposal.get('new_support_metrics') or []
    to = proposal.get('change_to')

    if kind == 'thesis_status':
        if to not in THESIS_TERMINAL_STATES:
            return True, f'过程状态调整({to},非终态)——允许,仍记录审计(现行同构)'
        direction = THESIS_TRIGGER_DIRECTIONS[to]
        fired = [r for r in trig if r.get('direction') == direction]
        if fired:
            return True, (f"{direction}触发器{'+'.join(str(r.get('trig_id')) for r in fired)}"
                          '(引擎核验已触发)')
        if len(new_sup) >= RATING_CHANGE_MIN_EVIDENCE:
            return True, (f'新增独立支持证据{len(new_sup)}项经验证'
                          f'(≥{RATING_CHANGE_MIN_EVIDENCE})')
        return False, (f"'{to}'为终态判定,须{direction}触发器已触发"
                       f"或≥{RATING_CHANGE_MIN_EVIDENCE}项新增独立支持证据"
                       f'(本次{len(new_sup)}项)——与现行门禁同构'
                       '(report_generator.py:1137-1168)')

    if kind in ('thesis_confidence', 'view_confidence'):
        star_max = proposal.get('star_max')
        if not isinstance(to, int) or not 1 <= to <= 5:
            return False, f'确信度非法(1-5整数): {to!r}'
        if star_max is None:
            return False, ('确信度判定须程序星级star_max(证据分级程序验证产物),'
                           '缺席→fail-closed 拒(不得默认通过)')
        if to > star_max:
            return False, (f'证据仅支撑{star_max}★,不足以授予{to}★(上调不得'
                           '超过程序星级,report_generator.py:1177-1188 同构)')
        return True, f'{to}★ ≤ 程序星级{star_max}★(下调/相等技术上自由)'

    if kind == 'view_rating':
        if to not in ae.ALLOWED_RATINGS:
            return False, f'评级非法(枚举{ae.ALLOWED_RATINGS}): {to!r}'
        current = proposal.get('current')
        direction = ae._change_direction(current, to)   # 复用调用
        if direction is None:
            return False, '评级未变更(无提案语义)'
        fired = [r for r in trig if r.get('direction') == direction]
        if fired:
            return True, (f'{direction}触发器'
                          f"{'+'.join(str(r.get('trig_id')) for r in fired)}"
                          '(引擎核验已触发)')
        min_ev = 1 if direction in ('suspend', 'resume') \
            else RATING_CHANGE_MIN_EVIDENCE
        if len(new_sup) >= min_ev:
            return True, (f'新增独立支持证据{len(new_sup)}项经验证(≥{min_ev}'
                          f';direction={direction})')
        return False, (f'评级变更须{direction}同向触发器已触发或≥{min_ev}项'
                       f'程序验证新增证据(本次{len(new_sup)}项)——与现行门禁'
                       '同构(allocation_engine.py:1262-1269)')

    if kind == 'prediction_candidate':
        spec = proposal.get('change_to') or {}
        if not isinstance(spec, dict):
            return False, f'预测候选 spec 非对象: {spec!r}'
        missing = [k for k in PRED_CANDIDATE_SPEC_KEYS if k not in spec]
        if missing:
            return False, f'预测候选 spec 缺键: {missing}'
        if spec.get('pred_op') not in SPEC_OPS:
            return False, f'pred_op 非法(枚举{SPEC_OPS}): {spec.get("pred_op")!r}'
        if spec.get('pred_mode') not in SPEC_MODES:
            return False, (f'pred_mode 非法(枚举{SPEC_MODES}): '
                           f'{spec.get("pred_mode")!r}')
        if not _num(spec.get('pred_target')):
            return False, f'pred_target 须数值(带完整规格者到期由程序裁决): {spec.get("pred_target")!r}'
        return True, (f'预测候选形态校验通过(初始态={PRED_INITIAL_STATUS};'
                      '裁决与终态保护沿既有引擎门禁,B8)')

    return False, f'未知 proposal kind: {kind!r}'


def record_rejected_proposal(target_state, proposal, reason, today_iso):
    """被拒提案留档(DESIGN L175: 不删除、进 proposals 留档)——复用调用
    ae._record_proposal(同向 21 天去重;与现行周报链同一函数,
    report_generator.py:1080/1163 先例: 论点侧同样调用 ae._record_proposal)。"""
    evidence_summary = json.dumps({
        'hypothesis_id': proposal.get('hypothesis_id'),
        'new_support': proposal.get('new_support_metrics'),
        'kind': proposal.get('kind')},
        ensure_ascii=False, sort_keys=True)
    return ae._record_proposal(target_state, str(proposal.get('change_to')),
                               reason, evidence_summary, today_iso)


# ══ §五(3) append-only 结论记录+ID 交叉引用 ═════════════════════════════

def _output_digest(obj):
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode('utf-8')).hexdigest()[:OUTPUT_DIGEST_LEN]


def build_conclusion_record(inp, result, *, gate_b_results=(), seq=1,
                            today_iso=None):
    """结论记录构造(DESIGN L173): 含被门禁拒绝的轮次同样落档
    (gate_b_verdicts 逐项登记 accepted/rejected;L175 被拒提案不删除)。

    result=G2 run_conclusion_pipeline 产物(outcome/validated_output/
    absence_event/…);outcome 三结局透传(OUTCOMES)。
    conclusion_id=CR-YYYYMMDD-NNN(seq 由编排层/调用方给定,缺省 1)。"""
    sb = inp.get('snapshot_binding') or {}
    tref, qref = inp.get('task_ref'), inp.get('query_ref')
    task_id = tref.get('task_id') if isinstance(tref, dict) else None
    origin_query_id = qref.get('query_id') if isinstance(qref, dict) else None
    if not task_id and not origin_query_id:
        raise InvalidConclusionRecord(
            '交叉引用缺失: 结论记录必携 task_id 或 origin_query_id 之一'
            '(锚定产生语境,DESIGN §六 L207)')
    if task_id and not _RT_PREFIX_RE.match(str(task_id)):
        raise InvalidConclusionRecord(f'task_id 形态非法(RT- 前缀族): {task_id!r}')
    if origin_query_id and not _QB_PREFIX_RE.match(str(origin_query_id)):
        raise InvalidConclusionRecord(
            f'origin_query_id 形态非法(QB- 前缀族): {origin_query_id!r}')
    validated = result.get('validated_output')
    hyps = (validated or {}).get('hypotheses') or []
    hyp_ids = [h.get('hypothesis_id') for h in hyps if isinstance(h, dict)]
    for hid in hyp_ids:
        if not (isinstance(hid, str) and _HY_ID_RE.fullmatch(hid)):
            raise InvalidConclusionRecord(
                f'hypothesis_id 格式非法(HY-YYYYMMDD-NNN): {hid!r}')
    outcome = result.get('outcome')
    if outcome not in OUTCOMES:
        raise InvalidConclusionRecord(f'outcome 非法(G2 三结局): {outcome!r}')
    payload = validated if validated is not None else result.get('absence_event')
    day = (today_iso or '1970-01-01').replace('-', '')[:8]
    record = {
        'conclusion_id': f'{CONCLUSION_ID_PREFIX}{day}-{seq:03d}',
        'hypothesis_ids': hyp_ids,
        'task_id': task_id,
        'origin_query_id': origin_query_id,
        'snapshot_id': sb.get('snapshot_id'),
        'snapshot_digest': sb.get('snapshot_digest'),
        'outcome': outcome,
        'output_digest': _output_digest(payload),
        'gate_b_verdicts': [dict(v) for v in gate_b_results],
        'falsifiable_spec_count': sum(
            1 for h in hyps if isinstance(h, dict)
            for c in h.get('falsifiable_conditions') or []
            if isinstance(c, dict) and isinstance(c.get('spec'), dict)
            and _num(c['spec'].get('target'))),
        'created_at': today_iso,
    }
    return record


def validate_conclusion_record(record):
    """档案入档校验: CR- 格式+交叉引用必携其一(append 前置,fail-closed)。"""
    cid = record.get('conclusion_id')
    if not (isinstance(cid, str) and _CR_ID_RE.fullmatch(cid)):
        raise InvalidConclusionRecord(
            f'conclusion_id 格式非法(CR-YYYYMMDD-NNN[__vN]): {cid!r}')
    if not record.get('task_id') and not record.get('origin_query_id'):
        raise InvalidConclusionRecord(
            '交叉引用缺失: 必携 task_id 或 origin_query_id 之一(§六 L207)')
    return True


def append_conclusion_record(record, archive):
    """append-only 追加(注入面;本模块零文件写入,生产持久化属编排层)。

    重放策略(登记 ARCHIVE_REPLAY_POLICY,沿 E2E-A rtm.save_task 先例):
    指纹(conclusion_id+output_digest)一致→幂等跳过(零写入);
    conclusion_id 同而指纹不一致→新版本记录追加(__v{N},原记录字节不动);
    全新→追加。既有记录结构性零修改(append 只增不改)。"""
    validate_conclusion_record(record)
    concl = archive.setdefault('conclusions', [])
    for existing in concl:
        if existing.get('conclusion_id') == record['conclusion_id'] \
                and existing.get('output_digest') == record['output_digest']:
            return 'skipped-idempotent', existing
    base = record['conclusion_id'].split('__v')[0]
    if any((c.get('conclusion_id') == record['conclusion_id'])
           or (str(c.get('conclusion_id', '')).startswith(base + '__v'))
           for c in concl):
        n = 2
        while any(c.get('conclusion_id') == f'{base}__v{n}' for c in concl):
            n += 1
        new_rec = dict(record)
        new_rec['conclusion_id'] = f'{base}__v{n}'
        concl.append(new_rec)
        return 'written-new-version', new_rec
    concl.append(dict(record))
    return 'written', record


def mutate_conclusion_record(archive, conclusion_id, mutations):
    """改写面(显式防呆): append-only 档案结论记录写入后不可改不可删
    (DESIGN §五(3) L173)——任何改写尝试一律拒绝。"""
    raise ArchiveImmutable(
        f'append-only 档案: 结论记录 {conclusion_id} 写入后不可改不可删'
        f'(DESIGN §五(3));mutations={mutations!r} 被拒')


# ══ §五(4) E2E-A 字段映射(rtm.SCHEMA_MIN_FIELDS 契约同源) ════════════════

def build_e2ea_projection(inp, validated_output, *, evidence_map=None,
                          proposals=(), gate_results=(), today_iso=None):
    """按 DESIGN §五(4) 9 行映射表产出任务侧投影(E2EA_FIELD_MAP 静态契约)。

    - task_id 透传 / task_ref 其余字段只读回显(echo)不回写;
    - history_append_lines: statement+confidence+limitations 随结论记录入档;
    - evidence_refs: 方向化挂载(direction 三值完整校验——G2 留 G3 的枚举
      完整性承接;quality_status/snapshot 绑定自输入与 G2 映射表透传);
    - falsifiable_conditions_merge: 可规格化子集(四键全+target 数值);
    - prediction_candidates: spec→pred_* 候选(落 allocation_views 侧沿既有
      门禁,本模块零写);
    - conclusions 子结构(登记型扩展,E2EA_CONCLUSIONS_KEY);
    - status_proposal: 状态推进=提案(经门禁,不直接改状态)。
    模式 B: 裁剪投影(无任务语义,§六;升级任务后承接模式 A 全义务)。"""
    sb = inp.get('snapshot_binding') or {}
    tref, qref = inp.get('task_ref'), inp.get('query_ref')
    hyps = (validated_output or {}).get('hypotheses') or []
    if inp.get('mode') == 'B':
        return {
            'origin_query_id': qref.get('query_id')
            if isinstance(qref, dict) else None,
            E2EA_CONCLUSIONS_KEY: [dict(g) for g in gate_results],
            'mode_b_note': ('模式B裁剪版(无任务语义,DESIGN §六): 查询历史'
                            'append-only,不触发状态回写;升级为研究任务'
                            '(promoted_to_task_id)后承接模式A全义务'),
        }
    facts_by_id = {f.get('fact_id'): f
                   for f in ((inp.get('evidence_pack') or {}).get('facts'))
                   or [] if isinstance(f, dict)}
    evidence_refs = []
    if evidence_map is not None:
        for row in evidence_map.get('rows') or []:
            d = row.get('direction')
            if d not in DIRECTIONS:      # 三值完整枚举校验(承接面)
                raise ValueError(f'evidence_ref.direction 非法(枚举{DIRECTIONS}):'
                                 f' {d!r}')
            evidence_refs.append(dict(row))
    else:
        for h in hyps:
            for label, d in (('supporting_evidence', 'support'),
                             ('counter_evidence', 'counter')):
                for ref in h.get(label) or []:
                    if not isinstance(ref, dict):
                        continue
                    fact = facts_by_id.get(ref.get('fact_id')) or {}
                    evidence_refs.append({
                        'hypothesis_id': h.get('hypothesis_id'),
                        'fact_id': ref.get('fact_id'),
                        'metric_id': ref.get('metric_id'),
                        'direction': d,
                        'quality_status': fact.get('quality_status'),
                        'snapshot_id': sb.get('snapshot_id'),
                        'snapshot_digest': sb.get('snapshot_digest')})
    history_lines = [
        f"[{h.get('hypothesis_id')}] {h.get('statement')} "
        f"(confidence={h.get('confidence')}; "
        f"limitations={' ; '.join(str(x) for x in h.get('limitations') or [])})"
        for h in hyps if isinstance(h, dict)]
    conds_merge, pred_candidates = [], []
    for h in hyps:
        for c in h.get('falsifiable_conditions') or []:
            spec = c.get('spec') if isinstance(c, dict) else None
            if not isinstance(spec, dict) or not _num(spec.get('target')):
                continue
            if not all(k in spec for k in ('metric', 'op', 'mode')):
                continue
            conds_merge.append({'hypothesis_id': h.get('hypothesis_id'),
                                'cond_text': c.get('cond_text'),
                                'spec': dict(spec)})
            pred_candidates.append({
                'source_hypothesis_id': h.get('hypothesis_id'),
                'pred_metric': spec.get('metric'),
                'pred_op': spec.get('op'),
                'pred_target': spec.get('target'),
                'pred_mode': spec.get('mode'),
                'window': spec.get('window'),
                'initial_status': PRED_INITIAL_STATUS})
    return {
        'task_id': tref.get('task_id') if isinstance(tref, dict) else None,
        'echo_fields': {k: (tref or {}).get(k) for k in
                        ('phenomenon', 'indicators', 'window', 'detection')},
        'history_append_lines': history_lines,
        'evidence_refs': evidence_refs,
        'falsifiable_conditions_merge': conds_merge,
        'prediction_candidates': pred_candidates,
        E2EA_CONCLUSIONS_KEY: [dict(g) for g in gate_results],
        'status_proposal': {
            'current_status_note': ('任务状态推进(' + '→'.join(rtm.STATUS_FLOW)
                                    + ')经门禁提案制: 本层证据装配完成=任务'
                                    'active 的组成部分;反驳条件触发→'
                                    'concluded/tracking 的提案(经门禁,'
                                    '不直接改状态)'),
            'proposals': [dict(p) for p in proposals]},
        'created': today_iso,
    }


if __name__ == '__main__':
    print(json.dumps(echo_params(), ensure_ascii=False, sort_keys=True))
