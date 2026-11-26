#!/usr/bin/python3 -I
"""s10_points.py — ①研究截止日/发布纪律 ②点值锚格 ③同比 基期 独立直算.
用法: /usr/bin/python3 -I s10_points.py <冻结快照> <冻结日历> <席位目录>
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seatlib as L  # noqa: E402

snap_path, cal_path, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
snap = L.load_json(snap_path)
cal = L.load_json(cal_path)
st = L.Store(snap)
CUT = "2026-11-23"
SRC = "root_overlay/data/daily/research_snapshot_20261123.json"


def cut() -> str:
    return "2026-11-23"


# ---------------------------------------------------------------- ① 截止日
P = L.Points("①", "研究截止日与观测/发布纪律")
P.add_bool("A1-研究截止日=快照 research_as_of 日期",
           True, snap["research_as_of"][:10] == CUT, SRC + ":research_as_of",
           f"research_as_of={snap['research_as_of']}")
P.add_bool("A1-研究截止日=快照 target_date",
           True, snap["target_date"] == CUT.replace("-", ""), SRC + ":target_date",
           f"target_date={snap['target_date']}")
# 快照内是否有晚于截止日的观测(逐序列扫最大观测日)
late = {}
for mid, e in snap["series_store"].items():
    if e["dates"] and max(e["dates"]) > CUT:
        late[mid] = max(e["dates"])
P.add_bool("A1-快照 series_store 无晚于截止日的观测", True, not late, SRC + ":series_store[*].dates",
           f"晚于截止日的序列={late}")
# 日频序列最新观测日
for mid in ["SPX", "VIX", "GOLD_F", "DXY", "EURUSD", "USDJPY", "BRENT_F", "NIKKEI225",
            "UST_10Y", "TIPS_10Y", "BEI_10Y", "DFEDTARU", "ECB_DFR"]:
    d, v = st.le(mid, CUT)
    P.rows.append({"block": "①", "id": f"A1-{mid} 截止日前最新观测日",
                   "source": SRC + f":series_store.{mid}.dates",
                   "computed": d, "claim": "≤2026-11-23", "match": d <= CUT,
                   "detail": f"最新观测 {d} 值 {v}(≤截止日={d <= CUT})"})
# 发布日推定规则复核(月末+N 天) 与截止日关系
import datetime as _dt


def me_plus(period_end, n):
    d = L.to_date(period_end) + _dt.timedelta(days=n)
    return d.isoformat()


pub_specs = [  # (metric, obs_date, period_end, n, engine_pub, anchor_as_of)
    ("US_REAL_GDP", "2026-04-01", "2026-06-30", 29, "2026-07-29", "2026-08-23"),
    ("US_REAL_GDP", "2026-07-01", "2026-09-30", 29, "2026-10-29", "2026-11-23"),
    ("UNEMPLOYMENT", "2026-07-01", "2026-07-31", 5, "2026-08-05", "2026-08-23"),
    ("UNEMPLOYMENT", "2026-10-01", "2026-10-31", 5, "2026-11-05", "2026-11-23"),
    ("INDPRO", "2026-07-01", "2026-07-31", 15, "2026-08-15", "2026-08-23"),
    ("INDPRO", "2026-10-01", "2026-10-31", 15, "2026-11-15", "2026-11-23"),
    ("CPI", "2026-07-01", "2026-07-31", 13, "2026-08-13", "2026-08-23"),
    ("CPI", "2026-10-01", "2026-10-31", 13, "2026-11-13", "2026-11-23"),
    ("CORE_CPI", "2026-10-01", "2026-10-31", 13, "2026-11-13", "2026-11-23"),
    ("CORE_PCE", "2026-06-01", "2026-06-30", 30, "2026-07-30", "2026-08-23"),
    ("CORE_PCE", "2026-09-01", "2026-09-30", 30, "2026-10-30", "2026-11-23"),
    ("EA_REAL_GDP_YOY", "2026-04-01", "2026-06-30", 35, "2026-08-04", "2026-08-23"),
    ("EA_REAL_GDP_YOY", "2026-07-01", "2026-09-30", 35, "2026-11-04", "2026-11-23"),
    ("EA_HICP_YOY", "2026-07-01", "2026-07-31", 16, "2026-08-16", "2026-08-23"),
    ("EA_HICP_YOY", "2026-10-01", "2026-10-31", 16, "2026-11-16", "2026-11-23"),
    ("JP_POLICY_RATE", "2026-07-01", "2026-07-31", 5, "2026-08-05", "2026-08-23"),
    ("JP_POLICY_RATE", "2026-10-01", "2026-10-31", 5, "2026-11-05", "2026-11-23"),
]
for mid, od, pe, n, ep, anchor in pub_specs:
    r = me_plus(pe, n)
    P.rows.append({"block": "①", "id": f"A2-{mid}@{od} 推定发布日",
                   "source": f"规则=期末({pe})+{n}天",
                   "computed": r, "claim": ep, "match": r == ep,
                   "detail": f"期末+{n}天={r}; 引擎/读者面={ep}; ≤锚日({anchor})={r <= anchor}"})
# CORE_PCE 2026-07 观测为何不作 3 个月前锚: 推定发布 2026-08-30 > 2026-08-23
r = me_plus("2026-07-31", 30)
P.rows.append({"block": "①", "id": "A2-CORE_PCE@2026-07 推定发布日晚于 3 个月前锚日(故锚=2026-06)",
               "source": "规则=期末(2026-07-31)+30天",
               "computed": r > "2026-08-23", "claim": True, "match": r > "2026-08-23",
               "detail": f"推定发布日 {r} > 锚日 2026-08-23"})
r = me_plus("2026-09-30", 29)
P.rows.append({"block": "①", "id": "A2-US_REAL_GDP@2026-07 推定发布日晚于 3 个月前锚日(故锚=2026-04)",
               "source": "规则=期末(2026-09-30)+29天",
               "computed": r > "2026-08-23", "claim": True, "match": r > "2026-08-23",
               "detail": f"推定发布日 {r} > 锚日 2026-08-23"})
P.save("points_01_cutoff.json")

# ------------------------------------------------------------ ② 点值锚格
P = L.Points("②", "点值锚格(9 格×2 锚: 值/观测日/同比)")
cells = [  # metric, 3m obs, 3m val, 3m yoy(or None), latest obs, latest val, latest yoy(or None), latest_valid(yoy ym or None)
    ("US_REAL_GDP", "2026-04-01", 24408.011, 2.19, "2026-07-01", 24611.077, 2.07, None),
    ("UNEMPLOYMENT", "2026-07-01", 4.1, None, "2026-10-01", 4.1, None, None),
    ("INDPRO", "2026-07-01", 103.1675, 1.25, "2026-10-01", 103.3954, 2.15, None),
    ("CPI", "2026-07-01", 332.813, 3.3, "2026-10-01", 337.476, None, ("2026-09", 3.72)),
    ("CORE_CPI", "2026-07-01", 336.789, 2.47, "2026-10-01", 339.9, None, ("2026-09", 2.57)),
    ("CORE_PCE", "2026-06-01", 129.969, 3.04, "2026-09-01", 130.902, 3.12, None),
    ("EA_REAL_GDP_YOY", "2026-04-01", 1.19, None, "2026-07-01", 1.28, None, None),
    ("EA_HICP_YOY", "2026-07-01", 2.9, None, "2026-10-01", 4.0, None, None),
    ("JP_POLICY_RATE", "2026-07-01", 0.978, None, "2026-10-01", 1.227, None, None),
]
for mid, o3, v3, y3, ol, vl, yl, lv in cells:
    k3 = SRC + f":series_store.{mid}"
    x3 = st.exact(mid, o3)
    nd3 = 4 if abs(v3) > 1000 else (3 if abs(v3) > 100 else (4 if mid == "INDPRO" else 3))
    P.add(f"B-{mid} 3个月前锚值@{o3}", v3, x3, k3 + f".values[dates=={o3}]", nd=nd3)
    xl = st.exact(mid, ol)
    P.add(f"B-{mid} 最新一期值@{ol}", vl, xl, k3 + f".values[dates=={ol}]", nd=nd3)
    # 最新一期是否为序列在截止日前的最新观测
    d_last, _ = st.le(mid, CUT)
    P.rows.append({"block": "②", "id": f"B-{mid} 最新一期=截止日前最新观测",
                   "source": k3 + ".dates", "computed": d_last, "claim": ol, "match": d_last == ol,
                   "detail": f"序列截止日前最新观测日 {d_last}; 报告 {ol}"})
    if y3 is not None:
        y, why = st.yoy(mid, o3[:7])
        P.add(f"B-{mid} 3个月前锚同比(基期={L.month_shift(o3[:7] + '-01', -12)[:7]})", y3, y,
              k3 + f" ({o3[:7]} / {L.month_shift(o3[:7] + '-01', -12)[:7]} - 1)")
    if yl is not None:
        y, why = st.yoy(mid, ol[:7])
        P.add(f"B-{mid} 最新一期同比(基期={L.month_shift(ol[:7] + '-01', -12)[:7]})", yl, y,
              k3 + f" ({ol[:7]} / {L.month_shift(ol[:7] + '-01', -12)[:7]} - 1)")
    if lv is not None:
        y, why = st.yoy(mid, ol[:7])
        P.rows.append({"block": "②", "id": f"B-{mid} 最新一期同比不可得(缺基期)",
                       "source": k3 + f" ({ol[:7]} 与 {L.month_shift(ol[:7] + '-01', -12)[:7]})",
                       "computed": (y is None), "claim": True, "match": (y is None),
                       "detail": f"直算同比={y} 原因={why}; 报告=不可得"})
        base_ym = L.month_shift(ol[:7] + "-01", -12)[:7]
        P.rows.append({"block": "②", "id": f"B-{mid} 基期 {base_ym} 在序列库缺席",
                       "source": k3 + f".dates", "computed": st.mval(mid, base_ym),
                       "claim": None, "match": (st.mval(mid, base_ym) is None),
                       "detail": f"{base_ym} 观测值={st.mval(mid, base_ym)}(报告: 缺采)"})
        yy, _ = st.yoy(mid, lv[0])
        P.add(f"B-{mid} 最近有效同比 {lv[0]}", lv[1], yy, k3 + f" ({lv[0]} / {L.month_shift(lv[0] + '-01', -12)[:7]} - 1)")
        # 最近有效同比的月份确为截止日前最后一个可算同比的月份
        rows = st.monthly(mid, n=14)
        last_ok = None
        for ym, _ in rows:
            if ym > CUT[:7]:
                continue
            v, w = st.yoy(mid, ym)
            if v is not None:
                last_ok = ym
        P.rows.append({"block": "②", "id": f"B-{mid} 最近有效同比月份", "source": k3, "computed": last_ok,
                       "claim": lv[0], "match": last_ok == lv[0], "detail": f"逐月直算最后可算同比月份={last_ok}"})
# CPI / CORE_CPI 2025-09..2026-01 的观测在场性(缺采月份定位)
for mid in ["CPI", "CORE_CPI"]:
    pres = [(ym, st.mval(mid, ym)) for ym in ["2025-08", "2025-09", "2025-10", "2025-11", "2025-12", "2026-01"]]
    miss = [ym for ym, v in pres if v is None]
    P.rows.append({"block": "②", "id": f"B-{mid} 2025-08..2026-01 缺采月=仅 2025-10",
                   "source": SRC + f":series_store.{mid}.dates", "computed": miss, "claim": ["2025-10"],
                   "match": miss == ["2025-10"], "detail": f"在场性={pres}"})
P.save("points_02_anchors.json")

# ---------------------------------------------------------------- ③ 同比
P = L.Points("③", "同比口径/基期/年内高低/美欧水平对比史")


def yy(mid, ym):
    return st.yoy(mid, ym)[0]


# 走位叙述中的全部同比数字
for mid, ym, claimed in [
    ("CPI", "2026-02", 2.434), ("CPI", "2026-05", 4.1666), ("CPI", "2026-09", 3.72), ("CPI", "2026-07", 3.3),
    ("CORE_CPI", "2026-02", 2.4725), ("CORE_CPI", "2026-05", 2.8229), ("CORE_CPI", "2026-08", 2.4462),
    ("CORE_CPI", "2026-09", 2.5658), ("CORE_CPI", "2026-07", 2.47), ("CORE_CPI", "2026-09", 2.57),
    ("CORE_PCE", "2026-06", 3.04), ("CORE_PCE", "2026-09", 3.12),
    ("INDPRO", "2025-11", 1.7543), ("INDPRO", "2026-02", 0.7972), ("INDPRO", "2026-07", 1.25), ("INDPRO", "2026-10", 2.15),
    ("US_REAL_GDP", "2026-04", 2.19), ("US_REAL_GDP", "2026-07", 2.07),
]:
    nd = len(str(claimed).split(".")[1]) if "." in str(claimed) else 0
    P.add(f"C-{mid} 同比 {ym}", claimed, yy(mid, ym),
          SRC + f":series_store.{mid} ({ym}/{L.month_shift(ym + '-01', -12)[:7]}-1)", nd=nd)
# 美国 headline CPI 同比 2026 年内高点=2026-05
cpi26 = [(ym, yy("CPI", ym)) for ym in [f"2026-{m:02d}" for m in range(1, 11)]]
mx = max((v, ym) for ym, v in cpi26 if v is not None)
P.rows.append({"block": "③", "id": "C-CPI 同比 2026 年内高点月=2026-05(约 4.17)",
               "source": SRC + ":series_store.CPI", "computed": mx, "claim": ("2026-05", 4.17),
               "match": mx[1] == "2026-05" and round(mx[0], 2) == 4.17, "detail": f"逐月同比={[(y, round(v, 4) if v is not None else None) for y, v in cpi26]}"})
# 美欧同比对比史: EA_HICP_YOY > CPI同比 的月份
both = []
for d, _ in zip(*st.series("EA_HICP_YOY")):
    ym = d[:7]
    us = yy("CPI", ym)
    ea = st.mval("EA_HICP_YOY", ym)
    if us is not None and ea is not None:
        both.append((ym, ea, us))
gt = [ym for ym, ea, us in both if ea > us]
eq = [ym for ym, ea, us in both if abs(ea - us) < 1e-9]
lt = [ym for ym, ea, us in both if ea < us]
last_gt_before = [ym for ym in gt if ym < "2026-09"]
P.rows.append({"block": "③", "id": "C-美欧可比同月: 2026-09 为 2023-09 以来首个 EA>US 月份",
               "source": SRC + ":series_store.EA_HICP_YOY + CPI(同比派生)",
               "computed": {"2026-09": dict((y, (e, round(u, 4))) for y, e, u in both if y == "2026-09").get("2026-09"),
                            "max EA>US month before 2026-09": max(last_gt_before) if last_gt_before else None,
                            "months 2023-10..2026-08 with EA>US": [y for y in gt if "2023-10" <= y <= "2026-08"]},
               "claim": "2023-09 以来首个; 2026-09 EA 略高",
               "match": (max(last_gt_before) == "2023-09" if last_gt_before else False) and "2026-09" in gt
               and not [y for y in gt if "2023-10" <= y <= "2026-08"],
               "detail": f"2026-09 EA={dict((y, e) for y, e, u in both).get('2026-09')} US同比={round(dict((y, u) for y, e, u in both).get('2026-09'), 4)}; 2026-10 EA可比但US缺基期; EA>US 月份总数={len(gt)}"})
# 2022-07..2023-09 持续高于
seg = [(ym, ea, round(us, 3)) for ym, ea, us in both if "2022-07" <= ym <= "2023-09"]
P.rows.append({"block": "③", "id": "C-2022-07..2023-09 EA 持续高于 US(逐月)",
               "source": SRC + ":series_store.EA_HICP_YOY + CPI", "computed": all(e > u for _, e, u in seg),
               "claim": True, "match": all(e > u for _, e, u in seg) and len(seg) == 15,
               "detail": f"n={len(seg)} 段内最低差={min(e - u for _, e, u in seg):.3f}"})
# 2026-08 及之前: EA<=US
seg2 = [(ym, ea, round(us, 3)) for ym, ea, us in both if "2025-01" <= ym <= "2026-08"]
P.rows.append({"block": "③", "id": "C-2025-01..2026-08 逐月 EA<=US(可比月)",
               "source": SRC + ":series_store.EA_HICP_YOY + CPI", "computed": [(y, e, u) for y, e, u in seg2 if e > u],
               "claim": [], "match": not [(y, e, u) for y, e, u in seg2 if e > u],
               "detail": f"可比月数={len(seg2)}; EA>US 的月份={[(y, e, u) for y, e, u in seg2 if e > u]}"})
# EA HICP 同比路径
for ym, claimed in [("2026-02", 1.9), ("2026-05", 3.2), ("2026-06", 2.8), ("2026-07", 2.9), ("2026-10", 4.0)]:
    P.add(f"C-EA_HICP_YOY {ym}", claimed, st.mval("EA_HICP_YOY", ym), SRC + f":series_store.EA_HICP_YOY[{ym}]", nd=1)
ea26 = [(d[:7], v) for d, v in zip(*st.series("EA_HICP_YOY")) if d[:4] == "2026"]
P.rows.append({"block": "③", "id": "C-EA_HICP 2026-10=年内新高", "source": SRC + ":series_store.EA_HICP_YOY",
               "computed": max(ea26, key=lambda t: t[1]), "claim": ("2026-10", 4.0),
               "match": max(ea26, key=lambda t: t[1])[0] == "2026-10" and max(ea26, key=lambda t: t[1])[1] == 4.0,
               "detail": f"逐月={ea26}"})
P.add("C-HICP 三个月上行幅度(pp)", 1.1, st.mval("EA_HICP_YOY", "2026-10") - st.mval("EA_HICP_YOY", "2026-07"),
      SRC + ":series_store.EA_HICP_YOY[2026-10]-[2026-07]", nd=1)
# INDPRO 环比与基数
P.add("C-INDPRO 2026-10 环比(%)", -0.43, (st.mval("INDPRO", "2026-10") / st.mval("INDPRO", "2026-09") - 1) * 100,
      SRC + ":series_store.INDPRO[2026-10]/[2026-09]-1")
P.add("C-INDPRO 2025-07→2025-10 基数变化(%)", -0.66, (st.mval("INDPRO", "2025-10") / st.mval("INDPRO", "2025-07") - 1) * 100,
      SRC + ":series_store.INDPRO[2025-10]/[2025-07]-1")
P.add("C-INDPRO 水平 2026-07→2026-10 变化(%)", 0.22, (st.mval("INDPRO", "2026-10") / st.mval("INDPRO", "2026-07") - 1) * 100,
      SRC + ":series_store.INDPRO[2026-10]/[2026-07]-1")
P.add("C-INDPRO 同比三个月变动(pp)", 0.90, yy("INDPRO", "2026-10") - yy("INDPRO", "2026-07"),
      SRC + ":series_store.INDPRO 同比 2026-10 − 2026-07", note="报告写 1.25→2.15(差 0.90)", nd=2)
# 失业率路径
un = {d[:7]: v for d, v in zip(*st.series("UNEMPLOYMENT"))}
for ym, claimed in [("2026-07", 4.1), ("2026-09", 4.2), ("2026-10", 4.1), ("2026-08", 4.1), ("2025-11", 4.5), ("2026-02", 4.4), ("2026-05", 4.3)]:
    P.add(f"C-UNEMPLOYMENT {ym}", claimed, un.get(ym), SRC + f":series_store.UNEMPLOYMENT[{ym}]", nd=1)
# GDP 水平
P.add("C-US_REAL_GDP 2026-04 水平", 24408.011, st.mval("US_REAL_GDP", "2026-04"), SRC + ":series_store.US_REAL_GDP[2026-04]", nd=3)
P.add("C-EA_REAL_GDP_YOY 2026-04", 1.19, st.mval("EA_REAL_GDP_YOY", "2026-04"), SRC + ":series_store.EA_REAL_GDP_YOY[2026-04]", nd=2)
P.add("C-EA_REAL_GDP_YOY 2026-07", 1.28, st.mval("EA_REAL_GDP_YOY", "2026-07"), SRC + ":series_store.EA_REAL_GDP_YOY[2026-07]", nd=2)
P.save("points_03_yoy.json")
