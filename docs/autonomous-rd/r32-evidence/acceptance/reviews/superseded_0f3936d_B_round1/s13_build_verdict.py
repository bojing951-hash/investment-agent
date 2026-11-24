#!/usr/bin/python3 -I
# Seat script 13: build VERDICT-round1.json from the recompute table (guarantees valid UTF-8 JSON).
# usage: s13_build_verdict.py <recompute_points.json> <VERDICT-round1.json>
import json, sys

pts_path, out_path = sys.argv[1], sys.argv[2]
tab = json.load(open(pts_path, encoding="utf-8"))
pts = tab["points"]
by_id = {p["id"]: p for p in pts}
mis = [p for p in pts if not p["match"]]
assert [p["id"] for p in mis] == ["J5-S1-falsifier-reachable"], [p["id"] for p in mis]
j5 = by_id["J5-S1-falsifier-reachable"]

S1_ORIG = "若 2027-01 前发布的 EA_HICP_YOY 同比连续两个月低于 3.0%,通胀粘性假设被证伪"
S1_FIX = "若 2026-12 与 2027-01 两月发布的 EA_HICP_YOY 同比(对应 2026-11、2026-12 观测月,规则发布日 2026-12-16、2027-01-16,均不晚于期限 2027-02-15)连续两个月低于 3.0%,通胀粘性假设被证伪"

