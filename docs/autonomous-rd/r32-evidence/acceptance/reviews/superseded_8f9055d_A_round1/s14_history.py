#!/usr/bin/python3 -I
"""⑧ history analog: ex-post month-end tables + sync-face recompute (read-only).
usage: s14_history.py <snapshot>"""
import sys
import datetime as dt
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import lib  # seat-owned

snap = lib.load_json(sys.argv[1])
st = lib.Store(snap)
N = [0, 0]
MIS = []


def cmp(tag, mine, claim, nd=2):
    N[0] += 1
    if isinstance(mine, (int, float)) and isinstance(claim, (int, float)):
        ok = abs(round(mine, nd) - round(claim, nd)) <= 1e-9
    else:
        ok = mine == claim
    if not ok:
        N[1] += 1
        MIS.append("%s mine=%s claim=%s" % (tag, mine, claim))
    print("   %-52s mine=%-24s claim=%-20s %s" % (tag, mine, claim, "OK" if ok else "<<< MISMATCH"))
    return ok


def info(tag, mine):
    print("   %-52s mine=%s   (info)" % (tag, mine))


def mend(ym):
    y, m = int(ym[:4]), int(ym[5:7])
    nm_y, nm_m = (y, m + 1) if m < 12 else (y + 1, 1)
    return (dt.date(nm_y, nm_m, 1) - dt.timedelta(days=1)).isoformat()


def me_val(mid, ym):
    """month-end reading: latest obs with obs date <= month end (and inside that month for daily series)."""
    o = st.on_or_before(mid, mend(ym))
    return o


M = ["DFEDTARU", "UNEMPLOYMENT", "CPI", "INDPRO", "SPX", "NIKKEI225", "DAX", "SHCOMP", "GOLD_F", "DXY", "UST_10Y"]
PP = {"DFEDTARU", "UNEMPLOYMENT", "UST_10Y"}
TAB = {
    "2025-03": {"3m": ("2025-06", [0.00, -0.10, 0.52, 0.43, 10.57, 13.67, 7.88, 3.26, 5.92, -7.03, 0.01]),
                "6m": ("2025-09", [-0.25, 0.20, 1.39, 0.62, 19.18, 26.15, 7.75, 16.40, 24.03, -6.18, -0.07]),
                "12m": ("2026-03", [-0.75, 0.10, 3.29, 0.69, 16.33, 43.37, 2.33, 16.67, 48.83, -4.08, 0.07])},
    "2022-06": {"3m": ("2022-09", [1.50, -0.10, 0.47, 0.27, -5.28, -1.73, -5.24, -11.01, -7.49, 7.10, 0.85]),
                "6m": ("2022-12", [2.75, -0.10, 1.31, -1.24, 1.43, -1.13, 8.92, -9.10, 1.05, -1.12, 0.90]),
                "12m": ("2023-06", [3.50, 0.00, 3.07, -0.89, 17.57, 25.75, 26.32, -5.78, 6.76, -1.70, 0.83])},
    "2023-10": {"3m": ("2024-01", [0.00, -0.20, 0.65, -1.24, 15.54, 17.59, 14.13, -7.63, 2.71, -3.18, -0.89]),
                "6m": ("2024-04", [0.00, 0.00, 1.73, -0.22, 20.07, 24.46, 21.08, 2.85, 15.47, -0.41, -0.19]),
                "12m": ("2024-10", [-0.50, 0.20, 2.58, -0.99, 36.04, 26.65, 28.81, 8.65, 37.86, -2.51, -0.60])},
}
print("### ex-post month-end tables (judgment history_periods[*].ex_post)")
for anc, hor in TAB.items():
    a0 = {m: me_val(m, anc) for m in M}
    print("  anchor %s base obs: %s" % (anc, {m: (a0[m][0], round(a0[m][1], 4)) for m in M}))
    for h, (ym, claims) in hor.items():
        cmp("%s %s target month" % (anc, h), lib.shift_months(anc + "-01", int(h[:-1]))[:7], ym)
        for m, c in zip(M, claims):
            b = me_val(m, ym)
            if m in PP:
                mine = round(b[1] - a0[m][1], 2)
            else:
                mine = round(lib.pct_change(a0[m][1], b[1]), 2)
            cmp("%s %s %s" % (anc, h, m), mine, c)
            info("%s %s %s obs dates" % (anc, h, m), (a0[m][0], b[0]))

