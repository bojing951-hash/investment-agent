#!/usr/bin/env python3
"""Recompute ⑤ (three-rate decomposition + asset moves) ⑥ (turnings) ⑦ (transmission numbers) — read-only."""
import re
import sys

sys.path.insert(0, "/tmp/r32-accept/review/A_round1")
import rc_common as C  # noqa: E402
from rc_a import LEVEL_YOY, first_date, first_num, ndec, same_round, table_by_header  # noqa: E402

L = C.L
TRIO = ("UST_10Y", "TIPS_10Y", "BEI_10Y")
ASSET_NAMES = {"标普500指数": "SPX", "NIKKEI225": "NIKKEI225", "SHCOMP": "SHCOMP", "DAX": "DAX", "GOLD_F": "GOLD_F", "DXY": "DXY"}


def mvals(ctx, sid, ym0, ym1, yoy=False):
    out = []
    d = ym0 + "-01"
    while d <= ym1 + "-01":
        v = ctx.yoy(sid, d)[0] if yoy else ctx.exact(sid, d)
        out.append((d[:7], v))
        d = C.L.shift_months(d, 1)
    return out


def fmt(vals):
    return " ".join("%s=%s" % (ym, "—" if v is None else "%.4g" % v) for ym, v in vals)


def last_upturn(vals):
    """first month of the rising streak that ends at the last point of vals"""
    pts = [(ym, v) for ym, v in vals if v is not None]
    i = len(pts) - 1
    while i > 0 and pts[i - 1][1] < pts[i][1]:
        i -= 1
    return pts[i][0]


def last_downturn(vals):
    """first month of the declining streak that ends at the last point of vals"""
    pts = [(ym, v) for ym, v in vals if v is not None]
    i = len(pts) - 1
    while i > 0 and pts[i - 1][1] > pts[i][1]:
        i -= 1
    return pts[i][0]


def upturn_after(vals, trough_ym):
    """month right after the trough if the series rises out of it (else None)"""
    pts = [(ym, v) for ym, v in vals if v is not None]
    i = [k for k, (ym, _) in enumerate(pts) if ym == trough_ym][0]
    return pts[i + 1][0] if i + 1 < len(pts) and pts[i + 1][1] > pts[i][1] else None