items = [
    {
        "severity": "MAJOR",
        "where": "agent_judgment.json → l4.scenarios[id=S1-INFL-STICKY].rows.falsification.threshold;逐字渲染于 MAP_REPORT.md 第 146 行、FULL_REPORT.md 第 81 行、report.md 第 90 行;相关披露 quality_gate_notes[2]「两情景各给出可观测触发条件与失效阈值」",
        "note": "证伪条件按字面不可触发(规程第 3 节⑨「期限与截止日读数相容」、第 5 节「证伪条件不可观测」): 「2027-01 前发布」且晚于截止日 2026-11-23 的 EA_HICP_YOY 只有 2026-11 观测月一次发布(规则发布日 2026-12-16,月末+16 天推定,与 MAP_REPORT.md 第 181 行发布日期列同口径);能与它相邻的 2026-10 读数=4.0 已于 2026-11-16 发布,不低于 3.0,「连续两个月低于 3.0%」在 2027-01 前不可能成立——该证伪条件在截止日已确定为假,S1 在其自述期限内不可被证伪;且与本情景触发条件(2026-12 或 2027-01 发布)及 S2 证伪句(2026-12 与 2027-01 两月发布)的发布月口径不一致。改句中两个观测月在截止日均未发布,条件可观测、可触发;阈值 3.0% 与期限 2027-02-15 不变。",
        "original": S1_ORIG,
        "fix": S1_FIX,
    },
    {
        "severity": "MINOR",
        "where": "agent_judgment.json → l3.contradictions[id=C1-INFL-SYNC].statement 括注;FULL_REPORT.md 第 58 行;report.md 第 67 行",
        "note": "「更早月份位次有交叉」字面属实但缺时间范围: 全史 106 个可比月(2017-11 起)中欧元区高于美国仅 2022-07 至 2023-09(15 个月)与 2026-09,其前 34 个可比月(2023-10 至 2026-08)均为欧元区低于美国,易被读成近年频繁交叉。建议改句: 「九月为 2023-09 以来首个高于美国的可比月份(2022-07 至 2023-09 曾持续高于美国)」。",
        "original": "两地最新可比同月为九月，更早月份位次有交叉",
        "fix": "",
    },
    {
        "severity": "MINOR",
        "where": "agent_judgment.json → reader_map.transmission[chain_id=CH-INFL-RATES-RISKOFF].links[0].observed_fact;MAP_REPORT.md 传导面第 1 环",
        "note": "早段端点 2026-02-27 的 2.25→2026-05-04 的 2.50 是该窗(2026-02-20 至 2026-05-04)的最小值→最大值(2026-05-04 亦为 2026 年内最高),未标注;月末对月末(2026-02-27→2026-05-29)仅 +13bp 至 2.38。「尚不能区分」裁定不变。建议注明「段内低点→峰值」或改用月末端点并给出幅度。",
        "original": "BEI_10Y 自 2026-02-27 的 2.25 升至 2026-05-04 的 2.50，合主解释",
        "fix": "",
    },
    {
        "severity": "MINOR",
        "where": "agent_judgment.json → l3.mechanism_chains[id=M1-JP-RATE-PATH].links[step=3].text;FULL_REPORT.md 第 71 行;report.md 第 82 行",
        "note": "「利差仍高」在 E2 环以事实位措辞出现,而本问证据面无日美利差序列(JGB 收益率在册未采);在场的是 USDJPY 159.35(2026-11-23,12 个月窗内约 71% 分位)。建议改为「风险收缩+日元仍处低位(USDJPY 高位)」或把「利差」标为【假设】。",
        "original": "组合更接近「风险收缩+利差仍高」的混合态",
        "fix": "",
    },
    {
        "severity": "MINOR",
        "where": "agent_judgment.json → l3.contradictions[id=C1-INFL-SYNC].competing_explanations[0];l4.scenarios[id=S2-INFL-FADE].rows.scenario",
        "note": "能源前提未与在场证据对账: 证据索引在列的 BRENT_F@2026-11-23=88.19 未被引用;快照直算近一月 116.72→88.19=−24.44%、三个月(2026-08-19→2026-11-23)91.62→88.19=−3.74%、12 个月 +38.86%——三个月窗内油价微降而两地通胀走高,对「能源持续传导」是反向事实、对「能源基数」消退假设是同向事实。建议在竞争解释或披露块注明。",
        "original": "【假设】若美欧通胀抬升主要源于能源与进口成本的持续传导(弱欧元放大输入压力),则 headline 强于 core 的结构应延续,且同比读数在数月内维持高位。",
        "fix": "",
    },
    {
        "severity": "MINOR",
        "where": "agent_judgment.json → l4.scenarios[id=S1-INFL-STICKY 与 S2-INFL-FADE].rows.scenario「至 2027-01」",
        "note": "「至 2027-01」的发布月/观测月口径不明: 2027-01 观测月的规则发布日为 2027-02-16,晚于两情景期限 2027-02-15,故只能指发布月(2026-11/2026-12 观测月)。建议写成「至 2027-01 发布(2026-12 观测月)」。",
        "original": "至 2027-01,EA_HICP_YOY 同比维持 3.5% 以上",
        "fix": "",
    },
    {
        "severity": "NIT",
        "where": "agent_judgment.json → l3.mechanism_chains[id=M1-JP-RATE-PATH].links[step=2].text 与 missing_link_note",
        "note": "「本引擎无日本融资成本/套息持仓序列」略过宽: JP_POLICY_RATE 本身即无担保隔夜拆借利率月均(一种隔夜融资成本),JGB 收益率在册未采;建议写「无日本套息持仓与中长端融资成本(国债收益率)序列」。",
        "original": "本引擎无日本融资成本/套息持仓序列,此环为【假设】",
        "fix": "",
    },
    {
        "severity": "NIT",
        "where": "agent_judgment.json → reader_map.headline_conclusion;MAP_REPORT.md 第 12 行",
        "note": "「日本央行官方政策目标利率约 1.25」缺 % 单位(冻结日历注记为「目标水平约1.25%」;走位面 JP 行带 %)。",
        "original": "日本央行官方政策目标利率约 1.25(2026-09-18 决议、2026-09-24 生效",
        "fix": "",
    },
    {
        "severity": "NIT",
        "where": "agent_judgment.json → reader_map.transmission[chain_id=CH-INFL-RATES-RISKOFF].links[2].observed_fact",
        "note": "环 3 窗口端点不一致(TIPS_10Y 止于 2026-11-19,SPX 等取 2026-11-23,NIKKEI225 止于 2026-11-20);文中已披露,共同窗(2026-10-23→2026-11-19)SPX −5.87% 方向不变。",
        "original": "近一月(2026-10-23→2026-11-20/23)SPX 下跌 5.51%",
        "fix": "",
    },
    {
        "severity": "NIT",
        "where": "agent_judgment.json → reader_map.transmission[chain_id=CH-INFL-RATES-RISKOFF].links[1].distinguishing_metric",
        "note": "环 2 把 TIPS_10Y 列为区分指标,同时自陈两解释在其上预言不分立;属诚实披露,更准确的说法是「本环无可区分指标」。",
        "original": "两解释在区分指标 TIPS_10Y 上的预期方向不分立",
        "fix": "",
    },
    {
        "severity": "NIT",
        "where": "agent_judgment.json → l4.scenarios[id=S1-INFL-STICKY].rows.scenario",
        "note": "「两地政策面维持紧缩偏向(日本月均中枢不低于当前台阶)」地区指代混用(「两地」指美欧,括注却是日本);美欧政策面不在本问证据面,只能作假设。",
        "original": "两地政策面维持紧缩偏向(日本月均中枢不低于当前台阶)",
        "fix": "",
    },
    {
        "severity": "NIT",
        "where": "agent_judgment.json → quality_gate_notes[5]",
        "note": "「已登记为待裁定残留,本轮未改引擎」属程序性声明,只读面无法核验(非错误,仅记录)。",
        "original": "引擎缺口披露(已登记为待裁定残留，本轮未改引擎)",
        "fix": "",
    },
    {
        "severity": "NIT",
        "where": "MAP_REPORT.md 第 8 行(引擎模板文字,非判断文字)",
        "note": "「经独立语义审查」写于裁决缺席状态的渲染(同文件第 217 行为「独立席位待裁」);属引擎模板,规程第 0 节已说明,仅记录。",
        "original": "判断文字=Agent 席 reader_map 原文(attribution=ai_inferred,经独立语义审查)",
        "fix": "",
    },
    {
        "severity": "NIT",
        "where": "agent_judgment.json → l3.contradictions[id=C2-GROWTH-STABLE].statement",
        "note": "「增长面大体平稳」只基于硬数据;快照库内软数据 UMCSENT 55.2(2026-07)→48.0(2026-10)方向相反,但不在本问计划指标面与证据索引;可把「增长面」限定为「硬数据增长面」。",
        "original": "两地增长面大体平稳、并非本期主导变化",
        "fix": "",
    },
    {
        "severity": "NIT",
        "where": "agent_judgment.json → quality_gate_notes[4]③;reader_map.turnings[2].follow_or_diverge",
        "note": "「跨国跟进/背离在政策维度依本问证据不可判」限定语准确;快照库内(不在计划指标面与证据索引)另有美联储目标区间上限 3.75→4.00(2026-09-17)、欧央行存款便利利率 2.25→2.50(2026-09-16),与日本央行 2026-09-18 决议同月收紧;可选择性注明「快照库内有、本问未纳入」。",
        "original": "跨国政策跟进/背离在政策维度依本问证据不可判",
        "fix": "",
    },
    {
        "severity": "NIT",
        "where": "agent_judgment.json → l3.contradictions[id=C3-JP-POLICY].statement",
        "note": "关键数字写成中文数字(约一点二五/六十天/六十六天/正六十七个基点/正七十五个基点),判断档已自陈其不在契约数字绑定之列;席位人工复算五个数均正确(1.25/60/66/+67/+75);建议用阿拉伯数字并带单位。",
        "original": "日本央行政策目标利率约一点二五",
        "fix": "",
    },
]

