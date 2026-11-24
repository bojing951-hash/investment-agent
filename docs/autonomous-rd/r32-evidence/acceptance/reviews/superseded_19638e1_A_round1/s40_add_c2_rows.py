#!/usr/bin/python3 -I
"""Seat-internal: the C2 statement summarises ex-post directions ("2025-03、2023-10 段风险资产与 GOLD_F
多数窗走强 ... 而 DXY 走弱").  The single-window values were already recomputed by s10; this script
recomputes them directly from the frozen snapshot once more, reconciles every value with the ledger,
and appends four aggregate rows (section history) to the seat ledger, then refreshes the count
sentence / count fields of VERDICT-round1.json and adds the matching counter-attack.
The only files written are the ledger (argv[1]) and the verdict (argv[3]); a backup copy of the
verdict is written next to it first.  The script refuses to run twice.

Usage:
  python3 -I s40_add_c2_rows.py <points_all.jsonl> <research_snapshot.json> <VERDICT-round1.json>
"""
import json
import re
import shutil
import sys
from collections import Counter

RISK = ['SPX', 'NIKKEI225', 'DAX', 'SHCOMP', 'GOLD_F']
PERIODS = {
    '2025-03': {'start': '2025-03-31', 'ends': {'3m': '2025-06-30', '6m': '2025-09-30', '12m': '2026-03-31'}},
    '2023-10': {'start': '2023-10-31', 'ends': {'3m': '2024-01-31', '6m': '2024-04-30', '12m': '2024-10-31'}},
}


