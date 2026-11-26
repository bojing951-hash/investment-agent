#!/usr/bin/python3 -I
# s02c: 资产月窗 + 三利率分解 + 类比面 + 情景阈值 独立复算(只读)
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rc_lib import *

snap_p, rep_p, cal_p, reg_p, aj_p, outdir = sys.argv[1:7]
snap, rep, cal, reg, aj = load(snap_p, rep_p, cal_p, reg_p, aj_p)
SS = snap["series_store"]
P = Points()

def nearest_before(mid, date):
    return at_or_before(SS, mid, date)

# ---------- 资产月窗(引擎窗 2026-10-23→≤2026-11-23 最新观测; 收盘窗 2026-10-23→2026-11-20) ----------
rows = {"SPX": (-5.51, -9.36), "NIKKEI225": (-9.98, -9.98), "SHCOMP": (-4.11, -4.25), "DAX": (0.11, -1.50), "VIX": (38.87, 84.52)}
i = 1
for mid, (e_chg, c_chg) in rows.items():
    f = at(SS, mid, "2026-10-23"); t = at_or_before(SS, mid, CUT); c = at(SS, mid, "2026-11-20")
    P.add("A%02d" % i, SNAP, "%s@2026-10-23" % mid, f, {"SPX": 7623.680176, "NIKKEI225": 62693.16, "SHCOMP": 3690.4753, "DAX": 25181.650391, "VIX": 19.450001}[mid], 6); i += 1
    P.adds("A%02d" % i, SNAP, "%s 引擎窗终点观测日" % mid, t[0], "2026-11-20" if mid == "NIKKEI225" else "2026-11-23"); i += 1
    P.add("A%02d" % i, SNAP, "%s 引擎窗(10-23→末观测) 变动%%" % mid, pct(f, t[1]), e_chg, 2); i += 1
    P.add("A%02d" % i, SNAP, "%s 收盘窗(10-23→11-20) 变动%%" % mid, pct(f, c), c_chg, 2); i += 1