counter = [
    "反方攻击 1(C1-INFL-SYNC): 「同步走高」的美国端只到 9 月且 3.72 低于 2026-05 高点 4.17,能否称走高→成立: 3 个月前锚 2026-07=3.3039,最近有效 2026-09=3.7173,方向为升;2026-10 缺 2025-10 基期已在句内披露,未以相邻月替代(若替代会得 3.82%)",
    "反方攻击 2(C1-INFL-SYNC): 「水平高于美国」差距仅约 0.08 个百分点,舍入内是否翻转→不翻转: EA 3.8 为一位小数,真值不小于 3.75,大于 3.7173",
    "反方攻击 3(C1-INFL-SYNC): 「更早月份位次有交叉」是否夸大→字面属实但缺时间范围(全史 106 个可比月中仅 2022-07 至 2023-09 与 2026-09 共 16 个月欧元区高于美国,其前 34 个可比月均低于美国)→记 MINOR",
    "反方攻击 4(传导链环 1): 「尚不能区分」是否偏保守→三窗 BEI_10Y −14/−19/−11bp 合竞争解释而欧元区读数未回落,早段 2.25→2.50 端点为窗内最小→最大(月末对月末仅 +13bp)未标注→裁定不变,记 MINOR",
    "反方攻击 1(C2-GROWTH-STABLE): 工业同比 1.25→2.15、失业率低位,增长是否已重新加速→指数水平仅 +0.22%、2026-10 环比 −0.43%、基数 −0.66%,GDP 同比 2.19→2.07;判断档已把「重新加速」列为竞争【假设】→陈述成立",
    "反方攻击 2(C2-GROWTH-STABLE): 欧元区 GDP 同比 +0.09 是否构成上行→幅度微小,判断档写「仅微幅变动」→相称;快照库内软数据 UMCSENT 55.2→48.0 不在本问证据面,记 NIT",
    "反方攻击 1(C3-JP-POLICY): 「距上次调整 60/66 天」可否读成自 2026-10-30 维持会议起算(24 天)→句内明确决议日/生效日两种起算,与日历注记「按生效日计算」一致,维持会议另行披露→成立",
    "反方攻击 2(C3-JP-POLICY): 月均 1.227% 低于目标 1.25%,「相互印证」是否成立→1.227 为 10 月整月均值(目标 2026-09-24 生效),判断档明确该序列非政策目标宣布值→成立",
    "反方攻击 1(M1-JP-RATE-PATH): 若加息传导成立 USDJPY 应走低→实际近一月 156.494→159.347(+1.82%)、三个月 −0.13%、12 个月窗内约 71% 分位;环 3 已如实写「USDJPY 仍处高位…传导方向证据不单一」→未超出证据;「利差仍高」措辞记 MINOR",
    "反方攻击 2(M1-JP-RATE-PATH): 「股指已明显回落」是否被单一归因于加息→环 3 标混合态并注明多因子驱动、区分指标=USDJPY→相称",
    "反方攻击(CH-INFL-RATES-RISKOFF 环 3): TIPS_10Y 止于 11-19 而 SPX 取 11-23 的窗口错配是否改变方向→共同窗 2026-10-23→2026-11-19 SPX −5.87%,方向不变;错配已披露→「支持主解释」成立",
    "反方攻击(CH-INFL-RATES-RISKOFF 链级): 环 1、2 判「尚不能区分」而环 3 判「支持主解释」是否自相矛盾→不矛盾: 环 3 两侧预期在区分指标上分立且有在场观测,环 1、2 分立性弱或不可分;披露块「支持×1/尚不能区分×2」与逐环一致",
    "反方攻击(CH-INFL-RATES-RISKOFF 环 3 流动性因素): 「支持主解释」是否忽略流动性/仓位冲击→文中已写「VIX 的涨幅幅度提示流动性/仓位因素可能叠加，单月窗不能完全区分」→未超出证据",
    "反方攻击 1(情景 S1/S2 触发条件): 触发条件是否已触发、前提是否与截止日读数相容、两情景是否孤证→均未触发(S1: EA_HICP_YOY 4.0<4.2、CORE_PCE 3.12<3.2、TIPS_10Y 2.88<3.0;S2: EA_HICP_YOY 3.8→4.0 未回落、BEI_10Y 2.15>2.0),S1 前提与截止日读数相容,S2 属待验证的反例情景,两者方向互补(延续上行 vs 回落,资产方向相反)→通过",
    "反方攻击 2(情景 S1/S2 证伪条件): 证伪条件是否可观测、期限是否与截止日读数相容→S2 可触发(2026-12-16 / 2027-01-16 两次发布均在期限 2027-02-15 内);S1 按字面不可触发→MAJOR-1",
]