# --------------------------------------------------------------------------- ⑤
def run_rates(ctx):
    txt = ctx.map_lines
    ln = next(l for l in txt if l.startswith("- **年度窗(年度判断同窗)**"))
    m = re.search(r"计算窗口 \*\*(\S+) → (\S+)\*\*\(间隔(\d+)个日历日\),十年期分解 \*\*十年期名义 Δ([+-]\d+)bp = 实际 Δ([+-]\d+)bp \+ 盈亏平衡 Δ([+-]\d+)bp\*\*\(恒等残差 ([+-]\d+)bp\)", ln)
    a, b, days, dn, dr, db, res = m.groups()
    trio_face = (ctx.rep.get("research_plan") or {}).get("us_rates_trio") or {}
    for tag, (x, y, exp) in {"12m": (a, b, (int(dn), int(dr), int(db), int(res)))}.items():
        vals = {s: (ctx.exact(s, x), ctx.exact(s, y)) for s in TRIO}
        ctx.add("R5%s.common" % tag, "⑤", "series_store.{UST_10Y,TIPS_10Y,BEI_10Y} 窗两端当日观测", {s: vals[s] for s in TRIO},
                "共同交易日 %s→%s" % (x, y), all(v[0] is not None and v[1] is not None for v in vals.values()))
        ctx.add("R5%s.days" % tag, "⑤", "窗端日历日间隔", C.days_between(x, y), "间隔%s个日历日" % days, int(days) == C.days_between(x, y))
        for s, lbl, d in (("UST_10Y", "名义", exp[0]), ("TIPS_10Y", "实际", exp[1]), ("BEI_10Y", "盈亏平衡", exp[2])):
            bp = round((vals[s][1] - vals[s][0]) * 100)
            ctx.add("R5%s.%s" % (tag, s), "⑤", "series_store.%s[%s]−[%s] (bp)" % (s, y, x), bp, "十年期%s Δ%+dbp" % (lbl, d), bp == d,
                    note="值 %s→%s" % vals[s])
        ctx.add("R5%s.resid" % tag, "⑤", "Δ名义−Δ实际−Δ盈亏平衡", exp[0] - exp[1] - exp[2], "恒等残差 %s bp" % res,
                exp[0] - exp[1] - exp[2] == int(res))
        for i, d in enumerate((x, y)):
            gap = (vals["UST_10Y"][i] - vals["TIPS_10Y"][i] - vals["BEI_10Y"][i]) * 100
            ctx.add("R5%s.lvl%s" % (tag, d), "⑤", "名义−实际−盈亏平衡 水平恒等差 @%s (bp)" % d, round(gap, 2), "名义=实际+盈亏平衡", abs(gap) <= 1.0)
        for k, s in enumerate(TRIO):
            ctx.add("R5%s.face.%s" % (tag, s), "⑤", "report.research_plan.us_rates_trio.chg_bp_12m[%s]" % s, trio_face.get("chg_bp_12m", {}).get(s),
                    "Δ%+dbp" % exp[k], trio_face.get("chg_bp_12m", {}).get(s) == float(exp[k]))
    ln2 = next(l for l in txt if l.startswith("- 月度窗(另列)"))
    m2 = re.search(r"计算窗口 \*\*(\S+) → (\S+)\*\*\(间隔(\d+)个日历日\),十年期分解 \*\*十年期名义 Δ([+-]\d+)bp = 实际 Δ([+-]\d+)bp \+ 盈亏平衡 Δ([+-]\d+)bp\*\*\(恒等残差 ([+-]\d+)bp", ln2)
    a, b, days, dn, dr, db, res = m2.groups()
    exp = (int(dn), int(dr), int(db), int(res))
    vals = {s: (ctx.exact(s, a), ctx.exact(s, b)) for s in TRIO}
    ctx.add("R5m.common", "⑤", "series_store.{UST_10Y,TIPS_10Y,BEI_10Y} 窗两端当日观测", {s: vals[s] for s in TRIO}, "共同交易日 %s→%s" % (a, b),
            all(v[0] is not None and v[1] is not None for v in vals.values()))
    ctx.add("R5m.days", "⑤", "窗端日历日间隔", C.days_between(a, b), "间隔%s个日历日" % days, int(days) == C.days_between(a, b))
    for s, lbl, d in (("UST_10Y", "名义", exp[0]), ("TIPS_10Y", "实际", exp[1]), ("BEI_10Y", "盈亏平衡", exp[2])):
        bp = round((vals[s][1] - vals[s][0]) * 100)
        ctx.add("R5m.%s" % s, "⑤", "series_store.%s[%s]−[%s] (bp)" % (s, b, a), bp, "月度窗 十年期%s Δ%+dbp" % (lbl, d), bp == d,
                note="值 %s→%s" % vals[s])
        ctx.add("R5m.face.%s" % s, "⑤", "report.research_plan.us_rates_trio.chg_bp[%s]" % s, trio_face.get("chg_bp", {}).get(s), "Δ%+dbp" % d,
                trio_face.get("chg_bp", {}).get(s) == float(d))
    ctx.add("R5m.resid", "⑤", "Δ名义−Δ实际−Δ盈亏平衡", exp[0] - exp[1] - exp[2], "恒等残差 %s bp" % res, exp[0] - exp[1] - exp[2] == int(res))
    ln3 = next(l for l in txt if l.startswith("- 期末水平"))
    m3 = re.search(r"名义 ([\d.]+) / 实际 ([\d.]+) / 盈亏平衡 ([\d.]+)", ln3)
    for s, v in zip(TRIO, m3.groups()):
        ctx.add("R5m.lvl.%s" % s, "⑤", "series_store.%s@%s" % (s, b), vals[s][1], "期末水平 %s" % v, C.close(vals[s][1], float(v), 2))
    ctx.add("R5m.face.win", "⑤", "report.research_plan.us_rates_trio.window", "%s..%s/%s" % (trio_face.get("window", {}).get("from"), trio_face.get("window", {}).get("to"), trio_face.get("window", {}).get("calendar_days_between")),
            "%s..%s/%s" % (a, b, days), trio_face.get("window", {}).get("from") == a and trio_face.get("window", {}).get("to") == b)
    # ---- assets
    at = table_by_header(ctx, ["资产", "计算窗口", "起→末", "变化"])
    face_rows = {r["metric_id"]: r for r in ((ctx.rep.get("research_plan") or {}).get("asset_moves") or {}).get("rows", [])}
    for r in at["rows"]:
        sid, win, se, chg = r[0], r[1], r[2], r[3]
        a, b = win.split("..")
        v0, v1 = ctx.lob(sid, a), ctx.lob(sid, b)
        s0, s1 = [x.strip() for x in se.split("→")]
        mm = re.match(r"([+-]?\d+\.\d+)%\(([+-]?\d+\.\d+)\)", chg.replace("−", "-"))
        pct, ab = float(mm.group(1)), float(mm.group(2))
        last = ctx.ser(sid)[-1]
        ctx.add("A.%s.win" % sid, "⑤", "series_store.%s 最近于%s 的观测 / ≤截止日最新观测的实际日" % (sid, a), "%s..%s" % (v0[0], v1[0]),
                "计算窗口 %s" % win, v0[0] == a and v1[0] == b and v1[0] == last[0] and b <= C.CUTOFF)
        ctx.add("A.%s.val" % sid, "⑤", "series_store.%s 起/末值" % sid, "%s→%s" % (v0[1], v1[1]), "起→末 %s" % se,
                C.close(v0[1], float(s0), ndec(s0)) and C.close(v1[1], float(s1), ndec(s1)))
        ctx.add("A.%s.pct" % sid, "⑤", "(末/起−1)×100", L.pct(v0[1], v1[1]), "变化 %s" % chg, C.close(L.pct(v0[1], v1[1]), pct, 2))
        ctx.add("A.%s.abs" % sid, "⑤", "末−起", v1[1] - v0[1], "变化 %s" % chg, C.close(v1[1] - v0[1], ab, 2))
        fr = face_rows.get(sid) or {}
        ctx.add("A.%s.face" % sid, "⑤", "report.research_plan.asset_moves.rows[%s]" % sid, "chg_pct=%s chg_abs=%s" % (fr.get("chg_pct"), fr.get("chg_abs")),
                "变化 %s" % chg, fr.get("chg_pct") == pct and C.close(fr.get("chg_abs"), ab, ndec(mm.group(2))))
    rule = next((txt[i] for i in range(at["line"] - 2, max(0, at["line"] - 6), -1) if "2026-10-23" in txt[i]), "")
    ctx.add("A.rule", "⑤", "report.research_plan.asset_moves.window_rule", ((ctx.rep.get("research_plan") or {}).get("asset_moves") or {}).get("window_rule"),
            "窗口规则行: %s" % rule[:60], bool(rule) and "2026-10-23" in rule and "2026-11-23" in rule)
    # headline chain figures (L199) == table
    ln = ctx.map_lines[198]
    for nm, sid, sign in (("标普500指数下跌", "SPX", -1), ("NIKKEI225 下跌", "NIKKEI225", -1), ("SHCOMP 下跌", "SHCOMP", -1), ("DAX 下跌", "DAX", -1),
                          ("GOLD_F 下跌", "GOLD_F", -1), ("DXY 上涨", "DXY", 1)):
        mm = re.search(re.escape(nm) + r"(\d+\.\d+)%", ln)
        v0, v1 = ctx.lob(sid, "2026-10-23"), ctx.ser(sid)[-1]
        ctx.add("A.%s.text" % sid, "⑤⑩", "series_store.%s 月窗变动" % sid, abs(L.pct(v0[1], v1[1])), "L199 %s%s%%" % (nm, mm.group(1) if mm else "?"),
                bool(mm) and C.close(abs(L.pct(v0[1], v1[1])), float(mm.group(1)), 2) and (L.pct(v0[1], v1[1]) * sign > 0))
    mm = re.search(r"VIX 自(\d+\.\d+)升至(\d+\.\d+)\(\+?(\d+\.\d+)%", ln)
    v0, v1 = ctx.lob("VIX", "2026-10-23"), ctx.ser("VIX")[-1]
    ctx.add("A.VIX.text", "⑤⑩", "series_store.VIX 起/末/变动%", "%s→%s (%+.2f%%)" % (v0[1], v1[1], L.pct(v0[1], v1[1])), "L199 VIX %s" % mm.group(0),
            C.close(v0[1], float(mm.group(1)), 2) and C.close(v1[1], float(mm.group(2)), 2) and C.close(L.pct(v0[1], v1[1]), float(mm.group(3)), 2))
    hl = ctx.map_lines[10]
    for nm, sid in (("标普500指数下跌", "SPX"),):
        mm = re.search(re.escape(nm) + r"(\d+\.\d+)%", hl)
        v0, v1 = ctx.lob(sid, "2026-10-23"), ctx.ser(sid)[-1]
        ctx.add("A.%s.head" % sid, "⑤⑩", "series_store.%s 月窗变动" % sid, L.pct(v0[1], v1[1]), "L11 %s%s%%" % (nm, mm.group(1)),
                bool(mm) and C.close(abs(L.pct(v0[1], v1[1])), float(mm.group(1)), 2))
    mm = re.search(r"VIX升(\d+\.\d+)%", hl)
    ctx.add("A.VIX.head", "⑤⑩", "series_store.VIX 月窗变动%", L.pct(v0[1], v1[1]) if False else L.pct(ctx.lob("VIX", "2026-10-23")[1], ctx.ser("VIX")[-1][1]),
            "L11 VIX升%s%%" % (mm.group(1) if mm else "?"), bool(mm) and C.close(L.pct(ctx.lob("VIX", "2026-10-23")[1], ctx.ser("VIX")[-1][1]), float(mm.group(1)), 2))
    mm = re.search(r"近1个月\(2026-10-23起\)", hl)
    ctx.add("A.VIX.head.date", "⑤⑩", "资产月窗起点(各序列最近于 2026-10-23 的观测日)", sorted({ctx.lob(s, "2026-10-23")[0] for s in ("SPX", "VIX", "DXY", "GOLD_F")}),
            "L11 近1个月(2026-10-23起)", bool(mm))


