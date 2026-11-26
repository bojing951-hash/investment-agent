#!/usr/bin/python3 -I
# s06a: 对首轮检查设计中属于「检查口径」而非受审稿偏差的 6 处予以更正(浮点精度/符号约定/『同窗』所指窗口/所引四位小数之差),
#       并把 E25 的键名写明。更正理由逐条记入 PROSE。只改本席脚本, 不触碰受审文件。
import sys, os
out = sys.argv[1]
def patch(fn, pairs):
    p = os.path.join(out, fn)
    s = open(p, encoding="utf-8").read()
    for old, new in pairs:
        assert s.count(old) == 1, (fn, old[:60], s.count(old))
        s = s.replace(old, new)
    open(p, "w", encoding="utf-8").write(s)
    print("patched", fn, len(pairs))
patch("s02a_policy_energy.py", [
    ('P.addb("E25", SNAP, "WTI_F 2026-11-09..11-23 全部 < 锚", all(v < w0[1] for d, v in late if d >= first_below))',
     'P.addb("E25", SNAP, "WTI_F 2026-11-09..11-23 全部 < 锚(受审稿『11-09 起再度跌破该锚』的字面持续性; 实测 11 个观测中 9 个低于锚, 11-12=88.74、11-13=88.56 回到锚上方)", all(v < w0[1] for d, v in late if d >= first_below))\n'
     'P.addb("E29", SNAP, "WTI_F 2026-09-01..2026-10-31 观测全部 > 锚(受审稿『期货 9 月初至 10 月底的观测全部高于三个月前锚』)", all(v > w0[1] for d, v in series(SS, "WTI_F") if "2026-09-01" <= d <= "2026-10-31"), "观测数 %d, 最低 %.2f" % (len([1 for d, v in series(SS, "WTI_F") if "2026-09-01" <= d <= "2026-10-31"]), min(v for d, v in series(SS, "WTI_F") if "2026-09-01" <= d <= "2026-10-31")))'),
])
patch("s02b_macro.py", [
    ('P.add("T04", SNAP, "核心CPI同比 2026-08 - 2026-05 (pp)", yoy(SS, "CORE_CPI", "2026-08") - yoy(SS, "CORE_CPI", "2026-05"), -0.3767, 4)',
     '_y05, _y08 = yoy(SS, "CORE_CPI", "2026-05"), yoy(SS, "CORE_CPI", "2026-08")\n'
     'P.add("T04", SNAP, "核心CPI同比 所引两位四位小数之差 2026-08 − 2026-05 (pp)(未舍入差 %.6f, 四舍五入为 -0.3768)" % (_y08 - _y05), round(_y08, 4) - round(_y05, 4), -0.3767, 4)\n'
     'P.add("T04b", "report.json research_plan.turning_candidates.candidates[CORE_CPI].delta", "引擎候选面 CORE_CPI delta(受审稿『三个月回落 0.3767 个百分点』)", [c for c in rep["research_plan"]["turning_candidates"]["candidates"] if c["metric_id"] == "CORE_CPI"][0]["delta"], -0.3767, 4)'),
])
patch("s02c_assets_rates.py", [
    ('{"SPX": 7623.680176, "NIKKEI225": 62693.16, "SHCOMP": 3690.4753, "DAX": 25181.650391, "VIX": 19.450001}[mid], 4); i += 1',
     '{"SPX": 7623.680176, "NIKKEI225": 62693.16, "SHCOMP": 3690.4753, "DAX": 25181.650391, "VIX": 19.450001}[mid], 6); i += 1'),
    ('P.add("A31", SNAP, "引擎窗 SPX 与 NIKKEI225 跌幅落差(pp)", pct(at(SS, "NIKKEI225", "2026-10-23"), at(SS, "NIKKEI225", "2026-11-20")) - pct(at(SS, "SPX", "2026-10-23"), at(SS, "SPX", CUT)), 4.47, 2)',
     'P.add("A31", SNAP, "引擎窗 NIKKEI225 与 SPX 跌幅落差绝对值(pp)(受审稿『两者跌幅相差四点四七个百分点』)", abs(pct(at(SS, "NIKKEI225", "2026-10-23"), at(SS, "NIKKEI225", "2026-11-20")) - pct(at(SS, "SPX", "2026-10-23"), at(SS, "SPX", CUT))), 4.47, 2)'),
    ('P.add("A40", SNAP, "USDJPY 共同交易日窗(10-20→11-19) %", pct(at(SS, "USDJPY", "2026-10-20"), at(SS, "USDJPY", "2026-11-19")), 1.82, 2, "若『同窗』指 10-20→11-19")',
     'P.addb("A40", SNAP, "受审稿『同窗 USDJPY 156.494→159.347』两端值=引擎月窗 2026-10-23→2026-11-23 的观测(非 10-20→11-19 共同交易日窗; 该窗为 158.523→159.381, 见 out_s05_extra.txt)", abs(at(SS, "USDJPY", "2026-10-23") - 156.494) < 1e-3 and abs(at_or_before(SS, "USDJPY", CUT)[1] - 159.347) < 1e-3 and abs(at(SS, "USDJPY", "2026-10-20") - 156.494) > 0.5)\n'
     'P.addb("A44", SNAP, "USDJPY 在三窗(10-20→11-19 / 10-23→11-23 / 10-23→11-20)均为美元对日元走强(方向稳健)", all(pct(at(SS, "USDJPY", a), at(SS, "USDJPY", b)) > 0 for a, b in (("2026-10-20", "2026-11-19"), ("2026-10-23", "2026-11-23"), ("2026-10-23", "2026-11-20"))))\n'
     'P.addb("A45", SNAP, "USDCNY 在三窗均未走强(方向稳健)", all(pct(at(SS, "USDCNY", a), at(SS, "USDCNY", b)) < 0 for a, b in (("2026-10-20", "2026-11-19"), ("2026-10-23", "2026-11-23"), ("2026-10-23", "2026-11-20"))))'),
])
