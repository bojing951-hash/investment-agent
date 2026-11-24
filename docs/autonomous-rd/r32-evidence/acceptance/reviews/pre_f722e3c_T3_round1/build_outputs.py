#!/usr/bin/env python3
"""Seat-owned output builder for the T3 Round-1 independent semantic review.

Usage:
  python3 -I build_outputs.py <agent_judgment.json> <recompute_table.tsv> <recompute_summary.json> <out_dir>

Reads the seat's recompute table/summary and the item list defined below, asserts every quoted
`original` sentence occurs verbatim in agent_judgment.json, then writes:
  <out_dir>/PROSE-round1.md
  <out_dir>/VERDICT-round1.json
"""
import csv
import json
import os
import sys

AJ_P, TSV_P, SUM_P, OUT = sys.argv[1:5]
with open(AJ_P, "r", encoding="utf-8") as fh:
    BLOB = json.dumps(json.load(fh), ensure_ascii=False)
with open(TSV_P, "r", encoding="utf-8", newline="") as fh:
    ROWS = list(csv.DictReader(fh, delimiter="\t"))
with open(SUM_P, "r", encoding="utf-8") as fh:
    SUM = json.load(fh)

# ------------------------------------------------------------------ 问题清单
ITEMS = [
    # ================= MAJOR =================
    dict(id="MA-1", sev="MAJOR", pts=["P77"],
         where="agent_judgment.json reader_map.turnings[1].follow_or_diverge(转折 T2:欧元区 HICP 同比 2026-05);MAP_REPORT.md L168;report.md / FULL_REPORT.md 转折表同句",
         original="日本端同窗通胀下行(2026-05 1.53),两地背离;ECB 随后首次上调(2026-06-11 决议、2026-06-17 生效),跟进方向一致,月频先后未定。",
         note="""T2 的同窗为 2026-02→2026-05;series_store.JP_CPI_YOY 该窗由 1.27 升至 1.53(+0.26),并非下行,与欧元区同向上行,且与 T1 叙述「此后总体回升」自相矛盾。「同窗下行/两地背离」方向与证据相左。""",
         fix="""日本端同窗通胀自谷底回升(2026-02 1.27→2026-05 1.53),与欧元区同向上行、同窗并未背离;ECB 随后首次上调(2026-06-17 生效;决议日 2026-06-11 为引擎按惯例回推),跟进方向一致,月频先后未定。"""),
    dict(id="MA-2", sev="MAJOR", pts=["P76"],
         where="agent_judgment.json reader_map.turnings[0].follow_or_diverge(转折 T1:日本全国 CPI 同比 2026-02);MAP_REPORT.md L168;report.md / FULL_REPORT.md 转折表同句",
         original="同期欧元区 HICP 反向上行(2026-02 1.9→2026-05 3.2),两地通胀转折方向相反;月频证据下两个转折的相对先后未定。",
         note="""T1 的窗为 2025-11→2026-02;该窗内 series_store.EA_HICP_YOY 由 2.1 降至 1.9(2025-11 2.1、2025-12 2.0、2026-01 1.7、2026-02 1.9),与日本同向下行;所引「1.9→3.2」属 2026-02→2026-05 另一窗。「同期反向上行」不成立。""",
         fix="""日本 2025-11→2026-02 下行期内,欧元区 HICP 亦小幅下行(2.1→1.9),两地同向;其后欧元区于 2026-02→2026-05 转为上行(1.9→3.2)——两个转折符号相反、时间错位、以 2026-02 相接,月频证据下谁先转折不可判。"""),
    dict(id="MA-3", sev="MAJOR", pts=["P75"],
         where="agent_judgment.json l3.mechanism_chains[0].links[0].text(M1 step1,E1 观察环);reader_map.regions[1].from_to(日本走位同句);MAP_REPORT.md L127",
         original="JP_CPI_YOY 自 2025-07 高点 3.1 回落至 2026-02 的 1.27,此后总体回升至 2026-10 的 2.44。",
         note="""series_store.JP_CPI_YOY 2025-06=3.27 高于 2025-07 的 3.1,2025 年内最大为 2025-01 的 4.03;「2025-07 高点」关系词错,引擎 S4_history 面亦无高点标记。日本走位同句「2025-07 高点 3.1 回落至 2026-02 的 1.27,此后总体回升」同改。""",
         fix="""JP_CPI_YOY 自 2025 年初高位(2025-01 4.03)持续回落,经 2025-07 的 3.1 至 2026-02 的 1.27,此后总体回升至 2026-10 的 2.44。(日本走位同句改为「2025 年初高位(2025-01 4.03)持续回落,经 2025-07 的 3.1 至 2026-02 的 1.27,此后总体回升」。)"""),
    dict(id="MA-4", sev="MAJOR", pts=["P95", "P53"],
         where="agent_judgment.json reader_map.transmission[0].links[0].face_off_verdict(「支持主解释」)与 verdict_note(对质表第 1 行);MAP_REPORT.md L149、L153;与 l3.contradictions[1].competing_explanations[1] 自相矛盾",
         original="两次 ECB 决议前均已见通胀读数高于年初水平(2026-06-11 决议前可见 2026-04=3.0、2026-09-10 决议前可见 2026-07=2.9,均高于 2026-02 的 1.9;2026-09-10 决议前可见读数低于 5 月峰值 3.2),与读数驱动相容;但样本仅两次、月频分辨有限,程序驱动不被排除——本月窗口裁定,置信有限。",
         note="""越裁:两解释对同一指标(决议前可见读数)的预期未分立——程序驱动解释的预期是「无稳定先后关系、平稳期亦可加息」,并不预言「决议前读数不高」;n=2 的两次加息前读数抬升对两种解释同样相容。按报告自述对质口径(MAP L153:预期分立且引擎面观测在场才可裁)应为「尚不能区分」,且与同档 C2 竞争解释「月频证据下两种驱动不可区分」矛盾。未披露的反向事实:2025-06-11 至 2026-06-16 间 ECB 利率维持 2.15/2.0 未动,而 HICP 已由 2026-01 的 1.7 升至 2026-04 的 3.0(2026-05-16 公布)。「决议前读数低于 5 月峰值」仅按终值日计成立(冻结日历三条 EA_HICP 实录显示快报在次月 1 日,按快报则 09-10 前可见 2026-08=3.2)。""",
         fix="""face_off_verdict 改「尚不能区分」;verdict_note 改:「两次 ECB 决议前均已见通胀读数高于 2026-02 的 1.9(2026-06-11 决议前可见 2026-04=3.0、2026-09-10 决议前可见 2026-07=2.9),与读数驱动相容;但程序驱动解释对『决议前读数是否抬升』不作相反预期,且 2025-06-11 至 2026-06-16 间利率维持 2.15/2.0 而 HICP 已由 1.7(2026-01)升至 3.0(2026-04),样本仅两次——两种驱动在月频证据下不可区分。」"""),
    dict(id="MA-5", sev="MAJOR", pts=["P93", "P94"],
         where="agent_judgment.json reader_map.transmission[0].links[1].verdict_note(对质表第 2 行);l3.mechanism_chains[0].links[2].text(M1 step3 末句「当前仅水平观测…方向对质不可判」);MAP_REPORT.md L150",
         original="引擎面仅水平观测,利率→汇率为近零渠道(无本地数据支持方向依据),方向对质不可判,如实留白。",
         note="""依据失实:同一快照事实行 derived.m1 给出近一月(2026-10-23→11-23)EURUSD −2.29%、USDJPY +1.57%、DXY +2.06%——欧元、日元同向对美元走弱;MAP L150 该行自身即展示引擎当前面「近30日 1.12215→1.09649(−2.29%)」。观测与竞争解释(两汇率同向随美元)相容,与主解释(方向分立/高利率货币相对走强)的预期不符;两解释对同一指标预言不同且观测在场,按 MAP L153 属可裁,却称不可裁且理由不成立。""",
         fix="""引擎近一月面(2026-10-23→11-23):EURUSD −2.29%、USDJPY +1.57%、DXY +2.06%——欧元与日元同向对美元走弱,与竞争解释(美元全局主导)相容,主解释『方向分立』的预期与本月观测不符;窗内无两地政策变动、单月窗,裁「支持竞争解释(本月窗口,置信有限)」。M1 step3 末句同改:「当前近一月观测为两货币同向对美元走弱(EURUSD 1.0965、月内 −2.29%;USDJPY 158.96、月内 +1.57%;均观测 2026-11-23,11-23 值为当日实时快照、非收盘价),与利差主导的『反向组合』预期不符,本月窗口偏向美元全局解释(置信有限)。」"""),
    dict(id="MA-6", sev="MAJOR", pts=["P96", "P100"],
         where="agent_judgment.json reader_map.transmission[0].links[2].verdict_note(对质表第 3 行);MAP_REPORT.md L151",
         original="单月窗三地同跌无法区分两地政策与全局冲击(NIKKEI225 跌幅大于 DAX 与 SPX,方向与紧缩叙事相容但幅度差亦可由仓位/汇率解释);两解释均与观测相容,留待后续窗复检。",
         note="""主解释的预期之一是「两地股指弱于美股」。同日口径(至 2026-11-20)SPX −9.36%、NIKKEI225 −9.98%、DAX −1.50%、CAC40 +1.86%:日本仅弱 0.62 个百分点,欧元区股指显著强于美股——与主解释在欧元区一端相反;注记只举 NIKKEI225 跌幅大于 DAX 与 SPX 并称「方向与紧缩叙事相容」,未披露 DAX/CAC40 对美股的反向事实,且以端点日不同的 DAX(至 11-23 盘中)与 SPX(至 11-20)相比。另:VIX 跳升集中于 11-13→11-20 周(19.30→35.89),距两地最近政策日 2026-10-30 已隔两周(11-13 起),11-23 已回落 15.7%——两项观测均偏竞争解释(冲击主导)。裁定词「尚不能区分」可保留,依据须如实。""",
         fix="""单月窗(同日口径至 2026-11-20):SPX −9.36%、NIKKEI225 −9.98%、DAX −1.50%、CAC40 +1.86%——日本股指仅略弱于美股,欧元区股指强于美股,与主解释『两地股指弱于美股』在欧元区一端不符;VIX 跳升集中于 11-13→11-20 周(19.30→35.89),距两地最近政策日(2026-10-30)已隔两周,观测偏向全局冲击解释;单月窗不足以排除紧缩叙事,留待后续窗复检。"""),
    dict(id="MA-7", sev="MAJOR", pts=["P35", "P39"],
         where="agent_judgment.json l3.contradictions[1].statement(C2);reader_map.headline_conclusion;reader_map.regions[0].from_to(欧元区走位「决议日公布」);l3.mechanism_chains[0].links[1].text(M1 step2);MAP_REPORT.md L59–L66、L124",
         original="欧央行主要再融资利率(ECB_MRO,政策目标口径)最新生效水平为 2.65%,观测=生效日 2026-09-16,决议日 2026-09-10,决议日当日公布。",
         note="""问句四问之一是「各数据的公布时间」。冻结发布日历无任何 ECB 实录;注册表 ECB_MRO/ECB_DFR 记「ECB管委会金融政策决议公布后生效并当日更新系列」(决议日=生效日=变更日 2026-09-16);引擎发布面 point_values…publication_date=2026-09-16(关键数字表同;规则文本「ECB 决议日当日公布(变更日观测)」把决议日等同于变更日观测)。判断档以引擎 prev_thursday 惯例回推的 09-10 为决议日并称「决议日当日公布」,使同一数据点出现两个公布日(09-10 对 09-16),且决议日在事实位无推断标注;MAP L10 自称「序列面决议/生效日亦不可推」,与 L66「决议日由央行公告惯例自生效日回推」并存。6 个月前锚行的 2025-06-05 同属惯例回推。""",
         fix="""欧央行主要再融资利率(ECB_MRO,政策目标口径)最新生效水平为 2.65%,序列变更日=生效日 2026-09-16,引擎发布面公布日 2026-09-16;决议日 2026-09-10 系引擎按『生效日前上一个周四』惯例自变更日回推【推断】(冻结发布日历无 ECB 实录,决议公布日未能核实)。(标题结论、欧元区走位、M1 step2、对质表第 1 行的「2026-09-10 决议」同加「引擎按惯例回推」注;欧元区走位「决议日公布」改「序列变更日 2026-09-16 公布」。)"""),
    dict(id="MA-8", sev="MAJOR", pts=["P88"],
         where="agent_judgment.json reader_map.history_zero_case_note;MAP_REPORT.md L205",
         original="检索范围=引擎 analog 能力未启用(本问未请求历史相似对照,问句焦点为当前水平、最近六个月决议与同比对照);三时点锚(6个月前/最新一期)+发布日历实录+序列面已足够支撑问句,零历史段呈现以避免以事后冒充预测;如需「两地通胀一升一降+同向收紧」的历史相似检索,可另行发起 analog 问句。",
         note="""与证据面相左:report.json steps[S6_analog] executed=True、ok=True、argv=['analog'],envelope scanned=1871、valid=74,TOP5 首位候选 2025-03(距离 0.752676);FULL_REPORT.md 含「历史相似结构(引擎确定性面·读者版)」表;引擎内部摘要 question_summary 亦列「历史类比」。零段呈现本身不违规(问句未请求历史相似对照),违规在缺口理由陈述不实。""",
         fix="""检索范围=研判席本轮未采用历史相似段:引擎 analog 面已运行(report.json steps[S6_analog]:扫描 1871、有效 74、TOP5,首位候选 2025-03 距离 0.752676;完整报告「历史相似结构」表),本问未请求历史相似对照(焦点为当前水平、最近六个月决议与同比对照),三时点锚+发布日历实录+序列面已足够支撑问句,零历史段呈现以避免以事后冒充预测;如需「两地通胀一升一降+同向收紧」的历史相似检索,可另行发起 analog 问句。"""),
    # ================= MINOR =================
    dict(id="MI-1", sev="MINOR", pts=["P40", "P41", "P42"],
         where="MAP_REPORT.md L75/L78「净变动 **+25bp**(2.25→2.5)/(2.4→2.65)」、L81「净变动 **+67bp**(0.557→1.227)」;agent_judgment.json reader_map.regions[1].from_to(日本走位)",
         original="近 12 个月政策窗净 +67bp",
         note="""窗 2025-11-23..2026-11-23 的窗启在值为 2.0/2.15(2025-06-11 起)→窗末 2.5/2.65=+50bp,同句列两步各 +25bp;日本六步之和 +75bp、窗启在值 0.478→1.227=+74.9bp。引擎 net_bp 取「窗内首末观测差」(漏计窗内首步/舍入),括注已披露端点,但「净变动」一词与同句所列变动点之和不一致。""",
         fix="""改称「窗内末次观测对首步前值之差」,或改用窗启在值口径并注明:「近 12 个月月均由 0.478 升至 1.227(约 +75bp;引擎窗内净 +67bp 不含 2025-12 首步 +8bp)」。"""),
    dict(id="MI-2", sev="MINOR", pts=["P104"],
         where="agent_judgment.json l3.contradictions[2].statement(C3 首两句)",
         original="ECB 数据面断档使 2026-09-16 之后的决议面在引擎不可见。",
         note="""以事实位陈述「断档/源端缺席」:snapshot.sources_status.ea.status=EXACT(采集档 ea_20261123.json 当日入场);事实行 issues[0] 为 frequency 类「ECB_DFR观测日滞后68天(>10天有效窗,daily频;未发布或采集失败,不得当作最新一期)」(成因留两可;注册表 freshness.max_calendar_lag_days=10);注册表 decision_dated 注记「无更晚已证实决议不作过期」。「断档/源端缺席」是解释而非观测,应标【推断】或改述为「序列止于 2026-09-16」;后文【尚未验证】与两解释并列部分合规。""",
         fix="""ECB_MRO/ECB_DFR 序列止于 2026-09-16(观测日距截止 68 天,超过注册表 10 天新鲜度阈,Gate A 列 degraded),其后的决议面在引擎不可见;采集档 sources_status.ea=EXACT(2026-11-23 入场),是否另有新决议不可判,属【尚未验证】。"""),
    dict(id="MI-3", sev="MINOR", pts=["P105"],
         where="agent_judgment.json l3.contradictions[2].competing_explanations[0]",
         original="若断档纯为源端技术缺席(生产观察登记 ECB 504)而实际无新决议",
         note="""「生产观察登记 ECB 504」在只读面(快照、发布日历、注册表、report.json 引擎面、证据索引)无此登记,数字无出处。""",
         fix="""若序列止于 2026-09-16 纯属源端未更新而实际无新决议,则 2.65%/2.50% 即最新水平(与 2026-09-16 变更后无新事件相容)。"""),
    dict(id="MI-4", sev="MINOR", pts=["P90", "P91"],
         where="agent_judgment.json l4.scenarios[0].rows.trigger.condition 与 falsification.threshold(S1);l4.scenarios[1].rows.trigger.condition(S2)",
         original="2026-12 或 2027-01 发布的 EA_HICP_YOY 同比 ≥4.0% 且 JP_CPI_YOY 同比 ≥2.0%,同时 VIX 高于 30",
         note="""指标均在册、期限在前、方向互补,不构成不可观测;口径可改进:S1 触发「VIX 高于 30」未绑日期,且截止日读数 30.24(盘中值)已满足,不具前瞻区分力;S1 前提「维持 3.5% 以上」与证伪「两月均 <3.0%」之间留有 [3.0,3.5) 未定带;S2 触发「≤3.4%」宽于其前提「<3.0%」;两情景陈述含 ECB/BOJ 政策分量(「再上调一级」「按兵不动」)而触发/证伪只含通胀与 VIX。""",
         fix="""VIX 条件绑定观测日(如 2027-01 最后收盘)或改用月末收盘口径;证伪阈值与前提对齐(如两月均低于 3.5%);S2 触发与前提对齐(最新值 <3.0%);补 ECB/BOJ 决议分量或声明政策分量不设触发。"""),
    dict(id="MI-5", sev="MINOR", pts=["P107"],
         where="MAP_REPORT.md L41(东京都CPI同比 ok | ok)与判断档口径披露 quality_gate_notes[4];snapshot gate_a.noncore_missing",
         original="",
         note="""快照 gate_a.noncore_missing 含 JP_CPI_TOKYO_YOY(noncore_missing_detail:「来源文件在场而指标缺席(采集遗漏或子源缺席——档内无该指标子源状态记录,不可区分)」),MAP 覆盖表该格记「ok | ok」,判断档 C1 引用东京最新读数 2.73 而未披露该列名(series_store 中东京序列 n=10 至 2026-10 在场,L1 无事实行,数值可用);Gate A 如实披露不完整。""",
         fix="""口径披露补一句:快照 Gate A 将 JP_CPI_TOKYO_YOY 列入 noncore_missing(来源文件在场而指标缺席),本报告东京值取自 series_store 在场序列(2026-01..2026-10,10 期),L1 无事实行。"""),
    dict(id="MI-6", sev="MINOR", pts=["P106"],
         where="agent_judgment.json l3.contradictions[0].statement(C1「官方实录公表日同为 2026-11-20,引擎外旁证」);reader_map.regions[1].from_to;quality_gate_notes[4]",
         original="官方实录公表日同为 2026-11-20,引擎外旁证",
         note="""冻结发布日历无 JP_CPI_YOY 条目,注册表 release_semantics 仅「每月中旬(通常周五)发布上月全国CPI」,只读面不能核此「官方实录」;东京 2026-10-30 可由注册表规则文本「官方实录锚 2026年10月分=2026-10-30」旁证。已标引擎外,宜写明出处或删「官方实录」字样。""",
         fix="""全国: 最新读数发布 2026-11-20(引擎推定规则,非日历实录;引擎外旁证从略或注明出处)。"""),
    dict(id="MI-7", sev="MINOR", pts=["P108"],
         where="agent_judgment.json l3.mechanism_chains[0].links[2].text 与 links[3].text(M1 step3/step4);reader_map.transmission[0].links[1].observed_fact、links[2].observed_fact;l4.scenarios[0].rows.trigger.condition",
         original="11-23 值为当日实时快照(非收盘价)",
         note="""事实行 calc 记「VIX指数收盘」「指数收盘点位」,与「非收盘价」说明相反;快照时间 2026-11-23T20:41:34+08:00(=12:41Z),美股常规时段收盘值此时尚不可能入场,VIX 30.24 的时点/口径在证据面不可核(11-20 收盘 35.89)。M1 step4、资产月窗(+55.5%)与 S1 触发(VIX>30)均以其为端点,同一月窗内混用收盘与盘中口径;研判席的时点说明与 research_as_of 相容,属可改进。""",
         fix="""并列 11-20 收盘口径:VIX 35.89(月窗 +84.5%)、DAX 24802.78(月窗 −1.50%);11-23 盘中值仅作旁注。"""),
    dict(id="MI-8", sev="MINOR", pts=[],
         where="agent_judgment.json l3.mechanism_chains[0].links[1].text(M1 step2);reader_map.regions[1].from_to;reader_map.turnings[2].narrative",
         original="月均口径 0.727→1.227 的台阶与决议-生效记录相容",
         note="""冻结日历对 BOJ 仅有 2026-09-18 决议与 2026-10-30 维持两条;2025-12、2026-01、2026-06、2026-07 四次月均台阶(合计 +50bp)在日历中无对应决议实录,引擎 JP_POLICY_RATE 的 policy_face decision/effective 均为 null。「相容」仅对 2026-09 以后可核,宜限定范围。""",
         fix="""月均口径 2026-09 1.043→2026-10 1.227 的台阶与 2026-09-18 决议、2026-09-24 生效(目标约 1.25%)相容;2025-12 至 2026-07 的四次月均台阶在冻结日历无对应决议实录,仅作市场口径陈述。"""),
    dict(id="MI-9", sev="MINOR", pts=[],
         where="agent_judgment.json l3.contradictions[0].statement(C1 日本同比对照)与口径披露 quality_gate_notes[4]",
         original="",
         note="""注册表 JP_CPI_YOY calc 记「zmi2025aa(2025基)+zmi2020aa(2020基)双档水平值,各自基期内做严格同月同比后拼接(新基优先,重叠差>0.10pp 告警)」;报告与判断档的口径披露未提及拼接口径,2026-10 对 2025-10 的对照落在哪一基期档只读面不可核。不影响 −0.55pp 的方向,属披露可改进。""",
         fix="""口径披露补:全国 CPI 同比为 2025 基/2020 基拼接序列(各自基期内同月同比,新基优先,重叠差>0.10pp 告警)。"""),
    # ================= NIT =================
    dict(id="NI-1", sev="NIT", pts=["P37", "P38"],
         where="MAP_REPORT.md L66(注,引擎面行文)",
         original="",
         note="""「ECB_MRO/ECB_DFR 观测日全为周三=生效日」:series_store 中 MRO 9/48、DFR 21/69 条观测非周三(均不晚于 2008-10-09),其后全为周三;「全为」宜改「2008-10 以来」。""",
         fix=""),
    dict(id="NI-2", sev="NIT", pts=[],
         where="MAP_REPORT.md L7(口径行,引擎面行文)",
         original="",
         note="""「三个对照时点=日历点锚(截止日−12月/−3月/最新一期)」与本问实际锚(6个月前/最新一期)不符;判断档已在引擎缺口披露①说明,读者版宜随锚渲染。""",
         fix=""),
    dict(id="NI-3", sev="NIT", pts=["P84"],
         where="agent_judgment.json l3.mechanism_chains[0].links[2].text、reader_map.transmission[0].links[1].observed_fact「EURUSD 最新 1.1」",
         original="",
         note="""EURUSD 水平写作 1.1(事实行两位有效数字;序列值 1.096491,MAP L139/L150 作 1.09649),同档 USDJPY 保留两位小数,精度不一。""",
         fix=""),
    dict(id="NI-4", sev="NIT", pts=["P43"],
         where="agent_judgment.json M1 step4、reader_map.transmission[0].links[2].observed_fact;MAP_REPORT.md L81",
         original="",
         note="""「(+55.5%(至 2026-11-23,…))」括号嵌套;L81 变动点省略 2026-04 的 0.728→0.727(−0.1bp)微动(不影响结论)。""",
         fix=""),
]

