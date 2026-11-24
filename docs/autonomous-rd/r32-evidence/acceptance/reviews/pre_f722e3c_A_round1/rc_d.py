#!/usr/bin/env python3
"""Recompute sections ⑨(scenarios) ⑩(headline/walk text vs numbers) ⑪(honest absences + Gate A)
⑫(cutoff-day labels) ⑬(map sub-questions / residual) — read-only, independent of engine code."""
import os
import re
import sys

sys.path.insert(0, "/tmp/r32-accept/review/A_round1")
import rc_common as C  # noqa: E402

L = C.L
from rc_a import ndec, table_by_header  # noqa: E402,F401

SIDS_CITED_1123 = ["SHCOMP", "DAX", "VIX", "DXY", "GOLD_F", "BRENT_F", "USDJPY", "CN_POLICY_OVERNIGHT", "USDCNY"]


# ----------------------------------------------------------------------------- helpers
def line_with(ctx, needle, start=0):
    for i in range(start, len(ctx.map_lines)):
        if needle in ctx.map_lines[i]:
            return i + 1, ctx.map_lines[i]
    return None, None


def next_nonempty(ctx, start):
    for i in range(start, len(ctx.map_lines)):
        if ctx.map_lines[i].strip():
            return i + 1, ctx.map_lines[i]
    return None, None


def fmt_tok(v, tok):
    d = ndec(tok)
    if v is None:
        return "None"
    return ("%+.*f" % (d, v)) if tok.strip().startswith("+") else ("%.*f" % (d, v))


def cmp_seq(vals, expect):
    toks = [t.strip() for t in expect.split("→")]
    if len(toks) != len(vals):
        return "长度不符(%d vs %d)" % (len(vals), len(toks)), False
    ok = True
    comp = []
    for v, tok in zip(vals, toks):
        rep = C.num(tok)
        good = (v is None and rep is None) or (v is not None and rep is not None and C.close(v, rep, ndec(tok)))
        ok = ok and good
        comp.append(fmt_tok(v, tok) if v is not None else "None")
    return "→".join(comp), ok


def seq_point(ctx, pid, cat, sid, dates, expect, ln, txt, yoy=False, note=""):
    vals = [(ctx.yoy(sid, d)[0] if yoy else ctx.exact(sid, d)) for d in dates]
    comp, ok = cmp_seq(vals, expect)
    found = expect in txt
    src = "series_store.%s[%s]%s" % (sid, ",".join(d[:7] for d in dates), " 同比(基期=去年同月)" if yoy else "")
    ctx.add(pid, cat, src, comp, "MAP L%d 「%s」" % (ln, expect), ok and found,
            note=("文字未找到该串; " if not found else "") + note)


def me_chg(ctx, sid, ym0, n):
    y, m = int(ym0[:4]), int(ym0[5:7])
    tot = y * 12 + (m - 1) + n
    ny, nm = divmod(tot, 12)
    ym1 = "%04d-%02d" % (ny, nm + 1)
    a = ctx.mlast(sid, ym0)
    b = ctx.mlast(sid, ym1)
    if not a or not b:
        return None, (a, b, ym1)
    return (b[1] / a[1] - 1.0) * 100.0, (a, b, ym1)


def aj_of(ctx):
    """agent_judgment.json (judgment file; protocol §1 read-only object) — same directory as MAP_REPORT.md"""
    if not hasattr(ctx, "_aj"):
        path = os.path.join(os.path.dirname(ctx.map_path), "agent_judgment.json")
        ctx._aj = L.load(path) if os.path.exists(path) else {}
    return ctx._aj


def has_flag(txt):
    return "当日实时快照" in txt and "非收盘价" in txt