P.adds("A21", SNAP, "NIKKEI225 序列末观测", last(SS, "NIKKEI225")[0], "2026-11-20")
P.addb("A22", SNAP, "NIKKEI225 在 2026-11-23 无观测", at(SS, "NIKKEI225", CUT) is None)
P.add("A23", SNAP, "DAX@2026-11-23", at(SS, "DAX", CUT), 25209.45, 2)
P.add("A24", SNAP, "VIX@2026-11-20", at(SS, "VIX", "2026-11-20"), 35.89, 2)
P.add("A25", SNAP, "SPX 11-23 vs 11-20 %", pct(at(SS, "SPX", "2026-11-20"), at(SS, "SPX", CUT)), 4.25, 2)
P.add("A26", SNAP, "VIX 11-23 vs 11-20 %", pct(at(SS, "VIX", "2026-11-20"), at(SS, "VIX", CUT)), -24.74, 2)
P.add("A27", SNAP, "DAX 11-23 vs 11-20 %", pct(at(SS, "DAX", "2026-11-20"), at(SS, "DAX", CUT)), 1.64, 2)
P.add("A28", SNAP, "CAC40 收盘窗 %", pct(at(SS, "CAC40", "2026-10-23"), at(SS, "CAC40", "2026-11-20")), 1.86, 2)
P.add("A29", SNAP, "DXY 收盘窗 %", pct(at(SS, "DXY", "2026-10-23"), at(SS, "DXY", "2026-11-20")), 1.96, 2)
P.add("A30", SNAP, "DXY 引擎窗 %", pct(at(SS, "DXY", "2026-10-23"), at_or_before(SS, "DXY", CUT)[1]), 2.23, 2)
P.add("A31", SNAP, "引擎窗 NIKKEI225 与 SPX 跌幅落差绝对值(pp)(受审稿『两者跌幅相差四点四七个百分点』)", abs(pct(at(SS, "NIKKEI225", "2026-10-23"), at(SS, "NIKKEI225", "2026-11-20")) - pct(at(SS, "SPX", "2026-10-23"), at(SS, "SPX", CUT))), 4.47, 2)
P.add("A32", SNAP, "引擎窗 SPX 与 SHCOMP 落差(pp)", pct(at(SS, "SHCOMP", "2026-10-23"), at_or_before(SS, "SHCOMP", CUT)[1]) - pct(at(SS, "SPX", "2026-10-23"), at(SS, "SPX", CUT)), 1.40, 2)
P.add("A33", SNAP, "收盘窗 SPX 与 SHCOMP 落差(pp)", pct(at(SS, "SHCOMP", "2026-10-23"), at(SS, "SHCOMP", "2026-11-20")) - pct(at(SS, "SPX", "2026-10-23"), at(SS, "SPX", "2026-11-20")), 5.11, 2, "收盘口径下美日跌幅深于中国(落差>2pp)")
P.add("A34", SNAP, "USDJPY@2026-10-23", at(SS, "USDJPY", "2026-10-23"), 156.494, 3)
P.add("A35", SNAP, "USDJPY@2026-11-23", at_or_before(SS, "USDJPY", CUT)[1], 159.347, 3)
P.add("A36", SNAP, "USDJPY 引擎窗 %", pct(at(SS, "USDJPY", "2026-10-23"), at_or_before(SS, "USDJPY", CUT)[1]), 1.82, 2)
P.add("A37", SNAP, "USDCNY@2026-10-23", at(SS, "USDCNY", "2026-10-23"), 6.6779, 4)
P.add("A38", SNAP, "USDCNY@2026-11-23", at_or_before(SS, "USDCNY", CUT)[1], 6.6542, 4)
P.add("A39", SNAP, "USDCNY 引擎窗 %", pct(at(SS, "USDCNY", "2026-10-23"), at_or_before(SS, "USDCNY", CUT)[1]), -0.35, 2)
P.addb("A40", SNAP, "受审稿『同窗 USDJPY 156.494→159.347』两端值=引擎月窗 2026-10-23→2026-11-23 的观测(非 10-20→11-19 共同交易日窗; 该窗为 158.523→159.381, 见 out_s05_extra.txt)", abs(at(SS, "USDJPY", "2026-10-23") - 156.494) < 1e-3 and abs(at_or_before(SS, "USDJPY", CUT)[1] - 159.347) < 1e-3 and abs(at(SS, "USDJPY", "2026-10-20") - 156.494) > 0.5)
P.addb("A44", SNAP, "USDJPY 在三窗(10-20→11-19 / 10-23→11-23 / 10-23→11-20)均为美元对日元走强(方向稳健)", all(pct(at(SS, "USDJPY", a), at(SS, "USDJPY", b)) > 0 for a, b in (("2026-10-20", "2026-11-19"), ("2026-10-23", "2026-11-23"), ("2026-10-23", "2026-11-20"))))
P.addb("A45", SNAP, "USDCNY 在三窗均未走强(方向稳健)", all(pct(at(SS, "USDCNY", a), at(SS, "USDCNY", b)) < 0 for a, b in (("2026-10-20", "2026-11-19"), ("2026-10-23", "2026-11-23"), ("2026-10-23", "2026-11-20"))))
P.adds("A41", "datetime", "2026-11-20 星期", wd("2026-11-20"), "Friday")
P.adds("A42", "datetime", "2026-11-23 星期", wd("2026-11-23"), "Monday")
P.adds("A43", "datetime", "2026-08-23 星期", wd("2026-08-23"), "Sunday")

# ---------- 三利率分解 ----------
for mid, v in [("UST_10Y", 5.04), ("TIPS_10Y", 2.88), ("BEI_10Y", 2.16)]:
    P.add("R_%s_1" % mid, SNAP, "%s@2026-11-19" % mid, at(SS, mid, "2026-11-19"), v, 2)
