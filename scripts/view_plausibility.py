#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter9 P0-2 观点可信度(VP)sidecar 引擎——假设级验证链+六标签聚合。

独立于 views v1.1(不动机构观点档): 验证判断落在
data/institutions/verification/VP-{VIEW-ID}.json(编排层 Agent 写入,
引擎只做确定性校验/聚合/装载);views 档保持"采集的原文",VP 档承载
"对照本地数据的判定"——两层职责分离,校验不过的 sidecar 不入面。
sidecar 的假设↔forecast 对应是语义判断,归编排层 Agent(引擎不造判定);
本引擎消费 view_verifier --mode C 的机械 verdict,做映射/聚合/装载。

六标签(协调裁定④最保守聚合;优先级表锁定于 tests/test_c9_vp_sidecar.py):
  SUPPORTED / PARTIALLY_SUPPORTED / MIXED / CONTRADICTED /
  NOT_YET_TESTABLE / INSUFFICIENT_EVIDENCE

聚合(假设级→观点级,确定性,逐条短路):
  1 全部 CONTRADICTED     → CONTRADICTED
  2 任一 CONTRADICTED     → MIXED(任一被推翻,观点级至少 MIXED)
  3 全部 NOT_YET_TESTABLE → NOT_YET_TESTABLE
  4 全部 SUPPORTED        → SUPPORTED(观点级 SUPPORTED 需全部假设 SUPPORTED)
  5 任一 SUPPORTED        → PARTIALLY_SUPPORTED
  6 其余                  → INSUFFICIENT_EVIDENCE

mode C verdict → 假设标签机械映射: supports→SUPPORTED;against→CONTRADICTED;
NOT_YET_TESTABLE→NOT_YET_TESTABLE;UNPARSEABLE_HORIZON/NOT_MACHINE_VERIFIABLE/
INSUFFICIENT_DATA/LEVEL_TARGET/neutral→INSUFFICIENT_EVIDENCE(机器不可判=
证据不足,不升不降)。

CLI:
  python3 scripts/view_plausibility.py VIEW-YYYYMMDD-NNN [--vp-dir DIR]
  python3 scripts/view_plausibility.py --list [--vp-dir DIR]
  python3 scripts/view_plausibility.py --build VIEW-… [--dry-run] [--vp-dir DIR]
  python3 scripts/view_plausibility.py --build-all [--dry-run] [--vp-dir DIR]
  python3 scripts/view_plausibility.py --verify-binding VIEW-… [--vp-dir DIR]
退出码: 0=装载校验成功;1=缺失/不可用;2=用法错。

v1.1(R1 autonomous-rd 2026-11-11): 三型证据落库——hypotheses[].stages.{A,B}
结构化证据+stage_labels(假设证据评价,非预测验证);view_label/C 层契约零变动。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
SCRIPTS = os.path.join(ROOT, 'scripts')
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import view_store as vs  # noqa: E402

VP_DIR = os.path.join(ROOT, 'data', 'institutions', 'verification')

LABELS = ('SUPPORTED', 'PARTIALLY_SUPPORTED', 'MIXED', 'CONTRADICTED',
          'NOT_YET_TESTABLE', 'INSUFFICIENT_EVIDENCE')

REF_KINDS = ('core_view', 'key_assumption')

# mode C verdict(view_verifier verify_expiry)→假设标签
VERDICT_TO_LABEL = {
    'supports': 'SUPPORTED',
    'against': 'CONTRADICTED',
    'NOT_YET_TESTABLE': 'NOT_YET_TESTABLE',
    'UNPARSEABLE_HORIZON': 'INSUFFICIENT_EVIDENCE',
    'NOT_MACHINE_VERIFIABLE': 'INSUFFICIENT_EVIDENCE',
    'INSUFFICIENT_DATA': 'INSUFFICIENT_EVIDENCE',
    'LEVEL_TARGET': 'INSUFFICIENT_EVIDENCE',
    'neutral': 'INSUFFICIENT_EVIDENCE',
}

# R22(Charter 10 §5.3): 判定标签=宣称由机器证据产生的对错判断;
# 不可判族=底证不可支撑判定标签的证据状态。
_JUDGMENT_LABELS = ('SUPPORTED', 'CONTRADICTED')
_UNTESTABLE_FAMILY = ('NOT_YET_TESTABLE', 'INSUFFICIENT_EVIDENCE')


def verdict_to_label(verdict):
    """mode C verdict → 六标签(未知 verdict→INSUFFICIENT_EVIDENCE,不猜)。

    R22(2026-11-12,Charter 10 §5.3): 编排层多 forecast 假设存复合 verdict
    ('NOT_YET_TESTABLE/NOT_YET_TESTABLE')——拆 '/' 后各段标签一致取该标签,
    不一致/空→INSUFFICIENT_EVIDENCE(最保守)。"""
    s = str(verdict).strip()
    parts = [p.strip() for p in s.split('/') if p.strip()]
    if not parts:
        return 'INSUFFICIENT_EVIDENCE'
    labels = [VERDICT_TO_LABEL.get(p, 'INSUFFICIENT_EVIDENCE') for p in parts]
    return labels[0] if len(set(labels)) == 1 else 'INSUFFICIENT_EVIDENCE'


