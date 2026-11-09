#!/usr/bin/env python3
"""模型研究结论层结构化输出契约与校验器(输出侧确定性结构;v2.1 中性名,原 G2)

v2.1(Charter 5 S3, 2026-11-09): 模块更名 model_output_validator,删除
"命名沿历史"豁免注;合同要点(历史设计档已移出公开仓):
- 输出 schema: HypothesisSet(模式 A 七字段全量)/模式 B 裁剪三字段;
- 校验器: 证据引用在场核验+数值接地(证据包/三合法来源)+竞争性区分性判据
  +反方证据强制(空即拒)+缺席承接(absent_ack/limitations 四义务)
  +阈值取值约束(编造 target 拒绝);
- 假设-证据映射表构建(§四(2),装配期由校验器构建,入研究档案);
- 失败三径状态机(§三(b): 径1重试→径2降级→径3缺席登记)。

零真实模型调用、零凭证、零付费、零网络出站(设计对象≠设计手段;
DESIGN L224「不含真实调用(以确定性样例驱动)」;真实调用属 WP-G4,执行前置=
用户批准凭证/费用 PENDING 未批)。调用面以确定性样例驱动:
run_conclusion_pipeline 的 attempts 参数=注入的尝试产物序列
(桩注入点,登记 REPORT §二.3),禁任何真实出站。
import 面纯标准库+项目既有模块(model_input_assembler/research_provenance
复用调用,禁复制分叉)。
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import research_provenance as rp        # noqa: E402 (注册表访问复用,禁复制分叉)
import model_input_assembler as mia       # noqa: E402 (G1 输入契约复用,禁复制分叉)

# ══ 契约常量(DESIGN 明示值/G1 登记值沿用;登记=常量=echo 三方一致,REPORT §二.1) ══
OUTPUT_SCHEMA_VERSION = 'hs-1.0'        # G1 登记(model_input_assembler.py:64)沿用
HYPOTHESIS_FIELDS = ('hypothesis_id', 'statement', 'supporting_evidence',
                     'counter_evidence', 'falsifiable_conditions',
                     'confidence', 'limitations')   # DESIGN L95-103 七字段
TOP_LEVEL_FIELDS = ('hypotheses', 'phenomenon_echo', 'absent_ack')  # L107-115
MODE_B_FIELDS = ('phenomenon_echo', 'explanation', 'absent_ack')    # §六 L199
EVIDENCE_REF_FIELDS = ('fact_id', 'metric_id', 'direction_note')    # L99/L100
CONDITION_FIELDS = ('cond_text', 'spec')                            # L101
SPEC_FIELDS = ('metric', 'op', 'target', 'mode', 'window')          # L111/L158
SPEC_REQUIRED_FIELDS = ('metric', 'op', 'target', 'mode')   # window 缺省=task 窗
SPEC_OPS = ('>', '>=', '<', '<=')          # report_generator.py:526 比较符族
SPEC_MODES = ('touch', 'expiry')           # report_generator.py:526/allocation L77
CONFIDENCE_ENUM = ('high', 'medium', 'low')        # DESIGN L102
DIRECTIONS = ('support', 'counter', 'neutral')    # §四(2) L139(G2 仅发前两类)
NON_SPECIFIABLE_MARKER = '不可程序裁决'            # DESIGN L161
TRANSIENT_ERROR_KINDS = ('network', 'risk_control', 'stream_interrupted')  # L85
COST_BREAKER_KIND = 'cost_breaker'                 # L87 费用熔断
OUTCOME_ACCEPTED = 'ACCEPTED'
OUTCOME_ACCEPTED_DOWNGRADED = 'ACCEPTED_DOWNGRADED'
OUTCOME_ABSENT_REGISTERED = 'ABSENT_REGISTERED'

# ══ 实现登记值(DESIGN 未定值,本包登记;运行后禁回改,REPORT §二.2) ═════════
MAX_RETRIES = 3                    # DESIGN L85 候选基线=周报链实值(rg:553)
BACKOFF_LINEAR_BASE = 1.0          # 线性退避计划表(记录不实际休眠,登记 §二.2)
DEGRADED_ACK_MARKERS = ('DEGRADED', '降级')        # 径2 义务承接标记
REGISTRY_THRESHOLD_KEYS = ('range', 'max_week_pct_move')  # L157(ii) 点名字段族
_DERIVED_VALUE_KEYS = ('value', 'pct_change', 'pp_change', 'bp_change',
                       'abs_change', 'basis_value')        # L157(i) 窗口值族
_HY_ID_RE = re.compile(r'^HY-\d{8}-\d{3}$')               # DESIGN L97
_ID_FAMILY_RE = re.compile(r'(?:HY|RT|QB)-\d{8}-\d{3}')   # 标识符豁免族
_FACT_ID_RE = re.compile(r'[A-Za-z0-9_]+@\d{4}-\d{2}-\d{2}')
_ISO_DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')
_COMPACT_DATE_RE = re.compile(r'(?<![A-Za-z0-9_])\d{8}(?![A-Za-z0-9_])')
_YEAR_CN_RE = re.compile(r'(?:19|20)\d{2}年')
_MONTH_CN_RE = re.compile(r'(?<![A-Za-z0-9_])(?:[1-9]|1[0-2])月')
_NUM_TOKEN_RE = re.compile(
    r'(?<![A-Za-z0-9_@])([-+]?\d[\d,]*(?:\.\d+)?)(?:bps|bp|pp|%)?'
    r'(?![A-Za-z0-9_@])')


class InvalidResearchInput(Exception):
    """入参非有效 ModelResearchInput(G1 契约): 管线入口 fail-closed 拒绝。"""


class InvalidOutput(Exception):
    """构建假设-证据映射表时输出未过校验(fail-closed,不产映射)。"""


def echo_params():
    """登记参数 echo(R011 纪律: 登记=常量=echo 三方一致)。"""
    return {
        'output_schema_version': OUTPUT_SCHEMA_VERSION,
        'hypothesis_fields': list(HYPOTHESIS_FIELDS),
        'top_level_fields': list(TOP_LEVEL_FIELDS),
        'mode_b_fields': list(MODE_B_FIELDS),
        'evidence_ref_fields': list(EVIDENCE_REF_FIELDS),
        'condition_fields': list(CONDITION_FIELDS),
        'spec_fields': list(SPEC_FIELDS),
        'spec_required_fields': list(SPEC_REQUIRED_FIELDS),
        'spec_ops': list(SPEC_OPS),
        'spec_modes': list(SPEC_MODES),
        'confidence_enum': list(CONFIDENCE_ENUM),
        'directions': list(DIRECTIONS),
        'non_specifiable_marker': NON_SPECIFIABLE_MARKER,
        'degraded_ack_markers': list(DEGRADED_ACK_MARKERS),
        'transient_error_kinds': list(TRANSIENT_ERROR_KINDS),
        'cost_breaker_kind': COST_BREAKER_KIND,
        'registry_threshold_keys': list(REGISTRY_THRESHOLD_KEYS),
        'derived_value_keys': list(_DERIVED_VALUE_KEYS),
        'max_retries': MAX_RETRIES,
        'backoff_linear_base': BACKOFF_LINEAR_BASE,
        'outcome_accepted': OUTCOME_ACCEPTED,
        'outcome_accepted_downgraded': OUTCOME_ACCEPTED_DOWNGRADED,
        'outcome_absent_registered': OUTCOME_ABSENT_REGISTERED,
    }


# ══ 解析面(DESIGN L82: 容忍围栏/注释包裹,不容忍字段缺失→校验三径) ════════

def parse_hypothesis_set(text):
    """围栏/注释剥壳→单一 JSON 对象;返回 (obj, None) 或 (None, 错误说明)。"""
    if not isinstance(text, str) or not text.strip():
        return None, f'响应为空/非字符串: {type(text).__name__}'
    t = text.strip()
    m = re.search(r'```(?:json)?\s*(.+?)\s*```', t, re.S)
    if m:
        t = m.group(1).strip()
    if t.startswith('<!--') and t.endswith('-->'):
        t = t[4:-3].strip()
    try:
        obj = json.loads(t)
    except json.JSONDecodeError as exc:
        return None, f'JSON解析失败: {exc}'
    if not isinstance(obj, dict):
        return None, f'顶层须单一JSON对象: {type(obj).__name__}'
    return obj, None


# ══ 数值接地(§四(1)之5/L99/L130/L157;登记规则族 REPORT §二.2/§二.3) ═══════

def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def extract_numeric_tokens(text):
    """自由文本数值抽取(标识符/日历类豁免+单位后缀消费;登记 REPORT §二.2)。"""
    if not isinstance(text, str):
        return []
    t = text.replace('−', '-')
    for rx in (_ID_FAMILY_RE, _FACT_ID_RE, _ISO_DATE_RE, _COMPACT_DATE_RE,
               _YEAR_CN_RE, _MONTH_CN_RE):
        t = rx.sub(' ', t)
    out = []
    for m in _NUM_TOKEN_RE.finditer(t):
        s = m.group(1).replace(',', '')
        try:
            out.append(float(s))
        except ValueError:       # pragma: no cover(正则已保证可析)
            continue
    return out


def collect_evidence_numbers(inp):
    """合法来源(i): 输入证据包在场数值(fact.value+derived 窗口值;DESIGN L157)。"""
    nums = set()
    for f in ((inp.get('evidence_pack') or {}).get('facts')) or []:
        if not isinstance(f, dict):
            continue
        if _num(f.get('value')):
            nums.add(f['value'])
        for wrec in (f.get('derived') or {}).values():
            if isinstance(wrec, dict):
                for k in _DERIVED_VALUE_KEYS:
                    if _num(wrec.get(k)):
                        nums.add(wrec[k])
    return nums


def registry_legal_targets():
    """合法来源(ii): 注册表既有校验阈值(rp.active_registry_metrics 复用调用)。"""
    nums = set()
    for m in rp.active_registry_metrics().values():
        val = m.get('validation') or {}
        rng = val.get('range')
        if isinstance(rng, (list, tuple)):
            for v in list(rng)[:2]:
                if _num(v):
                    nums.add(v)
        mw = val.get('max_week_pct_move')
        if _num(mw):
            nums.add(mw)
    return nums


def legal_target_numbers(inp, *, registry_targets=None,
                         prior_trigger_targets=None):
    """三合法来源并集(§五(1)之2): (i)证据包在场数值+(ii)注册表阈值+(iii)先验触发器阈值.

    registry_targets/prior_trigger_targets=注入面(登记 REPORT §二.3):
    缺省 (ii) 经 rp 实取注册表;(iii) 由编排层(G3/G4)传结构化触发值;
    测试一律注入合成集(确定性,R014-D3 漂移防护)。三个来源之外=编造,校验拒绝。"""
    nums = collect_evidence_numbers(inp)
    nums |= registry_legal_targets() if registry_targets is None \
        else {t for t in registry_targets if _num(t)}
    if prior_trigger_targets:
        nums |= {t for t in prior_trigger_targets if _num(t)}
    return nums


# ══ 输出契约校验(§三(c)+§四+§五(1)+§六;闭合 schema,报告问题列表) ═════════

def _validate_common(inp, out, probs):
    """模式共用: 输入形态/echo 复述/absent_ack 逐项复述/数值集准备。"""
    if not isinstance(inp, dict) or inp.get('mode') not in mia.MODE_ENUM:
        probs.append(f'输入非法(非ModelResearchInput形态): '
                     f'mode={inp.get("mode") if isinstance(inp, dict) else type(inp).__name__}')
        return None
    return inp['mode']


def _validate_echo_and_ack(inp, out, probs, echo_key, source_text, source_label):
    echo = out.get(echo_key)
    if not isinstance(echo, str) or not echo.strip():
        probs.append(f'{echo_key}缺失/非空校验失败(现象复述,防答非所问): {echo!r}')
    elif isinstance(source_text, str) and source_text.strip() \
            and source_text not in echo:
        probs.append(f'{echo_key}未复述{source_label}原文(防答非所问)')
    ack = out.get('absent_ack')
    absent_ids = [a.get('metric_id') for a in inp.get('absent_registry') or []
                  if isinstance(a, dict)]
    if not isinstance(ack, list):
        probs.append(f'absent_ack须列表: {ack!r}')
    else:
        if not absent_ids and ack:
            probs.append('absent_registry为空而absent_ack非空(逐项复述=空进空出)')
        blob = ' | '.join(str(x) for x in ack)
        for mid in absent_ids:
            if mid not in blob:
                probs.append(f'absent_ack未逐项复述缺席指标(缺席未承接): {mid}')
    return absent_ids


def validate_output(inp, out, *, registry_targets=None,
                    prior_trigger_targets=None):
    """HypothesisSet(模式A)/裁剪版(模式B) 输出契约校验;返回问题列表(空=过)。

    inp=ModelResearchInput(G1 契约产物;九字段级校验由管线入口 mia.validate_input
    承担,本函数不重复);out=解析后的输出对象。分层接地/闭合 schema/竞争性
    区分性/反方证据强制/缺席承接/阈值三来源——逐项登记 REPORT §二.3。"""
    probs = []
    mode = _validate_common(inp, out, probs)
    if mode is None:
        return probs
    if not isinstance(out, dict):
        probs.append(f'输出非单一JSON对象: {type(out).__name__}')
        return probs
    facts_by_id, facts_by_mid = {}, {}
    for f in ((inp.get('evidence_pack') or {}).get('facts')) or []:
        if isinstance(f, dict):
            facts_by_id[f.get('fact_id')] = f
            facts_by_mid[f.get('metric_id')] = f
    ev_nums = collect_evidence_numbers(inp)
    legal = legal_target_numbers(inp, registry_targets=registry_targets,
                                 prior_trigger_targets=prior_trigger_targets)
    gate_a = (inp.get('snapshot_binding') or {}).get('gate_a')

    if mode == 'A':
        _validate_mode_a(inp, out, probs, facts_by_id, facts_by_mid,
                         ev_nums, legal, gate_a)
    else:
        _validate_mode_b(inp, out, probs, ev_nums)
    return probs


def _validate_mode_a(inp, out, probs, facts_by_id, facts_by_mid,
                     ev_nums, legal, gate_a):
    missing_top = set(TOP_LEVEL_FIELDS) - set(out)
    extra_top = set(out) - set(TOP_LEVEL_FIELDS)
    if missing_top:
        probs.append(f'顶层缺必备字段: {sorted(missing_top)}')
    if extra_top:
        probs.append(f'顶层含schema外字段(闭合schema防数值旁路): {sorted(extra_top)}')
    absent_ids = _validate_echo_and_ack(
        inp, out, probs, 'phenomenon_echo',
        (inp.get('task_ref') or {}).get('phenomenon'), '任务现象')

    hyps = out.get('hypotheses')
    if not isinstance(hyps, list) or not hyps:
        probs.append(f'hypotheses须非空列表: {hyps!r}')
        return
    min_comp = (inp.get('prompt_contract') or {}).get(
        'min_competing_hypotheses') or mia.MIN_COMPETING_HYPOTHESES
    if len(hyps) < min_comp:
        probs.append(f'竞争假设数不足: {len(hyps)}<{min_comp}(§四竞争性强制)')

    ids = [h.get('hypothesis_id') for h in hyps if isinstance(h, dict)]
    if len(ids) != len(set(ids)):
        probs.append(f'hypothesis_id集内重复: '
                     f'{sorted({x for x in ids if ids.count(x) > 1})}')
    dates = {x.split('-')[1] for x in ids
             if isinstance(x, str) and x.startswith('HY-')}
    if len(dates) > 1:
        probs.append(f'hypothesis_id须同日序列(同日独立计数): {sorted(dates)}')

    spec_conds = []          # (hyp_id, spec四元组)——区分性判据池
    for i, h in enumerate(hyps):
        tag = f'hypotheses[{i}]'
        if not isinstance(h, dict):
            probs.append(f'{tag}非对象')
            continue
        hid = h.get('hypothesis_id')
        missing_h = set(HYPOTHESIS_FIELDS) - set(h)
        extra_h = set(h) - set(HYPOTHESIS_FIELDS)
        if missing_h:
            probs.append(f'{tag}缺七字段: {sorted(missing_h)}')
        if extra_h:
            probs.append(f'{tag}含schema外字段: {sorted(extra_h)}')
        if not _HY_ID_RE.fullmatch(str(hid or '')):
            probs.append(f'{tag}.hypothesis_id格式非法(HY-YYYYMMDD-NNN): {hid!r}')

        stmt = h.get('statement')
        if not isinstance(stmt, str) or not stmt.strip():
            probs.append(f'{tag}.statement缺失/非空校验失败')
        elif any(n not in ev_nums for n in extract_numeric_tokens(stmt)):
            bad = [n for n in extract_numeric_tokens(stmt) if n not in ev_nums]
            probs.append(f'{tag}.statement数值不在输入证据包(接地失败): {bad}')

        conf = h.get('confidence')
        if conf not in CONFIDENCE_ENUM:
            probs.append(f'{tag}.confidence非法(三档枚举high/medium/low): {conf!r}')

        sup, cnt = h.get('supporting_evidence'), h.get('counter_evidence')
        if not isinstance(sup, list):
            probs.append(f'{tag}.supporting_evidence须列表: {sup!r}')
        if not isinstance(cnt, list):
            probs.append(f'{tag}.counter_evidence须列表: {cnt!r}')
        if isinstance(cnt, list) and not cnt:
            probs.append(f'{tag}.counter_evidence为空'
                         '(§四(3)机制一: 不存在无反方证据的合法输出)')
        if isinstance(sup, list) and not sup and conf != 'low':
            probs.append(f'{tag}.supporting_evidence为空仅容confidence=low(证据单侧)')

        notes, cond_texts, non_spec = [], [], []
        n_spec = 0
        for label in ('supporting_evidence', 'counter_evidence'):
            lst = h.get(label)
            if not isinstance(lst, list):
                continue
            for j, ref in enumerate(lst):
                rtag = f'{tag}.{label}[{j}]'
                if not isinstance(ref, dict):
                    probs.append(f'{rtag}非对象')
                    continue
                missing_r = set(EVIDENCE_REF_FIELDS) - set(ref)
                extra_r = set(ref) - set(EVIDENCE_REF_FIELDS)
                if missing_r:
                    probs.append(f'{rtag}缺字段: {sorted(missing_r)}')
                if extra_r:
                    probs.append(f'{rtag}含schema外字段: {sorted(extra_r)}')
                fact = facts_by_id.get(ref.get('fact_id'))
                if fact is None:
                    probs.append(f'{rtag}.fact_id不在输入证据包'
                                 f'(只允许引用在场事实): {ref.get("fact_id")!r}')
                elif ref.get('metric_id') != fact.get('metric_id'):
                    probs.append(f'{rtag}.metric_id与在场事实身份不符: '
                                 f'{ref.get("metric_id")!r}'
                                 f'≠{fact.get("metric_id")!r}')
                dn = ref.get('direction_note')
                if not isinstance(dn, str) or not dn.strip():
                    probs.append(f'{rtag}.direction_note缺失/非空校验失败')
                else:
                    notes.append(dn)
                    bad = [n for n in extract_numeric_tokens(dn)
                           if n not in ev_nums]
                    if bad:
                        probs.append(f'{rtag}.direction_note数值不在输入证据包'
                                     f'(接地失败/数值被改写): {bad}')

        conds = h.get('falsifiable_conditions')
        if not isinstance(conds, list):
            probs.append(f'{tag}.falsifiable_conditions须列表: {conds!r}')
        else:
            if not conds:
                probs.append(f'{tag}.falsifiable_conditions为空(模式A强制,§六)')
            for j, c in enumerate(conds):
                ctag = f'{tag}.falsifiable_conditions[{j}]'
                if not isinstance(c, dict):
                    probs.append(f'{ctag}非对象')
                    continue
                missing_c = set(CONDITION_FIELDS) - set(c)
                extra_c = set(c) - set(CONDITION_FIELDS)
                if missing_c:
                    probs.append(f'{ctag}缺字段: {sorted(missing_c)}')
                if extra_c:
                    probs.append(f'{ctag}含schema外字段: {sorted(extra_c)}')
                ct = c.get('cond_text')
                if not isinstance(ct, str) or not ct.strip():
                    probs.append(f'{ctag}.cond_text缺失/非空校验失败')
                else:
                    cond_texts.append(ct)
                    bad = [n for n in extract_numeric_tokens(ct) if n not in legal]
                    if bad:
                        probs.append(f'{ctag}.cond_text数值非三合法来源'
                                     f'(接地失败): {bad}')
                spec = c.get('spec')
                if spec is None:
                    non_spec.append(ct if isinstance(ct, str) else '')
                    continue
                if not isinstance(spec, dict):
                    probs.append(f'{ctag}.spec须对象或null(不可规格化): {spec!r}')
                    non_spec.append(ct if isinstance(ct, str) else '')
                    continue
                missing_s = set(SPEC_REQUIRED_FIELDS) - set(spec)
                extra_s = set(spec) - set(SPEC_FIELDS)
                if missing_s:
                    probs.append(f'{ctag}.spec缺必备键: {sorted(missing_s)}')
                if extra_s:
                    probs.append(f'{ctag}.spec含schema外键: {sorted(extra_s)}')
                if spec.get('metric') not in facts_by_mid:
                    probs.append(f'{ctag}.spec.metric不在输入在场指标集'
                                 f'(不在场→不可推导,须转limitations声明): '
                                 f'{spec.get("metric")!r}')
                if spec.get('op') not in SPEC_OPS:
                    probs.append(f'{ctag}.spec.op非法(枚举{SPEC_OPS}): '
                                 f'{spec.get("op")!r}')
                if spec.get('mode') not in SPEC_MODES:
                    probs.append(f'{ctag}.spec.mode非法(枚举{SPEC_MODES}): '
                                 f'{spec.get("mode")!r}')
                tgt = spec.get('target')
                if tgt is None:
                    # target=null→不可程序核验(DESIGN L111 骨架示意):
                    # 合法形态=limitations 声明后存在(登记 REPORT §二.3)
                    non_spec.append(ct if isinstance(ct, str) else '')
                elif not _num(tgt):
                    probs.append(f'{ctag}.spec.target非法(须数值或null): {tgt!r}')
                    non_spec.append(ct if isinstance(ct, str) else '')
                elif tgt not in legal:
                    probs.append(f'{ctag}.spec.target非三合法来源'
                                 f'(编造阈值,校验器拒绝): {tgt}')
                else:
                    n_spec += 1
                    spec_conds.append((hid, (spec.get('metric'), spec.get('op'),
                                             tgt, spec.get('mode'))))
                win = spec.get('window')
                if win is not None and not isinstance(win, (str, dict)):
                    probs.append(f'{ctag}.spec.window须字符串或{{start,end}}: {win!r}')
        if isinstance(conds, list) and conds and n_spec == 0:
            probs.append(f'{tag}无可规格化条件(区分性判据须至少一条可程序核验条件)')

        lims = h.get('limitations')
        if not isinstance(lims, list):
            probs.append(f'{tag}.limitations须列表: {lims!r}')
        else:
            if not lims:
                probs.append(f'{tag}.limitations为空(须承接①-④)')
            blob = ' | '.join(str(x) for x in lims)
            for mid in absent_ids:
                if mid not in blob:
                    probs.append(f'{tag}.limitations未承接缺席指标(逐项): {mid}')
            if gate_a == 'DEGRADED' and not any(mk in blob
                                                for mk in DEGRADED_ACK_MARKERS):
                probs.append(f'{tag}.limitations未承接Gate A降级影响面(径2义务)')
            others = [x for x in ids if x != hid]
            if others and not any(isinstance(o, str) and o in blob
                                  for o in others):
                probs.append(f'{tag}.limitations缺未覆盖替代解释指针'
                             f'(指向竞争假设): {others}')
            for nst in non_spec:
                if not (nst and (nst in blob or NON_SPECIFIABLE_MARKER in blob)):
                    probs.append(f'{tag}.limitations未声明不可程序裁决条件: {nst!r}')
            for x in lims:
                if isinstance(x, str):
                    bad = [n for n in extract_numeric_tokens(x) if n not in ev_nums]
                    if bad:
                        probs.append(f'{tag}.limitations数值不在输入证据包'
                                     f'(接地失败): {bad}')

        if conf == 'high':
            if non_spec:
                probs.append(f'{tag}.confidence=high但存在不可程序核验条件'
                             '(定义要求全部可核验→应为medium/low)')
            if isinstance(sup, list) and not sup:
                probs.append(f'{tag}.confidence=high但支持证据为空(证据单侧→low)')
        substantive = ' '.join([stmt if isinstance(stmt, str) else '']
                               + notes + cond_texts)
        for mid in absent_ids:
            if mid in substantive and conf == 'high':
                probs.append(f'{tag}.confidence=high但实质字段涉及缺席指标{mid}'
                             '(涉及缺席→降置信,径2)')

    # 区分性判据(§四(1)之3/§五(1)之4): 两两配对须存在四元组不全同的条件对
    by_h = {}
    for hid, quad in spec_conds:
        by_h.setdefault(hid, []).append(quad)
    hids = list(by_h)
    for a in range(len(hids)):
        for b in range(a + 1, len(hids)):
            ha, hb = hids[a], hids[b]
            ok = any(qa != qb for qa in by_h[ha] for qb in by_h[hb])
            if not ok:
                probs.append(f'竞争性不足: {ha}与{hb}全部可规格条件裁决结果恒同'
                             '(仅措辞不同而无判据区分,校验器拒绝)')


def _validate_mode_b(inp, out, probs, ev_nums):
    missing_top = set(MODE_B_FIELDS) - set(out)
    extra_top = set(out) - set(MODE_B_FIELDS)
    if missing_top:
        probs.append(f'顶层缺必备字段(裁剪版): {sorted(missing_top)}')
    if extra_top:
        probs.append(f'顶层含schema外字段(闭合schema防数值旁路): {sorted(extra_top)}')
    _validate_echo_and_ack(inp, out, probs, 'phenomenon_echo',
                           (inp.get('query_ref') or {}).get('question_text'),
                           '查询问题')
    expl = out.get('explanation')
    if not isinstance(expl, str) or not expl.strip():
        probs.append('explanation缺失/非空校验失败(裁剪版必备)')
    else:
        bad = [n for n in extract_numeric_tokens(expl) if n not in ev_nums]
        if bad:
            probs.append(f'explanation数值不在输入证据包'
                         f'(模式B接地强制,无源数值fail-closed): {bad}')
    if 'hypotheses' in out or 'falsifiable_conditions' in out:
        probs.append('模式B裁剪版不得携带hypotheses/falsifiable_conditions'
                     '(默认不带,§六;升级为任务后走模式A全义务)')


# ══ 假设-证据映射表(§四(2): 装配期由校验器构建,入研究档案) ═══════════════

def build_hypothesis_evidence_map(inp, out, *, registry_targets=None,
                                  prior_trigger_targets=None):
    """映射表行={hypothesis_id, fact_id, metric_id, direction, quality_status,
    snapshot_id, snapshot_digest}(§四(2) L135-141)。模式B→None(无假设集)。

    公共API fail-closed: 输出未过校验→InvalidOutput(不产映射)。
    neutral 登记(G1/本包 REPORT §二.3): G2 不发(输出无中性向证据字段)。"""
    probs = validate_output(inp, out, registry_targets=registry_targets,
                            prior_trigger_targets=prior_trigger_targets)
    if probs:
        raise InvalidOutput('输出未过校验,拒绝构建假设-证据映射表: '
                            + '; '.join(probs[:5]))
    if inp.get('mode') != 'A':
        return None
    facts_by_id = {f.get('fact_id'): f
                   for f in (inp.get('evidence_pack') or {}).get('facts') or []
                   if isinstance(f, dict)}
    sb = inp.get('snapshot_binding') or {}
    rows = []
    for h in out.get('hypotheses') or []:
        for label, direction in (('supporting_evidence', 'support'),
                                 ('counter_evidence', 'counter')):
            for ref in h.get(label) or []:
                if not isinstance(ref, dict):
                    continue
                fact = facts_by_id.get(ref.get('fact_id')) or {}
                rows.append({'hypothesis_id': h.get('hypothesis_id'),
                             'fact_id': ref.get('fact_id'),
                             'metric_id': ref.get('metric_id'),
                             'direction': direction,
                             'quality_status': fact.get('quality_status'),
                             'snapshot_id': sb.get('snapshot_id'),
                             'snapshot_digest': sb.get('snapshot_digest')})
    return {'snapshot_id': sb.get('snapshot_id'),
            'snapshot_digest': sb.get('snapshot_digest'),
            'rows': rows}


# ══ 失败三径状态机(§三(b);确定性样例驱动,零真实调用) ═════════════════════

def _absent_event(inp, reason, used, trace):
    """径3 缺席登记事件记录(DESIGN L87: 不部分产出/不静默跳过/状态不推进)。"""
    sb = inp.get('snapshot_binding') or {}
    tref, qref = inp.get('task_ref'), inp.get('query_ref')
    event = {
        'event_type': OUTCOME_ABSENT_REGISTERED,
        'task_id': tref.get('task_id') if isinstance(tref, dict) else None,
        'origin_query_id': qref.get('query_id')
        if isinstance(qref, dict) else None,
        'snapshot_id': sb.get('snapshot_id'),
        'snapshot_digest': sb.get('snapshot_digest'),
        'failure_reason': reason,
        'attempts_used': used,
        'task_status_advanced': False,
        'conclusion_produced': False,
    }
    return {'outcome': OUTCOME_ABSENT_REGISTERED, 'absence_event': event,
            'validated_output': None, 'evidence_map': None,
            'attempts_used': used, 'trace': trace}


def run_conclusion_pipeline(inp, attempts, *, max_retries=MAX_RETRIES,
                            backoff_base=BACKOFF_LINEAR_BASE,
                            registry_targets=None,
                            prior_trigger_targets=None):
    """失败三径状态机(§三(b): 径1重试→径2降级→径3缺席登记;离线确定性)。

    【桩注入点】attempts=注入的模型尝试产物序列(本模块模型调用面的确定性形态;
    每项 {'raw': <响应文本>} 或 {'error': <说明>, 'kind': <瞬态类|cost_breaker>});
    禁任何真实出站(真实调用属WP-G4,PENDING)。零实际休眠: 线性退避=计划表记录。

    径1: 瞬态错误/解析失败/校验失败→反馈记录+退避计划→重试(≤max_retries);
    径2: 校验通过且(gate_a=DEGRADED 或 absent_registry非空)→ACCEPTED_DOWNGRADED
         (降级义务已由校验器强制: limitations逐项承接+涉缺席降置信);
    径3: 重试耗尽/cost_breaker(即时)/未知失败类(fail-closed)→缺席事件,
         无部分产出,task_status_advanced=False。"""
    probs0 = mia.validate_input(inp)
    if probs0:
        raise InvalidResearchInput('入参非有效ModelResearchInput(G1契约): '
                                   + '; '.join(probs0[:5]))
    trace = []
    used = 0
    for att in attempts:
        if used >= max_retries:
            break
        used += 1
        if 'error' in att:
            kind = att.get('kind')
            note = att.get('error')
            if kind == COST_BREAKER_KIND:
                trace.append({'attempt': used, 'kind': kind, 'note': note})
                return _absent_event(inp, f'费用熔断({COST_BREAKER_KIND}): {note}',
                                     used, trace)
            if kind in TRANSIENT_ERROR_KINDS:
                trace.append({'attempt': used, 'kind': kind, 'note': note,
                              'backoff_s': round(used * backoff_base, 4),
                              'feedback': f'瞬态失败({kind}),线性退避后重试'})
                continue
            trace.append({'attempt': used, 'kind': str(kind), 'note': note})
            return _absent_event(inp, f'未知失败类(fail-closed即径3): {kind}',
                                 used, trace)
        obj, perr = parse_hypothesis_set(att.get('raw'))
        if obj is None:
            trace.append({'attempt': used, 'kind': 'parse', 'note': perr,
                          'backoff_s': round(used * backoff_base, 4),
                          'feedback': f'解析失败回注修正: {perr}'})
            continue
        probs = validate_output(inp, obj, registry_targets=registry_targets,
                                prior_trigger_targets=prior_trigger_targets)
        if probs:
            fb = '; '.join(probs[:5])
            trace.append({'attempt': used, 'kind': 'validation', 'note': fb,
                          'backoff_s': round(used * backoff_base, 4),
                          'feedback': f'校验失败回注修正: {fb}'})
            continue
        gate_a = (inp.get('snapshot_binding') or {}).get('gate_a')
        downgraded = gate_a == 'DEGRADED' or bool(inp.get('absent_registry'))
        outcome = OUTCOME_ACCEPTED_DOWNGRADED if downgraded else OUTCOME_ACCEPTED
        emap = None
        if inp.get('mode') == 'A':
            emap = build_hypothesis_evidence_map(
                inp, obj, registry_targets=registry_targets,
                prior_trigger_targets=prior_trigger_targets)
        trace.append({'attempt': used, 'kind': 'ok', 'note': outcome})
        return {'outcome': outcome, 'validated_output': obj,
                'evidence_map': emap, 'absence_event': None,
                'attempts_used': used, 'trace': trace}
    return _absent_event(inp, '连续重试失败(校验不过/瞬态失败,重试上限耗尽)',
                         used, trace)


if __name__ == '__main__':
    print(json.dumps(echo_params(), ensure_ascii=False, sort_keys=True))
