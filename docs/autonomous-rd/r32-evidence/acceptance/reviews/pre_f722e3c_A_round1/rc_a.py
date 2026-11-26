#!/usr/bin/env python3
"""Recompute sections ①(cutoff) ②(anchor grid) ③(YoY) ④(policy) — read-only."""
import datetime
import re
import sys

sys.path.insert(0, "/tmp/r32-accept/review/A_round1")
import rc_common as C  # noqa: E402

L = C.L
STEP_SERIES = {"ECB_DFR", "ECB_MRO", "CN_LPR_1Y"}

MAP_ROW_SID = [
    ("制造业PMI", "CN_PMI_MFG"), ("居民消费价格指数(CPI)同比", "CN_CPI_YOY"), ("工业生产者出厂价格指数(PPI)同比", "CN_PPI_YOY"),
    ("贷款市场报价利率(LPR)1年期", "CN_LPR_1Y"), ("央行7天期逆回购利率", "CN_OMO_7D"),
    ("央行隔夜逆回购利率(政策利率锚)", "CN_POLICY_OVERNIGHT"), ("欧元区实际GDP同比", "EA_REAL_GDP_YOY"),
    ("欧元区HICP同比", "EA_HICP_YOY"), ("欧央行存款便利利率", "ECB_DFR"), ("欧央行主要再融资利率", "ECB_MRO"),
    ("日本实际GDP同比", "JP_REAL_GDP_YOY"), ("东京都CPI同比", "JP_CPI_TOKYO_YOY"), ("全国CPI同比(日本)", "JP_CPI_YOY"),
    ("日本无担保隔夜拆借利率(月均)", "JP_POLICY_RATE"), ("工业生产指数(SA)", "INDPRO"), ("失业率(U-3)", "UNEMPLOYMENT"),
    ("美国实际GDP(SAAR)", "US_REAL_GDP"), ("核心CPI(SA", "CORE_CPI"), ("核心PCE(SA)", "CORE_PCE"),
    ("CPI物价指数(SA)", "CPI"), ("联邦基金目标区间上限", "DFEDTARU"), ("有效联邦基金利率(日频)", "DFF"),
]
NAME_SID = {
    "贷款市场报价利率(LPR)1年期": "CN_LPR_1Y", "央行7天期逆回购利率": "CN_OMO_7D", "央行隔夜逆回购利率(政策利率锚)": "CN_POLICY_OVERNIGHT",
    "欧央行存款便利利率": "ECB_DFR", "欧央行主要再融资利率": "ECB_MRO", "日本无担保隔夜拆借利率(月均)": "JP_POLICY_RATE",
    "联邦基金目标区间上限": "DFEDTARU", "有效联邦基金利率(日频)": "DFF",
}
LEVEL_YOY = {"CPI", "CORE_CPI", "CORE_PCE", "INDPRO", "US_REAL_GDP", "CN_PMI_MFG"}


def first_num(s):
    return C.num(s)


def first_date(s):
    m = re.search(r"\d{4}-\d{2}-\d{2}", s or "")
    return m.group(0) if m else None


NUM_RE = r"[-+]?\d+(?:\.\d+)?"


def first_num_str(s):
    m = re.search(NUM_RE, str(s).replace("−", "-"))
    return m.group(0) if m else None


def ndec(s):
    t = first_num_str(s)
    return len(t.split(".")[1]) if t and "." in t else 0


def same_round(computed, reported_str):
    rep = C.num(reported_str)
    if rep is None or computed is None:
        return rep is None and computed is None
    return C.close(computed, rep, ndec(reported_str))


def table_by_header(ctx, first_cells):
    for t in ctx.tables:
        if t["header"][:len(first_cells)] == first_cells:
            return t
    return None


def yoy_cell_ok(ctx, sid, vis, cell, pid, where):
    """cell carries 同比≈X% / 同比不可得 annotations -> points"""
    yy, bd, bv = ctx.yoy(sid, vis[0])
    m = re.search(r"(?<!最近有效)同比≈([-+]?\d+(?:\.\d+)?)%", cell.replace("−", "-"))
    if m:
        ctx.add(pid + ".yoy", "③", "series_store.%s[%s]/[%s]-1" % (sid, vis[0], bd), yy, "%s 同比≈%s%%" % (where, m.group(1)),
                C.close(yy, float(m.group(1)), ndec(m.group(1))), note="基期值=%s" % bv)
    if "同比不可得" in cell:
        m2 = re.search(r"最近有效同比≈([-+]?\d+(?:\.\d+)?)%@(\d{4}-\d{2})", cell)
        if m2:
            lv = ctx.exact(sid, m2.group(2) + "-01")
            lyy, lbd, lbv = ctx.yoy(sid, m2.group(2) + "-01")
            nxt = C.L.shift_months(m2.group(2) + "-01", 1)
            prev_ok = ctx.yoy(sid, C.L.shift_months(m2.group(2) + "-01", -1))[0] is not None
            ctx.add(pid + ".lv", "③", "series_store.%s 最近可算同比月及其值(次月基期缺席=%s, 更早月可算=%s)" % (
                sid, ctx.yoy(sid, nxt)[0] is None, prev_ok), "%s@%s" % (m2.group(2), lyy),
                "%s 最近有效同比≈%s%%@%s" % (where, m2.group(1), m2.group(2)),
                C.close(lyy, float(m2.group(1)), ndec(m2.group(1))) and ctx.yoy(sid, nxt)[0] is None and prev_ok and lv is not None)
        else:
            ctx.add(pid + ".lv", "③", "series_store.%s 同比@%s (基期 %s 在场?)" % (sid, vis[0], bd), yy,
                    "%s 同比不可得" % where, yy is None and bv is None)
    return yy


