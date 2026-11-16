#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R23 阶段四(Charter 10 §六)Agent Native L3/L4 落位与纪律机器校验。

架构分工(§6.1/§6.2,红线):
- Python=确定性引擎: 本模块**只做校验与落位,绝不生成任何判断内容**——
  L3(矛盾综合/推断)与 L4(条件情景)的每个字都来自 Agent 提交的 judgment
  文件;校验器对内容零改写(原文入档),只验证纪律结构是否齐备。
- Agent=经济学判断: Agent 在兼容环境(Claude Code 等)内读完
  research-run 确定性证据面(L1 事实/L2 观点/证据索引)后撰写 judgment,
  经本校验器机器核纪律,attach 合并进报告,L3/L4 produced=True,
  attribution=ai_inferred(永非 institution_stated——机构明示面归 views 库)。

机器可查纪律子集(Skill 纪律 4/15/16 的结构面;判断质量归 Agent 与独立审计)。
已知边界: "假设"采用子串代理(与 E2 检查同口径)——"非假设"类对抗措辞含该
子串会漏拦,语义面归 Skill lint 与独立审计,不在本校验器伪装语义理解:
- ATTR    attribution 必须 ai_inferred(防 Agent 成果冒充机构观点)
- CON-EXP 每条矛盾陈述须并列 >=2 竞争性解释(纪律 4)
- CON-REF 每条矛盾陈述须 >=1 可解析证据引用,或明示免锚
          (no_anchor_reason 非空=R23 审计 MINOR-1: 零引用放行会割裂
          结论-证据绑定;免锚必须显式声明理由,不许静默零锚)
- REF     所有 evidence_refs 必须解析到**本报告证据索引**内的 fact_id/VP id
          (结论-证据绑定,R22 5.3 同源纪律;悬空引用拒收)
- E1-REF  E1 环(引擎直接可验证)须带 >=1 可解析证据引用
- E2-ASSUM E2 环须明写缺失环【假设】(missing_link_note 含"假设")
- E3-FALS E3 环(纯叙事)须给证伪指标(注册表在册 metric_id)
- SCN-FIVE 每情景五行齐备(情景/资产方向判断/敏感变量/证伪指标/触发条件)
- SCN-TYPE 五行类型锁(R23 审计 NIT: scenario=str/asset_direction=dict/
          sensitive_variables=list/falsification=dict/trigger=dict——
          错型原先静默绕过下游检查,现在显式拒收)
- SCN-ASSUM 情景行须含"假设"(明写假设非预测)
- SCN-DIR 资产方向判断=方向+置信层级(三档枚举: 有历史相似证据/有相关证据/纯逻辑推理)
- SCN-SENS 敏感变量 1-2 个且均为注册表在册 metric_id
- SCN-FALS 证伪指标=在册 metric_id+可观测阈值非空
- SCN-FALS2 复合证伪条件可选副指标(v1.1/R25 NIT V2-5): threshold 文本
          提及多指标时,主 metric_id 之外的指标可经 secondary_metric_ids
          (list,1-3 条,逐条在册)机器锚定——复合条件不再"可读但口径不对称";
          缺席不违规(单指标条件不需要),主锚仍由 metric_id 承担
- SCN-TRIG 触发条件=可观测条件+时限(YYYY-MM-DD)
- SCN-PLURAL >=2 情景并列(基准+反例;单一情景不得单独呈现)

入口: validate_judgment(judgment, evidence_refs, metric_ids) → dict;
      attach_judgment(report_dir, judgment_path, root=None) → dict(校验不过
      则 produced 保持 False,violations 落档,绝不半落位)。