def rollup_view_label(labels):
    """假设标签序列 → 观点级标签(裁定④最保守聚合;空序列=未验证面)。"""
    ls = [l for l in labels if l in LABELS]
    if not ls:
        return 'INSUFFICIENT_EVIDENCE'
    if all(l == 'CONTRADICTED' for l in ls):
        return 'CONTRADICTED'
    if any(l == 'CONTRADICTED' for l in ls):
        return 'MIXED'
    if all(l == 'NOT_YET_TESTABLE' for l in ls):
        return 'NOT_YET_TESTABLE'
    if all(l == 'SUPPORTED' for l in ls):
        return 'SUPPORTED'
    if any(l == 'SUPPORTED' for l in ls):
        return 'PARTIALLY_SUPPORTED'
    return 'INSUFFICIENT_EVIDENCE'


def vp_path(view_id, vp_dir=None):
    return os.path.join(vp_dir or VP_DIR, f'VP-{view_id}.json')


def load_vp(view_id, vp_dir=None):
    """读单份 sidecar → (doc|None, 原因)。缺目录/缺文件=未验证(非错误,
    干净 clone 常态);损坏 JSON/结构错→(None, 原因)不入面。"""
    p = vp_path(view_id, vp_dir)
    if not os.path.isdir(vp_dir or VP_DIR):
        return None, ('VP 目录不存在(data/institutions/verification/)——'
                      '观点未经验证链(干净 clone/编排层未写入,如实)')
    if not os.path.isfile(p):
        return None, f'无 VP sidecar(VP-{view_id}.json)——观点未经验证链'
    try:
        with open(p, encoding='utf-8') as f:
            doc = json.load(f)
    except (OSError, ValueError) as e:
        return None, f'VP sidecar 不可读/非 JSON: {e}'
    if not isinstance(doc, dict):
        return None, 'VP sidecar 顶层须为对象'
    return doc, 'loaded'


def load_all(vp_dir=None):
    """全部 sidecar → ([doc...], [(file, 原因)...])——坏档隔离不入面。"""
    docs, bad = [], []
    d = vp_dir or VP_DIR
    if not os.path.isdir(d):
        return [], []
    for fn in sorted(os.listdir(d)):
        if not (fn.startswith('VP-') and fn.endswith('.json')):
            continue
        view_id = fn[3:-5]
        doc, reason = load_vp(view_id, d)
        if doc is None:
            bad.append((fn, reason))
        else:
            docs.append(doc)
    return docs, bad