P.add("R01", SNAP, "名义=实际+盈亏平衡 @2026-11-19 残差(bp)", (at(SS, "UST_10Y", "2026-11-19") - at(SS, "TIPS_10Y", "2026-11-19") - at(SS, "BEI_10Y", "2026-11-19")) * 100, 0.0, 1)
P.adds("R02", SNAP, "UST_10Y@2026-10-20 在场", "yes" if at(SS, "UST_10Y", "2026-10-20") is not None else "no", "yes")
P.adds("R03", SNAP, "TIPS_10Y@2026-10-20 在场", "yes" if at(SS, "TIPS_10Y", "2026-10-20") is not None else "no", "yes")
P.adds("R04", SNAP, "BEI_10Y@2026-10-20 在场", "yes" if at(SS, "BEI_10Y", "2026-10-20") is not None else "no", "yes")
P.add("R05", SNAP, "近一月窗 UST_10Y 变动(bp)", bp(at(SS, "UST_10Y", "2026-10-20"), at(SS, "UST_10Y", "2026-11-19")), -8.0, 1)
P.add("R06", SNAP, "近一月窗 TIPS_10Y 变动(bp)", bp(at(SS, "TIPS_10Y", "2026-10-20"), at(SS, "TIPS_10Y", "2026-11-19")), 11.0, 1)
P.add("R07", SNAP, "近一月窗 BEI_10Y 变动(bp)", bp(at(SS, "BEI_10Y", "2026-10-20"), at(SS, "BEI_10Y", "2026-11-19")), -19.0, 1)
P.add("R08", SNAP, "近一月窗恒等残差(bp)", (bp(at(SS, "UST_10Y", "2026-10-20"), at(SS, "UST_10Y", "2026-11-19")) - bp(at(SS, "TIPS_10Y", "2026-10-20"), at(SS, "TIPS_10Y", "2026-11-19")) - bp(at(SS, "BEI_10Y", "2026-10-20"), at(SS, "BEI_10Y", "2026-11-19"))), 0.0, 1)
P.add("R09", SNAP, "12月窗 UST_10Y 变动(bp)", bp(at(SS, "UST_10Y", "2025-11-19"), at(SS, "UST_10Y", "2026-11-19")), 91.0, 1)
P.add("R10", SNAP, "12月窗 TIPS_10Y 变动(bp)", bp(at(SS, "TIPS_10Y", "2025-11-19"), at(SS, "TIPS_10Y", "2026-11-19")), 102.0, 1)
P.add("R11", SNAP, "12月窗 BEI_10Y 变动(bp)", bp(at(SS, "BEI_10Y", "2025-11-19"), at(SS, "BEI_10Y", "2026-11-19")), -11.0, 1)
P.add("R12", SNAP, "12月窗恒等残差(bp)", bp(at(SS, "UST_10Y", "2025-11-19"), at(SS, "UST_10Y", "2026-11-19")) - bp(at(SS, "TIPS_10Y", "2025-11-19"), at(SS, "TIPS_10Y", "2026-11-19")) - bp(at(SS, "BEI_10Y", "2025-11-19"), at(SS, "BEI_10Y", "2026-11-19")), 0.0, 1)
P.adds("R13", SNAP, "BEI_10Y 序列末观测日", last(SS, "BEI_10Y")[0], "2026-11-20")
P.add("R14", SNAP, "BEI_10Y@末观测", last(SS, "BEI_10Y")[1], 2.15, 2)
P.adds("R15", SNAP, "TIPS_10Y 序列末观测日", last(SS, "TIPS_10Y")[0], "2026-11-19")
P.adds("R16", SNAP, "UST_10Y 序列末观测日", last(SS, "UST_10Y")[0], "2026-11-19")
P.add("R17", SNAP, "UST_10Y@2026-10-23", at(SS, "UST_10Y", "2026-10-23"), 5.00, 2)
P.addb("R18", SNAP, "近一月共同交易日窗内(10-20→11-19)DFEDTARU 无变动", len(changes(SS, "DFEDTARU", "2026-10-20", "2026-11-19")) == 0)
P.addb("R19", SNAP, "近一月窗实际利率为名义利率的唯一上行分量", bp(at(SS, "TIPS_10Y", "2026-10-20"), at(SS, "TIPS_10Y", "2026-11-19")) > 0 and bp(at(SS, "BEI_10Y", "2026-10-20"), at(SS, "BEI_10Y", "2026-11-19")) < 0)
P.addb("R20", SNAP, "12月窗实际利率为主导分量(|+102|>|−11|)", abs(bp(at(SS, "TIPS_10Y", "2025-11-19"), at(SS, "TIPS_10Y", "2026-11-19"))) > abs(bp(at(SS, "BEI_10Y", "2025-11-19"), at(SS, "BEI_10Y", "2026-11-19"))))
P.addb("R21", SNAP, "近一月窗盈亏平衡降幅(19bp)大于实际上行幅度(11bp)", abs(bp(at(SS, "BEI_10Y", "2026-10-20"), at(SS, "BEI_10Y", "2026-11-19"))) > bp(at(SS, "TIPS_10Y", "2026-10-20"), at(SS, "TIPS_10Y", "2026-11-19")))

