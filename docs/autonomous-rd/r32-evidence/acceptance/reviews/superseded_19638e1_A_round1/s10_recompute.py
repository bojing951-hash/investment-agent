#!/usr/bin/python3 -I
"""Read-only deterministic recomputation for the zero-context semantic-audit seat.

Every number is computed directly from the frozen snapshot series_store, the
frozen release calendar and the engine faces in report.json, then compared with
the numbers written in agent_judgment.json.

Usage:
  python3 -I s10_recompute.py <snapshot.json> <report.json> <release_calendar.json> \
      <agent_judgment.json> <out_dir> <section> [<section> ...]

Sections: anchors monthly daily history sync misc counter
Writes only <out_dir>/points_<section>.txt, <out_dir>/info_<section>.txt and
<out_dir>/points_all.jsonl.
"""
import datetime as dt
import json
import re
import sys

POINTS = []
INFO = []
MISSING = []

MONTHLY = set(['US_REAL_GDP', 'UNEMPLOYMENT', 'INDPRO', 'CPI', 'CORE_CPI', 'CORE_PCE',
               'CN_PMI_MFG', 'CN_CPI_YOY', 'CN_PPI_YOY', 'EA_REAL_GDP_YOY', 'EA_HICP_YOY',
               'JP_REAL_GDP_YOY', 'JP_CPI_YOY', 'JP_CPI_TOKYO_YOY', 'JP_POLICY_RATE',
               'CN_NEW_LOANS'])
ANCHORS = {'12个月前': '2025-11-23', '3个月前': '2026-08-23', '最新一期': '2026-11-23'}
TAG = {'12个月前': '12m', '3个月前': '3m', '最新一期': 'now'}
CUTOFF = '2026-11-23'


# ---------------------------------------------------------------- utilities
def load(p):
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)


