#!/usr/bin/env python3
"""Build PROSE-round1.md and VERDICT-round1.json from the recompute table + seat findings.

usage: python3 -I build_outputs.py <recompute_table.json> <recompute_table.md> <out_dir>
All findings text below was composed by the seat from the read-only faces only.
"""
import json
import os
import sys

tbl = json.load(open(sys.argv[1], encoding="utf-8"))
md_full = open(sys.argv[2], encoding="utf-8").read()
outdir = sys.argv[3]

RUN = "20261123T124305Z"
N_PTS, N_OK, N_MM = tbl["n_points"], tbl["n_match"], tbl["n_mismatch"]
by = tbl["by_category"]
mm = {m["id"]: m for m in tbl["mismatches"]}

# --------------------------------------------------------------------------------------------
# findings
# --------------------------------------------------------------------------------------------
MAJOR = [
    {
        "severity": "MAJOR",
        "where": "MAP_REPORT.md L123(政策一年窗路径·欧央行存款便利利率)与 L126(主要再融资利率);同源: 引擎政策路径渲染段 L120-L133(自述 net_bp=窗首尾观测差)",
        "note": "『净变动 +25bp』按『窗内首个观测→窗末』(2026-06-17 的 2.25 → 2026-09-16 的 2.5)起算,漏计窗启时已在值的水平: series_store.ECB_DFR 自 2025-06-11 起为 2.0、ECB_MRO 为 2.15,窗 2025-11-23..2026-11-23 的真实净变动为 +50bp。同句列出的两个变动点各 +25bp(合计+50),首页 L11/L80/L195 亦写『ECB_DFR 2.0→2.5』——同一段内自相矛盾,读者得到的 12 个月政策净变动比真实值少一半。复算点 P04.net / P05.net。",
        "original": "变动点 2026-06-17: 2.0→2.25(+25bp);2026-09-16: 2.25→2.5(+25bp),净变动 **+25bp**(2.25→2.5) 〔L126: 变动点 2026-06-17: 2.15→2.4(+25bp);2026-09-16: 2.4→2.65(+25bp),净变动 **+25bp**(2.4→2.65)〕",
        "fix": "变动点 2026-06-17: 2.0→2.25(+25bp);2026-09-16: 2.25→2.5(+25bp),净变动 **+50bp**(2.0→2.5;窗启时在值为 2025-06-11 生效的 2.0) 〔L126: 净变动 **+50bp**(2.15→2.65)〕;并把括注 net_bp 口径改为『窗启时在值→窗末观测』。",
    },
    {
        "severity": "MAJOR",
        "where": "MAP_REPORT.md L80(首页速览·证据最充分的传导 ①)与 L191(传导机制 ①);FULL_REPORT.md L79(机制链 M1 环1);agent_judgment.json l3.mechanism_chains[M1].links[0].text(E1 事实环)与 reader_map.transmission[TR1].links[0].observed_fact",
        "note": "『此后美国CORE_PCE同比至2026-09续升至3.12』与证据相左: series_store.CORE_PCE 同比 2026-05=3.1617 → 2026-06=3.0412 → 2026-07=2.9953 → 2026-08=3.0344 → 2026-09=3.1212,9 月值低于 5 月高点(先回落后部分回升);美国 CPI 同比同为 4.1666@2026-05 → 3.3039@2026-07 → 3.3530@2026-08 → 3.7173@2026-09。『续升』=方向错,且该句位于标为【事实/E1】的冲击环。复算点 X1.corepce.rise。",
        "original": "此后美国CORE_PCE同比至2026-09续升至3.12、欧元区HICP至2026-10续升至4.0、中国PPI至2026-10续升至5.7(三地同窗共振,月频分辨率下先后未定)。",
        "fix": "此后美国 CORE_PCE 同比自 2026-05 高点 3.16 回落后部分回升(2026-07 3.00 → 2026-09 3.12,未越过 5 月高点)、欧元区HICP至2026-10续升至4.0、中国PPI至2026-10续升至5.7(三地同窗共振,月频分辨率下先后未定)。",
    },
    {
        "severity": "MAJOR",
        "where": "MAP_REPORT.md L215(主解释 vs 竞争解释对质表·BEI_10Y 政策行);agent_judgment.json reader_map.transmission[TR1].links[1].face_off_verdict=『支持竞争解释』",
        "note": "判断『支持竞争解释』仅凭观测格所列近 30 日回落(2.34→2.15)。主解释预期『BEI_10Y 在政策收紧前处上行段且高位』在证据面成立: series_store.BEI_10Y 2026-02-27 2.25 → 2026-05-04 2.50(收紧前上行段),首次加息决议前日 2026-06-10 2.34;收紧后回落(区间 2.15–2.40)亦与『通胀动机收紧、预期被锚定』相容,不专属于竞争解释。属以单侧证据裁,与报告自定口径 L219『不以单侧证据裁』相左。复算点 X2.bei.row(辅证 X2.bei.pre / X2.bei.post)。",
        "original": "| BEI_10Y | 通胀动机主导→BEI_10Y 在政策收紧前处上行段且高位(市场与央行同向定价通胀) | 非通胀动机主导→BEI_10Y 与政策节奏脱钩(政策续紧而 BEI_10Y 不升) | (引擎当前面: 2026-11-20=2.15,近30日2.34→2.15,下降19bp) | 支持竞争解释 |",
        "fix": "| BEI_10Y | 通胀动机主导→BEI_10Y 在政策收紧前处上行段且高位(市场与央行同向定价通胀) | 非通胀动机主导→BEI_10Y 与政策节奏脱钩(政策续紧而 BEI_10Y 不升) | (收紧前 2026-02-27→2026-05-04 2.25→2.50 上行段,合主解释;首次加息决议前日 2026-06-10 2.34,收紧后区间 2.15–2.40,近30日 2.34→2.15,合竞争解释——两侧均有相容观测) | 尚不能区分 |",
    },
]

