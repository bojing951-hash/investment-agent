#!/usr/bin/env python3
"""Seat library: read-only helpers over the frozen snapshot series_store (independent of engine code).

All functions take a points list [(date_str, value), ...] sorted ascending, built by load().
"""
import json
from datetime import date, timedelta


def load(snapshot_path):
    with open(snapshot_path, "r", encoding="utf-8") as f:
        return json.load(f)


def series(snap, sid):
    s = snap["series_store"].get(sid)
    if s is None:
        return None
    pts = []
    for d, v in zip(s["dates"], s["values"]):
        if v is None or v != v:  # None or NaN
            continue
        pts.append((d, float(v)))
    pts.sort(key=lambda x: x[0])
    return pts


def last_on_or_before(pts, d):
    best = None
    for dd, v in pts:
        if dd <= d:
            best = (dd, v)
        else:
            break
    return best


def first_on_or_after(pts, d):
    for dd, v in pts:
        if dd >= d:
            return (dd, v)
    return None


def exact(pts, d):
    for dd, v in pts:
        if dd == d:
            return v
        if dd > d:
            return None
    return None


def month_last(pts, ym):
    """last observation whose date starts with ym (YYYY-MM)"""
    best = None
    for dd, v in pts:
        if dd.startswith(ym):
            best = (dd, v)
    return best


def month_mean(pts, ym):
    vals = [v for dd, v in pts if dd.startswith(ym)]
    return (sum(vals) / len(vals), len(vals)) if vals else (None, 0)


def month_first(pts, ym):
    for dd, v in pts:
        if dd.startswith(ym):
            return (dd, v)
    return None


def shift_months(d, n):
    y, m, dd = int(d[:4]), int(d[5:7]), int(d[8:10])
    tot = y * 12 + (m - 1) + n
    ny, nm = divmod(tot, 12)
    nm += 1
    # clamp day
    import calendar
    day = min(dd, calendar.monthrange(ny, nm)[1])
    return f"{ny:04d}-{nm:02d}-{day:02d}"


def yoy(pts, d):
    """(v(d)/v(d-12m) - 1)*100 ; returns (yoy or None, base_date, base_value)"""
    v = exact(pts, d)
    bd = shift_months(d, -12)
    b = exact(pts, bd)
    if v is None or b in (None, 0):
        return None, bd, b
    return (v / b - 1.0) * 100.0, bd, b


def pct(a, b):
    return (b / a - 1.0) * 100.0


def changes_in_window(pts, start, end, tol=1e-9):
    """list of (date, prev, new) where value changes vs previous observation, for obs dates in [start,end]"""
    out = []
    prev = None
    for dd, v in pts:
        if dd > end:
            break
        if start <= dd <= end and prev is not None and abs(v - prev[1]) > tol:
            out.append((dd, prev[1], v))
        prev = (dd, v)
    return out


def days_between(a, b):
    da = date.fromisoformat(a)
    db = date.fromisoformat(b)
    return (db - da).days


def common_days(a_pts, b_pts, c_pts, start, end):
    sa = {d for d, _ in a_pts if start <= d <= end}
    sb = {d for d, _ in b_pts if start <= d <= end}
    sc = {d for d, _ in c_pts if start <= d <= end}
    return sorted(sa & sb & sc)


def r(x, n=2):
    if x is None:
        return None
    return round(x + 0.0, n)