for it in ITEMS:
    if it["original"]:
        assert it["original"] in BLOB, "原句不在判断档中(非逐字): %s %s" % (it["id"], it["original"][:40])

MAJ = [i for i in ITEMS if i["sev"] == "MAJOR"]
MIN = [i for i in ITEMS if i["sev"] == "MINOR"]
NIT = [i for i in ITEMS if i["sev"] == "NIT"]

# ------------------------------------------------------------------ 六查
SIX = [
    ("C1-INFL-DIVERGE(两地通胀同比对照)", [
        ("证据相关性", "通过。两条最新读数事实行(JP_CPI_YOY@2026-10-01=2.44 WARN、EA_HICP_YOY@2026-10-01=4.0 WARN)与「相比去年同月」直接相关;基期 2025-10 两序列在场(2.99/2.1);20 条 evidence_refs 全部可在 evidence_index.json 解析。"),
        ("支持度", "通过。−0.55pp / +1.9pp 直算成立,「日本回落、欧元区抬升」方向词与数值一致。"),
        ("竞争解释", "通过。两条竞争解释(能源/进口传导+高基数消退→剪刀差收敛,对 需求与政策组合→持续分化)为真正竞争、对后续路径预言不同;研判席明示引擎无分项不可验证、如实并列,未越裁。"),
        ("反对证据", "未见未披露的反向事实;东京 CPI 基期缺席已如实声明。全国 CPI 序列为 2025 基/2020 基拼接,口径未披露(MINOR)。"),
        ("结论是否超出证据", "未超出(只陈述对照,未归因)。"),
        ("证伪可观测性", "两条竞争解释的区分指标(后续 EA_HICP_YOY 与 JP_CPI_YOY 是否收敛)在场、方向不同,可观测;未写入 L4 区分指标(非强制)。"),
    ], "无需修订。"),
    ("C2-POLICY-SYNC(两地政策同向收紧、无未生效决议)", [
        ("证据相关性", "通过。日历 RC-JP-BOJ-TARGET-2026-09 / RC-JP-BOJ-MAINT-2026-10、ECB 序列变更点、资产水平事实行均与陈述直接相关。"),
        ("支持度", "目标 1.25、生效 2026-09-24、维持 2026-10-30、MRO 2.65/DFR 2.5、窗内两次 +25bp、无待生效条目——全部直算一致;「决议日 2026-09-10…决议日当日公布」不可核且与引擎发布面 2026-09-16 冲突(MAJOR)。"),
        ("竞争解释", "读数驱动 对 程序驱动为真正竞争;本条自述「月频证据下两种驱动不可区分」合规,但对质表第 1 行却裁「支持主解释」,同档自相矛盾(MAJOR)。"),
        ("反对证据", "月均口径「台阶与决议-生效记录相容」偏宽:2025-12 至 2026-07 四次台阶在冻结日历无决议实录(MINOR)。"),
        ("结论是否超出证据", "「决议日当日公布」超出证据。"),
        ("证伪可观测性", "「后续决议节奏是否与读数联动」可在后续决议日历与读数观测,方向不同,可观测。"),
    ], "需修订(MAJOR:ECB 决议日/公布日)。"),
    ("C3-ECB-VISIBILITY(ECB 决议面可见性)", [
        ("证据相关性", "通过。序列末观测 2026-09-16、gate_a.noncore_degraded 含 ECB_DFR/ECB_MRO、日历无 ECB 条目、事实行 DEGRADED——直算一致。"),
        ("支持度", "「2026-09-16 之后决议面不可见(引擎面内)」成立。"),
        ("竞争解释", "技术缺席 对 实际新决议,对「2.65/2.5 是否为最新水平」预言不同;明示不可区分、需官网核对(引擎外,待授权),合规。"),
        ("反对证据", "首句把「断档/源端缺席」写成事实,而 sources_status.ea=EXACT(2026-11-23 采集档入场)、注册表 decision_dated 注记「无更晚已证实决议不作过期」、事实行 issue 为频次滞后 68 天;「生产观察登记 ECB 504」无出处(MINOR)。"),
        ("结论是否超出证据", "首句超出(解释冒充观测);其余【尚未验证】标注到位。"),
        ("证伪可观测性", "引擎面内可观测(下一版快照 ECB 序列是否出现 2026-09-16 之后的变更点)。"),
    ], "披露修订(MINOR)。"),
    ("M1-INFL-POLICY-ASSET(机制链四环)", [
        ("step1 [E1] 通胀路径", "数值全部一致(1.9/3.2/2.8/4.0;1.27/2.44);「2025-07 高点 3.1」与序列相左(2025-06=3.27、2025-01=4.03)——MAJOR。观察环无竞争解释/证伪要求。"),
        ("step2 [E1] 政策跟进", "幅度与生效日一致;决议日为引擎惯例回推、未标推断——MAJOR;「月均台阶与决议-生效记录相容」范围偏宽——MINOR。反对证据:2025-06-11 至 2026-06-16 读数升而利率未动(应由对质表披露)。"),
        ("step3 [E2] 利差→汇率", "标注合规(【假设】、缺环说明、区分指标在场);但「仅水平观测…方向对质不可判」失实:近一月面 EURUSD −2.29%、USDJPY +1.57%、DXY +2.06%,两货币同向走弱,与竞争解释相容——MAJOR。两解释对同一指标预言不同且观测在场,按报告自述口径属可裁。"),
        ("step4 [E2] 资产面", "数值一致;竞争解释真正;未披露同日口径下欧元区股指强于美股、称「与紧缩叙事相容」——MAJOR;端点口径混用(盘中/收盘)——MINOR;区分指标 VIX 在场,「后续窗复检」可观测。"),
    ], "需修订(MAJOR 三处)。"),
    ("L4 条件情景(S1-STICKY-TIGHTEN / S2-INFL-FADE)", [
        ("证据相关性", "通过。EA_HICP_YOY、JP_CPI_YOY、VIX 均在 series_store 在册。"),
        ("支持度/与截止日相容", "S1 与截止日读数相容(HICP 4.0、CPI 2.44、VIX 30.24);S2 为并列反例、自述与近一月观察相反。"),
        ("竞争解释/方向互补", "通过。两情景方向互补(收紧+高位波动 对 回落+政策不变)。"),
        ("反对证据", "无(均标【假设·非预测】,未冒充预测)。"),
        ("结论是否超出证据", "未超出。"),
        ("证伪可观测性", "证伪指标 EA_HICP_YOY(次级 JP_CPI_YOY)在场,期限 2027-02-15 在截止日之后。不足:阈值未定带 [3.0,3.5)、S2 触发 ≤3.4% 宽于前提 <3.0%、VIX 条件未绑日期且已满足、政策分量未入触发/证伪——MINOR,非不可观测。"),
    ], "口径修订(MINOR)。"),
    ("转折面(reader_map.turnings)", [
        ("数值与窗口", "T1 2.9→1.27、T2 1.9→3.2、T3 0.727→0.978(经 0.841)及逐月路径、「候选池内最大单段变动」「近十二个月最高」直算一致。"),
        ("谁先变/同窗方向", "T3「两地同向、先后未定」合规;T1/T2「同期/同窗背离」与序列相左(T1 窗欧元区 2.1→1.9,T2 窗日本 1.27→1.53)——MAJOR×2。"),
    ], "需修订(MAJOR 两句)。"),
    ("历史类比", [
        ("零段呈现", "问句未请求历史相似对照,零段呈现本身合规;引擎候选的事后结果标注「非预测」。"),
        ("缺口理由", "「引擎 analog 能力未启用」与 report.json steps[S6_analog] 已运行相左——MAJOR。"),
    ], "需修订(MAJOR 一句)。"),
    ("诚实缺席/Gate A、截止日当日观测、目标利率与同比(⑪⑫⑬)", [
        ("诚实缺席", "JP_POLICY_TARGET 注册表与 series_store 均无——属实;ECB 序列止于 2026-09-16 且 DEGRADED——属实;东京 CPI 列 noncore_missing 未披露——MINOR;Gate A 总体 DEGRADED 已披露。"),
        ("截止日当日观测", "DAX 11-23 盘中标注与快照时点 12:41Z 相容;VIX 30.24 标「非收盘价」与事实行「收盘」口径相反、时点不可核——MINOR。"),
        ("目标利率与同比", "日本现行有效目标 1.25(2026-09-24 生效,维持核验至 2026-10-30)属实;ECB 序列现值 2.65/2.5 属实(官方目标定性无日历实录,MAP 标草稿,判断档以 DEGRADED+【尚未验证】披露);月均 1.227 与宣布值 1.25 分列未冒充;全国/全区同比对照成立。"),
    ], "披露修订(MINOR)。"),
]

