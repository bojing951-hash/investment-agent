#!/usr/bin/python3 -I
"""Seat-internal, read-only: for each policy decision date quoted in section 2.4 (M1-2) of the prose,
list the latest INFLATION observation of the deciding economy that was published on or before the
decision date, using the seat visibility rules of section 0.3 (calendar entries first; here the frozen
calendar has no entry for these observation months, so the convention rules apply):
US CPI = month-end + 13 days, euro-area HICP = flash at month-end, Japan CPI = month-end + 20 days.
The only file written is the info file argv[3] (inside the seat directory).

Usage:
  python3 -I s42_decision_cpi.py <research_snapshot.json> <release_calendar.json> <out.txt>
"""
import calendar
import datetime as dt
import json
import sys

DECISIONS = [('ECB', '2026-06-11', 'EA_HICP_YOY'), ('ECB', '2026-09-10', 'EA_HICP_YOY'),
             ('Fed', '2026-09-16', 'CPI'), ('BoJ', '2026-09-18', 'JP_CPI_YOY')]
US_CPI_BEFORE = ['2026-06-11', '2026-09-10', '2026-09-16', '2026-09-18']


def month_end(y, m):
    return dt.date(y, m, calendar.monthrange(y, m)[1])


def pub_date(metric, obs):
    y, m = obs.year, obs.month
    if metric == 'CPI':
        return month_end(y, m) + dt.timedelta(days=13)
    if metric == 'EA_HICP_YOY':
        return month_end(y, m)
    if metric == 'JP_CPI_YOY':
        return month_end(y, m) + dt.timedelta(days=20)
    raise ValueError(metric)


def main():
    snap = json.load(open(sys.argv[1], encoding='utf-8'))
    cal = json.load(open(sys.argv[2], encoding='utf-8'))
    store = snap['series_store']
    out = []
    # the calendar must not carry an entry for these observation months (otherwise the entry wins)
    for e in cal['entries']:
        mids = e.get('metric_ids', [e.get('metric_id')])
        for mid in mids:
            if mid in ('CPI', 'EA_HICP_YOY', 'JP_CPI_YOY'):
                assert e['obs_to'] < '2026-01-01', ('calendar entry in 2026', e['entry_id'])
    out.append('frozen calendar: no entry for CPI / EA_HICP_YOY / JP_CPI_YOY observation months from 2026 on '
               '(18 entries scanned) -> convention rules of section 0.3 apply')

    def level(metric, obs_date):
        s = store[metric]
        i = s['dates'].index(obs_date.isoformat())
        return s['values'][i]

    def yoy(metric, obs):
        base = obs.replace(year=obs.year - 1)
        if base.isoformat() not in store[metric]['dates']:
            return None  # base-month observation absent (2025-10 federal shutdown)
        return (level(metric, obs) / level(metric, base) - 1.0) * 100.0

    def latest_visible(metric, asof):
        best = None
        for d in store[metric]['dates']:
            obs = dt.date.fromisoformat(d)
            if obs.day != 1:
                continue
            pd = pub_date(metric, obs)
            if pd <= asof:
                if best is None or obs > best[0]:
                    best = (obs, pd)
        assert best
        return best

    def fmt_val(metric, obs):
        return yoy(metric, obs) if metric == 'CPI' else level(metric, obs)

    asof_all = sorted(set(dt.date.fromisoformat(d) for _, d, _ in DECISIONS))
    for metric in ('CPI', 'EA_HICP_YOY', 'JP_CPI_YOY'):
        out.append('')
        out.append('== %s (observation month, publish date by rule, value%s)' % (
            metric, ' = year-on-year %' if metric == 'CPI' else ''))
        for d in store[metric]['dates']:
            obs = dt.date.fromisoformat(d)
            if obs.day != 1 or not (dt.date(2026, 1, 1) <= obs <= dt.date(2026, 10, 1)):
                continue
            out.append('  obs %s  pub(by rule) %s  value %s' % (
                obs, pub_date(metric, obs), 'n/a (base-month observation absent)' if fmt_val(metric, obs) is None
                else '%.4f' % fmt_val(metric, obs)))
    for bank, d, metric in DECISIONS:
        asof = dt.date.fromisoformat(d)
        obs, pd = latest_visible(metric, asof)
        nxt = dt.date(obs.year + (obs.month == 12), obs.month % 12 + 1, 1)
        out.append('')
        nv = fmt_val(metric, nxt)
        out.append('%s decision %s: latest visible %s = obs %s (published by rule %s <= decision), value %.4f; '
                   'next observation %s published by rule %s (> decision) value %s' % (
                       bank, d, metric, obs, pd, fmt_val(metric, obs), nxt, pub_date(metric, nxt),
                       'n/a (base-month observation absent)' if nv is None else '%.4f' % nv))
    out.append('')
    for d in US_CPI_BEFORE:
        asof = dt.date.fromisoformat(d)
        obs, pd = latest_visible('CPI', asof)
        out.append('US CPI latest visible before %s: obs %s (published by rule %s), yoy %.4f' % (d, obs, pd, yoy('CPI', obs)))
    obs = dt.date(2026, 9, 1)
    out.append('US CPI 2026-09 observation: published by rule %s, yoy %.4f (after all four decision dates)' % (
        pub_date('CPI', obs), yoy('CPI', obs)))
    assert pub_date('CPI', obs) > max(asof_all)
    text = '\n'.join(out)
    open(sys.argv[3], 'w', encoding='utf-8').write(text + '\n')
    print(text)


if __name__ == '__main__':
    main()