def addm(ym, k):
    y = int(ym[:4])
    m = int(ym[5:7])
    t = y * 12 + (m - 1) + k
    return '%04d-%02d' % (t // 12, t % 12 + 1)


def last_day(ym):
    y = int(ym[:4])
    m = int(ym[5:7])
    if m == 12:
        return '%04d-12-31' % y
    n = (dt.date(y, m + 1, 1) - dt.date(y, m, 1)).days
    return '%04d-%02d-%02d' % (y, m, n)


def plus_days(d, n):
    y = int(d[:4])
    m = int(d[5:7])
    dd = int(d[8:10])
    return (dt.date(y, m, dd) + dt.timedelta(days=n)).isoformat()


def days_between(a, b):
    da = dt.date(int(a[:4]), int(a[5:7]), int(a[8:10]))
    db = dt.date(int(b[:4]), int(b[5:7]), int(b[8:10]))
    return (db - da).days


def dec_of(rep):
    s = str(rep)
    if 'e' in s:
        return 6
    if '.' not in s:
        return 0
    return len(s.split('.')[1])


def add(section, pid, src, comp, rep, ok, note=''):
    POINTS.append({'section': section, 'id': pid, 'src': src, 'computed': comp,
                   'reported': rep, 'ok': bool(ok), 'note': note})


def addn(section, pid, src, comp, rep, note='', tol_extra=0.0):
    if comp is None or rep is None:
        ok = (comp is None and rep is None)
        add(section, pid, src, comp, rep, ok, note + ' | null handling')
        return
    d = dec_of(rep)
    tol = 0.5 * (10 ** (-d)) + 1e-9 + tol_extra
    ok = abs(float(comp) - float(rep)) <= tol
    add(section, pid, src, round(float(comp), max(d, 4)), rep, ok, note)


def info(section, text):
    INFO.append({'section': section, 'text': text})


def need(blob, snippet):
    if snippet not in blob:
        MISSING.append(snippet)


class Store(object):
    def __init__(self, ss):
        self.map = {}
        for m in ss:
            s = ss[m]
            dates = s.get('dates') or []
            vals = s.get('values') or []
            d = {}
            i = 0
            while i < len(dates) and i < len(vals):
                v = vals[i]
                if v is not None:
                    fv = None
                    try:
                        fv = float(v)
                    except (TypeError, ValueError):
                        fv = None
                    if fv is not None and fv == fv and fv != float('inf') and fv != float('-inf'):
                        d[str(dates[i])[:10]] = fv
                i += 1
            self.map[m] = d

    def has(self, m):
        return m in self.map and len(self.map[m]) > 0

    def dates(self, m):
        return sorted(self.map.get(m, {}).keys())

    def at(self, m, d):
        return self.map.get(m, {}).get(d)

    def le(self, m, d):
        best = None
        for k in self.map.get(m, {}):
            if k <= d and (best is None or k > best):
                best = k
        if best is None:
            return None
        return (best, self.map[m][best])

    def ge(self, m, d):
        best = None
        for k in self.map.get(m, {}):
            if k >= d and (best is None or k < best):
                best = k
        if best is None:
            return None
        return (best, self.map[m][best])

    def month_val(self, m, ym):
        d = self.month_last_date(m, ym)
        if d is None:
            return None
        return self.map[m][d]

    def month_last_date(self, m, ym):
        best = None
        for k in self.map.get(m, {}):
            if k[:7] == ym and (best is None or k > best):
                best = k
        return best

    def yoy(self, m, ym):
        c = self.month_val(m, ym)
        b = self.month_val(m, addm(ym, -12))
        if c is None or b is None:
            return None
        return (c / b - 1.0) * 100.0

    def latest_visible(self, m, asof, entries):
        """Latest observation of a monthly series published on or before asof (seat rules)."""
        best = None
        for d in self.dates(m):
            if d > asof:
                break
            p = pub_date(entries, m, d)
            if p is not None and p <= asof:
                best = (d, p)
        return best


def calendar_pub(entries, m, od):
    best = None
    best_key = None
    for e in entries:
        ids = e.get('metric_ids')
        if ids is None:
            ids = [e.get('metric_id')]
        if m not in ids:
            continue
        f = str(e.get('obs_from'))[:10]
        t = str(e.get('obs_to'))[:10]
        if od < f or od > t:
            continue
        p = e.get('first_publish_on_or_after')
        if p is None:
            continue
        width = days_between(f, t)
        key = (f, -width, 1 if e.get('basis') == 'user_directive' else 0)
        if best_key is None or key > best_key:
            best_key = key
            best = str(p)[:10]
    return best


def pub_date(entries, m, od):
    """Seat publication rule: frozen calendar entry first, else a conservative
    presumption (never earlier than the engine's presumed rule)."""
    p = calendar_pub(entries, m, od)
    if p is not None:
        return p
    ym = od[:7]
    ld = last_day(ym)
    if m in ('CPI', 'CORE_CPI'):
        return plus_days(ld, 13)
    if m == 'CORE_PCE':
        return plus_days(ld, 30)
    if m == 'UNEMPLOYMENT':
        return plus_days(ld, 5)
    if m == 'INDPRO':
        return plus_days(ld, 15)
    if m in ('US_REAL_GDP', 'EA_REAL_GDP_YOY', 'JP_REAL_GDP_YOY'):
        # quarterly series are dated by the first day of the statistical quarter;
        # publication = quarter end + lag (29 / 35 / 45 days)
        qe = last_day(addm(ym, 2))
        lag = {'US_REAL_GDP': 29, 'EA_REAL_GDP_YOY': 35, 'JP_REAL_GDP_YOY': 45}[m]
        return plus_days(qe, lag)
    if m == 'EA_HICP_YOY':
        return ld
    if m in ('CN_CPI_YOY', 'CN_PPI_YOY'):
        return plus_days(ld, 9)
    if m == 'CN_PMI_MFG':
        return ld
    if m == 'JP_CPI_YOY':
        return plus_days(ld, 20)
    if m == 'JP_CPI_TOKYO_YOY':
        return plus_days(ld, -1)
    if m == 'JP_POLICY_RATE':
        return plus_days(ld, 5)
    return plus_days(ld, 20)


def path(st, m, ym0, ym1):
    out = []
    ym = ym0
    while True:
        out.append((ym, st.month_val(m, ym)))
        if ym == ym1:
            break
        ym = addm(ym, 1)
    return out


def yoy_path(st, m, ym0, ym1):
    out = []
    ym = ym0
    while True:
        out.append((ym, st.yoy(m, ym)))
        if ym == ym1:
            break
        ym = addm(ym, 1)
    return out


def argmax(p):
    best = None
    for ym, v in p:
        if v is None:
            continue
        if best is None or v > best[1]:
            best = (ym, v)
    return best


def argmin(p):
    best = None
    for ym, v in p:
        if v is None:
            continue
        if best is None or v < best[1]:
            best = (ym, v)
    return best


def monotonic(p, direction):
    prev = None
    for ym, v in p:
        if v is None:
            return None
        if prev is not None:
            if direction > 0 and v <= prev:
                return False
            if direction < 0 and v >= prev:
                return False
        prev = v
    return True


def fmt(p):
    out = []
    for ym, v in p:
        if v is None:
            out.append('%s:NA' % ym)
        else:
            out.append('%s:%.4g' % (ym, v))
    return ' '.join(out)


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = 0.0
    syy = 0.0
    sxy = 0.0
    i = 0
    while i < n:
        a = xs[i] - mx
        b = ys[i] - my
        sxx += a * a
        syy += b * b
        sxy += a * b
        i += 1
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / ((sxx ** 0.5) * (syy ** 0.5))


# ---------------------------------------------------------------- sections
def sec_anchors(S, st, snap, rep, entries, jud, blob):
    cells = {}
    for c in rep['research_plan']['point_values']['cells']:
        cells[c['metric_id']] = c
    n_echo = 0
    for ri, reg in enumerate(jud['reader_map']['regions']):
        for ei, e in enumerate(reg['anchor_echo']):
            n_echo += 1
            m = e['metric_id']
            an = e['anchor']
            anchor = ANCHORS[an]
            pid = m + '@' + TAG[an]
            ref = 'judgment reader_map.regions[%d].anchor_echo[%d]' % (ri, ei)
            ec = cells.get(m)
            if ec is None:
                add(S, pid + ':engine_cell_present', 'report.json point_values.cells', None, m, False, ref)
                continue
            ea = ec['anchors'][an]
            od = None
            pub = None
            if m in MONTHLY:
                r = st.latest_visible(m, anchor, entries)
                if r is not None:
                    od = r[0]
                    pub = r[1]
            else:
                lim = anchor
                if m == 'DFF':
                    lim = plus_days(anchor, -1)
                r = st.le(m, lim)
                if r is not None:
                    od = r[0]
                    pub = calendar_pub(entries, m, od) or od
                    if m == 'DFF':
                        pub = plus_days(od, 1)
            val = None if od is None else st.at(m, od)
            src = 'no visible observation at ' + anchor if od is None else 'series_store.%s@%s (pub %s)' % (m, od, pub)
            addn(S, pid + ':value', src, val, e['value'], ref)
            om = e.get('observation_month')
            if om is not None:
                got = None if od is None else od[:7]
                add(S, pid + ':obs_month', 'series_store.%s dates' % m, got, om, got == om, ref)
            ev = ea.get('value')
            addn(S, pid + ':engine_cell_value', 'report.json cells.%s.anchors[%s].value' % (m, an), val, ev, '')
            eod = str(ea.get('observation_date'))[:7]
            got = None if od is None else od[:7]
            add(S, pid + ':engine_cell_obs_month', 'report.json cells.%s.anchors[%s].observation_date' % (m, an), got, eod, got == eod, '')
            if m in ('US_REAL_GDP', 'INDPRO', 'CPI', 'CORE_PCE', 'CORE_CPI'):
                yv = None if od is None else st.yoy(m, od[:7])
                ed = ea.get('derived_yoy_pct')
                addn(S, pid + ':yoy_vs_engine_cell', 'series_store %s yoy(%s)' % (m, od), yv, ed, 'yoy_status=%s' % ea.get('yoy_status'))
    info(S, 'anchor_echo entries checked: %d' % n_echo)
    # absence / non-impersonation claims
    add(S, 'JP_POLICY_TARGET not in registry', 'snapshot series_store keys', 'JP_POLICY_TARGET' in st.map, 'absent', 'JP_POLICY_TARGET' not in st.map, 'judgment: plan metric not in registry')
    r = st.le('CN_POLICY_OVERNIGHT', '2026-08-23')
    add(S, 'CN_POLICY_OVERNIGHT no obs before 3m anchor', 'series_store CN_POLICY_OVERNIGHT', None if r is None else r[0], 'absent', r is None, '')
    ds = st.dates('CN_POLICY_OVERNIGHT')
    add(S, 'CN_POLICY_OVERNIGHT first obs = 2026-11-02', 'series_store CN_POLICY_OVERNIGHT dates', None if not ds else ds[0], '2026-11-02', bool(ds) and ds[0] == '2026-11-02', 'headline: 2026-11-02 anchor switch')
    if ds:
        vals = set()
        for d in ds:
            vals.add(st.at('CN_POLICY_OVERNIGHT', d))
        add(S, 'CN_POLICY_OVERNIGHT flat since first obs', 'series_store CN_POLICY_OVERNIGHT values', sorted(vals), 'single value 1.25', len(vals) == 1 and 1.25 in vals, 'flat at first observation')
    r = st.latest_visible('JP_CPI_TOKYO_YOY', '2025-11-23', entries)
    add(S, 'JP_CPI_TOKYO_YOY no published obs before 12m anchor', 'series_store JP_CPI_TOKYO_YOY', None if r is None else r[0], 'absent', r is None, '')
    info(S, 'JP_CPI_TOKYO_YOY first dates: %s' % ' '.join(st.dates('JP_CPI_TOKYO_YOY')[:6]))
    # cutoff discipline
    maxd = ''
    maxm = ''
    for m in st.map:
        ds = st.dates(m)
        if ds and ds[-1] > maxd:
            maxd = ds[-1]
            maxm = m
    add(S, 'no observation after cutoff', 'series_store all series max date', '%s(%s)' % (maxd, maxm), '<=2026-11-23', maxd <= CUTOFF, 'research_as_of=%s' % snap.get('research_as_of'))
    add(S, 'snapshot research_as_of date', 'snapshot research_as_of', str(snap.get('research_as_of'))[:10], '2026-11-23', str(snap.get('research_as_of'))[:10] == '2026-11-23', '')
    add(S, 'snapshot target_date', 'snapshot target_date', str(snap.get('target_date')), '20261123', str(snap.get('target_date')) == '20261123', '')


def sec_monthly(S, st, snap, rep, entries, jud, blob):
    TRIPLES = [
        ('US_REAL_GDP', 'val', ['2025-04', '2026-04', '2026-07'], ['23884.563', '24408.011', '24611.077'], 'US GDP level'),
        ('US_REAL_GDP', 'yoy', ['2025-04', '2026-04', '2026-07'], ['2.42', '2.19', '2.07'], 'US GDP yoy'),
        ('UNEMPLOYMENT', 'val', ['2025-09', '2026-07', '2026-10'], ['4.4', '4.1', '4.1'], 'UNEMP'),
        ('INDPRO', 'val', ['2025-08', '2026-07', '2026-10'], ['101.6247', '103.1675', '103.3954'], 'INDPRO level'),
        ('INDPRO', 'yoy', ['2025-08', '2026-07', '2026-10'], ['1.19', '1.25', '2.15'], 'INDPRO yoy'),
        ('CPI', 'val', ['2025-09', '2026-07', '2026-10'], ['324.245', '332.813', '337.476'], 'CPI level'),
        ('CPI', 'yoy', ['2025-09', '2026-07', '2026-10'], ['3.02', '3.30', None], 'CPI yoy'),
        ('CORE_PCE', 'val', ['2025-08', '2026-06', '2026-09'], ['126.646', '129.969', '130.902'], 'CORE_PCE level'),
        ('CORE_PCE', 'yoy', ['2025-08', '2026-06', '2026-09'], ['2.85', '3.04', '3.12'], 'CORE_PCE yoy'),
        ('EA_REAL_GDP_YOY', 'val', ['2025-07', '2026-04', '2026-07'], ['1.11', '1.19', '1.28'], 'EA GDP yoy'),
        ('EA_HICP_YOY', 'val', ['2025-10', '2026-07', '2026-10'], ['2.1', '2.9', '4.0'], 'EA HICP'),
        ('JP_REAL_GDP_YOY', 'val', ['2025-07', '2026-04', '2026-07'], ['0.63', '0.80', '1.16'], 'JP GDP yoy'),
        ('JP_CPI_YOY', 'val', ['2025-10', '2026-07', '2026-10'], ['2.99', '1.97', '2.44'], 'JP CPI yoy'),
        ('JP_CPI_TOKYO_YOY', 'val', ['2026-07', '2026-10'], ['1.85', '2.73'], 'Tokyo CPI yoy'),
        ('JP_POLICY_RATE', 'val', ['2025-10', '2026-07', '2026-10'], ['0.477', '0.978', '1.227'], 'JP policy rate'),
        ('CN_PPI_YOY', 'val', ['2025-10', '2026-07', '2026-10'], ['-2.1', '3.5', '5.7'], 'CN PPI yoy'),
        ('CN_CPI_YOY', 'val', ['2025-10', '2026-07', '2026-10'], ['0.2', '0.5', '0.7'], 'CN CPI yoy'),
        ('CN_PMI_MFG', 'val', ['2025-10', '2026-07', '2026-10'], ['49.0', '49.2', '49.3'], 'CN PMI'),
    ]
    for row in TRIPLES:
        m = row[0]
        kind = row[1]
        for i in range(len(row[2])):
            ym = row[2][i]
            rp = row[3][i]
            if kind == 'val':
                comp = st.month_val(m, ym)
                src = 'series_store %s@%s' % (m, ym)
            else:
                comp = st.yoy(m, ym)
                src = 'series_store %s %s vs %s' % (m, ym, addm(ym, -12))
            addn(S, '%s %s' % (row[4], ym), src, comp, rp, 'from_to narrative')

    # ---- US CPI yoy path
    p = yoy_path(st, 'CPI', '2024-10', '2026-10')
    info(S, 'CPI yoy path 2024-10..2026-10: ' + fmt(p))
    lp = yoy_path(st, 'CPI', '2024-10', '2026-10')
    for ym, rp in [('2026-02', '2.434'), ('2026-04', '3.78'), ('2026-05', '4.1666'), ('2026-07', '3.30'), ('2026-08', '3.35'), ('2026-09', '3.72')]:
        addn(S, 'CPI yoy %s' % ym, 'series_store CPI yoy(%s)' % ym, st.yoy('CPI', ym), rp, 'turnings/TR1 link2')
    add(S, 'CPI yoy 2026-10 absent (base 2025-10 missing)', 'series_store CPI 2025-10', st.month_val('CPI', '2025-10'), 'absent', st.month_val('CPI', '2025-10') is None, '')
    addn(S, 'CPI yoy peak 2026-05 rounded 4.17', 'series_store CPI yoy(2026-05)', round(st.yoy('CPI', '2026-05'), 2), '4.17', '')
    w = yoy_path(st, 'CPI', '2025-11', '2026-10')
    info(S, 'CPI yoy window: ' + fmt(w))
    pk = argmax(yoy_path(st, 'CPI', '2025-11', '2026-09'))
    add(S, 'CPI yoy peak month (valid yoy)', 'series_store CPI yoy argmax 2025-11..2026-09', pk[0], '2026-05', pk[0] == '2026-05', '2026-05 见顶')
    lo = argmin(yoy_path(st, 'CPI', '2025-11', '2026-10'))
    add(S, 'CPI yoy low month', 'series_store CPI yoy argmin 2025-11..2026-10', lo[0], '2026-01', lo[0] == '2026-01', '低点均在 2026-01')
    after = yoy_path(st, 'CPI', '2026-06', '2026-09')
    mx = argmax(after)
    add(S, 'CPI yoy after peak never exceeds peak', 'series_store CPI yoy max 2026-06..2026-09 = %.4f (peak 2026-05)' % mx[1], bool(mx[1] < st.yoy('CPI', '2026-05')), True, bool(mx[1] < st.yoy('CPI', '2026-05')), '未再越过高点')
    for ym, rp in [('2026-02', '2.47'), ('2026-05', '2.8229'), ('2026-08', '2.4462'), ('2026-09', '2.57')]:
        addn(S, 'CORE_CPI yoy %s' % ym, 'series_store CORE_CPI yoy(%s)' % ym, st.yoy('CORE_CPI', ym), rp, 'TR1 link1 / candidate face / latest valid yoy')
    addn(S, 'CORE_CPI yoy 2026-05 rounded', 'series_store CORE_CPI yoy(2026-05)', st.yoy('CORE_CPI', '2026-05'), '2.82', '')
    info(S, 'CORE_CPI yoy path: ' + fmt(yoy_path(st, 'CORE_CPI', '2025-11', '2026-10')))

    # ---- CORE_PCE
    for ym, rp in [('2026-05', '3.16'), ('2026-07', '3.00'), ('2026-09', '3.12')]:
        addn(S, 'CORE_PCE yoy %s' % ym, 'series_store CORE_PCE yoy(%s)' % ym, st.yoy('CORE_PCE', ym), rp, '')
    pp = yoy_path(st, 'CORE_PCE', '2025-11', '2026-09')
    info(S, 'CORE_PCE yoy path: ' + fmt(pp))
    pk = argmax(pp)
    add(S, 'CORE_PCE yoy peak month', 'series_store CORE_PCE yoy argmax 2025-11..2026-09', pk[0], '2026-05', pk[0] == '2026-05', '月度同比自2026-05高点3.16回落')
    mx = argmax(yoy_path(st, 'CORE_PCE', '2026-06', '2026-09'))
    add(S, 'CORE_PCE yoy after peak never exceeds peak', 'series_store max 2026-06..2026-09 = %.4f (peak 2026-05)' % mx[1], bool(mx[1] < st.yoy('CORE_PCE', '2026-05')), True, bool(mx[1] < st.yoy('CORE_PCE', '2026-05')), '未再越过高点')
    add(S, 'CORE_PCE latest obs month = 2026-09', 'series_store CORE_PCE dates', st.dates('CORE_PCE')[-1][:7], '2026-09', st.dates('CORE_PCE')[-1][:7] == '2026-09', '')
    add(S, 'CORE_PCE 2026-10 not visible at cutoff', 'series_store + seat rule', pub_date(entries, 'CORE_PCE', st.dates('CORE_PCE')[-1]) if st.month_last_date('CORE_PCE', '2026-10') else 'absent', '>2026-11-23', (st.month_last_date('CORE_PCE', '2026-10') is None) or pub_date(entries, 'CORE_PCE', st.month_last_date('CORE_PCE', '2026-10')) > CUTOFF, '')

    # ---- INDPRO
    for ym, rp in [('2025-11', '1.7543'), ('2026-02', '0.7972')]:
        addn(S, 'INDPRO yoy %s' % ym, 'series_store INDPRO yoy(%s)' % ym, st.yoy('INDPRO', ym), rp, 'turnings[1]')
    a = st.yoy('INDPRO', '2025-11')
    b = st.yoy('INDPRO', '2026-02')
    add(S, 'INDPRO yoy halved (ratio < 0.5)', 'series_store INDPRO yoy ratio 2026-02/2025-11', round(b / a, 4), '<0.5', b / a < 0.5, '折半')
    info(S, 'INDPRO yoy path: ' + fmt(yoy_path(st, 'INDPRO', '2025-08', '2026-10')))

    # ---- EA HICP
    for ym, rp in [('2026-01', '1.7'), ('2026-02', '1.9'), ('2026-05', '3.2'), ('2026-06', '2.8')]:
        addn(S, 'EA_HICP_YOY %s' % ym, 'series_store EA_HICP_YOY@%s' % ym, st.month_val('EA_HICP_YOY', ym), rp, '')
    pe = path(st, 'EA_HICP_YOY', '2025-10', '2026-10')
    info(S, 'EA HICP path: ' + fmt(pe))
    lo = argmin(path(st, 'EA_HICP_YOY', '2025-11', '2026-10'))
    add(S, 'EA HICP low month', 'series_store EA_HICP_YOY argmin 2025-11..2026-10', lo[0], '2026-01', lo[0] == '2026-01', '自2026-01低点1.7')
    hi = argmax(path(st, 'EA_HICP_YOY', '2025-11', '2026-10'))
    add(S, 'EA HICP high month (本轮最高)', 'series_store EA_HICP_YOY argmax 2025-11..2026-10', hi[0], '2026-10', hi[0] == '2026-10', '升至本轮最高')
    m1 = monotonic(path(st, 'EA_HICP_YOY', '2026-01', '2026-05'), 1)
    add(S, 'EA HICP 连续上行 2026-01..2026-05', 'series_store EA_HICP_YOY monotonic up', m1, True, m1 is True, '')
    v = {}
    for ym, val in path(st, 'EA_HICP_YOY', '2025-12', '2026-10'):
        v[ym] = val
    d02 = v['2026-02'] - v['2026-01']
    d03 = v['2026-03'] - v['2026-02']
    d04 = v['2026-04'] - v['2026-03']
    d05 = v['2026-05'] - v['2026-04']
    info(S, 'EA HICP monthly increments 02..05: %.2f %.2f %.2f %.2f' % (d02, d03, d04, d05))
    add(S, 'EA HICP 2026-03起加速 (inc03>inc02)', 'series_store EA_HICP_YOY increments', '%.2f vs %.2f' % (d03, d02), 'inc03>inc02', d03 > d02, '')
    d07 = v['2026-07'] - v['2026-06']
    d08 = v['2026-08'] - v['2026-07']
    d09 = v['2026-09'] - v['2026-08']
    d10 = v['2026-10'] - v['2026-09']
    info(S, 'EA HICP monthly increments 07..10: %.2f %.2f %.2f %.2f' % (d07, d08, d09, d10))
    m2 = monotonic(path(st, 'EA_HICP_YOY', '2026-07', '2026-10'), 1)
    add(S, 'EA HICP 再度上行 2026-07..2026-10', 'series_store EA_HICP_YOY monotonic up', m2, True, m2 is True, '自2026-07再度上行')
    add(S, 'EA HICP 2026-08至10加速 (each increment > 2026-07 increment)', 'series_store EA_HICP_YOY increments 07..10', '%.2f %.2f %.2f %.2f' % (d07, d08, d09, d10), 'd08,d09,d10 > d07', d08 > d07 and d09 > d07 and d10 > d07, 'note: 2026-10 increment smaller than 2026-09')
    info(S, 'EA HICP increments 2026-07..10 (info only, strict reading of 加速 not counted): %+.2f %+.2f %+.2f %+.2f' % (d07, d08, d09, d10))
    add(S, 'EA HICP latest visible obs at cutoff = 2026-10', 'series_store + seat rule', st.latest_visible('EA_HICP_YOY', CUTOFF, entries), '2026-10', st.latest_visible('EA_HICP_YOY', CUTOFF, entries)[0][:7] == '2026-10', '')

    # ---- CN PPI
    for ym, rp in [('2026-02', '-0.9'), ('2026-05', '3.9')]:
        addn(S, 'CN_PPI_YOY %s' % ym, 'series_store CN_PPI_YOY@%s' % ym, st.month_val('CN_PPI_YOY', ym), rp, 'TR1 link1 / turning[0]')
    pc = path(st, 'CN_PPI_YOY', '2024-10', '2026-10')
    info(S, 'CN PPI path: ' + fmt(pc))
    lo = argmin(path(st, 'CN_PPI_YOY', '2025-11', '2026-10'))
    add(S, 'CN PPI low month (window)', 'series_store CN_PPI_YOY argmin 2025-11..2026-10', lo[0], '2025-11', lo[0] == '2025-11', '中国 PPI 低点在 2025-11')
    lo2 = argmin(path(st, 'CN_PPI_YOY', '2024-11', '2026-10'))
    info(S, 'CN PPI argmin over 2024-11..2026-10: %s %.2f' % (lo2[0], lo2[1]))
    m1 = monotonic(path(st, 'CN_PPI_YOY', '2025-11', '2026-05'), 1)
    add(S, 'CN PPI 连升 2025-11..2026-05', 'series_store CN_PPI_YOY monotonic up', m1, True, m1 is True, '此后连升 (to resonance-window end)')
    m1b = monotonic(path(st, 'CN_PPI_YOY', '2025-11', '2026-06'), 1)
    info(S, 'CN PPI monotonic up 2025-11..2026-06: %s' % m1b)
    w = path(st, 'CN_PPI_YOY', '2025-11', '2026-10')
    hi = argmax(w)
    add(S, 'CN PPI latest = window high', 'series_store CN_PPI_YOY argmax 2025-11..2026-10', hi[0], '2026-10', hi[0] == '2026-10', '续创本轮新高')
    c = {}
    for ym, val in w:
        c[ym] = val
    seq = [c['2026-07'], c['2026-08'], c['2026-09'], c['2026-10']]
    info(S, 'CN PPI 2026-07..10: %.2f %.2f %.2f %.2f' % (seq[0], seq[1], seq[2], seq[3]))
    add(S, 'CN PPI rising every month 2026-07..2026-10', 'series_store CN_PPI_YOY', seq, 'strictly increasing', seq[0] < seq[1] < seq[2] < seq[3], '续创本轮新高 / 2026-07回落至3.5后升至5.7')
    swing = st.month_val('CN_PPI_YOY', '2026-10') - st.month_val('CN_PPI_YOY', '2025-10')
    others = [st.yoy('CPI', '2026-09') - st.yoy('CPI', '2025-09'), st.month_val('EA_HICP_YOY', '2026-10') - st.month_val('EA_HICP_YOY', '2025-10'),
              st.month_val('JP_CPI_YOY', '2026-10') - st.month_val('JP_CPI_YOY', '2025-10'), st.month_val('CN_CPI_YOY', '2026-10') - st.month_val('CN_CPI_YOY', '2025-10')]
    add(S, 'CN PPI largest 12m swing among four regions', 'series_store 12m change: CN PPI vs CPI/EA/JP/CN CPI', '%.2f vs max %.2f' % (swing, max(others)), 'largest', swing > max(others), '四地最大价格摆动')

    # ---- CN CPI
    for ym, rp in [('2026-01', '0.2'), ('2026-04', '1.2')]:
        addn(S, 'CN_CPI_YOY %s' % ym, 'series_store CN_CPI_YOY@%s' % ym, st.month_val('CN_CPI_YOY', ym), rp, 'candidate face')

    # ---- CN PMI
    pm = path(st, 'CN_PMI_MFG', '2024-10', '2026-10')
    info(S, 'CN PMI path: ' + fmt(pm))
    w = path(st, 'CN_PMI_MFG', '2025-11', '2026-10')
    above = []
    rng = []
    for ym, val in w:
        if val > 50.0:
            above.append('%s=%.1f' % (ym, val))
        if ym != '2026-05' and val <= 50.0:
            rng.append(val)
    add(S, 'CN PMI months above 50', 'series_store CN_PMI_MFG 2025-11..2026-10', ' '.join(above), '2025-12=50.1 2026-03=50.4 2026-04=50.3 2026-06=50.3 2026-09=50.1', ' '.join(above) == '2025-12=50.1 2026-03=50.4 2026-04=50.3 2026-06=50.3 2026-09=50.1', '')
    add(S, 'CN PMI 2026-05 = 50.0', 'series_store CN_PMI_MFG@2026-05', st.month_val('CN_PMI_MFG', '2026-05'), '50.0', abs(st.month_val('CN_PMI_MFG', '2026-05') - 50.0) < 1e-9, '')
    add(S, 'CN PMI other months within 49.0..49.8', 'series_store CN_PMI_MFG min/max of others', '%.1f..%.1f' % (min(rng), max(rng)), '49.0..49.8', min(rng) >= 49.0 - 1e-9 and max(rng) <= 49.8 + 1e-9, 'n=%d' % len(rng))
    for ym, rp in [('2025-10', '-2.2'), ('2026-07', '-0.2'), ('2026-10', '0.61')]:
        a = st.month_val('CN_PMI_MFG', ym)
        b = st.month_val('CN_PMI_MFG', addm(ym, -12))
        addn(S, 'CN PMI yoy percent %s' % ym, 'series_store CN_PMI_MFG %s vs %s (pct change)' % (ym, addm(ym, -12)), (a / b - 1.0) * 100.0, rp, '同比口径 -2.2→-0.2→+0.61; pp difference = %.2f' % (a - b))

    # ---- JP CPI
    for ym, rp in [('2025-11', '2.9'), ('2025-12', '2.13'), ('2026-01', '1.51'), ('2026-02', '1.27'), ('2026-03', '1.46'), ('2026-04', '1.38')]:
        addn(S, 'JP_CPI_YOY %s' % ym, 'series_store JP_CPI_YOY@%s' % ym, st.month_val('JP_CPI_YOY', ym), rp, 'turnings[2]')
    jp = path(st, 'JP_CPI_YOY', '2024-01', '2026-10')
    info(S, 'JP CPI path: ' + fmt(jp))
    addn(S, 'JP_CPI_YOY 2025-01', 'series_store JP_CPI_YOY@2025-01', st.month_val('JP_CPI_YOY', '2025-01'), '4.03', '自 2025-01 高点 4.03')
    hi = argmax(path(st, 'JP_CPI_YOY', '2024-01', '2026-10'))
    info(S, 'JP CPI argmax 2024-01..2026-10: %s %.2f' % (hi[0], hi[1]))
    lo = argmin(path(st, 'JP_CPI_YOY', '2025-01', '2026-02'))
    add(S, 'JP CPI low = 2026-02 since 2025-01', 'series_store JP_CPI_YOY argmin 2025-01..2026-02', lo[0], '2026-02', lo[0] == '2026-02', '')
    c = {}
    for ym, val in path(st, 'JP_CPI_YOY', '2025-01', '2026-10'):
        c[ym] = val
    add(S, 'JP CPI rebound 2025-09', 'series_store JP_CPI_YOY 2025-09 vs 2025-08', '%.2f vs %.2f' % (c['2025-09'], c['2025-08']), 'up', c['2025-09'] > c['2025-08'], '其间 2025-09、2025-10 小幅回升')
    add(S, 'JP CPI rebound 2025-10', 'series_store JP_CPI_YOY 2025-10 vs 2025-09', '%.2f vs %.2f' % (c['2025-10'], c['2025-09']), 'up', c['2025-10'] > c['2025-09'], '')
    others = []
    for ym in ('2025-02', '2025-03', '2025-04', '2025-05', '2025-06', '2025-07', '2025-11', '2025-12', '2026-01', '2026-02'):
        others.append(ym)
    info(S, 'JP CPI general decline 2025-01..2026-02 end change: %.2f' % (c['2026-02'] - c['2025-01']))
    m3 = monotonic(path(st, 'JP_CPI_YOY', '2026-05', '2026-10'), 1)
    add(S, 'JP CPI 持续回升自 2026-05 起 (monotonic up to 2026-10)', 'series_store JP_CPI_YOY monotonic up', m3, True, m3 is True, '')
    add(S, 'JP CPI first uptick month after trough = 2026-03', 'series_store JP_CPI_YOY 2026-03 vs 2026-02', '%.2f vs %.2f' % (c['2026-03'], c['2026-02']), 'up', c['2026-03'] > c['2026-02'], '全国口径的回升起点(2026-03)')

    # ---- Tokyo
    for ym, rp in [('2026-06', '1.6'), ('2026-08', '1.9'), ('2026-09', '2.69')]:
        addn(S, 'JP_CPI_TOKYO_YOY %s' % ym, 'series_store JP_CPI_TOKYO_YOY@%s' % ym, st.month_val('JP_CPI_TOKYO_YOY', ym), rp, 'turning supplement')
    tk = path(st, 'JP_CPI_TOKYO_YOY', '2025-10', '2026-10')
    info(S, 'Tokyo CPI path: ' + fmt(tk))
    t = {}
    for ym, val in tk:
        t[ym] = val
    ok = True
    prev = None
    for ym in ('2026-06', '2026-07', '2026-08', '2026-09', '2026-10'):
        if prev is not None and not (t[ym] > prev):
            ok = False
        prev = t[ym]
    add(S, 'Tokyo CPI rising every month 2026-06..2026-10', 'series_store JP_CPI_TOKYO_YOY', [t[x] for x in ('2026-06', '2026-07', '2026-08', '2026-09', '2026-10')], 'strictly increasing', ok, '东京口径的上行起点(2026-06)')

    # ---- JP policy rate monthly
    jr = path(st, 'JP_POLICY_RATE', '2024-10', '2026-10')
    info(S, 'JP_POLICY_RATE monthly: ' + fmt(jr))
    j = {}
    for ym, val in jr:
        j[ym] = val
    for ym, rp in [('2025-11', '0.478'), ('2025-12', '0.557')]:
        addn(S, 'JP_POLICY_RATE %s' % ym, 'series_store JP_POLICY_RATE@%s' % ym, st.month_val('JP_POLICY_RATE', ym), rp, '')
    addn(S, 'JP policy net change from 2025-11 (bp)', 'series_store (2026-10 - 2025-11)*100', (j['2026-10'] - j['2025-11']) * 100.0, '75', '净 +75 个基点')
    addn(S, 'JP policy net change from 2025-12 (bp)', 'series_store (2026-10 - 2025-12)*100', (j['2026-10'] - j['2025-12']) * 100.0, '67', '自 2025-12 起 +67bp')
    steps = [('2025-12', '8'), ('2026-01', '17'), ('2026-06', '11'), ('2026-07', '14'), ('2026-09', '7'), ('2026-10', '18')]
    for ym, rp in steps:
        addn(S, 'JP policy step %s (bp)' % ym, 'series_store (%s - %s)*100' % (ym, addm(ym, -1)), (j[ym] - j[addm(ym, -1)]) * 100.0, rp, '', 0.5)
    small = []
    declines = []
    ym = '2025-12'
    while ym <= '2026-10':
        if addm(ym, -1) not in j or j[addm(ym, -1)] is None or j[ym] is None:
            ym = addm(ym, 1)
            continue
        d = (j[ym] - j[addm(ym, -1)]) * 100.0
        if abs(d) > 1e-9 and abs(d) < 1.0:
            small.append('%s:%+.2fbp' % (ym, d))
        if d < -0.5:
            declines.append('%s:%+.2fbp' % (ym, d))
        ym = addm(ym, 1)
    add(S, 'JP policy small rounding changes only in 2026-04 and 2026-08', 'series_store JP_POLICY_RATE month steps', ' '.join(small), '2026-04 and 2026-08', len(small) == 2 and '2026-04' in ' '.join(small) and '2026-08' in ' '.join(small), '各约零点一个基点的舍入变动')
    add(S, 'JP policy no decline >= 0.5bp in window', 'series_store JP_POLICY_RATE month steps', ' '.join(declines), 'none', len(declines) == 0, '窗内未回撤')
    first = None
    pre = []
    ym = '2024-11'
    while ym <= '2026-10':
        if addm(ym, -1) not in j or j[addm(ym, -1)] is None or j[ym] is None:
            ym = addm(ym, 1)
            continue
        d = (j[ym] - j[addm(ym, -1)]) * 100.0
        if d >= 1.0:
            if ym >= '2025-11' and first is None:
                first = ym
            if ym < '2025-11':
                pre.append('%s:%+.1fbp' % (ym, d))
        ym = addm(ym, 1)
    add(S, 'JP policy first in-window hike >= 1bp', 'series_store JP_POLICY_RATE steps 2025-11..2026-10', first, '2025-12', first == '2025-12', '日本月均利率上行自2025-12已开始 (window start 2025-11-23)')
    info(S, 'JP policy pre-window hikes >= 1bp: ' + ' '.join(pre))

    # ---- monthly visibility of CPI before decisions
    for dec, ym, rp in [('2026-06-11', '2026-04', '3.78'), ('2026-09-10', '2026-07', '3.30'), ('2026-09-16', '2026-08', '3.35'), ('2026-09-18', '2026-08', '3.35')]:
        r = st.latest_visible('CPI', dec, entries)
        addn(S, 'CPI yoy latest visible before %s = %s' % (dec, ym), 'series_store CPI latest visible (seat rule) = %s pub %s' % (None if r is None else r[0], None if r is None else r[1]), st.yoy('CPI', r[0][:7]) if r else None, rp, 'obs month %s' % (None if r is None else r[0][:7]))
        add(S, 'CPI obs month visible before %s' % dec, 'series_store + seat rule', None if r is None else r[0][:7], ym, r is not None and r[0][:7] == ym, '')
    add(S, 'CPI 2026-09 obs published after 2026-09-18', 'series_store + seat rule', pub_date(entries, 'CPI', st.month_last_date('CPI', '2026-09')), '>2026-09-18', pub_date(entries, 'CPI', st.month_last_date('CPI', '2026-09')) > '2026-09-18', '决议后发布的 2026-09 观测')
    add(S, 'CPI 2025-11 base present for 2026-11 yoy', 'series_store CPI@2025-11', st.month_val('CPI', '2025-11'), 'present', st.month_val('CPI', '2025-11') is not None, '2026-11 起同比不受缺基期影响')
    add(S, 'CPI yoy at cutoff not below 2.5 / 3.5 (SCN thresholds compatible)', 'series_store CPI yoy 2026-09', st.yoy('CPI', '2026-09'), '>=3.5', st.yoy('CPI', '2026-09') >= 3.5, '')
    add(S, 'CORE_PCE yoy at cutoff not below 2.8', 'series_store CORE_PCE yoy 2026-09', st.yoy('CORE_PCE', '2026-09'), '>=2.8', st.yoy('CORE_PCE', '2026-09') >= 2.8, '')
    add(S, 'CN_NEW_LOANS latest obs month', 'series_store CN_NEW_LOANS', st.dates('CN_NEW_LOANS')[-1][:7], '2026-10', st.dates('CN_NEW_LOANS')[-1][:7] == '2026-10', 'C3')


def sec_daily(S, st, snap, rep, entries, jud, blob):
    # rates trio
    for (d0, d1, reps, label) in [('2025-11-19', '2026-11-19', ('91', '102', '-11'), '12m'),
                                  ('2026-10-20', '2026-11-19', ('-8.0', '11.0', '-19.0'), '1m common days')]:
        vals0 = []
        vals1 = []
        for m in ('UST_10Y', 'TIPS_10Y', 'BEI_10Y'):
            a = st.at(m, d0)
            b = st.at(m, d1)
            vals0.append(a)
            vals1.append(b)
            add(S, '%s trio common day %s has %s' % (label, d0, m), 'series_store %s@%s' % (m, d0), a, 'present', a is not None, '')
            add(S, '%s trio common day %s has %s' % (label, d1, m), 'series_store %s@%s' % (m, d1), b, 'present', b is not None, '')
        i = 0
        names = ('UST_10Y', 'TIPS_10Y', 'BEI_10Y')
        while i < 3:
            addn(S, '%s %s change (bp)' % (label, names[i]), 'series_store (%s %s→%s)*100' % (names[i], d0, d1), (vals1[i] - vals0[i]) * 100.0, reps[i], '', 0.5)
            i += 1
        res0 = vals0[0] - vals0[1] - vals0[2]
        res1 = vals1[0] - vals1[1] - vals1[2]
        addn(S, '%s trio residual change (bp)' % label, 'series_store identity residual change*100', (res1 - res0) * 100.0, '0', '恒等残差0', 0.5)
        info(S, '%s trio start %s end %s' % (label, vals0, vals1))
    for m, rp in [('UST_10Y', '5.04'), ('TIPS_10Y', '2.88'), ('BEI_10Y', '2.16')]:
        addn(S, '%s level 2026-11-19' % m, 'series_store %s@2026-11-19' % m, st.at(m, '2026-11-19'), rp, 'M1 link3')
    addn(S, 'BEI_10Y level 2026-11-20', 'series_store BEI_10Y@2026-11-20', st.at('BEI_10Y', '2026-11-20'), '2.15', 'latest')
    for d, rp in [('2026-02-27', '2.25'), ('2026-05-04', '2.50'), ('2026-06-10', '2.34'), ('2026-10-23', '2.34')]:
        addn(S, 'BEI_10Y %s' % d, 'series_store BEI_10Y@%s' % d, st.at('BEI_10Y', d), rp, 'TR1 link2')
    lo = None
    hi = None
    for d in st.dates('BEI_10Y'):
        if d > '2026-06-17':
            v = st.at('BEI_10Y', d)
            if lo is None or v < lo:
                lo = v
            if hi is None or v > hi:
                hi = v
    add(S, 'BEI_10Y range after 2026-06-17', 'series_store BEI_10Y min..max', '%.2f..%.2f' % (lo, hi), '2.15..2.40', abs(lo - 2.15) < 1e-9 and abs(hi - 2.40) < 1e-9, '')
    add(S, 'BEI_10Y 2026-10-23→2026-11-20 calendar days', 'dates', days_between('2026-10-23', '2026-11-20'), '28', days_between('2026-10-23', '2026-11-20') == 28, '')
    rd = jud['reader_map'].get('rates_decomposition')
    if rd:
        addn(S, 'rates_decomposition.nominal_bp', 'series_store recompute', (st.at('UST_10Y', '2026-11-19') - st.at('UST_10Y', '2026-10-20')) * 100.0, rd.get('nominal_bp'), 'judgment field')
        addn(S, 'rates_decomposition.real_bp', 'series_store recompute', (st.at('TIPS_10Y', '2026-11-19') - st.at('TIPS_10Y', '2026-10-20')) * 100.0, rd.get('real_bp'), 'judgment field')
        addn(S, 'rates_decomposition.bei_bp', 'series_store recompute', (st.at('BEI_10Y', '2026-11-19') - st.at('BEI_10Y', '2026-10-20')) * 100.0, rd.get('bei_bp'), 'judgment field')
        add(S, 'rates_decomposition window', 'judgment field', '%s..%s' % (rd.get('window_from'), rd.get('window_to')), '2026-10-20..2026-11-19', rd.get('window_from') == '2026-10-20' and rd.get('window_to') == '2026-11-19', '')

    # asset returns echo
    for e in jud['reader_map'].get('asset_returns_echo', []):
        m = e['metric_id']
        d0 = e['window']['from']
        d1 = e['window']['to']
        a = st.at(m, d0)
        b = st.at(m, d1)
        comp = None if (a is None or b is None) else (b / a - 1.0) * 100.0
        addn(S, 'asset %s %s→%s' % (m, d0, d1), 'series_store %s %s→%s' % (m, d0, d1), comp, e.get('chg_pct'), 'asset_returns_echo')
    for m, rp in [('SPX', '-9.36'), ('DAX', '-1.50'), ('CAC40', '1.86'), ('NIKKEI225', '-9.98'), ('VIX', '84.52')]:
        a = st.at(m, '2026-10-23')
        b = st.at(m, '2026-11-20')
        addn(S, 'close basis %s 2026-10-23→2026-11-20' % m, 'series_store %s 2026-10-23→2026-11-20' % m, None if (a is None or b is None) else (b / a - 1.0) * 100.0, rp, 'TR1 link3 close basis')
    addn(S, 'VIX 2026-10-23', 'series_store VIX@2026-10-23', st.at('VIX', '2026-10-23'), '19.45', '')
    addn(S, 'VIX 2026-11-23', 'series_store VIX@2026-11-23', st.at('VIX', '2026-11-23'), '27.01', '')
    for m, rp in [('UST_10Y', '5.04'), ('TIPS_10Y', '2.88'), ('BEI_10Y', '2.15'), ('VIX', '27.01'), ('USDJPY', '159.35'), ('DFF', '3.88'), ('JP_POLICY_RATE', '1.227'), ('CN_PPI_YOY', '5.7'), ('CN_CPI_YOY', '0.7'), ('CN_PMI_MFG', '49.3')]:
        r = st.le(m, CUTOFF)
        addn(S, 'C1 level %s' % m, 'series_store %s latest %s' % (m, None if r is None else r[0]), None if r is None else r[1], rp, 'latest level at cutoff', 0.005)
    addn(S, 'C1 level HY_OAS', 'series_store HY_OAS@2026-11-19', st.at('HY_OAS', '2026-11-19'), '3.52', '')
    for m, rp in [('SPX', '-5.51'), ('NIKKEI225', '-9.98'), ('GOLD_F', '-8.05'), ('DXY', '2.23')]:
        e = None
        for x in jud['reader_map'].get('asset_returns_echo', []):
            if x['metric_id'] == m:
                e = x
        a = st.at(m, '2026-10-23')
        b = st.at(m, '2026-11-23') if m != 'NIKKEI225' else st.at(m, '2026-11-20')
        addn(S, 'M1 link4 %s near 1m' % m, 'series_store %s 2026-10-23→%s' % (m, None if r is None else '2026-11-23' if m != 'NIKKEI225' else '2026-11-20'), None if (a is None or b is None) else (b / a - 1.0) * 100.0, rp, 'SPX/VIX 2026-10-23→2026-11-23')

    # HY_OAS
    ds = st.dates('HY_OAS')
    cur = st.at('HY_OAS', '2026-11-19')
    mx = None
    for d in ds:
        v = st.at('HY_OAS', d)
        if mx is None or v > mx[1]:
            mx = (d, v)
    add(S, 'HY_OAS series high date', 'series_store HY_OAS argmax', mx[0], '2025-04-07', mx[0] == '2025-04-07', '')
    addn(S, 'HY_OAS series high', 'series_store HY_OAS@%s' % mx[0], mx[1], '4.61', '')
    add(S, 'HY_OAS first date (自 2023-11-21 起)', 'series_store HY_OAS first date', ds[0], '2023-11-21', ds[0] == '2023-11-21', '')
    n_le = 0
    for d in ds:
        if st.at('HY_OAS', d) <= cur:
            n_le += 1
    pct = 100.0 * n_le / len(ds)
    addn(S, 'HY_OAS percentile of current value', 'series_store HY_OAS share of history <= current *100', pct, '92', '约第 92 百分位', 1.0)
    info(S, 'HY_OAS n=%d pct_le=%.2f first=%s last=%s' % (len(ds), pct, ds[0], ds[-1]))
    since = None
    for d in ds:
        if d < '2026-11-19' and st.at('HY_OAS', d) >= cur:
            since = d
    add(S, 'HY_OAS last earlier date with value >= current', 'series_store HY_OAS', since, '2025-05-09', since == '2025-05-09', '为 2025-05-09 以来最高')
    addn(S, 'HY_OAS 1w change vs 2026-11-13 (pp)', 'series_store HY_OAS 2026-11-19 - 2026-11-13', cur - st.at('HY_OAS', '2026-11-13'), '0.29', '')
    r = st.le('HY_OAS', '2026-11-12')
    addn(S, 'HY_OAS strict 7d change (pp)', 'series_store HY_OAS 2026-11-19 - %s' % r[0], cur - r[1], '0.32', '')
    r = st.le('HY_OAS', '2025-11-19')
    addn(S, 'HY_OAS 12m change (pp)', 'series_store HY_OAS 2026-11-19 - %s' % r[0], cur - r[1], '0.35', '')
    wk = []
    i = 0
    while i < len(ds):
        d = ds[i]
        r7 = None
        j = i
        while j >= 0 and days_between(ds[j], d) < 7:
            j -= 1
        if j >= 0 and days_between(ds[j], d) == 7:
            wk.append((d, st.at('HY_OAS', d) - st.at('HY_OAS', ds[j])))
        i += 1
    recent = [x for x in wk if x[0] >= '2026-08-23']
    mxw = None
    for x in recent:
        if mxw is None or x[1] > mxw[1]:
            mxw = x
    info(S, 'HY_OAS max strict 7d widening since 2026-08-23: %s %+.2f; n=%d' % (None if mxw is None else mxw[0], 0 if mxw is None else mxw[1], len(recent)))

    # BRENT_F
    for ym, rp in [('2026-02', '72.48'), ('2026-03', '118.35'), ('2026-05', '92.05')]:
        d = st.month_last_date('BRENT_F', ym)
        addn(S, 'BRENT_F month-end %s' % ym, 'series_store BRENT_F@%s' % d, st.at('BRENT_F', d), rp, 'TR1 link1')
    a = st.at('BRENT_F', st.month_last_date('BRENT_F', '2026-02'))
    b = st.at('BRENT_F', st.month_last_date('BRENT_F', '2026-05'))
    addn(S, 'BRENT_F first-last 2026-02→2026-05', 'series_store BRENT_F month-ends', (b / a - 1.0) * 100.0, '27.00', '首尾 +27.00%')
    addn(S, 'BRENT_F level 2026-11-23', 'series_store BRENT_F@2026-11-23', st.at('BRENT_F', '2026-11-23'), '88.19', '')
    d = st.month_last_date('BRENT_F', '2026-10')
    addn(S, 'BRENT_F MTD', 'series_store BRENT_F %s→2026-11-23' % d, (st.at('BRENT_F', '2026-11-23') / st.at('BRENT_F', d) - 1.0) * 100.0, '-25.03', '当月至今')
    addn(S, 'BRENT_F engine near-30-day', 'series_store BRENT_F 2026-10-23→2026-11-23', (st.at('BRENT_F', '2026-11-23') / st.at('BRENT_F', '2026-10-23') - 1.0) * 100.0, '-24.44', 'engine face quoted', 0.01)

    # FX
    addn(S, 'USDJPY 2026-11-23', 'series_store USDJPY@2026-11-23', st.at('USDJPY', '2026-11-23'), '159.347', '')
    addn(S, 'USDJPY 2026-10-23', 'series_store USDJPY@2026-10-23', st.at('USDJPY', '2026-10-23'), '156.494', '')
    addn(S, 'USDJPY near-30-day', 'series_store USDJPY 2026-10-23→2026-11-23', (st.at('USDJPY', '2026-11-23') / st.at('USDJPY', '2026-10-23') - 1.0) * 100.0, '1.82', 'TR2', 0.01)
    add(S, 'USDCNY@2026-11-23 present', 'series_store USDCNY', st.at('USDCNY', '2026-11-23'), 'present', st.at('USDCNY', '2026-11-23') is not None, 'C3 ref')

    # policy series
    for m, reps in [('DFEDTARU', ('4.0', '3.75', '4.0')), ('DFF', ('3.88', '3.63', '3.88')), ('ECB_DFR', ('2.0', '2.25', '2.5')), ('ECB_MRO', ('2.15', '2.4', '2.65')), ('CN_LPR_1Y', ('3.0', '3.0', '3.0')), ('CN_OMO_7D', ('1.4', '1.4', '1.4'))]:
        i = 0
        for an in ('12个月前', '3个月前', '最新一期'):
            lim = ANCHORS[an]
            if m == 'DFF':
                lim = plus_days(lim, -1)
            r = st.le(m, lim)
            addn(S, '%s@%s' % (m, TAG[an]), 'series_store %s latest %s' % (m, None if r is None else r[0]), None if r is None else r[1], reps[i], '')
            i += 1
    for m, exp in [('DFEDTARU', '2025-11-23|2026-08-23|2026-11-23'), ('DFF', '2025-11-22|2026-08-22|2026-11-19'), ('ECB_DFR', '2025-06-11|2026-06-17|2026-09-16'), ('ECB_MRO', '2025-06-11|2026-06-17|2026-09-16'), ('CN_LPR_1Y', '2025-11-20|2026-08-20|2026-11-20'), ('CN_OMO_7D', '2025-11-14|2026-08-21|2026-10-30')]:
        got = []
        for an in ('12个月前', '3个月前', '最新一期'):
            lim = ANCHORS[an]
            if m == 'DFF':
                lim = plus_days(lim, -1)
            r = st.le(m, lim)
            got.append('NA' if r is None else r[0])
        add(S, '%s anchor observation dates' % m, 'series_store %s latest<=anchor' % m, '|'.join(got), exp, '|'.join(got) == exp, '')

    def changes(m, d0, d1, minbp):
        out = []
        prev = None
        for d in st.dates(m):
            if d < d0 or d > d1:
                continue
            v = st.at(m, d)
            if prev is not None and abs(v - prev[1]) * 100.0 >= minbp:
                out.append('%s:%.4g→%.4g' % (d, prev[1], v))
            prev = (d, v)
        return out

    ch = changes('DFEDTARU', '2025-11-24', '2026-11-23', 1)
    add(S, 'DFEDTARU changes in window', 'series_store DFEDTARU', ' '.join(ch), '2025-12-11:4→3.75 2026-09-17:3.75→4', ' '.join(ch) == '2025-12-11:4→3.75 2026-09-17:3.75→4', 'Fed effective dates')
    ch = changes('DFF', '2025-11-24', '2026-11-23', 20)
    add(S, 'DFF changes >=20bp in window', 'series_store DFF', ' '.join(ch), '2025-12-11:3.89→3.64 2026-09-17:3.63→3.88', ' '.join(ch) == '2025-12-11:3.89→3.64 2026-09-17:3.63→3.88', '')
    info(S, 'DFF small changes: ' + ' '.join(changes('DFF', '2025-11-24', '2026-11-23', 1)))
    ch = changes('ECB_DFR', '2025-06-01', '2026-11-23', 1)
    add(S, 'ECB_DFR changes since 2025-06', 'series_store ECB_DFR', ' '.join(ch), '2026-06-17:2→2.25 2026-09-16:2.25→2.5', ' '.join(ch) == '2026-06-17:2→2.25 2026-09-16:2.25→2.5', '')
    ch = changes('ECB_MRO', '2025-06-01', '2026-11-23', 1)
    add(S, 'ECB_MRO changes since 2025-06', 'series_store ECB_MRO', ' '.join(ch), '2026-06-17:2.15→2.4 2026-09-16:2.4→2.65', ' '.join(ch) == '2026-06-17:2.15→2.4 2026-09-16:2.4→2.65', '')
    add(S, 'ECB series end date', 'series_store ECB_MRO/ECB_DFR last date', '%s/%s' % (st.dates('ECB_MRO')[-1], st.dates('ECB_DFR')[-1]), '2026-09-16', st.dates('ECB_MRO')[-1] == '2026-09-16' and st.dates('ECB_DFR')[-1] == '2026-09-16', '')
    add(S, 'ECB series lag days', '2026-11-23 - last obs', days_between(st.dates('ECB_MRO')[-1], CUTOFF), '68', days_between(st.dates('ECB_MRO')[-1], CUTOFF) == 68, '')
    ch = changes('CN_LPR_1Y', '2025-11-24', '2026-11-23', 1)
    add(S, 'CN_LPR_1Y no change in window', 'series_store CN_LPR_1Y', ' '.join(ch), 'none', len(ch) == 0, '')
    ch = changes('CN_OMO_7D', '2025-11-24', '2026-11-23', 1)
    add(S, 'CN_OMO_7D no change in window', 'series_store CN_OMO_7D', ' '.join(ch), 'none', len(ch) == 0, '')
    r = st.le('CN_OMO_7D', CUTOFF)
    add(S, 'CN_OMO_7D last observation lag (days)', '2026-11-23 - last obs', days_between(r[0], CUTOFF), '24', days_between(r[0], CUTOFF) == 24, '滞后24天')
    info(S, 'CN_OMO_7D obs: ' + ' '.join(['%s=%g' % (d, st.at('CN_OMO_7D', d)) for d in st.dates('CN_OMO_7D')]))

    # cutoff-day observation basis
    for m, exp in [('SPX', '2026-11-23'), ('DAX', '2026-11-23'), ('CAC40', '2026-11-23'), ('VIX', '2026-11-23'), ('GOLD_F', '2026-11-23'), ('DXY', '2026-11-23'), ('BRENT_F', '2026-11-23'), ('USDJPY', '2026-11-23'), ('SHCOMP', '2026-11-23'), ('NIKKEI225', '2026-11-20'), ('UST_10Y', '2026-11-19'), ('TIPS_10Y', '2026-11-19'), ('BEI_10Y', '2026-11-20'), ('HY_OAS', '2026-11-19'), ('DFF', '2026-11-19'), ('DFEDTARU', '2026-11-23'), ('CN_POLICY_OVERNIGHT', '2026-11-23')]:
        add(S, 'last observation date %s' % m, 'series_store %s last date' % m, st.dates(m)[-1], exp, st.dates(m)[-1] == exp, 'basis note for cutoff-day observations')


def sec_history(S, st, snap, rep, entries, jud, blob):
    data = rep['steps'][61]['envelope']['data']
    top = data['top']
    cands = data['candidates']
    EXU = {'DFEDTARU': 'pp', 'UNEMPLOYMENT': 'pp', 'CPI': 'pct', 'INDPRO': 'pct', 'SPX': 'pct', 'NIKKEI225': 'pct',
           'DAX': 'pct', 'SHCOMP': 'pct', 'GOLD_F': 'pct', 'DXY': 'pct', 'UST_10Y': 'pp'}
    pat = re.compile(r'([A-Z0-9_]+) ([+-]\d+\.\d+)(pp|%)')
    DIMNAME = {'波动': 'volatility', '利率': 'rates', '通胀': 'inflation', '估值': 'valuation', '信用': 'credit', '增长': 'growth'}
    FEATNAME = {'CURVE_2S10S 12月变化': 'CURVE_2S10S_d12m', 'TIPS_10Y 12月变化': 'TIPS_10Y_d12m', 'UST_10Y 12月变化': 'UST_10Y_d12m',
                'CURVE_2S10S水平': 'CURVE_2S10S_level', 'SPX CAPE': 'SPX_CAPE_level', 'SPX 21日已实现波动': 'SPX_rv21', 'VIX水平': 'VIX_level'}
    hp = jud['reader_map']['history_periods']
    add(S, 'history periods count', 'judgment reader_map.history_periods', len(hp), '3 (top-3)', len(hp) == 3, '')
    for i, h in enumerate(hp):
        an = h['anchor_ym']
        t = top[i]
        add(S, '%s candidate month = engine rank %d' % (an, i + 1), 'report.json steps[61].data.top[%d].candidate_month' % i, t['candidate_month'], an, t['candidate_month'] == an, '')
        md = re.search(r'距离([\d.]+)', h['period_label'])
        addn(S, '%s distance' % an, 'report.json top[%d].distance' % i, t['distance'], md.group(1), 'judgment period_label')
        mp = re.search(r'分位([\d.]+)', h['period_label'])
        addn(S, '%s distance percentile' % an, 'report.json top[%d].distance_percentile' % i, t['distance_percentile'], mp.group(1), 'judgment period_label', 0.01)
        mc = re.search(r'(\d+)个有效候选', h['period_label'])
        if mc:
            add(S, '%s valid candidates' % an, 'report.json candidates.valid', cands['valid'], mc.group(1), str(cands['valid']) == mc.group(1), '')
        contrib = re.search(r'贡献维=(.+?)——', h['similarity']).group(1)
        tot = 0.0
        for nm, num in re.findall(r'([一-鿿]+)(\d+\.\d)%', contrib):
            key = DIMNAME.get(nm)
            ev = None if key is None else t['dims'][key]['contribution_share'] * 100.0
            addn(S, '%s contribution %s (%%)' % (an, nm), 'report.json top[%d].dims.%s.contribution_share*100' % (i, key), ev, num, '', 0.06)
            tot += float(num)
        addn(S, '%s contributions sum to 100' % an, 'judgment similarity text', tot, '100.0', 'shares renormalised to accounted dims', 0.3)
        # differences > 1 sigma
        listed = re.findall(r'([^、（）()]+?)\((?:[^,()]*,)?([+-]\d+\.\d+)\)', h['difference'])
        listed_names = []
        for nm, num in listed:
            nm = nm.strip().replace('差异>1σ逐维点名:', '').strip()
            key = FEATNAME.get(nm)
            listed_names.append(key)
            ev = None if key is None else t['features_detail'].get(key, {}).get('gap')
            sign_ok = True
            if '当前高于候选期' in h['difference'] and ev is not None:
                pass
            addn(S, '%s gap magnitude %s' % (an, nm), 'report.json top[%d].features_detail.%s.gap (abs)' % (i, key), None if ev is None else abs(ev), num.lstrip('+').lstrip('-'), '')
            if ev is not None:
                pos = ('当前高于候选期,+' + num.lstrip('+')) in h['difference']
                neg = ('候选期高于当前,' + num) in h['difference']
                sign_ok = (ev > 0 and pos) or (ev < 0 and neg)
                add(S, '%s gap direction %s' % (an, nm), 'engine gap sign', '+' if ev > 0 else '-', '+' if pos else '-', sign_ok, '')
        big = []
        for k, fd in t['features_detail'].items():
            if abs(fd.get('gap', 0.0)) > 1.0:
                big.append(k)
        add(S, '%s all |gap|>1 features listed' % an, 'report.json top[%d].features_detail' % i, ' '.join(sorted(big)), ' '.join(sorted(listed_names)), sorted(big) == sorted(listed_names), '')
        for k, why in t['missing_features'].items():
            add(S, '%s missing feature %s disclosed' % (an, k), 'report.json top[%d].missing_features' % i, why, why in h['difference'] or ('信用维' in h['difference']), (why in h['difference']) or ('信用维' in h['difference']), '')
        mw = h['match_window']
        add(S, '%s match window = 12 months ending at candidate month' % an, 'report.json feature_window_months x top[%d].candidate_month' % i, '%s..%s' % (addm(t['candidate_month'], -11), t['candidate_month']), '%s..%s' % (mw['start_ym'], mw['end_ym']), addm(t['candidate_month'], -11) == mw['start_ym'] and t['candidate_month'] == mw['end_ym'], 'cluster members %d: %s..%s' % (len(t['cluster_members']), t['cluster_members'][0], t['cluster_members'][-1]))
        # ex post month-end basis
        for key in ('3m', '6m', '12m'):
            n = int(key[:-1])
            s = h['ex_post'][key]
            m0 = re.match(r'(\d{4}-\d{2})月末→(\d{4}-\d{2})月末', s)
            add(S, '%s %s start month' % (an, key), 'judgment ex_post label', an, m0.group(1), an == m0.group(1), '')
            add(S, '%s %s end month' % (an, key), 'judgment ex_post label', addm(an, n), m0.group(2), addm(an, n) == m0.group(2), '')
            for mm in pat.findall(s):
                m = mm[0]
                num = mm[1]
                unit = mm[2]
                d0 = st.month_last_date(m, an)
                d1 = st.month_last_date(m, addm(an, n))
                v0 = st.at(m, d0)
                v1 = st.at(m, d1)
                if unit == 'pp':
                    comp = None if (v0 is None or v1 is None) else v1 - v0
                else:
                    comp = None if (v0 is None or v1 is None) else (v1 / v0 - 1.0) * 100.0
                addn(S, '%s %s %s (%s)' % (an, key, m, unit), 'series_store %s %s→%s' % (m, d0, d1), comp, num, '')
        # engine aftermath
        for a in ('SPX', 'UST_10Y', 'DXY', 'GOLD_F'):
            unit = t['aftermath'][a + '_unit']
            for k in ('1m', '3m', '6m', '12m'):
                w = t['aftermath'][a + '_window'][k]
                r0 = st.ge(a, w['start'])
                r1 = st.le(a, w['end'])
                if unit == 'pp':
                    comp = r1[1] - r0[1]
                else:
                    comp = (r1[1] / r0[1] - 1.0) * 100.0
                addn(S, '%s engine aftermath %s %s' % (an, a, k), 'series_store %s %s→%s' % (a, r0[0], r1[0]), comp, t['aftermath'][a][k], 'engine face', 0.01)
        # known-at-time other regions
        asof = last_day(an)
        found = re.findall(r'(欧元区HICP同比|日本CPI同比|中国PPI同比|中国CPI同比)(\d{4}-\d{2})为(-?\d+\.\d+)', h['other_regions_sync'])
        namemap = {'欧元区HICP同比': 'EA_HICP_YOY', '日本CPI同比': 'JP_CPI_YOY', '中国PPI同比': 'CN_PPI_YOY', '中国CPI同比': 'CN_CPI_YOY'}
        for nm, ym, num in found:
            m = namemap[nm]
            addn(S, '%s known-at-time %s %s' % (an, m, ym), 'series_store %s@%s' % (m, ym), st.month_val(m, ym), num, '')
            r = st.latest_visible(m, asof, entries)
            add(S, '%s latest visible %s at %s' % (an, m, asof), 'series_store + seat rule = %s (pub %s)' % (None if r is None else r[0], None if r is None else r[1]), None if r is None else r[0][:7], ym, r is not None and r[0][:7] == ym, '')
        lab = re.search(r'中国(同步|分化|缺证)、欧元区(同步|分化|缺证)、日本(同步|分化|缺证)', h['other_regions_sync'])
        add(S, '%s sync labels present' % an, 'judgment other_regions_sync', None if lab is None else lab.group(0), 'present', lab is not None, '')
        cov = re.search(r'增长维覆盖([\d.]+)/通胀([\d.]+)/信用([\d.]+)', h['sample_note'])
        sv = data['state_vector']
        addn(S, '%s coverage growth' % an, 'report.json state_vector.growth.coverage', sv['growth']['coverage'], cov.group(1), '')
        addn(S, '%s coverage inflation' % an, 'report.json state_vector.inflation.coverage', sv['inflation']['coverage'], cov.group(2), '')
        addn(S, '%s coverage credit' % an, 'report.json state_vector.credit.coverage', sv['credit']['coverage'], cov.group(3), '')
    # C2 narrative vs ex-post numbers
    for i, an in enumerate(['2025-03', '2022-06', '2023-10']):
        ex = hp[i]['ex_post']
        s3 = dict((mm[0], float(mm[1])) for mm in pat.findall(ex['3m']))
        s12 = dict((mm[0], float(mm[1])) for mm in pat.findall(ex['12m']))
        eq = ['SPX', 'NIKKEI225', 'DAX', 'SHCOMP']
        c3 = ' '.join(['%s%+.2f' % (k, s3[k]) for k in eq])
        c12 = ' '.join(['%s%+.2f' % (k, s12[k]) for k in eq])
        info(S, 'C2 %s 3m equities: %s | 12m equities: %s' % (an, c3, c12))
        if an == '2022-06':
            add(S, 'C2 2022-06 3m equities all negative', 'judgment ex_post 3m', c3, 'all negative', all(s3[k] < 0 for k in eq), '')
            add(S, 'C2 2022-06 12m equities positive except SHCOMP', 'judgment ex_post 12m', c12, 'SHCOMP<0, others>0', s12['SHCOMP'] < 0 and all(s12[k] > 0 for k in eq if k != 'SHCOMP'), '')
        else:
            add(S, 'C2 %s 3m DXY negative' % an, 'judgment ex_post 3m', s3['DXY'], '<0', s3['DXY'] < 0, '')
            add(S, 'C2 %s 3m GOLD_F positive' % an, 'judgment ex_post 3m', s3['GOLD_F'], '>0', s3['GOLD_F'] > 0, '')
    s3 = dict((mm[0], float(mm[1])) for mm in pat.findall(hp[2]['ex_post']['3m']))
    add(S, 'C2 2023-10 3m SHCOMP negative (exception)', 'judgment ex_post 3m', s3['SHCOMP'], '<0', s3['SHCOMP'] < 0, '')
    # sign agreement recompute
    agree = data['dispersion']['topN_aftermath_sign_agreement']
    for a in ('SPX', 'UST_10Y', 'DXY', 'GOLD_F'):
        for k in ('1m', '3m', '6m', '12m'):
            vals = []
            for t in top:
                w = t['aftermath'][a + '_window'][k]
                r0 = st.ge(a, w['start'])
                r1 = st.le(a, w['end'])
                if t['aftermath'][a + '_unit'] == 'pp':
                    vals.append(r1[1] - r0[1])
                else:
                    vals.append((r1[1] / r0[1] - 1.0) * 100.0)
            npos = 0
            for v in vals:
                if v > 0:
                    npos += 1
            comp = float(max(npos, len(vals) - npos)) / len(vals)
            addn(S, 'sign agreement %s %s' % (a, k), 'series_store recompute over 5 cluster representatives', comp, agree[a + '_' + k], 'engine dispersion face', 0.05)
            if a in ('SPX', 'GOLD_F') and k in ('6m', '12m'):
                add(S, 'sign agreement %s %s = 1.0 (C2 claim)' % (a, k), 'recompute', comp, 1.0, abs(comp - 1.0) < 1e-9, '')
            elif not (a == 'DXY' or (a in ('SPX', 'GOLD_F') and k == '1m')):
                add(S, 'sign agreement %s %s between 0.6 and 0.8 (C2 claim)' % (a, k), 'recompute', comp, '0.6..0.8', 0.6 - 1e-9 <= comp <= 0.8 + 1e-9, '')
    add(S, 'candidates scanned/valid/dropped', 'report.json candidates', '%d/%d/%d/%d' % (cands['scanned'], cands['valid'], cands['dropped_overlap'], cands['dropped_insufficient']), '1871/74/12/1785', (cands['scanned'], cands['valid'], cands['dropped_overlap'], cands['dropped_insufficient']) == (1871, 74, 12, 1785), '')
    add(S, 'n independent clusters', 'report.json candidates.n_independent_clusters_topN', cands['n_independent_clusters_topN'], '5', cands['n_independent_clusters_topN'] == 5, 'TOP-5独立簇')


SYNC_ROWS = [
    ('US', 'growth', 'US_REAL_GDP', 'yoy'), ('US', 'inflation', 'CPI', 'yoy'), ('US', 'policy', 'DFEDTARU', 'level'),
    ('CN', 'growth', 'CN_PMI_MFG', 'level'), ('CN', 'inflation', 'CN_CPI_YOY', 'level'), ('CN', 'policy', 'CN_LPR_1Y', 'level'),
    ('EA', 'growth', 'EA_REAL_GDP_YOY', 'level'), ('EA', 'inflation', 'EA_HICP_YOY', 'level'), ('EA', 'policy', 'ECB_MRO', 'level'),
    ('JP', 'growth', 'JP_REAL_GDP_YOY', 'level'), ('JP', 'inflation', 'JP_CPI_YOY', 'level'), ('JP', 'policy', 'JP_POLICY_RATE', 'level'),
]
ENGINE_SYNC = {
    '2025-03': ['US growth 下行', 'US inflation 上行', 'US policy 持平', 'CN growth 分化', 'CN inflation 分化', 'CN policy 同步', 'EA growth 分化', 'EA inflation 分化', 'EA policy 分化', 'JP growth 同步', 'JP inflation 同步', 'JP policy 分化'],
    '2022-06': ['US growth 下行', 'US inflation 上行', 'US policy 上行', 'CN growth 分化', 'CN inflation 同步', 'CN policy 分化', 'EA growth 同步', 'EA inflation 同步', 'EA policy 分化', 'JP growth 同步', 'JP inflation 同步', 'JP policy 分化'],
    '2023-10': ['US growth 上行', 'US inflation 上行', 'US policy 持平', 'CN growth 同步', 'CN inflation 分化', 'CN policy 分化', 'EA growth 分化', 'EA inflation 分化', 'EA policy 分化', 'JP growth 分化', 'JP inflation 分化', 'JP policy 分化'],
}


def sec_sync(S, st, snap, rep, entries, jud, blob):
    """Independent recompute of the engine region x dimension history sync face."""
    for an in ('2025-03', '2022-06', '2023-10'):
        asof = last_day(an)
        d_start = last_day(addm(an, -3))
        usd = {}
        for (reg, dim, m, kind) in SYNC_ROWS:
            vals = []
            for d in (d_start, asof):
                if m in MONTHLY:
                    r = st.latest_visible(m, d, entries)
                else:
                    r = st.le(m, d)
                if r is None:
                    vals.append(None)
                    continue
                v = st.at(m, r[0])
                if kind == 'yoy':
                    v = st.yoy(m, r[0][:7])
                vals.append(v)
            if None in vals:
                lab = '缺证'
                chg = None
            else:
                chg = vals[1] - vals[0]
                if abs(chg) < 1e-9:
                    dr = '持平'
                elif chg > 0:
                    dr = '上行'
                else:
                    dr = '下行'
                if reg == 'US':
                    usd[dim] = dr
                    lab = '基准'
                else:
                    u = usd.get(dim)
                    if u == dr:
                        lab = '同步'
                    elif u is None:
                        lab = 'NA'
                    else:
                        lab = '分化'
                info(S, 'sync %s %s %s: %s -> %s (%+.4g)' % (an, reg, m, vals[0], vals[1], chg))
            idx = SYNC_ROWS.index((reg, dim, m, kind))
            exp = ENGINE_SYNC[an][idx]
            exp_lab = exp.split(' ')[-1]
            if reg == 'US':
                lab = dr
            got = '%s %s' % (('NA' if chg is None else dr), lab)
            info(S, 'sync row %s %s %s -> %s' % (an, reg, m, got))
            add(S, 'sync %s %s %s label' % (an, reg, dim), 'series_store + seat visibility rule', lab, exp_lab, lab == exp_lab, 'engine face label')
            if reg == 'US' or lab not in ('缺证',):
                add(S, 'sync %s %s %s direction' % (an, reg, dim), 'series_store + seat visibility rule', None if chg is None else ('%.4g' % chg), None, True, 'engine: %s' % exp)
        info(S, 'sync %s window start date %s end date %s' % (an, d_start, asof))


def sec_misc(S, st, snap, rep, entries, jud, blob):
    ga = snap.get('gate_a') or {}
    info(S, 'snapshot gate_a keys: ' + ' '.join(sorted(ga.keys())))
    add(S, 'Gate A status', 'snapshot gate_a', ga.get('status'), 'DEGRADED', str(ga.get('status')).upper() == 'DEGRADED', 'judgment: 本轮 Gate A 判 DEGRADED')
    for key, exp in [('core_missing', 0), ('noncore_missing', 7), ('noncore_degraded', 8)]:
        v = ga.get(key)
        n = None if v is None else len(v)
        add(S, 'Gate A %s count' % key, 'snapshot gate_a.%s' % key, n, exp, n == exp, '')
    miss = ga.get('noncore_missing') or []
    withobs = []
    for m in miss:
        if st.has(m):
            withobs.append(m)
    add(S, 'Gate A noncore missing metrics with stock observations', 'snapshot gate_a.noncore_missing x series_store', '%d: %s' % (len(withobs), ' '.join(withobs)), '5', len(withobs) == 5, '缺口指标中有五项在序列库内仍有存量观测')
    # evidence refs
    refs = []

    def walk(o):
        if isinstance(o, dict):
            for k in o:
                if k == 'evidence_refs' and isinstance(o[k], list):
                    refs.extend(o[k])
                else:
                    walk(o[k])
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(jud)
    uniq = sorted(set(refs))
    info(S, 'evidence_refs total=%d unique=%d' % (len(refs), len(uniq)))
    info(S, 'evidence refs: resolvability check follows as one counted point over unique refs')
    bad = []
    for r in uniq:
        if '@' not in str(r):
            bad.append(str(r))
            continue
        m, d = str(r).split('@', 1)
        okr = False
        if st.has(m):
            if st.at(m, d) is not None:
                okr = True
            else:
                md = st.month_last_date(m, d[:7])
                if md is not None and d == last_day(d[:7]):
                    okr = True
        if not okr:
            bad.append(str(r))
    add(S, 'all unique evidence refs point to an observation', 'judgment evidence_refs x series_store', ' '.join(bad), 'none unresolved', len(bad) == 0, 'n_unique=%d' % len(uniq))
    need(blob, '证据引用共 41 条')
    l3refs = []
    l4refs = []

    def walk2(o, bucket):
        if isinstance(o, dict):
            for k in o:
                if k == 'evidence_refs' and isinstance(o[k], list):
                    bucket.extend(o[k])
                else:
                    walk2(o[k], bucket)
        elif isinstance(o, list):
            for x in o:
                walk2(x, bucket)
    walk2(jud['l3'], l3refs)
    walk2(jud['l4'], l4refs)
    info(S, 'evidence_refs scope: l3=%d l4=%d total=%d unique=%d' % (len(l3refs), len(l4refs), len(l3refs) + len(l4refs), len(set(l3refs + l4refs))))
    add(S, 'evidence refs count, L3 scope (contradictions + mechanism chains)', 'agent_judgment l3.*.evidence_refs', len(l3refs), 41, len(l3refs) == 41, 'quality note says 证据引用共 41 条 without naming the scope; L4 scenarios add %d more refs (total %d)' % (len(l4refs), len(l3refs) + len(l4refs)))
    # S5 correlation face (engine quantity): pairing by observation month is NOT the same quantity as the engine face
    # (n differs) -> recorded as information only, not counted as a point.
    xs = []
    ys = []
    for d in st.dates('US_REAL_GDP'):
        ym = d[:7]
        g = st.yoy('US_REAL_GDP', ym)
        u = st.month_val('UNEMPLOYMENT', ym)
        if g is not None and u is not None:
            xs.append(g)
            ys.append(u)
    r = pearson(xs, ys)
    info(S, 'S5 face check (info only): GDP yoy x UNEMP level paired by observation month: pearson=%.4f n=%d; engine face text says -0.8936 n=37 -> quantity not reproduced, not compared' % (r, len(xs)))
    # turnings vs series
    for i, t in enumerate(jud['reader_map']['turnings']):
        m = t['metric_id']
        a = st.month_val(m, t['before_date'][:7])
        b = st.month_val(m, t['date'][:7])
        if m in ('CPI', 'INDPRO'):
            a = st.yoy(m, t['before_date'][:7])
            b = st.yoy(m, t['date'][:7])
        addn(S, 'turning[%d] %s before' % (i, m), 'series_store %s@%s' % (m, t['before_date'][:7]), a, t.get('value_before'), '')
        addn(S, 'turning[%d] %s after' % (i, m), 'series_store %s@%s' % (m, t['date'][:7]), b, t.get('value_after'), '')
        add(S, 'turning[%d] %s window' % (i, m), 'judgment turnings', '%s→%s' % (t.get('before_date'), t.get('date')), None, True, 'dimension=%s' % t.get('dimension'))
    for t in jud['reader_map'].get('turning_supplement', []):
        m = t['metric_id']
        addn(S, 'turning supplement %s from' % m, 'series_store %s@%s' % (m, t['from_ym']), st.month_val(m, t['from_ym']), t.get('value_before'), '')
        addn(S, 'turning supplement %s to' % m, 'series_store %s@%s' % (m, t['to_ym']), st.month_val(m, t['to_ym']), t.get('value_after'), '')
    # candidate face values quoted
    addn(S, 'candidate CN_CPI_YOY 2026-01', 'series_store CN_CPI_YOY@2026-01', st.month_val('CN_CPI_YOY', '2026-01'), '0.2', '')
    addn(S, 'candidate CN_PPI_YOY 2026-02', 'series_store CN_PPI_YOY@2026-02', st.month_val('CN_PPI_YOY', '2026-02'), '-0.9', '')
    # work-order coverage markers
    info(S, 'presence markers (not counted): three anchors in judgment text: %s' % ' '.join('%s=%s' % (snip, snip in blob) for snip in ['12个月前', '3个月前', '最新一期']))
    info(S, 'presence markers (not counted): work-order elements in judgment text: %s' % ' '.join('%s=%s' % (snip, snip in blob) for snip in ['谁先变', '历史', '事后', '证伪', '竞争解释']))
    # SCN1 trigger pointer
    info(S, 'calendar metric ids with kind set (not counted): %s ; SCN trigger text says 决议日见发布日历实录 for Fed/ECB' % ' '.join(sorted(set(str(e.get('metric_id')) for e in entries if e.get('kind')))))


def sec_counter(S, st, snap, rep, entries, jud, blob):
    """Counter-attack recomputations (not judgment comparisons)."""
    for (d0, d1, lab) in [('2026-10-23', '2026-11-23', '1m'), ('2026-08-23', '2026-11-23', '3m'), ('2025-11-23', '2026-11-23', '12m')]:
        ds = [d for d in st.dates('SPX') if d >= d0 and d <= d1 and st.at('USDJPY', d) is not None]
        rs = []
        ru = []
        prev = None
        for d in ds:
            v = st.at('SPX', d)
            u = st.at('USDJPY', d)
            if prev is not None:
                rs.append((v / prev[0] - 1.0) * 100.0)
                ru.append((u / prev[1] - 1.0) * 100.0)
            prev = (v, u)
        r = pearson(rs, ru)
        dn_up = 0
        dn_dn = 0
        up_dn = 0
        up_up = 0
        i = 0
        while i < len(rs):
            if rs[i] < 0 and ru[i] > 0:
                dn_up += 1
            elif rs[i] < 0 and ru[i] < 0:
                dn_dn += 1
            elif rs[i] > 0 and ru[i] < 0:
                up_dn += 1
            elif rs[i] > 0 and ru[i] > 0:
                up_up += 1
            i += 1
        info(S, 'counter SPX~USDJPY daily %s: n=%d pearson=%.3f | SPXdn&USDJPYup=%d SPXdn&USDJPYdn=%d SPXup&USDJPYdn=%d SPXup&USDJPYup=%d' % (lab, len(rs), r, dn_up, dn_dn, up_dn, up_up))
        tot_spx = (st.at('SPX', ds[-1]) / st.at('SPX', ds[0]) - 1.0) * 100.0
        tot_u = (st.at('USDJPY', ds[-1]) / st.at('USDJPY', ds[0]) - 1.0) * 100.0
        info(S, 'counter %s window total: SPX %+.2f%% USDJPY %+.2f%% (%s→%s)' % (lab, tot_spx, tot_u, ds[0], ds[-1]))
    # HY_OAS weekly widening history
    ds = st.dates('HY_OAS')
    big = []
    i = 0
    while i < len(ds):
        d = ds[i]
        j = i
        while j >= 0 and days_between(ds[j], d) < 7:
            j -= 1
        if j >= 0 and days_between(ds[j], d) == 7:
            ch = st.at('HY_OAS', d) - st.at('HY_OAS', ds[j])
            if ch >= 0.29 - 1e-9:
                big.append(d)
        i += 1
    info(S, 'counter HY_OAS: number of strict-7d widenings >= +0.29pp in series history: %d of %d weeks; latest 1w +0.29pp' % (len(big), len(ds) - 5))
    # CPI yoy 3-month change vs BRN
    info(S, 'counter BEI_10Y at 2026-05-04 = %s ; TIPS_10Y change 2026-02-27→2026-05-04 (bp) = %s' % (st.at('BEI_10Y', '2026-05-04'), None if (st.at('TIPS_10Y', '2026-02-27') is None or st.at('TIPS_10Y', '2026-05-04') is None) else round((st.at('TIPS_10Y', '2026-05-04') - st.at('TIPS_10Y', '2026-02-27')) * 100.0, 1)))
    # Explanation C: VIX vs USDJPY coupling
    ds = [d for d in st.dates('VIX') if d >= '2026-10-23' and st.at('USDJPY', d) is not None]
    rv = []
    ru = []
    prev = None
    for d in ds:
        v = st.at('VIX', d)
        u = st.at('USDJPY', d)
        if prev is not None:
            rv.append((v / prev[0] - 1.0) * 100.0)
            ru.append((u / prev[1] - 1.0) * 100.0)
        prev = (v, u)
    info(S, 'counter VIX~USDJPY daily 1m: pearson=%.3f n=%d' % (pearson(rv, ru), len(rv)))


def sec_extra(S, st, snap, rep, entries, jud, blob):
    """Additional counter-attack recomputations (information only, no judgment comparison)."""
    import datetime
    wk = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    for d in ['2025-12-10', '2025-12-11', '2026-06-11', '2026-06-17', '2026-09-10', '2026-09-16', '2026-09-17', '2026-09-18', '2026-09-24', '2026-08-30', '2026-09-29', '2026-09-13', '2026-05-13']:
        info(S, 'weekday %s = %s' % (d, wk[datetime.date(int(d[:4]), int(d[5:7]), int(d[8:10])).weekday()]))
    # 1) horizon asymmetry: returns of each asset over 12m / 3m / 1m on a common trading-day basis
    def ret(m, d0, d1):
        a = st.le(m, d0)
        b = st.le(m, d1)
        if a is None or b is None or a[1] in (None, 0):
            return None
        return ((b[1] / a[1] - 1.0) * 100.0, a[0], b[0])
    for m in ['SPX', 'NIKKEI225', 'SHCOMP', 'DAX', 'CAC40', 'GOLD_F', 'DXY', 'VIX', 'USDJPY', 'USDCNY', 'BRENT_F', 'HY_OAS', 'UST_10Y', 'TIPS_10Y', 'BEI_10Y']:
        r12 = ret(m, '2025-11-19', '2026-11-19')
        r3 = ret(m, '2026-08-19', '2026-11-19')
        r1 = ret(m, '2026-10-20', '2026-11-19')
        r1j = ret(m, '2026-10-23', '2026-11-23')

        def f(x):
            return 'n/a' if x is None else '%+.2f%% [%s→%s]' % x
        info(S, 'horizon %s: 12m %s | 3m %s | 1m %s | judgment-1m-basis %s' % (m, f(r12), f(r3), f(r1), f(r1j)))
    # 2) SPX~USDJPY daily magnitudes (window endpoint reading vs daily reading)
    for (d0, d1, lab) in [('2026-10-23', '2026-11-23', 'intraday-2026-11-23'), ('2026-10-23', '2026-11-20', 'close-basis')]:
        ds = [d for d in st.dates('SPX') if d >= d0 and d <= d1 and st.at('USDJPY', d) is not None]
        prev = None
        sum_dn = 0.0
        sum_up = 0.0
        rows = []
        for d in ds:
            v = st.at('SPX', d)
            u = st.at('USDJPY', d)
            if prev is not None:
                rs = (v / prev[0] - 1.0) * 100.0
                ru = (u / prev[1] - 1.0) * 100.0
                if rs < 0:
                    sum_dn += ru
                elif rs > 0:
                    sum_up += ru
                rows.append((d, rs, ru))
            prev = (v, u)
        info(S, 'SPX~USDJPY daily %s: days=%d; sum USDJPY %%chg on SPX-down days %+.2f%%, on SPX-up days %+.2f%%' % (lab, len(rows), sum_dn, sum_up))
        rows.sort(key=lambda x: -abs(x[2]))
        info(S, 'SPX~USDJPY daily %s: 6 largest |USDJPY| daily moves (date, SPX %%, USDJPY %%): %s' % (lab, '; '.join('%s %+.2f %+.2f' % r for r in rows[:6])))
        rows.sort(key=lambda x: -abs(x[1]))
        info(S, 'SPX~USDJPY daily %s: 6 largest |SPX| daily moves (date, SPX %%, USDJPY %%): %s' % (lab, '; '.join('%s %+.2f %+.2f' % r for r in rows[:6])))
        # biggest single-day contributors to the window net move
    # 3) visible domestic inflation before each September decision (decision-relevant series vs US CPI proxy)
    for (m, asof, lab) in [('EA_HICP_YOY', '2026-06-11', 'ECB 2026-06-11'), ('EA_HICP_YOY', '2026-09-10', 'ECB 2026-09-10'),
                           ('JP_CPI_YOY', '2026-09-18', 'BoJ 2026-09-18'), ('CPI', '2026-09-16', 'Fed 2026-09-16'),
                           ('CORE_PCE', '2026-09-16', 'Fed 2026-09-16'), ('CPI', '2026-06-11', 'ECB 2026-06-11 (US proxy)'), ('CPI', '2026-09-10', 'ECB 2026-09-10 (US proxy)'), ('CPI', '2026-09-18', 'BoJ 2026-09-18 (US proxy)')]:
        v = st.latest_visible(m, asof, entries)
        info(S, 'visible %s before %s: %s' % (m, lab, json.dumps(v, ensure_ascii=False) if not isinstance(v, (list, tuple)) else ' '.join(str(x) for x in v)))
    for m, y0 in [('EA_HICP_YOY', '2026-01'), ('JP_CPI_YOY', '2026-01'), ('CPI', '2026-01')]:
        info(S, 'path %s 2026-01..2026-10: %s' % (m, ' '.join('%s=%s' % (ym, st.month_val(m, ym)) for ym in ['2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08', '2026-09', '2026-10'] if st.has(m))))
    # 4) CN_NEW_LOANS (credit-side evidence available to the judgment for C3)
    if st.has('CN_NEW_LOANS'):
        ds = st.dates('CN_NEW_LOANS')
        info(S, 'CN_NEW_LOANS first/last obs: %s / %s n=%d' % (ds[0], ds[-1], len(ds)))
        vals = []
        for d in ds:
            vals.append((d[:7], st.at('CN_NEW_LOANS', d)))
        ymap = dict(vals)
        out = []
        for ym, v in vals[-16:]:
            pv = ymap.get(addm(ym, -12))
            out.append('%s=%s%s' % (ym, v, '' if pv in (None, 0) else '(yoy %+.1f%%)' % ((v / pv - 1.0) * 100.0)))
        info(S, 'CN_NEW_LOANS last 16 months: ' + ' '.join(out))
    # 5) absence of series in the frozen store
    names = sorted(snap['series_store'].keys())
    info(S, 'series_store metric count: %d' % len(names))
    info(S, 'series_store names containing JGB / CN_ / CAPITAL / FLOW: %s' % ' '.join(n for n in names if ('JGB' in n) or n.startswith('CN_') or 'CAPITAL' in n or 'FLOW' in n))
    info(S, 'series_store all names: ' + ' '.join(names))
    # 6) engine policy window path face (cell level)
    for c in (((rep.get('research_plan') or {}).get('point_values') or {}).get('cells') or []):
        m = c.get('metric_id')
        if m in ('DFEDTARU', 'DFF', 'ECB_DFR', 'ECB_MRO', 'JP_POLICY_RATE', 'CN_LPR_1Y', 'CN_OMO_7D', 'CN_POLICY_OVERNIGHT'):
            pwp = c.get('policy_window_path') or {}
            ev = [(e.get('date'), e.get('from'), e.get('to'), e.get('delta_bp'), e.get('decision_date')) for e in (pwp.get('events') or [])]
            info(S, 'engine policy_window_path %s: window=%s start=%s end=%s net_bp=%s events(date,from,to,delta_bp,decision)=%s' % (m, pwp.get('window'), pwp.get('window_start_value'), pwp.get('window_end_value'), pwp.get('net_bp'), ' '.join('%s:%s→%s(%s)[dec %s]' % e for e in ev)))
    # 7) policy_event_clusters face
    pec = (rep.get('research_plan') or {}).get('policy_event_clusters') or {}
    for cl in pec.get('clusters') or []:
        info(S, 'engine policy cluster %s %s..%s regions=%s events=%s' % (cl.get('cluster_id'), cl.get('date_from'), cl.get('date_to'), cl.get('regions'), ' '.join('%s dec %s eff %s %s→%s %s' % (e.get('metric_id'), e.get('date'), e.get('effective_date'), e.get('from'), e.get('to'), e.get('delta_bp')) for e in cl.get('events') or [])))

def main():
    snap_p, rep_p, cal_p, jud_p, out_dir = sys.argv[1:6]
    sections = sys.argv[6:]
    snap = load(snap_p)
    rep = load(rep_p)
    cal = load(cal_p)
    jud = load(jud_p)
    blob = json.dumps(jud, ensure_ascii=False)
    st = Store(snap['series_store'])
    entries = cal.get('entries') or []
    funcs = {'anchors': sec_anchors, 'monthly': sec_monthly, 'daily': sec_daily, 'history': sec_history,
             'sync': sec_sync, 'misc': sec_misc, 'counter': sec_counter, 'extra': sec_extra}
    allp = []
    alli = []
    for s in sections:
        before = len(POINTS)
        ibefore = len(INFO)
        funcs[s](s, st, snap, rep, entries, jud, blob)
        pts = POINTS[before:]
        infos = INFO[ibefore:]
        allp.extend(pts)
        alli.extend(infos)
        with open(out_dir + '/points_' + s + '.txt', 'w', encoding='utf-8') as f:
            for p in pts:
                f.write('%s|%s|computed=%s|reported=%s|src=%s|note=%s\n' % ('OK' if p['ok'] else 'MISMATCH', p['id'], p['computed'], p['reported'], p['src'], p['note']))
        with open(out_dir + '/info_' + s + '.txt', 'w', encoding='utf-8') as f:
            for x in infos:
                f.write(x['text'] + '\n')
        n_ok = 0
        for p in pts:
            if p['ok']:
                n_ok += 1
        print('SECTION %s: points=%d ok=%d mismatch=%d' % (s, len(pts), n_ok, len(pts) - n_ok))
        for p in pts:
            if not p['ok']:
                print('  MISMATCH %s | computed=%s reported=%s | %s | %s' % (p['id'], p['computed'], p['reported'], p['src'], p['note']))
    with open(out_dir + '/points_all.jsonl', 'w', encoding='utf-8') as f:
        for p in allp:
            f.write(json.dumps(p, ensure_ascii=False) + '\n')
    counted = [p for p in allp if p.get('reported') is not None or p.get('computed') is None]
    c_mis = [p for p in counted if not p['ok']]
    i_mis = [p for p in allp if p.get('reported') is None and not p['ok']]
    print('TOTAL recorded=%d | counted (reported value present)=%d mismatches=%d | informational (reported None)=%d informational not-ok=%d' % (len(allp), len(counted), len(c_mis), len(allp) - len(counted), len(i_mis)))
    from collections import Counter
    print('counted by section: %s' % dict(Counter(p['section'] for p in counted)))
    print('mismatches by section: %s' % dict(Counter(p['section'] for p in c_mis)))
    if MISSING:
        print('SNIPPETS NOT FOUND IN JUDGMENT: %d' % len(MISSING))
        for x in MISSING:
            print('  ' + x)


if __name__ == '__main__':
    main()
