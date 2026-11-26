#!/usr/bin/python3 -I
"""席位自写脚本 s12: ⑤ 三利率分解 + 资产月窗 + 汇率/油价读数(只读复算).

用法: /usr/bin/python3 -I s12_rates_assets.py <快照> <席位目录>
出处键: <快照>:series_store.<metric_id>[dates/values]
"""
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seatlib  # noqa: E402
from seatlib import Points, Store, load_json, month_shift, to_date  # noqa: E402

SNAP, SEAT = sys.argv[1], sys.argv[2]
snap = load_json(SNAP)
S = Store(snap)
SRC = "root_overlay/data/daily/research_snapshot_20261123.json:series_store"


def pct(a, b):
    """b 相对 a 的变动(%)."""
    return (b / a - 1.0) * 100.0


def bp(a, b):
    return (b - a) * 100.0


def val(mid, d):
    v = S.exact(mid, d)
    assert v is not None, f"{mid} 无 {d} 观测"
    return v


def last(mid, d):
    r = S.le(mid, d)
    return r


# ---------------------------------------------------------------- ⑤-A 三利率
P = Points("⑤", "三利率分解(名义/实际/盈亏平衡)与汇率面读数")
for mid in ("UST_10Y", "TIPS_10Y", "BEI_10Y"):
    dts, vals = S.series(mid)
    P.rows.append({"block": "⑤", "id": f"A0-{mid} 序列末端观测日/值", "source": f"{SRC}.{mid}",
                   "computed": [dts[-1], vals[-1], len(dts), dts[0]], "claim": "利率三序列止于 2026-11-19(BEI_10Y 止于 2026-11-20)",
                   "match": dts[-1] in ("2026-11-19", "2026-11-20") and vals[-1] > 0,
                   "detail": f"末观测 {dts[-1]}={vals[-1]}; 首观测 {dts[0]}; n={len(dts)}"})

# 1 个月共同交易日窗 2026-10-20 -> 2026-11-19
w1 = ("2026-10-20", "2026-11-19")
lv_to = {m: val(m, w1[1]) for m in ("UST_10Y", "TIPS_10Y", "BEI_10Y")}
lv_fr = {m: val(m, w1[0]) for m in ("UST_10Y", "TIPS_10Y", "BEI_10Y")}
P.add("A1-近一月窗名义 UST_10Y 变动(bp)", -8, bp(lv_fr["UST_10Y"], lv_to["UST_10Y"]), f"{SRC}.UST_10Y[{w1[0]}..{w1[1]}]",
      f"窗 {lv_fr['UST_10Y']}→{lv_to['UST_10Y']}")
P.add("A2-近一月窗实际 TIPS_10Y 变动(bp)", 11, bp(lv_fr["TIPS_10Y"], lv_to["TIPS_10Y"]), f"{SRC}.TIPS_10Y[{w1[0]}..{w1[1]}]",
      f"窗 {lv_fr['TIPS_10Y']}→{lv_to['TIPS_10Y']}")
P.add("A3-近一月窗盈亏平衡 BEI_10Y 变动(bp)", -19, bp(lv_fr["BEI_10Y"], lv_to["BEI_10Y"]), f"{SRC}.BEI_10Y[{w1[0]}..{w1[1]}]",
      f"窗 {lv_fr['BEI_10Y']}→{lv_to['BEI_10Y']}")
P.add("A4-近一月窗名义=实际+盈亏平衡 残差(bp)", 0,
      bp(lv_fr["UST_10Y"], lv_to["UST_10Y"]) - bp(lv_fr["TIPS_10Y"], lv_to["TIPS_10Y"]) - bp(lv_fr["BEI_10Y"], lv_to["BEI_10Y"]),
      f"{SRC}.UST_10Y/TIPS_10Y/BEI_10Y", "恒等残差", nd=1)
