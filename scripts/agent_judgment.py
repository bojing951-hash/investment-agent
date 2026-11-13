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
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
SCRIPTS = os.path.join(ROOT, 'scripts')
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

JUDGMENT_SCHEMA_VERSION = '1.0'
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

    judgment: Agent 提交的 dict(schema v1.0);evidence_refs: 本报告证据索引
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

    # ── MINOR-4 门槛: 失败底座默认拒收 ─────────────────────────────
    run_ok = report.get('run_ok')
    if run_ok is False and not allow_failed_run:
        report['agent_judgment'] = {
            'attached': False,
            'attached_at': _now_utc(),
            'judgment_file': os.path.basename(judgment_path),
            'schema_version': JUDGMENT_SCHEMA_VERSION,
            'blocked': 'run_ok_false',
            'block_note': ('research-run run_ok=False——判断默认不得落在失败'
                           '证据面上;显式 allow_failed_run=True 才放行'
                           '(诚实拒答类失败且证据面仍可用时由 Agent 声明)'),
            'run_ok_at_attach': run_ok,
        }
        with open(rj_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        return {'report_dir': report_dir,
                'attached': False,
                'blocked': 'run_ok_false',
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

    layers = report.get('layers') or {}
    if res['passed']:
        content = copy.deepcopy(judgment)
        for key, layer_key in (('l3', 'L3_AI推断层'), ('l4', 'L4_条件情景层')):
            layers[layer_key]['produced'] = True
            layers[layer_key]['attribution'] = 'ai_inferred'
            layers[layer_key]['content'] = content.get(key)
            layers[layer_key]['note'] = (
                'Agent(编排层)研判落位,attribution=ai_inferred;'
                '纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,'
                '判断质量归 Agent 与独立审计')
        with open(os.path.join(report_dir, 'agent_judgment.json'), 'w',
                  encoding='utf-8') as f:
            json.dump(judgment, f, ensure_ascii=False, indent=2)
    else:
        # R23 MINOR-3(独立审计): 失败重提时清残留 content——
        # produced=False 与旧 content 并存=语义不一致
        for layer_key in ('L3_AI推断层', 'L4_条件情景层'):
            layers[layer_key]['produced'] = False
            layers[layer_key].pop('content', None)
            layers[layer_key].pop('attribution', None)

    report['layers'] = layers
    report['agent_judgment'] = {
        'attached': bool(res['passed']),
        'attached_at': _now_utc(),
        'judgment_file': os.path.basename(judgment_path),
        'schema_version': JUDGMENT_SCHEMA_VERSION,
        'validation': res,
        # MINOR-4: 落位时的底座状态随档(含 allow_failed_run 越过面)
        'run_ok_at_attach': run_ok,
        'allow_failed_run': bool(allow_failed_run and run_ok is False),
    }
    with open(rj_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    with open(os.path.join(report_dir, 'report.md'), 'w',
              encoding='utf-8') as f:
        import research_orchestrator as ro
        f.write(ro._render_md(report))
    return {'report_dir': report_dir,
            'attached': bool(res['passed']),
            'validation': res,
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
                   help='Agent judgment JSON 文件(schema v1.0)')
    p.add_argument('--root', default=ROOT)
    a = p.parse_args(argv)
    res = attach_judgment(a.report_dir, a.judgment, root=a.root)
    print(json.dumps(res, ensure_ascii=False, indent=2, default=str))
    return 0 if res['attached'] else 1


if __name__ == '__main__':
    sys.exit(main())