MINOR = [
    {
        "severity": "MINOR",
        "where": "MAP_REPORT.md L129(政策一年窗路径·JP_POLICY_RATE)、L186(日本走位)、L205(传导链 ①)、L234(转折表第1行)",
        "note": "『净+67个基点(0.557→1.227)』为『自2025-12月均』起算的首末月均差;窗内(2025-11-23 起)同句列出的变动点合计 +75bp(含 2025-12-01 0.478→0.557 的 +8bp),窗启时在值 0.478@2025-11-01。四处引用均未写明起算点,与同句变动点之和不符。复算点 P06.net / W.JP.RATE.net。",
        "original": "变动点 2025-12-01: 0.478→0.557(+8bp);…;2026-10-01: 1.043→1.227(+18bp),净变动 **+67bp**(0.557→1.227)",
        "fix": "净变动 **+75bp**(0.478→1.227;其中自 2025-12 月均 0.557 起 +67bp)",
    },
    {
        "severity": "MINOR",
        "where": "MAP_REPORT.md L234(转折表第1行·谁先变);agent_judgment.json reader_map.turnings[2].first_mover",
        "note": "『日本下行起点(2025-11)』=窗内末段连降首月(series_store.JP_CPI_YOY 2025-06 3.27 → 2025-08 2.72 → 2025-09 2.91 → 2025-10 2.99 → 2025-11 2.90 → 2025-12 2.13),属窗口边缘效应;序列自 2025-01(4.03)已处下行。结论(日本先变、方向向下)不变且更强,但起点日期表述不准。复算点 TN.jp.origin。",
        "original": "日本下行起点(2025-11)早于美欧中上行共振起点(2026-02),起点先后可判(日本先变、方向向下)",
        "fix": "日本全国CPI同比自2025年起已处下行、12个月窗内自2025-11(2.90)再度回落,早于美欧中上行共振起点(2026-02),起点先后可判(日本先变、方向向下)",
    },
    {
        "severity": "MINOR",
        "where": "MAP_REPORT.md L214(对质表 BRENT_F 行)与 L194(区分指标当前面)",
        "note": "预期窗口=2026-02至2026-05,观测格却只列近 30 日(116.72→88.83,-23.89%);同窗月频路径 72.48(02月末)→118.35(03月末)→92.05(05月末)未入观测格。判断『尚不能区分』与证据不冲突(同窗 CORE_CPI 同比 2.47→2.82 亦走高,两解释预期在该窗并未分立),但观测格窗口≠预期窗口。复算点 X1.brent.row(命中,附注)。",
        "original": "| BRENT_F | 供给冲击主导→BRENT_F 在2026-02至2026-05同窗显著上行 | 需求/基数主导→BRENT_F 同窗大体持平而 CORE_CPI 上行 | (引擎当前面: 2026-11-23=88.83,近30日116.72→88.83,-27.89 指数点(-23.89%)) | 尚不能区分 |",
        "fix": "观测格改为: 同窗月频 2026-02 月末 72.48→2026-03 月末 118.35→2026-05 月末 92.05(先冲高后回落),同期 CORE_CPI 同比 2.47→2.82 亦走高;近30日 116.72→88.83",
    },
    {
        "severity": "MINOR",
        "where": "MAP_REPORT.md L217(对质表 USDJPY 行)与 L208(区分指标当前面);agent_judgment.json reader_map.transmission[TR2].links[0]",
        "note": "主解释预期『风险资产收缩窗口与日元走强(USDJPY 走低)同现』,而同窗观测 USDJPY +1.57%(156.494→158.956)伴随 SPX -9.36%——主解释预期方向与观测相反,观测格未披露;按 M2 link2 自身证伪口径(风险资产收缩而 USDJPY 未走低→套息平仓渠道分量下调),本窗已出现一次反向观测。『尚不能区分』(竞争解释需逐日共动面)可辩护,但披露不全。复算点 X4.usdjpy.row(命中,附注)。",
        "original": "| USDJPY | 日本正常化溢出主导→风险资产收缩窗口与日元走强(USDJPY 走低)同现 | 美国国内定价主导→USDJPY 走势与风险资产收缩在时间上解耦 | (引擎当前面: 2026-11-23=158.956,近30日156.494→158.956,+2.46199 指数点(+1.57%)) | 尚不能区分 |",
        "fix": "观测格补『同窗 SPX -9.36% 而 USDJPY +1.57%(未同向)——主解释预期本窗未获支持』,判断写『尚不能区分(主解释预期本窗未获支持,竞争解释待逐日共动面)』",
    },
    {
        "severity": "MINOR",
        "where": "MAP_REPORT.md L11(一句总判断)、L180(中国走位)、L195(传导机制 ②)、L234(转折表第1行)",
        "note": "『中国按兵不动/政策利率全年按兵不动』对 2026-11-02 换锚后的政策利率锚不成立/不可证: series_store.CN_OMO_7D 末值 1.4@2026-10-30(此后无观测),CN_POLICY_OVERNIGHT 自 2026-11-02 起 1.25(metric_registry 注: 换锚后的政策利率锚)——新锚水平低于原操作目标 15bp,且换锚后 7 天工具序列无观测。同句已披露换锚,但结论句未限定口径。复算点 W.CN.onhold / PCN.anchor.level。",
        "original": "最新 1.25@2026-11-23——政策利率全年按兵不动,与美欧日的收紧方向背离。",
        "fix": "最新 1.25@2026-11-23——7天逆回购利率与 LPR 窗内无变动;2026-11-02 起政策利率锚切换为隔夜逆回购利率(1.25),换锚后原工具无观测——未跟进加息,与美欧日的收紧方向背离",
    },
    {
        "severity": "MINOR",
        "where": "MAP_REPORT.md 全文(读者面无数据门披露行);对照 report.md L5、L8-L12 与 report.json steps[*].envelope.gate_a",
        "note": "report.md 载『数据门(gate_a): 61/61 信封步非 OK(DEGRADED)』与『任务目标缺口 8 项』;report.json steps[*].envelope.gate_a.status 计数={'None': 6, 'DEGRADED': 61};snapshot.gate_a.status=DEGRADED。MAP_REPORT.md 无对应披露行。另: gate_a.noncore_missing 所列 CN_OMO_7D / CN_POLICY_OVERNIGHT / EA_REAL_GDP_YOY / JP_CPI_TOKYO_YOY / JP_REAL_GDP_YOY 在 series_store 在场且被本报告引用(门按事实层判缺席)——读者面无从知晓该降级。复算点 HA.gate.steps(偏离)、HA.gate.list、MR.gap.note。",
        "original": "",
        "fix": "在 MAP『逐组覆盖』节增一行: 数据门 gate_a=DEGRADED(信封步 61/67 降级,核心缺失 0;非核心缺失 7 项,其中 5 项序列层在场、按序列值引用)——降级不阻断,判断层须知",
    },
    {
        "severity": "MINOR",
        "where": "MAP_REPORT.md L80、L167/L170/L171(关键资产月度变化表 DAX/DXY/GOLD_F 行)、L199",
        "note": "DAX 25039.1、DXY 103.903、GOLD_F 3614.1 均为 2026-11-23 当日值(snapshot.research_as_of=2026-11-23T20:41:34+08:00=12:41:34 UTC);报告自身对同为 11-23 观测的 VIX/BRENT_F/USDJPY 标注『当日实时快照(非收盘价)』,而此三者全部引用处不带——口径标注不一致,窗末变动幅度(DAX -0.57%、GOLD_F -9.83%、DXY +2.06%)可能随收盘值变化。复算点 CD.DAX.label / CD.DXY.label / CD.GOLD_F.label。",
        "original": "| DAX | 2026-10-23..2026-11-23 | 25181.7→25039.1 | -0.57%(-142.551) |",
        "fix": "资产表与 L80/L199 对 DAX/DXY/GOLD_F 的 11-23 值补注『当日实时快照(非收盘价)』",
    },
    {
        "severity": "MINOR",
        "where": "MAP_REPORT.md L226(SCN2 触发条件);agent_judgment.json l4.scenarios[SCN2].rows.trigger.condition",
        "note": "触发条件『美国CPI同比连续两个月回落』字面上在截止日前已成立两次(series_store.CPI 同比 2025-11→2026-01 2.6964→2.6533→2.3912;2026-05→2026-07 4.1666→3.4635→3.3039,均已发布)——作为『待验证』触发缺『自截止日起』锚;另 2026-10 同比因 2025-10 基期缺席暂不可算,『连续』须注明。复算点 SC.SCN2.trig.already。",
        "original": "或美国CPI同比连续两个月回落(期限 2027-02-28)",
        "fix": "或美国 CPI 同比自 2026-11 观测月起连续两个月回落(2026-10 同比待 2025-10 基期补齐)(期限 2027-02-28)",
    },
    {
        "severity": "MINOR",
        "where": "MAP_REPORT.md L104、L105(政策口径四分面·US 联邦基金目标区间上限 12个月前/3个月前两行·市场观测日列)",
        "note": "该列自称『市场观测=配对 DFF 同窗观测日』,却打印锚日 2025-11-23 / 2026-08-23(均为周日,series_store.DFF 无该日观测);同表 DFF 行打印 2025-11-22 / 2026-08-22——同一表内口径不一。复算点 PDt17.mkt / PDt18.mkt。",
        "original": "2025-11-23(市场观测=配对 DFF(有效联邦基金利率)同窗观测日…) 〔L105: 2026-08-23(市场观测=配对 DFF…)〕",
        "fix": "市场观测日列改打印配对 DFF 的实际观测日 2025-11-22 / 2026-08-22",
    },
    {
        "severity": "MINOR",
        "where": "MAP_REPORT.md L80、L199(TR1 ③ 已有观测);agent_judgment.json l3.mechanism_chains[M1].links[3](E2)",
        "note": "HY_OAS 3.52pp@2026-11-19 在引擎史(2023-11-21 起 n=786)居 0.92 分位、为 2025-05-09 以来最高(史内最高 4.61@2025-04-07),12 个月 3.17→3.52(+35bp);『仍温和(非信用事件级)』在引擎证据面上缺依据支撑(引擎无危机期历史),宜写明分位与历史窗;M1 link4 证伪观察『HY_OAS 快速走阔至危机水平』未量化。复算点 X3.hy.calm(偏离)、X3.hy.week。",
        "original": "HY_OAS 水平3.52pp@2026-11-19仍温和(近1周走阔0.29pp,非信用事件级)",
        "fix": "HY_OAS 水平3.52pp@2026-11-19(引擎三年史约92分位、2025-05以来最高,12个月+35bp;仍低于2025-04高点4.61,未达信用事件级);M1 link4 证伪阈值量化(如升至4.6以上)",
    },
    {
        "severity": "MINOR",
        "where": "MAP_REPORT.md L234(转折表第1行·谁先变);agent_judgment.json reader_map.turnings[0].first_mover",
        "note": "『2026-03起三地序列同月转向』与序列转折月不符: series_store.CPI 同比低点 2026-01(2.3912)、EA_HICP_YOY 低点 2026-01(1.7)、CN_PPI_YOY 低点 2025-11(-2.2)此后连升;2026-03 只是三地同时大幅跳升的月份。同窗共振结论不变,转折月表述不准。复算点 TN.sync.US / TN.sync.EA / TN.sync.CN。",
        "original": "三地同窗共振(2026-03起三地序列同月转向),月频分辨率下谁先变先后未定",
        "fix": "三地同窗共振(2026-02起同向上行、2026-03 同月大幅跳升;中国PPI自2025-11已连升),月频分辨率下谁先变先后未定",
    },
    {
        "severity": "MINOR",
        "where": "MAP_REPORT.md L196(TR1 ② 因果假设);agent_judgment.json l3.mechanism_chains[M1].links[1](E3 政策环)",
        "note": "时序表述『政策变动月(2026-06起)在通胀转折月(至2026-05)之后』成立,但未披露: 9 月三央行收紧时点,决议前可见的美国 CPI 同比已自 4-5 月高点回落(ECB 2026-09-10 前可见 2026-07 观测 3.3039;Fed 2026-09-16 / BOJ 2026-09-18 前可见 2026-08 观测 3.3530;可见最新 CORE_PCE 同比 2.9953@2026-07)——对『因通胀再加速而收紧』的动机归因是应披露的反向事实;6 月欧央行决议(06-11)时可见读数为 2026-04 观测 3.7792。复算点 X1.cpi.path(命中,附注)。",
        "original": "时序上政策变动月(2026-06起)在通胀转折月(至2026-05)之后=时序事实,但动机归因不可由数据验证,证据级E3",
        "fix": "时序上政策变动月(2026-06起)在通胀转折月(至2026-05)之后=时序事实;其中 2026-06 欧央行决议时可见 CPI 同比为 2026-04 观测 3.78,2026-09 三央行决议时可见读数已回落至 3.30–3.35——动机归因对 9 月一轮未获时序支持,仍为【假设】(E3)",
    },
    {
        "severity": "MINOR",
        "where": "agent_judgment.json l3.contradictions[C3].statement(MAP_REPORT.md 未渲染该句)",
        "note": "『引擎面无中国利率预期序列与信贷/内需序列』与快照不符: series_store.CN_NEW_LOANS(2008-01..2026-10,226 观测)与 facts 层 CN_TOTAL_TURNOVER、CN_LPR_5Y 在场;『三种解释不可区分』的前提陈述不实(A/B 两解释并非完全不可检验);evidence_refs 中 USDCNY@2026-11-23 被引用而未用于说明。复算点 HA.C3.credit。",
        "original": "引擎面无中国利率预期序列与信贷/内需序列,三种解释不可区分,标注【尚未验证】。",
        "fix": "引擎面无中国利率预期序列;信贷/内需侧仅有 CN_NEW_LOANS(月频至 2026-10)等少量事实,不足以在三种解释间裁决,标注【尚未验证】",
    },
    {
        "severity": "MINOR",
        "where": "MAP_REPORT.md L180(中国走位);agent_judgment.json l3.contradictions[C1].statement",
        "note": "走位只写『春季回升至荣枯线上方→至2026-07回落至49.2』,漏披露 series_store.CN_PMI_MFG 2026-09=50.1 再度高于荣枯线(2026-10 回落 49.3);高于 50 的月份为 2025-12、2026-03/04/06 与 2026-09(2026-05 持平 50.0)。结论(未构成趋势性转折)不变。复算点 W.CN.PMI.sep。",
        "original": "序列2026年春季一度回升至荣枯线上方、至2026-07观测回落至49.2(月度序列事实,幅度温和,未构成趋势性转折)",
        "fix": "序列2026年春季(2026-03/04/06)与2026-09一度站上荣枯线,2026-07(49.2)与2026-10(49.3)回落至线下(月度序列事实,幅度温和,未构成趋势性转折)",
    },
]