# ---------- 类比面 (S6 envelope) ----------
env = None
for st in rep["steps"]:
    if st.get("step") == "S6_analog":
        env = st["envelope"]["data"]
F = "report.json steps[S6_analog].envelope.data"
P.add("N01", F + ".candidates", "scanned", env["candidates"]["scanned"], 1871, 0)
P.add("N02", F + ".candidates", "valid", env["candidates"]["valid"], 74, 0)
P.add("N03", F + ".candidates", "dropped_insufficient", env["candidates"]["dropped_insufficient"], 1785, 0)
P.add("N04", F + ".candidates", "dropped_overlap", env["candidates"]["dropped_overlap"], 12, 0)
P.add("N05", F + ".candidates", "valid+insufficient+overlap = scanned", env["candidates"]["valid"] + env["candidates"]["dropped_insufficient"] + env["candidates"]["dropped_overlap"], 1871, 0)
P.adds("N06", F + ".top[*].candidate_month", "TOP-5 顺序", ",".join(t["candidate_month"] for t in env["top"]), "2025-03,2022-06,2023-10,2021-02,2020-01")
P.addb("N07", F + ".sort_basis", "排序依据=缺席特征数优先、其后距离", "(n_missing, distance, month)" in json.dumps(env, ensure_ascii=False))
for k, v, i in [("growth", 0.17, 8), ("inflation", 0.33, 9), ("rates", 0.75, 10), ("credit", 0.50, 11), ("volatility", 1.00, 12), ("valuation", 0.50, 13)]:
    P.add("N%02d" % i, F + ".state_vector.%s.coverage" % k, "coverage %s" % k, env["state_vector"][k]["coverage"], v, 2)
t1 = env["top"][0]["dims"]
for k, v, i in [("volatility", 42.13, 14), ("rates", 40.66, 15), ("inflation", 10.54, 16), ("valuation", 6.67, 17), ("credit", 0.00, 18), ("growth", 0.00, 19)]:
    P.add("N%02d" % i, F + ".top[0].dims.%s.contribution_share" % k, "首位候选贡献份额 pct %s" % k, t1[k]["contribution_share"] * 100.0, v, 2)
P.add("N20", F + ".features_dropped_at_anchor", "锚点月缺席特征数", len(env["features_dropped_at_anchor"]), 12, 0)
P.adds("N21", F + ".features_dropped_at_anchor", "缺席特征名单(排序)", ",".join(sorted(env["features_dropped_at_anchor"])), "CORE_CPI_yoy,CPI_yoy,FED_FUNDS_d12m,FED_FUNDS_level,GDP_yoy,HY_IG_gap_d12m,HY_OAS_d12m,INDPRO_yoy,NFP_3m_chg,RSAFS_yoy,SPX_PE_TTM_level,UNEMPLOYMENT_level")
P.addb("N22", F + ".features_dropped_at_anchor", "HY_IG_gap_d12m/HY_OAS_d12m 属历史长度不足", all("hist" in env["features_dropped_at_anchor"][k] for k in ("HY_IG_gap_d12m", "HY_OAS_d12m")))
P.addb("N23", F + ".features_dropped_at_anchor", "CORE_CPI_yoy/CPI_yoy/GDP_yoy/SPX_PE_TTM_level 属序列止于锚前两个月", all("止于2026-09" in env["features_dropped_at_anchor"][k] for k in ("CORE_CPI_yoy", "CPI_yoy", "GDP_yoy", "SPX_PE_TTM_level")))
P.addb("N24", F + ".features_dropped_at_anchor", "FED_FUNDS_*/INDPRO_yoy/NFP_3m_chg/RSAFS_yoy/UNEMPLOYMENT_level 属锚点月无观测(止于锚前一月)", all("止于2026-10" in env["features_dropped_at_anchor"][k] for k in ("FED_FUNDS_d12m", "FED_FUNDS_level", "INDPRO_yoy", "NFP_3m_chg", "RSAFS_yoy", "UNEMPLOYMENT_level")))
P.adds("N25", F + ".top[0].aftermath", "事后表现四项", ",".join(k for k in env["top"][0]["aftermath"] if k in ("SPX", "UST_10Y", "DXY", "GOLD_F")), "SPX,UST_10Y,DXY,GOLD_F")
P.addb("N26", F + ".research_mode_gate", "描述性可用/事件研究被阻断", env["research_mode_gate"]["descriptive"] == "available" and env["research_mode_gate"]["event_study"].startswith("blocked"))
P.adds("N27", F + ".anchor_month", "anchor_month", env["anchor_month"], "2026-11")
P.add("N28", F + ".feature_window_months", "feature_window_months", env["feature_window_months"], 12, 0)