def validate_vp(doc, view_doc):
    """sidecar × views 档交叉校验(确定性)→ (ok, [错误...])。

    检查面: schema_version/view_id 一致;hypotheses 非空且逐条
    label∈六标签、ref 指向 views 档真实元素(core_views[i]/key_assumptions[i]
    索引界内;statement_digest 提供时须为被引陈述前缀);metric_refs 逐条
    {metric_id,direction,segment} 形;view_label 与 hypotheses 聚合一致
    (不一致=写入方未用引擎聚合,拒绝)。"""
    errs = []
    ver = doc.get('schema_version')
    if ver not in ('1.0', '1.1'):
        errs.append('schema_version 须为 "1.0" 或 "1.1"')
    if not isinstance(doc.get('view_id'), str) or not doc['view_id'].startswith('VIEW-'):
        errs.append('view_id 须为 VIEW-YYYYMMDD-NNN')
    elif view_doc is not None and doc['view_id'] != view_doc.get('view_id'):
        errs.append(f"view_id 与 views 档不符({doc['view_id']} vs "
                    f"{view_doc.get('view_id')})")
    hyps = doc.get('hypotheses')
    if not isinstance(hyps, list) or not hyps:
        errs.append('hypotheses 须为非空数组(假设级链)')
        hyps = []
    core = (view_doc or {}).get('core_views') or []
    keys = (view_doc or {}).get('key_assumptions') or []
    for i, h in enumerate(hyps):
        pre = f'hypotheses[{i}]'
        if not isinstance(h, dict):
            errs.append(f'{pre} 须为对象')
            continue
        if h.get('label') not in LABELS:
            errs.append(f'{pre}.label 须∈六标签({h.get("label")!r})')
        ref = h.get('ref') or {}
        kind, idx = ref.get('kind'), ref.get('index')
        if kind not in REF_KINDS:
            errs.append(f'{pre}.ref.kind 须∈{REF_KINDS}({kind!r})')
        arr = core if kind == 'core_view' else keys if kind == 'key_assumption' else []
        if not isinstance(idx, int) or isinstance(idx, bool) or not 0 <= idx < len(arr):
            errs.append(f'{pre}.ref.index 越界({idx};views 档该类元素 {len(arr)} 条)')
        else:
            stmt = str(arr[idx].get('statement', ''))
            dig = ref.get('statement_digest')
            if dig and not stmt.startswith(str(dig)[:24]):
                errs.append(f'{pre}.ref.statement_digest 与被引陈述不符')
        mrs = h.get('metric_refs')
        if not isinstance(mrs, list) or not mrs:
            errs.append(f'{pre}.metric_refs 须为非空数组(指标链)')
        else:
            for j, mr in enumerate(mrs):
                if not isinstance(mr, dict) or not mr.get('metric_id'):
                    errs.append(f'{pre}.metric_refs[{j}] 须含 metric_id')
                elif mr.get('direction') not in (None, 'up', 'down', 'flat'):
                    errs.append(f'{pre}.metric_refs[{j}].direction 须为 up/down/flat/缺省'
                                '(flat=水平不变假设,如"不再加息")')
        # R22(2026-11-12,Charter 10 §5.3)标签-证据绑定纯校验: mode C 绑定的
        # 判定标签(SUPPORTED/CONTRADICTED)必须携带存量 verdict 且
        # 标签=verdict_to_label(verdict)——底证 NOT_YET_TESTABLE 族不得撑
        # 判定标签(结构性防线,不依赖快照;对当前引擎的活体重算= binding_check)。
        ev = h.get('evidence') or {}
        if isinstance(ev, dict) and ev.get('mode') == 'C':
            if h.get('label') in _JUDGMENT_LABELS and ev.get('verdict') is None:
                errs.append(
                    f'{pre}.label={h.get("label")!r} 为判定标签但 mode C 绑定'
                    '无存量 verdict——判定无据可查(Charter 10 §5.3)')
            elif ev.get('verdict') is not None:
                expected = verdict_to_label(ev.get('verdict'))
                if h.get('label') != expected:
                    errs.append(
                        f'{pre}.label({h.get("label")!r})与底证 verdict'
                        f'({ev.get("verdict")!r})绑定不符——按证据应={expected}'
                        '(Charter 10 §5.3: 标签须真正由对应证据产生)')
    declared = doc.get('view_label')
    recomputed = rollup_view_label([h.get('label') for h in hyps
                                    if isinstance(h, dict)])
    if declared != recomputed:
        errs.append(f'view_label({declared!r})与最保守聚合({recomputed!r})不符'
                    '——写入方须用 rollup_view_label 生成')
    # v1.1(R1): 三阶段面校验——stages 结构/stage_labels∈六标签/
    # stage_summary 与假设层最保守聚合一致(C 仍=view_label 契约)。
    if ver == '1.1':
        sum_a, sum_b = [], []
        for i, h in enumerate(hyps):
            if not isinstance(h, dict):
                continue
            pre = f'hypotheses[{i}]'
            stages = h.get('stages')
            if not isinstance(stages, dict) or not all(
                    isinstance(stages.get(k), dict) for k in ('A', 'B')):
                errs.append(f'{pre}.stages.A/B 须为对象(v1.1 三型证据落库)')
                continue
            sl = h.get('stage_labels')
            if not isinstance(sl, dict) or sl.get('A') not in LABELS \
                    or sl.get('B') not in LABELS:
                errs.append(f'{pre}.stage_labels.A/B 须∈六标签')
                continue
            sum_a.append(sl['A'])
            sum_b.append(sl['B'])
        ss = doc.get('stage_summary')
        if not isinstance(ss, dict):
            errs.append('stage_summary 须为对象(v1.1)')
        else:
            if ss.get('C') != declared:
                errs.append(f'stage_summary.C({ss.get("C")!r})须=view_label'
                            f'({declared!r})(C=到期验证语义,契约不变)')
            if ss.get('A') != rollup_view_label(sum_a) or \
                    ss.get('B') != rollup_view_label(sum_b):
                errs.append('stage_summary.A/B 与假设层 stage_labels 最保守'
                            '聚合不符——写入方须用 rollup_view_label 生成')
    return (not errs), errs


def vp_badge_rows(vp_doc):
    """sidecar → 页③徽标表行(纯函数,app/测试共用)。

    v1.1: 有 stage_labels 时附「阶段A/B」列(证据评价,非预测判定)。"""
    kind_label = {'core_view': '观点', 'key_assumption': '假设'}
    rows = []
    for h in vp_doc.get('hypotheses') or []:
        ref = h.get('ref') or {}
        idx = ref.get('index')
        ref_txt = (f"{kind_label.get(ref.get('kind'), ref.get('kind'))}{idx + 1}"
                   if isinstance(idx, int) else f"{ref.get('kind')}?")
        chain = '; '.join(
            f"{mr.get('metric_id')} {mr.get('direction') or '—'}"
            f"({mr.get('segment') or '—'})"
            for mr in (h.get('metric_refs') or [])) or '—'
        ev = h.get('evidence') or {}
        if ev.get('mode') and ev.get('forecast_index'):
            basis = f"mode {ev.get('mode')} #{ev.get('forecast_index')}"
        elif ev.get('mode'):
            basis = f"mode {ev.get('mode')}"
        else:
            basis = '—'
        sl = h.get('stage_labels') or {}
        row = {'ref': ref_txt, '标签': h.get('label'),
               '指标链': chain, '判定依据': basis}
        if sl:
            row['阶段A/B'] = f"{sl.get('A', '—')}/{sl.get('B', '—')}"
        rows.append(row)
    return rows


# ── R22(2026-11-12,Charter 10 §5.3): 标签-证据绑定活体复核 ────────────
# 纯结构校验(validate_vp)只看"verdict 在档→标签=verdict_to_label";本节对
# mode C 绑定的假设**重跑 verify_expiry**(当前快照)复核: ①存量 verdict 与
# 当前引擎 verdict 是否一致(漂移=证据过期,须重建);②当前引擎重算标签 vs
# 声明标签——底证不可判(NOT_YET_TESTABLE 族)而声明判定标签(SUPPORTED/
# CONTRADICTED)= BINDING_VIOLATION(Charter 原文: 不得允许底证
# NOT_YET_TESTABLE 却无充分其他证据就将同一预测标记为 SUPPORTED)。
# 无 mode C 绑定的假设=语义映射层(AI/编排层),机器不可复算——显式标
# interpretation_boundary,人工审查面(诚实边界,不冒充机器验证)。


