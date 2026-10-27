#!/usr/bin/env python3
"""研究数据来源绑定与质量门禁原语(IA-P0-1, 2026-10-27; FIX1整改 2026-10-27;
FIX2整改 2026-10-27)

快照 → 数据包 → 锚点 → 报告 的可验证来源链(任务4):
- 确定性版本选择: 同日多版本快照(research_snapshot_YYYYMMDD[_vN].json)一律取
  **最高修订版**;任何候选损坏(JSON不可解析/缺snapshot_id)→明确拒绝,不得猜测
  回退低版本(不可判断=不可放行);
- Gate A三态语义(任务1): 缺gate_a字段/状态非法/快照不可解析一律**不得默认PASS**;
- 数据包与锚点旁挂meta sidecar(*.meta.json)记录来源快照/digest/Gate A状态,
  报告入口(任务5)与观察器(任务7)据此核验批次一致性;
- 门禁合成(任务6): 任一FAIL→FAIL;无FAIL有DEGRADED→DEGRADED;双PASS→PASS;
  未知状态按FAIL处理(保守)。

IA-P0-1-FIX1(2026-10-27第二轮整改)收紧:
- FIX-01 实际内容绑定: 摘要一律**读取实际文件后重算**(digest_file),不得信任
  sidecar声明值;锚点与权威快照做**确定性重建比对**(build_anchors为快照的
  纯函数——键集合/数值/残留指标任何偏差即拒绝);锚点prompt从已核验锚点重建比对;
- FIX-04 锚点指标质量门禁共享原语: quality缺失/非法/FAIL一律拒绝进入正式观察;
- FIX-05 Gate A声明一致性: 声明PASS但core_fail/core_missing非空、或核心事实
  实际FAIL、或与quality汇总冲突 → 拒绝放行(以注册表criticality为权威);
- FIX-06 快照身份核验: 物理文件名版本 ↔ 内部snapshot_id ↔ target_date必须
  互相匹配,内部声明与文件名冲突的候选整体拒绝。

IA-P0-1-FIX2(2026-10-27第三轮整改)收紧:
- FIX2-02(IA-DEF-002) Gate A从**真实事实重算**: recompute_gate_a以注册表
  active+core集合与快照实际facts为唯一权威,重算核心缺失/核心FAIL/非核心失败/
  重复metric_id/非法质量/计数,gate_status据此裁决声明一致性——声明DEGRADED但
  核心实际FAIL、声明PASS但核心实际缺失且未写入core_missing等矛盾一律拒绝;
- FIX2-04(IA-DEF-004) 版本表示唯一化: 仅接受base(无后缀)与_v2及以上**规范
  十进制**(_v0/_v1/_v00/_v01等一律非法→整日拒绝),保留最高修订版选择规则;
- FIX2-05(IA-DEF-005) 来源元数据必需字段完整一致: verify_anchor_batch要求
  meta日期↔请求日期↔文件名日期一致、必需摘要存在且与实际字节一致、
  meta.gate_a与权威重算一致——缺失即拒绝,不再"缺字段跳过校验"。

设计约束: 纯本地文件实现,不引入数据库/服务/多Agent(约束九);轻量可离线测试。
"""
import glob
import hashlib
import json
import math
import os
import re
from datetime import date as _date_cls

GATES = ('PASS', 'DEGRADED', 'FAIL')
# 锚点指标合法质量状态(事实引擎词汇表): WARN为轻度提示,可记录
ANCHOR_QUALITY_OK = ('PASS', 'DEGRADED', 'WARN')

_CORE_CACHE = None
_ACTIVE_CACHE = None


def core_metric_ids():
    """注册表核心指标ID集合(criticality=core且active)——Gate A分级的唯一权威。
    (FIX-05: 核心与否由注册表决定,不由调用方自行圈定;注册表加载失败→空集,
    调用方将得不到'核心'判定——宁可无法证明,不可虚报。)"""
    global _CORE_CACHE
    if _CORE_CACHE is None:
        try:
            import fact_engine as fe
            reg = fe.load_registry()
            _CORE_CACHE = frozenset(m['metric_id'] for m in reg['metrics']
                                    if m.get('criticality') == 'core'
                                    and m.get('status') == 'active')
        except Exception:
            _CORE_CACHE = frozenset()
    return _CORE_CACHE


def active_registry_metrics():
    """注册表active指标定义(metric_id→metric dict,缓存)——FIX4-01事实身份/
    单位/口径校验与FIX4-03非核心缺失判定的共同权威。加载失败→空dict
    (宁可无法证明,不可虚报)。"""
    global _ACTIVE_CACHE
    if _ACTIVE_CACHE is None:
        try:
            import fact_engine as fe
            reg = fe.load_registry()
            _ACTIVE_CACHE = {m['metric_id']: m for m in reg['metrics']
                             if m.get('status') == 'active'}
        except Exception:
            _ACTIVE_CACHE = {}
    return _ACTIVE_CACHE


# 注册表source → 采集输入通道(snapshot_builder.SOURCES的键)。
# FIX4-03非核心缺失判定边界: 指标"本期应有数据"以**其来源采集文件是否在场**为准
# ——来源文件在场而指标缺席=采集遗漏(计缺失);来源文件整体缺失=来源级缺失
# (同样披露;若该源含core指标则当日已因core_missing判FAIL)。
_SOURCE_TO_INPUT = {
    'global_market_collector': 'global',
    'macro_collector': 'macro',
    'macro_collector(derived)': 'macro',
    'china_market_collector': 'china',
    'rate_expectations': 'rate_economy',
}

# 派生指标输入依赖(与fact_engine.compute_derived一致): 派生缺席在**输入缺席**
# 时属归因性缺席(不计非核心缺失——输入自身已按其规则披露);输入齐全而派生
# 缺席才是异常(计缺失)。NFP_MOM_K额外要求NFP序列m1可算(镜像compute_derived条件)。
_DERIVED_DEPS = {
    'REAL_10Y': ('UST_10Y', 'BEI_10Y'),
    'REAL_5Y': ('UST_5Y', 'BEI_5Y'),
    'HY_IG_DIFF': ('HY_OAS', 'IG_OAS'),
    'ZQ_IMPLIED_AVG': ('ZQ_F1_PRICE',),
    'NFP_MOM_K': ('NFP',),
}


