#!/usr/bin/env python3
"""Recompute ⑧ historical analog sections (distance/percentile/contributions/gaps, region×dimension sync face,
known-then vs ex-post split, aftermath 3/6/12m as 事后实际, per-window tables) — read-only."""
import re
import sys

sys.path.insert(0, "/tmp/r32-accept/review/A_round1")
import rc_common as C  # noqa: E402
from rc_a import first_date, ndec, table_by_header  # noqa: E402

L = C.L
POLICY_SIDS = {"DFEDTARU", "ECB_MRO", "ECB_DFR", "JP_POLICY_RATE", "CN_LPR_1Y", "DFF"}
MONTHLY_SIDS = {"UNEMPLOYMENT", "CPI", "INDPRO", "CORE_PCE", "CORE_CPI"}
PP_AFTERMATH = {"DFEDTARU", "UNEMPLOYMENT", "UST_10Y"}
DIM_SHARE_CN = {"波动": "volatility", "利率": "rates", "通胀": "inflation", "估值": "valuation", "增长": "growth", "信用": "credit"}
REG = {"US": "US", "CN": "CN", "EA": "EA", "JP": "JP"}
SIDE = {"候选期高于当前": -1, "当前高于候选期": 1}


def sections(ctx):
    out, cur = [], None
    for i, l in enumerate(ctx.map_lines):
        m = re.match(r"^### (\d{4}-\d{2})\(距离([\d.]+),TOP-5独立簇第(\d+),分位([\d.]+),(\d+)个有效候选\)", l)
        if m:
            cur = {"ym": m.group(1), "dist": m.group(2), "rank": int(m.group(3)), "pct": m.group(4), "nvalid": int(m.group(5)), "line": i + 1, "lines": []}
            out.append(cur)
        elif cur is not None and (l.startswith("### ") or l.startswith("## ")):
            cur = None
        elif cur is not None:
            cur["lines"].append(l)
    return out


def hist_pub(ctx, sid, obs):
    """historical-section publication rule: calendar entry first; EA_HICP flash at month-end; else report rule"""
    if sid == "EA_HICP_YOY":
        hits = ctx.cal_entries(sid, obs)
        if hits:
            hits.sort(key=lambda e: e.get("first_publish_on_or_after") or "9999")
            return hits[0].get("first_publish_on_or_after"), "calendar"
        return C.month_end(obs[:7]), "rule:flash_month_end"
    return ctx.pub(sid, obs)


def hist_vis(ctx, sid, when):
    best = None
    for d, v in ctx.ser(sid):
        if v is None or d > when:
            continue
        p, b = hist_pub(ctx, sid, d)
        if p is not None and p <= when:
            best = (d, v, p, b)
    return best


def gdp_yoy(ctx, obs):
    a, b = ctx.exact("US_REAL_GDP", obs), ctx.exact("US_REAL_GDP", L.shift_months(obs, -12))
    return None if a is None or b is None else (a / b - 1) * 100


def sync_val(ctx, sid, vis):
    if sid == "US_REAL_GDP":
        return gdp_yoy(ctx, vis[0])
    if sid == "CPI":
        return ctx.yoy("CPI", vis[0])[0]
    return vis[1]


def direction(x):
    return "上行" if x > 1e-9 else "下行" if x < -1e-9 else "持平"


def me_val(ctx, sid, ym):
    return ctx.exact(sid, ym + "-01") if sid in MONTHLY_SIDS else (ctx.lob(sid, C.month_end(ym)) or (None, None))[1]


def num(s):
    return float(s.replace("−", "-").replace("pp", "").replace("%", ""))


