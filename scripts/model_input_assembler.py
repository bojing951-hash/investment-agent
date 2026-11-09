#!/usr/bin/env python3
"""模型研究结论层输入装配器(结论层输入唯一写者;v2.1 中性名,原 G1)

合同要点(历史设计档已移出公开仓;v2.1 Charter 5 S3: 模块更名
model_input_assembler,类 ModelResearchInput,删除"命名沿历史"豁免注):
产出 `ModelResearchInput`(模式 A 任务形态 / 模式 B 查询形态),九字段输入契约:
contract_version / mode / snapshot_binding / task_ref / query_ref / evidence_pack /
absent_registry / prior_knowledge / prompt_contract。

禁直读四机制(历史设计档 §三(a) 机制1-4):
1. 唯一写者+读取面封闭: 本模块零文件读取/零glob/零网络;唯一取数接入点=R1
   标准化层快照选择(接入点豁免标记单处落于 assemble,沿 E2E-A
   research_history_query 先例),只经手 research_snapshot_*.json 标准化产物,
   绝不接触原始采集档;
2. 披露与读取分离: evidence_pack.facts[].source_file 仅作披露字符串自快照事实
   source.file 逐字透传(规范basename),不构成任何读取通道;
3. 负向测试固化: 装配产物零原始档路径引用(除披露槽位)+ Gate A FAIL/None
   拒绝装配(tests/test_p03_w2_model_g1.py T2/T2b/T2c);
4. 数值零旁路: 装配器零算术,一切数值=快照事实逐位投影(T1b 断言字面量相等)。

缺席登记(历史设计档 §三(a) absent_registry;E2E-B 四级枚举): 数据不足不填0,
缺席如实进输入(classify_absence 四级: ABSENT_REGISTRY/ABSENT_SOURCE/
ABSENT_DATA/ABSENT_WINDOW)。

快照绑定核验(R5+R3 双层): snapshot_digest=R5 内容指纹(sha256前16位,canonical
JSON);入参 expected_snapshot_digest 携先验声明时重算比对,失配拒绝(疑篡改);
Gate A 经 R2 事实重算+R3 放行判定,FAIL/None/声明与重算矛盾一律拒绝装配
(沿 data_assembler 拒绝语义)。

零真实模型调用、零凭证、零付费、零网络出站(真实调用属调用层,
执行前置=用户批准凭证/费用,PENDING 未批)。import 面纯标准库+项目既有模块。
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import research_provenance as rp    # noqa: E402 (R1/R2/R3/R5 复用调用,禁复制分叉)
import research_task_manager as rtm  # noqa: E402 (E2E-A schema 契约复用导入)

# ══ 契约常量(DESIGN 明示值;登记=常量=echo 三方一致,REPORT §二.1) ════════
CONTRACT_VERSION = 'gri-1.0'                 # DESIGN L62(标识符)
MODE_ENUM = ('A', 'B')                       # DESIGN L63
ABSENT_LEVELS = ('ABSENT_REGISTRY', 'ABSENT_SOURCE', 'ABSENT_DATA',
                 'ABSENT_WINDOW')            # DESIGN L68 / E2E-B DESIGN L118-129
EVIDENCE_FACT_FIELDS = ('metric_id', 'fact_id', 'value', 'unit',
                        'observation_date', 'quality_status', 'derived',
                        'source_file')       # DESIGN L67 + L74 披露槽位
TASK_REF_FIELDS = ('task_id', 'phenomenon', 'indicators', 'window', 'detection',
                   'history_tail')           # DESIGN L65(与 E2E-A schema 一一对应)
QUERY_REF_FIELDS = ('query_id', 'question_text', 'as_of', 'metric_bindings_digest',
                    'derived_ops_digest')    # DESIGN L66(引用摘要,非数值载体)
MIN_COMPETING_HYPOTHESES = 2                 # DESIGN L70(合同级设计规则)
COUNTER_EVIDENCE_REQUIRED = True             # DESIGN L70
NUMERIC_GROUNDING_REQUIRED = True            # DESIGN L70
PROMPT_CONTRACT_KEYS = ('language', 'output_schema_version',
                        'counter_evidence_required', 'min_competing_hypotheses',
                        'numeric_grounding_required')   # DESIGN L70

# ══ 实现登记值(DESIGN 未定值,本包登记;运行后禁回改,REPORT §二.2) ════════
PROMPT_LANGUAGE_DEFAULT = 'zh'
OUTPUT_SCHEMA_VERSION_DEFAULT = 'hs-1.0'
HISTORY_TAIL_MAX = 5
REF_DIGEST_LEN = 16                          # 与 rp.digest_snapshot 同风格
_HEX16_RE = re.compile(r'^[0-9a-f]{16}$')
_ISO_DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


class AssemblyRefused(Exception):
    """装配拒绝(fail-closed): Gate A 不放行/快照绑定失配/上游契约破坏。
    拒绝即不产出正式输入——不部分产出、不静默降级(DESIGN §三(b) 径3 同语义)。"""


def echo_params():
    """登记参数 echo(R011 纪律: 登记=常量=echo 三方一致)。"""
    return {
        'contract_version': CONTRACT_VERSION,
        'mode_enum': list(MODE_ENUM),
        'absent_levels': list(ABSENT_LEVELS),
        'evidence_fact_fields': list(EVIDENCE_FACT_FIELDS),
        'task_ref_fields': list(TASK_REF_FIELDS),
        'query_ref_fields': list(QUERY_REF_FIELDS),
        'prompt_contract_keys': list(PROMPT_CONTRACT_KEYS),
        'min_competing_hypotheses': MIN_COMPETING_HYPOTHESES,
        'counter_evidence_required': COUNTER_EVIDENCE_REQUIRED,
        'numeric_grounding_required': NUMERIC_GROUNDING_REQUIRED,
        'prompt_language_default': PROMPT_LANGUAGE_DEFAULT,
        'output_schema_version_default': OUTPUT_SCHEMA_VERSION_DEFAULT,
        'history_tail_max': HISTORY_TAIL_MAX,
        'ref_digest_len': REF_DIGEST_LEN,
    }


# ══ 快照绑定与门禁(R5+R3,复用 research_provenance) ═════════════════════

def _gate_check(snapshot):
    """R2 复算+R3 放行: PASS/DEGRADED 放行;FAIL/None(声明与重算矛盾等)拒绝。"""
    status, reason = rp.gate_status(snapshot)   # 纯历史重验口径(不传 data_dir)
    if not rp.gate_allows_formal_research(status):
        raise AssemblyRefused(
            f"Gate A {status if status else '不可用(' + reason + ')'} — "
            f"拒绝装配正式 GLM 研究输入(FAIL/未知不得进入正式研究;"
            f"沿数据装配器拒绝语义)")
    return status


def _snapshot_binding(snapshot, expected_digest=None):
    """snapshot_binding 四键(DESIGN L64);R5 内容指纹+可选先验声明比对。"""
    sid = snapshot.get('snapshot_id')
    if not isinstance(sid, str) or not sid.strip():
        raise AssemblyRefused(f'快照缺snapshot_id(非有效权威快照): {sid!r}')
    as_of = snapshot.get('research_as_of')
    if not isinstance(as_of, str) or not as_of.strip():
        raise AssemblyRefused(f'快照缺research_as_of(研究截止不可核验): {as_of!r}')
    digest = rp.digest_snapshot(snapshot)      # R5 复用
    if expected_digest is not None and expected_digest != digest:
        raise AssemblyRefused(
            f'快照内容与声明摘要不一致(疑篡改/绑定漂移): 重算={digest} '
            f'声明={expected_digest}——拒绝装配(R5 内容级绑定核验)')
    return {'snapshot_id': sid, 'snapshot_digest': digest,
            'gate_a': None, 'research_as_of': as_of}   # gate_a 由调用方回填


def _facts_index(snapshot):
    """metric_id→事实 / fact_id→事实 双索引(重复指标已由 Gate 判FAIL先行拒绝)。"""
    by_mid, by_fid = {}, {}
    for f in snapshot.get('facts') or []:
        if isinstance(f, dict):
            by_mid.setdefault(f.get('metric_id'), f)
            by_fid.setdefault(f.get('fact_id'), f)
    return by_mid, by_fid


def _project_fact(fact):
    """快照事实 → evidence_pack.facts[] 投影(逐位透传,零算术;机制2/4)。"""
    out = {'metric_id': fact.get('metric_id'),
           'fact_id': fact.get('fact_id'),
           'value': fact.get('value'),
           'unit': fact.get('unit'),
           'observation_date': fact.get('observation_date'),
           'quality_status': fact.get('quality_status')}
    if 'derived' in fact:
        out['derived'] = fact.get('derived')
    src = fact.get('source')
    sf = src.get('file') if isinstance(src, dict) else None
    if isinstance(sf, str) and sf.strip():
        # 披露槽位(机制2): 仅接受规范basename(无路径成分);含路径=读取通道嫌疑→拒
        if '/' in sf or '\\' in sf or os.path.isabs(sf):
            raise AssemblyRefused(
                f'事实source.file含路径成分(非披露槽位合法形态,疑引入读取通道): {sf}')
        out['source_file'] = sf
    return out


# ══ 缺席分级(E2E-B 四级枚举;纯函数,零填0) ═════════════════════════════

def classify_absence(metric_id, snapshot, required_window=None):
    """缺席分级: 返回 None=事实在场非缺席;返回 (level, reason) 如实登记。

    四级(E2E-B DESIGN L118-129):
    - ABSENT_REGISTRY: 指标不在注册表(无身份定义);
    - ABSENT_SOURCE: 已注册但来源通道 MISSING/READ_FAIL(当日采集缺失);
    - ABSENT_DATA: 来源在场但快照facts无该metric_id事实;
    - ABSENT_WINDOW: 事实在场但所需派生窗口不可用(仅 required_window 给出时判)。
    通道映射复用 rp._SOURCE_TO_INPUT / rp._DERIVED_DEPS(复用调用,禁复制分叉)。"""
    actives = rp.active_registry_metrics()
    m = actives.get(metric_id)
    if m is None:
        return ('ABSENT_REGISTRY', f'指标不在注册表(无身份定义): {metric_id}')
    facts = {f.get('metric_id'): f for f in snapshot.get('facts') or []
             if isinstance(f, dict)}
    fact = facts.get(metric_id)
    if fact is None:
        if metric_id in rp._DERIVED_DEPS:
            return ('ABSENT_DATA', f'快照facts无该metric_id事实(派生指标): {metric_id}')
        ch = rp._SOURCE_TO_INPUT.get(m.get('source'))
        st = (snapshot.get('sources_status') or {}).get(ch) if ch else None
        status = st.get('status') if isinstance(st, dict) else None
        if status in ('MISSING', 'READ_FAIL'):
            return ('ABSENT_SOURCE',
                    f'指标已注册但当日采集缺失({ch}:{status})')
        return ('ABSENT_DATA', f'快照facts无该metric_id事实: {metric_id}')
    if required_window is not None:
        der = fact.get('derived') or {}
        win = der.get(required_window)
        if not isinstance(win, dict) or required_window not in der:
            return ('ABSENT_WINDOW',
                    f'派生窗口不可用: {required_window}'
                    f'({win.get("reason") if isinstance(win, dict) else "窗口缺席"})')
        if win.get('available') is False:
            return ('ABSENT_WINDOW',
                    f'派生窗口不可用: {required_window}({win.get("reason")})')
    return None


# ══ 模式 A: task_ref(E2E-A schema 契约,只读回显) ═══════════════════════

def _task_ref(task):
    """task_ref 六字段(DESIGN L65);E2E-A 最低字段集核验(复用 rtm.SCHEMA_MIN_FIELDS)。"""
    if not isinstance(task, dict):
        raise AssemblyRefused(f'任务档非对象: {type(task).__name__}')
    missing = [f for f in rtm.SCHEMA_MIN_FIELDS if f not in task]
    if missing:
        raise AssemblyRefused(
            f'任务档缺E2E-A schema最低字段(可增不可减契约): {missing}')
    indicators = task['indicators']
    if not isinstance(indicators, list) or not indicators \
            or not all(isinstance(x, str) and x.strip() for x in indicators):
        raise AssemblyRefused(f'task.indicators须非空字符串列表: {indicators!r}')
    window = task['window']
    if not isinstance(window, dict) or not _ISO_DATE_RE.fullmatch(str(window.get('start') or '')) \
            or not _ISO_DATE_RE.fullmatch(str(window.get('end') or '')):
        raise AssemblyRefused(f'task.window须含ISO日期start/end: {window!r}')
    detection = task['detection']
    if not isinstance(detection, dict) or not detection:
        raise AssemblyRefused(f'task.detection须非空对象: {detection!r}')
    history = task['history']
    if not isinstance(history, list):
        raise AssemblyRefused(f'task.history须列表(追加式): {history!r}')
    return {'task_id': task['task_id'],
            'phenomenon': task['phenomenon'],
            'indicators': list(indicators),
            'window': {'start': window['start'], 'end': window['end']},
            'detection': detection,
            'history_tail': list(history[-HISTORY_TAIL_MAX:])}


# ══ 模式 B: query_ref(E2E-B IR 契约,引用摘要非数值载体) ════════════════

def _digest_ref(obj):
    """引用摘要 digest(sha256前REF_DIGEST_LEN位,canonical JSON;R5同风格)。"""
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode('utf-8')).hexdigest()[:REF_DIGEST_LEN]


def _query_ref(query, snapshot):
    """query_ref 五字段(DESIGN L66)+绑定接地核验(fail-closed,REPORT §二.3)。"""
    for k in ('query_id', 'question_text'):
        if not isinstance(query.get(k), str) or not query[k].strip():
            raise AssemblyRefused(f'查询IR缺{k}(E2E-B StructuredResearchQuery契约)')
    bindings = query.get('metric_bindings')
    if not isinstance(bindings, list):
        raise AssemblyRefused(f'查询IR metric_bindings须列表: {bindings!r}')
    ops = query.get('derived_operations')
    if ops is None:
        ops = []
    if not isinstance(ops, list):
        raise AssemblyRefused(f'查询IR derived_operations须列表: {ops!r}')
    tgt = query.get('target_snapshot_id')
    if tgt is not None and tgt != snapshot.get('snapshot_id'):
        raise AssemblyRefused(
            f'查询IR绑定快照失配: target_snapshot_id={tgt!r} '
            f'≠ 权威快照={snapshot.get("snapshot_id")!r}(须以当日权威快照装配)')
    return {'query_id': query['query_id'],
            'question_text': query['question_text'],
            'as_of': query.get('as_of'),
            'metric_bindings_digest': _digest_ref(bindings),
            'derived_ops_digest': _digest_ref(ops)}


# ══ 注入面(prior_knowledge / 评分卡·相关性·新闻引用;缺省=显式缺席) ═════

def _ref_or_missing(value, label):
    if value is None:
        return {'status': 'MISSING',
                'reason': f'{label}未提供(装配期如实登记缺席)'}
    return value


def _prior_knowledge(pk):
    if pk is None:
        return {'theses_block': None, 'views_block': None, 'prior_conclusions': []}
    if not isinstance(pk, dict):
        raise AssemblyRefused(f'prior_knowledge须对象: {pk!r}')
    return {'theses_block': pk.get('theses_block'),
            'views_block': pk.get('views_block'),
            'prior_conclusions': list(pk.get('prior_conclusions') or [])}


def _prompt_contract(language=None, output_schema_version=None):
    return {'language': language or PROMPT_LANGUAGE_DEFAULT,
            'output_schema_version': output_schema_version or
            OUTPUT_SCHEMA_VERSION_DEFAULT,
            'counter_evidence_required': COUNTER_EVIDENCE_REQUIRED,
            'min_competing_hypotheses': MIN_COMPETING_HYPOTHESES,
            'numeric_grounding_required': NUMERIC_GROUNDING_REQUIRED}


# ══ 输入契约字段级校验(要点①;装配末步自检+测试直调) ═══════════════════

def validate_input(inp):
    """ModelResearchInput 九字段字段级校验;返回问题列表(空=过)。

    必备字段缺席/类型不符/枚举越界/常量漂移(prompt_contract 三合同级值)均为
    问题;额外字段 tolerated(前向兼容,E2E-A「可增不可减」同款语义)。"""
    probs = []
    if not isinstance(inp, dict):
        return [f'输入非对象: {type(inp).__name__}']
    cv = inp.get('contract_version')
    if not isinstance(cv, str) or not cv.strip():
        probs.append(f'contract_version缺失/非法: {cv!r}')
    if inp.get('mode') not in MODE_ENUM:
        probs.append(f'mode非法: {inp.get("mode")!r}(合法{MODE_ENUM})')
    sb = inp.get('snapshot_binding')
    if not isinstance(sb, dict):
        probs.append(f'snapshot_binding缺失/非对象: {sb!r}')
    else:
        if not isinstance(sb.get('snapshot_id'), str) or not sb['snapshot_id'].strip():
            probs.append(f'snapshot_binding.snapshot_id缺失/非法: {sb.get("snapshot_id")!r}')
        if not isinstance(sb.get('snapshot_digest'), str) \
                or not _HEX16_RE.fullmatch(sb['snapshot_digest']):
            probs.append(f'snapshot_binding.snapshot_digest非法(须16位hex): '
                         f'{sb.get("snapshot_digest")!r}')
        if sb.get('gate_a') not in ('PASS', 'DEGRADED'):
            probs.append(f'snapshot_binding.gate_a非法: {sb.get("gate_a")!r}'
                         '(装配产物只容放行态)')
        if not isinstance(sb.get('research_as_of'), str) or not sb['research_as_of'].strip():
            probs.append(f'snapshot_binding.research_as_of缺失/非法: '
                         f'{sb.get("research_as_of")!r}')
    mode = inp.get('mode')
    tref, qref = inp.get('task_ref'), inp.get('query_ref')
    if mode == 'A':
        if not isinstance(tref, dict):
            probs.append(f'mode A 须task_ref对象: {tref!r}')
        elif qref is not None:
            probs.append('mode A 须query_ref=null')
        else:
            for k in ('task_id', 'phenomenon'):
                if not isinstance(tref.get(k), str) or not tref[k].strip():
                    probs.append(f'task_ref.{k}缺失/非法: {tref.get(k)!r}')
            inds = tref.get('indicators')
            if not isinstance(inds, list) or not inds \
                    or not all(isinstance(x, str) for x in inds):
                probs.append(f'task_ref.indicators须非空字符串列表: {inds!r}')
            win = tref.get('window')
            if not isinstance(win, dict) or not isinstance(win.get('start'), str) \
                    or not isinstance(win.get('end'), str):
                probs.append(f'task_ref.window须含start/end字符串: {win!r}')
            if not isinstance(tref.get('detection'), dict):
                probs.append(f'task_ref.detection须对象: {tref.get("detection")!r}')
            if not isinstance(tref.get('history_tail'), list):
                probs.append(f'task_ref.history_tail须列表: {tref.get("history_tail")!r}')
    elif mode == 'B':
        if not isinstance(qref, dict):
            probs.append(f'mode B 须query_ref对象: {qref!r}')
        elif tref is not None:
            probs.append('mode B 须task_ref=null')
        else:
            for k in ('query_id', 'question_text'):
                if not isinstance(qref.get(k), str) or not qref[k].strip():
                    probs.append(f'query_ref.{k}缺失/非法: {qref.get(k)!r}')
            if not isinstance(qref.get('as_of'), (str, type(None))):
                probs.append(f'query_ref.as_of须字符串或null: {qref.get("as_of")!r}')
            for k in ('metric_bindings_digest', 'derived_ops_digest'):
                if not isinstance(qref.get(k), str) \
                        or not _HEX16_RE.fullmatch(qref[k]):
                    probs.append(f'query_ref.{k}非法(须16位hex): {qref.get(k)!r}')
    ep = inp.get('evidence_pack')
    if not isinstance(ep, dict):
        probs.append(f'evidence_pack缺失/非对象: {ep!r}')
    else:
        facts = ep.get('facts')
        if not isinstance(facts, list):
            probs.append(f'evidence_pack.facts须列表: {facts!r}')
        else:
            for i, f in enumerate(facts):
                if not isinstance(f, dict):
                    probs.append(f'facts[{i}]非对象: {f!r}')
                    continue
                for k in ('metric_id', 'fact_id', 'unit', 'observation_date',
                          'quality_status'):
                    if not isinstance(f.get(k), str) or not f[k].strip():
                        probs.append(f'facts[{i}].{k}缺失/非法: {f.get(k)!r}')
                v = f.get('value')
                if isinstance(v, bool) or not isinstance(v, (int, float)):
                    probs.append(f'facts[{i}].value须数值: {v!r}')
                if 'derived' in f and not isinstance(f['derived'], dict):
                    probs.append(f'facts[{i}].derived须对象: {f.get("derived")!r}')
                sf = f.get('source_file')
                if sf is not None and (not isinstance(sf, str)
                                       or '/' in sf or '\\' in sf):
                    probs.append(f'facts[{i}].source_file非法(披露槽位须规范'
                                 f'basename无路径成分): {sf!r}')
        for k in ('scorecard_summary', 'correlation_ref', 'news_index_ref'):
            ref = ep.get(k)
            if ref is None:
                probs.append(f'evidence_pack.{k}缺席(缺省须显式MISSING状态,不得隐藏)')
            elif not isinstance(ref, (dict, str)):
                probs.append(f'evidence_pack.{k}须对象或状态字符串: {ref!r}')
    ar = inp.get('absent_registry')
    if not isinstance(ar, list):
        probs.append(f'absent_registry须列表: {ar!r}')
    else:
        for i, a in enumerate(ar):
            if not isinstance(a, dict) or a.get('level') not in ABSENT_LEVELS \
                    or not isinstance(a.get('metric_id'), str) \
                    or not isinstance(a.get('reason'), str) or not a['reason'].strip():
                probs.append(f'absent_registry[{i}]非法(须metric_id/level∈四级枚举/'
                             f'reason非空): {a!r}')
    pk = inp.get('prior_knowledge')
    if not isinstance(pk, dict):
        probs.append(f'prior_knowledge须对象: {pk!r}')
    else:
        if not isinstance(pk.get('theses_block'), (str, type(None))):
            probs.append(f'prior_knowledge.theses_block须字符串或null: '
                         f'{pk.get("theses_block")!r}')
        if not isinstance(pk.get('views_block'), (str, type(None))):
            probs.append(f'prior_knowledge.views_block须字符串或null: '
                         f'{pk.get("views_block")!r}')
        if not isinstance(pk.get('prior_conclusions'), list):
            probs.append(f'prior_knowledge.prior_conclusions须列表: '
                         f'{pk.get("prior_conclusions")!r}')
    pc = inp.get('prompt_contract')
    if not isinstance(pc, dict):
        probs.append(f'prompt_contract须对象: {pc!r}')
    else:
        for k in ('language', 'output_schema_version'):
            if not isinstance(pc.get(k), str) or not pc[k].strip():
                probs.append(f'prompt_contract.{k}缺失/非法: {pc.get(k)!r}')
        if pc.get('counter_evidence_required') is not True:
            probs.append(f'prompt_contract.counter_evidence_required须True(合同级): '
                         f'{pc.get("counter_evidence_required")!r}')
        if pc.get('min_competing_hypotheses') != MIN_COMPETING_HYPOTHESES:
            probs.append(f'prompt_contract.min_competing_hypotheses须='
                         f'{MIN_COMPETING_HYPOTHESES}(合同级): '
                         f'{pc.get("min_competing_hypotheses")!r}')
        if pc.get('numeric_grounding_required') is not True:
            probs.append(f'prompt_contract.numeric_grounding_required须True(合同级): '
                         f'{pc.get("numeric_grounding_required")!r}')
    return probs


# ══ 装配主入口(模式 A / 模式 B / R1 壳) ═════════════════════════════════

def assemble_mode_a(snapshot, task, *, expected_snapshot_digest=None,
                    prior_knowledge=None, scorecard_summary=None,
                    correlation_ref=None, news_index_ref=None,
                    language=None, output_schema_version=None):
    """模式 A 装配: task_ref 在场+指标事实投影+缺席登记(DESIGN §三(a)/§六)。"""
    gate = _gate_check(snapshot)
    binding = _snapshot_binding(snapshot, expected_snapshot_digest)
    binding['gate_a'] = gate
    tref = _task_ref(task)
    by_mid, _ = _facts_index(snapshot)
    facts, absent = [], []
    for mid in tref['indicators']:
        verdict = classify_absence(mid, snapshot)
        if verdict is None:
            facts.append(_project_fact(by_mid[mid]))
        else:
            absent.append({'metric_id': mid, 'level': verdict[0],
                           'reason': verdict[1]})
    inp = {
        'contract_version': CONTRACT_VERSION,
        'mode': 'A',
        'snapshot_binding': binding,
        'task_ref': tref,
        'query_ref': None,
        'evidence_pack': {
            'facts': facts,
            'scorecard_summary': _ref_or_missing(scorecard_summary,
                                                 'scorecard_summary'),
            'correlation_ref': _ref_or_missing(correlation_ref, 'correlation_ref'),
            'news_index_ref': _ref_or_missing(news_index_ref, 'news_index_ref'),
        },
        'absent_registry': absent,
        'prior_knowledge': _prior_knowledge(prior_knowledge),
        'prompt_contract': _prompt_contract(language, output_schema_version),
    }
    probs = validate_input(inp)
    if probs:
        raise AssemblyRefused('装配产物未过输入契约校验: ' + '; '.join(probs))
    return inp


def assemble_mode_b(snapshot, query, *, expected_snapshot_digest=None,
                    prior_knowledge=None, scorecard_summary=None,
                    correlation_ref=None, news_index_ref=None,
                    language=None, output_schema_version=None):
    """模式 B 装配: query_ref 引用摘要+RESOLVED绑定接地投影+缺席透传(§六)。

    E2E-B WP-B1/B2 未落地时: query=None → 拒绝(无查询上下文,不产空壳,
    REPORT §二.3 登记);绑定级缺席按四级枚举如实透传。"""
    if query is None:
        raise AssemblyRefused(
            '模式B查询IR缺席(E2E-B WP-B1未落地): 无查询上下文拒绝装配——'
            '缺席登记路径=绑定级缺席透传,查询级无上下文即拒绝(登记决策)')
    if not isinstance(query, dict):
        raise AssemblyRefused(f'查询IR非对象: {type(query).__name__}')
    gate = _gate_check(snapshot)
    binding = _snapshot_binding(snapshot, expected_snapshot_digest)
    binding['gate_a'] = gate
    qref = _query_ref(query, snapshot)
    _, by_fid = _facts_index(snapshot)
    facts, absent = [], []
    for b in query['metric_bindings']:
        if not isinstance(b, dict):
            raise AssemblyRefused(f'metric_binding非对象: {b!r}')
        mid, st = b.get('metric_id'), b.get('status')
        if st == 'RESOLVED':
            prov = b.get('provenance') or {}
            fid = prov.get('fact_id')
            fact = by_fid.get(fid)
            if fact is None:
                raise AssemblyRefused(
                    f'RESOLVED绑定接地失败: fact_id={fid!r}不在权威快照'
                    '(fail-closed,无源数值不得进入输入)')
            if prov.get('snapshot_id') != snapshot.get('snapshot_id'):
                raise AssemblyRefused(
                    f'RESOLVED绑定快照失配: provenance.snapshot_id='
                    f'{prov.get("snapshot_id")!r}≠权威快照'
                    f'={snapshot.get("snapshot_id")!r}')
            if fact.get('metric_id') != mid:
                raise AssemblyRefused(
                    f'RESOLVED绑定指标与事实身份不符: binding={mid!r} '
                    f'fact={fact.get("metric_id")!r}')
            facts.append(_project_fact(fact))
        elif st in ABSENT_LEVELS:
            absent.append({'metric_id': mid, 'level': st,
                           'reason': b.get('absence_reason')
                           or f'E2E-B执行器产物缺席(原样登记:{st})'})
        else:
            raise AssemblyRefused(
                f'绑定status非法: {st!r}(合法RESOLVED|{"|".join(ABSENT_LEVELS)})')
    inp = {
        'contract_version': CONTRACT_VERSION,
        'mode': 'B',
        'snapshot_binding': binding,
        'task_ref': None,
        'query_ref': qref,
        'evidence_pack': {
            'facts': facts,
            'scorecard_summary': _ref_or_missing(scorecard_summary,
                                                 'scorecard_summary'),
            'correlation_ref': _ref_or_missing(correlation_ref, 'correlation_ref'),
            'news_index_ref': _ref_or_missing(news_index_ref, 'news_index_ref'),
        },
        'absent_registry': absent,
        'prior_knowledge': _prior_knowledge(prior_knowledge),
        'prompt_contract': _prompt_contract(language, output_schema_version),
    }
    probs = validate_input(inp)
    if probs:
        raise AssemblyRefused('装配产物未过输入契约校验: ' + '; '.join(probs))
    return inp


def assemble(ymd, snapshot_dir, mode='A', task=None, query=None, **kwargs):
    """R1 壳入口: 确定性选择当日权威快照(标准化层)后进入模式装配。

    ACCESS_POINT_EXEMPT: rp.select_snapshot=R1标准化层接入点(唯一取数通道,
    仅经手research_snapshot_*.json,绝不接触原始采集档;沿E2E-A接入点豁免先例)。"""
    snap, path_or_reason = rp.select_snapshot(str(ymd), str(snapshot_dir))
    if snap is None:
        raise AssemblyRefused(f'当日权威快照不可用(R1): {path_or_reason}')
    if mode == 'A':
        return assemble_mode_a(snap, task, **kwargs)
    if mode == 'B':
        return assemble_mode_b(snap, query, **kwargs)
    raise AssemblyRefused(f'mode非法: {mode!r}(合法{MODE_ENUM})')


if __name__ == '__main__':
    print(json.dumps(echo_params(), ensure_ascii=False, sort_keys=True))
