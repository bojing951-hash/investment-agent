# -*- coding: utf-8 -*-
"""Shared read-only helpers, seat T3 round 1 (Audit-R32). Loads the frozen inputs and the audited
judgment, exposes series/calendar/registry lookups and the claim-table recorder."""
import datetime as dt
import hashlib
import json
import os
from zoneinfo import ZoneInfo

EPS = 1e-12
SS = {}


def load(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def dp(x):
    s = repr(float(x))
    return 0 if ("e" in s or "E" in s or "." not in s) else len(s.split(".")[1])


def match(c, p):
    if isinstance(p, bool) or isinstance(c, bool):
        return c == p
    if isinstance(p, (int, float)) and isinstance(c, (int, float)):
        return abs(float(c) - float(p)) <= 0.5 * 10 ** (-dp(p)) + EPS
    if isinstance(p, (list, tuple)) and isinstance(c, (list, tuple)):
        return len(c) == len(p) and all(match(x, y) for x, y in zip(c, p))
    return c == p


def r(x, k=6):
    if isinstance(x, float):
        return round(x, k)
    if isinstance(x, (list, tuple)):
        return [r(v, k) for v in x]
    return x


def series(m):
    s = SS.get(m)
    if not s:
        raise KeyError("series absent: " + m)
    return sorted((d, v) for d, v in zip(s["dates"], s["values"]) if v is not None)


def at(m, date):
    last = None
    for d, v in series(m):
        if d <= date:
            last = (d, v)
        else:
            break
    return last


def prevobs(m, date):
    last = None
    for d, v in series(m):
        if d < date:
            last = (d, v)
        else:
            break
    return last


def val(m, date):
    for d, v in series(m):
        if d == date:
            return v
    raise KeyError("%s@%s absent" % (m, date))


def monthly(m):
    return dict((d[:7], v) for d, v in series(m))


def isMonthly(m):
    return all(d.endswith("-01") for d, _ in series(m))


def eom(ym):
    y, mo = int(ym[:4]), int(ym[5:7])
    return (dt.date(y + (mo == 12), mo % 12 + 1, 1) - dt.timedelta(days=1)).isoformat()


def latest_m(m, as_of):
    last = None
    for d, v in series(m):
        if eom(d[:7]) <= as_of:
            last = (d, v)
        else:
            break
    return last


def asof(m, date):
    return latest_m(m, date) if isMonthly(m) else at(m, date)


def pct(a, b):
    return (b - a) / a * 100.0


def wd(d):
    return dt.date.fromisoformat(d).strftime("%a")


def days(a, b):
    return (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days


def thu_before(d):
    x = dt.date.fromisoformat(d)
    return (x - dt.timedelta(days=(x.weekday() - 3) % 7)).isoformat()


def first_next(ym):
    y, mo = int(ym[:4]), int(ym[5:7])
    return dt.date(y + (mo == 12), mo % 12 + 1, 1).isoformat()


def rule_pub(ym, off):
    return (dt.date.fromisoformat(eom(ym)) + dt.timedelta(days=off)).isoformat()


def changes(m, lo, hi):
    s = series(m)
    return [(s[i][0], s[i - 1][1], s[i][1]) for i in range(1, len(s))
            if lo < s[i][0] <= hi and s[i][1] != s[i - 1][1]]


def tz_hm(iso, zone):
    return dt.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S%z").astimezone(ZoneInfo(zone)).strftime("%H:%M")


class Ctx(object):
    pass


def build(run_dir, tree, out_dir):
    c = Ctx()
    rp = lambda *a: os.path.join(run_dir, *a)
    c.run_dir, c.tree, c.out_dir = run_dir, tree, out_dir
    c.snap = load(rp("root_overlay", "data", "daily", "research_snapshot_20261123.json"))
    c.cal = load(rp("root_overlay", "config", "release_calendar.json"))
    c.reg = load(rp("root_overlay", "config", "metric_registry.json"))
    c.rep = load(rp("report.json"))
    c.J = load(rp("agent_judgment.json"))
    c.env = load(rp("AGENT_SEAT_ENVELOPE.json"))
    c.docs = {}
    for n in ("MAP_REPORT.md", "FULL_REPORT.md", "report.md"):
        with open(rp(n), "r", encoding="utf-8") as fh:
            c.docs[n] = fh.read()
    SS.clear()
    SS.update(c.snap["series_store"])
    c.jdump = json.dumps(c.J, ensure_ascii=False)
    c.rows, c.errors, c.F = [], [], {}
    plan = c.rep["research_plan"]
    c.plan = plan
    c.pa = dict((a["label"], a) for a in plan["point_anchors"])
    c.cutoff = c.pa["最新一期"]["as_of"]
    c.cells = dict((x["metric_id"], x) for x in plan["point_values"]["cells"])
    c.REGM = dict((m["metric_id"], m) for m in c.reg["metrics"])
    c.L1R = c.rep["layers"]["L1_事实层"]["rows"]
    c.EVI = dict((e["ref"], e) for e in c.rep["evidence_index"])
    c.CENT = c.cal["entries"]
    c.ga = c.snap["gate_a"]

    def l1(metric, date=None):
        for x in c.L1R:
            if x.get("metric_id") == metric and (date is None or x.get("observation_date") == date):
                return x

    def cent(metric=None):
        return [x for x in c.CENT if metric is None or x.get("metric_id") == metric
                or metric in (x.get("metric_ids") or [])]

    c.l1, c.cent = l1, cent
    c.ECBENT = [x for x in c.CENT if any(t in json.dumps(x, ensure_ascii=False)
                                          for t in ("ECB", "MRO", "DFR", "欧央行"))]
    c.S6 = None
    for st in c.rep["steps"]:
        ev = st.get("envelope") if isinstance(st, dict) else None
        if isinstance(ev, dict) and ev.get("capability") == "analog":
            c.S6 = ev
    c.cv = c.rep["agent_judgment"].get("contract_verification") or {}
    # audited texts
    T = {}
    J = c.J
    con = dict((x["id"], x) for x in J["l3"]["contradictions"])
    for k, s in (("C1", "C1-INFL-DIVERGE"), ("C2", "C2-POLICY-SYNC"), ("C3", "C3-ECB-VISIBILITY")):
        T[k] = con[s]["statement"]
    for lk in J["l3"]["mechanism_chains"][0]["links"]:
        T["M1.step%d" % lk["step"]] = lk["text"]
    RM = J["reader_map"]
    T["HC"] = RM["headline_conclusion"]
    T["EA"], T["JP"] = RM["regions"][0]["from_to"], RM["regions"][1]["from_to"]
    for i, lk in enumerate(RM["transmission"][0]["links"]):
        for k in ("observed_fact", "causal_hypothesis", "competing_explanation",
                  "main_predicts", "competing_predicts", "verdict_note"):
            T["TL%d.%s" % (i + 1, k)] = lk[k]
    for i, w in enumerate(RM["turnings"]):
        for k in ("first_mover", "follow_or_diverge", "narrative"):
            T["W%d.%s" % (i + 1, k)] = w[k]
    T["HIST"] = RM["history_zero_case_note"]
    for s in J["l4"]["scenarios"]:
        rw = s["rows"]
        T[s["id"] + ".scenario"] = rw["scenario"]
        T[s["id"] + ".asset"] = rw["asset_direction"]["direction"]
        T[s["id"] + ".falsify"] = rw["falsification"]["threshold"]
        T[s["id"] + ".trigger"] = rw["trigger"]["condition"]
    for i, q in enumerate(J["quality_gate_notes"]):
        T["Q%d" % i] = q
    c.T = T

    def A(cat, where, needle, src, comp, claim, note=""):
        found = True if needle is None else (needle in T[where])
        try:
            ok = bool(found) and bool(match(comp, claim))
        except Exception:
            ok = False
            note = (note + " [match error]").strip()
        c.rows.append({"cat": cat, "where": where, "needle": needle, "found": found, "src": src,
                       "computed": r(comp), "claimed": claim, "ok": ok, "note": note})
    c.A = A
    return c


def finish(c, name):
    p = os.path.join(c.out_dir, "_part_%s.json" % name)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump({"rows": c.rows, "errors": c.errors, "F": c.F}, fh, ensure_ascii=False, indent=1)
    print("part %s: rows=%d ok=%d notfound=%d errors=%d" % (
        name, len(c.rows), sum(1 for x in c.rows if x["ok"]),
        sum(1 for x in c.rows if not x["found"]), len(c.errors)))
    for x in c.rows:
        if not x["ok"]:
            print("  MISMATCH where=%s needle=%s computed=%s claimed=%s src=%s" % (
                x["where"], x["needle"], x["computed"], x["claimed"], x["src"]))
    for e in c.errors:
        print("  ERROR %s" % json.dumps(e, ensure_ascii=False))
    for k in sorted(c.F):
        print("  F %s = %s" % (k, json.dumps(c.F[k], ensure_ascii=False)[:400]))
