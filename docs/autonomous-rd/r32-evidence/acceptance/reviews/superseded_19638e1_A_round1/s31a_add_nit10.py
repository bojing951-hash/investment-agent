#!/usr/bin/python3 -I
"""Seat-internal: add NIT-10 (presumed CPI publication dates falling on week-ends) to the verdict file
and keep `notes` consistent (NIT count, contract-verification coverage caveat).

Usage:
  python3 -I s31a_add_nit10.py <VERDICT-round1.json> <agent_judgment.json>
"""
import json
import sys


def once(s, frag):
    assert s.count(frag) == 1, (frag, s.count(frag))
    return s.index(frag)


def main():
    v = json.load(open(sys.argv[1], encoding='utf-8'))
    jud = json.load(open(sys.argv[2], encoding='utf-8'))
    blob = json.dumps(jud, ensure_ascii=False)
    orig1 = u'2026-05 高点 4.17(推定发布 2026-06-13)'
    orig2 = u'2026-08 观测(3.35，推定发布 2026-09-13)'
    assert blob.count(orig1) >= 1 and blob.count(orig2) >= 1, (blob.count(orig1), blob.count(orig2))
    ids = [it['where'] + '|' + it['original'] for it in v['items']]
    assert not any(orig1 in x for x in ids), 'already present'
    item = {
        'severity': 'NIT',
        'where': u'agent_judgment.json reader_map.transmission[0].links[1].observed_fact(推定发布日)',
        'note': (u'两处美国 CPI 推定发布日按引擎规则(月末+13 天)推得,却落在周末: 2026-05 观测「推定发布 2026-06-13」为星期六,'
                 u'2026-08 观测「推定发布 2026-09-13」为星期日(冻结日历无该两月 CPI 实录条目);两处均已标「推定」。'
                 u'结论对发布日不敏感: 2026-08 观测的推定日期早于 2026-09-16/2026-09-18 两次决议且留有 3 天余量;'
                 u'2026-05 观测若实际早于 2026-06-11 发布,欧央行首次决议前最近可见即为高点 4.17,「仍处上行段」的表述不变。'),
        'original': orig1,
        'fix': u'2026-05 高点 4.17(推定发布 2026-06-13 前后;规则值为星期六)',
    }
    v['items'].append(item)
    n = v['notes']
    old = u'另 NIT 9 条(逐日共动面未入档、东京 8 月读数推定发布日为星期日、'
    new = u'另 NIT 10 条(逐日共动面未入档、推定发布日落在周末[东京 8 月读数 2026-08-30 为星期日;美国 CPI 两处推定发布日 2026-06-13 为星期六、2026-09-13 为星期日]、'
    assert n.count(old) == 1, n.count(old)
    n = n.replace(old, new)
    old2 = u'契约验证 14/14、six_checks 16/16、map_checks 7/7 均 VERIFIED,无非 VERIFIED 项。'
    new2 = u'契约验证 14/14(覆盖 C1 与 C3 陈述;C2 陈述的历史事后数字不在契约绑定范围,已由本席另行复算)、six_checks 16/16、map_checks 7/7 均 VERIFIED,无非 VERIFIED 项,unresolved_unbound 为空。'
    assert n.count(old2) == 1, n.count(old2)
    n = n.replace(old2, new2)
    v['notes'] = n
    sev = {}
    for it in v['items']:
        sev[it['severity']] = sev.get(it['severity'], 0) + 1
    assert sev == {'MINOR': 8, 'NIT': 10}, sev
    with open(sys.argv[1], 'w', encoding='utf-8') as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write(u'\n')
    print('items:', sev)
    print(n)


if __name__ == '__main__':
    main()
