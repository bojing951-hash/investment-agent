#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Seat script: assemble VERDICT-round1.json and PROSE-round1.md from the hand-written audit findings
plus the machine-generated recompute table/summary (read-only inputs; outputs go to this seat directory only).
Usage: python3 -I build_outputs.py <recompute_table.md> <recompute_summary.json> <extra_ctx.txt> <out_dir>
"""
import json
import os
import re
import sys

SEAT = "semantic-audit-seat"
REVIEWER = "independent-zero-context-seat-r32-n30-round1"
RUN = ("20261123T193232Z_2026年11月_日本和欧元区最近六个月的通胀与政策环境有什么不同_哪些方面分化")
CODE = "0f3936dd7eb74c557a2350e400d58e10a09c5139"

ITEMS = [
    # ------------------------------------------------------------------ MINOR
    {
        "severity": "MINOR",
        "where": "agent_judgment.json l3.contradictions[2].statement(C3⑤);reader_map.headline_conclusion",
        "note": "「增长与核心通胀背景序列缺席(GDP 两序列在册但快照缺席)」把「事实行缺席」写成「序列缺席」: 冻结快照 gate_a.noncore_missing 含 EA_REAL_GDP_YOY/JP_REAL_GDP_YOY,detail=「来源文件在场且子源FRED_EA_GDP/FRED_JP_GDP取数成功而指标缺席(采集遗漏——采集器已取到而事实未生成)」,而 series_store 两序列均有至 2026-07-01 期读数(EA 1.28,n=123;JP 1.16,n=127)。与同为 noncore_missing 却取序列面值并披露的东京 CPI 处理不一致;按 Gate A「缺失数据不得进入研究结论」不取用本身合规,结论不变。",
        "original": "⑤增长与核心通胀背景缺席: EA_REAL_GDP_YOY、JP_REAL_GDP_YOY 在册但列于快照缺席名单,两地「政策环境」无法对照增长背景;注册表亦无两地核心通胀序列。",
        "fix": "⑤增长与核心通胀背景对照缺席: EA_REAL_GDP_YOY、JP_REAL_GDP_YOY 在册,但当日快照 Gate A 列于缺席名单(事实行缺席,注记=采集器已取到而事实未生成;序列面存有至 2026-07 期读数 EA 1.28%/JP 1.16%,按 Gate A 不取用),两地「政策环境」无法对照增长背景;注册表亦无两地核心通胀序列。",
    },
    {
        "severity": "MINOR",
        "where": "agent_judgment.json l3.contradictions[1].statement(C2 节奏对照)",
        "note": "「相隔两天」=欧央行生效日 2026-09-16 对日央行决议日 2026-09-18,两端口径不对称;同口径距离为生效日对生效日(09-16→09-24)8 天、决议日对决议日(回推 09-10→实录 09-18)8 天。「在前/在后」排序不受影响。",
        "original": "欧央行第二次变更 2026-09-16 生效在前、日央行 2026-09-18 决议即 2026-09-24 生效在后,相隔两天,日级日期可排",
        "fix": "欧央行第二次变更 2026-09-16 生效在前、日央行 2026-09-18 决议(2026-09-24 生效)在后,同口径相隔八天(生效日对生效日;决议日对决议日亦八天),日级日期可排",
    },
    {
        "severity": "MINOR",
        "where": "agent_judgment.json reader_map.transmission[0].links[2].verdict_note;l3.mechanism_chains[0].links[3].text",
        "note": "称竞争解释的「快速回落」预期「仅有一个盘中观测」,漏列同窗收盘口径先例: VIX 2026-11-04 收盘 16.61→11-05 28.18(+69.66%),四个交易日内回到 11-11 的 17.49(较 11-05 -37.93%);同期 SPX 11-05 -4.36%、NIKKEI225 11-05/11-06 -1.79%/-5.96%(series_store[VIX/SPX/NIKKEI225] 日频收盘)。该未披露事实支持竞争解释的预期;裁定「尚不能区分」本已偏保守,方向不变。",
        "original": "但其『快速回落』预期仅有一个盘中观测(2026-11-23 快照 27.01,较 2026-11-20 收盘 -24.7%,非收盘)",
        "fix": "但其『快速回落』预期在本跳升上仅有一个盘中观测(2026-11-23 快照 27.01,较 2026-11-20 收盘 -24.7%,非收盘);同窗另有一次收盘口径先例: 2026-11-04→11-05 VIX 16.61→28.18(+69.7%),至 11-11 回落至 17.49(四个交易日,较 11-05 -37.9%),同期 SPX 11-05 -4.36%、NIKKEI225 11-05/11-06 -1.79%/-5.96%——与「冲击主导、快速回落」相容",
    },
    {
        "severity": "MINOR",
        "where": "agent_judgment.json l3.contradictions[2].statement(C3③);牵动 reader_map.transmission[0].links[0].verdict_note 的敏感性披露",
        "note": "冻结日历除日本政策目标两条外另有三条 EA_HICP_YOY 实录(RC-EA-HICP-2021M05/2022M06/2025M03),呈「次月 1 日快报+月中终值」两档;均不覆盖本窗月份。按该两档形态,两次欧央行变更决议日前可见读数应为 2026-05=3.2、2026-08=3.2,环1 注记「2.9 低于 2026-05 峰值 3.2」这一条反向观察不成立(另一条 371 天反向观察仍在,n=2),裁定不变。",
        "original": "日历实录仅覆盖日本政策目标两条",
        "fix": "本窗月度通胀读数无日历实录(日历仅有日本政策目标两条与三条历史期 EA HICP 快报/终值实录 2021M05、2022M06、2025M03);若按该两档形态(次月 1 日快报)计,两次欧央行变更决议日前可见读数为 2026-05=3.2、2026-08=3.2,环1「2.9 低于峰值」一象不成立,裁定不变",
    },
    {
        "severity": "MINOR",
        "where": "agent_judgment.json l4.scenarios[1].rows.falsification.threshold 与 trigger.condition(S2-CONVERGE)",
        "note": "S2 情景含欧元区<3.0%、日本<2.0%、水平差≤1.0 个百分点三分量,证伪阈值只覆盖欧元区分量(两月均不低于 3.5%),日本端与水平差分量无对应证伪,触发条件亦缺水平差分量;S1 三分量齐全,两情景不对称。",
        "original": "若观测月 2026-11 与 2026-12 两月 EA_HICP_YOY 同比均不低于 3.5%(未回落),「以一次性因素为主、回落至 3.0% 以下」的前提被证伪;政策分量(按兵不动)不设数值触发,以决议实录核验",
        "fix": "若观测月 2026-11 与 2026-12 两月 EA_HICP_YOY 同比均不低于 3.5%(未回落),「以一次性因素为主、回落至 3.0% 以下」的前提被证伪;或两月日本全国 CPI 同比均不低于 2.0%,或两月两地水平差(欧元区减日本)均不低于 1.0 个百分点,收敛情景的日本端/水平差分量被证伪;政策分量(按兵不动)不设数值触发,以决议实录核验(触发条件同步补「且两地水平差不超过 1.0 个百分点」)",
    },
    {
        "severity": "MINOR",
        "where": "agent_judgment.json reader_map.transmission[0].links[2].verdict_note((b) 时点论证);l3.mechanism_chains[0].links[3].text",
        "note": "时点论证只量到政策决议日(2026-10-30、2026-09-16),未检验链条首环的读数发布日: 引擎推定发布日 2026-11-16(欧元区 4.0)与 2026-11-20(日本 2.44)均落在跳升窗内,且为窗内两个最大单日跳升日(VIX +18.70%/+26.20%)。席位跨地区复核(series_store 日频收盘): 跳升窗 11-13→11-20 SPX -8.61%、NIKKEI225 -7.70%、DAX -7.28%、CAC40 -5.27%(均不深于美股),两日 EURUSD/USDJPY 变动幅度不超过 0.23%——未出现地区特异性读数冲击证据,「尚不能区分」不变,但应补注。",
        "original": "(b)『VIX 与政策日历联动』在时点上不成立: VIX 跳升集中于 2026-11-13→2026-11-20(19.30→35.89),距最近政策日 2026-10-30(BOJ 维持决议,无变更)14 天、距 ECB 最近生效日 2026-09-16 58 天。",
        "fix": "(b)『VIX 与政策日历联动』在时点上不成立: VIX 跳升集中于 2026-11-13→2026-11-20(19.30→35.89),距最近政策日 2026-10-30(BOJ 维持决议,无变更)14 天、距 ECB 最近生效日 2026-09-16 58 天;跳升窗内含两条推定读数发布日(2026-11-16 欧元区 4.0、2026-11-20 日本 2.44,当日 VIX +18.7%/+26.2%),但窗内四地股指跌幅均不深于美股(SPX -8.61%、NIKKEI225 -7.70%、DAX -7.28%、CAC40 -5.27%),两日欧元、日元汇率变动幅度不超过 0.23%,读数发布主因未获跨地区支持。",
    },
    {
        "severity": "MINOR",
        "where": "agent_judgment.json reader_map.turnings(三转折);MAP_REPORT「过去一年的三个转折」及其候选面折叠表",
        "note": "引擎候选面(report.json research_plan.turning_candidates)4 条,三转折采用其中 3 条,未说明为何不采用幅度最大的日本全国 CPI 2025-11→2026-02(2.9→1.27,Δ-1.63)候选(其变动主要发生在六个月窗之前,谷底 2026-02 的 1.27 已在 turnings[0] 写明);读者报告并排展示候选表,宜补一句取舍理由。",
        "original": "(缺句——候选面首行为: JP | inflation | JP_CPI_YOY | 2025-11..2026-02 | 2.9→1.27 | -1.63,三转折节无对应说明)",
        "fix": "于三转折节补注: 引擎候选面另列日本全国 CPI 2025-11→2026-02(2.9→1.27,Δ-1.63)为幅度最大候选,因该回落主要发生在六个月窗(起 2026-05-23)之前、且谷底已在两地走位中写明,不列入三转折。",
    },
    # ------------------------------------------------------------------ NIT
    {
        "severity": "NIT",
        "where": "agent_judgment.json l3.mechanism_chains[0].links[3].text(环4,E2)",
        "note": "环4 归因句无行内【假设】标注(环3 有「传导【假设】」);标注只在 missing_link_note 与对质表因果/竞争解释行。",
        "original": "VIX 跳升时点(2026-11-13→2026-11-20)不与政策日历对齐、欧元区股指不弱于美股,两点不利于紧缩主因,单一归因于两地政策不可证。",
        "fix": "该组合与「紧缩+通胀粘性压制估值」与「全局风险/流动性冲击」两种叙事均相容【假设·归因】;VIX 跳升时点…不与政策日历对齐、欧元区股指不弱于美股,两点不利于紧缩主因,单一归因于两地政策不可证。",
    },
    {
        "severity": "NIT",
        "where": "agent_judgment.json l3.contradictions[2].statement(C3④);quality_gate_notes[4] 末句",
        "note": "「月度数值为事后回顾口径」全称偏宽: 引擎点值格(research_plan.point_values.cells)仅 EA_HICP_YOY、JP_CPI_YOY 标「事后回顾(最新修订值,非当时首发值)」,东京 CPI 与 JP_POLICY_RATE 标「as_collected(采集时点值)」。",
        "original": "④月度数值为事后回顾口径(最新修订值,非当时首发值),当时信息集不可重构。",
        "fix": "④欧元区 HICP 与日本全国 CPI 月度数值为事后回顾口径(最新修订值,非当时首发值),东京 CPI 与月均拆借利率为采集时点值(是否首发值未核),当时信息集不可重构。",
    },
    {
        "severity": "NIT",
        "where": "agent_judgment.json reader_map.regions[1].from_to(日本走位)",
        "note": "「持续回落」非单调: series_store[JP_CPI_YOY] 2025-01 4.03→2025-08 2.72 后 2025-09 2.91、2025-10 2.99 两月回升,再降至 2026-02 的 1.27。",
        "original": "自 2025-01 高点 4.03 持续回落至 2026-02 的 1.27,此后总体回升。",
        "fix": "自 2025-01 高点 4.03 总体回落(2025-09、2025-10 两月小幅回升至 2.91、2.99)至 2026-02 的 1.27,此后总体回升。",
    },
    {
        "severity": "NIT",
        "where": "agent_judgment.json l3.mechanism_chains[0].links[0].text(环1)",
        "note": "「窗内(2026-05..2026-10 月度值)」含 2026-05 期(观测日 05-01 早于窗起 2026-05-23,仅推定发布日在窗内);引擎点值格 n_in_window=5。",
        "original": "窗内(2026-05..2026-10 月度值)",
        "fix": "窗内及其锚后月度值(2026-05..2026-10;2026-05 期观测日在窗前、推定发布日在窗内)",
    },
    {
        "severity": "NIT",
        "where": "agent_judgment.json turnings[2].follow_or_diverge、C1、C3③(东京 CPI 推定发布日)",
        "note": "引擎东京 CPI 推定规则「月末−1天」给出 2026-08-30(周日)与 2026-06-29,而引擎规则串自列官方实录锚为 2026-06-26、2026-10-30(均为当月最后一个周五);按「最后一个周五」计(8 月 08-28、9 月 09-25),决议前可见的最近东京读数仍为 2026-08 期、2026-09 期仍晚于 09-18 决议,结论不变。",
        "original": "决议前可见的最近东京读数为 2026-08 的 1.9(推定发布 2026-08-30)。",
        "fix": "决议前可见的最近东京读数为 2026-08 的 1.9(推定发布 2026-08-30;该推定规则与引擎自列官方实录锚 2026-06-26、2026-10-30 不完全一致,可见性结论不受影响)。",
    },
    {
        "severity": "NIT",
        "where": "agent_judgment.json l4.scenarios[*].rows(政策分量);quality_gate_notes[3]",
        "note": "「以决议实录核验」: 冻结日历对欧央行零条实录,欧央行分量在引擎面暂不可核验,须待日历补录;日本端有两条实录可核。",
        "original": "政策分量(再上调)不设数值触发,以决议实录核验",
        "fix": "政策分量(再上调)不设数值触发,以决议实录核验(欧央行分量须待发布日历补录 ECB 实录后方可核验)",
    },
    {
        "severity": "NIT",
        "where": "agent_judgment.json l3.contradictions[0].statement(C1「窗内动量不分化」)",
        "note": "「动量相近」依赖起点取六个月前锚(2026-04 期: 欧元区 +1.0 对日本 +1.06);自 2026-06 起算为 +1.2 对 +0.77、自 2026-05 为 +0.8 对 +0.91,快慢互换。陈述已限定锚点,建议加敏感性注。",
        "original": "均约一个百分点——「水平与同比方向分化、窗内动量不分化」。",
        "fix": "均约一个百分点(起点=六个月前锚;自 2026-06 期起算则为欧元区 +1.2 对日本 +0.77)——「水平与同比方向分化、窗内动量不分化」。",
    },
    {
        "severity": "NIT",
        "where": "agent_judgment.json l3.mechanism_chains[0].links[2].text;transmission[0].links[1].observed_fact",
        "note": "交叉盘可由证据面两条序列相乘推出: EURUSD×USDJPY=175.609(10-23)→175.194(11-20,-0.24%)→174.321(11-23,-0.73%),欧元未相对日元走强,与「支持竞争解释」一致;可补推算值。",
        "original": "EURJPY 交叉盘不在证据面,利差渠道不可直接检验",
        "fix": "EURJPY 交叉盘不在证据面(以 EURUSD×USDJPY 推算: 175.61→175.19(至 11-20 收盘,-0.24%),欧元未相对日元走强),利差渠道仅可间接检验",
    },
    {
        "severity": "NIT",
        "where": "agent_judgment.json l3.contradictions[1].statement(C2 水平对照)与环3/transmission[0].links[1]",
        "note": "水平差两处所用欧央行利率不同: C2 用 DFR(2.5−1.25=1.25 个百分点),环3/环2 用 MRO(2.65−1.25=1.40 个百分点);均已写明利率名,方向一致,宜统一或并列。",
        "original": "最新政策利率欧元区高于日本约一点二五个百分点(DFR 二点五 vs BOJ 目标约一点二五)。",
        "fix": "最新政策利率欧元区高于日本: 按 MRO 计约一点四零、按 DFR 计约一点二五个百分点(2.65/2.5 vs BOJ 目标约一点二五)。",
    },
    {
        "severity": "NIT",
        "where": "agent_judgment.json l3.contradictions[2].statement(C3①,与同一陈述③互指)",
        "note": "C3① 写「发布日历实录单条(user_directive 基础)」,而同一陈述③写「日本政策目标两条」;冻结日历 JP_POLICY_TARGET 实为两条(均为 user_directive): RC-JP-BOJ-TARGET-2026-09(决议 2026-09-18/生效 2026-09-24/目标 1.25)与 RC-JP-BOJ-MAINT-2026-10(2026-10-30 确认维持 1.25)。目标值条目确为一条,但「单条」与「两条」并置易生歧义。",
        "original": "对照以月均市场口径替代+发布日历实录单条(user_directive 基础)。",
        "fix": "对照以月均市场口径替代+发布日历实录两条(目标值决议一条、维持确认一条,均 user_directive 基础)。",
    },
]

COUNTER = [
    "反方攻击 1(C1): 「窗内动量不分化」是否依赖起点——改自 2026-06 期起算为欧元区 +1.2 对日本 +0.77、自 2026-05 期为 +0.8 对 +0.91(快慢互换)→ 陈述已明写锚=六个月前锚(2026-04 期: +1.0 对 +1.06,series_store 直算一致),不构成错误;列 NIT 建议加敏感性注。",
    "反方攻击 2(C1): 东京都 CPI 佐证是否可靠(该序列 Gate A 列 noncore_missing、仅 10 个月、单一基期文件)→ 判断档已披露缺席状态并只用于同月方向(东京 2.69→2.73 与全国 2.16→2.44 同向上行),未用于同比;攻击不成立。",
    "反方攻击 3(C1): 「同比对照方向相反」是否把日本连续回升写成「回落」造成误导→ 判断档分列「同比对照」(较 2025-10 的 2.99 低 0.55)与「窗内动量」(1.38→2.44),两口径均有数字支撑并已标明;攻击不成立。",
    "反方攻击 4(C2): 「累计幅度相近」是否以月均市场口径冒充宣布值口径→ 已写明「口径不同仅作量级对照」,宣布值/月均/官方目标分列;攻击不成立。但「相隔两天」取欧央行生效日对日央行决议日,同口径(生效对生效、决议对决议)均为 8 天→ 排序不变,列 MINOR。",
    "反方攻击 5(C2): 欧央行决议日为惯例回推,排序是否依赖未证日期→ 「在前/在后」在生效日对生效日(09-16 先于 09-24)与决议日对决议日(回推 09-10 先于实录 09-18)两口径下同向,且判断档明写回推日不参与排序;攻击不成立。",
    "反方攻击 6(C3): 五项缺口是否全部属实、有无多报或少报→ ①②经注册表/序列/新鲜度阈(10 天)/Gate A 证实;③漏计三条历史期 EA HICP 两档实录;④全称偏宽(仅两条序列为事后回顾);⑤与总判断把「事实行缺席(采集器已取到而事实未生成)」写成「序列缺席」,序列面实有至 2026-07 期读数(EA 1.28/JP 1.16);①「实录单条」与③「两条」不一(日历实为两条: 目标值决议+维持确认)→ 结论不变,列 2 MINOR + 2 NIT。",
    "反方攻击 7(链环1,E1): 窗内月度路径是否前视或错月→ 六个月值逐月回贴 series_store 一致;「窗内 2026-05」期观测日(05-01)在窗前、仅推定发布日在窗内(引擎 n_in_window=5)→ 无数值影响,列 NIT。",
    "反方攻击 8(链环2,E1): 「各 25bp」「合计 +50bp」与月均台阶是否可加总→ 四个变更点 (to−from)×100=25/25/25/25;日本四级台阶 11.4+13.7+6.6+18.4=50.1bp(2026-08 为 -0.1bp,未列为台阶),一致;攻击不成立。",
    "反方攻击 9(链环3,E2): 「EURJPY 交叉盘不在证据面、不可直接检验」是否放过可做检验——以 EURUSD×USDJPY 直算 175.609(10-23)→175.194(11-20,-0.24%)→174.321(11-23,-0.73%),欧元未相对日元走强→ 与「支持竞争解释」一致;美元端利率未纳入已在注记自陈;攻击不成立,列 NIT 建议补推算值。",
    "反方攻击 10(链环4,E2): 「快速回落仅有一个盘中观测」是否漏反向事实——同窗 2026-11-04→11-05 VIX 16.61→28.18(+69.66%),四个交易日内回落至 11-11 的 17.49(-37.93%),SPX 11-05 -4.36%、NIKKEI225 11-05/11-06 -1.79%/-5.96%→ 存在一条未披露的收盘口径「快涨快回落」先例,支持竞争解释的预期;裁定「尚不能区分」本已保守,方向不变,列 MINOR。",
    "反方攻击 11(链环4,E2): 「VIX 跳升不与政策日历对齐」是否漏检读数发布日——两个最大单日跳升日恰为推定通胀发布日(11-16 欧元区 4.0: VIX +18.70%;11-20 日本 2.44: +26.20%);跨地区复核: 跳升窗 11-13→11-20 四地股指 SPX -8.61%、NIKKEI225 -7.70%、DAX -7.28%、CAC40 -5.27%(均不深于美股),两日 EURUSD/USDJPY 变动不超过 0.23%→ 未出现地区特异性读数冲击证据,结论不变,列 MINOR(补注)。",
    "反方攻击 12(链环1 对质,读数驱动 vs 程序驱动): 「2.9 低于 2026-05 峰值 3.2」的反向观察是否依赖发布规则——若按日历三条 EA HICP 实录的「次月 1 日快报+月中终值」两档形态,两次决议日前可见读数为 2026-05=3.2、2026-08=3.2,该条反向观察不成立;另一条(2025-06-11→2026-06-17 共 371 天维持 2.15/2.0 而读数由 1.7 升至 3.0)仍在,n=2→ 裁定「尚不能区分」不变,列 MINOR(披露敏感性)。",
    "反方攻击 13(情景 S1/S2): 截止日是否已触发/已证伪、证伪指标是否可观测——S1 三项水平条件(≥4.0/水平差≥1.5/VIX 收盘>30)在截止日可得读数上已全部成立(4.0/1.56/35.89),但触发绑定尚未发布的 2026-11/2026-12 期读数,形式上未触发(延续情景信息量偏低,设计使然);S2 前提(欧元区<3.0)未被证伪;证伪指标 EA_HICP_YOY/JP_CPI_YOY 在册,2026-12 期推定入档 2027-01-16/2027-01-20 早于期限 2027-02-15;S2 证伪只覆盖欧元区分量→ 不构成「不可观测」,列 MINOR。",
]

OUT_OF_SCOPE = [
    "MAP_REPORT.md 第 5 行「研究时点口径: …按月末时点化为研究截止日 2026-11-30…本报告全部窗口/锚点/政策面绑定该时点(数据=当时已发布面,后来发布的数据不回填)」与第 4/6 行(研究截止日=2026-11-23)相抵,且与本运行实际口径(report.json run.evidence_gate.publication_basis=snapshot_presence、点值格标「事后回顾」)不符——引擎模板文字;判断档自身的截止日披露(总判断首句、quality_gate_notes[4])一致无误。",
    "MAP_REPORT.md 第 8 行「三个对照时点=日历点锚(截止日−12月/−3月/最新一期)」与本问实际锚(6个月前/最新一期,见「四地三时点环境对照」表)不符——判断档 quality_gate_notes[5]① 已登记该硬编码标签缺口。",
    "判断档三条 transmission[*].verdict_note(对质理由,如「共 371 天…未触发变更」)与三条 turnings[*].narrative(逐月叙述)、六条 quality_gate_notes 均未渲染进 MAP_REPORT.md/FULL_REPORT.md/report.md;已渲染的 41 个长文本块与判断档逐字一致(复算表 #245)。读者面只见裁定词、不见对质理由。",
    "MAP_REPORT.md「政策一年窗路径」对欧央行两序列写「净变动 +25bp(2.25→2.5)」,而同句列出窗内两个 +25bp 变更点(2026-06-17、2026-09-16): 引擎 net_bp 取「窗首尾观测差」,窗内首个观测即为 06-17 变更后的 2.25,致读者面净变动与窗内事件合计(+50bp)不闭合;判断档未引用该数,用的是六个月锚间 +50bp(复算表 #38)。",
]

SIX_CHECKS = [
    ("C1-INFL-DIVERGE(水平与同比方向分化、窗内动量不分化)", [
        ("证据相关性", "相关。证据引用 JP_CPI_YOY@2026-10-01、EA_HICP_YOY@2026-10-01 均在证据索引;水平差 1.56、同比对照(2025-10: 2.1/2.99,同比差 +1.9/−0.55)、欧元区锚间动量 +1.0 全部由 series_store 直算一致(复算表 #24–#28、#30);日本锚间动量 +1.06 为上下文点(#31,判断档写「均约一个百分点」)。"),
        ("支持度", "「约一点五六」「均约一个百分点」为限定措辞,与证据强度相称;东京序列只作同月方向佐证,并披露 Gate A noncore_missing、无 L1 事实行、缺去年同月基期(#29、#143、#185–#188)。"),
        ("竞争解释", "两条(能源/进口传导 vs 需求与政策组合)均标【假设】,并写明引擎无分项构成与核心通胀序列、不可在引擎面验证——真正竞争且同证据可容纳,非稻草人。"),
        ("反对证据", "动量结论对起点敏感(自 2026-06 期起算欧元区 +1.2 对日本 +0.77,见 #243)而未加注——陈述已限定锚点,列 NIT;无其他未披露反向事实。"),
        ("结论是否超出证据", "未超出。缺基期处(东京)如实拒答同比,未以相邻月替代。"),
        ("证伪条件可观测性", "C1 的两条竞争解释均自陈不可在引擎面验证、未设证伪阈值,如实并列,不以单侧证据裁;可观测的证伪面由 L4 两情景承担(见情景节)。"),
    ]),
    ("C2-POLICY-SYNC-LEVEL-GAP(同向收紧、累计幅度相近、水平分化、口径基础不对称)", [
        ("证据相关性", "相关。六个证据引用全在索引;DFR/MRO 变更日与幅度(2026-06-17、2026-09-16,各 +25bp)、BOJ 日历两条(09-18 决议/09-24 生效/目标 1.25;10-30 维持)、月均台阶(0.727→1.227,+50bp)、68 天、水平差 1.25 由 series_store 与冻结日历直算一致(#39–#45、#51、#57–#58、#69–#73、#82)。"),
        ("支持度", "「累计幅度相近」附口径声明(宣布值口径 vs 月均市场口径,仅作量级对照);欧央行决议日标【推断】;总判断写「其后决议面不可判【尚未验证】」。措辞与证据强度相称。"),
        ("竞争解释", "读数驱动 vs 正常化/汇率-金融稳定驱动,后者写明引擎无央行表态文本序列、月频不可区分——真正竞争。"),
        ("反对证据", "(1)「相隔两天」两端口径不对称,同口径 8 天(#67–#68);(2)水平差用 DFR(1.25)而环3 用 MRO(1.40),见 #244。均不改变「欧元区在前/高于日本」方向 → MINOR + NIT。"),
        ("结论是否超出证据", "未超出;「口径基础不对称」与引擎 dimension_gaps(JP_POLICY_TARGET=registry_absent)一致(#195),数据需求面 ECB_MRO/ECB_DFR=insufficient_coverage 如实披露(#196)。"),
        ("证伪条件可观测性", "由传导环1 的对质承担(读数可见性 vs 程序驱动),区分指标 EA_HICP_YOY 在证据面(#235);两解释在其上的预期方向不同(决议前读数已抬升 / 无稳定先后关系)。"),
    ]),
    ("C3-EVIDENCE-GAPS(证据不足五项)", [
        ("证据相关性", "相关。五项逐一对应问句「哪些证据不足」。"),
        ("支持度", "「引擎可核者五项」逐项序列级证实: ①注册表与 series_store 均无 JP_POLICY_TARGET(#64);②末观测 2026-09-16、距截止 68 天>注册表新鲜度阈 10 天、L1 quality_status=DEGRADED(#51–#55);③月度公布日为引擎推定规则(点值格 publication_date 附规则串,#152–#161);④仅 EA_HICP_YOY、JP_CPI_YOY 为「事后回顾」(#240);⑤Gate A noncore_missing 含两 GDP 序列、注册表 JP/EA 面无核心通胀(#189–#192)。"),
        ("竞争解释", "两条(此后无新决议 vs 有新决议)标【假设】,指明须官网核对、引擎外、待授权——如实并列。"),
        ("反对证据", "③漏计三条历史期 EA HICP 两档实录(#228);⑤与总判断把「事实行缺席」写成「序列缺席」(#190)→ 2 MINOR;④全称偏宽、①「实录单条」与③「两条」并置 → 2 NIT。"),
        ("结论是否超出证据", "未超出。契约 STALE 项(ECB_DFR@2026-09-16=2.5)披露一致(#202–#203);缺席格写「数据不可得」而非「无变化」(#197);BOJ 目标 1.25 归属日历实录,未把月均序列值写成官方目标(#198)。"),
        ("证伪条件可观测性", "竞争解释的裁定路径在引擎外(官网核对),已标注「须单独标注,待用户授权」,未冒充引擎可核。"),
    ]),
    ("M1-DIVERGE-TRANSMIT(通胀读数→政策决议→汇率→风险资产,四环+三环对质)", [
        ("证据相关性", "相关。环1 六个月两条路径(#122–#136)、环2 四个欧央行变更点与日本月均台阶(#40–#45、#69–#73)、环3 两口径汇率窗(#100–#106)、环4 同日收盘口径与 VIX 路径(#107–#121)全部回贴一致;四环证据引用均在索引(#210)。"),
        ("支持度", "环1/环2 标 E1,文字为「观察:」;环3 标 E2 且行内「传导【假设】」;环4 标 E2,归因句无行内标签而 missing_link_note 写明「归因环节为【假设】」(NIT)。对质裁定「尚不能区分/支持竞争解释/尚不能区分」均附置信注记(n=2、单月窗、交叉盘缺席)。"),
        ("竞争解释", "四环各有竞争解释且同证据可容纳: 程序驱动、美元全局主导、全局冲击主导——非稻草人;MAP_REPORT 逐环渲染「因果假设/竞争解释」两行(均带【假设】)。"),
        ("反对证据", "(1)环4 漏列同窗 11-05→11-11 收盘口径快涨快回落先例(#224、#227);(2)环4 时点论证未检验两条推定读数发布日(#225–#226);(3)环1 对质注记「2.9 低于峰值 3.2」对发布规则敏感(#228)。三项经席位补检均不改变裁定 → 3 MINOR。"),
        ("结论是否超出证据", "未超出。环2「支持竞争解释」与该行观测一致(EURUSD -2.51%、USDJPY +1.82%、DXY +2.23%,两货币同对美元走弱);环3「尚不能区分」在时点上倾向竞争解释而幅度判据不足,保守可辩。"),
        ("证伪条件可观测性", "被点名的区分指标 EA_HICP_YOY、EURUSD、VIX 均在注册表与证据索引(#235–#237);两解释在其上的预言方向确实不同(决议前读数抬升/无稳定关系;对美元方向分立/同向随美元;与政策日历联动且回落慢/独立于日历且快回落)。"),
    ]),
    ("L4 情景 S1-DIVERGE-PERSIST / S2-CONVERGE", [
        ("证据相关性", "敏感变量 EA_HICP_YOY/JP_CPI_YOY 与证伪指标在册(#179);S1 前提(≥3.5/≥2.0/水平差≥1.5)与截止日读数相容(4.0/2.44/1.56,#174–#177),S2 前提(<3.0)未被证伪(#175)。"),
        ("支持度", "两情景均标「【假设·非预测】」,资产方向标「方向性推演,非幅度预测」;置信档「有相关证据/纯逻辑推理」分记。"),
        ("竞争解释", "两情景方向互补(S1 维持 vs S2 回落,#180),非孤证。"),
        ("反对证据", "S1 三项触发水平条件在截止日可得读数上已全部成立(#178),触发绑定未发布的 2026-11/2026-12 期读数——形式上未触发,信息量偏低但属延续情景设计使然;S2 证伪只覆盖欧元区分量(MINOR-5)。"),
        ("结论是否超出证据", "未超出;情景与近一月观察的关系已写明(S2「属并列反例情景」)。"),
        ("证伪条件可观测性", "期限 2027-02-15 晚于 2026-12 期读数推定入档日(2027-01-16 欧元区/2027-01-20 日本,#173、#182);S1 证伪阈值覆盖三分量(#181),S2 仅覆盖欧元区分量(#184);政策分量「以决议实录核验」中欧央行端在冻结日历无实录(NIT)。"),
    ]),
    ("历史类比(0 段)与总判断/走位/对质表", [
        ("证据相关性", "历史类比 0 段如实写明;引擎 analog 执行数字(扫描 1871/有效 74/TOP1 2025-03 距离 0.727)与 S6 步面一致(#211–#215)。"),
        ("支持度", "一句总判断的每个数字(4.0/2.44/2.1/2.99/2.65/2.5/1.25/0.727→1.227/+50bp/68 天)均回贴一致;四地三时点 anchor_echo 12/12(#10–#22)。"),
        ("竞争解释", "对质表三行裁定计数 0·1·2 与 quality_gate_notes[1] 一致(#217);每条矛盾陈述并列 2 条竞争解释(#218)。"),
        ("反对证据", "三转折未说明未采用幅度最大候选的理由(MINOR-7);「先后未定」措辞与月频分辨率相称,「相隔两天」口径不对称(MINOR-2)。"),
        ("结论是否超出证据", "未超出;「方向同、水平分化、证据面不对称」三项均有对应数字。"),
        ("证伪条件可观测性", "已渲染的 41 个长文本块与判断档逐字一致(#245);未渲染的三条对质理由与逐月叙述见「范围外观察」。"),
    ]),
]


def main():
    tbl_p, sum_p, extra_p, out_dir = sys.argv[1:5]
    with open(tbl_p, encoding="utf-8") as f:
        table = f.read().strip()
    with open(sum_p, encoding="utf-8") as f:
        summ = json.load(f)
    with open(extra_p, encoding="utf-8") as f:
        extra = f.read().strip()
    pts, mis = int(summ["recompute_points"]), int(summ["recompute_mismatches"])
    n_ctx = len(summ.get("ctx_points", []))
    n_minor = sum(1 for x in ITEMS if x["severity"] == "MINOR")
    n_nit = sum(1 for x in ITEMS if x["severity"] == "NIT")
    n_major = sum(1 for x in ITEMS if x["severity"] == "MAJOR")
    assert n_major == 0 and mis == 0

    notes = (
        "裁决 UPHELD: 零 MAJOR、无 REVISE 级问题。只读复算 %d 点全部命中(偏离 %d;另列上下文点 %d 个,不计入),"
        "覆盖规程 §3 ①—⑭及「最近六个月」窗口: 截止日 2026-11-23 三面一致,全文无晚于截止日的观测/发布/决议/生效被引用;"
        "12 个点值锚格逐格由 series_store 按「推定发布日≤锚日」直算一致(六个月前锚取 2026-04 期,无前视);"
        "同比基期 2025-10 在场(东京缺基期已如实拒答);政策面决议/生效/目标/距离与冻结日历及序列变更日逐项一致,"
        "宣布值/月均/官方目标分记,无待生效决定;三利率分解恒等(残差 0)与资产月窗 4/4 一致;"
        "三转折与引擎候选面前值→后值一致,「先后未定」措辞与月频分辨率相称;传导链四环数字可回贴引擎面,E2 环带【假设】标注;"
        "情景期限 2027-02-15 晚于 2026-12 期读数推定入档日(2027-01-16/2027-01-20),截止日未触发未证伪;"
        "五项诚实缺席经 Gate A/注册表/冻结日历序列级证实;契约 1 项 STALE(ECB_DFR@2026-09-16=2.5)披露一致;"
        "缺席格写「数据不可得」非「无变化」,BOJ 目标 1.25 归属日历实录。"
        "六查: 三条矛盾陈述与机制链四环证据相关,定性措辞与证据强度相称(【推断】/【假设】/【尚未验证】标注齐备),"
        "竞争解释在列且同证据可容纳;反方攻击 %d 条均未推翻结论(动量结论依赖锚点、交叉盘可由两条序列推出、"
        "VIX 跳升日与推定读数发布日重合等,席位补检后方向与裁定不变)。"
        "问题清单: MINOR %d 条(节奏对照「相隔两天」混用生效日与决议日口径,同口径 8 天;环4 对质注记漏列同窗 11-05→11-11 收盘口径快涨快回落先例,"
        "且时点论证只量到决议日、未检验读数发布日;C3③「日历实录仅覆盖日本政策目标两条」漏计三条历史期 EA HICP 两档实录;"
        "C3⑤与总判断把「事实行缺席」写成「序列缺席」(序列面有至 2026-07 期读数);S2 证伪只覆盖欧元区分量;三转折未说明未采用幅度最大候选的原因),"
        "NIT %d 条(行文与披露),均不构成阻断。"
        "范围外观察(引擎渲染,不计入裁决): 读者报告头部一条写「研究截止日 2026-11-30」与另两行 2026-11-23 相抵;"
        "「三个对照时点=截止日−12月/−3月」与本问锚不符;三条对质理由与三条逐月叙述未渲染;"
        "欧央行一年窗路径「净变动 +25bp」与窗内两个 +25bp 变更点不闭合。"
    ) % (pts, mis, n_ctx, len(COUNTER), n_minor, n_nit)

    verdict = {
        "seat": SEAT,
        "reviewer": REVIEWER,
        "verdict": "UPHELD",
        "overall": "UPHELD",
        "notes": notes,
        "items": ITEMS,
        "must_fix": [],
        "counterexamples_sought": COUNTER,
        "recompute_points": pts,
        "recompute_mismatches": mis,
        "mismatch_details": summ.get("mismatch_details", []),
        "audited_at": "2026-11-24",
    }
    vp = os.path.join(out_dir, "VERDICT-round1.json")
    with open(vp, "w", encoding="utf-8") as f:
        json.dump(verdict, f, ensure_ascii=False, indent=1)
        f.write("\n")

    L = []
    L.append("# Audit-R32 · N30 · Round-1 独立语义审查席纪要(PROSE)\n")
    L.append("- 席位: %s / %s(零上下文;与研判席、操作席及其他审查席之间无任何通信,全部产出仅为文件)" % (SEAT, REVIEWER))
    L.append("- 受审运行: `%s`" % RUN)
    L.append("- 代码印章: `%s`(MAP_REPORT 头部第 4 行)" % CODE)
    L.append("- 受审对象: agent_judgment.json 全文(l3/l4/reader_map/quality_gate_notes/agent_declaration,schema 1.1)与读者报告(MAP_REPORT.md / FULL_REPORT.md / report.md)中的判断文字")
    L.append("- 裁决: **UPHELD**(MAJOR %d / MINOR %d / NIT %d;must_fix 空)" % (n_major, n_minor, n_nit))
    L.append("- 复算: 计入比对点 **%d**,偏离 **%d**;上下文点 %d 个(不计入);逐点出处键见下表" % (pts, mis, n_ctx))
    L.append("")
    L.append("## 0. 独立性与只读声明\n")
    L.append("- 未联网;未运行引擎 plan/attach/report/archive/replay/update 等任何写操作;未调用 record_semantic_verdict;未委派子代理。")
    L.append("- 未读取规程 §2 禁区: research_archive/、树内 docs/、/tmp/r32-accept/out|scripts|replay|install*|final*(只读安装树内两份引擎源码文件除外)、其他运行目录、review 目录下除本席产出目录以外的任何目录、~/investment-agent-product。")
    L.append("- 只读取的只读面: 受审运行目录下 report.json、agent_judgment.json、MAP_REPORT.md、FULL_REPORT.md、report.md、evidence_index.json、views_digest.json、AGENT_SEAT_ENVELOPE.json、question_verbatim.txt、root_overlay/config/release_calendar.json、root_overlay/config/metric_registry.json、root_overlay/data/daily/research_snapshot_20261123.json;以及只读安装树内 scripts/research_contract/judgment_contract.py 与 text_consistency.py(仅用于核验 quality_gate_notes[5]①② 的属实性,以路径参数只读打开)。")
    L.append("- 未使用记忆或常识补数;本纪要引用的每个数字均来自上述只读面并注明出处键(复算表行号 #n 对应表内「出处键」列;日频收盘类数字出处为 series_store[<metric_id>].dates/values)。")
    L.append("- 自写脚本与中间表全部在本席目录 /tmp/r32-accept/review4/N30_round1/;受审运行目录与安装树未写入任何文件。")
    L.append("")
    L.append("## 1. 复算方法与计数\n")
    L.append("- 逐点先从冻结快照 series_store、冻结日历、report.json 引擎面直算,再与报告/判断档文字比对;每条「报告值」均经字面片段守卫(确认该转述确实存在于判断档或读者报告原文,未命中 0 条)。")
    L.append("- 锚格规则: 月频序列以「引擎推定发布日 ≤ 锚日」的最新观测为锚(EA HICP 月末+16 天、日本全国 CPI 月末+20 天、东京 CPI 月末−1 天、BOJ 月均 月末+5 天;与点值格 publication_date 及规则串一致);六个月前锚(2026-05-23)因此取 2026-04 期,无前视(复算表 #10–#22、#74–#77)。")
    L.append("- 单位约定: 1 个百分点 = 100bp;「bp」换算按 (差)×100。")
    L.append("- 分档: 「一致」计入命中;「上下文(不计入)」为席位补充检验(反方攻击、敏感性、范围外观察),不计入命中/偏离。")
    tally, ctxn = {}, {}
    for ln in table.splitlines():
        if not ln.startswith("| ") or ln.startswith("| #"):
            continue
        head = ln.split("|", 3)
        try:
            int(head[1].strip())
        except ValueError:
            continue
        cat = head[2].strip()
        m = re.search(r"\| (一致|偏离|上下文\(不计入\)) \|", ln)
        st = m.group(1) if m else "?"
        key = cat if (st == "一致" or "不计入" in cat) else cat + "(" + st + ")"
        bucket = tally if st in ("一致", "偏离") else ctxn
        bucket[key] = bucket.get(key, 0) + 1
    assert sum(tally.values()) == pts and sum(ctxn.values()) == n_ctx, (sum(tally.values()), sum(ctxn.values()))
    L.append("- 分类计数(计入点): " + "; ".join("%s=%d" % kv for kv in sorted(tally.items(), key=lambda kv: (-kv[1], kv[0]))))
    L.append("- 分类计数(上下文点,不计入): " + "; ".join("%s=%d" % kv for kv in sorted(ctxn.items(), key=lambda kv: (-kv[1], kv[0]))))
    L.append("")
    L.append("## 2. 复算清单(逐点: 出处键 / 直算值 / 报告值 / 一致与否)\n")
    L.append(table)
    L.append("")
    L.append("## 3. 六查逐项结论(证据相关性 / 支持度 / 竞争解释 / 反对证据 / 结论是否超出证据 / 证伪条件可观测性)\n")
    for title, rows in SIX_CHECKS:
        L.append("### %s\n" % title)
        for k, v in rows:
            L.append("- **%s**: %s" % (k, v))
        L.append("")
    L.append("## 4. 反方攻击记录(每条 L3 陈述与机制链至少一条;共 %d 条)\n" % len(COUNTER))
    for c in COUNTER:
        L.append("- %s" % c)
    L.append("")
    L.append("## 5. 问题清单(MAJOR %d / MINOR %d / NIT %d)\n" % (n_major, n_minor, n_nit))
    L.append("### MAJOR(无)\n")
    L.append("未发现数字/日期/方向错误、缺基期给同比、相邻口径冒充、事后信息冒充当时可知、未标注的超证据结论或不可观测的证伪条件。\n")
    for sev in ("MINOR", "NIT"):
        L.append("### %s(%d)\n" % (sev, sum(1 for x in ITEMS if x["severity"] == sev)))
        for i, x in enumerate([y for y in ITEMS if y["severity"] == sev], 1):
            L.append("%d. **%s-%d** 位置: %s" % (i, sev, i, x["where"]))
            L.append("   - 问题: %s" % x["note"])
            L.append("   - 原句: 「%s」" % x["original"])
            L.append("   - 改句: 「%s」" % x["fix"])
        L.append("")
    L.append("## 6. 范围外观察(引擎渲染/交付面;不计入裁决,供操作席参考)\n")
    for o in OUT_OF_SCOPE:
        L.append("- %s" % o)
    L.append("")
    L.append("## 7. 席位补检用上下文数字(extra_ctx.txt 原文;只读直算,不计入复算点)\n")
    L.append("```")
    L.append(extra)
    L.append("```")
    L.append("")
    L.append("## 8. 席位脚本与中间表(同目录,供复核)\n")
    L.append("- recompute_n30.py → recompute_table.md、recompute_summary.json(复算主体)")
    L.append("- extract_*.py → *_dump.txt(只读面转储: engine_face / l1_contract / snapshot / calendar_registry / l3_l4 / steps / misc / regions)")
    L.append("- peek_daily.py、peek_jppath.py、peek_daily_window.py、extra_ctx.py → daily_tails.txt、daily_window_nov.txt、extra_ctx.txt(日频与上下文补检)")
    L.append("- build_outputs.py → 本文件与 VERDICT-round1.json")
    pp = os.path.join(out_dir, "PROSE-round1.md")
    with open(pp, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("wrote", vp, pp)
    print("points", pts, "mismatches", mis, "ctx", n_ctx, "items", n_major, n_minor, n_nit, "counter", len(COUNTER))


if __name__ == "__main__":
    main()
