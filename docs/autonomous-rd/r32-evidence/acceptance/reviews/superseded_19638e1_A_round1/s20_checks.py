#!/usr/bin/python3 -I
"""Read-only supplementary checks for items cited in the seat's findings (information only).

Usage:
  python3 -I s20_checks.py <snapshot.json> <report.json> <release_calendar.json> <agent_judgment.json>
"""
import json
import re
import sys


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


class St(object):
    def __init__(self, snap):
        self.store = snap['series_store']

    def series(self, m):
        s = self.store.get(m)
        if not s:
            return [], []
        return s['dates'], s['values']

    def at(self, m, d):
        """value at exact date d (None if absent)."""
        ds, vs = self.series(m)
        if d in ds:
            return vs[ds.index(d)]
        return None

    def le(self, m, d):
        """value at last observation with date <= d -> (date, value)."""
        ds, vs = self.series(m)
        out = (None, None)
        for dd, vv in zip(ds, vs):
            if dd <= d:
                out = (dd, vv)
            else:
                break
        return out

    def month_end(self, m, ym):
        """last observation within calendar month ym -> (date, value)."""
        return self.le(m, ym + '-31')

    def yoy(self, m, ym):
        """year-on-year change of a level series for observation month ym (obs dated YYYY-MM-01)."""
        y, mo = int(ym[:4]), int(ym[5:7])
        prev = '%04d-%02d' % (y - 1, mo)  # base = same month one year earlier
        a = self.at(m, ym + '-01')
        b = self.at(m, prev + '-01')
        if a is None or b in (None, 0):
            return None, None
        return (a / b - 1.0) * 100.0, b

    def path(self, m, ym_from, ym_to):
        y, mo = int(ym_from[:4]), int(ym_from[5:7])
        out = []
        while True:
            ym = '%04d-%02d' % (y, mo)
            if ym > ym_to:
                break
            out.append((ym, self.at(m, ym + '-01')))
            mo += 1
            if mo == 13:
                y, mo = y + 1, 1
        return out


def pct(a, b):
    if a in (None, 0) or b is None:
        return None
    return (b / a - 1.0) * 100.0