# ----------------------------------------------------------------------------- ⑨ scenarios
def run_scenarios(ctx):
    ln1, t1 = line_with(ctx, "| SCN1 |")
    ln2, t2 = line_with(ctx, "| SCN2 |")
    s6 = (ctx.steps.get("S6_analog") or {}).get("envelope", {}).get("data", {})
    top = {t.get("candidate_month"): t for t in s6.get("top", [])}
    # cited analog numbers (month-end basis)
    for sid, n, rep in (("SPX", 3, "-5.28%"), ("GOLD_F", 3, "-7.49%"), ("DXY", 3, "+7.10%"), ("SPX", 12, "+17.57%")):
        v, (a, b, ym1) = me_chg(ctx, sid, "2022-06", n)
        ctx.add("SC.c2022-06.%s.%dm" % (sid, n), "⑨", "series_store.%s 月末观测 %s→%s" % (sid, a[0], b[0]),
                None if v is None else round(v, 4), "L%d SCN1 资产方向文字 %s" % (ln1, rep),
                (rep.replace("%", "") in t1) and v is not None and C.close(v, C.num(rep), 2))
    for sid, rep in (("GOLD_F", "+48.83%"), ("DXY", "-4.08%"), ("SPX", "+16.33%")):
        v, (a, b, ym1) = me_chg(ctx, sid, "2025-03", 12)
        ctx.add("SC.c2025-03.%s.12m" % sid, "⑨", "series_store.%s 月末观测 %s→%s" % (sid, a[0], b[0]),
                None if v is None else round(v, 4), "L%d SCN2 资产方向文字 %s" % (ln2, rep),
                (rep.replace("%", "") in t2) and v is not None and C.close(v, C.num(rep), 2))
    # contribution shares quoted
    t03 = top.get("2025-03") or {}
    dims = (t03.get("dims") or {})
    try:
        sv = dims["volatility"]["contribution_share"] * 100.0
        sr = dims["rates"]["contribution_share"] * 100.0
    except Exception:
        sv = sr = None
    ctx.add("SC.share.vol", "⑨", "report.json steps[S6_analog].envelope.data.top[candidate_month=2025-03].dims.volatility.contribution_share×100",
            None if sv is None else round(sv, 2), "L%d 「(46.0%%+38.0%%)」波动维" % ln2, sv is not None and C.close(sv, 46.0, 1))
    ctx.add("SC.share.rates", "⑨", "report.json steps[S6_analog].envelope.data.top[candidate_month=2025-03].dims.rates.contribution_share×100",
            None if sr is None else round(sr, 2), "L%d 「(46.0%%+38.0%%)」利率维" % ln2, sr is not None and C.close(sr, 38.0, 1))
    # overlap statement
    win = ((t03.get("aftermath") or {}).get("SPX_window") or {}).get("12m") or {}
    ov = bool(win) and win.get("end", "") >= "2025-11-23"
    ctx.add("SC.overlap", "⑨", "S6 top[2025-03].aftermath.SPX_window.12m(%s..%s) vs 本轮 12 个月窗起点 2025-11-23" % (
        win.get("start"), win.get("end")), "重叠=%s" % ov, "L%d 「事后窗与本轮早段重叠,样本非独立」" % ln2, ov)
    # SCN1 trigger observability / compatibility
    b11, b12 = ctx.exact("CPI", "2025-11-01"), ctx.exact("CPI", "2025-12-01")
    p11, _ = ctx.pub("CPI", "2026-11-01")
    p12, _ = ctx.pub("CPI", "2026-12-01")
    dl = re.search(r"期限 (\d{4}-\d{2}-\d{2})", t1 or "")
    dl = dl.group(1) if dl else None
    ctx.add("SC.SCN1.trig.observable", "⑨", "series_store.CPI[2025-11-01]=%s,[2025-12-01]=%s; CPI 发布规则 月末+13 → %s/%s; 期限 %s" % (
        b11, b12, p11, p12, dl), "基期在场=%s; 首发日≤期限=%s" % (
            None not in (b11, b12), (p11 <= dl and p12 <= dl) if dl else None),
        "L%d 触发条件「美国2026-11或2026-12月CPI同比继续≥3.5」" % ln1,
        None not in (b11, b12) and dl is not None and p11 <= dl and p12 <= dl and dl > C.CUTOFF)
    y09 = ctx.yoy("CPI", "2026-09-01")[0]
    ctx.add("SC.SCN1.trig.compat", "⑨", "series_store.CPI 同比@2026-09=%s(最新有效同比)" % (None if y09 is None else round(y09, 4)),
            "≥3.5" if (y09 is not None and y09 >= 3.5) else "<3.5", "L%d 「继续≥3.5」与截止日读数相容" % ln1,
            y09 is not None and y09 >= 3.5)
    # SCN1 falsification not yet triggered (joint: CPI<2.5 and CORE_PCE<2.8 for two consecutive months)
    months = ["2025-%02d" % m for m in (11, 12)] + ["2026-%02d" % m for m in range(1, 10)]
    joint = []
    for ym in months:
        yc = ctx.yoy("CPI", ym + "-01")[0]
        yp = ctx.yoy("CORE_PCE", ym + "-01")[0]
        if yc is not None and yp is not None and yc < 2.5 and yp < 2.8:
            joint.append(ym)
    two = any(i + 1 < len(months) and months[i] in joint and months[i + 1] in joint for i in range(len(months)))
    ctx.add("SC.SCN1.fals.notyet", "⑨", "series_store.CPI/CORE_PCE 同比 2025-11..2026-09 联合阈值(CPI<2.5 且 CORE_PCE<2.8)命中月=%s" % joint,
            "连续两月命中=%s" % two, "L%d 证伪阈值「CPI回落至2.5以下且CORE_PCE回落至2.8以下并持续两个月」为待验证" % ln1, not two)
    ctx.add("SC.SCN1.fals.base", "⑨", "series_store.CPI[2025-10-01]=%s(2026-10 同比基期缺席);[2025-11-01]=%s(2026-11 同比基期在场)" % (
        ctx.exact("CPI", "2025-10-01"), b11), "缺基期只影响 2026-10 同比;2026-11 起基期在场",
        "L%d 「(2025-10基期补齐后)」" % ln1, True, note="NIT: 括注口径不准——2026-11 及以后同比不依赖 2025-10 基期")
    # SCN2 trigger already met?
    ym_all = ["2025-%02d" % m for m in (11, 12)] + ["2026-%02d" % m for m in range(1, 10)]
    yv = [(ym, ctx.yoy("CPI", ym + "-01")[0]) for ym in ym_all]
    pairs = []
    for i in range(2, len(yv)):
        a, b, c = yv[i - 2][1], yv[i - 1][1], yv[i][1]
        if None not in (a, b, c) and b < a and c < b:
            pd, _ = ctx.pub("CPI", yv[i][0] + "-01")
            pairs.append("%s/%s(%s→%s→%s,末值首发 %s)" % (yv[i - 1][0], yv[i][0], round(a, 4), round(b, 4), round(c, 4), pd))
    early = [p for p in pairs if re.search(r"首发 (\d{4}-\d{2}-\d{2})", p).group(1) <= C.CUTOFF]
    ctx.add("SC.SCN2.trig.already", "⑨", "series_store.CPI 同比连续两月回落段: %s" % (early or "无"),
            "截止日前已出现=%s" % bool(early), "L%d 触发条件「美国CPI同比连续两个月回落」作为待验证触发" % ln2, not early,
            note="MINOR: 触发条件缺『自截止日起』锚——字面条件在 2026-06/07 已成立且截止日前已发布")
    # SCN2 falsification not yet
    bei = ctx.ser("BEI_10Y")
    rec = [(d, v) for d, v in bei if d >= "2025-11-23"]
    mn = min(rec, key=lambda t: t[1]) if rec else (None, None)
    ctx.add("SC.SCN2.fals.notyet", "⑨", "series_store.BEI_10Y 近12个月最低=%s@%s; 最新=%s" % (mn[1], mn[0], bei[-1]),
            "≥1.8" if (mn[1] is not None and mn[1] >= 1.8) else "<1.8", "L%d 证伪阈值「BEI_10Y 跌破1.8」为待验证" % ln2,
            mn[1] is not None and mn[1] >= 1.8)
    dl2 = re.search(r"期限 (\d{4}-\d{2}-\d{2})", t2 or "")
    dl2 = dl2.group(1) if dl2 else None
    ctx.add("SC.SCN2.deadline", "⑨", "期限字段 %s vs 截止日 %s" % (dl2, C.CUTOFF), "晚于截止日=%s" % (dl2 > C.CUTOFF if dl2 else None),
            "L%d 期限 2027-02-28" % ln2, dl2 is not None and dl2 > C.CUTOFF)
    # complementarity (text)
    k1 = ("承压" in t1, "DXY 偏强" in t1, "GOLD_F 受" in t1, "VIX 中枢抬升" in t1)
    k2 = ("股指倾向修复" in t2, "DXY 转弱" in t2, "GOLD_F 修复走强" in t2)
    ctx.add("SC.complement", "⑨", "SCN1 方向(股指承压/GOLD_F 承压/DXY 偏强/VIX 抬升)=%s vs SCN2(股指修复/GOLD_F 走强/DXY 转弱)=%s" % (k1, k2),
            "SPX/GOLD_F/DXY 三项方向相反=%s; VIX 仅 SCN1 给出" % all(k1[:3]) and all(k2),
            "L228 「两情景方向互补」", all(k1[:3]) and all(k2))
    for sid in ("TIPS_10Y", "CPI", "BEI_10Y"):
        ctx.add("SC.sensitive.%s" % sid, "⑨", "series_store.%s 在场=%s" % (sid, ctx.has(sid)), "在场" if ctx.has(sid) else "缺席",
                "L%d/L%d 敏感变量/证伪指标在场" % (ln1, ln2), ctx.has(sid))
    l4 = ((aj_of(ctx).get("l4") or {}).get("scenarios") or [])
    rkeys = sorted((l4[0].get("rows") or {}).keys()) if l4 else None
    ctx.add("SC.role", "⑨", "agent_judgment.json l4.scenarios[0].rows 键=%s" % rkeys, "无 role/角色字段 → 渲染为 —",
            "L%d/L%d 角色列均为 —" % (ln1, ln2), bool(rkeys) and not any(k in ("role", "角色") for k in rkeys)
            and ("| SCN1 | — |" in t1) and ("| SCN2 | — |" in t2),
            note="NIT: 角色列空缺(基准/反例情景身份只在 scenario 行内文字)")
    # confidence tier vs signs (engine aftermath vs month-end)
    eng = ((top.get("2022-06") or {}).get("aftermath") or {})
    ok = True
    det = []
    for sid, key in (("SPX", "3m"), ("GOLD_F", "3m"), ("DXY", "3m"), ("SPX", "12m")):
        v, (a, b, _) = me_chg(ctx, sid, "2022-06", int(key[:-1]))
        e = (eng.get(sid) or {}).get(key)
        if v is None or e is None:
            ok = False
            det.append("%s:缺" % sid)
            continue
        same = (v > 0) == (e > 0)
        ok = ok and same
        det.append("%s %s 月末 %.2f/引擎 %.3f 同号=%s" % (sid, key, v, e, same))
    ctx.add("SC.conf", "⑨", "series_store 月末口径 vs S6 top[2022-06].aftermath: %s" % "; ".join(det), "四项同号=%s" % ok,
            "L%d 「confidence_tier=有历史相似证据」方向引证" % ln1, ok)


