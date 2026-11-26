#!/usr/bin/python3
"""s10_recompute.py -- 独立语义审查席复算表(全部输入只读,只写本席目录的输出文件)。

每个复算点: 类别 / 出处键 / 直算值 / 报告值 / 是否一致。直算一律取自冻结快照 series_store、
冻结发布日历、注册表与 report.json 引擎面,再与判断档(agent_judgment.json)及读者报告文字比对。

Usage:
  /usr/bin/python3 -I s10_recompute.py <snapshot.json> <report.json> <release_calendar.json>
      <metric_registry.json> <agent_judgment.json> <evidence_index.json> <AGENT_SEAT_ENVELOPE.json>
      <MAP_REPORT.md> <FULL_REPORT.md> <report.md> <out_table.txt> <out_summary.json> <out_appendix.txt>

类别前缀「引擎面自洽」的点只核对引擎面内部算术, 不计入对判断档/报告文字的命中-偏离计数。
"""
import datetime as dt
import json
import math
import re
import sys
from zoneinfo import ZoneInfo

CUT = dt.date(2026, 11, 23)
ANCH3 = dt.date(2026, 8, 23)
WSTART = dt.date(2025, 11, 23)
PTS = []
APPX = []


def D(s):
    return dt.date.fromisoformat(str(s)[:10])


def fmt(x):
    if x is None:
        return "N/A"
    if isinstance(x, float):
        if not math.isfinite(x):
            return repr(x)
        s = "%.6f" % x
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        return "0" if s in ("-0", "") else s
    return str(x)


def close(a, b, rel=1e-9):
    try:
        a = float(a)
        b = float(b)
    except (TypeError, ValueError):
        return False
    return abs(a - b) <= rel * max(1.0, abs(a), abs(b))


def within(a, b, tol):
    try:
        return a is not None and b is not None and abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def add(cat, src, mine, reported, ok, note=""):
    PTS.append({"cat": cat, "src": src, "mine": mine, "reported": reported, "ok": bool(ok), "note": note})


def month_end(d):
    return dt.date(d.year + (1 if d.month == 12 else 0), 1 if d.month == 12 else d.month + 1, 1) - dt.timedelta(days=1)