def binding_check(view_id=None, doc=None, snapshot=None, registry=None,
                  vmap=None, views_dir=None, vp_dir=None, target_map=None,
                  root=None):
    """标签-证据绑定复核(确定性): sidecar 假设层 × verify_expiry 活跑。

    doc 显式传入(build_vp 写入前自检用);否则按 view_id 从 vp_dir 装载。
    snapshot/registry/vmap/target_map 缺省按引擎根装载(与 build_vp 同源)。
    返回 {'ok', 'view_id', 'as_of', 'rows', 'summary'}——rows 每假设一条:
    status ∈ BINDING_OK|BINDING_VIOLATION|LABEL_DRIFT|NO_MACHINE_BINDING|
    ENGINE_UNAVAILABLE|VP_MISSING;ok=False 当且仅当存在 BINDING_VIOLATION。
    LABEL_DRIFT=存量 verdict 与当前引擎不一致(到期推进/数据更新)——披露
    不阻断(重建即消);violation 才是"标签非由证据产生"的红线。"""
    root = root or ROOT
    if doc is None:
        if not view_id:
            return {'ok': False, 'error': {'kind': 'usage',
                                           'message': '须给 view_id 或 doc'}}
        doc, reason = load_vp(view_id, vp_dir)
        if doc is None:
            return {'ok': False, 'view_id': view_id,
                    'error': {'kind': 'vp_missing', 'message': reason}}
    view_id = view_id or doc.get('view_id')
    rows, summary = [], {'BINDING_OK': 0, 'BINDING_VIOLATION': 0,
                         'LABEL_DRIFT': 0, 'NO_MACHINE_BINDING': 0,
                         'ENGINE_UNAVAILABLE': 0, 'VP_MISSING': 0}
    view_doc, vr = vs.get_view(view_id, views_dir)
    if view_doc is None:
        return {'ok': False, 'view_id': view_id,
                'error': {'kind': 'view_not_found_or_quarantined',
                          'message': vr}}
    import view_verifier as vv
    import workbench_data as wd
    if snapshot is None:
        snapshot, note = wd.latest_snapshot(root)
        if snapshot is None:
            snapshot = None
    if registry is None or vmap is None:
        # 注册表/映射固定引擎根(与 verify_expiry 同纪律);root 仅快照解析侧
        registry = registry or wd.load_registry(ROOT)
        vmap = vmap or vv.load_map()
    if target_map is None:
        try:
            target_map = vv.load_forecast_target_map()
        except (OSError, ValueError):
            target_map = None
    out_c = None
    if snapshot is not None:
        out_c = vv.verify_expiry(view_id, snapshot, registry, vmap,
                                 views_dir=views_dir, target_map=target_map)
        if not out_c.get('ok'):
            out_c = None
    verdicts = ((out_c or {}).get('forecast_verdicts') or [])
    for i, h in enumerate(doc.get('hypotheses') or []):
        if not isinstance(h, dict):
            continue
        pre = f'hypotheses[{i}]'
        ev = h.get('evidence') or {}
        declared = h.get('label')
        row = {'hyp': pre, 'declared_label': declared,
               'stored_verdict': ev.get('verdict')}
        if not isinstance(ev, dict) or ev.get('mode') != 'C':
            row['status'] = 'NO_MACHINE_BINDING'
            row['interpretation_boundary'] = (
                '无 mode C 机器绑定——语义映射=编排层/AI,机器不可复算,'
                '人工审查面(Charter 10 §5.3 解释边界)')
        elif out_c is None:
            row['status'] = 'ENGINE_UNAVAILABLE'
            row['note'] = '当前无快照/引擎不可跑(mode C 活体复核缺席,如实)'
        else:
            fi = ev.get('forecast_index')
            lfs = [k for k in (ev.get('linked_forecasts') or [])
                   if isinstance(k, int) and not isinstance(k, bool)]
            # 候选当前 verdict(基制歧义如实枚举,依存量 verdict 匹配定基):
            # 生产档实测 forecast_index/linked_forecasts=0-based(指向
            # forecasts 数组),引擎行号=1-based;复合假设存量 verdict 为
            # '/'.join(各 forecast verdict)。
            cands = []
            if lfs and all(0 <= k < len(verdicts) for k in lfs):
                cands.append(('/'.join(str(verdicts[k].get('verdict'))
                                       for k in lfs),
                              f'linked_forecasts 0-based({lfs})'))
            if lfs and all(1 <= k <= len(verdicts) for k in lfs):
                cands.append(('/'.join(str(verdicts[k - 1].get('verdict'))
                                       for k in lfs),
                              f'linked_forecasts 1-based({lfs})'))
            if isinstance(fi, int) and 0 <= fi < len(verdicts):
                cands.append((str(verdicts[fi].get('verdict')),
                              'forecast_index 0-based'))
            if isinstance(fi, int) and 1 <= fi <= len(verdicts):
                cands.append((str(verdicts[fi - 1].get('verdict')),
                              'forecast_index 1-based'))
            stored = ev.get('verdict')
            cur_verdict, basis = None, None
            for cv, b in cands:
                if cv == stored:
                    cur_verdict, basis = cv, b + '(存量匹配)'
                    break
            if cur_verdict is None and cands:
                cur_verdict, basis = cands[0][0], cands[0][1] + \
                    '(存量不匹配,按首候选取)'
            row['index_basis'] = basis
            row['current_verdict'] = cur_verdict
            recomputed = verdict_to_label(cur_verdict) if cur_verdict else None
            row['recomputed_label'] = recomputed
            if declared in _JUDGMENT_LABELS and recomputed in _UNTESTABLE_FAMILY:
                row['status'] = 'BINDING_VIOLATION'
                row['note'] = (f'底证当前={cur_verdict}(不可判)而声明={declared}'
                               '——判定标签非由当前证据产生(Charter 10 §5.3 红线)')
            elif (stored is not None and cur_verdict is not None
                    and cur_verdict != stored):
                row['status'] = 'LABEL_DRIFT'
                row['note'] = (f'存量 verdict({stored})与当前引擎'
                               f'({cur_verdict})不一致(到期推进/数据更新/'
                               '映射扩充)——重建即消,披露不阻断')
            else:
                row['status'] = 'BINDING_OK'
        summary[row['status']] = summary.get(row['status'], 0) + 1
        rows.append(row)
    return {'ok': summary['BINDING_VIOLATION'] == 0, 'view_id': view_id,
            'as_of': (snapshot or {}).get('target_date'),
            'snapshot_id': (snapshot or {}).get('snapshot_id'),
            'rows': rows, 'summary': summary,
            'semantics': ('BINDING_OK=标签由当前引擎证据产生 / '
                          'BINDING_VIOLATION=底证不可判却声明判定标签(红线) / '
                          'LABEL_DRIFT=证据推进待重建(披露) / '
                          'NO_MACHINE_BINDING=语义层,人工审查面')}


