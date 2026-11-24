#!/usr/bin/python3 -I
"""Recompute part B (categories ⑦-⑩): mechanism chain, transmission links, analog, scenarios, consistency.

Read-only. Args:
  <snapshot.json> <report.json> <agent_judgment.json> <release_calendar.json> <metric_registry.json>
  <run_dir> <tree_dir> <out_dir>
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("s10_common", os.path.join(HERE, "s10_common.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

a = sys.argv[1:]
snap, rep, jd, cal, reg = (C.load_json(p) for p in a[0:5])
run_dir, tree_dir, out_dir = a[5], a[6], a[7]
ss = snap["series_store"]
plan = rep["research_plan"]
cutoff = plan["cutoff"]
CD = C.D(cutoff)
regm = {m["metric_id"]: m for m in reg["metrics"]}
SNAP = "research_snapshot_20261123.json"


def T(p):
    return C.get(jd, p)


C1, C2, C3 = (T("l3.contradictions[%d].statement" % i) for i in range(3))
M = [T("l3.mechanism_chains[0].links[%d].text" % i) for i in range(4)]
HL = T("reader_map.headline_conclusion")
EA = T("reader_map.regions[0].from_to")
JP = T("reader_map.regions[1].from_to")
TL = [T("reader_map.transmission[0].links[%d]" % i) for i in range(3)]
TLN = [t["verdict_note"] for t in TL]
TN = [T("reader_map.turnings[%d]" % i) for i in range(3)]
QN = T("quality_gate_notes")
S1 = T("l4.scenarios[0].rows")
S2 = T("l4.scenarios[1].rows")
HN = T("reader_map.history_zero_case_note")
DECL = T("agent_declaration")
B = C.Book("B")
add = B.add


def v(mid, d):
    return C.val_at(ss, mid, d)


def pc(mid, d0, d1):
    return C.pct(v(mid, d1), v(mid, d0))


def r(x, n=2):
    return C.rnd(x, n)


def src(mid, d):
    return "%s:series_store.%s[%s]" % (SNAP, mid, d)


def tds(mid, upto, n=None):
    ds = [d for d, x in zip(*C.series(ss, mid)) if x is not None and d <= upto]
    return ds[-n:] if n else ds


eam, jpm, jpmr = C.monthly(ss, "EA_HICP_YOY"), C.monthly(ss, "JP_CPI_YOY"), C.monthly(ss, "JP_POLICY_RATE")


def change_points(mid, min_bp=0.5):
    ds, vs = C.series(ss, mid)
    return [(ds[i], vs[i - 1], vs[i]) for i in range(1, len(ds))
            if vs[i] is not None and vs[i - 1] is not None and abs(C.bp(vs[i], vs[i - 1])) >= min_bp]


# ================================================================ ⑦ mechanism chain
add("G001", "⑦", "M1-1 欧元区 2026-02", src("EA_HICP_YOY", "2026-02"), eam["2026-02"], 1.9, lit="2026-02 的 1.9", text=M[0])
add("G002", "⑦", "M1-1 欧元区 2026-05", src("EA_HICP_YOY", "2026-05"), eam["2026-05"], 3.2, lit="升至 2026-05 的 3.2", text=M[0])
add("G003", "⑦", "M1-1 欧元区 2026-06", src("EA_HICP_YOY", "2026-06"), eam["2026-06"], 2.8, lit="2026-06 一度回落至 2.8", text=M[0])
add("G004", "⑦", "M1-1 欧元区 2026-10", src("EA_HICP_YOY", "2026-10"), eam["2026-10"], 4.0, lit="2026-10 达 4.0", text=M[0])
add("G005", "⑦", "M1-1 日本 2025-01", src("JP_CPI_YOY", "2025-01"), jpm["2025-01"], 4.03, lit="自 2025-01 高点 4.03 回落", text=M[0])
jds, jvs = C.series(ss, "JP_CPI_YOY")
i0 = jds.index("2025-01-01")
t12 = [x for d, x in zip(jds, jvs) if "2024-01-01" <= d <= "2025-01-01" and x is not None]
smax = max((x, d) for d, x in zip(jds, jvs) if x is not None)
add("G006", "⑦", "M1-1『高点』用词", "JP_CPI_YOY 2025-01 是否局部峰值 / 是否为其前 12 个月最高",
    (jvs[i0 - 1] < jvs[i0] and jvs[i0 + 1] < jvs[i0], max(t12)), (True, 4.03),
    note="全序列最高为 %s@%s(更早年),『2025-01 高点』=局部高点/近一年高点,读法成立" % (smax[0], smax[1]))
add("G007", "⑦", "M1-1 日本 2025-07", src("JP_CPI_YOY", "2025-07"), jpm["2025-07"], 3.1, lit="经 2025-07 的 3.1", text=M[0])
add("G008", "⑦", "M1-1 日本 2025-09", src("JP_CPI_YOY", "2025-09"), jpm["2025-09"], 2.91, lit="两度小幅回升至 2.91、2.99", text=M[0])
add("G009", "⑦", "M1-1 日本 2025-10", src("JP_CPI_YOY", "2025-10"), jpm["2025-10"], 2.99, lit="两度小幅回升至 2.91、2.99", text=M[0])
add("G010", "⑦", "M1-1 日本 2026-02", src("JP_CPI_YOY", "2026-02"), jpm["2026-02"], 1.27, lit="至 2026-02 的 1.27", text=M[0])
add("G011", "⑦", "M1-1 日本 2026-10", src("JP_CPI_YOY", "2026-10"), jpm["2026-10"], 2.44, lit="总体回升至 2026-10 的 2.44", text=M[0])
seq = [jpm[k] for k in sorted(jpm) if "2025-01" <= k <= "2026-02"]
n_up = sum(1 for i in range(1, len(seq)) if seq[i] > seq[i - 1])
add("G012", "⑦", "M1-1『两度小幅回升』", "JP_CPI_YOY 2025-01..2026-02 月环比上升次数", n_up, 2,
    lit="非逐月单调,2025-09、2025-10 两度小幅回升", text=M[0])
seq2 = [jpm[k] for k in sorted(jpm) if "2026-02" <= k <= "2026-10"]
n_dn = sum(1 for i in range(1, len(seq2)) if seq2[i] < seq2[i - 1])
add("G013", "⑦", "M1-1『总体回升』用词", "JP_CPI_YOY 2026-02..2026-10 月环比下降次数 / 末值>首值",
    (n_dn, seq2[-1] > seq2[0]), (">=1(非逐月)", True), ok=(n_dn >= 1 and seq2[-1] > seq2[0]),
    lit="此后总体回升至 2026-10 的 2.44", text=M[0], note="2026-04 一处回落(1.46→1.38),故用『总体』而非逐月")
mro_cp, dfr_cp = change_points("ECB_MRO"), change_points("ECB_DFR")
add("G014", "⑦", "M1-2 欧央行两次变更幅度", "ECB_MRO 窗内两次变更 (bp)",
    tuple(int(round(C.bp(c[2], c[1]))) for c in mro_cp[-2:]), (25, 25), lit="ECB 两次变更各 25bp", text=M[1])
m06 = [c for c in mro_cp if c[0] == "2026-06-17"][0], [c for c in dfr_cp if c[0] == "2026-06-17"][0]
m09 = [c for c in mro_cp if c[0] == "2026-09-16"][0], [c for c in dfr_cp if c[0] == "2026-09-16"][0]
add("G015", "⑦", "M1-2 2026-06-17 变更前后", SNAP + ":series_store.ECB_MRO/ECB_DFR 变更点 2026-06-17 (from,to)",
    ((m06[0][1], m06[0][2]), (m06[1][1], m06[1][2])), ((2.15, 2.4), (2.0, 2.25)),
    lit="2026-06-17 生效,MRO 2.15→2.4、DFR 2.0→2.25", text=M[1])
add("G016", "⑦", "M1-2 2026-09-16 变更前后", SNAP + ":series_store.ECB_MRO/ECB_DFR 变更点 2026-09-16 (from,to)",
    ((m09[0][1], m09[0][2]), (m09[1][1], m09[1][2])), ((2.4, 2.65), (2.25, 2.5)),
    lit="2026-09-16 生效,MRO 2.4→2.65、DFR 2.25→2.5", text=M[1])
ecb_cal = [e for e in cal["entries"] if "ECB" in str(e.get("metric_id", ""))]
add("G017", "⑦", "M1-2 推断标注", "冻结日历 ECB 实录条数 / 决议日须标【推断】",
    (len(ecb_cal), "【推断】" in M[1]), (0, True), lit="冻结发布日历无 ECB 实录", text=M[1])
jcal = [e for e in cal["entries"] if e.get("metric_id") == "JP_POLICY_TARGET"]
jcp = [c for c in change_points("JP_POLICY_RATE") if C.D(c[0]) > C.add_months(CD, -12)]
with_rec = [c[0] for c in jcp if any(0 < (C.D(c[0]) - C.D(e["decision_date"])).days <= 45 for e in jcal if e.get("decision_date"))]
add("G018", "⑦", "M1-2 其余台阶无实录", "JP_POLICY_RATE 窗内 6 个变动点中,前 45 天内有日历 JP_POLICY_TARGET 决议实录者",
    with_rec, ["2026-10-01"], lit="其余月均台阶在发布日历无对应实录,不作相容性判断", text=M[1])
lv = [jd["l3"]["mechanism_chains"][0]["links"][i]["evidence_level"] for i in range(4)]
add("G019", "⑦", "机制链证据分级", "l3.mechanism_chains[0].links[*].evidence_level", lv, ["E1", "E1", "E2", "E2"])
add("G020", "⑦", "E2 环假设标注", "links[2].text 以『传导【假设】』起始 / links[3].text 归因含【假设·归因】",
    (M[2].startswith("传导【假设】"), "【假设·归因】" in M[3]), (True, True))
add("G021", "⑦", "E1 环事实位措辞", "links[0..1].text 不含『【假设】』", ("【假设】" in M[0], "【假设】" in M[1]), (False, False),
    note="E1 环只含【事实】与【推断】标注,推断(决议日回推)逐处标明")
# FX month window
add("G022", "⑦", "M1-3 EURUSD 窗起", src("EURUSD", "2026-10-23"), v("EURUSD", "2026-10-23"), 1.1221,
    lit="EURUSD 由 1.1221 降至 1.0970(-2.24%)", text=M[2])
add("G023", "⑦", "M1-3 EURUSD 11-20 收盘", src("EURUSD", "2026-11-20"), v("EURUSD", "2026-11-20"), 1.0970,
    lit="EURUSD 由 1.1221 降至 1.0970(-2.24%)", text=M[2])
add("G024", "⑦", "M1-3 EURUSD 月窗变动", "EURUSD 2026-10-23→2026-11-20", r(pc("EURUSD", "2026-10-23", "2026-11-20")), -2.24,
    lit="EURUSD 由 1.1221 降至 1.0970(-2.24%)", text=M[2])
add("G025", "⑦", "M1-3 USDJPY 窗起", src("USDJPY", "2026-10-23"), v("USDJPY", "2026-10-23"), 156.494,
    lit="USDJPY 由 156.494 升至 159.707(+2.05%)", text=M[2])
add("G026", "⑦", "M1-3 USDJPY 11-20 收盘", src("USDJPY", "2026-11-20"), v("USDJPY", "2026-11-20"), 159.707,
    lit="USDJPY 由 156.494 升至 159.707(+2.05%)", text=M[2])
add("G027", "⑦", "M1-3 USDJPY 月窗变动", "USDJPY 2026-10-23→2026-11-20", r(pc("USDJPY", "2026-10-23", "2026-11-20")), 2.05,
    lit="USDJPY 由 156.494 升至 159.707(+2.05%)", text=M[2])
add("G028", "⑦", "M1-3 DXY 窗起", src("DXY", "2026-10-23"), v("DXY", "2026-10-23"), 101.81,
    lit="DXY 由 101.81 升至 103.81(+1.96%)", text=M[2])
add("G029", "⑦", "M1-3 DXY 11-20 收盘", src("DXY", "2026-11-20"), v("DXY", "2026-11-20"), 103.81,
    lit="DXY 由 101.81 升至 103.81(+1.96%)", text=M[2])
add("G030", "⑦", "M1-3 DXY 月窗变动", "DXY 2026-10-23→2026-11-20", r(pc("DXY", "2026-10-23", "2026-11-20")), 1.96,
    lit="DXY 由 101.81 升至 103.81(+1.96%)", text=M[2])
add("G031", "⑦", "M1-3 EURUSD 11-23 盘中", src("EURUSD", "2026-11-23"), v("EURUSD", "2026-11-23"), 1.0940,
    lit="EURUSD 1.0940(-2.51%)", text=M[2])
add("G032", "⑦", "M1-3 EURUSD 至截止变动", "EURUSD 2026-10-23→2026-11-23", r(pc("EURUSD", "2026-10-23", "2026-11-23")), -2.51,
    lit="EURUSD 1.0940(-2.51%)", text=M[2])
add("G033", "⑦", "M1-3 USDJPY 11-23 盘中", src("USDJPY", "2026-11-23"), v("USDJPY", "2026-11-23"), 159.347,
    lit="USDJPY 159.347(+1.82%)", text=M[2])
add("G034", "⑦", "M1-3 USDJPY 至截止变动", "USDJPY 2026-10-23→2026-11-23", r(pc("USDJPY", "2026-10-23", "2026-11-23")), 1.82,
    lit="USDJPY 159.347(+1.82%)", text=M[2])
add("G035", "⑦", "M1-3 DXY 11-23 盘中", src("DXY", "2026-11-23"), v("DXY", "2026-11-23"), 104.079,
    lit="DXY 104.079(+2.23%)", text=M[2])
add("G036", "⑦", "M1-3 DXY 至截止变动", "DXY 2026-10-23→2026-11-23", r(pc("DXY", "2026-10-23", "2026-11-23")), 2.23,
    lit="DXY 104.079(+2.23%)", text=M[2])
x0 = v("EURUSD", "2026-10-23") * v("USDJPY", "2026-10-23")
x1 = v("EURUSD", "2026-11-20") * v("USDJPY", "2026-11-20")
x2 = v("EURUSD", "2026-11-23") * v("USDJPY", "2026-11-23")
add("G037", "⑦", "M1-3 EURJPY 合成 10-23", "EURUSD×USDJPY @2026-10-23 (%.4f×%.4f=%.5f)" % (v("EURUSD", "2026-10-23"), v("USDJPY", "2026-10-23"), x0),
    r(x0), 175.61, lit="2026-10-23 收盘 175.61", text=M[2])
add("G038", "⑦", "M1-3 EURJPY 合成 11-20", "EURUSD×USDJPY @2026-11-20 (%.4f)" % x1, r(x1), 175.19,
    lit="2026-11-20 收盘 175.19(-0.24%)", text=M[2])
add("G039", "⑦", "M1-3 EURJPY 合成月窗变动", "合成交叉盘 2026-10-23→2026-11-20 (全精度)", r(C.pct(x1, x0)), -0.24,
    lit="2026-11-20 收盘 175.19(-0.24%)", text=M[2])
add("G040", "⑦", "M1-3 EURJPY 合成 11-23", "EURUSD×USDJPY @2026-11-23 (%.5f)" % x2, r(x2), 174.32,
    lit="至 2026-11-23 盘中 174.32(较 10-23 -0.73%)", text=M[2])
add("G041", "⑦", "M1-3 EURJPY 至截止变动", "合成交叉盘 2026-10-23→2026-11-23 (全精度 %.4f%%)" % C.pct(x2, x0),
    r(C.pct(x2, x0)), -0.73, lit="至 2026-11-23 盘中 174.32(较 10-23 -0.73%)", text=M[2])
add("G042", "⑦", "M1-3 EURJPY 至截止变动(展示值路径)", "174.32/175.61−1", r(C.pct(174.32, 175.61)), -0.73,
    note="两条舍入路径(全精度/展示值)结果相同")
add("G043", "⑦", "M1-3 交叉盘缺席", "series_store 含 EURJPY 键", [k for k in ss if "EURJPY" in k], [],
    lit="EURJPY 交叉盘不在证据面", text=M[2])
# assets, same-day close window 2026-10-23 -> 2026-11-20
add("G044", "⑦", "M1-4 同日收盘口径窗端点", "SPX/NIKKEI225/DAX/CAC40/VIX 在 2026-10-23 与 2026-11-20 均有观测",
    all(v(m, d) is not None for m in ("SPX", "NIKKEI225", "DAX", "CAC40", "VIX") for d in ("2026-10-23", "2026-11-20")), True,
    lit="近一月同日收盘口径(窗起 2026-10-23 收盘→2026-11-20 收盘)", text=M[3])
add("G045", "⑦", "M1-4 SPX", "SPX 2026-10-23→2026-11-20 (%.2f→%.2f)" % (v("SPX", "2026-10-23"), v("SPX", "2026-11-20")),
    r(pc("SPX", "2026-10-23", "2026-11-20")), -9.36, lit="SPX 下跌 9.36%", text=M[3])
add("G046", "⑦", "M1-4 NIKKEI225", "NIKKEI225 2026-10-23→2026-11-20 (%.2f→%.2f)" % (v("NIKKEI225", "2026-10-23"), v("NIKKEI225", "2026-11-20")),
    r(pc("NIKKEI225", "2026-10-23", "2026-11-20")), -9.98, lit="NIKKEI225 下跌 9.98%", text=M[3])
add("G047", "⑦", "M1-4 DAX", "DAX 2026-10-23→2026-11-20 (%.2f→%.2f)" % (v("DAX", "2026-10-23"), v("DAX", "2026-11-20")),
    r(pc("DAX", "2026-10-23", "2026-11-20")), -1.50, lit="DAX 下跌 1.50%", text=M[3])
add("G048", "⑦", "M1-4 CAC40", "CAC40 2026-10-23→2026-11-20 (%.2f→%.2f)" % (v("CAC40", "2026-10-23"), v("CAC40", "2026-11-20")),
    r(pc("CAC40", "2026-10-23", "2026-11-20")), 1.86, lit="CAC40 上涨 1.86%", text=M[3])
add("G049", "⑦", "M1-4 VIX 窗起", src("VIX", "2026-10-23"), v("VIX", "2026-10-23"), 19.45, lit="VIX 由 19.45 升至 35.89(+84.5%)", text=M[3])
add("G050", "⑦", "M1-4 VIX 11-20 收盘", src("VIX", "2026-11-20"), v("VIX", "2026-11-20"), 35.89, lit="VIX 由 19.45 升至 35.89(+84.5%)", text=M[3])
add("G051", "⑦", "M1-4 VIX 月窗幅度", "VIX 2026-10-23→2026-11-20", r(pc("VIX", "2026-10-23", "2026-11-20"), 1), 84.5,
    lit="VIX 由 19.45 升至 35.89(+84.5%)", text=M[3])
PATH = "11-13 19.30→11-16 22.91→11-17 25.46→11-18 24.56→11-19 28.44→11-20 35.89"
k = 52
for d, val in (("11-13", 19.30), ("11-16", 22.91), ("11-17", 25.46), ("11-18", 24.56), ("11-19", 28.44), ("11-20", 35.89)):
    add("G%03d" % k, "⑦", "M1-4 VIX 末六日路径", src("VIX", "2026-" + d), v("VIX", "2026-" + d), val, lit=PATH, text=M[3]); k += 1
add("G%03d" % k, "⑦", "M1-4『末六个交易日』", "VIX 序列 ≤2026-11-20 的最后六个观测日", tds("VIX", "2026-11-20", 6),
    ["2026-11-13", "2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19", "2026-11-20"], lit="末六个交易日收盘路径", text=M[3]); k += 1
add("G%03d" % k, "⑦", "M1-4『末五个交易日』", "VIX 序列 2026-11-13 之后 ≤2026-11-20 的观测日数", len(tds("VIX", "2026-11-20")) - len(tds("VIX", "2026-11-13")),
    5, lit="跳升集中于末五个交易日(2026-11-13→2026-11-20,19.30→35.89)", text=M[3]); k += 1
add("G%03d" % k, "⑦", "M1-4 引擎回贴 SPX", src("SPX", "2026-11-23"), v("SPX", "2026-11-23"), 7203.85, lit="SPX -5.51%(7203.85,盘中)", text=M[3]); k += 1
add("G%03d" % k, "⑦", "M1-4 引擎回贴 DAX", src("DAX", "2026-11-23"), v("DAX", "2026-11-23"), 25209.45, lit="DAX +0.11%(25209.45,盘中)", text=M[3]); k += 1
add("G%03d" % k, "⑦", "M1-4 引擎回贴 NIKKEI225", src("NIKKEI225", "2026-11-20"), v("NIKKEI225", "2026-11-20"), 56436.65,
    lit="NIKKEI225 -9.98%(56436.65,2026-11-20 收盘)", text=M[3]); k += 1
add("G%03d" % k, "⑦", "M1-4 引擎回贴 VIX", src("VIX", "2026-11-23"), v("VIX", "2026-11-23"), 27.01, lit="VIX +38.87%(27.01,盘中", text=M[3]); k += 1
PREC = "2026-11-04→11-05 VIX 收盘 16.61→28.18(+69.66%),至 11-11 回落至 17.49(四个交易日,较 11-05 -37.93%),同期 SPX 11-05 -4.36%,下一交易日 NIKKEI225 11-06 -5.96%"
add("G%03d" % k, "⑦", "M1-4 先例 VIX 11-04", src("VIX", "2026-11-04"), v("VIX", "2026-11-04"), 16.61, lit=PREC, text=M[3]); k += 1
add("G%03d" % k, "⑦", "M1-4 先例 VIX 11-05", src("VIX", "2026-11-05"), v("VIX", "2026-11-05"), 28.18, lit=PREC, text=M[3]); k += 1
add("G%03d" % k, "⑦", "M1-4 先例 VIX 单日", "VIX 2026-11-04→2026-11-05", r(pc("VIX", "2026-11-04", "2026-11-05")), 69.66, lit=PREC, text=M[3]); k += 1
add("G%03d" % k, "⑦", "M1-4 先例 VIX 11-11", src("VIX", "2026-11-11"), v("VIX", "2026-11-11"), 17.49, lit=PREC, text=M[3]); k += 1
d5 = tds("VIX", "2026-11-11")
add("G%03d" % k, "⑦", "M1-4 先例『四个交易日』", "VIX 2026-11-05 之后至 2026-11-11 的观测日", len(d5) - 1 - d5.index("2026-11-05"), 4, lit=PREC, text=M[3]); k += 1
add("G%03d" % k, "⑦", "M1-4 先例 VIX 回落", "VIX 2026-11-05→2026-11-11", r(pc("VIX", "2026-11-05", "2026-11-11")), -37.93, lit=PREC, text=M[3]); k += 1
add("G%03d" % k, "⑦", "M1-4 先例 SPX 11-05", "SPX 2026-11-04→2026-11-05 (%.4f%%)" % pc("SPX", "2026-11-04", "2026-11-05"),
    r(pc("SPX", "2026-11-04", "2026-11-05")), -4.36, lit=PREC, text=M[3]); k += 1
add("G%03d" % k, "⑦", "M1-4 先例 NIKKEI 11-06", "NIKKEI225 2026-11-05→2026-11-06", r(pc("NIKKEI225", "2026-11-05", "2026-11-06")), -5.96, lit=PREC, text=M[3]); k += 1
add("G%03d" % k, "⑦", "M1-4『下一交易日』", "NIKKEI225 2026-11-05 之后的下一观测日",
    [d for d in tds("NIKKEI225", "2026-11-20") if d > "2026-11-05"][0], "2026-11-06",
    lit="下一交易日 NIKKEI225 11-06", text=M[3]); k += 1
JUMP = "2026-11-16、2026-11-20,当日 VIX +18.70%/+26.20%,为窗内两个最大单日跳升日"
vd = tds("VIX", "2026-11-20")
daily = {vd[i]: C.pct(v("VIX", vd[i]), v("VIX", vd[i - 1])) for i in range(1, len(vd)) if vd[i - 1] >= "2026-11-13"}
add("G%03d" % k, "⑦", "M1-4 发布日 VIX 11-16", "VIX 2026-11-13→2026-11-16 (%.4f%%)" % daily["2026-11-16"], r(daily["2026-11-16"]), 18.70, lit=JUMP, text=M[3]); k += 1
add("G%03d" % k, "⑦", "M1-4 发布日 VIX 11-20", "VIX 2026-11-19→2026-11-20 (%.4f%%)" % daily["2026-11-20"], r(daily["2026-11-20"]), 26.20, lit=JUMP, text=M[3]); k += 1
add("G%03d" % k, "⑦", "M1-4『窗内两个最大单日跳升日』", "跳升窗(2026-11-16..2026-11-20)单日涨幅前二",
    sorted(sorted(daily, key=lambda d: -daily[d])[:2]), ["2026-11-16", "2026-11-20"], lit=JUMP, text=M[3],
    note="窗=跳升窗; 若取近一月窗则 2026-11-05(+69.66%)最大,原文『跳升窗内』限定成立"); k += 1
DEC = "2026-11-13→2026-11-20: SPX -8.61%、NIKKEI225 -7.70%、DAX -7.28%、CAC40 -5.27%"
dec = {m: r(pc(m, "2026-11-13", "2026-11-20")) for m in ("SPX", "NIKKEI225", "DAX", "CAC40")}
for m, val in (("SPX", -8.61), ("NIKKEI225", -7.70), ("DAX", -7.28), ("CAC40", -5.27)):
    add("G%03d" % k, "⑦", "M1-4/对质环3 跳升窗股指", "%s 2026-11-13→2026-11-20 (%.4f%%)" % (m, pc(m, "2026-11-13", "2026-11-20")),
        dec[m], val, lit=DEC, text=M[3]); k += 1
add("G%03d" % k, "⑦", "M1-4『四地股指跌幅均不深于美股』", "跳升窗跌幅比较", min(dec.values()) == dec["SPX"] and dec["SPX"] < 0, True,
    lit="但窗内四地股指跌幅均不深于美股", text=M[3]); k += 1
fx_mv = {}
for m in ("EURUSD", "USDJPY"):
    dd = tds(m, "2026-11-20")
    for d in ("2026-11-16", "2026-11-20"):
        fx_mv[(m, d)] = abs(C.pct(v(m, d), v(m, dd[dd.index(d) - 1])))
add("G%03d" % k, "⑦", "M1-4 发布日汇市单日变动上限", "EURUSD/USDJPY 2026-11-16 与 2026-11-20 单日变动绝对值最大 (%.4f%%)" % (max(fx_mv.values())),
    max(fx_mv.values()) <= 0.23, True, lit="两日欧元、日元对美元单日变动幅度不超过 0.23%", text=M[3],
    note="逐项: " + ", ".join("%s@%s %.4f%%" % (kk[0], kk[1], vv) for kk, vv in sorted(fx_mv.items()))); k += 1
pdf = plan["policy_doc_facts"]
add("G%03d" % k, "⑦", "M1-4 FOMC 纪要", "research_plan.policy_doc_facts FOMC-MINUTES-2026-10.published_on",
    [x["published_on"] for x in pdf if x["doc_id"] == "FOMC-MINUTES-2026-10"], ["2026-11-18"],
    lit="FOMC 2026年10月会议纪要 2026-11-18 发布", text=M[3]); k += 1
for lab, d0, d1, val, lit in (("距最近政策日", "2026-10-30", "2026-11-13", 14, "14 天"), ("距 ECB 最近生效日(起点)", "2026-09-16", "2026-11-13", 58, "58 天"),
                              ("距最近政策日(终点)", "2026-10-30", "2026-11-20", 21, "21 天"), ("距 ECB 最近生效日(终点)", "2026-09-16", "2026-11-20", 65, "65 天")):
    add("G%03d" % k, "⑦", "对质环3 " + lab, "%s − %s (天)" % (d1, d0), (C.D(d1) - C.D(d0)).days, val,
        lit=("距最近政策日 2026-10-30(BOJ 维持决议,无变更)14 天、距 ECB 最近生效日 2026-09-16 58 天" if val in (14, 58) else "至跳升终点 2026-11-20 为 21 天、65 天"),
        text=TLN[2]); k += 1
add("G%03d" % k, "⑦", "对质环3 纪要发布后 VIX", "VIX 2026-11-18/11-19/11-20 收盘",
    (r(v("VIX", "2026-11-18")), r(v("VIX", "2026-11-19")), r(v("VIX", "2026-11-20"))), (24.56, 28.44, 35.89),
    lit="发布当日及其后两个交易日 VIX 收盘 24.56、28.44、35.89", text=TLN[2]); k += 1


def ea_visible(asof, mode):
    """latest EA_HICP_YOY observation month visible on asof under the engine rule (month end +16d)
    or under the calendar's two-tier form (flash on the first day of the next month)."""
    best = None
    for ym in sorted(eam):
        y, m = int(ym[:4]), int(ym[5:7])
        pub = C.add_days(C.month_end(y, m), 16) if mode == "rule" else C.D("%04d-%02d-01" % (y + m // 12, m % 12 + 1))
        if pub <= asof:
            best = (ym, eam[ym], pub)
    return best


VL = TLN[0]
add("G%03d" % k, "⑦", "对质环1 决议日前可见(2026-06-11)", "EA_HICP_YOY 推定规则(月末+16天): 发布日≤2026-06-11 的最新观测月", ea_visible(C.D("2026-06-11"), "rule")[:2],
    ("2026-04", 3.0), lit="决议日(回推 2026-06-11)前可见 2026-04=3.0", text=VL); k += 1
add("G%03d" % k, "⑦", "对质环1 生效日前可见(2026-06-17)", "同上 发布日≤2026-06-17", ea_visible(C.D("2026-06-17"), "rule")[:2],
    ("2026-05", 3.2), lit="生效日前可见 2026-05=3.2", text=VL); k += 1
add("G%03d" % k, "⑦", "对质环1 决议日前可见(2026-09-10)", "同上 发布日≤2026-09-10", ea_visible(C.D("2026-09-10"), "rule")[:2],
    ("2026-07", 2.9), lit="决议日(回推 2026-09-10)前可见 2026-07=2.9", text=VL); k += 1
add("G%03d" % k, "⑦", "对质环1 生效日前可见(2026-09-16)", "同上 发布日≤2026-09-16", ea_visible(C.D("2026-09-16"), "rule")[:2],
    ("2026-08", 3.2), lit="生效日前可见 2026-08=3.2", text=VL); k += 1
add("G%03d" % k, "⑦", "对质环1 发布日=生效日同日", "EA_HICP_YOY 2026-08 观测月推定发布日", ea_visible(C.D("2026-09-16"), "rule")[2].isoformat(),
    "2026-09-16", lit="发布日 2026-09-16 与生效日同日,先后时刻不可分", text=VL); k += 1
add("G%03d" % k, "⑦", "对质环1 日历两档形态(第一次)", "快报=次月首日: ≤2026-06-11 可见最新观测月", ea_visible(C.D("2026-06-11"), "flash")[:2],
    ("2026-05", 3.2), lit="两次变更决议日前可见读数为 2026-05 的 3.2 与 2026-08 的 3.2", text=VL); k += 1
add("G%03d" % k, "⑦", "对质环1 日历两档形态(第二次)", "快报=次月首日: ≤2026-09-10 可见最新观测月", ea_visible(C.D("2026-09-10"), "flash")[:2],
    ("2026-08", 3.2), lit="两次变更决议日前可见读数为 2026-05 的 3.2 与 2026-08 的 3.2", text=VL); k += 1
vis = [3.0, 3.2, 2.9, 3.2]
add("G%03d" % k, "⑦", "对质环1『变更前读数均高于 2026-02 的 1.9』", "四个变更前可见读数 vs EA_HICP_YOY[2026-02]=%s" % eam["2026-02"],
    all(x > eam["2026-02"] for x in vis), True, lit="两次变更前读数均高于 2026-02 的 1.9", text=VL); k += 1
add("G%03d" % k, "⑦", "对质环1 维持天数", "2025-06-11 → 2026-06-17 (天)", (C.D("2026-06-17") - C.D("2025-06-11")).days, 371,
    lit="维持 2.15/2.0 共 371 天", text=VL); k += 1
add("G%03d" % k, "⑦", "对质环1 维持期无变更", "ECB_MRO/ECB_DFR 在 (2025-06-11, 2026-06-17) 内变更点",
    [c[0] for c in mro_cp + dfr_cp if "2025-06-11" < c[0] < "2026-06-17"], [], lit="维持 2.15/2.0 共 371 天", text=VL); k += 1
add("G%03d" % k, "⑦", "对质环1 维持期读数", "EA_HICP_YOY 2026-01 / 2026-04", (eam["2026-01"], eam["2026-04"]), (1.7, 3.0),
    lit="其间读数已由 2026-01 的 1.7 升至 2026-04 的 3.0 而未触发变更", text=VL); k += 1
add("G%03d" % k, "⑦", "对质环1『2.9 低于 2026-05 峰值 3.2』", "决议日前可见读数 2.9 vs 2026-05=3.2 且 2026-05 为局部峰值(%s/%s/%s)" % (eam["2026-04"], eam["2026-05"], eam["2026-06"]),
    (2.9 < eam["2026-05"], eam["2026-05"] > eam["2026-04"] and eam["2026-05"] > eam["2026-06"]), (True, True),
    lit="决议日前可见读数 2.9 低于 2026-05 峰值 3.2", text=VL); k += 1
add("G%03d" % k, "⑦", "对质环1 样本数", "ECB_MRO 近十二月窗内变更次数", len([c for c in mro_cp if C.D(c[0]) > C.add_months(CD, -12)]), 2,
    lit="读数驱动与程序驱动均与观测相容,n=2", text=VL); k += 1
win_ev = [c[0] for c in mro_cp + dfr_cp + change_points("DFEDTARU") if "2026-10-23" <= c[0] <= cutoff]
win_ev += [c[0] for c in change_points("JP_POLICY_RATE") if "2026-10-23" <= c[0] <= cutoff]
win_ev += [e["entry_id"] for e in jcal if e.get("decision_date") and "2026-10-23" <= e["decision_date"] <= cutoff and e.get("kind") == "policy_decision"]
add("G%03d" % k, "⑦", "对质环2 窗内无政策变动点", "ECB/Fed 序列变更点、JP_POLICY_RATE 变动点、日央行决议实录 落在 [2026-10-23, 2026-11-23]", sorted(win_ev), [],
    lit="窗内三地均无政策利率变动点", text=TLN[1],
    note="日央行 2026-10-30 为维持决议(kind=policy_maintenance),不构成变动点"); k += 1
eidx_rows = rep["evidence_index"]
eidx = {x["ref"] for x in eidx_rows}
for i in range(3):
    dm = TL[i]["distinguishing_metric"]
    add("G%03d" % k, "⑦", "对质环%d 区分指标在场" % (i + 1), "区分指标 %s 在 series_store / 证据索引" % dm,
        (dm in ss, sorted(x for x in eidx if x.startswith(dm + "@"))[:1]), (True, ["%s@2026-11-23" % dm] if dm != "EA_HICP_YOY" else ["EA_HICP_YOY@2026-10-01"]),
        note="区分指标须在场且两解释预期方向不同(见 PROSE 六查)"); k += 1

# ================================================================ ⑧ analog
an = None
for st in rep["steps"]:
    if st.get("step") == "S6_analog":
        an = st
cdd = an["envelope"]["data"]["candidates"]
top0 = an["envelope"]["data"]["top"][0]
add("H001", "⑧", "类比 扫描数", "report.json:steps[S6_analog].envelope.data.candidates.scanned", cdd["scanned"], 1871,
    lit="扫描 1871 个候选月", text=HN)
add("H002", "⑧", "类比 有效数", "candidates.valid", cdd["valid"], 74, lit="有效 74", text=HN)
add("H003", "⑧", "类比 TOP1 候选月", "envelope.data.top[0].candidate_month", top0["candidate_month"], "2025-03",
    lit="TOP1 候选月 2025-03", text=HN)
add("H004", "⑧", "类比 TOP1 距离", "envelope.data.top[0].distance", C.rnd(top0["distance"], 3), 0.727, lit="距离 0.727", text=HN)
hp = T("reader_map.history_periods")
add("H005", "⑧", "历史类比段数", "reader_map.history_periods", len(hp), 0, lit="历史类比 0 段(契约允许 0..3 段,零段如实写明)", text=HN)
add("H006", "⑧", "类比能力已执行", "steps[S6_analog].ok / executed", (an["ok"], an["executed"]), (True, True),
    lit="S6_analog: 扫描", text=HN)


def _walk(o, needle, path="", out=None):
    if out is None:
        out = []
    if isinstance(o, str):
        if needle in o:
            out.append(path)
    elif isinstance(o, dict):
        for kk, vv in o.items():
            _walk(vv, needle, path + "." + kk, out)
    elif isinstance(o, list):
        for ii, vv in enumerate(o):
            _walk(vv, needle, path + "[%d]" % ii, out)
    return out


add("H007", "⑧", "零段类比=不引事后结果", "agent_judgment.json 中出现候选月『2025-03』的字段路径", _walk(jd, "2025-03"),
    [".reader_map.history_zero_case_note"], note="候选月仅出现于零段注记,无任何『随后 N 个月结果』数字",
    lit="不以未核验的事后结果充数", text=HN)


# ================================================================ ⑨ scenarios
ea_dec_pub = C.add_days(C.month_end(2026, 12), 16).isoformat()
jp_dec_pub = C.add_days(C.month_end(2026, 12), 20).isoformat()
add("I001", "⑨", "S1 时限晚于入档", "2026-12 观测月按推定规则发布日 EA=%s / JP=%s vs deadline" % (ea_dec_pub, jp_dec_pub),
    (ea_dec_pub < S1["trigger"]["deadline"], jp_dec_pub < S1["trigger"]["deadline"]), (True, True),
    lit="2027-01 入档,早于时限 2027-02-15", text=S1["scenario"])
add("I002", "⑨", "S2 时限", "同上 vs S2 deadline", S2["trigger"]["deadline"], "2027-02-15", lit="2027-01 入档,早于时限 2027-02-15", text=S2["scenario"])
for sid, sc in (("S1", S1), ("S2", S2)):
    fm = sc["falsification"]["metric_id"]
    add("I%03d" % (3 + (sid == "S2")), "⑨", "%s 证伪指标可观测" % sid, "falsification.metric_id 在注册表与证据索引",
        (fm in regm, fm in ss, any(x.startswith(fm + "@") for x in eidx)), (True, True, True))
    add("I%03d" % (5 + (sid == "S2")), "⑨", "%s 次证伪指标可观测" % sid, "falsification.secondary_metric_ids 在注册表",
        [x in regm for x in sc["falsification"]["secondary_metric_ids"]], [True])
add("I007", "⑨", "触发用 VIX 可观测", "VIX 在 series_store / 证据索引", ("VIX" in ss, "VIX@2026-11-23" in eidx), (True, True),
    lit="收盘高于 30", text=S1["trigger"]["condition"])
last_m = (max(C.monthly(ss, "EA_HICP_YOY")), max(C.monthly(ss, "JP_CPI_YOY")))
add("I008", "⑨", "情景尚未被截止日数据判定", "两序列在快照内的最后观测月(2026-11/2026-12 读数截止日尚未发布)", last_m, ("2026-10", "2026-10"),
    lit="观测月 2026-11 与 2026-12", text=S1["falsification"]["threshold"])
add("I009", "⑨", "阈值与截止日读数相容", "截止日读数 EA=%s(触发≥4.0/证伪<3.5) JP=%s(≥2.0/<2.0) VIX 11-20 收盘=%s(>30/<25)" % (eam["2026-10"], jpm["2026-10"], v("VIX", "2026-11-20")),
    (eam["2026-10"] >= 4.0, jpm["2026-10"] >= 2.0, v("VIX", "2026-11-20") > 30), (True, True, True),
    note="截止日读数落在两情景之间(未决),两情景方向互补")
add("I010", "⑨", "两情景方向互补", "S1『维持 3.5% 以上/维持 2.0% 以上』 vs S2『回落至 3.0% 以下/回落至 2.0% 以下』",
    ("维持 3.5% 以上" in S1["scenario"], "回落至 3.0% 以下" in S2["scenario"], "回落至 2.0% 以下" in S2["scenario"]), (True, True, True))
add("I011", "⑨", "S2 中间区间如实", "S2 证伪阈值 3.5 与触发阈值 3.0 之间既不触发也不证伪", "3.0%–3.5% 区间不触发亦不证伪" in S2["falsification"]["threshold"], True,
    lit="3.0%–3.5% 区间不触发亦不证伪", text=S2["falsification"]["threshold"])
add("I012", "⑨", "政策分量不可数值核验的披露", "冻结日历 ECB 实录条数 vs 情景披露", len(ecb_cal), 0,
    lit="冻结日历对欧央行零条实录,欧央行分量须待日历补录后方可核验", text=S1["falsification"]["threshold"])
for sid, sc, refs in (("S1", S1, S1["asset_direction"]["evidence_refs"]), ("S2", S2, S2["asset_direction"]["evidence_refs"])):
    add("I%03d" % (13 + (sid == "S2")), "⑨", "%s 证据引用可解析" % sid, "asset_direction.evidence_refs ⊂ 证据索引",
        [x for x in refs if x not in eidx], [], note="refs=" + ",".join(refs))
add("I015", "⑨", "S1 日本目标现值", "日历 RC-JP-BOJ-TARGET-2026-09.target_value vs 情景『目标现约 1.25%』",
    [e["target_value"] for e in jcal if e.get("kind") == "policy_decision"], [1.25], lit="目标现约 1.25%", text=S1["scenario"])
add("I016", "⑨", "S2 日本目标现值", "同上 vs S2『BOJ 维持目标约 1.25% 不变』",
    [e["target_value"] for e in jcal if e.get("kind") == "policy_maintenance"], [1.25], lit="BOJ 维持目标约 1.25% 不变", text=S2["scenario"])
add("I017", "⑨", "S2 资产方向所引近一月观察", "SPX/NIKKEI225/DAX/CAC40 2026-10-23→2026-11-20",
    tuple(r(pc(m, "2026-10-23", "2026-11-20")) for m in ("SPX", "NIKKEI225", "DAX", "CAC40")), (-9.36, -9.98, -1.50, 1.86),
    lit="SPX 下跌 9.36%、NIKKEI225 下跌 9.98%、DAX 下跌 1.50%、CAC40 上涨 1.86%", text=S2["asset_direction"]["direction"])

# ================================================================ ⑩ consistency
add("J001", "⑩", "总判断方向相反", "日本同比下降 / 欧元区同比上升",
    (jpm["2026-10"] < jpm["2025-10"], eam["2026-10"] > eam["2025-10"]), (True, True), lit="方向相反", text=HL)
add("J002", "⑩", "对质裁定取值", "transmission.links[*].face_off_verdict", sorted({t["face_off_verdict"] for t in TL}), ["尚不能区分"])
add("J003", "⑩", "对质裁定计数", "『尚不能区分』环数", sum(1 for t in TL if t["face_off_verdict"] == "尚不能区分"), 3,
    lit="尚不能区分 3", text=QN[1])
l3refs = []
for c in jd["l3"]["contradictions"]:
    l3refs += c["evidence_refs"]
for ch in jd["l3"]["mechanism_chains"]:
    for lk in ch["links"]:
        l3refs += lk["evidence_refs"]
add("J004", "⑩", "L3 引用条数", "contradictions[*].evidence_refs + mechanism_chains[*].links[*].evidence_refs", len(l3refs), 20,
    lit="共 20 条 snapshot_fact 引用", text=QN[0])
add("J005", "⑩", "L3 引用全部解析", "L3 引用不在证据索引者", sorted(set(x for x in l3refs if x not in eidx)), [],
    lit="零悬空引用", text=QN[0])
add("J006", "⑩", "L3 引用类型", "L3 引用在证据索引中的 kind 集合", sorted({x["kind"] for x in eidx_rows if x["ref"] in set(l3refs)}), ["snapshot_fact"])
l4refs = S1["asset_direction"]["evidence_refs"] + S2["asset_direction"]["evidence_refs"]
add("J007", "⑩", "L4 引用全部解析", "L4 evidence_refs 不在证据索引者", [x for x in l4refs if x not in eidx], [], note="L4 引用 %d 条" % len(l4refs))
add("J008", "⑩", "证据索引行数", "report.json:evidence_index 行数", len(eidx_rows), 60, lit="证据索引(60行)", text=DECL["basis"])
_kinds = {kk: sum(1 for x in eidx_rows if x["kind"] == kk) for kk in sorted({x["kind"] for x in eidx_rows})}
add("J009", "⑩", "证据索引构成", "kind 计数", _kinds, {"snapshot_fact": 35, "s3_envelope": 25}, ok=_kinds == {"snapshot_fact": 35, "s3_envelope": 25})
add("J010", "⑩", "点值格数", "research_plan.point_values.cells", len(plan["point_values"]["cells"]), 6, lit="点值格(6格)", text=DECL["basis"])
add("J011", "⑩", "日历版本", "release_calendar.json version / updated", ("v" + cal["version"], cal["updated"]), ("v1.5.0", "2026-11-21"),
    lit="发布日历(v1.5.0,2026-11-21 更新)", text=DECL["basis"])
MAP_MD = C.read_text(os.path.join(run_dir, "MAP_REPORT.md"))
_lv = (C.last_obs(ss, "ECB_MRO")[1], C.last_obs(ss, "ECB_DFR")[1], [e["target_value"] for e in jcal if e.get("kind") == "policy_decision"][0])
_ok12 = (_lv == (2.65, 2.5, 1.25) and all(s in HL for s in ("2.65%", "2.5%", "1.25%"))
         and all(s in C2 for s in ("二点六五", "2.5%", "一点二五")))
add("J012", "⑩", "总判断与 C2 政策水平一致", "ECB_MRO/ECB_DFR 现行水平与日历 BOJ 目标; 总判断(阿拉伯数字)与 C2(中文数字)两处字面",
    _lv, (2.65, 2.5, 1.25), ok=_ok12, lit="欧央行主要再融资利率 2.65%/存款便利利率 2.5%", text=HL,
    note="C2 字面: 『二点六五』『2.5%』『一点二五』; 总判断字面: 『2.65%』『2.5%』『1.25%』")
add("J013", "⑩", "读者报告 欧央行生效日滞后", "cutoff − 2026-09-16 = %d 天; MAP_REPORT 政策表" % (CD - C.D("2026-09-16")).days,
    "2026-09-16(距研究截止68天)" in MAP_MD, True, lit="2026-09-16(距研究截止68天)", text=MAP_MD)
REND = {"MAP_REPORT.md": C.squash(MAP_MD), "FULL_REPORT.md": C.squash(C.read_text(os.path.join(run_dir, "FULL_REPORT.md"))),
        "report.md": C.squash(C.read_text(os.path.join(run_dir, "report.md")))}


def render(pid, section, blocks, scope_out=False):
    """scope_out=True: the renderer's field coverage is an engine delivery-face observation,
    recorded with sev=SCOPE-OUT and kept out of the judgment mismatch count."""
    miss = [n for n, t in blocks if not any(C.squash(t) in txt for txt in REND.values())]
    nmap = sum(1 for n, t in blocks if C.squash(t) in REND["MAP_REPORT.md"])
    nfull = sum(1 for n, t in blocks if C.squash(t) in REND["FULL_REPORT.md"])
    nrep = sum(1 for n, t in blocks if C.squash(t) in REND["report.md"])
    comp = {"in_MAP": nmap, "in_FULL": nfull, "in_report": nrep, "not_rendered_anywhere": miss}
    note = "逐字在场(去空白): MAP %d/%d、FULL %d/%d、report %d/%d;三件均缺席 %d 段" % (
        nmap, len(blocks), nfull, len(blocks), nrep, len(blocks), len(miss))
    if scope_out:
        # engine delivery-face observation: record what the renderer leaves out; ok = observation confirmed
        add(pid, "⑩", "渲染一致性: " + section,
            "agent_judgment.json %s 共 %d 段原文(去空白)在 MAP/FULL/report 三件中的出现情况" % (section, len(blocks)),
            comp, "渲染面: 上述字段在三件报告中%s" % ("均缺席" if len(miss) == len(blocks) else "部分缺席"),
            ok=bool(miss), note=note, sev="SCOPE-OUT")
    else:
        add(pid, "⑩", "渲染一致性: " + section,
            "agent_judgment.json %s 共 %d 段原文(去空白)在 MAP/FULL/report 三件中的出现情况" % (section, len(blocks)),
            comp, {"not_rendered_anywhere": []}, ok=not miss, note=note)


render("J014", "总判断+三条矛盾陈述", [("headline", HL)] + [("C%d" % (i + 1), s) for i, s in enumerate((C1, C2, C3))])
render("J015", "机制链四环", [("M1-%d" % (i + 1), t) for i, t in enumerate(M)])
render("J016", "两地走位", [("EA", EA), ("JP", JP)])
tlb, tlb_note = [], []
for i, t in enumerate(TL):
    for key in ("observed_fact", "causal_hypothesis", "competing_explanation", "main_predicts", "competing_predicts", "face_off_verdict"):
        tlb.append(("TL%d.%s" % (i + 1, key), t[key]))
    tlb_note.append(("TL%d.verdict_note" % (i + 1), t["verdict_note"]))
render("J017", "传导对质三环(结构字段)", tlb)
render("J017X", "传导对质三环(verdict_note 裁定理由)", tlb_note, scope_out=True)
tnb, tnb_nar = [], []
for i in range(3):
    for key in ("first_mover", "follow_or_diverge"):
        tnb.append(("T%d.%s" % (i + 1, key), TN[i][key]))
    tnb_nar.append(("T%d.narrative" % (i + 1), TN[i]["narrative"]))
render("J018", "三转折(谁先变/跟进背离)", tnb)
render("J018X", "三转折(narrative 叙述)", tnb_nar, scope_out=True)
sb = [("S1.%s" % key, S1[key]) for key in ("scenario",)] + [("S1.direction", S1["asset_direction"]["direction"]), ("S1.threshold", S1["falsification"]["threshold"]), ("S1.condition", S1["trigger"]["condition"])]
sb += [("S2.%s" % key, S2[key]) for key in ("scenario",)] + [("S2.direction", S2["asset_direction"]["direction"]), ("S2.threshold", S2["falsification"]["threshold"]), ("S2.condition", S2["trigger"]["condition"])]
render("J019", "两情景", sb)
render("J020", "质量门注记六条", [("QN%d" % i, q) for i, q in enumerate(QN)], scope_out=True)
render("J021", "历史类比零段注记", [("history_zero_case_note", HN)])
add("J022", "⑩", "读者报告总判断逐字", "MAP_REPORT.md 含总判断原文(去空白)", C.squash(HL) in REND["MAP_REPORT.md"], True)
add("J023", "⑩", "C2 截止日盘中水平", "USDJPY/SPX/VIX @2026-11-23",
    (r(v("USDJPY", "2026-11-23")), r(v("SPX", "2026-11-23")), r(v("VIX", "2026-11-23"))), (159.35, 7203.85, 27.01),
    lit="USDJPY 水平为 159.35、SPX 水平为 7203.85、VIX 水平为 27.01", text=C2)
add("J024", "⑩", "C2 盘中口径", "三序列 2026-11-23 为快照日观测(非 11-20 收盘)",
    all(v(m, "2026-11-23") != v(m, "2026-11-20") for m in ("SPX", "VIX")), True, lit="均为 2026-11-23 盘中快照、非收盘价", text=C2)

out = B.save(out_dir)
bad = [r_ for r_ in B.rows if not r_["ok"]]
print("PART B: points=%d ok=%d mismatch=%d -> %s" % (len(B.rows), B.n_ok(), len(bad), out))
for r_ in bad:
    print("  MISMATCH", r_["id"], r_["cat"], r_["where"], "| computed=", str(r_["computed"])[:300], "| reported=", str(r_["reported"])[:200], "| lit_found=", r_["lit_found"], "|", str(r_["note"])[:200])