# ------------------------------------------------------------------ 反方攻击
ATTACKS = [
    "C1:「日本回落」是否为基期切换或相邻月替代的假象?→ 2025-10=2.99、2026-10=2.44 均为 series_store 同序列真值,方向成立;东京 CPI 未以相邻月凑基期;CPI 拼接口径未披露记 MINOR;竞争解释无分项不可验证、研判席如实并列——未击穿。",
    "C2:「无已决议未生效」是否被 ECB 序列断档架空?→ 引擎面内成立(冻结日历无待生效条目,ECB 末次变更 2026-09-16 已生效),报告以【尚未验证】限定;但「决议日当日公布」与引擎发布面公布日 2026-09-16 冲突——击穿(MAJOR)。",
    "C2:「月均台阶与决议-生效记录相容」是否夸大?→ 2025-12、2026-01、2026-06、2026-07 四次台阶在冻结日历无决议实录,仅 2026-09 以后可核——部分击穿(MINOR)。",
    "C3:「断档/源端缺席/ECB 504」是否有出处?→ sources_status.ea=EXACT,注册表不认过期,「ECB 504」仅见于判断档自身文字——无出处(MINOR);两解释并列与【尚未验证】标注合规。",
    "M1 step1:「2025-07 高点 3.1」是否成立?→ 2025-06=3.27 更高,2025 年最大为 2025-01 的 4.03——击穿(MAJOR)。",
    "M1 step2/标题:ECB 决议日 2026-09-10 是否可核?→ 冻结日历无 ECB 实录,注册表记决议公布后生效并当日更新系列,决议日仅引擎 prev_thursday 惯例回推——不可核且公布日冲突(MAJOR)。",
    "M1 step3/对质表第 2 行:「引擎面仅水平观测」是否属实?→ snapshot.facts[*].derived.m1 给出 EURUSD −2.29%、USDJPY +1.57%、DXY +2.06%,两货币同向走弱——失实(MAJOR)。",
    "M1 step4/对质表第 3 行:「三地同跌与紧缩叙事相容」是否漏反向事实?→ 同日口径至 11-20 DAX −1.50%、CAC40 +1.86% 对 SPX −9.36%,欧元区股指强于美股;VIX 跳升集中在 11-13→11-20 周、距最近政策日(2026-10-30)已隔两周——漏披露(MAJOR)。",
    "对质表第 1 行:「支持主解释」是否越裁?→ 两解释对「决议前读数抬升」预期未分立(n=2),且 2025-06-11 至 2026-06-16 读数升而利率未动;与 C2「不可区分」矛盾——越裁(MAJOR)。",
    "转折面:「同期/同窗背离」是否与序列一致?→ T1 窗欧元区 2.1→1.9 同向下行,T2 窗日本 1.27→1.53 同向上行——不一致(MAJOR×2)。",
    "L4:触发/证伪是否可观测、与截止日相容?→ 指标在册、期限在前、方向互补、读数相容;阈值未定带、VIX 条件已满足且未绑日期、政策分量缺位——未击穿可观测性,记 MINOR。",
    "历史类比:零段理由「analog 未启用」是否属实?→ report.json steps[S6_analog] ok=True、scanned 1871、valid 74、TOP5,完整报告有「历史相似结构」表——不属实(MAJOR)。",
    "确定性层:契约 VERIFIED 是否足以背书?→ 仅核验 4 个数值 token(1.227%/158.96/6910.39/30.24),其余数值以中文数字书写落在别名表之外(研判席已披露为引擎缺口②);本席 112 点复算为补位:一致 89、偏离 20、不可核 3。",
    "全局:是否出现未发布值或事后信息冒充当时可知?→ 6 个月前锚 12 格均按「公布日≤锚日」取值(2026-05 观测期公布日晚于锚日,未被采用),最晚被引公布日 2026-11-20 不晚于截止日——未见。",
]

