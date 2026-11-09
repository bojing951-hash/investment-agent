#!/usr/bin/env python3
"""模型研究结论层真实调用接线(第 4/末实现包;v2.1 中性名,原 WP-G4)

合同要点(历史设计档已移出公开仓):「调用点接入+费用/用量记录+熔断;
不含生产部署与 launchd」。

三层合同约束(模块级落实):
1. PENDING 门/执行发车硬门: 真实调用唯一入口 run_live_conclusion/run_smoke 先过
   _live_gate(RUN_MODEL_LIVE=1 且 MODEL_API_KEY 在场,沿 tests/test_model_live.py
   默认跳过门控模式),未过=LiveGateRefused,零出站零凭证读取;
2. 熔断护航(合同冻结值,禁回改): CB-1 连续失败≥5 TRIPPED/CB-2 单执行段
   ≤60 次出站达限软停/CB-3 单日(UTC)费用估算累计≥USD 5.00 TRIPPED/CB-4 单次
   >120 秒计失败并入 CB-1;TRIPPED 后零自动重试(复位=显式人工 reset,且仅清
   熔断态与连续计数,日费用与段出站计数不清零);
3. 逐面登记: 真实调用产物含 REGISTRY 行渲染(render_registry_row,凭证仅记
   环境变量名别名,禁明文禁值)。

tests 与 CI 零真实出站(无条件): 本模块真实出站路径=call_model_once 且仅当
client_factory=None(函数体内惰性 `from openai import OpenAI`,项目既有依赖
requirements openai>=1.0.0);一切测试经 client_factory 显式依赖注入合成桩。
模块级零 openai/requests/urllib import。

复用调用(禁复制分叉): 输入装配=G1(mia.assemble/validate_input);失败三径
状态机=G2(mov.run_conclusion_pipeline,attempts 序列唯一消费方);结论落档=G3
(mci.build_conclusion_record/append_conclusion_record);机制族=allocation_engine
MECHANISM_CATEGORIES;重试预算/失败类词表=mov 常量。

快照纪律: 本模块零原始采集档读取与路径引用(源码 grep 反证零命中);执行段
输入唯一来源=G1 装配产物(经 R1 标准化层);冒烟快照由既有 snapshot_builder
(标准化层)产出。

红线: 本层输出=研究辅助输入非事实源;零交易/仓位/收益承诺,
输出契约经 G2 校验器+G3 门禁提案,模型判断永不直接写状态。

v2.1(Charter 5 S2/S3, 2026-11-09): 模块更名 model_conclusion_client;
硬编码默认端点/模型名常量删除(实际调用值全部来自 MODEL_* 三参);
用量记录记实际值(model/endpoint_host 取自 env_config 实际配置);
执行门只认 MODEL_API_KEY;单次调用函数更名 call_model_once。
"""
import argparse
import datetime as _dt
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import model_input_assembler as mia       # noqa: E402 (G1 复用调用)
import model_output_validator as mov      # noqa: E402 (G2 复用调用)
import model_conclusion_integrator as mci  # noqa: E402 (G3 复用调用)
import allocation_engine as ae          # noqa: E402 (机制族清单复用引用)

# ══ 合同冻结值(§七.5,禁回改;echo=常量=登记三方一致,REPORT §二.1) ════════
CB1_MAX_CONSECUTIVE_FAILURES = 5      # 连续失败≥5 → TRIPPED
CB2_MAX_OUTBOUND_PER_SEGMENT = 60    # 单执行段出站上限,达限软停
CB3_DAILY_COST_CAP_USD = 5.00        # 单日(UTC)费用估算累计上限,达限 TRIPPED
CB4_TIMEOUT_SECONDS = 120           # 单次>120 秒计为失败并入 CB-1

# ══ 本包登记初值(历史 DP-1/DP-2/DP-4 决议;v2.1: 默认端点/模型名常量删除,
#     实际调用值全部来自 env_config.model_runtime_config() 的 MODEL_* 三参) ══
CALL_TEMPERATURE = 0.2            # 低温档(候选 0.1-0.2 内取 0.2)
CALL_REASONING_EFFORT = 'low'     # 思考档位(历史踩坑备案: 高档耗尽 token)
CALL_MAX_TOKENS = 16000           # 结构化输出+思考余量
CALL_CLIENT_TIMEOUT_S = 125.0     # CB4+5s 边际(判定阈独立于客户端超时)
CREDENTIAL_ENV = 'MODEL_API_KEY'  # 环境变量唯一凭证来源,零本机回退(v2.1 唯一名)
LIVE_GATE_ENV = 'RUN_MODEL_LIVE'  # 默认跳过门控(test_model_live.py 模式)

# ══ 费用估算参数(CB-3 口径;REPORT §二.3;保守估算非账单真值) ═════════════
EST_INPUT_USD_PER_MTOK = 3.0      # [示意·非实取] 保守输入单价 USD/1M tokens
EST_OUTPUT_USD_PER_MTOK = 9.0     # [示意·非实取] 保守输出单价 USD/1M tokens
EST_FLOOR_USD_PER_CALL = 0.02     # [示意·非实取] 单次下限(用量不可得/失败亦计)