def quarter_end(d):
    return month_end(dt.date(d.year, ((d.month - 1) // 3 + 1) * 3, 1))


def ym_add(ym, k):
    y, m = int(ym[:4]), int(ym[5:])
    t = (y * 12 + (m - 1)) + k
    return "%04d-%02d" % (t // 12, t % 12 + 1)


def main():
    (snap_path, rep_path, cal_path, reg_path, aj_path, ev_path, env_path, map_path, full_path, md_path,
     out_txt, out_json, out_appx) = sys.argv[1:14]

    def load_json(p):
        with open(p, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def load_text(p):
        with open(p, "r", encoding="utf-8") as fh:
            return fh.read()

    snap = load_json(snap_path)
    rep = load_json(rep_path)
    cal = load_json(cal_path)
    reg = load_json(reg_path)
    aj = load_json(aj_path)
    ev = load_json(ev_path)
    ENV = load_text(env_path)
    MAP = load_text(map_path)
    FULL = load_text(full_path)
    MD = load_text(md_path)
    AJ = json.dumps(aj, ensure_ascii=False)
    store = snap["series_store"]
    plan = rep["research_plan"]

    CACHE = {}

    def series(m):
        if m not in CACHE:
            s = store.get(m)
            out = []
            if isinstance(s, dict):
                for d, v in zip(s.get("dates", []), s.get("values", [])):
                    if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v):
                        out.append((D(d), float(v)))
            CACHE[m] = out
        return CACHE[m]

    SD = {}

    def sdict(m):
        if m not in SD:
            SD[m] = dict(series(m))
        return SD[m]

    def val(m, d):
        return sdict(m).get(D(d))

    def val_any(m, d):
        """精确日取值; 月频事实以月末日期标注而序列以月初标注时按月回退(CN 月频标签 2026-10-31 vs 序列 2026-10-01)。"""
        dd = D(d)
        x = val(m, dd)
        if x is None and dd == month_end(dd):
            x = month_val(m, dd.strftime("%Y-%m"))
        return x

    def last_le(m, d):
        dd = D(d)
        res = None
        for x, v in series(m):
            if x <= dd:
                res = (x, v)
            else:
                break
        return res

    def month_val(m, ym):
        for x, v in series(m):
            if x.strftime("%Y-%m") == ym:
                return v
        return None

    def yoy_level(m, ym):
        a = month_val(m, ym)
        b = month_val(m, ym_add(ym, -12))
        if a is None or b is None:
            return None
        return (a / b - 1.0) * 100.0

    def bound(*toks):
        return all(t in AJ for t in toks)

    def changes(m, start, end):
        s = series(m)
        res = []
        for i in range(1, len(s)):
            if start < s[i][0] <= end and abs(s[i][1] - s[i - 1][1]) > 1e-12:
                res.append((s[i][0], s[i - 1][1], s[i][1]))
        return res

    # ---------------------------------------------------------------- A 截止日与时点
    ra = snap.get("research_as_of")
    note0 = [s for s in aj["quality_gate_notes"] if s.startswith("证据与口径")][0]
    add("①截止日", "snapshot.research_as_of", ra, "研究截止日=快照版本日 2026-11-23(research_as_of 2026-11-23T22:58:11+08:00 (AJ 证据与口径)",
        ra == "2026-11-23T22:58:11+08:00" and "research_as_of 2026-11-23T22:58:11+08:00" in note0)
    add("①截止日", "snapshot.target_date / report.json research_plan.cutoff / run.evidence_asof",
        "%s / %s / %s" % (snap.get("target_date"), plan.get("cutoff"), rep["run"].get("evidence_asof")),
        "2026-11-23 (MAP_REPORT 头「研究截止日: 2026-11-23」)",
        snap.get("target_date") == "20261123" and plan.get("cutoff") == "2026-11-23"
        and rep["run"].get("evidence_asof") == "2026-11-23" and "研究截止日: 2026-11-23" in MAP)
    pa = {p["label"]: p for p in plan["point_anchors"]}
    add("①截止日", "research_plan.point_anchors[3个月前].as_of", "%s-3月=%s" % (CUT, ANCH3), "三个月前锚 2026-08-23 (AJ 同比基期纪律/转折取舍)",
        pa["3个月前"]["as_of"] == "2026-08-23" and "2026-08-23" in AJ)
    add("①截止日", "research_plan.point_anchors[最新一期].as_of", pa["最新一期"]["as_of"], "最新一期锚 2026-11-23", pa["最新一期"]["as_of"] == "2026-11-23")
    viol = []
    maxd = None
    for m in sorted(store):
        s = series(m)
        if s:
            if maxd is None or s[-1][0] > maxd:
                maxd = s[-1][0]
            if s[-1][0] > CUT:
                viol.append("%s@%s" % (m, s[-1][0]))
    add("①截止日", "snapshot.series_store[*] 88 序列末观测日", "max=%s 越界=%d" % (maxd, len(viol)),
        "研究截止日 2026-11-23 (序列不得含截止日之后观测)", not viol, ",".join(viol))
    full_dates = sorted(set(re.findall(r"20\d{2}-\d{2}-\d{2}", AJ)))
    fut = [t for t in full_dates if D(t) > CUT and t != "2027-02-28"]
    add("①截止日", "agent_judgment.json 全文日期 token(%d 个)" % len(full_dates), ">2026-11-23 的日期=%s" % (fut or "无(仅情景期限 2027-02-28)"),
        "情景期限 2027-02-28 (AJ 证伪面); 其余日期均须<=截止日", not fut, "越界: %s" % fut)
    ra_dt = dt.datetime.fromisoformat(ra)
    for tzn, tok in (("America/New_York", "纽约 09:58"), ("Europe/Berlin", "法兰克福 15:58"),
                     ("Asia/Tokyo", "东京 23:58"), ("Asia/Shanghai", "上海 22:58")):
        t = ra_dt.astimezone(ZoneInfo(tzn)).strftime("%H:%M")
        add("①截止日·时区", "snapshot.research_as_of → %s" % tzn, t, "%s (AJ 证据与口径)" % tok, t == tok.split()[1] and tok in note0)
    add("⑫盘中标签", "series_store.NIKKEI225 末观测日", str(series("NIKKEI225")[-1][0]), "NIKKEI225 止于 2026-11-20 收盘(2026-11-23 无观测) (AJ)",
        series("NIKKEI225")[-1][0] == dt.date(2026, 11, 20) and "止于 2026-11-20 收盘" in note0)
    add("⑫盘中标签", "series_store.SHCOMP 末观测日 / research_as_of(上海 22:58=收盘后)", str(series("SHCOMP")[-1][0]), "SHCOMP 2026-11-23 为收盘价 (AJ)",
        series("SHCOMP")[-1][0] == CUT and "SHCOMP 2026-11-23 为收盘价" in note0)
    add("⑫盘中标签", "series_store.SPX/VIX/DAX/CAC40/DXY 末观测日",
        ",".join("%s=%s" % (m, series(m)[-1][0]) for m in ("SPX", "VIX", "DAX", "CAC40", "DXY")),
        "SPX、VIX、DAX、CAC40 与 DXY 的当日值为盘中快照 (AJ)", all(series(m)[-1][0] == CUT for m in ("SPX", "VIX", "DAX", "CAC40", "DXY"))
        and "盘中快照(非收盘价)" in note0)

    # ---------------------------------------------------------------- B 锚点格
    cells = plan["point_values"]["cells"]
    cell_list = [cells[k] for k in sorted(cells, key=lambda x: int(x))] if isinstance(cells, dict) else list(cells)
    ANCH = (("3个月前", ANCH3), ("最新一期", CUT))
    OFFSETS = {
        "US_REAL_GDP": ("qe", 29), "UNEMPLOYMENT": ("me", 5), "INDPRO": ("me", 15), "CPI": ("me", 13),
        "CORE_CPI": ("me", 13), "CORE_PCE": ("me", 30), "DFF": ("od", 1), "CN_PMI_MFG": ("me", -1),
        "CN_CPI_YOY": ("me", 9), "CN_PPI_YOY": ("me", 9), "CN_LPR_1Y": ("od", 0), "CN_OMO_7D": ("od", 0),
        "CN_POLICY_OVERNIGHT": ("od", 0), "JP_REAL_GDP_YOY": ("qe", 45), "JP_CPI_YOY": ("me", 20),
        "JP_CPI_TOKYO_YOY": ("me", -1), "JP_POLICY_RATE": ("me", 5), "DFEDTARU": ("od", 0),
    }
    cal_entries = cal.get("entries", [])

    def cal_has(metric, pubdate):
        return [e for e in cal_entries if e.get("metric_id") == metric and e.get("first_publish_on_or_after") == pubdate]

    def pub_expected(m, obsd):
        base, off = OFFSETS[m]
        b = month_end(obsd) if base == "me" else (quarter_end(obsd) if base == "qe" else obsd)
        return b + dt.timedelta(days=off)

    echo = {}
    for r in aj["reader_map"]["regions"]:
        for e in r.get("anchor_echo", []):
            echo[(e["metric_id"], e["anchor"])] = e
    add("②锚格·回贴", "reader_map.regions[*].anchor_echo 条数", len(echo), "点值格锚格数(18 指标, 另 4 格序列缺席) (AJ agent_declaration.basis)",
        len(echo) == 35 and len(cell_list) == 18 and len(plan["point_values"].get("absent", [])) == 4
        and "点值格(18格,另4格序列缺席)" in AJ)
    cls_mismatch = []
    for c in cell_list:
        m = c["metric_id"]
        for lab, asof in ANCH:
            a = c["anchors"].get(lab)
            src = "cells[%s].anchors[%s]" % (m, lab)
            if a is None:
                add("②锚格", src, "缺锚格", "应有两锚", False)
                continue
            if a.get("status") != "ok":
                first = series(m)[0][0] if series(m) else None
                add("②锚格", src + ".status", "序列首观测日=%s" % first,
                    "%s (AJ「三个月前锚前无已发布观测」)" % a.get("status"),
                    a.get("status") == "no_published_observation_on_or_before_anchor" and first is not None
                    and first > asof and "三个月前锚(2026-08-23)前无已发布观测" in AJ)
                continue
            od = D(a["observation_date"])
            v = val(m, od)
            add("②锚格·值", "snapshot.series_store.%s@%s" % (m, od), fmt(v), "%s (%s.value)" % (fmt(a.get("value")), src),
                v is not None and close(v, a.get("value")))
            e = echo.get((m, lab))
            add("②锚格·回贴", "reader_map.anchor_echo[%s|%s] vs series_store" % (m, lab),
                "值=%s 观测月=%s" % (fmt(v), od.strftime("%Y-%m")),
                "echo 值=%s 观测月=%s" % (fmt(e.get("value")) if e else None, e.get("observation_month") if e else None),
                e is not None and close(v, e.get("value")) and e.get("observation_month") == od.strftime("%Y-%m"))
            basis = a.get("publication_basis") or ""
            if basis.startswith("calendar:"):
                hits = cal_has(m, a.get("publication_date"))
                mine = "日历条目发布日=%s" % (hits[0].get("first_publish_on_or_after") if hits else "无条目")
                ok = bool(hits) and a.get("publication_date") <= asof.isoformat() and od <= asof
            else:
                pe = pub_expected(m, od)
                nxt = next((x for x, _ in series(m) if x > od), None)
                npub = pub_expected(m, nxt) if nxt else None
                mine = "规则复算发布日=%s; 下一观测=%s(其发布日=%s)" % (pe, nxt, npub)
                ok = (pe.isoformat() == a.get("publication_date") and a.get("publication_date") <= asof.isoformat()
                      and od <= asof and (npub is None or npub > asof))
            add("②锚格·发布纪律", src + ".publication_date/observation_date", mine,
                "发布日=%s 观测日=%s (须发布日<=锚日 %s 且为最新已发布观测)" % (a.get("publication_date"), od, asof), ok)
    # 公布时间口径分类: AJ 公布时间口径注记 逐格 vs 引擎格 publication_basis
    note4 = [s for s in aj["quality_gate_notes"] if s.startswith("公布时间口径")][0]
    cls = {}
    body = note4.split("区分——", 1)[1].split("。发布时点晚于", 1)[0]
    for seg in body.split("；"):
        label, _, items = seg.partition(": ")
        core = re.sub(r"\(.*?\)", "", label).strip()
        for it in items.split("、"):
            mm = re.match(r"\s*([A-Z0-9_]+)(\(三个月前锚\))?\s*$", it)
            if mm:
                cls[(mm.group(1), "3个月前" if mm.group(2) else "最新一期")] = core

    def my_cls(a):
        pb = a.get("publication_basis") or ""
        if pb.startswith("calendar:"):
            return "发布日历实录"
        if "锚" in pb and ("实测" in pb or "实录" in pb):
            return "引擎推定规则并含官方实测锚"
        if pb.startswith("FOMC"):
            return "决议日当日公布口径"
        if "官方时刻" in pb:
            return "官方惯例时刻"
        return "引擎推定规则"

    cls_mis = []
    n_cls = 0
    for c in cell_list:
        for lab, _ in ANCH:
            a = c["anchors"].get(lab)
            if a and a.get("status") == "ok":
                n_cls += 1
                if cls.get((c["metric_id"], lab)) != my_cls(a):
                    cls_mis.append("%s|%s: AJ=%s 引擎=%s" % (c["metric_id"], lab, cls.get((c["metric_id"], lab)), my_cls(a)))
    add("②锚格·公布口径分类", "cells[*].anchors[*].publication_basis × 35 锚格", "逐格分类 %d 格, 不一致 %d" % (n_cls, len(cls_mis)),
        "AJ 公布时间口径注记逐格分类 (%d 格)" % len(cls), not cls_mis and n_cls == 35 and len(cls) == 35, "; ".join(cls_mis))

    # ---------------------------------------------------------------- C 同比基期
    cell_yoy = {}
    for c in cell_list:
        for lab, _ in ANCH:
            a = c["anchors"].get(lab)
            if a and a.get("status") == "ok" and a.get("observation_date"):
                cell_yoy[(c["metric_id"], a["observation_date"][:7])] = (a.get("derived_yoy_pct"), a.get("yoy_status"))

    def yoy_pt(metric, ym, rep_num, toks, tol, note):
        y = yoy_level(metric, ym)
        base = month_val(metric, ym_add(ym, -12))
        cy = cell_yoy.get((metric, ym))
        cy_s = "格同比=%s/%s" % (cy[0], cy[1]) if cy else "格同比=(非格值)"
        tok_ok = bound(*toks)
        if rep_num is None:
            ok = y is None and tok_ok and (cy is None or cy[0] is None)
        else:
            ok = within(y, rep_num, tol) and tok_ok and (cy is None or cy[0] is None or within(y, cy[0], 0.0051))
        add("③同比基期", "series_store.%s: %s月值/%s月值-1 (基期%s)" % (metric, ym, ym_add(ym, -12), "缺席" if base is None else fmt(base)),
            "N/A(基期缺席)" if y is None else "%.4f" % y, "%s (%s; %s)" % ("不可得" if rep_num is None else fmt(rep_num), toks[0], cy_s), ok, note)

    yoy_pt("US_REAL_GDP", "2026-04", 2.19, ["百分之二点一九"], 0.0051, "C3 三个月前锚所在季 2026Q2")
    yoy_pt("US_REAL_GDP", "2026-07", 2.07, ["百分之二点零七"], 0.0051, "C3 最新季 2026Q3")
    yoy_pt("INDPRO", "2026-07", 1.25, ["百分之一点二五"], 0.0051, "C3")
    yoy_pt("INDPRO", "2026-10", 2.15, ["百分之二点一五"], 0.0051, "C3")
    yoy_pt("CPI", "2026-07", 3.30, ["百分之三点三零"], 0.0051, "C2 三个月前锚")
    yoy_pt("CPI", "2026-09", 3.72, ["百分之三点七二"], 0.0051, "C2 最近有效同比")
    yoy_pt("CPI", "2026-10", None, ["同比因缺上年同月基期观测不可得"], 0, "C2/C4: 2025-10 基期缺席, 不得以相邻月冒充")
    yoy_pt("CORE_CPI", "2026-07", 2.47, ["百分之二点四七"], 0.0051, "C2")
    yoy_pt("CORE_CPI", "2026-09", 2.57, ["百分之二点五七"], 0.0051, "C2 最近有效同比")
    yoy_pt("CORE_CPI", "2026-10", None, ["2026-10 因缺上年同月基期观测同比不可得"], 0, "转折3: 2025-10 基期缺席")
    yoy_pt("CORE_PCE", "2026-06", 3.04, ["百分之三点零四"], 0.0051, "C2")
    yoy_pt("CORE_PCE", "2026-09", 3.12, ["百分之三点一二"], 0.0051, "C2")
    yoy_pt("CN_PMI_MFG", "2026-07", -0.2, ["49.2(观测 2026-07"], 0.0051, "引擎格派生同比(PMI 水平 49.2 同比)")
    yoy_pt("CN_PMI_MFG", "2026-10", 0.61, ["49.3(观测 2026-10"], 0.0051, "引擎格派生同比(PMI 水平 49.3 同比)")
    yoy_pt("CPI", "2026-02", 2.434, ["2.434"], 0.0006, "转折候选 美国CPI同比")
    yoy_pt("CPI", "2026-05", 4.1666, ["4.1666"], 0.0006, "转折候选 美国CPI同比")
    yoy_pt("CORE_CPI", "2026-05", 2.8229, ["2.8229"], 0.0006, "转折候选 核心CPI同比")
    yoy_pt("CORE_CPI", "2026-08", 2.4462, ["2.4462"], 0.0006, "转折候选 核心CPI同比")
    yoy_pt("CORE_CPI", "2026-09", 2.5658, ["2.5658"], 0.0006, "转折3 其后 2026-09 回升值")
    yoy_pt("INDPRO", "2025-11", 1.7543, ["1.7543"], 0.0006, "转折补选")
    yoy_pt("INDPRO", "2026-02", 0.7972, ["0.7972"], 0.0006, "转折补选")
    yoy_pt("CN_PMI_MFG", "2026-02", -2.3904, ["-2.3904"], 0.0006, "转折补选相邻窗")
    yoy_pt("CN_PMI_MFG", "2026-05", 1.0101, ["1.0101"], 0.0006, "转折补选相邻窗")

    # ---------------------------------------------------------------- D 政策面
    def cell(m):
        return next(c for c in cell_list if c["metric_id"] == m)

    def path(m):
        return cell(m).get("policy_window_path") or {}

    tu = series("DFEDTARU")
    last375 = max(x for x, v in tu if abs(v - 3.75) < 1e-9)
    first4 = min(x for x, v in tu if x > last375 and abs(v - 4.0) < 1e-9)
    add("④政策面", "series_store.DFEDTARU 变更点", "末次 3.75=%s; 其后首个 4.0=%s" % (last375, first4),
        "2026-09-16 决议(引擎按生效日前一日推定)、2026-09-17 生效 (AJ C1)",
        last375 == dt.date(2026, 9, 16) and first4 == dt.date(2026, 9, 17) and bound("2026-09-16 决议", "2026-09-17 生效"))
    a1, a2 = dt.date(2026, 9, 16), dt.date(2026, 9, 18)
    add("⑥先后·决议日", "日历星期 2026-09-16 / 2026-09-18", "%s / %s; ISO周 %d/%d; 相隔 %d 天" % (a1.strftime("%a"), a2.strftime("%a"), a1.isocalendar()[1], a2.isocalendar()[1], (a2 - a1).days),
        "美日两次决议日期相隔两日，属同一周内的同步收紧; 不据此排序先后 (AJ C1)",
        a1.strftime("%a") == "Wed" and a2.strftime("%a") == "Fri" and a1.isocalendar()[1] == a2.isocalendar()[1]
        and (a2 - a1).days == 2 and bound("相隔两日，属同一周内的同步收紧", "不据此排序先后"))
    pc = [c for c in changes("DFEDTARU", dt.date(2025, 10, 1), CUT) if c[0] == dt.date(2025, 12, 11)]
    add("④政策面", "series_store.DFEDTARU 2025-12 变更点", "%s: %s→%s" % (pc[0][0], fmt(pc[0][1]), fmt(pc[0][2])) if pc else "无",
        "2025-12-10 决议、2025-12-11 生效，下调二十五 (AJ C1)",
        bool(pc) and pc[0][1] == 4.0 and pc[0][2] == 3.75 and bound("2025-12-10 决议", "2025-12-11 生效", "下调二十五"))
    st = last_le("DFEDTARU", WSTART)
    ev12 = [(e[0].isoformat(), e[1], e[2]) for e in changes("DFEDTARU", WSTART, CUT)]
    pth = path("DFEDTARU")
    add("④政策面", "series_store.DFEDTARU 一年窗[2025-11-23,2026-11-23]", "起=%s(%s) 末=%s 事件=%s 净=%+d bp" % (st[0], fmt(st[1]), fmt(tu[-1][1]), ev12, round((tu[-1][1] - st[1]) * 100)),
        "近一年事件簇先降后升…净变动为零 (AJ C1); 引擎路径面 start=%s end=%s net=%s" % (pth.get("window_start_value"), pth.get("window_end_value"), pth.get("net_bp")),
        st[1] == 4.0 and tu[-1][1] == 4.0 and ev12 == [("2025-12-11", 4.0, 3.75), ("2026-09-17", 3.75, 4.0)]
        and pth.get("net_bp") == 0 and pth.get("window_start_value") == 4.0 and bound("净变动为零"))
    v3, vN = val("DFEDTARU", ANCH3), val("DFEDTARU", CUT)
    add("④政策面", "series_store.DFEDTARU@2026-08-23 → @2026-11-23", "%s → %s = %+d bp" % (fmt(v3), fmt(vN), round((vN - v3) * 100)),
        "三个月前锚三点七五、最新为四，上限上调二十五 (AJ C1)", v3 == 3.75 and vN == 4.0 and bound("三点七五", "上调二十五"))
    add("④政策面", "series_store.DFEDTARL@2026-11-23 与 DFEDTARU 之差", "下限=%s 区间宽度=%s" % (fmt(val("DFEDTARL", CUT)), fmt(vN - val("DFEDTARL", CUT))),
        "联邦基金目标区间上限 (口径=上限, 非区间中值)", val("DFEDTARL", CUT) == 3.75 and bound("目标区间上限"))
    de = [(e[0].isoformat(), e[1], e[2]) for e in changes("DFF", WSTART, CUT)]
    eng = [(e["date"], e["from"], e["to"]) for e in path("DFF").get("events", [])]
    dff_st = last_le("DFF", WSTART)
    add("④政策面", "series_store.DFF 一年窗变更点 vs cells[DFF].policy_window_path.events", "%d 事件; 起=%s(%s) 末=%s 净=%+d bp" % (len(de), dff_st[0], fmt(dff_st[1]), fmt(series("DFF")[-1][1]), round((series("DFF")[-1][1] - dff_st[1]) * 100)),
        "%d 事件 (引擎路径面 net=%s)" % (len(eng), path("DFF").get("net_bp")), de == eng and path("DFF").get("net_bp") == 0)
    d3, dn = val("DFF", "2026-08-22"), val("DFF", "2026-11-19")
    add("④政策面", "series_store.DFF@2026-08-22 → @2026-11-19", "%s → %s" % (fmt(d3), fmt(dn)), "3.63(2026-08-22)→3.88(2026-11-19) (AJ C1/M1)",
        d3 == 3.63 and dn == 3.88 and bound("3.63(观测 2026-08-22", "3.88(观测 2026-11-19", "发布 2026-11-20"))
    j7, j10 = month_val("JP_POLICY_RATE", "2026-07"), month_val("JP_POLICY_RATE", "2026-10")
    add("④政策面", "series_store.JP_POLICY_RATE 2026-07 → 2026-10", "%s → %s = %+.1f bp" % (fmt(j7), fmt(j10), (j10 - j7) * 100),
        "0.978→1.227, 三个月窗净 +25bp (AJ C1/M1/日本走位)", j7 == 0.978 and j10 == 1.227 and round((j10 - j7) * 100) == 25 and bound("净 +25bp"))
    stp = [month_val("JP_POLICY_RATE", y) for y in ("2026-08", "2026-09", "2026-10")]
    add("④政策面", "series_store.JP_POLICY_RATE 2026-08/09/10", ",".join(fmt(x) for x in stp), "2026-08 0.977、2026-09 1.043、2026-10 1.227 (AJ M1/日本走位/转折1)",
        stp == [0.977, 1.043, 1.227] and bound("2026-08 0.977、2026-09 1.043、2026-10 1.227"))
    jn, jd = month_val("JP_POLICY_RATE", "2025-11"), month_val("JP_POLICY_RATE", "2025-12")
    add("④政策面", "series_store.JP_POLICY_RATE 2025-11 月均 → 2026-10 月均", "%s → %s = %+.1f bp" % (fmt(jn), fmt(j10), (j10 - jn) * 100),
        "自窗启月在值(2025-11 月均 0.478)…为 +75bp (AJ 政策口径披露)", jn == 0.478 and round((j10 - jn) * 100) == 75 and bound("+75bp"))
    add("④政策面", "series_store.JP_POLICY_RATE 2025-12 月均 → 2026-10 月均", "%s → %s = %+.1f bp" % (fmt(jd), fmt(j10), (j10 - jd) * 100),
        "自窗内首个完整观测月(2025-12 月均 0.557)起算为 +67bp (AJ); MAP_REPORT 路径表「净变动 +67bp(0.557→1.227)」",
        jd == 0.557 and round((j10 - jd) * 100) == 67 and path("JP_POLICY_RATE").get("net_bp") == 67
        and path("JP_POLICY_RATE").get("window_start_value") == 0.557 and bound("+67bp") and "净变动 **+67bp**(0.557→1.227)" in MAP)
    je = [(e[0].strftime("%Y-%m-%d"), e[1], e[2], round((e[2] - e[1]) * 100)) for e in changes("JP_POLICY_RATE", WSTART, CUT) if abs(e[2] - e[1]) >= 0.005]
    jeng = [(e["date"], e["from"], e["to"], e["delta_bp"]) for e in path("JP_POLICY_RATE").get("events", [])]
    add("④政策面", "series_store.JP_POLICY_RATE 一年窗月度台阶 vs 引擎路径面事件", "%d 台阶 %s" % (len(je), je), "%d 事件 (引擎路径面)" % len(jeng), je == jeng)
    env_net = ENV.count("net_bp") if isinstance(ENV, str) else None
    add("④政策面·披露", "AGENT_SEAT_ENVELOPE.json 中 net_bp 出现次数", env_net, "本工单路径面未载净变动字段，两种口径由席位并列披露 (AJ 政策口径披露)",
        env_net == 0 and bound("本工单路径面未载净变动字段", "两种口径由席位并列披露"))
    lp3, lpN = val("CN_LPR_1Y", "2026-08-20"), val("CN_LPR_1Y", "2026-11-20")
    add("④政策面", "series_store.CN_LPR_1Y@2026-08-20 → @2026-11-20", "%s → %s" % (fmt(lp3), fmt(lpN)), "3.0(2026-08-20)→3.0(2026-11-20) (AJ 中国走位)",
        lp3 == 3.0 and lpN == 3.0 and bound("3.0(2026-08-20)→3.0(2026-11-20"))
    add("④政策面", "series_store.CN_LPR_1Y 一年窗内取值集合", sorted(set(v for x, v in series("CN_LPR_1Y") if WSTART <= x <= CUT)),
        "中国一年期 LPR 3→3 未变 (AJ M2); 引擎路径面 net=%s" % path("CN_LPR_1Y").get("net_bp"),
        set(v for x, v in series("CN_LPR_1Y") if WSTART <= x <= CUT) == {3.0} and path("CN_LPR_1Y").get("net_bp") == 0)
    o3, oN = val("CN_OMO_7D", "2026-08-21"), val("CN_OMO_7D", "2026-10-30")
    olast = series("CN_OMO_7D")[-1]
    add("④政策面", "series_store.CN_OMO_7D@2026-08-21 → 末观测", "%s → %s@%s; 滞后=%d 天; 窗内取值集合=%s" % (fmt(o3), fmt(olast[1]), olast[0], (CUT - olast[0]).days, sorted(set(v for x, v in series("CN_OMO_7D") if ANCH3 <= x <= CUT))),
        "1.4(2026-08-21)→1.4(末次 2026-10-30)，末观测滞后二十四天 (AJ C1/中国走位)",
        o3 == 1.4 and oN == 1.4 and olast[0] == dt.date(2026, 10, 30) and (CUT - olast[0]).days == 24 and bound("末观测滞后二十四天", "1.4(2026-08-21)"))
    ov = series("CN_POLICY_OVERNIGHT")
    add("④政策面", "series_store.CN_POLICY_OVERNIGHT 首末观测/取值", "首=%s 末=%s n=%d 取值=%s" % (ov[0][0], ov[-1][0], len(ov), sorted(set(v for _, v in ov))),
        "序列自 2026-11-02 起; 最新 1.25(2026-11-23) (AJ C1/中国走位)",
        ov[0][0] == dt.date(2026, 11, 2) and ov[-1] == (CUT, 1.25) and set(v for _, v in ov) == {1.25}
        and bound("序列自 2026-11-02 起", "最新 1.25(2026-11-23"))
    boj = [e for e in cal_entries if e.get("entry_id") == "RC-JP-BOJ-TARGET-2026-09"]
    bo = boj[0] if boj else {}
    add("④政策面·日历", "release_calendar.entries[RC-JP-BOJ-TARGET-2026-09].decision_date", bo.get("decision_date"), "日本央行 2026-09-18 决议 (AJ 标题/C1/日本走位)",
        bo.get("decision_date") == "2026-09-18" and bo.get("basis") == "user_directive" and bound("2026-09-18 决议"))
    add("④政策面·日历", "release_calendar.entries[RC-JP-BOJ-TARGET-2026-09].effective_on", bo.get("effective_on"), "2026-09-24 生效 (AJ)",
        bo.get("effective_on") == "2026-09-24" and bound("2026-09-24 生效"))
    add("④政策面·日历", "release_calendar.entries[RC-JP-BOJ-TARGET-2026-09].target_value", bo.get("target_value"), "官方目标利率约 1.25 / 目标水平约一点二五 (AJ 标题/C1)",
        bo.get("target_value") == 1.25 and bound("官方目标利率约 1.25", "目标水平约一点二五"))
    mnt = [e for e in cal_entries if e.get("entry_id") == "RC-JP-BOJ-MAINT-2026-10"]
    mo = mnt[0] if mnt else {}
    add("④政策面·日历", "release_calendar.entries[RC-JP-BOJ-MAINT-2026-10]", "decision_date=%s kind=%s effective_on=%s" % (mo.get("decision_date"), mo.get("kind"), mo.get("effective_on")),
        "2026-10-30 会议确认维持(维持条目无生效日) (AJ)", mo.get("decision_date") == "2026-10-30" and mo.get("kind") == "policy_maintenance"
        and not mo.get("effective_on") and bound("2026-10-30 会议确认维持", "维持条目无生效日"))
    gaps = ((CUT - dt.date(2026, 9, 24)).days, (CUT - dt.date(2026, 9, 18)).days, (CUT - dt.date(2026, 10, 30)).days)
    line = [l for l in MAP.splitlines() if "RC-JP-BOJ-TARGET-2026-09" in l]
    ltok = re.compile(r"(?<!\d)%d ?天" % gaps[0]).search(line[0]) if line else None
    ltok2 = re.compile(r"(?<!\d)%d ?天" % gaps[1]).search(line[0]) if line else None
    ltok3 = re.compile(r"(?<!\d)%d ?天" % gaps[2]).search(line[0]) if line else None
    add("④政策面·日历", "截止日 − 生效日/决议日/维持日", "距生效 %d 天 / 距决议 %d 天 / 距维持 %d 天" % gaps,
        "MAP_REPORT 政策官方记录面(日本行) 距上次调整/距决议/距维持", bool(ltok and ltok2 and ltok3) and gaps == (60, 66, 24), line[0][:160] if line else "未找到行")
    lpr = [e for e in cal_entries if e.get("metric_id") == "CN_LPR_1Y"]
    l11 = [e for e in lpr if e.get("first_publish_on_or_after") == "2026-11-20"]
    l08 = [e for e in lpr if e.get("obs_from", "9999") <= "2026-08-20" <= e.get("obs_to", "0000")]
    add("④政策面·日历", "release_calendar.entries[metric_id=CN_LPR_1Y]", "2026-11-20 条目=%s time=%s basis=%s; 覆盖 2026-08-20 的条目数=%d" % (bool(l11), l11[0].get("time") if l11 else None, l11[0].get("basis") if l11 else None, len(l08)),
        "发布日历实录 RC-CN-LPR-2026M11，公布时刻 09:00; 三个月前锚发布 2026-08-20 官方惯例时刻，非本轮日历实录 (AJ)",
        bool(l11) and l11[0].get("time") == "09:00" and l11[0].get("basis") == "user_directive" and not l08
        and bound("RC-CN-LPR-2026M11，公布时刻 09:00", "三个月前锚发布 2026-08-20，官方惯例时刻，非本轮日历实录"))
    pdf = plan.get("policy_doc_facts") or []
    uscal = [e for e in cal_entries if any(k in json.dumps(e, ensure_ascii=False) for k in ("FOMC", "DFEDTAR", "纪要", "minutes"))]
    add("④政策面·来源", "research_plan.policy_doc_facts[0].published_on", pdf[0].get("published_on") if pdf else None, "FOMC 2026年10月会议纪要 2026-11-18 发布 (AJ 证伪面)",
        bool(pdf) and pdf[0].get("published_on") == "2026-11-18" and bound("2026-11-18 发布"))
    add("④政策面·来源", "release_calendar.entries 中美国政策/纪要条目数 (命中条目: %s)" % ",".join(str(e.get("entry_id")) for e in uscal), len(uscal), "日历内仅有 FOMC 2026年10月会议纪要条目 (AJ 证伪面)",
        len(uscal) == 0 and not bound("日历内仅有 FOMC 2026年10月会议纪要条目"),
        "冻结日历 v%s 无美国政策与纪要条目; 纪要发布日来自引擎 policy_doc_facts(basis=%s), 非日历实录" % (cal.get("version"), pdf[0].get("basis") if pdf else None))
    regids = set(m.get("metric_id") for m in reg.get("metrics", []))
    dg = [g for g in plan.get("dimension_gaps", []) if g.get("metric_id") == "JP_POLICY_TARGET"]
    add("④政策面·四口径", "metric_registry.metrics 是否含 JP_POLICY_TARGET; research_plan.dimension_gaps", "注册表含=%s; dimension_gaps=%s" % ("JP_POLICY_TARGET" in regids, dg[0].get("gap") if dg else None),
        "宣布目标序列不在引擎注册表 (AJ 政策口径披露/日本走位)", "JP_POLICY_TARGET" not in regids and bool(dg) and dg[0].get("gap") == "registry_absent"
        and bound("宣布目标序列不在引擎注册表"))
    pcl = plan.get("policy_event_clusters", {}).get("clusters", [])
    add("④政策面·来源", "research_plan.policy_event_clusters.clusters", [(c["cluster_id"], c["date_from"], c["regions"], [(e["date"], e["effective_date"], e["delta_bp"]) for e in c["events"]]) for c in pcl],
        "引擎政策事件簇记 2026-09-16 决议、2026-09-17 生效 (AJ C1)",
        len(pcl) == 2 and pcl[1]["events"][0]["date"] == "2026-09-16" and pcl[1]["events"][0]["effective_date"] == "2026-09-17"
        and pcl[1]["events"][0]["delta_bp"] == 25 and all(c["regions"] == ["US"] for c in pcl) and bound("引擎政策事件簇记 2026-09-16 决议"))

    # ---------------------------------------------------------------- E 利率分解与资产窗
    trio = plan["us_rates_trio"]
    common = sorted(set(sdict("UST_10Y")) & set(sdict("TIPS_10Y")) & set(sdict("BEI_10Y")))
    to_d = max(d for d in common if d <= CUT)
    from_d = to_d - dt.timedelta(days=30)
    to12 = to_d - dt.timedelta(days=365)
    add("⑤利率窗", "series_store UST_10Y∩TIPS_10Y∩BEI_10Y 共同交易日", "窗末=%s 窗起(−30天)=%s 12月窗起(−365天)=%s 均为共同交易日=%s" % (to_d, from_d, to12, from_d in common and to12 in common),
        "近一月共同交易日窗(2026-10-20→2026-11-19), 12 个月窗(2025-11-19→2026-11-19) (AJ M1/传导面)",
        to_d == dt.date(2026, 11, 19) and from_d == dt.date(2026, 10, 20) and to12 == dt.date(2025, 11, 19) and from_d in common and to12 in common
        and trio["window"]["from"] == "2026-10-20" and trio["window"]["to"] == "2026-11-19" and bound("近一月共同交易日窗(2026-10-20→2026-11-19)", "12 个月窗(2025-11-19→2026-11-19)"))
    toks1 = {"UST_10Y": "名义 -8bp", "TIPS_10Y": "+11bp", "BEI_10Y": "-19bp"}
    toks12 = {"UST_10Y": "+91bp", "TIPS_10Y": "+102bp", "BEI_10Y": "-11bp"}
    chg1, chg12 = {}, {}
    for m in ("UST_10Y", "TIPS_10Y", "BEI_10Y"):
        chg1[m] = (val(m, to_d) - val(m, from_d)) * 100
        chg12[m] = (val(m, to_d) - val(m, to12)) * 100
        add("⑤利率窗", "series_store.%s %s→%s" % (m, from_d, to_d), "%s→%s = %+.1f bp" % (fmt(val(m, from_d)), fmt(val(m, to_d)), chg1[m]),
            "%s (AJ M1/传导面; 引擎 us_rates_trio.chg_bp=%s)" % (toks1[m], trio["chg_bp"].get(m)),
            round(chg1[m]) == round(trio["chg_bp"].get(m, 999)) and within(chg1[m], int(toks1[m].replace("名义 ", "").replace("bp", "")), 0.51) and bound(toks1[m]))
        add("⑤利率窗", "series_store.%s %s→%s" % (m, to12, to_d), "%s→%s = %+.1f bp" % (fmt(val(m, to12)), fmt(val(m, to_d)), chg12[m]),
            "%s (AJ M1/传导面; 引擎 chg_bp_12m=%s)" % (toks12[m], trio.get("chg_bp_12m", {}).get(m)),
            round(chg12[m]) == round(trio.get("chg_bp_12m", {}).get(m, 999)) and within(chg12[m], int(toks12[m].replace("bp", "")), 0.51) and bound(toks12[m]))
    res1 = chg1["UST_10Y"] - (chg1["TIPS_10Y"] + chg1["BEI_10Y"])
    res12 = chg12["UST_10Y"] - (chg12["TIPS_10Y"] + chg12["BEI_10Y"])
    add("⑤利率窗·恒等式", "名义Δ − (实际Δ + 盈亏平衡Δ) 两窗", "残差 一月=%+.3f bp, 12月=%+.3f bp" % (res1, res12),
        "名义 -8bp=实际利率(TIPS_10Y)+11bp+盈亏平衡(BEI_10Y)-19bp; +91bp=+102bp-11bp (两窗恒等残差均为 0) (AJ M1)",
        abs(res1) < 0.01 and abs(res12) < 0.01 and trio.get("identity_residual_bp") == 0 and trio.get("identity_residual_bp_12m") == 0 and bound("两窗恒等残差均为 0"))
    lev = val("TIPS_10Y", to_d) + val("BEI_10Y", to_d)
    resid_days = [abs(val("UST_10Y", d) - (val("TIPS_10Y", d) + val("BEI_10Y", d))) for d in common if from_d <= d <= to_d]
    add("⑤利率窗·恒等式", "共同交易日逐日 名义=实际+盈亏平衡 (窗内 %d 日)" % len(resid_days), "末日 %.2f+%.2f=%.2f; 窗内最大绝对残差=%.4f" % (val("TIPS_10Y", to_d), val("BEI_10Y", to_d), lev, max(resid_days)),
        "十年期美债名义利率 5.04%(2026-11-19) (AJ M1)", within(lev, 5.04, 0.0051) and max(resid_days) <= 0.011 and bound("十年期美债名义利率 5.04%(2026-11-19)"))
    add("⑤利率窗·最新值", "series_store.TIPS_10Y 末观测", "%s@%s" % (fmt(series("TIPS_10Y")[-1][1]), series("TIPS_10Y")[-1][0]), "最新 2.88(观测 2026-11-19) (AJ 传导面第1环)",
        series("TIPS_10Y")[-1] == (dt.date(2026, 11, 19), 2.88) and bound("最新 2.88(观测 2026-11-19)"))
    add("⑤利率窗·最新值", "series_store.BEI_10Y 末观测", "%s@%s (窗末 2026-11-19 值=%s)" % (fmt(series("BEI_10Y")[-1][1]), series("BEI_10Y")[-1][0], fmt(val("BEI_10Y", "2026-11-19"))),
        "最新 2.16(观测 2026-11-19) (AJ 传导面第2环)",
        series("BEI_10Y")[-1] == (dt.date(2026, 11, 19), 2.16) and bound("最新 2.16(观测 2026-11-19)"),
        "序列最新观测为 %s@%s; 2.16 是共同交易日窗末(2026-11-19)值而非最新观测" % (fmt(series("BEI_10Y")[-1][1]), series("BEI_10Y")[-1][0]))
    add("⑤利率窗·最新值", "series_store.UST_10Y 末观测", "%s@%s" % (fmt(series("UST_10Y")[-1][1]), series("UST_10Y")[-1][0]), "同期十年期名义利率 5.04 (AJ 传导面第1环)",
        series("UST_10Y")[-1] == (dt.date(2026, 11, 19), 5.04) and bound("同期十年期名义利率 5.04"))

    def pct(m, d0, d1):
        a, b = val(m, d0), val(m, d1)
        return None if a is None or b is None else (b / a - 1.0) * 100.0

    def nearest(m, d):
        return min(series(m), key=lambda x: (abs((x[0] - d).days), x[0]))

    am = {r["metric_id"]: r for r in plan["asset_moves"]["rows"]}
    echoar = {r["metric_id"]: r for r in aj["reader_map"]["asset_returns_echo"]}
    ajtok_engine = {"SPX": "SPX -5.51%", "NIKKEI225": "NIKKEI225 -9.98%", "SHCOMP": "SHCOMP -4.11%", "DAX": "DAX +0.11%", "VIX": "VIX +38.87%", "DXY": "+2.23%"}
    eng_mine = {}
    for m in ("SPX", "SHCOMP", "DAX", "NIKKEI225", "VIX", "DXY", "GOLD_F", "UST_10Y"):
        f = nearest(m, dt.date(2026, 10, 23))
        t = series(m)[-1]
        p = pct(m, f[0], t[0])
        eng_mine[m] = p
        row = am.get(m, {})
        e = echoar.get(m)
        rtxt = "%s (%s→%s; 引擎资产月窗 chg_pct=%s" % (ajtok_engine.get(m, "引擎面未入判断档文字"), f[0], t[0], row.get("chg_pct"))
        if e:
            rtxt += "; AJ asset_returns_echo=%s 窗 %s→%s" % (e.get("chg_pct"), e["window"]["from"], e["window"]["to"])
        rtxt += ")"
        ok = (f[0] == dt.date(2026, 10, 23) and within(p, row.get("chg_pct"), 0.0051) and row.get("window", {}).get("to") == t[0].isoformat()
              and within(f[1], row.get("from_value"), 0.0051) and within(t[1], row.get("to_value"), 0.0051))
        if e:
            ok = ok and within(p, e.get("chg_pct"), 0.0051) and e["window"]["to"] == t[0].isoformat()
        if m in ajtok_engine:
            ok = ok and bound(ajtok_engine[m]) and within(p, float(ajtok_engine[m].replace("%", "").split(" ")[-1]), 0.0051)
        add("⑤资产窗·引擎窗", "series_store.%s 最近于 2026-10-23 的观测 → 末观测" % m, "%s(%s)→%s(%s) = %.4f%%" % (fmt(f[1]), f[0], fmt(t[1]), t[0], p), rtxt, ok)
    d0, d1 = dt.date(2026, 10, 23), dt.date(2026, 11, 20)
    close_tok = {"SPX": ("标普500指数下跌百分之九点三六", -9.36, "标普500指数 -9.36%"), "NIKKEI225": ("日经225下跌百分之九点九八", -9.98, "日经225 -9.98%"),
                 "SHCOMP": ("上证综指下跌百分之四点二五", -4.25, "上证综指 -4.25%"), "DAX": ("DAX 下跌百分之一点五零", -1.50, "DAX -1.50%"),
                 "CAC40": ("法国CAC40 +1.86%", 1.86, None), "VIX": ("VIX 上涨百分之八十四点五二", 84.52, "VIX +84.52%(19.45→35.89)"),
                 "DXY": ("美元指数 +1.96%", 1.96, None)}
    close_mine = {}
    for m, (tok, num, tok2) in close_tok.items():
        p = pct(m, d0, d1)
        close_mine[m] = p
        ok = within(p, num, 0.0051) and bound(tok) and (tok2 is None or bound(tok2))
        add("⑤资产窗·收盘口径", "series_store.%s@2026-10-23 → @2026-11-20" % m, "%s→%s = %.4f%%" % (fmt(val(m, d0)), fmt(val(m, d1)), p), "%s (%s; AJ 证据与口径/C4/传导面)" % (num, tok), ok)
    for m, tok, num in (("SPX", "SPX +4.25%", 4.25), ("VIX", "VIX -24.74%", -24.74), ("DAX", "DAX +1.64%", 1.64)):
        p = pct(m, d1, CUT)
        add("⑤资产窗·盘中", "series_store.%s@2026-11-20 → @2026-11-23" % m, "%s→%s = %.4f%%" % (fmt(val(m, d1)), fmt(val(m, CUT)), p), "%s (%s; AJ 传导面第3环)" % (num, tok),
            within(p, num, 0.0051) and bound(tok))
    add("⑤资产窗·最新值", "series_store.DAX@2026-11-23", fmt(val("DAX", CUT)), "DAX 最新一期为 25209.45(观测 2026-11-23，盘中快照) (AJ C4)",
        within(val("DAX", CUT), 25209.45, 0.0051) and bound("DAX 最新一期为 25209.45"))
    g_e = abs(eng_mine["SPX"] - eng_mine["NIKKEI225"])
    g_c = abs(close_mine["SPX"] - close_mine["NIKKEI225"])
    g_es = abs(eng_mine["SPX"] - eng_mine["SHCOMP"])
    add("⑤资产窗·美日相近?", "引擎窗 SPX 与 NIKKEI225 跌幅差 (series_store 直算)", "引擎窗 |−5.51−(−9.98)|=%.2f pp; 收盘口径 |−9.36−(−9.98)|=%.2f pp" % (g_e, g_c),
        "两种口径下美日股指跌幅均相近 (AJ C4; 渲染于 FULL_REPORT.md / report.md)", g_c < 1.0 and g_e < 1.0,
        "引擎窗两跌幅相差 %.2f 个百分点(日经跌幅约为标普的 %.2f 倍), 不相近; 仅收盘口径相近" % (g_e, abs(eng_mine["NIKKEI225"] / eng_mine["SPX"])))
    add("⑤资产窗·排序", "引擎窗 SPX 与 SHCOMP 跌幅差", "%.2f pp (<2)" % g_es, "SPX 与 SHCOMP 落差不足两个百分点，该排序弱化 (AJ M1 第3环)", g_es < 2.0 and bound("SPX 与 SHCOMP 落差不足两个百分点"))
    add("⑤资产窗·排序", "收盘口径 美日 vs 中国 跌幅", "美 %.2f / 日 %.2f / 中 %.2f / DAX %.2f" % (close_mine["SPX"], close_mine["NIKKEI225"], close_mine["SHCOMP"], close_mine["DAX"]),
        "收盘口径下美日股指跌幅相近且深于中国与欧洲 (AJ M1 第3环)", close_mine["SPX"] < close_mine["SHCOMP"] and close_mine["NIKKEI225"] < close_mine["SHCOMP"]
        and close_mine["SPX"] < close_mine["DAX"] and close_mine["NIKKEI225"] < close_mine["DAX"] and bound("收盘口径下美日股指跌幅相近且深于中国与欧洲"))
    in_full = [l for l in FULL.splitlines() if "两种口径下美日股指跌幅均相近" in l]
    in_md = [l for l in MD.splitlines() if "两种口径下美日股指跌幅均相近" in l]
    add("⑩渲染", "读者报告中的「两种口径下美日股指跌幅均相近」", "FULL_REPORT.md %d 处 / report.md %d 处 / MAP_REPORT.md %d 处" % (len(in_full), len(in_md), MAP.count("跌幅均相近")),
        "C4 陈述全文内联渲染", bool(in_full) and bool(in_md), "该句进入读者面(L3 全文内联)")

    # ---------------------------------------------------------------- F 转折候选
    cands = plan["turning_candidates"]["candidates"]

    def cval(m, ym, derived):
        return yoy_level(m, ym) if derived else month_val(m, ym)

    order_ok = all(abs(cands[i]["delta"]) >= abs(cands[i + 1]["delta"]) - 1e-12 for i in range(len(cands) - 1))
    add("⑥转折候选", "research_plan.turning_candidates.candidates 排序与数量", "n=%d 按|Δ|降序=%s" % (len(cands), order_ok), "候选池九 项(引擎按三个月变动幅度列出) (AJ 转折取舍)", len(cands) == 9 and order_ok and bound("候选池 九 项"))
    for cd in cands:
        m = cd["metric_id"]
        derived = "派生于水平" in (cd.get("unit") or "")
        b, a = cval(m, cd["from_ym"], derived), cval(m, cd["to_ym"], derived)
        tol = 0.0006 if derived else 0.0051  # 派生同比: 序列值已四舍五入到 4 位, 复算容差放宽到 0.0006
        dl = (round(a, 4) - round(b, 4)) if (a is not None and b is not None) else None
        add("⑥转折候选·值", "series_store.%s %s → %s%s" % (m, cd["from_ym"], cd["to_ym"], "(同比派生)" if derived else ""),
            "%s → %s Δ=%s" % (fmt(None if b is None else round(b, 4)), fmt(None if a is None else round(a, 4)), fmt(None if dl is None else round(dl, 4))),
            "%s → %s Δ=%s (引擎候选面)" % (cd["value_before"], cd["value_after"], cd["delta"]),
            within(b, cd["value_before"], tol) and within(a, cd["value_after"], tol) and within(dl, cd["delta"], 0.0011 if derived else 0.011))
        best = None
        to = "2026-02"
        while to <= "2026-11":
            frm = ym_add(to, -3)
            x0, x1 = cval(m, frm, derived), cval(m, to, derived)
            if x0 is not None and x1 is not None:
                dd = abs(x1 - x0)
                if best is None or dd > best[0] + 1e-12:
                    best = (dd, frm, to)
            to = ym_add(to, 1)
        add("⑥转折候选·最大窗", "series_store.%s 过去12个月全部3月窗 |Δ| 最大者" % m, "%s→%s |Δ|=%.4f" % (best[1], best[2], best[0]) if best else "无",
            "%s→%s (引擎候选窗口)" % (cd["from_ym"], cd["to_ym"]), best is not None and best[1] == cd["from_ym"] and best[2] == cd["to_ym"])
    ends = [(cd["metric_id"], cd["to_ym"]) for cd in cands]
    rest = [t for m, t in ends if m not in ("JP_CPI_TOKYO_YOY", "JP_POLICY_RATE", "CORE_CPI")]
    add("⑥转折·取舍", "转折候选窗口终点 vs 三个月前锚 2026-08-23", "其余六项窗口终点=%s" % sorted(rest), "其余六项…窗口终点均不晚于 2026-05 / 均早于三个月前锚 (AJ 转折取舍/同比基期纪律)",
        len(rest) == 6 and max(rest) <= "2026-05" and bound("其余 六 项", "窗口终点均不晚于 2026-05", "属对照窗之前的转折"))
    add("⑥转折·取舍", "转折窗口终点 vs 三个月前锚", "东京都 2026-09-01 > 2026-08-23; 核心CPI 2026-08-01 < 2026-08-23; 日本政策利率 2026-07-01 < 2026-08-23",
        "①窗口终点落在三个月对照窗 2026-08-23→2026-11-23 之内; ③窗口终点 2026-08-01 略早于三个月前锚; ②窗口终点早于三个月前锚 (AJ 转折取舍)",
        bound("①东京都CPI同比 2026-06→2026-09", "窗口终点落在三个月对照窗 2026-08-23→2026-11-23 之内", "③美国核心CPI同比 2026-05→2026-08", "窗口终点 2026-08-01 略早于三个月前锚", "窗口终点(2026-07)早于三个月前锚(2026-08-23)"))
    add("⑥转折·补选", "转折补选面条数 / 指标", "%d 条 %s" % (len(aj["reader_map"]["turning_supplement"]), [t["metric_id"] for t in aj["reader_map"]["turning_supplement"]]),
        "引擎补选美国工业生产同比 2025-11→2026-02(增长维) (AJ 转折取舍)", len(aj["reader_map"]["turning_supplement"]) == 1 and aj["reader_map"]["turning_supplement"][0]["metric_id"] == "INDPRO")
    tset = set(c["metric_id"] for c in cands)
    add("⑥转折·取舍", "转折候选池内政策维候选", sorted(c["metric_id"] for c in cands if c["dimension"] == "policy"), "候选池内唯一的政策维候选 (AJ 转折1)",
        [c["metric_id"] for c in cands if c["dimension"] == "policy"] == ["JP_POLICY_RATE"])
    jp_before = [month_val("JP_POLICY_RATE", y) for y in ("2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04")]
    add("⑥转折·先后", "series_store.JP_POLICY_RATE 2025-11…2026-04", jp_before, "2026-04 的 0.727…是其后持续收紧的起点 (AJ 转折1)",
        True, "对照事实(不计命中/偏离): 2025-12 与 2026-01 已有两次上调(0.478→0.557→0.728), 2026-01→04 持平; 「起点」仅指最近一轮")

    # ---------------------------------------------------------------- G 证据引用与分级
    refs_idx = {r["ref"]: r for r in ev}
    allrefs = []
    for c in aj["l3"]["contradictions"]:
        allrefs += [("C:" + c["id"], x) for x in c.get("evidence_refs", [])]
    for mch in aj["l3"]["mechanism_chains"]:
        for l in mch["links"]:
            allrefs += [("M:%s#%d" % (mch["id"], l["step"]), x) for x in l.get("evidence_refs", [])]
    for sc in aj["l4"]["scenarios"]:
        allrefs += [("S:" + sc["id"], x) for x in sc["rows"].get("asset_direction", {}).get("evidence_refs", [])]

    def ref_in_series(r):
        try:
            m, d = r.split("@")
        except ValueError:
            return False
        if val(m, d) is not None:
            return True
        return month_val(m, d[:7]) is not None

    miss_idx = [(i, r) for i, r in allrefs if r not in refs_idx]
    add("⑦证据引用", "agent_judgment evidence_refs × evidence_index.json", "引用 %d 条, 不在证据索引=%d" % (len(allrefs), len(miss_idx)), "证据索引 69 行 (AJ)", not miss_idx, "; ".join("%s:%s" % x for x in miss_idx))
    miss_ser = [(i, r) for i, r in allrefs if not ref_in_series(r)]
    add("⑦证据引用", "agent_judgment evidence_refs × series_store", "无法解析到序列观测=%d" % len(miss_ser), "证据索引…全部取自本工单冻结快照 (AJ)", not miss_ser, "; ".join("%s:%s" % x for x in miss_ser))
    add("⑪诚实缺席", "evidence_index.json 行数 / 与 report.json.evidence_index 一致", "%d / %s" % (len(ev), ev == rep.get("evidence_index")), "证据索引共 69 条 (AJ); 证据行: 69 (FULL_REPORT 头)",
        len(ev) == 69 and ev == rep.get("evidence_index") and bound("证据索引共 69 条") and "| 证据行: 69 |" in FULL)
    fact_ids = set(f.get("fact_id") for f in snap.get("facts", []))
    kinds = set(r.get("kind") for r in ev)
    nofact = [r["ref"] for r in ev if r.get("kind") == "snapshot_fact" and r["ref"] not in fact_ids]
    s3bad = []
    for r in ev:
        if r.get("kind") != "snapshot_fact":
            continue
        m, d = r["ref"].split("@")
        if m == "HY_IG_DIFF":
            if val("HY_OAS", d) is None or val("IG_OAS", d) is None:
                s3bad.append(r["ref"])
        elif m not in store or val_any(m, d) is None:
            s3bad.append(r["ref"])
    s3snap = set()
    for x in rep["steps"]:
        if str(x.get("step", "")).startswith("S3_overview"):
            s3snap.add((x.get("envelope") or {}).get("snapshot_id"))
    add("⑪诚实缺席", "evidence_index[*].kind / ref ∈ snapshot.facts.fact_id 或 S3 概览信封", "kind=%s; 事实行不在 facts=%d; 信封行不可回贴序列=%d; S3 信封快照=%s" % (
        sorted(kinds), len(nofact), len(s3bad), sorted(x for x in s3snap if x)), "证据索引共 69 条，全部取自本工单冻结快照 research_snapshot_20261123 (AJ)",
        kinds == {"snapshot_fact", "s3_envelope"} and not nofact and not s3bad and s3snap == {"research_snapshot_20261123"}, "; ".join(s3bad))
    fdict = {f.get("fact_id"): f for f in snap.get("facts", [])}
    fbad = []
    for r in ev:
        f = fdict.get(r["ref"])
        if not f or f.get("value_type") != "level":
            continue
        m, d = r["ref"].split("@")
        v = val_any(m, d)
        if v is None or abs(f["value"] - v) > 0.0051 + 1e-6 * abs(v):
            fbad.append("%s:fact=%s series=%s" % (r["ref"], f.get("value"), fmt(v)))
    add("⑦证据引用", "snapshot.facts(level).value vs series_store 同日值 (证据索引 69 行)", "不一致=%d" % len(fbad), "L1 事实层与 series_store 逐行一致(证据面自洽)", not fbad, "; ".join(fbad))
    notin = ["JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY", "CN_OMO_7D", "CN_POLICY_OVERNIGHT"]
    evm = set(r.get("metric_id") for r in ev)
    add("⑪诚实缺席", "evidence_index[*].metric_id 是否含四指标", {m: (m in evm) for m in notin}, "该序列不在本轮证据索引(东京/日本GDP/七天逆回购/隔夜) (AJ)",
        all(m not in evm for m in notin) and bound("该序列不在本轮证据索引"))
    lv = {mch["id"]: [l["evidence_level"] for l in mch["links"]] for mch in aj["l3"]["mechanism_chains"]}
    hyp_ok = all("【假设】" in l["text"] for mch in aj["l3"]["mechanism_chains"] for l in mch["links"] if l["evidence_level"] != "E1")
    add("⑦证据分级", "l3.mechanism_chains[*].links[*].evidence_level", lv, "M1 三环 E1/E2/E2, M2 两环 E1/E2; 非 E1 环正文带【假设】", hyp_ok
        and lv.get("M1-POLICY-RATES-ASSETS") == ["E1", "E2", "E2"] and lv.get("M2-CN-PPI-CPI-SCISSORS") == ["E1", "E2"])
    APPX.append("=== contract verdicts")

    def norm(s):
        return re.sub(r"\s+", "", str(s)).replace("\\", "").replace("*", "")

    NMAP, NFULL, NMD = norm(MAP), norm(FULL), norm(MD)
    notes = aj["quality_gate_notes"]

    def note_by_prefix(p):
        hit = [s for s in notes if s.startswith(p)]
        return hit[0] if hit else ""

    rm = aj["reader_map"]

    # ---------------------------------------------------------------- H 历史类比
    an = {}
    s7 = {}
    for st in rep["steps"]:
        if st.get("step") == "S6_analog":
            an = (st.get("envelope") or {}).get("data") or {}
        if st.get("step") == "S7_mode_gate":
            s7 = st.get("gate") or {}
    hz = rm.get("history_zero_case_note") or ""
    add("⑧历史类比", "reader_map.history_periods", "段数=%d" % len(rm.get("history_periods") or []),
        "历史类比取零段(契约允许 0..3 段，如实写明) (AJ)", len(rm.get("history_periods") or []) == 0 and bound("历史类比取零段"))
    cand = an.get("candidates") or {}
    add("⑧历史类比", "S6_analog.data.candidates",
        "scanned=%s valid=%s insufficient=%s overlap=%s; scanned-insufficient=%d" % (
            cand.get("scanned"), cand.get("valid"), cand.get("dropped_insufficient"), cand.get("dropped_overlap"),
            (cand.get("scanned") or 0) - (cand.get("dropped_insufficient") or 0)),
        "扫描 1871 个候选月，有效候选 74 个，因特征不足剔除 1785 个、同簇去重剔除 12 个 (AJ)",
        cand.get("scanned") == 1871 and cand.get("valid") == 74 and cand.get("dropped_insufficient") == 1785
        and cand.get("dropped_overlap") == 12 and 1871 - 1785 == 74 + 12
        and bound("扫描 1871 个候选月", "有效候选 74 个", "因特征不足剔除 1785 个", "同簇去重剔除 12 个"))
    top = an.get("top") or []
    months = [t.get("candidate_month") for t in top]
    add("⑧历史类比", "S6_analog.data.top[*].candidate_month / rank", "%s / ranks=%s" % (months, [t.get("rank") for t in top]),
        "TOP-5 独立簇代表为 2025-03、2022-06、2023-10、2021-02、2020-01 (AJ)",
        months == ["2025-03", "2022-06", "2023-10", "2021-02", "2020-01"] and [t.get("rank") for t in top] == [1, 2, 3, 4, 5]
        and bound("TOP-5 独立簇代表为 2025-03、2022-06、2023-10、2021-02、2020-01"))
    skeys = [(t.get("n_missing"), t.get("distance"), t.get("candidate_month")) for t in top]
    add("⑧历史类比", "S6_analog.data.sort_basis × top[*](n_missing, distance, month) 单调性", skeys,
        "引擎排序依据=缺席特征数优先、其后距离，名次非纯距离序 (AJ)",
        skeys == sorted(skeys) and bound("缺席特征数优先、其后距离，名次非纯距离序"))
    dimorder = ["volatility", "rates", "inflation", "valuation", "credit", "growth"]
    t0 = top[0] if top else {}
    sh = [round(((t0.get("dims") or {}).get(d, {}).get("contribution_share") or 0) * 100, 2) for d in dimorder]
    add("⑧历史类比", "S6_analog.data.top[0].dims[*].contribution_share×100 (%s)" % t0.get("candidate_month"), sh,
        "以首位候选为例各维对距离的贡献份额(%)为 volatility 42.13、rates 40.66、inflation 10.54、valuation 6.67、credit 0.00、growth 0.00 (AJ)",
        sh == [42.13, 40.66, 10.54, 6.67, 0.0, 0.0] and "2025-03" in months
        and bound("volatility 42.13、rates 40.66、inflation 10.54、valuation 6.67、credit 0.00、growth 0.00"))
    badc = []
    for t in top:
        d2 = sum((v.get("z_gap") or 0) ** 2 for v in (t.get("dims") or {}).values())
        fd = t.get("features_detail") or {}
        d3 = math.sqrt(sum((f.get("w_norm") or 0) * (f.get("gap") or 0) ** 2 for f in fd.values()))
        if abs(math.sqrt(d2) - (t.get("distance") or 0)) > 1e-5 or abs(d3 - (t.get("distance") or 0)) > 1e-5:
            badc.append("%s: sqrt(Σz_gap²)=%.6f sqrt(Σw_norm·gap²)=%.6f distance=%s" % (t.get("candidate_month"), math.sqrt(d2), d3, t.get("distance")))
        for d, v in (t.get("dims") or {}).items():
            if d2 and abs((v.get("z_gap") or 0) ** 2 / d2 - (v.get("contribution_share") or 0)) > 1e-5:
                badc.append("%s/%s: share=%.6f vs z_gap²/Σ=%.6f" % (t.get("candidate_month"), d, v.get("contribution_share"), (v.get("z_gap") or 0) ** 2 / d2))
        APPX.append("analog top rank=%s month=%s n_missing=%s Σw_norm=%.6f missing_features=%s" % (
            t.get("rank"), t.get("candidate_month"), t.get("n_missing"), sum((f.get("w_norm") or 0) for f in fd.values()), t.get("missing_features")))
    add("引擎面自洽", "S6_analog top[0..4]: distance=√(Σ维 z_gap²)=√(Σ特征 w_norm·gap²); 份额=z_gap²/Σ", "恒等式偏离=%d" % len(badc),
        "引擎距离与份额的内部恒等", not badc, "; ".join(badc))
    DROP_DIM = {"UNEMPLOYMENT_level": "growth", "NFP_3m_chg": "growth", "INDPRO_yoy": "growth", "RSAFS_yoy": "growth", "GDP_yoy": "growth",
                "CORE_CPI_yoy": "inflation", "CPI_yoy": "inflation", "FED_FUNDS_level": "rates", "FED_FUNDS_d12m": "rates",
                "HY_OAS_d12m": "credit", "HY_IG_gap_d12m": "credit", "SPX_PE_TTM_level": "valuation"}
    dropped = an.get("features_dropped_at_anchor") or {}
    sv = an.get("state_vector") or {}
    dims6 = ["growth", "inflation", "rates", "credit", "volatility", "valuation"]
    unk = [f for f in dropped if f not in DROP_DIM]
    cov_mine, cov_eng = {}, {}
    for d in dims6:
        nd = sum(1 for f, dm in DROP_DIM.items() if dm == d and f in dropped)
        np_ = len((sv.get(d) or {}).get("features") or {})
        cov_mine[d] = round(np_ / float(np_ + nd), 4) if (np_ + nd) else None
        cov_eng[d] = (sv.get(d) or {}).get("coverage")
    add("⑧历史类比", "S6_analog.data.features_dropped_at_anchor(%d)+state_vector[*].features → 各维覆盖率=在场/(在场+缺席)" % len(dropped), cov_mine,
        "维度覆盖率…增长 0.17、通胀 0.33、利率 0.75、信用 0.50、波动 1.00、估值 0.50 (AJ); 引擎面=%s" % cov_eng,
        not unk and len(dropped) == 12 and set(dims6) == set(sv.keys())
        and all(cov_mine[d] is not None and cov_eng.get(d) is not None and abs(cov_mine[d] - cov_eng[d]) <= 6e-5 for d in dims6)
        and [round(cov_mine[d], 2) for d in dims6] == [0.17, 0.33, 0.75, 0.5, 1.0, 0.5]
        and bound("增长 0.17、通胀 0.33、利率 0.75、信用 0.50、波动 1.00、估值 0.50"))
    grp = {"release_lag": [], "no_value_at_anchor": [], "hist": []}
    for f, r in dropped.items():
        k = next((x for x in ("release_lag", "no_value_at_anchor") if str(r).startswith(x)), "hist")
        grp[k].append(f)
    setg = {k: sorted(v) for k, v in grp.items()}
    add("⑧历史类比", "S6_analog.data.features_dropped_at_anchor[*] 理由分组", "%d/%d/%d: %s" % (len(grp["hist"]), len(grp["no_value_at_anchor"]), len(grp["release_lag"]), setg),
        "锚点月有 12 项特征缺席(历史长度不足 36 个月——HY_IG_gap_d12m、HY_OAS_d12m；序列止于锚点前两个月——CORE_CPI_yoy、CPI_yoy、GDP_yoy、SPX_PE_TTM_level；月度指标在锚点月无观测——FED_FUNDS_d12m…UNEMPLOYMENT_level) (AJ)",
        setg["hist"] == ["HY_IG_gap_d12m", "HY_OAS_d12m"] and setg["no_value_at_anchor"] == ["CORE_CPI_yoy", "CPI_yoy", "GDP_yoy", "SPX_PE_TTM_level"]
        and setg["release_lag"] == ["FED_FUNDS_d12m", "FED_FUNDS_level", "INDPRO_yoy", "NFP_3m_chg", "RSAFS_yoy", "UNEMPLOYMENT_level"]
        and bound("锚点月有 12 项特征缺席", "HY_IG_gap_d12m、HY_OAS_d12m", "CORE_CPI_yoy、CPI_yoy、GDP_yoy、SPX_PE_TTM_level",
                  "FED_FUNDS_d12m、FED_FUNDS_level、INDPRO_yoy、NFP_3m_chg、RSAFS_yoy、UNEMPLOYMENT_level"))
    lagm = {m: (series(m)[-1][0].strftime("%Y-%m") if series(m) else None) for m in ("UNEMPLOYMENT", "INDPRO", "FED_FUNDS", "NFP", "RSAFS")}
    add("⑧历史类比", "series_store 末观测月: UNEMPLOYMENT/INDPRO/FED_FUNDS/NFP/RSAFS (release_lag 六项对应序列)", lagm,
        "月度指标在锚点月(2026-11)无观测 (AJ)", all(v == "2026-10" for v in lagm.values()), str(lagm))
    wts = an.get("weights") or {}
    ws = sum((wts.get(d) or 0) * ((sv.get(d) or {}).get("coverage") or 0) for d in dims6)
    wsum_eng = (an.get("feature_set") or {}).get("wsum")
    add("引擎面自洽", "S6_analog.data.weights × state_vector.coverage 求和", "%.6f" % ws, "feature_set.wsum=%s" % wsum_eng,
        abs(ws - 0.541667) <= 1e-6 and abs((wsum_eng or 0) - 0.541667) <= 1e-6)
    svv = {}
    for d in dims6:
        for f, fv in ((sv.get(d) or {}).get("features") or {}).items():
            svv[f] = fv.get("value")
    lvbad = []
    for f, v in sorted(svv.items()):
        base = f[:-len("_level")] if f.endswith("_level") else None
        if base in ("BEI_10Y", "UST_10Y", "TIPS_10Y", "CURVE_2S10S", "HY_OAS", "VIX", "SPX_CAPE"):
            s = series(base)[-1] if series(base) else (None, None)
            if s[0] is None or s[0] > CUT or v is None or abs(v - s[1]) > 5e-7:
                lvbad.append("%s: 锚值=%s 序列末值=%s@%s" % (f, v, s[1], s[0]))
    hg = last_le("HY_OAS", CUT)
    igv = last_le("IG_OAS", CUT)
    if hg and igv and abs(hg[1] - igv[1] - (svv.get("HY_IG_gap_level") or -99)) > 0.0051:
        lvbad.append("HY_IG_gap_level: 锚值=%s HY_OAS−IG_OAS=%.4f" % (svv.get("HY_IG_gap_level"), hg[1] - igv[1]))
    ic = series("ICSA")[-4:]
    icm = (sum(v for _, v in ic) / 4.0) if len(ic) == 4 else None
    if icm is None or abs(icm - (svv.get("ICSA_4w_avg") or -1)) > 0.51:
        lvbad.append("ICSA_4w_avg: 锚值=%s 末4周均值=%s(%s..%s)" % (svv.get("ICSA_4w_avg"), icm, ic[0][0] if ic else None, ic[-1][0] if ic else None))
    add("⑧历史类比", "S6_analog.data.state_vector 水平特征锚值 vs series_store 末观测(≤截止日)", "偏离=%d" % len(lvbad),
        "锚月 2026-11 状态向量(BEI_10Y 2.15、UST_10Y 5.04、TIPS_10Y 2.88、VIX 27.01、HY_OAS 3.52、CURVE_2S10S 0.29、SPX_CAPE、HY_IG_gap=HY_OAS−IG_OAS、ICSA_4w_avg)",
        not lvbad, "; ".join(lvbad))
    d12 = {}
    for f, base in (("UST_10Y_d12m", "UST_10Y"), ("TIPS_10Y_d12m", "TIPS_10Y"), ("CURVE_2S10S_d12m", "CURVE_2S10S")):
        pv = last_le(base, dt.date(2025, 11, 30))
        d12[f] = (svv.get(f), None if not pv else round(svv.get(f.replace("_d12m", "_level")) - pv[1], 4), pv)
    APPX.append("analog d12m 特征: 锚值−2025-11 月末值 → %s" % json.dumps(d12, ensure_ascii=False, default=str))
    add("引擎面自洽", "S6_analog d12m 特征 = 当前水平 − 12 个月前(2025-11)月末水平", {k: v[:2] for k, v in d12.items()},
        "引擎 state_vector.d12m 值", all(v[1] is not None and abs(v[0] - v[1]) <= 0.0056 for v in d12.values()))
    sp = series("SPX")[-22:]
    lr = [math.log(sp[i][1] / sp[i - 1][1]) for i in range(1, len(sp))]
    mu = sum(lr) / len(lr)
    sd1 = math.sqrt(sum((x - mu) ** 2 for x in lr) / (len(lr) - 1))
    sd0 = math.sqrt(sum((x - mu) ** 2 for x in lr) / len(lr))
    APPX.append("analog SPX_rv21: 锚值=%s; 末21日对数收益标准差 样本=%.4f 总体=%.4f (年化×√252: %.4f / %.4f)" % (
        svv.get("SPX_rv21"), sd1, sd0, sd1 * math.sqrt(252), sd0 * math.sqrt(252)))
    disp = an.get("dispersion") or {}
    agree = disp.get("topN_aftermath_sign_agreement") or {}
    exp_keys = set("%s_%s" % (a, h) for a in ("SPX", "UST_10Y", "DXY", "GOLD_F") for h in ("1m", "3m", "6m", "12m"))
    aft = set()
    for t in top:
        af = t.get("aftermath")
        if isinstance(af, dict):
            aft |= set(re.findall(r"(SPX|UST_10Y|DXY|GOLD_F|[A-Z0-9_]+)_(?:1m|3m|6m|12m)", " ".join(sorted(af.keys()))))
    add("⑧历史类比", "S6_analog.data.dispersion.topN_aftermath_sign_agreement 键集", "n=%d 序列=%s" % (len(agree), sorted(set(k.rsplit("_", 1)[0] for k in agree))),
        "事后表现为 DXY、GOLD_F、SPX、UST_10Y 四项 (AJ)",
        set(agree) == exp_keys and bound("事后表现为 DXY、GOLD_F、SPX、UST_10Y 四项"))
    fset = (an.get("feature_set") or {}).get("features") or []
    add("⑧历史类比", "S6_analog.data.feature_set.features(%d) 前缀" % len(fset), sorted(fset),
        "类比面的特征与事后窗全部为美国序列 (AJ)", len(fset) == 13 and not any(f.startswith(("CN_", "JP_", "EA_", "ECB_")) for f in fset)
        and bound("全部为美国序列"))
    mg = an.get("research_mode_gate") or {}
    add("⑧历史类比", "S6_analog.data.research_mode_gate / S7_mode_gate.gate", "descriptive=%s; event_study=%s | S7: %s" % (
        mg.get("descriptive"), (mg.get("event_study") or "")[:40], (s7.get("event_study") or "")[:40]),
        "描述性对齐可用、事件研究被阻断 (AJ)", mg.get("descriptive") == "available" and str(mg.get("event_study", "")).startswith("blocked")
        and str(s7.get("event_study", "")).startswith("blocked") and bound("描述性对齐可用、事件研究被阻断"))
    nrm = an.get("normalization") or {}
    add("⑧历史类比", "S6_analog.data.anchor_month / feature_window_months / normalization.min_history_months", "%s / %s / %s / %s" % (
        an.get("anchor_month"), an.get("feature_window_months"), nrm.get("min_history_months"), (nrm.get("method") or "")[:22]),
        "锚月 2026-11，12 个月特征窗; 历史长度不足 36 个月 (AJ)",
        an.get("anchor_month") == "2026-11" and an.get("feature_window_months") == 12 and nrm.get("min_history_months") == 36
        and "expanding" in (nrm.get("method") or "") and bound("锚月 2026-11，12 个月特征窗"))
    # ---------------------------------------------------------------- I 情景
    scns = {s["id"]: s["rows"] for s in aj["l4"]["scenarios"]}
    A = scns.get("SCN-A-POLICY-DIVERGENCE-EXTENDS") or {}
    B = scns.get("SCN-B-POLICY-CONVERGES") or {}
    Atxt, Btxt = json.dumps(A, ensure_ascii=False), json.dumps(B, ensure_ascii=False)
    at, af = A.get("trigger") or {}, A.get("falsification") or {}
    bt, bf = B.get("trigger") or {}, B.get("falsification") or {}
    uu = last_le("DFEDTARU", CUT)
    u, j = (uu[1] if uu else None), month_val("JP_POLICY_RATE", "2026-10")
    ll = last_le("CN_LPR_1Y", CUT)
    l = ll[1] if ll else None
    usteps_all = sorted(set(round(abs(c[2] - c[1]), 4) for c in changes("DFEDTARU", series("DFEDTARU")[0][0], CUT)))
    usteps_24 = sorted(set(round(abs(c[2] - c[1]), 4) for c in changes("DFEDTARU", dt.date(2024, 11, 23), CUT)))
    add("⑨情景", "series_store.DFEDTARU 变动步长 |Δ| 集合(全史 / 近24月) + 截止日上限", "%s / %s; 截止日=%s@%s" % (usteps_all, usteps_24, u, uu[0] if uu else None),
        "DFEDTARU 上限 4.0 再加一次标准步长=4.25 (AJ 证伪面)",
        min(usteps_all) == 0.25 and usteps_24 == [0.25] and u == 4.0 and bound("DFEDTARU 上限 4.0 再加一次标准步长=4.25") and "≥4.25" in str(at.get("condition")))
    add("⑨情景", "series_store.JP_POLICY_RATE 2026-10 月均", j, "JP_POLICY_RATE 月均 1.227 上取整分位加 0.05=1.28 (AJ 证伪面)",
        within(j, 1.227, 1e-9) and within(round(j, 2) + 0.05, 1.28, 1e-9) and bound("JP_POLICY_RATE 月均 1.227 上取整分位加 0.05=1.28") and "≥1.28" in str(at.get("condition")))
    lsteps = sorted(set(round(abs(c[2] - c[1]), 4) for c in changes("CN_LPR_1Y", series("CN_LPR_1Y")[0][0], CUT)))
    add("⑨情景", "series_store.CN_LPR_1Y 截止日值 + 全史变动步长集合", "%s@%s; 步长=%s" % (l, ll[0] if ll else None, lsteps),
        "CN_LPR_1Y 3.0 下调 0.10=2.90 (AJ 证伪面)",
        l == 3.0 and within(3.0 - 0.10, 2.90, 1e-9) and bound("CN_LPR_1Y 3.0 下调 0.10=2.90") and "2.90" in str(bt.get("condition")))
    stA = {"触发(≥4.25 且 JP≥1.28)": bool(u >= 4.25 and j >= 1.28), "证伪(<3.75 或 JP<1.17)": bool(u < 3.75 or j < 1.17)}
    tokA = ("上限 ≥4.25" in Atxt and "≥1.28" in Atxt and "3.75 以下" in str(af.get("threshold")) and "1.17 以下" in str(af.get("threshold")))
    add("⑨情景", "SCN-A 触发/证伪条件 vs 截止日读数 DFEDTARU=%s, JP_POLICY_RATE(2026-10)=%s" % (u, j), stA,
        "在截止日均未满足 (AJ 证伪面)", tokA and not any(stA.values()) and bound("在截止日均未满足"))
    stB = {"触发(LPR≤2.90 且 上限≤4 且 JP≤1.28)": bool(l <= 2.90 and u <= 4.0 and j <= 1.28), "证伪(LPR 仍为 3 且 上限≥4.25)": bool(l == 3.0 and u >= 4.25)}
    tokB = ("报 2.90 或以下" in Btxt and "上限 ≤4" in Btxt and "月均 ≤1.28" in Btxt and "仍为 3 且 DFEDTARU 上限 ≥4.25" in str(bf.get("threshold")))
    add("⑨情景", "SCN-B 触发/证伪条件 vs 截止日读数 CN_LPR_1Y=%s, DFEDTARU=%s, JP_POLICY_RATE=%s" % (l, u, j), stB,
        "在截止日均未满足 (AJ 证伪面)", tokB and not any(stB.values()) and bound("在截止日均未满足"))
    add("⑨情景", "l4.scenarios[*].rows.trigger.deadline", [at.get("deadline"), bt.get("deadline")], "两情景期限均为 2027-02-28(情景期至 2027-02) (AJ)",
        at.get("deadline") == "2027-02-28" and bt.get("deadline") == "2027-02-28" and bound("两情景期限均为 2027-02-28"))
    need = []
    for sc in (A, B):
        f = sc.get("falsification") or {}
        need += [f.get("metric_id"), sc.get("sensitive_variables"), f.get("secondary_metric_ids")]
    need = sorted(set(x for x in need if isinstance(x, str)))
    add("⑨情景", "l4.scenarios[*] 触发/证伪/敏感指标 ∈ series_store(可观测)", need, "L4 二 个情景各给出可观测触发条件与失效阈值 (AJ 对质面)",
        bool(need) and all(m in store and bool(series(m)) for m in need) and bound("L4 二 个情景各给出可观测触发条件与失效阈值"))
    adA = (A.get("asset_direction") or {}).get("direction") or ""
    adB = (B.get("asset_direction") or {}).get("direction") or ""
    add("⑨情景", "SCN-A/B asset_direction 引用数 vs us_rates_trio.chg_bp / asset_moves", "TIPS 一月窗=%sbp; VIX=%s; DXY=%s; 近一月: SPX=%s NIKKEI=%s VIX=%s" % (
        trio["chg_bp"].get("TIPS_10Y"), am.get("VIX", {}).get("chg_pct"), am.get("DXY", {}).get("chg_pct"), am.get("SPX", {}).get("chg_pct"), am.get("NIKKEI225", {}).get("chg_pct"), am.get("VIX", {}).get("chg_pct")),
        "SCN-A: 实际利率(TIPS_10Y)+11bp、VIX +38.87%、DXY +2.23%; SCN-B: DXY +2.23% 的反向, 与近一月观察(美日股指下跌、VIX 上行)相反 (AJ)",
        trio["chg_bp"].get("TIPS_10Y") == 11.0 and am.get("VIX", {}).get("chg_pct") == 38.87 and am.get("DXY", {}).get("chg_pct") == 2.23
        and "实际利率(TIPS_10Y)+11bp" in adA and "VIX +38.87%" in adA and "DXY +2.23%" in adA and "引擎月窗 DXY +2.23% 的反向" in adB
        and am.get("SPX", {}).get("chg_pct", 0) < 0 and am.get("NIKKEI225", {}).get("chg_pct", 0) < 0 and am.get("VIX", {}).get("chg_pct", 0) > 0 and "美日股指下跌、VIX 上行" in adB)
    # 互补性真值表(不入命中/偏离计数, 供问题清单引用)
    APPX.append("=== 情景互补性真值表 (u=DFEDTARU 上限, j=JP 月均, l=CN_LPR_1Y)")
    open_states = []
    for uu_ in (3.5, 3.75, 4.0, 4.25):
        for jj_ in (1.17, 1.227, 1.28, 1.30):
            for ll_ in (2.9, 3.0):
                s1 = uu_ >= 4.25 and jj_ >= 1.28
                s2 = uu_ < 3.75 or jj_ < 1.17
                s3 = ll_ <= 2.90 and uu_ <= 4.0 and jj_ <= 1.28
                s4 = ll_ == 3.0 and uu_ >= 4.25
                if not (s1 or s2 or s3 or s4):
                    open_states.append("u=%s j=%s l=%s" % (uu_, jj_, ll_))
                APPX.append("u=%s j=%s l=%s → A触发=%s A证伪=%s B触发=%s B证伪=%s" % (uu_, jj_, ll_, s1, s2, s3, s4))
    APPX.append("四类判据均不命中的状态数=%d/32, 例: %s" % (len(open_states), "; ".join(open_states[:6])))

    # ---------------------------------------------------------------- J 读者面
    def inmap(s):
        return norm(s) in NMAP

    add("⑩读者面", "reader_map.headline_conclusion → MAP_REPORT.md", "渲染在场=%s (归一长度 %d)" % (inmap(rm.get("headline_conclusion") or ""), len(norm(rm.get("headline_conclusion") or ""))),
        "判断文字=reader_map 原文(MAP 分工行)", inmap(rm.get("headline_conclusion") or ""))
    for r in rm.get("regions", []):
        ft = r.get("from_to") or ""
        add("⑩读者面", "reader_map.regions[%s].from_to → MAP_REPORT.md" % r["region"], "渲染在场=%s (归一长度 %d)" % (inmap(ft), len(norm(ft))),
            "各地区环境走位原文应完整进入读者报告", inmap(ft))
    links = (rm.get("transmission") or [{}])[0].get("links") or []
    n_obs = sum(1 for x in links if inmap(x.get("observed_fact") or ""))
    n_mc = sum(1 for x in links if inmap(x.get("main_predicts") or "") and inmap(x.get("competing_predicts") or ""))
    n_vn = sum(1 for x in links if norm(x.get("verdict_note") or "") in NMAP)
    add("⑩读者面", "reader_map.transmission[0].links[*].observed_fact → MAP_REPORT.md", "%d/%d 环渲染在场" % (n_obs, len(links)),
        "传导三环观察事实原文应完整进入读者报告", n_obs == 3 and len(links) == 3)
    add("⑩读者面", "reader_map.transmission[0].links[*].main_predicts / competing_predicts → MAP_REPORT.md(对质表)", "%d/%d 环两侧预期渲染在场" % (n_mc, len(links)),
        "对质表=主解释预期/竞争解释预期原文", n_mc == 3 and len(links) == 3)
    add("⑩读者面", "reader_map.transmission[0].links[*].verdict_note → MAP_REPORT.md", "渲染在场=%d/%d" % (n_vn, len(links)),
        "verdict_note 字段(逐环裁定理由)不进渲染 (AJ 引擎缺口披露⑤)", n_vn == 0 and bound("verdict_note 字段(逐环裁定理由)不进渲染"),
        "逐环裁定理由仅存于判断档, 读者报告对质表只显示裁定标签")
    tns = rm.get("turnings") or []
    fm = sum(1 for t in tns if inmap(t.get("first_mover") or ""))
    fo = sum(1 for t in tns if inmap(t.get("follow_or_diverge") or ""))
    na_m = sum(1 for t in tns if inmap(t.get("narrative") or ""))
    na_f = sum(1 for t in tns if norm(t.get("narrative") or "") in NFULL)
    add("⑩读者面", "reader_map.turnings[*].first_mover → MAP_REPORT.md(谁先变)", "%d/%d" % (fm, len(tns)), "转折「谁先变」原文应进入读者报告", fm == 3 and len(tns) == 3)
    add("⑩读者面", "reader_map.turnings[*].follow_or_diverge → MAP_REPORT.md(跟进/背离)", "%d/%d" % (fo, len(tns)), "转折「跟进/背离」原文应进入读者报告", fo == 3 and len(tns) == 3)
    add("引擎面·渲染", "reader_map.turnings[*].narrative → MAP_REPORT.md / FULL_REPORT.md / report.md", "MAP %d/%d; FULL %d/%d" % (na_m, len(tns), na_f, len(tns)),
        "引擎渲染面: narrative 是否进入读者报告(引擎侧行为, 不计判断档偏离)", (na_m == 3 or na_f == 3) and len(tns) == 3,
        "narrative 在 MAP 读者报告渲染 %d/3; 仅在 FULL_REPORT 内联判断档可见时读者地图不显示" % na_m)
    fv = [x.get("face_off_verdict") for x in links]
    add("⑩读者面", "reader_map.transmission[0].links[*].face_off_verdict", fv, "判断=支持主解释 ×2、尚不能区分 ×1 (AJ 对质面)",
        fv == ["支持主解释", "支持主解释", "尚不能区分"] and bound("判断=支持主解释 ×2、尚不能区分 ×1"))
    add("⑩读者面", "MAP_REPORT.md 对质表「判断」列出现次数", "|支持主解释|=%d; |尚不能区分|=%d" % (NMAP.count("|支持主解释|"), NMAP.count("|尚不能区分|")),
        "对质表三行裁定标签应与判断档一致", NMAP.count("|支持主解释|") >= 2 and NMAP.count("|尚不能区分|") >= 1)
    bad_st = []
    for x in links:
        dm, mp, cp = x.get("distinguishing_metric") or "", x.get("main_predicts") or "", x.get("competing_predicts") or ""
        if not (dm and mp and cp and mp != cp and dm in mp and dm in cp and norm(mp) != norm(cp)):
            bad_st.append(dm or "?")
    add("⑩读者面", "links[*]: 区分指标在场且主/竞争预期相异并各自点名区分指标", "不合格=%d" % len(bad_st),
        "传导面 三 环均给出主/竞争两侧对同一区分指标的不同预期 (AJ)", not bad_st, ",".join(bad_st))
    ces = aj["l3"]["contradictions"]
    ce_n = [len(c.get("competing_explanations") or []) for c in ces]
    ce_ok = all(n >= 2 and all(str(x).startswith("【假设】") for x in (c.get("competing_explanations") or [])) for n, c in zip(ce_n, ces))
    add("⑩读者面", "l3.contradictions[*].competing_explanations 条数与【假设】标注", ce_n, "L3 四 条矛盾陈述各并列 二 种解释 (AJ)",
        ce_ok and ce_n == [2, 2, 2, 2] and bound("L3 四 条矛盾陈述各并列 二 种解释"))
    nq = sum(1 for s in notes if norm(s) in NFULL)
    nq_m = sum(1 for s in notes if norm(s) in NMAP)
    nq_d = sum(1 for s in notes if norm(s) in NMD)
    add("引擎面·渲染", "quality_gate_notes(%d) → FULL_REPORT.md / MAP_REPORT.md / report.md" % len(notes), "FULL %d/%d; MAP %d/%d; report.md %d/%d" % (nq, len(notes), nq_m, len(notes), nq_d, len(notes)),
        "引擎渲染面: 质量门口径注记是否进入读者报告(引擎侧行为, 不计判断档偏离)", nq == len(notes) == 10 or nq_m == len(notes) or nq_d == len(notes),
        "十项口径注记(截止时点各时区/盘中快照/Gate A 明细/STALE/公布口径分类/同比基期纪律/政策口径披露/转折取舍/引擎缺口披露/草稿定性)仅存于判断档")
    rd = rm.get("rates_decomposition") or {}
    add("⑩读者面", "reader_map.rates_decomposition vs us_rates_trio", {k: rd.get(k) for k in ("window_from", "window_to", "nominal_bp", "real_bp", "bei_bp")},
        "引擎分解面: 窗 2026-10-20→2026-11-19, 名义 −8.0 / 实际 11.0 / 盈亏平衡 −19.0",
        rd.get("nominal_bp") == trio["chg_bp"].get("UST_10Y") == -8.0 and rd.get("real_bp") == trio["chg_bp"].get("TIPS_10Y") == 11.0
        and rd.get("bei_bp") == trio["chg_bp"].get("BEI_10Y") == -19.0 and rd.get("window_from") == "2026-10-20" and rd.get("window_to") == "2026-11-19")
    eb = []
    for e in rm.get("asset_returns_echo") or []:
        row = am.get(e.get("metric_id")) or {}
        if not row or not within(e.get("chg_pct"), row.get("chg_pct"), 0.0051) or (e.get("window") or {}).get("to") != (row.get("window") or {}).get("to"):
            eb.append("%s: echo=%s/%s engine=%s/%s" % (e.get("metric_id"), e.get("chg_pct"), e.get("window"), row.get("chg_pct"), row.get("window")))
    add("⑩读者面", "reader_map.asset_returns_echo(%d) vs research_plan.asset_moves" % len(rm.get("asset_returns_echo") or []), "不一致=%d" % len(eb),
        "资产月窗回贴值应与引擎面逐项一致", not eb and len(rm.get("asset_returns_echo") or []) == 6, "; ".join(eb))
    # ---------------------------------------------------------------- K 诚实缺席 / Gate A
    ga = snap.get("gate_a") or {}
    qa = snap.get("quality") or {}
    note3 = note_by_prefix("数据面")
    m1 = re.search(r"非核心缺口 十 项\(([^)]*)\)", note3)
    m2 = re.search(r"非核心降级 六 项\(([^)]*)\)", note3)
    m3 = re.search(r"质量计数 PASS (\d+) / DEGRADED (\d+) / FAIL (\d+)", note3)
    l_miss = [x.strip() for x in m1.group(1).split("、")] if m1 else []
    l_deg = [x.strip() for x in m2.group(1).split("、")] if m2 else []
    add("⑪诚实缺席", "snapshot.gate_a.status / core_missing", "%s / %s" % (ga.get("status"), ga.get("core_missing")),
        "Gate A=DEGRADED——核心缺口 0 项 (AJ 数据面)", ga.get("status") == "DEGRADED" and ga.get("core_missing") == [] and bound("Gate A=DEGRADED", "核心缺口 0 项"))
    add("⑪诚实缺席", "snapshot.gate_a.noncore_missing vs AJ 数据面", sorted(ga.get("noncore_missing") or []), "非核心缺口 十 项(%s) (AJ)" % l_miss,
        sorted(ga.get("noncore_missing") or []) == sorted(l_miss) and len(l_miss) == 10)
    add("⑪诚实缺席", "snapshot.gate_a.noncore_degraded vs AJ 数据面", sorted(ga.get("noncore_degraded") or []), "非核心降级 六 项(%s) (AJ)" % l_deg,
        sorted(ga.get("noncore_degraded") or []) == sorted(l_deg) and len(l_deg) == 6)
    cnt = qa.get("counts") or {}
    add("⑪诚实缺席", "snapshot.quality.counts / overall", "%s / %s" % (cnt, qa.get("overall")),
        "质量计数 PASS %s / DEGRADED %s / FAIL %s (AJ)" % (m3.groups() if m3 else None),
        bool(m3) and (int(m3.group(1)), int(m3.group(2)), int(m3.group(3))) == (cnt.get("PASS"), cnt.get("DEGRADED"), cnt.get("FAIL")))
    det = ga.get("noncore_missing_detail") or {}
    mine_g = {}
    for mm_, dd_ in det.items():
        mine_g.setdefault(dd_, []).append(mm_)
    seg = note3.split("缺口明细(引擎注记): ", 1)[1].split("。本证据面", 1)[0] if "缺口明细(引擎注记): " in note3 else ""
    aj_g = {}
    for s_ in seg.split("；"):
        dd_, sep_, ms_ = s_.rpartition("——")
        if sep_:
            aj_g[dd_] = [x.strip() for x in ms_.split("、") if x.strip()]
    gmis = ["%s: AJ=%s 引擎=%s" % (k, sorted(aj_g.get(k, [])), sorted(v)) for k, v in mine_g.items() if sorted(aj_g.get(k, [])) != sorted(v)]
    gmis += ["AJ 多出明细组: %s" % k for k in aj_g if k not in mine_g]
    add("⑪诚实缺席", "snapshot.gate_a.noncore_missing_detail 分组 vs AJ 缺口明细", "%d 组, 不一致=%d" % (len(mine_g), len(gmis)),
        "缺口明细(引擎注记) 逐组原文转述 (%d 组)" % len(aj_g), not gmis and len(aj_g) == 4 and sum(len(v) for v in aj_g.values()) == 10, "; ".join(gmis))
    ss = snap.get("sources_status") or {}
    ea_ids = [m for m in store if m.startswith(("EA_", "ECB_", "BUND_"))]
    absent = plan["point_values"].get("absent") or []
    abs_ids = sorted(x.get("metric_id") for x in absent)
    add("⑪诚实缺席", "snapshot.sources_status.ea / series_store 欧元区序列 / point_values.absent", "ea=%s; 欧元区序列=%s; absent=%s" % (ss.get("ea"), ea_ids, abs_ids),
        "欧元区增长、通胀、政策三维序列在本证据面全部缺席 (AJ); 四条序列缺席",
        (ss.get("ea") or {}).get("status") == "MISSING" and not ea_ids and abs_ids == ["EA_HICP_YOY", "EA_REAL_GDP_YOY", "ECB_DFR", "ECB_MRO"]
        and bound("欧元区增长、通胀、政策三维序列在本证据面全部缺席", "三时点对照无法成立"))
    present = [m for m in notin if m in store and bool(series(m))]
    add("⑪诚实缺席", "series_store 是否含 Gate A 非核心缺口清单中的四个指标", present,
        "Gate A 非核心缺口清单列入有序列库存量观测的指标(CN_OMO_7D、CN_POLICY_OVERNIGHT、JP_CPI_TOKYO_YOY、JP_REAL_GDP_YOY) (AJ 引擎缺口披露③)",
        len(present) == 4 and bound("Gate A 非核心缺口清单列入有序列库存量观测的指标(CN_OMO_7D、CN_POLICY_OVERNIGHT、JP_CPI_TOKYO_YOY、JP_REAL_GDP_YOY)"),
        "引擎 Gate A 把在序列库有观测的指标列为缺口; 判断档如实披露且未把其缺席写成「无变化」之外的口径(隔夜利率三个月前锚不可得、逆回购末次已发布观测过期均已标)")
    oa = (cell("CN_OMO_7D").get("anchors") or {}).get("最新一期") or {}
    add("⑪诚实缺席", "cells[CN_OMO_7D].anchors[最新一期].freshness*", {k: oa.get(k) for k in ("freshness", "freshness_lag_days", "freshness_window_days", "freshness_period_end")},
        "末次已发布观测 2026-10-30 被引擎注记为过期(末观测滞后 24 天，超出 10 天发布频率窗口) (AJ)",
        oa.get("freshness") == "stale" and oa.get("freshness_lag_days") == 24 and oa.get("freshness_window_days") == 10
        and oa.get("freshness_period_end") == "2026-10-30" and bound("末观测滞后 24 天，超出 10 天发布频率窗口"))
    pn = (rep.get("notes") or [""])[0]
    known_ids = set(store) | set(regids) | set(x.get("metric_id") for x in absent)
    ids19 = sorted(set(t for t in re.findall(r"[A-Z][A-Z0-9_]{2,}", pn) if t in known_ids))
    cellm = set(c["metric_id"] for c in cell_list)
    inv = [m for m in ids19 if m in cellm]
    add("⑪诚实缺席", "report.json notes[0] 指标清单 × 点值格", "清单=%d 项; 其中有格值=%d; 清单外缺席=%s" % (len(ids19), len(inv), sorted(m for m in ids19 if m not in cellm)),
        "列出 十九 个指标，其中 十五 个在点值格有值 (AJ 引擎缺口披露④)",
        len(ids19) == 19 and len(inv) == 15 and sorted(m for m in ids19 if m not in cellm) == abs_ids
        and bound("列出 十九 个指标", "十五 个在点值格有值"))
    prof = [m for m in store if re.search(r"PROFIT|利润|IND_EARN", m, re.I)]
    add("⑪诚实缺席", "series_store 中含 利润/PROFIT 的序列", prof, "本引擎无中国工业企业利润/上下游价格传导的识别序列 (AJ M2 缺环注)",
        not prof and bound("本引擎无中国工业企业利润/上下游价格传导的识别序列"))
    jpids = sorted(m for m in store if m.startswith("JP_"))
    add("⑪诚实缺席", "series_store 日本序列清单", jpids, "日本缺月频增长指标(JP_REAL_GDP_YOY 仅季频) (AJ 转折补选)",
        jpids == ["JP_CPI_TOKYO_YOY", "JP_CPI_YOY", "JP_POLICY_RATE", "JP_REAL_GDP_YOY"] and bound("日本缺月频增长指标"))
    vin = sorted(c["metric_id"] for c in cell_list if str(c.get("vintage_semantics") or "").startswith("事后回顾"))
    vin_cells = sum(len(c.get("anchors") or []) for c in cell_list if str(c.get("vintage_semantics") or "").startswith("事后回顾"))
    map_txt = MAP
    add("⑪诚实缺席", "cells[*].vintage_semantics=事后回顾(最新修订值,非当时首发值) 的指标与锚格数", (vin, vin_cells),
        "判断档全文含「事后回顾」=%s; 含「最新修订值」=%s; MAP_REPORT 点值表含「(事后回顾)」格数=%d" % (
            "事后回顾" in AJ, "最新修订值" in AJ, len(re.findall(r"\d(?:\.\d+)?\(事后回顾\)", map_txt))),
        vin == ["JP_CPI_YOY", "JP_REAL_GDP_YOY", "US_REAL_GDP"] and vin_cells == 6,
        "对照事实(不计命中/偏离计数): 三指标共 6 锚格在引擎面标为最新修订族(当时不可见); 判断档文字未转述该口径, 但判断档未把修订值称作当时首发值; 披露缺口另入 MINOR")

    # ---------------------------------------------------------------- M 契约
    cvr = (rep.get("agent_judgment") or {}).get("contract_verification") or {}
    vd = cvr.get("verdicts") or []
    stt = cvr.get("stats") or {}
    nonv = sorted((str(v.get("item", "")).split(".")[0], v.get("metric"), v.get("status")) for v in vd if v.get("status") != "VERIFIED")
    add("⑬契约", "report.agent_judgment.contract_verification.verdicts / stats", "n=%d; 非 VERIFIED=%s; stats=%s" % (len(vd), nonv, stt),
        "引擎数值核对…对核心PCE 最新水平(观测 2026-09-01)与美国实际 GDP 最新水平(观测 2026-07-01)标注 STALE (AJ 数据面)",
        len(vd) == 17 and stt.get("checks") == 17 and stt.get("verified") == 15 and stt.get("contradicted") == 0
        and nonv == [("C2-INFLATION-DIVERGENCE", "CORE_PCE", "STALE"), ("C3-GROWTH-LIMITED", "US_REAL_GDP", "STALE")]
        and bound("核心PCE 最新水平(观测 2026-09-01)", "美国实际 GDP 最新水平(观测 2026-07-01)", "标注 STALE"))
    vb, fam = [], {}
    for v in vd:
        fam[v.get("family")] = fam.get(v.get("family"), 0) + 1
        mm_ = re.search(r"直读 ([A-Z0-9_]+)@(\d{4}-\d{2}-\d{2})=", str(v.get("note")))
        if v.get("family") == "level" and mm_:
            x = val_any(mm_.group(1), mm_.group(2))
            if x is None or mm_.group(1) != v.get("metric") or abs(x - float(v.get("expected"))) > max(5e-7, 1e-6 * abs(x)) or str(v.get("token")) not in AJ:
                vb.append("%s: %s 序列值=%s expected=%s token=%s" % (v.get("item"), mm_.group(0), x, v.get("expected"), v.get("token")))
        elif v.get("family", "").startswith("change"):
            row = am.get(v.get("metric")) or {}
            if not within(v.get("value"), row.get("chg_pct"), 0.0051):
                vb.append("%s: %s 月窗=%s" % (v.get("item"), v.get("value"), row.get("chg_pct")))
        else:
            vb.append("%s: 未识别族/注记 %s" % (v.get("item"), v.get("note")))
    add("⑬契约", "契约 17 判定逐项独立复算(level 族=series_store 同日值+token 在判断档; change 族=资产月窗)", "族分布=%s; 复算偏离=%d" % (fam, len(vb)),
        "契约验证 17 判定数值应可独立复现", not vb and fam.get("level") == 13, "; ".join(vb))
    st_days = {}
    for mm_ in ("CORE_PCE", "US_REAL_GDP"):
        la = series(mm_)[-1] if series(mm_) else (None, None)
        st_days[mm_] = (la[0], (CUT - la[0]).days if la[0] else None, {k: (cell(mm_).get("anchors", {}).get("最新一期") or {}).get(k) for k in ("freshness", "freshness_lag_days", "freshness_window_days")})
    APPX.append("=== 契约 STALE 两项: 末观测日/距截止日天数/格级 freshness = %s" % json.dumps(st_days, ensure_ascii=False, default=str))
    add("⑬契约", "契约 STALE 两项(CORE_PCE / US_REAL_GDP)末观测日与判断档披露的观测期", {k: str(v[0]) for k, v in st_days.items()},
        "核心PCE 最新水平(观测 2026-09-01) / 美国实际 GDP 最新水平(观测 2026-07-01) (AJ)",
        st_days["CORE_PCE"][0] == dt.date(2026, 9, 1) and st_days["US_REAL_GDP"][0] == dt.date(2026, 7, 1), "见附录: 格级 freshness 面与契约 STALE 口径是否一致")
    cnum = {}
    for c in ces:
        t_ = str(c.get("statement") or "")
        cnum[c["id"]] = len(re.findall(r"[零一二三四五六七八九十百]{1,}[点]?[零一二三四五六七八九十]*", t_))
    APPX.append("=== 判断档汉字数字数量词出现次数(逐条 L3 陈述, 契约 token 绑定只覆盖阿拉伯数字): %s" % json.dumps(cnum, ensure_ascii=False))

    # ---------------------------------------------------------------- N 交付门
    sr = rep.get("semantic_review") or {}
    arch = [x for x in rep["steps"] if x.get("step") == "S11_archive"]
    add("⑭交付门", "FULL_REPORT.md run 门行 / deliverable 行 / review 行", "FULL 含 blocked_class=%s degraded_ok=False=%s 可交付False=%s" % (
        "blocked_class=map_core_dimension_missing" in FULL, "degraded_ok=False" in FULL, "deliverable(可交付): False" in FULL),
        "引擎交付门以核心维度缺数判为不可交付，正式归档应被拒绝 (AJ 本档定性)",
        "blocked_class=map_core_dimension_missing" in FULL and "degraded_ok=False" in FULL and "deliverable(可交付): False" in FULL
        and bound("引擎交付门以核心维度缺数判为不可交付", "正式归档应被拒绝"))
    add("⑭交付门", "report.json semantic_review / run.archive_requested / S11_archive", "required=%s seat_invoked=%s verdict=%s archive_requested=%s/%s" % (
        sr.get("required"), sr.get("seat_invoked"), sr.get("verdict"), rep["run"].get("archive_requested"), arch[0].get("archive_requested") if arch else None),
        "MAP「独立席位待裁(review required)」; FULL「review: required=True seat_invoked=False」; 判断档自称草稿 (AJ 本档定性)",
        sr.get("required") is True and sr.get("seat_invoked") is False and sr.get("verdict") is None and rep["run"].get("archive_requested") is False
        and bool(arch) and arch[0].get("archive_requested") is False and "review: required=True seat_invoked=False" in FULL
        and "独立席位待裁(review required)" in MAP and bound("草稿，非可交付正式研究"))
    ea_dims = sorted(set((x.get("region"), x.get("dimension")) for x in absent))
    add("⑭交付门", "point_values.absent[*].region×dimension vs MAP 草稿警示", ea_dims,
        "MAP: 核心维度组缺数(零 ok 格)——EA×growth、EA×inflation、EA×policy; 判决 map_core_dimension_missing / map_current_period_missing",
        ea_dims == [("EA", "growth"), ("EA", "inflation"), ("EA", "policy")] and all(("EA×%s" % d) in MAP for _, d in ea_dims)
        and "map_core_dimension_missing" in MAP and "map_current_period_missing" in MAP)
    add("⑭交付门", "判断档口径分列: 序列值≠官方宣布目标 / 缺席≠无变化", "JP 月均 1.227 vs 官方目标 1.25; CN 隔夜三个月前锚无观测; EA 四序列缺席",
        "月均口径，非宣布目标; 宣布目标序列不在引擎注册表; 该口径三个月对照不可得; 四条序列缺席",
        bound("月均口径，非宣布目标", "宣布目标序列不在引擎注册表", "该口径三个月对照不可得", "四条序列缺席", "不以之冒充宏观基本面"))

    # ---------------------------------------------------------------- O 开放问句
    rname = {"US": "美国", "EA": "欧元区", "CN": "中国", "JP": "日本"}
    regmap = {r["region"]: norm(r.get("from_to") or "") for r in rm.get("regions", [])}
    miss_pub, miss_val, n_ok = [], [], 0
    for c in cell_list:
        ft = regmap.get(c.get("region"), "")
        for lab, _ in ANCH:
            a = c["anchors"].get(lab)
            if not a or a.get("status") != "ok" or not a.get("observation_date"):
                continue
            n_ok += 1
            if str(a.get("publication_date")) not in ft:
                miss_pub.append("%s|%s|%s" % (c["metric_id"], lab, a.get("publication_date")))
            v = a.get("value")
            cands = set(x for x in ("%.4f" % v, "%.3f" % v, "%.2f" % v, "%.1f" % v, "%.0f" % v, fmt(v), str(v)) if float(x) == v)
            if not any(x in ft for x in cands):
                miss_val.append("%s|%s|%s" % (c["metric_id"], lab, v))
    add("⑮开放问句", "在场锚格 publication_date 是否逐项出现在所属地区走位文字(reader_map.regions[*].from_to)", "缺 %d/%d: %s" % (len(miss_pub), n_ok, miss_pub),
        "问句要求「各数据的公布时间」逐项给出且与引擎发布面一致", not miss_pub and n_ok == 35)
    add("⑮开放问句", "在场锚格两锚值是否逐项出现在所属地区走位文字", "缺 %d/%d: %s" % (len(miss_val), n_ok, miss_val),
        "四地被引指标两锚值", not miss_val and n_ok == 35)
    infl = {"JP_CPI_YOY": (month_val("JP_CPI_YOY", "2026-07"), month_val("JP_CPI_YOY", "2026-10")),
            "CPI": (yoy_level("CPI", "2026-07"), yoy_level("CPI", "2026-09")), "CORE_CPI": (yoy_level("CORE_CPI", "2026-07"), yoy_level("CORE_CPI", "2026-09")),
            "CORE_PCE": (yoy_level("CORE_PCE", "2026-06"), yoy_level("CORE_PCE", "2026-09")),
            "CN_CPI_YOY": (month_val("CN_CPI_YOY", "2026-07"), month_val("CN_CPI_YOY", "2026-10")),
            "CN_PPI_YOY": (month_val("CN_PPI_YOY", "2026-07"), month_val("CN_PPI_YOY", "2026-10"))}
    infl = {k: tuple(None if x is None else round(x, 2) for x in v) for k, v in infl.items()}
    add("⑮开放问句", "通胀维六指标 三个月前→最新 (series_store 直算; 美国两 CPI 取最近有效同比 2026-09)", infl,
        "通胀维三地读数均高于三个月前，分化在水平而非方向 (AJ 标题/C2)",
        all(v[0] is not None and v[1] is not None and v[1] > v[0] for v in infl.values()) and bound("通胀维三地读数均高于三个月前"))
    grow = {"US_REAL_GDP 同比": (round(yoy_level("US_REAL_GDP", "2026-04"), 2), round(yoy_level("US_REAL_GDP", "2026-07"), 2)),
            "INDPRO 同比": (round(yoy_level("INDPRO", "2026-07"), 2), round(yoy_level("INDPRO", "2026-10"), 2)),
            "UNEMPLOYMENT": (val("UNEMPLOYMENT", "2026-07-01"), val("UNEMPLOYMENT", "2026-10-01")),
            "JP_REAL_GDP_YOY": (month_val("JP_REAL_GDP_YOY", "2026-04"), month_val("JP_REAL_GDP_YOY", "2026-07")),
            "CN_PMI_MFG": (month_val("CN_PMI_MFG", "2026-07"), month_val("CN_PMI_MFG", "2026-10"))}
    add("⑮开放问句", "增长维五指标 三个月前→最新 (series_store 直算)", grow,
        "美国增长面同比读数有升有降、失业率持平，中国制造业景气在荣枯线下方，日本增长读数高于三个月前 (AJ C3)",
        grow["US_REAL_GDP 同比"][1] < grow["US_REAL_GDP 同比"][0] and grow["INDPRO 同比"][1] > grow["INDPRO 同比"][0]
        and grow["UNEMPLOYMENT"][0] == grow["UNEMPLOYMENT"][1] and grow["JP_REAL_GDP_YOY"][1] > grow["JP_REAL_GDP_YOY"][0]
        and max(grow["CN_PMI_MFG"]) < 50 and bound("美国增长面同比读数有升有降、失业率持平", "两期均在荣枯线下方", "日本增长读数高于三个月前"),
        "附注(计入): 美国GDP同比下行而日本上行(方向相反), 供 C3「未见方向性分化」措辞评注引用")
    insuf = ["增长维的「经济体之间分化」证据不足以单独成论", "涉及欧元区的横向分化均证据不足", "美国通胀是否转向证据不足",
             "缓和是否延续证据不足", "跨经济体跟进/背离证据不足"]
    add("⑮开放问句", "判断档「证据不足以结论」点名维度", insuf, "问句第三问: 点名增长维横向分化、欧元区各维、美国通胀转向、核心通胀缓和延续、跨经济体跟进/背离",
        bound(*insuf) and month_val("US_REAL_GDP", "2026-10") is None and (yoy_level("CPI", "2026-10") is None))

    # ---------------------------------------------------------------- 数值溯源普查(不入命中/偏离计数)
    def numstr(x):
        out = set()
        try:
            xf = float(x)
        except (TypeError, ValueError):
            return out
        if isinstance(x, bool) or not math.isfinite(xf):
            return out
        for f in ("%.6f", "%.4f", "%.3f", "%.2f", "%.1f", "%.0f"):
            s = f % xf
            if abs(float(s) - xf) <= 1e-9 * max(1.0, abs(xf)):
                out.add(fmt(float(s)))
        return out

    facenum = set()

    def harvest(o):
        if isinstance(o, dict):
            for v in o.values():
                harvest(v)
        elif isinstance(o, list):
            for v in o:
                harvest(v)
        elif isinstance(o, bool):
            facenum.update(numstr(int(o)))
        elif isinstance(o, (int, float)):
            facenum.update(numstr(o))
        elif isinstance(o, str):
            for t in re.findall(r"\d+(?:\.\d+)?", o):
                facenum.update(numstr(t))

    harvest(plan)
    harvest(an)
    for x in rep["steps"]:
        harvest(x.get("envelope"))
    harvest(snap.get("facts"))
    harvest(ga)
    harvest(qa)
    harvest(cal)
    harvest(cvr)
    harvest(pn)
    for m in store:
        for _, v in series(m):
            facenum.update(numstr(v))
    for x in list(eng_mine.values()) + list(close_mine.values()) + [g_e, g_c, g_es, (CUT - dt.date(2025, 11, 23)).days] + list(gaps):
        facenum |= numstr(x)
    for x in (pct("SPX", d1, CUT), pct("VIX", d1, CUT), pct("DAX", d1, CUT)):
        facenum |= numstr(x)
    texts = [("headline", rm.get("headline_conclusion") or ""), ("history_zero_case_note", hz)]
    for r in rm.get("regions", []):
        texts.append(("region:" + r["region"], r.get("from_to") or ""))
    for c in ces:
        texts.append((c["id"] + ".statement", c.get("statement") or ""))
        for k, x in enumerate(c.get("competing_explanations") or []):
            texts.append(("%s.competing[%d]" % (c["id"], k), str(x)))
    for mch in aj["l3"]["mechanism_chains"]:
        for l in mch["links"]:
            texts.append(("%s#%s" % (mch["id"], l["step"]), l.get("text") or ""))
    for sc in aj["l4"]["scenarios"]:
        rw = sc["rows"]
        texts.append((sc["id"] + ".scenario", str(rw.get("scenario"))))
        texts.append((sc["id"] + ".asset_direction", str((rw.get("asset_direction") or {}).get("direction"))))
        texts.append((sc["id"] + ".trigger", str((rw.get("trigger") or {}).get("condition"))))
        texts.append((sc["id"] + ".falsification", str((rw.get("falsification") or {}).get("threshold"))))
    tsupp = rm.get("turning_supplement") or []
    tsupp = [tsupp] if isinstance(tsupp, dict) else list(tsupp)
    for k, t in enumerate(tns + tsupp):
        for f in ("first_mover", "follow_or_diverge", "narrative", "resolution_note", "evidence_gap"):
            if isinstance(t.get(f), str):
                texts.append(("turning[%d].%s" % (k, f), t[f]))
    for k, x in enumerate(links):
        for f in ("observed_fact", "main_predicts", "competing_predicts", "causal_hypothesis", "competing_explanation", "verdict_note"):
            texts.append(("link[%d].%s" % (k, f), x.get(f) or ""))
    for k, s_ in enumerate(notes):
        texts.append(("note[%d]" % k, s_))
    APPX.append("=== 数值溯源普查: 判断档文字中的阿拉伯数字是否可溯源到引擎面/序列值/席位直算(未知项须人工复核)")
    n_unk_all = 0
    for tid, t_ in texts:
        t2 = re.sub(r"\d{4}-\d{2}(-\d{2})?|(?<!\d)\d{2}-\d{2}(?!\d)|\d{4}Q\d|\d+\.\d+\.\d+|[A-Za-z]+[A-Za-z0-9]*_[A-Za-z0-9_]+", " ", t_)
        toks = re.findall(r"\d+(?:\.\d+)?", t2)
        unk = [x for x in toks if not (numstr(x) & facenum)]
        n_unk_all += len(unk)
        if unk:
            APPX.append("%s: 数字 %d 个, 未溯源=%s" % (tid, len(toks), unk))
    APPX.append("数值溯源普查合计: 未溯源数字 %d 个" % n_unk_all)

    # ---------------------------------------------------------------- 输出
    def counted(p):
        return not p["cat"].startswith("引擎面") and not p["note"].startswith("对照事实")

    cp = [p for p in PTS if counted(p)]
    ef = [p for p in PTS if not counted(p)]
    mis = [dict(id=i, **p) for i, p in enumerate(PTS, 1) if counted(p) and not p["ok"]]
    byc = {}
    for p in cp:
        a = byc.setdefault(p["cat"], [0, 0])
        a[0] += 1
        a[1] += 0 if p["ok"] else 1
    lines = []
    for i, p in enumerate(PTS, 1):
        lines.append("[%s] #%03d %s | 出处: %s | 直算: %s | 报告: %s | 备注: %s" % (
            "OK" if p["ok"] else "XX", i, p["cat"], p["src"], p["mine"], p["reported"], p["note"]))
    with open(out_txt, "w", encoding="utf-8") as fh:
        fh.write("复算清单: 计数点 %d (偏离 %d); 引擎面自洽/对照事实 %d (偏离 %d)\n" % (
            len(cp), sum(1 for p in cp if not p["ok"]), len(ef), sum(1 for p in ef if not p["ok"])) + "\n".join(lines) + "\n")
    summ = {"points": len(cp), "mismatches": sum(1 for p in cp if not p["ok"]), "by_category": byc,
            "engine_face_checks": {"points": len(ef), "mismatches": sum(1 for p in ef if not p["ok"])},
            "mismatch_details": [{"id": x["id"], "cat": x["cat"], "src": x["src"], "mine": x["mine"], "reported": x["reported"], "note": x["note"]} for x in mis]}
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(summ, fh, ensure_ascii=False, indent=1)
    with open(out_appx, "w", encoding="utf-8") as fh:
        fh.write("\n".join(str(x) for x in APPX) + "\n")
    print("counted points=%d mismatches=%d | engine-face/other=%d mismatches=%d" % (
        summ["points"], summ["mismatches"], summ["engine_face_checks"]["points"], summ["engine_face_checks"]["mismatches"]))


if __name__ == "__main__":
    main()