notes = (
    "裁决 REVISE: 独立抽核 190 点(规程第 3 节①–⑭ 共 186 点,六查在场对照 4 点),偏离 1 点。"
    "全部点值锚(9 格 18 锚)、同比基期(均为去年同月/同季,2026-10 美国 CPI 与核心 CPI 缺基期如实标不可得)、"
    "日本央行官方记录(目标 1.25/决议 2026-09-18/生效 2026-09-24/维持 2026-10-30)与距上次调整 60/66 天、"
    "三利率分解三窗恒等(残差 0)、资产月窗、转折候选池(7/7)、Gate A 与两项 STALE 披露,均与冻结快照/冻结日历/引擎面逐位一致;"
    "无以相邻口径冒充、无事后信息冒充当时可知。"
    "唯一偏离=MAJOR-1: S1-INFL-STICKY 证伪阈值句「若 2027-01 前发布的 EA_HICP_YOY 同比连续两个月低于 3.0%,通胀粘性假设被证伪」按字面不可触发——"
    "截止日后 2027-01 前只剩 2026-11 观测月一次发布(规则发布日 2026-12-16),能与它相邻的 2026-10 读数 4.0 已于 2026-11-16 发布,"
    "「连续两个月低于 3.0%」在 2027-01 前不可能成立;该句与本情景触发条件(2026-12 或 2027-01 发布)及 S2 证伪句(2026-12 与 2027-01 两月发布)的发布月口径不一致,"
    "且与披露块「两情景各给出可观测触发条件与失效阈值」不符;读者报告 MAP_REPORT.md 第 146 行逐字渲染该句。"
    "必修改句: 「" + S1_FIX + "」。"
    "另列 MINOR 5 条(位次「有交叉」缺时间范围;传导环 1 早段端点为窗内最小→最大未标注;机制链环 3「利差仍高」以事实位措辞出现而无利差序列;"
    "能源前提未与在场的原油期货读数对账;情景「至 2027-01」发布月/观测月口径)与 NIT 10 条,均不改变结论。"
    "反方攻击: C1×4、C2×2、C3×2、M1×2、传导链×3、情景×2,除上述 MAJOR 外均未推翻陈述。"
)