NIT = [
    {"severity": "NIT", "where": "MAP_REPORT.md L225、L226(情景表·角色列)", "note": "角色列均为『—』,基准/反例情景身份只在 scenario 行内文字(判断档无 role 字段)。复算点 SC.role。", "original": "", "fix": ""},
    {"severity": "NIT", "where": "MAP_REPORT.md L225(SCN1 证伪阈值括注)", "note": "『(2025-10基期补齐后)』口径不准: 仅 2026-10 同比依赖该基期,2026-11 同比基期 325.063@2025-11、2026-12 基期 326.031@2025-12 在场(series_store.CPI)。复算点 SC.SCN1.fals.base。", "original": "", "fix": ""},
    {"severity": "NIT", "where": "MAP_REPORT.md L183(欧元区走位)", "note": "『两段上行(2026-03至05与2026-08至10)』第一段起点写作 2026-03,序列自 2026-01 低点 1.7 起已连续上行至 2026-05 的 3.2。复算点 W.EA.HICP.legs。", "original": "", "fix": ""},
    {"severity": "NIT", "where": "MAP_REPORT.md L235(转折表第2行·中国制造业PMI)", "note": "『z口径 -2.3904→1.0101』数值为同比(%),与引擎面 unit『同比%』不符。复算点 T.cnpmi.unit。", "original": "", "fix": ""},
    {"severity": "NIT", "where": "MAP_REPORT.md L234 vs L186(日本央行目标水平)", "note": "L234 写『目标水平1.25%』,L186 写『目标水平1.25』——利率单位不应带 %。", "original": "", "fix": ""},
    {"severity": "NIT", "where": "MAP_REPORT.md L80、L199(HY_OAS 近1周)", "note": "『近1周走阔0.29pp』= facts.derived.week 的 ISO 周内口径(基准 2026-11-13 3.23,4 个交易日);严格 7 日口径为 +0.32pp(2026-11-12 3.20→3.52)。复算点 X3.hy.week。", "original": "", "fix": ""},
    {"severity": "NIT", "where": "MAP_REPORT.md L198、L202、L215(BEI_10Y 近30日)", "note": "『近30日2.34→2.15』起点为 10-23(距 11-20 为 28 天),行文口径标注不精确。复算点 X2.bei.30d。", "original": "", "fix": ""},
    {"severity": "NIT", "where": "MAP_REPORT.md L196(TR1 ② 因果假设)", "note": "『BEI_10Y 12个月回落11个基点、水平2.15@2026-11-20』: 12 个月变动按共同交易日 11-19 计(2.27→2.16),水平取 11-20 的 2.15——两个日期并写一句。", "original": "", "fix": ""},
    {"severity": "NIT", "where": "agent_judgment.json l3.contradictions[C1].evidence_refs、l3.mechanism_chains[M1].links[0].evidence_refs", "note": "事实 id 日期『CN_PPI_YOY@2026-10-31』『CN_CPI_YOY@2026-10-31』与 series_store 观测日 2026-10-01 不一致(取数一致)。", "original": "", "fix": ""},
    {"severity": "NIT", "where": "agent_judgment.json l3.contradictions[C2].evidence_refs;report.json agent_judgment.contract_verification(C2 注)", "note": "C2 的 evidence_refs 为 4 个当前水平(UST_10Y/GOLD_F/DXY/SPX 最新值),与历史路径主张无绑定;契约校验已注『UST_10Y@2026-11-19 未在文本展开』。", "original": "", "fix": ""},
    {"severity": "NIT", "where": "agent_judgment.json l3.contradictions[C2].statement", "note": "『2025-03、2023-10段风险资产与 GOLD_F 各窗普遍走强』: 2023-10 段 SHCOMP 三个月窗 -7.63%(月末口径),『普遍』可容一例。", "original": "", "fix": ""},
    {"severity": "NIT", "where": "MAP_REPORT.md L234(转折表第1行)", "note": "第 1 行把美国 CPI 上行与日本 CPI 下行并为一项(『同轮事件并项』),方向相反的两转折同格;L238 已披露并项口径。", "original": "", "fix": ""},
    {"severity": "NIT", "where": "agent_judgment.json l3.mechanism_chains[M1].links[2]", "note": "evidence_refs 为『BEI_10Y@2026-11-20』而文本写『BEI_10Y 2.16@2026-11-19(共同交易日)』——引用日与文本日差一天。", "original": "", "fix": ""},
    {"severity": "NIT", "where": "MAP_REPORT.md L403(2025-03 段事后综合)", "note": "『股指六个月、十二个月窗满一致』——引擎符号一致率面(steps[S6_analog].envelope.data.dispersion)仅含 SPX 一类股指,『股指』为泛称。复算点 H1.agree。", "original": "", "fix": ""},
    {"severity": "NIT", "where": "MAP_REPORT.md L11(VIX)、L194/L214(BRENT_F)、L208/L217(USDJPY)", "note": "『当日实时快照(非收盘价)』说明只出现在 L80/L199、L192、L205,其余引用处未带(标注不遍历)。复算点 CD.*.label 附注。", "original": "", "fix": ""},
    {"severity": "NIT", "where": "MAP_REPORT.md L577(2023-10 段·当时同步性)", "note": "欧元区 HICP 历史段首发口径=月末快报(当日可见),当前段发布依据=rule:month_end+16(终值)——两段首发口径不同,已括注但未说明对可见性的影响。复算点 H1.S08.val。", "original": "", "fix": ""},
]

