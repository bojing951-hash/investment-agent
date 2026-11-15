#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R41 真实面复跑器(T8-R2 遗留①定性收口,RDG-20261116-011 诊断实验)。

对 T7 三份真实周报(V1=20261114/V2=20261108/V3=20261024)用**当前引擎**
(本分支,含 R27/R35/R38-R40 修复面)全文重跑新链 tc.check_text,
与冻结基线 audit/arch-reform/T7/t7_results.json(T8 整改轮, V1 contra=53)
逐报告对照;CONTRA 全量列出(不截 40)供逐簇裁定。

只读 LIVE 树(报告+快照+锚链),零写入;产出
audit/arch-reform/T7/t7_realface_r41.json(机械复跑面;裁定面由独立席/开
发席另注 adjudication 节——机械与裁定分离,防先称毕)。

非 CI 套件(命名无 test_ 前缀,同 t7_parallel_harness 惯例)——依赖 LIVE
只读数据面,本仓克隆无此路径时明确跳过(exit 0 + SKIP 行)。
"""
import contextlib          # noqa: F401(保留给调用方静默复跑)
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

LIVE = ('/Users/cast/AI内容/🤖_AI投资项目/每周宏观追踪/'
        'investment-agent')

from research_contract import claim_factory as cf            # noqa: E402
from research_contract import text_consistency as tc          # noqa: E402

OUT = os.path.join(ROOT, 'audit', 'arch-reform', 'T7',
                   't7_realface_r41.json')
BASELINE = os.path.join(ROOT, 'audit', 'arch-reform', 'T7',
                        't7_results.json')


def main():
    if not os.path.isdir(LIVE):
        print('SKIP: LIVE 树不可达(克隆环境),真实面复跑为在位诊断件')
        return 0
    snap14 = json.load(open(os.path.join(
        ROOT, 'tests/fixtures/t6/snapshot_20261114_v2.json'),
        encoding='utf-8'))
    snap08 = json.load(open(os.path.join(
        LIVE, 'data/daily/research_snapshot_20261108_v2.json'),
        encoding='utf-8'))
    snap24 = json.load(open(os.path.join(
        LIVE, 'data/daily/research_snapshot_20261024.json'),
        encoding='utf-8'))
    anc14 = json.load(open(os.path.join(
        LIVE, 'data/daily/anchors_20261114.json'), encoding='utf-8'))
    anc08 = json.load(open(os.path.join(
        LIVE, 'data/daily/anchors_20261108.json'), encoding='utf-8'))
    anc31 = json.load(open(os.path.join(
        LIVE, 'data/daily/anchors_20261031.json'), encoding='utf-8'))
    import re
    anc24_files = sorted(p for p in os.listdir(os.path.join(
        LIVE, 'data/daily'))
        if re.match(r'anchors_202610(1[7-9]|2[0-4])\.json$', p))
    anc24 = json.load(open(os.path.join(LIVE, 'data/daily',
                                        anc24_files[-1]), encoding='utf-8'))
    thr = cf.load_thresholds()
    REAL = [
        ('V1', 'output/weekly/weekly_report_20261114_UNVALIDATED.md',
         snap14, {'2026-11-08': anc08, '2026-11-14': anc14}),
        ('V2', 'output/weekly/weekly_report_20261108_UNVALIDATED.md',
         snap08, {'2026-10-31': anc31, '2026-11-08': anc08}),
        ('V3', 'output/weekly/weekly_report_20261024.md',
         snap24, {}),
    ]
    base = json.load(open(BASELINE, encoding='utf-8'))
    out = {'note': 'R41 真实面复跑(RDG-20261116-011 诊断实验;机械面,'
                   'adjudication 节另注)',
           'engine': '本分支当前引擎(含 R27 GateB五缺陷/R35 利差披露/'
                     'R38-R40 叙事族修复面)',
           'baseline': 'audit/arch-reform/T7/t7_results.json(T8 整改轮)',
           'runs': {}}
    for vid, rel, snap, prior in REAL:
        text = open(os.path.join(LIVE, rel), encoding='utf-8').read()
        r = tc.check_text(text, snapshot=snap, thresholds=thr,
                          prior_anchors=prior or None)
        contra = [c for c in r['checks'] if c['status'] == 'CONTRADICTED']
        clusters = {}
        for c in contra:
            key = f"{c['family']}|{c.get('metric')}"
            clusters.setdefault(key, []).append(
                str(c.get('token'))[:24])
        b = base['runs'].get(vid, {}).get('new', {}).get(
            'stats', {})
        out['runs'][vid] = {
            'file': os.path.basename(rel),
            'verdict': r['verdict'], 'stats': r['stats'],
            'baseline_stats': b,
            'delta_contradicted': (r['stats']['contradicted']
                                   - b.get('contradicted', 0)),
            'clusters': {k: {'n': len(v), 'tokens': v[:8]}
                         for k, v in sorted(
                             clusters.items(),
                             key=lambda kv: -len(kv[1]))},
            'contradicted_full': [
                {'family': c['family'], 'token': c.get('token'),
                 'metric': c.get('metric'),
                 'note': (c.get('note') or '')[:90],
                 'co_anchor': c.get('co_anchor')}
                for c in contra],
        }
        print(f"[{vid}] {r['verdict']} contra="
              f"{r['stats']['contradicted']} (基线 {b.get('contradicted')})"
              f" veri={r['stats']['verified']} "
              f"unbound={r['stats']['unbound']}")
        for k, v in out['runs'][vid]['clusters'].items():
            print(f"    {v['n']:3d}  {k}  例: {v['tokens'][:3]}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(f"→ {OUT}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
