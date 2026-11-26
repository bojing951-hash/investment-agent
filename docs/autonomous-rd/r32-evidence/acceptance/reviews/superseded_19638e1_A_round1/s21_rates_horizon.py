#!/usr/bin/python3 -I
"""Read-only: rates trio and equity levels on common trading days at 12m / 3m / 1m horizons (information only).
Usage: python3 -I s21_rates_horizon.py <snapshot.json>
"""
import json
import sys


def main():
    snap = json.load(open(sys.argv[1], encoding='utf-8'))
    st = snap['series_store']

    def at(m, d):
        s = st[m]
        return s['values'][s['dates'].index(d)] if d in s['dates'] else None

    for a, b, lab in (('2025-11-19', '2026-11-19', '12m'), ('2026-08-19', '2026-11-19', '3m'),
                      ('2026-10-20', '2026-11-19', '1m')):
        parts = []
        for m in ('UST_10Y', 'TIPS_10Y', 'BEI_10Y'):
            x, y = at(m, a), at(m, b)
            parts.append('%s %s→%s (%+.0fbp)' % (m, x, y, (y - x) * 100.0))
        print('%s [%s→%s]: %s' % (lab, a, b, ' | '.join(parts)))
    for a, b, lab in (('2025-11-19', '2026-11-19', '12m'), ('2026-08-19', '2026-11-19', '3m'),
                      ('2026-10-20', '2026-11-19', '1m')):
        parts = []
        for m in ('SPX', 'NIKKEI225', 'DAX', 'CAC40', 'SHCOMP', 'GOLD_F', 'DXY'):
            x, y = at(m, a), at(m, b)
            parts.append('%s %+.2f%%' % (m, (y / x - 1.0) * 100.0))
        print('%s assets [%s→%s]: %s' % (lab, a, b, ' | '.join(parts)))


if __name__ == '__main__':
    main()