# ----------------------------------------------------------------------------- ⑩ headline / walks
def run_walks(ctx):
    h_ln, h = next_nonempty(ctx, 0)
    for i, x in enumerate(ctx.map_lines):
        if x.startswith("## 一句总判断"):
            h_ln, h = next_nonempty(ctx, i + 1)
            break
    walks = {}
    for tag, key in (("US", "### 美国"), ("CN", "### 中国"), ("EA", "### 欧元区"), ("JP", "### 日本")):
        for i, x in enumerate(ctx.map_lines):
            if x.startswith(key):
                walks[tag] = next_nonempty(ctx, i + 1)
                break
    (u_ln, u), (c_ln, c), (e_ln, e), (j_ln, j) = walks["US"], walks["CN"], walks["EA"], walks["JP"]
    # --- US walk
    seq_point(ctx, "W.US.GDP.yoy", "⑩", "US_REAL_GDP", ["2025-04-01", "2026-04-01", "2026-07-01"], "2.42→2.19→2.07", u_ln, u, yoy=True)
    seq_point(ctx, "W.US.GDP.lvl", "⑩", "US_REAL_GDP", ["2025-04-01", "2026-04-01", "2026-07-01"], "23884.563→24408.011→24611.077", u_ln, u)
    seq_point(ctx, "W.US.UNEMP", "⑩", "UNEMPLOYMENT", ["2025-09-01", "2026-07-01", "2026-10-01"], "4.4→4.1→4.1", u_ln, u)
    seq_point(ctx, "W.US.INDPRO.yoy", "⑩", "INDPRO", ["2025-08-01", "2026-07-01", "2026-10-01"], "1.19→1.25→2.15", u_ln, u, yoy=True)
    seq_point(ctx, "W.US.CPI.yoy", "⑩", "CPI", ["2025-09-01", "2026-07-01"], "3.02→3.30", u_ln, u, yoy=True)
    y09 = ctx.yoy("CPI", "2026-09-01")[0]
    ctx.add("W.US.CPI.latest", "⑩", "series_store.CPI 同比@2026-09=%s; 同比@2026-10 基期 2025-10=%s" % (
        None if y09 is None else round(y09, 4), ctx.exact("CPI", "2025-10-01")), "最近有效同比 %s@2026-09; 2026-10 同比不可得" % (
            None if y09 is None else "%.2f" % y09), "L%d 「同比不可得…最近有效同比3.72@2026-09」" % u_ln,
            y09 is not None and C.close(y09, 3.72, 2) and ctx.yoy("CPI", "2026-10-01")[0] is None)
    seq_point(ctx, "W.US.CPI.lvl", "⑩", "CPI", ["2025-09-01", "2026-07-01", "2026-10-01"], "324.245→332.813→337.476", u_ln, u)
    seq_point(ctx, "W.US.COREPCE.yoy", "⑩", "CORE_PCE", ["2025-08-01", "2026-06-01", "2026-09-01"], "2.85→3.04→3.12", u_ln, u, yoy=True)
    vy = [ctx.yoy("CORE_PCE", d)[0] for d in ("2025-08-01", "2026-06-01", "2026-09-01")]
    ctx.add("W.US.COREPCE.mono", "⑩", "同上三点 %s" % [None if v is None else round(v, 4) for v in vy],
            "逐点走高=%s" % (vy[0] < vy[1] < vy[2]), "L%d 「逐点走高」" % u_ln, vy[0] < vy[1] < vy[2],
            note="仅三点单调;全序列 2026-05=3.1617 高于 2026-09(见 X1.corepce.rise)")
    seq_point(ctx, "W.US.DFF", "⑩", "DFF", ["2025-11-22", "2026-08-22", "2026-11-19"], "3.88→3.63→3.88", u_ln, u)
    chg = L.changes_in_window(ctx.ser("DFF"), "2025-12-10", "2025-12-12") + L.changes_in_window(ctx.ser("DFF"), "2026-09-16", "2026-09-18")
    tchg = L.changes_in_window(ctx.ser("DFEDTARU"), "2025-12-10", "2025-12-12") + L.changes_in_window(ctx.ser("DFEDTARU"), "2026-09-16", "2026-09-18")
    ctx.add("W.US.DFF.events", "⑩", "series_store.DFF/DFEDTARU 变更点: %s / %s" % (chg, tchg),
            "两次 ±25bp 且窗内净 0", "L%d 「2025-12-11生效降25个基点(4.0→3.75),2026-09-17生效回升25个基点(3.75→4.0),全年净变0」" % u_ln,
            any(abs(x[1] - 3.89) < 1e-9 and abs(x[2] - 3.64) < 1e-9 and x[0] == "2025-12-11" for x in chg)
            and any(abs(x[1] - 3.63) < 1e-9 and abs(x[2] - 3.88) < 1e-9 and x[0] == "2026-09-17" for x in chg)
            and any(abs(x[1] - 4.0) < 1e-9 and abs(x[2] - 3.75) < 1e-9 and x[0] == "2025-12-11" for x in tchg)
            and any(abs(x[1] - 3.75) < 1e-9 and abs(x[2] - 4.0) < 1e-9 and x[0] == "2026-09-17" for x in tchg))
    # --- CN walk
    seq_point(ctx, "W.CN.PMI", "⑩", "CN_PMI_MFG", ["2025-10-01", "2026-07-01", "2026-10-01"], "49.0→49.2→49.3", c_ln, c)
    seq_point(ctx, "W.CN.PMI.yoy", "⑩", "CN_PMI_MFG", ["2025-10-01", "2026-07-01", "2026-10-01"], "-2.2→-0.2→+0.61", c_ln, c, yoy=True)
    pv = [ctx.exact("CN_PMI_MFG", d) for d in ("2025-10-01", "2026-07-01", "2026-10-01")]
    ctx.add("W.CN.PMI.below50", "⑩", "series_store.CN_PMI_MFG 三锚值 %s" % pv, "均<50=%s" % all(v < 50 for v in pv),
            "L%d 「三时点均处荣枯线下方」" % c_ln, all(v < 50 for v in pv))
    sp = [(d, v) for d, v in ctx.ser("CN_PMI_MFG") if "2026-03" <= d[:7] <= "2026-06"]
    mx = max(sp, key=lambda t: t[1]) if sp else (None, None)
    ctx.add("W.CN.PMI.spring", "⑩", "series_store.CN_PMI_MFG 2026-03..06 最大=%s@%s" % (mx[1], mx[0]), ">50=%s" % (mx[1] is not None and mx[1] > 50),
            "L%d 「2026年春季一度回升至荣枯线上方」" % c_ln, mx[1] is not None and mx[1] > 50)
    ctx.add("W.CN.PMI.jul", "⑩", "series_store.CN_PMI_MFG[2026-07-01]=%s" % ctx.exact("CN_PMI_MFG", "2026-07-01"),
            ctx.exact("CN_PMI_MFG", "2026-07-01"), "L%d 「至2026-07观测回落至49.2」" % c_ln, C.close(ctx.exact("CN_PMI_MFG", "2026-07-01"), 49.2, 1))
    sep = ctx.exact("CN_PMI_MFG", "2026-09-01")
    ctx.add("W.CN.PMI.sep", "⑩", "series_store.CN_PMI_MFG[2026-08-01]=%s,[2026-09-01]=%s,[2026-10-01]=%s" % (
        ctx.exact("CN_PMI_MFG", "2026-08-01"), sep, ctx.exact("CN_PMI_MFG", "2026-10-01")),
        "2026-09 再度站上荣枯线(%s)" % sep, "L%d 走位只写『春季回升→至2026-07回落』" % c_ln, False,
        note="MINOR: 走位漏披露 2026-09=50.1 再度高于荣枯线(2026-10 回落 49.3);结论(未构成趋势性转折)不变")
    seq_point(ctx, "W.CN.CPI", "⑩", "CN_CPI_YOY", ["2025-10-01", "2026-07-01", "2026-10-01"], "0.2→0.5→0.7", c_ln, c)
    seq_point(ctx, "W.CN.PPI", "⑩", "CN_PPI_YOY", ["2025-10-01", "2026-07-01", "2026-10-01"], "-2.1→3.5→5.7", c_ln, c)
    swings = {"CN_PPI_YOY": ctx.exact("CN_PPI_YOY", "2026-10-01") - ctx.exact("CN_PPI_YOY", "2025-10-01"),
              "US_CPI": y09 - ctx.yoy("CPI", "2025-09-01")[0] if y09 is not None else None,
              "US_CORE_PCE": vy[2] - vy[0], "EA_HICP": ctx.exact("EA_HICP_YOY", "2026-10-01") - ctx.exact("EA_HICP_YOY", "2025-10-01"),
              "JP_CPI": ctx.exact("JP_CPI_YOY", "2026-10-01") - ctx.exact("JP_CPI_YOY", "2025-10-01")}
    ctx.add("W.CN.PPI.maxswing", "⑩", "三锚首末摆动(pp) %s" % {k: (None if v is None else round(v, 3)) for k, v in swings.items()},
            "CN_PPI 最大=%s" % (swings["CN_PPI_YOY"] == max(v for v in swings.values() if v is not None)),
            "L%d 「为四地最大价格摆动」" % c_ln, swings["CN_PPI_YOY"] == max(v for v in swings.values() if v is not None))
    seq_point(ctx, "W.CN.OMO", "⑩", "CN_OMO_7D", ["2025-11-14", "2026-08-21", "2026-10-30"], "1.4→1.4→1.4", c_ln, c)
    lo = ctx.lob("CN_OMO_7D", C.CUTOFF)
    ctx.add("W.CN.OMO.stale", "⑩", "series_store.CN_OMO_7D 末观测=%s; 距截止 %d 天" % (lo, C.days_between(lo[0], C.CUTOFF)),
            "滞后%d天" % C.days_between(lo[0], C.CUTOFF), "L%d 「末观测2026-10-30滞后24天」" % c_ln,
            lo[0] == "2026-10-30" and C.days_between(lo[0], C.CUTOFF) == 24)
    seq_point(ctx, "W.CN.LPR", "⑩", "CN_LPR_1Y", ["2025-11-20", "2026-08-20", "2026-11-20"], "3.0→3.0→3.0", c_ln, c)
    on = ctx.ser("CN_POLICY_OVERNIGHT")
    ctx.add("W.CN.ON.absent", "⑩", "series_store.CN_POLICY_OVERNIGHT 首观测=%s 末观测=%s" % (on[0], on[-1]),
            "锚 2025-11-23/2026-08-23 前无观测=%s; 最新 1.25@2026-11-23=%s" % (on[0][0] > "2026-08-23", on[-1]),
            "L%d 「12个月前与3个月前锚日前无已发布观测,最新 1.25@2026-11-23」" % c_ln,
            on[0][0] > "2026-08-23" and on[-1][0] == "2026-11-23" and C.close(on[-1][1], 1.25, 2))
    ctx.add("W.CN.onhold", "⑩", "series_store.CN_OMO_7D 末值 1.4@2026-10-30(此后无观测) → CN_POLICY_OVERNIGHT 1.25 自 2026-11-02 起(注册表注: 2026-11-02 换锚后政策利率锚)",
            "锚口径切换且新锚水平 1.25 低于原操作目标 1.40(−15bp);换锚后 7 天工具序列无观测,无法证实『无变动』",
            "L%d/L%d 「政策利率全年按兵不动」/「中国按兵不动(背离)」" % (c_ln, h_ln), False,
            note="MINOR: 『按兵不动』对 2026-11-02 换锚后的政策利率锚不成立/不可证;同句已披露换锚,建议改『7天逆回购与LPR窗内无变动;2026-11-02 起政策利率锚切换为隔夜逆回购(1.25)』")
    # --- EA walk
    seq_point(ctx, "W.EA.GDP.yoy", "⑩", "EA_REAL_GDP_YOY", ["2025-07-01", "2026-04-01", "2026-07-01"], "1.11→1.19→1.28", e_ln, e)
    seq_point(ctx, "W.EA.HICP", "⑩", "EA_HICP_YOY", ["2025-10-01", "2026-07-01", "2026-10-01"], "2.1→2.9→4.0", e_ln, e)
    hv = {m: ctx.exact("EA_HICP_YOY", "2026-%02d-01" % m) for m in range(1, 11)}
    leg1 = [hv[3], hv[4], hv[5]]
    leg2 = [hv[8], hv[9], hv[10]]
    mono = lambda xs: all(xs[i] < xs[i + 1] for i in range(len(xs) - 1))
    ctx.add("W.EA.HICP.legs", "⑩", "series_store.EA_HICP_YOY 2026-01..10=%s" % [hv[m] for m in range(1, 11)],
            "第一段 03→05 单调升=%s; 第二段 08→10 单调升=%s; 上行实际自 2026-01(1.7)起" % (mono(leg1), mono(leg2)),
            "L%d 「两段上行(2026-03至05与2026-08至10)」" % e_ln, mono(leg1) and mono(leg2),
            note="NIT: 第一段起点写作 2026-03,序列自 2026-01(1.7)已连续上行至 2026-05")
    allv = [v for d, v in ctx.ser("EA_HICP_YOY") if "2025-11-23" <= d <= C.CUTOFF]
    latest = {"EA_HICP": ctx.exact("EA_HICP_YOY", "2026-10-01"), "US_CPI": y09, "CN_CPI": ctx.exact("CN_CPI_YOY", "2026-10-01"),
              "JP_CPI": ctx.exact("JP_CPI_YOY", "2026-10-01"), "JP_TOKYO": ctx.exact("JP_CPI_TOKYO_YOY", "2026-10-01")}
    ctx.add("W.EA.HICP.max", "⑩", "series_store.EA_HICP_YOY 窗内最大=%s; 四地最新消费通胀读数 %s" % (
        max(allv), {k: (None if v is None else round(v, 3)) for k, v in latest.items()}),
            "窗内最高=%s; 四地消费通胀最高=%s" % (ctx.exact("EA_HICP_YOY", "2026-10-01") == max(allv),
                                              ctx.exact("EA_HICP_YOY", "2026-10-01") >= max(v for v in latest.values() if v is not None)),
            "L%d 「最新4.0为四地最高通胀读数之一」" % e_ln,
            ctx.exact("EA_HICP_YOY", "2026-10-01") == max(allv) and ctx.exact("EA_HICP_YOY", "2026-10-01") >= max(v for v in latest.values() if v is not None))
    seq_point(ctx, "W.EA.DFR", "⑩", "ECB_DFR", ["2025-06-11", "2026-06-17", "2026-09-16"], "2.0→2.25→2.5", e_ln, e)
    ech = L.changes_in_window(ctx.ser("ECB_DFR"), "2025-11-23", C.CUTOFF)
    ctx.add("W.EA.DFR.events", "⑩", "series_store.ECB_DFR 窗内变更点 %s" % ech, "两次 +25bp(06-17/09-16)",
            "L%d 「决议2026-06-11生效2026-06-17(+25个基点)、决议2026-09-10生效2026-09-16(+25个基点)」" % e_ln,
            len(ech) == 2 and ech[0][0] == "2026-06-17" and ech[1][0] == "2026-09-16" and all(C.close(x[2] - x[1], 0.25, 2) for x in ech))
    # --- JP walk
    seq_point(ctx, "W.JP.GDP.yoy", "⑩", "JP_REAL_GDP_YOY", ["2025-07-01", "2026-04-01", "2026-07-01"], "0.63→0.80→1.16", j_ln, j)
    seq_point(ctx, "W.JP.CPI", "⑩", "JP_CPI_YOY", ["2025-10-01", "2026-07-01", "2026-10-01"], "2.99→1.97→2.44", j_ln, j)
    seq_point(ctx, "W.JP.TOK", "⑩", "JP_CPI_TOKYO_YOY", ["2026-07-01", "2026-10-01"], "1.85→2.73", j_ln, j)
    tk = ctx.ser("JP_CPI_TOKYO_YOY")
    ctx.add("W.JP.TOK.absent12m", "⑩", "series_store.JP_CPI_TOKYO_YOY 首观测=%s" % (tk[0],), "2025-11-23 前无观测=%s" % (tk[0][0] > "2025-11-23"),
            "L%d 「12个月前锚日前无已发布观测」" % j_ln, tk[0][0] > "2025-11-23")
    ctx.add("W.JP.TARGET.absent", "⑩", "metric_registry.metrics[].metric_id 含 JP_POLICY_TARGET=%s; series_store 含=%s" % (
        "JP_POLICY_TARGET" in ctx.reg_ids, ctx.has("JP_POLICY_TARGET")), "注册表与序列均缺席",
        "L%d 「计划指标 JP_POLICY_TARGET 不在注册表…数据不可得」" % j_ln,
        "JP_POLICY_TARGET" not in ctx.reg_ids and not ctx.has("JP_POLICY_TARGET"))
    seq_point(ctx, "W.JP.RATE", "⑩", "JP_POLICY_RATE", ["2025-10-01", "2026-07-01", "2026-10-01"], "0.477→0.978→1.227", j_ln, j)
    a, b = ctx.exact("JP_POLICY_RATE", "2025-12-01"), ctx.exact("JP_POLICY_RATE", "2026-10-01")
    ctx.add("W.JP.RATE.net", "⑩", "series_store.JP_POLICY_RATE[2025-12-01]=%s,[2026-10-01]=%s" % (a, b), "净 %+d bp" % round((b - a) * 100),
            "L%d 「自2025-12月均0.557升至2026-10月均1.227净+67个基点」" % j_ln, C.close(a, 0.557, 3) and C.close(b, 1.227, 3) and C.close((b - a) * 100, 67, 0),
            note="MINOR: 窗内变更点之和 +75bp(含 2025-12-01 +8bp),+67bp 为首末月均差")
    ent = [x for x in ctx.cal.get("entries", []) if x.get("entry_id") == "RC-JP-BOJ-TARGET-2026-09"]
    ent = ent[0] if ent else {}
    ctx.add("W.JP.BOJ", "⑩", "release_calendar.entries[RC-JP-BOJ-TARGET-2026-09].decision_date/effective_on/target_value=%s/%s/%s" % (
        ent.get("decision_date"), ent.get("effective_on"), ent.get("target_value")), "决议 2026-09-18/生效 2026-09-24/目标 1.25",
        "L%d 「政策决议2026-09-18(生效2026-09-24,目标水平1.25)」" % j_ln,
        ent.get("decision_date") == "2026-09-18" and ent.get("effective_on") == "2026-09-24" and C.close(ent.get("target_value"), 1.25, 2))
    jpr = [(d, v) for d, v in ctx.ser("JP_POLICY_RATE") if "2025-11-23" <= d <= C.CUTOFF]
    first_up = next((jpr[i][0] for i in range(1, len(jpr)) if jpr[i][1] > jpr[i - 1][1] + 1e-9), None)
    max_dd = max([jpr[i - 1][1] - jpr[i][1] for i in range(1, len(jpr))] or [0.0])
    others = {sid: L.changes_in_window(ctx.ser(sid), "2025-11-23", "2026-01-31") for sid in ("DFEDTARU", "ECB_DFR", "ECB_MRO", "CN_LPR_1Y", "CN_OMO_7D") if ctx.ser(sid)}
    ups = [sid for sid, ch in others.items() for x in ch if x[2] > x[1]]
    ctx.add("W.JP.first", "⑩", "series_store.JP_POLICY_RATE 窗内首个上行月=%s; 最大月环比降幅=%.4f; 其他央行 2026-02 前窗内上调=%s(变更点 %s)" % (
        first_up, max_dd, ups, others), "2026-02 前已开始上调且唯一; 未回撤(最大降幅<0.5bp)",
        "L%d 「为四地中唯一在美欧通胀同窗回升(2026-02起)之前已开始上调、窗内未回撤的央行」" % j_ln,
        first_up is not None and first_up < "2026-02-01" and not ups and max_dd < 0.005)
    # --- headline
    w = {"CPI": (ctx.yoy("CPI", "2026-02-01")[0], ctx.yoy("CPI", "2026-05-01")[0]),
         "EA_HICP_YOY": (ctx.exact("EA_HICP_YOY", "2026-02-01"), ctx.exact("EA_HICP_YOY", "2026-05-01")),
         "CN_PPI_YOY": (ctx.exact("CN_PPI_YOY", "2026-02-01"), ctx.exact("CN_PPI_YOY", "2026-05-01"))}
    ctx.add("HL.window", "⑩", "series_store 2026-02→2026-05: %s" % {k: [None if x is None else round(x, 3) for x in v] for k, v in w.items()},
            "三地同窗回升=%s" % all(v[1] > v[0] for v in w.values()), "L%d 「美欧中通胀在2026-02至2026-05同窗共振回升」" % h_ln,
            all(v[1] > v[0] for v in w.values()) and ("2026-02至2026-05" in h))
    ctx.add("HL.ecb", "⑩", "series_store.ECB_DFR 变更点 %s; 决议日=生效−6天" % ech, "决议 2026-06-11/2026-09-10, 生效 06-17/09-16",
            "L%d 「欧央行两度加息(决议2026-06-11生效2026-06-17、决议2026-09-10生效2026-09-16)」" % h_ln,
            ("决议2026-06-11生效2026-06-17" in h and "决议2026-09-10生效2026-09-16" in h and len(ech) == 2))
    ctx.add("HL.fed", "⑩", "series_store.DFF[2026-09-16→17]=%s→%s; 12个月前锚值[2025-11-22]=%s" % (
        ctx.exact("DFF", "2026-09-16"), ctx.exact("DFF", "2026-09-17"), ctx.exact("DFF", "2025-11-22")), "回到 3.88(=12个月前锚值)",
            "L%d 「美联储决议2026-09-16生效2026-09-17回补此前降息(有效联邦基金利率回到3.88)」" % h_ln,
            C.close(ctx.exact("DFF", "2026-09-17"), 3.88, 2) and C.close(ctx.exact("DFF", "2025-11-22"), 3.88, 2)
            and "决议2026-09-16生效2026-09-17" in h and "回到3.88" in h)
    ctx.add("HL.boj", "⑩", "release_calendar RC-JP-BOJ-TARGET-2026-09 decision_date/effective_on", "2026-09-18/2026-09-24",
            "L%d 「日本央行决议2026-09-18生效2026-09-24」" % h_ln,
            ent.get("decision_date") == "2026-09-18" and ent.get("effective_on") == "2026-09-24" and "日本央行决议2026-09-18生效2026-09-24" in h)
    trio = (ctx.rep.get("research_plan") or {}).get("us_rates_trio") or {}
    c12 = trio.get("chg_bp_12m") or {}
    ctx.add("HL.rates", "⑩", "report.json research_plan.us_rates_trio.chg_bp_12m=%s" % c12, "名义+91/实际+102/盈亏平衡-11",
            "L%d 「名义+91bp、由实际+102bp主导(盈亏平衡-11bp)」" % h_ln,
            c12.get("UST_10Y") == 91 and c12.get("TIPS_10Y") == 102 and c12.get("BEI_10Y") == -11
            and "名义+91bp" in h and "实际+102bp主导" in h and "盈亏平衡-11bp" in h)
    am = {r.get("metric_id"): r for r in (ctx.rep.get("research_plan") or {}).get("asset_moves", {}).get("rows", [])}
    ctx.add("HL.assets", "⑩", "report.json research_plan.asset_moves.rows SPX chg_pct=%s VIX chg_pct=%s; 窗起 %s" % (
        (am.get("SPX") or {}).get("chg_pct"), (am.get("VIX") or {}).get("chg_pct"), (am.get("SPX") or {}).get("window", {}).get("from")),
        "SPX -9.36 / VIX +55.48 / 2026-10-23 起", "L%d 「近1个月(2026-10-23起)…标普500指数下跌9.36%%、VIX升55.48%%」" % h_ln,
        (am.get("SPX") or {}).get("chg_pct") == -9.36 and (am.get("VIX") or {}).get("chg_pct") == 55.48
        and "2026-10-23起" in h and "下跌9.36%" in h and "VIX升55.48%" in h)
    iy = [ctx.yoy("INDPRO", d)[0] for d in ("2025-11-01", "2026-02-01", "2026-10-01")]
    ctx.add("HL.indpro", "⑩", "series_store.INDPRO 同比 2025-11/2026-02/2026-10=%s" % [round(x, 4) for x in iy],
            "折半(%.2f<%.2f)后回升(%.2f)" % (iy[1], iy[0] / 2, iy[2]), "L%d 「美国工业同比一度折半后回升」" % h_ln,
            iy[1] < iy[0] / 2 and iy[2] > iy[1])
    gy = {"EA": [ctx.exact("EA_REAL_GDP_YOY", d) for d in ("2025-07-01", "2026-04-01", "2026-07-01")],
          "JP": [ctx.exact("JP_REAL_GDP_YOY", d) for d in ("2025-07-01", "2026-04-01", "2026-07-01")]}
    ctx.add("HL.gdp", "⑩", "series_store EA/JP GDP 同比三锚 %s" % gy, "缓步加速(单调升)=%s" % all(mono(v) for v in gy.values()),
            "L%d 「欧元区与日本GDP同比缓步加速」" % h_ln, all(mono(v) for v in gy.values()))