def fact_structure_problems(fact, m, cutoff):
    """FIX4-01(FIX3-NEW-001): 声明有效的注册表事实**必要字段/口径**完整性校验。

    以make_fact()实际结构为基准(与既有事实引擎完全兼容,不新造结构):
    对准备作为有效数值证据的事实(quality_status∈PASS/WARN/DEGRADED)要求——
    - value: 存在且为有限实数(None/NaN/±Infinity/布尔/不可解析字符串=非法);
    - unit: 非空且与注册表该指标定义一致(换单位=口径冲突,不能按原状态使用);
    - value_type: 与注册表一致;
    - observation_date: 存在、可解析、不晚于研究截止(未来观测不得冒充已发布;
      采集日/生成日/文件修改日不得自动充当观测日——只认事实自带观测日);
    - source: 对象且collector/file来源身份非空(retrieved_at按现有采集器实况
      可为None,不强制——不得未经核查就误伤合法事实);派生指标须有非空
      calculation_ref(计算来源可追溯)。
    合法FAIL事实**不在此判非法**: 异常原始值与诊断按既有质量体系降级隔离
    (已被隔离,不会作为有效数值证据)——"已识别并标注的合法质量失败"与
    "事实结构本身不可证明"是两种语义,不得混同。
    返回问题列表(空=结构完整);cutoff=None表示研究截止不可得(该子项跳过)。"""
    mid = m['metric_id']
    probs = []
    v = fact.get('value', _MISSING)
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        probs.append(f"{mid}=value非法:{_short(v)}(须有限实数)")
    elif not math.isfinite(v):
        probs.append(f"{mid}=value非有限实数:{_short(v)}")
    unit = fact.get('unit')
    if not isinstance(unit, str) or not unit.strip():
        probs.append(f"{mid}=unit缺失/为空:{_short(unit)}")
    elif unit != m.get('unit'):
        probs.append(f"{mid}=unit与注册表不一致:{_short(unit)}"
                     f"(注册表={m.get('unit')!r})")
    if fact.get('value_type', _MISSING) != m.get('value_type', 'level'):
        probs.append(f"{mid}=value_type与注册表不一致:{_short(fact.get('value_type'))}")
    od = fact.get('observation_date')
    if not isinstance(od, str) or not od.strip():
        probs.append(f"{mid}=observation_date缺失:{_short(od)}")
    else:
        try:
            d_obs = _date_cls.fromisoformat(od[:10])
        except ValueError:
            probs.append(f"{mid}=observation_date不可解析:{_short(od)}")
        else:
            if cutoff is not None and d_obs > cutoff:
                probs.append(f"{mid}=观测日{d_obs.isoformat()}晚于研究截止"
                             f"{cutoff.isoformat()}(未来观测不得冒充已发布)")
    src = fact.get('source')
    if not isinstance(src, dict):
        probs.append(f"{mid}=source非对象:{_short(src)}")
    else:
        col = src.get('collector')
        if not isinstance(col, str) or not col.strip():
            probs.append(f"{mid}=source.collector缺失/非法:{_short(col)}")
        fil = src.get('file')
        if not isinstance(fil, str) or not fil.strip():
            probs.append(f"{mid}=source.file缺失(来源文件身份不可追溯)")
        # retrieved_at不强制: 部分既有采集器合法地为None(发布日≠观测日亦不混同)
    if (mid in _DERIVED_DEPS or '(derived)' in str(m.get('source', ''))) \
            and (not isinstance(fact.get('calculation_ref'), str)
                 or not fact.get('calculation_ref', '').strip()):
        probs.append(f"{mid}=派生事实缺calculation_ref(计算来源不可追溯)")
    return probs


class _MissingType:
    """哨兵: 与None区分'字段被删除'与'字段值为null'。"""

    def __repr__(self):
        return '<字段缺失>'


_MISSING = _MissingType()


def _short(v, n=40):
    s = repr(v)
    return s if len(s) <= n else s[:n] + '…'


# ══ Gate A 三态语义 ═══════════════════════════════════════════════

# 事实质量合法词汇表(事实引擎grade_issues产出;WARN为轻度提示,counts不计)
FACT_QUALITY = ('PASS', 'WARN', 'DEGRADED', 'FAIL')


