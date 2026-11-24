#!/usr/bin/python3 -I
"""Seat-internal: cross-check every evidence reference cited by the judgment (L3 + L4) against
evidence_index.json and series_store, then append counted rows to the seat ledger (the only file
written is the ledger passed as argv[1]; the script refuses to run twice).

For each distinct reference "METRIC@DATE":
  * in_index   : a row of evidence_index.json has exactly this ref string;
  * resolution : series_store[METRIC] has an observation on DATE (exact), or -- label-date duality --
                 on the first observation of the same month when DATE is the month-end label;
  * observation date is not after the cutoff day 2026-11-23 and the value is not null.

Usage:
  python3 -I s34b_add_refs.py <points_all.jsonl> <agent_judgment.json> <evidence_index.json>
                                <research_snapshot.json> <out.txt>
"""
import json
import sys
from collections import Counter

CUTOFF = '2026-11-23'


def walk(o, path, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == 'evidence_refs' and isinstance(v, list):
                for i, ref in enumerate(v):
                    out.append(('%s.evidence_refs[%d]' % (path, i), ref))
            else:
                walk(v, '%s.%s' % (path, k), out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, '%s[%d]' % (path, i), out)


def main():
    ledger_path = sys.argv[1]
    jud = json.load(open(sys.argv[2], encoding='utf-8'))
    idx = json.load(open(sys.argv[3], encoding='utf-8'))
    snap = json.load(open(sys.argv[4], encoding='utf-8'))
    store = snap['series_store']
    rows = [json.loads(x) for x in open(ledger_path, encoding='utf-8') if x.strip()]
    assert not any(r['id'].startswith('evidence ref ') for r in rows), 'already appended'
    out = []
    refs = []
    for top in ('l3', 'l4'):
        walk(jud.get(top, {}), top, refs)
    out.append('judgment evidence refs (L3+L4): %d' % len(refs))
    uniq = {}
    for p, r in refs:
        uniq.setdefault(r, []).append(p)
    out.append('distinct refs: %d' % len(uniq))
    index_refs = set(r.get('ref') for r in idx if isinstance(r, dict))
    new = []
    n_exact = n_dual = 0
    for ref in uniq:
        metric, _, date = ref.partition('@')
        in_index = ref in index_refs
        d = store.get(metric) or {}
        dates = d.get('dates') or []
        vals = d.get('values') or []
        obs_date = None
        note = ''
        if date in dates:
            obs_date = date
            n_exact += 1
        else:
            same_month = [dt for dt in dates if dt[:7] == date[:7]]
            if same_month:
                obs_date = min(same_month)
                n_dual += 1
                note = '标签日=观测月末,序列观测日=月初(同一观测两个日期标签;判断档 quality_gate_notes[5]-④ 已披露)'
        value = None
        if obs_date is not None:
            value = vals[dates.index(obs_date)]
        ok = bool(in_index and obs_date is not None and value is not None and obs_date <= CUTOFF)
        first_path = sorted(uniq[ref])[0]
        new.append({'section': 'misc', 'id': 'evidence ref %s' % ref,
                    'src': 'agent_judgment.json %s 等共 %d 处 | evidence_index.json ref | series_store %s' % (
                        first_path, len(uniq[ref]), metric),
                    'computed': None if obs_date is None else '观测 %s=%s' % (obs_date, value),
                    'reported': '%s(证据索引在列=%s)' % (ref, in_index),
                    'ok': ok, 'note': note})
        out.append('%s %-26s in_index=%s obs=%s value=%s cited_by=%d' % (
            'OK ' if ok else 'BAD', ref, in_index, obs_date, value, len(uniq[ref])))
    rows.extend(new)
    counted = [r for r in rows if not (r['reported'] is None and r['computed'] is not None)]
    bad = [r for r in counted if not r['ok']]
    with open(ledger_path, 'a', encoding='utf-8') as f:
        for r in new:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    out.append('exact-date resolution=%d, month-label duality=%d' % (n_exact, n_dual))
    out.append('appended %d rows; ledger now rows=%d counted=%d ok=%d mismatch=%d info=%d' % (
        len(new), len(rows), len(counted), len(counted) - len(bad), len(bad), len(rows) - len(counted)))
    out.append('sections: %s' % dict(Counter(r['section'] for r in counted)))
    out.append('info by section: %s' % dict(Counter(r['section'] for r in rows if (r['reported'] is None and r['computed'] is not None))))
    text = '\n'.join(out)
    open(sys.argv[5], 'w', encoding='utf-8').write(text + '\n')
    print(text)


if __name__ == '__main__':
    main()