print("### scenario direction quotes (same tables)")
T = TAB


def g(anc, h, m):
    return TAB[anc][h][1][M.index(m)]


cmp("2022-06 3m SPX", g("2022-06", "3m", "SPX"), -5.28)
cmp("2022-06 3m GOLD_F", g("2022-06", "3m", "GOLD_F"), -7.49)
cmp("2022-06 3m DXY", g("2022-06", "3m", "DXY"), 7.10)
cmp("2022-06 12m SPX (+17.57)", g("2022-06", "12m", "SPX"), 17.57)
cmp("2025-03 12m GOLD_F", g("2025-03", "12m", "GOLD_F"), 48.83)
cmp("2025-03 12m DXY", g("2025-03", "12m", "DXY"), -4.08)
cmp("2025-03 12m SPX", g("2025-03", "12m", "SPX"), 16.33)

print("### S6-derived history facts (distance / pct / dims)")


def q(x):
    return round(x, 4)


DIMS = {"2025-03": (0.727212, 0.0, {"growth": 3.4e-05, "inflation": 0.105401, "rates": 0.4066, "credit": 0.0, "volatility": 0.421281, "valuation": 0.066684}, 42.1, 40.7, 10.5, 6.7),
        "2022-06": (0.791806, 1.3699, None, 51.9, 33.6, 11.4, 3.0),
        "2023-10": (1.054168, 30.137, None, 60.1, 21.2, 11.0, 7.7)}
for anc, (d0, p0, dims, a, b, c, e) in DIMS.items():
    cmp("%s distance 4dp" % anc, q(d0), {"2025-03": 0.7272, "2022-06": 0.7918, "2023-10": 1.0542}[anc], nd=4)
    cmp("%s pct 2dp" % anc, q(p0), {"2025-03": 0.0, "2022-06": 1.37, "2023-10": 30.14}[anc], nd=2)
    if dims:
        tot = sum(dims.values())
        cmp("%s vol share pct" % anc, round(100 * dims["volatility"] / tot, 1), a, nd=1)
        cmp("%s rates share pct" % anc, round(100 * dims["rates"] / tot, 1), b, nd=1)
        cmp("%s inflation share pct" % anc, round(100 * dims["inflation"] / tot, 1), c, nd=1)
        cmp("%s valuation share pct" % anc, round(100 * dims["valuation"] / tot, 1), e, nd=1)

print("### sync-face: quoted latest-revised values")


def mv(mid, ym):
    o = st.month_obs(mid, ym)
    return o[-1] if o else None


def cpi_yoy(ym):
    v = st.at("CPI", ym + "-01")
    b = st.at("CPI", lib.shift_months(ym + "-01", -12))
    return None if (v is None or b is None) else round((v / b - 1.0) * 100.0, 4)


for anc, q_ in {"2025-03": [("EA_HICP_YOY", "2025-02", 2.3), ("JP_CPI_YOY", "2025-02", 3.66), ("CN_PPI_YOY", "2025-02", -2.2), ("CN_CPI_YOY", "2025-02", -0.7)],
                "2022-06": [("EA_HICP_YOY", "2022-05", 8.1), ("JP_CPI_YOY", "2022-05", 2.46), ("CN_PPI_YOY", "2022-05", 6.4), ("CN_CPI_YOY", "2022-05", 2.1)],
                "2023-10": [("EA_HICP_YOY", "2023-10", 2.9), ("JP_CPI_YOY", "2023-09", 3.05), ("CN_PPI_YOY", "2023-09", -2.5), ("CN_CPI_YOY", "2023-09", 0.0)]}.items():
    for mid, ym, c in q_:
        o = mv(mid, ym)
        cmp("%s %s %s" % (anc, mid, ym), None if o is None else round(o[1], 2), c)