COUNTER = [
    "反方攻击 C1-1: 『风险资产收缩』只是近1个月现象,12 个月窗 SPX/NIKKEI225/DAX 仍为 +4.04%/+16.27%/+8.10%(series_store 2025-11-19→最新: 6642.16→6910.39、48537.7→56436.65、23162.92→25039.1),C1 的『同向共动』是否夸大?→ 攻击未成立: C1 原文限定『近月收缩』,与证据一致。",
    "反方攻击 C1-2: C1 称『CPI 与 CORE_PCE 同比走高』——以最新可见值对 5 月高点,CORE_PCE 3.12@2026-09 < 3.16@2026-05、CPI 3.35@2026-08 < 4.17@2026-05,『走高』在近月是否不成立?→ 部分成立: 相对窗内低点/窗首(CPI 2.65@2025-12、CORE_PCE 2.72@2025-11)仍显著走高,结论保留;『续升』措辞偏差记为 MAJOR-2。",
    "反方攻击 C1-3: BEI_10Y 在窗内先升后降(2026-02-27 2.25→2026-05-04 2.50→2026-11-20 2.15),『BEI_10Y 回落』是否掩盖了收紧前的上行段而简化了解释A/B 的区分?→ 成立: 该上行段支持主解释,对质表单侧裁决(MAJOR-3);C1 主句『UST_10Y 与 TIPS_10Y 上行而 BEI_10Y 回落』与 12 个月口径(4.13→5.04、1.86→2.88、2.27→2.16)一致,保留。",
    "反方攻击 C2-1: 2023-10 段 SHCOMP 三个月窗 -7.63%(月末口径 2023-10-31→2024-01-31)与『2025-03、2023-10段风险资产…各窗普遍走强』相左?→ 『普遍』可容一例,『事后路径分歧、不可外推』的结论不受影响;记 NIT。",
    "反方攻击 C2-2: 三段事后路径分歧是否只是窗口口径差(引擎事后块起点=锚后首个观测 vs 月末口径)造成的假象?→ 攻击未成立: 复算两口径差最大 1.10pp(GOLD_F 2025-03 十二个月窗 引擎 47.73 vs 月末 48.83),三段间方向性分歧(2022-06 三个月窗股指全负 vs 另两段全正)远大于口径差;C2 所列事后数字逐格命中(180 点)。",
    "反方攻击 C3-1: 若引擎已有中国信贷序列(新增贷款),『三种解释不可区分』是否为自我设限?→ 部分成立: series_store.CN_NEW_LOANS 在场(2008-01..2026-10,226 观测),C3『引擎面无…信贷/内需序列』陈述不实(MINOR);但单一新增贷款序列是否足以区分输入型/内需型解释,证据面仍不足,『【尚未验证】』保留。",
    "反方攻击 M1-link1: 『2026-02→2026-05 同窗回升』之后三地是否真的『续升』?→ 对 CORE_PCE 不成立: 2026-05 3.1617→2026-07 2.9953→2026-09 3.1212,E1 事实环含方向错(MAJOR-2);EA_HICP_YOY 3.2→4.0@2026-10、CN_PPI_YOY 3.9→5.7@2026-10 两支成立。",
    "反方攻击 M1-link2: 9 月三央行收紧时,决议前可见的美国 CPI 同比已自高点回落(ECB 09-10 前可见 2026-07 观测 3.30;Fed 09-16/BOJ 09-18 前可见 2026-08 观测 3.35;CORE_PCE 可见最新 2.9953@2026-07),『因通胀再加速而收紧』的时序支持在 9 月一轮是否已减弱?→ 成立: 报告只写『政策变动月在通胀转折月之后』,未披露该反向事实(MINOR);E3 标注与证伪指标(CPI)仍成立且可观测。",
    "反方攻击 M1-link3: 12 个月利率分解是否逐位成立?→ 成立: UST_10Y 4.13→5.04(+91bp)=TIPS_10Y 1.86→2.88(+102bp)+BEI_10Y 2.27→2.16(-11bp),残差 0(2025-11-19→2026-11-19 共同交易日);仅引用日(11-20)与文本日(11-19)差一天(NIT)。",
    "反方攻击 M1-link4: HY_OAS 3.52pp 为引擎三年史 92 分位、2025-05-09 以来最高,『若为利率驱动 HY_OAS 应保持温和』的判据是否已不满足?→ 部分成立: 仍低于 2025-04-07 高点 4.61,『非信用事件级』可辩护,但『仍温和』缺分位/历史窗说明、证伪阈值『危机水平』未量化(MINOR)。",
    "反方攻击 M2/TR2-1: 按 M2 link2 自身证伪口径(风险资产收缩而 USDJPY 未走低→套息平仓渠道分量下调),近1个月 SPX -9.36% 伴随 USDJPY +1.57%(156.494→158.956)——该渠道是否已被证伪一次而报告仍写『尚不能区分』?→ 观测方向与主解释预期相反且未在观测格披露(MINOR);逐日共动面缺失,『尚不能区分』作为保守结论可保留。",
    "反方攻击 M2-link1: JP_POLICY_RATE『持续上行、窗内未回撤』是否成立?→ 成立: 月均 0.478@2025-11→1.227@2026-10 单调不回撤(2026-04/05 0.727 与 2026-08 0.977 为月均舍入微降,非政策回撤);净变动口径差(+67 vs +75)记 MINOR。",
    "反方攻击 TR1-BRENT: 供给冲击说的区分指标在预期窗(2026-02至05)内先冲高(2026-03 月末 118.35)后回落(2026-05 月末 92.05),而观测格只列近30日(-23.89%)——判断所用窗口与预期窗口不一致?→ 成立(MINOR);『尚不能区分』与同窗 CORE_CPI 亦走高(2.47→2.82)的事实一致,保留。",
    "反方攻击 历史同步性: 三段『当时同步性』标签是否与引擎地区×维度同步面一致?→ 一致: 2025-03 部分同步(中国分化、欧元区分化、日本同步)/2022-06 同步(三者同步)/2023-10 不同步(三者分化),36 行同步表逐格命中;当时可知(27 行)与事后实际(66 行)分列成立;无 REVISE 级问题。",
    "反方攻击 证伪可观测性: SCN1/SCN2 证伪阈值是否截止日前已触发、触发条件是否可观测?→ 证伪均未触发: CPI 同比最新 3.72(CORE_PCE 3.12)未低于 2.5/2.8,BEI_10Y 2.15 未跌破 1.8;SCN1 触发(2026-11/12 CPI≥3.5 或再加息)可观测且未提前成立;但 SCN2 触发『CPI同比连续两个月回落』字面在 2026-06/07 已成立(MINOR h)。",
]