"""
import copy
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
SCRIPTS = os.path.join(ROOT, 'scripts')
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

JUDGMENT_SCHEMA_VERSION = '1.1'   # v1.0(R23)→v1.1(R25): falsification 增可选 secondary_metric_ids(复合证伪条件副指标锚)
CONFIDENCE_TIERS = ('有历史相似证据', '有相关证据', '纯逻辑推理')
ASSUMPTION_MARK = '假设'
_DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')

SCENARIO_ROWS = ('scenario', 'asset_direction', 'sensitive_variables',
                 'falsification', 'trigger')


def _now_utc():
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def _load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def validate_judgment(judgment, evidence_refs, metric_ids):
    """纪律结构校验(内容零改写零生成)。

    judgment: Agent 提交的 dict(schema v1.1);evidence_refs: 本报告证据索引
    ref 集合(set);metric_ids: 注册表在册 metric_id 集合(set)。
    返回 {'passed', 'violations': [(code, where, detail)], 'n_*'}。
    """
    v = []

    def bad(code, where, detail=''):
        v.append({'code': code, 'where': where, 'detail': detail})

    ev = set(evidence_refs or ())
    mids = set(metric_ids or ())

    # ── 结构与归因 ──────────────────────────────────────────────
    if not isinstance(judgment, dict):
        return {'passed': False,
                'violations': [{'code': 'SCHEMA', 'where': 'root',
                                'detail': 'judgment 非 object'}],
                'n_contradictions': 0, 'n_mechanism_chains': 0,
                'n_scenarios': 0}
    if judgment.get('schema_version') != JUDGMENT_SCHEMA_VERSION:
        bad('SCHEMA', 'schema_version',
            f"须为 {JUDGMENT_SCHEMA_VERSION}(得 {judgment.get('schema_version')!r})")
    decl = judgment.get('agent_declaration') or {}
    if decl.get('attribution') != 'ai_inferred':
        bad('ATTR', 'agent_declaration.attribution',
            f"须 ai_inferred(得 {decl.get('attribution')!r})——Agent 成果"
            '永不得标 institution_stated(机构明示面归 views 库)')

    def refs_ok(where, refs):
        """evidence_refs 逐条解析;返回是否全解析。"""
        ok = True
        for r in (refs or []):
            if r not in ev:
                bad('REF', where, f'悬空证据引用 {r!r}(不在本报告证据索引)')
                ok = False
        return ok

    # ── L3 矛盾综合(纪律 4: 四层标注+竞争性解释并列) ──────────────
    l3 = judgment.get('l3') or {}
    contras = l3.get('contradictions') or []
    if not contras:
        bad('SCHEMA', 'l3.contradictions',
            'L3 须至少 1 条矛盾/综合陈述(无判断内容=无可落位)')
    for c in contras:
        cid = c.get('id') or '?'
        if not (c.get('statement') or '').strip():
            bad('SCHEMA', f'l3.contradictions[{cid}].statement', '陈述为空')
        exps = c.get('competing_explanations') or []
        if len(exps) < 2:
            bad('CON-EXP', f'l3.contradictions[{cid}].competing_explanations',
                f'竞争性解释须 >=2 并列(得 {len(exps)};纪律 4: 数据同样'
                '容纳的其他解释至少列一种)')
        # R23 审计 MINOR-1: 零引用矛盾不再静默放行——须 >=1 可解析引用,
        # 或显式声明免锚理由(no_anchor_reason 非空;渲染面随之披露)
        if not (c.get('evidence_refs') or []):
            if not (c.get('no_anchor_reason') or '').strip():
                bad('CON-REF', f'l3.contradictions[{cid}].evidence_refs',
                    '矛盾陈述须 >=1 可解析证据引用,或以 no_anchor_reason '
                    '非空明示免锚(静默零锚=割裂结论-证据绑定)')
        refs_ok(f'l3.contradictions[{cid}].evidence_refs',
                c.get('evidence_refs'))

    # ── L3 机制链(纪律 15: E1/E2/E3) ────────────────────────────
    chains = l3.get('mechanism_chains') or []
    for ch in chains:
        chid = ch.get('id') or '?'
        links = ch.get('links') or []
        if not links:
            bad('SCHEMA', f'l3.mechanism_chains[{chid}].links', '机制链空')
        for lk in links:
            lid = f'{chid}.link{lk.get("step", "?")}'
            lvl = lk.get('evidence_level')
            if lvl not in ('E1', 'E2', 'E3'):
                bad('SCHEMA', f'l3…[{lid}].evidence_level',
                    f'须 E1/E2/E3(得 {lvl!r})')
                continue
            if lvl == 'E1':
                refs = lk.get('evidence_refs') or []
                if not refs or not refs_ok(
                        f'l3.mechanism_chains[{lid}].evidence_refs', refs):
                    bad('E1-REF', f'l3.mechanism_chains[{lid}]',
                        'E1 环(引擎直接可验证)须带 >=1 可解析证据引用')
            elif lvl == 'E2':
                note = lk.get('missing_link_note') or ''
                if ASSUMPTION_MARK not in note:
                    bad('E2-ASSUM', f'l3.mechanism_chains[{lid}]',
                        'E2 环须明写缺失环【假设】(missing_link_note 含"假设")')
                refs_ok(f'l3.mechanism_chains[{lid}].evidence_refs',
                        lk.get('evidence_refs'))
            else:  # E3
                fm = lk.get('falsification_metric')
                if fm not in mids:
                    bad('E3-FALS', f'l3.mechanism_chains[{lid}]',
                        f'E3 环须给注册表在册证伪指标(得 {fm!r})')

    # ── L4 条件情景(纪律 16: 五行强制+并列) ──────────────────────
    l4 = judgment.get('l4') or {}
    scenarios = l4.get('scenarios') or []
    if len(scenarios) < 2:
        bad('SCN-PLURAL', 'l4.scenarios',
            f'须 >=2 情景并列(基准+反例;得 {len(scenarios)};单一情景'
            '不得单独呈现)')
    for s in scenarios:
        sid = s.get('id') or '?'
        rows = s.get('rows') or {}
        for rname in SCENARIO_ROWS:
            if not rows.get(rname):
                bad('SCN-FIVE', f'l4.scenarios[{sid}].rows.{rname}',
                    '五行缺一不可(纪律 16)')
        # R23 审计 NIT: 五行类型锁——错型(如 scenario 传 dict)原先静默
        # 绕过 SCN-ASSUM/SCN-DIR 等下游检查,现在显式拒收
        ROW_TYPES = {'scenario': str, 'asset_direction': dict,
                     'sensitive_variables': list, 'falsification': dict,
                     'trigger': dict}
        type_bad = set()
        for rname, rtype in ROW_TYPES.items():
            rv = rows.get(rname)
            if rv and not isinstance(rv, rtype):
                bad('SCN-TYPE', f'l4.scenarios[{sid}].rows.{rname}',
                    f'类型须 {rtype.__name__}(得 {type(rv).__name__})')
                type_bad.add(rname)
        scen_text = (rows.get('scenario') or '') if isinstance(
            rows.get('scenario'), str) else ''
        if scen_text and ASSUMPTION_MARK not in scen_text:
            bad('SCN-ASSUM', f'l4.scenarios[{sid}].rows.scenario',
                '情景行须含"假设"(明写假设非预测)')
        ad = rows.get('asset_direction') or {}
        if 'asset_direction' not in type_bad and isinstance(ad, dict):
            if not (ad.get('direction') or '').strip():
                bad('SCN-DIR', f'l4.scenarios[{sid}].rows.asset_direction.direction',
                    '方向判断为空')
            if ad.get('confidence_tier') not in CONFIDENCE_TIERS:
                bad('SCN-DIR',
                    f'l4.scenarios[{sid}].rows.asset_direction.confidence_tier',
                    f'置信层级须三档之一 {CONFIDENCE_TIERS}'
                    f'(得 {ad.get("confidence_tier")!r})')
            refs_ok(f'l4.scenarios[{sid}].rows.asset_direction.evidence_refs',
                    ad.get('evidence_refs'))
        sens = rows.get('sensitive_variables') or []
        if 'sensitive_variables' not in type_bad:
            if sens and not (1 <= len(sens) <= 2):
                bad('SCN-SENS', f'l4.scenarios[{sid}].rows.sensitive_variables',
                    f'敏感变量须 1-2 个(得 {len(sens)})')
            for m in sens:
                if m not in mids:
                    bad('SCN-SENS', f'l4.scenarios[{sid}].rows.sensitive_variables',
                        f'{m!r} 不在注册表(须引擎可观测指标)')
        fals = rows.get('falsification') or {}
        if ('falsification' not in type_bad
                and isinstance(fals, dict) and fals):
            if fals.get('metric_id') not in mids:
                bad('SCN-FALS', f'l4.scenarios[{sid}].rows.falsification.metric_id',
                    f'{fals.get("metric_id")!r} 不在注册表(证伪指标须可观测)')
            if not (fals.get('threshold') or '').strip():
                bad('SCN-FALS', f'l4.scenarios[{sid}].rows.falsification.threshold',
                    '可观测阈值为空')
            # R25 NIT V2-5(R24 审计): 复合证伪条件副指标锚(可选;v1.1)。
            # threshold 文本可提及多指标,主锚=metric_id;其余指标经本字段
            # 机器可验,消除"可读但口径不对称"。缺席=单指标条件,不违规。
            sec = fals.get('secondary_metric_ids')
            if sec is not None:
                if not isinstance(sec, list) or not sec:
                    bad('SCN-FALS2',
                        f'l4.scenarios[{sid}].rows.falsification.'
                        'secondary_metric_ids',
                        '副指标须非空 list(单指标条件直接省略本字段)')
                elif not (1 <= len(sec) <= 3):
                    bad('SCN-FALS2',
                        f'l4.scenarios[{sid}].rows.falsification.'
                        'secondary_metric_ids',
                        f'副指标 1-3 条(得 {len(sec)};主锚仍由 metric_id 承担)')
                else:
                    for sm in sec:
                        if sm not in mids:
                            bad('SCN-FALS2',
                                f'l4.scenarios[{sid}].rows.falsification.'
                                'secondary_metric_ids',
                                f'{sm!r} 不在注册表(副指标同须可观测)')
                    # R36 Ni-4(R25 审计遗留): 重复=口径冗余,契约明示拒
                    # (不静默去重——审计可选"去重或明示",本仓纪律=显式)。
                    # 与主锚重复: 主锚由 metric_id 承担,副表再列=同指标
                    # 双口径;内部重复: 列表语义是集合,重复=凑数或笔误。
                    anchor_dup = fals.get('metric_id')
                    if anchor_dup in sec:
                        bad('SCN-FALS2',
                            f'l4.scenarios[{sid}].rows.falsification.'
                            'secondary_metric_ids',
                            f'{anchor_dup!r} 与主锚 metric_id 重复'
                            '(主锚已由 metric_id 承担,副表列其余指标)')
                    for d in sorted({m for m in sec if sec.count(m) > 1}):
                        bad('SCN-FALS2',
                            f'l4.scenarios[{sid}].rows.falsification.'
                            'secondary_metric_ids',
                            f'{d!r} 在副指标列表内重复(去重后再提)')
        trig = rows.get('trigger') or {}
        if 'trigger' not in type_bad and isinstance(trig, dict) and trig:
            if not (trig.get('condition') or '').strip():
                bad('SCN-TRIG', f'l4.scenarios[{sid}].rows.trigger.condition',
                    '可观测条件为空')
            dl = trig.get('deadline') or ''
            # R23 MINOR-2(独立审计): 真日期校验,防 '2027-13-45' 类过纯正则
            try:
                datetime.strptime(str(dl), '%Y-%m-%d')
            except ValueError:
                bad('SCN-TRIG', f'l4.scenarios[{sid}].rows.trigger.deadline',
                    f'时限须真日期 YYYY-MM-DD(得 {dl!r})')

    return {'passed': not v, 'violations': v,
            'n_contradictions': len(contras),
            'n_mechanism_chains': len(chains),
            'n_scenarios': len(scenarios)}


def _registry_metric_ids(root):
    import workbench_data as wd
    reg = wd.load_registry(root)
    return {m.get('metric_id') for m in (reg.get('metrics') or [])
            if m.get('metric_id')}


def _canonical(obj):
    """稳定规范化 JSON 串(跨 CPython 3.9-3.12 同文同串)。"""
    return json.dumps(obj, sort_keys=True, ensure_ascii=True,
                      separators=(',', ':'), default=str)


# Audit-R2 条目1: 摘要边界内须剥离的易变键(审查机制自身状态面,
# 写入即变——不剥离则裁决落档自噬;其余键全在摘要内,含 attach 台账
# 与版本指针 run.git_head/pipeline_version——重 attach/换引擎版本即
# 失效旧裁决,任一交付输入变化不得沿用旧审查)
_DIGEST_VOLATILE_REPORT_KEYS = ('semantic_review',)
_DIGEST_VOLATILE_JUDGMENT_KEYS = ('semantic_review',)


def content_digest(report_dir, judgment_path=None):
    """Audit-R2 条目1: 唯一规范化内容来源=report.json(审查与渲染同源)。

    边界(稳定,禁漂移): canonical(report.json, 剥离易变键 semantic_review)
    + NUL + canonical(agent_judgment.json, 剥离 semantic_review)。
    研究事实(L1/L2)、L3/L4 判断、run_ok、运行元数据、attach 台账、
    版本指针(run.git_head/pipeline_version/快照 id)全在摘要内——
    只改 report.json 的事实/结论/运行状态即失效旧裁决(Audit-R2 反例①)。
    report.md/FULL_REPORT=report.json 的渲染视图,**不入摘要**;视图与
    源的一致性由交付门 copies_consistent 核对(_r1_report_core)——
    审查绑定的与交付渲染的是同一份规范化内容。
    裁决档自身(VERDICT-*.json)不在 report_dir 内,天然不在边界
    (Audit-R1 F02 循环依赖切断面保留)。
    """
    import hashlib
    rp = _load_json(os.path.join(report_dir, 'report.json'))
    for k in _DIGEST_VOLATILE_REPORT_KEYS:
        rp.pop(k, None)
    if judgment_path is None:
        for cand in ('agent_judgment.json', 'judgment_mvp.json'):
            p = os.path.join(report_dir, cand)
            if os.path.isfile(p):
                judgment_path = p
                break
    j = _load_json(judgment_path)
    for k in _DIGEST_VOLATILE_JUDGMENT_KEYS:
        j.pop(k, None)
    return hashlib.sha256(
        (_canonical(rp) + '\x00' + _canonical(j)).encode('utf-8')).hexdigest()


def content_digest_v1(report_dir, judgment_path=None):
    """Audit-R1 旧口径(judgment + report.md 全文)——仅存续供裁决重绑
    迁移验证旧锚(rebind_verdict_digest),不得用于新裁决绑定。"""
    import hashlib
    if judgment_path is None:
        for cand in ('agent_judgment.json', 'judgment_mvp.json'):
            p = os.path.join(report_dir, cand)
            if os.path.isfile(p):
                judgment_path = p
                break
    j = _load_json(judgment_path)
    j.pop('semantic_review', None)
    md = open(os.path.join(report_dir, 'report.md'), encoding='utf-8').read()
    return hashlib.sha256((_canonical(j) + '\x00' + md).encode('utf-8')
                          ).hexdigest()


# Audit-R1 F02: 独立审查可放行档(裁决语汇——席位其余语汇一律不放行)
REVIEW_APPROVED_VERDICTS = ('VERIFIED', 'PASS', 'UPHELD')

# Audit-R2 条目2: 裁决档必填字段(缺任一=损坏档,最新档损坏即阻断,
# 不回退旧 PASS)
VERDICT_REQUIRED_FIELDS = ('overall', 'reviewer', 'run_ts', 'recorded_at')

# R32 席位词表(Audit-R2 收口): 语义审查席裁决档只认章程四词。与四态门
# 放行词(REVIEW_APPROVED_VERDICTS)是两张表——席位席报告词 VERIFIED/PASS
# 须映射为 UPHELD 后落档(同义,-01 档先例),越表词落档即抛(B3 机核面)。
SEAT_VERDICT_VOCAB = ('UPHELD', 'REVISE', 'NOT_VERIFIED', 'REJECT_ENTRY')


def _verdicts_for_run(root, run_ts):
    """按 run_ts 收全裁决档(跨日目录,run_ts 在文件名内)。

    返回 [(path, doc)];doc=None=不可解析(损坏档如实入列,不静默丢)。
    """
    import glob as _glob
    out = []
    for p in sorted(_glob.glob(os.path.join(
            root, 'audit', 'semantic_review', '*', 'VERDICT-*.json'))):
        if run_ts not in os.path.basename(p):
            continue
        try:
            v = _load_json(p)
            if not isinstance(v, dict):
                v = None
        except Exception:
            v = None
        out.append((p, v))
    return out


def _verdict_sort_key(path, doc):
    """裁决内容序(非 mtime): (代, revision, 日目录, 文件名 seq)。

    Audit-R2 条目2: 排序只读档**内容与稳定文件名**——revision=新档全局
    单调序号(record_semantic_verdict 按在档全数+1 赋号,跨日目录不归零);
    legacy 档(无 revision 键,含不可解析损坏档)以日目录+文件名序号兜底
    (写入序的事实承载),恒排新档前。损坏档排序不塌向链首——按文件名
    序仍可居链尾,最新位损坏即阻断,不得跳过错误记录回退旧 PASS。
    mtime 不参与: 调换裁决文件 mtime,状态面结果不得变化。
    """
    rev = (doc or {}).get('revision')
    if isinstance(rev, int) and rev > 0:
        return (1, rev, '', '', '')
    day = os.path.basename(os.path.dirname(path))
    name = os.path.basename(path)
    seq = ''
    m = re.search(r'-(\d+)\.json$', name)
    if m:
        seq = '%06d' % int(m.group(1))
    return (0, 0, day or '00000000', seq, name)


def record_semantic_verdict(root, report_dir, overall, reviewer,
                            notes='', extra=None):
    """Audit-R1 F02 + Audit-R2 条目2: 独立席裁决落档(append-only,带内容绑定)。

    写 root/audit/semantic_review/<YYYYMMDD>/VERDICT-<run_ts>-<seq>.json,
    content_sha256=content_digest(report_dir)(裁决绑定的锚)。修订循环:
    正文修订→摘要变→旧档自动过期(_semantic_review_state 的 fresh=False),
    席位复验后调本函数再写新档——旧失败证据永在档,不覆盖。

    Audit-R2 条目2 定序面: revision=该 run_ts 全档(跨日目录)最大号+1,
    predecessor=前一最新档相对路径(首档=None)——裁决顺序由内容字段
    显式承载,不依赖文件系统 mtime;必填字段(overall/reviewer/run_ts/
    recorded_at)缺失即抛 ValueError,损坏档不落盘。
    """
    if not overall or not reviewer:
        raise ValueError('裁决必填字段缺失: overall/reviewer 不得为空')
    if overall not in SEAT_VERDICT_VOCAB:
        raise ValueError(f'越表裁决词: {overall!r} 不在 R32 席位词表 '
                         f'{SEAT_VERDICT_VOCAB}(同义映射: '
                         'VERIFIED/PASS→UPHELD)')
    report = _load_json(os.path.join(report_dir, 'report.json'))
    run_ts = (report.get('run') or {}).get('ts_utc') or ''
    if not run_ts:
        raise ValueError('report.json 缺 run.ts_utc,无法绑定裁决')
    day = datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')
    d = os.path.join(root, 'audit', 'semantic_review', day)
    os.makedirs(d, exist_ok=True)
    seq = len([f for f in os.listdir(d) if f.startswith(
        'VERDICT-' + run_ts)]) + 1
    path = os.path.join(d, 'VERDICT-%s-%02d.json' % (run_ts, seq))
    prior = _verdicts_for_run(root, run_ts)
    revs = [v.get('revision') for _, v in prior
            if isinstance(v, dict) and isinstance(v.get('revision'), int)]
    revision = (max(revs) + 1) if revs else (len(prior) + 1)
    predecessor = None
    if prior:
        latest_p, _ = max(
            prior, key=lambda t: _verdict_sort_key(t[0], t[1]))
        predecessor = os.path.relpath(latest_p, root)
    # Audit-R1 对齐 R32 席位章程 schema: seat 恒为章程名,audited_at=归档日
    # (HKT),counterexamples_sought 非空由调用席自证(B3/B4/B5 机核面)。
    doc = {'seat': 'semantic-audit-seat', 'overall': overall,
           'reviewer': reviewer, 'notes': notes,
           'run_ts': run_ts, 'content_sha256': content_digest(report_dir),
           'audited_at': day[:4] + '-' + day[4:6] + '-' + day[6:],
           'recorded_at': _now_utc(),
           'revision': revision, 'predecessor': predecessor,
           'counterexamples_sought': ((extra or {}).pop(
               'counterexamples_sought', None)
               or ['(未记载: 席位简报须补反例面)'])}
    if extra:
        doc.update(extra)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    return path


def rebind_verdict_digest(root, report_dir, note):
    """Audit-R2 条目1 迁移面: 摘要口径换代(v1→v2)时的机械重绑。

    仅当**内容未变**可重绑: 先验旧锚(最新档 content_sha256 与
    content_digest_v1(当前内容)一致),再写新档(revision 续链,
    overall/reviewer 承袭,rebind 块如实记迁移事实)。内容已变则抛
    ValueError——那不是重绑,是修订,须独立席位复验,不得机械承袭。
    非重审: 判断内容零变化,裁决结论承袭;rebind 块=机器可查的迁移证据。
    """
    report = _load_json(os.path.join(report_dir, 'report.json'))
    run_ts = (report.get('run') or {}).get('ts_utc') or ''
    if not run_ts:
        raise ValueError('report.json 缺 run.ts_utc,无法重绑')
    hits = _verdicts_for_run(root, run_ts)
    if not hits:
        raise ValueError('无在档裁决可重绑')
    latest_p, latest = max(
        hits, key=lambda t: _verdict_sort_key(t[0], t[1]))
    if not isinstance(latest, dict) or not latest.get('content_sha256'):
        raise ValueError('最新档无旧锚,不适用机械重绑')
    if latest['content_sha256'] != content_digest_v1(report_dir):
        raise ValueError('旧锚与当前内容不符(内容已变)——须独立复验,'
                         '不得机械重绑')
    return record_semantic_verdict(
        root, report_dir, latest.get('overall'), latest.get('reviewer'),
        notes=(latest.get('notes') or ''),
        extra={'rebind': {
            'from_algorithm': 'digest_v1(judgment+report.md)',
            'to_algorithm': 'digest_v2(report.json+judgment)',
            'verified_v1_match': True,
            'predecessor_archive': os.path.relpath(latest_p, root),
            'note': note}})


def _semantic_review_state(report, root, report_dir=None):
    """R33-①: 语义审计席状态面(常驻席=SEMANTIC-AUDIT-SEAT;§4b/§8)。

    唤起点(ii): L3(定性推断)/L4(条件情景)落位即 required=True——
    渲染器只标状态+披露(§8 披露开关),真席位调用归编排层(引擎轮读
    report.semantic_review.required 自动唤席)。席位裁决档=
    root/audit/semantic_review/YYYYMMDD/VERDICT-<run_ts>*.json
    (append-only),在案→披露升为裁决摘要;缺席→「叙事语义未经
    独立裁决」。确定性: 纯文件面判定,零模型零网络。

    Audit-R1 F02 绑定面: 裁决档带 content_sha256 时按当前
    content_digest(report_dir) 判 fresh(True/False);无绑定键的旧档
    fresh=None(在场但不冒充新鲜——report 门不放行)。

    Audit-R2 条目2 裁决顺序与非法记录(fail-closed):
    - 定序=内容序 _verdict_sort_key(revision/recorded_at/文件名 seq),
      mtime 不参与——调换裁决文件 mtime 结果不变;
    - 最新档损坏(不可解析/缺 overall)→ error='corrupt_latest',
      verdict=None——**不回退旧 PASS**;
    - revision 同号多档 → error='duplicate_revision'——冲突即阻断;
    - 全史保留: prior_verdicts=除最新外全档(含损坏档,如实披露)。
    error 非空时 report 门 review_ok=False(阻断交付)。
    """
    layers = report.get('layers') or {}
    l3p = bool((layers.get('L3_AI推断层') or {}).get('produced'))
    l4p = bool((layers.get('L4_条件情景层') or {}).get('produced'))
    reasons = ((['l3_qualitative_inference'] if l3p else [])
               + (['l4_conditional_scenarios'] if l4p else []))
    state = {'required': bool(reasons), 'reasons': reasons,
             'seat_invoked': False, 'verdict': None, 'archive': None,
             'fresh': None, 'verdicts_n': 0, 'prior_verdicts': [],
             'error': None}
    if not reasons:
        return state
    run_ts = (report.get('run') or {}).get('ts_utc') or ''
    if not run_ts:
        return state
    hits = _verdicts_for_run(root, run_ts)
    if not hits:
        return state
    keyed = sorted((_verdict_sort_key(p, v), p, v) for p, v in hits)
    state['verdicts_n'] = len(keyed)
    state['prior_verdicts'] = [os.path.relpath(p, root)
                               for _, p, _ in keyed[:-1]]
    revs = [v.get('revision') for _, _, v in keyed
            if isinstance(v, dict) and isinstance(v.get('revision'), int)]
    _, latest_p, latest = keyed[-1]
    state['archive'] = os.path.relpath(latest_p, root)
    if len(revs) != len(set(revs)):
        state.update(seat_invoked=True, verdict=None,
                     error='duplicate_revision')
        return state
    if not isinstance(latest, dict) or not latest.get('overall'):
        state.update(seat_invoked=True, verdict=None,
                     error='corrupt_latest')
        return state
    state.update(seat_invoked=True, verdict=latest.get('overall'))
    bound = latest.get('content_sha256')
    if bound and report_dir:
        try:
            state['fresh'] = (content_digest(report_dir) == bound)
        except (OSError, ValueError):
            state['fresh'] = False
    elif bound:
        state['fresh'] = None   # 有绑定但无 report_dir 可核=不冒充新鲜
    return state


def _atomic_write_text(path, text):
    """R36 Ni-3(R25 审计遗留): 临时文件+os.replace 单文件原子写。

    跨写中断(进程杀/磁盘满)=要么旧全文要么新全文,无半写撕裂视图;
    .tmp 落同目录保证与目标同文件系统(replace 原子性前提)。
    """
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(text)
    os.replace(tmp, path)


def _write_report(report_dir, report, rj_path):
    """report.json + report.md 同步落盘(两视图一原子语义)。

    R25 NIT V1-2(R24 审计): blocked 路径原先只写 json 不重渲 md——md/json
    失同步(旧 md 无门槛拦截记录)。任何改变 report 的路径(含 blocked)退出
    前都经本函数,两视图同步是 attach 的不变式。
    R36 Ni-3: 两文件各经 _atomic_write_text(先渲 md 后落盘,渲染异常时
    两文件都不动——旧视图完整保留,不产生 json 新/md 旧的中间态)。
    """
    import research_orchestrator as ro
    md_text = ro._render_md(report)
    _atomic_write_text(
        rj_path, json.dumps(report, ensure_ascii=False, indent=2,
                            default=str))
    _atomic_write_text(os.path.join(report_dir, 'report.md'), md_text)


def _new_attach_meta(prior, meta):
    """R36 Ni-2(R25 审计遗留): attach 元数据换代保真。

    原实现整 dict 替换——重 attach(修订后再提/拦截后重跑)会把上一轮
    attach 记录从报告面抹掉。现把上一轮压缩进 attach_history 追加链
    (attached/attached_at/judgment_file/schema_version/blocked +
    validation.passed/contract verdict 摘要),最近 5 轮封顶防无界。
    """
    out = dict(meta)
    if isinstance(prior, dict) and prior.get('attached_at'):
        rec = {}
        for k in ('attached', 'attached_at', 'judgment_file',
                  'schema_version', 'blocked'):
            if k in prior:
                rec[k] = prior[k]
        val = prior.get('validation')
        if isinstance(val, dict):
            rec['validation_passed'] = val.get('passed')
        cv = prior.get('contract_verification')
        if isinstance(cv, dict):
            rec['contract_verdict'] = cv.get('verdict')
        hist = list(prior.get('attach_history') or [])
        hist.append(rec)
        out['attach_history'] = hist[-5:]
    return out


def attach_judgment(report_dir, judgment_path, root=None,
                    allow_failed_run=False):
    """校验 Agent judgment 并合并进 research-run 报告(半落位=不落位)。

    校验通过: layers L3/L4 produced=True+attribution=ai_inferred+判断原文,
    judgment 副本存 <report_dir>/agent_judgment.json,report.md 重渲(含
    L3/L4 节);校验不过: produced 保持 False,violations 落档供 Agent 修订
    重提,绝不半落位。

    R23 审计 MINOR-4: run_ok=False 的 research-run 默认拒收 judgment——
    判断不得落在失败证据面之上(静默落位=L3/L4 produced=True 掩盖底座红)。
    显式 allow_failed_run=True 才放行(诚实拒答类步骤失败但证据面可用的
    场景;门槛显式越过=可审计)。返回摘要 dict(ia_cli 与测试共用)。
    """
    root = root or ROOT
    rj_path = os.path.join(report_dir, 'report.json')
    report = _load_json(rj_path)
    judgment = _load_json(judgment_path)

    # ── MINOR-4 门槛: 失败底座默认拒收(Audit-R1 F02 分级) ──────────
    # 规则运行前固定(与 plan 段 run.degradation_policy 同文,双写=互证):
    #   critical_zero_evidence: L1 事实行=0(引擎崩溃/全量采集失败)——
    #     判断无处可落,**任何旗标不得放行**(不用 --allow-failed-run 把
    #     关键失败自动变成成功);
    #   required_data_missing(Audit-R2 条目7): 运行前声明的必要指标
    #     (问题词面命中,data_requirements tier=required)采集缺席——
    #     任务目标缺口,默认阻塞;显式 allow_failed_run 才放行并记
    #     degraded(缺口随档,不得事后把必要改判可选=缩减任务目标);
    #   optional_data_missing: L1 事实面在场、失败步=诚实拒答类(如源端
    #     缺席 no_series)——须显式 allow_failed_run=True,落位记 degraded。
    run_ok = report.get('run_ok')
    if run_ok is False:
        l1_rows = len(((report.get('layers') or {}).get('L1_事实层') or {})
                      .get('rows') or [])
        req_missing = [
            i.get('metric_id') for i in
            (((report.get('run') or {}).get('data_requirements') or {})
             .get('items') or [])
            if i.get('tier') == 'required' and i.get('outcome') == 'missing']
        if l1_rows == 0:
            blocked_class = 'critical_zero_evidence'
        elif req_missing:
            blocked_class = 'required_data_missing'
        else:
            blocked_class = 'optional_data_missing'
    else:
        blocked_class = None
    if run_ok is False and (blocked_class == 'critical_zero_evidence'
                            or not allow_failed_run):
        report['agent_judgment'] = _new_attach_meta(
            report.get('agent_judgment'),
            {
                'attached': False,
                'attached_at': _now_utc(),
                'judgment_file': os.path.basename(judgment_path),
                'schema_version': JUDGMENT_SCHEMA_VERSION,
                'blocked': 'run_ok_false',
                'blocked_class': blocked_class,
                'block_note': ('research-run run_ok=False——判断默认不得落在失败'
                               '证据面上;显式 allow_failed_run=True 只放行'
                               ' optional_data_missing(L1 证据面在场+诚实拒答类'
                               '失败);critical_zero_evidence 任何旗标不放行'
                               if blocked_class == 'critical_zero_evidence' else
                               'research-run run_ok=False——判断默认不得落在失败'
                               '证据面上;显式 allow_failed_run=True 才放行'
                               '(required_data_missing=必要指标缺席的任务目标'
                               '缺口,或 optional_data_missing=诚实拒答类失败'
                               '且证据面仍可用,由 Agent 显式声明并随档)'),
                'run_ok_at_attach': run_ok,
            })
        # R33-①: blocked 面同样落席位状态键(L3 未落位→required=False,
        # 面键一致;不追溯旧档)
        report['semantic_review'] = _semantic_review_state(
            report, root, report_dir)
        # R25 NIT V1-2: blocked 路径同样重渲 md(拦截记录两视图同步)
        _write_report(report_dir, report, rj_path)
        return {'report_dir': report_dir,
                'attached': False,
                'blocked': 'run_ok_false',
                'blocked_class': blocked_class,
                'run_ok_at_attach': run_ok,
                'layers_summary': {
                    'L3_produced': (report.get('layers', {})
                                    .get('L3_AI推断层', {})
                                    .get('produced')),
                    'L4_produced': (report.get('layers', {})
                                    .get('L4_条件情景层', {})
                                    .get('produced'))}}

    ev_refs = {e.get('ref') for e in report.get('evidence_index') or []
               if e.get('ref')}
    mids = _registry_metric_ids(root)
    res = validate_judgment(judgment, ev_refs, mids)

    # ── 阶段四钩子: 判定档 vs 自身证据面契约验证 ─────────────────────
    # 语义全在 research_contract/judgment_contract.py,此处仅挂载+门控:
    # 客观事实相左(CONTRADICTED)或未全证(NOT_VERIFIED)→拒落位,修档再提。
    try:
        from research_contract.judgment_contract import verify_judgment
        contract = verify_judgment(judgment, report)
    except Exception as exc:                        # 异常=如实降级,禁静默放行
        contract = {'verdict': 'NOT_VERIFIED', 'stats': {},
                    'error': f'{type(exc).__name__}: {exc}'}
    contract_ok = contract.get('verdict') == 'VERIFIED'

    layers = report.get('layers') or {}
    if res['passed'] and contract_ok:
        content = copy.deepcopy(judgment)
        for key, layer_key in (('l3', 'L3_AI推断层'), ('l4', 'L4_条件情景层')):
            layers[layer_key]['produced'] = True
            layers[layer_key]['attribution'] = 'ai_inferred'
            layers[layer_key]['content'] = content.get(key)
            layers[layer_key]['note'] = (
                'Agent(编排层)研判落位,attribution=ai_inferred;'
                '纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,'
                '判断质量归 Agent 与独立审计')
        # R36 Ni-3: 判定档副本同原子写(与 report.json 同级防撕裂)
        _atomic_write_text(
            os.path.join(report_dir, 'agent_judgment.json'),
            json.dumps(judgment, ensure_ascii=False, indent=2))
    else:
        # R23 MINOR-3(独立审计): 失败重提时清残留 content——
        # produced=False 与旧 content 并存=语义不一致
        for layer_key in ('L3_AI推断层', 'L4_条件情景层'):
            layers[layer_key]['produced'] = False
            layers[layer_key].pop('content', None)
            layers[layer_key].pop('attribution', None)

    report['layers'] = layers
    # R33-①: 席位状态面随档(确定性面零污染: 新增键,不动
    # steps/evidence_index/run;编排层读 required 自动唤席)
    report['semantic_review'] = _semantic_review_state(
        report, root, report_dir)
    report['agent_judgment'] = _new_attach_meta(
        report.get('agent_judgment'),
        {
            'attached': bool(res['passed'] and contract_ok),
            'attached_at': _now_utc(),
            'judgment_file': os.path.basename(judgment_path),
            'schema_version': JUDGMENT_SCHEMA_VERSION,
            'validation': res,
            'contract_verification': contract,   # 阶段四: 契约验证结果随档
            # MINOR-4: 落位时的底座状态随档(含 allow_failed_run 越过面)
            'run_ok_at_attach': run_ok,
            'allow_failed_run': bool(allow_failed_run and run_ok is False),
        })
    if res['passed'] and not contract_ok:    # 纪律绿但契约未全绿=契约门拦截
        report['agent_judgment']['blocked'] = \
            'contract_' + str(contract.get('verdict')).lower()
        report['agent_judgment']['block_note'] = (
            '判定档与证据面契约验证未全绿(客观事实相左/未全证)——'
            '修档再提;详见 contract_verification')
    _write_report(report_dir, report, rj_path)
    return {'report_dir': report_dir,
            'attached': bool(res['passed'] and contract_ok),
            'validation': res,
            'contract_verification': contract,
            'semantic_review': report['semantic_review'],
            'run_ok_at_attach': run_ok,
            'layers_summary': {
                'L3_produced': layers['L3_AI推断层']['produced'],
                'L4_produced': layers['L4_条件情景层']['produced']}}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    import argparse
    p = argparse.ArgumentParser(
        description='Agent Native L3/L4 判断落位+纪律机器校验'
                    '(校验器零生成,内容归 Agent)')
    p.add_argument('--report-dir', required=True,
                   help='research-run 报告目录(含 report.json)')
    p.add_argument('--judgment', required=True,
                   help='Agent judgment JSON 文件(schema v1.1)')
    p.add_argument('--root', default=ROOT)
    a = p.parse_args(argv)
    res = attach_judgment(a.report_dir, a.judgment, root=a.root)
    print(json.dumps(res, ensure_ascii=False, indent=2, default=str))
    return 0 if res['attached'] else 1


if __name__ == '__main__':
    sys.exit(main())
