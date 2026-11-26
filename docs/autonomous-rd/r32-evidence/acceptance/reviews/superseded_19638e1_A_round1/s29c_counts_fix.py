#!/usr/bin/python3 -I
"""Seat-internal: sync the verdict file with the ledger after s24_sync_labels.py (910 counted / 42 informational)
and extend the `where` of the mixed-window item to the C1 statement.

Usage:
  python3 -I s29c_counts_fix.py <VERDICT-round1.json> <points_all.jsonl>
"""
import json
import sys


def once(s, frag):
    assert s.count(frag) == 1, (frag, s.count(frag))
    return s.index(frag)


def main():
    with open(sys.argv[2], 'r', encoding='utf-8') as f:
        rows = [json.loads(x) for x in f if x.strip()]
    counted = [r for r in rows if not (r.get('reported') is None and r.get('computed') is not None)]
    info = len(rows) - len(counted)
    bad = sum(1 for r in counted if not r.get('ok'))
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        v = json.load(f)
    n = v['notes']
    old = u'计点 904、偏离 0(另 39 行仅作信息记录,不计入);覆盖锚点 275、月频 147、日频 133、历史 296、同步标签 36、其他 17。'
    new = (u'计点 %d、偏离 %d(另 %d 行仅作信息记录,不计入);覆盖锚点 275、月频 147、日频 133、历史 293、'
           u'同步面 45(引擎全维表 36 格+判断档通胀维标签 9 格)、其他 17。') % (len(counted), bad, info)
    if old in n:
        n = n.replace(old, new)
    else:
        # already updated: only refresh the counts
        i = once(n, u'计点 ')
        j = once(n, u'其他 ')
        k = n.index(u'。', j)
        n = n[:i] + new[:-1] + n[k:]
    assert u'910' in n and u'904' not in n
    v['notes'] = n
    v['recompute_points'] = len(counted)
    v['recompute_mismatches'] = bad
    # extend the where of the mixed-window item (the one whose note mentions 混窗)
    hit = 0
    for it in v['items']:
        if it['severity'] == 'MINOR' and u'l3.mechanism_chains[0].links[2].text' in it['where']:
            w = it['where']
            if u'l3.contradictions[0].statement' not in w:
                assert w.startswith(u'agent_judgment.json ')
                it['where'] = (u'agent_judgment.json l3.contradictions[0].statement(首句『过去12个月…同向共动』);' + w[len(u'agent_judgment.json '):])
            hit += 1
    assert hit == 1, hit
    with open(sys.argv[1], 'w', encoding='utf-8') as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write(u'\n')
    print('recompute_points=%d mismatches=%d informational=%d' % (len(counted), bad, info))
    print(n[:420])


if __name__ == '__main__':
    main()