def recompute_gate_a(snapshot):
    """从**真实事实+注册表**重算Gate A裁决(IA-P0-1-FIX2/FIX2-02权威口径;
    FIX3-01/F2-NEW-001: 非法事实结构fail-closed;FIX4-01/FIX3-NEW-001:
    事实必要字段与注册表身份完整校验;FIX4-03/FIX3-NEW-003: active非核心指标
    完全缺失识别)。

    不信任快照内任何声明字段——以注册表active集合与facts实际内容重算:
    - core_missing/core_fail: 核心指标无事实/事实FAIL;
    - noncore_fail/noncore_degraded: 非核心事实**合法**FAIL/DEGRADED(按既有
      规则降级披露——合法降级语义不变,不得一律升级FAIL);
    - noncore_missing(+detail): FIX4-03——active非核心指标本期**完全无事实**:
      来源采集文件在场而指标缺席=采集遗漏;来源文件整体缺失=来源级缺失;
      派生指标在输入缺席时属归因性缺席(不计),输入齐全而缺席才计;
      deprecated/未注册指标不要求(不被错误要求);月频"尚未发布新期"≠缺失
      (旧期观测仍应在场——真正未发布表现为**在场事实的观测日滞后**,由既有
      新鲜度窗口降级披露,不在此伪造发布日历);缺失不补零、不伪造数据,
      只进清单并使Gate A至少DEGRADED;
    - duplicates: 同一metric_id多条事实(数据身份冲突→FAIL);
    - non_research_facts: 未注册/已弃用指标的FAIL**诊断记录**(事实引擎
      normalize_*对游离序列的既有标注)——保留披露但**不计入有效研究事实**
      (counts/noncore清单);同一指标若自报PASS/WARN/DEGRADED则属**无注册表
      身份自宣有效**→illegal(FIX4-01: 未注册指标不得自行声明PASS进入正式研究);
    - illegal_quality: 任何非法/不可证明结构——非对象事实/身份缺失/质量缺失
      或非法,以及FIX4-01新增: 声明有效(PASS/WARN/DEGRADED)的注册表事实缺
      value/value非法/单位与注册表不一致/观测日缺失·不可解析·晚于研究截止/
      source无collector·file身份/派生缺calculation_ref。存在即effective=None
      (结构不可证明≠合法非核心FAIL,不得以降级放行);
    - counts: 仅统计注册表active指标事实(与fact_engine.snapshot_quality_grade
      同构改造: 非研究事实诊断记录不冒充研究事实计数);
    - effective: None(非法/不可证明)>FAIL(core缺失/失败/身份冲突)>
      DEGRADED(非核心合法失败/降级/完全缺失)>PASS。

    返回dict;snapshot结构损坏、事实结构非法或注册表不可用时 effective=None
    并在reasons说明(调用方不得当作任何放行状态)。"""
    out = {'core_missing': [], 'core_fail': [], 'noncore_fail': [],
           'noncore_degraded': [], 'noncore_missing': [],
           'noncore_missing_detail': {}, 'duplicates': [],
           'non_research_facts': [], 'illegal_quality': [],
           'counts': {'PASS': 0, 'DEGRADED': 0, 'FAIL': 0}, 'overall': 'PASS',
           'effective': None, 'reasons': []}
    if not isinstance(snapshot, dict):
        out['reasons'].append('快照不可解析(非JSON对象)')
        return out
    facts = snapshot.get('facts')
    if not isinstance(facts, list):
        out['reasons'].append(f'facts非列表: {type(facts).__name__}')
        return out
    core_ids = core_metric_ids()
    actives = active_registry_metrics()
    if not core_ids or not actives:
        # 注册表不可用→无法证明核心集合(宁可无法证明,不可虚报)
        out['reasons'].append('注册表不可用——无法重算核心集合(不得放行)')
        return out
    # FIX4-01: 研究截止(观测日不得晚于它)。取research_as_of日期部分;
    # 缺失时退target_date;两者皆缺→截止不可核验(fail-closed,不得放行)。
    cutoff = None
    as_of = snapshot.get('research_as_of')
    tgt = snapshot.get('target_date')
    if isinstance(as_of, str) and as_of.strip():
        try:
            cutoff = _date_cls.fromisoformat(as_of[:10])
        except ValueError:
            cutoff = None
    if cutoff is None and isinstance(tgt, str) and len(tgt) >= 8 and tgt[:8].isdigit():
        try:
            cutoff = _date_cls.fromisoformat(f"{tgt[:4]}-{tgt[4:6]}-{tgt[6:8]}")
        except ValueError:
            cutoff = None
    if cutoff is None:
        out['reasons'].append('快照缺research_as_of/target_date——研究截止不可得,'
                              '观测日合法性不可核验(不得放行)')
        return out
    by_id, seen_dup = {}, set()
    for f in facts:
        if not isinstance(f, dict):
            # FIX3-01: 非对象事实(字符串/null/数组)不得被静默跳过后仍当作
            # 完整合格快照——记入illegal_quality并最终判None
            out['illegal_quality'].append(f'<非对象事实:{type(f).__name__}>')
            continue
        mid = f.get('metric_id')
        if not isinstance(mid, str) or not mid.strip():
            # FIX3-01: 事实缺少可识别指标身份→无法归类核缺/核败,整套事实不可证明
            out['illegal_quality'].append(f'<身份缺失事实:metric_id={mid!r}>')
            continue
        m = actives.get(mid)
        qs = f.get('quality_status')
        if m is None:
            # FIX4-01: 未注册/已弃用指标——可保留FAIL诊断记录(不冒充研究事实),
            # 但自报任何有效状态=无注册表身份自宣有效→非法
            if qs == 'FAIL':
                out['non_research_facts'].append(
                    f"{mid}(FAIL诊断记录,未注册/非active,不入有效研究事实)")
            else:
                out['illegal_quality'].append(
                    f"{mid}=未注册/非active指标自报{qs!r}(无注册表身份不得自宣有效)")
            continue
        if mid in by_id:
            seen_dup.add(mid)
            continue
        by_id[mid] = f
        if qs not in FACT_QUALITY:
            out['illegal_quality'].append(f"{mid}={qs!r}")
            continue
        # FIX4-01: 声明有效的事实须通过必要字段/口径结构校验(合法FAIL保留
        # 异常原始值与诊断——已被质量体系隔离,不在此判非法)
        if qs in ('PASS', 'WARN', 'DEGRADED'):
            out['illegal_quality'].extend(fact_structure_problems(f, m, cutoff))
        if qs in ('PASS', 'DEGRADED', 'FAIL'):
            out['counts'][qs] += 1
    out['duplicates'] = sorted(seen_dup)

    # FIX4-03: active非核心指标完全缺失识别(注册表驱动,非硬编码特例)
    sources_status = snapshot.get('sources_status')
    boundary = []
    if not isinstance(sources_status, dict):
        # 显式判断边界: 无来源状态可判时不虚报缺失(快照构建器恒写入该字段;
        # 手工构造的部分dict无此字段→缺失判定不可执行,如实记录)
        boundary.append('快照缺sources_status——非核心缺失判定不可执行(显式边界)')
        sources_status = None
    for mid, m in actives.items():
        if mid in core_ids or mid in by_id:
            continue
        deps = _DERIVED_DEPS.get(mid)
        if deps is not None:
            # 派生: 输入缺席→归因性缺席(不计);输入齐全而缺席→计缺失。
            # 数值条件镜像compute_derived(仅输入有数值才可能生成派生);
            # NFP_MOM_K还须NFP序列m1可算(镜像compute_derived条件)。
            inputs_ok = all(
                d in by_id and isinstance(by_id[d].get('value'), (int, float))
                and not isinstance(by_id[d].get('value'), bool)
                for d in deps)
            if mid == 'NFP_MOM_K' and inputs_ok:
                m1 = (by_id['NFP'].get('derived') or {}).get('m1') or {}
                inputs_ok = m1.get('abs_change') is not None
            if not inputs_ok:
                continue   # 归因于输入缺席(输入自身已按其规则披露)
            reason = '派生输入齐全而派生事实未生成'
        else:
            src_input = _SOURCE_TO_INPUT.get(m.get('source'))
            if src_input is None:
                # 显式判断边界: 注册表来源无法映射到采集通道——不编造预期
                boundary.append(f"{mid}:来源{m.get('source')!r}无法映射采集通道,"
                                '不入缺失判定(边界如实记录)')
                continue
            if sources_status is None:
                continue   # 边界已在上方整体记录
            st = sources_status.get(src_input)
            if isinstance(st, dict) and st.get('status') in ('EXACT', 'FALLBACK'):
                reason = '来源文件在场而指标缺席(采集遗漏)'
            else:
                reason = f'来源文件缺失({src_input}:{(st or {}).get("status", "无状态")})'
        out['noncore_missing'].append(mid)
        out['noncore_missing_detail'][mid] = reason
    out['noncore_missing'].sort()
    if boundary:
        out['noncore_missing_boundary'] = boundary

    for mid in core_ids:
        f = by_id.get(mid)
        if f is None:
            out['core_missing'].append(mid)
        elif f.get('quality_status') == 'FAIL':
            out['core_fail'].append(mid)
        elif f.get('quality_status') not in FACT_QUALITY:
            out['core_fail'].append(mid)   # 记录性点名(结构非法已同时判None)
    for mid, f in by_id.items():
        if mid in core_ids:
            continue
        qs = f.get('quality_status')
        # FIX3-01: 非法质量只进illegal_quality(→None);不再混入noncore_fail
        # 冒充"合法非核心FAIL降级"——那是两种不同语义
        if qs == 'FAIL':
            out['noncore_fail'].append(str(mid))
        elif qs == 'DEGRADED':
            out['noncore_degraded'].append(str(mid))
    out['core_missing'].sort(); out['core_fail'].sort()
    out['noncore_fail'].sort(); out['noncore_degraded'].sort()
    c = out['counts']
    out['overall'] = ('FAIL' if c['FAIL'] else 'DEGRADED' if c['DEGRADED'] else 'PASS')
    if out['illegal_quality']:
        # FIX3-01/FIX4-01 fail-closed: 非法/不可证明结构不得放行任何正式状态
        out['effective'] = None
        out['reasons'].append(
            f"存在非法/不可证明事实结构{len(out['illegal_quality'])}条——"
            '事实集合不可证明,不得作为合格快照放行正式研究: '
            + '; '.join(out['illegal_quality'][:5]))
    elif out['core_missing'] or out['core_fail'] or out['duplicates']:
        out['effective'] = 'FAIL'
    elif c['DEGRADED'] or out['noncore_fail'] or out['noncore_degraded'] \
            or out['noncore_missing']:
        out['effective'] = 'DEGRADED'
    else:
        out['effective'] = 'PASS'
    return out