P.add("A5-期末水平 UST_10Y@2026-11-19", 5.04, lv_to["UST_10Y"], f"{SRC}.UST_10Y[2026-11-19]")
P.add("A6-期末水平 TIPS_10Y@2026-11-19", 2.88, lv_to["TIPS_10Y"], f"{SRC}.TIPS_10Y[2026-11-19]")
P.add("A7-期末水平 BEI_10Y@2026-11-19", 2.16, lv_to["BEI_10Y"], f"{SRC}.BEI_10Y[2026-11-19]")
P.add("A8-最新 BEI_10Y@2026-11-20", 2.15, val("BEI_10Y", "2026-11-20"), f"{SRC}.BEI_10Y[2026-11-20]")
P.add_bool("A9-名义水平=实际+盈亏平衡(同日 2026-11-19)", True,
           abs(val("UST_10Y", "2026-11-19") - val("TIPS_10Y", "2026-11-19") - val("BEI_10Y", "2026-11-19")) < 0.011,
           f"{SRC}.UST_10Y/TIPS_10Y/BEI_10Y[2026-11-19]",
           f"{val('UST_10Y', '2026-11-19')} vs {val('TIPS_10Y', '2026-11-19')}+{val('BEI_10Y', '2026-11-19')}")

# 3 个月窗 2026-08-19 -> 2026-11-19
w3 = ("2026-08-19", "2026-11-19")
for m, nm, cl in (("UST_10Y", "名义", 39), ("TIPS_10Y", "实际", 53), ("BEI_10Y", "盈亏平衡", -14)):
    a, b = val(m, w3[0]), val(m, w3[1])
    P.add(f"A10-三个月窗{nm} {m} 变动(bp)", cl, bp(a, b), f"{SRC}.{m}[{w3[0]}..{w3[1]}]", f"窗 {a}→{b}")
P.add("A11-三个月窗 BEI_10Y 窗启水平", 2.30, val("BEI_10Y", "2026-08-19"), f"{SRC}.BEI_10Y[2026-08-19]")
P.add("A12-三个月窗 BEI_10Y 窗末水平", 2.16, val("BEI_10Y", "2026-11-19"), f"{SRC}.BEI_10Y[2026-11-19]")
P.add("A13-三个月窗恒等残差(bp)", 0,
      bp(val("UST_10Y", w3[0]), val("UST_10Y", w3[1])) - bp(val("TIPS_10Y", w3[0]), val("TIPS_10Y", w3[1])) - bp(val("BEI_10Y", w3[0]), val("BEI_10Y", w3[1])),
      f"{SRC}.UST_10Y/TIPS_10Y/BEI_10Y", "恒等残差", nd=1)
P.add_bool("A14-三个月窗「名义上行由实际利率主导」(实际分量幅度>名义变动)", True,
           abs(bp(val("TIPS_10Y", w3[0]), val("TIPS_10Y", w3[1]))) > abs(bp(val("UST_10Y", w3[0]), val("UST_10Y", w3[1]))),
           f"{SRC}.TIPS_10Y/UST_10Y[{w3[0]}..{w3[1]}]", "实际 +53 > 名义 +39")

# 12 个月窗 2025-11-19 -> 2026-11-19
w12 = ("2025-11-19", "2026-11-19")
for m, nm, cl in (("UST_10Y", "名义", 91), ("TIPS_10Y", "实际", 102), ("BEI_10Y", "盈亏平衡", -11)):
    a, b = val(m, w12[0]), val(m, w12[1])
    P.add(f"A15-12个月窗{nm} {m} 变动(bp)", cl, bp(a, b), f"{SRC}.{m}[{w12[0]}..{w12[1]}]", f"窗 {a}→{b}")
P.add("A16-12个月窗恒等残差(bp)", 0,
      bp(val("UST_10Y", w12[0]), val("UST_10Y", w12[1])) - bp(val("TIPS_10Y", w12[0]), val("TIPS_10Y", w12[1])) - bp(val("BEI_10Y", w12[0]), val("BEI_10Y", w12[1])),
      f"{SRC}.UST_10Y/TIPS_10Y/BEI_10Y", "恒等残差", nd=1)
