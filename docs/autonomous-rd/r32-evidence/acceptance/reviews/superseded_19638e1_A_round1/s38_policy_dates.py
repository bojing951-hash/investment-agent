#!/usr/bin/python3 -I
"""Seat-internal: recompute the policy surface -- decision / effective dates, official target value,
engine event clusters and "days since" figures -- from the frozen calendar, series_store and the
convention the engine states, then append counted rows to the seat ledger (the only file written is
the ledger passed as argv[1]; the script refuses to run twice).

Sources of the "reported" side: the judgment text (agent_judgment.json), the engine policy clusters
(report.json research_plan.policy_event_clusters) and the engine-rendered policy record table and
"距研究截止N天" cells of MAP_REPORT.md.

Usage:
  python3 -I s38_policy_dates.py <points_all.jsonl> <release_calendar.json> <research_snapshot.json>
                                  <report.json> <agent_judgment.json> <MAP_REPORT.md> <out.txt>
"""
import datetime as dt
import json
import re
import sys
from collections import Counter

CUTOFF = '2026-11-23'


def d(s):
    return dt.date(int(s[:4]), int(s[5:7]), int(s[8:10]))


def changes(store, metric, since):
    """[(date, from, to)] value changes of a step series on or after `since`."""
    s = store[metric]
    out = []
    prev = None
    for date, v in zip(s['dates'], s['values']):
        if v is None:
            continue
        if prev is not None and v != prev[1] and date >= since:
            out.append((date, prev[1], v))
        prev = (date, v)
    return out