SEV_OF_MM = {
    "P04.net": "MAJOR-1", "P05.net": "MAJOR-1", "P06.net": "MINOR-a",
    "PDt17.mkt": "MINOR-i", "PDt18.mkt": "MINOR-i", "X1.corepce.rise": "MAJOR-2",
    "X2.bei.row": "MAJOR-3", "X3.hy.calm": "MINOR-j", "TN.jp.origin": "MINOR-b",
    "TN.sync.US": "MINOR-k", "TN.sync.EA": "MINOR-k", "TN.sync.CN": "MINOR-k",
    "HA.gate.steps": "MINOR-f", "HA.C3.credit": "MINOR-m",
    "CD.DAX.label": "MINOR-g", "CD.DXY.label": "MINOR-g", "CD.GOLD_F.label": "MINOR-g",
    "SC.SCN2.trig.already": "MINOR-h", "W.CN.PMI.sep": "MINOR-n", "W.CN.onhold": "MINOR-e",
}
assert set(SEV_OF_MM) == set(mm), (set(SEV_OF_MM) ^ set(mm))

mismatch_details = []
for m in tbl["mismatches"]:
    mismatch_details.append({
        "id": m["id"], "category": m.get("category"), "source": m.get("source"), "computed": m.get("computed"),
        "reported": m.get("reported"), "note": m.get("note"), "severity": SEV_OF_MM[m["id"]],
    })

items = MAJOR + MINOR + NIT
must_fix = ["%s %s | 原句: %s → 改句: %s" % (k + 1, it["where"], it["original"], it["fix"]) for k, it in enumerate(MAJOR)]

