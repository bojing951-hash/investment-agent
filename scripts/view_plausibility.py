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
退出码: 0=装载校验成功;1=缺失/不可用;2=用法错。
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


def verdict_to_label(verdict):
    """mode C verdict → 六标签(未知 verdict→INSUFFICIENT_EVIDENCE,不猜)。"""
    return VERDICT_TO_LABEL.get(str(verdict), 'INSUFFICIENT_EVIDENCE')


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
    if doc.get('schema_version') != '1.0':
        errs.append('schema_version 须为 "1.0"')
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
    declared = doc.get('view_label')
    recomputed = rollup_view_label([h.get('label') for h in hyps
                                    if isinstance(h, dict)])
    if declared != recomputed:
        errs.append(f'view_label({declared!r})与最保守聚合({recomputed!r})不符'
                    '——写入方须用 rollup_view_label 生成')
    return (not errs), errs


def vp_badge_rows(vp_doc):
    """sidecar → 页③徽标表行(纯函数,app/测试共用)。"""
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
        rows.append({'ref': ref_txt, '标签': h.get('label'),
                     '指标链': chain, '判定依据': basis})
    return rows


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    vp_dir = None
    args = list(argv)
    if '--vp-dir' in args:
        k = args.index('--vp-dir')
        if k + 1 >= len(args):
            print(json.dumps({'ok': False, 'error': {
                'kind': 'usage', 'message': '--vp-dir 须跟目录'}}, ensure_ascii=False))
            return 2
        vp_dir = args[k + 1]
        del args[k:k + 2]
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