# --------------------------------------------------------------------------- ①
def run_cutoff(ctx):
    snap, rep = ctx.snap, ctx.rep
    hdr = ctx.map_lines[3]
    m = re.search(r"研究截止日: (\d{4}-\d{2}-\d{2}) \| 快照: (\S+) \| 运行: (\S+) \| 代码: ([0-9a-f]+)", hdr)
    eg = rep["run"].get("evidence_gate") or {}
    ctx.add("C01", "①", "snapshot.research_as_of[:10] / snapshot.target_date / report.run.evidence_asof",
            "%s / %s / %s" % (snap["research_as_of"][:10], snap["target_date"], rep["run"].get("evidence_asof")),
            "研究截止日 %s (MAP L4)" % m.group(1),
            m.group(1) == snap["research_as_of"][:10] == rep["run"].get("evidence_asof") == "2026-11-23"
            and snap["target_date"] == "20261123")
    ctx.add("C02", "①", "snapshot.snapshot_id; report.run.evidence_gate.source_snapshot_id",
            "%s / %s" % (snap["snapshot_id"], eg.get("source_snapshot_id")), "快照 %s (MAP L4)" % m.group(2),
            m.group(2) == snap["snapshot_id"] == eg.get("source_snapshot_id"))
    ctx.add("C03", "①", "report.run.git_head (CODE_VERSION 印章)", rep["run"].get("git_head"), "代码 %s (MAP L4)" % m.group(4),
            m.group(4) == rep["run"].get("git_head") == "f722e3c0bf7cd10aee64a8f4a166a136180a28ea")
    cnt = eg.get("counts") or {}
    l5 = ctx.map_lines[4]
    m5 = re.search(r"事实: 保留 (\d+) / 重建 (\d+) / 剔除 (\d+)\+版本 (\d+) \| 序列剔观测 (\d+)", l5)
    exp = (cnt.get("facts_kept"), cnt.get("facts_rebuilt"), cnt.get("facts_dropped"), cnt.get("facts_excluded_version"),
           cnt.get("series_observations_dropped"))
    ctx.add("C04", "①", "report.run.evidence_gate.counts", "/".join(str(x) for x in exp), "MAP L5 " + m5.group(0),
            tuple(int(x) for x in m5.groups()) == tuple(int(x) for x in exp))
    ctx.add("C05", "①", "len(snapshot.facts) / len(snapshot.series_store) vs evidence_gate.counts.series_n",
            "%d / %d" % (len(snap["facts"]), len(snap["series_store"])), "MAP L5 事实保留 %s; series_n=%s" % (
                m5.group(1), cnt.get("series_n")),
            len(snap["facts"]) == cnt.get("facts_kept") and len(snap["series_store"]) == cnt.get("series_n"))
    over = []
    for sid, s in snap["series_store"].items():
        for d, v in zip(s["dates"], s["values"]):
            if v is not None and v == v and d > C.CUTOFF:
                over.append((sid, d))
    ctx.add("C06", "①", "series_store[*].dates vs 截止日", "晚于截止日的观测数=%d" % len(over), "全部观测日≤2026-11-23",
            len(over) == 0, note=str(over[:5]) if over else "")
    dates = ["2026-06-11", "2026-06-17", "2026-09-10", "2026-09-16", "2026-09-17", "2026-09-18", "2026-09-24",
             "2026-10-30", "2026-11-18", "2026-11-20"]
    ctx.add("C07", "①", "MAP L11/L117/L149/L183 决议/生效/纪要日 vs 截止日", "max=%s" % max(dates), "全部≤2026-11-23",
            max(dates) <= C.CUTOFF)
    txt = "\n".join(ctx.map_lines)
    n_lab = txt.count("随后结果(事后实际——与当时同步性分开,事后陈述非预测)")
    n_warn = txt.count("候选期**之后**的经济与资产表现为事后实际结果——当时不可知,亦非对本次的预测")
    ctx.add("C08", "①", "MAP 历史类比三段: 事后段标注计数", "事后实际标注=%d, 事后结果标注块=%d" % (n_lab, n_warn), "三段各一(=3)",
            n_lab == 3 and n_warn == 3)
    pred = re.findall(r"随后\d+个月[^\n]{0,60}(?:预计|预期|预测将|将上涨|将下跌|有望)", txt)
    ctx.add("C09", "①", "MAP 历史类比『随后N个月』行预测性措辞检索", "命中=%d" % len(pred), "0(事后实际不得表述为预测)",
            len(pred) == 0, note="; ".join(pred[:3]))
    kt_months = re.findall(r"^### (\d{4}-\d{2})\(距离", txt, flags=re.M)
    n_exp = 0
    bad = []
    for t in ctx.tables:
        if t["header"][:3] != ["指标", "观测期", "值"]:
            continue
        sec = None
        for ln in ctx.map_lines[:t["line"]]:
            m3 = re.search(r"^### (\d{4}-\d{2})\(距离", ln)
            if m3:
                sec = m3.group(1)
        cut_end = C.month_end(sec)
        for r in t["rows"]:
            if r[2].startswith("数据不可得"):
                continue
            pd = first_date(r[3])
            n_exp += 1
            if pd is None or pd <= cut_end:
                bad.append((sec, r[0], r[1], pd))
    ctx.add("C10", "①", "事后段各行首次发布日 > 该段截止月末(截止月=%s)" % "/".join(kt_months),
            "事后段行=%d, 违反=%d" % (n_exp, len(bad)), "全部事后行发布日晚于截止月末", len(bad) == 0, note=str(bad[:4]))
    ctx.note("①", "历史段=%s; 事后段行=%d" % (kt_months, n_exp))