OBS = [
    "契约层(agent_judgment.contract_verification,VERIFIED)只核验了 4 个数值 token(1.227%、158.96、6910.39、30.24):研判席对无别名指标的数值一律用中文数字书写,落在 text_consistency.ALIASES 之外(研判席已作为引擎缺口②披露)。确定性层对本档约百个数字的覆盖率很低,本席 112 点独立复算为补位;建议立研发项(别名表覆盖或中文数字 token 解析)。",
    "研判席自披露的三项引擎缺口,本席复核两项属实:①锚标签硬编码「12个月前/3个月前/最新一期」(MAP L7 样例文字同此);③点值格按发布规则取值(本席 12 个锚格均按「公布日≤锚日」成立,未见未发布值入场)。",
    "MAP_REPORT.md 被引擎标为草稿(map_official_target_missing:欧元区官方政策目标无日历实录);判断档以 DEGRADED 与【尚未验证】披露 ECB 决议面不可见,主答以序列现值 2.65/2.5 给出并注明口径——披露充分,本席未据此加项。",
]

NONOK = {p["id"] for p in ROWS if p["status"] != "OK"}
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
OK, DEV, UNV, MIS = SUM["ok"], SUM["dev"], SUM["unver"], SUM["recompute_mismatches"]
assert N == len(ROWS) and MIS == DEV + UNV


