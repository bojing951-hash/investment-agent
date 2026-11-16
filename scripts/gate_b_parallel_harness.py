#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""新旧 Gate B 并行迁移框架(Product Convergence Phase 2;章程§五)。

目的: 旧 Gate B(scripts/data_validator.validate_report,生产值守)与新
text_consistency.check_text(迁移门)在**同一批真实周报**上并行跑,产出
可比对照+迁移判据评估。**只测量不迁移**——达标才迁由独立席+用户裁定,
本件禁改任何生产配置(达标才迁,不提前替换)。

用法:
  python3 scripts/gate_b_parallel_harness.py --reports output/weekly \
      [--snapshot data/snapshots/latest.json] [--out audit/gate_b_parallel/]

迁移判据(MC1-MC4,固定于本件 docstring 与 MIGRATION_CRITERIA——先固定
后测量,禁事后调标):
  MC1 真错零容忍: 新面 CONTRA token 全簇人工裁定=全误报(或真错=0)
     —— 以裁定档在档为凭(t7_realface_r43.json 形态),本件只做计数对照;
  MC2 误报下降: 新面 contra 计数 < 旧面 problems 计数(同报告同锚);
  MC3 连续性: 连续 ≥2 期真实周报同时满足 MC1+MC2;
  MC4 独立复核: 独立席对 MC1 裁定档的复核记录在场。
"""
import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

MIGRATION_CRITERIA = {
    'MC1': '新面 CONTRA 全簇裁定真错=0(裁定档在档,本件计数对照)',
    'MC2': '裁定基对比: 新面真错漏报=0 且新面误杀(裁定误报/总断言)严格低于旧面误杀率——裸计数不可比(旧=聚合 problems,新=逐 token 断言),裸计数仅作上下文并行披露',
    'MC3': '连续 ≥2 期真实周报满足 MC1+MC2',
    'MC4': '独立席复核 MC1 裁定档记录在场',
}


def hkt_now():
    return datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M HKT')


def run_old_gate_b(report_path, anchors):
    """旧 Gate B: data_validator.validate_report(生产值守面,只读调用)。"""
    import data_validator
    import io
    import contextlib
    problems = []
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            problems = data_validator.validate_report(report_path, anchors)
    except Exception as e:  # 如实记,不吞
        return {'error': f'{type(e).__name__}: {e}', 'problems': None, 'count': None}
    # validate_report 返回 problems 列表(空=过);打印面含 ❌/⚠ 行
    printed_errors = [l for l in buf.getvalue().splitlines() if '❌' in l]
    return {'problems': problems, 'count': len(problems) if problems is not None else None,
            'printed_error_lines': len(printed_errors)}


def run_new_gate_b(report_path, snapshot):
    """新 Gate B: text_consistency.check_text(迁移门面)。"""
    from research_contract import text_consistency as tc
    text = open(report_path, encoding='utf-8').read()
    try:
        r = tc.check_text(text, snapshot=snapshot)
    except Exception as e:
        return {'error': f'{type(e).__name__}: {e}', 'verdict': None, 'contra': None}
    checks = r.get('checks', [])
    st = r.get('stats') or {}
    contra = st.get('contradicted',
                    sum(1 for c in checks if c.get('status') == 'CONTRADICTED'))
    return {'verdict': r.get('verdict'), 'contra': contra,
            'total_checks': len(checks), 'unbound': st.get('unbound', len(r.get('unbound', [])))}


def load_snapshot(path):
    if os.path.isdir(path):
        cands = sorted(glob.glob(os.path.join(path, '*.json')))
        if not cands:
            raise SystemExit(f'快照目录空: {path}')
        path = cands[-1]
    return json.load(open(path, encoding='utf-8')), path


def main(argv=None):
    ap = argparse.ArgumentParser(description='新旧 Gate B 并行迁移框架(只测量不迁移)')
    ap.add_argument('--reports', required=True, nargs='+', help='周报文件/目录(多报一次成套)')
    ap.add_argument('--snapshot', required=True, nargs='+',
                    help='快照 json/目录,与报告一一对应(同源可比: 快照选择影响新面计数)')
    ap.add_argument('--out', default=os.path.join(ROOT, 'audit', 'gate_b_parallel'))
    args = ap.parse_args(argv)

    def _expand(p):
        return [p] if os.path.isfile(p) else sorted(glob.glob(os.path.join(p, '*.md')))
    reports = []
    for p in args.reports:
        reports.extend(_expand(p))
    if not reports:
        raise SystemExit(f'无报告: {args.reports}')
    snaps = []
    for p in args.snapshot:
        snaps.extend([p] if os.path.isfile(p) or os.path.isdir(p) else [])
    if len(snaps) == 1:
        snaps = snaps * len(reports)
    if len(snaps) != len(reports):
        raise SystemExit(f'快照数({len(snaps)})须与报告数({len(reports)})一致或为 1')
    loaded = [load_snapshot(sp) for sp in snaps]

    # 旧面锚点: 与生产同源(data_validator 自提取)
    import data_validator
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        anchors = data_validator.extract_anchors_from_data()

    os.makedirs(args.out, exist_ok=True)
    rows = []
    for rp, (snapshot, snap_path) in zip(reports, loaded):
        old = run_old_gate_b(rp, anchors)
        new = run_new_gate_b(rp, snapshot)
        rows.append({'report': os.path.basename(rp), 'snapshot_used': snap_path,
                     'old': old, 'new': new})
        print(f"{os.path.basename(rp)}: 旧 problems={old.get('count')} 新 contra={new.get('contra')} (verdict={new.get('verdict')})")

    # MC2 逐报评估(MC1/MC3/MC4=裁定档/连续期/独立席职责,本件只登记待评)
    mc2_rows = []
    for r in rows:
        # 裁定基 MC2 须人工裁定档;此处只产上下文裸计数+待评位(R44 首测发现:
        # 裸计数不可比——V1 旧 18 problems vs 新 46 token 断言,非同基)
        mc2_rows.append({'report': r['report'], 'raw_old_problems': r['old'].get('count'),
                         'raw_new_contra': r['new'].get('contra'),
                         'adjudicated_pass': 'PENDING(须裁定档,MC1 同源)'})
    result = {
        'generated_at': hkt_now(),
        'snapshot_provenance': '每报各自快照(见 comparison[].snapshot_used);跨跑可比性=同快照同 prior_anchors(prior_anchors 未接线=新面计数保守偏高等,如实注记)',
        'migration_criteria': MIGRATION_CRITERIA,
        'comparison': rows,
        'MC2_per_report': mc2_rows,
        'honest_note': '本件只测量;MC1/3/4 须裁定档+连续期+独立席,达标才迁(章程 Phase 2: 不提前替换生产 Gate B)',
    }
    out_json = os.path.join(args.out, 'parallel_result.json')
    json.dump(result, open(out_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'→ {out_json}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