P.add_bool("A17-12个月窗「名义上行由实际利率主导」(实际分量幅度>名义变动)", True,
           abs(bp(val("TIPS_10Y", w12[0]), val("TIPS_10Y", w12[1]))) > abs(bp(val("UST_10Y", w12[0]), val("UST_10Y", w12[1]))),
           f"{SRC}.TIPS_10Y/UST_10Y[{w12[0]}..{w12[1]}]", "实际 +102 > 名义 +91")
P.add_bool("A18-三窗同为「实际上行、盈亏平衡回落」", True,
           all(bp(val("TIPS_10Y", a), val("TIPS_10Y", b)) > 0 and bp(val("BEI_10Y", a), val("BEI_10Y", b)) < 0 for a, b in (w1, w3, w12)),
           f"{SRC}.TIPS_10Y/BEI_10Y 三窗", "实际 +11/+53/+102bp; 盈亏平衡 -19/-14/-11bp")

# TIPS 2026-10-23 -> 2026-11-19
P.add("A19-同窗 TIPS_10Y 窗启 2026-10-23", 2.66, val("TIPS_10Y", "2026-10-23"), f"{SRC}.TIPS_10Y[2026-10-23]")
P.add("A20-同窗 TIPS_10Y 变动(bp, 2026-10-23→2026-11-19)", 22, bp(val("TIPS_10Y", "2026-10-23"), val("TIPS_10Y", "2026-11-19")),
      f"{SRC}.TIPS_10Y[2026-10-23..2026-11-19]")

# BEI_10Y 历史点: 12 个月窗内最低 / 更早上行段
dts, vals = S.series("BEI_10Y")
win12 = [(d, v) for d, v in zip(dts, vals) if "2025-11-20" <= d <= "2026-11-20"]
mn = min(win12, key=lambda x: x[1])
P.add_bool("A21-BEI_10Y 最新 2.15(2026-11-20)为 12 个月窗(2025-11-20..2026-11-20)最低", True,
           mn[0] == "2026-11-20" and abs(mn[1] - 2.15) < 0.006,
           f"{SRC}.BEI_10Y[2025-11-20..2026-11-20]", f"窗内最低 {mn[0]}={mn[1]}; 窗内观测数={len(win12)}")
win12b = [(d, v) for d, v in zip(dts, vals) if "2025-11-23" <= d <= "2026-11-23"]
mnb = min(win12b, key=lambda x: x[1])
P.add_bool("A21b-BEI_10Y 最新值为 12 个月窗(2025-11-23..2026-11-23)最低", True,
           mnb[0] == "2026-11-20" and abs(mnb[1] - 2.15) < 0.006,
           f"{SRC}.BEI_10Y[2025-11-23..2026-11-23]", f"窗内最低 {mnb[0]}={mnb[1]}; 观测数={len(win12b)}")
P.add("A22-BEI_10Y 2026-02-27", 2.25, val("BEI_10Y", "2026-02-27"), f"{SRC}.BEI_10Y[2026-02-27]")
P.add("A23-BEI_10Y 2026-05-04", 2.50, val("BEI_10Y", "2026-05-04"), f"{SRC}.BEI_10Y[2026-05-04]")
P.add_bool("A24-更早通胀上行段 BEI_10Y 上行(2026-02-27→2026-05-04)", True, val("BEI_10Y", "2026-05-04") > val("BEI_10Y", "2026-02-27"),
           f"{SRC}.BEI_10Y[2026-02-27, 2026-05-04]")
P.save("points_05a_rates.json")

# ---------------------------------------------------------------- ⑤-B 资产月窗
P = Points("⑤", "资产月窗(2026-10-23 → 最新)与收盘口径对照")
assets = [("SPX", "2026-11-23", 7623.68, 7203.85, -5.51), ("NIKKEI225", "2026-11-20", 62693.16, 56436.65, -9.98),
          ("GOLD_F", "2026-11-23", 4007.90, 3685.20, -8.05), ("DXY", "2026-11-23", 101.81, 104.079, 2.23),
          ("VIX", "2026-11-23", 19.45, 27.01, 38.87)]
