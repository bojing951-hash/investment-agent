#!/usr/bin/python3 -I
"""席位自写脚本 s18: 第 4 节六查所用反方攻击的直算数据(只读; 全部为探针, 不计复算点).

用法: /usr/bin/python3 -I s18_counter.py <快照> <report.json> <agent_judgment.json> <席位目录>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seatlib import Points, Store, load_json  # noqa: E402

SNAP, REP, AJ, SEAT = sys.argv[1:5]
snap = load_json(SNAP)
rep = load_json(REP)
aj = load_json(AJ)
S = Store(snap)
rp = rep["research_plan"]
SRC = "root_overlay/data/daily/research_snapshot_20261123.json:series_store"
P = Points("④查", "六查/反方攻击直算数据(探针, 不计复算点)")


def probe(pid, computed, source, note=""):
    P.add_probe(pid, "—(反方攻击探针, 受审稿无对应数字)", computed, source, note)


def chg(mid, a, b):
    x, y = S.exact(mid, a), S.exact(mid, b)
    if x is None or y is None:
        return f"{a}→{b}: 缺观测({x},{y})"
    return f"{a} {x} → {b} {y}: {y - x:+.4f} ({(y / x - 1) * 100:+.2f}%)"


# ---- 攻击 C1: 同月对齐后「同步走高、欧元区幅度更大」是否仍成立
for a, b in (("2026-07", "2026-09"), ("2026-07", "2026-08"), ("2026-08", "2026-09"), ("2026-06", "2026-09")):
    ea = S.mval("EA_HICP_YOY", b) - S.mval("EA_HICP_YOY", a)
    us = S.yoy("CPI", b)[0] - S.yoy("CPI", a)[0]
    uc = S.yoy("CORE_CPI", b)[0] - S.yoy("CORE_CPI", a)[0]
    probe(f"K1-同月对齐 {a}→{b} 同比变动(pp): EA / US headline / US core", f"{ea:+.4f} / {us:+.4f} / {uc:+.4f}", f"{SRC}.EA_HICP_YOY/CPI/CORE_CPI(同比)")
ea25 = [(d[:7], v) for d, v in zip(*S.series("EA_HICP_YOY")) if "2023-10" <= d[:7] <= "2026-09"]
probe("K1-EA_HICP_YOY 2023-10..2026-09 最大值(检验「年内新高」是否只是更高历史高位下的保守表述)", f"max {max(v for _, v in ea25)}@{max(ea25, key=lambda x: x[1])[0]}",
            f"{SRC}.EA_HICP_YOY[2023-10..2026-09]")
u26 = [(d[:7], v) for d, v in zip(*S.series("UNEMPLOYMENT")) if d[:7] >= "2025-11"]
probe("K2-失业率 2025-11..2026-10 逐月(检验「走平」)", "; ".join(f"{a}:{v}" for a, v in u26), f"{SRC}.UNEMPLOYMENT[2025-11..2026-10]")
lv = S.exact("INDPRO", "2026-10-01") / S.exact("INDPRO", "2026-07-01") - 1
base = S.exact("INDPRO", "2025-10-01") / S.exact("INDPRO", "2025-07-01") - 1
dec = (1 + lv) / (1 + base) - 1
probe("K2-INDPRO 同比三个月变动分解: 水平变动 × 上年基数变动 → 隐含同比变动", f"水平 {lv * 100:+.3f}% × 基数 {base * 100:+.3f}% ⇒ {dec * 100:+.3f}pp (直算同比变动 {(S.yoy('INDPRO', '2026-10')[0] - S.yoy('INDPRO', '2026-07')[0]):+.4f}pp)",
            f"{SRC}.INDPRO[2025-07, 2025-10, 2026-07, 2026-10]")

# ---- 攻击 传导链环2: 「实无可区分指标」——在场但未被用于区分的利率面(2Y/5Y/曲线)
for nm, a, b in (("近一月 2026-10-20→2026-11-19", "2026-10-20", "2026-11-19"), ("三个月 2026-08-19→2026-11-19", "2026-08-19", "2026-11-19"), ("12个月 2025-11-19→2026-11-19", "2025-11-19", "2026-11-19")):
    parts = [chg(m, a, b) for m in ("UST_2Y", "UST_5Y", "UST_10Y", "UST_30Y", "TIPS_5Y", "TIPS_10Y", "BEI_5Y", "BEI_10Y", "CURVE_2S10S")]
    probe(f"K3-利率面 {nm}", " | ".join(parts), f"{SRC}.UST_2Y/UST_5Y/UST_10Y/UST_30Y/TIPS_5Y/TIPS_10Y/BEI_5Y/BEI_10Y/CURVE_2S10S")

# ---- 攻击 传导链环3 / 总判断「风险收缩组合」: 引擎资产月窗内其余资产与未被引用的在场面
am = {r["metric_id"]: r for r in rp["asset_moves"]["rows"]}
probe("K4-引擎资产月窗 8 行(受审稿只回贴 5 行)", "; ".join(f"{m}:{r['chg_pct']:+.2f}%[{r['window']}]" for m, r in am.items()), "report.json:research_plan.asset_moves.rows")
for m in ("SPX", "NDX", "RUT", "DAX", "CAC40", "SHCOMP", "HSI", "NIKKEI225", "GOLD_F", "SILVER_F", "DXY", "EURUSD", "USDJPY", "VIX", "HY_OAS", "IG_OAS", "UST_10Y"):
    if not S.has(m):
        probe(f"K5-{m}", "序列库无", f"{SRC}")
        continue
    probe(f"K5-{m} 近一月(10-23→最新) / 三个月(08-19→最新) / 12个月(2025-11-19→最新)",
                f"{chg(m, '2026-10-23', S.series(m)[0][-1])} || {chg(m, '2026-08-19', S.series(m)[0][-1])} || {chg(m, '2025-11-19', S.series(m)[0][-1])}", f"{SRC}.{m}")

# ---- 攻击 M1 环3: 日本央行决议/生效/维持日前后 USDJPY 与 NIKKEI225 的在场反应
for nm, a, b in (("决议日前后 2026-09-17→2026-09-21", "2026-09-17", "2026-09-21"), ("决议日至生效后 2026-09-18→2026-09-25", "2026-09-18", "2026-09-25"),
                 ("确认维持前后 2026-10-29→2026-11-02", "2026-10-29", "2026-11-02")):
    probe(f"K6-{nm}", f"USDJPY {chg('USDJPY', a, b)} | NIKKEI225 {chg('NIKKEI225', a, b)}", f"{SRC}.USDJPY/NIKKEI225")

# ---- 攻击 C3: 月均 2026-09 的决议跨月均值效应量级(需此前目标水平; 冻结日历无此前目标 → 不可核)
d, v = S.series("JP_POLICY_RATE")
tail = [(a, b) for a, b in zip(d, v) if a >= "2026-03-01"]
probe("K7-JP_POLICY_RATE 2026-03..2026-10 月均", "; ".join(f"{a[:7]}:{b}" for a, b in tail), f"{SRC}.JP_POLICY_RATE")
probe("K8-冻结日历 2026-09 决议前的日本央行目标水平(用于检验「约 1.0→1.25」的台阶幅度)", "日历无此前目标条目(18 条中仅 2026-09/2026-10 两条日本央行实录)→ 不可核, 受审稿亦未写此前目标",
            "root_overlay/config/release_calendar.json:entries")
P.save("points_16_counter.json")