# ── R1(autonomous-rd 2026-11-11): VP v1.1 三型证据全落库 ──────────────
# 背景: v1.0 的 view_label 只消费 view_verifier --mode C verdict(到期验证),
# A(提出时)/B(发布后)两型引擎已可实算但从未结构化落库——AC3 三阶段区分
# 名存实亡。v1.1 在不动 C 契约(view_label=到期验证语义,未到期不可判)的
# 前提下,把 A/B 阶段证据与阶段标签(假设证据评价,非预测验证)落进 sidecar。
# 语义层(hypotheses↔metric_refs↔linked_forecasts)沿用编排层 v1.0 映射,
# 引擎不造语义;方向提取只认机构明示文本(词表机械解析,零 AI 判断)。

REL_TO_STAGE = {'supports': 'SUPPORTED', 'against': 'CONTRADICTED',
                'neutral': 'INSUFFICIENT_EVIDENCE'}


def _stage_relation_a(changes, hint):
    """阶段A关系: trailing 窗净变动方向 vs hint(与 verify 的机械规则同款;
    语义=假设证据评价,非预测验证——不进 view_label)。"""
    if hint not in ('up', 'down'):
        return None, '无方向(机构未明示)→证据观察,不判支持/反对'
    import view_verifier as vv
    got = vv._net_direction(changes)
    if got is None:
        return None, '窗口无可用变动(诚实缺席)'
    if got == 'flat':
        return 'neutral', '窗口净变动=0(无判别力)'
    rel = 'supports' if got == hint else 'against'
    return rel, f'净变动方向={got} vs hint={hint}(trailing窗机械比对,证据评价非预测验证)'


def _stage_relation_b(node, hint):
    """阶段B关系: since_publish 区间变动方向 vs hint(严格>publish 证据更新窗)。"""
    if hint not in ('up', 'down'):
        return None, '无方向(机构未明示)→证据观察,不判支持/反对'
    if not isinstance(node, dict) or node.get('available') is False:
        reason = node.get('reason') if isinstance(node, dict) else '缺节点'
        return None, f'发布后无可用新证据({reason})'
    val = next((node.get(k) for k in ('pp_change', 'pct_change', 'abs_change')
                if node.get(k) is not None), None)
    if val is None:
        return None, '发布后区间无变动值'
    got = 'up' if val > 0 else 'down' if val < 0 else 'flat'
    if got == 'flat':
        return 'neutral', '发布后净变动=0(无判别力)'
    rel = 'supports' if got == hint else 'against'
    return rel, f'发布后净变动方向={got} vs hint={hint}(机械比对,证据评价非预测验证)'