def run_analog(ctx):
    s6 = ctx.steps["S6_analog"]["envelope"]["data"]
    top = {t["rank"]: t for t in s6["top"]}
    cands = s6["candidates"]
    cov = {k: v.get("coverage") for k, v in s6["state_vector"].items()}
    agree = (s6.get("dispersion") or {}).get("topN_aftermath_sign_agreement") or {}
    secs = sections(ctx)
    ctx.add("H.n", "⑧", "MAP_REPORT.md 历史段 ### 标题数", len(secs), "≤3段", 1 <= len(secs) <= 3)
    ctx.add("H.valid", "⑧", "report.steps[S6_analog].envelope.data.candidates.valid / scanned", "%s/%s" % (cands.get("valid"), cands.get("scanned")), "各段标题『74个有效候选』",
            all(s["nvalid"] == cands.get("valid") for s in secs))
    hy_months_cache = {}
    for n, sec in enumerate(secs):
        tag = "H%d" % (n + 1)
        lines = sec["lines"]
        text = "\n".join(lines)
        t = top.get(sec["rank"])
        if t is None or t.get("candidate_month") != sec["ym"]:
            ctx.add("%s.hdr" % tag, "⑧", "report.steps[S6_analog].envelope.data.top[rank=%s]" % sec["rank"], None, "标题 %s 第%s" % (sec["ym"], sec["rank"]), False)
            continue
        cutoff_me = C.month_end(sec["ym"])
        ctx.add("%s.hdr" % tag, "⑧", "S6.top[rank=%s].candidate_month/distance/distance_percentile" % sec["rank"],
                "%s/%s/%s" % (t["candidate_month"], round(t["distance"], 4), round(t["distance_percentile"], 2)),
                "标题 %s(距离%s,TOP-5独立簇第%s,分位%s)" % (sec["ym"], sec["dist"], sec["rank"], sec["pct"]),
                C.close(t["distance"], float(sec["dist"]), 4) and C.close(t["distance_percentile"], float(sec["pct"]), 2))
        ctx.add("%s.rank" % tag, "⑧", "S6.top 排序(按 distance 升序)与各段名次", [x["rank"] for x in sorted(s6["top"], key=lambda x: x["distance"])],
                "第%s(独立簇代表)" % sec["rank"], [x["rank"] for x in sorted(s6["top"], key=lambda x: x["distance"])] == [x["rank"] for x in s6["top"]])
        mw = re.search(r"匹配区间: (\d{4}-\d{2})\.\.(\d{4}-\d{2})\(判断截止月 (\d{4}-\d{2})", text)
        fw = s6.get("feature_window_months")
        ctx.add("%s.win" % tag, "⑧", "匹配窗=候选月向前 feature_window_months(%s) 个月" % fw, "%s..%s" % (L.shift_months(sec["ym"] + "-01", -(fw - 1))[:7], sec["ym"]),
                "匹配区间 %s..%s(判断截止月 %s)" % mw.groups(), mw.group(1) == L.shift_months(sec["ym"] + "-01", -(fw - 1))[:7] and mw.group(2) == mw.group(3) == sec["ym"])
        # contributions
        sim = next((l for l in lines if l.startswith("- 相似点")), "")
        pairs = [(re.sub(r"[^\u4e00-\u9fff]", "", k), v) for k, v in re.findall(r"(\S+?)([\d.]+)%", sim.split("贡献维=")[1].split("——")[0])] if "贡献维=" in sim else []
        shares = {DIM_SHARE_CN.get(k, k): float(v) for k, v in pairs}
        eng = {k: round(v.get("contribution_share", 0) * 100, 1) for k, v in t["dims"].items()}
        eng_pos = {k: v for k, v in eng.items() if v > 0}
        ctx.add("%s.share" % tag, "⑧", "S6.top[rank].dims.*.contribution_share×100 (仅>0 维, 降序)", sorted(eng_pos.items(), key=lambda x: -x[1]), "贡献维 %s" % sim.split("贡献维=")[1][:60] if "贡献维=" in sim else "",
                shares == eng_pos and [DIM_SHARE_CN.get(k, k) for k, _ in pairs] == [k for k, _ in sorted(eng_pos.items(), key=lambda x: -x[1])])
        ctx.add("%s.share.order" % tag, "⑧", "贡献维文字顺序=份额降序", [k for k, _ in sorted(eng_pos.items(), key=lambda x: -x[1])], "贡献维文字 %s" % [k for k, _ in pairs],
                [DIM_SHARE_CN.get(k, k) for k, _ in pairs] == [k for k, _ in sorted(eng_pos.items(), key=lambda x: -x[1])])
        sim2 = re.search(r"距离([\d.]+)\(分位([\d.]+)\)|距离([\d.]+)为\d+个有效候选中最近\(分位([\d.]+)\)", sim)
        ctx.add("%s.sim.dist" % tag, "⑧", "S6.top[rank].distance / distance_percentile", "%s / %s" % (round(t["distance"], 4), round(t["distance_percentile"], 2)), "相似点行 %s" % sim[6:60],
                bool(sim2) and C.close(t["distance"], float(sim2.group(1) or sim2.group(3)), 4) and C.close(t["distance_percentile"], float(sim2.group(2) or sim2.group(4)), 2))
        # gaps > 1 sigma
        dif = next((l for l in lines if l.startswith("- 关键差异")), "")
        gp = re.findall(r"([A-Z][A-Z0-9_]*)([^,()]*?)\((候选期高于当前|当前高于候选期),([+-]\d+\.\d+)\)", dif)
        feats = t["features_detail"]
        big = {k: round(v.get("gap"), 2) for k, v in feats.items() if abs(v.get("gap") or 0) > 1}
        matched, ok_all = [], True
        for met, desc, side, val in gp:
            v = float(val)
            cands_k = [k for k, fv in feats.items() if k.startswith(met) and round(fv.get("gap"), 2) == v]
            ok = bool(cands_k) and (SIDE[side] == (1 if v > 0 else -1)) and any(k in big for k in cands_k)
            ok_all = ok_all and ok
            matched += [k for k in cands_k if k in big]
        ctx.add("%s.gaps" % tag, "⑧", "S6.top[rank].features_detail.*.gap (|gap|>1 全集)", big, "关键差异行逐维点名 %d 项" % len(gp),
                ok_all and sorted(set(matched)) == sorted(big) and len(matched) == len(big), note="点名项数=%d, 引擎|gap|>1项数=%d" % (len(gp), len(big)))
        hym = re.search(r"HY序列历史(\d+)个月<36", dif)
        hy_n = len({d[:7] for d, v in ctx.ser("HY_OAS") if v is not None and d <= cutoff_me}) if ctx.has("HY_OAS") else 0
        ctx.add("%s.hy" % tag, "⑧", "series_store.HY_OAS 至候选月末的历史月数", hy_n, "关键差异行信用维注记 %s" % (hym.group(0) if hym else ("无HY观测" if "无HY观测" in dif else "无")),
                (int(hym.group(1)) == hy_n) if hym else (("无HY观测" in dif) and hy_n == 0), note="缺失特征=%s" % (t.get("missing_features") or {}))
        # ---- sync narrative + table
        sync_t = table_by_header_ctx(lines, ["维度", "地区", "指标", "锚−3月(观测/公布)", "截止(观测/公布)", "读数变化", "同步性"])
        when0, when1 = C.month_end(L.shift_months(sec["ym"] + "-01", -3)[:7]), cutoff_me
        us_dir = {}
        row_label = {}
        k = 0
        for r in sync_t["rows"]:
            k += 1
            dim, reg, cell0, cell1, chg_cell, label = r[0], r[1], r[3], r[4], r[5], r[6]
            sid = re.search(r"\(([A-Z0-9_]+)\)\s*$", r[2]).group(1)
            m0 = re.search(r"(-?[\d.]+) @ (\d{4}-\d{2}-\d{2})\(公布 (\d{4}-\d{2}-\d{2})\)", cell0)
            m1 = re.search(r"(-?[\d.]+) @ (\d{4}-\d{2}-\d{2})\(公布 (\d{4}-\d{2}-\d{2})\)", cell1)
            v0, v1 = hist_vis(ctx, sid, when0), hist_vis(ctx, sid, when1)
            if v0 is None or v1 is None or m0 is None or m1 is None:
                ctx.add("%s.S%02d.vis" % (tag, k), "⑧", "series_store.%s 在 %s / %s 的当时可知观测" % (sid, when0, when1), "%s / %s" % (bool(v0), bool(v1)),
                        "同步面行 %s %s %s" % (dim, reg, sid), (v0 is None and v1 is None and "缺证" in label) or (v0 is not None and v1 is not None and "缺证" not in label and m0 is not None and m1 is not None))
                continue
            a0, a1 = sync_val(ctx, sid, v0), sync_val(ctx, sid, v1)
            ctx.add("%s.S%02d.val" % (tag, k), "⑧", "series_store.%s 发布日≤%s / ≤%s 的最新观测(值@观测日,公布日)" % (sid, when0, when1),
                    "%s@%s(%s) → %s@%s(%s)" % (a0, v0[0], v0[2], a1, v1[0], v1[2]), "同步面行 %s | %s | %s" % (sid, cell0, cell1),
                    v0[0] == m0.group(2) and v0[2] == m0.group(3) and v1[0] == m1.group(2) and v1[2] == m1.group(3)
                    and C.close(a0, float(m0.group(1)), ndec(m0.group(1))) and C.close(a1, float(m1.group(1)), ndec(m1.group(1))),
                    note="公布依据 %s / %s" % (v0[3], v1[3]))
            chg = a1 - a0
            mc = re.search(r"([+-]?\d+(?:\.\d+)?)(pp)?\((上行|下行|持平)\)", chg_cell)
            is_pp = sid in POLICY_SIDS
            ctx.add("%s.S%02d.chg" % (tag, k), "⑧", "读数变化=止值−起值 (%s)" % ("pp" if is_pp else "同比%"), round(chg, 6), "读数变化 %s" % chg_cell,
                    mc is not None and C.close(chg, num(mc.group(1)), ndec(mc.group(1))) and direction(chg) == mc.group(3) and (is_pp == bool(mc.group(2))))
            if reg == "US":
                us_dir[dim] = direction(chg)
                row_label[(dim, reg)] = label
                ctx.add("%s.S%02d.lab" % (tag, k), "⑧", "美国行标签", "基准(美国类比锚)", "同步性 %s" % label, label == "基准(美国类比锚)")
            else:
                ud, rd = us_dir.get(dim), direction(chg)
                if ud == rd:
                    exp = "同步" if ud != "持平" else "同步(双持平)"
                else:
                    exp = "分化——美国%svs该地区%s" % (ud, rd)
                row_label[(dim, reg)] = label
                ctx.add("%s.S%02d.lab" % (tag, k), "⑧", "标签=与美国同维方向对照(同步=同向,分化=相反或一端持平)", exp, "同步性 %s" % label, exp == label)
        narr = next((l for l in lines if l.startswith("- 当时同步性(其他经济体): ")), "")
        mm = re.search(r"^- 当时同步性\(其他经济体\): (\S+?):.*?引擎同步面\(通胀维方向,相对美国\): 中国(.+?)、欧元区(.+?)、日本(.+?)。", narr)
        words = {"CN": mm.group(2), "EA": mm.group(3), "JP": mm.group(4)} if mm else {}
        tbl = {reg: row_label.get(("通胀", reg), "") for reg in ("CN", "EA", "JP")}
        ok_words = all((w.startswith("同步") and tbl[r].startswith("同步") and "双持平" not in tbl[r] or w.startswith("分化") and tbl[r].startswith("分化")) for r, w in words.items())
        syn = [tbl[r].startswith("同步") for r in ("CN", "EA", "JP")]
        overall = "同步" if all(syn) else "不同步" if not any(syn) else "部分同步"
        ctx.add("%s.sync.narr" % tag, "⑧", "同步面表 通胀维各地区的标签 → 叙述用词与总括词", "%s / 总括=%s" % (tbl, overall), "叙述: %s" % (mm.group(0)[12:140] if mm else narr[6:120]),
                bool(mm) and ok_words and mm.group(1) == overall, note="规程§4: 叙述同步/分化主张须与引擎地区×维度同步面一致")
        for nm, sid in (("欧元区HICP", "EA_HICP_YOY"), ("日本CPI", "JP_CPI_YOY"), ("中国PPI", "CN_PPI_YOY"), ("中国CPI", "CN_CPI_YOY")):
            mv = re.search(nm + r"同比(\d{4}-\d{2})为(-?[\d.]+)", narr)
            vis = hist_vis(ctx, sid, cutoff_me)
            ctx.add("%s.sync.val.%s" % (tag, sid), "⑧", "series_store.%s 发布日≤%s 的最新观测" % (sid, cutoff_me), "%s@%s" % (vis[1], vis[0][:7]) if vis else None,
                    "叙述 %s" % (mv.group(0) if mv else "?"), bool(mv) and vis is not None and vis[0][:7] == mv.group(1) and C.close(vis[1], float(mv.group(2)), 2))
        # ---- known-then table
        kt = table_by_header_ctx(lines, ["指标", "观测期(最新可见)", "值", "首次公布日", "当时可知?", "来源", "修订口径"])
        k = 0
        for r in kt["rows"]:
            k += 1
            sid = re.search(r"\(([A-Z0-9_]+)\)\s*$", r[0]).group(1)
            vis = hist_vis(ctx, sid, cutoff_me)
            d1 = first_date(r[3])
            dates = re.findall(r"\d{4}-\d{2}-\d{2}", r[3])
            ok = (vis is not None and vis[0][:7] == r[1] and C.close(vis[1], num(r[2]), ndec(r[2])) and d1 == vis[2] and vis[2] <= cutoff_me and r[4] == "是")
            if sid == "EA_HICP_YOY" and "终值" in r[3] and len(dates) > 1:
                ok = ok and dates[-1] == C.add_days(C.month_end(r[1]), 16)
            ctx.add("%s.K%02d" % (tag, k), "⑧", "series_store.%s 发布日≤%s(截止月末)的最新观测=值/观测月/公布日" % (sid, cutoff_me),
                    "%s@%s 公布%s" % (vis[1], vis[0][:7], vis[2]) if vis else None, "当时可知面 %s | %s | %s | %s | %s" % (r[0], r[1], r[2], r[3][:40], r[4]), ok)
        # ---- ex-post table
        xt = table_by_header_ctx(lines, ["指标", "观测期", "值", "首次发布日", "延误/注记", "来源"])
        k = 0
        listed = {}
        end12 = C.month_end(L.shift_months(sec["ym"] + "-01", 12)[:7])
        for r in xt["rows"]:
            k += 1
            sid = re.search(r"\(([A-Z0-9_]+)\)\s*$", r[0]).group(1)
            note = r[4]
            obs = r[1] + "-01"
            if note.startswith("事后政策事件"):
                mv = re.search(r"([\d.]+)→([\d.]+)", r[2])
                a, b = float(mv.group(1)), float(mv.group(2))
                d = r[3]
                ser = ctx.ser(sid)
                prev = ctx.lob(sid, C.add_days(d, -1))
                exact = ctx.exact(sid, d)
                before = [x for x in ser if x[0] < d]
                pv = before[-1][1] if before else None
                dec = re.search(r"决议(\d{4}-\d{2}-\d{2})、生效(\d{4}-\d{2}-\d{2})", note)
                exp_dec = C.add_days(d, -6) if sid.startswith("ECB") else C.add_days(d, -1) if sid == "DFEDTARU" else None
                listed.setdefault(sid, []).append(d)
                ctx.add("%s.X%02d" % (tag, k), "⑧", "series_store.%s 在 %s 的变动(前值→新值) 及决议日惯例" % (sid, d), "%s→%s; 决议%s" % (pv, exact, exp_dec),
                        "事后政策事件 %s" % note[:70], exact == b and pv == a and d > cutoff_me and d <= end12 and (exp_dec is None or (dec and dec.group(1) == exp_dec and dec.group(2) == d)),
                        note="" if exp_dec is None or (dec and dec.group(1) == exp_dec) else "决议日不符惯例")
                continue
            val = ctx.exact(sid, obs)
            pub, basis = hist_pub(ctx, sid, obs)
            if r[2] == "数据不可得":
                ctx.add("%s.X%02d" % (tag, k), "⑧", "series_store.%s@%s" % (sid, r[1]), val, "事后段 %s | %s | 采集缺口" % (sid, r[1]), val is None and "采集缺口" in note)
                continue
            ok = val is not None and C.close(val, num(r[2]), ndec(r[2])) and r[3] == pub and pub > cutoff_me
            note_txt = "公布依据 %s" % basis
            if note.startswith("观测月=截止月"):
                ok = ok and r[1] == sec["ym"] and ("当时不可知,移入事后段" in note)
            elif note.startswith("缺口后恢复发布"):
                ok = ok and ctx.exact(sid, L.shift_months(obs, -1)) is None
            elif note.startswith("发布延误"):
                md = re.search(r"首发 (\d{4}-\d{2}-\d{2}) 晚于常轨推定 (\d{4}-\d{2}-\d{2}) (\d+) 天\(>(\d+) 容差\)", note)
                rule = C.add_days(C.month_end(L.shift_months(obs, 2)[:7]), C.RULE_Q_LAG[sid]) if sid in C.RULE_Q_LAG else C.add_days(C.month_end(r[1]), C.RULE_LAG.get(sid, 0))
                ok = ok and md and md.group(1) == r[3] and md.group(2) == rule and int(md.group(3)) == C.days_between(rule, r[3]) and int(md.group(3)) > int(md.group(4)) and basis.startswith("calendar")
                note_txt += "; 常轨=%s 延误=%s天" % (rule, C.days_between(rule, r[3]))
            ctx.add("%s.X%02d" % (tag, k), "⑧", "series_store.%s@%s 值 / 推定或日历发布日" % (sid, r[1]), "%s / %s" % (val, pub), "事后段 %s | %s | %s | %s" % (sid, r[1], r[2], r[3]), bool(ok), note=note_txt)
        for sid in ("DFEDTARU", "ECB_MRO", "ECB_DFR", "CN_LPR_1Y"):
            ev = [c[0] for c in L.changes_in_window(ctx.ser(sid), C.add_days(cutoff_me, 1), end12)]
            ctx.add("%s.X.ev.%s" % (tag, sid), "⑧", "series_store.%s 在(截止月末, +12月] 内的变动日全集" % sid, ev, "事后段已列事件 %s" % (listed.get(sid) or []),
                    ev == (listed.get(sid) or []), note="多列/漏列均为偏离")
        # ---- aftermath summary lines
        am = t["aftermath"]
        for ln in lines:
            m = re.match(r"\s*- 随后(\d+)个月\(锚(\d{4}-\d{2})\+(\d+)月→(\d{4}-\d{2})\): (\d{4}-\d{2})月末→(\d{4}-\d{2})月末: (.*?)\(月末口径", ln)
            if not m:
                continue
            N, anc, tgt, s_ym, e_ym = int(m.group(1)), m.group(2), m.group(4), m.group(5), m.group(6)
            ctx.add("%s.AF%d.lab" % (tag, N), "⑧", "事后窗=候选月+N 月(月末口径)", "%s→%s" % (sec["ym"], L.shift_months(sec["ym"] + "-01", N)[:7]),
                    "随后%d个月(锚%s+%d月→%s): %s月末→%s月末" % (N, anc, int(m.group(3)), tgt, s_ym, e_ym), anc == sec["ym"] and int(m.group(3)) == N and tgt == e_ym == s_ym == L.shift_months(sec["ym"] + "-01", N)[:7] or
                    (anc == sec["ym"] and tgt == e_ym and s_ym == sec["ym"] and int(m.group(3)) == N))
            for sid, sval, unit in re.findall(r"([A-Z][A-Z0-9_]+) ([+-]\d+\.\d+)(pp|%)", m.group(7)):
                v0, v1 = me_val(ctx, sid, s_ym), me_val(ctx, sid, e_ym)
                comp = (v1 - v0) if unit == "pp" else L.pct(v0, v1)
                ctx.add("%s.AF%d.%s" % (tag, N, sid), "⑧", "series_store.%s %s月末→%s月末 (%s %s→%s)" % (sid, s_ym, e_ym, unit, v0, v1), round(comp, 4),
                        "%s %s%s" % (sid, sval, unit), C.close(comp, num(sval), 2))
                if sid in am:
                    eng = am[sid]["%dm" % N]
                    ctx.add("%s.AF%d.%s.sign" % (tag, N, sid), "⑧", "S6.top[rank].aftermath.%s.%dm (引擎口径: 锚后首个观测→候选月+N月末)" % (sid, N), eng,
                            "月末口径 %s%s" % (sval, unit), (eng > 0) == (comp > 0) or (abs(eng) < 0.015 and abs(comp) < 0.015),
                            note="两口径差 %.2f" % (eng - comp))
        ctx.add("%s.AF.label" % tag, "⑧", "事后块标注(『事后实际』『非预测』)与纪律声明在场", "随后结果(事后实际——…事后陈述非预测)" in text and "事后结果标注" in text,
                "『随后结果(事后实际——与当时同步性分开,事后陈述非预测)』+『事后结果标注』", "事后实际" in text and "非预测" in text and "事后结果标注" in text)
        # engine aftermath windows independently recomputed
        for sid in ("SPX", "UST_10Y", "DXY", "GOLD_F"):
            for hz in ("3m", "6m", "12m"):
                st = L.first_on_or_after(ctx.ser(sid), L.shift_months(sec["ym"] + "-01", 1))
                en = ctx.lob(sid, C.month_end(L.shift_months(sec["ym"] + "-01", int(hz[:-1]))[:7]))
                comp = (en[1] - st[1]) if am["%s_unit" % sid] == "pp" else L.pct(st[1], en[1])
                ctx.add("%s.AE.%s.%s" % (tag, sid, hz), "⑧", "series_store.%s 锚后首个观测(%s)→候选月+%d月末最近观测(%s)" % (sid, st[0], int(hz[:-1]), en[0]), round(comp, 4),
                        "S6.aftermath.%s.%s=%s (窗 %s..%s)" % (sid, hz, am[sid][hz], am["%s_window" % sid][hz]["start"], am["%s_window" % sid][hz]["end"]),
                        C.close(comp, am[sid][hz], 4) and am["%s_window" % sid][hz]["start"] == st[0] and am["%s_window" % sid][hz]["end"] == en[0])
        # ---- sample note
        sm = next((l for l in lines if l.startswith("- 样本注记")), "")
        mc = re.search(r"增长维覆盖([\d.]+)/通胀([\d.]+)/信用([\d.]+)", sm)
        ctx.add("%s.cov" % tag, "⑧", "S6.state_vector.{growth,inflation,credit}.coverage", "%s/%s/%s" % (cov.get("growth"), cov.get("inflation"), cov.get("credit")),
                "增长维覆盖%s" % (mc.group(0) if mc else "?"), bool(mc) and C.close(cov["growth"], float(mc.group(1)), 2) and C.close(cov["inflation"], float(mc.group(2)), 2) and C.close(cov["credit"], float(mc.group(3)), 2))
        mo = re.search(r"候选期匹配窗\((\d{4}-\d{2})至(\d{4}-\d{2})\)与当前特征窗\((\d{4}-\d{2})至(\d{4}-\d{2})\)无重叠,但12个月事后窗\(至(\d{4}-\d{2})\)落入当前研究窗内", sm)
        fw0, fw1 = L.shift_months(s6["anchor_month"] + "-01", -(fw - 1))[:7], s6["anchor_month"]
        mw0, mw1 = L.shift_months(sec["ym"] + "-01", -(fw - 1))[:7], sec["ym"]
        end12ym = L.shift_months(sec["ym"] + "-01", 12)[:7]
        in_research = "2025-11" <= end12ym <= "2026-11"
        no_overlap = mw1 < fw0 or fw1 < mw0
        claims_in = "落入当前研究窗内" in sm
        ctx.add("%s.indep" % tag, "⑧", "匹配窗 %s..%s vs 当前特征窗 %s..%s (无重叠=%s); 12月事后窗止月 %s 落入当前研究窗(2025-11..2026-11)=%s" % (mw0, mw1, fw0, fw1, no_overlap, end12ym, in_research),
                {"no_overlap": no_overlap, "after12_in_research": in_research}, "样本注记 %s" % (mo.group(0)[:80] if mo else "(无『落入当前研究窗』句)"),
                no_overlap and (claims_in == in_research) and (not mo or (mo.group(1), mo.group(2), mo.group(3), mo.group(4), mo.group(5)) == (mw0, mw1, fw0, fw1, end12ym)))
        ms = re.search(r"TOP-N事后符号一致率: (.*?)——", sm)
        rates = agree
        spx_ok = rates.get("SPX_6m") == 1.0 and rates.get("SPX_12m") == 1.0
        others = [v for k, v in rates.items() if not (k.startswith("SPX_") and k in ("SPX_6m", "SPX_12m"))]
        ctx.add("%s.agree" % tag, "⑧", "S6.dispersion.topN_aftermath_sign_agreement (SPX 6m/12m; 其余最小~最大)", "%s/%s; 其余 %s~%s" % (rates.get("SPX_6m"), rates.get("SPX_12m"), min(others), max(others)),
                "TOP-N事后符号一致率: %s" % (ms.group(1)[:40] if ms else "?"), spx_ok and min(others) >= 0.6 and "满一致" in (ms.group(1) if ms else "") and "零点六" in (ms.group(1) if ms else ""),
                note="引擎面仅含 SPX 一类股指; 文字『股指』为泛称")
        # ---- per-window tables
        wt = [tb for tb in C.md_tables(lines) if tb["header"][:3] == ["组", "指标", "起期"]]
        ctx.add("%s.wt.n" % tag, "⑧", "逐窗并列表数量", len(wt), "3/6/12 个月各一表", len(wt) == 3)
        w = 0
        for tb in wt:
            w += 1
            for r in tb["rows"]:
                sid = re.search(r"\(([A-Z0-9_]+)\)\s*$", r[1]).group(1)
                get = (lambda d: (ctx.exact(sid, d), d)) if sid in MONTHLY_SIDS else (lambda d: (lambda t: (t[1], t[0]))(ctx.lob(sid, d)))
                x0, x1 = get(r[2]), get(r[4])
                okrow = x0[0] is not None and x1[0] is not None and x0[1] == r[2] and x1[1] == r[4] and C.close(x0[0], num(r[3]), ndec(r[3])) and C.close(x1[0], num(r[5]), ndec(r[5]))
                comp = None
                if okrow:
                    is_pp = r[6].endswith("pp")
                    comp = (x1[0] - x0[0]) if is_pp else L.pct(x0[0], x1[0])
                    okrow = is_pp == (r[7] == "percent") and C.close(comp, num(r[6]), ndec(r[6]))
                ctx.add("%s.W%d.%s" % (tag, w, sid), "⑧", "series_store.%s 起期/止期观测值 → 变化" % sid, "%s→%s (%s)" % (x0[0], x1[0], ("%.4f" % comp) if comp is not None else None),
                        "逐窗表 %s | %s %s→%s %s | %s %s" % (r[0], sid, r[2], r[4], r[3], r[5], r[6]), okrow)


def table_by_header_ctx(lines, first_cells):
    for tb in C.md_tables(lines):
        if tb["header"][:len(first_cells)] == first_cells:
            return tb
    return {"header": first_cells, "rows": [], "line": 0}
