# -*- coding: utf-8 -*-
"""席位自写只读复算库(Audit-R32 A round1)。只读冻结快照/日历/引擎面,不写任何运行目录文件。"""
import json
import datetime as dt

CAL_VERSION = None


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


class Face(object):
    def __init__(self, snap, cal=None):
        self.snap = snap
        self.ss = snap['series_store']
        self.facts = {f['fact_id']: f for f in snap.get('facts', [])}
        self.cal = cal
        self.entries = cal['entries'] if cal else []

    # ---------- 基础取数 ----------
    def series(self, name):
        s = self.ss[name]
        return list(zip(s['dates'], s['values']))

    def n(self, name):
        return len(self.ss[name]['dates'])

    def at_or_before(self, name, date):
        """date(含)当日或之前最近一个观测 -> (obs_date, value) 或 None"""
        best = None
        for d, v in self.series(name):
            if d <= date:
                best = (d, v)
            else:
                break
        return best

    def at(self, name, date):
        for d, v in self.series(name):
            if d == date:
                return v
        return None

    def last(self, name):
        s = self.ss[name]
        return (s['dates'][-1], s['values'][-1]) if s['dates'] else None

    def first(self, name):
        s = self.ss[name]
        return (s['dates'][-0 + 0], s['values'][0]) if s['dates'] else None

    def monthly(self, name):
        """月频序列 -> OrderedDict 'YYYY-MM' -> value(以观测日的年月为键)"""
        out = {}
        for d, v in self.series(name):
            out[d[:7]] = v
        return out

    def window(self, name, d0, d1):
        return [(d, v) for d, v in self.series(name) if d0 <= d <= d1]


def add_months(ym, k):
    y, m = int(ym[:4]), int(ym[5:7])
    t = (y * 12 + (m - 1)) + k
    return '%04d-%02d' % (t // 12, t % 12 + 1)


def month_end(ym):
    y, m = int(ym[:4]), int(ym[5:7])
    nxt = dt.date(y + (m == 12), (m % 12) + 1, 1)
    return (nxt - dt.timedelta(days=1)).isoformat()


def days(a, b):
    return (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days


def shift_days(d, k):
    return (dt.date.fromisoformat(d) + dt.timedelta(days=k)).isoformat()


def weekday(d):
    return dt.date.fromisoformat(d).isoweekday()  # 1=Mon .. 7=Sun


def pct(a, b):
    """(b/a-1)*100"""
    return (b / a - 1.0) * 100.0


def r(x, k=2):
    return round(x + 0.0, k)


def yoy_level(face, name, ym):
    """水平序列严格同月去年比(%) -> (yoy, base_ym, base_value, value) 或 (None, reason...)"""
    mm = face.monthly(name)
    if ym not in mm:
        return (None, 'obs_missing', ym, None)
    base = add_months(ym, -12)
    if base not in mm:
        return (None, 'no_same_period_base', base, mm[ym])
    return (pct(mm[base], mm[ym]), base, mm[base], mm[ym])


def qyoy_level(face, name, yq):
    """季度水平序列严格同季去年比; yq 如 '2026Q3' -> obs date '2026-07-01'"""
    y, q = int(yq[:4]), int(yq[5])
    obs = '%04d-%02d-01' % (y, (q - 1) * 3 + 1)
    bobs = '%04d-%02d-01' % (y - 1, (q - 1) * 3 + 1)
    v = face.at(name, obs)
    b = face.at(name, bobs)
    if v is None:
        return (None, 'obs_missing', obs, None)
    if b is None:
        return (None, 'no_same_period_base', bobs, v)
    return (pct(b, v), bobs, b, v)


# ---------- 发布日规则(与引擎 RELEASE_RULES 推定同式;日历条目优先) ----------
RULE_LAG = {
    'CPI': 13, 'CORE_CPI': 13, 'CORE_PCE': 30, 'INDPRO': 15, 'UNEMPLOYMENT': 5,
    'EA_HICP_YOY': 16, 'JP_CPI_YOY': 20, 'JP_POLICY_RATE': 5, 'CN_PMI_MFG': -1,
    'CN_CPI_YOY': 9, 'CN_PPI_YOY': 9, 'JP_CPI_TOKYO_YOY': -1,
}


def release_date(face, metric, obs_date):
    """返回 (date, basis)。日历条目优先(含 metric_ids 列表形式)。"""
    for e in face.entries:
        mids = e.get('metric_ids') or [e.get('metric_id')]
        if metric in mids and e.get('obs_from') and e.get('obs_to'):
            if e['obs_from'] <= obs_date <= e['obs_to']:
                fp = e.get('first_publish_on_or_after') or e.get('decision_date')
                if fp:
                    return (fp, 'calendar:' + e['entry_id'])
    freq_q = metric in ('US_REAL_GDP', 'EA_REAL_GDP_YOY', 'JP_REAL_GDP_YOY')
    if freq_q:
        y, m = int(obs_date[:4]), int(obs_date[5:7])
        qend_m = ((m - 1) // 3 + 1) * 3
        qend = month_end('%04d-%02d' % (y, qend_m))
        lag = {'US_REAL_GDP': 29, 'EA_REAL_GDP_YOY': 35, 'JP_REAL_GDP_YOY': 45}[metric]
        return (shift_days(qend, lag), 'rule:BEA/Eurostat/CabinetOffice')
    if metric == 'CN_LPR_1Y':
        return (obs_date, 'rule:obs=publish day(20日)')
    if metric == 'DFF':
        # 注册表 field_semantics.release_date_available: DFF 次日
        return (shift_days(obs_date, 1), 'rule:DFF次日(注册表)')
    if metric in RULE_LAG:
        return (shift_days(month_end(obs_date[:7]), RULE_LAG[metric]), 'rule')
    return (obs_date, 'obs=publish(市场/日频序列)')


def visible_latest(face, metric, asof):
    """发布纪律: 观测日<=asof 且 发布日<=as_of 的最新观测 -> dict"""
    out = None
    for d, v in face.series(metric):
        if d > asof:
            break
        pub, basis = release_date(face, metric, d)
        if pub <= asof:
            out = {'obs_date': d, 'value': v, 'pub_date': pub, 'basis': basis}
    return out