# --------------------------------------------------------------------------- ②
def run_anchor_grid(ctx):
    kt = table_by_header(ctx, ["指标", "锚", "值", "单位", "实际观测日"])
    n = 0
    pub_bad = []
    for r in kt["rows"]:
        sid, lab, val, unit, obsd, pubc = r[0], r[1], r[2], r[3], r[4], r[5]
        anchor = C.ANCHOR_DATE[lab]
        vis = ctx.visible(sid, anchor)
        n += 1
        absent_rep = val.startswith("数据不可得")
        ctx.add("K%02d.v" % n, "②", "series_store.%s 发布日≤%s 的最新可见观测" % (sid, anchor),
                "无" if vis is None else vis[1], "%s@%s=%s" % (sid, lab, val),
                absent_rep == (vis is None) and (vis is None or same_round(vis[1], val)))
        ctx.add("K%02d.d" % n, "②", "series_store.%s 最新可见观测日" % sid, "—" if vis is None else vis[0],
                "%s@%s 观测 %s" % (sid, lab, obsd),
                (vis is None and obsd in ("—", "-", "")) or (vis is not None and vis[0] == obsd))
        pd = first_date(pubc)
        if vis is None:
            continue
        mine, basis = vis[2], vis[3]
        okp = (mine == pd) or ("calendar:" in str(basis) and "calendar:" in pubc)
        if not okp:
            pub_bad.append((sid, lab, pd, mine, basis))
        ctx.add("K%02d.p" % n, "①", "席位发布日重建(日历条目优先/报告自述规则兜底): %s" % basis, mine,
                "%s@%s 发布 %s" % (sid, lab, pd), okp and pd <= C.CUTOFF)
        ctx.add("K%02d.lag" % n, "①", "发布日−观测月/季期末的滞后天数(括注为规则原文)", C.days_between(C.month_end(vis[0][:7]), mine),
                "括注 %s" % re.sub(r"^\S+\(", "", pubc)[:60], mine is not None and pd is not None and mine <= C.CUTOFF,
                note="只核发布日≤截止日")
    mt = table_by_header(ctx, ["地区", "维度", "指标(口径)"])
    nm = 0
    for r in mt["rows"]:
        sid = None
        for kw, s in MAP_ROW_SID:
            if r[2].startswith(kw):
                sid = s
                break
        if sid is None:
            continue
        for lab, cell in zip(["12个月前", "3个月前", "最新一期"], r[3:6]):
            nm += 1
            anchor = C.ANCHOR_DATE[lab]
            vis = ctx.visible(sid, anchor)
            where = "MAP 地图表 %s %s" % (sid, lab)
            if cell.startswith("数据不可得"):
                ctx.add("M%02d" % nm, "②⑬", "series_store.%s 发布日≤%s 的可见观测" % (sid, anchor),
                        "可见观测=%s" % ("无" if vis is None else vis[0]), "%s=%s" % (where, cell), vis is None)
                continue
            obsm = re.search(r"观测(\d{4}-\d{2})", cell)
            okd = vis is not None and bool(obsm) and vis[0][:7] == obsm.group(1)
            stale = "⚠过期" in cell
            lagm = re.search(r"滞后(\d+)天", cell)
            oks = (not stale) or (bool(lagm) and vis is not None and C.days_between(vis[0], C.CUTOFF) == int(lagm.group(1)))
            ctx.add("M%02d" % nm, "②⑬", "series_store.%s 发布日≤%s 的最新观测(值/观测月/过期标注)" % (sid, anchor),
                    "无" if vis is None else "%.6g@%s" % (vis[1], vis[0]), "%s=%s" % (where, cell.split("(同比")[0][:48]),
                    vis is not None and same_round(vis[1], cell) and okd and oks)
            if vis is not None and (sid in LEVEL_YOY or "同比" in cell):
                yoy_cell_ok(ctx, sid, vis, cell, "M%02d" % nm, where)
    ctx.note("②", "关键数字表 %d 行逐格值/观测日/发布日; 地图表 %d 格交叉核对(含同比括注); 发布日不一致行=%s" % (n, nm, pub_bad))
    cv = table_by_header(ctx, ["地区×维度", "指标", "12个月前", "3个月前", "最新一期"])
    rows = cv["rows"]
    groups = sorted({r[0] for r in rows})
    gok = [len({r[0] for r in rows if r[i] in ("ok", "⚠过期")}) for i in (2, 3, 4)]
    ctx.add("Mcov", "⑬", "MAP L49-72 逐组覆盖表按组计数(ok/⚠过期=在场)", "组级在场=%s / 组数=%d" % (gok, len(groups)), "L42: 12/12组ok ×3",
            len(groups) == 12 and all(x == 12 for x in gok))
    regions = sorted({g.split("×")[0] for g in groups})
    dims = sorted({g.split("×")[1] for g in groups})
    ctx.add("Mgrp", "⑬", "MAP L49-72 地区×维度集合", "%s / %s / %d组" % (regions, dims, len(groups)), "四地×三维=12组",
            len(groups) == 12 and regions == ["CN", "EA", "JP", "US"] and dims == ["growth", "inflation", "policy"])
    k = 0
    for r in rows:
        sid = None
        for kw, s in MAP_ROW_SID:
            if r[1].startswith(kw):
                sid = s
                break
        if sid is None:
            continue
        k += 1
        vis = ctx.visible(sid, C.CUTOFF)
        pd = first_date(r[6])
        ok = (vis is not None and ((vis[2] == pd) or ("calendar:" in str(vis[3]) and "calendar:" in r[6]))) or (
            vis is None and r[4] == "不可得")
        ctx.add("Cov%02d.pub" % k, "⑬", "series_store.%s 最新可见观测的发布日(席位重建)" % sid, "无" if vis is None else vis[2],
                "覆盖表 %s 发布日期 %s" % (r[1][:16], r[6][:40]), ok)
        if r[5] != "—" and vis is not None:
            end = C.month_end(C.L.shift_months(vis[0], 2)[:7]) if sid in C.RULE_Q_LAG else C.month_end(vis[0][:7])
            ctx.add("Cov%02d.end" % k, "⑬", "series_store.%s 最新可见观测期(月频=月末/季频=季末)的期末" % sid, end,
                    "覆盖表 统计期末 %s" % r[5], end == r[5])
        st = r[4]
        lag = None if vis is None else C.days_between(vis[0], C.CUTOFF)
        nxt = None if vis is None else L.first_on_or_after(ctx.ser(sid), C.add_days(vis[0], 1))
        nxt_pub = None if nxt is None else ctx.pub(sid, nxt[0])[0]
        hidden = bool(nxt) and nxt_pub is not None and nxt_pub <= C.CUTOFF      # newer obs that should be visible
        daily = sid in ("CN_OMO_7D", "CN_POLICY_OVERNIGHT")
        stale = daily and vis is not None and lag is not None and lag > 10
        ctx.add("Cov%02d.st" % k, "⑬", "series_store.%s 最新可见观测; 其后观测的发布日 vs 截止日(应可见而未用=藏数); 日频政策序列滞后>10天=过期" % sid,
                "无观测" if vis is None else ("滞后%d天; 其后观测发布日=%s" % (lag, nxt_pub)),
                "覆盖表 最新一期=%s" % st,
                (st == "不可得" and vis is None) or (st in ("ok", "⚠过期") and vis is not None and not hidden and (st == "⚠过期") == stale),
                note="其后观测应可见而未用" if hidden else "")
    body = "\n".join(ctx.map_lines)
    ctx.add("Msub", "⑬", "MAP 结构: 五个子问句各有对应节", "环境表/三转折/传导+对质/历史类比+同步面/随后3-6-12月", "问句五问(L3)逐一有答",
            all(k in body for k in ("## 四地三时点环境对照", "## 过去一年的三个转折", "## 证据最充分的传导机制", "## 主解释 vs 竞争解释",
                                    "## 历史上结构最像的时期", "随后3个月", "随后6个月", "随后12个月")))


