#!/usr/bin/python3 -I
"""Seat-internal: add the NIT on the counter-scenario falsification threshold (value basis not
stated; found by s37_threshold_history.py) and its counter-attack to VERDICT-round1.json (argv[1).
A backup copy is written next to the verdict before anything is changed.

Usage:
  python3 -I s34c_add_nit11.py <VERDICT-round1.json> <points_all.jsonl>
"""
import json
import shutil
import sys
from collections import Counter


def replace_once(text, old, new):
    assert text.count(old) == 1, ('expected exactly one occurrence', old, text.count(old))
    return text.replace(old, new)


def main():
    vpath = sys.argv[1]
    v = json.load(open(vpath, encoding='utf-8'))
    assert v['recompute_points'] == 970 and len(v['items']) == 19, 'unexpected starting state'
    assert Counter(it['severity'] for it in v['items']) == {'MINOR': 9, 'NIT': 10}
    n = replace_once(
        v['notes'],
        u'取值正确但未在判断档说明])。',
        u'取值正确但未在判断档说明]、反例情景证伪阈值 1.8 未说明取值依据[距截止日读数 2.15 有 35 个基点,库内最近一次低于 1.8 为 2020-11-30])。')
    n = replace_once(n, u'另 NIT 10 条(', u'另 NIT 11 条(')
    assert '\n' not in n
    v['notes'] = n
    v['items'].append({
        'severity': 'NIT',
        'where': u'agent_judgment.json l4.scenarios[1].rows.falsification.threshold',
        'note': u'反例情景的证伪阈值 1.8 未说明取值依据: 截止日 BEI_10Y 读数 2.15@2026-11-20,距阈值 35 个基点;库内最近一次低于 1.8 为 2020-11-30(1.77),近 24 个观测无一触及。阈值可观测(指标在库、历史上到过该水平),不属『不可观测』,但在 2027-02-28 期限内偏难触发,属阈值松紧未披露。',
        'original': u'BEI_10Y 跌破1.8且继续下行——盈亏平衡通胀不回升反深跌,『一次性通胀+宽松预期修复』前提失效(深跌 BEI 指向衰退定价而非修复)',
        'fix': u'BEI_10Y 跌破1.8且继续下行(阈值依据: 库内最近一次低于 1.8 为 2020-11-30,较截止日读数 2.15 低 35 个基点,作深跌确认线)——盈亏平衡通胀不回升反深跌,『一次性通胀+宽松预期修复』前提失效(深跌 BEI 指向衰退定价而非修复)',
    })
    v['counterexamples_sought'].append(
        u'反方攻击 27 (情景): 证伪阈值是否可观测、是否已被截止日读数跨越?→ 可观测: CPI 同比<2.5 在近 24 个月中有 6 个月成立(最近 2026-02 的 2.434)、CORE_PCE<2.8 有 5 个月(最近 2025-11 的 2.721)、HY_OAS 4.61=序列高点(2025-04-07);BEI_10Y<1.8 库内最近一次为 2020-11-30(1.77),阈值偏宽、取值依据未说明(记 NIT);截止日读数均未跨越任何阈值。')
    order = ['seat', 'reviewer', 'verdict', 'overall', 'notes', 'items', 'must_fix', 'counterexamples_sought',
             'recompute_points', 'recompute_mismatches', 'mismatch_details', 'audited_at']
    assert list(v.keys()) == order
    shutil.copyfile(vpath, vpath.replace('.json', '.before-nit11.json'))
    with open(vpath, 'w', encoding='utf-8') as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('items: %s; counterattacks: %d; notes len: %d' % (
        dict(Counter(it['severity'] for it in v['items'])), len(v['counterexamples_sought']), len(v['notes'])))


if __name__ == '__main__':
    main()
