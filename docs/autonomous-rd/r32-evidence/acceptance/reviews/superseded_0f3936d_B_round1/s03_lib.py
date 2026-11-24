#!/usr/bin/python3 -I
# Seat script 03: common read-only loader for frozen snapshot / report.json / judgment.
# Imported by later seat scripts (run with -I; this module lives in the seat dir).
import json, os, datetime

def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

def series_map(snap, mid):
    """Return {date_str: value} for series mid from snapshot.series_store (raw)."""
    s = snap["series_store"].get(mid)
    if s is None:
        return None
    keys = list(s.keys())
    if isinstance(s, dict) and "dates" in s and "values" in s:
        return dict(zip(s["dates"], s["values"])), keys
    return None, keys

def series_list(snap, mid):
    s = snap["series_store"].get(mid)
    if s is None:
        return None
    return list(zip(s["dates"], s["values"]))

def last_on_or_before(snap, mid, asof):
    sm = series_list(snap, mid)
    if sm is None:
        return None
    best = None
    for d, v in sm:
        if d <= asof and v is not None:
            best = (d, v)
    return best

def obs_at(snap, mid, date):
    for d, v in series_list(snap, mid):
        if d == date:
            return v
    return None

def shift_months(date_str, n):
    """date_str YYYY-MM-DD; shift by n months (calendar), clamp day."""
    y, m, d = [int(x) for x in date_str.split("-")]
    tot = (y * 12 + (m - 1)) - n
    ny, nm = divmod(tot, 12)
    nm += 1
    days_in = [31, 29 if (ny % 4 == 0 and (ny % 100 != 0 or ny % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    nd = min(d, days_in[nm - 1])
    return "%04d-%02d-%02d" % (ny, nm, nd)

def days_between(a, b):
    da = datetime.date(*[int(x) for x in a.split("-")])
    db = datetime.date(*[int(x) for x in b.split("-")])
    return (db - da).days

def fnum(x, nd=6):
    return float(("%." + str(nd) + "f") % x) if x is not None else None