# --------------------------------------------------------------------------- ③
def run_yoy(ctx):
    kt = table_by_header(ctx, ["指标", "锚", "值", "单位", "实际观测日"])
    n = 0
    for r in kt["rows"]:
        sid, lab = r[0], r[1]
        if sid not in LEVEL_YOY:
            continue
        anchor = C.ANCHOR_DATE[lab]
        vis = ctx.visible(sid, anchor)
        if vis is None:
            continue
        n += 1
        yy, bd, bv = ctx.yoy(sid, vis[0])
        if yy is None:
            ctx.add("Y%02d" % n, "③", "series_store.%s 基期观测@%s 是否在场" % (sid, bd), bv,
                    "%s@%s 同比不可得(缺基期)" % (sid, lab), bv is None, note="基期缺席=如实标注缺基期, 未给同比")
        else:
            ctx.add("Y%02d" % n, "③", "series_store.%s[%s]/[%s]-1 (去年同月基期值=%s)" % (sid, vis[0], bd, bv), yy,
                    "%s@%s 同比可算(地图表括注另核)" % (sid, lab), True)
    for sid, a, b, ra, rb, tag in (("CPI", "2026-02-01", "2026-05-01", 2.434, 4.1666, "L191/L246"),
                                   ("INDPRO", "2025-11-01", "2026-02-01", 1.7543, 0.7972, "L235/L251"),
                                   ("CORE_CPI", "2026-05-01", "2026-08-01", 2.8229, 2.4462, "L252")):
        ya, ba, _ = ctx.yoy(sid, a)
        yb, bb, _ = ctx.yoy(sid, b)
        ctx.add("Yt.%s.%s" % (sid, b[:7]), "③", "series_store.%s 同比@%s / @%s" % (sid, a[:7], b[:7]), "%s→%s" % (ya, yb),
                "%s: %s→%s" % (tag, ra, rb), C.close(ya, ra, 4) and C.close(yb, rb, 4))
    ctx.add("Yt.ind.oct", "③", "series_store.INDPRO 同比@2026-10-01", ctx.yoy("INDPRO", "2026-10-01")[0], "L235: 其后2026-10同比回到2.15",
            C.close(ctx.yoy("INDPRO", "2026-10-01")[0], 2.15, 2))
    ctx.note("③", "锚点同比点 %d 个 + 文中转折窗同比 4 点 + 地图表同比括注(计入②)" % n)


