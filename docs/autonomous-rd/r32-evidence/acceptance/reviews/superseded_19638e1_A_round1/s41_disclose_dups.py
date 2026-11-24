#!/usr/bin/python3 -I
"""Seat-internal: disclose, inside the notes of VERDICT-round1.json (argv[2]), that two observation values
of the seat ledger (argv[1]) are each recorded twice because the judgment cites them at two places.
No count is changed; a backup copy of the verdict is written next to it first.  Refuses to run twice.

Usage:
  python3 -I s41_disclose_dups.py <points_all.jsonl> <VERDICT-round1.json>
"""
import json
import shutil
import sys
from collections import Counter


def main():
    rows = [json.loads(x) for x in open(sys.argv[1], encoding='utf-8') if x.strip()]
    vpath = sys.argv[2]
    v = json.load(open(vpath, encoding='utf-8'))
    c = Counter(r['id'] for r in rows)
    dups = sorted(k for k, n in c.items() if n > 1)
    assert dups == ['CORE_PCE yoy 2026-09', 'CPI yoy 2026-07'], dups
    for k in dups:
        rs = [r for r in rows if r['id'] == k]
        assert all(r['ok'] and r['computed'] == rs[0]['computed'] and r['reported'] == rs[0]['reported'] for r in rs)

    n = v['notes']
    old = u'计点 %d、偏离 %d(另 %d 行仅作信息记录,不计入);' % (v['recompute_points'], v['recompute_mismatches'], 43)
    assert n.count(old) == 1, n.count(old)
    new = (u'计点 %d、偏离 %d(另 %d 行仅作信息记录,不计入;另有 2 个观测值[CPI 同比 2026-07、核心 PCE 同比 2026-09]'
           u'各因在判断档两处被引用而按引用处记两行,按观测值去重为 %d 点);' % (v['recompute_points'], v['recompute_mismatches'], 43, v['recompute_points'] - 2))
    n = n.replace(old, new)
    assert '\n' not in n
    v['notes'] = n
    order = ['seat', 'reviewer', 'verdict', 'overall', 'notes', 'items', 'must_fix', 'counterexamples_sought',
             'recompute_points', 'recompute_mismatches', 'mismatch_details', 'audited_at']
    assert list(v.keys()) == order
    shutil.copyfile(vpath, vpath.replace('.json', '.before-dups.json'))
    with open(vpath, 'w', encoding='utf-8') as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('notes len: %d' % len(n))
    print(n[:n.find(u';覆盖')] + u';(…)')
    print('recompute_points=%d recompute_mismatches=%d' % (v['recompute_points'], v['recompute_mismatches']))


if __name__ == '__main__':
    main()