notes = (
    "裁决=REVISE。零上下文独立席位对运行 20261123T124305Z(截止日 2026-11-23,代码印记 f722e3c0bf7cd10aee64a8f4a166a136180a28ea)"
    "做只读复算 %d 点: 命中 %d、偏离 %d(重复ID 0),覆盖规程 §3 十三类;逐点清单见 recompute_table.json/.md。"
    "偏离归类: MAJOR 3 / MINOR %d / NIT %d。"
    "MAJOR-1: MAP L123/L126 欧央行两口径『净变动 +25bp』按窗内首个观测起算,漏计窗启时在值(2025-06-11 起 2.0/2.15),"
    "与同句两个 +25bp 变动点及首页『ECB_DFR 2.0→2.5』自相矛盾,12个月净变动实为 +50bp。"
    "MAJOR-2: L80/L191 及 M1 link1(E1 事实环)『此后美国CORE_PCE同比至2026-09续升至3.12』与证据相左——"
    "series_store.CORE_PCE 同比 2026-05=3.1617→2026-07=2.9953→2026-09=3.1212,先回落后部分回升,未越过5月高点;"
    "CPI 同比同为 4.1666@05→3.3039@07→3.353@08→3.7173@09。"
    "MAJOR-3: L215 对质表 BEI_10Y 政策行判断『支持竞争解释』仅凭近30日回落,主解释预期『收紧前上行段』在证据面成立"
    "(2026-02-27 2.25→2026-05-04 2.50),收紧后回落亦与通胀动机说相容——单侧证据裁,与报告自定口径 L219 相左,应改『尚不能区分』并补全观测格。"
    "MINOR %d 条: JP_POLICY_RATE +67bp 漏同句 +8bp 变动点(合计+75);日本下行起点(2025-11)为窗口边缘效应;BRENT_F 行观测窗≠预期窗;"
    "USDJPY 行主解释预期同窗反向未披露;『中国按兵不动』对 2026-11-02 换锚后的政策利率锚不成立/不可证;MAP 读者面未披露 Gate A DEGRADED 与任务目标缺口;"
    "DAX/DXY/GOLD_F 当日实时值缺『非收盘价』说明;SCN2 触发『CPI同比连续两月回落』截止日前已成立,缺『自截止日起』锚;"
    "四分面 DFEDTARU 两行市场观测日打印锚日而非配对 DFF 观测日;HY_OAS 3.52 为引擎三年史 92 分位而称『仍温和』、M1 link4 证伪阈值未量化;"
    "『2026-03起三地同月转向』转折月不准;9月三央行收紧时可见 CPI 同比已自高点回落未披露(M1 link2);C3『引擎面无信贷/内需序列』与快照 CN_NEW_LOANS 在场不符;"
    "CN_PMI 2026-09=50.1 再度站上荣枯线漏披露。"
    "六查: 三条 L3 矛盾与两条机制链逐环做了相关性/支持度/竞争解释真竞争性/反面证据/超出证据/证伪可观测六查,每项至少一条反方攻击(见 counterexamples_sought);"
    "历史三段(2025-03/2022-06/2023-10)同步性叙述与引擎同步面一致(部分同步/同步/不同步),当时可知与事后实际分列成立,无 REVISE 级问题;"
    "地图四地×维度×三锚点 66 格与关键数字表 63 行逐格命中;情景互补、两情景证伪阈值均未触发、SCN1 触发可观测。"
) % (N_PTS, N_OK, N_MM, len(MINOR), len(NIT), len(MINOR))

verdict = {
    "seat": "semantic-audit-seat",
    "reviewer": "independent-zero-context-seat-r32-a-round1",
    "verdict": "REVISE",
    "overall": "REVISE",
    "notes": notes,
    "items": items,
    "must_fix": must_fix,
    "counterexamples_sought": COUNTER,
    "recompute_points": N_PTS,
    "recompute_mismatches": N_MM,
    "mismatch_details": mismatch_details,
    "audited_at": "2026-11-23",
}

vpath = os.path.join(outdir, "VERDICT-round1.json")
with open(vpath, "w", encoding="utf-8") as f:
    json.dump(verdict, f, ensure_ascii=False, indent=2)
    f.write("\n")

# --------------------------------------------------------------------------------------------
# PROSE
# --------------------------------------------------------------------------------------------
CAT_NOTE = {
    "①": ("锚点网格", "MAP 环境对照表 22 行 × 三锚点(值/观测日/发布日);可见性=发布日≤锚日的最新观测(日历条目优先,规则兜底)"),
    "②": ("锚点网格 + 地图子问句", "环境表值与 L1 事实层/序列交叉核对;同比括注逐格"),
    "②⑬": ("地图子问句", "四地区×维度×三锚点 66 格 + 子问句(转折/谁先变/传导/情景/历史/对质)各节在场"),
    "③": ("同比基期", "锚点同比点 + 转折窗同比;基期缺席处如实标注、未给同比"),
    "④": ("政策日期/目标/距离", "决议日/生效日/市场观测日/统计窗口终点四分列;日本央行目标取发布日历实录条目 RC-JP-BOJ-TARGET-2026-09(决议 2026-09-18/生效 2026-09-24/目标 1.25)与 RC-JP-BOJ-MAINT-2026-10"),
    "⑤": ("利率三件套 + 资产窗", "名义+91bp=实际+102bp+盈亏平衡-11bp(2025-11-19→2026-11-19);近1月资产窗逐行(起→末/幅度)"),
    "⑤⑩": ("资产窗 + 走位", "资产月度变化表窗口规则与走位引用交叉"),
    "⑥": ("转折与候选面", "转折表 3+1 行的前值→后值/窗口/谁先变;引擎 turning 候选面 9 行逐格"),
    "⑦": ("传导链证据级与数字", "TR1/TR2 四环【事实/E1】【E3】【E2】标注、竞争解释、区分指标当前面、对质表四行"),
    "⑧": ("历史类比", "三段(2025-03/2022-06/2023-10): 距离/分位/匹配窗/贡献份额/|gap|>1/当时可知 27 行/同步 36 行/事后 66 行/引擎事后 36 值/符号一致率/覆盖度"),
    "⑨": ("情景", "SCN1/SCN2 引用数字、互补性、触发可观测与截止日相容、证伪未触发、期限、敏感变量"),
    "⑩": ("走位与首页", "四地区走位数字、首页总判断与速览链逐数"),
    "⑪": ("诚实缺席", "JP_POLICY_TARGET/东京CPI 12个月前/隔夜利率锚日/CPI 与 CORE_CPI 2025-10 基期/JGB 序列/失业率 2025-10/OMO 滞后/Gate A"),
    "⑫": ("截止日当日值口径", "research_as_of 相容性;VIX/BRENT_F/USDJPY 带『当日实时快照』说明;DAX/DXY/GOLD_F 未带(偏离)"),
    "⑬": ("地图覆盖", "四地区×维度×三锚点 + 子问句各节在场;『尚不能区分/支持竞争解释』与观测格一致性;历史段事后措辞;缺口注记"),
}