def esc(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def table(rows):
    out = ["| # | 类 | 出处键 | 直算值 | 报告值 | 一致与否 | 类型 | 备注 |", "|---|---|---|---|---|---|---|---|"]
    for p in rows:
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            esc(p["id"]), esc(p["cat"]), esc(p["source"]), esc(p["computed"]), esc(p["reported"]),
            {"OK": "一致", "DEV": "偏离", "UNVER": "不可核"}.get(p["status"], p["status"]), esc(p["kind"]), esc(p["note"])))
    return "\n".join(out)


by_cat = "、".join("%s %d/%d" % (k, v["ok"], v["n"]) for k, v in sorted(SUM["by_cat"].items()))
kindstxt = "、".join("%s %d" % (k, v) for k, v in sorted(SUM["mismatch_kinds"].items()))

L = []
L.append("# T3 Round-1 独立语义审查记录(PROSE)\n")
L.append("- 审查对象: 工单 T3,运行 %s(问句原文见 question_verbatim.txt);代码印章 %s。" % (SUM.get("run_id", "20261123T124341Z"), "f722e3c0bf7cd10aee64a8f4a166a136180a28ea"))
L.append("- 席位: 常驻独立语义审计席(零上下文、真独立),reviewer=independent-zero-context-seat-r32-t3-round1;审查日 2026-11-23。")
L.append("- 只读面: 运行目录内 question_verbatim.txt / MAP_REPORT.md / FULL_REPORT.md / report.md / agent_judgment.json / report.json(引擎面)/ evidence_index.json / views_digest.json / root_overlay/config/release_calendar.json / root_overlay/config/metric_registry.json / root_overlay/data/daily/research_snapshot_20261123.json;安装树 CODE_VERSION 印章。")
L.append("- 边界声明: 未读取 research_archive/、树内 docs/、/tmp/r32-accept/out/、/tmp/r32-accept/scripts/、/tmp/r32-accept/replay/、/tmp/r32-accept/install*、其他运行目录、~/investment-agent-product,亦未读取运行目录内不在清单的 AGENT_SEAT_ENVELOPE.json;未运行 ia_cli.py 任何子命令;未联网;未修改运行目录与安装树任何文件;未调用 record_semantic_verdict。自写脚本(recompute.py、probe.py、extract_*.py、changes.py、check_refs*.py、build_outputs.py、validate_verdict.py)与全部产物均在 /tmp/r32-accept/review/T3_round1/;python 一律 `python3 -I 脚本 路径参数…` 于 /tmp 下运行。")
L.append("- 复算方法: recompute.py 从冻结快照 series_store / 冻结发布日历 / 注册表 / report.json 引擎面直算,再与报告与判断档文字逐点比对;点值锚按「公布日≤锚日」发布纪律取值;结果见 recompute_table.tsv / recompute_table.md / recompute_summary.json。")
L.append("")
L.append("## 一、复算清单(%d 点: 一致 %d、偏离 %d、不可核 %d)\n" % (N, OK, DEV, UNV))
L.append("按类别(一致/总数): %s。偏离与不可核按类型: %s。\n" % (by_cat, kindstxt))
L.append("偏离与不可核的分级归属: MAJOR 相关 %s;MINOR 相关 %s;NIT 级 %s(逐条见第四节)。\n" % ("、".join(MAJ_PTS), "、".join(MIN_PTS), "、".join(NIT_PTS)))
L.append("说明: 「偏离」含数值/日期/方向错、口径不一与披露缺口三类;「不可核」指报告断言在只读面无出处。类型为 numeric/date/direction 者才属事实性错判;caliber/disclosure/claim 另按裁决标准分级(见第四节)。\n")
L.append("### 1.1 偏离与不可核明细(%d)\n" % MIS)
L.append(table([p for p in ROWS if p["status"] != "OK"]))
L.append("")
L.append("### 1.2 全部复算点\n")
L.append(table(ROWS))
L.append("")
L.append("## 二、六查逐项结论与证伪\n")
for title, checks, concl in SIX:
    L.append("### %s\n" % title)
    L.append("| 查项 | 结论 |\n|---|---|")
    for k, v in checks:
        L.append("| %s | %s |" % (esc(k), esc(v)))
    L.append("")
    L.append("结论: %s\n" % concl)
