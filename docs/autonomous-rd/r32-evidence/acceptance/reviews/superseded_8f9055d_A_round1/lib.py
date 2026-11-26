#!/usr/bin/python3 -I
"""Seat-owned read-only helper library (imported by seat scripts via explicit sys.path insert
of the seat dir only).  No writes outside /tmp/r32-accept/review5/A_round1."""
import datetime as dt
import json
import math

SEAT_DIR = "/tmp/r32-accept/review5/A_round1"


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


class Store(object):
    def __init__(self, snap):
        self.snap = snap
        self.ss = snap["series_store"]

    def has(self, mid):
        return mid in self.ss

    def series(self, mid):
        e = self.ss[mid]
        return list(zip(e["dates"], e["values"]))

    def first_date(self, mid):
        s = self.series(mid)
        return s[0][0] if s else None

    def last_date(self, mid):
        s = self.series(mid)
        return s[-1][0] if s else None

    def at(self, mid, date):
        """exact observation on date -> value or None"""
        for d, v in self.series(mid):
            if d == date:
                return v
        return None

    def on_or_before(self, mid, date):
        """latest observation with obs date <= date -> (date,value) or None"""
        out = None
        for d, v in self.series(mid):
            if d <= date:
                out = (d, v)
            else:
                break
        return out

    def on_or_after(self, mid, date):
        for d, v in self.series(mid):
            if d >= date:
                return (d, v)
        return None

    def in_range(self, mid, d0, d1):
        return [(d, v) for d, v in self.series(mid) if d0 <= d <= d1]

    def month_obs(self, mid, ym):
        """observations whose date starts with ym (YYYY-MM)"""
        return [(d, v) for d, v in self.series(mid) if d[:7] == ym]

    def month_last(self, mid, ym):
        m = self.month_obs(mid, ym)
        return m[-1] if m else None

    def changes(self, mid, d0, d1):
        """change points in [d0,d1]: list of (date, from, to)"""
        s = self.series(mid)
        out = []
        for i in range(1, len(s)):
            d, v = s[i]
            if d0 <= d <= d1 and v != s[i - 1][1]:
                out.append((d, s[i - 1][1], v))
        return out


def shift_months(date_str, n):
    """shift YYYY-MM-DD by n months (n may be negative), clamp day to month length"""
    y, m, d = (int(x) for x in date_str.split("-"))
    t = (y * 12 + (m - 1)) + n
    ny, nm = divmod(t, 12)
    nm += 1
    days = [31, 29 if (ny % 4 == 0 and (ny % 100 != 0 or ny % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    nd = min(d, days[nm - 1])
    return "%04d-%02d-%02d" % (ny, nm, nd)


def pct_change(a, b):
    return (b / a - 1.0) * 100.0


def r(x, nd=2):
    return round(x + 0.0, nd)


def ymd(d):
    return dt.date(int(d[:4]), int(d[5:7]), int(d[8:10]))


def days_between(a, b):
    return (ymd(b) - ymd(a)).days


def pct_rank_le(series_vals, x):
    """share of values <= x"""
    n = len(series_vals)
    k = sum(1 for v in series_vals if v <= x)
    return 100.0 * k / n
