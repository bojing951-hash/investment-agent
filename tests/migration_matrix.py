# -*- coding: utf-8 -*-
"""T6c/T7 迁移矩阵跑台(公开面 V5/V6;仓内夹具优先): V5(注入错误→须 CONTRADICTED) + V6(改写变体→须 VERIFIED)。

用法:
    python3 tests/migration_matrix.py            # 摘要
    python3 tests/migration_matrix.py -v V5-013  # 单项细节(含逐 check)
    python3 tests/migration_matrix.py --fails    # 只列失败项

工件只读: QA 夹具(agent-loop)/t6 快照副本;禁读 heldout-sealed(封存件仅 T8
独立审计席开封)。
"""
import json
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from research_contract import claim_factory as cf          # noqa: E402
from research_contract import text_consistency as tc        # noqa: E402

QA_DIR = os.path.join(HERE, 'fixtures', 'qa')          # 公开面仓内副本
QA_FALLBACK = '/Users/cast/agent-loop/ARCH-REFORM/QA'   # 本机原件
FX = os.path.join(HERE, 'fixtures', 't6')


def load():
    snap = json.load(open(os.path.join(FX, 'snapshot_20261114_v2.json')))
    prior = {'2026-10-24': json.load(open(os.path.join(FX, 'anchors_20261024.json'))),
             '2026-10-31': json.load(open(os.path.join(FX, 'anchors_20261031.json'))),
             '2026-11-08': json.load(open(os.path.join(FX, 'anchors_20261108.json'))),
             '2026-11-14': json.load(open(os.path.join(FX, 'anchors_20261114.json')))}
    def _qa(name):
        p = os.path.join(QA_DIR, name)
        if not os.path.exists(p):
            p = os.path.join(QA_FALLBACK, name)
        return json.load(open(p))['items']
    v5, v6 = _qa('V5-INJECTIONS.json'), _qa('V6-PARAPHRASES.json')
    thr = cf.load_thresholds()
    return snap, prior, thr, v5, v6


# 时代面(T8 整改 HC-1/HC-2): 留出条目自带 base_anchor_set,
# 须按其时代取快照+锚链(V6-S03=20261108 面: UST_30Y 5.25 时代)。
ERAS = {
    '20261114': {
        'snapshot': 'snapshot_20261114_v2.json',
        'prior': ['anchors_20261024.json', 'anchors_20261031.json',
                  'anchors_20261108.json', 'anchors_20261114.json'],
    },
    '20261108': {
        'snapshot': 'snapshot_20261108_v2.json',
        'prior': ['anchors_20261024.json', 'anchors_20261031.json',
                  'anchors_20261108.json'],
    },
}


def load_era(era='20261114'):
    """按时代取 (snapshot, prior_anchors, thresholds);未知时代=fail-closed。"""
    spec = ERAS.get(era)
    if spec is None:
        raise KeyError(f'未知时代面: {era}(须先登记 ERAS,禁静默回退)')
    snap = json.load(open(os.path.join(FX, spec['snapshot'])))
    prior = {}
    for fn in spec['prior']:
        d = fn.replace('anchors_', '').replace('.json', '')
        prior[f'{d[:4]}-{d[4:6]}-{d[6:]}'] = json.load(
            open(os.path.join(FX, fn)))
    return snap, prior, cf.load_thresholds()


def run(snap, prior, thr, items):
    out = []
    for it in items:
        r = tc.check_text(it['text'], snapshot=snap, thresholds=thr,
                          prior_anchors=prior)
        out.append((it, r))
    return out


def main():
    verbose = None
    fails_only = '--fails' in sys.argv
    for a in sys.argv[1:]:
        if a.startswith('-v'):
            verbose = a[2:] if len(a) > 2 else None
    snap, prior, thr, v5, v6 = load()
    rows = []
    if not verbose or verbose.startswith('V5'):
        rows += [('V5', it, r) for it, r in run(snap, prior, thr, v5)]
    if not verbose or verbose.startswith('V6'):
        rows += [('V6', it, r) for it, r in run(snap, prior, thr, v6)]
    n_ok = n_bad = 0
    for setname, it, r in rows:
        want = 'CONTRADICTED' if setname == 'V5' else 'VERIFIED'
        got = r['verdict']
        ok = got == want
        n_ok += ok
        n_bad += (not ok)
        tag = 'PASS' if ok else 'FAIL'
        if verbose == it['id'] or (not verbose and (not ok or not fails_only)):
            s = r['stats']
            print(f"[{tag}] {it['id']} {it.get('fault_family') or it.get('variant_group','')}"
                  f" want={want} got={got} (checks={s['checks']} contra={s['contradicted']}"
                  f" veri={s['verified']} unbound={s['unbound']})")
        if verbose == it['id']:
            for c in r['checks']:
                print(f"   {c['status'][:4]} {c['family']:<22} {c.get('token','')!r:<14}"
                      f" v={c.get('value')} exp={c.get('expected')} | {c.get('note','')}")
            for u in r['unbound']:
                print(f"   unb  {u['raw']!r:<14} {u['ctx']}")
    print(f"\nTOTAL ok={n_ok} fail={n_bad} / {len(rows)}")


if __name__ == '__main__':
    main()