# --------------------------------------------------------------------------- ④
def latest_change(p, upto):
    ch = L.changes_in_window(p, "2000-01-01", upto)
    return ch[-1] if ch else None


def run_policy(ctx):
    txt = ctx.map_lines
    n = 0
    for i, ln in enumerate(txt):
        if not ln.startswith("- **政策一年窗路径**"):
            continue
        n += 1
        m = re.match(r"- \*\*政策一年窗路径\*\* (.+?): 窗 (\S+)\.\.(\S+),变动点 (.*?),净变动 \*\*([+-]\d+)bp\*\*\(([\d.]+)→([\d.]+)\)", ln)
        name, w0, w1, ev, net, n0, n1 = m.groups()
        sid = NAME_SID[name]
        p = ctx.ser(sid)
        evs = [] if ev == "窗内无变动" else re.findall(r"(\d{4}-\d{2}-\d{2}): ([\d.]+)→([\d.]+)\(([+-]\d+)bp\)", ev)
        mine_all = L.changes_in_window(p, w0, w1)
        mine = [c for c in mine_all if abs(c[2] - c[1]) * 100 >= 1.0] if sid == "JP_POLICY_RATE" else mine_all
        oklist = (len(evs) == len(mine)) and all(
            e[0] == mm[0] and C.close(float(e[1]), mm[1], 6) and C.close(float(e[2]), mm[2], 6)
            and int(e[3]) == round((mm[2] - mm[1]) * 100) for e, mm in zip(evs, mine))
        ctx.add("P%02d.ev" % n, "④", "series_store.%s 窗[%s..%s] 内观测对其前值的变动点" % (sid, w0, w1),
                ";".join("%s:%s→%s" % (a, b, c) for a, b, c in mine) or "无", "MAP L%d 变动点 %s" % (i + 1, ev), oklist)
        fin = L.first_on_or_after(p, w0)
        las = L.last_on_or_before(p, w1)
        net_engine = round((las[1] - fin[1]) * 100)
        start_eff = ctx.lob(sid, w0)
        if start_eff is None:
            # series has no observation at window start (new anchor series): only the engine basis exists
            net_effect = net_engine
            start_txt = "窗启日无观测(序列自 %s 起)" % fin[0]
        else:
            net_effect = round((las[1] - start_eff[1]) * 100)
            start_txt = str(start_eff)
        net_rep = int(net)
        ev_sum = sum(int(e[3]) for e in evs)
        ok = (net_rep == net_effect) or (net_rep == net_engine and net_engine == net_effect)
        ctx.add("P%02d.net" % n, "④", "series_store.%s 窗首在值 %s→窗末 %s; 同句变动点合计=%+dbp" % (sid, start_txt, las, ev_sum),
                net_effect, "MAP L%d 净变动 %s bp(%s→%s)" % (i + 1, net, n0, n1), ok,
                note="引擎口径(窗内首个观测→窗末)=%+d; 窗首在值口径=%+d; 变动点合计=%+d" % (net_engine, net_effect, ev_sum)
                if (net_engine != net_effect or ev_sum != net_rep) else "")
        ctx.add("P%02d.win" % n, "④", "研究截止−12月 / 研究截止", "%s..%s" % ("2025-11-23", C.CUTOFF), "窗 %s..%s" % (w0, w1),
                w1 == C.CUTOFF and w0 == "2025-11-23")
    k = 0
    for ln in txt:
        m = re.match(r"\s*- 事件 (\d{4}-\d{2}-\d{2})\(生效\): 决议日 (\d{4}-\d{2}-\d{2})→生效日 (\d{4}-\d{2}-\d{2})", ln)
        if not m:
            continue
        k += 1
        eff, dec, eff2 = m.groups()
        conv = C.add_days(eff, -6) if datetime.date.fromisoformat(eff).weekday() == 2 else C.add_days(eff, -1)
        wd = datetime.date.fromisoformat(dec).weekday()
        ctx.add("PE%02d" % k, "④", "序列值变更日(生效)按惯例回推决议日: ECB=生效前上一个周四(−6天)/Fed=前一日", conv,
                "事件 %s 生效: 决议 %s" % (eff, dec), eff == eff2 and conv == dec and ((wd == 3) == (conv == C.add_days(eff, -6))))
    ot = table_by_header(ctx, ["地区", "官方目标", "待生效", "最近决议日", "生效日", "最近确认维持", "核验覆盖截止", "距上次调整(按生效日)", "距决议", "距维持", "溯源"])
    k = 0
    for r in ot["rows"]:
        k += 1
        region = r[0]
        eff = first_date(r[4])
        dec = first_date(r[3])
        mnt = first_date(r[5])
        cov = first_date(r[6])
        d_eff = C.days_between(eff, C.CUTOFF)
        d_dec = C.days_between(dec, C.CUTOFF)
        d_mnt = None if mnt is None else C.days_between(mnt, C.CUTOFF)
        got = (r[7], r[8], r[9])
        exp = ("%d天" % d_eff, "%d天" % d_dec, "—" if d_mnt is None else "%d天" % d_mnt)
        ctx.add("O%02d.d" % k, "④", "截止日 2026-11-23 − 生效/决议/维持日", "/".join(exp), "%s %s (MAP L117 官方记录面)" % (region, "/".join(got)),
                tuple(got) == exp)
        if region == "日本":
            ent = [e for e in ctx.cal["entries"] if e.get("entry_id") == "RC-JP-BOJ-TARGET-2026-09"][0]
            ctx.add("O%02d.c" % k, "④", "release_calendar.entries[RC-JP-BOJ-TARGET-2026-09].decision_date/effective_on/target_value",
                    "%s/%s/%s" % (ent["decision_date"], ent["effective_on"], ent["target_value"]),
                    "%s 决议 %s 生效 %s 目标 %s" % (region, dec, eff, first_num(r[1])),
                    ent["decision_date"] == dec and ent["effective_on"] == eff and C.close(ent["target_value"], first_num(r[1]), 2))
            ent2 = [e for e in ctx.cal["entries"] if e.get("entry_id") == "RC-JP-BOJ-MAINT-2026-10"][0]
            ctx.add("O%02d.m" % k, "④", "release_calendar.entries[RC-JP-BOJ-MAINT-2026-10].decision_date(=核验覆盖截止)", ent2["decision_date"],
                    "%s 最近确认维持 %s / 核验覆盖截止 %s" % (region, mnt, cov), ent2["decision_date"] == mnt == cov)
            ctx.add("O%02d.t" % k, "④", "series_store.JP_POLICY_RATE@2026-10-01 (月均口径) vs 日历条目 target_value(宣布值口径)",
                    "月均=%s / 目标=%s" % (ctx.exact("JP_POLICY_RATE", "2026-10-01"), ent["target_value"]),
                    "官方目标 1.25 与 月均 1.227 两口径分列(不互冒充)",
                    C.close(ent["target_value"], 1.25, 2) and C.close(ctx.exact("JP_POLICY_RATE", "2026-10-01"), 1.227, 3))
            pend = [e for e in ctx.cal["entries"] if e.get("effective_on") and e["effective_on"] > C.CUTOFF]
            ctx.add("O%02d.pend" % k, "④", "release_calendar 中生效日>截止日的条目数", len(pend), "待生效列=—", len(pend) == 0 and r[2] == "—")
    policy_dates(ctx)
    for region, dec, eff, gap in [("ECB", "2026-06-11", "2026-06-17", 6), ("ECB", "2026-09-10", "2026-09-16", 6),
                                  ("US", "2025-12-10", "2025-12-11", 1), ("US", "2026-09-16", "2026-09-17", 1), ("JP", "2026-09-18", "2026-09-24", 6)]:
        wd = datetime.date.fromisoformat(dec).weekday()
        sid = "ECB_DFR" if region == "ECB" else ("DFEDTARU" if region == "US" else None)
        ch = None if sid is None else [c for c in L.changes_in_window(ctx.ser(sid), "2025-01-01", C.CUTOFF) if c[0] == eff]
        ctx.add("PD.%s.%s" % (region, eff), "④", "决议日→生效日 间隔; 序列值变更日=生效日", "间隔%d天; 变更点=%s" % (
            C.days_between(dec, eff), ch[0][1:] if ch else ("日历条目" if sid is None else "无")),
            "%s 决议 %s 生效 %s" % (region, dec, eff), C.days_between(dec, eff) == gap and (sid is None or bool(ch))
            and (region != "ECB" or wd == 3))
    ctx.add("PD.dff", "④", "series_store.DFF@2026-09-16/2026-09-17", "%s→%s" % (ctx.exact("DFF", "2026-09-16"), ctx.exact("DFF", "2026-09-17")),
            "L104: 生效日 DFF 同日跳变 2026-09-17 3.63→3.88",
            C.close(ctx.exact("DFF", "2026-09-16"), 3.63, 2) and C.close(ctx.exact("DFF", "2026-09-17"), 3.88, 2))
    cl = table_by_header(ctx, ["簇", "决议日区间", "地区", "事件(决议→生效,Δbp)", "跨国同一事件"])
    got = [(r[0], r[1], r[2], r[4]) for r in cl["rows"]]
    exp = [("POLCLUSTER-01", "2025-12-10..2025-12-10", "US", "否"), ("POLCLUSTER-02", "2026-06-11..2026-06-11", "EA", "否"),
           ("POLCLUSTER-03", "2026-09-10..2026-09-16", "EA/US", "是")]
    ctx.add("PCL", "④", "决议日(序列变更日按惯例回推)±7日聚簇", "/".join("%s|%s|%s|%s" % e for e in exp),
            "/".join("%s|%s|%s|%s" % g for g in got), got == exp)
    ctx.add("PCL.gap", "④", "2026-09-10 与 2026-09-16 相隔天数", C.days_between("2026-09-10", "2026-09-16"), "同簇(±7日)=是",
            C.days_between("2026-09-10", "2026-09-16") <= 7)
    omo = ctx.val("CN_OMO_7D", "2026-10-30")
    on = ctx.val("CN_POLICY_OVERNIGHT", "2026-11-23")
    lpr = [ctx.val("CN_LPR_1Y", a) for a in ("2025-11-23", "2026-08-23", "2026-11-23")]
    ctx.add("PCN.hold", "④", "series_store.CN_LPR_1Y/CN_OMO_7D 三锚与窗内变更点", "LPR=%s; OMO_7D末值=%s; 窗内变更点=%d/%d" % (
        lpr, omo, len(L.changes_in_window(ctx.ser("CN_LPR_1Y"), "2025-11-23", "2026-11-23")),
        len(L.changes_in_window(ctx.ser("CN_OMO_7D"), "2025-11-23", "2026-11-23"))),
        "L11/L180 中国按兵不动(7天逆回购1.4与LPR 3.0全年无变动)", lpr == [3.0, 3.0, 3.0] and C.close(omo, 1.4, 2))
    po = ctx.ser("CN_POLICY_OVERNIGHT")
    ctx.add("PCN.anchor", "④", "series_store.CN_POLICY_OVERNIGHT 首/末观测", "首=%s 末=%s" % (po[0], po[-1]),
            "L23/L180/L234: 2026-11-02 换锚, 最新 1.25@2026-11-23", po[0][0] == "2026-11-02" and C.close(on, 1.25, 2),
            note="换锚前操作目标=7天期 1.40; 换锚后=隔夜 1.25")
    ctx.add("PCN.anchor.level", "④", "series_store.CN_OMO_7D 末值 vs CN_POLICY_OVERNIGHT 末值(换锚前后政策利率锚水平)",
            "1.40→%s" % on, "『政策利率全年按兵不动』", not C.close(omo, on, 2),
            note="两锚水平不同(1.40 vs 1.25)=『按兵不动』表述须限定口径")
    txt_all = "\n".join(txt)
    evs = re.findall(r"\| (美联储目标区间上限\(DFEDTARU\)|欧央行主要再融资利率\(ECB_MRO\)|欧央行存款便利利率\(ECB_DFR\)|中国LPR\(1年\)\(CN_LPR_1Y\)) \| (\d{4}-\d{2}) \| ([\d.]+)→([\d.]+)\(事后政策事件\) \| (\d{4}-\d{2}-\d{2}) \|", txt_all)
    sidmap = {"美联储目标区间上限(DFEDTARU)": "DFEDTARU", "欧央行主要再融资利率(ECB_MRO)": "ECB_MRO",
              "欧央行存款便利利率(ECB_DFR)": "ECB_DFR", "中国LPR(1年)(CN_LPR_1Y)": "CN_LPR_1Y"}
    k = 0
    for nm, ym, a, b, d in evs:
        k += 1
        sid = sidmap[nm]
        ch = [c for c in L.changes_in_window(ctx.ser(sid), "2021-01-01", C.CUTOFF) if c[0] == d]
        ctx.add("PX%02d" % k, "④", "series_store.%s 值变更@%s" % (sid, d), ch[0][1:] if ch else "无变更点",
                "历史段事后政策事件 %s %s: %s→%s" % (ym, d, a, b),
                bool(ch) and C.close(ch[0][1], float(a), 6) and C.close(ch[0][2], float(b), 6) and d <= C.CUTOFF)
    tok8 = ctx.exact("JP_CPI_TOKYO_YOY", "2026-08-01")
    tok9 = ctx.exact("JP_CPI_TOKYO_YOY", "2026-09-01")
    pub9, b9 = ctx.pub("JP_CPI_TOKYO_YOY", "2026-09-01")
    pub8, b8 = ctx.pub("JP_CPI_TOKYO_YOY", "2026-08-01")
    ctx.add("PJP.tok", "④", "series_store.JP_CPI_TOKYO_YOY@2026-08/2026-09 + 席位发布日重建(%s/%s)" % (b8, b9),
            "2026-08=%s(发 %s); 2026-09=%s(发 %s)" % (tok8, pub8, tok9, pub9),
            "L236: 当时可见最近东京读数 2026-08=1.9(推定发布 2026-08-30); 2026-09 值 2.69 推定首发 2026-09-29 晚于决议 2026-09-18",
            C.close(tok8, 1.9, 2) and C.close(tok9, 2.69, 2) and pub8 == "2026-08-30" and pub9 == "2026-09-29" and pub9 > "2026-09-18")
    doc = table_by_header(ctx, ["文档", "发布日", "口径"])
    r = doc["rows"][0]
    ent = [e for e in ctx.cal["entries"] if "FOMC-MINUTES-2026-10" in json_of(e)]
    ctx.add("PDOC", "④", "release_calendar 纪要条目发布日(检索条目含 FOMC-MINUTES-2026-10)",
            (ent[0].get("first_publish_on_or_after") or ent[0].get("published_on")) if ent else "无条目",
            "FOMC 10月纪要发布 %s" % first_date(r[1]),
            first_date(r[1]) == "2026-11-18" and "2026-11-18" <= C.CUTOFF
            and (not ent or (ent[0].get("first_publish_on_or_after") or ent[0].get("published_on")) == "2026-11-18"))