RETRY_BUDGET = mov.MAX_RETRIES    # 复用 G2 登记值(=3,不另立)
ARCHIVE_KEY = 'conclusions'       # mci.append_conclusion_record 档案子结构键

_REDACTED = '<<REDACTED>>'
_RISK_CODES = (1301,)              # 内容风控码(report_generator.py:580 踩坑备案)


def _num(v):
    """数值判定(bool 豁免;与 mov._num 同语义,独立实现避免私有面依赖)。"""
    return isinstance(v, (int, float)) and not isinstance(v, bool)


class LiveGateRefused(Exception):
    """执行发车门未过(RUN_MODEL_LIVE/MODEL_API_KEY 缺席): 零出站零凭证读取。"""


class CircuitBreakerTripped(Exception):
    """熔断 TRIPPED/软停后出站请求被拒(供直接调用方;编排层走返回值分流)。"""


def echo_params():
    """登记参数 echo(登记=常量=echo 三方一致)。"""
    return {
        'cb1_max_consecutive_failures': CB1_MAX_CONSECUTIVE_FAILURES,
        'cb2_max_outbound_per_segment': CB2_MAX_OUTBOUND_PER_SEGMENT,
        'cb3_daily_cost_cap_usd': CB3_DAILY_COST_CAP_USD,
        'cb4_timeout_seconds': CB4_TIMEOUT_SECONDS,
        'call_temperature': CALL_TEMPERATURE,
        'call_reasoning_effort': CALL_REASONING_EFFORT,
        'call_max_tokens': CALL_MAX_TOKENS,
        'call_client_timeout_s': CALL_CLIENT_TIMEOUT_S,
        'credential_env': CREDENTIAL_ENV,
        'live_gate_env': LIVE_GATE_ENV,
        'est_input_usd_per_mtok': EST_INPUT_USD_PER_MTOK,
        'est_output_usd_per_mtok': EST_OUTPUT_USD_PER_MTOK,
        'est_floor_usd_per_call': EST_FLOOR_USD_PER_CALL,
        'retry_budget': RETRY_BUDGET,
        'mechanism_categories': list(ae.MECHANISM_CATEGORIES),
    }


# ══ 工具: 脱敏/费用估算/延迟分类 ═══════════════════════════════════════════

def redact(text):
    """凭证明文剥离: 内存中所有模型 Key(MODEL_API_KEY 与遗留变量名下的旧 Key
    值,长度>4)一律替换为占位符;Authorization 头(含可选 Bearer 前缀)整段
    吃满令牌。(v2.1: 凭证面唯一=MODEL_API_KEY;旧变量名值仍参与剥离=密钥卫生
    防泄漏,非配置读取面。)"""
    s = str(text)
    for _env_name in ('MODEL_API_KEY', 'GLM_API_KEY'):   # 旧名=密钥卫生(防泄漏),非配置面
        _v = os.environ.get(_env_name, '')
        if _v and len(_v) > 4 and _v in s:
            s = s.replace(_v, _REDACTED)
    s = re.sub(r'(Authorization\s*[:=]\s*(?:Bearer\s+)?)\S+',
               r'\1' + _REDACTED, s, flags=re.I)
    return s


def estimate_cost_usd(usage):
    """单次调用费用保守估算(CB-3 口径;单调高估方向安全,非账单真值)。"""
    if not isinstance(usage, dict):
        return EST_FLOOR_USD_PER_CALL
    pt = usage.get('prompt_tokens')
    ct = usage.get('completion_tokens')
    if not isinstance(pt, (int, float)) or not isinstance(ct, (int, float)):
        return EST_FLOOR_USD_PER_CALL
    est = (pt * EST_INPUT_USD_PER_MTOK / 1e6
           + ct * EST_OUTPUT_USD_PER_MTOK / 1e6)
    return round(max(EST_FLOOR_USD_PER_CALL, est), 6)


def classify_elapsed(elapsed_s):
    """CB-4 判定: 单次调用耗时(秒)>120 → 计为失败(严格大于,阈值冻结字面量)。"""
    if elapsed_s > CB4_TIMEOUT_SECONDS:
        return 'cb4_timeout'
    return 'ok'