def pub_date(mid, d):
    """engine RELEASE_RULES (planner source, read-only): publication date for an observation dated d."""
    if mid in ("DFEDTARU", "ECB_MRO"):
        return d
    if mid == "CN_LPR_1Y":
        return d[:7] + "-20"
    if mid == "EA_HICP_YOY" and d[:7] in CAL_FLASH:
        return CAL_FLASH[d[:7]]
    me = mend(d[:7])
    if mid == "US_REAL_GDP":
        qe = mend({1: d[:4] + "-03", 4: d[:4] + "-06", 7: d[:4] + "-09", 10: d[:4] + "-12"}[int(d[5:7])])
        return (lib.ymd(qe) + dt.timedelta(days=29)).isoformat()
    if mid == "EA_REAL_GDP_YOY":
        qe = mend({1: d[:4] + "-03", 4: d[:4] + "-06", 7: d[:4] + "-09", 10: d[:4] + "-12"}[int(d[5:7])])
        return (lib.ymd(qe) + dt.timedelta(days=35)).isoformat()
    if mid == "JP_REAL_GDP_YOY":
        qe = mend({1: d[:4] + "-03", 4: d[:4] + "-06", 7: d[:4] + "-09", 10: d[:4] + "-12"}[int(d[5:7])])
        return (lib.ymd(qe) + dt.timedelta(days=45)).isoformat()
    off = {"CPI": 13, "CN_PMI_MFG": -1, "CN_CPI_YOY": 9, "EA_HICP_YOY": 0, "JP_CPI_YOY": 20, "JP_POLICY_RATE": 5}[mid]
    return (lib.ymd(me) + dt.timedelta(days=off)).isoformat()


def visible(mid, limit_ym):
    """latest observation (obs date, value, pub date) with publication date <= last day of limit month"""
    lim = mend(limit_ym)
    out = None
    for d, v in st.series(mid):
        if d > lim:
            break
        p = pub_date(mid, d)
        if p <= lim:
            out = (d, v, p)
    return out


CAL_FLASH = {"2021-05": "2021-06-01", "2022-06": "2022-07-01", "2025-03": "2025-04-01"}  # frozen calendar entries RC-EA-HICP-*
FACE = [  # (dimension, region, metric)
    ("growth", "US", "US_REAL_GDP"), ("inflation", "US", "CPI"), ("policy", "US", "DFEDTARU"),
    ("growth", "CN", "CN_PMI_MFG"), ("inflation", "CN", "CN_CPI_YOY"), ("policy", "CN", "CN_LPR_1Y"),
    ("growth", "EA", "EA_REAL_GDP_YOY"), ("inflation", "EA", "EA_HICP_YOY"), ("policy", "EA", "ECB_MRO"),
    ("growth", "JP", "JP_REAL_GDP_YOY"), ("inflation", "JP", "JP_CPI_YOY"), ("policy", "JP", "JP_POLICY_RATE")]
