#!/usr/bin/python3 -I
# rc_lib: 本席复算脚本的公共函数(只读; 仅被同目录脚本 import)
import json, os, datetime as dt

SNAP = "snapshot.series_store"
CUT = "2026-11-23"
ANC = "2026-08-23"


def load(snap_p, rep_p, cal_p, reg_p, aj_p):
    snap = json.load(open(snap_p, encoding="utf-8"))
    rep = json.load(open(rep_p, encoding="utf-8"))
    cal = json.load(open(cal_p, encoding="utf-8"))
    reg = json.load(open(reg_p, encoding="utf-8"))
    aj = json.load(open(aj_p, encoding="utf-8"))
    return snap, rep, cal, reg, aj


class Points:
    def __init__(self):
        self.pts = []

    def add(self, pid, face, key, calc, repv, nd=2, note=""):
        if calc is None:
            ok = (repv is None)
            cs = "None(缺席)"
        else:
            cs = ("%." + str(nd) + "f") % float(calc)
            if repv is None:
                ok = False
            else:
                ok = abs(round(float(calc), nd) - float(repv)) <= 1e-9 * max(1.0, abs(float(repv)))
        self.pts.append({"id": pid, "face": face, "key": key, "calc": (None if calc is None else float(calc)),
                         "calc_str": cs, "report": repv, "ok": ok, "note": note})

    def adds(self, pid, face, key, calc_s, rep_s, note=""):
        ok = (str(calc_s) == str(rep_s))
        self.pts.append({"id": pid, "face": face, "key": key, "calc": str(calc_s), "calc_str": str(calc_s),
                         "report": rep_s, "ok": ok, "note": note})

    def addb(self, pid, face, key, calc, note=""):
        self.pts.append({"id": pid, "face": face, "key": key, "calc": bool(calc), "calc_str": str(bool(calc)),
                         "report": True, "ok": bool(calc), "note": note})

    def save(self, outdir, name):
        with open(os.path.join(outdir, name), "w", encoding="utf-8") as f:
            json.dump(self.pts, f, ensure_ascii=False, indent=0)
        bad = [p for p in self.pts if not p["ok"]]
        print("%s: points=%d mismatches=%d" % (name, len(self.pts), len(bad)))
        for p in bad:
            print("   MISMATCH", p["id"], "calc=", p["calc_str"], "report=", p["report"], "|", p["key"], "|", p["note"])


def series(SS, mid):
    s = SS.get(mid)
    if s is None:
        return None
    out = []
    for d, v in zip(s["dates"], s["values"]):
        if v is None:
            continue
        try:
            out.append((d, float(v)))
        except Exception:
            continue
    out.sort()
    return out


def at_or_before(SS, mid, date):
    s = series(SS, mid)
    if s is None:
        return None
    best = None
    for d, v in s:
        if d <= date:
            best = (d, v)
        else:
            break
    return best


def at(SS, mid, date):
    s = series(SS, mid)
    if s is None:
        return None
    for d, v in s:
        if d == date:
            return v
    return None


def at_month(SS, mid, ym):
    s = series(SS, mid)
    if s is None:
        return None
    for d, v in s:
        if d[:7] == ym:
            return (d, v)
    return None


def mv(SS, mid, ym):
    r = at_month(SS, mid, ym)
    return None if r is None else r[1]


def last(SS, mid):
    s = series(SS, mid)
    return s[-1] if s else None


def yoy(SS, mid, ym):
    y, m = int(ym[:4]), int(ym[5:7])
    a = at_month(SS, mid, ym)
    b = at_month(SS, mid, "%04d-%02d" % (y - 1, m))
    if a is None or b is None:
        return None
    return (a[1] / b[1] - 1.0) * 100.0


def pct(a, b):
    return (b / a - 1.0) * 100.0


def bp(a, b):
    return (b - a) * 100.0


def days(a, b):
    return (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days


def plus_days(d, n):
    return (dt.date.fromisoformat(d) + dt.timedelta(days=n)).isoformat()


def wd(d):
    return dt.date.fromisoformat(d).strftime("%A")


def changes(SS, mid, d0, d1, minbp=0.5):
    """窗内 [d0,d1] 的序列值变动点(与前一个有效观测相比)。"""
    s = series(SS, mid)
    out = []
    for i in range(1, len(s)):
        if s[i][0] < d0 or s[i][0] > d1:
            continue
        if abs(s[i][1] - s[i - 1][1]) * 100.0 >= minbp:
            out.append((s[i][0], s[i - 1][0], s[i - 1][1], s[i][1]))
    return out