def gate_status(snapshot):
    """读取快照Gate A状态并以**事实重算**裁决声明一致性
    (IA-P0-1-FIX1 FIX-05 + IA-P0-1-FIX2 FIX2-02收紧)。

    返回(status, reason);status=None 表示不可用——调用方不得将其当作PASS。
    裁决链(任一环失败→None):
    1. 格式: 缺gate_a/状态非法/快照不可解析 → None;
    2. 重算: recompute_gate_a从真实事实+注册表重算权威裁决;结构损坏/事实结构
       非法(FIX3-01: 非对象事实/身份缺失/质量缺失或非法→不可证明)/注册表
       不可用 → None;
    3. 一致性(声明↔重算,任何矛盾=声明不可信→拒绝放行):
       - 声明状态 ≠ 重算effective(如声明DEGRADED但核心实际FAIL、声明PASS但
         核心实际缺失) → None;
       - 声明core_missing/core_fail清单与重算清单不一致(如核心缺失未写入
         core_missing) → None;
       - quality.counts与按事实重计不一致 → None;
       - quality.overall与重计不一致 → None。
    4. 必需质量汇总(FIX3-01/F2-NEW-001: "缺失必要质量汇总字段"不得放行):
       快照必须带quality质量汇总且counts为对象、overall为合法状态——正式
       快照由snapshot_builder+fact_engine生成,汇总恒存在;缺汇总=事实质量
       不可核验,不得放行。
    语义说明(不机械要求overall==status): quality.overall=**全部事实中最严重的
    原始质量等级**(fact_engine.snapshot_quality_grade,非核心FAIL也会拉高它),
    gate_a.status=**是否允许正式研究**(非核心FAIL仅降级)——二者语义不同,
    不直接互比;各自的**声明值**都必须与其自身的重算结果一致。"""
    if not isinstance(snapshot, dict):
        return None, '快照不可解析(非JSON对象)'
    ga = snapshot.get('gate_a')
    if ga is None:
        return None, '快照缺gate_a字段(不得默认PASS)'
    status = ga.get('status') if isinstance(ga, dict) else ga
    if status not in GATES:
        return None, f'Gate A状态非法: {status!r}(合法值{GATES})'
    rec = recompute_gate_a(snapshot)
    if rec['effective'] is None:
        return None, '; '.join(rec['reasons']) or '重算不可用'
    if status != rec['effective']:
        why = []
        if rec['core_missing']:
            why.append(f"核心实际缺失{len(rec['core_missing'])}项"
                       f"({','.join(rec['core_missing'][:4])})")
        if rec['core_fail']:
            why.append(f"核心实际FAIL: {','.join(rec['core_fail'][:4])}")
        if rec['duplicates']:
            why.append(f"重复metric_id: {','.join(rec['duplicates'][:4])}")
        if not why:
            why.append(f"重算为{rec['effective']}")
        return None, (f'声明{status}与事实重算{rec["effective"]}不一致——'
                      + '; '.join(why))
    if isinstance(ga, dict):
        for field, actual, label in (('core_missing', rec['core_missing'], '核心缺失'),
                                     ('core_fail', rec['core_fail'], '核心失败'),
                                     # FIX4-03: 非核心缺失清单同样声明↔重算一致
                                     ('noncore_missing', rec['noncore_missing'],
                                      '非核心缺失')):
            declared = ga.get(field)
            if declared is None:
                continue
            if sorted(map(str, declared)) != actual:
                return None, (f'声明{label}({field})清单与事实重算不一致: '
                              f'声明{sorted(map(str, declared))[:6]} '
                              f'实际{actual[:6]}')
    q = snapshot.get('quality')
    if not isinstance(q, dict):
        return None, '快照缺quality质量汇总(事实质量不可核验,不得放行)'
    if not isinstance(q.get('counts'), dict):
        return None, f"quality.counts缺失/非法(事实质量计数不可核验): {q.get('counts')!r}"
    recounted = {k: q['counts'].get(k) for k in ('PASS', 'DEGRADED', 'FAIL')}
    if recounted != rec['counts']:
        return None, (f"quality.counts与事实重计不一致: 声明{q['counts']} "
                      f"实际{rec['counts']}")
    if q.get('overall') not in GATES:
        return None, f"quality.overall缺失/非法: {q.get('overall')!r}(合法值{GATES})"
    if q['overall'] != rec['overall']:
        return None, (f"quality.overall声明{q['overall']}与事实重计"
                      f"{rec['overall']}不一致")
    return status, ''