# ----------------------------------------------------------------------------- ⑪ honest absences + Gate A
def run_absences(ctx):
    ctx.add("HA.JP_POLICY_TARGET", "⑪", "metric_registry 含=%s; series_store 含=%s" % ("JP_POLICY_TARGET" in ctx.reg_ids, ctx.has("JP_POLICY_TARGET")),
            "注册表与序列均缺席", "MAP L45/L186 缺口声明(JP_POLICY_TARGET 历史序列与元数据均不可得)",
            "JP_POLICY_TARGET" not in ctx.reg_ids and not ctx.has("JP_POLICY_TARGET"))
    vis12 = ctx.visible("JP_CPI_TOKYO_YOY", "2025-11-23")
    ctx.add("HA.TOKYO.12个月前", "⑪", "series_store.JP_CPI_TOKYO_YOY 首观测 %s; 锚 2025-11-23 可见观测=%s" % (
        ctx.ser("JP_CPI_TOKYO_YOY")[0][0], vis12), "不可得=%s" % (vis12 is None), "MAP L30/L62 东京都CPI同比 12个月前=数据不可得", vis12 is None)
    vis3 = ctx.visible("JP_CPI_TOKYO_YOY", "2026-08-23")
    ctx.add("HA.TOKYO.3个月前", "⑪", "series_store.JP_CPI_TOKYO_YOY 锚 2026-08-23 可见观测=%s" % (vis3,),
            "%s@%s" % (None if vis3 is None else vis3[1], None if vis3 is None else vis3[0][:7]), "MAP L30/L62 东京都CPI同比 3个月前=1.85(观测2026-07)",
            vis3 is not None and vis3[0][:7] == "2026-07" and C.close(vis3[1], 1.85, 2))
    on = ctx.ser("CN_POLICY_OVERNIGHT")
    for anc, lab in (("2025-11-23", "12个月前"), ("2026-08-23", "3个月前")):
        ctx.add("HA.CN_POLICY_OVERNIGHT.%s" % lab, "⑪", "series_store.CN_POLICY_OVERNIGHT 首观测 %s(n=%d)" % (on[0][0], len(on)),
                "锚 %s 前无观测=%s" % (anc, on[0][0] > anc), "MAP L24/L56 隔夜逆回购利率 %s=数据不可得" % lab, on[0][0] > anc)
    for sid in ("CPI", "CORE_CPI"):
        ctx.add("HA.%s.base2025-10" % sid, "⑪", "series_store.%s[2025-10-01]=%s" % (sid, ctx.exact(sid, "2025-10-01")),
                "基期缺席,同比不可得=%s" % (ctx.yoy(sid, "2026-10-01")[0] is None), "MAP L36/L38 %s 同比不可得: 缺基期" % sid,
                ctx.exact(sid, "2025-10-01") is None and ctx.yoy(sid, "2026-10-01")[0] is None)
    jgb = [s for s in ctx.snap["series_store"] if s.startswith("JGB")]
    fmetrics = {f.get("metric_id") for f in ctx.snap.get("facts", []) if isinstance(f, dict)}
    ctx.add("HA.JGB.series", "⑪", "series_store 中 JGB* 序列=%s; facts 含 JGB=%s" % (jgb, sorted(m for m in fmetrics if m.startswith("JGB"))),
            "无 JGB 历史序列,仅单点事实", "MAP L205 「JGB 收益率历史序列不在引擎(单点观测)」", not jgb and any(m.startswith("JGB") for m in fmetrics))
    ctx.add("HA.UNEMP.2025-10", "⑪", "series_store.UNEMPLOYMENT[2025-10-01]=%s; [2025-09-01]=%s 发布 %s" % (
        ctx.exact("UNEMPLOYMENT", "2025-10-01"), ctx.exact("UNEMPLOYMENT", "2025-09-01"), ctx.pub("UNEMPLOYMENT", "2025-09-01")),
        "2025-10 缺席; 12 个月前锚取 2025-09", "MAP L34 失业率 12个月前=4.4(观测2025-09)",
        ctx.exact("UNEMPLOYMENT", "2025-10-01") is None and ctx.pub("UNEMPLOYMENT", "2025-09-01")[0] <= "2025-11-23")
    lo = ctx.lob("CN_OMO_7D", C.CUTOFF)
    ctx.add("HA.CN_OMO_7D.stale", "⑪", "series_store.CN_OMO_7D 末观测 %s(滞后 %d 天>10 天窗口)" % (lo, C.days_between(lo[0], C.CUTOFF)),
            "过期属实", "MAP L23/L55 ⚠过期: 末观测2026-10-30(滞后24天>10天窗口)", lo[0] == "2026-10-30")
    # Gate A
    from collections import Counter
    cnt = Counter()
    for st in ctx.rep.get("steps", []):
        ga = (st.get("envelope") or {}).get("gate_a")
        cnt[str(ga.get("status") if isinstance(ga, dict) else ga)] += 1
    ga = ctx.snap.get("gate_a") or {}
    map_txt = "\n".join(ctx.map_lines)
    disclosed = bool(re.search(r"gate_a|Gate A|数据门|DEGRADED|降级披露", map_txt))
    ctx.add("HA.gate.steps", "⑪", "report.json steps[*].envelope.gate_a.status 计数=%s; snapshot.gate_a.status=%s(noncore_missing=%s)" % (
        dict(cnt), ga.get("status"), ga.get("noncore_missing")), "MAP_REPORT 披露 Gate A 状态=%s" % disclosed,
        "report.md L5 「数据门(gate_a): 61/61 信封步非 OK(DEGRADED)」; MAP_REPORT.md 无对应披露行", disclosed,
        note="MINOR: 读者面 MAP_REPORT 未披露数据门 DEGRADED 状态(report.md 有);且 gate_a.noncore_missing 所列 5 个序列在 series_store 在场并被本报告引用")
    present = [s for s in (ga.get("noncore_missing") or []) if ctx.has(s)]
    ctx.add("HA.gate.list", "⑪", "snapshot.gate_a.noncore_missing=%s; 其中 series_store 在场=%s(facts 条数=%s)" % (
        ga.get("noncore_missing"), present, {s: sum(1 for f in ctx.snap.get("facts", []) if isinstance(f, dict) and f.get("metric_id") == s) for s in present}),
        "门面『缺席』与序列面在场并存", "MAP 引用 %s" % present, True,
        note="说明: 门面按事实层判缺席,序列层在场——报告引用序列值;读者面无从知晓该降级")
    # judgment-file statement about China credit / demand series
    aj = aj_of(ctx)
    stmts = {c.get("id"): c.get("statement", "") for c in ((aj.get("l3") or {}).get("contradictions") or [])}
    c3 = stmts.get("C3", "")
    has_credit = ctx.has("CN_NEW_LOANS")
    nl = ctx.ser("CN_NEW_LOANS") if has_credit else []
    demand_facts = sorted(m for m in fmetrics if m.startswith("CN_"))
    ctx.add("HA.C3.credit", "⑪", "agent_judgment.json l3.contradictions[C3].statement 含『引擎面无中国利率预期序列与信贷/内需序列』=%s; series_store.CN_NEW_LOANS n=%d 末观测 %s; facts 含 CN_*=%s" % (
        "信贷/内需序列" in c3, len(nl), nl[-1][0] if nl else None, demand_facts),
        "证据面陈述与快照不符" if (has_credit and "信贷/内需序列" in c3) else "相符",
        "C3.statement 「引擎面无中国利率预期序列与信贷/内需序列」", not (has_credit and "信贷/内需序列" in c3),
        note="MINOR(判断档): 快照含 CN_NEW_LOANS(2008-01..2026-10,226 观测,L1 事实在场)与 CN_TOTAL_TURNOVER 事实——『无信贷/内需序列』不实;MAP_REPORT 未渲染该句")


