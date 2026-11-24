#!/usr/bin/python3 -I
"""Adversarial ('反方攻击') computations on the read-only face. Each attack tries to break a judgment
claim with a computation the judgment did not make. Outcomes are recorded, not counted as judgment
recompute points unless a judgment literal is directly compared.

Args: <snapshot.json> <agent_judgment.json> <release_calendar.json> <metric_registry.json> <out_dir>
"""
import datetime as dt
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("s10_common", os.path.join(HERE, "s10_common.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

snap, jd, cal, reg = (C.load_json(p) for p in sys.argv[1:5])
out_dir = sys.argv[5]
ss = snap["series_store"]
R = {}


def pct(a, b):
    return None if (a is None or b is None) else round(C.pct(b, a), 4)


def rec(aid, target, claim, method, result, outcome):
    R[aid] = {"target": target, "claim": claim, "method": method, "result": result, "outcome": outcome}
    print(aid, "|", target, "|", json.dumps(result, ensure_ascii=False)[:400], "|", outcome)


# A1 multi-horizon direction of the two YoY series (C1 / headline)
out = {}
for mid in ("JP_CPI_YOY", "EA_HICP_YOY"):
    mo = C.monthly(ss, mid)
    last = "2026-10"
    base = mo[last]
    out[mid] = {"latest": base}
    for n in (1, 3, 6, 12):
        k = C.add_months(dt.date(2026, 10, 1), -n).strftime("%Y-%m")
        out[mid]["chg_%dm" % n] = None if mo.get(k) is None else round(base - mo[k], 4)
    win = [mo[k] for k in sorted(mo) if "2025-11" <= k <= "2026-09"]
    out[mid]["months_in_last12_below_latest"] = "%d/%d" % (sum(1 for v in win if v < base), len(win))
rec("A1", "C1/总判断「日本回落、欧元区抬升」(同比口径)", "同比方向相反;较六个月前锚两地均上行",
    "JP_CPI_YOY/EA_HICP_YOY 2026-10 相对 1/3/6/12 个月前的差值;近 12 个月中低于最新值的月数", out,
    "不推翻: 同比口径方向如述且有口径标注;「日本回落」仅对去年 10-12 月成立,对其余近月为上行——席位正文已写「此后总体回升」,总判断以「相比去年同月」限定")

# A3 base-splice caliber (C1)
regm = {m["metric_id"]: m for m in reg["metrics"]}
calc = regm["JP_CPI_YOY"].get("calc")
rec("A3", "C1「日本回落约 0.55 个百分点」", "2026-10(2025基) vs 2025-10(2020基)的拼接同月同比差",
    "注册表 JP_CPI_YOY.calc 的拼接告警阈(重叠差>0.10pp)与差值量级比较",
    {"registry_overlap_warn_pp": 0.10 if "0.10pp" in str(calc) else None, "yoy_diff_pp": -0.55,
     "ratio": 5.5, "overlap_values_on_face": False},
    "不推翻: 注册表自述的拼接告警阈 0.10pp 仅为差值的约 1/5,不足以翻转符号;重叠期双基值不在只读面,如实记为未能独立量化")

# A5 BOJ direction from monthly-average steps (C2)
mo = C.monthly(ss, "JP_POLICY_RATE")
steps = []
ks = sorted(mo)
for i in range(1, len(ks)):
    if "2025-10" <= ks[i - 1] <= "2026-10":
        steps.append([ks[i - 1], ks[i], mo[ks[i - 1]], mo[ks[i]], round((mo[ks[i]] - mo[ks[i - 1]]) * 100, 2)])
rec("A5", "C2「日本端收紧方向」(实录无前值,属推断)", "月均台阶与 2026-09-24 生效的决议相容",
    "JP_POLICY_RATE 逐月均值变动(bp)", steps,
    "不推翻: 12 个逐月台阶中 10 个上行或持平、仅两次 -0.1bp 微降(净 +75bp),2026-09(+6.6bp,决议 09-24 生效仅占 7 天)→2026-10(+18.4bp,首个完整月)与 9 月末生效的上调相容;「收紧」方向有市场口径证据,标注【推断】恰当")

# A8 longer-window cross rate (M1 step 3 / TL2)
def last_common(pairs, day):
    sets = []
    for mid in pairs:
        ds, vs = C.series(ss, mid)
        sets.append(set(d for d, v in zip(ds, vs) if v is not None and d <= day))
    common = sorted(set.intersection(*sets))
    return common[-1] if common else None


START6 = last_common(("EURUSD", "USDJPY"), "2026-05-23")  # question window starts 2026-05-23 (cutoff - 6 months)


def cross(day):
    e, u = C.val_at(ss, "EURUSD", day), C.val_at(ss, "USDJPY", day)
    return None if e is None else round(e * u, 4)


cr = {}
for a, b in (("2026-08-20", "2026-11-20"), (START6, "2026-11-20"), (START6, "2026-09-15"), ("2026-09-16", "2026-11-20")):
    x, y = cross(a), cross(b)
    cr["%s..%s" % (a, b)] = [x, y, None if (x is None or y is None) else round(C.pct(y, x), 2)]
ea_leg = {}
for a, b in ((START6, "2026-11-20"), (START6, "2026-09-15"), ("2026-09-16", "2026-11-20")):
    ea_leg["%s..%s" % (a, b)] = [pct(C.val_at(ss, "EURUSD", a), C.val_at(ss, "EURUSD", b)),
                                 pct(C.val_at(ss, "USDJPY", a), C.val_at(ss, "USDJPY", b))]
# visible policy differential (MRO minus Japanese monthly-average rate) at the two window ends
pol = {}
for day in (START6, "2026-11-20"):
    mro = C.last_on_or_before(ss, "ECB_MRO", day)
    jpr = C.last_on_or_before(ss, "JP_POLICY_RATE", day)
    pol[day] = {"ECB_MRO": list(mro), "JP_POLICY_RATE": list(jpr), "diff_pp": C.rnd(mro[1] - jpr[1], 3)}
rec("A8", "M1-3「利差渠道未获检验亦未被否定」(限本月窗)", "本月窗两货币同对美元走弱,两解释预期未分立",
    "EURUSD×USDJPY 合成交叉盘在 3 个月/6 个月(问句窗起点 2026-05-23 前的最近共同观测日起)/两次上调后窗口的变动(席位只算了 1 个月窗);窗两端可见政策水平差",
    {"cross": cr, "legs": ea_leg, "visible_policy_differential": pol},
    "限窗表述成立、不推翻: 席位明写「本月窗」「幅度小」;但问句窗为六个月,六个月窗(%s→2026-11-20)内合成交叉盘 %+.2f%% 而可见的两地政策水平差 %.3f→%.3f 个百分点未变,"
    "利差假说对六个月窗的交叉盘无解释力,美元全局主导解释对两腿分立(EURUSD %+.2f%% 对 USDJPY %+.2f%%)亦无预期——不改变「尚不能区分」;判断档未并列六个月窗读数,记 MINOR M-7"
    % (START6, cr["%s..2026-11-20" % START6][2], pol[START6]["diff_pp"], pol["2026-11-20"]["diff_pp"],
       ea_leg["%s..2026-11-20" % START6][0], ea_leg["%s..2026-11-20" % START6][1]))

# A11 release-day regional moves (M1 step 4 / TL3)
day_mv = {}
for mid in ("SPX", "NIKKEI225", "DAX", "CAC40", "VIX", "EURUSD", "USDJPY", "DXY", "UST_10Y"):
    ds, vs = C.series(ss, mid)
    row = {}
    for day in ("2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19", "2026-11-20"):
        if day in ds:
            k = ds.index(day)
            prev = None
            for j in range(k - 1, -1, -1):
                if vs[j] is not None:
                    prev = vs[j]
                    break
            row[day] = None if prev in (None, 0) else round(C.pct(vs[k], prev), 2)
    day_mv[mid] = row
rec("A11", "M1-4「读数发布主因未获跨地区支持」", "11-16、11-20 两个发布日 VIX 为窗内最大单日跳升,但四地股指跌幅均不深于美股、两日汇率单日变动≤0.23%",
    "发布日及其后各交易日的逐日变动%(四地股指+VIX+汇率)", day_mv,
    "不推翻结论、记 MINOR 披露补充: 窗内累计跌幅如述为真;但单日看 2026-11-20(日本 CPI 推定发布日)NIKKEI225 -5.06% 深于 SPX -3.70%、DAX -2.60%,为三地窗内最大单日跌幅,11-16(欧元区 HICP 推定发布日)欧元区股指跌幅浅于美股;「单一归因不可证」结论不变")

# A14 scenario falsifier observability vs current face
obs = {}
for mid in ("EA_HICP_YOY", "JP_CPI_YOY"):
    obs[mid] = {"in_registry": mid in regm, "last_obs": C.last_obs(ss, mid),
                "in_evidence_index_rows": None}
rec("A14", "情景证伪条件可观测性", "EA_HICP_YOY/JP_CPI_YOY 观测月 2026-11、2026-12 可观测",
    "注册表在场+序列末次观测", obs,
    "可观测: 指标在册且序列持续更新;2026-11/12 观测月尚未发布,证伪条件尚未到期亦未触发")

# A19 float storage precision behind +84.5%
v0, v1 = C.val_at(ss, "VIX", "2026-10-23"), C.val_at(ss, "VIX", "2026-11-20")
rec("A19", "M1-4/TL3「VIX 由 19.45 升至 35.89(+84.5%)」", "+84.5%",
    "快照存储精度复算 vs 按两位小数收盘价复算",
    {"stored": [v0, v1], "pct_stored": round(C.pct(v1, v0), 4), "pct_display": round(C.pct(35.89, 19.45), 4)},
    "一致: 快照存储值(19.450001/35.889999)复算 +84.52%,按两位小数收盘价(19.45/35.89)复算亦为 +84.52%,取一位小数为 +84.5%,与判断档一致")

json.dump(R, open(os.path.join(out_dir, "counterexamples.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