verdict = {
    "seat": "semantic-audit-seat",
    "reviewer": "independent-zero-context-seat-r32-b-round1",
    "verdict": "REVISE",
    "overall": "REVISE",
    "notes": notes,
    "items": items,
    "must_fix": [
        "MAJOR-1: " + S1_ORIG + " → " + S1_FIX
        + "(依据: EA_HICP_YOY 规则发布日=月末+16 天——2026-11 观测月 2026-12-16、2026-12 观测月 2027-01-16、2027-01 观测月 2027-02-16;"
        + "2026-10 观测月读数 4.0 已于 2026-11-16 发布;改后两个观测月在截止日 2026-11-23 均未发布,条件可观测、可触发,期限 2027-02-15 不变)"
    ],
    "counterexamples_sought": counter,
    "recompute_points": tab["recompute_points"],
    "recompute_mismatches": tab["recompute_mismatches"],
    "mismatch_details": [
        {
            "id": j5["id"],
            "category": j5["cat"],
            "where": "agent_judgment.json → l4.scenarios[id=S1-INFL-STICKY].rows.falsification.threshold;MAP_REPORT.md 第 146 行;FULL_REPORT.md 第 81 行;report.md 第 90 行",
            "computed": j5["computed"],
            "reported": j5["reported"],
            "detail": j5["note"],
        }
    ],
    "audited_at": "2026-11-24",
}

# schema self-check
need = ["seat", "reviewer", "verdict", "overall", "notes", "items", "must_fix", "counterexamples_sought", "recompute_points", "recompute_mismatches", "mismatch_details", "audited_at"]
assert list(verdict.keys()) == need
assert verdict["verdict"] in ("UPHELD", "REVISE") and verdict["overall"] == verdict["verdict"]
sev = {"MAJOR": 0, "MINOR": 0, "NIT": 0}
for it in items:
    assert set(it.keys()) == {"severity", "where", "note", "original", "fix"}
    assert it["severity"] in sev
    sev[it["severity"]] += 1
    if it["severity"] == "MAJOR":
        assert it["original"] and it["fix"]
assert verdict["recompute_points"] == len(pts) == 190 and verdict["recompute_mismatches"] == 1
assert sev == {"MAJOR": 1, "MINOR": 5, "NIT": 10}, sev
json.dump(verdict, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("written", out_path, "| items:", sev, "| counter:", len(counter), "| points/mismatch:", verdict["recompute_points"], verdict["recompute_mismatches"])
