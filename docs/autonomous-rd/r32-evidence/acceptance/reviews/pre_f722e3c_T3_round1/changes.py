#!/usr/bin/env python3
"""Seat-owned read-only change-point / window extractor.
Usage:
  python3 -I changes.py <snap> changes <SID>            -> all change points (date, prev, new, diff) + last obs + weekday
  python3 -I changes.py <snap> window <SID> <from> <to> -> first/last obs within [from,to] and pct chg
  python3 -I changes.py <snap> obs_on_or_before <SID> <date> -> last obs with date <= given date
  python3 -I changes.py <snap> obs_on_or_after <SID> <date>  -> first obs with date >= given date
  python3 -I changes.py <snap> maxwin <SID> <from> <to>   -> max/min value and dates in window
"""
import datetime as dt
import json
import sys


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)["series_store"]


def series(store, sid):
    s = store[sid]
    return list(zip(s["dates"], s["values"]))


def main(argv):
    store = load(argv[0])
    mode = argv[1]
    out = sys.stdout
    if mode == "changes":
        for sid in argv[2:]:
            pts = series(store, sid)
            out.write(f"## {sid}: n={len(pts)} first={pts[0][0]} last={pts[-1][0]}\n")
            out.write(f"first obs: {pts[0]}\n")
            out.write(f"last obs: {pts[-1]} weekday={dt.date.fromisoformat(pts[-1][0]).strftime('%a')}\n")
            prev = None
            nchg = 0
            for d, v in pts:
                if prev is not None and v is not None and prev[1] is not None and v != prev[1]:
                    nchg += 1
                    wd = dt.date.fromisoformat(d).strftime('%a')
                    out.write(f"CHG {sid}\t{d}({wd})\t{prev[1]}->{v}\tdiff={round((v - prev[1]) * 100, 3)}bp\tprev_obs={prev[0]}\n")
                if v is not None:
                    prev = (d, v)
            out.write(f"n_changes={nchg}\n")
        return
    if mode == "window":
        sid, frm, to = argv[2], argv[3], argv[4]
        pts = [(d, v) for d, v in series(store, sid) if frm <= d <= to and v is not None]
        if not pts:
            out.write(f"{sid}: no obs in [{frm},{to}]\n")
            return
        a, b = pts[0], pts[-1]
        pct = (b[1] / a[1] - 1.0) * 100.0
        out.write(f"{sid}\twindow[{frm},{to}]\tfirst={a}\tlast={b}\tchg={round(b[1] - a[1], 6)}\tpct={round(pct, 4)}%\tn_obs={len(pts)}\n")
        return
    if mode == "obs_on_or_before":
        sid, q = argv[2], argv[3]
        pts = [(d, v) for d, v in series(store, sid) if d <= q and v is not None]
        out.write(f"{sid}\t<= {q}\t{pts[-1] if pts else None}\n")
        return
    if mode == "obs_on_or_after":
        sid, q = argv[2], argv[3]
        pts = [(d, v) for d, v in series(store, sid) if d >= q and v is not None]
        out.write(f"{sid}\t>= {q}\t{pts[0] if pts else None}\n")
        return
    if mode == "maxwin":
        sid, frm, to = argv[2], argv[3], argv[4]
        pts = [(d, v) for d, v in series(store, sid) if frm <= d <= to and v is not None]
        mx = max(pts, key=lambda t: t[1])
        mn = min(pts, key=lambda t: t[1])
        out.write(f"{sid}\twindow[{frm},{to}]\tmax={mx}\tmin={mn}\n")
        return
    out.write("unknown mode\n")


if __name__ == "__main__":
    main(sys.argv[1:])