def _hypothesis_directions(hyp, view_doc, target_map):
    """机构明示方向提取(确定性): metric_refs[].direction 优先(编排层已给);
    否则由 evidence.linked_forecasts 指向的 forecast 自身 value_or_direction
    经 view_verifier._parse_direction 词表机械解析,且该 forecast 的 target 经
    forecast_target_map 解析到同一 metric 才采用(防错配)。
    R22(2026-11-12,Charter 10 §5.1): 文本提取的方向经
    direction_semantics 换算为**指标数值方向**(报价对计价货币侧/
    收益率-价格侧反转,disclosure 随 provenance 落档)——"日元升值"不再
    机械当 USDJPY 上行。metric_refs[].direction 为编排层已写的指标方向,
    无原始措辞可换算,维持原值(边界如实: 该层主体歧义归人工审阅)。
    linked_forecasts 基制=**1-based**(与 mode C verify_expiry 的
    evidence.forecast_index enumerate(...,1) 同惯例;E席审计 MAJOR-2:
    双基容忍会把方向挂到错误引文——生产 17 份该路径零使用,定基零迁移)。
    返回 ({metric_id: hint}, {metric_id: provenance});不可解析不猜。"""
    import view_verifier as vv
    import direction_semantics as dsem
    dirs, prov = {}, {}
    for mr in hyp.get('metric_refs') or []:
        mid = mr.get('metric_id')
        if mr.get('direction') in ('up', 'down'):
            dirs[mid] = mr['direction']
            prov[mid] = {'source': 'metric_ref', 'attribution': 'institution_stated'}
    forecasts = view_doc.get('forecasts') or []
    for fi in (hyp.get('evidence') or {}).get('linked_forecasts') or []:
        i = (fi - 1 if isinstance(fi, int) and 1 <= fi <= len(forecasts)
             else None)
        if i is None:
            continue
        f = forecasts[i]
        hint = vv._parse_direction(f.get('value_or_direction'))
        if hint is None:
            continue
        metric = vv._resolve_forecast_metric(f.get('target'), target_map)
        if metric and metric not in dirs:
            mhint, dnode = dsem.apply_metric_direction_semantics(
                hint, metric, [f.get('target'), f.get('value_or_direction')])
            dirs[metric] = mhint
            p = {'source': 'forecast_value_or_direction',
                 'forecast_index': fi,
                 'forecast_index_basis': '1-based',
                 'quote': str(f.get('value_or_direction'))[:120],
                 'attribution': 'institution_stated'}
            if dnode is not None:
                p['direction_semantics'] = dnode
            prov[metric] = p
    return dirs, prov


def _stage_label(rows):
    """阶段标签: 有判行的机械映射→最保守聚合;零判行=INSUFFICIENT(不猜)。"""
    ls = [REL_TO_STAGE[r['relation']] for r in rows
          if r.get('relation') in REL_TO_STAGE]
    return rollup_view_label(ls), len(ls)