def json_of(e):
    import json
    return json.dumps(e, ensure_ascii=False)


def policy_dates(ctx):
    pt = table_by_header(ctx, ["地区", "指标", "口径", "锚", "值", "决议/公布日", "生效日", "市场观测日", "统计窗口结束日"])
    k = 0
    for r in pt["rows"]:
        k += 1
        name, lab, val, dec, eff, mkt, win = r[1], r[3], r[4], r[5], r[6], r[7], r[8]
        sid = NAME_SID[name]
        anchor = C.ANCHOR_DATE[lab]
        vis = ctx.visible(sid, anchor)
        ctx.add("PDt%02d.v" % k, "④", "series_store.%s 发布日≤%s 最新可见观测" % (sid, anchor), vis[1],
                "四分面 %s %s=%s" % (name[:12], lab, val), C.close(vis[1], float(val), ndec(val)))
        p = ctx.ser(sid)
        if sid in ("ECB_DFR", "ECB_MRO"):
            eff_exp, dec_exp = vis[0], C.add_days(vis[0], -6)      # 生效=序列变更日; 决议=生效前上一个周四
        elif sid in ("CN_LPR_1Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT"):
            eff_exp, dec_exp = vis[0], vis[0]                        # 公布即时生效
        elif sid == "DFEDTARU":
            ch = latest_change(p, anchor)
            eff_exp, dec_exp = ch[0], C.add_days(ch[0], -1)          # 决议=生效前一日
        elif sid == "DFF":
            eff_exp, dec_exp = vis[0], None                          # 市场均值: 生效=观测日, 无决议日
        else:
            eff_exp, dec_exp = None, None
        pd_, pe = first_date(dec), first_date(eff)
        ctx.add("PDt%02d.dec" % k, "④", "series_store.%s 在值决议的序列变更日按惯例回推(或观测日本身)" % sid, dec_exp,
                "四分面 %s 决议/公布日 %s" % (lab, (dec or "—")[:10]), (pd_ is None and dec_exp is None) or (pd_ == dec_exp))
        ctx.add("PDt%02d.eff" % k, "④", "series_store.%s 在值决议的生效日(序列值变更日)" % sid, eff_exp,
                "四分面 %s 生效日 %s" % (lab, (eff or "—")[:10]), (pe is None and eff_exp is None) or (pe == eff_exp))
        for cell, lbl in ((eff, "生效"), (dec, "决议")):
            mm = re.search(r"距研究截止(\d+)天", cell)
            if mm:
                ctx.add("PDt%02d.%s" % (k, lbl), "④", "截止日−%s日" % lbl, C.days_between(first_date(cell), C.CUTOFF),
                        "四分面 %s 距研究截止%s天" % (lbl, mm.group(1)), int(mm.group(1)) == C.days_between(first_date(cell), C.CUTOFF))
        if sid == "DFEDTARU":
            dv = ctx.visible("DFF", anchor)
            pm = first_date(mkt)
            ctx.add("PDt%02d.mkt" % k, "④", "series_store.DFF 发布日≤%s 最新可见观测日(配对市场序列)" % anchor, dv[0],
                    "四分面 DFEDTARU %s 市场观测日 %s" % (lab, pm), pm == dv[0],
                    note="报告自称『市场观测=配对 DFF 同窗观测日』; DFF 行自身打印 %s" % dv[0])
        if sid == "DFF":
            ctx.add("PDt%02d.mkt" % k, "④", "series_store.DFF 最新可见观测日", vis[0],
                    "DFF 行 市场观测/生效/窗口结束 %s/%s/%s" % (first_date(mkt), first_date(eff), first_date(win)),
                    first_date(mkt) == first_date(eff) == first_date(win) == vis[0])
        if sid == "JP_POLICY_RATE":
            ctx.add("PDt%02d.win" % k, "④", "series_store.JP_POLICY_RATE 观测月月末", C.month_end(vis[0][:7]), "统计窗口结束日 %s" % win,
                    win == C.month_end(vis[0][:7]) and dec.startswith("—") and eff.startswith("—"))
        if sid == "CN_POLICY_OVERNIGHT":
            ctx.add("PDt%02d.dr" % k, "④", "series_store 是否含隔夜市场利率(DR001类)序列",
                    [s for s in ctx.snap["series_store"] if "DR001" in s], "市场观测日=隔夜市场利率未入库如实缺席",
                    not [s for s in ctx.snap["series_store"] if "DR001" in s])