for mid, d_to, v_fr, v_to, cl in assets:
    a, b = val(mid, "2026-10-23"), val(mid, d_to)
    P.add(f"B1-{mid} 窗启值 2026-10-23", v_fr, a, f"{SRC}.{mid}[2026-10-23]")
    P.add(f"B2-{mid} 窗末值 {d_to}", v_to, b, f"{SRC}.{mid}[{d_to}]")
    P.add(f"B3-{mid} 近一月变动(%)", cl, pct(a, b), f"{SRC}.{mid}[2026-10-23..{d_to}]")
    ld, lv = last(mid, "2026-11-23")
    P.add_bool(f"B4-{mid} 序列末观测={d_to}(截止日前最后观测)", True, ld == d_to, f"{SRC}.{mid}", f"≤2026-11-23 最后观测 {ld}")
P.add("B5-SPX 共同交易日窗 2026-10-23→2026-11-19 变动(%)", -5.87,
      pct(val("SPX", "2026-10-23"), val("SPX", "2026-11-19")), f"{SRC}.SPX[2026-10-23, 2026-11-19]")
P.add("B6-同日收盘口径 SPX 2026-10-23→2026-11-20 变动(%)", -9.36,
      pct(val("SPX", "2026-10-23"), val("SPX", "2026-11-20")), f"{SRC}.SPX[2026-10-23, 2026-11-20]")
P.add("B7-同日收盘口径 VIX 2026-10-23→2026-11-20 变动(%)", 84.52,
      pct(val("VIX", "2026-10-23"), val("VIX", "2026-11-20")), f"{SRC}.VIX[2026-10-23, 2026-11-20]")
P.add("B8-三个月收盘口径 SPX 2026-08-19→2026-11-20 变动(%)", -10.35,
      pct(val("SPX", "2026-08-19"), val("SPX", "2026-11-20")), f"{SRC}.SPX[2026-08-19, 2026-11-20]")
P.add("B9-三个月收盘口径 VIX 2026-08-19→2026-11-20 变动(%)", 141.03,
      pct(val("VIX", "2026-08-19"), val("VIX", "2026-11-20")), f"{SRC}.VIX[2026-08-19, 2026-11-20]")
P.add("B10-三个月收盘口径 VIX 窗启 2026-08-19", 14.89, val("VIX", "2026-08-19"), f"{SRC}.VIX[2026-08-19]")
P.add("B11-三个月收盘口径 VIX 窗末 2026-11-20", 35.89, val("VIX", "2026-11-20"), f"{SRC}.VIX[2026-11-20]")
P.add("B12-VIX 窗启 2026-10-23", 19.45, val("VIX", "2026-10-23"), f"{SRC}.VIX[2026-10-23]")
P.add("B13-VIX 窗末 2026-11-23", 27.01, val("VIX", "2026-11-23"), f"{SRC}.VIX[2026-11-23]")
P.add_bool("B14-「同窗 TIPS_10Y +53bp(三个月收盘口径, 利率序列止于 2026-11-19)」", True,
           abs(bp(val("TIPS_10Y", "2026-08-19"), val("TIPS_10Y", "2026-11-19")) - 53) < 0.5,
           f"{SRC}.TIPS_10Y[2026-08-19, 2026-11-19]")
# 风险资产方向组合
P.add_bool("B15-股金同跌、美元与波动率齐升(近一月窗)", True,
           val("SPX", "2026-11-23") < val("SPX", "2026-10-23") and val("GOLD_F", "2026-11-23") < val("GOLD_F", "2026-10-23")
           and val("DXY", "2026-11-23") > val("DXY", "2026-10-23") and val("VIX", "2026-11-23") > val("VIX", "2026-10-23")
           and val("NIKKEI225", "2026-11-20") < val("NIKKEI225", "2026-10-23"),
           f"{SRC}.SPX/GOLD_F/DXY/VIX/NIKKEI225", "SPX/NIKKEI225/GOLD_F 负、DXY/VIX 正")