L.append("## 三、反方攻击记录(每条 L3 矛盾陈述与机制链各环至少一次)\n")
for i, a in enumerate(ATTACKS, 1):
    L.append("%d. %s" % (i, a))
L.append("")
L.append("## 四、问题清单\n")
for sev, lst, title in (("MAJOR", MAJ, "4.1 MAJOR(必修,%d 条)" % len(MAJ)), ("MINOR", MIN, "4.2 MINOR(%d 条)" % len(MIN)), ("NIT", NIT, "4.3 NIT(%d 条)" % len(NIT))):
    L.append("### %s\n" % title)
    for i, it in enumerate(lst, 1):
        L.append("%d. **[%s]** 位置: %s" % (i, it["id"], it["where"]))
        L.append("   - 问题: %s" % it["note"])
        if it["pts"]:
            L.append("   - 对应复算点: %s" % "、".join(it["pts"]))
        if it["sev"] == "MAJOR":
            L.append("   - 原句: 「%s」" % it["original"])
            L.append("   - 改句: 「%s」" % it["fix"])
        elif it["original"]:
            L.append("   - 原句: 「%s」" % it["original"])
            if it["fix"]:
                L.append("   - 建议改法: 「%s」" % it["fix"])
    L.append("")
L.append("### 4.4 观察项(非判定项,供操作席参考)\n")
for o in OBS:
    L.append("- %s" % o)