def build_vp(view_id, root=None, vp_dir=None, views_dir=None, dry_run=False):
    """既有 VP v1.0(语义层)× 引擎三型实跑 → VP v1.1(三阶段证据落库)。

    C 层零变动: hypotheses[].label/evidence 与 view_label 保持 v1.0 语义
    (mode C verdict 映射+最保守聚合,未到期不可判——既有契约与测试不动)。
    新增: hypotheses[].stages.{A,B}(结构化证据行+关系+锚点披露)、
    stage_labels.{A,B}(假设证据评价)、view 级 stage_summary、lineage 留痕。
    引擎三型同一条取数路径(view_verifier;A=vintage/截断锚,B=最新快照+
    since_publish,C=到期),写入前自校验(validate_vp)。"""
    root = root or ROOT
    base, reason = load_vp(view_id, vp_dir)
    if base is None:
        return {'ok': False, 'view_id': view_id,
                'error': {'kind': 'base_vp_missing', 'message': reason}}
    view_doc, vr = vs.get_view(view_id, views_dir)
    if view_doc is None:
        return {'ok': False, 'view_id': view_id,
                'error': {'kind': 'view_not_found_or_quarantined',
                          'message': vr}}
    ok, errs = validate_vp(base, view_doc)
    if not ok:
        return {'ok': False, 'view_id': view_id,
                'error': {'kind': 'base_vp_invalid', 'message': '; '.join(errs[:3])}}
    import view_verifier as vv
    import workbench_data as wd
    reg = wd.load_registry(ROOT)
    vmap = vv.load_map()
    snap, note = wd.latest_snapshot(root)
    if snap is None:
        return {'ok': False, 'view_id': view_id,
                'error': {'kind': 'no_snapshot', 'message': note}}
    # R5(2026-11-11): 假设层 metric_refs 并入证据面——机构观点明确引用的指标
    # 不因观点 subjects 标签未覆盖而缺席(subject='hypothesis_ref';不在注册表
    # 的如实进 missing 注明语义层缺口,禁猜)。
    extra_ids = sorted({mr.get('metric_id')
                        for h in base.get('hypotheses') or []
                        for mr in h.get('metric_refs') or []
                        if mr.get('metric_id')})
    out_a = vv.verify_at_publish(view_id, reg, vmap, views_dir=views_dir,
                                 root=root, extra_metric_ids=extra_ids)
    out_b = vv.verify(view_id, snap, reg, vmap, views_dir=views_dir, mode='B',
                      extra_metric_ids=extra_ids)
    if not out_a.get('ok') or not out_b.get('ok'):
        bad = [k for k, o in (('A', out_a), ('B', out_b)) if not o.get('ok')]
        return {'ok': False, 'view_id': view_id,
                'error': {'kind': 'engine_error', 'mode': bad,
                          'message': [o.get('error') for o in (out_a, out_b)
                                      if not o.get('ok')]}}
    tmap = vv.load_forecast_target_map()
    ev_a = {e['metric_id']: e for e in out_a.get('evidence') or []}
    ev_b = {e['metric_id']: e for e in out_b.get('evidence') or []}
    miss_a = {m['metric_id']: m.get('reason')
              for m in out_a.get('missing') or []}
    miss_b = {m['metric_id']: m.get('reason')
              for m in out_b.get('missing') or []}
    stage_a_labels, stage_b_labels = [], []
    for h in base.get('hypotheses') or []:
        dirs, prov = _hypothesis_directions(h, view_doc, tmap)
        rows_a, rows_b, miss_rows = [], [], []
        for mr in h.get('metric_refs') or []:
            mid = mr.get('metric_id')
            hint = mr.get('direction') if mr.get('direction') in ('up', 'down') \
                else dirs.get(mid)
            p = ({'source': 'metric_ref', 'attribution': 'institution_stated'}
                 if mr.get('direction') in ('up', 'down') else prov.get(mid))
            e = ev_a.get(mid)
            if e is None:
                miss_rows.append({'metric_id': mid,
                                  'reason': miss_a.get(mid, '快照无该指标事实')})
            else:
                rel, rnote = _stage_relation_a(e.get('changes'), hint)
                row_a = {'metric_id': mid, 'direction': hint,
                         'direction_provenance': p,
                         'level': e.get('level'),
                         'observation_date': e.get('observation_date'),
                         'series_source': e.get('series_source'),
                         'changes': e.get('changes'),
                         'relation': rel, 'relation_note': rnote}
                if e.get('level_source') is not None:  # R5: 截断尾值近似披露
                    row_a['level_source'] = e['level_source']
                rows_a.append(row_a)
            e = ev_b.get(mid)
            if e is None:
                miss_rows.append({'metric_id': mid, 'stage': 'B',
                                  'reason': miss_b.get(mid, '快照无该指标事实')})
            else:
                node = e.get('since_publish')
                rel, rnote = _stage_relation_b(node, hint)
                rows_b.append({'metric_id': mid, 'direction': hint,
                               'direction_provenance': p,
                               'since_publish': node,
                               'relation': rel, 'relation_note': rnote})
        la, nja = _stage_label(rows_a)
        lb, njb = _stage_label(rows_b)
        stage_a_labels.append(la)
        stage_b_labels.append(lb)
        h['stages'] = {
            'A': {'anchor': out_a.get('mode_a_anchor'),
                  'rows': rows_a, 'n_rows': len(rows_a), 'n_judged': nja,
                  'no_lookahead': 'trailing 窗以观点时点为窗末;'
                                  'level observation_date≤publish(截断近似随行披露)'},
            'B': {'snapshot_id': out_b.get('snapshot_id'),
                  'target_date': out_b.get('target_date'),
                  'rows': rows_b, 'n_rows': len(rows_b), 'n_judged': njb,
                  'window': '严格>publish 的证据更新窗(since_publish)'},
        }
        if miss_rows:
            h['stages']['missing'] = miss_rows
        h['stage_labels'] = {'A': la, 'B': lb,
                             'semantics': '假设证据评价(非预测验证;'
                                          '预测判定=标签列,仅到期可判)'}
    doc = dict(base)
    doc['schema_version'] = '1.1'
    doc['generated_by'] = ('engine:view_plausibility.build_vp'
                           '(v1.1,R1 2026-11-11;R5 2026-11-11 覆盖面)')
    doc['as_of'] = snap.get('target_date')
    doc['lineage'] = {'prior_generated_by': base.get('generated_by'),
                      'prior_generation_basis': base.get('generation_basis'),
                      'upgraded': '2026-11-11 autonomous-rd R1: 三型证据落库;'
                                  '+R5: 假设引用并面+mode A 截断尾值近似;'
                                  'C 层契约零变动'}
    doc['generation_basis'] = (
        '引擎三型实跑(view_verifier A/B)×编排层 v1.0 语义映射;阶段标签='
        '假设证据评价(机构明示方向词表机械解析,trailing/since_publish 窗'
        '方向机械比对),非预测验证;view_label 仍=mode C 到期验证语义;'
        'R5(2026-11-11)证据面=观点 subjects 映射∪假设 metric_refs'
        '(hypothesis_ref),mode A 截断近似面 obs>publish 事实以截断序列'
        '尾值近似(level_source=series_tail_le_publish,DEGRADED)')
    doc['stage_summary'] = {
        'A': rollup_view_label(stage_a_labels),
        'B': rollup_view_label(stage_b_labels),
        'C': base.get('view_label'),
        'semantics': 'A=提出时假设证据 / B=发布后证据更新(证据评价,'
                     '非预测判定) / C=到期预测验证(未到期=不可判)'}
    ok, errs = validate_vp(doc, view_doc)
    if not ok:
        return {'ok': False, 'view_id': view_id,
                'error': {'kind': 'self_check_failed', 'message': errs}}
    if not dry_run:
        with open(vp_path(view_id, vp_dir), 'w', encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
    # R22 §5.3: 构建随行绑定复核(只入结果不入档,文件契约零扰动);
    # violation 经 validate_vp 纯校验已拦截写入,此处披露活体面(漂移等)。
    bind = binding_check(view_id=view_id, doc=doc, snapshot=snap,
                         registry=reg, vmap=vmap, views_dir=views_dir,
                         target_map=tmap, root=root)
    result = {'ok': True, 'view_id': view_id, 'written': not dry_run,
              'view_label': doc['view_label'],
              'stage_summary': doc['stage_summary'],
              'n_hypotheses': len(doc.get('hypotheses') or [])}
    if bind.get('rows') is not None:
        result['binding_summary'] = bind.get('summary')
    return result


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    vp_dir = None
    views_dir = None            # R22: --views-dir 注入缝(R17 tempdir 同款)
    data_root = None            # R22: --data-root 注入缝(CI 干净面/沙箱)
    args = list(argv)
    if '--vp-dir' in args:
        k = args.index('--vp-dir')
        if k + 1 >= len(args):
            print(json.dumps({'ok': False, 'error': {
                'kind': 'usage', 'message': '--vp-dir 须跟目录'}}, ensure_ascii=False))
            return 2
        vp_dir = args[k + 1]
        del args[k:k + 2]
    if '--views-dir' in args:
        k = args.index('--views-dir')
        if k + 1 >= len(args):
            print(json.dumps({'ok': False, 'error': {
                'kind': 'usage', 'message': '--views-dir 须跟目录'}},
                             ensure_ascii=False))
            return 2
        views_dir = args[k + 1]
        del args[k:k + 2]
    if '--data-root' in args:
        k = args.index('--data-root')
        if k + 1 >= len(args):
            print(json.dumps({'ok': False, 'error': {
                'kind': 'usage', 'message': '--data-root 须跟目录'}},
                             ensure_ascii=False))
            return 2
        data_root = args[k + 1]
        del args[k:k + 2]
    # R1: --build VIEW-ID | --build-all [--dry-run](三型证据落库,见 build_vp)
    dry = '--dry-run' in args
    if dry:
        args.remove('--dry-run')
    # R22(Charter 10 §5.3): 标签-证据绑定活体复核(重跑 mode C 比对声明标签)
    if args and args[0] == '--verify-binding':
        if len(args) != 2 or not args[1].startswith('VIEW-'):
            print(json.dumps({'ok': False, 'error': {
                'kind': 'usage', 'message': '用法: --verify-binding '
                        'VIEW-YYYYMMDD-NNN [--vp-dir DIR]'}}, ensure_ascii=False))
            return 2
        out = binding_check(view_id=args[1], vp_dir=vp_dir,
                            views_dir=views_dir, root=data_root)
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
        return 0 if out.get('ok') else 1
    if args and args[0] == '--build':
        if len(args) != 2 or not args[1].startswith('VIEW-'):
            print(json.dumps({'ok': False, 'error': {
                'kind': 'usage', 'message': '用法: --build VIEW-YYYYMMDD-NNN'
                        ' [--dry-run] [--vp-dir DIR]'}}, ensure_ascii=False))
            return 2
        out = build_vp(args[1], vp_dir=vp_dir, dry_run=dry)
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
        return 0 if out.get('ok') else 1
    if args and args[0] == '--build-all':
        docs, bad = load_all(vp_dir)
        results = [build_vp(d['view_id'], vp_dir=vp_dir, dry_run=dry)
                   for d in docs]
        ok_n = sum(1 for r in results if r.get('ok'))
        out = {'ok': ok_n == len(results) and len(results) > 0,
               'n': len(results), 'n_ok': ok_n,
               'dry_run': dry,
               'results': [{k: r.get(k) for k in
                            ('ok', 'view_id', 'view_label',
                             'stage_summary', 'error')}
                           for r in results]}
        if bad:
            out['skipped_bad_base'] = [f for f, _ in bad]
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
        return 0 if out['ok'] else 1
    if len(args) == 1 and args[0] == '--list':
        docs, bad = load_all(vp_dir)
        print(json.dumps({'ok': True, 'n': len(docs),
                          'views': [{'view_id': d.get('view_id'),
                                     'view_label': d.get('view_label'),
                                     'n_hypotheses': len(d.get('hypotheses') or [])}
                                    for d in docs],
                          'rejected': [{'file': f, 'reason': r} for f, r in bad]},
                         ensure_ascii=False, indent=2))
        return 0
    if len(args) != 1 or not args[0].startswith('VIEW-'):
        print(json.dumps({'ok': False, 'error': {
            'kind': 'usage', 'message': '用法: view_plausibility.py VIEW-YYYYMMDD-NNN'
                    ' | --list [--vp-dir DIR]'}}, ensure_ascii=False))
        return 2
    view_id = args[0]
    doc, reason = load_vp(view_id, vp_dir)
    if doc is None:
        print(json.dumps({'ok': False, 'error': {
            'kind': 'vp_not_found', 'message': reason}}, ensure_ascii=False))
        return 1
    view_doc, _ = vs.get_view(view_id)
    ok, errs = validate_vp(doc, view_doc)
    out = {'ok': ok, 'view_id': view_id,
           'view_label': doc.get('view_label'),
           'n_hypotheses': len(doc.get('hypotheses') or []),
           'hypotheses': doc.get('hypotheses'), 'as_of': doc.get('as_of'),
           'generated_by': doc.get('generated_by'),
           'disclosure': ('六标签最保守聚合(裁定④): 任一CONTRADICTED→至少MIXED;'
                          '全部NOT_YET_TESTABLE→NOT_YET_TESTABLE;SUPPORTED需全部'
                          '假设SUPPORTED——优先级表锁定于 tests/test_c9_vp_sidecar.py')}
    if not ok:
        out['errors'] = errs
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
