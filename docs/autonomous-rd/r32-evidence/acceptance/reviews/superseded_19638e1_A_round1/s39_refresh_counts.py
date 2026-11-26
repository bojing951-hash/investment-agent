#!/usr/bin/python3 -I
"""Seat-internal: refresh the count sentence and count fields of VERDICT-round1.json (argv[2]) from
the final seat ledger (argv[1]) after the policy-surface rows were appended, and add the policy-surface
counter-attack.  A backup copy is written next to the verdict before anything is changed.

Usage:
  python3 -I s39_refresh_counts.py <points_all.jsonl> <VERDICT-round1.json>
"""
import json
import re
import shutil
import sys
from collections import Counter


def main():
    rows = [json.loads(x) for x in open(sys.argv[1], encoding='utf-8') if x.strip()]
    vpath = sys.argv[2]
    v = json.load(open(vpath, encoding='utf-8'))
    assert v['recompute_points'] == 970 and len(v['items']) == 20 and len(v['counterexamples_sought']) == 27
    counted = [r for r in rows if not (r['reported'] is None and r['computed'] is not None)]
    bad = [r for r in counted if not r['ok']]
    info = len(rows) - len(counted)
    by = Counter(r['section'] for r in counted)
    total, nbad = len(counted), len(bad)
    assert total == 1002 and nbad == 1 and info == 43, (total, nbad, info)
    assert by == {'anchors': 275, 'monthly': 187, 'daily': 133, 'history': 293, 'sync': 45, 'misc': 69}, by
    assert bad[0]['id'] == 'candidate[8] CORE_CPI delta'

    n = v['notes']
    pat = re.compile(
        u'计点 \\d+、偏离 \\d+\\(另 \\d+ 行仅作信息记录,不计入\\);覆盖锚点 \\d+、月频 \\d+\\(含引擎转折候选面 9 项的前值/后值/Δ/窗口与判断档所引候选值共 40 行\\)、'
        u'日频 \\d+、历史 \\d+、同步面 \\d+\\(引擎全维表 36 格\\+判断档通胀维标签 9 格\\)、其他 \\d+\\(含判断档 L3/L4 证据引用 20 个不同引用逐一回查证据索引与序列库\\)。')
    assert len(pat.findall(n)) == 1
    n = pat.sub(
        u'计点 %d、偏离 %d(另 %d 行仅作信息记录,不计入);覆盖锚点 %d、月频 %d(含引擎转折候选面 9 项的前值/后值/Δ/窗口与判断档所引候选值共 40 行)、'
        u'日频 %d、历史 %d、同步面 %d(引擎全维表 36 格+判断档通胀维标签 9 格)、其他 %d(含判断档 L3/L4 证据引用 20 个不同引用逐一回查证据索引与序列库、'
        u'政策面 32 行: 决议日/生效日/官方目标值/待生效/距上次调整与距研究截止天数)。' % (
            total, nbad, info, by['anchors'], by['monthly'], by['daily'], by['history'], by['sync'], by['misc']), n)
    old = u'政策日期与目标值、'
    assert n.count(old) == 1
    n = n.replace(old, u'政策日期与目标值(冻结日历实录条目与按惯例回推的决议日)、官方记录面天数(距上次调整/距决议/距维持 60/66/24 天)、')
    assert '\n' not in n
    v['notes'] = n
    v['counterexamples_sought'].append(
        u'反方攻击 28 (政策面): 决议日、生效日、官方目标值与距上次调整天数是否有实录或序列依据?→ 有: 日本央行三项来自冻结日历实录(决议 2026-09-18、生效 2026-09-24、目标 1.25;2026-10-30 确认维持);美联储与欧央行的生效日=序列值变更日(2025-12-11、2026-09-17;2026-06-17、2026-09-16),决议日为引擎按惯例自生效日回推(2025-12-10、2026-09-16;2026-06-11、2026-09-10),判断档已标【推断】并写明日历无实录;距上次调整(按生效日)60 天、距决议 66 天、距维持 24 天直算一致;无待生效决定。')
    v['recompute_points'] = total
    v['recompute_mismatches'] = nbad
    order = ['seat', 'reviewer', 'verdict', 'overall', 'notes', 'items', 'must_fix', 'counterexamples_sought',
             'recompute_points', 'recompute_mismatches', 'mismatch_details', 'audited_at']
    assert list(v.keys()) == order
    shutil.copyfile(vpath, vpath.replace('.json', '.before-policy.json'))
    with open(vpath, 'w', encoding='utf-8') as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('points=%d mismatches=%d info=%d sections=%s' % (total, nbad, info, dict(by)))
    print('items: %s; counterattacks: %d; notes len: %d' % (
        dict(Counter(it['severity'] for it in v['items'])), len(v['counterexamples_sought']), len(v['notes'])))
    i = n.find(u'复算: ')
    print(n[i:i + 420])


if __name__ == '__main__':
    main()