def gate_allows_formal_research(status):
    """Gate A允许进入正式研究流程的状态: PASS(正常)/DEGRADED(披露降级)。
    FAIL/None/未知 → False(不得生成合格正式数据包/报告)。"""
    return status in ('PASS', 'DEGRADED')


def gate_reason_desc(snapshot):
    """人读的降级/失败原因摘要(供拒绝信息与披露用)。"""
    if not isinstance(snapshot, dict):
        return '快照不可解析'
    ga = snapshot.get('gate_a') or {}
    parts = []
    if ga.get('core_missing'):
        parts.append('core缺失: ' + ','.join(ga['core_missing'][:8]))
    if ga.get('core_fail'):
        parts.append('core失败: ' + ','.join(ga['core_fail'][:8]))
    if ga.get('noncore_missing'):
        # FIX4-03: 非核心完全缺失进入降级/拒绝原因(进入周报降级披露)
        parts.append('非核心缺失: ' + ','.join(ga['noncore_missing'][:8]))
    q = (snapshot.get('quality') or {}).get('counts') or {}
    if q.get('DEGRADED'):
        parts.append(f"DEGRADED事实{q['DEGRADED']}项")
    if q.get('FAIL'):
        parts.append(f"FAIL事实{q['FAIL']}项")
    return '; '.join(parts) or '未注明'


# ══ 确定性快照版本选择(任务3/任务4) ══════════════════════════════

def _version_of(path):
    """research_snapshot_YYYYMMDD[_vN].json → (ymd, N);base版N=1。非匹配→None。

    IA-P0-1-FIX2(FIX2-04)版本表示唯一化: 修订版仅接受_v2及以上的**规范十进制**
    (无前导零);_v0/_v1/_v00/_v01等非规范表示一律判非法(返回(ymd, None)),
    由选择器整体拒绝当日——可疑候选不得静默忽略后继续选其他版本。"""
    m = re.match(r'research_snapshot_(\d{8})(?:_v(\d+))?\.json$',
                 os.path.basename(path))
    if not m:
        return None
    ymd, vs = m.group(1), m.group(2)
    if vs is None:
        return ymd, 1
    if vs != str(int(vs)) or int(vs) < 2:   # 前导零/0/1 → 非法版本表示
        return ymd, None
    return ymd, int(vs)


def snapshot_candidates(ymd, daily_dir):
    """当日全部快照候选,按版本升序[(版本号, 路径)]。

    非法版本表示(_v0/_v1/_v00等)同样列为候选(版本号None)——选择器必须
    对其整日拒绝,不得当作不存在。"""
    out = []
    for p in glob.glob(os.path.join(str(daily_dir), 'research_snapshot_*.json')):
        v = _version_of(p)
        if v and v[0] == str(ymd):
            out.append((v[1], p))
    return sorted(out, key=lambda t: (t[0] is None, t[0] if t[0] is not None else 0))


def select_snapshot(ymd, daily_dir):
    """确定性选择当日权威快照: 取**最高修订版**(修订版是显式修正,晚于base)。

    - 无候选 → (None, 原因);
    - 任何候选损坏(不可解析/缺snapshot_id/target_date不符/内部身份与文件名版本
      冲突[IA-DEF-007]/**非法版本表示_v0/_v1/_v00[FIX2-04]**/同日重复版本号)
      → (None, 原因)——无法确认哪个版本有效时明确拒绝,不猜测回退,
      可疑候选不得静默忽略后继续选择其他版本;
    返回(snapshot_dict, path)或(None, reason)。"""
    cands = snapshot_candidates(ymd, daily_dir)
    if not cands:
        return None, f'无当日研究快照: research_snapshot_{ymd}*.json'
    bad = []
    snap_by_ver = {}
    for ver, p in cands:
        name = os.path.basename(p)
        if ver is None:
            bad.append(f'{name} 非法版本表示(合法: 无后缀base或_v2及以上规范十进制)')
            continue
        try:
            with open(p, 'r', encoding='utf-8') as f:
                snap = json.load(f)
        except Exception as e:
            bad.append(f'{name} JSON不可解析({e})')
            continue
        if not isinstance(snap, dict) or not snap.get('snapshot_id'):
            bad.append(f'{name} 缺snapshot_id(非有效快照)')
            continue
        # FIX-06(IA-DEF-007): 物理文件名版本 ↔ 内部snapshot_id必须一致
        # (research_snapshot_D_v2.json 内部不得自称 research_snapshot_D)
        expected_id = f"research_snapshot_{ymd}" + (f"_v{ver}" if ver > 1 else "")
        if str(snap.get('snapshot_id')) != expected_id:
            bad.append(f'{name} 内部snapshot_id={snap.get("snapshot_id")!r}与文件名'
                       f'版本不符(应为{expected_id!r})')
            continue
        if str(snap.get('target_date')) != str(ymd):
            bad.append(f'{name} target_date={snap.get("target_date")}≠{ymd}')
            continue
        if ver in snap_by_ver:
            # FIX-06(IA-DEF-007): 同日重复版本号(两个_v2)——无法确定性选择,整体拒绝
            bad.append(f'同日重复版本号v{ver}: {name}与'
                       f'{os.path.basename(snap_by_ver[ver][1])}(拒绝猜测取哪个)')
            continue
        snap_by_ver[ver] = (snap, p)
    if bad:
        return None, ('快照候选存在损坏/非法版本/身份冲突,无法确认有效版本(拒绝猜测): '
                      + '; '.join(bad))
    if not snap_by_ver:
        return None, f'当日快照候选全部无效: research_snapshot_{ymd}*.json'
    ver = max(snap_by_ver)
    snap, path = snap_by_ver[ver]
    return snap, path


def digest_snapshot(snapshot):
    """快照内容指纹(sha256前16位,canonical JSON)。用于数据包/报告与快照的
    精确绑定(同名快照文件被篡改时digest不匹配→拒绝)。"""
    blob = json.dumps(snapshot, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode('utf-8')).hexdigest()[:16]


