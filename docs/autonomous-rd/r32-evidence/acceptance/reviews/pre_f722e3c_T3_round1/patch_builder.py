#!/usr/bin/env python3
"""Seat-owned patcher: applies exact-once string replacements to build_outputs.py (the seat's own file)
so that every number/quote in PROSE/VERDICT matches the probes verify_fixnums.py / verify_registry.py.
Usage: python3 -I patch_builder.py <build_outputs.py>
"""
import sys

P = sys.argv[1]
with open(P, "r", encoding="utf-8") as fh:
    src = fh.read()

PAIRS = [
    # MA-1 / MA-2 point mapping
    ('''dict(id="MA-1", sev="MAJOR", pts=["P76", "P77"],''', '''dict(id="MA-1", sev="MAJOR", pts=["P77"],'''),
    # MA-6: precise distance wording
    ('''距两地最近政策日 2026-10-30 两周以上,11-23 已回落 15.7%''', '''距两地最近政策日 2026-10-30 已隔两周(11-13 起),11-23 已回落 15.7%'''),
    ('''距两地最近政策日(2026-10-30)两周以上,观测偏向全局冲击解释''', '''距两地最近政策日(2026-10-30)已隔两周,观测偏向全局冲击解释'''),
    ('''VIX 跳升集中在 11-13→11-20 周、距最近政策日两周以上——漏披露(MAJOR)。''', '''VIX 跳升集中在 11-13→11-20 周、距最近政策日(2026-10-30)已隔两周——漏披露(MAJOR)。'''),
    # MA-7: engine rule text
    ('''引擎发布面 point_values…publication_date=2026-09-16(关键数字表同)。''', '''引擎发布面 point_values…publication_date=2026-09-16(关键数字表同;规则文本「ECB 决议日当日公布(变更日观测)」把决议日等同于变更日观测)。'''),
    # MI-2: exact fact-row wording (cause left open by the engine)
    ('''事实行 issue 为「ECB_DFR观测日滞后68天」(频次新鲜度规则,注册表 max_calendar_lag_days=10);''', '''事实行 issues[0] 为 frequency 类「ECB_DFR观测日滞后68天(>10天有效窗,daily频;未发布或采集失败,不得当作最新一期)」(成因留两可;注册表 freshness.max_calendar_lag_days=10);'''),
    # MI-5: exact engine detail, drop unverified 1.42
    ('''判断档引用东京 1.42/2.73 而未披露该列名''', '''判断档 C1 引用东京最新读数 2.73 而未披露该列名'''),
    ('''含 JP_CPI_TOKYO_YOY(来源文件在场而指标缺席),MAP''', '''含 JP_CPI_TOKYO_YOY(noncore_missing_detail:「来源文件在场而指标缺席(采集遗漏或子源缺席——档内无该指标子源状态记录,不可区分)」),MAP'''),
    # MI-9: accurate registry quote, no cross-base claim
    ('''注册表 JP_CPI_YOY calc 记「zmi2025aa(2025基)+zmi2020aa(2020基)双档拼接(新基优先,重叠差>0.10pp 告警)」;2026-10 对 2025-10 的同比对照跨拼接口径,报告未披露。不影响 −0.55pp 的方向。''', '''注册表 JP_CPI_YOY calc 记「zmi2025aa(2025基)+zmi2020aa(2020基)双档水平值,各自基期内做严格同月同比后拼接(新基优先,重叠差>0.10pp 告警)」;报告与判断档的口径披露未提及拼接口径,2026-10 对 2025-10 的对照落在哪一基期档只读面不可核。不影响 −0.55pp 的方向,属披露可改进。'''),
    ('''口径披露补:全国 CPI 同比为 2020 基/2025 基拼接序列(注册表),2026-10 对 2025-10 的对照跨拼接口径。''', '''口径披露补:全国 CPI 同比为 2025 基/2020 基拼接序列(各自基期内同月同比,新基优先,重叠差>0.10pp 告警)。'''),
    ('''全国 CPI 对照跨 2020 基/2025 基拼接未披露(MINOR)。''', '''全国 CPI 序列为 2025 基/2020 基拼接,口径未披露(MINOR)。'''),
    # severity attribution of every non-OK point, computed and asserted
    ('''N = SUM["recompute_points"]\n''', '''NONOK = {p["id"] for p in ROWS if p["status"] != "OK"}
COV = {}
for _it in ITEMS:
    for _pid in _it["pts"]:
        assert _pid not in COV, "point mapped twice: %s" % _pid
        COV[_pid] = _it["sev"]
_num = lambda x: int(x[1:])
MAJ_PTS = sorted((pid for pid, s in COV.items() if s == "MAJOR" and pid in NONOK), key=_num)
MIN_PTS = sorted((pid for pid, s in COV.items() if s == "MINOR" and pid in NONOK), key=_num)
NIT_PTS = sorted((pid for pid, s in COV.items() if s == "NIT" and pid in NONOK), key=_num)
assert set(MAJ_PTS) | set(MIN_PTS) | set(NIT_PTS) == NONOK, sorted(set(MAJ_PTS) | set(MIN_PTS) | set(NIT_PTS) ^ NONOK)
N = SUM["recompute_points"]
'''),
    ('''一致 {ok}、偏离 {dev}、不可核 {unv}(偏离合计 {mis});''', '''一致 {ok}、偏离 {dev}、不可核 {unv}(偏离合计 {mis};分级归属: MAJOR 相关 {nmp}、MINOR 相关 {nmip}、NIT 级 {nnp});'''),
    ('''nmin=len(MIN), nnit=len(NIT))''', '''nmin=len(MIN), nnit=len(NIT), nmp=len(MAJ_PTS), nmip=len(MIN_PTS), nnp=len(NIT_PTS))'''),
    # notes: only category counts taken from recompute_summary.json by_cat
    ('''其中点值锚格 12/12(按「公布日≤锚日」发布纪律取值)、同比基期与差值、政策目标/生效日/距离天数、三利率分解、资产月窗 8/8、"''', '''其中截止日 4/4、点值锚格 12/12(按「公布日≤锚日」发布纪律取值)、同比基期 6/6、三利率与资产月窗 11/11、传导链证据级 9/9、两地目标利率与同比 3/3 整类一致,政策目标/生效日/距离天数、"'''),
    ('''"转折候选值与逐月路径、发布规则算术 8/8 均与证据面一致,未见''', '''"转折候选值与逐月路径各点一致,未见'''),
    ('''L.append("说明: 「偏离」含''', '''L.append("偏离与不可核的分级归属: MAJOR 相关 %s;MINOR 相关 %s;NIT 级 %s(逐条见第四节)。\\n" % ("、".join(MAJ_PTS), "、".join(MIN_PTS), "、".join(NIT_PTS)))
L.append("说明: 「偏离」含'''),
]
for old, new in PAIRS:
    c = src.count(old)
    assert c == 1, "expected exactly one occurrence, got %d: %s" % (c, old[:50])
    src = src.replace(old, new)
with open(P, "w", encoding="utf-8") as fh:
    fh.write(src)
print("applied %d patches" % len(PAIRS))
