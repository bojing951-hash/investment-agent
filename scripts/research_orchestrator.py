#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R2 一键研究编排器(AC6): Skill 十一步研究工作流的可执行化。

定位与边界(零模型诚实面):
- 本编排器只执行**确定性步骤**(体检/事实基线/历史/对比/类比/接地问答/
  观点面装载/lint 自检/落档开关),每步=真 ia_cli 子进程或既有库装载,
  信封原样留档——步骤成败与语义成败分开记录。
- 拆问题(自然语言)/主要矛盾综合/条件推演五行=编排层 Agent 工作,
  本管线不产出: L3(AI推断)/L4(条件情景) 两层恒 declared-not-produced,
  报告明示"本层结论须 Agent 补作并标 attribution",绝不代写。
- 实体映射=确定性词面匹配(metric_id/display_name 大小写折叠子串+
  经济体中文标签反查),匹配不到就如实 unmapped,零翻译零猜测。

四层区分(L1-L4)与逐数证据索引(evidence_index: 每个数字行带
fact_id/view_id 级来源)随报告落盘 report.json+report.md。

纯函数入口: run_research(question, root=None, archive=False, out_dir=None,
ia_timeout=180) → dict(ia_cli research-run 与测试共用)。
"""
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
SCRIPTS = os.path.join(ROOT, 'scripts')
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

PIPELINE_VERSION = '2.0'
IA_CLI = os.path.join(ROOT, 'ia_cli.py')


def _now_utc():
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def _slug(text, maxlen=40):
    s = re.sub(r'[^A-Za-z0-9一-鿿]+', '_', text).strip('_')
    return (s[:maxlen] or 'question')


def run_step(name, argv, timeout=180):
    """跑一步真 ia_cli 子进程;进程成败/语义成败/信封三层分开记录。"""
    t0 = time.monotonic()
    try:
        p = subprocess.run([sys.executable, IA_CLI] + argv,
                           capture_output=True, text=True, timeout=timeout,
                           cwd=ROOT)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return {'step': name, 'argv': argv, 'executed': True,
                'ok': False, 'exit_code': None,
                'note': f'超时(>{timeout}s)', 'duration_ms': None,
                'envelope': None}
    env = None
    try:
        env = json.loads(out)
    except ValueError:
        pass
    return {'step': name, 'argv': argv, 'executed': True,
            'ok': rc == 0,
            'exit_code': rc,
            'semantic_ok': bool(env.get('ok')) if isinstance(env, dict) else None,
            'note': (err.strip()[:200] or None) if rc != 0 and env is None else None,
            'duration_ms': int((time.monotonic() - t0) * 1000),
            'envelope': env}


def skipped_step(name, note):
    return {'step': name, 'argv': [], 'executed': False, 'ok': True,
            'exit_code': None, 'skipped_reason': note, 'envelope': None}


def map_entities(question, reg):
    """确定性实体映射: 指标(metric_id/display_name 折叠子串)+经济体(中文标签反查)。

    匹配不到=如实 unmapped(零翻译零猜测;Agent 可后续补语义层)。"""
    q = question.casefold()
    metrics = []
    for m in (reg.get('metrics') or []):
        mid = (m.get('metric_id') or '')
        names = [mid, m.get('display_name') or '']
        if any(n and n.casefold() in q for n in names):
            metrics.append(mid)
    economies = []
    import workbench_data as wd
    for code, label in (wd.ECONOMY_LABELS or {}).items():
        # 代码用词边界(防 'EA' 命中 tr'ea'sury 类子串误报);中文标签直接子串
        if label and (label in question
                      or re.search(r'\b' + re.escape(code.casefold()) + r'\b', q)):
            economies.append(code)
    note = None
    if not metrics:
        note = ('问题未词面命中任何指标(零模型不做语义翻译);'
                '事实面降级为经济体概览,接地问答步骤仍如实作答/拒答')
    return {'metrics': metrics, 'economies': economies, 'note': note}


def _fact_rows(snap, metric_ids):
    """L1 行: 快照事实直取(逐行 fact_id 证据;不猜不补)。

    无指标命中时不倾倒全量事实(防噪)——基线层只给计数,裸数行须有映射。"""
    if not metric_ids:
        return []
    rows = []
    for f in snap.get('facts') or []:
        if f.get('metric_id') not in metric_ids:
            continue
        rows.append({'metric_id': f.get('metric_id'),
                     'value': f.get('value'), 'unit': f.get('unit'),
                     'observation_date': f.get('observation_date'),
                     'quality_status': f.get('quality_status'),
                     'source': {'kind': 'snapshot_fact', 'id': f.get('fact_id')}})
    return rows


def vp_face(root):
    """L2 原料: VP sidecar 装载(标签/阶段摘要;缺席如实 None)。"""
    try:
        import view_plausibility as vp
        docs, bad = vp.load_all()
    except Exception as e:  # noqa: BLE001 —— 缺席/不可读=如实降级,不阻断管线
        return {'available': False, 'note': f'VP 装载失败: {e}'}
    if not docs:
        note = 'VP sidecar 缺席(data/ 本地层;干净 clone 常态)'
        if bad:
            note += f';另有 {len(bad)} 份坏档隔离不入面'
        return {'available': False, 'note': note}
    rows = []
    for doc in docs:
        vid = doc.get('view_id')
        rows.append({'view_id': vid,
                     'view_label': doc.get('view_label'),
                     'stage_summary': doc.get('stage_summary'),
                     'source': {'kind': 'vp_sidecar', 'id': f'VP-{vid}'}})
    return {'available': True, 'n': len(rows), 'rows': rows,
            'n_bad_quarantined': len(bad)}


def run_research(question, root=None, archive=False, out_dir=None,
                 ia_timeout=180):
    """十一步一键研究管线;返回完整报告 dict(run_ok=进程层,语义面看各步)。"""
    root = root or ROOT
    import workbench_data as wd
    steps = []
    notes = []

    # ── S1 拆问题(确定性面) ─────────────────────────────────────────
    reg = wd.load_registry(root)
    ent = map_entities(question, reg)
    steps.append({'step': 'S1_decompose', 'executed': True, 'ok': True,
                  'deterministic_face': ent,
                  'agent_face_note': '自然语言深拆/主要矛盾综合=编排层 Agent;'
                                     '本步只给确定性实体映射'})

    # ── S2 doctor 体检 ──────────────────────────────────────────────
    steps.append(run_step('S2_doctor', ['doctor'], ia_timeout))

    # ── S3 事实基线(overview+changes) ───────────────────────────────
    ecos = ent['economies'] or ['US', 'CN']
    for eco in ecos:
        steps.append(run_step(f'S3_overview_{eco}',
                              ['overview', '--economy', eco], ia_timeout))
    steps.append(run_step('S3_changes', ['changes'], ia_timeout))

    # ── S4 历史可得性(命中指标逐个;未命中=跳过如实) ─────────────────
    hist_metrics = ent['metrics'][:4]
    if len(ent['metrics']) > 4:
        notes.append(f"命中 {len(ent['metrics'])} 个指标,历史步骤只取前 4"
                     f"(防噪);其余由 Agent 按需 history --metric 查询")
    for mid in hist_metrics:
        steps.append(run_step(f'S4_history_{mid}',
                              ['history', '--metric', mid], ia_timeout))
    if not hist_metrics:
        steps.append(skipped_step(
            'S4_history', '问题未命中指标——零实体映射时如实跳过(不造数)'))

    # ── S5 对齐自配对(≥2 命中才可比) ────────────────────────────────
    if len(hist_metrics) >= 2:
        steps.append(run_step('S5_compare',
                              ['compare', '--metrics',
                               ','.join(hist_metrics[:2])], ia_timeout))
    else:
        steps.append(skipped_step(
            'S5_compare', '命中指标不足 2 个,无可对齐自配对(如实跳过)'))

    # ── S6 历史相似结构(analog;短历史诚实拒答透传) ─────────────────
    steps.append(run_step('S6_analog', ['analog'], ia_timeout))

    # ── S7 research_mode_gate(从 compare/analog 信封提取,无独立命令) ─
    gate = None
    for s in steps:
        env = s.get('envelope')
        if isinstance(env, dict):
            g = ((env.get('data') or {}).get('research_mode_gate')
                 if isinstance(env.get('data'), dict) else None)
            if g is None:
                g = env.get('research_mode_gate')
            if g is not None:
                gate = g
                break
    steps.append({'step': 'S7_mode_gate', 'executed': True, 'ok': gate is not None,
                  'gate': gate,
                  'note': None if gate else 'compare/analog 信封未含 gate'
                          '(本轮无可比对/被拒答)——如实缺席,不编造'})

    # ── S8 接地问答(ia_cli research;archive 开关在此一次性落档) ────
    qa_argv = ['research', '--question', question]
    if archive:
        qa_argv += ['--archive',
                    '--note', 'R2 research-run 一键编排落档']
    steps.append(run_step('S8_grounded_qa', qa_argv, ia_timeout))

    # ── S9 观点面(views lint + VP 装载) ────────────────────────────
    steps.append(run_step('S9_views_lint', ['views', 'lint'], ia_timeout))
    vpf = vp_face(root)

    # ── S10 lint/自检: views 违规数+证据索引完整性 ──────────────────
    lint_step = next((s for s in steps if s['step'] == 'S9_views_lint'), {})
    n_quarantined = ((((lint_step.get('envelope') or {}).get('data'))
                      or {}).get('n_quarantined'))

    snap, snap_note = wd.latest_snapshot(root)
    facts = snap.get('facts') if snap else None
    l1_rows = _fact_rows(snap or {}, set(hist_metrics)) if facts else []

    layers = {
        'L1_事实层': {
            'available': snap is not None,
            'snapshot_id': (snap or {}).get('snapshot_id'),
            'target_date': (snap or {}).get('target_date'),
            'n_facts_total': len(facts or []),
            'rows': l1_rows,
            'note': None if snap else f'快照缺席: {snap_note}',
        },
        'L2_机构观点层': {
            'views': vpf,
            'note': '标签=证据评价非预测判定;阶段摘要 A/B/C 见 VP sidecar',
        },
        'L3_AI推断层': {
            'produced': False,
            'note': '零模型管线: 本层(矛盾综合/推断)须编排层 Agent 补作,'
                    'attribution=ai_inferred——本管线绝不代写',
        },
        'L4_条件情景层': {
            'produced': False,
            'note': '条件推演五行(前提/机制/路径/观察指标/推翻条件)归编排层'
                    'Agent;不冒充预测——本管线绝不代写',
        },
    }

    # 证据索引: 每个数字行必须有 fact_id/view_id 级来源
    evidence_index = []
    for r in l1_rows:
        evidence_index.append({'ref': r['source']['id'],
                               'kind': r['source']['kind'],
                               'metric_id': r['metric_id']})
    for r in (vpf.get('rows') or []):
        evidence_index.append({'ref': r['source']['id'],
                               'kind': r['source']['kind'],
                               'view_label': r['view_label']})
    missing_ref = [r['metric_id'] for r in l1_rows if not r['source']['id']]
    selfcheck = {'n_evidence_rows': len(evidence_index),
                 'n_rows_missing_ref': len(missing_ref),
                 'ok': not missing_ref}
    steps.append({'step': 'S10_selfcheck', 'executed': True,
                  'ok': bool(selfcheck['ok']),
                  'n_views_quarantined': n_quarantined,
                  'selfcheck': selfcheck,
                  'note': None if selfcheck['ok'] else f'缺来源行: {missing_ref}'})

    # ── S11 落档(S8 一次性完成;默认关) ─────────────────────────────
    qa_env = next((s.get('envelope') for s in steps
                   if s.get('step') == 'S8_grounded_qa'), {}) or {}
    archived_id = ((qa_env.get('data') or {}).get('archived_query_id')
                   if isinstance(qa_env, dict) else None)
    steps.append({'step': 'S11_archive', 'executed': True,
                  'ok': (archived_id is not None) if archive else True,
                  'archive_requested': bool(archive),
                  'archived_query_id': archived_id,
                  'note': ('已随 S8 落档' if archived_id
                           else '默认关(--archive 显式开启;Skill 第 11 步=用户认可后)')})

    if ent['note']:
        notes.append(ent['note'])

    run_ok = all(s.get('ok') for s in steps if s.get('executed'))
    report = {
        'schema_version': '2.0',
        'pipeline_version': PIPELINE_VERSION,
        'run': {'question': question, 'ts_utc': _now_utc(),
                'archive_requested': bool(archive),
                'git_head': _git_head(root)},
        'steps': steps,
        'layers': layers,
        'evidence_index': evidence_index,
        'notes': notes,
        'run_ok': run_ok,
    }

    out_root = out_dir or os.path.join(root, 'output', 'research_runs')
    run_dir = os.path.join(out_root, f"{report['run']['ts_utc']}_{_slug(question)}")
    os.makedirs(run_dir, exist_ok=True)
    with open(os.path.join(run_dir, 'report.json'), 'w',
              encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    with open(os.path.join(run_dir, 'report.md'), 'w',
              encoding='utf-8') as f:
        f.write(_render_md(report))
    report['report_dir'] = run_dir
    return report


def _git_head(root):
    try:
        p = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
                           capture_output=True, text=True, timeout=10, cwd=root)
        return p.stdout.strip() if p.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _render_md(r):
    """人类可读面: 四层区分+步骤台账+证据索引(数字行全部带来源)。"""
    q = r['run']['question']
    L = r['layers']
    lines = [f"# 一键研究报告(零模型编排 v{r['pipeline_version']})",
             f"- 问题: {q}",
             f"- 运行: {r['run']['ts_utc']} @ {r['run'].get('git_head')}",
             f"- 快照: {L['L1_事实层'].get('snapshot_id')} "
             f"(target {L['L1_事实层'].get('target_date')})",
             '', '## 四层区分', '']
    l1 = L['L1_事实层']
    lines.append(f"### L1 事实层 available={l1['available']}"
                 + ('' if l1['available'] else f"({l1['note']})"))
    for row in l1['rows']:
        lines.append(f"- {row['metric_id']} = {row['value']} {row['unit'] or ''}"
                     f" @{row['observation_date']}"
                     f" [来源:{row['source']['kind']}:{row['source']['id']}]")
    vpf = L['L2_机构观点层']['views']
    lines.append(f"\n### L2 机构观点层 "
                 f"available={vpf.get('available')}"
                 + (f" n={vpf['n']}" if vpf.get('available')
                    else f"({vpf.get('note')})"))
    for row in (vpf.get('rows') or []):
        ss = row.get('stage_summary') or {}
        lines.append(f"- {row['view_id']}: view_label={row['view_label']}"
                     f" 阶段摘要={ {k: ss.get(k) for k in ('A', 'B', 'C')} }")
    lines.append(f"\n### L3 AI推断层 produced={L['L3_AI推断层']['produced']}"
                 f"\n> {L['L3_AI推断层']['note']}")
    lines.append(f"\n### L4 条件情景层 produced={L['L4_条件情景层']['produced']}"
                 f"\n> {L['L4_条件情景层']['note']}")
    lines += ['', '## 步骤台账', '']
    for s in r['steps']:
        tag = 'OK ' if s.get('ok') else ('SKIP' if not s.get('executed') else 'FAIL')
        extra = s.get('skipped_reason') or s.get('note') or ''
        lines.append(f"- [{tag}] {s['step']} {extra}")
    lines += ['', f"## 证据索引({len(r['evidence_index'])} 行)", '']
    for e in r['evidence_index'][:60]:
        lines.append(f"- {e['kind']}:{e['ref']}"
                     + (f" → {e['metric_id']}" if e.get('metric_id') else '')
                     + (f" [{e['view_label']}]" if e.get('view_label') else ''))
    if r['notes']:
        lines += ['', '## 注记', ''] + [f"- {n}" for n in r['notes']]
    lines.append('')
    return '\n'.join(lines)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    import argparse
    p = argparse.ArgumentParser(description='一键研究编排(十一步确定性管线,零模型)')
    p.add_argument('--question', required=True)
    p.add_argument('--archive', action='store_true',
                   help='落档(Skill 第 11 步=用户认可后;默认关)')
    p.add_argument('--out-dir', default=None)
    p.add_argument('--root', default=ROOT)
    a = p.parse_args(argv)
    rep = run_research(a.question, root=a.root, archive=a.archive,
                       out_dir=a.out_dir)
    print(json.dumps({'run_ok': rep['run_ok'],
                      'report_dir': rep['report_dir'],
                      'n_steps': len(rep['steps']),
                      'n_evidence_rows': len(rep['evidence_index'])},
                     ensure_ascii=False, indent=2))
    return 0 if rep['run_ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
