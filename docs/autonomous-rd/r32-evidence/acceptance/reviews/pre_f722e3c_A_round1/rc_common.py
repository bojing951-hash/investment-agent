#!/usr/bin/env python3
"""Seat common context for the Round-1 recompute (read-only; independent of engine code).

Loaded by recompute.py. All numbers come from the frozen snapshot series_store, the frozen release
calendar, report.json engine faces and the report text (MAP_REPORT.md) passed as path arguments.
"""
import calendar as _cal
import json
import re
import sys
from datetime import date, timedelta

sys.path.insert(0, "/tmp/r32-accept/review/A_round1")
import seatlib as L  # noqa: E402

CUTOFF = "2026-11-23"
ANCHORS = [("12个月前", "2025-11-23"), ("3个月前", "2026-08-23"), ("最新一期", CUTOFF)]
ANCHOR_DATE = {k: v for k, v in ANCHORS}

# publication rules as printed by the report itself (月末+N天 / 当日 / 次日); calendar entries take priority
RULE_LAG = {
    "CN_PMI_MFG": -1, "CN_CPI_YOY": 9, "CN_PPI_YOY": 9, "EA_HICP_YOY": 16, "JP_CPI_TOKYO_YOY": -1,
    "JP_CPI_YOY": 20, "JP_POLICY_RATE": 5, "INDPRO": 15, "UNEMPLOYMENT": 5, "CPI": 13, "CORE_CPI": 13,
    "CORE_PCE": 30,
}
RULE_Q_LAG = {"US_REAL_GDP": 29, "EA_REAL_GDP_YOY": 35, "JP_REAL_GDP_YOY": 45}   # from quarter end
SAME_DAY = {"DFEDTARU", "DFEDTARL", "ECB_DFR", "ECB_MRO", "CN_LPR_1Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT"}
NEXT_DAY = {"DFF"}


def month_end(ym):
    y, m = int(ym[:4]), int(ym[5:7])
    return "%04d-%02d-%02d" % (y, m, _cal.monthrange(y, m)[1])


def add_days(d, n):
    return (date.fromisoformat(d) + timedelta(days=n)).isoformat()


def days_between(a, b):
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def num(s):
    """parse first signed decimal in a string -> float or None"""
    if s is None:
        return None
    m = re.search(r"[-+]?\d+(?:\.\d+)?", str(s).replace("−", "-"))
    return float(m.group(0)) if m else None


def close(a, b, decimals=2, rel=None):
    if a is None or b is None:
        return a is None and b is None
    tol = 0.5 * 10 ** (-decimals) + 1e-9
    if rel is not None and abs(a) > 1e-12:
        tol = max(tol, rel * abs(a))
    return abs(a - b) <= tol


def md_tables(lines):
    """parse markdown pipe tables -> list of dicts {header, rows, line(1-based of header)}"""
    out = []
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        if ln.strip().startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            header = [c.strip() for c in ln.strip().strip("|").split("|")]
            j = i + 2
            rows = []
            while j < n and lines[j].strip().startswith("|"):
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            out.append({"header": header, "rows": rows, "line": i + 1})
            i = j
        else:
            i += 1
    return out


class Ctx:
    def __init__(self, argv):
        self.snap_path, self.cal_path, self.rep_path, self.reg_path, self.map_path, self.out_path = argv[1:7]
        self.snap = L.load(self.snap_path)
        self.cal = L.load(self.cal_path)
        self.rep = L.load(self.rep_path)
        self.reg = L.load(self.reg_path)
        with open(self.map_path, "r", encoding="utf-8") as f:
            self.map_lines = f.read().split("\n")
        self.tables = md_tables(self.map_lines)
        self.steps = {st.get("step"): st for st in self.rep.get("steps", [])}
        self.reg_ids = {m.get("metric_id") for m in self.reg.get("metrics", [])}
        self._S = {}
        self.pts = []
        self.notes = []

    # ---- series helpers -------------------------------------------------
    def ser(self, sid):
        if sid not in self._S:
            self._S[sid] = L.series(self.snap, sid)
        return self._S[sid]

    def has(self, sid):
        return self.snap["series_store"].get(sid) is not None

    def exact(self, sid, d):
        p = self.ser(sid)
        return L.exact(p, d) if p is not None else None

    def lob(self, sid, d):
        """last observation on or before d -> (date, value) | None"""
        p = self.ser(sid)
        return L.last_on_or_before(p, d) if p is not None else None

    def val(self, sid, d):
        t = self.lob(sid, d)
        return None if t is None else t[1]

    def mlast(self, sid, ym):
        p = self.ser(sid)
        return L.month_last(p, ym) if p is not None else None

    def mmean(self, sid, ym):
        p = self.ser(sid)
        return L.month_mean(p, ym) if p is not None else (None, 0)

    def yoy(self, sid, d):
        p = self.ser(sid)
        return L.yoy(p, d) if p is not None else (None, None, None)

    # ---- publication ----------------------------------------------------
    def cal_entries(self, sid, obs):
        hits = []
        for e in self.cal.get("entries", []):
            ids = []
            if e.get("metric_id"):
                ids.append(e["metric_id"])
            ids += list(e.get("metric_ids") or [])
            if sid in ids and e.get("obs_from", "0000") <= obs <= e.get("obs_to", "9999"):
                hits.append(e)
        return hits

    def pub(self, sid, obs):
        """(publication date, basis) — calendar entry (earliest first_publish) else report's rule"""
        hits = self.cal_entries(sid, obs)
        if hits:
            hits.sort(key=lambda e: e.get("first_publish_on_or_after") or "9999")
            return hits[0].get("first_publish_on_or_after"), "calendar:" + hits[0].get("entry_id", "?")
        if sid in SAME_DAY:
            return obs, "rule:same_day"
        if sid in NEXT_DAY:
            return add_days(obs, 1), "rule:next_day"
        if sid in RULE_Q_LAG:
            return add_days(month_end(L.shift_months(obs, 2)), RULE_Q_LAG[sid]), "rule:q_end+%d" % RULE_Q_LAG[sid]
        if sid in RULE_LAG:
            return add_days(month_end(obs[:7]), RULE_LAG[sid]), "rule:month_end%+d" % RULE_LAG[sid]
        return obs, "rule:assume_same_day"

    def visible(self, sid, anchor):
        """latest observation of sid whose publication date <= anchor -> (date, value, pub, basis) | None"""
        p = self.ser(sid)
        if p is None:
            return None
        best = None
        for d, v in p:
            if d > anchor:
                break
            pd, basis = self.pub(sid, d)
            if pd <= anchor:
                best = (d, v, pd, basis)
        return best

    # ---- points ---------------------------------------------------------
    def add(self, pid, cat, source, computed, reported, ok, note=""):
        p = {"id": pid, "category": cat, "source": source, "computed": computed, "reported": reported,
             "match": bool(ok)}
        if note:
            p["note"] = note
        self.pts.append(p)
        return bool(ok)

    def note(self, cat, text):
        self.notes.append({"category": cat, "note": text})
