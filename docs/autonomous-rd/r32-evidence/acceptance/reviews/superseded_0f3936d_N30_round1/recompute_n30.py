#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Seat recompute script (read-only) — Audit-R32 N30 Round-1, independent zero-context seat.

Every point is computed directly from the frozen faces (snapshot series_store / facts / gate_a,
frozen release calendar, metric registry, report.json engine face) and only THEN compared with the
value stated in the audited judgment text (agent_judgment.json) / reader report (MAP_REPORT.md).
The `snip` guard asserts that the transcribed "report value" really occurs in the audited text.

Usage:
  /usr/bin/python3 -I recompute_n30.py <report.json> <snapshot.json> <calendar.json> \
      <registry.json> <agent_judgment.json> <MAP_REPORT.md> <evidence_index.json> <out_dir>
Outputs (written only to out_dir): recompute_table.md, recompute_summary.json
"""
import calendar
import json
import os
import re
import sys
from datetime import date, datetime, timedelta

CUT = date(2026, 11, 23)
PTS = []
SNIP_MISS = []


def add(cat, src, comp, rep, ok, where, note="", ctx=False, snip=None):
    p = {"id": len(PTS) + 1, "cat": cat, "src": src, "comp": comp, "rep": rep, "ok": bool(ok),
         "where": where, "note": note, "ctx": ctx, "snip": snip}
    PTS.append(p)
    return p


def num_ok(comp, rep, tol):
    try:
        return comp is not None and rep is not None and abs(float(comp) - float(rep)) <= tol + 1e-9
    except (TypeError, ValueError):
        return False


def r2(x):
    return None if x is None else round(x + 0.0, 2)


def r3(x):
    return None if x is None else round(x + 0.0, 3)


def main():
    (rep_p, snap_p, cal_p, reg_p, judg_p, map_p, ev_p, out_dir) = sys.argv[1:9]
    src_contract, src_textcons = (sys.argv[9:11] if len(sys.argv) >= 11 else (None, None))
    with open(rep_p, encoding="utf-8") as f:
        rep = json.load(f)
    with open(snap_p, encoding="utf-8") as f:
        snap = json.load(f)
    with open(cal_p, encoding="utf-8") as f:
        cal = json.load(f)
    with open(reg_p, encoding="utf-8") as f:
        reg = json.load(f)
    with open(judg_p, encoding="utf-8") as f:
        judg = json.load(f)
    with open(map_p, encoding="utf-8") as f:
        map_txt = f.read()
    with open(ev_p, encoding="utf-8") as f:
        ev = json.load(f)
    full_txt = ""
    fp = os.path.join(os.path.dirname(os.path.abspath(map_p)), "FULL_REPORT.md")
    if os.path.exists(fp):
        with open(fp, encoding="utf-8") as f:
            full_txt = f.read()
    judg_txt = json.dumps(judg, ensure_ascii=False)

    def has(s):
        return (s in judg_txt) or (s in map_txt)

    ss = snap["series_store"]
    facts = {f_["fact_id"]: f_ for f_ in snap["facts"]}
    plan = rep["research_plan"]
    run = rep["run"]
    regm = {m.get("metric_id") or m.get("id"): m for m in reg["metrics"]}

    # ---------- series helpers ----------
    def ser(mid):
        s = ss[mid]
        return [date.fromisoformat(x) for x in s["dates"]], s["values"]

    def at(mid, ds):
        k = date.fromisoformat(ds) if isinstance(ds, str) else ds
        for x, y in zip(*ser(mid)):
            if x == k:
                return y
        return None

    def last_le(mid, ds):
        k = date.fromisoformat(ds) if isinstance(ds, str) else ds
        best = None
        for x, y in zip(*ser(mid)):
            if x <= k:
                best = (x, y)
        return best

    def mv(mid, ym):
        for x, y in zip(*ser(mid)):
            if x.strftime("%Y-%m") == ym:
                return y
        return None

    def pct(a, b):
        return (b / a - 1.0) * 100.0

    def month_end(y, m):
        return date(y, m, calendar.monthrange(y, m)[1])

    def pub(obs, rule):
        x = date.fromisoformat(obs) if isinstance(obs, str) else obs
        off = {"me+16": 16, "me+20": 20, "me-1": -1, "me+5": 5}[rule]
        return month_end(x.year, x.month) + timedelta(days=off)

    def prev_thursday(d):
        x = d
        while x.weekday() != 3:
            x -= timedelta(days=1)
        return x

    def days(a, b):
        return (date.fromisoformat(b) if isinstance(b, str) else b) - (date.fromisoformat(a) if isinstance(a, str) else a)

    WK = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

    # engine cells
    cells = {}
    for c in plan["point_values"]["cells"]:
        for lab, a in c["anchors"].items():
            cells[(c["metric_id"], lab)] = a

    def find_key(obj, key):
        if isinstance(obj, dict):
            if key in obj:
                return obj[key]
            for v in obj.values():
                r = find_key(v, key)
                if r is not None:
                    return r
        elif isinstance(obj, list):
            for v in obj:
                r = find_key(v, key)
                if r is not None:
                    return r
        return None

    # =====================================================================
    # ① 研究截止日
    # =====================================================================
    C = "①截止日"
    asof = snap["research_as_of"]
    add(C, "snapshot.research_as_of", asof[:10], "2026-11-23", asof[:10] == "2026-11-23",
        "agent_declaration.basis", snip="研究截止取实际覆盖日 2026-11-23")
    add(C, "snapshot.target_date", snap["target_date"], "20261123", snap["target_date"] == "20261123",
        "MAP_REPORT 头部", snip="快照实际覆盖 2026-11-23")
    add(C, "report.json research_plan.cutoff", plan["cutoff"], "2026-11-23", plan["cutoff"] == "2026-11-23",
        "MAP_REPORT 头部", snip="研究截止日: 2026-11-23")
    add(C, "report.json run.evidence_asof", run["evidence_asof"], "2026-11-23", run["evidence_asof"] == "2026-11-23",
        "agent_declaration.basis")
    cited = ["EA_HICP_YOY", "JP_CPI_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_RATE", "ECB_DFR", "ECB_MRO",
             "SPX", "NIKKEI225", "DAX", "CAC40", "VIX", "EURUSD", "USDJPY", "DXY", "UST_10Y", "TIPS_10Y", "BEI_10Y"]
    lastobs = {m: ser(m)[0][-1].isoformat() for m in cited}
    mx = max(lastobs.values())
    add(C, "series_store[*].dates[-1] (17 cited series)", mx, "≤2026-11-23", mx <= "2026-11-23",
        "全档", note="latest per series: " + ", ".join(f"{k}={v}" for k, v in lastobs.items()))

    # presumed publication dates of every observation month the judgment relies on
    RULE = {"EA_HICP_YOY": "me+16", "JP_CPI_YOY": "me+20", "JP_CPI_TOKYO_YOY": "me-1", "JP_POLICY_RATE": "me+5"}
    pubmap = {}
    for m, rule in RULE.items():
        d, _ = ser(m)
        for x in d:
            if x >= date(2025, 10, 1):
                pubmap[(m, x.isoformat())] = pub(x, rule)
    mxp = max(pubmap.values())
    add(C, "series_store obs + registry/engine 推定规则(月末+16/+20/−1/+5)", mxp.isoformat(), "≤2026-11-23",
        mxp <= CUT, "C1/C2 公布日", note="max presumed pub among obs 2025-10..latest of the four monthly series", snip="发布 2026-11-20")
    dec_dates = ["2026-06-11", "2026-06-17", "2026-09-10", "2026-09-16", "2026-09-18", "2026-09-24", "2026-10-30"]
    add(C, "冻结日历条目 + 序列变更日(决议/生效/维持)", max(dec_dates), "≤2026-11-23",
        max(dec_dates) <= "2026-11-23", "C2/M1", snip="2026-10-30 会议确认维持")

    # all YYYY-MM-DD tokens in the judgment and their relation to the cutoff
    toks = re.findall(r"20\d{2}-\d{2}-\d{2}", judg_txt)
    late = sorted({t for t in toks if t > "2026-11-23"})
    late_ok = late == ["2026-11-24", "2026-11-30", "2027-02-15"]
    paths = set()
    def walk_keys(o, path=""):
        if isinstance(o, dict):
            for k, v in o.items():
                yield from walk_keys(v, path + "." + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                yield from walk_keys(v, path + "[%d]" % i)
        else:
            yield path, o
    for pth, v in walk_keys(judg):
        if isinstance(v, str):
            for t in re.findall(r"20\d{2}-\d{2}-\d{2}", v):
                if t > "2026-11-23":
                    paths.add((t, pth.split("[")[0] if "scenarios" in pth else pth))
    add(C, "agent_judgment.json 全文正则 YYYY-MM-DD > 截止日", sorted(paths), "仅 written_at 时间戳 / 请求月末(披露未到) / 情景期限",
        late_ok, "l4.scenarios 触发期限 / agent_declaration",
        note="2026-11-24=agent_declaration.written_at(成稿时间戳); 2026-11-30=请求月末(披露未到、已取实际覆盖日); 2027-02-15=情景期限", snip='"deadline": "2027-02-15"')
    ym_toks = sorted({t for t in re.findall(r"20\d{2}-\d{2}(?![-\d])", judg_txt) if t > "2026-11"})
    add(C, "agent_judgment.json 全文正则 YYYY-MM > 2026-11", ym_toks, ["2026-12", "2027-01"],
        ym_toks == ["2026-12", "2027-01"], "l4.scenarios", note="2026-12=情景观测月(未发布,非已知值); 2027-01=入档月",
        snip="于 2027-01 入档")

    # =====================================================================
    # ② 点值锚格 (12 cells) + anchor_echo + window start
    # =====================================================================
    C = "②锚格"
    A6, AL = "2026-05-23", "2026-11-23"
    anchor_specs = [
        ("EA_HICP_YOY", A6, 3.0, "2026-04-01", "3.0%", "观测月 2026-04,发布 2026-05-16"),
        ("EA_HICP_YOY", AL, 4.0, "2026-10-01", "4.0%", "观测 2026-10,发布 2026-11-16"),
        ("ECB_MRO", A6, 2.15, "2025-06-11", "2.15%", "观测 2025-06-11)的 2.15%"),
        ("ECB_MRO", AL, 2.65, "2026-09-16", "2.65%", "2.65%"),
        ("ECB_DFR", A6, 2.0, "2025-06-11", "2.0%", "由 2.0% 升至 2.5%"),
        ("ECB_DFR", AL, 2.5, "2026-09-16", "2.5%", "升至最新水平 2.5%"),
        ("JP_CPI_YOY", A6, 1.38, "2026-04-01", "1.38%", "观测月 2026-04,发布 2026-05-20"),
        ("JP_CPI_YOY", AL, 2.44, "2026-10-01", "2.44%", "观测 2026-10,发布 2026-11-20"),
        ("JP_CPI_TOKYO_YOY", A6, 1.42, "2026-04-01", "1.42%", "1.42%"),
        ("JP_CPI_TOKYO_YOY", AL, 2.73, "2026-10-01", "2.73%", "发布 2026-10-30"),
        ("JP_POLICY_RATE", A6, 0.727, "2026-04-01", "0.727", "观测月 2026-04,发布 2026-05-05"),
        ("JP_POLICY_RATE", AL, 1.227, "2026-10-01", "1.227", "观测月 2026-10,发布 2026-11-05"),
    ]
    def anchor_val(mid, a):
        """latest observation of `mid` that is PUBLIC by anchor date a (presumed publication rule for monthly series)."""
        k = date.fromisoformat(a) if isinstance(a, str) else a
        if mid in RULE:
            cands = [(date.fromisoformat(o), v) for (m_, o), p in pubmap.items() if m_ == mid and p <= k for v in [mv(mid, o[:7])]]
            return max(cands, key=lambda t: t[0]) if cands else (None, None)
        return last_le(mid, k)

    for mid, a, repv, repd, reps, snip in anchor_specs:
        d, v = anchor_val(mid, a)
        lab = "6个月前" if a == A6 else "最新一期"
        ec = cells.get((mid, lab), {})
        eng_ok = (ec.get("value") == v and ec.get("observation_date") == d.isoformat())
        add(C, f"series_store[{mid}] latest obs with (presumed) pub ≤ {a}", f"{d.isoformat()}={v}",
            f"{repd}={repv}", num_ok(v, repv, 0.0005) and d.isoformat() == repd and eng_ok,
            "reader_map.regions/anchor_echo", note="engine cell=%s" % json.dumps(
                {"value": ec.get("value"), "observation_date": ec.get("observation_date"),
                 "publication_date": ec.get("publication_date")}, ensure_ascii=False), snip=snip)

    # anchor_echo 12 entries
    echo = []
    for rg in judg["reader_map"]["regions"]:
        for e in rg["anchor_echo"]:
            a = A6 if e["anchor"] == "6个月前" else AL
            d, v = anchor_val(e["metric_id"], a)
            echo.append(e["value"] == v and d.strftime("%Y-%m") == e["observation_month"])
    add(C, "anchor_echo(12 格) vs 快照各序列「已发布≤锚日」最新观测", "%d/%d" % (sum(echo), len(echo)), "12/12",
        all(echo) and len(echo) == 12, "reader_map.regions[*].anchor_echo")
    ws = (CUT.replace(day=1) - timedelta(days=0))
    # cut - 6 months
    y, m = CUT.year, CUT.month
    m -= 6
    while m <= 0:
        m += 12
        y -= 1
    add(C, "截止日 2026-11-23 − 6 个自然月", date(y, m, min(CUT.day, calendar.monthrange(y, m)[1])).isoformat(),
        "2026-05-23", date(y, m, 23).isoformat() == "2026-05-23", "headline_conclusion",
        note="engine question_window=%s" % json.dumps(plan["question_window"]["windows"][0], ensure_ascii=False),
        snip="窗起 2026-05-23 至研究截止 2026-11-23")

    # =====================================================================
    # ③ 同比 / 去年同月对照 / 锚间变化
    # =====================================================================
    C = "③同比对照"
    add(C, "series_store[EA_HICP_YOY] 2025-10", mv("EA_HICP_YOY", "2025-10"), 2.1, num_ok(mv("EA_HICP_YOY", "2025-10"), 2.1, 0.0501),
        "headline/EA from_to", snip="2025-10 为 2.1")
    add(C, "series_store[JP_CPI_YOY] 2025-10", mv("JP_CPI_YOY", "2025-10"), 2.99, num_ok(mv("JP_CPI_YOY", "2025-10"), 2.99, 0.0051),
        "headline/JP from_to", snip="2025-10 为 2.99")
    ea_d = mv("EA_HICP_YOY", "2026-10") - mv("EA_HICP_YOY", "2025-10")
    add(C, "EA 2026-10 − 2025-10", r2(ea_d), 1.9, num_ok(ea_d, 1.9, 0.0501), "C1/EA from_to", snip="高 1.9 个百分点")
    jp_d = mv("JP_CPI_YOY", "2026-10") - mv("JP_CPI_YOY", "2025-10")
    add(C, "JP 2026-10 − 2025-10", r2(jp_d), -0.55, num_ok(jp_d, -0.55, 0.0051), "C1/JP from_to", snip="低 0.55 个百分点")
    gap = mv("EA_HICP_YOY", "2026-10") - mv("JP_CPI_YOY", "2026-10")
    add(C, "EA 2026-10 − JP 2026-10", r2(gap), 1.56, num_ok(gap, 1.56, 0.0051), "C1", snip="约一点五六个百分点")
    tk_d, _ = ser("JP_CPI_TOKYO_YOY")
    add(C, "series_store[JP_CPI_TOKYO_YOY].dates[0]", tk_d[0].isoformat(), "2026-01-01(去年同月不在序列)",
        tk_d[0].isoformat() == "2026-01-01" and mv("JP_CPI_TOKYO_YOY", "2025-10") is None, "C1/JP from_to",
        note="n=%d, last=%s" % (len(tk_d), tk_d[-1].isoformat()), snip="去年同月读数不在序列内")
    add(C, "EA latest − EA 6m anchor", r2(mv("EA_HICP_YOY", "2026-10") - mv("EA_HICP_YOY", "2026-04")), 1.0,
        num_ok(mv("EA_HICP_YOY", "2026-10") - mv("EA_HICP_YOY", "2026-04"), 1.0, 0.0501), "C1", snip="均约一个百分点")
    add(C, "JP latest − JP 6m anchor", r2(mv("JP_CPI_YOY", "2026-10") - mv("JP_CPI_YOY", "2026-04")), 1.06,
        num_ok(mv("JP_CPI_YOY", "2026-10") - mv("JP_CPI_YOY", "2026-04"), 1.0, 0.0501), "C1",
        note="JP 1.38→2.44 = +1.06pp (\"约一个百分点\")", ctx=True, snip="均约一个百分点")
    # JP policy: three calibres
    add(C, "series_store[JP_POLICY_RATE] 2025-11", mv("JP_POLICY_RATE", "2025-11"), 0.478,
        num_ok(mv("JP_POLICY_RATE", "2025-11"), 0.478, 0.0005), "JP from_to", snip="2025-11 的 0.478")
    add(C, "(JP_POLICY_RATE 2026-10 − 2025-11)×100", r((mv("JP_POLICY_RATE", "2026-10") - mv("JP_POLICY_RATE", "2025-11")) * 100, 1),
        75, num_ok((mv("JP_POLICY_RATE", "2026-10") - mv("JP_POLICY_RATE", "2025-11")) * 100, 75, 0.5),
        "JP from_to", snip="约 +75bp")
    add(C, "(JP_POLICY_RATE 2026-10 − 2026-04)×100", r((mv("JP_POLICY_RATE", "2026-10") - mv("JP_POLICY_RATE", "2026-04")) * 100, 1),
        50, num_ok((mv("JP_POLICY_RATE", "2026-10") - mv("JP_POLICY_RATE", "2026-04")) * 100, 50, 0.5),
        "JP from_to/C2", snip="六个月锚间净 +50bp")
    fw = min([(x, y) for x, y in zip(*ser("JP_POLICY_RATE")) if x >= date(2025, 11, 23)], key=lambda t: t[0])
    add(C, "JP_POLICY_RATE first obs≥2025-11-23 → 2026-10 (引擎窗首尾口径)", r((mv("JP_POLICY_RATE", "2026-10") - fw[1]) * 100, 1),
        67, num_ok((mv("JP_POLICY_RATE", "2026-10") - fw[1]) * 100, 67, 0.5), "JP from_to",
        note="window start obs=%s=%.3f; engine policy_window_path.net_bp=67 (窗首尾观测差口径,不含窗启前 2025-11-01→2025-12-01 的 +8bp)" % (fw[0].isoformat(), fw[1]),
        snip="引擎政策窗净 +67bp")
    jp_cell = [c for c in plan["point_values"]["cells"] if c["metric_id"] == "JP_POLICY_RATE"][0]
    eng_pwp = jp_cell.get("policy_window_path") or {}
    ev_steps = [(e["date"], e["from"], e["to"], round((mv("JP_POLICY_RATE", e["date"][:7]) - e["from"]) * 100), e["delta_bp"]) for e in eng_pwp.get("events", [])]
    add(C, "engine policy_window_path(JP_POLICY_RATE).events (date, from, to, seriesΔbp, engineΔbp)",
        ev_steps, "seriesΔbp == engineΔbp for all 6 events", all(x[3] == x[4] for x in ev_steps) and len(ev_steps) == 6,
        "JP from_to", note=("Σ engine delta_bp=%d (窗内事件合计,引擎 net_bp=67 为窗首尾观测差); engine events=%s; 判断档三口径(+50/+75/+67)各自正确" % (
            sum(e["delta_bp"] for e in eng_pwp.get("events", [])),
            json.dumps([(e["date"], e["from"], e["to"], e["delta_bp"]) for e in eng_pwp.get("events", [])], ensure_ascii=False))),
        snip="近 12 个月月均由 2025-11 的 0.478 升至 2026-10 的 1.227,约 +75bp")
    add(C, "report.json policy_window_path(JP_POLICY_RATE).window", json.dumps(eng_pwp.get("window")), "2025-11-23..2026-11-23",
        "2025-11-23" in json.dumps(eng_pwp.get("window")) and "2026-11-23" in json.dumps(eng_pwp.get("window")),
        "JP from_to", note="engine face", snip="窗口 2025-11-23..2026-11-23")
    mro_steps = [0.25, 0.25]
    add(C, "ECB 六个月锚间: MRO 2.65−2.15, DFR 2.5−2.0", [r(mv("ECB_MRO", "2026-09") - 2.15, 2), r(mv("ECB_DFR", "2026-09") - 2.0, 2)],
        [0.50, 0.50], num_ok(mv("ECB_MRO", "2026-09") - 2.15, 0.5, 1e-9) and num_ok(mv("ECB_DFR", "2026-09") - 2.0, 0.5, 1e-9),
        "headline", note="两次各 25bp 合计 50bp", snip="两次合计五十个基点")
    boj_t = [e for e in cal["entries"] if e.get("entry_id") == "RC-JP-BOJ-TARGET-2026-09"][0]["target_value"]
    add(C, "DFR 2.5 − 日历 JP_POLICY_TARGET 1.25", r2(at("ECB_DFR", "2026-09-16") - boj_t), 1.25,
        num_ok(at("ECB_DFR", "2026-09-16") - boj_t, 1.25, 0.0051), "C2", snip="DFR 二点五 vs BOJ 目标约一点二五")

    # =====================================================================
    # ④ 政策面
    # =====================================================================
    C = "④政策面"

    def changes(mid, lo="2025-01-01"):
        d, v = ser(mid)
        out = []
        for i in range(1, len(d)):
            if d[i].isoformat() >= lo and v[i] != v[i - 1]:
                out.append((d[i].isoformat(), v[i - 1], v[i]))
        return out

    ch_dfr = changes("ECB_DFR", "2026-01-01")
    ch_mro = changes("ECB_MRO", "2026-01-01")
    add(C, "series_store[ECB_DFR] 2026 变更点", ch_dfr[0], ["2026-06-17", 2.0, 2.25], ch_dfr[0] == ("2026-06-17", 2.0, 2.25),
        "C2/M1 step2", note="all 2026 change points=%s" % ch_dfr, snip="2026-06-17 生效(决议日 2026-06-11")
    add(C, "series_store[ECB_DFR] 2026 变更点", ch_dfr[1], ["2026-09-16", 2.25, 2.5], ch_dfr[1] == ("2026-09-16", 2.25, 2.5),
        "C2/M1 step2", snip="2026-09-16 生效(决议日 2026-09-10")
    add(C, "series_store[ECB_MRO] 2026 变更点", ch_mro[0], ["2026-06-17", 2.15, 2.4], ch_mro[0] == ("2026-06-17", 2.15, 2.4),
        "M1 step2", snip="MRO 2.15→2.4、DFR 2.0→2.25")
    add(C, "series_store[ECB_MRO] 2026 变更点", ch_mro[1], ["2026-09-16", 2.4, 2.65], ch_mro[1] == ("2026-09-16", 2.4, 2.65),
        "M1 step2", snip="MRO 2.4→2.65、DFR 2.25→2.5")
    add(C, "number of ECB change points in 2026 (two series)", [len(ch_dfr), len(ch_mro)], [2, 2],
        len(ch_dfr) == 2 and len(ch_mro) == 2, "C2", snip="窗内两次同幅上调")
    steps_bp = [round((c[2] - c[1]) * 100) for c in ch_dfr + ch_mro]
    add(C, "(to−from)×100 for the four change points", steps_bp, [25, 25, 25, 25], steps_bp == [25, 25, 25, 25],
        "C2/M1 step2", snip="各 +25bp")
    add(C, "weekday(2026-06-17) / 上一个周四", WK[date(2026, 6, 17).weekday()] + "/" + prev_thursday(date(2026, 6, 17)).isoformat(),
        "周三/2026-06-11", prev_thursday(date(2026, 6, 17)).isoformat() == "2026-06-11", "C2",
        note="engine cell policy_dates.decision=%s" % (cells[("ECB_DFR", "最新一期")].get("policy_dates") or {}).get("decision"),
        snip="决议日 2026-06-11")
    add(C, "weekday(2026-09-16) / 上一个周四", WK[date(2026, 9, 16).weekday()] + "/" + prev_thursday(date(2026, 9, 16)).isoformat(),
        "周三/2026-09-10", prev_thursday(date(2026, 9, 16)).isoformat() == "2026-09-10", "C2",
        note="engine cell policy_dates.decision=%s" % (cells[("ECB_DFR", "最新一期")].get("policy_dates") or {}).get("decision"),
        snip="决议日 2026-09-10")
    add(C, "weekday(2025-06-11) / 上一个周四", WK[date(2025, 6, 11).weekday()] + "/" + prev_thursday(date(2025, 6, 11)).isoformat(),
        "周三/2025-06-05", prev_thursday(date(2025, 6, 11)).isoformat() == "2025-06-05", "MAP_REPORT 政策口径四分面",
        note="engine cell 6个月前 policy_dates.decision=%s" % (cells[("ECB_DFR", "6个月前")].get("policy_dates") or {}).get("decision"),
        snip="2025-06-05(决议日=生效日前的上一个周四")
    add(C, "2026-09-16 − 2026-06-17", days("2026-06-17", "2026-09-16").days, 91, days("2026-06-17", "2026-09-16").days == 91,
        "link1 verdict_note", snip="两次变更相隔 91 天")
    d371 = days("2025-06-11", "2026-06-17").days
    n_between = len([x for x in ser("ECB_DFR")[0] if date(2025, 6, 11) < x < date(2026, 6, 17)])
    add(C, "2026-06-17 − 2025-06-11; obs strictly between", [d371, n_between], [371, 0], d371 == 371 and n_between == 0,
        "link1 verdict_note", note="ECB_MRO likewise %d obs between" % len([x for x in ser("ECB_MRO")[0] if date(2025, 6, 11) < x < date(2026, 6, 17)]),
        snip="维持 2.15/2.0 共 371 天")
    lag = days("2026-09-16", "2026-11-23").days
    add(C, "2026-11-23 − ECB last obs 2026-09-16", lag, 68, lag == 68, "C3②", snip="六十八天")
    fr = {m: regm[m]["freshness"].get("max_calendar_lag_days") for m in ("ECB_MRO", "ECB_DFR")}
    add(C, "registry[ECB_MRO/ECB_DFR].freshness.max_calendar_lag_days", fr, {"ECB_MRO": 10, "ECB_DFR": 10},
        fr == {"ECB_MRO": 10, "ECB_DFR": 10} and lag > 10, "C3②", snip="新鲜度阈十天")
    ga = snap["gate_a"]
    add(C, "snapshot.gate_a.noncore_degraded ⊇ {ECB_DFR, ECB_MRO}", [m in ga["noncore_degraded"] for m in ("ECB_DFR", "ECB_MRO")],
        [True, True], all(m in ga["noncore_degraded"] for m in ("ECB_DFR", "ECB_MRO")), "C3②", snip="Gate A 将该两序列列于降级名单")
    add(C, "snapshot.facts[ECB_*@2026-09-16].quality_status / issue msg",
        [facts["ECB_DFR@2026-09-16"]["quality_status"], facts["ECB_MRO@2026-09-16"]["quality_status"], "68天" in facts["ECB_DFR@2026-09-16"]["issues"][0]["message"]],
        ["DEGRADED", "DEGRADED", True], facts["ECB_DFR@2026-09-16"]["quality_status"] == "DEGRADED" and facts["ECB_MRO@2026-09-16"]["quality_status"] == "DEGRADED"
        and "68天" in facts["ECB_DFR@2026-09-16"]["issues"][0]["message"], "C3②", snip="L1 事实行 quality_status=DEGRADED")
    l1 = {r_["metric_id"]: r_ for r_ in rep["layers"]["L1_事实层"]["rows"]}
    add(C, "report.json layers.L1_事实层.rows[ECB_*].quality_status", [l1["ECB_DFR"]["quality_status"], l1["ECB_MRO"]["quality_status"]],
        ["DEGRADED", "DEGRADED"], l1["ECB_DFR"]["quality_status"] == "DEGRADED" and l1["ECB_MRO"]["quality_status"] == "DEGRADED",
        "C3②", snip="L1 事实行 quality_status=DEGRADED")
    ecb_cal = [e for e in cal["entries"] if str(e.get("metric_id", "")).startswith("ECB")]
    add(C, "release_calendar.entries[metric_id startswith ECB]", len(ecb_cal), 0, len(ecb_cal) == 0, "C2/C3②",
        snip="冻结发布日历对欧央行无实录条目")
    tgt = [e for e in cal["entries"] if e.get("metric_id") == "JP_POLICY_TARGET"]
    t09 = [e for e in tgt if e.get("kind") == "policy_decision"][0]
    add(C, "release_calendar RC-JP-BOJ-TARGET-2026-09", [t09["decision_date"], t09["effective_on"], t09["target_value"], t09["basis"]],
        ["2026-09-18", "2026-09-24", 1.25, "user_directive"], t09["decision_date"] == "2026-09-18" and t09["effective_on"] == "2026-09-24"
        and t09["target_value"] == 1.25 and t09["basis"] == "user_directive", "C2/M1 step2", snip="2026-09-18 决议、2026-09-24 生效")
    mt = [e for e in tgt if e.get("kind") == "policy_maintenance"][0]
    add(C, "release_calendar RC-JP-BOJ-MAINT-2026-10", [mt["decision_date"], mt["target_value"]], ["2026-10-30", 1.25],
        mt["decision_date"] == "2026-10-30" and mt["target_value"] == 1.25, "C2/M1 step2", snip="2026-10-30 会议确认维持")
    add(C, "release_calendar JP_POLICY_TARGET entries (count)", len(tgt), 2, len(tgt) == 2, "C3③",
        note="calendar also holds 3 EA_HICP_YOY historical entries (2021M05/2022M06/2025M03) not covering the window", ctx=True,
        snip="日历实录仅覆盖日本政策目标两条")
    pend = [e for e in tgt if e.get("effective_on") and e["effective_on"] > "2026-11-23"]
    add(C, "calendar JP_POLICY_TARGET entries with effective_on > cutoff (待生效)", len(pend), 0, len(pend) == 0, "EA from_to",
        snip="均已生效")
    add(C, "2026-11-23 − 2026-09-24 (按生效日)", days("2026-09-24", "2026-11-23").days, 60, days("2026-09-24", "2026-11-23").days == 60,
        "MAP_REPORT 政策官方记录面", snip="| 日本 | 1.25 | — | 2026-09-18 | 2026-09-24 | 2026-10-30 | 2026-10-30 | 60天 | 66天 | 24天 |")
    add(C, "2026-11-23 − 2026-09-18 (按决议日)", days("2026-09-18", "2026-11-23").days, 66, days("2026-09-18", "2026-11-23").days == 66,
        "MAP_REPORT 政策官方记录面", snip="60天 | 66天 | 24天 |")
    add(C, "2026-11-23 − 2026-10-30 (距维持)", days("2026-10-30", "2026-11-23").days, 24, days("2026-10-30", "2026-11-23").days == 24,
        "MAP_REPORT 政策官方记录面", snip="66天 | 24天 |")
    add(C, "registry metric ids / snapshot series_store contain JP_POLICY_TARGET?",
        ["JP_POLICY_TARGET" in regm, "JP_POLICY_TARGET" in ss], [False, False],
        "JP_POLICY_TARGET" not in regm and "JP_POLICY_TARGET" not in ss, "C2/C3①", snip="注册表无 JP_POLICY_TARGET")
    add(C, "registry[JP_POLICY_RATE].value_type", regm["JP_POLICY_RATE"].get("value_type"), "monthly_avg_rate",
        regm["JP_POLICY_RATE"].get("value_type") == "monthly_avg_rate", "C2", snip="月均≠宣布值")
    add(C, "决议→生效 days (ECB ×2)", [days("2026-06-11", "2026-06-17").days, days("2026-09-10", "2026-09-16").days], [6, 6],
        days("2026-06-11", "2026-06-17").days == 6 and days("2026-09-10", "2026-09-16").days == 6, "MAP_REPORT 事件簇",
        snip="欧央行存款便利利率 2026-09-10→2026-09-16(+25bp)")
    add(C, "2026-09-18 (BOJ 决议) − 2026-09-16 (ECB 生效)", days("2026-09-16", "2026-09-18").days, 2,
        days("2026-09-16", "2026-09-18").days == 2, "C2 节奏对照",
        note="mixed calibre (ECB effective vs BOJ decision); like-for-like: effective↔effective=%dd, decision↔decision=%dd" % (
            days("2026-09-16", "2026-09-24").days, days("2026-09-10", "2026-09-18").days), snip="相隔两天")
    add(C, "like-for-like 2026-09-24 (BOJ 生效) − 2026-09-16 (ECB 生效)", days("2026-09-16", "2026-09-24").days, "(未述; 同口径=8天)",
        False, "C2 节奏对照", note="ctx: same-kind distance is 8 days; judgment text gives both BOJ dates so ordering is unaffected",
        ctx=True, snip="2026-09-18 决议即 2026-09-24 生效在后,相隔两天")
    for ym, a, b, snip in (("2026-06", 0.727, 0.841, "2026-06 0.727→0.841"), ("2026-07", 0.841, 0.978, "2026-07 0.841→0.978"),
                           ("2026-09", 0.977, 1.043, "2026-09 0.977→1.043"), ("2026-10", 1.043, 1.227, "2026-10 1.043→1.227")):
        y_, m_ = int(ym[:4]), int(ym[5:])
        pm = date(y_ - (1 if m_ == 1 else 0), 12 if m_ == 1 else m_ - 1, 1).strftime("%Y-%m")
        comp = [mv("JP_POLICY_RATE", pm), mv("JP_POLICY_RATE", ym)]
        add(C, f"series_store[JP_POLICY_RATE] {pm}→{ym}", comp, [a, b],
            num_ok(comp[0], a, 0.0005) and num_ok(comp[1], b, 0.0005), "M1 step2", snip=snip)
    ssum = sum([(0.841 - 0.727), (0.978 - 0.841), (1.043 - 0.977), (1.227 - 1.043)]) * 100
    add(C, "Σ four JP monthly steps ×100", r(ssum, 1), 50, num_ok(ssum, 50, 0.5), "M1 step2", snip="合计 +50bp")
    for mid in ("EA_HICP_YOY", "JP_CPI_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_RATE"):
        pp = pubmap[(mid, "2026-05-01")]
        add(C, f"no-look-ahead: {mid} obs 2026-05 presumed pub vs anchor 2026-05-23", pp.isoformat(), "> 2026-05-23 (锚取 2026-04 期)",
            pp > date(2026, 5, 23), "锚格", note="next-month reading not yet public at the 6-month anchor → anchor uses 2026-04 obs",
            snip="观测月 2026-04")
    add(C, "JP_POLICY_RATE 2026-08 (0.978→0.977 非上行台阶)", [mv("JP_POLICY_RATE", "2026-07"), mv("JP_POLICY_RATE", "2026-08")],
        [0.978, 0.977], mv("JP_POLICY_RATE", "2026-07") == 0.978 and mv("JP_POLICY_RATE", "2026-08") == 0.977, "turnings[1].narrative",
        snip="此后逐月路径 2026-08 0.977")
    jm_ = [x.strftime("%Y-%m") for x, y in zip(*ser("JP_POLICY_RATE")) if y == 1.043][0]
    add(C, "JP step month of 0.977→1.043 vs ECB effective month", [jm_, "2026-09"],
        "同月", jm_ == "2026-09", "C2 节奏对照", note="JP_POLICY_RATE obs 2026-09-01 (0.977→1.043); ECB effective 2026-09-16", snip="日本月均口径的 9 月台阶与欧央行生效日同月")
    add(C, "snapshot.facts USDJPY/SPX/VIX @2026-11-23", [facts["USDJPY@2026-11-23"]["value"], facts["SPX@2026-11-23"]["value"], facts["VIX@2026-11-23"]["value"]],
        [159.35, 7203.85, 27.01], [facts["USDJPY@2026-11-23"]["value"], facts["SPX@2026-11-23"]["value"], facts["VIX@2026-11-23"]["value"]] == [159.35, 7203.85, 27.01],
        "C2 末句", snip="USDJPY 水平为 159.35、SPX 水平为 7203.85、VIX 水平为 27.01")
    add(C, "report.json L1 rows JP_CPI_YOY / EA_HICP_YOY quality_status", [l1["JP_CPI_YOY"]["quality_status"], l1["EA_HICP_YOY"]["quality_status"]],
        ["WARN", "WARN"], l1["JP_CPI_YOY"]["quality_status"] == "WARN" and l1["EA_HICP_YOY"]["quality_status"] == "WARN", "C1",
        snip="L1 quality_status 分别为 WARN 与 WARN")
    add(C, "ECB last obs date == last change date (两序列)", [ser("ECB_DFR")[0][-1].isoformat(), ser("ECB_MRO")[0][-1].isoformat()],
        ["2026-09-16", "2026-09-16"], ser("ECB_DFR")[0][-1].isoformat() == "2026-09-16" and ser("ECB_MRO")[0][-1].isoformat() == "2026-09-16",
        "C2", snip="观测=序列变更日=生效日 2026-09-16")

    # =====================================================================
    # ⑤ 三利率分解与资产月窗
    # =====================================================================
    C = "⑤利率分解"
    trio = plan["us_rates_trio"]
    tw = trio.get("window") or {}
    tfrom, tto = tw.get("from"), tw.get("to")
    lv = {m: (at(m, tfrom), at(m, tto)) for m in ("UST_10Y", "TIPS_10Y", "BEI_10Y")}
    bp = {m: r((lv[m][1] - lv[m][0]) * 100) for m in lv}
    add(C, "series_store[UST_10Y] 2026-10-20 → 2026-11-19", lv["UST_10Y"], [5.12, 5.04], list(lv["UST_10Y"]) == [5.12, 5.04],
        "rates_decomposition", snip="十年期名义 Δ-8bp = 实际 Δ+11bp + 盈亏平衡 Δ-19bp")
    add(C, "series_store[TIPS_10Y] 2026-10-20 → 2026-11-19", lv["TIPS_10Y"], [2.77, 2.88], list(lv["TIPS_10Y"]) == [2.77, 2.88],
        "rates_decomposition")
    add(C, "series_store[BEI_10Y] 2026-10-20 → 2026-11-19", lv["BEI_10Y"], [2.35, 2.16], list(lv["BEI_10Y"]) == [2.35, 2.16],
        "rates_decomposition")
    add(C, "Δ nominal bp", bp["UST_10Y"], -8.0, num_ok(bp["UST_10Y"], -8.0, 0.5), "rates_decomposition", snip='"nominal_bp": -8.0')
    add(C, "Δ real bp", bp["TIPS_10Y"], 11.0, num_ok(bp["TIPS_10Y"], 11.0, 0.5), "rates_decomposition", snip='"real_bp": 11.0')
    add(C, "Δ breakeven bp", bp["BEI_10Y"], -19.0, num_ok(bp["BEI_10Y"], -19.0, 0.5), "rates_decomposition", snip='"bei_bp": -19.0')
    add(C, "nominal − (real + breakeven) at to-date", r((lv["UST_10Y"][1] - (lv["TIPS_10Y"][1] + lv["BEI_10Y"][1])) * 100, 1), 0,
        num_ok((lv["UST_10Y"][1] - (lv["TIPS_10Y"][1] + lv["BEI_10Y"][1])) * 100, 0, 0.05), "rates_decomposition",
        note="levels 5.04 / 2.88 / 2.16", snip="期末水平: 名义 5.04 / 实际 2.88 / 盈亏平衡 2.16")
    add(C, "Δbp identity: −8 − (11 + −19)", r(bp["UST_10Y"] - (bp["TIPS_10Y"] + bp["BEI_10Y"]), 1), 0,
        num_ok(bp["UST_10Y"] - (bp["TIPS_10Y"] + bp["BEI_10Y"]), 0, 0.05), "rates_decomposition", snip="十年期名义 Δ-8bp = 实际 Δ+11bp + 盈亏平衡 Δ-19bp")
    add(C, "trio window / calendar days", [tfrom, tto, days(tfrom, tto).days], ["2026-10-20", "2026-11-19", 30],
        [tfrom, tto, days(tfrom, tto).days] == ["2026-10-20", "2026-11-19", 30], "rates_decomposition", snip='"window_to": "2026-11-19"')
    w12 = trio.get("window_12m") or {}
    f12, t12 = w12.get("from"), w12.get("to")
    for m, rv in (("UST_10Y", 91.0), ("TIPS_10Y", 102.0), ("BEI_10Y", -11.0)):
        a0, a1 = last_le(m, f12), last_le(m, t12)
        comp = r((a1[1] - a0[1]) * 100)
        add(C, f"series_store[{m}] {a0[0].isoformat()} → {a1[0].isoformat()} (12m, ≤窗端最后观测)", comp, rv, num_ok(comp, rv, 0.5),
            "MAP_REPORT 美债三利率分解(年度窗)", note="engine chg_bp_12m", snip="十年期名义 Δ+91bp = 实际 Δ+102bp + 盈亏平衡 Δ-11bp")

    C = "⑤资产月窗"
    am = {r_["metric_id"]: r_ for r_ in plan["asset_moves"]["rows"]}
    for m, rv, snip in (("SPX", -5.51, "SPX -5.51%"), ("NIKKEI225", -9.98, "NIKKEI225 -9.98%"), ("DAX", 0.11, "DAX +0.11%"), ("VIX", 38.87, "VIX +38.87%")):
        row = am[m]
        a0 = last_le(m, row["window"]["from"])[1]
        a1 = last_le(m, row["window"]["to"])[1]
        comp = r2(pct(a0, a1))
        add(C, f"series_store[{m}] {row['window']['from']} → {row['window']['to']}", comp, rv, num_ok(comp, rv, 0.0051) and row["chg_pct"] == rv,
            "asset_returns_echo / M1 step4", note="engine row chg_pct=%s" % row["chg_pct"], snip=snip)
    echo_ok = all(any(r_["metric_id"] == e["metric_id"] and r_["chg_pct"] == e["chg_pct"] and r_["window"] == e["window"]
                      for r_ in plan["asset_moves"]["rows"]) for e in judg["reader_map"]["asset_returns_echo"])
    add(C, "reader_map.asset_returns_echo vs engine asset_moves.rows", "%d/%d" % (len(judg["reader_map"]["asset_returns_echo"]), len(judg["reader_map"]["asset_returns_echo"])),
        "4/4", echo_ok and len(judg["reader_map"]["asset_returns_echo"]) == 4, "asset_returns_echo")

    # =====================================================================
    # M1 step3 / link2: FX windows
    # =====================================================================
    C = "⑦传导·环2/3汇率"
    fx = [("EURUSD", "2026-10-23", "2026-11-20", 1.1221, 1.0970, -2.24, "EURUSD 由 1.1221 降至 1.0970(-2.24%)"),
          ("USDJPY", "2026-10-23", "2026-11-20", 156.494, 159.707, 2.05, "USDJPY 由 156.494 升至 159.707(+2.05%)"),
          ("DXY", "2026-10-23", "2026-11-20", 101.81, 103.81, 1.96, "DXY 由 101.81 升至 103.81(+1.96%)"),
          ("EURUSD", "2026-10-23", "2026-11-23", 1.1221, 1.0940, -2.51, "EURUSD 1.0940(-2.51%)"),
          ("USDJPY", "2026-10-23", "2026-11-23", 156.494, 159.347, 1.82, "USDJPY 159.347(+1.82%)"),
          ("DXY", "2026-10-23", "2026-11-23", 101.81, 104.079, 2.23, "DXY 104.079(+2.23%)")]
    for m, d0, d1, v0, v1, pc, snip in fx:
        a0, a1 = at(m, d0), at(m, d1)
        dec = 4 if m != "USDJPY" else 3
        ok0 = num_ok(r(a0, dec), v0, 0.5 * 10 ** (-dec) + 1e-12)
        dec1 = 4 if m != "USDJPY" else 3
        ok1 = num_ok(r(a1, dec1), v1, 0.5 * 10 ** (-dec1) + 1e-12)
        add(C, f"series_store[{m}] {d0} → {d1}", [a0, a1, r2(pct(a0, a1))], [v0, v1, pc],
            ok0 and ok1 and num_ok(pct(a0, a1), pc, 0.0051), "M1 step3 / link2", snip=snip)
    add(C, "direction: EURUSD Δ<0, USDJPY Δ>0, DXY Δ>0 (两口径)", [pct(at("EURUSD", "2026-10-23"), at("EURUSD", "2026-11-20")) < 0,
        pct(at("USDJPY", "2026-10-23"), at("USDJPY", "2026-11-20")) > 0, pct(at("DXY", "2026-10-23"), at("DXY", "2026-11-20")) > 0],
        [True, True, True], True, "link2", snip="两货币同对美元走弱、同向随美元指数")

    # =====================================================================
    # M1 step4 / link3: same-day-close asset window
    # =====================================================================
    C = "⑦传导·环4资产"
    for m, rv, snip in (("SPX", -9.36, "SPX 下跌 9.36%"), ("DAX", -1.50, "DAX 下跌 1.50%"), ("CAC40", 1.86, "CAC40 上涨 1.86%")):
        comp = r2(pct(at(m, "2026-10-23"), at(m, "2026-11-20")))
        add(C, f"series_store[{m}] 2026-10-23 → 2026-11-20 (同日收盘)", comp, rv, num_ok(comp, rv, 0.0051), "M1 step4 / link3", snip=snip)
    comp = r2(pct(at("NIKKEI225", "2026-10-23"), at("NIKKEI225", "2026-11-20")))
    add(C, "series_store[NIKKEI225] 2026-10-23 → 2026-11-20", comp, -9.98, num_ok(comp, -9.98, 0.0051), "M1 step4", snip="NIKKEI225 下跌 9.98%")
    comp = r2(pct(at("VIX", "2026-10-23"), at("VIX", "2026-11-20")))
    add(C, "VIX 2026-10-23 → 2026-11-20", [at("VIX", "2026-10-23"), at("VIX", "2026-11-20"), comp], [19.45, 35.89, 84.5],
        num_ok(at("VIX", "2026-10-23"), 19.45, 0.0051) and num_ok(at("VIX", "2026-11-20"), 35.89, 0.0051) and num_ok(comp, 84.5, 0.051),
        "M1 step4", snip="VIX 由 19.45 升至 35.89(+84.5%)")
    for d, rv in (("2026-11-13", 19.30), ("2026-11-16", 22.91), ("2026-11-17", 25.46), ("2026-11-18", 24.56),
                  ("2026-11-19", 28.44), ("2026-11-20", 35.89)):
        comp = at("VIX", d)
        add(C, f"series_store[VIX] {d}", comp, rv, num_ok(comp, rv, 0.0051), "M1 step4 VIX 路径", snip="11-13 19.30→11-16 22.91→11-17 25.46→11-18 24.56→11-19 28.44→11-20 35.89")
    comp = r2(pct(at("VIX", "2026-11-20"), at("VIX", "2026-11-23")))
    add(C, "VIX 2026-11-20 close → 2026-11-23 snapshot", comp, -24.7, num_ok(comp, -24.7, 0.051), "M1 step4 / link3", snip="-24.7%")
    add(C, "2026-11-13 − 2026-10-30", days("2026-10-30", "2026-11-13").days, 14, days("2026-10-30", "2026-11-13").days == 14,
        "link3 verdict_note", snip="14 天")
    add(C, "2026-11-13 − 2026-09-16", days("2026-09-16", "2026-11-13").days, 58, days("2026-09-16", "2026-11-13").days == 58,
        "link3 verdict_note", snip="58 天")
    vd = ser("VIX")[0]
    n5 = len([x for x in vd if date(2026, 11, 13) < x <= date(2026, 11, 20)])
    add(C, "VIX closes strictly after 2026-11-13 up to 2026-11-20", n5, 5, n5 == 5, "M1 step4", snip="跳升集中于末五个交易日")

    # =====================================================================
    # monthly paths
    # =====================================================================
    C = "⑬窗·逐月路径/转折"
    ea = {ym: mv("EA_HICP_YOY", ym) for ym in ("2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10")}
    jp = {ym: mv("JP_CPI_YOY", ym) for ym in ea}
    for (ym, rv) in (("2026-05", 3.2), ("2026-06", 2.8), ("2026-07", 2.9), ("2026-08", 3.2), ("2026-09", 3.8), ("2026-10", 4.0)):
        add(C, f"series_store[EA_HICP_YOY] {ym}", ea[ym], rv, num_ok(ea[ym], rv, 0.0501), "M1 step1 / EA from_to", snip="3.2(2026-05)→2.8(2026-06)→2.9(2026-07)→3.2(2026-08)→3.8(2026-09)→4.0(2026-10)")
    for (ym, rv) in (("2026-05", 1.53), ("2026-06", 1.67), ("2026-07", 1.97), ("2026-08", 1.98), ("2026-09", 2.16), ("2026-10", 2.44)):
        add(C, f"series_store[JP_CPI_YOY] {ym}", jp[ym], rv, num_ok(jp[ym], rv, 0.0051), "M1 step1 / JP from_to", snip="1.53(2026-05)→1.67(2026-06)→1.97(2026-07)→1.98(2026-08)→2.16(2026-09)→2.44(2026-10)")
    gaps = {ym: r2(ea[ym] - jp[ym]) for ym in ea}
    add(C, "min/max of (EA − JP) 2026-05..2026-10", [min(gaps.values()), max(gaps.values())], [0.93, 1.67],
        min(gaps.values()) == 0.93 and max(gaps.values()) == 1.67, "M1 step1", note="gaps=%s" % gaps, snip="0.93-1.67 个百分点")
    add(C, "EA 2026-06 < 2026-05 (非逐月单调)", ea["2026-06"] < ea["2026-05"], True, ea["2026-06"] < ea["2026-05"], "M1 step1", snip="非逐月单调")
    jv = [jp[k] for k in sorted(jp)]
    add(C, "JP 2026-05..2026-10 strictly increasing", all(jv[i] < jv[i + 1] for i in range(len(jv) - 1)), True,
        all(jv[i] < jv[i + 1] for i in range(len(jv) - 1)), "M1 step1", snip="日本逐月上行")
    add(C, "JP_CPI_YOY 2026-09 − EA_HICP_YOY 2026-09", r2(jp["2026-09"] - ea["2026-09"]), -1.64, num_ok(jp["2026-09"] - ea["2026-09"], -1.64, 0.0051),
        "turnings[2].narrative", snip="全国口径 -1.64")
    add(C, "JP_CPI_TOKYO_YOY 2026-09 − EA_HICP_YOY 2026-09", r2(mv("JP_CPI_TOKYO_YOY", "2026-09") - ea["2026-09"]), -1.11,
        num_ok(mv("JP_CPI_TOKYO_YOY", "2026-09") - ea["2026-09"], -1.11, 0.0051), "turnings[2].narrative", snip="东京口径 -1.11")
    ead, eav = ser("EA_HICP_YOY")
    last12 = eav[-12:]
    add(C, "EA_HICP_YOY last obs == max(last 12 obs)", [eav[-1], max(last12)], [4.0, 4.0], eav[-1] == max(last12) == 4.0, "EA from_to",
        snip="最新读数为近十二个月最高")
    jpd, jpv = ser("JP_CPI_YOY")
    seg = [(x, y) for x, y in zip(jpd, jpv) if x >= date(2025, 1, 1)]
    add(C, "JP_CPI_YOY max over 2025-01..latest", [max(seg, key=lambda t: t[1])[0].strftime("%Y-%m"), max(y for _, y in seg)], ["2025-01", 4.03],
        max(seg, key=lambda t: t[1])[0].strftime("%Y-%m") == "2025-01" and max(y for _, y in seg) == 4.03, "JP from_to", snip="自 2025-01 高点 4.03")
    add(C, "JP_CPI_YOY min over 2025-01..latest", [min(seg, key=lambda t: t[1])[0].strftime("%Y-%m"), min(y for _, y in seg)], ["2026-02", 1.27],
        min(seg, key=lambda t: t[1])[0].strftime("%Y-%m") == "2026-02" and min(y for _, y in seg) == 1.27, "JP from_to", snip="2026-02 的 1.27")
    seg2 = [y for x, y in zip(jpd, jpv) if date(2025, 1, 1) <= x <= date(2026, 2, 1)]
    mono = all(seg2[i] >= seg2[i + 1] for i in range(len(seg2) - 1))
    add(C, "JP_CPI_YOY 2025-01→2026-02 monotonic non-increasing?", mono, "「持续回落」(隐含单调)", mono, "JP from_to",
        note="ctx: upticks strictly inside the decline (2025-01→2026-02) at %s" % [jpd[i].strftime("%Y-%m") for i in range(1, len(jpd)) if date(2025, 1, 1) < jpd[i] <= date(2026, 2, 1) and jpv[i] > jpv[i - 1]],
        ctx=True, snip="持续回落至 2026-02 的 1.27")
    add(C, "Tokyo 2026-10 > 2026-09 and national 2026-10 > 2026-09", [mv("JP_CPI_TOKYO_YOY", "2026-10") > mv("JP_CPI_TOKYO_YOY", "2026-09"),
        jp["2026-10"] > jp["2026-09"]], [True, True], mv("JP_CPI_TOKYO_YOY", "2026-10") > mv("JP_CPI_TOKYO_YOY", "2026-09") and jp["2026-10"] > jp["2026-09"],
        "C1", snip="同月两者均较前月上行")
    add(C, "EA 2026-01 / 2026-02 / 2026-05", [mv("EA_HICP_YOY", "2026-01"), mv("EA_HICP_YOY", "2026-02"), mv("EA_HICP_YOY", "2026-05")], [1.7, 1.9, 3.2],
        [mv("EA_HICP_YOY", "2026-01"), mv("EA_HICP_YOY", "2026-02"), mv("EA_HICP_YOY", "2026-05")] == [1.7, 1.9, 3.2], "turnings[0]", snip="由 1.9 升至 3.2(三个月 +1.30 个百分点)")
    add(C, "EA 2026-05 − 2026-02", r2(mv("EA_HICP_YOY", "2026-05") - mv("EA_HICP_YOY", "2026-02")), 1.30,
        num_ok(mv("EA_HICP_YOY", "2026-05") - mv("EA_HICP_YOY", "2026-02"), 1.30, 0.0051), "turnings[0]", snip="+1.30 个百分点")
    add(C, "EA trough month over 2025-01..latest", min([(x, y) for x, y in zip(ead, eav) if x >= date(2025, 1, 1)], key=lambda t: t[1])[0].strftime("%Y-%m"),
        "2026-01", min([(x, y) for x, y in zip(ead, eav) if x >= date(2025, 1, 1)], key=lambda t: t[1])[0].strftime("%Y-%m") == "2026-01",
        "turnings[0].follow_or_diverge", snip="两地谷底分别在欧元区 2026-01 的 1.7")
    add(C, "JP 2026-02 → 2026-05", [mv("JP_CPI_YOY", "2026-02"), mv("JP_CPI_YOY", "2026-05")], [1.27, 1.53],
        [mv("JP_CPI_YOY", "2026-02"), mv("JP_CPI_YOY", "2026-05")] == [1.27, 1.53], "turnings[0].follow_or_diverge", snip="2026-02 1.27→2026-05 1.53")
    add(C, "JP_POLICY_RATE 2026-04 / 2026-06 / 2026-07", [mv("JP_POLICY_RATE", "2026-04"), mv("JP_POLICY_RATE", "2026-06"), mv("JP_POLICY_RATE", "2026-07")],
        [0.727, 0.841, 0.978], [mv("JP_POLICY_RATE", "2026-04"), mv("JP_POLICY_RATE", "2026-06"), mv("JP_POLICY_RATE", "2026-07")] == [0.727, 0.841, 0.978],
        "turnings[1]", snip="2026-04 0.727→2026-07 0.978(经 2026-06 0.841 过渡)")
    add(C, "Tokyo 2026-06 → 2026-09 (Δ)", [mv("JP_CPI_TOKYO_YOY", "2026-06"), mv("JP_CPI_TOKYO_YOY", "2026-09"),
        r2(mv("JP_CPI_TOKYO_YOY", "2026-09") - mv("JP_CPI_TOKYO_YOY", "2026-06"))], [1.6, 2.69, 1.09],
        [mv("JP_CPI_TOKYO_YOY", "2026-06"), mv("JP_CPI_TOKYO_YOY", "2026-09")] == [1.6, 2.69] and num_ok(mv("JP_CPI_TOKYO_YOY", "2026-09") - mv("JP_CPI_TOKYO_YOY", "2026-06"), 1.09, 0.0051),
        "turnings[2]", snip="由 1.6 升至 2.69(三个月 +1.09 个百分点)")
    add(C, "JP_CPI_YOY 2026-06 → 2026-08", [jp["2026-06"], jp["2026-08"]], [1.67, 1.98], [jp["2026-06"], jp["2026-08"]] == [1.67, 1.98],
        "turnings[2].narrative", snip="全国 2026-06 1.67→2026-08 1.98")
    add(C, "monthly obs strictly inside window 2026-05-23..2026-11-23 (EA/JP/Tokyo/JP_POLICY_RATE)",
        [len([x for x in ser(m)[0] if date(2026, 5, 23) <= x <= CUT]) for m in ("EA_HICP_YOY", "JP_CPI_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_RATE")],
        "6 值(2026-05..2026-10)称「窗内」(观测日在窗内=5)",
        False, "M1 step1 (\"窗内 2026-05..2026-10 月度值\")",
        note="ctx/NIT: by observation date 2026-05-01 lies before window start 2026-05-23 (only its presumed publication 06-05..06-20 falls inside); engine n_in_window=5 (2026-06..2026-10); 月份已在括号内写明,无数值影响", ctx=True,
        snip="窗内(2026-05..2026-10 月度值)")

    # =====================================================================
    # publication (presumed rule) dates & visibility
    # =====================================================================
    C = "①④公布日·可见性"
    for mid, obs, rv, snip in (("EA_HICP_YOY", "2026-04-01", "2026-05-16", "发布 2026-05-16"), ("EA_HICP_YOY", "2026-10-01", "2026-11-16", "发布 2026-11-16"),
                                ("JP_CPI_YOY", "2026-04-01", "2026-05-20", "发布 2026-05-20"), ("JP_CPI_YOY", "2026-10-01", "2026-11-20", "发布 2026-11-20"),
                                ("JP_CPI_TOKYO_YOY", "2026-10-01", "2026-10-30", "发布 2026-10-30"), ("JP_CPI_TOKYO_YOY", "2026-04-01", "2026-04-29", "2026-04-29"),
                                ("JP_CPI_TOKYO_YOY", "2026-09-01", "2026-09-29", "2026-09-29"), ("JP_CPI_TOKYO_YOY", "2026-08-01", "2026-08-30", "2026-08-30"),
                                ("JP_POLICY_RATE", "2026-10-01", "2026-11-05", "发布 2026-11-05"), ("JP_POLICY_RATE", "2026-04-01", "2026-05-05", "发布 2026-05-05")):
        comp = pub(obs, RULE[mid]).isoformat()
        add(C, f"month_end({obs[:7]}) + rule {RULE[mid]}", comp, rv, comp == rv, "C1/C2/regions", snip=snip)
    add(C, "2026-11-20 − 2026-11-16", days("2026-11-16", "2026-11-20").days, 4, days("2026-11-16", "2026-11-20").days == 4, "C1", snip="公布时间相差四天")

    def visible(mid, d):
        k = date.fromisoformat(d) if isinstance(d, str) else d
        best = None
        for (m_, o), p in pubmap.items():
            if m_ == mid and p <= k and (best is None or o > best[0]):
                best = (o, mv(mid, o[:7]))
        return best

    for mid, d, rv, snip, strict in (("EA_HICP_YOY", "2026-06-11", ["2026-04-01", 3.0], "决议日(回推 2026-06-11)前可见 2026-04=3.0", True),
                                     ("EA_HICP_YOY", "2026-06-17", ["2026-05-01", 3.2], "生效日前可见 2026-05=3.2", True),
                                     ("EA_HICP_YOY", "2026-09-10", ["2026-07-01", 2.9], "决议日(回推 2026-09-10)前可见 2026-07=2.9", True),
                                     ("EA_HICP_YOY", "2026-09-16", ["2026-08-01", 3.2], "生效日前可见 2026-08=3.2", False),
                                     ("JP_CPI_YOY", "2026-09-18", ["2026-07-01", 1.97], "决议前可见全国读数 2026-07 的 1.97", True),
                                     ("JP_CPI_TOKYO_YOY", "2026-09-18", ["2026-08-01", 1.9], "东京读数 2026-08 的 1.9", True)):
        v_ = visible(mid, d)
        comp = [v_[0], v_[1]]
        ok = comp == rv and (not strict or pubmap[(mid, v_[0])] < date.fromisoformat(d) or (strict and pubmap[(mid, v_[0])] < date.fromisoformat(d)))
        if strict:
            ok = comp == rv and pubmap[(mid, v_[0])] < date.fromisoformat(d)
        else:
            ok = comp == rv and pubmap[(mid, v_[0])] <= date.fromisoformat(d)
        add(C, f"last {mid} obs with presumed pub {'<' if strict else '≤'} {d}", comp, rv, ok, "link1 main_predicts/verdict_note",
            note="pub=%s" % pubmap[(mid, v_[0])].isoformat(), snip=snip)
    add(C, "presumed pub of EA 2026-08 obs", pubmap[("EA_HICP_YOY", "2026-08-01")].isoformat(), "2026-09-16",
        pubmap[("EA_HICP_YOY", "2026-08-01")].isoformat() == "2026-09-16", "link1", snip="发布日 2026-09-16 与生效日同日")
    add(C, "min(readings visible before each ECB change) > EA 2026-02 (1.9)", min(3.0, 3.2, 2.9, 3.2) > mv("EA_HICP_YOY", "2026-02"), True,
        min(3.0, 3.2, 2.9, 3.2) > mv("EA_HICP_YOY", "2026-02"), "link1 verdict_note", snip="两次变更前读数均高于 2026-02 的 1.9")
    add(C, "EA 2026-01 → 2026-04", [mv("EA_HICP_YOY", "2026-01"), mv("EA_HICP_YOY", "2026-04")], [1.7, 3.0],
        [mv("EA_HICP_YOY", "2026-01"), mv("EA_HICP_YOY", "2026-04")] == [1.7, 3.0], "link1 verdict_note", snip="由 2026-01 的 1.7 升至 2026-04 的 3.0")
    add(C, "EA max over 2026-01..2026-07 / value at 2026-05", [max(ea["2026-05"], mv("EA_HICP_YOY", "2026-01"), mv("EA_HICP_YOY", "2026-02"), mv("EA_HICP_YOY", "2026-03"), mv("EA_HICP_YOY", "2026-04"), ea["2026-06"], ea["2026-07"]), ea["2026-05"]],
        [3.2, 3.2], max([mv("EA_HICP_YOY", "2026-0%d" % i) for i in range(1, 8)]) == 3.2 == ea["2026-05"] and 2.9 < 3.2, "link1 verdict_note",
        snip="低于 2026-05 峰值 3.2")

    # =====================================================================
    # ⑨ 情景
    # =====================================================================
    C = "⑨情景"
    ea12 = pub(date(2026, 12, 1), "me+16")
    jp12 = pub(date(2026, 12, 1), "me+20")
    add(C, "presumed pub of 2026-12 obs (EA me+16 / JP me+20)", [ea12.isoformat(), jp12.isoformat()], "<2027-02-15",
        ea12 < date(2027, 2, 15) and jp12 < date(2027, 2, 15) and ea12.year == 2027 and ea12.month == 1, "l4.scenarios",
        snip="读数按引擎发布规则于 2027-01 入档,早于时限 2027-02-15")
    add(C, "EA latest vs S1 前提 3.5%", mv("EA_HICP_YOY", "2026-10"), "≥3.5", mv("EA_HICP_YOY", "2026-10") >= 3.5, "S1",
        note="premise compatible with cutoff; 2026-11/2026-12 obs not yet published at cutoff → not already triggered", snip="维持 3.5% 以上")
    add(C, "EA latest vs S2 前提 (<3.0)", mv("EA_HICP_YOY", "2026-10"), "not yet <3.0", not (mv("EA_HICP_YOY", "2026-10") < 3.0), "S2",
        snip="回落至 3.0% 以下")
    add(C, "JP latest vs S1 前提 (≥2.0) / S2 (<2.0)", [mv("JP_CPI_YOY", "2026-10") >= 2.0, not (mv("JP_CPI_YOY", "2026-10") < 2.0)], [True, True],
        mv("JP_CPI_YOY", "2026-10") >= 2.0 and not (mv("JP_CPI_YOY", "2026-10") < 2.0), "S1/S2", snip="日本全国 CPI 同比维持 2.0% 以上")
    add(C, "gap at cutoff vs S1 前提 (≥1.5)", r2(gap), "≥1.5", gap >= 1.5, "S1", snip="维持 1.5 个百分点或以上")
    add(C, "S1 trigger level-conditions at cutoff (EA≥4.0 / gap≥1.5 / VIX close>30) on latest available readings",
        [mv("EA_HICP_YOY", "2026-10") >= 4.0, r2(gap) >= 1.5, at("VIX", "2026-11-20") > 30], "trigger binds to 2026-11/2026-12 readings (unpublished at cutoff)",
        False, "S1/S2", note="ctx: all three level conditions already hold on 2026-10 readings + 2026-11-20 close; the trigger is formally tied to unpublished 2026-11/2026-12 readings → still 待验证, but a no-change path would fire it (persistence scenario by design)",
        ctx=True, snip="观测月 2026-11 或 2026-12 的 EA_HICP_YOY 同比 ≥4.0%")
    add(C, "distinguishing/falsification metrics in registry", [m in regm for m in ("EA_HICP_YOY", "JP_CPI_YOY", "VIX", "EURUSD")], [True] * 4,
        all(m in regm for m in ("EA_HICP_YOY", "JP_CPI_YOY", "VIX", "EURUSD")), "l4", snip="证伪指标(EA_HICP_YOY/JP_CPI_YOY)在册可观测")
    s1, s2 = judg["l4"]["scenarios"]
    add(C, "two scenarios direction-complementary (S1 维持 vs S2 回落)", ["维持 3.5% 以上" in s1["rows"]["scenario"] and "回落至 3.0% 以下" in s2["rows"]["scenario"],
        "2.0% 以上" in s1["rows"]["scenario"] and "2.0% 以下" in s2["rows"]["scenario"]], [True, True],
        "维持 3.5% 以上" in s1["rows"]["scenario"] and "回落至 3.0% 以下" in s2["rows"]["scenario"] and "2.0% 以上" in s1["rows"]["scenario"] and "2.0% 以下" in s2["rows"]["scenario"],
        "l4.scenarios", snip="两情景方向互补")
    s1f = s1["rows"]["falsification"]["threshold"]
    add(C, "S1: all three numeric scenario components present in falsification threshold",
        [x in s1f for x in ("3.5%", "2.0%", "水平差")], [True, True, True], all(x in s1f for x in ("3.5%", "2.0%", "水平差")),
        "l4 S1", snip="或两月两地水平差(欧元区减日本)均低于 1.5 个百分点")
    add(C, "scenario deadlines equal and after presumed archival of 2026-12 readings", [s1["rows"]["trigger"]["deadline"], s2["rows"]["trigger"]["deadline"]],
        ["2027-02-15", "2027-02-15"], s1["rows"]["trigger"]["deadline"] == s2["rows"]["trigger"]["deadline"] == "2027-02-15" and jp12 < date(2027, 2, 15),
        "l4.scenarios", snip="(期限 2027-02-15)")
    add(C, "S2 trigger: each below 2026-11 observation month (requires 2026-11 reading, unpublished at cutoff)", "较 2026-11 观测月回落" in s2["rows"]["trigger"]["condition"],
        "not determinable at cutoff", True, "l4 S2", note="2026-11 readings presumed pub 2026-12-16(EA)/2026-12-20(JP) > cutoff → trigger not yet determinable", snip="各自较 2026-11 观测月回落")
    add(C, "S2: which scenario components appear in trigger / falsification",
        {"scenario_components": ["EA<3.0", "JP<2.0", "gap≤1.0"],
         "trigger_has": [x for x in ("低于 3.0%", "低于 2.0%", "水平差") if x in s2["rows"]["trigger"]["condition"]],
         "falsification_has": [x for x in ("3.5%", "日本", "水平差") if x in s2["rows"]["falsification"]["threshold"]]},
        "S1: 三分量在证伪阈值中齐全", False, "l4 S2",
        note="ctx/MINOR: S2 证伪阈值只覆盖 EA 分量(两月均≥3.5%);日本<2.0% 与水平差≤1.0pp 两分量既不在触发条件(仅 EA<3.0% 且 JP<2.0%;无水平差)也无对应证伪——与 S1 不对称", ctx=True,
        snip="若观测月 2026-11 与 2026-12 两月 EA_HICP_YOY 同比均不低于 3.5%(未回落)")

    # =====================================================================
    # ⑪ 诚实缺席
    # =====================================================================
    C = "⑪诚实缺席"
    add(C, "snapshot.gate_a.noncore_missing ∋ JP_CPI_TOKYO_YOY", "JP_CPI_TOKYO_YOY" in ga["noncore_missing"], True,
        "JP_CPI_TOKYO_YOY" in ga["noncore_missing"], "C1/JP from_to", snip="Gate A 列于 noncore_missing")
    add(C, "snapshot.gate_a.noncore_missing_detail[JP_CPI_TOKYO_YOY]", "来源文件在场而指标缺席" in ga["noncore_missing_detail"]["JP_CPI_TOKYO_YOY"], True,
        "来源文件在场而指标缺席" in ga["noncore_missing_detail"]["JP_CPI_TOKYO_YOY"], "C1", snip="来源文件在场而指标缺席")
    add(C, "snapshot.facts with metric_id JP_CPI_TOKYO_YOY (count)", len([f_ for f_ in snap["facts"] if f_["metric_id"] == "JP_CPI_TOKYO_YOY"]), 0,
        len([f_ for f_ in snap["facts"] if f_["metric_id"] == "JP_CPI_TOKYO_YOY"]) == 0, "C1", snip="L1 无对应事实行")
    add(C, "report.json L1 rows with metric_id JP_CPI_TOKYO_YOY (count)", len([r_ for r_ in rep["layers"]["L1_事实层"]["rows"] if r_["metric_id"] == "JP_CPI_TOKYO_YOY"]), 0,
        len([r_ for r_ in rep["layers"]["L1_事实层"]["rows"] if r_["metric_id"] == "JP_CPI_TOKYO_YOY"]) == 0, "C1", snip="L1 无对应事实行")
    add(C, "snapshot.gate_a.noncore_missing ⊇ {EA_REAL_GDP_YOY, JP_REAL_GDP_YOY}", [m in ga["noncore_missing"] for m in ("EA_REAL_GDP_YOY", "JP_REAL_GDP_YOY")],
        [True, True], all(m in ga["noncore_missing"] for m in ("EA_REAL_GDP_YOY", "JP_REAL_GDP_YOY")), "C3⑤",
        snip="EA_REAL_GDP_YOY、JP_REAL_GDP_YOY 在册但列于快照缺席名单")
    gdp = {m: (ser(m)[0][-1].isoformat(), ser(m)[1][-1], len(ser(m)[0])) for m in ("EA_REAL_GDP_YOY", "JP_REAL_GDP_YOY")}
    add(C, "series_store[EA/JP_REAL_GDP_YOY] last obs / value / n", gdp, "序列在场(至 2026-07-01)",
        all(v[0] == "2026-07-01" for v in gdp.values()), "C3⑤",
        note="ctx: series ARE present in series_store (facts absent / Gate A noncore_missing) — gap is at fact level, not series level", ctx=True,
        snip="两地「政策环境」无法对照增长背景")
    ids_by = {}
    for m in reg["metrics"]:
        ids_by.setdefault(m.get("economy"), []).append(m.get("metric_id") or m.get("id"))
    core = [i for e in ("JP", "EA") for i in ids_by.get(e, []) if "CORE" in str(i).upper()]
    add(C, "registry economy=JP/EA ids containing CORE", core, [], core == [], "C3⑤/C1 competing",
        note="JP=%s; EA=%s" % (sorted(ids_by.get("JP", [])), sorted(ids_by.get("EA", []))), snip="注册表亦无两地核心通胀序列")
    infl = sorted([i for e in ("JP", "EA") for i in ids_by.get(e, []) if "CPI" in i or "HICP" in i])
    add(C, "registry JP/EA headline inflation ids", infl, ["EA_HICP_YOY", "JP_CPI_TOKYO_YOY", "JP_CPI_YOY"],
        infl == ["EA_HICP_YOY", "JP_CPI_TOKYO_YOY", "JP_CPI_YOY"], "C1 competing", snip="JP_CPI_YOY/JP_CPI_TOKYO_YOY/EA_HICP_YOY")
    add(C, "snapshot.gate_a.status", ga["status"], "DEGRADED", ga["status"] == "DEGRADED", "headline", snip="Gate A 列 degraded")
    add(C, "ECB obs strictly after 2026-09-16 (two series)", [len([x for x in ser(m)[0] if x > date(2026, 9, 16)]) for m in ("ECB_DFR", "ECB_MRO")],
        [0, 0], all(len([x for x in ser(m)[0] if x > date(2026, 9, 16)]) == 0 for m in ("ECB_DFR", "ECB_MRO")), "C3②",
        snip="2026-09-17 至研究截止 2026-11-23 间")
    dg = plan.get("dimension_gaps") or []
    add(C, "report.json research_plan.dimension_gaps", [(d_["metric_id"], d_["gap"]) for d_ in dg], [("JP_POLICY_TARGET", "registry_absent")],
        [(d_["metric_id"], d_["gap"]) for d_ in dg] == [("JP_POLICY_TARGET", "registry_absent")], "C3①/MAP_REPORT 缺数格说明",
        snip="JP_POLICY_TARGET 不在注册表")
    dr = run.get("data_requirements") or {}
    gaps_req = [(i_["metric_id"], i_.get("outcome")) for i_ in dr.get("items", [])]
    add(C, "report.json run.data_requirements.items outcome", gaps_req, "ECB_MRO/ECB_DFR = insufficient_coverage",
        dict(gaps_req).get("ECB_MRO") == "insufficient_coverage" and dict(gaps_req).get("ECB_DFR") == "insufficient_coverage",
        "C3②", note="gaps=%s" % json.dumps(dr.get("gaps"), ensure_ascii=False)[:400], snip="Gate A 列 degraded")
    _c1 = "该格以「数据不可得」呈现" in map_txt
    add(C, "MAP_REPORT/report.md: absent cell rendered as 数据不可得 (not 无变化)", _c1, True, _c1, "MAP_REPORT 缺数格说明",
        note="report.md 亦载「JP_POLICY_TARGET … 该格以「数据不可得」呈现…不以相邻口径冒充」", snip="不以相邻口径冒充")
    _c2 = ("发布日历实录" in judg_txt) and ("目标 1.227" not in judg_txt) and ("目标约 1.227" not in judg_txt) and ("月均≠宣布值" in judg_txt)
    add(C, "judgment: BOJ target 1.25 attributed to calendar; JP_POLICY_RATE never called 宣布值", _c2, True, _c2, "C2", snip="月均≠宣布值")

    # =====================================================================
    # ⑫ 截止日当日日频观测
    # =====================================================================
    C = "⑫截止日盘中"
    try:
        from zoneinfo import ZoneInfo
        dt = datetime.fromisoformat(asof)
        tz = {k: dt.astimezone(ZoneInfo(v)).strftime("%H:%M") for k, v in (("纽约", "America/New_York"), ("柏林", "Europe/Berlin"), ("东京", "Asia/Tokyo"), ("上海", "Asia/Shanghai"))}
    except Exception as ex:  # pragma: no cover
        tz = {"error": repr(ex)}
    add(C, "snapshot.research_as_of → zoneinfo local times", tz, {"纽约": "09:53", "柏林": "15:53", "东京": "23:53", "上海": "22:53"},
        tz == {"纽约": "09:53", "柏林": "15:53", "东京": "23:53", "上海": "22:53"}, "quality_gate_notes",
        snip="纽约 09:53、柏林 15:53、东京 23:53、上海 22:53")
    add(C, "snapshot.facts[*].observation_date == cutoff for SPX/VIX/DAX/CAC40/EURUSD/USDJPY/DXY",
        [facts["%s@2026-11-23" % m]["observation_date"] for m in ("SPX", "VIX", "DAX", "CAC40", "EURUSD", "USDJPY", "DXY")], ["2026-11-23"] * 7,
        all(facts["%s@2026-11-23" % m]["observation_date"] == "2026-11-23" for m in ("SPX", "VIX", "DAX", "CAC40", "EURUSD", "USDJPY", "DXY")) and "盘中" in judg_txt,
        "quality_gate_notes", snip="均为盘中快照、非收盘价")
    add(C, "series_store[NIKKEI225] last obs", ser("NIKKEI225")[0][-1].isoformat(), "2026-11-20", ser("NIKKEI225")[0][-1].isoformat() == "2026-11-20",
        "M1 step4", note="no 2026-11-23 observation for NIKKEI225 → cutoff-day cross-region comparison anchored on 2026-11-20 close", snip="56436.65,2026-11-20 收盘")

    # =====================================================================
    # ⑬ 契约验证 non-VERIFIED
    # =====================================================================
    C = "⑬契约"
    cv = rep["agent_judgment"]["contract_verification"]
    verd = [v for v in (cv.get("verdicts") or cv.get("items") or []) if isinstance(v, dict) and v.get("value") is not None]
    nonv = [(v.get("metric_id") or v.get("metric"), v.get("value"), v.get("status")) for v in verd if v.get("status") != "VERIFIED"]
    add(C, "report.json agent_judgment.contract_verification verdicts with status≠VERIFIED", nonv, [("ECB_DFR", 2.5, "STALE")],
        nonv == [("ECB_DFR", 2.5, "STALE")], "C3②/headline", note="n numeric verdicts=%d" % len(verd), snip="欧央行序列止于 2026-09-16(距截止 六十八 天,Gate A 列 degraded)")
    if verd:
        st = [v for v in verd if v.get("status") == "STALE"][0]
        add(C, "STALE item value == expected (value right, freshness stale)", st.get("value") == st.get("expected") == 2.5, True,
            st.get("value") == st.get("expected") == 2.5, "C3②", note="note=%s" % st.get("note"), snip="DFR 二点五")
    six = cv.get("six_checks") or []
    mapc = cv.get("map_checks") or []
    st_all = [x.get("status") for x in six + mapc]
    add(C, "contract_verification six_checks + map_checks statuses", sorted(set(st_all)), ["VERIFIED"], st_all and set(st_all) == {"VERIFIED"},
        "全档", note="date_order note=%s" % next((x.get("note") for x in mapc if "date_order" in str(x.get("item"))), None), snip="2026-09-29 晚于 BOJ 决议日 2026-09-18")
    add(C, "contract_verification.verdict / stats", [cv.get("verdict"), cv.get("stats", {}).get("checks"), cv.get("stats", {}).get("contradicted")],
        ["VERIFIED", 5, 0], [cv.get("verdict"), cv.get("stats", {}).get("checks"), cv.get("stats", {}).get("contradicted")] == ["VERIFIED", 5, 0], "report.json")

    # =====================================================================
    # ⑬' 最近六个月窗口
    # =====================================================================
    C = "⑬'窗口"
    ad = plan["as_of_declared"]
    add(C, "month_end(2026-11)", month_end(2026, 11).isoformat(), "2026-11-30", month_end(2026, 11).isoformat() == "2026-11-30",
        "agent_declaration.basis", snip="问句请求月末 2026-11-30 未到")
    add(C, "report.json as_of_declared", [ad["requested_as_of"], ad["clamped_to_coverage"], ad["coverage_date"]], ["2026-11-30", True, "2026-11-23"],
        [ad["requested_as_of"], ad["clamped_to_coverage"], ad["coverage_date"]] == ["2026-11-30", True, "2026-11-23"], "headline", snip="非请求月末的完整结果")
    add(C, "coverage_date == snapshot research_as_of date", ad["coverage_date"] == asof[:10], True, ad["coverage_date"] == asof[:10], "headline",
        snip="研究截止取实际覆盖日 2026-11-23")
    ww = plan["question_window"]["windows"][0]
    add(C, "report.json question_window", [ww["from"], ww["to"]], ["2026-05-23", "2026-11-23"], [ww["from"], ww["to"]] == ["2026-05-23", "2026-11-23"],
        "headline", snip="2026-05-23..2026-11-23")

    # =====================================================================
    # ⑦ 传导链 / ⑧ 类比 / 证据引用 / 对质表
    # =====================================================================
    C = "⑦⑧引用/类比/工单面"
    refs = []
    for c in judg["l3"]["contradictions"]:
        refs += c.get("evidence_refs", [])
    for ch in judg["l3"]["mechanism_chains"]:
        for lk in ch["links"]:
            refs += lk.get("evidence_refs", [])
    evrefs = {e["ref"] for e in ev}
    add(C, "l3 evidence_refs count / all resolve to evidence_index", [len(refs), all(r_ in evrefs for r_ in refs)], [21, True],
        len(refs) == 21 and all(r_ in evrefs for r_ in refs), "quality_gate_notes[0]", snip="共 21 条 snapshot_fact 引用")
    s6 = [s for s in rep["steps"] if (s.get("name") or s.get("step")) == "S6_analog"][0]["envelope"]["data"]
    add(C, "steps[S6_analog].envelope.data.candidates.scanned", s6["candidates"]["scanned"], 1871, s6["candidates"]["scanned"] == 1871, "history_zero_case_note",
        snip="扫描 1871 个候选月")
    add(C, "steps[S6_analog]…candidates.valid", s6["candidates"]["valid"], 74, s6["candidates"]["valid"] == 74, "history_zero_case_note", snip="有效 74")
    add(C, "steps[S6_analog]…top[0].candidate_month", s6["top"][0]["candidate_month"], "2025-03", s6["top"][0]["candidate_month"] == "2025-03",
        "history_zero_case_note", snip="TOP1 候选月 2025-03")
    add(C, "steps[S6_analog]…top[0].distance", r3(s6["top"][0]["distance"]), 0.727, num_ok(s6["top"][0]["distance"], 0.727, 0.0005), "history_zero_case_note",
        snip="距离 0.727")
    add(C, "len(history_periods) / history_zero_case_note present", [len(judg["reader_map"]["history_periods"]), bool(judg["reader_map"].get("history_zero_case_note"))],
        [0, True], len(judg["reader_map"]["history_periods"]) == 0 and bool(judg["reader_map"].get("history_zero_case_note")), "reader_map", snip="历史类比 0 段")
    add(C, "len(evidence_index.json)", len(ev), 60, len(ev) == 60, "agent_declaration.basis", snip="证据索引(60行)")
    C = "⑩对质表/标注"
    fo = [lk["face_off_verdict"] for lk in judg["reader_map"]["transmission"][0]["links"]]
    add(C, "transmission links face_off_verdict tally", [fo.count("支持主解释"), fo.count("支持竞争解释"), fo.count("尚不能区分")], [0, 1, 2],
        [fo.count("支持主解释"), fo.count("支持竞争解释"), fo.count("尚不能区分")] == [0, 1, 2], "quality_gate_notes[1]",
        snip="支持主解释 0·支持竞争解释 1·尚不能区分 2")
    add(C, "competing_explanations per contradiction", [len(c["competing_explanations"]) for c in judg["l3"]["contradictions"]], [2, 2, 2],
        [len(c["competing_explanations"]) for c in judg["l3"]["contradictions"]] == [2, 2, 2], "l3", snip="每条矛盾陈述并列 2 条")
    lv_ = [lk["evidence_level"] for lk in judg["l3"]["mechanism_chains"][0]["links"]]
    has_hyp = ["【假设】" in (lk["text"] + str(lk.get("missing_link_note") or "")) for lk in judg["l3"]["mechanism_chains"][0]["links"]]
    add(C, "mechanism chain evidence levels / E2 steps carry 【假设】 (text or missing_link_note)", [lv_, has_hyp],
        [["E1", "E1", "E2", "E2"], [False, False, True, True]],
        lv_ == ["E1", "E1", "E2", "E2"] and has_hyp == [False, False, True, True], "l3.mechanism_chains", snip="传导【假设】")
    add(C, "step4 inline label: literal 【假设】 in step-4 text?", "【假设】" in judg["l3"]["mechanism_chains"][0]["links"][3]["text"],
        "否(标签在 missing_link_note 与对质表因果/竞争解释行)", False, "l3.mechanism_chains[0].links[3]", ctx=True,
        note="step-4 text is an observation block whose attribution sentence has no inline label; the E2 tag + missing_link_note 「归因环节为【假设】」 carry it",
        snip="归因环节为【假设】")
    add(C, "registry JP/EA metrics vs no BOJ statement text series; policy_doc_facts", [len(plan.get("policy_doc_facts") or [])], [1],
        len(plan.get("policy_doc_facts") or []) == 1, "C2 competing", snip="政策文档事实仅 FOMC 纪要一条")
    add(C, "engine point_values_cells / dimension gaps", [len(plan["point_values"]["cells"]), len(plan["point_values"].get("absent") or [])], [6, 0],
        len(plan["point_values"]["cells"]) == 6, "agent_declaration.basis", snip="点值格(6格)")
    add(C, "calendar version / updated", [cal.get("version"), cal.get("updated")], ["1.5.0", "2026-11-21"],
        [cal.get("version"), cal.get("updated")] == ["1.5.0", "2026-11-21"], "C2/JP from_to", snip="v1.5.0,2026-11-21 更新")

    # =====================================================================
    # ctx points (not tallied): undisclosed in-window VIX round trip; EA flash-tier calendar entries
    # =====================================================================
    C = "反方攻击·上下文(不计入)"
    vd_, vv_ = ser("VIX")
    i05 = vd_.index(date(2026, 11, 5))
    i04 = vd_.index(date(2026, 11, 4))
    i11 = vd_.index(date(2026, 11, 11))
    add(C, "VIX 2026-11-04 close → 2026-11-05 close → 2026-11-11 close", [vv_[i04], vv_[i05], r2(pct(vv_[i04], vv_[i05])), vv_[i11], r2(pct(vv_[i05], vv_[i11]))],
        "(判断档未披露)", False, "link3", ctx=True,
        note="in-window earlier spike and fast full reversal (close-based), relevant to competing explanation's 快速回落", snip="仅有一个盘中观测")
    sp = r2(pct(at("SPX", "2026-11-04"), at("SPX", "2026-11-05")))
    nk = r2(pct(at("NIKKEI225", "2026-11-04"), at("NIKKEI225", "2026-11-05")))
    add(C, "presumed inflation release days inside the VIX jump window: VIX day change on 2026-11-16 (EA_HICP 2026-10, me+16) / 2026-11-20 (JP_CPI 2026-10, me+20)",
        [r2(pct(at("VIX", "2026-11-13"), at("VIX", "2026-11-16"))), r2(pct(at("VIX", "2026-11-19"), at("VIX", "2026-11-20")))],
        "(判断档只量到决议日 2026-10-30/生效日 2026-09-16,未检验读数发布日)", False, "link3 verdict_note (b)", ctx=True,
        note="ctx/MINOR: 两个最大单日跳升日与两条推定通胀发布日重合;跨地区复核见下一行")
    _jr = {m: r2(pct(at(m, "2026-11-13"), at(m, "2026-11-20"))) for m in ("SPX", "DAX", "CAC40", "NIKKEI225")}
    _dy = {m: [r2(pct(at(m, "2026-11-13"), at(m, "2026-11-16"))), r2(pct(at(m, "2026-11-19"), at(m, "2026-11-20")))] for m in ("SPX", "DAX", "CAC40", "NIKKEI225", "EURUSD", "USDJPY")}
    add(C, "cross-region check on release days: close-to-close 2026-11-13→2026-11-20 and day changes on 11-16 / 11-20",
        {"window_11-13_to_11-20": _jr, "day_11-16_/_11-20": _dy}, "读数发布主因?(未述)", False, "link3 verdict_note (b)", ctx=True,
        note="ctx: 跳升窗内四地股指跌幅均不大于美股(SPX 最深);发布日当日同日收盘跨时区不同步(东京<欧洲<纽约),不构成地区特异性证据→结论不变")
    add(C, "SPX / NIKKEI225 2026-11-04 → 2026-11-05", [sp, nk], "(判断档未披露)", False, "link3", ctx=True,
        note="earlier in-window risk-off episode", snip="仅有一个盘中观测")
    hic = [e for e in cal["entries"] if e.get("metric_id") == "EA_HICP_YOY"]
    add(C, "release_calendar EA_HICP_YOY entries (obs month, first_publish, final)", [[e["obs_from"][:7], e.get("first_publish_on_or_after"), e.get("final_publish_on")] for e in hic],
        "日历实录仅覆盖日本政策目标两条", False, "C3③", ctx=True, note="two-tier (flash/final) 实录 exists for EA_HICP_YOY, outside the window", snip="日历实录仅覆盖日本政策目标两条")
    add(C, "MAP_REPORT header line: 研究时点口径 … 研究截止日", "2026-11-30" in map_txt.split("\n")[4], "2026-11-23 (elsewhere in header)", False,
        "MAP_REPORT 头部(引擎渲染)", ctx=True, note="engine template line says cutoff 2026-11-30 while lines 4/6 say 2026-11-23", snip="研究时点口径: 裸年月 2026年11月 按月末时点化为研究截止日 2026-11-30")

    # =====================================================================
    # ⑥ 转折判断 vs 引擎候选面
    # =====================================================================
    C = "⑥转折"
    tc = plan["turning_candidates"]["candidates"]
    tby = {(c["metric_id"], c["to_ym"]): c for c in tc}
    tdates = []
    TSNIP = ["2026-02→2026-05", "2026-04 0.727→2026-07 0.978", "2026-06→2026-09"]
    for i, t in enumerate(judg["reader_map"]["turnings"]):
        c = tby.get((t["metric_id"], t["date"]))
        tdates.append(t["date"])
        okc = c is not None and t["before_date"] == c["from_ym"] and t["value_before"] == c["value_before"] and t["value_after"] == c["value_after"]
        sv = [mv(t["metric_id"], t["before_date"]), mv(t["metric_id"], t["date"])]
        add(C, f"turnings[{i}] ({t['metric_id']} {t['before_date']}→{t['date']}) vs report.json turning_candidates & series_store",
            [t["before_date"], t["date"], sv], [c["from_ym"], c["to_ym"], [c["value_before"], c["value_after"]]] if c else None,
            okc and sv == [c["value_before"], c["value_after"]], "reader_map.turnings", note="candidate face: %d candidates; judgment picked %d distinct metrics" % (len(tc), len(judg["reader_map"]["turnings"])),
            snip=TSNIP[i])
    add(C, "turning dates strictly increasing and within 12 months before cutoff", tdates, "递增、均在窗内", tdates == sorted(tdates) and len(set(tdates)) == 3
        and all(date(int(x[:4]), int(x[5:]), 1) >= date(2025, 11, 23) for x in tdates), "reader_map.turnings")
    add(C, "three turnings use three distinct metrics", len({t["metric_id"] for t in judg["reader_map"]["turnings"]}), 3,
        len({t["metric_id"] for t in judg["reader_map"]["turnings"]}) == 3, "reader_map.turnings", note="engine basis: 三转折须为不同事件")

    # =====================================================================
    # ⑦ 区分指标在证据面在场
    # =====================================================================
    C = "⑦传导·区分指标"
    for lk, nm in zip(judg["reader_map"]["transmission"][0]["links"], ("环1", "环2", "环3")):
        m = lk["distinguishing_metric"]
        inreg = m in regm
        inev = any(e["metric_id"] == m and e["kind"] == "snapshot_fact" for e in ev)
        add(C, f"{nm} distinguishing_metric {m}: in registry / in evidence_index(snapshot_fact)", [inreg, inev], [True, True], inreg and inev,
            "reader_map.transmission", snip="能区分解释的指标: %s" % m)
    # quality note [5] engine-gap disclosures (truthfulness) — read-only source inspection
    if src_contract and src_textcons:
        C = "质量注记[5]引擎缺口披露属实性"
        with open(src_contract, encoding="utf-8") as fh:
            sc = fh.read()
        with open(src_textcons, encoding="utf-8") as fh:
            st = fh.read()
        import ast
        tree = ast.parse(st)
        aliases = None
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(getattr(t_, "id", None) == "ALIASES" for t_ in node.targets):
                aliases = set(ast.literal_eval(node.value).keys())
        labels = "('12个月前', '3个月前', '最新一期')" in sc
        add(C, "judgment_contract.py _map_checks 锚标签硬编码「12个月前/3个月前/最新一期」", labels, True, labels,
            "quality_gate_notes[5]①", note="source lines with tuple: %s" % [i + 1 for i, l in enumerate(sc.splitlines()) if "'12个月前', '3个月前', '最新一期'" in l])
        miss = [m for m in ("JP_CPI_YOY", "EA_HICP_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_TARGET", "ECB_MRO") if m not in aliases]
        add(C, "text_consistency.ALIASES 未覆盖五指标 / 含别名 CPI",
            [len(miss), "CPI" in aliases], [5, True], len(miss) == 5 and "CPI" in aliases, "quality_gate_notes[5]②",
            note="ALIASES has %d keys; missing=%s" % (len(aliases), miss))

    # =====================================================================
    # extra context points (not tallied)
    # =====================================================================
    C = "反方攻击·上下文(不计入)"
    vint = {}
    for c in plan["point_values"]["cells"]:
        vint[c["metric_id"]] = {a.get("vintage") for a in c["anchors"].values()}
    add(C, "engine cell vintages per metric (事后回顾 vs as_collected)", {k: sorted(v) for k, v in vint.items()},
        "C3④「月度数值为事后回顾口径」(全称)", False, "C3④ / quality_gate_notes[4] 末句", ctx=True,
        note="ctx/NIT: 仅 EA_HICP_YOY、JP_CPI_YOY 标「事后回顾」;东京 CPI 与月均拆借利率为 as_collected(采集时点值)——④的全称表述偏宽(偏保守方向)")
    jf = facts["JP_CPI_YOY@2026-10-01"]
    add(C, "facts[JP_CPI_YOY@2026-10-01].calc 抽验句", "抽验一致(2026-09=2.16 vs 官方2.1)" if "2026-09=2.16 vs 官方2.1" in jf["calc"] else jf["calc"][-80:],
        "(判断档未述两位小数为采集端由指数水平直算)", False, "C1", ctx=True,
        note="ctx/NIT: 序列值为采集端由物价指数水平直算的两位小数,官方公布为一位小数;判断档以两位小数陈述并写「约」,方向不受影响")
    e0, u0, e1, u1 = at("EURUSD", "2026-10-23"), at("USDJPY", "2026-10-23"), at("EURUSD", "2026-11-20"), at("USDJPY", "2026-11-20")
    add(C, "implied EURJPY = EURUSD×USDJPY (2026-10-23 → 2026-11-20)", [round(e0 * u0, 3), round(e1 * u1, 3), r2(pct(e0 * u0, e1 * u1))],
        "(判断档称 EURJPY 交叉盘不在证据面、不可直接检验)", False, "link2 / step3", ctx=True,
        note="ctx: 交叉盘可由证据面两条序列相乘推出(窗内约 −0.2%%,量级很小);判断档「不可直接检验」偏保守,不改变「支持竞争解释」的倾向")
    sens = {}
    for ym0 in ("2026-04", "2026-05", "2026-06", "2026-07"):
        sens[ym0] = [r2(mv("EA_HICP_YOY", "2026-10") - mv("EA_HICP_YOY", ym0)), r2(mv("JP_CPI_YOY", "2026-10") - mv("JP_CPI_YOY", ym0))]
    add(C, "momentum (Δ to 2026-10) by alternative start month [EA, JP]", sens, "C1「窗内动量不分化」(锚=2026-04 期: +1.0 / +1.06)",
        False, "C1", ctx=True,
        note="ctx/反方攻击: 「动量相近」依赖起点取 2026-04 期;自 2026-06 起算为 +1.2 / +0.77、自 2026-07 为 +1.1 / +0.47(欧元区更快),自 2026-05 为 +0.8 / +0.91(日本更快)——陈述已限定锚点,不构成错误,结论对起点敏感")
    add(C, "level gap by ECB rate chosen: DFR 2.5−1.25 / MRO 2.65−1.25", [r2(2.5 - boj_t), r2(2.65 - boj_t)], "C2 用 DFR→约 1.25pp;step3/环2 用 MRO 2.65 vs 1.25",
        False, "C2 / step3 / link2", ctx=True, note="ctx/NIT: 两处水平差所用欧央行利率不同(均已写明利率名),量级差 0.15pp,不改变「欧元区高于日本」的方向")
    rendered = {"MAP": 0, "FULL": 0, "neither": []}
    def walkstr(o, path=""):
        if isinstance(o, dict):
            for k, v in o.items():
                yield from walkstr(v, path + "." + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                yield from walkstr(v, path + "[%d]" % i)
        elif isinstance(o, str) and len(o) >= 40:
            yield path, o
    for pth, v_ in walkstr(judg):
        if pth.startswith(".agent_declaration") or pth.startswith(".quality_gate_notes"):
            continue
        if v_ in map_txt:
            rendered["MAP"] += 1
        elif v_ in full_txt:
            rendered["FULL"] += 1
        else:
            rendered["neither"].append(pth)
    add(C, "judgment long text blocks rendered verbatim (MAP / FULL / neither)", rendered, "渲染文字与判断档逐字一致", not rendered["neither"],
        "读者报告", ctx=True, note="ctx(范围外观察): 渲染出的判断文字均逐字一致;未渲染=三条 verdict_note 与三条 turnings.narrative(对质理由与逐月叙述未进读者面)")

    # =====================================================================
    # supplementary points: walk-text claims (regions[*].from_to / step1 / step4 / declaration)
    # =====================================================================
    C = "⑩走位文字"
    # (EA 近十二个月最高 / 东京较前月上行 already covered above: rows "EA_HICP_YOY last obs == max(last 12 obs)" and "Tokyo 2026-10 > 2026-09 …")
    jp6 = [mv("JP_CPI_YOY", "2026-%02d" % m) for m in range(5, 11)]
    ea6 = [mv("EA_HICP_YOY", "2026-%02d" % m) for m in range(5, 11)]
    add(C, "EA_HICP_YOY 2026-05..2026-10: dip month(s)", [i for i in range(1, 6) if ea6[i] < ea6[i - 1]], "2026-06 回落至 2.8,非逐月单调",
        [i for i in range(1, 6) if ea6[i] < ea6[i - 1]] == [1] and ea6[1] == 2.8, "M1 step1", snip="欧元区 2026-06 一度回落至 2.8,非逐月单调")
    jpath = [y for x, y in zip(*ser("JP_CPI_YOY")) if x == date(2026, 2, 1) or x == date(2026, 10, 1)]
    add(C, "JP_CPI_YOY 2026-02 → 2026-10 (此后总体回升)", jpath, [1.27, 2.44], jpath[1] > jpath[0] and jpath == [1.27, 2.44], "JP from_to",
        snip="此后总体回升", note="non-monotonic: 2026-04 1.38 < 2026-03 1.46 (「总体」措辞如实)")
    add(C, "step4 levels: DAX 2026-11-23 / NIKKEI225 2026-11-20", [at("DAX", "2026-11-23"), at("NIKKEI225", "2026-11-20")], [25209.45, 56436.65],
        num_ok(at("DAX", "2026-11-23"), 25209.45, 0.01) and num_ok(at("NIKKEI225", "2026-11-20"), 56436.65, 0.01), "M1 step4", snip="NIKKEI225 -9.98%(56436.65,2026-11-20 收盘)")
    _ud, _uv = ser("UST_10Y")[0][-1].isoformat(), ser("UST_10Y")[1][-1]
    add(C, "UST_10Y latest obs / value", [_ud, _uv], ["2026-11-19", 5.04], _ud == "2026-11-19" and num_ok(_uv, 5.04, 0.006),
        "link2 verdict_note", snip="UST_10Y 最新 5.04%")

    # ---------- snip guard ----------
    for p in PTS:
        if p["snip"] and not has(p["snip"]):
            SNIP_MISS.append((p["id"], p["snip"]))

    # ---------- output ----------
    tallied = [p for p in PTS if not p["ctx"]]
    mism = [p for p in tallied if not p["ok"]]
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "recompute_table.md"), "w", encoding="utf-8") as f:
        f.write("# 复算清单(Audit-R32 N30 Round-1 独立语义审查席;只读直算后比对)\n\n")
        f.write("列: # | 类别 | 出处键(只读面) | 直算值 | 报告/判断档值 | 一致 | 位置 | 备注\n\n")
        for p in PTS:
            tag = "上下文(不计入)" if p["ctx"] else ("一致" if p["ok"] else "偏离")
            f.write("| %d | %s | %s | %s | %s | %s | %s | %s |\n" % (
                p["id"], p["cat"], str(p["src"]).replace("|", "/"), json.dumps(p["comp"], ensure_ascii=False).replace("|", "/"),
                json.dumps(p["rep"], ensure_ascii=False).replace("|", "/"), tag, str(p["where"]).replace("|", "/"),
                str(p["note"]).replace("|", "/").replace("\n", " ")))
        f.write("\n统计: 计入比对点数=%d, 偏离=%d, 上下文点(不计入)=%d, snip 未命中=%d\n" % (
            len(tallied), len(mism), len(PTS) - len(tallied), len(SNIP_MISS)))
    summ = {"recompute_points": len(tallied), "recompute_mismatches": len(mism),
            "mismatch_details": [{"id": p["id"], "cat": p["cat"], "src": p["src"], "computed": p["comp"], "report": p["rep"], "where": p["where"], "note": p["note"]} for p in mism],
            "ctx_points": [{"id": p["id"], "cat": p["cat"], "src": p["src"], "computed": p["comp"], "report": p["rep"], "note": p["note"]} for p in PTS if p["ctx"]],
            "snip_miss": SNIP_MISS}
    with open(os.path.join(out_dir, "recompute_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summ, f, ensure_ascii=False, indent=1)
    print("tallied points:", len(tallied), "| mismatches:", len(mism), "| ctx:", len(PTS) - len(tallied), "| snip_miss:", len(SNIP_MISS))
    for p in mism:
        print("MISMATCH", p["id"], p["cat"], p["src"], "computed=", p["comp"], "report=", p["rep"], "|", p["where"])
    for s in SNIP_MISS:
        print("SNIP_MISS", s)
    by = {}
    for p in tallied:
        by.setdefault(p["cat"], [0, 0])
        by[p["cat"]][0] += 1
        by[p["cat"]][1] += (0 if p["ok"] else 1)
    for k in by:
        print("  ", k, by[k])


def r(x, n=0):
    return None if x is None else round(x + 0.0, n)


if __name__ == "__main__":
    main()