def md_escape(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


L = []
L.append("# Round-1 独立语义审查纪要(工单 A·独立零上下文席位)\n")
L.append("- 席位: semantic-audit-seat / reviewer=independent-zero-context-seat-r32-a-round1;审查日 2026-11-23;轮次 Round-1。\n")
L.append("- 审查对象: 运行 `%s`(问题原文 question_verbatim.txt;研究截止日 2026-11-23;代码印记 f722e3c0bf7cd10aee64a8f4a166a136180a28ea;快照 research_snapshot_20261123,research_as_of=2026-11-23T20:41:34+08:00)。\n" % RUN)
L.append("- 只读面(规程 §1)与实际查阅: question_verbatim.txt、MAP_REPORT.md(读者面,主审对象)、report.md、agent_judgment.json、report.json(python 抽取: run / research_plan / layers.L1_事实层.rows / agent_judgment.contract_verification / steps[*].envelope)、views_digest.json(n=0)、root_overlay/config/release_calendar.json(18 条目)、root_overlay/config/metric_registry.json、root_overlay/data/daily/research_snapshot_20261123.json(series_store 92 序列 + facts 105 条 + gate_a/quality)。FULL_REPORT.md 未逐段复审,仅对三条 MAJOR 原句做定位检索(MAJOR-2 原句见于 FULL_REPORT.md L79;政策路径行与对质表不在其内);evidence_index.json 未开启。\n")
L.append("- 边界声明: 未读取规程 §2 任何禁读目录(research_archive/、树内 docs/、/tmp/r32-accept/out/、scripts/、replay/、install*、其他运行目录、~/investment-agent-product、AGENT_SEAT_ENVELOPE.json);未运行 ia_cli.py;未联网;未修改运行目录与安装树内任何文件;全部脚本与产出只写入 /tmp/r32-accept/review/A_round1/ 并以 python3 -I 运行。\n")
L.append("- 席位脚本与中间表(同目录): seatlib.py、rc_common.py、rc_paths.py、rc_a.py~rc_d.py、recompute.py(复算主程序)、recompute_table.json / recompute_table.md(逐点清单)、probe*.py 与 probe*_out.txt / quotes_out.txt / grep_*_out.txt(只读抽取)、extract_quotes.py、grep_phrases.py、build_outputs.py(本纪要与裁决档装配)、validate_verdict.py(裁决档校验)。\n")
L.append("- 复算结果: **复算点 %d / 命中 %d / 偏离 %d / 重复ID 0**(规程最低 60 点)。\n" % (N_PTS, N_OK, N_MM))
L.append("\n## 1. 复算清单\n")
L.append("逐点清单(出处键/席位直算值/报告值/一致与否/注)见文末附录 A(= recompute_table.md)与 recompute_table.json;按类汇总:\n")
L.append("| 类 | 覆盖面 | 点数 | 命中 | 偏离 |")
L.append("|---|---|---|---|---|")
for k in sorted(by, key=lambda x: (len(x), x)):
    nm = CAT_NOTE.get(k, (k, ""))
    L.append("| %s | %s——%s | %d | %d | %d |" % (k, nm[0], nm[1], by[k]["n"], by[k]["n"] - by[k]["mm"], by[k]["mm"]))
L.append("\n### 1.1 偏离逐条(出处键 / 直算值 / 报告值 / 判定)\n")
L.append("| 复算点 | 类 | 出处(文件+键) | 席位直算值 | 报告值 | 归入 |")
L.append("|---|---|---|---|---|---|")
for m in tbl["mismatches"]:
    L.append("| %s | %s | %s | %s | %s | %s |" % (
        md_escape(m["id"]), m.get("category"), md_escape(m.get("source")), md_escape(m.get("computed")),
        md_escape(m.get("reported")), SEV_OF_MM[m["id"]]))
L.append("\n### 1.2 命中要点(代表性,均逐格复算)\n")
L.append("- 锚点网格: 环境对照表 22 行 × 三锚点的值、观测日、发布日全部命中(如 CN_PMI_MFG 49.0@2025-10 / 49.2@2026-07 / 49.3@2026-10;发布日重建 rule:month_end-1),发布日≤锚日;2025 年美国政府停摆延误以发布日历条目为准(如 RC-2025SHUTDOWN-CPI-NOV、RC-2025SHUTDOWN-GDP-Q3)。\n")
L.append("- 关键数字表 63 行逐格值/观测日/发布日命中;同比括注与基期值命中(如 M01 基期值 50.1)。\n")
L.append("- 政策日期四分列: 欧央行决议 2026-06-11/生效 06-17、决议 09-10/生效 09-16;美联储决议 2026-09-16/生效 09-17;日本央行 RC-JP-BOJ-TARGET-2026-09(决议 2026-09-18、生效 2026-09-24、目标 1.25)与 RC-JP-BOJ-MAINT-2026-10(2026-10-30 维持),距离天数(60/66/24 天)命中。\n")
L.append("- 利率三件套(共同交易日 2025-11-19→2026-11-19): UST_10Y 4.13→5.04(+91bp)=TIPS_10Y 1.86→2.88(+102bp)+BEI_10Y 2.27→2.16(-11bp),残差 0;近1月 SPX 7623.68→6910.39(-9.36%)、SHCOMP -4.11%、DAX -0.57%、NIKKEI225 -9.98%、VIX 19.45→30.24(+55.48%)、DXY +2.06%、GOLD_F -9.83%、UST_10Y +0.8% 逐行命中。\n")
L.append("- 转折与候选面: CPI 2.434→4.1666(2026-02→05)、INDPRO 1.7543→0.7972(2025-11→2026-02)、JP_CPI_YOY 2.9→1.27、东京 1.6→2.69(2026-06→09)与引擎 turning 候选面 9 行逐格命中。\n")
L.append("- 传导链: 四环【事实/E1】【时序为事实,动机为假设/E3】【E2,缺环为假设】【E3,整环假设】证据级标注齐备;区分指标当前面数字(BRENT_F 116.72→88.83、BEI_10Y 2.34→2.15、USDJPY 156.494→158.956)命中;TR1 利率环对质行『尚不能区分』与观测一致。\n")
L.append("- 历史类比三段(2025-03 距离 0.7527 分位 0.0 / 2022-06 0.8099 分位 1.37 / 2023-10 1.0754 分位 28.77): 匹配窗、贡献份额(如 2025-03 波动维 46.0%+利率维 38.0%)、|gap|>1 集合、当时可知 27 行、同步表 36 行、事后 66 行(含事后窗起止与延误算术)、引擎事后 36 值、TOP-N 符号一致率、覆盖度 growth 0.17 / inflation 0.33 / credit 0.5、逐窗并列 81 行——180 点全部命中。\n")
L.append("- 情景: SCN1 引 2022-06 三个月窗 SPX -5.28%/GOLD_F -7.49%/DXY +7.10%、SCN2 引 2025-03 十二个月窗 GOLD_F +48.83%/DXY -4.08%/SPX +16.33%(月末口径)命中;两情景方向互补;证伪阈值(CPI<2.5 且 CORE_PCE<2.8;BEI_10Y<1.8)均未触发;SCN1 触发条件可观测且未提前成立;期限 2027-02-28。\n")
L.append("- 诚实缺席: JP_POLICY_TARGET(注册表缺席)、东京CPI 12个月前(首观测 2026-01)、隔夜利率锚日前无观测、CPI/CORE_CPI 2025-10 基期缺席、JGB 序列缺席(单点事实)、失业率 2025-10(停摆)缺席、CN_OMO_7D 末观测滞后 24 天——均如实标注。\n")
L.append("\n## 2. 六查逐项结论(L3 矛盾 C1–C3;机制链 M1 四环、M2 两环;对质表 TR1/TR2)\n")
L.append("六查维度: 相关性 / 支持度 / 竞争解释是否真竞争 / 反面证据 / 是否超出证据 / 证伪可观测。逐项结论:\n")
L.append("| 对象 | 相关性 | 支持度 | 竞争解释真竞争 | 反面证据 | 超出证据 | 证伪可观测 | 结论 |\n|---|---|---|---|---|---|---|---|")
L.append("| C1 主线综合 | 成立(11 个最新水平逐值命中) | 共动主张逐项命中;『CPI 与 CORE_PCE 同比走高』相对窗首成立、相对 5 月高点不成立(MAJOR-2 所在句) | A/B/C 三解释各有可区分预期(BEI 稳定 vs BEI 主导下行 vs USDJPY 耦合+HY_OAS 平稳),月窗与 12 月窗分别容纳不同解释 | BEI 窗内先升后降、CN_PMI 2026-09>50、HY_OAS 92 分位未在 C1 句内披露(MINOR j/n) | 未超出(明写『不足以裁决』) | 可观测(BEI_10Y/TIPS_10Y/HY_OAS/USDJPY 均在库) | REVISE(随 MAJOR-2) |")
L.append("| C2 历史相似段冲突 | 成立 | 2022-06 三个月窗股指全负、十二个月窗除 SHCOMP 外转正;另两段风险资产与 GOLD_F 各窗为正(DXY 六窗全负)——逐格命中 | A(政策/冲击环境【假设】)与 B(低维覆盖 0.17/0.33/0.5)真竞争 | 无实质反面证据;2023-10 SHCOMP 三个月窗 -7.63% 被『普遍』容纳(NIT) | 未超出(『不可外推』,纪律降级为描述性) | 事后路径为已发生事实,无需证伪 | 通过 |")
L.append("| C3 中国政策背离 | 成立(PPI 摆动 7.8pp 最大、LPR 3.0 持平、换锚 2026-11-02) | 命中 | A/B 真竞争,C(汇率/资本流动)自标不可检验 | 无 | 未超出(【尚未验证】) | 前提句『引擎面无…信贷/内需序列』与快照 CN_NEW_LOANS 在场不符(MINOR m) | 通过(MINOR) |")
L.append("| M1-link1 冲击环【E1】 | 成立 | 同窗回升三支命中;『此后 CORE_PCE 续升』方向错 | —(事实环) | CPI/CORE_PCE 自 5 月高点回落 | — | — | **REVISE(MAJOR-2)** |")
L.append("| M1-link2 政策环【E3】 | 成立 | 时序(2026-06 起)在转折窗(至 2026-05)之后成立;9 月一轮决议时可见读数已回落未披露 | 竞争解释(金融稳定/汇率/正常化)真竞争 | 9 月收紧时可见 CPI 同比 3.30–3.35(MINOR l) | 未超出(整环【假设】) | 证伪指标 CPI 可观测 | 通过(MINOR) |")
L.append("| M1-link3 利率环【E1】 | 成立 | +91=+102-11 残差 0 命中 | —(事实环) | 无 | — | — | 通过(引用日 NIT) |")
L.append("| M1-link4 资产环【E2】 | 成立 | 共动事实命中;缺环标为假设 | 竞争解释(增长担忧)真竞争 | HY_OAS 3.52 为三年史 92 分位(MINOR j) | 未超出 | 证伪观察『走阔至危机水平』未量化(MINOR j) | 通过(MINOR) |")
L.append("| M2-link1 日本环【E1】 | 成立 | 月均 0.478→1.227 单调上行命中;净变动口径差 +67 vs +75(MINOR a) | —(事实环) | 无 | — | — | 通过(MINOR) |")
L.append("| M2-link2 溢出环【E3】 | 成立 | 整环假设,无 JGB 序列如实标注 | 竞争解释(美国国内定价)真竞争 | 同窗 USDJPY +1.57% 伴随 SPX -9.36%(主解释预期反向,MINOR d) | 未超出 | 证伪指标 USDJPY 可观测 | 通过(MINOR) |")
L.append("| TR1 对质表 | — | BRENT_F 行观测窗≠预期窗(MINOR c);**BEI_10Y 政策行单侧裁(MAJOR-3)**;BEI_10Y 利率行『尚不能区分』一致 | 四行预期均两立 | BEI_10Y 收紧前上行段(2.25→2.50)支持主解释 | — | — | **REVISE(MAJOR-3)** |")
L.append("| TR2 对质表 | — | USDJPY 行主解释预期同窗反向未披露(MINOR d) | 预期两立 | 同上 | — | — | 通过(MINOR) |")
L.append("\n### 2.1 反方攻击记录(每条 L3/机制链至少一条;攻击 → 结果)\n")
for c in COUNTER:
    L.append("- %s\n" % c)
L.append("\n### 2.2 历史段同步性(规程 §4 专项)\n")
L.append("- 三段『- 当时同步性』叙述标签与引擎地区×维度同步面逐项一致: 2025-03『部分同步』=中国分化、欧元区分化、日本同步;2022-06『同步』=三者同步;2023-10『不同步』=三者分化(MAP L335/L453/L577);36 行同步表逐格命中。叙述称同步处引擎面均有同步证据,无『称同步而面=缺证』或叙述与面冲突的情形——无 REVISE 级问题。\n")
L.append("- 当时可知(known-then)27 行与事后实际(ex-post)66 行分列;事后段落均以『事后实际/当时不可知,亦非对本次的预测』措辞,候选相似期标注『事后以全窗口数据筛得』;事后窗起止、延误天数与政策事件集合(多列/漏列均为偏离的口径下)逐项命中。\n")
L.append("\n## 3. 问题清单\n")
L.append("### 3.1 MAJOR(必修 %d 条)\n" % len(MAJOR))
for k, it in enumerate(MAJOR):
    L.append("**MAJOR-%d** 位置: %s\n\n- 问题: %s\n- 原句: 『%s』\n- 改句: 『%s』\n" % (k + 1, it["where"], it["note"], it["original"], it["fix"]))
L.append("### 3.2 MINOR(%d 条)\n" % len(MINOR))
for k, it in enumerate(MINOR):
    L.append("**MINOR-%s** 位置: %s\n\n- 问题: %s\n- 改法: 『%s』\n" % (chr(ord("a") + k), it["where"], it["note"], it["fix"]))
L.append("### 3.3 NIT(%d 条)\n" % len(NIT))
for k, it in enumerate(NIT):
    L.append("%d. 位置: %s——%s\n" % (k + 1, it["where"], it["note"]))
L.append("\n## 4. 裁决\n")
L.append("**REVISE**——存在 3 条 MAJOR(数字错: 欧央行 12 个月净变动 +25bp 应为 +50bp;方向错: 『CORE_PCE 同比续升至 3.12』与证据相左;与证据相左/单侧证据裁: BEI_10Y 政策行『支持竞争解释』应为『尚不能区分』)。其余 %d 条 MINOR 为口径/披露改进(不改变结论),%d 条 NIT 为行文。改句均可由证据面数字支持(出处见各条)。\n" % (len(MINOR), len(NIT)))
L.append("\n---\n\n## 附录 A: 复算逐点表(= recompute_table.md)\n\n")
app = md_full
# demote headings in appendix to keep single H1
app = "\n".join(("#" + ln) if ln.startswith("#") else ln for ln in app.split("\n"))
L.append(app)
ppath = os.path.join(outdir, "PROSE-round1.md")
with open(ppath, "w", encoding="utf-8") as f:
    f.write("".join(x if (x.endswith("\n") or not x.startswith("|")) else x + "\n" for x in L))
print("written", vpath, ppath)
print("points=%d ok=%d mm=%d | MAJOR=%d MINOR=%d NIT=%d | counter=%d | items=%d" % (
    N_PTS, N_OK, N_MM, len(MAJOR), len(MINOR), len(NIT), len(COUNTER), len(items)))