def _utcnow_iso():
    return _dt.datetime.now(_dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _usage_dict(usage):
    if usage is None:
        return None
    pt = getattr(usage, 'prompt_tokens', None)
    ct = getattr(usage, 'completion_tokens', None)
    tt = getattr(usage, 'total_tokens', None)
    if pt is None and ct is None and isinstance(usage, dict):
        pt, ct, tt = usage.get('prompt_tokens'), usage.get('completion_tokens'), \
            usage.get('total_tokens')
    return {'prompt_tokens': pt, 'completion_tokens': ct, 'total_tokens': tt}


# ══ 熔断器(合同 §七.5 冻结值;合成注入面=note_* 直驱) ═════════════════════

class CircuitBreaker:
    """执行段熔断器: CB-1~CB-4 全程护航;TRIPPED 后零自动重试。

    复位语义(登记): reset()=显式人工动作,仅清 tripped 态与连续失败计数;
    日费用累计(day_cost_usd)与段出站计数(outbound_count)不清零——CB-2/CB-3
    为累计登记面,复位不扩张调用/费用边界。
    """

    def __init__(self, *, day_utc=None):
        self.cb1 = CB1_MAX_CONSECUTIVE_FAILURES
        self.cb2 = CB2_MAX_OUTBOUND_PER_SEGMENT
        self.cb3 = CB3_DAILY_COST_CAP_USD
        self.cb4 = CB4_TIMEOUT_SECONDS
        self.day_key = day_utc or _utcnow_iso()[:10]
        self.consecutive_failures = 0
        self.outbound_count = 0
        self.day_cost_usd = 0.0
        self.tripped = None            # None | 'CB-1' | 'CB-3'
        self.trip_reason = ''
        self.last_call_elapsed_s = None

    def outbound_allowed(self):
        """出站前置判定: TRIPPED/CB-2 达限 → (False, 原因);否则 (True, '')。"""
        if self.tripped:
            return False, f'TRIPPED-{self.tripped}: {self.trip_reason}'
        if self.outbound_count >= self.cb2:
            return False, (f'CB-2 软停: 单执行段出站已达上限 '
                           f'{self.outbound_count}/{self.cb2}')
        return True, ''

    def note_outbound(self):
        """出站计数(CB-2);调用发起前登记。"""
        self.outbound_count += 1
        return self.outbound_count

    def note_success(self, cost_usd):
        """成功: 连续失败计数清零+费用累计(CB-3 判定)。"""
        self.consecutive_failures = 0
        self._accrue(cost_usd)
        return self.state()

    def note_failure(self, kind, cost_usd=0.0):
        """失败(CB-1 计数;含 CB-4 超时类): 连续+1,达 CB-1 → TRIPPED。

        登记决策(保守方向): 一切调用失败类(含 4xx 认证类)均入 CB-1 连续
        计数——合同枚举「网络错/5xx/超时」为下限非上限,高估方向安全。
        """
        self.consecutive_failures += 1
        self._accrue(cost_usd)
        if self.consecutive_failures >= self.cb1:
            self.tripped = 'CB-1'
            self.trip_reason = (f'连续失败{self.consecutive_failures}次'
                                f'≥{self.cb1}(末次失败类={kind})')
        return self.state()

    def _accrue(self, cost_usd):
        c = float(cost_usd or 0.0)
        self.day_cost_usd = round(self.day_cost_usd + c, 6)
        if self.day_cost_usd >= self.cb3 and not self.tripped:
            self.tripped = 'CB-3'
            self.trip_reason = (f'单日({self.day_key} UTC)费用估算累计'
                                f'${self.day_cost_usd:.2f}≥${self.cb3:.2f}')

    def state(self):
        return {
            'day_utc': self.day_key,
            'tripped': self.tripped,
            'trip_reason': self.trip_reason,
            'consecutive_failures': self.consecutive_failures,
            'outbound_count': self.outbound_count,
            'day_cost_usd': self.day_cost_usd,
            'thresholds': {'cb1': self.cb1, 'cb2': self.cb2,
                           'cb3': self.cb3, 'cb4': self.cb4},
        }

    def reset(self):
        """显式人工复位(非自动): 仅清熔断态+连续失败计数(登记语义见类注释)。"""
        self.tripped = None
        self.trip_reason = ''
        self.consecutive_failures = 0
        return self.state()


# ══ Prompt 构造(DESIGN §四(1) 六槽位强制;模式 A/B) ══════════════════════

_SYSTEM_PROMPT = (
    '你是全球宏观研究系统的「研究结论层」辅助引擎(研究辅助输入,非事实源)。\n'
    '你的输出是供确定性校验器与程序门禁审查的结构化假设集,不是投资建议;\n'
    '禁止任何交易指令、仓位建议或收益承诺。\n'
    '一切数值只能取自用户消息给出的合法数值清单;禁止推算新数值、禁止编造阈值。\n'
    '只输出一个 JSON 对象(允许 ```json 围栏包裹),不要输出任何其他文字。')


def _legal_numbers(inp):
    """三合法来源并集(复用 mov): 证据包在场数值∪注册表阈值∪输入先验触发值。

    测试注入面: build_prompt(legal_targets=…) 显式注入(不读真实 registry)。"""
    nums = set(mov.collect_evidence_numbers(inp))
    nums |= mov.registry_legal_targets()
    pk = inp.get('prior_knowledge') or {}
    for trig in (pk.get('quant_triggers') or []):
        t = trig.get('target') if isinstance(trig, dict) else None
        if _num(t):
            nums.add(t)
    return nums


def _fmt_nums(nums, limit=400):
    vals = sorted(n for n in nums if _num(n))
    rendered = ', '.join(repr(v) for v in vals[:limit])
    if len(vals) > limit:
        rendered += f', …(共{len(vals)}个)'
    return rendered or '(无——此时 spec.target 只能 null 并声明不可程序裁决)'


def _facts_table(inp):
    rows = []
    for f in ((inp.get('evidence_pack') or {}).get('facts')) or []:
        if not isinstance(f, dict):
            continue
        derived = f.get('derived') or {}
        dparts = []
        for w, wrec in sorted(derived.items()):
            if isinstance(wrec, dict):
                for k in ('pct_change', 'pp_change', 'bp_change', 'abs_change',
                          'basis_value'):
                    v = wrec.get(k)
                    if _num(v):
                        dparts.append(f'{w}.{k}={v}')
        rows.append({
            'fact_id': f.get('fact_id'), 'metric_id': f.get('metric_id'),
            'value': f.get('value'), 'unit': f.get('unit'),
            'observation_date': f.get('observation_date'),
            'quality_status': f.get('quality_status'),
            'derived': ('; '.join(dparts) if dparts else None)})
    return rows


def build_prompt(inp, *, feedback=None, legal_targets=None):
    """六槽位 prompt 构造(DESIGN §四(1) L126-131;§六 模式 B 裁剪)。

    返回 (system_prompt, user_prompt)。槽位与输出 schema 字段名复用 mov 常量
    (禁复制分叉);合法数值默认=三来源并集实算,测试可注入。"""
    probs = mia.validate_input(inp)
    if probs:
        raise mia.AssemblyRefused(
            'prompt 构造前置: 输入非有效 ModelResearchInput(G1 契约): '
            + '; '.join(probs[:5]))
    mode = inp['mode']
    nums = _legal_numbers(inp) if legal_targets is None else set(legal_targets)
    facts = _facts_table(inp)
    absent = [a for a in inp.get('absent_registry') or [] if isinstance(a, dict)]
    mech = ' / '.join(ae.MECHANISM_CATEGORIES)
    lines = []

    if mode == 'A':
        tref = inp['task_ref']
        lines.append('【槽1·现象复述(必含)】')
        lines.append(f"任务现象(原文): {tref['phenomenon']}")
        win = tref.get('window') or {}
        lines.append(f"窗口: {win.get('start')} ~ {win.get('end')}")
        lines.append(f"指标: {', '.join(tref['indicators'])}")
        lines.append('')
        lines.append('【槽2·机制族提示(假设多样性)】')
        lines.append(f'机制类别清单: {mech}')
        lines.append('要求: 各假设至少覆盖两个不同机制族(设计规则)。')
        lines.append('')
        lines.append('【槽3·竞争性强制】')
        lines.append(f'必须产出至少 {mia.MIN_COMPETING_HYPOTHESES} 个相互竞争假设。')
        lines.append('竞争性判定: 假设间对同一指标组合给出可区分的预测方向或机制'
                     '路径,或各自可反驳条件中至少一条判据能区分彼此(区分性判据);'
                     '仅措辞不同而无判据区分=不构成竞争,将被拒绝。')
        lines.append('hypothesis_id 形态: HY-YYYYMMDD-NNN(三位序列,当日日期)。')
        lines.append('')
        lines.append('【槽4·反方证据强制】')
        lines.append('每个假设必须附 counter_evidence 非空数组(引用输入事实 '
                     'fact_id/metric_id);若证据与假设相悖,必须列为 '
                     'counter_evidence 而非省略或重新解释为支持。'
                     '空数组将被拒绝,不存在无反方证据的合法输出。')
        lines.append('')
        lines.append('【槽5·数值接地】')
        lines.append('一切数值只能取自输入证据包;合法数值清单(闭集):')
        lines.append(_fmt_nums(nums))
        lines.append('falsifiable_conditions[].spec.target 只能取上述清单中的值;'
                     '无法取合法值时 target=null 且该条件必须在 limitations 声明'
                     f'「{mov.NON_SPECIFIABLE_MARKER}」。')
        lines.append('')
        lines.append('【槽6·缺席承接】')
        if absent:
            for a in absent:
                lines.append(f"- 缺席: {a.get('metric_id')}"
                             f"({a.get('level')}): {a.get('reason')}")
            lines.append('要求: absent_ack 逐项复述每个缺席 metric_id;'
                         '相关假设 limitations 须承接缺席影响。')
        else:
            lines.append('输入无缺席登记: absent_ack 必须为空数组(空进空出)。')
        lines.append('')
        lines.append('【证据包(快照事实投影,数值唯一来源)】')
        lines.append('```json')
        lines.append(json.dumps(facts, ensure_ascii=False, indent=1))
        lines.append('```')
        lines.append('')
        lines.append('【输出 JSON schema(严格闭合,字段名逐字一致)】')
        lines.append('```json')
        lines.append(json.dumps({
            'hypotheses': [{
                'hypothesis_id': 'HY-YYYYMMDD-NNN',
                'statement': '假设陈述(可含证据包数值)',
                'supporting_evidence': [{'fact_id': '<输入fact_id>',
                                         'metric_id': '<输入metric_id>',
                                         'direction_note': '方向说明'}],
                'counter_evidence': [{'fact_id': '<输入fact_id>',
                                      'metric_id': '<输入metric_id>',
                                      'direction_note': '反方方向说明'}],
                'falsifiable_conditions': [{
                    'cond_text': '若X则Y(可反驳条件)',
                    'spec': {'metric': '<指标之一>', 'op': '>=|>|<|<=',
                             'target': '<合法数值清单中的值或null>',
                             'mode': 'touch|expiry',
                             'window': {'start': win.get('start'),
                                        'end': win.get('end')}}}],
                'confidence': 'high|medium|low',
                'limitations': ['缺席承接(如有)/未覆盖替代解释指针/'
                                '不可程序裁决声明(如有)'],
            }],
            'phenomenon_echo': '<必须包含任务现象原文>',
            'absent_ack': ['<逐项复述缺席指标;无缺席则空数组>'],
        }, ensure_ascii=False, indent=1))
        lines.append('```')
        lines.append(f"spec.metric 只能取: {', '.join(tref['indicators'])};"
                     f" op ∈ {', '.join(mov.SPEC_OPS)};"
                     f" mode ∈ {', '.join(mov.SPEC_MODES)};"
                     ' window 与任务窗口一致。')
    else:
        qref = inp['query_ref']
        lines.append('【槽1·现象复述(必含)】')
        lines.append(f"用户问题(原文): {qref['question_text']}")
        lines.append(f"研究截止: {qref.get('as_of')}")
        lines.append('')
        lines.append('【槽5·数值接地】')
        lines.append('解释(explanation)中一切数值只能取自输入证据包;'
                     '合法数值清单(闭集):')
        lines.append(_fmt_nums(nums))
        lines.append('')
        lines.append('【槽6·缺席承接】')
        if absent:
            for a in absent:
                lines.append(f"- 缺席: {a.get('metric_id')}"
                             f"({a.get('level')}): {a.get('reason')}")
            lines.append('要求: absent_ack 逐项复述每个缺席 metric_id。')
        else:
            lines.append('输入无缺席登记: absent_ack 必须为空数组。')
        lines.append('')
        lines.append('【证据包(快照事实投影,数值唯一来源)】')
        lines.append('```json')
        lines.append(json.dumps(facts, ensure_ascii=False, indent=1))
        lines.append('```')
        lines.append('')
        lines.append('【输出 JSON schema(模式B裁剪,严格闭合)】')
        lines.append('```json')
        lines.append(json.dumps({
            'phenomenon_echo': '<必须包含用户问题原文>',
            'explanation': '<接地解释: 数值全部取自证据包>',
            'absent_ack': ['<逐项复述缺席指标;无缺席则空数组>'],
        }, ensure_ascii=False, indent=1))
        lines.append('```')

    if feedback:
        lines.append('')
        lines.append('【径1反馈回注(上一尝试失败原因,修正后重试)】')
        lines.append(str(feedback))
    return _SYSTEM_PROMPT, '\n'.join(lines)


# ══ 调用点(client_factory=显式依赖注入面;None=真实路径) ═════════════════

def _classify_exception(exc):
    name = type(exc).__name__
    msg = str(exc)
    if 'timeout' in name.lower() or 'timeout' in msg.lower():
        return 'network'
    status = getattr(exc, 'status_code', None) or getattr(exc, 'code', None)
    if status in _RISK_CODES:
        return 'risk_control'
    if status in (401, 403):
        return 'auth_error'
    if isinstance(status, int) and 500 <= status < 600:
        return 'network'
    if '1301' in msg:
        return 'risk_control'
    return 'network'


def _call_result(ok, *, kind=None, error=None, raw=None, usage=None,
                 elapsed_s, cost_est_usd):
    d = {'ok': ok, 'elapsed_s': round(elapsed_s, 3),
         'cost_est_usd': cost_est_usd}
    if ok:
        d.update({'raw': raw, 'usage': usage, 'kind': 'ok'})
    else:
        d.update({'kind': kind, 'error': redact(error or '')})
    return d


def call_model_once(system_prompt, user_prompt, *, client_factory=None,
                    model=None, temperature=None, max_tokens=None):
    """单次模型调用(执行段真实路径/测试合成桩同一入口)。

    【桩注入点】client_factory=注入的客户端工厂(测试合成桩;返回对象须支持
    chat.completions.create(...) 流式协议);None=真实路径(惰性 import openai,
    项目既有依赖)。model=None 且真实路径→取 env_config 实际配置的 MODEL_NAME;
    桩路径 model 保持 None(如实,不虚构)。返回:
      成功 {'ok':True,'raw','usage','elapsed_s','cost_est_usd'}
      失败 {'ok':False,'kind','error'(已脱敏),'elapsed_s','cost_est_usd'}
    CB-4: elapsed>CB4_TIMEOUT_SECONDS(120) 即使有正文也计为失败(合同冻结)。"""
    temperature = CALL_TEMPERATURE if temperature is None else temperature
    max_tokens = CALL_MAX_TOKENS if max_tokens is None else max_tokens
    t0 = time.monotonic()
    usage = None
    try:
        if client_factory is not None:
            client = client_factory()
        else:
            # v2.1: 真实路径读 env_config 中性三参(MODEL_*),无回退无硬编码默认;
            # 三参不齐=零出站。
            import env_config as _ec
            _cfg = _ec.model_runtime_config()
            if not _cfg['complete']:
                return _call_result(
                    False, kind='auth_error',
                    error='模型 API 未配置(MODEL_API_KEY/MODEL_BASE_URL/'
                          'MODEL_NAME 三参不齐;零凭证零出站;Agent Native '
                          '模式不需要模型 Key)',
                    elapsed_s=time.monotonic() - t0,
                    cost_est_usd=EST_FLOOR_USD_PER_CALL)
            model = _cfg['model']
            from openai import OpenAI   # 惰性: 项目既有依赖(requirements)
            client = OpenAI(api_key=_cfg['api_key'], base_url=_cfg['base_url'],
                            timeout=CALL_CLIENT_TIMEOUT_S)
        stream = client.chat.completions.create(
            model=model,
            messages=[{'role': 'system', 'content': system_prompt},
                      {'role': 'user', 'content': user_prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            extra_body={'reasoning_effort': CALL_REASONING_EFFORT},
            stream=True,
            stream_options={'include_usage': True})
        chunks = []
        for ev in stream:
            u = getattr(ev, 'usage', None)
            if u is not None:
                usage = u
            choices = getattr(ev, 'choices', None)
            if choices:
                delta = getattr(choices[0], 'delta', None)
                piece = getattr(delta, 'content', None) if delta else None
                if piece:
                    chunks.append(piece)
        text = ''.join(chunks)
        elapsed = time.monotonic() - t0
        udict = _usage_dict(usage)
        cost = estimate_cost_usd(udict)
        if classify_elapsed(elapsed) == 'cb4_timeout':
            return _call_result(
                False, kind='network',
                error=(f'CB-4: 单次调用耗时 {elapsed:.1f}s>'
                       f'{CB4_TIMEOUT_SECONDS}s 计为失败(正文弃用)'),
                usage=udict, elapsed_s=elapsed, cost_est_usd=cost)
        if not text.strip():
            return _call_result(
                False, kind='stream_interrupted',
                error='流式返回正文为空(疑似思考耗尽或风控拦截)',
                usage=udict, elapsed_s=elapsed, cost_est_usd=cost)
        return _call_result(True, raw=text, usage=udict,
                            elapsed_s=elapsed, cost_est_usd=cost)
    except Exception as exc:                      # noqa: BLE001(如实分类登记)
        elapsed = time.monotonic() - t0
        udict = _usage_dict(usage)
        cost = estimate_cost_usd(udict)
        return _call_result(False, kind=_classify_exception(exc),
                            error=f'{type(exc).__name__}: {exc}',
                            usage=udict, elapsed_s=elapsed, cost_est_usd=cost)


# ══ 执行段编排(G2 管线消费方+G3 落档+用量记录) ═══════════════════════════

def _live_gate():
    """执行发车门(默认跳过门控,沿 test_model_live.py 模式)。

    未过 → LiveGateRefused(零出站零凭证读取,先于任何 client 构造)。
    v2.1(Charter 5 S2): 凭证面只认 MODEL_API_KEY(env_config 唯一解析面),
    旧变量名不再开例外。"""
    if os.environ.get(LIVE_GATE_ENV) != '1':
        raise LiveGateRefused(
            f'执行门未开: {LIVE_GATE_ENV}!=1(默认跳过,零真实调用零凭证读取)')
    import env_config as _ec
    if not _ec.model_runtime_config()['api_key']:
        raise LiveGateRefused(
            f'执行门未开: {CREDENTIAL_ENV} 缺席(零凭证零出站)')


def _log_usage(path, record):
    """用量/调用日志落盘(JSONL 追加;记录内零凭证明文,error 已脱敏)。"""
    if not path:
        return
    with open(path, 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + '\n')


def run_live_conclusion(inp, *, client_factory=None, breaker=None,
                        face='F1', usage_log_path=None, seq=1,
                        today_iso=None, archive=None):
    """执行段编排: 门控→六槽位 prompt→真实调用(熔断护航)→G2 失败三径
    (attempts 序列唯一消费方,权威 outcome/trace)→G3 结论记录+append-only 落档
    →用量记录。

    重试语义: 预算=mov.MAX_RETRIES(复用);瞬态/解析/校验失败→径1 反馈回注
    (下一尝试 prompt 附反馈槽);TRIPPED/CB-2 达限/费用熔断/未知失败类→停止
    出站(G2 管线对既有 attempts 出权威裁决)。真实出站仅当 client_factory=None
    且门已过;测试一律注入合成桩(零出站)。

    v2.1(Charter 5 S2): 用量记录记**实际值**——model/endpoint_host 取自
    env_config.model_runtime_config() 实际配置(三参不齐→null 如实),不再回显
    任何登记默认端点/模型名。"""
    _live_gate()
    import env_config as _ec
    _cfg = _ec.model_runtime_config()
    # 实际值捕获(S2 实质违规修复): 记录的是本进程真实生效的模型与端点主机
    model_actual = _cfg['model'] or None
    endpoint_host_actual = (
        _cfg['base_url'].split('//')[-1].split('/')[0]
        if _cfg.get('base_url') else None)
    breaker = breaker if breaker is not None else CircuitBreaker()
    probs = mia.validate_input(inp)
    if probs:
        raise mia.AssemblyRefused(
            '编排前置: 输入非有效 ModelResearchInput: ' + '; '.join(probs[:5]))
    system, user = build_prompt(inp)
    attempts = []
    result = None
    blocked_reason = None
    n = 0
    while len(attempts) < RETRY_BUDGET:
        allowed, why = breaker.outbound_allowed()
        if not allowed:
            blocked_reason = why
            break
        breaker.note_outbound()
        n += 1
        breaker_before = breaker.state()
        call = call_model_once(system, user, client_factory=client_factory)
        breaker.last_call_elapsed_s = call.get('elapsed_s')
        if call['ok']:
            breaker.note_success(call['cost_est_usd'])
            attempts.append({'raw': call['raw']})
        else:
            breaker.note_failure(call['kind'], call['cost_est_usd'])
            attempts.append({'error': call['error'], 'kind': call['kind']})
        rec = {
            'ts_utc': _utcnow_iso(), 'face': face, 'attempt': n,
            'ok': call['ok'], 'kind': call['kind'],
            'model': model_actual,
            'endpoint_host': endpoint_host_actual,
            'elapsed_s': call.get('elapsed_s'),
            'usage': call.get('usage'),
            'cost_est_usd': call['cost_est_usd'],
            'breaker_before_tripped': breaker_before.get('tripped'),
            'breaker_after': breaker.state(),
            'error_note': (call.get('error') or '')[:300] if not call['ok']
            else None,
        }
        _log_usage(usage_log_path, rec)
        result = mov.run_conclusion_pipeline(inp, attempts)
        if result['outcome'] != mov.OUTCOME_ABSENT_REGISTERED:
            break
        reason = (result.get('absence_event') or {}).get(
            'failure_reason') or ''
        if mov.COST_BREAKER_KIND in reason or '未知失败类' in reason:
            break
        trace = result.get('trace') or []
        feedback = trace[-1].get('feedback') if trace else None
        if feedback:
            _, user = build_prompt(inp, feedback=feedback)
    if result is None:
        result = mov.run_conclusion_pipeline(inp, attempts)
    record = mci.build_conclusion_record(
        inp, result, seq=seq,
        today_iso=today_iso or _utcnow_iso()[:10])
    archive_status = None
    if archive is not None:
        archive_status, _rec = mci.append_conclusion_record(record, archive)
    validated = result.get('validated_output')
    grounding = None
    if validated is not None:
        grounding = {
            'enforced_by': 'mov.validate_output(数值接地校验通过=outcome 受纳)',
            'evidence_numbers_sorted': sorted(
                mov.collect_evidence_numbers(inp)),
            'outcome': result['outcome'],
        }
    return {
        'pipeline': result,
        'conclusion_record': record,
        'archive_status': archive_status,
        'attempts_used': len(attempts),
        'blocked_reason': blocked_reason,
        'breaker': breaker.state(),
        'grounding': grounding,
    }


def render_registry_row(seq, *, face, purpose, outbound_count, cost_usd,
                        breaker_state, ts_utc=None, approval_ref=''):
    """凭证使用登记行渲染(REGISTRY 文档粘贴用;凭证仅记环境变量名别名;
    模型@端点=env_config 实际配置值,v2.1 S5 去端点示例默认值)。"""
    import env_config as _ec
    _cfg = _ec.model_runtime_config()
    model_disp = _cfg['model'] or '(未配置)'
    endpoint_disp = _cfg['base_url'] or '(未配置)'
    tripped = breaker_state.get('tripped') if isinstance(breaker_state, dict) \
        else None
    cb_state = '未触发' if not tripped else f'TRIPPED-{tripped}'
    return (
        f'| G4-CRED-{seq:03d} | {ts_utc or _utcnow_iso()} | {face} | '
        f'{model_disp} @ {endpoint_disp} | {purpose} | '
        f'{CREDENTIAL_ENV}(环境变量,值不落盘) | '
        f'{outbound_count} / {breaker_state.get("outbound_count", "?")} | '
        f'${cost_usd:.4f} / ${breaker_state.get("day_cost_usd", 0.0):.4f} | '
        f'{cb_state} | {approval_ref} |')


# ══ 冒烟入口(CLI;执行段功能验证步骤) ═════════════════════════════════════

def run_smoke(ymd, snapshot_dir, task_path, out_dir, *, registry_seq=1,
              face='F1', purpose='真实调用冒烟要点①'):
    """模式 A 真实调用冒烟: 装配→真实调用编排→产物落 data/research/。"""
    _live_gate()
    with open(task_path, encoding='utf-8') as fh:   # 运行时输入档(非原始采集档)
        task = json.load(fh)
    inp = mia.assemble(str(ymd), str(snapshot_dir), mode='A', task=task)
    os.makedirs(out_dir, exist_ok=True)
    ts = _utcnow_iso().replace(':', '').replace('-', '')
    usage_log_path = os.path.join(out_dir, f'model_usage_log_{ymd}.jsonl')
    archive_path = os.path.join(out_dir, 'model_conclusions_archive.json')
    archive = {ARCHIVE_KEY: []}
    if os.path.exists(archive_path):
        with open(archive_path, encoding='utf-8') as fh:
            loaded = json.load(fh)
        if isinstance(loaded, dict):
            archive = loaded
    outcome = run_live_conclusion(
        inp, usage_log_path=usage_log_path, seq=registry_seq,
        today_iso=_utcnow_iso()[:10], archive=archive)
    with open(archive_path, 'w', encoding='utf-8') as fh:
        json.dump(archive, fh, ensure_ascii=False, indent=1, sort_keys=True)
    report_path = os.path.join(out_dir, f'model_live_smoke_{ts}.json')
    breaker = outcome['breaker']
    reg_row = render_registry_row(
        registry_seq, face=face, purpose=purpose,
        outbound_count=outcome['attempts_used'],
        cost_usd=breaker.get('day_cost_usd', 0.0),
        breaker_state=breaker,
        approval_ref='PENDING-APPROVALS.md 2026-11-05 批复行(合同冻结章②)')
    report = {
        'wp': 'model-conclusion-client-live', 'face': face, 'purpose': purpose,
        'ymd': str(ymd), 'snapshot_dir': str(snapshot_dir),
        'task_path': str(task_path),
        'task_id': (inp.get('task_ref') or {}).get('task_id'),
        'snapshot_id': (inp.get('snapshot_binding') or {}).get('snapshot_id'),
        'gate_a': (inp.get('snapshot_binding') or {}).get('gate_a'),
        'absent_registry': inp.get('absent_registry'),
        'outcome': outcome['pipeline']['outcome'],
        'attempts_used': outcome['attempts_used'],
        'blocked_reason': outcome['blocked_reason'],
        'trace': outcome['pipeline'].get('trace'),
        'grounding': outcome['grounding'],
        'conclusion_record': outcome['conclusion_record'],
        'archive_status': outcome['archive_status'],
        'breaker': breaker,
        'registry_row': reg_row,
        'usage_log_path': usage_log_path,
    }
    with open(report_path, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1, sort_keys=True)
    return {'report_path': report_path, 'report': report,
            'registry_row': reg_row}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        description='模型研究结论层真实调用接线(默认跳过门控'
                    f'{LIVE_GATE_ENV}=1)')
    ap.add_argument('--echo', action='store_true', help='登记参数 echo')
    ap.add_argument('--live-smoke', action='store_true',
                    help='执行段真实调用冒烟(要点①;需门控+凭证)')
    ap.add_argument('--ymd', default=None, help='快照目标日 YYYYMMDD')
    ap.add_argument('--snapshot-dir', default='data/research',
                    help='快照目录(R1 标准化产物)')
    ap.add_argument('--task', default=None, help='任务档路径(RT-*.json)')
    ap.add_argument('--out-dir', default='data/research',
                    help='运行产物目录(不 commit)')
    ap.add_argument('--registry-seq', type=int, default=1,
                    help='REGISTRY 登记序号')
    args = ap.parse_args()
    if args.echo:
        print(json.dumps(echo_params(), ensure_ascii=False, sort_keys=True))
        sys.exit(0)
    if args.live_smoke:
        try:
            r = run_smoke(args.ymd, args.snapshot_dir, args.task, args.out_dir,
                          registry_seq=args.registry_seq)
        except LiveGateRefused as exc:
            print(f'⏭️ 跳过({exc})')
            sys.exit(0)
        print(json.dumps(r['report'], ensure_ascii=False, indent=1,
                         sort_keys=True))
        print('\n[REGISTRY 行(粘贴至 CREDENTIAL_REGISTRY)]')
        print(r['registry_row'])
        sys.exit(0)
    print(__doc__)
    sys.exit(0)