def digest_file(path):
    """文件**实际字节**指纹(sha256前16位)。FIX-01: 数据包/锚点/prompt的内容
    绑定必须读取实际文件重算,不得直接采用sidecar中声明的摘要值。"""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()[:16]


def _canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


def anchor_quality_problem(info):
    """锚点指标质量门禁(FIX-04共享原语,观察器/状态引擎双侧同口径):
    返回None=可记录;返回问题描述=拒绝进入正式长期观察。
    FAIL→拒绝;quality缺失→拒绝(不得默认合格);非法值→拒绝。
    PASS/DEGRADED(已验证+披露)/WARN(轻度提示)可按既有规则处理。"""
    if not isinstance(info, dict):
        return '锚点记录非对象'
    q = info.get('quality')
    if q is None or str(q).strip() == '':
        return '锚点缺quality字段(不得默认合格进入正式观察)'
    qs = str(q).strip().upper()
    if qs == 'FAIL':
        return '锚点指标质量FAIL(事实引擎校验未通过)'
    if qs not in ANCHOR_QUALITY_OK:
        return f'锚点quality非法: {q!r}(合法值{ANCHOR_QUALITY_OK}或FAIL拒绝)'
    return None


def provenance_of(snapshot, path=None):
    """快照来源元数据(写入数据包/锚点/报告status sidecar)。"""
    status, _reason = gate_status(snapshot)
    return {
        'snapshot_id': snapshot.get('snapshot_id') if isinstance(snapshot, dict) else None,
        'snapshot_file': os.path.basename(path) if path else None,
        'target_date': snapshot.get('target_date') if isinstance(snapshot, dict) else None,
        'research_as_of': snapshot.get('research_as_of') if isinstance(snapshot, dict) else None,
        'gate_a': status,
        'snapshot_digest': digest_snapshot(snapshot) if isinstance(snapshot, dict) else None,
    }


# ══ meta sidecar(数据包/锚点旁挂来源元数据) ═════════════════════

def meta_path_for(json_path):
    """anchors_YYYYMMDD.json → anchors_YYYYMMDD.meta.json;
    data_pack_YYYYMMDD.md → data_pack_YYYYMMDD.meta.json(去扩展名+旁挂)。"""
    root, _ = os.path.splitext(str(json_path))
    return root + '.meta.json'


def write_meta(json_path, meta):
    """原子写meta sidecar(先tmp后replace,防半写状态)。"""
    mp = meta_path_for(json_path)
    tmp = mp + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    os.replace(tmp, mp)
    return mp


def load_meta(json_path):
    """读取meta sidecar;不存在/损坏返回None(调用方按'无来源元数据'处理)。"""
    mp = meta_path_for(json_path)
    if not os.path.exists(mp):
        return None
    try:
        with open(mp, 'r', encoding='utf-8') as f:
            m = json.load(f)
        return m if isinstance(m, dict) else None
    except Exception:
        return None


# ══ 正式周报权威读取(IA-P0-1-FIX3 FIX3-02/F2-NEW-002) ═════════════
# 报告的正式性由**可验证的已发布状态**决定,不得由文件存在/文件名决定:
# 发布事务=候选→Gate B→候选状态(独立文件)→备份→原子替换→原子写主状态,
# "替换已完成、主状态未写入"的中断窗口内,正式文件名下是**未发布**产物。

# 文件名级排除标记: 候选/未验证/标注版/发布备份/临时文件——所有周报目录扫描
# 的唯一口径(不得在各消费点用os.listdir/glob自行手写筛选)
FORMAL_REPORT_EXCLUDES = ('_CANDIDATE', '_UNVALIDATED', '_annotated',
                          '.prev.bak', '.tmp')
_WEEKLY_REPORT_RE = re.compile(r'^weekly_report_(\d{8})\.md$')
FORMAL_FINAL_QUALITIES = ('PASS', 'DEGRADED')


def weekly_report_files(output_dir):
    """列出周报目录下**规范正式文件名**的周报文件(sorted升序)。

    只认 weekly_report_YYYYMMDD.md 精确命名——_CANDIDATE/_UNVALIDATED/
    _annotated/.prev.bak/.tmp 及一切非规范名一律排除(单一口径,消费者共用)。"""
    if not os.path.isdir(output_dir):
        return []
    out = []
    for f in os.listdir(output_dir):
        if not _WEEKLY_REPORT_RE.match(f):
            continue
        out.append(f)
    return sorted(out)


def read_report_status(status_path):
    """读报告发布状态JSON;不存在/损坏/非对象 → None。"""
    if not os.path.exists(status_path):
        return None
    try:
        with open(status_path, 'r', encoding='utf-8') as f:
            st = json.load(f)
        return st if isinstance(st, dict) else None
    except Exception:
        return None


