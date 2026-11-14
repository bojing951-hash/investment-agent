#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""迁移门跑台(指定夹具文件;公开面/留出面同配置同命令)。

用法:
    python3 tests/run_matrix_dir.py <fixture.json>   # V5 形→须全 CONTRADICTED;
                                                     # V6 形→须全 VERIFIED
    python3 tests/run_matrix_dir.py --p4             # P4 五处真实值复位

配置 = migration_matrix.load_era()(仓内 t6 快照/锚链/thresholds;
条目自带 base_anchor_set 者按其时代取面——公开面与留出面同一命令同一机制)。
判定: 任一条目不达预期 → 退出码 1;unmapped>0 一并列败(P5)。
"""
import json
import sys

from migration_matrix import load_era
from research_contract import text_consistency as tc


def run_file(path):
    items = json.load(open(path))['items']
    is_v5 = 'fault_family' in items[0]        # V5 形态判定
    want = 'CONTRADICTED' if is_v5 else 'VERIFIED'
    era_cache = {}
    bad, unmapped = [], []
    for it in items:
        era = it.get('base_anchor_set', '20261114')
        if era not in era_cache:
            era_cache[era] = load_era(era)
        snap, prior, thr = era_cache[era]
        r = tc.check_text(it['text'], snapshot=snap, thresholds=thr,
                          prior_anchors=prior)
        unb = [u['raw'] for u in r['unbound']]
        unmapped += [(it['id'], u) for u in unb]
        ok = r['verdict'] == want
        if not ok:
            bad.append((it['id'], r['verdict']))
        print(f"[{'OK' if ok else 'BAD'}] {it['id']}"
              f"{'/' + it['fault_family'] if is_v5 else ''}"
              f" era={era} want={want} got={r['verdict']}"
              f" (contra={r['stats']['contradicted']}"
              f" veri={r['stats']['verified']} unbound={len(unb)})")
    print(f"\nTOTAL {len(items) - len(bad)}/{len(items)} 达标;"
          f" unmapped={len(unmapped)}")
    if unmapped:
        print('unmapped 明细:', unmapped[:10])
    return not bad and not unmapped


def run_p4():
    from migration_matrix import load_era as _le
    snap, prior, thr = _le('20261114')
    snap08, prior_v2, _ = _le('20261108')
    cases = [
        ('V1-滞后166天', 'SPX_EPS/PE_TTM滞后166天，本月数据的时效性受限',
         snap, prior),
        ('V1-距离0.80pp', 'HY OAS 3.20%（警告线400bp=4.00%，距离0.80pp）',
         snap, prior),
        ('V1-DXY周+1.09%', 'DXY 103.41（+1.09%）', snap, prior),
        ('V2-VIX桥式+32.03%至25.64', 'VIX +32.03%至25.64', snap08, prior_v2),
        ('V2-顿号零售+0.77%', '零售销售环比+0.77%', snap08, prior_v2),
    ]
    bad = []
    for name, frag, sn, pr in cases:
        r = tc.check_text(frag, snapshot=sn, thresholds=thr, prior_anchors=pr)
        print(f"[{'OK' if r['verdict'] == 'VERIFIED' else 'BAD'}] {name}: "
              f"{r['verdict']}")
        if r['verdict'] != 'VERIFIED':
            bad.append(name)
    print(f"\nP4 {len(cases) - len(bad)}/{len(cases)} 复位 VERIFIED")
    return not bad


if __name__ == '__main__':
    if '--p4' in sys.argv:
        sys.exit(0 if run_p4() else 1)
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(0 if run_file(sys.argv[1]) else 1)