P.add_bool("B16-S2 所述「共同交易日窗 2026-10-20→2026-11-19 实际利率 +11bp 而风险资产回落」", True,
           val("SPX", "2026-11-19") < val("SPX", "2026-10-20"),
           f"{SRC}.SPX[2026-10-20, 2026-11-19]",
           f"SPX {val('SPX', '2026-10-20')}→{val('SPX', '2026-11-19')} ({pct(val('SPX', '2026-10-20'), val('SPX', '2026-11-19')):.2f}%)")
P.save("points_05b_assets.json")

# ---------------------------------------------------------------- ⑤-C 汇率面
P = Points("⑤", "汇率面读数(USDJPY 百分位 / EURUSD)")


def pct_rank(series, target, defs=True):
    """返回多种百分位定义下 target 的百分位(0-100)."""
    xs = sorted(v for _, v in series)
    n = len(xs)
    below = sum(1 for x in xs if x < target)
    leq = sum(1 for x in xs if x <= target)
    return {"n": n, "leq_frac": leq / n * 100, "lt_frac": below / n * 100,
            "midrank": (below + leq) / 2 / n * 100, "rank_m1": (leq - 1) / (n - 1) * 100 if n > 1 else None}


dts, vals = S.series("USDJPY")
cur = val("USDJPY", "2026-11-23")
P.add("C1-USDJPY 2026-11-23 水平", 159.35, cur, f"{SRC}.USDJPY[2026-11-23]")
P.add("C2-USDJPY 近一月变动(%)(2026-10-23→2026-11-23)", 1.82, pct(val("USDJPY", "2026-10-23"), cur), f"{SRC}.USDJPY[2026-10-23, 2026-11-23]")
P.add("C3-USDJPY 三个月变动(%)(2026-08-19→2026-11-23)", -0.13, pct(val("USDJPY", "2026-08-19"), cur), f"{SRC}.USDJPY[2026-08-19, 2026-11-23]")
d3, v3 = last("USDJPY", "2026-08-23")
P.add_probe("C3b-USDJPY 三个月变动(替代口径: 日历锚 2026-08-23 最近观测起)", -0.13, {"窗启": [d3, v3], "chg_pct": round(pct(v3, cur), 2)},
            f"{SRC}.USDJPY[≤2026-08-23..2026-11-23]", "受审稿「三个月」未写窗启日; 本文其他处三个月窗启=2026-08-19; 日历锚口径下符号相反")
d3c, v3c = last("USDJPY", "2026-08-20")
P.add_probe("C3c-USDJPY 三个月变动(替代口径: ≤2026-08-20 最近观测起)", -0.13, {"窗启": [d3c, v3c], "chg_pct": round(pct(v3c, cur), 2)},
            f"{SRC}.USDJPY[≤2026-08-20..2026-11-23]", "替代口径探针")
r12 = pct_rank([(d, v) for d, v in zip(dts, vals) if "2025-11-23" <= d <= "2026-11-23"], cur)
defs12 = [r12[k] for k in ("lt_frac", "leq_frac", "midrank", "rank_m1")]
P.rows.append({"block": "⑤", "id": "C4-USDJPY 12 个月窗内百分位≈71", "source": f"{SRC}.USDJPY[2025-11-23..2026-11-23]", "kind": "point",
               "computed": r12, "claim": "约第 71 百分位",
               "match": all(abs(x - 71) <= 0.5 for x in defs12),
               "detail": f"四种常用定义 {['%.2f' % x for x in defs12]} (n={r12['n']}); 受审稿「约第 71」"})
r_all = pct_rank([(d, v) for d, v in zip(dts, vals) if d <= "2026-11-23"], cur)
defsall = [r_all[k] for k in ("lt_frac", "leq_frac", "midrank", "rank_m1")]
P.rows.append({"block": "⑤", "id": "C5-USDJPY 序列库全史百分位≈96.6", "source": f"{SRC}.USDJPY[全史≤2026-11-23]", "kind": "point",
               "computed": dict(r_all, first=dts[0], last=dts[-1]), "claim": "约第 96.6 百分位(全史 2016-11-23 起)",
               "match": (dts[0] == "2016-11-23") and all(abs(x - 96.6) <= 0.5 for x in defsall),
               "detail": f"首观测 {dts[0]}; 四种常用定义 {['%.2f' % x for x in defsall]} (n={r_all['n']}); 受审稿「约第 96.6」"})