# ----------------------------------------------------------------------------- ⑫ cutoff-day labels
def run_cutoffday(ctx):
    asof = ctx.snap.get("research_as_of")
    ctx.add("CD.asof", "⑫", "snapshot.research_as_of=%s (=%s UTC)" % (asof, asof.replace("T", " ").replace("+08:00", "") + " −8h"),
            asof[:10], "MAP L4 研究截止日 2026-11-23", asof[:10] == C.CUTOFF)
    for i, x in enumerate(ctx.map_lines):
        if "研究截止日: 2026-11-23" in x:
            ctx.add("CD.map.asof", "⑫", "snapshot.research_as_of 日期部分 %s" % asof[:10], x.split("|")[1].strip()[:40] if "|" in x else x[:40],
                    "MAP L%d 研究截止日" % (i + 1), "2026-11-23" in x)
            break
    cited = {}
    for sid in SIDS_CITED_1123:
        if ctx.has(sid):
            lo = ctx.lob(sid, C.CUTOFF)
            cited[sid] = lo
    ctx.add("CD.series.1123", "⑫", "series_store 各序列 ≤截止日末观测: %s" % cited, "截止日当日有观测=%s" % [s for s, t in cited.items() if t[0] == C.CUTOFF],
            "MAP 引用 @2026-11-23 的序列", all(t[0] <= C.CUTOFF for t in cited.values()), note="信息点: 当日观测日期均不晚于 research_as_of 日期")
    TOK = {"VIX": ["VIX"], "BRENT_F": ["BRENT_F"], "USDJPY": ["USDJPY"], "DAX": ["DAX"], "DXY": ["DXY"], "GOLD_F": ["GOLD_F"]}
    ALLTOK = [t for ts in TOK.values() for t in ts]
    LINES = {"VIX": (11, 80, 199), "BRENT_F": (192, 194, 214), "USDJPY": (205, 208, 217),
             "DAX": (80, 167, 199), "DXY": (80, 170, 199), "GOLD_F": (80, 171, 199)}
    for sid, lns in LINES.items():
        lab_lines, unlab_lines = [], []
        for n in lns:
            x = ctx.map_lines[n - 1]
            for tok in TOK[sid]:
                for m in re.finditer(re.escape(tok), x):
                    nxt = [q for t2 in ALLTOK if t2 != tok for q in [x.find(t2, m.end())] if q >= 0]
                    seg = x[m.start(): min(nxt) if nxt else len(x)]
                    (lab_lines if "实时快照" in seg else unlab_lines).append(n)
        oncut = cited[sid][0] == C.CUTOFF
        ctx.add("CD.%s.label" % sid, "⑫", "series_store.%s 末观测 %s(截止日当日; research_as_of=%s); 引用行 L%s 中带说明的引用行=%s, 未带=%s" % (
            sid, cited[sid], asof, list(lns), sorted(set(lab_lines)), sorted(set(unlab_lines))),
            "该序列截止日当日值在 MAP 至少一处带时点/口径说明=%s" % bool(lab_lines),
            "MAP 引用 %s@2026-11-23 的各行(非收盘价说明)" % sid, (not oncut) or bool(lab_lines),
            note="" if (not oncut or lab_lines) else "MINOR: 同为 11-23 当日值,VIX/BRENT_F/USDJPY 带说明而 %s 全部引用处不带(research_as_of=20:41:34+08:00=12:41:34 UTC;报告自身对同为 11-23 观测的 VIX/BRENT_F/USDJPY 标注『当日实时快照(非收盘价)』)" % sid)
        if lab_lines and unlab_lines:
            ctx.note("⑫", "%s: 说明只出现在 L%s,L%s 等引用处未带(标注不遍历)——NIT" % (sid, sorted(set(lab_lines)), sorted(set(unlab_lines))))
    sh = cited.get("SHCOMP")
    ctx.add("CD.SHCOMP.note", "⑫", "series_store.SHCOMP 末观测 %s; MAP L166/L199 未带说明" % (sh,), "无说明", "MAP SHCOMP 当日值",
            sh[0] == C.CUTOFF, note="信息点: 未带说明(未计入偏离)")


