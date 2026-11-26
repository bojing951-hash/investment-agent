#!/usr/bin/python3 -I
"""Seat-internal: verify the engine turning-candidate face against series_store and append
counted rows to the seat ledger (the only file rewritten is the ledger passed as argv[1]).

For each engine candidate (report.json research_plan.turning_candidates.candidates[i]) the seat
recomputes, from the frozen snapshot only:
  * the year-on-year percent of level series (same month one year earlier as base) or the
    observation itself for *_YOY series;
  * the best (largest absolute) change between two published window months lying three
    monthly observations apart, inside the 13 months ending at the cutoff month;
and compares before / after / delta / window with the reader-report table row and the engine face.

Usage:
  python3 -I s32_add_candidates.py <points_all.jsonl> <report.json> <research_snapshot.json>
                                  <MAP_REPORT.md> <agent_judgment.json> <out.txt>
"""
import json
import sys

WINDOW_NOTE = u'候选面: 过去12个月内相隔三个月观测的最大变化(席位按冻结快照重算)'


def dec_of(rep):
    s = str(rep)
    if 'e' in s:
        return 6
    if '.' not in s:
        return 0
    return len(s.split('.')[1])


def main():
    ledger_path = sys.argv[1]
    rep = json.load(open(sys.argv[2], encoding='utf-8'))
    snap = json.load(open(sys.argv[3], encoding='utf-8'))
    md = open(sys.argv[4], encoding='utf-8').read().split('\n')
    jud_blob = json.dumps(json.load(open(sys.argv[5], encoding='utf-8')), ensure_ascii=False)
    rows = [json.loads(x) for x in open(ledger_path, encoding='utf-8') if x.strip()]
    out = []
    assert not any(r['id'].startswith('candidate[') for r in rows), 'already appended'
    store = snap['series_store']
    plan = rep['research_plan']
    cutoff = plan['cutoff']
    cands = plan['turning_candidates']['candidates']
    out.append('cutoff=%s candidates=%d basis=%s' % (cutoff, len(cands), plan['turning_candidates']['basis']))
    y0, m0 = int(cutoff[:4]), int(cutoff[5:7])
    window = []
    for k in range(13):
        m = m0 - k
        y = y0
        while m <= 0:
            m += 12
            y -= 1
        window.append('%04d-%02d' % (y, m))
    window = set(window)

    def monthly(metric):
        """{YYYY-MM: value} year-on-year percent for level series, observation for *_YOY."""
        d = store[metric]
        dates = d.get('dates') or []
        vals = d.get('values') or []
        idx = {dt: i for i, dt in enumerate(dates)}
        res = {}
        for dt, v in zip(dates, vals):
            if not dt.endswith('-01'):
                continue
            if metric.endswith('_YOY'):
                res[dt[:7]] = v
                continue
            y, m = int(dt[:4]), dt[5:7]
            j = idx.get('%04d-%s-01' % (y - 1, m))
            base = vals[j] if j is not None else None
            res[dt[:7]] = None if (v is None or base in (None, 0)) else (v / base - 1.0) * 100.0
        return res

    def best_change(series):
        mon = [(ym, series[ym]) for ym in sorted(series) if ym in window and series[ym] is not None]
        best = None
        for i in range(len(mon) - 3):
            a, b = mon[i], mon[i + 3]
            delta = b[1] - a[1]
            if best is None or abs(delta) > abs(best[3]):
                best = (a[0], b[0], (a[1], b[1]), delta)
        return mon, best

    # reader-report table rows
    tbl = {}
    in_tbl = False
    for i, l in enumerate(md):
        if l.startswith('| ') and u'前值→后值' in l and u'Δ' in l:
            in_tbl = True
            continue
        if in_tbl:
            if not l.startswith('|'):
                if tbl:
                    in_tbl = False
                continue
            cells = [c.strip() for c in l.strip().strip('|').split('|')]
            if set(''.join(cells)) <= set('- ') or len(cells) != 6:
                continue
            tbl[cells[2]] = (i + 1, cells)
    out.append('reader-report candidate table rows parsed: %d' % len(tbl))
    new = []

    def addn(pid, src, comp, repv, note=''):
        if comp is None or repv is None:
            new.append({'section': 'monthly', 'id': pid, 'src': src, 'computed': comp, 'reported': repv,
                        'ok': (comp is None and repv is None), 'note': note + ' | null handling'})
            return
        d = dec_of(repv)
        tol = 0.5 * (10 ** (-d)) + 1e-9
        ok = abs(float(comp) - float(repv)) <= tol
        new.append({'section': 'monthly', 'id': pid, 'src': src, 'computed': round(float(comp), max(d, 4)),
                    'reported': repv, 'ok': bool(ok), 'note': note})

    prev_abs = None
    sorted_ok = True
    for i, c in enumerate(cands):
        mid = c['metric_id']
        ln, cells = tbl[mid]
        before_s, after_s = cells[4].split(u'→')
        win_s = cells[3]
        delta_s = cells[5]
        s = monthly(mid)
        mon, best = best_change(s)
        src = 'series_store %s 同比%%(水平序列)或观测值' % mid
        face = 'MAP_REPORT.md L%d 引擎转折候选面 | report.json turning_candidates.candidates[%d]' % (ln, i)
        assert win_s == '%s..%s' % (c['from_ym'], c['to_ym']), (win_s, c)
        addn('candidate[%d] %s value_before (%s)' % (i, mid, c['from_ym']), src, s.get(c['from_ym']), before_s,
             '报告值=读者报告候选表前值;引擎面 value_before=%s' % c['value_before'])
        addn('candidate[%d] %s value_after (%s)' % (i, mid, c['to_ym']), src, s.get(c['to_ym']), after_s,
             '报告值=读者报告候选表后值;引擎面 value_after=%s' % c['value_after'])
        comp_delta = None if (s.get(c['from_ym']) is None or s.get(c['to_ym']) is None) else s[c['to_ym']] - s[c['from_ym']]
        addn('candidate[%d] %s delta' % (i, mid), src + ' 后值−前值', comp_delta, delta_s,
             '报告值=读者报告候选表 Δ;引擎面 delta=%s' % c['delta'])
        seat_win = None if best is None else '%s..%s' % (best[0], best[1])
        new.append({'section': 'monthly', 'id': 'candidate[%d] %s window = seat max |3-apart change|' % (i, mid),
                    'src': src + ' 窗=%s..%s 相隔三个观测' % (min(window), max(window)),
                    'computed': seat_win, 'reported': win_s, 'ok': seat_win == win_s,
                    'note': WINDOW_NOTE})
        out.append('candidate[%d] %s %s before=%s after=%s delta=%s | seat n_month=%d best=%s' % (
            i, mid, win_s, before_s, after_s, delta_s, len(mon), best))
        if prev_abs is not None and abs(float(delta_s)) > prev_abs + 1e-12:
            sorted_ok = False
        prev_abs = abs(float(delta_s))
    new.append({'section': 'monthly', 'id': 'candidate face sorted by |delta| descending (9 rows)',
                'src': 'MAP_REPORT.md 引擎转折候选面行序', 'computed': sorted_ok, 'reported': True,
                'ok': sorted_ok, 'note': ''})
    # judgment-quoted numbers
    q1, q2 = u'-2.3904', u'1.0101'
    assert (q1 + u'→' + q2) in jud_blob, 'judgment quote not found'
    pmi = monthly('CN_PMI_MFG')
    addn('turnings[1] CN_PMI_MFG z口径 2026-02 (judgment quote)', 'series_store CN_PMI_MFG 指数水平同比%', pmi['2026-02'], q1,
         '判断档 turnings[1].first_mover 「z口径 -2.3904→1.0101」')
    addn('turnings[1] CN_PMI_MFG z口径 2026-05 (judgment quote)', 'series_store CN_PMI_MFG 指数水平同比%', pmi['2026-05'], q2,
         '判断档 turnings[1].first_mover 「z口径 -2.3904→1.0101」')
    us_ea = [abs(float(tbl[c['metric_id']][1][5])) for c in cands if c['region'] in ('US', 'EA')]
    cpi_abs = abs(float(tbl['CPI'][1][5]))
    claim = (max(us_ea) == cpi_abs)
    new.append({'section': 'monthly', 'id': "turnings[0] 'CPI = 候选面最大美欧值' (|delta| max among US+EA candidates)",
                'src': 'MAP_REPORT.md 引擎转折候选面 US/EA 行', 'computed': claim, 'reported': True, 'ok': claim,
                'note': 'US/EA |Δ|=%s' % sorted(us_ea, reverse=True)})
    # informational: policy-dimension candidates under the same rule (not rendered in the face)
    out.append('-- seat same-rule scan of policy-dimension series (informational only, not in ledger):')
    for mid in ('JP_POLICY_RATE', 'DFEDTARU', 'DFF', 'ECB_DFR', 'ECB_MRO', 'CN_LPR_1Y', 'CN_OMO_7D', 'CN_POLICY_OVERNIGHT'):
        d = store.get(mid)
        if not d:
            out.append('  %s: not in store' % mid)
            continue
        # month-end last observation
        last = {}
        for dt, v in zip(d['dates'], d['values']):
            last[dt[:7]] = v
        s = {k: (None if v is None else float(v)) for k, v in last.items()}
        mon, best = best_change(s)
        out.append('  %s: n_month=%d best=%s' % (mid, len(mon), best))

    with open(ledger_path, 'a', encoding='utf-8') as f:
        for r in new:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    rows.extend(new)
    counted = [r for r in rows if not (r['reported'] is None and r['computed'] is not None)]
    bad = [r for r in counted if not r['ok']]
    out.append('appended %d rows; ledger now rows=%d counted=%d ok=%d mismatch=%d info=%d' % (
        len(new), len(rows), len(counted), sum(1 for r in counted if r['ok']), len(bad), len(rows) - len(counted)))
    for r in new:
        if not r['ok']:
            out.append('  MISMATCH %s' % json.dumps(r, ensure_ascii=False))
    from collections import Counter
    out.append('sections: %s' % dict(Counter(r['section'] for r in counted)))
    out.append('info by section: %s' % dict(Counter(r['section'] for r in rows if (r['reported'] is None and r['computed'] is not None))))
    text = '\n'.join(out)
    open(sys.argv[6], 'w', encoding='utf-8').write(text + '\n')
    print(text)


if __name__ == '__main__':
    main()