def main():
    ledger_path = sys.argv[1]
    cal = json.load(open(sys.argv[2], encoding='utf-8'))
    snap = json.load(open(sys.argv[3], encoding='utf-8'))
    rep = json.load(open(sys.argv[4], encoding='utf-8'))
    jud_blob = json.dumps(json.load(open(sys.argv[5], encoding='utf-8')), ensure_ascii=False)
    md = open(sys.argv[6], encoding='utf-8').read().split('\n')
    rows = [json.loads(x) for x in open(ledger_path, encoding='utf-8') if x.strip()]
    assert not any(r['id'].startswith('policy ') for r in rows), 'already appended'
    store = snap['series_store']
    entries = cal['entries']
    out = []
    new = []

    def add(pid, src, comp, repv, note=''):
        new.append({'section': 'misc', 'id': pid, 'src': src, 'computed': comp, 'reported': repv,
                    'ok': comp == repv, 'note': note})

    # ---- A. frozen calendar (official record) ----
    ent = {e['entry_id']: e for e in entries}
    tgt = ent['RC-JP-BOJ-TARGET-2026-09']
    main_ = ent['RC-JP-BOJ-MAINT-2026-10']
    src_cal = 'release_calendar.json entries[RC-JP-BOJ-TARGET-2026-09]'
    assert '决议2026-09-18' in jud_blob and '生效2026-09-24' in jud_blob
    add('policy BoJ decision date', src_cal + '.decision_date | agent_judgment.json 「决议2026-09-18」',
        tgt['decision_date'], '2026-09-18', '冻结日历实录条目(非回推)')
    add('policy BoJ effective date', src_cal + '.effective_on | agent_judgment.json 「生效2026-09-24」',
        tgt['effective_on'], '2026-09-24', '')
    in_jud = ('目标水平 1.25' in jud_blob)
    add('policy BoJ official target value', src_cal + '.target_value | %s' % (
        'agent_judgment.json' if in_jud else 'MAP_REPORT.md 转折表「目标水平 1.25」'),
        tgt['target_value'], 1.25, '判断档含该表述=%s' % in_jud)
    # Japan record table row of the reader report
    tbl = [l for l in md if l.startswith(u'| 日本 |') and 'RC-JP-BOJ' in l]
    assert len(tbl) == 1, tbl
    cells = [c.strip() for c in tbl[0].strip().strip('|').split('|')]
    assert len(cells) == 11, cells
    out.append('Japan policy record row: %s' % cells)
    add('policy Japan latest maintenance decision date', 'release_calendar.json entries[RC-JP-BOJ-MAINT-2026-10].decision_date | MAP_REPORT.md 政策官方记录面「最近确认维持」',
        main_['decision_date'], cells[5], '')
    add('policy Japan verification coverage end', 'release_calendar.json latest JP_POLICY_TARGET entry with decision_date <= cutoff | MAP_REPORT.md 「核验覆盖截止」',
        main_['decision_date'], cells[6], '')
    eff = d(tgt['effective_on'])
    dec = d(tgt['decision_date'])
    cut = d(CUTOFF)
    add('policy Japan days since last change (by effective date)', '(2026-11-23 − %s) days | MAP_REPORT.md 「距上次调整(按生效日)」' % tgt['effective_on'],
        (cut - eff).days, int(cells[7].replace(u'天', '')), '判断档未给出天数')
    add('policy Japan days since decision', '(2026-11-23 − %s) days | MAP_REPORT.md 「距决议」' % tgt['decision_date'],
        (cut - dec).days, int(cells[8].replace(u'天', '')), '判断档未给出天数')
    add('policy Japan days since maintenance', '(2026-11-23 − %s) days | MAP_REPORT.md 「距维持」' % main_['decision_date'],
        (cut - d(main_['decision_date'])).days, int(cells[9].replace(u'天', '')), '判断档未给出天数')
    pending = [e['entry_id'] for e in entries if e.get('kind') == 'policy_decision' and e.get('effective_on') and e['effective_on'] > CUTOFF]
    add('policy pending decision effective after cutoff', 'release_calendar.json policy_decision entries with effective_on > 2026-11-23 | MAP_REPORT.md 「待生效」',
        (len(pending) == 0), (cells[2] == u'—'), 'True=无待生效决定(表内记「—」);无待生效决定则现行目标与官方目标同值')
    fed_ecb = [e['entry_id'] for e in entries if any(k in (e.get('metric_id') or '') for k in ('DFEDTARU', 'ECB_', 'DFF'))]
    has_claim = (u'冻结发布日历无美联储与欧央行实录条目' in jud_blob)
    add('policy calendar has no Fed/ECB record entries', 'release_calendar.json entries metric_id scan | agent_judgment.json quality_gate_notes[2]',
        (not fed_ecb), has_claim, '命中条目=%s' % fed_ecb)

    # ---- B. decision dates by the stated convention, effective dates = series change dates ----
    ch_dfr = changes(store, 'ECB_DFR', '2026-06-01')
    ch_mro = changes(store, 'ECB_MRO', '2026-06-01')
    ch_tar = changes(store, 'DFEDTARU', '2025-11-23')
    out.append('ECB_DFR changes: %s | ECB_MRO changes: %s | DFEDTARU changes: %s' % (ch_dfr, ch_mro, ch_tar))
    assert [(c[0], c[1], c[2]) for c in ch_dfr] == [('2026-06-17', 2.0, 2.25), ('2026-09-16', 2.25, 2.5)]
    assert [(c[0], c[1], c[2]) for c in ch_mro] == [('2026-06-17', 2.15, 2.4), ('2026-09-16', 2.4, 2.65)]
    assert [(c[0], c[1], c[2]) for c in ch_tar] == [('2025-12-11', 4.0, 3.75), ('2026-09-17', 3.75, 4.0)]
    clusters = rep['research_plan']['policy_event_clusters']['clusters']
    conv = rep['research_plan']['policy_event_clusters']['basis']
    assert u'Fed=次日' in conv and u'ECB=决议后首个周三' in conv
    seen = set()
    for cl in clusters:
        for ev in cl['events']:
            eff_date = d(ev['effective_date'])
            if ev['region'] == 'EA':
                # "effective on the first Wednesday after the decision" -> latest Thursday strictly before it
                assert eff_date.weekday() == 2, eff_date
                dec_date = eff_date - dt.timedelta(days=1)
                while dec_date.weekday() != 3:      # Thursday
                    dec_date -= dt.timedelta(days=1)
            else:
                dec_date = eff_date - dt.timedelta(days=1)
            key = (ev['metric_id'], ev['effective_date'])
            if key in seen:
                continue
            seen.add(key)
            ser = {'ECB_DFR': ch_dfr, 'ECB_MRO': ch_mro, 'DFEDTARU': ch_tar}[ev['metric_id']]
            hit = [c for c in ser if c[0] == ev['effective_date']]
            assert len(hit) == 1, (key, hit)
            tag = '%s %s %s' % (cl['cluster_id'], ev['region'], ev['metric_id'])
            in_j = ev['date'] in jud_blob
            add('policy decision date %s (convention back-calculation)' % tag,
                'series_store %s value-change date %s + engine convention (%s -> %s) | report.json policy_event_clusters | judgment contains date=%s' % (
                    ev['metric_id'], ev['effective_date'], ev['date'], ev['effective_date'], in_j),
                dec_date.isoformat(), ev['date'], u'判断档标【推断】' if in_j else '仅引擎面与读者报告载该决议日')
            add('policy effective date %s (= series change date)' % tag,
                'series_store %s value-change date | report.json policy_event_clusters.events.effective_date' % ev['metric_id'],
                hit[0][0], ev['effective_date'], '判断档含该生效日=%s' % (ev['effective_date'] in jud_blob))
            add('policy value before %s' % tag, 'series_store %s value before change' % ev['metric_id'], hit[0][1], ev['from'], '')
            add('policy value after %s' % tag, 'series_store %s value after change' % ev['metric_id'], hit[0][2], ev['to'], '')
    assert len(seen) == 4, seen

    # ---- C. engine "距研究截止N天" cells ----
    lag = {}
    for i, l in enumerate(md):
        for m in re.finditer(r'(\d{4}-\d{2}-\d{2})\(距研究截止(\d+)天\)', l):
            lag.setdefault((m.group(1), int(m.group(2))), []).append(i + 1)
    out.append('距研究截止 cells: %s' % sorted(lag.items()))
    for (date, n), lines in sorted(lag.items()):
        comp = (cut - d(date)).days
        add('policy lag to research cutoff: %s' % date, '(2026-11-23 − %s) days | MAP_REPORT.md L%s 「距研究截止」' % (date, ','.join(str(x) for x in lines)),
            comp, n, '')
    # informational: the judgment itself states no day counts
    new.append({'section': 'misc', 'id': 'policy days since last change at cutoff (US by effective date / EA by effective date / JP by effective date)',
                'src': 'seat arithmetic from series change dates and calendar effective_on', 'computed': 'US %d / EA %d / JP %d' % (
                    (cut - d('2026-09-17')).days, (cut - d('2026-09-16')).days, (cut - eff).days),
                'reported': None, 'ok': True, 'note': '判断档未给出天数,仅作信息记录'})

    rows.extend(new)
    counted = [r for r in rows if not (r['reported'] is None and r['computed'] is not None)]
    bad = [r for r in counted if not r['ok']]
    with open(ledger_path, 'a', encoding='utf-8') as f:
        for r in new:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    out.append('appended %d rows; ledger now rows=%d counted=%d ok=%d mismatch=%d info=%d' % (
        len(new), len(rows), len(counted), len(counted) - len(bad), len(bad), len(rows) - len(counted)))
    for r in new:
        out.append('  %s %s | computed=%s | reported=%s' % ('OK ' if r['ok'] else 'BAD', r['id'], json.dumps(r['computed'], ensure_ascii=False), json.dumps(r['reported'], ensure_ascii=False)))
    out.append('sections: %s' % dict(Counter(r['section'] for r in counted)))
    out.append('info by section: %s' % dict(Counter(r['section'] for r in rows if (r['reported'] is None and r['computed'] is not None))))
    text = '\n'.join(out)
    open(sys.argv[7], 'w', encoding='utf-8').write(text + '\n')
    print(text)


if __name__ == '__main__':
    main()