# --------------------------------------------------------------------------- ⑥
def run_turnings(ctx):
    ct = table_by_header(ctx, ["地区", "维度", "指标", "窗口", "前值→后值", "Δ"])
    face = {c["metric_id"]: c for c in ((ctx.rep.get("research_plan") or {}).get("turning_candidates") or {}).get("candidates", [])}
    k = 0
    deltas = []
    for r in ct["rows"]:
        k += 1
        sid, win, se, d = r[2], r[3], r[4], r[5]
        y0, y1 = win.split("..")
        s0, s1 = [x.strip() for x in se.replace("−", "-").split("→")]
        yoy = sid in LEVEL_YOY
        v0 = ctx.yoy(sid, y0 + "-01")[0] if yoy else ctx.exact(sid, y0 + "-01")
        v1 = ctx.yoy(sid, y1 + "-01")[0] if yoy else ctx.exact(sid, y1 + "-01")
        ctx.add("T%02d.v" % k, "⑥", "series_store.%s @%s / @%s%s" % (sid, y0, y1, " (同比%)" if yoy else ""), "%s→%s" % (v0, v1), "候选面 %s %s" % (sid, se),
                C.close(v0, float(s0), ndec(s0)) and C.close(v1, float(s1), ndec(s1)))
        dv = float(d.replace("−", "-"))
        ctx.add("T%02d.d" % k, "⑥", "后值−前值(容差=两端显示舍入 1.5×10^-dec)", round(v1 - v0, 5), "Δ %s" % d,
                abs((v1 - v0) - dv) <= 1.5 * 10 ** (-ndec(d)) + 1e-12)
        deltas.append((sid, round(v1 - v0, 4)))
        fc = face.get(sid) or {}
        ctx.add("T%02d.face" % k, "⑥", "report.research_plan.turning_candidates.candidates[%s]" % sid, "%s/%s/%s/%s" % (fc.get("from_ym"), fc.get("to_ym"), fc.get("value_before"), fc.get("value_after")),
                "候选面 %s %s→%s" % (win, s0, s1), fc.get("from_ym") == y0 and fc.get("to_ym") == y1 and fc.get("value_before") == float(s0) and fc.get("value_after") == float(s1))
        pub1 = ctx.pub(sid, y1 + "-01")[0]
        ctx.add("T%02d.vis" % k, "⑥", "窗端观测的发布日 ≤ 截止日(转折须截止日可见)", pub1, "候选面 %s" % win, pub1 is not None and pub1 <= C.CUTOFF)
    absd = [abs(x) for _, x in deltas]
    ctx.add("T.sort", "⑥", "候选面按 |Δ| 降序", absd, "表序", absd == sorted(absd, reverse=True))
    us_ea = [abs(x) for s, x in deltas if s in ("CPI", "CORE_CPI", "EA_HICP_YOY", "INDPRO")]
    ctx.add("T.maxuseu", "⑥", "美欧候选 |Δ| 最大者", deltas[[s for s, _ in deltas].index("CPI")][1], "L234: 美国CPI同比…3个月滚动窗候选面最大美欧值",
            max(us_ea) == abs(deltas[[s for s, _ in deltas].index("CPI")][1]))
    ctx.add("T.cnpmi.unit", "⑥", "CN_PMI_MFG 候选值=同比%(49.0/50.2−1, 50.0/49.5−1) 而非 z 分数", "%s→%s" % (ctx.yoy("CN_PMI_MFG", "2026-02-01")[0], ctx.yoy("CN_PMI_MFG", "2026-05-01")[0]),
            "L235: z口径 -2.3904→1.0101,候选面原值", True, note="数值=同比; 文字称『z口径』与引擎面 unit『同比%』不符(行文)")
    # ---- turning narrative
    jp = mvals(ctx, "JP_CPI_YOY", "2025-01", "2026-10")
    path = [ctx.exact("JP_CPI_YOY", "%s-01" % ym) for ym in ("2025-11", "2025-12", "2026-01", "2026-02")]
    ctx.add("TN.jp.path", "⑥", "series_store.JP_CPI_YOY 2025-11..2026-02", path, "L234: 月末路径 2.9→2.13→1.51→1.27", all(C.close(a, b, 2) for a, b in zip(path, (2.9, 2.13, 1.51, 1.27))))
    downs = last_downturn([x for x in jp if x[0] <= "2026-02"])
    ctx.add("TN.jp.origin", "⑥", "series_store.JP_CPI_YOY 下行起点(末段连降首月; 2025-06..2025-11 逐月=%s)" % fmt([(y, v) for y, v in jp if "2025-06" <= y <= "2025-11"]),
            downs, "L234: 日本下行起点(2025-11)", downs == "2025-11", note="起点若早于窗启=窗口边缘效应,非下行起点")
    seg = [(ym, v) for ym, v in jp if "2025-11" <= ym <= "2026-06" and v is not None]
    trough = min(v for _, v in seg)
    tmonth = [ym for ym, v in seg if v == trough][0]
    ctx.add("TN.jp.trough", "⑥", "series_store.JP_CPI_YOY 区间最小值月", tmonth, "L234: 2026-02触底1.27", tmonth == "2026-02" and C.close(trough, 1.27, 2))
    up = upturn_after(jp, tmonth)
    ctx.add("TN.jp.upturn", "⑥", "series_store.JP_CPI_YOY 触底后首个环比回升月", up, "L234: 于2026-02触底1.27后回升", up is not None and up > "2026-02",
            note="全国CPI同比回升起点=%s(相对美欧中共振窗起点2026-02滞后%d个月)" % (up, (int(up[:4]) - 2026) * 12 + int(up[5:]) - 2))
    tk = mvals(ctx, "JP_CPI_TOKYO_YOY", "2026-01", "2026-10")
    ctx.add("TN.tok.path", "⑥", "series_store.JP_CPI_TOKYO_YOY 2026-01..2026-10", fmt(tk), "L236: 东京CPI 2026-06→09 自1.6升至2.69; (2026-06起加速上行)",
            C.close(ctx.exact("JP_CPI_TOKYO_YOY", "2026-06-01"), 1.6, 2) and C.close(ctx.exact("JP_CPI_TOKYO_YOY", "2026-09-01"), 2.69, 2))
    tk_seg = [(ym, v) for ym, v in tk if "2026-01" <= ym <= "2026-07" and v is not None]
    tk_trough = min(tk_seg, key=lambda x: x[1])[0]
    tk_up = upturn_after(tk, tk_trough)
    tk_06 = ctx.exact("JP_CPI_TOKYO_YOY", "2026-06-01")
    tk_07 = ctx.exact("JP_CPI_TOKYO_YOY", "2026-07-01")
    tk_05 = ctx.exact("JP_CPI_TOKYO_YOY", "2026-05-01")
    ctx.add("TN.tok.upturn", "⑥", "series_store.JP_CPI_TOKYO_YOY 触底(%s)后首个环比回升月; 2026-05/06/07=%s/%s/%s" % (tk_trough, tk_05, tk_06, tk_07), tk_up,
            "L236: 东京区域口径后确认(2026-06起加速上行)", tk_up == "2026-06" or (tk_06 is not None and tk_05 is not None and tk_07 is not None and tk_06 - tk_05 > tk_07 - tk_06 > 0))
    lag_national = (int(up[:4]) - 2026) * 12 + int(up[5:]) - 2
    sus = last_upturn([x for x in jp if "2026-02" <= x[0] <= "2026-10"])      # start of sustained rise into 2026-10
    lag_sus = (int(sus[:4]) - 2026) * 12 + int(sus[5:]) - 2 + 1              # first month above the local trough
    lag_tokyo = (int(tk_up[:4]) - 2026) * 12 + int(tk_up[5:]) - 2 if tk_up else None
    ctx.add("TN.lag3", "⑥", "日本回升段相对美欧中共振窗起点(2026-02)的滞后月数: 首次回升月 / 持续回升段 / 东京", "%s / %s / %s" % (lag_national, lag_sus, lag_tokyo),
            "L236: 日本回升段晚约3个月(滞后同向)", 3 in (lag_national, lag_sus, lag_tokyo), note="全国口径2026-03首次回升(1个月)、2026-04回落、持续回升段自2026-05(3个月); 东京自2026-06(4个月)")
    for sid, tag in (("CPI", "US"), ("EA_HICP_YOY", "EA"), ("CN_PPI_YOY", "CN")):
        vals = mvals(ctx, sid, "2025-10", "2026-05", yoy=sid == "CPI")
        u = last_upturn(vals)
        mm = [(ym, v) for ym, v in vals if "2025-12" <= ym <= "2026-03"]
        ctx.add("TN.sync.%s" % tag, "⑥", "series_store.%s 同比 2025-12..2026-03=%s; 至2026-05 的末段连升首月" % (sid, fmt(mm)), u,
                "L234: 三地同窗共振(2026-03起三地序列同月转向)", u == "2026-03")
    for sid, ym, val, tag in (("JP_CPI_YOY", "2026-07", 1.97, "L234 月末序列 2026-07 1.97"), ("JP_CPI_YOY", "2026-10", 2.44, "L234 →2026-10 2.44")):
        v = ctx.exact(sid, ym + "-01")
        ctx.add("TN.%s.%s" % (sid, ym), "⑥", "series_store.%s@%s" % (sid, ym), v, tag, C.close(v, val, 2))
    ind_halved = ctx.yoy("INDPRO", "2026-02-01")[0] / ctx.yoy("INDPRO", "2025-11-01")[0]
    ctx.add("TN.ind.half", "⑥", "INDPRO 同比 0.7972/1.7543", round(ind_halved, 3), "L235: 自1.7543折半至0.7972", 0.4 <= ind_halved <= 0.6)
    for sid, a, b, ra, rb, tag in (("EA_REAL_GDP_YOY", "2025-07-01", "2026-07-01", 1.11, 1.28, "L235: 欧元区GDP同比同期缓升(1.11→1.28)"),
                                   ("JP_REAL_GDP_YOY", "2025-07-01", "2026-07-01", 0.63, 1.16, "L235: 日本GDP同比回升(0.63→1.16)"),
                                   ("UNEMPLOYMENT", "2025-09-01", "2026-10-01", 4.4, 4.1, "L235: 美国失业率改善(4.4→4.1)"),
                                   ("CN_CPI_YOY", "2026-10-01", "2026-10-01", 0.7, 0.7, "L236: 中国CPI同比 0.7@2026-10")):
        ctx.add("TN.%s" % sid, "⑥", "series_store.%s@%s/@%s" % (sid, a, b), "%s→%s" % (ctx.exact(sid, a), ctx.exact(sid, b)), tag,
                C.close(ctx.exact(sid, a), ra, 2) and C.close(ctx.exact(sid, b), rb, 2))
    aj = ctx.rep.get("agent_judgment") or {}
    rm = aj.get("reader_map_faces") or {}
    ctx.add("TN.three", "⑥", "report.agent_judgment.reader_map_faces.turnings_n / validation.n_contradictions", "%s/%s" % (rm.get("turnings_n"), (aj.get("validation") or {}).get("n_contradictions")),
            "三转折(表 3 行) / 矛盾 C1-C3", rm.get("turnings_n") == 3 and (aj.get("validation") or {}).get("n_contradictions") == 3)
    row3 = table_by_header(ctx, ["日期", "指标", "前值→后值", "观测窗口", "谁先变", "跟进/背离"]).copy()
    ctx.add("TN.row3.tag", "⑥", "第三转折行标注", "引擎补选·非判断席" in row3["rows"][2][0] + row3["rows"][2][2], "L236 标注『引擎补选·非判断席』",
            "引擎补选" in row3["rows"][2][0])
    ctx.add("TN.ecbboj", "⑥", "ECB 决议 2026-09-10 与 BOJ 决议 2026-09-18 先后", "ECB<BOJ(隔8天)", "L236: 决议日粒度 ECB 09-10 早于 BOJ 09-18,先后可判",
            C.days_between("2026-09-10", "2026-09-18") == 8)