def formal_report_view(md_path):
    """FIX3-02(F2-NEW-002)+FIX4-02(FIX3-NEW-002)权威正式周报读取入口——
    所有正式消费者的统一读法。

    校验链(任一不满足 → (None, 原因),不得作为已合格正式周报使用):
    1. 文件名为规范正式名 weekly_report_YYYYMMDD.md(候选/未验证/标注/备份/
       临时文件天然不匹配);
    2. 同目录存在对应发布状态 report_status_{ymd}.json 且可解析;
    3. published 明确为 True;
    4. final_quality ∈ (PASS, DEGRADED)(已明确允许的降级);
    5. FIX4-02: 状态报告身份**必需字段一律强制**——report_file必须存在且与
       实际文件名一致(缺失=身份不完整,不再容忍None);
    6. FIX4-02: target_date必须存在且与文件名日期一致(缺失=身份不完整);
    7. FIX4-02: report_path必须存在,且经realpath标准化后与实际读取路径一致
       ——指向其他目录/另一报告/被移动的报告在此被拒;同一文件的相对/绝对/
       ".."别名等价路径经标准化后放行(不得因路径别名误拒,亦不得借别名冒充)。
       路径兼容规则以_status_body真实写入行为为准:发布时写入的就是正式文件
       的完整路径(os.path.join(OUTPUT_DIR, weekly_report_ymd.md));
    8. 实际报告内容摘要(重算)与状态记录report_digest一致——发布中途被替换
       /中断窗口内的未发布产物在此被拒。
    旧状态若缺身份字段,只能走latest_archive_weekly_report未验证档案机制,
    不得冒充正式合格产物(本轮不为兼容不完整旧状态默认放行)。
    返回({'ymd','path','status'}, '') 或 (None, reason)。"""
    md_path = str(md_path)
    fname = os.path.basename(md_path)
    m = _WEEKLY_REPORT_RE.match(fname)
    if not m:
        return None, f'非规范正式周报文件名: {fname}'
    ymd = m.group(1)
    if not os.path.exists(md_path):
        return None, f'报告文件不存在: {fname}'
    st = read_report_status(os.path.join(os.path.dirname(md_path),
                                         f'report_status_{ymd}.json'))
    if st is None:
        return None, f'无有效发布状态 report_status_{ymd}.json(未发布/状态损坏)'
    if st.get('published') is not True:
        return None, (f"发布状态published={st.get('published')!r}"
                      f"(final={st.get('final_quality')!r})——未完成发布")
    if st.get('final_quality') not in FORMAL_FINAL_QUALITIES:
        return None, (f"final_quality={st.get('final_quality')!r}∉"
                      f"{FORMAL_FINAL_QUALITIES}——非合格正式报告")
    # FIX4-02: 身份字段强制(缺失即拒,不再把None当作"未记录则跳过")
    if st.get('report_file') != fname:
        return None, (f"状态报告身份缺失或不符: report_file={st.get('report_file')!r}"
                      f',实际文件={fname!r}')
    td = st.get('target_date')
    if td is None or str(td) != ymd:
        return None, (f"状态target_date缺失或与文件名日期不一致: {td!r} vs {ymd}")
    rp_path = st.get('report_path')
    if not isinstance(rp_path, str) or not rp_path.strip():
        return None, '状态缺report_path(报告路径身份不可核验)'
    if os.path.realpath(rp_path) != os.path.realpath(md_path):
        return None, (f'状态report_path({rp_path})与实际读取路径({md_path})'
                      '不一致(指向其他目录/另一报告/报告已被移动)')
    try:
        digest = digest_file(md_path)
    except OSError as e:
        return None, f'报告内容不可读: {e}'
    if not st.get('report_digest') or digest != st.get('report_digest'):
        return None, ('实际内容摘要与发布状态记录不一致'
                      '(发布中途被替换/写入不完整/中断产物)')
    return {'ymd': ymd, 'path': md_path, 'status': st}, ''


def scan_formal_weekly_reports(output_dir):
    """扫描目录内全部**已发布合格**正式周报(逐个过formal_report_view),
    返回views列表(按日期降序)。任何未发布/损坏/中断产物不入列。"""
    views = []
    for f in weekly_report_files(output_dir):
        view, _r = formal_report_view(os.path.join(output_dir, f))
        if view:
            views.append(view)
    views.sort(key=lambda v: v['ymd'], reverse=True)
    return views


def latest_formal_weekly_report(output_dir, exclude_ymd=None):
    """最新一份**已发布合格**正式周报(排除exclude_ymd当日)。
    返回(view, '')或(None, 原因)。"""
    for view in scan_formal_weekly_reports(output_dir):
        if exclude_ymd and view['ymd'] == str(exclude_ymd):
            continue
        return view, ''
    return None, '无已发布合格正式周报'


def latest_archive_weekly_report(output_dir, exclude_ymd=None):
    """历史档案回退(FIX3-02): 无任何已发布合格报告时的**未验证档案**最新一份。

    仅做规范文件名筛选(排除候选/未验证/标注/备份/临时);返回文件名或None。
    调用方必须将结果显式标注为"未验证历史档案",不得静默赋予合格认证。"""
    cands = [f for f in weekly_report_files(output_dir)
             if not (exclude_ymd and _WEEKLY_REPORT_RE.match(f)
                     and _WEEKLY_REPORT_RE.match(f).group(1) == str(exclude_ymd))]
    for f in reversed(cands):
        view, _r = formal_report_view(os.path.join(output_dir, f))
        if not view:
            # 已排除formal(否则直接用formal)——档案仅剩无有效状态者
            return f
    return None


# ══ Gate A / Gate B 合成(任务6) ═════════════════════════════════

def combine_gates(gate_a, gate_b):
    """正式报告最终质量等级(确定性规则):
    任一门禁FAIL(或状态未知/非法)→FAIL;无FAIL但有DEGRADED→DEGRADED;
    两门禁全PASS→PASS。未知状态按FAIL处理——不得默认通过。"""
    if gate_a not in GATES or gate_b not in GATES:
        return 'FAIL'
    if 'FAIL' in (gate_a, gate_b):
        return 'FAIL'
    if 'DEGRADED' in (gate_a, gate_b):
        return 'DEGRADED'
    return 'PASS'


# ══ 锚点批次核验(观察器/报告入口共用) ═══════════════════════════

def verify_meta_gate_a(meta, snap, label='meta'):
    """FIX3-03(F2-NEW-003): 来源meta声明的gate_a必须与**权威快照重算**Gate A一致。

    统一口径(锚点端verify_anchor_batch与数据包端verify_research_inputs共用,
    不得两套标准):
    1. 字段必须存在且非空(缺必需来源字段=无法验证,不得跳过);
    2. 必须属于合法状态(GATES);
    3. 权威=gate_status(snap)——内部以recompute_gate_a从真实facts+注册表重算,
       **不信任快照声明值,更不信任meta自报值**;快照不可重算(含事实结构非法,
       FIX3-01)→声明值不得作为权威;
    4. 声明==权威;且权威∈(PASS,DEGRADED)才允许正式链路。
    返回(True, '')或(False, reason)。"""
    declared = meta.get('gate_a')
    if declared in (None, ''):
        return False, f'{label}缺gate_a声明(必需来源字段,缺失即拒——无法验证批次质量口径)'
    if declared not in GATES:
        return False, f'{label}.gate_a非法: {declared!r}(合法值{GATES})'
    auth, why = gate_status(snap)
    if auth is None:
        return False, (f'{label}.gate_a={declared!r}对应权威快照Gate A不可重算'
                       f'({why})——非法/不可证明快照的声明值不得作为权威')
    if declared != auth:
        return False, (f'{label}.gate_a={declared!r}与权威快照Gate A={auth!r}'
                       '不一致(批次生成后被改写或meta陈旧)')
    if auth not in ('PASS', 'DEGRADED'):
        return False, f'权威快照Gate A={auth!r}不允许正式链路({label})'
    return True, ''


