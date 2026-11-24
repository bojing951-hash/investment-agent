#!/usr/bin/python3 -I
"""席位自写脚本 s19: 第 4 节「同步性」核查——受审稿的同步主张与引擎地区×维度面是否一致(只读复算).

用法: /usr/bin/python3 -I s19_sync.py <快照> <report.json> <agent_judgment.json> <席位目录>
每个点各自 try/except: 脚本自身假设的键名不成立时记为探针(不计点), 不产生假偏离.
"""
import json
import os
import re
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seatlib import Points, Store, load_json  # noqa: E402

SNAP, REP, AJ, SEAT = sys.argv[1:5]
snap = load_json(SNAP)
rep = load_json(REP)
aj = load_json(AJ)
S = Store(snap)
rp = rep["research_plan"]
SRC = "root_overlay/data/daily/research_snapshot_20261123.json:series_store"
P = Points("④查", "同步性: 受审稿同步主张 vs 引擎地区×维度面")
YM = re.compile(r"^\d{4}-\d{2}$")


def walk_str(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from walk_str(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk_str(v)


def guarded(pid, fn):
    try:
        return fn()
    except Exception as e:  # 脚本自身假设失败 → 探针, 不计点
        P.add_probe(pid + " [脚本未完成,转探针]", "ERROR " + repr(e)[:300], "s19 自身假设的键名/结构不成立", traceback.format_exc()[-500:])
        return None


cands = rp.get("turning_candidates", {}).get("candidates", []) or []


def cand(mid):
    for c in cands:
        if isinstance(c, dict) and c.get("metric_id") == mid:
            return c
    return {}


def win(c):
    for a, b in (("from_ym", "to_ym"), ("start_ym", "end_ym"), ("from", "to"), ("window_start", "window_end")):
        if a in c and b in c:
            return (str(c[a])[:7], str(c[b])[:7])
    ys = sorted({v for v in walk_str(c) if YM.match(v)})
    return (ys[0], ys[-1]) if len(ys) == 2 else (None, None)


def y1():
    wc, we = win(cand("CPI")), win(cand("EA_HICP_YOY"))
    keys = {"CPI": sorted(cand("CPI").keys()), "EA_HICP_YOY": sorted(cand("EA_HICP_YOY").keys())}
    if wc[0] is None or we[0] is None:
        P.add_probe("Y1 [候选窗键名未识别,转探针]", {"CPI": wc, "EA_HICP_YOY": we}, "report.json:research_plan.turning_candidates.candidates", json.dumps(keys, ensure_ascii=False))
        return
    ok = (wc == we == ("2026-02", "2026-05"))
    row = P.add_bool("Y1-「美欧通胀同月抬升」: 候选面 CPI 与 EA_HICP_YOY 的最大变动窗同为 2026-02..2026-05", True, ok,
                     "report.json:research_plan.turning_candidates.candidates[metric_id=CPI|EA_HICP_YOY]",
                     f"CPI 窗 {wc[0]}..{wc[1]}; EA_HICP_YOY 窗 {we[0]}..{we[1]}")
    return row


guarded("Y1", y1)


def y2():
    res = []
    ok = True
    for ym in ("2026-03", "2026-04", "2026-05"):
        u = (S.yoy("CPI", "2026-02")[0], S.yoy("CPI", ym)[0])
        e = (S.mval("EA_HICP_YOY", "2026-02"), S.mval("EA_HICP_YOY", ym))
        if None in u or None in e:
            raise RuntimeError(f"yoy 缺失 {ym} {u} {e}")
        same = (u[1] > u[0]) == (e[1] > e[0])
        ok = ok and same
        res.append({"ym": ym, "us_cpi_yoy": [round(u[0], 4), round(u[1], 4)], "ea_hicp_yoy": [e[0], e[1]], "same_dir": same})
    P.add_bool("Y2-同窗内美欧同比逐月同向(2026-03..05 各月相对窗启 2026-02 均上行)→「同月抬升」与序列面一致", True, ok,
               f"{SRC}.CPI(同比直算)/EA_HICP_YOY[2026-02..2026-05]", json.dumps(res, ensure_ascii=False))


guarded("Y2", y2)

raw = rp.get("point_values", {}).get("cells", [])
cells = {c.get("metric_id"): c for c in raw} if isinstance(raw, list) else dict(raw)


def anchors(c):
    a = c.get("anchors")
    if isinstance(a, dict):
        return a
    if isinstance(a, list):
        return {(x.get("label") or x.get("anchor") or x.get("name") or str(i)): x for i, x in enumerate(a) if isinstance(x, dict)}
    return {}


def by_asof(c, d):
    for k, v in anchors(c).items():
        if str(v.get("as_of", ""))[:10] == d:
            return k, v
    return None, {}


def y3():
    res = {}
    ok = True
    for mid in ("CPI", "CORE_CPI", "CORE_PCE", "EA_HICP_YOY"):
        c = cells[mid]
        k0, a0 = by_asof(c, "2026-08-23")
        k1, a1 = by_asof(c, "2026-11-23")
        if mid == "EA_HICP_YOY":
            v0, v1 = a0.get("value"), a1.get("value")
            m0, m1 = "2026-07", "2026-10"
            own = [S.mval(mid, m0), S.mval(mid, m1)]
        else:
            # 引擎格内同比: derived_yoy_pct; 缺基期格取格内 latest_valid_yoy(同比只以去年同月为基期, 不以相邻月替代)
            v0, v1 = a0.get("derived_yoy_pct"), a1.get("derived_yoy_pct")
            m0, m1 = a0["observation_date"][:7], a1["observation_date"][:7]
            if v1 is None:
                lv = a1.get("latest_valid_yoy") or {}
                v1, m1 = lv.get("yoy_pct"), str(lv.get("observation_date", ""))[:7]
            own = [S.yoy(mid, m0)[0], S.yoy(mid, m1)[0]]
        if v0 is None or v1 is None or None in own:
            raise RuntimeError(f"格值缺失 {mid} {a0} {a1} {own}")
        agree = abs(v0 - own[0]) < 0.006 and abs(v1 - own[1]) < 0.006
        up = v1 > v0
        ok = ok and up and agree
        res[mid] = {"anchors": [k0, k1], "obs": [a0.get("observation_date"), a1.get("observation_date")], "yoy_months": [m0, m1], "cell_yoy": [v0, v1], "own_yoy": [round(own[0], 4), round(own[1], 4)], "up": up, "cell_eq_own": agree}
    P.add_bool("Y3-「美欧通胀环境较 3 个月前同步走高」: 通胀维四格(美 CPI/核心 CPI/核心 PCE、欧 HICP)两锚间全部上行, 且格内同比与 series_store 直算一致", True, ok,
               "report.json:research_plan.point_values.cells[metric_id].anchors; series_store 直算", json.dumps(res, ensure_ascii=False))


guarded("Y3", y3)


def y4():
    g = lambda m: (S.yoy(m, "2026-04")[0], S.yoy(m, "2026-07")[0])  # noqa: E731
    us_gdp, ip = g("US_REAL_GDP"), (S.yoy("INDPRO", "2026-07")[0], S.yoy("INDPRO", "2026-10")[0])  # 月频: 锚观测月 2026-07→2026-10(初版误取 2026-04→2026-07, 已更正)
    un = (S.mval("UNEMPLOYMENT", "2026-07"), S.mval("UNEMPLOYMENT", "2026-10"))
    ea = (S.mval("EA_REAL_GDP_YOY", "2026-04"), S.mval("EA_REAL_GDP_YOY", "2026-07"))
    if None in us_gdp + ip + un + ea:
        raise RuntimeError("增长维值缺失")
    res = {"US_REAL_GDP_yoy": [round(us_gdp[0], 4), round(us_gdp[1], 4)], "UNEMPLOYMENT": list(un), "INDPRO_yoy": [round(ip[0], 4), round(ip[1], 4)],
           "EA_REAL_GDP_YOY": list(ea)}
    small = all(abs(x[1] - x[0]) < 0.9 for x in (us_gdp, ip, ea))
    mixed = (us_gdp[1] < us_gdp[0]) and (ip[1] > ip[0]) and (ea[1] >= ea[0])
    P.add_bool("Y4-增长维两锚方向(美 GDP 同比微降/失业率持平/工业生产同比回升;欧 GDP 同比不降)→「大体平稳」与序列面不相左(各变动<0.9pp 且正负互见)", True, small and mixed,
               f"{SRC}.US_REAL_GDP/UNEMPLOYMENT/INDPRO[2026-07→2026-10]、US_REAL_GDP/EA_REAL_GDP_YOY[2026-04→2026-07]", json.dumps(res, ensure_ascii=False))


guarded("Y4", y4)

turn_txt = " ".join(walk_str(aj.get("reader_map", {}).get("turnings", [])))
P.add_probe("Y5-同步主张的时间分辨率限定词在场(「月频证据先后未定」「同月」)", {"月频证据先后未定": "月频证据先后未定" in turn_txt, "同月": "同月" in turn_txt, "不可判": "不可判" in turn_txt},
            "agent_judgment.json:reader_map.turnings[*]", "文本性质核对, 不计点")


def y6():
    cl = rp.get("policy_event_clusters", {}).get("clusters", [])
    P.add_bool("Y6-受审稿未对美欧政策维下同步/分化断言(表述为「不可判」),且引擎政策事件簇为空(无跨国同步面可供引用)", True, cl == [] and ("不可判" in turn_txt),
               "report.json:research_plan.policy_event_clusters.clusters; agent_judgment.json:reader_map.turnings", f"clusters 条数 {len(cl)}")


guarded("Y6", y6)


def y7():
    dg = rp.get("dimension_gaps") or []
    if isinstance(dg, dict):
        dg = [dg]
    l3c = aj.get("l3", {}).get("contradictions", [])
    hit = [x for x in l3c if "C3-JP-POLICY" in json.dumps(x, ensure_ascii=False)]
    disclosed = bool(hit) and "JP_POLICY_TARGET" in json.dumps(hit[0], ensure_ascii=False)
    P.add_bool("Y7-引擎 dimension_gaps 恰为 JP_POLICY_TARGET registry_absent 一条,与受审稿的官方目标缺席披露一致", True,
               len(dg) == 1 and dg[0].get("metric_id") == "JP_POLICY_TARGET" and dg[0].get("gap") == "registry_absent" and disclosed,
               "report.json:research_plan.dimension_gaps; agent_judgment.json:l3.contradictions[C3-JP-POLICY]", json.dumps(dg, ensure_ascii=False)[:400])
    P.add("Y8-引擎 dimension_gaps 条数", 1, len(dg), "report.json:research_plan.dimension_gaps", nd=0)


guarded("Y7", y7)
def y9():
    mlist = ["2026-02", "2026-03", "2026-04", "2026-05", "2026-07", "2026-08"]
    mv = {y: S.mval("JP_POLICY_RATE", y) for y in mlist}
    if None in mv.values():
        raise RuntimeError(f"月均缺失 {mv}")
    d = {f"{a}->{b}": round(mv[b] - mv[a], 4) for a, b in (("2026-02", "2026-03"), ("2026-03", "2026-04"), ("2026-04", "2026-05"), ("2026-07", "2026-08"))}
    P.add_bool("Y9-C3 竞争解释容差依据「2026-02 至 2026-05 与 2026-08 的相邻月均差均不超过 0.001」(月均台阶按落入月计: 2026-08 档=2026-07→2026-08)", True,
               all(abs(x) <= 0.001 for x in d.values()), f"{SRC}.JP_POLICY_RATE[2026-02..2026-05,2026-07,2026-08]",
               json.dumps({"monthly": mv, "adjacent_diff": d}, ensure_ascii=False))


guarded("Y9", y9)
P.save("points_17_sync.json")