P.add_bool("C6-USDJPY 序列库首观测日=2016-11-23", True, dts[0] == "2016-11-23", f"{SRC}.USDJPY[0]", f"首观测 {dts[0]}")
P.add_bool("C7-USDJPY「近一月不降反升」", True, cur > val("USDJPY", "2026-10-23"), f"{SRC}.USDJPY[2026-10-23, 2026-11-23]")

dts, vals = S.series("EURUSD")
e_cur = val("EURUSD", "2026-11-23")
P.add("C8-EURUSD 2026-11-23 水平", 1.093972, e_cur, f"{SRC}.EURUSD[2026-11-23]", nd=6)
P.add("C9-EURUSD 三个月变动(%)", -5.52, pct(val("EURUSD", "2026-08-19"), e_cur), f"{SRC}.EURUSD[2026-08-19, 2026-11-23]")
e3, ev3 = last("EURUSD", "2026-08-23")
P.add_probe("C9b-EURUSD 三个月变动(替代口径: 日历锚 2026-08-23 最近观测起)", -5.52, {"窗启": [e3, ev3], "chg_pct": round(pct(ev3, e_cur), 2)},
            f"{SRC}.EURUSD[≤2026-08-23..2026-11-23]", "受审稿「三个月」未写窗启日; 本文其他处三个月窗启=2026-08-19")
win_e = [(d, v) for d, v in zip(dts, vals) if "2025-11-23" <= d <= "2026-11-23"]
mne = min(win_e, key=lambda x: x[1])
P.add_bool("C10-EURUSD 2026-11-23 为近 12 个月窗(2025-11-23..2026-11-23)最低", True, mne[0] == "2026-11-23",
           f"{SRC}.EURUSD[2025-11-23..2026-11-23]", f"窗内最低 {mne[0]}={mne[1]}; 观测数={len(win_e)}")
P.save("points_05c_fx.json")

# ---------------------------------------------------------------- ⑤-D 油价
P = Points("⑤", "供给侧对账: 布伦特原油(BRENT_F)窗内读数与月均")
dts, vals = S.series("BRENT_F")
b_start, b_end = val("BRENT_F", "2026-08-19"), val("BRENT_F", "2026-11-23")
P.add("D1-BRENT_F 2026-08-19", 91.62, b_start, f"{SRC}.BRENT_F[2026-08-19]")
P.add("D2-BRENT_F 2026-11-23", 88.19, b_end, f"{SRC}.BRENT_F[2026-11-23]")
P.add("D3-BRENT_F 近三个月变动(%)", -3.74, pct(b_start, b_end), f"{SRC}.BRENT_F[2026-08-19, 2026-11-23]")
b1023 = val("BRENT_F", "2026-10-23")
P.add("D4-BRENT_F 2026-10-23", 116.72, b1023, f"{SRC}.BRENT_F[2026-10-23]")
P.add("D5-BRENT_F 2026-10-23 较窗启(%)", 27.40, pct(b_start, b1023), f"{SRC}.BRENT_F[2026-08-19, 2026-10-23]")
P.add("D6-BRENT_F 近一月变动(%)(2026-10-23→2026-11-23)", -24.44, pct(b1023, b_end), f"{SRC}.BRENT_F[2026-10-23, 2026-11-23]")
cands = {}
for a in ("2025-11-19", "2025-11-23", "2025-11-20"):
    v = S.exact("BRENT_F", a)
    if v is not None:
        cands[a] = round(pct(v, b_end), 2)
for a in ("2025-11-19", "2025-11-23"):
    r = last("BRENT_F", a)
    cands[f"le{a}"] = [r[0], round(pct(r[1], b_end), 2)]