# ----------------------------------------------------------------------------- ⑬ map sub-questions
def run_map_coverage(ctx):
    heads = [(i + 1, x.strip()) for i, x in enumerate(ctx.map_lines) if x.startswith("## ")]
    htxt = [h for _, h in heads]
    need = {"总判断": "一句总判断", "三时点环境对照(增长/通胀/货币政策×四地)": "四地三时点环境对照", "三个转折": "过去一年的三个转折",
            "传导机制": "证据最充分的传导机制", "竞争解释对质": "主解释 vs 竞争解释", "情景": "情景", "历史类比": "历史上结构最像的时期"}
    for k, v in need.items():
        ctx.add("MR.head.%s" % k, "⑬", "MAP_REPORT.md 二级标题 %s" % [h for _, h in heads], v, "工单子问『%s』对应章节" % k, any(v in t for t in htxt))
    t = table_by_header(ctx, ["日期", "指标", "前值→后值"])
    ctx.add("MR.turning.cols", "⑬", "转折表表头=%s" % (t["header"] if t else None), "含『谁先变』『跟进/背离』列",
            "工单『谁先变,谁跟进或背离』", bool(t) and "谁先变" in t["header"] and "跟进/背离" in t["header"])
    ctx.add("MR.turning.n", "⑬", "转折表数据行数=%d" % (len(t["rows"]) if t else 0), 3, "工单『最重要的三个转折』", bool(t) and len(t["rows"]) == 3)
    links = [i + 1 for i, x in enumerate(ctx.map_lines) if x.strip().startswith("- 能区分解释的指标:")]
    comps = [i + 1 for i, x in enumerate(ctx.map_lines) if x.strip().startswith("- 竞争解释:")]
    hyps = [i + 1 for i, x in enumerate(ctx.map_lines) if x.strip().startswith("- 因果假设:")]
    ctx.add("MR.distinguish", "⑬", "『能区分解释的指标』行=%s; 『竞争解释』行=%s; 『因果假设』行=%s" % (links, comps, hyps), "四环各有一条",
            "工单『还有什么解释,哪个指标能区分它们』", len(links) == 4 and len(comps) == 4 and len(hyps) == 4)
    sync = [i + 1 for i, x in enumerate(ctx.map_lines) if x.startswith("- 当时同步性")]
    exp = [i + 1 for i, x in enumerate(ctx.map_lines) if "随后结果" in x or "事后结果" in x]
    hist = [i for i, x in enumerate(ctx.map_lines) if x.startswith("## 历史上结构最像的时期")]
    secs = [i + 1 for i, x in enumerate(ctx.map_lines) if x.startswith("### ") and "TOP-5独立簇" in x and re.match(r"### \d{4}-\d{2}", x)]
    ctx.add("MR.hist.sync", "⑬", "历史段小节=%s; 『当时同步性』所在行=%s" % (secs, sync), "三段各一", "工单『当时其他经济体是否同步』",
            len(secs) == 3 and len(sync) == 3)
    ctx.add("MR.hist.expost", "⑬", "『随后结果/事后结果』所在行=%s" % exp, "三段各一且以事后口径", "工单『随后3、6、12个月…实际怎么走』",
            len(secs) == 3 and len([x for x in exp if x > (hist[0] if hist else 10 ** 9)]) >= 3)
    ctx.add("MR.gap.note", "⑬", "MAP L44 缺数格说明段=%s" % ("缺数格说明" in "\n".join(ctx.map_lines[:50])), "在场",
            "工单『证据不足之处』的显式披露", "缺数格说明" in "\n".join(ctx.map_lines[:50]),
            note="report.md 另载『任务目标缺口 8 项』(US_REAL_GDP/CORE_PCE/CN_POLICY_OVERNIGHT 等),MAP 读者面未逐项披露——并入 MINOR(gate/缺口披露)")