def main():
    ledger_path = sys.argv[1]
    snap = json.load(open(sys.argv[2], encoding='utf-8'))
    vpath = sys.argv[3]
    v = json.load(open(vpath, encoding='utf-8'))
    rows = [json.loads(x) for x in open(ledger_path, encoding='utf-8') if x.strip()]
    assert not any(r['id'].startswith('C2 ') and 'windows' in r['id'] for r in rows), 'already appended'
    by_id = {r['id']: r for r in rows}
    store = snap['series_store']

    def val(metric, date):
        s = store[metric]
        i = s['dates'].index(date)
        a = s['values'][i]
        assert a is not None
        return a

    def pct(metric, d0, d1):
        return (val(metric, d1) / val(metric, d0) - 1.0) * 100.0

    new = []
    out = []
    for period, spec in PERIODS.items():
        neg, checked = [], 0
        for w, end in spec['ends'].items():
            for m in RISK + ['DXY']:
                c = pct(m, spec['start'], end)
                lid = '%s %s %s (%%)' % (period, w, m)
                assert lid in by_id, lid
                # ledger values are stored rounded to four decimals
                assert abs(by_id[lid]['computed'] - round(c, 4)) < 1e-9, (lid, by_id[lid]['computed'], c)
                checked += 1
                if m in RISK and c < 0:
                    neg.append('%s %s %.2f' % (m, w, c))
        out.append('%s: reconciled %d window values with the ledger; negative risk-asset/gold windows: %s' % (
            period, checked, neg or 'none'))
        pos = 15 - len(neg)
        if period == '2025-03':
            ok, comp, rep = (neg == []), '15/15', '多数窗走强'
            note = 'SPX/NIKKEI225/DAX/SHCOMP/GOLD_F × 3/6/12 月,月末口径,直算自 series_store'
        else:
            ok = (len(neg) == 1 and neg[0].startswith('SHCOMP 3m'))
            comp, rep = '14/15 (SHCOMP 3m -7.63)', '多数窗走强(2023-10段上证指数三个月窗为负,属例外)'
            note = '例外窗=2023-10段上证三个月窗,与陈述括注一致'
        new.append({'section': 'history', 'id': 'C2 %s risk assets & GOLD_F windows positive (5 metrics x 3/6/12m)' % period,
                    'src': 'series_store %s 月末→锚+N月月末,逐值与台账 history 行对账 | agent_judgment.json l3.contradictions[1].statement' % period,
                    'computed': comp, 'reported': rep, 'ok': ok, 'note': note})
        dx = [pct('DXY', spec['start'], end) for end in spec['ends'].values()]
        okd = all(x < 0 for x in dx)
        new.append({'section': 'history', 'id': 'C2 %s DXY negative in 3/6/12m windows' % period,
                    'src': 'series_store DXY %s 月末→锚+3/6/12月月末 | agent_judgment.json l3.contradictions[1].statement「DXY 走弱」' % period,
                    'computed': '%d/3' % sum(1 for x in dx if x < 0), 'reported': 'DXY 走弱', 'ok': okd,
                    'note': ' '.join('%+.2f' % x for x in dx)})

    rows.extend(new)
    counted = [r for r in rows if not (r['reported'] is None and r['computed'] is not None)]
    bad = [r for r in counted if not r['ok']]
    info = len(rows) - len(counted)
    by = Counter(r['section'] for r in counted)
    total, nbad = len(counted), len(bad)
    assert total == 1006 and nbad == 1 and info == 43 and by['history'] == 297, (total, nbad, info, dict(by))
    assert bad[0]['id'] == 'candidate[8] CORE_CPI delta'

    n = v['notes']
    pat = re.compile(u'计点 \\d+、偏离 \\d+\\(另 \\d+ 行仅作信息记录,不计入\\);覆盖锚点 \\d+、月频 \\d+'
                     u'\\(含引擎转折候选面 9 项的前值/后值/Δ/窗口与判断档所引候选值共 40 行\\)、日频 \\d+、历史 \\d+')
    hits = pat.findall(n)
    assert len(hits) == 1, hits
    n = pat.sub(u'计点 %d、偏离 %d(另 %d 行仅作信息记录,不计入);覆盖锚点 %d、月频 %d'
                u'(含引擎转折候选面 9 项的前值/后值/Δ/窗口与判断档所引候选值共 40 行)、日频 %d、历史 %d' % (
                    total, nbad, info, by['anchors'], by['monthly'], by['daily'], by['history']), n)
    old = u'历史事后 3/6/12 月 99 值与引擎事后块 48 值、'
    assert n.count(old) == 1
    n = n.replace(old, u'历史事后 3/6/12 月 99 值与引擎事后块 48 值、C2 陈述的事后方向归纳 4 行(风险资产与 GOLD_F 各窗为正的窗数 15/15 与 14/15、DXY 两段各 3/3 窗为负)、')
    assert '\n' not in n
    v['notes'] = n
    v['counterexamples_sought'].append(
        u'反方攻击 29 (C2): 『2025-03、2023-10 段风险资产与 GOLD_F 多数窗走强而 DXY 走弱』『2022-06 段三个月窗股指均为负、十二个月窗除上证外转正』的方向归纳是否与逐窗值一致?→ 一致: 2025-03 段 15 窗全正、2023-10 段 14/15(上证三个月窗 -7.63),DXY 两段各 3/3 窗为负;2022-06 段三个月窗 SPX -5.28、NIKKEI225 -1.73、DAX -5.24、SHCOMP -11.01,十二个月窗 SPX +17.57、NIKKEI225 +25.75、DAX +26.32、SHCOMP -5.78。')
    v['recompute_points'] = total
    v['recompute_mismatches'] = nbad
    order = ['seat', 'reviewer', 'verdict', 'overall', 'notes', 'items', 'must_fix', 'counterexamples_sought',
             'recompute_points', 'recompute_mismatches', 'mismatch_details', 'audited_at']
    assert list(v.keys()) == order

    with open(ledger_path, 'a', encoding='utf-8') as f:
        for r in new:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    shutil.copyfile(vpath, vpath.replace('.json', '.before-c2.json'))
    with open(vpath, 'w', encoding='utf-8') as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write('\n')

    for r in new:
        out.append('  %s %s | computed=%s | reported=%s' % ('OK ' if r['ok'] else 'BAD', r['id'], json.dumps(r['computed'], ensure_ascii=False), json.dumps(r['reported'], ensure_ascii=False)))
    out.append('appended %d rows; ledger now rows=%d counted=%d ok=%d mismatch=%d info=%d' % (
        len(new), len(rows), total, total - nbad, nbad, info))
    out.append('sections: %s' % dict(by))
    out.append('items: %s; counterattacks: %d; notes len: %d' % (
        dict(Counter(it['severity'] for it in v['items'])), len(v['counterexamples_sought']), len(v['notes'])))
    text = '\n'.join(out)
    open(ledger_path.replace('points_all.jsonl', 'info_c2_rows.txt'), 'w', encoding='utf-8').write(text + '\n')
    print(text)


if __name__ == '__main__':
    main()