P.add("D7-BRENT_F 近 12 个月变动(%)(窗启 2025-11-19, 与三利率 12 个月窗同口径)", 38.86,
      pct(val("BRENT_F", "2025-11-19"), b_end), f"{SRC}.BRENT_F[2025-11-19, 2026-11-23]", f"窗 {val('BRENT_F', '2025-11-19')}→{b_end}; 其他窗启候选 {cands}")
win = [(d, v) for d, v in zip(dts, vals) if "2026-08-19" <= d <= "2026-11-23"]
mx = max(win, key=lambda x: x[1])
P.add("D8-BRENT_F 窗内高点", 117.64, mx[1], f"{SRC}.BRENT_F[2026-08-19..2026-11-23]", f"窗内高点日 {mx[0]}")
P.add_bool("D9-BRENT_F 窗内高点日=2026-10-30", True, mx[0] == "2026-10-30", f"{SRC}.BRENT_F[2026-08-19..2026-11-23]")
P.add_bool("D10-BRENT_F 窗内观测数=68", True, len(win) == 68, f"{SRC}.BRENT_F[2026-08-19..2026-11-23]", f"观测数 {len(win)}")
P.add_bool("D11-BRENT_F 窗内不低于窗启值 91.62 的观测数=61", True, sum(1 for _, v in win if v >= b_start) == 61,
           f"{SRC}.BRENT_F[2026-08-19..2026-11-23]", f"不低于窗启 {sum(1 for _, v in win if v >= b_start)} 个")
# 日值月均
mm = defaultdict(list)
for d, v in zip(dts, vals):
    mm[d[:7]].append(v)
mean = {k: sum(v) / len(v) for k, v in mm.items()}
P.add("D12-BRENT_F 日值月均 2026-07", 84.51, mean["2026-07"], f"{SRC}.BRENT_F[2026-07 日值均]")
P.add("D13-BRENT_F 日值月均 2026-09", 102.26, mean["2026-09"], f"{SRC}.BRENT_F[2026-09 日值均]")
P.add("D14-BRENT_F 日值月均 2026-10", 108.34, mean["2026-10"], f"{SRC}.BRENT_F[2026-10 日值均]")
P.add("D15-BRENT_F 日值月均 2025-10", 63.95, mean["2025-10"], f"{SRC}.BRENT_F[2025-10 日值均]")
P.add("D16-BRENT_F 月均 2026-07→2026-09(%)", 21.0, pct(mean["2026-07"], mean["2026-09"]), f"{SRC}.BRENT_F[月均 2026-07, 2026-09]")
P.add("D17-BRENT_F 月均 2026-07→2026-10(%)", 28.2, pct(mean["2026-07"], mean["2026-10"]), f"{SRC}.BRENT_F[月均 2026-07, 2026-10]", nd=1)
P.add("D18-BRENT_F 月均 2026-10 较 2025-10(%)", 69.4, pct(mean["2025-10"], mean["2026-10"]), f"{SRC}.BRENT_F[月均 2025-10, 2026-10]")
pub = [(d, v) for d, v in zip(dts, vals) if "2026-10-13" <= d <= "2026-11-16"]
pmin, pmax = min(pub, key=lambda x: x[1]), max(pub, key=lambda x: x[1])
# 受审稿原句: 「这些读数的发布日 2026-10-13 至 2026-11-16 的油价在 92.44 至 117.64 之间,均不低于窗启值 91.62」
# 字面读法 A: 各发布日【当日】的油价. 「这些读数」=句中「本问所解释的 2026-09/2026-10 观测月」的通胀读数
# (美国 CPI/核心 CPI、核心 PCE、欧元区 HICP); 发布日=引擎推定规则(月末+N 天, N 取自 plan 点值格 publication_rule)
import re
from datetime import timedelta
plan = load_json(os.path.join(SEAT, "x_research_plan.json"))
rule_n = {}
for cell in plan["point_values"]["cells"]:
    m = re.search(r"月末\+(\d+)天", cell["anchors"]["最新一期"]["publication_rule"])
    if m:
        rule_n[cell["metric_id"]] = int(m.group(1))
        # 规则自检: 用规则重算最新锚发布日须等于 plan 所载
        pe = to_date(cell["anchors"]["最新一期"]["period_end"])
        assert (pe + timedelta(days=rule_n[cell["metric_id"]])).isoformat() == cell["anchors"]["最新一期"]["publication_date"], cell["metric_id"]
