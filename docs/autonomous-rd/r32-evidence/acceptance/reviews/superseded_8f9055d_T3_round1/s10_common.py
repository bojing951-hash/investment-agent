#!/usr/bin/python3 -I
"""Shared helpers for the semantic-audit recompute scripts (read-only).

Loaded by s11/s12 from their own directory via importlib (path derived from __file__,
because -I keeps the script directory off sys.path). All functions are pure readers.
"""
import datetime as dt
import hashlib
import json
import re
from decimal import ROUND_HALF_UP, Decimal

WD = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def D(s):
    s = str(s)
    if len(s) == 8 and s.isdigit():
        return dt.date(int(s[0:4]), int(s[4:6]), int(s[6:8]))
    return dt.date(int(s[0:4]), int(s[5:7]), int(s[8:10]))


def add_days(d, n):
    return d + dt.timedelta(days=n)


def month_end(y, m):
    if m == 12:
        return dt.date(y, 12, 31)
    return dt.date(y, m + 1, 1) - dt.timedelta(days=1)


def add_months(d, n):
    y = d.year + (d.month - 1 + n) // 12
    m = (d.month - 1 + n) % 12 + 1
    day = min(d.day, month_end(y, m).day)
    return dt.date(y, m, day)


def prev_weekday(d, wd):
    """Latest date strictly before d whose weekday() == wd."""
    x = d - dt.timedelta(days=1)
    while x.weekday() != wd:
        x -= dt.timedelta(days=1)
    return x


def norm_tz(s):
    """ISO text -> local times in four cities (string HH:MM)."""
    try:
        from zoneinfo import ZoneInfo
        t = dt.datetime.fromisoformat(s)
        out = {}
        for name, tz in (("NewYork", "America/New_York"), ("Berlin", "Europe/Berlin"),
                         ("Tokyo", "Asia/Tokyo"), ("Shanghai", "Asia/Shanghai")):
            out[name] = t.astimezone(ZoneInfo(tz)).strftime("%H:%M")
        out["NewYork_weekday"] = t.astimezone(ZoneInfo("America/New_York")).strftime("%a")
        return out
    except Exception as e:  # pragma: no cover
        return {"error": repr(e)}


def series(ss, mid):
    s = ss[mid]
    return list(s["dates"]), list(s["values"])


def val_at(ss, mid, date):
    ds, vs = series(ss, mid)
    if date in ds:
        return vs[ds.index(date)]
    return None


def last_on_or_before(ss, mid, date):
    ds, vs = series(ss, mid)
    if hasattr(date, "isoformat"):
        date = date.isoformat()
    best = None
    for d, v in zip(ds, vs):
        if d <= date and v is not None:
            best = (d, v)
    return best


def first_obs(ss, mid):
    ds, vs = series(ss, mid)
    return (ds[0], vs[0]) if ds else None


def last_obs(ss, mid):
    ds, vs = series(ss, mid)
    return (ds[-1], vs[-1]) if ds else None


def monthly(ss, mid):
    """'YYYY-MM' -> last non-null observation inside that month."""
    out = {}
    ds, vs = series(ss, mid)
    for d, v in zip(ds, vs):
        if v is not None:
            out[d[:7]] = v
    return out


def mv(ss, mid, ym):
    """Monthly value or None."""
    return monthly(ss, mid).get(ym)


def pct(new, old):
    return (new / old - 1.0) * 100.0


def bp(new, old):
    return (new - old) * 100.0


def decimals(x):
    """Display decimals of the reported number: int -> 0; 2.0 -> 1; 0.727 -> 3."""
    if isinstance(x, bool) or isinstance(x, int):
        return 0
    s = repr(float(x))
    if "e" in s or "E" in s or "." not in s:
        return 0
    return len(s.split(".")[1])


def rnd(x, d):
    q = Decimal(1).scaleb(-d)
    return float(Decimal(repr(float(x))).quantize(q, rounding=ROUND_HALF_UP))


def equal(computed, reported):
    """computed reproduces reported iff computed, rounded (half-up) to the number of
    decimals the report itself uses, equals the reported figure."""
    if computed is None or reported is None:
        return computed is None and reported is None
    if isinstance(computed, bool) or isinstance(reported, bool):
        return computed is reported
    if isinstance(computed, (int, float)) and isinstance(reported, (int, float)):
        if reported != reported or computed != computed:
            return False
        d = decimals(reported)
        return abs(rnd(computed, d) - float(reported)) < 1e-9 * max(1.0, abs(float(reported)))
    return str(computed) == str(reported)


def get(obj, path):
    """Dotted path with [i] indexes."""
    cur = obj
    for name, idx in re.findall(r"([^.\[\]]+)|\[(\*|\d+)\]", path):
        if name:
            cur = cur[name]
        else:
            cur = cur[int(idx)]
    return cur


def walk_strings(o, out):
    if isinstance(o, str):
        out.append(o)
    elif isinstance(o, dict):
        for v in o.values():
            walk_strings(v, out)
    elif isinstance(o, list):
        for v in o:
            walk_strings(v, out)
    return out


def all_text(o):
    return "\n".join(walk_strings(o, []))


def squash(s):
    """Drop whitespace and markdown escapes for verbatim-rendering comparisons."""
    return re.sub(r"\s+", "", s).replace("\\", "")


class Book(object):
    def __init__(self, part):
        self.part = part
        self.rows = []

    def add(self, cid, cat, where, src, computed, reported, ok=None, lit=None, text=None,
            note="", sev=""):
        if ok is None:
            ok = equal(computed, reported)
        found = None
        if lit is not None:
            found = bool(text is not None and lit in text)
            ok = bool(ok and found)
        self.rows.append({"id": cid, "cat": cat, "where": where, "src": src,
                          "computed": computed, "reported": reported,
                          "lit": lit, "lit_found": found, "ok": bool(ok),
                          "note": note, "sev": sev})
        return bool(ok)

    def n_ok(self):
        return sum(1 for r in self.rows if r["ok"])

    def save(self, out_dir):
        path = "%s/recompute_points_%s.json" % (out_dir, self.part)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"part": self.part, "n": len(self.rows), "n_ok": self.n_ok(),
                       "n_mismatch": len(self.rows) - self.n_ok(), "rows": self.rows},
                      f, ensure_ascii=False, indent=1)
        return path


def load_common():
    """Return this module's own namespace (kept for symmetry; scripts import via importlib)."""
    return globals()