# ---------- 情景阈值 ----------
P.add("C01", "算术", "DFEDTARU 4.0 + 标准步长 0.25", at_or_before(SS, "DFEDTARU", CUT)[1] + 0.25, 4.25, 2)
P.add("C02", "算术", "JP_POLICY_RATE 1.227 + 0.05 后上取整到分位", math.ceil((mv(SS, "JP_POLICY_RATE", "2026-10") + 0.05) * 100 - 1e-9) / 100.0, 1.28, 2)
P.add("C03", "算术", "CN_LPR_1Y 3.0 - 0.10", at_or_before(SS, "CN_LPR_1Y", CUT)[1] - 0.10, 2.90, 2)
P.addb("C04", SNAP, "截止日 DFEDTARU 4.0 未达 4.25", at_or_before(SS, "DFEDTARU", CUT)[1] < 4.25)
P.addb("C05", SNAP, "截止日 JP_POLICY_RATE 1.227 < 1.28", mv(SS, "JP_POLICY_RATE", "2026-10") < 1.28)
P.addb("C06", SNAP, "截止日 CN_LPR_1Y 3.0 > 2.90", at_or_before(SS, "CN_LPR_1Y", CUT)[1] > 2.90)
P.adds("C07", "datetime", "2027-02-28 合法日期/星期", wd("2027-02-28"), "Sunday")
_y, _m = (2026, 11 + 3); _y += (_m - 1) // 12; _m = (_m - 1) % 12 + 1
P.adds("C08", "datetime", "研究截止 2026-11-23 + 3 个日历月(年月进位后日取 23)", "%04d-%02d-23" % (_y, _m), "2027-02-23")
P.add("C09", "datetime", "2026-11-23→2027-02-28 天数", days(CUT, "2027-02-28"), 97, 0)
P.save(outdir, "pts_c.json")
print("TIPS/UST/BEI 2026-10-14..10-23:")
for d in [x[0] for x in series(SS, "TIPS_10Y") if "2026-10-14" <= x[0] <= "2026-10-23"]:
    print("  ", d, wd(d)[:3], "UST", at(SS, "UST_10Y", d), "TIPS", at(SS, "TIPS_10Y", d), "BEI", at(SS, "BEI_10Y", d))
print("TIPS/UST/BEI 2025-11-14..11-20:")
for d in [x[0] for x in series(SS, "TIPS_10Y") if "2025-11-14" <= x[0] <= "2025-11-20"]:
    print("  ", d, "UST", at(SS, "UST_10Y", d), "TIPS", at(SS, "TIPS_10Y", d), "BEI", at(SS, "BEI_10Y", d))
print("JP_POLICY_RATE monthly 2025-09..2026-10:", [(d[:7], v) for d, v in series(SS, "JP_POLICY_RATE") if "2025-09" <= d[:7] <= "2026-10"])
print("JP_POLICY_RATE first obs:", series(SS, "JP_POLICY_RATE")[0])