ENGINE = {  # engine sync face as rendered in MAP_REPORT.md: anchor-3 (obs,value,pub), cutoff (obs,value,pub)
    "2025-03": [("2024-07-01", 2.9479, "2024-10-29"), ("2024-10-01", 2.6419, "2025-01-29"), ("2024-11-01", 2.7195, "2024-12-13"), ("2025-02-01", 2.8016, "2025-03-13"),
                ("2024-12-31", 4.5, "2024-12-31"), ("2025-03-31", 4.5, "2025-03-31"), ("2024-12-01", 50.1, "2024-12-30"), ("2025-03-01", 50.5, "2025-03-30"),
                ("2024-11-01", 0.2, "2024-12-09"), ("2025-02-01", -0.7, "2025-03-09"), ("2024-12-20", 3.1, "2024-12-20"), ("2025-03-20", 3.1, "2025-03-20"),
                ("2024-07-01", 1.31, "2024-11-04"), ("2024-10-01", 1.56, "2025-02-04"), ("2024-12-01", 2.4, "2024-12-31"), ("2025-02-01", 2.3, "2025-02-28"),
                ("2024-12-18", 3.15, "2024-12-18"), ("2025-03-12", 2.65, "2025-03-12"), ("2024-07-01", 1.11, "2024-11-14"), ("2024-10-01", 1.01, "2025-02-14"),
                ("2024-11-01", 2.92, "2024-12-20"), ("2025-02-01", 3.66, "2025-03-20"), ("2024-11-01", 0.227, "2024-12-05"), ("2025-02-01", 0.478, "2025-03-05")],
    "2022-06": [("2021-10-01", 5.8182, "2022-01-29"), ("2022-01-01", 3.9754, "2022-04-29"), ("2022-02-01", 7.9373, "2022-03-13"), ("2022-05-01", 8.5382, "2022-06-13"),
                ("2022-03-31", 0.5, "2022-03-31"), ("2022-06-30", 1.75, "2022-06-30"), ("2022-03-01", 49.5, "2022-03-30"), ("2022-06-01", 50.2, "2022-06-29"),
                ("2022-02-01", 0.9, "2022-03-09"), ("2022-05-01", 2.1, "2022-06-09"), ("2022-03-21", 3.7, "2022-03-20"), ("2022-06-20", 3.7, "2022-06-19"),
                ("2021-10-01", 5.68, "2022-02-04"), ("2022-01-01", 5.58, "2022-05-05"), ("2022-03-01", 7.4, "2022-03-31"), ("2022-05-01", 8.1, "2022-05-31"),
                ("2019-09-18", 0, "2019-09-18"), ("2019-09-18", 0, "2019-09-18"), ("2021-10-01", 2.8, "2022-02-14"), ("2022-01-01", 1.15, "2022-05-15"),
                ("2022-02-01", 0.95, "2022-03-20"), ("2022-05-01", 2.46, "2022-06-20"), ("2022-02-01", -0.018, "2022-03-05"), ("2022-05-01", -0.018, "2022-06-05")],
    "2023-10": [("2023-04-01", 2.736, "2023-07-29"), ("2023-07-01", 3.1839, "2023-10-29"), ("2023-06-01", 3.0706, "2023-07-13"), ("2023-09-01", 3.6872, "2023-10-13"),
                ("2023-07-31", 5.5, "2023-07-31"), ("2023-10-31", 5.5, "2023-10-31"), ("2023-07-01", 49.3, "2023-07-30"), ("2023-10-01", 49.5, "2023-10-30"),
                ("2023-06-01", 0, "2023-07-09"), ("2023-09-01", 0, "2023-10-09"), ("2023-07-20", 3.55, "2023-07-20"), ("2023-10-20", 3.45, "2023-10-20"),
                ("2023-01-01", 1.22, "2023-05-05"), ("2023-04-01", 0.48, "2023-08-04"), ("2023-07-01", 5.3, "2023-07-31"), ("2023-10-01", 2.9, "2023-10-31"),
                ("2023-06-21", 4, "2023-06-21"), ("2023-09-20", 4.5, "2023-09-20"), ("2023-01-01", 2.06, "2023-05-15"), ("2023-04-01", 1.17, "2023-08-14"),
                ("2023-06-01", 3.3, "2023-07-20"), ("2023-09-01", 3.05, "2023-10-20"), ("2023-06-01", -0.066, "2023-07-05"), ("2023-09-01", -0.054, "2023-10-05")],
}
JUDG = {"2025-03": (3, {"CN": {"growth": "分化", "inflation": "分化", "policy": "同步"}, "EA": {"growth": "分化", "inflation": "分化", "policy": "分化"}, "JP": {"growth": "同步", "inflation": "同步", "policy": "分化"}}),
        "2022-06": (5, {"CN": {"growth": "分化", "inflation": "同步", "policy": "分化"}, "EA": {"growth": "同步", "inflation": "同步", "policy": "分化"}, "JP": {"growth": "同步", "inflation": "同步", "policy": "分化"}}),
        "2023-10": (1, {"CN": {"growth": "同步", "inflation": "分化", "policy": "分化"}, "EA": {"growth": "分化", "inflation": "分化", "policy": "分化"}, "JP": {"growth": "分化", "inflation": "分化", "policy": "分化"}})}


def val(dim, reg, mid, o):
    if o is None:
        return None
    if mid in ("CPI", "US_REAL_GDP"):  # engine kind level_yoy: same-month / same-quarter base a year earlier
        b = st.at(mid, lib.shift_months(o[0], -12))
        return None if (b in (None, 0)) else round((o[1] / b - 1.0) * 100.0, 4)
    return o[1]