# --------------------------------------------------------------------------- ⑦
def run_transmission(ctx):
    txt = "\n".join(ctx.map_lines)
    l191 = ctx.map_lines[190]
    # link-1 window values
    for sid, yoy, a, b, ra, rb in (("CPI", True, "2026-02-01", "2026-05-01", 2.434, 4.1666), ("EA_HICP_YOY", False, "2026-02-01", "2026-05-01", 1.9, 3.2),
                                   ("CN_PPI_YOY", False, "2026-02-01", "2026-05-01", -0.9, 3.9)):
        va = ctx.yoy(sid, a)[0] if yoy else ctx.exact(sid, a)
        vb = ctx.yoy(sid, b)[0] if yoy else ctx.exact(sid, b)
        ctx.add("X1.%s" % sid, "⑦", "series_store.%s@%s/@%s%s" % (sid, a[:7], b[:7], " 同比" if yoy else ""), "%s→%s" % (va, vb),
                "L191/L80: %s→%s" % (ra, rb), C.close(va, ra, 3) and C.close(vb, rb, 4))
        # same-window claim: both endpoints rise within 2026-02..2026-05
        ctx.add("X1.%s.win" % sid, "⑦", "%s 2026-02..2026-05 路径" % sid, fmt(mvals(ctx, sid, "2026-01", "2026-06", yoy=yoy)), "L191: 同窗回升(2026-02→2026-05)",
                vb > va)
    # 'continued rise to' claims
    cp = mvals(ctx, "CORE_PCE", "2026-04", "2026-09", yoy=True)
    ctx.add("X1.corepce.rise", "⑦", "series_store.CORE_PCE 同比 2026-05..2026-09=%s" % fmt(cp), "%s→%s" % (ctx.yoy("CORE_PCE", "2026-05-01")[0], ctx.yoy("CORE_PCE", "2026-09-01")[0]),
            "L80/L191: 此后美国CORE_PCE同比至2026-09续升至3.12", ctx.yoy("CORE_PCE", "2026-09-01")[0] > ctx.yoy("CORE_PCE", "2026-05-01")[0]
            and ctx.yoy("CORE_PCE", "2026-09-01")[0] >= max(v for _, v in cp if v is not None),
            note="『续升』要求末值>起点值; 实际 2026-05=3.1617 > 2026-09=3.1212(7月回落至2.9953后部分回升)")
    eh = mvals(ctx, "EA_HICP_YOY", "2026-05", "2026-10")
    ctx.add("X1.hicp.rise", "⑦", "series_store.EA_HICP_YOY 2026-05..2026-10=%s" % fmt(eh), ctx.exact("EA_HICP_YOY", "2026-10-01"),
            "L80/L191: 欧元区HICP至2026-10续升至4.0", ctx.exact("EA_HICP_YOY", "2026-10-01") > ctx.exact("EA_HICP_YOY", "2026-05-01")
            and ctx.exact("EA_HICP_YOY", "2026-10-01") >= max(v for _, v in eh if v is not None))
    pp = mvals(ctx, "CN_PPI_YOY", "2026-05", "2026-10")
    ctx.add("X1.ppi.rise", "⑦", "series_store.CN_PPI_YOY 2026-05..2026-10=%s" % fmt(pp), ctx.exact("CN_PPI_YOY", "2026-10-01"),
            "L80/L191: 中国PPI至2026-10续升至5.7", ctx.exact("CN_PPI_YOY", "2026-10-01") > ctx.exact("CN_PPI_YOY", "2026-05-01")
            and ctx.exact("CN_PPI_YOY", "2026-10-01") >= max(v for _, v in pp if v is not None))
    cpi_path = mvals(ctx, "CPI", "2026-02", "2026-10", yoy=True)
    ctx.add("X1.cpi.path", "⑦", "series_store.CPI 同比 2026-02..2026-10=%s" % fmt(cpi_path), cpi_path[-2][1],
            "美联储 2026-09-16 决议时最新可见 CPI 同比(2026-08 观测, 09-13 发布)", ctx.yoy("CPI", "2026-08-01")[0] < ctx.yoy("CPI", "2026-05-01")[0],
            note="决议时可见读数低于5月高点(通胀『再加速』在收紧前已部分回落)")
    vis = ctx.visible("CPI", "2026-09-16")
    vis2 = ctx.visible("CORE_PCE", "2026-09-16")
    ctx.add("X1.fedvis", "⑦", "series_store.CPI/CORE_PCE 发布日≤2026-09-16 的最新可见同比", "CPI@%s=%s / CORE_PCE@%s=%s" % (
        vis[0][:7], ctx.yoy("CPI", vis[0])[0], vis2[0][:7], ctx.yoy("CORE_PCE", vis2[0])[0]), "L195/L196: 央行因通胀再加速而收紧(时序事实)",
            vis[0][:7] == "2026-08" and vis2[0][:7] == "2026-07")
    # BRENT
    b = ctx.exact("BRENT_F", "2026-11-23")
    ctx.add("X1.brent.lvl", "⑦", "series_store.BRENT_F@2026-11-23", b, "L192: BRENT_F 水平88.83@2026-11-23", C.close(b, 88.83, 2))
    mp = [ctx.lob("BRENT_F", C.month_end(ym))[1] for ym in ("2026-02", "2026-03", "2026-05")]
    ctx.add("X1.brent.path", "⑦", "series_store.BRENT_F 月末最近观测 2026-02/03/05", mp, "L192: 月频路径 72.48→118.35→92.05",
            all(C.close(a, c, 2) for a, c in zip(mp, (72.48, 118.35, 92.05))))
    b0 = ctx.lob("BRENT_F", "2026-10-31")
    ctx.add("X1.brent.mtd", "⑦", "(BRENT_F@11-23 / 10月末最近观测 −1)×100", L.pct(b0[1], b), "L192: 当月至今-24.49%", C.close(L.pct(b0[1], b), -24.49, 2))
    b23 = ctx.lob("BRENT_F", "2026-10-23")
    ctx.add("X1.brent.30d", "⑦", "series_store.BRENT_F 最近于2026-10-23 的观测→最新", "%s→%s (%+.2f, %+.2f%%)" % (b23[1], b, b - b23[1], L.pct(b23[1], b)),
            "L194/L214: 近30日116.72→88.83,-27.89 指数点(-23.89%)",
            C.close(b23[1], 116.72, 2) and C.close(b - b23[1], -27.89, 2) and C.close(L.pct(b23[1], b), -23.89, 2))
    # the distinguishing-indicator window vs the hypothesis window
    cp_m = mvals(ctx, "CORE_PCE", "2026-01", "2026-05", yoy=True)
    ctx.add("X1.brent.row", "⑦", "对质表 BRENT_F 行: 主解释预期窗=2026-02至2026-05; 该窗 BRENT_F 月末路径与 CORE_PCE 同比", "BRENT %s; CORE_PCE同比 %s" % (
        mp, fmt(cp_m[-4:])), "L214 观测格=近30日(10-23→11-23)", mp[0] < mp[1] and mp[1] > mp[2],
            note="同窗内 BRENT 先冲高(118.35)后回落(92.05), CORE_CPI/CORE_PCE 同期亦走高——两解释预期在该窗并未分立; 观测格窗口≠预期窗口")
    # BEI
    bei20 = ctx.exact("BEI_10Y", "2026-11-20")
    ctx.add("X2.bei.lvl", "⑦", "series_store.BEI_10Y@2026-11-20", bei20, "L196/L198: BEI_10Y 2026-11-20=2.15", C.close(bei20, 2.15, 2))
    b30 = ctx.lob("BEI_10Y", "2026-10-23")
    bmt = ctx.exact("BEI_10Y", "2026-10-30")
    ctx.add("X2.bei.30d", "⑦", "series_store.BEI_10Y 最近于2026-10-23 的观测→11-20 (引擎 facts.derived.mtd 基准 10-30)", "%s→%s (%+.0fbp); mtd %s→%s (%+.0fbp)" % (b30[1], bei20, (bei20 - b30[1]) * 100, bmt, bei20, (bei20 - bmt) * 100),
            "L198: 近30日2.34→2.15,下降19bp", C.close(b30[1], 2.34, 2) and C.close((bei20 - b30[1]) * 100, -19, 0) and C.close((bei20 - bmt) * 100, -19, 0),
            note="近30日起点10-23(28天)与引擎月至今基准10-30数值相同(均为2.34),行文口径标注不精确(NIT)")
    pre = [(d, v) for d, v in ctx.ser("BEI_10Y") if "2026-02-01" <= d <= "2026-06-11"]
    lo = min(pre, key=lambda x: x[1])
    hi = max(pre, key=lambda x: x[1])
    pre_ok = hi[1] > lo[1] and hi[0] < "2026-06-01" and hi[1] - lo[1] >= 0.15
    ctx.add("X2.bei.pre", "⑦", "series_store.BEI_10Y 2026-02-01..2026-06-10(首次加息决议前) 低点/高点及日期", "低 %s=%s; 高 %s=%s; 决议前日 06-10=%s" % (
        lo[0], lo[1], hi[0], hi[1], ctx.exact("BEI_10Y", "2026-06-10")), "L215 主解释预期: BEI_10Y 在政策收紧前处上行段且高位", pre_ok,
        note="收紧前 BEI 自低点上行约 %.0fbp——主解释预期在该窗成立" % ((hi[1] - lo[1]) * 100))
    ctx.add("X2.bei.row", "⑦", "对质表 BEI_10Y(政策)行: 主解释预期(收紧前上行段)=%s; 竞争解释预期(收紧后不升)与近30日 2.34→2.15 相容" % ("成立" if pre_ok else "不成立"),
            "两侧预期各有相容观测 → 尚不能区分", "L215 判断=支持竞争解释(观测格仅列近30日)", not pre_ok,
            note="单侧证据裁;收紧后 BEI 回落亦与『通胀动机收紧且预期被锚定』相容,不专属于竞争解释;与 L219 自定口径『不以单侧证据裁』相左")
    post = [(d, v) for d, v in ctx.ser("BEI_10Y") if "2026-06-11" <= d <= C.CUTOFF]
    ctx.add("X2.bei.post", "⑦", "series_store.BEI_10Y 2026-06-11..截止日 区间", "%s..%s (max %s@%s)" % (post[0][1], post[-1][1], max(v for _, v in post), [d for d, v in post if v == max(x for _, x in post)][0]),
            "L215 竞争解释预期: 政策续紧而 BEI_10Y 不升", True, note="两解释对『收紧后 BEI 不升』相容: 通胀动机说不排除预期回落; 须以收紧前走势裁")
    # HY_OAS
    hy = ctx.exact("HY_OAS", "2026-11-19")
    hyf = [f for f in ctx.snap["facts"] if f.get("metric_id") == "HY_OAS"]
    wk = (hyf[0].get("derived") or {}).get("week") if hyf else None
    wk_base = wk.get("basis_value") if isinstance(wk, dict) else None
    ctx.add("X3.hy.lvl", "⑦", "series_store.HY_OAS@2026-11-19", hy, "L199/L80: HY_OAS 水平3.52pp@2026-11-19", C.close(hy, 3.52, 2))
    ctx.add("X3.hy.week", "⑦", "series_store.HY_OAS 上周五(2026-11-13)收盘→11-19; 严格7日前(11-12)→11-19", "%s→%s (%+.2fpp); 11-12=%s (%+.2fpp)" % (
        ctx.exact("HY_OAS", "2026-11-13"), hy, hy - ctx.exact("HY_OAS", "2026-11-13"), ctx.exact("HY_OAS", "2026-11-12"), hy - ctx.exact("HY_OAS", "2026-11-12")),
        "L199/L80: 近1周走阔0.29pp", C.close(hy - ctx.exact("HY_OAS", "2026-11-13"), 0.29, 2),
        note="facts.derived.week=%s(ISO周内首交易日相对上周五收盘); 严格7日口径为+0.32pp" % (json_d(wk)[:120]))
    ctx.add("X3.hy.calm", "⑦", "series_store.HY_OAS 全史分位(≤2026-11-19)", pct_rank(ctx.ser("HY_OAS"), hy), "L199: 仍温和(非信用事件级)",
            pct_rank(ctx.ser("HY_OAS"), hy) < 0.90, note="HY_OAS 序列始于 2023-11(约3年)")
    # USDJPY
    u = ctx.exact("USDJPY", "2026-11-23")
    u23 = ctx.lob("USDJPY", "2026-10-23")
    ctx.add("X4.usdjpy.lvl", "⑦", "series_store.USDJPY@2026-11-23", u, "L205: USDJPY 水平158.96@2026-11-23; L208: 158.956",
            C.close(u, 158.96, 2) and C.close(u, 158.956, 3))
    ctx.add("X4.usdjpy.30d", "⑦", "series_store.USDJPY 最近于2026-10-23 的观测→最新", "%s→%s (%+.5f, %+.4f%%)" % (u23[1], u, u - u23[1], L.pct(u23[1], u)),
            "L208/L217: 近30日156.494→158.956,+2.46199 指数点(+1.57%)",
            C.close(u23[1], 156.494, 3) and C.close(u - u23[1], 2.46199, 5) and C.close(L.pct(u23[1], u), 1.57, 2))
    spx0 = ctx.lob("SPX", "2026-10-23")
    ctx.add("X4.usdjpy.row", "⑦", "对质表 USDJPY 行: 主解释预期=收缩窗内日元走强(USDJPY 走低); 实际同窗 USDJPY %+.2f%% / SPX %+.2f%%" % (
        L.pct(u23[1], u), L.pct(spx0[1], ctx.ser("SPX")[-1][1])), "同窗 USDJPY 上行(与主解释预期方向相反)", "L217 判断=尚不能区分", True,
        note="主解释预期方向与同窗观测相反, 观测格未披露; 竞争解释(时间上解耦)需逐日共动面——『尚不能区分』可辩护但披露不全(MINOR)")
    # JP monthly steps
    ctx.add("X4.jp.step", "⑦", "series_store.JP_POLICY_RATE 月度步进(≥1bp)", "2025-12 +8; 2026-01 +17; 06 +11; 07 +14; 09 +7; 10 +18",
            "L205: 月度步进 +17/+11/+14/+7/+18 (自2025-12起); L186 自2025-12月均0.557升至2026-10月均1.227净+67个基点",
            C.close((ctx.exact("JP_POLICY_RATE", "2026-10-01") - ctx.exact("JP_POLICY_RATE", "2025-12-01")) * 100, 67, 0))
    tiny = [c for c in L.changes_in_window(ctx.ser("JP_POLICY_RATE"), "2026-01-01", "2026-10-01") if 0 < abs(c[2] - c[1]) * 100 < 1]
    ctx.add("X4.jp.tiny", "⑦", "series_store.JP_POLICY_RATE <1bp 的月度舍入变动数", len(tiny), "L205: 另有两个月各约零点一个基点的舍入变动", len(tiny) == 2)
    jgb = [s for s in ctx.snap["series_store"] if "JGB" in s.upper()]
    jf = [f.get("metric_id") for f in ctx.snap["facts"] if "JGB" in str(f.get("metric_id", "")).upper()]
    ctx.add("X4.jgb", "⑪", "series_store / facts 中 JGB 序列", "序列=%s; 事实=%s" % (jgb, jf), "L205: JGB 收益率历史序列不在引擎(单点观测)", not jgb and bool(jf),
            note="单点观测事实=%s" % jf)
    ctx.add("X4.jp.first", "⑦", "series_store.JP_POLICY_RATE/DFEDTARU/ECB_DFR 窗内首个变动月", "JP 2025-12; US 2025-12(降); EA 2026-06",
            "L186/L205/L234: 日本为四地中唯一在美欧通胀同窗回升(2026-02起)之前已开始上调、窗内未回撤的央行",
            L.changes_in_window(ctx.ser("JP_POLICY_RATE"), "2025-11-23", C.CUTOFF)[0][0][:7] == "2025-12"
            and all(c[2] > c[1] for c in L.changes_in_window(ctx.ser("JP_POLICY_RATE"), "2025-11-23", C.CUTOFF) if abs(c[2] - c[1]) * 100 >= 1)
            and all(c[0] >= "2026-06" for c in L.changes_in_window(ctx.ser("ECB_DFR"), "2025-11-23", C.CUTOFF))
            and any(c[2] < c[1] for c in L.changes_in_window(ctx.ser("DFEDTARU"), "2025-11-23", "2026-05-01")))
    # evidence level labels present per link
    for tag, needle in (("L1", "【假设】供给/能源冲击"), ("L2", "【假设】央行因通胀再加速而收紧"), ("L3", "【假设】实际利率上行压制"), ("M2", "【假设】日本正常化推升日债收益率")):
        mm = re.search(re.escape(needle) + r"[^\n]*?证据级(E\d)", txt)
        ctx.add("X.%s.evl" % tag, "⑦", "传导链因果假设行的证据级标注", mm.group(1) if mm else "无", "%s … 证据级E2/E3(不可识别环不得标E1)" % needle,
                bool(mm) and mm.group(1) in ("E2", "E3"))
    for tag, needle in (("L1", "【竞争解释】需求过热或基数效应主导"), ("L2", "【竞争解释】收紧另有动机"), ("L3", "【竞争解释】增长担忧主导"), ("M2", "【竞争解释】近月风险资产收缩源于美国国内")):
        ctx.add("X.%s.comp" % tag, "⑦", "每条传导链含竞争解释(带『【竞争解释】』字面与可区分指标)", needle in txt and ("能区分解释的指标" in txt), "每链一条竞争解释+区分指标", needle in txt)
    ctx.add("X.attribution", "⑦", "MAP L7 分工声明: 判断文字=Agent 席 reader_map 原文(attribution=ai_inferred)", "attribution=ai_inferred" in ctx.map_lines[6],
            "L7 声明在场", "attribution=ai_inferred" in ctx.map_lines[6] and "经独立语义审查" in ctx.map_lines[6])


def json_d(o):
    import json
    return json.dumps(o, ensure_ascii=False)


def pct_rank(p, v):
    vals = [x for _, x in p if _ <= "2026-11-19"]
    return sum(1 for x in vals if x <= v) / len(vals)