def verify_anchor_batch(anchors_path, anchors_date=None, daily_dir=None):
    """核验锚点文件批次一致性+**实际内容**(FIX-01/FIX-04,IA-DEF-001/005;
    FIX2-05必需字段完整一致)。

    核验链(任一环失败即拒绝,返回(False, reason);全部通过返回(True, '')):
    1. meta存在且source=snapshot(legacy/无meta/未知来源→拒绝——正式观察与
       报告输入必须可证明来源,FIX-04: 无来源证明不得进入正式长期观察);
    2. 日期三方一致(FIX2-05): 请求日期(anchors_date,如给)↔meta.target_date↔
       锚点**文件名**日期——meta自报错误日期/文件名与批次日期不符均拒绝
       (旧实现`anchors_date or meta.target_date`在调用方传日期时跳过meta日期核对);
    3. 必需来源字段完整(FIX2-05): snapshot_id/snapshot_digest/anchors_digest/
       gate_a缺一即拒——必需摘要缺失=无法验证内容,不得"缺字段跳过校验";
    4. 声明批次 = 当日确定性选择的权威快照(snapshot_id一致,同日修订后旧批次失配);
       meta.gate_a与权威快照重算Gate A一致(FIX3-03统一口径verify_meta_gate_a);
    5. meta声明的快照digest与权威快照实际内容digest一致;
       meta声明的锚点内容摘要与锚点文件**实际字节**摘要一致(重算,不信任声明值);
    6. 锚点实际内容与权威快照**确定性重建**结果一致(build_anchors为快照纯函数:
       键集合/数值/高低点/观测日任何偏差、额外残留指标、版本混用均失配)。
    """
    anchors_path = str(anchors_path)
    meta = load_meta(anchors_path)
    if not meta:
        return False, (f'锚点无来源meta({os.path.basename(anchors_path)})——'
                       '来源不可证明,不得进入正式观察/报告(FIX-04)')
    src = str(meta.get('source') or '')
    if src == 'legacy':
        return False, ('锚点批次来源=legacy(原始采集JSON拍平,未经Gate A快照链验证),'
                       '不得用于正式观察/报告')
    if src != 'snapshot':
        return False, f'锚点meta来源未知: {src!r}'
    # FIX2-05: 日期三方一致——meta必须自带target_date,且与请求日期/文件名一致
    meta_ymd = str(meta.get('target_date') or '')
    if not re.match(r'^\d{8}$', meta_ymd):
        return False, f'锚点meta缺target_date(必需来源字段): {meta_ymd!r}'
    ymd = meta_ymd
    if anchors_date is not None and str(anchors_date) != ymd:
        return False, (f'锚点meta日期与请求日期冲突: meta={ymd} '
                       f'请求={anchors_date}(批次来源不可信)')
    fname = os.path.basename(anchors_path)
    if fname != f'anchors_{ymd}.json':
        return False, f'锚点文件名日期与批次日期不符: {fname} ≠ anchors_{ymd}.json'
    # FIX2-05: 必需来源字段——缺失即拒(不得跳过对应校验)
    for field in ('snapshot_id', 'snapshot_digest', 'anchors_digest', 'gate_a'):
        if meta.get(field) in (None, ''):
            return False, f'锚点meta缺必需来源字段: {field}(无法验证来源与内容)'
    dd = daily_dir or os.path.dirname(anchors_path)
    snap, reason = select_snapshot(ymd, dd)
    if snap is None:
        return False, f'锚点声明的快照批次无法确认: {reason}'
    if snap.get('snapshot_id') != meta.get('snapshot_id'):
        return False, (f"数据批次不一致: 锚点绑定{meta.get('snapshot_id')},"
                       f"当日权威快照为{snap.get('snapshot_id')}(同日修订后旧锚点不得续用)")
    # FIX3-03: gate_a声明核验收敛到统一口径verify_meta_gate_a(与数据包端同规则)
    ok_gate, gate_reason = verify_meta_gate_a(meta, snap, label='锚点meta')
    if not ok_gate:
        return False, gate_reason
    if meta.get('snapshot_digest') != digest_snapshot(snap):
        return False, ('锚点meta声明的快照digest与权威快照实际内容不一致'
                       '(快照被改写或meta陈旧)')
    if meta.get('anchors_digest') != digest_file(anchors_path):
        return False, ('锚点实际内容与meta声明摘要不一致(疑被篡改/写入不完整)')
    # 确定性重建比对: 从权威快照重算锚点,与实际内容canonical比较
    try:
        import snapshot_builder as sb
        expected = sb.build_anchors(snap, ymd)
    except Exception as e:
        return False, f'锚点重建比对失败(无法证明内容一致): {e}'
    try:
        with open(anchors_path, 'r', encoding='utf-8') as f:
            actual = json.load(f)
    except Exception as e:
        return False, f'锚点文件不可读取: {e}'
    if not isinstance(actual, dict) or _canonical(actual) != _canonical(expected):
        extra = (sorted(set(actual) - set(expected))[:6] if isinstance(actual, dict) else [])
        detail = (f';实际多出残留键: {extra}' if extra else
                  (f';实际缺键{len(set(expected) - set(actual))}个'
                   if isinstance(actual, dict) else ''))
        return False, ('锚点实际内容与权威快照重建结果不一致'
                       '(数值被改/指标集合变动/残留旧指标/批次混用)' + detail)
    return True, ''


def verify_anchor_prompt(prompt_path, anchors):
    """锚点prompt实际内容核验(FIX-01): prompt由锚点确定性渲染
    (data_validator.generate_anchor_prompt_block为锚点纯函数),从**已核验**锚点
    重建并与文件实际内容比对——prompt中数字被替换/内容陈旧即拒绝。
    返回(ok, reason)。"""
    try:
        from data_validator import generate_anchor_prompt_block
    except Exception as e:
        return False, f'prompt渲染器不可用: {e}'
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            actual = f.read()
        expected = generate_anchor_prompt_block(anchors)
    except Exception as e:
        return False, f'prompt读取/重建失败: {e}'
    if actual.strip() != expected.strip():
        return False, ('锚点prompt实际内容与当日锚点重建结果不一致'
                       '(prompt被改写或锚点批次已变更)')
    return True, ''
