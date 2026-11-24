#!/usr/bin/python3 -I
"""Seat-internal: bring VERDICT-round1.json (argv[2]) in line with the final seat ledger (argv[1]):
counts by section, the single last-digit rounding deviation on the engine candidate face, the
evidence-reference cross-check, the added MINOR item and the two added counter-attacks.
A backup copy is written next to the verdict before anything is changed.

Usage:
  python3 -I s34_update_verdict_counts.py <points_all.jsonl> <VERDICT-round1.json>
"""
import json
import shutil
import sys
from collections import Counter


def replace_once(text, old, new):
    assert text.count(old) == 1, ('expected exactly one occurrence', old, text.count(old))
    return text.replace(old, new)


def main():
    rows = [json.loads(x) for x in open(sys.argv[1], encoding='utf-8') if x.strip()]
    vpath = sys.argv[2]
    v = json.load(open(vpath, encoding='utf-8'))
    assert v['recompute_points'] == 910 and len(v['items']) == 18, 'unexpected starting state'
    counted = [r for r in rows if not (r['reported'] is None and r['computed'] is not None)]
    bad = [r for r in counted if not r['ok']]
    info = len(rows) - len(counted)
    by = Counter(r['section'] for r in counted)
    total, nbad = len(counted), len(bad)
    assert total == 970 and nbad == 1 and info == 42, (total, nbad, info)
    assert by == {'anchors': 275, 'monthly': 187, 'daily': 133, 'history': 293, 'sync': 45, 'misc': 37}, by
    m = bad[0]
    assert m['id'] == 'candidate[8] CORE_CPI delta' and m['computed'] == -0.3768 and m['reported'] == '-0.3767', m

    n = v['notes']
    n = replace_once(
        n,
        u'计点 910、偏离 0(另 42 行仅作信息记录,不计入);覆盖锚点 275、月频 147、日频 133、历史 293、同步面 45(引擎全维表 36 格+判断档通胀维标签 9 格)、其他 17。',
        u'计点 %d、偏离 %d(另 %d 行仅作信息记录,不计入);覆盖锚点 %d、月频 %d(含引擎转折候选面 9 项的前值/后值/Δ/窗口与判断档所引候选值共 40 行)、日频 %d、历史 %d、同步面 %d(引擎全维表 36 格+判断档通胀维标签 9 格)、其他 %d(含判断档 L3/L4 证据引用 20 个不同引用逐一回查证据索引与序列库)。'
        u'唯一偏离在读者报告的引擎渲染面而非判断档文字: 候选面 CORE_CPI 行 Δ -0.3767 为两个四位小数端点之差(2.4462−2.8229),按未舍入值直算为 -0.3768,相差 0.0001(末位一个单位,小于端点自身的展示精度),方向与行序不变,记 MINOR。'
        % (total, nbad, info, by['anchors'], by['monthly'], by['daily'], by['history'], by['sync'], by['misc']))
    n = replace_once(
        n,
        u'判断档序列级数字全部命中——锚点回贴 63 值、',
        u'判断档序列级数字全部命中——锚点回贴 63 值、转折候选面前值/后值 9 项与判断档所引制造业PMI同比 -2.3904→1.0101、')
    n = replace_once(
        n,
        u'资产月窗、Gate A 清单。',
        u'资产月窗、Gate A 清单;证据引用 20 个不同引用全部在本轮证据索引内,均可解析到不晚于截止日的序列观测(其中 2 个按『标签日=观测月末、序列观测日=月初』双标签解析,该双标签已由判断档披露)。')
    n = replace_once(n, u'(5) 未达 MAJOR 的主要问题(MINOR 8 条): ', u'(5) 未达 MAJOR 的主要问题(MINOR 9 条): ')
    n = replace_once(
        n,
        u'季频 GDP 锚点为最新修订值未在判断档注明。另 NIT 10 条(',
        u'季频 GDP 锚点为最新修订值未在判断档注明;读者报告引擎转折候选面 CORE_CPI 行的 Δ -0.3767 由舍入后的端点相减而得,未舍入直算为 -0.3768(差值舍入口径未注明,判断档正文未引用该 Δ)。另 NIT 10 条(')
    n = replace_once(
        n,
        u'上述问题均不改变结论的数字与方向,亦无缺基期同比',
        u'上述问题均不改变结论的数字与方向(唯一数值偏离为末位舍入口径),亦无缺基期同比')
    assert '\n' not in n
    v['notes'] = n

    minor9 = {
        'severity': 'MINOR',
        'where': u'MAP_REPORT.md 引擎转折候选面(确定性排序表)CORE_CPI 行 Δ 列(引擎渲染面;判断档正文未引用该 Δ)',
        'note': u'Δ -0.3767 等于两个四位小数端点之差(2.4462−2.8229);按冻结快照未舍入值直算 CORE_CPI 同比 2026-05 为 2.8229420636、2026-08 为 2.4461631786,差 -0.3767788850,四位小数应为 -0.3768。面值与直算值相差 0.0000789,不足端点自身展示精度(0.0001)的一个单位,方向、量级与行序(末位)均不变;其余 8 项候选的 Δ 与未舍入直算逐位一致。属差值舍入口径未注明,不构成数值错误,故记 MINOR 而非 MAJOR。',
        'original': u'| US | inflation | CORE_CPI | 2026-05..2026-08 | 2.8229→2.4462 | -0.3767 |',
        'fix': u'| US | inflation | CORE_CPI | 2026-05..2026-08 | 2.8229→2.4462 | -0.3768 |(或保留 -0.3767 并注明「Δ 为端点四位小数相减值」)',
    }
    items = v['items']
    n_minor = sum(1 for it in items if it['severity'] == 'MINOR')
    assert n_minor == 8 and all(it['severity'] == 'NIT' for it in items[n_minor:])
    items.insert(n_minor, minor9)

    v['counterexamples_sought'] = v['counterexamples_sought'] + [
        u'反方攻击 25 (候选面): 引擎转折候选面的窗口、前值、后值与 Δ 是否与冻结快照一致?→ 窗口 9/9、前值 9/9、后值 9/9 与按引擎规则(相隔三个观测的最大变化)的席位重算一致;Δ 8/9 逐位一致;CORE_CPI 行 Δ 面值 -0.3767 为端点舍入后相减,未舍入直算 -0.3768(末位,记 MINOR);行序按 |Δ| 降序成立。',
        u'反方攻击 26 (引用): 判断档 L3/L4 的 50 处证据引用是否都在本轮证据索引与冻结快照内、且不晚于截止日?→ 是: 20 个不同引用全部在证据索引(72 行)内,18 个按日期精确命中序列库;CN_PPI_YOY@2026-10-31 与 CN_CPI_YOY@2026-10-31 两个引用按『标签日=观测月末、序列观测日=月初』双标签命中(值 5.7/0.7),该双标签已由判断档披露;全部观测日不晚于 2026-11-23。',
    ]
    v['recompute_points'] = total
    v['recompute_mismatches'] = nbad
    v['mismatch_details'] = [{
        'point': m['id'],
        'where': u'MAP_REPORT.md 引擎转折候选面 CORE_CPI 行 Δ 列(引擎渲染面;判断档正文未引用)',
        'computed': -0.3768,
        'reported': '-0.3767',
        'difference': 0.0000789,
        'severity': 'MINOR',
        'note': u'差值舍入顺序: 面值=舍入后端点相减 2.4462−2.8229;直算=未舍入后值 2.4461631786−未舍入前值 2.8229420636=−0.3767788850;四位小数应为 -0.3768',
    }]
    order = ['seat', 'reviewer', 'verdict', 'overall', 'notes', 'items', 'must_fix', 'counterexamples_sought',
             'recompute_points', 'recompute_mismatches', 'mismatch_details', 'audited_at']
    assert list(v.keys()) == order
    shutil.copyfile(vpath, vpath.replace('.json', '.before-minor9.json'))
    with open(vpath, 'w', encoding='utf-8') as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('updated: points=%d mismatches=%d info=%d sections=%s' % (total, nbad, info, dict(by)))
    print('items: %s' % dict(Counter(it['severity'] for it in v['items'])))
    print('counterattacks: %d; notes len: %d' % (len(v['counterexamples_sought']), len(v['notes'])))


if __name__ == '__main__':
    main()