pubdates = set()
for mid in ("CPI", "CORE_CPI", "CORE_PCE", "EA_HICP_YOY"):
    for ym in ("2026-09", "2026-10"):
        last_day = to_date(month_shift(ym + "-01", 1)) - timedelta(days=1)
        pd_ = (last_day + timedelta(days=rule_n[mid])).isoformat()
        if pd_ <= "2026-11-23":
            pubdates.add(pd_)
pubdates = sorted(pubdates)
on_pub = []
for d in pubdates:
    v = S.exact("BRENT_F", d)
    if v is None:  # 非交易日(如周日发布日): 取最近邻并留痕
        r = S.le("BRENT_F", d)
        on_pub.append((d, r[0], r[1]))
    else:
        on_pub.append((d, d, v))
mnA = min(on_pub, key=lambda x: x[2])
mxA = max(on_pub, key=lambda x: x[2])
P.rows.append({"block": "⑤", "id": "D19-各发布日当日 BRENT_F 最低(字面读法 A)", "source": f"{SRC}.BRENT_F[各发布日]; report.json:research_plan.point_values.cells[*].anchors.最新一期.publication_rule(月末+N天,推定)",
               "kind": "point", "computed": {"最低": [mnA[2], mnA[0], mnA[1]], "发布日数": len(on_pub)},
               "claim": 92.44, "match": abs(round(mnA[2], 2) - 92.44) < 0.006,
               "detail": "发布日→观测日→油价: " + "; ".join(f"{a}→{b} {c:.2f}" for a, b, c in on_pub)})
P.rows.append({"block": "⑤", "id": "D20-各发布日当日 BRENT_F 最高(字面读法 A)", "source": f"{SRC}.BRENT_F[各发布日]",
               "kind": "point", "computed": {"最高": [mxA[2], mxA[0], mxA[1]]}, "claim": 117.64,
               "match": abs(round(mxA[2], 2) - 117.64) < 0.006, "detail": f"最高 {mxA[2]}@发布日 {mxA[0]}"})
P.add_bool("D21-各发布日当日 BRENT_F 全部不低于窗启值 91.62(字面读法 A)", True, all(c >= b_start for _, _, c in on_pub),
           f"{SRC}.BRENT_F[各发布日]", f"{len(on_pub)} 个发布日; 最低 {mnA[2]}")
P.add_bool("D20b-发布日跨度端点=2026-10-13 与 2026-11-16(九月/十月通胀读数, 引擎推定规则月末+N天)", True,
           pubdates[0] == "2026-10-13" and pubdates[-1] == "2026-11-16",
           "x_research_plan.json:research_plan.point_values.cells[*].anchors.最新一期.publication_rule(月末+N天,推定)",
           f"规则天数 {rule_n}; 跨度 {pubdates[0]}..{pubdates[-1]}; 全部发布日 {pubdates}")
# 读法 B(区间): 探针留档
P.add_probe("D19p/D21p-读法 B(区间 2026-10-13..2026-11-16 内全部观测)的最低值与「均不低于」", "92.44 / 均不低于 91.62",
            {"区间最低": [round(pmin[1], 2), pmin[0]], "区间最高": [round(pmax[1], 2), pmax[0]], "观测数": len(pub),
             "低于 91.62 的观测": [[d, round(v, 2)] for d, v in pub if v < b_start]},
            f"{SRC}.BRENT_F[2026-10-13..2026-11-16]", "区间读法下最低 91.49@2026-11-10 低于窗启值, 原句不成立 → 记 MINOR(歧义)")
P.add_bool("D22-「窗内先升至 2026-10-23 的 116.72」「窗末急跌」: 窗末值低于窗启且低于 2026-10-23", True,
           b_end < b_start and b_end < b1023, f"{SRC}.BRENT_F[2026-08-19, 2026-10-23, 2026-11-23]")
P.save("points_05d_oil.json")