def main():
    snap = load(sys.argv[1])
    rep = load(sys.argv[2])
    cal = load(sys.argv[3])
    jud = load(sys.argv[4])
    st = St(snap)

    print('== A. BRENT_F month-end (last obs within month) ==')
    for ym in ('2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06', '2026-10'):
        print('BRENT_F month-end %s: %s' % (ym, st.month_end('BRENT_F', ym)))
    feb = st.month_end('BRENT_F', '2026-02')[1]
    may = st.month_end('BRENT_F', '2026-05')[1]
    mar = st.month_end('BRENT_F', '2026-03')[1]
    print('BRENT_F 2026-02 -> 2026-05 first/last: %.2f -> %.2f = %+.2f%%' % (feb, may, pct(feb, may)))
    print('BRENT_F 2026-02 -> 2026-03: %+.2f%% ; 2026-03 -> 2026-05: %+.2f%%' % (pct(feb, mar), pct(mar, may)))
    print('BRENT_F@2026-11-23: %s ; @2026-10-31: %s ; mtd: %s' % (
        st.at('BRENT_F', '2026-11-23'), st.le('BRENT_F', '2026-10-31'),
        pct(st.le('BRENT_F', '2026-10-31')[1], st.at('BRENT_F', '2026-11-23'))))

    print('== B. CORE_CPI / CPI yoy 2026-01..2026-05 (level yoy, base = same month last year) ==')
    for ym, v in st.path('CORE_CPI', '2026-01', '2026-06'):
        yy, base = st.yoy('CORE_CPI', ym)
        print('CORE_CPI %s level=%s base=%s yoy=%.4f' % (ym, v, base, yy))
    for ym in ('2025-09', '2025-11', '2026-01', '2026-02', '2026-04', '2026-05', '2026-07', '2026-08', '2026-09', '2026-10', '2025-10'):
        yy, base = st.yoy('CPI', ym)
        print('CPI %s level=%s base=%s yoy=%s' % (ym, st.at('CPI', ym + '-01'), base, yy))

    print('== C. CORE_PCE yoy 2026-01..2026-10 ==')
    for ym, v in st.path('CORE_PCE', '2026-01', '2026-10'):
        yy, base = st.yoy('CORE_PCE', ym)
        print('CORE_PCE %s level=%s base=%s yoy=%s' % (ym, v, base, None if yy is None else round(yy, 4)))

    print('== D. rates trio on common trading days (bp) ==')
    for m in ('UST_10Y', 'TIPS_10Y', 'BEI_10Y'):
        a = st.at(m, '2025-11-19')
        b = st.at(m, '2026-11-19')
        c = st.at(m, '2026-10-20')
        print('%s 2025-11-19=%s 2026-10-20=%s 2026-11-19=%s | 12m %+.0fbp | 1m(10-20->11-19) %+.0fbp' % (
            m, a, c, b, (b - a) * 100.0, (b - c) * 100.0))

    print('== E. CN_CPI_YOY path 2025-10..2026-06 ==')
    for ym, v in st.path('CN_CPI_YOY', '2025-10', '2026-06'):
        print('CN_CPI_YOY %s = %s' % (ym, v))

    print('== F. CN_PMI_MFG anchors and yoy in pp ==')
    for d in ('2025-10-31', '2026-07-31', '2026-10-31'):
        dd, v = st.le('CN_PMI_MFG', d)
        y = int(dd[:4]) - 1
        dd0, v0 = st.le('CN_PMI_MFG', '%04d%s' % (y, dd[4:]))
        print('CN_PMI_MFG obs %s = %s ; year-earlier obs %s = %s ; diff %+.2f pp ; ratio-yoy %+.2f%%' % (
            dd, v, dd0, v0, v - v0, pct(v0, v)))

    print('== G. INDPRO yoy 2025-10..2026-10 ==')
    for ym, v in st.path('INDPRO', '2025-10', '2026-10'):
        yy, base = st.yoy('INDPRO', ym)
        print('INDPRO %s level=%s yoy=%s' % (ym, v, None if yy is None else round(yy, 4)))

    print('== H. EA_HICP_YOY monthly increments 2026-01..2026-10 ==')
    prev = None
    for ym, v in st.path('EA_HICP_YOY', '2025-12', '2026-10'):
        print('EA_HICP_YOY %s = %s ; increment %s' % (ym, v, None if prev is None else '%+.2f' % (v - prev)))
        prev = v

    print('== I. USDCNY ==')
    for d in ('2025-11-19', '2026-08-19', '2026-10-20', '2026-10-23', '2026-11-19', '2026-11-23'):
        print('USDCNY %s -> %s' % (d, st.le('USDCNY', d)))

    print('== J. CN_POLICY_OVERNIGHT all observations ==')
    ds, vs = st.series('CN_POLICY_OVERNIGHT')
    print('CN_POLICY_OVERNIGHT n=%d first=%s last=%s distinct values=%s' % (
        len(ds), (ds[0], vs[0]) if ds else None, (ds[-1], vs[-1]) if ds else None, sorted(set(vs))))

    print('== K. evidence_refs counts ==')
    l3refs, l4refs = [], []
    for c in jud['l3'].get('contradictions', []):
        l3refs += c.get('evidence_refs', [])
    for m in jud['l3'].get('mechanism_chains', []):
        for lk in m.get('links', []):
            l3refs += lk.get('evidence_refs', [])
    for sc in jud['l4'].get('scenarios', []):
        for row in sc.get('rows', {}).values():
            if isinstance(row, dict):
                l4refs += row.get('evidence_refs', [])
    print('L3 refs=%d ; L4 refs=%d ; total=%d ; unique(L3+L4)=%d ; unique(L3)=%d' % (
        len(l3refs), len(l4refs), len(l3refs) + len(l4refs), len(set(l3refs + l4refs)), len(set(l3refs))))
    blob = json.dumps(jud, ensure_ascii=False)
    for m in re.finditer(r'[^，。；;“”"]{0,60}\b41\b[^，。；;“”"]{0,60}', blob):
        print('judgment text containing 41: …%s…' % m.group(0))
    for m in re.finditer(r'证据引用[^，。；]{0,80}', blob):
        print('judgment text: %s' % m.group(0))

    print('== L. frozen calendar: records by authority/issuer ==')
    entries = cal.get('entries') or cal.get('records') or cal.get('events') or []
    print('calendar top keys: %s ; n entries=%d' % (sorted(cal.keys()), len(entries)))
    issuers = {}
    for e in entries:
        for k in ('authority', 'issuer', 'source', 'region', 'agency'):
            if k in e:
                issuers[(k, str(e[k]))] = issuers.get((k, str(e[k])), 0) + 1
    print('issuer counts: %s' % sorted(issuers.items()))
    txt = json.dumps(entries, ensure_ascii=False)
    for kw in ('美联储', 'Federal Reserve', 'FOMC', '欧央行', 'ECB', '日本银行', '日本央行', 'BoJ', '中国人民银行', 'PBOC'):
        print('calendar entries mentioning %s: %d' % (kw, txt.count(kw)))

    print('== M. anchor GDP vintage wording in judgment ==')
    for kw in ('修订', '事后回顾', '当时可知', '首发'):
        print('count of "%s" in agent_judgment.json: %d' % (kw, blob.count(kw)))
    cells = rep['research_plan']['point_values']['cells']
    for c in cells:
        if c['metric_id'] in ('US_REAL_GDP', 'EA_REAL_GDP_YOY', 'JP_REAL_GDP_YOY'):
            print('engine cell %s vintage_semantics=%s' % (c['metric_id'], c.get('vintage_semantics')))

    print('== N. Tokyo CPI engine anchors (observation/publish dates) ==')
    for c in cells:
        if c['metric_id'] in ('JP_CPI_TOKYO_YOY',):
            print(json.dumps(c.get('anchors'), ensure_ascii=False))

    print('== O. 2026-11-23 weekday / snapshot stamps ==')
    import datetime
    for d in ('2026-11-23', '2026-11-20', '2026-08-30', '2026-08-31', '2026-09-29', '2026-06-26', '2026-10-30'):
        print('%s = %s' % (d, datetime.date(int(d[:4]), int(d[5:7]), int(d[8:10])).strftime('%a')))
    print('snapshot research_as_of = %s' % snap.get('research_as_of'))


if __name__ == '__main__':
    main()
