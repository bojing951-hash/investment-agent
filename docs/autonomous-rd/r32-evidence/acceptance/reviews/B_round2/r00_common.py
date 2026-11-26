# -*- coding: utf-8 -*-
# r00_common.py — 复算公共助手(只读; 本席自写)
import json, sys, os, datetime as dt, math, calendar


def load(p):
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)


def D(s):
    if isinstance(s, dt.date):
        return s
    return dt.date.fromisoformat(str(s)[:10])


class Snap:
    """只读访问冻结快照 series_store (剔除 null/NaN)。"""

    def __init__(self, sn):
        self.sn = sn
        self.store = sn.get('series_store', {})
        self._c = {}

    def has(self, sid):
        return sid in self.store

    def ids(self):
        return sorted(self.store.keys())

    def series(self, sid):
        if sid not in self._c:
            s = self.store[sid]
            pairs = []
            for a, b in zip(s.get('dates', []), s.get('values', [])):
                if b is None:
                    continue
                try:
                    b = float(b)
                except Exception:
                    continue
                if math.isnan(b) or math.isinf(b):
                    continue
                pairs.append((D(a), b))
            self._c[sid] = pairs
        return self._c[sid]

    def val(self, sid, date):
        date = D(date)
        for a, b in self.series(sid):
            if a == date:
                return b
            if a > date:
                return None
        return None

    def le(self, sid, date):
        date = D(date)
        best = None
        for a, b in self.series(sid):
            if a <= date:
                best = (a, b)
            else:
                break
        return best

    def win(self, sid, d0, d1):
        d0 = D(d0)
        d1 = D(d1)
        return [(a, b) for a, b in self.series(sid) if d0 <= a <= d1]

    def last(self, sid):
        s = self.series(sid)
        return s[-1] if s else None

    def first(self, sid):
        s = self.series(sid)
        return s[0] if s else None

    def key(self, sid, date):
        date = D(date)
        s = self.store[sid]
        ds = s.get('dates', [])
        iso = date.isoformat()
        if iso in ds:
            i = ds.index(iso)
            return 'series_store.%s.values[%d] (dates[%d]=%s)' % (sid, i, i, iso)
        return 'series_store.%s (无 %s 观测)' % (sid, iso)


def pct(a, b):
    if a is None or b is None or a == 0:
        return None
    return (b / a - 1.0) * 100.0


def diff_bp(a, b):
    if a is None or b is None:
        return None
    return (b - a) * 100.0


def minus_year(d):
    d = D(d)
    try:
        return d.replace(year=d.year - 1)
    except ValueError:
        return d.replace(year=d.year - 1, day=28)


def add_months(d, n):
    y = d.year + (d.month - 1 + n) // 12
    m = (d.month - 1 + n) % 12 + 1
    day = min(d.day, calendar.monthrange(y, m)[1])
    return dt.date(y, m, day)


def period_end(d, quarterly=None):
    """月频观测(月初日期)→当月末日; 季频观测(季初日期)→当季末日。
    quarterly: True/False 由调用方按注册表频率指明; None 仅作兜底推断(日期为 1/4/7/10 月 1 日时视为季初)。"""
    d = D(d)
    if d.day != 1:
        return d
    if quarterly is None:
        quarterly = d.month in (1, 4, 7, 10)
    if quarterly:
        e = add_months(d, 3)
        return e - dt.timedelta(days=1)
    return add_months(d, 1) - dt.timedelta(days=1)


def yoy(sn, sid, date):
    date = D(date)
    v = sn.val(sid, date)
    if v is None:
        return None
    base = sn.val(sid, minus_year(date))
    if base is None:
        return None
    return pct(base, v)


def r(x, n):
    if x is None:
        return None
    return float(('%.' + str(n) + 'f') % x)


def decimals(rep):
    if isinstance(rep, bool):
        return 0
    if isinstance(rep, int):
        return 0
    if isinstance(rep, float):
        s = repr(rep)
        if 'e' in s or 'E' in s:
            return 6
        return len(s.split('.')[1]) if '.' in s else 0
    return None


def same(comp, rep, tol=None):
    if comp is None or rep is None:
        return (comp is None and rep is None)
    if isinstance(rep, (int, float)) and not isinstance(rep, bool) and isinstance(comp, (int, float)) and not isinstance(comp, bool):
        if tol is None:
            n = decimals(rep)
            tol = (0.5 * (10 ** (-n)) + 1e-9) if n is not None else 1e-9
        return abs(comp - rep) <= tol
    return str(comp) == str(rep)


def find_keys(obj, name, path='', out=None):
    if out is None:
        out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = path + '.' + k if path else k
            if k == name:
                out.append((p, v))
            find_keys(v, name, p, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            find_keys(v, name, path + '[%d]' % i, out)
    return out


def find_dicts_with_value(obj, val, path='', out=None):
    """递归找出「自身某键的值 == val」的 dict 及其路径。"""
    if out is None:
        out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if v == val:
                out.append((path, obj))
                break
        for k, v in obj.items():
            find_dicts_with_value(v, val, (path + '.' + k) if path else k, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            find_dicts_with_value(v, val, path + '[%d]' % i, out)
    return out


def weekday(d):
    return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][D(d).weekday()]