print("### sync-face recompute (visibility = publication date <= month end; rules from planner RELEASE_RULES)")
for anc in ["2025-03", "2022-06", "2023-10"]:
    a3 = lib.shift_months(anc + "-01", -3)[:7]
    rows = {}
    n_sync = 0
    print("  -- segment %s (anchor-3 = %s)" % (anc, a3))
    for i, (dim, reg, mid) in enumerate(FACE):
        o0 = visible(mid, a3)
        o1 = visible(mid, anc)
        v0, v1 = val(dim, reg, mid, o0), val(dim, reg, mid, o1)
        e0, e1 = ENGINE[anc][2 * i], ENGINE[anc][2 * i + 1]
        tag = "%s %s/%s" % (anc, reg, dim)
        if o0 is None or o1 is None or v0 is None or v1 is None:
            lab = "缺证"
            cmp(tag + " presence", "absent", "absent")
        else:
            cmp(tag + " anchor-3 obs date", o0[0], e0[0])
            cmp(tag + " anchor-3 value", round(v0, 4), e0[1], nd=4)
            cmp(tag + " anchor-3 pub date", o0[2], e0[2])
            cmp(tag + " cutoff obs date", o1[0], e1[0])
            cmp(tag + " cutoff value", round(v1, 4), e1[1], nd=4)
            cmp(tag + " cutoff pub date", o1[2], e1[2])
            chg = round(v1 - v0, 4)
            sgn = 0 if abs(chg) < 1e-9 else (1 if chg > 0 else -1)
            rows[(reg, dim)] = sgn
            info(tag + " change", chg)
    us = {d: rows.get(("US", d)) for d in ("growth", "inflation", "policy")}
    info("%s US direction" % anc, us)
    for (reg, dim), s in rows.items():
        if reg == "US":
            continue
        u = us[dim]
        if s is None or u is None:
            lab = "缺证"
        elif s == 0 and u == 0:
            lab = "同步"
        elif s != 0 and u != 0 and s == u:
            lab = "同步"
        else:
            lab = "分化"
        if lab == "同步":
            n_sync += 1
        cmp("%s label %s/%s" % (anc, reg, dim), lab, JUDG[anc][1][reg][dim])
    cmp("%s number of synchronized cells (of 9)" % anc, n_sync, JUDG[anc][0], nd=0)

print("### misc: JP policy path facts quoted in turnings[2]")
cmp("JP_POLICY_RATE 2025-11 = 0.478", st.at("JP_POLICY_RATE", "2025-11-01"), 0.478, nd=3)
cmp("JP_POLICY_RATE 2025-12 = 0.557", st.at("JP_POLICY_RATE", "2025-12-01"), 0.557, nd=3)
cmp("JP_POLICY_RATE 2026-10 = 1.227", st.at("JP_POLICY_RATE", "2026-10-01"), 1.227, nd=3)
cmp("net 2025-11 -> 2026-10 (bp)", round((1.227 - 0.478) * 100), 75, nd=0)
cmp("net 2025-12 -> 2026-10 (bp)", round((1.227 - 0.557) * 100), 67, nd=0)
cmp("JP CPI 2026-07 = 1.97", st.at("JP_CPI_YOY", "2026-07-01"), 1.97)
cmp("JP CPI 2026-10 = 2.44", st.at("JP_CPI_YOY", "2026-10-01"), 2.44)
cmp("JP CPI 2026-03 = 1.46", st.at("JP_CPI_YOY", "2026-03-01"), 1.46)
cmp("JP CPI 2026-04 = 1.38", st.at("JP_CPI_YOY", "2026-04-01"), 1.38)
cmp("CN overnight 1.25 @ 2026-11-23", st.at("CN_POLICY_OVERNIGHT", "2026-11-23"), 1.25)
cmp("CN overnight latest", st.on_or_before("CN_POLICY_OVERNIGHT", "2026-11-23"), ("2026-11-23", 1.25))
print("   CN_POLICY_OVERNIGHT first obs:", st.series("CN_POLICY_OVERNIGHT")[:2])
cmp("CN_OMO_7D last obs", st.on_or_before("CN_OMO_7D", "2026-11-23"), ("2026-10-30", 1.4))
cmp("lag days CN_OMO_7D", lib.days_between("2026-10-30", "2026-11-23"), 24, nd=0)
print("   CN_OMO_7D 2026 obs (first 3, last 3):", st.in_range("CN_OMO_7D", "2025-11-01", "2026-11-23")[:3], st.in_range("CN_OMO_7D", "2025-11-01", "2026-11-23")[-3:])
cmp("CN_LPR_1Y last obs", st.on_or_before("CN_LPR_1Y", "2026-11-23"), ("2026-11-20", 3.0))
print("   ECB series last obs:", st.last_date("ECB_DFR"), st.last_date("ECB_MRO"))
print("=" * 100)
print("POINTS=%d MISMATCHES=%d" % (N[0], N[1]))
for m in MIS:
    print("MISMATCH:", m)