L.append("")
L.append("## 五、裁决\n")
L.append("REVISE。依据: 存在 MAJOR %d 条(方向/关系词与证据相左 3、对质表越裁与依据失实 3、日期与证据面冲突 1、缺口理由与证据面相左 1)。问句四问的主答(两地官方政策目标利率、最近六个月无已决议未生效、通胀同比对照、公布时间)经复算成立;修订第四节 4.1 各句并同步同源句后复审。\n" % len(MAJ))
L.append("机器可读裁决: VERDICT-round1.json(同目录)。\n")
with open(os.path.join(OUT, "PROSE-round1.md"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(L))

notes = (
    "REVISE:存在 MAJOR {nmaj} 条。独立复算 {n} 点(冻结快照 series_store / 冻结发布日历 / 注册表 / report.json 引擎面直算后与报告及判断档文字逐点比对):"
    "一致 {ok}、偏离 {dev}、不可核 {unv}(偏离合计 {mis};分级归属: MAJOR 相关 {nmp}、MINOR 相关 {nmip}、NIT 级 {nnp});其中截止日 4/4、点值锚格 12/12(按「公布日≤锚日」发布纪律取值)、同比基期 6/6、三利率与资产月窗 11/11、传导链证据级 9/9、两地目标利率与同比 3/3 整类一致,政策目标/生效日/距离天数、"
    "转折候选值与逐月路径各点一致,未见未发布值入场或以相邻口径冒充。"
    "MAJOR:①②转折表「同期/同窗背离」方向与序列相左(T1 窗 2025-11→2026-02 欧元区亦下行 2.1→1.9;T2 窗 2026-02→2026-05 日本自谷底回升 1.27→1.53);"
    "③M1 step1 及日本走位「2025-07 高点 3.1」关系词错(2025-06=3.27、2025-01=4.03);"
    "④对质表第 1 行裁「支持主解释」属越裁:两解释预期未分立,且与 C2「两种驱动不可区分」自相矛盾;"
    "⑤第 2 行「引擎面仅水平观测」失实(近一月 EURUSD −2.29%、USDJPY +1.57%、DXY +2.06%,两货币同向走弱,偏竞争解释);"
    "⑥第 3 行未披露同日口径下欧元区股指强于美股(至 11-20 DAX −1.50%、CAC40 +1.86% 对 SPX −9.36%)且称「与紧缩叙事相容」;"
    "⑦ECB「决议日 2026-09-10,决议日当日公布」与引擎发布面公布日 2026-09-16 及注册表相左,决议日系惯例回推未标推断;"
    "⑧「引擎 analog 能力未启用」与 report.json steps[S6_analog] 已运行(scanned 1871/valid 74/TOP5)相左。"
    "MINOR {nmin} 条(政策窗「净变动」口径、「断档/源端缺席」与「ECB 504」无出处、情景阈值未定带与 VIX 条件、东京 CPI 的 Gate A 列名未披露、全国 CPI「官方实录公表日」无出处、11-23 盘中值与收盘口径混用、月均台阶与决议实录相容范围、CPI 拼接口径未披露)、NIT {nnit} 条。"
    "问句四问主答(目标利率 1.25% 与 2.65%/2.5%、无已决议未生效、通胀同比 2.44% 低于去年同月/4.0% 高于去年同月及公布日)经复算成立;修订上述 {nmaj} 句后复审。"
).format(nmaj=len(MAJ), n=N, ok=OK, dev=DEV, unv=UNV, mis=MIS, nmin=len(MIN), nnit=len(NIT), nmp=len(MAJ_PTS), nmip=len(MIN_PTS), nnp=len(NIT_PTS))

verdict = {
    "seat": "semantic-audit-seat",
    "reviewer": "independent-zero-context-seat-r32-t3-round1",
    "verdict": "REVISE",
    "overall": "REVISE",
    "notes": notes,
    "items": [{"severity": it["sev"], "where": it["where"], "note": it["note"], "original": it["original"], "fix": it["fix"]} for it in ITEMS],
    "must_fix": ["%d. 原句:「%s」→ 改句:「%s」" % (i, it["original"], it["fix"]) for i, it in enumerate(MAJ, 1)],
    "counterexamples_sought": ATTACKS,
    "recompute_points": N,
    "recompute_mismatches": MIS,
    "mismatch_details": SUM["mismatch_details"],
    "audited_at": "2026-11-23",
}
with open(os.path.join(OUT, "VERDICT-round1.json"), "w", encoding="utf-8") as fh:
    json.dump(verdict, fh, ensure_ascii=False, indent=1)
print("items: MAJOR=%d MINOR=%d NIT=%d; points=%d ok=%d dev=%d unver=%d mismatches=%d" % (len(MAJ), len(MIN), len(NIT), N, OK, DEV, UNV, MIS))
print("wrote PROSE-round1.md and VERDICT-round1.json to", OUT)
